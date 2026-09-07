#!/usr/bin/env python3
"""Every dollar rate on the board against the risk-free dollar, priced by how much new supply the rate survives.

Two blind spots this closes, both found by looking at what `rate_dispersion` could not see.

**A single-venue outlier is invisible to a cross-venue comparison.** `rate_dispersion` asks "does this asset pay more
here than there", so an asset listed on exactly one venue can pay anything at all and never be reported. On
2026-09-07 Aave's USDtb reserve was paying **8.05%** — the highest dollar supply rate anywhere in the complex, against
3.59% on Aave USDC and 3.60% on the Sky savings rate — and no detector said a word, because USDtb is on Aave and
nowhere else. The right benchmark for a dollar is not the same dollar elsewhere; it is the *risk-free dollar*.

**A rate without its curve cannot be sized, and an unsized rate is a headline, not an opportunity.** A lending rate is
a point on a kinked function of utilisation, so the number that decides whether 8.05% is worth $5k a year or $5M is
how far the reserve sits above its kink. USDtb sat $626k above it: supply $626k and the rate collapses from 8.05% to
2.56%, below the savings rate you left. The detector therefore reports the *marginal* APR at several sizes and the
size that maximises dollars earned over the benchmark, from the reserve's own IRM parameters, and lets
`economics.py` deliver the verdict.

The same arithmetic run in reverse gives the second finding for free: **available liquidity**. A reserve at 100%
utilisation pays a spectacular rate and cannot be exited, and Aave's $2.16B USDC reserve does exactly that for about
half an hour every night — $503 of available liquidity on 2026-09-07 at 23:41 UTC. For any strategy whose exit leg is
that reserve, a daily blackout is a risk fact, not a yield.
"""
from . import Hit
from economics import Opportunity, Leg, score

NAME = 'dollar_rate_outlier'
DESCRIPTION = 'dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve'
SEVERITY = 'notable'

DOLLARS = {'USDC', 'USDT', 'DAI', 'USDS', 'USDe', 'GHO', 'PYUSD', 'RLUSD', 'USDG', 'USDtb', 'FRAX', 'LUSD', 'crvUSD',
           'sUSDe', 'sUSDS', 'USD1', 'AUSD', 'FDUSD', 'EURC'}
MIN_GAP = 0.005          # 50bps over the benchmark before it is worth a line
MIN_SUPPLIED = 1e6       # a reserve smaller than this cannot absorb a position worth opening
SIZES = (1e5, 1e6, 1e7, 5e7)
BLACKOUT_SHARE = 0.001   # available liquidity below a tenth of a percent of the reserve is an exit that is not there
SPIKE_RATIO = 1.5        # head read this many times the window median is a spike, not a rate
MIN_UPDATES = 20         # observations before a log-derived median means anything
# Venues that publish rate updates as logs, so a head read on them *can* be checked against the window. When one of
# these cannot be de-spiked the read is a single block that nothing corroborates, which is a weaker claim than a
# read from a venue that publishes nothing — the same distinction `rate_dispersion` makes.
LOG_VENUES = {'Aave v3', 'SparkLend'}


def borrow_apr(curve, util):
    """Aave's kinked variable-rate curve. Below the kink it is linear in utilisation; above it, steep."""
    o = curve.get('optimal') or 0.9
    base, s1, s2 = curve.get('base', 0.0), curve.get('slope1', 0.05), curve.get('slope2', 0.5)
    if util <= o:
        return base + s1 * (util / o if o else 0)
    return base + s1 + s2 * (util - o) / max(1 - o, 1e-9)


def supply_apr(curve, borrowed, supplied):
    """What a supplier earns: the borrow rate, shared over everyone supplying, less the reserve factor."""
    if supplied <= 0:
        return 0.0
    u = min(borrowed / supplied, 1.0)
    return borrow_apr(curve, u) * u * (1 - curve.get('reserve_factor', 0.1))


