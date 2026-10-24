#!/usr/bin/env python3
"""Liquity v2 stability pools: the realised return of a passive, pro-rata liquidation buyer.

Why. Every strategy this repo has kept is a rent paid by someone with a non-price motive and collected without a race.
A Liquity v2 stability pool (SP) is the cleanest version of that shape found so far:

  * borrowers pay an interest rate they set themselves, and 75% of it is minted to the branch's SP;
  * a liquidation burns SP BOLD against the trove's debt and hands the SP its collateral, worth ~105% (110% minimum
    collateral ratio less the 5% penalty cap), pro-rata to every depositor; the keeper who calls `liquidate()` gets
    only the gas compensation, so the race is for a gas refund, not for the discount;
  * entering an hour late misses only the liquidations of that hour.

This module rebuilds, from logs alone, the return per BOLD deposited on each branch since the May 2025 redeployment:

    collect  — SP total deposits, BOLD minted to the SP (the yield), and TroveManager `Liquidation` events
    analyze  — daily return per BOLD: yield + collateral gains sold at the next hour's price − BOLD burned

Collateral is valued as an hourly taker would sell it: the liquidation's own oracle price, moved by Binance ETHUSDT from
the liquidation hour to the next hour's close (LST/ETH ratios do not move in an hour). Output goes to
research/2026-10-23/stability_pools/.

    uv run --with pycryptodome python scripts/stability_pool.py collect
    python3 scripts/stability_pool.py analyze
"""
import argparse
import bisect
import json
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dislocation_history import keccak, sel  # noqa: E402
from live_rpc import RPC, word  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / '2026-10-23' / 'stability_pools'

BOLD = '0x6440f144b7e50d6a8439336510312d2f54beb01d'
START_BLOCK = 22_516_000          # TroveManager[0] created at 22,516,078 (2025-05-19)
STEP = 10_000                     # Infura's getLogs block-range cap
BRANCHES = {
    'WETH': {'tm': '0x7bcb64b2c9206a5b699ed43363f6f98d4776cf5a', 'sp': '0x5721cbbd64fc7ae3ef44a0a3f9a790a9264cf9bf'},
    'wstETH': {'tm': '0xa2895d6a3bf110561dfe4b71ca539d84e1928b22', 'sp': '0x9502b7c397e9aa22fe9db7ef7daf21cd2aebe56b'},
    'rETH': {'tm': '0xb2b2abeb5c357a234363ff5d180912d319e3e19e', 'sp': '0xd442e41019b7f5c4dd78f50dc03726c446148695'},
}
T_LIQ = keccak('Liquidation(uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256)')
T_DEP = keccak('StabilityPoolBoldBalanceUpdated(uint256)')
T_XFER = keccak('Transfer(address,address,uint256)')
T_OP = keccak('TroveOperation(uint256,uint8,uint256,uint256,uint256,int256,uint256,int256)')
T_RED = keccak('Redemption(uint256,uint256,uint256,uint256,uint256,uint256)')
T_FEE = keccak('RedemptionFeePaidToTrove(uint256,uint256)')
ZERO_T = '0x' + '0' * 64


def _t(addr):
    return '0x' + addr[2:].rjust(64, '0')


def get_logs(rpc, flt, lo, hi, depth=0):
    """All logs for one filter over [lo, hi], in 10k-block chunks; a chunk over the result cap is halved, any other
    error retried (splitting on every error turns a rate limit into a storm of one-block calls)."""
    spans = [(a, min(a + STEP - 1, hi)) for a in range(lo, hi + 1, STEP)]
    out = []
    for i in range(0, len(spans), 10):
        part = spans[i:i + 10]
        for attempt in range(4):
            res = rpc.batch([('eth_getLogs', [dict(flt, fromBlock=hex(a), toBlock=hex(b))]) for a, b in part],
                            allow_errors=True)
            bad = [(ab, r) for ab, r in zip(part, res) if not isinstance(r, list)]
            for ab, r in zip(part, res):
                if isinstance(r, list):
                    out.extend(r)
            capped = [ab for ab, r in bad if 'more than' in str(r) or '10000' in str(r) or 'range' in str(r)]
            for a, b in capped:
                m = (a + b) // 2
                out.extend(get_logs(rpc, flt, a, m, depth + 1) + get_logs(rpc, flt, m + 1, b, depth + 1))
            part = [ab for ab, r in bad if ab not in capped]
            if not part:
                break
            print('  retry', part[:2], str(bad[0][1])[:120], flush=True)
            time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError(f'getLogs failed for {part[:3]}')
        if depth == 0 and i % 100 == 0:
            print(f'  {flt["address"][:10]} block {part[0][0] if part else spans[i][0]:,} logs {len(out):,}', flush=True)
    return out


