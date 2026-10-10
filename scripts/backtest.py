#!/usr/bin/env python3
"""Out-of-sample and multiple-testing discipline for every strategy this repo backtests.

Why. Until now the loop priced strategies from windows: one hour of a funding rate, five hours of a rate gap. The
history collectors changed that (a year of hourly funding, 181 days of sUSDe swaps, every Pendle and Polymarket market
since launch), and with history comes the standard way to fool yourself: try thirty thresholds on two hundred markets,
report the best, and quote its in-sample Sharpe. ROADMAP P2 item 9 asked for a harness that makes that impossible to
do by accident. This is it, small on purpose, pure Python (the repo runs without numpy):

  * **time splits, never random ones** — `cutoff_index` / `walk_forward`: choose on the past, test once on the future;
  * **`perf`** — the one summary every study prints: annualised mean, volatility, Sharpe, max drawdown, hit rate;
  * **`newey_west_t`** — a t-statistic whose standard error survives the autocorrelation of hourly carry P&L;
  * **`block_bootstrap`** — a confidence interval for any statistic of a serially correlated series;
  * **`bh`** — Benjamini–Hochberg: which of many variants survive a false-discovery rate;
  * **`deflated_sharpe`** — the probability that the best of N tried variants has a true Sharpe above zero, given N;
  * **`choose_then_test`** — the protocol in one call: pick the best variant on the first part of time, report how it
    did on the rest, and where it ranked there.

Conventions. A return series is per period, as a fraction of the capital the strategy needs (a carry that earns 2bp
of notional in an hour on 1x margin is 0.0002). `periods_per_year` converts: 8760 for hourly, 365 for daily (crypto
trades every day), 252 for exchange days. Drawdown is measured on the additive cumulative sum, which is what a
constant-notional strategy experiences. Nothing here is random unless a seed is passed, and the default seed is fixed,
so a study re-run prints the same interval.

    import backtest as B
    B.perf(hourly_returns, 8760)
    B.choose_then_test({'thr=50%': r50, 'thr=100%': r100}, frac=0.5, periods_per_year=8760)
"""
import math
import random
import statistics

EULER_GAMMA = 0.5772156649015329
_N = statistics.NormalDist()


def _clean(x):
    return [float(v) for v in x if v is not None and not (isinstance(v, float) and math.isnan(v))]


def max_drawdown(returns):
    """Largest peak-to-trough fall of the additive cumulative sum, as a positive number (0 if it never falls)."""
    peak = cum = 0.0
    worst = 0.0
    for r in returns:
        cum += r
        peak = max(peak, cum)
        worst = max(worst, peak - cum)
    return worst


def moments(x):
    """Sample skewness and raw (not excess) kurtosis; a normal series gives about (0, 3)."""
    n = len(x)
    if n < 3:
        return 0.0, 3.0
    m = sum(x) / n
    m2 = sum((v - m) ** 2 for v in x) / n
    if m2 <= 0:
        return 0.0, 3.0
    m3 = sum((v - m) ** 3 for v in x) / n
    m4 = sum((v - m) ** 4 for v in x) / n
    return m3 / m2 ** 1.5, m4 / m2 ** 2


def perf(returns, periods_per_year):
    """The summary every study prints. Sharpe is the annualised mean over the annualised standard deviation, with no
    risk-free rate subtracted (strategies here are compared with an explicit benchmark row instead)."""
    x = _clean(returns)
    n = len(x)
    if n == 0:
        return {'n': 0}
    mean = sum(x) / n
    sd = statistics.pstdev(x) if n > 1 else 0.0
    skew, kurt = moments(x)
    nonzero = [v for v in x if v != 0]
    return {
        'n': n,
        'total': sum(x),
        'mean': mean,
        'ann_return': mean * periods_per_year,
        'ann_vol': sd * math.sqrt(periods_per_year),
        'sharpe': (mean / sd * math.sqrt(periods_per_year)) if sd > 0 else None,
        'max_drawdown': max_drawdown(x),
        'hit_rate': (sum(1 for v in nonzero if v > 0) / len(nonzero)) if nonzero else None,
        'active_share': len(nonzero) / n,
        'worst': min(x),
        'best': max(x),
        'skew': skew,
        'kurtosis': kurt,
    }


def newey_west_t(returns, lags=None):
    """t-statistic of the mean with a Bartlett-kernel HAC standard error, and its two-sided normal p-value.

    Hourly carry P&L is strongly autocorrelated (the same rate pays for hours on end), so the naive standard error is
    too small by a factor that can exceed five, and every carry looks significant. Default lags follow the usual
    floor(4 (n/100)^(2/9)) rule; pass more for slower-decaying series.
    """
    x = _clean(returns)
    n = len(x)
    if n < 3:
        return None, None
    if lags is None:
        lags = int(math.floor(4 * (n / 100.0) ** (2.0 / 9.0)))
    lags = max(0, min(lags, n - 1))
    m = sum(x) / n
    d = [v - m for v in x]
    s = sum(v * v for v in d) / n
    for k in range(1, lags + 1):
        g = sum(d[i] * d[i - k] for i in range(k, n)) / n
        s += 2.0 * (1.0 - k / (lags + 1.0)) * g
    if s <= 0:
        return None, None
    t = m / math.sqrt(s / n)
    return t, 2.0 * (1.0 - _N.cdf(abs(t)))


