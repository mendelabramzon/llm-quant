#!/usr/bin/env python3
"""Incentive-adjusted dollar yields: is a patient allocator paid by protocols' marketing budgets? (brainstorm 5.4)

Why. Protocols and chains spend fixed token budgets to rent deposits. A fixed budget is diluted by whoever arrives, and
attention, not speed, decides who arrives: an allocator who reads the rates once a week and moves when the incentive
pays should be able to collect part of that spend. The repo's prior is that a fixed rate far above the benchmark is
usually credit risk (dollar Pendle PTs above the savings rate lost -8.2%/yr after defaults), so the test nets
everything that can go wrong: the reward token falls before it is sold, the deposit dilutes its own reward and base
rate, switching costs gas and bridging, and venues get hacked, depeg or die.

Data (all public, all cached gzipped under research/2026-10-10/incentive_yields/raw/):
  * DefiLlama yields: /pools (today's 16.6k live pools), /chart/{pool} (daily tvlUsd, apyBase, apyReward since a
    pool's first day), /distinctID (every pool id ever tracked, dead ones included, but no metadata);
  * survivorship: /poolsOld is paywalled (HTTP 402), so the universe is rebuilt from the Wayback Machine's captures of
    yields.llama.fi/pools (462 capture days, 2022-10-13 -> today): every pool listed at a capture keeps its metadata
    (symbol, chain, project, reward tokens), whether or not it is alive today;
  * losses: api.llama.fi/hacks joined by protocol id and date; protocol TVL from api.llama.fi/protocol/{slug};
    deposit-token prices from coins.llama.fi (depegs); reward-token prices from coins.llama.fi/chart;
  * chain launch dates: api.llama.fi/v2/historicalChainTvl/{chain} (first day with TVL).

    uv run python scripts/incentive_yields.py collect --parts wayback        # archive.org, ~2 s a capture
    uv run python scripts/incentive_yields.py collect --parts universe,charts,losses,chains,coins
    uv run python scripts/incentive_yields.py analyze
    uv run python scripts/incentive_yields.py render

Rate policy: one request at a time, at least 0.4 s apart on DefiLlama hosts (other workers share the IP and the
3 requests/second budget), 2 s on archive.org; every response is cached and a rerun only fetches what is missing.
"""
import argparse
import bisect
import datetime as dt
import gzip
import json
import math
import os
import re
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402

OUT = ROOT / 'research' / '2026-10-10' / 'incentive_yields'
RAW = OUT / 'raw'
TERM_CARRY = ROOT / 'research' / '2026-10-10' / 'term_carry'
UTC = dt.timezone.utc
UA = 'Mozilla/5.0 (llm-quant research; read-only)'
DAY_S = 86400
SSR_NOW = 0.038

YIELDS = 'https://yields.llama.fi'
LLAMA = 'https://api.llama.fi'
COINS = 'https://coins.llama.fi'
STABLES = 'https://stablecoins.llama.fi'
WAYBACK = 'http://web.archive.org'

# Non-dollar stablecoins carry DefiLlama's stablecoin flag too; the study is about dollars.
NON_USD = re.compile(r'EUR|GBP|CHF|JPY|SGD|AUD|CAD|BRZ|BRL|TRY|MXN|XAU|PAXG|CNH|IDR|ZAR|NGN|KRW|PHP|INR|GYEN|ARS|'
                     r'^PAR$|^XSGD$|^ZCHF$|^GOLD|^XAUT|^DOLA-EUR|ILS|HKD|THB|VND|RUB|SEK|NOK|DKK|PLN|COP|CLP|PEN|UAH',
                     re.I)

# Blue-chip lending venues: large, old, audited money markets whose dollar supply rate is the utilisation-priced
# rate of a public borrow book. Chosen before any return was computed (listed by DefiLlama project slug).
BLUECHIP_LENDING = {
    'aave-v2', 'aave-v3', 'compound', 'compound-v2', 'compound-v3', 'spark', 'sparklend', 'morpho-blue',
    'morpho-v1', 'morpho-aave', 'morpho-aavev3', 'morpho-compound', 'fluid-lending', 'euler-v2', 'venus-core-pool',
    'venus', 'benqi-lending', 'radiant-v2', 'moonwell', 'moonwell-lending', 'kamino-lend', 'justlend', 'silo-v2',
    'notional-v3', 'maker-dsr', 'sky-lending', 'aave-v3-lido', 'aave-v3-etherfi',
}
# Lending markets whose supply rate falls roughly with utilisation squared when supply is added (borrow rate linear in
# utilisation below the kink, supply rate = borrow rate x utilisation): a deposit X into supply T scales the base rate
# by (T/(T+X))^2. Vaults and everything else: by T/(T+X).
LENDING_PROJECTS = BLUECHIP_LENDING | {
    'radiant', 'radiant-v1', 'geist-finance', 'granary-finance', 'iron-bank', 'cream-finance', 'euler', 'tectonic',
    'sonne-finance', 'hundred-finance', 'agave', 'uwu-lend', 'valas-finance', 'benqi', 'qidao', 'abracadabra',
    'zerolend', 'seamless-protocol', 'exactly', 'dforce', 'lodestar-v1', 'lodestar-v0', 'hana-finance', 'klap',
    'kinza-finance', 'lendle', 'avalon-finance', 'layerbank', 'mendi-finance', 'ionic-protocol', 'aurelius',
    'init-capital', 'dolomite', 'silo-v1', 'solend', 'marginfi', 'marginfi-lending', 'save', 'drift-staked-sol',
    'mars-lend', 'scallop-lend', 'navi-lending', 'suilend', 'echelon-market', 'aries-markets', 'tender-finance',
    'channels-finance', 'wepiggy', 'strike', 'flux-finance', 'liqee', 'moola-market', 'aave-v1', 'colend-protocol',
    'yei-finance', 'hyperlend', 'hypurrfi', 'felix-vanilla', 'euler-v1', 'neverland', 'mendi', 'zoth', 'term-finance',
}

COINS_CHAIN = {  # DefiLlama yields chain name -> coins.llama.fi chain key, where they differ from name.lower()
    'Avalanche': 'avax', 'BSC': 'bsc', 'Binance': 'bsc', 'Gnosis': 'xdai', 'xDai': 'xdai', 'zkSync Era': 'era',
    'ZKsync Era': 'era', 'Polygon zkEVM': 'polygon_zkevm', 'Hyperliquid L1': 'hyperliquid', 'OP Mainnet': 'optimism',
    'Arbitrum Nova': 'arbitrum_nova', 'Kaia': 'klaytn', 'Klaytn': 'klaytn', 'Rootstock': 'rsk', 'RSK': 'rsk',
    'Cronos zkEVM': 'cronos_zkevm', 'X Layer': 'xlayer', 'Plume Mainnet': 'plume_mainnet', 'Ethereum': 'ethereum',
    'Immutable zkEVM': 'imx', 'Mantle': 'mantle', 'Sei': 'sei', 'Flow': 'flow', 'Core': 'core', 'Meter': 'meter',
    'Fuse': 'fuse', 'Metis': 'metis', 'Moonbeam': 'moonbeam', 'Moonriver': 'moonriver', 'Celo': 'celo',
    'Harmony': 'harmony', 'Fantom': 'fantom', 'Aurora': 'aurora', 'Boba': 'boba', 'Kava': 'kava', 'Canto': 'canto',
    'Manta': 'manta', 'Mode': 'mode', 'Blast': 'blast', 'Linea': 'linea', 'Scroll': 'scroll', 'Base': 'base',
    'Taiko': 'taiko', 'Sonic': 'sonic', 'Berachain': 'berachain', 'Unichain': 'unichain', 'Ink': 'ink',
    'Soneium': 'soneium', 'Abstract': 'abstract', 'Katana': 'katana', 'Plasma': 'plasma', 'Monad': 'monad',
    'Hemi': 'hemi', 'Lisk': 'lisk', 'Fraxtal': 'fraxtal', 'Bob': 'bob', 'BOB': 'bob', 'Zircuit': 'zircuit',
    'World Chain': 'wc', 'Corn': 'corn', 'Flare': 'flare', 'Gravity': 'gravity', 'TAC': 'tac', 'Stable': 'stable',
    'MegaETH': 'megaeth', 'Etherlink': 'etherlink', 'Swellchain': 'swellchain', 'Apechain': 'apechain',
    'ApeChain': 'apechain', 'Rari': 'rari', 'Morph': 'morph', 'Arbitrum': 'arbitrum', 'Optimism': 'optimism',
    'Polygon': 'polygon', 'Solana': 'solana', 'Tron': 'tron', 'Sui': 'sui', 'Aptos': 'aptos', 'Near': 'near',
    'Starknet': 'starknet', 'Cronos': 'cronos', 'Telos': 'telos', 'Evmos': 'evmos', 'Oasis': 'oasis',
    'Astar': 'astar', 'Velas': 'velas', 'Milkomeda C1': 'milkomeda', 'Dogechain': 'dogechain', 'Heco': 'heco',
    'OKExChain': 'okexchain', 'Conflux': 'conflux', 'Shibarium': 'shibarium', 'opBNB': 'op_bnb', 'zkLink': 'zklink',
    'Merlin': 'merlin', 'Bitlayer': 'btr', 'BSquared': 'bsquared', 'Mantle Network': 'mantle', 'Hyperliquid': 'hyperliquid',
}
# DefiLlama yields project slug -> DefiLlama protocol slug where they differ (read from api.llama.fi/protocols on
# 2026-10-10: the yields server keeps older slugs after protocols are split into versions).
PROJECT_ALIAS = {
    'pendle': 'pendle-v2', 'morpho-v1': 'morpho-blue', 'euler': 'euler-v1', 'notional': 'notional-v2',
    'stake-dao': 'stake-dao-yield', 'stakedao': 'stake-dao-yield', 'sturdy': 'sturdy-v1', 'justlend': 'justlend-v1',
    'morpho-v0-compoundv2': 'morpho-optimizer-compoundv2', 'morpho-compound': 'morpho-optimizer-compoundv2',
    'morpho-v0-aavev2': 'morpho-optimizer-aavev2', 'morpho-aave': 'morpho-optimizer-aavev2',
    'morpho-aavev3': 'morpho-optimizer-aavev3', 'idle-finance': 'idle', 'makerdao': 'sky-lending',
    'silo-finance': 'silo-v1', 'venus': 'venus-core-pool', 'dforce': 'dforce-lending',
    'abracadabra': 'abracadabra-spell', 'resolv': 'resolv-usr', 'tangible': 'tangible-rwa',
    'zerolend': 'zerolend-lending', 'impermax-finance': 'impermax-v2', 'moonwell-artemis': 'moonwell-lending',
    'allbridge': 'allbridge-classic', 'mare-finance': 'mare-finance-v1', 'benddao-lending': 'benddao-lending-v1',
    'extra-finance': 'extra-finance-xlend', 'woofi': 'woofi-earn', 'balancer': 'balancer-v2',
    'solv-funds': 'solv-basis-trading', 'lisusd': 'lista-cdp', 'ipor': 'ipor-derivatives',
}


def proto_slug(project):
    return PROJECT_ALIAS.get(project, project)


CHAIN_TVL_NAME = {'Hyperliquid L1': 'Hyperliquid L1', 'BSC': 'BSC', 'Avalanche': 'Avalanche', 'Gnosis': 'Gnosis',
                  'zkSync Era': 'zkSync Era', 'OP Mainnet': 'OP Mainnet', 'Optimism': 'OP Mainnet'}


# ---------------------------------------------------------------------------------------------- small utilities

def now_iso():
    return dt.datetime.now(UTC).isoformat(timespec='seconds')


def day_of(s):
    """'2024-07-01...' or epoch seconds -> integer day number (days since 1970-01-01, UTC)."""
    if isinstance(s, (int, float)):
        return int(s // DAY_S)
    return (dt.date(int(s[0:4]), int(s[5:7]), int(s[8:10])) - dt.date(1970, 1, 1)).days


def ymd(d):
    return (dt.date(1970, 1, 1) + dt.timedelta(days=int(d))).isoformat()


def write_gz(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(obj, f, separators=(',', ':'))
    os.replace(tmp, path)


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
    return re.sub(r'[^A-Za-z0-9_.:-]+', '_', name)[:180]


# DefiLlama's stablecoin flag also admits ETH/BTC/SOL wrappers and governance tokens (USUALX, ZBU, sdBAL, MKR...):
# a dollar pool's symbol must also name a dollar token, a dollar-denominated fund share, or a known dollar wrapper.
DOLLAR = re.compile(r'USD|DAI|GHO|FRAX|DOLA|MIM|LUSD|BOLD|BUIDL|USTB|USYC|USCC|USDY|OUSG|TBILL|BENJI|USR|USN|HONEY|'
                    r'^HAY$|^MAI$|^UZD$|USP$|AID$|MBASIS|XSTABLE', re.I)


def is_usd_stable_row(r):
    """A pool DefiLlama flags as a single-exposure stablecoin pool whose symbol is a dollar token."""
    if not r.get('stablecoin') or r.get('exposure') != 'single':
        return False
    sym = str(r.get('symbol') or '')
    return bool(sym) and not NON_USD.search(sym) and bool(DOLLAR.search(sym))


class Net:
    """Sequential, paced HTTP with retries. Every host family has a minimum spacing; nothing runs in parallel."""

    def __init__(self, log=None):
        self.spacing = {'yields.llama.fi': 0.4, 'api.llama.fi': 0.4, 'coins.llama.fi': 0.4,
                        'stablecoins.llama.fi': 0.4, 'web.archive.org': 2.0, 'api.merkl.xyz': 0.5}
        self.last = {}
        self.requests = 0
        self.bytes = 0
        self.errors = []
        self.log = log or (lambda *a: None)
        self.lock = threading.Lock()

    def _wait(self, host):
        """Reserve the next start slot for this host family (thread-safe): request starts are at least `gap`
        apart however many workers are waiting, so the request rate never exceeds 1/gap."""
        gap = self.spacing.get(host, 0.5)
        key = 'llama' if host.endswith('llama.fi') else host   # DefiLlama hosts share one budget
        with self.lock:
            now = time.monotonic()
            at = max(now, self.last.get(key, 0.0) + gap)
            self.last[key] = at
        if at > now:
            time.sleep(at - now)

    def get(self, url, raw=False, timeout=90, retries=5):
        host = urllib.parse.urlsplit(url).netloc
        last = None
        for a in range(retries):
            self._wait(host)
            try:
                req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip',
                                                           'Accept': 'application/json'})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip' or body[:2] == b'\x1f\x8b':
                        body = gzip.decompress(body)
                self.requests += 1
                self.bytes += len(body)
                return body if raw else json.loads(body)
            except urllib.error.HTTPError as e:
                last = 'HTTP %s' % e.code
                if e.code in (400, 402, 403, 404):
                    self.errors.append('%s %s' % (url[:140], last))
                    return {'_http_error': e.code}
                time.sleep(min(60.0, (30.0 if e.code == 429 else 2.0) * 2 ** a))
            except Exception as e:  # noqa: BLE001 - transport errors are retried, then recorded
                last = repr(e)[:160]
                time.sleep(min(30.0, 2.0 * 2 ** a))
        self.errors.append('%s %s' % (url[:140], last))
        return {'_failed': last}


# ---------------------------------------------------------------------------------------------- collect: wayback

def wayback_pick(cdx_rows, per_month=(1, 15)):
    """From CDX rows [timestamp, status, length], pick the capture closest to each target day of each month
    (default the 1st and the 15th), without repeats. Returns sorted timestamps."""
    caps = sorted({r[0] for r in cdx_rows if r[1] == '200'})
    if not caps:
        return []
    days = [(day_of('%s-%s-%s' % (c[:4], c[4:6], c[6:8])), c) for c in caps]
    d0, d1 = days[0][0], days[-1][0]
    targets = []
    d = dt.date.fromisoformat(ymd(d0)).replace(day=1)
    end = dt.date.fromisoformat(ymd(d1))
    while d <= end:
        for k in per_month:
            targets.append(day_of(d.replace(day=k).isoformat()))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    keys = [x[0] for x in days]
    picked = set()
    for t in targets:
        i = bisect.bisect_left(keys, t)
        best = None
        for j in (i - 1, i):
            if 0 <= j < len(days) and abs(days[j][0] - t) <= 7:
                if best is None or abs(days[j][0] - t) < abs(best[0] - t):
                    best = days[j]
        if best:
            picked.add(best[1])
    return sorted(picked)


def compact_snapshot(data):
    """Keep every USD stable single-exposure row in full, and a compact row per pool for incentive-spend history."""
    rows = data['data'] if isinstance(data, dict) else data
    keep = ('chain', 'project', 'symbol', 'tvlUsd', 'apyBase', 'apyReward', 'apy', 'rewardTokens', 'pool',
            'stablecoin', 'ilRisk', 'exposure', 'poolMeta', 'underlyingTokens', 'count', 'apyMean30d', 'outlier')
    stable = [{k: r.get(k) for k in keep} for r in rows if is_usd_stable_row(r)]
    compact = [[r.get('pool'), r.get('chain'), r.get('project'), r.get('symbol'), fnum(r.get('tvlUsd'), 0.0),
                fnum(r.get('apyBase')), fnum(r.get('apyReward')), bool(r.get('stablecoin')), r.get('exposure'),
                r.get('ilRisk')] for r in rows]
    return {'n_pools': len(rows), 'stable_single_usd': stable, 'all_compact': compact,
            'all_fields': ['pool', 'chain', 'project', 'symbol', 'tvlUsd', 'apyBase', 'apyReward', 'stablecoin',
                           'exposure', 'ilRisk']}


def collect_wayback(net, log, per_month=(1, 8, 15, 22)):
    d = RAW / 'wayback'
    cdx_p = d / 'cdx.json.gz'
    if cdx_p.exists():
        cdx = read_gz(cdx_p)
    else:
        cdx = net.get(WAYBACK + '/cdx/search/cdx?url=yields.llama.fi/pools&output=json&fl=timestamp,statuscode,length'
                      '&filter=statuscode:200&collapse=timestamp:8', timeout=120)
        if isinstance(cdx, dict):
            log('wayback cdx failed %s' % cdx)
            return {'failed': cdx}
        write_gz(cdx_p, cdx)
    picks = wayback_pick(cdx[1:], per_month)
    got, failed = 0, []
    for ts in picks:
        p = d / ('%s.json.gz' % ts)
        if p.exists():
            got += 1
            continue
        body = net.get('%s/web/%sid_/https://yields.llama.fi/pools' % (WAYBACK, ts), raw=True, timeout=180)
        if isinstance(body, dict):
            failed.append([ts, str(body)])
            continue
        try:
            data = json.loads(body)
        except Exception as e:  # noqa: BLE001
            failed.append([ts, repr(e)[:80]])
            continue
        snap = compact_snapshot(data)
        snap['timestamp'] = ts
        write_gz(p, snap)
        got += 1
        log('wayback %s pools=%d stable=%d' % (ts, snap['n_pools'], len(snap['stable_single_usd'])))
    return {'captures_in_cdx': len(cdx) - 1, 'picked': len(picks), 'have': got, 'failed': failed}


def load_snapshots():
    """All snapshots (Wayback captures and today's /pools) as [(day, ts_label, snapshot)], sorted by day."""
    out = []
    for p in sorted((RAW / 'wayback').glob('2*.json.gz')):
        s = read_gz(p)
        ts = s['timestamp']
        out.append((day_of('%s-%s-%s' % (ts[:4], ts[4:6], ts[6:8])), ts, s))
    cur = RAW / 'pools_2026-10-10.json.gz'
    if cur.exists():
        s = compact_snapshot(read_gz(cur))
        s['timestamp'] = '20261010'
        out.append((day_of('2026-10-10'), '20261010', s))
    out.sort(key=lambda x: x[0])
    return out


