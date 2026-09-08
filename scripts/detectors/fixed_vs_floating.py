#!/usr/bin/env python3
"""Pendle's fixed rate against the floating rate on the same underlying — and the harder question of when they are.

A principal token redeems 1:1 into its asset at maturity, so its price is a fixed rate. Comparing that rate to the
floating rate the same asset pays is the cleanest yield trade on the chain when the two really are the same credit:
PT-sUSDS at 4.97% against a Sky savings rate of 3.60% is a term premium on identical USDS credit, and the buyer is
paid to accept that governance cannot raise the rate inside the window.

The trap is that most implied yields on the board are not that. The 2026-09-06 study found dollar PTs quoting 5% to
25%, and wrote down the reason: those are not term premia, they are the market's price of each issuer's credit and of
the points programmes attached. A detector that ranks by implied yield alone puts a distressed junior tranche at the
top of the book. So every row is classified before it is priced:

  * **term premium** — the floating rate on the *same* underlying is readable from the head state, so the gap is a
    rate view and nothing else. These are quoted as opportunities.
  * **credit spread** — no comparable floating rate, so the excess over the risk-free dollar is compensation for a
    credit this system has not assessed. Reported at low severity, explicitly not as an edge.

Two more things separate the quoted number from the realisable one. The oracle's observation window must be populated
or the price is not a price, which `getOracleState` reports and the head refuses to quote without. And entry costs
impact: the depth behind the quote is the market's own PT balance, so a size worth having is priced through it rather
than against it.

A caveat on that impact, stated because it is the weakest number here. Pendle's AMM is a rate curve, far flatter near
the prevailing implied yield than constant product, so charging a PT purchase the constant-product cost overstates it
by roughly two orders of magnitude — the same error `economics.py`'s `amplification` parameter exists to prevent for
Curve legs. The value used below is anchored to the one observation this repo has: the 2026-09-06 study put a $1M
order into a $3.5M pool at "a real part of" 137bp, which implies an amplification near 70. Fifty is used, which is
conservative in the direction of quoting less. Replacing it with a measured quote-by-size read from the Pendle router
is the obvious improvement and is not done here.
"""
from . import Hit
from economics import Opportunity, Leg, score

NAME = 'fixed_vs_floating'
DESCRIPTION = 'Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth'
SEVERITY = 'notable'

MIN_GAP = 0.004        # 40bps of annualised gap before a term premium is worth a line
MIN_DEPTH_USD = 2.5e5  # a market thinner than this cannot take a position worth opening
MIN_DAYS = 5           # inside a week the annualisation swamps the gap and the fees dominate
# Pendle's AMM is a rate curve, not constant product. See the module docstring: this is an estimate anchored to one
# observation, deliberately conservative, and the single number here most worth replacing with a measurement.
PENDLE_AMPLIFICATION = 50.0

# Underlying asset -> where the floating rate on *that exact asset* is read from in `head_state`.
#
# Matched exactly against the asset segment of the PT symbol, never as a substring. Substring matching classified
# PT-srUSDe as sUSDe credit — 'USDE' is inside 'SRUSDE' — and so quoted a different issuer's product as a term
# premium on Ethena. That is precisely the error this detector exists to prevent, committed by its own matcher.
FLOATING = {
    'SUSDS':  (('sky', 'ssr_apy'), 'Sky savings rate'),
    'USDS':   (('sky', 'ssr_apy'), 'Sky savings rate'),
    'SDAI':   (('sky', 'dsr_apy'), 'Sky DSR'),
    'DAI':    (('sky', 'dsr_apy'), 'Sky DSR'),
    'SUSDE':  (('ethena', 'apr_from_vesting'), 'sUSDe vesting APR'),
    'USDE':   (('ethena', 'apr_from_vesting'), 'sUSDe vesting APR'),
}


