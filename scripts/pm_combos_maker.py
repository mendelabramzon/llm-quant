#!/usr/bin/env python3
"""Would a NEW quoter, pricing Polymarket Combos from the legs' own prices at entry, have earned the combo rent?

Why. pm_parlays (2026-10-14) found that the 25 largest Polymarket Combo makers earned +1.93% on $217M risked since June
(daily HAC t 3.80): a rent paid by parlay buyers, open to any account that quotes through the RFQ SDK, with no maker fee
and a 400 ms response deadline (an auction on price, not a race for block position). It could not say whether an
entrant with a fair-value model would earn it: it had leg prices at entry for 257 fills. This study prices ~30k.

Pipeline (choose on June-August, test once on September-October 13):
  sample   stratified draw of the incumbents' resolved NO positions (the maker sold the buyer's YES) by entry month x
           legs (2-3, 4-6, 7+) x same-game/cross-game x maker; weights N_h / n_h back to the population.
  legs     gamma metadata of every leg market (CLOB token, game start); CLOB batch-prices-history (20 tokens a call,
           1-minute midpoints) in [hour - 30 min, hour + 60 min] windows for every (token, entry hour) needed.
  analyze  fair value (cross-game: product of leg midpoints; same-game: an in-sample correlation lift per leg-type
           signature), calibration, the pre-registered quoting family, choose_then_test, gates, capacity, tail.
  render   tables.md.

Facts this script depends on (verified 2026-10-14, see analysis.json 'checks'):
  * a combo leg's `position_id` is NOT its CLOB token: it is the Exchange-v3 combo position id, listed in gamma's
    `positionIds`; the CLOB token is `clobTokenIds` at the same index (= the leg's outcome_index);
  * `prices-history` points are regular midpoint samples (about one a minute at fidelity 1, from market creation);
    `POST /batch-prices-history` takes at most 20 tokens and `start_ts`/`end_ts`;
  * the maker's NO position is the buyer's YES: YES price = 1 - entry_avg_price (makers pay no fee), contracts =
    gross_entry_cost / entry_avg_price, the YES payout per contract = 1 - realized_payout / contracts (a partial leg
    pays its resolution price, so RESOLVED_PARTIAL combos pay e.g. 0.5 or 0.25);
  * a combo resolves as soon as one leg loses, so recently entered positions that are still alive are missing from a
    resolved-positions pull: the last days over-represent maker wins (the end of the test is checked for it).

Arithmetic (unit-tested in test_pm_combos_maker.py): quote q = fair x (1 + m) rounded up to 0.001; won only if
q < the incumbent's YES price; P&L = (q - payout) x contracts; capital = (1 - q) x contracts from entry to resolution;
no fee.

    uv run python scripts/pm_combos_maker.py sample  --out research/2026-10-14/pm_combos_maker
    uv run python scripts/pm_combos_maker.py legs    --out research/2026-10-14/pm_combos_maker
    uv run python scripts/pm_combos_maker.py analyze --out research/2026-10-14/pm_combos_maker
    uv run python scripts/pm_combos_maker.py render  --out research/2026-10-14/pm_combos_maker
"""
import argparse
import bisect
import collections
import concurrent.futures as cf
import datetime as dt
import json
import math
import statistics
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import backtest as B  # noqa: E402
from polymarket_history import Http, parse_ts, write_gz, read_gz, update_manifest, stable_u, write_json  # noqa: E402
from pm_parlays import own_quote_fill, payout_z, legs_bucket as parlay_legs_bucket, group_by, wmean  # noqa: E402

GAMMA = 'https://gamma-api.polymarket.com'
CLOB = 'https://clob.polymarket.com'
SRC = ROOT / 'research' / '2026-10-14' / 'pm_parlays' / 'raw' / 'polymarket' / 'positions'
SSR = 0.038                       # Sky savings rate (repo convention)
DAY = 86400.0
HOUR = 3600.0
TICK = 0.001
MAX_BUY_QUOTE = 0.90909           # docs: a BUY quote above this is rejected (QUOTED_PRICE_ABOVE_SAFETY_THRESHOLD)
MAX_AGE = 1800                    # a leg with no midpoint in the 30 minutes before entry is unpriced
SPLIT_DAY = '2026-09-01'          # choose on entries before, test once on entries from (pre-registered)
TEST_END = '2026-10-13'           # last entry day of the test (pre-registered)
MARGINS = [0.0, 0.02, 0.05, 0.10, 0.20, 0.40]
STRUCTS = ['cross', 'same']
LEG_BUCKETS = ['2-3', '4-6', '7+']
LIFT_MIN_GROUPS = 40              # a same-game signature needs this many in-sample groups for its own lift
BIG_NOTIONAL = 1000.0             # buyer YES notional at or above which a position is sampled with certainty
SIZE_CAP = 1000.0                 # family B: the quoter fills at most this notional per request (partial fills)
DESCRIPTIVE_VARIANT = 'cross/7+/m=0.40'   # named after the test: the strongest full-sample BH survivor, reported, never a go
STATS = collections.Counter()


# ------------------------------------------------------------------------------------------------ pure arithmetic

def legs_bucket(n):
    if n is None or n < 2:
        return None
    return '2-3' if n <= 3 else ('4-6' if n <= 6 else '7+')


def structure(event_ids):
    """'cross' when every leg is a different event, 'same' when any two legs share one (same-game or mixed),
    None when an event id is missing."""
    ev = list(event_ids)
    if not ev or not all(ev):
        return None
    return 'cross' if len(set(ev)) == len(ev) else 'same'


def position_terms(r):
    """The buyer-side terms of an incumbent's NO position: (yes_price, contracts, yes_payout_per_contract).

    The maker paid entry_avg_price per NO share; the buyer's YES price is 1 - that (no maker fee); the YES payout is
    what NO did not pay. None when the record is not a priced NO position."""
    no = r.get('entry_avg_price_usdc')
    cost = r.get('gross_entry_cost_usdc')
    pay = r.get('realized_payout_usdc')
    if r.get('outcome_index') != 1 or not no or not cost or pay is None or not (0.0 < no < 1.0) or cost <= 0:
        return None
    contracts = cost / no
    payout_no = pay / contracts
    if payout_no < -1e-6 or payout_no > 1.0 + 1e-6:
        return None
    y = min(1.0, max(0.0, 1.0 - payout_no))
    return 1.0 - no, contracts, round(y, 6)       # snap float noise: 1 - 0.99999999 is a maker win, not a payout


def leg_value(status):
    """Realized value of one leg outcome: a win pays 1, a loss 0, a partial (void/retirement) its resolution price,
    which the combos API shows as 0.5. None while open."""
    return {'RESOLVED_WIN': 1.0, 'RESOLVED_LOSS': 0.0, 'RESOLVED_PARTIAL': 0.5}.get(status)


def leg_price_at(series, t, max_age=MAX_AGE):
    """(price, age_s) of the last midpoint at or before t, if it is at most max_age old; else None.
    `series` is [[ts, p], ...] in time order."""
    if not series:
        return None
    i = bisect.bisect_right([x[0] for x in series], t) - 1
    if i < 0:
        return None
    ts, p = series[i]
    if t - ts > max_age or p is None or not (0.0 < p < 1.0):
        return None
    return p, t - ts


def coarse_type(t):
    t = (t or '').lower()
    if t == 'moneyline' or t.endswith('moneyline'):
        return 'ml'
    if 'spread' in t or 'handicap' in t:
        return 'spread'
    if 'total' in t:
        return 'total'
    if 'both_teams' in t or 'btts' in t:
        return 'btts'
    if 'player' in t or 'prop' in t:
        return 'prop'
    return 'other'


def leg_side(ctype, label, p):
    """A coarse side for a same-game signature: totals by Over/Under, everything else by whether the leg is the
    favourite at entry (p >= 0.5)."""
    lab = (label or '').strip().lower()
    if ctype == 'total':
        if lab.startswith('over'):
            return 'over'
        if lab.startswith('under'):
            return 'under'
    if ctype == 'btts':
        return 'yes' if lab.startswith('yes') else 'no'
    return 'hi' if p >= 0.5 else 'lo'


def group_signature(legs):
    """Signature of a same-event group of legs: sorted (coarse type, side) pairs. `legs` are dicts with ctype, side."""
    return '+'.join(sorted('%s:%s' % (l['ctype'], l['side']) for l in legs))


def frechet(probs):
    """Bounds on P(all events) given the marginals: (max(0, sum - (k - 1)), min)."""
    return max(0.0, sum(probs) - (len(probs) - 1)), min(probs)


def combo_fair(groups, lifts=None, default_lift=None):
    """Fair YES price of a combo: the product over events of each event's joint probability.

    `groups` is a list of (signature, [leg probabilities]) per event. A single-leg event contributes its price; a
    same-event group contributes lift x product, clamped to the Frechet bounds, where lift comes from `lifts`
    (signature -> lift, fitted in sample) or `default_lift`. With neither, a same-event group is unpriced (None)."""
    fair = 1.0
    for sig, ps in groups:
        if not ps or any(p is None or not (0.0 < p < 1.0) for p in ps):
            return None
        prod = 1.0
        for p in ps:
            prod *= p
        if len(ps) == 1:
            fair *= prod
            continue
        lift = (lifts or {}).get(sig, default_lift)
        if lift is None:
            return None
        lo, hi = frechet(ps)
        fair *= min(hi, max(lo, lift * prod))
    return fair


def quote_fill(incumbent_yes, fair, m, tick=TICK, cap=MAX_BUY_QUOTE):
    """The win rule: quote q = fair x (1 + m) rounded up to the tick; the request is won only if q is strictly below
    the incumbent's YES fill price, and then fills at q. Returns q or None (pm_parlays.own_quote_fill). A quote above
    the venue's BUY safety threshold cannot be sent."""
    q = own_quote_fill(incumbent_yes, fair, m, tick)
    return None if q is None or q > cap else q


