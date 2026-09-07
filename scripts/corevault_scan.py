#!/usr/bin/env python3
"""Find CORE / cVault.finance-style reward vaults that are harvestable the way StacyVault is.

Background (see research/2026-09-07/stacy_farm/findings.md): a CoreVault-family MasterChef pays reward lumps
pro-rata to *instantaneous* stake (rewards are pushed in by a token fee via `addPendingRewards` and distributed at
`massUpdatePools`), and its `depositFor` path does not set `lastDepositBlock`, so a flash-minted position can deposit
and withdraw in one block and capture ~all of a pool's share of the next lump. The strategy is only worth running when
a pool's LP is a *flash-mintable* pair (both sides blue-chip: WETH/USDC/USDT/WBTC/DAI...) AND that pool has little
staked (cheap to dominate) AND the reward token has real value and live fee flow. StacyVault has blue-chip pools but a
dust reward token; this scanner looks for the same shape with a token that is actually worth something.

Multichain (`--chain ethereum|arbitrum|bsc|base|polygon`). Candidates come from a Blockscout name search where one is
available (Ethereum, Arbitrum) and otherwise from `--addresses`. Verified source is fetched from Blockscout or, via the
`--source etherscan` backend (default where a chain has no Blockscout name-search host), the Etherscan V2 key in
`etherscan_key.txt` — whose free tier serves `getsourcecode` on BSC/Base/Polygon/Arbitrum even though its account/proxy
modules are gated there. On-chain reads (pools, prices) always go through a public JSON-RPC per chain. Read-only.

    uv run --with pycryptodome python scripts/corevault_scan.py --chain ethereum          # Blockscout name search
    uv run --with pycryptodome python scripts/corevault_scan.py --chain bsc --addresses 0x...  # Etherscan source + BSC RPC
"""
import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from Crypto.Hash import keccak

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from drpc import rpc as drpc_rpc, Revert  # JSON-RPC eth_call with public-endpoint rotation
import etherscan  # Etherscan V2 verified-source client (cross-chain, key from etherscan_key.txt)
import bytecode_fingerprint  # source-free CoreVault detection by selector cluster + norm codehash

ROOT = Path(__file__).resolve().parents[1]

# Per-chain presets: Blockscout host, JSON-RPC endpoints (rotated), blue-chip token set (flash-mintable pair sides),
# UniswapV2-style factories used only to price the reward token, and the native-coin USD price used for that pricing.
CHAINS = {
    'ethereum': {
        'chainid': 1,
        'host': 'eth.blockscout.com',
        'rpc': ['https://eth.drpc.org', 'https://ethereum-rpc.publicnode.com', 'https://eth.merkle.io', 'https://1rpc.io/eth'],
        'weth': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
        'blue': {
            '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': 'WETH', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 'USDC',
            '0xdac17f958d2ee523a2206206994597c13d831ec7': 'USDT', '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599': 'WBTC',
            '0x6b175474e89094c44da98b954eedeac495271d0f': 'DAI', '0x853d955acef822db058eb8505911ed77f175b99e': 'FRAX',
            '0x5f98805a4e8be255a32880fdec7f6728c6568ba0': 'LUSD',
        },
        'factories': ['0x5c69bee701ef814a2b6a3edd4b1652cb9cc5aa6f', '0xc0aee478e3658e2610c5f7a4a2e1777ce9e4f2ac'],
        'native_usd': 2500.0,
    },
    'arbitrum': {
        'chainid': 42161,
        'host': 'arbitrum.blockscout.com',
        'rpc': ['https://arbitrum.drpc.org', 'https://arb1.arbitrum.io/rpc', 'https://arbitrum-one-rpc.publicnode.com', 'https://1rpc.io/arb'],
        'weth': '0x82af49447d8a07e3bd95bd0d56f35241523fbab1',
        'blue': {
            '0x82af49447d8a07e3bd95bd0d56f35241523fbab1': 'WETH', '0xaf88d065e77c8cc2239327c5edb3a432268e5831': 'USDC',
            '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8': 'USDC.e', '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9': 'USDT',
            '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f': 'WBTC', '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': 'DAI',
        },
        'factories': ['0xc35dadb65012ec5796536bd9864ed8773abc74c4', '0x6eccab422d763ac031210895c81787e87b43a652'],
        'native_usd': 2500.0,
    },
    'bsc': {
        'chainid': 56, 'host': None, 'rpc': etherscan.CHAIN_RPC[56][1],
        'weth': '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
        'blue': {
            '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c': 'WBNB', '0x55d398326f99059ff775485246999027b3197955': 'USDT',
            '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d': 'USDC', '0xe9e7cea3dedca5984780bafc599bd69add087d56': 'BUSD',
            '0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c': 'BTCB', '0x2170ed0880ac9a755fd29b2688956bd959f933f8': 'ETH',
        },
        'factories': ['0xca143ce32fe78f1f7019d7d551a6402fc5350c73'], 'native_usd': 600.0,
    },
    'base': {
        'chainid': 8453, 'host': None, 'rpc': etherscan.CHAIN_RPC[8453][1],
        'weth': '0x4200000000000000000000000000000000000006',
        'blue': {
            '0x4200000000000000000000000000000000000006': 'WETH', '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913': 'USDC',
            '0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca': 'USDbC', '0x50c5725949a6f0c72e6c4a641f24049a917db0cb': 'DAI',
            '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf': 'cbBTC',
        },
        'factories': ['0x8909dc15e40173ff4699343b6eb8132c65e18ec6'], 'native_usd': 2500.0,
    },
    'polygon': {
        'chainid': 137, 'host': None, 'rpc': etherscan.CHAIN_RPC[137][1],
        'weth': '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270',
        'blue': {
            '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270': 'WMATIC', '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359': 'USDC',
            '0x2791bca1f2de4661ed88a30c99a7a9449aa84174': 'USDC.e', '0xc2132d05d31c914a87c6611c10748aeb04b58e8f': 'USDT',
            '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619': 'WETH', '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6': 'WBTC',
            '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063': 'DAI',
        },
        'factories': ['0x5757371414417b8c6caad45baef941abc7d3ab32', '0xc35dadb65012ec5796536bd9864ed8773abc74c4'], 'native_usd': 0.5,
    },
}