def scan(ctx):
    head = _head(ctx)
    if not head:
        return []
    pendle = head.get('pendle') or {}
    if not pendle:
        return []
    bench = (head.get('sky') or {}).get('ssr_apy') or 0.036
    gas_gwei = _gas(ctx)
    eth = ctx.prices.get('ETH') or 2500.0

    hits = []
    for m, r in pendle.items():
        apy, days = r.get('implied_apy'), r.get('days_to_maturity')
        if apy is None or not days or days < MIN_DAYS:
            continue
        sym = (r.get('pt_symbol') or '').upper()
        # Depth in dollars. Dollar PTs price at ~1 asset each; anything else is left unpriced rather than guessed,
        # because a wrong price here would size the position wrongly in the direction that flatters it.
        depth_units = r.get('pt_depth_units') or 0
        px = 1.0 if _is_dollar(sym) else None
        depth_usd = depth_units * (r.get('pt_to_asset') or 1) * px if px else None
        if not depth_usd or depth_usd < MIN_DEPTH_USD:
            continue

        floating, fname = _floating(head, sym)
        kind = 'term premium' if floating is not None else 'credit spread'
        base = floating if floating is not None else bench
        gap = apy - base
        if gap < MIN_GAP:
            continue

        # Held to maturity, so the edge is the annualised gap earned for `days`, once.
        edge_bps = 1e4 * gap * days / 365
        v = score(Opportunity(
            name='%s fixed %.2f%% against %s %.2f%%' % (sym or m[:10], 100 * apy, fname, 100 * base),
            edge_bps=edge_bps,
            legs=[Leg('buy %s on Pendle' % (sym or 'PT'), depth_usd=depth_usd, capacity_usd=depth_usd * 0.25,
                      amplification=PENDLE_AMPLIFICATION)],
            gas_units=400_000, capital_days=days, runs_per_day=1 / days, competitors=0,
            notes='held to maturity, where PT redeems 1:1; exit before maturity is a sale back into the same market. '
                  'Entry impact is priced against the market’s own PT balance with an amplification of %g, because '
                  'Pendle’s curve is a rate curve and not constant product; capacity is capped at a quarter of the '
                  'book because taking all of it is not a fill.' % PENDLE_AMPLIFICATION),
            gas_gwei=gas_gwei, eth_usd=eth, min_net_usd=0.0)

        hits.append(Hit(
            detector=NAME, key=sym or m,
            severity=('notable' if (kind == 'term premium' and v.go) else 'info'),
            usd=v.annual_net_usd,
            title='%s implies %.2f%% fixed for %.0f days against %s at %.2f%% — %s%s'
                  % (sym or m[:10], 100 * apy, days, fname, 100 * base, kind,
                     '' if kind == 'term premium' else ', not a rate trade: nothing here prices that issuer’s credit'),
            evidence={'market': m, 'pt': r.get('pt'), 'pt_symbol': sym,
                      'implied_apy_pct': round(100 * apy, 3), 'days_to_maturity': days,
                      'pt_to_asset': r.get('pt_to_asset'),
                      'underlying': underlying_of(sym),
                      'comparison': fname, 'floating_pct': round(100 * base, 3),
                      'gap_pp': round(100 * gap, 3), 'classification': kind,
                      'pt_depth_units': round(depth_units), 'pt_depth_usd': round(depth_usd),
                      'oracle_ready': r.get('oracle_ready'),
                      'why': ('the same credit pays more fixed than floating for a fixed term, which is a view on the '
                              'floating rate and nothing else'
                              if kind == 'term premium' else
                              'no floating rate on this underlying is readable, so the excess over the risk-free '
                              'dollar is the market’s price of an issuer’s credit — a judgement this system has not '
                              'made, quoted here only so it is not mistaken for a term premium')},
            economics={'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                       'net_per_run_usd': round(v.net_per_run_usd, 2), 'go': v.go, 'reason': v.reason,
                       'capacity_usd': round(depth_usd * 0.25), 'hold_days': days,
                       'optimal_size_usd': round(v.optimal_size_usd) if v.optimal_size_usd else None,
                       'amplification_assumed': PENDLE_AMPLIFICATION}))
    hits.sort(key=lambda h: -(h.usd or 0))
    return hits


def _is_dollar(sym):
    return any(t in sym for t in ('USD', 'DAI', 'GHO', 'DOLA', 'FRAX'))


def underlying_of(sym):
    """The asset segment of a `PT-<asset>-<DDMMMYYYY>` symbol, upper-cased. None when the shape is not that."""
    parts = (sym or '').split('-')
    return parts[1].upper() if len(parts) >= 3 and parts[0].upper() == 'PT' else None


def _floating(head, sym):
    u = underlying_of(sym)
    hit = FLOATING.get(u) if u else None
    if hit:
        (a, b), name = hit
        v = (head.get(a) or {}).get(b)
        if v:
            return v, name
    return None, 'the Sky savings rate (as the risk-free dollar)'


def _head(ctx):
    import json
    p = ctx.out / 'head_state.json'
    return json.loads(p.read_text()) if p.exists() else None


def _gas(ctx):
    from window_raw import median
    return median([b['base_gwei'] for b in ctx.blocks]) or 1.0
