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
        # Pick the venue pair on the *de-spiked* rate, not the spot one. Picking on spot means that during Aave's
        # nightly utilisation spike the highest USDC venue is whichever reserve is momentarily starved, the pair
        # becomes Aave-over-Spark, the de-spiker correctly calls it a spot artifact — and the real standing gap,
        # Compound over Spark, is never compared at all. The spike does not just add a false finding; it hides a
        # true one.
        def effective(v):
            return medians.get((v, sym), vs[v]['supply_apr'])
        hi_v = max(vs, key=effective)
        lo_v = min(vs, key=effective)
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
        fn, basis = marginal_rate_fn(hi_v, sym, hi, head)
        half, best = sized(fn, eff_lo, S) if dilutes else (None, None)
        # Price at the size that maximises dollars over the alternative venue, not at the headline rate: a rate you
        # cannot deploy into is not an edge, and on a kinked market the deployable size is the entire question.
        size = (best or {}).get('size_usd') or S
        eff_at_size = fn(size) if dilutes else eff_hi
        opp = Opportunity(
            name='%s supply spread: %s over %s' % (sym, hi_v, lo_v),
            edge_bps=1e4 * max(eff_at_size - eff_lo, 0.0),
            legs=[Leg('supply %s into %s%s' % (sym, hi_v, ' (rate dilutes as you add)' if dilutes else ' (fixed rate)'),
                      capacity_usd=size)],
            gas_units=300_000, capital_days=365, runs_per_day=1 / 365, competitors=0,
            notes='marginal rate from the venue’s own model (%s); the borrow side is held fixed, so a borrower '
                  'repaying closes the gap sooner than this' % basis)
        v = score(opp, gas_gwei=gas_gwei, eth_usd=eth, min_net_usd=0.0)
        # A gap that could not be de-spiked is a single block's reading. It may be real and it may be the tail of an
        # ALM transfer or a flash loan, and there is no way to tell from one observation, so it ranks below a gap the
        # window's own series confirms rather than sitting beside it as an equal.
        hits.append(Hit(
            detector=NAME, severity='info' if unchecked else 'notable', usd=v.annual_net_usd,
            key='%s:%s/%s' % (sym, hi_v, lo_v),
            title='%s pays %.2fpp more on %s than %s; %s%s'
                  % (sym, eff_gap, hi_v, lo_v,
                     ('best size $%s earns $%s a year over %s' % (_m(best['size_usd']),
                                                                  _m(best['over_low_venue_usd_per_year']), lo_v))
                     if best else ('$%s halves the gap' % _m(half)) if half else 'rate does not dilute with size',
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
                      'utilisation': {k: round(d['utilisation'], 3) for k, d in vs.items() if d.get('utilisation')},
                      'dilution_basis': basis, 'best_size': best,
                      'marginal_apr_ladder': [{'size_usd': x, 'apr_pct': round(100 * fn(x), 3)}
                                              for x in (1e5, 1e6, 5e6, 2.5e7, 1e8)] if dilutes else None},
            economics={'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                       'half_edge_size_usd': round(half) if half else None,
                       'net_apr_at_half_edge': round(eff_lo + (eff_hi - eff_lo) / 2, 4),
                       'go': v.go, 'reason': v.reason, 'gas_gwei': round(gas_gwei, 4)}))
    return hits


