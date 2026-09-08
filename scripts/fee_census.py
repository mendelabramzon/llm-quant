#!/usr/bin/env python3
"""Who pays what for Ethereum blockspace in a window, and where the money goes.

This exists because of a number the trailing-hour scan could not explain. On 2026-09-08 06:23-07:23 UTC the L1 base
fee sat at 0.049 gwei — the whole chain burned 0.44 ETH in an hour — while the single busiest sender on the chain
was paying 2.06 gwei on 1,335 USDT transfers. A base fee near zero does not mean blockspace is free; it means the
*protocol* stopped charging for it and whatever is still being paid is going somewhere else. This measures where.

`analyze` needs gas actually used, which the live collector does not fetch, so `receipts` pulls `eth_getBlockReceipts`
for every block in the window (1,000 credits a block) and caches them next to the raw blocks. Everything after that
is offline.

    uv run --with pycryptodome python scripts/fee_census.py receipts --out research/2026-09-08/live_1h_b
    uv run --with pycryptodome python scripts/fee_census.py analyze  --out research/2026-09-08/live_1h_b
"""
import argparse
import collections
import concurrent.futures as cf
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from live_rpc import RPC, hx


def rpath(out, n):
    return Path(out) / 'raw' / 'receipts' / (str(n) + '.json.gz')


def blocks_in(out):
    d = Path(out) / 'raw' / 'blocks'
    return sorted(int(p.name.split('.')[0]) for p in d.glob('*.json.gz'))


def census_blocks(out, every):
    """The blocks the census runs on. `every > 1` takes a regular subsample, which is what makes a ten-hour window
    affordable: receipts are a 1,000-credit call, so 2,993 blocks is 3M credits against 750k at every=4. A regular
    stride is used rather than a random sample so the series stays evenly spaced in time and the diurnal profile is
    not distorted; the sampling share is recorded in the output and every rate is reported per-gas, not per-block, so
    the estimate does not depend on the sampled blocks being average-sized."""
    nums = blocks_in(out)
    return nums[::every] if every > 1 else nums


def cmd_receipts(args):
    out = Path(args.out)
    # eth_getBlockReceipts is a 1,000-credit call and the keys throttle on sustained batches of them, so this is
    # paced deliberately rather than fanned out the way block fetching is.
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits, interval=args.interval)
    target = census_blocks(out, args.every)
    want = [n for n in target if not rpath(out, n).exists()]
    print(json.dumps({'blocks': len(blocks_in(out)), 'census_blocks': len(target), 'every': args.every, 'missing': len(want)}))

    def fetch(chunk):
        res = rpc.batch([('eth_getBlockReceipts', [hex(n)]) for n in chunk])
        for n, r in zip(chunk, res):
            if not r:
                raise RuntimeError('no receipts for %d' % n)
            p = rpath(out, n)
            p.parent.mkdir(parents=True, exist_ok=True)
            # keep only the four fields the census needs; receipts with logs are ~50x larger
            slim = [{'h': x['transactionHash'], 'f': x['from'], 't': x.get('to'),
                     'gu': hx(x['gasUsed']), 'egp': hx(x['effectiveGasPrice']), 'st': hx(x.get('status') or '0x1')}
                    for x in r]
            with gzip.open(p, 'wt') as f:
                json.dump(slim, f, separators=(',', ':'))
        return len(chunk)

    chunks = [want[i:i + args.chunk] for i in range(0, len(want), args.chunk)]
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(fetch, chunks):
            done += r
            if done % 50 < 5:
                print(json.dumps({'done': done, 'of': len(want), 'credits': rpc.credits}))
    print(json.dumps({'complete': True, 'blocks': len(want), **rpc.stats()}))
    return 0


