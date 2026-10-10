#!/usr/bin/env python3
"""Every chain at once, from the aggregators: the census that turns "high activity" into a ranked list and "new
activity" into a deviation from a measured baseline.

Why an aggregator layer at all, when the rest of this repo reads chains directly. Two reasons. Breadth: DefiLlama tracks
~470 chains, growthepie and L2Beat ~100 rollups, Blockchair the UTXO and payment ledgers, and no set of hand-written
probes will cover that in a session. History: every one of these sources serves a *daily series* going back months,
which is what a detector needs before it can call anything "new" — a probe that started today has no baseline, the
census has one on its first run. The direct probe (`chain_probe.py`) is the second, independent reading of the chains
that matter, and `chain_activity.py verify` holds the two against each other.

What each source contributes, keyed to one canonical chain row:

    DefiLlama   TVL, DEX volume (24h/7d/30d + daily history), fees (history), stablecoin float (history, and per
                asset with 1d/7d/30d changes), native-token CoinGecko id, EVM chain id
    growthepie  daily transactions, active addresses, stablecoin float for ~27 Ethereum rollups and Ethereum
    L2Beat      daily transactions and user operations for ~100 rollups (one year of history)
    Blockchair  trailing-24h transactions and gross output volume for UTXO chains, XRPL, Stellar, Cardano
    Tronscan    Tron's daily transactions and USDT transfer count (15 days)
    NEARBlocks  NEAR's daily transactions (full history)
    CoinGecko   native-token spot volume and market cap: can the token itself be traded, off chain
    Hyperliquid perp volume and open interest per coin: can the token be hedged

Identity is discovered, not typed: DefiLlama's internal chain keys (the coins-API prefix, and the keys of every DEX
breakdown) are inferred from single-chain protocols, growthepie rows join on EVM chain id, and the registry's `ids` are
only overrides, each of which `build` checks resolves to a real row.

    uv run python scripts/chain_census.py fetch --out research/2026-10-09/chains      # network, ~3-5 min, raw/ cache
    uv run python scripts/chain_census.py build --out research/2026-10-09/chains      # offline -> census.json
    uv run python scripts/chain_census.py show  --out research/2026-10-09/chains Base # one chain's row
"""
import argparse
import collections
import concurrent.futures as cf
import datetime as dt
import gzip
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from chain_adapters import Http, sha  # noqa: E402

REGISTRY = ROOT / 'scripts' / 'chain_registry.json'
LLAMA = 'https://api.llama.fi'
STABLES = 'https://stablecoins.llama.fi'
GTP = 'https://api.growthepie.com/v1'
L2BEAT = 'https://l2beat.com/api/scaling'
HISTORY_DAYS = 400          # daily points kept per series (the detectors use ~120)
HISTORY_UNIVERSE = 220      # chains whose full DefiLlama history is fetched (top by DEX, stables, TVL, fees + registry)

# DefiLlama rows that are not chains: off-chain venues booked under a pseudo-chain
NOT_CHAINS = {'Off Chain', 'off_chain'}

# gas tokens that many chains borrow -> the one registry slug where that token is the chain's own
BORROWED_GAS = {'ethereum': 'ethereum', 'binancecoin': 'bsc', 'usd-coin': None, 'tether': None}

# floors that decide which chains are worth a history fetch at all; a chain below every one of these is listed but not
# followed (it has no on-chain economy to trade against and no throughput worth a baseline)
UNIVERSE_FLOORS = {'dex_24h': 50_000, 'stables': 1_000_000, 'tvl': 2_000_000, 'fees_24h': 5_000}


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def day_of(ts):
    return dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).strftime('%Y-%m-%d')


