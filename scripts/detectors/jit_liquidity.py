#!/usr/bin/env python3
"""Just-in-time liquidity: how much of a pool's fee stream is taken by liquidity that arrives for one swap.

The finding this makes permanent. The passive-LP thesis in this repo prices a pool by its fee yield on in-range
capital, and that number is only honest if the fees actually reach passive liquidity. A JIT operator mints a
concentrated position immediately before a large swap and burns it immediately after, collecting the fee without ever
carrying inventory risk, and every dollar it takes is a dollar the fee-yield calculation credits to the passive LP who
did carry that risk. The test was run once by hand on 2026-09-06 and again on 2026-09-07, both times as throwaway code.

Two readings come out of it, and the second is the one worth keeping.

  * **Per pool**: the share of fees that went to JIT. Above roughly a tenth, a quoted LP APR is meaningfully overstated
    and the pool should be priced on `passive_fees_usd`, not `fees_usd`.
  * **Per window**: whether JIT is a material tax at all. On both 2026-09-07 windows it took $235 and $44 against
    thousands of dollars of pool fees — under 1% on every deep pool. That is a negative result, and recording it every
    window is exactly how the loop would notice the day it stops being one.

The operator economics are priced through `economics.py` as a race, because a JIT bot pays gas on the attempts it
loses as well as the ones it wins.
"""
from . import Hit
from economics import Opportunity, Leg, score

NAME = 'jit_liquidity'
DESCRIPTION = 'fee share taken by liquidity minted for a single swap, per pool and per window'
SEVERITY = 'info'

MIN_POOL_FEES = 20.0     # a pool below this earns too little for a share to mean anything
POOL_SHARE = 0.10        # JIT share above which a quoted passive APR is materially overstated
JIT_GAS = 400_000        # mint + burn, typically two transactions bracketing the victim swap


def scan(ctx):
    A = ctx.analysis or {}
    jit = A.get('jit') or {}
    lp = A.get('lp') or []
    if not jit:
        return []

    total_fees = sum((r.get('fees_usd') or 0) for r in lp)
    taken = jit.get('fee_taken_usd') or 0.0
    episodes = jit.get('episodes') or 0
    ops = jit.get('operators') or []
    share = taken / total_fees if total_fees else 0.0

    hits = []
    # Per-window: the fact a passive LP needs, stated as a share rather than a dollar amount so windows compare.
    econ = None
    if episodes:
        # A higher observed cost scenario for competing execution; direct bids and guaranteed adjacency are unpriced.
        gas_gwei = ctx.gas_quote(race=True)['gwei']
        eth = (A.get('price_basis') or {}).get('ETH') or 2500.0
        v = score(Opportunity(
            name='JIT liquidity, one episode',
            edge_usd=taken / episodes,          # a flat fee per episode, not bps on the bracketed notional
            legs=[Leg('mint and burn a concentrated position around one swap')],
            gas_units=JIT_GAS, runs_per_day=episodes * 24 / max(A['window']['hours'], 0.1),
            race=True, competitors=max(len(ops) - 1, 0),
            notes='a race: gas is paid on losing attempts too, and the winner is whoever the builder ordered first. '
                  'Gas is priced at the window median base fee plus median tip, which a bracket bidding for adjacency '
                  'would exceed, so the verdict is an upper bound on the operator economics'),
            gas_gwei=gas_gwei, eth_usd=eth, min_net_usd=0.0)
        econ = {'net_apr': round(v.net_apr, 4), 'net_per_year_usd': round(v.annual_net_usd),
                'net_per_run_usd': round(v.net_per_run_usd, 2), 'go': v.go, 'reason': v.reason,
                'gas_gwei': round(gas_gwei, 4), 'edge_per_episode_usd': round(taken / episodes, 2),
                'win_rate': round(v.win_rate, 3)}
    hits.append(Hit(
        detector=NAME, key='window', severity='notable' if share >= POOL_SHARE else 'info', usd=taken,
        title='JIT took $%.0f of $%.0f pool fees (%.2f%%) across %d episodes by %d operator(s)'
              % (taken, total_fees, 100 * share, episodes, len(ops)),
        evidence={'episodes': episodes, 'fee_taken_usd': round(taken, 2), 'pool_fees_usd': round(total_fees, 2),
                  'share_of_fees': round(share, 4), 'swap_usd_bracketed': jit.get('swap_usd_bracketed'),
                  'top_operators': ops[:5],
                  'why': 'fees taken by liquidity that was not at risk are credited to passive LPs by any yield '
                         'number computed from total fees; the honest input is passive_fees_usd'},
        economics=econ))

    # Per pool: where a quoted APR is actually overstated.
    for r in lp:
        f = r.get('fees_usd') or 0
        j = r.get('fees_to_jit_usd') or 0
        if f < MIN_POOL_FEES or j <= 0 or j / f < POOL_SHARE:
            continue
        hits.append(Hit(
            detector=NAME, key=r['pool'], severity='notable', usd=j,
            title='%s %s: JIT took %.1f%% of fees, so its quoted LP yield is overstated'
                  % (r.get('venue'), r.get('pair') or r['pool'][:10], 100 * j / f),
            evidence={'pool': r['pool'], 'venue': r.get('venue'), 'pair': r.get('pair'),
                      'fees_usd': round(f, 2), 'fees_to_jit_usd': round(j, 2),
                      'passive_fees_usd': round(r.get('passive_fees_usd') or 0, 2),
                      'volume_usd': round(r.get('volume_usd') or 0),
                      'apr_band_1pct_all_fees': r.get('apr_band_1pct'),
                      'apr_band_1pct_passive_only': (round(r['apr_band_1pct'] * (1 - j / f), 6)
                                                     if r.get('apr_band_1pct') else None),
                      'why': 'price this pool on passive fees; the JIT share never reaches liquidity that stayed'}))
    return hits
