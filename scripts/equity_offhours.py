#!/usr/bin/env python3
"""HIP-3 equity and index perps while the cash market is shut: who discovers the price, and does the off-hours move
predict the open?

Why. Hyperliquid's builder DEXes (trade.xyz, Paragon, Markets by Kinetiq, EntropyIO) list perpetuals on US stocks,
ETFs and indices that trade every hour of the week, while the stock trades 6.5 hours a day on five days. For the 17.5
hours between a close and the next open, and the 65.5 hours of a weekend, the perp is the only market quoting the name
(apart from thin pre-market and overnight venues). Two questions follow, and both are answerable from data this repo
already collects:

  * **price discovery** — by the last hour before the open, how much of the cash gap (close -> open) has the perp
    already moved, and how well does its move predict the gap? That is an insight about the venue even if nothing
    trades on it.
  * **tradability** — the deployer's oracle is the stock price when the stock trades. What is it when the stock does
    not, what does funding charge over those hours, and is there a rule, chosen on the first half of the history and
    tested once on the second, that makes money across the open after fees, spread and funding?

Definitions, used everywhere.

  * A *closed period* runs from one trading day's close (16:00 ET, 13:00 on the exchange's half days) to the next
    trading day's open (09:30 ET). Trading days are the dates the reference series itself prints (SPY's Nasdaq history),
    so holidays need no list; half days do, and are in `HALF_DAYS`. Eastern time is UTC-4 from the second Sunday of
    March to the first Sunday of November and UTC-5 otherwise, computed exactly rather than by month.
  * The perp's price *at* an instant T is the close of the hourly candle that ends at T (Hyperliquid candles are
    stamped with their open time). Closes and pre/post-open marks all fall on hour boundaries: the open is at :30 UTC
    in both seasons, so `pre` = open - 30 min is the last hour boundary before the open and `post` = open + 30 min the
    first after it.
  * Hyperliquid's funding row at T carries the hour's *average* premium P (sampled every few seconds against impact
    prices, not the mark) and the rate paid at T. For the builder markets studied here the rate is
    mult * (P + clamp(I - P, -0.0003, 0.0003)) / 8 per hour: a dead zone in which longs pay the interest leg I
    whatever the premium, and `mult` of the premium beyond it. trade.xyz uses mult 0.5 and I = 0.01% per 8 h (6.25e-6
    an hour, 5.5% a year), Paragon 0.6, Markets by Kinetiq 1.0 with a 5%-a-year I (`FUND_PARAMS`); `analyze` reports
    how many rows the formula reproduces. The *implied oracle* for an hour is the hour's average trade price /
    (1 + P), exact up to half the impact spread.
  * Returns are fractions of notional. Sessions are the unit of time for inference (one closed period each, about 252
    a year); names traded in the same session are averaged first, so a market-wide gap is one observation, not sixty.

    uv run python scripts/equity_offhours.py collect --out research/2026-10-09/equity_offhours
    uv run python scripts/equity_offhours.py books   --out research/2026-10-09/equity_offhours   # l2Book, <= 1/s
    uv run python scripts/equity_offhours.py analyze --out research/2026-10-09/equity_offhours
    uv run python scripts/equity_offhours.py render  --out research/2026-10-09/equity_offhours
"""
import argparse
import datetime as dt
import gzip
import json
import math
import statistics
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

HOUR_MS = 3_600_000
DAY = dt.timedelta(days=1)
# Oldest first: a store's last hourly candle was still forming when it was collected, so a later store's complete
# candle for the same hour must overwrite it when the stores are merged.
STORES = [ROOT / 'research/2026-09-10/perps_history', ROOT / 'research/2026-10-09/perps_hip3',
          ROOT / 'research/2026-10-09/perps_history']
REF_MAP = ROOT / 'research/2026-09-10/perps_daily/refs/map.json'
CANDLES_4H = ROOT / 'research/2026-10-09/equity_offhours/raw/candles_4h'
BOOK_SNAPS = {'pre_open': ROOT / 'research/2026-09-10/perps_2/books',      # 2026-09-10 12:21 UTC, 69 min before the open
              'in_session': ROOT / 'research/2026-09-10/perps_daily/books'}  # 2026-09-10 14:00 UTC, 30 min after it
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/128.0 Safari/537.36')
NASDAQ = 'https://api.nasdaq.com/api/quote/%s/%s?%s'

# NYSE/Nasdaq early closes (13:00 ET) inside or near the sample. 2026-07-02 is not one: when July 4 falls on a Saturday
# the holiday is the Friday and the Thursday trades a full day (as in 2015 and 2020).
HALF_DAYS = {dt.date(2025, 7, 3), dt.date(2025, 11, 28), dt.date(2025, 12, 24),
             dt.date(2026, 11, 27), dt.date(2026, 12, 24)}

# Index perps quote index points; the cash gap is read from the ETF that tracks the index, because an index's printed
# "open" is computed from components that have not all opened at 09:30 and so understates the gap.
INDEX_PROXY = {'SP:SPX': ('SPY', 'etf'), 'NASDAQ:NDX': ('QQQ', 'etf')}
US_EXCHANGES = {'NASDAQ', 'NYSE', 'AMEX', 'BATS'}
CRYPTO_LINKED = {'COIN', 'MSTR', 'HOOD', 'CRCL', 'BMNR', 'IREN', 'CIFR', 'STRC', 'GLXY', 'RIOT', 'MARA'}

FUND_MULT = 0.5           # trade.xyz's funding multiplier (universe.json `funding_multiplier`)
FUND_INTEREST = 0.0001    # 0.01% per 8 h
FUND_CLAMP = 0.0003       # the dead-zone half width every builder market here uses (core Hyperliquid uses 0.0005)
# Per-dex (multiplier, interest per 8 h), fitted to the funding rows and reproduced on 99.98% (xyz), 99.99% (para)
# and 100% (mkts) of them: Paragon pays 0.6 of the premium, Markets by Kinetiq the whole premium with a 5%-a-year
# interest leg. EntropyIO's recent rows fit xyz's parameters; its older rows used other multipliers.
FUND_PARAMS = {'xyz': (0.5, 0.0001), 'para': (0.6, 0.0001), 'io': (0.5, 0.0001), 'mkts': (1.0, 0.05 / 1095)}
BASE_TAKER_BPS = 4.5      # Hyperliquid tier-0 perp taker fee


# ---------------------------------------------------------------------------------------------- small helpers

def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_json(p, v):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=1, sort_keys=True, default=str))


def safe(coin):
    return coin.replace(':', '__').replace('/', '_')


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_num(s):
    """Nasdaq prints '$375.00', '30,725.81', '--' or 'N/A'."""
    if s is None:
        return None
    s = str(s).replace('$', '').replace(',', '').strip()
    if s in ('', '--', 'N/A', 'NA'):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def mean(x):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) if x else None


def median(x):
    x = [v for v in x if v is not None]
    return statistics.median(x) if x else None


def bps(x):
    """Mean of a list in basis points, None when the list is empty."""
    m = mean(x)
    return None if m is None else 1e4 * m


# ---------------------------------------------------------------------------------------------- calendar

def nth_weekday(year, month, weekday, n):
    """The n-th (1-based) given weekday (Monday = 0) of a month."""
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def us_dst(d):
    """Whether US Eastern daylight time is in force during the trading day on date `d`: from the second Sunday of
    March to the first Sunday of November (the switch happens at 02:00 on those Sundays, never in a session)."""
    return nth_weekday(d.year, 3, 6, 2) <= d < nth_weekday(d.year, 11, 6, 1)


def et_utc_ms(d, hour, minute=0):
    off = 4 if us_dst(d) else 5
    t = dt.datetime(d.year, d.month, d.day, hour, minute, tzinfo=dt.timezone.utc) + dt.timedelta(hours=off)
    return int(t.timestamp() * 1000)


def open_ms(d):
    return et_utc_ms(d, 9, 30)


def close_ms(d):
    return et_utc_ms(d, 13, 0) if d in HALF_DAYS else et_utc_ms(d, 16, 0)


def closed_periods(days):
    """Every closed period between consecutive trading days. `kind` is 'overnight' (next calendar day), 'weekend'
    (Friday to Monday) or 'holiday' (anything longer, or a mid-week closure)."""
    days = sorted(days)
    out = []
    for d0, d1 in zip(days, days[1:]):
        gap_days = (d1 - d0).days
        if gap_days == 1:
            kind = 'overnight'
        elif gap_days == 3 and d0.weekday() == 4:
            kind = 'weekend'
        else:
            kind = 'holiday'
        c0, o1 = close_ms(d0), open_ms(d1)
        out.append({'d0': d0.isoformat(), 'd1': d1.isoformat(), 'kind': kind, 'half_day_close': d0 in HALF_DAYS,
                    'close_ms': c0, 'open_ms': o1, 'pre_ms': o1 - HOUR_MS // 2, 'post_ms': o1 + HOUR_MS // 2,
                    'post2_ms': o1 + 3 * HOUR_MS // 2, 'close1_ms': close_ms(d1),
                    'closed_hours': (o1 - c0) / HOUR_MS})
    return out


# ---------------------------------------------------------------------------------------------- funding and oracle

def funding_rate(premium, mult=FUND_MULT, interest=FUND_INTEREST, clamp=FUND_CLAMP):
    """Hourly funding for a builder market given the hour's average premium (positive = longs pay)."""
    adj = max(-clamp, min(clamp, interest - premium))
    return mult * (premium + adj) / 8.0


def funding_params(coin):
    """(multiplier, interest per 8 h) for a builder market, from its dex."""
    return FUND_PARAMS.get(coin.split(':', 1)[0], (FUND_MULT, FUND_INTEREST))


def implied_oracle(avg_price, premium):
    """The oracle an hour's average price and average premium imply; premium = (impact price - oracle) / oracle."""
    if avg_price is None or premium is None or premium <= -1:
        return None
    return avg_price / (1.0 + premium)


# ---------------------------------------------------------------------------------------------- reference data

def http_json(url, retries=3, pause=1.0):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json',
                                               'Accept-Language': 'en-US,en;q=0.9'})
    last = None
    for a in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001 - recorded and retried
            last = e
            time.sleep(pause * (a + 1) * 2)
    raise RuntimeError('%s: %s' % (url, last))


def nasdaq_history(sym, assetclass, start, end):
    q = urllib.parse.urlencode({'assetclass': assetclass, 'fromdate': start, 'todate': end, 'limit': 9999})
    d = http_json(NASDAQ % (sym, 'historical', q))
    rows = (((d.get('data') or {}).get('tradesTable') or {}).get('rows')) or []
    out = {}
    for r in rows:
        try:
            day = dt.datetime.strptime(r['date'], '%m/%d/%Y').date().isoformat()
        except (KeyError, ValueError):
            continue
        o, c = parse_num(r.get('open')), parse_num(r.get('close'))
        if o and c:
            out[day] = {'open': o, 'close': c, 'high': parse_num(r.get('high')), 'low': parse_num(r.get('low')),
                        'volume': parse_num(r.get('volume'))}
    return out


def nasdaq_dividends(sym):
    d = http_json(NASDAQ % (sym, 'dividends', 'assetclass=stocks'))
    rows = (((d.get('data') or {}).get('dividends') or {}).get('rows')) or []
    out = []
    for r in rows:
        try:
            ex = dt.datetime.strptime(r['exOrEffDate'], '%m/%d/%Y').date().isoformat()
        except (KeyError, ValueError):
            continue
        amt = parse_num(r.get('amount'))
        if amt and (r.get('type') or 'Cash') == 'Cash':
            out.append({'ex_date': ex, 'amount': amt, 'currency': r.get('currency')})
    return out


