#!/usr/bin/env python3
"""Pendle fixed against floating, from the full history of every market that has matured — defaults included.

Why. The repo met Pendle only through windows: `detectors/fixed_vs_floating.py` classifies a live implied yield as a
term premium or a credit spread, and the book quotes PT-sUSDS at 4.97% against a 3.60% savings rate. A window can say
what the fixed rate is; it cannot say whether buying it was ever a good trade, because the answer arrives at maturity.
Pendle has now matured hundreds of markets, and a principal token held to maturity is the cleanest outcome in DeFi: it
pays exactly one unit of its accounting asset, so the fixed leg is known at entry and the only unknowns are what the
floating leg would have paid over the same days and whether the accounting asset was still worth one unit at the end.

What this measures, per matured market and entry day t (all in the market's own accounting unit unless stated):

  * **fixed**    the PT bought at t and held to expiry T returns (1 + implied_t)^(tau/365) - 1, tau = T - t in days,
                 less the AMM fee and the price impact of the size bought (Pendle's rate curve, `pt_buy_quote`);
  * **floating** holding the yield token instead returns the compounded realised `underlyingInterestApy` over [t, T]
                 (interest only: points and reward tokens are excluded and flagged);
  * **benchmark** for dollar markets, the Sky savings rate over [t, T], read from Pendle's own sUSDS/sDAI markets;
  * **recovery** the market price of the yield token at T over the SY price Pendle's history carries at T. Pendle's
                 history marks SY at the protocol's own exchange rate, so a stablecoin that collapsed keeps its
                 pre-collapse price in the API (Stream's xUSD sat at $1.2659 through its December 2025 expiry while
                 it traded at five cents). Recovery is what turns the API's fixed rate into what a holder got.

Then four strategy families, each chosen on the past and tested on the future (`backtest.py`):
  (a) unconditional PT minus floating, by asset class;  (b) buy PT when implied - trailing-7d floating > X;
  (c) long YT (interest only) when implied < trailing floating;  (d) dollar PT spread over the savings rate, by the
  spread at entry, after defaults.

    uv run python scripts/pendle_history.py collect --out research/2026-10-09/pendle_history
    uv run python scripts/pendle_history.py analyze --out research/2026-10-09/pendle_history
    uv run python scripts/pendle_history.py render  --out research/2026-10-09/pendle_history

Data. api-v2.pendle.finance (public, 200 computing units a minute, paced from its own rate-limit headers): the market
lists per chain, the flat asset list (which still carries markets the market lists have dropped, the November-2025
casualties among them), per-market metadata and the v3 daily history (implied, underlying interest and reward APY, PT
and SY prices, pool reserves, TVL, volume). Market prices of the yield tokens from DefiLlama's coins API, by contract
and, where DefiLlama has no contract price, by CoinGecko id. Everything raw is cached under `<out>/raw/` (gitignored).

Conventions. APYs are decimals (0.05 = 5%). Returns are simple over the holding period unless they say `_apr` (then
annualised by 365 / days, not compounded). `excess` is the PT's return minus the comparator's over the same days, so
positive means buying the PT won. A trade's capital is the price paid for it.
"""
import argparse
import collections
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

API = 'https://api-v2.pendle.finance/core'
LLAMA = 'https://coins.llama.fi'
COINGECKO = 'https://api.coingecko.com/api/v3'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) llm-quant research (read-only)'
DAY = 86400
FIELDS = ('timestamp,impliedApy,underlyingApy,underlyingInterestApy,underlyingRewardApy,ptPrice,syPrice,ytPrice,'
          'tvl,totalTvl,tradingVolume,totalPt,totalSy,swapFeeApy,pendleApy')

# DefiLlama's chain slugs and CoinGecko's platform ids for the chains Pendle lists.
LLAMA_CHAIN = {1: 'ethereum', 56: 'bsc', 143: 'monad', 196: 'xlayer', 999: 'hyperliquid', 4663: 'robinhood',
               8453: 'base', 9745: 'plasma', 42161: 'arbitrum', 10: 'optimism', 146: 'sonic', 5000: 'mantle',
               80094: 'berachain'}
CG_PLATFORM = {1: 'ethereum', 56: 'binance-smart-chain', 143: 'monad', 196: 'x-layer', 999: 'hyperevm',
               8453: 'base', 9745: 'plasma', 42161: 'arbitrum-one', 10: 'optimistic-ethereum', 146: 'sonic',
               5000: 'mantle', 80094: 'berachain'}


def utc(ts=None):
    return dt.datetime.fromtimestamp(time.time() if ts is None else ts, dt.timezone.utc).isoformat(timespec='seconds')


def iso_ts(s):
    """Unix seconds from an ISO string such as '2025-12-18T00:00:00.000Z'."""
    if s is None:
        return None
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())


def day_of(ts):
    return int(ts // DAY * DAY)


def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    if p.suffix == '.gz':
        with gzip.open(p, 'rt') as f:
            return json.load(f)
    return json.loads(p.read_text())


def write_json(path, obj, gz=False):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if gz:
        with gzip.open(p, 'wt') as f:
            json.dump(obj, f)
    else:
        p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str))


def fnum(v, d=None):
    try:
        x = float(v)
        return x if math.isfinite(x) else d
    except (TypeError, ValueError):
        return d


# --------------------------------------------------------------------------------------------------- HTTP

class Http:
    """Paced GET with retries. Pendle publishes its own budget in headers (`x-ratelimit-remaining`, reset as a unix
    second), so the client waits for the reset when the minute's budget runs low instead of discovering it as 429s."""

    def __init__(self, min_interval=0.2, retries=6, timeout=60):
        self.min_interval, self.retries, self.timeout = min_interval, retries, timeout
        self.next_at = 0.0
        self.stats = collections.Counter()

    def _observe(self, hdr):
        if hdr is None:
            return
        rem, reset = hdr.get('x-ratelimit-remaining'), hdr.get('x-ratelimit-reset')
        if rem is not None and reset is not None:
            try:
                if int(rem) < 15:
                    wait = max(0.0, int(reset) - time.time()) + 1.0
                    self.stats['budget_waits'] += 1
                    time.sleep(min(wait, 70.0))
            except ValueError:
                pass

    def get(self, url):
        last = None
        for attempt in range(self.retries):
            delay = self.next_at - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            self.next_at = time.monotonic() + self.min_interval
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
            self.stats['requests'] += 1
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    body = r.read()
                    self._observe(r.headers)
                    return 200, json.loads(body)
            except urllib.error.HTTPError as e:
                self._observe(e.headers)
                if e.code == 429 or e.code >= 500:
                    self.stats['throttled' if e.code == 429 else 'server_errors'] += 1
                    ra = e.headers.get('Retry-After') if e.headers else None
                    time.sleep(min(60.0, float(ra)) if ra and ra.isdigit() else min(30.0, 2.0 * 2 ** attempt))
                    last = 'HTTP %d' % e.code
                    continue
                try:
                    payload = json.loads(e.read())
                except Exception:  # noqa: BLE001 - an error body is only kept as a note
                    payload = {}
                self.stats['http_%d' % e.code] += 1
                return e.code, payload
            except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError) as e:
                self.stats['transport_errors'] += 1
                last = str(e)[:120]
                time.sleep(min(30.0, 1.5 * 2 ** attempt))
        return None, {'error': 'retry limit', 'last': last}


# --------------------------------------------------------------------------------------------------- collect

def market_key(chain, addr):
    return '%d-%s' % (int(chain), addr.lower())


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    http = Http(min_interval=args.interval)
    t0 = time.time()
    log = []

    def note(**kw):
        kw['at'] = utc()
        log.append(kw)
        print(json.dumps(kw), flush=True)

    # 1. The universe: market lists per chain, and the flat LP/PT/SY asset lists, which outlive de-listing.
    code, chains = http.get(API + '/v1/chains')
    chain_ids = sorted(chains.get('chainIds') or []) if code == 200 else sorted(LLAMA_CHAIN)
    lists = {}
    for c in chain_ids:
        for status in ('active', 'inactive'):
            p = raw / 'lists' / ('%d_%s.json' % (c, status))
            if not p.exists() or args.refresh_lists:
                code, d = http.get('%s/v1/%d/markets/%s' % (API, c, status))
                if code != 200:
                    note(step='list', chain=c, status=status, code=code)
                    continue
                write_json(p, d)
            lists[(c, status)] = read_json(p).get('markets', [])
    assets = {}
    for typ in ('PENDLE_LP', 'PT', 'SY', 'YT'):
        p = raw / 'lists' / ('assets_%s.json' % typ)
        if not p.exists() or args.refresh_lists:
            code, d = http.get('%s/v1/assets/all?type=%s' % (API, typ))
            if code != 200:
                note(step='assets', type=typ, code=code)
                continue
            write_json(p, d)
        assets[typ] = read_json(p).get('assets', [])

    universe = {}
    for (c, status), ms in lists.items():
        for m in ms:
            k = market_key(c, m['address'])
            universe[k] = {'key': k, 'chain': c, 'address': m['address'].lower(), 'expiry': m.get('expiry'),
                           'name': m.get('name'), 'listed': status, 'categoryIds': m.get('categoryIds') or [],
                           'list_underlying': m.get('underlyingAsset'), 'list_pt': m.get('pt'),
                           'list_feeRate': (m.get('details') or {}).get('feeRate')}
    for lp in assets.get('PENDLE_LP', []):
        k = market_key(lp['chainId'], lp['address'])
        if k not in universe:
            universe[k] = {'key': k, 'chain': int(lp['chainId']), 'address': lp['address'].lower(),
                           'expiry': lp.get('expiry'), 'name': lp.get('name'), 'listed': 'asset_list_only',
                           'categoryIds': [], 'list_underlying': None, 'list_pt': None, 'list_feeRate': None}
    note(step='universe', markets=len(universe), listed=sum(1 for u in universe.values() if u['listed'] != 'asset_list_only'),
         asset_list_only=sum(1 for u in universe.values() if u['listed'] == 'asset_list_only'))
    write_json(out / 'universe.json', {'collected_at': utc(t0), 'markets': sorted(universe.values(), key=lambda u: u['key'])})

    # 2. Per market: metadata and the daily history. Both are cached; a 404 is cached as the answer it is.
    keys = sorted(universe)
    for i, k in enumerate(keys, 1):
        u = universe[k]
        mp = raw / 'meta' / (k + '.json')
        if not mp.exists():
            code, d = http.get('%s/v1/%d/markets/%s' % (API, u['chain'], u['address']))
            write_json(mp, {'code': code, 'body': d})
        hp = raw / 'hist' / (k + '.json.gz')
        if not hp.exists():
            url = '%s/v3/%d/markets/%s/historical-data?time_frame=day&fields=%s' % (API, u['chain'], u['address'], FIELDS)
            code, d = http.get(url)
            write_json(hp, {'code': code, 'body': d}, gz=True)
        if i % 50 == 0:
            note(step='markets', done=i, of=len(keys), elapsed_s=round(time.time() - t0), **dict(http.stats))

    # 3. Market prices of every yield token and accounting asset that has metadata, from DefiLlama by contract.
    tokens = {}
    for k in keys:
        meta = (read_json(raw / 'meta' / (k + '.json')) or {}).get('body') or {}
        if not meta.get('address'):
            continue
        exp = iso_ts(meta.get('expiry'))
        born = iso_ts(meta.get('timestamp')) or (exp - 400 * DAY if exp else None)
        for role in ('underlyingAsset', 'accountingAsset'):
            a = meta.get(role) or {}
            if not a.get('address'):
                continue
            tk = market_key(a.get('chainId') or meta['chainId'], a['address'])
            t = tokens.setdefault(tk, {'chain': int(a.get('chainId') or meta['chainId']), 'address': a['address'].lower(),
                                       'symbol': a.get('symbol'), 'start': born, 'end': exp, 'markets': []})
            t['start'] = min(x for x in (t['start'], born) if x) if (t['start'] or born) else None
            t['end'] = max(x for x in (t['end'], exp) if x) if (t['end'] or exp) else None
            t['markets'].append(k)
    now = int(time.time())
    done = 0
    for tk, t in sorted(tokens.items()):
        pp = raw / 'prices' / (tk + '.json')
        if pp.exists():
            continue
        slug = LLAMA_CHAIN.get(t['chain'])
        if not slug or not t['start']:
            write_json(pp, {'source': None, 'prices': []})
            continue
        start = max(t['start'] - 2 * DAY, 1_600_000_000)
        end = min(now, (t['end'] or now) + 21 * DAY)
        write_json(pp, {'source': 'llama:%s:%s' % (slug, t['address']),
                        'prices': llama_chart(http, '%s:%s' % (slug, t['address']), start, end)})
        done += 1
        if done % 50 == 0:
            note(step='prices', done=done, of=len(tokens), **dict(http.stats))
    write_json(out / 'tokens.json', tokens)

    # 4. CoinGecko fallback for dollar yield tokens DefiLlama cannot price by contract: the defaults live here.
    fallback = 0
    for tk, t in sorted(tokens.items()):
        pp = raw / 'prices' / (tk + '.json')
        cur = read_json(pp) or {}
        if cur.get('prices') or cur.get('cg_tried'):
            continue
        if not needs_price_check(tk, t, universe, raw):
            continue
        plat = CG_PLATFORM.get(t['chain'])
        cg_id = None
        if plat:
            code, d = http.get('%s/coins/%s/contract/%s' % (COINGECKO, plat, t['address']))
            if code == 200:
                cg_id = d.get('id')
            time.sleep(args.cg_interval)
        prices = []
        if cg_id:
            start = max(t['start'] - 2 * DAY, 1_600_000_000)
            end = min(now, (t['end'] or now) + 21 * DAY)
            prices = llama_chart(http, 'coingecko:%s' % cg_id, start, end)
        write_json(pp, {'source': ('llama:coingecko:%s' % cg_id) if cg_id else cur.get('source'), 'prices': prices,
                        'cg_tried': True, 'cg_id': cg_id})
        fallback += 1
    note(step='coingecko_fallback', tried=fallback)

    hist_codes = collections.Counter()
    meta_codes = collections.Counter()
    for k in keys:
        hist_codes[str((read_json(raw / 'hist' / (k + '.json.gz')) or {}).get('code'))] += 1
        meta_codes[str((read_json(raw / 'meta' / (k + '.json')) or {}).get('code'))] += 1
    priced = sum(1 for tk in tokens if (read_json(raw / 'prices' / (tk + '.json')) or {}).get('prices'))
    man = {'collected_at': utc(t0), 'finished_at': utc(), 'seconds': round(time.time() - t0, 1),
           'sources': {'pendle_lists': API + '/v1/{chain}/markets/{active|inactive}',
                       'pendle_assets': API + '/v1/assets/all?type={PENDLE_LP|PT|SY|YT}',
                       'pendle_meta': API + '/v1/{chain}/markets/{address}',
                       'pendle_history': API + '/v3/{chain}/markets/{address}/historical-data?time_frame=day&fields=' + FIELDS,
                       'prices': LLAMA + '/chart/{chain}:{address} (fallback coingecko:{id} via ' + COINGECKO + '/coins/{platform}/contract/{address})'},
           'chains': chain_ids, 'markets': len(keys),
           'markets_listed': sum(1 for u in universe.values() if u['listed'] != 'asset_list_only'),
           'markets_asset_list_only': sum(1 for u in universe.values() if u['listed'] == 'asset_list_only'),
           'history_status': dict(hist_codes), 'meta_status': dict(meta_codes),
           'tokens': len(tokens), 'tokens_priced': priced, 'http': dict(http.stats), 'log_tail': log[-20:]}
    write_json(out / 'manifest.json', man)
    print(json.dumps({k: v for k, v in man.items() if k != 'log_tail'}, indent=1))
    return 0