def marginal_rate_fn(venue, sym, d, head):
    """`add_usd -> supply APR you would actually earn`, from the venue's own rate model where one is available.

    This replaces a smooth model that was wrong by more than an order of magnitude on exactly the market it mattered
    most for. Lending rates are kinked, and a market sitting a hair above its kink has almost no capacity: Compound v3
    USDC was at 90.77% utilisation against a kink at 90.0%, paying 5.69%, and $1.25M of new supply is the *whole*
    opportunity — $5M takes the rate to 3.22%, below the savings rate you left. The smooth `r·S/(S+X)` model reported
    tens of millions of capacity for that same market, because a smooth curve cannot express a cliff.

    Three sources, in order of what the head state actually carries:
      * **Aave and SparkLend** — the reserve's own IRM parameters (`rate_curves`), so the kink is exact;
      * **Compound** — the Comet's supply rate sampled across utilisations at head time, interpolated here;
      * **anything else** — the old smooth model, and the hit says `modelled` so the number is read as an estimate.
    """
    supplied, borrowed = d.get('supplied_usd') or 0, d.get('borrowed_usd')
    curve = (head.get('rate_curves') or {}).get('%s %s' % (venue, sym))
    if curve and borrowed and supplied > 0:
        from .dollar_rate_outlier import supply_apr
        return (lambda add: supply_apr(curve, borrowed, supplied + add)), 'irm'
    grid = d.get('supply_curve')
    if grid and borrowed and supplied > 0:
        def interp(add):
            u = borrowed / (supplied + add)
            pts = sorted(grid)
            if u <= pts[0][0]:
                return pts[0][1]
            for (u0, r0), (u1, r1) in zip(pts, pts[1:]):
                if u <= u1:
                    return r0 + (r1 - r0) * (u - u0) / max(u1 - u0, 1e-12)
            return pts[-1][1]
        return interp, 'sampled'
    r0 = d.get('supply_apr') or 0.0
    return (lambda add: r0 * supplied / (supplied + add) if supplied > 0 else r0), 'modelled'


def sized(fn, lo_rate, supplied_usd):
    """The two sizes worth quoting: where half the gap is gone, and where total dollars over the alternative peak.

    Reported together because they answer different questions. `half` is the allocator's rule of thumb for how much
    the market can take before the reason for being there is half spent; `best` is the size that literally maximises
    dollars earned over the venue you would otherwise use, and on a kinked market the two can differ by a factor.
    """
    r0 = fn(0.0)
    if r0 <= lo_rate:
        return None, None
    target = lo_rate + (r0 - lo_rate) / 2
    half = None
    best = None
    x = max(supplied_usd, 1e6) * 1e-4
    hi = max(supplied_usd, 1e6) * 10
    while x <= hi:
        r = fn(x)
        if half is None and r <= target:
            half = x
        gain = (r - lo_rate) * x
        if best is None or gain > best[1]:
            best = (x, gain, r)
        x *= 1.15
    return half, (None if not best or best[1] <= 0 else
                  {'size_usd': round(best[0]), 'apr_at_size_pct': round(100 * best[2], 3),
                   'over_low_venue_usd_per_year': round(best[1])})


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
                                 'borrowed_usd': d.get('borrowed_usd'),
                                 'utilisation': (d.get('borrowed_usd') or 0) / sup if sup else None}
    for venue, d in (head.get('compound') or {}).items():
        sym = ctx.window.symbol((d.get('base_token') or '').lower())
        if not sym or d.get('supply_apr') is None:
            continue
        px = ctx.prices.get('ETH', 2500.0) if sym == 'WETH' else 1.0
        # The sampled curve travels with the row: without `borrowed_usd` and `supply_curve` the dilution model falls
        # back to the smooth estimate, which is what overstated Compound USDC's capacity by ~75x.
        out[(venue, sym)] = {'supply_apr': d['supply_apr'], 'supplied_usd': (d.get('supplied') or 0) * px,
                             'borrowed_usd': (d.get('borrowed') or 0) * px,
                             'supply_curve': d.get('supply_curve'), 'utilisation': d.get('utilisation')}
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
        # `analysis.json` stores each point as [block, supply_apr, borrow_apr], so the supply rate is index 1.
        # Index 2 is the *borrow* rate, and reading it here de-spiked every supply rate against a borrow median —
        # a bug that survived a shipped detector because both sides of the comparison were wrong in the same
        # direction, so the gap still looked plausible.
        series = [p[1] for p in (r.get('series') or []) if len(p) > 1 and p[1] is not None]
        m = median(series)
        if m is not None:
            med[(r['venue'], r['sym'])] = m
    return med


def _m(v):
    if v is None:
        return 'n/a'
    return '%.1fM' % (v / 1e6) if v >= 1e6 else '%.0fk' % (v / 1e3)
