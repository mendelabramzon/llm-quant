#!/usr/bin/env python3
"""Collect a trailing window of Solana mainnet blocks (finalized, every produced block or every K-th) into compact per-block files.

Compact = the getBlock `json` encoding with vote transactions dropped (counted), `rewards` off, and log messages reduced to
the lines that carry information not derivable elsewhere: `Program data:` (Anchor events), `Program log:` (incl.
`Instruction:` names), `Program return:`, error lines, and `... consumed N of M compute units` (per-program CU). The
`invoke`/`success` lines are dropped because innerInstructions carry the call tree. Everything else (account keys,
instructions, inner instructions, loaded addresses, pre/post SOL and token balances, fee, CU, err) is kept verbatim, so
analyzers written against the RPC shape work on these files. Resumable: existing block files are skipped; the window is
pinned in manifest.json at first run. Read-only; tokens never written.

  uv run python scripts/solana_collect.py collect --out research/2026-09-07/solana_live --hours 1 [--workers 8] [--every 1]
  uv run python scripts/solana_collect.py verify  --out research/2026-09-07/solana_live
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from solana_rpc import Client, RpcError  # noqa: E402

VOTE = 'Vote111111111111111111111111111111111111111'
BLOCK_PARAMS = {'commitment': 'finalized', 'encoding': 'json', 'transactionDetails': 'full', 'rewards': False, 'maxSupportedTransactionVersion': 0}
KEEP_LOG_PREFIX = ('Program data:', 'Program log:', 'Program return:')


def now_utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save_json(path, obj, gz=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    if gz:
        with gzip.open(tmp, 'wt', compresslevel=6) as f:
            json.dump(obj, f, separators=(',', ':'))
    else:
        tmp.write_text(json.dumps(obj, indent=1))
    tmp.replace(path)


def load_json(path):
    path = Path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    return json.loads(path.read_text())


def compact_logs(logs):
    out = []
    for line in logs or []:
        if line.startswith(KEEP_LOG_PREFIX):
            out.append(line if len(line) <= 2000 else line[:2000] + '…')
        elif ' consumed ' in line and line.startswith('Program '):
            # "Program <id> consumed N of M compute units" -> "<id> consumed N"
            parts = line.split()
            if len(parts) >= 4:
                out.append('%s consumed %s' % (parts[1], parts[3]))
        elif 'failed' in line or 'Error' in line or 'error' in line:
            out.append(line[:600])
    return out


def compact_block(slot, b):
    txs = []
    n_vote = 0
    vote_fee = 0
    for t in b['transactions']:
        msg = t['transaction']['message']
        if VOTE in msg['accountKeys']:
            n_vote += 1
            vote_fee += t['meta']['fee']
            continue
        meta = t['meta']
        m = {k: meta.get(k) for k in ('err', 'fee', 'computeUnitsConsumed', 'costUnits', 'preBalances', 'postBalances', 'innerInstructions', 'loadedAddresses', 'returnData')}
        for side in ('preTokenBalances', 'postTokenBalances'):
            m[side] = [{'accountIndex': a['accountIndex'], 'mint': a['mint'], 'owner': a.get('owner'), 'programId': a.get('programId'),
                        'amount': a['uiTokenAmount']['amount'], 'decimals': a['uiTokenAmount']['decimals']} for a in meta.get(side) or []]
        m['logMessages'] = compact_logs(meta.get('logMessages'))
        if m['innerInstructions']:
            for group in m['innerInstructions']:
                for ix in group['instructions']:
                    ix.pop('stackHeight', None) if ix.get('stackHeight') in (None, 2) else None
        txs.append({'transaction': {'signatures': t['transaction']['signatures'][:1], 'message': {k: v for k, v in msg.items() if k != 'recentBlockhash'}},
                    'meta': m, 'version': t.get('version', 'legacy')})
    return {'slot': slot, 'blockTime': b['blockTime'], 'blockHeight': b['blockHeight'], 'blockhash': b['blockhash'], 'parentSlot': b['parentSlot'],
            'previousBlockhash': b['previousBlockhash'], 'n_tx': len(b['transactions']), 'n_vote': n_vote, 'vote_fee': vote_fee, 'transactions': txs}


def first_block_at_or_after(c, slot):
    """First produced slot >= slot (finalized)."""
    r = c.call('getBlocksWithLimit', [slot, 1, {'commitment': 'finalized'}])
    return r[0] if r else None


def find_start_slot(c, end_slot, start_ts, log):
    """Binary search the first produced block with blockTime >= start_ts (slots are ~0.4 s; search back from end)."""
    lo = max(0, end_slot - int((c.call('getBlockTime', [end_slot]) - start_ts) * 3.2) - 3000)
    hi = end_slot
    while lo < hi:
        mid = (lo + hi) // 2
        slot = first_block_at_or_after(c, mid)      # slot >= mid
        if c.call('getBlockTime', [slot]) < start_ts:
            lo = slot + 1                           # everything up to `slot` is too early
        else:
            hi = mid                                # a block at/after mid is in the window
    start = first_block_at_or_after(c, lo)
    prev = c.call('getBlocks', [max(0, start - 40), start - 1, {'commitment': 'finalized'}])
    prev_time = c.call('getBlockTime', [prev[-1]]) if prev else None
    log('start slot %d at %d (previous produced slot %s at %s)' % (start, c.call('getBlockTime', [start]), prev[-1] if prev else None, prev_time))
    return start, prev_time


def collect(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    logf = open(out / 'collect.log', 'a')

    def log(msg):
        line = '%s %s' % (now_utc(), msg)
        print(line, flush=True)
        logf.write(line + '\n')
        logf.flush()

    c = Client()
    mpath = out / 'manifest.json'
    if mpath.exists():
        m = load_json(mpath)
        log('resuming window %s .. %s (slots %d..%d)' % (m['start_utc'], m['end_utc'], m['start_slot'], m['end_slot']))
    else:
        end_slot = args.end_slot or c.call('getSlot', [{'commitment': 'finalized'}])
        # make sure the end slot is a produced block
        blk = c.call('getBlocks', [end_slot - 40, end_slot, {'commitment': 'finalized'}])
        end_slot = blk[-1]
        end_ts = c.call('getBlockTime', [end_slot])
        start_ts = end_ts - int(args.hours * 3600)
        start_slot, prev_time = find_start_slot(c, end_slot, start_ts, log)
        slots = c.call('getBlocks', [start_slot, end_slot, {'commitment': 'finalized'}])
        chosen = slots[::args.every] if args.every > 1 else slots
        leaders = {}
        try:
            s = start_slot
            while s <= end_slot:
                n = min(5000, end_slot - s + 1)
                for i, l in enumerate(c.call('getSlotLeaders', [s, n])):
                    leaders[str(s + i)] = l
                s += n
        except Exception as e:  # leaders are a nicety
            log('getSlotLeaders failed: %s' % str(e)[:200])
        save_json(out / 'leaders.json', leaders)
        m = {'chain': 'solana-mainnet', 'source': 'GetBlock JSON-RPC (tokens in getblock_keys.json, not recorded)', 'commitment': 'finalized',
             'block_params': BLOCK_PARAMS, 'compaction': 'votes dropped (counted per block), rewards off, logs reduced to data/log/return/error/consumed lines',
             'hours': args.hours, 'every': args.every, 'end_slot': end_slot, 'end_ts': end_ts, 'start_ts': start_ts, 'start_slot': start_slot,
             'start_utc': dt.datetime.fromtimestamp(start_ts, dt.timezone.utc).isoformat(), 'end_utc': dt.datetime.fromtimestamp(end_ts, dt.timezone.utc).isoformat(),
             'previous_slot_time': prev_time, 'produced_slots': len(slots), 'slot_span': end_slot - start_slot + 1, 'skipped_slots': end_slot - start_slot + 1 - len(slots),
             'chosen_slots': len(chosen), 'created_utc': now_utc()}
        save_json(out / 'slots.json', {'produced': slots, 'chosen': chosen})
        save_json(mpath, m)
        log('window %s .. %s: %d produced slots of %d, %d skipped; collecting %d blocks' % (m['start_utc'], m['end_utc'], len(slots), m['slot_span'], m['skipped_slots'], len(chosen)))
    slots = load_json(out / 'slots.json')
    chosen = slots['chosen']
    bdir = out / 'blocks'
    bdir.mkdir(exist_ok=True)
    todo = [s for s in chosen if not (bdir / ('%d.json.gz' % s)).exists()]
    log('%d of %d blocks already on disk; fetching %d with %d workers' % (len(chosen) - len(todo), len(chosen), len(todo), args.workers))
    done = 0
    t0 = time.time()
    lock = threading.Lock()
    failed = []

    def get(slot):
        try:
            b = c.call('getBlock', [slot, BLOCK_PARAMS], timeout=180)
        except RpcError as e:
            return slot, 'rpc error %s' % e
        except Exception as e:
            return slot, 'failed %s' % str(e)[:120]
        if not b:
            return slot, 'null block'
        if not m['start_ts'] <= b['blockTime'] <= m['end_ts']:
            return slot, 'blockTime %s outside pinned window' % b['blockTime']
        save_json(bdir / ('%d.json.gz' % slot), compact_block(slot, b), gz=True)
        return slot, None

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for slot, err in ex.map(get, todo):
            with lock:
                done += 1
                if err:
                    failed.append([slot, err])
                    log('slot %d: %s' % (slot, err))
                if done % 100 == 0 or done == len(todo):
                    el = time.time() - t0
                    log('fetched %d/%d (%.2f blocks/s, %.1f MB/s, %d transport errors), eta %.0f min' % (done, len(todo), done / el, c.bytes / el / 1e6, len(c.errors), (len(todo) - done) / max(done / el, 1e-9) / 60))
    m['collect_runs'] = m.get('collect_runs', []) + [{'utc': now_utc(), 'fetched': done, 'failed': failed, 'seconds': round(time.time() - t0, 1), 'rpc': c.stats()}]
    present = [s for s in chosen if (bdir / ('%d.json.gz' % s)).exists()]
    m['blocks_on_disk'] = len(present)
    if len(present) == len(chosen):
        m['block_file_sha256'] = {str(s): hashlib.sha256((bdir / ('%d.json.gz' % s)).read_bytes()).hexdigest() for s in chosen}
        m['completed_utc'] = now_utc()
    save_json(mpath, m)
    log('done: %d/%d blocks on disk, %d failed this run' % (len(present), len(chosen), len(failed)))


def verify(args):
    out = Path(args.out)
    m = load_json(out / 'manifest.json')
    slots = load_json(out / 'slots.json')
    produced = slots['produced']
    chosen = slots['chosen']
    problems = []
    prev = None
    n_tx = n_vote = 0
    for s in chosen:
        p = out / 'blocks' / ('%d.json.gz' % s)
        if not p.exists():
            problems.append('missing %d' % s)
            continue
        if 'block_file_sha256' in m and hashlib.sha256(p.read_bytes()).hexdigest() != m['block_file_sha256'].get(str(s)):
            problems.append('hash mismatch %d' % s)
        b = load_json(p)
        n_tx += b['n_tx']
        n_vote += b['n_vote']
        if m['every'] == 1 and prev is not None:
            if b['parentSlot'] != prev['slot'] or b['previousBlockhash'] != prev['blockhash']:
                problems.append('chain break at %d (parent %d vs %d)' % (s, b['parentSlot'], prev['slot']))
        if not m['start_ts'] <= b['blockTime'] <= m['end_ts']:
            problems.append('time outside window %d' % s)
        prev = b
    print(json.dumps({'chosen': len(chosen), 'produced': len(produced), 'transactions': n_tx, 'votes': n_vote, 'problems': problems[:20], 'n_problems': len(problems)}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('collect')
    a.add_argument('--out', required=True)
    a.add_argument('--hours', type=float, default=1.0)
    a.add_argument('--end-slot', type=int)
    a.add_argument('--every', type=int, default=1)
    a.add_argument('--workers', type=int, default=8)
    a.set_defaults(fn=collect)
    v = sub.add_parser('verify')
    v.add_argument('--out', required=True)
    v.set_defaults(fn=verify)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