def llama_chart(http, coin, start, end):
    """Daily prices for one coin between two unix seconds, in chunks DefiLlama accepts."""
    rows, s = [], start
    while s < end:
        span = min(400, int((end - s) // DAY) + 1)
        url = '%s/chart/%s?start=%d&span=%d&period=1d&searchWidth=43200' % (LLAMA, urllib.parse.quote(coin, safe=':,'), s, span)
        code, d = http.get(url)
        if code != 200:
            break
        pts = ((d.get('coins') or {}).get(coin) or {}).get('prices') or []
        rows.extend({'t': int(p['timestamp']), 'p': fnum(p.get('price'))} for p in pts if fnum(p.get('price')) is not None)
        s += span * DAY
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: r['t']):
        if r['t'] not in seen:
            seen.add(r['t'])
            out.append(r)
    return out


def needs_price_check(tk, t, universe, raw):
    """A token is worth a CoinGecko lookup when it backs a dollar market that once held real liquidity."""
    for k in t['markets']:
        u = universe.get(k) or {}
        meta = (read_json(raw / 'meta' / (k + '.json')) or {}).get('body') or {}
        if asset_class(meta.get('categoryIds') or u.get('categoryIds') or [], meta_name(meta, u)) not in ('stable', 'ethena'):
            continue
        h = ((read_json(raw / 'hist' / (k + '.json.gz')) or {}).get('body') or {}).get('results') or []
        if max((fnum(r.get('tvl'), 0) for r in h), default=0) >= 250_000:
            return True
    return False



# --------------------------------------------------------------------------------------------------- blocked markets

# Latest-state reads only (no archive needed): which SY, yield token and asset a blocked market uses, and the SY's
# current exchange rate. Public endpoints, no keys.
PUBLIC_RPC = {
    1: ['https://eth.drpc.org', 'https://ethereum-rpc.publicnode.com', 'https://1rpc.io/eth'],
    42161: ['https://arb1.arbitrum.io/rpc', 'https://arbitrum-one-rpc.publicnode.com'],
    8453: ['https://mainnet.base.org', 'https://base-rpc.publicnode.com'],
    56: ['https://bsc-dataseed.binance.org', 'https://bsc-rpc.publicnode.com'],
    10: ['https://mainnet.optimism.io', 'https://optimism-rpc.publicnode.com'],
    5000: ['https://rpc.mantle.xyz'], 146: ['https://rpc.soniclabs.com'], 999: ['https://rpc.hyperliquid.xyz/evm'],
    9745: ['https://rpc.plasma.to'], 80094: ['https://rpc.berachain.com'], 143: ['https://rpc.monad.xyz'],
    196: ['https://rpc.xlayer.tech'],
}
SEL = {'readTokens': '0x2c8ce6bc', 'yieldToken': '0x76d5de85', 'assetInfo': '0xa40bee50', 'exchangeRate': '0x3ba0b9a9'}

# The dollar benchmark's history: DefiLlama's yield series for Sky's sUSDS (the savings rate, from 2025-02-21 in that
# series) and sDAI (the DSR, since 2022-12), by pool id.
LLAMA_YIELDS = 'https://yields.llama.fi/chart/'
BENCH_POOLS = {'ssr': 'd8c4eff5-c8a9-46fc-a888-057c4c668e72', 'dsr': 'c8a24fee-ec00-4f38-86c0-9f6daebc4225'}


def cmd_bench(args):
    out = Path(args.out)
    http = Http(min_interval=0.5)
    for name, pool in BENCH_POOLS.items():
        code, d = http.get(LLAMA_YIELDS + pool)
        write_json(out / 'raw' / 'bench' / (name + '.json'), {'code': code, 'pool': pool, 'url': LLAMA_YIELDS + pool,
                                                            'data': (d or {}).get('data') if code == 200 else None})
        print(json.dumps({'bench': name, 'code': code, 'rows': len((d or {}).get('data') or [])}))
    man = read_json(out / 'manifest.json') or {}
    man['benchmark'] = {'fetched_at': utc(), 'sources': {k: LLAMA_YIELDS + v for k, v in BENCH_POOLS.items()}}
    write_json(out / 'manifest.json', man)
    return 0


def llama_rate_series(path):
    """{day: apy} from a DefiLlama yields chart file (percent in the file, decimals out), one value per UTC day."""
    d = read_json(path) or {}
    outd = {}
    for x in d.get('data') or []:
        t = iso_ts(x.get('timestamp'))
        v = fnum(x.get('apyBase'), fnum(x.get('apy')))
        if t is not None and v is not None:
            outd[day_of(t)] = v / 100.0
    return outd


def eth_call(chain, to, data, timeout=30):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [{'to': to, 'data': data}, 'latest']}).encode()
    last = None
    for ep in PUBLIC_RPC.get(chain, []):
        req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json', 'User-Agent': UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read())
            if 'error' in d:
                last = str(d['error'])[:120]
                continue
            return d.get('result')
        except Exception as e:  # noqa: BLE001 - try the next endpoint, keep the reason
            last = str(e)[:120]
    raise RuntimeError(last or 'no endpoint for chain %s' % chain)


def words(hexstr):
    h = (hexstr or '0x')[2:]
    return [h[i:i + 64] for i in range(0, len(h), 64)]


def addr_word(w):
    return '0x' + w[-40:]


def cmd_blocked(args):
    """Markets the API refuses ("market is unsafe"): their trades from the transactions endpoint, which still answers,
    their SY / yield token / asset from the chain, and the yield token's market price — enough to say who bought PTs
    there, at what rate, and what they got back."""
    out = Path(args.out)
    raw = out / 'raw'
    http = Http(min_interval=args.interval)
    uni = {u['key']: u for u in (read_json(out / 'universe.json') or {}).get('markets', [])}
    keys = [k for k in sorted(uni) if (read_json(raw / 'hist' / (k + '.json.gz')) or {}).get('code') not in (200, None)]
    print(json.dumps({'blocked': len(keys)}), flush=True)
    now = int(time.time())
    for i, k in enumerate(keys, 1):
        u = uni[k]
        tp = raw / 'tx' / (k + '.json.gz')
        if not tp.exists():
            rows, token, pages = [], None, 0
            while pages < 200:
                url = '%s/v5/%d/transactions/%s?limit=1000%s' % (API, u['chain'], u['address'],
                                                                ('&resumeToken=' + urllib.parse.quote(token)) if token else '')
                code, d = http.get(url)
                pages += 1
                if code != 200:
                    break
                res = d.get('results') or []
                rows.extend(res)
                token = d.get('resumeToken')
                if not res or not token or len(res) < 1000:
                    break
            write_json(tp, {'code': code, 'rows': rows, 'pages': pages}, gz=True)
        bp = raw / 'blocked' / (k + '.json')
        if not bp.exists():
            rec = {'key': k, 'chain': u['chain'], 'market': u['address']}
            try:
                w = words(eth_call(u['chain'], u['address'], SEL['readTokens']))
                rec['sy'], rec['pt'], rec['yt'] = addr_word(w[0]), addr_word(w[1]), addr_word(w[2])
                rec['yield_token'] = addr_word(words(eth_call(u['chain'], rec['sy'], SEL['yieldToken']))[0])
                ai = words(eth_call(u['chain'], rec['sy'], SEL['assetInfo']))
                rec['asset_type'], rec['asset'], rec['asset_decimals'] = int(ai[0], 16), addr_word(ai[1]), int(ai[2], 16)
                rec['exchange_rate_now'] = int(words(eth_call(u['chain'], rec['sy'], SEL['exchangeRate']))[0], 16) / 1e18
            except Exception as e:  # noqa: BLE001 - recorded, the market is reported as unresolved
                rec['error'] = str(e)[:160]
            write_json(bp, rec)
        rec = read_json(bp)
        if rec.get('yield_token'):
            tk = market_key(u['chain'], rec['yield_token'])
            pp = raw / 'prices' / (tk + '.json')
            if not pp.exists():
                exp = iso_ts(u.get('expiry')) or now
                start, end = exp - 400 * DAY, min(now, exp + 21 * DAY)
                slug = LLAMA_CHAIN.get(u['chain'])
                prices = llama_chart(http, '%s:%s' % (slug, rec['yield_token']), start, end) if slug else []
                src = 'llama:%s:%s' % (slug, rec['yield_token'])
                cg_id = None
                if not prices and CG_PLATFORM.get(u['chain']):
                    code, d = http.get('%s/coins/%s/contract/%s' % (COINGECKO, CG_PLATFORM[u['chain']], rec['yield_token']))
                    cg_id = d.get('id') if code == 200 else None
                    time.sleep(args.cg_interval)
                    if cg_id:
                        prices = llama_chart(http, 'coingecko:%s' % cg_id, start, end)
                        src = 'llama:coingecko:%s' % cg_id
                write_json(pp, {'source': src, 'prices': prices, 'cg_tried': True, 'cg_id': cg_id})
        if i % 10 == 0:
            print(json.dumps({'blocked_done': i, 'of': len(keys), **dict(http.stats)}), flush=True)
    man = read_json(out / 'manifest.json') or {}
    man['blocked'] = {'markets': len(keys), 'finished_at': utc(), 'http': dict(http.stats),
                      'sources': {'transactions': API + '/v5/{chain}/transactions/{market}?limit=1000&resumeToken=',
                                  'tokens': 'eth_call readTokens()/yieldToken()/assetInfo()/exchangeRate() at latest, public RPCs'}}
    write_json(out / 'manifest.json', man)
    return 0


# --------------------------------------------------------------------------------------------------- pure math

def meta_name(meta, u=None):
    for v in (meta.get('proName'), meta.get('simpleName'), (meta.get('pt') or {}).get('symbol'), (u or {}).get('name')):
        if v and v != 'PENDLE-LPT':
            return v
    return (u or {}).get('name') or ''


ETHENA_WORDS = ('usde', 'sena', 'ena')
ETH_WORDS = ('eth', 'steth', 'weeth', 'rseth', 'ezeth', 'reth', 'meth', 'cbeth', 'oseth', 'sweth', 'pufeth', 'lseth')
BTC_WORDS = ('btc',)
STABLE_WORDS = ('usd', 'dai', 'gho', 'frax', 'usdc', 'usdt', 'eur')


def asset_class(categories, name=''):
    """One class per market, from Pendle's category tags first and the name second.

    Ethena is split out of dollars because its floating rate is funding-driven and it is the largest single block of
    dollar PTs; a market tagged both is Ethena."""
    cats = set(categories or [])
    n = (name or '').lower()
    if 'ethena' in cats or any(w in n for w in ('usde', 'sena')):
        return 'ethena'
    if 'stables' in cats:
        return 'stable'
    if 'eth' in cats or 'lido' in cats:
        return 'eth'
    if 'btc' in cats:
        return 'btc'
    if 'hype' in cats:
        return 'hype'
    if any(w in n for w in BTC_WORDS):
        return 'btc'
    if any(w in n for w in ETH_WORDS):
        return 'eth'
    if any(w in n for w in STABLE_WORDS):
        return 'stable'
    return 'other'


def pt_fixed_return(implied_apy, days):
    """Held-to-maturity return of a PT bought at `implied_apy` with `days` left: Pendle prices PT at
    1 / (1 + implied)^(days/365) of its accounting asset, and it redeems for exactly 1."""
    if implied_apy is None or days is None or days <= 0 or implied_apy <= -1:
        return None
    return (1.0 + implied_apy) ** (days / 365.0) - 1.0


def compound_daily(apys):
    """Total return from compounding a run of daily annual yields, one day each."""
    g = 1.0
    for a in apys:
        g *= (1.0 + a) ** (1.0 / 365.0)
    return g - 1.0


def annualise(ret, days):
    """Simple annualisation used for every `_apr` field: total return x 365 / days."""
    if ret is None or not days:
        return None
    return ret * 365.0 / days


def logit(p):
    return math.log(p / (1.0 - p))


