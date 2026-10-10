#!/usr/bin/env python3
"""Search and estimation helpers shared by the Move and Starknet adapters (not an adapter itself: `load_all` skips
modules whose name starts with an underscore)."""
import math


def kary_first_at(read, lo, hi, ts, fanout=100):
    """First integer x in [lo, hi] with read(x) >= ts, for a non-decreasing read; hi if none is earlier.

    `read(list_of_x)` returns {x: value} (missing x are skipped). Each round reads `fanout` evenly spaced points and
    narrows the bracket to the gap that straddles ts, so a span of 10^6 heights is settled in three or four round trips
    instead of twenty — which matters when one read is a 0.3 s HTTP call or one multi-get answers 200 at once.
    """
    while hi - lo > fanout:
        step = (hi - lo) / fanout
        pts = sorted({lo + int(round(i * step)) for i in range(fanout + 1)} | {lo, hi})
        vals = read(pts)
        prev, nxt = lo, hi
        for x in pts:
            v = vals.get(x)
            if v is None:
                continue
            if v >= ts:
                nxt = x
                break
            prev = x
        if nxt == lo:
            return lo
        if (prev, nxt) == (lo, hi):      # nothing readable inside the bracket: fall back to bisection
            mid = (lo + hi) // 2
            v = read([mid]).get(mid)
            if v is None:
                break
            lo, hi = (lo, mid) if v >= ts else (mid, hi)
            continue
        lo, hi = prev, nxt
    vals = read(list(range(lo, hi + 1)))
    for x in range(lo, hi + 1):
        if vals.get(x) is not None and vals[x] >= ts:
            return x
    return hi


def ratio_estimate(ys, xs, X, N=None):
    """(Y, se) for Y = X * sum(y)/sum(x): the ratio estimator, with its variance from the residuals y - r x.

    Used for "user transactions = exact total x sampled user share": X is known exactly, so only the share is
    estimated, and its error is far smaller than estimating the user count from the sample alone.
    """
    n = len(ys)
    sx = float(sum(xs))
    if n == 0 or sx <= 0:
        return None, None
    r = sum(ys) / sx
    if n < 2:
        return X * r, None
    xbar = sx / n
    s2 = sum((y - r * x) ** 2 for y, x in zip(ys, xs)) / (n - 1)
    fpc = (1.0 - n / N) if N else 1.0
    var_r = max(fpc, 0.0) * s2 / (n * xbar * xbar)
    return X * r, X * math.sqrt(var_r)


def seeded_bracket(read_one, ts, head, head_ts, rate, floor=0, min_span=2000, widen=0.05):
    """(lo, hi) around the first height at or after ts, guessed from the observed rate and widened until it holds.

    read_one(x) -> timestamp of height x (or None). The guess is head - (head_ts - ts) * rate; the bracket starts at
    max(min_span, widen * distance) either side and doubles until read_one(lo) < ts <= read_one(hi).
    """
    guess = int(head - (head_ts - ts) * rate)
    span = max(min_span, int(abs(head_ts - ts) * rate * widen))
    lo, hi = max(floor, guess - span), min(head, guess + span)
    for _ in range(40):
        v = read_one(lo)
        if lo <= floor or (v is not None and v < ts):
            break
        lo, span = max(floor, lo - span), span * 2
    for _ in range(40):
        v = read_one(hi)
        if hi >= head or (v is not None and v >= ts):
            break
        hi, span = min(head, hi + span), span * 2
    return lo, hi
