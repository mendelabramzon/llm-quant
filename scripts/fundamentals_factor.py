#!/usr/bin/env python3
"""Do on-chain fundamentals predict token returns? The bridge from the chain-activity framework to a trading rule.

Why. `chain_activity.py` was built to "detect new activity on chains where it is reasonable to trade": stablecoins
arriving, DEX volume and fees surging against a chain's own month. Nobody had asked whether any of it moves the price
of the one thing a trader can hold for that chain, its token. This module is the test, slow on purpose — weekly,
cross-sectional, hedged, net of perp costs and funding, over every year DefiLlama's free history allows — plus a replay
of the framework's own surge and stablecoin-inflow detectors on that history, so "new activity" is tested exactly as
the framework defines it.

Two families of signals; every signal x hedge is a counted variant:

  chain flows -> the chain's token. 4- and 12-week log change of the stablecoin float (7-day mean); the change in the
      chain's share of all stablecoins (percentage points: the log change of a share ranks chains exactly as the log
      change of the float does, because the total is common to every chain in a week); DEX volume, fees (everything
      paid on the chain, its own gas included) and TVL (28-day means; TVL is in dollars and moves with the token's own
      price, so it is momentum in disguise and is tested against momentum); a composite of the four 4-week ranks.
  protocol value -> the protocol's token. 4- and 12-week growth of fees and revenue (28-day means); fees and revenue
      over fully diluted value (price x CoinGecko's max supply where the token is capped, else today's total supply —
      a supply look-ahead for inflating tokens); a composite. Chain tokens are left out of this family except app-chains
      whose protocol fees accrue to them (HYPE, DYDX, RUNE, INJ, FRAX).

  Controls, not candidates: the token's own 4- and 12-week price momentum.

  The framework replayed: chain_surge (DEX and fees d1/d7, TVL d7; ratio, empirical p and market-excess exactly as
  chain_activity computes them, checked against chain_activity.surge_stats in the tests) and stable_inflow (7 and 30
  readings), every day of history, first fire per token and type in 28 days; long the token from the close of the day
  after the data day for 7 or 28 days, hedged with BTC or with a basket of the other liquid chain tokens.

Data traps handled. A DefiLlama stablecoin reading written as {} is missing, never zero. Binance prints flat,
zero-volume bars at the settlement price for months after a perp is delisted, and Hyperliquid returns zero-volume bars
with prices before a coin's first trade: an untraded bar is not a price anywhere here (returns, beta, momentum,
liquidity, the identity check). DefiLlama serves some chains under two names ('OP Mainnet', 'Optimism'): identical
member series count once. The bars are fetched intraday, so the last one is partial and never used.

Timing. Rebalance Mondays 00:00 UTC. A signal reads DefiLlama days up to Saturday, one full UTC day of publication lag
after the last data day; the position earns Sunday close to next Sunday close on the perp (Binance USD-M daily bars,
Hyperliquid's where Binance has no perp that week), pays or receives that week's funding, and pays a per-side cost on
the week's turnover. Long the top tercile, short the bottom, equal weight, $1 a side per $1 of capital; beta-neutral
variants add a BTC position that zeroes the book's trailing 84-day beta.

Universe, point in time. A token is a candidate when a DefiLlama chain or protocol names its CoinGecko id and a Binance
USD-M perp (current or delisted: the public archive lists every symbol ever traded) or a Hyperliquid perp carries its
ticker; the identity is kept only when the venue's price agrees with DefiLlama's price for that id within 25% on a day
both traded (migrations such as MATIC->POL are named by hand). A token enters a week's cross-section when its perp has
a close the day before, at least $5M a day of perp volume over 28 days, and the signal's own history and floor.

    uv run python scripts/fundamentals_factor.py collect --out research/2026-10-10/fundamentals_factor          # all steps, cached
    uv run python scripts/fundamentals_factor.py collect --out ... --step universe|prices|verify|llama|funding|books|gecko
    uv run python scripts/fundamentals_factor.py analyze --out research/2026-10-10/fundamentals_factor
    uv run python scripts/fundamentals_factor.py render  --out research/2026-10-10/fundamentals_factor
"""
import argparse
import bisect
import collections
import datetime as dt
import gzip
import io
import json
import math
import random
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

UTC = dt.timezone.utc
DAY = 86400
DAY_MS = DAY * 1000
LLAMA = 'https://api.llama.fi'
STABLES = 'https://stablecoins.llama.fi'
COINS = 'https://coins.llama.fi'
BN = 'https://fapi.binance.com'
ARCHIVE = 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision'
GECKO = 'https://api.coingecko.com/api/v3'
SSR = 0.038
HISTORY_START = '2019-09-01'

# Venue symbols named by hand: migrations and renames the symbol search cannot find. Returns are computed per symbol,
# so a conversion ratio matters only to the value signal, which uses the token's current symbol alone.
CHAIN_VENUES = {
    'polygon-ecosystem-token': ['MATICUSDT', 'POLUSDT'],     # MATIC -> POL 1:1, 2024-09
    'kaia': ['KLAYUSDT', 'KAIAUSDT'],                        # Klaytn renamed Kaia, 1:1
    'vaulta': ['EOSUSDT', 'AUSDT'],                          # EOS rebranded Vaulta (A), 1:1
    'terra-luna': ['LUNAUSDT', '1000LUNCUSDT'],              # Terra Classic: LUNA until the 2022-05 collapse, then LUNC
    'terra-luna-2': ['LUNA2USDT'],                           # the 2022 relaunch; its ticker LUNA is the old chain's symbol
    'frax-share': ['FXSUSDT', 'FRAXUSDT'],                   # FXS renamed FRAX, 1:1
    'the-open-network': ['TONUSDT'],                         # DefiLlama's chain symbol is GRAM
    'dydx-chain': ['DYDXUSDT'],
}
PROTOCOL_VENUES = {
    'sky': ['MKRUSDT', 'SKYUSDT'],                           # MKR -> SKY at 1:24,000
    'frax-share': ['FXSUSDT', 'FRAXUSDT'],
}
# not candidates: the hedge itself, dollars, and chains whose gas token is a dollar
EXCLUDE_GECKO = {'bitcoin', 'usd-coin', 'tether', 'dai', 'xdai', 'usds', 'first-digital-usd', 'ethena-usde',
                 'paypal-usd', 'true-usd', 'binance-usd', 'frax', 'gho', 'usual-usd'}
PRICE_TOL = 0.25
# A chain token is a protocol token only where the protocol's fees accrue to it (app-chains); elsewhere DefiLlama's
# "protocol" with a chain token's id is a canonical bridge or a foundation ('Starknet Bridge', 'Ethereum Foundation'),
# or another project's metadata ('FlowSwap' -> FLOW). Gold tokens track gold, not fees.
APPCHAIN_PROTOCOLS = {'hyperliquid', 'dydx-chain', 'thorchain', 'injective-protocol', 'frax-share'}
NOT_A_PROTOCOL_CLAIM = {'tether-gold', 'pax-gold'}


def utc_now():
    return dt.datetime.now(UTC)


def day_str(ts):
    return dt.datetime.fromtimestamp(int(ts), UTC).strftime('%Y-%m-%d')


def day_ts(d):
    return int(dt.datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=UTC).timestamp())


