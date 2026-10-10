#!/usr/bin/env python3
"""One capital pool behind every queue bid: how much of the separate books survives when they share it.

Why. The book carries four queue bids priced one at a time: weETH $194k a year at $10M, stETH $130k at $10M, rsETH $44k
at $3M, LBTC $111k at $10M (research/2026-10-09/redemption_history, research/2026-10-10/queue_bids_ext). Each was sized
as if it owned its capital, and each study found the same binding constraint: capital locked in the redemption queue.
The ROADMAP has twice noted that the three ETH bids "share one collateral pool in a stress" and are not additive, but
nobody measured how often the dislocations coincide. If they rarely do, one pool backs all four and the return on
capital is the sum over a fraction of the capital; if they coincide, the book's $479k is an overstatement.

How. `dislocation_history.simulate_bid` back-runs one asset's sells with capital that each fill locks for the queue's
wait. `simulate_book` is the same rule over the merged, time-ordered sells of several assets: every sell is priced with
its own asset's queue wait, carry, venue-median discount cap and fees, and fills from one shared pool. With one asset
it reproduces `simulate_bid` exactly (tested). The hurdle is chosen on the first half of the common window and tested
once on the second (`backtest.choose_then_test`), as in the per-asset studies.

Inputs are the per-asset priced swaps the surface analysis writes (`swaps_<key>.jsonl.gz`) plus the queue state in the
same directory; nothing is fetched.

    uv run --with pycryptodome python scripts/queue_book.py analyze --long <dir with swaps_lido/kelp> --out research/2026-10-10/queue_book
    uv run --with pycryptodome python scripts/queue_book.py render --out research/2026-10-10/queue_book
"""
import argparse
import collections
import gzip
import heapq
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B                      # noqa: E402
import dislocation_history as D           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
QB = ROOT / 'research' / '2026-10-10' / 'queue_bids_ext' / 'raw'
# (asset key, directory holding its swaps file and queue state, the size the book quotes it at)
DEFAULT_ASSETS = [('lido', None, 10_000_000), ('etherfi_ev', QB / 'etherfi_long', 10_000_000),
                  ('kelp', None, 3_000_000), ('lbtc_cb', QB / 'new_assets', 10_000_000)]
BOOK_QUOTE_USD = {'lido': 130_000, 'etherfi_ev': 194_000, 'kelp': 44_000, 'lbtc_cb': 111_000}
SIZES = [1_000_000, 3_000_000, 5_000_000, 10_000_000, 15_000_000, 20_000_000, 30_000_000, 50_000_000]
SETS = {'eth3': ['lido', 'etherfi_ev', 'kelp'], 'all4': ['lido', 'etherfi_ev', 'kelp', 'lbtc_cb']}
UNBOUNDED = 1e15


