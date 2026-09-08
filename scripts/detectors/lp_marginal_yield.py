#!/usr/bin/env python3
"""What a concentrated LP position would actually have earned in this window: fees, minus divergence, at real size.

The two things this fixes about the LP table it reads.

**An APR quoted at zero size is not a yield.** `analysis.json` reports `apr_band_1pct` — the rate a concentrated
position would earn if it were infinitesimal beside the liquidity already there. The captive-flow study's whole point
was that the number collapses as you add: 15.8% at $50k into a $1M pool, and the thesis was worth writing only because
that dilution was computed by hand. Here it is computed for every pool, every window, from the liquidity the pool
itself reports. A pool's liquidity expressed as ±b-band capital is `k(b)·C`, where `C` is the full-range-equivalent
capital behind its active liquidity and `k(b) = 1 − 1/√(1+b)`; adding `Y` earns `passive_fees / (k·C + Y)`, which is
the band APR at `Y → 0` and dilutes correctly from there.

**A band narrower than the price moved is a position that was not in range.** The same table reports 5,981% for a
UNI/USDC pool whose price moved 3.0% inside the window — a ±1% position would have been out of range for most of it,
earning nothing. So the band quoted here is the *observed range*, never narrower, and the concentration multiplier
follows from it.

**The band is the assumption, so it is reported rather than buried.** Fee APR goes as `1/band` for small bands, so
the choice moves the answer by more than anything else in the calculation, and no single band is right for every
reader. Checking this against the hand-built captive-flow study makes the point: that study priced a USDC/USDG v4
pool at 14.2% on $1.04M of deployed TVL, while this pool's liquidity `C` implies its incumbent LPs sit in a band of
about ±1.2bp — corroborated by the 0.9bp the price actually moved over five hours. Quote the same pool at ±20bp and
it pays 1.1%; at its own concentration it pays about 20%. Both are true statements about different positions, so the
hit carries a ladder across bands and the headline names the one it used.

With those two corrections the interesting comparison becomes possible, and it is not fees against zero. It is **fees
against divergence**: a position in a band that the price traversed loses against holding, amplified by exactly the
same concentration factor that multiplied its fees. On that UNI pool the window's fees and its divergence are the same
order of magnitude and the sign is not obvious in advance, which is the honest state of a volatile-pair LP and the
opposite of what a four-digit APR implies.

Stable pairs are benchmarked against the risk-free dollar, because that is what the capital would otherwise do.
Volatile pairs are not benchmarked at all — the alternative to LPing ETH/USDC is holding some mix of ETH and USDC, and
this detector has no view on that.
"""
import math

from . import Hit

NAME = 'lp_marginal_yield'
DESCRIPTION = 'concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size'
SEVERITY = 'notable'

MIN_VOLUME = 2.5e5       # a pool below this has too few swaps for a fee rate to mean anything
MIN_BAND = 1e-4          # 1bp: below this a position needs rebalancing faster than a block, so it is not passive
BAND_MULTIPLES = (1, 2, 5, 20)   # the ladder: the observed range, and progressively safer bands around it
SIZES = (1e4, 5e4, 2.5e5, 1e6)
MIN_NET_BPS = 0.02       # window-realised net below this is arithmetic noise, not a thin sample
MIN_NET_APR = 0.01       # 1% a year, annualised from the window, before a pool is worth a line
MIN_SWAPS = 20           # a rate estimated from fewer trades than this is a rumour
STABLE = {'USDC', 'USDT', 'DAI', 'USDS', 'USDe', 'PYUSD', 'RLUSD', 'GHO', 'USDG', 'crvUSD', 'FDUSD', 'USD1', 'AUSD'}


def k_of(band):
    """Capital a ±band concentrated position needs, as a fraction of the full-range capital giving the same liquidity."""
    return 1 - 1 / math.sqrt(1 + band)


def divergence_bps(price_ratio, k):
    """Loss against holding, in bps of position, for a position that stayed in range while the price moved.

    The constant-product result `2√r/(1+r) − 1` is the loss per dollar of *full-range* capital. A concentrated
    position provides the same liquidity with `k` times the capital and takes the same absolute loss, so its loss per
    dollar is `1/k` times larger — the identical multiplier that made its fees look large. Approximate, and only valid
    while the position is in range, which is why the band is never quoted narrower than the move.
    """
    r = max(price_ratio, 1e-9)
    il = 2 * math.sqrt(r) / (1 + r) - 1
    return 1e4 * abs(il) / max(k, 1e-9)


