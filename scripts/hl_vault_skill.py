#!/usr/bin/env python3
"""Hyperliquid vaults as a survivorship-free database of fund managers: is there manager skill a depositor can rent?

Why. Hyperliquid lists every vault ever opened, closed ones included (`stats-data.hyperliquid.xyz/Mainnet/vaults`,
~9.5k vaults), and serves each vault's whole equity and P&L history (`info` `vaultDetails`). A depositor can join any
open user vault for a 10% profit share to the leader, a one-day lockup, and the rule that the leader keeps >= 5% of the
vault (which caps follower money). If past winners keep winning, "deposit in last quarter's best vaults" earns more
than the savings rate; if not, the most popular retail use of the vault page (copy the leaderboard) is dead. Unlike fund
databases, nothing here drops out when it closes, so the survivorship bias can be measured instead of assumed.

What this measures (`analyze`; every number lands in `analysis.json`, `render` prints `tables.md`):

  * **Returns net of flows.** Each vault's allTime history is a regular grid (24 h, 168 h or 336 h apart, by the vault's
    age today) of account value AV and cumulative P&L. A step's return is Modified Dietz,
    r = dP / (AV_prev + 0.5 F), F = dAV - dP (deposits less withdrawals); a closing step (AV -> 0) uses AV_prev.
    Returns chain into a time-weighted index per vault; closures and wipe-outs stay in (the last step carries the loss).
  * **No look-ahead on a mixed grid.** Decisions are taken at month starts (00:00 UTC on the 1st). A signal at t uses
    only grid points <= t. The holding return runs from the vault's first grid point >= t to its first point >= t+1,
    so consecutive holding windows chain without gaps and never touch the signal's data; the measured window starts up
    to one grid step (<= 14 days) after the decision, which is itself a late-entry test.
  * **Signals** (pre-committed in VARIANTS, hashed into analysis.json before any forward return is computed): trailing
    3- and 6-month return, 6-month Sharpe of grid-step returns, 6-month max drawdown, 3-month net flows over equity,
    3-month TVL growth, and size. leaderFraction and follower counts exist only as of today (API gap), so they cannot be
    signals.
  * **Portfolios.** Top quintile / decile of eligible vaults (age >= 6 months, equity >= $10k or >= $100k, open,
    relationship normal: HLP and its child vaults are tagged and excluded), equal- or equity-weighted, rebalanced
    monthly through a follower-account simulator that charges the leader's profit share exactly as Hyperliquid does
    (commission on equity above the follower's cost basis, crystallised pro rata on withdrawal). Compared with the
    savings rate actually paid (by year) and with SSR 3.80% today; regressed on BTC and HYPE over the same windows
    (beta, and |BTC| for a short-volatility signature).
  * **Protocol.** Choose the variant on decisions in the first half of the calendar, test once on the second
    (`backtest.choose_then_test`), Benjamini-Hochberg across variants, deflated Sharpe for the winner. Rank ICs per
    month for persistence. The survivorship check reruns everything on vaults that are open today.

    python3 scripts/hl_vault_skill.py collect --out research/2026-10-10/hl_vault_skill      # paced, ~1.25 s a call
    python3 scripts/hl_vault_skill.py analyze --out research/2026-10-10/hl_vault_skill
    python3 scripts/hl_vault_skill.py render  --out research/2026-10-10/hl_vault_skill

Network etiquette: the info API is weight-limited per IP (vaultDetails weighs 20 of 1200 a minute) and other workers
share the IP, so calls are spaced >= 1.25 s, a 429 pauses the host for a minute, and every response is cached gzipped
under raw/ (the collector resumes from the cache). Standard library only.
"""
import argparse
import bisect
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import backtest as B  # noqa: E402

STATS_URL = 'https://stats-data.hyperliquid.xyz/Mainnet/vaults'
INFO_URL = 'https://api.hyperliquid.xyz/info'
BINANCE_KLINES = 'https://api.binance.com/api/v3/klines'
UA = 'llm-quant-research/1.0'
DAY_MS = 86400000
SEED = 20261010

# Savings rate actually paid, by calendar year (Maker DSR, then Sky SSR), and SSR today.
SAVINGS_BY_YEAR = {2021: 0.0, 2022: 0.001, 2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}
SSR_NOW = 0.038

# Pre-filter for the full fetch: equity today >= $10k, or a coarse all-time P&L point >= $1k in absolute value
# (a vault that never moved $1k never held enough to matter). The rest are sampled at random to measure what the filter
# leaves out.
CORE_TVL = 10000.0
CORE_ABS_PNL = 1000.0
REST_SAMPLE_FRAC = 0.10

EPS_AV = 1.0                 # a vault with less than $1 of equity is empty (not yet funded, closed or wiped out)
MIN_AGE_MONTHS = 6           # eligibility: first funded grid point at least 6 calendar months before the decision
MIN_UNIVERSE_FOR_START = 10  # the calendar starts in the first month with >= 10 eligible vaults in the $100k universe
LAST_DECISION = '2026-09-01'
FRICTION_BP = 10.0           # sensitivity only: cost per unit of turnover (vault unwinds on withdrawal, gas-free)

# The pre-committed variant list. analyze() refuses to run if this changes after precommit.json was written.
SIGNALS = {
    'ret3': 'trailing 3-month time-weighted return (index at last point <= t over index at last point <= t-3m)',
    'ret6': 'trailing 6-month time-weighted return',
    'sharpe6': 'mean / sd of grid-step returns in (t-6m, t], annualised by the vault\'s step length (>= 4 steps)',
    'mdd6': 'minus the max drawdown of the return index over [t-6m, t] (shallower drawdown ranks higher)',
    'flow3': 'net deposits less withdrawals over (t-3m, t] over equity at t-3m',
    'tvlg3': 'equity at t over equity at t-3m, minus 1 (flows and P&L together)',
    'size': 'equity at t',
}
CUTS = {'q5': 0.20, 'q10': 0.10}
WEIGHTS = {'ew': 'equal weight', 'cw': 'weight proportional to equity at t (capacity-weighted)'}
UNIVERSES = {'u10k': 1e4, 'u100k': 1e5}
PRECOMMIT = {
    'study': 'hl_vault_skill',
    'decisions': 'month starts 00:00 UTC; first = first month with >= %d eligible vaults in u100k; last = %s'
                 % (MIN_UNIVERSE_FOR_START, LAST_DECISION),
    'holding': 'from the vault\'s first grid point >= t to its first grid point >= next month start',
    'eligibility': 'relationship normal (HLP parent/children and vaults led by the HLP leader excluded); first funded '
                   'point <= t - %d months; equity at the last point <= t >= the universe threshold' % MIN_AGE_MONTHS,
    'signals': SIGNALS, 'cuts': CUTS, 'weights': WEIGHTS, 'universes': UNIVERSES,
    'n_variants': len(SIGNALS) * len(CUTS) * len(WEIGHTS) * len(UNIVERSES),
    'fee': 'leaderCommission on follower equity above cost basis, crystallised pro rata on withdrawal (simulated '
           'follower account); deposits and withdrawals free; friction %.0fbp of turnover as a sensitivity' % FRICTION_BP,
    'benchmark': 'savings rate paid by year %s; SSR now %.2f%%' % (json.dumps(SAVINGS_BY_YEAR), 100 * SSR_NOW),
    'choice': 'backtest.choose_then_test on monthly net excess over the savings rate paid, frac 0.5, key sharpe',
    'go_rule': 'go only if the chosen variant earns > +2%/yr net over the savings rate paid out of sample with '
               'Newey-West t > 2, BH-adjusted out-of-sample p < 0.10 across all variants, and capacity >= $1M today',
    'kill_if_go': 'trailing 6-month net excess < 0, or selected vaults\' follower room < $1M, or a selected vault '
                  'closes after a > 20% loss inside a month',
}


# ---------------------------------------------------------------------------------------------- small helpers

def utc(ms=None):
    ms = time.time() * 1000 if ms is None else ms
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def day(ms):
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime('%Y-%m-%d')


def fnum(x, default=None):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def write_gz(path, obj):
    tmp = path + '.tmp'
    with gzip.open(tmp, 'wt') as f:
        json.dump(obj, f, separators=(',', ':'))
    os.replace(tmp, path)


def write_json(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=False, default=str)
    os.replace(tmp, path)


