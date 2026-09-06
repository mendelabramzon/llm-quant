#!/usr/bin/env python3
"""Scan live pools for the three signatures of "broken math" — the conditions that let value be extracted from a pool
because its accounting is inconsistent with reality, rather than by trading against it.

    1. rate-cache staleness   Balancer v2 rate-scaled pools price a rate-bearing token by a CACHED rate; if the live
                              rate provider has moved past the cache, the pool misprices the token until refreshed.
    2. reserve/balance drift  Uniswap-v2-style pairs cache reserves; a rebasing or fee-on-transfer token makes
                              balanceOf(pair) diverge from the cached reserve, and anyone can skim() the excess.
    3. round-trip leak        A correct AMM always returns strictly less than the input on A->B->A (it charges a fee).
                              A pool that returns MORE has a rounding/invariant bug.

Read-only. Point it at a mainnet RPC (a local anvil fork avoids public rate limits and lets you re-run freely):

    anvil --fork-url https://ethereum-rpc.publicnode.com --silent &
    uv run --with pycryptodome python scripts/pool_math_scan.py --rpc http://127.0.0.1:8545 \
        --curve-pools research/2026-09-06/live/pools.json --balancer-pools <bal_pools.json>

The finding of the 2026-09-06 run is written up in research/2026-09-06/strategy/broken_math.md: exploitable broken math
does not persist at size — searchers drain a leaking pool to dust and liquidity migrates (rebasing -> wrapped tokens),
so the signatures show up only in abandoned pools worth cents.
"""
import argparse
import json
import sys

from Crypto.Hash import keccak

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from drpc import rpc as _rpc, Revert  # noqa: E402

VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
UNIV2_FACTORY = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
SUSHI_FACTORY = '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac'
REBASING = {  # tokens whose balance drifts from a v2 pair's cached reserve
    'stETH': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84',
    'aEthUSDC': '0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c', 'aEthWETH': '0x4d5F47FA6A74757f35C14fD3a6Ef8E3c9BC514E8',
    'AMPL': '0xD46bA6D942050d489DBd938a2C909A5d5039A161', 'PAXG': '0x45804880De22913dAFE09f4980848ECE6EcbAf78',
}
PARTNERS = {'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
            'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7', 'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
            'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'}
_ep = ['http://127.0.0.1:8545']


