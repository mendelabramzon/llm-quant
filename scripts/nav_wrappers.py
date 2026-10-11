#!/usr/bin/env python3
"""Wrappers that trade away from what they hold: OTC crypto trusts and digital asset treasury companies (DATs).

Why. A vehicle that holds a coin but cannot be redeemed by its holders can trade far from the value of what it holds.
Holders who need out sell at a discount; the discount closes on a dated or semi-dated catalyst (conversion to an ETF, a
buyback funded by selling the coin, a merger, a liquidation or a tender). Buying the discount with the coin hedged is
a trade whose counterparty has a non-price motive (a holder who cannot redeem and will not wait), which is the kind of
edge this repo has found to survive. The question: does it pay above the savings rate, net of fees, funding and
borrow, and are there live candidates on 2026-10-10?

  (a) **Trusts.** Grayscale's single-asset trusts, Osprey's and Bitwise's OTC funds. Coin per share is read from each
      trust's own 10-Q/10-K XBRL (`InvestmentOwnedBalanceContracts` / `SharesOutstanding`, point in time by filing
      date) and carried between filings by the sponsor fee (the only thing that moves it while creations are shut).
      NAV per share = coin per share x the coin's Binance price at the US close (16:00 New York). Events (filing,
      approval, first exchange trading day) are hand-curated with sources in `curated.json`. Trade: long the trust,
      short the coin perp (Binance funding), from the filing or from a discount trigger, to conversion.
  (b) **DATs.** Look-through NAV per share = (coin holdings x price + cash - debt - preferred liquidation preference)
      / diluted shares, with convertibles counted as shares when in the money and as debt otherwise. Holdings:
      StrategyTracker's daily ledger (20 BTC treasuries, each row linked to its statement) and CoinGecko's weekly
      holdings chart (last 365 days, every coin); cash, debt and shares from XBRL company facts (point in time by
      filing date); preferred stock and convertibles hand-curated where XBRL drops them (dimensioned facts). Three
      ratios: naive mNAV (market cap / coin value, what most dashboards show), EV mNAV (Strategy's definition), true
      mNAV (price / look-through NAV per share). Tests: does a deep true discount predict convergence over 1-3 months
      with the coin hedged; event study on buybacks, coin sales, mergers and activists.

Conventions. Dates are UTC calendar days; a stock's close is 16:00 New York and the coin price paired with it is the
Binance close of the hour ending at that time. Discount = price / NAV - 1 (negative = discount). Hedged return of a
long position of 1 share with h coins short: [P1 - P0 - h (C1 - C0) + h * sum(funding * C)] / capital, capital = P0 +
margin of the short (default 1/3 of its notional). Everything is chosen on earlier events and tested once on later
ones through `backtest.py`.

    python3 scripts/nav_wrappers.py collect --parts yahoo,sec,binance,funding,coingecko,strategytracker,strategy
    python3 scripts/nav_wrappers.py analyze
    python3 scripts/nav_wrappers.py render

Network etiquette: Yahoo with UA 'Mozilla/5.0'; SEC data.sec.gov / efts with UA 'llm-quant research' (no e-mail; the
www.sec.gov document archive refuses that UA, so filing texts are read from press releases instead, recorded as a gap);
CoinGecko public API at >= 7 s a call; Binance public endpoints at ~4 calls a second.
"""
import argparse
import datetime as dt
import gzip
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'research' / '2026-10-10' / 'nav_wrappers'
RAW = OUT / 'raw'
UTC = dt.timezone.utc
NY = ZoneInfo('America/New_York')
UA_WEB = 'Mozilla/5.0'
UA_SEC = 'llm-quant research'
YAHOO = 'https://query1.finance.yahoo.com/v8/finance/chart/'
BN_SPOT = 'https://api.binance.com/api/v3/klines'
BN_PERP = 'https://fapi.binance.com/fapi/v1/klines'
BN_FUND = 'https://fapi.binance.com/fapi/v1/fundingRate'
CG = 'https://api.coingecko.com/api/v3/'
SEC_DATA = 'https://data.sec.gov/'
TODAY = '2026-10-10'

# Binance symbols for each coin: spot first, then the USD-M perp (a few coins only trade as a perp, or as 1000x).
COIN_SYMBOLS = {
    'BTC': ('BTCUSDT', 'BTCUSDT'), 'ETH': ('ETHUSDT', 'ETHUSDT'), 'ETC': ('ETCUSDT', 'ETCUSDT'),
    'BCH': ('BCHUSDT', 'BCHUSDT'), 'LTC': ('LTCUSDT', 'LTCUSDT'), 'ZEC': ('ZECUSDT', 'ZECUSDT'),
    'XLM': ('XLMUSDT', 'XLMUSDT'), 'SOL': ('SOLUSDT', 'SOLUSDT'), 'LINK': ('LINKUSDT', 'LINKUSDT'),
    'TAO': ('TAOUSDT', 'TAOUSDT'), 'ZEN': ('ZENUSDT', 'ZENUSDT'), 'MANA': ('MANAUSDT', 'MANAUSDT'),
    'FIL': ('FILUSDT', 'FILUSDT'), 'LPT': ('LPTUSDT', 'LPTUSDT'), 'BAT': ('BATUSDT', 'BATUSDT'),
    'NEAR': ('NEARUSDT', 'NEARUSDT'), 'STX': ('STXUSDT', 'STXUSDT'), 'BNB': ('BNBUSDT', 'BNBUSDT'),
    'BONK': ('BONKUSDT', '1000BONKUSDT'), 'XRP': ('XRPUSDT', 'XRPUSDT'), 'ADA': ('ADAUSDT', 'ADAUSDT'),
    'AVAX': ('AVAXUSDT', 'AVAXUSDT'), 'DOGE': ('DOGEUSDT', 'DOGEUSDT'), 'SUI': ('SUIUSDT', 'SUIUSDT'),
    'TON': ('TONUSDT', 'TONUSDT'), 'TRX': ('TRXUSDT', 'TRXUSDT'), 'HYPE': (None, 'HYPEUSDT'),
    'WLFI': ('WLFIUSDT', 'WLFIUSDT'), 'ENA': ('ENAUSDT', 'ENAUSDT'), 'WLD': ('WLDUSDT', 'WLDUSDT'),
    'UNI': ('UNIUSDT', 'UNIUSDT'), 'AAVE': ('AAVEUSDT', 'AAVEUSDT'), 'DOT': ('DOTUSDT', 'DOTUSDT'),
}
PERP_MULT = {'BONK': 1000.0}          # 1000BONKUSDT quotes 1000 coins
CG_COIN_IDS = {'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'BNB': 'binancecoin', 'HYPE': 'hyperliquid',
               'SUI': 'sui', 'TON': 'the-open-network', 'TRX': 'tron', 'WLFI': 'world-liberty-financial',
               'LTC': 'litecoin', 'AVAX': 'avalanche-2', 'DOGE': 'dogecoin', 'WLD': 'worldcoin-wld',
               'ENA': 'ethena', 'XRP': 'ripple'}
EXTRA_YAHOO = ['IBIT', 'ETHA', 'BTC-USD', 'ETH-USD', 'JPY=X', 'EURUSD=X', 'GBPUSD=X', 'SEK=X', 'SVIA', 'TSWCF',
               'MTPLF', 'SMLR', 'ETHZ', 'STSS', 'SLMT', 'KIDZ', 'GAME', 'ABTC', 'VVPR', 'STRC', 'STRK', 'STRF',
               'STRD', 'SATA']


# ---------------------------------------------------------------------------------------------- small utilities

def ymd(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, UTC).strftime('%Y-%m-%d')


def day_ms(s):
    return int(dt.datetime.strptime(s[:10], '%Y-%m-%d').replace(tzinfo=UTC).timestamp() * 1000)


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


def http_json(url, params=None, ua=UA_WEB, retries=5, pause=0.25, timeout=60, rate_wait=60.0):
    if params:
        url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
    last = None
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': 'application/json',
                                                       'Accept-Encoding': 'gzip'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    body = gzip.decompress(body)
                d = json.loads(body.decode())
            time.sleep(pause)
            return d
        except urllib.error.HTTPError as e:
            last = 'HTTP %s' % e.code
            if e.code in (400, 404):
                time.sleep(pause)
                return {'_http_error': e.code}
            wait = rate_wait if e.code in (418, 429) else pause * 2 ** (a + 1)
            time.sleep(min(wait, 120.0))
        except Exception as e:  # noqa: BLE001 - transport errors are retried, then raised with context
            last = repr(e)[:160]
            time.sleep(pause * 2 ** (a + 1))
    raise RuntimeError('%s: %s' % (url[:160], last))


def load_universe():
    return json.loads((OUT / 'universe.json').read_text())


def load_curated():
    p = OUT / 'curated.json'
    return json.loads(p.read_text()) if p.exists() else {}


# ---------------------------------------------------------------------------------------------- collectors

def collect_yahoo(force=False, log=print):
    u = load_universe()
    syms = [t['ticker'] for t in u['trusts']] + [d['yahoo'] for d in u['dats']] + EXTRA_YAHOO
    out = {}
    for s in dict.fromkeys(syms):
        p = RAW / 'yahoo' / ('%s.json.gz' % s.replace('=', '_'))
        if p.exists() and not force:
            continue
        d = http_json(YAHOO + urllib.parse.quote(s), {'period1': 1420070400, 'period2': int(time.time()),
                                                       'interval': '1d', 'events': 'div,split'}, pause=0.6)
        r = ((d.get('chart') or {}).get('result') or [None])[0] if isinstance(d, dict) else None
        if not r or not r.get('timestamp'):
            out[s] = 'no data'
            log('yahoo %s: no data' % s)
            continue
        q = r['indicators']['quote'][0]
        adj = (r['indicators'].get('adjclose') or [{}])[0].get('adjclose')
        rows = []
        for i, t in enumerate(r['timestamp']):
            c = q['close'][i]
            if c is None:
                continue
            rows.append([dt.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%d'), q['open'][i], q['high'][i],
                         q['low'][i], c, q['volume'][i], adj[i] if adj else None])
        ev = r.get('events') or {}
        write_gz(p, {'symbol': s, 'meta': {k: r['meta'].get(k) for k in ('currency', 'exchangeName', 'instrumentType',
                                                                            'longName', 'shortName', 'timezone',
                                                                            'exchangeTimezoneName')},
                     'rows': rows, 'splits': sorted((ev.get('splits') or {}).values(), key=lambda x: x['date']),
                     'dividends': sorted((ev.get('dividends') or {}).values(), key=lambda x: x['date']),
                     'fetched': dt.datetime.now(UTC).isoformat(timespec='seconds')})
        out[s] = len(rows)
        log('yahoo %s: %d rows' % (s, len(rows)))
    return out


def collect_yahoo_intraday(symbols, force=False, log=print):
    """60-minute bars for the last 730 days (Yahoo's limit): used for the 1-hour-late column."""
    out = {}
    for s in symbols:
        p = RAW / 'yahoo_1h' / ('%s.json.gz' % s)
        if p.exists() and not force:
            continue
        now = int(time.time())
        d = http_json(YAHOO + urllib.parse.quote(s), {'interval': '60m', 'period1': now - 728 * 86400,
                                                       'period2': now}, pause=0.8)
        r = ((d.get('chart') or {}).get('result') or [None])[0] if isinstance(d, dict) else None
        if not r or not r.get('timestamp'):
            out[s] = 'no data'
            log('yahoo 1h %s: no data %s' % (s, str(d)[:80]))
            continue
        q = r['indicators']['quote'][0]
        rows = [[t, q['open'][i], q['close'][i], q['volume'][i]] for i, t in enumerate(r['timestamp'])
                if q['close'][i] is not None]
        write_gz(p, {'symbol': s, 'rows': rows})
        out[s] = len(rows)
        log('yahoo 1h %s: %d' % (s, len(rows)))
    return out


def collect_sec(force=False, log=print):
    u = load_universe()
    ciks = sorted({x['cik'] for x in u['trusts'] + u['dats'] if x.get('cik')})
    out = {}
    for cik in ciks:
        for kind, url in (('facts', SEC_DATA + 'api/xbrl/companyfacts/CIK%010d.json' % cik),
                          ('subs', SEC_DATA + 'submissions/CIK%010d.json' % cik)):
            p = RAW / 'sec' / ('%s_%d.json.gz' % (kind, cik))
            if p.exists() and not force:
                continue
            d = http_json(url, ua=UA_SEC, pause=0.35)
            if isinstance(d, dict) and d.get('_http_error'):
                out['%s_%d' % (kind, cik)] = 'HTTP %s' % d['_http_error']
                log('sec %s %d: HTTP %s' % (kind, cik, d['_http_error']))
                continue
            if kind == 'subs':
                # keep the filing index only (forms, dates, accession numbers, primary documents)
                d = {'cik': cik, 'name': d.get('name'), 'tickers': d.get('tickers'), 'exchanges': d.get('exchanges'),
                     'formerNames': d.get('formerNames'), 'recent': d.get('filings', {}).get('recent'),
                     'files': d.get('filings', {}).get('files')}
            write_gz(p, d)
            out['%s_%d' % (kind, cik)] = 'ok'
        log('sec %d done' % cik)
    return out


def _klines(url, symbol, interval, start_ms, end_ms, log=print, limit=1000):
    rows, t = [], start_ms
    step = {'1h': 3600000, '1d': 86400000}[interval]
    while t < end_ms:
        d = http_json(url, {'symbol': symbol, 'interval': interval, 'startTime': t, 'limit': limit}, pause=0.12)
        if not isinstance(d, list) or not d:
            break
        rows.extend([[k[0], float(k[4]), float(k[7])] for k in d])   # open time, close, quote volume
        nt = d[-1][0] + step
        if nt <= t:
            break
        t = nt
        if len(d) < limit:
            break
    return rows


def collect_binance(coins=None, force=False, log=print, start='2019-01-01'):
    """Hourly closes (spot where listed, else the perp) and every funding settlement of the USD-M perp."""
    coins = coins or sorted(COIN_SYMBOLS)
    end = int(time.time() * 1000)
    out = {}
    for c in coins:
        spot, perp = COIN_SYMBOLS[c]
        p = RAW / 'binance' / ('%s_1h.json.gz' % c)
        if force or not p.exists():
            src, rows = None, []
            if spot:
                rows = _klines(BN_SPOT, spot, '1h', day_ms(start), end, log)
                src = 'spot:' + spot
            if not rows and perp:
                rows = _klines(BN_PERP, perp, '1h', day_ms(start), end, log, limit=1500)
                src = 'perp:' + perp
                if c in PERP_MULT:
                    rows = [[a, b / PERP_MULT[c], v] for a, b, v in rows]
            write_gz(p, {'coin': c, 'source': src, 'rows': rows})
            out[c + '_1h'] = len(rows)
            log('binance %s 1h: %d (%s)' % (c, len(rows), src))
        q = RAW / 'binance' / ('%s_funding.json.gz' % c)
        if perp and (force or not q.exists()):
            rows, t = [], day_ms(start)
            while t < end:
                d = http_json(BN_FUND, {'symbol': perp, 'startTime': t, 'limit': 1000}, pause=0.25)
                if not isinstance(d, list) or not d:
                    break
                rows.extend([[int(x['fundingTime']), float(x['fundingRate'])] for x in d])
                nt = int(d[-1]['fundingTime']) + 1
                if nt <= t or len(d) < 1000:
                    break
                t = nt
            write_gz(q, {'coin': c, 'symbol': perp, 'rows': rows})
            out[c + '_funding'] = len(rows)
            log('binance %s funding: %d' % (c, len(rows)))
    return out


def collect_coingecko(force=False, log=print, pause=8.0):
    """Public-treasury lists per coin, the entity list, each DAT's entity record and its 365-day holdings chart."""
    u = load_universe()
    out = {}
    base = RAW / 'coingecko'

    def get(path, params=None):
        for _ in range(4):
            d = http_json(CG + path, params, pause=pause, rate_wait=70.0)
            if isinstance(d, dict) and (d.get('status') or {}).get('error_code') == 429:
                time.sleep(70)
                continue
            return d
        return {'_error': 'rate limited'}

    for coin, cid in CG_COIN_IDS.items():
        p = base / ('treasury_%s.json.gz' % coin)
        if force or not p.exists():
            d = get('companies/public_treasury/' + cid)
            write_gz(p, d)
            out['treasury_' + coin] = len((d or {}).get('companies') or []) if isinstance(d, dict) else 0
    p = base / 'entities.json.gz'
    if force or not p.exists():
        ents = []
        for page in range(1, 9):
            d = get('entities/list', {'entity_type': 'company', 'per_page': 250, 'page': page})
            if not isinstance(d, list) or not d:
                break
            ents.extend(d)
        write_gz(p, ents)
        out['entities'] = len(ents)
    ents = read_gz(p)
    by_sym = {}
    for e in ents:
        if isinstance(e, dict) and e.get('symbol'):
            by_sym.setdefault(e['symbol'].upper(), e['id'])
    for d in u['dats']:
        eid = by_sym.get((d.get('cg') or '').upper())
        if not eid:
            out['missing_' + d['ticker']] = d.get('cg')
            log('coingecko: no entity for %s (%s)' % (d['ticker'], d.get('cg')))
            continue
        q = base / ('entity_%s.json.gz' % d['ticker'])
        if force or not q.exists():
            write_gz(q, get('public_treasury/' + eid))
        for coin in d['coins']:
            cid = CG_COIN_IDS.get(coin)
            if not cid:
                continue
            r = base / ('chart_%s_%s.json.gz' % (d['ticker'], coin))
            if force or not r.exists():
                c = get('public_treasury/%s/%s/holding_chart' % (eid, cid), {'days': 365})
                write_gz(r, c)
                n = len((c or {}).get('holdings') or []) if isinstance(c, dict) else 0
                out['chart_%s_%s' % (d['ticker'], coin)] = n
                log('coingecko chart %s %s: %d' % (d['ticker'], coin, n))
    return out


def collect_cg_prices(coins=('TON',), force=False, log=print):
    """Daily USD prices for coins Binance stopped quoting (CoinGecko public market chart, last 365 days)."""
    out = {}
    for c in coins:
        p = RAW / 'coingecko' / ('prices_%s.json.gz' % c)
        if p.exists() and not force:
            continue
        d = http_json(CG + 'coins/%s/market_chart' % CG_COIN_IDS[c], {'vs_currency': 'usd', 'days': 365}, pause=8.0,
                      rate_wait=70.0)
        write_gz(p, d)
        out[c] = len((d or {}).get('prices') or [])
        log('coingecko prices %s: %s' % (c, out[c]))
    return out


def collect_strategytracker(force=False, log=print):
    """StrategyTracker's public dataset (BTC treasuries): keep each company's daily history and its statement links."""
    p = RAW / 'strategytracker.json.gz'
    if p.exists() and not force:
        return {'strategytracker': 'cached'}
    latest = http_json('https://data.strategytracker.com/latest.json', pause=0.5)
    full = latest['files']['full']
    d = http_json('https://data.strategytracker.com/' + full, pause=0.5, timeout=180)
    keep = {}
    hist_keys = ('dates', 'stock_prices', 'btc_prices', 'btc_balance', 'total_outstanding_shares',
                 'diluted_shares_outstanding', 'effective_diluted_shares', 'cash_balance', 'debt',
                 'nav_premium_basic', 'nav_premium_diluted', 'market_cap_basic', 'purchase_statement_url', 'use_ev')
    for k, c in d['companies'].items():
        pm = c.get('processedMetrics') or {}
        h = c.get('historicalData') or {}
        keep[k] = {
            'metrics': {x: pm.get(x) for x in ('ticker', 'companyName', 'exchange', 'country', 'sharesOutstanding',
                                                'stockPrice', 'stockPriceDate', 'btcPrice', 'latestTreasuryDate',
                                                'latestBtcBalance', 'latestTotalShares', 'latestDilutedShares',
                                                'latestCashBalance', 'latestDebt', 'navPremiumBasic',
                                                'navPremiumDiluted', 'latestPurchaseStatementUrl', 'preferredStocks',
                                                'hasPreferredStocks', 'debtInstruments', 'debtSummary',
                                                'currencyInfo')},
            'treasury_table': pm.get('treasury_table'),
            'history': {x: h.get(x) for x in hist_keys},
            'currency': c.get('currencyMetadata'),
        }
    write_gz(p, {'version': latest.get('version'), 'timestamp': d.get('timestamp'), 'companies': keep})
    log('strategytracker: %d companies, version %s' % (len(keep), latest.get('version')))
    return {'strategytracker': len(keep), 'version': latest.get('version')}