def block_times(rpc, lo, hi, every=100_000):
    pts = list(range(lo, hi, every)) + [hi]
    res = rpc.batch([('eth_getBlockByNumber', [hex(b), False]) for b in pts])
    return [(b, int(r['timestamp'], 16)) for b, r in zip(pts, res)]


def interp(times, block):
    bs = [b for b, _ in times]
    i = min(max(bisect.bisect_left(bs, block), 1), len(bs) - 1)
    (b0, t0), (b1, t1) = times[i - 1], times[i]
    return t0 + (t1 - t0) * (block - b0) / max(b1 - b0, 1)


def collect(args):
    rpc = RPC(max_credits=4_000_000)
    head = int(rpc.call('eth_blockNumber', []), 16)
    OUT.mkdir(parents=True, exist_ok=True)
    times = block_times(rpc, START_BLOCK, head)
    data = {'head': head, 'times': times, 'branches': {}}
    for name, br in BRANCHES.items():
        sp, tm = br['sp'], br['tm']
        liq = get_logs(rpc, {'address': tm, 'topics': [T_LIQ]}, START_BLOCK, head)
        dep = get_logs(rpc, {'address': sp, 'topics': [T_DEP]}, START_BLOCK, head)
        mint = get_logs(rpc, {'address': BOLD, 'topics': [T_XFER, ZERO_T, _t(sp)]}, START_BLOCK, head)
        rows = {'liq': [], 'dep': [], 'mint': []}
        for lg in liq:
            d = lg['data']
            rows['liq'].append({'block': int(lg['blockNumber'], 16), 'tx': lg['transactionHash'],
                                'debt_sp': word(d, 0) / 1e18, 'debt_redist': word(d, 1) / 1e18,
                                'coll_gas': word(d, 3) / 1e18, 'coll_sp': word(d, 4) / 1e18,
                                'coll_redist': word(d, 5) / 1e18, 'coll_surplus': word(d, 6) / 1e18,
                                'price': word(d, 9) / 1e18})
        for lg in dep:
            rows['dep'].append({'block': int(lg['blockNumber'], 16), 'li': int(lg['logIndex'], 16),
                                'total': word(lg['data'], 0) / 1e18})
        for lg in mint:
            rows['mint'].append({'block': int(lg['blockNumber'], 16), 'amt': word(lg['data'], 0) / 1e18})
        for k, logs in (('liq', liq), ('dep', dep), ('mint', mint)):
            for r, lg in zip(rows[k], logs):
                r['ts'] = int(lg['blockTimestamp'], 16) if lg.get('blockTimestamp') else interp(times, r['block'])
        data['branches'][name] = rows
        print(name, {k: len(v) for k, v in rows.items()}, flush=True)
    (OUT / 'logs.json').write_text(json.dumps(data))
    print('credits', rpc.stats())


SUSDS = '0xa3931d71877c0e7a3148cb7eb4463524fec27fbd'
CURVE_BOLD_USDC = '0xefc6516323fbd28e80b85a497b65a86243a54b3e'   # coins: 0 BOLD, 1 USDC


def _w(v):
    return hex(int(v))[2:].rjust(64, '0')