def sel(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()[:8]


def ea(a):
    return a[2:].lower().rjust(64, '0')


def eu(v):
    return hex(int(v))[2:].rjust(64, '0')


def ei(v):
    return format(int(v) & (2 ** 256 - 1), '064x')


def call(to, data):
    try:
        return _rpc('eth_call', [{'to': to, 'data': data}, 'latest'], endpoints=_ep)
    except Revert:
        return None


def W(x, i=0):
    return int(x[2 + i * 64:2 + (i + 1) * 64], 16) if x and x != '0x' else None


def addrs(x):
    if not x:
        return []
    n = W(x, 1)
    return ['0x' + x[2 + (2 + i) * 64:2 + (3 + i) * 64][-40:] for i in range(n)]


def sym(a):
    r = call(a, sel('symbol()'))
    if not r:
        return a[:10]
    try:
        off = W(r, 0) // 32
        ln = W(r, off)
        return bytes.fromhex(r[2 + (off + 1) * 64:2 + (off + 1) * 64 + ln * 2]).decode('utf-8', 'ignore')
    except Exception:
        return a[:10]


def dec(t):
    r = call(t, sel('decimals()'))
    v = W(r) if r else None
    return v if v else 18


def scan_rate_caches(pools):
    ts = int(_rpc('eth_getBlockByNumber', ['latest', False], endpoints=_ep)['timestamp'], 16)
    hits = []
    for p in pools:
        pid = call(p, sel('getPoolId()'))
        rps = call(p, sel('getRateProviders()'))
        if not pid or not rps:
            continue
        provs = addrs(rps)
        if not any(int(x, 16) for x in provs):
            continue
        pt = call(VAULT, sel('getPoolTokens(bytes32)') + pid[2:])
        toks = addrs('0x' + pt[2:]) if pt else []
        for i, prov in enumerate(provs):
            if int(prov, 16) == 0 or i >= len(toks):
                continue
            cache = call(p, sel('getTokenRateCache(address)') + ea(toks[i])) or call(p, sel('getPriceRateCache(address)') + ea(toks[i]))
            live = call(prov, sel('getRate()'))
            if not cache or not live or not W(cache, 0):
                continue
            gap = (W(live, 0) - W(cache, 0)) / W(cache, 0)
            if abs(gap) > 1e-5:
                hits.append({'pool': p, 'token': sym(toks[i]), 'cached': W(cache, 0) / 1e18, 'live': W(live, 0) / 1e18,
                             'gap_bps': gap * 1e4, 'stale': W(cache, 3) is not None and ts > W(cache, 3)})
    return hits


def scan_v2_skim():
    hits = []
    for rn, ra in REBASING.items():
        for pn, pa in PARTNERS.items():
            for fn, fa in (('UniV2', UNIV2_FACTORY), ('Sushi', SUSHI_FACTORY)):
                r = call(fa, sel('getPair(address,address)') + ea(ra) + ea(pa))
                p = ('0x' + r[-40:]) if r and int('0x' + r[-40:], 16) else None
                if not p:
                    continue
                t0 = call(p, sel('token0()'))
                res = call(p, sel('getReserves()'))
                if not t0 or not res:
                    continue
                reserve = W(res, 0) if ('0x' + t0[-40:]).lower() == ra.lower() else W(res, 1)
                bal = W(call(ra, sel('balanceOf(address)') + ea(p)))
                if bal is None or reserve is None or bal == 0:
                    continue
                skim = bal - reserve
                if skim > 0 and skim / bal > 1e-7:
                    hits.append({'venue': fn, 'pair': '%s/%s' % (rn, pn), 'pool': p, 'reserve': reserve / 1e18,
                                 'actual': bal / 1e18, 'skimmable': skim / 1e18, 'bps_of_pool': 1e4 * skim / bal})
    return hits


def scan_curve_roundtrip(pools):
    gd = sel('get_dy(int128,int128,uint256)')
    leaks, tested = [], 0
    for p, toks in pools:
        if not (toks and len(toks) == 2 and all(toks)):
            continue
        if not call(p, sel('coins(uint256)') + eu(0)):
            continue
        tested += 1
        d0 = dec(toks[0])
        dx = 1000 * 10 ** d0
        dy = call(p, gd + ei(0) + ei(1) + eu(dx))
        if not dy or not W(dy):
            continue
        back = call(p, gd + ei(1) + ei(0) + eu(W(dy)))
        if not back or not W(back):
            continue
        if W(back) / dx > 1.0:
            leaks.append({'pool': p, 'ratio': W(back) / dx})
    return leaks, tested


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rpc', default='http://127.0.0.1:8545')
    ap.add_argument('--balancer-pools', help='JSON list of Balancer v2 pool addresses')
    ap.add_argument('--curve-pools', help='pools.json from the live scan (address -> {tokens:[...]})')
    args = ap.parse_args()
    _ep[0] = args.rpc

    print('== 1. Balancer v2 rate-cache staleness ==')
    if args.balancer_pools:
        hits = scan_rate_caches(json.load(open(args.balancer_pools)))
        for h in sorted(hits, key=lambda h: -abs(h['gap_bps']))[:25]:
            print('  %s %-10s cached %.6f live %.6f gap %+.2f bps %s' % (h['pool'], h['token'], h['cached'], h['live'], h['gap_bps'], 'STALE' if h['stale'] else ''))
        print('  %d pools mispricing a token by >0.1 bp' % len(hits))
    else:
        print('  (skipped: pass --balancer-pools)')

    print('\n== 2. Uniswap-v2 / Sushi rebasing reserve-vs-balance drift (skimmable) ==')
    hits = scan_v2_skim()
    for h in sorted(hits, key=lambda h: -h['skimmable']):
        print('  %s %s %s: reserve %.6f actual %.6f skimmable %.6f (%.1f bps of pool)' % (h['venue'], h['pair'], h['pool'], h['reserve'], h['actual'], h['skimmable'], h['bps_of_pool']))
    print('  %d pairs with skimmable excess' % len(hits))

    print('\n== 3. Curve round-trip leaks (A->B->A > input) ==')
    if args.curve_pools:
        raw = json.load(open(args.curve_pools))
        pools = [(p, v['tokens']) for p, v in raw.items() if len(p) == 42 and v.get('tokens')]
        leaks, tested = scan_curve_roundtrip(pools)
        for l in leaks:
            print('  LEAK %s ratio %.6f' % (l['pool'], l['ratio']))
        print('  %d leaks of %d pools tested' % (len(leaks), tested))
    else:
        print('  (skipped: pass --curve-pools)')


if __name__ == '__main__':
    main()
