#!/usr/bin/env python3
"""Do Polymarket wallets have persistent skill, and can a follower who copies them an hour late earn it?

Why. The repo's frame is that alpha is a rent paid by a counterparty with a non-price motive. On a prediction market
the obvious candidates are the informed wallets themselves: insiders, specialists and modellers trading against fans
and partisans. If some wallets keep predicting outcomes, and if their trades move prices slowly, a patient follower
who copies them an hour late (no racing, no block position) keeps part of the edge. The late-entry test is the whole
question: everything is priced at the market an hour (or a day) after the wallet traded.

Data (all public, no keys):
  * the resolved universe from research/2026-10-09/polymarket_history (gamma keyset, 446,503 markets >= $10k);
  * taker trades with wallets from data-api /trades?market=<conditionId> (takerOnly is the default: one row per taker
    transaction; `limit` <= 10,000; `offset` <= 10,000; `start`/`end` unix-second windows work; `filterType=CASH,
    filterAmount=X` keeps trades of at least $X), paged backwards in time by `end`;
  * hourly midpoints from CLOB /prices-history in windows of <= 14.5 days (longer windows are rejected);
  * one live read of the CLOB books of active binary markets, for the half-spread and the depth at the touch across
    the whole price range (the 2026-10-09 table only covers the favourite bands >= 0.85).

PRE-REGISTRATION (written 2026-10-14 ~07:50 UTC, before any trade, price or return of this study was fetched):
  sample      binary markets of the stored universe, not crypto up/down, $50k-$5M volume, scheduled endDate in
              [2025-10-01, 2026-10-01) (scheduled, not actual, so early YES resolutions of later markets do not leak
              in), life (close - start) >= 2 days; stratified by category x volume bucket, drawn by a hash of the id,
              processed in hash order so any prefix is a random subsample; weights = stratum count / collected.
  trades      taker trades of at least $50 (CASH filter), from 2025-07-01 to the close, at most 30,000 per market
              (newest first; the market is flagged truncated if the cap binds).
  formation   cutoff 2026-05-01: formation = trades in markets that closed before it; test = trades made at or
              after it.
  skill       every taker trade is a purchase: BUY of outcome o at p buys o at p; SELL of o at p buys 1-o at 1-p.
              Edge per $ = sum(shares x (payout - price)) / sum(shares x price), size-weighted; markout per $ at +1h
              and +1d is the same with the midpoint then in place of the payout (the payout once the market closed).
              t-statistics are clustered by market (ratio estimator, linearised). A wallet is ranked when it has at
              least 10 trades in at least 5 markets.
  persistence Spearman of formation vs test edge per $ (and t), wallets ranked in both; top-k (k = 10, 50, 100,
              250) by formation t: their test-period edge per $ with a market-clustered interval.
  follower    signal = a buy episode (a wallet's taker BUYs of one outcome, merged while each follows the last by
              under an hour), at least min_size dollars. Entry at the first hourly mark at least `delay` after the
              signal (+1h is the test; +1d and +5m are reported), at the midpoint then + the live half-spread for the
              category and price band + the taker fee; hold to resolution, or exit when the wallet sells (a taker SELL
              of the same outcome), at the first hourly mark at least `delay` after its sale, at mid - half-spread -
              fee. Equal dollars per signal. Selection is walk-forward: on the 1st of each month from 2026-05-01, using
              markets closed before that date only.
  grid (72)   score {edge t, +1d markout t} x selection {t>=2 top 20, t>=2 top 100, t>=1 top 300} x category {all,
              sports, non-sports} x min_size {$50, $1,000} x exit {hold, wallet exit}; delay +1h.
  protocol    daily P&L (on the close/exit day) over average deployed capital, minus SSR/365, from 2026-05-01 to the
              last close; backtest.choose_then_test with the split at the series midpoint. Go needs: in-sample
              positive, out-of-sample HAC t >= 2, the chosen variant among bh_survivors_positive, and excess over SSR
              at the stated capacity after all costs.
  stage 2     (added after a dry run of the analysis on the first 805 markets, so disclosed and secondary): the full
              taker histories (>= $50, from 2025-07-01, <= 30,000 rows newest first) of the 2,500 wallets with the most
              formation-period taker dollars in the sample; a 'hist' score = edge t over every universe market of the
              wallet closed before the selection date; 36 more variants, reported alone and pooled with the 72; the go
              rule is judged on the pre-registered 72.

    uv run python scripts/pm_wallet_skill.py sample   --out research/2026-10-14/pm_wallet_skill
    uv run python scripts/pm_wallet_skill.py collect  --out research/2026-10-14/pm_wallet_skill
    uv run python scripts/pm_wallet_skill.py books    --out research/2026-10-14/pm_wallet_skill
    uv run python scripts/pm_wallet_skill.py wallets  --out research/2026-10-14/pm_wallet_skill   (stage 2, below)
    uv run python scripts/pm_wallet_skill.py analyze  --out research/2026-10-14/pm_wallet_skill
    uv run python scripts/pm_wallet_skill.py render   --out research/2026-10-14/pm_wallet_skill
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import json
import math
import statistics
import sys
import threading
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
import polymarket_history as P  # noqa: E402
from polymarket_history import (Http, categorize, fee_rate, parse_ts, write_gz, read_gz,  # noqa: E402,F401
                                update_manifest, price_path, fetch_prices)

SRC = ROOT / 'research' / '2026-10-09' / 'polymarket_history'
DAY, HOUR = P.DAY, P.HOUR
SSR = 0.038
DATA, CLOB, GAMMA = P.DATA, P.CLOB, P.GAMMA

WIN_LO = '2025-10-01T00:00:00+00:00'     # scheduled endDate window of the sample
WIN_HI = '2026-10-01T00:00:00+00:00'
TRADES_FROM = '2025-07-01T00:00:00+00:00'
CUTOFF = '2026-05-01T00:00:00+00:00'     # formation: markets closed before; test: trades at or after
MONTHS = ['2026-05-01', '2026-06-01', '2026-07-01', '2026-08-01', '2026-09-01']
VOL_LO, VOL_HI = 5e4, 5e6
MIN_LIFE_DAYS = 2.0
MIN_CASH = 50
PAGE = 10000
MAX_PAGES = 3
MIN_TRADES, MIN_MARKETS = 10, 5
TOPK = [10, 50, 100, 250]
CAT_TARGETS = {'sports': 1400, 'politics': 700, 'crypto_price': 350, 'science_tech': 300, 'culture': 300,
               'economics': 300, 'elections': 300, 'other': 10 ** 6}
VB_SHARE = {'1m-5m': 0.35, '100k-1m': 0.45, '50k-100k': 0.20}

SCORES = ['edge', 'mk1d']
SELECTIONS = {'t2_top20': (2.0, 20), 't2_top100': (2.0, 100), 't1_top300': (1.0, 300)}
CATS = ['all', 'sports', 'nonsports']
MIN_SIZES = [50, 1000]
EXITS = ['hold', 'wexit']
DELAYS = {'5m': 300, '1h': HOUR, '1d': DAY}


# ------------------------------------------------------------------------------------------------ pure functions

def vb3(v):
    v = v or 0.0
    if v >= 1e6:
        return '1m-5m'
    if v >= 1e5:
        return '100k-1m'
    return '50k-100k'


def as_purchase(side, outcome, price, size):
    """A taker trade as a purchase: (outcome bought, price per share, shares). BUY of outcome o at p buys o at p; SELL
    of o at p is economically a purchase of the complement 1-o at 1-p (the shares sold pay 1 if o wins; the seller's
    position changes by exactly what buying 1-o at 1-p would do)."""
    if side == 'BUY':
        return outcome, price, size
    return 1 - outcome, 1.0 - price, size


def payout_of(outcome, payout0):
    """Payout of one share of `outcome` (0 or 1) given outcome 0's payout (1, 0, or 0.5 on a 50-50 resolution)."""
    return payout0 if outcome == 0 else 1.0 - payout0


def trade_edge(outcome, q, shares, payout0):
    """(dollar edge, dollars at risk) of a purchase of `outcome` at q: shares x (payout - q), shares x q."""
    return shares * (payout_of(outcome, payout0) - q), shares * q


def mid_of(outcome, mid0):
    return mid0 if outcome == 0 else 1.0 - mid0


def ratio_t(per_market):
    """Market-clustered ratio estimator: per_market is a list of (edge_m, capital_m) or (edge_m, capital_m, v_m).
    Returns (R = sum e / sum c, its t-statistic, number of clusters). The variance is the linearised (delta-method)
    cluster variance n/(n-1) sum (e_m - R c_m)^2 / (sum c)^2, floored, when v_m is given, at sum v_m / (sum c)^2: the
    variance of the edge if every market were fairly priced (fix 2026-10-14: without the floor a wallet that wins
    every one of its markets at similar prices has zero residuals and an infinite t, and such wallets topped the
    ranking)."""
    n = len(per_market)
    E = sum(x[0] for x in per_market)
    C = sum(x[1] for x in per_market)
    if n == 0 or C <= 0:
        return None, None, n
    R = E / C
    if n < 2:
        return R, None, n
    v = n / (n - 1.0) * sum((x[0] - R * x[1]) ** 2 for x in per_market) / (C * C)
    if len(per_market[0]) > 2:
        v = max(v, sum(x[2] for x in per_market) / (C * C))
    if v <= 0:
        return R, None, n
    return R, R / math.sqrt(v), n


def null_var(net0, s_p0, s_sh, capital):
    """Variance of a market's edge under fair pricing: p(1-p) x (net shares of outcome 0)^2, p the share-weighted
    price of outcome 0 the trades paid; floored at (1% of the capital)^2 so that a round trip with no outcome risk
    still counts as uncertain."""
    p = (s_p0 / s_sh) if s_sh > 0 else 0.5
    p = min(0.999, max(0.001, p))
    return max(p * (1.0 - p) * net0 * net0, (0.01 * capital) ** 2)


def spearman(x, y):
    """Spearman rank correlation with average ranks for ties."""
    n = len(x)
    if n < 3:
        return None

    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def buy_episodes(buys, gap=HOUR):
    """Merge one market's taker BUYs into episodes. `buys` is a list of dicts with ts, wallet, outcome, price, size.
    A wallet's buys of one outcome form one episode while each follows the previous by less than `gap` seconds.
    Returns episodes with the first trade's time, the total shares and dollars, and the VWAP."""
    by = collections.defaultdict(list)
    for b in sorted(buys, key=lambda x: x['ts']):
        by[(b['wallet'], b['outcome'])].append(b)
    eps = []
    for (w, o), xs in by.items():
        cur = None
        for b in xs:
            if cur is not None and b['ts'] - cur['last_ts'] < gap:
                cur['shares'] += b['size']
                cur['usd'] += b['size'] * b['price']
                cur['last_ts'] = b['ts']
                cur['n'] += 1
            else:
                if cur is not None:
                    eps.append(cur)
                cur = {'wallet': w, 'outcome': o, 'ts': b['ts'], 'last_ts': b['ts'], 'shares': b['size'],
                       'usd': b['size'] * b['price'], 'n': 1}
        if cur is not None:
            eps.append(cur)
    for e in eps:
        e['vwap'] = e['usd'] / e['shares'] if e['shares'] > 0 else None
    eps.sort(key=lambda e: (e['ts'], e['wallet']))
    return eps


def entry_cost(mid_o, half_spread, rate, cap=0.999):
    """Per-share cost of a taker buy at the midpoint plus the half-spread, with the taker fee rate x p x (1-p)."""
    ask = min(cap, max(0.001, mid_o + half_spread))
    return ask + rate * ask * (1.0 - ask), ask


def exit_proceeds(mid_o, half_spread, rate, floor=0.001):
    """Per-share proceeds of a taker sell at the midpoint minus the half-spread, net of the taker fee."""
    bid = max(floor, min(0.999, mid_o - half_spread))
    return bid - rate * bid * (1.0 - bid), bid


def follower_return(mid_in, payout_o, hs_in, rate, mid_out=None, hs_out=None):
    """Return per dollar of the follower's position: buy at mid_in + hs_in + fee; either hold to the payout or, if
    mid_out is given, sell at mid_out - hs_out - fee."""
    cost, _ = entry_cost(mid_in, hs_in, rate)
    if mid_out is None:
        return payout_o / cost - 1.0
    proceeds, _ = exit_proceeds(mid_out, hs_out if hs_out is not None else hs_in, rate)
    return proceeds / cost - 1.0


def ceil_hour(t):
    return float(math.ceil(t / HOUR) * HOUR)


def mid_at(sx, sp, t, max_stale=3 * DAY):
    """Midpoint of outcome 0 at time t from an hourly series split into sorted times `sx` and prices `sp`: the last
    point at or before t (points are emitted only when the price moves), None if there is none within max_stale."""
    i = bisect.bisect_right(sx, t) - 1
    if i < 0 or t - sx[i] > max_stale:
        return None
    return sp[i]


MARK_TOL = 300.0   # prices-history hourly points are stamped seconds after the boundary (e.g. 02:00:11)


def mark_mid(sx, sp, T):
    """Midpoint at the hourly mark T: the last point stamped at or before T + MARK_TOL. Fix 2026-10-14: reading the
    last point at or before T itself returned the previous hour's point (stamped hh:00:11), so a '+1h' entry used a
    price from 0-60 minutes after the signal, in the follower's favour."""
    return mid_at(sx, sp, T + MARK_TOL)


