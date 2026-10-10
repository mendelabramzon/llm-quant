#!/usr/bin/env python3
"""Fixed against floating carry on crypto derivatives: dated basis, a do-it-yourself Ethena, Boros rate swaps, and the
options volatility premium — is any of it a large, speed-independent yield above the savings rate?

Why. Every go row in the book is $1–20M wide; the only large row is the benchmark itself (the Sky savings rate, SSR,
3.80% a year on chain). The largest pools of carry in crypto are not on chain at all: the basis of dated futures over
spot, the funding a short perpetual collects against a spot hedge (the trade Ethena runs at $10B+, and sUSDe is the
market's price of it), and, since 2025, Pendle Boros, which quotes a fixed rate for a venue's floating funding. All three
are earned over weeks, not milliseconds, so they fit the standing constraint of this round (no latency or block-position
competition). The question is the one the book always asks: after costs, on the capital the trade really ties up, does
any of it beat the savings rate out of sample, and at what size?

What this measures (`analyze`; every number lands in `analysis.json`, `render` prints `tables.md`):

  (a) **Dated basis.** Binance USDⓈ-M quarterlies (continuous CURRENT_QUARTER / NEXT_QUARTER daily closes against
      Binance's own index, 2021→), Deribit's coin-margined quarterlies (every expired contract by name, against Deribit's
      USD index, 2019→), CME front months (Yahoo hourly, last ~2 years, against BTC-USD at the same hour). Each day's
      basis is annualised to the contract's expiry — the locked yield of buy-spot/sell-future held to expiry — net of
      fees and over the capital (spot + futures margin). The rule "enter when the locked yield beats SSR by x, hold to
      expiry, else hold SSR" chooses x and the tenor on the first half of each venue's years and is tested on the rest.
  (b) **DIY Ethena.** Long spot, short perp on Binance (2019→), on Hyperliquid (2023-05→), and on whichever paid more
      last month, for BTC, ETH, SOL and HYPE, with daily decisions, taker fees and half-spreads on every switch, the
      basis at entry and exit, margin rebalancing for separately margined legs, and three capital models (spot as
      collateral; spot plus the short margined at 3x or 5x in cash). Rules: always on, or on while trailing funding beats
      SSR + x. Compared with sUSDe's realised yield (convertToAssets on chain) and with the savings rate actually paid at
      the time (Maker's DSR, then the SSR) as well as the constant 3.80%. ETH also with wstETH as the spot leg.
  (c) **Boros.** Pendle Boros's open API (`api-boros.pendle.finance/apis`) serves every market, matured ones included,
      with daily mark (implied) APR and the venue's underlying APR. For each market day: the implied fixed rate against
      the floating funding actually paid over the market's remaining term (settled funding from the venues' own
      histories where on disk, Boros's hourly underlying series elsewhere). A persistent gap is a carry for whoever
      receives fixed (or pays it). Rule: receive fixed when implied − trailing-7d floating ≥ X (and the mirror), chosen on
      markets maturing in the first half, tested on the rest.
  (d) **Volatility risk premium (measurement only).** Deribit DVOL against the realised volatility of the next 30 days
      (Binance hourly closes), by year, with its tail.

Conventions. Rates are decimals per year unless named `_bp`. A funding rate is per settlement, positive when longs pay
shorts, so a short receives +rate. Daily funding is the sum of settlements in (d 00:00, d+1 00:00] UTC; a decision at
00:00 UTC acts on the next day's settlements. Capital is per unit of notional: 1.0 when the spot leg is the short's
collateral (Binance portfolio margin / multi-assets mode, Bybit UTA, OKX, Deribit coin margin, Hyperliquid portfolio
margin for BTC and HYPE), 1 + 1/L when the short is margined separately in cash at leverage L. Excess is over SSR on
that capital. Every rule is chosen on the first part of time and tested once on the rest through `backtest.py`.

    python3 scripts/term_carry.py collect --out research/2026-10-10/term_carry --parts binance,deribit,yahoo,boros,books
    python3 scripts/term_carry.py collect --out research/2026-10-10/term_carry --parts hl        # paced, ~12 min
    python3 scripts/term_carry.py collect --out research/2026-10-10/term_carry --parts chain     # public archive RPC
    python3 scripts/term_carry.py analyze --out research/2026-10-10/term_carry
    python3 scripts/term_carry.py render  --out research/2026-10-10/term_carry
    python3 scripts/term_carry.py snapshot --out research/2026-10-10/term_carry   # Boros term structure, daily

Data reused from disk: Hyperliquid hourly funding since 2025-10-01 (`research/2026-10-09/perps_history`), Binance,
Bybit and OKX funding (`research/2026-10-09/funding_arb/raw`), daily NAVs of sUSDS, wstETH and sUSDe
(`research/2026-10-09/redemption_history/raw/long/state.json`). Network etiquette: Hyperliquid through
`perp_rpc.Info` at ≥ 4 s a call; Binance through `funding_arb.Http` with its weight header; Yahoo with UA `Mozilla/5.0`.
"""
import argparse
import bisect
import calendar
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
DAY_S = 86400
SSR = 0.038                      # Sky savings rate, 3.80% APY on chain 2026-10-09: the benchmark of every row
UA = 'Mozilla/5.0'

BN_FAPI = 'https://fapi.binance.com'
BN_SPOT = 'https://api.binance.com'
DERIBIT = 'https://www.deribit.com/api/v2/public/'
YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart/'
BOROS = 'https://api-boros.pendle.finance/apis'

PERPS_STORE = ROOT / 'research' / '2026-10-09' / 'perps_history'
FARB_RAW = ROOT / 'research' / '2026-10-09' / 'funding_arb' / 'raw'
NAV_STATE = ROOT / 'research' / '2026-10-09' / 'redemption_history' / 'raw' / 'long' / 'state.json'
NAV_HEADERS = ROOT / 'research' / '2026-10-09' / 'redemption_history' / 'raw' / 'long' / 'headers.json'

# Fees in bp of notional (VIP0 taker unless stated). Binance spot 10bp (7.5 with BNB), USDⓈ-M 5bp; Hyperliquid perps
# 4.5bp, spot 7bp (funding_arb.FEES_TAKER); Deribit futures taker 5bp; CME ~1bp all-in (commission + exchange fee on a
# 5 BTC contract), with the spot leg bought at Coinbase-like 5bp or as an ETF. Delivery: Binance quarterlies settle to
# the 30-minute index average and the spot is sold into it (2bp assumed for the fill against that average).
FEE = {'bn_spot': 10.0, 'bn_perp': 5.0, 'bn_quarter': 5.0, 'bn_delivery': 2.0, 'hl_perp': 4.5, 'hl_spot': 7.0,
       'deribit_fut': 5.0, 'deribit_delivery': 2.5, 'cme_fut': 1.0, 'cme_spot': 5.0}
HALF_SPREAD = {'BTC': 0.5, 'ETH': 0.8, 'SOL': 2.0, 'HYPE': 3.0}   # bp, replaced by live books where read

# Ethereum contracts read for history (selectors computed with keccak256 and pinned in the tests).
SUSDE = '0x9D39A5DE30e57443BfF2A8307A4256c8797A3497'
POT = '0x197E90f9FAD81970bA7976f33CbD77088E5D7cf7'
WSTETH = '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0'
SEL = {'convertToAssets': '0x07a2d13a', 'dsr': '0x487bf082', 'stEthPerToken': '0x035faf82'}
SUSDE_DEPLOY_TS = 1700006400     # 2023-11-15
WSTETH_DEPLOY_TS = 1614124800    # 2021-02-24
MERGE_BLOCK, MERGE_TS = 15537394, 1663224162


# ---------------------------------------------------------------------------------------------- small utilities

def utc(ms=None):
    t = time.time() if ms is None else ms / 1000.0
    return dt.datetime.fromtimestamp(t, UTC).isoformat(timespec='seconds')


def day_ms(s):
    """'2024-07-01' -> epoch ms at 00:00 UTC."""
    return int(dt.datetime.strptime(s[:10], '%Y-%m-%d').replace(tzinfo=UTC).timestamp() * 1000)


def ymd(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, UTC).strftime('%Y-%m-%d')


def write_gz(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, 'wt') as f:
        json.dump(obj, f)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


def get_json(url, params=None, headers=None, retries=5, pause=0.25, timeout=60):
    if params:
        url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers=dict({'User-Agent': UA, 'Accept': 'application/json'}, **(headers or {})))
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
                d = json.loads(body.decode())
            time.sleep(pause)
            return d
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code == 404:
                return {'_http_error': 404}
            wait = 60.0 if e.code in (418, 429) else pause * 2 ** (a + 1)
            time.sleep(min(wait, 90.0))
        except Exception as e:  # noqa: BLE001 - transport errors are retried, then raised with context
            last = repr(e)[:160]
            time.sleep(pause * 2 ** (a + 1))
    raise RuntimeError('%s: %s' % (url[:160], last))


# ---------------------------------------------------------------------------------------------- calendars

def last_friday(year, month):
    """The last Friday of a month, as a date."""
    last = calendar.monthrange(year, month)[1]
    d = dt.date(year, month, last)
    return d - dt.timedelta(days=(d.weekday() - 4) % 7)


def quarterly_expiries(y0, y1, hour=8):
    """Binance and Deribit quarterlies: the last Friday of Mar/Jun/Sep/Dec at 08:00 UTC, as epoch ms, ascending."""
    out = []
    for y in range(y0, y1 + 1):
        for m in (3, 6, 9, 12):
            d = last_friday(y, m)
            out.append(int(dt.datetime(d.year, d.month, d.day, hour, tzinfo=UTC).timestamp() * 1000))
    return out


def monthly_expiries(y0, y1, hour=15):
    """CME bitcoin and ether futures: the last Friday of every month, at 4pm London (15:00 UTC in summer, 16:00 in
    winter; 15:00 is used — an hour of error is noise against a month to expiry)."""
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d = last_friday(y, m)
            out.append(int(dt.datetime(d.year, d.month, d.day, hour, tzinfo=UTC).timestamp() * 1000))
    return out


def nth_expiry_after(expiries, t, n=0):
    """The (n+1)-th expiry strictly after t (None past the calendar)."""
    i = bisect.bisect_right(expiries, t)
    return expiries[i + n] if i + n < len(expiries) else None


def deribit_name(asset, exp_ms):
    d = dt.datetime.fromtimestamp(exp_ms / 1000.0, UTC)
    return '%s-%d%s%s' % (asset, d.day, d.strftime('%b').upper(), d.strftime('%y'))


# ---------------------------------------------------------------------------------------------- collect: Binance

def bn_http():
    import funding_arb as FA
    return FA.Http(interval=0.5, weight_header='X-MBX-USED-WEIGHT-1M', weight_soft=1100)


def bn_paged(http, base, path, params, start_ms, end_ms, step_ms, limit=1000, key_time=0):
    """Page a Binance klines-style endpoint forward from start_ms. Rows are lists; row[key_time] is the open time."""
    rows, s = [], start_ms
    for _ in range(400):
        p = dict(params, startTime=s, endTime=end_ms, limit=limit)
        r = http.get(base + path, p)
        if not isinstance(r, list) or not r:
            break
        rows += r
        last = int(r[-1][key_time])
        if len(r) < limit or last + step_ms > end_ms:
            break
        s = last + step_ms
    seen = {}
    for x in rows:
        seen[int(x[key_time])] = x
    return [seen[k] for k in sorted(seen)]


def collect_binance(out, log):
    raw = Path(out) / 'raw' / 'binance'
    http = bn_http()
    now = int(time.time() * 1000)
    t0 = day_ms('2019-09-01')
    got = {}
    for pair in ('BTCUSDT', 'ETHUSDT'):
        for ct in ('CURRENT_QUARTER', 'NEXT_QUARTER', 'PERPETUAL'):
            fn = raw / ('cont_%s_%s_1d.json.gz' % (pair, ct))
            if not fn.exists():
                rows = bn_paged(http, BN_FAPI, '/fapi/v1/continuousKlines', {'pair': pair, 'contractType': ct,
                                                                            'interval': '1d'}, t0, now, DAY_MS)
                write_gz(fn, rows)
            got[fn.name] = len(read_gz(fn))
        fn = raw / ('index_%s_1d.json.gz' % pair)
        if not fn.exists():
            write_gz(fn, bn_paged(http, BN_FAPI, '/fapi/v1/indexPriceKlines', {'pair': pair, 'interval': '1d'},
                                  t0, now, DAY_MS))
        got[fn.name] = len(read_gz(fn))
    for sym in ('BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'HYPEUSDT'):
        fn = raw / ('funding_%s.json.gz' % sym)
        if not fn.exists():
            rows, s = [], t0
            for _ in range(60):
                r = http.get(BN_FAPI + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': now,
                                                                'limit': 1000})
                if not isinstance(r, list) or not r:
                    break
                rows += [{'t': int(x['fundingTime']), 'rate': float(x['fundingRate']),
                          'mark': fnum(x.get('markPrice'))} for x in r]
                if len(r) < 1000:
                    break
                s = int(r[-1]['fundingTime']) + 1
            write_gz(fn, rows)
        got[fn.name] = len(read_gz(fn))
        for kind, path in (('premium', '/fapi/v1/premiumIndexKlines'), ('perp', '/fapi/v1/klines')):
            fn = raw / ('%s_%s_1d.json.gz' % (kind, sym))
            if not fn.exists():
                write_gz(fn, bn_paged(http, BN_FAPI, path, {'symbol': sym, 'interval': '1d'}, t0, now, DAY_MS))
            got[fn.name] = len(read_gz(fn))
    # hourly spot closes for realised volatility (d): spot API, its own weight pool
    for sym in ('BTCUSDT', 'ETHUSDT'):
        fn = raw / ('spot1h_%s.json.gz' % sym)
        if not fn.exists():
            rows = bn_paged(http, BN_SPOT, '/api/v3/klines', {'symbol': sym, 'interval': '1h'}, day_ms('2021-01-01'),
                            now, HOUR_MS, limit=1000)
            write_gz(fn, [[int(x[0]), float(x[4])] for x in rows])
        got[fn.name] = len(read_gz(fn))
    log['binance'] = {'files': got, 'http': http.stats(), 'finished': utc()}


