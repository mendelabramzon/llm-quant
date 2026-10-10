#!/usr/bin/env python3
"""Gold carry: hold tokenized gold (PAXG, XAUT), short the gold perp that pays most — does it beat the savings rate
out of sample, after costs, the token's premium to spot and the capital both legs tie up, and at what size?

Why. The rent map (research/2026-10-10/rent_map) found gold and silver perps paying 6–15% a year to shorts on about
$2B of open interest across Hyperliquid (trade.xyz HIP-3 and the main-dex PAXG perp), Binance, Bybit and OKX. The
repo's history says big carries are often a schedule the market already prices (the xyz oil "carry" was the GSCI roll,
roll_carry) or the cost of two-venue capital (funding_arb). What survives has a payer with a non-price motive; here the
payer would be retail that wants 24/7 leveraged metal exposure from a crypto account. The spot leg exists on chain and
on exchanges as tokens that are 1 troy ounce each (PAXG, XAUT), so the trade is a cash-and-carry with a token hedge.

What this measures (`analyze`; every number lands in analysis.json, `render` prints tables.md and manifest.json):

  0. **What each perp's oracle tracks** (decides everything). The index/oracle of every gold and silver perp against
     (a) COMEX front futures (Yahoo GC=F/SI=F hourly) — a futures-based oracle sits on the futures, a spot one sits
     below them by the cost of carry and does not step at the futures roll; (b) the token's own spot price (the
     PAXG/XAUT perps' indices are token baskets by construction: Binance/Bybit/OKX constituents are saved); (c) the
     weekend: how much the index moves while spot gold is shut, and how much of the perp's own move it follows.
  1. **Funding per venue**, annualised by each venue's own settlement interval read from timestamps (Hyperliquid
     hourly, Binance/Bybit every 4 h, OKX every 8 h or as stamped), and the floor each venue sets.
  2. **Token premium**: PAXG and XAUT against spot gold (the XAU perps' spot index), hourly, on two venues.
  3. **Carry** of long token / short perp per venue, daily: funding received − the change of (perp premium over its
     index) + the change of (token premium over the same index) − fees and half-spreads on entry, exit, rebalancing
     and venue switches − borrow on losses when the token is the short's collateral − the savings rate on the capital
     tied up. Capital per unit of notional is explicit: 1 + m when the short is margined in cash with buffer m for a
     10% or 20% gold move on another venue; 1.0 when the token margins the short on the same venue (Binance portfolio
     margin, Bybit UTA, OKX — collateral rates read from the venues).
  4. **Rules** (pre-committed): always on; on while trailing 7- or 30-day funding beats SSR + 0/2/5pp (2pp
     hysteresis); and best-venue switching (monthly, trailing 30 days, switch costs paid). Chosen on the first half of
     each series' history, tested once on the second (backtest.choose_then_test); Newey–West t, 30-day block bootstrap,
     Benjamini–Hochberg and deflated Sharpe across all variants.
  5. **Capacity** from live books (depth within 25bp on both legs, all venues), open interest, and the marginal
     return of the next $1M; **late entry** (1 hour, 1 day); **risks**: delisted HIP-3 gold markets, weekend gaps,
     token premium tails, the funding regime against gold's own trend.

Conventions. Funding rates are per settlement, positive when longs pay, so a short receives +rate. Daily funding is the
sum of settlements in (d 00:00, d+1 00:00] UTC (term_carry.day_of). A decision at 00:00 UTC acts on the next day's
settlements. Prices for marking are the hourly close of the bar that ends at 00:00 UTC. Capital is per unit of
notional; excess is over the benchmark on that capital: SSR 3.80% a year constant (protocol), and as a check the savings
rate actually paid by calendar year (2023 2.9%, 2024 7.8%, 2025 5.5%, 2026 3.7%).

    python3 scripts/gold_carry.py collect --out research/2026-10-10/gold_carry --parts bn,by,okx,yahoo,tokens
    python3 scripts/gold_carry.py collect --out research/2026-10-10/gold_carry --parts hl      # paced >= 1.5 s/call
    python3 scripts/gold_carry.py collect --out research/2026-10-10/gold_carry --parts books   # live snapshot
    python3 scripts/gold_carry.py analyze --out research/2026-10-10/gold_carry
    python3 scripts/gold_carry.py render  --out research/2026-10-10/gold_carry

Read-only: public market-data endpoints only, no keys, no accounts. Hyperliquid through perp_rpc.Info at >= 1.5 s a
call (the IP is shared with other workers); Binance through funding_arb.Http with its weight header; Yahoo with UA
'Mozilla/5.0'.
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
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
HOUR_MS = 3_600_000
DAY_MS = 24 * HOUR_MS
SSR = 0.038
SAVINGS_BY_YEAR = {2022: 0.01, 2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}
UA = 'Mozilla/5.0'
BN_F = 'https://fapi.binance.com'
BN_S = 'https://api.binance.com'
BY = 'https://api.bybit.com'
OKX = 'https://www.okx.com'
YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart/'
GT = 'https://api.geckoterminal.com/api/v2'

# Instruments. Every perp is quoted per troy ounce (silver: per ounce) so one token hedges one unit.
BN_PERPS = ['XAUUSDT', 'XAGUSDT', 'PAXGUSDT', 'XAUTUSDT']
BN_SPOT = {'PAXGUSDT': '2022-01-01', 'XAUTUSDT': '2026-03-26'}
BY_PERPS = ['PAXGUSDT', 'XAUTUSDT', 'XAUUSDT', 'XAGUSDT']
BY_SPOT = ['XAUTUSDT']
OKX_SWAPS = ['XAU-USDT-SWAP', 'XAG-USDT-SWAP']
OKX_INDEX = ['XAU-USDT', 'XAG-USDT', 'PAXG-USDT', 'XAUT-USDT']
OKX_SPOT = {'PAXG-USDT': '2025-10-15', 'XAUT-USDT': '2024-01-01'}
HL_COINS = ['PAXG', 'xyz:GOLD', 'xyz:SILVER', 'km:GOLD', 'flx:GOLD', 'cash:GOLD', 'km:SILVER', 'flx:SILVER',
            'cash:SILVER']
HL_DELISTED_NO_DATA = ['hyna:GOLD', 'mkts:GOLD', 'vntl:GOLDJM', 'hyna:SILVER', 'mkts:SILVER', 'vntl:SILVERJM']
YAHOO_SYMS = {'GC=F': 'gold front future (COMEX)', 'SI=F': 'silver front future (COMEX)',
              'PAXG-USD': 'PAXG aggregate (CoinMarketCap via Yahoo)', 'XAUT-USD': 'XAUT aggregate'}
TOKENS_ETH = {'PAXG': '0x45804880De22913dAFE09f4980848ECE6EcbAf78', 'XAUT': '0x68749665FF8D2d112Fa859AA293F07A622782F38'}


# ---------------------------------------------------------------------------------------------- small helpers

def utc(ms=None):
    t = time.time() if ms is None else ms / 1000.0
    return dt.datetime.fromtimestamp(t, UTC).isoformat(timespec='seconds')


def ms_of(day):
    return int(dt.datetime.strptime(day[:10], '%Y-%m-%d').replace(tzinfo=UTC).timestamp() * 1000)


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


def safe(name):
    return name.replace(':', '__').replace('/', '_').replace('=', '_')


class Get:
    """Paced GET with retries; 429/418 sleep for Retry-After (or a minute) before anything else goes to that host."""

    def __init__(self, interval=0.25, timeout=40, retries=6, ua='llm-quant-research/1.0'):
        self.interval, self.timeout, self.retries, self.ua = interval, timeout, retries, ua
        self.next_at = 0.0
        self.n = self.errors = self.throttled = 0

    def __call__(self, url, params=None):
        if params:
            url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        last = None
        for a in range(self.retries):
            now = time.monotonic()
            if self.next_at > now:
                time.sleep(self.next_at - now)
            self.next_at = time.monotonic() + self.interval
            self.n += 1
            try:
                req = urllib.request.Request(url, headers={'User-Agent': self.ua, 'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                    return json.loads(body.decode())
            except urllib.error.HTTPError as e:
                last = 'HTTP %s' % e.code
                if e.code in (429, 418):
                    self.throttled += 1
                    ra = fnum(e.headers.get('Retry-After'), 60.0) if e.headers else 60.0
                    self.next_at = time.monotonic() + max(2.0, min(ra, 120.0))
                    continue
                if e.code in (500, 502, 503, 504):
                    self.errors += 1
                    time.sleep(min(10.0, 0.5 * 2 ** a))
                    continue
                self.errors += 1
                try:
                    return {'_http_error': e.code, '_body': e.read().decode()[:300]}
                except Exception:  # noqa: BLE001
                    return {'_http_error': e.code}
            except Exception as e:  # noqa: BLE001 - transport errors are retried
                last = repr(e)[:160]
                self.errors += 1
                time.sleep(min(10.0, 0.5 * 2 ** a))
        return {'_error': last}

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


# ---------------------------------------------------------------------------------------------- collect: Binance

def bn_klines(get, base, path, sym, start, end, key='symbol', interval='1h', limit=1000):
    """Rows [t_open, o, h, l, c, quote_volume] paged forward from start."""
    rows, s = [], start
    for _ in range(200):
        r = get(base + path, {key: sym, 'interval': interval, 'startTime': s, 'endTime': end, 'limit': limit})
        if not isinstance(r, list) or not r:
            break
        rows += [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), fnum(x[7], 0.0)] for x in r]
        if len(r) < limit:
            break
        s = int(r[-1][0]) + 1
    return sorted({r[0]: r for r in rows}.values(), key=lambda r: r[0])


def bn_funding(get, sym, start, end):
    rows, s = [], start
    for _ in range(100):
        r = get(BN_F + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': end, 'limit': 1000})
        if not isinstance(r, list) or not r:
            break
        rows += [{'t': int(x['fundingTime']), 'rate': float(x['fundingRate']), 'mark': fnum(x.get('markPrice'))}
                 for x in r]
        if len(r) < 1000:
            break
        s = int(r[-1]['fundingTime']) + 1
    return sorted({r['t']: r for r in rows}.values(), key=lambda r: r['t'])


def collect_bn(raw, refresh, log):
    get = Get(interval=0.25)
    getf = Get(interval=0.7)            # fundingRate shares a 500-per-5-minutes budget
    d = raw / 'bn'
    now = int(time.time() * 1000)
    end = now // HOUR_MS * HOUR_MS
    ex = get(BN_F + '/fapi/v1/exchangeInfo')
    syms = {s['symbol']: s for s in ex.get('symbols', []) if s['symbol'] in BN_PERPS}
    meta = {'at': utc(), 'symbols': syms,
            'fundingInfo': [f for f in (getf(BN_F + '/fapi/v1/fundingInfo') or []) if f.get('symbol') in BN_PERPS],
            'constituents': {s: get(BN_F + '/fapi/v1/constituents', {'symbol': s}) for s in BN_PERPS},
            'premiumIndex': {s: get(BN_F + '/fapi/v1/premiumIndex', {'symbol': s}) for s in BN_PERPS},
            'openInterest': {s: get(BN_F + '/fapi/v1/openInterest', {'symbol': s}) for s in BN_PERPS},
            'openInterestHist': {s: get(BN_F + '/futures/data/openInterestHist',
                                        {'symbol': s, 'period': '1d', 'limit': 30}) for s in BN_PERPS},
            'ticker24h': {s: get(BN_F + '/fapi/v1/ticker/24hr', {'symbol': s}) for s in BN_PERPS},
            'spot_ticker24h': {s: get(BN_S + '/api/v3/ticker/24hr', {'symbol': s})
                               for s in ('PAXGUSDT', 'XAUTUSDT', 'PAXGUSDC', 'XAUTUSDC')},
            'pm_collateral': [a for a in (get('https://www.binance.com/bapi/margin/v1/public/margin/portfolio/'
                                              'collateral-rate') or {}).get('data', [])
                              if a.get('asset') in ('PAXG', 'XAUT', 'BTC', 'ETH', 'USDT', 'USDC')],
            'multi_assets_index': [a.get('symbol') for a in (get(BN_F + '/fapi/v1/assetIndex') or [])
                                   if isinstance(a, dict)]}
    write_gz(d / 'meta.json.gz', meta)
    for sym in BN_PERPS:
        s0 = int(syms[sym]['onboardDate']) // HOUR_MS * HOUR_MS
        fp = d / ('funding_%s.json.gz' % sym)
        if refresh or not fp.exists():
            write_gz(fp, bn_funding(getf, sym, s0, now))
        for sub, path, key in (('klines', '/fapi/v1/klines', 'symbol'), ('premium', '/fapi/v1/premiumIndexKlines',
                                                                           'symbol'),
                               ('index', '/fapi/v1/indexPriceKlines', 'pair'), ('mark', '/fapi/v1/markPriceKlines',
                                                                               'symbol')):
            p = d / ('%s_%s.json.gz' % (sub, sym))
            if refresh or not p.exists():
                write_gz(p, bn_klines(get, BN_F, path, sym, s0, end, key=key))
        log['bn_' + sym] = {'funding': len(read_gz(fp)), 'klines': len(read_gz(d / ('klines_%s.json.gz' % sym)))}
    for sym, since in BN_SPOT.items():
        p = d / ('spot_%s.json.gz' % sym)
        if refresh or not p.exists():
            write_gz(p, bn_klines(get, BN_S, '/api/v3/klines', sym, ms_of(since), end))
        log['bn_spot_' + sym] = len(read_gz(p))
    log['bn_http'] = get.stats()
    log['bn_http_funding'] = getf.stats()


# ---------------------------------------------------------------------------------------------- collect: Bybit

def by_back(get, path, params, start, key_time=0, limit=1000):
    """Bybit's history endpoints return the newest `limit` rows inside [start, end]; page backwards on `end`."""
    rows, end = [], int(time.time() * 1000)
    for _ in range(400):
        r = get(BY + path, dict(params, start=start, end=end, limit=limit))
        lst = ((r or {}).get('result') or {}).get('list') or []
        if not lst:
            break
        rows += lst
        oldest = min(int(x[key_time]) if isinstance(x, list) else int(x[key_time]) for x in lst)
        if oldest <= start or len(lst) < limit:
            break
        end = oldest - 1
    return rows


def by_funding(get, sym, start):
    rows, end = [], int(time.time() * 1000)
    for _ in range(400):
        r = get(BY + '/v5/market/funding/history', {'category': 'linear', 'symbol': sym, 'startTime': start,
                                                     'endTime': end, 'limit': 200})
        lst = ((r or {}).get('result') or {}).get('list') or []
        if not lst:
            break
        rows += [{'t': int(x['fundingRateTimestamp']), 'rate': float(x['fundingRate'])} for x in lst]
        oldest = min(int(x['fundingRateTimestamp']) for x in lst)
        if oldest <= start or len(lst) < 200:
            break
        end = oldest - 1
    return sorted({r['t']: r for r in rows}.values(), key=lambda r: r['t'])


def collect_by(raw, refresh, log):
    get = Get(interval=0.15)
    d = raw / 'by'
    inst = {}
    for cat in ('linear', 'spot'):
        r = get(BY + '/v5/market/instruments-info', {'category': cat, 'limit': 1000})
        for x in ((r or {}).get('result') or {}).get('list') or []:
            if x['symbol'] in (BY_PERPS if cat == 'linear' else BY_SPOT + ['PAXGUSDT']):
                inst['%s:%s' % (cat, x['symbol'])] = x
    meta = {'at': utc(), 'instruments': inst,
            'tickers': {s: get(BY + '/v5/market/tickers', {'category': 'linear', 'symbol': s}) for s in BY_PERPS},
            'spot_tickers': {s: get(BY + '/v5/market/tickers', {'category': 'spot', 'symbol': s}) for s in BY_SPOT},
            'index_components': {s: get(BY + '/v5/market/index-price-components', {'indexName': s})
                                 for s in BY_PERPS},
            'collateral': {c: get(BY + '/v5/spot-margin-trade/collateral', {'currency': c}) for c in ('XAUT', 'PAXG')}}
    write_gz(d / 'meta.json.gz', meta)
    for sym in BY_PERPS:
        x = inst.get('linear:' + sym)
        if not x:
            continue
        s0 = int(x['launchTime']) // HOUR_MS * HOUR_MS
        fp = d / ('funding_%s.json.gz' % sym)
        if refresh or not fp.exists():
            write_gz(fp, by_funding(get, sym, s0))
        for sub, path in (('kline', '/v5/market/kline'), ('mark', '/v5/market/mark-price-kline'),
                          ('index', '/v5/market/index-price-kline'),
                          ('premium', '/v5/market/premium-index-price-kline')):
            p = d / ('%s_%s.json.gz' % (sub, sym))
            if refresh or not p.exists():
                rows = by_back(get, path, {'category': 'linear', 'symbol': sym, 'interval': '60'}, s0)
                rows = sorted({int(r[0]): [int(r[0])] + [float(v) for v in r[1:5]] + (
                    [float(r[6])] if len(r) > 6 else []) for r in rows}.values(), key=lambda r: r[0])
                write_gz(p, rows)
        log['by_' + sym] = {'funding': len(read_gz(fp)), 'kline': len(read_gz(d / ('kline_%s.json.gz' % sym)))}
    for sym in BY_SPOT:
        x = inst.get('spot:' + sym)
        p = d / ('spot_%s.json.gz' % sym)
        if refresh or not p.exists():
            rows = by_back(get, '/v5/market/kline', {'category': 'spot', 'symbol': sym, 'interval': '60'},
                           ms_of('2025-01-01'))
            rows = sorted({int(r[0]): [int(r[0])] + [float(v) for v in r[1:5]] + [float(r[6])]
                           for r in rows}.values(), key=lambda r: r[0])
            write_gz(p, rows)
        log['by_spot_' + sym] = len(read_gz(p))
    log['by_http'] = get.stats()


