#!/usr/bin/env python3
"""Bounded, read-only collection of an Ethereum mainnet window: full blocks plus every log.

Blocks come from eth_getBlockByNumber(n, true) in batches; logs from unfiltered eth_getLogs over short
block ranges that split themselves on Infura's 10,000-result cap. Receipts are not fetched here (they cost
1000 credits per block); status and gas used are fetched later only for selected transactions. Responses are
gzip-encoded on the wire. Everything is saved raw, one gzip file per block for blocks and one for logs,
with a manifest of hashes; `verify` cross-checks logs against blocks offline and rechecks a sample of block
hashes on the chain. Resumable: existing files are skipped. No key is written to output.
"""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import queue
import threading
import time

from onchain_probe import ROOT, RPC, RPCError, hx, save, utc, first_block_at

CHAIN = 'ethereum'


def parse_utc(s):
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())


def block_path(out, n):
    return out / 'raw' / 'blocks' / (str(n) + '.json.gz')


def logs_path(out, n):
    return out / 'raw' / 'logs' / (str(n) + '.json.gz')


def write_gz(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(value, f, separators=(',', ':'))
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def collect(args):
    if args.hours <= 0 or args.workers < 1 or args.block_batch < 1 or args.log_range < 1:
        raise ValueError('Duration, worker count and range sizes must be positive')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rpc = RPC(out, key_index=args.key_index, max_credits=args.max_credits, interval=args.interval, rate=args.rate)
    mpath = out / 'manifest.json'
    if mpath.exists():
        manifest = json.loads(mpath.read_text())
        first, last = manifest['first_block'], manifest['last_block']
    else:
        cid, fin = rpc.batch(CHAIN, [('eth_chainId', []), ('eth_getBlockByNumber', ['finalized', False])])
        if hx(cid) != 1:
            raise RPCError('Unexpected chain id')
        end = parse_utc(args.end) if args.end != 'finalized' else hx(fin['timestamp']) + 1
        start = end - int(args.hours * 3600)
        if end > hx(fin['timestamp']) + 1:
            raise RPCError('Window end is not yet finalized')
        first = first_block_at(rpc, CHAIN, start, fin)
        last = hx(fin['number']) if end > hx(fin['timestamp']) else first_block_at(rpc, CHAIN, end, fin) - 1
        manifest = {'chain': CHAIN, 'chain_id': 1, 'provider': 'Infura', 'started_at': utc(), 'key_index': args.key_index,
                    'window_definition': '[start_timestamp, end_timestamp)', 'start_timestamp': start, 'end_timestamp': end,
                    'start_utc': utc(start), 'end_utc': utc(end), 'first_block': first, 'last_block': last,
                    'finalized_at_start': {'number': hx(fin['number']), 'hash': fin['hash'], 'timestamp': hx(fin['timestamp'])},
                    'method': {'blocks': 'eth_getBlockByNumber(n, true) in batches of ' + str(args.block_batch),
                               'logs': 'eth_getLogs without address filter over ranges of up to ' + str(args.log_range) + ' blocks, split on the 10,000-result cap',
                               'receipts': 'not collected; fetched per selected transaction by the analysis'},
                    'errors': {}}
        save(mpath, manifest)
    print(json.dumps({'first': first, 'last': last, 'blocks': last - first + 1, 'start': manifest['start_utc'], 'end': manifest['end_utc']}), flush=True)
    if args.reuse:
        source = Path(args.reuse)
        manifest['cache_source'] = str(source)
        import shutil
        for n in range(first, last + 1):
            for path_fn in (block_path, logs_path):
                src, dst = path_fn(source, n), path_fn(out, n)
                if src.exists() and not dst.exists():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
    missing_blocks = [n for n in range(first, last + 1) if not block_path(out, n).exists()]
    missing_logs = [n for n in range(first, last + 1) if not logs_path(out, n).exists()]
    tasks = queue.Queue()
    for i in range(0, len(missing_blocks), args.block_batch):
        tasks.put(('blocks', missing_blocks[i:i + args.block_batch]))
    runs, run = [], []
    for n in missing_logs:
        if run and (n != run[-1] + 1 or len(run) >= args.log_range):
            runs.append(run)
            run = []
        run.append(n)
    if run:
        runs.append(run)
    for r in runs:
        tasks.put(('logs', r[0], r[-1]))
    print(json.dumps({'block_tasks': (len(missing_blocks) + args.block_batch - 1) // args.block_batch, 'log_tasks': len(runs)}), flush=True)
    state = {'blocks': 0, 'logs': 0, 'log_entries': 0, 'errors': [], 'splits': 0}
    lock = threading.Lock()
    stop = threading.Event()

    def do_blocks(nums):
        blocks = rpc.batch(CHAIN, [('eth_getBlockByNumber', [hex(n), True]) for n in nums])
        for n, b in zip(nums, blocks):
            if b is None or hx(b['number']) != n:
                raise RPCError('Block ' + str(n) + ' missing or mismatched')
            write_gz(block_path(out, n), b)
        with lock:
            state['blocks'] += len(nums)

    def do_logs(a, b):
        res = rpc.call(CHAIN, 'eth_getLogs', [{'fromBlock': hex(a), 'toBlock': hex(b)}], allow_errors=True)
        if isinstance(res, dict) and 'error' in res:
            err = res['error']
            data = err.get('data') if isinstance(err.get('data'), dict) else {}
            to = hx(data['to']) if 'to' in data else None
            if a < b:
                cut = to if to is not None and a <= to < b else (a + b) // 2
                with lock:
                    state['splits'] += 1
                tasks.put(('logs', a, cut))
                tasks.put(('logs', cut + 1, b))
                return
            raise RPCError('logs ' + str(a) + ': ' + rpc.clean(json.dumps(err)))
        by = collections.defaultdict(list)
        for l in res:
            by[hx(l['blockNumber'])].append(l)
        for n in range(a, b + 1):
            write_gz(logs_path(out, n), by.get(n, []))
        with lock:
            state['logs'] += b - a + 1
            state['log_entries'] += len(res)

    def worker():
        while not stop.is_set():
            try:
                task = tasks.get(timeout=2)
            except queue.Empty:
                if tasks.unfinished_tasks == 0:
                    return
                continue
            try:
                if task[0] == 'blocks':
                    do_blocks(task[1])
                else:
                    do_logs(task[1], task[2])
            except RPCError as exc:
                msg = rpc.clean(str(exc))
                with lock:
                    state['errors'].append({'task': task[0], 'range': task[1:] if task[0] == 'logs' else [task[1][0], task[1][-1]], 'error': msg})
                print(json.dumps({'error': msg, 'task': task[0]}), flush=True)
                if 'ceiling' in msg:
                    stop.set()
            finally:
                tasks.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(args.workers)]
    started, started_utc = time.monotonic(), utc()
    for t in threads:
        t.start()
    last_print = 0
    while any(t.is_alive() for t in threads):
        time.sleep(5)
        if time.monotonic() - last_print >= 60:
            last_print = time.monotonic()
            with lock:
                print(json.dumps({'elapsed_s': int(time.monotonic() - started), 'blocks': state['blocks'], 'logs_blocks': state['logs'],
                                  'log_entries': state['log_entries'], 'splits': state['splits'], 'errors': len(state['errors']),
                                  'credits': rpc.credits, 'queued': tasks.qsize()}), flush=True)
    manifest['collection_runs'] = manifest.get('collection_runs', []) + [
        {'started_at': started_utc, 'finished_at': utc(), 'blocks_fetched': state['blocks'],
         'log_blocks_fetched': state['logs'], 'log_entries': state['log_entries'], 'range_splits': state['splits'],
         'errors': state['errors'][:50], 'estimated_credits': rpc.credits, 'seconds': int(time.monotonic() - started)}]
    manifest['blocks_present'] = sum(block_path(out, n).exists() for n in range(first, last + 1))
    manifest['logs_present'] = sum(logs_path(out, n).exists() for n in range(first, last + 1))
    manifest['complete'] = manifest['blocks_present'] == last - first + 1 and manifest['logs_present'] == last - first + 1
    save(mpath, manifest)
    print(json.dumps({'finished': True, 'complete': manifest['complete'], 'blocks_present': manifest['blocks_present'],
                      'logs_present': manifest['logs_present'], 'errors': len(state['errors']), 'credits': rpc.credits}), flush=True)


def verify(args):
    """Offline cross-checks plus a bounded onchain recheck of block hashes."""
    out = Path(args.out)
    manifest = json.loads((out / 'manifest.json').read_text())
    first, last = manifest['first_block'], manifest['last_block']
    rows, problems, previous = [], collections.Counter(), None
    txs_total, logs_total = 0, 0
    for n in range(first, last + 1):
        bp, lp = block_path(out, n), logs_path(out, n)
        if not bp.exists() or not lp.exists():
            problems['missing_file'] += 1
            continue
        b, logs = read_gz(bp), read_gz(lp)
        issues = []
        if previous and b['parentHash'] != previous:
            issues.append('parent_hash_mismatch')
        previous = b['hash']
        hashes = {t['hash'] for t in b['transactions']}
        idx = {t['hash']: hx(t['transactionIndex']) for t in b['transactions']}
        if any(l['blockHash'] != b['hash'] or hx(l['blockNumber']) != n for l in logs):
            issues.append('log_block_mismatch')
        if any(l['transactionHash'] not in hashes for l in logs):
            issues.append('log_tx_not_in_block')
        if any(hx(l['transactionIndex']) != idx.get(l['transactionHash']) for l in logs):
            issues.append('log_tx_index_mismatch')
        if any(l.get('removed') for l in logs):
            issues.append('removed_log')
        li = [hx(l['logIndex']) for l in logs]
        if len(li) != len(set(li)) or (li and (min(li) != 0 or max(li) != len(li) - 1)):
            issues.append('log_index_gap')
        if b['logsBloom'] == '0x' + '0' * 512 and logs:
            issues.append('bloom_empty_with_logs')
        if b['logsBloom'] != '0x' + '0' * 512 and not logs:
            issues.append('bloom_nonempty_without_logs')
        ts = hx(b['timestamp'])
        if not manifest['start_timestamp'] <= ts < manifest['end_timestamp']:
            issues.append('timestamp_outside_window')
        for i in issues:
            problems[i] += 1
        txs_total += len(hashes)
        logs_total += len(logs)
        rows.append({'number': n, 'hash': b['hash'], 'timestamp': ts, 'transactions': len(hashes), 'logs': len(logs),
                     'gas_used': hx(b['gasUsed']), 'base_fee_wei': hx(b.get('baseFeePerGas', 0)), 'miner': b['miner'].lower(),
                     'issues': issues, 'block_sha256': hashlib.sha256(bp.read_bytes()).hexdigest(), 'logs_sha256': hashlib.sha256(lp.read_bytes()).hexdigest()})
    rechecked = []
    if not args.offline and rows:
        rpc = RPC(out, key_index=manifest.get('key_index', 0), max_credits=args.max_credits, interval=.5)
        sample = sorted({rows[0]['number'], rows[-1]['number']} | {r['number'] for r in rows[::args.recheck_every]})
        for i in range(0, len(sample), 10):
            part = sample[i:i + 10]
            got = rpc.batch(CHAIN, [('eth_getBlockByNumber', [hex(n), False]) for n in part])
            byn = {r['number']: r['hash'] for r in rows}
            rechecked.extend({'number': n, 'matches': g['hash'] == byn[n]} for n, g in zip(part, got))
        fin = rpc.call(CHAIN, 'eth_getBlockByNumber', ['finalized', False])
        manifest['finalized_at_verify'] = {'number': hx(fin['number']), 'hash': fin['hash'], 'timestamp': hx(fin['timestamp'])}
    manifest.update(verified_at=utc(), blocks=len(rows), transactions=txs_total, logs=logs_total, quality_issues=dict(problems),
                    hash_recheck={'sampled': len(rechecked), 'mismatches': [r['number'] for r in rechecked if not r['matches']]} if rechecked else manifest.get('hash_recheck'))
    save(out / 'manifest.json', manifest)
    save(out / 'blocks_manifest.json', {'first_block': first, 'last_block': last, 'blocks': rows})
    print(json.dumps({'blocks': len(rows), 'transactions': txs_total, 'logs': logs_total, 'quality_issues': dict(problems),
                      'hash_recheck': manifest.get('hash_recheck')}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['collect', 'verify'])
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-05' / 'eth_day'))
    p.add_argument('--end', default='finalized', help='exclusive UTC end, or finalized for latest finalized block')
    p.add_argument('--hours', type=float, default=24)
    p.add_argument('--reuse', help='copy matching raw block/log files from an earlier collection')
    p.add_argument('--key-index', type=int, default=0)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--block-batch', type=int, default=4)
    p.add_argument('--log-range', type=int, default=8)
    p.add_argument('--rate', type=int, default=400, help='estimated credits per second across all workers')
    p.add_argument('--interval', type=float, default=.2)
    p.add_argument('--max-credits', type=int, default=1500000)
    p.add_argument('--offline', action='store_true', help='verify: skip the onchain hash recheck')
    p.add_argument('--recheck-every', type=int, default=500)
    args = p.parse_args()
    {'collect': collect, 'verify': verify}[args.command](args)


if __name__ == '__main__':
    main()
