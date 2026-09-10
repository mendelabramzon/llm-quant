#!/usr/bin/env python3
"""Collect a trailing window of Ethereum mainnet blocks (full transactions) and their logs, then keep tailing the head.

Layout matches `eth_day_collect.py`: `<out>/raw/blocks/<n>.json.gz` and `<out>/raw/logs/<n>.json.gz`, plus `manifest.json`.
By default the window ends at the current head; --end-tag finalized pins a finalized window. Resuming collect keeps
both boundaries fixed; use tail to extend it. `tail` re-checks parent hashes and replaces reorganised blocks.
Receipts are not fetched.

    uv run python scripts/live_collect.py collect --out research/2026-09-06/live --hours 1
    uv run python scripts/live_collect.py tail --out research/2026-09-06/live        # keeps fetching new blocks until stopped
"""
import argparse
import collections
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import time
from pathlib import Path

from live_rpc import RPC, RPCError, hx

ROOT = Path(__file__).resolve().parents[1]


def utc(t=None):
    return dt.datetime.fromtimestamp(time.time() if t is None else t, dt.timezone.utc).isoformat(timespec='seconds')


def block_path(out, n):
    return Path(out) / 'raw' / 'blocks' / (str(n) + '.json.gz')


def logs_path(out, n):
    return Path(out) / 'raw' / 'logs' / (str(n) + '.json.gz')


def write_gz(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(value, f, separators=(',', ':'))
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def head(rpc, tag='latest'):
    b = rpc.call('eth_getBlockByNumber', [tag, False])
    return hx(b['number']), hx(b['timestamp']), b['hash']


def first_block_at(rpc, ts, head_number):
    """First block whose timestamp is >= ts, by binary search from a guess based on 12-second slots."""
    lo = max(0, head_number - int((time.time() - ts) / 12) - 600)
    hi = head_number
    while True:
        b = rpc.call('eth_getBlockByNumber', [hex(lo), False])
        if hx(b['timestamp']) < ts or lo == 0:
            break
        lo = max(0, lo - 600)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        b = rpc.call('eth_getBlockByNumber', [hex(mid), False])
        if hx(b['timestamp']) >= ts:
            hi = mid
        else:
            lo = mid
    return hi


def fetch_blocks(rpc, out, nums):
    blocks = rpc.batch([('eth_getBlockByNumber', [hex(n), True]) for n in nums])
    got = []
    for n, b in zip(nums, blocks):
        if b is None or hx(b['number']) != n:
            raise RPCError('block %d missing' % n)
        write_gz(block_path(out, n), b)
        got.append(b)
    return got


def fetch_logs(rpc, out, a, b, splits=None):
    res = rpc.call('eth_getLogs', [{'fromBlock': hex(a), 'toBlock': hex(b)}], allow_errors=True)
    if isinstance(res, dict) and 'error' in res:
        err = res['error']
        data = err.get('data') if isinstance(err.get('data'), dict) else {}
        to = hx(data['to']) if 'to' in data else None
        if a < b:
            cut = to if to is not None and a <= to < b else (a + b) // 2
            if splits is not None:
                splits.append((a, b, cut))
            return fetch_logs(rpc, out, a, cut, splits) + fetch_logs(rpc, out, cut + 1, b, splits)
        raise RPCError('logs %d: %s' % (a, rpc.clean(json.dumps(err))))
    by = collections.defaultdict(list)
    for l in res:
        by[hx(l['blockNumber'])].append(l)
    for n in range(a, b + 1):
        write_gz(logs_path(out, n), by.get(n, []))
    return res


def collect(args):
    if args.hours <= 0 or args.lag < 0 or min(args.workers, args.block_batch, args.log_range) < 1:
        raise ValueError('duration and batch sizes must be positive; lag must be nonnegative')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    mpath = out / 'manifest.json'
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    if manifest.get('first_block'):
        first = manifest['first_block']
        last = manifest.get('last_block', manifest.get('last_block_at_collect'))
        if last is None:
            raise ValueError('existing manifest has no pinned end block')
    else:
        if hx(rpc.call('eth_chainId', [])) != 1:
            raise RPCError('expected Ethereum mainnet chain id 1')
        tag = getattr(args, 'end_tag', 'latest')
        hn, hts, hh = head(rpc, tag)
        last = hn - args.lag
        if last < 0:
            raise ValueError('lag exceeds chain height')
        en, ets, eh = head(rpc, hex(last)) if args.lag else (hn, hts, hh)
        end = ets + 1  # exclusive bound includes the pinned endpoint block
        start = end - int(args.hours * 3600)
        first = first_block_at(rpc, start, last)
        manifest.update({'chain': 'ethereum', 'chain_id': 1, 'provider': 'Infura',
                         'window': 'trailing %.2f h ending at %s minus %d blocks' % (args.hours, tag, args.lag),
                         'window_definition': '[start_timestamp, end_timestamp)', 'end_tag': tag,
                         'start_timestamp': start, 'end_timestamp': end, 'start_utc': utc(start), 'end_utc': utc(end),
                         'first_block': first, 'last_block': last, 'last_block_at_collect': last,
                         'head_at_collect': {'number': hn, 'timestamp': hts, 'utc': utc(hts), 'hash': hh},
                         'endpoint': {'number': en, 'timestamp': ets, 'hash': eh},
                         'collect_started': utc(), 'keys_in_rotation': len(rpc.keys)})
        if tag == 'finalized':
            manifest['finalized_at_start'] = manifest['head_at_collect']
    (mpath).write_text(json.dumps(manifest, indent=2, sort_keys=True))
    missing_blocks = [n for n in range(first, last + 1) if not block_path(out, n).exists()]
    missing_logs = [n for n in range(first, last + 1) if not logs_path(out, n).exists()]
    print(json.dumps({'first': first, 'last': last, 'blocks': last - first + 1, 'missing_blocks': len(missing_blocks), 'missing_logs': len(missing_logs), 'start_utc': manifest.get('start_utc'), 'end_utc': manifest.get('end_utc')}), flush=True)
    runs, run = [], []
    for n in missing_logs:
        if run and (n != run[-1] + 1 or len(run) >= args.log_range):
            runs.append(run)
            run = []
        run.append(n)
    if run:
        runs.append(run)
    errors, splits = [], []
    started = time.monotonic()
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(fetch_blocks, rpc, out, missing_blocks[i:i + args.block_batch]) for i in range(0, len(missing_blocks), args.block_batch)]
        futs += [ex.submit(fetch_logs, rpc, out, r[0], r[-1], splits) for r in runs]
        for i, f in enumerate(cf.as_completed(futs)):
            try:
                f.result()
            except Exception as exc:
                errors.append(rpc.clean(str(exc)))
            if i % 25 == 0:
                print(json.dumps({'done': i + 1, 'of': len(futs), 'elapsed_s': int(time.monotonic() - started), **rpc.stats()}), flush=True)
    present_b = sum(block_path(out, n).exists() for n in range(first, last + 1))
    present_l = sum(logs_path(out, n).exists() for n in range(first, last + 1))
    manifest.update({'blocks_present': present_b, 'logs_present': present_l, 'complete': present_b == present_l == last - first + 1,
                     'collect_finished': utc(), 'collect_errors': errors[:20], 'log_range_splits': len(splits), 'rpc': rpc.stats()})
    mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(json.dumps({'complete': manifest['complete'], 'blocks_present': present_b, 'logs_present': present_l, 'errors': len(errors), 'seconds': int(time.monotonic() - started), **rpc.stats()}), flush=True)
    if not manifest['complete']:
        raise SystemExit('collection incomplete; resume the same output directory')