def collect_strategy(log=print):
    """Strategy's own live KPI feed (market cap, enterprise value, debt and preferred notional, in $M)."""
    d = http_json('https://api.strategy.com/btc/mstrKpiData', pause=0.5)
    p = RAW / 'strategy' / ('mstrKpiData_%s.json.gz' % dt.datetime.now(UTC).strftime('%Y%m%dT%H%M'))
    write_gz(p, {'fetched': dt.datetime.now(UTC).isoformat(timespec='seconds'), 'data': d})
    log('strategy kpi saved %s' % p.name)
    return {'strategy': p.name}



# ---------------------------------------------------------------------------------------------- core math (tested)

SSR_PAID = {2019: 0.0, 2020: 0.0, 2021: 0.0, 2022: 0.001, 2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}
SSR_NOW = 0.038


def ssr_for(date):
    return SSR_PAID.get(int(date[:4]), SSR_NOW)


def split_factor_after(date, splits):
    """Product of split ratios (new shares per old share) taking effect after `date`: an as-reported share count on
    `date` times this factor is on today's share basis. `splits`: [(yyyy-mm-dd, ratio)]."""
    f = 1.0
    for d, r in splits:
        if d > date:
            f *= r
    return f


def interp_log(anchors, date, decay=0.0):
    """Value on `date` from (date, value) anchors, log-linear between anchors; outside them, continuous decay at
    `decay` a year (the sponsor fee for coin per share). Anchors must be sorted and positive."""
    if not anchors:
        return None
    d0 = dt.date.fromisoformat(date)
    if date <= anchors[0][0]:
        a, v = anchors[0]
        return v * math.exp(decay * (dt.date.fromisoformat(a) - d0).days / 365.25)
    if date >= anchors[-1][0]:
        a, v = anchors[-1]
        return v * math.exp(-decay * (d0 - dt.date.fromisoformat(a)).days / 365.25)
    lo, hi = 0, len(anchors) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if anchors[mid][0] <= date:
            lo = mid
        else:
            hi = mid
    (a, va), (b, vb) = anchors[lo], anchors[hi]
    da, db = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    w = (d0 - da).days / max(1, (db - da).days)
    return math.exp(math.log(va) * (1 - w) + math.log(vb) * w)


def lookthrough_nav(coins, price, cash=0.0, debt=0.0, pref=0.0, shares=1.0, converts=(), stock_price=None,
                    extra_shares=0.0):
    """Look-through NAV per share of a treasury company.

    coins x price + cash - debt - preferred liquidation preference, over diluted shares. Each convertible
    (face, conversion price) is counted as shares (face / conversion price) when `stock_price` is at or above its
    conversion price (if-converted) and as debt at face otherwise; with no stock price every convertible is debt.
    `extra_shares` are pre-funded warrants and other near-certain shares. Returns (nav_per_share, diluted_shares,
    equity_value)."""
    d_shares = float(shares) + float(extra_shares)
    d_debt = float(debt)
    for face, cp in converts:
        if stock_price is not None and cp and stock_price >= cp:
            d_shares += face / cp
        else:
            d_debt += face
    equity = coins * price + cash - d_debt - pref
    return equity / d_shares, d_shares, equity


def mnav_variants(price, shares, coins, coin_price, cash=0.0, debt=0.0, pref=0.0, converts=(), extra_shares=0.0):
    """Three ratios on the same inputs: naive (market cap / coin value, what most dashboards show), EV (market cap +
    debt + preferred - cash, over coin value: Strategy's definition) and true (price / look-through NAV per share,
    convertibles if-converted)."""
    coin_value = coins * coin_price
    mcap = price * shares
    conv_face = sum(f for f, _ in converts)
    naive = mcap / coin_value if coin_value > 0 else None
    ev = (mcap + debt + conv_face + pref - cash) / coin_value if coin_value > 0 else None
    nav, dshares, equity = lookthrough_nav(coins, coin_price, cash, debt, pref, shares, converts, price, extra_shares)
    true = price / nav if nav > 0 else None
    return {'naive': naive, 'ev': ev, 'true': true, 'nav_per_share': nav, 'diluted_shares': dshares,
            'equity_value': equity, 'negative_equity': nav <= 0}


def hedged_path(prices, coin_px, hedge_units, funding, i0, i1, margin=1/3, cost_in=0.0, cost_out=0.0,
                perp_fee=0.0005, ssr=None, dates=None, dist=None):
    """Daily P&L of long 1/P0 of a wrapper per $1, short hedge_units[i] x (1/P0) coins, from close i0 to close i1.

    prices, coin_px, hedge_units (coins per wrapper share) and funding (sum of perp funding rates paid by longs over
    (close i-1, close i]) are aligned lists. The short is rebalanced daily to hedge_units[i]; it receives funding on
    its notional at the previous close. Capital = 1 + margin x the short's notional at entry. Costs are fractions of
    the traded notional per side (wrapper: cost_in / cost_out; perp: perp_fee). Returns per-day returns on capital and
    their excess over `ssr` (a function of the date, a year rate) when given."""
    q = 1.0 / prices[i0]
    n0 = q * hedge_units[i0] * coin_px[i0]
    cap = 1.0 + margin * n0
    pnl = [0.0] * (i1 - i0)
    pnl[0] -= cost_in + perp_fee * n0
    for k, i in enumerate(range(i0 + 1, i1 + 1)):
        h = q * hedge_units[i - 1]
        day = q * (prices[i] - prices[i - 1]) - h * (coin_px[i] - coin_px[i - 1]) + h * coin_px[i - 1] * funding[i]
        if dist:
            day += q * dist[i]                 # coin distributed per share (spin-off), taken as cash at NAV
        if k == i1 - i0 - 1:
            day -= cost_out * q * prices[i] + perp_fee * q * hedge_units[i] * coin_px[i]
        pnl[k] += day
    rets = [x / cap for x in pnl]
    out = {'capital': cap, 'returns': rets, 'total': sum(rets), 'days': i1 - i0}
    if ssr and dates:
        ex = []
        for k, i in enumerate(range(i0 + 1, i1 + 1)):
            gap = (dt.date.fromisoformat(dates[i]) - dt.date.fromisoformat(dates[i - 1])).days
            ex.append(rets[k] - ssr(dates[i]) * gap / 365.0)
        out['excess'] = ex
        out['excess_total'] = sum(ex)
    return out


def abdi_ranaldo_spread(highs, lows, closes):
    """Abdi & Ranaldo (2017) close-high-low spread estimator (full spread, fraction of price); None if undefined."""
    eta = [(math.log(h) + math.log(l)) / 2.0 for h, l in zip(highs, lows)]
    c = [math.log(x) for x in closes]
    terms = [(c[t] - eta[t]) * (c[t] - eta[t + 1]) for t in range(len(c) - 1)]
    if not terms:
        return None
    s2 = 4.0 * sum(terms) / len(terms)
    return math.sqrt(s2) if s2 > 0 else 0.0


def late_entry_share(path_returns_full, skip):
    """Share of a trade's total return kept when entering `skip` periods late (exit unchanged)."""
    tot = sum(path_returns_full)
    if tot == 0:
        return None
    return sum(path_returns_full[skip:]) / tot



# ---------------------------------------------------------------------------------------------- loaders

_CACHE = {}


def load_yahoo(sym):
    """{'dates','close','high','low','volume','splits':[(date, ratio)], 'meta'} or None."""
    key = ('y', sym)
    if key in _CACHE:
        return _CACHE[key]
    p = RAW / 'yahoo' / ('%s.json.gz' % sym.replace('=', '_'))
    if not p.exists():
        _CACHE[key] = None
        return None
    d = read_gz(p)
    rows = [list(r) for r in d['rows'] if r[4] is not None and r[4] > 0]
    for adj in (load_curated().get('yahoo_unadjust') or {}).get(sym, []):
        for r in rows:                     # undo Yahoo's spin-off scaling of the close (see curated.json)
            if r[0] < adj['before']:
                for k in (1, 2, 3, 4):
                    if r[k] is not None:
                        r[k] = r[k] / adj['factor']
    out = {'dates': [r[0] for r in rows], 'close': [r[4] for r in rows],
           'high': [r[2] if r[2] else r[4] for r in rows], 'low': [r[3] if r[3] else r[4] for r in rows],
           'volume': [r[5] or 0 for r in rows], 'meta': d.get('meta') or {},
           'splits': [(ymd(x['date'] * 1000), x['numerator'] / x['denominator']) for x in d.get('splits') or []]}
    _CACHE[key] = out
    return out


def load_hourly(coin):
    key = ('h', coin)
    if key not in _CACHE:
        p = RAW / 'binance' / ('%s_1h.json.gz' % coin)
        _CACHE[key] = {r[0]: r[1] for r in read_gz(p)['rows']} if p.exists() else {}
    return _CACHE[key]


def load_funding(coin):
    key = ('f', coin)
    if key not in _CACHE:
        p = RAW / 'binance' / ('%s_funding.json.gz' % coin)
        rows = sorted(read_gz(p)['rows']) if p.exists() else []
        _CACHE[key] = ([r[0] for r in rows], [r[1] for r in rows])
    return _CACHE[key]


def us_close_ms(date):
    """Epoch ms of 16:00 New York on `date`."""
    t = dt.datetime.combine(dt.date.fromisoformat(date), dt.time(16, 0), NY)
    return int(t.timestamp() * 1000)


def coin_close(coin, date):
    """Binance close of the hour ending 16:00 New York on `date` (falls back up to 6 hours earlier)."""
    h = load_hourly(coin)
    end = us_close_ms(date)
    for back in range(1, 7):
        v = h.get(end - back * 3600000)
        if v is not None:
            return v
    return None


def funding_between(coin, t0_ms, t1_ms):
    """Sum of funding rates settled in (t0, t1] (positive: longs paid shorts)."""
    import bisect
    ts, rs = load_funding(coin)
    if not ts:
        return 0.0
    a = bisect.bisect_right(ts, t0_ms)
    b = bisect.bisect_right(ts, t1_ms)
    return sum(rs[a:b])


def funding_start(coin):
    ts, _ = load_funding(coin)
    return ymd(ts[0]) if ts else None


def sec_facts(cik):
    key = ('sec', cik)
    if key not in _CACHE:
        p = RAW / 'sec' / ('facts_%d.json.gz' % cik)
        _CACHE[key] = read_gz(p) if p.exists() else None
    return _CACHE[key]


def xbrl_series(facts, tag, ns='us-gaap', units_exclude=('USD',), units_only=None):
    """All values of a tag as dicts {end, val, filed, form, accn, unit}, deduplicated by (end), keeping the latest
    filing (restatements win)."""
    if not facts:
        return []
    v = (facts.get('facts') or {}).get(ns, {}).get(tag)
    if not v:
        return []
    best = {}
    for unit, arr in v['units'].items():
        if units_only and unit not in units_only:
            continue
        if units_exclude and unit in units_exclude:
            continue
        for x in arr:
            if 'end' not in x or x.get('val') is None:
                continue
            if x.get('start') and tag not in ('InvestmentCompanyExpenseRatioIncludingIncentiveFee',):
                # duration facts are skipped for balance-sheet tags
                pass
            k = x['end']
            cur = best.get(k)
            if cur is None or (x.get('filed') or '') > (cur.get('filed') or ''):
                best[k] = dict(x, unit=unit)
    return [best[k] for k in sorted(best)]


# ---------------------------------------------------------------------------------------------- (a) trusts

def fix_split_basis(raw, splits, fee):
    """Put as-reported coin-per-share anchors on today's share basis.

    XBRL company facts keep the latest filing of each period, and later filings restate comparatives on the
    post-split basis, so the basis of an old period cannot be read from its date. Rule: the latest anchor is
    adjusted by the splits after its filing date; each earlier anchor takes the split factor (a product of any subset
    of the split ratios) that puts it closest to the next anchor grown back at the sponsor fee. `raw`: sorted
    [(end, cps_as_reported, filed)]. Returns [(end, cps, factor)]."""
    if not raw:
        return []
    ratios = [r for _, r in splits]
    cands = {1.0}
    for r in ratios:
        cands |= {c * r for c in cands}
    cands = sorted(cands)
    out = [None] * len(raw)
    e, v, filed = raw[-1]
    f = split_factor_after(filed or e, splits)
    out[-1] = (e, v / f, f)
    for i in range(len(raw) - 2, -1, -1):
        e, v, _ = raw[i]
        ne, nv, _ = out[i + 1]
        days = (dt.date.fromisoformat(ne) - dt.date.fromisoformat(e)).days
        expected = nv * math.exp(fee * days / 365.25)
        best = min(cands, key=lambda c: abs(math.log(v / c / expected)))
        out[i] = (e, v / best, best)
    return out


def trust_anchors(t, distributions=()):
    """Coin-per-share anchors (today's share basis) from the trust's 10-Q/10-K XBRL, the sponsor's NAV per share at
    the same dates on the same basis (for the independent check), and the latest fee.

    An anchor whose units/shares disagrees with the sponsor's own NAV per share by more than 3% at the period end
    (OBTC's 2025 share count is one) is replaced by NAV / coin price and flagged; the check statistics exclude
    replaced anchors. Distributions of coin (the 2024 Mini Trust spin-offs) are removed before interpolation by
    restating anchors after an ex-date to the pre-distribution basis; `trust_series` steps them back."""
    f = sec_facts(t['cik']) if t.get('cik') else None
    y = load_yahoo(t['ticker'])
    splits = y['splits'] if y else []
    units = {x['end']: x for x in xbrl_series(f, 'InvestmentOwnedBalanceContracts')}
    shares = {x['end']: x for x in xbrl_series(f, 'SharesOutstanding', units_exclude=())}
    navs = {x['end']: x for x in xbrl_series(f, 'NetAssetValuePerShare', units_exclude=())}
    fees = xbrl_series(f, 'InvestmentCompanyExpenseRatioIncludingIncentiveFee', units_exclude=())
    fee = fnum(fees[-1]['val']) if fees else 0.025

    def undist(end, v):
        for x in distributions:
            if end >= x['ex_date']:
                v /= (1.0 - x['fraction'])
        return v

    raw = []
    for end in sorted(set(units) & set(shares)):
        u, s_ = fnum(units[end]['val']), fnum(shares[end]['val'])
        if u and s_:
            raw.append((end, undist(end, u / s_), max(units[end].get('filed') or '', shares[end].get('filed') or '')))
    fixed = fix_split_basis(raw, splits, fee)
    anchors, checks, replaced = [], [], []
    for (end, cps, fac), r in zip(fixed, raw):
        nav = fnum(navs[end]['val']) / fac if end in navs and fnum(navs[end]['val']) else None
        cp = coin_close(t['coin'], end) if t.get('coin') else None
        if nav and cp:
            nav_u = undist(end, nav)
            if abs(cps * cp / nav_u - 1.0) > 0.03:
                replaced.append({'end': end, 'units_over_shares': cps, 'nav_over_price': nav_u / cp})
                anchors.append((end, nav_u / cp))
                continue
            checks.append({'end': end, 'cps': cps, 'sponsor_nav': nav_u, 'factor': fac, 'filed': r[2]})
        anchors.append((end, cps))
    return anchors, checks, fee, replaced


def trust_series(t, start='2019-01-01'):
    """Daily table for one single-coin trust: dates, close, coin price at the US close, coin per share, NAV,
    discount, funding over each (prev close, close], volume in $."""
    y = load_yahoo(t['ticker'])
    coin = t.get('coin')
    if not y or not coin:
        return None
    dists = (load_curated().get('trust_distributions') or {}).get(t['ticker'], [])
    anchors, checks, fee, replaced = trust_anchors(t, dists)
    if not anchors:
        return None
    rows = []
    prev_ms = None
    for d, c, h, l, v in zip(y['dates'], y['close'], y['high'], y['low'], y['volume']):
        if d < start:
            continue
        cp = coin_close(coin, d)
        if cp is None:
            continue
        cps = interp_log(anchors, d, fee)
        dist_cash = 0.0
        for x in dists:
            if d >= x['ex_date']:
                if rows and rows[-1]['date'] < x['ex_date']:
                    dist_cash += x['fraction'] * cps * cp     # value of the distributed coin, credited to the holder
                cps *= (1.0 - x['fraction'])
        nav = cps * cp
        ms = us_close_ms(d)
        fnd = funding_between(coin, prev_ms, ms) if prev_ms else 0.0
        prev_ms = ms
        rows.append({'date': d, 'close': c, 'high': h, 'low': l, 'dollar_volume': (v or 0) * c, 'coin_px': cp,
                     'cps': cps, 'nav': nav, 'disc': c / nav - 1.0, 'funding': fnd, 'dist_cash': dist_cash})
    return {'ticker': t['ticker'], 'coin': coin, 'rows': rows, 'anchors': anchors, 'checks': checks, 'fee': fee,
            'replaced': replaced, 'distributions': dists, 'funding_from': funding_start(coin)}