def chain_daily(args):
    """One archive sample per UTC day at the first block after 00:00: sUSDS NAV (the savings rate actually paid) and
    BOLD's executable price on its deepest pool, both ways, at $100k and $1M."""
    data = json.loads((OUT / 'logs.json').read_text())
    times = data['times']
    rpc = RPC(max_credits=1_000_000)
    d0 = int(times[0][1] // 86400 + 1)
    d1 = int(times[-1][1] // 86400)
    days = list(range(d0, d1 + 1))

    def block_at(ts):
        bs = [b for b, _ in times]
        ts_ = [t for _, t in times]
        i = min(max(bisect.bisect_left(ts_, ts), 1), len(ts_) - 1)
        return int(bs[i - 1] + (bs[i] - bs[i - 1]) * (ts - ts_[i - 1]) / (ts_[i] - ts_[i - 1])) + 1

    calls, keys = [], []
    for d in days:
        b = hex(block_at(d * 86400))
        for k, to, data_ in (('susds', SUSDS, sel('convertToAssets(uint256)') + _w(1e18)),
                             ('sell100k', CURVE_BOLD_USDC, sel('get_dy(int128,int128,uint256)') + _w(0) + _w(1) + _w(1e5 * 1e18)),
                             ('sell1m', CURVE_BOLD_USDC, sel('get_dy(int128,int128,uint256)') + _w(0) + _w(1) + _w(1e6 * 1e18)),
                             ('buy1m', CURVE_BOLD_USDC, sel('get_dy(int128,int128,uint256)') + _w(1) + _w(0) + _w(1e6 * 1e6))):
            calls.append(('eth_call', [{'to': to, 'data': data_}, b]))
            keys.append((d, k))
    out = defaultdict(dict)
    for i in range(0, len(calls), 50):
        res = rpc.batch(calls[i:i + 50], allow_errors=True)
        for (d, k), r in zip(keys[i:i + 50], res):
            if isinstance(r, str) and r.startswith('0x') and len(r) >= 66:
                v = int(r[2:66], 16)
                out[day(d * 86400)][k] = {'susds': v / 1e18, 'sell100k': v / 1e6 / 1e5, 'sell1m': v / 1e6 / 1e6,
                                          'buy1m': v / 1e18 / 1e6}[k]
    (OUT / 'chain_daily.json').write_text(json.dumps(out, indent=0))
    print(len(out), 'days', rpc.stats())


def troves(args):
    """Every TroveOperation and Redemption on each branch: the rates redemptions reached, and every rate borrowers set
    (opens, adjustments), which together price the redemption risk of a low-rate trove."""
    from live_rpc import sword
    rpc = RPC(max_credits=3_000_000)
    head = int(rpc.call('eth_blockNumber', []), 16)
    out = {}
    for name, br in BRANCHES.items():
        ops = get_logs(rpc, {'address': br['tm'], 'topics': [T_OP]}, START_BLOCK, head)
        reds = get_logs(rpc, {'address': br['tm'], 'topics': [T_RED]}, START_BLOCK, head)
        fees = get_logs(rpc, {'address': br['tm'], 'topics': [T_FEE]}, START_BLOCK, head)
        rows = {'ops': [], 'red': [], 'fee': []}
        for lg in fees:
            rows['fee'].append({'tx': lg['transactionHash'], 'trove': lg['topics'][1] if len(lg['topics']) > 1 else
                                '0x' + lg['data'][2:66], 'fee_coll': word(lg['data'], len(lg['topics']) == 1) / 1e18})
        for lg in ops:
            d = lg['data']
            rows['ops'].append({'block': int(lg['blockNumber'], 16), 'ts': int(lg['blockTimestamp'], 16),
                                'tx': lg['transactionHash'], 'trove': lg['topics'][1], 'op': word(d, 0),
                                'rate': word(d, 1) / 1e18, 'upfront': word(d, 3) / 1e18,
                                'debt_chg': sword(d, 4) / 1e18, 'coll_chg': sword(d, 6) / 1e18})
        for lg in reds:
            d = lg['data']
            rows['red'].append({'block': int(lg['blockNumber'], 16), 'ts': int(lg['blockTimestamp'], 16),
                                'tx': lg['transactionHash'], 'attempted': word(d, 0) / 1e18, 'actual': word(d, 1) / 1e18,
                                'coll_sent': word(d, 2) / 1e18, 'coll_fee': word(d, 3) / 1e18, 'price': word(d, 4) / 1e18,
                                'redemption_price': word(d, 5) / 1e18})
        out[name] = rows
        print(name, len(rows['ops']), 'ops', len(rows['red']), 'redemptions', len(rows['fee']), 'fees', flush=True)
    (OUT / 'troves.json').write_text(json.dumps(out))
    print(rpc.stats())


def _post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def funding(args):
    """ETH perp funding paid to shorts: Hyperliquid (hourly) and Binance (8-hourly), since the SP history starts; and
    the wstETH NAV from DefiLlama's Lido chart (staking APR)."""
    start_ms = 1747612800 * 1000      # 2025-05-19
    hl, t = [], start_ms
    while True:
        k = _post('https://api.hyperliquid.xyz/info', {'type': 'fundingHistory', 'coin': 'ETH', 'startTime': t})
        if not k:
            break
        hl += [(x['time'] // 1000, float(x['fundingRate'])) for x in k]
        if len(k) < 500:
            break
        t = k[-1]['time'] + 1
        time.sleep(0.3)
    bn, t = [], start_ms
    while True:
        url = f'https://fapi.binance.com/fapi/v1/fundingRate?symbol=ETHUSDT&startTime={t}&limit=1000'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as r:
            k = json.loads(r.read())
        bn += [(x['fundingTime'] // 1000, float(x['fundingRate'])) for x in k]
        if len(k) < 1000:
            break
        t = k[-1]['fundingTime'] + 1
    with urllib.request.urlopen('https://yields.llama.fi/chart/747c1d2a-c668-4682-b9f9-296708a3dd90', timeout=30) as r:
        lido = [(x['timestamp'][:10], x['apy']) for x in json.loads(r.read())['data']]
    (OUT / 'funding.json').write_text(json.dumps({'hl': hl, 'binance': bn, 'lido_apr': lido}))
    print('hl', len(hl), 'binance', len(bn), 'lido', len(lido))


def binance_hourly(symbol, start_ms):
    out, t = [], start_ms
    while True:
        url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&startTime={t}&limit=1000'
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as r:
            k = json.loads(r.read())
        out += [(int(x[0]) // 1000, float(x[1]), float(x[4])) for x in k]
        if len(k) < 1000:
            return out
        t = int(k[-1][0]) + 3_600_000
        time.sleep(0.2)


def day(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime('%Y-%m-%d')


def analyze(args):
    data = json.loads((OUT / 'logs.json').read_text())
    t0 = min(r['ts'] for b in data['branches'].values() for k in b.values() for r in k)
    kl_path = OUT / 'ethusdt_1h.json'
    if not kl_path.exists():
        kl_path.write_text(json.dumps(binance_hourly('ETHUSDT', int(t0 // 3600 * 3600 * 1000))))
    kl = {h: (o, c) for h, o, c in json.loads(kl_path.read_text())}

    def eth_move(ts):
        """Price ratio from the liquidation instant (open of its hour, conservative-neutral) to the next hour's close."""
        h = int(ts // 3600 * 3600)
        if h not in kl or h + 3600 not in kl:
            return 1.0
        return kl[h + 3600][1] / kl[h][0]

    summary = {}
    for name, b in data['branches'].items():
        deps = sorted(b['dep'], key=lambda r: (r['block'], r['li']))
        dep_ts = [r['ts'] for r in deps]

        def deposits_at(ts):
            i = bisect.bisect_right(dep_ts, ts) - 1
            return deps[i]['total'] if i >= 0 else 0.0

        daily = defaultdict(lambda: {'yield': 0.0, 'gain': 0.0, 'gain_oracle': 0.0, 'burn': 0.0, 'n_liq': 0})
        for m in b['mint']:
            daily[day(m['ts'])]['yield'] += m['amt']
        for lq in b['liq']:
            d = daily[day(lq['ts'])]
            d['burn'] += lq['debt_sp']
            d['gain_oracle'] += lq['coll_sp'] * lq['price']
            d['gain'] += lq['coll_sp'] * lq['price'] * eth_move(lq['ts'])
            d['n_liq'] += 1
        # average deposits per day: sample hourly
        days = sorted({day(t) for t in range(int(t0), int(data['times'][-1][1]), 3600)})
        rows = []
        for dd in days:
            ts0 = datetime.strptime(dd, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp()
            avg = sum(deposits_at(ts0 + h * 3600 + 1800) for h in range(24)) / 24
            x = daily.get(dd, {'yield': 0.0, 'gain': 0.0, 'gain_oracle': 0.0, 'burn': 0.0, 'n_liq': 0})
            rows.append({'day': dd, 'deposits': avg, **x,
                         'r_yield': x['yield'] / avg if avg > 1e5 else None,
                         'r_liq': (x['gain'] - x['burn']) / avg if avg > 1e5 else None})
        summary[name] = rows
    (OUT / 'daily.json').write_text(json.dumps(summary, indent=0))
    for name, rows in summary.items():
        ok = [r for r in rows if r['r_yield'] is not None]
        ry = sum(r['r_yield'] for r in ok) / len(ok) * 365
        rl = sum(r['r_liq'] for r in ok) / len(ok) * 365
        nl = sum(r['n_liq'] for r in rows)
        burn = sum(r['burn'] for r in rows)
        prem = sum(r['gain'] for r in rows) / burn - 1 if burn else 0
        prem_o = sum(r['gain_oracle'] for r in rows) / burn - 1 if burn else 0
        print(f'{name:7s} days {len(ok):4d}  yield {ry*100:5.2f}%/yr  liq {rl*100:+5.2f}%/yr  '
              f'n_liq {nl:4d}  burned {burn:,.0f}  premium oracle {prem_o*100:+.2f}% / sold next hour {prem*100:+.2f}%  '
              f'avg dep {sum(r["deposits"] for r in ok)/len(ok):,.0f}')


# ---------------------------------------------------------------------------------------------- the strategy study

UPFRONT_DAYS = 7          # Liquity v2 charges 7 days of the branch's average rate on every borrow
AVG_RATE_CAP = 0.06       # the branch average rate used for the upfront fee (conservative: above every branch's mean)
SPOT_COST = 0.0005        # re-buying the redeemed collateral (3bp taker + 2bp to wrap/route)
CR = 2.5                  # collateral ratio of the hedged trove; per $ of ETH collateral the BOLD is 1/CR


def _day_index(rows):
    return {r['day']: r for r in rows}


def _redemption_hits(trv, r, ties_first=False):
    """Per redemption tx on a branch, the BOLD that would have hit a trove at rate r (it sits in front of every
    trove the tx actually redeemed at a rate >= r), with the fee rate and the redemption-vs-oracle price ratio."""
    by_tx = defaultdict(list)
    for o in trv['ops']:
        if o['op'] == 6:
            by_tx[o['tx']].append(o)
    red = {x['tx']: x for x in trv['red']}
    out = []
    for tx, ops in by_tx.items():
        behind = sum(-o['debt_chg'] for o in ops if (o['rate'] >= r - 1e-12 if ties_first else o['rate'] > r + 1e-12))
        if behind <= 0:
            continue
        rv = red.get(tx)
        fee = rv['coll_fee'] / (rv['coll_sent'] + rv['coll_fee']) if rv and rv['coll_sent'] + rv['coll_fee'] else 0.005
        pr = rv['price'] / rv['redemption_price'] if rv and rv['redemption_price'] else 1.0
        out.append({'ts': ops[0]['ts'], 'amount': behind, 'fee': fee, 'price_ratio': pr})
    return sorted(out, key=lambda x: x['ts'])


def simulate_loop(branch, daily, trv, chain, r, D0, policy='sell_next_day', ties_first=False):
    """Daily P&L of a hedged trove at rate r with its BOLD in the same branch's SP. The ETH leg is hedged, so it is
    left out; what remains is SP income - interest + the redemption cycles. Returns per-day rows."""
    days = [x for x in daily if x['r_yield'] is not None]
    hits = _redemption_hits(trv, r, ties_first)
    hits_by_day = defaultdict(list)
    for h in hits:
        hits_by_day[day(h['ts'])].append(h)
    chain_days = sorted(chain)
    D, F, F_cost, out = D0, 0.0, 0.0, []
    for i, x in enumerate(days):
        dd = x['day']
        pnl_red, absorbed = 0.0, 0.0
        for h in hits_by_day.get(dd, []):
            a = min(D, h['amount'])
            if a <= 0:
                continue
            D -= a
            absorbed += a
            # collateral handed over, valued at the oracle price, per redeemed BOLD
            F += a
            F_cost += a * (1 - h['fee']) * h['price_ratio']
        # SP income on everything we hold in the pool, diluted by our own deposit; our interest adds to the flow
        hold = D + F
        flow = x['yield'] + 0.75 * r * D / 365 + (x['gain'] - x['burn'])
        sp = hold * flow / (x['deposits'] + hold)
        interest = D * r / 365
        # rebuild: sell the free BOLD, re-buy collateral, re-borrow to D0 (upfront fee)
        nxt = chain.get(days[i + 1]['day']) if i + 1 < len(days) else None
        b = (nxt or chain.get(dd) or {}).get('sell1m', 0.999)
        b = 1 - (1 - b) * max(1.0, F / 1e6)       # a day's sale beyond the $1M quote moves the pool proportionally
        if F > 0 and (policy == 'sell_next_day' or b >= 0.999 or i + 1 == len(days)):
            pnl_red += F * b - F_cost - F * SPOT_COST
            re = D0 - D
            pnl_red -= re * AVG_RATE_CAP * UPFRONT_DAYS / 365
            D, F, F_cost = D0, 0.0, 0.0
        out.append({'day': dd, 'sp': sp, 'interest': interest, 'red': pnl_red, 'absorbed': absorbed,
                    'pnl': sp - interest + pnl_red, 'D': D, 'F': F})
    return out


def ssr_by_day(chain):
    ks = sorted(k for k in chain if chain[k].get('susds'))
    out = {}
    for a, b in zip(ks, ks[1:]):
        out[a] = (chain[b]['susds'] / chain[a]['susds']) ** 365 - 1
    return out


MARGIN = 0.2              # perp margin per $ of hedged notional


def package(variants, common, chain, ssr, D0):
    """The whole position per $ of capital, daily, against the savings rate actually paid: wstETH (or ETH) collateral
    at CR x the BOLD, its staking yield, the perp short's funding, and the loop. Capital = CR * D0 * (1 + MARGIN)."""
    import backtest as B
    f = json.loads((OUT / 'funding.json').read_text())
    hl, bn = defaultdict(float), defaultdict(float)
    for t, x in f['hl']:
        hl[day(t)] += x
    for t, x in f['binance']:
        bn[day(t)] += x
    lido = {d: a / 100 for d, a in f['lido_apr']}
    cap = CR * D0 * (1 + MARGIN)
    out = {}
    for venue, fund in (('hl', hl), ('binance', bn)):
        for k in ('wstETH r=0.005 sell_next_day', 'WETH r=0.005 sell_next_day', 'rETH r=0.005 sell_next_day'):
            rows = {x['day']: x for x in variants[k]}
            stake = (lambda d: lido.get(d, 0.025)) if not k.startswith('WETH') else (lambda d: 0.0)
            ex_loop, ex_base = [], []
            for d in common:
                base = CR * D0 * (stake(d) / 365 + fund.get(d, 0.0)) - cap * ssr.get(d, 0.0407) / 365
                ex_base.append(base / cap)
                ex_loop.append((base + rows[d]['pnl']) / cap)
            pl, pb = B.perf(ex_loop, 365), B.perf(ex_base, 365)
            h = len(common) // 2
            out[f'{venue} {k}'] = {'excess_with_loop': pl['ann_return'], 'excess_carry_only': pb['ann_return'],
                                   'with_loop_2nd_half': B.perf(ex_loop[h:], 365)['ann_return'],
                                   't_with_loop': B.newey_west_t(ex_loop)[0], 'sharpe': pl['sharpe'],
                                   'max_dd': pl['max_drawdown']}
            print(f"package {venue:8s} {k:30s} excess over SSR: carry {pb['ann_return']*100:5.2f}%  "
                  f"+loop {pl['ann_return']*100:5.2f}% (2nd half {out[f'{venue} {k}']['with_loop_2nd_half']*100:5.2f}%, "
                  f"t {out[f'{venue} {k}']['t_with_loop']:.2f}, maxDD {pl['max_drawdown']*100:.2f}%)")
    return out


def study(args):
    import backtest as B
    daily = json.loads((OUT / 'daily.json').read_text())
    trv = json.loads((OUT / 'troves.json').read_text())
    cpath = OUT / 'chain_daily.json'
    chain = json.loads(cpath.read_text()) if cpath.exists() else {}
    ssr = ssr_by_day(chain)
    res = {'variants': {}, 'meta': {'cr': CR, 'spot_cost': SPOT_COST, 'upfront': [UPFRONT_DAYS, AVG_RATE_CAP]}}
    rates = [0.005, 0.0075, 0.01, 0.015, 0.02, 0.03, 0.04]
    variants = {}
    for br in BRANCHES:
        for r in rates:
            for pol in ('sell_next_day', 'wait_peg'):
                rows = simulate_loop(br, daily[br], trv[br], chain, r, args.size, pol)
                variants[f'{br} r={r:.3f} {pol}'] = rows
    # per-variant: daily return per $ of BOLD minted (the increment carried by the hedged collateral)
    common = sorted(set.intersection(*[{x['day'] for x in v} for v in variants.values()]))
    series = {k: [{x['day']: x for x in v}[d]['pnl'] / args.size for d in common] for k, v in variants.items()}
    ctt = B.choose_then_test(series, frac=0.5, periods_per_year=365, key='ann_return')
    print('choose_then_test:', json.dumps({k: v for k, v in ctt.items() if k not in ('table',)}, default=str)[:1500])
    print(f"{'variant':34s} {'ann%':>7s} {'1st%':>7s} {'2nd%':>7s} {'absorbed/yr':>12s} {'red pnl%':>8s} {'t':>6s}")
    for k, v in variants.items():
        s_ = series[k]
        n = len(s_)
        h = n // 2
        ann = sum(s_) / n * 365
        a1, a2 = sum(s_[:h]) / h * 365, sum(s_[h:]) / (n - h) * 365
        absorbed = sum(x['absorbed'] for x in v) / args.size / (n / 365)
        redp = sum(x['red'] for x in v) / args.size / (n / 365)
        t = B.newey_west_t(s_)[0] or 0.0
        res['variants'][k] = {'ann': ann, 'first': a1, 'second': a2, 'turnover': absorbed, 'red': redp, 't': t}
        print(f'{k:34s} {ann*100:7.2f} {a1*100:7.2f} {a2*100:7.2f} {absorbed:12.2f} {redp*100:8.2f} {t:6.2f}')
    res['ctt'] = ctt
    res['package'] = package(variants, common, chain, ssr, args.size)
    if ssr:
        print('SSR mean over sample', sum(ssr.values()) / len(ssr) * 100)
    (OUT / f'study_{int(args.size)}.json').write_text(json.dumps(res, default=str, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('collect').set_defaults(fn=collect)
    sub.add_parser('analyze').set_defaults(fn=analyze)
    sub.add_parser('chain').set_defaults(fn=chain_daily)
    sub.add_parser('troves').set_defaults(fn=troves)
    sub.add_parser('funding').set_defaults(fn=funding)
    st = sub.add_parser('study')
    st.add_argument('--size', type=float, default=5e6)
    st.set_defaults(fn=study)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
