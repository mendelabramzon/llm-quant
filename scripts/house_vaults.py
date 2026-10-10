#!/usr/bin/env python3
"""Being the house: do perp-venue liquidity vaults, with their market exposure hedged, beat the savings rate?

On a perp venue the liquidity vault is the traders' counterparty. It earns fees, spreads, borrow fees, liquidation
penalties and the traders' net losses, and it pays their net wins. Its takers come with non-price motives (retail
leverage demand, points farming that churns volume), which is the filter this repo's surviving strategies passed. The
question here: does any venue's vault, hedged, earn above the savings rate out of sample, with tails that can be named
and priced, and how much can a new depositor add before diluting the return away?

Universe (in the order the brief asked):
  1. HLP (Hyperliquid)                — vaultDetails portfolio grid (allTime ~7-14 days, month ~10h), 7 child vaults;
  2. dYdX MegaVault                   — indexer historicalPnl (the indexer serves 90 days);
  3. JLP (Jupiter perps, Solana)      — DefiLlama daily price, CoinGecko 365 days as a check, jlp-info, fees;
  4. GMX v2 GM pools and GLV vaults   — GMX synthetics squid: daily GM/GLV price snapshots, fees, pool value;
  5. Gains gUSDC (Arbitrum)           — shareToAssetsPrice() at daily blocks through an archive node;
  6. Lighter LLP                      — account pool_info daily returns and the account's daily P&L/flows ledger;
  7. others (Ostium, Avantis, Aster, Drift, Paradex, edgeX, Extended) — one probe each, gaps recorded.
Hedge legs: Binance USDT-margined perps (1h klines and funding), the deepest venue for BTC/ETH/SOL.

Subcommands:
  python3 scripts/house_vaults.py collect [--parts hlp,binance,jlp,llama,gmx,gains,dydx,lighter,probes] [--refresh]
  python3 scripts/house_vaults.py analyze
  python3 scripts/house_vaults.py render

Raw data go under research/2026-10-10/house_vaults/raw/<source>/ (large files gzipped). Collect is resumable: a file
that exists is not fetched again unless --refresh (dated snapshots are keyed by UTC day). Pacing is per host and
deliberately slow where other workers share the IP: Hyperliquid info >= 1.5 s a call, DefiLlama >= 2 s, CoinGecko 6 s.
Standard library only; the Gains part reuses scripts/live_rpc.py (local Infura keys, never written anywhere).
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import backtest as B  # noqa: E402

OUT = ROOT / 'research' / '2026-10-10' / 'house_vaults'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) llm-quant research'

# ----------------------------------------------------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------------------------------------------------
HLP = '0xdfc24b077bc1425ad1dea75bcb6f8158e10df303'
HL_INFO = 'https://api.hyperliquid.xyz/info'
JLP_MINT = '27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4'   # verified: getTokenSupply == jlp-info jlpTotalSupply
GMX_SQUID = 'https://gmx.squids.live/gmx-synthetics-arbitrum:prod/api/graphql'
GMX_API = 'https://arbitrum-api.gmxinfra.io'
DYDX = 'https://indexer.dydx.trade/v4'
BINANCE = 'https://fapi.binance.com'
GAINS = {  # gToken vaults (ERC-4626 with epoch-gated withdrawals); Arbitrum gUSDC is the largest
    'gUSDC_arbitrum': {'chain': 'arbitrum', 'address': '0xd3443ee1e91aF28e5FB858Fbd0D72A63bA8046E0', 'decimals': 6,
                       'start': '2023-09-01'},
}
INFURA_ARB = 'https://arbitrum-mainnet.infura.io/v3/'

# The GMX universe: the three launch GM pools, the two single-token pools and the two GLV baskets on Arbitrum.
GMX_TOKENS = {
    'GM_ETH-USDC': {'address': '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336', 'type': 'gm', 'asset': 'ETH', 'kind': 'two-token'},
    'GM_BTC-USDC': {'address': '0x47c031236e19d024b42f8AE6780E44A573170703', 'type': 'gm', 'asset': 'BTC', 'kind': 'two-token'},
    'GM_SOL-USDC': {'address': '0x09400D9DB990D5ed3f35D7be61DfAEB900Af03C9', 'type': 'gm', 'asset': 'SOL', 'kind': 'two-token'},
    'GM_ETH-ETH': {'address': '0x450bb6774Dd8a756274E0ab4107953259d2ac541', 'type': 'gm', 'asset': 'ETH', 'kind': 'single-token'},
    'GM_BTC-BTC': {'address': '0x7C11F78Ce78768518D743E81Fdfa2F860C6b9A77', 'type': 'gm', 'asset': 'BTC', 'kind': 'single-token'},
    'GLV_ETH-USDC': {'address': '0x528A5bac7E746C9A509A1f4F6dF58A03d44279F9', 'type': 'glv', 'asset': 'ETH', 'kind': 'basket'},
    'GLV_BTC-USDC': {'address': '0xdF03EEd325b82bC1d4Db8b49c30ecc9E05104b96', 'type': 'glv', 'asset': 'BTC', 'kind': 'basket'},
}
HEDGE_SYMBOLS = {'BTC': 'BTCUSDT', 'ETH': 'ETHUSDT', 'SOL': 'SOLUSDT', 'HYPE': 'HYPEUSDT'}
BINANCE_START = {'BTCUSDT': '2023-05-01', 'ETHUSDT': '2023-05-01', 'SOLUSDT': '2023-05-01', 'HYPEUSDT': '2025-05-30'}

# Savings rate actually paid (Maker DSR, then the Sky savings rate), by calendar year, as given in the brief; SSR today.
SAVINGS_BY_YEAR = {2019: 0.0, 2020: 0.0, 2021: 0.0, 2022: 0.001, 2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}
SSR_NOW = 0.038

# Cost model (one-way, fraction of notional). Binance VIP0 taker 5bp incl. half-spread, as in term_carry.
HEDGE_FEE = 0.0005
MARGIN = 1.0 / 3.0          # cash margin per unit of short notional (3x), held idle: capital = 1 + MARGIN * |hedge|
REBAL_BAND = 0.10           # rebalance a hedge leg when it drifts more than 10% from its target notional
ENTRY_EXIT = {              # vault entry + exit cost, fraction of the deposit, one round trip (see manifest notes)
    'HLP': 0.0,             # no deposit/withdraw fee; 4-day lockup
    'JLP': 0.0020,          # mint ~0.10% + burn ~0.10% at target weights (dynamic, higher off target); swap spread
    'GM': 0.0012,           # GMX v2 deposit 0.05-0.07% + withdrawal 0.05-0.07%, price impact small at target ratio
    'GLV': 0.0012,
    'gToken': 0.0,          # no fee; withdrawals gated by epochs (priced separately as a liquidity constraint)
    'dYdX': 0.0,
}

HOST_INTERVAL = {
    'mainnet.zklighter.elliot.ai': 1.5,
    'api.hyperliquid.xyz': 1.5, 'yields.llama.fi': 2.0, 'api.llama.fi': 2.0, 'coins.llama.fi': 2.0,
    'api.coingecko.com': 6.0, 'fapi.binance.com': 0.25, 'gmx.squids.live': 0.4, 'arbitrum-api.gmxinfra.io': 0.5,
    'indexer.dydx.trade': 0.5, 'perps-api.jup.ag': 1.0,
}
STATS = {'requests': 0, 'errors': 0, 'throttled': 0, 'by_host': {}}
_NEXT_AT = {}


# ----------------------------------------------------------------------------------------------------------------------
# I/O helpers
# ----------------------------------------------------------------------------------------------------------------------
def utc(ts):
    """Seconds or milliseconds since epoch -> aware UTC datetime."""
    ts = float(ts)
    if ts > 1e11:
        ts /= 1000.0
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc)


def day_of(ts):
    return utc(ts).strftime('%Y-%m-%d')


def today():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d')


def day_ts(day):
    return int(dt.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp())


def save_json(path, obj, gz=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    gz = path.suffix == '.gz' if gz is None else gz
    tmp = path.with_name(path.name + '.tmp')
    if gz:
        with gzip.open(tmp, 'wt') as f:
            json.dump(obj, f, separators=(',', ':'))
    else:
        with open(tmp, 'w') as f:
            json.dump(obj, f, indent=1, sort_keys=False, default=str)
    os.replace(tmp, path)


def load_json(path):
    path = Path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rt') as f:
            return json.load(f)
    with open(path) as f:
        return json.load(f)


def http_json(url, body=None, headers=None, timeout=90, retries=5):
    """GET (or POST JSON when body is given) with per-host pacing, backoff on 429/5xx, gzip; returns parsed JSON."""
    host = urllib.parse.urlparse(url).netloc
    gap = HOST_INTERVAL.get(host, 0.5)
    last = None
    for attempt in range(retries + 1):
        wait = _NEXT_AT.get(host, 0.0) - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _NEXT_AT[host] = time.monotonic() + gap
        STATS['requests'] += 1
        STATS['by_host'][host] = STATS['by_host'].get(host, 0) + 1
        h = {'User-Agent': UA, 'Accept-Encoding': 'gzip', 'Accept': 'application/json'}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h['Content-Type'] = 'application/json'
        h.update(headers or {})
        req = urllib.request.Request(url, data=data, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    raw = gzip.decompress(raw)
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            STATS['errors'] += 1
            last = 'HTTP %d' % e.code
            if e.code == 429:
                STATS['throttled'] += 1
                _NEXT_AT[host] = time.monotonic() + max(10.0, gap * 8) * (attempt + 1)
                continue
            if e.code in (500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
            STATS['errors'] += 1
            last = str(e)[:160]
            time.sleep(3 * (attempt + 1))
    raise RuntimeError('%s failed: %s' % (url[:120], last))


# ----------------------------------------------------------------------------------------------------------------------
# Parsers (pure functions; tested in test_house_vaults.py)
# ----------------------------------------------------------------------------------------------------------------------
def parse_hl_portfolio(details, window='allTime'):
    """vaultDetails -> list of (t_ms, account_value, cumulative_pnl) for one window, sorted, de-duplicated."""
    port = dict(details['portfolio'])
    w = port[window]
    av = {int(t): float(v) for t, v in w['accountValueHistory']}
    pn = {int(t): float(v) for t, v in w['pnlHistory']}
    ts = sorted(set(av) & set(pn))
    return [(t, av[t], pn[t]) for t in ts]


def parse_squid_prices(rows, scale=1e30):
    """GMX squid `prices` snapshots -> {day: mid price in USD}. GM and GLV prices carry 30 decimals per 1e18 token."""
    out = {}
    for r in rows:
        ts = int(r.get('snapshotTimestamp') or r['timestamp'])
        p = (int(r['minPrice']) + int(r['maxPrice'])) / 2.0 / scale
        out[day_of(ts)] = p
    return out


def parse_llama_chart(objs):
    """DefiLlama coins/chart responses -> {day: price} (the last observation of each UTC day wins)."""
    out = {}
    for d in objs:
        for v in (d.get('coins') or {}).values():
            for x in v.get('prices', []):
                out[(x['timestamp'], day_of(x['timestamp']))] = float(x['price'])
    res = {}
    for (ts, day), p in sorted(out.items()):
        res[day] = p
    return res


def parse_dydx_pnl(rows):
    """dYdX indexer historicalPnl rows -> sorted list of (t_ms, equity, totalPnl, netTransfers)."""
    out = []
    for r in rows:
        t = int(utc(dt.datetime.fromisoformat(r['blockTime'].replace('Z', '+00:00')).timestamp()).timestamp() * 1000)
        out.append((t, float(r['equity']), float(r['totalPnl']), float(r.get('netTransfers') or 0.0)))
    out.sort()
    return out


def hex_uint(x):
    return int(x, 16) if isinstance(x, str) and x.startswith('0x') and len(x) > 2 else None


def hex_int256(x):
    v = hex_uint(x)
    if v is None:
        return None
    return v - (1 << 256) if v >= (1 << 255) else v


# ----------------------------------------------------------------------------------------------------------------------
# collect
# ----------------------------------------------------------------------------------------------------------------------
def collect_hlp(out, refresh=False):
    """Parent HLP + every child vault, one dated snapshot per UTC day; plus the parent's last-7-day ledger flows
    (user addresses stripped) for the independent flow check."""
    d = out / 'raw' / 'hlp' / today()
    d.mkdir(parents=True, exist_ok=True)
    pf = d / ('vault_%s.json.gz' % HLP)
    if refresh or not pf.exists():
        parent = http_json(HL_INFO, {'type': 'vaultDetails', 'vaultAddress': HLP})
        parent['followers'] = len(parent.get('followers') or [])   # strip depositor addresses, keep the count
        save_json(pf, parent)
    parent = load_json(pf)
    kids = (parent.get('relationship') or {}).get('data', {}).get('childAddresses', [])
    for k in kids:
        f = d / ('vault_%s.json.gz' % k)
        if refresh or not f.exists():
            c = http_json(HL_INFO, {'type': 'vaultDetails', 'vaultAddress': k})
            c['followers'] = len(c.get('followers') or [])
            save_json(f, c)
    lf = d / 'ledger_7d.json.gz'
    if refresh or not lf.exists():
        week = dict(parent['portfolio'])['week']['accountValueHistory']
        start, end = int(week[0][0]), int(week[-1][0])
        rows, cur = [], start
        while True:
            page = http_json(HL_INFO, {'type': 'userNonFundingLedgerUpdates', 'user': HLP, 'startTime': cur, 'endTime': end})
            if not page:
                break
            for x in page:
                dl = x.get('delta', {})
                rows.append({'time': x['time'], 'type': dl.get('type'), 'vault': dl.get('vault'),
                             'usdc': dl.get('usdc'), 'requestedUsd': dl.get('requestedUsd'),
                             'netWithdrawnUsd': dl.get('netWithdrawnUsd'), 'commission': dl.get('commission'),
                             'closingCost': dl.get('closingCost'), 'hash': x.get('hash')})
            if len(page) < 2000:
                break
            cur = max(int(x['time']) for x in page) + 1
        seen, uniq = set(), []
        for r in rows:
            key = (r['hash'], r['time'], r['type'], r['vault'], r['usdc'], r['requestedUsd'])
            if key not in seen:
                seen.add(key)
                uniq.append(r)
        save_json(lf, {'start_ms': start, 'end_ms': end, 'rows': uniq})
    return {'snapshot_dir': str(d.relative_to(ROOT)), 'children': len(kids)}


def _binance_klines(sym, start_ms, end_ms):
    rows, cur = [], start_ms
    while cur < end_ms:
        q = urllib.parse.urlencode({'symbol': sym, 'interval': '1h', 'startTime': cur, 'limit': 1500})
        page = http_json('%s/fapi/v1/klines?%s' % (BINANCE, q))
        if not page:
            break
        rows.extend([[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[7])] for k in page])
        nxt = int(page[-1][0]) + 3600 * 1000
        if nxt <= cur:
            break
        cur = nxt
        if len(page) < 1500:
            break
    return rows


def _binance_funding(sym, start_ms, end_ms):
    rows, cur = [], start_ms
    while cur < end_ms:
        q = urllib.parse.urlencode({'symbol': sym, 'startTime': cur, 'limit': 1000})
        page = http_json('%s/fapi/v1/fundingRate?%s' % (BINANCE, q))
        if not page:
            break
        rows.extend([{'t': int(x['fundingTime']), 'rate': float(x['fundingRate'])} for x in page])
        cur = int(page[-1]['fundingTime']) + 1
        if len(page) < 1000:
            break
    return rows


def collect_binance(out, refresh=False):
    """1h perp klines (quote volume kept) and funding history for the hedge legs; resumable from the last row."""
    d = out / 'raw' / 'binance'
    end = int(time.time() * 1000)
    res = {}
    for sym, start in BINANCE_START.items():
        kf, ff = d / ('klines1h_%s.json.gz' % sym), d / ('funding_%s.json.gz' % sym)
        k = [] if (refresh or not kf.exists()) else load_json(kf)
        s = (k[-1][0] + 3600 * 1000) if k else day_ts(start) * 1000
        k += _binance_klines(sym, s, end - 3600 * 1000)
        k = sorted({r[0]: r for r in k}.values())
        save_json(kf, k)
        f = [] if (refresh or not ff.exists()) else load_json(ff)
        s = (f[-1]['t'] + 1) if f else day_ts(start) * 1000
        f += _binance_funding(sym, s, end)
        f = sorted({r['t']: r for r in f}.values(), key=lambda r: r['t'])
        save_json(ff, f)
        res[sym] = {'klines_1h': len(k), 'funding': len(f), 'first': day_of(k[0][0]) if k else None,
                    'last': day_of(k[-1][0]) if k else None}
    return res


def collect_jlp(out, refresh=False):
    d = out / 'raw' / 'jlp'
    d.mkdir(parents=True, exist_ok=True)
    starts = [1700000000, 1743200000, 1786400000]          # three 500-day DefiLlama windows from 2023-11-14
    for s in starts:
        f = d / ('llama_chart_%d.json' % s)
        if refresh or not f.exists() or s == starts[-1]:
            save_json(f, http_json('https://coins.llama.fi/chart/solana:%s?start=%d&span=500&period=1d' % (JLP_MINT, s)))
    f = d / ('coingecko_365d_%s.json' % today())
    if refresh or not f.exists():
        try:
            save_json(f, http_json('https://api.coingecko.com/api/v3/coins/jupiter-perpetuals-liquidity-provider-token/'
                                   'market_chart?vs_currency=usd&days=365&interval=daily'))
        except Exception as e:  # noqa: BLE001 — a gap to record, not a crash
            save_json(f, {'error': str(e)[:200]})
    f = d / ('jlp_info_%s.json' % today())
    if refresh or not f.exists():
        save_json(f, http_json('https://perps-api.jup.ag/v1/jlp-info'))
    return {'files': sorted(p.name for p in d.iterdir())}


def collect_llama(out, refresh=False):
    """DefiLlama fees (supply-side revenue = what LPs are paid) and protocol TVL, for the decomposition and capacity."""
    d = out / 'raw' / 'llama'
    d.mkdir(parents=True, exist_ok=True)
    jobs = []
    for p in ('jupiter-perpetual-exchange', 'gmx-v2-perps', 'gains-network'):
        for t in ('dailyFees', 'dailySupplySideRevenue'):
            jobs.append(('fees_%s_%s.json' % (p, t), 'https://api.llama.fi/summary/fees/%s?dataType=%s' % (p, t)))
    for p in ('jupiter-perpetual-exchange',):
        jobs.append(('protocol_%s.json.gz' % p, 'https://api.llama.fi/protocol/%s' % p))
    # yield-pool charts as an independent APY path for gUSDC (Arbitrum) and GM ETH-USDC
    for name, pool in (('gains_usdc_arbitrum', 'c48595c8-49bc-4853-80e4-f18c470bbfc3'),
                       ('gmx_eth_usdc', '61b4c35c-97f6-4c05-a5ff-aeb4426adf5b')):
        jobs.append(('yield_chart_%s.json' % name, 'https://yields.llama.fi/chart/%s' % pool))
    got = {}
    for name, url in jobs:
        f = d / name
        if refresh or not f.exists():
            try:
                obj = http_json(url)
                if name.startswith('protocol_'):
                    obj = {'name': obj.get('name'), 'tvl': obj.get('tvl'), 'chainTvls': {
                        k: {'tvl': v.get('tvl')} for k, v in (obj.get('chainTvls') or {}).items()}}
                save_json(f, obj)
            except Exception as e:  # noqa: BLE001
                save_json(f, {'error': str(e)[:200], 'url': url})
        got[name] = f.exists()
    return got


def squid(query):
    r = http_json(GMX_SQUID, {'query': query})
    if 'errors' in r:
        raise RuntimeError(json.dumps(r['errors'])[:300])
    return r['data']


def _squid_paged(entity, where, fields, order, limit=1000):
    rows, off = [], 0
    while True:
        q = '{ x: %s(where: {%s}, orderBy: %s, limit: %d, offset: %d) { %s } }' % (entity, where, order, limit, off, fields)
        page = squid(q)['x']
        rows.extend(page)
        if len(page) < limit:
            return rows
        off += limit


def collect_gmx(out, refresh=False):
    d = out / 'raw' / 'gmx'
    d.mkdir(parents=True, exist_ok=True)
    res = {}
    for name, m in GMX_TOKENS.items():
        a = m['address']
        f = d / ('prices_%s.json.gz' % name)
        if refresh or not f.exists():
            rows = _squid_paged('prices', 'token_eq: "%s", type_eq: %s, isSnapshot_eq: true' % (a, m['type']),
                                'minPrice maxPrice snapshotTimestamp', 'snapshotTimestamp_ASC')
            save_json(f, rows)
        f2 = d / ('fees1d_%s.json.gz' % name)
        if refresh or not f2.exists():
            rows = _squid_paged('collectedFeesInfos', 'address_eq: "%s", period_eq: "1d"' % a,
                                'timestampGroup feeUsdForPool borrowingFeeUsdForPool feeUsdPerPoolValue '
                                'borrowingFeeUsdPerPoolValue cumulativeFeeUsdForPool entityType', 'timestampGroup_ASC')
            save_json(f2, rows)
        f3 = d / ('apr_%s.json.gz' % name)
        if refresh or not f3.exists():
            fee = _squid_paged('aprSnapshots', 'address_eq: "%s"' % a, 'aprByFee aprByBorrowingFee snapshotTimestamp',
                               'snapshotTimestamp_ASC')
            pnl = _squid_paged('pnlAprSnapshots', 'address_eq: "%s"' % a, 'apr snapshotTimestamp', 'snapshotTimestamp_ASC')
            save_json(f3, {'fee': fee, 'pnl': pnl})
        f4 = d / ('poolvalue_%s.json.gz' % name)
        if refresh or not f4.exists():
            prices = load_json(f)
            days = sorted({int(r['snapshotTimestamp']) // 86400 * 86400 for r in prices})
            rows = []
            for i in range(0, len(days), 200):
                chunk = ','.join(str(x) for x in days[i:i + 200])
                q = ('{ x: cumulativePoolValues(where: {address_eq: "%s", isSnapshot_eq: true, snapshotTimestamp_in: [%s]}, '
                     'limit: 1000) { lastPoolValue snapshotTimestamp entityType } }' % (a, chunk))
                rows.extend(squid(q)['x'])
            save_json(f4, rows)
        res[name] = {'prices': len(load_json(f)), 'fees1d': len(load_json(f2)), 'poolvalue': len(load_json(f4))}
    f = d / ('markets_info_%s.json.gz' % today())
    if refresh or not f.exists():
        save_json(f, http_json(GMX_API + '/markets/info'))
    f = d / ('glvs_info_%s.json.gz' % today())
    if refresh or not f.exists():
        save_json(f, http_json(GMX_API + '/glvs/info'))
    f = d / ('squid_marketinfos_%s.json' % today())
    if refresh or not f.exists():
        rows = {}
        for name, m in GMX_TOKENS.items():
            if m['type'] != 'gm':
                continue
            q = ('{ x: marketInfos(where: {marketTokenAddress_eq: "%s"}, limit: 1) { marketTokenSupply poolValue '
                 'poolValueMax poolValueMin longPoolAmount shortPoolAmount longOpenInterestUsd shortOpenInterestUsd '
                 'maxLongPoolAmount maxShortPoolAmount maxLongPoolUsdForDeposit maxShortPoolUsdForDeposit '
                 'maxOpenInterestLong maxOpenInterestShort } '
                 'p: prices(where: {token_eq: "%s", type_eq: gm}, orderBy: timestamp_DESC, limit: 1) { minPrice maxPrice timestamp } }'
                 % (m['address'], m['address']))
            rows[name] = squid(q)
        save_json(f, rows)
    return res


def _arb_rpc():
    import live_rpc
    return live_rpc.RPC(url=INFURA_ARB, max_credits=3_000_000)


def _block_ts(rpc, n, cache):
    key = 'b%d' % n
    if key not in cache:
        b = rpc.batch([('eth_getBlockByNumber', [hex(n), False])])[0]
        cache[key] = int(b['timestamp'], 16)
    return cache[key]


def _anchors(rpc, cache, step=4_000_000):
    """(block, timestamp) every `step` blocks from genesis to head; cached, so a re-run costs one call."""
    head = int(rpc.batch([('eth_blockNumber', [])])[0], 16)
    out = [(n, _block_ts(rpc, n, cache)) for n in range(step, head, step)]
    out.append((head, _block_ts(rpc, head, cache)))
    return out


def interp_block(anchors, ts):
    """Linear interpolation of the block number at time ts between the bracketing (block, timestamp) anchors."""
    if ts <= anchors[0][1]:
        return anchors[0][0]
    for (b0, t0), (b1, t1) in zip(anchors, anchors[1:]):
        if t0 <= ts <= t1:
            return int(b0 + (b1 - b0) * (ts - t0) / max(1, t1 - t0))
    return anchors[-1][0]


def _block_at(rpc, ts, cache, anchors, tol=600):
    """A block within `tol` seconds before ts: interpolate between anchors, then correct with the local block rate
    (two or three calls instead of a full bisection). Good enough for a share price that moves a few bp a day."""
    key = str(ts)
    if key in cache:
        return cache[key]
    b = interp_block(anchors, ts)
    rate = None
    for _ in range(6):
        t = _block_ts(rpc, b, cache)
        if ts - tol <= t <= ts:
            break
        if rate is None:
            t2 = _block_ts(rpc, max(1, b - 20000), cache)
            rate = 20000.0 / max(1, t - t2)
        b = max(1, b - int((t - (ts - tol / 2)) * rate))
    cache[key] = b
    return b


def collect_gains(out, refresh=False):
    """gToken share price, assets, supply and accPnlPerToken at each UTC midnight, through Infura's archive node."""
    import dislocation_history as D
    sel = {k: D.sel(k) for k in ('shareToAssetsPrice()', 'totalAssets()', 'totalSupply()', 'accPnlPerToken()',
                                 'currentEpoch()', 'withdrawEpochsTimelock()', 'collateralizationP()',
                                 'accPnlPerTokenUsed()', 'accRewardsPerToken()')}
    d = out / 'raw' / 'gains'
    d.mkdir(parents=True, exist_ok=True)
    rpc = _arb_rpc()
    bf = d / 'blocks_arbitrum.json'
    blocks = {} if (refresh or not bf.exists()) else load_json(bf)
    anchors = _anchors(rpc, blocks)
    res = {}
    for name, g in GAINS.items():
        f = d / ('%s.json' % name)
        rows = {} if (refresh or not f.exists()) else load_json(f)
        start = day_ts(g['start'])
        end = day_ts(today())
        for ts in range(start, end + 1, 86400):
            day = day_of(ts)
            if day in rows:
                continue
            blk = _block_at(rpc, ts, blocks, anchors)
            calls = [('eth_call', [{'to': g['address'], 'data': s}, hex(blk)]) for s in sel.values()]
            try:
                out_ = rpc.batch(calls, allow_errors=True)
            except Exception as e:  # noqa: BLE001
                rows[day] = {'block': blk, 'error': rpc.clean(str(e))[:120]}
                continue
            rec = {'block': blk}
            for (k, _), v in zip(sel.items(), out_):
                rec[k.split('(')[0]] = v if isinstance(v, str) else None
            rows[day] = rec
            if len(rows) % 50 == 0:
                save_json(f, rows)
                save_json(bf, blocks)
        save_json(f, rows)
        save_json(bf, blocks)
        res[name] = {'days': len(rows)}
    res['rpc'] = {'requests': rpc.requests, 'errors': rpc.errors}
    return res