def reference_for(coin, m):
    """(nasdaq symbol, assetclass, kind) for a market whose TradingView reference is a US cash listing, else None."""
    tk, typ = m.get('ticker'), m.get('type')
    if not tk:
        return None
    if tk in INDEX_PROXY:
        sym, ac = INDEX_PROXY[tk]
        return sym, ac, 'index'
    ex, sym = tk.split(':', 1)
    if ex not in US_EXCHANGES or typ not in ('stock', 'dr', 'fund'):
        return None
    return sym.replace('.', '/'), ('etf' if typ == 'fund' else 'stocks'), ('etf' if typ == 'fund' else 'stock')


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    mp = json.loads(REF_MAP.read_text())
    uni = []
    for st in STORES:
        if (st / 'universe.json').exists():
            uni += [m['coin'] for m in json.loads((st / 'universe.json').read_text())['markets'] if m['dex'] != 'core']
    uni = sorted(set(uni))
    missing = [c for c in uni if c not in mp]
    resolved = {}
    if missing:
        # Same resolver the reference study used (TradingView scanner, first candidate that answers); every new
        # resolution is written beside its description so a wrong match is visible, and `--reject` drops it.
        import perp_refs
        found, _ = perp_refs.resolve_map([(c.split(':', 1)[0], c) for c in missing])
        resolved = found
    reject = set(args.reject or [])
    markets = {}
    for coin in uni:
        m = mp.get(coin) or resolved.get(coin) or {}
        ref = None if coin in reject else reference_for(coin, m)
        markets[coin] = {'ticker': m.get('ticker'), 'type': m.get('type'), 'description': m.get('description'),
                         'resolved_this_run': coin in resolved, 'rejected': coin in reject,
                         'ref': ({'symbol': ref[0], 'assetclass': ref[1], 'kind': ref[2]} if ref else None)}
    syms = sorted({(v['ref']['symbol'], v['ref']['assetclass']) for v in markets.values() if v['ref']} | {('SPY', 'etf')})
    print(json.dumps({'markets': len(markets), 'referenced': sum(1 for v in markets.values() if v['ref']),
                      'new_resolved': len(resolved), 'symbols': len(syms)}), flush=True)
    log = []
    for sym, ac in syms:
        p = raw / 'nasdaq' / (sym.replace('/', '_') + '.json')
        if p.exists() and not args.refresh:
            continue
        try:
            rows = nasdaq_history(sym, ac, args.since, args.until)
            write_json(p, {'symbol': sym, 'assetclass': ac, 'fetched': utc(time.time() * 1000), 'rows': rows})
            log.append({'symbol': sym, 'rows': len(rows)})
        except RuntimeError as e:
            log.append({'symbol': sym, 'error': str(e)[:200]})
        time.sleep(args.pause)
        if ac == 'stocks':
            q = raw / 'dividends' / (sym.replace('/', '_') + '.json')
            try:
                write_json(q, {'symbol': sym, 'fetched': utc(time.time() * 1000), 'rows': nasdaq_dividends(sym)})
            except RuntimeError as e:
                log.append({'symbol': sym, 'dividends_error': str(e)[:200]})
            time.sleep(args.pause)
    write_json(out / 'markets.json', markets)
    man_p = out / 'manifest.json'
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    man['collect'] = {'at': utc(time.time() * 1000), 'since': args.since, 'until': args.until,
                      'reference_source': 'api.nasdaq.com/api/quote/{sym}/historical (daily official open/close)',
                      'dividend_source': 'api.nasdaq.com/api/quote/{sym}/dividends (stocks only; ETFs return none)',
                      'ref_map': str(REF_MAP.relative_to(ROOT)), 'symbols': len(syms),
                      'errors': [x for x in log if 'error' in x or 'dividends_error' in x], 'fetched': len(log)}
    write_json(man_p, man)
    print(json.dumps({'fetched': len(log), 'errors': len(man['collect']['errors'])}))
    return 0


def cmd_books(args):
    """l2Book for every referenced market at this moment, at most one call a second, plus each dex's meta for the
    growth-mode flag and the deployer fee scale (what decides the fee)."""
    from perp_rpc import Info, meta_and_ctxs
    out = Path(args.out)
    markets = json.loads((out / 'markets.json').read_text())
    api = Info(interval=max(1.0, args.interval))
    stamp = int(time.time())
    snap = {'ts': stamp, 'utc': utc(stamp * 1000), 'books': {}, 'meta': {}}
    for dex in sorted({c.split(':', 1)[0] for c, v in markets.items() if v['ref']}):
        m = meta_and_ctxs(api, dex)
        snap['meta'][dex] = [{'name': u['name'], 'growth_mode': u.get('growthMode'),
                              'deployer_fee_scale': u.get('deployerFeeScale'), 'mark': c.get('markPx'),
                              'oracle': c.get('oraclePx'), 'oi': c.get('openInterest'), 'day_ntl_vlm': c.get('dayNtlVlm')}
                             for u, c in zip(m[0]['universe'], m[1])]
    uni = latest_universe()
    coins = sorted((c for c, v in markets.items() if v['ref']), key=lambda c: -((uni.get(c) or {}).get('oi_usd') or 0))
    coins = sorted(args.coins) if args.coins else coins[:args.top]
    for coin in coins:
        try:
            snap['books'][coin] = api.post({'type': 'l2Book', 'coin': coin})
        except Exception as e:  # noqa: BLE001
            snap['books'][coin] = {'error': str(e)[:160]}
    p = out / 'raw' / 'books' / ('books_%d.json.gz' % stamp)
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, 'wt') as f:
        json.dump(snap, f)
    print(json.dumps({'snapshot': str(p), 'books': len(snap['books']), **api.stats()}))
    return 0


def cmd_candles4h(args):
    """4-hour candles for referenced markets whose funding history starts before the 1-hour candles do.

    Hyperliquid serves only the latest 5,000 bars of any interval, so the stores' hourly candles begin 2026-03-15.
    5,000 four-hour bars reach back about 833 days. They mark the daily carry at 20:00 UTC (the close in daylight time,
    an hour before it in standard time) and are never used where the open needs hourly precision. One call per
    market, at least a second apart."""
    from perp_rpc import Info, candles
    out = Path(args.out)
    markets = json.loads((out / 'markets.json').read_text())
    api = Info(interval=max(1.0, args.interval))
    end = int(time.time() * 1000)
    done = []
    for coin in sorted(c for c, v in markets.items() if v['ref']):
        m = load_market(coin)
        f0 = min(m['rate']) if m['rate'] else None
        if not m['px'] or f0 is None or f0 >= min(m['px']) - 24 * HOUR_MS:
            continue
        p = out / 'raw' / 'candles_4h' / (safe(coin) + '.json.gz')
        if p.exists() and not args.refresh:
            continue
        rows = candles(api, coin, '4h', f0 - 4 * HOUR_MS, end) or []
        p.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(p, 'wt') as fh:
            json.dump(rows, fh)
        done.append({'coin': coin, 'bars': len(rows), 'first': utc(rows[0]['t']) if rows else None})
    man_p = out / 'manifest.json'
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    man['candles_4h'] = {'at': utc(time.time() * 1000), 'markets': done, 'api': api.stats()}
    write_json(man_p, man)
    print(json.dumps({'markets': len(done), **api.stats()}))
    return 0


PREMARKET = {'TSLA': 'xyz:TSLA', 'NVDA': 'xyz:NVDA', 'AAPL': 'xyz:AAPL', 'AMZN': 'xyz:AMZN', 'META': 'xyz:META',
             'COIN': 'xyz:COIN', 'MSTR': 'xyz:MSTR', 'SPY': 'mkts:US500'}


def cmd_premarket(args):
    """Hourly bars with pre- and post-market prices for a few names, from Yahoo's chart API: 60 days, one call per
    symbol, three seconds apart, with the bare `Mozilla/5.0` agent (a full browser string is refused from this
    machine). Used once, to ask whether the perp at 09:00 ET is behind the pre-market tape or ahead of it."""
    out = Path(args.out) / 'raw' / 'yahoo'
    out.mkdir(parents=True, exist_ok=True)
    got = []
    for sym in sorted(PREMARKET):
        url = ('https://query1.finance.yahoo.com/v8/finance/chart/%s?range=60d&interval=1h&includePrePost=true' % sym)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=40) as r:
            (out / (sym + '.json')).write_bytes(r.read())
        got.append(sym)
        time.sleep(3.0)
    print(json.dumps({'symbols': got}))
    return 0


def premarket_compare(out, rows):
    """At the last hour boundary before the open (09:00 ET): the perp's price against the pre-market's last trade in
    the hour before (Yahoo's bar ending at the same instant), and which of the two the opening print was closer to.
    `pm_lead_slope` regresses the gap still open after the perp on the pre-market's deviation from it: 1 would mean
    the perp lags the pre-market tape and the deviation is a trade, 0 that it carries nothing."""
    by = {(r['coin'], r['d1']): r for r in rows}
    res, per = [], {}
    for sym, coin in sorted(PREMARKET.items()):
        p = Path(out) / 'raw' / 'yahoo' / (sym + '.json')
        if not p.exists():
            continue
        d = json.loads(p.read_text())['chart']['result'][0]
        q = d['indicators']['quote'][0]
        bars = {t * 1000: q['close'][i] for i, t in enumerate(d['timestamp']) if q['close'][i]}
        xs = []
        for (c, d1), r in by.items():
            if c != coin:
                continue
            pm = bars.get(r['pre_ms'] - HOUR_MS)
            if not pm or r.get('r_open') is None:
                continue
            x = {'sym': sym, 'd1': d1, 'dev': r['P_pre'] / pm - 1.0, 'e_perp': r['unpriced'],
                 'e_pm': r['C_open'] / pm - 1.0,
                 'r_open': r['r_open']}
            xs.append(x)
        if xs:
            per[sym] = {'n': len(xs), 'mean_abs_dev_bps': bps([abs(x['dev']) for x in xs]),
                        'mean_abs_open_vs_perp_bps': bps([abs(x['e_perp']) for x in xs]),
                        'mean_abs_open_vs_premarket_bps': bps([abs(x['e_pm']) for x in xs])}
        res += xs
    if not res:
        return None
    a, b, r2, n = ols([(-x['dev'], x['e_perp']) for x in res])
    a2, b2, r22, _ = ols([(-x['dev'], x['r_open']) for x in res])
    closer = sum(1 for x in res if abs(x['e_perp']) < abs(x['e_pm'])) / len(res)
    return {'name_sessions': len(res), 'first': min(x['d1'] for x in res), 'last': max(x['d1'] for x in res),
            'mean_abs_dev_bps': bps([abs(x['dev']) for x in res]),
            'median_abs_dev_bps': 1e4 * median([abs(x['dev']) for x in res]),
            'mean_abs_open_vs_perp_bps': bps([abs(x['e_perp']) for x in res]),
            'mean_abs_open_vs_premarket_bps': bps([abs(x['e_pm']) for x in res]),
            'share_open_closer_to_perp': closer,
            'pm_lead_slope': b, 'pm_lead_r2': r2, 'pm_lead_intercept_bps': 1e4 * a if a is not None else None,
            'r_open_on_pm_dev_slope': b2, 'r_open_on_pm_dev_r2': r22, 'per_symbol': per,
            'source': 'query1.finance.yahoo.com/v8/finance/chart (1h, includePrePost); last trade of the bar ending at 09:00 ET'}


# ---------------------------------------------------------------------------------------------- perp store

