#!/usr/bin/env python3
"""Binance's TradFi perpetuals against Hyperliquid's HIP-3 markets: a new pair family, and whether a Binance perp can
replace the broker stock leg of the book's equity funding carry.

Why. The book's largest row (`hip3-equity-funding-carry`) shorts trade.xyz single-stock perps that pay high funding
and buys the stocks at a broker. Two things weaken it: the stock leg trades 6.5 hours a day, so a squeeze outside US
hours hits the perp short while the hedge cannot move, and a fully paid stock plus perp margin ties up 1.5x notional.
Binance has listed 217 "TRADIFI_PERPETUAL" contracts since December 2025 (US stocks and ETFs, Hong Kong, Korean and
Chinese names, metals, oil, gas, one FX pair and four pre-IPO names) that trade every hour of the week. If a Binance
perp can stand in for the stock, the hedge never closes and both legs are margined perps. Whether that pays depends
on the one thing this module measures first: what Binance's TradFi funding charges, and when.

What it measures.
  1. Binance TradFi funding since each listing (`/fapi/v1/fundingRate`, paged) with hourly premium-index, index-price
     and trade klines: the formula (interest leg, clamp, cap, interval) reproduced from the premium, and the average
     longs pay by asset class and by US session / weekday off-hours / weekend. A Binance-side broker carry (short the
     Binance perp, long the stock) is priced from the same funding.
  2. The pair family: every HIP-3 builder market matched to its Binance twin by name *and* by price (unit ratios for
     index-vs-ETF twins, split checks), the hourly funding spread, its persistence (first-half vs second-half pair
     means), and the hedged two-perp trade chosen on the first half and tested once on the second (funding_arb's
     fixed-quantity Pair/simulate machinery: always-on, trailing-k entry thresholds, a slow family; exit at zero).
  3. Whether the two-perp hedge fixes the off-hours risk: the basis between the two perps while the cash market is
     shut, its worst excursions, and the Monday-open gap.
  4. Capacity from live books on both venues (depth within 10 and 25bp a side) and open interest (5% of the smaller).
  5. Commodities: the metals and energy twins, and whether Binance's energy index rolls on a different schedule from
     trade.xyz's GSCI-style oracle (`roll_carry.roll_steps`).

Conventions.
  * A funding rate is a fraction of notional per settlement, positive when longs pay (both venues). Hyperliquid pays
    every hour; Binance at its own settlements (8 h for US equities, 4 h for commodities and Asian equities), read from
    the timestamps, never assumed. Binance's TradFi rate, as reproduced here, is (h/8) x [P + clamp(I - P, +-0.05%)]
    capped per symbol, with the interest leg I = 0 since February 2026 (`premiumIndex` reports interestRate 0): two
    settlements in three are exactly zero, where trade.xyz charges longs its 5.5%-a-year floor.
  * The pair (A, B) is short A, long B, a fixed quantity from entry, priced on hourly closes (funding_arb.Pair).
    Capital: each leg margined at 2x on its own venue, so a pair of notional N ties up N (the broker version: stock N
    plus perp margin N/2 = 1.5N). The benchmark is the Sky savings rate, 3.80% a year on that capital.
  * Costs: Hyperliquid builder taker 0.9bp on growth-mode markets (equity_offhours' schedule; 9bp on MSTR, BMNR, STRC),
    Binance taker 5bp (VIP0, no BNB discount), plus each venue's live half-spread.
  * US session = 09:30-16:00 ET on trading days; off-hours = the rest of a weekday; weekend = Friday close to Monday
    open (equity_offhours' calendar, exact DST).

    python3 scripts/tradfi_perps.py collect  --out research/2026-10-10/tradfi_perps     # Binance: funding, klines, OI
    python3 scripts/tradfi_perps.py hl-topup --out research/2026-10-10/tradfi_perps     # HL rows after the 10-09 store
    python3 scripts/tradfi_perps.py stocks   --out research/2026-10-10/tradfi_perps     # Yahoo daily closes, dividends
    python3 scripts/tradfi_perps.py books    --out research/2026-10-10/tradfi_perps     # live books, both venues
    python3 scripts/tradfi_perps.py analyze  --out research/2026-10-10/tradfi_perps
    python3 scripts/tradfi_perps.py render   --out research/2026-10-10/tradfi_perps     # tables.md, manifest.json
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
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
import funding_arb as FA  # noqa: E402

HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
HOURS_PER_YEAR = 8760.0
SSR = 0.038
BN = 'https://fapi.binance.com'
HL_STORES = [ROOT / 'research/2026-09-10/perps_history', ROOT / 'research/2026-10-09/perps_hip3',
             ROOT / 'research/2026-10-09/perps_history']
HL_STORE = ROOT / 'research/2026-10-09/perps_history'
EQ_DIR = ROOT / 'research/2026-10-09/equity_offhours'
YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart/'
UA_YAHOO = 'Mozilla/5.0'          # a bare string is served; a full Chrome string gets 429 from this machine

BN_TAKER_BP = 5.0
BN_MAKER_BP = 2.0
HL_TAKER_BP = 0.9                 # trade.xyz growth mode (equity_offhours: 4.5bp base x 0.2 deployer scale, after the cut)
HL_TAKER_BP_NO_GROWTH = 9.0       # MSTR, BMNR, STRC: growth mode off
HL_NO_GROWTH = {'xyz:MSTR', 'xyz:BMNR', 'xyz:STRC'}
MISSING_HALF_SPREAD_BP = 5.0
CAP_OI_SHARE = 0.05
CAP_SLIP_BP = 10.0

# HIP-3 coin (after the dex prefix) -> Binance base asset, where the names differ. Every candidate is still checked
# on price; the alias only proposes it.
ALIASES = {
    'GOLD': ['XAU'], 'SILVER': ['XAG'], 'PLATINUM': ['XPT'], 'PALLADIUM': ['XPD'], 'BRENTOIL': ['BZ'],
    'SP500': ['SPY'], 'US500': ['SPY'], 'XYZ100': ['QQQ'], 'USTECH': ['QQQ'], 'SMALL2000': ['IWM'],
    'SMSN': ['SAMSUNG', 'SAMSUNGEM'], 'SKHX': ['SKHYNIX'], 'KR200': ['KODEX200'], 'TCNT': ['TENCENT', 'HK0700'],
    'ANTH': ['ANTHROPIC'], 'OAI': ['OPENAI'],
}
# Twins whose units legitimately differ: an index quoted in points against the ETF that tracks it. The ratio drifts
# by the ETF's dividends and fee, so these are 'proxy' pairs, priced with a unit ratio and their dividends charged.
PROXY_OK = {('SP500', 'SPY'), ('US500', 'SPY'), ('XYZ100', 'QQQ'), ('USTECH', 'QQQ'), ('SMALL2000', 'IWM')}
YAHOO_ALIAS = {'BRKB': 'BRK-B'}


# ---------------------------------------------------------------------------------------------- io helpers

def utc(ms=None):
    t = time.time() if ms is None else ms / 1000.0
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def ms_of(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_gz(p, v):
    FA.write_gz(p, v)


def write_json(p, v):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(v, indent=1, sort_keys=True, default=str))
    tmp.replace(p)


def fnum(v, d=None):
    return FA.fnum(v, d)


def safe(name):
    return name.replace(':', '__').replace('/', '_')


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


def median(x):
    x = [v for v in x if v is not None]
    return statistics.median(x) if x else None


def corr(x, y):
    pts = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(pts) < 3:
        return None
    ma = sum(a for a, _ in pts) / len(pts)
    mb = sum(b for _, b in pts) / len(pts)
    sa = math.sqrt(sum((a - ma) ** 2 for a, _ in pts))
    sb = math.sqrt(sum((b - mb) ** 2 for _, b in pts))
    if sa == 0 or sb == 0:
        return None
    return sum((a - ma) * (b - mb) for a, b in pts) / (sa * sb)


# ---------------------------------------------------------------------------------------------- Binance collect

def bn_klines(http, path, sym, start, end, key='symbol'):
    """Hourly klines from `path`, paged 1,000 at a time (weight 5 each; 1,500 costs 10). Rows [t, o, h, l, c, qv]."""
    rows, s = [], start
    for _ in range(40):
        r = http.get(BN + path, {key: sym, 'interval': '1h', 'startTime': s, 'endTime': end, 'limit': 1000})
        if not isinstance(r, list) or not r:
            break
        rows += [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[7] or 0)] for x in r]
        if len(r) < 1000:
            break
        s = int(r[-1][0]) + HOUR_MS
    return sorted({r[0]: r for r in rows}.values(), key=lambda r: r[0])


def bn_funding_rows(http, sym, start, end):
    """Every settlement since `start`: [{'t', 'rate', 'mark'}] (paged 1,000; the endpoint shares a 500 per 5 minutes
    budget with fundingInfo, so its client is paced separately)."""
    rows, s = [], start
    for _ in range(40):
        r = http.get(BN + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': end, 'limit': 1000})
        if not isinstance(r, list):
            break
        rows += [{'t': int(x['fundingTime']), 'rate': float(x['fundingRate']), 'mark': fnum(x.get('markPrice'))}
                 for x in r]
        if len(r) < 1000:
            break
        s = int(r[-1]['fundingTime']) + 1
    return sorted({r['t']: r for r in rows}.values(), key=lambda r: r['t'])


def tradfi_symbols(exinfo):
    return [s for s in exinfo['symbols'] if s.get('contractType') == 'TRADIFI_PERPETUAL']


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    http = FA.Http(interval=0.2, weight_header='X-MBX-USED-WEIGHT-1M', weight_soft=1100)
    http_f = FA.Http(interval=0.7)             # fundingRate: 500 requests per 5 minutes per IP
    t_start = time.time()
    exinfo = http.get(BN + '/fapi/v1/exchangeInfo')
    write_json(raw / 'bn_exchangeInfo.json', exinfo)
    finfo = http_f.get(BN + '/fapi/v1/fundingInfo')
    write_json(raw / 'bn_fundingInfo.json', finfo)
    pidx = http.get(BN + '/fapi/v1/premiumIndex')
    write_json(raw / 'bn_premiumIndex.json', pidx)
    tick = http.get(BN + '/fapi/v1/ticker/24hr')
    write_json(raw / 'bn_ticker24h.json', tick)
    syms = tradfi_symbols(exinfo)
    if args.only:
        keep = set(args.only.split(','))
        syms = [s for s in syms if s['symbol'] in keep]
    now = int(time.time() * 1000)
    end = now // HOUR_MS * HOUR_MS
    log, fails = {}, []
    cons, oi_now, oi_hist = {}, {}, {}
    cp = raw / 'bn_constituents.json'
    if cp.exists():
        cons = json.loads(cp.read_text())
    def one(s):
        sym = s['symbol']
        start = int(s['onboardDate']) // HOUR_MS * HOUR_MS
        rec = {'onboard': utc(int(s['onboardDate'])), 'underlyingType': s.get('underlyingType')}
        try:
            fp = raw / 'binance' / 'funding' / (sym + '.json.gz')
            if args.refresh or not fp.exists():
                rows = bn_funding_rows(http_f, sym, start, now)
                write_gz(fp, rows)
            rec['funding_rows'] = len(read_gz(fp))
            for sub, path, key in (('klines', '/fapi/v1/klines', 'symbol'),
                                   ('premium', '/fapi/v1/premiumIndexKlines', 'symbol'),
                                   ('index', '/fapi/v1/indexPriceKlines', 'pair')):
                p = raw / 'binance' / sub / (sym + '.json.gz')
                if args.refresh or not p.exists():
                    write_gz(p, bn_klines(http, path, sym, start, end, key=key))
                rec[sub + '_rows'] = len(read_gz(p))
            if args.refresh or sym not in cons:
                c = http.get(BN + '/fapi/v1/constituents', {'symbol': sym})
                cons[sym] = c if isinstance(c, dict) else {'error': str(c)[:200]}
            o = http.get(BN + '/fapi/v1/openInterest', {'symbol': sym})
            oi_now[sym] = o if isinstance(o, dict) else None
            h = http.get(BN + '/futures/data/openInterestHist', {'symbol': sym, 'period': '1d', 'limit': 30})
            oi_hist[sym] = h if isinstance(h, list) else []
        except Exception as e:  # noqa: BLE001 - recorded, the rest continue
            fails.append({'symbol': sym, 'error': repr(e)[:200]})
        log[sym] = rec
        return sym, rec

    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for k, (sym, rec) in enumerate(ex.map(one, syms)):
            if k % 20 == 0:
                print('%3d/%d %s %s' % (k + 1, len(syms), sym, json.dumps(rec)), flush=True)
    write_json(cp, cons)
    write_json(raw / 'bn_open_interest.json', {'at': utc(), 'now': oi_now, 'hist_1d': oi_hist})
    man_p = out / 'collect_manifest.json'
    write_json(man_p, {'generated': utc(), 'endpoint': BN, 'symbols': len(syms), 'per_symbol': log,
                       'failures': fails, 'http': http.stats(), 'http_funding': http_f.stats(),
                       'seconds': round(time.time() - t_start, 1),
                       'note': 'klines/premium/index are 1h bars [t_open, o, h, l, c, quote_volume] from each '
                               'onboardDate; funding rows are every settlement with the mark at settlement'})
    print(json.dumps({'symbols': len(syms), 'failures': len(fails), 'http': http.stats(),
                      'seconds': round(time.time() - t_start)}))


# ---------------------------------------------------------------------------------------------- Hyperliquid top-up

def cmd_hl_topup(args):
    """Funding and 1h candles for the matched HIP-3 markets from the shared store's end to now, so the pair series
    reach the same hour as the Binance downloads (read with the store by `load_hl_market`)."""
    from perp_rpc import Info, funding_history, candles
    out = Path(args.out)
    pairs = json.loads((out / 'pairs.json').read_text())['pairs'] if (out / 'pairs.json').exists() else []
    coins = sorted({p['hl'] for p in pairs} | set((args.extra or '').split(',')) - {''})
    api = Info(interval=args.interval)
    start = ms_of(args.since)
    now = int(time.time() * 1000)
    got, fails = {}, []
    for c in coins:
        try:
            f = funding_history(api, c, start, now)
            k = candles(api, c, '1h', start, now)
            write_gz(out / 'raw' / 'hl_topup' / 'funding' / (safe(c) + '.json.gz'), f)
            write_gz(out / 'raw' / 'hl_topup' / 'candles_1h' / (safe(c) + '.json.gz'), k)
            got[c] = [len(f or []), len(k or [])]
        except Exception as e:  # noqa: BLE001
            fails.append({'coin': c, 'error': repr(e)[:200]})
    write_json(out / 'raw' / 'hl_topup' / 'manifest.json', {'at': utc(), 'since': args.since, 'coins': got,
                                                           'failures': fails, 'api': api.stats()})
    print(json.dumps({'coins': len(got), 'failures': len(fails), 'api': api.stats()}))


# ---------------------------------------------------------------------------------------------- stocks (Yahoo)

def yahoo_daily(sym, p1, p2, retries=4, pause=1.5):
    url = '%s%s?period1=%d&period2=%d&interval=1d&events=div%%2Csplit&includeAdjustedClose=false' % (
        YAHOO, sym, p1, p2)
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA_YAHOO})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = 'HTTP %d' % e.code
            if e.code == 404:
                break
            time.sleep(pause * 2 ** (a + 1))
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:120]
            time.sleep(pause * 2 ** (a + 1))
    raise RuntimeError('%s: %s' % (sym, last))


def parse_yahoo_daily(d):
    """{'closes': {date: close}, 'dividends': [{'ex_date', 'amount'}], 'splits': [...], 'tz': ...} from a chart
    response. Yahoo stamps a daily bar at the session's open; the date is read in the exchange's own time zone."""
    res = ((d or {}).get('chart') or {}).get('result') or []
    if not res:
        return None
    r = res[0]
    meta = r.get('meta') or {}
    off = int(meta.get('gmtoffset') or 0)
    ts = r.get('timestamp') or []
    q = ((r.get('indicators') or {}).get('quote') or [{}])[0]
    closes = {}
    for i, t in enumerate(ts):
        c = (q.get('close') or [None] * len(ts))[i]
        if c is None:
            continue
        day = dt.datetime.fromtimestamp(t + off, dt.timezone.utc).date().isoformat()
        closes[day] = c
    ev = r.get('events') or {}
    divs = [{'ex_date': dt.datetime.fromtimestamp(int(v['date']) + off, dt.timezone.utc).date().isoformat(),
             'amount': float(v['amount'])} for v in (ev.get('dividends') or {}).values()]
    splits = [{'date': dt.datetime.fromtimestamp(int(v['date']) + off, dt.timezone.utc).date().isoformat(),
               'ratio': '%s:%s' % (v.get('numerator'), v.get('denominator'))} for v in (ev.get('splits') or {}).values()]
    return {'closes': closes, 'dividends': sorted(divs, key=lambda x: x['ex_date']), 'splits': splits,
            'currency': meta.get('currency'), 'exchange': meta.get('exchangeName'), 'tz': meta.get('exchangeTimezoneName')}


def cmd_stocks(args):
    out = Path(args.out)
    exinfo = json.loads((out / 'raw' / 'bn_exchangeInfo.json').read_text())
    syms = sorted({s['baseAsset'] for s in tradfi_symbols(exinfo) if s.get('underlyingType') == 'EQUITY'})
    if args.only:
        syms = [s for s in syms if s in set(args.only.split(','))]
    p1, p2 = ms_of(args.since) // 1000, int(time.time())
    got, fails = {}, []
    for s in syms:
        p = out / 'raw' / 'yahoo' / (s + '.json.gz')
        if p.exists() and not args.refresh:
            got[s] = 'cached'
            continue
        try:
            d = parse_yahoo_daily(yahoo_daily(YAHOO_ALIAS.get(s, s), p1, p2))
            if not d or not d['closes']:
                raise RuntimeError('no bars')
            write_gz(p, d)
            got[s] = len(d['closes'])
        except Exception as e:  # noqa: BLE001
            fails.append({'symbol': s, 'error': repr(e)[:160]})
        time.sleep(args.pause)
    write_json(out / 'raw' / 'yahoo' / 'manifest.json', {'at': utc(), 'since': args.since, 'got': got,
                                                         'failures': fails})
    print(json.dumps({'symbols': len(syms), 'got': len(got), 'failures': len(fails)}))


# ---------------------------------------------------------------------------------------------- loading

def hl_stores(out):
    return HL_STORES + [Path(out) / 'raw' / 'hl_topup']


def load_hl(coin, out):
    """Hyperliquid builder market merged across the shared stores and this study's top-up (later stores overwrite):
    equity_offhours.load_market's dict — px/avg/n/usd keyed by the hour the candle ends, prem/rate by settlement hour."""
    import equity_offhours as EO
    return EO.load_market(coin, stores=hl_stores(out))