def collect_dydx(out, refresh=False):
    d = out / 'raw' / 'dydx'
    d.mkdir(parents=True, exist_ok=True)
    jobs = {'megavault_pnl_day_%s.json' % today(): '/vault/v1/megavault/historicalPnl?resolution=day',
            'megavault_pnl_hour_%s.json' % today(): '/vault/v1/megavault/historicalPnl?resolution=hour',
            'vaults_pnl_day_%s.json.gz' % today(): '/vault/v1/vaults/historicalPnl?resolution=day',
            'megavault_positions_%s.json' % today(): '/vault/v1/megavault/positions'}
    for name, path in jobs.items():
        f = d / name
        if refresh or not f.exists():
            save_json(f, http_json(DYDX + path))
    return {'files': sorted(p.name for p in d.iterdir())}


LIGHTER = 'https://mainnet.zklighter.elliot.ai/api/v1'
LLP_INDEX = 281474976710654        # systemConfig.liquidity_pool_index


def collect_lighter(out, refresh=False):
    """Lighter LLP: the pool account (pool_info carries the official daily return series) and the account's daily
    cumulative P&L and flows (the independent path). publicPools answers 403; these two documented endpoints work."""
    d = out / 'raw' / 'lighter'
    d.mkdir(parents=True, exist_ok=True)
    f = d / ('llp_account_%s.json.gz' % today())
    if refresh or not f.exists():
        acc = http_json('%s/account?by=index&value=%d' % (LIGHTER, LLP_INDEX))
        save_json(f, acc)
    f2 = d / ('llp_pnl_1d_%s.json.gz' % today())
    if refresh or not f2.exists():
        now = int(time.time())
        save_json(f2, http_json('%s/pnl?by=index&value=%d&resolution=1d&start_timestamp=%d&end_timestamp=%d&count_back=2000'
                                '&ignore_transfers=false' % (LIGHTER, LLP_INDEX, now - 1000 * 86400, now)))
    f3 = d / 'system_config.json'
    if refresh or not f3.exists():
        save_json(f3, http_json('%s/systemConfig' % LIGHTER))
    return {'files': sorted(p.name for p in d.iterdir())}


PROBES = [
    # (venue, what, url, method/body) — one documented endpoint each; the result is recorded, not retried
    ('Lighter LLP', 'public pool info', 'https://mainnet.zklighter.elliot.ai/api/v1/publicPools?filter=all&limit=10&index=0', None),
    ('Lighter LLP', 'system config', 'https://mainnet.zklighter.elliot.ai/api/v1/systemConfig', None),
    ('Paradex vaults', 'vault list', 'https://api.prod.paradex.trade/v1/vaults', None),
    ('Paradex vaults', 'vault summary', 'https://api.prod.paradex.trade/v1/vaults/summary', None),
    ('Extended vault', 'vault info', 'https://api.starknet.extended.exchange/api/v1/vault/public/summary', None),
    ('edgeX vault', 'pool list', 'https://pro.edgex.exchange/api/v1/public/meta/getMetaData', None),
    ('Drift insurance fund', 'IF stats', 'https://data.api.drift.trade/stats/insuranceFund', None),
    ('Aster ALP', 'ALP info', 'https://www.asterdex.com/bapi/futures/v1/public/future/alp/info', None),
    ('Avantis vaults', 'vault stats', 'https://api.avantisfi.com/v1/vault/stats', None),
    ('Ostium OLP', 'vault info', 'https://metadata-backend.ostium.io/vault/stats', None),
]


def collect_probes(out, refresh=False):
    d = out / 'raw' / 'probes'
    d.mkdir(parents=True, exist_ok=True)
    f = d / 'probes.json'
    if f.exists() and not refresh:
        return load_json(f)
    res = []
    for venue, what, url, body in PROBES:
        rec = {'venue': venue, 'what': what, 'url': url, 'at': dt.datetime.now(dt.timezone.utc).isoformat()}
        try:
            r = http_json(url, body, retries=1, timeout=30)
            s = json.dumps(r)
            rec.update({'ok': True, 'bytes': len(s), 'head': s[:300]})
        except urllib.error.HTTPError as e:
            rec.update({'ok': False, 'error': 'HTTP %d' % e.code})
        except Exception as e:  # noqa: BLE001
            rec.update({'ok': False, 'error': str(e)[:160]})
        res.append(rec)
    save_json(f, res)
    return res


COLLECTORS = {'hlp': collect_hlp, 'binance': collect_binance, 'jlp': collect_jlp, 'llama': collect_llama,
              'gmx': collect_gmx, 'gains': collect_gains, 'dydx': collect_dydx, 'lighter': collect_lighter,
              'probes': collect_probes}


def cmd_collect(args):
    out = Path(args.out)
    parts = [p.strip() for p in args.parts.split(',') if p.strip()]
    for p in parts:
        mf = out / 'raw' / ('manifest_%s.json' % p)
        t0 = time.time()
        before = dict(STATS, by_host=dict(STATS['by_host']))
        try:
            res = COLLECTORS[p](out, refresh=args.refresh)
            ok = True
        except Exception as e:  # noqa: BLE001 — record the gap, keep the other parts going
            res, ok = {'error': str(e)[:300]}, False
        man = {'part': p, 'ok': ok, 'result': res, 'finished': dt.datetime.now(dt.timezone.utc).isoformat(),
                  'seconds': round(time.time() - t0, 1),
                  'http_requests': STATS['requests'] - before['requests'], 'http_errors': STATS['errors'] - before['errors'],
                  'http_throttled': STATS['throttled'] - before['throttled']}
        save_json(mf, man)
        print(p, 'ok' if ok else 'FAILED', json.dumps(res)[:300], flush=True)


# ----------------------------------------------------------------------------------------------------------------------
# Core math (pure functions; tested in test_house_vaults.py)
# ----------------------------------------------------------------------------------------------------------------------
H_MS = 3600 * 1000
DAY_MS = 86400 * 1000


def dietz_returns(points):
    """[(t, account_value, cumulative_pnl)] -> list of period dicts, net of deposits and withdrawals.

    The vault's cumulative P&L excludes flows by construction, so the period P&L is the change in it; the flow is what
    the account value did beyond that (flow = dAV - dpnl). The return is modified Dietz, dpnl / (AV0 + flow/2): flows are
    assumed to arrive mid-period. `r_simple` = dpnl / AV0 is kept as the check. Periods with no capital are skipped.
    """
    out = []
    for (t0, a0, p0), (t1, a1, p1) in zip(points, points[1:]):
        dp = p1 - p0
        flow = (a1 - a0) - dp
        base = a0 + 0.5 * flow
        if a0 <= 0 or base <= 0 or t1 <= t0:
            continue
        out.append({'t0': t0, 't1': t1, 'days': (t1 - t0) / DAY_MS, 'r_v': dp / base, 'r_simple': dp / a0,
                    'flow': flow, 'dpnl': dp, 'tvl0': a0, 'tvl1': a1})
    return out