def add_days(d, n):
    return day_str(day_ts(d) + n * DAY)


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_gz(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(p, 'wt') as f:
        json.dump(obj, f)


def write_json(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def safe(name):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', name)


def slugify(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


# ---------------------------------------------------------------------------------------------- collect: plumbing

class Net:
    """One paced client per host family, with request counts and failures for the manifest."""

    def __init__(self):
        from chain_adapters import Http
        self.http = Http(min_interval=0.0, timeout=120, retries=4)
        self.http.host_interval.update({'api.llama.fi': 0.35, 'stablecoins.llama.fi': 0.35, 'coins.llama.fi': 0.4,
                                        'fapi.binance.com': 0.45, 'api.coingecko.com': 8.0,
                                        's3-ap-northeast-1.amazonaws.com': 0.2, 'data.binance.vision': 0.2})
        # Binance's funding endpoint has its own 500 / 5 min / IP budget, shared with every other worker here
        self.fund = Http(min_interval=0.0, timeout=60, retries=5)
        self.fund.host_interval['fapi.binance.com'] = 1.5
        self.failures = {}
        self.t0 = time.time()

    def get(self, name, url, params=None, client=None):
        try:
            return (client or self.http).get(url, params)
        except Exception as e:  # noqa: BLE001 - recorded in the manifest, the step carries on
            self.failures[name] = str(e)[:200]
            return None

    def raw(self, url):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        self.http._wait(urllib.parse.urlsplit(url).netloc)
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()

    def stats(self):
        return {'requests': self.http.requests, 'bytes': self.http.bytes, 'errors': len(self.http.errors),
                'funding_requests': self.fund.requests, 'funding_errors': len(self.fund.errors),
                'failures': dict(list(self.failures.items())[:80]), 'n_failures': len(self.failures),
                'seconds': round(time.time() - self.t0, 1)}


def cached(path, fetch, net=None, name=None):
    """Return the gzip-cached JSON at `path`, fetching (and caching anything not None) when absent. With `net` and
    `name`, a failed fetch is cached too, as {'_failed': reason}: DefiLlama answers HTTP 500 for a chain without a DEX or
    fee adapter, and the client retries a 500 with backoff, so an uncached failure costs ~20 s on every rerun."""
    p = Path(path)
    if p.exists():
        return read_gz(p)
    v = fetch()
    if v is not None:
        write_gz(p, v)
    elif net is not None and name in net.failures:
        write_gz(p, {'_failed': net.failures[name]})
    return v


def manifest_update(out, key, value):
    p = Path(out) / 'manifest.json'
    man = json.loads(p.read_text()) if p.exists() else {}
    man[key] = value
    man['updated'] = utc_now().isoformat(timespec='seconds')
    write_json(p, man)


# ---------------------------------------------------------------------------------------------- collect: universe

def archive_symbols(net):
    """Every USD-M perp symbol Binance's public archive has daily klines for (delisted ones included)."""
    syms, marker = [], ''
    for _ in range(20):
        url = ARCHIVE + '?delimiter=/&prefix=data/futures/um/monthly/klines/' + ('&marker=' + urllib.parse.quote(marker) if marker else '')
        body = net.raw(url).decode()
        syms += re.findall(r'<Prefix>data/futures/um/monthly/klines/([^/<]+)/</Prefix>', body)
        if '<IsTruncated>true' not in body:
            break
        m = re.search(r'<NextMarker>([^<]+)</NextMarker>', body)
        if not m:
            break
        marker = m.group(1)
    return sorted(set(syms))


def venue_candidates(ticker, bn_syms, hl_coins):
    """[(venue, symbol, scale)] for a token ticker: Binance USDT perps with the usual 1000x prefixes, Hyperliquid
    coins with its k-prefix."""
    t = (ticker or '').upper()
    if not t or not re.fullmatch(r'[A-Z0-9]+', t):
        return []
    out = []
    for pre, sc in (('', 1.0), ('1000', 1000.0), ('10000', 1e4), ('1000000', 1e6), ('1M', 1e6)):
        s = pre + t + 'USDT'
        if s in bn_syms:
            out.append(('binance', s, sc))
    for c, sc in ((t, 1.0), ('k' + t, 1000.0)):
        if c in hl_coins:
            out.append(('hl', c, sc))
    return out


def symbol_scale(sym):
    for pre, sc in (('1000000', 1e6), ('10000', 1e4), ('1000', 1000.0), ('1M', 1e6)):
        if sym.startswith(pre) and len(sym) > len(pre) + 4:
            return sc
    return 1.0


def build_candidates(chains, lite, stable_ids, bn_syms, hl_coins):
    """Chain tokens (grouped by CoinGecko id over every chain naming it) and protocol tokens (parents first), each with
    its venue candidates."""
    tokens = {}
    for c in chains:
        g, sym = c.get('gecko_id'), c.get('tokenSymbol')
        if not g or g in EXCLUDE_GECKO or g in stable_ids or c['name'] in ('Off Chain',):
            continue
        t = tokens.setdefault(g, {'gecko': g, 'symbol': sym, 'chains': [], 'override': g in CHAIN_VENUES})
        t['chains'].append(c['name'])
    for g, t in tokens.items():
        if g in CHAIN_VENUES:
            t['venues'] = [('binance', s, symbol_scale(s)) for s in CHAIN_VENUES[g]]
            t['venues'] += [v for v in venue_candidates(t['symbol'], set(), hl_coins)]
        else:
            t['venues'] = venue_candidates(t['symbol'], bn_syms, hl_coins)
    chain_tokens = {g: t for g, t in tokens.items() if t['venues']}

    protos = {}
    for p in lite.get('parentProtocols') or []:
        g = p.get('gecko_id')
        if not g or g in EXCLUDE_GECKO or g in stable_ids:
            continue
        slug = slugify(p['name'])
        protos[g] = {'gecko': g, 'symbol': p.get('symbol'), 'name': p['name'], 'parent': True,
                     'slugs': list(dict.fromkeys([slug, p['id'].split('#', 1)[-1]])),
                     'override': g in PROTOCOL_VENUES}
    for p in lite.get('protocols') or []:
        g = p.get('geckoId')
        if not g or g in protos or g in EXCLUDE_GECKO or g in stable_ids:
            continue
        protos[g] = {'gecko': g, 'symbol': p.get('symbol'), 'name': p['name'], 'parent': False,
                     'slugs': [slugify(p['name'])], 'category': p.get('category'), 'override': g in PROTOCOL_VENUES}
    for g, t in protos.items():
        if g in PROTOCOL_VENUES:
            t['venues'] = [('binance', s, symbol_scale(s)) for s in PROTOCOL_VENUES[g]]
        else:
            t['venues'] = venue_candidates(t['symbol'], bn_syms, hl_coins)
    proto_tokens = {g: t for g, t in protos.items() if t['venues']}
    return chain_tokens, proto_tokens


def step_universe(out, net):
    raw = Path(out) / 'raw'
    chains = cached(raw / 'llama_chains.json.gz', lambda: net.get('llama_chains', LLAMA + '/v2/chains'))
    lite = cached(raw / 'llama_lite_protocols2.json.gz',
                  lambda: _trim_lite(net.get('lite_protocols2', LLAMA + '/lite/protocols2?b=2')))
    stl = cached(raw / 'llama_stablecoins.json.gz', lambda: net.get('stablecoins', STABLES + '/stablecoins'))
    info = cached(raw / 'binance_exchangeInfo.json.gz', lambda: _trim_info(net.get('bn_info', BN + '/fapi/v1/exchangeInfo')))
    arch = cached(raw / 'binance_archive_symbols.json.gz', lambda: archive_symbols(net))
    import perp_rpc as R
    api = R.Info(interval=0.4)
    hl = cached(raw / 'hl_meta.json.gz', lambda: R.meta_and_ctxs(api))
    stable_ids = {s.get('gecko_id') for s in (stl or {}).get('peggedAssets', []) if s.get('gecko_id')}
    bn_syms = {s['symbol'] for s in info['symbols'] if s.get('contractType') == 'PERPETUAL' and s.get('quoteAsset') == 'USDT'}
    bn_syms |= {s for s in arch if s.endswith('USDT')}
    hl_coins = {u['name'] for u in hl[0]['universe']}
    ct, pt = build_candidates(chains, lite, stable_ids, bn_syms, hl_coins)
    write_json(Path(out) / 'candidates.json', {'chains': ct, 'protocols': pt, 'binance_symbols': len(bn_syms),
                                               'hl_coins': len(hl_coins), 'stable_ids_excluded': len(stable_ids)})
    manifest_update(out, 'universe', {'chain_candidates': len(ct), 'protocol_candidates': len(pt),
                                      'binance_symbols_incl_delisted': len(bn_syms), 'archive_symbols': len(arch),
                                      'hl_coins': len(hl_coins),
                                      'sources': [LLAMA + '/v2/chains', LLAMA + '/lite/protocols2', STABLES + '/stablecoins',
                                                  BN + '/fapi/v1/exchangeInfo', ARCHIVE + ' (data/futures/um/monthly/klines/)',
                                                  'hyperliquid metaAndAssetCtxs']})
    print('candidates: %d chain tokens, %d protocol tokens; %d Binance perps ever, %d HL coins' % (
        len(ct), len(pt), len(bn_syms), len(hl_coins)), flush=True)


def _trim_lite(d):
    if not d:
        return d
    keep_p = ('name', 'symbol', 'geckoId', 'category', 'parentProtocol', 'chains', 'mcap', 'defillamaId')
    keep_pp = ('id', 'name', 'symbol', 'gecko_id', 'chains', 'mcap')
    return {'protocols': [{k: p.get(k) for k in keep_p} for p in d.get('protocols') or []],
            'parentProtocols': [{k: p.get(k) for k in keep_pp} for p in d.get('parentProtocols') or []]}


def _trim_info(d):
    if not d:
        return d
    keep = ('symbol', 'contractType', 'status', 'onboardDate', 'deliveryDate', 'baseAsset', 'quoteAsset', 'underlyingType')
    return {'serverTime': d.get('serverTime'), 'symbols': [{k: s.get(k) for k in keep} for s in d.get('symbols') or []]}


# ---------------------------------------------------------------------------------------------- collect: prices

def bn_klines(net, sym, start_ms, end_ms):
    out, s = [], start_ms
    while s < end_ms:
        rows = net.http.get(BN + '/fapi/v1/klines', {'symbol': sym, 'interval': '1d', 'startTime': s, 'endTime': end_ms,
                                                     'limit': 1500})
        if not rows:
            break
        out += rows
        if len(rows) < 1500:
            break
        s = int(rows[-1][0]) + DAY_MS
    return out


def archive_klines(net, sym):
    """Daily klines from data.binance.vision's monthly zips: the fallback for a symbol the API no longer serves."""
    url = ARCHIVE + '?prefix=data/futures/um/monthly/klines/%s/1d/' % sym
    keys = re.findall(r'<Key>([^<]+\.zip)</Key>', net.raw(url).decode())
    rows = []
    for k in keys:
        z = zipfile.ZipFile(io.BytesIO(net.raw('https://data.binance.vision/' + k)))
        for name in z.namelist():
            for line in z.read(name).decode().splitlines():
                parts = line.split(',')
                if parts and parts[0].isdigit():
                    rows.append([int(parts[0])] + parts[1:])
    rows.sort(key=lambda r: r[0])
    return rows


def step_prices(out, net):
    from chain_adapters import HttpError
    import perp_rpc as R
    cand = json.loads((Path(out) / 'candidates.json').read_text())
    raw = Path(out) / 'raw'
    start = day_ts(HISTORY_START) * 1000
    end = int(time.time() * 1000)
    bn, hl = {'BTCUSDT'}, {'BTC'}
    for fam in ('chains', 'protocols'):
        for t in cand[fam].values():
            for v, s, _ in t['venues']:
                (bn if v == 'binance' else hl).add(s)
    got, fallback, empty = 0, [], []
    for s in sorted(bn):
        p = raw / 'klines' / (s + '.json.gz')
        if p.exists():
            got += 1
            continue
        try:
            rows = bn_klines(net, s, start, end)
        except HttpError as e:
            rows = None
            net.failures['klines:' + s] = str(e)[:160]
        if not rows:
            try:
                rows = archive_klines(net, s)
                fallback.append(s)
            except Exception as e:  # noqa: BLE001
                net.failures['archive:' + s] = str(e)[:160]
                rows = []
        if not rows:
            empty.append(s)
        write_gz(p, rows)
        got += 1
        if got % 25 == 0:
            print('  klines %d/%d' % (got, len(bn)), flush=True)
    api = R.Info(interval=0.4)
    for c in sorted(hl):
        p = raw / 'hl_candles' / (safe(c) + '.json.gz')
        if p.exists():
            continue
        try:
            rows = R.candles(api, c, '1d', start, end) or []
        except R.APIError as e:
            net.failures['hl_candles:' + c] = str(e)[:160]
            rows = []
        write_gz(p, rows)
    manifest_update(out, 'prices', {'binance_symbols': len(bn), 'archive_fallback': fallback, 'empty': empty,
                                    'hl_coins': len(hl), 'hl_api': api.stats(), 'net': net.stats(),
                                    'sources': [BN + '/fapi/v1/klines (1d)', 'data.binance.vision monthly klines (fallback)',
                                                'hyperliquid candleSnapshot (1d)']})
    print('prices: %d Binance symbols (%d from the archive, %d empty), %d HL coins' % (len(bn), len(fallback), len(empty), len(hl)))


# ---------------------------------------------------------------------------------------------- collect: identity check

def load_closes(raw, venue, sym):
    """{YYYY-MM-DD: (close, quote volume)} keyed by the bar's UTC day; the close is the price at the next 00:00."""
    if venue == 'binance':
        p = Path(raw) / 'klines' / (sym + '.json.gz')
        if not p.exists():
            return {}
        return {day_str(int(r[0]) // 1000): (float(r[4]), float(r[7])) for r in read_gz(p)}
    p = Path(raw) / 'hl_candles' / (safe(sym) + '.json.gz')
    if not p.exists():
        return {}
    return {day_str(int(r['t']) // 1000): (float(r['c']), float(r['v']) * float(r['c'])) for r in read_gz(p)}


def check_day(closes):
    """A day well inside the symbol's traded history (the median day with volume), where both sources should have a
    price. Untraded bars carry no price: Binance prints flat zero-volume bars at the settlement price for months after
    a delisting, and Hyperliquid's candleSnapshot returns zero-volume bars before a coin's first trade."""
    days = sorted(d for d, (c, q) in closes.items() if q > 0)
    return days[len(days) // 2] if days else None


def step_verify(out, net):
    """Keep a (token, venue symbol) pair only when the venue's close agrees with DefiLlama's price for the token's
    CoinGecko id within 25% on a day the symbol traded; hand-named migrations are kept and marked."""
    cand = json.loads((Path(out) / 'candidates.json').read_text())
    raw = Path(out) / 'raw'
    asks = []
    for fam in ('chains', 'protocols'):
        for g, t in cand[fam].items():
            for v, s, sc in t['venues']:
                cl = load_closes(raw, v, s)
                d = check_day(cl)
                if d:
                    asks.append((fam, g, v, s, sc, d, cl[d][0] / sc))
    need = collections.defaultdict(set)
    for fam, g, v, s, sc, d, px in asks:
        need['coingecko:' + g].add(day_ts(d) + DAY)
    prices = cached(raw / 'llama_check_prices.json.gz', lambda: _batch_hist(net, need))
    uni = {'chains': {}, 'protocols': {}}
    checks = []
    for fam, g, v, s, sc, d, px in asks:
        t = cand[fam][g]
        ref = (prices.get('coingecko:' + g) or {}).get(str(day_ts(d) + DAY))
        ok = ref is not None and ref > 0 and abs(px / ref - 1.0) <= PRICE_TOL
        why = 'price' if ok else ('override' if t.get('override') else 'rejected')
        checks.append({'family': fam, 'gecko': g, 'venue': v, 'symbol': s, 'day': d, 'venue_px': px, 'llama_px': ref,
                       'result': why})
        if why in ('price', 'override'):
            u = uni[fam].setdefault(g, {k: t[k] for k in t if k != 'venues'})
            u.setdefault('venues', []).append({'venue': v, 'symbol': s, 'scale': sc, 'check': why,
                                               'primary': why == 'price'})
    write_json(Path(out) / 'universe.json', uni)
    write_json(Path(out) / 'identity_checks.json', checks)
    c = collections.Counter((x['family'], x['result']) for x in checks)
    manifest_update(out, 'verify', {'checks': {'%s:%s' % k: n for k, n in sorted(c.items())},
                                    'chain_tokens': len(uni['chains']), 'protocol_tokens': len(uni['protocols']),
                                    'source': COINS + '/batchHistorical', 'tolerance': PRICE_TOL})
    print('verified: %d chain tokens, %d protocol tokens; %s' % (len(uni['chains']), len(uni['protocols']), dict(c)))


def _batch_hist(net, need):
    out = {}
    items = sorted(need.items())
    for i in range(0, len(items), 30):
        part = dict((k, sorted(v)) for k, v in items[i:i + 30])
        d = net.get('batchHistorical:%d' % i, COINS + '/batchHistorical',
                    {'coins': json.dumps(part), 'searchWidth': '12h'})
        for k, v in ((d or {}).get('coins') or {}).items():
            want = sorted(part.get(k, []))
            got = {}
            for pr in v.get('prices') or []:
                ts = int(pr['timestamp'])
                near = min(want, key=lambda w: abs(w - ts)) if want else None
                if near is not None and abs(near - ts) <= 12 * 3600:
                    got[str(near)] = float(pr['price'])
            out[k] = got
    return out


# ---------------------------------------------------------------------------------------------- collect: fundamentals

def step_llama(out, net):
    uni = json.loads((Path(out) / 'universe.json').read_text())
    raw = Path(out) / 'raw'
    names = sorted({c for t in uni['chains'].values() for c in t['chains']})
    cached(raw / 'llama' / 'stables_all.json.gz', lambda: net.get('stables:all', STABLES + '/stablecoincharts/all'))
    n = 0
    for name in names:
        q = urllib.parse.quote(name)
        base = raw / 'llama' / 'chain' / safe(name)
        cached(base / 'stables.json.gz', lambda: _trim_stables(net.get('stables:' + name, STABLES + '/stablecoincharts/' + q)),
               net, 'stables:' + name)
        cached(base / 'tvl.json.gz', lambda: net.get('tvl:' + name, LLAMA + '/v2/historicalChainTvl/' + q), net, 'tvl:' + name)
        cached(base / 'dex.json.gz', lambda: _trim_overview(net.get(
            'dex:' + name, LLAMA + '/overview/dexs/%s?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true&dataType=dailyVolume' % q)),
            net, 'dex:' + name)
        cached(base / 'fees.json.gz', lambda: _trim_overview(net.get(
            'fees:' + name, LLAMA + '/overview/fees/%s?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true&dataType=dailyFees' % q)),
            net, 'fees:' + name)
        n += 1
        if n % 20 == 0:
            print('  chains %d/%d' % (n, len(names)), flush=True)
    n = 0
    for g, t in sorted(uni['protocols'].items()):
        base = raw / 'llama' / 'protocol' / safe(g)
        for kind, dtype in (('fees', 'dailyFees'), ('revenue', 'dailyRevenue')):
            p = base / (kind + '.json.gz')
            if p.exists():
                continue
            got = None
            for slug in t['slugs']:
                got = _trim_overview(net.get('%s:%s' % (kind, slug), LLAMA + '/summary/fees/%s?dataType=%s&excludeTotalDataChartBreakdown=true' % (
                    urllib.parse.quote(slug), dtype)))
                if got and got.get('totalDataChart'):
                    got['slug'] = slug
                    break
            write_gz(p, got or {})
        n += 1
        if n % 20 == 0:
            print('  protocols %d/%d' % (n, len(uni['protocols'])), flush=True)
    manifest_update(out, 'llama', {'chains': len(names), 'protocols': len(uni['protocols']), 'net': net.stats(),
                                   'endpoints': {'stables': STABLES + '/stablecoincharts/{chain}',
                                                 'tvl': LLAMA + '/v2/historicalChainTvl/{chain}',
                                                 'dex': LLAMA + '/overview/dexs/{chain}?dataType=dailyVolume',
                                                 'fees': LLAMA + '/overview/fees/{chain}?dataType=dailyFees',
                                                 'protocol': LLAMA + '/summary/fees/{slug}?dataType=dailyFees|dailyRevenue'},
                                   'all_free': 'every endpoint above answered without a key on 2026-10-10'})
    print('llama: %d chains, %d protocols' % (len(names), len(uni['protocols'])))


def _trim_stables(d):
    """Keep the date and the USD-pegged float; a reading DefiLlama writes as {} stays None (missing, never zero)."""
    if d is None:
        return None
    return [[int(x['date']), (x.get('totalCirculatingUSD') or {}).get('peggedUSD')] for x in d if isinstance(x, dict)]


def _trim_overview(d):
    if not d:
        return d
    keep = ('name', 'slug', 'gecko_id', 'symbol', 'category', 'parentProtocol', 'total24h', 'total30d', 'totalDataChart')
    return {k: d.get(k) for k in keep if k in d}


# ---------------------------------------------------------------------------------------------- collect: funding, books

def bn_funding(net, sym, start_ms, end_ms):
    out, s = [], start_ms
    while s < end_ms:
        rows = net.fund.get(BN + '/fapi/v1/fundingRate', {'symbol': sym, 'startTime': s, 'endTime': end_ms, 'limit': 1000})
        if not rows:
            break
        out += [[int(r['fundingTime']), float(r['fundingRate'])] for r in rows]
        if len(rows) < 1000:
            break
        s = int(rows[-1]['fundingTime']) + 1
    return out


def ever_liquid(closes, floor=5e6):
    """Whether a symbol's 28-day mean quote volume ever reached `floor` (a name below it never enters a book)."""
    q = [v for _, (c, v) in sorted(closes.items())]
    run = sum(q[:28])
    if len(q) >= 28 and run / 28 >= floor:
        return True
    for i in range(28, len(q)):
        run += q[i] - q[i - 28]
        if run / 28 >= floor:
            return True
    return False


def used_venues(out):
    uni = json.loads((Path(out) / 'universe.json').read_text())
    bn, hl = {'BTCUSDT'}, set()
    for fam in ('chains', 'protocols'):
        for t in uni[fam].values():
            for v in t['venues']:
                (bn if v['venue'] == 'binance' else hl).add(v['symbol'])
    return sorted(bn), sorted(hl)


def hl_needed(out, min_days=7):
    """Hyperliquid coins that are a token's only traded venue on at least `min_days` days (Binance first otherwise):
    the only ones whose funding the books can pay."""
    uni = json.loads((Path(out) / 'universe.json').read_text())
    raw = Path(out) / 'raw'
    need = set()
    for fam in ('chains', 'protocols'):
        for t in uni[fam].values():
            bn_days = set()
            for v in t['venues']:
                if v['venue'] == 'binance':
                    bn_days |= {d for d, (c, q) in load_closes(raw, 'binance', v['symbol']).items() if q > 0}
            for v in t['venues']:
                if v['venue'] == 'hl':
                    own = {d for d, (c, q) in load_closes(raw, 'hl', v['symbol']).items() if q > 0}
                    if len(own - bn_days) >= min_days:
                        need.add(v['symbol'])
    return need


def step_funding(out, net):
    from chain_adapters import HttpError
    import perp_rpc as R
    raw = Path(out) / 'raw'
    bn, hl = used_venues(out)
    end = int(time.time() * 1000)
    for i, s in enumerate(bn):
        p = raw / 'funding' / (s + '.json.gz')
        if p.exists():
            continue
        cl = load_closes(raw, 'binance', s)
        if not cl or not ever_liquid(cl):
            continue
        start = day_ts(min(cl)) * 1000
        try:
            rows = bn_funding(net, s, start, end)
        except HttpError as e:
            net.failures['funding:' + s] = str(e)[:160]
            continue
        write_gz(p, rows)
        if (i + 1) % 20 == 0:
            print('  funding %d/%d' % (i + 1, len(bn)), flush=True)
    api = R.Info(interval=0.4)
    need = hl_needed(out)
    for c in hl:
        p = raw / 'hl_funding' / (safe(c) + '.json.gz')
        if p.exists() or c not in need:
            continue
        cl = load_closes(raw, 'hl', c)
        if not cl:
            continue
        s, rows = day_ts(min(cl)) * 1000, []
        while s < end:
            try:
                part = R.funding_history(api, c, s, end) or []
            except R.APIError as e:
                net.failures['hl_funding:' + c] = str(e)[:160]
                break
            rows += [[int(r['time']), float(r['fundingRate'])] for r in part]
            if len(part) < 500:
                break
            s = int(part[-1]['time']) + 1
        write_gz(p, rows)
    manifest_update(out, 'funding', {'binance_symbols': len(bn), 'hl_coins': len(hl), 'hl_coins_needed': sorted(need),
                                     'binance_skipped_never_liquid': [x for x in bn if not (raw / 'funding' / (x + '.json.gz')).exists()],
                                     'net': net.stats(),
                                     'hl_api': api.stats(),
                                     'sources': [BN + '/fapi/v1/fundingRate', 'hyperliquid fundingHistory']})
    print('funding: %d Binance symbols, %d HL coins' % (len(bn), len(hl)))


def step_books(out, net):
    import perp_rpc as R
    raw = Path(out) / 'raw'
    bn, hl = used_venues(out)
    live = {s['symbol'] for s in read_gz(raw / 'binance_exchangeInfo.json.gz')['symbols'] if s.get('status') == 'TRADING'}
    books = {'at': utc_now().isoformat(timespec='seconds'), 'binance': {}, 'hl': {}}
    for s in bn:
        if s not in live:
            continue
        d = net.get('depth:' + s, BN + '/fapi/v1/depth', {'symbol': s, 'limit': 500})
        if d:
            books['binance'][s] = {'bids': d['bids'][:500], 'asks': d['asks'][:500]}
    api = R.Info(interval=0.4)
    for c in hl + ['BTC']:
        try:
            b = R.l2_book(api, c)
            books['hl'][c] = {'bids': [[x['px'], x['sz']] for x in b['levels'][0]],
                              'asks': [[x['px'], x['sz']] for x in b['levels'][1]]}
        except R.APIError as e:
            net.failures['hl_book:' + c] = str(e)[:120]
    tick = net.get('ticker', BN + '/fapi/v1/ticker/price') or []
    books['binance_last'] = {x['symbol']: float(x['price']) for x in tick if x.get('symbol') in bn}
    try:
        mids = R.all_mids(api)
        books['hl_mids'] = {c: float(mids[c]) for c in hl + ['BTC'] if c in mids}
    except R.APIError as e:
        net.failures['hl_mids'] = str(e)[:120]
    write_gz(raw / 'books.json.gz', books)
    manifest_update(out, 'books', {'at': books['at'], 'binance': len(books['binance']), 'hl': len(books['hl']),
                                   'sources': [BN + '/fapi/v1/depth (limit 500)', 'hyperliquid l2Book']})
    print('books: %d Binance, %d HL' % (len(books['binance']), len(books['hl'])))


def step_gecko(out, net):
    """Today's circulating, total and max supply per token (one markets call per 250 ids): the FDV denominator."""
    uni = json.loads((Path(out) / 'universe.json').read_text())
    ids = sorted(set(uni['chains']) | set(uni['protocols']))
    rows = []
    for i in range(0, len(ids), 200):
        d = net.get('gecko_markets:%d' % i, GECKO + '/coins/markets',
                    {'vs_currency': 'usd', 'per_page': 250, 'ids': ','.join(ids[i:i + 200])})
        if isinstance(d, list):
            rows += [{k: r.get(k) for k in ('id', 'symbol', 'current_price', 'market_cap', 'fully_diluted_valuation',
                                            'circulating_supply', 'total_supply', 'max_supply', 'last_updated')} for r in d]
    write_gz(Path(out) / 'raw' / 'coingecko_markets.json.gz', rows)
    manifest_update(out, 'gecko', {'ids': len(ids), 'rows': len(rows), 'source': GECKO + '/coins/markets',
                                   'note': 'history (market_chart) is limited to 365 days on the free tier: HTTP 401, error 10012'})
    print('gecko: %d of %d ids' % (len(rows), len(ids)))


STEPS = {'universe': step_universe, 'prices': step_prices, 'verify': step_verify, 'llama': step_llama,
         'funding': step_funding, 'books': step_books, 'gecko': step_gecko}


def cmd_collect(args):
    out = Path(args.out)
    (out / 'raw').mkdir(parents=True, exist_ok=True)
    net = Net()
    steps = list(STEPS) if args.step == 'all' else args.step.split(',')
    for s in steps:
        t0 = time.time()
        STEPS[s](out, net)
        print('[%s] %.0fs' % (s, time.time() - t0), flush=True)
    return 0


# ---------------------------------------------------------------------------------------------- analysis: settings

PPY = 365.25 / 7               # weekly periods a year
COST_SIDE_BPS = 15.0           # per side per unit of turnover: taker 5bp + half-spread and impact ~10bp (checked on live books)
COST_BTC_BPS = 6.0             # the BTC hedge: taker 5bp + ~1bp
COST_GRID_BPS = (0.0, 10.0, 15.0, 20.0, 30.0)
LIQ_MIN_USD = 5e6              # 28-day mean perp quote volume a name needs to enter a week's cross-section
MIN_NAMES = 9                  # three a leg
BETA_DAYS, BETA_MIN = 84, 30
LAG_DAYS = 2                   # a Monday signal reads data days up to Saturday: one full UTC day of publication lag
FLOORS = {'stables': 10e6, 'tvl': 20e6, 'dex': 250e3, 'fees': 10e3, 'pfees': 10e3, 'prev': 3e3}
H4, H12 = 28, 84

CHAIN_SIGNALS = ('stables_4w', 'stables_12w', 'stables_share_4w', 'dex_4w', 'dex_12w', 'fees_4w', 'fees_12w',
                 'tvl_4w', 'tvl_12w', 'chain_composite')
PROTOCOL_SIGNALS = ('pfees_4w', 'pfees_12w', 'prev_4w', 'prev_12w', 'pfees_fdv', 'prev_fdv', 'protocol_composite')
CONTROL_SIGNALS = ('mom_4w', 'mom_12w')
HEDGES = ('dollar', 'beta')

# the chain-activity framework's detectors, replayed (chain_activity.py thresholds)
SURGE = {'d1_min_ratio': 2.0, 'd7_min_ratio': 1.5, 'max_p': 0.05, 'market_excess': 1.5, 'base_days': 28,
         'history': 150, 'min_history': 21, 'floors': {'dex': 1e6, 'fees': 2e4, 'tvl': 10e6}}
STABLE_7D = (25e6, 0.10)
STABLE_30D = (50e6, 0.30)
EVENT_TYPES = ('dex_surge', 'fees_surge', 'tvl_surge', 'stable_inflow')
EVENT_HORIZONS = (7, 28)
EVENT_REFRACTORY = 28
PLACEBO_SHIFT = 45
# every variant this study tries: signals x hedges in both families, and event types x horizons x hedges
N_VARIANTS_STUDY = 2 * (len(CHAIN_SIGNALS) + len(PROTOCOL_SIGNALS)) + 2 * len(EVENT_TYPES) * len(EVENT_HORIZONS)


def dnum(s):
    return day_ts(s) // DAY


def dstr(n):
    return day_str(n * DAY)


# ---------------------------------------------------------------------------------------------- analysis: series

def chart_series(rows):
    """DefiLlama chart rows -> {day number: value}. Rows are [ts, v] or {'date', 'tvl'}; a None value is missing (and
    a cached failure, {'_failed': ...}, is no rows at all)."""
    out = {}
    if isinstance(rows, dict):
        rows = rows.get('totalDataChart')
    for r in rows or []:
        if isinstance(r, dict):
            ts, v = r.get('date'), r.get('tvl')
        else:
            ts, v = r[0], r[1]
        if v is None or ts is None:
            continue
        out[int(ts) // DAY] = float(v)
    return out


def combine(members, stock):
    """Sum several chains' daily series into one token's. A stock (float, TVL) is carried forward up to three days per
    member and a day counts only when every member that has started has a value, so one member's missing reading does
    not read as an outflow; a flow (volume, fees) sums what is there."""
    members = [m for m in members if m]
    if not members:
        return {}
    if len(members) == 1:
        return dict(members[0])
    days = sorted(set().union(*members))
    if not stock:
        return {d: sum(m.get(d, 0.0) for m in members) for d in days}
    filled = []
    for m in members:
        f, last, lastd = {}, None, None
        for d in days:
            if d in m:
                last, lastd = m[d], d
            if last is not None and d - lastd <= 3:
                f[d] = last
        filled.append((min(m), f))
    out = {}
    for d in days:
        vals, ok = [], True
        for first, f in filled:
            if d < first:
                continue
            if d not in f:
                ok = False
                break
            vals.append(f[d])
        if ok and vals:
            out[d] = sum(vals)
    return out


def wmean(series, end, n, min_n):
    """Mean of the values on days end-n+1 .. end that exist; None when fewer than `min_n` do."""
    vals = [series[d] for d in range(end - n + 1, end + 1) if d in series]
    return (sum(vals) / len(vals)) if len(vals) >= min_n else None


def stock_level(series, end):
    return wmean(series, end, 7, 5)


def flow_level(series, end):
    return wmean(series, end, 28, 20)


def growth(level_fn, series, end, h, floor):
    """log(level at end / level at end-h); None below the floor now or with nothing then."""
    a, b = level_fn(series, end), level_fn(series, end - h)
    if a is None or b is None or a < floor or b <= 0:
        return None
    return math.log(a / b)


# ---------------------------------------------------------------------------------------------- analysis: prices

def venue_series(raw, venues):
    """[(vkey, scale, primary, {day: close}, {day: quote volume})] in preference order (Binance first, as listed)."""
    out = []
    for v in sorted(venues, key=lambda v: 0 if v['venue'] == 'binance' else 1):
        # Binance keeps printing flat, zero-volume bars for a delisted perp (TONUSDT, FTMUSDT, MKRUSDT to this day):
        # a bar nobody traded is not a price, and left in it would shadow the venue the token moved to
        cl = {d: (c, q) for d, (c, q) in load_closes(raw, v['venue'], v['symbol']).items() if q > 0}
        if not cl:
            continue
        out.append(('%s:%s' % (v['venue'], v['symbol']), v['scale'], v.get('primary', False),
                    {dnum(d): c for d, (c, q) in cl.items()}, {dnum(d): q for d, (c, q) in cl.items()}))
    return out


def daily_returns(vs):
    """Merged daily log returns: each day from the first venue whose close exists that day and the day before."""
    days = sorted(set().union(*[set(c) for _, _, _, c, _ in vs])) if vs else []
    out = {}
    for d in days:
        for _, _, _, c, _ in vs:
            a, b = c.get(d - 1), c.get(d)
            if a and b and a > 0 and b > 0:
                out[d] = math.log(b / a)
                break
    return out


def week_return(vs, R):
    """Return over the week starting Monday R: close of day R-1 (the price at R 00:00) to close of day R+6, on the
    first liquid venue with a close at R-1 (else the first venue with one); a perp delisted mid-week realises its last
    traded close. (return, vkey, close0, scale, primary) or None."""
    order = [v for v in vs if liquid(vs, v[0], R)] + [v for v in vs if not liquid(vs, v[0], R)]
    for vkey, sc, prim, c, q in order:
        c0 = c.get(R - 1)
        if not c0:
            continue
        c1 = None
        for d in range(R + 6, R - 1, -1):
            if c.get(d):
                c1 = c[d]
                break
        if c1 is None:
            continue
        return c1 / c0 - 1.0, vkey, c0, sc, prim
    return None


def liquid(vs, vkey, R, floor=LIQ_MIN_USD):
    for k, sc, prim, c, q in vs:
        if k == vkey:
            v = wmean(q, R - 1, 28, 20)
            return v is not None and v >= floor
    return False


class Funding:
    """Window sums of a venue's funding rates (positive = longs pay), from sorted cumulative sums."""

    def __init__(self, rows):
        rows = sorted((int(t), float(r)) for t, r in rows or [])
        self.t = [t for t, _ in rows]
        self.cum = [0.0]
        for _, r in rows:
            self.cum.append(self.cum[-1] + r)

    def window(self, t0_ms, t1_ms):
        """Sum of rates with time in (t0, t1]; None when the venue has no funding in or before the window."""
        if not self.t or self.t[0] > t1_ms:
            return None
        i, j = bisect.bisect_right(self.t, t0_ms), bisect.bisect_right(self.t, t1_ms)
        return self.cum[j] - self.cum[i]


def load_funding(raw, vkey):
    venue, sym = vkey.split(':', 1)
    p = Path(raw) / ('funding' if venue == 'binance' else 'hl_funding') / ((sym if venue == 'binance' else safe(sym)) + '.json.gz')
    return Funding(read_gz(p) if p.exists() else [])


def ols_beta(xs, ys):
    if len(xs) < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx) if vx > 0 else None


# ---------------------------------------------------------------------------------------------- analysis: panel

def mondays(first, last):
    d = dnum(first)
    d += (7 - dt.date.fromordinal(dt.date(1970, 1, 1).toordinal() + d).weekday()) % 7
    out = []
    while d <= dnum(last):
        out.append(d)
        d += 7
    return out


def build_panel(out, weeks):
    """Per token and week: the perp's return, venue, funding, liquidity, BTC beta and momentum; plus BTC's own."""
    out = Path(out)
    raw = out / 'raw'
    uni = json.loads((out / 'universe.json').read_text())
    gk = {r['id']: r for r in (read_gz(raw / 'coingecko_markets.json.gz') if (raw / 'coingecko_markets.json.gz').exists() else [])}
    btc_vs = venue_series(raw, [{'venue': 'binance', 'symbol': 'BTCUSDT', 'scale': 1.0, 'primary': True}])
    btc_daily = daily_returns(btc_vs)
    # the bars were fetched intraday: the last one is a partial day whose "close" is the price at fetch time
    last_complete = max(btc_vs[0][3]) - 1
    btc_f = load_funding(raw, 'binance:BTCUSDT')
    btc = {}
    for R in weeks:
        w = week_return(btc_vs, R)
        btc[R] = {'ret': w[0] if w else None,
                  'funding': btc_f.window((R) * DAY_MS, (R + 7) * DAY_MS) or 0.0}
    if weeks and weeks[-1] + 6 > last_complete:
        raise SystemExit('the last week (%s) ends after the last complete day %s' % (dstr(weeks[-1]), dstr(last_complete)))
    P = {'weeks': weeks, 'btc': btc, 'tokens': {}, 'missing_funding_weeks': 0, 'excluded_protocols': [],
         'last_complete': last_complete}
    fund_cache = {}
    for fam in ('chains', 'protocols'):
        for g, t in uni[fam].items():
            key = (fam, g)
            if fam == 'protocols' and ((g in uni['chains'] and g not in APPCHAIN_PROTOCOLS) or g in NOT_A_PROTOCOL_CLAIM):
                P['excluded_protocols'].append('%s (%s)' % (g, t.get('name')))
                continue
            vs = venue_series(raw, t['venues'])
            if not vs:
                continue
            dr = daily_returns(vs)
            sup = gk.get(g) or {}
            # A hard cap is known ahead of time; a total supply read today is a look-ahead for inflating tokens.
            supply = sup.get('max_supply') or sup.get('total_supply') or sup.get('circulating_supply')
            supply_kind = 'max' if sup.get('max_supply') else 'total' if sup.get('total_supply') else 'circulating' if supply else None
            rows = {}
            for R in weeks:
                w = week_return(vs, R)
                if not w:
                    continue
                r, vkey, c0, sc, prim = w
                if vkey not in fund_cache:
                    fund_cache[vkey] = load_funding(raw, vkey)
                f = fund_cache[vkey].window(R * DAY_MS, (R + 7) * DAY_MS)
                if f is None:
                    P['missing_funding_weeks'] += 1
                xs, ys = [], []
                for d in range(R - BETA_DAYS, R):
                    if d in dr and d in btc_daily:
                        xs.append(btc_daily[d])
                        ys.append(dr[d])
                m4 = [dr[d] for d in range(R - H4, R) if d in dr]
                m12 = [dr[d] for d in range(R - H12, R) if d in dr]
                rows[R] = {'ret': r, 'venue': vkey, 'funding': f or 0.0, 'funding_known': f is not None,
                           'liquid': liquid(vs, vkey, R),
                           'beta': ols_beta(xs, ys) if len(xs) >= BETA_MIN else None,
                           'mom_4w': sum(m4) if len(m4) >= 0.8 * H4 else None,
                           'mom_12w': sum(m12) if len(m12) >= 0.8 * H12 else None,
                           'fdv': (c0 / sc * supply) if (prim and supply) else None}
            P['tokens'][key] = {'gecko': g, 'symbol': t.get('symbol'), 'family': fam, 'rows': rows, 'supply_kind': supply_kind,
                                'chains': t.get('chains'), 'slugs': t.get('slugs'), 'venues': [v[0] for v in vs]}
    return P


def load_fundamentals(out, P):
    """{(family, gecko): {metric: {day: value}}}: chain tokens sum their chains; protocols read their own summary."""
    raw = Path(out) / 'raw' / 'llama'
    F = {}
    for key, tk in P['tokens'].items():
        fam, g = key
        if fam == 'chains':
            mem = {m: [] for m in ('stables', 'tvl', 'dex', 'fees')}
            for name in tk['chains'] or []:
                base = raw / 'chain' / safe(name)
                for m in mem:
                    p = base / (m + '.json.gz')
                    if not p.exists():
                        continue
                    d = read_gz(p)
                    rows = d.get('totalDataChart') if isinstance(d, dict) else d
                    ser = chart_series(rows)
                    # DefiLlama lists some chains twice under two names ('OP Mainnet' and 'Optimism' serve one
                    # series): an identical member is the same chain, and summing it would double the float
                    if ser and all(ser != x for x in mem[m]):
                        mem[m].append(ser)
            F[key] = {'stables': combine(mem['stables'], True), 'tvl': combine(mem['tvl'], True),
                      'dex': combine(mem['dex'], False), 'fees': combine(mem['fees'], False)}
        else:
            base = raw / 'protocol' / safe(g)
            d = {}
            for m, fn in (('pfees', 'fees'), ('prev', 'revenue')):
                p = base / (fn + '.json.gz')
                d[m] = chart_series((read_gz(p) or {}).get('totalDataChart')) if p.exists() else {}
            F[key] = d
    allp = raw / 'stables_all.json.gz'
    total = {}
    if allp.exists():
        for x in (read_gz(allp) if isinstance(read_gz(allp), list) else []):
            v = (x.get('totalCirculatingUSD') or {}).get('peggedUSD')
            if v is not None:
                total[int(x['date']) // DAY] = float(v)
    return F, total


def signals_for(key, fund, row, R, total_stables):
    """Every signal of one token at Monday R from data days <= R - LAG_DAYS (and the price row known at R)."""
    e = R - LAG_DAYS
    fam = key[0]
    s = {'mom_4w': row.get('mom_4w'), 'mom_12w': row.get('mom_12w')}
    if fam == 'chains':
        st, tv, dx, fe = fund['stables'], fund['tvl'], fund['dex'], fund['fees']
        s['stables_4w'] = growth(stock_level, st, e, H4, FLOORS['stables'])
        s['stables_12w'] = growth(stock_level, st, e, H12, FLOORS['stables'])
        a, b = stock_level(st, e), stock_level(st, e - H4)
        ta, tb = stock_level(total_stables, e), stock_level(total_stables, e - H4)
        s['stables_share_4w'] = (100.0 * (a / ta - b / tb)) if (a and b is not None and ta and tb and a >= FLOORS['stables']) else None
        s['dex_4w'] = growth(flow_level, dx, e, H4, FLOORS['dex'])
        s['dex_12w'] = growth(flow_level, dx, e, H12, FLOORS['dex'])
        s['fees_4w'] = growth(flow_level, fe, e, H4, FLOORS['fees'])
        s['fees_12w'] = growth(flow_level, fe, e, H12, FLOORS['fees'])
        s['tvl_4w'] = growth(stock_level, tv, e, H4, FLOORS['tvl'])
        s['tvl_12w'] = growth(stock_level, tv, e, H12, FLOORS['tvl'])
    else:
        fe, rv = fund['pfees'], fund['prev']
        s['pfees_4w'] = growth(flow_level, fe, e, H4, FLOORS['pfees'])
        s['pfees_12w'] = growth(flow_level, fe, e, H12, FLOORS['pfees'])
        s['prev_4w'] = growth(flow_level, rv, e, H4, FLOORS['prev'])
        s['prev_12w'] = growth(flow_level, rv, e, H12, FLOORS['prev'])
        fdv = row.get('fdv')
        f28, r28 = flow_level(fe, e), flow_level(rv, e)
        s['pfees_fdv'] = (f28 * 365 / fdv) if (fdv and f28 is not None and f28 >= FLOORS['pfees']) else None
        s['prev_fdv'] = (r28 * 365 / fdv) if (fdv and r28 is not None and r28 >= FLOORS['prev']) else None
    return s


def pct_rank(d):
    """{name: percentile rank in (0, 1]} with average ranks for ties."""
    items = sorted(d.items(), key=lambda kv: kv[1])
    n = len(items)
    out, i = {}, 0
    while i < n:
        j = i
        while j + 1 < n and items[j + 1][1] == items[i][1]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[items[k][0]] = r / n
        i = j + 1
    return out


def composite(per_signal, names, parts, min_parts=2):
    """Mean percentile rank over the parts each name has (ranks taken within the week's tradable set)."""
    ranks = [pct_rank({k: v for k, v in per_signal[p].items() if k in names}) for p in parts]
    out = {}
    for k in names:
        xs = [r[k] for r in ranks if k in r]
        if len(xs) >= min_parts:
            out[k] = sum(xs) / len(xs)
    return out


def weekly_scores(P, F, total_stables, family):
    """{signal: {R: {token key: score}}} over the tokens that are tradable that week (a return, a liquid perp)."""
    sigs = (CHAIN_SIGNALS if family == 'chains' else PROTOCOL_SIGNALS) + CONTROL_SIGNALS
    S = {s: {} for s in sigs}
    for R in P['weeks']:
        per = {s: {} for s in sigs}
        names = set()
        for key, tk in P['tokens'].items():
            if key[0] != family:
                continue
            row = tk['rows'].get(R)
            if not row or not row['liquid']:
                continue
            names.add(key)
            v = signals_for(key, F[key], row, R, total_stables)
            for s, x in v.items():
                if s in per and x is not None and math.isfinite(x):
                    per[s][key] = x
        if family == 'chains':
            per['chain_composite'] = composite(per, names, ('stables_4w', 'dex_4w', 'fees_4w', 'tvl_4w'))
        else:
            per['protocol_composite'] = composite(per, names, ('pfees_4w', 'prev_4w', 'pfees_fdv'))
        for s in sigs:
            S[s][R] = per[s]
    return S


# ---------------------------------------------------------------------------------------------- analysis: portfolio

def ls_weights(scores, min_names=MIN_NAMES):
    """Long the top tercile, short the bottom, equal weight, $1 a side; {} below `min_names`. Ties break by name so a
    rerun builds the same book."""
    n = len(scores)
    if n < min_names:
        return {}
    order = sorted(scores, key=lambda k: (scores[k], str(k)))
    k = n // 3
    w = {t: -1.0 / k for t in order[:k]}
    w.update({t: 1.0 / k for t in order[-k:]})
    return w


def run_book(P, scores_by_week, hedge='dollar', cost_bps=COST_SIDE_BPS, cost_btc_bps=COST_BTC_BPS, exclude=()):
    """Weekly long/short book. P&L per $1 a side: sum(w r) + BTC hedge, minus funding paid (longs pay a positive rate,
    shorts receive it), minus costs on turnover measured against last week's weights drifted by last week's returns."""
    rows = []
    prev_w, prev_h, prev_ret, prev_btc = {}, 0.0, {}, 0.0
    toks = P['tokens']
    for R in P['weeks']:
        sc = {k: v for k, v in (scores_by_week.get(R) or {}).items() if k not in exclude}
        w = ls_weights(sc)
        b = P['btc'][R]
        if w and b['ret'] is None:
            w = {}
        h = 0.0
        if w and hedge == 'beta':
            h = -sum(x * (toks[k]['rows'][R]['beta'] if toks[k]['rows'][R]['beta'] is not None else 1.0) for k, x in w.items())
        drift = {k: x * (1.0 + prev_ret.get(k, 0.0)) for k, x in prev_w.items()}
        turn = sum(abs(w.get(k, 0.0) - drift.get(k, 0.0)) for k in set(w) | set(drift))
        turn_b = abs(h - prev_h * (1.0 + prev_btc))
        cost = cost_bps / 1e4 * turn + cost_btc_bps / 1e4 * turn_b
        if not w and not prev_w:
            rows.append({'R': R, 'active': False, 'net': None})
            prev_ret, prev_btc = {}, 0.0
            continue
        gross = sum(x * toks[k]['rows'][R]['ret'] for k, x in w.items()) + (h * b['ret'] if h else 0.0)
        fpnl = -sum(x * toks[k]['rows'][R]['funding'] for k, x in w.items()) - (h * b['funding'] if h else 0.0)
        rows.append({'R': R, 'active': True, 'n': len(sc), 'k': len(w) // 2, 'gross': gross, 'funding': fpnl,
                     'cost': cost, 'net': gross + fpnl - cost, 'turnover': turn, 'hedge': h,
                     'long': sorted(k[1] for k, x in w.items() if x > 0), 'short': sorted(k[1] for k, x in w.items() if x < 0)})
        prev_w, prev_h = w, h
        prev_ret = {k: toks[k]['rows'][R]['ret'] for k in w}
        prev_btc = b['ret'] or 0.0
    return rows


def spearman(xs, ys):
    if len(xs) < 3:
        return None
    rx, ry = pct_rank(dict(enumerate(xs))), pct_rank(dict(enumerate(ys)))
    a, b = [rx[i] for i in range(len(xs))], [ry[i] for i in range(len(ys))]
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va, vb = sum((x - ma) ** 2 for x in a), sum((y - mb) ** 2 for y in b)
    return (sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)) if va > 0 and vb > 0 else None


def weekly_ic(P, scores_by_week, min_names=MIN_NAMES):
    out = {}
    for R in P['weeks']:
        sc = scores_by_week.get(R) or {}
        if len(sc) < min_names:
            continue
        ks = sorted(sc, key=str)
        ic = spearman([sc[k] for k in ks], [P['tokens'][k]['rows'][R]['ret'] for k in ks])
        if ic is not None:
            out[R] = ic
    return out


def summarize(rows, lo=None, hi=None):
    sel = [r for r in rows if r['active'] and (lo is None or r['R'] >= lo) and (hi is None or r['R'] < hi)]
    x = [r['net'] for r in sel]
    if not x:
        return {'n': 0}
    p = B.perf(x, PPY)
    t, pv = B.newey_west_t(x)
    p.update({'nw_t': t, 'nw_p': pv,
              'gross_ann': statistics.fmean(r['gross'] for r in sel) * PPY,
              'funding_ann': statistics.fmean(r['funding'] for r in sel) * PPY,
              'cost_ann': statistics.fmean(r['cost'] for r in sel) * PPY,
              'turnover_wk': statistics.fmean(r['turnover'] for r in sel),
              'names_per_leg': statistics.fmean(r['k'] for r in sel if 'k' in r) if any('k' in r for r in sel) else None,
              'first': dstr(sel[0]['R']), 'last': dstr(sel[-1]['R']),
              'excess_over_ssr': p['ann_return'] - SSR})
    return p


# ---------------------------------------------------------------------------------------------- analysis: the framework's detectors, replayed

def complete(series, today):
    """Only days strictly before `today`: the current UTC day is a partial reading."""
    return {d: v for d, v in series.items() if d < today}


def surge_replay(daily, recent=1, weekday=True, base_days=SURGE['base_days'], history=SURGE['history'],
                 min_history=SURGE['min_history']):
    """chain_activity.surge_stats evaluated at every position of a {day: value} series as if the series ended there:
    [{'day', 'recent', 'base', 'ratio', 'delta', 'p_up'}]. Positions are the series' own days (a missing day is
    skipped, as the framework skips it), so each reading uses nothing after its own day."""
    days = sorted(daily)
    vals = [float(daily[d] or 0) for d in days]
    n = len(vals)
    at = [None] * n
    for i in range(n):
        if i - recent + 1 < 0:
            continue
        rec = vals[i - recent + 1:i + 1]
        base = vals[max(0, i - recent - base_days + 1):i - recent + 1]
        if len(base) < min_history:
            continue
        r = sum(rec) / len(rec)
        b = statistics.median(base) if recent == 1 else sum(base) / len(base)
        ratio = (r / b) if b > 0 else (math.inf if r > 0 else 1.0)
        if recent == 1 and weekday:
            same = [base[j] for j in range(len(base) - 7, -1, -7)]
            bw = statistics.median(same) if same else None
            if bw and bw > 0:
                ratio = min(ratio, r / bw)
        at[i] = (r, b, ratio)
    out = []
    need = recent + max(base_days // 2, min_history)
    window = []                       # sorted ratios at positions [i - history, i - 1]
    for i in range(n):
        if i - history - 1 >= 0 and at[i - history - 1] is not None:
            del window[bisect.bisect_left(window, at[i - history - 1][2])]
        if i + 1 >= need and at[i] is not None:
            k_up = len(window) - bisect.bisect_left(window, at[i][2])
            out.append({'day': days[i], 'recent': at[i][0], 'base': at[i][1], 'ratio': at[i][2],
                        'delta': at[i][0] - at[i][1], 'p_up': (k_up + 1) / (len(window) + 1)})
        if at[i] is not None:
            bisect.insort(window, at[i][2])
    return out


def stable_replay(daily):
    """det_stable_inflow at every position: +max($25M, 10%) over 7 readings, else +max($50M, 30%) over 30."""
    days = sorted(daily)
    vals = [daily[d] for d in days]
    out = []
    for i in range(len(vals)):
        if i >= 7:
            cur, wk = vals[i], vals[i - 7]
            if cur - wk >= max(STABLE_7D[0], STABLE_7D[1] * wk):
                out.append({'day': days[i], 'kind': '7d', 'change': cur - wk, 'before': wk})
                continue
        if i >= 30:
            cur, mo = vals[i], vals[i - 30]
            if cur - mo >= max(STABLE_30D[0], STABLE_30D[1] * mo):
                out.append({'day': days[i], 'kind': '30d', 'change': cur - mo, 'before': mo})
    return out


def replay_events(out, P):
    """Every day each chain of a perp-traded chain token would have fired the framework's chain_surge (DEX, fees d1/d7,
    TVL d7; not market-wide) or stable_inflow detectors, first fire per token and type in any 28 days."""
    raw = Path(out) / 'raw' / 'llama' / 'chain'
    today = utc_now().date().toordinal() - dt.date(1970, 1, 1).toordinal()
    owner = {}
    for key, tk in P['tokens'].items():
        if key[0] == 'chains':
            for c in tk['chains'] or []:
                owner[c] = key
    stats, seen = {}, set()
    for c in sorted(owner):
        for m in ('dex', 'fees', 'tvl'):
            p = raw / safe(c) / (m + '.json.gz')
            if not p.exists():
                continue
            d = read_gz(p)
            series = complete(chart_series(d.get('totalDataChart') if isinstance(d, dict) else d), today)
            sig = (owner[c], m, hash(tuple(sorted(series.items()))))
            if not series or sig in seen:          # one chain listed under two names counts once
                continue
            seen.add(sig)
            for recent in ((7,) if m == 'tvl' else (1, 7)):
                stats[(c, m, recent)] = {x['day']: x for x in surge_replay(series, recent, weekday=(m != 'tvl'))}
    market = collections.defaultdict(list)
    for (c, m, recent), by_day in stats.items():
        for d, x in by_day.items():
            if math.isfinite(x['ratio']):
                market[(m, recent, d)].append(x['ratio'])
    market = {k: statistics.median(v) for k, v in market.items() if len(v) >= 8}
    raw_events = []
    for (c, m, recent), by_day in stats.items():
        floor = SURGE['floors'][m]
        mr = SURGE['d1_min_ratio'] if recent == 1 else SURGE['d7_min_ratio']
        for d, x in sorted(by_day.items()):
            if not (x['ratio'] >= mr and x['p_up'] <= SURGE['max_p'] and x['delta'] >= floor):
                continue
            mk = market.get((m, recent, d))
            excess = (x['ratio'] / mk) if (mk and math.isfinite(x['ratio'])) else x['ratio']
            if excess < SURGE['market_excess']:
                continue
            raw_events.append({'type': m + '_surge', 'chain': c, 'token': owner[c], 'day': d, 'window': 'd%d' % recent,
                               'ratio': x['ratio'], 'delta': x['delta'], 'market_ratio': mk})
    for c, key in sorted(owner.items()):
        p = raw / safe(c) / 'stables.json.gz'
        if p.exists():
            st = complete(chart_series(read_gz(p)), today)
            sig = (key, 'stables', hash(tuple(sorted(st.items()))))
            if not st or sig in seen:
                continue
            seen.add(sig)
            for x in stable_replay(st):
                raw_events.append({'type': 'stable_inflow', 'chain': c, 'token': key, 'day': x['day'],
                                   'window': x['kind'], 'change': x['change'], 'before': x['before']})
    raw_events.sort(key=lambda e: (e['token'], e['type'], e['day']))
    events, last = [], {}
    for e in raw_events:
        k = (e['token'], e['type'])
        if k in last and e['day'] - last[k] < EVENT_REFRACTORY:
            continue
        last[k] = e['day']
        events.append(e)
    return events, len(raw_events)


def event_trade(P, key, D, h, cost_bps=COST_SIDE_BPS, cost_btc_bps=COST_BTC_BPS, raw=None, cache=None):
    """Long the token and short BTC from the close of D+1 (one full day after the data day) to the close of D+1+h."""
    tk = P['tokens'].get(key)
    if not tk:
        return None
    vs = cache['vs'].get(key)
    if vs is None:
        vs = cache['vs'][key] = venue_series(raw, [{'venue': v.split(':')[0], 'symbol': v.split(':', 1)[1], 'scale': 1.0}
                                                   for v in tk['venues']])
    e0, e1 = D + 1, D + 1 + h
    if e1 > P.get('last_complete', e1):
        return None                     # the exit close has not printed yet
    for vkey, sc, prim, c, q in vs:
        c0 = c.get(e0)
        if not c0:
            continue
        c1 = next((c[d] for d in range(e1, e0, -1) if c.get(d)), None)
        if c1 is None:
            return None
        if not liquid(vs, vkey, e0 + 1):
            return None
        b0, b1 = cache['btc'].get(e0), cache['btc'].get(e1)
        if not b0 or not b1:
            return None
        if vkey not in cache['fund']:
            cache['fund'][vkey] = load_funding(raw, vkey)
        t0, t1 = (e0 + 1) * DAY_MS, (e1 + 1) * DAY_MS
        f = cache['fund'][vkey].window(t0, t1) or 0.0
        fb = cache['btc_f'].window(t0, t1) or 0.0
        r, rb = c1 / c0 - 1.0, b1 / b0 - 1.0
        cost = 2 * (cost_bps + cost_btc_bps) / 1e4
        out = {'ret': r, 'btc': rb, 'abnormal': r - rb, 'funding': -f + fb, 'cost': cost, 'pnl': r - rb - f + fb - cost}
        bk = basket_return(P, key, e0, e1, raw, cache)
        if bk is not None:
            # against every other liquid chain token over the same days: the time effect a same-token placebo leaves in
            out.update({'basket': bk, 'abnormal_basket': r - bk, 'funding_basket': -f,
                        'pnl_basket': r - bk - f - 4 * cost_bps / 1e4})
        return out
    return None


def basket_return(P, key, e0, e1, raw, cache):
    """Equal-weight simple return, close of e0 to close of e1, of the other chain tokens liquid at e0 (None under 9)."""
    ck = (e0, e1)
    if ck not in cache.setdefault('basket', {}):
        rets = {}
        for k, tk in P['tokens'].items():
            if k[0] != 'chains':
                continue
            vs = cache['vs'].get(k)
            if vs is None:
                vs = cache['vs'][k] = venue_series(raw, [{'venue': v.split(':')[0], 'symbol': v.split(':', 1)[1], 'scale': 1.0}
                                                         for v in tk['venues']])
            for vkey, sc, prim, c, q in vs:
                a = c.get(e0)
                if not a:
                    continue
                b = next((c[d] for d in range(e1, e0, -1) if c.get(d)), None)
                if b is not None and liquid(vs, vkey, e0 + 1):
                    rets[k] = b / a - 1.0
                break
        cache['basket'][ck] = rets
    rets = cache['basket'][ck]
    others = [v for k, v in rets.items() if k != key]
    return (sum(others) / len(others)) if len(others) >= MIN_NAMES else None


def welch_t(x, y):
    if len(x) < 3 or len(y) < 3:
        return None
    vx, vy = statistics.variance(x) / len(x), statistics.variance(y) / len(y)
    return (statistics.fmean(x) - statistics.fmean(y)) / math.sqrt(vx + vy) if vx + vy > 0 else None


def tstat(x):
    if len(x) < 3:
        return None
    sd = statistics.stdev(x)
    return statistics.fmean(x) / (sd / math.sqrt(len(x))) if sd > 0 else None


def by_day_means(pairs):
    d = collections.defaultdict(list)
    for day, v in pairs:
        d[day].append(v)
    return [statistics.fmean(v) for _, v in sorted(d.items())]


def pvalue(t):
    return None if t is None else 2.0 * (1.0 - statistics.NormalDist().cdf(abs(t)))


def event_study(out, P, cut):
    raw = Path(out) / 'raw'
    events, n_raw = replay_events(out, P)
    btc_vs = venue_series(raw, [{'venue': 'binance', 'symbol': 'BTCUSDT', 'scale': 1.0}])
    cache = {'vs': {}, 'fund': {}, 'btc': btc_vs[0][3] if btc_vs else {}, 'btc_f': load_funding(raw, 'binance:BTCUSDT')}
    by_tok_type = collections.defaultdict(list)
    for e in events:
        by_tok_type[(e['token'], e['type'])].append(e['day'])
    variants = []
    trades = {}
    for typ in EVENT_TYPES:
        for h in EVENT_HORIZONS:
            tr, pl = [], []
            for e in events:
                if e['type'] != typ:
                    continue
                x = event_trade(P, e['token'], e['day'], h, raw=raw, cache=cache)
                if x:
                    tr.append((e, x))
                for sh in (-PLACEBO_SHIFT, PLACEBO_SHIFT):
                    Dp = e['day'] + sh
                    if any(abs(Dp - d) < 14 for d in by_tok_type[(e['token'], typ)]):
                        continue
                    y = event_trade(P, e['token'], Dp, h, raw=raw, cache=cache)
                    if y:
                        pl.append((Dp, y))
            trades[(typ, h)] = (tr, pl)
    hedges = (('btc', 'pnl', 'abnormal', 'funding'), ('basket', 'pnl_basket', 'abnormal_basket', 'funding_basket'))
    for typ, h, (hedge, pk, ak, fk) in ((t, h, x) for t in EVENT_TYPES for h in EVENT_HORIZONS for x in hedges):
        tr0, pl0 = trades[(typ, h)]
        tr = [(e, dict(x, pnl=x[pk], abnormal=x[ak], funding=x[fk])) for e, x in tr0 if pk in x]
        pl = [(d, dict(y, pnl=y[pk])) for d, y in pl0 if pk in y]
        ins = [x['pnl'] for e, x in tr if e['day'] < cut]
        oos = [x['pnl'] for e, x in tr if e['day'] >= cut]
        p_in = [y['pnl'] for d, y in pl if d < cut]
        p_out = [y['pnl'] for d, y in pl if d >= cut]
        variants.append({
            'type': typ, 'horizon_days': h, 'hedge': hedge, 'n_in': len(ins), 'n_out': len(oos),
            'mean_in': statistics.fmean(ins) if ins else None, 'mean_out': statistics.fmean(oos) if oos else None,
            'placebo_n_in': len(p_in), 'placebo_n_out': len(p_out),
            'placebo_mean_in': statistics.fmean(p_in) if p_in else None,
            'placebo_mean_out': statistics.fmean(p_out) if p_out else None,
            'excess_t_in': welch_t(ins, p_in), 'excess_t_out': welch_t(oos, p_out),
            't_in_by_day': tstat(by_day_means([(e['day'], x['pnl']) for e, x in tr if e['day'] < cut])),
            't_out_by_day': tstat(by_day_means([(e['day'], x['pnl']) for e, x in tr if e['day'] >= cut])),
            'hit_out': (sum(1 for v in oos if v > 0) / len(oos)) if oos else None,
            'abnormal_out': statistics.fmean(x['abnormal'] for e, x in tr if e['day'] >= cut) if oos else None,
            'funding_out': statistics.fmean(x['funding'] for e, x in tr if e['day'] >= cut) if oos else None,
            'tokens_out': len({e['token'] for e, x in tr if e['day'] >= cut}),
            'last_trades': [{'token': e['token'][1], 'chain': e['chain'], 'day': dstr(e['day']), 'window': e['window'],
                             'ratio': e.get('ratio'), 'change': e.get('change'), 'pnl': x['pnl'],
                             'abnormal': x['abnormal']} for e, x in tr[-8:]]})
    # chosen on what a trader keeps: the in-sample P&L, averaged by event day first (events cluster on market days)
    eligible = [v for v in variants if v['n_in'] >= 15 and v['t_in_by_day'] is not None]
    chosen = max(eligible, key=lambda v: v['t_in_by_day']) if eligible else None
    rej, adj = B.bh([pvalue(v['t_out_by_day']) for v in variants], q=0.10)
    for v, r, a in zip(variants, rej, adj):
        v['bh_reject_out'], v['bh_adj_p_out'] = r, a
    rej, adj = B.bh([pvalue(v['excess_t_out']) for v in variants], q=0.10)
    for v, r, a in zip(variants, rej, adj):
        v['bh_reject_excess_out'], v['bh_adj_p_excess_out'] = r, a
    counts = collections.Counter(e['type'] for e in events)
    return {'events_raw_days': n_raw, 'events': len(events), 'by_type': dict(counts),
            'tokens_with_events': len({e['token'] for e in events}), 'cutoff': dstr(cut),
            'variants': variants, 'chosen': chosen,
            'rule': 'long the token perp from the close of D+1 to the close of D+1+h (D the data day), hedged with the same '
                    'notional of BTC or of an equal-weight basket of the other liquid chain tokens; costs %.0fbp a side on the '
                    'token, %.0fbp on BTC, %.0fbp on the basket; placebo: the same token %d days either side, skipped within 14 days '
                    'of a same-type event; chosen on the in-sample event-day t of the P&L' % (
                        COST_SIDE_BPS, COST_BTC_BPS, COST_SIDE_BPS, PLACEBO_SHIFT),
            'event_list_tail': [{**{k: v for k, v in e.items() if k != 'token'}, 'token': e['token'][1], 'day': dstr(e['day'])}
                                for e in sorted(events, key=lambda e: e['day'])[-40:]]}


# ---------------------------------------------------------------------------------------------- analysis: capacity, anecdotes

def book_cost_bps(levels, usd, mid):
    """Average price impact in bp of taking `usd` from one side of a book (levels [[px, size], ...] best first);
    None if the book is too thin."""
    left, cost_usd = usd, 0.0
    for px, sz in levels:
        px, sz = float(px), float(sz)
        take = min(left, px * sz)
        cost_usd += take * abs(px - mid) / mid
        left -= take
        if left <= 1e-9:
            return 1e4 * cost_usd / usd
    return None


def capacity_table(out, P, names, sizes=(25e3, 100e3, 250e3, 1e6)):
    p = Path(out) / 'raw' / 'books.json.gz'
    if not p.exists():
        return None
    books = read_gz(p)
    rows = []
    last = P['weeks'][-1]
    for key in names:
        tk = P['tokens'][key]
        vkey = (tk['rows'].get(last) or {}).get('venue')     # the venue the book would trade now
        if not vkey:
            continue
        venue, sym = vkey.split(':', 1)
        bk = (books.get('binance') or {}).get(sym) if venue == 'binance' else (books.get('hl') or {}).get(sym)
        if not bk or not bk.get('bids') or not bk.get('asks'):
            continue
        bid, ask = float(bk['bids'][0][0]), float(bk['asks'][0][0])
        mid = (bid + ask) / 2
        r = {'token': key[1], 'venue': vkey, 'half_spread_bps': 1e4 * (ask - bid) / 2 / mid}
        for s in sizes:
            a, b = book_cost_bps(bk['asks'], s, mid), book_cost_bps(bk['bids'], s, mid)
            r['cost_bps_%dk' % int(s / 1e3)] = (max(a, b) + 5.0) if (a is not None and b is not None) else None
        rows.append(r)
    return {'at': books.get('at'), 'taker_fee_bps': 5.0, 'names': rows,
            'median': {k: statistics.median([r[k] for r in rows if r.get(k) is not None]) if any(r.get(k) is not None for r in rows) else None
                       for k in ['half_spread_bps'] + ['cost_bps_%dk' % int(s / 1e3) for s in sizes]}}


ANECDOTES = (
    ('Starknet DEX volume x3.6 (first reading)', '2026-10-08', 'starknet'),
    ('Starknet DEX volume x4.1 (second day)', '2026-10-09', 'starknet'),
    ('TON DEX volume x3.6', '2026-10-09', 'the-open-network'),
    ('Cronos transactions x2.6, memecoin wave', '2026-10-08', 'crypto-com-chain'),
    ('Plasma stablecoins +$396M in 30 days', '2026-10-08', 'plasma'),
    ('XRPL stablecoins +$215M in 7 days', '2026-10-08', 'ripple'),
    ('X Layer USDC x7 in a week', '2026-10-08', 'okb'),
    ('Tempo stablecoins +$678M in 30 days (no token)', '2026-10-08', None),
    ('Arc stablecoins +$110M in 7 days (gas token is USDC)', '2026-10-08', None),
)


def anecdotes(out, P):
    raw = Path(out) / 'raw'
    books = read_gz(raw / 'books.json.gz') if (raw / 'books.json.gz').exists() else {}
    btc_vs = venue_series(raw, [{'venue': 'binance', 'symbol': 'BTCUSDT', 'scale': 1.0}])
    btc_c = btc_vs[0][3] if btc_vs else {}
    btc_live = (books.get('binance_last') or {}).get('BTCUSDT')
    rows = []
    for title, day, g in ANECDOTES:
        key = ('chains', g) if g else None
        tk = P['tokens'].get(key) if key else None
        r = {'event': title, 'data_day': day, 'token': g}
        if not tk:
            r['note'] = 'no perp in the universe' if g else 'no token'
            rows.append(r)
            continue
        allv = venue_series(raw, [{'venue': v.split(':')[0], 'symbol': v.split(':', 1)[1], 'scale': 1.0} for v in tk['venues']])
        if not allv:
            r['note'] = 'no traded bars'
            rows.append(r)
            continue
        vkey, _, _, c, _ = max(allv, key=lambda v: max(v[3]))   # the venue still trading
        venue, sym = vkey.split(':', 1)
        D = dnum(day)
        entry = D + 1                 # close of D+1: one full day after the data day
        c = {d: v for d, v in c.items() if d <= P['last_complete']}
        last = max(c) if c else None
        live = (books.get('binance_last') or {}).get(sym) if venue == 'binance' else (books.get('hl_mids') or {}).get(sym)
        r.update({'venue': vkey, 'entry_close_day': dstr(entry), 'last_close_day': dstr(last) if last else None,
                  'books_at': books.get('at')})
        if c.get(D) and live:
            r['move_since_data_day_close'] = live / c[D] - 1.0
            if btc_c.get(D) and btc_live:
                r['vs_btc_since_data_day_close'] = live / c[D] - btc_live / btc_c[D]
        if c.get(entry) and live:
            r['move_since_entry'] = live / c[entry] - 1.0
            if btc_c.get(entry) and btc_live:
                r['vs_btc_since_entry'] = live / c[entry] - btc_live / btc_c[entry]
        elif live:
            r['note'] = 'entry close (%s) not yet printed when the books were read' % dstr(entry)
        rows.append(r)
    return rows


# ---------------------------------------------------------------------------------------------- analysis: the protocol

def ic_summary(ic, lo=None, hi=None):
    x = [v for R, v in sorted(ic.items()) if (lo is None or R >= lo) and (hi is None or R < hi)]
    if not x:
        return {'n': 0}
    t, p = B.newey_west_t(x)
    return {'n': len(x), 'mean': statistics.fmean(x), 'nw_t': t, 'nw_p': p, 'positive_share': sum(1 for v in x if v > 0) / len(x)}


def ic_by_year(ic):
    by = collections.defaultdict(list)
    for R, v in ic.items():
        by[dstr(R)[:4]].append(v)
    return {y: {'n': len(v), 'mean': statistics.fmean(v)} for y, v in sorted(by.items())}


def ret_by_year(rows):
    by = collections.defaultdict(list)
    for r in rows:
        if r['active']:
            by[dstr(r['R'])[:4]].append(r['net'])
    return {y: {'n': len(v), 'ann_return': statistics.fmean(v) * PPY} for y, v in sorted(by.items())}


def placebo(P, scores, hedge, cut, reps=200, seed=7):
    """The signal shuffled across the week's tradable tokens, `reps` times: the book a meaningless ranking builds."""
    rng = random.Random(seed)
    full, oos, gross, gross_oos = [], [], [], []
    for _ in range(reps):
        sh = {}
        for R, sc in scores.items():
            ks = sorted(sc, key=str)
            vals = [sc[k] for k in ks]
            rng.shuffle(vals)
            sh[R] = dict(zip(ks, vals))
        rows = run_book(P, sh, hedge)
        a = summarize(rows)
        b = summarize(rows, lo=cut)
        if a.get('n'):
            full.append(a['ann_return'])
            gross.append(a['gross_ann'])
        if b.get('n'):
            oos.append(b['ann_return'])
            gross_oos.append(b['gross_ann'])
    q = lambda v, f: sorted(v)[int(f * (len(v) - 1))] if v else None  # noqa: E731
    # A shuffled ranking churns the whole book every week, so its net is mostly cost; gross is the fair null.
    return {'reps': reps, 'full_mean': statistics.fmean(full) if full else None, 'full_p05': q(full, 0.05),
            'full_p95': q(full, 0.95), 'gross_mean': statistics.fmean(gross) if gross else None,
            'gross_p05': q(gross, 0.05), 'gross_p95': q(gross, 0.95),
            'gross_oos_mean': statistics.fmean(gross_oos) if gross_oos else None,
            'gross_oos_p05': q(gross_oos, 0.05), 'gross_oos_p95': q(gross_oos, 0.95),
            'oos_mean': statistics.fmean(oos) if oos else None, 'oos_p05': q(oos, 0.05), 'oos_p95': q(oos, 0.95),
            'full_values': full, 'oos_values': oos, 'gross_values': gross, 'gross_oos_values': gross_oos}


def regress_on(y_rows, x_rows):
    xs = {r['R']: r['net'] for r in x_rows if r['active']}
    pairs = [(xs[r['R']], r['net']) for r in y_rows if r['active'] and r['R'] in xs]
    if len(pairs) < 20:
        return None
    x, y = [a for a, _ in pairs], [b for _, b in pairs]
    beta = ols_beta(x, y) or 0.0
    alpha = [b - beta * a for a, b in pairs]
    t, p = B.newey_west_t(alpha)
    corr = statistics.correlation(x, y) if len(x) > 2 else None
    return {'n': len(pairs), 'beta': beta, 'corr': corr, 'alpha_ann': statistics.fmean(alpha) * PPY, 'alpha_nw_t': t}


def signal_mom_corr(S, sig, mom):
    out = []
    for R, sc in S[sig].items():
        m = S[mom].get(R) or {}
        ks = [k for k in sc if k in m]
        if len(ks) >= MIN_NAMES:
            c = spearman([sc[k] for k in ks], [m[k] for k in ks])
            if c is not None:
                out.append(c)
    return statistics.fmean(out) if out else None


def dependence(P, scores, hedge, rows, cut, fam, top=3):
    """Out of sample: each token's summed gross contribution, the return without the `top` largest contributors,
    and the return by half-year — whether a result is a few tokens or a few months."""
    contrib = collections.Counter()
    for r in rows:
        if not r['active'] or r['R'] < cut or not r.get('k'):
            continue
        for g in r['long']:
            contrib[g] += P['tokens'][(fam, g)]['rows'][r['R']]['ret'] / r['k']
        for g in r['short']:
            contrib[g] -= P['tokens'][(fam, g)]['rows'][r['R']]['ret'] / r['k']
    lead = [g for g, _ in contrib.most_common(top)]
    halves = collections.defaultdict(list)
    for r in rows:
        if r['active'] and r['R'] >= cut:
            d = dstr(r['R'])
            halves[d[:4] + ('H1' if int(d[5:7]) <= 6 else 'H2')].append(r['net'])
    return {'top_contributors_oos': [[g, v] for g, v in contrib.most_common(top)],
            'oos_ann_without_top': summarize(run_book(P, scores, hedge, exclude={(fam, g) for g in lead}), lo=cut).get('ann_return'),
            'oos_ann_by_half_year': {k: statistics.fmean(v) * PPY for k, v in sorted(halves.items())}}


def family_analysis(out, P, S, fam, cands):
    cands = list(cands)
    variants = {(s, h): run_book(P, S[s], h) for s in cands + list(CONTROL_SIGNALS) for h in HEDGES}
    act = sorted({r['R'] for (s, h), rows in variants.items() if s in cands for r in rows if r['active']})
    if not act:
        return {'family': fam, 'error': 'no active week'}
    span = [R for R in P['weeks'] if act[0] <= R <= act[-1]]
    cut = span[B.cutoff_index(len(span), 0.5)]
    ics = {s: weekly_ic(P, S[s]) for s in cands + list(CONTROL_SIGNALS)}
    table = []
    for (s, h), rows in variants.items():
        table.append({'signal': s, 'hedge': h, 'candidate': s in cands,
                      'full': summarize(rows), 'in_sample': summarize(rows, hi=cut), 'out_of_sample': summarize(rows, lo=cut),
                      'ic_full': ic_summary(ics[s]), 'ic_in': ic_summary(ics[s], hi=cut), 'ic_out': ic_summary(ics[s], lo=cut),
                      'ic_by_year': ic_by_year(ics[s]) if h == 'dollar' else None, 'by_year': ret_by_year(rows),
                      'mean_names': statistics.fmean([len(v) for v in S[s].values() if len(v) >= MIN_NAMES]) if any(len(v) >= MIN_NAMES for v in S[s].values()) else 0,
                      'corr_with_mom_12w': signal_mom_corr(S, s, 'mom_12w') if s not in CONTROL_SIGNALS else None})
    cand_rows = [v for v in table if v['candidate']]
    ok = [v for v in cand_rows if v['in_sample'].get('n', 0) >= 26 and v['in_sample'].get('sharpe') is not None]
    chosen = max(ok, key=lambda v: v['in_sample']['sharpe']) if ok else None
    res = {'family': fam, 'cutoff': dstr(cut), 'first_week': dstr(span[0]), 'last_week': dstr(span[-1]),
           'weeks': len(span), 'n_candidates': len(cand_rows), 'table': table}
    if chosen:
        key = (chosen['signal'], chosen['hedge'])
        rows = variants[key]
        in_srs = [v['in_sample']['sharpe'] for v in ok]
        sr_std = statistics.pstdev(in_srs) / math.sqrt(PPY) if len(in_srs) > 1 else None
        ins = [r['net'] for r in rows if r['active'] and r['R'] < cut]
        oos_rank = sorted(cand_rows, key=lambda v: -(v['out_of_sample'].get('sharpe') or -1e9)).index(chosen) + 1
        sens = {}
        for c in COST_GRID_BPS:
            sens['%gbp' % c] = summarize(run_book(P, S[key[0]], key[1], cost_bps=c), lo=cut).get('ann_return')
        o = [r for r in rows if r['active'] and r['R'] >= cut]
        be = (1e4 * sum(r['gross'] + r['funding'] for r in o) / sum(r['turnover'] for r in o)) if o and sum(r['turnover'] for r in o) > 0 else None
        oos_names = sorted({(fam, g) for r in o for g in r.get('long', []) + r.get('short', [])}, key=str)
        drop = {}
        for k in oos_names:
            drop[k[1]] = summarize(run_book(P, S[key[0]], key[1], exclude={k}), lo=cut).get('ann_return')
        pl = placebo(P, S[key[0]], key[1], cut)
        actual_gross = chosen['full'].get('gross_ann')
        actual_gross_oos = chosen['out_of_sample'].get('gross_ann')
        res['chosen'] = {
            'signal': key[0], 'hedge': key[1], 'in_sample': chosen['in_sample'], 'out_of_sample': chosen['out_of_sample'],
            'oos_rank_by_sharpe': oos_rank, 'deflated_sharpe_in_sample': B.deflated_sharpe(ins, len(cand_rows), sr_std),
            'deflated_sharpe_in_sample_all_variants': B.deflated_sharpe(ins, N_VARIANTS_STUDY, sr_std),
            'ic_out': chosen['ic_out'], 'cost_sensitivity_oos_ann': sens, 'breakeven_cost_bps_per_side_oos': be,
            'drop_one_oos_ann': drop,
            'drop_one_range': [min(drop.values()), max(drop.values())] if drop else None,
            'placebo': {k: v for k, v in pl.items() if not k.endswith('_values')},
            'placebo_percentile_gross_full': (sum(1 for v in pl['gross_values'] if v < actual_gross) / len(pl['gross_values'])) if pl['gross_values'] and actual_gross is not None else None,
            'placebo_percentile_gross_oos': (sum(1 for v in pl['gross_oos_values'] if v < actual_gross_oos) / len(pl['gross_oos_values'])) if pl['gross_oos_values'] and actual_gross_oos is not None else None,
            'vs_momentum_12w': regress_on(rows, variants[('mom_12w', key[1])]),
            'vs_momentum_4w': regress_on(rows, variants[('mom_4w', key[1])]),
            'last_book': next(({'R': dstr(r['R']), 'long': r['long'], 'short': r['short']} for r in reversed(rows) if r['active'] and r.get('long')), None),
        }
    # walk-forward: choose on 104 weeks, hold the choice 26, roll by 26
    wf, wf_rows = [], []
    for tr_rng, te_rng in B.walk_forward(len(span), 104, 26):
        lo, mid, hi = span[tr_rng[0]], span[te_rng[0]], span[te_rng[-1]] + 1
        best, best_sr = None, None
        for (s, h), rows in variants.items():
            if s not in cands:
                continue
            st = summarize(rows, lo=lo, hi=mid)
            if st.get('n', 0) >= 26 and st.get('sharpe') is not None and (best_sr is None or st['sharpe'] > best_sr):
                best, best_sr = (s, h), st['sharpe']
        if not best:
            continue
        te = [r for r in variants[best] if r['active'] and mid <= r['R'] < hi]
        wf_rows += te
        wf.append({'test_from': dstr(mid), 'chosen': '%s/%s' % best, 'train_sharpe': best_sr,
                   'test_ann_return': (statistics.fmean(r['net'] for r in te) * PPY) if te else None, 'test_weeks': len(te)})
    res['walk_forward'] = {'windows': wf, 'summary': summarize(wf_rows) if wf_rows else {'n': 0}}
    # what a reader might pick with hindsight, labelled as such, with what it rests on
    best_oos = max(cand_rows, key=lambda v: v['out_of_sample'].get('sharpe') or -1e9)
    bkey = (best_oos['signal'], best_oos['hedge'])
    res['best_out_of_sample_hindsight'] = dict({'signal': bkey[0], 'hedge': bkey[1],
                                                'in_sample': best_oos['in_sample'],
                                                'out_of_sample': best_oos['out_of_sample'], 'ic_in': best_oos['ic_in'],
                                                'ic_out': best_oos['ic_out']},
                                               **dependence(P, S[bkey[0]], bkey[1], variants[bkey], cut, fam))
    res['_variants'] = variants
    return res


def untraded_bars(out):
    """Zero-volume bars in the universe's price files: Binance's flat post-delisting bars and Hyperliquid's
    pre-listing bars. Every reader drops them; this counts what was dropped."""
    uni = json.loads((Path(out) / 'universe.json').read_text())
    raw = Path(out) / 'raw'
    seen, res = set(), {'binance': {'pairs': 0, 'bars': 0, 'after_last_trade': 0}, 'hl': {'pairs': 0, 'bars': 0, 'before_first_trade': 0}}
    for fam in ('chains', 'protocols'):
        for t in uni[fam].values():
            for v in t['venues']:
                k = (v['venue'], v['symbol'])
                if k in seen:
                    continue
                seen.add(k)
                cl = load_closes(raw, v['venue'], v['symbol'])
                traded = sorted(d for d, (c, q) in cl.items() if q > 0)
                zero = [d for d, (c, q) in cl.items() if q <= 0]
                if not zero:
                    continue
                r = res[v['venue']]
                r['pairs'] += 1
                r['bars'] += len(zero)
                if traded and v['venue'] == 'binance':
                    r['after_last_trade'] += sum(1 for d in zero if d > traded[-1])
                if traded and v['venue'] == 'hl':
                    r['before_first_trade'] += sum(1 for d in zero if d < traded[0])
    return res


def cmd_analyze(args):
    out = Path(args.out)
    t0 = time.time()
    weeks = mondays(args.start, args.end)
    P = build_panel(out, weeks)
    F, total = load_fundamentals(out, P)
    print('panel: %d tokens, %d weeks (%.0fs)' % (len(P['tokens']), len(weeks), time.time() - t0), flush=True)
    res = {'generated': utc_now().isoformat(timespec='seconds'), 'weeks': [dstr(weeks[0]), dstr(weeks[-1])],
           'settings': {'cost_side_bps': COST_SIDE_BPS, 'cost_btc_bps': COST_BTC_BPS, 'liquidity_min_usd': LIQ_MIN_USD,
                        'min_names': MIN_NAMES, 'lag_days': LAG_DAYS, 'floors': FLOORS, 'beta_days': BETA_DAYS,
                        'ssr': SSR, 'periods_per_year': PPY, 'surge': SURGE, 'stable_7d': STABLE_7D, 'stable_30d': STABLE_30D},
           'missing_funding_token_weeks': P['missing_funding_weeks'],
           'excluded_from_protocol_family': P['excluded_protocols']}
    fams = {}
    for fam, cands in (('chains', list(CHAIN_SIGNALS)), ('protocols', list(PROTOCOL_SIGNALS))):
        S = weekly_scores(P, F, total, fam)
        fa = family_analysis(out, P, S, fam, cands)
        variants = fa.pop('_variants', {})
        fams[fam] = (fa, S, variants)
        res[fam] = fa
        ntok = len({k for R in S[cands[0]] for k in S[cands[0]][R]})
        res[fam]['tokens_ever_tradable'] = len({k for k, tk in P['tokens'].items() if k[0] == fam and any(r['liquid'] for r in tk['rows'].values())})
        res[fam]['tokens_with_signal_' + cands[0]] = ntok
        c = fa.get('chosen') or {}
        print('%s: chosen %s/%s  in %s  out %s (t %s)  (%.0fs)' % (
            fam, c.get('signal'), c.get('hedge'), pct((c.get('in_sample') or {}).get('ann_return')),
            pct((c.get('out_of_sample') or {}).get('ann_return')), f2((c.get('out_of_sample') or {}).get('nw_t')),
            time.time() - t0), flush=True)
    # one false-discovery count over every candidate variant of both families
    allv = [(fam, v) for fam in ('chains', 'protocols') for v in res[fam].get('table', []) if v['candidate']]
    for lab, part in (('full', 'full'), ('out_of_sample', 'out_of_sample')):
        rej, adj = B.bh([v[part].get('nw_p') for _, v in allv], q=0.10)
        res['bh_%s' % lab] = {'n_variants': len(allv),
                              'survivors': ['%s:%s/%s' % (f, v['signal'], v['hedge']) for (f, v), r in zip(allv, rej) if r],
                              'min_adjusted_p': min((a for a in adj if a is not None), default=None)}
    # the same count on the rank IC (dollar rows: the IC does not depend on the hedge)
    icv = [(fam, v) for fam, v in allv if v['hedge'] == 'dollar']
    for lab, part in (('in', 'ic_in'), ('out', 'ic_out')):
        rej, adj = B.bh([v[part].get('nw_p') for _, v in icv], q=0.10)
        res['bh_ic_%s' % lab] = {'n_signals': len(icv), 'adjusted_p': {'%s:%s' % (f, v['signal']): a for (f, v), a in zip(icv, adj)},
                                 'survivors': ['%s:%s' % (f, v['signal']) for (f, v), r in zip(icv, rej) if r]}
    res['data'] = {'tokens_in_panel': len(P['tokens']), 'excluded_protocols': len(P['excluded_protocols']),
                   'last_complete_day': dstr(P['last_complete']), 'untraded_bars_dropped': untraded_bars(out)}
    cut = dnum(res['chains']['cutoff']) if res['chains'].get('cutoff') else dnum('2024-01-01')
    res['events'] = event_study(out, P, cut)
    ev = res['events']
    print('events: %d (%s); chosen %s' % (ev['events'], ev['by_type'], ev['chosen'] and (ev['chosen']['type'], ev['chosen']['horizon_days'], ev['chosen']['hedge'])), flush=True)
    last = P['weeks'][-1]
    for fam in ('chains', 'protocols'):
        names = [k for k, tk in P['tokens'].items() if k[0] == fam and (tk['rows'].get(last) or {}).get('liquid')]
        res[fam]['capacity_live_books'] = capacity_table(out, P, names)
    res['anecdotes'] = anecdotes(out, P)
    write_json(out / 'analysis.json', res)
    manifest_update(out, 'analyze', {'at': res['generated'], 'seconds': round(time.time() - t0, 1),
                                     'weeks': res['weeks'], 'tokens_in_panel': len(P['tokens']),
                                     'untraded_bars_dropped': res['data']['untraded_bars_dropped']})
    print('analysis.json written (%.0fs)' % (time.time() - t0))
    return 0


def pct(x, d=1):
    return '—' if x is None else '%+.*f%%' % (d, 100 * x)


def f2(x):
    return '—' if x is None else '%.2f' % x


# ---------------------------------------------------------------------------------------------- render

def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# Fundamentals factor — tables', '',
         'Generated %s from `analysis.json`. Weeks %s to %s (Mondays; each week earns Sunday close to Sunday close). '
         'Net = gross + funding − costs at %.0fbp a side on turnover (BTC hedge %.0fbp); $1 long and $1 short per $1 '
         'of capital; annualised with %.2f weeks a year. SSR benchmark %.2f%%.' % (
             A['generated'], A['weeks'][0], A['weeks'][1], A['settings']['cost_side_bps'], A['settings']['cost_btc_bps'],
             A['settings']['periods_per_year'], 100 * A['settings']['ssr']), '']
    for fam in ('chains', 'protocols'):
        R = A.get(fam) or {}
        if not R.get('table'):
            continue
        L += ['## %s: %d candidate variants, cutoff %s (in sample %s → %s, out of sample → %s)' % (
            fam, R['n_candidates'], R['cutoff'], R['first_week'], R['cutoff'], R['last_week']), '',
            'Tokens ever tradable: %d.' % R.get('tokens_ever_tradable', 0), '',
            '| signal | hedge | names/wk | in: ann | in: Sharpe | out: ann | out: Sharpe | out: NW t | IC in | IC out | IC out t | turnover/wk | out: funding | out: cost | corr mom12 |',
            '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for v in sorted(R['table'], key=lambda v: (not v['candidate'], v['signal'], v['hedge'])):
            i, o = v['in_sample'], v['out_of_sample']
            L.append('| %s%s | %s | %.1f | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                v['signal'], '' if v['candidate'] else ' (control)', v['hedge'], v['mean_names'] or 0,
                pct(i.get('ann_return')), f2(i.get('sharpe')), pct(o.get('ann_return')), f2(o.get('sharpe')),
                f2(o.get('nw_t')), f2(v['ic_in'].get('mean')), f2(v['ic_out'].get('mean')), f2(v['ic_out'].get('nw_t')),
                '—' if o.get('turnover_wk') is None else '%.2f' % o['turnover_wk'],
                pct(o.get('funding_ann')), pct(o.get('cost_ann')),
                f2(v.get('corr_with_mom_12w'))))
        c = R.get('chosen')
        if c:
            pl = c['placebo']
            vm = c.get('vs_momentum_12w') or {}
            L += ['', '**Chosen on the first half (best in-sample Sharpe): `%s` / %s.** In sample %s a year (Sharpe %s, %d weeks); '
                  'out of sample %s a year (Sharpe %s, NW t %s, %d weeks; rank %d of %d by out-of-sample Sharpe). Deflated Sharpe '
                  'of the in-sample choice: %s given %d family variants, %s given every variant in the study. '
                  'Out-of-sample net at 0/10/15/20/30bp a side: %s. Break-even cost %s bp a side. '
                  'Placebo (signal shuffled within week, %d reps): gross full-sample mean %s (5–95%%: %s to %s), gross out of sample %s '
                  '(5–95%%: %s to %s), net %s (it churns the book weekly); the real gross sits at the %s percentile in full and %s out of sample. '
                  'Drop-one-token range out of sample: %s to %s. '
                  'Against the same-hedge 12-week momentum book: beta %s, correlation %s, alpha %s a year (NW t %s).' % (
                      c['signal'], c['hedge'], pct(c['in_sample'].get('ann_return')), f2(c['in_sample'].get('sharpe')),
                      c['in_sample'].get('n', 0), pct(c['out_of_sample'].get('ann_return')), f2(c['out_of_sample'].get('sharpe')),
                      f2(c['out_of_sample'].get('nw_t')), c['out_of_sample'].get('n', 0), c['oos_rank_by_sharpe'], R['n_candidates'],
                      f2(c['deflated_sharpe_in_sample']), R['n_candidates'], f2(c['deflated_sharpe_in_sample_all_variants']),
                      ' / '.join(pct(v) for v in c['cost_sensitivity_oos_ann'].values()),
                      '—' if c['breakeven_cost_bps_per_side_oos'] is None else '%.1f' % c['breakeven_cost_bps_per_side_oos'],
                      pl['reps'], pct(pl['gross_mean']), pct(pl['gross_p05']), pct(pl['gross_p95']), pct(pl['gross_oos_mean']),
                      pct(pl['gross_oos_p05']), pct(pl['gross_oos_p95']), pct(pl['full_mean']),
                      '—' if c['placebo_percentile_gross_full'] is None else '%.0f%%' % (100 * c['placebo_percentile_gross_full']),
                      '—' if c['placebo_percentile_gross_oos'] is None else '%.0f%%' % (100 * c['placebo_percentile_gross_oos']),
                      pct((c['drop_one_range'] or [None])[0]), pct((c['drop_one_range'] or [None, None])[1]),
                      f2(vm.get('beta')), f2(vm.get('corr')), pct(vm.get('alpha_ann')), f2(vm.get('alpha_nw_t')))]
        b = R.get('best_out_of_sample_hindsight') or {}
        L += ['', 'Best out of sample with hindsight (not a test): `%s` / %s, %s a year (NW t %s; in sample %s); rank IC out of '
              'sample %s (t %s). Without its top three contributors (%s) %s; by half-year %s.' % (
                  b.get('signal'), b.get('hedge'), pct((b.get('out_of_sample') or {}).get('ann_return')),
                  f2((b.get('out_of_sample') or {}).get('nw_t')), pct((b.get('in_sample') or {}).get('ann_return')),
                  f2((b.get('ic_out') or {}).get('mean')), f2((b.get('ic_out') or {}).get('nw_t')),
                  ', '.join(g for g, _ in b.get('top_contributors_oos') or []), pct(b.get('oos_ann_without_top')),
                  ', '.join('%s %s' % (k, pct(v)) for k, v in (b.get('oos_ann_by_half_year') or {}).items())), '']
        years = sorted({y for v in R['table'] if v['ic_by_year'] for y in v['ic_by_year']})
        L += ['### Rank IC by year (signal vs next-week return)', '',
              '| signal | ' + ' | '.join(years) + ' |', '|---|' + '---:|' * len(years)]
        for v in R['table']:
            if v['hedge'] != 'dollar':
                continue
            L.append('| %s | %s |' % (v['signal'], ' | '.join(
                f2((v['ic_by_year'].get(y) or {}).get('mean')) for y in years)))
        L += ['', '### Walk-forward (choose on 104 weeks, hold 26)', '', '| test from | chosen | train Sharpe | test ann | weeks |',
              '|---|---|---:|---:|---:|']
        for w in R['walk_forward']['windows']:
            L.append('| %s | %s | %s | %s | %d |' % (w['test_from'], w['chosen'], f2(w['train_sharpe']),
                                                   pct(w['test_ann_return']), w['test_weeks']))
        s = R['walk_forward']['summary']
        L += ['', 'Walk-forward concatenated: %s a year, Sharpe %s, NW t %s over %d weeks.' % (
            pct(s.get('ann_return')), f2(s.get('sharpe')), f2(s.get('nw_t')), s.get('n', 0)), '']
        cap = R.get('capacity_live_books')
        if cap:
            L += ['Live books (%s): median cost per side including the 5bp taker fee, %s; median half-spread %s bp, over %d names.' % (
                cap['at'], ', '.join('%s %s' % (k.replace('cost_bps_', '$'), '—' if v is None else '%.1fbp' % v)
                                     for k, v in cap['median'].items() if k.startswith('cost')),
                f2(cap['median'].get('half_spread_bps')), len(cap['names'])), '']
    for lab in ('in', 'out'):
        b = A.get('bh_ic_' + lab) or {}
        L.append('Benjamini–Hochberg at q = 0.10 over the rank IC of %s signals (%s sample): survivors %s.' % (
            b.get('n_signals'), lab, b.get('survivors') or 'none'))
    for lab in ('full', 'out_of_sample'):
        b = A.get('bh_' + lab) or {}
        L.append('Benjamini–Hochberg at q = 0.10 over %s candidate variants (%s): survivors %s; smallest adjusted p %s.' % (
            b.get('n_variants'), lab.replace('_', ' '), b.get('survivors') or 'none', f2(b.get('min_adjusted_p'))))
    E = A.get('events') or {}
    if E:
        L += ['', '## The framework\'s "new activity", replayed: %d events on %d tokens (%s)' % (
            E['events'], E['tokens_with_events'], ', '.join('%s %d' % kv for kv in sorted(E['by_type'].items()))), '',
            E['rule'] + '; cutoff %s.' % E['cutoff'], '',
            '| event | days | hedge | n in | mean in | by-day t in | placebo in | n out | mean out | by-day t out | placebo out | excess t out | hit out | abnormal out | BH adj p out |',
            '|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for v in E['variants']:
            L.append('| %s | %d | %s | %d | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (
                v['type'], v['horizon_days'], v['hedge'], v['n_in'], pct(v['mean_in'], 2), f2(v['t_in_by_day']),
                pct(v['placebo_mean_in'], 2), v['n_out'], pct(v['mean_out'], 2), f2(v['t_out_by_day']),
                pct(v['placebo_mean_out'], 2), f2(v['excess_t_out']),
                '—' if v['hit_out'] is None else '%.0f%%' % (100 * v['hit_out']), pct(v['abnormal_out'], 2),
                f2(v.get('bh_adj_p_out'))))
        c = E.get('chosen')
        if c:
            L += ['', 'Chosen in sample (highest event-day t of the P&L): %s over %d days against %s — in %s a trade (by-day t %s; '
                  'placebo %s); out of sample %s (by-day t %s; placebo %s, excess t %s).' % (
                      c['type'], c['horizon_days'], c['hedge'], pct(c['mean_in'], 2), f2(c['t_in_by_day']),
                      pct(c['placebo_mean_in'], 2), pct(c['mean_out'], 2), f2(c['t_out_by_day']),
                      pct(c['placebo_mean_out'], 2), f2(c['excess_t_out']))]
    if A.get('anecdotes'):
        L += ['', '## Anecdotes (not evidence)', '', '| event | data day | token | since the data day close | vs BTC | since entry (close of D+1) | vs BTC | note |',
              '|---|---|---|---:|---:|---:|---:|---|']
        for r in A['anecdotes']:
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
                r['event'], r['data_day'], r.get('venue') or r.get('token') or '—', pct(r.get('move_since_data_day_close')),
                pct(r.get('vs_btc_since_data_day_close')), pct(r.get('move_since_entry')), pct(r.get('vs_btc_since_entry')),
                r.get('note') or ''))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:40]))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect', help='download and cache every input (resumable)')
    c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--step', default='all', help='all, or a comma list of: ' + ','.join(STEPS))
    a = sub.add_parser('analyze', help='weekly long/short books, the time split, walk-forward, placebo, events')
    a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--start', default='2020-01-06')
    a.add_argument('--end', default='2026-09-28', help='last Monday whose week is complete')
    r = sub.add_parser('render', help='tables.md from analysis.json')
    r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
