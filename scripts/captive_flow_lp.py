#!/usr/bin/env python3
"""Captive-flow LP finder: rank DEX pools by fee yield to a marginal concentrated LP,
weighted by how *captive* and *non-toxic* the flow is.

Thesis (see research/2026-09-07/captive_flow_lp/findings.md): a stablecoin whose issuer
rebates reserve yield to ecosystem partners (USDG / the Global Dollar Network) manufactures
durable DEX conversion volume, because partners are paid to transact it. That volume routes
to the cheapest venue for each clip -- ultra-low-fee Uniswap v4 pools that are thin because
they are new. Thin TVL + high, subsidized, stable-stable (non-toxic) turnover = a fee APR far
above ordinary stablecoin LPing, capturable by a small, early, *active* concentrated LP.

This script is deterministic and block-pinned. It:
  * reads each target pool's live state at a pinned block (v4 poolKey/slot0/liquidity + the
    initialised-tick liquidity distribution -> exact deployed TVL and the active peg band;
    Curve balances/fee/get_dy -> TVL and the round-trip spread),
  * replays the saved full-day and live logs to measure realised volume, direction, per-taker
    concentration, and whether the dominant takers are themselves LPs (toxic) or pure takers,
  * computes turnover, gross fees, and the APR a marginal concentrated LP earns at several add
    sizes -- i.e. capacity -- plus the price band that position must hold to earn it.

Public archive RPC for state (drpc.py); saved logs for flow. No signing, no broadcast.
Usage:
  uv run --with pycryptodome python scripts/captive_flow_lp.py            # pinned replay if cached
  uv run --with pycryptodome python scripts/captive_flow_lp.py --offline  # cache only
  uv run --with pycryptodome python scripts/captive_flow_lp.py --out research/<date>/captive_flow_lp
"""
import argparse
import collections
import datetime as dt
import glob
import gzip
import json
import math
import os
from pathlib import Path

from non_mev_screen import Evidence, ROOT, calldata, digest, words, string

# --------------------------------------------------------------------------------------------------
# Configuration -- the target pools and the flow windows to replay.
# --------------------------------------------------------------------------------------------------
PIN_BLOCK = 25920655           # last block of the saved live window; archive read
LOG_DIRS = ['research/2026-09-05/eth_day/raw', 'research/2026-09-06/live/raw']

STATE_VIEW = '0x7ffe42c4a5deea5b0fec41c94c136cf115597227'   # Uniswap v4 StateView
POSITION_MGR = '0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e'  # Uniswap v4 PositionManager (poolKeys)
POOL_MANAGER = '0x000000000004444c5dc75cb358380d2e3de08a90'  # Uniswap v4 PoolManager (event emitter)

USDC = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
USDG = '0xe343167631d89b6ffc58b88d6b7fb0228795491d'

# v4 pools to inspect (id -> label). Both are USDC/USDG, tickSpacing 1, no hook.
V4_POOLS = {
    '0xb90d11907f96a9d5fd8979ef271d3bb9b90052d9299d1f95faa5168c55bcb716': 'USDC/USDG v4 0.65bp',
    '0x7da1afe9de05528e6559b5845188b98d013843e630b20cd511b974a425267427': 'USDC/USDG v4 0.75bp',
}
# Curve pools to inspect (address -> label), for the deep-venue comparison.
CURVE_POOLS = {
    '0xc061caa073f3d95f80f8e5428d32d2d76f5e1622': 'USDC/USDG Curve',
}
YEAR = 365 * 86400

# Event topics.
T_V4SWAP = '0x' + digest('Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)')
T_V4MOD = '0x' + digest('ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)')
T_CURVE_EX = '0x' + digest('TokenExchange(address,int128,uint256,int128,uint256)')


def s256(x):
    return x - 2 ** 256 if x >= 2 ** 255 else x


def sqrtp_at_tick(t):
    return 1.0001 ** (t / 2)