def price_returns(points, drop_stale=True):
    """[(t, price)] -> period dicts with r_v = p1/p0 - 1. A price identical to the previous one is treated as stale (no
    update that day) and skipped, so the next period spans the gap; the hedge legs are measured over the same span."""
    pts = sorted((t, p) for t, p in points if p is not None and p > 0)
    if drop_stale:
        kept = []
        for t, p in pts:
            if kept and p == kept[-1][1]:
                continue
            kept.append((t, p))
        pts = kept
    out = []
    for (t0, p0), (t1, p1) in zip(pts, pts[1:]):
        out.append({'t0': t0, 't1': t1, 'days': (t1 - t0) / DAY_MS, 'r_v': p1 / p0 - 1.0, 'p0': p0, 'p1': p1})
    return out


def savings_between(t0_ms, t1_ms, table=None):
    """Savings-rate return over (t0, t1], pro rata by calendar year at the rate actually paid that year (simple)."""
    table = table or SAVINGS_BY_YEAR
    total, t, end = 0.0, t0_ms / 1000.0, t1_ms / 1000.0
    while t < end:
        y = utc(t).year
        ny = dt.datetime(y + 1, 1, 1, tzinfo=dt.timezone.utc).timestamp()
        seg = min(end, ny) - t
        total += table.get(y, table[max(table)]) * seg / (365.0 * 86400)
        t += seg
    return total


def solve(A, b):
    """Gaussian elimination with partial pivoting for a small dense system; None if singular."""
    n = len(A)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-15:
            return None
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def ols(y, X):
    """OLS with intercept. y: list; X: list of rows (k regressors). Returns {'alpha','betas','r2','n','se','t'}."""
    n = len(y)
    if n == 0:
        return None
    k = len(X[0]) if X else 0
    Z = [[1.0] + list(map(float, row)) for row in X]
    p = k + 1
    if n <= p:
        return None
    ZtZ = [[sum(Z[i][a] * Z[i][b] for i in range(n)) for b in range(p)] for a in range(p)]
    Zty = [sum(Z[i][a] * y[i] for i in range(n)) for a in range(p)]
    coef = solve(ZtZ, Zty)
    if coef is None:
        return None
    fit = [sum(coef[a] * Z[i][a] for a in range(p)) for i in range(n)]
    res = [y[i] - fit[i] for i in range(n)]
    ybar = sum(y) / n
    sst = sum((v - ybar) ** 2 for v in y)
    ssr = sum(v * v for v in res)
    s2 = ssr / (n - p)
    se, t = [], []
    for a in range(p):
        e = [1.0 if i == a else 0.0 for i in range(p)]
        col = solve(ZtZ, e)
        v = col[a] * s2 if col else None
        se.append(math.sqrt(v) if v and v > 0 else None)
        t.append(coef[a] / se[-1] if se[-1] else None)
    return {'alpha': coef[0], 'betas': coef[1:], 'r2': (1 - ssr / sst) if sst > 0 else None, 'n': n,
            'se': se, 't': t}


def static_betas(periods, assets, upto):
    """In-sample OLS betas of the vault return on the asset returns over periods[:upto]."""
    if not assets:
        return {}
    rows = [p for p in periods[:upto] if all(a in p['r'] for a in assets)]
    fit = ols([p['r_v'] for p in rows], [[p['r'][a] for a in assets] for p in rows])
    return dict(zip(assets, fit['betas'])) if fit else {}


def rolling_betas(periods, assets, window_days, every_days=7, min_obs=20):
    """Betas set at the start of each period from an OLS on the periods that ended within the trailing window (no
    look-ahead); refitted every `every_days`, held in between. Before enough history: unhedged ({})."""
    out, cur, last_fit = [], {}, None
    for i, p in enumerate(periods):
        if last_fit is None or (p['t0'] - last_fit) >= every_days * DAY_MS:
            lo = p['t0'] - window_days * DAY_MS
            rows = [q for q in periods[:i] if q['t1'] <= p['t0'] and q['t0'] >= lo and all(a in q['r'] for a in assets)]
            if len(rows) >= min_obs:
                fit = ols([q['r_v'] for q in rows], [[q['r'][a] for a in assets] for q in rows])
                if fit:
                    cur = dict(zip(assets, fit['betas']))
                    last_fit = p['t0']
        out.append(dict(cur))
    return out


def simulate_hedge(periods, betas, fee=None, margin=None, band=None):
    """Run a short-perp hedge against a vault return series.

    Each period: the vault returns r_v on one unit; leg k holds h_k (short notional per unit of vault value, negative =
    long) and earns -h_k * r_k (price) + h_k * f_k (funding: positive rates pay the short). Before the period, each leg
    is traded to its target beta when it has drifted more than `band` from it (always when the target is zero or the
    sign flips), at `fee` per unit traded. Capital = 1 + margin * sum|h| (idle cash margin). Returned per period:
    pnl (per unit of vault), cost, capital, ret = pnl / capital, and the legs' price and funding P&L.
    """
    fee = HEDGE_FEE if fee is None else fee
    margin = MARGIN if margin is None else margin
    band = REBAL_BAND if band is None else band
    held = {}
    out = []
    for p, tgt in zip(periods, betas):
        tgt = tgt or {}
        cost, traded = 0.0, 0.0
        for k in set(held) | set(tgt):
            h, b = held.get(k, 0.0), tgt.get(k, 0.0)
            if b == 0.0 or h == 0.0 or (h > 0) != (b > 0) or abs(h - b) > band * abs(b):
                traded += abs(b - h)
                held[k] = b
        held = {k: v for k, v in held.items() if v != 0.0}
        cost = fee * traded
        price_pnl = sum(-h * p['r'].get(k, 0.0) for k, h in held.items())
        fund_pnl = sum(h * p['f'].get(k, 0.0) for k, h in held.items())
        gross = sum(abs(h) for h in held.values())
        pnl = p['r_v'] + price_pnl + fund_pnl - cost
        cap = 1.0 + margin * gross
        out.append({'pnl': pnl, 'cost': cost, 'capital': cap, 'ret': pnl / cap, 'price_pnl': price_pnl,
                    'fund_pnl': fund_pnl, 'gross': gross, 'traded': traded})
        g = 1.0 + p['r_v']
        held = {k: h * (1.0 + p['r'].get(k, 0.0)) / g for k, h in held.items()} if g > 0 else {}
    return out


def close_cost(gross, fee=None):
    return (HEDGE_FEE if fee is None else fee) * gross


def apply_rule(periods, shadow, rule, entry_exit=0.0, lookback_days=30.0, start_on=None):
    """Turn an always-on excess series into a rule's series.

    shadow[i] = {'ret','capital','gross','s'} for always-on; rule = None (always on) or a threshold on the trailing
    `lookback_days` annualised excess (known before period i starts). Off periods earn exactly the savings rate (excess
    0). Switching on pays half the vault round trip plus opening the hedge; switching off pays the other half plus
    closing it. The first period of a segment opens the position; the caller closes it at the segment's end.
    """
    out, on_prev = [], False if start_on is None else start_on
    for i, p in enumerate(periods):
        if rule is None:
            on = True
        else:
            lo = p['t0'] - lookback_days * DAY_MS
            win = [j for j in range(i) if periods[j]['t1'] <= p['t0'] and periods[j]['t0'] >= lo]
            days = sum(periods[j]['days'] for j in win)
            if days < 0.6 * lookback_days:
                on = False
            else:
                ex = sum(shadow[j]['ret'] - shadow[j]['s'] for j in win) / days * 365.0
                on = ex > rule
        x = 0.0
        if on:
            x = shadow[i]['ret'] - shadow[i]['s']
            if not on_prev:
                x -= (entry_exit / 2.0 + close_cost(shadow[i]['gross'])) / shadow[i]['capital']
        elif on_prev:
            x -= (entry_exit / 2.0 + close_cost(shadow[i - 1]['gross'] if i else 0.0)) / shadow[i - 1 if i else 0]['capital']
        out.append({'x': x, 'on': on})
        on_prev = on
    return out


def worst_window(periods, xs, days=7.0):
    """Worst sum of excess over any run of consecutive periods spanning at most `days` (>= one period)."""
    worst, n = None, len(xs)
    for i in range(n):
        s, span = 0.0, 0.0
        for j in range(i, n):
            span += periods[j]['days']
            if j > i and span > days + 1e-9:
                break
            s += xs[j]
            worst = s if worst is None or s < worst else worst
    return worst


def best_share(xs, frac=0.01):
    """Share of the total P&L earned in the best `frac` of periods (at least one)."""
    tot = sum(xs)
    if not xs or tot == 0:
        return None
    k = max(1, int(round(frac * len(xs))))
    return sum(sorted(xs, reverse=True)[:k]) / tot


def nw_lags(periods, days=30.0):
    d = statistics.median([p['days'] for p in periods]) if periods else 1.0
    return max(1, int(round(days / max(d, 1e-9))))


def seg_stats(periods, xs):
    """Summary of an excess series over a segment: time-annualised mean, NW t (30-day lags), block bootstrap CI of the
    annualised mean (30-day blocks), drawdown, worst week, best-1% share."""
    if not xs:
        return {'n': 0}
    days = sum(p['days'] for p in periods)
    ann = sum(xs) / days * 365.0 if days else None
    lags = nw_lags(periods)
    t, pv = B.newey_west_t(xs, lags=lags)
    per_year = 365.0 / statistics.median([p['days'] for p in periods])
    bb = B.block_bootstrap(xs, block=lags, n=2000)
    pf = B.perf(xs, per_year)
    return {'n': len(xs), 'start': day_of(periods[0]['t0']), 'end': day_of(periods[-1]['t1']), 'days': round(days, 1),
            'ann_excess': ann, 'nw_t': t, 'nw_p': pv, 'nw_lags': lags,
            'boot_lo': bb['lo'] * per_year if bb['lo'] is not None else None,
            'boot_hi': bb['hi'] * per_year if bb['hi'] is not None else None, 'boot_p_le_0': bb['p_le_0'],
            'sharpe': pf.get('sharpe'), 'ann_vol': pf.get('ann_vol'), 'max_drawdown': pf.get('max_drawdown'),
            'worst_period': pf.get('worst'), 'best_period': pf.get('best'), 'worst_week': worst_window(periods, xs, 7.0),
            'best1pct_share': best_share(xs), 'hit_rate': pf.get('hit_rate'), 'active_share': pf.get('active_share'),
            'skew': pf.get('skew'), 'kurtosis': pf.get('kurtosis')}


def income_vs_tvl(rows):
    """rows: [(tvl_usd, income_usd_per_day)] -> OLS income = a + b * tvl. a is the fixed (TVL-independent) dollar
    income a day, b the part proportional to TVL (a daily rate). Also the median TVL and median income."""
    rows = [(x, y) for x, y in rows if x and x > 0 and y is not None]
    if len(rows) < 8:
        return None
    fit = ols([y for _, y in rows], [[x] for x, _ in rows])
    if not fit:
        return None
    return {'n': len(rows), 'a_usd_day': fit['alpha'], 'b_per_day': fit['betas'][0], 't_a': fit['t'][0],
            't_b': fit['t'][1], 'r2': fit['r2'], 'median_tvl': statistics.median(x for x, _ in rows),
            'median_income_day': statistics.median(y for _, y in rows), 'mean_income_day': sum(y for _, y in rows) / len(rows)}


def diluted_excess(a_usd_day, b_per_day, tvl, deposit, savings):
    """Annual excess over the savings rate for the vault as a whole after a deposit X: (a + b (T + X)) / (T + X) * 365 -
    s. With b = 0 (fixed income) every dollar dilutes; with a = 0 (proportional) none does."""
    T = tvl + deposit
    if T <= 0:
        return None
    return (a_usd_day + b_per_day * T) / T * 365.0 - savings


def deposit_for_excess(a_usd_day, b_per_day, tvl, savings, target):
    """Largest deposit X with diluted_excess >= target: solve (a/T + b) * 365 - s = target for T, return T - tvl."""
    need = (target + savings) / 365.0 - b_per_day
    if a_usd_day <= 0:
        return 0.0 if (b_per_day * 365.0 - savings) < target else float('inf')
    if need <= 0:
        return float('inf')
    return max(0.0, a_usd_day / need - tvl)