def pt_buy_quote(implied_apy, days, total_pt, total_asset, scalar_root, fee_rate, size_asset):
    """Implied APY a buyer of `size_asset` (accounting units of cash in) actually gets on Pendle's AMM.

    Pendle V2 (MarketMathCore): exchangeRate = PT per asset = ln(p/(1-p)) / rateScalar + rateAnchor, where p is the PT
    share of the pool (totalPt / (totalPt + totalAsset)) and rateScalar = scalarRoot x 365 / days. A trade executes at
    the post-trade proportion, and the fee divides the buyer's exchange rate by exp(lnFeeRate x days / 365). The anchor
    is solved from the observed implied rate, so only the change in proportion matters.

    Solved by fixed point: buying dPT costs dPT / exchangeRate(after) of asset. Returns (apy_after, pt_bought) or
    (None, None) when the pool cannot fill the size (proportion would leave (0, 1) or the rate would fall below 1).
    """
    if None in (implied_apy, days, total_pt, total_asset, scalar_root) or days <= 0 or total_pt <= 0 or total_asset <= 0:
        return None, None
    ln_fee = math.log(1.0 + (fee_rate or 0.0))
    t = days / 365.0
    scalar = scalar_root / t
    e0 = (1.0 + implied_apy) ** t
    n = total_pt + total_asset
    p0 = total_pt / n
    if not 0 < p0 < 1:
        return None, None
    l0 = logit(p0)
    dpt = size_asset * e0
    e = e0
    for _ in range(60):
        p = (total_pt - dpt) / n
        if not 0 < p < 1:
            return None, None
        e_pre = e0 + (logit(p) - l0) / scalar
        e = e_pre / math.exp(ln_fee * t)
        if e <= 1.0:
            return None, None
        new = size_asset * e
        if abs(new - dpt) < 1e-9 * max(1.0, dpt):
            dpt = new
            break
        dpt = new
    return e ** (1.0 / t) - 1.0, dpt


def recovery_ratio(prices, t_ref, sy_price_ref, window_days=21):
    """Market value of the yield token over the SY price Pendle carried, at maturity.

    The median over [t_ref - 1d, t_ref + window_days] of the market price (three weeks: what a holder who could wait
    would get), divided by the API's SY price at t_ref. Returns (ratio, n_points); (None, 0) without prices. A healthy
    market reads about 1.0 (DefiLlama's own noise is a few tenths of a percent); a collapsed one reads its recovery."""
    if not prices or not sy_price_ref:
        return None, 0
    lo, hi = t_ref - DAY, t_ref + window_days * DAY
    pts = [r['p'] for r in prices if lo <= r['t'] <= hi and r['p'] is not None]
    if not pts:
        return None, 0
    return statistics.median(pts) / sy_price_ref, len(pts)


def first_break(prices, sy_series, threshold=0.9, start=None, end=None):
    """First day the market price fell below `threshold` x the API's SY price: when a default became visible."""
    sy = {day_of(r['t']): r['p'] for r in sy_series if r.get('p')}
    for r in prices:
        d = day_of(r['t'])
        if (start and d < start) or (end and d > end):
            continue
        ref = sy.get(d)
        if ref and r['p'] is not None and r['p'] < threshold * ref:
            return d
    return None


def yt_interest_return(floating_ret, implied_apy, days, yield_fee=0.05):
    """Return on capital of a YT bought at `implied_apy` and held to expiry, interest only.

    A YT costs 1 - PT = 1 - (1+implied)^(-days/365) of the accounting asset and collects the floating interest on one
    unit over the same days, less Pendle's fee on YT yield (`yield_fee`). Points and reward tokens are excluded."""
    if floating_ret is None or implied_apy is None or days <= 0:
        return None
    cost = 1.0 - (1.0 + implied_apy) ** (-days / 365.0)
    if cost <= 1e-6:
        return None
    return floating_ret * (1.0 - yield_fee) / cost - 1.0



# --------------------------------------------------------------------------------------------------- analysis inputs

DOLLAR_CLASSES = ('stable', 'ethena')
SKY_SYMBOLS = ('susds', 'sdai')
USD_ACCOUNTING = ('usdc', 'usdt', 'dai', 'usds', 'usde', 'usdt0', 'usd₮0', 'frxusd', 'gho', 'pyusd', 'rlusd',
                  'usdtb', 'crvusd', 'lusd', 'usd0', 'usdg', 'fdusd', 'usdai')


def load_markets(out):
    """One record per market with its metadata and its daily rows, from the raw cache. Pure apart from reading."""
    raw = Path(out) / 'raw'
    uni = {u['key']: u for u in (read_json(Path(out) / 'universe.json') or {}).get('markets', [])}
    tokens = read_json(Path(out) / 'tokens.json') or {}
    markets = []
    for k, u in sorted(uni.items()):
        m = read_json(raw / 'meta' / (k + '.json')) or {}
        meta = m.get('body') if m.get('code') == 200 else {}
        meta = meta or {}
        h = read_json(raw / 'hist' / (k + '.json.gz')) or {}
        hist_ok = h.get('code') == 200
        rows = []
        for r in ((h.get('body') or {}).get('results') or []) if hist_ok else []:
            t = iso_ts(r.get('timestamp'))
            if t is None:
                continue
            rows.append({'t': day_of(t), 'implied': fnum(r.get('impliedApy')), 'und': fnum(r.get('underlyingApy')),
                         'und_int': fnum(r.get('underlyingInterestApy')), 'und_rew': fnum(r.get('underlyingRewardApy')),
                         'pt': fnum(r.get('ptPrice')), 'sy': fnum(r.get('syPrice')), 'yt': fnum(r.get('ytPrice')),
                         'tvl': fnum(r.get('tvl')), 'total_tvl': fnum(r.get('totalTvl')), 'vol': fnum(r.get('tradingVolume')),
                         'total_pt': fnum(r.get('totalPt')), 'total_sy': fnum(r.get('totalSy'))})
        rows.sort(key=lambda r: r['t'])
        cats = meta.get('categoryIds') or u.get('categoryIds') or []
        name = meta_name(meta, u)
        und = meta.get('underlyingAsset') or {}
        acct = meta.get('accountingAsset') or {}
        und_key = market_key(und.get('chainId') or u['chain'], und['address']) if und.get('address') else None
        acct_key = market_key(acct.get('chainId') or u['chain'], acct['address']) if acct.get('address') else None
        fee = fnum((meta.get('extendedInfo') or {}).get('feeRate'), fnum(u.get('list_feeRate')))
        cls = asset_class(cats, name)
        acct_usd = early_unit_price(rows, iso_ts(meta.get('expiry') or u.get('expiry')))
        if cls in DOLLAR_CLASSES and acct_usd is not None and not 0.8 <= acct_usd <= 1.25:
            # Tagged with a dollar issuer but priced like something else (sENA, rsENA): not a dollar market.
            cls = 'other'
        markets.append({
            'key': k, 'chain': u['chain'], 'address': u['address'], 'name': name, 'acct_usd_early': acct_usd,
            'protocol': meta.get('protocol'), 'cls': cls, 'points': 'points' in cats,
            'categories': cats, 'expiry': iso_ts(meta.get('expiry') or u.get('expiry')),
            'created': iso_ts(meta.get('timestamp')), 'listed': u.get('listed'),
            'meta_status': m.get('code'), 'meta_message': (m.get('body') or {}).get('message') if m.get('code') != 200 else None,
            'hist_status': h.get('code'), 'hist_message': (h.get('body') or {}).get('message') if not hist_ok else None,
            'fee_rate': fee, 'scalar_root': fnum(meta.get('scalarRoot')),
            'und_key': und_key, 'und_symbol': und.get('symbol'), 'acct_key': acct_key, 'acct_symbol': acct.get('symbol'),
            'rows': rows,
        })
    prices = {}
    for tk in tokens:
        pr = read_json(raw / 'prices' / (tk + '.json')) or {}
        prices[tk] = {'source': pr.get('source'), 'prices': pr.get('prices') or []}
    return markets, prices


def early_unit_price(rows, expiry, n=30):
    """Median USD price of the accounting unit over a market's first `n` rows, read from the rows themselves."""
    if not expiry:
        return None
    vals = []
    for r in rows[:n]:
        left = (expiry - r['t']) / DAY
        if left > 0 and r.get('pt') and r.get('implied') is not None and -0.5 < r['implied'] < 2.0:
            vals.append(r['pt'] * (1.0 + r['implied']) ** (left / 365.0))
    return statistics.median(vals) if vals else None


def by_day(rows, field):
    return {r['t']: r[field] for r in rows if r.get(field) is not None}


def series_on_days(m, field, start, end, fill=True):
    """Values of `field` for each day in [start, end), forward-filled from the last observation when `fill`."""
    d = by_day(m['rows'], field)
    out, last, have = [], None, 0
    day = start
    while day < end:
        if day in d:
            last = d[day]
            have += 1
        out.append(last if fill else d.get(day))
        day += DAY
    return out, have


def floating_over(m, t0, t1, field='und_int', clip=(-0.5, 2.0)):
    """Compounded realised floating return over [t0, t1) and the share of days actually observed."""
    vals, have = series_on_days(m, field, t0, t1)
    n = len(vals)
    if n == 0:
        return None, 0.0
    vals = [min(clip[1], max(clip[0], v)) if v is not None else None for v in vals]
    if any(v is None for v in vals):
        first = next((v for v in vals if v is not None), None)
        if first is None:
            return None, 0.0
        vals = [first if v is None else v for v in vals]
    return compound_daily(vals), have / n


