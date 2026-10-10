#!/usr/bin/env python3
"""Token unlocks against the perpetual that can be shorted into them: is there still a drift, and does it pay the funding?

Why. A scheduled cliff unlock to insiders or early investors is the most predictable supply event in crypto: its date
and size are published months ahead. The folklore is that prices drift down into large insider unlocks; if the market
has learned that, the drift is gone or the perp funding charges shorts for it. Both can be measured: DefiLlama's
public dataset bucket (`defillama-datasets.llama.fi`) carries every documented cliff with its category and token
count, and perp_history's store holds a year of hourly Hyperliquid prices and funding for every core perp — the
instrument a trader would actually use, with its actual carry.

Identity. A DefiLlama token is matched to a Hyperliquid perp by symbol, and the match is kept only if the two prices
agree within 25% now (DefiLlama's `tokenPrice` against the perp's mark), which removes symbol collisions without a
hand list. Hyperliquid's thousand-unit tickers (kPEPE, kBONK, ...) are compared at 1000x.

Event. A cliff whose allocation category is `insiders` or `privateSale` (the holders who sell; `airdrop` is reported
separately), sized against the supply already unlocked on that day (DefiLlama's documented cumulative unlock curve).
Several allocations on the same token and day are one event.

Measurement, per event and window [T+a, T+b] (days): the perp's log return less the same window of BTC's (a beta-one
hedge; the estimated beta is reported beside it), and the funding a short would have received (Hyperliquid funding
is positive when longs pay, so a short receives +rate each hour) less what the BTC long paid. The trade is short the
coin and long BTC at T+a, closed at T+b; its P&L is -abnormal return + funding legs - two round trips.

Protocol. The window (a, b) and the minimum size are chosen on events before the cutoff (default 2026-04-01) and
tested on events after it, through the same backtest harness every study here uses; every variant tried is counted.

    uv run python scripts/unlock_study.py collect --out research/2026-10-09/unlocks
    uv run python scripts/unlock_study.py prices  --out research/2026-10-09/unlocks    # 4h bars before the 1h store
    uv run python scripts/unlock_study.py analyze --out research/2026-10-09/unlocks --hl research/2026-10-09/perps_history
    uv run python scripts/unlock_study.py render  --out research/2026-10-09/unlocks
    uv run python scripts/unlock_study.py upcoming --out research/2026-10-09/unlocks   # the forward test's calendar
"""
import argparse
import bisect
import datetime as dt
import gzip
import json
import math
import statistics
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
BASE = 'https://defillama-datasets.llama.fi/'
UA = 'Mozilla/5.0'
SELLER_CATEGORIES = {'insiders', 'privateSale'}
DEFAULT_RT_BPS = 12.0          # one core-perp round trip at $100k (09-10 window: ADA 20bp, LINK 21bp, SOL 12.6bp)
BTC_RT_BPS = 9.1               # BTC at $100k, 2026-09-10


def get_json(url, retries=4, pause=0.4):
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read().decode())
            time.sleep(pause)
            return d
        except Exception as e:  # noqa: BLE001 - retried, then raised with context
            last = repr(e)[:160]
            time.sleep(pause * 2 ** (a + 1))
    raise RuntimeError('%s: %s' % (url, last))


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def safe(coin):
    return coin.replace(':', '__').replace('/', '_')


def utc_iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).isoformat()


# ------------------------------------------------------------------------------------------------ identity

def hl_symbol_scale(coin):
    """('PEPE', 1000) for Hyperliquid's kPEPE; (coin, 1) otherwise."""
    if len(coin) > 1 and coin[0] == 'k' and coin[1:].isupper():
        return coin[1:], 1000.0
    return coin, 1.0


def match_tokens(index_rows, hl_universe, tol=0.25):
    """{hl coin: index row} for symbols that also agree on price within `tol` (relative)."""
    by_sym = {}
    for p in index_rows:
        tp = (p.get('tokenPrice') or [{}])[0]
        sym, px = (tp.get('symbol') or '').upper(), tp.get('price')
        if sym and px:
            by_sym.setdefault(sym, []).append((p, float(px)))
    out, rejected = {}, []
    for m in hl_universe:
        if m.get('dex') != 'core' or not m.get('mark'):
            continue
        sym, scale = hl_symbol_scale(m['coin'])
        for p, px in by_sym.get(sym.upper(), []):
            ratio = (float(m['mark']) / scale) / px
            if abs(ratio - 1.0) <= tol:
                out[m['coin']] = p
                break
        else:
            if sym.upper() in by_sym:
                rejected.append(m['coin'])
    return out, rejected


# ------------------------------------------------------------------------------------------------ events

def unlocked_on(documented, ts):
    """Cumulative unlocked tokens on day `ts` (seconds), summed over every documented allocation."""
    total = 0.0
    for alloc in (documented or {}).get('data') or []:
        pts = alloc.get('data') or []
        if not pts:
            continue
        keys = [p['timestamp'] for p in pts]
        i = bisect.bisect_right(keys, ts) - 1
        if i >= 0:
            total += float(pts[i].get('unlocked') or 0.0)
    return total


