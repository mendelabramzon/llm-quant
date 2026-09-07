#!/usr/bin/env python3
"""Analyse a window collected by `orbit_collect.py` (Arbitrum Nitro / Orbit chain, e.g. Robinhood Chain).

One streaming pass over `data/*.jsonl.gz` builds `analysis.json`; `--md` also renders deterministic tables into
`tables.md`. Everything is offline except (a) pool-key resolution for the most active Uniswap v3/v4 pools (eth_call,
cached in `pools.json`) and (b) name lookups for the top addresses, selectors and event topics (Blockscout + OpenChain,
cached in `names.json` / `selectors.json`); both are skipped with `--offline`.

    uv run python scripts/orbit_scan.py --dir research/2026-09-07/robinhood_10h --md

Memory: a 10-hour Orbit window is ~6M transactions and ~3M kept logs, so nothing per-transaction is retained. Per-address
detail (sender counters, selectors) is only kept for targets after 50 transactions and senders after 20; swap volumes
are accumulated per pool in USDG and in WETH (converted at the end with the per-bucket on-chain ETH price); pool keys
come from `pools.json` (pre-resolved or resolved after the pass for the most active pools) and from in-window
Initialize / PoolCreated events, and a light second pass prices swaps in pools resolved after the first pass.

Conventions: "user transactions" exclude Nitro's internal ArbOS transactions (type 0x6a, one per block) and L1-initiated
deposits (0x64, 0x68, 0x69). Fees are `gasUsed x effectiveGasPrice` from receipts; on this chain the L1 component
(`gasUsedForL1`) is zero and the effective price equals the base fee. USD values use USDG = $1, WETH at the on-chain
WETH/USDG VWAP for the 15-minute bucket, and a stock token at Blockscout's rate from `stock_tokens.json` (falling back
to its own USDG pool when it traded).
"""
import argparse
import collections
import glob
import gzip
import heapq
import json
import statistics
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
RPCS = ['https://robinhood-rpc.publicnode.com', 'https://robinhood.rpc.blxrbdn.com', 'https://rpc-robinhood.blockmachine.io', 'https://rpc.mainnet.chain.robinhood.com']

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
V3SWAP = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
V4SWAP = '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f'
V2SWAP = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
V3POOL = '0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'
V4INIT = '0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438'
V2PAIR = '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'
V3MINT = '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde'
V3BURN = '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c'
V4MODIFY = '0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec'
USEROP = '0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f'
L2TOL1 = '0x3e7aafa77dbf186b7fd488006beff893744caa3c4f6f299e8a709fa2087374fc'
WDEP = '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'
WWD = '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'
ORACLE_PAUSED = '0xe28b7053f432ae5400c6168140cbe15638399715519a0a39b16b505fb9fc9d9a'
ORACLE_UNPAUSED = '0xa274116fec684497d55e11cc9516edaa8d206c8b5f84c4603e32572c37f8e6dd'
UIMULT = '0x2205df4534432b2f60654a3fdb48737ffdaf3e9edb1a498bd985bc026b15b055'
BLOCKED = '0x75e91ce73c1d3352d8dd3610443539cd33dfe13b1de8f8caae54ec26dd0dc9cb'
SCALED_UI = '0x37e7f0db430edc9dd31bc66f25f8449353aa0818f503b906747dd8f286cd3802'
APPROVAL = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'
ZERO32 = '0x' + '0' * 64
ZERO_ADDR = '0x' + '0' * 40

USDG = '0x5fc5360d0400a0fd4f2af552add042d716f1d168'
WETH = '0x0bd7d308f8e1639fab988df18a8011f41eacad73'
POOL_MANAGER = '0x8366a39cc670b4001a1121b8f6a443a643e40951'
POSM = '0x58daec3116aae6d93017baaea7749052e8a04fa7'
ENTRYPOINTS = {'0x4337084d9e255ff0702461cf8895ce9e3b5ff108': 'v0.8', '0x0000000071727de22e5e9d8baf0edac6f37da032': 'v0.7'}
ARBSYS = '0x0000000000000000000000000000000000000064'
FEE_ROUTER = '0x65050a9b7e5075a2ba5ced7b1b64ee66262c40dc'
FEE_COLLECTED = '0x205442d6'
FEE_DISTRIBUTORS = ('0xbc5c3a7adecf54d34169fd90dbd1b7d3142df067', '0x5a2b80a9b7effc06129bd5462d77bc20a8a59be7', '0x92433c650785397386a0cc347ec2489718e45307')
FOCUS = {'0x51c72848c68a965f66fa7a88855f9f7784502a7f': 'market-maker venue 0x51c72848', '0x8f10b468b06c6fd214b65f87778827f7d113f996': 'aggregator executor 0x8f10b468', '0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f': 'RelayRouterV3',
         '0xccc88a9d1b4ed6b0eaba998850414b24f1c315be': 'RelayApprovalProxyV3', '0x4cd00e387622c35bddb9b4c962c136462338bc31': 'RelayDepository', FEE_ROUTER: 'fee router 0x65050a9b', POOL_MANAGER: 'Uniswap v4 PoolManager',
         '0x9d53d5e3bd5e8d4cbfa6db1ca238aea02e651010': 'Morpho Blue', '0xbeeff0fb1dc19344a87b8479dab60a2e16160737': 'ethenaUSDG VaultV2', '0xbeeff033f34c046626b8d0a041844c5d1a5409dd': 'steakUSDG'}
INTERNAL_TYPES = {'0x6a'}
DEPOSIT_TYPES = {'0x64', '0x69', '0x68', '0x65', '0x66'}
CAP = 3000
TO_DETAIL_AT = 50
FROM_DETAIL_AT = 20


def hx(v):
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


def s256(word):
    v = int(word, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def s128(word):
    v = int(word, 16) & ((1 << 128) - 1)
    return v - (1 << 128) if v >= (1 << 127) else v


def words(data):
    d = data[2:] if data.startswith('0x') else data
    return [d[i:i + 64] for i in range(0, len(d), 64)]


def addr(topic):
    return '0x' + topic[-40:]


def bucket_of(ts, size):
    return ts - ts % size


def ahash(a):
    return int(a[2:18], 16)


class Capped:
    __slots__ = ('s', 'n')

    def __init__(self):
        self.s = set()
        self.n = 0

    def add(self, x):
        self.n += 1
        if len(self.s) < CAP:
            self.s.add(x)

    def count(self):
        return len(self.s) if len(self.s) < CAP else '%d+' % CAP


def rpc_call(to, data):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [{'to': to, 'data': data}, 'latest']}).encode()
    last = None
    for ep in RPCS:
        try:
            req = urllib.request.Request(ep, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read())
            if 'result' in d:
                return d['result']
            last = d.get('error')
        except Exception as e:
            last = str(e)[:100]
    raise RuntimeError('eth_call failed: %s' % last)


def resolve_pools(v3_pools, v4_ids, cache_path, cache=None):
    cache = cache if cache is not None else (json.loads(cache_path.read_text()) if cache_path.exists() else {})
    n = 0
    for p in v3_pools:
        if p in cache and not cache[p].get('error'):
            continue
        try:
            t0 = addr(rpc_call(p, '0x0dfe1681'))
            t1 = addr(rpc_call(p, '0xd21220a7'))
            fee = hx(rpc_call(p, '0xddca3f43'))
            cache[p] = {'kind': 'v3', 'token0': t0, 'token1': t1, 'fee': fee}
        except Exception as e:
            cache[p] = {'kind': 'v3', 'error': str(e)[:80]}
        n += 1
        if n % 100 == 0:
            cache_path.write_text(json.dumps(cache, indent=0, sort_keys=True))
    for pid in v4_ids:
        if pid in cache and not cache[pid].get('error'):
            continue
        try:
            r = rpc_call(POSM, '0x' + '5a91ea92' + pid[2:52].ljust(64, '0'))  # poolKeys(bytes25)
            w = words(r)
            if len(w) >= 5 and (int(w[0], 16) or int(w[1], 16)):
                cache[pid] = {'kind': 'v4', 'token0': addr(w[0]), 'token1': addr(w[1]), 'fee': int(w[2], 16), 'tickSpacing': s256(w[3]), 'hooks': addr(w[4])}
            else:
                cache[pid] = {'kind': 'v4', 'unresolved': True}
        except Exception as e:
            cache[pid] = {'kind': 'v4', 'error': str(e)[:80]}
        n += 1
        if n % 100 == 0:
            cache_path.write_text(json.dumps(cache, indent=0, sort_keys=True))
    cache_path.write_text(json.dumps(cache, indent=0, sort_keys=True))
    return cache