def trailing_mean(m, t, field='und_int', days=7):
    d = by_day(m['rows'], field)
    xs = [d[t - k * DAY] for k in range(1, days + 1) if (t - k * DAY) in d]
    return sum(xs) / len(xs) if len(xs) >= max(3, days // 2) else None


def sky_benchmark(markets):
    """Daily Sky savings rate (SSR, and DSR before sUSDS existed) as the median underlying interest APY across Pendle's
    own sUSDS and sDAI markets on that day. Returns {day: apy}."""
    per_day = collections.defaultdict(list)
    for m in markets:
        if (m.get('und_symbol') or '').lower() not in SKY_SYMBOLS:
            continue
        for r in m['rows']:
            v = r.get('und_int')
            if v is not None and 0 <= v < 0.3:
                per_day[r['t']].append(v)
    return {d: statistics.median(v) for d, v in sorted(per_day.items())}


def combined_benchmark(out, markets, last_day):
    """Daily dollar benchmark: the savings rate from DefiLlama's sUSDS series where it exists, else the median of
    Pendle's own sUSDS/sDAI markets that day, else the DSR from DefiLlama's sDAI series; forward-filled day by day.
    Returns ({day: apy}, {day: source})."""
    raw = Path(out) / 'raw' / 'bench'
    ssr = llama_rate_series(raw / 'ssr.json')
    dsr = llama_rate_series(raw / 'dsr.json')
    pend = sky_benchmark(markets)
    starts = [min(x) for x in (ssr, dsr, pend) if x]
    if not starts:
        return {}, {}
    ssr_start = min(ssr) if ssr else None
    day = min(starts)
    last = {'ssr': None, 'pendle': None, 'dsr': None}
    bench, src = {}, {}
    while day <= last_day:
        for k, ser in (('ssr', ssr), ('pendle', pend), ('dsr', dsr)):
            if day in ser:
                last[k] = ser[day]
        if ssr_start is not None and day >= ssr_start and last['ssr'] is not None:
            bench[day], src[day] = last['ssr'], 'ssr'
        elif day in pend:
            bench[day], src[day] = pend[day], 'pendle_susds_sdai'
        elif last['dsr'] is not None:
            bench[day], src[day] = last['dsr'], 'dsr'
        day += DAY
    return bench, src


def bench_over(bench, t0, t1):
    """Compounded benchmark return over [t0, t1), forward-filling gaps; None before the first observation."""
    days = sorted(bench)
    if not days or t0 < days[0]:
        return None
    vals, last, day = [], None, t0
    idx = {d: bench[d] for d in days}
    # last observation at or before t0
    for d in days:
        if d <= t0:
            last = idx[d]
        else:
            break
    while day < t1:
        if day in idx:
            last = idx[day]
        vals.append(last)
        day += DAY
    return compound_daily(vals)


def asset_usd_price(row, days):
    """The accounting asset's USD price implied by the row itself: the PT trades at 1/(1+implied)^tau of it.

    The API writes impliedApy = -1 on a market's last day before expiry (and other sentinels on dead days); a row whose
    implied is outside (-50%, 200%) prices nothing and returns None."""
    imp = row.get('implied')
    if not row.get('pt') or imp is None or not (-0.5 < imp < 2.0) or days <= 0:
        return None
    return row['pt'] * (1.0 + imp) ** (days / 365.0)


def pool_in_asset(row, days):
    """(totalPt, totalAsset) of the pool in accounting units. totalSy is converted with the asset-per-SY rate implied
    by the API's own SY and PT prices; returns (None, None) when any input is missing."""
    p_asset = asset_usd_price(row, days)
    if not p_asset or not row.get('sy') or row.get('total_pt') is None or row.get('total_sy') is None:
        return None, None
    er = row['sy'] / p_asset
    return row['total_pt'], row['total_sy'] * er


def market_recovery(m, prices, t_ref=None):
    """Recovery at maturity and when a break first showed, with the checks that make the ratio trustworthy.

    The ratio is only trusted as a default when the same price series agreed with the API early in the market's life
    (median ratio within 3% over the first 30 observed days): that separates a collapse from a token mapping or unit
    error, which reads as a constant offset from day one."""
    out = {'ratio': None, 'n': 0, 'early_ratio': None, 'break_day': None, 'status': 'no_price', 'source': None}
    pr = prices.get(m.get('und_key') or '') or {}
    series = pr.get('prices') or []
    out['source'] = pr.get('source')
    sy_rows = [{'t': r['t'], 'p': r['sy']} for r in m['rows'] if r.get('sy')]
    if not series or not sy_rows:
        return out
    t_ref = t_ref or m['expiry']
    sy_at = by_day(m['rows'], 'sy')
    ref_day = max((d for d in sy_at if d <= t_ref), default=None)
    if ref_day is None:
        return out
    ratio, n = recovery_ratio(series, t_ref, sy_at[ref_day])
    out.update(ratio=ratio, n=n)
    early = []
    first_days = sorted(sy_at)[:30]
    pmap = {day_of(r['t']): r['p'] for r in series}
    for d in first_days:
        if d in pmap and sy_at[d]:
            early.append(pmap[d] / sy_at[d])
    out['early_ratio'] = statistics.median(early) if early else None
    out['break_day'] = first_break(series, sy_rows, 0.9, start=sorted(sy_at)[0], end=t_ref + 7 * DAY)
    # The token's own price must have fallen too. A rebasing token (aUSDC at $1) under a non-rebasing SY wrapper reads
    # a ratio that sinks by the interest the wrapper accrued, with nothing lost; a collapse moves the price itself.
    early_px = [pmap[d] for d in first_days if d in pmap]
    end_px = window_median(series, t_ref - DAY, t_ref + 21 * DAY)
    out['token_drop'] = (end_px / statistics.median(early_px)) if (early_px and end_px) else None
    if ratio is None:
        out['status'] = 'no_price_at_maturity'
    elif out['early_ratio'] is None or abs(out['early_ratio'] - 1.0) > 0.03:
        out['status'] = 'unmapped' if ratio < 0.98 or ratio > 1.05 else 'ok_unanchored'
    elif ratio < 0.98 and out['token_drop'] is not None and out['token_drop'] < 0.98:
        out['status'] = 'default'
    else:
        out['status'] = 'ok'
    return out


# --------------------------------------------------------------------------------------------------- trades

def make_trades(markets, prices, bench, last_day, size_usd=100_000.0, step_days=7, min_days=14, max_days=400,
                min_tvl=1_000_000.0, yield_fee=0.05, fee_by_class=None):
    """Every (matured market, weekly entry day) pair that passes the liquidity and data filters, with both legs and the
    costs of buying `size_usd` through the AMM at that day's reserves."""
    trades, rec_by_market = [], {}
    skipped_after_break = [0]
    fee_by_class = fee_by_class or {}
    for m in markets:
        if not m['rows'] or not m['expiry'] or m['expiry'] > last_day:
            continue
        rec = market_recovery(m, prices)
        rec_by_market[m['key']] = rec
        # The ratio compares a USD market price over three weeks after expiry with the API's SY price at expiry. For a
        # dollar unit that is a depeg reading; for an ETH, BTC or HYPE unit it is mostly the underlying's own USD move
        # over those weeks (weETH "recovered" 0.959 in June 2024 because ETH fell), so it is applied to dollar markets
        # only. Non-dollar markets are measured in their own unit, where a depeg of the token hits both legs alike.
        ratio_rec = rec['ratio'] if (rec['status'] == 'default' and m['cls'] in DOLLAR_CLASSES) else 1.0
        # The accounting unit's USD price at the end of the data, from the last row: a PT at expiry is worth one unit,
        # and a PT with days left is worth (1+implied)^(-days/365) of one. `end_gap_days` says how far before expiry
        # the data stopped (an abandoned market's rows can end weeks early).
        valid = [r for r in m['rows'] if r['t'] < m['expiry'] and r.get('pt') and r.get('implied') is not None
                 and -0.5 < r['implied'] < 2.0 and r['implied'] != 0.0]
        last_row = valid[-1] if valid else m['rows'][-1]
        end_left = max(0.0, (m['expiry'] - last_row['t']) / DAY)
        p_acct_end = (asset_usd_price(last_row, end_left) if end_left > 0 else last_row.get('pt')) or None
        fee = m['fee_rate'] if m['fee_rate'] is not None else fee_by_class.get(m['cls'], 0.001)
        first = m['rows'][0]['t']
        # After a dollar market breaks, the API keeps pricing it at its accounting value until it catches up, so a
        # purchase "at the API price" after the break is a trade nobody could do (sUSDX in late November 2025 at 97
        # cents of USDX that traded at five). Entries from the first break on are skipped unless the API's own unit
        # price already shows the break, in which case the entry is priced at market.
        broken_from = None
        if m['cls'] in DOLLAR_CLASSES:
            cands = [rec['break_day']] if (rec['status'] == 'default' and rec['break_day']) else []
            aser0 = (prices.get(m.get('acct_key') or '') or {}).get('prices') or []
            early_acct = window_median(aser0, first, first + 30 * DAY)
            if early_acct:
                b = first_series_break(aser0, first, early_acct, 0.95)
                if b:
                    cands.append(b)
            broken_from = min(cands) if cands else None
        rows = {r['t']: r for r in m['rows']}
        t = first + ((m['expiry'] - first) % (step_days * DAY))  # entry days aligned so the last one is a whole step before expiry
        while t < m['expiry']:
            r = rows.get(t)
            days = (m['expiry'] - t) / DAY
            t_next = t + step_days * DAY
            if r is None or days < min_days or days > max_days:
                t = t_next
                continue
            imp = r.get('implied')
            tvl = r.get('tvl') or 0.0
            if imp is None or not (-0.5 < imp < 2.0) or imp == 0.0 or tvl < min_tvl:
                t = t_next
                continue
            p_asset = asset_usd_price(r, days)
            if broken_from is not None and t >= broken_from and not (
                    p_asset and m.get('acct_usd_early') and p_asset < 0.95 * m['acct_usd_early']):
                skipped_after_break[0] += 1
                t = t_next
                continue
            flt, cov = floating_over(m, t, m['expiry'])
            if flt is None or cov < 0.8:
                t = t_next
                continue
            rew, _ = floating_over(m, t, m['expiry'], field='und_rew')
            tr7 = trailing_mean(m, t)
            tot_pt, tot_asset = pool_in_asset(r, days)
            imp_eff = None
            if p_asset and tot_pt and tot_asset and m['scalar_root']:
                imp_eff, _ = pt_buy_quote(imp, days, tot_pt, tot_asset, m['scalar_root'], fee, size_usd / p_asset)
            elif p_asset:
                # No reserves or curve: charge the fee only, and mark the trade so capacity is not claimed for it.
                imp_eff = (1.0 + imp) / (1.0 + fee) - 1.0
            if imp_eff is None:
                t = t_next
                continue
            fixed_gross = pt_fixed_return(imp, days)
            fixed_net = pt_fixed_return(imp_eff, days)
            b = bench_over(bench, t, m['expiry']) if m['cls'] in DOLLAR_CLASSES else None
            # A dollar investor also carries the accounting asset itself: a PT on USD0++ pays one USD0++, worth what
            # USD0++ is worth at expiry. That leg is the API's own accounting-unit price at expiry over entry, applied
            # when it moved more than 1% (below that it is the identity's noise).
            # Two readings of the same move: the accounting asset's market price from DefiLlama (median over the three
            # weeks after expiry a holder could wait, against the entry day), and the API's own unit price. The market
            # reading decides when it exists; both are kept so their agreement can be reported.
            #
            # One unit is worth P_mkt(yield token) / ER at expiry, and ER = SY price / unit price in the API's own
            # terms, so value(T) / value(t0) = ratio(T) x unit_API(T) / unit_API(t0). The ratio carries a collapse the
            # API marked at its accounting price (xUSD); the API's unit move carries one it marked at market (USD0++).
            # Multiplying the ratio by the accounting asset's *market* move instead would count a same-token collapse
            # twice (USDX: yield token = accounting asset), so the market move is used only when the yield token has no
            # market price at all, and otherwise kept as a cross-check of the API's reading.
            acct_move, acct_break, acct_src, api_move, mkt_move = 1.0, None, None, None, None
            aser = []
            if m['cls'] in DOLLAR_CLASSES and p_asset and p_acct_end:
                api_move = p_acct_end / p_asset
                aser = (prices.get(m.get('acct_key') or '') or {}).get('prices') or []
                p0 = window_median(aser, t - DAY, t + DAY)
                p1 = window_median(aser, m['expiry'] - DAY, m['expiry'] + 21 * DAY)
                if p0 and p1:
                    mkt_move = p1 / p0
                acct_move, acct_src = unit_move(rec['status'], api_move, mkt_move)
                if acct_move < 0.95:
                    acct_break = first_acct_break(m, t, p_asset, 0.95) or (
                        first_series_break(aser, t, p0, 0.95) if p0 else None)
            recovery = ratio_rec * acct_move
            bday = rec['break_day'] if rec['status'] == 'default' else None
            if acct_break is not None and (bday is None or acct_break < bday):
                bday = acct_break
            # The YT buyer crosses the same curve the other way: charge the PT buyer's impact with the sign reversed.
            imp_yt = imp + (imp - imp_eff)
            yt = yt_interest_return(flt, imp_yt, days, yield_fee)
            paths = daily_paths(m, t, m['expiry'], imp_eff, imp_yt, bench if m['cls'] in DOLLAR_CLASSES else None)
            trades.append({
                'key': m['key'], 'name': m['name'], 'cls': m['cls'], 'points': m['points'], 'protocol': m['protocol'],
                't0': t, 'T': m['expiry'], 'days': days, 'implied': imp, 'implied_eff': imp_eff,
                'trailing7': tr7, 'floating': flt, 'rewards': rew, 'coverage': cov, 'fixed_gross': fixed_gross, 'fixed_net': fixed_net,
                'bench': b, 'recovery': recovery, 'recovery_status': rec['status'], 'break_day': bday,
                'ratio_recovery': ratio_rec, 'acct_move': acct_move, 'p_acct_entry': p_asset, 'end_gap_days': end_left,
                'acct_move_source': acct_src, 'acct_move_api': api_move, 'acct_move_market': mkt_move,
                'tvl': tvl, 'yt': yt, 'reserves': bool(tot_pt and tot_asset and m['scalar_root']),
                'yield_fee': yield_fee, '_paths': paths,
                'spread_bench_entry': (imp - (bench_at(bench, t) or 0.0)) if m['cls'] in DOLLAR_CLASSES else None,
            })
            t = t_next
    return trades, rec_by_market, {'skipped_entries_after_a_dollar_break': skipped_after_break[0]}


def unit_move(ratio_status, api_move, mkt_move, noise=0.01):
    """The accounting unit's USD move to multiply the yield-token ratio by, and which reading it came from.

    When the yield token has a market price the ratio is in play, so the unit move must be the API's own (the market
    move would double-count a collapse of a token that is both yield token and accounting asset). Without a yield-token
    price the market reading of the accounting asset is the better one. Moves within `noise` are treated as none."""
    und_priced = ratio_status in ('ok', 'default', 'ok_unanchored')
    if (und_priced or mkt_move is None) and api_move is not None:
        mv, src = api_move, 'api'
    elif mkt_move is not None:
        mv, src = mkt_move, 'market'
    else:
        return 1.0, None
    if abs(mv - 1.0) > noise and 0.0 < mv < 2.0:
        return mv, src
    return 1.0, src


def window_median(series, lo, hi):
    pts = [r['p'] for r in series if lo <= r['t'] <= hi and r.get('p') is not None]
    return statistics.median(pts) if pts else None


def first_series_break(series, t0, p0, threshold):
    for r in series:
        if r['t'] > t0 and r.get('p') is not None and r['p'] < threshold * p0:
            return day_of(r['t'])
    return None


def first_acct_break(m, t0, p0, threshold):
    """First day after t0 on which the accounting unit's own USD price (from the row) fell below threshold x entry."""
    for r in m['rows']:
        if r['t'] <= t0 or not m['expiry']:
            continue
        left = (m['expiry'] - r['t']) / DAY
        pa = asset_usd_price(r, left) if left > 0 else r.get('pt')
        if pa and pa < threshold * p0:
            return r['t']
    return None


def bench_at(bench, t):
    days = [d for d in bench if d <= t]
    return bench[max(days)] if days else None


def trade_legs(tr, mode):
    """(total excess over the holding period, the part of it that lands on the break day) for one trade.

    mode 'float': PT against holding the same yield token; a default hits both legs, so only the difference is scaled.
    mode 'bench': PT against the savings rate; a default is the PT's loss alone.
    mode 'yt':    YT (interest only) against the savings rate on the YT's own capital."""
    rec = tr['recovery']
    if mode == 'float':
        x = (tr['fixed_net'] - tr['floating']) * rec
        return x, 0.0
    if mode == 'bench':
        if tr['bench'] is None:
            return None, None
        nondef = tr['fixed_net'] - tr['bench']
        jump = (1.0 + tr['fixed_net']) * (rec - 1.0)
        return nondef + jump, jump
    if mode == 'yt':
        if tr['yt'] is None:
            return None, None
        b = tr['bench'] if tr['bench'] is not None else 0.0
        payoff = (1.0 + tr['yt']) * rec - 1.0
        return payoff - b, payoff - tr['yt']
    raise ValueError(mode)


def daily_paths(m, t0, T, imp_entry, imp_yt_entry, bench, clip=(-0.5, 2.0)):
    """Mark-to-market inputs for one trade, one entry per day of the hold.

    `pt`: PT price in accounting units at each day boundary, (1 + implied)^(-days_left/365) from the day's implied
    (forward-filled), starting at the price actually paid (`imp_entry`, after fee and impact) and ending at 1.
    `yt0`: the YT price paid. `flt` and `bench`: each day's floating and benchmark return."""
    n = max(1, int(round((T - t0) / DAY)))
    imp_by = by_day(m['rows'], 'implied')
    flt_by = by_day(m['rows'], 'und_int')
    pt, flt, bch = [], [], []
    last_imp, last_flt = imp_entry, None
    for k in range(n):
        d = t0 + k * DAY
        left = (T - d) / DAY
        if k == 0:
            pt.append((1.0 + imp_entry) ** (-left / 365.0))
        else:
            v = imp_by.get(d)
            if v is not None and clip[0] < v < clip[1] and v != 0.0:
                last_imp = v
            pt.append((1.0 + last_imp) ** (-left / 365.0))
        f = flt_by.get(d)
        if f is not None:
            last_flt = min(clip[1], max(clip[0], f))
        flt.append((1.0 + (last_flt or 0.0)) ** (1.0 / 365.0) - 1.0)
        if bench is not None:
            bv = bench_at_cached(bench, d)
            bch.append(((1.0 + bv) ** (1.0 / 365.0) - 1.0) if bv is not None else None)
    pt.append(1.0)
    yt0 = 1.0 - (1.0 + imp_yt_entry) ** (-((T - t0) / DAY) / 365.0)
    return {'n': n, 'pt': pt, 'flt': flt, 'bench': bch if bench is not None else None, 'yt0': yt0}


_BENCH_CACHE = {}


def bench_at_cached(bench, d):
    if d in bench:
        return bench[d]
    key = (id(bench), d)
    if key not in _BENCH_CACHE:
        _BENCH_CACHE[key] = bench_at(bench, d)
    return _BENCH_CACHE[key]


def trade_daily(tr, mode):
    """Daily excess returns of one trade on its entry capital, marked to market; the list starts at the entry day.

    float: long PT against holding the yield token. bench: long PT against the savings rate, with a default landing
    on its break day and every later day scaled by the recovery. yt: long YT (interest only, net of the yield fee)
    against the savings rate on the YT's own capital. Summed, each reproduces the held-to-maturity result of
    `trade_legs` to within compounding."""
    p = tr.get('_paths')
    if not p:
        return None
    n, pt = p['n'], p['pt']
    p0 = pt[0]
    rec = tr['recovery']
    kb = None
    if rec < 1.0:
        bd = tr['break_day'] if tr['break_day'] is not None else tr['T'] - DAY
        kb = min(n - 1, max(0, int(round((bd - tr['t0']) / DAY))))
    out = []
    if mode == 'float':
        for k in range(n):
            x = (pt[k + 1] - pt[k]) / p0 - p['flt'][k]
            out.append(x * (rec if (kb is not None and k >= kb) else 1.0))
        return out
    if mode == 'bench':
        if p['bench'] is None or any(v is None for v in p['bench']):
            return None
        for k in range(n):
            scale = rec if (kb is not None and k >= kb) else 1.0
            x = scale * (pt[k + 1] - pt[k]) / p0 - p['bench'][k]
            if kb is not None and k == kb:
                x += (pt[k] / p0) * (rec - 1.0)
            out.append(x)
        return out
    if mode == 'yt':
        y0 = p['yt0']
        if y0 <= 1e-6:
            return None
        bch = p['bench'] or [0.0] * n
        if any(v is None for v in bch):
            return None
        fee = tr.get('yield_fee', 0.05)
        for k in range(n):
            y_now, y_next = 1.0 - (pt[k] if k else 1.0 - y0), 1.0 - pt[k + 1]
            interest = p['flt'][k] * (1.0 - fee)
            x = (y_next - y_now + interest) / y0
            if kb is not None and k >= kb:
                x *= rec
            out.append(x - bch[k])
        return out
    raise ValueError(mode)


def portfolio_series(trades, mode, day_axis, cutoff, last_day, weight='equal'):
    """Daily return of a book that puts one unit of capital to work each entry day, split equally across that day's
    trades, and holds each to expiry, marked to market every day (`trade_daily`).

    Before `cutoff` the book holds only trades that had matured by `cutoff` (what was knowable when choosing); from
    `cutoff` on it holds only trades entered on or after it. Returns a list aligned with `day_axis`."""
    ins = [tr for tr in trades if tr['T'] <= cutoff]
    oos = [tr for tr in trades if tr['t0'] >= cutoff and tr['T'] <= last_day]
    idx = {d: i for i, d in enumerate(day_axis)}
    num = [0.0] * len(day_axis)
    den = [0.0] * len(day_axis)
    for group, lo, hi in ((ins, day_axis[0], cutoff), (oos, cutoff, last_day + DAY)):
        daily = {id(tr): trade_daily(tr, mode) for tr in group}
        per_entry = collections.Counter()
        for tr in group:
            if daily[id(tr)] is not None:
                per_entry[tr['t0']] += (tr['tvl'] if weight == 'tvl' else 1.0)
        for tr in group:
            xs = daily[id(tr)]
            if xs is None:
                continue
            w = (tr['tvl'] if weight == 'tvl' else 1.0) / per_entry[tr['t0']]
            for k, x in enumerate(xs):
                d = tr['t0'] + k * DAY
                if d < lo or d >= hi or d not in idx:
                    continue
                i = idx[d]
                num[i] += w * x
                den[i] += w
    return [(num[i] / den[i]) if den[i] > 0 else 0.0 for i in range(len(day_axis))]


def trade_stats(trades, mode):
    xs, aprs = [], []
    for tr in trades:
        x, _ = trade_legs(tr, mode)
        if x is None:
            continue
        xs.append(x)
        aprs.append(annualise(x, tr['days']))
    if not xs:
        return {'n': 0}
    aprs_sorted = sorted(aprs)
    years = sum(tr['days'] for tr in trades if trade_legs(tr, mode)[0] is not None) / 365.0
    return {'n': len(xs), 'pooled_apr': sum(xs) / years if years else None, 'mean_apr': sum(aprs) / len(aprs),
            'median_apr': statistics.median(aprs),
            'share_positive': sum(1 for a in aprs if a > 0) / len(aprs), 'worst_apr': aprs_sorted[0],
            'p10_apr': aprs_sorted[int(0.1 * (len(aprs) - 1))], 'p90_apr': aprs_sorted[int(0.9 * (len(aprs) - 1))],
            'markets': len({tr['key'] for tr in trades}), 'mean_days': sum(tr['days'] for tr in trades) / len(trades)}


def evaluate(variants, trades, mode, day_axis, cutoff, last_day, hold_days, weight='equal'):
    """choose_then_test over named trade filters, plus the inference that respects overlapping holdings."""
    series = {name: portfolio_series([tr for tr in trades if f(tr)], mode, day_axis, cutoff, last_day, weight)
              for name, f in variants.items()}
    c = day_axis.index(cutoff) if cutoff in day_axis else B.cutoff_index(len(day_axis), 0.5)
    frac = c / len(day_axis)
    res = B.choose_then_test(series, frac=frac, periods_per_year=365)
    lag = max(7, int(hold_days))
    per = {}
    for name, f in variants.items():
        sub = [tr for tr in trades if f(tr)]
        s = series[name]
        oos = s[c:]
        t_oos, p_oos = B.newey_west_t(oos, lags=lag)
        boot = B.block_bootstrap(oos, block=lag, n=1000)
        per[name] = {
            'in_sample': B.perf(s[:c], 365), 'out_of_sample': B.perf(oos, 365),
            'oos_nw_t_lag_hold': t_oos, 'oos_nw_p_lag_hold': p_oos,
            'oos_boot_mean_ci_apr': [boot['lo'] * 365 if boot['lo'] is not None else None,
                                     boot['hi'] * 365 if boot['hi'] is not None else None],
            'oos_boot_p_le_0': boot['p_le_0'],
            'trades_in_sample': trade_stats([tr for tr in sub if tr['T'] <= cutoff], mode),
            'trades_out_of_sample': trade_stats([tr for tr in sub if tr['t0'] >= cutoff and tr['T'] <= last_day], mode),
        }
    pv = [per[n]['oos_nw_p_lag_hold'] for n in variants]
    rej, adj = B.bh(pv, q=0.10)
    for n, r, a in zip(variants, rej, adj):
        per[n]['oos_bh_reject_q10'] = r
        per[n]['oos_bh_adj_p'] = a
    return {'choose_then_test': res, 'variants': per, 'cutoff_index': c, 'nw_lag_days': lag, 'weight': weight}




# --------------------------------------------------------------------------------------------------- blocked analysis

def price_at(series, t, tol_days=3):
    """Market price nearest to t within `tol_days`, or None."""
    best = None
    for r in series:
        dd = abs(r['t'] - t)
        if dd <= tol_days * DAY and (best is None or dd < best[0]):
            best = (dd, r['p'])
    return best[1] if best else None


def blocked_trade_returns(txs, expiry, prices, er_now, bench, dollar=True):
    """Realised outcome of every PT purchase in a market the API no longer serves.

    Each BUY_PT trade fixes (1 + implied)^(tau/365) of the accounting unit at expiry. The unit's market value is the
    yield token's market price divided by the SY exchange rate. Before a break the dollar unit is worth $1 by
    construction; at expiry it is P(T) / ER, with ER read now (a collapsed protocol's rate is frozen, so now = then;
    a healthy one has grown a little, which understates recovery by that growth, a few tenths of a percent).
    When the SY's asset is the yield token itself (ER = 1), the unit is the token, so recovery is P(T) / P(t).
    Returns rows {t, usd, implied, days, fixed, recovery, realised, bench, excess} for dollar markets."""
    rows = []
    p_t_exp = None
    pts = [r['p'] for r in prices if expiry - DAY <= r['t'] <= expiry + 7 * DAY]
    if pts:
        p_t_exp = statistics.median(pts)
    for x in txs:
        if x.get('action') != 'BUY_PT':
            continue
        t = iso_ts(x.get('timestamp'))
        imp = fnum(x.get('impliedApy'))
        usd = fnum(x.get('value'), 0.0)
        if t is None or imp is None or not (-0.5 < imp < 2.0) or t >= expiry:
            continue
        days = (expiry - t) / DAY
        fixed = pt_fixed_return(imp, days)
        rec = None
        if p_t_exp is not None:
            if er_now and abs(er_now - 1.0) > 1e-9:
                rec = min(1.0, p_t_exp / er_now) if dollar else None
            else:
                p0 = price_at(prices, t)
                rec = min(1.0, p_t_exp / p0) if p0 else None
        b = bench_over(bench, t, expiry) if (dollar and bench) else None
        realised = ((1 + fixed) * rec - 1) if (fixed is not None and rec is not None) else None
        rows.append({'t': t, 'usd': usd, 'implied': imp, 'days': days, 'fixed': fixed, 'recovery': rec,
                     'realised': realised, 'bench': b,
                     'excess': (realised - b) if (realised is not None and b is not None) else None})
    return rows


def blocked_summary(out, markets, prices, bench, last_day):
    raw = Path(out) / 'raw'
    res = []
    for m in markets:
        if m['hist_status'] == 200 or m['hist_status'] is None:
            continue
        tx = read_json(raw / 'tx' / (m['key'] + '.json.gz')) or {}
        txs = tx.get('rows') or []
        rec = read_json(raw / 'blocked' / (m['key'] + '.json')) or {}
        acts = collections.Counter()
        usd = collections.Counter()
        for x in txs:
            acts[x.get('action')] += 1
            usd[x.get('action')] += fnum(x.get('value'), 0.0)
        tk = market_key(m['chain'], rec['yield_token']) if rec.get('yield_token') else None
        series = (prices.get(tk) or {}).get('prices') or []
        if not series and tk:
            series = (read_json(raw / 'prices' / (tk + '.json')) or {}).get('prices') or []
        dollar = m['cls'] in DOLLAR_CLASSES
        matured = bool(m['expiry'] and m['expiry'] <= last_day)
        trs = blocked_trade_returns(txs, m['expiry'], series, rec.get('exchange_rate_now'), bench, dollar) if (m['expiry'] and matured) else []
        priced = [r for r in trs if r['excess'] is not None]
        w = sum(r['usd'] for r in priced)
        res.append({'key': m['key'], 'name': m['name'], 'cls': m['cls'], 'expiry': utc(m['expiry']) if m['expiry'] else None,
                    'matured': matured, 'listed': m['listed'], 'tx': len(txs), 'buy_pt_usd': usd.get('BUY_PT', 0.0),
                    'sell_pt_usd': usd.get('SELL_PT', 0.0), 'add_liquidity_usd': usd.get('ADD_LIQUIDITY', 0.0),
                    'first_tx': utc(min(iso_ts(x['timestamp']) for x in txs)) if txs else None,
                    'yield_token': rec.get('yield_token'), 'exchange_rate_now': rec.get('exchange_rate_now'),
                    'price_points': len(series), 'resolve_error': rec.get('error'),
                    'recovery_min': min((r['recovery'] for r in trs if r['recovery'] is not None), default=None),
                    'buy_pt_trades_priced': len(priced), 'buy_pt_usd_priced': w,
                    'usd_weighted_excess_vs_ssr': (sum(r['excess'] * r['usd'] for r in priced) / w) if w else None,
                    'usd_weighted_implied': (sum(r['implied'] * r['usd'] for r in priced) / w) if w else None})
    res.sort(key=lambda x: -x['buy_pt_usd'])
    return res


# --------------------------------------------------------------------------------------------------- analyze

THRESHOLDS_B = [None, 0, 100, 200, 300, 500, 800, 1200]        # bp of implied over trailing-7d floating
THRESHOLDS_C = [0, 100, 200, 400]                              # bp of trailing floating over implied (YT)
BUCKETS_D = [(None, 0.02), (0.02, 0.04), (0.04, 0.06), (0.06, 0.10), (0.10, 0.15), (0.15, None)]
THRESHOLDS_D = [0.0, 0.02, 0.04, 0.06, 0.10, 0.15]
CLASSES = ['stable', 'ethena', 'eth', 'btc', 'hype', 'other']
SIZES = [25_000, 100_000, 250_000, 500_000, 1_000_000, 2_500_000, 5_000_000, 10_000_000]


def bucket_name(lo, hi):
    f = lambda x: '%g%%' % (100 * x)  # noqa: E731
    return ('<%s' % f(hi)) if lo is None else ('>=%s' % f(lo)) if hi is None else '%s-%s' % (f(lo), f(hi))


def in_bucket(x, lo, hi):
    return x is not None and (lo is None or x >= lo) and (hi is None or x < hi)


def identity_checks(markets):
    """Three re-derivations of the API's own numbers from each other, so a decode or unit error shows as a residual."""
    tvl_res, pt_res, flt_res = [], [], []
    for m in markets:
        usd = (m.get('acct_symbol') or '').lower() in USD_ACCOUNTING
        rows = m['rows']
        for r in rows:
            if (r.get('tvl') or 0) >= 1e6 and None not in (r.get('total_pt'), r.get('pt'), r.get('total_sy'), r.get('sy')):
                tvl_res.append(abs(r['tvl'] - (r['total_pt'] * r['pt'] + r['total_sy'] * r['sy'])) / r['tvl'])
            if usd and m['expiry'] and r.get('pt') and r.get('implied') is not None and (r.get('tvl') or 0) >= 1e6:
                days = (m['expiry'] - r['t']) / DAY
                if days >= 7:
                    pt_res.append(abs(r['pt'] - (1 + r['implied']) ** (-days / 365.0)))
        if usd:
            sy = by_day(rows, 'sy')
            ds = sorted(sy)
            for i in range(0, len(ds) - 30, 30):
                a, b = ds[i], ds[i] + 30 * DAY
                if b in sy and sy[a] and sy[b]:
                    er = (sy[b] / sy[a]) - 1.0
                    fl, cov = floating_over(m, a, b)
                    if fl is not None and cov >= 0.9 and abs(er) < 0.2:
                        flt_res.append(abs(er - fl) * 365.0 / 30.0)

    def q(xs):
        if not xs:
            return {'n': 0}
        xs = sorted(xs)
        return {'n': len(xs), 'median': xs[len(xs) // 2], 'p90': xs[int(0.9 * (len(xs) - 1))]}
    return {'pool_tvl_identity_rel_err': q(tvl_res), 'usd_pt_price_identity_abs_err': q(pt_res),
            'usd_sy_growth_vs_interest_apy_abs_err_30d': q(flt_res)}


def capacity_curve(m, row, comparator, sizes=SIZES):
    """Implied APY after buying each size through the AMM, the edge over `comparator`, and dollars a year at each size.
    The capacity is the size that maximises dollars a year."""
    days = (m['expiry'] - row['t']) / DAY
    p_asset = asset_usd_price(row, days)
    tot_pt, tot_asset = pool_in_asset(row, days)
    curve = []
    for s in sizes:
        imp = None
        if p_asset and tot_pt and tot_asset and m['scalar_root']:
            imp, _ = pt_buy_quote(row['implied'], days, tot_pt, tot_asset, m['scalar_root'], m['fee_rate'] or 0.001, s / p_asset)
        edge = (imp - comparator) if imp is not None else None
        curve.append({'size_usd': s, 'implied_after': imp, 'edge': edge,
                      'usd_per_year': (s * edge) if edge is not None else None})
    best = max((c for c in curve if c['usd_per_year'] is not None), key=lambda c: c['usd_per_year'], default=None)
    return curve, best


def cmd_analyze(args):
    out = Path(args.out)
    markets, prices = load_markets(out)
    last_day = max((r['t'] for m in markets for r in m['rows']), default=day_of(time.time()))
    bench, bench_src = combined_benchmark(out, markets, last_day)
    fee_by_class = {}
    for c in CLASSES:
        fs = [m['fee_rate'] for m in markets if m['cls'] == c and m['fee_rate'] is not None]
        fee_by_class[c] = statistics.median(fs) if fs else 0.001

    # Universe and survivorship.
    def max_tvl(m):
        return max((r.get('tvl') or 0 for r in m['rows']), default=0)
    matured = [m for m in markets if m['expiry'] and m['expiry'] <= last_day]
    active = [m for m in markets if m['expiry'] and m['expiry'] > last_day]
    blocked = [m for m in markets if m['hist_status'] not in (200, None)]
    universe = {
        'markets': len(markets), 'matured': len(matured), 'active': len(active),
        'listed': collections.Counter(m['listed'] for m in markets),
        'history_status': collections.Counter(str(m['hist_status']) for m in markets),
        'meta_status': collections.Counter(str(m['meta_status']) for m in markets),
        'by_class_matured_with_history': collections.Counter(m['cls'] for m in matured if m['rows']),
        'blocked_history': [{'key': m['key'], 'name': m['name'], 'expiry': utc(m['expiry']) if m['expiry'] else None,
                             'listed': m['listed'], 'status': m['hist_status'], 'message': m['hist_message']}
                            for m in blocked],
        'last_day': utc(last_day),
    }

    # Cutoff rule, fixed before any strategy is evaluated: the median expiry of matured markets that ever held $1M,
    # rounded down to the first of its month.
    liquid_expiries = sorted(m['expiry'] for m in matured if max_tvl(m) >= 1e6)
    med = liquid_expiries[len(liquid_expiries) // 2] if liquid_expiries else last_day - 365 * DAY
    md = dt.datetime.fromtimestamp(med, dt.timezone.utc)
    cutoff = int(dt.datetime(md.year, md.month, 1, tzinfo=dt.timezone.utc).timestamp())
    if args.cutoff:
        cutoff = iso_ts(args.cutoff + 'T00:00:00Z')

    # Recovery: every matured market, dollar ones first.
    trades, rec, trade_build = make_trades(markets, prices, bench, last_day, size_usd=args.size, min_tvl=args.min_tvl,
                                           fee_by_class=fee_by_class)
    rec_rows = []
    for m in matured:
        r = rec.get(m['key']) or market_recovery(m, prices)
        rec_rows.append({'key': m['key'], 'name': m['name'], 'protocol': m['protocol'], 'cls': m['cls'],
                         'expiry': utc(m['expiry']), 'max_tvl': max_tvl(m), 'status': r['status'],
                         'ratio': r['ratio'], 'early_ratio': r['early_ratio'],
                         'break_day': utc(r['break_day']) if r['break_day'] else None, 'source': r['source'],
                         'und_symbol': m['und_symbol'], 'listed': m['listed']})
    both = sorted(abs(tr['acct_move_api'] - tr['acct_move_market']) for tr in trades
                  if tr.get('acct_move_api') is not None and tr.get('acct_move_market') is not None)
    acct_agreement = {'n': len(both), 'median_abs_diff': both[len(both) // 2] if both else None,
                      'p90_abs_diff': both[int(0.9 * (len(both) - 1))] if both else None,
                      'share_within_1pct': (sum(1 for x in both if x <= 0.01) / len(both)) if both else None,
                      'dollar_trades_market_source': sum(1 for tr in trades if tr.get('acct_move_source') == 'market'),
                      'dollar_trades_api_source': sum(1 for tr in trades if tr.get('acct_move_source') == 'api')}
    loss_by = collections.defaultdict(list)
    for tr in trades:
        if tr['cls'] in DOLLAR_CLASSES and tr['recovery'] < 0.98:
            loss_by[tr['key']].append(tr)
    mk = {m['key']: m for m in markets}
    dollar_losses = []
    for k, ts in loss_by.items():
        m = mk[k]
        dollar_losses.append({'key': k, 'name': m['name'], 'protocol': m['protocol'], 'expiry': utc(m['expiry']),
                              'max_tvl': max_tvl(m), 'trades': len(ts), 'recovery_min': min(t['recovery'] for t in ts),
                              'recovery_max': max(t['recovery'] for t in ts),
                              'ratio_recovery': min(t['ratio_recovery'] for t in ts),
                              'acct_move_min': min(t['acct_move'] for t in ts),
                              'acct_move_source': sorted({t['acct_move_source'] or '-' for t in ts}),
                              'acct_move_api_min': min((t['acct_move_api'] for t in ts if t['acct_move_api'] is not None), default=None),
                              'acct_move_market_min': min((t['acct_move_market'] for t in ts if t['acct_move_market'] is not None), default=None),
                              'break_day': utc(min(t['break_day'] for t in ts if t['break_day'])) if any(t['break_day'] for t in ts) else None,
                              'spread_min': min(t['spread_bench_entry'] for t in ts if t['spread_bench_entry'] is not None),
                              'spread_max': max(t['spread_bench_entry'] for t in ts if t['spread_bench_entry'] is not None)})
    dollar_losses.sort(key=lambda x: x['recovery_min'])
    dollar_rec = [x for x in rec_rows if x['cls'] in DOLLAR_CLASSES and x['max_tvl'] >= 1e6]
    recovery = {
        'status_all_matured': collections.Counter(x['status'] for x in rec_rows),
        'status_dollar_ever_1m': collections.Counter(x['status'] for x in dollar_rec),
        'dollar_ever_1m_tvl_by_status': {s: sum(x['max_tvl'] for x in dollar_rec if x['status'] == s)
                                         for s in set(x['status'] for x in dollar_rec)},
        'accounting_move_agreement_api_vs_market': acct_agreement,
        'dollar_losses': dollar_losses,
        'defaults': sorted([x for x in rec_rows if x['status'] == 'default' and x['cls'] in DOLLAR_CLASSES],
                           key=lambda x: -x['max_tvl']),
        'non_dollar_usd_ratio_below_098_not_applied': sum(1 for x in rec_rows if x['status'] == 'default'
                                                          and x['cls'] not in DOLLAR_CLASSES),
        'unmapped_dollar': sorted([x for x in dollar_rec if x['status'] == 'unmapped'], key=lambda x: -x['max_tvl'])[:40],
        'unpriced_dollar': sorted([x for x in dollar_rec if x['status'] in ('no_price', 'no_price_at_maturity')],
                                  key=lambda x: -x['max_tvl'])[:60],
    }

    blocked = blocked_summary(out, markets, prices, bench, last_day)
    panel_volume = sum((r.get('vol') or 0.0) for m in markets if m['hist_status'] == 200 for r in m['rows'])
    bd = [b for b in blocked if b['cls'] in DOLLAR_CLASSES and b['matured']]
    bw = sum(b['buy_pt_usd_priced'] for b in bd)
    blocked_block = {
        'markets': len(blocked), 'with_transactions': sum(1 for b in blocked if b['tx']),
        'buy_pt_usd_total': sum(b['buy_pt_usd'] for b in blocked),
        'panel_trading_volume_usd_total': panel_volume,
        'dollar_matured': len(bd), 'dollar_matured_buy_pt_usd': sum(b['buy_pt_usd'] for b in bd),
        'dollar_matured_buy_pt_usd_priced': bw,
        'dollar_matured_usd_weighted_excess_vs_ssr': (sum((b['usd_weighted_excess_vs_ssr'] or 0) * b['buy_pt_usd_priced'] for b in bd) / bw) if bw else None,
        'markets_detail': blocked[:60],
    }

    day_axis = list(range(min(tr['t0'] for tr in trades), last_day + DAY, DAY)) if trades else []
    if cutoff not in day_axis and day_axis:
        cutoff = min(day_axis, key=lambda d: abs(d - cutoff))
    hold = statistics.median(tr['days'] for tr in trades) if trades else 30

    results = {}
    # (a) unconditional, by class.
    va = {c: (lambda tr, c=c: tr['cls'] == c) for c in CLASSES}
    va['all'] = lambda tr: True
    va['points'] = lambda tr: tr['points']
    va['no_points'] = lambda tr: not tr['points']
    results['a_pt_minus_floating_by_class'] = evaluate(va, trades, 'float', day_axis, cutoff, last_day, hold)
    # (b) conditional on implied over trailing floating.
    vb = {}
    for x in THRESHOLDS_B:
        name = 'all' if x is None else 'spread>=%dbp' % x
        vb[name] = (lambda tr, x=x: True if x is None else (tr['trailing7'] is not None and tr['implied'] - tr['trailing7'] >= x / 1e4))
    results['b_pt_when_implied_over_trailing'] = evaluate(vb, trades, 'float', day_axis, cutoff, last_day, hold)
    # (c) long YT when floating runs above implied.
    vc = {'yt>=%dbp' % y: (lambda tr, y=y: tr['trailing7'] is not None and tr['trailing7'] - tr['implied'] >= y / 1e4)
          for y in THRESHOLDS_C}
    vc['yt_all'] = lambda tr: True
    results['c_yt_when_floating_over_implied'] = evaluate(vc, trades, 'yt', day_axis, cutoff, last_day, hold)
    # (d) dollar PT over the savings rate, after defaults: buckets (descriptive) and thresholds (the choice).
    dollar = [tr for tr in trades if tr['cls'] in DOLLAR_CLASSES and tr['bench'] is not None]
    vdb = {bucket_name(lo, hi): (lambda tr, lo=lo, hi=hi: in_bucket(tr['spread_bench_entry'], lo, hi)) for lo, hi in BUCKETS_D}
    vdb['all_dollar'] = lambda tr: True
    results['d_dollar_pt_over_ssr_buckets'] = evaluate(vdb, dollar, 'bench', day_axis, cutoff, last_day, hold)
    vdt = {'spread>=%g%%' % (100 * z): (lambda tr, z=z: tr['spread_bench_entry'] is not None and tr['spread_bench_entry'] >= z)
           for z in THRESHOLDS_D}
    results['d_dollar_pt_over_ssr_thresholds'] = evaluate(vdt, dollar, 'bench', day_axis, cutoff, last_day, hold)
    # (e) the combination a dollar book would run: dollar PTs whose implied clears the underlying's own trailing
    # interest by X, judged against the savings rate after defaults.
    ve = {'dollar_spread_over_trailing>=%dbp' % x: (lambda tr, x=x: tr['trailing7'] is not None and tr['implied'] - tr['trailing7'] >= x / 1e4)
          for x in (0, 200, 500, 800)}
    results['e_dollar_pt_over_ssr_when_implied_over_trailing'] = evaluate(ve, dollar, 'bench', day_axis, cutoff, last_day, hold)
    # Weighting by pool TVL at entry instead of equally: the deep markets are the ones capital can actually use, and an
    # equal-weighted book over-weights the small issuers where the defaults were.
    results['d_dollar_pt_over_ssr_thresholds_tvl_weighted'] = evaluate(vdt, dollar, 'bench', day_axis, cutoff, last_day, hold, weight='tvl')
    results['b_pt_when_implied_over_trailing_tvl_weighted'] = evaluate(vb, trades, 'float', day_axis, cutoff, last_day, hold, weight='tvl')
    # (d') the same thresholds without the defaults, to show what the credit events cost.
    nodef = [dict(tr, recovery=1.0, break_day=None) for tr in dollar]
    results['d_dollar_pt_over_ssr_thresholds_ex_defaults'] = evaluate(vdt, nodef, 'bench', day_axis, cutoff, last_day, hold)

    # Default arithmetic by spread bucket: promised spread, realised loss, realised excess, per trade (annualised).
    credit = []
    for lo, hi in BUCKETS_D:
        sub = [tr for tr in dollar if in_bucket(tr['spread_bench_entry'], lo, hi)]
        if not sub:
            continue
        years = sum(tr['days'] for tr in sub) / 365.0
        prom = sum(tr['fixed_net'] - tr['bench'] for tr in sub) / years
        loss = sum((1 + tr['fixed_net']) * (1 - tr['recovery']) for tr in sub) / years
        exc_tot = sum(trade_legs(tr, 'bench')[0] for tr in sub) / years
        exc = [annualise(trade_legs(tr, 'bench')[0], tr['days']) for tr in sub]
        oos = [tr for tr in sub if tr['t0'] >= cutoff]
        oos_years = sum(tr['days'] for tr in oos) / 365.0
        credit.append({'bucket': bucket_name(lo, hi), 'trades': len(sub), 'markets': len({tr['key'] for tr in sub}),
                       'capital_years': years,
                       'defaulted_trades': sum(1 for tr in sub if tr['recovery'] < 0.98),
                       'defaulted_markets': len({tr['key'] for tr in sub if tr['recovery'] < 0.98}),
                       'mean_promised_spread_apr': prom, 'mean_default_loss_apr': loss,
                       'mean_realised_excess_apr': exc_tot, 'median_realised_excess_apr': statistics.median(exc),
                       'oos_trades': len(oos),
                       'oos_default_loss_apr': (sum((1 + tr['fixed_net']) * (1 - tr['recovery']) for tr in oos) / oos_years) if oos_years else None,
                       'oos_realised_excess_apr': (sum(trade_legs(tr, 'bench')[0] for tr in oos) / oos_years) if oos_years else None})

    # Where the dollar trades came from: per protocol, promised spread against what was realised.
    by_proto = collections.defaultdict(list)
    for tr in dollar:
        by_proto[tr['protocol'] or tr['name']].append(tr)
    protocols = []
    for k, sub in by_proto.items():
        exc = [annualise(trade_legs(tr, 'bench')[0], tr['days']) for tr in sub]
        years = sum(tr['days'] for tr in sub) / 365.0
        protocols.append({'protocol': k, 'trades': len(sub), 'markets': len({tr['key'] for tr in sub}),
                          'defaulted_markets': len({tr['key'] for tr in sub if tr['recovery'] < 0.98}),
                          'mean_promised_spread_apr': sum(tr['fixed_net'] - tr['bench'] for tr in sub) / years,
                          'mean_realised_excess_apr': sum(trade_legs(tr, 'bench')[0] for tr in sub) / years,
                          'worst_trade_apr': min(exc), 'first_entry': utc(min(tr['t0'] for tr in sub)),
                          'last_expiry': utc(max(tr['T'] for tr in sub))})
    protocols.sort(key=lambda x: -x['trades'])

    # The book already holds one Pendle row (pt-susds-fixed-vs-ssr). Sky's own PTs, held to expiry against the savings
    # rate, are its history.
    mk_und = {m['key']: (m['und_symbol'] or '').lower() for m in markets}
    sky = [tr for tr in dollar if mk_und.get(tr['key']) in SKY_SYMBOLS]
    sky_block = {'all': trade_stats(sky, 'bench'),
                 'out_of_sample': trade_stats([tr for tr in sky if tr['t0'] >= cutoff], 'bench'),
                 'markets': sorted({tr['name'] + ' ' + utc(tr['T'])[:10] for tr in sky})}

    # Points: what the YT side pays for them, as implied minus trailing floating at entry.
    pts = collections.defaultdict(list)
    for tr in trades:
        if tr['trailing7'] is not None:
            pts['points' if tr['points'] else 'no_points'].append(tr['implied'] - tr['trailing7'])
    points_premium = {k: {'n': len(v), 'median_implied_minus_trailing': statistics.median(v)} for k, v in pts.items()}

    # Live board: today's active markets scored by what survived, with capacity through the AMM. The dollar comparator
    # today is the savings rate read on chain (sUSDS.ssr() at latest), not the Pendle-derived series' last value, which
    # is a trailing interest APY; both are reported.
    bench_series_now = bench_at(bench, last_day)
    bench_now = args.ssr_now if args.ssr_now is not None else bench_series_now
    live = []
    for m in active:
        if not m['rows']:
            continue
        row = m['rows'][-1]
        if row['t'] < last_day - 2 * DAY or row.get('implied') is None:
            continue
        days = (m['expiry'] - row['t']) / DAY
        if days < 7 or not (-0.5 < row['implied'] < 2.0) or row['implied'] == 0.0:
            continue
        tr7 = trailing_mean(m, row['t'] + DAY)
        comp = bench_now if m['cls'] in DOLLAR_CLASSES else tr7
        if comp is None:
            continue
        curve, best = capacity_curve(m, row, comp)
        best_float = capacity_curve(m, row, tr7)[1] if tr7 is not None else None
        entry = {'key': m['key'], 'name': m['name'], 'protocol': m['protocol'], 'cls': m['cls'],
                 'points': m['points'], 'expiry': utc(m['expiry']), 'days': days, 'tvl': row.get('tvl'),
                 'implied': row['implied'], 'trailing7': tr7, 'comparator': comp,
                 'spread': row['implied'] - comp, 'implied_minus_trailing': (row['implied'] - tr7) if tr7 is not None else None,
                 'best': best, 'best_vs_floating': best_float, 'curve': curve}
        if m['cls'] in DOLLAR_CLASSES:
            # What history says a dollar PT at this spread lost to defaults, per year, charged against today's quote.
            for lo, hi in BUCKETS_D:
                if in_bucket(entry['spread'], lo, hi):
                    cb = next((c for c in credit if c['bucket'] == bucket_name(lo, hi)), None)
                    entry['bucket'] = bucket_name(lo, hi)
                    entry['hist_default_loss_apr'] = cb['mean_default_loss_apr'] if cb else None
                    entry['hist_realised_excess_apr'] = cb['mean_realised_excess_apr'] if cb else None
                    if cb and best and best.get('edge') is not None:
                        entry['expected_excess_after_impact_and_defaults'] = best['edge'] - cb['mean_default_loss_apr']
                    break
        live.append(entry)
    live.sort(key=lambda x: -((x['best'] or {}).get('usd_per_year') or 0))

    # What each family's in-sample choice would hold today: the live markets it selects, each at the size that maximises
    # its dollars a year through the AMM, dollar ones charged the historical default loss of their spread bucket.
    fam_defs = {'a_pt_minus_floating_by_class': (va, False), 'b_pt_when_implied_over_trailing': (vb, False),
                'c_yt_when_floating_over_implied': (vc, False), 'd_dollar_pt_over_ssr_buckets': (vdb, True),
                'd_dollar_pt_over_ssr_thresholds': (vdt, True),
                'e_dollar_pt_over_ssr_when_implied_over_trailing': (ve, True)}
    live_books = {}
    mode_of = {'a_pt_minus_floating_by_class': 'float', 'b_pt_when_implied_over_trailing': 'float',
               'c_yt_when_floating_over_implied': 'yt', 'd_dollar_pt_over_ssr_buckets': 'bench',
               'd_dollar_pt_over_ssr_thresholds': 'bench', 'e_dollar_pt_over_ssr_when_implied_over_trailing': 'bench'}
    for fam, (variants, dollar_only) in fam_defs.items():
        chosen = results[fam]['choose_then_test']['chosen']
        pred = variants[chosen]
        pool = dollar if dollar_only else trades
        oos_sel = [tr for tr in pool if pred(tr) and tr['t0'] >= cutoff and tr['T'] <= last_day]
        results[fam]['chosen_oos_by_class'] = {c: trade_stats([tr for tr in oos_sel if tr['cls'] == c], mode_of[fam])
                                               for c in CLASSES if any(tr['cls'] == c for tr in oos_sel)}
        if mode_of[fam] == 'float' and oos_sel:
            # The token holder also collects the reward tokens the comparator leaves out; charge them to the switch.
            yrs = sum(tr['days'] for tr in oos_sel) / 365.0
            results[fam]['chosen_oos_pooled_apr_net_of_reward_tokens'] = sum(
                trade_legs(tr, 'float')[0] - (tr['rewards'] or 0.0) * tr['recovery'] for tr in oos_sel) / yrs
            results[fam]['chosen_oos_reward_token_apr'] = sum((tr['rewards'] or 0.0) for tr in oos_sel) / yrs
        if mode_of[fam] == 'yt':
            # A YT book's capacity is not the PT-buy curve; the family failed out of sample and is not sized.
            live_books[fam] = {'chosen': chosen, 'markets': 0, 'capacity_usd': 0.0, 'usd_per_year_before_defaults': 0.0,
                               'usd_per_year_after_hist_defaults': 0.0, 'net_apr_after_hist_defaults': None, 'top': [],
                               'note': 'not sized: YT capacity is a different curve and the family failed out of sample'}
            continue
        key_best = 'best_vs_floating' if mode_of[fam] == 'float' else 'best'
        rows = []
        for e in live:
            if dollar_only and e['cls'] not in DOLLAR_CLASSES:
                continue
            pseudo = {'cls': e['cls'], 'implied': e['implied'], 'trailing7': e['trailing7'], 'points': e['points'],
                      'spread_bench_entry': (e['implied'] - bench_now) if e['cls'] in DOLLAR_CLASSES else None}
            b = e.get(key_best)
            if pred(pseudo) and b and b.get('usd_per_year') is not None and b['usd_per_year'] > 0:
                rows.append((e, b))
        cap = sum(b['size_usd'] for e, b in rows)
        usd = sum(b['usd_per_year'] for e, b in rows)
        # Defaults are charged only against the savings rate: against the same token's floating yield they hit both legs.
        loss = sum((e.get('hist_default_loss_apr') or 0.0) * b['size_usd'] for e, b in rows) if mode_of[fam] == 'bench' else 0.0
        split = {}
        if mode_of[fam] == 'float':
            # A token whose trailing interest reads zero (a non-yielding stable such as AUSD, or a yield the API does not
            # measure) makes "PT over floating" the whole implied rate; it is reported apart from true fixed-for-floating.
            for name_, sel in (('floating_measured', lambda e: (e['trailing7'] or 0) > 0.001),
                               ('floating_zero_or_unmeasured', lambda e: (e['trailing7'] or 0) <= 0.001)):
                sub = [(e, b) for e, b in rows if sel(e)]
                split[name_] = {'markets': len(sub), 'capacity_usd': sum(b['size_usd'] for e, b in sub),
                                'usd_per_year': sum(b['usd_per_year'] for e, b in sub),
                                'dollar_markets': sum(1 for e, b in sub if e['cls'] in DOLLAR_CLASSES)}
        live_books[fam] = {'chosen': chosen, 'split': split,
                           'comparator': 'trailing 7-day floating of the same token' if mode_of[fam] == 'float' else 'savings rate today',
                           'markets': len(rows), 'capacity_usd': cap, 'usd_per_year_before_defaults': usd,
                           'usd_per_year_after_hist_defaults': usd - loss,
                           'net_apr_after_hist_defaults': ((usd - loss) / cap) if cap else None,
                           'top': [{'name': e['name'], 'protocol': e['protocol'], 'cls': e['cls'], 'expiry': e['expiry'][:10],
                                    'implied': e['implied'], 'trailing7': e['trailing7'], 'size_usd': b['size_usd'],
                                    'implied_after': b['implied_after'], 'edge': b['edge'], 'usd_per_year': b['usd_per_year'],
                                    'hist_default_loss_apr': e.get('hist_default_loss_apr'), 'tvl': e['tvl']}
                                   for e, b in sorted(rows, key=lambda eb: -eb[1]['usd_per_year'])[:15]]}

    n_variants = sum(len(r['variants']) for r in results.values())
    # One false-discovery control across every variant of every family, on the out-of-sample HAC p-values.
    flat = [(fam, name, v['oos_nw_p_lag_hold'], v['out_of_sample'].get('ann_return'))
            for fam, r in results.items() for name, v in r['variants'].items()]
    rej, adj = B.bh([x[2] for x in flat], q=0.10)
    global_bh = [{'family': f, 'variant': n, 'oos_apr': apr, 'oos_p': pv, 'bh_adj_p': ap, 'survives_q10': rj}
                 for (f, n, pv, apr), rj, ap in zip(flat, rej, adj)]
    a = {'generated': utc(), 'out': str(out), 'last_day': utc(last_day), 'cutoff': utc(cutoff),
         'cutoff_rule': 'median expiry of matured markets that ever held $1M of pool TVL, first of that month',
         'size_usd': args.size, 'min_tvl': args.min_tvl, 'hold_days_median': hold,
         'universe': universe, 'identities': identity_checks(markets),
         'benchmark': {'days': len(bench), 'first': utc(min(bench)) if bench else None,
                       'last': utc(max(bench)) if bench else None, 'now': bench_now,
                       'now_source': 'on-chain sUSDS.ssr() at latest (passed as --ssr-now)' if args.ssr_now is not None else 'Pendle sUSDS/sDAI series',
                       'series_last_value': bench_series_now,
                       'source_days': dict(collections.Counter(bench_src.values())),
                       'samples': {utc(d): bench[d] for d in sorted(bench)[::60]}},
         'fee_by_class_median': fee_by_class, 'recovery': recovery, 'blocked': blocked_block,
         'trades': {'n': len(trades), 'markets': len({tr['key'] for tr in trades}),
                    'by_class': collections.Counter(tr['cls'] for tr in trades),
                    'in_sample': sum(1 for tr in trades if tr['T'] <= cutoff),
                    'out_of_sample': sum(1 for tr in trades if tr['t0'] >= cutoff),
                    'straddling_cutoff_unused': sum(1 for tr in trades if tr['t0'] < cutoff < tr['T']),
                    'without_reserves_fee_only': sum(1 for tr in trades if not tr['reserves']),
                    **trade_build},
         'results': results, 'credit_buckets': credit, 'dollar_by_protocol': protocols, 'points_premium': points_premium,
         'sky_pts_vs_savings_rate': sky_block,
         'variants_tried': n_variants, 'global_bh_q10': global_bh, 'live_books': live_books, 'live': live[:80]}
    write_json(out / ('analysis%s.json' % args.suffix), a)
    write_json(out / ('trades%s.json.gz' % args.suffix), [{k: v for k, v in tr.items() if not k.startswith('_')} for tr in trades], gz=True)
    print(json.dumps({'trades': len(trades), 'cutoff': utc(cutoff), 'variants': n_variants,
                      'defaults': [(d['name'], round(d['ratio'], 3)) for d in recovery['defaults']][:20]}, indent=1))
    return 0



# --------------------------------------------------------------------------------------------------- render

def _pct(x, d=2):
    return '-' if x is None else ('%.' + str(d) + 'f%%') % (100 * x)


def _num(x, d=2):
    return '-' if x is None else ('%.' + str(d) + 'f') % x


def _usd(x):
    if x is None:
        return '-'
    a = abs(x)
    return ('$%.1fM' % (x / 1e6)) if a >= 1e6 else ('$%.0fk' % (x / 1e3)) if a >= 1e3 else '$%.0f' % x


def render_eval(title, ev):
    ct = ev['choose_then_test']
    lines = ['### %s' % title, '',
             'Chosen in sample: **%s** (of %d variants; out-of-sample rank %d; deflated Sharpe of the in-sample choice %s).'
             % (ct['chosen'], ct['n_variants'], ct['oos_rank'], _num(ct['deflated_sharpe_in_sample'], 3)), '',
             '| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag %dd) | OOS 95%% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |'
             % ev['nw_lag_days'],
             '|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|']
    for name, v in ev['variants'].items():
        i, o = v['in_sample'], v['out_of_sample']
        ti, to = v['trades_in_sample'], v['trades_out_of_sample']
        ci = v['oos_boot_mean_ci_apr']
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s to %s | %s | %s | %s | %s | %s |' % (
            name, _pct(i.get('ann_return')), _num(i.get('sharpe')), ti.get('n', 0), _pct(o.get('ann_return')),
            _num(o.get('sharpe')), _pct(o.get('max_drawdown')), _num(v['oos_nw_t_lag_hold']), _pct(ci[0]), _pct(ci[1]),
            to.get('n', 0), _pct(to.get('pooled_apr')), _pct(to.get('median_apr')), _pct(to.get('share_positive'), 0),
            'yes' if v['oos_bh_reject_q10'] else 'no'))
    if ev.get('chosen_oos_by_class'):
        lines += ['', 'Chosen variant out of sample, by class: ' + '; '.join(
            '%s %d trades, pooled %s, median %s, %s positive' % (c, st.get('n', 0), _pct(st.get('pooled_apr')),
                                                                 _pct(st.get('median_apr')), _pct(st.get('share_positive'), 0))
            for c, st in ev['chosen_oos_by_class'].items()) + '.']
    return lines + ['']


def cmd_render(args):
    out = Path(args.out)
    a = read_json(out / 'analysis.json')
    u = a['universe']
    L = ['# Pendle fixed vs floating — tables', '',
         'Generated %s from `analysis.json`; last data day %s; choose/test cutoff %s (%s); size %s per trade through '
         'the AMM; pool TVL at entry >= %s; median hold %.0f days; %d strategy variants tried in total.'
         % (a['generated'], a['last_day'][:10], a['cutoff'][:10], a['cutoff_rule'], _usd(a['size_usd']),
            _usd(a['min_tvl']), a['hold_days_median'], a['variants_tried']), '',
         '## Universe', '',
         '%d markets (%d matured, %d active). Listing: %s. History status: %s. Metadata status: %s.'
         % (u['markets'], u['matured'], u['active'], json.dumps(u['listed']), json.dumps(u['history_status']),
            json.dumps(u['meta_status'])), '',
         'Blocked by the API ("market is unsafe"): %d markets.' % len(u['blocked_history']), '']
    L += ['## Identities', '', '| check | n | median | p90 |', '|---|---:|---:|---:|']
    for k, v in a['identities'].items():
        L.append('| %s | %d | %s | %s |' % (k, v.get('n', 0), _num(v.get('median'), 5), _num(v.get('p90'), 5)))
    b = a['benchmark']
    L += ['', '## Benchmark', '', 'Sky savings rate from Pendle sUSDS/sDAI markets: %d days, %s to %s, now %s.'
          % (b['days'], (b['first'] or '-')[:10], (b['last'] or '-')[:10], _pct(b['now'])), '']
    r = a['recovery']
    L += ['## Recovery at maturity', '', 'All matured: %s. Dollar markets that ever held $1M: %s.'
          % (json.dumps(r['status_all_matured']), json.dumps(r['status_dollar_ever_1m'])), '',
          '| market | protocol | class | expiry | max pool TVL | recovery | first break | source |', '|---|---|---|---|---:|---:|---|---|']
    for d in r['defaults']:
        L.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (d['name'], d['protocol'], d['cls'], d['expiry'][:10],
                 _usd(d['max_tvl']), _num(d['ratio'], 3), (d['break_day'] or '-')[:10], d['source']))
    L += ['', '### Dollar markets whose PT holders lost more than 2% (from the trade panel)', '',
          '| market | protocol | expiry | max pool TVL | trades | recovery (min / max) | yield-token ratio | accounting move (source) | API / market reading | first break | spread at entry |',
          '|---|---|---|---:|---:|---|---:|---|---|---|---|']
    for d in r.get('dollar_losses', [])[:40]:
        L.append('| %s | %s | %s | %s | %d | %s / %s | %s | %s (%s) | %s / %s | %s | %s to %s |' % (
            d['name'], d['protocol'], d['expiry'][:10], _usd(d['max_tvl']), d['trades'], _num(d['recovery_min'], 3),
            _num(d['recovery_max'], 3), _num(d['ratio_recovery'], 3), _num(d['acct_move_min'], 3), ','.join(d['acct_move_source']),
            _num(d['acct_move_api_min'], 3), _num(d['acct_move_market_min'], 3), (d['break_day'] or '-')[:10],
            _pct(d['spread_min'], 1), _pct(d['spread_max'], 1)))
    agr = r.get('accounting_move_agreement_api_vs_market') or {}
    if agr:
        L += ['', 'Accounting-asset move, API reading against market reading, on %d dollar trades where both exist: median '
              'absolute difference %s, p90 %s, %s within 1%%. Source used: market %d, API %d.'
              % (agr['n'], _num(agr['median_abs_diff'], 4), _num(agr['p90_abs_diff'], 4), _pct(agr['share_within_1pct'], 0),
                 agr['dollar_trades_market_source'], agr['dollar_trades_api_source'])]
    L += ['']
    bl = a.get('blocked') or {}
    if bl:
        L += ['## Markets the API blocks', '',
              '%d markets answer "market is unsafe"; %d have transactions. PT bought in them: %s (the served panel traded %s '
              'in total). Matured dollar markets among them: %d, with %s of PT bought, %s of it priced; USD-weighted '
              'realised excess over the savings rate of those purchases: %s.'
              % (bl['markets'], bl['with_transactions'], _usd(bl['buy_pt_usd_total']), _usd(bl['panel_trading_volume_usd_total']),
                 bl['dollar_matured'], _usd(bl['dollar_matured_buy_pt_usd']), _usd(bl['dollar_matured_buy_pt_usd_priced']),
                 _pct(bl['dollar_matured_usd_weighted_excess_vs_ssr'])), '',
              '| market | class | expiry | tx | PT bought | priced | implied (USD-wtd) | min recovery | excess vs SSR (USD-wtd) | yield token prices |',
              '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
        for b in bl['markets_detail'][:25]:
            L.append('| %s | %s | %s | %d | %s | %s | %s | %s | %s | %d |' % (
                b['name'], b['cls'], (b['expiry'] or '-')[:10], b['tx'], _usd(b['buy_pt_usd']), _usd(b['buy_pt_usd_priced']),
                _pct(b['usd_weighted_implied']), _num(b['recovery_min'], 3), _pct(b['usd_weighted_excess_vs_ssr']),
                b['price_points']))
        L += ['']
    if a.get('dollar_by_protocol'):
        L += ['## Dollar trades by protocol (per trade, annualised, after defaults)', '',
              '| protocol | trades | markets | defaulted | promised spread | realised excess | worst trade | first entry | last expiry |',
              '|---|---:|---:|---:|---:|---:|---:|---|---|']
        for x in a['dollar_by_protocol'][:40]:
            L.append('| %s | %d | %d | %d | %s | %s | %s | %s | %s |' % (x['protocol'], x['trades'], x['markets'],
                     x['defaulted_markets'], _pct(x['mean_promised_spread_apr']), _pct(x['mean_realised_excess_apr']),
                     _pct(x['worst_trade_apr']), x['first_entry'][:10], x['last_expiry'][:10]))
        L += ['']
    for title, key in (('(a) PT minus floating, by class', 'a_pt_minus_floating_by_class'),
                       ('(b) PT when implied exceeds trailing-7d floating', 'b_pt_when_implied_over_trailing'),
                       ('(c) YT (interest only) when floating exceeds implied, against the savings rate', 'c_yt_when_floating_over_implied'),
                       ('(d) Dollar PT over the savings rate, by spread at entry, after defaults', 'd_dollar_pt_over_ssr_buckets'),
                       ('(d) Dollar PT over the savings rate, threshold rule, after defaults', 'd_dollar_pt_over_ssr_thresholds'),
                       ('(d) The same, defaults removed', 'd_dollar_pt_over_ssr_thresholds_ex_defaults'),
                       ('(d) Threshold rule, weighted by pool TVL at entry', 'd_dollar_pt_over_ssr_thresholds_tvl_weighted'),
                       ('(b) Implied over trailing, weighted by pool TVL at entry', 'b_pt_when_implied_over_trailing_tvl_weighted'),
                       ('(e) Dollar PT over the savings rate when implied clears the trailing floating, after defaults',
                        'e_dollar_pt_over_ssr_when_implied_over_trailing')):
        L += render_eval(title, a['results'][key])
    L += ['## Credit buckets (dollar PTs; rates pooled per capital-year)', '',
          '| spread over savings rate at entry | trades | markets | capital-years | defaulted markets | promised spread | default loss | realised excess | median trade | OOS trades | OOS default loss | OOS realised excess |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for c in a['credit_buckets']:
        L.append('| %s | %d | %d | %.1f | %d | %s | %s | %s | %s | %d | %s | %s |' % (
            c['bucket'], c['trades'], c['markets'], c['capital_years'], c['defaulted_markets'],
            _pct(c['mean_promised_spread_apr']), _pct(c['mean_default_loss_apr']), _pct(c['mean_realised_excess_apr']),
            _pct(c['median_realised_excess_apr']), c['oos_trades'], _pct(c['oos_default_loss_apr']),
            _pct(c['oos_realised_excess_apr'])))
    L += ['', '## What each family\'s in-sample choice would hold today', '',
          '| family | chosen | markets | capacity | $/yr before defaults | $/yr after historical default loss | net APR after defaults |',
          '|---|---|---:|---:|---:|---:|---:|']
    for fam, lb in (a.get('live_books') or {}).items():
        L.append('| %s | %s | %d | %s | %s | %s | %s |' % (fam, lb['chosen'], lb['markets'], _usd(lb['capacity_usd']),
                 _usd(lb['usd_per_year_before_defaults']), _usd(lb['usd_per_year_after_hist_defaults']),
                 _pct(lb['net_apr_after_hist_defaults'])))
    L += ['', '## Live board (top 25 by dollars a year at the size that maximises them)', '',
          '| market | class | points | days | pool TVL | implied | comparator | spread | best size | implied after | $/yr |',
          '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for x in a['live'][:25]:
        bst = x['best'] or {}
        L.append('| %s | %s | %s | %.0f | %s | %s | %s | %s | %s | %s | %s |' % (
            x['name'], x['cls'], 'y' if x['points'] else '', x['days'], _usd(x['tvl']), _pct(x['implied']),
            _pct(x['comparator']), _pct(x['spread']), _usd(bst.get('size_usd')), _pct(bst.get('implied_after')),
            _usd(bst.get('usd_per_year'))))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0


# --------------------------------------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.set_defaults(fn=cmd_collect)
    c.add_argument('--out', required=True)
    c.add_argument('--interval', type=float, default=0.25)
    c.add_argument('--cg-interval', type=float, default=7.0, help='seconds between CoinGecko contract lookups')
    c.add_argument('--refresh-lists', action='store_true')
    a = sub.add_parser('analyze')
    a.set_defaults(fn=cmd_analyze)
    a.add_argument('--out', required=True)
    a.add_argument('--size', type=float, default=100_000.0, help='USD bought per trade, priced through the AMM')
    a.add_argument('--min-tvl', type=float, default=1_000_000.0)
    a.add_argument('--cutoff', default=None, help='YYYY-MM-DD; default is the rule in the analysis')
    a.add_argument('--suffix', default='', help='write analysis<suffix>.json (sensitivity runs)')
    a.add_argument('--ssr-now', type=float, default=0.038,
                   help='Sky savings rate today as an APY, read on chain (sUSDS.ssr() = 3.80%% on 2026-10-09)')
    bn = sub.add_parser('bench')
    bn.set_defaults(fn=cmd_bench)
    bn.add_argument('--out', required=True)
    bl = sub.add_parser('blocked')
    bl.set_defaults(fn=cmd_blocked)
    bl.add_argument('--out', required=True)
    bl.add_argument('--interval', type=float, default=0.25)
    bl.add_argument('--cg-interval', type=float, default=7.0)
    r = sub.add_parser('render')
    r.set_defaults(fn=cmd_render)
    r.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