WETH = CHAINS['ethereum']['weth']
BLUE = CHAINS['ethereum']['blue']
FACTORIES = CHAINS['ethereum']['factories']
NATIVE_USD = CHAINS['ethereum']['native_usd']
RPC_ENDPOINTS = None  # set in main() from the chosen chain
CHAINID = 1
SOURCE_BACKEND = 'blockscout'  # 'blockscout' (name search) or 'etherscan' (verified source via key)
CHAIN_NAME = 'ethereum'  # for bytecode_fingerprint public-RPC selection


def sel(sig):
    k = keccak.new(digest_bits=256)
    k.update(sig.encode())
    return '0x' + k.hexdigest()[:8]


SELS = {n: sel(n + s) for n, s in {
    'poolLength': '()', 'poolInfo': '(uint256)', 'token0': '()', 'token1': '()', 'getReserves': '()',
    'totalSupply': '()', 'balanceOf': '(address)', 'symbol': '()', 'decimals': '()', 'getPair': '(address,address)',
}.items()}
# candidate reward-token getters on the vault (first that returns an address wins)
REWARD_GETTERS = [sel(n + '()') for n in ('stacy', 'core', 'rewardToken', 'rewards', 'cake', 'token', 'CORE', 'reward')]


def http_json(url, timeout=30, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'llm-quant research', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            return json.loads(body)
        except Exception as e:
            if i == retries:
                return {'_error': str(e)[:120]}
            time.sleep(1.0)


def eth_call(host, to, data, timeout=25):
    # `host` is kept for signature stability; reads go through public JSON-RPC (Blockscout's proxy is rate-limited).
    try:
        res = drpc_rpc('eth_call', [{'to': to, 'data': data}, 'latest'], endpoints=(RPC_ENDPOINTS or None) or __import__('drpc').ENDPOINTS, timeout=timeout, retries=2)
    except Revert:
        return None
    except Exception:
        return None
    if isinstance(res, str) and res.startswith('0x') and len(res) > 2:
        return res
    return None


def enc_addr(a):
    return a.lower().replace('0x', '').rjust(64, '0')


def word(hexres, i):
    h = hexres[2:]
    return h[i * 64:(i + 1) * 64]


def as_addr(w):
    return '0x' + w[-40:]


def as_int(w):
    return int(w, 16) if w else 0


def call_uint(host, to, name):
    r = eth_call(host, to, SELS[name])
    return as_int(word(r, 0)) if r else None


def call_addr(host, to, name):
    r = eth_call(host, to, SELS[name])
    return as_addr(word(r, 0)) if r else None


def call_symbol(host, to):
    r = eth_call(host, to, SELS['symbol'])
    if not r:
        return '?'
    try:
        h = r[2:]
        # try string ABI (offset,len,data)
        if len(h) >= 128:
            ln = int(h[64:128], 16)
            if 0 < ln <= 32:
                return bytes.fromhex(h[128:128 + ln * 2]).decode('utf-8', 'replace').strip('\x00')
        return bytes.fromhex(h[:64]).decode('utf-8', 'replace').strip('\x00') or '?'
    except Exception:
        return '?'


def get_pair(host, factory, a, b):
    r = eth_call(host, factory, SELS['getPair'] + enc_addr(a) + enc_addr(b))
    if not r:
        return None
    p = as_addr(word(r, 0))
    return None if p == '0x' + '0' * 40 else p


def reward_token_price_usd(host, tok):
    """Best-effort (USD price, basis, liquidity_usd) of a token from its WETH-pair. liquidity_usd ~ the WETH-side
    reserve value (half the pool TVL) — the depth you could actually sell harvested rewards into."""
    if not tok or tok == '0x' + '0' * 40:
        return None, None, None
    if tok.lower() in BLUE:
        return (1.0 if BLUE[tok.lower()] in ('USDC', 'USDT', 'DAI', 'FRAX', 'LUSD') else None), BLUE[tok.lower()], 1e12
    for fac in FACTORIES:
        pair = get_pair(host, fac, tok, WETH)
        if not pair:
            continue
        rr = eth_call(host, pair, SELS['getReserves'])
        t0 = call_addr(host, pair, 'token0')
        if not rr or not t0:
            continue
        r0 = int(word(rr, 0), 16)
        r1 = int(word(rr, 1), 16)
        dec = call_uint(host, tok, 'decimals') or 18
        weth_res, tok_res = (r1, r0) if t0.lower() == tok.lower() else (r0, r1)
        if tok_res == 0:
            continue
        eth_per_tok = (weth_res / 1e18) / (tok_res / 10 ** dec)
        return eth_per_tok * NATIVE_USD, 'WETH-pair', (weth_res / 1e18) * NATIVE_USD
    return None, None, None


def name_search(host, q, limit=50):
    if not host:
        return []
    d = http_json('https://%s/api/v2/smart-contracts?q=%s' % (host, urllib.parse.quote(q)))
    items = d.get('items', []) if isinstance(d, dict) else []
    out = []
    for it in items[:limit]:
        a = it.get('address') or {}
        out.append((a.get('hash') or it.get('address_hash') or '').lower())
    return [a for a in out if a]


def get_source(host, addr):
    """Return (name, source_text, impl_addr_or_None). Uses Etherscan V2 (key) or Blockscout per SOURCE_BACKEND."""
    if SOURCE_BACKEND == 'etherscan':
        r = etherscan.source(CHAINID, addr)
        return r.get('name'), r.get('source') or '', r.get('implementation')
    d = http_json('https://%s/api/v2/smart-contracts/%s' % (host, addr))
    src = (d.get('source_code') or '') if isinstance(d, dict) else ''
    name = d.get('name') if isinstance(d, dict) else None
    impl = None
    if not src or 'depositFor' not in src:
        a = http_json('https://%s/api/v2/addresses/%s' % (host, addr))
        for i in (a.get('implementations') or []) if isinstance(a, dict) else []:
            impl = i.get('address_hash')
            break
        if impl:
            d2 = http_json('https://%s/api/v2/smart-contracts/%s' % (host, impl))
            if isinstance(d2, dict) and d2.get('source_code'):
                return name or d2.get('name'), d2.get('source_code'), impl
    return name, src, impl


def fingerprint(src):
    """Is this a CoreVault-family vault, and is the same-block guard bypassable?"""
    if not src:
        return None
    has_depositfor = 'depositFor' in src
    has_lump = ('addPendingRewards' in src) or ('updateAndPayOutPending' in src)
    has_share = 'PerShare' in src  # accCorePerShare / accStacyPerShare / accXPerShare
    if not (has_depositfor and has_lump and has_share):
        return None
    # guard analysis
    has_guard = 'lastDepositBlock' in src
    # does depositFor set lastDepositBlock?
    i = src.find('function depositFor')
    j = src.find('}', i) if i >= 0 else -1
    # crude: take ~1200 chars of the depositFor body
    body = src[i:i + 1400] if i >= 0 else ''
    depositfor_sets_guard = 'lastDepositBlock' in body and '=' in body[body.find('lastDepositBlock'):body.find('lastDepositBlock') + 40] if body else False
    if not has_guard:
        guard = 'none (deposit+withdraw same block allowed)'
        bypassable = True
    elif not depositfor_sets_guard:
        guard = 'present but depositFor does NOT set it -> bypassable'
        bypassable = True
    else:
        guard = 'depositFor sets lastDepositBlock -> not bypassable via depositFor'
        bypassable = False
    return {'lump_rewards': has_lump, 'guard': guard, 'bypassable': bypassable}


def analyze_vault(host, addr):
    name, src, impl = get_source(host, addr)
    fp = fingerprint(src)
    # bytecode fingerprint — works with no verified source, on any chain (see scripts/bytecode_fingerprint.py)
    try:
        bfp = bytecode_fingerprint.fingerprint(CHAIN_NAME, addr)
    except Exception:
        bfp = {}
    if not fp:
        if bfp.get('is_corevault_fork'):
            # unverified/renamed but the bytecode carries the CoreVault selector cluster; the depositFor guard bypass
            # is inherited from the CORE origin, so treat as bypassable and flag pools/token for verification.
            fp = {'lump_rewards': True, 'bypassable': True,
                  'guard': 'CoreVault selector cluster in bytecode (source unavailable) — depositFor bypass inherited from CORE origin, verify',
                  'bytecode_only': True}
        else:
            return {'address': addr, 'match': False, 'bytecode_matched': bfp.get('n_matched', 0)}
    # reward token
    rtok = None
    for g in REWARD_GETTERS:
        r = eth_call(host, addr, g)
        if r and len(r) >= 66:
            cand = as_addr(word(r, 0))
            if cand != '0x' + '0' * 40 and int(cand, 16) > 0xffff:
                rtok = cand
                break
    rsym = call_symbol(host, rtok) if rtok else '?'
    rprice, rbasis, rliq = reward_token_price_usd(host, rtok) if rtok else (None, None, None)
    rbal = None
    if rtok:
        rr = eth_call(host, rtok, SELS['balanceOf'] + enc_addr(addr))
        rbal = as_int(word(rr, 0)) if rr else None
    # pools
    npools = call_uint(host, addr, 'poolLength') or 0
    pools = []
    bluechip_cheap = 0
    for pid in range(min(npools, 24)):
        r = eth_call(host, addr, SELS['poolInfo'] + hex(pid)[2:].rjust(64, '0'))
        if not r:
            continue
        ptok = as_addr(word(r, 0))
        t0 = call_addr(host, ptok, 'token0')
        t1 = call_addr(host, ptok, 'token1')
        row = {'pid': pid, 'token': ptok}
        if t0 and t1:
            s0 = BLUE.get(t0.lower()) or call_symbol(host, t0)
            s1 = BLUE.get(t1.lower()) or call_symbol(host, t1)
            both_blue = (t0.lower() in BLUE) and (t1.lower() in BLUE)
            ts = call_uint(host, ptok, 'totalSupply') or 0
            rb = eth_call(host, ptok, SELS['balanceOf'] + enc_addr(addr))
            staked = as_int(word(rb, 0)) if rb else 0
            share = (staked / ts) if ts else 0
            row.update({'pair': s0 + '/' + s1, 'both_blue': both_blue, 'vault_share_of_pair': round(share, 6)})
            if both_blue and share < 0.5:
                bluechip_cheap += 1
        else:
            row.update({'pair': 'not-a-univ2-pair'})
        pools.append(row)
        time.sleep(0.05)
    MIN_REWARD_LIQ_USD = 25000.0
    score = fp['bypassable'] and bluechip_cheap > 0 and (rliq or 0) >= MIN_REWARD_LIQ_USD
    return {
        'address': addr, 'match': True, 'name': name, 'impl': impl, **fp,
        'reward_token': rtok, 'reward_symbol': rsym, 'reward_price_usd_est': rprice, 'reward_price_basis': rbasis, 'reward_liq_usd': round(rliq) if rliq else None,
        'reward_bal_in_vault': rbal, 'pools': pools, 'bluechip_cheap_pools': bluechip_cheap,
        'EXPLOITABLE_AND_VALUABLE': bool(score),
        'bytecode_matched': bfp.get('n_matched', 0), 'bytecode_fork': bfp.get('is_corevault_fork'), 'logic_hash': bfp.get('norm_codehash'),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--chain', default='ethereum', choices=list(CHAINS.keys()))
    p.add_argument('--host', default='')
    p.add_argument('--source', default='', choices=['', 'blockscout', 'etherscan'], help='source backend; default etherscan when the chain has no Blockscout name-search host')
    p.add_argument('--queries', default='CoreVault,cVault,StacyVault,CoreVaultV2')
    p.add_argument('--addresses', default='')
    p.add_argument('--max', type=int, default=60, help='max unique candidates to fingerprint')
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-07' / 'stacy_farm' / 'corevault_scan.json'))
    a = p.parse_args()

    global WETH, BLUE, FACTORIES, NATIVE_USD, RPC_ENDPOINTS, CHAINID, SOURCE_BACKEND, CHAIN_NAME
    ch = CHAINS[a.chain]
    CHAIN_NAME = a.chain
    WETH = ch['weth']; BLUE = ch['blue']; FACTORIES = ch['factories']; NATIVE_USD = ch['native_usd']; RPC_ENDPOINTS = ch['rpc']
    CHAINID = ch.get('chainid', 1)
    SOURCE_BACKEND = a.source if a.source else ('blockscout' if ch.get('host') else 'etherscan')
    if not a.host:
        a.host = ch.get('host') or ''
    print('chain', a.chain, 'chainid', CHAINID, 'source', SOURCE_BACKEND, 'host', a.host or '(none)', 'rpc', RPC_ENDPOINTS[0])

    cands = []
    for q in [x for x in a.queries.split(',') if x]:
        cands += name_search(a.host, q)
        time.sleep(0.3)
    for x in [x.strip().lower() for x in a.addresses.split(',') if x.strip()]:
        cands.append(x)
    seen, uniq = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            uniq.append(c)
    uniq = uniq[:a.max]
    print('candidates:', len(uniq))

    results = []
    for i, addr in enumerate(uniq):
        try:
            r = analyze_vault(a.host, addr)
        except Exception as e:
            r = {'address': addr, 'match': False, 'error': str(e)[:120]}
        results.append(r)
        if r.get('match'):
            tag = 'EXPLOITABLE+VALUABLE' if r.get('EXPLOITABLE_AND_VALUABLE') else ('bypassable' if r.get('bypassable') else 'match')
            print('[%2d/%d] %s  %s  reward=%s $%s  bluechip_cheap_pools=%s  %s' % (
                i + 1, len(uniq), addr, tag, r.get('reward_symbol'),
                (round(r['reward_price_usd_est'], 6) if r.get('reward_price_usd_est') else None),
                r.get('bluechip_cheap_pools'), r.get('guard')))
        time.sleep(0.1)

    matches = [r for r in results if r.get('match')]
    hot = [r for r in matches if r.get('EXPLOITABLE_AND_VALUABLE')]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({'host': a.host, 'candidates': len(uniq), 'matches': matches}, indent=1, default=str))
    print('\n=== %d CoreVault-family matches, %d bypassable, %d exploitable+valuable ===' % (
        len(matches), sum(1 for r in matches if r.get('bypassable')), len(hot)))
    for r in sorted(matches, key=lambda r: (-int(bool(r.get('EXPLOITABLE_AND_VALUABLE'))), -(r.get('bluechip_cheap_pools') or 0))):
        print(' %s reward=%-8s $%-10s cheap_bluechip=%s bypass=%s pools=%s' % (
            r['address'], r.get('reward_symbol'),
            (round(r['reward_price_usd_est'], 6) if r.get('reward_price_usd_est') else 'n/a'),
            r.get('bluechip_cheap_pools'), r.get('bypassable'),
            ','.join(p.get('pair', '?') for p in (r.get('pools') or [])[:8])))
    print('written', a.out)


if __name__ == '__main__':
    main()