# ---------------------------------------------------------------------------------------------- collect: Deribit

def deribit(method, **params):
    d = get_json(DERIBIT + method, params, pause=0.15)
    if isinstance(d, dict) and 'result' in d:
        return d['result']
    return None


def collect_deribit(out, log):
    raw = Path(out) / 'raw' / 'deribit'
    now = int(time.time() * 1000)
    got, missing = {}, []
    for asset in ('BTC', 'ETH'):
        for exp in quarterly_expiries(2019, 2027):
            if exp - 400 * DAY_MS > now:
                continue
            name = deribit_name(asset, exp)
            fn = raw / ('fut_%s_1d.json.gz' % name)
            if not fn.exists():
                start = exp - 400 * DAY_MS
                r = deribit('get_tradingview_chart_data', instrument_name=name, start_timestamp=start,
                            end_timestamp=min(now, exp + DAY_MS), resolution='1D')
                if not r or r.get('status') != 'ok' or not r.get('ticks'):
                    missing.append(name)
                    write_gz(fn, {'missing': True})
                    continue
                write_gz(fn, {'ticks': r['ticks'], 'close': r['close'], 'volume': r.get('volume'),
                              'cost': r.get('cost'), 'expiry': exp})
            d = read_gz(fn)
            got[name] = 0 if d.get('missing') else len(d['ticks'])
        idx = '%s_usd' % asset.lower()
        fn = raw / ('index_%s.json.gz' % idx)
        if not fn.exists():
            write_gz(fn, deribit('get_index_chart_data', index_name=idx, range='all'))
        got[fn.name] = len(read_gz(fn))
        # Deribit's daily bars run 08:00 → 08:00 UTC, so the index they are compared with is the 08:00 delivery
        # price (a 30-minute average of the index before 08:00), one per day.
        fn = raw / ('delivery_%s.json.gz' % idx)
        if not fn.exists():
            rows, off = [], 0
            for _ in range(100):                     # the venue serves at most 100 a page
                r = deribit('get_delivery_prices', index_name=idx, offset=off, count=100)
                data = (r or {}).get('data') or []
                rows += data
                off += len(data)
                if not data or off >= int((r or {}).get('records_total') or 0):
                    break
            write_gz(fn, rows)
        got[fn.name] = len(read_gz(fn))
        fn = raw / ('dvol_%s.json.gz' % asset)
        if not fn.exists():
            rows, end = [], now
            for _ in range(20):
                r = deribit('get_volatility_index_data', currency=asset, start_timestamp=day_ms('2021-01-01'),
                            end_timestamp=end, resolution='1D')
                if not r or not r.get('data'):
                    break
                rows += r['data']
                if not r.get('continuation'):
                    break
                end = int(r['continuation'])
            write_gz(fn, sorted({int(x[0]): x for x in rows}.values(), key=lambda x: x[0]))
        got[fn.name] = len(read_gz(fn))
    log['deribit'] = {'instruments': got, 'missing': missing, 'finished': utc()}


# ---------------------------------------------------------------------------------------------- collect: Yahoo (CME)

def collect_yahoo(out, log):
    raw = Path(out) / 'raw' / 'yahoo'
    got = {}
    for sym in ('BTC=F', 'ETH=F', 'BTC-USD', 'ETH-USD'):
        fn = raw / ('%s_1h.json.gz' % sym.replace('=', '_'))
        if not fn.exists():
            d = get_json(YAHOO + urllib.parse.quote(sym), {'interval': '1h', 'range': '730d'}, pause=1.0)
            r = d['chart']['result'][0]
            q = r['indicators']['quote'][0]
            write_gz(fn, {'t': r['timestamp'], 'close': q['close'], 'volume': q.get('volume'), 'meta': r['meta']})
        got[fn.name] = len(read_gz(fn)['t'])
    log['yahoo'] = {'files': got, 'finished': utc()}


# ---------------------------------------------------------------------------------------------- collect: Boros

def boros(path, **params):
    d = get_json(BOROS + path, params or None, pause=0.35)
    return d


def boros_markets():
    out, tok = [], None
    for _ in range(20):
        p = {'limit': 200}
        if tok:
            p['resumeToken'] = tok
        d = boros('/v1/markets', **p)
        out += d.get('results') or []
        tok = d.get('resumeToken')
        if not tok:
            break
    return out


def collect_boros(out, log):
    raw = Path(out) / 'raw' / 'boros'
    raw.mkdir(parents=True, exist_ok=True)
    mk = boros_markets()
    write_json(raw / 'markets.json', {'collected_at': utc(), 'markets': mk})
    now_s = int(time.time())
    got, failed = {}, []
    for m in mk:
        mid = m['marketId']
        fn = raw / ('ind_%d.json.gz' % mid)
        if fn.exists():
            got[mid] = len(read_gz(fn).get('results') or [])
            continue
        mat = int(m['imData']['maturity'])
        try:
            d = boros('/v1/indicators', marketId=mid, timeFrame='1d', startTimestamp=max(0, mat - 450 * DAY_S),
                      endTimestamp=min(now_s, mat + DAY_S), select='u,mr')
            o = boros('/v1/markets/ohlcv', marketId=mid, timeFrame='1d', startTimestamp=max(0, mat - 199 * DAY_S),
                      endTimestamp=min(now_s, mat + DAY_S))
        except RuntimeError as e:
            failed.append({'market': mid, 'error': str(e)[:200]})
            continue
        write_gz(fn, {'results': d.get('results') if isinstance(d, dict) else d, 'ohlcv': o})
        got[mid] = len((d or {}).get('results') or [])
    # Boros's daily `u` is the venue's funding settled in (d, d+1] times 365 (checked against Binance's own settlements
    # on disk: 2025-10-01..05 agree to 1e-12), so the per-market indicator series is the floating leg itself. The
    # catalogue of funding streams is kept for the manifest.
    syms = boros('/v1/funding-rate/all-funding-rate-symbols')
    write_json(raw / 'funding_symbols.json', syms)
    und = {'streams': len((syms or {}).get('fundingRateSymbols') or [])}
    log['boros'] = {'markets': len(mk), 'indicator_files': len(got), 'underlying': und, 'failed': failed,
                    'finished': utc()}


def boros_book_depth(book, side, band):
    """Notional (in the market's YU units) resting within `band` (APR, absolute) of the best price on one side of a
    Boros order book reply; None if the side is empty."""
    lv = (book or {}).get(side) or {}
    ia, sz = lv.get('ia') or [], lv.get('sz') or []
    if not ia:
        return None
    best = ia[0]
    return sum(float(s) for a, s in zip(ia, sz) if abs(float(a) - float(best)) <= band)


# ---------------------------------------------------------------------------------------------- collect: Hyperliquid

def collect_hl(out, log, interval=5.0):
    """Hyperliquid funding before the shared store (2023-05 → 2025-10-01) for the coins this study needs."""
    import perp_rpc as R
    raw = Path(out) / 'raw' / 'hl'
    api = R.Info(interval=interval)
    end = day_ms('2025-10-01') + HOUR_MS
    got = {}
    for coin, start in (('BTC', '2023-05-01'), ('ETH', '2023-05-01'), ('SOL', '2023-05-01'), ('HYPE', '2024-11-01')):
        fn = raw / ('funding_%s_pre.json.gz' % coin)
        if fn.exists():
            got[coin] = len(read_gz(fn))
            continue
        rows, s = [], day_ms(start)
        for _ in range(200):
            r = R.funding_history(api, coin, s, end) or []
            rows += r
            if len(r) < 500:
                break
            s = int(r[-1]['time']) + 1
        write_gz(fn, rows)
        got[coin] = len(rows)
        print('hl funding %s: %d rows %s → %s' % (coin, len(rows), rows and utc(rows[0]['time']),
                                                  rows and utc(rows[-1]['time'])), flush=True)
    # daily closes for HYPE before Binance listed it (2025-05-31): Hyperliquid serves its last 5,000 daily bars
    fn = raw / 'candles_1d_HYPE.json.gz'
    if not fn.exists():
        write_gz(fn, R.candles(api, 'HYPE', '1d', day_ms('2024-11-29'), int(time.time() * 1000)) or [])
    got['HYPE_1d_candles'] = len(read_gz(fn))
    log['hl'] = {'rows': got, 'api': api.stats(), 'finished': utc()}


# ---------------------------------------------------------------------------------------------- collect: live books

def collect_books(out, log):
    """Live depth for capacity: Binance quarterlies and perps (+ spot), Deribit futures, Hyperliquid perps and spot,
    Boros order books of live markets, with open interest wherever the venue publishes it."""
    raw = Path(out) / 'raw' / 'books'
    raw.mkdir(parents=True, exist_ok=True)
    snap = {'at': utc()}
    http = bn_http()
    ex = http.get(BN_FAPI + '/fapi/v1/exchangeInfo')
    quarters = [s['symbol'] for s in ex['symbols'] if s['contractType'] in ('CURRENT_QUARTER', 'NEXT_QUARTER')
                and s['pair'] in ('BTCUSDT', 'ETHUSDT')]
    bn = {}
    for sym in quarters + ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'HYPEUSDT']:
        bn[sym] = {'depth': http.get(BN_FAPI + '/fapi/v1/depth', {'symbol': sym, 'limit': 500}),
                   'oi': http.get(BN_FAPI + '/fapi/v1/openInterest', {'symbol': sym}),
                   'ticker': http.get(BN_FAPI + '/fapi/v1/ticker/24hr', {'symbol': sym})}
    for sym in ('BTCUSDT', 'ETHUSDT', 'SOLUSDT'):
        bn['spot:' + sym] = {'depth': http.get(BN_SPOT + '/api/v3/depth', {'symbol': sym, 'limit': 1000}),
                             'ticker': http.get(BN_SPOT + '/api/v3/ticker/24hr', {'symbol': sym})}
    snap['binance'] = bn
    der = {}
    for cur in ('BTC', 'ETH'):
        summ = deribit('get_book_summary_by_currency', currency=cur, kind='future') or []
        der[cur] = {'summary': summ, 'books': {}}
        for s in summ:
            name = s['instrument_name']
            if 'PERPETUAL' in name:
                continue
            der[cur]['books'][name] = deribit('get_order_book', instrument_name=name, depth=100)
    snap['deribit'] = der
    import perp_rpc as R
    api = R.Info(interval=1.0)
    meta = R.meta_and_ctxs(api)
    hl = {'meta_ctxs': meta, 'books': {}}
    for coin in ('BTC', 'ETH', 'SOL', 'HYPE'):
        hl['books'][coin] = R.l2_book(api, coin)
    for pair in ('@142', '@151', '@156', '@107'):
        hl['books'][pair] = R.l2_book(api, pair)
    hl['coarse_25bp'] = hl_coarse_depth(api)
    hl['api'] = api.stats()
    snap['hl'] = hl
    mk = boros_markets()
    live = [m for m in mk if int(m['imData']['maturity']) > time.time()]
    bb = {}
    for m in live:
        try:
            bb[m['marketId']] = boros('/v1/markets/order-book', marketId=m['marketId'], tickSize=0.0001,
                                      includeAmm='true')
        except RuntimeError as e:
            bb[m['marketId']] = {'error': str(e)[:160]}
    snap['boros'] = {'markets': live, 'books': bb}
    write_gz(raw / 'snapshot.json.gz', snap)
    log['books'] = {'binance_symbols': sorted(bn), 'deribit': {c: len(v['books']) for c, v in der.items()},
                    'hl_books': sorted(hl['books']), 'boros_live_markets': len(live), 'finished': utc()}


def hl_coarse_depth(api, coins=('BTC', 'ETH', 'HYPE', '@107', '@142', '@151')):
    """Hyperliquid's default l2Book shows 20 levels at full precision (2–5bp of HYPE), which understates depth; the
    4-significant-figure aggregation spans ~25bp. USD within 25bp each side, per coin."""
    out = {}
    for c in coins:
        b = api.post({'type': 'l2Book', 'coin': c, 'nSigFigs': 4})
        lv = b.get('levels') or [[], []]
        if not lv[0] or not lv[1]:
            continue
        mid = (float(lv[0][0]['px']) + float(lv[1][0]['px'])) / 2
        out[c] = {'mid': mid, 'bid_25bp': depth_usd(lv[0], mid, 25), 'ask_25bp': depth_usd(lv[1], mid, 25),
                  'span_bp': (mid / float(lv[0][-1]['px']) - 1) * 1e4}
    return out


# ---------------------------------------------------------------------------------------------- collect: chain

def rpc_call(method, params, endpoints=None, timeout=60):
    import drpc
    return drpc.rpc(method, params, endpoints=endpoints or drpc.ENDPOINTS, timeout=timeout, retries=3)


def estimate_block(ts):
    """A block near timestamp ts from two anchors (post-merge 12.05 s, pre-merge 13.3 s). The block's own timestamp
    is read afterwards, so the estimate only has to be close."""
    if ts >= MERGE_TS:
        return int(MERGE_BLOCK + (ts - MERGE_TS) / 12.05)
    return int(MERGE_BLOCK - (MERGE_TS - ts) / 13.3)