def load_env(k, out):
    """Everything `simulate_bid` needs for asset k, rebuilt the way `cmd_surface_analyze` builds it, from saved files."""
    out = Path(out)
    a = D.SURFACE[k]
    r = a['redemption']
    man, headers, state = D.read_json(out / 'manifest.json'), D.read_json(out / 'headers.json'), D.read_json(out / 'state.json')
    if not (man and headers and state):
        raise SystemExit('%s: %s lacks manifest/headers/state' % (k, out))
    hb = sorted(int(x) for x in headers)
    hts = [headers[str(n)]['ts'] for n in hb]
    first_ts, last_ts = headers[str(man['first_block'])]['ts'], headers[str(man['last_block'])]['ts']

    def ts_at(n):
        return int(round(D.interp(hb, hts, n)))
    lido_series = [(s['ts'], s['value']) for s in state['samples'].get('wsteth_nav', [])]
    ssr_series = [(s['ts'], s['value']) for s in state['samples'].get('susds_nav', [])]
    staking_apr = D.apr_from_nav(lido_series) or D.ETH_STAKING_FALLBACK
    ssr_fn = D.trailing_rate_fn(ssr_series, 1.0, D.SSR_FALLBACK)
    if a['unit'] == 'ETH':
        carry = (lambda ts: staking_apr / 365.0 * 1e4)
    elif a['unit'] == 'BTC':
        carry = (lambda ts: D.BTC_CARRY_APR / 365.0 * 1e4)
    else:
        carry = (lambda ts: (ssr_fn(ts) or D.SSR_FALLBACK) / 365.0 * 1e4)
    if r.get('exit_cap_usd_per_day') or r.get('daily_cap_state'):
        raise SystemExit('%s: daily exit caps are not modelled here' % k)
    path = out / ('swaps_%s.jsonl.gz' % k)
    if not path.exists():
        raise SystemExit('%s: %s missing; run dislocation_history.py analyze --assets %s --out %s' % (k, path, k, out))
    kept = []
    with gzip.open(path, 'rt') as f:
        for line in f:
            kept.append(json.loads(line))
    kept.sort(key=lambda s: (s['ts'], s.get('block') or 0))
    sells = [s for s in kept if s['side'] == 'sell']
    queue_logs = list(D.load_stream(out, 'x_queues'))
    wait_fn, wait_summary = D.wait_model(k, out, state, queue_logs, ts_at, last_ts)
    return {'key': k, 'unit': a['unit'], 'label': a.get('label', k), 'sells': sells, 'swaps': len(kept),
            'market': D.market_discount_fn(kept), 'wait': wait_fn, 'carry': carry, 'accrues': r.get('accrues', False),
            'redemption_fee_bps': r.get('fee_bps', 0.0), 'first_ts': first_ts, 'last_ts': last_ts,
            'staking_apr': staking_apr, 'wait_summary': wait_summary, 'dir': str(out)}


