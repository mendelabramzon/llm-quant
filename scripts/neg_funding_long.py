#!/usr/bin/env python3
"""Long the perp after its funding goes deeply negative: when shorts have paid longs extreme funding for a day or
three, does a long entered late (a full day after the signal) collect more funding than the price drift takes away?

Why. On 2026-10-23 several Binance alt perps (BTW, BIRB, ALT, GTC, ARK) were settling at -20bp to -199bp per 4 h, every
settlement, for days: shorts paying longs at 1,000%+ a year. Whoever pays that is presumably a hedger who cannot borrow
the spot (airdrop, unlock and locked-token holders), and such hedgers are exactly the agents with a non-price motive the
repo's surviving edges come from. But the same supply that makes them hedge also lands on the market, so the price may
fall faster than the funding pays. This study prices that on two years of history, delisted perps included (the coins
that collapse are the ones this rule buys), with the late-entry rule, taker costs and volume-based capacity.

How.
  collect   Tops up the alt_floor_carry raw files (Binance USD-M and Bybit linear, 2024-10-01 -> 2026-10-10) to now:
            Binance bulk funding (no symbol, paged forward) from 2026-10-09, fresh exchangeInfo / fundingInfo / book and
            24 h tickers, daily perp klines from 2026-09-01 for every perp in the top-up funding; Bybit funding and daily
            klines for every Trading linear perp whose symbol is also a Binance perp; hourly klines (both venues) for
            the names in today's episode. Kept under <out>/raw/topup/.
  grid      Writes the rule family into analysis.json before any return is computed.
  analyze   Builds every Binance USDT perp (spot not required, delisted kept, phantom post-delisting settlements and
            untraded days cut by alt_floor_carry.clean_funding), runs the family as events, then backtest.choose_then_test
            on daily portfolio excess split at 2025-10-06 (the alt_floor_carry convention), BH on one-sided full-sample
            HAC p, robustness rows (lag 0, volume floors, zero costs, Bybit as the venue), the Binance-Bybit funding-gap
            carry, the current episode, and capacity. Writes analysis.json, trades.json.gz and tables.md.

Conventions. A rate is per settlement, positive when longs pay; a long receives -rate x quantity x mark. Day d holds the
settlements in (d 00:00, d+1 00:00] UTC (alt_floor_carry.day_of) and the kline that opens at d 00:00. A trailing
signal is restated per 8 h from the settlements' own intervals: F_L(d) = sum of rates on days d-L..d-1 x 8 / hours
covered, so 4 h and 1 h perps are on one scale (Binance switches a perp to 4 h, then 1 h, as funding hits its cap).
The decision at the start of day d sees days <= d-1. Late entry (lag 1, the default): the long is bought at the close
of day d (the next day's open), a full day after the signal's last settlement, and earns funding from day d+1. Lag 0
(bought at the close of day d-1, the instant the signal completes) is a sensitivity row only. A position is a fixed
quantity (1 / entry price per $ of notional) at 1x (no liquidation); its daily P&L per $ of entry notional is
funding + close-to-close price change; costs are taker (VIP0 perp 5bp; Bybit 5.5bp) plus the alt_floor_carry
half-spread model by trailing-7-day volume on each side; excess subtracts the savings rate (3.80% constant) on the
capital while it is deployed. Exit: after H days, or ('N') at the close of the day after the first held day whose
funding is back above NORMAL_8H, capped at MAX_HOLD days; a perp that stops trading exits at its last traded close.
A coin is not re-entered while a trade in it is open. Portfolio daily return = mean over open trades (equal weight,
idle days 0). Capacity: each trade is sized at most PARTICIPATION of its trailing-7-day median perp volume, entered and
exited in one day, square-root impact Y x sigma x sqrt(size / volume) per side.

    uv run python scripts/neg_funding_long.py collect --out research/2026-10-23/neg_funding_long
    uv run python scripts/neg_funding_long.py grid --out research/2026-10-23/neg_funding_long
    uv run python scripts/neg_funding_long.py analyze --out research/2026-10-23/neg_funding_long

Read-only: public, unauthenticated endpoints only; nothing is signed or sent.
"""
import argparse
import collections
import datetime as dt
import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B                 # noqa: E402
import alt_floor_carry as AF         # noqa: E402
from alt_floor_carry import (DAY_MS, HOUR_MS, day_ms, dname, utc, write_gz, read_gz, write_json, fnum, bad,  # noqa: E402
                             kline_days, clean_funding, half_spread_bp, impact_frac, VENUE_FEES_BP,
                             DELISTED_STATUS, EXCLUDE_BASES, SSR_CONST)

OUT = ROOT / 'research' / '2026-10-23' / 'neg_funding_long'
HIST = AF.OUT                        # research/2026-10-11/alt_floor_carry (raw files reused, never re-downloaded)
TOPUP_FUND_START = '2026-10-09'
TOPUP_KLINE_START = '2026-09-01'
EPISODE_START = '2026-10-15'         # hourly klines from here for the live names
EPISODE_NAMES = ['BTWUSDT', 'BIRBUSDT', 'ALTUSDT', 'GTCUSDT', 'ARKUSDT']
PNL_START = AF.PNL_START             # 2024-10-01
SPLIT_DAY = '2025-10-06'             # alt_floor_carry's in/out-of-sample cut

GRID = {'lookback_days': [1, 3], 'thr_8h_bp': [-10, -25, -50, -100], 'hold': [1, 3, 7, 'N'],
        'perp_vol_min_usd': [5e6]}
LAG = 1                              # days between the signal's last settlement and the entry close
NORMAL_8H = -0.0005                  # 'N' exit: a held day whose funding per 8 h is above -5bp
MAX_HOLD = 28
VOL_DAYS = 7                         # trailing median perp quote volume (liquidity floor, spreads, capacity)
SIGMA_DAYS = 30
MIN_COVER = 0.8                      # hours settled / hours in the lookback
PARTICIPATION = 0.02
IMPACT_Y = 0.5
SIZES = [50_000, 250_000, 1_000_000]
GAP_GRID = {'lookback_days': [1, 3], 'gap_8h_bp': [10, 25, 50], 'hold': [1, 3, 7]}
BN_F, BY = AF.BN_F, AF.BY


# ---------------------------------------------------------------------------------------------- collect (top-up)

