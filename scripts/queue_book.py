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

kHYPE, the fifth bid (2026-10-11). Its dislocations were uncorrelated with the four Ethereum-side ones (-0.03 against
the three ETH bids summed), but its environment lived inside queue_bids_alt. `--khype <queue_bids_alt directory>` loads
it through `queue_bids_alt.khype_book_env` (swaps priced in HYPE, valued in USD at the HYPE close that study used;
HyperEVM's $1 gas and $1k minimum fill travel with the env and apply to kHYPE alone). The run checks itself twice
before it reports anything: kHYPE alone through this module's protocol must reproduce that study's stand-alone grid,
and all4 on its own window must still earn $409,889 at $15M. It then runs the same protocol (sizes, hurdle chosen on the
first half, late entry, monthly concentration, overlap of locked capital) on the five assets' common window, which
starts at kHYPE's first whole day (2025-07-15), for `all5` and `eth3_khype` and for all4 and eth3 on the same
shortened window, so kHYPE's increment is like for like.

    uv run --with pycryptodome python scripts/queue_book.py analyze --long <dir with swaps_lido/kelp> --out research/2026-10-10/queue_book
    uv run --with pycryptodome python scripts/queue_book.py render --out research/2026-10-10/queue_book
    uv run --with pycryptodome python scripts/queue_book.py analyze --long <dir> --khype research/2026-10-10/queue_bids_alt --out research/2026-10-11/queue_book5
    uv run --with pycryptodome python scripts/queue_book.py render --out research/2026-10-11/queue_book5
"""
import argparse
import bisect
import collections
import gzip
import heapq
from array import array
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
LATE_SIZES = (10_000_000, 15_000_000, 20_000_000)
# The fifth bid: kHYPE on HyperEVM, its environment exported by queue_bids_alt (`--khype <that study's directory>`).
KHYPE_DIR = ROOT / 'research' / '2026-10-10' / 'queue_bids_alt'
KHYPE_BOOK_SIZE = 10_000_000
SETS_KHYPE = {'all5': ['lido', 'etherfi_ev', 'kelp', 'lbtc_cb', 'khype'], 'eth3_khype': ['lido', 'etherfi_ev', 'kelp', 'khype'],
              'all4': SETS['all4'], 'eth3': SETS['eth3']}
REGRESSION = {'set': 'all4', 'size_usd': 15_000_000, 'out_of_sample_usd_per_year': 409_889,
              'source': 'research/2026-10-10/queue_book (all4 on its own window, 2024-09-26 -> 2026-10-09)'}


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
    market_in, first_in = trade_window_fns((s['ts'], s['pool'], s['discount_bps'], s['usd']) for s in kept)
    return {'key': k, 'unit': a['unit'], 'label': a.get('label', k), 'sells': sells, 'swaps': len(kept),
            'market': D.market_discount_fn(kept), 'wait': wait_fn, 'carry': carry, 'accrues': r.get('accrues', False),
            'redemption_fee_bps': r.get('fee_bps', 0.0), 'first_ts': first_ts, 'last_ts': last_ts,
            'staking_apr': staking_apr, 'wait_summary': wait_summary, 'dir': str(out),
            'market_in': market_in, 'first_in': first_in}


def window_fns_from_arrays(ts, pool, disc, usd):
    """(market_in, first_in) over priced trades held as parallel arrays sorted by (ts, pool, discount, usd).

    market_in(t0, t1): the median across venues of each venue's volume-weighted discount over the trades inside
    [t0, t1) only; first_in(t0, t1): the discount of the first trade at or after t0 and before t1. Both are None when
    nothing traded: unlike `market_discount_fn`, a quiet venue carries nothing forward. The semantics, sums and tie
    order are queue_live's `window_median` / `window_first`. Hour-aligned windows are cached."""
    n = len(ts)
    cache = {}

    def market_in(t0, t1):
        hour = t1 - t0 == 3600 and t0 % 3600 == 0
        if hour and t0 in cache:
            return cache[t0]
        lo, hi = bisect.bisect_left(ts, t0), bisect.bisect_left(ts, t1)
        v = None
        if lo < hi:
            acc = {}
            for j in range(lo, hi):
                a = acc.get(pool[j])
                if a is None:
                    a = acc[pool[j]] = [0.0, 0.0]
                a[0] += disc[j] * usd[j]
                a[1] += usd[j]
            vals = [x / y for x, y in acc.values() if y]
            v = statistics.median(vals) if vals else None
        if hour:
            cache[t0] = v
        return v

    def first_in(t0, t1):
        lo = bisect.bisect_left(ts, t0)
        return disc[lo] if lo < n and ts[lo] < t1 else None
    return market_in, first_in


def trade_window_fns(trades):
    """`window_fns_from_arrays` from an iterable of (ts, pool, discount_bps, usd), sorted here."""
    rows = sorted(trades)
    code = {p: j for j, p in enumerate(sorted({r[1] for r in rows}))}
    return window_fns_from_arrays(array('d', (r[0] for r in rows)), array('l', (code[r[1]] for r in rows)),
                                  array('d', (r[2] for r in rows)), array('d', (r[3] for r in rows)))


def load_khype_env(d=KHYPE_DIR):
    """kHYPE's `load_env`-shaped environment, rebuilt from queue_bids_alt's saved files (`khype_book_env`)."""
    import queue_bids_alt as QA
    return QA.khype_book_env(d)


def own_rows(e, fee_legs, use_market_cap, dk):
    """Per sell of env e: (edge priced at the sell's own print and hour, wait, edge the market showed `dk` earlier),
    cached on the env: edge and wait do not depend on size or hurdle."""
    ck = ('_edges', fee_legs, use_market_cap, dk)
    if ck not in e:
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
            if dk:
                mp = e['market'](s['ts'] - dk)
                seen = (mp - s['fee_bps'] - carry - e['redemption_fee_bps']) if mp is not None else float('-inf')
            rows.append((disc - carry - e['redemption_fee_bps'], wait, seen))
        e[ck] = rows
    return e[ck]


LATER = {'hour': 'bought at the next hour boundary H, priced over [H, H+1h)',
         'day': 'bought 24 hours after the sale, priced over [t+24h, t+25h)'}
LATER_PRICES = {'median': 'the venue median of the trades inside the later window (strict: no carry-forward)',
                'first': 'the first trade inside the later window'}


def later_rows(e, later, later_price='median', fee_legs=D.FEE_LEGS):
    """Per sell of env e: (purchase ts, edge at the later price or None, wait at the purchase), cached on the env. The
    later edge = min(print less `fee_legs` fees, later discount less one fee) - carry - redemption fee, with the carry
    and wait taken at the purchase (the withdrawal is requested then): queue_live's `later_rows`."""
    lk = ('_later', later, later_price, fee_legs)
    if lk not in e:
        fn = e['first_in'] if later_price == 'first' else e['market_in']
        rows = []
        for s in e['sells']:
            t = s['ts']
            buy = (int(t // 3600) + 1) * 3600 if later == 'hour' else t + 86400
            lp = fn(buy, buy + 3600)
            wait = e['wait'](buy)
            carry = 0.0 if e['accrues'] else wait * e['carry'](buy)
            base = s['discount_bps'] - fee_legs * s['fee_bps']
            rows.append((buy, None if lp is None else min(base, lp - s['fee_bps']) - carry - e['redemption_fee_bps'], wait))
        e[lk] = rows
    return e[lk]


def simulate_book(envs, size_usd, hurdle_bps, fee_legs=D.FEE_LEGS, gas_usd=D.GAS_PER_FILL_USD,
                  min_fill_usd=D.MIN_FILL_USD, use_market_cap=True, trace=None, delay_s=0, later=None, later_price='median'):
    """`simulate_bid` over several assets' sells at once, filled from one pool of `size_usd`.

    `envs` maps key -> env (see `load_env`; `sells` sorted by ts). Every sell is priced with its own asset's wait, carry,
    venue-median cap and redemption fee; a fill locks its capital for that asset's wait. Ties in time keep each asset's
    order and break across assets by key, so the result is deterministic. `trace`, if a dict, receives
    {day: max capital locked that day}. `delay_s` is the late-entry test: a sell is only taken when the market (the
    venue median) already showed an edge above the hurdle `delay_s` earlier, i.e. by a bidder who starts that late
    in every episode. An env may carry its own chain's `gas_usd` and `min_fill_usd` (kHYPE on HyperEVM: $1 and $1k,
    `queue_bids_alt.khype_book_env`); they replace `gas_usd` / `min_fill_usd` for that asset only. An env's own
    `delay_s` is a floor on `delay_s` for that asset alone (capital that has to cross chains before it can buy). An env
    without these keys is priced exactly as before.

    `later` makes the bidder executable: by default each sell is bought at its own print, capped at its own hour's venue
    median, which only a bidder trading right behind each seller gets. With `later='hour'` a sell that qualifies on that
    own-hour edge is bought at the next hour boundary H at `later_rows`' edge (the venue median of the trades inside
    [H, H+1h), or with `later_price='first'` the first trade after H), and skipped when nothing traded there or that edge
    is at or under the hurdle; `later='day'` buys 24 hours after the sell. Capital locks from the purchase for the wait
    at the purchase, and fills are dated at the purchase (queue_live's `simulate_later`, implementations f and g). The
    env needs `market_in` / `first_in` (`load_env`, `queue_bids_alt.khype_book_env`). Returns (fills, stats)."""
    gas_of = {k: envs[k].get('gas_usd', gas_usd) for k in envs}
    min_fill_of = {k: envs[k].get('min_fill_usd', min_fill_usd) for k in envs}
    delay_of = {k: max(delay_s, envs[k].get('delay_s', 0)) for k in envs}
    if later:
        return _simulate_later(envs, size_usd, hurdle_bps, fee_legs, use_market_cap, trace, later, later_price,
                               gas_of, min_fill_of, delay_of)
    merged = []
    for k in sorted(envs):
        own_rows(envs[k], fee_legs, use_market_cap, delay_of[k])
        for i, s in enumerate(envs[k]['sells']):
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
        edge, wait, seen = e[('_edges', fee_legs, use_market_cap, delay_of[k])][i]
        gas = gas_of[k]
        if edge <= hurdle_bps or seen <= hurdle_bps or s['usd'] * edge / 1e4 <= gas:
            continue
        st['qualifying_sells'] += 1
        st['qualifying_usd'] += s['usd']
        avail = max(0.0, size_usd - locked)
        fill = min(s['usd'], avail)
        if fill < s['usd']:
            st['missed_capital_usd'] += s['usd'] - fill
        value = fill * edge / 1e4 - gas
        if fill < min_fill_of[k] or value <= 0:
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


def _simulate_later(envs, size_usd, hurdle_bps, fee_legs, use_market_cap, trace, later, later_price, gas_of, min_fill_of,
                    delay_of):
    """`simulate_book` with `later` set: events ordered by (purchase, sell, asset key, index), as queue_live orders them."""
    events = []
    for k in sorted(envs):
        own_rows(envs[k], fee_legs, use_market_cap, delay_of[k])
        rows = later_rows(envs[k], later, later_price, fee_legs)
        for i, s in enumerate(envs[k]['sells']):
            events.append((rows[i][0], s['ts'], k, i))
    events.sort()
    heap, locked = [], 0.0
    fills = []
    st = {'qualifying_sells': 0, 'qualifying_usd': 0.0, 'filled_usd': 0.0, 'missed_capital_usd': 0.0, 'later_missing': 0,
          'later_below_hurdle': 0, 'by_asset_filled_usd': collections.defaultdict(float),
          'by_asset_value_usd': collections.defaultdict(float)}
    for buy, t, k, i in events:
        e = envs[k]
        s = e['sells'][i]
        while heap and heap[0][0] <= buy:
            locked -= heapq.heappop(heap)[1]
        own, _, seen = e[('_edges', fee_legs, use_market_cap, delay_of[k])][i]
        gas = gas_of[k]
        if own <= hurdle_bps or seen <= hurdle_bps or s['usd'] * own / 1e4 <= gas:
            continue
        st['qualifying_sells'] += 1
        st['qualifying_usd'] += s['usd']
        _, edge, wait = e[('_later', later, later_price, fee_legs)][i]
        if edge is None:
            st['later_missing'] += 1
            continue
        if edge <= hurdle_bps or s['usd'] * edge / 1e4 <= gas:
            st['later_below_hurdle'] += 1
            continue
        avail = max(0.0, size_usd - locked)
        fill = min(s['usd'], avail)
        if fill < s['usd']:
            st['missed_capital_usd'] += s['usd'] - fill
        value = fill * edge / 1e4 - gas
        if fill < min_fill_of[k] or value <= 0:
            continue
        st['filled_usd'] += fill
        st['by_asset_filled_usd'][k] += fill
        st['by_asset_value_usd'][k] += value
        fills.append({'asset': k, 'ts': buy, 'sell_ts': t, 'usd': fill, 'edge_bps': edge, 'own_edge_bps': own,
                      'value_usd': value, 'wait_days': wait, 'discount_bps': s['discount_bps'], 'pool': s.get('pool'),
                      'tx': s.get('tx')})
        if wait > 0:
            heapq.heappush(heap, (buy + wait * 86400.0, fill))
            locked += fill
        if trace is not None:
            d = int(buy // 86400)
            trace[d] = max(trace.get(d, 0.0), locked)
    st['by_asset_filled_usd'] = dict(st['by_asset_filled_usd'])
    st['by_asset_value_usd'] = dict(st['by_asset_value_usd'])
    return fills, st


def persistence(e, hurdle_bps=1.0, deep_bps=10.0, delays=('hour', 'day'), prices=('median', 'first'), fee_legs=D.FEE_LEGS):
    """Of the sells that qualified in their own hour (the own-hour edge above `hurdle_bps`), the share whose edge still
    clears it at the later price, by count and volume, for all of them and the deep ones (own edge above `deep_bps`):
    queue_live's `persistence_stats` for one env."""
    own = own_rows(e, fee_legs, True, 0)
    out = {}
    for delay in delays:
        for price in prices:
            rows = [(s, o[0], r[1]) for s, o, r in zip(e['sells'], own, later_rows(e, delay, price, fee_legs)) if o[0] > hurdle_bps]
            res = {}
            for tag, sub in (('all', rows), ('deep', [x for x in rows if x[1] > deep_bps])):
                n, vol = len(sub), sum(x[0]['usd'] for x in sub)
                ok = [x for x in sub if x[2] is not None and x[2] > hurdle_bps]
                miss = [x for x in sub if x[2] is None]
                res[tag] = {'qualifying': n, 'qualifying_usd': vol, 'still_clear_share': len(ok) / n if n else None,
                            'still_clear_usd_share': sum(x[0]['usd'] for x in ok) / vol if vol else None,
                            'later_missing_share': len(miss) / n if n else None,
                            'still_clear_share_of_those_traded': len(ok) / (n - len(miss)) if n > len(miss) else None,
                            'median_edge_kept': statistics.median([x[2] / x[1] for x in ok]) if ok else None}
            out['%s|%s' % (delay, price)] = res
    return out


def locked_daily(fills, first_day, n_days):
    """Capital locked at the end of each day, from fills alone (fill at ts, released after its wait)."""
    v = [0.0] * n_days
    for f in fills:
        a = int(f['ts'] // 86400) - first_day
        b = int((f['ts'] + f['wait_days'] * 86400.0) // 86400) - first_day
        for d in range(max(0, a), min(n_days, b + 1)):
            v[d] += f['usd']
    return v


def locked_end_of_day(fills, first_day, n_days):
    """Capital locked at each day's last second (an instant, so never above the pool), from fills alone. `locked_daily`
    counts a fill on every day it touches, so a day that releases and refills counts both."""
    v = [0.0] * n_days
    for f in fills:
        rel = f['ts'] + f['wait_days'] * 86400.0
        a = int(f['ts'] // 86400) - first_day
        for d in range(max(0, a), n_days):
            if (first_day + d + 1) * 86400 >= rel:      # released by the day's end (simulate_book frees it at rel)
                break
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


def run_choice(envs, size, first_day, n_days, hurdles=D.HURDLES_BPS, delay_s=0, later=None, later_price='median'):
    """The per-asset studies' protocol on a book: one daily value series per hurdle, chosen on the first half."""
    variants, per = {}, {}
    for h in hurdles:
        fills, st = simulate_book(envs, size, h, delay_s=delay_s, later=later, later_price=later_price)
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


def common_window(envs):
    """(first_ts, last_ts, first_day, n_days): the intersection of the envs' windows, cut into days as since 2026-10-10."""
    first_ts = max(e['first_ts'] for e in envs.values())
    last_ts = min(e['last_ts'] for e in envs.values())
    return first_ts, last_ts, first_ts // 86400, int((last_ts - first_ts) // 86400) + 1


def load_default_envs(long_dir):
    envs = {}
    for k, d, _ in DEFAULT_ASSETS:
        d = d or long_dir
        if d is None:
            raise SystemExit('--long is required for %s' % k)
        envs[k] = load_env(k, d)
        print('loaded', k, len(envs[k]['sells']), 'sells', flush=True)
    return envs


def assets_block(envs):
    return {k: {'label': e['label'], 'unit': e['unit'], 'dir': e['dir'], 'sells': len(e['sells']),
                'swaps': e['swaps'], 'staking_apr': e['staking_apr'],
                'wait_median_days': e['wait_summary'].get('median_days')} for k, e in envs.items()}


def alone_block(envs, book_sizes, first_day, n_days, sizes=SIZES):
    """Each asset alone at every size and at its book size, on one window."""
    alone = {}
    for k, book_size in book_sizes:
        alone[k] = {}
        for size in sorted(set(sizes + [book_size])):
            r, _ = run_choice({k: envs[k]}, size, first_day, n_days)
            alone[k][str(size)] = r
        print('alone', k, {s: round(v['out_of_sample_usd_per_year'] or 0) for s, v in alone[k].items()}, flush=True)
    return alone


def separate_block(alone, book_sizes):
    """The separate books at the book's sizes, from `alone`."""
    return {'capital_usd': sum(s for _, s in book_sizes),
            'oos_usd_per_year': sum(alone[k][str(s)]['out_of_sample_usd_per_year'] or 0.0 for k, s in book_sizes),
            'by_asset': {k: alone[k][str(s)]['out_of_sample_usd_per_year'] for k, s in book_sizes}}


def joint_block(envs, sets, first_day, n_days, sizes=SIZES):
    """Each set of assets on one pool, at every size."""
    joint = {}
    for name, keys in sets.items():
        sub = {k: envs[k] for k in keys}
        joint[name] = {}
        for size in sizes:
            r, _ = run_choice(sub, size, first_day, n_days)
            joint[name][str(size)] = r
        print('joint', name, {s: round(v['out_of_sample_usd_per_year'] or 0) for s, v in joint[name].items()}, flush=True)
    return joint


def late_block(envs, sets, joint, first_day, n_days, sizes=LATE_SIZES, later=None, later_price='median'):
    """Late entry: the same books when every episode is joined an hour, or a day, after it became visible."""
    late = {}
    for name, keys in sets.items():
        sub = {k: envs[k] for k in keys}
        for size in sizes:
            base = joint[name][str(size)]['out_of_sample_usd_per_year'] or 0.0
            for lbl, d in (('1h', 3600), ('1d', 86400)):
                r, _ = run_choice(sub, size, first_day, n_days, delay_s=d, later=later, later_price=later_price)
                late['%s|%d|%s' % (name, size, lbl)] = {
                    'out_of_sample_usd_per_year': r['out_of_sample_usd_per_year'], 'chosen_hurdle': r['chosen_hurdle'],
                    'oos_t': r['oos_t'], 'kept_share': (r['out_of_sample_usd_per_year'] or 0.0) / base if base else None}
    return late


def concentration_block(sub, rows, first_day, n_days, sizes=LATE_SIZES, by_asset=False):
    """Is the out-of-sample value one stress or many months? Value by month at each size's chosen hurdle."""
    conc = {}
    for size in sizes:
        r = rows[str(size)]
        h = float(r['chosen_hurdle'].split('=')[1])
        fills, _ = simulate_book(sub, size, h)
        cut = first_day + B.cutoff_index(n_days, 0.5)          # the split choose_then_test used
        bym = collections.defaultdict(float)
        bymk = collections.defaultdict(lambda: collections.defaultdict(float))
        for f in fills:
            if int(f['ts'] // 86400) >= cut:
                bym[D.utc(f['ts'])[:7]] += f['value_usd']
                bymk[f['asset']][D.utc(f['ts'])[:7]] += f['value_usd']
        tot = sum(bym.values())
        top = sorted(bym.values(), reverse=True)
        conc[str(size)] = {'hurdle_bps': h, 'oos_value_by_month_usd': dict(sorted(bym.items())),
                           'top_month_share': top[0] / tot if tot else None,
                           'top_two_months_share': sum(top[:2]) / tot if tot else None}
        if by_asset:
            oos = [f for f in fills if int(f['ts'] // 86400) >= cut]
            usd = sum(f['usd'] for f in oos)
            conc[str(size)]['oos_value_by_month_by_asset_usd'] = {k: dict(sorted(v.items())) for k, v in sorted(bymk.items())}
            conc[str(size)]['oos_filled_usd_by_asset'] = {k: sum(f['usd'] for f in oos if f['asset'] == k) for k in sorted(sub)}
            conc[str(size)]['oos_usd_weighted_wait_days'] = sum(f['usd'] * f['wait_days'] for f in oos) / usd if usd else None
            conc[str(size)]['oos_fills_by_pool'] = {k: dict(collections.Counter(f['pool'] for f in oos if f['asset'] == k).most_common(8))
                                                    for k in sorted(sub)}
            lk = {k: locked_end_of_day([f for f in fills if f['asset'] == k], first_day, n_days) for k in sorted(sub)}
            lk['_pool'] = [sum(lk[k][d] for k in sorted(sub)) for d in range(n_days)]
            c0 = cut - first_day
            conc[str(size)]['locked_end_of_day_by_asset_usd'] = {k: {'max': max(v), 'mean': sum(v) / n_days, 'max_oos': max(v[c0:]),
                                                                     'mean_oos': sum(v[c0:]) / (n_days - c0), 'p90': D.pct(v, 0.9)}
                                                                 for k, v in lk.items()}
    return conc


def demand_series(envs, h, first_day, n_days):
    """Capital each asset would lock, day by day, with unbounded capital at hurdle h."""
    demand = {}
    for k in envs:
        fills, _ = simulate_book({k: envs[k]}, UNBOUNDED, h)
        demand[k] = locked_daily(fills, first_day, n_days)
    return demand


def overlap_block(envs, demand, h, first_day, n_days, eth_keys=SETS['eth3']):
    """How often the dislocations coincide: each asset's peak, the sum's peak and quantiles, pairwise correlations."""
    tot = [sum(demand[k][d] for k in envs) for d in range(n_days)]
    eth_tot = [sum(demand[k][d] for k in eth_keys) for d in range(n_days)]
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
    return {
        'hurdle_bps': h,
        'peak_locked_usd': {k: max(demand[k]) for k in envs},
        'sum_of_peaks_usd': sum(max(demand[k]) for k in envs),
        'peak_of_sum_usd': max(tot), 'peak_of_sum_eth3_usd': max(eth_tot),
        'p90_of_sum_usd': D.pct(tot, 0.9), 'p99_of_sum_usd': D.pct(tot, 0.99),
        'days_with_any_locked': sum(1 for x in tot if x > 0),
        'peak_day_utc': D.utc((first_day + tot.index(max(tot))) * 86400),
        'pairs': pairs,
        'locked_by_month_max_usd': {m: max(tot[d] for d in range(n_days) if D.utc((first_day + d) * 86400)[:7] == m)
                                    for m in sorted({D.utc((first_day + d) * 86400)[:7] for d in range(n_days)})},
    }


def cmd_analyze(args):
    t0 = time.monotonic()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    envs = load_default_envs(Path(args.long) if args.long else None)
    if args.khype:
        return analyze_with_khype(args, envs, out, t0)
    first_ts, last_ts, first_day, n_days = common_window(envs)
    book_sizes = [(k, s) for k, _, s in DEFAULT_ASSETS]
    res = {'generated': D.utc(), 'window': [D.utc(first_ts), D.utc(last_ts)], 'days': n_days,
           'assets': assets_block(envs),
           'parameters': {'fee_legs': D.FEE_LEGS, 'gas_per_fill_usd': D.GAS_PER_FILL_USD, 'min_fill_usd': D.MIN_FILL_USD,
                          'hurdles_bps': D.HURDLES_BPS, 'sizes_usd': SIZES, 'book_sizes_usd': dict(book_sizes),
                          'book_quotes_usd_per_year': BOOK_QUOTE_USD}}

    # 1. Each asset alone, on the common window: the reproduction check against the book's quotes.
    alone = alone_block(envs, book_sizes, first_day, n_days)
    res['alone'] = alone
    res['separate_at_book_sizes'] = separate_block(alone, book_sizes)

    # 2. The shared pool; 2b. late entry; 2c. monthly concentration of the four-asset book.
    joint = joint_block(envs, SETS, first_day, n_days)
    res['joint'] = joint
    late = late_block(envs, SETS, joint, first_day, n_days)
    res['late_entry'] = late
    res['concentration'] = concentration_block({k: envs[k] for k in SETS['all4']}, joint['all4'], first_day, n_days)
    print('late', {k: round(v['kept_share'] or 0, 2) for k, v in late.items()}, flush=True)

    # 3. How often the dislocations coincide: capital each asset would lock with unbounded capital, day by day, at the
    #    hurdle the four-asset book chose at $10M.
    h = float(joint['all4'][str(10_000_000)]['chosen_hurdle'].split('=')[1])
    res['overlap'] = overlap_block(envs, demand_series(envs, h, first_day, n_days), h, first_day, n_days)
    res['seconds'] = time.monotonic() - t0
    D.write_json(out / 'analysis.json', res)
    D.write_json(out / 'manifest.json', {
        'generated': res['generated'], 'inputs': {k: e['dir'] for k, e in envs.items()},
        'note': 'inputs are the priced swaps and queue state of the per-asset studies; nothing fetched. lido and kelp '
                'swaps were regenerated in a scratch copy of research/2026-10-09/redemption_history/raw/long with '
                '`dislocation_history.py analyze --assets lido,kelp` (the original directory predates the swaps files)',
        'window': res['window']})
    print('done', round(res['seconds']), 's')


# ----------------------------------------------------------------------------------------------------------------------
# Five assets: kHYPE joins the pool (--khype)
# ----------------------------------------------------------------------------------------------------------------------
RUN_FIELDS = ('chosen_hurdle', 'in_sample_usd_per_year', 'out_of_sample_usd_per_year', 'oos_t', 'oos_ci95_usd_per_year', 'fills')


def in_sample_flag(rows):
    """`backtest.choose_then_test`'s in_sample_positive, added to stored run_choice rows (the default output keeps its
    keys): the chosen hurdle earned something before the split."""
    for r in rows:
        r['in_sample_positive'] = (r.get('in_sample_usd_per_year') or 0.0) > 0
    return rows


def khype_reproduction(env, kdir):
    """kHYPE alone through `run_choice` against queue_bids_alt's stand-alone grid: same sells, window, split and
    costs, so every size must agree to the cent. The unbounded locked-capital series it saved is checked too."""
    ref = ((D.read_json(Path(kdir) / 'analysis.json') or {}).get('queue_bids') or {}).get('khype') or {}
    grid = ref.get('grid') or {}
    if not grid:
        raise SystemExit('khype: %s/analysis.json has no queue_bids.khype.grid to reproduce' % kdir)
    _, _, first_day, n_days = common_window({'khype': env})
    rows = {}
    for s in sorted(grid, key=int):
        r, _ = run_choice({'khype': env}, int(s), first_day, n_days)
        g = grid[s]
        rows[s] = {'queue_book': {x: r.get(x) for x in RUN_FIELDS}, 'queue_bids_alt': {x: g.get(x) for x in RUN_FIELDS},
                   'diff_oos_usd_per_year': (r['out_of_sample_usd_per_year'] or 0.0) - (g.get('out_of_sample_usd_per_year') or 0.0)}
        rows[s]['identical'] = all(rows[s]['queue_book'][x] == rows[s]['queue_bids_alt'][x] for x in RUN_FIELDS)
        print('khype repro', s, r['chosen_hurdle'], round(r['out_of_sample_usd_per_year'] or 0, 2),
              round(g.get('out_of_sample_usd_per_year') or 0, 2), rows[s]['identical'], flush=True)
    lk = ref.get('locked_capital_daily_unbounded') or {}
    series = None
    if lk.get('series'):
        fills, _ = simulate_book({'khype': env}, UNBOUNDED, lk['hurdle_bps'])
        mine = locked_daily(fills, first_day, n_days)
        theirs = [x['locked_usd'] for x in lk['series']]
        series = {'hurdle_bps': lk['hurdle_bps'], 'days': len(theirs), 'same_length': len(mine) == len(theirs),
                  'max_abs_diff_usd': max(abs(round(a, 2) - b) for a, b in zip(mine, theirs)) if len(mine) == len(theirs) else None}
    return {'source': '%s/analysis.json queue_bids.khype.grid' % kdir, 'window': [D.utc(first_day * 86400), D.utc((first_day + n_days) * 86400 - 1)],
            'days': n_days, 'cutoff_utc': D.utc((first_day + B.cutoff_index(n_days, 0.5)) * 86400),
            'gas_usd': env.get('gas_usd'), 'min_fill_usd': env.get('min_fill_usd'), 'by_size': rows,
            'exact': all(v['identical'] for v in rows.values()) and (series is None or series['max_abs_diff_usd'] == 0),
            'locked_series_check': series}


def regression_all4(envs4, ref_path=ROOT / 'research' / '2026-10-10' / 'queue_book' / 'analysis.json'):
    """all4 on its own (four-asset) window, at every size the 2026-10-10 study stored; the headline is $409,889 at $15M."""
    sub = {k: envs4[k] for k in SETS[REGRESSION['set']]}
    first_ts, last_ts, first_day, n_days = common_window(sub)
    stored = (((D.read_json(ref_path) or {}).get('joint') or {}).get(REGRESSION['set'])) or {}
    rows = {}
    for s in sorted(set(stored) | {str(REGRESSION['size_usd'])}, key=int):
        r, _ = run_choice(sub, int(s), first_day, n_days)
        old = (stored.get(s) or {}).get('out_of_sample_usd_per_year')
        rows[s] = {'chosen_hurdle': r['chosen_hurdle'], 'out_of_sample_usd_per_year': r['out_of_sample_usd_per_year'],
                   'oos_t': r['oos_t'], 'stored_out_of_sample_usd_per_year': old,
                   'identical_to_stored': old is not None and r['out_of_sample_usd_per_year'] == old}
    got = rows[str(REGRESSION['size_usd'])]['out_of_sample_usd_per_year'] or 0.0
    print('regression all4 $15M', round(got), 'expected', REGRESSION['out_of_sample_usd_per_year'], flush=True)
    return {'window': [D.utc(first_ts), D.utc(last_ts)], 'days': n_days, 'size_usd': REGRESSION['size_usd'],
            'out_of_sample_usd_per_year': got, 'expected_usd_per_year': REGRESSION['out_of_sample_usd_per_year'],
            'ok': int(round(got)) == REGRESSION['out_of_sample_usd_per_year'],
            'all_sizes_identical_to_stored': all(v['identical_to_stored'] for v in rows.values()),
            'by_size': rows, 'source': REGRESSION['source']}


def input_hashes(envs):
    """sha256 and size of the main input files of each asset (the coordinator re-derives from these)."""
    out = {}
    for k, e in envs.items():
        d = Path(e['dir'])
        if k == 'khype':
            names = ['analysis.json', 'raw/prices_usd.json.gz', 'raw/blocks_hyperevm.json.gz', 'raw/rates/khype.json.gz',
                     'raw/queue/khype_events.json.gz'] + sorted(('raw/khype_swaps/' + p.name for p in (d / 'raw' / 'khype_swaps').glob('shard_*.json.gz')),
                                                               key=lambda x: int(x.split('_')[-1].split('.')[0]))
        else:
            names = ['swaps_%s.jsonl.gz' % k, 'manifest.json', 'headers.json', 'state.json']
        for n in names:
            p = d / n
            if p.exists():
                out['%s/%s' % (d, n)] = {'bytes': p.stat().st_size, 'sha256': D.sha256(p)}
    return out


SPLIT_KHYPE_USD = [2_000_000, 3_000_000, 5_000_000, 7_500_000, 10_000_000]
ROTATION_DELAYS = (('1h', 3600), ('1d', 86400))


def combined_oos(parts, first_day, n_days):
    """In- and out-of-sample $/yr, HAC t and block-bootstrap interval of several books' summed daily values."""
    v = [0.0] * n_days
    for fills in parts:
        for i, x in enumerate(D.daily_values(fills, first_day, n_days)):
            v[i] += x
    c = B.cutoff_index(n_days, 0.5)
    oos = v[c:]
    boot = B.block_bootstrap(oos, block=7, n=2000)
    return {'in_sample_usd_per_year': sum(v[:c]) * 365.0 / c, 'out_of_sample_usd_per_year': sum(oos) * 365.0 / len(oos),
            'oos_t': B.newey_west_t(oos)[0],
            'oos_ci95_usd_per_year': [boot['lo'] * 365 if boot['lo'] is not None else None, boot['hi'] * 365 if boot['hi'] is not None else None]}


def split_block(envs, joint, first_day, n_days, totals=LATE_SIZES[1:], parts=SPLIT_KHYPE_USD):
    """In practice the pool is two balances: Ethereum (ETH and BTC legs) and HyperEVM (kHYPE). Each fixed split is two
    separate books, each choosing its own hurdle in sample; the split that earned most in sample is marked, so the
    comparison with the fungible all5 pool carries no hindsight."""
    out = {}
    eth4 = {k: envs[k] for k in SETS['all4']}
    for total in totals:
        rows = {}
        for kp in parts:
            if kp >= total:
                continue
            r4, f4 = run_choice(eth4, total - kp, first_day, n_days)
            rk, fk = run_choice({'khype': envs['khype']}, kp, first_day, n_days)
            rows[str(kp)] = dict(combined_oos([f4, fk], first_day, n_days), ethereum_usd=total - kp, khype_usd=kp,
                                 ethereum_part={x: r4[x] for x in RUN_FIELDS}, khype_part={x: rk[x] for x in RUN_FIELDS})
        best = max(rows, key=lambda x: rows[x]['in_sample_usd_per_year']) if rows else None
        fung = joint['all5'][str(total)]
        out[str(total)] = {'fungible_all5': {x: fung[x] for x in RUN_FIELDS}, 'by_khype_allocation': rows,
                           'chosen_in_sample': best,
                           'chosen_out_of_sample_usd_per_year': rows[best]['out_of_sample_usd_per_year'] if best else None,
                           'fungible_over_chosen_split': ((fung['out_of_sample_usd_per_year'] or 0.0) / rows[best]['out_of_sample_usd_per_year'])
                           if best and rows[best]['out_of_sample_usd_per_year'] else None}
        print('split', total, {k: round(v['out_of_sample_usd_per_year']) for k, v in rows.items()}, 'chosen', best, flush=True)
    return out


def rotated_env(env, delay_s):
    """kHYPE when its capital must first cross from Ethereum and later go back: it buys only once the venue median has
    shown the edge `delay_s` earlier, and its capital returns to the pool `delay_s` after the queue pays, with the
    staking carry charged over the extra time (capital in transit earns nothing). A proxy, conservative on both ends
    (capital already on HyperEVM would not wait) except one: Ethereum fills are not delayed when capital sits on HyperEVM."""
    e = {k: v for k, v in env.items() if not isinstance(k, tuple)}          # drop the priced-edge caches
    w0, c0, stake = env['wait'], env['carry'], env.get('carry_stake') or env['carry']
    x = delay_s / 86400.0
    e['wait'] = (lambda ts: w0(ts) + x)
    e['carry'] = (lambda ts: (w0(ts) * c0(ts) + x * stake(ts)) / (w0(ts) + x))
    e['delay_s'] = delay_s
    return e


def rotation_block(envs, joint, first_day, n_days, sizes=LATE_SIZES, delays=ROTATION_DELAYS, late_size=15_000_000):
    """The fungible pool with the HyperEVM leg reached only after the capital moves (`rotated_env`), hurdle re-chosen."""
    out = {}
    for lbl, d in delays:
        sub = {k: envs[k] for k in SETS['all4']}
        sub['khype'] = rotated_env(envs['khype'], d)
        for size in sizes:
            r, _ = run_choice(sub, size, first_day, n_days)
            base = joint['all5'][str(size)]['out_of_sample_usd_per_year'] or 0.0
            a4 = joint['all4'][str(size)]['out_of_sample_usd_per_year'] or 0.0
            row = dict({x: r[x] for x in RUN_FIELDS}, oos_by_asset_usd_per_year=r['oos_by_asset_usd_per_year'],
                       in_sample_positive=(r['in_sample_usd_per_year'] or 0.0) > 0,
                       kept_share_of_fungible=(r['out_of_sample_usd_per_year'] or 0.0) / base if base else None,
                       increment_over_all4=(r['out_of_sample_usd_per_year'] or 0.0) - a4)
            if size == late_size:            # the late-entry test on this variant too (kHYPE: the later of the two delays)
                row['late_entry'] = {}
                for l2, d2 in (('1h', 3600), ('1d', 86400)):
                    rl, _ = run_choice(sub, size, first_day, n_days, delay_s=d2)
                    v = rl['out_of_sample_usd_per_year'] or 0.0
                    row['late_entry'][l2] = {'out_of_sample_usd_per_year': v, 'chosen_hurdle': rl['chosen_hurdle'], 'oos_t': rl['oos_t'],
                                             'kept_share': v / r['out_of_sample_usd_per_year'] if r['out_of_sample_usd_per_year'] else None}
            out['%s|%d' % (lbl, size)] = row
        print('rotation', lbl, {k: round(v['out_of_sample_usd_per_year'] or 0) for k, v in out.items() if k.startswith(lbl)}, flush=True)
    return out


QUEUE_LIVE_IMPL = ROOT / 'research' / 'queue_live' / 'implementation.json'
TAKER_SIZES = [5_000_000, 10_000_000, 15_000_000, 20_000_000]


def trailing_90d(fills, last_day):
    return sum(f['value_usd'] for f in fills if int(f['ts'] // 86400) > last_day - 90) * 365.0 / 90


def taker_block(envs, envs4, alone, first_day, n_days, sizes=TAKER_SIZES):
    """The books priced as an hourly taker (`simulate_book(later='hour')`): each qualifying sale bought back at the next
    hour boundary at that hour's venue median (the rule) or its first trade (the closer reading). First the check against
    queue_live's implementations (f) and (g) on queue_book's own window; then kHYPE alone, all5 (fungible and with the
    kHYPE leg a day behind), all4 on the same window, late entry with the later price, persistence and the fixed split."""
    out = {'rule': '%s; %s' % (LATER['hour'], LATER_PRICES['median']), 'closer_reading': LATER_PRICES['first']}
    a4 = {k: envs4[k] for k in SETS['all4']}
    _, _, fd4, nd4 = common_window(a4)
    ql = ((D.read_json(QUEUE_LIVE_IMPL) or {}).get('sets') or {}).get('all4') or {}
    ver = {}
    for later, tag in (('hour', 'f_taker_next_hour'), ('day', 'g_taker_next_day')):
        for price in ('median', 'first'):
            r, _ = run_choice(a4, 15_000_000, fd4, nd4, later=later, later_price=price)
            q = ql.get('%s|%s' % (tag, price)) or {}
            ver['%s|%s' % (later, price)] = {
                'queue_book': {x: r[x] for x in RUN_FIELDS},
                'queue_live': {'out_of_sample_usd_per_year': q.get('out_of_sample_usd_per_year'), 'chosen_hurdle': q.get('chosen'), 'oos_t': q.get('oos_t')},
                'identical': q.get('out_of_sample_usd_per_year') == r['out_of_sample_usd_per_year'] and q.get('chosen') == r['chosen_hurdle']}
            print('taker check', later, price, round(r['out_of_sample_usd_per_year'] or 0, 2), q.get('out_of_sample_usd_per_year'), flush=True)
    q0 = ql.get('a0_taker_no_delay') or {}
    ver['no_delay'] = {'queue_book': REGRESSION['out_of_sample_usd_per_year'], 'queue_live': q0.get('out_of_sample_usd_per_year'),
                       'note': 'the own-print baselines differ by about $4: queue_live resolves requests pending at the study\'s end with '
                               'later queue events (waits of 63 stETH, 10 weETH and 10 rsETH sales in the last days); with its waits '
                               'swapped into these envs the own-print value is queue_live\'s, and every later-priced value is identical'}
    out['all4_original_window_vs_queue_live'] = ver
    last_day = first_day + n_days - 1
    kh = {}
    for price in ('median', 'first'):
        for size in (10_000_000, 30_000_000):
            r, fills = run_choice({'khype': envs['khype']}, size, first_day, n_days, later='hour', later_price=price)
            kh['%s|%d' % (price, size)] = dict({x: r[x] for x in RUN_FIELDS}, in_sample_positive=(r['in_sample_usd_per_year'] or 0.0) > 0,
                                               trailing_90d_usd_per_year=trailing_90d(fills, last_day), oos_rank_of_chosen=r['oos_rank_of_chosen'],
                                               own_print_out_of_sample_usd_per_year=alone['khype'][str(size)]['out_of_sample_usd_per_year'])
    for size in (10_000_000,):
        base = kh['median|%d' % size]['out_of_sample_usd_per_year'] or 0.0
        for lbl, d in (('1h', 3600), ('1d', 86400)):
            r, _ = run_choice({'khype': envs['khype']}, size, first_day, n_days, delay_s=d, later='hour', later_price='median')
            kh['median|%d' % size]['late_%s' % lbl] = {'out_of_sample_usd_per_year': r['out_of_sample_usd_per_year'], 'chosen_hurdle': r['chosen_hurdle'],
                                                       'kept_share': (r['out_of_sample_usd_per_year'] or 0.0) / base if base else None}
    out['khype_alone'] = kh
    print('taker khype', {k: round(v['out_of_sample_usd_per_year'] or 0) for k, v in kh.items()}, flush=True)
    crossing = {k: envs[k] for k in SETS['all4']}
    crossing['khype'] = rotated_env(envs['khype'], 86400)
    books = {'all5': {k: envs[k] for k in SETS_KHYPE['all5']}, 'all5_1d_crossing': crossing, 'all4': {k: envs[k] for k in SETS['all4']}}
    jt = {}
    for name, sub in books.items():
        for price in ('median', 'first'):
            for size in sizes:
                r, fills = run_choice(sub, size, first_day, n_days, later='hour', later_price=price)
                jt['%s|%s|%d' % (name, price, size)] = dict({x: r[x] for x in RUN_FIELDS}, oos_by_asset_usd_per_year=r['oos_by_asset_usd_per_year'],
                                                           in_sample_positive=(r['in_sample_usd_per_year'] or 0.0) > 0,
                                                           oos_rank_of_chosen=r['oos_rank_of_chosen'],
                                                           trailing_90d_usd_per_year=trailing_90d(fills, last_day))
            print('taker', name, price, {s_: round(jt['%s|%s|%d' % (name, price, s_)]['out_of_sample_usd_per_year'] or 0) for s_ in sizes}, flush=True)
    out['books'] = jt
    late = {}
    for name, szs in (('all5', LATE_SIZES), ('all5_1d_crossing', (15_000_000,))):
        for size in szs:
            base = jt['%s|median|%d' % (name, size)]['out_of_sample_usd_per_year'] or 0.0
            for lbl, d in (('1h', 3600), ('1d', 86400)):
                r, _ = run_choice(books[name], size, first_day, n_days, delay_s=d, later='hour', later_price='median')
                late['%s|%d|%s' % (name, size, lbl)] = {'out_of_sample_usd_per_year': r['out_of_sample_usd_per_year'], 'chosen_hurdle': r['chosen_hurdle'],
                                                        'oos_t': r['oos_t'], 'kept_share': (r['out_of_sample_usd_per_year'] or 0.0) / base if base else None}
    out['late_entry'] = late
    print('taker late', {k: round(v['kept_share'] or 0, 2) for k, v in late.items()}, flush=True)
    out['persistence'] = {str(h): {k: persistence(envs[k], hurdle_bps=h, delays=('hour',)) for k in SETS_KHYPE['all5']} for h in (1.0, 10.0)}
    eth4 = {k: envs[k] for k in SETS['all4']}
    rows = {}
    for kp in SPLIT_KHYPE_USD:
        r4, f4 = run_choice(eth4, 15_000_000 - kp, first_day, n_days, later='hour', later_price='median')
        rk, fk = run_choice({'khype': envs['khype']}, kp, first_day, n_days, later='hour', later_price='median')
        rows[str(kp)] = dict(combined_oos([f4, fk], first_day, n_days), ethereum_usd=15_000_000 - kp, khype_usd=kp,
                             ethereum_part={x: r4[x] for x in RUN_FIELDS}, khype_part={x: rk[x] for x in RUN_FIELDS})
    best = max(rows, key=lambda x: rows[x]['in_sample_usd_per_year'])
    out['split_15m'] = {'by_khype_allocation': rows, 'chosen_in_sample': best,
                        'chosen_out_of_sample_usd_per_year': rows[best]['out_of_sample_usd_per_year']}
    return out


def analyze_with_khype(args, envs4, out, t0):
    """The five-asset book: kHYPE's reproduction and the all4 regression first, then the protocol on the common window."""
    kdir = Path(args.khype)
    envs = dict(envs4)
    envs['khype'] = load_khype_env(kdir)
    print('loaded khype', len(envs['khype']['sells']), 'sells', flush=True)
    book_sizes = [(k, s) for k, _, s in DEFAULT_ASSETS] + [('khype', KHYPE_BOOK_SIZE)]

    # 0. The checks: kHYPE alone must reproduce queue_bids_alt; all4 on its own window must reproduce 2026-10-10.
    repro = khype_reproduction(envs['khype'], kdir)
    reg = regression_all4(envs4)

    first_ts, last_ts, first_day, n_days = common_window(envs)
    w4 = common_window(envs4)
    gas = {k: e.get('gas_usd', D.GAS_PER_FILL_USD) for k, e in envs.items()}
    minf = {k: e.get('min_fill_usd', D.MIN_FILL_USD) for k, e in envs.items()}
    assets = assets_block(envs)
    for k in assets:
        assets[k].update({'gas_per_fill_usd': gas[k], 'min_fill_usd': minf[k], 'first_utc': D.utc(envs[k]['first_ts']),
                          'last_utc': D.utc(envs[k]['last_ts']),
                          'sells_in_window': sum(1 for s in envs[k]['sells'] if first_day <= s['ts'] // 86400 < first_day + n_days)})
    res = {'generated': D.utc(), 'window': [D.utc(first_ts), D.utc(last_ts)], 'days': n_days,
           'cutoff_utc': D.utc((first_day + B.cutoff_index(n_days, 0.5)) * 86400),
           'window_all4_original': [D.utc(w4[0]), D.utc(w4[1])], 'days_all4_original': w4[3],
           'assets': assets,
           'parameters': {'fee_legs': D.FEE_LEGS, 'gas_per_fill_usd': gas, 'min_fill_usd': minf, 'hurdles_bps': D.HURDLES_BPS,
                          'sizes_usd': SIZES, 'late_sizes_usd': list(LATE_SIZES), 'book_sizes_usd': dict(book_sizes),
                          'book_quotes_usd_per_year': dict(BOOK_QUOTE_USD, khype=round(repro['by_size'][str(KHYPE_BOOK_SIZE)]['queue_bids_alt']['out_of_sample_usd_per_year'])),
                          'sets': SETS_KHYPE,
                          'warm_start': 'sells before the common window are simulated too (as in the 2026-10-10 run): '
                                        'capital they lock at the window start is unavailable, their value is not counted'},
           'khype_reproduction': repro, 'regression_all4_original_window': reg}

    # 1. Each asset alone on the common window.
    alone = alone_block(envs, book_sizes, first_day, n_days)
    for k in alone:
        in_sample_flag(alone[k].values())
    res['alone'] = alone
    res['separate_at_book_sizes'] = separate_block(alone, book_sizes)
    res['separate_at_book_sizes_all4'] = separate_block(alone, book_sizes[:4])

    # 2. One pool: all5 and eth3_khype, and all4 / eth3 on the same shortened window.
    joint = joint_block(envs, SETS_KHYPE, first_day, n_days)
    for name in joint:
        in_sample_flag(joint[name].values())
    res['joint'] = joint
    inc = {}
    for s in map(str, SIZES):
        a5, a4 = joint['all5'][s]['out_of_sample_usd_per_year'] or 0.0, joint['all4'][s]['out_of_sample_usd_per_year'] or 0.0
        e4, e3 = joint['eth3_khype'][s]['out_of_sample_usd_per_year'] or 0.0, joint['eth3'][s]['out_of_sample_usd_per_year'] or 0.0
        kh = alone['khype'][s]['out_of_sample_usd_per_year'] or 0.0
        inc[s] = {'all4': a4, 'all5': a5, 'all5_minus_all4': a5 - a4, 'eth3': e3, 'eth3_khype': e4, 'eth3_khype_minus_eth3': e4 - e3,
                  'khype_alone': kh, 'all5_khype_share': (joint['all5'][s]['oos_by_asset_usd_per_year'].get('khype', 0.0) / a5) if a5 else None,
                  'increment_over_khype_alone': ((a5 - a4) / kh) if kh else None}
    res['increment'] = inc
    late = late_block(envs, SETS_KHYPE, joint, first_day, n_days)
    late.update(late_block(envs, {'khype': ['khype']}, {'khype': alone['khype']}, first_day, n_days))   # kHYPE alone
    res['late_entry'] = late
    print('late', {k: round(v['kept_share'] or 0, 2) for k, v in late.items()}, flush=True)
    res['concentration'] = {name: concentration_block({k: envs[k] for k in SETS_KHYPE[name]}, joint[name], first_day, n_days,
                                                      by_asset=True) for name in ('all5', 'eth3_khype', 'all4')}
    res['split'] = split_block(envs, joint, first_day, n_days)
    res['rotation'] = rotation_block(envs, joint, first_day, n_days)
    res['hourly_taker'] = taker_block(envs, envs4, alone, first_day, n_days)

    # 3. Overlap of locked capital at the hurdle the five-asset book chose at $10M.
    h = float(joint['all5'][str(10_000_000)]['chosen_hurdle'].split('=')[1])
    demand = demand_series(envs, h, first_day, n_days)
    ov = overlap_block(envs, demand, h, first_day, n_days)
    all4_tot = [sum(demand[k][d] for k in SETS['all4']) for d in range(n_days)]
    eth_tot = [sum(demand[k][d] for k in SETS['eth3']) for d in range(n_days)]
    ov['peak_of_sum_all4_usd'] = max(all4_tot)
    ov['khype_against_sums'] = {'corr_with_eth3_sum': corr(demand['khype'], eth_tot), 'corr_with_all4_sum': corr(demand['khype'], all4_tot)}
    # kHYPE at the hurdle it chose alone at its book size, the others at h: the coordinator's 2026-10-10 check, recomputed
    hk = float(alone['khype'][str(KHYPE_BOOK_SIZE)]['chosen_hurdle'].split('=')[1])
    if hk != h:
        dk = demand_series({'khype': envs['khype']}, hk, first_day, n_days)['khype']
        ov['khype_at_own_hurdle'] = {'khype_hurdle_bps': hk, 'others_hurdle_bps': h,
                                     'corr': {k: corr(dk, demand[k]) for k in SETS['all4']},
                                     'corr_with_eth3_sum': corr(dk, eth_tot), 'corr_with_all4_sum': corr(dk, all4_tot),
                                     'peak_locked_usd': max(dk)}
    res['overlap'] = ov
    res['seconds'] = time.monotonic() - t0
    D.write_json(out / 'analysis.json', res)
    D.write_json(out / 'manifest.json', {
        'generated': res['generated'], 'inputs': {k: e['dir'] for k, e in envs.items()}, 'files': input_hashes(envs),
        'command': 'uv run --with pycryptodome python scripts/queue_book.py analyze --long %s --khype %s --out %s' % (
            args.long, args.khype, args.out),
        'note': 'nothing fetched. lido and kelp: the swaps regenerated on 2026-10-10 (research/2026-10-10/queue_book/manifest.json) '
                'in a scratch copy of research/2026-10-09/redemption_history/raw/long, copied unchanged to this run\'s --long; '
                'etherfi_ev and lbtc_cb: research/2026-10-10/queue_bids_ext/raw; khype: research/2026-10-10/queue_bids_alt '
                '(queue_bids_alt.khype_book_env). The regression and reproduction checks are in analysis.json.',
        'window': res['window'], 'checks': {'khype_reproduction_exact': repro['exact'], 'regression_all4_ok': reg['ok'],
                                            'regression_all4_all_sizes_identical': reg['all_sizes_identical_to_stored']}})
    print('done', round(res['seconds']), 's')


def fmt(v):
    return '—' if v is None else '$%s' % format(int(round(v)), ',')


def ft(v):
    return '—' if v is None else '%.2f' % v


def fpct(v):
    return '—' if v is None else '%.0f%%' % (100 * v)


def render_taker(a):
    """tables.md lines for the hourly taker (the executable pricing)."""
    t = a['hourly_taker']
    L = ['', '## The hourly taker: what an executable bidder earns', '',
         'Everything above buys each sale at its own print, capped at its own hour\'s venue median: only a bidder right behind '
         'each seller gets that. Here a sale that qualifies on that own-hour edge is bought at the next hour boundary H at the '
         'venue median of the trades inside [H, H+1h) (the rule; the first trade after H is the closer reading), and skipped '
         'when nothing traded there or the edge no longer clears the hurdle (`simulate_book(later=\'hour\')`). Hurdle re-chosen '
         'in sample.', '', '### Check against queue_live\'s implementations (f) and (g): all4 at $15M on queue_book\'s window', '',
         '| version | queue_live | queue_book | hurdle | t | identical |', '|---|---:|---:|---|---:|---|']
    for k, v in t['all4_original_window_vs_queue_live'].items():
        if k == 'no_delay':
            continue
        q, b = v['queue_live'], v['queue_book']
        L.append('| %s | %s | %s | %s | %s | %s |' % (k.replace('hour', 'next hour').replace('day', 'a day later'), fmt(q['out_of_sample_usd_per_year']),
                                                    fmt(b['out_of_sample_usd_per_year']), b['chosen_hurdle'], ft(b['oos_t']), 'yes' if v['identical'] else 'NO'))
    nd = t['all4_original_window_vs_queue_live']['no_delay']
    L += ['', 'Own-print baseline: queue_book %s, queue_live %s; %s.' % (fmt(nd['queue_book']), fmt(nd['queue_live']), nd['note']), '',
          '### kHYPE alone (452 days, split 2026-02-26)', '', '| size | own print | next hour, median | t | 95% interval | next hour, first trade | t |',
          '|---:|---:|---:|---:|---|---:|---:|']
    for size in (10_000_000, 30_000_000):
        m, f = t['khype_alone']['median|%d' % size], t['khype_alone']['first|%d' % size]
        L.append('| %s | %s | %s (%s) | %s | %s – %s | %s (%s) | %s |' % (fmt(size), fmt(m['own_print_out_of_sample_usd_per_year']), fmt(m['out_of_sample_usd_per_year']),
                                                                    m['chosen_hurdle'], ft(m['oos_t']), fmt(m['oos_ci95_usd_per_year'][0]), fmt(m['oos_ci95_usd_per_year'][1]),
                                                                    fmt(f['out_of_sample_usd_per_year']), f['chosen_hurdle'], ft(f['oos_t'])))
    m = t['khype_alone']['median|10000000']
    L += ['', 'kHYPE at $10M, later price, late entry: an hour late %s (%s), a day late %s (%s).' % (
        fmt(m['late_1h']['out_of_sample_usd_per_year']), fpct(m['late_1h']['kept_share']), fmt(m['late_1d']['out_of_sample_usd_per_year']),
        fpct(m['late_1d']['kept_share'])), '', '### The books as hourly takers (common window)', '',
          '| book | pool | own print | next hour, median | t | 95% interval | by asset (median) | next hour, first trade |', '|---|---:|---:|---:|---:|---|---|---:|']
    own = {'all5': a['joint']['all5'], 'all4': a['joint']['all4']}
    for name in ('all5', 'all5_1d_crossing', 'all4'):
        for size in sorted({int(k.split('|')[2]) for k in t['books'] if k.startswith(name + '|')}):
            r, f = t['books']['%s|median|%d' % (name, size)], t['books']['%s|first|%d' % (name, size)]
            op = (own.get(name) or {}).get(str(size), {}).get('out_of_sample_usd_per_year') if name in own else \
                (a.get('rotation') or {}).get('1d|%d' % size, {}).get('out_of_sample_usd_per_year')
            ci = r['oos_ci95_usd_per_year']
            L.append('| %s | $%gM | %s | %s (%s) | %s | %s – %s | %s | %s (%s) |' % (
                name, size / 1e6, fmt(op), fmt(r['out_of_sample_usd_per_year']), r['chosen_hurdle'], ft(r['oos_t']), fmt(ci[0]), fmt(ci[1]),
                ', '.join('%s %s' % (k, fmt(v)) for k, v in r['oos_by_asset_usd_per_year'].items()), fmt(f['out_of_sample_usd_per_year']), f['chosen_hurdle']))
    L += ['', '| pool | all5 − all4 (median) | kHYPE leg a day behind − all4 | all5 − all4 (first trade) |', '|---:|---:|---:|---:|']
    for size in sorted({int(k.split('|')[2]) for k in t['books'] if k.startswith('all5|')}):
        g = lambda n, pr: t['books']['%s|%s|%d' % (n, pr, size)]['out_of_sample_usd_per_year'] or 0.0  # noqa: E731
        L.append('| $%gM | %s | %s | %s |' % (size / 1e6, fmt(g('all5', 'median') - g('all4', 'median')),
                                             fmt(g('all5_1d_crossing', 'median') - g('all4', 'median')), fmt(g('all5', 'first') - g('all4', 'first'))))
    L += ['', '### Late entry with the later price (hurdle re-chosen)', '', '| book | pool | on time | an hour late | kept | a day late | kept |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for key in sorted({k.rsplit('|', 1)[0] for k in t['late_entry']}):
        name, size = key.split('|')
        h1, d1 = t['late_entry'][key + '|1h'], t['late_entry'][key + '|1d']
        L.append('| %s | $%gM | %s | %s | %s | %s | %s |' % (name, int(size) / 1e6, fmt(t['books']['%s|median|%s' % (name, size)]['out_of_sample_usd_per_year']),
                                                         fmt(h1['out_of_sample_usd_per_year']), fpct(h1['kept_share']), fmt(d1['out_of_sample_usd_per_year']), fpct(d1['kept_share'])))
    L += ['', '### Does the discount persist into the next hour? (sales qualifying on their own-hour edge, full window)', '',
          '| asset | hurdle | qualifying sales | still clear at the next hour\'s median | by volume | no trade next hour | of those traded | at the first trade |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for h, per in t['persistence'].items():
        for k, v in per.items():
            m, f = v['hour|median']['all'], v['hour|first']['all']
            L.append('| %s | %gbp | %s | %s | %s | %s | %s | %s |' % (k, float(h), format(m['qualifying'], ','), fpct(m['still_clear_share']), fpct(m['still_clear_usd_share']),
                                                                fpct(m['later_missing_share']), fpct(m['still_clear_share_of_those_traded']), fpct(f['still_clear_share'])))
    sp = t['split_15m']
    L += ['', 'Fixed split at $15M as hourly takers (each part its own hurdle; the split best in sample): %s on HyperEVM, %s a year (%s).' % (
        fmt(int(sp['chosen_in_sample'])), fmt(sp['chosen_out_of_sample_usd_per_year']),
        ', '.join('%s → %s' % (fmt(int(k)), fmt(v['out_of_sample_usd_per_year'])) for k, v in sorted(sp['by_khype_allocation'].items(), key=lambda kv: int(kv[0]))))]
    return L


def render_khype(a, out):
    """tables.md for the five-asset run (`analyze --khype`)."""
    rp, rg = a['khype_reproduction'], a['regression_all4_original_window']
    L = ['# Queue bids on one capital pool, with kHYPE — tables', '',
         'Common window of the five assets %s → %s (%d days), split %s: the hurdle is chosen on the first half and tested '
         'once on the second. all4 and eth3 are rerun on the same window, so every kHYPE row compares like for like. '
         'kHYPE fills pay HyperEVM costs ($%g a fill, $%s minimum); the Ethereum-side assets $%g and $%s.' % (
             a['window'][0], a['window'][1], a['days'], a['cutoff_utc'][:10], a['parameters']['gas_per_fill_usd']['khype'],
             format(int(a['parameters']['min_fill_usd']['khype']), ','), a['parameters']['gas_per_fill_usd']['lido'],
             format(int(a['parameters']['min_fill_usd']['lido']), ',')), '']
    L += ['## Checks', '', '### kHYPE alone through this protocol vs queue_bids_alt (%s → %s, %d days, split %s)' % (
        rp['window'][0][:10], rp['window'][1][:10], rp['days'], rp['cutoff_utc'][:10]), '',
          '| size | queue_bids_alt | queue_book | difference | hurdle | t | identical |', '|---:|---:|---:|---:|---|---:|---|']
    for s, v in sorted(rp['by_size'].items(), key=lambda kv: int(kv[0])):
        q, r = v['queue_bids_alt'], v['queue_book']
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (fmt(int(s)), fmt(q['out_of_sample_usd_per_year']), fmt(r['out_of_sample_usd_per_year']),
                                                         '$%.2f' % v['diff_oos_usd_per_year'], r['chosen_hurdle'], ft(r['oos_t']),
                                                         'yes' if v['identical'] else 'NO'))
    ls = rp.get('locked_series_check') or {}
    if ls:
        L += ['', 'The saved unbounded locked-capital series (%gbp, %d days) is reproduced to %s a day at most.' % (
            ls['hurdle_bps'], ls['days'], '$%.2f' % ls['max_abs_diff_usd'] if ls.get('max_abs_diff_usd') is not None else '—')]
    L += ['', '### all4 on its own window (%s → %s, %d days) against the stored 2026-10-10 run' % (rg['window'][0][:10], rg['window'][1][:10], rg['days']), '',
          '| size | stored | rerun | hurdle | t | identical |', '|---:|---:|---:|---|---:|---|']
    for s, v in sorted(rg['by_size'].items(), key=lambda kv: int(kv[0])):
        L.append('| %s | %s | %s | %s | %s | %s |' % (fmt(int(s)), fmt(v['stored_out_of_sample_usd_per_year']), fmt(v['out_of_sample_usd_per_year']),
                                                    v['chosen_hurdle'], ft(v['oos_t']), 'yes' if v['identical_to_stored'] else 'NO'))
    L += ['', 'Regression: all4 at $15M = %s (expected %s): %s.' % (fmt(rg['out_of_sample_usd_per_year']), fmt(rg['expected_usd_per_year']),
                                                                  'pass' if rg['ok'] else 'FAIL'), '']
    sizes = sorted(a['alone']['khype'], key=int)
    L += ['## Each asset alone on the common window (out of sample, $ a year)', '',
          '| asset | ' + ' | '.join('$%gM' % (int(s) / 1e6) for s in sizes) + ' |', '|---|' + '---:|' * len(sizes)]
    for k, v in a['alone'].items():
        L.append('| %s | %s |' % (k, ' | '.join(fmt((v.get(s) or {}).get('out_of_sample_usd_per_year')) for s in sizes)))
    sep, sep4 = a['separate_at_book_sizes'], a['separate_at_book_sizes_all4']
    L += ['', 'Separate books at the book sizes on this window: five %s of capital, %s a year; the four Ethereum-side %s, %s.' % (
        fmt(sep['capital_usd']), fmt(sep['oos_usd_per_year']), fmt(sep4['capital_usd']), fmt(sep4['oos_usd_per_year'])), '']
    L += ['## One pool (common window)', '', '| set | pool | chosen | in sample | out of sample | t | 95% interval | by asset |',
          '|---|---:|---|---:|---:|---:|---|---|']
    for name in ('all5', 'all4', 'eth3_khype', 'eth3'):
        for s in sorted(a['joint'][name], key=int):
            r = a['joint'][name][s]
            ci = r['oos_ci95_usd_per_year']
            L.append('| %s | $%gM | %s | %s | %s | %s | %s – %s | %s |' % (
                name, int(s) / 1e6, r['chosen_hurdle'], fmt(r['in_sample_usd_per_year']), fmt(r['out_of_sample_usd_per_year']),
                ft(r['oos_t']), fmt(ci[0]), fmt(ci[1]), ', '.join('%s %s' % (k, fmt(v)) for k, v in r['oos_by_asset_usd_per_year'].items())))
    L += ['', '## What kHYPE adds (out of sample, $ a year, same window)', '',
          '| pool | all4 | all5 | all5 − all4 | kHYPE alone | increment / kHYPE alone | kHYPE share of all5 | eth3 | eth3+kHYPE | difference |',
          '|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for s, v in sorted(a['increment'].items(), key=lambda kv: int(kv[0])):
        L.append('| $%gM | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            int(s) / 1e6, fmt(v['all4']), fmt(v['all5']), fmt(v['all5_minus_all4']), fmt(v['khype_alone']),
            fpct(v['increment_over_khype_alone']), fpct(v['all5_khype_share']), fmt(v['eth3']), fmt(v['eth3_khype']),
            fmt(v['eth3_khype_minus_eth3'])))
    L += ['', '## Late entry (hurdle re-chosen in sample on the delayed book)', '',
          '| set | pool | on time | 1 hour late | kept | 1 day late | kept |', '|---|---:|---:|---:|---:|---:|---:|']
    for name in ('all5', 'all4', 'eth3_khype', 'eth3'):
        for size in a['parameters']['late_sizes_usd']:
            h1, d1 = a['late_entry']['%s|%d|1h' % (name, size)], a['late_entry']['%s|%d|1d' % (name, size)]
            L.append('| %s | $%gM | %s | %s | %s | %s | %s |' % (name, size / 1e6, fmt(a['joint'][name][str(size)]['out_of_sample_usd_per_year']),
                                                             fmt(h1['out_of_sample_usd_per_year']), fpct(h1['kept_share']),
                                                             fmt(d1['out_of_sample_usd_per_year']), fpct(d1['kept_share'])))
    L += ['', '## Monthly concentration of the out-of-sample value', '',
          '| set | pool | hurdle | best month | best two | months with value |', '|---|---:|---:|---:|---:|---:|']
    for name, rows in a['concentration'].items():
        for s, c in sorted(rows.items(), key=lambda kv: int(kv[0])):
            L.append('| %s | $%gM | %gbp | %s | %s | %d |' % (name, int(s) / 1e6, c['hurdle_bps'], fpct(c['top_month_share']),
                                                          fpct(c['top_two_months_share']), sum(1 for x in c['oos_value_by_month_usd'].values() if x > 0)))
    c5 = a['concentration']['all5'].get('15000000')
    if c5:
        ms = list(c5['oos_value_by_month_usd'])
        ks = list(c5['oos_value_by_month_by_asset_usd'])
        L += ['', 'all5 at $15M (%gbp), out-of-sample value by month and asset:' % c5['hurdle_bps'], '',
              '| month | total | ' + ' | '.join(ks) + ' |', '|---|---:|' + '---:|' * len(ks)]
        for m in ms:
            L.append('| %s | %s | %s |' % (m, fmt(c5['oos_value_by_month_usd'][m]),
                                          ' | '.join(fmt(c5['oos_value_by_month_by_asset_usd'][k].get(m, 0.0)) for k in ks)))
        lk = c5.get('locked_end_of_day_by_asset_usd') or {}
        if lk:
            L += ['', 'Capital each asset holds inside the all5 $15M pool at the end of each day (from its fills and waits):', '',
                  '| asset | peak | mean | peak out of sample | mean out of sample | 90th percentile |', '|---|---:|---:|---:|---:|---:|']
            for k, v in lk.items():
                L.append('| %s | %s | %s | %s | %s | %s |' % ('whole pool' if k == '_pool' else k, fmt(v['max']), fmt(v['mean']),
                                                            fmt(v['max_oos']), fmt(v['mean_oos']), fmt(v['p90'])))
    sp = a.get('split') or {}
    if sp:
        L += ['', '## Two balances instead of one: an Ethereum pool plus a fixed HyperEVM kHYPE sub-pool', '',
              'Each part is its own book and chooses its own hurdle in sample; the split marked was the best in sample.', '',
              '| total | kHYPE sub-pool | Ethereum pool | in sample | out of sample | t | 95% interval | Ethereum hurdle | kHYPE hurdle |',
              '|---:|---:|---:|---:|---:|---:|---|---|---|']
        for tot, v in sorted(sp.items(), key=lambda kv: int(kv[0])):
            for kp, r in sorted(v['by_khype_allocation'].items(), key=lambda kv: int(kv[0])):
                ci = r['oos_ci95_usd_per_year']
                L.append('| %s | %s%s | %s | %s | %s | %s | %s – %s | %s | %s |' % (
                    fmt(int(tot)), fmt(r['khype_usd']), ' (chosen)' if kp == v['chosen_in_sample'] else '', fmt(r['ethereum_usd']),
                    fmt(r['in_sample_usd_per_year']), fmt(r['out_of_sample_usd_per_year']), ft(r['oos_t']), fmt(ci[0]), fmt(ci[1]),
                    r['ethereum_part']['chosen_hurdle'], r['khype_part']['chosen_hurdle']))
            f = v['fungible_all5']
            ci = f['oos_ci95_usd_per_year']
            L.append('| %s | one fungible pool (all5) | | %s | %s | %s | %s – %s | %s | %s |' % (
                fmt(int(tot)), fmt(f['in_sample_usd_per_year']), fmt(f['out_of_sample_usd_per_year']), ft(f['oos_t']), fmt(ci[0]), fmt(ci[1]),
                f['chosen_hurdle'], f['chosen_hurdle']))
    ro = a.get('rotation') or {}
    if ro:
        L += ['', '## One pool whose HyperEVM leg is reached only after the capital moves', '',
              'kHYPE buys only once the venue median showed the edge the crossing time earlier, and its capital returns to the '
              'pool that long after the queue pays (carry charged over the crossing); Ethereum fills are on time. Hurdle re-chosen in sample.', '',
              '| crossing | pool | chosen | in sample | out of sample | t | 95% interval | kept of fungible | over all4 | kHYPE in it |',
              '|---|---:|---|---:|---:|---:|---|---:|---:|---:|']
        for key, r in ro.items():
            lbl, size = key.split('|')
            ci = r['oos_ci95_usd_per_year']
            L.append('| %s | $%gM | %s | %s | %s | %s | %s – %s | %s | %s | %s |' % (
                lbl, int(size) / 1e6, r['chosen_hurdle'], fmt(r['in_sample_usd_per_year']), fmt(r['out_of_sample_usd_per_year']),
                ft(r['oos_t']), fmt(ci[0]), fmt(ci[1]), fpct(r['kept_share_of_fungible']), fmt(r['increment_over_all4']),
                fmt(r['oos_by_asset_usd_per_year'].get('khype'))))
        for key, r in ro.items():
            if r.get('late_entry'):
                L.append('')
                L.append('Late entry on the %s-crossing pool at %s (hurdle re-chosen): an hour late %s (%s), a day late %s (%s).' % (
                    key.split('|')[0], fmt(int(key.split('|')[1])), fmt(r['late_entry']['1h']['out_of_sample_usd_per_year']),
                    fpct(r['late_entry']['1h']['kept_share']), fmt(r['late_entry']['1d']['out_of_sample_usd_per_year']),
                    fpct(r['late_entry']['1d']['kept_share'])))
    o = a['overlap']
    L += ['', '## How often the dislocations coincide (unbounded capital, hurdle %g bp, the all5 choice at $10M)' % o['hurdle_bps'], '',
          '- Peak capital each asset would lock: ' + ', '.join('%s %s' % (k, fmt(v)) for k, v in o['peak_locked_usd'].items()),
          '- Sum of the peaks %s; peak of the sum %s (all4: %s; ETH three: %s); 99th percentile of the sum %s; 90th %s.' % (
              fmt(o['sum_of_peaks_usd']), fmt(o['peak_of_sum_usd']), fmt(o['peak_of_sum_all4_usd']), fmt(o['peak_of_sum_eth3_usd']),
              fmt(o['p99_of_sum_usd']), fmt(o['p90_of_sum_usd'])),
          '- Busiest day %s; days with any capital locked: %d of %d.' % (o['peak_day_utc'][:10], o['days_with_any_locked'], a['days']),
          '- kHYPE against the sums: %s with the three ETH bids, %s with all four.' % (
              ft(o['khype_against_sums']['corr_with_eth3_sum']), ft(o['khype_against_sums']['corr_with_all4_sum'])), '',
          '| pair | correlation of daily locked capital | days both locked | days either | overlap |', '|---|---:|---:|---:|---:|']
    for p, v in o['pairs'].items():
        L.append('| %s | %s | %d | %d | %s |' % (p, ft(v['corr_daily_locked']), v['days_both_locked'], v['days_either_locked'], fpct(v['jaccard'])))
    ko = o.get('khype_at_own_hurdle')
    if ko:
        L += ['', 'kHYPE at its own stand-alone hurdle (%gbp), the others at %gbp: %s; with the ETH three summed %s, with all four %s.' % (
            ko['khype_hurdle_bps'], ko['others_hurdle_bps'], ', '.join('%s %s' % (k, ft(v)) for k, v in ko['corr'].items()),
            ft(ko['corr_with_eth3_sum']), ft(ko['corr_with_all4_sum']))]
    if a.get('hourly_taker'):
        L += render_taker(a)
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


BOOK5_SIZE = 15_000_000          # the one-pool row's size since 2026-10-10
BOOK5_QUOTE = 'all5_1d_crossing' # the hourly taker with the HyperEVM leg a day behind (capital crossing)
BOOK5_GO = {'min_oos_t': 2.0, 'min_late_1d_kept': 0.5}   # with in_sample_positive: the coordinator's go rule
NAMES = {'lido': 'stETH', 'etherfi_ev': 'weETH', 'kelp': 'rsETH', 'lbtc_cb': 'LBTC', 'khype': 'kHYPE'}


def go_rule(r, late1d):
    return bool(r.get('in_sample_positive')) and (r.get('oos_t') or 0) > BOOK5_GO['min_oos_t'] and \
        (late1d.get('kept_share') or 0) > BOOK5_GO['min_late_1d_kept']


def book_entries_khype(a, out_dir, size=BOOK5_SIZE, quote=BOOK5_QUOTE):
    """A DRAFT of the one-pool row with kHYPE inside, for the coordinator (not written to the book).

    Priced as an hourly taker (`simulate_book(later='hour')`, the venue median of the hour after each sale: the
    executable reading), with the HyperEVM leg reached a day after capital starts to move (`rotated_env`). The fungible
    taker, the first-trade reading, the own-print values and the fixed split are in the note. go needs the quoted
    variant's chosen hurdle positive in sample, its out-of-sample t above 2 and its day-late book (later price) keeping
    more than half."""
    rel = str(Path(out_dir).resolve().relative_to(ROOT)) if str(Path(out_dir).resolve()).startswith(str(ROOT)) else str(out_dir)
    t = a['hourly_taker']
    q = t['books']['%s|median|%d' % (quote, size)]
    qf = t['books']['%s|first|%d' % (quote, size)]
    fung = t['books']['all5|median|%d' % size]
    a4 = t['books']['all4|median|%d' % size]
    late1h, late1d = t['late_entry']['%s|%d|1h' % (quote, size)], t['late_entry']['%s|%d|1d' % (quote, size)]
    own5, own_cross, own4 = a['joint']['all5'][str(size)], a['rotation']['1d|%d' % size], a['joint']['all4'][str(size)]
    sp = t['split_15m']
    ov = a['overlap']
    kcorr = {k: ov['pairs']['%s|%s' % tuple(sorted((k, 'khype')))]['corr_daily_locked'] for k in SETS['all4']}
    per = t['persistence']['1.0']
    go = go_rule(q, late1d)
    ci = q['oos_ci95_usd_per_year']
    conc = a['concentration']['all5'][str(size)]
    thesis = (
        'Five queue bids on one pool, priced as an executable hourly taker: each sale that cleared the hurdle in its own hour is '
        'bought back at the next hour boundary at that hour\'s venue median. The book adds kHYPE on HyperEVM, whose locked capital '
        'is uncorrelated with the Ethereum-side bids (%s against the three ETH bids summed; %s). On the five assets\' common '
        'window (%s to %s, split %s) a %s pool whose kHYPE leg is reached a day after capital starts to move earned %s a year '
        'out of sample (t %.2f, 95%% interval %s to %s; in sample %s), against %s for the four Ethereum-side bids priced the '
        'same way on the same capital: +%s. At the first trade after each boundary it is %s; with capital that moves '
        'instantly %s; the backtest\'s own-print pricing gave %s. The discounts persist: of the sales that qualified in their own '
        'hour, %s (stETH), %s (weETH), %s (kHYPE) still cleared 1bp at the next hour\'s median; rsETH (%s) and LBTC (%s) '
        'often had no trade in the next hour. Late entry with the later price keeps %s (an hour) and %s (a day).') % (
        ft(ov['khype_against_sums']['corr_with_eth3_sum']), ', '.join('%s %s' % (NAMES[k], ft(v)) for k, v in kcorr.items()),
        a['window'][0][:10], a['window'][1][:10], a['cutoff_utc'][:10], fmt(size), fmt(q['out_of_sample_usd_per_year']), q['oos_t'],
        fmt(ci[0]), fmt(ci[1]), fmt(q['in_sample_usd_per_year']), fmt(a4['out_of_sample_usd_per_year']),
        fmt((q['out_of_sample_usd_per_year'] or 0.0) - (a4['out_of_sample_usd_per_year'] or 0.0)), fmt(qf['out_of_sample_usd_per_year']),
        fmt(fung['out_of_sample_usd_per_year']), fmt(own_cross['out_of_sample_usd_per_year']),
        fpct(per['lido']['hour|median']['all']['still_clear_share']), fpct(per['etherfi_ev']['hour|median']['all']['still_clear_share']),
        fpct(per['khype']['hour|median']['all']['still_clear_share']), fpct(per['kelp']['hour|median']['all']['still_clear_share']),
        fpct(per['lbtc_cb']['hour|median']['all']['still_clear_share']), fpct(late1h['kept_share']), fpct(late1d['kept_share']))
    mechanism = (
        'Holders who will not wait for a withdrawal queue sell the staking token below what the queue pays; a patient bidder '
        'buys after them and redeems (per-asset mechanisms and payout checks: research/2026-10-09/redemption_history, '
        'research/2026-10-10/queue_bids_ext, research/2026-10-10/queue_bids_alt; Kinetiq paid 13,426 of 13,426 kHYPE '
        'confirmations exactly). The discounts last beyond the hour of the sale, so an hourly keeper buying the previous hour\'s '
        'qualifying sales at the market captures most of them without racing anyone (research/2026-10-11/queue_live). Capital is '
        'bound by time in the queue and the queues stall at different times, so one pool rotates through them; in a kHYPE '
        'stress the whole pool wants to be on HyperEVM, which is why the quote charges a day for the crossing each way.')
    legs = [
        'Ethereum: hold WETH/aWETH and cbBTC (or borrowing power against wstETH) as one balance; at each hour boundary a keeper '
        'submits one CoW order per token (stETH, weETH, rsETH; LBTC against cbBTC) for the previous hour\'s sales whose edge '
        'cleared the hurdle (%sbp over fees and the queue\'s carry), limited at that edge; the sale happened up to an hour earlier, so '
        'nothing races for block position' % q['chosen_hurdle'].replace('h=', ''),
        'HyperEVM (kHYPE leg): CoW Protocol is not deployed there; when the kHYPE venue median has cleared the hurdle, move '
        'capital across to WHYPE and have the keeper buy the previous hour\'s qualifying kHYPE sales back on the kHYPE/WHYPE AMM '
        'pools at the hour boundary (queue_bids_alt: Project X carried most of the volume since launch; this pool\'s out-of-sample '
        'fills were on %s). Valantis STEX, Kinetiq\'s instant-unstake pool, is a competing standing bidder there, not a venue' % ', '.join(
            '%s (%s)' % (k, format(v, ',')) for k, v in sorted(((conc.get('oos_fills_by_pool') or {}).get('khype') or {}).items(), key=lambda kv: -kv[1])),
        'on a fill, request withdrawal (Lido WithdrawalQueueERC721, ether.fi WithdrawRequestNFT, Kelp LRTWithdrawalManager, LBTC '
        'redeemForBtc, Kinetiq StakingManager.queueWithdrawal); claim when finalized (kHYPE: confirmWithdrawal after the 7-day '
        'withdrawalDelay) and move the proceeds back to the Ethereum balance',
        'hedge the HYPE held on HyperEVM, idle or queued, with a short HYPE perp on Hyperliquid (the bid is priced in HYPE)']
    entry = {
        'id': 'lst-queue-book-one-pool', 'name': 'One capital pool behind the stETH, weETH, rsETH, LBTC and kHYPE queue bids, run as an hourly taker',
        'kind': 'redemption', 'status': 'proposed', 'draft': True,
        'thesis': thesis, 'mechanism': mechanism, 'legs': legs, 'capacity_usd': size,
        'capital_days': round(conc['oos_usd_weighted_wait_days'], 1) if conc.get('oos_usd_weighted_wait_days') else None,
        'kill_criteria': [
            'trailing 90-day simulated value of the five-asset hourly taker under $40,000 a year at %s (it was %s)' % (
                fmt(size), fmt(q.get('trailing_90d_usd_per_year'))),
            'any component\'s payout check failing (a claim paying less than requested, a fee appearing, an invalidated request that '
            'is not repaid; for kHYPE a confirmation below its WithdrawalQueued hypeAmount or a non-zero unstakeFeeRate)',
            'the daily correlation of LBTC\'s or kHYPE\'s locked capital with the ETH tokens\' rising above 0.5 over a trailing year',
            'the share of qualifying sales still clearing the hurdle at the next hour\'s venue median falling under half for a quarter '
            '(the persistence the taker lives on)',
            'capital taking more than a day to reach HyperEVM in a kHYPE episode; Kinetiq\'s fastest confirmation above 10 days for a '
            'month, or withdrawals paused for more than a week'],
        'quotes': [{'at': a['generated'], 'source': 'history', 'window': rel,
                    'net_apr': round((q['out_of_sample_usd_per_year'] or 0.0) / size, 4), 'usd': round(q['out_of_sample_usd_per_year'] or 0.0),
                    'go': go, 'present': True,
                    'note': ('hourly taker at the next hour\'s venue median, out of sample %s..%s, five assets on one %s pool with the kHYPE '
                             'leg a day behind; hurdle chosen in sample (%s; in sample %s), t %.2f; late entry (later price) 1h %s, 1d %s; '
                             'first-trade reading %s; fungible taker %s; fixed split %s; all4 taker on the same window %s; own-print '
                             'pricing %s (crossing) and %s (fungible); by asset %s. Draft: replaces the 2026-10-10 quote ($409,889, '
                             'own-print all4) only if the coordinator accepts it') % (
                        a['cutoff_utc'][:10], a['window'][1][:10], fmt(size), q['chosen_hurdle'], fmt(q['in_sample_usd_per_year']), q['oos_t'],
                        fpct(late1h['kept_share']), fpct(late1d['kept_share']), fmt(qf['out_of_sample_usd_per_year']),
                        fmt(fung['out_of_sample_usd_per_year']), fmt(sp['chosen_out_of_sample_usd_per_year']), fmt(a4['out_of_sample_usd_per_year']),
                        fmt(own_cross['out_of_sample_usd_per_year']), fmt(own5['out_of_sample_usd_per_year']),
                        ', '.join('%s %s' % (NAMES[k], fmt(v)) for k, v in q['oos_by_asset_usd_per_year'].items()))}],
        'go_rule': {'variant': 'all5 hourly taker (next hour, venue median), kHYPE leg a day behind', 'in_sample_positive': q.get('in_sample_positive'),
                    'oos_t': q['oos_t'], 'late_1d_kept_share': late1d['kept_share'], 'thresholds': dict(BOOK5_GO, in_sample_positive=True), 'go': go},
        'variants_usd_per_year': {
            'taker_1d_crossing_median': q['out_of_sample_usd_per_year'], 'taker_1d_crossing_first_trade': qf['out_of_sample_usd_per_year'],
            'taker_fungible_median': fung['out_of_sample_usd_per_year'], 'taker_fixed_split_median': sp['chosen_out_of_sample_usd_per_year'],
            'taker_all4_median': a4['out_of_sample_usd_per_year'], 'own_print_1d_crossing': own_cross['out_of_sample_usd_per_year'],
            'own_print_fungible': own5['out_of_sample_usd_per_year'], 'own_print_all4': own4['out_of_sample_usd_per_year']},
        'risks': [
            'the out-of-sample half is short (%s to %s, %d days) because kHYPE launched in July 2025; the in-sample half, which holds '
            'the 2025 kHYPE and Lido stresses, was %.1fx richer' % (a['cutoff_utc'][:10], a['window'][1][:10], a['days'] - B.cutoff_index(a['days'], 0.5),
                                                                  (q['in_sample_usd_per_year'] or 0.0) / (q['out_of_sample_usd_per_year'] or 1.0)),
            'the hourly taker is a model of a keeper that has not run: a CoW order may not fill at the hour\'s median, and the later '
            'price can be worse than the median for size (the first-trade reading brackets it)',
            'competing bidders (83 CoW owners in the April 2026 stETH episode; Valantis STEX and arbitrageurs on kHYPE) are not '
            'simulated: values are ceilings for one participant',
            'capital split across chains: the quote charges a day each way for the crossing; a fixed HyperEVM sub-pool earns %s' % fmt(
                sp['chosen_out_of_sample_usd_per_year']),
            'HYPE price exposure of capital on HyperEVM unless hedged; Kinetiq contract, validator and governance risk on HYPE queued a week',
            'the component risks stand: Lido bunker mode, ether.fi request invalidation, Kelp withdrawal pauses, LBTC\'s off-chain '
            'payout (9-day wait from docs)'],
        'evidence': {'notes': '%s/tables.md (The hourly taker); analysis.json (hourly_taker, joint, rotation, split, overlap); '
                              'research/2026-10-11/queue_live (implementations f, g); scripts/queue_book.py (simulate_book later=); '
                              'scripts/queue_bids_alt.py (khype_book_env)' % rel,
                     'findings': [], 'verify': []},
        'recheck_hours': 168}
    return [entry]


def khype_requote_entry(a, out_dir, size=KHYPE_BOOK_SIZE):
    """A DRAFT re-quote of `kinetiq-khype-queue-bid` as an hourly taker (id kept; not written to the book)."""
    rel = str(Path(out_dir).resolve().relative_to(ROOT)) if str(Path(out_dir).resolve()).startswith(str(ROOT)) else str(out_dir)
    t = a['hourly_taker']
    m, f, m30 = t['khype_alone']['median|%d' % size], t['khype_alone']['first|%d' % size], t['khype_alone']['median|30000000']
    p1, p10 = t['persistence']['1.0']['khype']['hour|median']['all'], t['persistence']['10.0']['khype']['hour|median']['all']
    go = go_rule(m, m['late_1d'])
    ci = m['oos_ci95_usd_per_year']
    entry = {
        'id': 'kinetiq-khype-queue-bid', 'name': 'Buy kHYPE below the HYPE Kinetiq pays for it and redeem through the 7-day queue (hourly taker)',
        'kind': 'redemption', 'status': 'proposed', 'draft': True, 'requote_of': 'kinetiq-khype-queue-bid (research/2026-10-10/queue_bids_alt, $140,043 own-print)',
        'thesis': ('kHYPE trades below the HYPE its withdrawal queue pays, and the discount lasts: %s of the sales that cleared 1bp in their '
                   'own hour still cleared it at the next hour\'s venue median (%s of those clearing 10bp still cleared 10bp), and the next '
                   'hour always had trades. Bought back at each hour boundary at that hour\'s venue median, a %s bid that redeems every '
                   'fill made %s a year out of sample (t %.2f, 95%% interval %s to %s), against %s when each sale was bought at its own '
                   'print; %s at the first trade after the boundary; %s at $30M (t %.2f).') % (
            fpct(p1['still_clear_share']), fpct(p10['still_clear_share']), fmt(size), fmt(m['out_of_sample_usd_per_year']), m['oos_t'],
            fmt(ci[0]), fmt(ci[1]), fmt(m['own_print_out_of_sample_usd_per_year']), fmt(f['out_of_sample_usd_per_year']),
            fmt(m30['out_of_sample_usd_per_year']), m30['oos_t']),
        'mechanism': ('Anyone can queueWithdrawal(kHYPE) on Kinetiq\'s StakingManager; the HYPE amount is fixed at the request at '
                      'StakingAccountant.kHYPEToHYPE and confirmWithdrawal pays it after withdrawalDelay (604,800 s); every one of 13,426 '
                      'confirmations paid exactly its request and the 10bp unstake fee was set to zero on 2026-04-08. The taker prices '
                      'against kHYPEToHYPE, waits the fastest confirmation seen within a day of the purchase (never under 7 days), charges '
                      'two pool fees and the staking yield forgone while queued, and pays the venue median of the hour after the sale.'),
        'legs': ['at each hour boundary, buy the previous hour\'s kHYPE sales whose edge cleared the hurdle back on the kHYPE/WHYPE pools '
                 '(Project X, Ramses v3, Nest, HyperSwap v3, Hybra) at the market, priced at that hour\'s venue median',
                 'queueWithdrawal on the Kinetiq StakingManager', 'confirmWithdrawal after 7 days; unwrap or reuse the HYPE'],
        'capacity_usd': size, 'capital_days': 8.5,
        'capacity_rule': {'size_usd': 30_000_000, 'oos_usd_per_year': m30['out_of_sample_usd_per_year'], 'oos_t': m30['oos_t']},
        'kill_criteria': ['trailing 90-day value of the hourly taker under $10k a year at the quoted size (it was %s)' % fmt(m['trailing_90d_usd_per_year']),
                          'any confirmation paying less than its WithdrawalQueued hypeAmount, or a non-zero unstakeFeeRate',
                          'the fastest confirmation over a month above 10 days', 'withdrawals paused for over a week',
                          'under half of the qualifying sales still clearing the hurdle at the next hour\'s median over a quarter'],
        'risks': ['HYPE price exposure of the capital unless hedged (a short HYPE perp, which itself earns funding)',
                  'Kinetiq contract, validator slashing and governance risk on HYPE queued for a week',
                  'other bidders (Valantis STEX, arbitrageurs) not simulated: values are ceilings for one participant',
                  'lumpy: most of the value comes from stress episodes; the chosen hurdle (%s) ranked %s of 7 out of sample' % (
                      m['chosen_hurdle'], t['khype_alone']['median|%d' % size].get('oos_rank_of_chosen', '—'))],
        'evidence': {'notes': '%s/tables.md (The hourly taker); analysis.json (hourly_taker.khype_alone, persistence); '
                              'research/2026-10-10/queue_bids_alt; scripts/queue_book.py; scripts/queue_bids_alt.py' % rel,
                     'findings': [], 'verify': []},
        'quotes': [{'at': a['generated'], 'go': go, 'present': True, 'source': 'history', 'usd': round(m['out_of_sample_usd_per_year'] or 0.0),
                    'net_apr': round((m['out_of_sample_usd_per_year'] or 0.0) / size, 4), 'window': rel,
                    'note': ('hourly taker at the next hour\'s venue median, 2025-07-15..2026-10-09 split %s; hurdle %s chosen in sample (in '
                             'sample %s), t %.2f; first-trade reading %s; late entry (later price) 1h %s, 1d %s; replaces the own-print '
                             'quote of $140,043 only if the coordinator accepts it; the go rule (t above 2) %s') % (
                        a['cutoff_utc'][:10], m['chosen_hurdle'], fmt(m['in_sample_usd_per_year']), m['oos_t'], fmt(f['out_of_sample_usd_per_year']),
                        fpct(m['late_1h']['kept_share']), fpct(m['late_1d']['kept_share']), 'passes' if go else 'fails at this size')}],
        'go_rule': {'in_sample_positive': m.get('in_sample_positive'), 'oos_t': m['oos_t'], 'late_1d_kept_share': m['late_1d']['kept_share'],
                    'thresholds': dict(BOOK5_GO, in_sample_positive=True), 'go': go},
        'recheck_hours': 168}
    return [entry]


def cmd_render(args):
    out = Path(args.out)
    a = D.read_json(out / 'analysis.json')
    if 'khype_reproduction' in a:
        render_khype(a, out)
        D.write_json(out / 'book_entries.json', book_entries_khype(a, out))
        if a.get('hourly_taker'):
            D.write_json(out / 'book_entries_khype_requote.json', khype_requote_entry(a, out))
        return
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
    a.add_argument('--khype', help='queue_bids_alt output directory: add kHYPE (sets all5, eth3_khype) and run the '
                                   'five-asset protocol on the common window (default: the four-asset 2026-10-10 run)')
    r = sub.add_parser('render')
    r.add_argument('--out', required=True)
    args = p.parse_args()
    {'analyze': cmd_analyze, 'render': cmd_render}[args.cmd](args)


if __name__ == '__main__':
    main()