def load_market(coin, stores=STORES):
    """Hourly series for one market merged across stores: price at each hour boundary T (candle ending at T), the
    hour's average price, trade count and notional, and the funding row (premium, rate) stamped at T."""
    cand, fund = {}, {}
    for st in stores:
        cp = st / 'candles_1h' / (safe(coin) + '.json.gz')
        fp = st / 'funding' / (safe(coin) + '.json.gz')
        if cp.exists():
            for r in read_gz(cp):
                cand[int(r['t']) + HOUR_MS] = r
        if fp.exists():
            for r in read_gz(fp):
                fund[(int(r['time']) + HOUR_MS // 2) // HOUR_MS * HOUR_MS] = r
    px, avg, n, usd = {}, {}, {}, {}
    for T, r in cand.items():
        o, h, l, c = (fnum(r.get(k)) for k in ('o', 'h', 'l', 'c'))
        if not c:
            continue
        px[T] = c
        avg[T] = (o + h + l + c) / 4.0 if (o and h and l) else c
        n[T] = int(r.get('n') or 0)
        usd[T] = (fnum(r.get('v')) or 0.0) * avg[T]
    prem = {T: fnum(r.get('premium')) for T, r in fund.items()}
    rate = {T: fnum(r.get('fundingRate')) for T, r in fund.items()}
    px4, usd4 = {}, {}
    p4 = CANDLES_4H / (safe(coin) + '.json.gz')
    if p4.exists():
        for r in read_gz(p4):
            c = fnum(r.get('c'))
            if c and int(r.get('n') or 0) > 0:
                px4[int(r['t']) + 4 * HOUR_MS] = c
                usd4[int(r['t']) + 4 * HOUR_MS] = (fnum(r.get('v')) or 0.0) * c
    return {'coin': coin, 'px': px, 'avg': avg, 'n': n, 'usd': usd, 'prem': prem, 'rate': rate, 'px4': px4, 'usd4': usd4,
            'first': min(px) if px else None, 'last': max(px) if px else None,
            'first4': min(px4) if px4 else None}


def px_at(m, T, max_stale_h=2):
    """Last trade at or before hour boundary T, looking back at most `max_stale_h` hours of empty candles.
    Returns (price, hours stale) or (None, None)."""
    for k in range(max_stale_h + 1):
        t = T - k * HOUR_MS
        if t in m['px'] and (m['n'].get(t, 1) > 0):
            return m['px'][t], k
    return None, None


def funding_between(m, t0, t1):
    """Sum of hourly funding rates paid at boundaries in (t0, t1] (positive = longs paid), and how many were present."""
    s, k, hours = 0.0, 0, 0
    for T in range(t0 + HOUR_MS, t1 + 1, HOUR_MS):
        hours += 1
        r = m['rate'].get(T)
        if r is not None:
            s += r
            k += 1
    return s, k, hours


# ---------------------------------------------------------------------------------------------- session rows

def session_rows(m, ref, periods, divs=None, max_basis=0.03, scale=1.0):
    """One row per closed period the market has data for: perp prices at close/pre/post/post2/close1, the cash close
    and open, funding over the closed hours and over each holding window, and the sanity basis at the close.
    A period whose perp close sits more than `max_basis` from the cash close (split, mapping error, halted listing)
    is kept with `bad_basis` so the exclusion is counted, not silent. `scale` puts an index perp's points in its
    ETF's units for that check only; every return is scale-free."""
    divs = {d['ex_date']: d['amount'] for d in (divs or [])}
    rows = []
    for p in periods:
        c0, o1 = ref.get(p['d0']), ref.get(p['d1'])
        if not c0 or not o1:
            continue
        P_close, s_close = px_at(m, p['close_ms'])
        P_pre, s_pre = px_at(m, p['pre_ms'])
        P_post, s_post = px_at(m, p['post_ms'], max_stale_h=0)
        P_post2, _ = px_at(m, p['post2_ms'], max_stale_h=0)
        P_close1, _ = px_at(m, p['close1_ms'], max_stale_h=1)
        if not P_close or not P_pre:
            continue
        C_close, C_open, C_close1 = c0['close'], o1['open'], o1['close']
        basis = P_close / (scale * C_close) - 1.0
        f_closed, f_n, f_h = funding_between(m, p['close_ms'], p['open_ms'] - HOUR_MS // 2)
        row = dict(p)
        row.update({
            'coin': m.get('coin'),
            'P_close': P_close, 'P_pre': P_pre, 'P_post': P_post, 'P_post2': P_post2, 'P_close1': P_close1,
            'stale_close_h': s_close, 'stale_pre_h': s_pre,
            'C_close': C_close, 'C_open': C_open, 'C_close1': C_close1,
            'basis_close': basis, 'bad_basis': abs(basis) > max_basis,
            'gap': C_open / C_close - 1.0,
            'r_off': P_pre / P_close - 1.0,
            'unpriced': (C_open / C_close) / (P_pre / P_close) - 1.0,
            'r_open': (P_post / P_pre - 1.0) if P_post else None,
            'r_open2': (P_post2 / P_pre - 1.0) if P_post2 else None,
            'r_day': (P_close1 / P_pre - 1.0) if P_close1 else None,
            'funding_closed': f_closed, 'funding_closed_hours': f_h, 'funding_closed_present': f_n,
            'funding_pre_post': funding_between(m, p['pre_ms'], p['post_ms'])[0],
            'funding_pre_post2': funding_between(m, p['pre_ms'], p['post2_ms'])[0],
            'funding_pre_close1': funding_between(m, p['pre_ms'], p['close1_ms'])[0],
            'dividend': divs.get(p['d1']),
            'dividend_yield': (divs[p['d1']] / C_close) if p['d1'] in divs else None,
            'pre_hour_usd': m['usd'].get(p['pre_ms']), 'pre_hour_trades': m['n'].get(p['pre_ms']),
        })
        rows.append(row)
    return rows


def discovery_marks(m, periods_rows, marks_h=(0.5, 1.5, 2.5, 4.5, 6.5, 9.5, 13.5, 16.5)):
    """For each mark h hours before the open: the perp's return from the close to that mark, per session row."""
    out = {h: [] for h in marks_h}
    for r in periods_rows:
        for h in marks_h:
            T = r['open_ms'] - int(h * HOUR_MS)
            if T <= r['close_ms']:
                continue
            P, _ = px_at(m, T)
            if P:
                out[h].append((r['gap'], P / r['P_close'] - 1.0, r['d1'], r['kind']))
    return out


def spearman(pairs):
    """Rank correlation of (x, y) pairs (average ranks for ties)."""
    n = len(pairs)
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
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    a, b, r2, _ = ols(list(zip(rx, ry)))
    return None if r2 is None else math.copysign(math.sqrt(max(r2, 0.0)), b)


def origin_slope(pairs):
    """Least squares through the origin of y on x for (x, y) pairs, with R^2 of the same fit."""
    sxx = sum(x * x for x, _ in pairs)
    if sxx <= 0:
        return None, None
    b = sum(x * y for x, y in pairs) / sxx
    syy = sum(y * y for _, y in pairs)
    r2 = (1.0 - sum((y - b * x) ** 2 for x, y in pairs) / syy) if syy > 0 else None
    return b, r2


def ols(pairs):
    """y = a + b x for (x, y) pairs: (a, b, r2, n)."""
    n = len(pairs)
    if n < 3:
        return None, None, None, n
    mx = sum(x for x, _ in pairs) / n
    my = sum(y for _, y in pairs) / n
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    if sxx <= 0:
        return None, None, None, n
    b = sum((x - mx) * (y - my) for x, y in pairs) / sxx
    a = my - b * mx
    syy = sum((y - my) ** 2 for _, y in pairs)
    r2 = (1.0 - sum((y - a - b * x) ** 2 for x, y in pairs) / syy) if syy > 0 else None
    return a, b, r2, n


# ---------------------------------------------------------------------------------------------- costs

def walk_cost_bps(levels, side, mid, notional):
    """Average fill vs mid, in bps, for a market order of `notional` walking the saved levels; plus unfilled share."""
    book = levels[1] if side == 'buy' else levels[0]
    left, spent, filled = notional, 0.0, 0.0
    for lv in book:
        px, sz = float(lv['px']), float(lv['sz'])
        take = min(left, px * sz)
        spent += take
        filled += take / px
        left -= take
        if left <= 1e-9:
            break
    if filled <= 0:
        return None, 1.0
    avg = spent / filled
    return 1e4 * (avg - mid) / mid * (1 if side == 'buy' else -1), max(left, 0.0) / notional


def book_summary(levels, sizes=(1e4, 5e4, 1e5)):
    bids, asks = levels[0], levels[1]
    if not bids or not asks:
        return None
    bb, ba = float(bids[0]['px']), float(asks[0]['px'])
    mid = (bb + ba) / 2.0

    def depth(side, bps):
        lv = asks if side == 'ask' else bids
        lim = mid * (1 + bps / 1e4) if side == 'ask' else mid * (1 - bps / 1e4)
        return sum(float(x['px']) * float(x['sz']) for x in lv
                   if (float(x['px']) <= lim if side == 'ask' else float(x['px']) >= lim))

    s = {'mid': mid, 'spread_bps': 1e4 * (ba - bb) / mid,
         'depth25_bid_usd': depth('bid', 25), 'depth25_ask_usd': depth('ask', 25)}
    for z in sizes:
        b, ub = walk_cost_bps(levels, 'buy', mid, z)
        a, ua = walk_cost_bps(levels, 'sell', mid, z)
        s['half_rt_bps_%dk' % int(z / 1e3)] = (None if (b is None or a is None or ub > 0 or ua > 0)
                                               else (b + a) / 2.0)
    return s


def taker_fee_bps(growth_mode, fee_scale, base=BASE_TAKER_BPS):
    """All-in taker fee on a HIP-3 market: the protocol fee (cut 90% in growth mode) plus the deployer's share of it
    (0-300%, 0-100% in growth mode; above 100% the protocol fee rises to match). Hyperliquid fee docs, 2026-10."""
    scale = 1.0 if fee_scale is None else float(fee_scale)
    proto = base * (0.1 if growth_mode == 'enabled' else 1.0)
    if scale > 1.0:
        return proto * scale * 2.0
    return proto * (1.0 + scale)


def load_books(out):
    """Per-coin half round-trip cost and depth from the two 2026-09-10 snapshots (pre-open and in-session) and any
    snapshot `books` saved in this study; plus growth mode / fee scale from the newest meta."""
    res = {}
    for label, d in BOOK_SNAPS.items():
        if not d.exists():
            continue
        for p in d.glob('*.json.gz'):
            b = read_gz(p)
            coin = b.get('coin')
            if not coin or ':' not in coin:
                continue
            s = book_summary(b['levels'])
            if s:
                s['utc'] = utc(b['time'])
                s['levels'] = b['levels']
                res.setdefault(coin, {})[label] = s
    meta = {}
    snaps = sorted((Path(out).resolve() / 'raw' / 'books').glob('books_*.json.gz'))
    for p in snaps:
        sn = read_gz(p)
        for dex, rows in sn.get('meta', {}).items():
            for r in rows:
                meta[r['name']] = r
        for coin, b in sn.get('books', {}).items():
            if isinstance(b, dict) and b.get('levels'):
                s = book_summary(b['levels'])
                if s:
                    s['utc'] = sn['utc']
                    s['levels'] = b['levels']
                    res.setdefault(coin, {})['latest'] = s
    return res, meta, [str(p.relative_to(ROOT)) for p in snaps]


def fee_for(coin, meta, fee_case='schedule'):
    """Taker fee in bps. 'schedule' reads growth mode and the deployer scale from the latest meta (growth mode assumed
    on when unknown, as it was for 113 of 119 xyz markets on 2026-09-10); 'flat' is the repo's older 4.5bp convention;
    'no_growth' prices the market as if growth mode were switched off (2x the base fee)."""
    if fee_case == 'flat':
        return BASE_TAKER_BPS
    mt = meta.get(coin) or {}
    if fee_case == 'no_growth':
        return taker_fee_bps(None, mt.get('deployer_fee_scale', 1.0))
    return taker_fee_bps(mt.get('growth_mode', 'enabled'), mt.get('deployer_fee_scale', 1.0))


def trip_cost_bps(coin, books, meta, side, size, entry='pre_open', exit_='in_session', fee_case='schedule'):
    """Cost of opening `side` (+1 long, -1 short) at the `entry` book and closing at the `exit_` book for `size`
    dollars: both fees plus the walked fill against each book's mid. None if a book is missing or too thin."""
    bk = books.get(coin) or {}
    e, x = bk.get(entry) or bk.get('latest'), bk.get(exit_) or bk.get('latest')
    if not e or not x:
        return None
    ce, ue = walk_cost_bps(e['levels'], 'buy' if side > 0 else 'sell', e['mid'], size)
    cx, ux = walk_cost_bps(x['levels'], 'sell' if side > 0 else 'buy', x['mid'], size)
    if ce is None or cx is None or ue > 0 or ux > 0:
        return None
    return 2.0 * fee_for(coin, meta, fee_case) + ce + cx


def capacity_usd(coin, books, side, entry='pre_open', exit_='in_session', bps=25):
    """Depth within `bps` of mid on the side each leg takes: asks at entry and bids at exit for a long."""
    bk = books.get(coin) or {}
    e, x = bk.get(entry) or bk.get('latest'), bk.get(exit_) or bk.get('latest')
    if not e or not x:
        return None
    if side > 0:
        return min(e['depth25_ask_usd'], x['depth25_bid_usd'])
    return min(e['depth25_bid_usd'], x['depth25_ask_usd'])


# ---------------------------------------------------------------------------------------------- analysis

def load_refs(out):
    raw = Path(out) / 'raw'
    refs, divs = {}, {}
    for p in sorted((raw / 'nasdaq').glob('*.json')):
        d = json.loads(p.read_text())
        refs[d['symbol']] = d['rows']
    for p in sorted((raw / 'dividends').glob('*.json')):
        d = json.loads(p.read_text())
        divs[d['symbol']] = d['rows']
    return refs, divs


def session_bootstrap(rows, fn, n=500, seed=11):
    """Resample whole sessions (all names of a date together) and recompute `fn(rows)`: a 90% interval that respects
    the cross-sectional correlation of a market-wide gap."""
    import random
    by = {}
    for r in rows:
        by.setdefault(r['d1'], []).append(r)
    dates = sorted(by)
    if len(dates) < 5:
        return None, None
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        smp = []
        for _ in dates:
            smp.extend(by[dates[rng.randrange(len(dates))]])
        v = fn(smp)
        if v is not None:
            vals.append(v)
    vals.sort()
    if not vals:
        return None, None
    return vals[int(0.05 * (len(vals) - 1))], vals[int(math.ceil(0.95 * (len(vals) - 1)))]


def discovery_stats(rows):
    """Price discovery for a set of session rows: how much of the cash gap the perp had moved 30 minutes before the
    open (slope of r_off on gap through the origin), how well its move predicts the gap (OLS of gap on r_off), and how
    big the part left for the open is."""
    if len(rows) < 5:
        return {'n': len(rows)}
    share, r2o = origin_slope([(r['gap'], r['r_off']) for r in rows])
    a, b, r2, n = ols([(r['r_off'], r['gap']) for r in rows])
    lo, hi = session_bootstrap(rows, lambda s: origin_slope([(r['gap'], r['r_off']) for r in s])[0])
    return {
        'n': len(rows), 'sessions': len({r['d1'] for r in rows}), 'names': len({r['coin'] for r in rows}),
        'share_priced': share, 'share_priced_ci90': [lo, hi], 'r2_through_origin': r2o,
        'gap_on_perp_intercept_bps': (1e4 * a) if a is not None else None, 'gap_on_perp_slope': b, 'gap_on_perp_r2': r2,
        'mean_abs_gap_bps': 1e4 * mean([abs(r['gap']) for r in rows]),
        'mean_abs_unpriced_bps': 1e4 * mean([abs(r['unpriced']) for r in rows]),
        'median_abs_unpriced_bps': 1e4 * median([abs(r['unpriced']) for r in rows]),
        'mean_gap_bps': 1e4 * mean([r['gap'] for r in rows]),
        'mean_unpriced_bps': 1e4 * mean([r['unpriced'] for r in rows]),
        'corr_r_off_gap': (math.sqrt(r2) * (1 if (b or 0) >= 0 else -1)) if r2 is not None and r2 >= 0 else None,
    }


def oracle_stats(m, rows):
    """What the implied oracle does while the market is shut, and what funding charges then.

    `follow_slope`: regression through the origin of the oracle's log change on the perp's (same hours' average
    prices) from the last session hour to the last pre-open hour — 0 means frozen at the close, 1 means it moves with
    the perp. Premium and funding are split by whether the US cash session is open at that hour."""
    pairs = []
    for r in rows:
        t0, t1 = r['close_ms'], r['pre_ms']
        o0 = implied_oracle(m['avg'].get(t0), m['prem'].get(t0))
        o1 = implied_oracle(m['avg'].get(t1), m['prem'].get(t1))
        a0, a1 = m['avg'].get(t0), m['avg'].get(t1)
        if o0 and o1 and a0 and a1 and abs(math.log(a1 / a0)) > 0.002:
            pairs.append((math.log(a1 / a0), math.log(o1 / o0)))
    slope, r2 = origin_slope(pairs)
    return {'follow_slope': slope, 'follow_r2': r2, 'pairs': len(pairs)}


def hour_states(periods):
    """Map each hour boundary T to 'open' (cash session in progress for the hour ending at T) or 'closed'."""
    st = {}
    for p in periods:
        for T in range(p['close_ms'] + HOUR_MS, p['open_ms'] + HOUR_MS // 2, HOUR_MS):
            st[T] = 'closed'
    return st


def premium_by_state(m, states, t_lo, t_hi):
    out = {}
    fit = [0, 0]
    mult, interest = funding_params(m['coin'])
    for T, P in m['prem'].items():
        if P is None or T < t_lo or T > t_hi:
            continue
        s = states.get(T, 'open')
        d = out.setdefault(s, {'hours': 0, 'abs_prem': 0.0, 'outside_dead_zone': 0, 'rate_sum': 0.0})
        d['hours'] += 1
        d['abs_prem'] += abs(P)
        r = m['rate'].get(T)
        if r is not None:
            d['rate_sum'] += r
            fit[1] += 1
            if abs(funding_rate(P, mult, interest) - r) <= 1e-9 + 0.01 * abs(r):
                fit[0] += 1
        if not (interest - FUND_CLAMP <= P <= interest + FUND_CLAMP):
            d['outside_dead_zone'] += 1
    res = {}
    for s, d in out.items():
        h = max(d['hours'], 1)
        res[s] = {'hours': d['hours'], 'mean_abs_premium_bps': 1e4 * d['abs_prem'] / h,
                  'share_outside_dead_zone': d['outside_dead_zone'] / h,
                  'mean_funding_apr': d['rate_sum'] / h * 8760.0}
    return res, fit


# --- strategies ---------------------------------------------------------------------------------------------------

EXITS = {'post': ('r_open', 'funding_pre_post'), 'post2': ('r_open2', 'funding_pre_post2'),
         'close1': ('r_day', 'funding_pre_close1')}


def trade_return(row, side, exit_key, cost_bps):
    """Net return of `side` on the perp from the pre-open mark to `exit_key`: price move, funding received
    (-side x rate summed over the holding hours), minus the round-trip cost."""
    rk, fk = EXITS[exit_key]
    r = row.get(rk)
    if r is None or cost_bps is None:
        return None
    return side * r - side * row[fk] - cost_bps / 1e4


def family_open(rows_by_session, cost_of, dirs=('follow', 'fade'), ks=(0.0, 0.005, 0.01, 0.02),
                exits=('post', 'post2', 'close1'), subsets=('all', 'closed_long'), hedge=None, hedge_coin=None):
    """Position at 30 min before the open on the sign of the perp's own off-hours move (follow) or against it (fade),
    when |move| >= k; exit 30 min after the open, 90 min after, or at the close. Equal notional per traded name; a
    session's return is the mean over its trades (0 when flat).

    With `hedge` = {session: index row}, the signal is the name's move net of the index perp's over the same hours and
    every trade carries an equal and opposite index-perp leg over the same window (its move, funding and cost), so
    only the idiosyncratic part of the open is traded."""
    variants, trades = {}, {}
    sessions = sorted(rows_by_session)
    tag = 'hedged|' if hedge is not None else ''
    for d in dirs:
        for k in ks:
            for ex in exits:
                for sub in subsets:
                    name = '%s%s|k=%g|exit=%s|%s' % (tag, d, k, ex, sub)
                    ser, tr = [], []
                    for s in sessions:
                        rets = []
                        hx = hedge.get(s) if hedge is not None else None
                        if hedge is not None and hx is None:
                            ser.append(0.0)
                            continue
                        for row in rows_by_session[s]:
                            if sub == 'closed_long' and row['kind'] == 'overnight':
                                continue
                            if hedge is not None and row['coin'] == hedge_coin:
                                continue
                            sig = row['r_off'] - (hx['r_off'] if hx else 0.0)
                            if abs(sig) < max(k, 1e-12):
                                continue
                            side = (1 if sig > 0 else -1) * (1 if d == 'follow' else -1)
                            x = trade_return(row, side, ex, cost_of(row['coin'], side, ex))
                            if x is not None and hx is not None:
                                y = trade_return(hx, -side, ex, cost_of(hedge_coin, -side, ex))
                                x = None if y is None else x + y
                            if x is not None:
                                rets.append(x)
                                tr.append((s, row['coin'], side, x))
                        ser.append(mean(rets) if rets else 0.0)
                    variants[name] = ser
                    trades[name] = tr
    return sessions, variants, trades


def family_crypto(rows_by_session, btc, cost_of, ks=(0.0, 0.02)):
    """Crypto-linked names against Bitcoin's move over the same closed hours: follow or fade BTC's move, or the
    name's residual against it (BTC move minus the name's own), entering 30 min before the open, exiting 30 min after."""
    variants, trades = {}, {}
    sessions = sorted(rows_by_session)
    for sig in ('btc', 'residual'):
        for d in ('follow', 'fade'):
            for k in ks:
                name = 'crypto|%s|%s|k=%g' % (sig, d, k)
                ser, tr = [], []
                for s in sessions:
                    rets = []
                    for row in rows_by_session[s]:
                        if row['coin'].split(':', 1)[1] not in CRYPTO_LINKED:
                            continue
                        b0, _ = px_at(btc, row['close_ms'])
                        b1, _ = px_at(btc, row['pre_ms'])
                        if not b0 or not b1:
                            continue
                        rb = b1 / b0 - 1.0
                        x = rb if sig == 'btc' else rb - row['r_off']
                        if abs(x) < max(k, 1e-12):
                            continue
                        side = (1 if x > 0 else -1) * (1 if d == 'follow' else -1)
                        v = trade_return(row, side, 'post', cost_of(row['coin'], side, 'post'))
                        if v is not None:
                            rets.append(v)
                            tr.append((s, row['coin'], side, v))
                    ser.append(mean(rets) if rets else 0.0)
                variants[name] = ser
                trades[name] = tr
    return sessions, variants, trades


def carry_days(m, ref, days, divs=None, scale=1.0, max_basis=0.03):
    """Daily P&L, close to close, of short the perp / long the stock, per unit notional: the funding the short
    receives over the 24-odd hourly payments, the stock's price return plus any dividend going ex that day, and the
    perp's return against it. The stock is held through every closed period, so the open's gap cancels between the
    legs and what remains is funding plus the change in the perp-stock basis at the close."""
    divs = {d['ex_date']: d['amount'] for d in (divs or [])}
    out = []
    prev = None
    for d in days:
        ds = d.isoformat()
        c = ref.get(ds)
        T = close_ms(d)
        P, stale = px_at(m, T)
        src = '1h'
        if not P and m.get('px4'):
            # before the hourly candles begin: the 4-hour bar ending at or before the close (20:00 UTC)
            T4 = T // (4 * HOUR_MS) * (4 * HOUR_MS)
            P, stale, src = m['px4'].get(T4), 0, '4h'
            T = T4
        if not c or not P or stale is None or stale > 1:
            prev = None
            continue
        basis = P / (scale * c['close']) - 1.0
        if abs(basis) > max_basis:
            prev = None
            continue
        if prev is not None:
            f, k, h = funding_between(m, prev['T'], T)
            stock = c['close'] / prev['C'] - 1.0 + (divs.get(ds, 0.0) / prev['C'])
            perp = P / prev['P'] - 1.0
            if src == '1h':
                vol = sum(m['usd'].get(t, 0.0) for t in range(prev['T'] + HOUR_MS, T + 1, HOUR_MS))
            else:
                vol = sum(v for t, v in m.get('usd4', {}).items() if prev['T'] < t <= T)
            out.append({'d': ds, 'funding': f, 'funding_hours': h, 'funding_present': k, 'stock': stock,
                        'perp': perp, 'pnl': f + stock - perp, 'basis': basis, 'dividend': divs.get(ds),
                        'mark': src, 'vol_usd': vol})
        prev = {'T': T, 'C': c['close'], 'P': P}
    return out


def family_carry(per_coin_days, oi_usd, days, cost_bps, capital_per_notional=1.5, ssr=0.038, rebalance=21,
                 vol_floors=(5e5, 2e6), rules=('all', 'trail_8pct', 'top10')):
    """Hold short-perp / long-stock on a basket re-chosen every `rebalance` sessions from information before the
    rebalance date only: every name whose trailing-30-session perp volume averaged at least a floor a day ('all'),
    those of them whose trailing-30-session funding exceeded 8% a year, or the ten highest. The liquidity floor is the
    perp's own traded notional from the hourly candles, not today's open interest, so nothing is chosen with
    information from after the rebalance. Equal notional per name; a name entering or leaving pays `cost_bps[coin]`
    (both legs, round trip) on that notional. The series is the daily return on capital in excess of the savings
    rate: (P&L - ssr/252 * capital) / capital, with capital = stock notional plus perp margin. `oi_usd` is used only
    by the caller, to size the latest basket."""
    variants, members, raw = {}, {}, {}
    dlist = [d.isoformat() for d in days]
    by_coin = {c: {r['d']: r for r in rows} for c, rows in per_coin_days.items()}
    for floor in vol_floors:
        for rule in rules:
            name = 'carry|%s|vol>=%gM' % (rule, floor / 1e6)
            ser, basket, held, rw = [], set(), [], []
            for i, d in enumerate(dlist):
                if i % rebalance == 0:
                    cand = []
                    for c, rows in by_coin.items():
                        past_rows = [rows[x] for x in dlist[max(0, i - 30):i] if x in rows]
                        vols = [r['vol_usd'] for r in past_rows if r.get('vol_usd') is not None]
                        if len(past_rows) < 15 or not vols or sum(vols) / len(vols) < floor:
                            continue
                        past = [r['funding'] for r in past_rows]
                        cand.append((sum(past) / len(past) * 252, c))
                    if rule == 'all':
                        new = {c for _, c in cand}
                    elif rule == 'trail_8pct':
                        new = {c for a, c in cand if a >= 0.08}
                    else:
                        new = {c for _, c in sorted(cand, reverse=True)[:10]}
                    turn = (new ^ basket)
                    tc = sum((cost_bps.get(c) or 30.0) / 2.0 for c in turn) / 1e4 / max(len(new | basket), 1)
                    basket = new
                    held.append((d, sorted(basket)))
                else:
                    tc = 0.0
                pn = [by_coin[c][d]['pnl'] for c in basket if d in by_coin[c]]
                r = (mean(pn) if pn else 0.0) - tc
                ser.append((r - ssr / 252.0 * capital_per_notional) / capital_per_notional if pn else 0.0)
                rw.append((d, mean(pn) if pn else None, mean([by_coin[c][d]['funding'] for c in basket if d in by_coin[c]]),
                           tc, len(pn)))
            variants[name] = ser
            members[name] = held
            raw[name] = rw
    return dlist, variants, members, raw


def funding_persistence(markets_m, days, rebalance=21, trail=30, fwd=21, thresh=0.08):
    """Does the funding a name paid over the last 30 sessions predict the next 21? Uses funding rows alone, which reach
    back to each market's listing (the candles do not), so the persistence of the carry is tested on the whole history
    without any price marks. At each rebalance: the rank correlation across names of trailing and forward funding,
    and the forward funding (a year rate) of names whose trailing funding cleared `thresh` against all names."""
    bounds = [close_ms(d) for d in days]
    out = []
    for i in range(trail, len(days) - fwd, rebalance):
        t0, t1, t2 = bounds[i - trail], bounds[i], bounds[i + fwd]
        pairs, hi, al = [], [], []
        for coin, m in markets_m.items():
            tr = [r for T, r in m['rate'].items() if t0 < T <= t1 and r is not None]
            fw = [r for T, r in m['rate'].items() if t1 < T <= t2 and r is not None]
            if len(tr) < 0.8 * (t1 - t0) / HOUR_MS or len(fw) < 0.8 * (t2 - t1) / HOUR_MS:
                continue
            a_ = sum(tr) / len(tr) * 8760
            b_ = sum(fw) / len(fw) * 8760
            pairs.append((a_, b_))
            al.append(b_)
            if a_ >= thresh:
                hi.append(b_)
        if len(pairs) >= 5:
            out.append({'date': days[i].isoformat(), 'names': len(pairs), 'spearman': spearman(pairs),
                        'fwd_apr_selected': mean(hi), 'selected': len(hi), 'fwd_apr_all': mean(al)})
    sp = [x['spearman'] for x in out if x['spearman'] is not None]
    sel = [x['fwd_apr_selected'] for x in out if x['fwd_apr_selected'] is not None]
    return {'rebalances': out, 'mean_spearman': mean(sp), 'share_positive_spearman': (sum(1 for x in sp if x > 0) / len(sp)) if sp else None,
            'mean_fwd_apr_selected': mean(sel), 'mean_fwd_apr_all': mean([x['fwd_apr_all'] for x in out]),
            'min_fwd_apr_selected': min(sel) if sel else None, 'threshold': thresh}


def pair_days(ma, mb, days):
    """Daily close-to-close P&L, per unit notional, of short perp `ma` / long perp `mb` on the same underlying: the
    funding difference (what the short collects on `ma` minus what the long pays on `mb`) plus `mb`'s return minus
    `ma`'s. Both legs are 24/7 on the same venue, so the position is held through every closed period."""
    out, prev = [], None
    for d in days:
        T = close_ms(d)
        pa, sa = px_at(ma, T, max_stale_h=1)
        pb, sb = px_at(mb, T, max_stale_h=1)
        if not pa or not pb:
            prev = None
            continue
        if prev is not None:
            fa = funding_between(ma, prev['T'], T)[0]
            fb = funding_between(mb, prev['T'], T)[0]
            ra, rb = pa / prev['pa'] - 1.0, pb / prev['pb'] - 1.0
            out.append({'d': d.isoformat(), 'funding': fa - fb, 'pnl': fa - fb + rb - ra,
                        'spread': pa / pb - 1.0})
        prev = {'T': T, 'pa': pa, 'pb': pb}
    return out


def family_pairs(pairs, days, cost_bps, capital_per_notional=0.67, ssr=0.038, rebalance=21, thresholds=(0.0, 0.05)):
    """Every same-underlying pair of builder perps, oriented each rebalance so the short leg is the one whose trailing
    30-session funding was higher; held when that trailing difference exceeds the threshold (a year rate). Series:
    excess return on capital over the savings rate, capital = both legs' margin."""
    variants, members = {}, {}
    dlist = [d.isoformat() for d in days]
    rows = {k: {r['d']: r for r in v} for k, v in pairs.items()}
    for thr in thresholds:
        name = 'pairs|diff>=%g' % thr
        ser, book, held = [], {}, []
        for i, d in enumerate(dlist):
            tc = 0.0
            if i % rebalance == 0:
                new = {}
                for k, rr in rows.items():
                    past = [rr[x]['funding'] for x in dlist[max(0, i - 30):i] if x in rr]
                    if len(past) < 15:
                        continue
                    a = sum(past) / len(past) * 252
                    if abs(a) >= max(thr, 1e-12):
                        new[k] = 1 if a > 0 else -1
                changed = [k for k in set(new) | set(book) if new.get(k) != book.get(k)]
                tc = sum(cost_bps.get(k, 30.0) / 2.0 for k in changed) / 1e4 / max(len(set(new) | set(book)), 1)
                book = new
                held.append((d, sorted('%s%s' % ('' if v > 0 else '-', k) for k, v in book.items())))
            pn = [sgn * rows[k][d]['pnl'] for k, sgn in book.items() if d in rows[k]]
            r = (mean(pn) if pn else 0.0) - tc
            ser.append((r - ssr / 252.0 * capital_per_notional) / capital_per_notional if pn else 0.0)
        variants[name] = ser
        members[name] = held
    return dlist, variants, members


def dividend_events(rows, index_rows, cost_of):
    """Short the perp 30 min before an ex-dividend open and cover 30 min after: a perp pays no dividend, the oracle
    drops by it at the open, and the question is whether off-hours perp traders priced the drop in. 'hedged' subtracts
    the same window's index-perp move."""
    idx = {(r['d1']): r for r in index_rows}
    ev = []
    for r in rows:
        if not r.get('dividend_yield') or r.get('r_open') is None:
            continue
        c = cost_of(r['coin'], -1, 'post')
        if c is None:
            continue
        raw = -r['r_open'] + r['funding_pre_post'] - c / 1e4
        ir = idx.get(r['d1'])
        hedged = (raw + ir['r_open']) if (ir and ir.get('r_open') is not None) else None
        ev.append({'d1': r['d1'], 'coin': r['coin'], 'dividend_yield': r['dividend_yield'], 'r_open': r['r_open'],
                   'r_off': r['r_off'], 'net_raw': raw, 'net_hedged': hedged, 'cost_bps': c,
                   'priced_before_open': (-r['r_off'] / r['dividend_yield']) if r['dividend_yield'] else None})
    return ev


def summarize_choice(res, variants, n_trials_total, ppy=252):
    """choose_then_test output plus a bootstrap interval for the chosen variant's out-of-sample mean, its deflated
    Sharpe against every variant tried in the study, and the full-sample result of every variant."""
    if not res:
        return None
    ser = variants[res['chosen']]
    c = res['cutoff_index']
    oos = ser[c:]
    res['oos_bootstrap_mean'] = B.block_bootstrap(oos, n=1000)
    res['deflated_sharpe_vs_all_variants'] = B.deflated_sharpe(ser[:c], n_trials_total)
    res['all_variants_full_sample'] = {k: {kk: v for kk, v in B.perf(s, ppy).items()
                                           if kk in ('ann_return', 'sharpe', 'hit_rate', 'active_share', 'n')}
                                       for k, s in variants.items()}
    res['all_variants_oos'] = {k: {kk: v for kk, v in B.perf(s[c:], ppy).items()
                                   if kk in ('ann_return', 'sharpe', 'active_share', 'n')}
                               for k, s in variants.items()}
    return res


def capacity_pnl(trades, sessions, cutoff, books, meta, entry, exit_map, fee_case='schedule'):
    """Out-of-sample dollars per year if every trade is sized to the depth within 25bp on both legs, costed by walking
    the saved books at that size. Trades whose size cannot be filled inside the saved levels are dropped."""
    oos_sessions = set(sessions[cutoff:])
    per_session, notional = {}, {}
    sizes = []
    for s, coin, side, net_small in trades:
        if s not in oos_sessions:
            continue
        cap = capacity_usd(coin, books, side, entry=entry, exit_=exit_map)
        if not cap or cap < 1000:
            continue
        c_small = trip_cost_bps(coin, books, meta, side, 1e4, entry, exit_map, fee_case)
        c_cap = trip_cost_bps(coin, books, meta, side, cap, entry, exit_map, fee_case)
        if c_small is None or c_cap is None:
            continue
        gross = net_small + c_small / 1e4              # back out the small-size cost, charge the at-capacity one
        per_session[s] = per_session.get(s, 0.0) + (gross - c_cap / 1e4) * cap
        notional[s] = notional.get(s, 0.0) + cap
        sizes.append(cap)
    n = len(oos_sessions)
    tot = sum(per_session.values())
    return {'oos_sessions': n, 'traded_sessions': len(per_session), 'usd_total': tot,
            'usd_per_year': (tot / n * 252.0) if n else None, 'median_size_usd': median(sizes),
            'trades_sized': len(sizes), 'max_session_notional_usd': max(notional.values()) if notional else None,
            'median_session_notional_usd': median(list(notional.values()))}


def latest_universe():
    """Open interest (USD) and day volume per market from the most recently collected store universe."""
    best = {}
    for st in STORES:
        p = st / 'universe.json'
        if not p.exists():
            continue
        u = json.loads(p.read_text())
        for m in u['markets']:
            if m['coin'] not in best or u['collected_at'] > best[m['coin']]['at']:
                best[m['coin']] = {'at': u['collected_at'], 'oi_usd': (m.get('oi') or 0) * (m.get('mark') or 0),
                                   'day_ntl_vlm': m.get('day_ntl_vlm'), 'mark': m.get('mark')}
    return best


def carry_result(res, variants, n_trials, s_car, mem_car, raw_car, oi, args):
    """choose_then_test output for the carry family plus its capacity, baskets and out-of-sample decomposition."""
    res_car = summarize_choice(res, variants, n_trials)
    if not res_car:
        return None
    c = res_car['cutoff_index']
    names = sorted({x for d, b in mem_car[res_car['chosen']] if d >= s_car[c] for x in b})
    notional = sum(args.carry_oi_share * (oi.get(x) or 0) for x in mem_car[res_car['chosen']][-1][1])
    res_car['capacity'] = {
        'oi_share': args.carry_oi_share, 'final_basket': mem_car[res_car['chosen']][-1][1],
        'oos_names': names, 'notional_usd': notional, 'capital_usd': notional * args.carry_capital,
        'usd_per_year_excess_over_ssr': (res_car['out_of_sample'].get('ann_return') or 0) * notional * args.carry_capital,
        'note': 'notional = oi_share x open interest of each name in the latest basket; excess is over the savings '
                'rate on capital = notional x (1 + perp margin)'}
    res_car['baskets'] = mem_car[res_car['chosen']]
    res_car['oos_first'], res_car['oos_last'] = s_car[c], s_car[-1]
    res_car['is_first'], res_car['is_last'] = s_car[0], s_car[c - 1]

    def decomp(rw):
        act = [x for x in rw if x[1] is not None]
        return {'active_days': len(act), 'names_held_mean': mean([x[4] for x in act]),
                'pnl_per_notional_apr': (sum(x[1] for x in act) / len(act) * 252) if act else None,
                'funding_per_notional_apr': (sum(x[2] for x in act) / len(act) * 252) if act else None,
                'rebalance_cost_apr': (sum(x[3] for x in rw) / len(rw) * 252) if rw else None,
                'capital_per_notional': args.carry_capital, 'ssr': args.ssr,
                'note': 'excess on capital = (pnl - cost - ssr x capital) / capital'}
    res_car['oos_decomposition'] = decomp(raw_car[res_car['chosen']][c:])
    res_car['is_decomposition'] = decomp(raw_car[res_car['chosen']][:c])
    return res_car


def cmd_analyze(args):
    out = Path(args.out)
    markets = json.loads((out / 'markets.json').read_text())
    refs, divs = load_refs(out)
    spy = refs.get('SPY') or {}
    days = sorted(dt.date.fromisoformat(d) for d in spy)
    books, meta, snaps = load_books(out)
    btc = load_market('BTC')
    all_periods = closed_periods(days)
    states = hour_states(all_periods)

    rows, per_market, oracle, prem_states, fit = [], {}, {}, {}, [0, 0]
    carry, uni = {}, latest_universe()
    excluded = {'no_ref': [], 'no_data': [], 'bad_basis_sessions': 0}
    for coin, v in sorted(markets.items()):
        if not v['ref']:
            excluded['no_ref'].append(coin)
            continue
        sym = v['ref']['symbol']
        ref = refs.get(sym)
        m = load_market(coin)
        if not ref or not m['px']:
            excluded['no_data'].append(coin)
            continue
        periods = [p for p in all_periods if m['first'] <= p['close_ms'] and p['close1_ms'] <= m['last'] + HOUR_MS]
        scale = 1.0
        if v['ref']['kind'] == 'index':
            ratios = [px_at(m, p['close_ms'])[0] / ref[p['d0']]['close'] for p in periods
                      if p['d0'] in ref and px_at(m, p['close_ms'])[0]]
            scale = median(ratios) or 1.0
        rs = session_rows(m, ref, periods, divs.get(sym), scale=scale)
        for r in rs:
            r['coin'], r['symbol'], r['ref_kind'] = coin, sym, v['ref']['kind']
        excluded['bad_basis_sessions'] += sum(1 for r in rs if r['bad_basis'])
        good = [r for r in rs if not r['bad_basis']]
        rows += good
        per_market[coin] = {'symbol': sym, 'kind': v['ref']['kind'], 'sessions': len(good), 'scale': scale,
                            'first': utc(m['first']), 'last': utc(m['last']),
                            'bad_basis_sessions': sum(1 for r in rs if r['bad_basis']),
                            'median_pre_hour_usd': median([r['pre_hour_usd'] for r in good])}
        oracle[coin] = oracle_stats(m, good)
        ps, f = premium_by_state(m, states, m['first'], m['last'])
        prem_states[coin] = ps
        fit[0] += f[0]
        fit[1] += f[1]
        per_market[coin]['discovery'] = discovery_stats(good)
        per_market[coin]['_m'] = m
        c_first = min(x for x in (m['first'], m.get('first4')) if x)
        cdays = carry_days(m, ref, [d for d in days if c_first <= close_ms(d) <= m['last'] + HOUR_MS],
                           divs.get(sym), scale=scale)
        carry[coin] = cdays
        if cdays:
            fa = [r['funding'] for r in cdays]
            per_market[coin]['carry'] = {
                'days': len(cdays), 'days_4h_mark': sum(1 for r in cdays if r['mark'] == '4h'),
                'first_day': cdays[0]['d'], 'funding_apr': sum(fa) / len(fa) * 252,
                'pnl_apr': sum(r['pnl'] for r in cdays) / len(cdays) * 252,
                'basis_sd_bps': 1e4 * statistics.pstdev([r['basis'] for r in cdays]) if len(cdays) > 1 else None,
                'daily_pnl_sd_bps': 1e4 * statistics.pstdev([r['pnl'] for r in cdays]) if len(cdays) > 1 else None,
                'share_days_funding_positive': sum(1 for x in fa if x > 0) / len(fa),
                'oi_usd': (uni.get(coin) or {}).get('oi_usd'), 'day_ntl_vlm': (uni.get(coin) or {}).get('day_ntl_vlm')}
    # ---- discovery: pooled, by kind, by mark, by half
    disc = {'all': discovery_stats(rows)}
    for kind in ('overnight', 'weekend', 'holiday'):
        disc[kind] = discovery_stats([r for r in rows if r['kind'] == kind])
    for kind in ('stock', 'etf', 'index'):
        disc['ref_' + kind] = discovery_stats([r for r in rows if r['ref_kind'] == kind])
    liquid = [r for r in rows if (r['pre_hour_usd'] or 0) >= 100_000]
    disc['pre_hour_over_100k'] = discovery_stats(liquid)
    disc['pre_hour_under_100k'] = discovery_stats([r for r in rows if (r['pre_hour_usd'] or 0) < 100_000])
    dates = sorted({r['d1'] for r in rows})
    half = dates[len(dates) // 2] if dates else None
    disc['first_half'] = discovery_stats([r for r in rows if r['d1'] < half]) if half else None
    disc['second_half'] = discovery_stats([r for r in rows if r['d1'] >= half]) if half else None
    curve = {}
    pooled_marks = {}
    for coin, pm in per_market.items():
        mk = discovery_marks(pm['_m'], [r for r in rows if r['coin'] == coin])
        for h, lst in mk.items():
            pooled_marks.setdefault(h, []).extend(lst)
    for h, lst in sorted(pooled_marks.items()):
        for kind in ('overnight', 'closed_long'):
            sel = [(g, x) for g, x, _, k in lst if (k == 'overnight') == (kind == 'overnight')]
            s, r2 = origin_slope(sel)
            curve.setdefault(kind, {})[str(h)] = {'n': len(sel), 'share_priced': s, 'r2': r2}
    # ---- oracle and funding while shut
    fs = [v['follow_slope'] for v in oracle.values() if v['follow_slope'] is not None and v['pairs'] >= 10]
    closed_prem = [ps['closed'] for ps in prem_states.values() if 'closed' in ps]
    open_prem = [ps['open'] for ps in prem_states.values() if 'open' in ps]

    def agg(lst, key):
        h = sum(x['hours'] for x in lst)
        return sum(x[key] * x['hours'] for x in lst) / h if h else None

    fund_closed = [r['funding_closed'] for r in rows]
    unp = [r['unpriced'] for r in rows]
    oracle_summary = {
        'markets_with_10_moves': len(fs), 'median_follow_slope': median(fs),
        'share_markets_follow_over_0_8': (sum(1 for x in fs if x > 0.8) / len(fs)) if fs else None,
        'closed_hours': sum(x['hours'] for x in closed_prem), 'open_hours': sum(x['hours'] for x in open_prem),
        'closed_mean_abs_premium_bps': agg(closed_prem, 'mean_abs_premium_bps'),
        'open_mean_abs_premium_bps': agg(open_prem, 'mean_abs_premium_bps'),
        'closed_share_outside_dead_zone': agg(closed_prem, 'share_outside_dead_zone'),
        'open_share_outside_dead_zone': agg(open_prem, 'share_outside_dead_zone'),
        'closed_mean_funding_apr': agg(closed_prem, 'mean_funding_apr'),
        'open_mean_funding_apr': agg(open_prem, 'mean_funding_apr'),
        'funding_formula_reproduced_share': (fit[0] / fit[1]) if fit[1] else None, 'funding_rows_checked': fit[1],
        'mean_funding_closed_bps_per_session': bps(fund_closed),
        'mean_funding_closed_bps_weekend': bps([r['funding_closed'] for r in rows if r['kind'] == 'weekend']),
        'mean_unpriced_bps': bps(unp),
        'sd_unpriced_bps': 1e4 * statistics.pstdev(unp) if len(unp) > 1 else None,
        'share_sessions_shorts_paid': (sum(1 for x in fund_closed if x > 0) / len(fund_closed)) if fund_closed else None,
    }
    # Does the funding a short collects while the market is shut pay for the gap it bears? A short perp held from the
    # close to 30 min after the open: funding received over those hours minus the perp's move.
    sh = [r['funding_closed'] + r['funding_pre_post'] - (r['P_post'] / r['P_close'] - 1.0) for r in rows if r.get('P_post')]
    by_s = {}
    for r in rows:
        if r.get('P_post'):
            by_s.setdefault(r['d1'], []).append(r['funding_closed'] + r['funding_pre_post'] - (r['P_post'] / r['P_close'] - 1.0))
    sess = [mean(v) for _, v in sorted(by_s.items())]
    oracle_summary['unhedged_short_close_to_post'] = {
        'name_sessions': len(sh), 'mean_bps': bps(sh), 'sd_bps': 1e4 * statistics.pstdev(sh) if len(sh) > 1 else None,
        'funding_part_bps': bps([r['funding_closed'] + r['funding_pre_post'] for r in rows if r.get('P_post')]),
        'session_mean_t': B.newey_west_t(sess, lags=0)[0] if len(sess) > 3 else None, 'sessions': len(sess)}
    # Is funding persistent per name? Rank correlation of each name's mean hourly rate in the first and second half.
    halves = []
    t_mid = None
    if rows:
        ts = sorted({r['close_ms'] for r in rows})
        t_mid = ts[len(ts) // 2]
    for coin, pm in per_market.items():
        rr = pm['_m']['rate']
        a = [x for T, x in rr.items() if x is not None and T < t_mid]
        b2 = [x for T, x in rr.items() if x is not None and T >= t_mid]
        if len(a) > 200 and len(b2) > 200:
            halves.append((sum(a) / len(a), sum(b2) / len(b2)))
    oracle_summary['funding_persistence'] = {'names': len(halves), 'spearman_first_vs_second_half': spearman(halves)}
    # ---- strategies
    def cost_of(coin, side, exit_key, fee_case=args.fee_case):
        return trip_cost_bps(coin, books, meta, side, args.clip, 'pre_open', 'in_session', fee_case)

    tradable = [r for r in rows if r['stale_pre_h'] == 0 and (r['pre_hour_trades'] or 0) >= args.min_pre_trades]
    by_session = {}
    for r in tradable:
        by_session.setdefault(r['d1'], []).append(r)
    s_open, v_open, t_open = family_open(by_session, cost_of)
    hedge = {r['d1']: r for r in rows if r['coin'] == args.hedge_coin and r.get('r_open') is not None}
    s_hed, v_hed, t_hed = family_open(by_session, cost_of, hedge=hedge, hedge_coin=args.hedge_coin)
    s_cry, v_cry, t_cry = family_crypto(by_session, btc, cost_of)
    idx_rows = [r for r in rows if r['coin'] == args.hedge_coin]
    # Crypto-linked names: is Bitcoin's move over the closed hours already in the perp by 30 min before the open?
    cr = []
    for r in rows:
        if r['coin'].split(':', 1)[1] not in CRYPTO_LINKED:
            continue
        b0, b1 = px_at(btc, r['close_ms'])[0], px_at(btc, r['pre_ms'])[0]
        if b0 and b1:
            cr.append((b1 / b0 - 1.0, r))
    crypto_reg = {}
    for lab, sel in (('all', cr), ('weekend', [x for x in cr if x[1]['kind'] != 'overnight'])):
        if len(sel) < 10:
            continue
        a1, b1_, r21, n1 = ols([(x, r['gap']) for x, r in sel])
        a2, b2_, r22, _ = ols([(x, r['r_off']) for x, r in sel])
        a3, b3_, r23, _ = ols([(x, r['unpriced']) for x, r in sel])
        crypto_reg[lab] = {'n': n1, 'names': sorted({r['coin'] for _, r in sel}),
                           'gap_on_btc_beta': b1_, 'gap_on_btc_r2': r21,
                           'perp_on_btc_beta': b2_, 'perp_on_btc_r2': r22,
                           'unpriced_on_btc_beta': b3_, 'unpriced_on_btc_r2': r23}
    div_ev = dividend_events(tradable, idx_rows, cost_of)
    n_trials = len(v_open) + len(v_hed) + len(v_cry) + 2
    res_open = summarize_choice(B.choose_then_test(v_open, frac=0.5, periods_per_year=252), v_open, n_trials)
    res_hed = summarize_choice(B.choose_then_test(v_hed, frac=0.5, periods_per_year=252), v_hed, n_trials)
    res_cry = summarize_choice(B.choose_then_test(v_cry, frac=0.5, periods_per_year=252), v_cry, n_trials)
    for res, trades, sessions in ((res_open, t_open, s_open), (res_hed, t_hed, s_hed), (res_cry, t_cry, s_cry)):
        if res:
            ex = res['chosen'].split('exit=')[1].split('|')[0] if 'exit=' in res['chosen'] else 'post'
            res['capacity'] = capacity_pnl(trades[res['chosen']], sessions, res['cutoff_index'], books, meta,
                                           'pre_open', 'in_session')
            res['capacity']['exit'] = ex
            res['trades_oos'] = sum(1 for t in trades[res['chosen']] if t[0] >= sessions[res['cutoff_index']])
            res['trades_in_sample'] = sum(1 for t in trades[res['chosen']] if t[0] < sessions[res['cutoff_index']])
    # ---- persistence of funding across names, from the funding rows alone (back to listing)
    fp_days = [d for d in days if d >= dt.date(2025, 10, 1)]
    persistence = funding_persistence({c: pm['_m'] for c, pm in per_market.items()}, fp_days)
    # ---- hedged funding carry: short perp / long stock, held through the closed periods. The primary sample uses
    # hourly marks only (from 2026-03-15): a 4-hour mark sits an hour before the close in standard time and adds the
    # stock's last hour to every daily basis (daily P&L sd ~100bp against ~35bp on hourly marks). The full sample back
    # to listing is run beside it as a robustness check, and persistence is tested on funding alone above.
    carry_cost = {c: ((trip_cost_bps(c, books, meta, -1, args.clip) or 30.0) + args.stock_rt_bps) for c in carry}
    oi = {c: (uni.get(c) or {}).get('oi_usd') for c in carry}
    carry_1h = {c: [r for r in v if r['mark'] == '1h'] for c, v in carry.items()}
    res_car = res_car_all = None
    for label, sample in (('all_marks', carry), ('hourly_marks', carry_1h)):
        lo = min((r['d'] for c in sample for r in sample[c]), default=None)
        cdays_s = [d for d in days if lo and d.isoformat() >= lo]
        s_car, v_car, mem_car, raw_car = family_carry(sample, oi, cdays_s, carry_cost,
                                                      capital_per_notional=args.carry_capital, ssr=args.ssr)
        n_trials += len(v_car)
        r_ = carry_result(B.choose_then_test(v_car, frac=0.5, periods_per_year=252), v_car, n_trials, s_car, mem_car,
                          raw_car, oi, args)
        if r_:
            r_['sample'] = label
        if label == 'all_marks':
            res_car_all = r_
        else:
            res_car = r_
    # ---- same-underlying pairs across builder dexes: the 24/7 hedge that needs no broker
    by_sym = {}
    for coin, v in markets.items():
        if v['ref'] and coin in per_market:
            by_sym.setdefault(v['ref']['symbol'], []).append(coin)
    pair_rows, pair_cost, pair_stats = {}, {}, {}
    for sym, coins in sorted(by_sym.items()):
        coins = sorted(coins)
        for i in range(len(coins)):
            for j in range(i + 1, len(coins)):
                a_, b_ = coins[i], coins[j]
                ma, mb = load_market(a_), load_market(b_)
                lo_ = max(ma['first'], mb['first'])
                pr = pair_days(ma, mb, [d for d in days if close_ms(d) >= lo_])
                if len(pr) < 20:
                    continue
                key = '%s/%s' % (a_, b_)
                pair_rows[key] = pr
                pair_cost[key] = ((trip_cost_bps(a_, books, meta, -1, args.clip) or 30.0)
                                  + (trip_cost_bps(b_, books, meta, 1, args.clip) or 30.0))
                fd = [r['funding'] for r in pr]
                pair_stats[key] = {'days': len(pr), 'funding_diff_apr': sum(fd) / len(fd) * 252,
                                   'pnl_apr': sum(r['pnl'] for r in pr) / len(pr) * 252,
                                   'spread_sd_bps': 1e4 * statistics.pstdev([r['spread'] for r in pr]),
                                   'share_days_same_sign': max(sum(1 for x in fd if x > 0), sum(1 for x in fd if x < 0)) / len(fd),
                                   'round_trip_bps': pair_cost[key],
                                   'oi_usd': [(uni.get(a_) or {}).get('oi_usd'), (uni.get(b_) or {}).get('oi_usd')]}
    res_pairs = None
    if pair_rows:
        lo_p = min(r['d'] for v in pair_rows.values() for r in v)
        s_pr, v_pr, mem_pr = family_pairs(pair_rows, [d for d in days if d.isoformat() >= lo_p], pair_cost,
                                          ssr=args.ssr)
        n_trials += len(v_pr)
        res_pairs = summarize_choice(B.choose_then_test(v_pr, frac=0.5, periods_per_year=252), v_pr, n_trials)
        if res_pairs:
            res_pairs['baskets'] = mem_pr[res_pairs['chosen']]
            fin = mem_pr[res_pairs['chosen']][-1][1]
            cap = 0.0
            for k in fin:
                a_, b_ = k.lstrip('-').split('/')
                oa, ob = (uni.get(a_) or {}).get('oi_usd') or 0, (uni.get(b_) or {}).get('oi_usd') or 0
                cap += args.carry_oi_share * min(oa, ob)
            res_pairs['capacity'] = {'oi_share': args.carry_oi_share, 'final_basket': fin, 'notional_usd': cap,
                                     'capital_usd': cap * 0.67,
                                     'usd_per_year_excess_over_ssr': (res_pairs['out_of_sample'].get('ann_return') or 0) * cap * 0.67,
                                     'note': 'notional = oi_share x the smaller leg\'s open interest per pair'}
    div_dates = sorted({e['d1'] for e in div_ev})
    div_cut = div_dates[len(div_dates) // 2] if div_dates else None
    div_summary = {
        'events': len(div_ev), 'names': len({e['coin'] for e in div_ev}),
        'mean_dividend_yield_bps': bps([e['dividend_yield'] for e in div_ev]),
        'mean_net_raw_bps': bps([e['net_raw'] for e in div_ev]),
        'mean_net_hedged_bps': bps([e['net_hedged'] for e in div_ev]),
        'median_priced_before_open': median([e['priced_before_open'] for e in div_ev]),
        'first_half_mean_net_hedged_bps': bps([e['net_hedged'] for e in div_ev if div_cut and e['d1'] < div_cut]),
        'second_half_mean_net_hedged_bps': bps([e['net_hedged'] for e in div_ev if div_cut and e['d1'] >= div_cut]),
        't_hedged': B.newey_west_t([e['net_hedged'] for e in div_ev if e['net_hedged'] is not None], lags=0)[0] if len(div_ev) > 3 else None,
        'events_list': div_ev,
    }
    for pm in per_market.values():
        pm.pop('_m', None)
    cost_table = {}
    for coin in sorted({r['coin'] for r in tradable}):
        cost_table[coin] = {fc: cost_of(coin, 1, 'post', fc) for fc in ('schedule', 'flat', 'no_growth')}
        cost_table[coin]['capacity25_long'] = capacity_usd(coin, books, 1)
        cost_table[coin]['fee_bps'] = fee_for(coin, meta)
    analysis = {
        'generated': utc(time.time() * 1000),
        'sample': {'first_session': rows and min(r['d1'] for r in rows), 'last_session': rows and max(r['d1'] for r in rows),
                   'sessions': len(dates), 'name_sessions': len(rows), 'markets': len(per_market),
                   'tradable_name_sessions': len(tradable), 'stores': [str(s.relative_to(ROOT)) for s in STORES],
                   'book_snapshots': {k: str(v.relative_to(ROOT)) for k, v in BOOK_SNAPS.items()}, 'own_snaps': snaps,
                   'clip_usd': args.clip, 'fee_case': args.fee_case, 'min_pre_trades': args.min_pre_trades},
        'excluded': excluded,
        'discovery': disc, 'discovery_curve': curve,
        'oracle_and_funding': oracle_summary, 'oracle_by_market': oracle, 'premium_by_market': prem_states,
        'premarket': premarket_compare(out, rows),
        'strategies': {'n_variants_total': n_trials, 'open_reaction': res_open, 'open_reaction_hedged': res_hed,
                       'pairs': res_pairs, 'pair_stats': pair_stats, 'funding_persistence_history': persistence,
                       'carry': res_car, 'carry_all_marks': res_car_all, 'carry_params': {'capital_per_notional': args.carry_capital, 'ssr': args.ssr,
                                                          'stock_rt_bps': args.stock_rt_bps, 'rebalance_sessions': 21},
                       'hedge_coin': args.hedge_coin, 'crypto_vs_btc': res_cry, 'crypto_regression': crypto_reg,
                       'dividend': div_summary},
        'costs': cost_table,
        'per_market': per_market,
    }
    write_json(out / 'analysis.json', analysis)
    man_p = out / 'manifest.json'
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    stores = {}
    for st_ in STORES:
        mp_ = st_ / 'manifest.json'
        if mp_.exists():
            mm = json.loads(mp_.read_text())
            stores[str(st_.relative_to(ROOT))] = {k: mm.get(k) for k in ('collected_at', 'finished_at', 'since_utc',
                                                                          'until_utc', 'markets')}
            stores[str(st_.relative_to(ROOT))]['failed_markets'] = sorted(mm.get('failures') or {})
    man['analyze'] = {'at': analysis['generated'], 'stores': stores, 'settings': analysis['sample'],
                      'hourly_candles_from': '2026-03-15 (Hyperliquid serves the latest 5,000 bars of an interval)',
                      'premarket_source': 'raw/yahoo (1h bars with pre/post, 60 days, 8 symbols)'}
    write_json(man_p, man)
    with gzip.open(out / 'sessions.json.gz', 'wt') as f:
        json.dump(rows, f, default=str)
    print(json.dumps({'name_sessions': len(rows), 'sessions': len(dates), 'markets': len(per_market),
                      'share_priced_all': disc['all'].get('share_priced'),
                      'open_choice': res_open and res_open['chosen'],
                      'open_oos_ann': res_open and res_open['out_of_sample'].get('ann_return'),
                      'crypto_choice': res_cry and res_cry['chosen'],
                      'crypto_oos_ann': res_cry and res_cry['out_of_sample'].get('ann_return'),
                      'dividend_events': div_summary['events']}, indent=1, default=str))
    return 0


# ---------------------------------------------------------------------------------------------- render

def _f(v, fmt='%.2f', none='—'):
    return none if v is None else fmt % v


def _pct(v, d=1):
    return '—' if v is None else ('%.' + str(d) + 'f%%') % (100 * v)


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    S = a['sample']
    L = ['# HIP-3 equity perps while the cash market is shut — tables', '',
         'Generated %s by `scripts/equity_offhours.py` from `analysis.json`. Sessions %s to %s: %d closed periods, '
         '%d name-sessions over %d markets (%d tradable at the pre-open hour). Costs at a $%s clip, fee case `%s`.'
         % (a['generated'], S['first_session'], S['last_session'], S['sessions'], S['name_sessions'], S['markets'],
            S['tradable_name_sessions'], format(int(S['clip_usd']), ','), S['fee_case']), '']
    L += ['## Price discovery: how much of the cash gap the perp had moved 30 minutes before the open', '',
          '| subset | name-sessions | sessions | share priced (90% CI) | R² | gap on perp: slope, intercept | mean abs gap | mean abs unpriced |',
          '|---|---|---|---|---|---|---|---|']
    for k, d in a['discovery'].items():
        if not d or d.get('n', 0) < 5:
            continue
        ci = d.get('share_priced_ci90') or [None, None]
        L.append('| %s | %d | %d | %s (%s–%s) | %s | %s, %sbp | %sbp | %sbp |' % (
            k, d['n'], d['sessions'], _f(d['share_priced']), _f(ci[0]), _f(ci[1]), _f(d['r2_through_origin']),
            _f(d['gap_on_perp_slope']), _f(d['gap_on_perp_intercept_bps'], '%.1f'), _f(d['mean_abs_gap_bps'], '%.0f'),
            _f(d['mean_abs_unpriced_bps'], '%.0f')))
    L += ['', '## Discovery curve: share of the gap priced h hours before the open', '',
          '| hours before open | overnight share (R²) | weekend/holiday share (R²) |', '|---|---|---|']
    cv = a['discovery_curve']
    for h in sorted({float(x) for d in cv.values() for x in d}, reverse=True):
        o = cv.get('overnight', {}).get(str(h)) or {}
        w = cv.get('closed_long', {}).get(str(h)) or {}
        L.append('| %.1f | %s (%s), n=%s | %s (%s), n=%s |' % (h, _f(o.get('share_priced')), _f(o.get('r2')), o.get('n', 0),
                                                            _f(w.get('share_priced')), _f(w.get('r2')), w.get('n', 0)))
    O = a['oracle_and_funding']
    L += ['', '## The oracle and funding while the market is shut', '',
          '| measure | closed hours | open hours |', '|---|---|---|',
          '| hours | %d | %d |' % (O['closed_hours'], O['open_hours']),
          '| mean abs premium | %sbp | %sbp |' % (_f(O['closed_mean_abs_premium_bps']), _f(O['open_mean_abs_premium_bps'])),
          '| share of hours outside the funding dead zone | %s | %s |' % (_pct(O['closed_share_outside_dead_zone']), _pct(O['open_share_outside_dead_zone'])),
          '| mean funding APR (longs pay +) | %s | %s |' % (_pct(O['closed_mean_funding_apr'], 2), _pct(O['open_mean_funding_apr'], 2)),
          '', 'Implied oracle follows the perp while shut: median slope %s over %d markets with at least ten moves; '
          '%s of them above 0.8. Funding formula reproduced on %s of %d rows. Funding over a closed period: %sbp on '
          'average (%sbp over a weekend), shorts paid in %s of sessions; the gap left at 30 min before the open averaged '
          '%sbp with a standard deviation of %sbp.' % (
              _f(O['median_follow_slope']), O['markets_with_10_moves'], _pct(O['share_markets_follow_over_0_8']),
              _pct(O['funding_formula_reproduced_share']), O['funding_rows_checked'],
              _f(O['mean_funding_closed_bps_per_session']), _f(O['mean_funding_closed_bps_weekend']),
              _pct(O['share_sessions_shorts_paid']), _f(O['mean_unpriced_bps'], '%.1f'), _f(O['sd_unpriced_bps'], '%.0f'))]
    pmk = a.get('premarket')
    if pmk:
        L += ['', '## The perp against the pre-market tape at 09:00 ET (%d name-sessions, %s to %s)' % (
            pmk['name_sessions'], pmk['first'], pmk['last']), '',
              'Mean absolute distance perp vs pre-market last trade %sbp (median %sbp). The opening print was %sbp from '
              'the perp and %sbp from the pre-market price on average, closer to the perp in %s of name-sessions. The '
              'gap still open after the perp, regressed on the pre-market\'s deviation from it: slope %s, R² %s.' % (
                  _f(pmk['mean_abs_dev_bps'], '%.1f'), _f(pmk['median_abs_dev_bps'], '%.1f'),
                  _f(pmk['mean_abs_open_vs_perp_bps'], '%.1f'), _f(pmk['mean_abs_open_vs_premarket_bps'], '%.1f'),
                  _pct(pmk['share_open_closer_to_perp'], 0), _f(pmk['pm_lead_slope']), _f(pmk['pm_lead_r2'])), '',
              '| symbol | n | mean abs perp vs pre-market | open vs perp | open vs pre-market |', '|---|---|---|---|---|']
        for sym, v in sorted(pmk['per_symbol'].items()):
            L.append('| %s | %d | %sbp | %sbp | %sbp |' % (sym, v['n'], _f(v['mean_abs_dev_bps'], '%.1f'),
                                                        _f(v['mean_abs_open_vs_perp_bps'], '%.1f'),
                                                        _f(v['mean_abs_open_vs_premarket_bps'], '%.1f')))
    st = a['strategies']
    L += ['', '## Strategies (chosen on the first half of sessions, tested once on the second; %d variants tried in all)'
          % st['n_variants_total'], '']
    for fam in ('open_reaction', 'open_reaction_hedged', 'crypto_vs_btc', 'carry', 'carry_all_marks', 'pairs'):
        r = st.get(fam)
        if not r:
            continue
        i, o = r['in_sample'], r['out_of_sample']
        bs = r.get('oos_bootstrap_mean') or {}
        cap = r.get('capacity') or {}
        L += ['### %s' % fam, '',
              '| | in sample | out of sample |', '|---|---|---|',
              '| chosen | `%s` | rank %d of %d |' % (r['chosen'], r['oos_rank'], r['n_variants']),
              '| sessions | %d | %d |' % (i['n'], o['n']),
              '| annual return on deployed notional | %s | %s |' % (_pct(i.get('ann_return')), _pct(o.get('ann_return'))),
              '| Sharpe | %s | %s |' % (_f(i.get('sharpe')), _f(o.get('sharpe'))),
              '| active sessions | %s | %s |' % (_pct(i.get('active_share')), _pct(o.get('active_share'))),
              ('| trades | %s | %s |' % (r.get('trades_in_sample'), r.get('trades_oos')) if r.get('trades_oos') is not None
               else '| rebalances | %d | %d |' % (sum(1 for d, _ in r.get('baskets') or [] if d < (r.get('oos_first') or '')),
                                                  sum(1 for d, _ in r.get('baskets') or [] if d >= (r.get('oos_first') or '')))),
              '', 'Out of sample: Newey–West t %s (p %s); bootstrap 95%% interval of the mean session return %s to %s bp; '
              'deflated Sharpe of the in-sample choice against all %d variants %s; BH survivors on the full sample: %s. ' % (
                  _f(r.get('oos_t')), _f(r.get('oos_p'), '%.3f'), _f((bs.get('lo') or 0) * 1e4, '%.1f'),
                  _f((bs.get('hi') or 0) * 1e4, '%.1f'), st['n_variants_total'],
                  _f(r.get('deflated_sharpe_vs_all_variants'), '%.3f'),
                  ', '.join('`%s`' % x for x in r['bh_survivors_full_sample']) or 'none')
              + (('At the depth within 25bp on both legs: %s a year (median size $%s, %d trades sized).' % (
                  ('$' + format(int(cap['usd_per_year']), ',')) if cap.get('usd_per_year') is not None else '—',
                  format(int(cap.get('median_size_usd') or 0), ','), cap.get('trades_sized') or 0)) if fam not in ('carry', 'carry_all_marks', 'pairs') else
                 ('Sized at %s of each basket name\'s open interest: $%s notional, $%s of capital, $%s a year over the '
                  'savings rate; latest basket %s.' % (_pct(cap.get('oi_share'), 0), format(int(cap.get('notional_usd') or 0), ','),
                                                       format(int(cap.get('capital_usd') or 0), ','),
                                                       format(int(cap.get('usd_per_year_excess_over_ssr') or 0), ','),
                                                       ', '.join(cap.get('final_basket') or []))) if cap else ''), '']
        for lab in ('is_decomposition', 'oos_decomposition'):
            dd = r.get(lab)
            if dd:
                L.append('%s: funding %s a year per notional, P&L %s, rebalancing %s, %s names held on average over %d '
                         'active days.' % ('In sample (from %s)' % r.get('is_first') if lab == 'is_decomposition'
                                           else 'Out of sample (%s to %s)' % (r.get('oos_first'), r.get('oos_last')),
                                           _pct(dd['funding_per_notional_apr']), _pct(dd['pnl_per_notional_apr']),
                                           _pct(dd['rebalance_cost_apr'], 2), _f(dd['names_held_mean'], '%.1f'),
                                           dd['active_days']))
        L.append('')
        top = sorted(r['all_variants_full_sample'].items(), key=lambda kv: -(kv[1].get('sharpe') or -9))[:8]
        L += ['| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |',
              '|---|---|---|---|---|']
        for k, v in top:
            ov = r['all_variants_oos'][k]
            L.append('| `%s` | %s | %s | %s | %s |' % (k, _pct(v.get('ann_return')), _f(v.get('sharpe')),
                                                    _pct(ov.get('ann_return')), _f(ov.get('sharpe'))))
        L.append('')
    fp = st.get('funding_persistence_history')
    if fp:
        L += ['### funding persistence (funding rows only, back to listing)', '',
              'At %d monthly rebalances the rank correlation between each name\'s trailing-30-session and next-21-session '
              'funding averaged %s (positive at %s of them); names that had paid at least %s went on to pay %s a year '
              'over the next 21 sessions (worst rebalance %s) against %s for all names.' % (
                  len(fp['rebalances']), _f(fp['mean_spearman']), _pct(fp['share_positive_spearman'], 0),
                  _pct(fp['threshold'], 0), _pct(fp['mean_fwd_apr_selected']), _pct(fp['min_fwd_apr_selected']),
                  _pct(fp['mean_fwd_apr_all'])), '',
              '| rebalance | names | rank corr | selected | forward APR selected | forward APR all |', '|---|---|---|---|---|---|']
        for x in fp['rebalances']:
            L.append('| %s | %d | %s | %d | %s | %s |' % (x['date'], x['names'], _f(x['spearman']), x['selected'],
                                                       _pct(x['fwd_apr_selected']), _pct(x['fwd_apr_all'])))
        L.append('')
    dv = st['dividend']
    L += ['### dividend', '',
          '%d ex-dividend opens on %d names; mean dividend %sbp; shorting 30 min before the open and covering 30 min after '
          'netted %sbp raw and %sbp index-hedged per event (first half %sbp, second half %sbp; t %s); the perp had moved '
          'a median %s of the dividend before the open.' % (
              dv['events'], dv['names'], _f(dv['mean_dividend_yield_bps'], '%.1f'), _f(dv['mean_net_raw_bps'], '%.1f'),
              _f(dv['mean_net_hedged_bps'], '%.1f'), _f(dv['first_half_mean_net_hedged_bps'], '%.1f'),
              _f(dv['second_half_mean_net_hedged_bps'], '%.1f'), _f(dv['t_hedged']),
              _f(dv['median_priced_before_open'])), '']
    L += ['## Per market (sessions >= 20)', '',
          '| market | ref | sessions | share priced | R² | mean abs unpriced | median pre-open hour notional | oracle follow slope |',
          '|---|---|---|---|---|---|---|---|']
    for coin, pm in sorted(a['per_market'].items(), key=lambda kv: -kv[1]['sessions']):
        d = pm.get('discovery') or {}
        if pm['sessions'] < 20 or d.get('n', 0) < 5:
            continue
        L.append('| %s | %s | %d | %s | %s | %sbp | $%s | %s |' % (
            coin, pm['symbol'], pm['sessions'], _f(d.get('share_priced')), _f(d.get('r2_through_origin')),
            _f(d.get('mean_abs_unpriced_bps'), '%.0f'), format(int(pm.get('median_pre_hour_usd') or 0), ','),
            _f((a['oracle_by_market'].get(coin) or {}).get('follow_slope'))))
    L += ['', '## Same-underlying builder pairs (short the first, long the second; close to close)', '',
          '| pair | days | funding difference APR | pair P&L APR | spread sd | same-sign days | round trip | open interest |',
          '|---|---|---|---|---|---|---|---|']
    for k, v in sorted(st.get('pair_stats', {}).items(), key=lambda kv: -abs(kv[1]['funding_diff_apr'])):
        L.append('| %s | %d | %s | %s | %sbp | %s | %sbp | $%sM / $%sM |' % (
            k, v['days'], _pct(v['funding_diff_apr']), _pct(v['pnl_apr']), _f(v['spread_sd_bps'], '%.1f'),
            _pct(v['share_days_same_sign'], 0), _f(v['round_trip_bps'], '%.1f'),
            _f((v['oi_usd'][0] or 0) / 1e6, '%.1f'), _f((v['oi_usd'][1] or 0) / 1e6, '%.1f')))
    L += ['', '## Hedged funding carry per market (short perp, long stock; close to close)', '',
          '| market | days | funding APR | carry P&L APR | basis sd | daily P&L sd | funding > 0 days | open interest |',
          '|---|---|---|---|---|---|---|---|']
    for coin, pm in sorted(a['per_market'].items(), key=lambda kv: -((kv[1].get('carry') or {}).get('oi_usd') or 0)):
        cy = pm.get('carry')
        if not cy or cy['days'] < 20:
            continue
        L.append('| %s | %d | %s | %s | %sbp | %sbp | %s | $%sM |' % (
            coin, cy['days'], _pct(cy['funding_apr']), _pct(cy['pnl_apr']), _f(cy['basis_sd_bps'], '%.1f'),
            _f(cy['daily_pnl_sd_bps'], '%.1f'), _pct(cy['share_days_funding_positive'], 0),
            _f((cy.get('oi_usd') or 0) / 1e6, '%.1f')))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0


def cmd_book(args):
    """Strategy-book entries (research/strategies.jsonl schema) for the families that survived out of sample, written
    to book_entries.json for the coordinator to merge; nothing is appended to the book from here.

    The carry is judged on the longest history (`carry_all_marks`: rule chosen on 2025-10 to 2026-04, where daily
    marks are 4-hour bars and noisy, and tested on 2026-04 to 2026-10, where every mark is hourly). It enters when the
    chosen rule's out-of-sample excess over the savings rate is positive with a Newey-West t above 2 and the
    hourly-only rerun (`carry`) is positive out of sample as well; both runs' statistics go into the quote."""
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    st = a['strategies']
    entries = []
    c, h = st.get('carry_all_marks'), st.get('carry')
    if c and h and (c['out_of_sample'].get('ann_return') or 0) > 0 and (c.get('oos_t') or 0) > 2 \
            and (h['out_of_sample'].get('ann_return') or 0) > 0:
        dec, cap, prm = c['oos_decomposition'], c['capacity'], st['carry_params']
        excess_cap = c['out_of_sample']['ann_return']
        net_notional = excess_cap * prm['capital_per_notional']
        basket = cap['final_basket']
        entries.append({
            'id': 'hip3-equity-funding-carry',
            'name': 'Short HIP-3 equity perps that pay high funding, long the same stocks at a broker',
            'kind': 'carry', 'status': 'proposed',
            'thesis': ('On trade.xyz\'s single-stock perps the longs pay the shorts every hour, and on the names that '
                       'paid most over the last month they kept paying the next month: %.1f%% a year of funding on the '
                       'out-of-sample basket, %.1f%% after the basis and dividends. Short the perp, own the stock, and '
                       'the open\'s gap cancels between the legs; what is left is the funding.'
                       % (100 * dec['funding_per_notional_apr'], 100 * dec['pnl_per_notional_apr'])),
            'mechanism': ('Hyperliquid builder funding is mult x (P + clamp(I - P, +-0.03%%)) / 8 an hour; on trade.xyz '
                          'mult is 0.5 and I is 0.01%% per 8 h, so longs pay at least 5.5%% a year whenever the premium '
                          'sits inside the dead zone and half the premium beyond it. Retail demand for leveraged 24/7 '
                          'single-stock exposure keeps the premium above the zone on a persistent set of names (rank '
                          'correlation of first-half and second-half funding across %d names: %.2f). Shorting the perp '
                          'needs a cash-equity leg to hedge, i.e. a broker account and capital on two venues, which is '
                          'what keeps the arbitrage thin.' % (a['oracle_and_funding']['funding_persistence']['names'],
                                                              a['oracle_and_funding']['funding_persistence']['spearman_first_vs_second_half'] or 0)),
            'legs': ['short each basket perp on Hyperliquid at 2x (margin 50% of notional)',
                     'buy the same notional of the stock at a broker, fully paid',
                     're-select monthly: names with open interest >= $5M whose trailing 30-session funding >= 8% a year',
                     'collect hourly funding; on removal unwind both legs inside the US session'],
            'capacity_usd': round(cap['notional_usd']),
            'capital_days': 365,
            'kill_criteria': ['basket trailing-30-session funding below %.1f%% a year, where it no longer covers the '
                              'savings rate on %.1fx capital plus costs' % (100 * (prm['ssr'] * prm['capital_per_notional']
                                                                                     + dec['rebalance_cost_apr']), prm['capital_per_notional']),
                              'the selection rule\'s out-of-sample excess over the savings rate negative over a trailing quarter',
                              'trade.xyz changes the funding multiplier, interest leg or clamp (funding_formula_reproduced_share below 95%)',
                              'any basket name with funding negative on more than half of a month\'s days'],
            'risks': ['the funding is a crowded-trade signal: shorts arriving compress the premium toward the dead zone, '
                      'where funding is 5.5%% a year and the excess over the savings rate is gone at %.1fx capital'
                      % prm['capital_per_notional'],
                      'off-hours squeezes hit the perp short while the stock leg cannot trade: margin must survive a '
                      'weekend move with no hedge adjustment (2x leverage assumed)',
                      'the oracle is the deployer\'s; a methodology change, outage or delisting settles the perp at '
                      'the deployer\'s price',
                      'capacity is a planning size (%.0f%% of each name\'s open interest), not a measured elasticity'
                      % (100 * cap['oi_share']),
                      'two venues: the stock leg needs a broker; the funding accrues on Hyperliquid'],
            'evidence': {'notes': 'research/2026-10-09/equity_offhours (tables.md, analysis.json); scripts/equity_offhours.py '
                                  'carry family, chosen %s of %d carry variants and %d in the study; funding persistence '
                                  'from listing: trailing-30 vs next-21 rank correlation %.2f, positive at %d of %d rebalances'
                                  % (c['chosen'], len(c['all_variants_full_sample']), st['n_variants_total'],
                                     st['funding_persistence_history']['mean_spearman'] or 0,
                                     sum(1 for x in st['funding_persistence_history']['rebalances'] if (x['spearman'] or 0) > 0),
                                     len(st['funding_persistence_history']['rebalances'])),
                         'findings': [], 'verify': []},
            'quotes': [{'at': a['generated'], 'net_apr': net_notional, 'usd': net_notional * cap['notional_usd'],
                        'note': ('rule %s chosen on %s to %s, tested out of sample %s to %s: excess over the %.1f%% savings '
                                 'rate %.2f%% a year on capital (%.2f%% on notional), Newey-West t %.2f, Sharpe %.1f. '
                                 'Hourly-marks rerun (rule %s chosen %s to %s): %.2f%% out of sample, t %.2f, Sharpe %.1f; '
                                 'all %d of its variants are Benjamini-Hochberg survivors. Basket %s'
                                 % (c['chosen'], c['is_first'], c['is_last'], c['oos_first'], c['oos_last'],
                                    100 * prm['ssr'], 100 * excess_cap, 100 * net_notional, c['oos_t'],
                                    c['out_of_sample'].get('sharpe') or 0, h['chosen'], h['is_first'], h['is_last'],
                                    100 * h['out_of_sample']['ann_return'], h['oos_t'] or 0,
                                    h['out_of_sample'].get('sharpe') or 0, len(h['bh_survivors_full_sample']),
                                    ', '.join(basket))),
                        'present': True, 'source': 'history', 'window': 'research/2026-10-09/equity_offhours'}],
            'recheck_hours': 168,
        })
    write_json(out / 'book_entries.json', entries)
    print(json.dumps({'entries': [e['id'] for e in entries]}))
    return 0


# ---------------------------------------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect'); c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--since', default='2025-09-01')
    c.add_argument('--until', default=dt.date.today().isoformat())
    c.add_argument('--pause', type=float, default=0.6)
    c.add_argument('--refresh', action='store_true')
    c.add_argument('--reject', nargs='*', help='coins whose resolved reference is wrong')
    b = sub.add_parser('books'); b.set_defaults(fn=cmd_books)
    b.add_argument('--out', required=True)
    b.add_argument('--interval', type=float, default=1.1)
    b.add_argument('--top', type=int, default=40, help='books for this many referenced markets, largest open interest first')
    b.add_argument('--coins', nargs='*')
    a = sub.add_parser('analyze'); a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--clip', type=float, default=1e4, help='trade size for the edge test, USD')
    a.add_argument('--fee-case', default='schedule', choices=['schedule', 'flat', 'no_growth'])
    a.add_argument('--min-pre-trades', type=int, default=20, help='trades in the pre-open hour for a tradable row')
    a.add_argument('--hedge-coin', default='xyz:XYZ100', help='index perp for the hedged family and the dividend hedge')
    a.add_argument('--ssr', type=float, default=0.038, help='capital opportunity cost (Sky savings rate, read 2026-10-09)')
    a.add_argument('--carry-capital', type=float, default=1.5, help='capital per $1 of carry notional: stock + perp margin')
    a.add_argument('--stock-rt-bps', type=float, default=2.0, help='stock leg round trip, bps')
    a.add_argument('--carry-oi-share', type=float, default=0.05, help='carry size as a share of each name\'s open interest')

    pmk = sub.add_parser('premarket'); pmk.set_defaults(fn=cmd_premarket)
    pmk.add_argument('--out', required=True)
    k4 = sub.add_parser('candles4h'); k4.set_defaults(fn=cmd_candles4h)
    k4.add_argument('--out', required=True)
    k4.add_argument('--interval', type=float, default=1.1)
    k4.add_argument('--refresh', action='store_true')
    bk = sub.add_parser('book'); bk.set_defaults(fn=cmd_book)
    bk.add_argument('--out', required=True)
    r = sub.add_parser('render'); r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