def entry_time(t_signal, delay):
    """The follower acts at the first hourly mark at least `delay` after the signal (so +1h means 1-2 hours)."""
    return ceil_hour(t_signal + delay)


def daily_pnl_series(rows, d_lo, d_hi, ssr=SSR):
    """rows: dicts with t_in, t_out (seconds), stake (dollars), ret (per dollar). P&L lands on the exit/close day,
    capital is the stake open each day. Returns (excess daily return series on average capital, avg capital,
    capital-days, total pnl)."""
    n = d_hi - d_lo + 1
    pnl = [0.0] * n
    cap = [0.0] * n
    for r in rows:
        a = int(r['t_in'] // DAY) - d_lo
        b = int(r['t_out'] // DAY) - d_lo
        a, b = max(0, a), min(n - 1, b)
        if 0 <= b < n:
            pnl[b] += r['stake'] * r['ret']
        for d in range(a, b + 1):
            cap[d] += r['stake']
    k = sum(cap) / n if n else 0.0
    if k <= 0:
        return [0.0] * n, 0.0, 0.0, 0.0
    return [x / k - ssr / 365.0 for x in pnl], k, sum(cap), sum(pnl)


# ------------------------------------------------------------------------------------------------ sample

def life_days(m):
    st, cl = P.start_ts(m), parse_ts(m.get('closedTime'))
    if st is None or cl is None:
        return None
    return (cl - st) / DAY


def eligible(m):
    if not P.eligible_binary(m) or m.get('cat') == 'crypto_updown':
        return False
    v = m.get('volumeNum') or 0.0
    if not (VOL_LO <= v <= VOL_HI):
        return False
    end = parse_ts(m.get('endDate'))
    if end is None or not (parse_ts(WIN_LO) <= end < parse_ts(WIN_HI)):
        return False
    L = life_days(m)
    return L is not None and L >= MIN_LIFE_DAYS


def cmd_sample(args):
    out = Path(args.out)
    uni = read_gz(SRC / 'raw' / 'universe.json.gz')
    el = [m for m in uni if eligible(m)]
    counts = collections.Counter((m['cat'], vb3(m['volumeNum'])) for m in el)
    plan = {}
    for (cat, vb), n in counts.items():
        tgt = CAT_TARGETS.get(cat, 300) * VB_SHARE[vb]
        plan['%s|%s' % (cat, vb)] = {'count': n, 'target': tgt, 'prob': min(1.0, tgt / n)}
    rows = []
    for m in el:
        key = '%s|%s' % (m['cat'], vb3(m['volumeNum']))
        u = P.stable_u('pm-wallet-skill:' + str(m['id']))
        if u < plan[key]['prob']:
            rows.append({'id': m['id'], 'u': u, 'stratum': key})
    rows.sort(key=lambda r: r['u'])
    by_id = {m['id']: m for m in el}
    keep = []
    for r in rows:
        m = by_id[r['id']]
        keep.append({'id': m['id'], 'conditionId': m['conditionId'], 'clobTokenIds': m['clobTokenIds'],
                     'question': m.get('question'), 'cat': m['cat'], 'tags': m.get('tags'),
                     'volumeNum': m.get('volumeNum'), 'start': P.start_ts(m), 'end': parse_ts(m['endDate']),
                     'close': parse_ts(m['closedTime']), 'payout0': P.binary_payout(m), 'negRisk': m.get('negRisk'),
                     'event_id': m.get('event_id'), 'event_title': m.get('event_title'),
                     'gameStartTime': m.get('gameStartTime'), 'stratum': r['stratum'], 'u': r['u']})
    P.write_json(out / 'sample.json', {'generated': P.utc(), 'eligible': len(el), 'plan': plan, 'markets': keep})
    print(json.dumps({'universe': len(uni), 'eligible': len(el), 'sample': len(keep),
                      'by_cat': collections.Counter(k['cat'] for k in keep).most_common()}))
    return 0


# ------------------------------------------------------------------------------------------------ collect

def compact_trade(x, tokens):
    """[ts, wallet, side (1 BUY, 0 SELL), outcome index, shares, price]; the outcome index is checked against the
    market's token list and set to -1 when the asset does not match it (such rows are dropped in analysis)."""
    oi = x.get('outcomeIndex')
    oi = int(oi) if oi is not None else -1
    if oi not in (0, 1) or tokens[oi] != x.get('asset'):
        oi = -1
    return [int(x.get('timestamp') or 0), (x.get('proxyWallet') or '').lower(), 1 if x.get('side') == 'BUY' else 0,
            oi, P.fnum(x.get('size'), 0.0), P.fnum(x.get('price'), 0.0)]


def fetch_market_trades(http, m, t_from):
    """Taker trades >= MIN_CASH for one market, newest first, paging backwards by `end` (offset is capped at 10,000).
    Returns (rows, truncated, pages, error)."""
    rows, seen = [], set()
    end = int(m['close'] + HOUR)
    start = int(max(t_from, (m['start'] or t_from) - DAY))
    trunc, err, pages = False, None, 0
    for page in range(MAX_PAGES):
        q = {'market': m['conditionId'], 'limit': PAGE, 'takerOnly': 'true', 'filterType': 'CASH',
             'filterAmount': MIN_CASH, 'start': start, 'end': end}
        d = http.request(DATA + '/trades?' + urllib.parse.urlencode(q))
        pages += 1
        if not isinstance(d, list):
            err = d.get('__error__') if isinstance(d, dict) else 'not a list'
            break
        new = 0
        for x in d:
            c = compact_trade(x, m['clobTokenIds'])
            key = ((x.get('transactionHash') or ''), c[1], x.get('asset'), c[2])
            if key in seen:
                continue
            seen.add(key)
            rows.append(c)
            new += 1
        if len(d) < PAGE:
            break
        if page == MAX_PAGES - 1:
            trunc = True
            break
        end = min(int(x.get('timestamp') or end) for x in d)
        if new == 0:
            trunc = True
            break
    return rows, trunc, pages, err


def price_windows(m, t_from):
    a = max(t_from, (m['start'] or t_from)) - HOUR
    b = m['close'] + HOUR
    w = []
    s = a
    while s < b:
        e = min(b, s + 14.5 * DAY)
        w.append((s, e))
        s = e
    return w


def cmd_collect(args):
    out = Path(args.out)
    smp = json.loads((out / 'sample.json').read_text())['markets']
    if args.limit:
        smp = smp[:args.limit]
    t_from = parse_ts(TRADES_FROM)
    raw = out / 'raw'
    h_tr = Http(interval=args.interval, timeout=90)
    h_px = Http(interval=args.interval)
    t0 = time.time()
    lock = threading.Lock()
    stat = collections.Counter()
    errs = []

    def one_trades(m):
        p = raw / 'trades' / str(m['id'])[-2:] / ('%s.json.gz' % m['id'])
        if p.exists():
            return
        rows, trunc, pages, err = fetch_market_trades(h_tr, m, t_from)
        if err and not rows:
            with lock:
                errs.append({'id': m['id'], 'kind': 'trades', 'err': err[:200]})
            return
        write_gz(p, {'id': m['id'], 'fetched_at': P.utc(), 'truncated': trunc, 'pages': pages, 'error': err,
                     'min_cash': MIN_CASH, 'rows': rows})
        with lock:
            stat['trade_markets'] += 1
            stat['trade_rows'] += len(rows)
            stat['truncated'] += int(trunc)

    def one_prices(m):
        p = raw / 'prices' / str(m['id'])[-2:] / ('%s_h.json.gz' % m['id'])
        if p.exists():
            return
        ser, err = [], None
        for a, b in price_windows(m, t_from):
            s, e = fetch_prices(h_px, m['clobTokenIds'][0], coarse=False, start=a, end=b, fidelity=60)
            if s is None:
                err = e
                continue
            ser.extend(s)
        if err and not ser:
            with lock:
                errs.append({'id': m['id'], 'kind': 'prices', 'err': str(err)[:200]})
            return
        ser = sorted({tuple(x) for x in ser})
        write_gz(p, {'id': m['id'], 'fetched_at': P.utc(), 'error': err, 'series': [list(x) for x in ser]})
        with lock:
            stat['price_markets'] += 1
            stat['price_points'] += len(ser)

    def run(fn, items, workers, label):
        done = 0
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for _ in ex.map(fn, items):
                done += 1
                if done % 200 == 0:
                    with lock:
                        print(json.dumps({'kind': label, 'done': done, 'of': len(items), **stat,
                                          'errors': len(errs), 'elapsed_s': round(time.time() - t0),
                                          'trades_http': h_tr.stats(), 'prices_http': h_px.stats()}), flush=True)

    th = threading.Thread(target=run, args=(one_prices, smp, args.price_workers, 'prices'))
    th.start()
    run(one_trades, smp, args.workers, 'trades')
    th.join()
    man = {'finished_at': P.utc(), 'started_at': P.utc(t0), 'markets': len(smp), **stat, 'errors': len(errs),
           'error_examples': errs[:20], 'trades_http': h_tr.stats(), 'prices_http': h_px.stats(),
           'seconds': round(time.time() - t0, 1),
           'sources': {'trades': DATA + '/trades?market=<conditionId>&takerOnly=true&filterType=CASH&filterAmount=%d'
                                 '&limit=%d (paged back by end, max %d pages)' % (MIN_CASH, PAGE, MAX_PAGES),
                       'prices': CLOB + '/prices-history?market=<token0>&startTs&endTs&fidelity=60 (14.5-day windows)'}}
    prev = {}
    mp = out / 'manifest.json'
    if mp.exists():
        prev = json.loads(mp.read_text()).get('collect_runs', [])
    update_manifest(out, 'collect_runs', (prev if isinstance(prev, list) else []) + [man])
    print(json.dumps(man))
    return 0


# ------------------------------------------------------------------------------------------------ event completion
# Coordinator note (2026-10-14 ~08:00 UTC, acted on after the collection above): selecting markets by lifetime volume
# over-represents the winners of multi-outcome events (volume flows to the eventual winner), so buyers of the sampled
# members look skilled. Measured here: sampled neg-risk members resolved YES 24.0% against a mid-life mean price of
# 20.7%. The fix is event-level sampling: every member of each sampled event is included whatever its volume, and the
# event is weighted by 1 / P(any of its members was drawn).

def cmd_events(args):
    out = Path(args.out)
    S = json.loads((out / 'sample.json').read_text())
    evs = sorted({str(m['event_id']) for m in S['markets'] if m.get('event_id')})
    http = Http(interval=args.interval)
    t0 = time.time()
    lock = threading.Lock()
    stat = collections.Counter()

    def one(e):
        p = out / 'raw' / 'events' / e[-2:] / ('%s.json.gz' % e)
        if p.exists():
            return
        d = http.request(GAMMA + '/events/' + e)
        if not isinstance(d, dict) or 'markets' not in d:
            with lock:
                stat['errors'] += 1
            return
        ms = []
        for m in d.get('markets') or []:
            cm = P.compact_market(m)
            cm['event_id'] = e
            ms.append(cm)
        write_gz(p, {'id': e, 'title': d.get('title'), 'negRisk': d.get('negRisk'), 'fetched_at': P.utc(),
                     'tags': [t.get('label') for t in d.get('tags') or [] if isinstance(t, dict)], 'markets': ms})
        with lock:
            stat['events'] += 1
            stat['members'] += len(ms)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(one, evs))
    update_manifest(out, 'events', {'finished_at': P.utc(), 'started_at': P.utc(t0), 'events': len(evs), **stat,
                                    'http': http.stats(), 'source': GAMMA + '/events/<id>'})
    print(json.dumps({'events': len(evs), **stat, **http.stats()}))
    return 0


def event_inclusion_prob(member_probs):
    """Probability that an event enters the sample: at least one of its members was drawn, each independently with
    its stratum's probability (0 for members outside the frame, e.g. under $50k or over $5M)."""
    none = 1.0
    for q in member_probs:
        none *= 1.0 - min(1.0, max(0.0, q))
    return 1.0 - none


MAX_MEMBERS = 10     # events with more members (scheduled in the window) are left out: the fetch is too large for this session


def event_members(out, S, max_members=MAX_MEMBERS):
    """Every member of every sampled event, with the event's inclusion probability. Members scheduled to end on or
    after WIN_HI are left out (the frame's own rule); an event with any other member unresolved is dropped whole.
    Returns (members: list of market dicts in the sample's format, meta)."""
    out = Path(out)
    plan = S['plan']
    uni_ok = {}
    for m in read_gz(SRC / 'raw' / 'universe.json.gz'):
        if eligible(m):
            uni_ok[m['id']] = plan['%s|%s' % (m['cat'], vb3(m['volumeNum']))]['prob']
    by_event = collections.defaultdict(list)
    for m in S['markets']:
        by_event[str(m.get('event_id') or ('m' + str(m['id'])))].append(m)
    hi = parse_ts(WIN_HI)
    rows, meta = [], collections.Counter()
    for e, sampled in by_event.items():
        p = out / 'raw' / 'events' / e[-2:] / ('%s.json.gz' % e)
        if not p.exists():
            meta['events_missing_file'] += 1
            continue
        ev = read_gz(p)
        mem = [m for m in ev['markets'] if (parse_ts(m.get('endDate')) or 0) < hi]
        if not mem:
            meta['events_no_members_in_window'] += 1
            continue
        if len(mem) > max_members:
            meta['events_over_member_cap'] += 1
            meta['sampled_markets_in_capped_events'] += len(sampled)
            continue
        if any(P.binary_payout(m) is None or parse_ts(m.get('closedTime')) is None or len(m.get('clobTokenIds') or []) != 2
               for m in mem):
            meta['events_dropped_unresolved_member'] += 1
            meta['sampled_markets_dropped'] += len(sampled)
            continue
        p_event = event_inclusion_prob([uni_ok.get(m['id'], 0.0) for m in mem])
        if p_event <= 0:
            meta['events_zero_prob'] += 1
            continue
        s0 = sampled[0]
        sampled_ids = {x['id'] for x in sampled}
        meta['events'] += 1
        meta['members'] += len(mem)
        meta['members_added'] += sum(1 for m in mem if m['id'] not in sampled_ids)
        meta['neg_risk_events'] += int(bool(ev.get('negRisk')))
        for m in mem:
            rows.append({'id': m['id'], 'conditionId': m['conditionId'], 'clobTokenIds': m['clobTokenIds'],
                         'question': m.get('question'), 'cat': s0['cat'], 'tags': s0.get('tags'),
                         'volumeNum': m.get('volumeNum'), 'start': P.start_ts(m), 'end': parse_ts(m['endDate']),
                         'close': parse_ts(m['closedTime']), 'payout0': P.binary_payout(m),
                         'negRisk': m.get('negRisk'), 'event_id': e, 'event_title': ev.get('title'),
                         'n_members': len(mem), 'p_event': p_event, 'w_event': 1.0 / p_event,
                         'sampled': m['id'] in sampled_ids, 'stratum': s0['stratum']})
    return rows, meta


def cmd_members(args):
    """Trades and hourly prices for the members of sampled events that the volume-drawn sample left out."""
    out = Path(args.out)
    S = json.loads((out / 'sample.json').read_text())
    rows, meta = event_members(out, S)
    todo = [m for m in rows if not m['sampled'] and (m.get('volumeNum') or 0) >= args.min_member_volume]
    print(json.dumps({**meta, 'to_fetch': len(todo),
                      'skipped_small': sum(1 for m in rows if not m['sampled']) - len(todo)}), flush=True)
    t_from = parse_ts(TRADES_FROM)
    h_tr = Http(interval=args.interval, timeout=90)
    h_px = Http(interval=args.interval)
    lock = threading.Lock()
    stat = collections.Counter()
    t0 = time.time()

    def one_trades(m):
        pt = out / 'raw' / 'trades' / str(m['id'])[-2:] / ('%s.json.gz' % m['id'])
        if pt.exists():
            return
        tr, trunc, pages, err = fetch_market_trades(h_tr, m, t_from)
        if err and not tr:
            with lock:
                stat['trade_errors'] += 1
            return
        write_gz(pt, {'id': m['id'], 'fetched_at': P.utc(), 'truncated': trunc, 'pages': pages, 'error': err,
                      'min_cash': MIN_CASH, 'rows': tr, 'member_of': m['event_id']})
        with lock:
            stat['trade_markets'] += 1
            stat['trade_rows'] += len(tr)

    def one_prices(m):
        pp = out / 'raw' / 'prices' / str(m['id'])[-2:] / ('%s_h.json.gz' % m['id'])
        if pp.exists():
            return
        ser, err = [], None
        for a, b in price_windows(m, t_from):
            sx, e = fetch_prices(h_px, m['clobTokenIds'][0], coarse=False, start=a, end=b, fidelity=60)
            if sx is None:
                err = e
                continue
            ser.extend(sx)
        ser = sorted({tuple(x) for x in ser})
        write_gz(pp, {'id': m['id'], 'fetched_at': P.utc(), 'error': err, 'series': [list(x) for x in ser]})
        with lock:
            stat['price_markets'] += 1

    def run(fn, workers, label):
        done = 0
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for _ in ex.map(fn, todo):
                done += 1
                if done % 250 == 0:
                    with lock:
                        print(json.dumps({'kind': label, 'done': done, 'of': len(todo), **stat,
                                          'elapsed_s': round(time.time() - t0), 'trades_http': h_tr.stats(),
                                          'prices_http': h_px.stats()}), flush=True)
        return done

    th = threading.Thread(target=run, args=(one_prices, args.price_workers, 'prices'))
    th.start()
    done = run(one_trades, args.workers, 'trades')
    th.join()
    update_manifest(out, 'members', {'finished_at': P.utc(), 'started_at': P.utc(t0), **meta, 'fetched': len(todo),
                                     'min_member_volume': args.min_member_volume, **stat,
                                     'trades_http': h_tr.stats(), 'prices_http': h_px.stats()})
    print(json.dumps({'done': done, **stat}))
    return 0


# ------------------------------------------------------------------------------------------------ stage 2: wallet histories
# Added after a dry run of the analysis on the first 805 markets (disclosed): a wallet's skill measured on a 5% slice
# of its markets is noisy, so the most active formation wallets' full taker histories are fetched and a 'hist' score
# (edge t over every universe market of theirs closed before the selection date) is run as a secondary protocol.

HIST_N = 2500


def cmd_wallets(args):
    out = Path(args.out)
    S = json.loads((out / 'sample.json').read_text())
    c_ts = parse_ts(CUTOFF)
    usd = collections.Counter()
    for m in S['markets']:
        if m['close'] >= c_ts:
            continue
        p = out / 'raw' / 'trades' / str(m['id'])[-2:] / ('%s.json.gz' % m['id'])
        if not p.exists():
            continue
        for ts, w, side, o, sz, px in read_gz(p)['rows']:
            usd[w] += sz * px
    cands = [w for w, _ in usd.most_common(args.n_wallets)]
    http = Http(interval=args.interval, timeout=90)
    t0 = time.time()
    t_from = int(parse_ts(TRADES_FROM))
    lock = threading.Lock()
    stat = collections.Counter()

    def one(w):
        p = out / 'raw' / 'wallets' / w[2:4] / ('%s.json.gz' % w)
        if p.exists():
            return
        rows, seen, end, trunc, err = [], set(), int(t0), False, None
        for page in range(MAX_PAGES):
            q = {'user': w, 'limit': PAGE, 'takerOnly': 'true', 'filterType': 'CASH', 'filterAmount': MIN_CASH,
                 'start': t_from, 'end': end}
            d = http.request(DATA + '/trades?' + urllib.parse.urlencode(q))
            if not isinstance(d, list):
                err = d.get('__error__') if isinstance(d, dict) else 'not a list'
                break
            new = 0
            for x in d:
                key = (x.get('transactionHash'), x.get('asset'), x.get('side'))
                if key in seen:
                    continue
                seen.add(key)
                new += 1
                oi = x.get('outcomeIndex')
                rows.append([int(x.get('timestamp') or 0), x.get('conditionId'), 1 if x.get('side') == 'BUY' else 0,
                             int(oi) if oi is not None else -1, P.fnum(x.get('size'), 0.0), P.fnum(x.get('price'), 0.0),
                             str(x.get('asset') or '')[-12:]])
            if len(d) < PAGE:
                break
            if page == MAX_PAGES - 1 or new == 0:
                trunc = True
                break
            end = min(int(x.get('timestamp') or end) for x in d)
        if err and not rows:
            with lock:
                stat['errors'] += 1
            return
        write_gz(p, {'wallet': w, 'fetched_at': P.utc(), 'truncated': trunc, 'error': err, 'rows': rows})
        with lock:
            stat['wallets'] += 1
            stat['rows'] += len(rows)
            stat['truncated'] += int(trunc)

    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for _ in ex.map(one, cands):
            done += 1
            if done % 250 == 0:
                print(json.dumps({'done': done, 'of': len(cands), **stat, 'elapsed_s': round(time.time() - t0),
                                  **http.stats()}), flush=True)
    update_manifest(out, 'wallets', {'finished_at': P.utc(), 'started_at': P.utc(t0), 'candidates': len(cands),
                                     'rule': 'top %d wallets by formation-period taker $ in the sampled markets'
                                             % len(cands), **stat, 'http': http.stats(),
                                     'source': DATA + '/trades?user=<wallet>&takerOnly=true&filterType=CASH'
                                                      '&filterAmount=%d&start=%s (paged back by end)'
                                                      % (MIN_CASH, TRADES_FROM[:10])})
    print(json.dumps({'done': done, **stat, **http.stats()}))
    return 0


def load_hist(out):
    """Per wallet, per universe market (binary, resolved, not crypto up/down, life >= 2 days): (close, scheduled end,
    category, edge, capital, trades) from the wallet's full taker history. None if stage 2 was not run."""
    files = sorted((Path(out) / 'raw' / 'wallets').glob('*/*.json.gz'))
    if not files:
        return None, {}
    uni = read_gz(SRC / 'raw' / 'universe.json.gz')
    ev_n = collections.Counter(m.get('event_id') for m in uni)
    idx = {}
    for m in uni:
        if not P.eligible_binary(m) or m.get('cat') == 'crypto_updown':
            continue
        L = life_days(m)
        if L is None or L < MIN_LIFE_DAYS:
            continue
        # market type for the volume-selection bias: members of mutually exclusive or grouped sets are 'set'
        typ = 'set' if (m.get('negRisk') or m.get('event_neg_risk') or (m.get('groupItemTitle') and
                                                                        ev_n[m.get('event_id')] > 1)) else 'single'
        idx[m['conditionId']] = (parse_ts(m['closedTime']), parse_ts(m['endDate']), m['cat'], P.binary_payout(m),
                                 [str(t)[-12:] for t in m['clobTokenIds']], typ)
    del uni
    hist, meta = {}, collections.Counter()
    c_cut = parse_ts(CUTOFF)
    for f in files:
        d = read_gz(f)
        per = collections.defaultdict(lambda: [0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        for ts, cid, side, o, sz, px, asset in d['rows']:
            mm = idx.get(cid)
            if mm is None:
                meta['rows_not_in_universe'] += 1
                continue
            close, end, cat, pay0, toks, typ = mm
            if o not in (0, 1) or toks[o] != asset or not (0 < px < 1) or sz <= 0 or ts >= close:
                meta['rows_bad'] += 1
                continue
            ob, q, sh = as_purchase('BUY' if side else 'SELL', o, px, sz)
            e, c = trade_edge(ob, q, sh, pay0)
            x = per[cid]
            x[0] += e
            x[1] += c
            x[2] += 1
            d0, p0 = (sh if ob == 0 else -sh), sh * (q if ob == 0 else 1.0 - q)
            x[5] += d0
            x[6] += p0
            x[7] += sh
            if ts >= c_cut:
                x[3] += e
                x[4] += c
                x[8] += d0
                x[9] += p0
                x[10] += sh
            meta['rows'] += 1
        hist[d['wallet']] = [(idx[cid][0], idx[cid][1], idx[cid][2], x[0], x[1], x[2], x[3], x[4], cid, idx[cid][5],
                              null_var(x[5], x[6], x[7], x[1]), null_var(x[8], x[9], x[10], x[4]))
                             for cid, x in per.items()]
        meta['truncated'] += int(bool(d.get('truncated')))
    meta['wallets'] = len(hist)
    return hist, meta


def hist_table(hist, before, types=('single',)):
    """Per-wallet edge t over the wallet's universe markets closed before `before`, of the given types only: 'single'
    (default) leaves out neg-risk and grouped members, whose volume-filtered universe over-represents winners."""
    out = {}
    for w, lst in hist.items():
        sel = [x for x in lst if x[0] < before and x[9] in types]
        if not sel:
            continue
        R, t, nm = ratio_t([(x[3], x[4], x[10]) for x in sel])
        out[w] = {'n': sum(x[5] for x in sel), 'markets': nm, 'edge': R, 't': t, 't1d': None}
    return out


def hist_persistence(hist, c_ts, types=('single',)):
    """Full-history persistence: formation = markets closed before the cutoff; test = trades at or after it in markets
    scheduled to end before 2026-10-01 (so early YES resolutions of later markets are not over-represented)."""
    hi = parse_ts(WIN_HI)
    F = hist_table(hist, c_ts, types)
    T = {}
    for w, lst in hist.items():
        sel = [x for x in lst if x[0] >= c_ts and x[1] is not None and x[1] < hi and x[7] > 0 and x[9] in types]
        if not sel:
            continue
        R, t, nm = ratio_t([(x[6], x[7], x[11]) for x in sel])
        T[w] = {'n': None, 'markets': nm, 'edge': R, 't': t, 'usd': sum(x[7] for x in sel),
                'e': sum(x[6] for x in sel), 'per': [(x[8], x[6], x[7], x[11]) for x in sel]}
    rf = {w: r for w, r in F.items() if r['n'] >= MIN_TRADES and r['markets'] >= MIN_MARKETS and r['t'] is not None}
    rt = {w: r for w, r in T.items() if r['markets'] >= MIN_MARKETS and r['t'] is not None}
    both = sorted(rf.keys() & rt.keys())
    res = {'wallets': len(hist), 'ranked_formation': len(rf), 'ranked_both': len(both),
           'share_formation_t_ge_2': (sum(1 for r in rf.values() if r['t'] >= 2) / len(rf)) if rf else None,
           'spearman_edge_value': spearman([rf[w]['edge'] for w in both], [rt[w]['edge'] for w in both]),
           'spearman_edge_t': spearman([rf[w]['t'] for w in both], [rt[w]['t'] for w in both])}
    order = [w for _, w in sorted(((r['t'], w) for w, r in rf.items()), reverse=True)]

    def pooled(grp):
        # wallets in one market share its outcome: their null variances are summed (an upper bound when they bet
        # opposite ways is not needed here; the cluster variance usually binds)
        acc = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
        for w in grp:
            for cid, e, c, v in (T[w]['per'] if w in T else []):
                acc[cid][0] += e
                acc[cid][1] += c
                acc[cid][2] += v
        return ratio_t([tuple(v) for v in acc.values()])
    for k in TOPK:
        for label, grp in (('top', order[:k]), ('bottom', order[-k:])):
            R, t, n = pooled(grp)
            res['%s%d' % (label, k)] = {'test_edge_per_usd': R, 't': t, 'markets': n,
                                        'active_in_test': sum(1 for w in grp if w in T),
                                        'formation_t_min': rf[grp[-1]]['t'] if grp and label == 'top' else None}
    dec = []
    n = len(order)
    for i in range(10):
        grp = order[i * n // 10:(i + 1) * n // 10]
        R, t, nn = pooled(grp)
        if grp:
            dec.append({'decile': i + 1, 'wallets': len(grp), 't_hi': rf[grp[0]]['t'], 't_lo': rf[grp[-1]]['t'],
                        'test_edge_per_usd': R, 't': t})
    res['deciles'] = dec
    return res


# ------------------------------------------------------------------------------------------------ live books

PX_BANDS = [(0.50, 0.60), (0.60, 0.70), (0.70, 0.85), (0.85, 0.90), (0.90, 0.95), (0.95, 0.98), (0.98, 0.995)]


def fold_band(p):
    """Band of max(p, 1-p): a binary token at p and its complement at 1-p share one book, so one spread."""
    q = max(p, 1.0 - p)
    for lo, hi in PX_BANDS:
        if lo <= q < hi:
            return '%.2f-%.3f' % (lo, hi)
    return None


def cmd_books(args):
    """One read of the books of active binary markets with >= $50k volume: half-spread and touch depth on both sides,
    by category and folded price band."""
    out = Path(args.out)
    http = Http(interval=args.interval)
    t0 = time.time()
    act = P.paginate_markets_keyset(http, {'closed': 'false', 'active': 'true', 'volume_num_min': VOL_LO,
                                           'include_tag': 'true'}, max_pages=args.max_pages)
    mk = []
    for m in act:
        cm = P.compact_market(m)
        if len(cm['outcomes']) != 2 or len(cm['clobTokenIds']) != 2 or not m.get('acceptingOrders'):
            continue
        if cm['cat'] == 'crypto_updown' or not m.get('enableOrderBook', True):
            continue
        mk.append({'id': cm['id'], 'cat': cm['cat'], 'tags': cm['tags'], 'token0': cm['clobTokenIds'][0],
                   'volume': cm.get('volumeNum'), 'endDate': cm.get('endDate')})
    books = P.fetch_books(http, [m['token0'] for m in mk])
    snap = {'at': P.utc(t0), 'markets': mk, 'books': books, 'http': http.stats(), 'seconds': round(time.time() - t0)}
    write_gz(out / 'raw' / 'books' / ('books_%d.json.gz' % int(t0)), snap)
    update_manifest(out, 'books', {'at': snap['at'], 'markets': len(mk), 'books': len(books), 'http': http.stats(),
                                   'source': GAMMA + '/markets/keyset (active, volume >= $50k) + ' + CLOB + '/books'})
    print(json.dumps({'markets': len(mk), 'books': len(books), **http.stats()}))
    return 0


def book_stats(b):
    """Half-spread and touch depth (USD at the best level) of both outcomes from outcome 0's book: outcome 1's ask is
    1 - outcome 0's bid, with the bid's size."""
    asks, bids = b.get('asks') or [], b.get('bids') or []
    if not asks or not bids:
        return None
    ba, bb = asks[0][0], bids[0][0]
    if ba <= bb:
        return None
    mid = (ba + bb) / 2.0
    return {'mid': mid, 'half_spread': (ba - bb) / 2.0,
            'ask0_usd': ba * asks[0][1], 'ask1_usd': (1.0 - bb) * bids[0][1],
            'ask0_usd_2c': sum(p * s for p, s in asks if p <= ba + 0.02 + 1e-9),
            'ask1_usd_2c': sum((1.0 - p) * s for p, s in bids if p >= bb - 0.02 - 1e-9)}




# ------------------------------------------------------------------------------------------------ cost tables

def pctl(v, q):
    v = sorted(v)
    return v[int(q * (len(v) - 1))] if v else None


def spread_tables(out):
    """Half-spread by (category, folded band): the 2026-10-09 live table where it covers the band (folded price >=
    0.85, the protocol's), this study's live read below 0.85. Touch depth (USD at the best ask) by (category, folded
    band, side), side = 'fav' when the token bought is priced >= 0.5, from this study's read."""
    old = json.loads((SRC / 'analysis.json').read_text())['live']
    snaps = sorted((Path(out) / 'raw' / 'books').glob('books_*.json.gz'))
    hs, dep = collections.defaultdict(list), collections.defaultdict(list)
    at = None
    if snaps:
        s = read_gz(snaps[-1])
        at = s['at']
        for m in s['markets']:
            b = s['books'].get(m['token0'])
            st = book_stats(b) if b else None
            if not st:
                continue
            band = fold_band(st['mid'])
            if band is None:
                continue
            fav0 = st['mid'] >= 0.5
            for c in (m['cat'], 'all'):
                hs[(c, band)].append(st['half_spread'])
                dep[(c, band, 'fav')].append(st['ask0_usd'] if fav0 else st['ask1_usd'])
                dep[(c, band, 'long')].append(st['ask1_usd'] if fav0 else st['ask0_usd'])
    return {'books_at': at, 'old_half_spread': old['half_spread'],
            'new_half_spread': {'%s|%s' % k: {'n': len(v), 'median': statistics.median(v), 'p75': pctl(v, 0.75)}
                                for k, v in hs.items()},
            'new_depth': {'%s|%s|%s' % k: {'n': len(v), 'median_usd': statistics.median(v), 'p25_usd': pctl(v, 0.25),
                                           'p75_usd': pctl(v, 0.75)} for k, v in dep.items()}}


def half_spread_of(tbl, cat, p, which='median'):
    band = fold_band(p) or '0.98-0.995'
    srcs = [tbl['old_half_spread'], tbl['new_half_spread']] if max(p, 1.0 - p) >= 0.85 else [tbl['new_half_spread']]
    for src in srcs:
        for key in ('%s|%s' % (cat, band), 'all|%s' % band):
            r = src.get(key)
            if r and r['n'] >= 5:
                return r[which]
    return 0.005


def touch_depth(tbl, cat, p):
    band = fold_band(p) or '0.98-0.995'
    side = 'fav' if p >= 0.5 else 'long'
    for key in ('%s|%s|%s' % (cat, band, side), 'all|%s|%s' % (band, side)):
        r = tbl['new_depth'].get(key)
        if r and r['n'] >= 5:
            return r['median_usd']
    return 0.0


# ------------------------------------------------------------------------------------------------ load

def load_markets(out, mode='events'):
    """mode 'sample': the volume-drawn sample as collected, weighted by stratum (biased: see event completion).
    mode 'events': every member of each sampled event, weighted by 1 / P(event drawn)."""
    out = Path(out)
    S = json.loads((out / 'sample.json').read_text())
    plan = S['plan']
    meta = collections.Counter()
    if mode in ('events', 'events_sampled_only'):
        cand, emeta = event_members(out, S)
        meta.update({'ev_' + k: v for k, v in emeta.items()})
        for m in cand:
            m['w'] = m['w_event']
        if mode == 'events_sampled_only':
            cand = [m for m in cand if m['sampled']]
    else:
        cand = [dict(m) for m in S['markets']]
        have = [m for m in cand if (out / 'raw' / 'trades' / str(m['id'])[-2:] / ('%s.json.gz' % m['id'])).exists()]
        ncoll = collections.Counter(m['stratum'] for m in have)
        for m in cand:
            m['w'] = plan[m['stratum']]['count'] / max(1, ncoll[m['stratum']])
            m['sampled'] = True
    mk = {}
    for m in cand:
        pt = out / 'raw' / 'trades' / str(m['id'])[-2:] / ('%s.json.gz' % m['id'])
        pp = out / 'raw' / 'prices' / str(m['id'])[-2:] / ('%s_h.json.gz' % m['id'])
        d = read_gz(pt) if pt.exists() else None
        if d is None:
            if mode == 'sample' or m.get('sampled'):
                meta['missing_trades_file'] += 1
                continue
            meta['members_without_trades_file'] += 1     # below the member volume floor: no trades >= $50 kept
            d = {'rows': [], 'truncated': False}
        px = read_gz(pp) if pp.exists() else {'series': []}
        if d['rows'] and not pp.exists():
            meta['markets_trades_without_prices'] += 1
        rows = []
        for ts, w, side, o, sz, pr in d['rows']:
            if o not in (0, 1) or not (0.0 < pr < 1.0) or sz <= 0:
                meta['rows_bad'] += 1
                continue
            if ts >= m['close']:
                meta['rows_after_close'] += 1
                continue
            rows.append((ts, sys.intern(w), side, o, sz, pr))
        rows.sort()
        meta['rows'] += len(rows)
        m['rate'] = fee_rate(m['cat'], m.get('tags'))
        m['trades'] = rows
        m['_tx'] = [x[0] for x in rows]
        ser = sorted(px['series'])
        m['sx'] = [x[0] for x in ser]
        m['sp'] = [x[1] for x in ser]
        m['truncated'] = d['truncated']
        meta['truncated'] += int(bool(d['truncated']))
        meta['markets'] += 1
        meta['markets_with_trades'] += int(bool(rows))
        mk[m['id']] = m
    return mk, meta, S


def market_type(m):
    if m.get('negRisk'):
        return 'negrisk'
    return 'multi' if (m.get('n_members') or 1) > 1 else 'single'


def calibration_by_type(markets):
    """YES rate against outcome 0's midpoint at a quarter, half and three quarters of the market's life, by type:
    the selection check (a volume-drawn sample over-represents winners of multi-outcome events)."""
    acc = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0])
    for m in markets.values():
        if m['payout0'] not in (0.0, 1.0) or not m['sx']:
            continue
        st = max(m['start'] or m['sx'][0], m['sx'][0])
        for frac in (0.25, 0.5, 0.75):
            p = mid_at(m['sx'], m['sp'], st + frac * (m['close'] - st))
            if p is None:
                continue
            for key in ((market_type(m), frac), ('all', frac)):
                a = acc[key]
                a[0] += 1
                a[1] += p
                a[2] += m['payout0']
                a[3] += m['w']
    out = {}
    for (t, f), (n, sp_, sy, sw) in acc.items():
        out['%s|%.2f' % (t, f)] = {'n': n, 'mean_price0': sp_ / n, 'yes_rate': sy / n, 'excess': (sy - sp_) / n,
                                    'se': math.sqrt(max(1e-9, (sy / n) * (1 - sy / n) / n))}
    return out


def mid0_at(m, T):
    """Outcome 0's midpoint at T; the payout once the market has closed."""
    if T >= m['close']:
        return m['payout0']
    return mark_mid(m['sx'], m['sp'], T)


# ------------------------------------------------------------------------------------------------ wallet skill

def market_accumulators(m, c_ts):
    """Per-wallet sums over one market: for all trades and for trades at or after c_ts. Each is
    [n, edge, capital, mk1h, cap1h, mk1d, cap1d, buy_usd, sell_usd, outcome mask, first ts, last ts, net shares of
    outcome 0, sum shares x price of outcome 0, sum shares]."""
    acc = {}
    for ts, w, side, o, s, p in m['trades']:
        ob, q, sh = as_purchase('BUY' if side else 'SELL', o, p, s)
        e, c = trade_edge(ob, q, sh, m['payout0'])
        m1, m24 = mid0_at(m, entry_time(ts, HOUR)), mid0_at(m, entry_time(ts, DAY))
        parts = acc.get(w)
        if parts is None:
            parts = acc[w] = {'all': None, 'test': None}
        for part in ('all', 'test'):
            if part == 'test' and ts < c_ts:
                continue
            x = parts[part]
            if x is None:
                x = parts[part] = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, ts, ts, 0.0, 0.0, 0.0]
            x[0] += 1
            x[1] += e
            x[2] += c
            if m1 is not None:
                x[3] += sh * (mid_of(ob, m1) - q)
                x[4] += c
            if m24 is not None:
                x[5] += sh * (mid_of(ob, m24) - q)
                x[6] += c
            if side:
                x[7] += s * p
            else:
                x[8] += s * p
            x[9] |= (1 << ob)
            x[11] = ts
            x[12] += sh if ob == 0 else -sh          # net shares of outcome 0
            x[13] += sh * (q if ob == 0 else 1.0 - q)  # share-weighted price of outcome 0 paid
            x[14] += sh
    return acc


def wallet_table(accs, markets, part='all', keep=None):
    """Aggregate per-(wallet, market) sums into per-wallet skill over the markets `keep` accepts."""
    per = collections.defaultdict(list)
    for mid, a in accs.items():
        m = markets[mid]
        if keep is not None and not keep(m):
            continue
        for w, parts in a.items():
            x = parts[part]
            if x is not None and x[0] > 0:
                per[w].append((mid, x))
    out = {}
    for w, lst in per.items():
        R, t, nm = ratio_t([(x[1], x[2], null_var(x[12], x[13], x[14], x[2])) for _, x in lst])
        # the markout t's take the same fair-pricing floor (conservative: a 1-day price change varies less than the
        # payout); without it a wallet whose markets all resolve within the day has the clean-sweep infinite t
        R1, t1, _ = ratio_t([(x[3], x[4], null_var(x[12], x[13], x[14], x[4])) for _, x in lst if x[4] > 0])
        R24, t24, _ = ratio_t([(x[5], x[6], null_var(x[12], x[13], x[14], x[6])) for _, x in lst if x[6] > 0])
        cats = collections.Counter()
        for mid, x in lst:
            cats[markets[mid]['cat']] += x[2]
        out[w] = {'n': sum(x[0] for _, x in lst), 'markets': nm, 'usd': sum(x[2] for _, x in lst),
                  'edge': R, 't': t, 'mk1h': R1, 't1h': t1, 'mk1d': R24, 't1d': t24,
                  'buy_usd': sum(x[7] for _, x in lst), 'sell_usd': sum(x[8] for _, x in lst),
                  'two_sided_share': sum(1 for _, x in lst if x[9] == 3) / nm,
                  'cat_usd': dict(cats), 'first': min(x[10] for _, x in lst), 'last': max(x[11] for _, x in lst)}
    return out


def ranked(tab, score_key):
    return {w: r for w, r in tab.items() if r['n'] >= MIN_TRADES and r['markets'] >= MIN_MARKETS
            and r.get(score_key) is not None}


def select(tab, score, thr, k):
    key = 't' if score == 'edge' else 't1d'
    el = ranked(tab, key)
    xs = sorted(((r[key], w) for w, r in el.items() if r[key] >= thr), reverse=True)[:k]
    return [w for _, w in xs]


def pooled_edge(accs, markets, wallets, part='test', field=(1, 2)):
    """Edge per $ of a set of wallets pooled, clustered by market."""
    ws = set(wallets)
    per = []
    for mid, a in accs.items():
        e = c = d = sp_ = ss = 0.0
        for w in ws & a.keys():
            x = a[w][part]
            if x is not None:
                e += x[field[0]]
                c += x[field[1]]
                d += x[12]
                sp_ += x[13]
                ss += x[14]
        if c > 0:
            per.append((e, c, null_var(d, sp_, ss, c)) if field == (1, 2) else (e, c))
    R, t, n = ratio_t(per)
    return {'edge_per_usd': R, 't': t, 'markets': n, 'usd': sum(x[1] for x in per)}


def persistence(accs, markets, c_ts):
    F = wallet_table(accs, markets, 'all', keep=lambda m: m['close'] < c_ts)
    T = wallet_table(accs, markets, 'test', keep=lambda m: m['close'] >= c_ts)
    res = {'formation_wallets': len(F), 'test_wallets': len(T)}
    for key in ('t', 't1d'):
        rf, rt = ranked(F, key), ranked(T, key)
        both = sorted(rf.keys() & rt.keys())
        res['ranked_formation_%s' % key] = len(rf)
        res['ranked_both_%s' % key] = len(both)
        res['share_formation_t_ge_2_%s' % key] = (sum(1 for r in rf.values() if r[key] >= 2) / len(rf)) if rf else None
        res['share_formation_t_le_-2_%s' % key] = (sum(1 for r in rf.values() if r[key] <= -2) / len(rf)) if rf else None
        if len(both) >= 3:
            val = 'edge' if key == 't' else 'mk1d'
            res['spearman_%s_value' % val] = spearman([rf[w][val] for w in both], [rt[w][val] for w in both])
            res['spearman_%s_t' % val] = spearman([rf[w][key] for w in both], [rt[w][key] for w in both])
    both = sorted(ranked(F, 't1d').keys() & ranked(T, 't').keys())
    if len(both) >= 3:
        res['spearman_formation_mk1d_vs_test_edge'] = spearman([F[w]['mk1d'] for w in both], [T[w]['edge'] for w in both])
    # top-k by formation t: their pooled test-period edge (all their test trades, not only ranked wallets)
    for key, label in (('t', 'edge'), ('t1d', 'mk1d')):
        rf = ranked(F, key)
        order = [w for _, w in sorted(((r[key], w) for w, r in rf.items()), reverse=True)]
        rows = {}
        for k in TOPK:
            top = order[:k]
            rows['top%d' % k] = {'formation_t_min': rf[top[-1]][key] if top else None,
                                 'test_edge': pooled_edge(accs, markets, top, 'test', (1, 2)),
                                 'test_mk1h': pooled_edge(accs, markets, top, 'test', (3, 4)),
                                 'test_mk1d': pooled_edge(accs, markets, top, 'test', (5, 6)),
                                 'active_in_test': sum(1 for w in top if w in T)}
            rows['bottom%d' % k] = {'test_edge': pooled_edge(accs, markets, order[-k:], 'test', (1, 2))}
        # deciles of formation t among ranked wallets
        dec = []
        n = len(order)
        for i in range(10):
            grp = order[i * n // 10:(i + 1) * n // 10]
            if grp:
                dec.append({'decile': i + 1, 'wallets': len(grp), 't_hi': rf[grp[0]][key], 't_lo': rf[grp[-1]][key],
                            'test_edge': pooled_edge(accs, markets, grp, 'test', (1, 2))})
        rows['deciles'] = dec
        res['topk_by_%s' % label] = rows
    return res, F, T


def all_taker_edge(accs, markets, keep, part):
    by = collections.defaultdict(list)
    for mid, a in accs.items():
        m = markets[mid]
        if not keep(m):
            continue
        e = c = e1 = c1 = 0.0
        for parts in a.values():
            x = parts[part]
            if x is not None:
                e += x[1]
                c += x[2]
                e1 += x[3]
                c1 += x[4]
        if c > 0:
            by[m['cat']].append((e, c, e1, c1))
            by['all'].append((e, c, e1, c1))
    out = {}
    for cat, lst in by.items():
        R, t, n = ratio_t([(e, c) for e, c, _, _ in lst])
        R1, t1, _ = ratio_t([(e1, c1) for _, _, e1, c1 in lst if c1 > 0])
        out[cat] = {'edge_per_usd': R, 't': t, 'mk1h_per_usd': R1, 'markets': n, 'usd': sum(x[1] for x in lst)}
    return out


# ------------------------------------------------------------------------------------------------ follower

def market_episodes(m, c_ts):
    buys = [{'ts': ts, 'wallet': w, 'outcome': o, 'price': p, 'size': s} for ts, w, side, o, s, p in m['trades']
            if side == 1]
    eps = [e for e in buy_episodes(buys) if e['ts'] >= c_ts]
    sells = collections.defaultdict(list)
    for ts, w, side, o, s, p in m['trades']:
        if side == 0:
            sells[(w, o)].append(ts)
    return eps, sells


def ref_mid_5m(m, ep, tbl, txs):
    """Reference only: outcome o's midpoint implied by the first trade by another wallet 5-65 minutes after the
    signal (an ask when it bought o, a bid when it bought the complement), +- the half-spread."""
    t0 = ep['ts'] + 300
    i = bisect.bisect_left(txs, t0)
    tr = m['trades']
    while i < len(tr) and tr[i][0] <= ep['ts'] + 3900:
        ts, w, side, o, s, p = tr[i]
        if w != ep['wallet']:
            ob, q, _ = as_purchase('BUY' if side else 'SELL', o, p, s)
            if ob == ep['outcome']:
                return ts, q - half_spread_of(tbl, m['cat'], q)
            bid = 1.0 - q
            return ts, bid + half_spread_of(tbl, m['cat'], bid)
        i += 1
    return None, None


def episode_records(m, ep, sells, tbl, txs):
    """Everything the follower variants need for one signal: the leader's own return and, per delay, the hold and
    wallet-exit records (None when the follower cannot enter: market closed, no price, or the wallet already out)."""
    o = ep['outcome']
    pay = payout_of(o, m['payout0'])
    rate = m['rate']
    lv = ep['vwap']
    rec = {'leader': payout_of(o, m['payout0']) / (lv + rate * lv * (1 - lv)) - 1.0}
    s_after = [t for t in sells.get((ep['wallet'], o), []) if t > ep['ts'] and t >= ep['last_ts']]
    t_sell = s_after[0] if s_after else None
    rec['t_sell'] = t_sell
    for name, delay in DELAYS.items():
        if name == '5m':
            ts_ref, mo = ref_mid_5m(m, ep, tbl, txs)
            if mo is None or not (0.0 < mo < 1.0):
                rec['5m'] = None
                continue
            hs = half_spread_of(tbl, m['cat'], mo)
            rec['5m'] = {'hold': {'t_in': ts_ref, 't_out': m['close'], 'mid_in': mo,
                                  'ret': follower_return(mo, pay, hs, rate)}}
            continue
        T_in = entry_time(ep['ts'], delay)
        if T_in >= m['close']:
            rec[name] = None
            continue
        m0 = mark_mid(m['sx'], m['sp'], T_in)
        if m0 is None:
            rec[name] = None
            continue
        mo = mid_of(o, m0)
        hs = half_spread_of(tbl, m['cat'], mo)
        r = {'hold': {'t_in': T_in, 't_out': m['close'], 'mid_in': mo, 'hs': hs,
                      'ret': follower_return(mo, pay, hs, rate)}}
        if t_sell is not None and t_sell + delay <= T_in:
            r['wexit'] = None          # the follower sees the wallet's exit before it would enter
        elif t_sell is not None and entry_time(t_sell, delay) < m['close']:
            T_out = entry_time(t_sell, delay)
            m1 = mark_mid(m['sx'], m['sp'], T_out)
            if m1 is None:
                r['wexit'] = dict(r['hold'])
            else:
                mo1 = mid_of(o, m1)
                hs1 = half_spread_of(tbl, m['cat'], mo1)
                r['wexit'] = {'t_in': T_in, 't_out': T_out, 'mid_in': mo, 'hs': hs, 'mid_out': mo1,
                              'ret': follower_return(mo, pay, hs, rate, mo1, hs1)}
        else:
            r['wexit'] = dict(r['hold'])
        rec[name] = r
    return rec


def build_signals(markets, c_ts, tbl):
    sig = []
    for mid, m in markets.items():
        eps, sells = market_episodes(m, c_ts)
        txs = m['_tx']
        for ep in eps:
            rec = episode_records(m, ep, sells, tbl, txs)
            sig.append({'mid': mid, 'cat': m['cat'], 'w': m['w'], 'wallet': ep['wallet'], 'ts': ep['ts'],
                        'usd': ep['usd'], 'outcome': ep['outcome'], 'vwap': ep['vwap'], 'close': m['close'],
                        'event': m.get('event_id') or mid, **rec})
    sig.sort(key=lambda s: s['ts'])
    return sig


def month_bounds():
    b = [parse_ts(d + 'T00:00:00+00:00') for d in MONTHS] + [parse_ts(WIN_HI)]
    return list(zip(b[:-1], b[1:]))


def selections(accs, markets, hist=None):
    """Walk-forward: on the 1st of each month, rank wallets on markets closed before that date only."""
    out = {}
    for lo, hi in month_bounds():
        tab = wallet_table(accs, markets, 'all', keep=lambda m, lo=lo: m['close'] < lo)
        sel = {}
        for score in SCORES:
            for name, (thr, k) in SELECTIONS.items():
                sel[(score, name)] = set(select(tab, score, thr, k))
        if hist:
            tab_h = hist_table(hist, lo)
            for name, (thr, k) in SELECTIONS.items():
                sel[('hist', name)] = set(select(tab_h, 'edge', thr, k))
        key = 't'
        el = ranked(tab, key)
        sel[('edge', 'anti_bottom100')] = set(w for _, w in sorted(((r[key], w) for w, r in el.items()
                                                                     if r[key] <= -2.0))[:100])
        out[(lo, hi)] = {'sel': sel, 'ranked': len(el), 'tab_size': len(tab)}
    return out


def variant_rows(signals, sels, score, selname, cat, min_size, exit_mode, delay, weighted=True):
    rows = []
    for (lo, hi), S in sels.items():
        ws = S['sel'].get((score, selname)) if selname != 'all_wallets' else None
        for s in signals:
            if not (lo <= s['ts'] < hi):
                continue
            if ws is not None and s['wallet'] not in ws:
                continue
            if cat == 'sports' and s['cat'] != 'sports':
                continue
            if cat == 'nonsports' and s['cat'] == 'sports':
                continue
            if s['usd'] < min_size:
                continue
            r = s.get(delay)
            if r is None:
                continue
            x = r.get(exit_mode) if exit_mode in r else r.get('hold')
            if x is None:
                continue
            rows.append({'t_in': x['t_in'], 't_out': x['t_out'], 'ret': x['ret'], 'stake': s['w'] if weighted else 1.0,
                         'outcome': s['outcome'], 'event': s['event'],
                         'mid': s['mid'], 'cat': s['cat'], 'mid_in': x['mid_in'], 'usd': s['usd'], 'w': s['w'],
                         'wallet': s['wallet'], 'leader': s['leader'], 'close': s['close'], 'sig_ts': s['ts']})
    return rows


def rows_summary(rows):
    if not rows:
        return {'n': 0}
    sw = sum(r['stake'] for r in rows)
    sr = sum(r['stake'] * r['ret'] for r in rows)
    sd = sum(r['stake'] * max(1.0 / 24, (r['t_out'] - r['t_in']) / DAY) for r in rows)
    per = collections.defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        per[r['mid']][0] += r['stake'] * r['ret']
        per[r['mid']][1] += r['stake']
    R, t, nm = ratio_t([tuple(v) for v in per.values()])
    pe = collections.defaultdict(lambda: [0.0, 0.0])
    for r in rows:
        pe[r['event']][0] += r['stake'] * r['ret']
        pe[r['event']][1] += r['stake']
    _, t_ev, n_ev = ratio_t([tuple(v) for v in pe.values()])
    ann = sr / sd * 365.0 if sd > 0 else None
    return {'n': len(rows), 'markets': nm, 'events': n_ev, 'wallets': len({r['wallet'] for r in rows}), 'stake': sw,
            'mean_ret': sr / sw, 't_market_clustered': t, 't_event_clustered': t_ev, 'hit_rate': sum(r['stake'] for r in rows if r['ret'] > 0) / sw,
            'mean_hold_days': sd / sw, 'ann_return': ann, 'ann_excess': (ann - SSR) if ann is not None else None,
            'mean_entry_mid': sum(r['stake'] * r['mid_in'] for r in rows) / sw,
            'leader_mean_ret': sum(r['stake'] * r['leader'] for r in rows) / sw}


# ------------------------------------------------------------------------------------------------ analyze

PREREG = {
    'written': '2026-10-14 ~07:50 UTC, before any trade, price or return of this study was fetched',
    'sample': 'binary, not crypto up/down, $50k-$5M volume, scheduled endDate in [2025-10-01, 2026-10-01), life >= 2 '
              'days; category x volume strata, hash-drawn; weight = stratum count / collected',
    'trades': 'taker trades >= $50 (CASH filter) from 2025-07-01, <= 30,000 per market',
    'formation_cutoff': CUTOFF,
    'skill': 'edge per $ = sum(shares x (payout - price)) / sum(shares x price) over purchases (SELL o at p = buy 1-o '
             'at 1-p); markouts at the first hourly mark >= +1h / +1d; t clustered by market; ranked when >= 10 trades '
             'in >= 5 markets',
    'persistence': 'Spearman formation vs test (wallets ranked in both); top-k (10, 50, 100, 250) by formation t: '
                   'pooled test edge per $, market-clustered',
    'follower': "buy episodes (a wallet's BUYs of one outcome merged while gaps < 1h); entry at the first hourly mark "
                ">= +delay at mid + live half-spread + taker fee; hold, or exit at the first hourly mark >= the "
                "wallet's sale + delay at mid - half-spread - fee; walk-forward monthly selection on markets closed "
                "before the 1st; stake = market weight (equal dollars per universe signal)",
    'grid': 'score {edge, mk1d} x selection {t2_top20, t2_top100, t1_top300} x cat {all, sports, nonsports} x '
            'min_size {50, 1000} x exit {hold, wexit}; delay +1h (72)',
    'protocol': 'daily P&L over average capital minus SSR/365 from 2026-05-01; choose_then_test frac 0.5; go = '
                'in-sample positive & OOS HAC t >= 2 & chosen in bh_survivors_positive & positive $/yr over SSR at '
                'capacity',
}


def grid_names():
    names = []
    for score in SCORES:
        for sel in SELECTIONS:
            for cat in CATS:
                for ms in MIN_SIZES:
                    for ex in EXITS:
                        names.append((score, sel, cat, ms, ex))
    return names


def vname(v):
    return '%s|%s|%s|min%d|%s' % v


def split_rows(rows, split_ts):
    return [r for r in rows if r['t_out'] < split_ts], [r for r in rows if r['t_in'] >= split_ts]


def capacity_of(rows, tbl, markets, span_days):
    """$/yr over SSR at capacity: each signal is filled up to the smaller of the live median depth at the best ask
    (category, folded band, side) and the leader's own episode size; universe-scaled by the market weight."""
    if not rows:
        return {'signals': 0}
    cap_days = exc = stake = 0.0
    flows, sizes = [], []
    for r in rows:
        m = markets[r['mid']]
        c = min(touch_depth(tbl, r['cat'], r['mid_in']), r['usd'])
        hold = max(1.0 / 24, (r['t_out'] - r['t_in']) / DAY)
        cap_days += r['w'] * c * hold
        exc += r['w'] * c * (r['ret'] - SSR * hold / 365.0)
        stake += r['w'] * c
        sizes.append(c)
        # what other takers bought of the same outcome within an hour either side of the follower's entry
        lo, hi = r['t_in'] - HOUR, r['t_in'] + HOUR
        i = bisect.bisect_left(m['_tx'], lo)
        v = 0.0
        while i < len(m['trades']) and m['trades'][i][0] <= hi:
            ts, w, side, o, s, p = m['trades'][i]
            if w != r['wallet']:
                ob, q, sh = as_purchase('BUY' if side else 'SELL', o, p, s)
                if ob == r['outcome']:
                    v += sh * q
            i += 1
        flows.append(v)
    return {'signals': len(rows), 'universe_signals_per_year': sum(r['w'] for r in rows) * 365.0 / span_days,
            'median_fill_usd': statistics.median(sizes), 'median_same_side_flow_usd_2h': statistics.median(flows),
            'median_fill_over_flow': statistics.median([c / f for c, f in zip(sizes, flows) if f > 0]) if any(flows) else None,
            'avg_capital_usd': cap_days / span_days, 'stake_usd_total': stake,
            'excess_usd': exc, 'usd_per_year': exc * 365.0 / span_days,
            'ann_excess_on_capital': (exc / cap_days * 365.0) if cap_days > 0 else None}


def describe_wallets(F, T, wallets, signals, markets):
    rows = []
    for w in wallets:
        f = F.get(w)
        if not f:
            continue
        mine = [s for s in signals if s['wallet'] == w]
        holds = []
        for s in mine:
            end = s['t_sell'] if s.get('t_sell') else s['close']
            holds.append((end - s['ts']) / DAY)
        cat = max(f['cat_usd'].items(), key=lambda kv: kv[1])[0] if f['cat_usd'] else None
        rows.append({'wallet': w, 'formation_n': f['n'], 'formation_markets': f['markets'], 'formation_usd': f['usd'],
                     'formation_edge': f['edge'], 'formation_t': f['t'], 'formation_mk1h': f['mk1h'],
                     'formation_mk1d': f['mk1d'], 'main_cat': cat,
                     'main_cat_share': f['cat_usd'][cat] / f['usd'] if cat and f['usd'] else None,
                     'two_sided_share': f['two_sided_share'],
                     'sell_share': f['sell_usd'] / (f['buy_usd'] + f['sell_usd']) if (f['buy_usd'] + f['sell_usd']) else None,
                     'test_edge': T[w]['edge'] if w in T else None, 'test_t': T[w]['t'] if w in T else None,
                     'test_markets': T[w]['markets'] if w in T else 0,
                     'test_signals': len(mine), 'median_signal_usd': statistics.median([s['usd'] for s in mine]) if mine else None,
                     'median_hold_days': statistics.median(holds) if holds else None})
    return rows


def cmd_analyze(args):
    out = Path(args.out)
    t0 = time.time()
    tbl = spread_tables(out)
    markets, meta, S = load_markets(out, args.mode)
    c_ts = parse_ts(CUTOFF)
    print(json.dumps({'loaded': len(markets), **meta, 's': round(time.time() - t0)}), flush=True)
    accs = {mid: market_accumulators(m, c_ts) for mid, m in markets.items()}
    print(json.dumps({'accumulated': len(accs), 's': round(time.time() - t0)}), flush=True)
    res = {'generated': P.utc(), 'mode': args.mode, 'prereg': PREREG, 'cutoff': CUTOFF, 'ssr': SSR, 'meta': dict(meta),
           'calibration_by_type': calibration_by_type(markets),
           'cost_tables': {'books_at': tbl['books_at'], 'new_half_spread': tbl['new_half_spread'],
                           'new_depth': tbl['new_depth']}}
    cats = collections.Counter(m['cat'] for m in markets.values())
    res['sample'] = {'markets': len(markets), 'by_cat': dict(cats),
                     'formation_markets': sum(1 for m in markets.values() if m['close'] < c_ts),
                     'test_markets': sum(1 for m in markets.values() if m['close'] >= c_ts),
                     'trades': meta['rows'], 'wallets': len({w for a in accs.values() for w in a}),
                     'universe_markets_represented': sum(m['w'] for m in markets.values()),
                     'truncated_markets': meta['truncated']}
    res['all_takers'] = {'formation': all_taker_edge(accs, markets, lambda m: m['close'] < c_ts, 'all'),
                         'test': all_taker_edge(accs, markets, lambda m: m['close'] >= c_ts, 'test')}
    pers, F, T = persistence(accs, markets, c_ts)
    res['persistence'] = pers
    print(json.dumps({'persistence': {k: v for k, v in pers.items() if not isinstance(v, dict)},
                      's': round(time.time() - t0)}), flush=True)

    hist, hmeta = load_hist(out)
    if hist:
        res['hist_meta'] = dict(hmeta)
        res['hist_persistence'] = hist_persistence(hist, c_ts, ('single',))
        res['hist_persistence_incl_sets_biased'] = hist_persistence(hist, c_ts, ('single', 'set'))
        print(json.dumps({'hist': dict(hmeta), 's': round(time.time() - t0)}), flush=True)
    signals = build_signals(markets, c_ts, tbl)
    sels = selections(accs, markets, hist)
    res['selection_by_month'] = {P.utc(lo)[:10]: {'ranked_wallets': S_['ranked'],
                                                  'sizes': {'%s|%s' % k: len(v) for k, v in S_['sel'].items()}}
                                 for (lo, hi), S_ in sels.items()}
    res['signals'] = {'episodes_test': len(signals), 'with_1h_entry': sum(1 for s in signals if s.get('1h')),
                      'with_1d_entry': sum(1 for s in signals if s.get('1d')),
                      'with_5m_ref': sum(1 for s in signals if s.get('5m'))}
    print(json.dumps({'signals': res['signals'], 's': round(time.time() - t0)}), flush=True)

    d_lo = int(c_ts // DAY)
    d_hi = int(max(m['close'] for m in markets.values()) // DAY)
    n_days = d_hi - d_lo + 1
    split_i = B.cutoff_index(n_days, 0.5)
    split_ts = (d_lo + split_i) * DAY
    res['series'] = {'first_day': P.utc(d_lo * DAY)[:10], 'last_day': P.utc(d_hi * DAY)[:10], 'days': n_days,
                     'split_day': P.utc(split_ts)[:10]}

    variants, summaries = {}, {}
    for v in grid_names():
        rows = variant_rows(signals, sels, *v, delay='1h')
        variants[vname(v)] = daily_pnl_series(rows, d_lo, d_hi)[0]
        ins, oos = split_rows(rows, split_ts)
        summaries[vname(v)] = {'all': rows_summary(rows), 'in': rows_summary(ins), 'oos': rows_summary(oos)}
    proto = B.choose_then_test(variants, frac=0.5, periods_per_year=365)
    res['protocol'] = {k: v for k, v in proto.items() if k != 'bh_adjusted_p'}
    res['protocol']['bh_adjusted_p_chosen'] = proto['bh_adjusted_p'].get(proto['chosen'])
    res['variants_1h'] = summaries
    ch = proto['chosen']
    chv = tuple(int(x[3:]) if x.startswith('min') else x for x in ch.split('|'))

    # robustness of the chosen variant: unweighted, p75 spread
    rows_ch = variant_rows(signals, sels, *chv, delay='1h')
    ins, oos = split_rows(rows_ch, split_ts)
    rows_uw = variant_rows(signals, sels, *chv, delay='1h', weighted=False)
    res['chosen'] = {'name': ch, 'in': rows_summary(ins), 'oos': rows_summary(oos),
                     'unweighted_all': rows_summary(rows_uw),
                     'unweighted_oos': rows_summary(split_rows(rows_uw, split_ts)[1])}

    # baselines and the +1d grid (counted as tried, not used for the go)
    base = {}
    for cat in CATS:
        for ms in MIN_SIZES:
            rows = variant_rows(signals, sels, 'edge', 'all_wallets', cat, ms, 'hold', '1h')
            base['all_wallets|%s|min%d|hold' % (cat, ms)] = {'all': rows_summary(rows),
                                                             'oos': rows_summary(split_rows(rows, split_ts)[1])}
    rows = variant_rows(signals, sels, 'edge', 'anti_bottom100', 'all', 50, 'hold', '1h')
    base['anti_bottom100|all|min50|hold'] = {'all': rows_summary(rows), 'oos': rows_summary(split_rows(rows, split_ts)[1])}
    res['baselines_1h'] = base
    grid_1d = {}
    for v in grid_names():
        rows = variant_rows(signals, sels, *v, delay='1d')
        grid_1d[vname(v)] = {'all': rows_summary(rows), 'oos': rows_summary(split_rows(rows, split_ts)[1])}
    res['variants_1d'] = grid_1d

    # secondary (disclosed, added after a partial dry run): the 'hist' selection, alone and pooled with the grid
    if hist:
        hv, hs_ = dict(variants), {}
        for v in grid_names():
            if v[0] != 'edge':
                continue
            hv_name = vname(('hist',) + v[1:])
            rows = variant_rows(signals, sels, 'hist', *v[1:], delay='1h')
            hv[hv_name] = daily_pnl_series(rows, d_lo, d_hi)[0]
            ins_, oos_ = split_rows(rows, split_ts)
            hs_[hv_name] = {'all': rows_summary(rows), 'in': rows_summary(ins_), 'oos': rows_summary(oos_)}
        only = {k: v for k, v in hv.items() if k.startswith('hist|')}
        p_only = B.choose_then_test(only, frac=0.5, periods_per_year=365)
        p_all = B.choose_then_test(hv, frac=0.5, periods_per_year=365)
        res['secondary_hist'] = {
            'variants': hs_,
            'protocol_hist_only': {k: v for k, v in p_only.items() if k != 'bh_adjusted_p'},
            'protocol_pooled_108': {k: v for k, v in p_all.items() if k != 'bh_adjusted_p'}}
        for label, v in (('hist_t2_top100_all', ('hist', 't2_top100', 'all', 50, 'hold')),
                         ('hist_t2_top20_all', ('hist', 't2_top20', 'all', 50, 'hold'))):
            by_delay = {d: variant_rows(signals, sels, *v[:4], 'hold', d) for d in DELAYS}
            common = set.intersection(*[{(r['mid'], r['wallet'], r['sig_ts']) for r in by_delay[d]} for d in DELAYS])
            row = {d: {'all': rows_summary(rows), 'common': rows_summary(
                [r for r in rows if (r['mid'], r['wallet'], r['sig_ts']) in common])} for d, rows in by_delay.items()}
            cr = [r for r in by_delay['1h'] if (r['mid'], r['wallet'], r['sig_ts']) in common]
            row['leader_common_mean_ret'] = (sum(r['stake'] * r['leader'] for r in cr) / sum(r['stake'] for r in cr)) if cr else None
            row['common_signals'] = len(common)
            res['secondary_hist']['decay_' + label] = row

    # decay: the same signals at the leader's fill, +5m (reference), +1h, +1d
    dec = {}
    for label, v in (('chosen', chv), ('all_wallets', ('edge', 'all_wallets', 'all', 50, 'hold'))):
        by_delay = {d: variant_rows(signals, sels, v[0], v[1], v[2], v[3], 'hold', d) for d in DELAYS}
        common = set.intersection(*[{(r['mid'], r['wallet'], r['sig_ts']) for r in by_delay[d]} for d in DELAYS])
        row = {}
        for d, rows in by_delay.items():
            cr = [r for r in rows if (r['mid'], r['wallet'], r['sig_ts']) in common]
            row[d] = {'all': rows_summary(rows), 'common': rows_summary(cr)}
        cr = [r for r in by_delay['1h'] if (r['mid'], r['wallet'], r['sig_ts']) in common]
        row['leader_common_mean_ret'] = (sum(r['stake'] * r['leader'] for r in cr) / sum(r['stake'] for r in cr)) if cr else None
        row['common_signals'] = len(common)
        dec[label] = row
    res['decay'] = dec

    # capacity at the chosen variant (test half and the whole test window)
    span_oos = max(1.0, (d_hi + 1) * DAY - split_ts) / DAY
    span_all = float(n_days)
    res['capacity'] = {'oos': capacity_of(oos, tbl, markets, span_oos),
                       'all_test_window': capacity_of(rows_ch, tbl, markets, span_all)}

    # who the skilled wallets are: top 50 by formation edge t at the cutoff, and the chosen variant's wallets
    rf = ranked(F, 't')
    top = [w for _, w in sorted(((r['t'], w) for w, r in rf.items()), reverse=True)[:50]]
    res['skilled_wallets_top50'] = describe_wallets(F, T, top, signals, markets)
    chosen_wallets = sorted({r['wallet'] for r in rows_ch})
    res['chosen_wallets'] = describe_wallets(F, T, chosen_wallets[:200], signals, markets)

    n_hist = len(res.get('secondary_hist', {}).get('variants', {}))
    n_tried = len(grid_names()) + len(base) + len(grid_1d) + n_hist
    res['variants_tried'] = {'protocol_grid_1h': len(grid_names()), 'baselines_1h': len(base),
                             'grid_1d_reported': len(grid_1d), 'secondary_hist_1h': n_hist, 'total': n_tried}
    go = (proto['in_sample_positive'] and (proto['oos_t'] or 0) >= 2 and ch in proto['bh_survivors_positive']
          and (res['capacity']['oos'].get('usd_per_year') or 0) > 0)
    res['go'] = {'in_sample_positive': proto['in_sample_positive'], 'oos_t': proto['oos_t'],
                 'chosen_in_bh_positive': ch in proto['bh_survivors_positive'],
                 'usd_per_year_oos': res['capacity']['oos'].get('usd_per_year'), 'go': bool(go)}
    other = out / 'analysis_volume_sample.json'
    if args.mode == 'events' and other.exists():
        b = json.loads(other.read_text())
        c3 = out / 'analysis_events_sampled_only.json'
        c3 = json.loads(c3.read_text()) if c3.exists() else None

        def brief(x):
            if not x:
                return None
            return {'calibration_negrisk_0.50': x['calibration_by_type'].get('negrisk|0.50'),
                    'calibration_all_0.50': x['calibration_by_type'].get('all|0.50'),
                    'share_formation_t_ge_2': x['persistence'].get('share_formation_t_ge_2_t'),
                    'share_formation_t_le_-2': x['persistence'].get('share_formation_t_le_-2_t'),
                    'spearman_edge_t': x['persistence'].get('spearman_edge_t'),
                    'top50_test_edge': x['persistence']['topk_by_edge']['top50']['test_edge'],
                    'top100_test_edge': x['persistence']['topk_by_edge']['top100']['test_edge'],
                    'all_takers_formation': x['all_takers']['formation'].get('all'),
                    'protocol_chosen': x['protocol']['chosen'], 'protocol_oos_t': x['protocol']['oos_t'],
                    'markets': x['sample']['markets'], 'go': x['go']}
        res['bias_comparison'] = {'events_sampled_only': brief(c3),
            'note': 'the same pipeline on the volume-drawn sample (analysis_volume_sample.json) against this '
                    'event-complete set',
            'volume_sample': {'calibration_negrisk_0.50': b['calibration_by_type'].get('negrisk|0.50'),
                              'calibration_all_0.50': b['calibration_by_type'].get('all|0.50'),
                              'share_formation_t_ge_2': b['persistence'].get('share_formation_t_ge_2_t'),
                              'share_formation_t_le_-2': b['persistence'].get('share_formation_t_le_-2_t'),
                              'spearman_edge_t': b['persistence'].get('spearman_edge_t'),
                              'top50_test_edge': b['persistence']['topk_by_edge']['top50']['test_edge'],
                              'top100_test_edge': b['persistence']['topk_by_edge']['top100']['test_edge'],
                              'all_takers_formation': b['all_takers']['formation'].get('all'),
                              'protocol_chosen': b['protocol']['chosen'], 'protocol_oos_t': b['protocol']['oos_t'],
                              'go': b['go']},
            'event_complete': {'calibration_negrisk_0.50': res['calibration_by_type'].get('negrisk|0.50'),
                               'calibration_all_0.50': res['calibration_by_type'].get('all|0.50'),
                               'share_formation_t_ge_2': pers.get('share_formation_t_ge_2_t'),
                               'share_formation_t_le_-2': pers.get('share_formation_t_le_-2_t'),
                               'spearman_edge_t': pers.get('spearman_edge_t'),
                               'top50_test_edge': pers['topk_by_edge']['top50']['test_edge'],
                               'top100_test_edge': pers['topk_by_edge']['top100']['test_edge'],
                               'all_takers_formation': res['all_takers']['formation'].get('all'),
                               'protocol_chosen': res['protocol']['chosen'], 'protocol_oos_t': res['protocol']['oos_t'],
                               'go': res['go']}}
    res['seconds'] = round(time.time() - t0, 1)
    P.write_json(out / {'events': 'analysis.json', 'sample': 'analysis_volume_sample.json',
                        'events_sampled_only': 'analysis_events_sampled_only.json'}[args.mode], res)
    print(json.dumps({'chosen': ch, 'go': res['go'], 'seconds': res['seconds']}, indent=1))
    return 0


# ------------------------------------------------------------------------------------------------ render

def f_pct(x, d=1):
    return '-' if x is None else ('%.*f%%' % (d, 100.0 * x))


def f_num(x, d=2):
    return '-' if x is None else ('%.*f' % (d, x))


def f_usd(x):
    return '-' if x is None else '${:,.0f}'.format(x)


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_wallet_skill tables (%s)' % a['generated'], '',
         'Every number is in `analysis.json`; keys are given in brackets.', '']
    s = a['sample']
    L += ['## Sample [sample]', '',
          '| markets | formation (closed < %s) | test | taker trades >= $50 | wallets | universe markets represented |'
          % a['cutoff'][:10], '|---:|---:|---:|---:|---:|---:|',
          '| %d | %d | %d | %d | %d | %.0f |' % (s['markets'], s['formation_markets'], s['test_markets'], s['trades'],
                                              s['wallets'], s['universe_markets_represented']), '']
    L += ['## Selection check: YES rate against the midpoint by market type [calibration_by_type]', '',
          'Mode: %s. A volume-drawn sample over-represents the winners of multi-outcome events.' % a.get('mode'), '',
          '| type at life fraction | n | mean price of YES | YES rate | excess | s.e. |', '|---|---:|---:|---:|---:|---:|']
    for k in sorted(a.get('calibration_by_type', {})):
        r = a['calibration_by_type'][k]
        L.append('| %s | %d | %.3f | %.3f | %+.3f | %.3f |' % (k, r['n'], r['mean_price0'], r['yes_rate'], r['excess'], r['se']))
    if a.get('bias_comparison'):
        bc = a['bias_comparison']
        L += ['', '## The volume-selection bias: same pipeline, three market sets [bias_comparison]', '',
              '| measure | volume-drawn sample | same events, drawn members only | event-complete (primary) |',
              '|---|---:|---:|---:|']
        cols = [bc.get('volume_sample') or {}, bc.get('events_sampled_only') or {}, bc.get('event_complete') or {}]

        def g(c, path):
            v = c
            for k in path:
                v = (v or {}).get(k) if isinstance(v, dict) else None
            return v
        for lab, path, fmt in (('neg-risk YES excess at mid-life', ('calibration_negrisk_0.50', 'excess'), 'pp'),
                               ('all-market YES excess at mid-life', ('calibration_all_0.50', 'excess'), 'pp'),
                               ('share of formation wallets with t >= 2', ('share_formation_t_ge_2',), 'pct'),
                               ('share with t <= -2', ('share_formation_t_le_-2',), 'pct'),
                               ('Spearman of formation vs test t', ('spearman_edge_t',), 'num'),
                               ('top-50 test edge per $', ('top50_test_edge', 'edge_per_usd'), 'pct'),
                               ('top-100 test edge per $', ('top100_test_edge', 'edge_per_usd'), 'pct'),
                               ('all takers formation edge per $', ('all_takers_formation', 'edge_per_usd'), 'pct'),
                               ('protocol OOS t (chosen)', ('protocol_oos_t',), 'num')):
            vals = []
            for c in cols:
                v = g(c, path)
                vals.append('-' if v is None else ('%+.1fpp' % (100 * v) if fmt == 'pp' else
                                                   (f_pct(v, 2) if fmt == 'pct' else f_num(v))))
            L.append('| %s | %s | %s | %s |' % (lab, vals[0], vals[1], vals[2]))
        L.append('')
    L += ['## What taking costs: all takers pooled [all_takers]', '',
          '| category | formation edge/$ | t | test edge/$ | t | test +1h markout/$ |', '|---|---:|---:|---:|---:|---:|']
    for cat in sorted(a['all_takers']['test'], key=lambda c: -a['all_takers']['test'][c]['usd']):
        fo = a['all_takers']['formation'].get(cat, {})
        te = a['all_takers']['test'][cat]
        L.append('| %s | %s | %s | %s | %s | %s |' % (cat, f_pct(fo.get('edge_per_usd'), 2), f_num(fo.get('t')),
                                                    f_pct(te['edge_per_usd'], 2), f_num(te['t']),
                                                    f_pct(te['mk1h_per_usd'], 2)))
    p = a['persistence']
    L += ['', '## Persistence, formation (markets closed before the cutoff) vs test (trades after it) [persistence]', '',
          '| measure | value |', '|---|---:|']
    for k in ('ranked_formation_t', 'ranked_both_t', 'share_formation_t_ge_2_t', 'share_formation_t_le_-2_t',
              'spearman_edge_value', 'spearman_edge_t', 'ranked_both_t1d', 'spearman_mk1d_value', 'spearman_mk1d_t',
              'spearman_formation_mk1d_vs_test_edge'):
        v = p.get(k)
        L.append('| %s | %s |' % (k, f_num(v, 3) if isinstance(v, float) else v))
    for label in ('edge', 'mk1d'):
        tk = p['topk_by_%s' % label]
        L += ['', 'Top-k by formation %s t: their pooled test-period trades [persistence.topk_by_%s]' % (label, label), '',
              '| group | formation t >= | active in test | test edge/$ | t | test +1h mk/$ | test +1d mk/$ | markets |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        for k in TOPK:
            r = tk['top%d' % k]
            L.append('| top %d | %s | %d | %s | %s | %s | %s | %d |' % (
                k, f_num(r['formation_t_min']), r['active_in_test'], f_pct(r['test_edge']['edge_per_usd'], 2),
                f_num(r['test_edge']['t']), f_pct(r['test_mk1h']['edge_per_usd'], 2),
                f_pct(r['test_mk1d']['edge_per_usd'], 2), r['test_edge']['markets']))
        for k in TOPK:
            r = tk['bottom%d' % k]
            L.append('| bottom %d | | | %s | %s | | | %d |' % (k, f_pct(r['test_edge']['edge_per_usd'], 2),
                                                             f_num(r['test_edge']['t']), r['test_edge']['markets']))
        L += ['', '| formation decile | wallets | t range | test edge/$ | t | markets |', '|---:|---:|---|---:|---:|---:|']
        for d in tk['deciles']:
            L.append('| %d | %d | %s to %s | %s | %s | %d |' % (d['decile'], d['wallets'], f_num(d['t_hi']),
                                                            f_num(d['t_lo']), f_pct(d['test_edge']['edge_per_usd'], 2),
                                                            f_num(d['test_edge']['t']), d['test_edge']['markets']))
    pr = a['protocol']
    L += ['', '## Follower protocol at +1h [protocol, variants_1h]', '',
          'Series %s to %s, split %s; %d variants.' % (a['series']['first_day'], a['series']['last_day'],
                                                     a['series']['split_day'], pr['n_variants']), '',
          '| chosen | in-sample Sharpe | in-sample ann | OOS ann | OOS HAC t | OOS rank | deflated Sharpe | '
          'BH positive survivors |', '|---|---:|---:|---:|---:|---:|---:|---:|',
          '| %s | %s | %s | %s | %s | %d | %s | %d |' % (
              pr['chosen'], f_num(pr['in_sample'].get('sharpe')), f_pct(pr['in_sample'].get('ann_return')),
              f_pct(pr['out_of_sample'].get('ann_return')), f_num(pr['oos_t']), pr['oos_rank'],
              f_num(pr['deflated_sharpe_in_sample']), len(pr['bh_survivors_positive'])), '']
    L += ['| variant | signals | in: mean ret | in: ann excess | OOS: signals | OOS mean ret | OOS ann excess | '
          'OOS t (mkt) | leader own ret (OOS) |', '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    vs = a['variants_1h']
    L += ['Top 15 by out-of-sample market-clustered t among variants with at least 20 OOS signals, then the chosen one '
          '(annualised figures are on short holds and mean little; the t-statistics carry the test).', '']
    order = sorted([k for k in vs if vs[k]['oos'].get('n', 0) >= 20],
                   key=lambda k: -(vs[k]['oos'].get('t_market_clustered') or -9))
    for k in order[:15] + ([pr['chosen']] if pr['chosen'] not in order[:15] else []):
        v = vs[k]
        L.append('| %s | %d | %s | %s | %d | %s | %s | %s | %s |' % (
            k, v['all']['n'], f_pct(v['in'].get('mean_ret'), 2), f_pct(v['in'].get('ann_excess')), v['oos']['n'],
            f_pct(v['oos'].get('mean_ret'), 2), f_pct(v['oos'].get('ann_excess')), f_num(v['oos'].get('t_market_clustered')),
            f_pct(v['oos'].get('leader_mean_ret'), 2)))
    L += ['', '## Baselines at +1h [baselines_1h]', '', '| baseline | signals | mean ret | ann excess | t (mkt) | OOS mean ret |',
          '|---|---:|---:|---:|---:|---:|']
    for k, v in a['baselines_1h'].items():
        L.append('| %s | %d | %s | %s | %s | %s |' % (k, v['all']['n'], f_pct(v['all'].get('mean_ret'), 2),
                                                      f_pct(v['all'].get('ann_excess')), f_num(v['all'].get('t_market_clustered')),
                                                      f_pct(v['oos'].get('mean_ret'), 2)))
    L += ['', '## Late-entry decay on common signals [decay]', '',
          '| selection | common signals | leader own fill | +5m (reference) | +1h | +1d |', '|---|---:|---:|---:|---:|---:|']
    for label, d in a['decay'].items():
        L.append('| %s | %d | %s | %s | %s | %s |' % (label, d['common_signals'], f_pct(d['leader_common_mean_ret'], 2),
                                                      f_pct(d['5m']['common'].get('mean_ret'), 2),
                                                      f_pct(d['1h']['common'].get('mean_ret'), 2),
                                                      f_pct(d['1d']['common'].get('mean_ret'), 2)))
    ch = a['chosen']
    L += ['', '## The chosen variant, weighted and unweighted [chosen]', '',
          '| part | signals | events | mean ret | t (market) | t (event) | hit rate | leader own ret |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k in ('in', 'oos', 'unweighted_all', 'unweighted_oos'):
        r = ch[k]
        if r.get('n'):
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (k, r['n'], r.get('events', '-'), f_pct(r['mean_ret'], 2),
                                                                f_num(r.get('t_market_clustered')),
                                                                f_num(r.get('t_event_clustered')), f_pct(r.get('hit_rate')),
                                                                f_pct(r.get('leader_mean_ret'), 2)))
    c = a['capacity']
    L += ['', '## Capacity at the chosen variant [capacity]', '', '| window | signals | universe signals/yr | median fill | '
          'median same-side flow +-1h | avg capital | $/yr over SSR |', '|---|---:|---:|---:|---:|---:|---:|']
    for k in ('oos', 'all_test_window'):
        r = c[k]
        if r.get('signals'):
            L.append('| %s | %d | %.0f | %s | %s | %s | %s |' % (k, r['signals'], r['universe_signals_per_year'],
                                                                f_usd(r['median_fill_usd']),
                                                                f_usd(r['median_same_side_flow_usd_2h']),
                                                                f_usd(r['avg_capital_usd']), f_usd(r['usd_per_year'])))
    L += ['', '## Who the top formation wallets are [skilled_wallets_top50]', '',
          '| wallet | markets | $ | edge/$ | t | +1h mk/$ | +1d mk/$ | main cat (share) | two-sided | sell share | '
          'test edge/$ | test mkts | median signal $ | median hold d |', '|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|']
    for r in a['skilled_wallets_top50'][:20]:
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s | %d | %s | %s |' % (
            r['wallet'][:10], r['formation_markets'], f_usd(r['formation_usd']), f_pct(r['formation_edge']),
            f_num(r['formation_t']), f_pct(r['formation_mk1h']), f_pct(r['formation_mk1d']), r['main_cat'],
            f_pct(r['main_cat_share'], 0), f_pct(r['two_sided_share'], 0), f_pct(r['sell_share'], 0),
            f_pct(r['test_edge']), r['test_markets'], f_usd(r['median_signal_usd']), f_num(r['median_hold_days'], 1)))
    for hk in ('hist_persistence', 'hist_persistence_incl_sets_biased'):
        if not a.get(hk):
            continue
        h = a[hk]
        L += ['', '### %s' % hk]
        L += ['', '## Stage 2: full taker histories of the %d most active formation wallets [hist_persistence]' % h['wallets'],
              '', 'Formation = universe markets closed before the cutoff; test = trades after it in markets scheduled to '
              'end before 2026-10-01.', '', '| measure | value |', '|---|---:|']
        for k in ('ranked_formation', 'ranked_both', 'share_formation_t_ge_2', 'spearman_edge_value', 'spearman_edge_t'):
            v = h.get(k)
            L.append('| %s | %s |' % (k, f_num(v, 3) if isinstance(v, float) else v))
        L += ['', '| group | formation t >= | active in test | test edge/$ | t (market-clustered) | markets |',
              '|---|---:|---:|---:|---:|---:|']
        for k in TOPK:
            for lab in ('top', 'bottom'):
                r = h['%s%d' % (lab, k)]
                L.append('| %s %d | %s | %d | %s | %s | %d |' % (lab, k, f_num(r.get('formation_t_min')), r['active_in_test'],
                                                               f_pct(r['test_edge_per_usd'], 2), f_num(r['t']), r['markets']))
        L += ['', '| formation decile | wallets | t range | test edge/$ | t |', '|---:|---:|---|---:|---:|']
        for d in h['deciles']:
            L.append('| %d | %d | %s to %s | %s | %s |' % (d['decile'], d['wallets'], f_num(d['t_hi']), f_num(d['t_lo']),
                                                         f_pct(d['test_edge_per_usd'], 2), f_num(d['t'])))
    if a.get('secondary_hist'):
        sh = a['secondary_hist']
        L += ['', '## Secondary protocol: selection on full histories [secondary_hist]', '',
              '| run | variants | chosen | in-sample ann | OOS ann | OOS HAC t | OOS rank | BH positive survivors |',
              '|---|---:|---|---:|---:|---:|---:|---:|']
        for k in ('protocol_hist_only', 'protocol_pooled_108'):
            q = sh[k]
            L.append('| %s | %d | %s | %s | %s | %s | %d | %d |' % (
                k, q['n_variants'], q['chosen'], f_pct(q['in_sample'].get('ann_return')),
                f_pct(q['out_of_sample'].get('ann_return')), f_num(q['oos_t']), q['oos_rank'],
                len(q['bh_survivors_positive'])))
        L += ['', '| hist variant | signals | mean ret | OOS signals | OOS mean ret | OOS ann excess | OOS t (mkt) | OOS t (event) |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        for k, v in sorted(sh['variants'].items(), key=lambda kv: -(kv[1]['oos'].get('t_market_clustered') or -9)):
            L.append('| %s | %d | %s | %d | %s | %s | %s | %s |' % (
                k, v['all']['n'], f_pct(v['all'].get('mean_ret'), 2), v['oos']['n'], f_pct(v['oos'].get('mean_ret'), 2),
                f_pct(v['oos'].get('ann_excess')), f_num(v['oos'].get('t_market_clustered')),
                f_num(v['oos'].get('t_event_clustered'))))
        for k in [x for x in sh if x.startswith('decay_')]:
            d = sh[k]
            L += ['', '%s: common signals %d; leader %s, +5m %s, +1h %s, +1d %s [secondary_hist.%s]' % (
                k, d['common_signals'], f_pct(d['leader_common_mean_ret'], 2), f_pct(d['5m']['common'].get('mean_ret'), 2),
                f_pct(d['1h']['common'].get('mean_ret'), 2), f_pct(d['1d']['common'].get('mean_ret'), 2), k)]
    vt = a['variants_tried']
    L += ['', '## Variants tried [variants_tried]', '', '| family | count |', '|---|---:|']
    for k, v in vt.items():
        L.append('| %s | %d |' % (k, v))
    L += ['', '## Go rule [go]', '', '```', json.dumps(a['go'], indent=1), '```', '']
    (out / 'tables.md').write_text('\n'.join(L))
    entries = []
    if a['go']['go']:
        c = a['capacity']['oos']
        entries.append({
            'id': 'pm-wallet-follow', 'name': 'Copy skilled Polymarket wallets an hour late', 'kind': 'prediction_market',
            'status': 'proposed', 'thesis': 'see research/2026-10-14/pm_wallet_skill', 'mechanism': 'informed wallets',
            'legs': ["buy the selected wallets' new taker buys at the next hourly mark, hold to resolution"],
            'capacity_usd': c['avg_capital_usd'], 'capital_days': None, 'kill_criteria': [],
            'quotes': [{'at': a['generated'], 'source': 'history', 'window': 'research/2026-10-14/pm_wallet_skill',
                        'net_apr': c['ann_excess_on_capital'], 'usd': c['usd_per_year'], 'go': True, 'present': False,
                        'note': a['protocol']['chosen']}],
            'risks': ['wallet churn'], 'evidence': ['research/2026-10-14/pm_wallet_skill/analysis.json']})
    P.write_json(out / 'book_entries.json', entries)
    print('tables.md and book_entries.json written (%d entries)' % len(entries))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('cmd', choices=['sample', 'collect', 'books', 'events', 'members', 'wallets', 'analyze', 'render'])
    ap.add_argument('--min-member-volume', type=float, default=1000.0)
    ap.add_argument('--mode', choices=['events', 'events_sampled_only', 'sample'], default='events')
    ap.add_argument('--n-wallets', type=int, default=HIST_N)
    ap.add_argument('--out', default=str(ROOT / 'research' / '2026-10-14' / 'pm_wallet_skill'))
    ap.add_argument('--interval', type=float, default=0.25)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--price-workers', type=int, default=3)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--max-pages', type=int, default=150)
    a = ap.parse_args()
    return {'sample': cmd_sample, 'collect': cmd_collect, 'books': cmd_books, 'events': cmd_events,
            'members': cmd_members, 'wallets': cmd_wallets,
            'analyze': cmd_analyze, 'render': cmd_render}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
