#!/usr/bin/env python3
"""Levered hedged trove: Liquity v2 credit at the 0.51% floor rate, used to lever a delta-neutral ETH carry.

Why. A hedged borrower does not care about redemption (it is paid the fee and its ETH is hedged), so it can borrow at
the protocol's floor rate while unhedged borrowers pay 2.5-8.4% to stand behind it in the queue. The unlevered study
(stability_pool.py) used that credit to fund a stability-pool deposit, about 5% a year on the BOLD. Here it funds more
collateral instead: mint BOLD, sell it for more wstETH, hedge all of it with a Hyperliquid short. Per $ of equity the
position earns (staking + funding) on CR/(CR-1)-ish times the equity and pays 0.51% on the debt.

Simulation, hourly, from the first live day (2025-05-19):
  * state: collateral q (ETH units), debt D (BOLD), perp short s (ETH units), HL margin m (USD);
  * each hour: the short marks to market, collects HL funding on s*P, collateral accrues staking (Lido APR), debt
    accrues r;
  * redemptions: every historical redemption tx that reached troves above r would have hit us first (queue ties at
    r go in front of us, as in stability_pool); D falls by a, q by a*(1-fee)*price_ratio/P;
  * rebalance when ETH moves more than `band` from the last rebalance, after a redemption, or when CR or margin
    leaves its safe range; it is decided at an hour's close and executed at the next hour's close (one hour for
    the bridge: HL withdraw to Arbitrum, CCTP); the target is CR c and perp leverage k at today's equity;
  * costs: BOLD sold at the day's Curve quote (sell1m, scaled linearly past $1M), BOLD bought back at buy1m, the
    7-day upfront fee on every debt increase (at a 6% average rate, above every branch's mean), 5bp per spot ETH
    trade, 4.5bp per perp trade (HL tier-0 taker);
  * liquidation check on each hour's high and low before the rebalance lands: trove below MCR loses 5% of debt and
    is rebuilt; perp margin below 2% of notional loses the margin left and is rebuilt.

    python3 scripts/levered_trove.py study [--equity 1e6]
"""
import argparse
import json
from collections import defaultdict

import stability_pool as S

OUT = S.OUT
MCR = {'WETH': 1.10, 'wstETH': 1.20, 'rETH': 1.20}
RATE = 0.0051
SPOT = 0.0005
PERP = 0.00045
MAINT = 0.02              # HL maintenance margin per $ of notional on ETH (max leverage 25x)
LIQ_PENALTY = 0.05