def scan(ctx):
    hs = _head(ctx)
    if not hs:
        return []
    lending, curves = hs.get('lending') or {}, hs.get('rate_curves') or {}
    medians = _log_medians(ctx)
    bench, bench_name = _benchmark(hs, lending)
    if bench is None:
        return []

    hits = []
    for venue, rows in lending.items():
        for addr, r in rows.items():
            sym = r.get('sym')
            sup_usd, bor_usd = r.get('supplied_usd'), r.get('borrowed_usd')
            if sym not in DOLLARS or not sup_usd or sup_usd < MIN_SUPPLIED:
                continue
            avail = sup_usd - (bor_usd or 0)
            curve = curves.get('%s %s' % (venue, sym))

            # An exit that is not there is worth reporting whatever the rate is doing.
            if avail <= BLACKOUT_SHARE * sup_usd:
                hits.append(Hit(
                    detector=NAME, key='%s:%s:blackout' % (venue, sym), severity='high', usd=sup_usd,
                    title='%s %s is fully utilised: $%s of exit liquidity on a $%s reserve'
                          % (venue, sym, _m(avail), _m(sup_usd)),
                    evidence={'venue': venue, 'asset': sym, 'supplied_usd': round(sup_usd),
                              'borrowed_usd': round(bor_usd or 0), 'available_usd': round(avail),
                              'utilisation': round((bor_usd or 0) / sup_usd, 6),
                              'supply_apr_pct': round(100 * r['supply_apr'], 3),
                              'borrow_apr_pct': round(100 * r['borrow_apr'], 3),
                              'why': 'nobody can withdraw from this reserve until a borrower repays or a supplier '
                                     'arrives; any strategy whose exit leg is this reserve is blocked, and the high '
                                     'rate it prints is the symptom rather than an opportunity'}))

            # De-spike before pricing. The head is one block, and the reserve this detector was written for prints
            # 12.87% for about half an hour every night while an account withdraws its supply — annualising that read
            # would report a $3.0M-a-year opportunity that exists for thirty minutes and is unenterable anyway,
            # because the same event takes exit liquidity to zero. Where the window's own log series has enough
            # observations, the median is what gets priced and the spot read is reported beside it.
            spot = r.get('supply_apr') or 0
            med = medians.get((venue, sym))
            spiked = med is not None and spot > SPIKE_RATIO * max(med, 1e-9)
            # A log venue we could not de-spike is an unchecked one-block read. SparkLend's USDT reserve printed 6.05%
            # on 2026-09-07 immediately after Spark's own allocator withdrew $46M from it, and the window carried only
            # sixteen updates — under the threshold at which a median means anything — so nothing contradicted the
            # read and it would otherwise have been filed as a standing 2.45pp edge. It normalised within the hour.
            unchecked = venue in LOG_VENUES and med is None
            eff_spot = med if spiked else spot
            gap = eff_spot - bench
            if gap < MIN_GAP:
                continue
            ladder, best = [], None
            # When the spot read is a spike, the reserve's *current* utilisation is the spike too, so the ladder is
            # built from the utilisation implied by the de-spiked rate rather than from the spiked balances.
            base_sup = sup_usd if not spiked else _implied_supplied(curve, bor_usd, eff_spot, sup_usd)
            if curve and bor_usd:
                for s in SIZES:
                    apr = supply_apr(curve, bor_usd, base_sup + s)
                    ladder.append({'size_usd': s, 'marginal_apr_pct': round(100 * apr, 3),
                                   'over_benchmark_usd_per_year': round((apr - bench) * s)})
                best = _best_size(curve, bor_usd, base_sup, bench)
            # Priced at the size that actually maximises dollars over the benchmark, not at the headline rate.
            size = (best or {}).get('size_usd') or min(sup_usd * 0.1, 1e6)
            eff = (best or {}).get('apr', r['supply_apr'])
            v = score(Opportunity(
                name='%s %s supply over %s' % (venue, sym, bench_name),
                edge_bps=1e4 * (eff - bench),
                legs=[Leg('supply %s to %s' % (sym, venue), capacity_usd=size)],
                gas_units=250_000, capital_days=365, runs_per_day=1 / 365, competitors=0,
                notes='the marginal APR is computed from the reserve’s own IRM at the sized position, holding '
                      'borrows fixed; a borrower repaying closes it faster than this assumes'),
                gas_gwei=_gas(ctx), eth_usd=(ctx.prices.get('ETH') or 2500), min_net_usd=0.0)
            hits.append(Hit(
                detector=NAME, key='%s:%s' % (venue, sym),
                severity=('info' if (spiked or unchecked or not curve) else ('notable' if gap >= 0.02 else 'info')),
                usd=(best or {}).get('over_benchmark_usd_per_year'),
                title='%s %s pays %.2f%%%s against the %s at %.2f%%; %s'
                      % (venue, sym, 100 * eff_spot,
                         (' on the window median, %.2f%% spot [spike]' % (100 * spot)) if spiked else '',
                         bench_name, 100 * bench,
                         ('best size $%s earns $%s a year over it' % (_m(best['size_usd']),
                                                                     _m(best['over_benchmark_usd_per_year'])))
                         if best else 'no rate curve, so the size it survives is unknown')
                      + (' [one-block read, de-spiking unavailable]' if unchecked else ''),
                evidence={'venue': venue, 'asset': sym, 'supply_apr_spot_pct': round(100 * spot, 3),
                          'supply_apr_window_median_pct': None if med is None else round(100 * med, 3),
                          'spiked': spiked, 'despike_unavailable': unchecked,
                          'benchmark': bench_name, 'benchmark_pct': round(100 * bench, 3),
                          'gap_pp': round(100 * gap, 3), 'supplied_usd': round(sup_usd),
                          'borrowed_usd': round(bor_usd or 0), 'available_usd': round(avail),
                          'utilisation': round((bor_usd or 0) / sup_usd, 4), 'curve': curve,
                          'marginal_apr_ladder': ladder, 'best': best,
                          'why': 'a headline rate is a point on a kinked curve; what it is worth is the marginal APR '
                                 'at the size you can actually put in, over the dollar you would otherwise hold'},
                economics={'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                           'go': v.go, 'reason': v.reason}))
    return hits


def _best_size(curve, borrowed, supplied, bench, hi=2e8):
    """The size that maximises (marginal APR − benchmark) × size. Not the largest, and not the headline."""
    best = None
    s = 1e4
    while s <= hi:
        apr = supply_apr(curve, borrowed, supplied + s)
        gain = (apr - bench) * s
        if best is None or gain > best['over_benchmark_usd_per_year']:
            best = {'size_usd': s, 'apr': apr, 'marginal_apr_pct': round(100 * apr, 3),
                    'over_benchmark_usd_per_year': round(gain)}
        s *= 1.25
    return best if best and best['over_benchmark_usd_per_year'] > 0 else None


def _implied_supplied(curve, borrowed, target_apr, fallback):
    """The supply the reserve had when it was paying `target_apr`, holding borrows fixed.

    Needed because a spike is a *balance* event: the 12.87% read and the $2.16B supplied are the same fact, so
    de-spiking the rate without de-spiking the balance would price the calm rate against the spiked utilisation.
    """
    if not curve or not borrowed:
        return fallback
    lo, hi = borrowed, borrowed * 20
    for _ in range(60):
        mid = (lo + hi) / 2
        if supply_apr(curve, borrowed, mid) > target_apr:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _log_medians(ctx):
    """(venue, symbol) -> median supply APR over the window, from the reserve's own update logs."""
    from window_raw import median
    med = {}
    for r in (ctx.analysis or {}).get('lending_rates') or []:
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


def _benchmark(hs, lending):
    """The risk-free dollar: the savings rate an issuer pays on its own dollar, in unlimited size and at no venue risk.

    Falling back to a lending venue's own USDC rate would make the comparison circular, so the fallback is used only
    when the savings rate cannot be read, and it says which one it used.
    """
    ssr = (hs.get('sky') or {}).get('ssr_apy')
    if ssr:
        return ssr, 'Sky savings rate'
    best = 0.0
    for rows in lending.values():
        for r in rows.values():
            if r.get('sym') == 'USDC' and (r.get('supplied_usd') or 0) > 1e8:
                best = max(best, r.get('supply_apr') or 0)
    return (best, 'largest USDC reserve') if best else (None, None)


def _head(ctx):
    import json
    p = ctx.out / 'head_state.json'
    return json.loads(p.read_text()) if p.exists() else None


def _gas(ctx):
    from window_raw import median
    return median([b['base_gwei'] for b in ctx.blocks]) or 1.0


def _m(v):
    v = v or 0
    for unit, scale in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= scale:
            return format(round(v / scale, 1), ',') + unit
    return format(round(v), ',')
