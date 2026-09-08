#!/usr/bin/env python3
"""Collect a trailing window of every perpetual market on Hyperliquid — the first-party one and every HIP-3
builder-deployed DEX — into a replayable window directory.

Why this exists. Every study in this repo so far has read *settlement*: transfers, lending state, bridge legs. A perp
DEX settles almost nothing on chain; what it produces is a price, a funding rate and an open-interest number, and the
value in it is in the relationships between those three across venues and over time. That needs its own collector.

HIP-3 makes it more interesting than a single venue. A deployer stakes HYPE, gets to list markets, **sets the oracle
themselves**, and can charge an extra fee share of 0–300%. So the same underlying — AAPL, GOLD, SP500 — can exist on
several independently-operated books with independently-operated oracles, per-asset open-interest caps, and different
fee scales. That is a price surface with real dispersion and a real capacity limit, which is exactly the shape this
repo has learned to measure.

What a window holds:

    dexes.json            every perp DEX, its deployer, oracle updater, fee recipient and per-asset OI caps
    snap/<ts>.json.gz     metaAndAssetCtxs for every DEX: funding, OI, mark/oracle/mid, premium, impact prices, volume
    candles/<coin>.json.gz  1-minute OHLCV for the window, per asset, from candleSnapshot
    books/<coin>.json.gz  a full L2 book for the assets worth pricing depth on
    funding/<coin>.json.gz  realised hourly funding for the window
    predicted.json        Hyperliquid's own next-funding prediction beside Binance's and Bybit's, per coin
    manifest.json         what was asked for, what arrived, and what the API refused

    uv run python scripts/perp_collect.py window --out research/2026-09-08/perps_1h --hours 1
    uv run python scripts/perp_collect.py tape   --out research/2026-09-08/perps_1h --minutes 45 --every 20
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from perp_rpc import Info, APIError, perp_dexes, meta_and_ctxs, l2_book, candles, funding_history, predicted_fundings


def utc(t=None):
    return dt.datetime.fromtimestamp(time.time() if t is None else t, dt.timezone.utc).isoformat(timespec='seconds')


def write_gz(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(value, f, separators=(',', ':'))
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True))


def safe(coin):
    """A filename for an asset. HIP-3 names are `dex:SYMBOL`, and the colon is not portable."""
    return coin.replace(':', '__').replace('/', '_')


def dex_key(d):
    """The first entry of perpDexs is null and means the first-party HyperCore perp DEX, whose `dex` parameter is ''."""
    return '' if d is None else d['name']


def universe(out):
    """(dex, coin, meta) for every asset in the collected snapshots, from the newest snapshot present."""
    snaps = sorted((Path(out) / 'snap').glob('*.json.gz'))
    if not snaps:
        return []
    s = read_gz(snaps[-1])
    rows = []
    for dex, payload in s['dexes'].items():
        if not payload:
            continue
        for m, c in zip(payload[0]['universe'], payload[1]):
            rows.append((dex, m['name'], m, c))
    return rows


# ---------------------------------------------------------------------------------------------- snapshot

def take_snapshot(api, out, dexes):
    ts = time.time()
    payload = {}
    errs = {}

    def one(dk):
        try:
            return dk, meta_and_ctxs(api, dk)
        except APIError as e:
            return dk, {'error': str(e)[:200]}

    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for dk, v in ex.map(one, dexes):
            if isinstance(v, dict) and 'error' in v:
                errs[dk] = v['error']
            else:
                payload[dk] = v
    rec = {'ts': ts, 'utc': utc(ts), 'dexes': payload, 'errors': errs}
    write_gz(Path(out) / 'snap' / ('%d.json.gz' % int(ts)), rec)
    return rec


def cmd_tape(args):
    """Repeated snapshots of every market's state. One snapshot is a price; a tape is a premium series."""
    out = Path(args.out)
    api = Info()
    dexes = [dex_key(d) for d in json.loads((out / 'dexes.json').read_text())['raw']]
    t_end = time.time() + args.minutes * 60
    n = 0
    while time.time() < t_end:
        t0 = time.time()
        rec = take_snapshot(api, out, dexes)
        n += 1
        print(json.dumps({'snapshot': n, 'utc': rec['utc'],
                          'dexes': len(rec['dexes']), 'errors': len(rec['errors'])}), flush=True)
        time.sleep(max(0.0, args.every - (time.time() - t0)))
    print(json.dumps({'tape_complete': True, 'snapshots': n, **api.stats()}))
    return 0


# ---------------------------------------------------------------------------------------------- window