def load_bn(out, sym):
    """Binance TradFi perp: settlements [(hour, rate)], premium bars {hour_end: (o, h, l, c)}, trade closes and quote
    volume {hour_end: x}, index closes {hour_end: x}, and the usual settlement interval in hours."""
    raw = Path(out) / 'raw' / 'binance'
    fp = raw / 'funding' / (sym + '.json.gz')
    if not fp.exists():
        return None
    sett = [(FA.hour_of(r['t']), float(r['rate'])) for r in read_gz(fp)]
    d = {'sym': sym, 'sett': sett, 'prem': {}, 'px': {}, 'qv': {}, 'idx': {}}
    for sub, key in (('premium', 'prem'), ('klines', 'px'), ('index', 'idx')):
        p = raw / sub / (sym + '.json.gz')
        if not p.exists():
            continue
        for k in read_gz(p):
            te = int(k[0]) + HOUR_MS
            if key == 'prem':
                d['prem'][te] = (k[1], k[2], k[3], k[4])
            else:
                d[key][te] = k[4]
                if key == 'px':
                    d['qv'][te] = k[5]
    gaps = {}
    hs = [t for t, _ in sett]
    for a, b in zip(hs, hs[1:]):
        g = (b - a) // HOUR_MS
        gaps[g] = gaps.get(g, 0) + 1
    d['interval'] = max(gaps, key=gaps.get) if gaps else None
    d['intervals'] = gaps
    return d