# ---------------------------------------------------------------------------------------------- collect: OKX

def okx_back(get, path, params, start, limit=100):
    """OKX history endpoints: newest first, `after` = strictly older than; page back to `start`."""
    rows, after = [], None
    for _ in range(2000):
        q = dict(params, limit=limit)
        if after:
            q['after'] = after
        r = get(OKX + path, q)
        lst = (r or {}).get('data') or []
        if not lst:
            break
        rows += lst
        oldest = min(int(x[0]) if isinstance(x, list) else int(x['fundingTime']) for x in lst)
        if oldest <= start:
            break
        after = oldest
    return rows


def collect_okx(raw, refresh, log):
    get = Get(interval=0.25)
    d = raw / 'okx'
    inst = {}
    for t in ('SWAP', 'SPOT'):
        r = get(OKX + '/api/v5/public/instruments', {'instType': t})
        for x in (r or {}).get('data') or []:
            if x['instId'] in OKX_SWAPS or x['instId'] in OKX_SPOT:
                inst[x['instId']] = x
    meta = {'at': utc(), 'instruments': inst,
            'index_components': {i: get(OKX + '/api/v5/market/index-components', {'index': i}) for i in OKX_INDEX},
            'open_interest': {i: get(OKX + '/api/v5/public/open-interest', {'instType': 'SWAP', 'instId': i})
                              for i in OKX_SWAPS},
            'tickers': {i: get(OKX + '/api/v5/market/ticker', {'instId': i}) for i in OKX_SWAPS + list(OKX_SPOT)},
            'funding_now': {i: get(OKX + '/api/v5/public/funding-rate', {'instId': i}) for i in OKX_SWAPS}}
    disc = {}
    for c in ('PAXG', 'XAUT'):
        time.sleep(2.5)                  # this endpoint's limit is tight (2 requests / 2 s)
        disc[c] = get(OKX + '/api/v5/public/discount-rate-interest-free-quota', {'ccy': c})
    meta['collateral'] = disc
    write_gz(d / 'meta.json.gz', meta)
    for i in OKX_SWAPS:
        s0 = int(inst[i]['listTime']) if i in inst else ms_of('2025-04-01')
        fp = d / ('funding_%s.json.gz' % i)
        if refresh or not fp.exists():
            rows = okx_back(get, '/api/v5/public/funding-rate-history', {'instId': i}, s0)
            rows = sorted({int(x['fundingTime']): {'t': int(x['fundingTime']), 'rate': float(x['realizedRate'] or
                                                                                             x['fundingRate'])}
                           for x in rows}.values(), key=lambda r: r['t'])
            write_gz(fp, rows)
        for sub, path, inst_id in (('candles', '/api/v5/market/history-candles', i),
                                   ('mark', '/api/v5/market/history-mark-price-candles', i),
                                   ('index', '/api/v5/market/history-index-candles', i.replace('-SWAP', ''))):
            p = d / ('%s_%s.json.gz' % (sub, i))
            if refresh or not p.exists():
                rows = okx_back(get, path, {'instId': inst_id, 'bar': '1H'}, s0)
                rows = sorted({int(r[0]): [int(r[0])] + [float(v) for v in r[1:5]] + (
                    [fnum(r[7], 0.0)] if sub == 'candles' and len(r) > 7 else []) for r in rows}.values(),
                    key=lambda r: r[0])
                write_gz(p, rows)
        log['okx_' + i] = {'funding': len(read_gz(fp)), 'index': len(read_gz(d / ('index_%s.json.gz' % i)))}
    for i, since in OKX_SPOT.items():
        p = d / ('spot_%s.json.gz' % i)
        if refresh or not p.exists():
            rows = okx_back(get, '/api/v5/market/history-candles', {'instId': i, 'bar': '1H'}, ms_of(since))
            rows = sorted({int(r[0]): [int(r[0])] + [float(v) for v in r[1:5]] + [fnum(r[7], 0.0)]
                           for r in rows}.values(), key=lambda r: r[0])
            write_gz(p, rows)
        log['okx_spot_' + i] = len(read_gz(p))
    log['okx_http'] = get.stats()


# ---------------------------------------------------------------------------------------------- collect: Hyperliquid

def collect_hl(raw, refresh, log, interval=1.5):
    from perp_rpc import Info
    from perp_history import page_funding, page_candles
    api = Info(interval=interval)
    d = raw / 'hl'
    now = int(time.time() * 1000)
    meta = {'at': utc(), 'core': api.post({'type': 'metaAndAssetCtxs'}),
            'xyz': api.post({'type': 'metaAndAssetCtxs', 'dex': 'xyz'}),
            'spot': api.post({'type': 'spotMetaAndAssetCtxs'})}
    keep = {}
    for k in ('core', 'xyz'):
        m, ctxs = meta[k]
        keep[k] = [dict(u, **c) for u, c in zip(m['universe'], ctxs)
                   if any(x in u['name'] for x in ('PAXG', 'GOLD', 'SILVER'))]
    sm, sctx = meta['spot']
    toks = {t['index']: t for t in sm['tokens'] if t['name'] in ('XAUT0', 'XAUM', 'USDC', 'USDT0', 'USDH')}
    pairs = []
    for u, c in zip(sm['universe'], sctx):
        if any(t in toks and toks[t]['name'] in ('XAUT0', 'XAUM') for t in u['tokens']):
            pairs.append(dict(u, **c, token_names=[toks.get(t, {}).get('name') for t in u['tokens']]))
    write_gz(d / 'meta.json.gz', {'at': meta['at'], 'perps': keep, 'spot_tokens': list(toks.values()),
                                  'spot_pairs': pairs})
    for c in HL_COINS:
        fp = d / ('funding_%s.json.gz' % safe(c))
        if refresh or not fp.exists():
            write_gz(fp, page_funding(api, c, ms_of('2025-01-01'), now))
        p1 = d / ('c1h_%s.json.gz' % safe(c))
        if refresh or not p1.exists():
            write_gz(p1, page_candles(api, c, now - 5000 * HOUR_MS, now, '1h'))
        pd = d / ('c1d_%s.json.gz' % safe(c))
        if refresh or not pd.exists():
            write_gz(pd, api.post({'type': 'candleSnapshot', 'req': {'coin': c, 'interval': '1d',
                                                                     'startTime': ms_of('2025-01-01'),
                                                                     'endTime': now}}))
        log['hl_' + c] = {'funding': len(read_gz(fp)), 'c1h': len(read_gz(p1)), 'c1d': len(read_gz(pd))}
    log['hl_api'] = {'requests': api.requests, 'errors': api.errors, 'throttled': api.throttled}


# ---------------------------------------------------------------------------------------------- collect: Yahoo

def yahoo(sym, params):
    url = YAHOO + urllib.parse.quote(sym) + '?' + urllib.parse.urlencode(params)
    for a in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.loads(r.read().decode())
            res = (d.get('chart') or {}).get('result') or []
            if not res:
                return {'error': (d.get('chart') or {}).get('error')}
            r0 = res[0]
            q = r0['indicators']['quote'][0]
            rows = [[int(t) * 1000, q['open'][i], q['high'][i], q['low'][i], q['close'][i], q['volume'][i]]
                    for i, t in enumerate(r0.get('timestamp') or []) if q['close'][i] is not None]
            return {'meta': {k: r0['meta'].get(k) for k in ('symbol', 'exchangeName', 'instrumentType', 'currency',
                                                            'exchangeTimezoneName', 'gmtoffset')}, 'rows': rows}
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:160]
            time.sleep(1.5 * 2 ** a)
    return {'error': last}


def collect_yahoo(raw, refresh, log):
    d = raw / 'yahoo'
    now = int(time.time())
    for sym in YAHOO_SYMS:
        for iv, params in (('1h', {'range': '730d', 'interval': '1h'}),
                           ('1d', {'period1': ms_of('2019-01-01') // 1000, 'period2': now, 'interval': '1d'})):
            p = d / ('%s_%s.json.gz' % (safe(sym), iv))
            if refresh or not p.exists():
                write_gz(p, yahoo(sym, params))
                time.sleep(1.0)
            log['yahoo_%s_%s' % (sym, iv)] = len(read_gz(p).get('rows') or [])


# ---------------------------------------------------------------------------------------------- collect: tokens

def eth_call(to, data):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [{'to': to, 'data': data},
                                                                                  'latest']}).encode()
    for url in ('https://ethereum-rpc.publicnode.com', 'https://eth.llamarpc.com', 'https://rpc.ankr.com/eth'):
        try:
            req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json',
                                                                  'User-Agent': 'llm-quant-research/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read().decode())
            if 'result' in res:
                return {'rpc': url, 'result': res['result']}
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:120]
    return {'error': last}


def collect_tokens(raw, refresh, log):
    """Token-side facts: on-chain supply and fee parameters, DEX pools (GeckoTerminal), Coinbase PAXG-USD hourly
    candles (a USD-quoted second venue for the premium check)."""
    d = raw / 'tokens'
    get = Get(interval=2.2)            # GeckoTerminal: 30 calls a minute
    out = {'at': utc()}
    sel = {'totalSupply': '0x18160ddd', 'feeRate': '0x978bbdb9', 'decimals': '0x313ce567'}
    for tok, addr in TOKENS_ETH.items():
        out[tok] = {k: eth_call(addr, v) for k, v in sel.items()}
        out[tok + '_pools'] = get(GT + '/networks/eth/tokens/%s/pools' % addr.lower(), {'page': 1})
    write_gz(d / 'onchain_pools.json.gz', out)
    cb = Get(interval=0.4)
    p = d / 'coinbase_PAXG-USD_1h.json.gz'
    if refresh or not p.exists():
        rows, end = [], int(time.time()) // 3600 * 3600
        start = ms_of('2025-12-01') // 1000
        while end > start:
            s = max(start, end - 300 * 3600)
            r = cb('https://api.exchange.coinbase.com/products/PAXG-USD/candles',
                   {'granularity': 3600, 'start': utc(s * 1000), 'end': utc(end * 1000)})
            if isinstance(r, list):
                rows += [[int(x[0]) * 1000, float(x[3]), float(x[2]), float(x[1]), float(x[4]), float(x[5])]
                         for x in r]
            end = s
        write_gz(p, sorted({r[0]: r for r in rows}.values(), key=lambda r: r[0]))
    log['coinbase_paxg_1h'] = len(read_gz(p))
    log['tokens_http'] = {'gt': get.stats(), 'coinbase': cb.stats()}


# ---------------------------------------------------------------------------------------------- collect: books

def collect_books(raw, log):
    """One live snapshot of every book that matters for capacity: the perps on all venues and the token spot books."""
    from perp_rpc import Info
    get = Get(interval=0.3)
    api = Info(interval=1.5)
    snap = {'at': utc(), 'books': {}}
    B_ = snap['books']
    for s in BN_PERPS:
        B_['bn_perp:' + s] = get(BN_F + '/fapi/v1/depth', {'symbol': s, 'limit': 1000})
    for s in ('PAXGUSDT', 'XAUTUSDT', 'PAXGUSDC', 'XAUTUSDC'):
        B_['bn_spot:' + s] = get(BN_S + '/api/v3/depth', {'symbol': s, 'limit': 5000})
    for s in BY_PERPS:
        B_['by_perp:' + s] = get(BY + '/v5/market/orderbook', {'category': 'linear', 'symbol': s, 'limit': 500})
    for s in BY_SPOT:
        B_['by_spot:' + s] = get(BY + '/v5/market/orderbook', {'category': 'spot', 'symbol': s, 'limit': 200})
    for i in OKX_SWAPS + list(OKX_SPOT):
        B_['okx:' + i] = get(OKX + '/api/v5/market/books', {'instId': i, 'sz': 400})
    B_['kraken_spot:PAXGUSD'] = get('https://api.kraken.com/0/public/Depth', {'pair': 'PAXGUSD', 'count': 500})
    B_['coinbase_spot:PAXG-USD'] = get('https://api.exchange.coinbase.com/products/PAXG-USD/book', {'level': 2})
    B_['bitfinex_spot:XAUT:USD'] = get('https://api-pub.bitfinex.com/v2/book/tXAUT:USD/P0', {'len': 100})
    B_['bitfinex_spot:XAUT:UST'] = get('https://api-pub.bitfinex.com/v2/book/tXAUT:UST/P0', {'len': 100})
    for c in ('PAXG', 'xyz:GOLD', 'xyz:SILVER'):
        B_['hl:' + c] = api.post({'type': 'l2Book', 'coin': c})
        B_['hl_coarse:' + c] = api.post({'type': 'l2Book', 'coin': c, 'nSigFigs': 4})
    try:
        hm = read_gz(raw / 'hl' / 'meta.json.gz')
        for p in hm.get('spot_pairs', []):
            B_['hl_spot:' + p['name']] = api.post({'type': 'l2Book', 'coin': p['name']})
            B_['hl_spot_meta:' + p['name']] = {'token_names': p.get('token_names'), 'markPx': p.get('markPx'),
                                               'dayNtlVlm': p.get('dayNtlVlm')}
    except FileNotFoundError:
        pass
    stamp = dt.datetime.now(UTC).strftime('%Y%m%dT%H%M')
    write_gz(raw / 'books' / ('books_%s.json.gz' % stamp), snap)
    log['books_' + stamp] = {k: (len(v) if isinstance(v, (list, dict)) else None) for k, v in B_.items()}
    log['books_http'] = get.stats()


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    parts = args.parts.split(',')
    logp = out / 'collect_log.json'
    log = json.loads(logp.read_text()) if logp.exists() else {}
    t0 = time.time()
    fns = {'bn': collect_bn, 'by': collect_by, 'okx': collect_okx, 'yahoo': collect_yahoo, 'tokens': collect_tokens}
    for p in parts:
        try:
            if p == 'hl':
                collect_hl(raw, args.refresh, log)
            elif p == 'books':
                collect_books(raw, log)
            else:
                fns[p](raw, args.refresh, log)
            log['done_' + p] = utc()
        except Exception as e:  # noqa: BLE001 - one part failing does not lose the others
            log['failed_' + p] = repr(e)[:300]
            print('part %s failed: %r' % (p, e), flush=True)
        merged = json.loads(logp.read_text()) if logp.exists() else {}   # parts may run in parallel processes
        merged.update(log)
        write_json(logp, merged)
        print('part %s done %.0fs' % (p, time.time() - t0), flush=True)


# ============================================================================================== analysis: calendars

try:
    from zoneinfo import ZoneInfo
    NY = ZoneInfo('America/New_York')
except Exception:  # noqa: BLE001 - without tz data, fixed EDT (the study's test window is mostly daylight time)
    NY = dt.timezone(dt.timedelta(hours=-4))


def spot_open(ms):
    """Is spot gold/silver (OTC London/NY, COMEX Globex) trading in the hour that starts at `ms`? Sunday 18:00 ET to
    Friday 17:00 ET with a daily 17:00–18:00 ET break (the Pyth XAU/USD schedule saved in the manifest). Exchange
    holidays are not modelled; they count as open hours here, which can only blur the weekday/weekend contrast."""
    t = dt.datetime.fromtimestamp(ms / 1000.0, NY)
    wd, h = t.weekday(), t.hour
    if wd == 5:
        return False
    if wd == 6:
        return h >= 18
    if wd == 4:
        return h < 17
    return h != 17


def day_of(ms):
    """Day index d (epoch days) whose window (d 00:00, d+1 00:00] UTC holds a settlement stamped at ms (rounded to
    the hour first: venues stamp a few milliseconds after the boundary). Same convention as term_carry."""
    h = int(round(ms / HOUR_MS)) * HOUR_MS
    return (h - 1) // DAY_MS


def daily_funding(events, t_max=None):
    """{day: sum of settlement rates} and {day: count} from [(ms, rate)]; one settlement per stamped hour (last wins);
    settlements after t_max (a delisting) are dropped."""
    by_hour = {}
    for t, r in events:
        if t_max is not None and t > t_max:
            continue
        by_hour[int(round(t / HOUR_MS))] = r
    s, n = {}, {}
    for h, r in by_hour.items():
        d = day_of(h * HOUR_MS)
        s[d] = s.get(d, 0.0) + r
        n[d] = n.get(d, 0) + 1
    return s, n


def settlement_hours(events):
    """The venue's settlement interval in hours, read from the timestamps (median spacing)."""
    ts = sorted({int(round(t / HOUR_MS)) for t, _ in events})
    gaps = [b - a for a, b in zip(ts, ts[1:]) if b > a]
    return statistics.median(gaps) if gaps else None


def funding_apr(events, t0=None, t1=None):
    """Annualised funding a short receives over [t0, t1): the sum of settlements divided by the elapsed years. This is
    independent of the venue's convention (hourly on Hyperliquid, 4 h on Binance/Bybit, 8 h on OKX) because it adds
    what was actually paid; `apr_per_settlement` is the same thing from the mean rate and the interval."""
    ev = [(t, r) for t, r in events if (t0 is None or t >= t0) and (t1 is None or t < t1)]
    if len(ev) < 2:
        return None
    h = settlement_hours(ev)
    a = ev[0][0] if t0 is None else t0
    b = ev[-1][0] + h * HOUR_MS if t1 is None else t1
    years = (b - a) / (365.0 * DAY_MS)
    return sum(r for _, r in ev) / years if years > 0 else None