APY_CAP_SNAP = 100.0


def fetch_priority(u):
    """Order in which charts are fetched when the API throttles: pools that could be picked first (TVL >= $1M at a
    capture, highest yield seen at such a capture first; lending venues early because the blue-chip universe ranks
    them), then pools that never showed $1M at a capture (they can only enter between captures)."""
    lend = u.get('project') in LENDING_PROJECTS
    if u['max_tvl'] >= 1e6:
        return (0, -(u.get('max_apy_1m', 0.0) + (5.0 if lend else 0.0)))
    return (1, -u['max_tvl'])


def build_universe(min_tvl=250e3):
    """Merge every snapshot's USD stable single-exposure rows into one metadata record per pool: first/last snapshot
    seen, max TVL seen, symbol/chain/project (latest), reward tokens with the snapshot days they were listed, and the
    underlying tokens. Keep pools whose TVL reached `min_tvl` at some snapshot (the decision filter, $1M, is applied
    on the daily chart; the lower bar catches pools that crossed $1M between captures)."""
    snaps = load_snapshots()
    uni = {}
    for d, ts, s in snaps:
        for r in s['stable_single_usd']:
            pid = r.get('pool')
            if not pid or not is_usd_stable_row(r):     # captures saved earlier used a looser filter
                continue
            u = uni.setdefault(pid, {'pool': pid, 'first_snap': d, 'last_snap': d, 'max_tvl': 0.0, 'n_snaps': 0,
                                     'reward_tokens': {}, 'underlying': [], 'symbols': []})
            u['last_snap'] = max(u['last_snap'], d)
            u['first_snap'] = min(u['first_snap'], d)
            u['n_snaps'] += 1
            tv = fnum(r.get('tvlUsd'), 0.0)
            u['max_tvl'] = max(u['max_tvl'], tv)
            if tv >= 1e6:
                apy = (fnum(r.get('apyBase'), 0.0) or 0.0) + (fnum(r.get('apyReward'), 0.0) or 0.0)
                u['max_apy_1m'] = max(u.get('max_apy_1m', 0.0), min(apy, APY_CAP_SNAP))
                u['snaps_1m'] = u.get('snaps_1m', 0) + 1
            for k in ('chain', 'project', 'symbol', 'poolMeta'):
                u[k] = r.get(k)
            if r.get('symbol') and r['symbol'] not in u['symbols']:
                u['symbols'].append(r['symbol'])
            for t in (r.get('rewardTokens') or []):
                if t:
                    u['reward_tokens'].setdefault(str(t), []).append(d)
            for t in (r.get('underlyingTokens') or []):
                if t and str(t) not in u['underlying']:
                    u['underlying'].append(str(t))
    keep = {k: v for k, v in uni.items() if v['max_tvl'] >= min_tvl}
    return keep, {'snapshots': len(snaps), 'first': snaps[0][1] if snaps else None,
                  'last': snaps[-1][1] if snaps else None, 'pools_any_tvl': len(uni), 'pools_kept': len(keep)}


# ---------------------------------------------------------------------------------------------- collect: charts etc.

def collect_charts(net, log, pools, limit=None):
    d = RAW / 'charts'
    d.mkdir(parents=True, exist_ok=True)
    have = {p.name[:-8] for p in d.glob('*.json.gz')}
    todo = [p for p in pools if p not in have]
    if limit:
        todo = todo[:limit]
    log('charts: %d cached, %d to fetch' % (len(have), len(todo)))
    from concurrent.futures import ThreadPoolExecutor
    state = {'done': 0, 'fails': 0}

    def one(pid):
        r = net.get('%s/chart/%s' % (YIELDS, pid))
        if isinstance(r, dict) and ('_failed' in r):
            state['fails'] += 1
            return
        write_gz(d / ('%s.json.gz' % pid), r)
        state['done'] += 1
        if state['done'] % 200 == 0:
            log('charts %d/%d (fails %d)' % (state['done'], len(todo), state['fails']))

    # three requests in flight at most; the shared pacer keeps starts >= 0.4 s apart (<= 2.5 requests a second)
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(one, todo))
    return {'cached_before': len(have), 'fetched': state['done'], 'failed': state['fails']}


def collect_losses(net, log, universe):
    out = {}
    for name, url in (('hacks', LLAMA + '/hacks'), ('protocols', LLAMA + '/protocols'),
                      ('stablecoins', STABLES + '/stablecoins?includePrices=true'),
                      ('stablecoinprices', STABLES + '/stablecoinprices')):
        p = RAW / ('%s.json.gz' % name)
        if not p.exists():
            r = net.get(url, timeout=180)
            if isinstance(r, dict) and ('_failed' in r or '_http_error' in r):
                out[name] = 'failed %s' % r
                continue
            if name == 'protocols':  # keep what the join needs; the full list is ~10 MB
                r = [{k: x.get(k) for k in ('id', 'name', 'slug', 'parentProtocol', 'category', 'chains', 'tvl',
                                            'listedAt', 'deadFrom', 'deprecated', 'rugged', 'misrepresentedTokens')}
                     for x in r]
            write_gz(p, r)
        out[name] = 'ok'
    # protocol TVL histories for every universe project (severity of a hack = loss / TVL at the time; deaths)
    protos = read_gz(RAW / 'protocols.json.gz')
    slugs = {x.get('slug') for x in protos}
    projects = sorted({proto_slug(u.get('project')) for u in universe.values() if u.get('project')})
    d = RAW / 'protocol'
    n = 0
    for pr in projects:
        if pr not in slugs:
            continue
        p = d / ('%s.json.gz' % safe(pr))
        if p.exists():
            continue
        r = net.get('%s/protocol/%s' % (LLAMA, pr), timeout=120)
        if isinstance(r, dict) and ('_failed' in r or '_http_error' in r):
            write_gz(p, {'_failed': str(r)})
            continue
        keep = {'id': r.get('id'), 'name': r.get('name'), 'slug': pr, 'parentProtocol': r.get('parentProtocol'),
                'category': r.get('category'), 'deadFrom': r.get('deadFrom'), 'hallmarks': r.get('hallmarks'),
                'tvl': [[x.get('date'), x.get('totalLiquidityUSD')] for x in (r.get('tvl') or [])],
                'chainTvls': {c: [[x.get('date'), x.get('totalLiquidityUSD')] for x in (v.get('tvl') or [])]
                              for c, v in (r.get('chainTvls') or {}).items()
                              if '-' not in c and c not in ('borrowed', 'staking', 'pool2', 'vesting')}}
        write_gz(p, keep)
        n += 1
        if n % 50 == 0:
            log('protocol tvl %d' % n)
    out['protocol_tvl_fetched'] = n
    out['projects'] = len(projects)
    out['projects_without_slug'] = sorted(pr for pr in projects if pr not in slugs)
    return out


def collect_chains(net, log, universe):
    d = RAW / 'chains'
    chains = sorted({u.get('chain') for u in universe.values() if u.get('chain')})
    n = 0
    for c in chains:
        p = d / ('%s.json.gz' % safe(c))
        if p.exists():
            continue
        r = net.get('%s/v2/historicalChainTvl/%s' % (LLAMA, urllib.parse.quote(CHAIN_TVL_NAME.get(c, c))))
        write_gz(p, r)
        n += 1
    return {'chains': len(chains), 'fetched': n}


def coin_key(chain, addr):
    a = str(addr)
    if ':' in a:
        return a
    ck = COINS_CHAIN.get(chain, (chain or '').lower().replace(' ', '_'))
    if a.startswith('0x') and len(a) == 42:
        a = a.lower()
    return '%s:%s' % (ck, a)


CHAIN_SUFFIX = {'ethereum': 'ethereum', 'arbitrum': 'arbitrum', 'base': 'base', 'optimism': 'optimism',
                'polygon': 'polygon', 'bsc': 'bsc', 'avalanche': 'avax', 'avax': 'avax', 'monad': 'monad',
                'hyperliquid': 'hyperliquid', 'hyperevm': 'hyperliquid', 'sonic': 'sonic', 'gnosis': 'xdai',
                'xdai': 'xdai', 'linea': 'linea', 'scroll': 'scroll', 'mantle': 'mantle', 'fantom': 'fantom',
                'katana': 'katana', 'plasma': 'plasma', 'unichain': 'unichain', 'berachain': 'berachain',
                'mode': 'mode', 'blast': 'blast', 'era': 'era', 'zksync': 'era', 'celo': 'celo', 'metis': 'metis',
                'fraxtal': 'fraxtal', 'swellchain': 'swellchain', 'ink': 'ink', 'flare': 'flare', 'sei': 'sei',
                'tac': 'tac', 'corn': 'corn', 'plume': 'plume_mainnet', 'kava': 'kava', 'moonbeam': 'moonbeam',
                'polygon_zkevm': 'polygon_zkevm', 'arbitrum_nova': 'arbitrum_nova', 'cronos': 'cronos'}
_ADDR = re.compile(r'0x[0-9a-fA-F]{40}')


def share_key(pool_str, chain):
    """Coin key of a pool's share/receipt token from DefiLlama's pool id string ('0xADDR-chain', 'morpho-blue-0xADDR-
    ethereum', 'euler-earn-0xADDR-avax', '0xADDR'): the first 40-hex address and the chain named after it, else the
    pool's own chain. None when the string holds no EVM address."""
    if not pool_str:
        return None
    m = _ADDR.search(pool_str)
    if not m:
        return None
    rest = pool_str[m.end():].lstrip('-').split('-')[0].lower()
    ck = CHAIN_SUFFIX.get(rest) or COINS_CHAIN.get(chain, (chain or '').lower().replace(' ', '_'))
    return '%s:%s' % (ck, m.group(0).lower())


def collect_coins(net, log, keys, start_day, end_day, span=500):
    """Daily price history of each coin key over [start_day, end_day], 500 points a request (the API's cap)."""
    d = RAW / 'coins'
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    for k in keys:
        p = d / ('%s.json.gz' % safe(k))
        if p.exists():
            continue
        pts, sym, failed = [], None, None
        s = start_day
        while s <= end_day:
            r = net.get('%s/chart/%s?start=%d&span=%d&period=1d' % (COINS, urllib.parse.quote(k, safe=':'),
                                                                      s * DAY_S, span), timeout=90)
            if isinstance(r, dict) and r.get('coins'):
                for _, v in r['coins'].items():
                    sym = v.get('symbol') or sym
                    pts += [[int(x['timestamp']), x['price']] for x in v.get('prices') or []]
            elif isinstance(r, dict) and ('_failed' in r or '_http_error' in r):
                failed = str(r)
            s += span
        write_gz(p, {'key': k, 'symbol': sym, 'prices': sorted(pts), 'failed': failed})
        n += 1
        if n % 50 == 0:
            log('coins %d/%d' % (n, len(keys)))
    return {'keys': len(keys), 'fetched': n}


def collect_merkl(net, log):
    """Live Merkl campaigns on dollar stablecoins (a present-day view; Merkl's history is not reconstructed)."""
    d = RAW / 'merkl'
    out = []
    for page in range(0, 40):
        r = net.get('https://api.merkl.xyz/v4/opportunities?items=100&page=%d&status=LIVE' % page, timeout=60)
        if not isinstance(r, list) or not r:
            break
        out += r
        if len(r) < 100:
            break
    write_gz(d / 'opportunities_live.json.gz', out)
    return {'opportunities': len(out)}


def main_collect(args):
    RAW.mkdir(parents=True, exist_ok=True)
    logf = open(RAW / 'collect.log', 'a')

    def log(msg):
        line = '%s %s' % (now_iso(), msg)
        print(line, flush=True)
        logf.write(line + '\n')
        logf.flush()

    net = Net(log)
    for h in ('yields.llama.fi', 'api.llama.fi', 'coins.llama.fi', 'stablecoins.llama.fi'):
        net.spacing[h] = args.spacing
    parts = args.parts.split(',')
    man_p = RAW / 'manifest_collect.json'
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    t0 = time.time()
    if 'pools' in parts or not (RAW / 'pools_2026-10-10.json.gz').exists():
        r = net.get(YIELDS + '/pools', timeout=180)
        write_gz(RAW / 'pools_2026-10-10.json.gz', r)
    if 'wayback' in parts:
        man['wayback'] = collect_wayback(net, log)
    universe = None
    if any(p in parts for p in ('universe', 'charts', 'losses', 'chains', 'coins')):
        universe, info = build_universe()
        write_gz(RAW / 'universe.json.gz', universe)
        man['universe'] = info
        log('universe %s' % info)
    if 'charts' in parts:
        order = sorted(universe, key=lambda k: fetch_priority(universe[k]))
        first_p = RAW / 'fetch_first.json'
        if first_p.exists():                      # pools seen in a top-20 at some capture go first
            first = [p for p in json.loads(first_p.read_text()) if p in universe]
            order = first + [p for p in order if p not in set(first)]
        man['charts'] = collect_charts(net, log, order, args.limit)
    if 'losses' in parts:
        man['losses'] = collect_losses(net, log, universe)
    if 'chains' in parts:
        man['chains'] = collect_chains(net, log, universe)
    if 'coins' in parts:
        keys = coin_keys_needed(universe)
        man['coins'] = collect_coins(net, log, keys, day_of('2022-06-01'), day_of('2026-10-10'))
    if 'shares' in parts:
        if universe is None:
            universe = read_gz(RAW / 'universe.json.gz')
        ids = {x['config_id']: x['pool'] for x in read_gz(RAW / 'distinctID.json.gz')}
        held = json.loads((RAW / 'held_pools.json').read_text())
        if (RAW / 'fetch_first.json').exists():
            held = sorted(set(held) | set(json.loads((RAW / 'fetch_first.json').read_text())))
        keys = sorted({k for k in (share_key(ids.get(p), universe.get(p, {}).get('chain')) for p in held) if k})
        man['shares'] = collect_coins(net, log, keys, day_of('2022-09-01'), day_of('2026-10-10'))
    if 'merkl' in parts:
        man['merkl'] = collect_merkl(net, log)
    if 'lp' in parts:
        man['lp'] = collect_lp(net, log, args.limit)
    if 'verify' in parts:
        man['verify'] = collect_verify(log)
    if 'survivorship' in parts:
        man['survivorship_sample'] = collect_survivorship_sample(net, log)
    man['last_run'] = {'parts': parts, 'at': now_iso(), 'seconds': round(time.time() - t0, 1),
                       'requests': net.requests, 'bytes': net.bytes, 'errors': net.errors[:50],
                       'n_errors': len(net.errors)}
    write_json(man_p, man)
    log('done %s' % json.dumps(man['last_run'])[:400])


# ---------------------------------------------------------------------------------------------- core math (tested)

WEEK = 7
PPY_WEEK = 365.0 / 7.0
APY_CAP = 100.0          # a stablecoin pool reporting more than 100% a year on a day is a data error or a trap
FRESH_DAYS = 3           # a pool must have a record within 3 days of the decision to be ranked or held
DEPEG_BAND = 0.01        # depegs are marked when the deposit token is >1% below its entry price at exit
ENTRY_MIN_PX = 0.985     # no entry into (and exit from) a plain stable priced below this at the decision
FREEZE_DAYS = 30         # a hacked venue's withdrawals are treated as frozen for 30 days (no yield, no exit)
FREEZE_MIN_SEVERITY = 0.05   # ...when the hack took >= 5% of the venue; smaller ones are booked at once, no freeze
CLAIM_EVERY = 7          # rewards are claimed weekly (and at exit) and sold one day later
SALE_LAG = 1
REWARD_SALE_COST = 0.01  # swap fee and impact when selling a reward token


def dilution(T, X):
    """Share of a pool's per-dollar yield that a deposit X into a pool of TVL T keeps: T/(T+X) (fixed reward
    budget spread over more dollars; the base rate re-priced the same way, as the spec allows when a market's rate
    model is unknown). T is DefiLlama's tvlUsd, which for lending markets is supply net of borrows, so this
    overstates dilution there (conservative)."""
    if X <= 0:
        return 1.0
    if not T or T <= 0:
        return 0.0
    return T / (T + X)


def capacity_deposit(y, T, m):
    """Deposit X at which the marginal yield of a pool paying y (a fraction a year, before the deposit) on TVL T
    falls to m. Income I(X) = X y T/(T+X), so dI/dX = y T^2/(T+X)^2 = m gives X = T (sqrt(y/m) - 1); 0 if y <= m."""
    if y is None or T is None or T <= 0 or m <= 0 or y <= m:
        return 0.0
    return T * (math.sqrt(y / m) - 1.0)


def claim_sale_day(d, entry, exit_day, every=CLAIM_EVERY, lag=SALE_LAG):
    """Day on which a reward accrued on day d (entry <= d < exit_day) is sold: claimed at the end of the claim week
    that contains d (weeks counted from entry) or at exit, whichever is first, then sold `lag` days later."""
    k = (d - entry) // every + 1
    claim = min(exit_day, entry + k * every)
    return claim + lag


def price_at(series_days, series_px, day, max_back=5):
    """Last price at or before `day`, no older than `max_back` days; None otherwise. Inputs are parallel sorted
    lists. Never looks forward."""
    i = bisect.bisect_right(series_days, day) - 1
    if i < 0 or day - series_days[i] > max_back:
        return None
    return series_px[i]


SALE_RATIO_CAP = 3.0


def robust_price(days, px, d, back=2):
    """Median of the prices on days d-back..d (backward only): one bad print (DefiLlama's iUSD series has a day at
    8e-7) cannot set a valuation. Falls back to the last price within 5 days."""
    v = [x for x in (price_at(days, px, d - i, 0) for i in range(back + 1)) if x]
    if not v:
        x = price_at(days, px, d, 5)
        return x
    return statistics.median(v)


def sale_ratio(prices, accrual_day, sale_day):
    """Mean over reward tokens of P(sale_day)/P(accrual_day) with robust (3-day backward median) prices, each
    ratio capped at SALE_RATIO_CAP; `prices` is a list of (days, px) per token. Returns (ratio, n_tokens_priced);
    ratio None when no token has both prices."""
    rs = []
    for days, px in prices:
        a = robust_price(days, px, accrual_day)
        b = robust_price(days, px, sale_day)
        if a and b and a > 0:
            rs.append(min(SALE_RATIO_CAP, b / a))
    if not rs:
        return None, 0
    return sum(rs) / len(rs), len(rs)


def depeg_loss(p_entry, p_exit, band=DEPEG_BAND):
    """Mark-to-market loss of a deposit token between entry and exit, as a (negative) fraction; moves within the
    band are price noise and count as zero (otherwise min(0, noise) would bias every hold down)."""
    if not p_entry or not p_exit or p_entry <= 0:
        return 0.0
    r = p_exit / p_entry - 1.0
    return r if r < -band else 0.0


def hack_severity(net_loss, tvl_before):
    """Fraction of a venue's deposits lost in a hack: net stolen (after returned funds) over the venue's TVL the day
    before, capped at 1. Unknown TVL -> 1 (a hack with no denominator is marked as a total loss)."""
    if net_loss is None or net_loss <= 0:
        return 0.0
    if not tvl_before or tvl_before <= 0:
        return 1.0
    return min(1.0, net_loss / tvl_before)