def apply_rule_segments(periods, shadow, rule, entry_exit=0.0, lookback_days=30.0, starts=(0,)):
    """apply_rule over several segments that each start flat and end flat (the in-sample and test halves).

    shadow[i] carries the always-on hedged return of a hedge simulated from flat at each segment start, so the opening
    hedge trade of a segment's first period is already in shadow; later switch-ons pay it here."""
    n = len(periods)
    starts = sorted(set(starts))
    ends = {s - 1 for s in starts if s > 0} | {n - 1}
    out, on_prev = [], False
    for i, p in enumerate(periods):
        if i in starts:
            on_prev = False
        if rule is None:
            on = True
        else:
            lo = p['t0'] - lookback_days * DAY_MS
            win = [j for j in range(i) if periods[j]['t1'] <= p['t0'] and periods[j]['t0'] >= lo - 1]
            days = sum(periods[j]['days'] for j in win)
            on = False
            if days >= 0.6 * lookback_days:
                on = sum(shadow[j]['ret'] - shadow[j]['s'] for j in win) / days * 365.0 > rule
        x = 0.0
        if on:
            cap = shadow[i]['capital']
            x = shadow[i]['ret'] - shadow[i]['s']
            if not on_prev:
                x -= entry_exit / 2.0 / cap
                if i not in starts:
                    x -= close_cost(shadow[i]['gross']) / cap
            if i in ends:
                x -= (entry_exit / 2.0 + close_cost(shadow[i]['gross'])) / cap
        elif on_prev and i not in starts:
            x -= (entry_exit / 2.0 + close_cost(shadow[i - 1]['gross'])) / shadow[i - 1]['capital']
        out.append({'x': x, 'on': on})
        on_prev = on
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Hedge-leg prices and funding (Binance USDT-margined perps)
# ----------------------------------------------------------------------------------------------------------------------
class PriceBook:
    """Hourly perp closes and funding settlements for the hedge assets."""

    def __init__(self, raw):
        import bisect
        self._bisect = bisect
        self.close, self.qvol, self.ft, self.fcum = {}, {}, {}, {}
        for a, sym in HEDGE_SYMBOLS.items():
            kf, ff = raw / 'binance' / ('klines1h_%s.json.gz' % sym), raw / 'binance' / ('funding_%s.json.gz' % sym)
            if kf.exists():
                rows = load_json(kf)
                self.close[a] = {int(r[0]): float(r[4]) for r in rows}
                self.qvol[a] = {int(r[0]): float(r[5]) for r in rows}
            if ff.exists():
                rows = sorted(load_json(ff), key=lambda r: r['t'])
                self.ft[a] = [int(r['t']) for r in rows]
                c, acc = [0.0], 0.0
                for r in rows:
                    acc += float(r['rate'])
                    c.append(acc)
                self.fcum[a] = c

    def price(self, a, t_ms):
        """Close of the last hourly bar that closed at or before t."""
        c = self.close.get(a)
        if not c:
            return None
        h = (int(t_ms) // H_MS) * H_MS - H_MS
        for _ in range(4):
            if h in c:
                return c[h]
            h -= H_MS
        return None

    def ret(self, a, t0, t1):
        p0, p1 = self.price(a, t0), self.price(a, t1)
        return (p1 / p0 - 1.0) if p0 and p1 else None

    def funding(self, a, t0, t1):
        """Sum of funding rates settled in (t0, t1]; positive = longs paid shorts."""
        ts = self.ft.get(a)
        if not ts:
            return None
        i0 = self._bisect.bisect_right(ts, int(t0))
        i1 = self._bisect.bisect_right(ts, int(t1))
        return self.fcum[a][i1] - self.fcum[a][i0]

    def daily_quote_volume(self, a, days=30):
        q = self.qvol.get(a)
        if not q:
            return None
        last = max(q)
        tot = sum(v for t, v in q.items() if t > last - days * DAY_MS)
        return tot / days


def attach_legs(periods, book, assets):
    """Add asset returns, funding sums and the savings return to each period; drop periods a leg cannot price."""
    out = []
    for p in periods:
        r, f, ok = {}, {}, True
        for a in assets:
            ra, fa = book.ret(a, p['t0'], p['t1']), book.funding(a, p['t0'], p['t1'])
            if ra is None or fa is None:
                ok = False
                break
            r[a], f[a] = ra, fa
        if not ok:
            continue
        q = dict(p)
        q.update({'r': r, 'f': f, 's': savings_between(p['t0'], p['t1'])})
        out.append(q)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Loaders
# ----------------------------------------------------------------------------------------------------------------------
def latest_dir(d):
    ds = sorted(x for x in d.iterdir() if x.is_dir()) if d.exists() else []
    return ds[-1] if ds else None


def load_hlp(raw):
    snap = latest_dir(raw / 'hlp')
    parent = load_json(snap / ('vault_%s.json.gz' % HLP))
    kids = {}
    for k in (parent.get('relationship') or {}).get('data', {}).get('childAddresses', []):
        f = snap / ('vault_%s.json.gz' % k.lower())
        if f.exists():
            c = load_json(f)
            kids[c['name']] = {'address': k, 'allTime': parse_hl_portfolio(c, 'allTime'),
                               'month': parse_hl_portfolio(c, 'month')}
    led = snap / 'ledger_7d.json.gz'
    return {'snapshot': snap.name, 'parent': parent, 'allTime': parse_hl_portfolio(parent, 'allTime'),
            'month': parse_hl_portfolio(parent, 'month'), 'week': parse_hl_portfolio(parent, 'week'),
            'perpAllTime': parse_hl_portfolio(parent, 'perpAllTime'), 'children': kids,
            'ledger': load_json(led) if led.exists() else None}


def load_jlp(raw):
    d = raw / 'jlp'
    objs = [load_json(f) for f in sorted(d.glob('llama_chart_*.json'))]
    pts = {}
    for o in objs:
        for v in (o.get('coins') or {}).values():
            for x in v.get('prices', []):
                pts[int(x['timestamp']) * 1000] = float(x['price'])
    cg = None
    cgs = sorted(d.glob('coingecko_365d_*.json'))
    if cgs:
        c = load_json(cgs[-1])
        if 'prices' in c:
            cg = [(int(t), float(p)) for t, p in c['prices']]
    infos = sorted(d.glob('jlp_info_*.json'))
    return {'points': sorted(pts.items()), 'coingecko': cg, 'info': load_json(infos[-1]) if infos else None}


def load_gmx(raw, name):
    d = raw / 'gmx'
    prices = load_json(d / ('prices_%s.json.gz' % name))
    pts = sorted((int(r['snapshotTimestamp']) * 1000, (int(r['minPrice']) + int(r['maxPrice'])) / 2e30) for r in prices)
    pv = {}
    f = d / ('poolvalue_%s.json.gz' % name)
    if f.exists():
        for r in load_json(f):
            pv[int(r['snapshotTimestamp']) * 1000] = int(r['lastPoolValue']) / 1e30
    fees = {}
    f = d / ('fees1d_%s.json.gz' % name)
    if f.exists():
        for r in load_json(f):
            fees[int(r['timestampGroup']) * 1000] = {
                'fee_usd': int(r['feeUsdForPool']) / 1e30, 'borrow_usd': int(r['borrowingFeeUsdForPool'] or 0) / 1e30}
    apr = load_json(d / ('apr_%s.json.gz' % name)) if (d / ('apr_%s.json.gz' % name)).exists() else {'fee': [], 'pnl': []}
    return {'points': pts, 'tvl': pv, 'fees': fees, 'apr': apr}


def load_gains(raw, name):
    f = raw / 'gains' / ('%s.json' % name)
    if not f.exists():
        return None
    rows = load_json(f)
    pts, tvl, extra = [], {}, {}
    dec = GAINS[name]['decimals']
    for day, r in sorted(rows.items()):
        px = hex_uint(r.get('shareToAssetsPrice'))
        if not px:
            continue
        t = day_ts(day) * 1000
        pts.append((t, px / 1e18))
        ta = hex_uint(r.get('totalAssets'))
        ts_ = hex_uint(r.get('totalSupply'))
        if ta:
            tvl[t] = ta / 10 ** dec
        extra[t] = {'totalAssets': ta / 10 ** dec if ta else None, 'totalSupply': ts_ / 10 ** dec if ts_ else None,
                    'accPnlPerToken': (hex_int256(r.get('accPnlPerToken')) or 0) / 1e18,
                    'accRewardsPerToken': (hex_uint(r.get('accRewardsPerToken')) or 0) / 1e18,
                    'collateralizationP': hex_uint(r.get('collateralizationP')),
                    'withdrawEpochsTimelock': hex_uint(r.get('withdrawEpochsTimelock')),
                    'currentEpoch': hex_uint(r.get('currentEpoch'))}
    return {'points': pts, 'tvl': tvl, 'extra': extra}


def load_dydx(raw):
    d = raw / 'dydx'
    fs = sorted(d.glob('megavault_pnl_day_*.json'))
    if not fs:
        return None
    rows = parse_dydx_pnl(load_json(fs[-1])['megavaultPnl'])
    return {'points': [(t, e, p) for t, e, p, _ in rows], 'transfers': rows}


# ----------------------------------------------------------------------------------------------------------------------
# The protocol: pre-committed variants, chosen on the first half of each vault's history, tested once on the second
# ----------------------------------------------------------------------------------------------------------------------
RULES = {'always': None, 'trail30>0': 0.0, 'trail30>2pp': 0.02}


def variant_plan(assets, comp=None, roll_days=60):
    """The variant list, fixed before any test-half number is computed (its hash goes into analysis.json)."""
    hedges = ['none', 'static', 'roll%d' % roll_days] + (['comp'] if comp else [])
    return {'hedges': hedges, 'rules': list(RULES), 'assets': list(assets), 'comp': comp, 'roll_days': roll_days}


def run_protocol(name, periods, assets, comp=None, entry_exit=0.0, roll_days=60, every_days=7, min_obs=20,
                 warmup_days=60):
    plan = variant_plan(assets, comp, roll_days)
    plan_hash = hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:16]
    t_start = periods[0]['t0'] + warmup_days * DAY_MS
    roll_full = rolling_betas(periods, assets, roll_days, every_days, min_obs)
    idx = [i for i, p in enumerate(periods) if p['t0'] >= t_start]
    P = [periods[i] for i in idx]
    n = len(P)
    c = B.cutoff_index(n, 0.5)
    hedges = {'none': [{}] * n}
    st = static_betas(P, assets, c)
    hedges['static'] = [st] * n
    hedges['roll%d' % roll_days] = [roll_full[i] for i in idx]
    if comp:
        hedges['comp'] = [comp] * n
    variants, shadows, onflags = {}, {}, {}
    for hn, betas in hedges.items():
        sh = simulate_hedge(P[:c], betas[:c]) + simulate_hedge(P[c:], betas[c:])
        for i, s in enumerate(sh):
            s['s'] = P[i]['s']
        shadows[hn] = sh
        for rn, thr in RULES.items():
            ap = apply_rule_segments(P, sh, thr, entry_exit, 30.0, starts=(0, c))
            variants['%s|%s' % (hn, rn)] = [x['x'] for x in ap]
            onflags['%s|%s' % (hn, rn)] = [x['on'] for x in ap]
    ppy = 365.0 / statistics.median([p['days'] for p in P])
    ct = B.choose_then_test(variants, frac=0.5, periods_per_year=ppy)
    per_variant = {}
    for k, xs in variants.items():
        per_variant[k] = {'in': seg_stats(P[:c], xs[:c]), 'out': seg_stats(P[c:], xs[c:]),
                          'on_share_out': sum(onflags[k][c:]) / max(1, n - c)}
    # deflated Sharpe of the in-sample choice given every variant tried, with the variants' own Sharpe spread
    ch = ct['chosen']
    hn_ch = ch.split('|')[0]
    sh = shadows[hn_ch]
    comp_out = decompose(P[c:], sh[c:], [x for x in onflags[ch][c:]])
    comp_in = decompose(P[:c], sh[:c], [x for x in onflags[ch][:c]])
    # late entry: the chosen rule's signal lagged one period
    late = None
    if RULES[ch.split('|')[1]] is not None:
        on = onflags[ch]
        lagged = [False] + on[:-1]
        xs = []
        for i in range(c, n):
            xs.append((sh[i]['ret'] - sh[i]['s']) if lagged[i] else 0.0)
        tot0 = sum(variants[ch][c:])
        late = {'lag_periods': 1, 'ann_excess_lagged': sum(xs) / sum(p['days'] for p in P[c:]) * 365.0,
                'share_kept': (sum(xs) / tot0) if tot0 else None}
    by_year = {}
    for i, p in enumerate(P):
        y = utc(p['t1']).year
        b = by_year.setdefault(y, {'days': 0.0, 'raw': 0.0, 'chosen': 0.0, 'static_always': 0.0, 'none_always': 0.0,
                                   's': 0.0, 'n': 0})
        b['days'] += p['days']
        b['raw'] += p['r_v']
        b['s'] += p['s']
        b['chosen'] += variants[ch][i]
        b['static_always'] += variants['static|always'][i]
        b['none_always'] += variants['none|always'][i]
        b['n'] += 1
    for y, b in by_year.items():
        for k in ('raw', 'chosen', 'static_always', 'none_always', 's'):
            b[k + '_ann'] = b[k] / b['days'] * 365.0 if b['days'] else None
    return {
        'name': name, 'plan': plan, 'plan_sha256_16': plan_hash, 'n_periods': n, 'cutoff_index': c,
        'in_sample': [day_of(P[0]['t0']), day_of(P[c - 1]['t1'])], 'test': [day_of(P[c]['t0']), day_of(P[-1]['t1'])],
        'median_period_days': statistics.median([p['days'] for p in P]), 'periods_per_year': ppy,
        'static_betas_in_sample': st, 'last_rolling_betas': hedges['roll%d' % roll_days][-1],
        'chosen': ch, 'oos_rank': ct['oos_rank'], 'n_variants': ct['n_variants'],
        'deflated_sharpe_in_sample': ct['deflated_sharpe_in_sample'],
        'bh_survivors_full_sample': ct['bh_survivors_full_sample'],
        'chosen_in': per_variant[ch]['in'], 'chosen_out': per_variant[ch]['out'],
        'variants': per_variant, 'decomposition_in': comp_in, 'decomposition_out': comp_out,
        'late_entry': late, 'by_year': by_year,
        '_series': {'P': P, 'P_all': periods, 'variants': variants, 'shadows': shadows, 'onflags': onflags, 'c': c},
    }


def decompose(P, sh, on):
    """Annualised components of the hedged series (per unit of vault value, then the capital factor), over periods
    where the rule was on: vault return, hedge price P&L, hedge funding, rebalance costs, savings."""
    days = sum(p['days'] for p, o in zip(P, on) if o)
    if not days:
        return None
    a = lambda xs: sum(xs) / days * 365.0  # noqa: E731
    sel = [(p, s) for p, s, o in zip(P, sh, on) if o]
    return {'days_on': round(days, 1), 'vault': a([p['r_v'] for p, _ in sel]), 'hedge_price': a([s['price_pnl'] for _, s in sel]),
            'hedge_funding': a([s['fund_pnl'] for _, s in sel]), 'rebalance_cost': a([s['cost'] for _, s in sel]),
            'pnl_per_vault_unit': a([s['pnl'] for _, s in sel]), 'mean_capital': sum(s['capital'] for _, s in sel) / len(sel),
            'savings': a([p['s'] for p, _ in sel]), 'mean_gross_hedge': sum(s['gross'] for _, s in sel) / len(sel)}


def events(P, xs, k=5):
    """Worst and best k periods of an excess series, dated."""
    idx = sorted(range(len(xs)), key=lambda i: xs[i])
    f = lambda i: {'start': utc(P[i]['t0']).isoformat()[:16], 'end': utc(P[i]['t1']).isoformat()[:16],  # noqa: E731
                   'excess': xs[i], 'vault_return': P[i]['r_v'], 'assets': P[i]['r']}
    return {'worst': [f(i) for i in idx[:k]], 'best': [f(i) for i in idx[::-1][:k]]}


INCIDENTS = [  # dated incidents to look up in each vault's series (the series, not this list, says what happened)
    ('2024-08-05', 'yen carry unwind crash'),
    ('2025-02-03', 'tariff-headline crash'),
    ('2025-03-12', 'Hyperliquid ETH 50x whale exits through HLP (reported HLP loss ~$4M)'),
    ('2025-03-26', 'Hyperliquid JELLY squeeze; market delisted'),
    ('2025-04-07', 'April 2025 tariff crash'),
    ('2025-10-10', '10 Oct 2025 liquidation cascade and auto-deleveraging'),
    ('2025-11-12', 'Hyperliquid POPCAT manipulation (reported HLP loss ~$5M)'),
]


def incident_rows(P, xs):
    out = []
    for day, what in INCIDENTS:
        t = day_ts(day) * 1000 + 12 * H_MS
        for i, p in enumerate(P):
            if p['t0'] <= t < p['t1']:
                out.append({'date': day, 'incident': what, 'period': [utc(p['t0']).isoformat()[:16], utc(p['t1']).isoformat()[:16]],
                            'vault_return': p['r_v'], 'excess': xs[i], 'assets': p['r']})
                break
    return out


def load_lighter(raw):
    d = raw / 'lighter'
    accs = sorted(d.glob('llp_account_*.json.gz'))
    pnls = sorted(d.glob('llp_pnl_1d_*.json.gz'))
    if not accs or not pnls:
        return None
    acc = load_json(accs[-1])['accounts'][0]
    rows = sorted(load_json(pnls[-1])['pnl'], key=lambda r: r['timestamp'])
    # one row per UTC midnight: the API appends an intraday row stamped at the current day's midnight; keep the first
    seen, pts = set(), []
    for r in rows:
        t = int(r['timestamp'])
        if t % 86400 or t in seen:
            continue
        seen.add(t)
        value = float(r['inflow']) - float(r['outflow']) + float(r['trade_pnl'])
        pts.append((t * 1000, value, float(r['trade_pnl']), float(r.get('pool_total_shares') or 0)))
    official = [(int(x['timestamp']) * 1000, float(x['daily_return'])) for x in acc['pool_info'].get('daily_returns', [])]
    share = [(t, v / sh) for t, v, _, sh in pts if sh > 0]
    return {'points': [(t, v, p) for t, v, p, _ in pts], 'share_points': share, 'official': official,
            'tvl_now': float(acc.get('total_asset_value') or 0),
            'apy_official': acc['pool_info'].get('annual_percentage_yield'), 'operator_fee': acc['pool_info'].get('operator_fee'),
            'positions': len(acc.get('positions') or [])}


def interp_cum(points, t):
    """Cumulative P&L at time t from a (t, av, pnl) grid by linear interpolation; 0 before the first point."""
    if not points or t <= points[0][0]:
        return 0.0
    for (t0, _, p0), (t1, _, p1) in zip(points, points[1:]):
        if t0 <= t <= t1:
            return p0 + (p1 - p0) * (t - t0) / max(1, t1 - t0)
    return points[-1][2]


def lagged_beta(P, asset):
    """Staleness check: OLS of the vault return on the asset's same-period and previous-period returns."""
    rows = [(P[i]['r_v'], P[i]['r'][asset], P[i - 1]['r'][asset]) for i in range(1, len(P))
            if asset in P[i]['r'] and asset in P[i - 1]['r']]
    fit = ols([r[0] for r in rows], [[r[1], r[2]] for r in rows])
    if not fit:
        return None
    return {'asset': asset, 'beta_same': fit['betas'][0], 'beta_lag': fit['betas'][1], 't_lag': fit['t'][2], 'n': fit['n']}


def tvl_lookup(series):
    """{t_ms: tvl} -> function t -> the latest TVL at or before t (None before the first)."""
    import bisect
    ks = sorted(series)
    vs = [series[k] for k in ks]

    def f(t):
        i = bisect.bisect_right(ks, t) - 1
        return vs[i] if i >= 0 else None
    return f


def nav_points(P):
    """A NAV index from a period series: 1 at the first start, compounded at each period end."""
    if not P:
        return []
    out, v = [(P[0]['t0'], 1.0)], 1.0
    for p in P:
        v *= 1.0 + p['r_v']
        out.append((p['t1'], v))
    return out