def bs_names(addresses, cache_path):
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    for a in addresses:
        if a in cache:
            continue
        try:
            req = urllib.request.Request('https://robinhoodchain.blockscout.com/api/v2/addresses/' + a, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read())
            tok = d.get('token') or {}
            impl = [(i.get('name'), (i.get('address') or i.get('address_hash') or '')) for i in (d.get('implementations') or [])]
            cache[a] = {'name': d.get('name'), 'contract': bool(d.get('is_contract')), 'verified': bool(d.get('is_verified')), 'token': tok.get('symbol') if tok else None, 'token_name': tok.get('name') if tok else None, 'impl': impl[:3], 'creator': d.get('creator_address_hash')}
        except Exception as e:
            cache[a] = {'name': None, 'error': str(e)[:60]}
        time.sleep(0.12)
    cache_path.write_text(json.dumps(cache, indent=0, sort_keys=True))
    return cache


def openchain(kind, keys, cache_path):
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    prefix = '' if kind == 'function' else 'event:'
    todo = [k for k in keys if k and (prefix + k) not in cache]
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        try:
            req = urllib.request.Request('https://api.openchain.xyz/signature-database/v1/lookup?%s=%s&filter=true' % (kind, ','.join(chunk)), headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                res = (json.load(r).get('result') or {}).get(kind) or {}
            for k in chunk:
                names = [x['name'] for x in (res.get(k) or [])]
                cache[prefix + k] = names[0] if names else None
        except Exception:
            for k in chunk:
                cache.setdefault(prefix + k, None)
    cache_path.write_text(json.dumps(cache, indent=0, sort_keys=True))
    return cache


def label(a, names, stock_syms):
    if not a:
        return ''
    if a in stock_syms:
        return stock_syms[a] + ' stock token'
    if a in FOCUS:
        return FOCUS[a]
    n = names.get(a) or {}
    parts = []
    if n.get('token'):
        parts.append('token ' + str(n['token']))
    if n.get('name'):
        parts.append(n['name'])
    if n.get('impl') and n['impl'][0][0]:
        parts.append('impl ' + n['impl'][0][0])
    if not parts and n.get('contract') is False:
        parts.append('EOA')
    return ' / '.join(parts)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dir', required=True)
    p.add_argument('--bucket', type=int, default=15, help='series bucket in minutes')
    p.add_argument('--offline', action='store_true')
    p.add_argument('--md', action='store_true')
    p.add_argument('--v4-pools', type=int, default=1000, help='resolve this many most-active v4 pools via PositionManager.poolKeys')
    p.add_argument('--v3-pools', type=int, default=300)
    a = p.parse_args()
    d = Path(a.dir)
    manifest = json.loads((d / 'manifest.json').read_text())
    stocks = {}
    sp = d / 'stock_tokens.json'
    if sp.exists():
        for t in json.loads(sp.read_text()):
            ad = (t.get('address_hash') or t.get('address') or '').lower()
            if ad:
                stocks[ad] = {'symbol': t.get('symbol'), 'name': t.get('name'), 'px': float(t['exchange_rate']) if t.get('exchange_rate') else None}
    stock_syms = {k: v['symbol'] for k, v in stocks.items()}
    B = a.bucket * 60
    pools_path = d / 'pools.json'
    pools = json.loads(pools_path.read_text()) if pools_path.exists() else {}
    v3_pool_set = {k for k, v in pools.items() if v.get('kind') == 'v3' and v.get('token0')}

    def tokname(x):
        if x in stocks:
            return stocks[x]['symbol']
        if x == USDG:
            return 'USDG'
        if x == WETH:
            return 'WETH'
        return None

    def run_pass(pools, first_pass, skip_pools=frozenset()):
        """One streaming pass. The first pass builds everything; the second only re-prices swaps in pools not priced before."""
        S = {}
        S['blocks'] = 0
        S['first_ts'] = S['last_ts'] = S['first_n'] = S['last_n'] = None
        S['gas_total'] = 0
        S['tx_total'] = S['tx_user'] = 0
        S['fees_wei'] = 0
        S['basefees'] = []
        series = collections.defaultdict(lambda: collections.defaultdict(float))
        series_senders = collections.defaultdict(set)
        series_bf = collections.defaultdict(list)
        types = collections.Counter()
        type_gas = collections.Counter()
        type_fee = collections.Counter()
        to_count = collections.Counter()
        to_stats = {}
        from_count = collections.Counter()
        from_stats = {}
        sel_stats = collections.Counter()
        sel_fee = collections.Counter()
        sel_to = collections.defaultdict(collections.Counter)
        senders = set()
        failed = 0
        failed_fees = 0
        bidders = []
        bid_count = 0
        bid_senders = set()
        bid_extra_paid = 0
        bid_over_base = 0
        creations = []
        creators = collections.Counter()
        deposits = {'count': 0, 'eth': 0.0, 'by_type': collections.Counter()}
        seven02 = {'txs': 0, 'senders': set(), 'targets': collections.Counter()}
        top_value = []
        value_eth_total = 0.0
        stock_ev = collections.defaultdict(lambda: {'transfers': 0, 'mints': 0, 'burns': 0, 'mint_amt': 0, 'burn_amt': 0, 'vol': 0, 'from': Capped(), 'to': Capped(), 'max': (0, None), 'dex': 0})
        stock_addrs = set()
        stock_hourly = collections.defaultdict(collections.Counter)
        stock_admin = []
        mint_senders = collections.Counter()
        usdg = {'transfers': 0, 'vol': 0, 'mints': 0, 'mint_amt': 0, 'burns': 0, 'burn_amt': 0, 'addrs': set(), 'top': []}
        usdg_flows = collections.Counter()
        weth = {'deposits': 0, 'dep_eth': 0.0, 'withdrawals': 0, 'wd_eth': 0.0, 'transfers': 0}
        pool_swaps = collections.Counter()
        pool_traders = {}
        pool_usdg = collections.Counter()
        pool_weth = collections.defaultdict(collections.Counter)
        pool_unpriced = collections.Counter()
        eth_px = collections.defaultdict(lambda: [0.0, 0.0])
        stock_px_last = {}
        stock_px_first = {}
        stock_px_n = collections.Counter()
        stock_swap_n = collections.Counter()
        stock_swap_usdg = collections.Counter()
        stock_swap_weth = collections.defaultdict(collections.Counter)
        bucket_usdg = collections.Counter()
        bucket_weth = collections.Counter()
        v2_count = 0
        new_v3 = []
        new_v4 = []
        new_v2 = 0
        liq = collections.Counter()
        userops = {'count': 0, 'success': 0, 'senders': set(), 'paymasters': collections.Counter(), 'bundlers': collections.Counter(), 'entrypoint': collections.Counter()}
        l2l1 = []
        nft_transfers = 0
        nft_mints = collections.Counter()
        fee_dist = []
        router_fees = collections.defaultdict(lambda: [0, 0])
        router_fee_rcpt = collections.Counter()
        focus = {f: collections.defaultdict(lambda: {'in': 0, 'out': 0, 'n_in': 0, 'n_out': 0, 'cp': Capped()}) for f in FOCUS}
        ta_tot = {}
        ea_tot = collections.Counter()
        tx_ts = {}
        tx_from = {}
        v3_active = set(v3_pool_set)
        files = sorted(glob.glob(str(d / 'data' / '*.jsonl.gz')), key=lambda x: int(Path(x).name.split('.')[0]))
        for fi, fp in enumerate(files):
            cur_ts = None
            with gzip.open(fp, 'rt') as f:
                for line in f:
                    t = line[6]
                    if t == 'x' and not first_pass:
                        continue
                    r = json.loads(line)
                    if t == 'b':
                        cur_ts = r['ts']
                        if not first_pass:
                            continue
                        S['blocks'] += 1
                        if S['first_ts'] is None:
                            S['first_ts'], S['first_n'] = r['ts'], r['n']
                        S['last_ts'], S['last_n'] = r['ts'], r['n']
                        S['gas_total'] += r['gu']
                        S['basefees'].append(r['bf'])
                        bk = bucket_of(r['ts'], B)
                        series[bk]['blocks'] += 1
                        series[bk]['gas'] += r['gu']
                        series_bf[bk].append(r['bf'])
                        S['tx_total'] += r['tx']
                    elif t == 'x':
                        ty = r['ty']
                        types[ty] += 1
                        type_gas[ty] += r['gu']
                        fee = r['gu'] * r['egp']
                        type_fee[ty] += fee
                        tx_ts[r['h']] = cur_ts
                        tx_from[r['h']] = r['f']
                        bk = bucket_of(cur_ts, B)
                        if ty in DEPOSIT_TYPES:
                            deposits['count'] += 1
                            deposits['by_type'][ty] += 1
                            if ty == '0x64':
                                deposits['eth'] += hx(r['v']) / 1e18
                            series[bk]['deposits'] += 1
                        if ty in INTERNAL_TYPES or ty in DEPOSIT_TYPES:
                            continue
                        S['tx_user'] += 1
                        S['fees_wei'] += fee
                        series[bk]['txs'] += 1
                        series[bk]['fees'] += fee
                        series_senders[bk].add(ahash(r['f']))
                        senders.add(r['f'])
                        ok = r['st'] == 1
                        if not ok:
                            failed += 1
                            failed_fees += fee
                            series[bk]['failed'] += 1
                        if ty == '0x4':
                            seven02['txs'] += 1
                            seven02['senders'].add(r['f'])
                            seven02['targets'][r['to']] += 1
                            series[bk]['eip7702'] += 1
                        to = r['to'] or ('CREATE:' + (r['ca'] or '?'))
                        to_count[to] += 1
                        st = to_stats.get(to)
                        if st is None and to_count[to] >= TO_DETAIL_AT:
                            st = to_stats[to] = {'txs': 0, 'gas': 0, 'fees': 0, 'failed': 0, 'senders': Capped(), 'sels': collections.Counter(), 'value': 0, 'sc': collections.Counter()}
                        if st is not None:
                            st['txs'] += 1
                            st['gas'] += r['gu']
                            st['fees'] += fee
                            st['failed'] += not ok
                            st['senders'].add(r['f'])
                            if len(st['sc']) < 20000 or r['f'] in st['sc']:
                                st['sc'][r['f']] += 1
                            st['sels'][r['s']] += 1
                            st['value'] += hx(r['v'])
                        from_count[r['f']] += 1
                        fs = from_stats.get(r['f'])
                        if fs is None and from_count[r['f']] >= FROM_DETAIL_AT:
                            fs = from_stats[r['f']] = {'txs': 0, 'gas': 0, 'fees': 0, 'failed': 0, 'targets': collections.Counter(), 'first_nonce': r['nc'], 'last_nonce': r['nc']}
                        if fs is not None:
                            fs['txs'] += 1
                            fs['gas'] += r['gu']
                            fs['fees'] += fee
                            fs['failed'] += not ok
                            if len(fs['targets']) < 200 or r['to'] in fs['targets']:
                                fs['targets'][r['to']] += 1
                            fs['first_nonce'] = min(fs['first_nonce'], r['nc'])
                            fs['last_nonce'] = max(fs['last_nonce'], r['nc'])
                        sel_stats[r['s']] += 1
                        sel_fee[r['s']] += fee
                        if len(sel_to[r['s']]) < 50 or r['to'] in sel_to[r['s']]:
                            sel_to[r['s']][r['to']] += 1
                        v = hx(r['v'])
                        if v:
                            value_eth_total += v / 1e18
                            if v >= 5 * 10 ** 18:
                                top_value.append((v / 1e18, r['h'], r['f'], r['to'], cur_ts))
                        bf = series_bf[bk][-1] if series_bf[bk] else 0
                        if bf and r['gp'] >= 3 * bf:
                            bid_count += 1
                            bid_senders.add(r['f'])
                            bid_extra_paid += max(0, r['egp'] - bf) * r['gu']
                            bid_over_base += (r['egp'] > bf)
                            if r['gp'] >= 20 * bf:
                                item = (r['gp'] / 1e9, bf / 1e9, r['h'], r['f'], r['to'], r['s'], r['st'], cur_ts)
                                if len(bidders) < 60:
                                    heapq.heappush(bidders, item)
                                elif item > bidders[0]:
                                    heapq.heapreplace(bidders, item)
                        if r['ca']:
                            creations.append((r['n'], cur_ts, r['f'], r['ca'], r['h']))
                            creators[r['f']] += 1
                            series[bk]['creations'] += 1
                    elif t == 'l':
                        tp = r['tp']
                        t0 = tp[0] if tp else None
                        ad = r['a']
                        ts = tx_ts.get(r['h'], cur_ts) if first_pass else cur_ts
                        bk = bucket_of(ts, B)
                        if t0 == V3SWAP:
                            w = words(r['d'])
                            a0, a1, sq = s256(w[0]), s256(w[1]), int(w[2], 16)
                            pool = ad
                            v3_active.add(ad)
                            kind = 'v3'
                        elif t0 == V4SWAP:
                            w = words(r['d'])
                            a0, a1, sq = s128(w[0]), s128(w[1]), int(w[2], 16)
                            pool = tp[1]
                            kind = 'v4'
                        else:
                            pool = None
                        if pool is not None:
                            if first_pass:
                                pool_swaps[pool] += 1
                                series[bk]['swaps'] += 1
                                if pool_swaps[pool] >= 20:
                                    pt = pool_traders.get(pool)
                                    if pt is None:
                                        pt = pool_traders[pool] = Capped()
                                    pt.add(addr(tp[1]) if kind == 'v3' else addr(tp[2]))
                            elif pool in skip_pools:
                                continue
                            pk = pools.get(pool) or {}
                            t0k, t1k = pk.get('token0'), pk.get('token1')
                            if not t0k:
                                if first_pass:
                                    pool_unpriced[pool] += 1
                                continue
                            if t0k == USDG or t1k == USDG:
                                u = abs(a0 if t0k == USDG else a1) / 1e6
                                pool_usdg[pool] += u
                                bucket_usdg[bk] += u
                                other = t1k if t0k == USDG else t0k
                                if other == WETH:
                                    w_ = abs(a1 if t0k == USDG else a0) / 1e18
                                    if u > 20 and w_ > 0.005:
                                        eth_px[bk][0] += u
                                        eth_px[bk][1] += w_
                                if other in stocks:
                                    stock_swap_n[other] += 1
                                    stock_swap_usdg[other] += u
                                    if sq:
                                        ratio = (sq / 2 ** 96) ** 2
                                        px = ratio * 1e12 if t0k == other else (1 / (ratio * 1e-12) if ratio else None)
                                        if px:
                                            stock_px_last[other] = px
                                            stock_px_first.setdefault(other, px)
                                            stock_px_n[other] += 1
                            elif t0k == WETH or t1k == WETH:
                                w_ = abs(a0 if t0k == WETH else a1) / 1e18
                                pool_weth[pool][bk] += w_
                                bucket_weth[bk] += w_
                                other = t1k if t0k == WETH else t0k
                                if other in stocks:
                                    stock_swap_n[other] += 1
                                    stock_swap_weth[other][bk] += w_
                            elif first_pass:
                                pool_unpriced[pool] += 1
                            continue
                        if not first_pass:
                            continue
                        if t0 == TRANSFER and len(tp) == 3:
                            fr, to_, val = addr(tp[1]), addr(tp[2]), hx(r['d'][:66]) if len(r['d']) >= 66 else 0
                            if fr in focus or to_ in focus:
                                tk = stock_syms.get(ad) or ('USDG' if ad == USDG else 'WETH' if ad == WETH else ad)
                                if to_ in focus:
                                    fx = focus[to_][tk]
                                    fx['in'] += val
                                    fx['n_in'] += 1
                                    fx['cp'].add(fr)
                                if fr in focus:
                                    fx = focus[fr][tk]
                                    fx['out'] += val
                                    fx['n_out'] += 1
                                    fx['cp'].add(to_)
                            if ad in stocks:
                                se = stock_ev[ad]
                                se['transfers'] += 1
                                se['vol'] += val
                                se['from'].add(fr)
                                se['to'].add(to_)
                                stock_addrs.add(ahash(fr))
                                stock_addrs.add(ahash(to_))
                                if val > se['max'][0]:
                                    se['max'] = (val, r['h'])
                                hb = bucket_of(ts, 3600)
                                pxb = stocks[ad]['px'] or 0
                                if fr == ZERO_ADDR:
                                    se['mints'] += 1
                                    se['mint_amt'] += val
                                    mint_senders[tx_from.get(r['h'])] += 1
                                    stock_hourly[hb]['mints'] += 1
                                    stock_hourly[hb]['mint_usd'] += val / 1e18 * pxb
                                elif to_ == ZERO_ADDR:
                                    se['burns'] += 1
                                    se['burn_amt'] += val
                                    stock_hourly[hb]['burns'] += 1
                                    stock_hourly[hb]['burn_usd'] += val / 1e18 * pxb
                                else:
                                    stock_hourly[hb]['transfers'] += 1
                                    stock_hourly[hb]['transfer_usd'] += val / 1e18 * pxb
                                if fr == POOL_MANAGER or to_ == POOL_MANAGER or fr in v3_active or to_ in v3_active:
                                    se['dex'] += 1
                                series[bk]['stock_transfers'] += 1
                            elif ad == USDG:
                                usdg['transfers'] += 1
                                usdg['vol'] += val
                                usdg['addrs'].add(ahash(fr))
                                usdg['addrs'].add(ahash(to_))
                                series[bk]['usdg_vol'] += val / 1e6
                                if fr == ZERO_ADDR:
                                    usdg['mints'] += 1
                                    usdg['mint_amt'] += val
                                if to_ == ZERO_ADDR:
                                    usdg['burns'] += 1
                                    usdg['burn_amt'] += val
                                usdg_flows[to_] += val
                                usdg_flows[fr] -= val
                                if val >= 100_000 * 10 ** 6:
                                    usdg['top'].append((val / 1e6, r['h'], fr, to_, ts))
                            elif ad == WETH:
                                weth['transfers'] += 1
                        elif t0 == TRANSFER and len(tp) == 4:
                            nft_transfers += 1
                            if tp[1] == ZERO32:
                                nft_mints[ad] += 1
                        elif t0 == V2SWAP:
                            v2_count += 1
                            series[bk]['swaps'] += 1
                        elif t0 == V3POOL:
                            w = words(r['d'])
                            pl = {'token0': addr(tp[1]), 'token1': addr(tp[2]), 'fee': hx(tp[3]), 'pool': addr(w[1]) if len(w) > 1 else None, 'block': r['n'], 'ts': ts}
                            new_v3.append(pl)
                            if pl['pool']:
                                pools.setdefault(pl['pool'], {'kind': 'v3', 'token0': pl['token0'], 'token1': pl['token1'], 'fee': pl['fee']})
                                v3_active.add(pl['pool'])
                        elif t0 == V4INIT:
                            w = words(r['d'])
                            pl = {'id': tp[1], 'token0': addr(tp[2]), 'token1': addr(tp[3]), 'fee': int(w[0], 16), 'tickSpacing': s256(w[1]), 'hooks': addr(w[2]), 'block': r['n'], 'ts': ts, 'tx': r['h'], 'creator': tx_from.get(r['h'])}
                            new_v4.append(pl)
                            pools.setdefault(pl['id'], {'kind': 'v4', 'token0': pl['token0'], 'token1': pl['token1'], 'fee': pl['fee'], 'tickSpacing': pl['tickSpacing'], 'hooks': pl['hooks']})
                            series[bk]['new_pools'] += 1
                        elif t0 == V2PAIR:
                            new_v2 += 1
                        elif t0 in (V3MINT, V3BURN, V4MODIFY):
                            liq[{V3MINT: 'v3_mint', V3BURN: 'v3_burn', V4MODIFY: 'v4_modify'}[t0]] += 1
                        elif t0 == USEROP:
                            userops['count'] += 1
                            w = words(r['d'])
                            okop = int(w[1], 16) == 1 if len(w) > 1 else None
                            userops['success'] += bool(okop)
                            userops['senders'].add(ahash(addr(tp[2])))
                            userops['paymasters'][addr(tp[3])] += 1
                            userops['bundlers'][tx_from.get(r['h'])] += 1
                            userops['entrypoint'][ENTRYPOINTS.get(ad, ad)] += 1
                            series[bk]['userops'] += 1
                        elif t0 == L2TOL1:
                            w = words(r['d'])
                            callvalue = int(w[4], 16) if len(w) > 4 else 0
                            l2l1.append({'caller': addr(w[0]), 'destination': addr(tp[1]), 'eth': callvalue / 1e18, 'tx': r['h'], 'ts': ts, 'data_len': (int(w[6], 16) if len(w) > 6 else 0)})
                        elif t0 == WDEP and ad == WETH:
                            weth['deposits'] += 1
                            weth['dep_eth'] += hx(r['d'][:66]) / 1e18
                        elif t0 == WWD and ad == WETH:
                            weth['withdrawals'] += 1
                            weth['wd_eth'] += hx(r['d'][:66]) / 1e18
                        elif ad == FEE_ROUTER and t0 and t0[:10] == FEE_COLLECTED:
                            w = words(r['d'])
                            k = addr(tp[1]) if len(tp) > 1 else '?'
                            router_fees[k][0] += 1
                            router_fees[k][1] += int(w[0], 16) if w else 0
                            if len(tp) > 2:
                                router_fee_rcpt[addr(tp[2])] += 1
                        elif ad in stocks and t0 not in (SCALED_UI, APPROVAL):
                            if len(stock_admin) < 500:
                                stock_admin.append({'token': stock_syms.get(ad, ad), 'topic': t0, 'block': r['n'], 'ts': ts, 'tx': r['h'], 'topics': tp[1:], 'data': r['d'][:200]})
                        elif ad in FEE_DISTRIBUTORS:
                            if len(fee_dist) < 200:
                                fee_dist.append({'contract': ad, 'topic': t0, 'block': r['n'], 'ts': ts, 'tx': r['h'], 'topics': tp[1:], 'data': r['d'][:200]})
                    elif t == 't' and first_pass and line.startswith('{"t":"ta"'):
                        for tok, v in r['v'].items():
                            agg = ta_tot.get(tok)
                            if agg is None:
                                agg = ta_tot[tok] = [0, 0, 0, 0]
                            agg[0] += v[0]
                            agg[1] += v[1]
                            agg[2] += v[2]
                            agg[3] = max(agg[3], v[3])
                    elif t == 'e' and first_pass:
                        ea_tot.update(r['v'])
            tx_ts.clear()
            tx_from.clear()
            if first_pass and (fi + 1) % 500 == 0:
                print('pass1 %d/%d files' % (fi + 1, len(files)), flush=True)
        return dict(S=S, series=series, series_senders=series_senders, series_bf=series_bf, types=types, type_gas=type_gas, type_fee=type_fee, to_count=to_count, to_stats=to_stats, from_count=from_count, from_stats=from_stats,
                    sel_stats=sel_stats, sel_fee=sel_fee, sel_to=sel_to, senders=senders, failed=failed, failed_fees=failed_fees, bidders=bidders, bid_count=bid_count, bid_senders=bid_senders, bid_extra_paid=bid_extra_paid, bid_over_base=bid_over_base,
                    creations=creations, creators=creators, deposits=deposits, seven02=seven02, top_value=top_value, value_eth_total=value_eth_total, stock_ev=stock_ev, stock_addrs=stock_addrs, stock_hourly=stock_hourly, stock_admin=stock_admin, mint_senders=mint_senders,
                    usdg=usdg, usdg_flows=usdg_flows, weth=weth, pool_swaps=pool_swaps, pool_traders=pool_traders, pool_usdg=pool_usdg, pool_weth=pool_weth, pool_unpriced=pool_unpriced, eth_px=eth_px, stock_px_last=stock_px_last, stock_px_first=stock_px_first, stock_px_n=stock_px_n,
                    stock_swap_n=stock_swap_n, stock_swap_usdg=stock_swap_usdg, stock_swap_weth=stock_swap_weth, bucket_usdg=bucket_usdg, bucket_weth=bucket_weth, v2_count=v2_count, new_v3=new_v3, new_v4=new_v4, new_v2=new_v2, liq=liq, userops=userops, l2l1=l2l1,
                    nft_transfers=nft_transfers, nft_mints=nft_mints, fee_dist=fee_dist, router_fees=router_fees, router_fee_rcpt=router_fee_rcpt, focus=focus, ta_tot=ta_tot, ea_tot=ea_tot, v3_active=v3_active)

    R = run_pass(pools, True)
    S = R['S']
    v3_top = [p for p, _ in R['pool_swaps'].most_common() if len(p) == 42 and not (pools.get(p) or {}).get('token0')][:a.v3_pools]
    v4_top = [p for p, _ in R['pool_swaps'].most_common() if len(p) == 66 and not (pools.get(p) or {}).get('token0')][:a.v4_pools]
    if not a.offline and (v3_top or v4_top):
        before = set(k for k, v in pools.items() if v.get('token0'))
        pools = resolve_pools(v3_top, v4_top, pools_path, pools)
        newly = set(k for k, v in pools.items() if v.get('token0')) - before
        print('pools resolved now: %d new (candidates v3 %d, v4 %d); active pools v3 %d / v4 %d' % (len(newly), len(v3_top), len(v4_top), sum(1 for p in R['pool_swaps'] if len(p) == 42), sum(1 for p in R['pool_swaps'] if len(p) == 66)), flush=True)
        if newly:
            R2 = run_pass(pools, False, skip_pools=frozenset(before))
            R['pool_usdg'].update(R2['pool_usdg'])
            R['bucket_usdg'].update(R2['bucket_usdg'])
            R['stock_swap_n'].update(R2['stock_swap_n'])
            R['stock_swap_usdg'].update(R2['stock_swap_usdg'])
            R['stock_px_n'].update(R2['stock_px_n'])
            for pool, c in R2['pool_weth'].items():
                R['pool_weth'][pool].update(c)
            R['bucket_weth'].update(R2['bucket_weth'])
            for tok, c in R2['stock_swap_weth'].items():
                R['stock_swap_weth'][tok].update(c)
            for bk, v in R2['eth_px'].items():
                R['eth_px'][bk][0] += v[0]
                R['eth_px'][bk][1] += v[1]
            for tok, px in R2['stock_px_last'].items():
                R['stock_px_last'].setdefault(tok, px)
                R['stock_px_first'].setdefault(tok, R2['stock_px_first'].get(tok, px))
            for pool in list(R2['pool_usdg']) + list(R2['pool_weth']):
                R['pool_unpriced'].pop(pool, None)
    eth_series = {bk: v[0] / v[1] for bk, v in R['eth_px'].items() if v[1] > 0}
    eth_ref = statistics.median(eth_series.values()) if eth_series else None

    def eth_at(bk):
        return eth_series.get(bk, eth_ref) or 0

    pool_vol = collections.Counter()
    for pool, u in R['pool_usdg'].items():
        pool_vol[pool] += u
    for pool, c in R['pool_weth'].items():
        for bk, w_ in c.items():
            pool_vol[pool] += w_ * eth_at(bk)
    per_bucket_vol = collections.Counter(R['bucket_usdg'])
    for bk, w_ in R['bucket_weth'].items():
        per_bucket_vol[bk] += w_ * eth_at(bk)
    stock_swap_usd = collections.Counter(R['stock_swap_usdg'])
    for tok, c in R['stock_swap_weth'].items():
        for bk, w_ in c.items():
            stock_swap_usd[tok] += w_ * eth_at(bk)
    vol_usd_total = sum(pool_vol.values())
    priced_swaps = sum(c for p, c in R['pool_swaps'].items() if p in pool_vol)

    to_sorted = [k for k, _ in R['to_count'].most_common(80) if not k.startswith('CREATE:')]
    from_sorted = [k for k, _ in R['from_count'].most_common(60)]
    from_by_fees = [k for k, _ in sorted(R['from_stats'].items(), key=lambda kv: -kv[1]['fees'])[:30]]
    names, sels = {}, {}
    if not a.offline:
        want = set(to_sorted) | set(from_sorted) | set(from_by_fees)
        want.update([k for k, _ in R['creators'].most_common(15)])
        want.update([k.split('|')[0] for k, _ in R['ea_tot'].most_common(50)])
        want.update([t for t, _ in sorted(R['ta_tot'].items(), key=lambda kv: -kv[1][0])[:30]])
        want.update([t for t, _ in sorted(R['ta_tot'].items(), key=lambda kv: -kv[1][3])[:20]])
        want.update([k for k, _ in R['userops']['paymasters'].most_common(8)] + [k for k, _ in R['userops']['bundlers'].most_common(8)])
        want.update([k for k, _ in sorted(R['usdg_flows'].items(), key=lambda kv: -abs(kv[1]))[:25]])
        want.update([k for k, _ in R['mint_senders'].most_common(5)])
        bidders_sorted = sorted(R['bidders'], key=lambda x: -x[0])
        want.update([x[3] for x in bidders_sorted[:25]] + [x[4] for x in bidders_sorted[:25]])
        tv = sorted(R['top_value'], key=lambda x: -x[0])[:15]
        want.update([x[2] for x in tv] + [x[3] for x in tv])
        want.update([x['caller'] for x in R['l2l1'][:10]] + [x['destination'] for x in R['l2l1'][:10]])
        want.update([k for k, _ in R['nft_mints'].most_common(10)])
        want.update([t[0] for t in R['seven02']['targets'].most_common(5)])
        want.update(list(R['router_fees'].keys())[:10] + [k for k, _ in R['router_fee_rcpt'].most_common(5)])
        for pl, _ in pool_vol.most_common(40):
            pk = pools.get(pl) or {}
            want.update([x for x in (pk.get('token0'), pk.get('token1'), pk.get('hooks')) if x])
        for pl in R['new_v4'][:300]:
            want.add(pl['hooks'])
        want.discard(None)
        want = {w for w in want if isinstance(w, str) and w.startswith('0x') and len(w) == 42}
        names = bs_names(sorted(want), d / 'names.json')
        sels = openchain('function', [s for s, _ in R['sel_stats'].most_common(120)], d / 'selectors.json')
        sels = openchain('event', [k.split('|')[1] for k, _ in R['ea_tot'].most_common(60)], d / 'selectors.json')
    else:
        names = json.loads((d / 'names.json').read_text()) if (d / 'names.json').exists() else {}
        sels = json.loads((d / 'selectors.json').read_text()) if (d / 'selectors.json').exists() else {}

    def tokname2(x):
        return tokname(x) or (names.get(x) or {}).get('token') or (names.get(x) or {}).get('name') or x[:10]

    def poolname(pid):
        pk = pools.get(pid) or {}
        if not pk.get('token0'):
            return pid[:12] + ' (unresolved)'
        hooks = pk.get('hooks')
        hk = ''
        if hooks and hooks != ZERO_ADDR:
            hk = ' hook ' + ((names.get(hooks) or {}).get('name') or hooks[:10])
        return '%s/%s %s%s' % (tokname2(pk['token0']), tokname2(pk['token1']), pk.get('kind'), hk)

    stock_rows = []
    for tok, se in R['stock_ev'].items():
        ref = stocks[tok]['px']
        px_first, px_last = R['stock_px_first'].get(tok), R['stock_px_last'].get(tok)
        if ref and px_last and not (0.2 * ref <= px_last <= 5 * ref):
            px_first = px_last = None
        if not ref and R['stock_px_n'].get(tok, 0) < 5:
            px_first = px_last = None
        px = ref or px_last
        stock_rows.append({'token': tok, 'symbol': stocks[tok]['symbol'], 'transfers': se['transfers'], 'mints': se['mints'], 'burns': se['burns'], 'mint_tokens': se['mint_amt'] / 1e18, 'burn_tokens': se['burn_amt'] / 1e18,
                           'net_issued_tokens': (se['mint_amt'] - se['burn_amt']) / 1e18, 'volume_tokens': se['vol'] / 1e18, 'volume_usd': (se['vol'] / 1e18 * px) if px else None, 'net_issued_usd': ((se['mint_amt'] - se['burn_amt']) / 1e18 * px) if px else None,
                           'mint_usd': (se['mint_amt'] / 1e18 * px) if px else None, 'burn_usd': (se['burn_amt'] / 1e18 * px) if px else None, 'unique_from': se['from'].count(), 'unique_to': se['to'].count(), 'dex_transfers': se['dex'],
                           'swaps': R['stock_swap_n'].get(tok, 0), 'swap_usd': stock_swap_usd.get(tok, 0.0), 'px_blockscout': ref, 'px_onchain_first': px_first, 'px_onchain_last': px_last, 'onchain_price_points': R['stock_px_n'].get(tok, 0),
                           'max_transfer_tokens': se['max'][0] / 1e18, 'max_transfer_tx': se['max'][1]})
    stock_rows.sort(key=lambda r: -(r['volume_usd'] or 0))
    stock_tot = {'tokens_active': len(stock_rows), 'transfers': sum(r['transfers'] for r in stock_rows), 'mints': sum(r['mints'] for r in stock_rows), 'burns': sum(r['burns'] for r in stock_rows),
                 'volume_usd': sum(r['volume_usd'] or 0 for r in stock_rows), 'unpriced_tokens': sum(1 for r in stock_rows if r['volume_usd'] is None), 'net_issued_usd': sum(r['net_issued_usd'] or 0 for r in stock_rows), 'mint_usd': sum(r['mint_usd'] or 0 for r in stock_rows),
                 'burn_usd': sum(r['burn_usd'] or 0 for r in stock_rows), 'dex_transfers': sum(r['dex_transfers'] for r in stock_rows), 'swaps': sum(r['swaps'] for r in stock_rows), 'swap_usd': sum(r['swap_usd'] for r in stock_rows),
                 'unique_addresses': len(R['stock_addrs']), 'mint_tx_senders': [(k, label(k, names, stock_syms), c) for k, c in R['mint_senders'].most_common(5)]}

    series, series_bf, series_senders = R['series'], R['series_bf'], R['series_senders']

    def ser(bk):
        s = series[bk]
        bfs = series_bf[bk]
        return {'bucket_utc': time.strftime('%H:%M', time.gmtime(bk)), 'blocks': int(s['blocks']), 'txs': int(s['txs']), 'gas_M': round(s['gas'] / 1e6, 1), 'fees_eth': round(s['fees'] / 1e18, 3),
                'basefee_gwei_med': round(statistics.median(bfs) / 1e9, 3) if bfs else None, 'basefee_gwei_max': round(max(bfs) / 1e9, 3) if bfs else None, 'senders': len(series_senders[bk]),
                'failed': int(s['failed']), 'swaps': int(s['swaps']), 'dex_usd': round(per_bucket_vol.get(bk, 0.0)), 'stock_transfers': int(s['stock_transfers']), 'usdg_vol': round(s['usdg_vol']),
                'userops': int(s['userops']), 'eip7702': int(s['eip7702']), 'creations': int(s['creations']), 'new_pools': int(s['new_pools']), 'deposits': int(s['deposits']), 'eth_px': round(eth_series[bk], 2) if bk in eth_series else None}

    tx_user, fees_wei = S['tx_user'], S['fees_wei']
    top_to = []
    for k in to_sorted[:60]:
        st = R['to_stats'].get(k)
        if not st:
            continue
        top_to.append({'to': k, 'label': label(k, names, stock_syms), 'txs': R['to_count'][k], 'share_pct': round(100 * R['to_count'][k] / max(1, tx_user), 2), 'gas_M': round(st['gas'] / 1e6, 1), 'fees_eth': round(st['fees'] / 1e18, 3), 'fail_pct': round(100 * st['failed'] / max(1, st['txs']), 1),
                       'senders': st['senders'].count(), 'heavy_senders_100plus': sum(1 for _, c in st['sc'].items() if c >= 100), 'top_sender_share_pct': round(100 * st['sc'].most_common(1)[0][1] / st['txs'], 1) if st['sc'] else None, 'value_eth': round(st['value'] / 1e18, 2),
                       'top_selectors': [(s, (sels.get(s) or '').split('(')[0], c) for s, c in st['sels'].most_common(3)]})
    top_to_fees = []
    for k, st in sorted(R['to_stats'].items(), key=lambda kv: -kv[1]['fees'])[:25]:
        top_to_fees.append({'to': k, 'label': label(k, names, stock_syms), 'txs': R['to_count'][k], 'fees_eth': round(st['fees'] / 1e18, 3), 'fee_share_pct': round(100 * st['fees'] / max(1, fees_wei), 2), 'gas_per_tx': round(st['gas'] / max(1, st['txs']))})
    top_from = []
    for k in from_sorted[:40]:
        fs = R['from_stats'].get(k)
        if not fs:
            continue
        top_from.append({'from': k, 'label': label(k, names, stock_syms), 'txs': R['from_count'][k], 'fees_eth': round(fs['fees'] / 1e18, 3), 'fail_pct': round(100 * fs['failed'] / max(1, fs['txs']), 1), 'nonce_span': fs['last_nonce'] - fs['first_nonce'] + 1,
                         'targets': [(t, label(t, names, stock_syms), c) for t, c in fs['targets'].most_common(3)]})
    top_from_fees = []
    for k in from_by_fees[:25]:
        fs = R['from_stats'][k]
        top_from_fees.append({'from': k, 'label': label(k, names, stock_syms), 'txs': R['from_count'][k], 'fees_eth': round(fs['fees'] / 1e18, 3), 'fee_share_pct': round(100 * fs['fees'] / max(1, fees_wei), 2), 'targets': [(t, label(t, names, stock_syms), c) for t, c in fs['targets'].most_common(2)]})
    fleets = []
    for k in to_sorted[:25]:
        st = R['to_stats'].get(k)
        if not st:
            continue
        heavy = [(s_, c) for s_, c in st['sc'].items() if c >= 100]
        heavy.sort(key=lambda x: -x[1])
        fleets.append({'to': k, 'label': label(k, names, stock_syms), 'txs': st['txs'], 'heavy_senders': len(heavy), 'heavy_share_pct': round(100 * sum(c for _, c in heavy) / max(1, st['txs']), 1), 'top5': [(s_, c) for s_, c in heavy[:5]]})
    sel_rows = [{'selector': s, 'name': (sels.get(s) or ''), 'txs': c, 'share_pct': round(100 * c / max(1, tx_user), 2), 'fees_eth': round(R['sel_fee'][s] / 1e18, 3), 'top_targets': [(t, label(t, names, stock_syms), n) for t, n in R['sel_to'][s].most_common(2)]} for s, c in R['sel_stats'].most_common(40)]
    bidders = sorted(R['bidders'], key=lambda x: -x[0])
    ea_rows = [{'address': k.split('|')[0], 'label': label(k.split('|')[0], names, stock_syms), 'topic0': k.split('|')[1][:10], 'event': (sels.get('event:' + k.split('|')[1]) or '').split('(')[0], 'count': c} for k, c in R['ea_tot'].most_common(50)]
    ta_rows = [{'token': t, 'label': label(t, names, stock_syms), 'transfers': v[0], 'mints': v[1], 'burns': v[2], 'distinct_receivers_max_unit': v[3]} for t, v in sorted(R['ta_tot'].items(), key=lambda kv: -kv[1][0])[:40]]
    spam_rows = [{'token': t, 'label': label(t, names, stock_syms), 'transfers': v[0], 'mints': v[1], 'distinct_receivers_max_unit': v[3]} for t, v in sorted(R['ta_tot'].items(), key=lambda kv: -kv[1][3])[:25]]
    pool_rows = [{'pool': pl, 'name': poolname(pl), 'kind': (pools.get(pl) or {}).get('kind'), 'swaps': R['pool_swaps'][pl], 'traders': R['pool_traders'][pl].count() if pl in R['pool_traders'] else None, 'volume_usd': round(v), 'hooks': (pools.get(pl) or {}).get('hooks'), 'fee': (pools.get(pl) or {}).get('fee')} for pl, v in pool_vol.most_common(40)]
    unpriced = [{'pool': pl, 'name': poolname(pl), 'swaps': c} for pl, c in R['pool_unpriced'].most_common(15)]
    hooks_new = collections.Counter(pl['hooks'] for pl in R['new_v4'])
    hook_rows = [{'hooks': h, 'label': label(h, names, stock_syms), 'pools_initialized': c} for h, c in hooks_new.most_common(15)]
    stock_admin = sorted(R['stock_admin'], key=lambda x: x['block'])
    oracle_events = [e for e in stock_admin if e['topic'] in (ORACLE_PAUSED, ORACLE_UNPAUSED)]
    usdg = R['usdg']
    usdg['top'].sort(key=lambda x: -x[0])
    usdg_flow_rows = [{'address': k, 'label': label(k, names, stock_syms), 'net_usdg': round(v / 1e6)} for k, v in sorted(R['usdg_flows'].items(), key=lambda kv: -abs(kv[1]))[:25]]
    l2l1 = sorted(R['l2l1'], key=lambda x: -x['eth'])
    creations = sorted(R['creations'])
    basefees = S['basefees']
    seconds = (S['last_ts'] - S['first_ts']) if S['first_ts'] is not None else 0
    deposits = R['deposits']
    userops = R['userops']
    seven02 = R['seven02']
    weth = R['weth']
    stock_hourly = R['stock_hourly']

    out = {
        'window': {'chain': manifest.get('chain'), 'chain_id': manifest.get('chain_id'), 'client': manifest.get('client'), 'first_block': S['first_n'], 'last_block': S['last_n'], 'blocks': S['blocks'], 'expected_blocks': manifest['last_block'] - manifest['first_block'] + 1,
                   'first_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(S['first_ts'])) if S['first_ts'] else None, 'last_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(S['last_ts'])) if S['last_ts'] else None, 'seconds': seconds,
                   'block_time_s': round(seconds / max(1, S['blocks'] - 1), 4), 'txs_total': S['tx_total'], 'txs_user': tx_user, 'txs_internal': S['tx_total'] - tx_user - deposits['count'], 'user_tx_per_s': round(tx_user / max(1, seconds), 2),
                   'gas_total_G': round(S['gas_total'] / 1e9, 3), 'gas_per_s_M': round(S['gas_total'] / max(1, seconds) / 1e6, 2), 'gas_per_user_tx': round(S['gas_total'] / max(1, tx_user)), 'fees_eth': round(fees_wei / 1e18, 3), 'fees_usd': round(fees_wei / 1e18 * eth_ref) if eth_ref else None,
                   'fee_per_user_tx_usd': round(fees_wei / 1e18 * eth_ref / max(1, tx_user), 4) if eth_ref else None, 'basefee_gwei': {'min': round(min(basefees) / 1e9, 4), 'median': round(statistics.median(basefees) / 1e9, 4), 'p90': round(sorted(basefees)[int(0.9 * len(basefees))] / 1e9, 4), 'max': round(max(basefees) / 1e9, 4)} if basefees else None,
                   'unique_senders': len(R['senders']), 'failed_txs': R['failed'], 'failed_pct': round(100 * R['failed'] / max(1, tx_user), 2), 'failed_fees_eth': round(R['failed_fees'] / 1e18, 3), 'eth_price_ref': round(eth_ref, 2) if eth_ref else None, 'value_transferred_eth': round(R['value_eth_total'], 2), 'contract_creations': len(creations)},
        'series': [ser(bk) for bk in sorted(series)],
        'tx_types': [{'type': t, 'txs': c, 'gas_M': round(R['type_gas'][t] / 1e6, 1), 'fees_eth': round(R['type_fee'][t] / 1e18, 3)} for t, c in R['types'].most_common()],
        'top_to': top_to, 'top_to_by_fees': top_to_fees, 'top_from': top_from, 'top_from_by_fees': top_from_fees, 'sender_fleets': fleets, 'selectors': sel_rows,
        'gas_bidding': {'txs_ge_3x_basefee': R['bid_count'], 'senders_ge_3x': len(R['bid_senders']), 'bids_charged_above_basefee': R['bid_over_base'], 'extra_paid_eth': round(R['bid_extra_paid'] / 1e18, 6),
                        'top': [{'gas_price_gwei': round(g, 2), 'basefee_gwei': round(b, 3), 'multiple': round(g / b) if b else None, 'tx': h, 'from': f, 'to': t, 'to_label': label(t, names, stock_syms), 'selector': s, 'ok': st == 1, 'utc': time.strftime('%H:%M:%S', time.gmtime(ts))} for g, b, h, f, t, s, st, ts in bidders[:25]]},
        'creations': {'count': len(creations), 'creators_top': [(c, label(c, names, stock_syms), n) for c, n in R['creators'].most_common(15)], 'first': [{'block': n, 'utc': time.strftime('%H:%M:%S', time.gmtime(ts)), 'creator': f, 'address': ca, 'tx': h} for n, ts, f, ca, h in creations[:10]]},
        'deposits_l1_to_l2': {'count': deposits['count'], 'eth': round(deposits['eth'], 3), 'by_type': dict(deposits['by_type'])},
        'withdrawals_l2_to_l1': {'count': len(l2l1), 'eth': round(sum(x['eth'] for x in l2l1), 3), 'callers': [(k, label(k, names, stock_syms), c) for k, c in collections.Counter(x['caller'] for x in l2l1).most_common(5)], 'top': [{**x, 'caller_label': label(x['caller'], names, stock_syms)} for x in l2l1[:10]]},
        'eip7702': {'txs': seven02['txs'], 'senders': len(seven02['senders']), 'targets': [(t, label(t, names, stock_syms), c) for t, c in seven02['targets'].most_common(5)]},
        'account_abstraction': {'userops': userops['count'], 'success': userops['success'], 'unique_senders': len(userops['senders']), 'entrypoints': dict(userops['entrypoint']), 'paymasters': [(k, label(k, names, stock_syms), c) for k, c in userops['paymasters'].most_common(8)], 'bundlers': [(k, label(k, names, stock_syms), c) for k, c in userops['bundlers'].most_common(8)]},
        'stocks': {'totals': stock_tot, 'rows': stock_rows[:60], 'hourly': [{'hour_utc': time.strftime('%H:%M', time.gmtime(hb)), **{k: (round(v) if 'usd' in k else v) for k, v in c.items()}} for hb, c in sorted(stock_hourly.items())], 'admin_events': stock_admin[:200], 'oracle_events': oracle_events[:50]},
        'usdg': {'transfers': usdg['transfers'], 'volume_usd': round(usdg['vol'] / 1e6), 'mints': usdg['mints'], 'mint_usd': round(usdg['mint_amt'] / 1e6), 'burns': usdg['burns'], 'burn_usd': round(usdg['burn_amt'] / 1e6), 'unique_addresses': len(usdg['addrs']),
                 'largest': [{'usd': round(u), 'tx': h, 'from': f, 'from_label': label(f, names, stock_syms), 'to': t, 'to_label': label(t, names, stock_syms), 'utc': time.strftime('%H:%M:%S', time.gmtime(ts))} for u, h, f, t, ts in usdg['top'][:15]], 'net_flows': usdg_flow_rows},
        'weth': {k: (round(v, 3) if isinstance(v, float) else v) for k, v in weth.items()},
        'dex': {'swaps_total': sum(R['pool_swaps'].values()) + R['v2_count'], 'v3_swaps': sum(c for p, c in R['pool_swaps'].items() if len(p) == 42), 'v4_swaps': sum(c for p, c in R['pool_swaps'].items() if len(p) == 66), 'v2_swaps': R['v2_count'], 'priced_swaps': priced_swaps, 'volume_usd_priced': round(vol_usd_total),
                'pools_active_v3': sum(1 for p in R['pool_swaps'] if len(p) == 42), 'pools_active_v4': sum(1 for p in R['pool_swaps'] if len(p) == 66), 'pools_priced': len(pool_vol), 'new_pools': {'v3': len(R['new_v3']), 'v4': len(R['new_v4']), 'v2': R['new_v2']}, 'new_v4_hooks': hook_rows, 'liquidity_events': dict(R['liq']),
                'top_pools': pool_rows, 'unpriced_top': unpriced, 'eth_price_series': [(time.strftime('%H:%M', time.gmtime(bk)), round(v, 2)) for bk, v in sorted(eth_series.items())],
                'new_v4_pools_sample': [{**pl, 'utc': time.strftime('%H:%M:%S', time.gmtime(pl['ts'])), 'name': '%s/%s' % (tokname2(pl['token0']), tokname2(pl['token1'])), 'hook_label': label(pl['hooks'], names, stock_syms)} for pl in R['new_v4'][:30]]},
        'nft': {'transfers': R['nft_transfers'], 'mints_top': [(k, label(k, names, stock_syms), c) for k, c in R['nft_mints'].most_common(10)]},
        'fee_distribution_events': R['fee_dist'][:50],
        'fee_router': {'address': FEE_ROUTER, 'fee_events_by_topic1': [{'topic1': k, 'label': label(k, names, stock_syms), 'events': v[0], 'amount_raw': str(v[1]), 'amount_units': round(v[1] / (1e6 if k == USDG else 1e18), 4)} for k, v in sorted(R['router_fees'].items(), key=lambda kv: -kv[1][0])[:10]],
                       'topic2_top': [(k, label(k, names, stock_syms), c) for k, c in R['router_fee_rcpt'].most_common(5)]},
        'focus_flows': {FOCUS[f]: {tk: {'in': (fx['in'] / (1e6 if tk == 'USDG' else 1e18)), 'out': (fx['out'] / (1e6 if tk == 'USDG' else 1e18)), 'n_in': fx['n_in'], 'n_out': fx['n_out'], 'counterparties': fx['cp'].count()} for tk, fx in sorted(fl.items(), key=lambda kv: -(kv[1]['in'] + kv[1]['out']))[:12]} for f, fl in R['focus'].items()},
        'event_landscape': ea_rows,
        'token_transfer_aggregates': ta_rows, 'airdrop_candidates': spam_rows,
        'top_value_txs': [{'eth': round(v, 3), 'tx': h, 'from': f, 'from_label': label(f, names, stock_syms), 'to': t, 'to_label': label(t, names, stock_syms), 'utc': time.strftime('%H:%M:%S', time.gmtime(ts))} for v, h, f, t, ts in sorted(R['top_value'], key=lambda x: -x[0])[:15]],
    }
    (d / 'analysis.json').write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out['window'], indent=1))
    if a.md:
        (d / 'tables.md').write_text(render(out))
        print('wrote', d / 'tables.md')