MAJORS = {'USDC', 'USDT', 'DAI', 'USDS', 'USDC.E', 'USDT0', 'USDBC', 'BUSD', 'USDT.E', 'DAI.E', 'USDCE', 'USD₮0',
          'USD₮', 'AXLUSDC', 'SDAI', 'SUSDS'}
GAS_ETH = ((day_of('2024-01-01'), 20.0), (day_of('2025-01-01'), 10.0), (10 ** 9, 3.0))  # $/tx by era (until day)
GAS_OTHER = 0.5


def gas_per_tx(chain, day):
    if chain != 'Ethereum':
        return GAS_OTHER
    for until, usd in GAS_ETH:
        if day < until:
            return usd
    return GAS_ETH[-1][1]


def swap_bp(sym_from, sym_to, X):
    """Cost (bp) of swapping one dollar stablecoin for another at size X: majors 2/3/5bp at $100k/$1M/$10M, anything
    else 10/20/50bp (exotic stables trade in thin pools)."""
    if (sym_from or '').upper() == (sym_to or '').upper():
        return 0.0
    major = (sym_from or '').upper() in MAJORS and (sym_to or '').upper() in MAJORS
    tiers = (2.0, 3.0, 5.0) if major else (10.0, 20.0, 50.0)
    return tiers[0] if X <= 2e5 else tiers[1] if X <= 2e6 else tiers[2]


def switch_cost(X, from_chain, to_chain, from_sym, to_sym, day):
    """Dollar cost of moving X from one pool to another: withdraw (1 tx) on the old chain, approve + deposit (2 tx)
    on the new one, a bridge when the chain changes ($10 + 5bp, 8bp above $2M), and a stable-to-stable swap when the
    deposit token changes. From cash (None chain) the money starts as a savings token on Ethereum."""
    fc = from_chain or 'Ethereum'
    fs = from_sym or 'USDS'
    c = gas_per_tx(fc, day) + 2 * gas_per_tx(to_chain, day)
    if fc != to_chain:
        c += 10.0 + X * (8.0 if X > 2e6 else 5.0) / 1e4
    c += X * swap_bp(fs, to_sym, X) / 1e4
    return c


def exit_to_cash_cost(X, from_chain, from_sym, day):
    """Withdrawing to the savings token on Ethereum (used when nothing qualifies or a slice is released)."""
    return switch_cost(X, from_chain, 'Ethereum', from_sym, 'USDS', day) - 2 * gas_per_tx('Ethereum', day) + \
        gas_per_tx('Ethereum', day)


def rank_pools(cands, top):
    """cands: list of (score, tvl, pid). Highest score first, ties by TVL then id (deterministic)."""
    return [c[2] for c in sorted(cands, key=lambda c: (-c[0], -c[1], c[2]))[:top]]


class Pool:
    """A pool's daily chart as dense arrays from its first to its last record. Gaps of up to FRESH_DAYS are forward
    filled; longer gaps are 'dark' days (no data, no yield, not rankable). Prefix sums over real records give
    trailing means in O(1) and only ever over days strictly before the decision day."""
    __slots__ = ('pid', 'meta', 'first', 'last', 'tvl', 'base', 'rew', 'valid', 'cb', 'cr', 'cn', 'bad')

    def __init__(self, pid, meta, rows):
        self.pid = pid
        self.meta = meta
        recs = {}
        bad = 0
        for r in rows:
            d = day_of(r['timestamp']) if isinstance(r.get('timestamp'), str) else int(r['timestamp'])
            tvl = fnum(r.get('tvlUsd'), 0.0)
            rew = fnum(r.get('apyReward'), 0.0) or 0.0
            base = fnum(r.get('apyBase'))
            if base is None:
                apy = fnum(r.get('apy'))
                base = (apy - rew) if apy is not None else 0.0
            if base > APY_CAP or rew > APY_CAP or base < -100.0 or rew < 0:
                bad += 1
                continue
            recs[d] = (tvl, base, rew)
        self.bad = bad
        if not recs:
            self.first = self.last = None
            return
        days = sorted(recs)
        self.first, self.last = days[0], days[-1]
        n = self.last - self.first + 1
        self.tvl = [0.0] * n
        self.base = [0.0] * n
        self.rew = [0.0] * n
        self.valid = [False] * n
        self.cb = [0.0] * (n + 1)
        self.cr = [0.0] * (n + 1)
        self.cn = [0] * (n + 1)
        last_real = None
        for i in range(n):
            d = self.first + i
            r = recs.get(d)
            if r is not None:
                last_real = i
                self.tvl[i], self.base[i], self.rew[i] = r
                self.valid[i] = True
            elif last_real is not None and i - last_real <= FRESH_DAYS:
                self.tvl[i], self.base[i], self.rew[i] = self.tvl[last_real], self.base[last_real], self.rew[last_real]
                self.valid[i] = True
            self.cb[i + 1] = self.cb[i] + (r[1] if r else 0.0)
            self.cr[i + 1] = self.cr[i] + (r[2] if r else 0.0)
            self.cn[i + 1] = self.cn[i] + (1 if r else 0)

    def at(self, d):
        """(tvl, base, reward) on day d, or None (outside the chart or dark)."""
        if self.first is None or d < self.first or d > self.last:
            return None
        i = d - self.first
        if not self.valid[i]:
            return None
        return self.tvl[i], self.base[i], self.rew[i]

    def trailing(self, D, k, min_frac=0.5):
        """Mean apyBase and apyReward (percent) over real records on days [D-k, D-1]; None if too few records or the
        latest record is older than FRESH_DAYS before D. Uses nothing on or after D."""
        if self.first is None or D - 1 < self.first:
            return None
        hi = min(D - 1, self.last) - self.first + 1     # prefix index (exclusive) of day D-1
        lo = max(D - k, self.first) - self.first
        if hi <= lo:
            return None
        n = self.cn[hi] - self.cn[lo]
        if n < max(1, int(math.ceil(min_frac * k))):
            return None
        last_i = hi - 1
        while last_i >= lo and not (self.cn[last_i + 1] - self.cn[last_i]):
            last_i -= 1
        if last_i < lo or (D - 1) - (self.first + last_i) > FRESH_DAYS:
            return None
        return (self.cb[hi] - self.cb[lo]) / n, (self.cr[hi] - self.cr[lo]) / n

    def tvl_before(self, D):
        """TVL on the last valid day before D (within FRESH_DAYS)."""
        for d in range(D - 1, D - 2 - FRESH_DAYS, -1):
            r = self.at(d)
            if r is not None:
                return r[0]
        return None


def coin_keys_needed(universe):
    """Coin keys to price: the deposit token of every pool that any strategy variant held (written by analyze pass 1
    to raw/held_pools.json; every single-token pool if absent), then every reward token any universe pool listed."""
    held_p = RAW / 'held_pools.json'
    held = set(json.loads(held_p.read_text())) if held_p.exists() else set(universe)
    dep, rew = set(), set()
    for pid, u in universe.items():
        if pid in held and len(u.get('underlying') or []) == 1:
            dep.add(coin_key(u.get('chain'), u['underlying'][0]))
        for t in u.get('reward_tokens') or {}:
            rew.add(coin_key(u.get('chain'), t))
    return sorted(dep) + sorted(rew - dep)


# ---------------------------------------------------------------------------------------------- analysis: context

SPLIT = '2024-07-01'          # choose on decisions before, test once after (justified in the note)
START = '2022-10-17'          # first Monday after the first Wayback capture (2022-10-13): the universe is survivorship-
                              # free only from here
YEAR_BENCH = {2021: 0.0, 2022: 0.001, 2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}

CHAIN_ALIASES = {'binance smart chain': 'bsc', 'bnb chain': 'bsc', 'bnb': 'bsc', 'binance': 'bsc',
                 'gnosis chain': 'gnosis', 'xdai': 'gnosis', 'avalanche c-chain': 'avalanche', 'avax': 'avalanche',
                 'op mainnet': 'optimism', 'zksync': 'zksync era', 'era': 'zksync era', 'polygon pos': 'polygon',
                 'arbitrum one': 'arbitrum', 'hyperliquid l1': 'hyperliquid', 'hyperevm': 'hyperliquid',
                 'ethereum mainnet': 'ethereum', 'klaytn': 'kaia'}


def norm_chain(c):
    x = (c or '').strip().lower()
    return CHAIN_ALIASES.get(x, x)


def norm_name(x):
    return re.sub(r'[^a-z0-9]+', '', (x or '').lower())


def series_lookup(pairs, scale=1.0):
    """[[epoch_s or day, value], ...] -> (sorted days, values)."""
    m = {}
    for t, v in pairs or []:
        v = fnum(v)
        if v is None or t is None:
            continue
        d = int(t) // DAY_S if int(t) > 10 ** 6 else int(t)
        m[d] = v * scale
    days = sorted(m)
    return days, [m[d] for d in days]


def capture_series():
    """pool id -> [(day, tvlUsd, apyBase, apyReward)] from every capture (dollar single-exposure rows)."""
    out = {}
    for d, ts, s_ in load_snapshots():
        for r in s_['stable_single_usd']:
            if r.get('pool'):
                out.setdefault(r['pool'], []).append((d, fnum(r.get('tvlUsd'), 0.0), fnum(r.get('apyBase')),
                                                      fnum(r.get('apyReward'), 0.0)))
    for v in out.values():
        v.sort()
    return out


def densify_captures(caps, max_carry=10, tail=7):
    """Daily rows from captures: each capture's values carried forward to the next capture (at most max_carry
    days; `tail` days after the last one). Values are used only from the capture's own day on: no look-ahead."""
    rows = []
    for i, (d, tvl, base, rew) in enumerate(caps):
        nxt = caps[i + 1][0] if i + 1 < len(caps) else d + tail
        for x in range(d, min(nxt, d + max_carry)):
            rows.append({'timestamp': x, 'tvlUsd': tvl, 'apyBase': base, 'apyReward': rew})
    return rows


class Ctx:
    """Everything the backtest reads, loaded once from raw/."""

    def __init__(self, universe, log=print):
        self.log = log
        self.universe = universe
        self.meta = {}
        self.pools = {}
        self.synthetic = set()
        bad = 0
        cap_rows = None
        for pid, u in universe.items():
            f = RAW / 'charts' / ('%s.json.gz' % pid)
            if not f.exists():
                continue
            try:
                rows = read_gz(f).get('data') or []
            except Exception:  # noqa: BLE001
                continue
            if not rows:
                # DefiLlama deleted this pool's records (107 of the 110 are old Morpho vault ids): rebuild a daily
                # series from the Wayback captures, each capture's values used from its own day forward
                if cap_rows is None:
                    cap_rows = capture_series()
                rows = densify_captures(cap_rows.get(pid) or [])
                if not rows:
                    continue
                self.synthetic.add(pid)
            P = Pool(pid, u, rows)
            bad += P.bad
            if P.first is None:
                continue
            self.pools[pid] = P
            self.meta[pid] = {'chain': u.get('chain'), 'project': u.get('project'), 'symbol': u.get('symbol'),
                              'poolMeta': u.get('poolMeta')}
        self.bad_records = bad
        self.savings = self._savings()
        self._protocols()
        self._hacks()
        self._prices()
        self._shares()
        self._chains()
        self._elig_cache = {}

    # -- benchmark
    def _savings(self):
        try:
            import term_carry as TC
            path = TC.load_navs(TERM_CARRY)['savings_path']
            self.savings_source = 'term_carry.load_navs: Pot.dsr weekly reads (raw/chain/samples.json), sUSDS NAV daily'
            return dict(path)
        except Exception as e:  # noqa: BLE001 - fall back to the yearly table the brief gives
            self.savings_source = 'yearly table (term_carry load failed: %s)' % repr(e)[:80]
            return {}

    def sav(self, d):
        v = self.savings.get(d)
        if v is None:
            v = YEAR_BENCH.get(int(ymd(d)[:4]), SSR_NOW)
        return v

    # -- protocols: category, TVL history, age
    def _protocols(self):
        self.proto = {}
        self.proto_by_id = {}
        p = RAW / 'protocols.json.gz'
        if p.exists():
            for x in read_gz(p):
                if x.get('slug'):
                    self.proto[x['slug']] = x
                    self.proto_by_id[str(x.get('id'))] = x
        self.proto_tvl = {}
        self.proto_chain_tvl = {}
        for slug in {proto_slug(m['project']) for m in self.meta.values()}:
            f = RAW / 'protocol' / ('%s.json.gz' % safe(slug or ''))
            if not f.exists():
                continue
            r = read_gz(f)
            if r.get('_failed'):
                continue
            self.proto_tvl[slug] = series_lookup(r.get('tvl'))
            self.proto_chain_tvl[slug] = {norm_chain(c): series_lookup(v) for c, v in (r.get('chainTvls') or {}).items()}
            if slug in self.proto:
                self.proto[slug]['_category_hist'] = r.get('category')

    def category(self, project):
        x = self.proto.get(proto_slug(project)) or {}
        return x.get('category') or x.get('_category_hist') or 'unknown'

    def proto_tvl_at(self, project, d, chain=None):
        project = proto_slug(project)
        if chain is not None:
            ser = (self.proto_chain_tvl.get(project) or {}).get(norm_chain(chain))
        else:
            ser = self.proto_tvl.get(project)
        if not ser or not ser[0]:
            return None
        return price_at(ser[0], ser[1], d, max_back=10)

    def proto_first_day(self, project):
        ser = self.proto_tvl.get(proto_slug(project))
        if not ser or not ser[0]:
            return None
        for d, v in zip(*ser):
            if v and v > 0:
                return d
        return None

    def is_bluechip(self, project, D):
        """Decided with data before D only: a lending protocol (DefiLlama category) with TVL >= $1B the day before
        and at least a year of TVL history."""
        if self.category(project) != 'Lending':
            return False
        f = self.proto_first_day(project)
        if f is None or D - f < 365:
            return False
        t = self.proto_tvl_at(project, D - 1)
        return bool(t and t >= 1e9)

    # -- hacks, joined by protocol id (exact) or by normalised name when the hack has no id
    def _hacks(self):
        self.hacks = {}
        self.hack_join = {'matched': [], 'unmatched_large': []}
        p = RAW / 'hacks.json.gz'
        if not p.exists():
            return
        hacks = read_gz(p)
        projects = {m['project'] for m in self.meta.values()}
        id2proj = {}
        name2proj = {}
        for pr in projects:                       # several yields projects can share one protocol (aliases)
            x = self.proto.get(proto_slug(pr))
            if x:
                id2proj.setdefault(str(x.get('id')), []).append(pr)
                name2proj.setdefault(norm_name(x.get('name')), []).append(pr)
        for h in hacks:
            d = int(h.get('date') or 0) // DAY_S
            if d < day_of('2022-06-01'):
                continue
            projs = id2proj.get(str(h.get('defillamaId'))) if h.get('defillamaId') else None
            if projs is None and not h.get('defillamaId'):
                projs = name2proj.get(norm_name(h.get('name')))
            for slug in (projs or [None]):
                self._add_hack(h, d, slug)

    def _add_hack(self, h, d, slug):
        """One hack against one yields project (slug None: unmatched, kept for the report if >= $10M)."""
        gross = fnum(h.get('amount'), 0.0) or 0.0
        ret = fnum(h.get('returnedFunds'), 0.0) or 0.0
        net = max(0.0, gross - ret)
        chains = [norm_chain(c) for c in (h.get('chain') or [])]
        if slug is None:
            if gross >= 1e7:
                self.hack_join['unmatched_large'].append([ymd(d), h.get('name'), gross, h.get('chain')])
            return
        ev = {'day': d, 'name': h.get('name'), 'gross': gross, 'returned': ret, 'net': net, 'chains': chains,
              'classification': h.get('classification'), 'technique': h.get('technique')}
        # severity on the chain hit when there is one chain and a chain TVL; else on the protocol TVL
        if len(chains) == 1:
            tv = self.proto_tvl_at(slug, d - 1, chains[0]) or self.proto_tvl_at(slug, d - 1)
        else:
            tv = self.proto_tvl_at(slug, d - 1)
        ev['tvl_before'] = tv
        ev['severity'] = hack_severity(net, tv)
        ev['gross_severity'] = hack_severity(gross, tv)
        self.hacks.setdefault(slug, []).append(ev)
        self.hack_join['matched'].append([ymd(d), h.get('name'), slug, gross, ret, round(ev['severity'], 4)])

    def hack_on(self, project, chain, d):
        for ev in self.hacks.get(project) or ():
            if ev['day'] == d and (not ev['chains'] or norm_chain(chain) in ev['chains']):
                return ev
        return None

    def recent_hack(self, project, chain, D, window=30):
        for ev in self.hacks.get(project) or ():
            if D - window <= ev['day'] < D and (not ev['chains'] or norm_chain(chain) in ev['chains']):
                return True
        return False

    # -- prices: reward tokens (sale valuation) and deposit tokens (depegs)
    def _prices(self):
        self.coin = {}
        d = RAW / 'coins'
        if d.exists():
            for f in d.glob('*.json.gz'):
                try:
                    r = read_gz(f)
                except Exception:  # noqa: BLE001
                    continue
                if r.get('prices'):
                    self.coin[r['key']] = series_lookup(r['prices'])
        self.stable_px = {}
        sp = RAW / 'stablecoinprices.json.gz'
        sl = RAW / 'stablecoins.json.gz'
        if sp.exists() and sl.exists():
            lst = read_gz(sl)
            assets = lst.get('peggedAssets', []) if isinstance(lst, dict) else lst
            sym2gecko = {}
            for a in assets:
                if a.get('pegType') == 'peggedUSD' and a.get('gecko_id'):
                    sym2gecko.setdefault(str(a.get('symbol')).upper(), a['gecko_id'])
            by_gecko = {}
            for row in read_gz(sp):
                dd = int(row['date']) // DAY_S
                for g, v in (row.get('prices') or {}).items():
                    by_gecko.setdefault(g, []).append([dd, v])
            for sym, g in sym2gecko.items():
                if g in by_gecko:
                    self.stable_px[sym] = series_lookup(by_gecko[g])
        self.reward_px = {}
        self.dep_px = {}
        self.dep_plain = {}
        self.not_dollar = set()
        for pid in self.pools:
            u = self.universe[pid]
            ch = u.get('chain')
            toks = [coin_key(ch, t) for t in (u.get('reward_tokens') or {})]
            self.reward_px[pid] = [self.coin[k] for k in toks if k in self.coin and self.coin[k][0]]
            ser = None
            if len(u.get('underlying') or []) == 1:
                ser = self.coin.get(coin_key(ch, u['underlying'][0]))
            if not ser or not ser[0]:
                ser = self.stable_px.get(str(u.get('symbol') or '').upper())
            if ser and ser[0]:
                self.dep_px[pid] = ser
                # classified on the token's first 90 days of prices: a dollar token that collapsed later must stay in
                # the universe for the life it had (classifying on recent prices would drop xUSD-type failures)
                early = [v for d, v in zip(*ser) if d < ser[0][0] + 90]
                med = statistics.median(early)
                self.dep_plain[pid] = 0.9 <= med <= 1.1
                if not 0.85 <= med <= 1.7:          # not a dollar token (or a share priced in other units)
                    self.not_dollar.add(pid)
        # global reward-token haircut for rewards whose token has no price: the median 8-day price ratio of all
        # priced reward tokens on days before the split (in-sample only)
        # the expected value matters (rewards are summed), so the mean of the ratios, each clipped to [0.2, 5]
        ratios = []
        split = day_of(SPLIT)
        seen = set()
        for pid, lst in self.reward_px.items():
            for days, px in lst:
                if id(px) in seen:
                    continue
                seen.add(id(px))
                for i in range(0, len(days), 7):
                    if days[i] >= split:
                        break
                    b = price_at(days, px, days[i] + 8)
                    if b and px[i] > 0:
                        ratios.append(min(5.0, max(0.2, b / px[i])))
        self.impute_ratio = sum(ratios) / len(ratios) if ratios else 0.97
        self.impute_ratio_median = statistics.median(ratios) if ratios else None
        self.impute_n = len(ratios)

    def _shares(self):
        """Share-token price series (DefiLlama prices many vault and receipt tokens) for pools whose id string
        names an EVM token. 'Accruing' when the share price grows with the pool's yield (vault shares), else
        'flat' (rebasing receipts such as aTokens, priced like the underlying)."""
        self.share_px = {}
        self.share_accruing = {}
        p = RAW / 'distinctID.json.gz'
        if not p.exists():
            return
        ids = {x['config_id']: x['pool'] for x in read_gz(p)}
        self.pool_str = {pid: ids.get(pid) for pid in self.pools}
        for pid, P in self.pools.items():
            k = share_key(ids.get(pid), self.meta[pid]['chain'])
            ser = self.coin.get(k) if k else None
            if not ser or len(ser[0]) < 30:
                continue
            self.share_px[pid] = ser
            days, px = ser
            # growth over the overlap with the chart, against the chart's mean apyBase there (before any crash:
            # the first 80% of the overlap)
            lo, hi = max(days[0], P.first), min(days[-1], P.last)
            hi = lo + int(0.8 * (hi - lo))
            if hi - lo < 30:
                continue
            a, b = price_at(days, px, lo, 10), price_at(days, px, hi, 10)
            if a and b and a > 0 and b > 0:
                g = math.log(b / a) * 365.0 / (hi - lo) * 100.0
                # a rebasing receipt (aToken-like) keeps the underlying's price; a vault share grows. Whatever the
                # pool claims, growth above 1% a year marks a share whose price must deliver the claimed yield.
                self.share_accruing[pid] = g > 1.0

    def share_price(self, pid, d, back=2):
        """Median of the share prices on days d-back..d (robust to a one-day glitch; never looks forward)."""
        ser = self.share_px.get(pid)
        if not ser:
            return None
        v = [x for x in (price_at(ser[0], ser[1], d - i, 0) for i in range(back + 1)) if x]
        if not v:
            v = [price_at(ser[0], ser[1], d, 5)] if price_at(ser[0], ser[1], d, 5) else []
        return statistics.median(v) if v else None

    def principal_mark(self, pid, d_entry, d_exit, px0, spx0, base_acc, collapsed):
        """Loss (negative fraction) on the deposit between entry and exit, and its kind. With a share-price series:
        the share return short of what the pool claimed (apyBase accrual, for accruing shares; zero for rebasing
        receipts), counted beyond the 1% band; when the pool's liquidity collapsed during the hold the exit is
        marked at the price four weeks later if the share is still >5% below (a run on a 100%-utilised vault cannot
        be exited). Without one: the deposit token's depeg."""
        if pid in self.share_px and spx0:
            p1 = self.share_price(pid, d_exit)
            if p1 is None:
                return 0.0, 'share_missing'
            kind = 'share'
            if collapsed:
                later = [self.share_price(pid, d_exit + k) for k in (7, 14, 21, 28)]
                later = [x for x in later if x]
                if later and min(later) < 0.95 * p1 and later[-1] < 0.95 * p1:
                    p1, kind = later[-1], 'share_stuck'
            if self.share_accruing.get(pid):
                # a vault share must have delivered the apyBase the pool claimed: book the whole shortfall (never a
                # surplus, which could be rewards compounded into the share and also counted as apyReward)
                short = p1 / spx0 - 1.0 - base_acc
                return min(0.0, short), kind
            short = p1 / spx0 - 1.0
            return (short if short < -DEPEG_BAND else 0.0), kind
        return depeg_loss(px0, self.dep_price(pid, d_exit)), 'depeg'

    def dep_price(self, pid, d):
        ser = self.dep_px.get(pid)
        if not ser:
            return None
        return robust_price(ser[0], ser[1], d)

    # -- chain launch dates
    def _chains(self):
        self.chain_launch = {}
        d = RAW / 'chains'
        if not d.exists():
            return
        for f in d.glob('*.json.gz'):
            r = read_gz(f)
            if not isinstance(r, list):
                continue
            first = None
            for x in r:
                if (fnum(x.get('tvl'), 0) or 0) > 0:
                    first = int(x['date']) // DAY_S
                    break
            if first is not None:
                self.chain_launch[f.name[:-8]] = first

    CHAIN_ZERO_ALIAS = {'Hyperevm': 'Hyperliquid L1', 'APTOS': 'Aptos', 'Native Core': 'CORE'}

    def chain_age(self, chain, d):
        c = self.CHAIN_ZERO_ALIAS.get(chain, chain)
        f = self.chain_launch.get(safe(c or ''))
        if f is None:
            f = self.chain_launch.get(safe(chain or ''))
        return None if f is None else d - f

    # -- eligibility at a decision day (cached per (D, k, universe))
    def eligible(self, D, k, uni, alive=None):
        key = (D, k, uni, None if alive is None else id(alive))
        hit = self._elig_cache.get(key)
        if hit is not None:
            return hit
        out = []
        for pid, P in self.pools.items():
            if alive is not None and pid not in alive:
                continue
            if pid in self.not_dollar or not DOLLAR.search(str(self.meta[pid]['symbol'] or '')):
                continue
            if D - P.first < 7 or D > P.last + FRESH_DAYS + 1:
                continue
            tr = P.trailing(D, k)
            if tr is None:
                continue
            T = P.tvl_before(D)
            if not T or T < 1e6:
                continue
            m = self.meta[pid]
            if uni == 'bluechip' and not self.is_bluechip(m['project'], D):
                continue
            if uni == 'lending' and self.category(m['project']) != 'Lending':
                continue
            if self.recent_hack(m['project'], m['chain'], D):
                continue
            px = self.dep_price(pid, D - 1)
            if px is not None and self.dep_plain.get(pid) and px < ENTRY_MIN_PX:
                continue
            out.append((tr[0], tr[1], T, pid))
        self._elig_cache[key] = out
        return out


