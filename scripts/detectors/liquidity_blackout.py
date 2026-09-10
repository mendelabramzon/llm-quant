#!/usr/bin/env python3
"""Reserves whose exit closes: episodes where a lending market's withdrawable liquidity collapses, and when they happen.

The finding this makes permanent. On 2026-09-07 at 23:41 UTC, Aave's $2.16B USDC reserve stood at 100.0000%
utilisation with **$503 of available liquidity**, after an account withdrew about $152M of supply. It was read off a
head state by hand, filed as a sentence, and would have been rediscovered from scratch or not at all. Two windows
later the cross-chain scan found the same shape everywhere: on the dollar surface the binding constraint is almost
never the rate, it is whether the money can leave — seven of twenty cross-chain switches were capped by the source
reserve's withdrawable liquidity rather than by the destination's rate curve.

So this is the detector for the constraint rather than the yield.

**Why it reads utilisation out of the rate.** The window records `ReserveDataUpdated` per reserve, which carries rates,
not balances. Inverting the pool's own published borrow rate through its IRM recovers the utilisation the pool was
evaluated at — the same trick `multichain.py` uses, and for the same reason: the aToken ratio is a different number
and, near a kink, a very different one. Given utilisation and the reserve's size, available liquidity is
`supplied x (1 - u)`, which is what a supplier can actually withdraw.

**Why the time of day is in the evidence.** A blackout that happens once is an event. A blackout that lands in the same
minutes every night is a *schedule*, and a schedule is a fact you can plan an exit around — or be trapped by. The hit
therefore reports the UTC clock time of each episode, and the ledger's recurrence column does the rest across windows.
A one-hour window can only ever see a fragment of this; ten hours spanning midnight sees the whole thing.

What it does not claim: the cause. An episode is a measurement of utilisation over time, not an attribution to any
actor. `window_followups.py` and the largest-position-change table are where the counterparty is chased.
"""
import collections

from . import Hit

NAME = 'liquidity_blackout'
DESCRIPTION = 'lending reserves whose withdrawable liquidity collapses, and the time of day it happens'
SEVERITY = 'high'

HIGH_U = 0.985          # utilisation at which an exit is effectively closed for anything but dust
WARN_U = 0.95           # a squeeze worth noting even if the door has not shut
MIN_SUPPLIED_USD = 5e6  # a reserve smaller than this cannot trap a position worth reporting
MIN_POINTS = 3          # rate observations before a series describes anything
MIN_EPISODE_S = 60      # a single block at 100% is a flash loan, not a blackout


def borrow_apr(curve, u):
    o = curve.get('optimal') or 0.9
    base, s1, s2 = curve.get('base', 0.0), curve.get('slope1', 0.05), curve.get('slope2', 0.5)
    if u <= o:
        return base + s1 * (u / o if o else 0)
    return base + s1 + s2 * (u - o) / max(1 - o, 1e-9)


