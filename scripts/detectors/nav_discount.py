#!/usr/bin/env python3
"""Redeemable claims trading below the value the protocol pays on redemption, and how long you must wait to collect it.

This is the repo's redemption-liquidity thesis turned into a standing check. That thesis, built by hand on 2026-09-06
and proven on a mainnet fork, says the durable non-MEV edge on an efficient chain is *redemption that clears over
time*: buy a claim below the value its protocol will pay, and realise the convergence through the protocol's own
queue, which a bot cannot do because it has to hold the position for a day. The strategy has sat in the book since
with no quote, because nothing re-measured the discount.

Everything needed is already in the two artifacts. `head_state.rates` carries each claim's exchange rate against its
underlying — the value the protocol pays — and `analysis.peg` carries the volume-weighted price the market actually
traded it at, from the window's own swaps. The gap between them is the trade.

Three things make the difference between a finding and a strategy, and each is reported:

  * **Latency.** An *atomically* redeemable claim at a discount is an MEV race and belongs to whoever is fastest;
    a claim behind a queue cannot be flashed, which is exactly why the edge survives. sDAI and sUSDS redeem in the
    same transaction. sUSDe waits a day. stETH and the liquid restaking tokens wait longer, and their queues are the
    reason their discounts are wider.
  * **Capacity is the volume actually offered, not the pool.** You cannot buy a discount that nobody is selling. The
    window's traded volume in that asset is the honest cap, and it is usually far smaller than the pool depth a
    naive sizing would use.
  * **The annualised rate depends on the wait.** 20bps collected over one day is 73% a year; the same 20bps over a
    ten-day withdrawal queue is 7.3%, and over a queue that lengthens under stress, less than that.

A premium — the claim trading *above* NAV — is reported too, at low severity. It is not a trade in this direction, but
it says the market is paying for immediacy, which is the same mechanism seen from the other side.

**And a discount smaller than the spread it was measured across is not a discount.** The market price here is a
volume-weighted average of the window's swaps, so the window's own p10-to-p90 spread bounds how confidently any gap
below it can be called. On 2026-09-07 sUSDe showed a 7.1bp discount, 4.4bp after the round trip, across a window whose
p10-to-p90 spread was 5.4bp: the edge was inside the dispersion of the prices it was averaged from, which is a
materially weaker claim than the number alone suggests. Every hit now carries that comparison and is demoted when it
fails it.
"""
from . import Hit
from economics import Opportunity, Leg, score

NAME = 'nav_discount'
DESCRIPTION = 'redeemable claims trading away from the value the protocol pays, with the queue that separates them'
SEVERITY = 'notable'

MIN_BPS = 5.0          # below this the gap is inside the fee and the price basis, not an edge
MIN_VOLUME = 5e4       # a price from less volume than this is one trade, not a market
GAS_UNITS = 500_000    # buy + request redemption + claim

# What redeeming actually involves. Three fields decide whether a discount is a trade.
#
#   `days`         the wait before the underlying is in hand, which sets the annualisation and keeps bots out;
#   `atomic`       settles in one transaction, so any gap there is a latency race and not a holding trade;
#   `availability` whether the redemption leg is *there when you want it*. This is the field that stops the detector
#                  quoting a 65% APR on rETH: Rocket Pool's burn path pays out of a deposit pool that is empty most
#                  of the time, and Coinbase's cbETH redemption is off-chain and permissioned. A discount whose exit
#                  is conditional is a discount you may have to sell back into the market, which is a different trade.
#   `exit_bps`     what the round trip costs in DEX fees and impact beyond the discount itself. The 2026-09-06 fork
#                  test measured the sUSDe path at −2.7bp with the ask *at* NAV — two Curve legs — so quoting the
#                  raw NAV gap as profit overstates every one of these by roughly that much.
REDEMPTION = {
    'SDAI':   {'days': 0.0, 'atomic': True,  'availability': 'always',       'exit_bps': 1.0,
               'path': 'ERC-4626 redeem into DAI, same transaction'},
    'SUSDS':  {'days': 0.0, 'atomic': True,  'availability': 'always',       'exit_bps': 1.0,
               'path': 'ERC-4626 redeem into USDS, same transaction'},
    'SUSDE':  {'days': 1.0, 'atomic': False, 'availability': 'always',       'exit_bps': 2.7,
               'path': 'cooldownShares, then unstake after cooldownDuration (1 day)'},
    'WSTETH': {'days': 3.0, 'atomic': False, 'availability': 'queued',       'exit_bps': 3.0,
               'path': 'unwrap to stETH, then the Lido withdrawal queue'},
    'RETH':   {'days': 1.0, 'atomic': False, 'availability': 'conditional',  'exit_bps': 5.0,
               'path': 'burn into available rETH contract ETH and excess deposit-pool ETH; liquidity requires a pinned check'},
    'RSETH':  {'days': 7.0, 'atomic': False, 'availability': 'queued',       'exit_bps': 5.0,
               'path': 'Kelp withdrawal queue'},
    'EZETH':  {'days': 7.0, 'atomic': False, 'availability': 'queued',       'exit_bps': 5.0,
               'path': 'Renzo withdrawal queue'},
    'WEETH':  {'days': 7.0, 'atomic': False, 'availability': 'queued',       'exit_bps': 5.0,
               'path': 'EtherFi withdrawal queue'},
    'CBETH':  {'days': 2.0, 'atomic': False, 'availability': 'permissioned', 'exit_bps': 5.0,
               'path': 'Coinbase redemption, off-chain and permissioned'},
}
DEFAULT_REDEMPTION = {'days': 7.0, 'atomic': False, 'availability': 'unknown', 'exit_bps': 5.0,
                      'path': 'unknown redemption path'}