# ---------------------------------------------------------------------------------------------- analysis: engine

def score_selector(ctx, k, h, uni, alive=None):
    def sel(D):
        el = ctx.eligible(D, k, uni, alive)
        return rank_pools([(b + h * r, T, pid) for b, r, T, pid in el], len(el)), {pid for _, _, _, pid in el}
    return sel


def simulate(ctx, select, N, H, capital, start, end, delay=0, buffer=2, collapse_loss=0.0, dark_loss=0.0,
             reward_mode='sale', record=False, losses=True):
    """Weekly-decision allocator over `N` equal slices of `capital` (constant notional, additive P&L).

    Every H weeks, on decision day D, `select(D)` ranks the eligible pools using data before D only; held pools
    still eligible and ranked within the top buffer*N are kept, free slices take the best-ranked pools not held, and
    the moves execute `delay` days later. Each day a slice earns the pool's apyBase and apyReward diluted by its own
    deposit (T/(T+X)), the reward valued at the price on its sale day (weekly claim + 1 day) less a 1% sale cost
    (reward_mode 'face' values it at accrual, 'none' drops it); idle slices earn the savings rate. Losses: a matched
    hack marks the slice to zero for FREEZE_DAYS (no yield, no exit), then returns (1 - severity); the deposit token
    is marked at exit when it is >1% below its entry price; a TVL collapse (>80% in 7 days, no hack) or a pool going
    dark costs `collapse_loss` / `dark_loss` (0 in the base case, stressed separately). Costs: gas, bridges and
    stable swaps on every switch (switch_cost), and two transactions a week to claim and sell rewards.

    Returns weekly series (strategy return, savings benchmark, excess) and, with record=True, holdings and events.
    """
    X = capital / N
    slices = [{'pool': None, 'chain': None, 'sym': None, 'entry': None, 'px0': None, 'spx0': None, 'base_acc': 0.0,
               'frozen': None, 'sev': 0.0, 'collapsed': False, 'dark': False} for _ in range(N)]
    pm = getattr(ctx, 'principal_mark', None)

    def mark(sl, d):
        """Principal loss fraction at exit (share-price mark where the context has one, else the depeg mark)."""
        if not losses or sl['pool'] is None:
            return 0.0, None
        if pm is None:
            return depeg_loss(sl['px0'], ctx.dep_price(sl['pool'], d)), 'depeg'
        return pm(sl['pool'], sl['entry'], d, sl['px0'], sl.get('spx0'), sl.get('base_acc', 0.0), sl['collapsed'])
    pnl = {}
    events = []
    by_pool = {}
    hold_days = {}
    switches = 0
    pending = []

    def book(d, v):
        pnl[d] = pnl.get(d, 0.0) + v

    def bp(pid):
        return by_pool.setdefault(pid, {'base': 0.0, 'reward': 0.0, 'reward_imputed': 0.0, 'cost': 0.0,
                                        'loss': 0.0, 'days': 0, 'bench': 0.0})

    def exit_slice(sl, d, to_chain, to_sym):
        nonlocal switches
        pid = sl['pool']
        if pid is not None:
            frac, kind = mark(sl, d)
            loss = frac * X
            if loss:
                book(d, loss)
                bp(pid)['loss'] += loss
                events.append({'type': kind, 'day': ymd(d), 'pool': pid, 'loss': loss, 'entry': ymd(sl['entry'])})
        if to_chain is None:
            c = exit_to_cash_cost(X, sl['chain'], sl['sym'], d) if pid is not None else 0.0
        else:
            c = switch_cost(X, sl['chain'], to_chain, sl['sym'], to_sym, d)
            switches += 1
        book(d, -c)
        if pid is not None:
            bp(pid)['cost'] += c

    for d in range(start, end):
        # a freeze ends: the slice recovers (1 - severity) of its notional and waits in the savings token
        for sl in slices:
            if sl['frozen'] is not None and d >= sl['frozen']:
                book(d, (1.0 - sl['sev']) * X)
                c = exit_to_cash_cost(X, sl['chain'], sl['sym'], d)
                book(d, -c)
                bp(sl['pool'])['cost'] += c
                sl.update({'pool': None, 'chain': None, 'sym': None, 'entry': d, 'px0': None, 'spx0': None,
                           'base_acc': 0.0, 'frozen': None, 'sev': 0.0, 'collapsed': False, 'dark': False})
        if (d - start) % (7 * H) == 0:
            ranked, elig = select(d)
            pending.append((d + delay, ranked, elig))
        while pending and pending[0][0] == d:
            _, ranked, elig = pending.pop(0)
            rank_of = {pid: i for i, pid in enumerate(ranked)}
            held = set()
            free = []
            for sl in slices:
                if sl['frozen'] is not None:
                    held.add(sl['pool'])
                    continue
                pid = sl['pool']
                if pid is not None and pid in elig and rank_of.get(pid, 10 ** 9) < buffer * N and pid not in held:
                    held.add(pid)
                else:
                    free.append(sl)
            targets = [pid for pid in ranked if pid not in held][:len(free)]
            # slices already in a target keep it; others take the remaining targets in rank order
            stay = [sl for sl in free if sl['pool'] in targets]
            for sl in stay:
                targets.remove(sl['pool'])
                held.add(sl['pool'])
            for sl in free:
                if sl in stay:
                    continue
                new = targets.pop(0) if targets else None
                if new is None:
                    if sl['pool'] is not None:
                        exit_slice(sl, d, None, None)
                    sl.update({'pool': None, 'chain': None, 'sym': None, 'entry': d, 'px0': None, 'spx0': None,
                               'base_acc': 0.0, 'collapsed': False, 'dark': False})
                    continue
                m = ctx.meta[new]
                exit_slice(sl, d, m['chain'], m['symbol'])
                bp(new)['cost'] += 0.0
                sl.update({'pool': new, 'chain': m['chain'], 'sym': m['symbol'], 'entry': d,
                           'px0': ctx.dep_price(new, d), 'base_acc': 0.0, 'collapsed': False, 'dark': False,
                           'spx0': ctx.share_price(new, d) if hasattr(ctx, 'share_price') else None})
                held.add(new)
                if record:
                    events.append({'type': 'enter', 'day': ymd(d), 'pool': new})
        sav = ctx.sav(d) / 365.0
        for sl in slices:
            pid = sl['pool']
            if sl['frozen'] is not None and d < sl['frozen']:
                continue
            if pid is None:
                book(d, X * sav)
                continue
            P = ctx.pools[pid]
            m = ctx.meta[pid]
            st = bp(pid)
            st['days'] += 1
            st['bench'] += X * sav
            hold_days[pid] = hold_days.get(pid, 0) + 1
            ev = ctx.hack_on(m['project'], m['chain'], d) if losses else None
            if ev is not None:
                st['loss'] += -ev['severity'] * X
                events.append({'type': 'hack', 'day': ymd(d), 'pool': pid, 'project': m['project'],
                               'name': ev['name'], 'severity': ev['severity'], 'loss': -ev['severity'] * X,
                               'frozen': ev['severity'] >= FREEZE_MIN_SEVERITY})
                if ev['severity'] >= FREEZE_MIN_SEVERITY:
                    book(d, -X)                   # withdrawals frozen: marked to zero until resolved
                    sl['frozen'] = d + FREEZE_DAYS
                    sl['sev'] = ev['severity']
                    continue
                book(d, -ev['severity'] * X)      # a small exploit: the loss is booked, the deposit stays liquid
            r = P.at(d)
            if r is None:
                if not sl['dark']:
                    sl['dark'] = True
                    events.append({'type': 'dark', 'day': ymd(d), 'pool': pid, 'loss': 0.0})
                continue
            tvl, base, rew = r
            if not sl['collapsed']:
                prev = [P.at(x) for x in range(d - 7, d)]
                mx = max([q[0] for q in prev if q is not None] or [0.0])
                if mx > 0 and tvl < 0.2 * mx:
                    sl['collapsed'] = True
                    # stress only where no share price can say what happened (the share mark covers the rest)
                    stress = collapse_loss if pid not in getattr(ctx, 'share_px', {}) else 0.0
                    events.append({'type': 'collapse', 'day': ymd(d), 'pool': pid, 'tvl_from': mx, 'tvl_to': tvl,
                                   'loss': -stress * X})
                    if stress:
                        book(d, -stress * X)
                        st['loss'] += -stress * X
            f = dilution(tvl, X)
            b = X * base / 100.0 / 365.0 * f
            book(d, b)
            st['base'] += b
            sl['base_acc'] += base / 36500.0
            if rew > 0 and reward_mode != 'none':
                if reward_mode == 'face':
                    ratio, n = 1.0, 1
                else:
                    ratio, n = sale_ratio(ctx.reward_px.get(pid) or [], d, claim_sale_day(d, sl['entry'], 10 ** 9))
                    if ratio is None:
                        ratio = ctx.impute_ratio
                v = X * rew / 100.0 / 365.0 * f * ratio * (1.0 - REWARD_SALE_COST)
                gas = 2.0 * gas_per_tx(m['chain'], d) / 7.0
                book(d, v - gas)
                st['reward'] += v
                st['cost'] += gas
                if n == 0:
                    st['reward_imputed'] += v
    # mark open positions at the end (depeg) so the last week carries what an exit would realise
    for sl in slices:
        if sl['pool'] is not None and sl['frozen'] is None:
            frac, kind = mark(sl, end - 1)
            loss = frac * X
            if loss:
                book(end - 1, loss)
                bp(sl['pool'])['loss'] += loss
                events.append({'type': (kind or 'mark') + '_open', 'day': ymd(end - 1), 'pool': sl['pool'],
                               'loss': loss, 'entry': ymd(sl['entry'])})
        elif sl['frozen'] is not None:            # still frozen at the end: carry (1 - severity)
            book(end - 1, (1.0 - sl['sev']) * X)
    weeks = []
    for w0 in range(start, end - 6, 7):
        ret = sum(pnl.get(d, 0.0) for d in range(w0, w0 + 7)) / capital
        bench = sum(ctx.sav(d) for d in range(w0, w0 + 7)) / 365.0
        weeks.append((w0, ret, bench, ret - bench))
    out = {'weeks': weeks, 'switches': switches, 'capital': capital, 'N': N, 'H': H}
    if record:
        out['events'] = events
        out['by_pool'] = by_pool
        out['hold_days'] = hold_days
    else:
        out['events'] = [e for e in events if e['type'] != 'enter']
        out['by_pool'] = by_pool
    return out


def series_stats(weeks, lo=None, hi=None, lags=8):
    """perf + Newey-West t (8 weekly lags) + 8-week block bootstrap of the weekly excess over [lo, hi)."""
    xs = [w[3] for w in weeks if (lo is None or w[0] >= lo) and (hi is None or w[0] < hi)]
    rs = [w[1] for w in weeks if (lo is None or w[0] >= lo) and (hi is None or w[0] < hi)]
    if not xs:
        return {'n': 0}
    pf = B.perf(xs, PPY_WEEK)
    t, p = B.newey_west_t(xs, lags=lags)
    bb = B.block_bootstrap(xs, block=8, n=1000)
    return {'weeks': len(xs), 'ann_excess': pf['ann_return'], 'ann_return_gross': sum(rs) / len(rs) * PPY_WEEK,
            'ann_vol': pf['ann_vol'], 'sharpe_excess': pf['sharpe'], 'max_drawdown': pf['max_drawdown'],
            'worst_week': pf['worst'], 'hit_rate': pf['hit_rate'], 'nw_t': t, 'nw_p': p,
            'boot_lo': bb['lo'] * PPY_WEEK if bb['lo'] is not None else None,
            'boot_hi': bb['hi'] * PPY_WEEK if bb['hi'] is not None else None}


# ---------------------------------------------------------------------------------------------- analysis: studies

GRID = [{'universe': u, 'k': k, 'h': h, 'H': H}
        for u in ('all', 'bluechip') for k in (7, 30) for h in (0.0, 0.5, 1.0) for H in (1, 2, 4)]
N_MAIN = 5
CAP_MAIN = 1e6


def vname(v):
    return '%s k%d h%.1f H%d' % (v['universe'], v['k'], v['h'], v['H'])


def forward_window(ctx, pid, D, days=28):
    """What an eligible pool delivered over [D, D+days) at zero size: base, reward at face and at the sale price,
    and the losses (matched hack at its net severity, depeg at exit, TVL collapse, going dark)."""
    P = ctx.pools[pid]
    m = ctx.meta[pid]
    base = face = sale = 0.0
    hack = None
    dark = collapse = False
    for d in range(D, D + days):
        ev = ctx.hack_on(m['project'], m['chain'], d)
        if ev is not None:
            hack = ev
            break
        r = P.at(d)
        if r is None:
            dark = True
            continue
        tvl, b, rw = r
        base += b / 36500.0
        if rw > 0:
            face += rw / 36500.0
            ratio, _ = sale_ratio(ctx.reward_px.get(pid) or [], d, claim_sale_day(d, D, 10 ** 9))
            sale += rw / 36500.0 * (ctx.impute_ratio if ratio is None else ratio) * (1.0 - REWARD_SALE_COST)
        if not collapse:
            prev = [P.at(x) for x in range(d - 7, d)]
            mx = max([q[0] for q in prev if q is not None] or [0.0])
            collapse = mx > 0 and tvl < 0.2 * mx
    if hack is None:
        dep, kind = ctx.principal_mark(pid, D, D + days, ctx.dep_price(pid, D), ctx.share_price(pid, D), base,
                                       collapse)
    else:
        dep, kind = 0.0, None
    hl = -hack['severity'] if hack else 0.0
    bench = sum(ctx.sav(d) for d in range(D, D + days)) / 365.0
    return {'base': base, 'face': face, 'sale': sale, 'hack': hl, 'depeg': dep, 'collapse': collapse, 'dark': dark,
            'bench': bench, 'net': base + sale + hl + dep}


