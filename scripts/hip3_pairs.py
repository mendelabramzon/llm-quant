#!/usr/bin/env python3
"""The same underlying on two HIP-3 builder books: does the funding difference pay, net of the round trips?

Why. The book's `hip3-cross-builder-funding` was quoted once, on 2026-09-10, from a snapshot (UNITREE at 307 points
between Paragon and XYZ, priced at $25k because the small book was that thin). A funding difference between two books
of one name is only a strategy if it lasts longer than the two round trips it costs to hold, and a snapshot cannot say
how long. The perp history store holds every hour of both books' funding and prices since 2026-07-01, so the pair can
be held on paper.

Position p on a pair (A, B): +1 is long A and short B. One hour returns p (r_A - r_B) - p (f_A - f_B), where f is
Hyperliquid's hourly funding rate (positive: longs pay) and r the close-to-close price return. The rule: at each hour,
with the trailing-k mean of f_A - f_B through the previous hour, hold the pair that receives the difference (p = -1
when A's longs pay more) while its magnitude exceeds X a year; leave below X/2. A position change costs half of each
leg's round trip per leg traded. (k, X) are chosen on hours before 2026-09-10 13:00 UTC and tested after, through
backtest.choose_then_test. The two books have independent oracles, so the pair is neutral in the underlying, not in
the oracles; their disagreement is inside r_A - r_B and is reported.

    uv run python scripts/hip3_pairs.py analyze --hl research/2026-10-09/perps_hip3 --out research/2026-10-09/hip3_pairs
    uv run python scripts/hip3_pairs.py render  --out research/2026-10-09/hip3_pairs
"""
import argparse
import datetime as dt
import gzip
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

HOUR_MS = 3_600_000
HOURS_PER_YEAR = 8760.0
UTC = dt.timezone.utc
CUTOFF = '2026-09-10T13:00:00+00:00'
DEFAULT_RT_BPS = 40.0     # a builder book with no priced round trip is charged this per leg: io:NBIS was 44bp at $100k


def safe(coin):
    return coin.replace(':', '__').replace('/', '_')


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def utc_iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).isoformat()


def pairs_in(universe):
    """Every (A, B) of builder markets sharing a base name, both with open interest. Core markets are excluded: a core
    listing of the same ticker is a different asset (a crypto token), never an equity."""
    by = {}
    for m in universe:
        if m['dex'] == 'core' or not (m.get('oi') or 0) > 0:
            continue
        by.setdefault(m['coin'].split(':')[-1], []).append(m['coin'])
    out = []
    for base, coins in sorted(by.items()):
        coins = sorted(coins)
        for i in range(len(coins)):
            for j in range(i + 1, len(coins)):
                out.append((coins[i], coins[j]))
    return out