def block_bootstrap(returns, stat=None, block=None, n=2000, seed=7, ci=0.95):
    """Circular block bootstrap of `stat` (default: the mean). Returns {'point','lo','hi','p_le_0'}.

    Blocks keep the serial dependence that an i.i.d. resample would destroy. Default block length is n^(1/3), at least
    one. `p_le_0` is the share of resampled statistics at or below zero: a one-sided bootstrap p-value for "the
    statistic is positive".
    """
    x = _clean(returns)
    N = len(x)
    if N == 0:
        return {'point': None, 'lo': None, 'hi': None, 'p_le_0': None}
    stat = stat or (lambda v: sum(v) / len(v))
    block = block or max(1, int(round(N ** (1.0 / 3.0))))
    rng = random.Random(seed)
    k = int(math.ceil(N / block))
    vals = []
    for _ in range(n):
        s = []
        for _ in range(k):
            i = rng.randrange(N)
            s.extend(x[(i + j) % N] for j in range(block))
        vals.append(stat(s[:N]))
    vals.sort()
    a = (1.0 - ci) / 2.0
    lo = vals[int(math.floor(a * (n - 1)))]
    hi = vals[int(math.ceil((1.0 - a) * (n - 1)))]
    return {'point': stat(x), 'lo': lo, 'hi': hi, 'p_le_0': sum(1 for v in vals if v <= 0) / n}


def bh(pvalues, q=0.10):
    """Benjamini–Hochberg. Returns (reject flags, adjusted p-values) in the input order; None p-values never reject."""
    idx = [i for i, p in enumerate(pvalues) if p is not None]
    m = len(idx)
    rej = [False] * len(pvalues)
    adj = [None] * len(pvalues)
    if m == 0:
        return rej, adj
    order = sorted(idx, key=lambda i: pvalues[i])
    running = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        running = min(running, pvalues[i] * m / rank)
        adj[i] = running
    for i in idx:
        rej[i] = adj[i] <= q
    return rej, adj


def expected_max_sharpe(n_trials, sr_std):
    """Expected maximum of `n_trials` independent Sharpe estimates whose true value is zero and spread is `sr_std`
    (Bailey & López de Prado's false-strategy theorem)."""
    if n_trials <= 1:
        return 0.0
    a = _N.inv_cdf(1.0 - 1.0 / n_trials)
    b = _N.inv_cdf(1.0 - 1.0 / (n_trials * math.e))
    return sr_std * ((1.0 - EULER_GAMMA) * a + EULER_GAMMA * b)


def deflated_sharpe(returns, n_trials, sr_std=None):
    """Probability that the true per-period Sharpe of `returns` exceeds the best Sharpe you would expect from
    `n_trials` worthless variants. `sr_std` is the spread of Sharpe estimates across the variants tried; without it
    the estimator's own null spread 1/sqrt(T-1) is used, which is optimistic when the variants were correlated.

    Reading: above 0.95 the selection survives the number of things tried; near 0.5 it is what trying N things buys.
    """
    x = _clean(returns)
    T = len(x)
    if T < 3:
        return None
    sd = statistics.pstdev(x)
    if sd <= 0:
        return None
    sr = (sum(x) / T) / sd
    skew, kurt = moments(x)
    sr0 = expected_max_sharpe(n_trials, sr_std if sr_std is not None else 1.0 / math.sqrt(T - 1))
    denom = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if denom <= 0:
        return None
    return _N.cdf((sr - sr0) * math.sqrt(T - 1) / math.sqrt(denom))


def cutoff_index(n, frac=0.5):
    """Index that splits n periods into a choose part [0, i) and a test part [i, n)."""
    return max(1, min(n - 1, int(round(n * frac))))


def walk_forward(n, train, test, step=None):
    """Yield (train_range, test_range) index ranges rolling forward through n periods; nothing in a test range is
    ever in its own train range."""
    step = step or test
    s = 0
    while s + train + test <= n:
        yield range(s, s + train), range(s + train, s + train + test)
        s += step


def choose_then_test(variants, frac=0.5, periods_per_year=8760, key='sharpe'):
    """Pick the variant with the best in-sample `key` on the first `frac` of time, then report it on the rest.

    `variants` maps a name to a return series; all series must share one time axis. Returns the chosen name, its
    in-sample and out-of-sample `perf`, its out-of-sample rank among all variants, the HAC t-stat out of sample, the
    deflated Sharpe of the in-sample choice given how many were tried, and the BH survivors on the full sample.
    """
    names = list(variants)
    if not names:
        return None
    n = min(len(variants[k]) for k in names)
    c = cutoff_index(n, frac)
    ins = {k: perf(variants[k][:c], periods_per_year) for k in names}
    outs = {k: perf(variants[k][c:n], periods_per_year) for k in names}

    def score(p):
        v = p.get(key)
        return -1e18 if v is None else v

    chosen = max(names, key=lambda k: score(ins[k]))
    ranked = sorted(names, key=lambda k: -score(outs[k]))
    in_srs = [ins[k].get('sharpe') for k in names if ins[k].get('sharpe') is not None]
    sr_std = (statistics.pstdev(in_srs) / math.sqrt(periods_per_year)) if len(in_srs) > 1 else None
    pv = [newey_west_t(variants[k][:n])[1] for k in names]
    rej, adj = bh(pv)
    t_oos, p_oos = newey_west_t(variants[chosen][c:n])
    return {
        'chosen': chosen,
        'n_variants': len(names),
        'cutoff_index': c,
        'in_sample': ins[chosen],
        'out_of_sample': outs[chosen],
        'oos_rank': ranked.index(chosen) + 1,
        'oos_t': t_oos,
        'oos_p': p_oos,
        'deflated_sharpe_in_sample': deflated_sharpe(variants[chosen][:c], len(names), sr_std),
        'bh_survivors_full_sample': [k for k, r in zip(names, rej) if r],
        'bh_adjusted_p': dict(zip(names, adj)),
    }