def load():
    f = json.loads((OUT / 'funding.json').read_text())
    hl = {t // 3600 * 3600: x for t, x in f['hl']}
    lido = {d: a / 100 for d, a in f['lido_apr']}
    chain = json.loads((OUT / 'chain_daily.json').read_text())
    px = json.loads((OUT / 'ethusdt_1h_ohlc.json').read_text())
    trv = json.loads((OUT / 'troves.json').read_text())
    return hl, lido, chain, px, trv


def simulate(branch, data, c, k, band, E0, r=RATE, fixed=0.0, relever_at=1.0):
    """`fixed`: $ per full rebalance (Ethereum gas, bridge, HL withdrawal fee), which decides small accounts.
    `relever_at`: after a redemption, trim the short at once (an HL trade, no gas) and rebuild the trove only when
    collateral has fallen below this fraction of target; 1.0 rebuilds after every redemption."""
    hl, lido, chain, px, trv = data
    hits = defaultdict(list)
    for h in S._redemption_hits(trv[branch], r):
        hits[h['ts'] // 3600 * 3600].append(h)
    stake_on = branch != 'WETH'

    def quote(d, key, default):
        return (chain.get(d) or {}).get(key, default)

    def rebalance(P, d, E):
        """Move to CR c and perp leverage k at equity E; returns new state and the cost paid."""
        nonlocal q, D, s, m
        Q = E / (1 - 1 / c + 1 / k) / P
        D1, s1 = Q * P / c, Q
        cost = abs(Q - q) * P * SPOT + abs(s1 - s) * P * PERP + fixed
        dD = D1 - D
        if dD > 0:
            cost += dD * (1 - quote(d, 'sell1m', 0.999)) * max(1.0, dD / 1e6)
            cost += dD * S.AVG_RATE_CAP * S.UPFRONT_DAYS / 365
        elif dD < 0:
            cost += -dD * (1 / quote(d, 'buy1m', 0.999) - 1) * max(1.0, -dD / 1e6)
        q, D, s = Q, D1, s1
        m = Q * P / k - cost                     # the cost comes out of the margin account
        return cost

    q = D = s = m = 0.0
    t0, P0 = px[0][0], px[0][4]
    costs = rebalance(P0, S.day(t0), E0)
    P_reb, pending, wait_day, rows = P0, False, None, []
    liqs, n_reb, absorbed, fees_got = [], 1, 0.0, 0.0
    day_eq, last = {}, P0
    for t, o, hi, lo, cl in px[1:]:
        d = S.day(t)
        do_reb, pending = pending, False
        if wait_day and d != wait_day:
            do_reb, wait_day = True, None
        # liquidation checks on the hour's extremes, before anything we decided last hour lands
        # A liquidated leg is rebuilt at the hour's close, not at the wick that liquidated it.
        if D > 0 and q * lo / D < MCR[branch]:
            loss = LIQ_PENALTY * D                   # the SP takes 5% of the debt; the surplus collateral is claimable
            liqs.append((d, 'trove', loss))
            E = (q - (D + loss) / lo) * cl + m + s * (last - cl)
            last = cl
            costs += rebalance(cl, d, E)
            n_reb, P_reb, do_reb = n_reb + 1, cl, False
            day_eq[d] = q * cl - D + m
            continue
        if s > 0 and m - s * (hi - last) < MAINT * s * hi:
            loss = max(0.0, m - s * (hi - last))     # whatever margin is left goes to the liquidator
            liqs.append((d, 'perp', m))
            E = q * cl - D
            last = cl
            s = m = 0.0
            costs += rebalance(cl, d, E)
            n_reb, P_reb, do_reb = n_reb + 1, cl, False
            day_eq[d] = q * cl - D + m
            continue
        # mark, carry
        m += s * (last - cl) + s * cl * hl.get(t, 0.0)
        last = cl
        if stake_on:
            q *= 1 + lido.get(d, 0.025) / 8760
        D *= 1 + r / 8760
        if do_reb:
            costs += rebalance(cl, d, q * cl - D + m)
            n_reb, P_reb = n_reb + 1, cl
        for h in hits.get(t, []):
            a = min(D, h['amount'])
            if a > 0:
                D -= a
                q -= a * (1 - h['fee']) * h['price_ratio'] / cl
                absorbed += a
                fees_got += a * h['fee']
                if q * cl < relever_at * (q * cl - D + m) / (1 - 1 / c + 1 / k):
                    wait_day = d                     # rebuilt at the next UTC day's quote: BOLD sits below
                                                     # 1 - fee while redemptions run, so not within the episode
        if s > q:                                    # trim the over-hedge left by a redemption
            costs += (s - q) * cl * PERP
            m -= (s - q) * cl * PERP
            s = q
        cr = q * cl / D if D > 0 else 99.0
        if (abs(cl / P_reb - 1) > band or cr < c - 0.6 * (c - MCR[branch])
                or (s > 0 and m / (s * cl) < 0.5 / k)):
            pending = True
        day_eq[d] = q * cl - D + m
    days = sorted(day_eq)
    rets = [day_eq[b] / day_eq[a] - 1 for a, b in zip(days, days[1:])]
    return {'days': days[1:], 'rets': rets, 'liqs': liqs, 'n_reb': n_reb, 'costs': costs, 'absorbed': absorbed,
            'fees': fees_got, 'E_end': day_eq[days[-1]], 'debt': D}


def study(args):
    import backtest as B
    data = load()
    ssr = S.ssr_by_day(data[2])
    res = {}
    grid = [(c, k, band) for c in (1.35, 1.5, 1.75, 2.0) for k in (3, 5, 8) for band in (0.03, 0.05, 0.1)]
    series = {}
    for br in ('wstETH', 'rETH', 'WETH'):
        for c, k, band in grid:
            if c - 0.6 * (c - MCR[br]) <= MCR[br]:
                continue
            x = simulate(br, data, c, k, band, args.equity)
            key = f'{br} c={c} k={k} band={band}'
            ex = [rt - ssr.get(d, 0.0407) / 365 for d, rt in zip(x['days'], x['rets'])]
            series[key] = ex
            p = B.perf(x['rets'], 365)
            h = len(ex) // 2
            res[key] = {'roe': p['ann_return'], 'excess': B.perf(ex, 365)['ann_return'],
                        'first': B.perf(x['rets'][:h], 365)['ann_return'], 'second': B.perf(x['rets'][h:], 365)['ann_return'],
                        'sharpe': p['sharpe'], 'max_dd': p['max_drawdown'], 't_excess': B.newey_west_t(ex)[0],
                        'liqs': len(x['liqs']), 'liq_loss': sum(l[2] for l in x['liqs']) / args.equity,
                        'n_reb': x['n_reb'], 'cost_frac': x['costs'] / args.equity,
                        'absorbed_x': x['absorbed'] / args.equity, 'fees_frac': x['fees'] / args.equity}
            v = res[key]
            print(f"{key:34s} ROE {v['roe']*100:6.2f}% (1st {v['first']*100:6.2f} 2nd {v['second']*100:6.2f}) "
                  f"ex {v['excess']*100:6.2f}% t {v['t_excess']:5.2f} SR {v['sharpe']:4.1f} DD {v['max_dd']*100:6.2f}% "
                  f"liq {v['liqs']} ({v['liq_loss']*100:.1f}%) reb {v['n_reb']:4d} cost {v['cost_frac']*100:5.2f}%")
    ctt = B.choose_then_test(series, frac=0.5, periods_per_year=365, key='ann_return')
    print('choose_then_test:', json.dumps({k: v for k, v in ctt.items() if k != 'table'}, default=str)[:1200])
    (OUT / f'levered_{int(args.equity)}.json').write_text(json.dumps({'variants': res, 'ctt': ctt}, default=str, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    st = sub.add_parser('study')
    st.add_argument('--equity', type=float, default=1e6)
    st.set_defaults(fn=study)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