def cmd_analyze(args):
    out = Path(args.out)
    eth = args.eth_usd
    if eth is None:
        hs = json.loads((out / 'head_state.json').read_text())
        eth = hs['feeds']['ETH']['usd']
    nums = [n for n in census_blocks(out, args.every) if rpath(out, n).exists()]
    all_blocks = blocks_in(out)
    base, ts = {}, {}
    for n in nums:
        with gzip.open(Path(out) / 'raw' / 'blocks' / (str(n) + '.json.gz'), 'rt') as f:
            b = json.load(f)
        base[n] = hx(b['baseFeePerGas'])
        ts[n] = hx(b['timestamp'])
    burn = tip = 0
    gas_total = 0
    by_sender = collections.defaultdict(lambda: {'txs': 0, 'gas': 0, 'tip_wei': 0, 'burn_wei': 0, 'failed': 0})
    by_target = collections.defaultdict(lambda: {'txs': 0, 'gas': 0, 'tip_wei': 0})
    tip_gwei_weighted = []
    failed_gas = 0
    n_tx = 0
    buckets = collections.OrderedDict()   # the diurnal profile: is the ratio a property of the hour, or of the chain?
    for n in nums:
        p = rpath(out, n)
        if not p.exists():
            continue
        with gzip.open(p, 'rt') as f:
            rs = json.load(f)
        bf = base[n]
        for x in rs:
            gu, egp = x['gu'], x['egp']
            t = max(egp - bf, 0)
            burn += gu * bf
            tip += gu * t
            gas_total += gu
            n_tx += 1
            s = by_sender[x['f'].lower()]
            s['txs'] += 1; s['gas'] += gu; s['tip_wei'] += gu * t; s['burn_wei'] += gu * bf
            if not x['st']:
                s['failed'] += 1
                failed_gas += gu
            if x['t']:
                d = by_target[x['t'].lower()]
                d['txs'] += 1; d['gas'] += gu; d['tip_wei'] += gu * t
            tip_gwei_weighted.append((t / 1e9, gu))
            bk = ts[n] - (ts[n] % (args.bucket * 60))
            bb = buckets.setdefault(bk, {'gas': 0, 'burn_wei': 0, 'tip_wei': 0, 'txs': 0, 'blocks': set(), 'base_wei': 0})
            bb['gas'] += gu; bb['burn_wei'] += gu * bf; bb['tip_wei'] += gu * t; bb['txs'] += 1
            bb['blocks'].add(n); bb['base_wei'] = bf

    tip_gwei_weighted.sort()
    cum, half = 0, gas_total / 2
    med_tip = 0.0
    for g, w in tip_gwei_weighted:
        cum += w
        if cum >= half:
            med_tip = g
            break
    # What the same gas would have cost at the gas-weighted median tip. The gap is not "waste" in any moral sense —
    # it buys inclusion certainty — but it is the price of a fee estimator that has not noticed the base fee move,
    # and it is paid to whoever builds the block rather than burned.
    overpay_wei = sum(max(g - med_tip, 0) * 1e9 * w for g, w in tip_gwei_weighted)

    def rows(d, key, n=15):
        return [{'address': a, **{k: v for k, v in r.items() if not k.endswith('_wei')},
                 'tip_eth': r['tip_wei'] / 1e18, 'tip_usd': r['tip_wei'] / 1e18 * eth,
                 'mean_tip_gwei': (r['tip_wei'] / r['gas'] / 1e9) if r['gas'] else 0}
                for a, r in sorted(d.items(), key=lambda kv: -kv[1][key])[:n]]

    series = []
    for k in sorted(buckets):
        b = buckets[k]
        series.append({'utc': __import__('datetime').datetime.fromtimestamp(k, __import__('datetime').timezone.utc).isoformat(timespec='minutes'),
                       'blocks_sampled': len(b['blocks']), 'txs': b['txs'], 'gas': b['gas'],
                       'base_fee_gwei': b['burn_wei'] / b['gas'] / 1e9 if b['gas'] else 0,
                       'mean_tip_gwei': b['tip_wei'] / b['gas'] / 1e9 if b['gas'] else 0,
                       'burn_usd': b['burn_wei'] / 1e18 * eth, 'tip_usd': b['tip_wei'] / 1e18 * eth,
                       'tip_over_burn': (b['tip_wei'] / b['burn_wei']) if b['burn_wei'] else None})

    A = {'window': str(out), 'blocks': len(nums), 'blocks_in_window': len(all_blocks),
         'sample_every': args.every, 'sample_share': len(nums) / max(len(all_blocks), 1),
         'series_bucket_minutes': args.bucket, 'series': series,
         'transactions': n_tx, 'eth_usd': eth,
         'gas_used': gas_total,
         'base_fee_burn_eth': burn / 1e18, 'base_fee_burn_usd': burn / 1e18 * eth,
         'priority_fees_eth': tip / 1e18, 'priority_fees_usd': tip / 1e18 * eth,
         'tip_over_burn_ratio': (tip / burn) if burn else None,
         'gas_weighted_median_tip_gwei': med_tip,
         'tip_above_median_eth': overpay_wei / 1e18, 'tip_above_median_usd': overpay_wei / 1e18 * eth,
         'failed_gas_share': failed_gas / gas_total if gas_total else 0,
         'top_tippers': rows(by_sender, 'tip_wei'),
         'top_gas_targets': rows(by_target, 'gas'),
         'note': ('figures are the totals over the %d sampled blocks (%.1f%% of the window); scale by the inverse '
                  'share for a window estimate, but the ratios and per-gas rates need no scaling. ' %
                  (len(nums), 100 * len(nums) / max(len(all_blocks), 1))) +
                 'the burn is protocol revenue destroyed; the priority fee is paid to the block builder and, through '
                 'the auction, to the proposer. When the ratio exceeds one the chain is charging less for its '
                 'blockspace than the private market clearing it is charging for position inside a block.'}
    (out / 'fee_census.json').write_text(json.dumps(A, indent=2, sort_keys=True))
    print(json.dumps({k: v for k, v in A.items() if not isinstance(v, (list, dict))}, indent=1))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('receipts'); r.set_defaults(fn=cmd_receipts)
    r.add_argument('--out', required=True); r.add_argument('--workers', type=int, default=3)
    r.add_argument('--chunk', type=int, default=2); r.add_argument('--interval', type=float, default=0.25)
    r.add_argument('--every', type=int, default=1, help='subsample: fetch receipts for every Nth block')
    r.add_argument('--max-credits', type=int, default=2_000_000)
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True); a.add_argument('--eth-usd', type=float, default=None)
    a.add_argument('--every', type=int, default=1); a.add_argument('--bucket', type=int, default=30)
    x = ap.parse_args()
    raise SystemExit(x.fn(x))


if __name__ == '__main__':
    main()