def scan(ctx):
    A = ctx.analysis or {}
    hours = (A.get('window') or {}).get('hours') or 0
    if hours <= 0:
        return []
    bench = ((_head(ctx) or {}).get('sky') or {}).get('ssr_apy') or 0.036

    hits = []
    for r in A.get('lp') or []:
        C = r.get('full_range_capital_usd')
        passive = r.get('passive_fees_usd')
        if not C or passive is None or (r.get('volume_usd') or 0) < MIN_VOLUME:
            continue
        rng = (r.get('price_range_pct') or 0) / 100.0
        band = max(rng, MIN_BAND)
        k = k_of(band)
        cap = k * C                                  # the pool's own liquidity, priced as band capital
        if cap <= 0:
            continue
        stable = bool(r.get('stable_pair'))
        div_bps = 0.0 if stable and rng < 5e-4 else divergence_bps(1 + rng, k)
        # The same calculation across wider bands, so the reader can see how much of the answer is the band choice.
        band_ladder = []
        for mult in BAND_MULTIPLES:
            b = max(rng * mult, MIN_BAND)
            kb = k_of(b)
            f = 1e4 * passive / (kb * C + SIZES[0])
            d = 0.0 if stable and rng < 5e-4 else divergence_bps(1 + rng, kb)
            band_ladder.append({'band_pct': round(100 * b, 4),
                                'apr_pct_at_%s' % int(SIZES[0]): round(100 * (f - d) * 1e-4 * 8760 / hours, 2)})

        ladder = []
        best = None
        for Y in SIZES:
            fee_bps = 1e4 * passive / (cap + Y)       # fees over the window, per dollar of position
            net_bps = fee_bps - div_bps
            hold_bps = 1e4 * bench * hours / 8760 if stable else 0.0
            over = net_bps - hold_bps
            ladder.append({'size_usd': Y, 'fee_bps_window': round(fee_bps, 3),
                           'divergence_bps_window': round(div_bps, 3), 'net_bps_window': round(net_bps, 3),
                           'over_benchmark_usd': round(over * 1e-4 * Y, 2),
                           'annualised_net_apr_pct': round(100 * net_bps * 1e-4 * 8760 / hours, 2)})
            if best is None or over * Y > best[0]:
                best = (over * Y, ladder[-1])
        row = best[1] if best else None
        if row is None or row['net_bps_window'] < MIN_NET_BPS:
            continue
        # Gate on the annualised rate, because an LP position is a standing one and the window is a sample of it —
        # but keep the sample size in the evidence, since a two-hour window annualises by a factor of 4,380 and a
        # reader is entitled to see what the estimate rests on.
        if row['annualised_net_apr_pct'] < 100 * MIN_NET_APR or (r.get('swaps') or 0) < MIN_SWAPS:
            continue

        hits.append(Hit(
            detector=NAME, key=r['pool'],
            severity='notable' if (stable and row['net_bps_window'] > 0) else 'info',
            usd=row['over_benchmark_usd'] * 8760 / hours,
            title='%s %s: %s in a ±%.2f%% band earns %.1fbp of fees less %.1fbp of divergence over %.1fh (%.1f%% a year if it repeats)'
                  % (r.get('venue'), r.get('pair') or r['pool'][:10], _m(row['size_usd']), 100 * band,
                     row['fee_bps_window'], row['divergence_bps_window'], hours, row['annualised_net_apr_pct']),
            evidence={'pool': r['pool'], 'venue': r.get('venue'), 'pair': r.get('pair'),
                      'stable_pair': stable, 'window_hours': round(hours, 3),
                      'observed_price_range_pct': round(100 * rng, 4), 'band_quoted_pct': round(100 * band, 4),
                      'concentration_multiplier': round(1 / k, 1), 'band_ladder': band_ladder,
                      'pool_band_capital_usd': round(cap), 'full_range_capital_usd': round(C),
                      'passive_fees_usd': round(passive, 2), 'volume_usd': round(r.get('volume_usd') or 0),
                      'swaps': r.get('swaps'), 'annualisation_factor': round(8760 / hours, 1),
                      'n_takers': r.get('n_takers'), 'top_taker': r.get('top_taker'),
                      'top_taker_share': r.get('top_taker_share'), 'taker_herfindahl': r.get('taker_herfindahl'),
                      'apr_band_1pct_as_reported': r.get('apr_band_1pct'),
                      'ladder': ladder,
                      'why': ('fee yield priced at the band the price actually stayed inside, at a size that dilutes '
                              'the pool’s own liquidity, net of the divergence that the same concentration amplifies'
                              + ('' if stable else '; no benchmark is applied — the alternative to LPing a volatile '
                                                  'pair is holding the pair, and this detector has no view on that'))},
            # The annualised net rate is the strategy-facing number, so it goes in `economics` where the findings
            # ledger reads it and the strategy book inherits it as a quote. Without this a linked strategy re-quotes
            # as "present, no rate", which is the least useful of the three possible answers.
            economics={'net_apr': round(row['annualised_net_apr_pct'] / 100, 4),
                       'net_per_year_usd': round(row['over_benchmark_usd'] * 8760 / hours),
                       'size_usd': row['size_usd'], 'band_pct': round(100 * band, 4),
                       'go': bool(stable and row['annualised_net_apr_pct'] / 100 > bench),
                       'reason': ('nets %.2f%% a year at $%s in a ±%.3f%% band against a %.2f%% savings rate'
                                  % (row['annualised_net_apr_pct'], format(round(row['size_usd']), ','),
                                     100 * band, 100 * bench)) if stable else
                                 ('nets %.2f%% a year at $%s in a ±%.3f%% band, before any view on holding the pair'
                                  % (row['annualised_net_apr_pct'], format(round(row['size_usd']), ','), 100 * band))}))
    hits.sort(key=lambda h: -(h.usd or 0))
    return hits[:10]


def _head(ctx):
    import json
    p = ctx.out / 'head_state.json'
    return json.loads(p.read_text()) if p.exists() else None


def _m(v):
    for unit, scale in (('M', 1e6), ('k', 1e3)):
        if abs(v) >= scale:
            return '$' + format(round(v / scale, 1), ',') + unit
    return '$' + format(round(v), ',')