def nav_check(ts):
    """Our NAV (coin per share from XBRL x Binance at 16:00 New York) against the sponsor's reported NAV per share at
    each period end: the independent-path verification for the trusts."""
    out = []
    coin = ts['coin']
    for c in ts['checks']:
        cp = coin_close(coin, c['end'])
        if cp is None or not c.get('sponsor_nav'):
            continue
        ours = c['cps'] * cp          # both on the pre-distribution basis, so the ratio is unaffected
        out.append({'end': c['end'], 'ours': ours, 'sponsor': c['sponsor_nav'], 'err': ours / c['sponsor_nav'] - 1})
    errs = sorted(abs(x['err']) for x in out)
    return {'n': len(out), 'median_abs_err': errs[len(errs) // 2] if errs else None,
            'max_abs_err': errs[-1] if errs else None, 'worst': max(out, key=lambda x: abs(x['err'])) if out else None}


def fee_check(anchors, fee):
    """Coin per share should fall at the sponsor fee between filings while creations are shut: the implied annual
    decay between consecutive anchors."""
    out = []
    for (a, va), (b, vb) in zip(anchors, anchors[1:]):
        days = (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days
        if days <= 0:
            continue
        out.append({'from': a, 'to': b, 'implied_fee': -math.log(vb / va) * 365.25 / days})
    return out


def spread_estimate(rows, i, window=60):
    lo = max(0, i - window)
    hs = [r['high'] for r in rows[lo:i + 1]]
    ls = [r['low'] for r in rows[lo:i + 1]]
    cs = [r['close'] for r in rows[lo:i + 1]]
    if len(cs) < 10:
        return None
    try:
        return abdi_ranaldo_spread(hs, ls, cs)
    except ValueError:
        return None


def adv_usd(rows, i, window=60):
    lo = max(0, i - window)
    xs = [r['dollar_volume'] for r in rows[lo:i + 1]]
    return sum(xs) / len(xs) if xs else 0.0


COST_MODEL = {'mode': 'tiered'}      # 'tiered' (base) or 'estimator' (sensitivity)


def side_cost(rows, i):
    """Cost per side as a fraction of notional. Base ('tiered'): half the Abdi-Ranaldo spread estimate, floored by
    liquidity tier of the trailing-60-day dollar volume (>= $10M: 5bp; $1-10M: 25bp; < $1M: 100bp; OTC quotes in
    thin trusts are often 1-3% wide), capped at 500bp. 'estimator': half the estimate, floored at 5bp."""
    s = (spread_estimate(rows, i) or 0.0) / 2.0
    if COST_MODEL['mode'] == 'estimator':
        return min(0.05, max(0.0005, s))
    adv = adv_usd(rows, i)
    floor = 0.0005 if adv >= 1e7 else (0.0025 if adv >= 1e6 else 0.01)
    return min(0.05, max(floor, s))


def index_of(rows, date, on_or_after=True):
    for i, r in enumerate(rows):
        if (r['date'] >= date) if on_or_after else (r['date'] > date):
            return i
    return None


def event_trade(ts, entry_date, exit_date, margin=1/3, perp_fee=0.0005, skip=0, hedge='nav'):
    """Long the trust / short its NAV in perps from the first close on or after entry_date (+skip trading days) to
    the first close on or after exit_date (or the last row for open trades)."""
    rows = ts['rows']
    i0 = index_of(rows, entry_date)
    if i0 is None:
        return None
    i0 += skip
    i1 = index_of(rows, exit_date) if exit_date else len(rows) - 1
    if i1 is None:
        i1 = len(rows) - 1
    if i0 >= i1:
        return None
    prices = [r['close'] for r in rows]
    cpx = [r['coin_px'] for r in rows]
    # 'nav': short the coins the trust holds per share (locks the discount in dollars at convergence);
    # 'dollar': short $1 of coin per $1 of trust, rebalanced daily (neutral while the discount is constant)
    hu = [r['cps'] for r in rows] if hedge == 'nav' else [r['close'] / r['coin_px'] for r in rows]
    fund = [r['funding'] for r in rows]
    dates = [r['date'] for r in rows]
    dist = [r.get('dist_cash', 0.0) for r in rows]
    res = hedged_path(prices, cpx, hu, fund, i0, i1, margin, side_cost(rows, i0), side_cost(rows, i1), perp_fee,
                      ssr_for, dates, dist)
    years = (dt.date.fromisoformat(dates[i1]) - dt.date.fromisoformat(dates[i0])).days / 365.25
    cum = peak = mdd = 0.0
    for x in res['returns']:
        cum += x
        peak = max(peak, cum)
        mdd = max(mdd, peak - cum)
    fsum = sum(fund[i0 + 1:i1 + 1])
    return {'entry': dates[i0], 'exit': dates[i1], 'disc_entry': rows[i0]['disc'], 'disc_exit': rows[i1]['disc'],
            'days': (dt.date.fromisoformat(dates[i1]) - dt.date.fromisoformat(dates[i0])).days,
            'return_on_capital': res['total'], 'excess_on_capital': res['excess_total'],
            'ann_return': res['total'] / years if years > 0 else None,
            'ann_excess': res['excess_total'] / years if years > 0 else None,
            'max_drawdown': mdd, 'capital_per_dollar': res['capital'], 'funding_received_sum': fsum,
            'cost_in': side_cost(rows, i0), 'cost_out': side_cost(rows, i1), 'adv_usd_entry': adv_usd(rows, i0),
            'returns': res['returns'], 'excess': res['excess'], 'dates': dates[i0 + 1:i1 + 1]}



TRUST_SPLIT = '2025-01-01'          # choose on events / days before, test once on or after
ENTRY_VARIANTS = [('disc<0', 0.0), ('disc<=-5%', 0.05), ('disc<=-10%', 0.10), ('disc<=-20%', 0.20),
                  ('disc<=-30%', 0.30)]


def _ann(x, days):
    return x / (days / 365.25) if days and days > 0 else None


def trust_event_table(series, events):
    """Event trades for every single-coin trust with a conversion filing: discount path, the base trade (enter at
    the first close on or after the filing, exit at the first exchange close), late entries, and each pre-committed
    entry variant."""
    out = []
    for e in events:
        ts = series.get(e['ticker'])
        if not ts or e.get('basket'):
            continue
        rows = ts['rows']
        i0 = index_of(rows, e['filing_public'])
        if i0 is None:
            continue
        exit_date = e.get('listed')
        i1 = index_of(rows, exit_date) if exit_date else len(rows) - 1
        if i1 is None:
            i1 = len(rows) - 1
        seg = rows[i0:i1 + 1]
        worst = min(seg, key=lambda r: r['disc'])
        last_otc = rows[i1 - 1] if exit_date and i1 > i0 else None
        base = event_trade(ts, e['filing_public'], exit_date)
        base_dollar = event_trade(ts, e['filing_public'], exit_date, hedge='dollar')
        late = {k: event_trade(ts, e['filing_public'], exit_date, skip=n) for k, n in (('1d', 1), ('1w', 5))}
        var = {}
        for name, x in ENTRY_VARIANTS:
            j = next((k for k in range(i0, i1) if rows[k]['disc'] < -x or (x > 0 and rows[k]['disc'] <= -x)), None)
            tr = event_trade(ts, rows[j]['date'], exit_date) if j is not None else None
            var[name] = None if tr is None else {k: tr[k] for k in ('entry', 'disc_entry', 'days', 'return_on_capital',
                                                                    'excess_on_capital', 'ann_excess', 'max_drawdown')}
        rec = {'ticker': e['ticker'], 'set': e['set'], 'coin': ts['coin'], 'filing_public': e['filing_public'],
               'listed': exit_date, 'open': exit_date is None,
               'disc_at_filing': rows[i0]['disc'], 'filing_row_date': rows[i0]['date'],
               'disc_prev_close': rows[i0 - 1]['disc'] if i0 > 0 else None,
               'worst_disc': worst['disc'], 'worst_disc_date': worst['date'],
               'disc_last_otc': last_otc['disc'] if last_otc else None,
               'disc_exit': rows[i1]['disc'], 'exit_row_date': rows[i1]['date'],
               'funding_from': ts['funding_from'], 'hedged_from_start': (ts['funding_from'] or '9') <= rows[i0]['date'],
               'adv_usd_at_filing': adv_usd(rows, i0), 'adv_usd_at_exit': adv_usd(rows, i1),
               'spread_est_at_filing': spread_estimate(rows, i0)}
        if base:
            rec['base'] = {k: base[k] for k in base if k not in ('returns', 'excess', 'dates')}
            rec['base']['sharpe'] = None
            r = base['returns']
            if len(r) > 2:
                import statistics as st
                sd = st.pstdev(r)
                rec['base']['sharpe'] = (sum(r) / len(r)) / sd * math.sqrt(252) if sd > 0 else None
            rec['late'] = {}
            for k, tr in late.items():
                if tr:
                    rec['late'][k] = {'return_on_capital': tr['return_on_capital'],
                                      'excess_on_capital': tr['excess_on_capital'],
                                      'share_of_excess_kept': (tr['excess_on_capital'] / base['excess_on_capital']
                                                               if base['excess_on_capital'] else None),
                                      'disc_entry': tr['disc_entry']}
        if base_dollar:
            rec['base_dollar_hedge'] = {k: base_dollar[k] for k in ('return_on_capital', 'excess_on_capital',
                                                                     'ann_excess', 'max_drawdown')}
        rec['variants'] = var
        out.append(rec)
    return out


def choose_entry_variant(events_tab):
    """Choose the entry variant on early events (mean annualised excess on capital), report it on late events."""
    def stats(evs, name):
        xs = [e['variants'][name] for e in evs if e['variants'].get(name)]
        if not xs:
            return {'n': 0}
        ex = [x['excess_on_capital'] for x in xs]
        ann = [x['ann_excess'] for x in xs if x['ann_excess'] is not None]
        days = sum(x['days'] for x in xs)
        return {'n': len(xs), 'mean_excess_per_trade': sum(ex) / len(ex), 'mean_ann_excess': sum(ann) / len(ann) if ann else None,
                'pooled_ann_excess': sum(ex) / (days / 365.25) if days else None, 'min_trade_excess': min(ex),
                'max_drawdown_worst': max(x['max_drawdown'] for x in xs), 'per_trade': [(e['ticker'], e['variants'][name]['excess_on_capital']) for e in evs if e['variants'].get(name)]}
    early = [e for e in events_tab if e['set'] == 'early']
    late_done = [e for e in events_tab if e['set'] == 'late']
    pending = [e for e in events_tab if e['set'] == 'pending']
    ins = {n: stats(early, n) for n, _ in ENTRY_VARIANTS}
    chosen = max((n for n in ins if ins[n].get('n')), key=lambda n: ins[n]['pooled_ann_excess'])
    return {'protocol': 'choose the entry rule on the early conversions (GBTC, ETHE) by pooled excess over the savings rate per year of capital; test once on the conversions completed 2025-2026; pending filings are marked to market on 2026-10-09 and reported separately',
            'chosen': chosen, 'in_sample': ins, 'out_of_sample': {n: stats(late_done, n) for n, _ in ENTRY_VARIANTS},
            'pending_mark_to_market': {n: stats(pending, n) for n, _ in ENTRY_VARIANTS}}


def trust_daily_returns(ts, margin=1/3, hedge='nav'):
    """Per-day hedged return on capital of holding the trust from the previous close, and the per-side transition
    cost for that day. hedge='nav': short the coins held per share (net short |discount| x NAV in the coin while
    the discount persists: P&L = (d1 - d0 + d1 x coin return) / (1 + d0)); hedge='dollar': short $1 of coin per $1
    of trust (P&L = coin factor x (d1 - d0) / (1 + d0), no directional term)."""
    rows = ts['rows']
    key = ('tdr', ts['ticker'], margin, hedge)
    if key in _CACHE:
        return _CACHE[key]
    out = {}
    for i in range(1, len(rows)):
        a, b = rows[i - 1], rows[i]
        h = a['nav'] / a['close'] if hedge == 'nav' else 1.0     # coin notional short per $ of trust
        r = (b['close'] + b.get('dist_cash', 0.0)) / a['close'] - 1.0 - h * (b['coin_px'] / a['coin_px'] - 1.0) + h * b['funding']
        out[b['date']] = {'r': r / (1.0 + margin * h), 'h': h, 'cost': side_cost(rows, i - 1), 'disc_prev': a['disc'],
                          'gap': (dt.date.fromisoformat(b['date']) - dt.date.fromisoformat(a['date'])).days}
    _CACHE[key] = out
    return out


def catalyst_window(e):
    return (e['filing_public'], e.get('listed') or '9999-12-31')


def rule_backtest(series, events, x, need_catalyst, exit_frac=0.5, margin=1/3, perp_fee=0.0005, delay=0,
                  start=None, end=None, hedge='nav'):
    """Daily portfolio of trusts: hold every single-coin trust whose close discount is at or below -x (and, when
    need_catalyst, whose conversion filing is public and not yet listed); leave when the discount is above
    -x * exit_frac or the catalyst is resolved. Entry `delay` trading days after the signal (late-entry test).
    Equal capital across open positions; flat days earn the savings rate (excess 0). Returns ({date: excess on
    capital}, trade log)."""
    win = {e['ticker']: catalyst_window(e) for e in events if not e.get('basket')}
    daily = {tk: trust_daily_returns(ts, margin, hedge) for tk, ts in series.items()}
    bydate = {tk: {r['date']: (i, r) for i, r in enumerate(ts['rows'])} for tk, ts in series.items()}
    cal = sorted({d for v in bydate.values() for d in v if (start is None or d >= start) and (end is None or d <= end)})
    pos, wait, log, out = {}, {}, [], {}
    prev = None
    for d in cal:
        rs = [daily[tk][d]['r'] for tk in pos if d in daily[tk]]
        n_before = len(pos)
        costs = 0.0
        for tk in series:
            if d not in bydate[tk]:
                continue
            i, row = bydate[tk][d]
            inwin = tk in win and win[tk][0] <= d < win[tk][1]
            ok = inwin or not need_catalyst
            h = row['nav'] / row['close'] if hedge == 'nav' else 1.0
            c = (side_cost(series[tk]['rows'], i) + perp_fee * h) / (1.0 + margin * h)
            if tk in pos:
                if (not ok) or row['disc'] > -x * exit_frac:
                    costs += c
                    log.append({'ticker': tk, 'entry': pos.pop(tk), 'exit': d, 'disc_exit': row['disc']})
            elif ok and row['disc'] <= -x:
                if wait.get(tk, 0) >= delay:
                    pos[tk] = d
                    costs += c
                    wait.pop(tk, None)
                else:
                    wait[tk] = wait.get(tk, 0) + 1
            else:
                wait.pop(tk, None)
        n = max(n_before, len(pos))
        gap = (dt.date.fromisoformat(d) - dt.date.fromisoformat(prev)).days if prev else 1
        prev = d
        if n == 0:
            out[d] = 0.0
            continue
        day = (sum(rs) / n_before if n_before else 0.0) - costs / n
        out[d] = day - (ssr_for(d) * gap / 365.0 if n_before else 0.0)
    for tk, e in pos.items():
        log.append({'ticker': tk, 'entry': e, 'exit': None, 'disc_exit': None})
    return out, log



DISC_BUCKETS = [(-1e9, -0.30), (-0.30, -0.20), (-0.20, -0.10), (-0.10, -0.05), (-0.05, 0.0), (0.0, 1e9)]


def bucket_name(lo, hi):
    f = lambda v: ('%+d%%' % round(v * 100)) if abs(v) < 5 else ('-inf' if v < 0 else '+inf')
    return '%s..%s' % (f(lo), f(hi))


def trust_state(tk, d, wins):
    w = wins.get(tk)
    if not w:
        return 'no_filing'
    if d < w[0]:
        return 'no_filing'
    if d < w[1]:
        return 'pending'
    return 'listed'


def trust_panel(series, events, horizons=(21, 63), hedge='nav'):
    """Every trust-day before listing: discount bucket x catalyst state x period, with the forward hedged excess
    return on capital over h trading days (stopping at the listing). HAC t-stats with h lags (overlapping
    windows)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import backtest as B
    wins = {e['ticker']: catalyst_window(e) for e in events if not e.get('basket')}
    cells = {}
    for tk, ts in series.items():
        dr = trust_daily_returns(ts, hedge=hedge)
        rows = ts['rows']
        ex = [None] + [dr[r['date']]['r'] - ssr_for(r['date']) * dr[r['date']]['gap'] / 365.0 for r in rows[1:]]
        for i, r in enumerate(rows):
            st = trust_state(tk, r['date'], wins)
            if st == 'listed' or ts['funding_from'] is None or r['date'] < ts['funding_from']:
                continue
            per = 'early' if r['date'] < TRUST_SPLIT else 'late'
            b = next(bucket_name(lo, hi) for lo, hi in DISC_BUCKETS if lo < r['disc'] <= hi)
            for h in horizons:
                j_end = min(len(rows) - 1, i + h)
                if wins.get(tk) and rows[j_end]['date'] > wins[tk][1]:
                    j_end = index_of(rows, wins[tk][1]) or j_end
                if j_end <= i:
                    continue
                fwd = sum(ex[k] for k in range(i + 1, j_end + 1))
                cells.setdefault((per, st, b, h), []).append((r['date'], tk, fwd))
    out = []
    for (per, st, b, h), xs in sorted(cells.items()):
        xs.sort()
        vals = [v for _, _, v in xs]
        t, p = B.newey_west_t(vals, lags=h) if len(vals) > h + 2 else (None, None)
        out.append({'period': per, 'state': st, 'bucket': b, 'h': h, 'n_days': len(vals),
                    'n_trusts': len({tk for _, tk, _ in xs}), 'mean_fwd_excess': sum(vals) / len(vals),
                    'hit': sum(1 for v in vals if v > 0) / len(vals), 'nw_t': t,
                    'trusts': sorted({tk for _, tk, _ in xs})})
    return out


def trust_rules(series, events, hedge='nav'):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import backtest as B
    variants = {}
    logs = {}
    for x in (0.05, 0.10, 0.20, 0.30):
        for cat in (True, False):
            name = 'disc<=-%d%%%s' % (round(x * 100), '|filing' if cat else '|any')
            r, lg = rule_backtest(series, events, x, cat, start='2019-09-10', hedge=hedge)
            variants[name] = r
            logs[name] = lg
    cal = sorted(next(iter(variants.values())))
    cut = next(i for i, d in enumerate(cal) if d >= TRUST_SPLIT)
    frac = cut / len(cal)
    ser = {k: [v[d] for d in cal] for k, v in variants.items()}
    ct = B.choose_then_test(ser, frac=frac, periods_per_year=252)
    chosen = ct['chosen']
    x = float(chosen.split('<=-')[1].split('%')[0]) / 100.0
    cat = chosen.endswith('|filing')
    test_dates = cal[cut:]

    def active_perf(series_d, dates):
        act = [series_d[d] for d in dates if series_d[d] != 0.0]
        return {'active_days': len(act), 'perf_active': B.perf(act, 252) if act else {'n': 0},
                'calendar_ann_excess': sum(series_d[d] for d in dates) / (len(dates) / 252.0) if dates else None}

    late = {}
    for k, delay in (('1d', 1), ('1w', 5)):
        r, _ = rule_backtest(series, events, x, cat, delay=delay, start='2019-09-10', hedge=hedge)
        late[k] = {'test_total_excess': sum(r[d] for d in test_dates), 'full_total_excess': sum(r[d] for d in cal),
                   'insample_total_excess': sum(r[d] for d in cal[:cut])}
    base_tot = {'test': sum(variants[chosen][d] for d in test_dates), 'full': sum(variants[chosen][d] for d in cal),
                'insample': sum(variants[chosen][d] for d in cal[:cut])}
    all_variants = {}
    for k, v in variants.items():
        all_variants[k] = {'insample': active_perf(v, cal[:cut]), 'test': active_perf(v, test_dates),
                           'trades_test': [t for t in logs[k] if (t['exit'] or '9') >= TRUST_SPLIT],
                           'n_trades': len(logs[k])}
    clean = {k: v for k, v in ct.items() if k not in ('bh_adjusted_p',)}
    return {'protocol': 'daily portfolio of trusts, equal capital; 8 pre-committed variants (discount trigger 5/10/20/30% x with or without a pending conversion filing); exit when the discount is above half the trigger or the catalyst resolves; chosen on 2019-09-10..2024-12-31 by in-sample Sharpe, tested once on 2025-01-01..2026-10-09',
            'choose_then_test': clean, 'bh_adjusted_p': ct.get('bh_adjusted_p'), 'chosen': chosen,
            'chosen_totals': base_tot, 'late_entry': late, 'variants': all_variants, 'calendar': [cal[0], cal[-1]],
            'test_from': cal[cut]}


def trust_live(series, universe, curated):
    wins = {e['ticker']: e for e in curated.get('trust_events', [])}
    nofile = curated.get('trusts_without_filing', {})
    out = []
    for t in universe['trusts']:
        tk = t['ticker']
        y = load_yahoo(tk)
        rec = {'ticker': tk, 'coin': t.get('coin'), 'kind': t['kind'], 'sponsor': t['sponsor'],
               'exchange': (y or {}).get('meta', {}).get('exchangeName')}
        if y:
            i = len(y['dates']) - 1
            rec['last_date'] = y['dates'][i]
            rec['close'] = y['close'][i]
            lo = max(0, i - 59)
            dv = [c * v for c, v in zip(y['close'][lo:i + 1], y['volume'][lo:i + 1])]
            rec['adv60_usd'] = sum(dv) / len(dv)
            try:
                rec['spread_est'] = abdi_ranaldo_spread(y['high'][lo:i + 1], y['low'][lo:i + 1], y['close'][lo:i + 1])
            except ValueError:
                rec['spread_est'] = None
            rec['capacity_usd'] = 0.10 * rec['adv60_usd'] * 5
        ts = series.get(tk)
        if ts:
            r = ts['rows'][-1]
            rec.update({'nav': r['nav'], 'disc': r['disc'], 'cps': r['cps'], 'nav_date': r['date']})
        e = wins.get(tk)
        if e:
            rec['filing'] = e['filing_public']
            rec['listed'] = e.get('listed')
            rec['status'] = 'listed' if e.get('listed') else 'pending conversion'
        else:
            rec['status'] = ('listed' if rec.get('exchange') in ('PCX', 'NGM', 'NMS', 'NYQ') else
                             'no conversion filing') if tk not in nofile else 'no conversion filing'
            rec['status_note'] = nofile.get(tk)
        if not ts and tk in nofile:
            rec['nav_note'] = 'non-reporting: no XBRL coin per share; the sponsor site refuses automated access (gap)'
        out.append(rec)
    return out


def basket_table(universe, curated):
    """Basket trusts (GDLC, BITW, DEFG): the sponsor's quarter-end NAV per share against the Yahoo close on the
    last trading day on or before the period end."""
    ev = {e['ticker']: e for e in curated.get('trust_events', [])}
    out = []
    for t in universe['trusts']:
        if t['kind'] != 'basket':
            continue
        f = sec_facts(t['cik'])
        navs = xbrl_series(f, 'NetAssetValuePerShare', units_exclude=())
        y = load_yahoo(t['ticker'])
        if not navs or not y:
            out.append({'ticker': t['ticker'], 'note': 'no XBRL NAV per share (non-reporting)'})
            continue
        rows = []
        for x in navs:
            j = max((k for k, d in enumerate(y['dates']) if d <= x['end']), default=None)
            if j is None:
                continue
            rows.append({'end': x['end'], 'nav': fnum(x['val']), 'close': y['close'][j],
                         'disc': y['close'][j] / fnum(x['val']) - 1.0})
        out.append({'ticker': t['ticker'], 'filing': (ev.get(t['ticker']) or {}).get('filing_public'),
                    'listed': (ev.get(t['ticker']) or {}).get('listed'), 'quarter_ends': rows[-16:]})
    return out


def rule_trade_dollars(series, log, hedge='dollar', margin=1/3, participation=0.10, build_days=5, since=None):
    """Dollar P&L of each logged trade at an ADV-limited size: notional = participation x trailing-60-day dollar
    volume x build days, at the entry. Trade return on capital from the daily hedged returns between entry and exit
    (costs at both ends from the cost model)."""
    out = []
    for t in log:
        if since and (t['exit'] or '9999') < since:
            continue
        ts = series[t['ticker']]
        rows = ts['rows']
        dr = trust_daily_returns(ts, margin, hedge)
        i0 = index_of(rows, t['entry'])
        i1 = index_of(rows, t['exit']) if t['exit'] else len(rows) - 1
        if i0 is None or i1 is None or i1 <= i0:
            continue
        r = sum(dr[rows[k]['date']]['r'] for k in range(i0 + 1, i1 + 1))
        h0 = rows[i0]['nav'] / rows[i0]['close'] if hedge == 'nav' else 1.0
        cost = (side_cost(rows, i0) + 0.0005 * h0 + side_cost(rows, i1) + 0.0005 * h0) / (1 + margin * h0)
        ex = sum(ssr_for(rows[k]['date']) * (dt.date.fromisoformat(rows[k]['date']) - dt.date.fromisoformat(rows[k - 1]['date'])).days / 365.0
                 for k in range(i0 + 1, i1 + 1))
        notional = participation * adv_usd(rows, i0) * build_days
        cap = notional * (1 + margin * h0)
        out.append({'ticker': t['ticker'], 'entry': rows[i0]['date'], 'exit': rows[i1]['date'], 'open': t['exit'] is None,
                    'disc_entry': rows[i0]['disc'], 'disc_exit': rows[i1]['disc'], 'ret_on_capital': r - cost,
                    'excess_on_capital': r - cost - ex, 'notional_usd': notional, 'capital_usd': cap,
                    'excess_usd': (r - cost - ex) * cap})
    return out


def analyze_trusts(log=print):
    u = load_universe()
    cur = load_curated()
    series = {}
    for t in u['trusts']:
        if t['kind'] != 'single':
            continue
        ts = trust_series(t)
        if ts and ts['rows']:
            series[t['ticker']] = ts
            log('trust %s: %d rows %s..%s' % (t['ticker'], len(ts['rows']), ts['rows'][0]['date'], ts['rows'][-1]['date']))
    verification = {}
    for tk, ts in series.items():
        fc = fee_check(ts['anchors'], ts['fee'])
        verification[tk] = {'nav_check': nav_check(ts), 'anchors': len(ts['anchors']), 'replaced': ts['replaced'],
                            'fee': ts['fee'], 'implied_fee_min': min((x['implied_fee'] for x in fc), default=None),
                            'implied_fee_max': max((x['implied_fee'] for x in fc), default=None),
                            'distributions': ts['distributions']}
    events = trust_event_table(series, cur['trust_events'])
    choice = choose_entry_variant(events)
    panel = trust_panel(series, cur['trust_events'])
    panel_dollar = trust_panel(series, cur['trust_events'], hedge='dollar')
    rules = trust_rules(series, cur['trust_events'])
    rules_dollar = trust_rules(series, cur['trust_events'], hedge='dollar')
    live = trust_live(series, u, cur)
    baskets = basket_table(u, cur)
    return {'series_coverage': {tk: [ts['rows'][0]['date'], ts['rows'][-1]['date'], len(ts['rows'])] for tk, ts in series.items()},
            'verification': verification, 'events': events, 'entry_choice': choice, 'panel': panel,
            'panel_dollar_hedge': panel_dollar, 'rules': rules, 'rules_dollar_hedge': rules_dollar,
            'live': live, 'baskets': baskets}



# ---------------------------------------------------------------------------------------------- (b) DATs

DAT_SPLIT = '2026-04-01'           # panel: choose on signals before, test once on signals on or after
EXCH_CLOSE = {'JPX': ('Asia/Tokyo', 15, 30), 'PAR': ('Europe/Paris', 17, 30), 'LSE': ('Europe/London', 16, 30)}
NON_PURE = {'DJT': 'operating company (Truth Social)', 'CEPO': 'SPAC: shareholders own trust cash until the merger closes',
            'BTBT': 'owns a WhiteFiber stake not in the look-through NAV', 'DDC': 'operating food business',
            'SQNS': 'operating semiconductor business; sold all BTC by 2026-09', 'GDC': 'operating business',
            'NXTT': 'operating business'}
SANE_MNAV = (0.05, 20.0)


def close_ms_exch(date, exch):
    tz, h, m = EXCH_CLOSE.get(exch, ('America/New_York', 16, 0))
    t = dt.datetime.combine(dt.date.fromisoformat(date), dt.time(h, m), ZoneInfo(tz))
    return int(t.timestamp() * 1000)


def coin_at_ms(coin, ms):
    """Close of the last complete Binance hour ending at or before `ms`; for coins Binance stopped quoting (TON
    after 2026-06-30) CoinGecko's daily price on or before that day."""
    h = load_hourly(coin)
    end = ms - ms % 3600000
    for back in range(1, 7):
        v = h.get(end - back * 3600000)
        if v is not None:
            return v
    p = RAW / 'coingecko' / ('prices_%s.json.gz' % coin)
    if p.exists():
        key = ('cgp', coin)
        if key not in _CACHE:
            _CACHE[key] = sorted((ymd(t), v) for t, v in (read_gz(p).get('prices') or []))
        r = asof(_CACHE[key], ymd(ms))
        if r and (dt.date.fromisoformat(ymd(ms)) - dt.date.fromisoformat(r[0])).days <= 3:
            return r[1]
    return None


def fx_to_usd(currency, date):
    """USD per unit of `currency` on `date` (Yahoo daily FX, last value on or before)."""
    if currency in (None, 'USD'):
        return 1.0
    sym, invert, scale = {'JPY': ('JPY=X', True, 1.0), 'EUR': ('EURUSD=X', False, 1.0), 'GBP': ('GBPUSD=X', False, 1.0),
                          'GBp': ('GBPUSD=X', False, 0.01), 'SEK': ('SEK=X', True, 1.0)}.get(currency, (None, False, 1.0))
    if not sym:
        return None
    y = load_yahoo(sym)
    if not y:
        return None
    key = ('fxidx', sym)
    if key not in _CACHE:
        _CACHE[key] = dict(zip(y['dates'], y['close']))
    m = _CACHE[key]
    d = dt.date.fromisoformat(date)
    for back in range(0, 8):
        v = m.get((d - dt.timedelta(days=back)).isoformat())
        if v:
            return (1.0 / v if invert else v) * scale
    return None


def xbrl_original(facts, tag, ns='us-gaap', forms=('10-Q', '10-K', '10-KT', '10-Q/A', '10-K/A')):
    """{end: fact} for instant facts of a tag, keeping the ORIGINAL filing of each period (earliest filed): later
    filings restate comparatives (splits, reclassifications), and a point-in-time study must see what was known."""
    if not facts:
        return {}
    v = (facts.get('facts') or {}).get(ns, {}).get(tag)
    if not v:
        return {}
    out = {}
    for unit, arr in v['units'].items():
        for x in arr:
            if x.get('start') or x.get('val') is None or (forms and x.get('form') not in forms):
                continue
            cur = out.get(x['end'])
            if cur is None or (x.get('filed') or '') < (cur.get('filed') or ''):
                out[x['end']] = dict(x, unit=unit)
    return out


DEBT_TOTALS = [('LongTermDebt',), ('LongTermDebtNoncurrent', 'LongTermDebtCurrent'),
               ('ConvertibleDebtNoncurrent', 'ConvertibleNotesPayableCurrent'),
               ('ConvertibleLongTermNotesPayable', 'ConvertibleNotesPayableCurrent'), ('ConvertibleNotesPayable',),
               ('DebtInstrumentCarryingAmount',), ('NotesPayable', 'LoansPayable', 'SecuredDebt')]
PREF_TAGS = ['TemporaryEquityCarryingAmountAttributableToParent', 'PreferredStockLiquidationPreferenceValue',
             'PreferredStockValue']


def capital_from_xbrl(f, end, tagvals):
    """Cash, debt and preferred at one balance-sheet date by a fixed rule: debt = the largest of the alternative
    total-debt measures reported for that date (they overlap, so they are never summed across groups) plus
    short-term borrowings; preferred = the largest of temporary equity, liquidation preference and preferred
    carrying value (values under $1M ignored)."""
    def val(tag):
        x = tagvals.get(tag, {}).get(end)
        return fnum(x['val']) if x else None
    cash = val('CashAndCashEquivalentsAtCarryingValue')
    if cash is None:
        cash = val('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents')
    totals = []
    for grp in DEBT_TOTALS:
        vs = [val(t) for t in grp]
        if any(v is not None for v in vs):
            totals.append((sum(v for v in vs if v is not None), '+'.join(t for t, v in zip(grp, vs) if v is not None)))
    debt, debt_rule = max(totals) if totals else (0.0, None)
    stb = val('ShortTermBorrowings') or 0.0
    prefs = [(val(t) or 0.0, t) for t in PREF_TAGS]
    pref, pref_rule = max(prefs)
    if pref < 1e6:
        pref, pref_rule = 0.0, None
    return {'cash': cash or 0.0, 'debt': debt + stb, 'debt_rule': debt_rule, 'short_term_borrowings': stb,
            'pref': pref, 'pref_rule': pref_rule}


def st_company(key):
    k = ('st', key)
    if k not in _CACHE:
        p = RAW / 'strategytracker.json.gz'
        _CACHE[k] = read_gz(p)['companies'].get(key) if (p.exists() and key) else None
    return _CACHE[k]


def asof(series, date):
    """Last (date, value...) row of a sorted list on or before `date`."""
    lo, hi = 0, len(series) - 1
    if not series or series[0][0] > date:
        return None
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if series[mid][0] <= date:
            lo = mid
        else:
            hi = mid - 1
    return series[lo]


def holdings_series(d):
    """[(date, coins)] for the DAT's primary coin: StrategyTracker's daily ledger when present, else CoinGecko's
    weekly chart (last 365 days). Source name returned."""
    st = st_company(d.get('st'))
    if st and st['history'].get('dates'):
        h = st['history']
        rows = [(a, b) for a, b in zip(h['dates'], h['btc_balance']) if b is not None]
        return rows, 'strategytracker'
    p = RAW / 'coingecko' / ('chart_%s_%s.json.gz' % (d['ticker'], d['coins'][0]))
    if p.exists():
        c = read_gz(p)
        hs = (c or {}).get('holdings') if isinstance(c, dict) else None
        if hs:
            return [(ymd(t), v) for t, v in hs], 'coingecko'
    return [], None


def st_pref_history(key):
    """[(date, total preferred notional USD)] from StrategyTracker's per-series histories (from 2026-03 for MSTR)."""
    st = st_company(key)
    if not st:
        return []
    ev = []
    for x in st['metrics'].get('preferredStocks') or []:
        # USD per unit of the series' notional currency, from the series' own notionalUSD / notionalMillions
        usd_per = (fnum(x.get('notionalUSD')) or 0.0) / ((fnum(x.get('notionalMillions')) or 0.0) * 1e6) \
            if fnum(x.get('notionalMillions')) else 1.0
        for h in x.get('history') or []:
            if h.get('effective_date') and h.get('notional_millions') is not None:
                ev.append((h['effective_date'], x.get('ticker'), fnum(h['notional_millions']) * 1e6 * usd_per))
    ev.sort()
    cur, out = {}, []
    for date, tk, v in ev:
        cur[tk] = v
        out.append((date, sum(cur.values())))
    return out


def dat_anchors(d):
    """Point-in-time capital-structure anchors from each 10-Q/10-K: usable from the filing date."""
    f = sec_facts(d['cik']) if d.get('cik') else None
    if not f:
        return []
    y = load_yahoo(d['yahoo'])
    splits = y['splits'] if y else []
    tags = ['CashAndCashEquivalentsAtCarryingValue', 'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',
            'ShortTermBorrowings', 'CommonStockSharesOutstanding', 'CryptoAssetNumberOfUnits'] + PREF_TAGS + \
           sorted({t for g in DEBT_TOTALS for t in g})
    tv = {t: xbrl_original(f, t) for t in tags}
    cover = xbrl_original(f, 'EntityCommonStockSharesOutstanding', ns='dei')
    cover_by_accn = {}
    for e, x in cover.items():
        cover_by_accn[x.get('accn')] = x
    ends = set()
    for t in ('CashAndCashEquivalentsAtCarryingValue', 'CommonStockSharesOutstanding', 'CryptoAssetNumberOfUnits'):
        ends |= set(tv[t])
    out = []
    for e in sorted(ends):
        if e < '2025-03-31':
            continue
        facts_e = [tv[t][e] for t in tags if e in tv[t]]
        filed = min(x['filed'] for x in facts_e)
        accn = next((x['accn'] for x in facts_e if x['filed'] == filed), None)
        sh = tv['CommonStockSharesOutstanding'].get(e)
        sh_src = 'us-gaap:CommonStockSharesOutstanding'
        if not sh or sh['filed'] != filed:
            c = cover_by_accn.get(accn)
            if c:
                sh, sh_src = c, 'dei:EntityCommonStockSharesOutstanding (cover %s)' % c['end']
        if not sh:
            wa = [x for x in ((f.get('facts') or {}).get('us-gaap', {}).get('WeightedAverageNumberOfDilutedSharesOutstanding', {})
                              .get('units', {}).get('shares', [])) if x.get('end') == e and x.get('form') in ('10-Q', '10-K')]
            if wa:
                wa.sort(key=lambda x: (x['filed'], (dt.date.fromisoformat(x['end']) - dt.date.fromisoformat(x['start'])).days))
                sh, sh_src = wa[0], 'us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding (fallback: no instant count)'
        if sh and (fnum(sh['val']) or 0) < 1000:          # pre-merger shells report 1 share
            sh, sh_src = None, None
        cap = capital_from_xbrl(f, e, tv)
        fac = split_factor_after(filed, splits)
        units = tv['CryptoAssetNumberOfUnits'].get(e)
        out.append(dict(cap, end=e, filed=filed, accn=accn, shares=fnum(sh['val']) * fac if sh else None,
                        shares_src=sh_src if sh else None, split_factor=fac,
                        units_xbrl=fnum(units['val']) if units else None))
    out.sort(key=lambda a: a['filed'])
    return out



def _latest(cands, date):
    """Most recent (date, value) among candidates dated on or before `date`."""
    xs = [c for c in cands if c[0] <= date and c[1] is not None]
    return max(xs) if xs else None


def dat_daily(d, start='2025-06-01'):
    """Daily look-through series for one DAT (USD): price, coin price at the stock's close, coins per share, cash,
    debt and preferred per share, the three mNAV ratios, funding, dollar volume. Point in time: capital structure
    from the latest 10-Q/10-K already filed; StrategyTracker names use its daily coins and shares, others hold the
    anchor's coins per share until the next filing."""
    y = load_yahoo(d['yahoo'])
    if not y or not d.get('coins'):
        return None
    coin = d['coins'][0]
    exch = y['meta'].get('exchangeName')
    cur = y['meta'].get('currency')
    hs, hsrc = holdings_series(d)
    anchors = dat_anchors(d)
    st = st_company(d.get('st'))
    st_rows = []
    if st:
        h = st['history']
        st_rows = [(a, b, c, e, f) for a, b, c, e, f in zip(h['dates'], h['btc_balance'], h['total_outstanding_shares'],
                                                          h.get('cash_balance') or [None] * len(h['dates']),
                                                          h.get('debt') or [None] * len(h['dates']))]
    prefh = st_pref_history(d.get('st'))
    rows, prev_ms = [], None
    vols = []
    for date, close, vol in zip(y['dates'], y['close'], y['volume']):
        fx = fx_to_usd(cur, date)
        if fx is None:
            continue
        vols.append((vol or 0) * close * fx)
        if date < start:
            continue
        P = close * fx
        ms = close_ms_exch(date, exch)
        C = coin_at_ms(coin, ms)
        if C is None:
            continue
        fnd = funding_between(coin, prev_ms, ms) if prev_ms else 0.0
        prev_ms = ms
        a = None
        for x in anchors:
            if x['filed'] <= date:
                a = x
        src = {}
        if st_rows:
            r = asof(st_rows, date)
            if not r or not r[2]:
                continue
            H, S = r[1], r[2]
            if a and a.get('cash') is not None and d.get('cik'):
                cash, debt = a['cash'], a['debt']
                src['capital'] = 'xbrl %s filed %s' % (a['end'], a['filed'])
            else:
                cash, debt = (r[3] or 0.0), (r[4] or 0.0)
                src['capital'] = 'strategytracker'
            pc = [(a['filed'], a['pref'])] if a else []
            ph = asof(prefh, date) if prefh else None
            if ph:
                pc.append(ph)
            lp = _latest(pc, date)
            pref = lp[1] if lp else 0.0
            cps = H / S
        else:
            if a is None or not a.get('shares'):
                continue
            S = a['shares']
            hh = asof(hs, a['end']) if hs else None
            if hh is None and hs and hs[0][0] <= (dt.date.fromisoformat(a['end']) + dt.timedelta(days=21)).isoformat():
                hh = hs[0]
            # XBRL CryptoAssetNumberOfUnits only when the company has no dashboard holdings at all: where both exist
            # they can disagree badly (SBET's tag counts 229k of its ~870k ETH), so a period outside the dashboard's
            # window is skipped rather than filled from the tag
            if hh:
                H = hh[1]
                src['holdings'] = hsrc
            elif not hs:
                H = a.get('units_xbrl')
                src['holdings'] = 'xbrl units'
            else:
                H = None
            if not H:
                continue
            cash, debt, pref = a['cash'], a['debt'], a['pref']
            src['capital'] = 'xbrl %s filed %s' % (a['end'], a['filed'])
            cps = H / S
        coin_ps = cps * C
        nav = coin_ps + (cash - debt - pref) / S
        naive = P / coin_ps if coin_ps > 0 else None
        ev = (P * S + debt + pref - cash) / (cps * S * C) if coin_ps > 0 else None
        true = P / nav if nav > 0 else None
        rows.append({'date': date, 'price': P, 'coin_px': C, 'cps': cps, 'shares': S, 'cash': cash, 'debt': debt,
                     'pref': pref, 'nav': nav, 'naive': naive, 'ev': ev, 'true': true, 'funding': fnd,
                     'adv_usd': sum(vols[-60:]) / max(1, len(vols[-60:])), 'src': src})
    return {'ticker': d['ticker'], 'coin': coin, 'rows': rows, 'anchors': anchors, 'holdings_source': hsrc,
            'exchange': exch, 'currency': cur}


def dat_side_cost(adv):
    """Stock cost per side by trailing-60-day dollar volume: >= $100M 5bp; $10-100M 10bp; $1-10M 30bp; < $1M 100bp."""
    return 0.0005 if adv >= 1e8 else (0.001 if adv >= 1e7 else (0.003 if adv >= 1e6 else 0.01))


def dat_hedge_ratio(row, hedge):
    """Coin notional short per $ of stock. 'asset': the look-through coins (locks the dollar discount at
    convergence, net short (1 - true mNAV) x coin value while it persists); 'beta': coin value per share over NAV
    per share (neutral to coin moves at constant true mNAV; capped at 3)."""
    cv = row['cps'] * row['coin_px']
    if hedge == 'asset':
        return cv / row['price']
    if row['nav'] <= 0:
        return None
    return min(3.0, cv / row['nav'])


def dat_forward(dd, i, k, hedge='beta', margin=1/3):
    """Hedged excess return on capital of buying at close i and holding k trading days (hedge rebalanced daily to
    the ratio at each previous close), net of costs; None if the window runs past the data or the hedge is
    undefined."""
    rows = dd['rows']
    if i + k >= len(rows):
        return None
    h0 = dat_hedge_ratio(rows[i], hedge)
    if h0 is None:
        return None
    cap = 1.0 + margin * h0
    tot = 0.0
    for j in range(i + 1, i + k + 1):
        a, b = rows[j - 1], rows[j]
        h = dat_hedge_ratio(a, hedge)
        if h is None:
            h = h0
        r = b['price'] / a['price'] - 1.0 - h * (b['coin_px'] / a['coin_px'] - 1.0) + h * b['funding']
        gap = (dt.date.fromisoformat(b['date']) - dt.date.fromisoformat(a['date'])).days
        tot += r * (1.0 / cap) - ssr_for(b['date']) * gap / 365.0
    c_in = dat_side_cost(rows[i]['adv_usd']) + 0.0005 * h0
    c_out = dat_side_cost(rows[i + k]['adv_usd']) + 0.0005 * h0
    return tot - (c_in + c_out) / cap



MNAV_BUCKETS = [(-1e9, 0.5), (0.5, 0.7), (0.7, 0.9), (0.9, 1.1), (1.1, 1.5), (1.5, 1e9)]


def dat_series_all(log=print):
    u = load_universe()
    out = {}
    for d in u['dats']:
        dd = dat_daily(d)
        if dd and dd['rows']:
            out[d['ticker']] = dd
    return out


def dat_flags(tk, row):
    fl = []
    if tk in NON_PURE:
        fl.append('non-pure: ' + NON_PURE[tk])
    if tk == '3350.T':
        fl.append('capital structure history not reliable (debt/preferred from a dashboard, currency unclear before 2026-10)')
    for k in ('true', 'naive'):
        v = row.get(k)
        if v is not None and v < 0.2:
            fl.append('implausible %s mNAV %.2f: asset existence/ownership or share count not verified' % (k, v))
            break
    return fl


def weekly_index(rows):
    """Indices of the last trading day of each ISO week."""
    out = []
    for i, r in enumerate(rows):
        if i + 1 == len(rows) or dt.date.fromisoformat(rows[i + 1]['date']).isocalendar()[:2] != \
                dt.date.fromisoformat(r['date']).isocalendar()[:2]:
            out.append(i)
    return out


def dat_signals(series, ks=(20, 40, 65), start='2025-11-01'):
    """Every DAT-week: ratios, flags and forward hedged excess returns (beta and asset hedges) over k days."""
    sig = []
    for tk, dd in series.items():
        rows = dd['rows']
        for i in weekly_index(rows):
            r = rows[i]
            if r['date'] < start:
                continue
            fl = dat_flags(tk, r)
            rec = {'ticker': tk, 'date': r['date'], 'i': i, 'true': r['true'], 'naive': r['naive'], 'ev': r['ev'],
                   'nav_neg': r['nav'] <= 0, 'adv_usd': r['adv_usd'], 'excluded': bool(fl), 'flags': fl}
            for k in ks:
                for hg in ('beta', 'asset'):
                    rec['fwd_%s_%d' % (hg, k)] = dat_forward(dd, i, k, hg)
                    for late, sk in (('1d', 1), ('1w', 5)):
                        if hg == 'beta':
                            v = dat_forward(dd, i + sk, k - sk, hg) if k > sk else None
                            rec['fwd_%s_%d_late%s' % (hg, k, late)] = v
            sig.append(rec)
    sig.sort(key=lambda x: (x['date'], x['ticker']))
    return sig


def _cohort_series(sig, pred, key):
    """Weekly cohort means of `key` over signals satisfying pred: [(date, mean, n)]."""
    by = {}
    for x in sig:
        if pred(x) and x.get(key) is not None:
            by.setdefault(x['date'][:10], []).append(x[key])
    # merge cohorts by ISO week (different exchanges end weeks on different days)
    wk = {}
    for d, vs in by.items():
        w = dt.date.fromisoformat(d).isocalendar()[:2]
        wk.setdefault(w, []).extend(vs)
    out = []
    for w in sorted(wk):
        vs = wk[w]
        monday = dt.date.fromisocalendar(w[0], w[1], 1).isoformat()
        out.append((monday, sum(vs) / len(vs), len(vs)))
    return out


def dat_panel(sig, ks=(20, 40, 65)):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import backtest as B
    buckets = []
    for per in ('in_sample', 'test'):
        for lo, hi in MNAV_BUCKETS:
            for k in ks:
                for hg in ('beta', 'asset'):
                    key = 'fwd_%s_%d' % (hg, k)
                    pred = lambda x, lo=lo, hi=hi, per=per: (not x['excluded']) and x['true'] is not None and \
                        lo <= x['true'] < hi and ((x['date'] < DAT_SPLIT) == (per == 'in_sample'))
                    cs = _cohort_series(sig, pred, key)
                    if not cs:
                        continue
                    vals = [m for _, m, _ in cs]
                    t, p = B.newey_west_t(vals, lags=max(1, k // 5)) if len(vals) > 3 else (None, None)
                    buckets.append({'period': per, 'bucket': '%s..%s' % (lo if lo > -1e8 else '-inf', hi if hi < 1e8 else 'inf'),
                                    'k': k, 'hedge': hg, 'weeks': len(cs), 'signals': sum(n for _, _, n in cs),
                                    'names': len({x['ticker'] for x in sig if pred(x) and x.get(key) is not None}),
                                    'mean_trade_excess': sum(vals) / len(vals), 'ann_excess': sum(vals) / len(vals) * 252.0 / k,
                                    'nw_t': t})
    # negative-equity and excluded counts
    return buckets


def dat_rules(sig, ks=(20, 40, 65), xs=(0.5, 0.6, 0.7, 0.8, 0.9, 1.0), metric='true', hedge='beta'):
    """Pre-committed variants: every week buy all eligible DATs whose `metric` mNAV < x, hold k trading days,
    hedged. Chosen on signal weeks before DAT_SPLIT by NW t of weekly cohort means; tested once on the rest."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import backtest as B
    res = {}
    for x in xs:
        for k in ks:
            key = 'fwd_%s_%d' % (hedge, k)
            name = '%s<%.1f|%dd' % (metric, x, k)
            pred = lambda r, x=x: (not r['excluded']) and r[metric] is not None and r[metric] < x
            cs = _cohort_series(sig, pred, key)
            ins = [m for d, m, _ in cs if d < DAT_SPLIT]
            oos = [m for d, m, _ in cs if d >= DAT_SPLIT]

            def st(v):
                if len(v) < 3:
                    return {'weeks': len(v)}
                t, pv = B.newey_west_t(v, lags=max(1, k // 5))
                return {'weeks': len(v), 'mean_trade_excess': sum(v) / len(v), 'ann_excess': sum(v) / len(v) * 252.0 / k,
                        'nw_t': t, 'p': pv, 'hit': sum(1 for z in v if z > 0) / len(v)}
            res[name] = {'x': x, 'k': k, 'in_sample': st(ins), 'test': st(oos),
                         'signals_in': sum(n for d, _, n in cs if d < DAT_SPLIT),
                         'signals_test': sum(n for d, _, n in cs if d >= DAT_SPLIT)}
    ok = {n: v for n, v in res.items() if v['in_sample'].get('nw_t') is not None}
    chosen = max(ok, key=lambda n: ok[n]['in_sample']['nw_t']) if ok else None
    ranked = sorted([n for n in res if res[n]['test'].get('nw_t') is not None], key=lambda n: -res[n]['test']['nw_t'])
    pv = [res[n]['test'].get('p') for n in res]
    rej, adj = B.bh(pv)
    late = {}
    if chosen:
        x, k = res[chosen]['x'], res[chosen]['k']
        for tag in ('1d', '1w'):
            key = 'fwd_%s_%d_late%s' % (hedge, k, tag) if hedge == 'beta' else None
            if not key:
                continue
            cs = _cohort_series(sig, lambda r: (not r['excluded']) and r[metric] is not None and r[metric] < x, key)
            oos = [m for d, m, _ in cs if d >= DAT_SPLIT]
            late[tag] = {'test_mean_trade_excess': sum(oos) / len(oos) if oos else None,
                         'share_kept': (sum(oos) / len(oos)) / res[chosen]['test']['mean_trade_excess']
                         if oos and res[chosen]['test'].get('mean_trade_excess') else None}
    return {'metric': metric, 'hedge': hedge, 'variants': res, 'chosen': chosen,
            'chosen_test': res[chosen]['test'] if chosen else None,
            'chosen_test_rank': ranked.index(chosen) + 1 if chosen in ranked else None, 'n_variants': len(res),
            'bh_test_survivors': [n for n, r in zip(res, rej) if r], 'late_entry': late}


def edgar_near(cik, date, days=5, forms=('8-K', '6-K', 'SC 13D', 'SC 13D/A', 'DEFA14A', 'DFAN14A', '8-K/A', '425')):
    if not cik:
        return None
    p = RAW / 'sec' / ('subs_%d.json.gz' % cik)
    if not p.exists():
        return None
    r = read_gz(p)['recent']
    d0 = dt.date.fromisoformat(date)
    best = None
    for f, fd, acc in zip(r['form'], r['filingDate'], r['accessionNumber']):
        if f not in forms:
            continue
        gap = (dt.date.fromisoformat(fd) - d0).days
        if abs(gap) <= days and (best is None or abs(gap) < abs(best['gap_days'])):
            best = {'form': f, 'filed': fd, 'accession': acc, 'gap_days': gap}
    return best


def first_hour_share(ticker, date):
    """Share of the event day's close-to-close move made by the end of the first trading hour (Yahoo 60m bars):
    a direct read of how much a one-hour-late entry misses."""
    p = RAW / 'yahoo_1h' / ('%s.json.gz' % ticker)
    if not p.exists():
        return None
    rows = read_gz(p)['rows']
    y = load_yahoo(ticker)
    if not y:
        return None
    try:
        j = next(k for k, d in enumerate(y['dates']) if d >= date)
    except StopIteration:
        return None
    if j == 0:
        return None
    d0, prev_close, close0 = y['dates'][j], y['close'][j - 1], y['close'][j]
    bars = [b for b in rows if dt.datetime.fromtimestamp(b[0], UTC).astimezone(NY).date().isoformat() == d0]
    if not bars or not bars[0][2]:
        return None
    first = bars[0][2]
    tot = close0 / prev_close - 1.0
    return {'day0': d0, 'move_day0': tot, 'move_first_hour': first / prev_close - 1.0,
            'share_in_first_hour': (first / prev_close - 1.0) / tot if abs(tot) > 1e-9 else None}


def price_only_series(d, start='2025-05-01'):
    """Fallback for event windows outside the look-through series: Yahoo price and coin price only, hedged 1:1 in
    dollars ('dollar' hedge via cps = price / coin price)."""
    y = load_yahoo(d['yahoo'])
    if not y:
        return None
    coin = d['coins'][0]
    exch, cur = y['meta'].get('exchangeName'), y['meta'].get('currency')
    rows, prev_ms, vols = [], None, []
    for date, close, vol in zip(y['dates'], y['close'], y['volume']):
        fx = fx_to_usd(cur, date)
        if fx is None:
            continue
        vols.append((vol or 0) * close * fx)
        if date < start:
            continue
        ms = close_ms_exch(date, exch)
        C = coin_at_ms(coin, ms)
        if C is None:
            continue
        fnd = funding_between(coin, prev_ms, ms) if prev_ms else 0.0
        prev_ms = ms
        P = close * fx
        rows.append({'date': date, 'price': P, 'coin_px': C, 'cps': P / C, 'nav': P, 'true': None, 'naive': None,
                     'funding': fnd, 'adv_usd': sum(vols[-60:]) / max(1, len(vols[-60:]))})
    return {'ticker': d['ticker'], 'coin': coin, 'rows': rows}


def dat_event_study(series, events, hs=(5, 20, 60)):
    out = []
    u = {d['ticker']: d for d in load_universe()['dats']}
    for e in events:
        dd = series.get(e['ticker'])
        rec = {k: e[k] for k in ('ticker', 'date', 'type', 'what')}
        rec['edgar'] = edgar_near((u.get(e['ticker']) or {}).get('cik'), e['date'])
        rec['first_hour'] = first_hour_share(e['ticker'], e['date'])
        rec['hedge'] = 'beta'
        i0 = index_of(dd['rows'], e['date']) if dd else None
        if dd is None or i0 is None or i0 == 0:
            dd = price_only_series(u[e['ticker']]) if e['ticker'] in u else None
            rec['hedge'] = 'dollar (no look-through NAV at the event)'
            i0 = index_of(dd['rows'], e['date']) if dd else None
            if dd is None or i0 is None or i0 == 0:
                rec['note'] = 'no price series around the event'
                out.append(rec)
                continue
        rows = dd['rows']
        rec['true_before'] = rows[i0 - 1]['true']
        rec['naive_before'] = rows[i0 - 1]['naive']
        rec['reaction_day0'] = dat_forward(dd, i0 - 1, 1, 'beta')
        for h in hs:
            rec['post_%d' % h] = dat_forward(dd, i0, h, 'beta')
            rec['post_%d_asset' % h] = dat_forward(dd, i0, h, 'asset')
            rec['late1d_%d' % h] = dat_forward(dd, i0 + 1, h - 1, 'beta')
            rec['late1w_%d' % h] = dat_forward(dd, i0 + 5, h - 5, 'beta') if h > 5 else None
        rec['true_after_20'] = rows[min(len(rows) - 1, i0 + 20)]['true']
        out.append(rec)
    return out


def event_summary(evs, split):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import backtest as B
    groups = {'buyback_auth': ('buyback_auth',), 'buyback_exec': ('buyback_exec',),
              'coin_sale': ('coin_sale_buyback', 'coin_sale_debt', 'coin_sale_exit'),
              'merger': ('merger', 'merger_close'), 'activist': ('activist', 'activist_settle'),
              'all_supportive': ('buyback_auth', 'buyback_exec', 'coin_sale_buyback', 'activist')}
    out = {}
    for g, types in groups.items():
        for per in ('early', 'late', 'all'):
            xs = [e for e in evs if e['type'] in types and
                  (per == 'all' or (e['date'] < split) == (per == 'early'))]
            row = {'n': len(xs)}
            for key in ('reaction_day0', 'post_5', 'post_20', 'post_60', 'late1d_20', 'late1w_20', 'post_20_asset'):
                v = [e[key] for e in xs if e.get(key) is not None]
                if v:
                    import statistics as stt
                    sd = stt.pstdev(v) if len(v) > 1 else None
                    row[key] = {'n': len(v), 'mean': sum(v) / len(v), 't': (sum(v) / len(v)) / (sd / math.sqrt(len(v)))
                                if sd else None}
            out['%s|%s' % (g, per)] = row
    # choose the holding window on early supportive events, test on late ones
    early = [e for e in evs if e['type'] in groups['all_supportive'] and e['date'] < split]
    late = [e for e in evs if e['type'] in groups['all_supportive'] and e['date'] >= split]

    def m(xs, key):
        v = [e[key] for e in xs if e.get(key) is not None]
        return sum(v) / len(v) if v else None
    choice = {h: m(early, 'post_%d' % h) for h in (5, 20, 60)}
    best = max((h for h in choice if choice[h] is not None), key=lambda h: choice[h], default=None)
    out['window_choice'] = {'in_sample_mean_by_h': choice, 'chosen_h': best,
                            'test_mean': m(late, 'post_%d' % best) if best else None,
                            'test_n': len([e for e in late if e.get('post_%d' % best) is not None]) if best else 0}
    return out



def strategy_kpi():
    fs = sorted((RAW / 'strategy').glob('mstrKpiData_*.json.gz'))
    if not fs:
        return None
    d = read_gz(fs[-1])
    k = (d.get('data') or [{}])[0]
    num = lambda x: fnum(str(x).replace(',', '')) if x is not None else None
    return {'fetched': d.get('fetched'), 'as_of': k.get('timeStampUtc'), 'price': num(k.get('price')),
            'market_cap_musd': num(k.get('marketCap')), 'ev_musd': num(k.get('entVal')), 'debt_musd': num(k.get('debt')),
            'pref_musd': num(k.get('pref'))}


def _xxi_live(d):
    """XXI has no instant share count in XBRL: shares from CoinGecko's entity record (holdings / amount per share),
    capital from the latest 10-Q anchor."""
    p = RAW / 'coingecko' / 'entity_XXI.json.gz'
    if not p.exists():
        return None
    ent = read_gz(p)
    h = next((x for x in ent.get('holdings') or [] if x.get('coin_id') == 'bitcoin'), None)
    if not h or not h.get('amount_per_share'):
        return None
    shares = h['amount'] / h['amount_per_share']
    y = load_yahoo(d['yahoo'])
    a = [x for x in dat_anchors(d) if x['filed'] <= y['dates'][-1]]
    a = a[-1] if a else {'cash': 0.0, 'debt': 0.0, 'pref': 0.0, 'end': None, 'filed': None}
    date = y['dates'][-1]
    C = coin_at_ms('BTC', close_ms_exch(date, 'NYQ'))
    lo = max(0, len(y['dates']) - 60)
    adv = sum(c * v for c, v in zip(y['close'][lo:], y['volume'][lo:])) / (len(y['dates']) - lo)
    P = y['close'][-1]
    cps = h['amount'] / shares
    nav = cps * C + (a['cash'] - a['debt'] - a['pref']) / shares
    row = {'date': date, 'price': P, 'coin_px': C, 'cps': cps, 'shares': shares, 'cash': a['cash'], 'debt': a['debt'],
           'pref': a['pref'], 'nav': nav, 'naive': P / (cps * C), 'ev': None, 'true': P / nav if nav > 0 else None,
           'funding': 0.0, 'adv_usd': adv, 'src': {'capital': 'xbrl %s filed %s; shares from CoinGecko entity' % (a['end'], a['filed'])}}
    return {'ticker': 'XXI', 'coin': 'BTC', 'rows': [row], 'holdings_source': 'coingecko entity'}


def dat_live(series, events):
    """One row per DAT on the last close: holdings, capital structure, three ratios, liquidity, hedge and stock-perp
    availability, flags and catalysts. MSTR and Metaplanet use their documented live capital structure."""
    u = load_universe()
    out = []
    by_ev = {}
    for e in events:
        by_ev.setdefault(e['ticker'], []).append('%s %s' % (e['date'], e['type']))
    for d in u['dats']:
        tk = d['ticker']
        dd = series.get(tk)
        rec = {'ticker': tk, 'coin': d['coins'][0], 'hip3': d.get('hip3'), 'binance_tradfi': d.get('binance_tradfi'),
               'note': d.get('note'), 'catalysts': by_ev.get(tk, [])}
        fu = load_funding(d['coins'][0])
        rec['coin_perp_binance'] = bool(fu[0]) and ymd(fu[0][-1]) >= '2026-10-01'
        if (not dd or not dd['rows'] or dd['rows'][-1]['date'] < '2026-10-01') and tk == 'XXI':
            dd = _xxi_live(d)
        if not dd or not dd['rows']:
            rec['status'] = 'no look-through series (no price, no 10-Q anchors, or no holdings)'
            out.append(rec)
            continue
        r = dd['rows'][-1]
        H = r['cps'] * r['shares']
        rec.update({'date': r['date'], 'price_usd': r['price'], 'shares': r['shares'], 'coins': H,
                    'coin_px': r['coin_px'], 'coin_value_usd': H * r['coin_px'], 'cash_usd': r['cash'],
                    'debt_usd': r['debt'], 'pref_usd': r['pref'], 'market_cap_usd': r['price'] * r['shares'],
                    'adv60_usd': r['adv_usd'], 'capital_source': r['src'].get('capital'),
                    'holdings_source': dd['holdings_source'] or r['src'].get('holdings')})
        if tk == 'MSTR':
            k = strategy_kpi()
            if k:
                mc = k['market_cap_musd'] * 1e6
                rec['shares'] = mc / k['price']
                rec['debt_usd'] = k['debt_musd'] * 1e6
                rec['pref_usd'] = k['pref_musd'] * 1e6
                rec['cash_usd'] = (k['market_cap_musd'] + k['debt_musd'] + k['pref_musd'] - k['ev_musd']) * 1e6
                rec['market_cap_usd'] = mc
                rec['capital_source'] = 'Strategy KPI feed %s (cash implied = market cap + debt + preferred - EV)' % k['as_of']
        if tk == '3350.T':
            st = st_company('3350.T')
            ds = (st['metrics'].get('debtSummary') or {})
            rec['debt_usd'] = fnum(ds.get('totalDebtUsd')) or rec['debt_usd']
            rec['pref_usd'] = sum(fnum(x.get('notionalUSD')) or 0 for x in st['metrics'].get('preferredStocks') or [])
            rec['capital_source'] = 'StrategyTracker debt summary and preferred notional (no SEC filings)'
        ov = (load_curated().get('dat_live_overrides') or {}).get(tk) or {}
        if ov.get('coins'):
            rec.update({'coins': ov['coins'], 'cash_usd': ov['cash_usd'], 'debt_usd': ov['debt_usd'],
                        'shares': ov['shares'], 'market_cap_usd': rec['price_usd'] * ov['shares'],
                        'coin_value_usd': ov['coins'] * rec['coin_px'], 'capital_source': 'documents: ' + ov['note'][:120]})
            alt = mnav_variants(rec['price_usd'], ov['shares'], ov['coins'], rec['coin_px'],
                                ov['cash_usd'] - ov.get('committed_to_illiquid_usd', 0.0), ov['debt_usd'], rec['pref_usd'])
            rec['mnav_true_illiquid_at_zero'] = alt['true']
        stale = ((load_curated().get('stale_dashboard_checks') or {}).get('flags') or {}).get(tk)
        if stale:
            rec.setdefault('flags_extra', []).append('holdings check: ' + stale)
        f = sec_facts(d['cik']) if d.get('cik') else None
        fv = xbrl_original(f, 'CryptoAssetFairValue') if f else {}
        if fv:
            e_, x_ = sorted(fv.items())[-1]
            cpx = coin_at_ms(d['coins'][0], close_ms_exch(e_, 'NMS'))
            hs_, _ = holdings_series(d)
            dash = asof(hs_, e_) if hs_ else None
            if cpx and dash and dash[1]:
                rec['fv_check'] = {'period': e_, 'fair_value_usd': fnum(x_['val']), 'implied_coins': fnum(x_['val']) / cpx,
                                   'dashboard_coins': dash[1], 'ratio': fnum(x_['val']) / cpx / dash[1]}
        mv = mnav_variants(rec['price_usd'], rec['shares'], rec['coins'], rec['coin_px'], rec['cash_usd'],
                           rec['debt_usd'], rec['pref_usd'])
        rec.update({'mnav_naive': mv['naive'], 'mnav_ev': mv['ev'], 'mnav_true': mv['true'],
                    'nav_per_share': mv['nav_per_share'], 'negative_equity': mv['negative_equity']})
        if rec.get('fv_check') and not ov.get('coins'):
            mf = mnav_variants(rec['price_usd'], rec['shares'], rec['fv_check']['implied_coins'], rec['coin_px'],
                               rec['cash_usd'], rec['debt_usd'], rec['pref_usd'])
            rec['mnav_true_10q_holdings'] = mf['true']
        rec['flags'] = dat_flags(tk, {'true': mv['true'], 'naive': mv['naive']}) + rec.pop('flags_extra', [])
        if not rec['coin_perp_binance']:
            rec['flags'].append('no live Binance perp on %s (hedge leg unavailable there)' % d['coins'][0])
        rec['capacity_usd'] = 0.10 * rec['adv60_usd'] * 5
        out.append(rec)
    out.sort(key=lambda x: (x.get('mnav_true') is None, x.get('mnav_true') or 9))
    return out



def _clean(o):
    """JSON-safe copy: drop long per-day lists and round floats."""
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items() if k not in ('returns', 'excess', 'dates', 'rows')}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, float):
        return None if not math.isfinite(o) else round(o, 6)
    return o


def mstr_verification():
    """MSTR's headline inputs from independent sources: preferred notional (StrategyTracker per-series, Strategy's
    KPI feed, XBRL temporary equity), debt (KPI vs XBRL), shares (KPI market cap / price vs StrategyTracker), BTC
    (StrategyTracker, CoinGecko, 10-Q units, 10-Q fair value / BTC price)."""
    k = strategy_kpi() or {}
    st = st_company('MSTR')
    prefs = {x.get('ticker'): fnum(x.get('notionalUSD')) for x in st['metrics'].get('preferredStocks') or []}
    f = sec_facts(1050446)
    te = sorted(xbrl_original(f, 'TemporaryEquityCarryingAmountAttributableToParent').items())[-1]
    ltd = sorted(xbrl_original(f, 'LongTermDebt').items())[-1]
    units = sorted(xbrl_original(f, 'CryptoAssetNumberOfUnits').items())[-1]
    fv = sorted(xbrl_original(f, 'CryptoAssetFairValue').items())[-1]
    cpx = coin_at_ms('BTC', close_ms_exch(fv[0], 'NMS'))
    cg = read_gz(RAW / 'coingecko' / 'entity_MSTR.json.gz') if (RAW / 'coingecko' / 'entity_MSTR.json.gz').exists() else {}
    cgb = next((x['amount'] for x in cg.get('holdings') or [] if x.get('coin_id') == 'bitcoin'), None)
    return {'preferred_usd': {'strategytracker_sum': sum(v for v in prefs.values() if v), 'strategytracker_series': prefs,
                              'strategy_kpi': (k.get('pref_musd') or 0) * 1e6, 'xbrl_temporary_equity': {'end': te[0], 'val': fnum(te[1]['val'])}},
            'debt_usd': {'strategy_kpi': (k.get('debt_musd') or 0) * 1e6, 'xbrl_long_term_debt': {'end': ltd[0], 'val': fnum(ltd[1]['val'])}},
            'shares': {'kpi_market_cap_over_price': (k.get('market_cap_musd') or 0) * 1e6 / k['price'] if k.get('price') else None,
                       'strategytracker': st['metrics'].get('latestTotalShares')},
            'btc': {'strategytracker': st['metrics'].get('latestBtcBalance'), 'coingecko': cgb,
                    'xbrl_units': {'end': units[0], 'val': fnum(units[1]['val'])},
                    'xbrl_fair_value_over_price': {'end': fv[0], 'val': fnum(fv[1]['val']) / cpx if cpx else None}},
            'kpi': k}


def cmd_analyze(args):
    t0 = time.time()
    cur = load_curated()
    res = {'generated': dt.datetime.now(UTC).isoformat(timespec='seconds'),
           'benchmark': {'ssr_now': SSR_NOW, 'ssr_paid_by_year': SSR_PAID},
           'conventions': {'margin_on_short': 1 / 3, 'perp_fee_per_side': 0.0005,
                           'trust_cost_model': 'half Abdi-Ranaldo spread, floored by ADV tier (>=$10M 5bp, $1-10M 25bp, <$1M 100bp)',
                           'dat_cost_model': 'ADV tiers: >=$100M 5bp, $10-100M 10bp, $1-10M 30bp, <$1M 100bp per side',
                           'capacity': '10% of trailing-60-day dollar volume x 5 days'}}
    # ---- (a) trusts
    tr = analyze_trusts(log=lambda *a: None)
    u = load_universe()
    series = {}
    for t in u['trusts']:
        if t['kind'] == 'single':
            ts = trust_series(t)
            if ts and ts['rows']:
                series[t['ticker']] = ts
    dollars = {}
    for name, x, cat, hedge in (('dollar|disc<=-5%|any', 0.05, False, 'dollar'), ('dollar|disc<=-10%|any', 0.10, False, 'dollar'),
                                ('dollar|disc<=-10%|filing', 0.10, True, 'dollar')):
        _, lg = rule_backtest(series, cur['trust_events'], x, cat, start='2019-09-10', hedge=hedge)
        trades = rule_trade_dollars(series, lg, hedge=hedge, since=TRUST_SPLIT)
        yrs = (dt.date.fromisoformat(max(r['date'] for ts in series.values() for r in ts['rows'][-1:])) -
               dt.date.fromisoformat(TRUST_SPLIT)).days / 365.25
        by = {}
        for t_ in trades:
            b = by.setdefault(t_['ticker'], {'trades': 0, 'excess_usd': 0.0, 'max_capital_usd': 0.0})
            b['trades'] += 1
            b['excess_usd'] += t_['excess_usd']
            b['max_capital_usd'] = max(b['max_capital_usd'], t_['capital_usd'])
        dollars[name] = {'test_trades': len(trades), 'excess_usd_total': sum(t_['excess_usd'] for t_ in trades),
                         'excess_usd_per_year': sum(t_['excess_usd'] for t_ in trades) / yrs,
                         'mean_trade_excess_on_capital': sum(t_['excess_on_capital'] for t_ in trades) / len(trades) if trades else None,
                         'hit': sum(1 for t_ in trades if t_['excess_on_capital'] > 0) / len(trades) if trades else None,
                         'by_trust': by, 'trades': trades}
    tr['rule_dollars_test'] = dollars
    res['trusts'] = tr
    # ---- (b) DATs
    ds = dat_series_all(log=lambda *a: None)
    sig = dat_signals(ds)
    flagged = set(((cur.get('stale_dashboard_checks') or {}).get('flags') or {}).keys())
    sig_robust = [dict(x, excluded=x['excluded'] or x['ticker'] in flagged) for x in sig]
    dat = {'coverage': {k: [v['rows'][0]['date'], v['rows'][-1]['date'], len(v['rows']), v['holdings_source']] for k, v in ds.items()},
           'signals': {'n': len(sig), 'eligible': sum(1 for x in sig if not x['excluded']),
                       'excluded_reasons': sorted({f_ for x in sig for f_ in x['flags']}),
                       'eligible_robust': sum(1 for x in sig_robust if not x['excluded'])},
           'panel': dat_panel(sig), 'panel_robust': dat_panel(sig_robust), 'rules': {}, 'rules_robust': {}}
    for hedge in ('beta', 'asset'):
        for metric in ('true', 'naive'):
            dat['rules']['%s|%s' % (metric, hedge)] = dat_rules(sig, metric=metric, hedge=hedge)
            dat['rules_robust']['%s|%s' % (metric, hedge)] = dat_rules(sig_robust, metric=metric, hedge=hedge)
    evs = dat_event_study(ds, cur['dat_events'])
    dat['events'] = evs
    dat['event_summary'] = event_summary(evs, cur['dat_event_split'])
    fh = [e['first_hour']['share_in_first_hour'] for e in evs if e.get('first_hour') and
          e['first_hour'].get('share_in_first_hour') is not None]
    fh.sort()
    dat['first_hour_share'] = {'n': len(fh), 'median': fh[len(fh) // 2] if fh else None}
    dat['live'] = dat_live(ds, cur['dat_events'])
    dat['verification_mstr'] = mstr_verification()
    res['dats'] = dat
    res['runtime_seconds'] = round(time.time() - t0, 1)
    write_json(OUT / 'analysis.json', _clean(res))
    print('analysis.json written in %.1fs' % (time.time() - t0))



def _p(v, nd=1, pct=True, sign=True):
    if v is None:
        return '—'
    if pct:
        return ('%+.*f%%' if sign else '%.*f%%') % (nd, v * 100)
    return '%.*f' % (nd, v)


def _m(v):
    return '—' if v is None else ('$%.1fM' % (v / 1e6) if abs(v) < 1e9 else '$%.2fB' % (v / 1e9))


def cmd_render(args):
    a = json.loads((OUT / 'analysis.json').read_text())
    t, d = a['trusts'], a['dats']
    L = ['# nav_wrappers — tables (generated %s)' % a['generated'], '',
         'Every number is from `analysis.json`; method in `scripts/nav_wrappers.py`; sources in `manifest.json`.', '']
    L += ['## (a) Trusts', '', '### A1. NAV check: coin per share (XBRL) x Binance at 16:00 New York vs the sponsor\'s NAV per share', '',
          '| trust | quarter-ends | median abs error | max abs error | anchors replaced | implied fee range |', '|---|---:|---:|---:|---:|---|']
    for tk, v in t['verification'].items():
        c = v['nav_check']
        L.append('| %s | %d | %s | %s | %d | %s..%s |' % (tk, c['n'], _p(c['median_abs_err'], 2, sign=False),
                                                       _p(c['max_abs_err'], 2, sign=False), len(v['replaced']),
                                                       _p(v['implied_fee_min'], 2, sign=False), _p(v['implied_fee_max'], 2, sign=False)))
    L += ['', '### A2. Conversion events (long trust, short coin perp; enter at the first close on or after the filing, exit at the first exchange close; open trades marked 2026-10-09)', '',
          '| trust | set | filing | disc at filing | worst (date) | last OTC | at exit | excess on capital, NAV hedge | per year | max DD | $ hedge excess | funding sum | 1d late kept | 1w late kept | ADV at filing |',
          '|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in t['events']:
        b = e.get('base') or {}
        bd = e.get('base_dollar_hedge') or {}
        lt = e.get('late') or {}
        L.append('| %s | %s | %s | %s | %s (%s) | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            e['ticker'], e['set'], e['filing_public'], _p(e['disc_at_filing']), _p(e['worst_disc']), e['worst_disc_date'],
            _p(e['disc_last_otc']), _p(e['disc_exit']), _p(b.get('excess_on_capital')), _p(b.get('ann_excess')),
            _p(b.get('max_drawdown'), sign=False), _p(bd.get('excess_on_capital')), _p(b.get('funding_received_sum')),
            _p((lt.get('1d') or {}).get('share_of_excess_kept'), 0, sign=False), _p((lt.get('1w') or {}).get('share_of_excess_kept'), 0, sign=False),
            _m(e['adv_usd_at_filing'])))
    ch = t['entry_choice']
    L += ['', '### A3. Entry rule chosen on the early conversions, tested on 2025-26 (pooled excess per year of capital)', '',
          '| variant | early n | early | late n | late | late per trade | pending n | pending per trade (marked) |', '|---|---:|---:|---:|---:|---|---:|---|']
    for n in ch['in_sample']:
        i, o, pd = ch['in_sample'][n], ch['out_of_sample'][n], ch['pending_mark_to_market'][n]
        L.append('| %s%s | %s | %s | %s | %s | %s | %s | %s |' % (n, ' (chosen)' if n == ch['chosen'] else '', i.get('n'), _p(i.get('pooled_ann_excess')),
                                                         o.get('n'), _p(o.get('pooled_ann_excess')),
                                                         ', '.join('%s %s' % (k, _p(v)) for k, v in (o.get('per_trade') or [])),
                                                         pd.get('n'), ', '.join('%s %s' % (k, _p(v)) for k, v in (pd.get('per_trade') or []))))
    for key, title in (('panel_dollar_hedge', 'dollar hedge'), ('panel', 'NAV hedge')):
        L += ['', '### A4. Discount buckets, forward 63-day hedged excess on capital (%s; early < 2025, late >= 2025)' % title, '',
              '| period | state | discount | trust-days | trusts | mean | NW t | hit |', '|---|---|---|---:|---:|---:|---:|---:|']
        for c in t[key]:
            if c['h'] == 63:
                L.append('| %s | %s | %s | %d | %d | %s | %s | %.0f%% |' % (c['period'], c['state'], c['bucket'], c['n_days'], c['n_trusts'],
                                                                     _p(c['mean_fwd_excess']), _p(c['nw_t'], 2, pct=False), c['hit'] * 100))
    for key, title in (('rules_dollar_hedge', 'dollar hedge'), ('rules', 'NAV hedge')):
        r = t[key]
        ct = r['choose_then_test']
        L += ['', '### A5. Daily trust rules (%s): chosen on 2019-09..2024-12, tested 2025-01..2026-10' % title, '',
              'Chosen: **%s**; test %s a year over the savings rate (calendar), NW t %s, rank %s of %s, deflated Sharpe %s, BH survivors (full sample): %s. Late entry keeps %s (1 day) and %s (1 week) of the test excess.' % (
                  r['chosen'], _p(ct['out_of_sample'].get('ann_return')), _p(ct.get('oos_t'), 2, pct=False), ct.get('oos_rank'),
                  ct.get('n_variants'), _p(ct.get('deflated_sharpe_in_sample'), 2, pct=False), ', '.join(ct.get('bh_survivors_full_sample') or []) or 'none',
                  _p(r['late_entry']['1d']['test_total_excess'] / r['chosen_totals']['test'] if r['chosen_totals']['test'] else None, 0, sign=False),
                  _p(r['late_entry']['1w']['test_total_excess'] / r['chosen_totals']['test'] if r['chosen_totals']['test'] else None, 0, sign=False)), '',
              '| variant | in-sample excess / yr | test excess / yr | test active days |', '|---|---:|---:|---:|']
        for n, v in r['variants'].items():
            L.append('| %s | %s | %s | %d |' % (n, _p(v['insample']['calendar_ann_excess']), _p(v['test']['calendar_ann_excess']), v['test']['active_days']))
    L += ['', '### A6. Dollar P&L of test-period trades at capacity (10% of 60-day ADV x 5 days), dollar hedge', '',
          '| rule | trades | excess $ / yr | mean trade excess | hit | by trust (excess $) |', '|---|---:|---:|---:|---:|---|']
    for n, v in t['rule_dollars_test'].items():
        L.append('| %s | %d | %s | %s | %s | %s |' % (n, v['test_trades'], _m(v['excess_usd_per_year']), _p(v['mean_trade_excess_on_capital']),
                                                  _p(v['hit'], 0, sign=False), ', '.join('%s %s' % (k, _m(x['excess_usd'])) for k, x in v['by_trust'].items())))
    L += ['', '### A7. Trusts on 2026-10-09', '', '| trust | coin | venue | status | filing | close | NAV | discount | ADV60 | spread est. | capacity |', '|---|---|---|---|---|---:|---:|---:|---:|---:|---:|']
    for r in t['live']:
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (r['ticker'], r.get('coin') or 'basket', r.get('exchange'), r.get('status'),
                                                                  r.get('filing') or '—', _p(r.get('close'), 2, pct=False), _p(r.get('nav'), 2, pct=False),
                                                                  _p(r.get('disc')), _m(r.get('adv60_usd')), _p(r.get('spread_est'), 1, sign=False), _m(r.get('capacity_usd'))))
    L += ['', '### A8. Basket trusts: sponsor NAV per share at quarter-ends vs the close', '']
    for b in t['baskets']:
        if b.get('quarter_ends'):
            L.append('- %s (filing %s, listed %s): ' % (b['ticker'], b.get('filing'), b.get('listed')) +
                     ', '.join('%s %s' % (q['end'], _p(q['disc'])) for q in b['quarter_ends'][-8:]))
    L += ['', '## (b) DATs', '', '### B1. Live: three ratios on 2026-10-09 (sorted by true mNAV; flags in analysis.json)', '',
          '| DAT | coin | coins | coin value | cash | debt | preferred | market cap | naive | EV | true | true, 10-Q holdings | ADV60 | stock perp | 10-Q check | flags |',
          '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|']
    for r in d['live']:
        if 'mnav_true' not in r and 'mnav_naive' not in r:
            continue
        fv = r.get('fv_check') or {}
        tv = _p(r.get('mnav_true'), 2, pct=False)
        if r.get('mnav_true_illiquid_at_zero'):
            tv += ' (%s)' % _p(r['mnav_true_illiquid_at_zero'], 2, pct=False)
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['ticker'], r['coin'], '{:,.0f}'.format(r['coins']), _m(r['coin_value_usd']), _m(r['cash_usd']), _m(r['debt_usd']), _m(r['pref_usd']),
            _m(r['market_cap_usd']), _p(r.get('mnav_naive'), 2, pct=False), _p(r.get('mnav_ev'), 2, pct=False), tv,
            _p(r.get('mnav_true_10q_holdings'), 2, pct=False), _m(r['adv60_usd']),
            r.get('binance_tradfi') or r.get('hip3') or '—', _p(fv.get('ratio'), 2, pct=False), '; '.join(f[:60] for f in r.get('flags') or [])))
    for key, title in (('panel', 'all eligible names'), ('panel_robust', 'excluding names with stale or unresolved holdings')):
        L += ['', '### B2. True-mNAV buckets, forward hedged excess (beta hedge, 40 trading days; %s; split %s)' % (title, DAT_SPLIT), '',
              '| period | true mNAV | weeks | signals | names | mean per trade | NW t |', '|---|---|---:|---:|---:|---:|---:|']
        for b in d[key]:
            if b['hedge'] == 'beta' and b['k'] == 40:
                L.append('| %s | %s | %d | %d | %d | %s | %s |' % (b['period'], b['bucket'], b['weeks'], b['signals'], b['names'],
                                                              _p(b['mean_trade_excess']), _p(b['nw_t'], 2, pct=False)))
    L += ['', '### B3. DAT rules: buy every week all names below x, hold k days (18 variants per line; chosen in sample by NW t)', '',
          '| universe | signal / hedge | chosen | in-sample per trade (t) | test per trade (t) | test rank | late 1d kept |', '|---|---|---|---|---|---:|---:|']
    for key, uni in (('rules', 'all eligible'), ('rules_robust', 'robust')):
        for n, r in d[key].items():
            v = r['variants'][r['chosen']]
            L.append('| %s | %s | %s | %s (%s) | %s (%s) | %s | %s |' % (uni, n, r['chosen'], _p(v['in_sample'].get('mean_trade_excess')),
                                                                     _p(v['in_sample'].get('nw_t'), 2, pct=False), _p(v['test'].get('mean_trade_excess')),
                                                                     _p(v['test'].get('nw_t'), 2, pct=False), r['chosen_test_rank'],
                                                                     _p((r['late_entry'].get('1d') or {}).get('share_kept'), 0, sign=False)))
    L += ['', '### B4. Events (hedged excess on capital; day 0 = first close on or after the announcement; dollar hedge where no NAV series)', '',
          '| DAT | date | type | EDGAR filing | true mNAV before | day-0 reaction | +5d | +20d | +60d | 20d, 1 day late | 20d, 1 week late | first-hour share of day-0 move |',
          '|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in d['events']:
        ed = e.get('edgar') or {}
        fh = e.get('first_hour') or {}
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            e['ticker'], e['date'], e['type'], ('%s %s' % (ed.get('form'), ed.get('filed'))) if ed else '—', _p(e.get('true_before'), 2, pct=False),
            _p(e.get('reaction_day0')), _p(e.get('post_5')), _p(e.get('post_20')), _p(e.get('post_60')), _p(e.get('late1d_20')),
            _p(e.get('late1w_20')), _p(fh.get('share_in_first_hour'), 0, sign=False)))
    L += ['', '| group | n | day-0 | +20d (n, t) | +60d (n, t) | 20d 1 day late | 20d 1 week late |', '|---|---:|---:|---|---|---:|---:|']
    for g, v in d['event_summary'].items():
        if g == 'window_choice' or not v.get('n'):
            continue
        f = lambda k: ('%s (%d, %s)' % (_p(v[k]['mean']), v[k]['n'], _p(v[k]['t'], 2, pct=False))) if k in v else '—'
        L.append('| %s | %d | %s | %s | %s | %s | %s |' % (g, v['n'], _p((v.get('reaction_day0') or {}).get('mean')), f('post_20'), f('post_60'),
                                                        _p((v.get('late1d_20') or {}).get('mean')), _p((v.get('late1w_20') or {}).get('mean'))))
    wc = d['event_summary']['window_choice']
    L += ['', 'Holding window chosen on events before %s: %s days (in-sample means %s); test mean %s over %d events.' % (
        load_curated().get('dat_event_split'), wc['chosen_h'], ', '.join('%s: %s' % (k, _p(v)) for k, v in wc['in_sample_mean_by_h'].items()),
        _p(wc['test_mean']), wc['test_n']),
          'First trading hour carries a median %s of the event day\'s move (%d events with hourly bars).' % (_p(d['first_hour_share']['median'], 0, sign=False), d['first_hour_share']['n'])]
    v = d['verification_mstr']
    L += ['', '### B5. Independent-path check: Strategy (MSTR)', '',
          '- BTC: StrategyTracker %s; CoinGecko %s; 10-Q units %s at %s; 10-Q fair value / BTC price %s.' % (
              '{:,.0f}'.format(v['btc']['strategytracker']), '{:,.0f}'.format(v['btc']['coingecko'] or 0), '{:,.0f}'.format(v['btc']['xbrl_units']['val']),
              v['btc']['xbrl_units']['end'], '{:,.0f}'.format(v['btc']['xbrl_fair_value_over_price']['val'] or 0)),
          '- Preferred: StrategyTracker per-series sum %s; Strategy KPI %s; XBRL temporary equity %s at %s.' % (
              _m(v['preferred_usd']['strategytracker_sum']), _m(v['preferred_usd']['strategy_kpi']), _m(v['preferred_usd']['xbrl_temporary_equity']['val']),
              v['preferred_usd']['xbrl_temporary_equity']['end']),
          '- Debt: KPI %s; XBRL LongTermDebt %s. Shares: KPI market cap / price %s; StrategyTracker %s.' % (
              _m(v['debt_usd']['strategy_kpi']), _m(v['debt_usd']['xbrl_long_term_debt']['val']),
              '{:,.0f}'.format(v['shares']['kpi_market_cap_over_price']), '{:,.0f}'.format(v['shares']['strategytracker']))]
    (OUT / 'tables.md').write_text('\n'.join(L) + '\n')
    print('tables.md written (%d lines)' % len(L))


# ---------------------------------------------------------------------------------------------- forward test (DATs)

# The study's next step 1: EMPD and BNC pre-registered and scored at +20 and +60 sessions, read against a basket of the
# other discounted DATs of the live table (no dated catalyst) and against MSTR. The rule is the study's own trade
# (dat_forward: beta hedge rebalanced at each close, capital 1 + 1/3 of the short, ADV-tier stock costs, 5bp perp,
# excess over the savings rate paid) on holdings and capital structure frozen at registration. A registered row is
# never edited and carries its own parameters, so a later change to this file cannot re-score it; a later filing that
# moves the holdings is a fact about the trade, not a reason to re-register.
DAT_FORWARD_LEDGER = ROOT / 'research' / 'dat_events_forward.jsonl'
WATCH_DIR = ROOT / 'research' / '2026-10-11' / 'watch_forward'
DAT_FORWARD_HORIZONS = (20, 60)
DAT_FORWARD_RULE = {
    'id': 'dat-discount-catalyst',
    'study': 'research/2026-10-10/nav_wrappers (findings.md, Next 1; live table of the 2026-10-09 close)',
    'entry': 'the first regular-session close (16:00 New York; 13:00 on early-close days) strictly after registration',
    'position': 'long $1 of the stock at the entry close; short h x $1 of the coin on its Binance USD-M perp',
    'hedge': "beta, the study's main DAT hedge: h = coin value / (coin value + cash - debt - preferred), capped at 3, "
             'from the holdings and capital structure frozen at registration and the coin price at each close; '
             'rebalanced at every close (dat_forward)',
    'coin_price': "Binance close of the hour ending at the stock close: spot where listed, else the perp (the study's "
                  "convention); a variant marks the hedge leg on the perp's own close",
    'funding': 'Binance funding settled in (previous close, close], received by the short when positive',
    'capital': '1 + margin x h at entry, margin 1/3',
    'costs': 'stock per side by trailing-60-session dollar volume (>= $100M 5bp, $10-100M 10bp, $1-10M 30bp, '
             '< $1M 100bp) at entry and at exit; perp 5bp per side on h at entry',
    'benchmark': 'savings rate paid (2026: 3.7%; after: 3.8%) per calendar day held',
    'horizons': "the 20th and 60th NYSE session after the entry close (the study's +20d/+60d are trading-day rows)",
    'nav_ratio': 'true mNAV = price / look-through NAV per share on the frozen holdings and capital structure; EMPD '
                 'also with its $65M AI commitment at zero',
    'placebo': 'equal-weight basket of the other discounted DATs of the live table with a Binance coin perp and no '
               'dated catalyst (SKYA, HYPD, HSDT, NAKA, FWDI), the same rule each; MSTR as the sector benchmark',
    'kill': 'once all four candidate horizons are scored: mean +60-session excess over the placebo basket not positive',
    'promote': 'both candidates above the savings rate and above the placebo basket at +60 sessions, and both true mNAV '
               'ratios higher than at entry: then pre-register the next dated-catalyst DATs (n = 2 is an anecdote, '
               'not a book entry)',
    'not_applied': "the study's DAT exits (coins sold for anything but buybacks; 3 months) are not applied: +60 "
                   'sessions is the 3 months, and coin sales are recorded as notes',
}
DAT_FORWARD_PARAMS = {'margin': 1 / 3, 'perp_fee': 0.0005, 'hedge_cap': 3.0,
                      'stock_cost_tiers': [[1e8, 0.0005], [1e7, 0.001], [1e6, 0.003], [0.0, 0.01]],
                      'ssr_paid': {str(k): v for k, v in SSR_PAID.items()}, 'ssr_default': SSR_NOW,
                      'horizons': list(DAT_FORWARD_HORIZONS), 'adv_sessions': 60}
DAT_FORWARD_NAMES = {
    'EMPD': {'role': 'candidate',
             'catalyst': "ATG Capital proxy fight: Delaware Chancery (2026-08-28) and Supreme Court (2026-10-08) backed "
                         "ATG's nominees; annual meeting vote 2026-10-14 per the study's sources (ISS, Glass Lewis, "
                         'Egan-Jones back ATG); true mNAV 0.56, 0.97 with the AI stake at zero'},
    'BNC': {'role': 'candidate',
            'catalyst': '$250M buyback authorised 2025-09-22; YZi Labs settlement and three new directors 2026-06-24; '
                        'Binance TradFi lists a BNCUSDT stock perp'},
    'SKYA': {'role': 'placebo'}, 'HYPD': {'role': 'placebo'}, 'HSDT': {'role': 'placebo'},
    'NAKA': {'role': 'placebo'}, 'FWDI': {'role': 'placebo'},
    'MSTR': {'role': 'benchmark'},
}
DAT_FORWARD_MIN = 2 * len(DAT_FORWARD_HORIZONS)       # candidate horizon scores before any verdict
NYSE_HOLIDAYS = {'2026-01-01', '2026-01-19', '2026-02-16', '2026-04-03', '2026-05-25', '2026-06-19', '2026-07-03',
                 '2026-09-07', '2026-11-26', '2026-12-25', '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26',
                 '2027-05-31', '2027-06-18', '2027-07-05', '2027-09-06', '2027-11-25', '2027-12-24'}
NYSE_EARLY_CLOSE = {'2026-11-27', '2026-12-24', '2027-11-26'}      # 13:00 New York
SETTLE_MS = 30 * 60 * 1000                                         # a close is final 30 minutes after it
FWD_DAY_MS = 86400000
DAT_PLACEBO_MIN = 3                                                # placebo names scored before a comparison


def is_session(date):
    d = dt.date.fromisoformat(date)
    return d.weekday() < 5 and date not in NYSE_HOLIDAYS


def session_close_ms(date):
    """Epoch ms of the regular-session close on `date` (16:00 New York, 13:00 on early-close days)."""
    t = dt.datetime.combine(dt.date.fromisoformat(date), dt.time(13 if date in NYSE_EARLY_CLOSE else 16, 0), NY)
    return int(t.timestamp() * 1000)


def next_close_after(ms):
    """(date, close ms) of the first session close strictly after `ms`."""
    d = dt.datetime.fromtimestamp(ms / 1000.0, NY).date()
    for _ in range(15):
        s = d.isoformat()
        if is_session(s) and session_close_ms(s) > ms:
            return s, session_close_ms(s)
        d += dt.timedelta(days=1)
    raise ValueError('no session within 15 days of %s' % ms)


def sessions_after(date, n):
    """The n NYSE sessions after `date` (holiday calendar to 2027)."""
    out, d = [], dt.date.fromisoformat(date)
    while len(out) < n:
        d += dt.timedelta(days=1)
        if is_session(d.isoformat()):
            out.append(d.isoformat())
    return out


def frozen_beta(inputs, coin_px, cap=3.0):
    """The study's beta hedge on frozen inputs: coin notional short per $ of stock at constant true mNAV."""
    cv = inputs['coins'] * coin_px
    nav = cv + inputs['cash_usd'] - inputs['debt_usd'] - inputs['pref_usd']
    return min(cap, cv / nav) if nav > 0 else None


def frozen_true_mnav(inputs, price, coin_px, share_factor=1.0, illiquid_at_zero=False):
    """price / look-through NAV per share on frozen inputs (shares x share_factor: splits after registration)."""
    cash = inputs['cash_usd'] - ((inputs.get('committed_to_illiquid_usd') or 0.0) if illiquid_at_zero else 0.0)
    eq = inputs['coins'] * coin_px + cash - inputs['debt_usd'] - inputs['pref_usd']
    return price * inputs['shares'] * share_factor / eq if eq > 0 else None


def stock_side_cost(adv, tiers):
    for lo, c in tiers:
        if adv >= lo:
            return c
    return tiers[-1][1]


def dat_forward_trade(rows, i0, k, inputs, params, leg='coin_px'):
    """The frozen rule from session i0 to i0 + k: dat_forward's arithmetic on frozen inputs. rows: session dicts with
    date, price, coin_px, perp_px, funding (in (previous close, close]) and adv_usd. `leg` is the price the hedge is
    marked on ('coin_px' as the study; 'perp_px' the perp's own close). None when a price is missing."""
    if i0 + k >= len(rows):
        return None
    if any(rows[j].get('coin_px') is None or rows[j].get(leg) is None or rows[j].get('price') is None
           for j in range(i0, i0 + k + 1)):
        return None
    h0 = frozen_beta(inputs, rows[i0]['coin_px'], params['hedge_cap'])
    if h0 is None:
        return None
    cap = 1.0 + params['margin'] * h0
    parts = {'stock': 0.0, 'hedge': 0.0, 'funding': 0.0, 'savings': 0.0}
    tot = 0.0
    for j in range(i0 + 1, i0 + k + 1):
        a, b = rows[j - 1], rows[j]
        h = frozen_beta(inputs, a['coin_px'], params['hedge_cap'])
        if h is None:
            h = h0
        rs = b['price'] / a['price'] - 1.0
        rh = -h * (b[leg] / a[leg] - 1.0)
        rf = h * b['funding']
        gap = (dt.date.fromisoformat(b['date']) - dt.date.fromisoformat(a['date'])).days
        sv = params['ssr_paid'].get(b['date'][:4], params['ssr_default']) * gap / 365.0
        tot += (rs + rh + rf) / cap - sv
        parts['stock'] += rs / cap
        parts['hedge'] += rh / cap
        parts['funding'] += rf / cap
        parts['savings'] -= sv
    c_in = stock_side_cost(rows[i0]['adv_usd'], params['stock_cost_tiers']) + params['perp_fee'] * h0
    c_out = stock_side_cost(rows[i0 + k]['adv_usd'], params['stock_cost_tiers']) + params['perp_fee'] * h0
    parts['costs'] = -(c_in + c_out) / cap
    return {'excess': tot + parts['costs'], 'h0': h0, 'capital': cap, 'parts': parts,
            'stock_return': rows[i0 + k]['price'] / rows[i0]['price'] - 1.0,
            'coin_return': rows[i0 + k][leg] / rows[i0][leg] - 1.0,
            'calendar_days': (dt.date.fromisoformat(rows[i0 + k]['date']) - dt.date.fromisoformat(rows[i0]['date'])).days}


def dat_session_rows(y, coin_px, perp_px, funding, adv_n=60):
    """Session rows from a Yahoo daily read ({'dates','close','volume'}) and Binance hourly closes keyed by open time:
    the coin and perp close of the hour ending at each session close (up to 6 hours earlier when missing), funding
    settled in (previous close, close], trailing dollar volume over adv_n sessions including the day."""
    import bisect
    funding = sorted(funding)
    fts = [t for t, _ in funding]
    frs = [r for _, r in funding]

    def hour_close(m, T):
        for back in range(1, 7):
            v = m.get(T - back * 3600000)
            if v is not None:
                return v
        return None
    rows, vols, prev = [], [], None
    for date, close, vol in zip(y['dates'], y['close'], y['volume']):
        vols.append((vol or 0) * close)
        T = session_close_ms(date)
        f = sum(frs[bisect.bisect_right(fts, prev):bisect.bisect_right(fts, T)]) if prev is not None else 0.0
        rows.append({'date': date, 'close_ms': T, 'price': close, 'coin_px': hour_close(coin_px, T),
                     'perp_px': hour_close(perp_px, T), 'funding': f,
                     'adv_usd': sum(vols[-adv_n:]) / len(vols[-adv_n:])})
        prev = T
    return rows


def dat_forward_registrable(cands, ledger, now_ms):
    """(new, late): candidates not yet in the ledger under the same rule and ticker whose entry close is still ahead,
    and those whose entry has passed (a row registered after its entry would carry the price it bets on)."""
    have = {(r.get('rule'), r.get('ticker')) for r in ledger}
    new, late = [], []
    for c in cands:
        if (c['rule'], c['ticker']) in have:
            continue
        (new if iso_to_ms(c['entry_utc']) > now_ms else late).append(c)
    return new, late


def iso_to_ms(s):
    return int(dt.datetime.fromisoformat(s).timestamp() * 1000)


def read_jsonl(path):
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def append_jsonl(path, rows):
    if not rows:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a') as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, default=str) + '\n')


class DatFetch:
    """The forward test's network reads (Yahoo daily, Binance hourly closes and funding, Binance perp state), each
    saved raw under `raw_dir`. Read-only public endpoints; Yahoo with UA 'Mozilla/5.0'."""

    def __init__(self, raw_dir):
        self.raw = Path(raw_dir)

    def _save(self, name, obj):
        write_gz(self.raw / name, obj)

    def yahoo_daily(self, sym, t0_s, t1_s):
        d = http_json(YAHOO + urllib.parse.quote(sym), {'period1': int(t0_s), 'period2': int(t1_s), 'interval': '1d',
                                                        'events': 'div,split'}, pause=0.6)
        self._save('yahoo_%s.json.gz' % sym, d)
        r = ((d.get('chart') or {}).get('result') or [None])[0] if isinstance(d, dict) else None
        if not r or not r.get('timestamp'):
            return None
        q = r['indicators']['quote'][0]
        out = {'dates': [], 'close': [], 'volume': []}
        for i, t in enumerate(r['timestamp']):
            if q['close'][i] is None:
                continue
            out['dates'].append(dt.datetime.fromtimestamp(t, UTC).strftime('%Y-%m-%d'))
            out['close'].append(float(q['close'][i]))
            out['volume'].append(q['volume'][i] or 0)
        ev = r.get('events') or {}
        out['splits'] = sorted((ymd(x['date'] * 1000), x['numerator'] / x['denominator'])
                               for x in (ev.get('splits') or {}).values())
        return out

    def hourly(self, coin, start_ms, end_ms, kind='study'):
        """{open ms: close}: 'study' = spot where Binance lists it, else the perp (collect_binance's choice);
        'perp' = the USD-M perp."""
        spot, perp = COIN_SYMBOLS[coin]
        if kind == 'study' and spot:
            url, sym, src = BN_SPOT, spot, 'spot:' + spot
        else:
            url, sym, src = BN_PERP, perp, 'perp:' + perp
        rows = _klines(url, sym, '1h', start_ms, end_ms, log=lambda *a: None, limit=1000)
        mult = PERP_MULT.get(coin, 1.0) if src.startswith('perp') else 1.0
        self._save('binance_%s_%s_1h.json.gz' % (coin, 'study' if kind == 'study' else 'perp'),
                   {'source': src, 'rows': rows})
        return {r[0]: r[1] / mult for r in rows}, src

    def funding(self, coin, start_ms, end_ms):
        perp = COIN_SYMBOLS[coin][1]
        rows, t = [], start_ms
        while t < end_ms:
            d = http_json(BN_FUND, {'symbol': perp, 'startTime': t, 'endTime': end_ms, 'limit': 1000}, pause=0.25)
            if not isinstance(d, list) or not d:
                break
            rows.extend([[int(x['fundingTime']), float(x['fundingRate'])] for x in d])
            nt = int(d[-1]['fundingTime']) + 1
            if nt <= t or len(d) < 1000:
                break
            t = nt
        self._save('binance_%s_funding.json.gz' % coin, {'symbol': perp, 'rows': rows})
        return [(a, b) for a, b in rows]

    def perp_state(self, symbol):
        base = 'https://fapi.binance.com'
        out = {'symbol': symbol, 'at': dt.datetime.now(UTC).isoformat(timespec='seconds')}
        for key, path, params in (('premium_index', '/fapi/v1/premiumIndex', {'symbol': symbol}),
                                  ('ticker_24h', '/fapi/v1/ticker/24hr', {'symbol': symbol}),
                                  ('open_interest', '/fapi/v1/openInterest', {'symbol': symbol}),
                                  ('depth', '/fapi/v1/depth', {'symbol': symbol, 'limit': 100}),
                                  ('funding_last', '/fapi/v1/fundingRate', {'symbol': symbol, 'limit': 30})):
            try:
                out[key] = http_json(base + path, params, pause=0.25)
            except RuntimeError as e:
                out[key] = {'_error': str(e)[:200]}
        self._save('binance_perp_state_%s.json.gz' % symbol, out)
        return out


def perp_state_summary(st):
    """Mark, index, last funding, 24h quote volume, open interest and depth within 1% from a perp_state read."""
    pi, tk, oi, dp = (st.get(k) or {} for k in ('premium_index', 'ticker_24h', 'open_interest', 'depth'))
    mark = fnum(pi.get('markPrice'))
    out = {'symbol': st.get('symbol'), 'at': st.get('at'), 'mark': mark, 'index': fnum(pi.get('indexPrice')),
           'last_funding_rate': fnum(pi.get('lastFundingRate')), 'quote_volume_24h': fnum(tk.get('quoteVolume')),
           'open_interest_units': fnum(oi.get('openInterest'))}
    if mark and isinstance(dp, dict) and dp.get('bids'):
        out['bid_usd_within_1pct'] = sum(float(p) * float(q) for p, q in dp['bids'] if float(p) >= mark * 0.99)
        out['ask_usd_within_1pct'] = sum(float(p) * float(q) for p, q in dp.get('asks', []) if float(p) <= mark * 1.01)
    fl = st.get('funding_last')
    if isinstance(fl, list) and fl:
        out['funding_last_n'] = len(fl)
        out['funding_last_sum'] = sum(float(x['fundingRate']) for x in fl)
        out['funding_last_from'] = ymd(int(fl[0]['fundingTime']))
    return out


def dat_forward_inputs(live_row, override):
    """Frozen look-through inputs from the study's live row (analysis.json dats.live) and its curated override."""
    return {'coins': live_row['coins'], 'cash_usd': live_row['cash_usd'], 'debt_usd': live_row['debt_usd'],
            'pref_usd': live_row['pref_usd'], 'shares': live_row['shares'],
            'committed_to_illiquid_usd': (override or {}).get('committed_to_illiquid_usd', 0.0)}


def dat_forward_register(ledger_path, now_ms, fetch, analysis, curated, entry_date=None, names=None, log=print):
    """Append one registration row per name (rule, ticker) not yet in the ledger, entry at the first close after
    `now_ms` (or the close of `entry_date`, refused when it has passed). Returns (new rows, late candidates)."""
    ledger = read_jsonl(ledger_path)
    if entry_date:
        if not is_session(entry_date):
            raise SystemExit('%s is not an NYSE session' % entry_date)
        e_date, e_ms = entry_date, session_close_ms(entry_date)
    else:
        e_date, e_ms = next_close_after(now_ms)
    names = names or list(DAT_FORWARD_NAMES)
    live = {r['ticker']: r for r in analysis['dats']['live']}
    overrides = curated.get('dat_live_overrides') or {}
    exp = sessions_after(e_date, max(DAT_FORWARD_HORIZONS))
    cands = [{'rule': DAT_FORWARD_RULE['id'], 'ticker': tk, 'entry_date': e_date, 'entry_utc': utc_iso_ms(e_ms)}
             for tk in names]
    new, late = dat_forward_registrable(cands, ledger, now_ms)
    for c in late:
        log('too late  %-5s entry %s has passed' % (c['ticker'], c['entry_utc']))
    stamp = utc_iso_ms(now_ms)
    rows = []
    coin_cache = {}
    for c in new:
        tk = c['ticker']
        spec = DAT_FORWARD_NAMES[tk]
        r = live[tk]
        ov = overrides.get(tk) or {}
        coin = r['coin']
        inputs = dat_forward_inputs(r, ov)
        y = fetch.yahoo_daily(tk, now_ms / 1000 - 140 * 86400, now_ms / 1000)
        ref_i = max(i for i, d in enumerate(y['dates']) if session_close_ms(d) + SETTLE_MS <= now_ms)
        ref_date, ref_close = y['dates'][ref_i], y['close'][ref_i]
        T = session_close_ms(ref_date)
        if coin not in coin_cache:
            cs, src = fetch.hourly(coin, T - 12 * 3600000, now_ms, 'study')
            cp, psrc = fetch.hourly(coin, T - 12 * 3600000, now_ms, 'perp')
            st = perp_state_summary(fetch.perp_state(COIN_SYMBOLS[coin][1]))
            coin_cache[coin] = (cs, src, cp, psrc, st)
        cs, src, cp, psrc, st = coin_cache[coin]
        srows = dat_session_rows({'dates': y['dates'][:ref_i + 1], 'close': y['close'][:ref_i + 1],
                                  'volume': y['volume'][:ref_i + 1]}, cs, cp, [])
        ref = srows[-1]
        C = ref['coin_px']
        h = frozen_beta(inputs, C, DAT_FORWARD_PARAMS['hedge_cap'])
        stock_perp = None
        tf = (next((u for u in load_universe()['dats'] if u['ticker'] == tk), {}) or {}).get('binance_tradfi')
        if tf:
            stock_perp = perp_state_summary(fetch.perp_state(tf))
        cv_ps = inputs['coins'] * C / inputs['shares']
        row = {'rule': DAT_FORWARD_RULE['id'], 'rule_frozen': DAT_FORWARD_RULE, 'params': DAT_FORWARD_PARAMS,
               'ticker': tk, 'role': spec['role'], 'catalyst': spec.get('catalyst'), 'coin': coin,
               'hedge_perp': 'Binance USD-M %s' % COIN_SYMBOLS[coin][1], 'coin_price_source': src,
               'registered_at': stamp, 'entry_date': e_date, 'entry_utc': c['entry_utc'],
               'score_dates_expected': {str(k): exp[k - 1] for k in DAT_FORWARD_HORIZONS},
               'horizon_unit': 'NYSE sessions after the entry close',
               'reference': {'date': ref_date, 'close': ref_close, 'close_utc': utc_iso_ms(T), 'coin_px': C,
                             'perp_px': ref['perp_px'], 'adv60_usd': ref['adv_usd'],
                             'note': 'the latest settled close at registration; the trade enters at entry_date'},
               'nav_inputs': inputs,
               'nav_sources': {'as_of': r.get('date'), 'capital': r.get('capital_source'),
                               'holdings': r.get('holdings_source'), 'documents': ov.get('sources'),
                               'note': ov.get('note'), 'fv_check_10q': r.get('fv_check'), 'flags': r.get('flags'),
                               'study_analysis': 'research/2026-10-10/nav_wrappers/analysis.json',
                               'study_generated': analysis.get('generated')},
               'at_reference': {'true_mnav': frozen_true_mnav(inputs, ref_close, C),
                                'true_mnav_illiquid_at_zero': frozen_true_mnav(inputs, ref_close, C,
                                                                               illiquid_at_zero=True)
                                if inputs['committed_to_illiquid_usd'] else None,
                                'naive_mnav': ref_close * inputs['shares'] / (inputs['coins'] * C),
                                'nav_per_share': ref_close / frozen_true_mnav(inputs, ref_close, C)
                                if frozen_true_mnav(inputs, ref_close, C) else None,
                                'coin_value_per_share': cv_ps, 'hedge_beta': h,
                                'hedge_coin_units_per_share': (h * ref_close / C) if h else None,
                                'hedge_asset_alternative': cv_ps / ref_close,
                                'hedge_beta_illiquid_at_zero': frozen_beta(
                                    dict(inputs, cash_usd=inputs['cash_usd'] - inputs['committed_to_illiquid_usd']),
                                    C, DAT_FORWARD_PARAMS['hedge_cap']) if inputs['committed_to_illiquid_usd'] else None,
                                'stock_cost_per_side': stock_side_cost(ref['adv_usd'],
                                                                       DAT_FORWARD_PARAMS['stock_cost_tiers'])},
               'study_row': {k: r.get(k) for k in ('date', 'price_usd', 'coin_px', 'mnav_true', 'mnav_naive',
                                                   'mnav_ev', 'mnav_true_illiquid_at_zero', 'mnav_true_10q_holdings',
                                                   'nav_per_share', 'adv60_usd', 'capacity_usd')},
               'live_at_registration': {'coin_perp': st, 'stock_perp': stock_perp},
               'raw': str(fetch.raw.relative_to(ROOT)) if str(fetch.raw).startswith(str(ROOT)) else str(fetch.raw)}
        rows.append(row)
        log('registered %-5s %-9s entry %s close  ref %s %.4g  coin %s %.6g  true mNAV %.3f  beta %.3f  +20 %s  +60 %s'
            % (tk, spec['role'], e_date, ref_date, ref_close, coin, C, row['at_reference']['true_mnav'] or 0, h or 0,
               row['score_dates_expected']['20'], row['score_dates_expected']['60']))
    append_jsonl(ledger_path, rows)
    log('%d registered, %d too late, %d in the ledger' % (len(rows), len(late), len(ledger) + len(rows)))
    return rows, late


def utc_iso_ms(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, UTC).isoformat(timespec='seconds')


def dat_forward_score_row(row, srows, now_ms, share_factor=1.0):
    """One registered name: entry state and each horizon's trade (pending until its close has settled)."""
    P = row['params']
    inputs = row['nav_inputs']
    res = {'ticker': row['ticker'], 'role': row['role'], 'entry_date': row['entry_date'], 'horizons': {},
           'pending': []}
    i0 = next((i for i, r in enumerate(srows) if r['date'] == row['entry_date']), None)
    if i0 is None or srows[i0]['close_ms'] + SETTLE_MS > now_ms:
        res['pending'].append('entry: the %s close is not yet in the data' % row['entry_date'])
        return res
    e = srows[i0]
    if e['coin_px'] is None:
        res['pending'].append('entry: coin price missing at the entry close')
        return res
    ill = bool(inputs.get('committed_to_illiquid_usd'))
    res['entry'] = {'price': e['price'], 'coin_px': e['coin_px'], 'perp_px': e['perp_px'], 'adv_usd': e['adv_usd'],
                    'h0': frozen_beta(inputs, e['coin_px'], P['hedge_cap']),
                    'true_mnav': frozen_true_mnav(inputs, e['price'], e['coin_px'], share_factor),
                    'true_mnav_illiquid_at_zero': frozen_true_mnav(inputs, e['price'], e['coin_px'], share_factor,
                                                                   True) if ill else None}
    for k in P['horizons']:
        j = i0 + k
        if j >= len(srows) or srows[j]['close_ms'] + SETTLE_MS > now_ms:
            have = len([r for r in srows[i0 + 1:] if r['close_ms'] + SETTLE_MS <= now_ms])
            res['pending'].append('+%d: %d of %d sessions' % (k, min(have, k), k))
            continue
        tr = dat_forward_trade(srows, i0, k, inputs, P)
        if tr is None:
            res['pending'].append('+%d: a price is missing' % k)
            continue
        tp = dat_forward_trade(srows, i0, k, inputs, P, leg='perp_px')
        x = srows[j]
        t1 = frozen_true_mnav(inputs, x['price'], x['coin_px'], share_factor)
        h = dict(tr, date=x['date'], expected=row['score_dates_expected'].get(str(k)),
                 date_matches_expected=x['date'] == row['score_dates_expected'].get(str(k)),
                 excess_perp_leg=tp['excess'] if tp else None, true_mnav=t1,
                 true_change=(t1 - res['entry']['true_mnav']) if (t1 is not None and res['entry']['true_mnav']) else None)
        if ill:
            t1z = frozen_true_mnav(inputs, x['price'], x['coin_px'], share_factor, True)
            h['true_mnav_illiquid_at_zero'] = t1z
            e0z = res['entry']['true_mnav_illiquid_at_zero']
            h['true_change_illiquid_at_zero'] = (t1z - e0z) if (t1z is not None and e0z) else None
        res['horizons'][str(k)] = h
    return res


def dat_forward_summary(scored, horizons=DAT_FORWARD_HORIZONS):
    """Candidates against the placebo basket and MSTR at each horizon, and the verdict the frozen criteria imply."""
    by_role = {}
    for s in scored:
        by_role.setdefault(s['role'], []).append(s)
    out = {'horizons': {}}
    for k in horizons:
        kk = str(k)
        pl = [s['horizons'][kk]['excess'] for s in by_role.get('placebo', []) if kk in s['horizons']]
        n_pl = len(by_role.get('placebo', []))
        basket = sum(pl) / len(pl) if pl else None
        bm = [s['horizons'][kk]['excess'] for s in by_role.get('benchmark', []) if kk in s['horizons']]
        cands = {}
        for s in by_role.get('candidate', []):
            h = s['horizons'].get(kk)
            if not h:
                continue
            cands[s['ticker']] = {'excess': h['excess'], 'excess_perp_leg': h.get('excess_perp_leg'),
                                  'over_placebo': (h['excess'] - basket)
                                  if (basket is not None and len(pl) >= min(n_pl, DAT_PLACEBO_MIN)) else None,
                                  'over_benchmark': (h['excess'] - bm[0]) if bm else None,
                                  'true_change': h.get('true_change'),
                                  'true_change_illiquid_at_zero': h.get('true_change_illiquid_at_zero')}
        out['horizons'][kk] = {'placebo_basket_excess': basket, 'placebo_scored': len(pl), 'placebo_names': n_pl,
                               'benchmark_excess': bm[0] if bm else None, 'candidates': cands}
    n = sum(len(v['candidates']) for v in out['horizons'].values())
    out['candidate_horizons_scored'] = n
    last = out['horizons'].get(str(max(horizons)), {}).get('candidates', {})
    n_cand = len(by_role.get('candidate', []))
    if n < DAT_FORWARD_MIN or len(last) < n_cand or any(v['over_placebo'] is None for v in last.values()):
        out['verdict'] = 'accumulating (%d of %d candidate horizons scored)' % (n, DAT_FORWARD_MIN)
    elif sum(v['over_placebo'] for v in last.values()) / len(last) <= 0:
        out['verdict'] = 'kill: mean +%d-session excess over the placebo basket is not positive' % max(horizons)
    elif all(v['excess'] > 0 and v['over_placebo'] > 0 and (v['true_change'] or 0) > 0 for v in last.values()):
        out['verdict'] = 'promote: both candidates beat the savings rate and the placebo, and both discounts narrowed'
    else:
        out['verdict'] = 'hold: positive on average over the placebo, not on every criterion'
    return out


def cmd_forward(args):
    ledger_path = Path(args.ledger)
    now_ms = int(time.time() * 1000)
    stamp = dt.datetime.fromtimestamp(now_ms / 1000, UTC).strftime('%Y%m%dT%H%MZ')
    if args.action == 'register':
        fetch = DatFetch(WATCH_DIR / 'dat' / ('register_%s' % stamp))
        analysis = json.loads((OUT / 'analysis.json').read_text())
        names = [x for x in args.names.split(',') if x] or None
        dat_forward_register(ledger_path, now_ms, fetch, analysis, load_curated(), args.entry_date, names)
        return 0
    ledger = [r for r in read_jsonl(ledger_path) if r.get('rule') == DAT_FORWARD_RULE['id']]
    if not ledger:
        print('nothing registered in %s' % ledger_path)
        return 0
    first_entry = min(iso_to_ms(r['entry_utc']) for r in ledger)
    prev_p = ledger_path.with_suffix('.json')
    if not getattr(args, 'force', False) and prev_p.exists() and now_ms >= first_entry + SETTLE_MS:
        # the network is read only when a milestone (entry, +20, +60 close) has settled and is not yet in the score
        prev = json.loads(prev_p.read_text())
        done = {(n['ticker'], 'entry') for n in prev.get('names', []) if n.get('entry')} | \
            {(n['ticker'], k) for n in prev.get('names', []) for k in (n.get('horizons') or {})}
        due = [(r['ticker'], 'entry') for r in ledger if now_ms >= iso_to_ms(r['entry_utc']) + SETTLE_MS] + \
            [(r['ticker'], k) for r in ledger for k, d in r['score_dates_expected'].items()
             if now_ms >= session_close_ms(d) + SETTLE_MS]
        if all(x in done for x in due):
            print('no new milestone since %s: %s (next: %s)' % (
                prev.get('generated'), prev['summary']['verdict'],
                min([d for r in ledger for d in r['score_dates_expected'].values()
                     if session_close_ms(d) + SETTLE_MS > now_ms], default='none')))
            return 0
    if now_ms < first_entry + SETTLE_MS:
        print('nothing to score yet: %d registered, entry %s' % (len(ledger), min(r['entry_utc'] for r in ledger)))
        scored = [{'ticker': r['ticker'], 'role': r['role'], 'entry_date': r['entry_date'], 'horizons': {},
                   'pending': ['entry: the %s close has not happened' % r['entry_date']]} for r in ledger]
    else:
        fetch = DatFetch(WATCH_DIR / 'dat' / ('score_%s' % stamp))
        t0 = first_entry - 120 * FWD_DAY_MS
        coins = {}
        scored = []
        for r in ledger:
            y = fetch.yahoo_daily(r['ticker'], t0 / 1000, now_ms / 1000)
            if r['coin'] not in coins:
                cs, _ = fetch.hourly(r['coin'], first_entry - 2 * FWD_DAY_MS, now_ms, 'study')
                cp, _ = fetch.hourly(r['coin'], first_entry - 2 * FWD_DAY_MS, now_ms, 'perp')
                fu = fetch.funding(r['coin'], first_entry - 2 * FWD_DAY_MS, now_ms)
                coins[r['coin']] = (cs, cp, fu)
            cs, cp, fu = coins[r['coin']]
            sf = 1.0
            for d, ratio in (y or {}).get('splits', []):
                if d > r['registered_at'][:10]:
                    sf *= ratio
            srows = dat_session_rows(y, cs, cp, fu) if y else []
            s = dat_forward_score_row(r, srows, now_ms, sf)
            if sf != 1.0:
                s['share_factor_after_splits'] = sf
            scored.append(s)
    S = dat_forward_summary(scored)
    res = {'generated': utc_iso_ms(now_ms), 'rule': DAT_FORWARD_RULE, 'ledger': str(ledger_path),
           'registered': len(ledger), 'summary': S, 'names': scored}
    write_json(ledger_path.with_suffix('.json'), _clean(res))
    for s in scored:
        hs = ' '.join('+%s %s' % (k, _p(v['excess'], 2)) for k, v in sorted(s['horizons'].items(), key=lambda x: int(x[0])))
        print('%-5s %-9s %s  %s' % (s['ticker'], s['role'], hs or '—', '; '.join(s['pending'])))
    print('verdict: %s' % S['verdict'])
    return 0


def cmd_collect(args):
    parts = [x.strip() for x in args.parts.split(',') if x.strip()]
    man_p = RAW / 'collect_manifest.json'
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    for part in parts:
        t0 = time.time()
        if part == 'yahoo':
            r = collect_yahoo(args.force)
        elif part == 'yahoo1h':
            r = collect_yahoo_intraday([x for x in args.symbols.split(',') if x], args.force)
        elif part == 'sec':
            r = collect_sec(args.force)
        elif part == 'binance':
            r = collect_binance([x for x in args.coins.split(',') if x] or None, args.force)
        elif part == 'coingecko':
            r = collect_coingecko(args.force)
        elif part == 'strategytracker':
            r = collect_strategytracker(args.force)
        elif part == 'cgprices':
            r = collect_cg_prices(force=args.force)
        elif part == 'strategy':
            r = collect_strategy()
        else:
            raise SystemExit('unknown part %s' % part)
        man[part] = {'at': dt.datetime.now(UTC).isoformat(timespec='seconds'), 'seconds': round(time.time() - t0, 1),
                     'result': r}
        write_json(man_p, man)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--parts', default='yahoo,sec,binance,coingecko,strategytracker,strategy')
    c.add_argument('--coins', default='')
    c.add_argument('--symbols', default='')
    c.add_argument('--force', action='store_true')
    c.set_defaults(fn=cmd_collect)
    a = sub.add_parser('analyze')
    a.set_defaults(fn=lambda args: cmd_analyze(args))
    r = sub.add_parser('render')
    r.set_defaults(fn=lambda args: cmd_render(args))
    f = sub.add_parser('forward', help='register EMPD/BNC (and their placebo basket, MSTR) before entry; score at '
                                       '+20/+60 sessions')
    f.add_argument('action', choices=['register', 'score'])
    f.add_argument('--ledger', default=str(DAT_FORWARD_LEDGER))
    f.add_argument('--entry-date', default=None, help='an NYSE session whose close is the entry (default: the first '
                                                      'close after now); refused when it has passed')
    f.add_argument('--names', default='', help='comma-separated subset of %s' % ','.join(DAT_FORWARD_NAMES))
    f.add_argument('--force', action='store_true', help='score: read the network even when no milestone is new')
    f.set_defaults(fn=cmd_forward)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == '__main__':
    main()