def fill_contracts(incumbent_yes, incumbent_contracts, q):
    """BUY requests are sized in notional (docs): the buyer spends the same pUSD, so a quote at q fills
    notional / q contracts, where notional = the incumbent's YES price x its contracts."""
    return incumbent_yes * incumbent_contracts / q


def quoter_pnl(q, payout, contracts):
    """The quoter sold YES at q: it keeps q and pays the YES payout. No maker fee on Polymarket Combos."""
    return (q - payout) * contracts


def quoter_capital(q, contracts):
    """Collateral for selling YES at q: (1 - q) per contract, held from entry to resolution."""
    return (1.0 - q) * contracts


def weighted_payout_z(fills):
    """Payout z of a weighted sample: fills are (key, weight, contracts, pnl, prob) for a short-YES book.

    Each sampled fill stands for `weight` population fills, so the population P&L estimate is sum(w x pnl) and its
    outcome variance sum(prob (1 - prob) (w x contracts)^2) (exposure netted per key). Passed to pm_parlays.payout_z
    as signed weighted contracts; with unit weights it is that function exactly."""
    return payout_z([(k, -w * c, w * p, pr) for k, w, c, p, pr in fills])


def payout_count_z(fills):
    """The go rule's payout-count z: are fewer combos paying out than the quotes imply?

    fills are (weight, q, payout in [0, 1]); each fill counts once whatever its size. Under the no-edge null the
    payout rate equals the quoted price, so z = (sum w q - sum w y) / sqrt(sum w^2 q (1 - q)). A short book of
    longshots cannot pass by never paying: with zero payouts z is at most about sqrt(sum q), so it needs about four
    expected payouts at the quote before z can reach 2. (The dollar payout z of pm_parlays, P&L over its payout sd,
    reaches 2.0 on a one-expected-payout lottery that never paid; it is kept as a diagnostic.)"""
    e = sum(q for _, q, _ in fills)
    r = sum(y for _, _, y in fills)
    num = sum(w * (q - y) for w, q, y in fills)
    v = sum(w * w * q * (1.0 - q) for w, q, _ in fills)
    return {'fills': len(fills), 'expected_at_quote': e, 'realized': r, 'z': (num / math.sqrt(v)) if v > 0 else None}


def outstanding(intervals, t0, t1, step):
    """Outstanding capital on a grid: intervals are (start, end, amount); returns [(t, sum of amounts open at t)]."""
    ev = []
    for s, e, a in intervals:
        ev.append((s, a))
        ev.append((e, -a))
    ev.sort()
    out, cur, j = [], 0.0, 0
    t = t0
    while t <= t1:
        while j < len(ev) and ev[j][0] <= t:
            cur += ev[j][1]
            j += 1
        out.append((t, cur))
        t += step
    return out


def ruin_buffer(daily_pnl, q=0.01):
    """The equity buffer that a day's loss exceeds with probability q: the empirical (1 - q) quantile of daily loss."""
    losses = sorted(-x for x in daily_pnl)
    if not losses:
        return None
    i = min(len(losses) - 1, int(math.ceil((1.0 - q) * len(losses))) - 1)
    return max(0.0, losses[i])


# ------------------------------------------------------------------------------------------------ helpers

def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec='seconds')