def bucket_excess(x):
    for lo, hi, name in ((-1e9, 0, '< SSR'), (0, 2, '0-2pp'), (2, 5, '2-5pp'), (5, 10, '5-10pp'), (10, 20, '10-20pp'),
                         (20, 1e9, '>= 20pp')):
        if lo <= x < hi:
            return name
    return '?'


def age_bucket(days):
    if days is None:
        return None
    mo = days / 30.4
    for lo, hi, name in ((0, 1, 'm0-1'), (1, 2, 'm1-2'), (2, 3, 'm2-3'), (3, 6, 'm3-6'), (6, 12, 'm6-12'),
                         (12, 24, 'm12-24'), (24, 1e9, 'm24+')):
        if lo <= mo < hi:
            return name
    return None


AGE_MID = {'m0-1': 0.5, 'm1-2': 1.5, 'm2-3': 2.5, 'm3-6': 4.5, 'm6-12': 9.0, 'm12-24': 18.0, 'm24+': 30.0}


def fit_half_life(points):
    """Least-squares fit of y = A * 2^(-m/tau) over (m, y, weight) by grid search on tau (A in closed form)."""
    best = None
    for i in range(1, 400):
        tau = 0.1 * i
        g = [(2.0 ** (-m / tau), y, w) for m, y, w in points]
        den = sum(w * a * a for a, _, w in g)
        if den <= 0:
            continue
        A = sum(w * a * y for a, y, w in g) / den
        err = sum(w * (y - A * a) ** 2 for a, y, w in g)
        if best is None or err < best[0]:
            best = (err, tau, A)
    return None if best is None else {'tau_months': best[1], 'A_pp': best[2], 'sse': best[0]}


def window_study(ctx, start, end, every=28, days=28):
    """Every eligible pool (all universe, k=7) on non-overlapping 4-week windows: displayed yield at D against what
    the next four weeks delivered, by displayed-excess bucket, venue category, chain age and pool age."""
    rows = []
    for D in range(start, end - days, every):
        el = ctx.eligible(D, 7, 'all')
        sav = ctx.sav(D) * 100.0
        for b, r, T, pid in el:
            fw = forward_window(ctx, pid, D, days)
            m = ctx.meta[pid]
            rows.append({'D': D, 'pid': pid, 'disp_base': b, 'disp_rew': r, 'sav': sav, 'tvl': T,
                         'cat': ctx.category(m['project']), 'blue': ctx.is_bluechip(m['project'], D),
                         'chain': m['chain'], 'chain_age': ctx.chain_age(m['chain'], D),
                         'pool_age': D - ctx.pools[pid].first, **fw})
    return rows


def agg_rows(rows, key, days=28):
    out = {}
    f = 365.0 / days
    for r in rows:
        k = key(r)
        if k is None:
            continue
        a = out.setdefault(k, {'n': 0, 'disp': 0.0, 'base': 0.0, 'face': 0.0, 'sale': 0.0, 'hack': 0.0,
                               'depeg': 0.0, 'net': 0.0, 'bench': 0.0, 'n_hack': 0, 'n_depeg': 0, 'n_collapse': 0,
                               'n_dark': 0, 'tvl': 0.0, 'pools': set()})
        a['n'] += 1
        a['disp'] += (r['disp_base'] + r['disp_rew']) / 100.0
        for x in ('base', 'face', 'sale', 'hack', 'depeg', 'net', 'bench'):
            a[x] += r[x] * f
        a['n_hack'] += 1 if r['hack'] < 0 else 0
        a['n_depeg'] += 1 if r['depeg'] < 0 else 0
        a['n_collapse'] += 1 if r['collapse'] else 0
        a['n_dark'] += 1 if r['dark'] else 0
        a['tvl'] += r['tvl']
        a['pools'].add(r['pid'])
    res = {}
    for k, a in out.items():
        n = a['n']
        res[k] = {'pool_windows': n, 'pools': len(a['pools']), 'displayed': a['disp'] / n,
                  'realised_base': a['base'] / n, 'reward_face': a['face'] / n, 'reward_at_sale': a['sale'] / n,
                  'hack_loss': a['hack'] / n, 'depeg_loss': a['depeg'] / n, 'realised_net': a['net'] / n,
                  'savings': a['bench'] / n, 'net_excess': (a['net'] - a['bench']) / n,
                  'p_hack': a['n_hack'] / n, 'p_depeg': a['n_depeg'] / n, 'p_collapse': a['n_collapse'] / n,
                  'p_dark': a['n_dark'] / n, 'mean_tvl': a['tvl'] / n}
    return res


def new_chain_selector(ctx, window_days, pick, k=7, h=1.0, per_chain=3):
    """Chains aged 7..window_days days at D: their top `per_chain` eligible lending pools (by TVL or by score)."""
    def sel(D):
        el = ctx.eligible(D, k, 'lending')
        by_chain = {}
        for b, r, T, pid in el:
            ch = ctx.meta[pid]['chain']
            age = ctx.chain_age(ch, D)
            if age is None or age < 7 or age > window_days:
                continue
            by_chain.setdefault(ch, []).append(((b + h * r) if pick == 'score' else T, T, pid))
        ranked = []
        for ch, lst in by_chain.items():
            ranked += rank_pools(lst, per_chain)
        tv = {pid: T for _, _, T, pid in el}
        ranked.sort(key=lambda pid: (-tv[pid], pid))
        return ranked, set(ranked)
    return sel


def filtered_selector(ctx, sel, exclude_projects):
    """The same ranking with some venues removed (robustness rows, not part of the selection family)."""
    def f(D):
        ranked, elig = sel(D)
        keep = [p for p in ranked if ctx.meta[p]['project'] not in exclude_projects]
        return keep, {p for p in elig if ctx.meta[p]['project'] not in exclude_projects}
    return f


def guarded_selector(ctx, k, h, uni, run_drop=0.5, spike=2.0):
    """Diagnostic (post hoc, never used for selection): the score ranking without pools in a run (TVL the day
    before D below run_drop x its maximum over the previous week) or in a spike (trailing-7 score above `spike` x the
    trailing-30 score). Both use data before D only."""
    base = score_selector(ctx, k, h, uni)

    def f(D):
        ranked, elig = base(D)
        bad = set()
        for pid in ranked[:40]:
            P = ctx.pools[pid]
            t1 = P.tvl_before(D)
            mx = max([r[0] for r in (P.at(x) for x in range(D - 8, D - 1)) if r is not None] or [0.0])
            if t1 is not None and mx > 0 and t1 < run_drop * mx:
                bad.add(pid)
                continue
            a, b = P.trailing(D, 7), P.trailing(D, 30)
            if a and b and (b[0] + h * b[1]) > 0 and (a[0] + h * a[1]) > spike * (b[0] + h * b[1]):
                bad.add(pid)
        return [p for p in ranked if p not in bad], {p for p in elig if p not in bad}
    return f


def filtered_selector_pools(sel, drop):
    def f(D):
        ranked, elig = sel(D)
        return [p for p in ranked if p not in drop], {p for p in elig if p not in drop}
    return f


def filtered_audited(ctx, sel):
    """Keep only pools with a share-price series."""
    def f(D):
        ranked, elig = sel(D)
        return [p for p in ranked if p in ctx.share_px], {p for p in elig if p in ctx.share_px}
    return f


def audited_split(ctx, res):
    """Excess P&L (dollars) by whether the pool's yield is checked by a share-price series (accruing vault share,
    rebasing receipt) or rests on DefiLlama's apyBase alone."""
    out = {}
    for pid, st in res['by_pool'].items():
        k = ('share_accruing' if ctx.share_accruing.get(pid) else 'share_flat') if pid in ctx.share_px else 'unaudited'
        a = out.setdefault(k, {'pools': 0, 'excess_usd': 0.0, 'loss_usd': 0.0, 'days': 0})
        a['pools'] += 1
        a['excess_usd'] += st['base'] + st['reward'] - st['cost'] + st['loss'] - st['bench']
        a['loss_usd'] += st['loss']
        a['days'] += st['days']
    return out


def tvl_selector(ctx, uni, k=7):
    """Reference: the largest eligible pools by TVL, ignoring yield (what does ranking by yield add?)."""
    def sel(D):
        el = ctx.eligible(D, k, uni)
        return rank_pools([(T, T, pid) for _, _, T, pid in el], len(el)), {pid for _, _, _, pid in el}
    return sel


def fixed_selector(ctx, pid):
    def sel(D):
        return ([pid], {pid}) if ctx.pools[pid].at(D - 1) else ([], set())
    return sel


def pnl_concentration(res, lo, hi, X_bench=True):
    """Share of the period's excess P&L (pool P&L minus the savings it displaced) from the five best pools."""
    # by_pool is over the whole run; recompute per-period from events is costly, so the run is repeated on the
    # period by the caller. Here: rank pools by excess dollars.
    ex = {pid: st['base'] + st['reward'] - st['cost'] + st['loss'] - st['bench'] for pid, st in res['by_pool'].items()}
    tot = sum(ex.values())
    top = sorted(ex.items(), key=lambda kv: -kv[1])[:5]
    return {'total_excess_usd': tot, 'top5': [[pid, v] for pid, v in top],
            'top5_share': (sum(v for _, v in top) / tot) if tot > 0 else None, 'n_pools': len(ex)}


def capacity_now(ctx, picks, D, h_eff, m):
    out = []
    for pid in picks:
        P = ctx.pools[pid]
        tr = P.trailing(D, 7)
        T = P.tvl_before(D)
        if tr is None or not T:
            continue
        y = (tr[0] + h_eff * tr[1]) / 100.0
        out.append({'pool': pid, 'project': ctx.meta[pid]['project'], 'chain': ctx.meta[pid]['chain'],
                    'symbol': ctx.meta[pid]['symbol'], 'tvl': T, 'base_7d': tr[0], 'reward_7d': tr[1],
                    'yield_eff': y, 'x_star': capacity_deposit(y, T, m)})
    return out


def incentive_spend(rows_compact, fields):
    """Annual incentive spend sum(tvlUsd * apyReward/100): raw, and clean (apyReward <= 500%, TVL >= $10k), by
    stable vs volatile, exposure, chain and project."""
    ix = {f: i for i, f in enumerate(fields)}
    tot = {'raw': 0.0, 'clean': 0.0}
    by = {'stable': {}, 'exposure': {}, 'chain': {}, 'project': {}}
    n_pay = 0
    for r in rows_compact:
        tvl = r[ix['tvlUsd']] or 0.0
        ar = r[ix['apyReward']] or 0.0
        if ar <= 0 or tvl <= 0:
            continue
        v = tvl * ar / 100.0
        tot['raw'] += v
        if ar > 500 or tvl < 1e4:
            continue
        n_pay += 1
        tot['clean'] += v
        st = 'stable' if r[ix['stablecoin']] else 'volatile'
        by['stable'][st] = by['stable'].get(st, 0.0) + v
        ex = r[ix['exposure']] or '?'
        by['exposure'][ex] = by['exposure'].get(ex, 0.0) + v
        by['chain'][r[ix['chain']]] = by['chain'].get(r[ix['chain']], 0.0) + v
        by['project'][r[ix['project']]] = by['project'].get(r[ix['project']], 0.0) + v
        if r[ix['stablecoin']] and r[ix['exposure']] == 'single' and not NON_USD.search(str(r[ix['symbol']] or '')):
            by.setdefault('usd_stable_single', {'usd': 0.0, 'tvl': 0.0})
            by['usd_stable_single']['usd'] += v
            by['usd_stable_single']['tvl'] += tvl
    res = {'total_raw_usd': tot['raw'], 'total_clean_usd': tot['clean'], 'pools_paying': n_pay,
           'stable_vs_volatile': by['stable'], 'by_exposure': by['exposure'],
           'usd_stable_single': by.get('usd_stable_single'),
           'top_chains': sorted(by['chain'].items(), key=lambda kv: -kv[1])[:30],
           'top_projects': sorted(by['project'].items(), key=lambda kv: -kv[1])[:30],
           'by_chain_all': by['chain'], 'filters': 'clean = apyReward <= 500% and tvlUsd >= $10k'}
    return res


def missing_chart_check(ctx, top=10):
    """Would the pools without a chart have been picked? At every capture, rank the dollar pools with TVL >= $1M by
    the yield shown at the capture (base + reward, <= APY_CAP) and count top-`top` slots held by pools with no chart,
    for the whole universe and for blue-chip lending."""
    out = {}
    for uni in ('all', 'bluechip'):
        slots = missing = 0
        examples = []
        for d, ts, s_ in load_snapshots():
            rows = []
            for r in s_['stable_single_usd']:
                if not is_usd_stable_row(r) or (fnum(r.get('tvlUsd'), 0.0) or 0.0) < 1e6:
                    continue
                if uni == 'bluechip' and not ctx.is_bluechip(r.get('project'), d):
                    continue
                y = (fnum(r.get('apyBase'), 0.0) or 0.0) + (fnum(r.get('apyReward'), 0.0) or 0.0)
                if y <= APY_CAP:
                    rows.append((y, r.get('pool'), r.get('project'), r.get('chain'), r.get('symbol')))
            rows.sort(key=lambda x: -x[0])
            for y, pid, proj, ch, sym in rows[:top]:
                slots += 1
                if pid not in ctx.pools:
                    missing += 1
                    if len(examples) < 15:
                        examples.append([ymd(d), proj, ch, sym, round(y, 2)])
        out[uni] = {'top': top, 'slots': slots, 'slots_without_chart': missing,
                    'share': missing / slots if slots else None, 'examples': examples}
    return out


def top_slot_pools(ctx, top=20):
    """Pools that sat in the top `top` by displayed yield (TVL >= $1M) of either universe at any capture, most
    frequent first: the fetch priority when the chart API throttles."""
    cnt = {}
    for d, ts, s_ in load_snapshots():
        for uni in ('all', 'bluechip'):
            rows = []
            for r in s_['stable_single_usd']:
                if not is_usd_stable_row(r) or (fnum(r.get('tvlUsd'), 0.0) or 0.0) < 1e6:
                    continue
                if uni == 'bluechip' and not ctx.is_bluechip(r.get('project'), d):
                    continue
                y = (fnum(r.get('apyBase'), 0.0) or 0.0) + (fnum(r.get('apyReward'), 0.0) or 0.0)
                if y <= APY_CAP:
                    rows.append((y, r.get('pool')))
            rows.sort(key=lambda x: -x[0])
            for _, pid in rows[:top]:
                cnt[pid] = cnt.get(pid, 0) + 1
    return [p for p, _ in sorted(cnt.items(), key=lambda kv: -kv[1])]


def merkl_summary(m=SSR_NOW + 0.01):
    """Live Merkl campaigns (2026-10-10): the annualised reward budget, how much of it pays dollar-token positions,
    and the live candidates for this study (dollar token, LEND/HOLD/POOL single-asset actions, TVL >= $1M) with the
    deposit at which each one's marginal APR falls to SSR + 1pp (the campaign APR is all reward, so it dilutes fully)."""
    p = RAW / 'merkl' / 'opportunities_live.json.gz'
    if not p.exists():
        return None
    ops = read_gz(p)
    tot = sum((o.get('dailyRewards') or 0) for o in ops) * 365
    dollar = [o for o in ops if any(DOLLAR.search(str(t.get('symbol') or '')) for t in o.get('tokens') or [])]
    by_chain, by_action = {}, {}
    for o in dollar:
        v = (o.get('dailyRewards') or 0) * 365
        by_chain[str(o.get('chainId'))] = by_chain.get(str(o.get('chainId')), 0.0) + v
        by_action[o.get('action')] = by_action.get(o.get('action'), 0.0) + v
    cands = []
    for o in dollar:
        tvl = fnum(o.get('tvl'), 0.0) or 0.0
        apr = (fnum(o.get('apr'), 0.0) or 0.0) / 100.0
        if tvl < 1e6 or o.get('action') not in ('LEND', 'HOLD') or len(o.get('tokens') or []) > 2:
            continue
        x = capacity_deposit(apr + SSR_NOW, tvl, m)   # reward on top of a savings-rate-like base
        cands.append({'name': o.get('name'), 'chainId': o.get('chainId'), 'action': o.get('action'), 'tvl': tvl,
                      'apr_reward': apr, 'x_star_if_base_is_ssr': x, 'tags': o.get('tags')})
    cands.sort(key=lambda c: -c['x_star_if_base_is_ssr'])
    return {'opportunities': len(ops), 'annual_rewards_usd': tot, 'dollar_token_opportunities': len(dollar),
            'dollar_token_annual_rewards_usd': sum((o.get('dailyRewards') or 0) for o in dollar) * 365,
            'by_chain_id': sorted(by_chain.items(), key=lambda kv: -kv[1])[:15],
            'by_action': by_action, 'lend_hold_candidates_tvl_1m': len(cands),
            'candidates_reward_apr_above_1pp': sum(1 for c in cands if c['apr_reward'] > 0.01),
            'sum_x_star_if_base_is_ssr': sum(c['x_star_if_base_is_ssr'] for c in cands), 'top': cands[:15],
            'note': 'x_star assumes each position also earns a base equal to the SSR; campaign rules (looping, '
                    'borrow requirements, KYC, caps) are not checked'}


def by_year(weeks):
    out = {}
    for w0, r, b, x in weeks:
        y = ymd(w0)[:4]
        a = out.setdefault(y, [0, 0.0, 0.0])
        a[0] += 1
        a[1] += r
        a[2] += x
    return {y: {'weeks': a[0], 'ann_return': a[1] / a[0] * PPY_WEEK, 'ann_excess': a[2] / a[0] * PPY_WEEK}
            for y, a in sorted(out.items())}


LOSS_TYPES = ('hack', 'depeg', 'share', 'share_stuck', 'depeg_open', 'share_open', 'share_stuck_open', 'collapse',
              'dark')


def loss_summary(ctx, res):
    """Events of a run aggregated by type and by venue category (dollars at the run's capital)."""
    by_type, by_cat = {}, {}
    for e in res['events']:
        if e['type'] not in LOSS_TYPES:
            continue
        cat = ctx.category(ctx.meta[e['pool']]['project'])
        t = by_type.setdefault(e['type'], {'n': 0, 'usd': 0.0})
        t['n'] += 1
        t['usd'] += e.get('loss', 0.0)
        c = by_cat.setdefault(cat, {})
        c2 = c.setdefault(e['type'], {'n': 0, 'usd': 0.0})
        c2['n'] += 1
        c2['usd'] += e.get('loss', 0.0)
    return {'by_type': by_type, 'by_category': by_cat,
            'events': [dict(e, project=ctx.meta[e['pool']]['project'], chain=ctx.meta[e['pool']]['chain'],
                            symbol=ctx.meta[e['pool']]['symbol'])
                       for e in res['events'] if e['type'] in LOSS_TYPES and (e.get('loss') or e['type'] in ('collapse', 'dark'))][:120]}


