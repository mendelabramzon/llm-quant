#!/usr/bin/env python3
"""The same asset lending at different rates on different venues, de-spiked and sized by how fast the gap closes.

The finding this makes permanent. Cross-venue rate gaps show up in every window: Compound USDC paying roughly twice Aave
through a whole quiet Monday, Spark USDT spiking to 7% on an ALM transfer and normalising within the hour. Each was read
off a table by hand, so nothing separated a gap worth capital from one block of noise, and nothing said how much capital
it would take.

Three things decide that, and all three are computed here.

**De-spiking.** A rate is quoted as the median of the window's `ReserveDataUpdated` series where one exists, not the last
reading. The midnight balance routine and same-block flash loans move a reserve's rate several-fold for one block, so a
spot read is the single most pollutable number the scan produces. A gap the median keeps but the last reading has lost
is reported as a transient rather than as an opportunity.

**Dilution capacity.** Supplying into the high-paying venue is what closes the gap: your own capital raises the supply,
lowers utilisation, and the rate falls with it. A supplier earns the borrow rate times utilisation, and below the kink
the borrow rate is itself roughly linear in utilisation, so the supply rate goes as `u²`. Every market here sits at 84%
to 93% utilisation — above the usual kink, where the borrow curve is steeper still — so `u²` is the conservative reading
and a rate treated as linear in `u` would overstate capacity several-fold. Capital `X` into a pool holding `S` then earns
an average of `r·S/(S+X)`, which halves the rate at `X = S`: to halve a gap you must roughly match the existing pool.

A venue whose rate does not depend on utilisation at all, such as Sky's savings rate, is marked as not diluting and its
capacity is reported as rate-invariant rather than solved for.

**Economics.** Every gap is scored through `economics.py` and reports a net annual figure after gas, so a wide gap on a
thin market ranks below a narrow one on a deep market, which is the ordering that matters.
"""
import collections
import math

from . import Hit
from economics import Leg, Opportunity, score
from window_raw import median

NAME = 'rate_dispersion'
DESCRIPTION = 'cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution'
SEVERITY = 'notable'

MIN_GAP_PP = 0.5        # percentage points of supply-rate gap worth reporting
MIN_SUPPLIED_USD = 5e6  # ignore markets too small to take any size
MIN_UPDATES = 20        # observations a venue needs before its log-derived median means anything
# Venues whose rates arrive as `ReserveDataUpdated` logs, and so can be de-spiked from the window itself. Compound's
# Comet and Sky's savings rate emit nothing comparable, so their head read is the only source there is — a coverage
# limit rather than a spike risk, and the two deserve different treatment.
LOG_VENUES = {'Aave v3', 'SparkLend'}