def collect(out):
    out = Path(out)
    raw = out / 'raw' / 'topup'
    raw.mkdir(parents=True, exist_ok=True)
    now_ms = int(time.time() * 1000)
    log = {'started': utc(), 'end_ms': now_ms}
    hf, hfund, hb = AF.bn_http(0.25), AF.bn_http(0.7), AF.by_http()
    for name, url in (('fapi_exchangeInfo', '/fapi/v1/exchangeInfo'), ('fapi_fundingInfo', '/fapi/v1/fundingInfo'),
                      ('fapi_bookTicker', '/fapi/v1/ticker/bookTicker'), ('fapi_ticker24hr', '/fapi/v1/ticker/24hr')):
        r = hf.get(BN_F + url)
        if bad(r):
            raise RuntimeError('%s: %s' % (name, json.dumps(r)[:200]))
        write_gz(raw / (name + '.json.gz'), {'fetched_at': utc(), 'url': BN_F + url, 'data': r})
    # Binance bulk funding, forward from TOPUP_FUND_START (overlaps the history by a day; duplicates drop on load)
    fb = raw / 'funding_bulk'
    for fn in fb.glob('chunk_*.json.gz'):
        fn.unlink()
    st = fb / 'state.json'
    if st.exists():
        st.unlink()
    AF.collect_funding_bulk(hfund, raw, day_ms(TOPUP_FUND_START), now_ms, log)
    fund = AF.load_funding_bulk(raw)
    syms = sorted(fund)
    kd = raw / 'perp_klines'
    for i, sym in enumerate(syms):
        r = hf.get(BN_F + '/fapi/v1/klines', {'symbol': sym, 'interval': '1d', 'startTime': day_ms(TOPUP_KLINE_START),
                                              'limit': 1000})
        write_gz(kd / ('%s.json.gz' % sym), r if isinstance(r, list) else {'error': r})
        if (i + 1) % 100 == 0:
            print('binance perp klines %d/%d' % (i + 1, len(syms)), flush=True)
    # names in today's episode: the five from the lead plus every perp whose last-3-day funding is below -10bp / 8 h
    ep = set(EPISODE_NAMES)
    t0 = now_ms - 3 * DAY_MS
    for sym, ev in fund.items():
        xs = [r for t, r, _ in ev if t >= t0 and r is not None]
        if xs and sum(xs) * 8.0 / 72.0 <= -0.001:           # below -10bp per 8 h over the last 72 h
            ep.add(sym)
    log['episode_names'] = sorted(ep)
    for sym in sorted(ep):
        r = hf.get(BN_F + '/fapi/v1/klines', {'symbol': sym, 'interval': '1h', 'startTime': day_ms(EPISODE_START),
                                              'limit': 1000})
        write_gz(raw / 'perp_klines_1h' / ('%s.json.gz' % sym), r if isinstance(r, list) else {'error': r})
    # Bybit: Trading linear perps that are also Binance perps
    pages, cursor = [], None
    while True:
        p = {'category': 'linear', 'limit': 1000, 'status': 'Trading'}
        if cursor:
            p['cursor'] = cursor
        r = hb.get(BY + '/v5/market/instruments-info', p)
        pages.append(r)
        cursor = ((r or {}).get('result') or {}).get('nextPageCursor')
        if not cursor or not AF.by_list(r):
            break
    write_gz(raw / 'bybit_instruments_linear_Trading.json.gz', {'fetched_at': utc(), 'pages': pages})
    by_syms = sorted({x['symbol'] for pg in pages for x in (AF.by_list(pg) or [])
                      if x.get('contractType') == 'LinearPerpetual' and x.get('quoteCoin') == 'USDT'} & set(fund))
    log['bybit_symbols'] = len(by_syms)
    for i, sym in enumerate(by_syms):
        rows, end = [], now_ms
        while True:
            r = hb.get(BY + '/v5/market/funding/history', {'category': 'linear', 'symbol': sym, 'limit': 200,
                                                           'startTime': day_ms(TOPUP_FUND_START), 'endTime': end})
            L = AF.by_list(r)
            if not L:
                break
            rows.append(r)
            oldest = min(int(x['fundingRateTimestamp']) for x in L)
            if len(L) < 200 or oldest <= day_ms(TOPUP_FUND_START):
                break
            end = oldest - 1
        write_gz(raw / 'bybit_funding' / ('%s.json.gz' % sym), rows)
        r = hb.get(BY + '/v5/market/kline', {'category': 'linear', 'symbol': sym, 'interval': 'D',
                                             'start': day_ms(TOPUP_KLINE_START), 'limit': 1000})
        write_gz(raw / 'bybit_perp_klines' / ('%s.json.gz' % sym), r)
        if sym in ep:
            r = hb.get(BY + '/v5/market/kline', {'category': 'linear', 'symbol': sym, 'interval': '60',
                                                 'start': day_ms(EPISODE_START), 'limit': 1000})
            write_gz(raw / 'bybit_perp_klines_1h' / ('%s.json.gz' % sym), r)
        if (i + 1) % 100 == 0:
            print('bybit %d/%d' % (i + 1, len(by_syms)), flush=True)
    log['http'] = {'fapi': hf.stats(), 'funding': hfund.stats(), 'bybit': hb.stats()}
    log['finished'] = utc()
    write_json(raw / 'manifest.json', log)
    return log


# ---------------------------------------------------------------------------------------------- inputs (history + top-up)

def merge_funding(a, b):
    out = {}
    for s in set(a) | set(b):
        m = {t: (r, mk) for t, r, mk in a.get(s, [])}
        m.update({t: (r, mk) for t, r, mk in b.get(s, [])})
        out[s] = sorted((t, r, mk) for t, (r, mk) in m.items())
    return out


def bybit_funding_rows(pages):
    ev = {}
    for p in pages or []:
        for x in AF.by_list(p) or []:
            ev[int(x['fundingRateTimestamp'])] = fnum(x.get('fundingRate'))
    return sorted((t, r, None) for t, r in ev.items())