def chain_check(out, first, last):
    """Verify parent links of stored blocks; return the list of block numbers whose stored copy is inconsistent."""
    bad, prev = [], None
    for n in range(first, last + 1):
        p = block_path(out, n)
        if not p.exists():
            bad.append(n)
            prev = None
            continue
        b = read_gz(p)
        if prev is not None and b['parentHash'] != prev:
            bad.append(n - 1)
        prev = b['hash']
    return sorted(set(bad))


def tail_once(rpc, out, last_known, lag=0, reorg_depth=6):
    """Fetch every block above last_known up to head-lag, re-validating the last few stored blocks against the chain.
    Returns (new_block_numbers, replaced_block_numbers, head_number)."""
    hn, hts, hh = head(rpc)
    target = hn - lag
    new, replaced = [], []
    # recheck recent stored blocks by hash (cheap header calls)
    recheck = [n for n in range(max(last_known - reorg_depth + 1, 0), last_known + 1) if block_path(out, n).exists()]
    if recheck:
        hdrs = rpc.batch([('eth_getBlockByNumber', [hex(n), False]) for n in recheck])
        for n, h in zip(recheck, hdrs):
            if h and read_gz(block_path(out, n))['hash'] != h['hash']:
                replaced.append(n)
    if replaced:
        fetch_blocks(rpc, out, replaced)
        for n in replaced:
            fetch_logs(rpc, out, n, n)
    if target > last_known:
        nums = list(range(last_known + 1, target + 1))
        for i in range(0, len(nums), 4):
            fetch_blocks(rpc, out, nums[i:i + 4])
        for i in range(0, len(nums), 4):
            fetch_logs(rpc, out, nums[i], min(nums[-1], nums[i] + 3))
        new = nums
    return new, replaced, hn


def tail(args):
    out = Path(args.out)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    manifest = json.loads((out / 'manifest.json').read_text())
    last_known = max(int(p.name.split('.')[0]) for p in (out / 'raw' / 'blocks').glob('*.json.gz'))
    print(json.dumps({'tail_from': last_known + 1}), flush=True)
    while True:
        try:
            new, replaced, hn = tail_once(rpc, out, last_known, lag=args.lag)
            if new or replaced:
                last_known = max(last_known, *new) if new else last_known
                print(json.dumps({'t': utc(), 'new': new, 'replaced': replaced, 'head': hn, **rpc.stats()}), flush=True)
                manifest['last_block_tailed'] = last_known
                (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True))
        except RPCError as exc:
            print(json.dumps({'t': utc(), 'error': rpc.clean(str(exc))}), flush=True)
            time.sleep(5)
        time.sleep(args.poll)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['collect', 'tail'])
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-06' / 'live'))
    p.add_argument('--hours', type=float, default=1.0)
    p.add_argument('--end-tag', choices=['latest', 'safe', 'finalized'], default='latest',
                   help='collect: endpoint for a new window; resume preserves its original boundaries')
    p.add_argument('--lag', type=int, default=0, help='stay this many blocks behind the head')
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--block-batch', type=int, default=4)
    p.add_argument('--log-range', type=int, default=6)
    p.add_argument('--poll', type=float, default=3.0)
    p.add_argument('--max-credits', type=int, default=6_000_000)
    args = p.parse_args()
    {'collect': collect, 'tail': tail}[args.command](args)


if __name__ == '__main__':
    main()