def implied_u(curve, rate):
    """Utilisation the pool's own curve was evaluated at to publish `rate`. None when the curve carries no slope."""
    if not curve or rate is None:
        return None
    if abs(curve.get('slope1', 0)) < 1e-12 and abs(curve.get('slope2', 0)) < 1e-12:
        return None
    if borrow_apr(curve, 1.0) < rate - 1e-12:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(120):
        mid = (lo + hi) / 2
        if borrow_apr(curve, mid) < rate:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def scan(ctx):
    import json
    hp = ctx.out / 'head_state.json'
    if not hp.exists():
        return []
    hs = json.loads(hp.read_text())
    curves = hs.get('rate_curves') or {}
    lending = hs.get('lending') or {}
    ts = {b['n']: b['ts'] for b in ctx.blocks}
    rows = (ctx.analysis or {}).get('lending_rates') or []

    hits = []
    for row in rows:
        venue, sym = row.get('venue'), row.get('sym')
        # Complete, log-ordered final updates per block prevent atomic rate spikes from being
        # carried forward. Old sampled series cannot establish duration reliably; re-analyze first.
        series = row.get('block_end_series') or []
        if len(series) < MIN_POINTS:
            continue
        curve = curves.get('%s %s' % (venue, sym))
        reserve = (lending.get(venue) or {}).get((row.get('reserve') or '').lower()) or {}
        supplied = reserve.get('supplied_usd')
        if not curve or not supplied or supplied < MIN_SUPPLIED_USD:
            continue

        pts = []
        for p in series:
            n, _sup, bor = p[0], p[1], p[2]
            u = implied_u(curve, bor)
            if u is not None and n in ts:
                pts.append((ts[n], n, u))
        if len(pts) < MIN_POINTS:
            continue
        pts.sort(key=lambda p: p[0])

        # A rate holds until the next update, so an episode runs from the observation that crossed the threshold to
        # the observation that came back under it. The last point is carried to the window's end, and that fact is
        # recorded — an episode still open when the window closes has an unknown duration, not a short one.
        last_ts = ctx.blocks[-1]['ts'] if ctx.blocks else pts[-1][0]
        episodes, cur = [], None
        for i, (t, n, u) in enumerate(pts):
            end = pts[i + 1][0] if i + 1 < len(pts) else last_ts
            if u >= HIGH_U:
                if cur is None:
                    cur = {'start_ts': t, 'start_block': n, 'end_ts': end, 'peak_u': u, 'peak_block': n, 'points': 1}
                else:
                    cur['end_ts'] = end
                    cur['points'] += 1
                    if u > cur['peak_u']:
                        cur['peak_u'], cur['peak_block'] = u, n
            elif cur is not None:
                episodes.append(cur)
                cur = None
        if cur is not None:
            cur['open_at_window_end'] = True
            episodes.append(cur)
        episodes = [e for e in episodes if e['end_ts'] - e['start_ts'] >= MIN_EPISODE_S or e['points'] > 1]

        us = sorted(u for _, _, u in pts)
        peak_u = us[-1]
        median_u = us[len(us) // 2]
        if not episodes and peak_u < WARN_U:
            continue

        worst = max(episodes, key=lambda e: e['end_ts'] - e['start_ts']) if episodes else None
        avail_at_peak = supplied * (1 - peak_u)
        sev = 'high' if episodes else 'notable'
        if episodes:
            title = ('%s %s exit liquidity squeezed %s for %s: approximately %s available on a %s reserve at %.4f%% utilisation'
                     % (venue, sym, _clock(worst['start_ts']), _dur(worst['end_ts'] - worst['start_ts']),
                        _m(avail_at_peak), _m(supplied), 100 * peak_u))
        else:
            title = ('%s %s squeezed to %.2f%% utilisation: %s withdrawable on a %s reserve'
                     % (venue, sym, 100 * peak_u, _m(avail_at_peak), _m(supplied)))

        hits.append(Hit(
            detector=NAME, key='%s:%s' % (venue, sym), severity=sev, usd=supplied,
            title=title,
            evidence={
                'venue': venue, 'asset': sym, 'reserve': row.get('reserve'),
                'supplied_usd': round(supplied),
                'utilisation_peak': round(peak_u, 6), 'utilisation_median': round(median_u, 6),
                'available_at_peak_usd': round(avail_at_peak),
                'available_at_median_usd': round(supplied * (1 - median_u)),
                'observations': len(pts),
                'window_hours': round((pts[-1][0] - pts[0][0]) / 3600, 2),
                'episodes': [{'from_utc': _iso(e['start_ts']), 'to_utc': _iso(e['end_ts']),
                              'clock': _clock(e['start_ts']), 'minutes': round((e['end_ts'] - e['start_ts']) / 60, 1),
                              'peak_utilisation': round(e['peak_u'], 6),
                              'available_at_peak_usd': round(supplied * (1 - e['peak_u'])),
                              'peak_block': e['peak_block'],
                              'open_at_window_end': e.get('open_at_window_end', False)}
                             for e in episodes[:8]],
                'utilisation_source': 'inverted from the reserve’s published borrow rate through its own IRM',
                'why': 'High utilisation limits aggregate withdrawals. Available amounts are estimates from '
                       'endpoint supply times (1 - historical utilisation), not historical cash balance reads '
                       'or account-specific withdrawability. The curve is also taken from the endpoint.',
                'next_step': 'any strategy whose exit leg is this reserve must either size to the trough of this '
                             'series or hold through it; the ledger’s recurrence column says whether the '
                             'episode is a schedule or an accident'}))
    return sorted(hits, key=lambda h: (-len(h.evidence['episodes']), -(h.usd or 0)))


def _iso(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(timespec='seconds')


def _clock(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime('at %H:%M UTC')


def _dur(s):
    if s < 90:
        return '%d seconds' % s
    if s < 5400:
        return '%.0f minutes' % (s / 60)
    return '%.1f hours' % (s / 3600)


def _m(v):
    v = v or 0
    for unit, scale in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= scale:
            return '$' + format(round(v / scale, 1), ',') + unit
    return '$' + format(round(v), ',')