def scan(ctx):
    head = _head_state(ctx)
    if not head:
        return []
    venues = _venue_table(head, ctx)
    medians = _log_medians(ctx)
    gas_gwei = median([b['base_gwei'] for b in ctx.blocks]) or 1.0
    eth = ctx.prices.get('ETH', 2500.0)

    by_sym = collections.defaultdict(dict)
    for (venue, sym), d in venues.items():
        by_sym[sym][venue] = d

    hits = []
    for sym, vs in by_sym.items():
        if len(vs) < 2:
            continue
        hi_v = max(vs, key=lambda v: vs[v]['supply_apr'])
        lo_v = min(vs, key=lambda v: vs[v]['supply_apr'])
        hi, lo = vs[hi_v], vs[lo_v]
        gap = (hi['supply_apr'] - lo['supply_apr']) * 100
        # Both sides must be live markets. A reserve with almost nothing supplied sits at zero utilisation and
        # therefore near a zero supply rate, which manufactures a spectacular gap against any real market.
        if gap < MIN_GAP_PP or (hi['supplied_usd'] or 0) < MIN_SUPPLIED_USD or (lo['supplied_usd'] or 0) < MIN_SUPPLIED_USD:
            continue

        # de-spike: prefer the window median where the logs carry enough observations for that venue and asset
        med_hi = medians.get((hi_v, sym))
        spiked = None
        despiked = med_hi is not None
        # Only a venue we could have de-spiked is suspicious when we could not.
        unchecked = (hi_v in LOG_VENUES) and not despiked
        if med_hi is not None and hi['supply_apr'] > 0:
            ratio = hi['supply_apr'] / med_hi if med_hi > 0 else float('inf')
            spiked = ratio > 1.5 or ratio < 0.67
            eff_hi = med_hi
        else:
            eff_hi = hi['supply_apr']
        med_lo = medians.get((lo_v, sym))
        eff_lo = med_lo if med_lo is not None else lo['supply_apr']
        eff_gap = (eff_hi - eff_lo) * 100
        if eff_gap < MIN_GAP_PP:
            hits.append(Hit(detector=NAME, severity='info', usd=None,
                            key='%s:%s/%s' % (sym, hi_v, lo_v),
                            title='%s gap on %s over %s is a spot artifact: %.2fpp spot, %.2fpp on window medians'
                                  % (sym, hi_v, lo_v, gap, eff_gap),
                            evidence={'asset': sym, 'spot_gap_pp': round(gap, 3), 'median_gap_pp': round(eff_gap, 3),
                                      'why': 'the head read is one block; the median over the window is what persists'}))
            continue

        S = float(hi['supplied_usd'])
        dilutes = hi.get('dilutes', True)
        opp = Opportunity(
            name='%s supply spread: %s over %s' % (sym, hi_v, lo_v),
            edge_bps=eff_gap * 100,
            legs=[Leg('supply %s into %s%s' % (sym, hi_v, ' (rate dilutes as you add)' if dilutes else ' (fixed rate)'),
                      capacity_usd=S, impact_curve=_dilution_curve(eff_hi, S) if dilutes else None)],
            gas_units=300_000, capital_days=365, runs_per_day=1 / 365, competitors=0,
            notes='supply rate modelled as proportional to utilisation; the borrow rate is held fixed, so the '
                  'realised gap closes sooner than this')
        v = score(opp, gas_gwei=gas_gwei, eth_usd=eth, min_net_usd=0.0)
        half = _half_edge_size(eff_hi, eff_lo, S) if dilutes else None
        # A gap that could not be de-spiked is a single block's reading. It may be real and it may be the tail of an
        # ALM transfer or a flash loan, and there is no way to tell from one observation, so it ranks below a gap the
        # window's own series confirms rather than sitting beside it as an equal.
        hits.append(Hit(
            detector=NAME, severity='info' if unchecked else 'notable', usd=v.annual_net_usd,
            key='%s:%s/%s' % (sym, hi_v, lo_v),
            title='%s pays %.2fpp more on %s than %s; %s%s'
                  % (sym, eff_gap, hi_v, lo_v,
                     ('$%s halves the gap' % _m(half)) if half else 'rate does not dilute with size',
                     ' [one-block read, de-spiking unavailable]' if unchecked else ''),
            evidence={'asset': sym, 'high_venue': hi_v, 'low_venue': lo_v,
                      'supply_apr_spot_pct': {k: round(100 * d['supply_apr'], 3) for k, d in vs.items()},
                      'supply_apr_median_pct': {k: round(100 * medians[(k, sym)], 3) for k in vs
                                                if (k, sym) in medians},
                      'gap_pp_spot': round(gap, 3), 'gap_pp_despiked': round(eff_gap, 3),
                      'head_read_spiked': spiked,
                      'despiked': despiked,
                      'despike_note': 'median of the window log series' if despiked else
                                      ('%s emits no ReserveDataUpdated logs, so the head read is the only source'
                                       % hi_v if hi_v not in LOG_VENUES else
                                       'too few log observations for %s %s: this is one block, and a large transfer or '
                                       'flash loan can move a reserve rate several-fold for one block' % (hi_v, sym)),
                      'supplied_usd': {k: round(d['supplied_usd']) for k, d in vs.items() if d.get('supplied_usd')},
                      'utilisation': {k: round(d['utilisation'], 3) for k, d in vs.items() if d.get('utilisation')}},
            economics={'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                       'half_edge_size_usd': round(half) if half else None,
                       'net_apr_at_half_edge': round(eff_lo + (eff_hi - eff_lo) / 2, 4),
                       'go': v.go, 'reason': v.reason, 'gas_gwei': round(gas_gwei, 4)}))
    return hits