def apr_per_settlement(mean_rate, hours):
    return mean_rate * 8760.0 / hours


def trailing_apr(f, d, k, min_frac=0.8):
    """Mean daily funding over the k days strictly before d, x365 (None when fewer than min_frac of them exist).
    A decision at d 00:00 can only use days that ended by then: days d-k .. d-1."""
    vals = [f[d - i] for i in range(1, k + 1) if (d - i) in f]
    if len(vals) < max(1, int(math.ceil(min_frac * k))):
        return None
    return sum(vals) / len(vals) * 365.0


def bench_const(d):
    return SSR


def bench_hist(d):
    y = dt.datetime.fromtimestamp(d * 86400, UTC).year
    return SAVINGS_BY_YEAR.get(y, SSR)


# ============================================================================================== analysis: carry math

def day_return(F_prev, F, b_prev, b, f):
    """Return on one unit of notional over one day for long token / short perp in equal ounces.

    With b = T/F - 1 (token over perp), the fixed-quantity P&L q[(T - T_prev) - (F - F_prev)] equals
    q[F b - F_prev b_prev]; per unit of the day's opening notional q F_prev that is (F/F_prev) b - b_prev. The gold
    move cancels; what is left is the change of the token-minus-perp basis (the token's premium to the perp's index
    minus the perp's premium to it) plus the funding the short received."""
    return (F / F_prev) * b - b_prev + f


def entry_cost(cost_token, cost_perp):
    """One side of both legs, as a fraction of notional (fee + half-spread each)."""
    return cost_token + cost_perp


CAPITAL = {
    # name: (gold move the short must survive without a top-up, rebalance trigger as a share of that move)
    'cash10': (0.10, 0.5),
    'cash20': (0.20, 0.5),
    'collateral': (None, None),
}
COLLATERAL_REBALANCE = 0.25     # token as the short's collateral: re-size after a 25% move (the term_carry rule)


def capital_per_notional(model, mm):
    """Capital tied up per unit of notional. Cash models: the token (1.0) plus the short's margin on its own venue,
    sized to survive `move` before liquidation at maintenance margin `mm`: 1 + move + mm. Collateral: the token is the
    short's margin on the same venue (collateral rates 0.6–0.95 leave a 20% rise far from liquidation), so 1.0."""
    move, _ = CAPITAL[model]
    if move is None:
        return 1.0
    return 1.0 + move + mm


def rebalance_threshold(model):
    move, share = CAPITAL[model]
    return COLLATERAL_REBALANCE if move is None else move * share


def rule_wants(rule, f, d, bench, pos):
    """Pre-committed rules. 'always': hold whenever the venue has funding data that day. 'thr': enter when trailing
    k-day funding beats the benchmark + x, leave when it falls below benchmark + x - h. Uses days before d only."""
    if rule['kind'] == 'always':
        return True
    sig = trailing_apr(f, d, rule['k'])
    if sig is None:
        return pos
    if not pos and sig > bench + rule['x']:
        return True
    if pos and sig < bench + rule['x'] - rule['h']:
        return False
    return pos


RULES = [{'name': 'always', 'kind': 'always'}] + [
    {'name': 'trail%dd_x%dpp' % (k, round(100 * x)), 'kind': 'thr', 'k': k, 'x': x, 'h': 0.02}
    for k in (7, 30) for x in (0.0, 0.02, 0.05)]


def best_venue_schedule(f_by, days, k=30):
    """At the first day of each month, the venue whose trailing k-day funding was highest; venues without enough
    history that day are skipped. Nothing after the decision day is used."""
    sched, cur = {}, None
    for d in days:
        if cur is None or dt.datetime.fromtimestamp(d * 86400, UTC).day == 1:
            best = None
            for v, f in f_by.items():
                s = trailing_apr(f, d, k)
                if s is not None and (best is None or s > best[0]):
                    best = (s, v)
            if best:
                cur = best[1]
        sched[d] = cur
    return sched


def simulate(days, legs, rule, model, bench_fn, schedule=None, delay=0, late_hours=0.0, K=None):
    """Long token / short perp, decided at 00:00 UTC each day, excess return per unit of capital per day.

    legs[v] = {'F': {d: perp price at the end of day d}, 'T': {d: token price}, 'f': {d: funding received},
               'hi': {d: perp high during day d}, 'cost_perp', 'cost_token', 'mm', 'hourly': bool};
    schedule[d] picks the venue (best-venue rule); otherwise the single leg is used.
    delay: decisions act `delay` days late (the late-entry test); late_hours: the first hours of each entry day are
    missed (hourly-funded venues lose that share of the day's funding; 4- and 8-hour venues settle later in the day).
    K: capital per notional (default from the model and the leg's maintenance margin).

    Returns (excess series, in-position flags, bookkeeping)."""
    only = next(iter(legs))
    pos, venue = False, None
    F_prev = b_prev = p_ref = None
    ex, flags = [], []
    st = {'entries': 0, 'exits': 0, 'switches': 0, 'rebalances': 0, 'liq_near': 0, 'days_in': 0, 'funding': 0.0,
          'basis': 0.0, 'costs': 0.0, 'neg_funding_days': 0}
    theta = rebalance_threshold(model)
    move = CAPITAL[model][0]
    last = days[-1]
    for i, d in enumerate(days):
        b_day = bench_fn(d)
        v = (schedule.get(d) if schedule else only) or venue or only
        L = legs[v]
        Kv = K if K is not None else capital_per_notional(model, legs[venue or v]['mm'])
        dd = d - delay
        if rule['kind'] == 'always':
            want = (dd in L['f']) or pos
        else:
            want = rule_wants(rule, L['f'], dd, b_day, pos)
        cost = 0.0
        entered = False
        if pos and not want:
            cost += entry_cost(legs[venue]['cost_token'], legs[venue]['cost_perp'])
            st['exits'] += 1
            pos = False
        elif not pos and want:
            cost += entry_cost(L['cost_token'], L['cost_perp'])
            st['entries'] += 1
            pos, venue, entered = True, v, True
            F_prev = L['F'].get(d - 1)
            T_prev = L['T'].get(d - 1)
            b_prev = (T_prev / F_prev - 1.0) if (F_prev and T_prev) else None
            p_ref = F_prev
        elif pos and v != venue:
            cost += legs[venue]['cost_perp'] + L['cost_perp']
            st['switches'] += 1
            venue = v
            F_prev = L['F'].get(d - 1)
            T_prev = L['T'].get(d - 1)
            b_prev = (T_prev / F_prev - 1.0) if (F_prev and T_prev) else None
        if pos:
            Lp = legs[venue]
            Kp = K if K is not None else capital_per_notional(model, Lp['mm'])
            fund = Lp['f'].get(d, 0.0)
            if entered and late_hours and Lp.get('hourly'):
                fund *= max(0.0, 1.0 - late_hours / 24.0)
            F, T = Lp['F'].get(d), Lp['T'].get(d)
            if F and T and F_prev and b_prev is not None:
                b = T / F - 1.0
                r = day_return(F_prev, F, b_prev, b, fund)
                st['basis'] += r - fund
                F_prev, b_prev = F, b
            else:
                r = fund                      # a missing mark: the basis change is taken when prices resume
                if F and T and (F_prev is None or b_prev is None):
                    F_prev, b_prev = F, T / F - 1.0
            if F and p_ref:
                if move is not None and Lp.get('hi', {}).get(d) and Lp['hi'][d] / p_ref - 1.0 > move - 0.01:
                    st['liq_near'] += 1
                g = F / p_ref - 1.0
                if abs(g) > theta:
                    cost += abs(g) * (Lp['cost_token'] + Lp['cost_perp'])
                    st['rebalances'] += 1
                    p_ref = F
            elif F and not p_ref:
                p_ref = F
            if d == last:
                cost += entry_cost(Lp['cost_token'], Lp['cost_perp'])     # closed at the end of the sample
            st['funding'] += fund
            st['days_in'] += 1
            st['neg_funding_days'] += 1 if fund < 0 else 0
            ex.append((r - cost) / Kp - b_day / 365.0)
        else:
            ex.append(-cost / Kv)
        st['costs'] += cost
        flags.append(pos)
    return ex, flags, st


def nw_t(x, lags=None):
    t, p = B.newey_west_t(x, lags=lags)
    return t, p


def ann_mean(x, per=365.0):
    x = [v for v in x if v is not None]
    return sum(x) / len(x) * per if x else None



# ============================================================================================== analysis: loading

# Perp legs: where the short sits. fee_bp is the VIP0 taker fee; mm the maintenance margin at the venue's max
# leverage tier 1 (Hyperliquid: half of the initial margin at max leverage); collateral: tokens the venue accepts as
# the short's margin (collateral rates read in `collect`).
PERP_LEGS = {
    'hl:PAXG': {'fee_bp': 4.5, 'mm': 0.05, 'ref': 'token PAXG (CEX basket)', 'collateral': (), 'hourly': True},
    'bn:PAXGUSDT': {'fee_bp': 5.0, 'mm': 0.01, 'ref': 'token PAXG (CEX basket)', 'collateral': ('PAXG', 'XAUT')},
    'by:PAXGUSDT': {'fee_bp': 5.5, 'mm': 0.01, 'ref': 'token PAXG (CEX basket)', 'collateral': ('XAUT',)},
    'bn:XAUTUSDT': {'fee_bp': 5.0, 'mm': 0.01, 'ref': 'token XAUT (CEX basket)', 'collateral': ('PAXG', 'XAUT')},
    'by:XAUTUSDT': {'fee_bp': 5.5, 'mm': 0.01, 'ref': 'token XAUT (CEX basket)', 'collateral': ('XAUT',)},
    'bn:XAUUSDT': {'fee_bp': 5.0, 'mm': 0.01, 'ref': 'spot XAU', 'collateral': ('PAXG', 'XAUT')},
    'by:XAUUSDT': {'fee_bp': 5.5, 'mm': 0.01, 'ref': 'spot XAU', 'collateral': ('XAUT',)},
    'okx:XAU-USDT-SWAP': {'fee_bp': 5.0, 'mm': 0.01, 'ref': 'spot XAU', 'collateral': ('PAXG', 'XAUT')},
    'hl:xyz:GOLD': {'fee_bp': 9.0, 'mm': 0.02, 'ref': 'spot XAU', 'collateral': (), 'hourly': True},
    'hl:km:GOLD': {'fee_bp': 9.0, 'mm': 0.02, 'ref': 'spot XAU', 'collateral': (), 'hourly': True},
    'hl:flx:GOLD': {'fee_bp': 9.0, 'mm': 0.02, 'ref': 'spot XAU', 'collateral': (), 'hourly': True},
    'hl:cash:GOLD': {'fee_bp': 9.0, 'mm': 0.025, 'ref': 'spot XAU', 'collateral': (), 'hourly': True},
}
SILVER_PERPS = ['bn:XAGUSDT', 'by:XAGUSDT', 'okx:XAG-USDT-SWAP', 'hl:xyz:SILVER', 'hl:km:SILVER', 'hl:flx:SILVER',
                'hl:cash:SILVER']
# Token legs: where the ounce is bought (spot taker fee, VIP0).
TOKEN_LEGS = {
    'PAXG@bn': {'series': 'bn:spot:PAXGUSDT', 'fee_bp': 10.0, 'token': 'PAXG', 'venue': 'bn'},
    'XAUT@bn': {'series': 'bn:spot:XAUTUSDT', 'fee_bp': 10.0, 'token': 'XAUT', 'venue': 'bn'},
    'XAUT@okx': {'series': 'okx:spot:XAUT-USDT', 'fee_bp': 10.0, 'token': 'XAUT', 'venue': 'okx'},
    'XAUT@by': {'series': 'by:spot:XAUTUSDT', 'fee_bp': 10.0, 'token': 'XAUT', 'venue': 'by'},
    'PAXG@okx': {'series': 'okx:spot:PAXG-USDT', 'fee_bp': 10.0, 'token': 'PAXG', 'venue': 'okx'},
}
# The combinations tested (perp, token, capital models). Collateral only where the token sits on the perp's venue
# and that venue accepts it as margin.
COMBOS = [
    ('hl:PAXG', 'PAXG@bn', ('cash10', 'cash20')),
    ('bn:PAXGUSDT', 'PAXG@bn', ('collateral', 'cash10', 'cash20')),
    ('by:PAXGUSDT', 'PAXG@bn', ('cash10', 'cash20')),
    ('bn:XAUTUSDT', 'XAUT@bn', ('collateral', 'cash10', 'cash20')),
    ('by:XAUTUSDT', 'XAUT@by', ('collateral', 'cash10', 'cash20')),
    ('bn:XAUUSDT', 'PAXG@bn', ('collateral', 'cash10', 'cash20')),
    ('bn:XAUUSDT', 'XAUT@bn', ('collateral',)),
    ('by:XAUUSDT', 'XAUT@by', ('collateral', 'cash10', 'cash20')),
    ('hl:xyz:GOLD', 'PAXG@bn', ('cash10', 'cash20')),
]
DESCRIPTIVE = [('okx:XAU-USDT-SWAP', 'XAUT@okx', 'collateral'), ('hl:km:GOLD', 'PAXG@bn', 'cash10'),
               ('hl:flx:GOLD', 'PAXG@bn', 'cash10'), ('hl:cash:GOLD', 'PAXG@bn', 'cash10')]
FAMILIES = {
    'best_paxg_hedged': (['hl:PAXG', 'bn:PAXGUSDT', 'by:PAXGUSDT', 'bn:XAUUSDT', 'hl:xyz:GOLD'], 'PAXG@bn'),
    'best_xaut_hedged': (['bn:XAUTUSDT', 'by:XAUTUSDT', 'bn:XAUUSDT', 'by:XAUUSDT'], 'XAUT@okx'),
}
DEFAULT_HALF_SPREAD_BP = 2.0


def closes_from(rows, kind, step=HOUR_MS, drop_zero_volume=True):
    """{bar end ms: close} and {bar end ms: high} from a venue's bars. Trade bars with zero volume are dropped
    (Hyperliquid serves priced zero-volume bars before listing; Binance serves delisted perps as flat zero-volume
    bars); index/mark/premium bars carry no volume and are kept."""
    c, h = {}, {}
    for r in rows:
        if isinstance(r, dict):
            t, close, hi, vol = int(r['t']), fnum(r['c']), fnum(r['h']), fnum(r.get('v'), 0.0)
        else:
            t, close, hi = int(r[0]), fnum(r[4]), fnum(r[2])
            vol = fnum(r[5], 0.0) if len(r) > 5 else None
        if close is None:
            continue
        if kind == 'trade' and drop_zero_volume and vol is not None and vol <= 0:
            continue
        c[t + step] = close
        h[t + step] = hi
    return c, h


def load_prices(raw):
    """Every hourly price series the study uses, keyed 'venue:instrument:kind' -> {end ms: close}, and highs."""
    P, H = {}, {}
    for s in BN_PERPS:
        for sub, kind in (('klines', 'trade'), ('index', 'index'), ('mark', 'mark'), ('premium', 'premium')):
            fp = raw / 'bn' / ('%s_%s.json.gz' % (sub, s))
            if fp.exists():
                P['bn:%s:%s' % (s, kind)], H['bn:%s:%s' % (s, kind)] = closes_from(read_gz(fp), kind)
    for s in BN_SPOT:
        fp = raw / 'bn' / ('spot_%s.json.gz' % s)
        if fp.exists():
            P['bn:spot:' + s], _ = closes_from(read_gz(fp), 'trade')
    for s in BY_PERPS:
        for sub, kind in (('kline', 'trade'), ('index', 'index'), ('mark', 'mark'), ('premium', 'premium')):
            fp = raw / 'by' / ('%s_%s.json.gz' % (sub, s))
            if fp.exists():
                P['by:%s:%s' % (s, kind)], H['by:%s:%s' % (s, kind)] = closes_from(read_gz(fp), kind)
    for s in BY_SPOT:
        fp = raw / 'by' / ('spot_%s.json.gz' % s)
        if fp.exists():
            P['by:spot:' + s], _ = closes_from(read_gz(fp), 'trade')
    for i in OKX_SWAPS:
        for sub, kind in (('candles', 'trade'), ('mark', 'mark'), ('index', 'index')):
            fp = raw / 'okx' / ('%s_%s.json.gz' % (sub, i))
            if fp.exists():
                P['okx:%s:%s' % (i, kind)], H['okx:%s:%s' % (i, kind)] = closes_from(read_gz(fp), kind)
    for i in OKX_SPOT:
        fp = raw / 'okx' / ('spot_%s.json.gz' % i)
        if fp.exists():
            P['okx:spot:' + i], _ = closes_from(read_gz(fp), 'trade')
    for c in HL_COINS:
        k = 'hl:%s:trade' % c
        fp1, fpd = raw / 'hl' / ('c1h_%s.json.gz' % safe(c)), raw / 'hl' / ('c1d_%s.json.gz' % safe(c))
        c1, h1 = closes_from(read_gz(fp1), 'trade') if fp1.exists() else ({}, {})
        cd, hd = closes_from(read_gz(fpd), 'trade', step=DAY_MS) if fpd.exists() else ({}, {})
        for t, v in cd.items():          # daily bars fill 00:00 marks before the hourly window (last 5,000 hours)
            c1.setdefault(t, v)
        P[k] = c1
        H[k] = h1
        H[k + ':daily_high'] = hd
    for sym in YAHOO_SYMS:
        fp = raw / 'yahoo' / ('%s_1h.json.gz' % safe(sym))
        if fp.exists():
            P['yahoo:%s:1h' % sym], _ = closes_from(read_gz(fp).get('rows') or [], 'futures', drop_zero_volume=False)
        fp = raw / 'yahoo' / ('%s_1d.json.gz' % safe(sym))
        if fp.exists():
            P['yahoo:%s:1d' % sym] = {int(r[0]): r[4] for r in (read_gz(fp).get('rows') or []) if r[4] is not None}
    fp = raw / 'tokens' / 'coinbase_PAXG-USD_1h.json.gz'
    if fp.exists():
        P['cb:spot:PAXG-USD'], _ = closes_from(read_gz(fp), 'trade')
    return P, H