def run_summary(res, split, lo=None):
    w = res['weeks']
    yrs = len(w) / PPY_WEEK
    out = {'full': series_stats(w), 'in_sample': series_stats(w, hi=split), 'out_of_sample': series_stats(w, lo=split),
           'by_year': by_year(w), 'switches_per_year': res['switches'] / yrs if yrs else None}
    oos = [x for x in w if x[0] >= split]
    if len(oos) >= 8:
        h = len(oos) // 2
        out['oos_first_half'] = series_stats(oos[:h])
        out['oos_second_half'] = series_stats(oos[h:])
        out['last_52w'] = series_stats(w[-52:])
    tot = {'base': 0.0, 'reward': 0.0, 'reward_imputed': 0.0, 'cost': 0.0, 'loss': 0.0, 'days': 0}
    for st in res['by_pool'].values():
        for k in tot:
            tot[k] += st[k]
    out['pnl_components_usd'] = tot
    return out


def main_analyze(args):
    t0 = time.time()
    universe = read_gz(RAW / 'universe.json.gz')
    ctx = Ctx(universe)
    start, split, end = day_of(START), day_of(SPLIT), day_of('2026-10-10')
    A = {'generated': now_iso(), 'protocol': {
        'start': START, 'split': SPLIT, 'end_exclusive': ymd(end), 'decision': 'weekly, Mondays 00:00 UTC, data '
        'strictly before the decision day', 'N': N_MAIN, 'buffer': '2N', 'capital_for_selection': CAP_MAIN,
        'grid': [vname(v) for v in GRID], 'choose_on': 'in-sample mean weekly excess over the savings rate paid',
        'apy_cap_pct': APY_CAP, 'fresh_days': FRESH_DAYS, 'depeg_band': DEPEG_BAND, 'entry_min_px': ENTRY_MIN_PX,
        'freeze_days': FREEZE_DAYS, 'claim_every_days': CLAIM_EVERY, 'sale_lag_days': SALE_LAG,
        'reward_sale_cost': REWARD_SALE_COST, 'tvl_min': 1e6, 'benchmark': ctx.savings_source}}
    A['data'] = {'pools_in_universe': len(universe), 'pools_with_chart': len(ctx.pools),
                 'pools_rebuilt_from_captures': len(ctx.synthetic),
                 'bad_records_dropped': ctx.bad_records, 'protocols_with_tvl': len(ctx.proto_tvl),
                 'hack_events_matched': len(ctx.hack_join['matched']),
                 'hack_matches': ctx.hack_join['matched'], 'large_hacks_unmatched': ctx.hack_join['unmatched_large'],
                 'coins_priced': len(ctx.coin), 'pools_with_reward_prices': sum(1 for v in ctx.reward_px.values() if v),
                 'pools_listing_reward_tokens': sum(1 for p in ctx.pools if universe[p].get('reward_tokens')),
                 'pools_with_deposit_price': len(ctx.dep_px), 'impute_ratio': ctx.impute_ratio,
                 'impute_ratio_n': ctx.impute_n, 'chains_with_launch': len(ctx.chain_launch)}
    ctx.log('ctx loaded %.0fs: %s' % (time.time() - t0, {k: v for k, v in A['data'].items()
                                                          if not isinstance(v, list)}))

    # 1. the pre-committed grid at $1M
    runs = {}
    for v in GRID:
        runs[vname(v)] = simulate(ctx, score_selector(ctx, v['k'], v['h'], v['universe']), N_MAIN, v['H'], CAP_MAIN,
                                  start, end)
    held = sorted({pid for r in runs.values() for pid in r['by_pool']})
    write_json(RAW / 'held_pools.json', held)
    ctx.log('grid done %.0fs, %d pools held by some variant' % (time.time() - t0, len(held)))
    axis = [w[0] for w in next(iter(runs.values()))['weeks']]
    cut = next(i for i, w0 in enumerate(axis) if w0 >= split)
    frac = cut / len(axis)
    grid_rows = {}
    for nm, r in runs.items():
        grid_rows[nm] = {'in_sample': series_stats(r['weeks'], hi=split), 'out_of_sample': series_stats(r['weeks'], lo=split),
                         'switches_per_year': r['switches'] / (len(r['weeks']) / PPY_WEEK)}
    oos_p = [grid_rows[vname(v)]['out_of_sample']['nw_p'] for v in GRID]
    rej, adj = B.bh(oos_p, q=0.10)
    for v, rj, a in zip(GRID, rej, adj):
        grid_rows[vname(v)]['oos_bh_adj_p'] = a
        grid_rows[vname(v)]['oos_bh_reject'] = rj
    A['grid'] = grid_rows
    chosen = {}
    for uni in ('all', 'bluechip'):
        names = [vname(v) for v in GRID if v['universe'] == uni]
        ct = B.choose_then_test({nm: [w[3] for w in runs[nm]['weeks']] for nm in names}, frac=frac,
                                periods_per_year=PPY_WEEK, key='ann_return')
        nm = ct['chosen']
        oos = [w[3] for w in runs[nm]['weeks'][cut:]]
        ins_sr = [grid_rows[n]['in_sample']['sharpe_excess'] for n in names
                  if grid_rows[n]['in_sample'].get('sharpe_excess') is not None]
        sr_std = statistics.pstdev(ins_sr) / math.sqrt(PPY_WEEK) if len(ins_sr) > 1 else None
        ct['deflated_sharpe_oos'] = B.deflated_sharpe(oos, len(names), sr_std)
        ct['oos_rank_of'] = len(names)
        chosen[uni] = ct
    A['choose_then_test'] = {u: {k: v for k, v in ct.items() if k not in ('bh_adjusted_p',)} for u, ct in chosen.items()}

    # 2. the chosen variants in detail
    detail = {}
    for uni, ct in chosen.items():
        v = next(x for x in GRID if vname(x) == ct['chosen'])
        sel = score_selector(ctx, v['k'], v['h'], uni)
        main = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, record=True)
        d = {'variant': vname(v), 'main_1m': run_summary(main, split), 'losses_1m': loss_summary(ctx, main)}
        for cap in (1e5, 1e7):
            r = simulate(ctx, sel, N_MAIN, v['H'], cap, start, end)
            d['capital_%d' % int(cap)] = run_summary(r, split)
        d['capital_curve_oos'] = {}
        for cap in (1e5, 3e5, 1e6, 2e6, 3e6, 5e6, 1e7, 2e7):
            r = simulate(ctx, sel, N_MAIN, v['H'], cap, start, end)
            st = series_stats(r['weeks'], lo=split)
            d['capital_curve_oos'][str(int(cap))] = {'ann_excess': st['ann_excess'], 'nw_t': st['nw_t'],
                                                     'usd_per_year': st['ann_excess'] * cap}
        for nn in (1, 10):
            r = simulate(ctx, sel, nn, v['H'], CAP_MAIN, start, end)
            d['N%d' % nn] = run_summary(r, split)
        for delay in (1, 7):
            r = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, delay=delay)
            d['delay_%dd' % delay] = run_summary(r, split)
        for mode in ('face', 'none'):
            r = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, reward_mode=mode)
            d['reward_%s' % mode] = run_summary(r, split)
        for cl in (0.1, 0.5):
            r = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, collapse_loss=cl)
            d['stress_collapse_%g' % cl] = run_summary(r, split)
        r = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, losses=False)
        d['no_losses'] = run_summary(r, split)
        r = simulate(ctx, filtered_selector(ctx, sel, {'pendle', 'pendle-v2', 'notional', 'notional-v2', 'notional-v3',
                                                         'spectra-v2', 'stake-dao'}),
                     N_MAIN, v['H'], CAP_MAIN, start, end)
        d['ex_pendle_notional'] = run_summary(r, split)
        d['audited_split_1m'] = audited_split(ctx, main)
        syn_days = sum(n for p, n in main['hold_days'].items() if p in ctx.synthetic)
        d['days_in_capture_rebuilt_pools_share'] = syn_days / max(1, sum(main['hold_days'].values()))
        r = simulate(ctx, filtered_selector_pools(sel, ctx.synthetic), N_MAIN, v['H'], CAP_MAIN, start, end)
        d['without_capture_rebuilt_pools'] = run_summary(r, split)
        alive = {p for p in ctx.pools if universe[p].get('last_snap') == day_of('2026-10-10')}
        r = simulate(ctx, score_selector(ctx, v['k'], v['h'], uni, alive), N_MAIN, v['H'], CAP_MAIN, start, end)
        d['alive_only_survivorship_biased'] = run_summary(r, split)
        oos_run = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, split, end, record=True)
        d['oos_concentration'] = pnl_concentration(oos_run, split, end)
        for row in d['oos_concentration']['top5']:
            row.append(ctx.meta[row[0]]['project'])
            row.append(ctx.meta[row[0]]['chain'])
            row.append(ctx.meta[row[0]]['symbol'])
        dead_days = sum(n for p, n in main['hold_days'].items() if p not in alive)
        d['days_in_pools_dead_today_share'] = dead_days / max(1, sum(main['hold_days'].values()))
        d['top_held'] = sorted([[p, n, ctx.meta[p]['project'], ctx.meta[p]['chain'], ctx.meta[p]['symbol']]
                                for p, n in main['hold_days'].items()], key=lambda x: -x[1])[:15]
        detail[uni] = d
        ctx.log('detail %s done %.0fs' % (uni, time.time() - t0))
    A['chosen_detail'] = detail

    # 2b. the audited family (added after the first results, disclosed as post hoc): the same grid, restricted to
    # pools whose realised return a share-price series can check (vault shares: the claimed yield must show up in
    # the share price; rebasing receipts: priced like the underlying). Chosen and tested the same way.
    aud = {}
    aud_runs = {}
    for v in GRID:
        sel = filtered_audited(ctx, score_selector(ctx, v['k'], v['h'], v['universe']))
        aud_runs[vname(v)] = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end)
    aud['grid'] = {nm: {'in_sample': series_stats(r['weeks'], hi=split), 'out_of_sample': series_stats(r['weeks'], lo=split)}
                   for nm, r in aud_runs.items()}
    a_p = [aud['grid'][vname(v)]['out_of_sample']['nw_p'] for v in GRID]
    a_rej, a_adj = B.bh(a_p, q=0.10)
    for v, rj, a in zip(GRID, a_rej, a_adj):
        aud['grid'][vname(v)]['oos_bh_adj_p'] = a
        aud['grid'][vname(v)]['oos_bh_reject'] = rj
    aud['choose_then_test'] = {}
    aud['detail'] = {}
    for uni in ('all', 'bluechip'):
        names = [vname(v) for v in GRID if v['universe'] == uni]
        ct = B.choose_then_test({nm: [w[3] for w in aud_runs[nm]['weeks']] for nm in names}, frac=frac,
                                periods_per_year=PPY_WEEK, key='ann_return')
        oos = [w[3] for w in aud_runs[ct['chosen']]['weeks'][cut:]]
        ins_sr = [aud['grid'][n]['in_sample'].get('sharpe_excess') for n in names]
        ins_sr = [x for x in ins_sr if x is not None]
        ct['deflated_sharpe_oos'] = B.deflated_sharpe(oos, len(names), statistics.pstdev(ins_sr) / math.sqrt(PPY_WEEK)
                                                      if len(ins_sr) > 1 else None)
        aud['choose_then_test'][uni] = {k: v for k, v in ct.items() if k != 'bh_adjusted_p'}
        v = next(x for x in GRID if vname(x) == ct['chosen'])
        sel = filtered_audited(ctx, score_selector(ctx, v['k'], v['h'], uni))
        main = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, record=True)
        dd = {'variant': vname(v), 'main_1m': run_summary(main, split), 'losses_1m': loss_summary(ctx, main),
              'audited_split_1m': audited_split(ctx, main)}
        for cap in (1e5, 1e7):
            dd['capital_%d' % int(cap)] = run_summary(simulate(ctx, sel, N_MAIN, v['H'], cap, start, end), split)
        for delay in (1, 7):
            dd['delay_%dd' % delay] = run_summary(simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, delay=delay),
                                                  split)
        dd['no_losses'] = run_summary(simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, losses=False), split)
        dd['capital_curve_oos'] = {}
        for cap in (1e5, 3e5, 1e6, 2e6, 3e6, 5e6, 1e7):
            st = series_stats(simulate(ctx, sel, N_MAIN, v['H'], cap, start, end)['weeks'], lo=split)
            dd['capital_curve_oos'][str(int(cap))] = {'ann_excess': st['ann_excess'], 'nw_t': st['nw_t'],
                                                      'usd_per_year': st['ann_excess'] * cap}
        dd['reward_none'] = run_summary(simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end, reward_mode='none'),
                                        split)
        oos_run = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, split, end, record=True)
        dd['oos_concentration'] = pnl_concentration(oos_run, split, end)
        for row in dd['oos_concentration']['top5']:
            row += [ctx.meta[row[0]]['project'], ctx.meta[row[0]]['chain'], ctx.meta[row[0]]['symbol']]
        dd['top_held'] = sorted([[p, n, ctx.meta[p]['project'], ctx.meta[p]['chain'], ctx.meta[p]['symbol']]
                                 for p, n in main['hold_days'].items()], key=lambda x: -x[1])[:15]
        aud['detail'][uni] = dd
    aud['pools_with_share_series'] = len(ctx.share_px)
    aud['accruing'] = sum(1 for p in ctx.share_px if ctx.share_accruing.get(p))
    A['audited'] = aud
    ctx.log('audited family done %.0fs' % (time.time() - t0))

    # diagnostic (post hoc, labelled): does a pre-entry run/spike guard change the family? Not used for any choice.
    diag = {}
    for v in GRID:
        r = simulate(ctx, guarded_selector(ctx, v['k'], v['h'], v['universe']), N_MAIN, v['H'], CAP_MAIN, start, end)
        diag[vname(v)] = {'in_sample': series_stats(r['weeks'], hi=split), 'out_of_sample': series_stats(r['weeks'], lo=split)}
    A['diagnostic_run_spike_guard'] = {'note': 'post hoc: excludes pools whose TVL fell below half of the prior '
                                               "week's maximum or whose trailing-7 score exceeds 2x the trailing-30 "
                                               'score; data before D only; for a forward test, not for this verdict',
                                       'grid': diag}
    ctx.log('guard diagnostic done %.0fs' % (time.time() - t0))
    curated = {'morpho-blue', 'morpho-v1', 'euler-v2', 'morpho-aave', 'morpho-compound', 'morpho-aavev3',
               'morpho-v0-aavev2', 'morpho-v0-compoundv2'}
    pooled = {}
    for v in GRID:
        if v['universe'] != 'bluechip':
            continue
        sel = filtered_selector(ctx, score_selector(ctx, v['k'], v['h'], 'bluechip'), curated)
        r = simulate(ctx, sel, N_MAIN, v['H'], CAP_MAIN, start, end)
        pooled[vname(v)] = {'in_sample': series_stats(r['weeks'], hi=split),
                            'out_of_sample': series_stats(r['weeks'], lo=split)}
    A['diagnostic_bluechip_pooled_only'] = {'note': 'post hoc: blue-chip rule without curated-vault platforms '
                                                    '(Morpho vaults, Euler v2)', 'excluded': sorted(curated),
                                            'grid': pooled}
    fam = [A['grid'][vname(v)]['out_of_sample']['ann_excess'] for v in GRID if v['universe'] == 'bluechip']
    A['bluechip_family_oos'] = {'mean_ann_excess': sum(fam) / len(fam), 'n_negative': sum(1 for x in fam if x < 0),
                                'min': min(fam), 'max': max(fam)}
    # the event behind the negative blue-chip variants: the worst variant's largest losses, with share prices
    worst = min((v for v in GRID if v['universe'] == 'bluechip'),
                key=lambda v: A['grid'][vname(v)]['out_of_sample']['ann_excess'])
    rw = simulate(ctx, score_selector(ctx, worst['k'], worst['h'], 'bluechip'), N_MAIN, worst['H'], CAP_MAIN, start,
                  end, record=True)
    evs = sorted([e for e in rw['events'] if e.get('loss')], key=lambda e: e['loss'])[:5]
    for e in evs:
        e.update(ctx.meta[e['pool']])
        if e.get('entry') and e['pool'] in ctx.share_px:
            e['share_px_entry'] = ctx.share_price(e['pool'], day_of(e['entry']))
            e['share_px_exit'] = ctx.share_price(e['pool'], day_of(e['day']))
    A['bluechip_family_oos']['worst_variant'] = vname(worst)
    A['bluechip_family_oos']['worst_variant_losses'] = evs

    # references: biggest pools by TVL (no yield ranking) and the always-on blue-chip lending pool
    refs = {}
    for uni in ('all', 'bluechip'):
        r = simulate(ctx, tvl_selector(ctx, uni), N_MAIN, 4, CAP_MAIN, start, end)
        refs['top5_by_tvl_%s_H4' % uni] = run_summary(r, split)
    aave = max((p for p in ctx.pools if ctx.meta[p]['project'] == 'aave-v3' and ctx.meta[p]['chain'] == 'Ethereum'
                and str(ctx.meta[p]['symbol']).upper() == 'USDC'), key=lambda p: universe[p]['max_tvl'], default=None)
    if aave:
        r = simulate(ctx, fixed_selector(ctx, aave), 1, 52, CAP_MAIN, start, end)
        refs['aave_v3_usdc_ethereum_hold'] = dict(run_summary(r, split), pool=aave)
    A['references'] = refs

    # 3. what you see vs what you get: every eligible pool on non-overlapping 4-week windows
    rows = window_study(ctx, start, end)
    A['windows'] = {
        'n_pool_windows': len(rows),
        'by_bucket_all': agg_rows(rows, lambda r: bucket_excess(r['disp_base'] + r['disp_rew'] - r['sav'])),
        'by_bucket_in_sample': agg_rows([r for r in rows if r['D'] < split],
                                        lambda r: bucket_excess(r['disp_base'] + r['disp_rew'] - r['sav'])),
        'by_bucket_oos': agg_rows([r for r in rows if r['D'] >= split],
                                  lambda r: bucket_excess(r['disp_base'] + r['disp_rew'] - r['sav'])),
        'by_category': agg_rows(rows, lambda r: r['cat']),
        'by_bluechip': agg_rows(rows, lambda r: 'bluechip' if r['blue'] else 'other'),
        'by_reward_share': agg_rows(rows, lambda r: 'no reward' if r['disp_rew'] <= 0 else
                                    ('reward < half' if r['disp_rew'] < r['disp_base'] else 'reward >= half')),
        # the same buckets for pools whose return a share price checks (vault shares: apyBase must show up in the
        # share price) against pools that rest on DefiLlama's apyBase alone
        'by_bucket_audited_vault_share': agg_rows(
            [r for r in rows if ctx.share_accruing.get(r['pid'])],
            lambda r: bucket_excess(r['disp_base'] + r['disp_rew'] - r['sav'])),
        'by_bucket_unaudited': agg_rows(
            [r for r in rows if r['pid'] not in ctx.share_px],
            lambda r: bucket_excess(r['disp_base'] + r['disp_rew'] - r['sav'])),
    }
    # 4. new-venue premium: chains first seen with TVL on/after 2022-09-01 (their youth is inside the sample)
    young_cut = day_of('2022-09-01')
    young = {c for c, f in ctx.chain_launch.items() if f >= young_cut}
    med_old = {}
    for r in rows:
        if safe(r['chain'] or '') not in young:
            med_old.setdefault(r['D'], []).append((r['disp_base'] + r['disp_rew']) / 100.0)
    med_old = {D: statistics.median(v) for D, v in med_old.items()}
    for r in rows:
        r['prem_disp'] = (r['disp_base'] + r['disp_rew']) / 100.0 - med_old.get(r['D'], 0.0)
    yrows = [r for r in rows if safe(r['chain'] or '') in young]
    curve = agg_rows(yrows, lambda r: age_bucket(r['chain_age']))
    for b, c in curve.items():
        sub = [r['prem_disp'] for r in yrows if age_bucket(r['chain_age']) == b]
        c['premium_vs_old_chain_median'] = sum(sub) / len(sub) if sub else None
        c['chains'] = len({r['chain'] for r in yrows if age_bucket(r['chain_age']) == b})
    pts_disp = [(AGE_MID[b], c['premium_vs_old_chain_median'] * 100.0, c['pool_windows']) for b, c in curve.items()
                if c.get('premium_vs_old_chain_median') is not None]
    pts_net = [(AGE_MID[b], c['net_excess'] * 100.0, c['pool_windows']) for b, c in curve.items()]
    old_net = agg_rows([r for r in rows if safe(r['chain'] or '') not in young], lambda r: 'old')
    A['new_venue'] = {
        'young_chains': sorted([[c, ymd(f)] for c, f in ctx.chain_launch.items() if f >= young_cut], key=lambda x: x[1]),
        'curve_by_chain_age': curve, 'old_chains': old_net,
        'half_life_displayed_premium': fit_half_life(pts_disp), 'half_life_net_excess': fit_half_life(pts_net),
        'by_pool_age': agg_rows(rows, lambda r: age_bucket(r['pool_age']))}
    nv = {}
    for wd in (90, 180):
        for pick in ('tvl', 'score'):
            r = simulate(ctx, new_chain_selector(ctx, wd, pick), N_MAIN, 1, CAP_MAIN, start, end, record=True)
            s_ = run_summary(r, split)
            s_['losses'] = loss_summary(ctx, r)['by_type']
            s_['chains_entered'] = sorted({ctx.meta[e['pool']]['chain'] for e in r['events'] if e['type'] == 'enter'})
            s_['active_weeks'] = sum(1 for w0, ret, b, x in r['weeks'] if abs(x) > 1e-9)
            for lab, lo, hi in (('in_sample', None, split), ('out_of_sample', split, None)):
                act = [x for w0, ret, b, x in r['weeks'] if abs(x) > 1e-9 and (lo is None or w0 >= lo)
                       and (hi is None or w0 < hi)]
                s_['%s_active' % lab] = {'weeks': len(act), 'ann_excess_when_active': sum(act) / len(act) * PPY_WEEK
                                         if act else None, 'nw_t': B.newey_west_t(act, lags=8)[0] if len(act) > 8 else None}
            nv['new_chain_lending_%dd_%s' % (wd, pick)] = s_
    A['new_venue']['rules'] = nv

    # 5. capacity now (last decision day) for the chosen picks and for the whole eligible universe
    D_last = start + 7 * ((end - 1 - start) // 7)
    m = SSR_NOW + 0.01
    h_sale = ctx.impute_ratio * (1.0 - REWARD_SALE_COST)
    cap = {'decision_day': ymd(D_last), 'marginal_hurdle': m, 'reward_value_per_face_dollar': h_sale}
    for uni, ct in chosen.items():
        v = next(x for x in GRID if vname(x) == ct['chosen'])
        el = ctx.eligible(D_last, v['k'], uni)
        picks = rank_pools([(b + v['h'] * r, T, pid) for b, r, T, pid in el], N_MAIN)
        cp = capacity_now(ctx, picks, D_last, v['h'] * ctx.impute_ratio * (1 - REWARD_SALE_COST), m)
        cap['chosen_%s' % uni] = {'picks': cp, 'sum_x_star': sum(c['x_star'] for c in cp)}
    for uni in ('all', 'bluechip'):
        el = ctx.eligible(D_last, 7, uni)
        cp = capacity_now(ctx, [pid for _, _, _, pid in el], D_last, h_sale, m)
        cp.sort(key=lambda c: -c['x_star'])
        cap['universe_%s' % uni] = {'eligible': len(el), 'above_hurdle': sum(1 for c in cp if c['x_star'] > 0),
                                    'sum_x_star': sum(c['x_star'] for c in cp), 'top': cp[:15]}
    A['capacity'] = cap

    # 6. incentive spend now (and through the Wayback captures)
    cur = compact_snapshot(read_gz(RAW / 'pools_2026-10-10.json.gz'))
    A['incentive_spend_now'] = incentive_spend(cur['all_compact'], cur['all_fields'])
    hist = []
    for d, ts, s_ in load_snapshots():
        sp = incentive_spend(s_['all_compact'], s_['all_fields'])
        hist.append([ymd(d), sp['total_clean_usd'], sp['stable_vs_volatile'].get('stable', 0.0),
                     sp['stable_vs_volatile'].get('volatile', 0.0),
                     (sp.get('usd_stable_single') or {}).get('usd', 0.0)])
    A['incentive_spend_history'] = {'fields': ['date', 'clean_total', 'stable', 'volatile', 'usd_stable_single'],
                                    'rows': hist}

    A['merkl_live'] = merkl_summary()

    # 7. survivorship
    man = json.loads((RAW / 'manifest_collect.json').read_text()) if (RAW / 'manifest_collect.json').exists() else {}
    # parallel collect runs overwrite each other's manifest entries: recount the captures from disk
    cdx = read_gz(RAW / 'wayback' / 'cdx.json.gz') if (RAW / 'wayback' / 'cdx.json.gz').exists() else [[]]
    man['wayback'] = {'capture_days_in_cdx': len(cdx) - 1, 'picked': len(wayback_pick(cdx[1:], (1, 8, 15, 22))),
                      'have': len(list((RAW / 'wayback').glob('2*.json.gz'))),
                      'first': ymd(load_snapshots()[0][0]), 'rule': 'closest capture within 7 days of the 1st, 8th, '
                      '15th and 22nd of each month'}
    dead = [p for p in ctx.pools if universe[p].get('last_snap') != day_of('2026-10-10')]
    A['survivorship'] = {'universe_build': man.get('universe'), 'wayback': man.get('wayback'),
                         'pools_with_chart': len(ctx.pools), 'dead_today': len(dead),
                         'dead_share': len(dead) / max(1, len(ctx.pools)),
                         'missing_chart_check': missing_chart_check(ctx),
                         'bound_sample': read_gz(RAW / 'survivorship_sample.json.gz')
                         if (RAW / 'survivorship_sample.json.gz').exists() else None}
    bs = A['survivorship'].get('bound_sample')
    if bs and bs.get('rows'):
        d0 = day_of(START)
        uni_days = 0
        for pid, P in ctx.pools.items():
            for d in range(max(P.first, d0), P.last + 1):
                r = P.at(d)
                if r is not None and r[0] >= 1e6:
                    uni_days += 1
        miss = sum(x['days_tvl_1m_after_start'] for x in bs['rows'])
        est = bs['unseen_in_universe_projects'] * miss / max(1, bs['fetched'])
        A['survivorship']['bound'] = {
            'universe_pool_days_tvl_1m_after_start': uni_days, 'sample_pool_days_tvl_1m': miss,
            'sample_pools_ever_1m': sum(1 for x in bs['rows'] if x['days_tvl_1m_after_start'] > 0),
            'estimated_missing_pool_days_tvl_1m': est, 'missing_share_upper_bound': est / max(1, uni_days + est),
            'note': 'never-captured ids from the universe projects, any asset (an upper bound for dollar pools)'}
        A['survivorship']['bound_sample'] = {k: v for k, v in bs.items() if k != 'rows'}
    vp = RAW / 'verify' / 'verify.json'
    A['verify'] = json.loads(vp.read_text()) if vp.exists() else None
    A['seconds'] = round(time.time() - t0, 1)
    write_json(OUT / 'analysis.json', A)
    write_manifest(ctx, A, man)
    ctx.log('analysis written %.0fs' % (time.time() - t0))


def write_manifest(ctx, A, man):
    uni = ctx.universe
    no_chart = [p for p in uni if p not in ctx.pools]
    no_chart_1m = [p for p in no_chart if uni[p]['max_tvl'] >= 1e6]
    held = json.loads((RAW / 'held_pools.json').read_text()) if (RAW / 'held_pools.json').exists() else []
    pc = json.loads((OUT / 'precommit.json').read_text()) if (OUT / 'precommit.json').exists() else {}
    M = {
        'generated': now_iso(), 'analysis_generated': A['generated'], 'script': 'scripts/incentive_yields.py',
        'precommit': {'file': 'precommit.json', 'written': pc.get('written'),
                      'code_sha256_at_freeze': pc.get('code_sha256_at_freeze')},
        'endpoints': {
            'yields': 'https://yields.llama.fi /pools (2026-10-10 snapshot), /chart/{pool} (daily), /distinctID '
                      '(401,835 pool ids, no metadata); /poolsOld and /lsdRates answer HTTP 402 (paid)',
            'wayback': 'http://web.archive.org/cdx/search/cdx?url=yields.llama.fi/pools + /web/{ts}id_/https://'
                       'yields.llama.fi/pools (captures closest to the 1st/8th/15th/22nd of each month)',
            'llama': 'https://api.llama.fi /hacks, /protocols, /protocol/{slug} (TVL history), '
                     '/v2/historicalChainTvl/{chain}',
            'stablecoins': 'https://stablecoins.llama.fi /stablecoins, /stablecoinprices',
            'coins': 'https://coins.llama.fi/chart/{chain:address}?start&span=500&period=1d (500 points per request)',
            'chain': 'public Ethereum archive RPC (scripts/drpc.py): Aave v3 / Spark getReserveData, Comet '
                     'getUtilization + getSupplyRate'},
        'counts': {'wayback_captures_used': (man.get('wayback') or {}).get('have'),
                   'wayback_capture_days_in_cdx': (man.get('wayback') or {}).get('capture_days_in_cdx'),
                   'universe_pools': len(uni), 'universe_pools_max_tvl_1m': sum(1 for u in uni.values() if u['max_tvl'] >= 1e6),
                   'charts_loaded': len(ctx.pools), 'charts_missing': len(no_chart),
                   'charts_missing_with_tvl_1m_at_a_capture': len(no_chart_1m),
                   'protocol_tvl_series': len(ctx.proto_tvl), 'coins_priced': len(ctx.coin),
                   'held_pools_any_variant': len(held), 'chains_with_launch': len(ctx.chain_launch),
                   'hack_matches': len(ctx.hack_join['matched'])},
        'rate_policy': 'one process per host family; DefiLlama request starts >= 0.4 s apart (0.7 s for the parallel '
                       'coins/protocol runs); yields.llama.fi answered HTTP 429 to roughly two requests in three from '
                       '15:45 UTC (shared IP), so charts arrived at ~0.3 a second and were fetched in priority order',
        'gaps': [
            'charts not fetched (API throttling): %d universe pools, of which %d had TVL >= $1M at some capture; '
            'they were last in the queue (lowest yield seen at a capture), see survivorship.missing_chart_check'
            % (len(no_chart), len(no_chart_1m)),
            'DefiLlama floors vault yields at zero (3 negative apyBase records in the charts): vault-level bad debt '
            'is invisible unless it shows as a matched hack, a deposit-token depeg or a TVL collapse',
            'pricePerShare exists only from 2026-02 (151 pools); not used',
            'rewards with no priced token are valued at the in-sample median 8-day price ratio (impute_ratio)',
            'reward vesting/lock-ups (e.g. Radiant dLP, Venus XVS vesting) are not modelled; DefiLlama face value is used',
            'lending TVL on DefiLlama is supply net of borrows, so the dilution T/(T+X) is conservative there',
            'part (b), hedged LP, was not run',
        ],
        'collect_manifest': man,
    }
    write_json(OUT / 'manifest.json', M)


def collect_lp(net, log, limit=None):
    """Part (b), hedged LP, was not run (see the note): the throttled chart API left no time for it."""
    return {'skipped': 'part (b) not run'}


def collect_survivorship_sample(net, log, n=80, seed=11):
    """Bound the pools the Wayback captures missed. /distinctID lists every pool id DefiLlama ever tracked but
    without symbol or chain; take the ids never seen at any capture, keep those from projects that appear in the
    dollar universe, draw a fixed random sample, fetch their charts and measure how many had TVL >= $1M after the
    first capture (and for how many days). The share is an upper bound: the sample is not restricted to stables."""
    import random
    ids = read_gz(RAW / 'distinctID.json.gz')
    seen = set()
    for _, _, snap in load_snapshots():
        for r in snap['all_compact']:
            seen.add(r[0])
    uni = read_gz(RAW / 'universe.json.gz')
    projects = {u.get('project') for u in uni.values()}
    cand = sorted(x['config_id'] for x in ids if x.get('config_id') not in seen and x.get('project') in projects)
    rng = random.Random(seed)
    sample = rng.sample(cand, min(n, len(cand)))
    d0 = day_of(START)
    rows = []
    for pid in sample:
        p = RAW / 'charts_unseen' / ('%s.json.gz' % pid)
        if p.exists():
            r = read_gz(p)
        else:
            r = net.get('%s/chart/%s' % (YIELDS, pid))
            if isinstance(r, dict) and '_failed' in r:
                continue
            write_gz(p, r)
        data = r.get('data') or [] if isinstance(r, dict) else []
        days_1m = sum(1 for x in data if day_of(x['timestamp']) >= d0 and (fnum(x.get('tvlUsd'), 0) or 0) >= 1e6)
        mx = max([fnum(x.get('tvlUsd'), 0) or 0 for x in data if day_of(x['timestamp']) >= d0] or [0])
        first = day_of(data[0]['timestamp']) if data else None
        last = day_of(data[-1]['timestamp']) if data else None
        rows.append({'pool': pid, 'records': len(data), 'first': ymd(first) if first else None,
                     'last': ymd(last) if last else None, 'max_tvl_after_start': mx, 'days_tvl_1m_after_start': days_1m})
    out = {'distinct_ids': len(ids), 'ids_seen_at_captures': len(seen), 'unseen_in_universe_projects': len(cand),
           'sampled': len(sample), 'fetched': len(rows), 'rows': rows}
    write_gz(RAW / 'survivorship_sample.json.gz', out)
    return {k: v for k, v in out.items() if k != 'rows'}


AAVE_V3_POOL = '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2'
SPARK_POOL = '0xC13e21B648A5Ee794902342038FF3aDAB66BE987'
COMET_USDC = '0xc3d688B66703497DAA19211EEdff47f25384cdc3'
USDC_ETH = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
DAI_ETH = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
USDT_ETH = '0xdAC17F958D2ee523a2206206994597C13D831ec7'
SEL_GET_RESERVE_DATA = '0x35ea6a75'   # getReserveData(address)
SEL_GET_UTILIZATION = '0x7eb71131'    # getUtilization()
SEL_GET_SUPPLY_RATE = '0xd955759d'    # getSupplyRate(uint256)
SECONDS_PER_YEAR = 31536000


def aave_apy_from_ray(rate_ray):
    """Aave's currentLiquidityRate is an APR in ray (1e27); the APY compounds it per second."""
    r = rate_ray / 1e27
    return (1.0 + r / SECONDS_PER_YEAR) ** SECONDS_PER_YEAR - 1.0


def comet_apy_from_rate(rate_per_sec_1e18):
    r = rate_per_sec_1e18 / 1e18
    return (1.0 + r) ** SECONDS_PER_YEAR - 1.0


def collect_verify(log, targets=None, dates=None):
    """Independent path for the base yield: read the lending market's own rate on chain (public archive nodes) at
    ~23:00 UTC on sample days and compare with DefiLlama's apyBase for the same pool and day."""
    import drpc
    from term_carry import estimate_block
    uni = read_gz(RAW / 'universe.json.gz')

    def find(project, symbol):
        c = [p for p, u in uni.items() if u.get('project') == project and u.get('chain') == 'Ethereum'
             and str(u.get('symbol') or '').upper() == symbol]
        return max(c, key=lambda p: uni[p]['max_tvl']) if c else None

    targets = targets or [
        ('aave-v3', 'USDC', 'aave', AAVE_V3_POOL, USDC_ETH),
        ('aave-v3', 'USDT', 'aave', AAVE_V3_POOL, USDT_ETH),
        ('sparklend', 'DAI', 'aave', SPARK_POOL, DAI_ETH),
        ('compound-v3', 'USDC', 'comet', COMET_USDC, None),
    ]
    dates = dates or ['2023-03-15', '2023-07-15', '2023-11-15', '2024-03-15', '2024-07-15', '2024-11-15',
                      '2025-03-15', '2025-07-15', '2025-11-15', '2026-03-15', '2026-07-15', '2026-10-05']
    out = []
    for project, sym, kind, contract, asset in targets:
        pid = find(project, sym)
        if pid is None:
            out.append({'project': project, 'symbol': sym, 'error': 'pool not in universe'})
            continue
        f = RAW / 'charts' / ('%s.json.gz' % pid)
        chart = {day_of(r['timestamp']): r for r in (read_gz(f).get('data') or [])} if f.exists() else {}
        for ds in dates:
            d = day_of(ds)
            row = chart.get(d)
            if row is None:
                continue
            ts = d * DAY_S + 23 * 3600
            try:
                blk = estimate_block(ts)
                b = drpc.rpc('eth_getBlockByNumber', [hex(blk), False])
                bts = int(b['timestamp'], 16)
                if kind == 'aave':
                    data = SEL_GET_RESERVE_DATA + asset[2:].lower().rjust(64, '0')
                    res = drpc.rpc('eth_call', [{'to': contract, 'data': data}, hex(blk)])
                    words = [int(res[2 + 64 * i: 2 + 64 * (i + 1)], 16) for i in range(3)]
                    apy = aave_apy_from_ray(words[2])
                else:
                    u = int(drpc.rpc('eth_call', [{'to': contract, 'data': SEL_GET_UTILIZATION}, hex(blk)]), 16)
                    data = SEL_GET_SUPPLY_RATE + hex(u)[2:].rjust(64, '0')
                    rate = int(drpc.rpc('eth_call', [{'to': contract, 'data': data}, hex(blk)]), 16)
                    apy = comet_apy_from_rate(rate)
                out.append({'project': project, 'symbol': sym, 'pool': pid, 'day': ds, 'block': blk,
                            'block_time': dt.datetime.fromtimestamp(bts, UTC).isoformat(), 'onchain_apy_pct': apy * 100,
                            'llama_apyBase_pct': fnum(row.get('apyBase')), 'llama_time': row.get('timestamp')})
                log('verify %s %s %s onchain %.3f llama %s' % (project, sym, ds, apy * 100, row.get('apyBase')))
            except Exception as e:  # noqa: BLE001 - recorded, the check continues
                out.append({'project': project, 'symbol': sym, 'day': ds, 'error': repr(e)[:160]})
    # the check that matters for the backtest: realised 7-day supply return from Aave's liquidityIndex (word 1 of
    # getReserveData) against the sum of DefiLlama's daily apyBase/365 over the same 7 days (what simulate accrues)
    idx_rows = []
    for project, sym, kind, contract, asset in targets:
        if kind != 'aave':
            continue
        pid = find(project, sym)
        f = RAW / 'charts' / ('%s.json.gz' % pid) if pid else None
        if not f or not f.exists():
            continue
        chart = {day_of(r['timestamp']): fnum(r.get('apyBase')) for r in (read_gz(f).get('data') or [])}
        for ds in dates[:-1]:
            d = day_of(ds)
            if any(chart.get(x) is None for x in range(d, d + 7)):
                continue
            try:
                idx = []
                for t in (d, d + 7):
                    blk = estimate_block(t * DAY_S)
                    data = SEL_GET_RESERVE_DATA + asset[2:].lower().rjust(64, '0')
                    res = drpc.rpc('eth_call', [{'to': contract, 'data': data}, hex(blk)])
                    b = drpc.rpc('eth_getBlockByNumber', [hex(blk), False])
                    idx.append((int(res[2 + 64: 2 + 128], 16), int(b['timestamp'], 16)))
                secs = idx[1][1] - idx[0][1]
                realised = idx[1][0] / idx[0][0] - 1.0
                llama = sum(chart[x] for x in range(d, d + 7)) / 100.0 / 365.0
                idx_rows.append({'project': project, 'symbol': sym, 'week_from': ds, 'seconds': secs,
                                 'realised_7d': realised * 7 * DAY_S / secs, 'llama_7d': llama,
                                 'realised_apr_pct': realised * 365 * DAY_S / secs * 100,
                                 'llama_apr_pct': llama * 365 / 7 * 100})
                log('verify-index %s %s %s realised %.3f%% llama %.3f%%' % (project, sym, ds,
                                                                           idx_rows[-1]['realised_apr_pct'],
                                                                           idx_rows[-1]['llama_apr_pct']))
            except Exception as e:  # noqa: BLE001
                idx_rows.append({'project': project, 'symbol': sym, 'week_from': ds, 'error': repr(e)[:160]})
    good = [r for r in idx_rows if 'realised_7d' in r]
    index_check = {'n': len(good), 'rows': idx_rows,
                   'sum_llama_over_sum_realised': (sum(r['llama_7d'] for r in good) / sum(r['realised_7d'] for r in good))
                   if good else None,
                   'mean_diff_apr_pp': (sum(r['llama_apr_pct'] - r['realised_apr_pct'] for r in good) / len(good))
                   if good else None,
                   'mean_abs_diff_apr_pp': (sum(abs(r['llama_apr_pct'] - r['realised_apr_pct']) for r in good) / len(good))
                   if good else None}
    ok = [r for r in out if 'onchain_apy_pct' in r and r.get('llama_apyBase_pct') is not None]
    diffs = [r['llama_apyBase_pct'] - r['onchain_apy_pct'] for r in ok]
    summ = {'index_check': index_check, 'n': len(ok), 'mean_diff_pp': sum(diffs) / len(diffs) if diffs else None,
            'mean_abs_diff_pp': sum(abs(x) for x in diffs) / len(diffs) if diffs else None,
            'max_abs_diff_pp': max((abs(x) for x in diffs), default=None), 'rows': out}
    write_json(RAW / 'verify' / 'verify.json', summ)
    return {k: v for k, v in summ.items() if k != 'rows'}


# ---------------------------------------------------------------------------------------------- render

def pct(x, d=2):
    return '—' if x is None else ('%+.*f%%' % (d, x * 100.0))


def num(x, d=2):
    return '—' if x is None else ('%.*f' % (d, x))


def usd(x):
    if x is None:
        return '—'
    a = abs(x)
    if a >= 1e9:
        return '$%.2fB' % (x / 1e9)
    if a >= 1e6:
        return '$%.1fM' % (x / 1e6)
    if a >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def stat_row(name, st):
    return '| %s | %s | %s | %s | %s | %s | %s |' % (
        name, pct(st.get('ann_excess')), num(st.get('nw_t')), '%s to %s' % (pct(st.get('boot_lo')), pct(st.get('boot_hi'))),
        pct(st.get('ann_return_gross')), pct(st.get('max_drawdown')), st.get('weeks', 0))


def main_render(args):
    A = json.loads((OUT / 'analysis.json').read_text())
    L = ['# incentive_yields — tables (generated %s)' % A['generated'], '',
         'Excess = weekly return minus the savings rate actually paid that week (DSR, then SSR), annualised. '
         't = Newey-West (8 weekly lags); interval = 8-week block bootstrap, 95%%. Split %s.' % A['protocol']['split'], '']
    L += ['## 1. Choose then test (pre-committed grid, $1M, N=5)', '',
          '| universe | chosen | in-sample excess | OOS excess | OOS t | OOS rank | deflated Sharpe (in / OOS) |',
          '|---|---|---|---|---|---|---|']
    for u, ct in A['choose_then_test'].items():
        L.append('| %s | %s | %s | %s | %s | %s of %s | %s / %s |' % (
            u, ct['chosen'], pct(ct['in_sample']['ann_return']), pct(ct['out_of_sample']['ann_return']),
            num(ct['oos_t']), ct['oos_rank'], ct['n_variants'], num(ct['deflated_sharpe_in_sample']),
            num(ct.get('deflated_sharpe_oos'))))
    L += ['', '## 2. Grid (36 variants, $1M, N=5)', '',
          '| variant | in-sample excess | t | OOS excess | t | BH adj p (OOS, q=0.10) | switches/yr |', '|---|---|---|---|---|---|---|']
    for nm, g in A['grid'].items():
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            nm, pct(g['in_sample'].get('ann_excess')), num(g['in_sample'].get('nw_t')),
            pct(g['out_of_sample'].get('ann_excess')), num(g['out_of_sample'].get('nw_t')),
            num(g.get('oos_bh_adj_p'), 3), num(g.get('switches_per_year'), 1)))
    for u, d in A['chosen_detail'].items():
        L += ['', '## 3%s. Chosen variant, %s universe: %s' % ('a' if u == 'all' else 'b', u, d['variant']), '',
              '| run | excess (OOS) | t | 95% interval | gross return | max drawdown | weeks |', '|---|---|---|---|---|---|---|']
        L.append(stat_row('main $1M, in sample', d['main_1m']['in_sample']))
        L.append(stat_row('**main $1M, out of sample**', d['main_1m']['out_of_sample']))
        for k in ('oos_first_half', 'oos_second_half', 'last_52w'):
            if k in d['main_1m']:
                L.append(stat_row('main $1M, %s' % k, d['main_1m'][k]))
        for k, lab in (('capital_100000', '$100k'), ('capital_10000000', '$10M'), ('N1', 'N=1'), ('N10', 'N=10'),
                       ('delay_1d', 'entered 1 day late'), ('delay_7d', 'entered 1 week late'),
                       ('reward_face', 'rewards at accrual price'), ('reward_none', 'rewards ignored'),
                       ('no_losses', 'no hack/depeg/share marking'),
                       ('stress_collapse_0.1', 'each unmarked TVL collapse costs 10%'),
                       ('stress_collapse_0.5', 'each unmarked TVL collapse costs 50%'),
                       ('ex_pendle_notional', 'without Pendle/Notional/Spectra fixed-rate pools'),
                       ('without_capture_rebuilt_pools', 'without pools rebuilt from captures'),
                       ('alive_only_survivorship_biased', 'pools alive today only (biased)')):
            if k in d:
                L.append(stat_row(lab + ' (OOS)', d[k]['out_of_sample']))
        if d.get('capital_curve_oos'):
            L += ['', 'Capital curve (OOS excess, t, $ a year): ' + '; '.join(
                '%s %s (t %s, %s)' % (usd(float(c)), pct(v['ann_excess']), num(v['nw_t']), usd(v['usd_per_year']))
                for c, v in d['capital_curve_oos'].items())]
        L += ['', 'By year ($1M): ' + '; '.join('%s %s (excess %s)' % (y, pct(v['ann_return']), pct(v['ann_excess']))
                                                 for y, v in d['main_1m']['by_year'].items()), '']
        pc = d['main_1m']['pnl_components_usd']
        L.append('P&L components over the whole run ($1M): base %s, rewards at sale %s (imputed price %s), costs %s, '
                 'losses %s; switches a year %s; share of held days in pools dead today %s.' % (
                     usd(pc['base']), usd(pc['reward']), usd(pc['reward_imputed']), usd(-pc['cost']), usd(pc['loss']),
                     num(d['main_1m'].get('switches_per_year'), 1), pct(d.get('days_in_pools_dead_today_share'), 1)))
        oc = d['oos_concentration']
        L.append('OOS excess P&L %s; top-5 pools %s of it: %s.' % (
            usd(oc['total_excess_usd']), pct(oc['top5_share'], 0) if oc['top5_share'] is not None else '—',
            ', '.join('%s %s %s %s' % (r[2], r[3], r[4], usd(r[1])) for r in oc['top5'])))
        L += ['', 'Losses ($1M run): ' + '; '.join('%s n=%d %s' % (t, v['n'], usd(v['usd']))
                                                    for t, v in d['losses_1m']['by_type'].items()), '']
        if d.get('audited_split_1m'):
            L.append('Excess P&L by audit status: ' + '; '.join('%s %d pools %s (losses %s)' % (
                k, v['pools'], usd(v['excess_usd']), usd(v['loss_usd'])) for k, v in d['audited_split_1m'].items()))
            L.append('')
        L.append('Top held: ' + '; '.join('%s %s %s (%d d)' % (r[2], r[3], r[4], r[1]) for r in d['top_held'][:10]))
    AU = A.get('audited')
    if AU:
        L += ['', '## 3c. Audited family (post hoc): the same grid on pools whose return a share price checks', '',
              'Pools with a share-price series: %d (vault shares %d). Vault shares must deliver the claimed apyBase in '
              'their price (shortfalls booked in full); rebasing receipts are marked like the deposit token.' % (
                  AU['pools_with_share_series'], AU['accruing']), '',
              '| universe | chosen | in-sample excess | OOS excess | OOS t | OOS rank |', '|---|---|---|---|---|---|']
        for u, ct in AU['choose_then_test'].items():
            L.append('| %s | %s | %s | %s | %s | %s of %s |' % (
                u, ct['chosen'], pct(ct['in_sample']['ann_return']), pct(ct['out_of_sample']['ann_return']),
                num(ct['oos_t']), ct['oos_rank'], ct['n_variants']))
        L += ['', '| variant (audited) | in-sample excess | t | OOS excess | t | BH adj p |', '|---|---|---|---|---|---|']
        for nm, g in AU['grid'].items():
            L.append('| %s | %s | %s | %s | %s | %s |' % (
                nm, pct(g['in_sample'].get('ann_excess')), num(g['in_sample'].get('nw_t')),
                pct(g['out_of_sample'].get('ann_excess')), num(g['out_of_sample'].get('nw_t')),
                num(g.get('oos_bh_adj_p'), 3)))
        for u, d in AU['detail'].items():
            L += ['', '### audited %s: %s' % (u, d['variant']), '',
                  '| run | excess (OOS) | t | 95% interval | gross return | max drawdown | weeks |', '|---|---|---|---|---|---|---|']
            L.append(stat_row('in sample', d['main_1m']['in_sample']))
            L.append(stat_row('**out of sample**', d['main_1m']['out_of_sample']))
            for k, lab in (('capital_100000', '$100k'), ('capital_10000000', '$10M'), ('delay_1d', '1 day late'),
                           ('delay_7d', '1 week late'), ('no_losses', 'no loss marking'), ('reward_none', 'rewards ignored')):
                if k in d:
                    L.append(stat_row(lab + ' (OOS)', d[k]['out_of_sample']))
            L.append('')
            L.append('Losses: ' + '; '.join('%s n=%d %s' % (t, v['n'], usd(v['usd'])) for t, v in d['losses_1m']['by_type'].items()))
            L.append('Top-5 OOS pools: ' + ', '.join('%s %s %s %s' % (r[2], r[3], r[4], usd(r[1])) for r in d['oos_concentration']['top5']))
    L += ['', '## 4. References ($1M)', '', '| reference | excess (OOS) | t | 95% interval | gross | max DD | weeks |',
          '|---|---|---|---|---|---|---|']
    for k, r in A['references'].items():
        L.append(stat_row(k + ' (in sample)', r['in_sample']))
        L.append(stat_row(k + ' (OOS)', r['out_of_sample']))
    W = A['windows']
    L += ['', '## 5. What you see vs what you get: every eligible pool, non-overlapping 4-week windows (%d)' % W['n_pool_windows'], '',
          'Annualised, equal-weighted across pool-windows, zero size. net = base + rewards at sale + hack + depeg.', '']
    for key, title in (('by_bucket_in_sample', 'displayed excess over savings, in sample'),
                       ('by_bucket_oos', 'displayed excess over savings, out of sample'),
                       ('by_category', 'venue category (DefiLlama)'), ('by_bluechip', 'blue-chip lending vs other'),
                       ('by_reward_share', 'reward share of the displayed yield'),
                       ('by_bucket_audited_vault_share', 'displayed excess, pools whose vault share price audits the yield'),
                       ('by_bucket_unaudited', 'displayed excess, pools with no share price (apyBase taken as given)')):
        L += ['### ' + title, '', '| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | '
              'hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |',
              '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
        for b, v in sorted(W[key].items(), key=lambda kv: -kv[1]['pool_windows']):
            L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                b, v['pool_windows'], v['pools'], pct(v['displayed'], 1), pct(v['realised_base'], 1),
                pct(v['reward_face'], 1), pct(v['reward_at_sale'], 1), pct(v['hack_loss'], 2), pct(v['depeg_loss'], 2),
                pct(v['realised_net'], 1), pct(v['savings'], 1), pct(v['net_excess'], 2), pct(v['p_hack'], 2),
                pct(v['p_depeg'], 2), pct(v['p_collapse'], 2)))
        L.append('')
    NV = A['new_venue']
    L += ['## 6. New-venue premium', '', 'Young chains (first DefiLlama TVL on/after 2022-09-01): ' +
          ', '.join('%s %s' % (c, d) for c, d in NV['young_chains']), '',
          '| chain age | pool-windows | chains | displayed | premium vs old-chain median | reward at sale | losses | net excess |',
          '|---|---|---|---|---|---|---|---|']
    for b in ('m0-1', 'm1-2', 'm2-3', 'm3-6', 'm6-12', 'm12-24', 'm24+'):
        v = NV['curve_by_chain_age'].get(b)
        if v:
            L.append('| %s | %d | %d | %s | %s | %s | %s | %s |' % (
                b, v['pool_windows'], v['chains'], pct(v['displayed'], 1), pct(v['premium_vs_old_chain_median'], 1),
                pct(v['reward_at_sale'], 1), pct(v['hack_loss'] + v['depeg_loss'], 2), pct(v['net_excess'], 2)))
    oc = NV['old_chains'].get('old', {})
    L += ['', 'Old chains: displayed %s, net excess %s (%d pool-windows).' % (
        pct(oc.get('displayed'), 1), pct(oc.get('net_excess'), 2), oc.get('pool_windows', 0)),
        'Half-life of the displayed premium: %s months (A %s pp); of the net excess: %s months.' % (
            num((NV['half_life_displayed_premium'] or {}).get('tau_months'), 1),
            num((NV['half_life_displayed_premium'] or {}).get('A_pp'), 1),
            num((NV['half_life_net_excess'] or {}).get('tau_months'), 1)), '',
        '| new-chain rule ($1M, N=5, weekly) | excess (OOS) | t | 95% interval | gross | max DD | weeks |', '|---|---|---|---|---|---|---|']
    for k, r in NV['rules'].items():
        L.append(stat_row(k + ' in sample', r['in_sample']))
        L.append(stat_row(k + ' OOS', r['out_of_sample']))
        L.append('| %s: excess when invested %s in sample (%s wk), %s out of sample (%s wk, t %s); chains %s; '
                 'active weeks %s; losses %s | | | | | | |' % (
            k, pct(r['in_sample_active']['ann_excess_when_active']), r['in_sample_active']['weeks'],
            pct(r['out_of_sample_active']['ann_excess_when_active']), r['out_of_sample_active']['weeks'],
            num(r['out_of_sample_active']['nw_t']), ', '.join(r['chains_entered']), r['active_weeks'],
            '; '.join('%s n=%d %s' % (t, v['n'], usd(v['usd'])) for t, v in r['losses'].items())))
    C = A['capacity']
    L += ['', '## 7. Capacity at %s (marginal yield falls to SSR + 1pp = %s)' % (C['decision_day'], pct(C['marginal_hurdle'])), '']
    for k in ('chosen_all', 'chosen_bluechip'):
        if k in C:
            L.append('%s: sum %s — ' % (k, usd(C[k]['sum_x_star'])) + '; '.join(
                '%s %s %s TVL %s yield %s X* %s' % (c['project'], c['chain'], c['symbol'], usd(c['tvl']),
                                                   pct(c['yield_eff'], 1), usd(c['x_star'])) for c in C[k]['picks']))
    for k in ('universe_all', 'universe_bluechip'):
        L.append('%s: %d eligible, %d above the hurdle, sum %s; largest: %s' % (
            k, C[k]['eligible'], C[k]['above_hurdle'], usd(C[k]['sum_x_star']),
            '; '.join('%s %s %s %s' % (c['project'], c['chain'], c['symbol'], usd(c['x_star'])) for c in C[k]['top'][:8])))
    S = A['incentive_spend_now']
    L += ['', '## 8. Incentive spend now (sum tvlUsd x apyReward, %s)' % S['filters'], '',
          'Total %s a year (raw %s), %d pools paying; stable %s, volatile %s; USD-stable single-exposure %s on TVL %s.' % (
              usd(S['total_clean_usd']), usd(S['total_raw_usd']), S['pools_paying'],
              usd(S['stable_vs_volatile'].get('stable')), usd(S['stable_vs_volatile'].get('volatile')),
              usd((S.get('usd_stable_single') or {}).get('usd')), usd((S.get('usd_stable_single') or {}).get('tvl'))), '',
          'Top chains: ' + '; '.join('%s %s' % (c, usd(v)) for c, v in S['top_chains'][:15]), '',
          'Top projects: ' + '; '.join('%s %s' % (c, usd(v)) for c, v in S['top_projects'][:15]), '',
          'Through the captures (clean total / stable / volatile / USD-stable single): ' + '; '.join(
              '%s %s/%s/%s/%s' % (r[0], usd(r[1]), usd(r[2]), usd(r[3]), usd(r[4]))
              for r in A['incentive_spend_history']['rows'][::8])]
    SV = A['survivorship']
    L += ['', '## 9. Survivorship', '', json.dumps({k: v for k, v in SV.items() if k != 'bound_sample'}, default=str)[:1500]]
    if SV.get('bound_sample'):
        bs = SV['bound_sample']
        L.append('distinctID sample: %s' % json.dumps({k: v for k, v in bs.items() if k != 'rows'}))
    if A.get('verify'):
        V = A['verify']
        L += ['', '## 10. Independent check: on-chain supply rate vs DefiLlama apyBase', '',
              'n %s, mean difference %s pp, mean |difference| %s pp, max |difference| %s pp' % (
                  V['n'], num(V['mean_diff_pp'], 3), num(V['mean_abs_diff_pp'], 3), num(V['max_abs_diff_pp'], 3)), '',
              '| pool | day | on-chain APY | DefiLlama apyBase |', '|---|---|---|---|']
        for r in V['rows']:
            if 'onchain_apy_pct' in r:
                L.append('| %s %s | %s | %.3f%% | %s%% |' % (r['project'], r['symbol'], r['day'], r['onchain_apy_pct'],
                                                            num(r['llama_apyBase_pct'], 3)))
    (OUT / 'tables.md').write_text('\n'.join(L) + '\n')
    print('tables.md written (%d lines)' % len(L))


# ---------------------------------------------------------------------------------------------- CLI

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--parts', default='wayback,universe,charts,losses,chains,coins')
    c.add_argument('--limit', type=int, default=None)
    c.add_argument('--spacing', type=float, default=0.4, help='seconds between DefiLlama request starts')
    sub.add_parser('analyze')
    sub.add_parser('render')
    args = ap.parse_args()
    if args.cmd == 'collect':
        main_collect(args)
    elif args.cmd == 'analyze':
        main_analyze(args)
    elif args.cmd == 'render':
        main_render(args)


if __name__ == '__main__':
    main()