def hourly(fund_rows, candle_rows):
    """{bar end ms: (rate, close)}: candles keyed by bar end, funding by the hour it pays for."""
    f = {int((int(r['time']) + HOUR_MS // 2) // HOUR_MS * HOUR_MS): float(r['fundingRate']) for r in fund_rows}
    c = {int(x['t']) + HOUR_MS: float(x['c']) for x in candle_rows}
    return {t: (f.get(t), c[t]) for t in c}


def align(a, b):
    """Rows over hours both books printed: {'t', 'fa', 'fb', 'ra', 'rb'}; returns need the previous hour on both."""
    ts = sorted(set(a) & set(b))
    rows = []
    for i, t in enumerate(ts):
        fa, ca = a[t]
        fb, cb = b[t]
        prev = ts[i - 1] if i else None
        ok = prev is not None and prev == t - HOUR_MS
        rows.append({'t': t, 'fa': fa, 'fb': fb,
                     'ra': (ca / a[prev][1] - 1.0) if ok else None, 'rb': (cb / b[prev][1] - 1.0) if ok else None})
    return rows


def pair_return(p, ra, rb, fa, fb):
    """One hour of position p (+1 long A short B): p (r_A - r_B) - p (f_A - f_B)."""
    return p * (ra - rb) - p * (fa - fb)


def run_rule(rows, k, x, rt_a_bps, rt_b_bps):
    """Returns (hourly returns, positions, entries) for the trailing-k / X rule; decisions use data through i-1."""
    rets, pos_s = [], []
    hist = []
    p = 0
    entries = 0
    for r in rows:
        tr = statistics.fmean(hist[-k:]) * HOURS_PER_YEAR if len(hist) >= k else None
        want = p
        if tr is not None:
            target = -1 if tr > 0 else 1
            if p == 0 and abs(tr) >= x:
                want = target
            elif p != 0 and (abs(tr) < x / 2 or target != p):
                want = target if abs(tr) >= x else 0
        cost = 0.0
        if want != p:
            legs = abs(want - p)                     # 1 = open or close, 2 = flip
            cost = legs * (rt_a_bps + rt_b_bps) / 2.0 / 1e4
            entries += 1 if want != 0 else 0
            p = want
        g = 0.0
        if p and r['ra'] is not None and r['rb'] is not None and r['fa'] is not None and r['fb'] is not None:
            g = pair_return(p, r['ra'], r['rb'], r['fa'], r['fb'])
        rets.append(g - cost)
        pos_s.append(p)
        if r['fa'] is not None and r['fb'] is not None:
            hist.append(r['fa'] - r['fb'])
    return rets, pos_s, entries


def decompose(rows, pos):
    fund = basis = 0.0
    for r, p in zip(rows, pos):
        if p and r['ra'] is not None and r['rb'] is not None and r['fa'] is not None and r['fb'] is not None:
            fund += -p * (r['fa'] - r['fb'])
            basis += p * (r['ra'] - r['rb'])
    return {'funding': fund, 'basis': basis}


def load_round_trips(window_analysis):
    """Round trip at $100k per market from a perp window's analysis.json, where the book was priced."""
    if not window_analysis or not Path(window_analysis).exists():
        return {}
    A = json.loads(Path(window_analysis).read_text())
    return {r['coin']: (r.get('book') or {}).get('round_trip_bps_100k') for r in A.get('assets', [])}


def cmd_analyze(args):
    hl, out = Path(args.hl), Path(args.out)
    uni = json.loads((hl / 'universe.json').read_text())['markets']
    rts = load_round_trips(args.window)
    oi = {m['coin']: m.get('oi') for m in uni}
    mark = {m['coin']: m.get('mark') for m in uni}
    cut = int(dt.datetime.fromisoformat(args.cutoff).timestamp() * 1000)
    ks = [int(v) for v in args.lookbacks.split(',')]
    xs = [float(v) for v in args.entries.split(',')]
    res = {'generated': dt.datetime.now(UTC).isoformat(), 'cutoff': args.cutoff, 'hl_store': str(hl),
           'round_trips_from': args.window, 'default_rt_bps': DEFAULT_RT_BPS, 'pairs': []}
    pooled_oos = []
    for a, b in pairs_in(uni):
        fa, fb = hl / 'funding' / (safe(a) + '.json.gz'), hl / 'funding' / (safe(b) + '.json.gz')
        ca, cb = hl / 'candles_1h' / (safe(a) + '.json.gz'), hl / 'candles_1h' / (safe(b) + '.json.gz')
        if not all(p.exists() for p in (fa, fb, ca, cb)):
            continue
        rows = align(hourly(read_gz(fa), read_gz(ca)), hourly(read_gz(fb), read_gz(cb)))
        if len(rows) < 24 * 14:
            continue
        rt_a = rts.get(a) or DEFAULT_RT_BPS
        rt_b = rts.get(b) or DEFAULT_RT_BPS
        n = len(rows)
        ci = next((i for i, r in enumerate(rows) if r['t'] >= cut), n)
        diffs = [r['fa'] - r['fb'] for r in rows if r['fa'] is not None and r['fb'] is not None]
        rec = {'a': a, 'b': b, 'hours': n, 'first': utc_iso(rows[0]['t']), 'last': utc_iso(rows[-1]['t']),
               'rt_a_bps': rt_a, 'rt_b_bps': rt_b, 'rt_priced': [a in rts and rts[a] is not None, b in rts and rts[b] is not None],
               'oi_usd': [(oi.get(a) or 0) * (mark.get(a) or 0), (oi.get(b) or 0) * (mark.get(b) or 0)],
               'diff_apr_mean': statistics.fmean(diffs) * HOURS_PER_YEAR if diffs else None,
               'diff_apr_abs_median': statistics.median(abs(d) for d in diffs) * HOURS_PER_YEAR if diffs else None,
               'basis_sd_hourly': statistics.pstdev([r['ra'] - r['rb'] for r in rows if r['ra'] is not None and r['rb'] is not None])}
        if 0 < ci < n:
            variants = {}
            for k in ks:
                for x in xs:
                    variants['k=%dh,X=%d%%' % (k, round(100 * x))] = run_rule(rows, k, x, rt_a, rt_b)[0]
            sel = B.choose_then_test(variants, frac=ci / n, periods_per_year=HOURS_PER_YEAR)
            k = int(sel['chosen'].split(',')[0][2:-1])
            x = float(sel['chosen'].split('X=')[1][:-1]) / 100.0
            rets, pos, entries = run_rule(rows, k, x, rt_a, rt_b)
            oos = rets[ci:]
            pooled_oos.append(oos)
            rec.update({'selection': {kk: sel[kk] for kk in ('chosen', 'n_variants', 'oos_rank', 'oos_t', 'oos_p',
                                                               'deflated_sharpe_in_sample', 'in_sample', 'out_of_sample')},
                        'oos_total': sum(oos), 'oos_hours_held': sum(1 for p in pos[ci:] if p),
                        'entries_total': entries,
                        'oos_components': decompose(rows[ci:], pos[ci:]),
                        'is_components': decompose(rows[:ci], pos[:ci])})
        res['pairs'].append(rec)
        print('%-14s %-14s hours %5d  diff |median| %6.0f%%  %s' % (
            a, b, n, 100 * (rec['diff_apr_abs_median'] or 0),
            ('chosen %s OOS total %+.2f%% held %dh' % (rec['selection']['chosen'], 100 * rec['oos_total'], rec['oos_hours_held']))
            if 'selection' in rec else 'no out-of-sample period'), flush=True)
    if pooled_oos:
        # equal-weight across pairs, hour by hour (pairs share the calendar after the cutoff)
        m = min(len(x) for x in pooled_oos)
        port = [statistics.fmean(x[i] for x in pooled_oos) for i in range(m)]
        t, p = B.newey_west_t(port, lags=48)
        res['pooled_oos'] = {'pairs': len(pooled_oos), 'hours': m, 'perf': B.perf(port, HOURS_PER_YEAR),
                             'nw_t': t, 'nw_p': p, 'bootstrap': B.block_bootstrap(port, block=24, n=1000)}
    write_json(out / 'analysis.json', res)
    return 0


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# HIP-3 cross-builder pairs — tables', '', 'Generated %s; cutoff %s; round trips from `%s` (default %.0fbp per leg where a book was not priced).'
         % (A['generated'], A['cutoff'], A['round_trips_from'], A['default_rt_bps']), '',
         '| pair | hours | |f_A − f_B| median | chosen | IS ann. | OOS total | OOS held h | OOS funding | OOS basis | OOS t |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for r in A['pairs']:
        s = r.get('selection') or {}
        c = r.get('oos_components') or {}
        L.append('| %s / %s | %d | %.0f%% | %s | %s | %s | %s | %s | %s | %s |' % (
            r['a'], r['b'], r['hours'], 100 * (r['diff_apr_abs_median'] or 0), s.get('chosen', '—'),
            ('%.0f%%' % (100 * s['in_sample']['ann_return'])) if s.get('in_sample', {}).get('ann_return') is not None else '—',
            ('%+.2f%%' % (100 * r['oos_total'])) if 'oos_total' in r else '—', r.get('oos_hours_held', '—'),
            ('%+.2f%%' % (100 * c['funding'])) if c else '—', ('%+.2f%%' % (100 * c['basis'])) if c else '—',
            ('%.2f' % s['oos_t']) if s.get('oos_t') is not None else '—'))
    po = A.get('pooled_oos')
    if po:
        L += ['', 'Pooled out of sample, equal weight across %d pairs over %d hours: annualised %.1f%%, Sharpe %s, Newey–West t %.2f, bootstrap mean CI [%.2e, %.2e].'
              % (po['pairs'], po['hours'], 100 * po['perf']['ann_return'],
                 ('%.2f' % po['perf']['sharpe']) if po['perf'].get('sharpe') is not None else '—', po['nw_t'] or 0,
                 po['bootstrap']['lo'], po['bootstrap']['hi'])]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--hl', default='research/2026-10-09/perps_hip3')
    a.add_argument('--out', required=True)
    a.add_argument('--window', default='research/2026-09-10/perps_2/analysis.json')
    a.add_argument('--cutoff', default=CUTOFF)
    a.add_argument('--lookbacks', default='6,24,72')
    a.add_argument('--entries', default='0.5,1.0,2.0,3.0')
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