def cmd_window(args):
    out = Path(args.out)
    api = Info(interval=args.interval)
    t0 = time.time()
    end_ms = int(t0 * 1000)
    start_ms = end_ms - int(args.hours * 3600 * 1000)

    raw = perp_dexes(api)
    dexes = [dex_key(d) for d in raw]
    write_json(out / 'dexes.json', {'collected_at': utc(t0), 'raw': raw, 'keys': dexes})
    print(json.dumps({'perp_dexes': len(dexes), 'keys': dexes}), flush=True)

    snap = take_snapshot(api, out, dexes)
    uni = []
    for dex, payload in snap['dexes'].items():
        for m, c in zip(payload[0]['universe'], payload[1]):
            uni.append((dex, m['name'], m, c))
    print(json.dumps({'assets': len(uni), 'by_dex': {d: sum(1 for x in uni if x[0] == d) for d in dexes}}), flush=True)

    def ntl(c):
        try:
            return float(c.get('dayNtlVlm') or 0)
        except (TypeError, ValueError):
            return 0.0

    def oi_usd(m, c):
        try:
            return float(c.get('openInterest') or 0) * float(c.get('markPx') or c.get('oraclePx') or 0)
        except (TypeError, ValueError):
            return 0.0

    # Candles for everything: a market with no volume in the window is itself a finding (a listed market nobody
    # trades), and skipping it would make "how many of these markets are real" unanswerable.
    todo = [(d, name) for d, name, m, c in uni if not m.get('isDelisted')]
    print(json.dumps({'candles_requested': len(todo)}), flush=True)

    got = {'candles': 0, 'candles_empty': 0, 'candles_failed': 0}
    fails = {}

    def pull_candles(item):
        d, name = item
        p = out / 'candles' / (safe(name) + '.json.gz')
        if p.exists() and not args.force:
            return name, 'cached'
        try:
            rows = candles(api, name, args.interval_str, start_ms, end_ms)
        except APIError as e:
            return name, 'fail:' + str(e)[:120]
        write_gz(p, rows or [])
        return name, ('empty' if not rows else 'ok')

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, (name, status) in enumerate(ex.map(pull_candles, todo), 1):
            if status.startswith('fail'):
                got['candles_failed'] += 1
                fails[name] = status
            elif status == 'empty':
                got['candles_empty'] += 1
            else:
                got['candles'] += 1
            if i % 100 == 0:
                print(json.dumps({'candles_done': i, 'of': len(todo), **api.stats()}), flush=True)

    # Depth only where there is something to price: an order book on a market with no open interest and no volume
    # costs a request and answers a question nobody asked.
    ranked = sorted(uni, key=lambda x: -(ntl(x[3]) + oi_usd(x[2], x[3])))
    book_set = [(d, n) for d, n, m, c in ranked if (ntl(c) > 0 or oi_usd(m, c) > 0)][:args.books]
    print(json.dumps({'books_requested': len(book_set)}), flush=True)

    def pull_book(item):
        d, name = item
        try:
            b = l2_book(api, name)
        except APIError as e:
            return name, 'fail:' + str(e)[:120]
        write_gz(out / 'books' / (safe(name) + '.json.gz'), b)
        return name, 'ok'

    nb = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for name, status in ex.map(pull_book, book_set):
            if status == 'ok':
                nb += 1
            else:
                fails[name] = status

    # Realised funding, for the same set. `fundingHistory` is the settled series; the snapshot's `funding` field is
    # the current hourly rate, and the two disagreeing is a finding rather than an error.
    def pull_funding(item):
        d, name = item
        try:
            f = funding_history(api, name, end_ms - int(max(args.hours, 8) * 3600 * 1000), end_ms)
        except APIError as e:
            return name, 'fail:' + str(e)[:120]
        write_gz(out / 'funding' / (safe(name) + '.json.gz'), f or [])
        return name, 'ok'

    nf = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for name, status in ex.map(pull_funding, book_set):
            if status == 'ok':
                nf += 1
            else:
                fails[name] = status

    try:
        write_json(out / 'predicted.json', {'collected_at': utc(), 'rows': predicted_fundings(api)})
        pf = True
    except APIError as e:
        pf = False
        fails['predictedFundings'] = str(e)[:120]

    man = {
        'collected_at': utc(t0), 'finished_at': utc(),
        'venue': 'hyperliquid', 'info_url': 'https://api.hyperliquid.xyz/info',
        'window': {'start_ms': start_ms, 'end_ms': end_ms, 'hours': args.hours,
                   'start_utc': utc(start_ms / 1000), 'end_utc': utc(end_ms / 1000)},
        'candle_interval': args.interval_str,
        'dexes': dexes, 'assets': len(uni),
        'assets_by_dex': {d: sum(1 for x in uni if x[0] == d) for d in dexes},
        'candles': got, 'books': nb, 'funding_series': nf, 'predicted_fundings': pf,
        'failures': fails, 'api': api.stats(), 'seconds': round(time.time() - t0, 1),
    }
    write_json(out / 'manifest.json', man)
    print(json.dumps({k: v for k, v in man.items() if k not in ('failures', 'assets_by_dex')}, indent=1))
    return 0


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    w = sub.add_parser('window'); w.set_defaults(fn=cmd_window)
    w.add_argument('--out', required=True)
    w.add_argument('--hours', type=float, default=1.0)
    w.add_argument('--interval-str', default='1m')
    w.add_argument('--books', type=int, default=140)
    w.add_argument('--workers', type=int, default=4)
    w.add_argument('--interval', type=float, default=0.09)
    w.add_argument('--force', action='store_true')
    t = sub.add_parser('tape'); t.set_defaults(fn=cmd_tape)
    t.add_argument('--out', required=True)
    t.add_argument('--minutes', type=float, default=30)
    t.add_argument('--every', type=float, default=20)
    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == '__main__':
    main()