def chain_grid(first_ts, last_ts):
    """Sampling grid: weekly before sUSDe existed, every 3 days after (yields are compared over weeks and months)."""
    out, t = [], first_ts
    while t <= last_ts:
        out.append(t)
        t += (3 if t >= SUSDE_DEPLOY_TS else 7) * DAY_S
    return out


def collect_chain(out, log, workers=3):
    raw = Path(out) / 'raw' / 'chain'
    raw.mkdir(parents=True, exist_ok=True)
    fn = raw / 'samples.json'
    have = json.loads(fn.read_text()) if fn.exists() else {}
    grid = chain_grid(int(day_ms('2020-01-01') / 1000), int(day_ms('2026-03-14') / 1000))
    todo = [t for t in grid if str(t) not in have]
    errors = []

    def one(t):
        blk = estimate_block(t)
        rec = {'target_ts': t, 'block': blk}
        try:
            h = rpc_call('eth_getBlockByNumber', [hex(blk), False])
            rec['ts'] = int(h['timestamp'], 16)
            if t < day_ms('2024-09-27') / 1000:
                r = rpc_call('eth_call', [{'to': POT, 'data': SEL['dsr']}, hex(blk)])
                rec['dsr_ray'] = str(int(r, 16))
            if WSTETH_DEPLOY_TS <= t < day_ms('2024-09-27') / 1000:
                r = rpc_call('eth_call', [{'to': WSTETH, 'data': SEL['stEthPerToken']}, hex(blk)])
                if r and r != '0x':                 # '0x' before the contract existed at that block
                    rec['wsteth'] = int(r, 16) / 1e18
            if t >= SUSDE_DEPLOY_TS:
                data = SEL['convertToAssets'] + hex(10 ** 18)[2:].rjust(64, '0')
                r = rpc_call('eth_call', [{'to': SUSDE, 'data': data}, hex(blk)])
                rec['susde'] = int(r, 16) / 1e18
        except Exception as e:  # noqa: BLE001 - recorded, the grid point is retried on the next run
            rec['error'] = str(e)[:200]
        return t, rec

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, (t, rec) in enumerate(ex.map(one, todo)):
            if 'error' in rec:
                errors.append(rec)
            else:
                have[str(t)] = rec
            if i % 50 == 0:
                fn.write_text(json.dumps(have))
                print('chain %d/%d' % (i, len(todo)), flush=True)
    fn.write_text(json.dumps(have))
    log['chain'] = {'grid': len(grid), 'samples': len(have), 'errors': len(errors),
                    'error_examples': errors[:5], 'finished': utc()}


# ============================================================================================== analysis: shared

def day_of(ms):
    """Day index d (epoch days) whose window (d 00:00, d+1 00:00] UTC holds a settlement stamped at ms. Timestamps are
    rounded to the hour first: venues stamp a settlement a few milliseconds after the hour."""
    h = int(round(ms / HOUR_MS)) * HOUR_MS
    return (h - 1) // DAY_MS


def daily_sums(events):
    """{day: sum of rates}, {day: count} from [(ms, rate)] (duplicates by hour removed, last one wins)."""
    by_hour = {}
    for t, r in events:
        by_hour[int(round(t / HOUR_MS))] = r
    s, n = {}, {}
    for h, r in by_hour.items():
        d = day_of(h * HOUR_MS)
        s[d] = s.get(d, 0.0) + r
        n[d] = n.get(d, 0) + 1
    return s, n


def trailing_apr(f, d, k, min_frac=0.8):
    """Mean daily funding over the k days before d, x365 (None when fewer than min_frac of the days exist)."""
    vals = [f[d - i] for i in range(1, k + 1) if (d - i) in f]
    if len(vals) < max(1, int(math.ceil(min_frac * k))):
        return None
    return sum(vals) / len(vals) * 365.0


def interp_log(xs, ys, x):
    """Log-linear interpolation of a NAV series (xs ascending); None outside the range."""
    if not xs or x < xs[0] or x > xs[-1]:
        return None
    i = bisect.bisect_left(xs, x)
    if xs[i] == x:
        return ys[i]
    x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
    w = (x - x0) / (x1 - x0)
    return math.exp(math.log(y0) + w * (math.log(y1) - math.log(y0)))


def nav_daily_returns(points, d0, d1):
    """{day: ln(NAV(d+1)/NAV(d))} from [(ts seconds, nav)] sampled irregularly, interpolated log-linearly."""
    pts = sorted(points)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    out = {}
    for d in range(d0, d1):
        a, b = interp_log(xs, ys, d * DAY_S), interp_log(xs, ys, (d + 1) * DAY_S)
        if a and b:
            out[d] = math.log(b / a)
    return out