def bn_interval_at(sett, i):
    """Hours covered by settlement i: the gap since the previous one (the first takes the next gap)."""
    if i > 0:
        return max(1, (sett[i][0] - sett[i - 1][0]) // HOUR_MS)
    if len(sett) > 1:
        return max(1, (sett[1][0] - sett[0][0]) // HOUR_MS)
    return 8


def bn_hourly_accrual(sett):
    """{hour_end: rate per hour}: each settlement spread evenly over the hours of its own interval — what a position
    held through those hours pays on average."""
    acc = {}
    for i, (T, r) in enumerate(sett):
        h = bn_interval_at(sett, i)
        for k in range(h):
            acc[T - k * HOUR_MS] = r / h
    return acc


# ---------------------------------------------------------------------------------------------- calendar

def trading_days(out):
    """US trading days: SPY's Nasdaq history from the equity study, SPY's Yahoo closes from this one, and weekdays
    after the last of them up to a week ahead (the next close is needed to classify the current weekend)."""
    days = set()
    p = EQ_DIR / 'raw' / 'nasdaq' / 'SPY.json'
    if p.exists():
        days |= set(json.loads(p.read_text())['rows'])
    y = Path(out) / 'raw' / 'yahoo' / 'SPY.json.gz'
    if y.exists():
        days |= set(read_gz(y)['closes'])
    ds = sorted(dt.date.fromisoformat(x) for x in days)
    if not ds:
        return []
    d = ds[-1]
    end = dt.date.today() + dt.timedelta(days=7)
    while d < end:
        d += dt.timedelta(days=1)
        if d.weekday() < 5:
            ds.append(d)
    return ds


class HourState:
    """'session' (09:30-16:00 ET on a trading day), 'offhours' (a weekday night between two sessions) or 'weekend'
    (a closed period of two nights or more: weekends and holidays), for the hour that ends at T; by its midpoint."""

    def __init__(self, days):
        import equity_offhours as EO
        self.opens, self.closes = [], []
        for d in days:
            self.opens.append(EO.open_ms(d))
            self.closes.append(EO.close_ms(d))
        self.gap_days = [None] + [(b - a).days for a, b in zip(days, days[1:])]

    def __call__(self, T):
        mid = T - HOUR_MS // 2
        i = bisect.bisect_right(self.opens, mid) - 1
        if i < 0 or i >= len(self.opens):
            return None
        if mid <= self.closes[i]:
            return 'session'
        if i + 1 >= len(self.opens):
            return None
        return 'offhours' if self.gap_days[i + 1] == 1 else 'weekend'


# ---------------------------------------------------------------------------------------------- matching

def tradfi_usdt(exinfo):
    return {s['symbol']: s for s in tradfi_symbols(exinfo) if s.get('quoteAsset') == 'USDT'}


def ratio_profile(hl_px, bn_px):
    """Daily medians of the hourly price ratio HL / Binance over the hours both printed a close."""
    by_day = {}
    for T, a in hl_px.items():
        b = bn_px.get(T)
        if a and b:
            by_day.setdefault(T // DAY_MS, []).append(a / b)
    return {d: statistics.median(v) for d, v in sorted(by_day.items())}


def classify_ratio(daily, base, cand, tol=0.01, break_tol=0.10):
    """Decide whether two listings are the same asset in the same units. Returns (kind, unit_ratio, start_day, info):
    kind 'same' (ratio within `tol` of 1; real twins sit within 0.1%, the USDT/USDC rate), 'proxy' (an index/ETF
    twin in PROXY_OK, priced at its median ratio) or 'reject' (pre-IPO marks 2.6-4.4% apart are different prices of
    the same company, not the same price). A day whose ratio sits more than `break_tol` from the latest week's is a break (a split, a relisting, a
    different contract); the pair starts after the last one."""
    if len(daily) < 3:
        return 'reject', None, None, {'reason': 'under 3 days of overlap', 'days': len(daily)}
    days = sorted(daily)
    recent = statistics.median([daily[d] for d in days[-7:]])
    breaks = [d for d in days if abs(daily[d] / recent - 1.0) > break_tol]
    start = (max(breaks) + 1) if breaks else days[0]
    kept = [daily[d] for d in days if d >= start]
    if len(kept) < 3:
        return 'reject', None, None, {'reason': 'under 3 days after the last break', 'breaks': len(breaks)}
    med = statistics.median(kept)
    dev = max(abs(v / med - 1.0) for v in kept)
    info = {'median_ratio': med, 'max_dev_from_median': dev, 'days': len(kept), 'breaks': len(breaks),
            'first_day': utc(start * DAY_MS)[:10], 'last_day': utc(days[-1] * DAY_MS)[:10]}
    if abs(med - 1.0) <= tol:
        return 'same', 1.0, start, info
    if (base, cand) in PROXY_OK:
        return 'proxy', med, start, info
    info['reason'] = 'price ratio %.4f' % med
    return 'reject', None, None, info


def cmd_match(args):
    out = Path(args.out)
    exinfo = json.loads((out / 'raw' / 'bn_exchangeInfo.json').read_text())
    bn = tradfi_usdt(exinfo)
    by_base = {}
    for sym, s in bn.items():
        by_base.setdefault(s['baseAsset'], []).append(sym)
    uni = json.loads((HL_STORE / 'universe.json').read_text())
    markets = [m for m in uni['markets'] if m['dex'] != 'core']
    pairs, rejects, unmatched = [], [], []
    bn_cache = {}
    for m in sorted(markets, key=lambda m: m['coin']):
        coin = m['coin']
        dex, base = coin.split(':', 1)
        cands = [c for c in ALIASES.get(base, [base]) if c in by_base]
        if not cands:
            unmatched.append(coin)
            continue
        hl = load_hl(coin, out)
        for cand in cands:
            for sym in by_base[cand]:
                if sym not in bn_cache:
                    bn_cache[sym] = load_bn(out, sym)
                b = bn_cache[sym]
                if b is None or not b['px']:
                    rejects.append({'hl': coin, 'bn': sym, 'reason': 'no Binance data'})
                    continue
                daily = ratio_profile(hl['px'], b['px'])
                kind, ur, start, info = classify_ratio(daily, base, cand)
                if kind == 'reject':
                    rejects.append(dict({'hl': coin, 'bn': sym}, **info))
                    continue
                s = bn[sym]
                pairs.append({'hl': coin, 'dex': dex, 'bn': sym, 'kind': kind, 'unit_ratio': ur,
                              'class': s.get('underlyingType'), 'start': utc(start * DAY_MS),
                              'bn_onboard': utc(int(s['onboardDate'])), 'bn_interval_h': b['interval'],
                              'hl_mult': m.get('funding_multiplier'), 'hl_oi_usd': (m.get('oi') or 0) * (m.get('mark') or 0),
                              'ratio': info})
    write_json(out / 'pairs.json', {'generated': utc(), 'pairs': pairs, 'rejects': rejects,
                                    'unmatched_hl': unmatched,
                                    'note': 'HIP-3 builder markets live on 2026-10-09 matched to Binance TradFi '
                                            'USDT perps by name (ALIASES) and price (classify_ratio)'})
    print(json.dumps({'pairs': len(pairs), 'rejects': len(rejects), 'unmatched_hl': len(unmatched),
                      'kinds': {k: sum(1 for p in pairs if p['kind'] == k) for k in ('same', 'proxy')}}))
    for r in rejects:
        print('reject', r)


# ---------------------------------------------------------------------------------------------- live books

def hl_levels(book):
    lv = (book or {}).get('levels') or [[], []]
    bids = [[float(x['px']), float(x['sz'])] for x in lv[0]]
    asks = [[float(x['px']), float(x['sz'])] for x in lv[1]]
    return bids, asks


def merged_side(fine, coarse, mid, bp):
    """Depth within `bp` from the fine book when its last level reaches past `bp`, else from the coarse
    (nSigFigs-aggregated) book, which sees further at the cost of bucket rounding."""
    if fine and abs(fine[-1][0] / mid - 1.0) * 1e4 >= bp:
        return fine
    return coarse or fine


def side_summary(fine, coarse, mid):
    out = {}
    for bp in (10, 25):
        lv = merged_side(fine, coarse, mid, bp)
        out['depth%d' % bp] = FA.depth_within(lv, mid, bp) if lv else 0.0
    lv = merged_side(fine, coarse, mid, 50)
    out['max_size_10bp'] = FA.max_size(lv, mid, CAP_SLIP_BP) if lv else 0.0
    return out


def book_summary(bids_f, asks_f, bids_c=None, asks_c=None):
    if not bids_f or not asks_f:
        return None
    mid = (bids_f[0][0] + asks_f[0][0]) / 2.0
    return {'mid': mid, 'half_spread_bp': (asks_f[0][0] - bids_f[0][0]) / 2.0 / mid * 1e4,
            'bid': side_summary(bids_f, bids_c, mid), 'ask': side_summary(asks_f, asks_c, mid)}


def cmd_books(args):
    from perp_rpc import Info, meta_and_ctxs
    out = Path(args.out)
    pairs = json.loads((out / 'pairs.json').read_text())['pairs']
    bn_syms = sorted({p['bn'] for p in pairs})
    hl_coins = sorted({p['hl'] for p in pairs})
    http = FA.Http(interval=0.25, weight_header='X-MBX-USED-WEIGHT-1M', weight_soft=1100)
    snap = {'at': utc(), 'binance': {}, 'hl': {}, 'hl_meta': {}, 'bn_oi': {}}
    for sym in bn_syms:
        d = http.get(BN + '/fapi/v1/depth', {'symbol': sym, 'limit': 500})
        o = http.get(BN + '/fapi/v1/openInterest', {'symbol': sym})
        if not isinstance(d, dict) or not d.get('bids'):
            continue
        bids = [[float(p), float(q)] for p, q in d['bids']]
        asks = [[float(p), float(q)] for p, q in d['asks']]
        mid = (bids[0][0] + asks[0][0]) / 2.0
        snap['binance'][sym] = {'at': utc(), 'bids': FA.trim(bids, mid, 150), 'asks': FA.trim(asks, mid, 150)}
        snap['bn_oi'][sym] = o if isinstance(o, dict) else None
    api = Info(interval=args.interval)
    for dex in sorted({c.split(':', 1)[0] for c in hl_coins}):
        snap['hl_meta'][dex] = meta_and_ctxs(api, dex)
    for coin in hl_coins:
        b = api.post({'type': 'l2Book', 'coin': coin})
        c = api.post({'type': 'l2Book', 'coin': coin, 'nSigFigs': 4})
        snap['hl'][coin] = {'at': utc(), 'fine': b, 'coarse': c}
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M')
    p = out / 'raw' / 'books' / ('books_%s.json.gz' % stamp)
    write_gz(p, snap)
    print(json.dumps({'file': str(p), 'binance': len(snap['binance']), 'hl': len(snap['hl']),
                      'bn_http': http.stats(), 'hl_api': api.stats()}))


# ---------------------------------------------------------------------------------------------- Binance funding

BN_CLAMP = 0.0005                 # the +-0.05% band of Binance's interest-minus-premium clamp
BN_INTEREST_8H = 0.0001           # the crypto perps' 0.01% per 8 h; TradFi perps report 0 (premiumIndex interestRate)


def bn_formula(P, interest8, h=8, clamp=BN_CLAMP, cap=None, floor=None):
    """Binance funding for one settlement from the interval's average premium P:
    (h/8) x [P + clamp(I - P, -c, c)], then the symbol's cap and floor; I is the 8-hour interest rate and h the
    settlement interval in hours. With I = 0 the rate is zero whenever |P| <= c and (h/8)(P -/+ c) beyond; a 4-hour
    symbol pays half the 8-hour rate twice as often. (Fitted here: the unscaled form reproduces 4-hour symbols within
    1bp on 56-67% of settlements, the scaled one on 87-92%.)"""
    f = (h / 8.0) * (P + max(-clamp, min(clamp, interest8 - P)))
    if cap is not None:
        f = min(cap, f)
    if floor is not None:
        f = max(floor, f)
    return f


def window_premium(prem, T, h, weighting='linear'):
    """Average premium over the h hours ending at T from hourly premium-index bars, each hour's mean taken as
    (o+h+l+c)/4. Binance weights the 5-second samples linearly in time (1, 2, ..., n), so hour k of h gets weight
    2k-1. None when fewer than three quarters of the hours have a bar."""
    num = den = 0.0
    got = 0
    for k in range(1, h + 1):
        b = prem.get(T - (h - k) * HOUR_MS)
        if b is None:
            continue
        w = (2 * k - 1) if weighting == 'linear' else 1
        num += w * (b[0] + b[1] + b[2] + b[3]) / 4.0
        den += w
        got += 1
    return num / den if got >= 0.75 * h and den else None


def interest_regimes(sett, tol=1e-12):
    """Months in which the interest leg was on: more than 5% of settlements exactly at 0.01% x interval/8."""
    by_m = {}
    for i, (T, r) in enumerate(sett):
        h = bn_interval_at(sett, i)
        m = utc(T)[:7]
        x = by_m.setdefault(m, [0, 0])
        x[1] += 1
        if abs(r - BN_INTEREST_8H * h / 8.0) < tol:
            x[0] += 1
    return {m: (a / n > 0.05) for m, (a, n) in by_m.items()}


def formula_check(b, cap, floor):
    """Reproduce each settlement from the premium bars. Returns counts: rows checked, rows within 0.5bp and 1bp of
    the printed rate, zero/non-zero agreement, the clamp implied by non-zero rows (P - F for F > 0, F - P... as c), and
    the share of settlements at exactly zero."""
    sett, prem = b['sett'], b['prem']
    regimes = interest_regimes(sett)
    n = within05 = within1 = zero_ok = 0
    zeros = 0
    c_est = []
    for i, (T, F) in enumerate(sett):
        h = bn_interval_at(sett, i)
        if F == 0.0:
            zeros += 1
        P = window_premium(prem, T, h)
        if P is None:
            continue
        I8 = BN_INTEREST_8H if regimes.get(utc(T)[:7]) else 0.0
        Fp = bn_formula(P, I8, h, cap=cap, floor=floor)
        dead = I8 * h / 8.0                         # what the dead zone pays per settlement
        n += 1
        within05 += abs(Fp - F) <= 0.00005
        within1 += abs(Fp - F) <= 0.0001
        zero_ok += (abs(Fp - dead) < 1e-12) == (abs(F - dead) < 1e-12)
        F8 = F * 8.0 / h                            # the settlement in 8-hour units
        if F > dead + 1e-9 and P > 0:
            c_est.append(P + I8 - F8)
        elif F < dead - 1e-9 and P < 0:
            c_est.append(F8 - P - I8)
    return {'settlements': len(sett), 'checked': n, 'within_0.5bp': within05, 'within_1bp': within1,
            'zero_class_agree': zero_ok, 'zero_settlements': zeros, 'clamp_estimates': c_est,
            'interest_months': sorted(m for m, on in regimes.items() if on)}


def state_apr(rates_by_hour, state):
    """{state: (annualised mean of hourly rates, hours)} over the hours that have a state."""
    acc = {}
    for T, r in rates_by_hour.items():
        s = state(T)
        if s is None:
            continue
        a = acc.setdefault(s, [0.0, 0])
        a[0] += r
        a[1] += 1
    return {s: {'apr': v[0] / v[1] * HOURS_PER_YEAR, 'hours': v[1]} for s, v in acc.items() if v[1]}


def bn_funding_summary(out, exinfo, finfo, state, since_ms=None):
    """Per TradFi symbol: funding longs paid (a year rate) since listing and over the last 90 days, share of
    settlements at zero / negative, by-state accrual, and the formula check."""
    fi = {x['symbol']: x for x in finfo}
    res = {}
    for sym, s in sorted(tradfi_usdt(exinfo).items()):
        b = load_bn(out, sym)
        if not b or not b['sett']:
            continue
        cap = fnum(fi.get(sym, {}).get('adjustedFundingRateCap'))
        floor = fnum(fi.get(sym, {}).get('adjustedFundingRateFloor'))
        sett = b['sett']
        acc = bn_hourly_accrual(sett)
        if since_ms:
            acc = {T: r for T, r in acc.items() if T >= since_ms}
        hours = len(acc)
        last = max(acc) if acc else None
        rec = {'class': s.get('underlyingType'), 'interval_h': b['interval'], 'intervals': b['intervals'],
               'onboard': utc(int(s['onboardDate'])), 'settlements': len(sett), 'cap': cap, 'floor': floor,
               'apr_since_listing': (sum(acc.values()) / hours * HOURS_PER_YEAR) if hours else None,
               'hours': hours,
               'apr_last_90d': None, 'zero_share': sum(1 for _, r in sett if r == 0.0) / len(sett),
               'negative_share': sum(1 for _, r in sett if r < 0) / len(sett),
               'max_rate': max(r for _, r in sett), 'min_rate': min(r for _, r in sett),
               'by_state': state_apr(acc, state)}
        if last:
            rec90 = [r for T, r in acc.items() if T > last - 90 * DAY_MS]
            rec['apr_last_90d'] = sum(rec90) / len(rec90) * HOURS_PER_YEAR if rec90 else None
            rec['quote_volume_30d'] = sum(v for T, v in b['qv'].items() if T > last - 30 * DAY_MS)
        rec['formula'] = formula_check(b, cap, floor)
        res[sym] = rec
    return res


def class_table(per_sym, key='apr_since_listing'):
    """By asset class: symbols, the median and hour-weighted mean of `key`, and by-state hour-weighted means."""
    out = {}
    for cls in sorted({r['class'] for r in per_sym.values()}):
        rows = [r for r in per_sym.values() if r['class'] == cls and r.get(key) is not None]
        if not rows:
            continue
        hw = sum(r[key] * r['hours'] for r in rows) / max(1, sum(r['hours'] for r in rows))
        st = {}
        for s in ('session', 'offhours', 'weekend'):
            xs = [(r['by_state'][s]['apr'], r['by_state'][s]['hours']) for r in rows if s in r['by_state']]
            h = sum(w for _, w in xs)
            st[s] = sum(a * w for a, w in xs) / h if h else None
        out[cls] = {'symbols': len(rows), 'median_apr': median([r[key] for r in rows]), 'hour_weighted_apr': hw,
                    'by_state_hour_weighted': st,
                    'zero_share_median': median([r['zero_share'] for r in rows]),
                    'negative_share_median': median([r['negative_share'] for r in rows]),
                    'symbols_over_8pct': sum(1 for r in rows if r[key] >= 0.08),
                    'symbols_over_5_7pct': sum(1 for r in rows if r[key] >= 0.057)}
    return out


def formula_totals(per_sym):
    tot = {'checked': 0, 'within_0.5bp': 0, 'within_1bp': 0, 'zero_class_agree': 0, 'settlements': 0,
           'zero_settlements': 0}
    cs = []
    months = {}
    for sym, r in per_sym.items():
        f = r['formula']
        for k in tot:
            tot[k] += f[k]
        cs += f['clamp_estimates']
        for m in f['interest_months']:
            months.setdefault(m, []).append(sym)
    tot['share_within_0.5bp'] = tot['within_0.5bp'] / tot['checked'] if tot['checked'] else None
    tot['share_within_1bp'] = tot['within_1bp'] / tot['checked'] if tot['checked'] else None
    tot['share_zero_class_agree'] = tot['zero_class_agree'] / tot['checked'] if tot['checked'] else None
    tot['share_zero'] = tot['zero_settlements'] / tot['settlements'] if tot['settlements'] else None
    cs.sort()
    tot['implied_clamp_median'] = median(cs)
    tot['implied_clamp_iqr'] = [cs[len(cs) // 4], cs[3 * len(cs) // 4]] if len(cs) > 4 else None
    tot['implied_clamp_n'] = len(cs)
    tot['interest_leg_months'] = {m: sorted(v) for m, v in sorted(months.items())}
    return tot


def hl_funding_summary(pairs, out, state):
    """Hyperliquid funding by state for each matched builder market, over the same hours as its Binance twin."""
    res = {}
    for p in pairs:
        m = load_hl(p['hl'], out)
        t0 = ms_of(p['start'][:10])
        rates = {T: r for T, r in m['rate'].items() if r is not None and T >= t0}
        if not rates:
            continue
        res[p['hl']] = {'apr': sum(rates.values()) / len(rates) * HOURS_PER_YEAR, 'hours': len(rates),
                        'by_state': state_apr(rates, state),
                        'prem_by_state_bp': {s: v['apr'] / HOURS_PER_YEAR * 1e4 for s, v in
                                             state_apr({T: x for T, x in m['prem'].items()
                                                        if x is not None and T >= t0}, state).items()}}
    return res


# ---------------------------------------------------------------------------------------------- daily carries

def bn_market(b):
    """A Binance perp in equity_offhours' market layout, so its px_at / funding_between / carry_days read it."""
    return {'coin': b['sym'], 'px': dict(b['px']), 'n': {T: (1 if b['qv'].get(T, 0) > 0 else 0) for T in b['px']},
            'usd': dict(b['qv']), 'avg': {}, 'prem': {}, 'rate': {T: r for T, r in b['sett']}, 'px4': {}, 'usd4': {},
            'first': min(b['px']) if b['px'] else None, 'last': max(b['px']) if b['px'] else None}


def load_stock_refs(out):
    """{symbol: ({date: {'close'}}, [dividends])}: Yahoo daily closes fetched here, else the equity study's Nasdaq
    history and dividends. One source per name, so every version of a carry on that name reads the same closes."""
    import equity_offhours as EO
    refs = {}
    ydir = Path(out) / 'raw' / 'yahoo'
    for p in sorted(ydir.glob('*.json.gz')):
        d = read_gz(p)
        refs[p.name[:-8]] = ({k: {'close': v} for k, v in d['closes'].items()}, d.get('dividends') or [], 'yahoo')
    eq_refs, eq_divs = EO.load_refs(EQ_DIR)
    for sym, rows in eq_refs.items():
        if sym not in refs:
            refs[sym] = (rows, eq_divs.get(sym) or [], 'nasdaq')
    return refs


def ref_symbol(hl_coin):
    """The cash ticker behind a trade.xyz / Paragon single-stock or ETF perp (index perps have none here)."""
    return hl_coin.split(':', 1)[1]


def pair_carry_days(mh, mb, days, max_basis=0.03):
    """Daily close-to-close (16:00 ET) P&L per unit notional of short the Hyperliquid perp / long the Binance perp:
    HL funding received, Binance funding paid, and the change in the two perps' basis (Binance return minus HL return).
    `funding` carries HL's funding (the book rule's signal) and `spread` HL minus Binance."""
    import equity_offhours as EO
    rows, prev = [], None
    for d in days:
        T = EO.close_ms(d)
        Ph, sh = EO.px_at(mh, T)
        Pb, sb = EO.px_at(mb, T)
        if not Ph or not Pb or sh is None or sb is None or sh > 1 or sb > 1:
            prev = None
            continue
        basis = Ph / Pb - 1.0
        if abs(basis) > max_basis:
            prev = None
            continue
        if prev is not None:
            fh = EO.funding_between(mh, prev['T'], T)[0]
            fb = EO.funding_between(mb, prev['T'], T)[0]
            rh, rb = Ph / prev['Ph'] - 1.0, Pb / prev['Pb'] - 1.0
            vol = sum(mh['usd'].get(t, 0.0) for t in range(prev['T'] + HOUR_MS, T + 1, HOUR_MS))
            rows.append({'d': d.isoformat(), 'f_hl': fh, 'f_bn': fb, 'r_hl': rh, 'r_bn': rb,
                         'pnl': fh - fb + rb - rh, 'funding': fh, 'spread': fh - fb, 'vol_usd': vol, 'basis': basis})
        prev = {'T': T, 'Ph': Ph, 'Pb': Pb}
    return rows


def with_signal(per_coin, key):
    """Copy of per-coin rows whose `funding` field (what family_carry ranks on) is `key`."""
    return {c: [dict(r, funding=r[key]) for r in rows] for c, rows in per_coin.items()}


def carry_family(per_coin_days, days, cost_bps, capital, label, frac=0.5):
    """equity_offhours.family_carry's six variants (all / trailing >= 8% / top ten, two volume floors) on these rows,
    chosen on the first `frac` of sessions and tested once on the rest. Returns the summary and the raw series."""
    import equity_offhours as EO
    dlist, variants, members, raw = EO.family_carry(per_coin_days, {}, days, cost_bps,
                                                    capital_per_notional=capital, ssr=SSR)
    # Sessions before the first basket are flat in every variant; the test split counts from the first live day.
    first = next((i for i in range(len(dlist)) if any(variants[k][i] != 0.0 for k in variants)), 0)
    v = {k: s[first:] for k, s in variants.items()}
    ctt = B.choose_then_test(v, frac=frac, periods_per_year=252)
    if not ctt:
        return None, None
    c = ctt['cutoff_index']
    ch = ctt['chosen']
    oos = v[ch][c:]
    rw = raw[ch][first:][c:]
    fund = [x[2] for x in rw if x[2] is not None]
    pnl = [x[1] for x in rw if x[1] is not None]
    allv = {k: {'in': B.perf(s[:c], 252).get('ann_return'), 'out': B.perf(s[c:], 252).get('ann_return'),
                'out_t': B.newey_west_t(s[c:])[0]} for k, s in v.items()}
    res = {'label': label, 'capital_per_notional': capital, 'sessions': len(v[ch]),
           'first_session': dlist[first], 'test_from': dlist[first + c] if first + c < len(dlist) else None,
           'last_session': dlist[-1], 'chosen': ch,
           'in_sample_excess': ctt['in_sample'].get('ann_return'), 'in_sample_sharpe': ctt['in_sample'].get('sharpe'),
           'oos_excess': ctt['out_of_sample'].get('ann_return'), 'oos_sharpe': ctt['out_of_sample'].get('sharpe'),
           'oos_t': ctt['oos_t'], 'oos_p': ctt['oos_p'], 'oos_rank': ctt['oos_rank'], 'n_variants': ctt['n_variants'],
           'deflated_sharpe_in_sample': ctt['deflated_sharpe_in_sample'],
           'bh_survivors_full_sample': ctt['bh_survivors_full_sample'],
           'oos_bootstrap': B.block_bootstrap(oos, block=10),
           'oos_basket_funding_apr': (mean(fund) * 252) if fund else None,
           'oos_basket_pnl_per_notional_apr': (mean(pnl) * 252) if pnl else None,
           'oos_mean_names': mean([x[4] for x in rw]),
           'baskets': [(d, b) for d, b in members[ch] if d >= dlist[first]],
           'all_variants': allv}
    return res, v


# ---------------------------------------------------------------------------------------------- hourly pair grid

def build_pair(p, out, t0, n):
    """funding_arb.Pair of (short HL, long Binance) on the study grid, masked before the pair's start day."""
    m = load_hl(p['hl'], out)
    sett = sorted((T, r) for T, r in m['rate'].items() if r is not None)
    A = FA.Venue(n).fill(t0, n, sett, {T: x for T, x in m['prem'].items() if x is not None}, m['px'])
    Bv = FA.load_cex_venue(Path(out) / 'raw', 'binance', p['bn'], t0, n)
    if Bv is None:
        return None
    js = max(0, (ms_of(p['start'][:10]) - t0) // HOUR_MS)
    for j in range(min(js, n)):
        A.live[j] = False
        Bv.live[j] = False
    return FA.Pair(p['hl'], A, Bv, n, a_name='hl', b_name='bn', unit_ratio=p['unit_ratio'] or 1.0)


def simulate_fixed(pair, d, step, ce, cx):
    """Always-on in one direction: enter d (+1 = short A / long B) at the first observable decision hour, hold while
    the pair stays observable, re-enter after a gap. Trades in funding_arb.simulate's format."""
    trades, ei = [], None

    def close(e, forced):
        f, b = pair.hold(ei, e)
        trades.append({'d': d, 'i': ei, 'e': e, 'funding': d * f, 'basis': d * b, 'cost': ce + cx,
                       'net': d * (f + b) - ce - cx, 'forced': forced})

    for i in range(0, pair.n, step):
        ok = pair.av[i] and pair.window(i, 24) is not None
        if ei is None and ok:
            ei = i
        elif ei is not None and not ok:
            close(i, True)
            ei = None
    if ei is not None and ei < pair.n - 1:
        close(pair.n - 1, True)
    return trades


def run_variants(pairs, costs, n_days):
    """funding_arb's 106-variant grid (fast trailing-k thresholds and the slow 30/90-day family, exit at zero or half)
    plus always-on in each direction, summed over pairs: daily P&L and deployed capital per variant."""
    variants = FA.variants_grid()
    res = FA.run_grid(pairs, costs, variants, n_days)
    for name, d in (('always_short_hl', 1), ('always_short_bn', -1)):
        P, C, ntr = [0.0] * n_days, [0.0] * n_days, 0
        for coin, pr in pairs.items():
            ce, cx = costs[coin]
            tr = simulate_fixed(pr, d, FA.STEP, ce, cx)
            ntr += len(tr)
            pnl, cap = FA.daily_pnl(pr, tr, n_days)
            P = [a + b for a, b in zip(P, pnl)]
            C = [a + b for a, b in zip(C, cap)]
        res[name] = {'P': P, 'C': C, 'trades': ntr,
                     'variant': {'name': name, 'k': 24, 'X': None, 'Y': None, 'H': None, 'step': FA.STEP,
                                 'family': 'always', 'd': d}}
    return res


def chosen_trades(pairs, costs, v):
    out = {}
    for coin, pr in pairs.items():
        ce, cx = costs[coin]
        if v.get('family') == 'always':
            out[coin] = simulate_fixed(pr, v['d'], FA.STEP, ce, cx)
        else:
            out[coin] = FA.simulate(pr, v['k'], v['X'], v['Y'], v['H'], v.get('step', FA.STEP), ce, cx)
    return out


def grid_eval(pairs, costs, n, t0, test_day, label):
    n_days = n // 24
    cnt = FA.live_counts(pairs, n_days)
    res = run_variants(pairs, costs, n_days)
    series = {k: [r['P'][d] / cnt[d] if cnt[d] else 0.0 for d in range(n_days)] for k, r in res.items()}
    ctt = B.choose_then_test(series, frac=test_day / n_days, periods_per_year=365)
    ch = ctt['chosen']

    def dep(r, a, b):
        cc = sum(r['C'][a:b])
        return (sum(r['P'][a:b]) / cc * 365) if cc else None

    trs = chosen_trades(pairs, costs, res[ch]['variant'])
    test_h = test_day * 24
    tt = [(c, t) for c, ts in trs.items() for t in ts if t['i'] >= test_h]
    held = sum(t['e'] - t['i'] for _, t in tt)
    nw30 = B.newey_west_t(series[ch][test_day:], lags=30)
    ranked = sorted(res, key=lambda k: -(B.perf(series[k][:test_day], 365).get('sharpe') or -1e9))
    top = [{'variant': k, 'choose_sharpe': B.perf(series[k][:test_day], 365).get('sharpe'),
            'test_deployed_apr': dep(res[k], test_day, n_days),
            'test_reserved_apr': B.perf(series[k][test_day:], 365).get('ann_return')} for k in ranked[:10]]
    per_class = {}
    for c, t in tt:
        k = pairs[c].klass if hasattr(pairs[c], 'klass') else 'all'
        x = per_class.setdefault(k, {'trades': 0, 'net': 0.0, 'hours': 0, 'funding': 0.0, 'basis': 0.0})
        x['trades'] += 1
        x['net'] += t['net']
        x['funding'] += t['funding']
        x['basis'] += t['basis']
        x['hours'] += t['e'] - t['i']
    for x in per_class.values():
        x['net_per_year_held'] = x['net'] / x['hours'] * HOURS_PER_YEAR if x['hours'] else None
        x['funding_per_year_held'] = x['funding'] / x['hours'] * HOURS_PER_YEAR if x['hours'] else None
        x['basis_per_year_held'] = x['basis'] / x['hours'] * HOURS_PER_YEAR if x['hours'] else None
    always = {k: {'test_reserved_apr': B.perf(series[k][test_day:], 365).get('ann_return'),
                  'test_deployed_apr': dep(res[k], test_day, n_days),
                  'train_deployed_apr': dep(res[k], 0, test_day),
                  'test_t': B.newey_west_t(series[k][test_day:], lags=30)[0]}
              for k in ('always_short_hl', 'always_short_bn')}
    return {
        'label': label, 'pairs': len(pairs), 'variants': len(res), 'grid_start': utc(t0), 'hours': n,
        'test_from': utc(t0 + test_day * DAY_MS), 'chosen': ch, 'chosen_variant': res[ch]['variant'],
        'in_sample': ctt['in_sample'], 'out_of_sample': ctt['out_of_sample'], 'oos_rank': ctt['oos_rank'],
        'oos_t': ctt['oos_t'], 'oos_t_30d': nw30[0], 'deflated_sharpe_in_sample': ctt['deflated_sharpe_in_sample'],
        'bh_survivors_full_sample': len(ctt['bh_survivors_full_sample']),
        'test_trades': len(tt), 'test_years_held': held / HOURS_PER_YEAR,
        'test_net_per_year_held': (sum(t['net'] for _, t in tt) / held * HOURS_PER_YEAR) if held else None,
        'test_deployed_apr': dep(res[ch], test_day, n_days),
        'test_cost_per_trade_bp': mean([t['cost'] * 1e4 for _, t in tt]),
        'top10': top, 'always_on': always, 'per_class_test': per_class,
        'share_variants_test_deployed_over_ssr': (lambda xs: sum(1 for x in xs if x > SSR) / len(xs) if xs else None)(
            [x for x in (dep(r, test_day, n_days) for r in res.values()) if x is not None]),
    }, series, trs


def spread_stats(pairs):
    """Per pair: the hourly funding spread (HL - Binance accrual) a year, both halves of the pair's own life, and
    across pairs the correlation of first-half with second-half means (persistence)."""
    rows = {}
    for coin, pr in pairs.items():
        hrs = [j for j in range(pr.n) if pr.av[j]]
        if len(hrs) < 24 * 14:
            continue
        mid = len(hrs) // 2
        a = sum(pr.s[j] for j in hrs[:mid]) / mid * HOURS_PER_YEAR
        b = sum(pr.s[j] for j in hrs[mid:]) / (len(hrs) - mid) * HOURS_PER_YEAR
        hl = sum(pr.A.pay[j] for j in hrs) / len(hrs) * HOURS_PER_YEAR
        bn = sum(pr.B.pay[j] for j in hrs) / len(hrs) * HOURS_PER_YEAR
        rows[coin] = {'hours': len(hrs), 'spread_apr': (a * mid + b * (len(hrs) - mid)) / len(hrs),
                      'first_half': a, 'second_half': b, 'hl_apr': hl, 'bn_apr': bn,
                      'class': getattr(pr, 'klass', None)}
    fa = [r['first_half'] for r in rows.values()]
    sb = [r['second_half'] for r in rows.values()]
    return {'pairs': rows, 'n': len(rows), 'corr_halves': corr(fa, sb),
            'same_sign_share': (sum(1 for a, b in zip(fa, sb) if a * b > 0) / len(fa)) if fa else None,
            'median_spread_apr': median([r['spread_apr'] for r in rows.values()]),
            'share_hl_higher': (sum(1 for r in rows.values() if r['spread_apr'] > 0) / len(rows)) if rows else None}


# ---------------------------------------------------------------------------------------------- off-hours basis

def quantiles(x, qs=(0.5, 0.9, 0.95, 0.99)):
    x = sorted(v for v in x if v is not None)
    if not x:
        return {}
    out = {('p%d' % round(q * 100)): x[min(len(x) - 1, int(q * (len(x) - 1) + 0.5))] for q in qs}
    out['max'] = x[-1]
    out['n'] = len(x)
    out['mean'] = sum(x) / len(x)
    return out


def bn_px_at(b, T, max_stale_h=2):
    for k in range(max_stale_h + 1):
        v = b['px'].get(T - k * HOUR_MS)
        if v and b['qv'].get(T - k * HOUR_MS, 0) > 0:
            return v
    return None


def closed_period_rows(mh, b, periods, start_ms, ur=1.0):
    """Per closed period (cash market shut) for one pair: the worst move of the HL perp against a short that cannot
    be re-hedged (the broker version: the stock is frozen), and the worst move of the HL-Binance basis against
    the same short hedged with the Binance perp (the two-perp version), both from the cash close to 30 minutes
    before the open, plus the basis gap from the close to 30 minutes after the open."""
    import equity_offhours as EO
    rows = []
    for p in periods:
        if p['close_ms'] < start_ms:
            continue
        P0, s0 = EO.px_at(mh, p['close_ms'])
        Q0 = bn_px_at(b, p['close_ms'])
        if not P0 or not Q0 or s0 is None or s0 > 1:
            continue
        b0 = P0 / (Q0 * ur)
        up = dn = bu = bd = 0.0
        hours = 0
        for T in range(p['close_ms'] + HOUR_MS, p['pre_ms'] + 1, HOUR_MS):
            P, _ = EO.px_at(mh, T, max_stale_h=1)
            Q = bn_px_at(b, T, max_stale_h=1)
            if not P or not Q:
                continue
            hours += 1
            r = P / P0 - 1.0
            up, dn = max(up, r), max(dn, -r)
            x = (P / (Q * ur)) / b0 - 1.0
            bu, bd = max(bu, x), max(bd, -x)
        if not hours:
            continue
        Pp, _ = EO.px_at(mh, p['post_ms'], max_stale_h=0)
        Qp = bn_px_at(b, p['post_ms'], max_stale_h=0)
        rows.append({'d0': p['d0'], 'kind': p['kind'], 'hours': hours, 'perp_up': up, 'perp_down': dn,
                     'basis_up': bu, 'basis_down': bd,
                     'basis_gap_open': ((Pp / (Qp * ur)) / b0 - 1.0) if (Pp and Qp) else None,
                     'perp_gap_open': (Pp / P0 - 1.0) if Pp else None})
    return rows


def comovement(mh, b, state, start_ms, ur=1.0):
    """Hourly returns of the two perps by state: correlation, and the volatility of the basis change against the
    volatility of the HL perp (how much of the move the second perp hedges)."""
    acc = {}
    Ts = sorted(T for T in mh['px'] if T >= start_ms)
    for T in Ts:
        P1, P0 = mh['px'].get(T), mh['px'].get(T - HOUR_MS)
        Q1, Q0 = b['px'].get(T), b['px'].get(T - HOUR_MS)
        if not (P1 and P0 and Q1 and Q0):
            continue
        if mh['n'].get(T, 1) <= 0 or b['qv'].get(T, 0) <= 0:
            continue
        s = state(T)
        if s is None:
            continue
        a = acc.setdefault(s, ([], []))
        a[0].append(math.log(P1 / P0))
        a[1].append(math.log(Q1 / Q0))
    out = {}
    for s, (x, y) in acc.items():
        if len(x) < 30:
            continue
        d = [u - v for u, v in zip(x, y)]
        sx = statistics.pstdev(x)
        out[s] = {'hours': len(x), 'corr': corr(x, y), 'sd_hl_bp': sx * 1e4, 'sd_basis_bp': statistics.pstdev(d) * 1e4,
                  'hedge_ratio_var': (1 - (statistics.pstdev(d) / sx) ** 2) if sx else None}
    return out


# ---------------------------------------------------------------------------------------------- capacity

def load_snapshot(out):
    snaps = sorted((Path(out).resolve() / 'raw' / 'books').glob('books_*.json.gz'))
    return (read_gz(snaps[-1]), str(snaps[-1].relative_to(ROOT))) if snaps else (None, None)


def hl_ctx_map(snap):
    """{coin: {'oi_usd', 'mark', 'oracle', 'funding', 'premium', 'vol24'}} from the snapshot's metaAndAssetCtxs."""
    out = {}
    for dex, mc in (snap.get('hl_meta') or {}).items():
        if not isinstance(mc, list) or len(mc) < 2:
            continue
        uni = mc[0].get('universe') or []
        for u, c in zip(uni, mc[1]):
            name = u.get('name')
            mark = fnum(c.get('markPx'))
            out[name] = {'oi_usd': (fnum(c.get('openInterest'), 0) or 0) * (mark or 0), 'mark': mark,
                         'oracle': fnum(c.get('oraclePx')), 'funding': fnum(c.get('funding')),
                         'premium': fnum(c.get('premium')), 'vol24': fnum(c.get('dayNtlVlm')),
                         'growth_mode': u.get('growthMode'), 'fee_scale': u.get('deployerFeeScale')}
    return out


def hl_fee_bp(coin, ctx=None):
    if coin in HL_NO_GROWTH:
        return HL_TAKER_BP_NO_GROWTH
    return HL_TAKER_BP


def pair_books(snap, p, ctx):
    """Both legs' book summaries, open interest and the pair's capacity for short HL / long Binance (and the reverse):
    the smaller of the needed sides' depth within 25bp (and the 10bp-slippage size), capped at 5% of the smaller OI."""
    hb = (snap.get('hl') or {}).get(p['hl']) or {}
    bf, af = hl_levels(hb.get('fine'))
    bc, ac = hl_levels(hb.get('coarse'))
    hs = book_summary(bf, af, bc, ac)
    bb = (snap.get('binance') or {}).get(p['bn']) or {}
    bs = book_summary(bb.get('bids'), bb.get('asks')) if bb else None
    oi_b = None
    o = (snap.get('bn_oi') or {}).get(p['bn'])
    if o and bs:
        oi_b = (fnum(o.get('openInterest'), 0) or 0) * bs['mid']
    oi_h = (ctx.get(p['hl']) or {}).get('oi_usd')
    if not hs or not bs:
        return {'hl': hs, 'bn': bs, 'oi_hl': oi_h, 'oi_bn': oi_b, 'capacity': None}
    oi_cap = CAP_OI_SHARE * min(x for x in (oi_h, oi_b) if x is not None) if (oi_h or oi_b) else None
    d25 = min(hs['bid']['depth25'], bs['ask']['depth25'], hs['ask']['depth25'], bs['bid']['depth25'])
    s10 = min(hs['bid']['max_size_10bp'], bs['ask']['max_size_10bp'])
    cap = min(x for x in (d25, oi_cap) if x is not None)
    hl_d25 = min(hs['bid']['depth25'], hs['ask']['depth25'])
    return {'hl': hs, 'bn': bs, 'oi_hl': oi_h, 'oi_bn': oi_b, 'oi_cap': oi_cap, 'depth25_min': d25,
            'size_10bp_short_hl': s10, 'capacity': cap, 'hl_depth25_min': hl_d25,
            'capacity_broker': min(x for x in (hl_d25, CAP_OI_SHARE * oi_h if oi_h else None) if x is not None)}


# ---------------------------------------------------------------------------------------------- commodity rolls

ENERGY = {'xyz:CL': ('CLUSDT', 'wti', 'CL'), 'xyz:BRENTOIL': ('BZUSDT', 'brent', 'BZ'),
          'xyz:NATGAS': ('NATGASUSDT', 'ng', 'NG')}
RC_YAHOO = ROOT / 'research/2026-10-09/roll_carry/raw/yahoo'


def implied_oracle_series(mh):
    import equity_offhours as EO
    out = {}
    for T, a in mh['avg'].items():
        p = mh['prem'].get(T)
        o = EO.implied_oracle(a, p)
        if o:
            out[T] = o
    return out


def yahoo_hourly(sym):
    """{hour_end_ms: close} for one futures contract from roll_carry's cache (bars stamped at their open)."""
    p = RC_YAHOO / ('%s_60m.json.gz' % sym)
    if not p.exists():
        return {}
    d = read_gz(p)
    return {int(b['t']) + HOUR_MS: b['c'] for b in d.get('bars', []) if b.get('c')}


def roll_study(out, coin):
    """Binance's energy index against trade.xyz's oracle around each GSCI roll step: the log ratio's change across
    each xyz step hour (a step there that the Binance index does not take shows up one-for-one), the largest
    hourly changes off the schedule (Binance's own roll, if any), and the pair's funding against its basis over each
    month's roll window. For the October roll, both indices' front weights fitted to the two contracts' hourly bars."""
    import roll_carry as RC
    sym, rule, root = ENERGY[coin]
    mh = load_hl(coin, out)
    b = load_bn(out, sym)
    if not b:
        return None
    orc = implied_oracle_series(mh)
    idx = b['idx']
    q = {T: math.log(idx[T] / orc[T]) for T in orc if T in idx and idx[T] > 0}
    Ts = sorted(q)
    dq = {T: q[T] - q[T - HOUR_MS] for T in Ts if T - HOUR_MS in q}
    sd = statistics.pstdev(list(dq.values())) if len(dq) > 10 else None
    first, last = dt.datetime.fromtimestamp(Ts[0] / 1000, dt.timezone.utc), dt.datetime.fromtimestamp(Ts[-1] / 1000, dt.timezone.utc)
    step_hours, months = set(), []
    for mon, s0, s1 in RC.roll_windows(first, last):
        y, m = int(mon[:4]), int(mon[5:])
        steps = RC.roll_steps(y, m)
        # did the xyz oracle actually roll this month? (the month's expiring front contract)
        (fy, fm), _ = RC.front_second(rule, steps[0][0])
        rolls = (RC.expiry(rule, fy, fm).year, RC.expiry(rule, fy, fm).month) == (y, m)
        dqs = []
        for t, w in steps:
            T = int(t.timestamp() * 1000)
            # the step lands at 22:00 UTC; the hour ending 23:00 straddles it, so measure 22:00 -> 00:00
            a, c = q.get(T), q.get(T + 2 * HOUR_MS)
            dqs.append(None if a is None or c is None else c - a)
            step_hours.update((T + HOUR_MS, T + 2 * HOUR_MS))
        # the pair over the roll window: short xyz / long Binance from 24 h before the first step to 2 h after the last
        t_in, t_out = int(steps[0][0].timestamp() * 1000) - 24 * HOUR_MS, int(steps[-1][0].timestamp() * 1000) + 2 * HOUR_MS
        f_hl = sum(r for T, r in mh['rate'].items() if r is not None and t_in < T <= t_out)
        f_bn = sum(r for T, r in b['sett'] if t_in < T <= t_out)
        import equity_offhours as EO
        P0, _ = EO.px_at(mh, t_in)
        P1, _ = EO.px_at(mh, t_out)
        Q0, Q1 = bn_px_at(b, t_in), bn_px_at(b, t_out)
        basis = ((Q1 / Q0 - 1.0) - (P1 / P0 - 1.0)) if (P0 and P1 and Q0 and Q1) else None
        months.append({'month': mon, 'xyz_rolls': rolls, 'step_dq': dqs,
                       'sum_step_dq': sum(x for x in dqs if x is not None) if any(x is not None for x in dqs) else None,
                       'pair_short_xyz': {'f_hl': f_hl, 'f_bn': f_bn, 'basis': basis,
                                          'net': (f_hl - f_bn + basis) if basis is not None else None}})
    off = sorted(((abs(v), T, v) for T, v in dq.items() if T not in step_hours), reverse=True)[:12]
    fit = None
    # October 2026: both contracts are cached; fit each index as w * front + (1 - w) * second
    (fy, fm), (sy, sm) = RC.front_second(rule, dt.datetime(2026, 10, 5, tzinfo=dt.timezone.utc))
    f1 = yahoo_hourly(RC.contract_symbol(root, fy, fm).replace('.NYM', '') + '.NYM')
    f2 = yahoo_hourly(RC.contract_symbol(root, sy, sm).replace('.NYM', '') + '.NYM')
    if f1 and f2:
        fit = {'front': RC.contract_symbol(root, fy, fm), 'second': RC.contract_symbol(root, sy, sm), 'days': {}}
        for T in sorted(set(f1) & set(f2)):
            if T < ms_of('2026-09-28'):
                continue
            a, c = f1[T], f2[T]
            if abs(a - c) / c < 0.004:
                continue
            day = utc(T)[:10]
            x = fit['days'].setdefault(day, {'bn': [], 'xyz': []})
            if T in idx:
                x['bn'].append((idx[T] - c) / (a - c))
            if T in orc:
                x['xyz'].append((orc[T] - c) / (a - c))
        fit['days'] = {d: {'bn_w': median(v['bn']), 'xyz_w': median(v['xyz']), 'hours': len(v['bn'])}
                       for d, v in sorted(fit['days'].items())}
    return {'coin': coin, 'bn': sym, 'hours': len(q), 'sd_dq_bp': sd * 1e4 if sd else None,
            'months': months, 'largest_off_schedule_moves': [{'utc': utc(T), 'dq_bp': v * 1e4} for _, T, v in off],
            'october_weights': fit,
            'constituents_note': 'see analysis.binance.constituents for the index sources'}


# ---------------------------------------------------------------------------------------------- analyze

US_CLASSES = {'EQUITY'}


def constituent_summary(cons):
    """Which sources feed Binance's TradFi indices, and how often Hyperliquid (a HIP-3 market) is one of them."""
    by_src, with_hl, total = {}, [], 0
    for sym, c in cons.items():
        rows = (c or {}).get('constituents') or []
        if not rows:
            continue
        total += 1
        for r in rows:
            by_src[r.get('exchange')] = by_src.get(r.get('exchange'), 0) + 1
            if r.get('exchange') == 'hyperliquid':
                with_hl.append({'symbol': sym, 'source': r.get('symbol'), 'weight': fnum(r.get('weight'))})
    return {'symbols': total, 'source_counts': dict(sorted(by_src.items(), key=lambda x: -x[1])),
            'hyperliquid_in_index': with_hl}


def leg_costs(snap_b, ctx, p, eq_costs):
    """(HL half round trip bp, Binance half round trip bp) for one pair: fee plus half-spread from the live books,
    the equity study's book cost for HL where this snapshot has no book, 5bp of half-spread where neither does."""
    hl_hs = ((snap_b or {}).get('hl') or {}).get('half_spread_bp')
    bn_hs = ((snap_b or {}).get('bn') or {}).get('half_spread_bp')
    hl = hl_fee_bp(p['hl']) + (hl_hs if hl_hs is not None else MISSING_HALF_SPREAD_BP)
    bn = BN_TAKER_BP + (bn_hs if bn_hs is not None else MISSING_HALF_SPREAD_BP)
    return hl, bn


def first_cutoff_by_pair_days(pairs, n_days, frac=0.5):
    cnt = FA.live_counts(pairs, n_days)
    tot = sum(cnt)
    run = 0
    for d, c in enumerate(cnt):
        run += c
        if run >= frac * tot:
            return d, cnt
    return n_days // 2, cnt


def cmd_analyze(args):
    import equity_offhours as EO
    out = Path(args.out)
    t_run = time.time()
    raw = out / 'raw'
    exinfo = json.loads((raw / 'bn_exchangeInfo.json').read_text())
    finfo = json.loads((raw / 'bn_fundingInfo.json').read_text())
    cons = json.loads((raw / 'bn_constituents.json').read_text()) if (raw / 'bn_constituents.json').exists() else {}
    pj = json.loads((out / 'pairs.json').read_text())
    pairs = pj['pairs']
    days = trading_days(out)
    state = HourState(days)
    snap, snap_path = load_snapshot(out)
    ctx = hl_ctx_map(snap) if snap else {}
    A = {'generated': utc(), 'params': {'ssr': SSR, 'bn_taker_bp': BN_TAKER_BP, 'hl_taker_bp': HL_TAKER_BP,
                                        'hl_taker_bp_no_growth': HL_TAKER_BP_NO_GROWTH, 'cap_oi_share': CAP_OI_SHARE,
                                        'capital_two_perp': 1.0, 'capital_broker': 1.5, 'snapshot': snap_path}}

    # 1. Binance funding: formula, level, by class and by hour state
    per_sym = bn_funding_summary(out, exinfo, finfo, state)
    ftot = formula_totals(per_sym)
    for r in per_sym.values():
        r['formula'] = {k: v for k, v in r['formula'].items() if k != 'clamp_estimates'}
    A['binance'] = {'symbols': len(per_sym), 'formula': ftot, 'by_class': class_table(per_sym),
                    'by_class_last_90d': class_table(per_sym, 'apr_last_90d'), 'per_symbol': per_sym,
                    'constituents': constituent_summary(cons)}
    print('binance funding: %d symbols, %.1fs' % (len(per_sym), time.time() - t_run), flush=True)

    # 2. pair books and costs (live snapshot)
    books = {}
    for p in pairs:
        books[p['hl']] = pair_books(snap, p, ctx) if snap else None
    A['books'] = {'at': (snap or {}).get('at'), 'pairs': {p['hl']: books[p['hl']] for p in pairs}}

    # 3. hourly pair grid (funding_arb machinery) on every matched pair
    t0 = ms_of(args.grid_start)
    end = None
    for p in pairs:
        b = load_bn(out, p['bn'])
        if b and b['px']:
            end = max(b['px']) if end is None else max(end, max(b['px']))
    hl_end = max(max(load_hl(p['hl'], out)['px'] or [0]) for p in pairs)
    end = min(end, hl_end)
    n = (end - t0) // HOUR_MS + 1
    n -= n % 24
    P, costs = {}, {}
    for p in pairs:
        pr = build_pair(p, out, t0, n)
        if pr is None or pr.AV[-1] < 24 * 7:
            continue
        pr.klass = ('index_proxy' if p['kind'] == 'proxy' else
                    'commodity' if p['class'] == 'COMMODITY' else
                    'us_equity' if p['class'] in US_CLASSES else 'other')
        hl_c, bn_c = leg_costs(books.get(p['hl']), ctx, p, None)
        c = (hl_c + bn_c) / 1e4
        P[p['hl']] = pr
        costs[p['hl']] = (c, c)
    n_days = n // 24
    test_day, cnt = first_cutoff_by_pair_days(P, n_days)
    grid, series, trs = grid_eval(P, costs, n, t0, test_day, 'all matched pairs')
    A['pair_grid'] = grid
    A['spreads'] = spread_stats(P)
    sub = {k: {c: pr for c, pr in P.items() if pr.klass == k} for k in ('us_equity', 'commodity')}
    A['pair_grid_by_class'] = {}
    for k, ps in sub.items():
        if len(ps) >= 3:
            td, _ = first_cutoff_by_pair_days(ps, n_days)
            A['pair_grid_by_class'][k] = grid_eval(ps, {c: costs[c] for c in ps}, n, t0, td, k)[0]
    print('pair grid: %d pairs, %.1fs' % (len(P), time.time() - t_run), flush=True)

    # 4. daily carries on one calendar: broker xyz, Binance-hedged xyz, broker Binance
    refs = load_stock_refs(out)
    eq_costs = json.loads((EQ_DIR / 'analysis.json').read_text()).get('costs', {})
    d0 = dt.date.fromisoformat(args.carry_start)
    dlist = [d for d in days if d0 <= d <= dt.date.fromisoformat(utc(end)[:10]) and d.isoformat() <= utc(end)[:10]]
    last_close = max(d for d in dlist if EO.close_ms(d) <= end)
    dlist = [d for d in dlist if d <= last_close]
    hl_cost, pair_cost, bn_cost = {}, {}, {}
    v_broker, v_pair, v_bn, v_broker_all = {}, {}, {}, {}
    eq_pairs = [p for p in pairs if p['kind'] == 'same' and p['class'] in US_CLASSES]
    for p in eq_pairs:
        sym = ref_symbol(p['hl'])
        mh = load_hl(p['hl'], out)
        mb = bn_market(load_bn(out, p['bn']))
        hl_c, bn_c = leg_costs(books.get(p['hl']), ctx, p, eq_costs)
        pair_cost[p['hl']] = 2 * (hl_c + bn_c)
        rows = pair_carry_days(mh, mb, dlist)
        if rows:
            v_pair[p['hl']] = rows
        if sym in refs:
            ref, dv, _ = refs[sym]
            hl_cost[p['hl']] = 2 * hl_c + 2.0
            rr = EO.carry_days(mh, ref, dlist, dv)
            if rr:
                v_broker[p['hl']] = rr
    # the book's own universe: every xyz single-stock/ETF perp with a cash reference, twin or not
    uni = json.loads((HL_STORE / 'universe.json').read_text())
    for m in uni['markets']:
        c = m['coin']
        if not c.startswith('xyz:'):
            continue
        sym = ref_symbol(c)
        if sym not in refs:
            continue
        ref, dv, _ = refs[sym]
        mh = load_hl(c, out)
        rr = EO.carry_days(mh, ref, dlist, dv)
        if rr:
            v_broker_all[c] = rr
            if c not in hl_cost:
                ec = (eq_costs.get(c) or {}).get('schedule')
                hl_cost[c] = (ec if ec is not None else 2 * (hl_fee_bp(c) + MISSING_HALF_SPREAD_BP)) + 2.0
    for sym, s in tradfi_usdt(exinfo).items():
        if s.get('underlyingType') not in US_CLASSES:
            continue
        base = s['baseAsset']
        if base not in refs:
            continue
        b = load_bn(out, sym)
        if not b or not b['px']:
            continue
        ref, dv, _ = refs[base]
        rr = EO.carry_days(bn_market(b), ref, dlist, dv)
        if rr:
            v_bn[sym] = rr
            bn_cost[sym] = 2 * (BN_TAKER_BP + MISSING_HALF_SPREAD_BP) + 2.0
    carries = {}
    for label, rows, cst, cap in (('xyz_broker_all', v_broker_all, hl_cost, 1.5),
                                  ('xyz_broker_twins', v_broker, hl_cost, 1.5),
                                  ('xyz_short_bn_long_twins', v_pair, pair_cost, 1.0),
                                  ('xyz_short_bn_long_twins_spread_signal', with_signal(v_pair, 'spread'), pair_cost, 1.0),
                                  ('bn_broker', v_bn, bn_cost, 1.5)):
        if not rows:
            continue
        res, _ = carry_family(rows, dlist, cst, cap, label)
        if res:
            res['names'] = len(rows)
            carries[label] = res
    A['carries'] = carries
    A['carry_calendar'] = {'first': dlist[0].isoformat() if dlist else None,
                           'last': dlist[-1].isoformat() if dlist else None, 'sessions': len(dlist)}
    # the two-perp version's sensitivity: the same rows at 3x margin per leg (capital 0.67 of notional)
    if v_pair:
        r3, _ = carry_family(v_pair, dlist, pair_cost, 2.0 / 3.0, 'xyz_short_bn_long_twins_3x')
        if r3:
            r3['names'] = len(v_pair)
        A['carries']['xyz_short_bn_long_twins_3x'] = r3
    # decomposition of the two-perp rows: funding legs and basis, all names, all days
    allrows = [r for rows in v_pair.values() for r in rows]
    monthly = {}
    for r in allrows:
        x = monthly.setdefault(r['d'][:7], {'name_days': 0, 'f_hl': 0.0, 'f_bn': 0.0, 'basis': 0.0})
        x['name_days'] += 1
        x['f_hl'] += r['f_hl']
        x['f_bn'] += r['f_bn']
        x['basis'] += r['r_bn'] - r['r_hl']
    for x in monthly.values():
        k = 252.0 / x['name_days']
        x['f_hl_apr'], x['f_bn_apr'], x['basis_apr'] = x['f_hl'] * k, x['f_bn'] * k, x['basis'] * k
        x['net_apr'] = x['f_hl_apr'] - x['f_bn_apr'] + x['basis_apr']
    A['pair_daily_decomposition'] = {
        'monthly': dict(sorted(monthly.items())),
        'name_days': len(allrows),
        'f_hl_apr': mean([r['f_hl'] for r in allrows]) * 252 if allrows else None,
        'f_bn_apr': mean([r['f_bn'] for r in allrows]) * 252 if allrows else None,
        'basis_apr': mean([r['r_bn'] - r['r_hl'] for r in allrows]) * 252 if allrows else None}
    print('carries: %s, %.1fs' % (sorted(carries), time.time() - t_run), flush=True)

    # 5. capacity of the latest baskets (Saturday books here; the equity study's 2026-09-10 in-session HL books for a
    # weekday reference)
    try:
        weekday, _, _ = EO.load_books(EQ_DIR)
    except Exception:  # noqa: BLE001 - reference only
        weekday = {}
    cap_rows = {}
    for label in ('xyz_short_bn_long_twins', 'xyz_short_bn_long_twins_spread_signal', 'xyz_broker_twins',
                  'xyz_broker_all'):
        r = carries.get(label)
        if not r or not r['baskets']:
            continue
        last_basket = r['baskets'][-1][1]
        rows = []
        broker = label.startswith('xyz_broker')
        for c in last_basket:
            bk = books.get(c) or {}
            hl_oi = (ctx.get(c) or {}).get('oi_usd') or bk.get('oi_hl')
            if broker:
                plan = CAP_OI_SHARE * hl_oi if hl_oi else None
                inst = bk.get('capacity_broker')
            else:
                plan = bk.get('oi_cap')
                inst = bk.get('capacity')
            wk = (weekday.get(c) or {}).get('in_session') or {}
            rows.append({'coin': c, 'capacity_usd': plan, 'capacity_instant_usd': inst, 'oi_hl': hl_oi,
                         'oi_bn': bk.get('oi_bn'), 'depth25_min': bk.get('depth25_min'),
                         'hl_depth25_min': bk.get('hl_depth25_min'), 'size_10bp_short_hl': bk.get('size_10bp_short_hl'),
                         'hl_weekday_depth25_bid': wk.get('depth25_bid_usd'),
                         'hl_weekday_depth25_ask': wk.get('depth25_ask_usd')})
        notional = sum(x['capacity_usd'] or 0 for x in rows)
        inst_n = sum(x['capacity_instant_usd'] or 0 for x in rows)
        capital = notional * r['capital_per_notional']
        cap_rows[label] = {'basket_from': r['baskets'][-1][0], 'names': rows, 'notional_usd': notional,
                           'capital_usd': capital, 'instant_notional_usd': inst_n,
                           'usd_per_year_over_ssr_at_oos_excess': capital * (r['oos_excess'] or 0.0),
                           'usd_per_year_over_ssr_instant': inst_n * r['capital_per_notional'] * (r['oos_excess'] or 0.0),
                           'note': 'capacity_usd = 5% of open interest (HL for the broker version, the smaller venue '
                                   'for the two-perp one); capacity_instant_usd = also capped at the depth within '
                                   '25bp on the Saturday 2026-10-10 books (HL only for the broker version)'}
    A['carry_capacity'] = cap_rows

    # 4b. where the carry lives: both always-on carries (equal weight, no selection, no costs) by HL open interest
    oi_now = {c: (v or {}).get('oi_usd') for c, v in ctx.items()}
    uni_oi = {m['coin']: (m.get('oi') or 0) * (m.get('mark') or 0) for m in uni['markets']}
    oi_of = lambda c: oi_now.get(c) if oi_now.get(c) is not None else uni_oi.get(c, 0.0)  # noqa: E731
    split_day = A['carries'].get('xyz_broker_all', {}).get('test_from') or '2026-07-15'
    buckets = (('oi_under_5m', lambda c: oi_of(c) < 5e6), ('oi_5m_to_20m', lambda c: 5e6 <= oi_of(c) < 20e6),
               ('oi_over_20m', lambda c: oi_of(c) >= 20e6), ('all', lambda c: True))
    liq = {}
    for label, rows_by, cap_, key in (('broker_xyz', v_broker_all, 1.5, 'funding'),
                                      ('two_perp_twins', v_pair, 1.0, 'spread')):
        out_b = {}
        for bname, filt in buckets:
            for half, lo, hi in (('first', '0000', split_day), ('second', split_day, '9999')):
                byday = {}
                for c, rows in rows_by.items():
                    if not filt(c):
                        continue
                    for x in rows:
                        if lo <= x['d'] < hi:
                            byday.setdefault(x['d'], []).append(x)
                if not byday:
                    continue
                s_ = [sum(x['pnl'] for x in v) / len(v) for _, v in sorted(byday.items())]
                f_ = [sum(x[key] for x in v) / len(v) for _, v in sorted(byday.items())]
                ex = [(x - SSR / 252 * cap_) / cap_ for x in s_]
                out_b['%s_%s' % (bname, half)] = {
                    'days': len(s_), 'names': len({c for c, rows in rows_by.items() if filt(c)}),
                    'pnl_per_notional_apr': mean(s_) * 252, 'funding_apr': mean(f_) * 252,
                    'excess_on_capital': mean(ex) * 252, 't': B.newey_west_t(ex)[0]}
        liq[label] = out_b
    A['liquidity_split'] = {'split_day': split_day, 'note': 'equal-weight always-on rows, no selection and no costs; '
                            'buckets by HL open interest on 2026-10-10 (a description, not a tradeable filter)',
                            'carries': liq}

    # 6. off-hours: the two hedges while the cash market is shut
    periods = EO.closed_periods(days)
    off_rows, como = [], {}
    for p in eq_pairs:
        mh = load_hl(p['hl'], out)
        b = load_bn(out, p['bn'])
        st = ms_of(p['start'][:10])
        rows = closed_period_rows(mh, b, periods, max(st, t0))
        for r in rows:
            r['coin'] = p['hl']
        off_rows += rows
        como[p['hl']] = comovement(mh, b, state, max(st, t0))
    off = {}
    for kind in ('overnight', 'weekend', 'holiday'):
        rr = [r for r in off_rows if r['kind'] == kind]
        if not rr:
            continue
        off[kind] = {'name_periods': len(rr), 'perp_up': quantiles([r['perp_up'] for r in rr]),
                     'basis_up': quantiles([r['basis_up'] for r in rr]),
                     'perp_abs': quantiles([max(r['perp_up'], r['perp_down']) for r in rr]),
                     'basis_abs': quantiles([max(r['basis_up'], r['basis_down']) for r in rr]),
                     'basis_gap_open_abs': quantiles([abs(r['basis_gap_open']) for r in rr
                                                      if r['basis_gap_open'] is not None]),
                     'perp_gap_open_abs': quantiles([abs(r['perp_gap_open']) for r in rr
                                                     if r['perp_gap_open'] is not None])}
    liquid = {p['hl'] for p in eq_pairs if (oi_of(p['hl']) or 0) >= 5e6}
    for kind in ('overnight', 'weekend'):
        rr = [r for r in off_rows if r['kind'] == kind and r['coin'] in liquid]
        if rr:
            off['%s_hl_oi_over_5m' % kind] = {
                'name_periods': len(rr), 'perp_up': quantiles([r['perp_up'] for r in rr]),
                'basis_up': quantiles([r['basis_up'] for r in rr]),
                'perp_abs': quantiles([max(r['perp_up'], r['perp_down']) for r in rr]),
                'basis_abs': quantiles([max(r['basis_up'], r['basis_down']) for r in rr]),
                'basis_gap_open_abs': quantiles([abs(r['basis_gap_open']) for r in rr
                                                 if r['basis_gap_open'] is not None]),
                'perp_gap_open_abs': quantiles([abs(r['perp_gap_open']) for r in rr
                                                if r['perp_gap_open'] is not None])}
    worst = sorted(off_rows, key=lambda r: -max(r['basis_up'], r['basis_down']))[:10]
    cm = {}
    for s in ('session', 'offhours', 'weekend'):
        xs = [v[s] for v in como.values() if s in v]
        if xs:
            cm[s] = {'pairs': len(xs), 'median_corr': median([x['corr'] for x in xs]),
                     'median_sd_hl_bp': median([x['sd_hl_bp'] for x in xs]),
                     'median_sd_basis_bp': median([x['sd_basis_bp'] for x in xs]),
                     'median_var_hedged': median([x['hedge_ratio_var'] for x in xs])}
    A['offhours'] = {'by_kind': off, 'worst_basis_periods': worst, 'comovement': cm, 'per_pair_comovement': como}
    print('off-hours: %d name-periods, %.1fs' % (len(off_rows), time.time() - t_run), flush=True)

    # 7. HL funding by state on the matched markets, and the commodities
    A['hl_matched_funding'] = hl_funding_summary(pairs, out, state)
    A['energy_rolls'] = {c: roll_study(out, c) for c in ENERGY}
    A['pairs'] = {'n': len(pairs), 'kinds': {k: sum(1 for p in pairs if p['kind'] == k) for k in ('same', 'proxy')},
                  'rejects': pj.get('rejects'), 'unmatched_hl': len(pj.get('unmatched_hl') or []),
                  'by_class': {k: sum(1 for p in pairs if p['class'] == k) for k in sorted({p['class'] for p in pairs})}}
    A['seconds'] = round(time.time() - t_run, 1)
    write_json(out / 'analysis.json', A)
    print('analysis.json written, %.1fs' % (time.time() - t_run))


# ---------------------------------------------------------------------------------------------- render

def pc(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def nm(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


def usd(x):
    if x is None:
        return '—'
    a = abs(x)
    if a >= 1e6:
        return '$%.2fM' % (x / 1e6)
    if a >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# Binance TradFi perps vs HIP-3 — tables (generated %s)' % A['generated'], '']
    bn = A['binance']
    f = bn['formula']
    L += ['## 1. Binance TradFi funding', '',
          'Formula (h/8) x [P + clamp(I - P, +-0.05%%)], capped per symbol; I = 0 after the launch months. '
          'Reproduced from hourly premium-index bars: %s of %d settlements within 0.5bp, %s within 1bp; the '
          'zero/non-zero call agrees on %s. %s of settlements are exactly zero. Implied clamp median %s '
          '(IQR %s–%s, n %d).' % (pc(f['share_within_0.5bp']), f['checked'], pc(f['share_within_1bp']),
                                    pc(f['share_zero_class_agree']), pc(f['share_zero']),
                                    pc(f['implied_clamp_median'], 3),
                                    pc((f['implied_clamp_iqr'] or [None])[0], 3),
                                    pc((f['implied_clamp_iqr'] or [None, None])[1], 3), f['implied_clamp_n']), '',
          'Months with the interest leg on: ' + ', '.join('%s (%s)' % (m, ', '.join(v)) for m, v in
                                                         f['interest_leg_months'].items()), '',
          '| class | symbols | median APR since listing | hour-weighted | US session | weekday off-hours | weekend | '
          'last 90d median | zero settlements (median) | negative | symbols >= 8% | >= 5.7% |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    c90 = bn['by_class_last_90d']
    for k, v in bn['by_class'].items():
        s = v['by_state_hour_weighted']
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %d | %d |' % (
            k, v['symbols'], pc(v['median_apr']), pc(v['hour_weighted_apr']), pc(s.get('session')),
            pc(s.get('offhours')), pc(s.get('weekend')), pc((c90.get(k) or {}).get('median_apr')),
            pc(v['zero_share_median'], 0), pc(v['negative_share_median'], 0), v['symbols_over_8pct'],
            v['symbols_over_5_7pct']))
    cs = bn['constituents']
    L += ['', 'Index sources across %d symbols: %s. Hyperliquid (a HIP-3 market) is a constituent of %d indices: %s.' % (
        cs['symbols'], ', '.join('%s %d' % kv for kv in cs['source_counts'].items()), len(cs['hyperliquid_in_index']),
        ', '.join('%s (%s, %.1f%%)' % (x['symbol'], x['source'].split('//')[0], 100 * (x['weight'] or 0))
                  for x in cs['hyperliquid_in_index'])), '']
    sp = A['spreads']
    L += ['## 2. The pair family: funding spread HL - Binance', '',
          '%d pairs with two weeks of overlap; median spread %s a year; HL higher on %s of pairs; first-half vs '
          'second-half correlation of pair means %s, same sign %s.' % (
              sp['n'], pc(sp['median_spread_apr']), pc(sp['share_hl_higher'], 0), nm(sp['corr_halves']),
              pc(sp['same_sign_share'], 0)), '',
          '| pair | class | hours | HL APR | Binance APR | spread | first half | second half |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    for c, r in sorted(sp['pairs'].items(), key=lambda kv: -kv[1]['spread_apr']):
        L.append('| %s | %s | %d | %s | %s | %s | %s | %s |' % (c, r['class'], r['hours'], pc(r['hl_apr']),
                                                               pc(r['bn_apr']), pc(r['spread_apr']),
                                                               pc(r['first_half']), pc(r['second_half'])))
    g = A['pair_grid']
    L += ['', '## 3. Hourly pair grid (funding_arb machinery), chosen on the first half of pair-days', '',
          '| sample | pairs | variants | test from | chosen | in-sample Sharpe | test reserved APR | test deployed APR | '
          'test t (30d) | rank | DSR | test trades | net / year held | cost/trade |',
          '|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for gg in [g] + list(A.get('pair_grid_by_class', {}).values()):
        L.append('| %s | %d | %d | %s | `%s` | %s | %s | %s | %s | %d | %s | %d | %s | %sbp |' % (
            gg['label'], gg['pairs'], gg['variants'], gg['test_from'][:10], gg['chosen'],
            nm(gg['in_sample'].get('sharpe')), pc(gg['out_of_sample'].get('ann_return')), pc(gg['test_deployed_apr']),
            nm(gg['oos_t_30d']), gg['oos_rank'], nm(gg['deflated_sharpe_in_sample']), gg['test_trades'],
            pc(gg['test_net_per_year_held']), nm(gg['test_cost_per_trade_bp'], 1)))
    L += ['', 'Always-on (no signal), deployed APR before SSR, first half -> test (t, 30-day lags):', '']
    for gg in [g] + list(A.get('pair_grid_by_class', {}).values()):
        L.append('- %s: ' % gg['label'] + '; '.join(
            '%s %s -> %s (t %s)' % (k, pc(v['train_deployed_apr']), pc(v['test_deployed_apr']), nm(v['test_t']))
            for k, v in gg['always_on'].items()))
    L.append('')
    L += ['Chosen rule, test trades by class: ' + '; '.join(
        '%s %d trades, net %s / yr held (funding %s, basis %s)' % (k, v['trades'], pc(v['net_per_year_held']),
                                                                  pc(v['funding_per_year_held']),
                                                                  pc(v['basis_per_year_held']))
        for k, v in g['per_class_test'].items()), '']
    L += ['## 4. Daily carries on one calendar (%s to %s, %d sessions)' % (
        A['carry_calendar']['first'], A['carry_calendar']['last'], A['carry_calendar']['sessions']), '',
          'Excess over the 3.80%% savings rate, a year, on capital (broker legs 1.5x notional, two-perp 1.0x). Each '
          'family has six variants (all / trailing >= 8%% / top ten, two volume floors), chosen on the first half.', '',
          '| version | names | capital | chosen | test from | in-sample excess | Sharpe | OOS excess | OOS Sharpe | '
          'OOS t | rank | DSR | BH survivors | OOS basket funding | OOS basket P&L / notional |',
          '|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, r in A['carries'].items():
        if not r:
            continue
        L.append('| %s | %d | %.2f | `%s` | %s | %s | %s | %s | %s | %s | %d | %s | %d | %s | %s |' % (
            k, r.get('names', 0), r['capital_per_notional'], r['chosen'], r['test_from'], pc(r['in_sample_excess']),
            nm(r['in_sample_sharpe']), pc(r['oos_excess']), nm(r['oos_sharpe']), nm(r['oos_t']), r['oos_rank'],
            nm(r['deflated_sharpe_in_sample']), len(r['bh_survivors_full_sample']),
            pc(r['oos_basket_funding_apr']), pc(r['oos_basket_pnl_per_notional_apr'])))
    d = A['pair_daily_decomposition']
    L += ['', 'Two-perp rows, all twins and days: HL funding %s, Binance funding %s, basis %s a year per notional.' % (
        pc(d['f_hl_apr']), pc(d['f_bn_apr']), pc(d['basis_apr'])), '',
          '| month | name-days | HL funding | Binance funding | basis | net (a year, per notional) |',
          '|---|---:|---:|---:|---:|---:|']
    for m_, x in (d.get('monthly') or {}).items():
        L.append('| %s | %d | %s | %s | %s | %s |' % (m_, x['name_days'], pc(x['f_hl_apr']), pc(x['f_bn_apr']),
                                                    pc(x['basis_apr']), pc(x['net_apr'])))
    L.append('')
    ls_ = A.get('liquidity_split') or {}
    if ls_:
        L += ['Where the carry lives (equal-weight always-on rows, no selection, no costs; split at %s; buckets by HL '
              'open interest now):' % ls_['split_day'], '',
              '| carry | bucket | names | first half: P&L / notional | funding | excess on capital (t) | '
              'second half: P&L / notional | funding | excess on capital (t) |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
        for lab, d_ in ls_['carries'].items():
            for b_ in ('oi_under_5m', 'oi_5m_to_20m', 'oi_over_20m', 'all'):
                a_, z_ = d_.get(b_ + '_first') or {}, d_.get(b_ + '_second') or {}
                L.append('| %s | %s | %s | %s | %s | %s (%s) | %s | %s | %s (%s) |' % (
                    lab, b_, a_.get('names', z_.get('names', 0)), pc(a_.get('pnl_per_notional_apr')),
                    pc(a_.get('funding_apr')), pc(a_.get('excess_on_capital')), nm(a_.get('t')),
                    pc(z_.get('pnl_per_notional_apr')), pc(z_.get('funding_apr')), pc(z_.get('excess_on_capital')),
                    nm(z_.get('t'))))
        L.append('')
    for k, c in A['carry_capacity'].items():
        L += ['Capacity, %s (basket from %s): planning notional (5%% of OI) %s, capital %s, %s a year over SSR at the '
              'OOS excess; capped also at the Saturday depth within 25bp: %s notional, %s a year.' % (
                  k, c['basket_from'], usd(c['notional_usd']), usd(c['capital_usd']),
                  usd(c['usd_per_year_over_ssr_at_oos_excess']), usd(c.get('instant_notional_usd')),
                  usd(c.get('usd_per_year_over_ssr_instant'))), '',
              '| name | 5% of OI | with depth cap | HL OI | Binance OI | HL depth 25bp (Sat, min side) | '
              'HL depth 25bp bid/ask (2026-09-10 in session) | both venues min depth 25bp | size at 10bp (short HL) |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for x in c['names']:
            L.append('| %s | %s | %s | %s | %s | %s | %s / %s | %s | %s |' % (
                x['coin'], usd(x['capacity_usd']), usd(x.get('capacity_instant_usd')), usd(x['oi_hl']),
                usd(x['oi_bn']), usd(x.get('hl_depth25_min')), usd(x.get('hl_weekday_depth25_bid')),
                usd(x.get('hl_weekday_depth25_ask')), usd(x['depth25_min']), usd(x['size_10bp_short_hl'])))
        L.append('')
    o = A['offhours']
    L += ['## 5. While the cash market is shut: broker hedge vs Binance hedge', '',
          '| period | name-periods | perp up p50 / p95 / p99 / max (broker short) | basis up p50 / p95 / p99 / max '
          '(two-perp short) | basis gap at open, abs p50 / p95 |', '|---|---:|---|---|---|']
    for k, v in o['by_kind'].items():
        pu, bu, bg = v['perp_up'], v['basis_up'], v['basis_gap_open_abs']
        L.append('| %s | %d | %s / %s / %s / %s | %s / %s / %s / %s | %s / %s |' % (
            k, v['name_periods'], pc(pu.get('p50'), 2), pc(pu.get('p95'), 2), pc(pu.get('p99'), 2),
            pc(pu.get('max'), 2), pc(bu.get('p50'), 2), pc(bu.get('p95'), 2), pc(bu.get('p99'), 2),
            pc(bu.get('max'), 2), pc(bg.get('p50'), 2), pc(bg.get('p95'), 2)))
    L += ['', '| hours | pairs | median corr | median sd HL (bp) | median sd basis (bp) | variance hedged |',
          '|---|---:|---:|---:|---:|---:|']
    for k, v in o['comovement'].items():
        L.append('| %s | %d | %s | %s | %s | %s |' % (k, v['pairs'], nm(v['median_corr']), nm(v['median_sd_hl_bp'], 1),
                                                    nm(v['median_sd_basis_bp'], 1), pc(v['median_var_hedged'])))
    L += ['', 'Worst basis excursions: ' + '; '.join('%s %s %s %s' % (r['coin'], r['d0'], r['kind'],
                                                                     pc(max(r['basis_up'], r['basis_down']), 2))
                                                    for r in o['worst_basis_periods']), '']
    L += ['## 6. Energy: Binance index vs trade.xyz oracle around the GSCI roll', '']
    for c, r in A['energy_rolls'].items():
        if not r:
            continue
        L += ['**%s / %s** (%d hours; sd of the hourly log-ratio change %sbp)' % (c, r['bn'], r['hours'],
                                                                                 nm(r['sd_dq_bp'], 1)), '',
              '| month | xyz rolls | ratio change at the five step hours (bp) | sum | pair short xyz: HL funding | '
              'Binance funding | basis | net |', '|---|---|---|---:|---:|---:|---:|---:|']
        for m in r['months']:
            pz = m['pair_short_xyz']
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                m['month'], m['xyz_rolls'], ' '.join(nm(x * 1e4 if x is not None else None, 0) for x in m['step_dq']),
                nm(m['sum_step_dq'] * 1e4 if m['sum_step_dq'] is not None else None, 0), pc(pz['f_hl'], 2),
                pc(pz['f_bn'], 2), pc(pz['basis'], 2), pc(pz['net'], 2)))
        ow = r.get('october_weights')
        if ow:
            L += ['', 'October front weights (%s / %s): ' % (ow['front'], ow['second']) + '; '.join(
                '%s Binance %s xyz %s' % (dd, nm(v['bn_w']), nm(v['xyz_w'])) for dd, v in ow['days'].items())]
        L += ['', 'Largest hourly ratio moves off the xyz schedule: ' + ', '.join(
            '%s %+.0fbp' % (x['utc'][:13], x['dq_bp']) for x in r['largest_off_schedule_moves'][:6]), '']
    pr = A['pairs']
    L += ['## 7. Matching', '', '%d pairs (%s), by Binance class %s; %d HIP-3 markets have no Binance twin; '
          'rejected on price: %s.' % (pr['n'], pr['kinds'], pr['by_class'], pr['unmatched_hl'],
                                      ', '.join('%s/%s (%s)' % (r['hl'], r['bn'], r.get('reason')) for r in
                                                (pr['rejects'] or []) if r.get('reason') != 'no Binance data'))]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    man = {'generated': utc(), 'code': {}, 'sources': {
        'binance': {'endpoint': BN, 'calls': ['/fapi/v1/exchangeInfo', '/fapi/v1/fundingInfo', '/fapi/v1/premiumIndex',
                                              '/fapi/v1/ticker/24hr', '/fapi/v1/fundingRate (paged)',
                                              '/fapi/v1/klines 1h', '/fapi/v1/premiumIndexKlines 1h',
                                              '/fapi/v1/indexPriceKlines 1h', '/fapi/v1/constituents',
                                              '/fapi/v1/openInterest', '/futures/data/openInterestHist 1d',
                                              '/fapi/v1/depth 500']},
        'hyperliquid': {'stores': [str(p.relative_to(ROOT)) for p in HL_STORES],
                        'topup': 'raw/hl_topup (fundingHistory, candleSnapshot 1h from 2026-10-09)',
                        'books': 'l2Book (fine and nSigFigs 4), metaAndAssetCtxs per dex'},
        'yahoo': 'v8 chart 1d with dividends and splits (UA Mozilla/5.0)',
        'equity_offhours': str(EQ_DIR.relative_to(ROOT)) + ' (Nasdaq refs, book costs)',
        'roll_carry': str(RC_YAHOO.relative_to(ROOT)) + ' (contract-month futures, 60m)'}}
    import hashlib
    for f_ in ('scripts/tradfi_perps.py', 'scripts/funding_arb.py', 'scripts/equity_offhours.py', 'scripts/backtest.py',
               'scripts/roll_carry.py'):
        man['code'][f_] = hashlib.sha256((ROOT / f_).read_bytes()).hexdigest()[:16]
    for name in ('collect_manifest.json',):
        p = out / name
        if p.exists():
            cm = json.loads(p.read_text())
            man['collect'] = {k: cm.get(k) for k in ('generated', 'symbols', 'failures', 'http', 'http_funding',
                                                      'seconds')}
            man['collect']['rows'] = {k: sum((v.get(k) or 0) for v in cm['per_symbol'].values())
                                      for k in ('funding_rows', 'klines_rows', 'premium_rows', 'index_rows')}
    for name, sub in (('hl_topup', 'raw/hl_topup/manifest.json'), ('yahoo', 'raw/yahoo/manifest.json')):
        p = out / sub
        if p.exists():
            d = json.loads(p.read_text())
            man[name] = {'at': d.get('at'), 'failures': d.get('failures'),
                         'count': len(d.get('coins') or d.get('got') or {}), 'api': d.get('api')}
    man['books'] = A['params'].get('snapshot')
    man['analysis_seconds'] = A.get('seconds')
    man['counts'] = {'binance_symbols': A['binance']['symbols'], 'pairs': A['pairs']['n'],
                     'grid_pairs': A['pair_grid']['pairs'], 'variants_grid': A['pair_grid']['variants'],
                     'carry_variants_per_family': 6, 'carry_families': len(A['carries'])}
    write_json(out / 'manifest.json', man)
    print('tables.md, manifest.json written')


# ---------------------------------------------------------------------------------------------- main (collect side)

def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect', help='Binance TradFi perps: funding, 1h klines/premium/index, constituents, OI')
    c.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    c.add_argument('--only', help='comma-separated symbols')
    c.add_argument('--refresh', action='store_true')
    c.add_argument('--workers', type=int, default=6)
    c.set_defaults(fn=cmd_collect)
    h = sub.add_parser('hl-topup', help='HIP-3 funding and 1h candles after the shared store ends (paced)')
    h.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    h.add_argument('--since', default='2026-10-09T00:00:00')
    h.add_argument('--extra', help='comma-separated HIP-3 coins to add')
    h.add_argument('--interval', type=float, default=0.35)
    h.set_defaults(fn=cmd_hl_topup)
    s = sub.add_parser('stocks', help='Yahoo daily closes and dividends for the US underlyings')
    s.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    s.add_argument('--since', default='2025-11-01')
    s.add_argument('--only')
    s.add_argument('--refresh', action='store_true')
    s.add_argument('--pause', type=float, default=0.8)
    s.set_defaults(fn=cmd_stocks)
    m = sub.add_parser('match', help='pair each HIP-3 market with its Binance twin, checked on price')
    m.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    m.set_defaults(fn=cmd_match)
    b = sub.add_parser('books', help='live books on both venues for the matched pairs, and open interest')
    b.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    b.add_argument('--interval', type=float, default=0.35)
    b.set_defaults(fn=cmd_books)
    a = sub.add_parser('analyze', help='funding, pair grid, carries, off-hours basis, capacity, energy rolls')
    a.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    a.add_argument('--grid-start', default='2026-03-16')
    a.add_argument('--carry-start', default='2026-03-16')
    a.set_defaults(fn=cmd_analyze)
    r = sub.add_parser('render', help='tables.md and manifest.json from analysis.json')
    r.add_argument('--out', default='research/2026-10-10/tradfi_perps')
    r.set_defaults(fn=cmd_render)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.fn(args)


if __name__ == '__main__':
    main()