class Paced:
    """One request at a time, at least `interval` seconds apart; 429 pauses for `pause_429` seconds and retries."""

    def __init__(self, interval=1.25, timeout=60, retries=8, pause_429=60.0):
        self.interval, self.timeout, self.retries, self.pause_429 = interval, timeout, retries, pause_429
        self.next_at = 0.0
        self.n = self.errors = self.throttled = 0

    def call(self, url, body=None):
        last = None
        for attempt in range(self.retries):
            now = time.monotonic()
            if self.next_at > now:
                time.sleep(self.next_at - now)
            self.next_at = time.monotonic() + self.interval
            self.n += 1
            try:
                data = json.dumps(body).encode() if body is not None else None
                req = urllib.request.Request(url, data=data, headers={'User-Agent': UA,
                                                                      'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                last = 'HTTP %s' % e.code
                if e.code == 429:
                    self.throttled += 1
                    self.next_at = time.monotonic() + self.pause_429
                    continue
                self.errors += 1
                if e.code >= 500:
                    time.sleep(min(30.0, 2.0 * 2 ** attempt))
                    continue
                return {'_http_error': e.code}
            except Exception as e:  # noqa: BLE001 - network errors are retried
                last = repr(e)[:160]
                self.errors += 1
                time.sleep(min(30.0, 2.0 * 2 ** attempt))
        raise RuntimeError('retry limit: %s' % last)

    def stats(self):
        return {'requests': self.n, 'errors': self.errors, 'throttled': self.throttled}


# ---------------------------------------------------------------------------------------------- collection

def coarse_max_abs_pnl(v):
    pn = dict(v.get('pnls') or [])
    pts = [fnum(x, 0.0) for x in pn.get('allTime') or []]
    return max((abs(x) for x in pts), default=0.0)


def fetch_plan(stats):
    """Deterministic fetch list: the core (pre-filter) by importance, then a seeded random sample of the rest."""
    core, rest = [], []
    for v in stats:
        s = v['summary']
        tvl = fnum(s.get('tvl'), 0.0)
        m = coarse_max_abs_pnl(v)
        rel = (s.get('relationship') or {}).get('type')
        if tvl >= CORE_TVL or m >= CORE_ABS_PNL or rel in ('parent', 'child'):
            core.append((max(tvl, m), s['vaultAddress']))
        else:
            rest.append(s['vaultAddress'])
    core.sort(key=lambda x: -x[0])
    rng = random.Random(SEED)
    rest_sorted = sorted(rest)
    sample = sorted(rng.sample(rest_sorted, int(round(len(rest_sorted) * REST_SAMPLE_FRAC))))
    return [a for _, a in core], sample, len(rest_sorted)


def collect(out, parts, max_vaults=None):
    raw = os.path.join(out, 'raw')
    det = os.path.join(raw, 'details')
    os.makedirs(det, exist_ok=True)
    t0 = time.time()
    man_path = os.path.join(raw, 'collect_manifest.json')
    man = json.load(open(man_path)) if os.path.exists(man_path) else {}
    http = Paced()
    if 'stats' in parts:
        p = os.path.join(raw, 'vaults_stats.json.gz')
        if not os.path.exists(p):
            req = urllib.request.Request(STATS_URL, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=180) as r:
                stats = json.loads(r.read().decode())
            write_gz(p, {'fetched_at_ms': int(time.time() * 1000), 'url': STATS_URL, 'data': stats})
        man['stats'] = {'file': 'raw/vaults_stats.json.gz', 'fetched_at': utc(read_gz(p)['fetched_at_ms'])}
    if 'prices' in parts:
        pdir = os.path.join(raw, 'prices')
        os.makedirs(pdir, exist_ok=True)
        bn = Paced(interval=0.5)
        for sym in ('BTCUSDT', 'ETHUSDT'):
            rows, start = [], int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
            while True:
                q = '%s?symbol=%s&interval=1d&startTime=%d&limit=1000' % (BINANCE_KLINES, sym, start)
                got = bn.call(q)
                if not isinstance(got, list) or not got:
                    break
                rows.extend(got)
                start = got[-1][0] + DAY_MS
                if len(got) < 1000:
                    break
            write_gz(os.path.join(pdir, 'binance_%s_1d.json.gz' % sym),
                     {'fetched_at_ms': int(time.time() * 1000), 'source': BINANCE_KLINES, 'rows': rows})
        start = int(dt.datetime(2024, 11, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        body = {'type': 'candleSnapshot', 'req': {'coin': 'HYPE', 'interval': '1d', 'startTime': start,
                                                  'endTime': int(time.time() * 1000)}}
        got = http.call(INFO_URL, body)
        write_gz(os.path.join(pdir, 'hl_HYPE_1d.json.gz'),
                 {'fetched_at_ms': int(time.time() * 1000), 'request': body, 'rows': got})
        man['prices'] = {'files': sorted(os.listdir(pdir)), 'fetched_at': utc()}
    if 'details' in parts:
        stats = read_gz(os.path.join(raw, 'vaults_stats.json.gz'))['data']
        core, sample, n_rest = fetch_plan(stats)
        plan = [(a, 'core') for a in core] + [(a, 'sample') for a in sample]
        write_json(os.path.join(raw, 'fetch_plan.json'), {
            'rule': 'core: tvl >= %.0f or max |coarse allTime pnl| >= %.0f or HLP family; sample: %.0f%% of the rest, '
                    'seed %d' % (CORE_TVL, CORE_ABS_PNL, 100 * REST_SAMPLE_FRAC, SEED),
            'n_stats': len(stats), 'n_core': len(core), 'n_rest': n_rest, 'n_sample': len(sample),
            'core': core, 'sample': sample})
        if max_vaults:
            plan = plan[:max_vaults]
        done = fails = 0
        for i, (addr, tier) in enumerate(plan):
            p = os.path.join(det, '%s.json.gz' % addr)
            if os.path.exists(p):
                continue
            body = {'type': 'vaultDetails', 'vaultAddress': addr}
            try:
                got = http.call(INFO_URL, body)
            except RuntimeError as e:
                fails += 1
                print('fail', addr, e, flush=True)
                continue
            if not isinstance(got, dict) or '_http_error' in got:
                fails += 1
                print('bad', addr, str(got)[:120], flush=True)
                continue
            write_gz(p, {'fetched_at_ms': int(time.time() * 1000), 'tier': tier, 'request': body, 'response': got})
            done += 1
            if done % 100 == 0:
                print('%s fetched %d (%d/%d in plan) %s' % (utc(), done, i + 1, len(plan), http.stats()), flush=True)
        man['details'] = {'planned': len(plan), 'fetched_this_run': done, 'failures_this_run': fails,
                          'on_disk': len([f for f in os.listdir(det) if f.endswith('.json.gz')]),
                          'finished_at': utc(), 'http': http.stats()}
    man['seconds_last_run'] = round(time.time() - t0, 1)
    write_json(man_path, man)
    print(json.dumps(man, indent=1))
    return 0


# ---------------------------------------------------------------------------------------------- pre-commit

def precommit_hash(obj=None):
    return hashlib.sha256(json.dumps(obj or PRECOMMIT, sort_keys=True).encode()).hexdigest()


def precommit(out):
    p = os.path.join(out, 'precommit.json')
    if os.path.exists(p):
        old = json.load(open(p))
        print('precommit exists (%s), hash %s, matches current: %s' % (old['written_at'], old['sha256'],
                                                                        old['sha256'] == precommit_hash()))
        return 0
    write_json(p, {'written_at': utc(), 'sha256': precommit_hash(), 'precommit': PRECOMMIT,
                   'note': 'written before any forward return was computed; analyze() checks this hash'})
    print('wrote', p, precommit_hash())
    return 0


# ---------------------------------------------------------------------------------------------- core math

def month_start(ms):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc)
    return int(dt.datetime(d.year, d.month, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def add_months(ms, k):
    d = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc)
    m = d.month - 1 + k
    y, m = d.year + m // 12, m % 12 + 1
    last = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30,
            31][m - 1]
    return int(d.replace(year=y, month=m, day=min(d.day, last)).timestamp() * 1000)


def last_le(ts, t):
    """Index of the last grid point at or before t, or None."""
    i = bisect.bisect_right(ts, t) - 1
    return i if i >= 0 else None


def first_ge(ts, t):
    """Index of the first grid point at or after t, or None."""
    i = bisect.bisect_left(ts, t)
    return i if i < len(ts) else None


RET_FLOOR = -0.9999   # a wipe-out; the index stays positive so a vault refunded afterwards keeps a usable index
FLOW_TOL = 0.10       # net flows within 10% of starting equity: Dietz is essentially exact
DIETZ_LO, DIETZ_HI = -0.9, 1.0


def step_returns(av, pnl, eps=EPS_AV, timing='mid'):
    """Flow-adjusted return of each grid step (Modified Dietz, flows assumed mid-step).

    For step k (point k-1 -> k): dP = pnl[k] - pnl[k-1]; F = (av[k] - av[k-1]) - dP is the net deposit;
    r = dP / (av[k-1] + 0.5 F). Special cases:
      * av[k-1] empty: no capital was at risk at the start, so the step has no return (None); this includes the first
        funding step, whose deposit timing inside the step is unknown;
      * av[k] empty after a funded point: a closure or a wipe-out; all P&L of the step was earned before the money
        left, on the starting equity, so r = dP / av[k-1];
      * large net flows (|F| > 10% of starting equity) with a Dietz return outside [-90%, +100%], or a Dietz
        denominator below half the starting equity: the mid-step timing assumption is not credible (money arrived,
        traded and left inside one 1-2 week step), so the step uses the largest capital plausibly at risk,
        max(av[k-1] + max(F, 0), av[k]) — a conservative bound that shrinks |r| (flag 'dietz_fallback');
      * every return is floored at -99.99% (flag 'wipeout').
    A step with small flows is never altered, however extreme (a no-flow +1,400% week is a real return).
    timing='conservative' (a post-hoc sensitivity) puts deposits at the start of the step and withdrawals at its end,
    den = av[k-1] + max(F, 0): the largest denominator, so the smallest |r| for every step with net deposits.
    Returns (r, flow, flags), each a list aligned with the points (index 0 is None / 0 / None).
    """
    n = len(av)
    r, flow, flags = [None] * n, [0.0] * n, [None] * n
    for k in range(1, n):
        a0, a1 = av[k - 1], av[k]
        dp = pnl[k] - pnl[k - 1]
        f = (a1 - a0) - dp
        flow[k] = f
        if a0 <= eps:
            continue
        if a1 <= eps:
            x = dp / a0
            flags[k] = 'closing'
        else:
            den = a0 + 0.5 * f if timing == 'mid' else a0 + max(f, 0.0)
            if abs(f) <= FLOW_TOL * a0:
                x = dp / den
            else:
                x = dp / den if den >= 0.5 * a0 else None
                if x is None or not (DIETZ_LO <= x <= DIETZ_HI):
                    x = dp / max(a0 + max(f, 0.0), a1)
                    flags[k] = 'dietz_fallback'
            if x > DIETZ_HI and not flags[k]:
                flags[k] = 'gt100pct'
        if x < RET_FLOOR:
            x = RET_FLOOR
            flags[k] = 'wipeout'
        r[k] = x
    return r, flow, flags


def twr_index(r):
    """Chained index of step returns; a step without a return leaves the index flat."""
    idx = [1.0] * len(r)
    for k in range(1, len(r)):
        idx[k] = idx[k - 1] * (1.0 + r[k]) if r[k] is not None else idx[k - 1]
    return idx


def forward_return(v, t0, t1):
    """Holding return from the vault's first grid point >= t0 to its first point >= t1, or None when the grid does not
    reach t1. A vault that is empty at the entry point returns 0 (the money was never deposited: cash)."""
    ts = v['ts']
    b0, b1 = first_ge(ts, t0), first_ge(ts, t1)
    if b0 is None or b1 is None:
        return None
    if v['av'][b0] <= EPS_AV:
        return 0.0
    return v['idx'][b1] / v['idx'][b0] - 1.0


def forward_window(v, t0, t1):
    ts = v['ts']
    b0, b1 = first_ge(ts, t0), first_ge(ts, t1)
    if b0 is None or b1 is None:
        return None
    return ts[b0], ts[b1]


def max_drawdown_index(vals):
    peak, worst = None, 0.0
    for x in vals:
        if peak is None or x > peak:
            peak = x
        if peak and peak > 0:
            worst = max(worst, 1.0 - x / peak)
    return worst


def signals_at(v, t, months=None):
    """Every pre-committed signal for vault v at decision time t, from grid points <= t only."""
    ts, idx, av, r, flow = v['ts'], v['idx'], v['av'], v['r'], v['flow']
    a = last_le(ts, t)
    if a is None:
        return None
    t3, t6 = add_months(t, -3), add_months(t, -6)
    a3, a6 = last_le(ts, t3), last_le(ts, t6)
    out = {'size': av[a]}
    out['ret3'] = (idx[a] / idx[a3] - 1.0) if a3 is not None and idx[a3] > 0 else None
    out['ret6'] = (idx[a] / idx[a6] - 1.0) if a6 is not None and idx[a6] > 0 else None
    lo = (a6 + 1) if a6 is not None else 1
    steps = [r[k] for k in range(max(1, lo), a + 1) if r[k] is not None]
    sd = statistics.pstdev(steps) if len(steps) >= 4 else 0.0
    out['sharpe6'] = (statistics.mean(steps) / sd * math.sqrt(365.0 / v['step_days'])) if sd > 0 else None
    out['mdd6'] = -max_drawdown_index(idx[(a6 if a6 is not None else 0):a + 1]) if a6 is not None else None
    if a3 is not None and av[a3] > EPS_AV:
        out['flow3'] = sum(flow[k] for k in range(a3 + 1, a + 1)) / av[a3]
        out['tvlg3'] = av[a] / av[a3] - 1.0
    else:
        out['flow3'] = out['tvlg3'] = None
    return out


def eligible(v, t, min_equity):
    """Open, old enough, big enough at t, using points <= t only."""
    if v['excluded']:
        return False
    a = last_le(v['ts'], t)
    if a is None or v['born_ts'] is None:
        return False
    if v['born_ts'] > add_months(t, -MIN_AGE_MONTHS):
        return False
    return v['av'][a] >= min_equity


def select_top(cands, frac):
    """cands: list of (addr, signal, weight_base). Top `frac` by signal (ties by address), at least one."""
    c = [x for x in cands if x[1] is not None]
    if not c:
        return []
    c.sort(key=lambda x: (-x[1], x[0]))
    k = max(1, int(round(len(c) * frac)))
    return c[:k]


def savings_rate(ms):
    y = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).year
    return SAVINGS_BY_YEAR.get(y, SSR_NOW)


def savings_accrual(t0, t1, const=None):
    """Simple accrual of the savings rate over [t0, t1), split by calendar year."""
    total, t = 0.0, t0
    while t < t1:
        y = dt.datetime.fromtimestamp(t / 1000.0, dt.timezone.utc).year
        y_end = int(dt.datetime(y + 1, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
        seg = min(t1, y_end) - t
        rate = const if const is not None else SAVINGS_BY_YEAR.get(y, SSR_NOW)
        total += rate * seg / (365.0 * DAY_MS)
        t += seg
    return total


class FollowerAccount:
    """One depositor's positions in several vaults, with Hyperliquid's profit share.

    A position is (equity E, cost basis B). The leader is owed c * max(0, E - B); a withdrawal of a fraction f pays
    that share pro rata (E and B both scale by 1 - f), so the remaining position keeps its basis — the high-water mark is
    the depositor's own cost. A deposit adds to E and B alike. Net value = E - c * max(0, E - B)."""

    def __init__(self, cash=1.0):
        self.cash = cash
        self.pos = {}       # addr -> [E, B, commission]
        self.fees_paid = 0.0
        self.turnover = 0.0

    def net(self, addr):
        e, b, c = self.pos[addr]
        return e - c * max(0.0, e - b)

    def nav(self):
        return self.cash + sum(self.net(a) for a in self.pos)

    def withdraw_all(self, addr):
        e, b, c = self.pos.pop(addr)
        fee = c * max(0.0, e - b)
        self.fees_paid += fee
        self.cash += e - fee
        self.turnover += e - fee

    def rebalance(self, targets, commissions):
        """targets: addr -> weight of NAV (weights sum to <= 1; the rest stays in cash)."""
        nav = self.nav()
        for a in list(self.pos):
            if a not in targets:
                self.withdraw_all(a)
        for a, w in targets.items():
            want = w * nav
            if a in self.pos:
                cur = self.net(a)
                if want < cur and cur > 0:
                    f = 1.0 - want / cur
                    e, b, c = self.pos[a]
                    fee = f * c * max(0.0, e - b)
                    self.fees_paid += fee
                    self.cash += f * e - fee
                    self.turnover += f * e - fee
                    self.pos[a] = [e * (1 - f), b * (1 - f), c]
                elif want > cur:
                    d = want - cur
                    self.pos[a][0] += d
                    self.pos[a][1] += d
                    self.cash -= d
                    self.turnover += d
            else:
                self.pos[a] = [want, want, commissions.get(a, 0.1)]
                self.cash -= want
                self.turnover += want

    def grow(self, returns, cash_return=0.0):
        for a, x in returns.items():
            if a in self.pos:
                self.pos[a][0] *= (1.0 + x)
        self.cash *= (1.0 + cash_return)


def spearman(x, y):
    n = len(x)
    if n < 3:
        return None

    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        rk = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                rk[order[k]] = (i + j) / 2.0
            i = j + 1
        return rk

    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _inv(m):
    n = len(m)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        p = max(range(c, n), key=lambda i: abs(a[i][c]))
        if abs(a[p][c]) < 1e-15:
            return None
        a[c], a[p] = a[p], a[c]
        pv = a[c][c]
        a[c] = [v / pv for v in a[c]]
        for i in range(n):
            if i != c and a[i][c] != 0:
                f = a[i][c]
                a[i] = [vi - f * vc for vi, vc in zip(a[i], a[c])]
    return [row[n:] for row in a]


def ols_hac(y, X, lags=2):
    """OLS with Newey-West (Bartlett) standard errors. X rows include the constant. Returns coef, se, t, r2, n."""
    n, k = len(y), len(X[0]) if X else 0
    if n <= k + 1:
        return None
    xtx = [[sum(X[t][i] * X[t][j] for t in range(n)) for j in range(k)] for i in range(k)]
    inv = _inv(xtx)
    if inv is None:
        return None
    xty = [sum(X[t][i] * y[t] for t in range(n)) for i in range(k)]
    b = [sum(inv[i][j] * xty[j] for j in range(k)) for i in range(k)]
    e = [y[t] - sum(b[i] * X[t][i] for i in range(k)) for t in range(n)]
    s = [[0.0] * k for _ in range(k)]
    for t in range(n):
        for i in range(k):
            for j in range(k):
                s[i][j] += e[t] * e[t] * X[t][i] * X[t][j]
    for l in range(1, lags + 1):
        w = 1.0 - l / (lags + 1.0)
        for t in range(l, n):
            for i in range(k):
                for j in range(k):
                    s[i][j] += w * e[t] * e[t - l] * (X[t][i] * X[t - l][j] + X[t - l][i] * X[t][j])
    v = [[sum(inv[i][p] * s[p][q] * inv[q][j] for p in range(k) for q in range(k)) for j in range(k)]
         for i in range(k)]
    se = [math.sqrt(v[i][i]) if v[i][i] > 0 else None for i in range(k)]
    my = sum(y) / n
    sst = sum((v_ - my) ** 2 for v_ in y)
    r2 = 1.0 - sum(x * x for x in e) / sst if sst > 0 else None
    return {'coef': b, 'se': se, 't': [b[i] / se[i] if se[i] else None for i in range(k)], 'r2': r2, 'n': n}


# ---------------------------------------------------------------------------------------------- loading

def parse_vault(rec, hlp_leader=None):
    """A vault record from a cached vaultDetails response: the allTime grid, step returns, index and current state."""
    resp = rec['response']
    port = dict(resp.get('portfolio') or [])
    at = port.get('allTime') or {}
    pmap = {}
    for t, x in at.get('pnlHistory') or []:
        pmap[int(t)] = fnum(x, 0.0)
    pts = {}
    for t, x in at.get('accountValueHistory') or []:
        t = int(t)
        if t in pmap:
            pts[t] = (fnum(x, 0.0), pmap[t])
    ts = sorted(pts)
    av = [pts[t][0] for t in ts]
    pnl = [pts[t][1] for t in ts]
    r, flow, flags = step_returns(av, pnl)
    idx = twr_index(r)
    born = next((k for k, x in enumerate(av) if x > EPS_AV), None)
    gaps = [(ts[k + 1] - ts[k]) / DAY_MS for k in range(len(ts) - 1)]
    regular = sorted(gaps)[:-1] if len(gaps) > 1 else gaps     # the last point is "now", off the grid
    step_days = statistics.median(regular) if regular else 1.0
    rel = (resp.get('relationship') or {}).get('type') or 'normal'
    leader = (resp.get('leader') or '').lower()
    return {
        'addr': resp.get('vaultAddress', '').lower(), 'name': resp.get('name') or '', 'leader': leader,
        'closed': bool(resp.get('isClosed')), 'rel': rel, 'allow': resp.get('allowDeposits'),
        'lf': fnum(resp.get('leaderFraction')), 'lc': fnum(resp.get('leaderCommission'), 0.1),
        'n_followers_listed': len(resp.get('followers') or []), 'followers': resp.get('followers') or [],
        'max_withdrawable': fnum(resp.get('maxWithdrawable')), 'max_distributable': fnum(resp.get('maxDistributable')),
        'always_close': resp.get('alwaysCloseOnWithdraw'),
        'ts': ts, 'av': av, 'pnl': pnl, 'r': r, 'flow': flow, 'flags': flags, 'idx': idx,
        'born_ts': ts[born] if born is not None else None, 'step_days': step_days,
        'tier': rec.get('tier'), 'fetched_at_ms': rec.get('fetched_at_ms'),
        'excluded': rel in ('parent', 'child') or (hlp_leader is not None and leader == hlp_leader),
        'all_time_pnl_api': pnl[-1] if pnl else None,
    }


def load(out):
    raw = os.path.join(out, 'raw')
    stats = read_gz(os.path.join(raw, 'vaults_stats.json.gz'))
    sdata = stats['data']
    hlp_leader = None
    for v in sdata:
        if (v['summary'].get('relationship') or {}).get('type') == 'parent':
            hlp_leader = v['summary']['leader'].lower()
    det = os.path.join(raw, 'details')
    vaults = {}
    for f in sorted(os.listdir(det)):
        if not f.endswith('.json.gz'):
            continue
        v = parse_vault(read_gz(os.path.join(det, f)), hlp_leader)
        if v['ts']:
            vaults[v['addr']] = v
    return stats, sdata, hlp_leader, vaults


def load_prices(out):
    pdir = os.path.join(out, 'raw', 'prices')
    series = {}
    for sym in ('BTCUSDT', 'ETHUSDT'):
        rows = read_gz(os.path.join(pdir, 'binance_%s_1d.json.gz' % sym))['rows']
        series[sym[:3]] = sorted((int(x[6]) + 1, float(x[4])) for x in rows)
    rows = read_gz(os.path.join(pdir, 'hl_HYPE_1d.json.gz'))['rows']
    series['HYPE'] = sorted((int(x['T']) + 1, float(x['c'])) for x in rows)
    return series


def price_at(series, ms):
    """Linear interpolation between daily closes (benchmark returns only; never used for a decision)."""
    xs = [t for t, _ in series]
    i = bisect.bisect_right(xs, ms) - 1
    if i < 0 or i + 1 >= len(series):
        return None if i < 0 or ms > xs[-1] + DAY_MS else series[-1][1]
    (t0, p0), (t1, p1) = series[i], series[i + 1]
    return p0 + (p1 - p0) * (ms - t0) / (t1 - t0)


def window_return(series, w):
    if w is None:
        return None
    a, b = price_at(series, w[0]), price_at(series, w[1])
    return (b / a - 1.0) if a and b else None


# ---------------------------------------------------------------------------------------------- panel

def forward_return_late(v, t0, t1, shift=1):
    """Holding return entering `shift` grid points after the first point >= t0 (late-entry check)."""
    ts = v['ts']
    b0, b1 = first_ge(ts, t0), first_ge(ts, t1)
    if b0 is None or b1 is None:
        return None
    b0 = min(b0 + shift, len(ts) - 1)
    b1 = min(b1 + shift, len(ts) - 1)
    if v['av'][b0] <= EPS_AV:
        return 0.0
    return v['idx'][b1] / v['idx'][b0] - 1.0


def build_panel(vaults, months, prices, min_equity=min(UNIVERSES.values())):
    """panel[t][addr] for every vault eligible in the broadest universe at t: signals (points <= t), the holding
    return and its window (points >= t), matched BTC/HYPE returns over the same window, and state flags."""
    panel = {}
    for t in months:
        t1 = add_months(t, 1)
        rows = {}
        for a, v in vaults.items():
            if not eligible(v, t, min_equity):
                continue
            sig = signals_at(v, t)
            if sig is None:
                continue
            w = forward_window(v, t, t1)
            fwd = forward_return(v, t, t1)
            closed_in = False
            if w is not None:
                b0, b1 = first_ge(v['ts'], t), first_ge(v['ts'], t1)
                closed_in = v['av'][b0] > EPS_AV and v['av'][b1] <= EPS_AV
                flagged = [v['flags'][k] for k in range(b0 + 1, b1 + 1)
                           if v['flags'][k] in ('wipeout', 'gt100pct', 'dietz_fallback')]
            else:
                flagged = []
            rows[a] = {
                'addr': a, 'sig': sig, 'size': sig['size'], 'fwd': fwd, 'fwd_late': forward_return_late(v, t, t1),
                'win': w, 'btc': window_return(prices['BTC'], w), 'hype': window_return(prices['HYPE'], w),
                'elig': {u: sig['size'] >= x for u, x in UNIVERSES.items()},
                'closed_now': v['closed'], 'closed_in': closed_in, 'lc': v['lc'] if v['lc'] is not None else 0.1,
                'flagged': flagged, 'tier': v['tier'], 'allow_now': v['allow'],
                'delay_days': ((w[0] - t) / DAY_MS) if w else None,
            }
        panel[t] = rows
    return panel


def decision_months(vaults):
    first = min(v['born_ts'] for v in vaults.values() if v['born_ts'] is not None)
    t = add_months(month_start(first), MIN_AGE_MONTHS)
    last = int(dt.datetime.strptime(LAST_DECISION, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    out = []
    while t <= last:
        out.append(t)
        t = add_months(t, 1)
    return out


# ---------------------------------------------------------------------------------------------- strategies

def run_strategy(panel, months, universe, signal=None, frac=None, weight='ew', keep=None, late=False,
                 friction_bp=0.0, detail=False):
    """Monthly follower-account simulation. signal None = every eligible vault (the vault market).
    keep(row) filters candidate rows (survivorship and deposit-gate checks). Returns per-month records."""
    acct = FollowerAccount(1.0)
    recs = []
    for t in months:
        t1 = add_months(t, 1)
        rows = panel[t]
        cands = []
        for a, row in rows.items():
            if not row['elig'][universe] or (keep and not keep(row)):
                continue
            s = row['sig'][signal] if signal else 0.0
            cands.append((a, s, row['size']))
        sel = select_top(cands, frac) if signal else [c for c in cands]
        if weight == 'ew':
            w = {a: 1.0 / len(sel) for a, _, _ in sel} if sel else {}
        else:
            tot = sum(s for _, _, s in sel)
            w = {a: s / tot for a, _, s in sel} if tot > 0 else {}
        nav0 = acct.nav()
        fees0, turn0 = acct.fees_paid, acct.turnover
        acct.rebalance(w, {a: rows[a]['lc'] for a in w})
        traded = acct.turnover - turn0
        key = 'fwd_late' if late else 'fwd'
        rets = {a: (rows[a][key] if rows[a][key] is not None else 0.0) for a in w}
        acct.grow(rets, cash_return=savings_accrual(t, t1))
        nav1 = acct.nav()
        net = nav1 / nav0 - 1.0 - friction_bp / 1e4 * traded / nav0
        gross = sum(w[a] * rets[a] for a in w) if w else savings_accrual(t, t1)
        simple = sum(w[a] * (rets[a] - rows[a]['lc'] * max(0.0, rets[a])) for a in w) if w else gross

        def wavg(k):
            vals = [(w[a], rows[a][k]) for a in w if rows[a][k] is not None]
            tw = sum(x for x, _ in vals)
            return sum(x * y for x, y in vals) / tw if tw > 0 and tw >= 0.8 * sum(w.values()) else None

        recs.append({
            't': day(t), 'n_eligible': len(cands), 'n_selected': len(w), 'gross': gross, 'net': net,
            'net_simple_fee': simple, 'sav': savings_accrual(t, t1), 'ssr_now': savings_accrual(t, t1, SSR_NOW),
            'btc': wavg('btc'), 'hype': wavg('hype'), 'traded_frac': traded / nav0 if nav0 > 0 else None,
            'fees_frac': (acct.fees_paid - fees0) / nav0 if nav0 > 0 else None,
            'sel_tvl': sum(rows[a]['size'] for a in w), 'closed_in': sum(1 for a in w if rows[a]['closed_in']),
            'closed_now': sum(1 for a in w if rows[a]['closed_now']),
            'top': sorted(w, key=lambda a: -w[a])[:3],
        })
        if detail:
            recs[-1]['w'] = dict(w)
            recs[-1]['rets'] = dict(rets)
    return recs


def series(recs, kind='net', bench='sav'):
    return [r[kind] - r[bench] for r in recs]


def split_perf(x, c, ppy=12):
    tin, pin = B.newey_west_t(x[:c], lags=2)
    tout, pout = B.newey_west_t(x[c:], lags=2)
    return {'in': B.perf(x[:c], ppy), 'in_t': tin, 'in_p': pin, 'out': B.perf(x[c:], ppy), 'out_t': tout,
            'out_p': pout, 'full': B.perf(x, ppy)}


def variant_names():
    for s in SIGNALS:
        for c in CUTS:
            for w in WEIGHTS:
                for u in UNIVERSES:
                    yield '%s|%s|%s|%s' % (s, c, w, u), s, c, w, u


# ---------------------------------------------------------------------------------------------- diagnostics

def ic_table(panel, months, c, keep=None):
    out = {}
    for u in UNIVERSES:
        for s in SIGNALS:
            ics = []
            for t in months:
                xs, ys = [], []
                for row in panel[t].values():
                    if not row['elig'][u] or (keep and not keep(row)):
                        continue
                    if row['sig'][s] is None or row['fwd'] is None:
                        continue
                    xs.append(row['sig'][s])
                    ys.append(row['fwd'])
                ics.append(spearman(xs, ys) if len(xs) >= 8 else None)
            vin = [x for x in ics[:c] if x is not None]
            vout = [x for x in ics[c:] if x is not None]
            tin = B.newey_west_t(vin, lags=2)[0] if len(vin) > 3 else None
            tout, pout = B.newey_west_t(vout, lags=2) if len(vout) > 3 else (None, None)
            out['%s|%s' % (s, u)] = {
                'ic_in': statistics.mean(vin) if vin else None, 't_in': tin, 'months_in': len(vin),
                'ic_out': statistics.mean(vout) if vout else None, 't_out': tout, 'p_out': pout,
                'months_out': len(vout), 'share_pos_out': (sum(1 for x in vout if x > 0) / len(vout)) if vout else None}
    return out


def quintile_table(panel, months, c, keep=None, signals=('ret3', 'ret6', 'sharpe6', 'mdd6', 'flow3', 'size')):
    out = {}
    for u in UNIVERSES:
        for s in signals:
            per = []   # per month list of 5 means
            for t in months:
                rows = [r for r in panel[t].values() if r['elig'][u] and (not keep or keep(r))
                        and r['sig'][s] is not None and r['fwd'] is not None]
                if len(rows) < 10:
                    per.append(None)
                    continue
                rows.sort(key=lambda r: r['sig'][s])
                n = len(rows)
                qs = []
                for q in range(5):
                    grp = rows[q * n // 5:(q + 1) * n // 5]
                    qs.append(statistics.mean(r['fwd'] for r in grp))
                per.append(qs)

            def avg(part):
                p = [x for x in part if x is not None]
                if not p:
                    return None
                return {'q%d' % (q + 1): statistics.mean(x[q] for x in p) for q in range(5)} | {
                    'q5_minus_q1': statistics.mean(x[4] - x[0] for x in p),
                    't_q5_minus_q1': B.newey_west_t([x[4] - x[0] for x in p], lags=2)[0], 'months': len(p)}

            out['%s|%s' % (s, u)] = {'in': avg(per[:c]), 'out': avg(per[c:])}
    return out


def regress(recs, kind='gross', with_hype=False):
    ys, X = [], []
    for r in recs:
        if r['btc'] is None or (with_hype and r['hype'] is None):
            continue
        y = r[kind] - r['sav']
        row = [1.0, r['btc'], abs(r['btc'])]
        if with_hype:
            row.append(r['hype'])
        ys.append(y)
        X.append(row)
    res = ols_hac(ys, X, lags=2)
    if not res:
        return None
    names = ['alpha_monthly', 'beta_btc', 'gamma_abs_btc'] + (['beta_hype'] if with_hype else [])
    return {'n': res['n'], 'r2': res['r2'], 'alpha_annual': res['coef'][0] * 12,
            **{n: {'coef': res['coef'][i], 't': res['t'][i]} for i, n in enumerate(names)}}


def follower_check(vaults, min_days=60, max_days=None):
    """Independent path: each listed follower's own P&L over its own equity (the API's per-follower accounting)
    against this study's time-weighted index over the same dates. A follower who topped up during the holding earns a
    money-weighted return that can differ from the index for a volatile, performance-chased vault without either being
    wrong; short tenures leave less room for top-ups."""
    pairs = []      # (implied, twr, flow intensity of the vault over the follower's holding)
    for v in vaults.values():
        if v['closed'] or v['excluded'] or len(v['ts']) < 3:
            continue
        for f in v['followers']:
            eq, pnl, apnl = fnum(f.get('vaultEquity')), fnum(f.get('pnl')), fnum(f.get('allTimePnl'))
            entry = f.get('vaultEntryTime')
            days = f.get('daysFollowing', 0) or 0
            if None in (eq, pnl, apnl) or not entry or days < min_days or (max_days is not None and days >= max_days):
                continue
            if abs(pnl - apnl) > 1e-6 * max(1.0, abs(pnl)) or eq - pnl < 1000:
                continue      # several spells, or too small to read
            implied = pnl / (eq - pnl)
            ts, idx = v['ts'], v['idx']
            k = last_le(ts, int(entry))
            if k is None or k + 1 >= len(ts) or idx[k] <= 0:
                continue
            # log-linear interpolation of the index at the entry time
            w = (int(entry) - ts[k]) / (ts[k + 1] - ts[k])
            i0 = idx[k] * (idx[k + 1] / idx[k]) ** w if idx[k + 1] > 0 else idx[k]
            twr = idx[-1] / i0 - 1.0
            mean_av = statistics.mean(v['av'][k:]) or 1.0
            intensity = sum(abs(v['flow'][j]) for j in range(k + 1, len(ts))) / mean_av
            pairs.append((implied, twr, intensity))
    if len(pairs) < 5:
        return None

    def summ(pp):
        if len(pp) < 5:
            return None
        diffs = [p[0] - p[1] for p in pp]
        ad = sorted(abs(x) for x in diffs)
        xs, ys = [p[0] for p in pp], [p[1] for p in pp]
        return {'n': len(pp), 'median_abs_diff': ad[len(ad) // 2], 'p90_abs_diff': ad[int(0.9 * (len(ad) - 1))],
                'share_within_2pp': sum(1 for x in ad if x <= 0.02) / len(ad),
                'share_within_5pp': sum(1 for x in ad if x <= 0.05) / len(ad),
                'median_diff': sorted(diffs)[len(diffs) // 2], 'spearman': spearman(xs, ys),
                'mean_implied': statistics.mean(xs), 'mean_twr': statistics.mean(ys)}

    out = summ(pairs)
    out['low_flow'] = summ([p for p in pairs if p[2] <= 0.5])
    out['high_flow'] = summ([p for p in pairs if p[2] > 0.5])
    out['note'] = ('flow intensity = sum of |net flows| per grid step over the holding / mean equity; with few flows '
                   'the follower\'s money-weighted return and the time-weighted index must agree')
    return out


def stats_check(sdata, vaults):
    """Independent path: the stats file's coarse allTime P&L (last point) against the vaultDetails P&L history."""
    sm = {v['summary']['vaultAddress'].lower(): v for v in sdata}
    closed, open_ = [], []
    for a, v in vaults.items():
        s = sm.get(a)
        if not s:
            continue
        pts = [fnum(x, 0.0) for x in dict(s.get('pnls') or []).get('allTime') or []]
        if not pts or v['all_time_pnl_api'] is None:
            continue
        x, y = pts[-1], v['all_time_pnl_api']
        rel = abs(x - y) / max(1.0, abs(y))
        (closed if v['closed'] else open_).append((abs(x - y), rel))
    out = {}
    for name, arr in (('closed', closed), ('open', open_)):
        if not arr:
            continue
        rels = sorted(r for _, r in arr)
        out[name] = {'n': len(arr), 'share_exact_1usd': sum(1 for d, _ in arr if d <= 1.0) / len(arr),
                     'share_within_1pct': sum(1 for r in rels if r <= 0.01) / len(arr),
                     'median_rel_diff': rels[len(rels) // 2], 'p95_rel_diff': rels[int(0.95 * (len(rels) - 1))]}
    return out


def stats_aggregate(sdata, hlp_leader):
    """Independent of every return computed here: lifetime dollar P&L of all user vaults straight from the stats
    file's coarse allTime series (last point), leaders' own money included."""
    out = {}
    for tag, pick in (('all', lambda s: True), ('closed', lambda s: s['isClosed']),
                      ('open', lambda s: not s['isClosed'])):
        pn = []
        for v in sdata:
            s = v['summary']
            rel = (s.get('relationship') or {}).get('type')
            if rel in ('parent', 'child') or (s.get('leader') or '').lower() == hlp_leader or not pick(s):
                continue
            pts = [fnum(x, 0.0) for x in dict(v.get('pnls') or []).get('allTime') or []]
            if pts:
                pn.append(pts[-1])
        out[tag] = {'n': len(pn), 'sum_pnl': sum(pn), 'sum_gains': sum(x for x in pn if x > 0),
                    'sum_losses': sum(x for x in pn if x < 0), 'share_positive': sum(1 for x in pn if x > 0) / len(pn),
                    'share_below_minus_1k': sum(1 for x in pn if x < -1000) / len(pn),
                    'share_above_1k': sum(1 for x in pn if x > 1000) / len(pn)}
    return out


def capacity_now(vaults, panel_now, universe, signal, frac, weight, keep=None):
    rows = [(a, r) for a, r in panel_now.items() if r['elig'][universe] and (not keep or keep(r))]
    sel = select_top([(a, r['sig'][signal], r['size']) for a, r in rows], frac)
    out = []
    for a, s, size in sel:
        v = vaults[a]
        tvl = v['av'][-1]
        lf = v['lf'] or 0.0
        room = max(0.0, tvl * (lf / 0.05 - 1.0)) if lf > 0 and not v['closed'] and v['allow'] else 0.0
        out.append({'addr': a, 'name': v['name'][:40], 'signal': s, 'tvl_at_t': size, 'tvl_now': tvl,
                    'leader_fraction': lf, 'room_leader_floor': room, 'allow_deposits': v['allow'],
                    'closed': v['closed'], 'followers_listed': v['n_followers_listed'],
                    'commission': v['lc']})
    tot_tvl = sum(x['tvl_now'] for x in out)
    return {'selected': out, 'n': len(out), 'tvl_now': tot_tvl,
            'room_leader_floor': sum(x['room_leader_floor'] for x in out),
            'room_10pct_tvl': sum(min(x['room_leader_floor'], 0.1 * x['tvl_now']) for x in out),
            'n_open_allowing': sum(1 for x in out if x['allow_deposits'] and not x['closed'])}


def reindex(vaults, timing):
    """Copies of the vaults with step returns and index recomputed under another flow-timing assumption."""
    out = {}
    for a, v in vaults.items():
        w = dict(v)
        w['r'], w['flow'], w['flags'] = step_returns(v['av'], v['pnl'], timing=timing)
        w['idx'] = twr_index(w['r'])
        out[a] = w
    return out


def posthoc(core, panel, cal, c, chosen, months_all, prices):
    """Diagnostics added after the pre-committed result was seen (labelled as such in every output): where the
    chosen variant's out-of-sample return comes from, whether it survives losing its best vault, factor exposure in the
    test half alone, a conservative flow-timing rerun, a per-vault follower check, and the months before the calendar."""
    u, s, frac, w = _parts(chosen)
    P = {'note': 'post-hoc: computed after the pre-committed choose-then-test result was seen; not part of the test'}
    recs = run_strategy(panel, cal, u, s, frac, w, detail=True)
    oos = recs[c:]
    P['regress_out_of_sample'] = {'gross': regress(oos), 'net': regress(oos, 'net'),
                                  'gross_with_hype': regress(oos, with_hype=True)}
    m_oos = run_strategy(panel, cal, 'u100k', weight='cw')[c:]
    P['regress_out_of_sample_market_u100k_cw'] = regress(m_oos)
    contrib, held = {}, {}
    for r in oos:
        for a, x in r['w'].items():
            contrib[a] = contrib.get(a, 0.0) + x * r['rets'][a]
            held[a] = held.get(a, 0) + 1
    tot = sum(r['gross'] for r in oos)
    top = sorted(contrib, key=lambda a: -contrib[a])
    P['contributions_out_of_sample'] = {
        'sum_monthly_gross': tot,
        'by_vault': [{'addr': a, 'name': core[a]['name'][:40], 'sum_weighted_return': contrib[a],
                      'share_of_total': contrib[a] / tot if tot else None, 'months_held': held[a]} for a in top[:10]],
        'distinct_vaults_held_in_sample': len({a for r in recs[:c] for a in r['w']}),
        'distinct_vaults_held_out_of_sample': len({a for r in oos for a in r['w']}),
        'overlap': len({a for r in recs[:c] for a in r['w']} & {a for r in oos for a in r['w']})}
    loo = {}
    for a in top[:5]:
        x = series(run_strategy(panel, cal, u, s, frac, w, keep=lambda row, a=a: row['addr'] != a))
        sp = split_perf(x, c)
        loo[core[a]['name'][:40]] = {'out_ann': sp['out']['ann_return'], 'out_t': sp['out_t'],
                                     'in_ann': sp['in']['ann_return']}
    top3 = set(top[:3])
    x = series(run_strategy(panel, cal, u, s, frac, w, keep=lambda row: row['addr'] not in top3))
    sp = split_perf(x, c)
    loo['without the top 3 together'] = {'out_ann': sp['out']['ann_return'], 'out_t': sp['out_t'],
                                         'in_ann': sp['in']['ann_return']}
    P['leave_out_out_of_sample'] = loo
    # conservative flow timing: deposits at the start of each step, withdrawals at its end
    cons = reindex(core, 'conservative')
    pc = build_panel(cons, cal, prices)
    P['conservative_flow_timing'] = {
        'chosen': split_perf(series(run_strategy(pc, cal, u, s, frac, w)), c),
        'market_u100k_cw': split_perf(series(run_strategy(pc, cal, 'u100k', weight='cw')), c),
        'market_u10k_ew': split_perf(series(run_strategy(pc, cal, 'u10k', weight='ew')), c),
        'ic': {k: v for k, v in ic_table(pc, cal, c).items() if k.split('|')[0] in ('size', 'sharpe6', 'ret6')}}
    P['follower_check_top_vaults'] = {core[a]['name'][:40]: {'tenure_ge_60d': follower_check({a: core[a]}),
                                                             'tenure_7_60d': follower_check({a: core[a]}, 7, 60)}
                                      for a in top[:5]}
    # months before the pre-committed calendar (fewer than 10 eligible $100k vaults)
    early = [t for t in months_all if t < cal[0]]
    pe = build_panel(core, early, prices)
    early = [t for t in early if sum(1 for r in pe[t].values() if r['elig'][u]) >= 3]
    if early:
        er = run_strategy(pe, early, u, s, frac, w)
        x = series(er)
        P['pre_calendar_months'] = {'from': day(early[0]), 'to': day(early[-1]), 'n': len(early),
                                    'perf': B.perf(x, 12), 't': B.newey_west_t(x, lags=2)[0],
                                    'top_holdings': sorted({core[a]['name'][:30] for r in er for a in r['top'][:1]})}
        full = x + series(recs)
        P['full_history_chosen_rule'] = {'from': day(early[0]), 'to': day(cal[-1]), 'n': len(full),
                                         'perf': B.perf(full, 12), 't': B.newey_west_t(full, lags=2)[0],
                                         'months_positive': sum(1 for v in full if v > 0)}
    return P


# ---------------------------------------------------------------------------------------------- analyze

def analyze(out):
    pc_path = os.path.join(out, 'precommit.json')
    pc = json.load(open(pc_path))
    if pc['sha256'] != precommit_hash():
        raise SystemExit('PRECOMMIT changed after %s: %s != %s' % (pc['written_at'], pc['sha256'], precommit_hash()))
    t0 = time.time()
    stats, sdata, hlp_leader, vaults_all = load(out)
    prices = load_prices(out)
    core = {a: v for a, v in vaults_all.items() if v['tier'] == 'core'}
    sample = {a: v for a, v in vaults_all.items() if v['tier'] == 'sample'}
    months = decision_months(core)
    panel = build_panel(core, months, prices)
    n_u100 = [sum(1 for r in panel[t].values() if r['elig']['u100k']) for t in months]
    start = next((i for i, n in enumerate(n_u100) if n >= MIN_UNIVERSE_FOR_START), 0)
    cal = months[start:]
    c = B.cutoff_index(len(cal), 0.5)
    A = {'generated': utc(), 'precommit_sha256': pc['sha256'], 'precommit_written_at': pc['written_at']}

    # ---- data and universe
    flags_all = {}
    for v in core.values():
        for f in v['flags']:
            if f:
                flags_all[f] = flags_all.get(f, 0) + 1
    A['data'] = {
        'stats_vaults': len(sdata), 'stats_closed': sum(1 for v in sdata if v['summary']['isClosed']),
        'details_on_disk': len(vaults_all), 'core': len(core), 'sample': len(sample),
        'hlp_leader': hlp_leader, 'excluded_hlp_family': sorted(v['name'] for v in core.values() if v['excluded']),
        'step_days': {str(k): sum(1 for v in core.values() if round(v['step_days']) == k) for k in (1, 7, 14, 28)},
        'step_flags_core': flags_all,
        'calendar': {'first_decision': day(cal[0]), 'last_decision': day(cal[-1]), 'months': len(cal),
                     'in_sample': '%s..%s' % (day(cal[0]), day(cal[c - 1])),
                     'out_of_sample': '%s..%s' % (day(cal[c]), day(cal[-1])), 'cutoff_index': c},
        'eligible_per_month': [{'t': day(t), 'u10k': sum(1 for r in panel[t].values() if r['elig']['u10k']),
                                'u100k': sum(1 for r in panel[t].values() if r['elig']['u100k']),
                                'tvl_u100k': sum(r['size'] for r in panel[t].values() if r['elig']['u100k']),
                                'later_closed_u10k': sum(1 for r in panel[t].values()
                                                         if r['elig']['u10k'] and r['closed_now'])}
                               for t in cal],
    }
    delays = [r['delay_days'] for t in cal for r in panel[t].values() if r['delay_days'] is not None]
    A['data']['entry_delay_days'] = {'median': statistics.median(delays), 'max': max(delays),
                                     'mean': statistics.mean(delays)}
    fl = [x for t in cal for r in panel[t].values() if r['elig']['u10k'] for x in r['flagged']]
    A['data']['flagged_steps_in_holding_windows_u10k'] = {k: fl.count(k) for k in set(fl)}
    A['data']['vault_months'] = {u: sum(1 for t in cal for r in panel[t].values() if r['elig'][u]) for u in UNIVERSES}

    # ---- the vault market (every eligible vault) and its survivorship bias
    survivors = (lambda r: not r['closed_now'])
    market = {}
    for u in UNIVERSES:
        for w in WEIGHTS:
            for tag, keep in (('all', None), ('survivors_only', survivors)):
                recs = run_strategy(panel, cal, u, weight=w, keep=keep)
                market['%s|%s|%s' % (u, w, tag)] = {
                    'net_excess_savings': split_perf(series(recs), c),
                    'gross_excess_savings': split_perf(series(recs, 'gross'), c),
                    'regress_gross': regress(recs), 'regress_gross_hype': regress(recs, with_hype=True),
                    'months': recs}
    A['market'] = market
    # pooled vault-month means (equal weight per vault-month), all vs survivors vs later-closed
    pool = {}
    for u in UNIVERSES:
        for part, rng in (('in', cal[:c]), ('out', cal[c:]), ('full', cal)):
            allv = [r['fwd'] for t in rng for r in panel[t].values() if r['elig'][u] and r['fwd'] is not None]
            surv = [r['fwd'] for t in rng for r in panel[t].values()
                    if r['elig'][u] and r['fwd'] is not None and not r['closed_now']]
            dead = [r['fwd'] for t in rng for r in panel[t].values()
                    if r['elig'][u] and r['fwd'] is not None and r['closed_now']]
            pool['%s|%s' % (u, part)] = {
                'n_all': len(allv), 'mean_all': statistics.mean(allv) if allv else None,
                'median_all': statistics.median(allv) if allv else None,
                'n_survivors': len(surv), 'mean_survivors': statistics.mean(surv) if surv else None,
                'n_later_closed': len(dead), 'mean_later_closed': statistics.mean(dead) if dead else None,
                'share_closed_within_month': (sum(1 for t in rng for r in panel[t].values()
                                                  if r['elig'][u] and r['closed_in']) / len(allv)) if allv else None}
    A['vault_month_pool'] = pool

    # ---- persistence: rank ICs and quintile spreads, all vaults and survivors only
    A['ic'] = ic_table(panel, cal, c)
    A['ic_survivors_only'] = ic_table(panel, cal, c, keep=survivors)
    A['quintiles'] = quintile_table(panel, cal, c)
    A['quintiles_survivors_only'] = quintile_table(panel, cal, c, keep=survivors)

    # ---- the pre-committed variants: choose on the first half, test once on the second
    var_recs, var_series = {}, {}
    for name, s, cut, w, u in variant_names():
        recs = run_strategy(panel, cal, u, s, CUTS[cut], w)
        var_recs[name] = recs
        var_series[name] = series(recs)
    ctt = B.choose_then_test(var_series, frac=0.5, periods_per_year=12, key='sharpe')
    oos_p = [B.newey_west_t(var_series[k][c:], lags=2)[1] for k in var_series]
    rej, adj = B.bh(oos_p, q=0.10)
    table = {}
    for (k, x), p_adj, rj in zip(var_series.items(), adj, rej):
        sp = split_perf(x, c)
        g = split_perf(series(var_recs[k], 'gross'), c)
        table[k] = {'in_ann': sp['in']['ann_return'], 'in_sharpe': sp['in']['sharpe'], 'in_t': sp['in_t'],
                    'out_ann': sp['out']['ann_return'], 'out_sharpe': sp['out']['sharpe'], 'out_t': sp['out_t'],
                    'out_p': sp['out_p'], 'out_bh_adj_p': p_adj, 'out_bh_reject': rj,
                    'gross_out_ann': g['out']['ann_return'], 'gross_in_ann': g['in']['ann_return'],
                    'mean_selected': statistics.mean(r['n_selected'] for r in var_recs[k]),
                    'out_worst_month': sp['out']['worst'], 'out_max_dd': sp['out']['max_drawdown']}
    chosen = ctt['chosen']
    A['variants'] = {'n': len(var_series), 'table': table,
                     'choose_then_test': {k: v for k, v in ctt.items() if k != 'bh_adjusted_p'},
                     'bh_out_of_sample_survivors': [k for k, r in zip(var_series, rej) if r]}
    s_, cut_, w_, u_ = chosen.split('|')
    recs = var_recs[chosen]
    ch = {'name': chosen, 'months': recs, 'net_excess_savings': split_perf(series(recs), c),
          'net_excess_ssr_now': split_perf(series(recs, 'net', 'ssr_now'), c),
          'gross_excess_savings': split_perf(series(recs, 'gross'), c),
          'net_simple_fee_excess': split_perf(series(recs, 'net_simple_fee'), c),
          'regress_gross': regress(recs), 'regress_net': regress(recs, 'net'),
          'regress_gross_hype': regress(recs, with_hype=True),
          'block_bootstrap_out': B.block_bootstrap(series(recs)[c:], block=3),
          'deflated_sharpe_out': B.deflated_sharpe(series(recs)[c:], len(var_series)),
          'turnover_one_sided_monthly': statistics.mean(r['traded_frac'] / 2 for r in recs[1:]),
          'fees_frac_annual': 12 * statistics.mean(r['fees_frac'] for r in recs),
          'sel_tvl_median': statistics.median(r['sel_tvl'] for r in recs),
          'sel_tvl_median_out': statistics.median(r['sel_tvl'] for r in recs[c:]),
          'selected_closed_within_month': sum(r['closed_in'] for r in recs),
          'selected_vault_months': sum(r['n_selected'] for r in recs)}
    ch['late_entry_one_step'] = split_perf(series(run_strategy(panel, cal, u_, s_, CUTS[cut_], w_, late=True)), c)
    ch['friction_10bp'] = split_perf(series(run_strategy(panel, cal, u_, s_, CUTS[cut_], w_,
                                                         friction_bp=FRICTION_BP)), c)
    ch['survivors_only'] = split_perf(series(run_strategy(panel, cal, u_, s_, CUTS[cut_], w_, keep=survivors)), c)
    ch['deposits_open_today_only'] = split_perf(series(run_strategy(
        panel, cal, u_, s_, CUTS[cut_], w_, keep=lambda r: r['closed_now'] or r['allow_now'] is not False)), c)
    A['chosen'] = ch

    # ---- survivorship bias across every variant (out of sample and full), net excess over savings
    surv_tab = {}
    for name, s, cut, w, u in variant_names():
        xs = series(run_strategy(panel, cal, u, s, CUTS[cut], w, keep=survivors))
        x = var_series[name]
        surv_tab[name] = {'full_all': B.perf(x, 12)['ann_return'], 'full_survivors': B.perf(xs, 12)['ann_return'],
                          'out_all': B.perf(x[c:], 12)['ann_return'], 'out_survivors': B.perf(xs[c:], 12)['ann_return']}
    diffs_full = [v['full_survivors'] - v['full_all'] for v in surv_tab.values()]
    A['survivorship'] = {'per_variant': surv_tab, 'mean_bias_full_ann': statistics.mean(diffs_full),
                         'median_bias_full_ann': statistics.median(diffs_full),
                         'mean_bias_out_ann': statistics.mean(v['out_survivors'] - v['out_all']
                                                              for v in surv_tab.values())}

    # ---- the naive retail strategy (copy last quarter's leaderboard), reported whatever the choice
    for nm in ('ret3|q10|ew|u100k', 'ret3|q5|cw|u100k', 'sharpe6|q5|ew|u100k'):
        rr = var_recs[nm]
        A.setdefault('reference_strategies', {})[nm] = {
            'net_excess_savings': split_perf(series(rr), c), 'regress_gross': regress(rr),
            'survivors_only': split_perf(series(run_strategy(panel, cal, *_parts(nm), keep=survivors)), c)}

    # ---- pre-filter bias: the random sample of vaults the filter left out
    sp_panel = build_panel(sample, cal, prices)
    est = 1.0 / REST_SAMPLE_FRAC
    sp = {}
    for u in UNIVERSES:
        ever = {a for t in cal for a, r in sp_panel[t].items() if r['elig'][u]}
        vm = [r['fwd'] for t in cal for r in sp_panel[t].values() if r['elig'][u] and r['fwd'] is not None]
        core_vm = A['data']['vault_months'][u]
        sp[u] = {'sample_vaults_ever_eligible': len(ever), 'estimated_population': len(ever) * est,
                 'sample_vault_months': len(vm), 'estimated_vault_months': len(vm) * est,
                 'share_of_universe_missed': (len(vm) * est / (len(vm) * est + core_vm)) if core_vm else None,
                 'mean_fwd_sample': statistics.mean(vm) if vm else None}
    sp['sample_max_equity'] = {'n': len(sample),
                               'ge_10k': sum(1 for v in sample.values() if max(v['av'] or [0]) >= 1e4),
                               'ge_100k': sum(1 for v in sample.values() if max(v['av'] or [0]) >= 1e5)}
    A['prefilter_bias'] = sp

    # ---- capacity today: what the chosen variant and the naive leaderboard would hold now
    t_now = add_months(int(dt.datetime.strptime(LAST_DECISION, '%Y-%m-%d').replace(
        tzinfo=dt.timezone.utc).timestamp() * 1000), 1)
    pnow = build_panel(core, [t_now], prices)[t_now]
    A['capacity_now'] = {'decision': day(t_now),
                         'chosen': capacity_now(core, pnow, u_, s_, CUTS[cut_], w_),
                         'naive_ret3_q10_u100k': capacity_now(core, pnow, 'u100k', 'ret3', 0.10, 'ew')}

    # ---- post-hoc diagnostics (after the pre-committed result was seen)
    A['posthoc'] = posthoc(core, panel, cal, c, chosen, months, prices)

    # ---- independent checks
    A['checks'] = {'stats_file_vs_details_all_time_pnl': stats_check(sdata, vaults_all),
                   'follower_pnl_vs_twr_index': follower_check(core),
                   'follower_pnl_vs_twr_index_tenure_7_60d': follower_check(core, 7, 60),
                   'stats_file_lifetime_dollar_pnl_user_vaults': stats_aggregate(sdata, hlp_leader)}
    A['seconds'] = round(time.time() - t0, 1)
    write_json(os.path.join(out, 'analysis.json'), A)
    write_manifest(out, A)
    print(json.dumps({'chosen': chosen, 'out': A['chosen']['net_excess_savings']['out'].get('ann_return'),
                      'out_t': A['chosen']['net_excess_savings']['out_t'], 'seconds': A['seconds']}, indent=1))
    return 0


def _parts(name):
    s, cut, w, u = name.split('|')
    return u, s, CUTS[cut], w


def write_manifest(out, A):
    raw = os.path.join(out, 'raw')
    cm = json.load(open(os.path.join(raw, 'collect_manifest.json')))
    plan = json.load(open(os.path.join(raw, 'fetch_plan.json')))
    write_json(os.path.join(out, 'manifest.json'), {
        'generated': utc(), 'analysis_generated': A['generated'], 'precommit_sha256': A['precommit_sha256'],
        'endpoints': {'stats': 'GET ' + STATS_URL + ' (all vaults, closed included; summary + coarse pnls)',
                      'details': 'POST ' + INFO_URL + ' {"type":"vaultDetails","vaultAddress":...} (portfolio '
                                 'histories, leaderFraction, leaderCommission, followers (top 100 only), '
                                 'allowDeposits, isClosed)',
                      'prices': BINANCE_KLINES + ' BTCUSDT/ETHUSDT 1d; ' + INFO_URL + ' candleSnapshot HYPE 1d'},
        'fetch_plan': {k: v for k, v in plan.items() if not isinstance(v, list)},
        'collect': cm, 'counts': {k: A['data'][k] for k in ('stats_vaults', 'details_on_disk', 'core', 'sample')},
        'files': {'raw/vaults_stats.json.gz': 'stats file', 'raw/details/<vault>.json.gz': 'vaultDetails responses',
                  'raw/prices/': 'BTC/ETH (Binance) and HYPE (Hyperliquid) daily closes',
                  'precommit.json': 'variant list and rules, hashed before forward returns were computed',
                  'analysis.json': 'every number', 'tables.md': 'rendered tables'},
        'api_gaps': [
            'no history of leaderFraction, follower count or allowDeposits: only today\'s values, so they cannot be '
            'signals and the deposit gate at t is assumed open while the vault was open',
            'followers list is capped at 100 entries (largest first), so follower counts above 100 are unknown',
            'allTime grid is 24 h / 168 h / 336 h by the vault\'s age today, so month-end values are the last grid '
            'point <= t and holding windows start at the first point >= t (<= 14 days later)',
            'the profit share is charged on withdrawal by the protocol; the simulator charges it on the follower\'s '
            'cost basis, which is the documented rule, but the exact on-chain crystallisation was not observed',
        ],
    })


# ---------------------------------------------------------------------------------------------- render

def _pct(x, d=2, sign=True):
    if x is None:
        return '—'
    return ('%+.*f%%' if sign else '%.*f%%') % (d, 100.0 * x)


def _num(x, d=2):
    if x is None:
        return '—'
    return '%.*f' % (d, x)


def _usd(x):
    if x is None:
        return '—'
    if abs(x) >= 1e6:
        return '$%.2fM' % (x / 1e6)
    if abs(x) >= 1e3:
        return '$%.0fk' % (x / 1e3)
    return '$%.0f' % x


def _sp_row(label, sp):
    i, o = sp['in'], sp['out']
    return '| %s | %s | %s | %s | %s | %s | %s |' % (
        label, _pct(i.get('ann_return')), _num(sp.get('in_t')), _pct(o.get('ann_return')), _num(sp.get('out_t')),
        _num(o.get('sharpe')), _pct(o.get('worst')))


def render(out):
    A = json.load(open(os.path.join(out, 'analysis.json')))
    d = A['data']
    cal = d['calendar']
    L = ['# hl_vault_skill — tables', '',
         'Generated %s from analysis.json (precommit %s…, written %s). Monthly decisions; holding windows start at each '
         'vault\'s first grid point at or after the decision (median %.1f days later, max %.1f). Returns are net of '
         'flows; "net" is after the leader\'s profit share in a simulated follower account; excess is over the '
         'savings rate paid in each year unless marked SSR.' % (
             A['generated'], A['precommit_sha256'][:12], A['precommit_written_at'], d['entry_delay_days']['median'],
             d['entry_delay_days']['max']), '']
    L += ['## Data', '',
          '| item | value |', '|---|---|',
          '| vaults in the stats file (closed) | %d (%d) |' % (d['stats_vaults'], d['stats_closed']),
          '| vaultDetails fetched: core / random sample of the rest | %d / %d |' % (d['core'], d['sample']),
          '| HLP family excluded | %d vaults |' % len(d['excluded_hlp_family']),
          '| grid step (core vaults: 1d / 7d / 14d) | %s / %s / %s |' % (d['step_days'].get('1'), d['step_days'].get('7'),
                                                                     d['step_days'].get('14')),
          '| step flags (core) | %s |' % ', '.join('%s %d' % kv for kv in sorted(d['step_flags_core'].items())),
          '| flagged steps inside u10k holding windows | %s |' % (
              ', '.join('%s %d' % kv for kv in sorted(d['flagged_steps_in_holding_windows_u10k'].items())) or 'none'),
          '| decision calendar | %s → %s, %d months |' % (cal['first_decision'], cal['last_decision'], cal['months']),
          '| choose / test | %s / %s |' % (cal['in_sample'], cal['out_of_sample']),
          '| vault-months u10k / u100k | %d / %d |' % (d['vault_months']['u10k'], d['vault_months']['u100k']), '']
    L += ['Eligible vaults by month (later-closed counted in u10k):', '', '| month | u10k | u100k | u100k equity | '
          'u10k later closed |', '|---|---:|---:|---:|---:|']
    for x in d['eligible_per_month']:
        L.append('| %s | %d | %d | %s | %d |' % (x['t'], x['u10k'], x['u100k'], _usd(x['tvl_u100k']),
                                                x['later_closed_u10k']))
    ck = A['checks']
    L += ['', '## Independent checks', '']
    s = ck['stats_file_vs_details_all_time_pnl']
    for k in ('closed', 'open'):
        if k in s:
            L.append('- Stats-file coarse allTime P&L vs vaultDetails P&L, %s vaults: n %d, exact to $1 %s, within 1%% '
                     '%s, median rel. diff %s, p95 %s.' % (k, s[k]['n'], _pct(s[k]['share_exact_1usd'], 1, False),
                                                           _pct(s[k]['share_within_1pct'], 1, False),
                                                           _pct(s[k]['median_rel_diff'], 3, False),
                                                           _pct(s[k]['p95_rel_diff'], 2, False)))
    f = ck['follower_pnl_vs_twr_index']
    if f:
        L.append('- Listed followers (single spell, >= 60 days, >= $1k basis): own P&L / basis vs this study\'s index '
                 'over the same dates: n %d, Spearman %.3f, median diff %s, median |diff| %s, within 5pp %s; mean %s '
                 '(followers) vs %s (index).' % (f['n'], f['spearman'], _pct(f['median_diff']),
                                                _pct(f['median_abs_diff'], 2, False),
                                                _pct(f['share_within_5pp'], 1, False), _pct(f['mean_implied']),
                                                _pct(f['mean_twr'])))
        sa = ck.get('stats_file_lifetime_dollar_pnl_user_vaults')
        if sa:
            x = sa['all']
            L.append('- Stats file alone, lifetime dollar P&L of all %d user vaults (HLP family out, leaders\' money in): '
                     '%s in total (gains %s, losses %s); %s of vaults ended positive, %s lost more than $1k; closed '
                     'vaults %s, open vaults %s.' % (x['n'], _usd(x['sum_pnl']), _usd(x['sum_gains']),
                                                     _usd(x['sum_losses']), _pct(x['share_positive'], 1, False),
                                                     _pct(x['share_below_minus_1k'], 1, False),
                                                     _usd(sa['closed']['sum_pnl']), _usd(sa['open']['sum_pnl'])))
        g7 = ck.get('follower_pnl_vs_twr_index_tenure_7_60d')
        if g7:
            L.append('- Same check, followers of 7-60 days (less room for top-ups): n %d, Spearman %.3f, median |diff| '
                     '%s, within 5pp %s.' % (g7['n'], g7['spearman'], _pct(g7['median_abs_diff'], 2, False),
                                            _pct(g7['share_within_5pp'], 1, False)))
        for k in ('low_flow', 'high_flow'):
            if f.get(k):
                g = f[k]
                L.append('  - %s vaults: n %d, Spearman %.3f, median |diff| %s, within 5pp %s.' % (
                    k.replace('_', ' '), g['n'], g['spearman'], _pct(g['median_abs_diff'], 2, False),
                    _pct(g['share_within_5pp'], 1, False)))
    L += ['', '## The vault market: every eligible vault', '',
          '| portfolio | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |', '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in A['market'].items():
        L.append(_sp_row(k + ' net', v['net_excess_savings']))
    L += ['', 'Pooled vault-months (each vault-month weighs the same; mean monthly holding return before fees):', '',
          '| universe / part | n | mean | median | survivors (n, mean) | later closed (n, mean) | closed within the month |',
          '|---|---:|---:|---:|---|---|---:|']
    for k, v in A['vault_month_pool'].items():
        L.append('| %s | %d | %s | %s | %d, %s | %d, %s | %s |' % (
            k, v['n_all'], _pct(v['mean_all']), _pct(v['median_all']), v['n_survivors'], _pct(v['mean_survivors']),
            v['n_later_closed'], _pct(v['mean_later_closed']), _pct(v['share_closed_within_month'], 2, False)))
    L += ['', '## Persistence: monthly rank IC of each signal with the next holding return', '',
          '| signal / universe | IC in | t in | IC out | t out | share of months > 0 (out) | IC out, survivors only |',
          '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in A['ic'].items():
        sv = A['ic_survivors_only'].get(k, {})
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (k, _num(v['ic_in'], 3), _num(v['t_in']), _num(v['ic_out'], 3),
                                                           _num(v['t_out']), _pct(v['share_pos_out'], 0, False),
                                                           _num(sv.get('ic_out'), 3)))
    L += ['', 'Quintiles (equal-weight mean monthly holding return before fees; q5 = highest signal):', '',
          '| signal / universe | part | q1 | q2 | q3 | q4 | q5 | q5 − q1 | t |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['quintiles'].items():
        for part in ('in', 'out'):
            q = v[part]
            if not q:
                continue
            L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                k, part, _pct(q['q1']), _pct(q['q2']), _pct(q['q3']), _pct(q['q4']), _pct(q['q5']),
                _pct(q['q5_minus_q1']), _num(q['t_q5_minus_q1'])))
    V = A['variants']
    ctt = V['choose_then_test']
    L += ['', '## The %d pre-committed variants (net excess over the savings rate paid, per year)' % V['n'], '',
          'Chosen on the first half by Sharpe: **%s**; its out-of-sample rank %d of %d; deflated Sharpe of the choice '
          '(in sample, %d tried) %s; BH survivors out of sample (q 0.10): %s.' % (
              ctt['chosen'], ctt['oos_rank'], ctt['n_variants'], ctt['n_variants'],
              _num(ctt['deflated_sharpe_in_sample'], 3), ', '.join(V['bh_out_of_sample_survivors']) or 'none'), '',
          '| variant | in: net/yr | in Sharpe | out: net/yr | out t | BH adj. p | out gross/yr | mean held | out max DD |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in sorted(V['table'].items(), key=lambda kv: -(kv[1]['in_sharpe'] or -99)):
        L.append('| %s | %s | %s | %s | %s | %s | %s | %.1f | %s |' % (
            k, _pct(v['in_ann']), _num(v['in_sharpe']), _pct(v['out_ann']), _num(v['out_t']), _num(v['out_bh_adj_p'], 3),
            _pct(v['gross_out_ann']), v['mean_selected'], _pct(v['out_max_dd'], 1, False)))
    ch = A['chosen']
    L += ['', '## The chosen variant: %s' % ch['name'], '',
          '| series | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |', '|---|---:|---:|---:|---:|---:|---:|',
          _sp_row('net, over savings paid', ch['net_excess_savings']),
          _sp_row('net, over SSR 3.80%', ch['net_excess_ssr_now']),
          _sp_row('gross (no profit share)', ch['gross_excess_savings']),
          _sp_row('net, 10% of every positive month', ch['net_simple_fee_excess']),
          _sp_row('net, entering one grid step late', ch['late_entry_one_step']),
          _sp_row('net, 10bp friction on turnover', ch['friction_10bp']),
          _sp_row('net, survivors only (biased)', ch['survivors_only']),
          _sp_row('net, vaults taking deposits today', ch['deposits_open_today_only']), '']
    bb = ch['block_bootstrap_out']
    L.append('Out of sample: block-bootstrap 95%% interval of the monthly mean %s to %s (point %s); deflated Sharpe '
             '(%d variants) %s. Monthly one-sided turnover %s; profit share paid %s of capital a year; median equity '
             'of the selected vaults %s (out of sample %s); %d of %d selected vault-months closed inside the month.' % (
                 _pct(bb['lo']), _pct(bb['hi']), _pct(bb['point']), V['n'], _num(ch['deflated_sharpe_out'], 3),
                 _pct(ch['turnover_one_sided_monthly'], 1, False), _pct(ch['fees_frac_annual'], 2, False),
                 _usd(ch['sel_tvl_median']), _usd(ch['sel_tvl_median_out']), ch['selected_closed_within_month'],
                 ch['selected_vault_months']))
    L += ['', 'Factor regressions of monthly excess return (HAC t, 2 lags):', '',
          '| series | n | alpha/yr | t | beta BTC | t | gamma abs BTC | t | beta HYPE | t | R² |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']

    def reg_row(label, g):
        if not g:
            return '| %s | — |' % label
        h = g.get('beta_hype') or {}
        return '| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            label, g['n'], _pct(g['alpha_annual']), _num(g['alpha_monthly']['t']), _num(g['beta_btc']['coef']),
            _num(g['beta_btc']['t']), _num(g['gamma_abs_btc']['coef']), _num(g['gamma_abs_btc']['t']),
            _num(h.get('coef')), _num(h.get('t')), _num(g['r2']))

    L.append(reg_row('chosen, gross', ch['regress_gross']))
    L.append(reg_row('chosen, net', ch['regress_net']))
    L.append(reg_row('chosen, gross, with HYPE', ch['regress_gross_hype']))
    for k, v in A['market'].items():
        if k.endswith('|all'):
            L.append(reg_row('market %s, gross' % k, v['regress_gross']))
            L.append(reg_row('market %s, gross, with HYPE' % k, v['regress_gross_hype']))
    for k, v in A.get('reference_strategies', {}).items():
        L.append(reg_row('%s, gross' % k, v['regress_gross']))
    L += ['', '## Reference: copy the leaderboard', '',
          '| strategy | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |', '|---|---:|---:|---:|---:|---:|---:|']
    for k, v in A.get('reference_strategies', {}).items():
        L.append(_sp_row(k + ' net', v['net_excess_savings']))
        L.append(_sp_row(k + ' net, survivors only', v['survivors_only']))
    S = A['survivorship']
    L += ['', '## Survivorship', '',
          'Rerunning all %d variants on vaults that are open today (the database a leaderboard shows) changes the net '
          'excess by %s a year on average over the full calendar (median %s; out of sample %s).' % (
              V['n'], _pct(S['mean_bias_full_ann']), _pct(S['median_bias_full_ann']), _pct(S['mean_bias_out_ann'])), '']
    P = A['prefilter_bias']
    L += ['Pre-filter (random %d%% sample of the %s vaults left out of the full fetch): %d of %d sampled vaults ever '
          'held >= $10k, %d >= $100k.' % (int(100 * REST_SAMPLE_FRAC), '6.3k', P['sample_max_equity']['ge_10k'],
                                         P['sample_max_equity']['n'], P['sample_max_equity']['ge_100k']), '',
          '| universe | sampled vaults ever eligible | est. population | est. vault-months missed | share of universe | '
          'mean holding return (sample) |', '|---|---:|---:|---:|---:|---:|']
    for u in UNIVERSES:
        x = P[u]
        L.append('| %s | %d | %.0f | %.0f | %s | %s |' % (u, x['sample_vaults_ever_eligible'], x['estimated_population'],
                                                         x['estimated_vault_months'],
                                                         _pct(x['share_of_universe_missed'], 1, False),
                                                         _pct(x['mean_fwd_sample'])))
    C = A['capacity_now']
    L += ['', '## Capacity at the %s decision' % C['decision'], '']
    for k in ('chosen', 'naive_ret3_q10_u100k'):
        c = C[k]
        L += ['**%s**: %d vaults, equity %s, follower room before the leader\'s 5%% floor %s (capped at 10%% of each '
              'vault: %s); %d open and taking deposits.' % (k, c['n'], _usd(c['tvl_now']), _usd(c['room_leader_floor']),
                                                            _usd(c['room_10pct_tvl']), c['n_open_allowing']), '',
              '| vault | signal | equity | leader share | room | deposits | listed followers |',
              '|---|---:|---:|---:|---:|---|---:|']
        for x in c['selected'][:25]:
            L.append('| %s (%s…) | %s | %s | %s | %s | %s | %d |' % (
                x['name'].replace('|', '/'), x['addr'][:8], _num(x['signal'], 3), _usd(x['tvl_now']),
                _pct(x['leader_fraction'], 1, False), _usd(x['room_leader_floor']),
                'open' if x['allow_deposits'] and not x['closed'] else 'closed' if x['closed'] else 'off',
                x['followers_listed']))
        L.append('')
    P = A.get('posthoc')
    if P:
        L += ['## Post-hoc diagnostics (after the pre-committed result was seen; not part of the test)', '']
        ro = P['regress_out_of_sample']
        L += ['Factor regressions on the test half only (11 months):', '',
              '| series | n | alpha/yr | t | beta BTC | t | gamma abs BTC | t | beta HYPE | t | R² |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|',
              reg_row('chosen, gross', ro['gross']), reg_row('chosen, net', ro['net']),
              reg_row('chosen, gross, with HYPE', ro['gross_with_hype']),
              reg_row('market u100k cw, gross', P['regress_out_of_sample_market_u100k_cw']), '']
        co = P['contributions_out_of_sample']
        L += ['Where the test-half gross return came from (sum of weight x monthly return %s; %d distinct vaults held '
              'in the choose half, %d in the test half, %d in both):' % (
                  _pct(co['sum_monthly_gross']), co['distinct_vaults_held_in_sample'],
                  co['distinct_vaults_held_out_of_sample'], co['overlap']), '',
              '| vault | months held | contribution | share |', '|---|---:|---:|---:|']
        for x in co['by_vault']:
            L.append('| %s | %d | %s | %s |' % (x['name'].replace('|', '/'), x['months_held'],
                                               _pct(x['sum_weighted_return']), _pct(x['share_of_total'], 1, False)))
        L += ['', 'Leaving vaults out (net excess over savings, per year):', '', '| left out | in | out | t out |',
              '|---|---:|---:|---:|']
        for k, v in P['leave_out_out_of_sample'].items():
            L.append('| %s | %s | %s | %s |' % (k.replace('|', '/'), _pct(v['in_ann']), _pct(v['out_ann']),
                                               _num(v['out_t'])))
        cf = P['conservative_flow_timing']
        L += ['', 'Conservative flow timing (deposits at the start of each step, withdrawals at its end):', '',
              '| series | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |',
              '|---|---:|---:|---:|---:|---:|---:|',
              _sp_row('chosen', cf['chosen']), _sp_row('market u100k cw', cf['market_u100k_cw']),
              _sp_row('market u10k ew', cf['market_u10k_ew']), '']
        L += ['Follower check on the vaults that carry the test half (own P&L vs index):', '',
              '| vault | tenure >= 60d: n, Spearman, median abs diff | 7-60d: n, Spearman, median abs diff |',
              '|---|---|---|']
        for k, v in P['follower_check_top_vaults'].items():
            def fc(g):
                return '%d, %.2f, %s' % (g['n'], g['spearman'] or 0, _pct(g['median_abs_diff'], 1, False)) if g else '—'
            L.append('| %s | %s | %s |' % (k.replace('|', '/'), fc(v['tenure_ge_60d']), fc(v['tenure_7_60d'])))
        fh = P.get('full_history_chosen_rule')
        if fh:
            L += ['', 'The chosen rule over all the history available (%s → %s, %d months): net excess %s a year '
                  '(t %s), %d months positive.' % (fh['from'], fh['to'], fh['n'], _pct(fh['perf']['ann_return']),
                                                   _num(fh['t']), fh['months_positive'])]
        pe = P.get('pre_calendar_months')
        if pe:
            L += ['', 'Before the calendar (%s → %s, %d months with >= 3 eligible vaults): mean monthly net excess %s, '
                  'worst month %s, t %s; largest holdings %s.' % (
                      pe['from'], pe['to'], pe['n'], _pct(pe['perf']['mean']), _pct(pe['perf']['worst']),
                      _num(pe['t']), ', '.join(pe['top_holdings'])), '']
    L += ['## Chosen variant, month by month', '',
          '| month | eligible | held | gross | net | savings | matched BTC | selected equity | closed in month |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in ch['months']:
        L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %d |' % (
            r['t'], r['n_eligible'], r['n_selected'], _pct(r['gross']), _pct(r['net']), _pct(r['sav']), _pct(r['btc']),
            _usd(r['sel_tvl']), r['closed_in']))
    with open(os.path.join(out, 'tables.md'), 'w') as fh:
        fh.write('\n'.join(L) + '\n')
    print('wrote', os.path.join(out, 'tables.md'), len(L), 'lines')
    return 0


# ---------------------------------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('collect')
    c.add_argument('--out', required=True)
    c.add_argument('--parts', default='stats,prices,details')
    c.add_argument('--max-vaults', type=int, default=None)
    a = sub.add_parser('analyze')
    a.add_argument('--out', required=True)
    r = sub.add_parser('render')
    r.add_argument('--out', required=True)
    pc = sub.add_parser('precommit')
    pc.add_argument('--out', required=True)
    args = ap.parse_args(argv)
    if args.cmd == 'precommit':
        return precommit(args.out)
    if args.cmd == 'collect':
        return collect(args.out, set(args.parts.split(',')), args.max_vaults)
    if args.cmd == 'analyze':
        return analyze(args.out)
    if args.cmd == 'render':
        return render(args.out)
    return 1


if __name__ == '__main__':
    sys.exit(main())