def finish(res, tvl_at, tvl_now, extra=None, book=None):
    """Common extras for one vault: events, incidents, late entry, capacity, dilution and (daily series) the weekly
    re-measurement of the test half."""
    S = res['_series']
    P, c, ch = S['P'], S['c'], res['chosen']
    if book is not None and res['median_period_days'] <= 1.5:
        rob = res.setdefault('robustness', {})
        nav = nav_points(S['P_all'])
        rob['weekly_grid'] = weekly_check(nav, book, res['plan']['assets'], P[c]['t0'])
        rob['daily_roll120'] = weekly_check(nav, book, res['plan']['assets'], P[c]['t0'], step=1, roll_days=120, min_obs=40)
        rob['note'] = ('re-measurements of the test half, never used for selection: every 7th point with a 120-day '
                       'trailing hedge, and daily with a 120-day trailing hedge (added after JLP\'s 60- and 120-day '
                       'windows disagreed; applied to every daily vault)')
    xs = S['variants'][ch]
    hn = ch.split('|')[0]
    sh = S['shadows'][hn]
    res['events_test'] = events(P[c:], xs[c:])
    res['incidents'] = incident_rows(P, S['variants'][hn + '|always'])
    xo, Po = xs[c:], P[c:]
    days = sum(p['days'] for p in Po)
    k = max(1, int(round(0.01 * len(xo))))
    top = sorted(range(len(xo)), key=lambda i: -xo[i])[:k]
    res['late_entry_jumps'] = {
        'best1pct_periods': [[day_of(Po[i]['t0']), day_of(Po[i]['t1']), xo[i]] for i in top],
        'best1pct_share': best_share(xo), 'ann_excess_ex_best1pct': (sum(xo) - sum(xo[i] for i in top)) / days * 365.0,
        'one_hour_late_share_kept': 1.0 - (1.0 / 24.0) / days if days else None,
        'one_day_late_share_kept': 1.0 - 1.0 / days if days else None,
        'note': 'an always-on deposit loses only the hour/day it is late; the jumps are what a timer would miss'}
    # Capacity: vault-level hedged dollar income (vault return + hedge price P&L, before our funding and costs)
    rows = []
    for i in range(c, len(P)):
        tv = tvl_at(P[i]['t0'])
        if tv:
            rows.append((tv, (P[i]['r_v'] + sh[i]['price_pnl']) * tv / P[i]['days']))
    fit = income_vs_tvl(rows)
    dec = res['decomposition_out'] if res['decomposition_out'] else decompose(Po, sh[c:], [True] * len(Po))
    # trailing 365 days of the always-on shadow of the chosen hedge
    t_end = P[-1]['t1']
    last = [(p, s) for p, s in zip(P, sh) if p['t0'] >= t_end - 365 * DAY_MS]
    d365 = sum(p['days'] for p, _ in last)
    y365 = sum(p['r_v'] + s['price_pnl'] for p, s in last) / d365 * 365.0 if d365 else None
    f365 = sum(s['fund_pnl'] for _, s in last) / d365 * 365.0 if d365 else 0.0
    c365 = sum(s['cost'] for _, s in last) / d365 * 365.0 if d365 else 0.0
    cap365 = sum(s['capital'] for _, s in last) / len(last) if last else 1.0
    yout = dec['vault'] + dec['hedge_price'] if dec else None
    cap = {'tvl_now_usd': tvl_now, 'income_vs_tvl_test': fit,
           'vault_hedged_yield_test': yout, 'vault_hedged_yield_365d': y365, 'funding_365d': f365, 'cost_365d': c365,
           'capital_365d': cap365}
    y0 = min(v for v in (yout, y365) if v is not None) if (yout is not None or y365 is not None) else None
    cap['y0_used'] = y0
    if y0 is not None and tvl_now:
        def excess_at(X):
            return (y0 * tvl_now / (tvl_now + X) + f365 - c365) / cap365 - SSR_NOW
        cap['excess_now_at_0'] = excess_at(0.0)
        cap['excess_at'] = {str(X): excess_at(X) for X in (1e6, 2e6, 3e6, 5e6, 10e6, 25e6, 50e6, 100e6)}
        for tgt, key in ((0.02, 'deposit_for_2pp'), (0.0, 'deposit_for_0')):
            need = (tgt + SSR_NOW) * cap365 - f365 + c365
            cap[key] = (max(0.0, y0 * tvl_now / need - tvl_now) if need > 0 and y0 > 0 else (float('inf') if need <= 0 else 0.0))
    res['capacity'] = cap
    if extra:
        res.update(extra)
    return res


def by_year_sum(rows):
    out = {}
    for t, v in rows:
        y = utc(t).year
        out[y] = out.get(y, 0.0) + v
    return out


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if not str(k).startswith('_')}
    if isinstance(o, list):
        return [strip(v) for v in o]
    if isinstance(o, float):
        if math.isnan(o):
            return None
        if math.isinf(o):
            return 'inf' if o > 0 else '-inf'
        return round(o, 8)
    return o


def analyze_hlp(raw, book):
    hl = load_hlp(raw)
    assets = ['BTC', 'ETH', 'SOL']
    P = attach_legs(dietz_returns(hl['allTime']), book, assets)
    res = run_protocol('HLP', P, assets, entry_exit=ENTRY_EXIT['HLP'], roll_days=182, every_days=14, min_obs=8, warmup_days=0)
    tv = {p['t0']: p['tvl0'] for p in P}
    av_now = hl['allTime'][-1][1]
    # children decomposition by calendar year
    years = range(2023, 2027)
    kids = {}
    for name, k in hl['children'].items():
        pts = k['allTime']
        per = {}
        for y in years:
            a = day_ts('%d-01-01' % y) * 1000
            b = min(day_ts('%d-01-01' % (y + 1)) * 1000, pts[-1][0])
            if b > a:
                per[y] = interp_cum(pts, b) - interp_cum(pts, a)
        kids[name] = {'total_pnl': pts[-1][2], 'account_value_now': pts[-1][1], 'first': day_of(pts[0][0]), 'by_year': per}
    parent_by_year = {}
    for y in years:
        a = day_ts('%d-01-01' % y) * 1000
        b = min(day_ts('%d-01-01' % (y + 1)) * 1000, hl['allTime'][-1][0])
        parent_by_year[y] = interp_cum(hl['allTime'], b) - interp_cum(hl['allTime'], a)
    liq = sum(v['total_pnl'] for n, v in kids.items() if 'Liquidator' in n)
    mm = sum(v['total_pnl'] for n, v in kids.items() if 'Liquidator' not in n)
    # independent check 1: the week window's flows against the ledger (deposits/withdrawals into the parent only)
    chk = {}
    wk = hl['week']
    led = hl['ledger']
    if led and wk:
        dep = sum(float(r['usdc'] or 0) for r in led['rows'] if r['type'] == 'vaultDeposit' and (r['vault'] or '').lower() == HLP)
        wreq = sum(float(r['requestedUsd'] or 0) for r in led['rows'] if r['type'] == 'vaultWithdraw' and (r['vault'] or '').lower() == HLP)
        wnet = sum(float(r['netWithdrawnUsd'] or 0) for r in led['rows'] if r['type'] == 'vaultWithdraw' and (r['vault'] or '').lower() == HLP)
        implied = (wk[-1][1] - wk[0][1]) - (wk[-1][2] - wk[0][2])
        chk['week_flow_check'] = {'window': [utc(wk[0][0]).isoformat()[:16], utc(wk[-1][0]).isoformat()[:16]],
                                  'implied_flow_from_portfolio': implied, 'ledger_deposits': dep,
                                  'ledger_withdrawals_requested': wreq, 'ledger_withdrawals_net': wnet,
                                  'ledger_net_flow': dep - wnet, 'difference': implied - (dep - wnet),
                                  'difference_share_of_av': (implied - (dep - wnet)) / wk[0][1],
                                  'ledger_rows': len(led['rows'])}
    # check 2: parent P&L against the sum of the children over the last year
    a, b = hl['allTime'][-1][0] - 365 * DAY_MS, hl['allTime'][-1][0]
    par = interp_cum(hl['allTime'], b) - interp_cum(hl['allTime'], a)
    kid = sum(interp_cum(k['allTime'], b) - interp_cum(k['allTime'], a) for k in hl['children'].values())
    chk['children_sum_last_365d'] = {'parent_pnl': par, 'children_pnl': kid, 'children_share': kid / par if par else None}
    # check 3: modified Dietz against the simple return (flows mid-period vs at the start)
    PP = res['_series']['P']
    c = res['_series']['c']
    chk['dietz_vs_simple_test'] = {'dietz_ann': sum(p['r_v'] for p in PP[c:]) / sum(p['days'] for p in PP[c:]) * 365,
                                   'simple_ann': sum(p['r_simple'] for p in PP[c:]) / sum(p['days'] for p in PP[c:]) * 365}
    # recent detail: the month window (~10 h grid)
    mo = dietz_returns(hl['month'])
    mdays = sum(p['days'] for p in mo)
    recent = {'window': [day_of(hl['month'][0][0]), day_of(hl['month'][-1][0])], 'points': len(hl['month']),
              'median_gap_hours': statistics.median([p['days'] * 24 for p in mo]),
              'ann_return': sum(p['r_v'] for p in mo) / mdays * 365 if mdays else None,
              'worst_period': min(p['r_v'] for p in mo), 'best_period': max(p['r_v'] for p in mo),
              'account_value_now': av_now}
    extra = {'resolution': 'allTime grid: %d points, median gap %.1f days (7 days in 2023, 14 days since); month grid ~10 h '
                           'for the last 30 days only; a daily series does not exist in the public API'
                           % (len(hl['allTime']), statistics.median([p['days'] for p in PP])),
             'children': kids, 'parent_pnl_by_year': parent_by_year, 'liquidator_pnl_total': liq, 'mm_strategies_pnl_total': mm,
             'parent_total_pnl': hl['allTime'][-1][2], 'checks': chk, 'recent_month': recent,
             'vault_meta': {'apr_field': hl['parent'].get('apr'), 'leader_commission': hl['parent'].get('leaderCommission'),
                            'allow_deposits': hl['parent'].get('allowDeposits'), 'followers_count': hl['parent'].get('followers'),
                            'lockup_days': 4, 'snapshot': hl['snapshot']}}
    return finish(res, tvl_lookup(tv), av_now, extra, book=None)


def analyze_jlp(raw, book):
    j = load_jlp(raw)
    assets = ['SOL', 'ETH', 'BTC']
    info = j['info'] or {}
    comp = {}
    for cst in info.get('custodies', []):
        sym = {'SOL': 'SOL', 'ETH': 'ETH', 'WBTC': 'BTC'}.get(cst['symbol'])
        if sym:
            comp[sym] = float(cst['targetWeightagePct']) / 100.0
    P = attach_legs(price_returns(j['points']), book, assets)
    res = run_protocol('JLP', P, assets, comp=comp, entry_exit=ENTRY_EXIT['JLP'])
    # TVL (DefiLlama protocol TVL, i.e. JLP AUM) and the fee yield paid to LPs (75% of fees, DefiLlama supply side)
    prot = load_json(raw / 'llama' / 'protocol_jupiter-perpetual-exchange.json.gz')
    tv = {int(x['date']) * 1000: float(x['totalLiquidityUSD']) for x in prot['tvl']}
    fees = load_json(raw / 'llama' / 'fees_jupiter-perpetual-exchange_dailySupplySideRevenue.json')['totalDataChart']
    tvf = tvl_lookup(tv)
    fy = {}
    for t, v in fees:
        tvl = tvf(int(t) * 1000)
        if tvl:
            y = utc(t).year
            b = fy.setdefault(y, [0.0, 0])
            b[0] += v / tvl
            b[1] += 1
    fee_yield = {y: v[0] / v[1] * 365 for y, v in fy.items() if v[1] >= 30}
    S = res['_series']
    c = S['c']
    Po = S['P'][c:]
    sh = S['shadows'][res['chosen'].split('|')[0]][c:]
    t0, t1 = Po[0]['t0'], Po[-1]['t1']
    fy_test = [v / tvf(int(t) * 1000) for t, v in fees if t0 <= int(t) * 1000 < t1 and tvf(int(t) * 1000)]
    dec = {'fee_yield_by_year': fee_yield, 'fee_yield_test': sum(fy_test) / len(fy_test) * 365 if fy_test else None}
    dec['vault_hedged_test'] = (res['decomposition_out'] or {}).get('vault', 0) + (res['decomposition_out'] or {}).get('hedge_price', 0)
    dec['residual_test_trader_pnl_staking_hedge_error'] = (dec['vault_hedged_test'] - dec['fee_yield_test']) if dec['fee_yield_test'] else None
    sol = next((x for x in info.get('custodies', []) if x['symbol'] == 'SOL'), None)
    staking = {'sol_custody_usd': float(sol['aumUsdFormatted']) if sol else None,
               'sol_staked_usd': float(sol['totalStakedAmountUsdFormatted']) if sol else None,
               'aum_usd': float(info.get('aumUsdFormatted') or 0), 'aum_limit_usd': float(info.get('aumLimitUsdFormatted') or 0),
               'apr_field_pct': float(info.get('jlpAprPct') or 0), 'price_now': float(info.get('jlpPriceUsdFormatted') or 0),
               'target_weights': {x['symbol']: float(x['targetWeightagePct']) for x in info.get('custodies', [])},
               'current_weights': {x['symbol']: float(x['currentWeightagePct']) for x in info.get('custodies', [])},
               'utilization_pct': {x['symbol']: float(x['utilizationPct']) for x in info.get('custodies', [])}}
    # independent checks: CoinGecko against DefiLlama over the overlap; jlp-info price against the last DefiLlama point
    chk = {}
    cg = j['coingecko'] or []
    if cg:
        # match each CoinGecko point (00:00 UTC) to the nearest DefiLlama point within 3 hours (DefiLlama stamps ~22:00;
        # matching by calendar day pairs prices 22 hours apart, which is how this check first read a 0.04 correlation)
        import bisect
        lt = [t for t, _ in j['points']]
        pairs = []
        for t, pc in cg:
            k = bisect.bisect_left(lt, t)
            cand = [x for x in (k - 1, k) if 0 <= x < len(lt)]
            if not cand:
                continue
            x = min(cand, key=lambda q: abs(lt[q] - t))
            if abs(lt[x] - t) <= 3 * H_MS:
                pairs.append((j['points'][x][1], pc, abs(lt[x] - t) / H_MS))
        rl = [b2[0] / a2[0] - 1 for a2, b2 in zip(pairs, pairs[1:])]
        rc = [b2[1] / a2[1] - 1 for a2, b2 in zip(pairs, pairs[1:])]
        mx, my = sum(rl) / len(rl), sum(rc) / len(rc)
        cov = sum((x - mx) * (y - my) for x, y in zip(rl, rc))
        vx, vy = sum((x - mx) ** 2 for x in rl), sum((y - my) ** 2 for y in rc)
        chk['coingecko_vs_defillama'] = {'matched_points': len(pairs), 'median_gap_hours': statistics.median(p_[2] for p_ in pairs),
                                         'daily_return_corr': cov / math.sqrt(vx * vy) if vx and vy else None,
                                         'total_return_defillama': pairs[-1][0] / pairs[0][0] - 1,
                                         'total_return_coingecko': pairs[-1][1] / pairs[0][1] - 1,
                                         'median_abs_level_gap': statistics.median(abs(a2 / b2 - 1) for a2, b2, _ in pairs)}
        # regression residual of each path on the hedge assets at its own stamps: how much timing noise each carries
        for label, pts in (('defillama', [(t, p) for t, p in j['points'] if t >= cg[0][0] - DAY_MS]), ('coingecko', list(cg))):
            PP = attach_legs(price_returns(pts, drop_stale=False), book, assets)
            fit = ols([q['r_v'] for q in PP], [[q['r'][a_] for a_ in assets] for q in PP])
            if fit:
                res_sd = statistics.pstdev([q['r_v'] - fit['alpha'] - sum(b_ * q['r'][a_] for b_, a_ in zip(fit['betas'], assets)) for q in PP])
                chk['coingecko_vs_defillama']['fit_' + label] = {'r2': fit['r2'], 'resid_sd_daily': res_sd,
                                                                 'alpha_ann': fit['alpha'] * 365,
                                                                 'betas': dict(zip(assets, fit['betas']))}
        # the headline re-computed through the other price path: the chosen hedge, always on, over CoinGecko's window;
        # each path fits its own trailing betas (DefiLlama history before the window feeds the CoinGecko path's warm-up)
        hn = res['chosen'].split('|')[0]
        cg_t0 = cg[0][0]
        Pc_all = attach_legs(price_returns([(t, p) for t, p in j['points'] if t < cg_t0] + list(cg)), book, assets)

        def betas_for(PP):
            if hn.startswith('roll'):
                return rolling_betas(PP, assets, int(hn[4:]), 7, 20)
            b0 = res['static_betas_in_sample'] if hn == 'static' else (comp if hn == 'comp' else {})
            return [b0] * len(PP)
        two = {'hedge': hn}
        for label, PP in (('defillama', P), ('coingecko', Pc_all)):
            bb = betas_for(PP)
            i0 = next(i for i, p in enumerate(PP) if p['t0'] >= cg_t0 + DAY_MS - H_MS)
            sim = simulate_hedge(PP[i0:], bb[i0:])
            dd = sum(p['days'] for p in PP[i0:])
            two[label] = {'excess_ann': sum(s_['ret'] - p['s'] for s_, p in zip(sim, PP[i0:])) / dd * 365,
                          'days': round(dd, 1), 'start': day_of(PP[i0]['t0']), 'end': day_of(PP[-1]['t1']), 'periods': len(PP) - i0}
        chk['headline_two_paths'] = two
    if j['points'] and info:
        chk['jlp_info_vs_last_defillama'] = {'jlp_info_price': float(info.get('jlpPriceUsdFormatted') or 0),
                                             'defillama_last': j['points'][-1][1], 'defillama_last_day': day_of(j['points'][-1][0])}
    chk['lagged_beta_SOL'] = lagged_beta(S['P'], 'SOL')
    # the fee level now, two ways: DefiLlama's last 30 days of supply-side revenue over AUM, and the venue's APR field
    last30 = [v for t, v in fees if int(t) * 1000 >= (int(fees[-1][0]) - 29 * 86400) * 1000]
    if last30 and staking['aum_usd']:
        chk['fee_yield_30d_vs_venue_apr'] = {'defillama_30d_supply_side_usd': sum(last30), 'days': len(last30),
                                             'annualised_over_aum': sum(last30) / len(last30) * 365 / staking['aum_usd'],
                                             'venue_apr': staking['apr_field_pct'] / 100.0}
    extra = {'decomposition_fees': dec, 'pool_state_now': staking, 'checks': chk,
             'resolution': 'daily (DefiLlama coins chart, one point a day at varying times, 2-decimal prices until mid-2025)'}
    res['robustness'] = {'coingecko_daily_window': chk.get('headline_two_paths', {}).get('coingecko'),
                         'defillama_daily_same_window': chk.get('headline_two_paths', {}).get('defillama')}
    for k in ('coingecko_daily_window', 'defillama_daily_same_window'):
        if res['robustness'][k]:
            res['robustness'][k]['ann_excess'] = res['robustness'][k]['excess_ann']
    return finish(res, tvf, staking['aum_usd'], extra, book=book)