# `head_state.rates` keys are upper-case; the peg table is keyed by the token symbol as traded.
SYMBOL = {'SDAI': 'sDAI', 'SUSDS': 'sUSDS', 'SUSDE': 'sUSDe', 'WSTETH': 'wstETH', 'RETH': 'rETH',
          'RSETH': 'rsETH', 'EZETH': 'ezETH', 'WEETH': 'weETH', 'CBETH': 'cbETH'}


def scan(ctx):
    head = _head(ctx)
    if not head:
        return []
    A = ctx.analysis or {}
    hours = (A.get('window') or {}).get('hours') or 1.0
    peg = A.get('peg') or {}
    px = A.get('price_basis') or {}
    gas_gwei = _gas(ctx)
    eth = px.get('ETH') or 2500.0

    hits = []
    for key, r in (head.get('rates') or {}).items():
        rate, under = r.get('rate'), (r.get('underlying') or '').upper()
        sym = SYMBOL.get(key)
        if not rate or not sym:
            continue
        p = peg.get(sym)
        if not p or (p.get('volume_usd') or 0) < MIN_VOLUME or not p.get('vw_price'):
            continue
        # NAV in the same units the peg table quotes: USD for the dollar claims, USD via ETH for the staking ones.
        if under in ('USD',):
            nav = rate
        elif under in ('ETH', 'STETH'):
            nav = rate * eth          # stETH is treated as one ETH; its own discount is reported separately below
        elif under == 'DAI':
            nav = rate * (px.get('DAI') or 1.0)
        else:
            continue
        market = p['vw_price']
        disc_bps = 1e4 * (nav - market) / nav
        if abs(disc_bps) < MIN_BPS:
            continue

        red = REDEMPTION.get(key, DEFAULT_REDEMPTION)
        cap = float(p['volume_usd'])          # you can only buy what was offered
        net_bps = disc_bps - red['exit_bps']
        # How wide were the prices this average came from? A gap narrower than that spread is inside the noise of the
        # sample it was measured against. For an ETH-denominated claim the spread also contains ETH's own move over
        # the window, so the test is conservative there rather than wrong — it is noted in the evidence.
        p10, p90 = p.get('p10'), p.get('p90')
        disp_bps = (1e4 * (p90 - p10) / nav) if (p10 and p90 and nav) else None
        best_bps = (1e4 * (nav - p10) / nav) if (p10 and nav) else None
        significance = (net_bps / disp_bps) if (disp_bps and disp_bps > 0) else None
        inside_noise = significance is not None and significance < 1.0
        if disc_bps > 0:
            v = score(Opportunity(
                name='%s at %.1fbp below NAV, redeemed in %.1f day(s)' % (sym, disc_bps, red['days']),
                edge_bps=net_bps,
                legs=[Leg('buy %s on the window’s venues' % sym, capacity_usd=cap),
                      Leg('exit the underlying back to a dollar or to ETH', fee_bps=0.0)],
                gas_units=GAS_UNITS, capital_days=max(red['days'], 0.02),
                runs_per_day=1 / max(red['days'], 0.02),
                race=red['atomic'], competitors=8 if red['atomic'] else 0,
                notes='edge is the NAV gap less a measured round-trip cost of %.1fbp; capacity is the volume '
                      'actually traded in this window, not pool depth, because a discount you cannot buy is not a '
                      'trade. The redemption leg is assumed to pay NAV exactly, which the fork test of the sDAI path '
                      'confirmed and which a queue under stress would not.' % red['exit_bps']),
                gas_gwei=gas_gwei, eth_usd=eth, min_net_usd=0.0)
            # The go/no-go has to carry the significance test, not just the arithmetic: the ledger and the strategy
            # book read `go` and `net_apr` from here, so an edge inside its own price noise must not reach them as a
            # clean yes.
            econ = {'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                    'net_per_run_usd': round(v.net_per_run_usd, 2),
                    'go': bool(v.go and not inside_noise),
                    'reason': (v.reason if not inside_noise else
                               'net edge %.1fbp is inside the window’s %.1fbp p10-to-p90 price spread (significance '
                               '%.2f): the discount is not distinguishable from where the asset traded'
                               % (net_bps, disp_bps, significance)),
                    'capacity_usd': round(cap), 'hold_days': red['days'],
                    'discount_bps': round(disc_bps, 2), 'exit_cost_bps': red['exit_bps'],
                    'net_edge_bps': round(net_bps, 2),
                    'price_dispersion_bps': None if disp_bps is None else round(disp_bps, 2),
                    'significance': None if significance is None else round(significance, 2),
                    'inside_price_noise': inside_noise}
            if red['availability'] not in ('always', 'queued'):
                econ.update({'conditional_model_net_apr': econ['net_apr'],
                             'conditional_model_net_per_year_usd': econ['net_per_year_usd'],
                             'net_apr': None, 'net_per_year_usd': 0, 'net_per_run_usd': 0,
                             'go': False, 'capacity_usd': 0,
                             'reason': 'Redemption is %s; exit capacity/access has not been verified. '
                                       'The conditional model is not an executable quote.' % red['availability']})
            solid = (v.go and not red['atomic'] and red['availability'] in ('always', 'queued')
                     and not inside_noise)
            sev = 'high' if (solid and net_bps >= 15) else ('notable' if solid else 'info')
            title = ('%s trades %.1fbp below NAV, %.1fbp after the %.1fbp round trip; %s%s%s'
                     % (sym, disc_bps, net_bps, red['exit_bps'], red['path'],
                        '' if red['availability'] in ('always', 'queued') else
                        ' — %s, so the exit may not be there when you want it' % red['availability'],
                        (' — but the window’s own p10-to-p90 spread is %.1fbp, so the edge is inside the dispersion '
                         'of the prices it was averaged from' % disp_bps) if inside_noise else ''))
        else:
            econ, sev = None, 'info'
            title = '%s trades %.1fbp above NAV — the market is paying for immediacy' % (sym, -disc_bps)

        hits.append(Hit(
            detector=NAME, key=sym, severity=sev, usd=(econ or {}).get('net_per_year_usd'),
            title=title,
            evidence={'asset': sym, 'nav_source': '%s %s' % (r.get('contract', '')[:10], r.get('method')),
                      'nav': round(nav, 6), 'market_vw_price': round(market, 6),
                      'market_median': round(p.get('median') or 0, 6),
                      'market_p10': round(p.get('p10') or 0, 6),
                      'discount_bps': round(disc_bps, 2), 'traded_volume_usd': round(cap),
                      # The annualised rate assumes you refill the position every `days`. Whether that is plausible
                      # is a question about how much of this asset trades in a day, so the extrapolation is shown
                      # rather than left implicit inside the APR.
                      'implied_daily_volume_usd': round(cap * 24 / max(hours, 1e-9)),
                      'refills_needed_per_year': round(365 / max(red['days'], 0.02)),
                      'swaps': p.get('n'), 'venues': p.get('venues'),
                      'redemption': red, 'net_edge_bps': round(net_bps, 2),
                      'price_dispersion_bps': None if disp_bps is None else round(disp_bps, 2),
                      'discount_at_p10_bps': None if best_bps is None else round(best_bps, 2),
                      'significance_vs_dispersion': None if significance is None else round(significance, 2),
                      'dispersion_note': ('the spread of an ETH-denominated claim also contains ETH’s own move over '
                                          'the window, so this test is conservative here'
                                          if under in ('ETH', 'STETH') else
                                          'a dollar claim’s NAV barely moves, so the spread is mostly execution '
                                          'dispersion and the test is meaningful'),
                      'why': ('the protocol pays NAV and the market paid less; the gap closes when you redeem, and '
                              'the wait is the reason a bot cannot take it from you'
                              if disc_bps > 0 else
                              'a claim above NAV is the same mechanism seen from the seller’s side')},
            economics=econ))
    hits.sort(key=lambda h: -(h.usd or 0))
    return hits


def _head(ctx):
    import json
    p = ctx.out / 'head_state.json'
    return json.loads(p.read_text()) if p.exists() else None


def _gas(ctx):
    return ctx.gas_quote()['gwei']