def hl_delisting(raw, coin):
    """End of trading for a delisted HIP-3 market: one hour after its last bar with volume (None if still live)."""
    fp1, fpd = raw / 'hl' / ('c1h_%s.json.gz' % safe(coin)), raw / 'hl' / ('c1d_%s.json.gz' % safe(coin))
    meta = {}
    try:
        meta = read_gz(raw / 'hl' / 'meta.json.gz')
    except FileNotFoundError:
        pass
    live = {p['name'] for k in ('core', 'xyz') for p in (meta.get('perps') or {}).get(k, [])}
    if coin in live or ':' not in coin or coin.startswith('xyz:'):
        return None
    last = None
    for fp, step in ((fp1, HOUR_MS), (fpd, DAY_MS)):
        if fp.exists():
            for r in read_gz(fp):
                if fnum(r.get('v'), 0.0) > 0:
                    last = max(last or 0, int(r['t']) + step)
    return last


def load_funding(raw):
    """{market: [(ms, rate)]} for every perp; delisted HIP-3 markets are cut at their last traded hour (Hyperliquid
    keeps serving zero-rate rows after a delisting)."""
    ev, cut = {}, {}
    for s in BN_PERPS:
        fp = raw / 'bn' / ('funding_%s.json.gz' % s)
        if fp.exists():
            ev['bn:' + s] = [(int(r['t']), float(r['rate'])) for r in read_gz(fp)]
    for s in BY_PERPS:
        fp = raw / 'by' / ('funding_%s.json.gz' % s)
        if fp.exists():
            ev['by:' + s] = [(int(r['t']), float(r['rate'])) for r in read_gz(fp)]
    for i in OKX_SWAPS:
        fp = raw / 'okx' / ('funding_%s.json.gz' % i)
        if fp.exists():
            ev['okx:' + i] = [(int(r['t']), float(r['rate'])) for r in read_gz(fp)]
    for c in HL_COINS:
        fp = raw / 'hl' / ('funding_%s.json.gz' % safe(c))
        if not fp.exists():
            continue
        end = hl_delisting(raw, c)
        rows = [(int(r['time']), float(r['fundingRate'])) for r in read_gz(fp)]
        if end:
            cut['hl:' + c] = end
            rows = [(t, r) for t, r in rows if t <= end]
        ev['hl:' + c] = rows
    return ev, cut


def hl_premiums(raw, coin):
    """{funding hour ms: premium} from Hyperliquid's fundingHistory (the hour's average of impact price over oracle)."""
    fp = raw / 'hl' / ('funding_%s.json.gz' % safe(coin))
    if not fp.exists():
        return {}
    return {int(round(int(r['time']) / HOUR_MS)) * HOUR_MS: fnum(r.get('premium')) for r in read_gz(fp)}


def at(series, T, stale=2):
    """The series value at T, or the latest within `stale` hours before it."""
    for k in range(stale + 1):
        v = series.get(T - k * HOUR_MS)
        if v is not None:
            return v
    return None


def daily_marks(series, d0, d1, stale=2):
    """{d: value at (d+1) 00:00 UTC} for days d0..d1-1 (the end-of-day mark of day d)."""
    out = {}
    for d in range(d0, d1):
        v = at(series, (d + 1) * DAY_MS, stale)
        if v is not None:
            out[d] = v
    return out


def daily_highs(highs, d0, d1):
    out = {}
    for t, v in highs.items():
        d = (t - 1) // DAY_MS
        if d0 <= d < d1 and v is not None:
            out[d] = max(out.get(d, v), v)
    return out



# ============================================================================================== analysis: sections

def pctl(values, q):
    v = sorted(x for x in values if x is not None)
    if not v:
        return None
    k = (len(v) - 1) * q
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def dist(values):
    v = [x for x in values if x is not None]
    if not v:
        return {'n': 0}
    return {'n': len(v), 'mean': statistics.fmean(v), 'median': statistics.median(v), 'p01': pctl(v, 0.01),
            'p05': pctl(v, 0.05), 'p25': pctl(v, 0.25), 'p75': pctl(v, 0.75), 'p95': pctl(v, 0.95),
            'p99': pctl(v, 0.99), 'min': min(v), 'max': max(v), 'sd': statistics.pstdev(v) if len(v) > 1 else 0.0}


def ols_slope(x, y):
    n = len(x)
    if n < 10:
        return None, None
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx <= 0 or syy <= 0:
        return None, None
    return sxy / sxx, sxy / math.sqrt(sxx * syy)


def market_index(P, raw, m):
    """The index/oracle series of a perp market. Binance, Bybit and OKX publish theirs as klines; Hyperliquid does
    not, so its oracle is implied from the hour's trade close and the hour's average premium (close / (1 + premium)),
    which is approximate to the premium's within-hour variation."""
    v, inst = m.split(':', 1)
    if v in ('bn', 'by'):
        return P.get('%s:%s:index' % (v, inst), {})
    if v == 'okx':
        return P.get('okx:%s:index' % inst, {})
    prem = hl_premiums(raw, inst)
    tr = P.get('hl:%s:trade' % inst, {})
    out = {}
    for t, c in tr.items():
        p = prem.get(t)
        if p is not None:
            out[t] = c / (1.0 + p)
    return out


def business_days_back(day, n):
    """The date n weekdays before `day` (holidays ignored)."""
    x = day
    while n > 0:
        x -= dt.timedelta(days=1)
        if x.weekday() < 5:
            n -= 1
    return x