def write_gz(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(value, f, separators=(',', ':'))
    tmp.replace(path)


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def load_registry():
    return json.loads(REGISTRY.read_text())


def norm(name):
    """Loose name key for joining sources that have no shared id (L2Beat, Blockchair)."""
    s = (name or '').lower()
    s = re.sub(r'\b(chain|mainnet|network|one|l1|l2|smart|protocol|blockchain)\b', ' ', s)
    return re.sub(r'[^a-z0-9]', '', s)


# ---------------------------------------------------------------------------------------------- fetch

class Fetcher:
    def __init__(self, out):
        self.raw = Path(out) / 'raw'
        self.raw.mkdir(parents=True, exist_ok=True)
        self.http = Http(min_interval=0.0, timeout=90, retries=4)
        # per-host pacing: DefiLlama tolerates ~10/s, CoinGecko's free tier ~10-30/min, the rest are one-shot
        self.http.host_interval.update({'api.llama.fi': 0.12, 'stablecoins.llama.fi': 0.12, 'coins.llama.fi': 0.2,
                                        'api.coingecko.com': 6.5, 'l2beat.com': 0.3, 'api.blockchair.com': 2.0,
                                        'api.hyperliquid.xyz': 0.5})
        self.status = {}

    def get(self, name, url, body=None, timeout=None):
        t0 = time.time()
        try:
            d = self.http.post(url, body, timeout=timeout) if body is not None else self.http.get(url, timeout=timeout)
            self.status[name] = {'ok': True, 'url': url, 'seconds': round(time.time() - t0, 2), 'fetched_utc': utc_now().isoformat(timespec='seconds')}
            return d
        except Exception as e:
            self.status[name] = {'ok': False, 'url': url, 'error': str(e)[:200], 'fetched_utc': utc_now().isoformat(timespec='seconds')}
            return None

    def save(self, name, value):
        if value is not None:
            write_gz(self.raw / ('%s.json.gz' % name), value)


def infer_llama_keys(dexs, fees=None):
    """DefiLlama internal chain key -> display name, from protocols that live on exactly one chain.

    The DEX and fee breakdowns are keyed by internal names ('avax', 'xdai', 'era', 'klaytn', 'wc', 'hyperliquid'),
    the chain list by display names ('Avalanche', 'Gnosis', ...). A protocol deployed on one chain names both, so the
    mapping falls out of the data; where two protocols disagree the majority wins and the vote is kept as evidence.
    """
    votes = collections.defaultdict(collections.Counter)
    for src in (dexs, fees):
        for p in (src or {}).get('protocols') or []:
            ch = p.get('chains') or []
            bk = list((p.get('breakdown24h') or {}).keys())
            if len(ch) == 1 and len(bk) == 1:
                votes[bk[0]][ch[0]] += 1
    out = {}
    for k, c in votes.items():
        name, n = c.most_common(1)[0]
        out[k] = {'name': name, 'votes': n, 'contested': len(c) > 1}
    return out


def breakdown_by_key(overview):
    """Sum each protocol's 24h breakdown per internal chain key."""
    tot = collections.Counter()
    for p in (overview or {}).get('protocols') or []:
        for k, v in (p.get('breakdown24h') or {}).items():
            tot[k] += sum(x for x in v.values() if isinstance(x, (int, float)))
    return tot


def cmd_fetch(args):
    out = Path(args.out)
    F = Fetcher(out)
    reg = load_registry()
    t0 = time.time()

    # ---- one-call sources (in parallel; each host is paced separately)
    one = {
        'llama_chains': (LLAMA + '/v2/chains', None),
        'llama_dexs': (LLAMA + '/overview/dexs?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true', None),
        'llama_fees': (LLAMA + '/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true', None),
        'llama_stablecoinchains': (STABLES + '/stablecoinchains', None),
        'llama_stablecoins': (STABLES + '/stablecoins?includePrices=true', None),
        'growthepie_fundamentals': (GTP + '/fundamentals.json', None),
        'growthepie_master': (GTP + '/master.json', None),
        'l2beat_summary': (L2BEAT + '/summary', None),
        'blockchair_stats': ('https://api.blockchair.com/stats', None),
        'tronscan_bundle': ('https://apilist.tronscanapi.com/api/system/homepage-bundle', None),
        'nearblocks_charts': ('https://api.nearblocks.io/v1/charts', None),
        'hyperliquid_meta': ('https://api.hyperliquid.xyz/info', {'type': 'metaAndAssetCtxs'}),
        'hyperliquid_spot': ('https://api.hyperliquid.xyz/info', {'type': 'spotMetaAndAssetCtxs'}),
    }
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(F.get, name, url, body): name for name, (url, body) in one.items()}
        for f in cf.as_completed(futs):
            F.save(futs[f], f.result())
    print(json.dumps({k: v.get('ok') for k, v in F.status.items()}), flush=True)

    chains = read_gz(F.raw / 'llama_chains.json.gz') if (F.raw / 'llama_chains.json.gz').exists() else []
    dexs = read_gz(F.raw / 'llama_dexs.json.gz') if (F.raw / 'llama_dexs.json.gz').exists() else {}
    fees = read_gz(F.raw / 'llama_fees.json.gz') if (F.raw / 'llama_fees.json.gz').exists() else {}
    stc = read_gz(F.raw / 'llama_stablecoinchains.json.gz') if (F.raw / 'llama_stablecoinchains.json.gz').exists() else []
    keys = infer_llama_keys(dexs, fees)
    name_of_key = {k: v['name'] for k, v in keys.items()}
    dex24 = {name_of_key.get(k, k): v for k, v in breakdown_by_key(dexs).items()}
    fee24 = {name_of_key.get(k, k): v for k, v in breakdown_by_key(fees).items()}
    st = {x['name']: (x.get('totalCirculatingUSD') or {}).get('peggedUSD') or 0 for x in stc}
    tvl = {c['name']: c.get('tvl') or 0 for c in chains}

    # ---- the history universe: anything above a floor on any axis, capped, plus every registry chain
    names = set(tvl) | set(st) | set(dex24) | set(fee24)
    def rank(d):
        return [n for n, _ in sorted(d.items(), key=lambda kv: -kv[1])]
    picked = []
    for d, floor in ((dex24, UNIVERSE_FLOORS['dex_24h']), (st, UNIVERSE_FLOORS['stables']),
                     (tvl, UNIVERSE_FLOORS['tvl']), (fee24, UNIVERSE_FLOORS['fees_24h'])):
        picked += [n for n in rank(d) if d.get(n, 0) >= floor][:HISTORY_UNIVERSE]
    for c in reg['chains']:
        n = (c.get('ids') or {}).get('defillama')
        if n:
            picked.append(n)
    universe = [n for n in dict.fromkeys(picked) if n in names]
    if args.max_history:
        universe = universe[:args.max_history]
    print('history universe: %d chains' % len(universe), flush=True)

    def hist(name):
        q = urllib.parse.quote(name)
        res = {}
        d = F.get('dex:' + name, LLAMA + '/overview/dexs/%s?excludeTotalDataChartBreakdown=true' % q)
        if d:
            res['dex'] = d.get('totalDataChart') or []
            res['dex_meta'] = {k: d.get(k) for k in ('total24h', 'total48hto24h', 'total7d', 'total14dto7d', 'total30d', 'total60dto30d', 'change_1d', 'change_7d', 'change_7dover7d', 'change_30dover30d')}
        s = F.get('stables:' + name, STABLES + '/stablecoincharts/%s' % q)
        if s:
            res['stables'] = stable_points(s)
        t = F.get('tvl:' + name, LLAMA + '/v2/historicalChainTvl/%s' % q)
        if t:
            res['tvl'] = [[int(x['date']), x.get('tvl') or 0] for x in t if isinstance(x, dict)]
        if not args.no_fees and fee24.get(name, 0) >= UNIVERSE_FLOORS['fees_24h']:
            fz = F.get('fees:' + name, LLAMA + '/overview/fees/%s?excludeTotalDataChartBreakdown=true' % q, timeout=120)
            if fz:
                res['fees'] = fz.get('totalDataChart') or []
        cut = time.time() - HISTORY_DAYS * 86400
        for k in ('dex', 'stables', 'tvl', 'fees'):
            if k in res:
                # None stays None: complete_days drops it, so a gap is a gap rather than a zero day
                res[k] = [[int(a), None if b is None else float(b)] for a, b in res[k] if int(a) >= cut]
        return name, res

    H = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, (name, res) in enumerate(ex.map(hist, universe)):
            H[name] = res
            if (i + 1) % 25 == 0:
                print('  history %d/%d (%.0fs)' % (i + 1, len(universe), time.time() - t0), flush=True)
    write_gz(F.raw / 'llama_history.json.gz', H)

    # ---- L2Beat per-project activity, one year
    summ = read_gz(F.raw / 'l2beat_summary.json.gz') if (F.raw / 'l2beat_summary.json.gz').exists() else {}
    projects = [p for p, v in ((summ or {}).get('projects') or {}).items() if not v.get('isArchived')]

    def l2(pid):
        d = F.get('l2beat:' + pid, L2BEAT + '/activity/%s?range=1y' % pid)
        try:
            return pid, d['data']['chart']['data'] if d else None
        except Exception:
            return pid, None
    L2 = {}
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for pid, rows in ex.map(l2, projects):
            if rows:
                L2[pid] = rows
    write_gz(F.raw / 'l2beat_activity.json.gz', L2)

    # ---- CoinGecko markets for native tokens (spot tradeability), 250 ids per call
    gecko = sorted({c.get('gecko_id') for c in chains if c.get('gecko_id') and (tvl.get(c['name'], 0) >= 1e6 or st.get(c['name'], 0) >= 1e6 or dex24.get(c['name'], 0) >= 1e5)} |
                   {(c.get('native') or {}).get('coingecko') for c in reg['chains'] if (c.get('native') or {}).get('coingecko')})
    G = []
    for i in range(0, len(gecko), 250):
        part = gecko[i:i + 250]
        d = F.get('coingecko:%d' % i, 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=250&ids=' + ','.join(part))
        if isinstance(d, list):
            G += d
    write_gz(F.raw / 'coingecko_markets.json.gz', G)

    write_gz(F.raw / 'llama_keys.json.gz', keys)
    meta = {'fetched_utc': utc_now().isoformat(timespec='seconds'), 'seconds': round(time.time() - t0, 1),
            'history_universe': len(universe), 'l2beat_projects': len(L2), 'coingecko_ids': len(G),
            'status': F.status, 'http': F.http.stats()}
    (Path(out) / 'raw' / 'fetch_meta.json').write_text(json.dumps(meta, indent=1, sort_keys=True))
    bad = {k: v.get('error') for k, v in F.status.items() if not v.get('ok')}
    print(json.dumps({'seconds': meta['seconds'], 'universe': len(universe), 'l2beat': len(L2), 'gecko': len(G),
                      'failed_requests': len(bad)}, indent=1))
    if bad:
        print('failed (first 12):', json.dumps(dict(list(bad.items())[:12]), indent=1))


# ---------------------------------------------------------------------------------------------- build

def stable_points(rows):
    """DefiLlama's per-chain stablecoin history as [[ts, usd or None]]. A day it could not compute is written as
    `totalCirculatingUSD: {}`; read as zero, every gap's recovery looks like stablecoins arriving (the history had
    Linea at $0 on 2026-08-28, Zilliqa with 108 missing days, Secret with 794). Missing stays missing."""
    return [[int(x['date']), (x.get('totalCirculatingUSD') or {}).get('peggedUSD')] for x in rows if isinstance(x, dict)]


def complete_days(series, today):
    """[[ts|date, v], ...] -> {YYYY-MM-DD: v} for days strictly before `today` (a partial day is never a reading)."""
    out = {}
    for row in series or []:
        a, v = row[0], row[1]
        d = a if isinstance(a, str) else day_of(a)
        if d < today and v is not None:
            out[d] = float(v)
    return dict(sorted(out.items()))


def last(series_d, n=1):
    vals = list(series_d.values())
    return vals[-n:] if vals else []


def tier_of(now):
    """How reasonable it is to trade on (or around) this chain, from what is measurable about its liquidity.

    deep        an on-chain market a size-able strategy can use: $100M+/day DEX or $1B+ of stables with $10M+/day DEX
    tradeable   $1M+/day DEX and $10M+ of stables: entries and exits exist on chain
    token_only  the chain's own token is liquid off chain (CoinGecko $10M+/day or a Hyperliquid perp $1M+/day) but its
                on-chain economy is below `tradeable`: activity there is a signal to trade the token, not on the chain
    thin        some on-chain market ($100k+/day DEX or $1M+ stables) but not enough to enter and leave
    inactive    none of the above
    """
    dex = now.get('dex_7d_avg') or now.get('dex_24h') or 0
    st = now.get('stables') or 0
    tok = max(now.get('native_volume_24h') or 0, 0)
    perp = now.get('perp_volume_24h') or 0
    if dex >= 100e6 or (st >= 1e9 and dex >= 10e6):
        return 'deep'
    if dex >= 1e6 and st >= 10e6:
        return 'tradeable'
    if tok >= 10e6 or perp >= 1e6:
        return 'token_only'
    if dex >= 1e5 or st >= 1e6:
        return 'thin'
    return 'inactive'


TIER_ORDER = {'deep': 0, 'tradeable': 1, 'token_only': 2, 'thin': 3, 'inactive': 4}


def pct_ranks(values):
    """value -> percentile rank in (0, 1], ties share the higher rank; None stays None."""
    xs = sorted(v for v in values.values() if v is not None and v > 0)
    n = len(xs)
    out = {}
    import bisect
    for k, v in values.items():
        if v is None or v <= 0 or not n:
            out[k] = None
        else:
            out[k] = bisect.bisect_right(xs, v) / n
    return out


def cmd_build(args):
    out = Path(args.out)
    raw = out / 'raw'
    R = lambda n: read_gz(raw / ('%s.json.gz' % n)) if (raw / ('%s.json.gz' % n)).exists() else None
    reg = load_registry()
    today = utc_now().strftime('%Y-%m-%d') if not args.today else args.today
    chains = R('llama_chains') or []
    dexs, fees = R('llama_dexs') or {}, R('llama_fees') or {}
    keys = R('llama_keys') or infer_llama_keys(dexs, fees)
    name_of_key = {k: v['name'] for k, v in keys.items()}
    key_of_name = {}
    for k, v in keys.items():
        key_of_name.setdefault(v['name'], k)
    stc = R('llama_stablecoinchains') or []
    sts = (R('llama_stablecoins') or {}).get('peggedAssets') or []
    H = R('llama_history') or {}
    gtp = R('growthepie_fundamentals') or []
    gtpm = (R('growthepie_master') or {}).get('chains') or {}
    l2s = (R('l2beat_summary') or {}).get('projects') or {}
    L2 = R('l2beat_activity') or {}
    bc = (R('blockchair_stats') or {}).get('data') or {}
    tron = R('tronscan_bundle') or {}
    near = (R('nearblocks_charts') or {}).get('charts') or []
    G = R('coingecko_markets') or []
    hlm = R('hyperliquid_meta')

    rows = {}
    def row(name):
        r = rows.get(name)
        if r is None:
            r = rows[name] = {'name': name, 'slug': None, 'family': None, 'layer': None, 'evm_chain_id': None,
                              'gecko_id': None, 'symbol': None, 'llama_key': key_of_name.get(name),
                              'now': {}, 'series': {}, 'sources': [], 'stables_by_asset': []}
        return r

    for c in chains:
        r = row(c['name'])
        r.update({'evm_chain_id': c.get('chainId'), 'gecko_id': c.get('gecko_id'), 'symbol': c.get('tokenSymbol')})
        r['now']['tvl'] = c.get('tvl')
        r['sources'].append('defillama')
    for k, v in breakdown_by_key(dexs).items():
        r = row(name_of_key.get(k, k))
        r['now']['dex_24h'] = v
        r['llama_key'] = r['llama_key'] or k
    for k, v in breakdown_by_key(fees).items():
        row(name_of_key.get(k, k))['now']['fees_24h'] = v
    for x in stc:
        row(x['name'])['now']['stables'] = (x.get('totalCirculatingUSD') or {}).get('peggedUSD') or 0

    # per-asset stablecoin float with its own 1d/7d/30d changes: which dollar is arriving where
    per_chain_assets = collections.defaultdict(list)
    for a in sts:
        for ch, v in (a.get('chainCirculating') or {}).items():
            def usd(x):
                # an empty object means DefiLlama has no reading for that date, which is not the same as zero:
                # treating it as zero turns every stablecoin with a gap in its history into a "new" one
                if not isinstance(x, dict) or 'peggedUSD' not in x:
                    return None
                return x.get('peggedUSD') or 0.0
            cur = usd(v.get('current')) or 0.0
            if cur <= 0 and not usd(v.get('circulatingPrevMonth')):
                continue
            per_chain_assets[ch].append({'symbol': a.get('symbol'), 'name': a.get('name'), 'id': a.get('id'),
                                         'peg': a.get('pegType'), 'usd': cur, 'prev_day': usd(v.get('circulatingPrevDay')),
                                         'prev_week': usd(v.get('circulatingPrevWeek')), 'prev_month': usd(v.get('circulatingPrevMonth'))})
    for ch, lst in per_chain_assets.items():
        lst.sort(key=lambda x: -x['usd'])
        row(ch)['stables_by_asset'] = lst[:15]

    # daily DefiLlama history
    for name, res in H.items():
        r = row(name)
        for k in ('dex', 'stables', 'tvl', 'fees'):
            if res.get(k):
                r['series'][k] = complete_days(res[k], today)
        if res.get('dex_meta'):
            r['now']['dex_7d'] = res['dex_meta'].get('total7d')
            r['now']['dex_30d'] = res['dex_meta'].get('total30d')

    # registry identities first (they are the overrides), then the joins that need them
    reg_by_name, warnings = {}, []
    for c in reg['chains']:
        ids = c.get('ids') or {}
        name = ids.get('defillama') or c['name']
        if ids.get('defillama') and ids['defillama'] not in rows:
            warnings.append('registry %s: defillama name %r not found' % (c['slug'], ids['defillama']))
        if c['slug'] == 'hyperliquid':
            continue   # HyperCore and HyperEVM share DefiLlama's "Hyperliquid L1" row; the EVM entry owns it
        r = row(name)
        if r['slug'] and r['slug'] != c['slug']:
            continue
        r.update({'slug': c['slug'], 'family': c.get('family'), 'layer': c.get('layer')})
        if c.get('evm_chain_id') and not r['evm_chain_id']:
            r['evm_chain_id'] = c['evm_chain_id']
        if ids.get('llama_key'):
            if r['llama_key'] and r['llama_key'] != ids['llama_key'] and ids['llama_key'] in keys:
                warnings.append('registry %s: llama_key %s, inferred %s' % (c['slug'], ids['llama_key'], r['llama_key']))
            r['llama_key'] = ids['llama_key']
        # The chain's *own* token decides "token_only" tradeability, so a rollup that only borrows ETH (or USDC, or BNB)
        # as gas must not inherit that token's market: only DefiLlama's id, or the registry's when the token is home here.
        g = (c.get('native') or {}).get('coingecko')
        if g and not r['gecko_id'] and BORROWED_GAS.get(g, c['slug']) == c['slug']:
            r['gecko_id'] = g
        if not r['symbol']:
            r['symbol'] = (c.get('native') or {}).get('symbol')
        reg_by_name[name] = c

    # growthepie: join on EVM chain id, registry key as the override
    by_cid = {r['evm_chain_id']: n for n, r in rows.items() if r.get('evm_chain_id')}
    gkey_to_name = {}
    for c in reg['chains']:
        if (c.get('ids') or {}).get('growthepie'):
            gkey_to_name[c['ids']['growthepie']] = (c.get('ids') or {}).get('defillama') or c['name']
    for k, v in gtpm.items():
        if k not in gkey_to_name and v.get('evm_chain_id') in by_cid:
            gkey_to_name[k] = by_cid[v['evm_chain_id']]
    gser = collections.defaultdict(lambda: collections.defaultdict(dict))
    for x in gtp:
        gser[x['origin_key']][x['metric_key']][x['date']] = x['value']
    for k, metrics in gser.items():
        name = gkey_to_name.get(k)
        if not name:
            continue
        r = row(name)
        r['sources'].append('growthepie')
        for metric, src in (('txcount', 'tx_growthepie'), ('daa', 'daa_growthepie'), ('stables_mcap', 'stables_growthepie')):
            if metrics.get(metric):
                r['series'][src] = complete_days(sorted(metrics[metric].items()), today)

    # L2Beat: registry key, else a loose name match
    lkey_to_name = {}
    for c in reg['chains']:
        if (c.get('ids') or {}).get('l2beat'):
            lkey_to_name[c['ids']['l2beat']] = (c.get('ids') or {}).get('defillama') or c['name']
    nmap = {norm(n): n for n in rows}
    for pid, v in l2s.items():
        if pid not in lkey_to_name:
            n = nmap.get(norm(v.get('name'))) or nmap.get(norm(pid))
            if n:
                lkey_to_name[pid] = n
    for pid, data in L2.items():
        name = lkey_to_name.get(pid) or (l2s.get(pid) or {}).get('name') or pid
        r = row(name)
        r['sources'].append('l2beat')
        if not r['layer']:
            r['layer'] = {'layer2': 'L2', 'layer3': 'L3'}.get((l2s.get(pid) or {}).get('type'))
        r['l2beat_id'] = pid
        r['series']['tx_l2beat'] = complete_days([[t, c] for t, c, *_ in data], today)
        r['series']['uops_l2beat'] = complete_days([[t, u] for t, _, u, *_ in data if u is not None], today)

    # Blockchair trailing 24h (not a calendar day: kept in `now` only)
    bkey_to_name = {}
    for c in reg['chains']:
        if (c.get('ids') or {}).get('blockchair'):
            bkey_to_name[c['ids']['blockchair']] = (c.get('ids') or {}).get('defillama') or c['name']
    for k, v in bc.items():
        d = (v or {}).get('data') or {}
        if not isinstance(d, dict) or 'transactions_24h' not in d:
            continue
        r = row(bkey_to_name.get(k) or k)
        r['sources'].append('blockchair')
        r['now']['tx_24h_blockchair'] = d.get('transactions_24h')
        r['now']['blockchair_best_time'] = d.get('best_block_time') or d.get('best_ledger_time')

    # Tronscan: daily rows
    so = ((tron.get('statsOverview') or {}).get('data')) or []
    if so:
        r = row('Tron')
        r['sources'].append('tronscan')
        r['series']['tx_tronscan'] = complete_days([[x['dateDayStr'], x.get('newTransactionSeen')] for x in so], today)
        r['series']['usdt_tx_tronscan'] = complete_days([[x['dateDayStr'], x.get('usdt_transaction')] for x in so], today)
        r['series']['daa_tronscan'] = complete_days([[x['dateDayStr'], x.get('active_account_number')] for x in so], today)
    if near:
        r = row('Near')
        r['sources'].append('nearblocks')
        r['series']['tx_nearblocks'] = complete_days([[x['date'][:10], float(x.get('txns') or 0)] for x in near][-HISTORY_DAYS:], today)
        r['series']['daa_nearblocks'] = complete_days([[x['date'][:10], float(x.get('active_accounts') or 0)] for x in near][-HISTORY_DAYS:], today)

    # tradeability of the native token: CoinGecko spot, Hyperliquid perp (main dex; the coin name is the symbol)
    gk = {g['id']: g for g in G if isinstance(g, dict)}
    perp = {}
    if isinstance(hlm, list) and len(hlm) == 2:
        for u, ctxm in zip(hlm[0].get('universe') or [], hlm[1]):
            if u.get('isDelisted'):
                continue
            px = float(ctxm.get('markPx') or 0)
            perp[u['name'].upper()] = {'volume_24h': float(ctxm.get('dayNtlVlm') or 0), 'oi_usd': float(ctxm.get('openInterest') or 0) * px}
    for name, r in rows.items():
        g = gk.get(r.get('gecko_id'))
        if not g:
            continue
        r['now']['native_volume_24h'] = g.get('total_volume')
        r['now']['native_mcap'] = g.get('market_cap')
        r['now']['native_change_24h_pct'] = g.get('price_change_percentage_24h')
        sym = (g.get('symbol') or '').upper()
        r['symbol'] = r['symbol'] or sym
        pp = perp.get(sym) or perp.get('K' + sym)   # Hyperliquid lists low-priced coins in thousands (kPEPE)
        if pp:
            r['now']['perp_volume_24h'] = pp['volume_24h']
            r['now']['perp_oi_usd'] = pp['oi_usd']
            r['now']['perp_coin'] = sym

    # derived 'now' fields and the best daily transaction series
    for name, r in rows.items():
        s = r['series']
        n = r['now']
        if s.get('dex'):
            v = last(s['dex'], 7)
            n['dex_7d_avg'] = sum(v) / len(v)
            n['dex_last_day'] = v[-1]
        if s.get('fees'):
            v = last(s['fees'], 7)
            n['fees_7d_avg'] = sum(v) / len(v)
        for src in ('tx_growthepie', 'tx_l2beat', 'tx_tronscan', 'tx_nearblocks'):
            if s.get(src):
                s['tx'] = s[src]
                n['tx_source'] = src.replace('tx_', '')
                v = last(s[src], 7)
                n['tx_last_day'] = v[-1]
                n['tx_7d_avg'] = sum(v) / len(v)
                break
        if 'tx_7d_avg' not in n and n.get('tx_24h_blockchair'):
            n['tx_7d_avg'] = n['tx_24h_blockchair']
            n['tx_source'] = 'blockchair-24h'
        st = s.get('stables') or {}
        if st:
            vals = list(st.values())
            n['stables_7d_change'] = vals[-1] - vals[-8] if len(vals) >= 8 else None
            n['stables_30d_change'] = vals[-1] - vals[-31] if len(vals) >= 31 else None
        first = [min(s[k]) for k in ('dex', 'stables', 'tx', 'tvl') if s.get(k)]
        n['first_seen'] = min(first) if first else None
        r['tier'] = tier_of(n)
        r['sources'] = sorted(set(r['sources']))

    for k in [k for k in rows if k in NOT_CHAINS]:
        del rows[k]
    # composite activity rank over five axes (percentile within the axis), needing at least three of them
    axes = {'dex': {k: r['now'].get('dex_7d_avg') or r['now'].get('dex_24h') for k, r in rows.items()},
            'fees': {k: r['now'].get('fees_7d_avg') or r['now'].get('fees_24h') for k, r in rows.items()},
            'stables': {k: r['now'].get('stables') for k, r in rows.items()},
            'tvl': {k: r['now'].get('tvl') for k, r in rows.items()},
            'tx': {k: r['now'].get('tx_7d_avg') for k, r in rows.items()}}
    P = {a: pct_ranks(v) for a, v in axes.items()}
    for k, r in rows.items():
        got = {a: P[a][k] for a in P if P[a].get(k) is not None}
        r['activity'] = {'axes': got, 'score': (sum(got.values()) / len(got)) if len(got) >= 3 else None, 'n_axes': len(got)}

    ranked = sorted(rows.values(), key=lambda r: (-(r['activity']['score'] or -1), TIER_ORDER[r['tier']]))
    for r in ranked:
        # what is committed is what the detectors read: ~200 days, compact, and none for chains with nothing to detect
        r['series'] = {} if r['tier'] == 'inactive' else {k: compact(v, KEEP_DAYS) for k, v in r['series'].items() if v}
    census = {'generated_utc': utc_now().isoformat(timespec='seconds'), 'today': today,
              'fetch': json.loads((raw / 'fetch_meta.json').read_text()) if (raw / 'fetch_meta.json').exists() else None,
              'registry_sha': sha(REGISTRY.read_text()), 'llama_keys': keys, 'warnings': warnings,
              'tier_rule': tier_of.__doc__.strip(), 'n_chains': len(rows),
              'tiers': dict(collections.Counter(r['tier'] for r in rows.values())),
              'chains': {r['name']: r for r in ranked}}
    (out / 'census.json').write_text(json.dumps(census, separators=(',', ':'), default=str))
    print(json.dumps({'chains': len(rows), 'tiers': census['tiers'], 'warnings': warnings[:20]}, indent=1))
    print('\n%-22s %-10s %6s %10s %10s %10s %10s %10s  %s' % ('chain', 'tier', 'score', 'DEX/day', 'stables', 'TVL', 'fees/day', 'tx/day', 'tx source'))
    for r in ranked[:args.top]:
        n = r['now']
        print('%-22s %-10s %6s %10s %10s %10s %10s %10s  %s' % (
            r['name'][:22], r['tier'], ('%.2f' % r['activity']['score']) if r['activity']['score'] is not None else '-',
            m(n.get('dex_7d_avg') or n.get('dex_24h')), m(n.get('stables')), m(n.get('tvl')),
            m(n.get('fees_7d_avg') or n.get('fees_24h')), m(n.get('tx_7d_avg'), dollar=False), n.get('tx_source') or ''))


KEEP_DAYS = 200


def compact(daily, keep=KEEP_DAYS):
    """{YYYY-MM-DD: v} -> {'start': first day, 'v': [one value per day, None where the source had no reading]}."""
    ds = sorted(daily)[-keep:]
    if not ds:
        return {'start': None, 'v': []}
    d0 = dt.date.fromisoformat(ds[0])
    n = (dt.date.fromisoformat(ds[-1]) - d0).days + 1
    vals = [None] * n
    for d in ds:
        x = daily[d]
        vals[(dt.date.fromisoformat(d) - d0).days] = round(x, 2) if isinstance(x, float) and abs(x) < 1e6 else (round(x) if x is not None else None)
    return {'start': ds[0], 'v': vals}


def expand(c):
    """The inverse of `compact`."""
    if isinstance(c, dict) and 'v' in c:
        if not c.get('start'):
            return {}
        d0 = dt.date.fromisoformat(c['start'])
        return {(d0 + dt.timedelta(days=i)).isoformat(): float(x) for i, x in enumerate(c['v']) if x is not None}
    return c or {}


def load_census(out):
    """census.json with every series expanded back to {day: value}."""
    p = Path(out) / 'census.json'
    if not p.exists():
        return None
    C = json.loads(p.read_text())
    for r in C['chains'].values():
        r['series'] = {k: expand(v) for k, v in (r.get('series') or {}).items()}
    return C


def m(v, dollar=True):
    if v is None:
        return '-'
    v = float(v)
    for u, d in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= d:
            return ('$' if dollar else '') + '%.1f%s' % (v / d, u)
    return ('$' if dollar else '') + '%.0f' % v


def cmd_show(args):
    C = load_census(args.out)
    r = C['chains'].get(args.name) or next((v for k, v in C['chains'].items() if k.lower() == args.name.lower() or v.get('slug') == args.name), None)
    if not r:
        raise SystemExit('no chain %r' % args.name)
    r = dict(r)
    r['series'] = {k: dict(list(v.items())[-14:]) for k, v in r['series'].items()}
    print(json.dumps(r, indent=1, default=str))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('fetch')
    a.add_argument('--out', required=True)
    a.add_argument('--workers', type=int, default=6)
    a.add_argument('--max-history', type=int, default=0, help='cap the history universe (testing)')
    a.add_argument('--no-fees', action='store_true', help='skip per-chain fee history (the slowest endpoint)')
    b = sub.add_parser('build')
    b.add_argument('--out', required=True)
    b.add_argument('--today', help='treat this UTC date as today (days before it are complete)')
    b.add_argument('--top', type=int, default=60)
    c = sub.add_parser('show')
    c.add_argument('--out', required=True)
    c.add_argument('name')
    args = p.parse_args()
    {'fetch': cmd_fetch, 'build': cmd_build, 'show': cmd_show}[args.cmd](args)


if __name__ == '__main__':
    main()