def analyze_gmx(raw, book, name):
    m = GMX_TOKENS[name]
    g = load_gmx(raw, name)
    assets = [m['asset']]
    comp = {m['asset']: 1.0} if m['kind'] == 'single-token' else None
    P = attach_legs(price_returns(g['points']), book, assets)
    res = run_protocol(name, P, assets, comp=comp, entry_exit=ENTRY_EXIT['GLV' if m['type'] == 'glv' else 'GM'])
    tvf = tvl_lookup(g['tvl'])
    S = res['_series']
    c = S['c']
    t0, t1 = S['P'][c]['t0'], S['P'][-1]['t1']
    fee = [(int(r['snapshotTimestamp']) * 1000, int(r['aprByFee']) / 1e30, int(r['aprByBorrowingFee']) / 1e30) for r in g['apr']['fee']]
    pnl = [(int(r['snapshotTimestamp']) * 1000, int(r['apr']) / 1e30) for r in g['apr']['pnl']]
    ft = [x for x in fee if t0 <= x[0] < t1]
    pt = [x for x in pnl if t0 <= x[0] < t1]
    dec = {'apr_by_fee_test': sum(x[1] for x in ft) / len(ft) if ft else None,
           'apr_by_borrowing_fee_test': sum(x[2] for x in ft) / len(ft) if ft else None,
           'apr_trader_pnl_test': sum(x[1] for x in pt) / len(pt) if pt else None,
           'note': 'squid aprSnapshots / pnlAprSnapshots (daily, as a fraction a year); aprByFee includes the borrowing part'}
    dec['vault_hedged_test'] = (res['decomposition_out'] or {}).get('vault', 0) + (res['decomposition_out'] or {}).get('hedge_price', 0)
    chk = {'lagged_beta': lagged_beta(S['P'], m['asset'])}
    mi = raw / 'gmx' / ('squid_marketinfos_%s.json' % today())
    mis = sorted((raw / 'gmx').glob('squid_marketinfos_*.json'))
    if mis and m['type'] == 'gm':
        x = load_json(mis[-1]).get(name)
        if x and x.get('x') and x.get('p'):
            info = x['x'][0]
            pv = int(info['poolValue']) / 1e30
            sup = int(info['marketTokenSupply']) / 1e18
            px = (int(x['p'][0]['minPrice']) + int(x['p'][0]['maxPrice'])) / 2e30
            chk['price_vs_poolvalue_over_supply'] = {'pool_value_usd': pv, 'supply': sup, 'pv_over_supply': pv / sup if sup else None,
                                                     'squid_price_latest': px, 'gap': (pv / sup / px - 1) if sup and px else None,
                                                     'long_oi_usd': int(info['longOpenInterestUsd']) / 1e30,
                                                     'short_oi_usd': int(info['shortOpenInterestUsd']) / 1e30}
    del mi
    tvl_now = g['tvl'][max(g['tvl'])] if g['tvl'] else None
    return finish(res, tvf, tvl_now, {'decomposition_fees': dec, 'checks': chk, 'kind': m['kind'], 'address': m['address'],
                                      'resolution': 'daily squid snapshots at 00:00 UTC (price stamped at the snapshot)'}, book=book)


def analyze_gains(raw, book, name):
    g = load_gains(raw, name)
    if not g or len(g['points']) < 200:
        return None
    assets = ['BTC']
    P = attach_legs(price_returns(g['points']), book, assets)
    res = run_protocol(name, P, assets, entry_exit=ENTRY_EXIT['gToken'])
    tvf = tvl_lookup(g['tvl'])
    ex = g['extra']
    ks = sorted(ex)
    S = res['_series']
    c = S['c']
    t0, t1 = S['P'][c]['t0'], S['P'][-1]['t1']
    a = [k for k in ks if t0 <= k <= t1]
    dec = {}
    if a:
        e0, e1 = ex[a[0]], ex[a[-1]]
        yrs = (a[-1] - a[0]) / DAY_MS / 365.0
        dec = {'acc_rewards_per_token_change': e1['accRewardsPerToken'] - e0['accRewardsPerToken'],
               'acc_pnl_per_token_change': e1['accPnlPerToken'] - e0['accPnlPerToken'],
               'years': yrs, 'note': 'accRewardsPerToken = fees credited per share; accPnlPerToken > 0 = traders net winning'}
    # checks: share price against assets/supply; DefiLlama APY against our trailing 30-day share-price return
    ratio = [(k, ex[k]['totalAssets'] / ex[k]['totalSupply']) for k in ks if ex[k]['totalAssets'] and ex[k]['totalSupply']]
    px = dict(g['points'])
    gaps = [r / px[k] - 1 for k, r in ratio if k in px]
    chk = {'assets_over_supply_vs_share_price': {'n': len(gaps), 'median_gap': statistics.median(gaps) if gaps else None,
                                                  'max_abs_gap': max(abs(x) for x in gaps) if gaps else None,
                                                  'last_gap': gaps[-1] if gaps else None}}
    yc = raw / 'llama' / 'yield_chart_gains_usdc_arbitrum.json'
    if yc.exists() and name == 'gUSDC_arbitrum':
        rows = load_json(yc).get('data', [])
        apy = {r['timestamp'][:10]: r['apy'] for r in rows if r.get('apy') is not None}
        pts = dict((day_of(t), p) for t, p in g['points'])
        diffs = []
        for d in sorted(apy):
            d0 = (dt.datetime.strptime(d, '%Y-%m-%d') - dt.timedelta(days=30)).strftime('%Y-%m-%d')
            if d in pts and d0 in pts:
                ours = (pts[d] / pts[d0] - 1) * 365 / 30 * 100
                diffs.append((ours, apy[d]))
        if diffs:
            mx = sum(x for x, _ in diffs) / len(diffs)
            my = sum(y for _, y in diffs) / len(diffs)
            cov = sum((x - mx) * (y - my) for x, y in diffs)
            vx = sum((x - mx) ** 2 for x, _ in diffs)
            vy = sum((y - my) ** 2 for _, y in diffs)
            chk['defillama_apy_vs_trailing30d'] = {'n': len(diffs), 'mean_ours_pct': mx, 'mean_defillama_pct': my,
                                                   'corr': cov / math.sqrt(vx * vy) if vx and vy else None}
    last = ex[ks[-1]]
    eps = [(k, ex[k]['currentEpoch']) for k in ks if ex[k].get('currentEpoch')]
    epoch_days = None
    if len(eps) > 30 and eps[-1][1] > eps[0][1]:
        epoch_days = (eps[-1][0] - eps[0][0]) / DAY_MS / (eps[-1][1] - eps[0][1])
    tl = last.get('withdrawEpochsTimelock')
    meta = {'withdraw_epochs_timelock_now': tl, 'collateralization_p_now': last.get('collateralizationP'),
            'current_epoch_now': last.get('currentEpoch'), 'first_day': day_of(g['points'][0][0]),
            'epoch_days_measured': epoch_days,
            'withdrawal_wait_days_now': (tl * epoch_days) if (tl and epoch_days) else None,
            'withdrawal_wait_cost_at_ssr': (tl * epoch_days * SSR_NOW / 365) if (tl and epoch_days) else None}
    return finish(res, tvf, g['tvl'][max(g['tvl'])] if g['tvl'] else None,
                  {'decomposition_fees': dec, 'checks': chk, 'vault_meta': meta, 'resolution': 'daily share price at the last block before 00:00 UTC'},
                  book=book)


def analyze_lighter(raw, book):
    L = load_lighter(raw)
    if not L:
        return None
    assets = ['BTC', 'ETH', 'SOL']
    # primary: the share price (pool value / pool shares at 00:00 UTC), flow-free by construction. LLP churns large
    # internal flows ($4B cumulative inflow on an $83M pool), which breaks Dietz's mid-period-flow assumption.
    P = attach_legs(price_returns(L['share_points'], drop_stale=False), book, assets)
    res = run_protocol('LLP', P, assets, entry_exit=0.0)
    tv = {t: v for t, v, _ in L['points']}
    D = dietz_returns(L['points'])
    # check: our flow-adjusted daily return against the official pool_info daily returns (stamped 21:00 UTC)
    off = L['official']
    od = {}
    for t, r in off:
        od[day_of(t + 3 * H_MS)] = r          # the 21:00 stamp closes the UTC day that starts 3 hours later? matched both ways below
    ours = {day_of(p['t1']): p['r_v'] for p in P}   # share-price returns
    best = None
    for shift in (-1, 0, 1):
        pairs = []
        for d, r in ours.items():
            dd = (dt.datetime.strptime(d, '%Y-%m-%d') + dt.timedelta(days=shift)).strftime('%Y-%m-%d')
            if dd in od:
                pairs.append((r, od[dd]))
        if len(pairs) > 30:
            mx = sum(x for x, _ in pairs) / len(pairs)
            my = sum(y for _, y in pairs) / len(pairs)
            cov = sum((x - mx) * (y - my) for x, y in pairs)
            vx = sum((x - mx) ** 2 for x, _ in pairs)
            vy = sum((y - my) ** 2 for _, y in pairs)
            cr = cov / math.sqrt(vx * vy) if vx and vy else None
            if best is None or (cr or -1) > (best['corr'] or -1):
                best = {'shift_days': shift, 'n': len(pairs), 'corr': cr, 'sum_ours': sum(x for x, _ in pairs),
                        'sum_official': sum(y for _, y in pairs)}
    ts0 = res['_series']['P'][res['_series']['c']]['t0']

    def comp(rs):
        g = 1.0
        for r in rs:
            g *= 1.0 + r
        return g - 1.0
    sp = [x for x in L['share_points'] if x[0] >= ts0]
    chk = {'official_daily_returns_vs_share_price': best, 'official_apy_pct': L['apy_official'],
           'test_window_total_return': {'from': day_of(ts0), 'share_price': sp[-1][1] / sp[0][1] - 1 if len(sp) > 1 else None,
                                        'official_daily_returns': comp([r for t, r in L['official'] if t >= ts0]),
                                        'dietz_from_flows': comp([p['r_v'] for p in D if p['t0'] >= ts0])}}
    # robustness: the venue's own daily returns (stamped 21:00 UTC; taken as the 24 h ending at the stamp), unhedged
    # (LLP's betas are ~0), test window only
    op = [{'t0': t - DAY_MS, 't1': t, 'days': 1.0, 'r_v': r} for t, r in L['official'] if t - DAY_MS >= ts0]
    if len(op) > 30:
        xs = [p['r_v'] - savings_between(p['t0'], p['t1']) for p in op]
        res.setdefault('robustness', {})['official_daily_returns_unhedged'] = seg_stats(op, xs)
    meta = {'operator_fee': L['operator_fee'], 'positions_now': L['positions'], 'tvl_now': L['tvl_now']}
    return finish(res, tvl_lookup(tv), L['tvl_now'], {'checks': chk, 'vault_meta': meta,
                                                       'resolution': 'daily cumulative P&L and flows at 00:00 UTC'}, book=book)


def analyze_dydx(raw):
    d = load_dydx(raw)
    if not d:
        return None
    pts = d['points']
    R = dietz_returns(pts)
    days = sum(p['days'] for p in R)
    tr = d['transfers']
    flows = sum(x[3] for x in tr[1:])
    chk = {'pnl_vs_equity_minus_transfers': {'dpnl': tr[-1][2] - tr[0][2], 'dequity': tr[-1][1] - tr[0][1],
                                             'net_transfers_reported': flows,
                                             'gap': (tr[-1][1] - tr[0][1]) - (tr[-1][2] - tr[0][2]) - flows}}
    sv = sum(savings_between(p['t0'], p['t1']) for p in R)
    return {'name': 'dYdX MegaVault', 'window': [day_of(pts[0][0]), day_of(pts[-1][0])], 'points': len(pts),
            'ann_return': sum(p['r_v'] for p in R) / days * 365 if days else None,
            'ann_excess_over_savings': (sum(p['r_v'] for p in R) - sv) / days * 365 if days else None,
            'equity_now': pts[-1][1], 'total_pnl_all_time': pts[-1][2], 'checks': chk,
            'verdict': 'no-go (capacity)', 'why': 'the indexer serves 90 days only (no out-of-sample test possible) and the '
                                                  'vault holds $%.2fM; at that size the question of an edge is moot' % (pts[-1][1] / 1e6)}


def weekly_check(points, book, assets, test_start_ms, step=7, roll_days=120, min_obs=12):
    """Robustness, fixed in advance and never used for selection: resample the price path to every `step`-th point,
    hedge with trailing `roll_days` OLS betas (no look-ahead), always on, and report the test window."""
    pts = sorted(points)
    grid = pts[::step]
    P = attach_legs(price_returns(grid, drop_stale=False), book, assets)
    bb = rolling_betas(P, assets, roll_days, 7, min_obs)
    idx = [i for i, p in enumerate(P) if p['t0'] >= test_start_ms]
    if len(idx) < 8:
        return None
    i0 = idx[0]
    sim = simulate_hedge(P[i0:], bb[i0:])
    xs = [s_['ret'] - p['s'] for s_, p in zip(sim, P[i0:])]
    st = seg_stats(P[i0:], xs)
    st['grid_step'] = step
    st['roll_days'] = roll_days
    st['mean_gross_hedge'] = sum(s_['gross'] for s_ in sim) / len(sim)
    return st


def verdict(res):
    """go: >= +2pp a year over the savings rate in the test half, NW t >= 2, survives BH across vaults, room for >= $1M
    at +2pp, and every robustness re-measurement >= +2pp. watch: positive with t >= 1.5, or significant but too small or
    not robust. no-go otherwise."""
    o = res['chosen_out']
    cap = res.get('capacity') or {}
    x, t = o.get('ann_excess') or 0.0, o.get('nw_t') or 0.0
    dep2 = cap.get('deposit_for_2pp') or 0.0
    rob = [r.get('ann_excess') for r in (res.get('robustness') or {}).values() if isinstance(r, dict) and r.get('ann_excess') is not None]
    res['robustness_min'] = min(rob) if rob else None
    bh_ok = (res.get('bh_across_vaults') or {}).get('reject_q10', False)
    if x >= 0.02 and t >= 2.0 and bh_ok and dep2 >= 1e6 and all(r >= 0.02 for r in rob):
        return 'go'
    if x > 0 and t >= 1.5:
        return 'watch'
    return 'no-go'


def cmd_analyze(args):
    out = Path(args.out)
    raw = out / 'raw'
    book = PriceBook(raw)
    A = {'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'as_of': today(),
         'benchmark': {'ssr_now': SSR_NOW, 'savings_by_year': SAVINGS_BY_YEAR,
                       'note': 'history: the savings rate actually paid that calendar year (DSR, then SSR), pro rata by day'},
         'cost_model': {'hedge_fee_one_way': HEDGE_FEE, 'margin_per_unit_short': MARGIN, 'rebalance_band': REBAL_BAND,
                        'vault_round_trip': ENTRY_EXIT, 'hedge_venue': 'Binance USDT-margined perps (1h closes, funding)'},
         'protocol': {'split': 'first half of each vault\'s periods (after a 60-day warm-up) to choose, second half to test once',
                      'rules': {k: v for k, v in RULES.items()}, 'hedges': ['none', 'static (OLS on the choose half)',
                      'roll60 (trailing 60-day OLS, refit weekly; HLP: 182 days on its 14-day grid)',
                      'comp (composition: current JLP target weights; 1.0 for single-token GM pools)'],
                      'selection': 'highest choose-half Sharpe of the excess series (backtest.choose_then_test)',
                      'stats': 'Newey-West t with ~30 days of lags; circular block bootstrap with 30-day blocks; BH across vaults'},
         'vaults': {}, 'skipped': {}, 'errors_found': ERRORS_FOUND}
    runs = {}
    for key, fn in (('HLP', lambda: analyze_hlp(raw, book)), ('JLP', lambda: analyze_jlp(raw, book)),
                    ('LLP', lambda: analyze_lighter(raw, book))):
        try:
            r = fn()
            if r:
                runs[key] = r
        except Exception as e:  # noqa: BLE001
            A['skipped'][key] = 'analysis failed: %s' % str(e)[:200]
            raise
    for name in GMX_TOKENS:
        runs[name] = analyze_gmx(raw, book, name)
    for name in GAINS:
        r = analyze_gains(raw, book, name)
        if r:
            runs[name] = r
        else:
            A['skipped'][name] = 'share-price history not collected or under 200 days'
    dy = analyze_dydx(raw)
    if dy:
        A['dydx_megavault'] = dy
    # BH across the vaults' chosen test-half p-values
    names = list(runs)
    rej, adj = B.bh([runs[n]['chosen_out'].get('nw_p') for n in names], q=0.10)
    for n, r_, a_ in zip(names, rej, adj):
        runs[n]['bh_across_vaults'] = {'reject_q10': r_, 'adjusted_p': a_}
        runs[n]['verdict'] = verdict(runs[n])
    for n in names:
        A['vaults'][n] = strip(runs[n])
    A['skipped'].update(skipped_venues(raw))
    # hedge-leg depth: Binance 30-day average daily quote volume
    A['hedge_depth'] = {a: book.daily_quote_volume(a) for a in HEDGE_SYMBOLS}
    A['verdict_table'] = [{'vault': n, 'chosen': runs[n]['chosen'], 'in': runs[n]['chosen_in'].get('ann_excess'),
                           'in_t': runs[n]['chosen_in'].get('nw_t'), 'out': runs[n]['chosen_out'].get('ann_excess'),
                           'out_t': runs[n]['chosen_out'].get('nw_t'), 'verdict': runs[n]['verdict']} for n in names]
    save_json(out / 'analysis.json', strip(A))
    print(json.dumps(strip(A['verdict_table']), indent=0)[:3000])