def simulate_book(envs, size_usd, hurdle_bps, fee_legs=D.FEE_LEGS, gas_usd=D.GAS_PER_FILL_USD,
                  min_fill_usd=D.MIN_FILL_USD, use_market_cap=True, trace=None, delay_s=0):
    """`simulate_bid` over several assets' sells at once, filled from one pool of `size_usd`.

    `envs` maps key -> env (see `load_env`; `sells` sorted by ts). Every sell is priced with its own asset's wait, carry,
    venue-median cap and redemption fee; a fill locks its capital for that asset's wait. Ties in time keep each asset's
    order and break across assets by key, so the result is deterministic. `trace`, if a dict, receives
    {day: max capital locked that day}. `delay_s` is the late-entry test: a sell is only taken when the market (the
    venue median) already showed an edge above the hurdle `delay_s` earlier, i.e. by a bidder who starts that late
    in every episode. Returns (fills, stats)."""
    merged = []
    for k in sorted(envs):
        e = envs[k]
        ck = ('_edges', fee_legs, use_market_cap, delay_s)
        if ck not in e:               # edge and wait do not depend on size or hurdle: price each sell once
            rows = []
            for s in e['sells']:
                wait = e['wait'](s['ts'])
                carry = 0.0 if e['accrues'] else wait * e['carry'](s['ts'])
                disc = s['discount_bps'] - fee_legs * s['fee_bps']
                if use_market_cap:
                    m = e['market'](s['ts'])
                    if m is not None:
                        disc = min(disc, m - s['fee_bps'])
                seen = float('inf')
                if delay_s:
                    mp = e['market'](s['ts'] - delay_s)
                    seen = (mp - s['fee_bps'] - carry - e['redemption_fee_bps']) if mp is not None else float('-inf')
                rows.append((disc - carry - e['redemption_fee_bps'], wait, seen))
            e[ck] = rows
        for i, s in enumerate(e['sells']):
            merged.append((s['ts'], k, i))
    merged.sort()
    heap, locked = [], 0.0
    fills = []
    st = {'qualifying_sells': 0, 'qualifying_usd': 0.0, 'filled_usd': 0.0, 'missed_capital_usd': 0.0,
          'by_asset_filled_usd': collections.defaultdict(float), 'by_asset_value_usd': collections.defaultdict(float)}
    for ts, k, i in merged:
        e = envs[k]
        s = e['sells'][i]
        while heap and heap[0][0] <= ts:
            locked -= heapq.heappop(heap)[1]
        edge, wait, seen = e[('_edges', fee_legs, use_market_cap, delay_s)][i]
        if edge <= hurdle_bps or seen <= hurdle_bps or s['usd'] * edge / 1e4 <= gas_usd:
            continue
        st['qualifying_sells'] += 1
        st['qualifying_usd'] += s['usd']
        avail = max(0.0, size_usd - locked)
        fill = min(s['usd'], avail)
        if fill < s['usd']:
            st['missed_capital_usd'] += s['usd'] - fill
        value = fill * edge / 1e4 - gas_usd
        if fill < min_fill_usd or value <= 0:
            continue
        st['filled_usd'] += fill
        st['by_asset_filled_usd'][k] += fill
        st['by_asset_value_usd'][k] += value
        fills.append({'asset': k, 'ts': ts, 'usd': fill, 'edge_bps': edge, 'value_usd': value, 'wait_days': wait,
                      'discount_bps': s['discount_bps'], 'pool': s.get('pool'), 'tx': s.get('tx')})
        if wait > 0:
            heapq.heappush(heap, (ts + wait * 86400.0, fill))
            locked += fill
        if trace is not None:
            d = int(ts // 86400)
            trace[d] = max(trace.get(d, 0.0), locked)
    st['by_asset_filled_usd'] = dict(st['by_asset_filled_usd'])
    st['by_asset_value_usd'] = dict(st['by_asset_value_usd'])
    return fills, st


def locked_daily(fills, first_day, n_days):
    """Capital locked at the end of each day, from fills alone (fill at ts, released after its wait)."""
    v = [0.0] * n_days
    for f in fills:
        a = int(f['ts'] // 86400) - first_day
        b = int((f['ts'] + f['wait_days'] * 86400.0) // 86400) - first_day
        for d in range(max(0, a), min(n_days, b + 1)):
            v[d] += f['usd']
    return v


def corr(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx > 0 and syy > 0 else None


def run_choice(envs, size, first_day, n_days, hurdles=D.HURDLES_BPS, delay_s=0):
    """The per-asset studies' protocol on a book: one daily value series per hurdle, chosen on the first half."""
    variants, per = {}, {}
    for h in hurdles:
        fills, st = simulate_book(envs, size, h, delay_s=delay_s)
        variants['h=%g' % h] = D.daily_values(fills, first_day, n_days)
        per['h=%g' % h] = (fills, st)
    ct = B.choose_then_test(variants, frac=0.5, periods_per_year=365, key='ann_return')
    chosen = ct['chosen']
    oos = variants[chosen][ct['cutoff_index']:]
    boot = B.block_bootstrap(oos, block=7, n=2000)
    fills, st = per[chosen]
    by_asset_oos = collections.defaultdict(float)
    cut_day = first_day + ct['cutoff_index']
    for f in fills:
        if int(f['ts'] // 86400) >= cut_day:
            by_asset_oos[f['asset']] += f['value_usd']
    years_oos = (n_days - ct['cutoff_index']) / 365.0
    return {'chosen_hurdle': chosen, 'in_sample_usd_per_year': ct['in_sample'].get('ann_return'),
            'out_of_sample_usd_per_year': ct['out_of_sample'].get('ann_return'), 'oos_t': ct['oos_t'],
            'oos_rank_of_chosen': ct['oos_rank'],
            'oos_ci95_usd_per_year': [boot['lo'] * 365 if boot['lo'] is not None else None,
                                      boot['hi'] * 365 if boot['hi'] is not None else None],
            'by_hurdle_oos_usd_per_year': {v: sum(x[ct['cutoff_index']:]) / years_oos for v, x in variants.items()},
            'oos_by_asset_usd_per_year': {k: v / years_oos for k, v in sorted(by_asset_oos.items())},
            'fills': len(fills), 'filled_usd': st['filled_usd'], 'missed_capital_usd': st['missed_capital_usd'],
            'cutoff_utc': D.utc(cut_day * 86400)}, fills


def cmd_analyze(args):
    t0 = time.monotonic()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    long_dir = Path(args.long) if args.long else None
    envs = {}
    for k, d, _ in DEFAULT_ASSETS:
        d = d or long_dir
        if d is None:
            raise SystemExit('--long is required for %s' % k)
        envs[k] = load_env(k, d)
        print('loaded', k, len(envs[k]['sells']), 'sells', flush=True)
    first_ts = max(e['first_ts'] for e in envs.values())
    last_ts = min(e['last_ts'] for e in envs.values())
    first_day, n_days = first_ts // 86400, int((last_ts - first_ts) // 86400) + 1
    res = {'generated': D.utc(), 'window': [D.utc(first_ts), D.utc(last_ts)], 'days': n_days,
           'assets': {k: {'label': e['label'], 'unit': e['unit'], 'dir': e['dir'], 'sells': len(e['sells']),
                          'swaps': e['swaps'], 'staking_apr': e['staking_apr'],
                          'wait_median_days': e['wait_summary'].get('median_days')} for k, e in envs.items()},
           'parameters': {'fee_legs': D.FEE_LEGS, 'gas_per_fill_usd': D.GAS_PER_FILL_USD, 'min_fill_usd': D.MIN_FILL_USD,
                          'hurdles_bps': D.HURDLES_BPS, 'sizes_usd': SIZES, 'book_sizes_usd': {k: s for k, _, s in DEFAULT_ASSETS},
                          'book_quotes_usd_per_year': BOOK_QUOTE_USD}}

    # 1. Each asset alone, on the common window: the reproduction check against the book's quotes.
    alone = {}
    for k, _, book_size in DEFAULT_ASSETS:
        alone[k] = {}
        for size in sorted(set(SIZES + [book_size])):
            r, _ = run_choice({k: envs[k]}, size, first_day, n_days)
            alone[k][str(size)] = r
        print('alone', k, {s: round(v['out_of_sample_usd_per_year'] or 0) for s, v in alone[k].items()}, flush=True)
    res['alone'] = alone
    res['separate_at_book_sizes'] = {
        'capital_usd': sum(s for _, _, s in DEFAULT_ASSETS),
        'oos_usd_per_year': sum(alone[k][str(s)]['out_of_sample_usd_per_year'] or 0.0 for k, _, s in DEFAULT_ASSETS),
        'by_asset': {k: alone[k][str(s)]['out_of_sample_usd_per_year'] for k, _, s in DEFAULT_ASSETS}}

    # 2. The shared pool.
    joint = {}
    for name, keys in SETS.items():
        sub = {k: envs[k] for k in keys}
        joint[name] = {}
        for size in SIZES:
            r, _ = run_choice(sub, size, first_day, n_days)
            joint[name][str(size)] = r
        print('joint', name, {s: round(v['out_of_sample_usd_per_year'] or 0) for s, v in joint[name].items()}, flush=True)
    res['joint'] = joint

    # 2b. Late entry: the same books when every episode is joined an hour, or a day, after it became visible.
    late = {}
    for name in SETS:
        sub = {k: envs[k] for k in SETS[name]}
        for size in (10_000_000, 15_000_000, 20_000_000):
            base = joint[name][str(size)]['out_of_sample_usd_per_year'] or 0.0
            for lbl, d in (('1h', 3600), ('1d', 86400)):
                r, _ = run_choice(sub, size, first_day, n_days, delay_s=d)
                late['%s|%d|%s' % (name, size, lbl)] = {
                    'out_of_sample_usd_per_year': r['out_of_sample_usd_per_year'], 'chosen_hurdle': r['chosen_hurdle'],
                    'oos_t': r['oos_t'], 'kept_share': (r['out_of_sample_usd_per_year'] or 0.0) / base if base else None}
    res['late_entry'] = late

    # 2c. Is the out-of-sample value one stress or many months? Value by month at the chosen hurdle.
    conc = {}
    for size in (10_000_000, 15_000_000, 20_000_000):
        r = joint['all4'][str(size)]
        h = float(r['chosen_hurdle'].split('=')[1])
        fills, _ = simulate_book(envs, size, h)
        cut = first_day + B.cutoff_index(n_days, 0.5)          # the split choose_then_test used
        bym = collections.defaultdict(float)
        for f in fills:
            if int(f['ts'] // 86400) >= cut:
                bym[D.utc(f['ts'])[:7]] += f['value_usd']
        tot = sum(bym.values())
        top = sorted(bym.values(), reverse=True)
        conc[str(size)] = {'hurdle_bps': h, 'oos_value_by_month_usd': dict(sorted(bym.items())),
                           'top_month_share': top[0] / tot if tot else None,
                           'top_two_months_share': sum(top[:2]) / tot if tot else None}
    res['concentration'] = conc
    print('late', {k: round(v['kept_share'] or 0, 2) for k, v in late.items()}, flush=True)

    # 3. How often the dislocations coincide: capital each asset would lock with unbounded capital, day by day, at the
    #    hurdle the four-asset book chose at $10M.
    h = float(joint['all4'][str(10_000_000)]['chosen_hurdle'].split('=')[1])
    demand = {}
    for k in envs:
        fills, _ = simulate_book({k: envs[k]}, UNBOUNDED, h)
        demand[k] = locked_daily(fills, first_day, n_days)
    tot = [sum(demand[k][d] for k in envs) for d in range(n_days)]
    eth_tot = [sum(demand[k][d] for k in SETS['eth3']) for d in range(n_days)]
    pairs = {}
    ks = sorted(envs)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            a, b = demand[ks[i]], demand[ks[j]]
            both = sum(1 for d in range(n_days) if a[d] > 0 and b[d] > 0)
            either = sum(1 for d in range(n_days) if a[d] > 0 or b[d] > 0)
            pairs['%s|%s' % (ks[i], ks[j])] = {'corr_daily_locked': corr(a, b), 'days_both_locked': both,
                                               'days_either_locked': either,
                                               'jaccard': both / either if either else None}
    res['overlap'] = {
        'hurdle_bps': h,
        'peak_locked_usd': {k: max(v) for k, v in demand.items()},
        'sum_of_peaks_usd': sum(max(v) for v in demand.values()),
        'peak_of_sum_usd': max(tot), 'peak_of_sum_eth3_usd': max(eth_tot),
        'p90_of_sum_usd': D.pct(tot, 0.9), 'p99_of_sum_usd': D.pct(tot, 0.99),
        'days_with_any_locked': sum(1 for x in tot if x > 0),
        'peak_day_utc': D.utc((first_day + tot.index(max(tot))) * 86400),
        'pairs': pairs,
        'locked_by_month_max_usd': {m: max(tot[d] for d in range(n_days) if D.utc((first_day + d) * 86400)[:7] == m)
                                    for m in sorted({D.utc((first_day + d) * 86400)[:7] for d in range(n_days)})},
    }
    res['seconds'] = time.monotonic() - t0
    D.write_json(out / 'analysis.json', res)
    D.write_json(out / 'manifest.json', {
        'generated': res['generated'], 'inputs': {k: e['dir'] for k, e in envs.items()},
        'note': 'inputs are the priced swaps and queue state of the per-asset studies; nothing fetched. lido and kelp '
                'swaps were regenerated in a scratch copy of research/2026-10-09/redemption_history/raw/long with '
                '`dislocation_history.py analyze --assets lido,kelp` (the original directory predates the swaps files)',
        'window': res['window']})
    print('done', round(res['seconds']), 's')


def fmt(v):
    return '—' if v is None else '$%s' % format(int(round(v)), ',')


def cmd_render(args):
    out = Path(args.out)
    a = D.read_json(out / 'analysis.json')
    L = ['# Queue bids on one capital pool — tables', '',
         'Window %s → %s (%d days); hurdle chosen on the first half, tested once on the second.' % (a['window'][0], a['window'][1], a['days']), '']
    L += ['## Each asset alone (out of sample, $ a year)', '', '| asset | ' + ' | '.join('$%gM' % (int(s) / 1e6) for s in sorted(a['alone'][next(iter(a['alone']))], key=int)) + ' |',
          '|---|' + '---:|' * len(a['alone'][next(iter(a['alone']))])]
    for k, v in a['alone'].items():
        L.append('| %s | %s |' % (k, ' | '.join(fmt(v[s]['out_of_sample_usd_per_year']) for s in sorted(v, key=int))))
    sep = a['separate_at_book_sizes']
    L += ['', 'Separate books at the book sizes: %s of capital, %s a year out of sample.' % (fmt(sep['capital_usd']), fmt(sep['oos_usd_per_year'])), '']
    L += ['## One pool', '', '| set | pool | chosen | out of sample | t | 95% interval | by asset |', '|---|---:|---|---:|---:|---|---|']
    for name, rows in a['joint'].items():
        for s in sorted(rows, key=int):
            r = rows[s]
            ci = r['oos_ci95_usd_per_year']
            L.append('| %s | $%gM | %s | %s | %s | %s – %s | %s |' % (
                name, int(s) / 1e6, r['chosen_hurdle'], fmt(r['out_of_sample_usd_per_year']),
                '%.2f' % r['oos_t'] if r['oos_t'] is not None else '—', fmt(ci[0]), fmt(ci[1]),
                ', '.join('%s %s' % (k, fmt(v)) for k, v in r['oos_by_asset_usd_per_year'].items())))
    o = a['overlap']
    L += ['', '## How often the dislocations coincide (unbounded capital, hurdle %g bp)' % o['hurdle_bps'], '',
          '- Peak capital each asset would lock: ' + ', '.join('%s %s' % (k, fmt(v)) for k, v in o['peak_locked_usd'].items()),
          '- Sum of the peaks %s; peak of the sum %s (ETH three: %s); 99th percentile of the sum %s; 90th %s.' % (
              fmt(o['sum_of_peaks_usd']), fmt(o['peak_of_sum_usd']), fmt(o['peak_of_sum_eth3_usd']), fmt(o['p99_of_sum_usd']), fmt(o['p90_of_sum_usd'])),
          '- Busiest day %s; days with any capital locked: %d.' % (o['peak_day_utc'], o['days_with_any_locked']), '',
          '| pair | correlation of daily locked capital | days both locked | days either | overlap |', '|---|---:|---:|---:|---:|']
    for p, v in o['pairs'].items():
        L.append('| %s | %s | %d | %d | %s |' % (p, '%.2f' % v['corr_daily_locked'] if v['corr_daily_locked'] is not None else '—',
                                               v['days_both_locked'], v['days_either_locked'],
                                               '%.0f%%' % (100 * v['jaccard']) if v['jaccard'] is not None else '—'))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('analyze')
    a.add_argument('--out', required=True)
    a.add_argument('--long', help='directory holding swaps_lido/kelp.jsonl.gz and the long-window queue state')
    r = sub.add_parser('render')
    r.add_argument('--out', required=True)
    args = p.parse_args()
    {'analyze': cmd_analyze, 'render': cmd_render}[args.cmd](args)


if __name__ == '__main__':
    main()