def day_of(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime('%Y-%m-%d')


def notional(r):
    """The buyer's YES notional (pUSD) of an incumbent NO position."""
    t = position_terms(r)
    return t[0] * t[1] if t else 0.0


def load_source_positions():
    """Every resolved position of the 25 incumbent makers (pm_parlays raw), one maker at a time."""
    for p in sorted(SRC.glob('*.json.gz')):
        d = read_gz(p)
        yield d['maker'], d['positions']


# ------------------------------------------------------------------------------------------------ sample

def cmd_sample(args):
    out = Path(args.out)
    pop = collections.defaultdict(lambda: {'n': 0, 'cost': 0.0, 'pnl': 0.0, 'yes_premium': 0.0})
    excl = collections.Counter()
    excl_usd = collections.defaultdict(float)
    keep = {}
    partial = {'positions': 0, 'pnl_usd': 0.0, 'payout_values': collections.Counter(), 'legs_product_agrees': 0}
    for maker, positions in load_source_positions():
        for r in positions:
            pnl_all = (r.get('realized_payout_usdc') or 0.0) - (r.get('gross_entry_cost_usdc') or 0.0) - (r.get('entry_fees_usdc') or 0.0)
            if r.get('outcome_index') != 1:
                excl['maker_yes_side'] += 1
                excl_usd['maker_yes_side'] += pnl_all
                continue
            terms = position_terms(r)
            legs = r.get('legs') or []
            st = structure(l.get('event_id') for l in legs)
            lb = legs_bucket(len(legs))
            t = parse_ts(r.get('first_entry_at'))
            if terms is None or st is None or lb is None or t is None or not r.get('resolved_at'):
                excl['unusable'] += 1
                excl_usd['unusable'] += pnl_all
                continue
            month = r['first_entry_at'][:7]
            h = (month, lb, st, maker)
            yes, c, pay = terms
            pop[h]['n'] += 1
            pop[h]['cost'] += r['gross_entry_cost_usdc']
            pop[h]['pnl'] += (yes - pay) * c
            pop[h]['yes_premium'] += yes * c
            if r.get('status') == 'RESOLVED_PARTIAL':
                partial['positions'] += 1
                partial['pnl_usd'] += (yes - pay) * c
                partial['payout_values'][round(pay, 3)] += 1
                vals = [leg_value(l.get('status')) for l in legs]
                if all(v is not None for v in vals) and abs(math.prod(vals) - pay) < 0.01:
                    partial['legs_product_agrees'] += 1
            u = stable_u('pm_combos_maker|%s|%s|%s' % (maker, r['combo_condition_id'], r['first_entry_at']))
            keep.setdefault(h, []).append((u, dict(r, maker=maker)))
    # allocation: proportional with boosts for the thin structures, a floor per stratum
    boost = {('same', '2-3'): 2.0, ('same', '4-6'): 3.0, ('same', '7+'): 4.0, ('cross', '7+'): 4.0, ('cross', '4-6'): 1.0,
             ('cross', '2-3'): 1.0}
    N = sum(v['n'] for v in pop.values())
    f_lo, f_hi = 0.0, 1.0
    for _ in range(40):
        f = (f_lo + f_hi) / 2.0
        tot = sum(min(v['n'], max(min(v['n'], args.floor), int(round(v['n'] * f * boost[(h[2], h[1])])))) for h, v in pop.items())
        if tot > args.n:
            f_hi = f
        else:
            f_lo = f
    f = f_lo
    # draw within each stratum by hash rank; then post-stratify by ticket size: every position with a YES notional of
    # BIG_NOTIONAL or more is taken with certainty (weight 1), the drawn small ones stand for the stratum's small ones
    sample, alloc, post = [], {}, collections.Counter()
    for h, v in pop.items():
        n_h = min(v['n'], max(min(v['n'], args.floor), int(round(v['n'] * f * boost[(h[2], h[1])]))))
        alloc[h] = n_h
        ranked = sorted(keep[h], key=lambda x: x[0])
        chosen = ranked[:n_h]
        big = [r for _, r in ranked if notional(r) >= BIG_NOTIONAL]
        small_chosen = [r for _, r in chosen if notional(r) < BIG_NOTIONAL]
        n_small_pop = v['n'] - len(big)
        for r in big:
            sample.append(dict(r, stratum='|'.join(h) + '|big', weight=1.0))
        if small_chosen:
            for r in small_chosen:
                sample.append(dict(r, stratum='|'.join(h) + '|small', weight=n_small_pop / len(small_chosen)))
        elif n_small_pop:
            post['small_unrepresented_positions'] += n_small_pop
        post['big'] += len(big)
        post['small_drawn'] += len(small_chosen)
    write_gz(out / 'raw' / 'sample.json.gz', sample)
    census = {'population_no_positions': N, 'strata': len(pop), 'sample': len(sample), 'base_fraction': f,
              'boosts': {'%s/%s' % k: b for k, b in boost.items()}, 'floor': args.floor,
              'big_notional_usd': BIG_NOTIONAL, 'post_stratification': dict(post),
              'excluded': dict(excl), 'excluded_pnl_usd': dict(excl_usd),
              'partial': dict(partial, payout_values={str(k): v for k, v in partial['payout_values'].most_common(12)}),
              'population': {'|'.join(h): v for h, v in sorted(pop.items())},
              'allocation': {'|'.join(h): n for h, n in sorted(alloc.items())}}
    write_json(out / 'raw' / 'census.json', census)
    update_manifest(out, 'sample', {'finished_at': utc(time.time()), 'population_no_positions': N, 'strata': len(pop),
                                    'sample': len(sample), 'base_fraction': f, 'source': str(SRC.relative_to(ROOT))})
    print('population %d NO positions in %d strata; sample %d (base fraction %.4f)' % (N, len(pop), len(sample), f))
    return 0


# ------------------------------------------------------------------------------------------------ legs

def fetch_gamma(http, ids):
    """Gamma metadata for market ids, closed first, then open for the rest."""
    got = {}
    ids = sorted(set(ids))
    for closed in ('&closed=true', ''):
        todo = [i for i in ids if i not in got]
        with cf.ThreadPoolExecutor(4) as ex:
            futs = [ex.submit(http.request, GAMMA + '/markets?' + '&'.join('id=%s' % m for m in todo[i:i + 50]) + closed + '&limit=100')
                    for i in range(0, len(todo), 50)]
            for fu in futs:
                d = fu.result()
                if not isinstance(d, list):
                    STATS['gamma_errors'] += 1
                    continue
                for m in d:
                    ev = (m.get('events') or [{}])[0] or {}
                    got[str(m['id'])] = {'tokens': json.loads(m.get('clobTokenIds') or '[]'),
                                         'position_ids': json.loads(m.get('positionIds') or '[]') if isinstance(m.get('positionIds'), str) else (m.get('positionIds') or []),
                                         'outcomes': json.loads(m.get('outcomes') or '[]'),
                                         'game_start': m.get('gameStartTime'), 'event_start': ev.get('startTime') or ev.get('startDate'),
                                         'start_date': m.get('startDate'), 'closed_time': m.get('closedTime'),
                                         'type': m.get('sportsMarketType'), 'slug': m.get('slug'), 'line': m.get('line')}
    return got


def leg_token(gm, leg):
    """(clob token, error) for a combo leg: its position_id's index in gamma positionIds picks the clobTokenIds entry;
    that index must equal the leg's outcome_index."""
    if not gm:
        return None, 'no_gamma'
    toks, pids, oi = gm.get('tokens') or [], gm.get('position_ids') or [], leg.get('outcome_index')
    if leg.get('position_id') in pids:
        i = pids.index(leg['position_id'])
        if oi is not None and i != oi:
            return None, 'index_mismatch'
    else:
        i = oi
        STATS['token_by_outcome_index'] += 1
    if i is None or i >= len(toks):
        return None, 'no_token'
    return toks[i], None


def game_start(gm):
    return parse_ts(gm.get('game_start')) or parse_ts(gm.get('event_start')) if gm else None


def cmd_legs(args):
    out = Path(args.out)
    sample = read_gz(out / 'raw' / 'sample.json.gz')
    http = Http(interval=args.interval)
    gpath = out / 'raw' / 'gamma.json.gz'
    gamma = read_gz(gpath) if gpath.exists() else {}
    missing = sorted({str(l['market_id']) for r in sample for l in r['legs'] if l.get('market_id')} - set(gamma))
    if missing:
        gamma.update(fetch_gamma(http, missing))
        write_gz(gpath, gamma)
    print('gamma: %d markets (%d were missing)' % (len(gamma), len(missing)), flush=True)
    need = collections.defaultdict(set)          # hour start -> tokens
    cls = collections.Counter()
    for r in sample:
        t = parse_ts(r['first_entry_at'])
        starts, toks = [], []
        for l in r['legs']:
            gm = gamma.get(str(l.get('market_id')))
            tok, err = leg_token(gm, l)
            toks.append(tok)
            starts.append(game_start(gm))
        if any(s is None for s in starts):
            cls['start_unknown'] += 1
            continue
        if t >= min(starts):
            cls['inplay'] += 1
            continue
        if any(x is None for x in toks):
            cls['no_token'] += 1
            continue
        cls['pregame'] += 1
        h = int(t // HOUR * HOUR)
        for tok in toks:
            need[h].add(tok)
    pdir = out / 'raw' / 'prices'
    pdir.mkdir(parents=True, exist_ok=True)
    by_day = collections.defaultdict(list)
    for h in sorted(need):
        by_day[day_of(h)].append(h)
    n_req = sum(math.ceil(len(need[h]) / 20) for h in need)
    print('positions: %s; token-hours %d; batch requests %d' % (dict(cls), sum(len(v) for v in need.values()), n_req), flush=True)
    t_start = time.time()
    done = 0

    def one(h, toks):
        body = {'markets': toks, 'start_ts': int(h - MAX_AGE), 'end_ts': int(h + HOUR), 'fidelity': 1}
        d = http.request(CLOB + '/batch-prices-history', body=body)
        if not isinstance(d, dict) or '__error__' in d or not isinstance(d.get('history'), dict):
            STATS['price_errors'] += 1
            return h, toks, None
        return h, toks, {k: [[x['t'], x['p']] for x in v if x.get('t') is not None] for k, v in d['history'].items()}

    for day in sorted(by_day):
        path = pdir / ('%s.json.gz' % day)
        prev = read_gz(path) if path.exists() else {'hours': {}, 'failed': []}
        jobs = []
        for h in by_day[day]:
            toks = sorted(need[h] - set((prev['hours'].get(str(h)) or {})))
            for i in range(0, len(toks), 20):
                jobs.append((h, toks[i:i + 20]))
        if not jobs:
            continue
        res = collections.defaultdict(dict, {k: dict(v) for k, v in prev['hours'].items()})
        failed = []
        with cf.ThreadPoolExecutor(args.workers) as ex:
            for h, toks, hist in ex.map(lambda j: one(*j), jobs):
                if hist is None:
                    failed.append([h, toks])
                    continue
                for tok in toks:
                    res[str(h)][tok] = hist.get(tok, [])
        write_gz(path, {'day': day, 'hours': res, 'failed': failed})
        done += len(jobs)
        print('%s: %d requests (%d failed); %d/%d done; %.0fs; %s' % (day, len(jobs), len(failed), done, n_req,
                                                                   time.time() - t_start, http.stats()), flush=True)
    update_manifest(out, 'legs', {'finished_at': utc(time.time()), 'gamma_markets': len(gamma), 'classes': dict(cls),
                                  'token_hours': sum(len(v) for v in need.values()), 'batch_requests': n_req,
                                  'http': http.stats(), 'stats': dict(STATS), 'seconds': round(time.time() - t_start)})
    return 0


# ------------------------------------------------------------------------------------------------ analyze

def load_prices(out):
    """(day -> hour -> token -> [[t, p], ...]) from raw/prices."""
    P = {}
    for f in sorted((out / 'raw' / 'prices').glob('*.json.gz')):
        d = read_gz(f)
        P[d['day']] = d['hours']
    return P


def build_rows(out):
    """One row per sampled position: buyer terms, structure, game timing, leg prices at entry and the naive fair."""
    sample = read_gz(out / 'raw' / 'sample.json.gz')
    gamma = read_gz(out / 'raw' / 'gamma.json.gz')
    P = load_prices(out)
    rows, C = [], collections.Counter()
    for r in sample:
        yes, c, pay = position_terms(r)
        t = parse_ts(r['first_entry_at'])
        tr = parse_ts(r['resolved_at'])
        legs = []
        starts = []
        err = None
        for l in r['legs']:
            gm = gamma.get(str(l.get('market_id')))
            tok, e = leg_token(gm, l)
            err = err or e
            st = game_start(gm)
            starts.append(st)
            oi = l.get('outcome_index')
            outs = (gm or {}).get('outcomes') or []
            legs.append({'event': l.get('event_id'), 'type': l.get('type'), 'ctype': coarse_type(l.get('type')),
                         'label': outs[oi] if oi is not None and oi < len(outs) else None, 'token': tok,
                         'value': leg_value(l.get('status')), 'start': st})
        known = all(s_ is not None for s_ in starts)
        pre = known and t < min(starts)
        cls = 'pregame' if pre else ('inplay' if known else 'start_unknown')
        if pre and err:
            cls = 'no_token'
        priced = False
        if cls == 'pregame':
            hours = (P.get(day_of(t)) or {}).get(str(int(t // HOUR * HOUR)))
            if hours is None:
                cls = 'no_price_file'
            else:
                ok = True
                for lg in legs:
                    hit = leg_price_at(hours.get(lg['token']), t)
                    lg['p'], lg['age'] = (hit if hit else (None, None))
                    ok = ok and hit is not None
                priced = ok
        C[cls] += 1
        if cls == 'pregame':
            C['pregame_priced' if priced else 'pregame_unpriced'] += 1
        st = structure(l['event'] for l in legs)
        row = {'maker': r['maker'], 'stratum': r['stratum'], 'w': r['weight'], 'combo': r['combo_condition_id'],
               't': t, 'tr': tr, 'day': day_of(t), 'month': r['first_entry_at'][:7], 'n_legs': len(legs),
               'lb': legs_bucket(len(legs)), 'struct': st, 'yes': yes, 'c': c, 'y': pay, 'status': r['status'],
               'cls': cls, 'priced': priced, 'legs': legs,
               'min_start_gap_s': (min(starts) - t) if known else None}
        if priced:
            for lg in legs:
                lg['side'] = leg_side(lg['ctype'], lg['label'], lg['p'])
            g = collections.OrderedDict()
            for lg in legs:
                g.setdefault(lg['event'], []).append(lg)
            row['groups'] = [(group_signature(v) if len(v) > 1 else None, [x['p'] for x in v],
                              [x['value'] for x in v]) for v in g.values()]
            row['fair_naive'] = math.prod(lg['p'] for lg in legs)
            row['leg_age_max'] = max(lg['age'] for lg in legs)
        rows.append(row)
    return rows, C


def fit_lifts(rows, split_t):
    """In-sample correlation lift per same-event signature: sum w x joint outcome / sum w x product of leg prices,
    over groups whose legs all resolved. Signatures with fewer than LIFT_MIN_GROUPS groups fall back to the pooled
    lift of their group size (2 or 3+)."""
    acc = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for x in rows:
        if not x['priced'] or x['t'] >= split_t:
            continue
        for sig, ps, vs in x['groups']:
            if sig is None or any(v is None for v in vs):
                continue
            prod = math.prod(ps)
            yv = math.prod(vs)
            for key in (sig, 'pooled:%s' % ('2' if len(ps) == 2 else '3+')):
                a = acc[key]
                a[0] += x['w'] * yv
                a[1] += x['w'] * prod
                a[2] += 1
    lifts = {k: v[0] / v[1] for k, v in acc.items() if v[2] >= LIFT_MIN_GROUPS and v[1] > 0}
    table = {k: {'groups': v[2], 'lift': (v[0] / v[1]) if v[1] else None, 'used': k in lifts} for k, v in acc.items()}
    return lifts, table


def fair_of(x, lifts):
    if not x.get('priced'):
        return None
    if x['struct'] == 'cross':
        return x['fair_naive']
    groups = []
    for sig, ps, _ in x['groups']:
        if sig is None:
            groups.append((None, ps))
            continue
        key = sig if sig in lifts else 'pooled:%s' % ('2' if len(ps) == 2 else '3+')
        groups.append((key, ps))
    return combo_fair(groups, lifts)


def calib(rows, key='fair'):
    bands = ((0, 0.02), (0.02, 0.05), (0.05, 0.1), (0.1, 0.2), (0.2, 0.35), (0.35, 0.5), (0.5, 0.75), (0.75, 1.01))
    out = []
    for lo, hi in bands:
        b = [x for x in rows if lo <= x[key] < hi]
        if not b:
            continue
        W = sum(x['w'] for x in b)
        e = sum(x['w'] * x[key] for x in b)
        o = sum(x['w'] * x['y'] for x in b)
        v = sum(x['w'] ** 2 * x[key] * (1 - x[key]) for x in b)
        out.append({'band': '%.2f-%.2f' % (lo, hi), 'n': len(b), 'mean_fair': e / W, 'hit_rate': o / W,
                    'mean_incumbent_yes': sum(x['w'] * x['yes'] for x in b) / W,
                    'z_hits_minus_fair': (o - e) / math.sqrt(v) if v > 0 else None})
    W = sum(x['w'] for x in rows)
    e = sum(x['w'] * x[key] for x in rows)
    o = sum(x['w'] * x['y'] for x in rows)
    v = sum(x['w'] ** 2 * x[key] * (1 - x[key]) for x in rows)
    return {'bands': out, 'n': len(rows), 'hits_over_fair': (o / e) if e else None,
            'z_hits_minus_fair': (o - e) / math.sqrt(v) if v > 0 else None,
            'incumbent_yes_over_fair': (sum(x['w'] * x['yes'] for x in rows) / e) if e else None,
            'note': 'weighted to the population; z = (weighted hits - weighted fair) / sqrt(sum w^2 f (1 - f))'}


def margin_stats(rows):
    if not rows:
        return {'n': 0}
    ms = sorted((x['yes'] / x['fair'] - 1.0, x['w']) for x in rows)
    W = sum(w for _, w in ms)
    acc, med = 0.0, None
    for m, w in ms:
        acc += w
        if acc >= W / 2:
            med = m
            break
    prem = sum(x['w'] * x['yes'] * x['c'] for x in rows)
    fairp = sum(x['w'] * x['fair'] * x['c'] for x in rows)
    inc = sum(x['w'] * (x['yes'] - x['y']) * x['c'] for x in rows)
    cap = sum(x['w'] * (1 - x['yes']) * x['c'] for x in rows)
    return {'n': len(rows), 'margin_median_weighted': med, 'margin_premium_weighted': prem / fairp - 1.0 if fairp else None,
            'incumbent_pnl_usd': inc, 'incumbent_capital_usd': cap, 'incumbent_return_on_capital': inc / cap if cap else None,
            'share_below_fair': sum(w for m, w in ms if m < 0) / W}


def fills_for(rows, sel, m, fair_key='fair', size_cap=None):
    """Won fills of quoting fair x (1 + m) on the rows `sel` keeps: (row, q, pnl, capital, contracts). With a
    size cap the quoter fills at most `size_cap` of the request's notional (the rest goes to the incumbent)."""
    out = []
    for x in rows:
        if not sel(x) or x.get(fair_key) is None:
            continue
        q = quote_fill(x['yes'], x[fair_key], m)
        if q is None:
            continue
        cq = fill_contracts(x['yes'], x['c'], q)
        if size_cap is not None:
            cq = min(cq, size_cap / q)
        out.append((x, q, quoter_pnl(q, x['y'], cq), quoter_capital(q, cq), cq))
    return out


def daily_book(fills, days, t_lo, t_hi, step=600):
    """Weighted per-day P&L by entry day, and the outstanding capital grid between t_lo and t_hi."""
    pnl = collections.Counter()
    for x, q, p, k, cq in fills:
        pnl[x['day']] += x['w'] * p
    grid = outstanding([(x['t'], x['tr'], x['w'] * k) for x, q, p, k, cq in fills], t_lo, t_hi, step)
    return [pnl[d] for d in days], grid


def series_on_capital(pnl_days, grid, days, cut):
    """Daily return series: P&L by entry day over the mean outstanding capital of its half (choose / test)."""
    cut_t = parse_ts(days[cut] + 'T00:00:00Z')
    k_in = statistics.mean([v for t, v in grid if t < cut_t] or [0.0])
    k_out = statistics.mean([v for t, v in grid if t >= cut_t] or [0.0])
    ser = [(p / k_in if k_in > 0 else 0.0) if i < cut else (p / k_out if k_out > 0 else 0.0) for i, p in enumerate(pnl_days)]
    return ser, k_in, k_out


def worst_window(xs, n):
    if len(xs) < n:
        return None
    return min(sum(xs[i:i + n]) for i in range(len(xs) - n + 1))


def cmd_analyze(args):
    out = Path(args.out)
    A = {'generated_at': utc(time.time()), 'ssr': SSR, 'split_day': SPLIT_DAY, 'test_end': TEST_END}
    census = json.loads((out / 'raw' / 'census.json').read_text())
    rows, C = build_rows(out)
    split_t = parse_ts(SPLIT_DAY + 'T00:00:00Z')
    end_t = parse_ts(TEST_END + 'T00:00:00Z') + DAY
    rows = [x for x in rows if x['t'] < end_t]
    A['sample'] = {k: census.get(k) for k in ('population_no_positions', 'strata', 'sample', 'base_fraction', 'boosts', 'floor',
                                              'big_notional_usd', 'post_stratification', 'excluded', 'excluded_pnl_usd', 'partial')}
    A['sample']['classes'] = dict(C)
    A['sample']['rows_through_test_end'] = len(rows)
    W_all = sum(x['w'] for x in rows)
    pri = [x for x in rows if x['priced']]
    A['coverage'] = {
        'weighted_share': {k: sum(x['w'] for x in rows if x['cls'] == k) / W_all for k in ('pregame', 'inplay', 'start_unknown', 'no_token', 'no_price_file')},
        'priced_share_of_pregame_weighted': sum(x['w'] for x in pri) / max(1e-9, sum(x['w'] for x in rows if x['cls'] == 'pregame')),
        'priced_by_legs_struct': {'%s/%s' % k: {'n': len(v), 'weighted_positions': sum(x['w'] for x in v)}
                                  for k, v in sorted(group_by(pri, lambda x: (x['struct'], x['lb'])).items())},
        'pregame_priced_share_by_legs': {lb: sum(x['w'] for x in rows if x['lb'] == lb and x['priced']) / max(1e-9, sum(x['w'] for x in rows if x['lb'] == lb and x['cls'] == 'pregame')) for lb in LEG_BUCKETS},
        'leg_age_median_s': statistics.median([x['leg_age_max'] for x in pri]) if pri else None,
        'entry_within_15min_of_start_share': sum(x['w'] for x in pri if x['min_start_gap_s'] < 900) / max(1e-9, sum(x['w'] for x in pri))}
    # population check: the sample's weighted incumbent P&L against the census (every NO position)
    inc_pop = sum(v['pnl'] for v in census['population'].values())
    inc_smp = sum(x['w'] * (x['yes'] - x['y']) * x['c'] for x in read_rows_all(out))
    A['checks'] = {'incumbent_pnl_population_usd': inc_pop, 'incumbent_pnl_sample_weighted_usd': inc_smp,
                   'partial_payout_equals_leg_product': census['partial']['legs_product_agrees'] == census['partial']['positions'],
                   'token_map': 'leg position_id found in gamma positionIds; CLOB token = clobTokenIds[same index]',
                   'stats': dict(STATS)}
    # ---- same-game lift (in sample) and fair
    lifts, lift_table = fit_lifts(pri, split_t)
    A['same_game_lift'] = {'min_groups': LIFT_MIN_GROUPS, 'fitted_on': 'entries before %s' % SPLIT_DAY,
                           'table': dict(sorted(lift_table.items(), key=lambda kv: -kv[1]['groups']))}
    for x in pri:
        x['fair'] = fair_of(x, lifts)
    fr = [x for x in pri if x['fair'] is not None and 0 < x['fair'] < 1]
    ins = [x for x in fr if x['t'] < split_t]
    oos = [x for x in fr if x['t'] >= split_t]
    A['calibration'] = {'cross_in_sample': calib([x for x in ins if x['struct'] == 'cross']),
                        'same_in_sample': calib([x for x in ins if x['struct'] == 'same']),
                        'same_naive_in_sample': calib([dict(x, fair=x['fair_naive']) for x in ins if x['struct'] == 'same']),
                        'cross_out_of_sample': calib([x for x in oos if x['struct'] == 'cross']),
                        'same_out_of_sample': calib([x for x in oos if x['struct'] == 'same'])}
    A['incumbent_margin'] = {'all': margin_stats(fr)}
    for name, key in (('struct_legs', lambda x: '%s/%s' % (x['struct'], x['lb'])), ('month', lambda x: x['month']),
                      ('half', lambda x: 'in_sample' if x['t'] < split_t else 'out_of_sample')):
        A['incumbent_margin'][name] = {k: margin_stats(v) for k, v in sorted(group_by(fr, key).items())}
    # ---- the pre-registered family: m x struct x legs bucket, daily series on capital, choose then test
    days = []
    d0 = dt.date.fromisoformat(min(x['day'] for x in rows))
    while d0.isoformat() <= TEST_END:
        days.append(d0.isoformat())
        d0 += dt.timedelta(days=1)
    ctx = {'rows': rows, 'fr': fr, 'days': days, 'cut': days.index(SPLIT_DAY), 'split_t': split_t,
           't_lo': parse_ts(days[0] + 'T00:00:00Z'), 't_hi': end_t}
    FA = run_family(ctx, size_cap=None, report=DESCRIPTIVE_VARIANT)
    FB = run_family(ctx, size_cap=SIZE_CAP, report=DESCRIPTIVE_VARIANT)
    for k in ('variants', 'protocol', 'winners_curse', 'capacity', 'tail', 'censoring_check', 'go_rule'):
        A[k] = FA[k]
    A['descriptive_cross7'] = FA['descriptive']
    A['family_capped'] = {k: FB[k] for k in ('variants', 'protocol', 'winners_curse', 'capacity', 'tail', 'censoring_check', 'go_rule', 'descriptive')}
    A['family_capped']['size_cap_usd'] = SIZE_CAP
    A['variant_count'] = {'family_A_full_size': FA['protocol']['variants_in_family'],
                          'family_B_capped': FB['protocol']['variants_in_family'],
                          'total_evaluated': FA['protocol']['variants_in_family'] + FB['protocol']['variants_in_family'],
                          'note': 'family B (notional cap per request) was registered on 2026-10-14 before any test-period '
                                  'price was on disk, after the June data showed 1% of tickets carry 37% of |P&L|; the go rule '
                                  'is family A\'s'}
    A['errors_found'] = ERRORS_FOUND
    A['limitations'] = LIMITATIONS
    A['feasibility'] = {'source': 'https://docs.polymarket.com/trading/combos/market-makers (read 2026-10-14)',
                        'facts': dict(FEASIBILITY)}
    write_json(out / 'analysis.json', A)
    go = FA['go_rule']
    ch, ct, vc, cp = FA['ch'], FA['ct'], FA['variants'][FA['ch']], FA['capacity']
    entries = []
    if go['go']:
        tl = FA['tail']
        entries.append({
            'id': 'pm-combo-quoter', 'name': 'Quote Polymarket Combo RFQs at the legs\' midpoint fair plus a margin',
            'kind': 'rfq-quoting', 'status': 'proposed',
            'thesis': ('Parlay buyers on Polymarket Combos pay the incumbents a margin over the legs\' joint probability. A quoter '
                       'pricing %s at fair x (1 + m) from the legs\' CLOB midpoints, undercutting the observed winner, earned '
                       '%s a year over SSR on %s peak capital in the test (Sep 1-Oct 13; HAC t %.2f; payout-count z %.2f in '
                       'sample, %.2f out).' % (ch, round(cp['excess_over_ssr_on_peak_usd_per_year']), round(cp['capital_peak_usd']),
                                                ct['oos_t'], vc['count_z_in']['z'], vc['count_z_out']['z'])),
            'mechanism': 'RFQ auction: the buyer requests YES on a multi-leg combo, makers quote within 400 ms, the best price '
                         'fills; makers pay no fee; collateral 1 - q per contract until the combo resolves (hours to days).',
            'legs': ['subscribe to RFQ_REQUEST on wss://combos-rfq-gateway-quoter.polymarket.com/ws/rfq',
                     'price each leg from the CLOB midpoint at receipt; fair = product (cross-game) or the frozen in-sample lift (same-game)',
                     'quote q = fair x (1 + m) rounded up to 0.001 for the chosen cell only; never above 0.90909',
                     'hold pUSD collateral; redeem through the relayer at resolution'],
            'capacity_usd': cp['capital_peak_usd'],
            'capital_days': None,
            'kill_criteria': ['payout-count z of live fills below 0 after 500 fills',
                              'trailing 30-day realized edge per $ of capital below the SSR',
                              'share of requests won falling below a third of the backtest share (incumbent response)'],
            'quotes': [{'at': A['generated_at'], 'source': 'history', 'window': 'research/2026-10-14/pm_combos_maker',
                        'net_apr': cp['excess_over_ssr_on_peak_usd_per_year'] / cp['capital_peak_usd'] if cp['capital_peak_usd'] else None,
                        'usd': cp['excess_over_ssr_on_peak_usd_per_year'], 'go': True, 'present': True,
                        'note': 'excess over SSR on peak outstanding capital; 25 incumbents\' fills, weighted sample'}],
            'risks': ['winner\'s curse: the quote wins exactly where the leg fair is lowest against the incumbents\'',
                      'short a lottery: worst test day %s, worst week %s; 1%% daily-ruin buffer %s (empirical)' % (
                          round(tl['daily_pnl_out']['worst_day_usd'] or 0), round(tl['daily_pnl_out']['worst_week_usd'] or 0),
                          round(tl['ruin_buffer_1pct_empirical_usd'] or 0)),
                      'incumbents respond: the backtest assumes their quotes do not move',
                      'unfilled requests are not in the history: share won is measured against filled requests only'],
            'evidence': ['research/2026-10-14/pm_combos_maker/analysis.json', 'research/2026-10-14/pm_combos_maker/tables.md']})
    write_json(out / 'book_entries.json', entries)
    update_manifest(out, 'analyze', {'finished_at': A['generated_at'], 'rows': len(rows), 'priced': len(pri),
                                     'chosen': ch, 'go': go['go'], 'chosen_capped': FB['ch'], 'go_capped': FB['go_rule']['go']})
    for F in (FA, FB):
        print(json.dumps({'family': F['protocol']['size_cap_usd'], 'chosen': F['ch'], 'in_sample_positive': F['ct']['in_sample_positive'],
                          'oos_t': F['ct']['oos_t'], 'oos_rank': F['ct']['oos_rank'], 'bh_pos': F['ct']['bh_survivors_positive'],
                          'go': F['go_rule']}, default=str))
    return 0


def run_family(ctx, size_cap=None, report=None):
    """The 36-variant family at one fill-size rule: daily series, choose_then_test, per-variant gates, the winner's
    curse, and the chosen variant's capacity, tail and censoring check."""
    rows, fr, days, cut, split_t, t_lo, t_hi = (ctx[k] for k in ('rows', 'fr', 'days', 'cut', 'split_t', 't_lo', 't_hi'))
    variants, meta, books = {}, {}, {}
    for st in STRUCTS:
        for lb in LEG_BUCKETS:
            for m in MARGINS:
                name = '%s/%s/m=%.2f' % (st, lb, m)
                sel = (lambda x, st=st, lb=lb: x['struct'] == st and x['lb'] == lb)
                fl = fills_for(fr, sel, m, size_cap=size_cap)
                pnl_days, grid = daily_book(fl, days, t_lo, t_hi)
                ser, k_in, k_out = series_on_capital(pnl_days, grid, days, cut)
                variants[name] = ser
                meta[name] = {'struct': st, 'lb': lb, 'm': m}
                books[name] = (fl, pnl_days, grid, k_in, k_out)
    ct = B.choose_then_test(variants, frac=cut / len(days), periods_per_year=365)
    assert ct['cutoff_index'] == cut, (ct['cutoff_index'], cut)
    ch = ct['chosen']
    vdesc = {}
    for name, ser in variants.items():
        fl, pnl_days, grid, k_in, k_out = books[name]
        fin = [f for f in fl if f[0]['t'] < split_t]
        fout = [f for f in fl if f[0]['t'] >= split_t]
        zi = weighted_payout_z([(f[0]['combo'], f[0]['w'], f[4], f[2], f[0]['fair']) for f in fin])   # one bet per combo
        zo = weighted_payout_z([(f[0]['combo'], f[0]['w'], f[4], f[2], f[0]['fair']) for f in fout])
        cell = [x for x in fr if x['struct'] == meta[name]['struct'] and x['lb'] == meta[name]['lb']]
        vdesc[name] = {'fills_in': len(fin), 'fills_out': len(fout), 'cell_rows': len(cell),
                       'in_sample_sharpe': B.perf(ser[:cut], 365).get('sharpe'), 'in_sample_ann_return': B.perf(ser[:cut], 365).get('ann_return'),
                       'in_sample_hac_t': B.newey_west_t(ser[:cut])[0],
                       'oos_ann_return': B.perf(ser[cut:], 365).get('ann_return'), 'oos_hac_t': B.newey_west_t(ser[cut:])[0],
                       'pnl_in_usd': sum(pnl_days[:cut]), 'pnl_out_usd': sum(pnl_days[cut:]),
                       'capital_mean_in_usd': k_in, 'capital_mean_out_usd': k_out,
                       'payout_z_in': zi, 'payout_z_out': zo,
                       'count_z_in': payout_count_z([(f[0]['w'], f[1], f[0]['y']) for f in fin]),
                       'count_z_out': payout_count_z([(f[0]['w'], f[1], f[0]['y']) for f in fout])}
    protocol = {'variants_in_family': len(variants), 'variant_names': list(variants), 'cutoff_day': days[cut],
                'days': len(days), 'first_day': days[0], 'last_day': days[-1], 'choose_then_test': ct, 'size_cap_usd': size_cap,
                'series': 'daily P&L of the quotes won, by entry day, over the mean outstanding (1 - q) capital of '
                          'the half (choose / test); weighted to the 25 incumbents\' flow'}
    wc = {}
    for name in variants:
        fl = books[name][0]
        if not fl:
            continue
        Cn = sum(f[0]['w'] * f[4] for f in fl)
        Ci = sum(f[0]['w'] * f[0]['c'] for f in fl)
        cap = sum(f[0]['w'] * f[3] for f in fl)
        wc[name] = {'won': len(fl), 'model_edge_per_contract': sum(f[0]['w'] * (f[1] - f[0]['fair']) * f[4] for f in fl) / Cn,
                    'realized_edge_per_contract': sum(f[0]['w'] * f[2] for f in fl) / Cn,
                    'incumbent_edge_per_contract_same_fills': sum(f[0]['w'] * (f[0]['yes'] - f[0]['y']) * f[0]['c'] for f in fl) / Ci,
                    'realized_return_on_capital_per_fill': sum(f[0]['w'] * f[2] for f in fl) / cap if cap else None,
                    'mean_q': sum(f[0]['w'] * f[1] * f[4] for f in fl) / Cn,
                    'mean_fair': sum(f[0]['w'] * f[0]['fair'] * f[4] for f in fl) / Cn,
                    'hit_rate': sum(f[0]['w'] * f[0]['y'] * f[4] for f in fl) / Cn,
                    'hit_rate_per_fill': sum(f[0]['w'] * f[0]['y'] for f in fl) / sum(f[0]['w'] for f in fl),
                    'mean_q_per_fill': sum(f[0]['w'] * f[1] for f in fl) / sum(f[0]['w'] for f in fl)}
    def block(ch):
        fl, pnl_days, grid, k_in, k_out = books[ch]
        vc = vdesc[ch]
        g_out = [v for t, v in grid if t >= split_t]
        n_out = len(days) - cut
        pnl_out_day = sum(pnl_days[cut:]) / n_out
        cap_avg, cap_peak = (statistics.mean(g_out) if g_out else 0.0), (max(g_out) if g_out else 0.0)
        flow_all = [x for x in rows if x['t'] >= split_t]
        cell = [x for x in fr if x['t'] >= split_t and x['struct'] == meta[ch]['struct'] and x['lb'] == meta[ch]['lb']]
        won_out = [f for f in fl if f[0]['t'] >= split_t]
        prem = lambda xs: sum(x['w'] * x['yes'] * x['c'] for x in xs)  # noqa: E731
        won_prem = sum(f[0]['w'] * f[1] * f[4] for f in won_out)
        out_pnl = pnl_days[cut:]
        weekly = [sum(out_pnl[i:i + 7]) for i in range(0, len(out_pnl) - 6)]
        sd_ind = []
        for d in days[cut:]:
            v = sum(f[0]['w'] * f[0]['fair'] * (1 - f[0]['fair']) * f[4] ** 2 for f in won_out if f[0]['day'] == d)
            sd_ind.append(math.sqrt(v))
        capacity = {'chosen': ch, 'size_cap_usd': size_cap,
                    'basis': 'the 25 incumbents\' fills (84.1% of onchain maker $), weighted from the sample; whole-flow figures divide by 0.841',
                    'share_won_of_cell_premium': prem([f[0] for f in won_out]) / max(1e-9, prem(cell)),
                    'share_won_of_all_no_flow_premium': prem([f[0] for f in won_out]) / max(1e-9, prem(flow_all)),
                    'share_won_of_cell_count': sum(f[0]['w'] for f in won_out) / max(1e-9, sum(x['w'] for x in cell)),
                    'premium_sold_usd_per_day': won_prem / n_out,
                    'pnl_usd_per_day': pnl_out_day, 'pnl_usd_per_year': pnl_out_day * 365,
                    'capital_avg_usd': cap_avg, 'capital_peak_usd': cap_peak,
                    'excess_over_ssr_on_peak_usd_per_year': pnl_out_day * 365 - SSR * cap_peak,
                    'excess_over_ssr_on_avg_usd_per_year': pnl_out_day * 365 - SSR * cap_avg,
                    'whole_flow_excess_on_peak_usd_per_year': (pnl_out_day * 365 - SSR * cap_peak) / 0.841,
                    'yield_on_peak': (pnl_out_day * 365 / cap_peak) if cap_peak else None,
                    'yield_on_avg': (pnl_out_day * 365 / cap_avg) if cap_avg else None,
                    'excess_ci95_usd_per_year': [pnl_out_day * 365 - SSR * cap_peak - 1.96 * (vc['payout_z_out'].get('payout_sd_usd') or 0) / n_out * 365,
                                                 pnl_out_day * 365 - SSR * cap_peak + 1.96 * (vc['payout_z_out'].get('payout_sd_usd') or 0) / n_out * 365]}
        tail = {'daily_pnl_out': {'worst_day_usd': min(out_pnl) if out_pnl else None, 'best_day_usd': max(out_pnl) if out_pnl else None,
                                  'worst_week_usd': min(weekly) if weekly else None,
                                  'quantiles_usd': {str(q): sorted(out_pnl)[int(q * (len(out_pnl) - 1))] for q in (0.01, 0.05, 0.25, 0.5, 0.75, 0.95)} if out_pnl else None,
                                  'losing_days': sum(1 for v in out_pnl if v < 0), 'days': len(out_pnl)},
                'daily_pnl_full': {'worst_day_usd': min(pnl_days), 'worst_week_usd': worst_window(pnl_days, 7),
                                   'losing_days': sum(1 for v in pnl_days if v < 0), 'days': len(pnl_days)},
                'ruin_buffer_1pct_empirical_usd': ruin_buffer(out_pnl, 0.01),
                'ruin_buffer_1pct_empirical_full_usd': ruin_buffer(pnl_days, 0.01),
                'ruin_buffer_1pct_independent_usd': (max(0.0, 2.326 * statistics.mean(sd_ind) - pnl_out_day) if sd_ind else None),
                'note': 'empirical = the sample\'s weighted daily P&L, as if each sampled fill stood for w identical bets '
                        '(perfectly correlated copies: an upper bound on dispersion); independent = normal approximation with '
                        'each copy independent (a lower bound). Losses never exceed posted collateral (1 - q per contract).'}
        early_end = days.index('2026-10-08') + 1 if '2026-10-08' in days else len(days)
        ser_c = variants[ch][cut:early_end]
        cens = {'test_through': days[early_end - 1], 'oos_hac_t': B.newey_west_t(ser_c)[0],
                'oos_ann_return': B.perf(ser_c, 365).get('ann_return'),
                'maker_loss_share_by_entry_day_last10': {d: (sum(x['w'] for x in rows if x['day'] == d and x['y'] > 0) / max(1e-9, sum(x['w'] for x in rows if x['day'] == d))) for d in days[-10:]},
                'maker_loss_share_sep': sum(x['w'] for x in rows if x['month'] == '2026-09' and x['y'] > 0) / max(1e-9, sum(x['w'] for x in rows if x['month'] == '2026-09'))}
        return capacity, tail, cens, vc

    capacity, tail, cens, vc = block(ch)
    descriptive = None
    if report:
        c2, t2, e2, v2 = block(report)
        descriptive = {'variant': report, 'variant_stats': v2, 'capacity': c2, 'tail': t2, 'censoring_check': e2,
                       'note': 'descriptive only: not the in-sample choice, so it cannot carry a go'}
    go = {'in_sample_positive': bool(ct['in_sample_positive']),
          'oos_hac_t_ge_2': (ct['oos_t'] or 0) >= 2.0,
          'chosen_in_bh_survivors_positive': ch in ct['bh_survivors_positive'],
          'payout_count_z_in_ge_2': (vc['count_z_in'].get('z') or 0) >= 2.0,
          'payout_count_z_out_ge_2': (vc['count_z_out'].get('z') or 0) >= 2.0,
          'excess_over_ssr_positive': capacity['excess_over_ssr_on_peak_usd_per_year'] > 0}
    go['go'] = all(go.values())
    return {'variants': vdesc, 'protocol': protocol, 'winners_curse': wc, 'capacity': capacity, 'tail': tail,
            'censoring_check': cens, 'go_rule': go, 'ch': ch, 'ct': ct, 'descriptive': descriptive}


def read_rows_all(out):
    """Every sampled position's buyer terms and weight (for the population check)."""
    rows = []
    for r in read_gz(out / 'raw' / 'sample.json.gz'):
        yes, c, pay = position_terms(r)
        rows.append({'w': r['weight'], 'yes': yes, 'c': c, 'y': pay})
    return rows


# ------------------------------------------------------------------------------------------------ render

def _pct(x, d=1):
    return '—' if x is None else ('%.' + str(d) + 'f%%') % (100.0 * x)


def _usd(x):
    if x is None:
        return '—'
    a = abs(x)
    return '$%.2fM' % (x / 1e6) if a >= 1e6 else ('$%.1fk' % (x / 1e3) if a >= 1e4 else '$%.0f' % x)


def _f(x, d=2):
    return '—' if x is None else ('%.' + str(d) + 'f') % x


ERRORS_FOUND = [
    'task brief: a combo leg position_id is not its CLOB token (prices-history on it returns nothing); it is the Exchange-v3 '
    'combo position id listed in gamma positionIds; the CLOB token is clobTokenIds at the same index, which equals the leg '
    'outcome_index on every leg checked',
    'pm_parlays by_legs table: a dict comprehension over legs_total overwrote each bucket with its last member: 5-6 shows the '
    '33,007 six-leg positions of 81,228, 7-10 the 7,268 ten-leg of 61,183, 11+ one of 17,202',
    'pm_parlays coordinator note: the $11k recount gap is the $11,188.64 of entry fees on maker-YES-side positions (which '
    'pm_parlays agg ignored), not RESOLVED_PARTIAL; partials are 2,802 NO positions, incumbents lost $238k on them, and the '
    'YES payout equals the product of leg values (a partial leg 0.5) on all 2,802',
    'gate: the dollar payout z of pm_parlays passes a lottery short (z 2.0 on one expected payout that never came); the gate is '
    'the payout-count z against the count the quotes imply',
    'sample: 1% of tickets (notional >= $1,288) carry 37% of |P&L|; at weights of ~26 the first draw measured whales, not '
    'edge; every ticket >= $1,000 is now taken with certainty and the rest post-stratified',
    'sizing: BUY requests are sized in notional (docs), so a lower quote fills notional / q contracts, not the incumbent\'s '
    'contract count; quotes above 0.90909 cannot be sent',
    'censoring: a combo resolves when its first leg loses, so recent positions still alive are missing from a resolved-only '
    'pull and the last days over-represent maker wins; the test is re-run through 2026-10-08',
]

LIMITATIONS = [
    'a position can aggregate several fills: in the latest 500 activity rows of 0x26cf4a41, 13 of 209 combos had 2-6 SPLITs '
    '(fills) spread over 31 s to 7.6 h; leg prices are taken at first_entry_at and compared with the average price',
    'only filled requests are observed: requests the incumbents priced too high (unfilled) and fills by the other ~16% of '
    'maker dollars are not in the history, so share won is against the 25 incumbents\' fills only',
    'incumbent quotes are held fixed: a new quoter undercutting them would meet a response the backtest cannot see',
    'pre-game is judged by gamma gameStartTime (scheduled); a late-starting match can leak in-play entries into the set',
]

FEASIBILITY = [
    ('subscribe', 'WebSocket wss://combos-rfq-gateway-quoter.polymarket.com/ws/rfq; auth with CLOB API credentials as the first message within 30 s; ping/pong every 30 s'),
    ('requests', 'RFQ_REQUEST messages, side always YES; BUY sized in notional (pUSD), SELL in shares; partial fills via size_e6'),
    ('deadline', '400 ms before submission_deadline (late quotes: SUBMISSION_WINDOW_CLOSED); Last Look optional, needs ~$2,500 combo notional and Polymarket approval, >15% declines in an hour pauses the maker'),
    ('quote limits', 'BUY quote above 0.90909 rejected (QUOTED_PRICE_ABOVE_SAFETY_THRESHOLD); MAKER_QUOTE_LIMITED exists but no numbers are published; no size or position limits documented'),
    ('collateral', 'pUSD in the maker wallet, approved to Exchange v3, plus PositionManager setApprovalForAll; balance reserved before execution (BALANCE_VALIDATION_FAILED, PRE_EXECUTION_BALANCE_RESERVATION_FAILED); a short YES costs 1 - q per contract until the combo resolves and is redeemed through the relayer'),
    ('fees', 'makers pay none (pm_parlays: 96.7% of 14,523 onchain matches charge 0.05·p(1−p) to the requester only)'),
    ('visibility', 'RFQ_TRADE broadcasts every fill to authenticated quoter sessions without maker identity or allocation; with RFQ_REQUEST this shows which requests went unfilled (inferred, not stated)'),
    ('history', 'data-api /v2/positions/combos and /v2/activity/combos per wallet; no public archive of requests or losing quotes'),
]


def cmd_render(args):
    out = Path(args.out)
    A = json.loads((out / 'analysis.json').read_text())
    L = ['# pm_combos_maker tables (%s)' % A['generated_at'], '',
         'Every number is in `analysis.json` (key in brackets). Population = the 25 incumbent makers\' resolved NO '
         'positions (the maker sold the buyer\'s YES), June to 2026-10-13, from pm_parlays raw; sample weighted back.', '']
    S = A['sample']
    L += ['## 1. Sample and coverage [sample, coverage, checks]', '', '| item | value |', '|---|---|',
          '| population NO positions / strata | %d / %d |' % (S['population_no_positions'], S['strata']),
          '| sample (base fraction, boosts) | %d (%.4f; %s) |' % (S['sample'], S['base_fraction'], ', '.join('%s x%g' % kv for kv in S['boosts'].items())),
          '| excluded: maker YES side / unusable | %d / %d |' % (S['excluded'].get('maker_yes_side', 0), S['excluded'].get('unusable', 0)),
          '| RESOLVED_PARTIAL NO positions / their incumbent P&L | %d / %s; YES payout = product of leg values (partial leg 0.5) in %s |' % (
              S['partial']['positions'], _usd(S['partial']['pnl_usd']), 'all' if A['checks']['partial_payout_equals_leg_product'] else 'NOT all'),
          '| classes (sample rows) | %s |' % ', '.join('%s %d' % kv for kv in sorted(S['classes'].items())),
          '| weighted share pre-game / in-play | %s / %s |' % (_pct(A['coverage']['weighted_share']['pregame']), _pct(A['coverage']['weighted_share']['inplay'])),
          '| priced share of pre-game (weighted) | %s |' % _pct(A['coverage']['priced_share_of_pregame_weighted']),
          '| pre-game priced share by legs | %s |' % ', '.join('%s %s' % (k, _pct(v)) for k, v in A['coverage']['pregame_priced_share_by_legs'].items()),
          '| median age of the oldest leg midpoint at entry | %s s |' % _f(A['coverage']['leg_age_median_s'], 0),
          '| priced entries within 15 min of the first game start | %s |' % _pct(A['coverage']['entry_within_15min_of_start_share']),
          '| incumbent P&L: population / sample-weighted | %s / %s |' % (_usd(A['checks']['incumbent_pnl_population_usd']), _usd(A['checks']['incumbent_pnl_sample_weighted_usd'])), '']
    L += ['| priced cell | sample rows | weighted positions |', '|---|---:|---:|']
    for k, v in A['coverage']['priced_by_legs_struct'].items():
        L.append('| %s | %d | %.0f |' % (k, v['n'], v['weighted_positions']))
    L += ['', '## 2. Is the leg-midpoint fair calibrated? [calibration]', '',
          '| set | n | hits / fair | z (hits − fair) | incumbent YES / fair |', '|---|---:|---:|---:|---:|']
    for k, v in A['calibration'].items():
        L.append('| %s | %d | %s | %s | %s |' % (k, v['n'], _f(v['hits_over_fair'], 3), _f(v['z_hits_minus_fair']), _f(v['incumbent_yes_over_fair'], 3)))
    L += ['', 'Cross-game, in sample, by fair band:', '', '| fair band | n | mean fair | hit rate | incumbent YES | z |', '|---|---:|---:|---:|---:|---:|']
    for b in A['calibration']['cross_in_sample']['bands']:
        L.append('| %s | %d | %.4f | %.4f | %.4f | %s |' % (b['band'], b['n'], b['mean_fair'], b['hit_rate'], b['mean_incumbent_yes'], _f(b['z_hits_minus_fair'])))
    L += ['', '## 3. Same-game correlation lift, fitted on entries before %s [same_game_lift]' % A['split_day'], '',
          '| signature | groups | lift (hits / product) | used |', '|---|---:|---:|---|']
    for k, v in list(A['same_game_lift']['table'].items())[:25]:
        L.append('| %s | %d | %s | %s |' % (k, v['groups'], _f(v['lift'], 3), 'yes' if v['used'] else 'no'))
    L += ['', '## 4. The incumbents\' margin over the fair [incumbent_margin]', '',
          '| cut | bucket | n | weighted median margin | premium-weighted margin | incumbent P&L | return on capital | share below fair |',
          '|---|---|---:|---:|---:|---:|---:|---:|']
    im = A['incumbent_margin']
    v = im['all']
    L.append('| all | priced | %d | %s | %s | %s | %s | %s |' % (v['n'], _pct(v['margin_median_weighted']), _pct(v['margin_premium_weighted']), _usd(v['incumbent_pnl_usd']), _pct(v['incumbent_return_on_capital'], 2), _pct(v['share_below_fair'])))
    for cut in ('struct_legs', 'month', 'half'):
        for k, v in im[cut].items():
            L.append('| %s | %s | %d | %s | %s | %s | %s | %s |' % (cut, k, v['n'], _pct(v['margin_median_weighted']), _pct(v['margin_premium_weighted']), _usd(v['incumbent_pnl_usd']), _pct(v['incumbent_return_on_capital'], 2), _pct(v['share_below_fair'])))
    P = A['protocol']
    ct = P['choose_then_test']
    L += ['', '## 5. Protocol: %d pre-registered variants, chosen on %s..%s, tested once on %s..%s [protocol, variants]' % (
        P['variants_in_family'], P['first_day'], '2026-08-31', P['cutoff_day'], P['last_day']), '',
          '| variant | fills in / out | in-sample Sharpe | in-sample t | OOS ann. return | OOS HAC t | P&L in / out | payout z in / out | count z in / out |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['variants'].items():
        L.append('| %s | %d / %d | %s | %s | %s | %s | %s / %s | %s / %s | %s / %s |' % (
            k, v['fills_in'], v['fills_out'], _f(v['in_sample_sharpe']), _f(v['in_sample_hac_t']), _pct(v['oos_ann_return']),
            _f(v['oos_hac_t']), _usd(v['pnl_in_usd']), _usd(v['pnl_out_usd']), _f(v['payout_z_in'].get('z')), _f(v['payout_z_out'].get('z')),
            _f(v['count_z_in'].get('z')), _f(v['count_z_out'].get('z'))))
    L += ['', '| item | value |', '|---|---|',
          '| chosen | %s |' % ct['chosen'],
          '| in-sample positive / ann. return / Sharpe | %s / %s / %s |' % (ct['in_sample_positive'], _pct(ct['in_sample'].get('ann_return')), _f(ct['in_sample'].get('sharpe'))),
          '| out-of-sample ann. return / Sharpe / HAC t / rank | %s / %s / %s / %d of %d |' % (_pct(ct['out_of_sample'].get('ann_return')), _f(ct['out_of_sample'].get('sharpe')), _f(ct['oos_t']), ct['oos_rank'], ct['n_variants']),
          '| BH survivors (positive, full sample) | %s |' % (', '.join(ct['bh_survivors_positive']) or 'none'),
          '| deflated Sharpe of the in-sample choice | %s |' % _f(ct['deflated_sharpe_in_sample']), '']
    L += ['## 6. Winner\'s curse: model edge vs realized edge on the fills won [winners_curse]', '',
          '| variant | won | mean q | mean fair | model edge / contract | realized edge / contract | incumbent edge on same requests | realized / capital | hit rate |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in A['winners_curse'].items():
        L.append('| %s | %d | %.4f | %.4f | %+.4f | %+.4f | %+.4f | %s | %.4f |' % (k, v['won'], v['mean_q'], v['mean_fair'], v['model_edge_per_contract'],
                                                                         v['realized_edge_per_contract'], v['incumbent_edge_per_contract_same_fills'],
                                                                         _pct(v['realized_return_on_capital_per_fill'], 2), v['hit_rate']))
    cp, tl = A['capacity'], A['tail']
    L += ['', '## 7. Capacity, dollars and the tail of the chosen variant (test period) [capacity, tail, censoring_check]', '',
          '| item | value |', '|---|---|',
          '| share of the cell\'s YES premium won / of all incumbent NO flow / of cell requests | %s / %s / %s |' % (_pct(cp['share_won_of_cell_premium']), _pct(cp['share_won_of_all_no_flow_premium']), _pct(cp['share_won_of_cell_count'])),
          '| premium sold $/day; P&L $/day / $/yr | %s; %s / %s |' % (_usd(cp['premium_sold_usd_per_day']), _usd(cp['pnl_usd_per_day']), _usd(cp['pnl_usd_per_year'])),
          '| excess over SSR on peak, 95%% interval from the payout sd | %s to %s |' % (_usd(cp['excess_ci95_usd_per_year'][0]), _usd(cp['excess_ci95_usd_per_year'][1])),
          '| capital: average / peak outstanding (1 − q) | %s / %s |' % (_usd(cp['capital_avg_usd']), _usd(cp['capital_peak_usd'])),
          '| excess over SSR on peak / on average capital, $/yr | %s / %s |' % (_usd(cp['excess_over_ssr_on_peak_usd_per_year']), _usd(cp['excess_over_ssr_on_avg_usd_per_year'])),
          '| whole-flow excess on peak (÷ 0.841) | %s |' % _usd(cp['whole_flow_excess_on_peak_usd_per_year']),
          '| yield on peak / average capital | %s / %s |' % (_pct(cp['yield_on_peak']), _pct(cp['yield_on_avg'])),
          '| worst day / worst week / best day (test) | %s / %s / %s |' % (_usd(tl['daily_pnl_out']['worst_day_usd']), _usd(tl['daily_pnl_out']['worst_week_usd']), _usd(tl['daily_pnl_out']['best_day_usd'])),
          '| losing days (test) | %d of %d |' % (tl['daily_pnl_out']['losing_days'], tl['daily_pnl_out']['days']),
          '| daily P&L quantiles (test) | %s |' % (', '.join('%s: %s' % (k, _usd(v)) for k, v in (tl['daily_pnl_out']['quantiles_usd'] or {}).items())),
          '| worst day / week (full) | %s / %s |' % (_usd(tl['daily_pnl_full']['worst_day_usd']), _usd(tl['daily_pnl_full']['worst_week_usd'])),
          '| 1%% daily-ruin buffer: empirical test / full / independent-outcome | %s / %s / %s |' % (_usd(tl['ruin_buffer_1pct_empirical_usd']), _usd(tl['ruin_buffer_1pct_empirical_full_usd']), _usd(tl['ruin_buffer_1pct_independent_usd'])),
          '| censoring check: test through %s: ann. return / HAC t | %s / %s |' % (A['censoring_check']['test_through'], _pct(A['censoring_check']['oos_ann_return']), _f(A['censoring_check']['oos_hac_t'])), '']
    g = A['go_rule']
    L += ['Go rule (family A, as pre-registered): ' + ', '.join('%s=%s' % kv for kv in g.items()), '']
    FB = A['family_capped']
    ctb = FB['protocol']['choose_then_test']
    L += ['## 7b. Family B: the same 36 variants, each fill capped at %s of notional per request [family_capped]' % _usd(FB['size_cap_usd']), '',
          '| variant | fills in / out | in-sample Sharpe | OOS ann. return | OOS HAC t | P&L in / out | count z in / out | payout z in / out |',
          '|---|---:|---:|---:|---:|---:|---:|---:|']
    for k, v in FB['variants'].items():
        L.append('| %s | %d / %d | %s | %s | %s | %s / %s | %s / %s | %s / %s |' % (
            k, v['fills_in'], v['fills_out'], _f(v['in_sample_sharpe']), _pct(v['oos_ann_return']), _f(v['oos_hac_t']),
            _usd(v['pnl_in_usd']), _usd(v['pnl_out_usd']), _f(v['count_z_in'].get('z')), _f(v['count_z_out'].get('z')),
            _f(v['payout_z_in'].get('z')), _f(v['payout_z_out'].get('z'))))
    cpb, tlb = FB['capacity'], FB['tail']
    L += ['', '| item | value |', '|---|---|',
          '| chosen | %s |' % ctb['chosen'],
          '| in-sample positive / Sharpe | %s / %s |' % (ctb['in_sample_positive'], _f(ctb['in_sample'].get('sharpe'))),
          '| out-of-sample ann. return / HAC t / rank | %s / %s / %d of %d |' % (_pct(ctb['out_of_sample'].get('ann_return')), _f(ctb['oos_t']), ctb['oos_rank'], ctb['n_variants']),
          '| BH survivors (positive, full sample) | %s |' % (', '.join(ctb['bh_survivors_positive']) or 'none'),
          '| P&L $/yr; capital avg / peak; excess over SSR on peak (95%% interval) | %s; %s / %s; %s (%s to %s) |' % (
              _usd(cpb['pnl_usd_per_year']), _usd(cpb['capital_avg_usd']), _usd(cpb['capital_peak_usd']), _usd(cpb['excess_over_ssr_on_peak_usd_per_year']),
              _usd(cpb['excess_ci95_usd_per_year'][0]), _usd(cpb['excess_ci95_usd_per_year'][1])),
          '| share of cell premium won; premium sold $/day | %s; %s |' % (_pct(cpb['share_won_of_cell_premium']), _usd(cpb['premium_sold_usd_per_day'])),
          '| worst day / worst week (test); 1%% ruin buffer empirical / independent | %s / %s; %s / %s |' % (
              _usd(tlb['daily_pnl_out']['worst_day_usd']), _usd(tlb['daily_pnl_out']['worst_week_usd']),
              _usd(tlb['ruin_buffer_1pct_empirical_usd']), _usd(tlb['ruin_buffer_1pct_independent_usd'])),
          '| censoring check through %s: ann. return / HAC t | %s / %s |' % (FB['censoring_check']['test_through'], _pct(FB['censoring_check']['oos_ann_return']), _f(FB['censoring_check']['oos_hac_t'])),
          '', 'Go rule (family B, descriptive): ' + ', '.join('%s=%s' % kv for kv in FB['go_rule'].items()), '',
          'Variants evaluated: %(family_A_full_size)d (A) + %(family_B_capped)d (B) = %(total_evaluated)d; none dropped. [variant_count]' % A['variant_count'], '']
    D = A['descriptive_cross7']
    dv, dc, dt_ = D['variant_stats'], D['capacity'], D['tail']
    L += ['## 7c. Descriptive only: %s, the strongest full-sample BH survivor (not the in-sample choice) [descriptive_cross7]' % D['variant'], '',
          '| item | value |', '|---|---|',
          '| fills in / out; in-sample Sharpe / t; OOS HAC t | %d / %d; %s / %s; %s |' % (dv['fills_in'], dv['fills_out'], _f(dv['in_sample_sharpe']), _f(dv['in_sample_hac_t']), _f(dv['oos_hac_t'])),
          '| payout-count z in / out (realized vs expected at the quote) | %s (%.1f vs %.1f) / %s (%.1f vs %.1f) |' % (_f(dv['count_z_in']['z'], 3), dv['count_z_in']['realized'], dv['count_z_in']['expected_at_quote'], _f(dv['count_z_out']['z'], 4), dv['count_z_out']['realized'], dv['count_z_out']['expected_at_quote']),
          '| dollar payout z in / out; expected payouts at fair in / out | %s / %s; %.1f / %.1f |' % (_f(dv['payout_z_in']['z']), _f(dv['payout_z_out']['z']), dv['payout_z_in']['expected_payouts'], dv['payout_z_out']['expected_payouts']),
          '| share of the cell\'s requests / premium won; of all incumbent NO premium | %s / %s; %s |' % (_pct(dc['share_won_of_cell_count']), _pct(dc['share_won_of_cell_premium']), _pct(dc['share_won_of_all_no_flow_premium'], 2)),
          '| premium sold $/day; P&L $/day / $/yr | %s; %s / %s |' % (_usd(dc['premium_sold_usd_per_day']), _usd(dc['pnl_usd_per_day']), _usd(dc['pnl_usd_per_year'])),
          '| capital average / peak; excess over SSR on peak (95%% interval) | %s / %s; %s (%s to %s) |' % (_usd(dc['capital_avg_usd']), _usd(dc['capital_peak_usd']), _usd(dc['excess_over_ssr_on_peak_usd_per_year']), _usd(dc['excess_ci95_usd_per_year'][0]), _usd(dc['excess_ci95_usd_per_year'][1])),
          '| worst day / worst week / losing days (test); 1%% ruin buffer empirical / independent | %s / %s / %d of %d; %s / %s |' % (_usd(dt_['daily_pnl_out']['worst_day_usd']), _usd(dt_['daily_pnl_out']['worst_week_usd']), dt_['daily_pnl_out']['losing_days'], dt_['daily_pnl_out']['days'], _usd(dt_['ruin_buffer_1pct_empirical_usd']), _usd(dt_['ruin_buffer_1pct_independent_usd'])),
          '| test through %s: HAC t | %s |' % (D['censoring_check']['test_through'], _f(D['censoring_check']['oos_hac_t'])), '',
          '## 8. Feasibility (docs.polymarket.com/trading/combos/market-makers, read 2026-10-14)', '', '| item | fact |', '|---|---|']
    for k, v in FEASIBILITY:
        L.append('| %s | %s |' % (k, v))
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    return 0


# ------------------------------------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample'); s.set_defaults(fn=cmd_sample)
    s.add_argument('--out', required=True)
    s.add_argument('--n', type=int, default=32000)
    s.add_argument('--floor', type=int, default=12)
    lg = sub.add_parser('legs'); lg.set_defaults(fn=cmd_legs)
    lg.add_argument('--out', required=True)
    lg.add_argument('--interval', type=float, default=0.2)
    lg.add_argument('--workers', type=int, default=4)
    an = sub.add_parser('analyze'); an.set_defaults(fn=lambda a: cmd_analyze(a))
    an.add_argument('--out', required=True)
    rn = sub.add_parser('render'); rn.set_defaults(fn=lambda a: cmd_render(a))
    rn.add_argument('--out', required=True)
    args = p.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == '__main__':
    main()