ERRORS_FOUND = [
    'collect hlp: `d / "vault_%s.json.gz" % HLP` divided before formatting (TypeError); fixed with parentheses; the first '
    'background run recorded the part as failed, the snapshot was re-collected by a separate run',
    'manifest race: two collect processes rewrote one manifest file; manifests are now one file per part',
    'gains loader divided gUSDC totalSupply by 1e18; gToken shares carry the asset\'s 6 decimals',
    'GMX squid collectedFeesInfos has no "1d" period (only "1h"/"total"): fees1d files are empty; the fee decomposition '
    'uses the daily aprSnapshots instead',
    'Arbitrum block lookup by bisection cost ~25 calls a day; replaced by interpolation between 4M-block anchors plus a '
    'local-rate correction (blocks land within 10 minutes before midnight)',
    'JLP source check first matched CoinGecko (00:00 UTC) and DefiLlama (~22:00 UTC) by calendar day, pairing prices 22 '
    'hours apart: daily-return correlation 0.04. Nearest-timestamp matching (median 1.75 h apart) gives 0.91',
    'LLP first used modified Dietz on value = inflow - outflow + trade P&L; the pool churns $4B of internal flows on $83M, '
    'so the mid-period-flow assumption failed (test-half total +3.9% vs +5.7% from value/shares); the share price is primary',
    'the verdict rule first called any positive vault with under $1M of room "watch" whatever its t; now watch needs t >= 1.5',
    'the robustness grid (120-day hedge window) was added after JLP\'s 60-day and 120-day windows disagreed; it is applied '
    'to every daily vault and never used for selection, but it was not pre-registered',
]


def skipped_venues(raw):
    out = {}
    pr = raw / 'probes' / 'probes.json'
    rows = load_json(pr) if pr.exists() else []
    st = {}
    for r in rows:
        st.setdefault(r['venue'], []).append('%s: %s' % (r['what'], 'ok' if r.get('ok') else r.get('error')))
    out['Ostium OLP'] = 'no public share-price history found (documented metadata endpoint 404); an archive-node read of the ' \
                        'OLP vault was not attempted for lack of a verified vault address. Probes: %s' % '; '.join(st.get('Ostium OLP', []))
    out['Avantis'] = 'no public vault-history endpoint (404); tranche share prices would need Base archive reads of unverified ' \
                     'addresses. Probes: %s' % '; '.join(st.get('Avantis vaults', []))
    out['Aster ALP'] = 'ALP endpoint 404; BNB-chain archive reads not attempted. Probes: %s' % '; '.join(st.get('Aster ALP', []))
    out['Drift insurance fund'] = 'data API host did not resolve; the insurance fund is a backstop, not the traders\' counterparty. ' \
                                  'Probes: %s' % '; '.join(st.get('Drift insurance fund', []))
    out['edgeX'] = 'metadata endpoint 503. Probes: %s' % '; '.join(st.get('edgeX vault', []))
    p2 = raw / 'probes' / 'probes_round2.json'
    out['Extended vault'] = 'summary only (equity ~$64M, last-30-day APR 9.36% on 2026-10-10); no history endpoint (404)'
    out['Paradex'] = 'the public vault list holds curated strategy vaults (largest $2.6M, a multi-strategy fund), no protocol ' \
                     'house vault with history'
    del p2
    return out


# ----------------------------------------------------------------------------------------------------------------------
# render: tables.md and manifest.json from analysis.json and the raw cache
# ----------------------------------------------------------------------------------------------------------------------
def pct(x, d=1, sign=True):
    if x is None or isinstance(x, str):
        return '—' if x is None else x
    return ('%+.*f%%' if sign else '%.*f%%') % (d, 100 * x)


def num(x, d=2):
    return '—' if x is None else ('%.*f' % (d, x))


def usd(x):
    if x is None:
        return '—'
    if isinstance(x, str):
        return x
    a = abs(x)
    if a >= 1e9:
        return '$%.2fB' % (x / 1e9)
    if a >= 1e6:
        return '$%.1fM' % (x / 1e6)
    if a >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def build_manifest(out):
    raw = out / 'raw'
    files = []
    for f in sorted(raw.rglob('*')):
        if not f.is_file() or f.name.endswith('.tmp'):
            continue
        rec = {'path': str(f.relative_to(out)), 'bytes': f.stat().st_size}
        try:
            if f.suffix in ('.json', '.gz') and f.name != 'pools.json.gz':
                o = load_json(f)
                if isinstance(o, list):
                    rec['rows'] = len(o)
                elif isinstance(o, dict):
                    for k in ('prices', 'megavaultPnl', 'pnl', 'totalDataChart', 'data', 'rows', 'tvl', 'vaultsPnl'):
                        if isinstance(o.get(k), list):
                            rec['rows'] = len(o[k])
                            break
                    if 'coins' in o:
                        rec['rows'] = sum(len(v.get('prices', [])) for v in o['coins'].values())
                    if 'portfolio' in o:
                        rec['rows'] = {w: len(p['pnlHistory']) for w, p in o['portfolio']}
                    if f.parent.name == 'gains' and f.name.startswith('gUSDC'):
                        rec['rows'] = len(o)
        except Exception as e:  # noqa: BLE001
            rec['parse_error'] = str(e)[:80]
        files.append(rec)
    parts = {}
    for m in sorted(raw.glob('manifest_*.json')):
        parts[m.stem.replace('manifest_', '')] = load_json(m)
    A = load_json(out / 'analysis.json') if (out / 'analysis.json').exists() else {}
    ranges = {n: {'choose': v.get('in_sample'), 'test': v.get('test'), 'periods': v.get('n_periods'),
                  'median_period_days': v.get('median_period_days')} for n, v in (A.get('vaults') or {}).items()}
    man = {
        'study': 'house_vaults', 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'script': 'scripts/house_vaults.py (collect / analyze / render)',
        'sources': {
            'hyperliquid': 'POST https://api.hyperliquid.xyz/info vaultDetails (HLP parent + 7 children), '
                           'userNonFundingLedgerUpdates (HLP, last 7 days, addresses stripped); >= 1.5 s a call',
            'binance': 'https://fapi.binance.com/fapi/v1/klines (1h) and /fapi/v1/fundingRate for BTC/ETH/SOL/HYPE USDT perps',
            'jupiter': 'https://perps-api.jup.ag/v1/jlp-info (snapshot); JLP mint %s verified against getTokenSupply' % JLP_MINT,
            'defillama': 'coins.llama.fi/chart/solana:<JLP mint> (daily price), api.llama.fi/summary/fees (supply-side revenue), '
                         'api.llama.fi/protocol/jupiter-perpetual-exchange (TVL), yields.llama.fi/pools and /chart/<pool>',
            'coingecko': 'api.coingecko.com coins/jupiter-perpetuals-liquidity-provider-token/market_chart?days=365 (check path)',
            'gmx': 'GraphQL %s: prices (type gm/glv, daily snapshots), aprSnapshots, pnlAprSnapshots, cumulativePoolValues, '
                   'marketInfos; %s/markets/info and /glvs/info' % (GMX_SQUID, GMX_API),
            'gains': 'Infura Arbitrum archive eth_call at the last block before each 00:00 UTC: shareToAssetsPrice, totalAssets, '
                     'totalSupply, accPnlPerToken, accRewardsPerToken, collateralizationP, currentEpoch, withdrawEpochsTimelock '
                     '(gUSDC %s)' % GAINS['gUSDC_arbitrum']['address'],
            'lighter': '%s/account?by=index&value=%d (pool_info.daily_returns) and /pnl?resolution=1d (cumulative P&L and flows)'
                       % (LIGHTER, LLP_INDEX),
            'dydx': '%s/vault/v1/megavault/historicalPnl (day, hour), /vault/v1/vaults/historicalPnl, /megavault/positions' % DYDX,
        },
        'ranges': ranges,
        'gaps': [
            'HLP: no daily history in the public API; allTime is a 7-14 day grid (100 points), month a ~10 h grid for 30 days',
            'dYdX MegaVault: indexer serves 90 days (daily) and 7 days (hourly) only',
            'JLP: DefiLlama prices carry 2 decimals until mid-2025 (rounding noise in the choose half); no composition history',
            'GMX: squid collectedFeesInfos has no 1d period (fees from aprSnapshots instead); GM deposit caps not collected',
            'Gains: only Arbitrum gUSDC read on chain (Base/Polygon gUSDC and gETH are smaller: $0.6M, $0.25M, $0.55M TVL)',
            'Lighter: publicPools 403; account and pnl endpoints used',
            'Ostium, Avantis, Aster, edgeX, Drift: no working public history endpoint (see analysis.json skipped)',
            'Extended: current summary only; Paradex: no protocol house vault in the public list',
        ],
        'collect_parts': parts,
        'files': files,
    }
    save_json(out / 'manifest.json', man)
    return man