def last_business_day(y, m):
    x = dt.datetime(y + (m // 12), m % 12 + 1, 1, tzinfo=UTC) - dt.timedelta(days=1)
    while x.weekday() >= 5:
        x -= dt.timedelta(days=1)
    return x


YAHOO_GC_MONTHS = (2, 4, 6, 8, 12)    # Yahoo's GC=F skips October: it rolled Aug -> Dec on 2025-07-30 and 2026-07-29


def contract_for(ms):
    """The COMEX gold contract Yahoo's continuous GC=F refers to at ms, and its last trading day.

    Read from the data (the index/GC=F steps in `oracle_check`): GC=F holds Feb, Apr, Jun, Aug and Dec, and moves to the
    next one two business days before the last business day of the month before delivery (2026-01-28, 03-27, 05-27,
    07-29; 2025-11-26). Last trading day: the third-last business day of the contract month."""
    t = dt.datetime.fromtimestamp(ms / 1000.0, UTC)
    for k in range(0, 14):
        y, m = t.year + (t.month - 1 + k) // 12, (t.month - 1 + k) % 12 + 1
        if m not in YAHOO_GC_MONTHS:
            continue
        py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
        roll = business_days_back(last_business_day(py, pm), 2)
        if t < roll:
            last = last_business_day(y, m)
            return '%04d-%02d' % (y, m), business_days_back(last, 2)
    return None, None


def months_between(a, b):
    ya, ma = int(a[:4]), int(a[5:7])
    yb, mb = int(b[:4]), int(b[5:7])
    return (yb - ya) * 12 + (mb - ma)


def implied_carry(P):
    """The futures market's cost of carry (USD rate minus gold lease, plus COMEX's premium over London when there is
    one), two ways: (a) the calendar spread paid at each GC=F roll, read as the step of PAXG/GC=F, divided by the months
    between the contracts; (b) ln(GC=F / Binance's spot index) over the time to the contract's last trading day."""
    gc = P.get('yahoo:GC=F:1h', {})
    paxg = P.get('bn:spot:PAXGUSDT', {})
    idx = P.get('bn:XAUUSDT:index', {})
    day = {}
    for t, g in gc.items():
        p = paxg.get(t)
        if p and spot_open(t - HOUR_MS):
            day.setdefault(t // DAY_MS, []).append(p / g - 1.0)
    dm = {d: statistics.median(v) for d, v in day.items() if len(v) >= 3}
    rolls = []
    for d in sorted(dm):
        if (d - 1) not in dm:
            continue
        c0, _ = contract_for((d - 1) * DAY_MS + 12 * HOUR_MS)
        c1, _ = contract_for(d * DAY_MS + 12 * HOUR_MS)
        if c0 and c1 and c0 != c1:
            # Compare the medians two days apart to straddle the switch hour.
            a = dm.get(d - 2, dm[d - 1])
            b = dm.get(d + 1, dm[d])
            step = b - a
            mths = months_between(c0, c1)
            rolls.append({'day': ymd(d * DAY_MS), 'from': c0, 'to': c1, 'step': step, 'months': mths,
                          'implied_carry_apr': -step / mths * 12.0})
    lvl, by_contract = [], {}
    t_end = max(idx) if idx else 0
    for t, o in idx.items():
        g = gc.get(t)
        if not g or not spot_open(t - HOUR_MS):
            continue
        cname, last = contract_for(t)
        tau = (last.timestamp() * 1000 - t) / (365.0 * DAY_MS) if last else None
        if not tau or tau < 20 / 365.0:
            continue
        c = math.log(g / o) / tau
        by_contract.setdefault(cname, []).append(c)
        if t >= t_end - 60 * DAY_MS:
            lvl.append(c)
    recent = [r['implied_carry_apr'] for r in rolls if r['day'] >= '2025-12-01']
    return {'rolls': rolls, 'recent_rolls_median': statistics.median(recent) if recent else None,
            'level_last_60d': dist(lvl),
            'level_by_contract_median': {k: statistics.median(v) for k, v in sorted(by_contract.items())
                                         if len(v) > 20},
            'method': '(a) -step of the daily median PAXG/GC=F at each GC=F roll x 12 / months between contracts; '
                      '(b) ln(GC=F / Binance spot index) / years to last trading day, US-session hours. Both include '
                      'COMEX\'s premium over London (EFP), which blew out in 2024-12..2025-02'}


def weekend_regimes(P, raw, markets=('bn:XAUUSDT', 'by:XAUUSDT', 'okx:XAU-USDT-SWAP', 'hl:xyz:GOLD', 'bn:XAGUSDT',
                                      'hl:xyz:SILVER')):
    """Weekend hours (Fri 17:00 to Sun 18:00 ET) by calendar month: share of hours the index did not move, and the
    slope of its hourly move on its own perp's. A frozen index is a spot index left alone; a moving one is a 24/7 blend
    that includes perps (Binance's lists xyz:GOLD and its own XAUUSDT; OKX's lists Hyperliquid's oracle and Binance's
    index; Bybit's lists Binance's index and perps)."""
    out = {}
    for m in markets:
        O = market_index(P, raw, m)
        v, inst = m.split(':', 1)
        F = P.get('%s:%s:trade' % (v, inst), {})
        byq = {}
        for t in sorted(O):
            if (t - HOUR_MS) not in O or t not in F or (t - HOUR_MS) not in F:
                continue
            x = dt.datetime.fromtimestamp((t - HOUR_MS) / 1000.0, NY)
            wd, h = x.weekday(), x.hour
            if not (wd == 5 or (wd == 6 and h < 18) or (wd == 4 and h >= 17)):
                continue
            byq.setdefault(utc(t)[:7], []).append((math.log(F[t] / F[t - HOUR_MS]),
                                                   math.log(O[t] / O[t - HOUR_MS])))
        rows, first_moving = {}, None
        for q in sorted(byq):
            xs, ys = [a for a, _ in byq[q]], [b for _, b in byq[q]]
            sl, cr = ols_slope(xs, ys)
            fr = sum(1 for y in ys if abs(y) < 1e-5) / len(ys)
            rows[q] = {'hours': len(ys), 'frozen_share': fr, 'slope_on_perp': sl, 'corr': cr}
            if first_moving is None and fr < 0.5 and len(ys) > 50:
                first_moving = q
        out[m] = {'by_month': rows, 'first_month_moving': first_moving}
    # The exact first weekend Binance's XAU index moved.
    O = P.get('bn:XAUUSDT:index', {})
    first = None
    for t in sorted(O):
        x = dt.datetime.fromtimestamp((t - HOUR_MS) / 1000.0, NY)
        if x.weekday() == 5 and (t - HOUR_MS) in O and abs(math.log(O[t] / O[t - HOUR_MS])) > 1e-5:
            first = utc(t)
            break
    out['_binance_xau_first_saturday_move'] = first
    return out


def oracle_check(P, H, raw):
    """What each gold/silver perp's index tracks. A spot-following index sits below COMEX's front future by the cost of
    carry, steps with the future's roll in the opposite direction and drifts towards it between rolls; a
    futures-following one sits on the future. Tokens are 1 oz of spot gold, so index/token is stable for a spot index.
    Weekends: how much of its own perp's move the index follows while spot is shut."""
    gc, si = P.get('yahoo:GC=F:1h', {}), P.get('yahoo:SI=F:1h', {})
    paxg = P.get('bn:spot:PAXGUSDT', {})
    out = {}
    markets = [('bn:XAUUSDT', gc), ('by:XAUUSDT', gc), ('okx:XAU-USDT-SWAP', gc), ('hl:xyz:GOLD', gc),
               ('hl:km:GOLD', gc), ('hl:flx:GOLD', gc), ('hl:cash:GOLD', gc),
               ('bn:XAGUSDT', si), ('by:XAGUSDT', si), ('okx:XAG-USDT-SWAP', si), ('hl:xyz:SILVER', si),
               ('bn:PAXGUSDT', gc), ('by:PAXGUSDT', gc), ('hl:PAXG', gc), ('bn:XAUTUSDT', gc), ('by:XAUTUSDT', gc)]
    for m, fut in markets:
        O = market_index(P, raw, m)
        if not O:
            continue
        v, inst = m.split(':', 1)
        F = P.get('%s:%s:trade' % (v, inst), {})
        rec = {'hours': len(O), 'first': utc(min(O)), 'last': utc(max(O))}
        r_fut, r_tok, by_day_fut, by_day_tok = [], [], {}, {}
        for t, o in O.items():
            if not spot_open(t - HOUR_MS):
                continue
            g = fut.get(t)
            if g:
                r_fut.append(o / g - 1.0)
                by_day_fut.setdefault(t // DAY_MS, []).append(o / g - 1.0)
            p = paxg.get(t)
            if p and 'XAG' not in m and 'SILVER' not in m:
                r_tok.append(o / p - 1.0)
                by_day_tok.setdefault(t // DAY_MS, []).append(o / p - 1.0)
        dm_f = {d: statistics.median(v_) for d, v_ in by_day_fut.items() if len(v_) >= 3}
        dm_t = {d: statistics.median(v_) for d, v_ in by_day_tok.items() if len(v_) >= 3}
        rec['vs_front_future_open_hours'] = dist(r_fut)
        rec['vs_paxg_open_hours'] = dist(r_tok)
        rec['daily_median_sd_vs_future'] = statistics.pstdev(list(dm_f.values())) if len(dm_f) > 2 else None
        rec['daily_median_sd_vs_paxg'] = statistics.pstdev(list(dm_t.values())) if len(dm_t) > 2 else None
        # Steps: day-over-day changes of the daily median ratio larger than 25bp.
        steps_f = [(ymd(d * DAY_MS), dm_f[d] - dm_f[d - 1]) for d in sorted(dm_f) if (d - 1) in dm_f
                   and abs(dm_f[d] - dm_f[d - 1]) > 0.0025]
        steps_t = [(ymd(d * DAY_MS), dm_t[d] - dm_t[d - 1]) for d in sorted(dm_t) if (d - 1) in dm_t
                   and abs(dm_t[d] - dm_t[d - 1]) > 0.0025]
        rec['steps_vs_future_gt25bp'] = steps_f[:40]
        rec['steps_vs_paxg_gt25bp'] = steps_t[:40]
        # Weekend / closed hours: does the index follow its own perp?
        xs_c, ys_c, xs_o, ys_o, frozen, closed_n = [], [], [], [], 0, 0
        for t in sorted(O):
            if (t - HOUR_MS) not in O or t not in F or (t - HOUR_MS) not in F:
                continue
            dO = math.log(O[t] / O[t - HOUR_MS])
            dF = math.log(F[t] / F[t - HOUR_MS])
            if spot_open(t - HOUR_MS):
                xs_o.append(dF)
                ys_o.append(dO)
            else:
                closed_n += 1
                frozen += 1 if abs(dO) < 1e-5 else 0
                xs_c.append(dF)
                ys_c.append(dO)
        so, co = ols_slope(xs_o, ys_o)
        sc, cc = ols_slope(xs_c, ys_c)
        rec['open_hours'] = {'n': len(xs_o), 'slope_index_on_perp': so, 'corr': co,
                             'abs_move_bp_median': statistics.median([abs(y) * 1e4 for y in ys_o]) if ys_o else None}
        rec['closed_hours'] = {'n': closed_n, 'slope_index_on_perp': sc, 'corr': cc,
                               'share_frozen_lt_0p1bp': frozen / closed_n if closed_n else None,
                               'abs_move_bp_median': statistics.median([abs(y) * 1e4 for y in ys_c]) if ys_c else None}
        out[m] = rec
    out['_implied_carry'] = implied_carry(P)
    out['_weekend_regimes'] = weekend_regimes(P, raw)
    return out


def index_regime_funding(ev, switch_iso):
    """Binance XAU/XAG funding while spot is open and shut, before and after the weekend index started moving."""
    if not switch_iso:
        return None
    sw = int(dt.datetime.fromisoformat(switch_iso).timestamp() * 1000)
    out = {}
    for m in ('bn:XAUUSDT', 'bn:XAGUSDT'):
        rows = ev.get(m) or []
        h = settlement_hours(rows) or 4
        acc = {}
        for t, r in rows:
            k = ('before' if t < sw else 'after') + ('_open' if spot_open(int(t - h * HOUR_MS / 2.0)) else '_shut')
            a = acc.setdefault(k, [0.0, 0])
            a[0] += r
            a[1] += 1
        out[m] = {k: v[0] / v[1] * 8760.0 / h for k, v in sorted(acc.items()) if v[1]}
    out['switch'] = switch_iso
    return out


def funding_table(ev, cut):
    """Per market: interval, APR since listing, by halves, recent windows, and how often the venue sat at its floor."""
    out = {}
    for m, rows in sorted(ev.items()):
        if len(rows) < 10:
            continue
        rows = sorted(rows)
        t0, t1 = rows[0][0], rows[-1][0]
        h = settlement_hours(rows)
        rates = [r for _, r in rows]
        mode = statistics.mode(rates)
        mid = t0 + (t1 - t0) // 2
        now = t1
        f, n = daily_funding(rows)
        monthly = {}
        for t, r in rows:
            k = utc(t)[:7]
            monthly.setdefault(k, []).append(r)
        # Spot open vs shut: each settlement is attributed to the mid-point of the interval it pays for.
        so = sc = 0.0
        no = nc = 0
        for t, r in rows:
            if spot_open(int(t - h * HOUR_MS / 2.0)):
                so, no = so + r, no + 1
            else:
                sc, nc = sc + r, nc + 1
        out[m] = {
            'apr_spot_open': so / no * 8760.0 / h if no and h else None,
            'apr_spot_shut': sc / nc * 8760.0 / h if nc and h else None,
            'share_settlements_spot_shut': nc / len(rows),
            'first': utc(t0), 'last': utc(t1), 'settlements': len(rows), 'interval_h': h,
            'delisted_at': utc(cut[m]) if m in cut else None,
            'apr_since_listing': funding_apr(rows),
            'apr_first_half': funding_apr(rows, t0, mid), 'apr_second_half': funding_apr(rows, mid, t1 + 1),
            'apr_last_90d': funding_apr(rows, now - 90 * DAY_MS, now + 1),
            'apr_last_30d': funding_apr(rows, now - 30 * DAY_MS, now + 1),
            'mode_rate': mode, 'mode_apr': apr_per_settlement(mode, h) if h else None,
            'share_at_mode': sum(1 for r in rates if r == mode) / len(rates),
            'share_negative': sum(1 for r in rates if r < 0) / len(rates),
            'share_zero': sum(1 for r in rates if r == 0) / len(rates),
            'monthly_apr': {k: sum(v) / len(v) * 8760.0 / h for k, v in sorted(monthly.items())} if h else {},
        }
    return out


def premium_paths(P, raw):
    """PAXG and XAUT against spot gold, open hours only, on three independent-ish paths."""
    hl_o = market_index(P, raw, 'hl:xyz:GOLD')
    paths = {
        'PAXG@binance / Binance XAU index (USDT)': (P.get('bn:spot:PAXGUSDT', {}), P.get('bn:XAUUSDT:index', {})),
        'PAXG@coinbase (USD) / xyz:GOLD implied oracle (USD)': (P.get('cb:spot:PAXG-USD', {}), hl_o),
        'PAXG@okx / OKX XAU-USDT index': (P.get('okx:spot:PAXG-USDT', {}), P.get('okx:XAU-USDT-SWAP:index', {})),
        'XAUT@binance / Binance XAU index (USDT)': (P.get('bn:spot:XAUTUSDT', {}), P.get('bn:XAUUSDT:index', {})),
        'XAUT@okx / OKX XAU-USDT index': (P.get('okx:spot:XAUT-USDT', {}), P.get('okx:XAU-USDT-SWAP:index', {})),
        'XAUT@bybit / Bybit XAU index': (P.get('by:spot:XAUTUSDT', {}), P.get('by:XAUUSDT:index', {})),
    }
    out = {}
    common = None
    for name, (tok, ref) in paths.items():
        prem, closed, by_month, day_med = [], [], {}, {}
        for t, x in tok.items():
            o = ref.get(t)
            if not o:
                continue
            q = x / o - 1.0
            if spot_open(t - HOUR_MS):
                prem.append(q)
                by_month.setdefault(utc(t)[:7], []).append(q)
                day_med.setdefault(t // DAY_MS, []).append(q)
            else:
                closed.append(q)
        dm = {d: statistics.median(v) for d, v in day_med.items() if len(v) >= 3}
        chg = [dm[d] - dm[d - 1] for d in sorted(dm) if (d - 1) in dm]
        out[name] = {'open_hours': dist(prem), 'closed_hours': dist(closed),
                     'daily_median_change': dist(chg),
                     'by_month_median': {k: statistics.median(v) for k, v in sorted(by_month.items())},
                     '_days': dm}
    # A common window for the cross-path check (the headline's independent verification).
    keys = ['PAXG@binance / Binance XAU index (USDT)', 'PAXG@coinbase (USD) / xyz:GOLD implied oracle (USD)',
            'PAXG@okx / OKX XAU-USDT index']
    days = None
    for k in keys:
        s = set(out[k]['_days'])
        days = s if days is None else days & s
    days = sorted(days or [])
    out['_cross_check'] = {
        'days': len(days), 'first': ymd(days[0] * DAY_MS) if days else None,
        'last': ymd(days[-1] * DAY_MS) if days else None,
        'median_of_daily_medians': {k: statistics.median([out[k]['_days'][d] for d in days]) if days else None
                                    for k in keys},
        'corr_daily_binance_vs_coinbase': ols_slope([out[keys[0]]['_days'][d] for d in days],
                                                    [out[keys[1]]['_days'][d] for d in days])[1] if days else None,
        'corr_daily_binance_vs_okx': ols_slope([out[keys[0]]['_days'][d] for d in days],
                                               [out[keys[2]]['_days'][d] for d in days])[1] if days else None,
    }
    for k in list(out):
        if not k.startswith('_'):
            out[k].pop('_days', None)
    return out


def half_spreads(books):
    """{book key: (half-spread bp, mid)} from the newest snapshot."""
    hs = {}
    for k, (bids, asks) in books.items():
        if bids and asks:
            mid = (bids[0][0] + asks[0][0]) / 2.0
            hs[k] = ((asks[0][0] - bids[0][0]) / 2.0 / mid * 1e4, mid)
    return hs


def parse_books(snap):
    """Normalise every venue's book to {key: (bids [(px, qty)], asks)} sorted best first; qty in ounces (tokens or
    contracts converted to ounces)."""
    out = {}
    for k, b in (snap or {}).get('books', {}).items():
        try:
            bids = asks = None
            if k.startswith('bn_'):
                bids = [(float(p), float(q)) for p, q in b.get('bids', [])]
                asks = [(float(p), float(q)) for p, q in b.get('asks', [])]
            elif k.startswith('by_'):
                r = b.get('result') or {}
                bids = [(float(p), float(q)) for p, q in r.get('b', [])]
                asks = [(float(p), float(q)) for p, q in r.get('a', [])]
            elif k.startswith('okx:'):
                r = (b.get('data') or [{}])[0]
                ct = 0.001 if 'XAU-USDT-SWAP' in k else (0.01 if 'XAG-USDT-SWAP' in k else 1.0)
                bids = [(float(x[0]), float(x[1]) * ct) for x in r.get('bids', [])]
                asks = [(float(x[0]), float(x[1]) * ct) for x in r.get('asks', [])]
            elif k.startswith('kraken'):
                r = list((b.get('result') or {}).values())
                if r:
                    bids = [(float(x[0]), float(x[1])) for x in r[0].get('bids', [])]
                    asks = [(float(x[0]), float(x[1])) for x in r[0].get('asks', [])]
            elif k.startswith('coinbase'):
                bids = [(float(x[0]), float(x[1])) for x in b.get('bids', [])]
                asks = [(float(x[0]), float(x[1])) for x in b.get('asks', [])]
            elif k.startswith('bitfinex'):
                if isinstance(b, list):
                    bids = [(float(x[0]), float(x[2])) for x in b if float(x[2]) > 0]
                    asks = [(float(x[0]), -float(x[2])) for x in b if float(x[2]) < 0]
            elif k.startswith('hl:') or k.startswith('hl_coarse:') or k.startswith('hl_spot:'):
                lv = b.get('levels') if isinstance(b, dict) else None
                if lv:
                    bids = [(float(x['px']), float(x['sz'])) for x in lv[0]]
                    asks = [(float(x['px']), float(x['sz'])) for x in lv[1]]
            if bids is not None and asks is not None:
                out[k] = (sorted(bids, key=lambda x: -x[0]), sorted(asks, key=lambda x: x[0]))
        except Exception:  # noqa: BLE001 - one malformed book does not stop the rest
            continue
    return out


def depth_usd(levels, mid, bp):
    """USD notional resting within `bp` of mid on one side."""
    lim = bp / 1e4
    return sum(p * q for p, q in levels if abs(p / mid - 1.0) <= lim)


def walk_cost(levels, mid, usd):
    """Average cost in bp of taking `usd` notional from one side (None when the book is too thin)."""
    left, cost = usd, 0.0
    for p, q in levels:
        take = min(left, p * q)
        cost += take * abs(p / mid - 1.0)
        left -= take
        if left <= 1e-9:
            return cost / usd * 1e4
    return None


BOOK_OF_PERP = {'hl:PAXG': 'hl:PAXG', 'bn:PAXGUSDT': 'bn_perp:PAXGUSDT', 'by:PAXGUSDT': 'by_perp:PAXGUSDT',
                'bn:XAUTUSDT': 'bn_perp:XAUTUSDT', 'by:XAUTUSDT': 'by_perp:XAUTUSDT', 'bn:XAUUSDT': 'bn_perp:XAUUSDT',
                'by:XAUUSDT': 'by_perp:XAUUSDT', 'okx:XAU-USDT-SWAP': 'okx:XAU-USDT-SWAP', 'hl:xyz:GOLD': 'hl:xyz:GOLD',
                'bn:XAGUSDT': 'bn_perp:XAGUSDT', 'by:XAGUSDT': 'by_perp:XAGUSDT', 'hl:xyz:SILVER': 'hl:xyz:SILVER',
                'okx:XAG-USDT-SWAP': 'okx:XAG-USDT-SWAP'}
BOOKS_OF_TOKEN = {'PAXG': ['bn_spot:PAXGUSDT', 'bn_spot:PAXGUSDC', 'okx:PAXG-USDT', 'kraken_spot:PAXGUSD',
                           'coinbase_spot:PAXG-USD'],
                  'XAUT': ['bn_spot:XAUTUSDT', 'bn_spot:XAUTUSDC', 'okx:XAUT-USDT', 'by_spot:XAUTUSDT',
                           'bitfinex_spot:XAUT:USD', 'bitfinex_spot:XAUT:UST']}
BOOK_OF_TOKEN_LEG = {'PAXG@bn': 'bn_spot:PAXGUSDT', 'XAUT@bn': 'bn_spot:XAUTUSDT', 'XAUT@okx': 'okx:XAUT-USDT',
                     'XAUT@by': 'by_spot:XAUTUSDT', 'PAXG@okx': 'okx:PAXG-USDT'}


def latest_books(raw):
    files = sorted((raw / 'books').glob('books_*.json.gz')) if (raw / 'books').exists() else []
    snaps = []
    for fp in files:
        s = read_gz(fp)
        snaps.append((s.get('at'), parse_books(s)))
    return snaps


def book_table(snaps):
    out = {}
    for at_, books in snaps:
        rows = {}
        for k, (bids, asks) in books.items():
            if not bids or not asks:
                continue
            mid = (bids[0][0] + asks[0][0]) / 2.0
            rows[k] = {'mid': mid, 'half_spread_bp': (asks[0][0] - bids[0][0]) / 2.0 / mid * 1e4,
                       'bid_25bp_usd': depth_usd(bids, mid, 25), 'ask_25bp_usd': depth_usd(asks, mid, 25),
                       'bid_10bp_usd': depth_usd(bids, mid, 10), 'ask_10bp_usd': depth_usd(asks, mid, 10),
                       'bid_total_usd': sum(p * q for p, q in bids), 'ask_total_usd': sum(p * q for p, q in asks)}
        out[at_] = rows
    return out


def leg_costs(books_now):
    """One-side cost per leg (fee + half-spread) from the newest books; the default half-spread where a book is
    missing is recorded."""
    hs = half_spreads(books_now) if books_now else {}
    perp, tok, used = {}, {}, {}
    for m, spec in PERP_LEGS.items():
        k = BOOK_OF_PERP.get(m)
        h = hs.get(k, (DEFAULT_HALF_SPREAD_BP, None))[0] if k else DEFAULT_HALF_SPREAD_BP
        perp[m] = (spec['fee_bp'] + h) / 1e4
        used[m] = {'fee_bp': spec['fee_bp'], 'half_spread_bp': h, 'measured': k in hs}
    for t, spec in TOKEN_LEGS.items():
        k = BOOK_OF_TOKEN_LEG.get(t)
        h = hs.get(k, (DEFAULT_HALF_SPREAD_BP, None))[0]
        tok[t] = (spec['fee_bp'] + h) / 1e4
        used[t] = {'fee_bp': spec['fee_bp'], 'half_spread_bp': h, 'measured': k in hs}
    return perp, tok, used



# ============================================================================================== analysis: carry

def build_leg(P, H, ev, cut, perp, tok, cost_perp, cost_tok):
    """Daily inputs of one perp/token pair: end-of-day marks, funding by day, highs; the span is where the perp has
    funding and both legs have prices (a delisted market ends at its last traded hour)."""
    v, inst = perp.split(':', 1)
    f, n = daily_funding(ev.get(perp, []), cut.get(perp))
    if not f:
        return None
    d0, d1 = min(f), max(f) + 1
    Fh = P.get('%s:%s:trade' % (v, inst), {})
    Th = P.get(TOKEN_LEGS[tok]['series'], {})
    F, T = daily_marks(Fh, d0 - 1, d1), daily_marks(Th, d0 - 1, d1)
    hi = daily_highs(H.get('%s:%s:trade' % (v, inst), {}), d0 - 1, d1)
    for d, x in daily_highs(H.get('%s:%s:trade:daily_high' % (v, inst), {}), d0 - 1, d1).items():
        hi.setdefault(d, x)
    # Usable days: funding that day and both marks at its start and end (a partial last day is dropped).
    days = [d for d in range(d0, d1) if d in f and n.get(d, 0) >= 1 and (d - 1) in F and (d - 1) in T]
    if perp in cut:
        days = [d for d in days if (d + 1) * DAY_MS <= cut[perp]]
    today = int(time.time() * 1000) // DAY_MS
    days = [d for d in days if d < today]
    if len(days) < 20:
        return None
    return {'F': F, 'T': T, 'f': f, 'n': n, 'hi': hi, 'days': days, 'cost_perp': cost_perp, 'cost_token': cost_tok,
            'mm': PERP_LEGS[perp]['mm'], 'hourly': PERP_LEGS[perp].get('hourly', False)}


def decompose(days, leg):
    """Always-on, before costs, per unit notional: funding, the token-minus-perp basis change, and the split of that
    basis between the token's premium and the perp's premium is left to the premium section."""
    fsum = bsum = 0.0
    nd = 0
    b_prev = F_prev = None
    for d in days:
        F, T = leg['F'].get(d), leg['T'].get(d)
        if F_prev is None:
            F0, T0 = leg['F'].get(d - 1), leg['T'].get(d - 1)
            if F0 and T0:
                F_prev, b_prev = F0, T0 / F0 - 1.0
        fund = leg['f'].get(d, 0.0)
        fsum += fund
        if F and T and F_prev:
            b = T / F - 1.0
            bsum += day_return(F_prev, F, b_prev, b, 0.0)
            F_prev, b_prev = F, b
        nd += 1
    return {'days': nd, 'funding_apr': fsum / nd * 365.0, 'basis_apr': bsum / nd * 365.0}


def run_block(name, days, legs, model, schedule=None, K=None, frac=0.5):
    """Seven pre-committed rules on one series, chosen on the first `frac` of its days, tested on the rest."""
    series, books, flags = {}, {}, {}
    for r in RULES:
        ex, fl, st = simulate(days, legs, r, model, bench_const, schedule=schedule, K=K)
        series[r['name']], books[r['name']], flags[r['name']] = ex, st, fl
    ctt = B.choose_then_test(series, frac=frac, periods_per_year=365)
    c = ctt['cutoff_index']
    ch = ctt['chosen']
    test = series[ch][c:]
    hist_ex, _, _ = simulate(days, legs, next(r for r in RULES if r['name'] == ch), model, bench_hist,
                             schedule=schedule, K=K)
    t30 = nw_t(test, lags=30)
    by_year = {}
    for i, d in enumerate(days):
        by_year.setdefault(str(dt.datetime.fromtimestamp(d * 86400, UTC).year), []).append(series['always'][i])
    leg0 = legs[next(iter(legs))]
    Kc = K if K is not None else capital_per_notional(model, leg0['mm'])
    return {
        'name': name, 'model': model, 'capital_per_notional': Kc, 'first_day': ymd(days[0] * DAY_MS),
        'split_day': ymd(days[c] * DAY_MS), 'last_day': ymd(days[-1] * DAY_MS), 'days': len(days),
        'chosen': ch, 'n_variants': ctt['n_variants'],
        'in_sample': {k: ctt['in_sample'].get(k) for k in ('ann_return', 'ann_vol', 'sharpe', 'max_drawdown')},
        'out_of_sample': {k: ctt['out_of_sample'].get(k) for k in ('ann_return', 'ann_vol', 'sharpe', 'max_drawdown',
                                                                   'hit_rate', 'n')},
        'oos_rank': ctt['oos_rank'], 'oos_t': ctt['oos_t'], 'oos_p': ctt['oos_p'], 'oos_t_nw30': t30[0],
        'oos_p_nw30': t30[1],
        'deflated_sharpe_in_sample': ctt['deflated_sharpe_in_sample'],
        'bh_survivors_full_sample': ctt['bh_survivors_full_sample'],
        'test_block_bootstrap': B.block_bootstrap([x * 365.0 for x in test], block=20),
        'test_hist_benchmark_ann': ann_mean(hist_ex[c:]),
        'variants_test_ann': {k: ann_mean(v[c:]) for k, v in series.items()},
        'variants_train_ann': {k: ann_mean(v[:c]) for k, v in series.items()},
        'variants_test_p_nw30': {k: nw_t(v[c:], lags=30)[1] for k, v in series.items()},
        'always_by_year_ann': {y: ann_mean(v) for y, v in by_year.items()},
        'always_last_90d_ann': ann_mean(series['always'][-90:]),
        'chosen_last_90d_ann': ann_mean(series[ch][-90:]),
        'bookkeeping_chosen': books[ch], 'bookkeeping_always': books['always'],
        'time_in_position_test': sum(1 for x in flags[ch][c:] if x) / max(1, len(flags[ch][c:])),
        '_series': series, '_days': days, '_c': c,
    }


def late_entry(days, legs, model, rule_name, c, schedule=None, K=None):
    """Share of the chosen rule's test-period excess kept when every decision acts 1 day late, and when the first
    hour of every entry day is missed."""
    r = next(x for x in RULES if x['name'] == rule_name)
    base, _, _ = simulate(days, legs, r, model, bench_const, schedule=schedule, K=K)
    d1, _, _ = simulate(days, legs, r, model, bench_const, schedule=schedule, K=K, delay=1)
    h1, _, _ = simulate(days, legs, r, model, bench_const, schedule=schedule, K=K, late_hours=1.0)
    b, x1, xh = ann_mean(base[c:]), ann_mean(d1[c:]), ann_mean(h1[c:])
    gross = None
    return {'test_excess': b, 'late_1day_excess': x1, 'late_1hour_excess': xh,
            'kept_1day': (x1 / b) if b and b > 0 else None, 'kept_1hour': (xh / b) if b and b > 0 else None,
            'note': gross}


def carry_section(P, H, ev, cut, cost_perp, cost_tok):
    blocks, legs_all = [], {}
    for perp, tok, models in COMBOS:
        leg = build_leg(P, H, ev, cut, perp, tok, cost_perp[perp], cost_tok[tok])
        if not leg:
            continue
        legs_all[(perp, tok)] = leg
        for model in models:
            blk = run_block('%s x %s' % (perp, tok), leg['days'], {perp: leg}, model)
            blk['perp'], blk['token'] = perp, tok
            blk['decomposition_always_gross'] = decompose(leg['days'], leg)
            blk['late_entry'] = late_entry(leg['days'], {perp: leg}, model, blk['chosen'], blk['_c'])
            blocks.append(blk)
    fams = []
    for fam, (venues, tok) in FAMILIES.items():
        legs = {}
        for v in venues:
            leg = legs_all.get((v, tok)) or build_leg(P, H, ev, cut, v, tok, cost_perp[v], cost_tok[tok])
            if leg:
                legs[v] = leg
        if len(legs) < 2:
            continue
        days = sorted(set().union(*[set(l['days']) for l in legs.values()]))
        f_by = {v: l['f'] for v, l in legs.items()}
        sched = best_venue_schedule(f_by, days)
        # Days where the scheduled venue has no usable data are skipped by marking funding only.
        K = 1.0 + 0.10 + max(l['mm'] for l in legs.values())
        blk = run_block(fam, days, legs, 'cash10', schedule=sched, K=K)
        blk['venues'] = list(legs)
        blk['token'] = tok
        blk['schedule_share'] = {v: sum(1 for d in days if sched.get(d) == v) / len(days) for v in legs}
        blk['late_entry'] = late_entry(days, legs, 'cash10', blk['chosen'], blk['_c'], schedule=sched, K=K)
        fams.append(blk)
    desc = []
    for perp, tok, model in DESCRIPTIVE:
        leg = build_leg(P, H, ev, cut, perp, tok, cost_perp[perp], cost_tok[tok])
        if not leg:
            desc.append({'perp': perp, 'token': tok, 'note': 'not enough overlapping data'})
            continue
        r = RULES[0]
        ex, _, st = simulate(leg['days'], {perp: leg}, r, model, bench_const)
        desc.append({'perp': perp, 'token': tok, 'model': model, 'first_day': ymd(leg['days'][0] * DAY_MS),
                     'last_day': ymd(leg['days'][-1] * DAY_MS), 'days': len(leg['days']),
                     'always_ann_excess': ann_mean(ex), 'nw_t': nw_t(ex, lags=10)[0],
                     'decomposition_always_gross': decompose(leg['days'], leg), 'bookkeeping': st})
    # Multiple testing across the whole study: every (series, capital, rule) variant's test-period p-value.
    allp, names = [], []
    for blk in blocks + fams:
        for k, p in blk['variants_test_p_nw30'].items():
            names.append('%s|%s|%s' % (blk['name'], blk['model'], k))
            allp.append(p)
    rej, adj = B.bh(allp, q=0.10)
    chosen_keys = {'%s|%s|%s' % (b['name'], b['model'], b['chosen']) for b in blocks + fams}
    n_trials = len(allp)
    for blk in blocks + fams:
        c = blk['_c']
        test = blk['_series'][blk['chosen']][c:]
        train = blk['_series'][blk['chosen']][:c]
        blk['deflated_sharpe_study_wide'] = B.deflated_sharpe(train, n_trials)
        key = '%s|%s|%s' % (blk['name'], blk['model'], blk['chosen'])
        blk['bh_study_wide'] = {'adjusted_p': adj[names.index(key)], 'survives_q10': rej[names.index(key)]}
    mt = {'variants': n_trials, 'bh_q10_survivors': [n for n, r in zip(names, rej) if r],
          'bh_q10_survivors_among_chosen': [n for n, r in zip(names, rej) if r and n in chosen_keys]}
    return blocks, fams, desc, mt, legs_all


# ============================================================================================== analysis: capacity

def capacity_section(snaps, blocks, oi):
    """Depth within 25bp on the side each leg trades (perp bids for the short, token asks for the purchase), open
    interest, and the marginal cost of the next $1M."""
    if not snaps:
        return {'note': 'no book snapshot'}
    at_, books = snaps[-1]
    tok_depth = {}
    for t, keys in BOOKS_OF_TOKEN.items():
        tot, per = 0.0, {}
        for k in keys:
            if k in books and books[k][0] and books[k][1]:
                bids, asks = books[k]
                mid = (bids[0][0] + asks[0][0]) / 2.0
                usd = depth_usd(asks, mid, 25)
                if 'USDC' in k or 'coinbase' in k or 'kraken' in k or ':USD' in k:
                    per[k] = usd
                else:
                    per[k] = usd
                tot += usd
        tok_depth[t] = {'ask_25bp_usd_total': tot, 'by_book': per}
    rows = []
    seen = set()
    for blk in blocks:
        perp, tok = blk.get('perp'), blk.get('token')
        if not perp or (perp, tok, blk['model']) in seen:
            continue
        seen.add((perp, tok, blk['model']))
        k = BOOK_OF_PERP.get(perp)
        if perp.startswith('hl:') and ('hl_coarse:' + perp[3:]) in books:
            k = 'hl_coarse:' + perp[3:]     # 20 levels at 4 significant figures reach past 25bp; the fine book does not
        pb = books.get(k)
        tb = books.get(BOOK_OF_TOKEN_LEG.get(tok))
        if not pb or not tb:
            rows.append({'perp': perp, 'token': tok, 'model': blk['model'], 'note': 'book missing'})
            continue
        pmid = (pb[0][0][0] + pb[1][0][0]) / 2.0
        tmid = (tb[0][0][0] + tb[1][0][0]) / 2.0
        perp_bid = depth_usd(pb[0], pmid, 25)
        tok_ask_venue = depth_usd(tb[1], tmid, 25)
        tok_ask_all = tok_depth[TOKEN_LEGS[tok]['token']]['ask_25bp_usd_total']
        oi_usd = oi.get(perp)
        size = min(x for x in (perp_bid, tok_ask_all if blk['model'] != 'collateral' else tok_ask_venue,
                               0.05 * oi_usd if oi_usd else None) if x is not None)
        ex = blk['out_of_sample'].get('ann_return')
        K = blk['capital_per_notional']
        # Marginal: the next $1M taken through both books beyond `size`, paid twice (in and out) and spread over a
        # year of holding, against the excess the $1M of notional would earn.
        c1 = walk_cost(pb[0], pmid, size + 1e6)
        c0 = walk_cost(pb[0], pmid, size) if size > 0 else 0.0
        t1 = walk_cost(tb[1], tmid, size + 1e6)
        t0 = walk_cost(tb[1], tmid, size) if size > 0 else 0.0
        marg_bp = None
        if None not in (c1, c0, t1, t0):
            marg_bp = ((c1 * (size + 1e6) - c0 * size) + (t1 * (size + 1e6) - t0 * size)) / 1e6
        rows.append({'perp': perp, 'token': tok, 'model': blk['model'], 'perp_bid_25bp_usd': perp_bid,
                     'token_ask_25bp_usd_same_venue': tok_ask_venue, 'token_ask_25bp_usd_all_venues': tok_ask_all,
                     'oi_usd': oi_usd, 'size_usd': size, 'test_excess_on_capital': ex,
                     'usd_per_year_at_size': (ex * K * size) if (ex is not None) else None,
                     'next_1m_extra_cost_bp_one_way': marg_bp,
                     'next_1m_net_excess_on_capital': ((ex * K - 2 * (marg_bp or 0) / 1e4) / K) if (
                         ex is not None and marg_bp is not None) else None})
    return {'snapshot_at': at_, 'token_depth': tok_depth, 'rows': rows}


def open_interest_usd(raw):
    """Open interest in USD per perp from the collect-time metadata."""
    oi = {}
    try:
        m = read_gz(raw / 'bn' / 'meta.json.gz')
        for s, o in m['openInterest'].items():
            px = fnum((m['premiumIndex'].get(s) or {}).get('markPrice'))
            if o and px:
                oi['bn:' + s] = fnum(o.get('openInterest'), 0.0) * px
    except (FileNotFoundError, KeyError):
        pass
    try:
        m = read_gz(raw / 'by' / 'meta.json.gz')
        for s, t in m['tickers'].items():
            lst = ((t or {}).get('result') or {}).get('list') or []
            if lst:
                oi['by:' + s] = fnum(lst[0].get('openInterestValue'), 0.0)
    except (FileNotFoundError, KeyError):
        pass
    try:
        m = read_gz(raw / 'okx' / 'meta.json.gz')
        for i, t in m['open_interest'].items():
            d = (t or {}).get('data') or []
            if d:
                oi['okx:' + i] = fnum(d[0].get('oiUsd'), 0.0)
    except (FileNotFoundError, KeyError):
        pass
    try:
        m = read_gz(raw / 'hl' / 'meta.json.gz')
        for k in ('core', 'xyz'):
            for p in m['perps'].get(k, []):
                oi['hl:' + p['name']] = fnum(p.get('openInterest'), 0.0) * fnum(p.get('oraclePx'), 0.0)
    except (FileNotFoundError, KeyError):
        pass
    return oi



# ============================================================================================== analysis: risks, checks

def weekend_basis(P, perp, tok_series):
    """Token-minus-perp basis change over each weekend close (spot shut), from the last open hour on Friday to one hour
    after the Sunday reopen: the hedge risk the weekend adds to an XAU-referenced short hedged with a token."""
    v, inst = perp.split(':', 1)
    F, T = P.get('%s:%s:trade' % (v, inst), {}), P.get(tok_series, {})
    hours = sorted(t for t in F if t in T)
    out, prev_open, start = [], None, None
    for t in hours:
        is_open = spot_open(t - HOUR_MS)
        if prev_open and not is_open and start is None:
            start = t - HOUR_MS if (t - HOUR_MS) in F and (t - HOUR_MS) in T else t
        if is_open and start is not None:
            end = t + HOUR_MS if (t + HOUR_MS) in F and (t + HOUR_MS) in T else t
            if end - start > 36 * HOUR_MS:          # weekends only, not the daily one-hour break
                b0 = T[start] / F[start] - 1.0
                b1 = T[end] / F[end] - 1.0
                out.append({'from': utc(start), 'to': utc(end), 'basis_change': b1 - b0,
                            'gold_move': F[end] / F[start] - 1.0})
            start = None
        prev_open = is_open
    ch = [x['basis_change'] for x in out]
    return {'weekends': len(out), 'basis_change': dist(ch),
            'worst5': sorted(out, key=lambda x: x['basis_change'])[:5]}


def regime_section(ev, P):
    """Funding against gold's own trend, by calendar month: does the carry need a gold bull market?"""
    gold = P.get('yahoo:PAXG-USD:1d', {})
    gd = {}
    for t, c in gold.items():
        gd[utc(t)[:7]] = c                         # last close of each month
    months = sorted(gd)
    ret = {m: gd[m] / gd[p] - 1.0 for p, m in zip(months, months[1:])}
    out = {}
    for m_ in ('by:PAXGUSDT', 'bn:PAXGUSDT', 'hl:PAXG', 'bn:XAUUSDT', 'hl:xyz:GOLD', 'by:XAUTUSDT'):
        rows = ev.get(m_)
        if not rows:
            continue
        h = settlement_hours(rows)
        mon = {}
        for t, r in rows:
            mon.setdefault(utc(t)[:7], []).append(r)
        apr = {k: sum(v) / len(v) * 8760.0 / h for k, v in mon.items() if len(v) * h >= 24 * 20}
        both = [(ret[k], apr[k]) for k in apr if k in ret]
        if len(both) < 6:
            continue
        up = [a for r, a in both if r > 0]
        dn = [a for r, a in both if r <= 0]
        out[m_] = {'months': len(both), 'corr_funding_vs_gold_month_return': ols_slope([r for r, _ in both],
                                                                                       [a for _, a in both])[1],
                   'mean_apr_gold_up_months': statistics.fmean(up) if up else None,
                   'mean_apr_gold_down_months': statistics.fmean(dn) if dn else None,
                   'n_up': len(up), 'n_down': len(dn),
                   'by_year_apr': {y: statistics.fmean([a for k, a in apr.items() if k.startswith(y)])
                                   for y in sorted({k[:4] for k in apr})}}
    yr = {}
    for t, c in gold.items():
        yr.setdefault(utc(t)[:4], []).append(c)
    out['_gold_by_year_return'] = {y: v[-1] / v[0] - 1.0 for y, v in sorted(yr.items()) if len(v) > 100}
    return out


def delisting_section(raw, ev, cut, P, desc):
    """The HIP-3 gold markets that were delisted: how long they lived, what they paid, how they ended."""
    out = []
    for c in ('km:GOLD', 'flx:GOLD', 'cash:GOLD', 'km:SILVER', 'flx:SILVER', 'cash:SILVER'):
        m = 'hl:' + c
        rows = ev.get(m) or []
        if not rows:
            continue
        tr = P.get('hl:%s:trade' % c, {})
        last_t = max(tr) if tr else None
        paxg = P.get('bn:spot:PAXGUSDT', {})
        end_basis = None
        if last_t and 'GOLD' in c:
            p = at(paxg, last_t, 3)
            end_basis = (p / tr[last_t] - 1.0) if p else None
        out.append({'market': m, 'first_funding': utc(rows[0][0]), 'last_trade': utc(cut.get(m)) if m in cut else None,
                    'days_live': (cut.get(m, rows[-1][0]) - rows[0][0]) / DAY_MS,
                    'funding_apr_while_live': funding_apr(rows), 'paxg_over_last_trade': end_basis})
    for d in desc:
        if d['perp'].startswith('hl:') and d.get('always_ann_excess') is not None:
            for o in out:
                if o['market'] == d['perp']:
                    o['carry_always_cash10_excess'] = d['always_ann_excess']
    meta_names = HL_DELISTED_NO_DATA
    return {'markets': out, 'delisted_without_history': meta_names,
            'note': 'live: xyz:GOLD and xyz:SILVER only; 6 gold and 6 silver HIP-3 markets on other builders are '
                    'flagged isDelisted in the venue metadata (2026-10-10)'}


def hl_formula(P_, mult, I8, band):
    """Hyperliquid hourly funding from the hour's average premium: mult x (P + clamp(I - P, +-band)) / 8."""
    return mult * (P_ + max(-band, min(band, I8 - P_))) / 8.0


def verify_section(raw, ev, prem):
    out = {}
    # 1. Hyperliquid funding fetched here vs the shared store fetched a day earlier (same endpoint, other session).
    for c in ('PAXG', 'xyz:GOLD', 'xyz:SILVER'):
        fp = ROOT / 'research/2026-10-09/perps_history/funding' / ('%s.json.gz' % safe(c))
        if not fp.exists():
            continue
        old = {int(round(int(r['time']) / HOUR_MS)): float(r['fundingRate']) for r in read_gz(fp)}
        new = {int(round(t / HOUR_MS)): r for t, r in ev.get('hl:' + c, [])}
        both = [h for h in old if h in new]
        diffs = [abs(old[h] - new[h]) for h in both]
        out['hl_store_vs_fresh:' + c] = {'overlap_hours': len(both), 'max_abs_diff': max(diffs) if diffs else None,
                                         'identical_share': sum(1 for x in diffs if x == 0) / len(diffs) if diffs
                                         else None}
    # 2. Binance funding vs the rent map's download (2026-10-10, earlier in the day).
    for s in BN_PERPS:
        fp = ROOT / 'research/2026-10-10/rent_map/raw/binance/funding' / ('%s.json.gz' % s)
        if not fp.exists():
            continue
        d = read_gz(fp)
        rows = d.get('rows', d) if isinstance(d, dict) else d
        old = {int(round(int(r['fundingTime']) / HOUR_MS)): float(r['fundingRate']) for r in rows}
        new = {int(round(t / HOUR_MS)): r for t, r in ev.get('bn:' + s, [])}
        both = [h for h in old if h in new]
        diffs = [abs(old[h] - new[h]) for h in both]
        out['bn_rent_map_vs_fresh:' + s] = {'overlap': len(both), 'max_abs_diff': max(diffs) if diffs else None}
    # 3. The headline funding (Hyperliquid PAXG and xyz:GOLD) recomputed from the premium with the venue formula.
    for c, mult, band in (('PAXG', 1.0, 0.0005), ('xyz:GOLD', 0.5, 0.0003), ('xyz:SILVER', 0.5, 0.0003)):
        fp = raw / 'hl' / ('funding_%s.json.gz' % safe(c))
        if not fp.exists():
            continue
        rows = read_gz(fp)
        ok = n = 0
        s_rep = s_hat = 0.0
        for r in rows:
            p, f = fnum(r.get('premium')), fnum(r.get('fundingRate'))
            if p is None or f is None:
                continue
            hat = hl_formula(p, mult, 0.0001, band)
            n += 1
            ok += 1 if abs(hat - f) <= 1e-7 else 0
            s_rep += f
            s_hat += hat
        out['hl_formula:' + c] = {'rows': n, 'within_0p001pct': ok / n if n else None,
                                  'apr_reported_mean': s_rep / n * 8760 if n else None,
                                  'apr_formula_mean': s_hat / n * 8760 if n else None}
    out['paxg_premium_three_paths'] = prem.get('_cross_check')
    return out



# ============================================================================================== analyze

def strip_private(x):
    if isinstance(x, dict):
        return {k: strip_private(v) for k, v in x.items() if not str(k).startswith('_') or k in (
            '_implied_carry', '_cross_check', '_gold_by_year_return', '_weekend_regimes',
            '_binance_xau_first_saturday_move')}
    if isinstance(x, list):
        return [strip_private(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x):
        return None
    return x


def collateral_terms(raw):
    out = {}
    try:
        m = read_gz(raw / 'bn' / 'meta.json.gz')
        out['binance_portfolio_margin'] = {a['asset']: fnum(a.get('collateralRate')) for a in m['pm_collateral']}
        out['binance_multi_assets_mode_has_gold'] = any('PAXG' in s or 'XAUT' in s for s in m['multi_assets_index'])
    except (FileNotFoundError, KeyError):
        pass
    try:
        m = read_gz(raw / 'by' / 'meta.json.gz')
        out['bybit_uta'] = {c: [(x.get('maxQty'), fnum(x.get('collateralRatio'))) for x in
                                ((((v or {}).get('result') or {}).get('list') or [{}])[0].get('collateralRatioList')
                                 or [])] for c, v in m['collateral'].items()}
    except (FileNotFoundError, KeyError):
        pass
    try:
        m = read_gz(raw / 'okx' / 'meta.json.gz')
        out['okx'] = {c: [(x.get('minAmt'), x.get('maxAmt'), fnum(x.get('discountRate'))) for x in
                          (((v or {}).get('data') or [{}])[0].get('details') or [])][:8]
                      for c, v in m['collateral'].items()}
    except (FileNotFoundError, KeyError):
        pass
    try:
        m = read_gz(raw / 'hl' / 'meta.json.gz')
        out['hyperliquid_spot_gold'] = [{'pair': p['name'], 'tokens': p.get('token_names'),
                                         'day_ntl_vlm': fnum(p.get('dayNtlVlm')), 'mark': fnum(p.get('markPx'))}
                                        for p in m.get('spot_pairs', [])]
        out['hyperliquid_portfolio_margin_collateral'] = ('BTC and HYPE only (docs read 2026-10-10, term_carry); '
                                                          'no gold token')
    except (FileNotFoundError, KeyError):
        pass
    return out


ISSUER_TERMS = {
    'PAXG': {
        'issuer': 'Paxos Trust Company (NYDFS-regulated); 1 PAXG = 1 fine troy oz in London Good Delivery bars',
        'redeem': 'Paxos account holders (onboarded, KYC) can sell PAXG to Paxos for USD at the gold price or take '
                  'allocated bars/unallocated gold; physical bars need about 430 oz plus fees (third-party guides; '
                  'the official minimums article was not read)',
        'fees': 'creation waived through 2027-01-01 (then 0.02 PAXG under 2 oz, 1.0% → 0.125% by size); redemption '
                '0.125% on the first $2M of 30-day net redemptions, 0.25% to $10M, 0.35% to $20M, 0.5% above '
                '(from 2026-09-01); in-kind conversion to bars 0.05%; no storage fee',
        'sources': ['https://support.paxos.com/articles/2899561282-PAX-Gold-Fees (read 2026-10-10)',
                    'https://www.paxos.com/pax-gold (read 2026-10-10)'],
    },
    'XAUT': {
        'issuer': 'TG Commodities Limited (Tether Gold); 1 XAUT = 1 troy oz in a Swiss vault',
        'redeem': 'verified TG Commodities customers (non-US); physical delivery to a Swiss address, minimum about '
                  '430 XAUT per third-party listings; USD redemption possible',
        'fees': '0.25% on creation and redemption plus a 150 USDT verification fee (third-party listings: rwa.xyz, '
                'MEXC; Tether\'s own terms page is script-rendered and was not read)',
        'sources': ['https://app.rwa.xyz/assets/tether-gold (search result, 2026-10-10)',
                    'https://gold.tether.to/ (no text served)'],
    },
}

API_GAPS = [
    'Spot XAU/USD history: Yahoo XAUUSD=X is gone (404) and Pyth Benchmarks history returns 401/404 without a key; '
    'Binance\'s XAU index (spot feeds dxFeed/Kaiko/Massive/Pyth plus xyz:GOLD) is the spot reference, GC=F the futures',
    'stooq.com serves a JavaScript proof-of-work page to scripts; not used',
    'OKX serves 3 months of funding history (from 2026-06-29) and XAU index candles from 2025-10-31 only',
    'Hyperliquid does not serve oracle history; its oracle is implied as close / (1 + hourly average premium)',
    'Hyperliquid PAXG funding history starts 2025-04-06 although daily candles start 2025-03-27',
    'HIP-3 hyna/mkts/vntl gold and silver markets (all delisted) return no funding or candles',
    'Binance TradFi perps (XAUUSDT) inside portfolio margin: not confirmed from public data; collateral rates are '
    'for the PM account (PAXG and XAUT 0.80)',
    'Bitfinex XAUT books are thin; Kraken/Coinbase PAXG books are USD-quoted (no stablecoin conversion applied)',
    'Tether Gold\'s official terms page renders by script; XAUT redemption terms are from third-party listings',
    'Book depth is one Saturday snapshot (2026-10-10); weekday books for the XAU perps were not read',
]


def token_section(raw, P):
    """Token-side facts: supply on Ethereum, the largest DEX pools (GeckoTerminal), and the issuer gate."""
    out = {}
    try:
        d = read_gz(raw / 'tokens' / 'onchain_pools.json.gz')
    except FileNotFoundError:
        return {'note': 'not collected'}
    px = {'PAXG': at(P.get('bn:spot:PAXGUSDT', {}), max(P.get('bn:spot:PAXGUSDT', {0: 0}))),
          'XAUT': at(P.get('bn:spot:XAUTUSDT', {}), max(P.get('bn:spot:XAUTUSDT', {0: 0})))}
    for tok, dec in (('PAXG', 18), ('XAUT', 6)):
        sup = d.get(tok, {}).get('totalSupply', {}).get('result')
        oz = int(sup, 16) / 10 ** dec if sup else None
        pools = []
        for p in ((d.get(tok + '_pools') or {}).get('data') or [])[:20]:
            a = p.get('attributes', {})
            pools.append({'name': a.get('name'), 'dex': ((p.get('relationships') or {}).get('dex') or {}).get(
                'data', {}).get('id'), 'reserve_usd': fnum(a.get('reserve_in_usd')),
                'volume_24h_usd': fnum((a.get('volume_usd') or {}).get('h24'))})
        pools.sort(key=lambda x: -(x['reserve_usd'] or 0))
        out[tok] = {'supply_oz_ethereum': oz, 'supply_usd_ethereum': oz * px[tok] if (oz and px[tok]) else None,
                    'dex_pools_top': pools[:8],
                    'dex_reserve_usd_top20': sum(x['reserve_usd'] or 0 for x in pools),
                    'dex_volume_24h_usd_top20': sum(x['volume_24h_usd'] or 0 for x in pools)}
    return out


PASS_RULES = {
    'min_oos_excess': 0.01,       # at least 1% a year over the savings rate on capital, out of sample
    'min_nw_t_30': 2.0,           # Newey-West t (30 lags) of the test-period daily excess
    'max_boot_p': 0.05,           # 30-day... 20-day block bootstrap: share of resampled means <= 0
    'bh_study_wide': True,        # survives Benjamini-Hochberg at q = 0.10 across all 168 variants' test p-values
    'both_test_halves_positive': True,
    'min_capacity_usd': 1e6,      # notional within 25bp on both legs (one-shot, Saturday books)
}


def verdicts(blocks, fams, cap):
    """Pre-committed go criteria (PASS_RULES) applied to every chosen variant."""
    caprow = {(r['perp'], r['token'], r['model']): r for r in cap.get('rows', [])}
    out = []
    for b in blocks + fams:
        c = b['_c']
        test = b['_series'][b['chosen']][c:]
        h = len(test) // 2
        halves = [ann_mean(test[:h]), ann_mean(test[h:])]
        cr = caprow.get((b.get('perp'), b.get('token'), b['model']), {})
        flags = {
            'oos_excess': (b['out_of_sample'].get('ann_return') or -1) >= PASS_RULES['min_oos_excess'],
            'nw_t_30': (b['oos_t_nw30'] or 0) >= PASS_RULES['min_nw_t_30'],
            'bootstrap': (b['test_block_bootstrap'].get('p_le_0') if b['test_block_bootstrap'].get('p_le_0')
                          is not None else 1) <= PASS_RULES['max_boot_p'],
            'bh_study_wide': bool(b['bh_study_wide']['survives_q10']),
            'both_test_halves_positive': all(x is not None and x > 0 for x in halves),
            'capacity': (cr.get('size_usd') or 0) >= PASS_RULES['min_capacity_usd'] if cr else None,
        }
        out.append({'name': b['name'], 'model': b['model'], 'chosen': b['chosen'],
                    'oos_excess': b['out_of_sample'].get('ann_return'), 'test_halves_excess': halves,
                    'flags': flags, 'passes': all(v for v in flags.values() if v is not None) and
                    flags['capacity'] is not False})
    return out


def headline_check(P, ev, blocks, name='hl:xyz:GOLD x PAXG@bn', model='cash10'):
    """The headline block's test-period funding and basis recomputed from the raw rows and hourly closes, outside the
    simulator."""
    b = next((x for x in blocks if x['name'] == name and x['model'] == model), None)
    if not b:
        return None
    perp = b['perp']
    v, inst = perp.split(':', 1)
    s0 = ms_of(b['split_day']) // DAY_MS
    s1 = ms_of(b['last_day']) // DAY_MS
    rows = [(t, r) for t, r in ev[perp] if s0 * DAY_MS < t <= (s1 + 1) * DAY_MS]
    F, T = P['%s:%s:trade' % (v, inst)], P[TOKEN_LEGS[b['token']]['series']]
    Fa, Ta = at(F, s0 * DAY_MS), at(T, s0 * DAY_MS)
    Fb, Tb = at(F, (s1 + 1) * DAY_MS), at(T, (s1 + 1) * DAY_MS)
    yrs = (s1 - s0 + 1) / 365.0
    leg_days = b['_days'][b['_c']:]
    return {'block': name, 'model': model, 'window': [b['split_day'], b['last_day']],
            'funding_apr_from_raw_rows': sum(r for _, r in rows) / yrs,
            'basis_change_from_hourly_closes': (Tb / Fb - 1.0) - (Ta / Fa - 1.0),
            'excess_before_rebalancing_costs': ((sum(r for _, r in rows) + (Tb / Fb - Ta / Fa) - 2 * 0.00095)
                                                / b['capital_per_notional'] / yrs - SSR),
            'simulator_oos_excess': b['out_of_sample'].get('ann_return'), 'test_days': len(leg_days)}


def cmd_analyze(args):
    out = Path(args.out)
    raw = out / 'raw'
    t0 = time.time()
    P, H = load_prices(raw)
    ev, cut = load_funding(raw)
    snaps = latest_books(raw)
    books_now = snaps[-1][1] if snaps else {}
    cost_perp, cost_tok, costs_used = leg_costs(books_now)
    res = {'generated': utc(), 'ssr': SSR, 'savings_by_year': SAVINGS_BY_YEAR, 'api_gaps': API_GAPS,
           'issuer_terms': ISSUER_TERMS, 'collateral': collateral_terms(raw), 'costs_one_side': costs_used}
    res['oracle'] = oracle_check(P, H, raw)
    res['funding'] = funding_table(ev, cut)
    res['oracle']['_weekend_regimes']['funding_by_index_regime'] = index_regime_funding(
        ev, res['oracle']['_weekend_regimes'].get('_binance_xau_first_saturday_move'))
    prem = premium_paths(P, raw)
    res['premium'] = prem
    blocks, fams, desc, mt, legs_all = carry_section(P, H, ev, cut, cost_perp, cost_tok)
    res['carry'] = blocks
    res['families'] = fams
    res['descriptive'] = desc
    res['multiple_testing'] = mt
    oi = open_interest_usd(raw)
    res['open_interest_usd'] = oi
    res['books'] = book_table(snaps)
    res['capacity'] = capacity_section(snaps, blocks, oi)
    res['risks'] = {
        'weekend_basis': {'%s x %s' % (p, t): weekend_basis(P, p, TOKEN_LEGS[t]['series'])
                          for p, t in (('bn:XAUUSDT', 'PAXG@bn'), ('hl:xyz:GOLD', 'PAXG@bn'),
                                       ('by:XAUUSDT', 'XAUT@by'), ('bn:PAXGUSDT', 'PAXG@bn'),
                                       ('hl:PAXG', 'PAXG@bn'))},
        'regime': regime_section(ev, P),
        'delistings': delisting_section(raw, ev, cut, P, desc),
    }
    res['verify'] = verify_section(raw, ev, prem)
    res['verify']['headline_recomputed'] = headline_check(P, ev, blocks)
    res['tokens'] = token_section(raw, P)
    res['pass_rules'] = PASS_RULES
    res['verdicts'] = verdicts(blocks, fams, res['capacity'])
    res['seconds'] = round(time.time() - t0, 1)
    write_json(out / 'analysis.json', strip_private(res))
    print(json.dumps({'blocks': len(blocks), 'families': len(fams), 'seconds': res['seconds']}))
    return res


def pc(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def bp(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f') % (1e4 * x)


def nm(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


def usd(x):
    if x is None:
        return '—'
    a = abs(x)
    if a >= 1e9:
        return '$%.2fB' % (x / 1e9)
    if a >= 1e6:
        return '$%.2fM' % (x / 1e6)
    if a >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '|'.join('---' for _ in head) + '|']
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)


def file_inventory(raw):
    inv = {}
    for fp in sorted(raw.rglob('*.json.gz')):
        rel = str(fp.relative_to(raw))
        try:
            d = read_gz(fp)
        except Exception:  # noqa: BLE001
            inv[rel] = {'error': 'unreadable'}
            continue
        rows = d.get('rows') if isinstance(d, dict) and 'rows' in d else d
        rec = {'bytes': fp.stat().st_size}
        if isinstance(rows, list) and rows:
            t = [r[0] if isinstance(r, list) else (r.get('t') or r.get('time')) for r in rows
                 if isinstance(r, (list, dict))]
            t = [int(x) for x in t if x is not None]
            rec.update({'rows': len(rows), 'first': utc(min(t)) if t else None, 'last': utc(max(t)) if t else None})
        inv[rel] = rec
    return inv


def cmd_render(args):
    out = Path(args.out)
    a = json.loads((out / 'analysis.json').read_text())
    L = ['# Gold carry: long tokenized gold, short the metal perp — tables (%s)' % a['generated'][:10], '',
         'Every number below is in `analysis.json`; benchmark SSR %s a year on capital unless noted.' % pc(a['ssr'])]
    # 1. verdicts
    caps = {(r['perp'], r['token'], r['model']): r for r in a['capacity'].get('rows', [])}
    blocks = {(b['name'], b['model']): b for b in a['carry'] + a['families']}
    rows = []
    for v in a['verdicts']:
        b = blocks[(v['name'], v['model'])]
        cr = caps.get((b.get('perp'), b.get('token'), b['model']), {})
        bt = b['test_block_bootstrap']
        rows.append([v['name'], v['model'], nm(b['capital_per_notional']), v['chosen'],
                     '%s→%s' % (b['split_day'], b['last_day']), pc(b['in_sample']['ann_return']),
                     pc(v['oos_excess']), nm(b['oos_t_nw30']), nm(bt.get('p_le_0'), 3),
                     nm(b['bh_study_wide']['adjusted_p'], 2), ' / '.join(pc(x) for x in v['test_halves_excess']),
                     usd(cr.get('size_usd')), usd(cr.get('usd_per_year_at_size')), 'yes' if v['passes'] else 'no'])
    L += ['', '## 1. Verdicts (pre-committed go rules: %s)' % json.dumps(a['pass_rules']), '',
          table(['series', 'capital', 'K', 'chosen rule', 'test window', 'excess in sample', 'excess out of sample',
                 'NW t (30)', 'bootstrap p≤0', 'BH adj p (168)', 'test halves', 'size (25bp)', '$/yr at size',
                 'go'], rows)]
    # 2. oracle
    o = a['oracle']
    wk = o.get('_weekend_regimes', {})
    rows = []
    for m, r in o.items():
        if m.startswith('_'):
            continue
        w = wk.get(m, {})
        rows.append([m, bp(r['vs_front_future_open_hours'].get('median')),
                     '%s / %s' % (bp(r['vs_front_future_open_hours'].get('p05')),
                                  bp(r['vs_front_future_open_hours'].get('p95'))),
                     bp(r['vs_paxg_open_hours'].get('median')), bp(r['daily_median_sd_vs_future']),
                     bp(r['daily_median_sd_vs_paxg']), len(r['steps_vs_future_gt25bp']),
                     len(r['steps_vs_paxg_gt25bp']), nm(r['open_hours']['slope_index_on_perp']),
                     nm(r['closed_hours']['slope_index_on_perp']), pc(r['closed_hours']['share_frozen_lt_0p1bp'], 0),
                     w.get('first_month_moving') or '—'])
    L += ['', '## 2. What each index tracks (US-session hours unless noted; bp)', '',
          table(['market', 'index/GC=F median', 'p05 / p95', 'index/PAXG median', 'sd of daily median vs GC',
                 'vs PAXG', 'steps >25bp vs GC', 'vs PAXG', 'slope on own perp (open)', '(shut)', 'shut hours frozen',
                 'weekends moving since'], rows),
          '', 'Binance XAU index first moved on a Saturday at %s.' % o.get('_weekend_regimes', {}).get(
              '_binance_xau_first_saturday_move')]
    ic = o['_implied_carry']
    L += ['', '### Cost of carry implied by COMEX (USD rate − lease, incl. any COMEX premium over London)', '',
          table(['roll day', 'from', 'to', 'step of PAXG/GC=F (bp)', 'months', 'implied carry a year'],
                [[r['day'], r['from'], r['to'], bp(r['step']), r['months'], pc(r['implied_carry_apr'])]
                 for r in ic['rolls']]),
          '', 'Median of rolls since 2025-12: %s; level method over the last 60 days: %s (median).' % (
              pc(ic['recent_rolls_median']), pc(ic['level_last_60d'].get('median')))]
    # 3. funding
    rows = []
    for m, r in a['funding'].items():
        rows.append([m, r['first'][:10], (r['delisted_at'] or '')[:10], nm(r['interval_h'], 0),
                     pc(r['apr_since_listing']), pc(r['apr_first_half']), pc(r['apr_second_half']),
                     pc(r['apr_last_90d']), pc(r['apr_last_30d']), pc(r['apr_spot_open']), pc(r['apr_spot_shut']),
                     '%s at %s' % (pc(r['share_at_mode'], 0), pc(r['mode_apr'])), pc(r['share_negative'], 0)])
    L += ['', '## 3. Funding a short receives (annualised from what was paid)', '',
          table(['market', 'first', 'delisted', 'interval h', 'since listing', 'first half', 'second half',
                 'last 90d', 'last 30d', 'spot open', 'spot shut', 'modal rate (floor)', 'negative'], rows)]
    # 4. premium
    rows = []
    for k, r in a['premium'].items():
        if k.startswith('_'):
            continue
        oh, ch, dc = r['open_hours'], r['closed_hours'], r['daily_median_change']
        rows.append([k, oh.get('n'), bp(oh.get('median')), bp(oh.get('p05')), bp(oh.get('p95')), bp(oh.get('min')),
                     bp(oh.get('max')), bp(ch.get('median')), bp(dc.get('sd'))])
    cc = a['premium']['_cross_check']
    L += ['', '## 4. Token premium over spot gold (bp)', '',
          table(['path', 'open hours', 'median', 'p05', 'p95', 'min', 'max', 'median while spot shut',
                 'sd of daily change'], rows),
          '', 'Cross-check on the %d common days %s→%s: medians %s; daily correlation Binance vs Coinbase/xyz %s, '
              'vs OKX %s.' % (cc['days'], cc['first'], cc['last'],
                              ', '.join('%s %s' % (k.split(' /')[0], bp(v)) for k, v in
                                        cc['median_of_daily_medians'].items()),
                              nm(cc['corr_daily_binance_vs_coinbase']), nm(cc['corr_daily_binance_vs_okx']))]
    mrows = []
    for k, r in a['premium'].items():
        if k.startswith('_') or not k.startswith('PAXG@binance') and not k.startswith('XAUT@okx'):
            continue
        mrows.append([k] + ['%s %s' % (m, bp(v, 0)) for m, v in r['by_month_median'].items()])
    L += ['', 'Monthly medians:', ''] + ['- ' + ' · '.join(r) for r in mrows]
    # 5. carry details
    rows = []
    for b in a['carry'] + a['families']:
        dcp = b.get('decomposition_always_gross') or {}
        rows.append([b['name'], b['model'], pc(dcp.get('funding_apr')), pc(dcp.get('basis_apr')),
                     pc(b['variants_train_ann']['always']), pc(b['variants_test_ann']['always']),
                     pc(b['always_last_90d_ann']), ', '.join('%s %s' % (y, pc(v)) for y, v in
                                                             b['always_by_year_ann'].items()),
                     b['bookkeeping_always']['rebalances'], b['bookkeeping_always']['liq_near'],
                     pc(b['test_hist_benchmark_ann']), nm(b['deflated_sharpe_study_wide'])])
    L += ['', '## 5. Always-on detail (gross per notional; excess on capital)', '',
          table(['series', 'capital', 'funding', 'basis change', 'always, first half', 'always, second half',
                 'last 90d', 'by year', 'rebalances', 'days near liquidation', 'chosen vs savings rate paid',
                 'deflated Sharpe (168 trials)'], rows)]
    rows = [[d['perp'], d['token'], d.get('model', ''), '%s→%s' % (d.get('first_day', ''), d.get('last_day', '')),
             pc((d.get('decomposition_always_gross') or {}).get('funding_apr')),
             pc((d.get('decomposition_always_gross') or {}).get('basis_apr')), pc(d.get('always_ann_excess')),
             nm(d.get('nw_t'))] for d in a['descriptive']]
    L += ['', 'Descriptive only (too short to split, or delisted):', '',
          table(['perp', 'token', 'capital', 'window', 'funding', 'basis', 'always excess', 'NW t'], rows)]
    # 6. capacity
    cap = a['capacity']
    rows = [[r['perp'], r['token'], r['model'], usd(r.get('perp_bid_25bp_usd')),
             usd(r.get('token_ask_25bp_usd_same_venue')), usd(r.get('token_ask_25bp_usd_all_venues')),
             usd(r.get('oi_usd')), usd(r.get('size_usd')), pc(r.get('test_excess_on_capital')),
             usd(r.get('usd_per_year_at_size')), nm(r.get('next_1m_extra_cost_bp_one_way'), 0),
             pc(r.get('next_1m_net_excess_on_capital'))] for r in cap.get('rows', [])]
    L += ['', '## 6. Capacity (books at %s, a Saturday)' % cap.get('snapshot_at'), '',
          table(['perp', 'token', 'capital', 'perp bids ≤25bp', 'token asks ≤25bp (venue)', '(all venues)',
                 'open interest', 'size', 'test excess', '$/yr at size', 'next $1M extra cost bp (one way)',
                 'next $1M excess (1-yr hold)'], rows)]
    tdp = cap.get('token_depth', {})
    L += ['', 'Token asks within 25bp: ' + '; '.join('%s %s (%s)' % (t, usd(v['ask_25bp_usd_total']), ', '.join(
        '%s %s' % (k, usd(x)) for k, x in v['by_book'].items())) for t, v in tdp.items())]
    # 7. late entry
    rows = [[b['name'], b['model'], b['chosen'], pc(b['late_entry']['test_excess']),
             pc(b['late_entry']['late_1hour_excess']), pc(b['late_entry']['late_1day_excess']),
             nm(b['late_entry']['kept_1hour']), nm(b['late_entry']['kept_1day'])] for b in a['carry'] + a['families']]
    L += ['', '## 7. Late entry (test period)', '',
          table(['series', 'capital', 'rule', 'on time', '1 hour late', '1 day late', 'kept (1h)', 'kept (1d)'], rows)]
    # 8. risks
    rk = a['risks']
    rows = [[k, v['weekends'], bp(v['basis_change'].get('median')), bp(v['basis_change'].get('p05')),
             bp(v['basis_change'].get('p95')), bp(v['basis_change'].get('min')), bp(v['basis_change'].get('sd'))]
            for k, v in rk['weekend_basis'].items()]
    L += ['', '## 8. Risks', '', 'Weekend change of the token-minus-perp basis (Friday close → one hour after the '
          'Sunday reopen, bp):', '', table(['pair', 'weekends', 'median', 'p05', 'p95', 'worst', 'sd'], rows)]
    rg = rk['regime']
    rows = [[m, v['months'], nm(v['corr_funding_vs_gold_month_return']), pc(v['mean_apr_gold_up_months']),
             pc(v['mean_apr_gold_down_months']), ', '.join('%s %s' % (y, pc(x)) for y, x in v['by_year_apr'].items())]
            for m, v in rg.items() if not m.startswith('_')]
    L += ['', 'Funding against gold\'s own monthly return (gold by year: %s):' % ', '.join(
        '%s %s' % (y, pc(x, 0)) for y, x in rg.get('_gold_by_year_return', {}).items()), '',
          table(['market', 'months', 'corr', 'mean APR, gold up months', 'down months', 'by year'], rows)]
    dl = rk['delistings']
    rows = [[x['market'], x['first_funding'][:10], (x['last_trade'] or '')[:10], nm(x['days_live'], 0),
             pc(x['funding_apr_while_live']), bp(x.get('paxg_over_last_trade')),
             pc(x.get('carry_always_cash10_excess'))] for x in dl['markets']]
    L += ['', 'Delisted HIP-3 metal markets (%s; no data served for %s):' % (dl['note'], ', '.join(
        dl['delisted_without_history'])), '',
          table(['market', 'first funding', 'last trade', 'days live', 'funding while live',
                 'PAXG over last trade (bp)', 'carry excess (always, cash10)'], rows)]
    # 9. collateral, issuers, tokens
    col = a['collateral']
    L += ['', '## 9. Collateral, issuers, token supply', '',
          '- Binance portfolio margin collateral rates: %s; multi-assets mode lists gold: %s' % (
              json.dumps(col.get('binance_portfolio_margin')), col.get('binance_multi_assets_mode_has_gold')),
          '- Bybit UTA tiers (max qty, ratio): %s' % json.dumps(col.get('bybit_uta')),
          '- OKX tiers (min, max, discount): %s' % json.dumps(col.get('okx')),
          '- Hyperliquid: %s; HyperCore spot gold pairs: %s' % (
              col.get('hyperliquid_portfolio_margin_collateral'), json.dumps(col.get('hyperliquid_spot_gold')))]
    for t, v in a['issuer_terms'].items():
        L += ['- %s: %s. Redeem: %s. Fees: %s.' % (t, v['issuer'], v['redeem'], v['fees'])]
    for t, v in a['tokens'].items():
        if isinstance(v, dict) and 'supply_oz_ethereum' in v:
            L += ['- %s on Ethereum: %s oz (%s); top-20 DEX pools hold %s, trade %s a day; largest: %s' % (
                t, nm(v['supply_oz_ethereum'], 0), usd(v['supply_usd_ethereum']), usd(v['dex_reserve_usd_top20']),
                usd(v['dex_volume_24h_usd_top20']), '; '.join('%s %s %s' % (p['name'], p['dex'], usd(p['reserve_usd']))
                                                               for p in v['dex_pools_top'][:4]))]
    # 10. verification and gaps
    L += ['', '## 10. Verification', '', '```', json.dumps(a['verify'], indent=1), '```', '',
          '## 11. API gaps', ''] + ['- ' + g for g in a['api_gaps']]
    L += ['', 'Multiple testing: %d variants; BH q=0.10 survivors: %s; among chosen: %s.' % (
        a['multiple_testing']['variants'], ', '.join(a['multiple_testing']['bh_q10_survivors']) or 'none',
        ', '.join(a['multiple_testing']['bh_q10_survivors_among_chosen']) or 'none')]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    raw = out / 'raw'
    log = json.loads((out / 'collect_log.json').read_text()) if (out / 'collect_log.json').exists() else {}
    man = {'generated': utc(), 'study': 'gold_carry', 'script': 'scripts/gold_carry.py',
           'commands': ['python3 scripts/gold_carry.py collect --out %s --parts bn,by,okx,yahoo,tokens' % args.out,
                        'python3 scripts/gold_carry.py collect --out %s --parts hl' % args.out,
                        'python3 scripts/gold_carry.py collect --out %s --parts books' % args.out,
                        'python3 scripts/gold_carry.py analyze --out %s' % args.out,
                        'python3 scripts/gold_carry.py render --out %s' % args.out],
           'endpoints': {'binance_futures': BN_F + ' (/fapi/v1/fundingRate, klines, premiumIndexKlines, '
                                                  'indexPriceKlines, markPriceKlines, constituents, depth, openInterest)',
                         'binance_spot': BN_S + ' (/api/v3/klines, depth)',
                         'binance_pm_collateral': 'https://www.binance.com/bapi/margin/v1/public/margin/portfolio/'
                                                  'collateral-rate',
                         'bybit': BY + ' (/v5/market/funding/history, kline, mark/index/premium-index-price-kline, '
                                       'index-price-components, orderbook, spot-margin-trade/collateral)',
                         'okx': OKX + ' (/api/v5/public/funding-rate-history, market/history-candles, '
                                      'history-index-candles, history-mark-price-candles, index-components, books, '
                                      'discount-rate-interest-free-quota)',
                         'hyperliquid': 'https://api.hyperliquid.xyz/info (fundingHistory, candleSnapshot, l2Book, '
                                        'metaAndAssetCtxs, spotMetaAndAssetCtxs, perpDexs, meta) at >= 1.5 s a call',
                         'yahoo': YAHOO + ' (GC=F, SI=F, PAXG-USD, XAUT-USD)',
                         'coinbase': 'https://api.exchange.coinbase.com/products/PAXG-USD (candles, book)',
                         'kraken': 'https://api.kraken.com/0/public/Depth?pair=PAXGUSD',
                         'bitfinex': 'https://api-pub.bitfinex.com/v2/book/tXAUT:USD|UST',
                         'geckoterminal': GT + '/networks/eth/tokens/{PAXG,XAUT}/pools',
                         'ethereum_rpc': 'publicnode (totalSupply)'},
           'issuer_pages': {t: v['sources'] for t, v in a['issuer_terms'].items()},
           'files': file_inventory(raw), 'collect_log': log, 'api_gaps': a['api_gaps'],
           'analysis_seconds': a.get('seconds')}
    write_json(out / 'manifest.json', man)
    print('wrote tables.md (%d lines) and manifest.json' % len(L))

# ============================================================================================== entry point

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--out', default='research/2026-10-10/gold_carry')
    c.add_argument('--parts', default='bn,by,okx,yahoo,tokens')
    c.add_argument('--refresh', action='store_true')
    c.set_defaults(fn=cmd_collect)
    a = sub.add_parser('analyze')
    a.add_argument('--out', default='research/2026-10-10/gold_carry')
    a.set_defaults(fn=lambda args: cmd_analyze(args))
    r = sub.add_parser('render')
    r.add_argument('--out', default='research/2026-10-10/gold_carry')
    r.set_defaults(fn=lambda args: cmd_render(args))
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == '__main__':
    main()