def md_table(rows, cols, fmt=None):
    if not rows:
        return '_none_\n'
    fmt = fmt or {}
    head = '| ' + ' | '.join(cols) + ' |\n|' + '|'.join('---' for _ in cols) + '|\n'
    body = ''
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c) if isinstance(r, dict) else r[cols.index(c)]
            if isinstance(v, float):
                v = fmt.get(c, '{:,.2f}').format(v)
            elif isinstance(v, int) and not isinstance(v, bool):
                v = '{:,}'.format(v)
            elif isinstance(v, (list, tuple)):
                v = '; '.join(' '.join(str(y) for y in x) if isinstance(x, (list, tuple)) else str(x) for x in v)
            cells.append(str(v if v is not None else '').replace('|', '/'))
        body += '| ' + ' | '.join(cells) + ' |\n'
    return head + body


def render(o):
    w = o['window']
    L = ['# Deterministic tables\n', 'Window %s to %s UTC, blocks %s-%s (%s blocks, %.3f s/block). User txs %s (%.1f/s), fees %s ETH (~$%s), median base fee %s gwei, unique senders %s, failed %s%% (paying %s ETH), contract creations %s.\n' % (
        w['first_utc'], w['last_utc'], w['first_block'], w['last_block'], format(w['blocks'], ','), w['block_time_s'], format(w['txs_user'], ','), w['user_tx_per_s'], w['fees_eth'], format(w['fees_usd'] or 0, ','), w['basefee_gwei']['median'] if w['basefee_gwei'] else None, format(w['unique_senders'], ','), w['failed_pct'], w['failed_fees_eth'], w['contract_creations'])]
    L.append('\n## Series (15-minute buckets)\n')
    L.append(md_table(o['series'], ['bucket_utc', 'blocks', 'txs', 'gas_M', 'fees_eth', 'basefee_gwei_med', 'basefee_gwei_max', 'senders', 'failed', 'swaps', 'dex_usd', 'stock_transfers', 'usdg_vol', 'userops', 'eip7702', 'creations', 'new_pools', 'eth_px'], {'fees_eth': '{:,.3f}', 'basefee_gwei_med': '{:.3f}', 'basefee_gwei_max': '{:.3f}', 'gas_M': '{:,.0f}'}))
    L.append('\n## Transaction types\n')
    L.append(md_table(o['tx_types'], ['type', 'txs', 'gas_M', 'fees_eth']))
    L.append('\n## Top targets by transactions\n')
    L.append(md_table(o['top_to'][:40], ['to', 'label', 'txs', 'share_pct', 'gas_M', 'fees_eth', 'fail_pct', 'senders', 'heavy_senders_100plus', 'top_sender_share_pct', 'value_eth', 'top_selectors']))
    L.append('\n## Sender fleets (senders with >= 100 txs to the target)\n')
    L.append(md_table(o['sender_fleets'], ['to', 'label', 'txs', 'heavy_senders', 'heavy_share_pct', 'top5']))
    L.append('\n## Top targets by fees paid to them (gas burned there)\n')
    L.append(md_table(o['top_to_by_fees'], ['to', 'label', 'txs', 'fees_eth', 'fee_share_pct', 'gas_per_tx']))
    L.append('\n## Top senders by transactions\n')
    L.append(md_table(o['top_from'][:30], ['from', 'label', 'txs', 'fees_eth', 'fail_pct', 'nonce_span', 'targets']))
    L.append('\n## Top senders by fees\n')
    L.append(md_table(o['top_from_by_fees'], ['from', 'label', 'txs', 'fees_eth', 'fee_share_pct', 'targets']))
    L.append('\n## Selectors\n')
    L.append(md_table(o['selectors'][:30], ['selector', 'name', 'txs', 'share_pct', 'fees_eth', 'top_targets']))
    g = o['gas_bidding']
    L.append('\n## Gas bidding (txs at >= 3x base fee: %s from %s senders; charged above base fee: %s, extra paid %s ETH)\n' % (format(g['txs_ge_3x_basefee'], ','), g['senders_ge_3x'], g['bids_charged_above_basefee'], g['extra_paid_eth']))
    L.append(md_table(g['top'], ['utc', 'gas_price_gwei', 'basefee_gwei', 'multiple', 'from', 'to', 'to_label', 'selector', 'ok', 'tx']))
    s = o['stocks']
    t = s['totals']
    L.append('\n## Robinhood stock tokens (%s active of the registry; %s transfers, %s mints, %s burns; transfer volume ~$%s (%s tokens unpriced); minted ~$%s, burned ~$%s; DEX-touching transfers %s; swaps %s (~$%s); %s distinct addresses)\n' % (
        t['tokens_active'], format(t['transfers'], ','), t['mints'], t['burns'], format(round(t['volume_usd']), ','), t['unpriced_tokens'], format(round(t['mint_usd']), ','), format(round(t['burn_usd']), ','), format(t['dex_transfers'], ','), format(t['swaps'], ','), format(round(t['swap_usd']), ','), format(t['unique_addresses'], ',')))
    L.append('Mint transaction senders: %s\n' % t['mint_tx_senders'])
    L.append(md_table(s['rows'][:40], ['symbol', 'token', 'transfers', 'mints', 'burns', 'net_issued_tokens', 'volume_tokens', 'volume_usd', 'unique_from', 'unique_to', 'dex_transfers', 'swaps', 'swap_usd', 'px_blockscout', 'px_onchain_first', 'px_onchain_last', 'max_transfer_tokens'], {'volume_usd': '{:,.0f}', 'swap_usd': '{:,.0f}', 'net_issued_tokens': '{:,.2f}', 'volume_tokens': '{:,.1f}', 'max_transfer_tokens': '{:,.1f}'}))
    L.append('\n### Stock tokens by hour (USD at Blockscout price)\n')
    L.append(md_table(s['hourly'], ['hour_utc', 'transfers', 'transfer_usd', 'mints', 'mint_usd', 'burns', 'burn_usd']))
    L.append('\n### Stock admin / oracle events (non-transfer logs of stock tokens)\n')
    L.append(md_table([{**e, 'utc': time.strftime('%H:%M:%S', time.gmtime(e['ts']))} for e in s['admin_events'][:40]], ['utc', 'token', 'topic', 'tx']))
    u = o['usdg']
    L.append('\n## USDG (%s transfers, volume $%s, mints %s ($%s), burns %s ($%s), %s addresses)\n' % (format(u['transfers'], ','), format(u['volume_usd'], ','), u['mints'], format(u['mint_usd'], ','), u['burns'], format(u['burn_usd'], ','), format(u['unique_addresses'], ',')))
    L.append(md_table(u['largest'], ['utc', 'usd', 'from', 'from_label', 'to', 'to_label', 'tx']))
    L.append('\n### USDG net flows by address\n')
    L.append(md_table(u['net_flows'], ['address', 'label', 'net_usdg']))
    x = o['dex']
    L.append('\n## DEX (%s swaps: v3 %s, v4 %s, v2 %s; priced %s = $%s across %s pools; active pools v3 %s / v4 %s; new pools v3 %s, v4 %s, v2 %s)\n' % (format(x['swaps_total'], ','), format(x['v3_swaps'], ','), format(x['v4_swaps'], ','), x['v2_swaps'], format(x['priced_swaps'], ','), format(x['volume_usd_priced'], ','), x['pools_priced'], x['pools_active_v3'], x['pools_active_v4'], x['new_pools']['v3'], x['new_pools']['v4'], x['new_pools']['v2']))
    L.append(md_table(x['top_pools'], ['name', 'kind', 'swaps', 'traders', 'volume_usd', 'fee', 'pool']))
    L.append('\n### Unpriced active pools\n')
    L.append(md_table(x['unpriced_top'], ['name', 'swaps', 'pool']))
    L.append('\n### New v4 pools by hook\n')
    L.append(md_table(x['new_v4_hooks'], ['hooks', 'label', 'pools_initialized']))
    L.append('\n### ETH price on-chain (WETH/USDG VWAP per bucket)\n')
    L.append(md_table([{'bucket': b, 'eth_usd': v} for b, v in x['eth_price_series']], ['bucket', 'eth_usd']))
    aa = o['account_abstraction']
    L.append('\n## Account abstraction: %s userops (%s ok) from %s senders; entrypoints %s; EIP-7702 txs %s from %s senders\n' % (format(aa['userops'], ','), format(aa['success'], ','), format(aa['unique_senders'], ','), aa['entrypoints'], format(o['eip7702']['txs'], ','), format(o['eip7702']['senders'], ',')))
    L.append(md_table([{'paymaster': k, 'label': l, 'ops': c} for k, l, c in aa['paymasters']], ['paymaster', 'label', 'ops']))
    L.append(md_table([{'bundler': k, 'label': l, 'ops': c} for k, l, c in aa['bundlers']], ['bundler', 'label', 'ops']))
    L.append(md_table([{'target': k, 'label': l, 'txs': c} for k, l, c in o['eip7702']['targets']], ['target', 'label', 'txs']))
    b = o['deposits_l1_to_l2']
    wd = o['withdrawals_l2_to_l1']
    L.append('\n## Bridge: L1->L2 deposits %s (%s ETH, types %s); L2->L1 messages %s (%s ETH); callers %s\n' % (b['count'], b['eth'], b['by_type'], wd['count'], wd['eth'], wd['callers']))
    L.append(md_table(wd['top'], ['caller', 'caller_label', 'destination', 'eth', 'tx']))
    L.append('\n## WETH\n')
    L.append(md_table([o['weth']], ['deposits', 'dep_eth', 'withdrawals', 'wd_eth', 'transfers']))
    c = o['creations']
    L.append('\n## Contract creations: %s\n' % c['count'])
    L.append(md_table([{'creator': k, 'label': l, 'created': n} for k, l, n in c['creators_top']], ['creator', 'label', 'created']))
    L.append('\n## Event landscape (all logs, by emitter and topic)\n')
    L.append(md_table(o['event_landscape'][:40], ['address', 'label', 'topic0', 'event', 'count']))
    L.append('\n## ERC-20 transfer aggregates (tokens not kept in full)\n')
    L.append(md_table(o['token_transfer_aggregates'][:30], ['token', 'label', 'transfers', 'mints', 'burns', 'distinct_receivers_max_unit']))
    L.append('\n## Airdrop / mass-distribution candidates (most distinct receivers within one 100-block unit)\n')
    L.append(md_table(o['airdrop_candidates'][:20], ['token', 'label', 'transfers', 'mints', 'distinct_receivers_max_unit']))
    L.append('\n## NFT: %s ERC-721 transfers\n' % format(o['nft']['transfers'], ','))
    L.append(md_table([{'collection': k, 'label': l, 'mints': c} for k, l, c in o['nft']['mints_top']], ['collection', 'label', 'mints']))
    L.append('\n## Largest native ETH value transfers\n')
    L.append(md_table(o['top_value_txs'], ['utc', 'eth', 'from', 'from_label', 'to', 'to_label', 'tx']))
    fr = o['fee_router']
    L.append('\n## Fee router %s: FeeCollected events by token (topic1)\n' % fr['address'])
    L.append(md_table(fr['fee_events_by_topic1'], ['topic1', 'label', 'events', 'amount_raw', 'amount_units']))
    L.append('\n## Focus-address token flows (units: tokens; USDG in dollars)\n')
    for name_, fl in o['focus_flows'].items():
        L.append('\n### %s\n' % name_)
        L.append(md_table([{'token': tk, **v} for tk, v in fl.items()], ['token', 'in', 'out', 'n_in', 'n_out', 'counterparties'], {'in': '{:,.2f}', 'out': '{:,.2f}'}))
    L.append('\n## Fee distribution events in window\n')
    L.append(md_table(o['fee_distribution_events'][:20], ['contract', 'topic', 'block', 'tx']))
    return '\n'.join(L)


if __name__ == '__main__':
    main()