def cmd_render(args):
    out = Path(args.out)
    A = load_json(out / 'analysis.json')
    V = A['vaults']
    L = []
    w = L.append
    w('# house_vaults — tables (generated by `scripts/house_vaults.py render` from analysis.json, %s)' % A['as_of'])
    w('')
    w('Excess = hedged return on capital (vault + short-perp hedge + funding − fees, capital = vault + 1/3 of the short '
      'notional) minus the savings rate actually paid. Choose half → test half per vault; t = Newey–West, ~30-day lags.')
    w('')
    w('## 1. Verdicts')
    w('')
    w('| vault | chosen (hedge \\| rule) | choose half | excess (t) | test half | excess (t) | boot 95% | max DD | worst week | '
      'best 1%% share | TVL now | deposit to +2pp | verdict |')
    w('|---|---|---|---:|---|---:|---|---:|---:|---:|---:|---:|---|')
    for n, v in V.items():
        i, o, cp = v['chosen_in'], v['chosen_out'], v.get('capacity') or {}
        w('| %s | %s | %s → %s | %s (%s) | %s → %s | %s (%s) | %s … %s | %s | %s | %s | %s | %s | **%s** |' % (
            n, v['chosen'], v['in_sample'][0], v['in_sample'][1], pct(i.get('ann_excess')), num(i.get('nw_t')),
            v['test'][0], v['test'][1], pct(o.get('ann_excess')), num(o.get('nw_t')), pct(o.get('boot_lo')), pct(o.get('boot_hi')),
            pct(o.get('max_drawdown'), 1, False), pct(o.get('worst_week')), num(o.get('best1pct_share')),
            usd(cp.get('tvl_now_usd')), usd(cp.get('deposit_for_2pp')), v.get('verdict')))
    if A.get('dydx_megavault'):
        d = A['dydx_megavault']
        w('| dYdX MegaVault | — (90 days only) | — | — | %s → %s | %s raw, %s over savings | — | — | — | — | %s | — | **%s** |' % (
            d['window'][0], d['window'][1], pct(d['ann_return']), pct(d['ann_excess_over_savings']), usd(d['equity_now']), d['verdict']))
    w('')
    w('## 2. Every pre-committed variant (choose half → test half)')
    w('')
    for n, v in V.items():
        w('**%s** (plan hash %s; static betas %s; latest rolling betas %s; DSR of the choice %s; test-half rank %s of %s)' % (
            n, v['plan_sha256_16'], {k: round(b, 3) for k, b in (v.get('static_betas_in_sample') or {}).items()},
            {k: round(b, 3) for k, b in (v.get('last_rolling_betas') or {}).items()}, num(v.get('deflated_sharpe_in_sample'), 3),
            v.get('oos_rank'), v.get('n_variants')))
        w('')
        w('| variant | choose: excess | t | test: excess | t | max DD | worst week | time on |')
        w('|---|---:|---:|---:|---:|---:|---:|---:|')
        for k, x in v['variants'].items():
            w('| %s%s | %s | %s | %s | %s | %s | %s | %s |' % (k, ' ←' if k == v['chosen'] else '', pct(x['in'].get('ann_excess')),
                                                         num(x['in'].get('nw_t')), pct(x['out'].get('ann_excess')), num(x['out'].get('nw_t')),
                                                         pct(x['out'].get('max_drawdown'), 1, False), pct(x['out'].get('worst_week')),
                                                         pct(x.get('on_share_out'), 0, False)))
        w('')
    w('## 3. By calendar year (annualised; raw = unhedged vault return)')
    w('')
    w('| vault | year | raw | chosen excess | static, always | unhedged excess | savings |')
    w('|---|---|---:|---:|---:|---:|---:|')
    for n, v in V.items():
        for y, b in sorted(v['by_year'].items()):
            w('| %s | %s | %s | %s | %s | %s | %s |' % (n, y, pct(b.get('raw_ann')), pct(b.get('chosen_ann')), pct(b.get('static_always_ann')),
                                                  pct(b.get('none_always_ann')), pct(b.get('s_ann'))))
    w('')
    w('## 4. Where the test-half return came from (chosen hedge, while on; a year, per unit of vault value)')
    w('')
    w('| vault | vault return | hedge price P&L | funding to the short | rebalance fees (cost) | savings (benchmark) | mean capital | gross hedge |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|')
    for n, v in V.items():
        d = v.get('decomposition_out') or {}
        w('| %s | %s | %s | %s | %s | %s | %s | %s |' % (n, pct(d.get('vault')), pct(d.get('hedge_price')), pct(d.get('hedge_funding'), 2),
                                                    pct(d.get('rebalance_cost'), 2, False), pct(d.get('savings'), 1, False), num(d.get('mean_capital')),
                                                    num(d.get('mean_gross_hedge'))))
    w('')
    if 'HLP' in V:
        h = V['HLP']
        w('## 5. HLP: who earned it (child vaults, P&L by calendar year)')
        w('')
        yrs = sorted({y for k in h['children'].values() for y in k['by_year']})
        w('| child | since | ' + ' | '.join(str(y) for y in yrs) + ' | total | account value |')
        w('|---|---|' + '---:|' * (len(yrs) + 2))
        for nm, k in h['children'].items():
            w('| %s | %s | %s | %s | %s |' % (nm, k['first'], ' | '.join(usd(k['by_year'].get(str(y), k['by_year'].get(y))) for y in yrs),
                                          usd(k['total_pnl']), usd(k['account_value_now'])))
        w('| **parent (all)** | 2023-05 | %s | %s | %s |' % (' | '.join(usd(h['parent_pnl_by_year'].get(str(y), h['parent_pnl_by_year'].get(y))) for y in yrs),
                                                         usd(h['parent_total_pnl']), usd(h['capacity']['tvl_now_usd'])))
        w('')
        w('Recent month (%s → %s, %d points, median gap %.1f h): %s a year; worst period %s.' % (
            h['recent_month']['window'][0], h['recent_month']['window'][1], h['recent_month']['points'],
            h['recent_month']['median_gap_hours'], pct(h['recent_month']['ann_return']), pct(h['recent_month']['worst_period'], 2)))
        w('')
    w('## 6. Capacity (fixed-dollar income assumption; regression of income on TVL over the test half)')
    w('')
    w('| vault | TVL now | hedged vault yield (test / last 365d) | income = a + b·TVL: a ($/day, t) | b (a year, t) | excess now | '
      'at +$10M | at +$50M | deposit to +2pp | to 0 |')
    w('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for n, v in V.items():
        c = v.get('capacity') or {}
        f = c.get('income_vs_tvl_test') or {}
        ea = c.get('excess_at') or {}
        w('| %s | %s | %s / %s | %s (%s) | %s (%s) | %s | %s | %s | %s | %s |' % (
            n, usd(c.get('tvl_now_usd')), pct(c.get('vault_hedged_yield_test')), pct(c.get('vault_hedged_yield_365d')),
            usd(f.get('a_usd_day')), num(f.get('t_a')), pct((f.get('b_per_day') or 0) * 365) if f else '—', num(f.get('t_b')),
            pct(c.get('excess_now_at_0')), pct(ea.get('10000000.0')), pct(ea.get('50000000.0')), usd(c.get('deposit_for_2pp')),
            usd(c.get('deposit_for_0'))))
    w('')
    w('Hedge depth (Binance 30-day average daily quote volume): ' + ', '.join('%s %s' % (k, usd(x)) for k, x in (A.get('hedge_depth') or {}).items()))
    w('')
    w('## 7. Late entry and jumps (test half, chosen variant)')
    w('')
    w('| vault | best-1% periods | share of test P&L | excess without them | 1 h late keeps | 1 period late (rules) |')
    w('|---|---|---:|---:|---:|---:|')
    for n, v in V.items():
        j = v.get('late_entry_jumps') or {}
        le = v.get('late_entry') or {}
        w('| %s | %s | %s | %s | %s | %s |' % (n, '; '.join('%s→%s %s' % (a, b, pct(x, 2)) for a, b, x in j.get('best1pct_periods', [])),
                                            num(j.get('best1pct_share')), pct(j.get('ann_excess_ex_best1pct')),
                                            pct(j.get('one_hour_late_share_kept'), 2, False), num(le.get('share_kept')) if le else 'always on'))
    w('')
    w('## 8. Named incidents (the period containing the date; static/rolling hedge as chosen, always on)')
    w('')
    w('| vault | date | incident | period | vault return | hedged excess |')
    w('|---|---|---|---|---:|---:|')
    for n, v in V.items():
        for r in v.get('incidents') or []:
            w('| %s | %s | %s | %s → %s | %s | %s |' % (n, r['date'], r['incident'], r['period'][0], r['period'][1], pct(r['vault_return'], 2),
                                                   pct(r['excess'], 2)))
    w('')
    w('## 9. Worst and best test-half periods (chosen variant)')
    w('')
    for n, v in V.items():
        e = v.get('events_test') or {}
        w('- **%s** worst: %s; best: %s' % (n, '; '.join('%s %s' % (x['start'][:10], pct(x['excess'], 2)) for x in e.get('worst', [])),
                                            '; '.join('%s %s' % (x['start'][:10], pct(x['excess'], 2)) for x in e.get('best', []))))
    w('')
    w('## 10. Independent checks')
    w('')
    for n, v in V.items():
        for k, x in (v.get('checks') or {}).items():
            w('- %s / %s: `%s`' % (n, k, json.dumps(x, default=str)[:400]))
    if A.get('dydx_megavault'):
        w('- dYdX / %s' % json.dumps(A['dydx_megavault']['checks'])[:300])
    w('')
    w('## 11. Venues skipped')
    w('')
    for k, x in (A.get('skipped') or {}).items():
        w('- %s: %s' % (k, x))
    w('')
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    rows = write_book_entries(out, A)
    print('book entries:', [r['id'] for r in rows])
    build_manifest(out)
    print('wrote', out / 'tables.md', 'and manifest.json')


# ----------------------------------------------------------------------------------------------------------------------
# book entries (proposals only: written to the study folder, never to research/strategies.jsonl)
# ----------------------------------------------------------------------------------------------------------------------
BOOK_SIZES = {'JLP': 10e6, 'GM_SOL-USDC': 2e6, 'gUSDC_arbitrum': 1e6}


def quote_excess(v, size):
    """Conservative quote at a deposit size: the fixed-income dilution of the hedged yield, lowered further by the gap
    between the chosen measurement and the least favourable robustness re-measurement."""
    c = v.get('capacity') or {}
    ea = (c.get('excess_at') or {}).get(str(float(size)))
    if ea is None:
        return None
    rob = v.get('robustness_min')
    if rob is None:
        return ea
    return min(ea, rob - ((c.get('excess_now_at_0') or ea) - ea))


def book_entry(name, v, A):
    o, i = v['chosen_out'], v['chosen_in']
    size = BOOK_SIZES.get(name, 1e6)
    q = quote_excess(v, size)
    rob = v.get('robustness') or {}
    robtxt = '; '.join('%s %+.1f%%' % (k, 100 * r['ann_excess']) for k, r in rob.items() if isinstance(r, dict) and r.get('ann_excess') is not None)
    ev = {'notes': 'research/2026-10-10/house_vaults/analysis.json vaults.%s (chosen_in/out, variants, robustness, capacity, '
                   'decomposition_fees, checks); tables.md; scripts/house_vaults.py (collect / analyze / render)' % name,
          'findings': [], 'verify': []}
    common = {'kind': 'liquidity', 'status': 'proposed', 'capital_days': 365, 'recheck_hours': 72, 'evidence': ev}
    if name == 'JLP':
        df = v['decomposition_fees']
        ps = v['pool_state_now']
        e = dict(common)
        e.update({
            'id': 'jlp-hedged-house-lp',
            'name': 'Hold JLP (Jupiter perps liquidity) and short its net SOL/ETH/BTC delta on Binance perps: keep the house\'s fee share',
            'thesis': ('JLP is the counterparty to every Jupiter perps trade and receives 75%% of its fees. Hedged with a trailing '
                       '60-day beta to SOL/ETH/BTC (chosen on %s..%s), it beat the savings rate by %+.1f%% a year on capital in '
                       'the test half %s..%s (Newey-West t %.2f; bootstrap %+.1f%%..%+.1f%%; max drawdown %.1f%%; worst week %+.1f%%), '
                       'after fees, funding and a 0.2%% mint/burn round trip. The pool\'s fee yield over the same window was '
                       '%.1f%% a year against a hedged vault yield of %.1f%%: under the chosen hedge the return is the fee share, '
                       'with traders\' net P&L, staking and hedge error adding %+.1f%%. Re-measured without selection the test half reads %s, so the quote uses the least '
                       'favourable one. The fee yield is falling (%s) and the venue reports %.1f%% now.'
                       % (v['in_sample'][0], v['in_sample'][1], 100 * o['ann_excess'], v['test'][0], v['test'][1], o['nw_t'],
                          100 * o['boot_lo'], 100 * o['boot_hi'], 100 * o['max_drawdown'], 100 * o['worst_week'],
                          100 * df['fee_yield_test'], 100 * df['vault_hedged_test'],
                          100 * df['residual_test_trader_pnl_staking_hedge_error'], robtxt,
                          ', '.join('%s %.0f%%' % (y, 100 * x) for y, x in sorted(df['fee_yield_by_year'].items())),
                          ps['apr_field_pct'])),
            'mechanism': ('Retail leverage demand on Solana\'s largest perp venue pays open/close fees, hourly borrow fees and '
                          'price impact; JLP holders receive 75%% of them and take the other side of trader P&L. The pool holds '
                          'SOL, ETH, WBTC and dollars at target weights (now %s); its market exposure is the tokens it owns less '
                          'what traders\' longs have locked, plus traders\' shorts. Shorting that net delta leaves the fee share, '
                          'traders\' net P&L and any staking yield on the SOL custody (jlp-info reports %s of the %s SOL '
                          'custody as staked).'
                          % (', '.join('%s %.0f%%' % (k, x) for k, x in ps['target_weights'].items() if x),
                             usd(ps['sol_staked_usd']), usd(ps['sol_custody_usd']))),
            'legs': [
                'mint JLP with USDC (or SOL) through the Jupiter perps pool, or buy it on a DEX, in tranches; mint/burn fees are '
                'dynamic (about 0.1% each way at target weights)',
                'short SOL, ETH and BTC USDT-margined perps on Binance sized to JLP\'s net delta: daily from jlp-info (owned minus '
                'locked plus short open interest per custody), cross-checked with a trailing 60-day regression (betas now %s); '
                'margin one third of the short notional in USDC' % ({k: round(x, 2) for k, x in v['last_rolling_betas'].items()}),
                'rebalance a leg when it drifts more than 10% from target; top up the margin from JLP burns after a rally',
                'hold; no timing rule (always on was chosen)'],
            'capacity_usd': size,
        })
        e['kill_criteria'] = [
            'trailing 30-day fee yield (DefiLlama supply-side revenue / JLP AUM) below 6.5% a year: hedged, that is under '
            'the savings rate + 1.5pp on capital',
            'realised hedged excess over the savings rate negative over a trailing 90 days (house_vaults.py analyze, JLP chosen variant)',
            'first 60 days live: realised hedged excess below +1% a year with the jlp-info net-delta hedge (the backtest\'s '
            'regression hedge is replaced, and must be shown to work)',
            'daily hedged P&L standard deviation above 0.5% for two weeks (the delta is not being tracked)',
            'any Jupiter perps exploit, oracle failure, AUM-limit or fee-split change (75% to LPs), or JLP depeg of more '
            'than 1% from its NAV on DEXs']
        e['risks'] = [
            'model risk in the hedge: the test-half excess ranged %s across hedge windows and price sources; the chosen 60-day '
            'window read highest (+%.1f%%)' % (robtxt, 100 * o['ann_excess']),
            'traders\' net P&L is the pool\'s short option: rallies with crowded longs cost the hedged position (worst test day %s %+.1f%%: '
            'SOL %+.1f%% that day)' % (v['events_test']['worst'][0]['start'][:10], 100 * v['events_test']['worst'][0]['excess'],
                                       100 * v['events_test']['worst'][0]['assets'].get('SOL', 0)),
            'half of the test-half P&L came from the best 1%% of days (%.0f%%): jumps on volatile days, not a smooth accrual'
            % (100 * v['late_entry_jumps']['best1pct_share']),
            'fee yield has fallen from %.0f%% (2024) to %.0f%% (2026); the edge is the fee share and shrinks with volume'
            % (100 * df['fee_yield_by_year'].get('2024', 0), 100 * df['fee_yield_by_year'].get('2026', 0)),
            'smart-contract, oracle and custody risk on Solana (Jupiter perps program, Wormhole-bridged ETH/WBTC custodies)',
            'two venues: JLP on Solana, the short on Binance; a rally needs margin moved before the short is liquidated']
        e['quotes'] = [{
            'at': A['generated_at'][:19] + '+00:00', 'window': 'research/2026-10-10/house_vaults', 'source': 'history',
            'present': True, 'go': True, 'net_apr': round(q, 4), 'usd': int(round(q * size, -3)),
            'note': ('excess over the 3.80%% savings rate on capital (JLP + one-third margin on a ~%.2f short), at $%dM: the '
                     'least favourable test-half re-measurement (%+.1f%%) less dilution; the chosen measurement reads %+.1f%% '
                     '(t %.2f). Current JLP AUM %s, venue APR %.1f%%.'
                     % (v['decomposition_out']['mean_gross_hedge'], size / 1e6, 100 * v['robustness_min'], 100 * o['ann_excess'],
                        o['nw_t'], usd(ps['aum_usd']), ps['apr_field_pct']))}]
        return e
    if name == 'GM_SOL-USDC':
        df = v['decomposition_fees']
        ck = (v.get('checks') or {}).get('price_vs_poolvalue_over_supply') or {}
        e = dict(common)
        e.update({
            'id': 'gmx-gm-sol-usdc-hedged-lp',
            'name': 'Deposit in GMX v2 GM SOL/USD [SOL-USDC] on Arbitrum and short the pool\'s SOL delta on Binance',
            'thesis': ('The GM SOL-USDC pool is the counterparty to GMX\'s SOL perp traders. Hedged with its in-sample beta '
                       '(%.2f SOL, chosen on %s..%s), it beat the savings rate by %+.1f%% a year on capital in the test half '
                       '%s..%s (Newey-West t %.2f; bootstrap %+.1f%%..%+.1f%%; max drawdown %.1f%%; worst week %+.1f%%). The '
                       'squid\'s own accounting explains it: fees %.1f%% a year (of which borrowing %.1f%%) plus traders\' net '
                       'losses %.1f%% against a measured hedged yield of %.1f%%. Re-measured without selection: %s. The pool is '
                       'small (%s), so the income dilutes: the quote is at $%dM.'
                       % (v['static_betas_in_sample'].get('SOL', 0), v['in_sample'][0], v['in_sample'][1], 100 * o['ann_excess'],
                          v['test'][0], v['test'][1], o['nw_t'], 100 * o['boot_lo'], 100 * o['boot_hi'], 100 * o['max_drawdown'],
                          100 * o['worst_week'], 100 * df['apr_by_fee_test'], 100 * df['apr_by_borrowing_fee_test'],
                          100 * df['apr_trader_pnl_test'], 100 * df['vault_hedged_test'], robtxt,
                          usd(v['capacity']['tvl_now_usd']), size / 1e6)),
            'mechanism': ('GMX v2 isolates each market: this pool holds wrapped SOL and USDC, earns position, swap and borrow '
                          'fees and the traders\' net losses, and pays their wins. Its SOL exposure is the SOL it holds less '
                          'traders\' net long open interest (now long %s, short %s). The capital that would compete the fee '
                          'yield down is small because the market is small and on Arbitrum.'
                          % (usd(ck.get('long_oi_usd')), usd(ck.get('short_oi_usd')))),
            'legs': ['deposit USDC and SOL in the pool\'s ratio through the GMX v2 ExchangeRouter (deposit fee ~0.05-0.07%; '
                     'the cap is $17.5M a side, not binding)',
                     'short the SOL USDT perp on Binance at the pool\'s SOL beta (%.2f in sample, %.2f trailing 60 days) per '
                     'dollar deposited; one-third margin' % (v['static_betas_in_sample'].get('SOL', 0), v['last_rolling_betas'].get('SOL', 0)),
                     'rebalance at a 10% drift; hold'],
            'capacity_usd': size,
        })
        e['kill_criteria'] = [
            'trailing 30-day aprByFee (squid) below 6% a year',
            'realised hedged excess over the savings rate negative over a trailing 90 days',
            'pool value below $3M (the deposit would be most of the pool) or above $15M (the fee yield dilutes away)',
            'any GMX v2 exploit or a Wormhole SOL depeg on Arbitrum of more than 0.5%']
        e['risks'] = [
            'size: the pool is %s; a $%dM deposit cuts the hedged yield by about %.0f%% (fixed-dollar income)'
            % (usd(v['capacity']['tvl_now_usd']), size / 1e6, 100 * size / (v['capacity']['tvl_now_usd'] + size)),
            'traders\' P&L is the pool\'s short option (worst test day %s %+.1f%%)' % (v['events_test']['worst'][0]['start'][:10],
                                                                                   100 * v['events_test']['worst'][0]['excess']),
            'wrapped SOL on Arbitrum (Wormhole) and GMX v2 contract risk; GMX v1 was exploited in July 2025',
            'two venues (Arbitrum and Binance)']
        e['quotes'] = [{
            'at': A['generated_at'][:19] + '+00:00', 'window': 'research/2026-10-10/house_vaults', 'source': 'history',
            'present': True, 'go': True, 'net_apr': round(q, 4), 'usd': int(round(q * size, -3)),
            'note': 'excess over the 3.80%% savings rate on capital at $%dM after fixed-dollar dilution of a %s pool and the '
                    'gap to the least favourable re-measurement; chosen measurement %+.1f%% (t %.2f)'
                    % (size / 1e6, usd(v['capacity']['tvl_now_usd']), 100 * o['ann_excess'], o['nw_t'])}]
        return e
    if name == 'gUSDC_arbitrum':
        df = v.get('decomposition_fees') or {}
        meta = v.get('vault_meta') or {}
        e = dict(common)
        e.update({
            'id': 'gains-gusdc-arbitrum-lp',
            'name': 'Deposit USDC in Gains Network\'s gUSDC vault on Arbitrum (the gTrade house vault)',
            'thesis': ('gUSDC is the counterparty to gTrade\'s traders and holds only USDC. Chosen on %s..%s (%s), it beat the '
                       'savings rate by %+.1f%% a year in the test half %s..%s (Newey-West t %.2f; max drawdown %.2f%%). '
                       'Re-measured without selection: %s. Its dollar income is fixed (it does not grow with deposits), so '
                       'the vault\'s %s caps the size.'
                       % (v['in_sample'][0], v['in_sample'][1], v['chosen'], 100 * o['ann_excess'], v['test'][0], v['test'][1],
                          o['nw_t'], 100 * o['max_drawdown'], robtxt, usd(v['capacity']['tvl_now_usd']))),
            'mechanism': ('Fees are credited per share (accRewardsPerToken); traders\' net wins are charged per share '
                          '(accPnlPerToken); withdrawals are requested and paid after %s epochs (an epoch measured at %.1f days, '
                          'so about %.0f days; the wait costs ~%.2f%% at the savings rate, but it means no exit during a run of '
                          'trader wins).' % (meta.get('withdraw_epochs_timelock_now'), meta.get('epoch_days_measured') or 0,
                                             meta.get('withdrawal_wait_days_now') or 0, 100 * (meta.get('withdrawal_wait_cost_at_ssr') or 0))),
            'legs': ['deposit USDC (ERC-4626 deposit; no fee)', 'request withdrawals ahead of need (epoch-gated)'],
            'capacity_usd': size,
        })
        e['kill_criteria'] = ['realised excess over the savings rate negative over a trailing 90 days',
                              'collateralization below 100% (traders net winning beyond the buffer)',
                              'vault TVL below $2M']
        e['risks'] = ['traders\' net wins are paid from the vault; withdrawals are gated by epochs',
                      'Gains contract risk on Arbitrum']
        e['quotes'] = [{
            'at': A['generated_at'][:19] + '+00:00', 'window': 'research/2026-10-10/house_vaults', 'source': 'history',
            'present': True, 'go': True, 'net_apr': round(q, 4), 'usd': int(round(q * size, -3)),
            'note': 'excess over the savings rate at $%dM after fixed-dollar dilution' % (size / 1e6)}]
        return e
    return None


def write_book_entries(out, A):
    rows = []
    for n, v in A['vaults'].items():
        if v.get('verdict') == 'go':
            e = book_entry(n, v, A)
            if e:
                rows.append(e)
    f = out / 'book_entries.json'
    if rows:
        f.write_text(json.dumps(rows, indent=1) + '\n')
    elif f.exists():
        f.unlink()
    return rows


# ----------------------------------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--out', default=str(OUT))
    c.add_argument('--parts', default='hlp,binance,jlp,llama,gmx,gains,dydx,lighter,probes')
    c.add_argument('--refresh', action='store_true')
    a = sub.add_parser('analyze')
    a.add_argument('--out', default=str(OUT))
    r = sub.add_parser('render')
    r.add_argument('--out', default=str(OUT))
    args = ap.parse_args(argv)
    if args.cmd == 'collect':
        cmd_collect(args)
    elif args.cmd == 'analyze':
        cmd_analyze(args)
    elif args.cmd == 'render':
        cmd_render(args)


if __name__ == '__main__':
    main()