def inputs(out, venue):
    """alt_floor_carry.venue_inputs for the history, the top-up merged over it (top-up wins on overlapping days and
    stamps). end_ms = today 00:00 UTC, so today's partial bar is never a backtest price."""
    out = Path(out)
    top = out / 'raw' / 'topup'
    tman = json.loads((top / 'manifest.json').read_text())
    vi = AF.venue_inputs(HIST, venue)
    end_ms = (tman['end_ms'] // DAY_MS) * DAY_MS
    old_bars = vi['perp_bars']
    if venue == 'binance':
        fex = read_gz(top / 'fapi_exchangeInfo.json.gz')['data']
        new = AF.perp_universe(fex, [])
        for s in fex.get('symbols') or []:
            if s['symbol'] in new:
                new[s['symbol']]['tick'] = AF.tick_of(s)
        uni = dict(vi['uni'])
        uni.update(new)
        fund = merge_funding(vi['funding'], AF.load_funding_bulk(top))
        for s in fund:
            if s not in uni and s.endswith('USDT'):
                uni[s] = {'base': s[:-4], 'status': 'absent_from_exchangeInfo', 'source': 'funding_history',
                          'onboard_ms': None, 'delivery_ms': None, 'max_lev': None, 'tick': None}

        def bars(sym):
            d = dict(old_bars(sym))
            d.update(kline_days(AF.read_or(top / 'perp_klines' / ('%s.json.gz' % sym), [])))
            return d
    else:
        uni = dict(vi['uni'])
        fund = dict(vi['funding'])
        for fn in (top / 'bybit_funding').glob('*.json.gz'):
            s = fn.name[:-8]
            fund[s] = merge_funding({s: fund.get(s, [])}, {s: bybit_funding_rows(read_gz(fn))})[s]
        inst = read_gz(top / 'bybit_instruments_linear_Trading.json.gz')['pages']
        for x in (y for p in inst for y in (AF.by_list(p) or [])):
            if x['symbol'] in fund and x['symbol'] not in uni and x.get('contractType') == 'LinearPerpetual':
                uni[x['symbol']] = {'base': x.get('baseCoin'), 'status': x.get('status'), 'source': 'instruments',
                                    'onboard_ms': fnum(x.get('launchTime')), 'delivery_ms': None, 'max_lev': None,
                                    'tick': fnum((x.get('priceFilter') or {}).get('tickSize'))}

        def bars(sym):
            d = dict(old_bars(sym))
            d.update(AF.kline_days_bybit(AF.read_or(top / 'bybit_perp_klines' / ('%s.json.gz' % sym), {})))
            return d
    return {'venue': venue, 'end_ms': end_ms, 'uni': uni, 'funding': fund, 'perp_bars': bars,
            'perp_spread': vi['spread'][1], 'fees': VENUE_FEES_BP[venue], 'hist_end': vi['manifest']['log']['window']}


def build_perps(vi):
    """Every coin perp of the venue (spot not required): traded daily bars, real settlements by funding day, last
    traded day. Returns (perps, report, last complete day)."""
    end_ms = vi['end_ms']
    last_day = end_ms // DAY_MS - 1
    rep = collections.Counter()
    perps = {}
    for sym, info in sorted(vi['uni'].items()):
        if not sym.endswith('USDT') or (info.get('base') or sym[:-4]) in EXCLUDE_BASES:
            rep['excluded'] += 1
            continue
        pdays = {d: v for d, v in vi['perp_bars'](sym).items() if d <= last_day}
        if not pdays:
            rep['no_traded_bar'] += 1
            continue
        dlv = info.get('delivery_ms') if (info.get('status') == DELISTED_STATUS[vi['venue']] and
                                          info.get('delivery_ms') and info['delivery_ms'] < end_ms) else None
        ev, dropped = clean_funding(vi['funding'].get(sym, []), pdays, dlv)
        rep['settlements_kept'] += len(ev)
        rep['settlements_dropped_untraded_or_after_delivery'] += dropped
        fd = collections.defaultdict(list)
        for t, r, m, h, d in ev:
            fd[d].append((t, r, m, h))
        lp = max(pdays)
        perps[sym] = {'sym': sym, 'base': info.get('base'), 'status': info.get('status'),
                      'pc': {d: v[0] for d, v in pdays.items()}, 'pv': {d: v[1] for d, v in pdays.items()},
                      'fd': dict(fd), 'fs': {d: sum(x[1] for x in v) for d, v in fd.items()},
                      'fh': {d: sum(x[3] for x in v) for d, v in fd.items()},
                      'first_p': min(pdays), 'last_p': lp, 'delisted': lp < last_day - 1, 'tick': info.get('tick')}
        rep['perps'] += 1
        rep['perps_delisted_in_window'] += int(lp < last_day - 1)
    rep = dict(rep)
    rep['last_day'] = dname(last_day)
    return perps, rep, last_day


# ---------------------------------------------------------------------------------------------- the rule

def signal(p, d, L):
    """Funding per 8 h over days d-L..d-1 from the settlements' own intervals, or None if under-covered (memoised)."""
    key = (d, L)
    cache = p.setdefault('_sig', {})
    if key not in cache:
        cache[key] = _signal(p, d, L)
    return cache[key]


def _signal(p, d, L):
    h = sum(p['fh'].get(x, 0) for x in range(d - L, d))
    if h < MIN_COVER * 24 * L:
        return None
    return sum(p['fs'].get(x, 0.0) for x in range(d - L, d)) * 8.0 / h


def vol_med(p, d, n=VOL_DAYS):
    cache = p.setdefault('_vol', {})
    if (d, n) not in cache:
        cache[(d, n)] = _vol_med(p, d, n)
    return cache[(d, n)]


def _vol_med(p, d, n):
    return statistics.median(p['pv'].get(x, 0.0) for x in range(d - n, d))


def sigma_of(p, d, n=SIGMA_DAYS):
    r = [math.log(p['pc'][x] / p['pc'][x - 1]) for x in range(d - n + 1, d) if x in p['pc'] and x - 1 in p['pc']]
    return statistics.pstdev(r) if len(r) >= 10 else None


def side_cost(vi, p, vol, px, mult=1.0):
    tick_bp = 0.5 * p['tick'] / px * 1e4 if p.get('tick') and px else 0.0
    return (vi['fees']['perp'] + half_spread_bp(vi['perp_spread'], vol, tick_bp)) / 1e4 * mult


def run_trade(p, d, e, hold, last_day):
    """One long bought at the close of day e (decision at the start of day d). Daily rows (day, funding, price) per $
    of entry notional, and the exit day. hold: int days, or 'N' (exit at the close of the day after the first held
    day with funding per 8 h above NORMAL_8H; at most MAX_HOLD days)."""
    P0 = p['pc'][e]
    prev = P0
    X = e + (hold if hold != 'N' else MAX_HOLD)
    rows, k, exit_day, normalised = [], e, e, None
    while k < min(X, last_day):
        k += 1
        if k > p['last_p']:
            break                                   # stopped trading: out at the last traded close
        f = -sum(r * ((m if m and m > 0 else prev) / P0) for _, r, m, _ in p['fd'].get(k, ()))
        pr = 0.0
        if k in p['pc']:
            pr = (p['pc'][k] - prev) / P0
            prev = p['pc'][k]
            exit_day = k
        rows.append((k, f, pr))
        if hold == 'N' and normalised is None and p['fh'].get(k):
            if p['fs'][k] * 8.0 / p['fh'][k] > NORMAL_8H:
                normalised = k
                X = min(X, k + 1)
    while rows and rows[-1][0] > exit_day:         # untraded tail days carry nothing
        rows.pop()
    return rows, exit_day, (k >= last_day and exit_day == last_day and k < X)


def run_variant(vi, perps, v, days, last_day, lag=LAG, cost_mult=1.0):
    """All trades of one variant: per perp, decision days in order, no re-entry while a trade is open."""
    L, thr, hold, vmin = v['lookback_days'], v['thr_8h_bp'] / 1e4, v['hold'], v['perp_vol_min_usd']
    trades = []
    d0, d1 = days[0], days[-1]
    for sym, p in perps.items():
        busy = -1
        for d in range(max(d0, p['first_p'] + L), d1 + 1):
            if d <= busy:
                continue
            F = signal(p, d, L)
            if F is None or F > thr:
                continue
            e = d + lag - 1
            if e not in p['pc'] or e >= last_day:
                continue
            vol = vol_med(p, d)
            if vol < vmin:
                continue
            rows, x, still_open = run_trade(p, d, e, hold, last_day)
            busy = max(x, e + 1)
            if not rows:
                continue
            P0 = p['pc'][e]
            c_in = side_cost(vi, p, vol, P0, cost_mult)
            c_out = 0.0 if (still_open or (p['delisted'] and x == p['last_p'])) else side_cost(vi, p, vol, P0,
                                                                                               cost_mult)
            fund = sum(r[1] for r in rows)
            price = sum(r[2] for r in rows)
            trades.append({'sym': sym, 'decision': d, 'entry': e, 'exit': x, 'days': len(rows), 'signal_8h': F,
                           'vol7': vol, 'sigma': sigma_of(p, d), 'P0': P0, 'funding': fund, 'price': price,
                           'cost': c_in + c_out, 'gross': fund + price, 'net': fund + price - c_in - c_out,
                           'excess': fund + price - c_in - c_out - SSR_CONST / 365.0 * len(rows),
                           'open': still_open, 'delist_exit': bool(p['delisted'] and x == p['last_p']),
                           'rows': rows, 'c_in': c_in, 'c_out': c_out})
    return trades


def daily_series(trades, days):
    """Equal weight over the trades open each day (each trade's daily excess per $ of its notional; costs on its
    first and last day); idle days 0."""
    acc = collections.defaultdict(list)
    for t in trades:
        n = len(t['rows'])
        for i, (k, f, pr) in enumerate(t['rows']):
            x = f + pr - SSR_CONST / 365.0
            if i == 0:
                x -= t['c_in']
            if i == n - 1:
                x -= t['c_out']
            acc[k].append(x)
    return [statistics.fmean(acc[d]) if acc.get(d) else 0.0 for d in days], [len(acc.get(d, ())) for d in days]


def trade_stats(ts):
    if not ts:
        return {'n': 0}
    net = [t['net'] for t in ts]
    g0 = [t['gross'] for t in ts]
    paid = [t for t in ts if t['funding'] > 0]
    s = statistics.pstdev(net) if len(net) > 1 else 0.0
    return {'n': len(ts), 'coins': len({t['sym'] for t in ts}), 'mean_net': statistics.fmean(net),
            'median_net': statistics.median(net), 'hit_rate': sum(1 for x in net if x > 0) / len(net),
            'worst': min(net), 'best': max(net), 'p10': sorted(net)[len(net) // 10],
            'p90': sorted(net)[(9 * len(net)) // 10], 'naive_t': (statistics.fmean(net) / s * math.sqrt(len(net)))
            if s else None, 'mean_funding': statistics.fmean(t['funding'] for t in ts),
            'mean_price': statistics.fmean(t['price'] for t in ts), 'median_price': statistics.median(
                t['price'] for t in ts), 'mean_cost': statistics.fmean(t['cost'] for t in ts),
            'mean_gross_zero_cost': statistics.fmean(g0), 'hit_rate_zero_cost': sum(1 for x in g0 if x > 0) / len(g0),
            'mean_days': statistics.fmean(t['days'] for t in ts),
            'share_price_eats_funding': (sum(1 for t in paid if t['gross'] < 0) / len(paid)) if paid else None,
            'share_price_down': sum(1 for t in ts if t['price'] < 0) / len(ts),
            'delist_exits': sum(1 for t in ts if t['delist_exit']),
            'mean_net_ex_top1pct': statistics.fmean(sorted(net)[:max(1, len(net) - max(1, len(net) // 100))]),
            'mean_net_ex_top5': statistics.fmean(sorted(net)[:-5]) if len(net) > 5 else None,
            'top5_share_of_sum': (sum(sorted(net)[-5:]) / sum(net)) if sum(net) > 0 else None}


def capacity(ts, years, size=None, Y=IMPACT_Y):
    """$ a year from these trades: each sized at min(size, PARTICIPATION x trailing-7-day perp volume), one-day entry
    and exit with square-root impact on both sides; and the capital that is open on an average and a peak day."""
    pnl, notional, by_day = 0.0, 0.0, collections.Counter()
    for t in ts:
        cap = PARTICIPATION * t['vol7']
        s = min(size, cap) if size else cap
        sig = t['sigma'] or 0.10
        imp = impact_frac(s, t['vol7'], sig, Y, days=1) * (1 if (t['open'] or t['delist_exit']) else 2)
        pnl += s * (t['excess'] - imp)
        notional += s
        for k, _, _ in t['rows']:
            by_day[k] += s
    span = max(1e-9, years)
    return {'size_per_trade': size or 'participation cap', 'usd_per_year': pnl / span, 'notional_traded': notional,
            'avg_open_capital': sum(by_day.values()) / (span * 365.0), 'peak_open_capital': max(by_day.values(),
                                                                                                 default=0.0),
            'return_on_avg_capital': (pnl / span) / (sum(by_day.values()) / (span * 365.0)) if by_day else None}


def variants(grid=GRID):
    out = []
    for L in grid['lookback_days']:
        for thr in grid['thr_8h_bp']:
            for h in grid['hold']:
                for v in grid['perp_vol_min_usd']:
                    out.append({'lookback_days': L, 'thr_8h_bp': thr, 'hold': h, 'perp_vol_min_usd': v,
                                'name': 'L%d_T%d_H%s_V%dM' % (L, -thr, h, v / 1e6)})
    return out


def preregistration():
    return {'written_at': utc(), 'grid': GRID, 'n_variants': len(variants()), 'variants': [v['name'] for v in
                                                                                          variants()],
            'gap_grid': GAP_GRID, 'lag_days': LAG, 'normal_8h': NORMAL_8H, 'max_hold': MAX_HOLD,
            'split_day': SPLIT_DAY, 'protocol': 'backtest.choose_then_test on daily portfolio excess (equal weight over '
            'open trades, idle 0), choose on Sharpe before SPLIT_DAY, test after; BH q=0.10 on one-sided full-sample '
            'HAC p', 'pass_rule': 'in-sample positive, OOS HAC t > 2, chosen in one-sided BH survivors, OOS $/yr > 0 at '
            'the participation cap after impact',
            'costs': {'fee_bp': VENUE_FEES_BP, 'half_spread': 'alt_floor_carry spread_table p75 by trailing-7-day perp '
                      'volume, floored at half a tick', 'impact_Y': IMPACT_Y, 'participation': PARTICIPATION},
            'benchmark': 'savings 3.80% constant on deployed days'}


# ---------------------------------------------------------------------------------------------- structure tables

def bucket_table(vi, perps, days, last_day, L=1, horizon=3, edges=(-10, -25, -50, -100, -200, -1e9)):
    """Every coin-day (not just non-overlapping trades) whose trailing-L-day funding is below -10bp / 8 h, bucketed by
    that signal: the next `horizon` days' funding received and price change after a lag-1 entry, at zero cost. This is
    the shape of the effect before any trade rule."""
    acc = collections.defaultdict(list)
    for p in perps.values():
        for d in range(max(days[0], p['first_p'] + L), days[-1] + 1):
            F = signal(p, d, L)
            if F is None or F > edges[0] / 1e4 or d not in p['pc'] or vol_med(p, d) < 5e6:
                continue
            rows, x, _ = run_trade(p, d, d, horizon, last_day)
            if len(rows) < horizon:
                continue
            for i in range(len(edges) - 1):
                if edges[i + 1] / 1e4 < F <= edges[i] / 1e4:
                    acc[i].append((sum(r[1] for r in rows), sum(r[2] for r in rows), d))
    out = []
    for i in range(len(edges) - 1):
        xs = acc.get(i, [])
        if not xs:
            continue
        out.append({'signal_8h_bp': '(%s, %s]' % (edges[i + 1] if edges[i + 1] > -1e8 else '-inf', edges[i]),
                    'n': len(xs), 'mean_funding': statistics.fmean(a for a, _, _ in xs),
                    'mean_price': statistics.fmean(b for _, b, _ in xs),
                    'median_price': statistics.median(b for _, b, _ in xs),
                    'mean_total': statistics.fmean(a + b for a, b, _ in xs),
                    'median_total': statistics.median(a + b for a, b, _ in xs),
                    'hit_total': sum(1 for a, b, _ in xs if a + b > 0) / len(xs)})
    return out


# ---------------------------------------------------------------------------------------------- Binance-Bybit funding gap

def pair_up(bn, by):
    """Same-symbol perps on both venues whose closes agree (median ratio within 2%: same coin, same multiplier)."""
    out = {}
    for s in set(bn) & set(by):
        ov = [d for d in bn[s]['pc'] if d in by[s]['pc']]
        if len(ov) < 14:
            continue
        rs = sorted(bn[s]['pc'][d] / by[s]['pc'][d] for d in ov)
        if abs(rs[len(rs) // 2] - 1.0) <= 0.02:
            out[s] = (bn[s], by[s])
    return out


def gap_trade(a, b, e, hold, last_day):
    """Long a, short b, both bought/sold at the close of day e; daily rows (day, funding, price) per $ of one leg."""
    A0, B0 = a['pc'][e], b['pc'][e]
    pa, pb = A0, B0
    rows, k, X = [], e, e + hold
    stop = min(a['last_p'], b['last_p'], last_day)
    while k < min(X, stop):
        k += 1
        f = -sum(r * ((m if m and m > 0 else pa) / A0) for _, r, m, _ in a['fd'].get(k, ())) + \
            sum(r * ((m if m and m > 0 else pb) / B0) for _, r, m, _ in b['fd'].get(k, ()))
        pr = 0.0
        if k in a['pc'] and k in b['pc']:
            pr = (a['pc'][k] - pa) / A0 - (b['pc'][k] - pb) / B0
            pa, pb = a['pc'][k], b['pc'][k]
        rows.append((k, f, pr))
    return rows


def run_gap(vis, pairs, v, days, last_day, cost_mult=1.0):
    L, g, hold = v['lookback_days'], v['gap_8h_bp'] / 1e4, v['hold']
    trades = []
    for s, (bn, by) in pairs.items():
        busy = -1
        for d in range(max(days[0], max(bn['first_p'], by['first_p']) + L), days[-1] + 1):
            if d <= busy or d not in bn['pc'] or d not in by['pc'] or d >= last_day:
                continue
            Fa, Fb = signal(bn, d, L), signal(by, d, L)
            if Fa is None or Fb is None:
                continue
            G = Fb - Fa                       # > 0: Binance more negative -> long Binance, short Bybit
            if abs(G) < g:
                continue
            vol = min(vol_med(bn, d), vol_med(by, d))
            if vol < 5e6:
                continue
            (a, va), (b, vb) = ((bn, 'binance'), (by, 'bybit')) if G > 0 else ((by, 'bybit'), (bn, 'binance'))
            rows = gap_trade(a, b, d, hold, last_day)
            busy = d + hold
            if not rows:
                continue
            c = 2 * (side_cost(vis[va], a, vol, a['pc'][d], cost_mult) + side_cost(vis[vb], b, vol, b['pc'][d],
                                                                                   cost_mult))
            fund, price = sum(r[1] for r in rows), sum(r[2] for r in rows)
            mae = max(abs(b['pc'].get(k, b['pc'][d]) / b['pc'][d] - 1.0) for k, _, _ in rows)
            trades.append({'sym': s, 'decision': d, 'entry': d, 'exit': rows[-1][0], 'days': len(rows),
                           'long': va, 'gap_8h': G, 'vol7': vol, 'sigma': sigma_of(a, d), 'funding': fund,
                           'price': price, 'cost': c, 'gross': fund + price, 'net': fund + price - c,
                           'excess': fund + price - c - SSR_CONST / 365.0 * len(rows), 'open': False,
                           'delist_exit': False, 'rows': rows, 'c_in': c / 2, 'c_out': c / 2,
                           'short_leg_max_move': mae})
    return trades


def gap_persistence(pairs, days, edges=(10, 25, 50, 100, 1e9)):
    """Does a trailing-1-day gap carry into the day after next (the day a lag-1 entry earns first)? Pair-days by |gap|."""
    acc = collections.defaultdict(list)
    for s, (bn, by) in pairs.items():
        for d in range(days[0], days[-1]):
            Fa, Fb = signal(bn, d, 1), signal(by, d, 1)
            if Fa is None or Fb is None or min(vol_med(bn, d), vol_med(by, d)) < 5e6:
                continue
            G = Fb - Fa
            k = d + 1
            ha, hb = bn['fh'].get(k), by['fh'].get(k)
            if not ha or not hb:
                continue
            nxt = (by['fs'][k] * 8.0 / hb - bn['fs'][k] * 8.0 / ha)
            for i in range(len(edges) - 1):
                if edges[i] / 1e4 <= abs(G) < edges[i + 1] / 1e4:
                    acc[i].append((G, nxt))
    out = []
    for i in range(len(edges) - 1):
        xs = acc.get(i, [])
        if xs:
            al = [n * (1 if G > 0 else -1) for G, n in xs]
            out.append({'abs_gap_8h_bp': '[%s, %s)' % (edges[i], edges[i + 1] if edges[i + 1] < 1e8 else 'inf'),
                        'n': len(xs), 'mean_abs_gap_8h': statistics.fmean(abs(G) for G, _ in xs),
                        'next_day_gap_8h_signed_mean': statistics.fmean(al),
                        'next_day_gap_8h_signed_median': statistics.median(al),
                        'next_day_same_sign_share': sum(1 for x in al if x > 0) / len(al),
                        'next_day_received_per_day': statistics.fmean(al) * 3.0})
    return out


def gap_variants():
    return [{'lookback_days': L, 'gap_8h_bp': g, 'hold': h, 'name': 'G_L%d_G%d_H%d' % (L, g, h)}
            for L in GAP_GRID['lookback_days'] for g in GAP_GRID['gap_8h_bp'] for h in GAP_GRID['hold']]


# ---------------------------------------------------------------------------------------------- the live episode

def hourly(out, venue, sym):
    top = Path(out) / 'raw' / 'topup'
    if venue == 'binance':
        r = AF.read_or(top / 'perp_klines_1h' / ('%s.json.gz' % sym), [])
        return sorted((int(x[0]), fnum(x[1]), fnum(x[4])) for x in r) if isinstance(r, list) else []
    r = AF.read_or(top / 'bybit_perp_klines_1h' / ('%s.json.gz' % sym), {})
    return sorted((int(x[0]), fnum(x[1]), fnum(x[4])) for x in (AF.by_list(r) or []))


def mark_now(out, vis, sym, entry_day, P0):
    """A long bought at the close of `entry_day`, marked at the last hourly close: (funding, price, marked at)."""
    h = hourly(out, 'binance', sym)
    t0 = (entry_day + 1) * DAY_MS
    if not h or h[-1][0] < t0:
        return None
    t1 = h[-1][0] + HOUR_MS
    f = sum(-r * (m if m and m > 0 else P0) / P0 for t, r, m in vis['binance']['funding'].get(sym, [])
            if t0 + 60_000 < t <= t1 and r is not None)
    return {'funding': f, 'price': h[-1][2] / P0 - 1.0, 'marked_at': utc(t1)}


def episode(out, vis, entry_iso, names):
    """A long bought at the hourly open of `entry_iso` and marked at the last hourly close (taker both sides), and the
    same long hedged with a Bybit short: funding and price in % of entry notional."""
    t0 = int(dt.datetime.fromisoformat(entry_iso).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    res = []
    for s in names:
        row = {'sym': s}
        legs = {}
        for venue in ('binance', 'bybit'):
            h = [x for x in hourly(out, venue, s) if x[0] >= t0]
            if not h or h[0][0] != t0:
                continue
            P0, P1, t1 = h[0][1], h[-1][2], h[-1][0] + HOUR_MS
            closes = {x[0]: x[2] for x in h}
            ev = [(t, r, m) for t, r, m in vis[venue]['funding'].get(s, []) if t0 < t <= t1 and r is not None]
            f = 0.0
            for t, r, m in ev:
                mk = m if m and m > 0 else closes.get((t // HOUR_MS) * HOUR_MS - HOUR_MS, P0)
                f += -r * mk / P0
            legs[venue] = {'P0': P0, 'P1': P1, 'funding': f, 'price': P1 / P0 - 1.0, 'n_settlements': len(ev),
                           'mean_rate_per_settlement_bp': (statistics.fmean(r for _, r, _ in ev) * 1e4) if ev
                           else None, 'marked_at': utc(t1)}
        if 'binance' not in legs:
            continue
        L = legs['binance']
        c = 2 * (VENUE_FEES_BP['binance']['perp'] + 10.0) / 1e4        # taker + a 10bp half-spread allowance, both sides
        row.update({'long_binance': L, 'long_net': L['funding'] + L['price'] - c, 'cost_assumed': c})
        if 'bybit' in legs:
            Y = legs['bybit']
            cy = c + 2 * (VENUE_FEES_BP['bybit']['perp'] + 10.0) / 1e4
            row.update({'short_bybit': Y, 'hedged_funding': L['funding'] - Y['funding'],
                        'hedged_price': L['price'] - Y['price'],
                        'hedged_net': L['funding'] - Y['funding'] + L['price'] - Y['price'] - cy})
        res.append(row)
    return res


# ---------------------------------------------------------------------------------------------- analyze

def slim(t):
    x = {k: v for k, v in t.items() if k != 'rows'}
    for k in ('decision', 'entry', 'exit'):
        x[k] = dname(x[k])
    return x


def split_stats(ts, cut):
    return {'in_sample': trade_stats([t for t in ts if t['entry'] < cut]),
            'out_of_sample': trade_stats([t for t in ts if t['entry'] >= cut]), 'full': trade_stats(ts)}


def series_summary(ex, c):
    t_f, p_f = B.newey_west_t(ex)
    t_o, p_o = B.newey_west_t(ex[c:])
    t_i, _ = B.newey_west_t(ex[:c])
    pi, po = B.perf(ex[:c], 365), B.perf(ex[c:], 365)
    return {'ann_in': pi.get('ann_return'), 'ann_oos': po.get('ann_return'), 'sharpe_in': pi.get('sharpe'),
            'sharpe_oos': po.get('sharpe'), 't_in': t_i, 't_oos': t_o, 't_full': t_f, 'p_full': p_f,
            'maxdd_oos': po.get('max_drawdown'), 'boot_oos': B.block_bootstrap(ex[c:])}


def by_period(ts):
    acc = collections.defaultdict(list)
    for t in ts:
        d = dname(t['entry'])
        acc[d[:4] + ('H1' if d[5:7] <= '06' else 'H2')].append(t)
    return {k: {'n': len(v), 'mean_net': statistics.fmean(x['net'] for x in v),
                'mean_funding': statistics.fmean(x['funding'] for x in v),
                'mean_price': statistics.fmean(x['price'] for x in v)} for k, v in sorted(acc.items())}


def analyze(out):
    out = Path(out)
    fn = out / 'analysis.json'
    pre = json.loads(fn.read_text()).get('preregistered') if fn.exists() else None
    if not pre or pre.get('grid') != json.loads(json.dumps(GRID)):
        raise SystemExit('run `grid` first (the rule family is fixed before any result)')
    t0 = time.time()
    vis = {v: inputs(out, v) for v in ('binance', 'bybit')}
    bn, rep_bn, last_day = build_perps(vis['binance'])
    by, rep_by, last_by = build_perps(vis['bybit'])
    days = list(range(day_ms(PNL_START) // DAY_MS, last_day + 1))
    cut = day_ms(SPLIT_DAY) // DAY_MS
    c = days.index(cut)
    frac = c / len(days)
    years_in, years_oos = c / 365.0, (len(days) - c) / 365.0
    print('built %d binance / %d bybit perps, %d days, %.0fs' % (len(bn), len(by), len(days), time.time() - t0),
          flush=True)
    V = variants()
    fam_trades, fam_series = {}, {}
    for v in V:
        ts = run_variant(vis['binance'], bn, v, days, last_day)
        fam_trades[v['name']] = ts
        fam_series[v['name']], _ = daily_series(ts, days)
    ctt = B.choose_then_test(fam_series, frac=frac, periods_per_year=365)
    tp = [B.newey_west_t(fam_series[v['name']]) for v in V]
    pv1 = [None if p is None else (p / 2.0 if t > 0 else 1.0 - p / 2.0) for t, p in tp]
    rej1, adj1 = B.bh(pv1)
    family = []
    for v, (t, p), r, a in zip(V, tp, rej1, adj1):
        ts = fam_trades[v['name']]
        ss = series_summary(fam_series[v['name']], c)
        st = split_stats(ts, cut)
        family.append({'name': v['name'], 'n_trades': len(ts), 'trades_oos': st['out_of_sample']['n'],
                       'mean_net_in': st['in_sample'].get('mean_net'), 'mean_net_oos': st['out_of_sample'].get(
                           'mean_net'), 'mean_funding_oos': st['out_of_sample'].get('mean_funding'),
                       'mean_price_oos': st['out_of_sample'].get('mean_price'),
                       'hit_oos': st['out_of_sample'].get('hit_rate'),
                       'median_net_oos': st['out_of_sample'].get('median_net'),
                       'mean_net_oos_ex_top5': st['out_of_sample'].get('mean_net_ex_top5'), **{k: ss[k] for k in
                                                                          ('ann_in', 'ann_oos', 'sharpe_in',
                                                                           'sharpe_oos', 't_oos', 't_full')},
                       'p_one_sided': pv1[V.index(v)], 'bh_adj_one_sided': a, 'bh_positive': r,
                       'usd_per_year_oos_cap': capacity([x for x in ts if x['entry'] >= cut], years_oos)[
                           'usd_per_year']})
    print('family done %.0fs' % (time.time() - t0), flush=True)
    ch = ctt['chosen']
    vch = next(v for v in V if v['name'] == ch)
    ts = fam_trades[ch]
    oos = [t for t in ts if t['entry'] >= cut]
    ins = [t for t in ts if t['entry'] < cut]
    chosen = {'variant': vch, 'series': series_summary(fam_series[ch], c), 'trades': split_stats(ts, cut),
              'by_half_year': by_period(ts),
              'capacity_oos': [capacity(oos, years_oos)] + [capacity(oos, years_oos, s) for s in SIZES],
              'capacity_oos_ex_top5': [capacity(sorted(oos, key=lambda t: t['net'])[:-5], years_oos)] +
              [capacity(sorted(oos, key=lambda t: t['net'])[:-5], years_oos, s) for s in SIZES],
              'capacity_in': [capacity(ins, years_in)] + [capacity(ins, years_in, s) for s in SIZES],
              'top_coins_oos': sorted(({'sym': s, 'n': len(g), 'net_sum': sum(x['net'] for x in g)}
                                       for s, g in ((s, [x for x in oos if x['sym'] == s]) for s in
                                                    {x['sym'] for x in oos})), key=lambda r: r['net_sum'])}
    # robustness of the chosen rule: lag 0 (no late entry), zero costs, double costs, volume floors, every variant at
    # zero cost (does any rule make money before costs?)
    rob = {}
    for name, kw, vv in (('lag0_enter_at_signal', {'lag': 0}, vch), ('zero_cost', {'cost_mult': 0.0}, vch),
                         ('double_cost', {'cost_mult': 2.0}, vch),
                         ('vol_floor_1M', {}, dict(vch, perp_vol_min_usd=1e6)),
                         ('vol_floor_20M', {}, dict(vch, perp_vol_min_usd=2e7))):
        tsr = run_variant(vis['binance'], bn, vv, days, last_day, **kw)
        ser, _ = daily_series(tsr, days)
        rob[name] = {'series': series_summary(ser, c), 'trades': split_stats(tsr, cut)}
    zc = {}
    for v in V:
        tsr = run_variant(vis['binance'], bn, v, days, last_day, cost_mult=0.0)
        ser, _ = daily_series(tsr, days)
        s0 = series_summary(ser, c)
        st0 = split_stats(tsr, cut)
        zc[v['name']] = {'ann_in': s0['ann_in'], 'ann_oos': s0['ann_oos'], 't_full': s0['t_full'],
                         'mean_net_full': st0['full'].get('mean_net'), 'hit_full': st0['full'].get('hit_rate')}
    # the lag-0 version of every variant (what the late-entry rule costs, family-wide)
    lag0 = {}
    for v in V:
        tsr = run_variant(vis['binance'], bn, v, days, last_day, lag=0)
        st0 = split_stats(tsr, cut)
        lag0[v['name']] = {'mean_net_full': st0['full'].get('mean_net'), 'n': st0['full'].get('n')}
    # Bybit as the venue, same family
    days_by = list(range(day_ms(PNL_START) // DAY_MS, last_by + 1))
    c_by = days_by.index(cut)
    by_fam = {}
    for v in V:
        tsr = run_variant(vis['bybit'], by, v, days_by, last_by)
        ser, _ = daily_series(tsr, days_by)
        s0 = series_summary(ser, c_by)
        st0 = split_stats(tsr, cut)
        by_fam[v['name']] = {'n': len(tsr), 'ann_in': s0['ann_in'], 'ann_oos': s0['ann_oos'], 't_oos': s0['t_oos'],
                             'mean_net_in': st0['in_sample'].get('mean_net'),
                             'mean_net_oos': st0['out_of_sample'].get('mean_net')}
    print('robustness done %.0fs' % (time.time() - t0), flush=True)
    buckets = {'L1_H3': bucket_table(vis['binance'], bn, days, last_day, 1, 3),
               'L1_H7': bucket_table(vis['binance'], bn, days, last_day, 1, 7),
               'L3_H7': bucket_table(vis['binance'], bn, days, last_day, 3, 7)}
    # Binance-Bybit gap carry
    pairs = pair_up(bn, by)
    GV = gap_variants()
    g_tr, g_ser = {}, {}
    for v in GV:
        g_tr[v['name']] = run_gap(vis, pairs, v, days, last_day)
        g_ser[v['name']], _ = daily_series(g_tr[v['name']], days)
    g_ctt = B.choose_then_test(g_ser, frac=frac, periods_per_year=365)
    gap = {'pairs': len(pairs), 'persistence': gap_persistence(pairs, days), 'ctt': g_ctt,
           'family': [{'name': v['name'], 'n': len(g_tr[v['name']]), **{k: series_summary(g_ser[v['name']], c)[k]
                                                                         for k in ('ann_in', 'ann_oos', 't_oos')},
                       **{('%s_%s' % (part, k)): split_stats(g_tr[v['name']], cut)[part].get(k)
                          for part in ('in_sample', 'out_of_sample')
                          for k in ('mean_net', 'mean_funding', 'mean_price', 'hit_rate', 'worst')},
                       'usd_per_year_oos_cap': capacity([x for x in g_tr[v['name']] if x['entry'] >= cut],
                                                        years_oos)['usd_per_year'],
                       'max_short_leg_move': max((x['short_leg_max_move'] for x in g_tr[v['name']]), default=None)}
                      for v in GV]}
    print('gap done %.0fs' % (time.time() - t0), flush=True)
    # the live episode: rule trades since the history ended, and a long bought 5 days before the lead
    tman = json.loads((out / 'raw' / 'topup' / 'manifest.json').read_text())
    hist_end = day_ms(vis['binance']['hist_end']['end_exclusive']) // DAY_MS
    recent = {name: [slim(t) for t in fam_trades[name] if t['entry'] >= hist_end - 3] for name in (ch,)}
    lead_ms = tman['end_ms'] - 5 * DAY_MS
    entry_iso = dt.datetime.fromtimestamp((lead_ms // HOUR_MS) * HOUR_MS / 1000, dt.timezone.utc).strftime(
        '%Y-%m-%dT%H:%M')
    names = sorted(set(EPISODE_NAMES) | set(tman.get('episode_names') or []))
    epi = {'entry': entry_iso, 'rows': episode(out, vis, entry_iso, names), 'rule_trades_recent': recent,
           'all_variants_recent': {v['name']: [{'sym': t['sym'], 'entry': dname(t['entry']), 'exit': dname(t['exit']),
                                                'net': t['net'], 'funding': t['funding'], 'price': t['price'],
                                                'open': t['open'], 'now': mark_now(out, vis, t['sym'], t['entry'], t['P0'])
                                                if t['open'] else None} for t in fam_trades[v['name']]
                                               if t['entry'] >= hist_end - 3] for v in V}}
    res = {'preregistered': pre, 'results_written_at': utc(), 'window': {'pnl_start': PNL_START,
                                                                         'last_day': dname(last_day),
                                                                         'split_day': SPLIT_DAY, 'days': len(days),
                                                                         'years_in': years_in,
                                                                         'years_oos': years_oos},
           'build': {'binance': rep_bn, 'bybit': rep_by}, 'choose_then_test': ctt, 'family': family,
           'chosen': chosen, 'robustness': rob, 'zero_cost_family': zc, 'lag0_family': lag0, 'bybit_family': by_fam,
           'buckets': buckets, 'gap': gap, 'episode': epi, 'topup': {k: tman.get(k) for k in ('started', 'finished',
                                                                                            'episode_names', 'http')}}
    write_json(fn, res)
    write_gz(out / 'trades.json.gz', {'chosen': [slim(t) for t in ts],
                                      'gap_chosen': [slim(t) for t in g_tr[g_ctt['chosen']]]})
    (out / 'tables.md').write_text(render(res))
    print('analysis written %.0fs' % (time.time() - t0), flush=True)
    return res


# ---------------------------------------------------------------------------------------------- render

def pc(x, d=2):
    return '—' if x is None else ('%+.*f%%' % (d, 100 * x))


def num(x, d=2):
    return '—' if x is None else ('%.*f' % (d, x))


def usd(x):
    if x is None:
        return '—'
    a = abs(x)
    s = '-' if x < 0 else ''
    return s + ('$%.2fM' % (a / 1e6) if a >= 1e6 else '$%.0fk' % (a / 1e3) if a >= 1e3 else '$%.0f' % a)


def render(R):
    L = ['# neg_funding_long — tables (%s)' % R['results_written_at'], '']
    w = R['window']
    L.append('Window %s → %s (%d days), split %s: %.2f years in sample, %.2f out of sample.' % (
        w['pnl_start'], w['last_day'], w['days'], w['split_day'], w['years_in'], w['years_oos']))
    L += ['', '## Family (Binance, lag-1 entry, taker costs; per-trade net in % of notional; portfolio = equal weight '
              'over open trades)', '',
          '| variant | trades | OOS trades | net/trade in | net/trade OOS | median OOS | OOS ex best 5 | funding OOS | '
          'price OOS | hit OOS | ann in | ann OOS | t OOS | t full | BH+ | $/yr OOS at cap |', '|' + '---|' * 16]
    for f in R['family']:
        L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            f['name'], f['n_trades'], f['trades_oos'], pc(f['mean_net_in']), pc(f['mean_net_oos']),
            pc(f['median_net_oos']), pc(f['mean_net_oos_ex_top5']), pc(f['mean_funding_oos']), pc(f['mean_price_oos']), pc(f['hit_oos'], 0), pc(f['ann_in'], 0),
            pc(f['ann_oos'], 0), num(f['t_oos']), num(f['t_full']), 'yes' if f['bh_positive'] else 'no',
            usd(f['usd_per_year_oos_cap'])))
    ct = R['choose_then_test']
    L += ['', 'choose_then_test: chosen **%s**, in-sample positive %s, OOS rank %d/%d, OOS HAC t %s, deflated Sharpe '
              '(in) %s; one-sided BH survivors: %s' % (ct['chosen'], ct['in_sample_positive'], ct['oos_rank'],
                                                      ct['n_variants'], num(ct['oos_t']),
                                                      num(ct['deflated_sharpe_in_sample']),
                                                      ', '.join(ct['bh_survivors_positive']) or 'none'), '']
    ch = R['chosen']
    L += ['## Chosen variant: trades', '', '| part | n | coins | mean net | median | hit | p10 | worst | best | '
          'funding | price | cost | zero-cost mean | price eats funding | delist exits | mean days | ex best 5 | best-5 '
          'share of sum |', '|' + '---|' * 18]
    for part in ('in_sample', 'out_of_sample', 'full'):
        s = ch['trades'][part]
        if not s.get('n'):
            continue
        L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %d | %.1f | %s | %s |' % (
            part, s['n'], s['coins'], pc(s['mean_net']), pc(s['median_net']), pc(s['hit_rate'], 0), pc(s['p10']),
            pc(s['worst'], 0), pc(s['best'], 0), pc(s['mean_funding']), pc(s['mean_price']), pc(s['mean_cost']),
            pc(s['mean_gross_zero_cost']), pc(s['share_price_eats_funding'], 0), s['delist_exits'], s['mean_days'],
            pc(s['mean_net_ex_top5']), pc(s['top5_share_of_sum'], 0)))
    L += ['', '| by half-year | n | mean net | funding | price |', '|---|---|---|---|---|']
    for k, s in ch['by_half_year'].items():
        L.append('| %s | %d | %s | %s | %s |' % (k, s['n'], pc(s['mean_net']), pc(s['mean_funding']),
                                                 pc(s['mean_price'])))
    L += ['', '| capacity (OOS) | $/yr | avg open capital | peak open | return on avg capital |', '|---|---|---|---|---|']
    for cp in ch['capacity_oos'] + [dict(c, size_per_trade='ex best 5: ' + (c['size_per_trade'] if isinstance(
            c['size_per_trade'], str) else usd(c['size_per_trade']))) for c in ch['capacity_oos_ex_top5']]:
        L.append('| %s | %s | %s | %s | %s |' % (cp['size_per_trade'] if isinstance(cp['size_per_trade'], str)
                                                 else usd(cp['size_per_trade']), usd(cp['usd_per_year']),
                                                 usd(cp['avg_open_capital']), usd(cp['peak_open_capital']),
                                                 pc(cp['return_on_avg_capital'], 1)))
    L += ['', '## Robustness of the chosen rule', '', '| row | n | net/trade OOS | net/trade full | ann OOS | t OOS |',
          '|---|---|---|---|---|---|']
    for k, r in R['robustness'].items():
        L.append('| %s | %d | %s | %s | %s | %s |' % (k, r['trades']['full'].get('n', 0),
                                                      pc(r['trades']['out_of_sample'].get('mean_net')),
                                                      pc(r['trades']['full'].get('mean_net')),
                                                      pc(r['series']['ann_oos'], 0), num(r['series']['t_oos'])))
    L += ['', '## Every variant at zero cost, lag 0, and on Bybit', '',
          '| variant | zero-cost net/trade | zero-cost hit | zero-cost ann OOS | lag-0 net/trade | Bybit n | Bybit '
          'net/trade in | Bybit net/trade OOS | Bybit t OOS |', '|' + '---|' * 9]
    for f in R['family']:
        z, l0, b = R['zero_cost_family'][f['name']], R['lag0_family'][f['name']], R['bybit_family'][f['name']]
        L.append('| %s | %s | %s | %s | %s | %d | %s | %s | %s |' % (
            f['name'], pc(z['mean_net_full']), pc(z['hit_full'], 0), pc(z['ann_oos'], 0), pc(l0['mean_net_full']),
            b['n'], pc(b['mean_net_in']), pc(b['mean_net_oos']), num(b['t_oos'])))
    for k, rows in R['buckets'].items():
        L += ['', '## Every coin-day by signal (%s, lag-1 entry, zero cost, perp volume >= $5M)' % k, '',
              '| signal bp/8h | n | funding | price mean | price median | total mean | total median | hit |',
              '|---|---|---|---|---|---|---|---|']
        for r in rows:
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (
                r['signal_8h_bp'], r['n'], pc(r['mean_funding']), pc(r['mean_price']), pc(r['median_price']),
                pc(r['mean_total']), pc(r['median_total']), pc(r['hit_total'], 0)))
    g = R['gap']
    L += ['', '## Binance-Bybit funding gap (%d same-coin pairs)' % g['pairs'], '',
          '| |gap| bp/8h | n | mean |gap| | next-day gap (signed) mean | median | same sign | received/day |',
          '|---|---|---|---|---|---|---|']
    for r in g['persistence']:
        L.append('| %s | %d | %s | %s | %s | %s | %s |' % (
            r['abs_gap_8h_bp'], r['n'], pc(r['mean_abs_gap_8h'], 3), pc(r['next_day_gap_8h_signed_mean'], 3),
            pc(r['next_day_gap_8h_signed_median'], 3), pc(r['next_day_same_sign_share'], 0),
            pc(r['next_day_received_per_day'], 3)))
    L += ['', '| variant | n | net/trade in | net/trade OOS | funding OOS | price OOS | hit OOS | worst OOS | ann OOS | '
              't OOS | $/yr OOS at cap | max short-leg move |', '|' + '---|' * 12]
    for f in g['family']:
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            f['name'], f['n'], pc(f['in_sample_mean_net']), pc(f['out_of_sample_mean_net']),
            pc(f['out_of_sample_mean_funding']), pc(f['out_of_sample_mean_price']),
            pc(f['out_of_sample_hit_rate'], 0), pc(f['out_of_sample_worst'], 0), pc(f['ann_oos'], 0),
            num(f['t_oos']), usd(f['usd_per_year_oos_cap']), pc(f['max_short_leg_move'], 0)))
    gc = g['ctt']
    L += ['', 'gap choose_then_test: chosen **%s**, in-sample positive %s, OOS t %s, OOS rank %d/%d, one-sided BH: %s'
          % (gc['chosen'], gc['in_sample_positive'], num(gc['oos_t']), gc['oos_rank'], gc['n_variants'],
             ', '.join(gc['bh_survivors_positive']) or 'none')]
    e = R['episode']
    L += ['', '## The live episode: long bought at %s UTC, marked at the last hourly close' % e['entry'], '',
          '| perp | settlements | mean rate bp | funding | price | long net | Bybit funding (long) | hedged funding | '
          'hedged price | hedged net |', '|' + '---|' * 10]
    for r in e['rows']:
        lb, sb = r['long_binance'], r.get('short_bybit') or {}
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['sym'], lb['n_settlements'], num(lb['mean_rate_per_settlement_bp'], 1), pc(lb['funding']),
            pc(lb['price']), pc(r['long_net']), pc(sb.get('funding')), pc(r.get('hedged_funding')),
            pc(r.get('hedged_price')), pc(r.get('hedged_net'))))
    for name, ts in e['rule_trades_recent'].items():
        L += ['', 'Rule trades of %s entered since the history ended (marked at %s close if open):' % (name, w['last_day']),
              '', '| perp | decision | entry close | exit | days | signal bp/8h | funding | price | net | open |',
              '|---|---|---|---|---|---|---|---|---|---|']
        for t in ts:
            L.append('| %s | %s | %s | %s | %d | %.0f | %s | %s | %s | %s |' % (
                t['sym'], t['decision'], t['entry'], t['exit'], t['days'], t['signal_8h'] * 1e4, pc(t['funding']),
                pc(t['price']), pc(t['net']), t['open']))
    L += ['', 'Every variant\'s trades in the episode names since the history ended (open ones marked to the last hourly '
              'close as well):', '', '| variant | perp | entry close | exit | net at %s close | open | funding now | '
              'price now | net now (before exit cost) |' % w['last_day'], '|---|---|---|---|---|---|---|---|---|']
    epi_names = {r['sym'] for r in e['rows']}
    for v, ts in e['all_variants_recent'].items():
        for t in (x for x in ts if x['sym'] in epi_names):
            n = t.get('now') or {}
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                v, t['sym'], t['entry'], t['exit'], pc(t['net']), t['open'], pc(n.get('funding')), pc(n.get('price')),
                pc(n['funding'] + n['price'] - 0.0015) if n else '—'))
    return '\n'.join(L) + '\n'


def cmd_grid(args):
    fn = Path(args.out) / 'analysis.json'
    if fn.exists() and json.loads(fn.read_text()).get('results_written_at'):
        raise SystemExit('analysis.json already holds results; the grid is fixed')
    write_json(fn, {'preregistered': preregistration()})
    print('grid written:', fn, len(variants()), 'variants')


def cmd_analyze(args):
    R = analyze(args.out)
    ct = R['choose_then_test']
    print(json.dumps({'chosen': ct['chosen'], 'in_sample_positive': ct['in_sample_positive'], 'oos_t': ct['oos_t'],
                      'bh_positive': ct['bh_survivors_positive'],
                      'oos_trades': R['chosen']['trades']['out_of_sample']}, indent=1, default=str))


def cmd_collect(args):
    log = collect(args.out)
    print(json.dumps({k: log.get(k) for k in ('episode_names', 'bybit_symbols', 'http', 'finished')}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name, fn in (('collect', cmd_collect), ('grid', cmd_grid), ('analyze', cmd_analyze)):
        p = sub.add_parser(name)
        p.add_argument('--out', default=str(OUT))
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