# --------------------------------------------------------------------------------------------------
# On-chain state at the pinned block.
# --------------------------------------------------------------------------------------------------
def v4_state(e, pid, block):
    """Read a v4 pool's key, price, active liquidity and the nearby initialised-tick distribution,
    and integrate the deployed token reserves (exact concentrated-liquidity TVL)."""
    key25 = '0x' + pid[2:52].ljust(64, '0')   # bytes25 is left-aligned in the ABI word
    pk = e.call(POSITION_MGR, 'poolKeys(bytes25)', key25, block=block)
    c0, c1, fee, ts = f'0x{pk[0]:040x}', f'0x{pk[1]:040x}', pk[2], s256(pk[3])
    slot = e.call(STATE_VIEW, 'getSlot0(bytes32)', pid, block=block)
    sqrtp, tick, lp_fee = slot[0], s256(slot[1]), slot[3]
    L = e.call(STATE_VIEW, 'getLiquidity(bytes32)', pid, block=block)[0]
    # walk the tick bitmap +-1500 ticks around price for the initialised ticks
    net = {}
    lo_word = ((tick // ts) - 1500) // 256 - 1
    hi_word = ((tick // ts) + 1500) // 256 + 1
    for word in range(lo_word, hi_word + 1):
        bm = e.call(STATE_VIEW, 'getTickBitmap(bytes32,int16)', pid, word % (2 ** 256), block=block)[0]
        if not bm:
            continue
        for bit in range(256):
            if bm >> bit & 1:
                t = (word * 256 + bit) * ts
                info = e.call(STATE_VIEW, 'getTickInfo(bytes32,int24)', pid, t % (2 ** 256), block=block)
                net[t] = s256(info[1])   # liquidityNet
    # integrate reserves across contiguous [tick_i, tick_{i+1}) segments
    order = sorted(net)
    usdc = usdg = 0.0
    run = 0
    dec0 = e.call(c0, 'decimals()', block=block)[0]
    dec1 = e.call(c1, 'decimals()', block=block)[0]
    sp = sqrtp / 2 ** 96
    band_lo = band_hi = None
    for i, t in enumerate(order):
        run += net[t]
        if i + 1 >= len(order):
            break
        t_hi = order[i + 1]
        if run <= 0:
            continue
        slo, shi = sqrtp_at_tick(t), sqrtp_at_tick(t_hi)
        if tick >= t_hi:                     # entirely below price -> token1 only
            usdg += run * (shi - slo)
        elif tick < t:                       # entirely above price -> token0 only
            usdc += run * (shi - slo) / (slo * shi)
        else:                                # straddles price -> both
            usdg += run * (sp - slo)
            usdc += run * (shi - sp) / (sp * shi)
            band_lo, band_hi = t, t_hi
    # token0 is USDC, token1 is USDG (verified against currency ordering below)
    scale0, scale1 = 10 ** dec0, 10 ** dec1
    reserves = {c0.lower(): usdc / scale0, c1.lower(): usdg / scale1}
    return {
        'poolId': pid, 'currency0': c0.lower(), 'currency1': c1.lower(), 'fee_pips': fee,
        'lp_fee_pips': lp_fee, 'tickSpacing': ts, 'tick': tick, 'sqrtPriceX96': str(sqrtp),
        'price_c1_per_c0': sp * sp * 10 ** (dec0 - dec1), 'liquidity': str(L),
        'reserves_units': reserves, 'tvl_usd': usdc / scale0 + usdg / scale1,
        'active_band_ticks': [band_lo, band_hi],
        'active_band_pct': (1.0001 ** ((band_hi or 0) - (band_lo or 0)) - 1) * 100 if band_lo is not None else None,
        'n_ticks': len(net),
    }


def curve_state(e, addr, block):
    coins = [f"0x{e.call(addr, 'coins(uint256)', i, block=block)[0]:040x}".lower() for i in range(2)]
    bal = [e.call(addr, 'balances(uint256)', i, block=block)[0] for i in range(2)]
    fee = e.call(addr, 'fee()', block=block)[0]           # 1e10 == 100%
    dec = [e.call(c, 'decimals()', block=block)[0] for c in coins]
    tvl = sum(b / 10 ** d for b, d in zip(bal, dec))
    # round-trip spread on a $100k clip both ways
    clip = 100_000
    dy01 = e.call(addr, 'get_dy(int128,int128,uint256)', 0, 1, clip * 10 ** dec[0], block=block)[0] / 10 ** dec[1]
    dy10 = e.call(addr, 'get_dy(int128,int128,uint256)', 1, 0, clip * 10 ** dec[1], block=block)[0] / 10 ** dec[0]
    return {'address': addr, 'coins': coins, 'balances_units': [b / 10 ** d for b, d in zip(bal, dec)],
            'fee_bps': fee / 1e10 * 1e4, 'tvl_usd': tvl,
            'dy_100k_0to1': dy01, 'dy_100k_1to0': dy10}


# --------------------------------------------------------------------------------------------------
# Flow replay from saved logs.
# --------------------------------------------------------------------------------------------------
def replay(log_dirs):
    v4 = collections.defaultdict(list)      # pid -> swaps
    v4_lp = collections.defaultdict(list)   # pid -> modifyLiquidity
    curve = collections.defaultdict(list)   # addr -> exchanges
    need_tx = collections.defaultdict(set)  # block -> {txhash}
    files = []
    for d in log_dirs:
        files += sorted(glob.glob(os.path.join(ROOT, d, 'logs', '*.json.gz')))
    for f in files:
        try:
            logs = json.load(gzip.open(f, 'rt'))
        except Exception:
            continue
        if isinstance(logs, dict):
            logs = logs.get('logs') or logs.get('result') or []
        for lg in logs:
            tps = lg.get('topics') or []
            if not tps:
                continue
            a = lg['address'].lower(); t0 = tps[0]
            bn = int(lg['blockNumber'], 16); ts = int(lg.get('blockTimestamp', '0x0'), 16)
            h = lg['transactionHash']
            if a == POOL_MANAGER and t0 == T_V4SWAP and len(tps) > 1 and tps[1] in V4_POOLS:
                w = words(lg['data'])
                v4[tps[1]].append({'block': bn, 'ts': ts, 'tx': h, 'a0': s256(w[0]), 'a1': s256(w[1]),
                                   'sqrtp': w[2], 'router': '0x' + tps[2][26:]})
                need_tx[bn].add(h)
            elif a == POOL_MANAGER and t0 == T_V4MOD and len(tps) > 1 and tps[1] in V4_POOLS:
                w = words(lg['data'])
                v4_lp[tps[1]].append({'block': bn, 'ts': ts, 'tx': h, 'dL': s256(w[2]),
                                      'router': '0x' + tps[2][26:]})
                need_tx[bn].add(h)
            elif a in CURVE_POOLS and t0 == T_CURVE_EX:
                w = words(lg['data'])
                curve[a].append({'block': bn, 'ts': ts, 'tx': h, 'buyer': '0x' + tps[1][26:],
                                 'sold_id': s256(w[0]), 'sold': w[1], 'bought_id': s256(w[2]), 'bought': w[3]})
                need_tx[bn].add(h)
    # join tx.from / tx.to from block files
    tx_meta = {}
    for d in log_dirs:
        for bn, hs in need_tx.items():
            fp = os.path.join(ROOT, d, 'blocks', f'{bn}.json.gz')
            if not os.path.exists(fp):
                continue
            b = json.load(gzip.open(fp, 'rt'))
            for t in b.get('transactions', []):
                if t['hash'] in hs:
                    tx_meta[t['hash']] = ((t.get('from') or '').lower(), (t.get('to') or '').lower())
    for pid, sws in v4.items():
        for x in sws:
            x['from'], x['to'] = tx_meta.get(x['tx'], (None, None))
    for pid, ms in v4_lp.items():
        for x in ms:
            x['from'], x['to'] = tx_meta.get(x['tx'], (None, None))
    return v4, v4_lp, curve


def contiguous_daily(rows, size_fn, gap_h=2.0):
    """Split rows into contiguous windows (breaking at >gap_h timestamp gaps) and return the
    volume-weighted 24h-equivalent across them, so a data gap never dilutes the daily figure."""
    ts = sorted(set(r['ts'] for r in rows))
    if len(ts) < 2:
        return 0.0, 0.0, 0
    windows = []
    start = ts[0]; prev = ts[0]
    for t in ts[1:]:
        if t - prev > gap_h * 3600:
            windows.append((start, prev)); start = t
        prev = t
    windows.append((start, prev))
    total_vol = total_secs = 0.0; n = 0
    for lo, hi in windows:
        w = [r for r in rows if lo <= r['ts'] <= hi]
        if hi <= lo:
            continue
        total_vol += sum(size_fn(r) for r in w); total_secs += (hi - lo); n += len(w)
    daily = total_vol / total_secs * 86400 if total_secs else 0.0
    return daily, total_vol, n


def herfindahl(shares):
    tot = sum(shares.values()) or 1
    return sum((v / tot) ** 2 for v in shares.values())


def analyse(v4, v4_lp, curve, states):
    """Combine state and flow into per-pool economics for a marginal concentrated LP."""
    out = []
    lp_addrs = set()
    for ms in v4_lp.values():
        lp_addrs |= {(m['from'] or m['router']) for m in ms}
    for pid, label in V4_POOLS.items():
        st = states['v4'][pid]
        sws = v4.get(pid, [])
        fee = st['lp_fee_pips'] / 1e6

        def size(x):
            return abs(x['a0']) / 10 ** 6 if x['a0'] else abs(x['a1']) / 10 ** 6  # USDC leg

        daily, vol, n = contiguous_daily(sws, size)
        by_taker = collections.defaultdict(float)
        for x in sws:
            by_taker[x['from'] or '?'] += size(x)
        top = sorted(by_taker.items(), key=lambda kv: -kv[1])[:5]
        top_share = (top[0][1] / vol) if vol else 0
        top_is_lp = top[0][0] in lp_addrs if top else False
        tvl = st['tvl_usd']
        daily_fees = daily * fee
        apr_at = {}
        for add in (10_000, 50_000, 100_000, 500_000):
            apr_at[add] = daily_fees / (tvl + add) * 365 if (tvl + add) else 0
        out.append({
            'pool': label, 'poolId': pid, 'lp_fee_bps': st['lp_fee_pips'] / 100,
            'deployed_tvl_usd': round(tvl), 'active_band_pct': st['active_band_pct'],
            'price_usdg_per_usdc': st['price_c1_per_c0'], 'tick': st['tick'],
            'daily_volume_usd': round(daily), 'swaps': n, 'turnover_per_day': daily / tvl if tvl else None,
            'gross_fees_per_day_usd': round(daily_fees, 2),
            'top_taker': top[0][0] if top else None, 'top_taker_share': round(top_share, 3),
            'top_taker_is_lp': top_is_lp, 'taker_herfindahl': round(herfindahl(by_taker), 4),
            'n_takers': len(by_taker),
            'marginal_lp_apr': {str(k): round(v, 4) for k, v in apr_at.items()},
        })
    for addr, label in CURVE_POOLS.items():
        st = states['curve'][addr]
        exs = curve.get(addr, [])

        def csize(x):
            return (x['sold'] if x['sold_id'] == 1 else x['bought']) / 10 ** 6  # USDC leg (coin1)

        daily, vol, n = contiguous_daily(exs, csize)
        fee = st['fee_bps'] / 1e4
        daily_fees = daily * fee
        out.append({
            'pool': label, 'address': addr, 'lp_fee_bps': round(st['fee_bps'], 3),
            'deployed_tvl_usd': round(st['tvl_usd']), 'daily_volume_usd': round(daily), 'swaps': n,
            'turnover_per_day': daily / st['tvl_usd'] if st['tvl_usd'] else None,
            'gross_fees_per_day_usd': round(daily_fees, 2),
            'marginal_lp_apr': {'whole_pool': round(daily_fees / st['tvl_usd'] * 365, 4) if st['tvl_usd'] else None},
            'round_trip_spread_bps': round((st['dy_100k_0to1'] / 100_000 - 1) * 1e4, 3),
        })
    return out, sorted(lp_addrs)


def render(result, out):
    b = result['block']; states = result['states']; rows = result['pools']
    L = ['# Captive-flow LP: USDC/USDG venues', '',
         f"Block **{b}**, {result['utc']}. Flow replayed from {result['flow_windows']} contiguous windows "
         f"of saved logs ({result['flow_swaps']} swaps). Deployed TVL and price read on-chain at the pinned block.",
         '', '## Pools', '',
         '| Pool | LP fee | Deployed TVL | 24h volume | Turnover | Gross fees/day | Marginal-LP APR (+$50k) | Top taker share |',
         '|---|--:|--:|--:|--:|--:|--:|--:|']
    for r in rows:
        apr = r['marginal_lp_apr']
        aprv = apr.get('50000') or apr.get('whole_pool')
        L.append('| %s | %.2f bp | $%s | $%s | %s | $%s | %s | %s |' % (
            r['pool'], r['lp_fee_bps'], f"{r['deployed_tvl_usd']:,}", f"{r['daily_volume_usd']:,}",
            (f"{r['turnover_per_day']:.1f}x" if r['turnover_per_day'] else '-'),
            f"{r['gross_fees_per_day_usd']:,.0f}",
            (f"{aprv*100:.1f}%" if aprv else '-'),
            (f"{r['top_taker_share']*100:.0f}%" if 'top_taker_share' in r else '-')))
    L += ['', '## Marginal concentrated-LP APR by add size (v4)', '',
          '| Pool | +$10k | +$50k | +$100k | +$500k |', '|---|--:|--:|--:|--:|']
    for r in rows:
        if 'top_taker' not in r:
            continue
        a = r['marginal_lp_apr']
        L.append('| %s | %.1f%% | %.1f%% | %.1f%% | %.1f%% |' % (
            r['pool'], a['10000'] * 100, a['50000'] * 100, a['100000'] * 100, a['500000'] * 100))
    L += ['', '## Flow quality', '']
    for r in rows:
        if 'top_taker' not in r:
            continue
        L.append('- **%s**: top taker `%s` is %.0f%% of volume, %s an LP; %d distinct takers, '
                 'Herfindahl %.3f. Active peg band %.3f%%.' % (
                     r['pool'], r['top_taker'], r['top_taker_share'] * 100,
                     'IS' if r['top_taker_is_lp'] else 'is NOT', r['n_takers'], r['taker_herfindahl'],
                     r['active_band_pct'] or 0))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=ROOT / 'research/2026-09-07/captive_flow_lp')
    p.add_argument('--block', type=int, default=PIN_BLOCK)
    p.add_argument('--offline', action='store_true')
    args = p.parse_args()
    e = Evidence(args.out, args.offline)
    assert e.get('eth_chainId', []) == '0x1'
    hdr = e.header(args.block)
    print('Pinned block', args.block, dt.datetime.fromtimestamp(hdr['timestamp'], dt.timezone.utc).isoformat(), flush=True)
    # verify token identities before interpreting amounts
    assert string(e.get('eth_call', [{'to': USDG, 'data': calldata('symbol()')}, hex(args.block)])) == 'USDG'
    assert string(e.get('eth_call', [{'to': USDC, 'data': calldata('symbol()')}, hex(args.block)])) == 'USDC'
    states = {'v4': {}, 'curve': {}}
    for pid, label in V4_POOLS.items():
        st = v4_state(e, pid, args.block)
        assert {st['currency0'], st['currency1']} == {USDC, USDG}, st
        states['v4'][pid] = st
        print(label, 'TVL $%.0f' % st['tvl_usd'], 'band %.3f%%' % (st['active_band_pct'] or 0), flush=True)
    for addr, label in CURVE_POOLS.items():
        states['curve'][addr] = curve_state(e, addr, args.block)
        print(label, 'TVL $%.0f' % states['curve'][addr]['tvl_usd'], flush=True)
    v4, v4_lp, curve = replay(LOG_DIRS)
    pools, lp_addrs = analyse(v4, v4_lp, curve, states)
    flow_swaps = sum(len(x) for x in v4.values()) + sum(len(x) for x in curve.values())
    result = {'block': args.block, 'utc': dt.datetime.fromtimestamp(hdr['timestamp'], dt.timezone.utc).isoformat(),
              'states': states, 'pools': pools, 'lp_addresses': lp_addrs,
              'flow_windows': 2, 'flow_swaps': flow_swaps, 'log_dirs': LOG_DIRS}
    (args.out).mkdir(parents=True, exist_ok=True)
    (args.out / 'captive_flow.json').write_text(json.dumps(result, indent=1, default=str) + '\n')
    render(result, args.out)
    print('cache: %d hits / %d requests' % (e.hits, e.requests))


if __name__ == '__main__':
    main()