def cliff_events(protocol_file, categories=SELLER_CATEGORIES):
    """Cliff unlocks in `categories`, merged by UTC day: [{'ts', 'tokens', 'categories'}]."""
    days = {}
    for e in ((protocol_file.get('metadata') or {}).get('events') or []):
        if e.get('unlockType') != 'cliff' or e.get('category') not in categories:
            continue
        ts = int(e['timestamp'])
        d = ts - ts % 86400
        x = days.setdefault(d, {'ts': ts, 'tokens': 0.0, 'categories': set()})
        x['tokens'] += sum(float(v or 0) for v in (e.get('noOfTokens') or []))
        x['categories'].add(e['category'])
        x['ts'] = min(x['ts'], ts)
    return [{'ts': v['ts'], 'tokens': v['tokens'], 'categories': sorted(v['categories'])} for _, v in sorted(days.items())]


# ------------------------------------------------------------------------------------------------ prices

def series(hl_dir, coin, extra_4h=None):
    """(sorted bar-end ms list, {ms: close}, {ms: funding rate}) from perp_history's store, or None.

    Hyperliquid's candleSnapshot serves only the most recent 5000 bars, so the store's 1h closes begin about 208 days
    before collection (2026-03-15 for this store) while its funding goes back the full year. `extra_4h` is a directory
    of 4h candles (`prices`) that fills the earlier months; where both exist the 1h close wins.
    """
    hl = Path(hl_dir)
    cp, fp = hl / 'candles_1h' / (safe(coin) + '.json.gz'), hl / 'funding' / (safe(coin) + '.json.gz')
    if not cp.exists() or not fp.exists():
        return None
    closes = {}
    if extra_4h:
        xp = Path(extra_4h) / (safe(coin) + '.json.gz')
        if xp.exists():
            closes.update({int(c['t']) + 4 * HOUR_MS: float(c['c']) for c in read_gz(xp)})
    closes.update({int(c['t']) + HOUR_MS: float(c['c']) for c in read_gz(cp)})
    fund = {int((int(r['time']) + HOUR_MS // 2) // HOUR_MS * HOUR_MS): float(r['fundingRate']) for r in read_gz(fp)}
    return sorted(closes), closes, fund


def price_at(s, t, max_age_ms=6 * HOUR_MS):
    keys, closes, _ = s
    i = bisect.bisect_right(keys, t) - 1
    if i < 0 or t - keys[i] > max_age_ms:
        return None
    return closes[keys[i]]


def funding_sum(s, t0, t1):
    """Sum of hourly funding rates paid in (t0, t1]; positive = longs paid shorts."""
    _, _, fund = s
    return sum(v for k, v in fund.items() if t0 < k <= t1)


def window_trade(coin_s, btc_s, T, a, b, rt_bps=DEFAULT_RT_BPS, btc_rt_bps=BTC_RT_BPS):
    """Short the coin and long BTC from T+a days to T+b days. Returns None if a price is missing."""
    t0, t1 = T + a * DAY_MS, T + b * DAY_MS
    c0, c1 = price_at(coin_s, t0), price_at(coin_s, t1)
    b0, b1 = price_at(btc_s, t0), price_at(btc_s, t1)
    if None in (c0, c1, b0, b1):
        return None
    ar = math.log(c1 / c0) - math.log(b1 / b0)
    f_coin = funding_sum(coin_s, t0, t1)          # the short receives this
    f_btc = funding_sum(btc_s, t0, t1)            # the BTC long pays this
    cost = (rt_bps + btc_rt_bps) / 1e4
    return {'abnormal': ar, 'coin_return': math.log(c1 / c0), 'btc_return': math.log(b1 / b0),
            'funding_short_received': f_coin, 'funding_btc_long_paid': f_btc, 'cost': cost,
            'pnl': -ar + f_coin - f_btc - cost}


def beta(coin_s, btc_s, T, days=60):
    """OLS beta of daily coin log returns on BTC's over the `days` before T (None when too few)."""
    xs, ys = [], []
    for d in range(days, 0, -1):
        t0, t1 = T - (d + 1) * DAY_MS, T - d * DAY_MS
        c0, c1, b0, b1 = price_at(coin_s, t0), price_at(coin_s, t1), price_at(btc_s, t0), price_at(btc_s, t1)
        if None in (c0, c1, b0, b1):
            continue
        xs.append(math.log(b1 / b0))
        ys.append(math.log(c1 / c0))
    if len(xs) < 20:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx if vx > 0 else None


# ------------------------------------------------------------------------------------------------ commands

def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    idx = get_json(BASE + 'emissionsIndex')
    (raw / 'emissions_index.json').write_text(json.dumps(idx))
    rows = idx.get('data') or []
    uni = json.loads((Path(args.hl) / 'universe.json').read_text())['markets']
    matched, rejected = match_tokens(rows, uni)
    got = {}
    for coin, p in sorted(matched.items()):
        slug = p.get('protocolSlug') or p.get('protocolId')
        fn = raw / 'emissions' / ('%s.json' % slug)
        if not fn.exists():
            fn.parent.mkdir(parents=True, exist_ok=True)
            try:
                fn.write_text(json.dumps(get_json(BASE + 'emissions/' + slug)))
            except RuntimeError as e:
                got[coin] = {'slug': slug, 'error': str(e)[:160]}
                continue
        got[coin] = {'slug': slug}
    write_json(out / 'manifest.json', {'collected_at': dt.datetime.now(UTC).isoformat(), 'source': BASE,
                                       'index_rows': len(rows), 'matched': got, 'rejected_on_price': rejected,
                                       'hl_universe': str(Path(args.hl) / 'universe.json'),
                                       'seconds': round(time.time() - t0, 1)})
    print(json.dumps({'index_rows': len(rows), 'matched': len(got), 'rejected_on_price': rejected}))
    return 0


def cmd_prices(args):
    """4h Hyperliquid candles for every matched coin and BTC over the months the 1h store does not reach."""
    from perp_rpc import Info, APIError, candles
    out = Path(args.out)
    man = json.loads((out / 'manifest.json').read_text())
    dst = out / 'raw' / 'candles_4h'
    dst.mkdir(parents=True, exist_ok=True)
    api = Info(interval=args.interval)
    s_ms = int(dt.datetime.fromisoformat(args.since).replace(tzinfo=UTC).timestamp() * 1000)
    e_ms = int(dt.datetime.fromisoformat(args.until).replace(tzinfo=UTC).timestamp() * 1000)
    coins = ['BTC'] + sorted(c for c, m in man['matched'].items() if 'error' not in m and c != 'BTC')
    done, failed = 0, {}
    for c in coins:
        fn = dst / (safe(c) + '.json.gz')
        if fn.exists():
            done += 1
            continue
        try:
            rows = candles(api, c, '4h', s_ms, e_ms) or []
        except APIError as e:
            failed[c] = str(e)[:120]
            continue
        with gzip.open(fn, 'wt') as f:
            json.dump(rows, f)
        done += 1
    man['candles_4h'] = {'since': args.since, 'until': args.until, 'coins': done, 'failed': failed, 'api': api.stats()}
    write_json(out / 'manifest.json', man)
    print(json.dumps(man['candles_4h']))
    return 0


def build_events(out, hl, categories):
    man = json.loads((out / 'manifest.json').read_text())
    x4 = out / 'raw' / 'candles_4h'
    btc = series(hl, 'BTC', x4)
    events = []
    for coin, m in sorted(man['matched'].items()):
        if 'error' in m:
            continue
        fn = out / 'raw' / 'emissions' / ('%s.json' % m['slug'])
        if not fn.exists():
            continue
        pf = json.loads(fn.read_text())
        s = series(hl, coin, x4)
        if not s:
            continue
        first, last = s[0][0], s[0][-1]
        for e in cliff_events(pf, categories):
            T = e['ts'] * 1000
            if not (first + 14 * DAY_MS <= T <= last - 1 * DAY_MS):
                continue
            unlocked = unlocked_on(pf.get('documentedData'), e['ts'] - 1)
            events.append({'coin': coin, 'slug': m['slug'], 'T': T, 'utc': utc_iso(T), 'tokens': e['tokens'],
                           'categories': e['categories'], 'unlocked_before': unlocked,
                           'size_of_unlocked': (e['tokens'] / unlocked) if unlocked else None,
                           'beta_60d': beta(s, btc, T)})
    return events, btc


def coin_round_trips(window_analysis, key='round_trip_bps_100k'):
    """{coin: round trip bps} for core perps priced in a perp window (perp_scan analyze); {} if none."""
    p = Path(window_analysis) if window_analysis else None
    if not p or not p.exists():
        return {}
    A = json.loads(p.read_text())
    return {r['coin']: (r.get('book') or {}).get(key) for r in A.get('assets', [])
            if ':' not in r['coin'] and (r.get('book') or {}).get(key) is not None}


def cmd_analyze(args):
    out, hl = Path(args.out), Path(args.hl)
    rts = coin_round_trips(args.rt_window)
    cut = int(dt.datetime.fromisoformat(args.cutoff).timestamp() * 1000)
    windows = [tuple(int(v) for v in w.split(':')) for w in args.windows.split(',')]
    sizes = [float(v) for v in args.sizes.split(',')]
    res = {'generated': dt.datetime.now(UTC).isoformat(), 'cutoff': args.cutoff, 'hl_store': str(hl),
           'windows': windows, 'sizes': sizes, 'round_trips_from': args.rt_window, 'coins_with_priced_round_trip': len(rts),
           'default_rt_bps': args.rt_bps}
    for label, cats in (('sellers', SELLER_CATEGORIES), ('airdrop', {'airdrop'})):
        events, btc = build_events(out, hl, cats)
        coin_series = {}
        trades = {}
        for (a, b) in windows:
            for e in events:
                if e['coin'] not in coin_series:
                    coin_series[e['coin']] = series(hl, e['coin'], out / 'raw' / 'candles_4h')
                tr = window_trade(coin_series[e['coin']], btc, e['T'], a, b, rt_bps=rts.get(e['coin'], args.rt_bps))
                if tr:
                    trades.setdefault((a, b), []).append((e, tr))
        # Placebo: the same coins and windows a fortnight before and after each event, skipped when another real
        # event of that coin is within a week. Alt-coins fell against BTC for much of this year, so shorting any of
        # them against BTC made money; the unlock is only an edge if it beats its own placebo.
        real_days = {}
        for e in events:
            real_days.setdefault(e['coin'], []).append(e['T'])
        placebo = {}
        for (a, b) in windows:
            for e in events:
                for shift in (-15, 15):
                    Tp = e['T'] + shift * DAY_MS
                    if any(abs(Tp - t) < 7 * DAY_MS for t in real_days[e['coin']]):
                        continue
                    tr = window_trade(coin_series[e['coin']], btc, Tp, a, b, rt_bps=rts.get(e['coin'], args.rt_bps))
                    if tr:
                        placebo.setdefault((a, b), []).append((e, Tp, tr))
        # variants: (window, minimum size); a variant's sample is its qualifying events in time order
        variants = []
        for (a, b), lst in trades.items():
            for smin in sizes:
                sel = [(e, tr) for e, tr in lst if (e['size_of_unlocked'] or 0) >= smin]
                ins = [tr['pnl'] for e, tr in sel if e['T'] < cut]
                oos = [tr['pnl'] for e, tr in sel if e['T'] >= cut]
                pl = [(e, Tp, tr) for e, Tp, tr in placebo.get((a, b), []) if (e['size_of_unlocked'] or 0) >= smin]
                p_in = [tr['pnl'] for e, Tp, tr in pl if Tp < cut]
                p_out = [tr['pnl'] for e, Tp, tr in pl if Tp >= cut]
                variants.append({'window': [a, b], 'min_size': smin, 'n_in': len(ins), 'n_out': len(oos),
                                 'mean_in': statistics.fmean(ins) if ins else None,
                                 'mean_out': statistics.fmean(oos) if oos else None,
                                 't_in': tstat(ins), 't_out': tstat(oos),
                                 'hit_out': (sum(1 for x in oos if x > 0) / len(oos)) if oos else None,
                                 'placebo_n_in': len(p_in), 'placebo_n_out': len(p_out),
                                 'placebo_mean_in': statistics.fmean(p_in) if p_in else None,
                                 'placebo_mean_out': statistics.fmean(p_out) if p_out else None,
                                 'excess_t_in': welch_t(ins, p_in), 'excess_t_out': welch_t(oos, p_out),
                                 # unlocks cluster on calendar dates (the 1st, the 15th) and share that week's market,
                                 # so a t across events overstates; this one averages by event day first
                                 't_out_by_day': tstat(by_day([(e['T'], tr['pnl']) for e, tr in sel if e['T'] >= cut])),
                                 'days_out': len({e['T'] // DAY_MS for e, tr in sel if e['T'] >= cut}),
                                 'by_quarter': quarters(sel, pl),
                                 'components_out': components([tr for e, tr in sel if e['T'] >= cut]),
                                 'components_in': components([tr for e, tr in sel if e['T'] < cut])})
        # chosen on the excess over placebo in sample: the claim is about unlocks, not about alt-coins against BTC
        eligible = [v for v in variants if v['n_in'] >= args.min_events and v['excess_t_in'] is not None]
        chosen = max(eligible, key=lambda v: v['excess_t_in']) if eligible else None
        pv = [pvalue(v['excess_t_in']) for v in variants]
        rej, adj = B.bh(pv, q=0.10)
        res[label] = {'events': len(events), 'events_before_cutoff': sum(1 for e in events if e['T'] < cut),
                      'events_after_cutoff': sum(1 for e in events if e['T'] >= cut),
                      'coins': sorted({e['coin'] for e in events}), 'variants': variants,
                      'n_variants': len(variants), 'chosen': chosen,
                      'bh_survivors_in_sample': [(v['window'], v['min_size']) for v, r in zip(variants, rej) if r],
                      'event_list': [{k: e[k] for k in ('coin', 'utc', 'tokens', 'categories', 'size_of_unlocked',
                                                        'beta_60d')} for e in events]}
        print(label, 'events', len(events), 'chosen', chosen and (chosen['window'], chosen['min_size'], chosen['n_in'],
                                                                 chosen['mean_in'], chosen['n_out'], chosen['mean_out']),
              flush=True)
    write_json(out / 'analysis.json', res)
    return 0


def tstat(x):
    if len(x) < 3:
        return None
    sd = statistics.stdev(x)
    return (statistics.fmean(x) / (sd / math.sqrt(len(x)))) if sd > 0 else None


def quarter_of(T):
    d = dt.datetime.fromtimestamp(T / 1000, UTC)
    return '%dQ%d' % (d.year, (d.month - 1) // 3 + 1)


def quarters(sel, placebo_rows):
    """Per calendar quarter: events, mean P&L, the placebo's mean, and the difference. Four quarters are four
    chances for a pattern to fail, which is a stronger test than one split when the split was chosen afterwards."""
    q = {}
    for e, tr in sel:
        q.setdefault(quarter_of(e['T']), {'pnl': [], 'placebo': []})['pnl'].append(tr['pnl'])
    for e, Tp, tr in placebo_rows:
        q.setdefault(quarter_of(Tp), {'pnl': [], 'placebo': []})['placebo'].append(tr['pnl'])
    out = {}
    for k in sorted(q):
        a, b = q[k]['pnl'], q[k]['placebo']
        out[k] = {'n': len(a), 'mean': statistics.fmean(a) if a else None,
                  'placebo_mean': statistics.fmean(b) if b else None,
                  'excess': (statistics.fmean(a) - statistics.fmean(b)) if (a and b) else None}
    return out


def by_day(pairs):
    """Mean of the values sharing a UTC day, one per day, in day order."""
    d = {}
    for T, v in pairs:
        d.setdefault(T // DAY_MS, []).append(v)
    return [statistics.fmean(v) for _, v in sorted(d.items())]


def welch_t(x, y):
    """Welch t of mean(x) - mean(y); None when either side has fewer than three observations."""
    if len(x) < 3 or len(y) < 3:
        return None
    vx, vy = statistics.variance(x) / len(x), statistics.variance(y) / len(y)
    if vx + vy <= 0:
        return None
    return (statistics.fmean(x) - statistics.fmean(y)) / math.sqrt(vx + vy)


def pvalue(t):
    if t is None:
        return None
    return 2.0 * (1.0 - statistics.NormalDist().cdf(abs(t)))


def components(trs):
    if not trs:
        return None
    return {k: statistics.fmean(t[k] for t in trs) for k in ('abnormal', 'funding_short_received',
                                                           'funding_btc_long_paid', 'cost', 'pnl')}


def pct(x, d=2):
    return '—' if x is None else '%+.*f%%' % (d, 100 * x)


def upcoming_rows(out, days, min_size, rt_window, now_s):
    """Seller cliffs in the next `days` on matched perps, at least `min_size` of the supply unlocked so far, with the
    entry time the pre-unlock rule implies (T - 3 days) and the coin's book from `rt_window`."""
    man = json.loads((out / 'manifest.json').read_text())
    rts = coin_round_trips(rt_window)
    depth = {}
    if rt_window and Path(rt_window).exists():
        W = json.loads(Path(rt_window).read_text())
        depth = {r['coin']: (r.get('book') or {}).get('bid_depth_25bp_usd') for r in W.get('assets', [])}
    rows = []
    for coin, m in sorted(man['matched'].items()):
        if 'error' in m:
            continue
        fn = out / 'raw' / 'emissions' / ('%s.json' % m['slug'])
        if not fn.exists():
            continue
        pf = json.loads(fn.read_text())
        for e in cliff_events(pf):
            if not (now_s < e['ts'] <= now_s + days * 86400):
                continue
            unlocked = unlocked_on(pf.get('documentedData'), int(now_s))
            size = (e['tokens'] / unlocked) if unlocked else None
            if size is None or size < min_size:
                continue
            rows.append({'coin': coin, 'unlock_utc': utc_iso(e['ts'] * 1000),
                         'enter_short_utc': utc_iso((e['ts'] - 3 * 86400) * 1000), 'tokens': e['tokens'],
                         'size_of_unlocked': size, 'categories': e['categories'],
                         'round_trip_bps_100k': rts.get(coin), 'bid_depth_25bp_usd': depth.get(coin)})
    rows.sort(key=lambda r: r['unlock_utc'])
    return rows


def cmd_upcoming(args):
    """The forward test's calendar: seller cliffs in the next `--days` on matched perps, at least `--min-size` of the
    supply unlocked so far, with the entry time the pre-unlock rule implies (T - 3 days) and the coin's book."""
    out = Path(args.out)
    rows = upcoming_rows(out, args.days, args.min_size, args.rt_window, time.time())
    write_json(out / 'upcoming.json', {'generated': dt.datetime.now(UTC).isoformat(), 'days': args.days,
                                       'min_size': args.min_size, 'rule': 'short the perp and buy BTC at T-3d, close both at T',
                                       'rows': rows})
    for r in rows:
        print('%-8s unlock %s  enter %s  size %5.2f%%  %s  rt %s  bid depth %s' % (
            r['coin'], r['unlock_utc'][:16], r['enter_short_utc'][:16], 100 * r['size_of_unlocked'],
            '+'.join(r['categories']), r['round_trip_bps_100k'] and '%.0fbp' % r['round_trip_bps_100k'],
            r['bid_depth_25bp_usd'] and '$%.0fk' % (r['bid_depth_25bp_usd'] / 1e3)))
    return 0


# ------------------------------------------------------------------------------------------------ forward test

# The rule the book's `unlock-preshort` entry was proposed on, frozen. A registered row is never edited: a later
# schedule download may move an unlock by hours, and the first registration stands, because the point of a forward
# test is that nothing about an event is decided after its entry time.
FORWARD_RULE = {'id': 'unlock-preshort', 'window_days': [-3, 0], 'min_size': 0.01,
                'categories': sorted(SELLER_CATEGORIES), 'venue': 'Hyperliquid core perps',
                'hedge': 'long the BTC perp, same notional', 'placebo_shift_days': [-15, 15],
                'kill': 'after 30 scored events, mean excess over the placebo not positive',
                'promote': 'after 30 scored events, excess positive and event-day t of the P&L above 2'}
FORWARD_MIN_EVENTS = 30
FORWARD_LEDGER = ROOT / 'research' / 'unlocks_forward.jsonl'


def iso_ms(s):
    return int(dt.datetime.fromisoformat(s).timestamp() * 1000)


def read_ledger(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def ledger_key(row):
    return row['coin'], row['unlock_utc'][:10]


def registrable(rows, ledger, now_s):
    """(new, late): rows whose entry is still ahead and are not yet registered for that coin and unlock day, and rows
    whose entry has already passed. A row registered after its entry would carry the price it is betting on."""
    have = {ledger_key(r) for r in ledger}
    new, late = [], []
    for r in rows:
        if ledger_key(r) in have:
            continue
        (new if iso_ms(r['enter_short_utc']) / 1000 > now_s else late).append(r)
    return new, late


def bid_depth(book, bps=25):
    """USD of bids within `bps` of the mid in a Hyperliquid l2Book reply (None for an empty side)."""
    bids, asks = book['levels'][0], book['levels'][1]
    if not bids or not asks:
        return None
    mid = (float(bids[0]['px']) + float(asks[0]['px'])) / 2
    floor = mid * (1 - bps / 1e4)
    return sum(float(lv['px']) * float(lv['sz']) for lv in bids if float(lv['px']) >= floor)


def api_series(api, coin, t0, t1):
    """The (keys, closes, funding) triple `series` reads from the store, fetched from the venue: hourly closes keyed by
    bar end, hourly funding keyed by its hour. candleSnapshot serves the last 5,000 bars, so an event must be scored
    within about 200 days of its unlock."""
    import perp_rpc as R
    closes = {int(c['t']) + HOUR_MS: float(c['c']) for c in (R.candles(api, coin, '1h', t0, t1) or [])}
    fund, start = {}, t0
    while True:
        rows = R.funding_history(api, coin, start, t1) or []
        for r in rows:
            fund[int((int(r['time']) + HOUR_MS // 2) // HOUR_MS * HOUR_MS)] = float(r['fundingRate'])
        if len(rows) < 500:
            break
        start = int(rows[-1]['time']) + 1
    return sorted(closes), closes, fund


def score_event(row, coin_s, btc_s, rt_bps, other_T, now_ms):
    """The frozen rule on one registered event, and its placebo windows a fortnight either side (skipped within a week
    of another scheduled cliff of the same coin, and until the window has closed)."""
    T = iso_ms(row['unlock_utc'])
    a, b = FORWARD_RULE['window_days']
    res = {'coin': row['coin'], 'unlock_utc': row['unlock_utc'], 'T': T, 'trade': None, 'placebo': [],
           'pending': []}
    if now_ms >= T + HOUR_MS:
        res['trade'] = window_trade(coin_s, btc_s, T, a, b, rt_bps=rt_bps)
        if res['trade'] is None:
            res['pending'].append('trade: price missing')
    else:
        res['pending'].append('trade: unlock not yet passed')
    for shift in FORWARD_RULE['placebo_shift_days']:
        Tp = T + shift * DAY_MS
        if any(abs(Tp - t) < 7 * DAY_MS for t in other_T):
            continue
        if now_ms < Tp + HOUR_MS:
            res['pending'].append('placebo %+d: not yet passed' % shift)
            continue
        tr = window_trade(coin_s, btc_s, Tp, a, b, rt_bps=rt_bps)
        if tr:
            res['placebo'].append(dict(tr, shift_days=shift))
    return res


def forward_summary(scored):
    """Mean P&L, the placebo's mean, their difference and its Welch t, the event-day t of the P&L, and the verdict the
    book's kill criteria imply once 30 events have been scored."""
    trades = [(s['T'], s['trade']['pnl']) for s in scored if s.get('trade')]
    pnl = [v for _, v in trades]
    plac = [p['pnl'] for s in scored for p in s['placebo']]
    m, mp = (statistics.fmean(pnl) if pnl else None), (statistics.fmean(plac) if plac else None)
    excess = (m - mp) if (m is not None and mp is not None) else None
    t_day = tstat(by_day(trades))
    if len(pnl) < FORWARD_MIN_EVENTS:
        verdict = 'accumulating (%d of %d events scored)' % (len(pnl), FORWARD_MIN_EVENTS)
    elif excess is None or excess <= 0:
        verdict = 'kill: mean excess over the placebo is not positive'
    elif t_day is not None and t_day > 2:
        verdict = 'promote: excess positive and event-day t above 2'
    else:
        verdict = 'hold: excess positive, event-day t not above 2'
    return {'events_scored': len(pnl), 'mean_pnl': m, 'placebo_n': len(plac), 'placebo_mean': mp, 'excess': excess,
            'excess_t': welch_t(pnl, plac), 't_by_day': t_day,
            'hit': (sum(1 for v in pnl if v > 0) / len(pnl)) if pnl else None,
            'components': components([s['trade'] for s in scored if s.get('trade')]), 'verdict': verdict}


def cmd_forward(args):
    out, ledger_path = Path(args.out), Path(args.ledger)
    ledger = read_ledger(ledger_path)
    now_s = time.time()
    import perp_rpc as R
    api = R.Info(interval=0.4)
    if args.action == 'register':
        rows = upcoming_rows(out, args.days, FORWARD_RULE['min_size'], args.rt_window, now_s)
        new, late = registrable(rows, ledger, now_s)
        man = json.loads((out / 'manifest.json').read_text())
        stamp = dt.datetime.fromtimestamp(now_s, UTC).isoformat()
        with ledger_path.open('a') as f:
            for r in new:
                try:
                    depth = bid_depth(R.l2_book(api, r['coin']))
                except R.APIError as e:
                    depth = None
                    print('book %s: %s' % (r['coin'], e))
                row = dict(r, registered_at=stamp, rule=FORWARD_RULE['id'], bid_depth_25bp_usd_at_registration=depth,
                           schedule_from=str(out), schedule_collected=man.get('collected_at'))
                f.write(json.dumps(row, sort_keys=True) + '\n')
                print('registered %-8s unlock %s  enter %s  size %5.2f%%  bids within 25bp %s' % (
                    r['coin'], r['unlock_utc'][:16], r['enter_short_utc'][:16], 100 * r['size_of_unlocked'],
                    '—' if depth is None else '$%.0fk' % (depth / 1e3)))
        for r in late:
            print('too late  %-8s entry %s has passed' % (r['coin'], r['enter_short_utc'][:16]))
        print('%d registered, %d too late, %d in the ledger' % (len(new), len(late), len(ledger) + len(new)))
        return 0
    # score
    rts = coin_round_trips(args.rt_window)
    man = json.loads((out / 'manifest.json').read_text())
    now_ms = int(now_s * 1000)
    due = [r for r in ledger if iso_ms(r['unlock_utc']) - 15 * DAY_MS <= now_ms]
    if not due:
        print('nothing to score yet: %d registered, first unlock %s' % (
            len(ledger), min((r['unlock_utc'] for r in ledger), default='—')))
        return 0
    t0 = min(iso_ms(r['unlock_utc']) for r in due) - 20 * DAY_MS
    t1 = min(now_ms, max(iso_ms(r['unlock_utc']) for r in due) + 16 * DAY_MS)
    btc = api_series(api, 'BTC', t0, t1)
    scored = []
    for r in due:
        T = iso_ms(r['unlock_utc'])
        slug = (man['matched'].get(r['coin']) or {}).get('slug')
        other = [r2_T for r2_T in (iso_ms(x['unlock_utc']) for x in ledger if x['coin'] == r['coin']) if r2_T != T]
        fn = out / 'raw' / 'emissions' / ('%s.json' % slug) if slug else None
        if fn and fn.exists():
            other += [e['ts'] * 1000 for e in cliff_events(json.loads(fn.read_text())) if abs(e['ts'] * 1000 - T) > DAY_MS]
        coin_s = api_series(api, r['coin'], T - 20 * DAY_MS, min(now_ms, T + 16 * DAY_MS))
        scored.append(score_event(r, coin_s, btc, rts.get(r['coin'], args.rt_bps), other, now_ms))
    S = forward_summary(scored)
    res = {'generated': dt.datetime.fromtimestamp(now_s, UTC).isoformat(), 'rule': FORWARD_RULE,
           'ledger': str(ledger_path), 'registered': len(ledger), 'summary': S,
           'events': [{k: v for k, v in s.items() if k != 'T'} for s in scored]}
    write_json(ledger_path.with_suffix('.json'), res)
    for s in scored:
        tr = s['trade']
        print('%-8s %s  trade %s  placebo %s  %s' % (
            s['coin'], s['unlock_utc'][:16], pct(tr and tr['pnl']),
            ' '.join(pct(p['pnl']) for p in s['placebo']) or '—', '; '.join(s['pending'])))
    print('scored %d: mean %s, placebo %s, excess %s (t %s), event-day t %s -> %s' % (
        S['events_scored'], pct(S['mean_pnl']), pct(S['placebo_mean']), pct(S['excess']),
        '—' if S['excess_t'] is None else '%.2f' % S['excess_t'],
        '—' if S['t_by_day'] is None else '%.2f' % S['t_by_day'], S['verdict']))
    return 0


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# Token unlocks — tables', '', 'Generated %s; cutoff %s.' % (A['generated'], A['cutoff']), '']
    for label in ('sellers', 'airdrop'):
        R = A.get(label)
        if not R:
            continue
        L += ['## %s cliffs: %d events (%d before the cutoff, %d after) on %d coins' % (
            label, R['events'], R['events_before_cutoff'], R['events_after_cutoff'], len(R['coins'])), '',
            '| window (days) | min size | n in | mean in | placebo in | excess t in | n out | mean out | placebo out | excess t out | hit out | abnormal out | short funding out |',
            '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for v in sorted(R['variants'], key=lambda v: (v['window'], v['min_size'])):
            co = v['components_out'] or {}
            f2 = lambda x: '—' if x is None else '%.2f' % x
            L.append('| %d..%+d | %.1f%% | %d | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s |' % (
                v['window'][0], v['window'][1], 100 * v['min_size'], v['n_in'], pct(v['mean_in']),
                pct(v['placebo_mean_in']), f2(v['excess_t_in']), v['n_out'], pct(v['mean_out']),
                pct(v['placebo_mean_out']), f2(v['excess_t_out']),
                '—' if v['hit_out'] is None else '%.0f%%' % (100 * v['hit_out']),
                pct(co.get('abnormal')), pct(co.get('funding_short_received'))))
        c = R.get('chosen')
        if c:
            L += ['', 'Chosen on events before the cutoff (highest excess-over-placebo t of %d variants with at least the minimum count): window %s, size ≥ %.1f%%: in sample %s against a placebo %s over %d events (excess t %.2f); out of sample %s against %s over %d events (excess t %s). BH survivors in sample (excess over placebo) at q=0.10: %s.'
                  % (R['n_variants'], c['window'], 100 * c['min_size'], pct(c['mean_in']), pct(c['placebo_mean_in']),
                     c['n_in'], c['excess_t_in'] or 0, pct(c['mean_out']), pct(c['placebo_mean_out']), c['n_out'],
                     '—' if c['excess_t_out'] is None else '%.2f' % c['excess_t_out'],
                     R['bh_survivors_in_sample'] or 'none'), '']
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--hl', default='research/2026-10-09/perps_history')
    q = sub.add_parser('prices'); q.set_defaults(fn=cmd_prices)
    q.add_argument('--out', required=True)
    q.add_argument('--since', default='2025-09-15')
    q.add_argument('--until', default='2026-03-20')
    q.add_argument('--interval', type=float, default=2.0)
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--hl', default='research/2026-10-09/perps_history')
    a.add_argument('--cutoff', default='2026-04-01T00:00:00+00:00')
    a.add_argument('--windows', default='-14:0,-7:0,-7:1,-3:0,-3:3,-1:1,0:3,0:7')
    a.add_argument('--sizes', default='0.005,0.01,0.02')
    a.add_argument('--min-events', type=int, default=8)
    a.add_argument('--rt-window', default='research/2026-09-10/perps_2/analysis.json',
                   help='a perp window whose books price each coin\'s round trip at $100k')
    a.add_argument('--rt-bps', type=float, default=35.0, help='round trip for a coin the window did not price (the median priced one was 35bp)')
    u = sub.add_parser('upcoming'); u.set_defaults(fn=cmd_upcoming)
    u.add_argument('--out', required=True)
    u.add_argument('--days', type=int, default=45)
    u.add_argument('--min-size', type=float, default=0.01)
    u.add_argument('--rt-window', default='research/2026-09-10/perps_2/analysis.json')
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    f = sub.add_parser('forward', help='register upcoming events before their entry; score them after their unlock')
    f.set_defaults(fn=cmd_forward)
    f.add_argument('action', choices=['register', 'score'])
    f.add_argument('--out', required=True, help='the study directory whose schedule (collect) is used')
    f.add_argument('--ledger', default=str(FORWARD_LEDGER))
    f.add_argument('--days', type=int, default=45)
    f.add_argument('--rt-window', default='research/2026-09-10/perps_2/analysis.json')
    f.add_argument('--rt-bps', type=float, default=35.0)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
