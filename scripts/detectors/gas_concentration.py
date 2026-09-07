#!/usr/bin/env python3
"""Base-fee spikes, and the contract whose demand caused each one.

The finding this makes permanent. On 2026-09-07 the base fee rose roughly tenfold between 03:45 and 04:10 UTC, and the
cause turned out to be a swarm of freshly funded accounts hammering three tokenized-stock routers. Establishing that
took bespoke code with the three router addresses written into it, so the check could never fire again on a different
contract.

The generalised form asks the question without naming anyone. Find the windows where the base fee runs well above the
window median, then compare each contract's share of requested gas inside the spike against its share outside it. The
contract whose share rises most is the cause, whatever it happens to be. A spike with no such contract is congestion
rather than one actor, and saying so is also useful.

Requested gas, not gas used, is the right measure: the base fee responds to blocks filling, and a transaction reserves
its limit whether or not it burns it.
"""
import collections

from . import Hit
from window_raw import hx

NAME = 'gas_concentration'
DESCRIPTION = 'base-fee spikes attributed to the contract whose gas demand caused them'
SEVERITY = 'notable'

SPIKE_RATIO = 2.5       # base fee this many times the window median counts as a spike
MIN_SPIKE_BLOCKS = 5    # ignore a single noisy block
MIN_SHARE = 0.10        # a cause must hold at least this share of gas inside the spike


def scan(ctx):
    blocks = ctx.blocks
    if len(blocks) < 60:
        return []
    fees = sorted(b['base_gwei'] for b in blocks)
    med = fees[len(fees) // 2]
    if med <= 0:
        return []
    spike_nums = {b['n'] for b in blocks if b['base_gwei'] >= SPIKE_RATIO * med}
    if len(spike_nums) < MIN_SPIKE_BLOCKS:
        return []

    inside = collections.Counter()
    outside = collections.Counter()
    in_total = out_total = 0
    for b, _ in ctx.window.blocks():
        n = hx(b['number'])
        tgt = inside if n in spike_nums else outside
        for t in b['transactions']:
            if not t.get('to'):
                continue
            g = hx(t['gas'])
            tgt[t['to'].lower()] += g
            if n in spike_nums:
                in_total += g
            else:
                out_total += g
    if not in_total:
        return []

    peak = max(b['base_gwei'] for b in blocks if b['n'] in spike_nums)
    span = (min(spike_nums), max(spike_nums))
    rows = []
    for a, g in inside.most_common(40):
        share_in = g / in_total
        share_out = outside[a] / out_total if out_total else 0.0
        if share_in >= MIN_SHARE and share_in > share_out:
            rows.append({'address': a, 'label': ctx.label(a), 'share_in_spike': round(share_in, 4),
                         'share_outside': round(share_out, 4),
                         'lift': round(share_in / share_out, 1) if share_out > 1e-9 else None,
                         'gas_in_spike': g})
    hits = [Hit(detector=NAME, severity='notable',
                title='base fee peaked %.3f gwei (%.1fx the %.3f gwei median) across %d blocks' % (
                    peak, peak / med, med, len(spike_nums)),
                evidence={'blocks': list(span), 'spike_blocks': len(spike_nums), 'median_gwei': round(med, 4),
                          'peak_gwei': round(peak, 4), 'top_gas_in_spike': rows[:8],
                          'attribution': ('%s holds %.0f%% of requested gas inside the spike against %.1f%% outside'
                                          % (rows[0]['label'] or rows[0]['address'], 100 * rows[0]['share_in_spike'],
                                             100 * rows[0]['share_outside'])) if rows else
                                         'no single contract exceeds the share threshold: broad congestion, not one actor'})]
    return hits