def load_navs(out):
    """sUSDe, wstETH and the savings-rate path as daily log returns, from the chain samples this study read and the
    daily NAVs the redemption study read (2024-09-26 →)."""
    samples = json.loads((Path(out) / 'raw' / 'chain' / 'samples.json').read_text())
    st = json.loads(NAV_STATE.read_text())['samples']
    susde = [(r['ts'], r['susde']) for r in samples.values() if r.get('susde')]
    susde += [(r['ts'], r['value']) for r in st['susde_nav']]
    wst = [(r['ts'], r['wsteth']) for r in samples.values() if r.get('wsteth')]
    wst += [(r['ts'], r['value']) for r in st['wsteth_nav']]
    susds = [(r['ts'], r['value']) for r in st['susds_nav']]
    d_end = int(time.time()) // DAY_S
    nav = {'susde': nav_daily_returns(susde, SUSDE_DEPLOY_TS // DAY_S + 1, d_end),
           'wsteth': nav_daily_returns(wst, WSTETH_DEPLOY_TS // DAY_S + 7, d_end),
           'susds': nav_daily_returns(susds, min(t for t, _ in susds) // DAY_S + 1, d_end)}
    # Maker's DSR before the SSR: the per-second rate `dsr` (ray), held as a step function between samples.
    dsr = sorted((r['ts'], int(r['dsr_ray'])) for r in samples.values() if r.get('dsr_ray'))
    path = {}
    first_susds = min(nav['susds']) if nav['susds'] else None
    for d in range(day_ms('2019-09-01') // DAY_MS, d_end):
        if first_susds is not None and d >= first_susds and d in nav['susds']:
            path[d] = nav['susds'][d] * 365.0
            continue
        i = bisect.bisect_right([t for t, _ in dsr], d * DAY_S) - 1
        if i >= 0:
            per_sec = dsr[i][1] / 1e27
            path[d] = math.log(per_sec) * 86400 * 365.0
        elif dsr:
            path[d] = math.log(dsr[0][1] / 1e27) * 86400 * 365.0
    nav['savings_path'] = path
    nav['counts'] = {'susde_points': len(susde), 'wsteth_points': len(wst), 'susds_points': len(susds),
                     'dsr_points': len(dsr)}
    return nav


def bench_of(mode, nav):
    """Benchmark APR by day: the constant SSR (protocol), or the savings rate paid at the time (DSR, then SSR)."""
    if mode == 'const':
        return lambda d: SSR
    path = nav['savings_path']
    return lambda d: path.get(d, SSR)


def ann(x, days):
    return x * 365.0 / days if days else None


def pctl(values, q):
    v = sorted(x for x in values if x is not None)
    if not v:
        return None
    k = (len(v) - 1) * q
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def summary(values):
    v = [x for x in values if x is not None]
    if not v:
        return {'n': 0}
    return {'n': len(v), 'mean': statistics.fmean(v), 'median': statistics.median(v), 'p10': pctl(v, 0.10),
            'p90': pctl(v, 0.90), 'min': min(v), 'max': max(v)}


def year_of_day(d):
    return dt.datetime.fromtimestamp(d * DAY_S, UTC).year


def concentration(series, block=7, top=4):
    """Share of a series' total that came from its best `top` blocks of `block` days (how lumpy a carry is)."""
    blocks = [sum(series[i:i + block]) for i in range(0, len(series), block)]
    tot = sum(blocks)
    if not blocks or tot <= 0:
        return None
    return sum(sorted(blocks, reverse=True)[:top]) / tot


# ============================================================================================== (a) dated basis

CAPITAL_A = {
    # name: (capital per notional, share of capital that earns the benchmark while held)
    'portfolio': (1.0, 0.0),     # spot is the short's collateral: Binance PM / multi-assets, Deribit coin margin
    'cash3x': (4.0 / 3.0, 0.0),  # spot plus the short margined separately in cash at 3x, the cash idle
    'cme_tbill': (1.4, 0.4),     # CME: 40% initial margin posted in T-bills that keep earning (taken as SSR)
    'cme_idle': (1.4, 0.0),      # CME with the margin in cash that earns nothing
}


def locked_excess(g_net, tau_days, model, bench):
    """Excess over the benchmark, per year, on the capital a hold-to-expiry basis trade ties up.
    g_net = F/S - 1 - all costs (fraction of notional); the margin share in `model` earns the benchmark."""
    K, earn = CAPITAL_A[model]
    apr_notional = g_net * 365.0 / tau_days
    return (apr_notional + earn * bench) / K - bench


def bn_basis_rows(raw, pair):
    """{day: {'front': (F, exp_ms, tau_days, quote_volume), 'next': ..., 'S': index}} at the close of each day."""
    rb = Path(raw) / 'binance'
    ix = {int(r[0]) // DAY_MS: float(r[4]) for r in read_gz(rb / ('index_%s_1d.json.gz' % pair))}
    exps = quarterly_expiries(2019, 2029)
    out = {}
    for which, ct, n in (('front', 'CURRENT_QUARTER', 0), ('next', 'NEXT_QUARTER', 1)):
        for r in read_gz(rb / ('cont_%s_%s_1d.json.gz' % (pair, ct))):
            d = int(r[0]) // DAY_MS
            t_close = (d + 1) * DAY_MS
            if d not in ix or float(r[7]) <= 0:
                continue
            exp = nth_expiry_after(exps, t_close - 1, n)
            out.setdefault(d, {'S': ix[d]})[which] = (float(r[4]), exp, (exp - t_close) / DAY_MS, float(r[7]))
    return out


def deribit_basis_rows(raw, asset):
    """Deribit's daily bars open and close at 08:00 UTC (checked against its hourly bars: the 1D bar stamped
    2024-03-12 08:00 closes at 74,092.5, the hourly close at 2024-03-13 08:00). Each bar is keyed by the day on which
    it closes and compared with that day's 08:00 delivery price."""
    rd = Path(raw) / 'deribit'
    dl = read_gz(rd / ('delivery_%s_usd.json.gz' % asset.lower()))
    ix = {day_ms(r['date']) // DAY_MS: float(r['delivery_price']) for r in dl}
    exps = quarterly_expiries(2018, 2028)
    closes = {}
    for exp in exps:
        fn = rd / ('fut_%s_1d.json.gz' % deribit_name(asset, exp))
        if not fn.exists():
            continue
        d = read_gz(fn)
        if d.get('missing'):
            continue
        for t, c, v in zip(d['ticks'], d['close'], d.get('volume') or [None] * len(d['ticks'])):
            if v is not None and v <= 0:
                continue
            close_day = (int(t) + DAY_MS) // DAY_MS          # the bar closes at 08:00 on this day
            closes.setdefault(exp, {})[close_day] = (float(c), float(v or 0))
    out = {}
    days = sorted({day for m in closes.values() for day in m})
    for day in days:
        t_close = day * DAY_MS + 8 * HOUR_MS
        S = ix.get(day)
        if S is None:
            continue
        row = {'S': S, 't_close': t_close}
        for which, n in (('front', 0), ('next', 1)):
            exp = nth_expiry_after(exps, t_close - 1, n)
            c = (closes.get(exp) or {}).get(day)
            if c:
                row[which] = (c[0], exp, (exp - t_close) / DAY_MS, c[1])
        if len(row) > 2:
            out[day] = row
    return out


def cme_basis_rows(raw, asset, hour_utc=19):
    """Daily samples from Yahoo hourly bars: the bar opening at `hour_utc` (inside CME's session), future against
    BTC-USD/ETH-USD at the same hour, front month expiring the last Friday of the month."""
    ry = Path(raw) / 'yahoo'
    fut, spot = read_gz(ry / ('%s_F_1h.json.gz' % asset)), read_gz(ry / ('%s-USD_1h.json.gz' % asset))
    F = {int(t): c for t, c in zip(fut['t'], fut['close']) if c}
    S = {int(t): c for t, c in zip(spot['t'], spot['close']) if c}
    exps = monthly_expiries(2023, 2028)
    out = {}
    for t in sorted(F):
        if (t % DAY_S) != hour_utc * 3600 or t not in S:
            continue
        day = t // DAY_S
        t_close = (t + 3600) * 1000
        exp = nth_expiry_after(exps, t_close, 0)
        out[day] = {'S': S[t], 'front': (F[t], exp, (exp - t_close) / DAY_MS, 1.0)}
    return out


def basis_entry_costs(venue):
    """(entry, exit at expiry, spot one side) costs as fractions of notional, half-spreads included."""
    if venue == 'binance':
        spot, fut, dlv, hs = FEE['bn_spot'], FEE['bn_quarter'], FEE['bn_delivery'], 1.0
    elif venue == 'deribit':
        spot, fut, dlv, hs = FEE['bn_spot'], FEE['deribit_fut'], FEE['deribit_delivery'], 2.0
    else:
        spot, fut, dlv, hs = FEE['cme_spot'], FEE['cme_fut'], 0.5, 1.5
    return (spot + fut + hs) / 1e4, (spot + dlv) / 1e4, spot / 1e4


def basis_distribution(rows, venue, model, bench_fn, min_tau=14):
    """Every day's locked yield for each tenor: annualised basis, net locked APR on capital, excess over SSR."""
    c_in, c_out, _ = basis_entry_costs(venue)
    recs = []
    for day in sorted(rows):
        r = rows[day]
        for which in ('front', 'next'):
            x = r.get(which)
            if not x or x[2] < min_tau:
                continue
            F, exp, tau, _ = x
            g = F / r['S'] - 1.0
            b = bench_fn(day)
            recs.append({'day': day, 'tenor': which, 'tau': tau, 'basis_apr': g * 365.0 / tau,
                         'excess': locked_excess(g - c_in - c_out, tau, model, b)})
    return recs


def simulate_basis(rows, venue, model, bench_fn, tenor, x, min_tau=14, start=None, end=None):
    """Hold-to-expiry basis trades, one at a time: at a day's close, if idle and the chosen tenor's locked excess over
    the benchmark (after a full round trip) beats x, enter; the locked P&L accrues evenly to the expiry day. A trade
    that ends the same day another begins keeps its spot: neither spot fee is paid (a roll). Returns the daily excess
    series on capital (aligned with the sorted days in [start, end)) and the trades."""
    c_in, c_out, c_spot = basis_entry_costs(venue)
    K, earn = CAPITAL_A[model]
    days = [d for d in sorted(rows) if (start is None or d >= start) and (end is None or d < end)]
    if not days:
        return [], [], []
    accr = {}           # day -> accrual on notional
    extra_cost = {}     # day -> cost on notional
    trades = []
    busy_until = None   # expiry day of the open trade
    held_spot_until = None
    for day in days:
        if busy_until is not None and day < busy_until:
            continue
        r = rows[day]
        cand = []
        for w in (('front', 'next') if tenor == 'best' else (tenor,)):
            v = r.get(w)
            if v and v[2] >= min_tau:
                g = v[0] / r['S'] - 1.0
                cand.append((locked_excess(g - c_in - c_out, v[2], model, bench_fn(day)), w, v, g))
        if not cand:
            continue
        ex, w, v, g = max(cand)
        if ex <= x:
            continue
        rolled = held_spot_until is not None and held_spot_until == day
        if rolled and trades:
            trades[-1]['rolled_into_next'] = True
            extra_cost[day] = extra_cost.get(day, 0.0) - c_spot     # the previous trade's spot sale is not made
        cost = c_in - (c_spot if rolled else 0.0)
        d_exp = v[1] // DAY_MS
        n = max(1, d_exp - day)
        net = g - cost - c_out
        for k in range(day + 1, d_exp + 1):
            accr[k] = accr.get(k, 0.0) + net / n
        trades.append({'entry_day': day, 'entry': ymd(day * DAY_MS), 'tenor': w, 'tau': v[2], 'gross': g, 'net': net,
                       'excess_at_entry': ex, 'rolled_from_previous': rolled})
        busy_until = d_exp
        held_spot_until = d_exp
    out_days = [d for d in range(days[0], days[-1] + 1)]
    series = []
    for d in out_days:
        b = bench_fn(d)
        a = accr.get(d)
        c = extra_cost.get(d, 0.0)
        if a is None:
            series.append(-c / K)
        else:
            series.append((a - c + earn * b / 365.0) / K - b / 365.0)
    return out_days, series, trades


def analyze_basis(raw, nav, split_frac=0.5):
    venues = {}
    for venue, assets in (('binance', ('BTC', 'ETH')), ('deribit', ('BTC', 'ETH')), ('cme', ('BTC', 'ETH'))):
        for asset in assets:
            try:
                if venue == 'binance':
                    rows = bn_basis_rows(raw, asset + 'USDT')
                elif venue == 'deribit':
                    rows = deribit_basis_rows(raw, asset)
                else:
                    rows = cme_basis_rows(raw, asset)
            except (FileNotFoundError, KeyError, TypeError) as e:
                venues['%s:%s' % (venue, asset)] = {'error': repr(e)[:200]}
                continue
            if not rows:
                continue
            venues['%s:%s' % (venue, asset)] = basis_venue(rows, venue, asset, nav, split_frac)
    return venues


def basis_venue(rows, venue, asset, nav, split_frac):
    model = 'cme_tbill' if venue == 'cme' else 'portfolio'
    alt = 'cme_idle' if venue == 'cme' else 'cash3x'
    const, hist = bench_of('const', nav), bench_of('hist', nav)
    days = sorted(rows)
    d0, d1 = days[0], days[-1] + 1
    split = d0 + int((d1 - d0) * split_frac)
    dist = basis_distribution(rows, venue, model, const)
    dist_hist = basis_distribution(rows, venue, model, hist)
    by_year = {}
    for rec in dist:
        y = year_of_day(rec['day'])
        by_year.setdefault((y, rec['tenor']), []).append(rec)
    years = {}
    for (y, ten), recs in sorted(by_year.items()):
        ex = [r['excess'] for r in recs]
        years.setdefault(str(y), {})[ten] = {
            'days': len(recs), 'basis_apr': summary([r['basis_apr'] for r in recs]), 'excess': summary(ex),
            'share_excess_ge_2pp': sum(1 for v in ex if v >= 0.02) / len(ex), 'share_excess_gt_0': sum(1 for v in ex if v > 0) / len(ex)}
    # the protocol: tenor x threshold, chosen on the first half of the venue's days, tested once on the rest
    xs = (0.0, 0.01, 0.02, 0.03, 0.05, 0.08)
    tenors = ('front', 'next') if venue != 'cme' else ('front',)
    variants, tr_by, od_by = {}, {}, {}
    for ten in tenors:
        for x in xs:
            name = '%s_x%.0fpp' % (ten, 100 * x)
            od, ser, trs = simulate_basis(rows, venue, model, const, ten, x)
            variants[name] = ser
            tr_by[name] = trs
            od_by[name] = od
    n = min(len(v) for v in variants.values())
    frac = (split - d0) / (d1 - d0)
    ctt = B.choose_then_test({k: v[:n] for k, v in variants.items()}, frac=frac, periods_per_year=365,
                             key='ann_return')
    ch = ctt['chosen']
    test_trades = [t for t in tr_by[ch] if t['entry_day'] >= split]
    train_trades = [t for t in tr_by[ch] if t['entry_day'] < split]
    t_test = [t['excess_at_entry'] for t in test_trades]
    # the chosen rule on the other capital model and against the savings rate paid at the time
    ten, x = ch.split('_x')[0], float(ch.split('_x')[1][:-2]) / 100.0
    _, ser_alt, _ = simulate_basis(rows, venue, alt, const, ten, x)
    _, ser_hist, tr_hist = simulate_basis(rows, venue, model, hist, ten, x)
    c = B.cutoff_index(n, frac)
    oos = ctt['out_of_sample']
    by_year = {}
    for d, v in zip(od_by[ch][:n], variants[ch][:n]):
        by_year.setdefault(str(year_of_day(d)), []).append(v)
    return {
        'chosen_by_year_ann_excess': {y: sum(v) / len(v) * 365.0 for y, v in by_year.items()},
        'chosen_by_year_time_in_trade': {y: share_active(v) for y, v in by_year.items()},
        'locked_now': {w: (locked_excess(rows[days[-1]][w][0] / rows[days[-1]]['S'] - 1.0 - sum(basis_entry_costs(venue)[:2]),
                                         rows[days[-1]][w][2], model, SSR), rows[days[-1]][w][2],
                           (rows[days[-1]][w][0] / rows[days[-1]]['S'] - 1.0) * 365.0 / rows[days[-1]][w][2])
                       for w in ('front', 'next') if rows[days[-1]].get(w)},
        'venue': venue, 'asset': asset, 'capital_model': model, 'alt_capital_model': alt,
        'first_day': ymd(d0 * DAY_MS), 'last_day': ymd((d1 - 1) * DAY_MS), 'split_day': ymd(split * DAY_MS),
        'days_with_quotes': len(days), 'locked_by_year': years,
        'locked_all': {'excess': summary([r['excess'] for r in dist]),
                       'share_excess_ge_2pp': (sum(1 for r in dist if r['excess'] >= 0.02) / len(dist)) if dist else None,
                       'excess_vs_savings_paid': summary([r['excess'] for r in dist_hist])},
        'protocol': {k: ctt[k] for k in ('chosen', 'n_variants', 'in_sample', 'out_of_sample', 'oos_rank', 'oos_t',
                                         'oos_p', 'bh_survivors_full_sample')},
        'chosen_test': {'trades': len(test_trades), 'mean_locked_excess': statistics.fmean(t_test) if t_test else None,
                        't_trades': tstat(t_test), 'share_time_in_trade': share_active(variants[ch][c:n]),
                        'ann_excess_alt_capital': B.perf(ser_alt[c:n], 365).get('ann_return'),
                        'ann_excess_vs_savings_paid': B.perf(ser_hist[c:n], 365).get('ann_return'),
                        'rolls': sum(1 for t in test_trades if t['rolled_from_previous'])},
        'chosen_train': {'trades': len(train_trades),
                         'mean_locked_excess': statistics.fmean([t['excess_at_entry'] for t in train_trades]) if train_trades else None},
        'all_variants_test_ann_excess': {k: B.perf(v[c:n], 365).get('ann_return') for k, v in variants.items()},
        'all_variants_train_ann_excess': {k: B.perf(v[:c], 365).get('ann_return') for k, v in variants.items()},
        'trades_chosen': tr_by[ch][-12:],
        'test_ann_excess_on_capital': oos.get('ann_return'),
    }


def tstat(v):
    v = [x for x in v if x is not None]
    if len(v) < 3:
        return None
    sd = statistics.stdev(v)
    return statistics.fmean(v) / (sd / math.sqrt(len(v))) if sd > 0 else None


def share_active(series):
    return (sum(1 for v in series if v != 0) / len(series)) if series else None


# ============================================================================================== (b) DIY Ethena

ASSETS_B = ('BTC', 'ETH', 'SOL', 'HYPE')


def load_bn_funding(raw, asset):
    fn = Path(raw) / 'binance' / ('funding_%sUSDT.json.gz' % asset)
    return [(r['t'], r['rate']) for r in read_gz(fn)] if fn.exists() else []


def load_hl_funding(raw, asset):
    ev = []
    pre = Path(raw) / 'hl' / ('funding_%s_pre.json.gz' % asset)
    if pre.exists():
        ev += [(int(r['time']), float(r['fundingRate']), fnum(r.get('premium'))) for r in read_gz(pre)]
    st = PERPS_STORE / 'funding' / ('%s.json.gz' % asset)
    if st.exists():
        ev += [(int(r['time']), float(r['fundingRate']), fnum(r.get('premium'))) for r in read_gz(st)]
    return ev


def bn_daily_premium(raw, asset):
    fn = Path(raw) / 'binance' / ('premium_%sUSDT_1d.json.gz' % asset)
    return {int(r[0]) // DAY_MS: float(r[4]) for r in read_gz(fn)} if fn.exists() else {}


def bn_daily_px(raw, asset):
    fn = Path(raw) / 'binance' / ('perp_%sUSDT_1d.json.gz' % asset)
    if not fn.exists():
        return {}, {}
    rows = read_gz(fn)
    return ({int(r[0]) // DAY_MS: float(r[4]) for r in rows}, {int(r[0]) // DAY_MS: float(r[2]) for r in rows})


def hl_daily_premium(events):
    """Hyperliquid's hourly premium at 00:00 UTC, keyed by the day that just ended (the basis at decision time)."""
    out = {}
    for t, _, prem in events:
        h = int(round(t / HOUR_MS)) * HOUR_MS
        if h % DAY_MS == 0 and prem is not None:
            out[h // DAY_MS - 1] = prem
    return out


def venue_costs(venue, asset):
    """One side of each leg, fraction of notional: (spot leg, perp leg). The spot leg is bought on Binance spot in
    every variant (Hyperliquid's spot books are thin: funding_arb found under $5k within 10bp on most coins)."""
    hs = HALF_SPREAD.get(asset, 3.0)
    spot = (FEE['bn_spot'] + hs) / 1e4
    perp = ((FEE['bn_perp'] if venue == 'binance' else FEE['hl_perp']) + hs) / 1e4
    return spot, perp


def best_venue_schedule(f_by_venue, days, lookback=30):
    """At the first day of each month, the venue whose trailing `lookback`-day funding was highest (ties: first)."""
    sched, cur = {}, None
    for d in days:
        if cur is None or dt.datetime.fromtimestamp(d * DAY_S, UTC).day == 1:
            best = None
            for v, f in f_by_venue.items():
                s = trailing_apr(f, d, lookback)
                if s is not None and (best is None or s > best[0]):
                    best = (s, v)
            if best:
                cur = best[1]
        sched[d] = cur
    return sched


def simulate_carry(days, f_by_venue, p_by_venue, rule, spot_cost, perp_cost, K, bench_fn, schedule=None,
                   extra=None, closes=None, highs=None, lev=None, theta=None, borrow_apr=0.0, borrow_base=0.0):
    """Long spot / short perp, decided at 00:00 UTC each day, P&L per unit of capital.

    f_by_venue[v][d]   funding the short receives on day d (sum of settlements in (d, d+1]);
    p_by_venue[v][d]   the perp's premium over the index at the end of day d (the basis the short is marked at);
    rule               {'kind': 'always'} or {'kind': 'thr', 'k': lookback days, 'x': hurdle over the benchmark,
                       'h': hysteresis below the hurdle before leaving};
    spot_cost, perp_cost[v]  one side of each leg; schedule[d] the venue of the short (None: the only venue);
    extra[d]           a further accrual on notional while held (wstETH's staking yield);
    closes/highs, lev  for separately margined legs: rebalance when the price has moved 1/(2L) from the last
                       rebalance (cost: the move times one side of both legs), and count days whose high came within
                       1% of the short's liquidation before that rebalance (a diagnostic; liquidation is not simulated);
    theta, borrow_apr, borrow_base   for spot-as-collateral on Hyperliquid's portfolio margin: the short's margin
                       (`borrow_base` of notional) and any loss on it after a rise are borrowed against the spot at
                       `borrow_apr`; rebalanced (repaid by selling spot and buying back short) when the price has moved
                       `theta` from the last rebalance.

    Out of the carry the capital earns the benchmark. Returns the daily excess series and the bookkeeping."""
    pos, venue, p_ref = False, None, None
    ex, inpos = [], []
    st = {'entries': 0, 'exits': 0, 'switches': 0, 'rebalances': 0, 'liq_near': 0, 'funding': 0.0, 'basis': 0.0,
          'extra': 0.0, 'costs': 0.0, 'days_in': 0, 'neg_funding_days_in': 0}
    theta = (0.5 / lev) if lev else theta
    only = next(iter(f_by_venue))
    st['borrow'] = 0.0
    last = days[-1]
    for d in days:
        b = bench_fn(d)
        v = (schedule.get(d) if schedule else only) or venue or only
        f, p = f_by_venue[v], p_by_venue.get(v, {})
        cost = 0.0
        want = pos
        if rule['kind'] == 'always':
            want = d in f or pos
        else:
            sig = trailing_apr(f, d, rule['k'])
            if sig is not None:
                if not pos and sig > b + rule['x']:
                    want = True
                elif pos and sig < b + rule['x'] - rule['h']:
                    want = False
        if pos and not want:
            cost += spot_cost + perp_cost[venue]
            st['exits'] += 1
            pos = False
        elif not pos and want:
            cost += spot_cost + perp_cost[v]
            st['entries'] += 1
            pos, venue = True, v
            p_ref = closes.get(d - 1) if closes else None
        elif pos and v != venue:
            cost += perp_cost[venue] + perp_cost[v]
            st['switches'] += 1
            venue = v
        if pos and d == last:
            cost += spot_cost + perp_cost[venue]        # closed at the end of the sample
        if pos:
            f, p = f_by_venue[venue], p_by_venue.get(venue, {})
            fund = f.get(d, 0.0)
            mtm = -(p[d] - p[d - 1]) if (d in p and (d - 1) in p) else 0.0
            ext = extra.get(d, 0.0) if extra else 0.0
            if p_ref is None and closes and (d - 1) in closes:
                p_ref = closes[d - 1]               # prices began after the entry (HYPE before its Binance listing)
            if borrow_apr and closes and p_ref and d in closes:
                bc = (borrow_base + max(0.0, closes[d] / p_ref - 1.0)) * borrow_apr / 365.0
                cost += bc
                st['borrow'] += bc
            if theta and closes and p_ref and d in closes:
                if lev and highs and d in highs and highs[d] / p_ref - 1.0 > 1.0 / lev - 0.01:
                    st['liq_near'] += 1
                g = closes[d] / p_ref - 1.0
                if abs(g) > theta:
                    cost += abs(g) * (spot_cost + perp_cost[venue])
                    st['rebalances'] += 1
                    p_ref = closes[d]
            r = (fund + mtm + ext - cost) / K
            st['funding'] += fund
            st['basis'] += mtm
            st['extra'] += ext
            st['days_in'] += 1
            st['neg_funding_days_in'] += 1 if fund < 0 else 0
            ex.append(r - b / 365.0)
        else:
            ex.append(-cost / K)
        st['costs'] += cost
        inpos.append(pos)
    return ex, inpos, st


RULES_B = [{'name': 'always', 'kind': 'always'}] + [
    {'name': 'trail%dd_x%dpp' % (k, round(100 * x)), 'kind': 'thr', 'k': k, 'x': x, 'h': 0.02}
    for k in (7, 30) for x in (0.0, 0.02, 0.05)]
CAPITAL_B = {'collateral': (1.0, None), 'cash3x': (4.0 / 3.0, 3.0), 'cash5x': (1.2, 5.0)}
SPLIT_B = '2024-07-01'


def carry_inputs(raw, asset):
    """Daily funding, premium and price for each venue that lists the asset; days are the venue's own span."""
    out = {}
    bn = load_bn_funding(raw, asset)
    if bn:
        f, n = daily_sums([(t, r) for t, r in bn])
        out['binance'] = {'f': f, 'n': n, 'p': bn_daily_premium(raw, asset)}
    hl = load_hl_funding(raw, asset)
    if hl:
        f, n = daily_sums([(t, r) for t, r, _ in hl])
        out['hl'] = {'f': f, 'n': n, 'p': hl_daily_premium(hl)}
    closes, highs = bn_daily_px(raw, asset)
    fn = Path(raw) / 'hl' / ('candles_1d_%s.json.gz' % asset)
    if fn.exists():                         # Hyperliquid's own daily bars fill the days Binance did not list
        for c in read_gz(fn):
            d = int(c['t']) // DAY_MS
            closes.setdefault(d, float(c['c']))
            highs.setdefault(d, float(c['h']))
    return out, closes, highs


def span(f, d_end):
    """Contiguous days from the first day with funding to d_end (exclusive), dropping a partial last day."""
    if not f:
        return []
    return list(range(min(f) + 1, min(max(f), d_end - 1) + 1))


HL_BORROW_APR = 0.055     # Hyperliquid portfolio margin: stablecoin borrow 5% APY at utilisation below 80%, +10% kept
HL_PM_MARGIN = 0.10       # the short's margin borrowed against the spot (10x on the perp, the docs' own example)


def run_carry_block(name, days, f_by, p_by, spot_cost, perp_cost, cap_name, bench_fn, schedule, extra, closes, highs,
                    split_day):
    K, lev = CAPITAL_B[cap_name]
    hl_pm = cap_name == 'collateral' and set(f_by) == {'hl'}
    series, stats = {}, {}
    for r in RULES_B:
        ex, inpos, st = simulate_carry(days, f_by, p_by, r, spot_cost, perp_cost, K, bench_fn, schedule=schedule,
                                       extra=extra, closes=closes if (lev or hl_pm) else None,
                                       highs=highs if lev else None, lev=lev, theta=0.25 if hl_pm else None,
                                       borrow_apr=HL_BORROW_APR if hl_pm else 0.0,
                                       borrow_base=HL_PM_MARGIN if hl_pm else 0.0)
        series[r['name']] = ex
        stats[r['name']] = st
    frac = (split_day - days[0]) / len(days)
    ctt = B.choose_then_test(series, frac=frac, periods_per_year=365)
    c = B.cutoff_index(len(days), frac)
    ch = ctt['chosen']
    test = series[ch][c:]
    by_year = {}
    for i, d in enumerate(days):
        by_year.setdefault(str(year_of_day(d)), []).append(series[ch][i])
    always = series['always']
    last = days[-1]

    def window(ser, d_from):
        xs = [v for d, v in zip(days, ser) if d >= d_from]
        return (sum(xs) / len(xs) * 365.0) if xs else None
    recent = {}
    for label, d_from in (('last_365d', last - 364), ('last_90d', last - 89), ('ytd_2026', day_ms('2026-01-01') // DAY_MS)):
        recent[label] = {'chosen': window(series[ch], d_from), 'always': window(always, d_from)}
    always_by_year = {}
    for i, d in enumerate(days):
        always_by_year.setdefault(str(year_of_day(d)), []).append(always[i])
    f0 = f_by[(schedule.get(last) if schedule else None) or next(iter(f_by))]
    return {
        'recent_ann_excess': recent,
        'always_by_year_ann_excess': {y: sum(v) / len(v) * 365.0 for y, v in always_by_year.items()},
        'signal_now': {'trail7': trailing_apr(f0, last + 1, 7), 'trail30': trailing_apr(f0, last + 1, 30),
                       'trail90': trailing_apr(f0, last + 1, 90)},
        'name': name, 'capital': cap_name, 'first_day': ymd(days[0] * DAY_MS), 'last_day': ymd(days[-1] * DAY_MS),
        'split_day': ymd(days[c] * DAY_MS), 'days': len(days),
        'protocol': {k: ctt[k] for k in ('chosen', 'n_variants', 'in_sample', 'out_of_sample', 'oos_rank', 'oos_t',
                                         'oos_p', 'deflated_sharpe_in_sample', 'bh_survivors_full_sample')},
        'test_block_bootstrap_mean': B.block_bootstrap(test, block=30),
        'test_concentration_top4_weeks': concentration(test),
        'chosen_by_year_ann_excess': {y: sum(v) / len(v) * 365.0 for y, v in by_year.items()},
        'always_test': B.perf(always[c:], 365), 'always_train': B.perf(always[:c], 365),
        'always_test_nw_t': B.newey_west_t(always[c:], lags=30)[0],
        'variants_test_ann_excess': {k: B.perf(v[c:], 365).get('ann_return') for k, v in series.items()},
        'variants_train_ann_excess': {k: B.perf(v[:c], 365).get('ann_return') for k, v in series.items()},
        'bookkeeping_chosen': stats[ch], 'bookkeeping_always': stats['always'],
        '_series': series, '_days': days, '_c': c,
    }


def analyze_carry(raw, nav):
    const, hist = bench_of('const', nav), bench_of('hist', nav)
    d_end = int(time.time() * 1000) // DAY_MS
    split_day = day_ms(SPLIT_B) // DAY_MS
    blocks, raw_series = [], {}
    for asset in ASSETS_B:
        V, closes, highs = carry_inputs(raw, asset)
        variants = []
        for venue in ('binance', 'hl'):
            if venue in V:
                variants.append((venue, {venue: V[venue]['f']}, {venue: V[venue]['p']}, None))
        if 'binance' in V and 'hl' in V:
            both0 = max(min(V['binance']['f']), min(V['hl']['f'])) + 31
            fb = {v: V[v]['f'] for v in ('binance', 'hl')}
            pb = {v: V[v]['p'] for v in ('binance', 'hl')}
            variants.append(('best', fb, pb, both0))
        for venue, f_by, p_by, start in variants:
            if venue == 'best':
                days = list(range(start, d_end - 1))
                sched = best_venue_schedule(f_by, days)
                caps = ('cash3x',)
            else:
                days = span(f_by[venue], d_end)
                sched = None
                caps = ('collateral', 'cash3x', 'cash5x')
            if len(days) < 120:
                continue
            sp = split_day if (split_day - days[0]) >= 365 else days[0] + len(days) // 2
            spot_c = venue_costs('binance', asset)[0]
            perp_c = {v: venue_costs(v, asset)[1] for v in f_by}
            for cap in caps:
                for bmode, bfn in (('const', const), ('hist', hist)):
                    if bmode == 'hist' and cap != caps[0]:
                        continue
                    blk = run_carry_block('%s:%s' % (venue, asset), days, f_by, p_by, spot_c, perp_c, cap, bfn, sched,
                                          None, closes, highs, sp)
                    blk.update({'venue': venue, 'asset': asset, 'bench': bmode})
                    if bmode == 'const':
                        raw_series['%s:%s:%s' % (venue, asset, cap)] = (blk['_days'], blk['_series'], blk['_c'])
                    blocks.append(blk)
        # ETH with wstETH as the spot leg: the staking yield accrues on the spot notional while held
        if asset == 'ETH' and nav.get('wsteth'):
            for venue in ('binance', 'hl'):
                if venue not in V:
                    continue
                days = [d for d in span(V[venue]['f'], d_end) if d in nav['wsteth']]
                if len(days) < 120:
                    continue
                days = list(range(days[0], days[-1] + 1))
                sp = split_day if (split_day - days[0]) >= 365 else days[0] + len(days) // 2
                spot_c = (FEE['bn_spot'] + 3.0) / 1e4          # wstETH bought on chain: ~3bp pool fee + impact
                perp_c = {venue: venue_costs(venue, 'ETH')[1]}
                for cap in ('cash3x',):
                    blk = run_carry_block('%s:wstETH' % venue, days, {venue: V[venue]['f']}, {venue: V[venue]['p']},
                                          spot_c, perp_c, cap, const, None, nav['wsteth'], closes, highs, sp)
                    blk.update({'venue': venue, 'asset': 'wstETH', 'bench': 'const'})
                    blocks.append(blk)
    # multiple testing over every (venue, asset, capital) block's seven rules, full sample, constant SSR
    names, pv = [], []
    for k, (days, series, c) in raw_series.items():
        for rn, ser in series.items():
            names.append('%s:%s' % (k, rn))
            pv.append(B.newey_west_t(ser, lags=30)[1])
    rej, adj = B.bh(pv, q=0.10)
    for blk in blocks:
        blk.pop('_series', None)
        blk.pop('_days', None)
        blk.pop('_c', None)
    return {'blocks': blocks, 'variants_tried': len(names),
            'bh_survivors_q10': [n for n, r in zip(names, rej) if r],
            'rules': RULES_B, 'capital_models': CAPITAL_B, 'split': SPLIT_B}, raw_series


def funding_facts(raw, nav):
    """Plain facts: funding by venue, asset and year (annualised mean daily sum) and sUSDe's realised yield."""
    out = {}
    for asset in ASSETS_B:
        V, _, _ = carry_inputs(raw, asset)
        for venue, v in V.items():
            by = {}
            for d, x in v['f'].items():
                by.setdefault(str(year_of_day(d)), []).append(x)
            out['%s:%s' % (venue, asset)] = {
                y: {'ann': sum(xs) / len(xs) * 365.0, 'days': len(xs),
                    'neg_days_share': sum(1 for x in xs if x < 0) / len(xs)} for y, xs in sorted(by.items())}
    sus = {}
    for d, x in nav['susde'].items():
        sus.setdefault(str(year_of_day(d)), []).append(x)
    out['susde'] = {y: {'ann': sum(xs) / len(xs) * 365.0, 'days': len(xs)} for y, xs in sorted(sus.items())}
    sav = {}
    for d, x in nav['savings_path'].items():
        sav.setdefault(str(year_of_day(d)), []).append(x)
    out['savings_paid'] = {y: {'ann': sum(xs) / len(xs), 'days': len(xs)} for y, xs in sorted(sav.items())}
    wst = {}
    for d, x in nav['wsteth'].items():
        wst.setdefault(str(year_of_day(d)), []).append(x)
    out['wsteth_staking'] = {y: {'ann': sum(xs) / len(xs) * 365.0, 'days': len(xs)} for y, xs in sorted(wst.items())}
    split = day_ms(SPLIT_B) // DAY_MS
    t = [x for d, x in nav['susde'].items() if d >= split]
    out['susde_test_ann'] = sum(t) / len(t) * 365.0 if t else None
    t = [x for d, x in nav['savings_path'].items() if d >= split]
    out['savings_paid_test_ann'] = sum(t) / len(t) if t else None
    return out


# ============================================================================================== (c) Boros

BOROS_TOKEN = {1: 'BTC', 2: 'ETH', 3: 'USDT', 4: 'BNB', 5: 'HYPE'}
SPLIT_C = '2026-03-01'


def boros_load(raw):
    rb = Path(raw) / 'boros'
    mk = json.loads((rb / 'markets.json').read_text())['markets']
    out = []
    for m in mk:
        fn = rb / ('ind_%d.json.gz' % m['marketId'])
        if not fn.exists():
            continue
        d = read_gz(fn)
        rows = d.get('results') or []
        md = m.get('metadata') or {}
        cfg = m.get('config') or {}
        ext = m.get('extConfig') or {}
        if md.get('isUiWhitelisted') is False or md.get('isSpreadMarket'):
            continue                    # dev/test markets and spread markets are not the fixed-for-floating swap
        out.append({
            'id': m['marketId'], 'symbol': m['imData']['symbol'], 'maturity': int(m['imData']['maturity']),
            'asset': boros_asset(m), 'venue': boros_venue(m), 'stream': boros_stream_key(m),
            'token': BOROS_TOKEN.get(m.get('tokenId'), str(m.get('tokenId'))),
            'taker_fee': fnum(cfg.get('takerFee'), 5e14) / 1e18, 'settle_fee': fnum(ext.get('settleFeeRate'), 1e15) / 1e18,
            'k_im': fnum(cfg.get('kIM'), 6.45e17) / 1e18, 'floor': fnum(m['imData'].get('marginFloor'), 0.08),
            't_thresh': fnum(cfg.get('tThresh'), 432000),
            'u': {int(r['ts']) // DAY_S: float(r['u']) for r in rows if r.get('u') is not None},
            'mr': {int(r['ts']) // DAY_S: float(r['mr']) for r in rows if r.get('mr') is not None},
            'data': m.get('data') or {}, 'state': m.get('state')})
    return out


def boros_asset(m):
    md = m.get('metadata') or {}
    return md.get('underlyingSymbol') or md.get('assetSymbol') or m['imData']['symbol'].split('-')[1]


def boros_venue(m):
    pl = m.get('platform') or {}
    md = m.get('metadata') or {}
    return (pl.get('name') or md.get('platformName') or m['imData']['symbol'].split('-')[0]).lower()


def boros_stream_key(m):
    """The funding stream a market settles against (`metadata.fundingRateSymbol`, e.g. 'hyperliquid-eth',
    'BTCUSDT'), qualified by venue: several maturities share one stream and report the same daily `u`."""
    md = m.get('metadata') or {}
    return '%s:%s' % (boros_venue(m), md.get('fundingRateSymbol') or boros_asset(m))


def boros_streams(markets):
    """One daily floating series per funding stream: every market on the same stream reports the same `u`."""
    s = {}
    for m in markets:
        for d, u in m['u'].items():
            s.setdefault(m['stream'], {})[d] = u
    return s


def boros_trades(markets, streams, now_day, min_tau=7, half_spread=0.0025):
    """Every market day with a mark rate: implied vs the floating actually paid until maturity, receive-fixed P&L."""
    out = []
    for m in markets:
        T = m['maturity'] // DAY_S
        st = streams.get(m['stream'], {})
        for d, imp in sorted(m['mr'].items()):
            tau = T - d
            if tau < min_tau or T > now_day:
                continue
            days = [k for k in range(d, T)]
            got = [st[k] for k in days if k in st]
            if len(got) < 0.9 * len(days):
                continue
            realized = sum(got) / len(got)
            tr7 = [st[k] for k in range(d - 7, d) if k in st]
            trail = sum(tr7) / len(tr7) if len(tr7) >= 5 else None
            fee_apr = m['taker_fee'] + m['settle_fee'] + half_spread
            out.append({'market': m['id'], 'symbol': m['symbol'], 'asset': m['asset'], 'venue': m['venue'],
                        'day': d, 'tau': tau, 'implied': imp, 'realized': realized, 'trail7': trail,
                        'spread': imp - realized, 'fee_apr': fee_apr,
                        'rf_pnl': (imp - realized - fee_apr) * tau / 365.0,
                        'pf_pnl': (realized - imp - fee_apr) * tau / 365.0,
                        'im_per_notional': max(abs(imp), m['floor']) * m['k_im'] * max(tau * DAY_S, m['t_thresh']) / (365 * DAY_S)})
    return out


def by_day_mean(trades, key):
    by = {}
    for t in trades:
        by.setdefault(t['day'], []).append(t[key])
    return [statistics.fmean(v) for _, v in sorted(by.items())]


def boros_rule(trades, side, X):
    """Receive fixed ('rf') when implied - trailing-7d floating >= X; pay fixed ('pf') when <= -X."""
    if side == 'rf':
        return [t for t in trades if t['trail7'] is not None and t['implied'] - t['trail7'] >= X]
    return [t for t in trades if t['trail7'] is not None and t['implied'] - t['trail7'] <= -X]


def analyze_boros(raw, now_day=None):
    markets = boros_load(raw)
    now_day = now_day or int(time.time()) // DAY_S
    streams = boros_streams(markets)
    trades = boros_trades(markets, streams, now_day)
    crypto = {'BTC', 'ETH', 'SOL', 'HYPE', 'BNB', 'XRP'}
    split = day_ms(SPLIT_C) // DAY_MS
    res = {'markets': len(markets), 'matured_with_history': len({t['market'] for t in trades}),
           'market_days': len(trades), 'split': SPLIT_C}
    groups = {}
    for t in trades:
        cls = 'crypto' if t['asset'] in crypto else 'tradfi'
        for g in ('all', cls, '%s:%s' % (t['venue'], t['asset'])):
            groups.setdefault(g, []).append(t)
    bias = {}
    for g, ts in sorted(groups.items()):
        sp = by_day_mean(ts, 'spread')
        bias[g] = {'market_days': len(ts), 'markets': len({t['market'] for t in ts}),
                   'mean_spread': statistics.fmean(t['spread'] for t in ts),
                   'mean_spread_by_day': statistics.fmean(sp) if sp else None,
                   'nw_t_by_day': B.newey_west_t(sp, lags=30)[0] if len(sp) > 10 else None,
                   'share_implied_above': sum(1 for t in ts if t['spread'] > 0) / len(ts),
                   'mean_implied': statistics.fmean(t['implied'] for t in ts),
                   'mean_realized': statistics.fmean(t['realized'] for t in ts)}
    res['bias'] = bias
    # protocol: side x X chosen on trades that matured before the split, tested on trades entered after it
    train = [t for t in trades if t['day'] + t['tau'] <= split]
    test = [t for t in trades if t['day'] >= split]
    rules = {}
    for side in ('rf', 'pf'):
        for X in (0.0, 0.02, 0.05, 0.10):
            name = '%s_X%dpp' % (side, round(100 * X))
            key = '%s_pnl' % side
            tr_in, tr_out = boros_rule(train, side, X), boros_rule(test, side, X)
            def apr(ts):
                return (sum(t[key] for t in ts) / sum(t['tau'] / 365.0 for t in ts)) if ts else None
            rules[name] = {'train_n': len(tr_in), 'train_apr_notional': apr(tr_in),
                           'train_t_by_day': B.newey_west_t(by_day_mean(tr_in, key), lags=30)[0] if len(tr_in) > 20 else None,
                           'test_n': len(tr_out), 'test_apr_notional': apr(tr_out),
                           'test_t_by_day': B.newey_west_t(by_day_mean(tr_out, key), lags=30)[0] if len(tr_out) > 20 else None,
                           'test_hit': (sum(1 for t in tr_out if t[key] > 0) / len(tr_out)) if tr_out else None,
                           'test_mean_im': statistics.fmean(t['im_per_notional'] for t in tr_out) if tr_out else None}
    ok = {k: v for k, v in rules.items() if v['train_n'] >= 30 and v['train_t_by_day'] is not None}
    chosen = max(ok, key=lambda k: ok[k]['train_t_by_day']) if ok else None
    pv = []
    for k, v in rules.items():
        t = v['train_t_by_day']
        pv.append(None if t is None else 2 * (1 - statistics.NormalDist().cdf(abs(t))))
    rej, _ = B.bh(pv, q=0.10)
    res['rules'] = rules
    res['chosen'] = chosen
    res['bh_survivors_train'] = [k for k, r in zip(rules, rej) if r]
    # same split on the crypto subset only (the TradFi feeds are a different market)
    ct = [t for t in trades if t['asset'] in crypto]
    res['crypto_rules'] = {}
    for side in ('rf', 'pf'):
        for X in (0.0, 0.02, 0.05):
            name = '%s_X%dpp' % (side, round(100 * X))
            key = '%s_pnl' % side
            tr_in = boros_rule([t for t in ct if t['day'] + t['tau'] <= split], side, X)
            tr_out = boros_rule([t for t in ct if t['day'] >= split], side, X)
            res['crypto_rules'][name] = {
                'train_n': len(tr_in), 'test_n': len(tr_out),
                'train_apr_notional': (sum(t[key] for t in tr_in) / sum(t['tau'] / 365.0 for t in tr_in)) if tr_in else None,
                'test_apr_notional': (sum(t[key] for t in tr_out) / sum(t['tau'] / 365.0 for t in tr_out)) if tr_out else None,
                'test_t_by_day': B.newey_west_t(by_day_mean(tr_out, key), lags=30)[0] if len(tr_out) > 20 else None}
    # the live term structure: implied against trailing realised for markets still trading
    live = []
    for m in markets:
        if m['maturity'] // DAY_S <= now_day:
            continue
        st = streams.get(m['stream'], {})
        tr7 = [st[k] for k in range(now_day - 7, now_day) if k in st]
        tr30 = [st[k] for k in range(now_day - 30, now_day) if k in st]
        da = m['data']
        live.append({'id': m['id'], 'symbol': m['symbol'], 'token': m['token'],
                     'days_to_maturity': m['maturity'] // DAY_S - now_day, 'mark_apr': da.get('markApr'),
                     'best_bid': da.get('bestBid'), 'best_ask': da.get('bestAsk'),
                     'floating_apr_now': da.get('floatingApr'),
                     'trail7': sum(tr7) / len(tr7) if tr7 else None, 'trail30': sum(tr30) / len(tr30) if tr30 else None,
                     'oi_units': da.get('notionalOI'), 'volume24h_units': da.get('volume24h'),
                     'asset_px': da.get('assetMarkPrice')})
    res['live'] = sorted(live, key=lambda r: (r['symbol'].split('-')[1], r['days_to_maturity']))
    res['_trades'] = trades
    return res


# ============================================================================================== (d) volatility premium

def realized_vol_forward(closes, t0_ms, days=30):
    """Annualised realised volatility of hourly log returns over (t0, t0 + days], zero-mean; None if < 90% covered."""
    pts = [(t, c) for t, c in closes if t0_ms <= t <= t0_ms + days * DAY_MS]
    if len(pts) < 0.9 * days * 24:
        return None
    r = [math.log(pts[i][1] / pts[i - 1][1]) for i in range(1, len(pts)) if pts[i][0] - pts[i - 1][0] == HOUR_MS]
    if len(r) < 0.9 * days * 24:
        return None
    return math.sqrt(sum(x * x for x in r) / len(r) * 8760.0)


def analyze_vrp(raw):
    res = {}
    for asset in ('BTC', 'ETH'):
        dv = read_gz(Path(raw) / 'deribit' / ('dvol_%s.json.gz' % asset))
        sp = read_gz(Path(raw) / 'binance' / ('spot1h_%sUSDT.json.gz' % asset))
        closes = sorted((int(t) + HOUR_MS, float(c)) for t, c in sp)
        times = [t for t, _ in closes]
        rows = []
        for r in dv:
            t_close = int(r[0]) + DAY_MS
            if t_close + 30 * DAY_MS > times[-1]:
                continue
            i0 = bisect.bisect_left(times, t_close)
            i1 = bisect.bisect_right(times, t_close + 30 * DAY_MS)
            rv = realized_vol_forward(closes[i0:i1], t_close)
            if rv is None:
                continue
            iv = float(r[4]) / 100.0
            rows.append({'day': t_close // DAY_MS, 'iv': iv, 'rv': rv, 'spread': iv - rv, 'var_spread': iv * iv - rv * rv})
        by = {}
        for x in rows:
            by.setdefault(str(year_of_day(x['day'])), []).append(x)
        years = {}
        for y, xs in sorted(by.items()):
            s = [x['spread'] for x in xs]
            years[y] = {'days': len(xs), 'mean_iv': statistics.fmean(x['iv'] for x in xs),
                        'mean_rv': statistics.fmean(x['rv'] for x in xs), 'mean_spread': statistics.fmean(s),
                        'median_spread': statistics.median(s), 'share_iv_above': sum(1 for v in s if v > 0) / len(s),
                        'p5_spread': pctl(s, 0.05), 'p1_spread': pctl(s, 0.01), 'min_spread': min(s),
                        'mean_var_spread': statistics.fmean(x['var_spread'] for x in xs)}
        s = [x['spread'] for x in rows]
        worst = sorted(rows, key=lambda x: x['spread'])[:5]
        res[asset] = {'days': len(rows), 'first': rows and ymd(rows[0]['day'] * DAY_MS),
                      'last': rows and ymd(rows[-1]['day'] * DAY_MS), 'by_year': years,
                      'all': {'mean_spread': statistics.fmean(s), 'median_spread': statistics.median(s),
                              'share_iv_above': sum(1 for v in s if v > 0) / len(s), 'p5': pctl(s, 0.05),
                              'p1': pctl(s, 0.01), 'min': min(s), 'skew_kurt': B.moments(s),
                              'nw_t_mean_spread': B.newey_west_t(s, lags=30)[0],
                              'mean_var_spread': statistics.fmean(x['var_spread'] for x in rows)},
                      'worst_windows': [{'start': ymd(x['day'] * DAY_MS), 'iv': x['iv'], 'rv': x['rv']} for x in worst]}
    return res


# ============================================================================================== capacity

def depth_usd(levels, mid, bp, px_i=0, qty_i=1, qty_in_usd=False):
    """USD resting within `bp` of mid on one side of a book given as [[px, qty], ...] or [{'px','sz'}...]."""
    tot = 0.0
    for lv in levels or []:
        if isinstance(lv, dict):
            px, q = float(lv['px']), float(lv['sz'])
        else:
            px, q = float(lv[px_i]), float(lv[qty_i])
        if abs(px / mid - 1.0) * 1e4 <= bp:
            tot += q if qty_in_usd else px * q
    return tot


def analyze_capacity(raw):
    fn = Path(raw) / 'books' / 'snapshot.json.gz'
    if not fn.exists():
        return {'error': 'no books snapshot'}
    S = read_gz(fn)
    out = {'at': S.get('at'), 'binance': {}, 'deribit': {}, 'hl': {}, 'boros': {}}
    for sym, v in (S.get('binance') or {}).items():
        dpt = v.get('depth') or {}
        bids, asks = dpt.get('bids') or [], dpt.get('asks') or []
        if not bids or not asks:
            continue
        mid = (float(bids[0][0]) + float(asks[0][0])) / 2
        oi = fnum((v.get('oi') or {}).get('openInterest'))
        tk = v.get('ticker') or {}
        out['binance'][sym] = {'mid': mid, 'half_spread_bp': (float(asks[0][0]) / mid - 1) * 1e4,
                               'bid_10bp': depth_usd(bids, mid, 10), 'ask_10bp': depth_usd(asks, mid, 10),
                               'bid_25bp': depth_usd(bids, mid, 25), 'ask_25bp': depth_usd(asks, mid, 25),
                               'oi_usd': oi * mid if oi is not None else None,
                               'volume_24h_usd': fnum(tk.get('quoteVolume'))}
    for cur, v in (S.get('deribit') or {}).items():
        for s in v.get('summary') or []:
            name = s['instrument_name']
            bk = (v.get('books') or {}).get(name) or {}
            bids, asks = bk.get('bids') or [], bk.get('asks') or []
            row = {'oi_usd': fnum(s.get('open_interest')), 'volume_24h_usd': fnum(s.get('volume_usd')),
                   'mark': fnum(s.get('mark_price')), 'index': fnum(s.get('estimated_delivery_price'))}
            if bids and asks:
                mid = (float(bids[0][0]) + float(asks[0][0])) / 2
                row.update({'bid_10bp_usd': depth_usd(bids, mid, 10, qty_in_usd=True),
                            'ask_10bp_usd': depth_usd(asks, mid, 10, qty_in_usd=True),
                            'bid_25bp_usd': depth_usd(bids, mid, 25, qty_in_usd=True),
                            'half_spread_bp': (float(asks[0][0]) / mid - 1) * 1e4})
            out['deribit'][name] = row
    hl = S.get('hl') or {}
    meta = hl.get('meta_ctxs')
    if meta:
        uni, ctxs = meta[0]['universe'], meta[1]
        for a, c in zip(uni, ctxs):
            if a['name'] in ('BTC', 'ETH', 'SOL', 'HYPE'):
                out['hl'][a['name']] = {'oi_usd': fnum(c.get('openInterest'), 0) * fnum(c.get('markPx'), 0),
                                        'volume_24h_usd': fnum(c.get('dayNtlVlm'))}
    for k, bk in (hl.get('books') or {}).items():
        lv = bk.get('levels') or [[], []]
        if lv[0] and lv[1]:
            mid = (float(lv[0][0]['px']) + float(lv[1][0]['px'])) / 2
            out['hl'].setdefault(k, {}).update({'bid_10bp': depth_usd(lv[0], mid, 10), 'ask_10bp': depth_usd(lv[1], mid, 10),
                                                'half_spread_bp': (float(lv[1][0]['px']) / mid - 1) * 1e4})
    bo = S.get('boros') or {}
    for m in bo.get('markets') or []:
        da = m.get('data') or {}
        tok = BOROS_TOKEN.get(m.get('tokenId'))
        px = 1.0 if tok == 'USDT' else fnum(da.get('assetMarkPrice'), 0.0)
        if tok not in ('USDT',) and tok != boros_asset(m):
            px = None       # collateral token differs from the asset: price unknown here
        bk = (bo.get('books') or {}).get(m['marketId']) or {}
        long_d = boros_book_depth(bk, 'long', 0.005)
        short_d = boros_book_depth(bk, 'short', 0.005)
        out['boros'][m['imData']['symbol']] = {
            'token': tok, 'oi_units': da.get('notionalOI'),
            'oi_usd': (da.get('notionalOI') or 0) * px if px is not None else None,
            'mark_apr': da.get('markApr'), 'bid': da.get('bestBid'), 'ask': da.get('bestAsk'),
            'depth_50bp_long_units': long_d, 'depth_50bp_short_units': short_d,
            'depth_50bp_long_usd': long_d * px if (long_d is not None and px is not None) else None,
            'depth_50bp_short_usd': short_d * px if (short_d is not None and px is not None) else None,
            'days_to_maturity': (int(m['imData']['maturity']) - time.time()) / DAY_S}
    return out


CAP_OI_SHARE = 0.05


def capacity_estimates(cap, raw):
    """The sizes the book entries quote, from the live snapshot: (a) 5% of dated-futures open interest on Deribit and
    Binance (CME's is not public in this session); (b) Hyperliquid HYPE carry limited by the HL spot book (the leg
    that must sit on Hyperliquid to be collateral) built over ~2 weeks, cross-checked against perp OI."""
    out = {}
    dated = {}
    for name, v in (cap.get('deribit') or {}).items():
        if 'PERPETUAL' in name or v.get('oi_usd') is None:
            continue
        exp = name.split('-')[1]
        try:
            d = dt.datetime.strptime(exp, '%d%b%y')
        except ValueError:
            continue
        if d.month in (3, 6, 9, 12) and d.date() == last_friday(d.year, d.month):
            dated['deribit:' + name] = v['oi_usd']
    for name, v in (cap.get('binance') or {}).items():
        if '_' in name and v.get('oi_usd'):
            dated['binance:' + name] = v['oi_usd']
    out['dated_quarterly_oi_usd'] = dated
    out['dated_total_oi_usd'] = sum(dated.values())
    out['dated_capacity_usd'] = CAP_OI_SHARE * out['dated_total_oi_usd']
    fn = Path(raw) / 'books' / 'hl_coarse.json'
    coarse = json.loads(fn.read_text()) if fn.exists() else {}
    out['hl_coarse_25bp'] = coarse.get('depth')
    hl = cap.get('hl') or {}
    sp = (coarse.get('depth') or {}).get('@107') or {}
    spot_25 = min(sp.get('bid_25bp') or 0, sp.get('ask_25bp') or 0)
    out['hype'] = {'perp_oi_usd': (hl.get('HYPE') or {}).get('oi_usd'), 'perp_volume_24h_usd': (hl.get('HYPE') or {}).get('volume_24h_usd'),
                   'spot_depth_25bp_min_side_usd': spot_25,
                   'capacity_usd': 5_000_000,
                   'capacity_rule': 'about four times the HL spot book within 25bp, bought over ~2 weeks; 0.3% of perp OI; '
                                    'the per-user portfolio-margin cap (1M HYPE) does not bind'}
    btc = (coarse.get('depth') or {}).get('@142') or {}
    out['btc'] = {'perp_oi_usd': (hl.get('BTC') or {}).get('oi_usd'),
                  'spot_depth_25bp_min_side_usd': min(btc.get('bid_25bp') or 0, btc.get('ask_25bp') or 0),
                  'pm_user_cap_btc': 200}
    return out


# ============================================================================================== analyze / render

def cmd_analyze(args):
    out = Path(args.out)
    raw = out / 'raw'
    t0 = time.time()
    nav = load_navs(out)
    A = {'generated': utc(), 'ssr': SSR, 'fees_bp': FEE, 'half_spread_bp_assumed': HALF_SPREAD,
         'nav_points': nav['counts']}
    A['capacity'] = analyze_capacity(raw)
    A['capacity_estimates'] = capacity_estimates(A['capacity'], raw)
    print('capacity done', flush=True)
    A['basis'] = analyze_basis(raw, nav)
    print('basis done', flush=True)
    A['funding_facts'] = funding_facts(raw, nav)
    carry, _ = analyze_carry(raw, nav)
    A['carry'] = carry
    print('carry done', flush=True)
    bo = analyze_boros(raw)
    trades = bo.pop('_trades')
    write_gz(out / 'boros_trades.json.gz', trades)
    A['boros'] = bo
    print('boros done', flush=True)
    A['vrp'] = analyze_vrp(raw)
    A['seconds'] = round(time.time() - t0, 1)
    write_json(out / 'analysis.json', A)
    print('analysis.json written in %.0fs' % A['seconds'])
    return 0


def pct(x, d=1):
    return '—' if x is None else ('%+.' + str(d) + 'f%%') % (100 * x)


def pctu(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100 * x)


def num(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


def usd(x):
    if x is None:
        return '—'
    if abs(x) >= 1e9:
        return '$%.2fB' % (x / 1e9)
    if abs(x) >= 1e6:
        return '$%.1fM' % (x / 1e6)
    if abs(x) >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# Term carry — tables', '', 'Generated %s from `analysis.json`. Benchmark: SSR %.2f%% a year unless a column says '
         '"vs savings paid" (Maker DSR, then the SSR, as paid at the time). Excess is per year on the capital the trade '
         'ties up.' % (A['generated'], 100 * A['ssr']), '']
    F = A['funding_facts']
    years = sorted({y for k, v in F.items() if isinstance(v, dict) for y in v if y.isdigit()})
    L += ['## Funding a short perp received, by year (annualised mean of daily sums)', '',
          '| series | ' + ' | '.join(years) + ' |', '|---|' + '---:|' * len(years)]
    for k in sorted(k for k in F if ':' in k) + ['susde', 'wsteth_staking', 'savings_paid']:
        v = F.get(k) or {}
        L.append('| %s | %s |' % (k, ' | '.join(pct((v.get(y) or {}).get('ann')) for y in years)))
    L += ['', 'sUSDe realised from %s: %s a year; savings rate paid over the same days: %s.' % (
        A['carry']['split'], pctu(F.get('susde_test_ann')), pctu(F.get('savings_paid_test_ann'))), '']
    # (a)
    L += ['## (a) Dated basis: the locked yield of buy-spot / sell-the-future held to expiry', '',
          '| venue | days | span | locked excess, mean | median | share ≥ +2pp | vs savings paid, mean |',
          '|---|---:|---|---:|---:|---:|---:|']
    for k, v in sorted(A['basis'].items()):
        if 'error' in v:
            L.append('| %s | error: %s |' % (k, v['error']))
            continue
        la = v['locked_all']
        L.append('| %s (%s) | %d | %s → %s | %s | %s | %s | %s |' % (
            k, v['capital_model'], v['days_with_quotes'], v['first_day'], v['last_day'], pct(la['excess']['mean']),
            pct(la['excess']['median']), pctu(la['share_excess_ge_2pp'], 0), pct(la['excess_vs_savings_paid'].get('mean'))))
    L += ['', '### By year (front | next quarterly): mean annualised basis, mean locked excess, share of days ≥ +2pp', '',
          '| venue | year | front basis | front excess | front ≥2pp | next basis | next excess | next ≥2pp |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted(A['basis'].items()):
        for y, t in sorted((v.get('locked_by_year') or {}).items()):
            fr, nx = t.get('front') or {}, t.get('next') or {}
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                k, y, pct((fr.get('basis_apr') or {}).get('mean')), pct((fr.get('excess') or {}).get('mean')),
                pctu(fr.get('share_excess_ge_2pp'), 0), pct((nx.get('basis_apr') or {}).get('mean')),
                pct((nx.get('excess') or {}).get('mean')), pctu(nx.get('share_excess_ge_2pp'), 0)))
    L += ['', '### The rule, chosen on the first half of each venue\'s days, tested once on the rest', '',
          '| venue | split | chosen | in-sample ann excess | test ann excess | test trades | mean locked excess / trade | t (trades) | time in trade | alt capital | vs savings paid |',
          '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted(A['basis'].items()):
        if 'protocol' not in v:
            continue
        pr, ct = v['protocol'], v['chosen_test']
        L.append('| %s | %s | %s | %s | %s | %d | %s | %s | %s | %s (%s) | %s |' % (
            k, v['split_day'], pr['chosen'], pct(pr['in_sample'].get('ann_return'), 2),
            pct(pr['out_of_sample'].get('ann_return'), 2), ct['trades'], pct(ct['mean_locked_excess']),
            num(ct['t_trades']), pctu(ct['share_time_in_trade'], 0), pct(ct['ann_excess_alt_capital'], 2),
            v['alt_capital_model'], pct(ct['ann_excess_vs_savings_paid'], 2)))
    # (b)
    C = A['carry']
    L += ['', '## (b) Long spot / short perp: rules chosen before %s, tested after (daily excess over the benchmark on capital)' % C['split'], '',
          '| block | capital | bench | chosen | in-sample | test | test NW t | deflated SR (IS) | always-on test | always NW t | test bootstrap 95%% | top-4-week share |',
          '|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|']
    for b in C['blocks']:
        pr = b['protocol']
        bb = b['test_block_bootstrap_mean']
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s…%s | %s |' % (
            b['name'], b['capital'], b['bench'], pr['chosen'], pct(pr['in_sample'].get('ann_return'), 2),
            pct(pr['out_of_sample'].get('ann_return'), 2), num(pr['oos_t']), num(pr['deflated_sharpe_in_sample']),
            pct(b['always_test'].get('ann_return'), 2), num(b['always_test_nw_t']),
            pct(bb['lo'] * 365 if bb.get('lo') is not None else None, 1),
            pct(bb['hi'] * 365 if bb.get('hi') is not None else None, 1), pctu(b['test_concentration_top4_weeks'], 0)))
    L += ['', 'Variants tried: %d; BH survivors at q=0.10 (full sample, NW 30 lags): %d — %s' % (
        C['variants_tried'], len(C['bh_survivors_q10']), ', '.join(C['bh_survivors_q10'][:40]) or 'none'), '']
    L += ['### Chosen rule by calendar year (annualised excess on capital, constant SSR)', '']
    yrs = sorted({y for b in C['blocks'] for y in b['chosen_by_year_ann_excess']})
    L += ['| block | capital | chosen | ' + ' | '.join(yrs) + ' |', '|---|---|---|' + '---:|' * len(yrs)]
    for b in C['blocks']:
        if b['bench'] != 'const':
            continue
        L.append('| %s | %s | %s | %s |' % (b['name'], b['capital'], b['protocol']['chosen'], ' | '.join(
            pct(b['chosen_by_year_ann_excess'].get(y), 1) for y in yrs)))
    # (c)
    Bo = A['boros']
    L += ['', '## (c) Boros: implied fixed against the floating actually paid to maturity', '',
          '%d markets listed; %d matured with history; %d market-days scored (entry ≥ 7 days before maturity).' % (
              Bo['markets'], Bo['matured_with_history'], Bo['market_days']), '',
          '| group | markets | market-days | mean implied | mean realised | implied − realised | by-day mean | NW t (by day) | share implied above |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for g, v in sorted(Bo['bias'].items(), key=lambda kv: (-kv[1]['market_days'])):
        if v['market_days'] < 40 and g not in ('all', 'crypto', 'tradfi'):
            continue
        L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s |' % (
            g, v['markets'], v['market_days'], pct(v['mean_implied']), pct(v['mean_realized']), pct(v['mean_spread'], 2),
            pct(v['mean_spread_by_day'], 2), num(v['nw_t_by_day']), pctu(v['share_implied_above'], 0)))
    L += ['', 'Rules (receive fixed `rf` when implied − trailing-7d ≥ X; pay fixed `pf` when ≤ −X), chosen on trades that matured before %s, tested on trades entered after it. APR is on notional after the taker fee, the settlement fee and a 25bp half-spread.' % Bo['split'], '',
          '| rule | train n | train APR | train t | test n | test APR | test t | test hit | mean IM / notional |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in Bo['rules'].items():
        L.append('| %s%s | %d | %s | %s | %d | %s | %s | %s | %s |' % (
            k, ' (chosen)' if k == Bo['chosen'] else '', v['train_n'], pct(v['train_apr_notional'], 2),
            num(v['train_t_by_day']), v['test_n'], pct(v['test_apr_notional'], 2), num(v['test_t_by_day']),
            pctu(v['test_hit'], 0), pctu(v['test_mean_im'], 2)))
    L += ['', 'BH survivors (train, q=0.10): %s' % (', '.join(Bo['bh_survivors_train']) or 'none'), '',
          '### Live term structure', '', '| market | days | mark | bid | ask | trailing 7d | trailing 30d | OI (units) |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in Bo['live']:
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (
            r['symbol'], r['days_to_maturity'], pct(r['mark_apr'], 2), pct(r['best_bid'], 2), pct(r['best_ask'], 2),
            pct(r['trail7'], 2), pct(r['trail30'], 2), num(r['oi_units'], 0)))
    # (d)
    L += ['', '## (d) Volatility risk premium: DVOL against the next 30 days\' realised volatility (vol points)', '',
          '| asset | year | days | mean DVOL | mean RV | mean spread | median | share DVOL > RV | p5 | p1 | worst |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for asset, v in A['vrp'].items():
        for y, t in v['by_year'].items():
            L.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                asset, y, t['days'], pctu(t['mean_iv']), pctu(t['mean_rv']), pct(t['mean_spread']),
                pct(t['median_spread']), pctu(t['share_iv_above'], 0), pct(t['p5_spread']), pct(t['p1_spread']),
                pct(t['min_spread'])))
        a = v['all']
        L.append('| %s | all | %d | | | %s | %s | %s | %s | %s | %s |' % (
            asset, v['days'], pct(a['mean_spread']), pct(a['median_spread']), pctu(a['share_iv_above'], 0),
            pct(a['p5']), pct(a['p1']), pct(a['min'])))
    # capacity
    K = A['capacity']
    L += ['', '## Capacity inputs (live books %s)' % K.get('at'), '',
          '| venue | instrument | OI | 24h volume | bids ≤10bp | asks ≤10bp | half-spread bp |', '|---|---|---:|---:|---:|---:|---:|']
    for venue in ('binance', 'deribit', 'hl'):
        for k, v in sorted((K.get(venue) or {}).items()):
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                venue, k, usd(v.get('oi_usd')), usd(v.get('volume_24h_usd')),
                usd(v.get('bid_10bp') if 'bid_10bp' in v else v.get('bid_10bp_usd')),
                usd(v.get('ask_10bp') if 'ask_10bp' in v else v.get('ask_10bp_usd')), num(v.get('half_spread_bp'))))
    L += ['', '| Boros market | OI | mark | bid | ask | long depth ±50bp | short depth ±50bp | days |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted((K.get('boros') or {}).items(), key=lambda kv: -(kv[1].get('oi_usd') or 0)):
        L.append('| %s | %s | %s | %s | %s | %s | %s | %.0f |' % (
            k, usd(v.get('oi_usd')), pct(v.get('mark_apr'), 2), pct(v.get('bid'), 2), pct(v.get('ask'), 2),
            usd(v.get('depth_50bp_long_usd')), usd(v.get('depth_50bp_short_usd')), v.get('days_to_maturity') or 0))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('tables.md: %d lines' % len(L))
    build_manifest(out, A)
    return 0


def build_manifest(out, A):
    """manifest.json: sources, endpoints, per-part timings and counts, failures, and what analyze read from disk."""
    parts = {}
    for fn in sorted((out / 'raw').glob('manifest_*.json')):
        parts[fn.stem.replace('manifest_', '')] = json.loads(fn.read_text())
    man = {
        'study': 'term_carry', 'generated': utc(), 'analysis_generated': A.get('generated'),
        'endpoints': {
            'binance_fapi': BN_FAPI + ' /fapi/v1/continuousKlines (CURRENT_QUARTER, NEXT_QUARTER, PERPETUAL; 1d), '
                            '/fapi/v1/indexPriceKlines, /fapi/v1/fundingRate, /fapi/v1/premiumIndexKlines, /fapi/v1/klines, '
                            '/fapi/v1/depth, /fapi/v1/openInterest, /fapi/v1/ticker/24hr',
            'binance_spot': BN_SPOT + ' /api/v3/klines (1h, realised volatility), /api/v3/depth',
            'deribit': DERIBIT + 'get_tradingview_chart_data (1D bars run 08:00-08:00 UTC; expired contracts are served by '
                       'name), get_delivery_prices (08:00 index, 100 a page), get_index_chart_data, '
                       'get_volatility_index_data (DVOL), get_book_summary_by_currency, get_order_book',
            'yahoo': YAHOO + 'BTC=F, ETH=F, BTC-USD, ETH-USD (1h, range 730d; UA Mozilla/5.0)',
            'boros': BOROS + ' /v1/markets (all, matured included), /v1/indicators (u, mr; 1d), /v1/markets/ohlcv, '
                     '/v1/markets/order-book, /v1/funding-rate/all-funding-rate-symbols, /v1/assets; docs at /apis/docs',
            'hyperliquid': 'https://api.hyperliquid.xyz/info fundingHistory (2023-05-12..2025-10-01, interval 5 s), '
                           'candleSnapshot (HYPE 1d), l2Book (incl. nSigFigs 4), metaAndAssetCtxs',
            'ethereum_archive': 'public endpoints in scripts/drpc.py: sUSDe convertToAssets(1e18), Pot.dsr(), '
                                'wstETH.stEthPerToken() at estimated blocks (block timestamps read back)'},
        'reused_from_disk': {
            'hl_funding_since_2025_10_01': str(PERPS_STORE / 'funding'),
            'navs_daily_since_2024_09_26': str(NAV_STATE),
        },
        'parts': parts,
        'failures': {k: (v.get('error') or (v.get(k) or {}).get('failed') or (v.get(k) or {}).get('missing') or
                         (v.get(k) or {}).get('error_examples')) for k, v in parts.items()},
        'nav_points': A.get('nav_points'),
        'counts': {
            'basis_days': {k: v.get('days_with_quotes') for k, v in (A.get('basis') or {}).items()},
            'carry_blocks': len((A.get('carry') or {}).get('blocks') or []),
            'carry_variants_tried': (A.get('carry') or {}).get('variants_tried'),
            'boros_markets': (A.get('boros') or {}).get('markets'),
            'boros_market_days_scored': (A.get('boros') or {}).get('market_days'),
            'vrp_days': {k: v.get('days') for k, v in (A.get('vrp') or {}).items()},
        },
    }
    write_json(out / 'manifest.json', man)
    print('manifest.json written')


def cmd_snapshot(args):
    """Boros's live term structure (implied against trailing realised floating) appended to a JSONL file, so the
    implied-versus-realised history this study had to reconstruct accumulates from here on at the source."""
    out = Path(args.out)
    mk = boros_markets()
    now = int(time.time())
    live = [m for m in mk if int(m['imData']['maturity']) > now]
    streams = {}
    for m in live:
        k = boros_stream_key(m)
        if k in streams:
            continue
        d = boros('/v1/indicators', marketId=m['marketId'], timeFrame='1d', startTimestamp=now - 31 * DAY_S,
                  endTimestamp=now, select='u')
        streams[k] = [r['u'] for r in (d.get('results') or []) if r.get('u') is not None]
    rows = []
    for m in live:
        k = boros_stream_key(m)
        u = streams.get(k) or []
        da = m.get('data') or {}
        rows.append({'at': utc(), 'id': m['marketId'], 'symbol': m['imData']['symbol'],
                     'maturity': m['imData']['maturity'], 'mark_apr': da.get('markApr'), 'bid': da.get('bestBid'),
                     'ask': da.get('bestAsk'), 'floating_now': da.get('floatingApr'),
                     'trail7': statistics.fmean(u[-8:-1]) if len(u) >= 8 else None,
                     'trail30': statistics.fmean(u[:-1]) if len(u) >= 20 else None,
                     'oi_units': da.get('notionalOI'), 'token': BOROS_TOKEN.get(m.get('tokenId'))})
    fn = Path(args.ledger) if args.ledger else out / 'boros_snapshots.jsonl'
    with fn.open('a') as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + '\n')
    print('%d live Boros markets appended to %s' % (len(rows), fn))
    return 0


def cmd_collect(args):
    out = Path(args.out)
    (out / 'raw').mkdir(parents=True, exist_ok=True)
    parts = args.parts.split(',')
    fns = {'binance': collect_binance, 'deribit': collect_deribit, 'yahoo': collect_yahoo, 'boros': collect_boros,
           'hl': collect_hl, 'books': collect_books, 'chain': collect_chain}
    for p in parts:
        log = {'part': p, 'started': utc()}
        t0 = time.time()
        try:
            fns[p](out, log)
        except Exception as e:  # noqa: BLE001 - one source failing must not lose the others
            log['error'] = repr(e)[:400]
            print('collect %s failed: %r' % (p, e), flush=True)
        log['seconds'] = round(time.time() - t0, 1)
        write_json(out / 'raw' / ('manifest_%s.json' % p), log)
        print('collect %s done in %.0fs' % (p, log['seconds']), flush=True)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--parts', default='binance,deribit,yahoo,boros,books')
    a = sub.add_parser('analyze')
    a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    r = sub.add_parser('render')
    r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    sn = sub.add_parser('snapshot', help='append the live Boros term structure to a JSONL ledger (run daily)')
    sn.set_defaults(fn=cmd_snapshot)
    sn.add_argument('--out', required=True)
    sn.add_argument('--ledger', default=None)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