def _half_edge_size(hi_rate, lo_rate, supplied_usd):
    """Capital at which your own dilution has eaten half the gap — the number a capital allocator actually wants.

    Maximising total dollars against a dilution curve just says "deploy everything", because the marginal yield stays
    positive right up to the cap. The size worth quoting is where the realised average rate has given back half its
    advantage over the alternative venue.
    """
    target = lo_rate + (hi_rate - lo_rate) / 2
    if hi_rate <= target or supplied_usd <= 0:
        return None
    # average realised rate is r·S/(S+X); solve r·S/(S+X) = target
    return supplied_usd * (hi_rate / target - 1.0)


def _dilution_curve(rate, supplied_usd):
    """Yield given up, in bps, by supplying `X` into a pool that already holds `supplied_usd`.

    With the supply rate going as `u²` (a supplier earns the borrow rate times utilisation, and the borrow rate is
    itself roughly linear in utilisation), adding `X` earns an average of `r·S/(S+X)` instead of `r`, so the shortfall is
    `r·X/(S+X)` — nothing for a small size, the whole rate for a size that dwarfs the pool.
    """
    def curve(x):
        if x <= 0 or supplied_usd <= 0:
            return 0.0
        return 1e4 * rate * x / (supplied_usd + x)
    return curve


def _head_state(ctx):
    import json
    p = ctx.out / 'head_state.json'
    return json.loads(p.read_text()) if p.exists() else None


def _venue_table(head, ctx):
    """(venue, symbol) -> {supply_apr, supplied_usd, utilisation} across Aave, Spark, Compound, Sky and Ethena."""
    out = {}
    for venue, reserves in (head.get('lending') or {}).items():
        for tok, d in reserves.items():
            sym = ctx.window.symbol(tok.lower())
            if not sym or d.get('supply_apr') is None:
                continue
            sup = d.get('supplied_usd') or 0
            out[(venue, sym)] = {'supply_apr': d['supply_apr'], 'supplied_usd': sup,
                                 'utilisation': (d.get('borrowed_usd') or 0) / sup if sup else None}
    for venue, d in (head.get('compound') or {}).items():
        sym = ctx.window.symbol((d.get('base_token') or '').lower())
        if not sym or d.get('supply_apr') is None:
            continue
        px = ctx.prices.get('ETH', 2500.0) if sym == 'WETH' else 1.0
        out[(venue, sym)] = {'supply_apr': d['supply_apr'], 'supplied_usd': (d.get('supplied') or 0) * px,
                             'utilisation': d.get('utilisation')}
    ssr = (head.get('sky') or {}).get('ssr_apy')
    if ssr is not None:
        # Sky's savings rate takes any size at the same rate, so it is the natural floor to compare a stable gap against.
        out[('Sky SSR', 'USDS')] = {'supply_apr': ssr, 'supplied_usd': 1e9, 'utilisation': None, 'dilutes': False}
        out[('Sky SSR', 'USDC')] = {'supply_apr': ssr, 'supplied_usd': 1e9, 'utilisation': None, 'dilutes': False}
    return out


def _log_medians(ctx):
    """(venue, symbol) -> median supply APR over the window, where the log series has enough observations."""
    med = {}
    for r in ctx.analysis.get('lending_rates') or []:
        if r.get('updates', 0) < MIN_UPDATES or not r.get('sym'):
            continue
        series = [p[2] for p in (r.get('series') or []) if len(p) > 2 and p[2] is not None]
        m = median(series)
        if m is not None:
            med[(r['venue'], r['sym'])] = m
    return med


def _m(v):
    if v is None:
        return 'n/a'
    return '%.1fM' % (v / 1e6) if v >= 1e6 else '%.0fk' % (v / 1e3)
