#!/usr/bin/env python3
"""Which chains are busy, which of them can be traded on, and what is new there: the census and the probe joined into
one ranked list, a set of new-activity detectors, a cross-source verification, and a report — as one loop member.

The question this answers. "Detect new activity on chains where it is reasonable to trade" has two halves, and the
second one is easy to drop. *New activity* is a deviation from a chain's own history: a day or a week of transactions,
DEX volume, fees or stablecoin float well outside what the same chain did over the previous four weeks, judged against
how often that chain has produced a deviation that large before (an empirical null, not a fixed threshold — a chain
whose volume doubles every other week is not news when it doubles again). *Reasonable to trade* is a property of the
chain's liquidity, measured, not assumed: `chain_census.tier_of` puts every chain in deep / tradeable / token_only /
thin / inactive from its DEX volume, stablecoin float and the liquidity of its own token on and off chain, and every
hit carries that block so a surge on a chain with $40k a day of DEX volume reads as what it is.

Detectors (each emits the repo's `Hit` shape, keyed by the persistent thing so `findings.py ingest --chain chains`
folds repeat observations into one finding):

    chain_surge          a metric's last day (and last week) against its trailing 28 days, with the empirical
                         exceedance rate of that ratio over the chain's own history
    chain_drop           the same, downwards, for the activity that is leaving (info)
    chain_new            a chain whose first non-zero day in any aggregator series is within the last 60 days
    stable_inflow        stablecoin float arriving on a chain, in total and per stablecoin (which dollar, where)
    dex_share_shift      a chain's share of all on-chain DEX volume rising against its four-week share
    activity_divergence  transactions surging with no value behind them (bots, farming, spam), or value surging
                         without transactions (fewer, larger hands)
    unregistered_active  a deep or tradeable chain the probe registry does not cover yet
    probe_new_asset      an asset carrying real value on a chain where the previous probe did not see it
    probe_tx_surge       the probe's own transaction count against its previous readings

    uv run python scripts/chain_activity.py analyze --out research/2026-10-09/chains
    uv run python scripts/chain_activity.py detect  --out research/2026-10-09/chains
    uv run python scripts/chain_activity.py verify  --out research/2026-10-09/chains
    uv run python scripts/chain_activity.py render  --out research/2026-10-09/chains
    uv run --with pycryptodome python scripts/chain_activity.py run [--out ...] [--skip-probe] [--samples N]
"""
import argparse
import collections
import datetime as dt
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from detectors import Hit  # noqa: E402
from chain_census import load_census  # noqa: E402

SERIES = ROOT / 'research' / 'chains' / 'series.jsonl'
LOG = ROOT / 'research' / 'chains_daily_log.md'
REGISTRY = ROOT / 'scripts' / 'chain_registry.json'

# --- thresholds -------------------------------------------------------------------------------------------------------
BASE_DAYS = 28                 # trailing baseline for a surge
HISTORY_DAYS = 150             # how far back the empirical null looks
MIN_HISTORY = 21               # a series needs this many baseline-able days before it can surge
D1_MIN_RATIO, D7_MIN_RATIO = 2.0, 1.5
DROP_MAX_RATIO = 0.5
MAX_P = 0.05                   # the surge must be rarer than one day in twenty for this chain
HIGH_RATIO, HIGH_P = 3.0, 0.02
FLOORS = {'dex': 1e6, 'fees': 2e4, 'tx': 25_000, 'daa': 5_000, 'tvl': 10e6}   # absolute rise over the baseline, per day
METRICS = (('dex', 'dex', True), ('fees', 'fees', True), ('tx', 'tx', False), ('daa', None, False), ('tvl', 'tvl', True))
NEW_CHAIN_DAYS = 60
STABLE_7D_MIN_USD, STABLE_7D_MIN_SHARE = 25e6, 0.10
STABLE_ASSET_MIN_USD, STABLE_ASSET_MIN_SHARE = 20e6, 0.25
NEW_STABLE_MIN_USD = 10e6
SHARE_MIN, SHARE_MIN_RATIO = 0.005, 1.5
DIVERGE_UP, DIVERGE_FLAT = 1.5, 1.1
SPIKE_SHARE = 0.5              # a week whose excess comes more than half from one day is a spike, not a level
MARKET_EXCESS = 1.5            # a surge within x1.5 of the cross-chain median move that day is the market, not news
STABLE_30D_MIN_USD, STABLE_30D_MIN_SHARE = 50e6, 0.30
PROBE_NEW_ASSET_MIN_USD = 5e6  # an asset must carry this much a day (estimated) on the probe to be "new value"
TRADEABLE = ('deep', 'tradeable')


def utc_now():
    return dt.datetime.now(dt.timezone.utc)


def load_json(p, default=None):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else default


def m(v, dollar=True):
    if v is None:
        return '-'
    v = float(v)
    for u, d in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(v) >= d:
            return ('$' if dollar else '') + '%.1f%s' % (v / d, u)
    return ('$' if dollar else '') + ('%.0f' % v)


# ---------------------------------------------------------------------------------------------- statistics

def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def surge_stats(daily, recent=1, base_days=BASE_DAYS, history=HISTORY_DAYS, weekday=True, min_history=MIN_HISTORY):
    """A metric's recent level against its trailing baseline, and how unusual that ratio is for this series.

    daily: {YYYY-MM-DD: value}, complete days only, sorted or not. recent=1 compares the last day with the median of
    the `base_days` before it — and, when `weekday`, also with the median of the same weekday over those weeks, keeping
    the smaller ratio, so a Monday after a quiet weekend is not a surge; recent=7 compares the last week's mean with the
    mean of the `base_days` before it. The empirical p is (k+1)/(n+1), k the number of earlier days in the last
    `history` whose same statistic was at least as large. Returns None when the series is too short.
    """
    days = sorted(daily)
    vals = [float(daily[d] or 0) for d in days]
    if len(vals) < recent + max(base_days // 2, min_history):
        return None

    def at(i):
        if i - recent + 1 < 0:
            return None
        rec = vals[i - recent + 1:i + 1]
        base = vals[max(0, i - recent - base_days + 1):i - recent + 1]
        if len(base) < min_history:
            return None
        r = _mean(rec)
        b = statistics.median(base) if recent == 1 else _mean(base)
        ratio = (r / b) if b > 0 else (math.inf if r > 0 else 1.0)
        if recent == 1 and weekday:
            same = [base[j] for j in range(len(base) - 7, -1, -7)]   # same weekday, going back a week at a time
            bw = statistics.median(same) if same else None
            if bw and bw > 0:
                ratio = min(ratio, r / bw)
        return r, b, ratio, len(base)

    cur = at(len(vals) - 1)
    if cur is None:
        return None
    r, b, ratio, n_base = cur
    rec = vals[-recent:]
    excess = [max(0.0, x - b) for x in rec]
    lo = max(0, len(vals) - 1 - history)
    hist = [x[2] for x in (at(i) for i in range(lo, len(vals) - 1)) if x is not None]
    k_up = sum(1 for h in hist if h >= ratio)
    k_dn = sum(1 for h in hist if h <= ratio)
    return {'recent': r, 'base': b, 'ratio': ratio, 'delta': r - b, 'n_base': n_base, 'p_up': (k_up + 1) / (len(hist) + 1),
            'p_down': (k_dn + 1) / (len(hist) + 1), 'n_hist': len(hist), 'last_day': days[-1], 'recent_days': recent,
            # how much of a week's excess one day carries: a week lifted by a single-day print (an adapter artifact
            # or one block trade) reads very differently from a week that is uniformly higher
            'max_day_excess_share': (max(excess) / sum(excess)) if recent > 1 and sum(excess) > 0 else None,
            'days_above_2x': sum(1 for x in rec if b > 0 and x >= 2 * b) if recent > 1 else None}


def first_nonzero(daily):
    for d in sorted(daily):
        if (daily[d] or 0) > 0:
            return d
    return None


def days_between(a, b):
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


# ---------------------------------------------------------------------------------------------- analyze

def tradeability(r):
    n = r.get('now') or {}
    return {'tier': r.get('tier'), 'dex_7d_avg': n.get('dex_7d_avg') or n.get('dex_24h'), 'stables': n.get('stables'),
            'tvl': n.get('tvl'), 'native_volume_24h': n.get('native_volume_24h'), 'perp_volume_24h': n.get('perp_volume_24h'),
            'perp_coin': n.get('perp_coin')}


def cmd_analyze(args):
    out = Path(args.out)
    C = load_census(out)
    if not C:
        raise SystemExit('no census.json in %s — run chain_census.py fetch + build first' % out)
    P = load_json(out / 'probe.json', {'meta': None, 'chains': {}})
    reg = load_json(REGISTRY)
    families = {c['slug']: c.get('family') for c in reg['chains']}

    rows = []
    for name, r in C['chains'].items():
        n = r['now']
        row = {'name': name, 'slug': r.get('slug'), 'family': r.get('family'), 'layer': r.get('layer'),
               'tier': r['tier'], 'score': r['activity']['score'], 'n_axes': r['activity']['n_axes'],
               'dex_7d_avg': n.get('dex_7d_avg') or n.get('dex_24h'), 'stables': n.get('stables'), 'tvl': n.get('tvl'),
               'fees_7d_avg': n.get('fees_7d_avg') or n.get('fees_24h'), 'tx_7d_avg': n.get('tx_7d_avg'),
               'tx_source': n.get('tx_source'), 'native_volume_24h': n.get('native_volume_24h'),
               'perp_volume_24h': n.get('perp_volume_24h'), 'perp_coin': n.get('perp_coin'),
               'first_seen': n.get('first_seen'), 'sources': r.get('sources')}
        pr = (P.get('chains') or {}).get(r.get('slug')) if r.get('slug') else None
        if pr and pr.get('ok'):
            row.update(probe_fields(pr))
            day = calendar_day(pr.get('window') or {})
            if day and (r.get('series') or {}).get('tx', {}).get(day) is not None:
                row['tx_probe_day_aggregator'] = r['series']['tx'][day]
        rows.append(row)
    # probe-only chains (no census row under the registry name — e.g. HyperCore, Bitcoin Cash)
    named = {r['slug'] for r in rows if r.get('slug')}
    for slug, pr in (P.get('chains') or {}).items():
        if slug in named or not pr.get('ok'):
            continue
        row = {'name': pr.get('name') or slug, 'slug': slug, 'family': families.get(slug), 'tier': None, 'score': None}
        row.update(probe_fields(pr))
        rows.append(row)

    ranked = sorted([r for r in rows if r.get('score') is not None], key=lambda r: -r['score'])
    for i, r in enumerate(ranked):
        r['rank'] = i + 1
    probe_rank = sorted([r for r in rows if r.get('probe_tx') is not None], key=lambda r: -(r['probe_tx'] or 0))
    A = {'generated_utc': utc_now().isoformat(timespec='seconds'),
         'window': window_of(C, P), 'census_today': C.get('today'),
         'provenance': {'census_generated': C.get('generated_utc'), 'registry_sha': C.get('registry_sha'),
                        'probe_registry_sha': (P.get('meta') or {}).get('registry_sha'),
                        'probe_window': (P.get('meta') or {}).get('window')},
         'tiers': C.get('tiers'), 'n_chains': C.get('n_chains'),
         'ranked': ranked, 'probe_ranked': [r['slug'] for r in probe_rank],
         'unranked_probe_only': [r for r in rows if r.get('score') is None and r.get('probe_tx') is not None],
         'families': dict(collections.Counter((r.get('family') or 'unregistered') for r in ranked[:args.top])),
         'probe_failed': (P.get('meta') or {}).get('failed')}
    (out / 'analysis.json').write_text(json.dumps(A, indent=1, default=str))
    print(json.dumps({'ranked': len(ranked), 'probe_rows': len(probe_rank), 'tiers': C.get('tiers')}, indent=1))


def window_of(C, P):
    w = (P.get('meta') or {}).get('window') if P else None
    if w:
        return {'first_utc': w['start_utc'], 'last_utc': w['end_utc'], 'hours': w['hours'], 'kind': 'probe window'}
    today = C.get('today')
    d = dt.date.fromisoformat(today) - dt.timedelta(days=1)
    return {'first_utc': d.isoformat() + 'T00:00:00+00:00', 'last_utc': today + 'T00:00:00+00:00', 'hours': 24.0,
            'kind': 'census day'}


def probe_fields(pr):
    tx = pr.get('tx') or {}
    tr = pr.get('transfers') or {}
    hours = (pr.get('window') or {}).get('hours') or 24
    scale = 24.0 / hours if hours else 1.0
    top = [{'asset': a['asset'], 'symbol': a.get('symbol'), 'class': a.get('class'), 'usd': a.get('usd'),
            'usd_se': a.get('usd_se'), 'transfers': a.get('transfers'), 'top_block_share': a.get('top_block_share'),
            'price_source': a.get('price_source')}
           for a in (tr.get('assets') or [])[:12]]
    tv = tr.get('top_targets_by_value') or []
    tt = tr.get('top_targets_by_txs') or []
    ptx = (tx.get('count') * scale) if tx.get('count') is not None else None
    pusd = (tr.get('priced_usd') * scale) if tr.get('priced_usd') is not None else None
    meth = (tr.get('method') or '').lower()
    kind = 'traded' if 'venue' in meth else 'gross' if 'gross outputs' in meth or meth.startswith('aggregator') else 'net'
    return {'probe_tx': ptx, 'probe_value_kind': kind,
            'probe_usd_per_tx': (pusd / ptx) if (pusd is not None and ptx and kind == 'net') else None,
            'probe_top_target_value': tv[0] if tv else None, 'probe_top_target_txs': tt[0] if tt else None,
            'probe_tx_se': (tx.get('se') * scale) if tx.get('se') is not None else None,
            'probe_tx_method': tx.get('method'), 'probe_hours': hours,
            'probe_bookkeeping_share': (tx['bookkeeping'] / tx['count']) if tx.get('bookkeeping') is not None and tx.get('count') else None,
            'probe_transfer_usd': pusd,
            'probe_usd_by_class': {k: v * scale for k, v in (tr.get('usd_by_class') or {}).items()},
            'probe_top_assets': top, 'probe_unpriced_assets': tr.get('unpriced_assets'),
            'probe_cumulative': tx.get('cumulative_total'), 'probe_endpoint': pr.get('endpoint')}


# ---------------------------------------------------------------------------------------------- detectors

def market_ratios(stats, min_chains=8):
    """Cross-sectional median of the same statistic over every chain that has it, per (metric, window, last day).

    A sell-off lifts transactions, DEX volume and fees on every chain at once; that is the market, not news about
    any one chain. The median ratio across chains on the same day is the market's move, and a chain's surge is judged
    by its excess over it (`excess_ratio`), so 'new activity' means activity that is new *here*.
    """
    groups = collections.defaultdict(list)
    for (name, metric, recent), st in stats.items():
        if st and math.isfinite(st['ratio']):
            groups[(metric, recent, st['last_day'])].append(st['ratio'])
    return {k: statistics.median(v) for k, v in groups.items() if len(v) >= min_chains}


def det_surge(C, A):
    stats = {}
    for name, r in C['chains'].items():
        s = r.get('series') or {}
        for metric, skey, dollar in METRICS:
            series = s.get(skey or '') if skey else (s.get('daa_growthepie') or s.get('daa_tronscan') or s.get('daa_nearblocks'))
            if not series:
                continue
            for recent in (1, 7):
                stats[(name, metric, recent)] = surge_stats(series, recent=recent, weekday=(metric in ('tx', 'daa', 'dex', 'fees')))
    mkt = market_ratios(stats)
    dollars = {mt: d for mt, _, d in METRICS}
    hits = []
    for (name, metric, recent), st in stats.items():
        if not st:
            continue
        r = C['chains'][name]
        tier = r.get('tier')
        dollar = dollars[metric]
        min_ratio = D1_MIN_RATIO if recent == 1 else D7_MIN_RATIO
        floor = FLOORS[metric]
        market = mkt.get((metric, recent, st['last_day']))
        excess = (st['ratio'] / market) if market and math.isfinite(st['ratio']) else st['ratio']
        up = st['ratio'] >= min_ratio and st['p_up'] <= MAX_P and st['delta'] >= floor
        down = recent == 7 and st['ratio'] <= DROP_MAX_RATIO and st['p_down'] <= MAX_P and -st['delta'] >= floor
        if not (up or down):
            continue
        if metric == 'tvl' and up and recent == 1:
            continue   # one-day TVL moves are mostly price; the weekly view carries the signal
        tw = 'd%d' % recent
        st = dict(st, market_ratio=market, excess_ratio=excess)
        if up:
            spiky = recent > 1 and (st.get('max_day_excess_share') or 0) > SPIKE_SHARE
            marketwide = excess < MARKET_EXCESS
            sev = ('info' if marketwide else
                   'high' if tier in TRADEABLE and st['ratio'] >= HIGH_RATIO and st['p_up'] <= HIGH_P and not spiky else
                   'notable' if tier in TRADEABLE + ('token_only',) else 'info')
            title = '%s %s %s: %s/day vs %s baseline (x%.1f%s, rarer than %.0f%% of its days)%s' % (
                name, metric, 'last day' if recent == 1 else 'last 7 days', m(st['recent'], dollar),
                m(st['base'], dollar), st['ratio'], (', market x%.2f' % market) if market else '', 100 * st['p_up'],
                ('; one day carries %.0f%% of the excess' % (100 * st['max_day_excess_share'])) if spiky else '')
            hits.append(Hit(detector='chain_surge', key='%s:%s:%s' % (name, metric, tw), severity=sev,
                            usd=st['delta'] if dollar else None, title=title,
                            evidence={'chain': name, 'metric': metric, 'window': tw, **rnd(st),
                                      'series_source': r['now'].get('tx_source') if metric == 'tx' else 'defillama',
                                      'tradeability': tradeability(r)}))
        else:
            hits.append(Hit(detector='chain_drop', key='%s:%s' % (name, metric), severity='info',
                            usd=-st['delta'] if dollar else None,
                            title='%s %s fell to %s/day over the last week from %s (x%.2f)' % (
                                name, metric, m(st['recent'], dollar), m(st['base'], dollar), st['ratio']),
                            evidence={'chain': name, 'metric': metric, **rnd(st), 'tradeability': tradeability(r)}))
    return hits


def rnd(st):
    return {k: (round(v, 4) if isinstance(v, float) and math.isfinite(v) else v) for k, v in st.items()}


def det_new_chain(C, A):
    hits = []
    today = C['today']
    for name, r in C['chains'].items():
        s = r.get('series') or {}
        firsts = [first_nonzero(s[k]) for k in ('dex', 'stables', 'tx', 'tvl') if s.get(k)]
        firsts = [f for f in firsts if f]
        if not firsts:
            continue
        f = min(firsts)
        age = days_between(f, today)
        if age > NEW_CHAIN_DAYS:
            continue
        tier = r.get('tier')
        n = r['now']
        if tier == 'inactive' or (tier == 'thin' and (n.get('stables') or 0) < 10e6):
            continue
        sev = 'high' if tier in TRADEABLE else 'notable'
        hits.append(Hit(detector='chain_new', key=name, severity=sev, usd=n.get('stables') or n.get('tvl'),
                        title='%s first appears %s (%d days ago) and is already %s: DEX %s/day, stables %s, TVL %s' % (
                            name, f, age, tier, m(n.get('dex_7d_avg') or n.get('dex_24h')), m(n.get('stables')), m(n.get('tvl'))),
                        evidence={'chain': name, 'first_seen': f, 'age_days': age, 'tradeability': tradeability(r),
                                  'note': 'first non-zero day in any aggregator series; a chain new to DefiLlama can be '
                                          'older than its listing'}))
    return hits


def det_stable_inflow(C, A):
    hits = []
    for name, r in C['chains'].items():
        st = (r.get('series') or {}).get('stables') or {}
        tier = r.get('tier')
        vals = list(st.values())
        days = list(st.keys())
        fired = False
        if len(vals) >= 8:
            cur, wk = vals[-1], vals[-8]
            d = cur - wk
            if d >= max(STABLE_7D_MIN_USD, STABLE_7D_MIN_SHARE * wk):
                fired = True
                sev = 'high' if (tier in TRADEABLE and d >= max(100e6, 0.25 * wk)) else 'notable' if tier != 'inactive' else 'info'
                hits.append(Hit(detector='stable_inflow', key=name, severity=sev, usd=d,
                                title='%s stablecoin float +%s in 7 days (%s -> %s, +%.0f%%)' % (name, m(d), m(wk), m(cur), 100 * d / wk if wk else 0),
                                evidence={'chain': name, 'stables_now': cur, 'stables_7d_ago': wk, 'change': d,
                                          'by_asset': [{k: a[k] for k in ('symbol', 'usd', 'prev_week', 'prev_month')} for a in (r.get('stables_by_asset') or [])[:6]],
                                          'tradeability': tradeability(r)}))
        if not fired and len(vals) >= 31:
            # a step older than a week: the float that arrived over the month and stayed
            cur, mo = vals[-1], vals[-31]
            d = cur - mo
            if d >= max(STABLE_30D_MIN_USD, STABLE_30D_MIN_SHARE * mo):
                steps = sorted(((vals[i] - vals[i - 1], days[i]) for i in range(len(vals) - 30, len(vals))), reverse=True)[:3]
                sev = 'notable' if tier != 'inactive' else 'info'
                hits.append(Hit(detector='stable_inflow', key='%s:30d' % name, severity=sev, usd=d,
                                title='%s stablecoin float +%s in 30 days (%s -> %s, +%.0f%%); largest step %s on %s' % (
                                    name, m(d), m(mo), m(cur), 100 * d / mo if mo else 0, m(steps[0][0]), steps[0][1]),
                                evidence={'chain': name, 'stables_now': cur, 'stables_30d_ago': mo, 'change': d,
                                          'largest_daily_steps': [{'day': dd, 'usd': x} for x, dd in steps],
                                          'by_asset': [{k: a[k] for k in ('symbol', 'usd', 'prev_week', 'prev_month')} for a in (r.get('stables_by_asset') or [])[:6]],
                                          'tradeability': tradeability(r)}))
        for a in r.get('stables_by_asset') or []:
            if a.get('peg') and a['peg'] != 'peggedUSD':
                continue
            cur, wk, mo = a['usd'], a['prev_week'], a['prev_month']
            if mo is not None and mo < 1e6 and cur >= NEW_STABLE_MIN_USD:
                hits.append(Hit(detector='stable_inflow', key='%s:%s:new' % (name, a['symbol']), severity='notable' if tier != 'inactive' else 'info',
                                usd=cur, title='%s is new on %s: %s now, %s a month ago' % (a['symbol'], name, m(cur), m(mo)),
                                evidence={'chain': name, 'asset': a, 'tradeability': tradeability(r)}))
            elif wk is not None and cur - wk >= max(STABLE_ASSET_MIN_USD, STABLE_ASSET_MIN_SHARE * wk):
                hits.append(Hit(detector='stable_inflow', key='%s:%s' % (name, a['symbol']), severity='notable' if tier in TRADEABLE else 'info',
                                usd=cur - wk, title='%s on %s +%s in 7 days (%s -> %s)' % (a['symbol'], name, m(cur - wk), m(wk), m(cur)),
                                evidence={'chain': name, 'asset': a, 'tradeability': tradeability(r)}))
    return hits


def det_share_shift(C, A):
    """A chain's share of all DEX volume, last 7 days against the 28 before."""
    total = collections.Counter()
    per = {}
    for name, r in C['chains'].items():
        d = (r.get('series') or {}).get('dex') or {}
        if d:
            per[name] = d
            for k, v in d.items():
                total[k] += v
    days = sorted(total)
    if len(days) < 35:
        return []
    rec, base = days[-7:], days[-35:-7]
    T_rec, T_base = sum(total[d] for d in rec), sum(total[d] for d in base)
    hits = []
    for name, d in per.items():
        s_rec = sum(d.get(x, 0) for x in rec) / T_rec if T_rec else 0
        s_base = sum(d.get(x, 0) for x in base) / T_base if T_base else 0
        if s_rec >= SHARE_MIN and s_base > 0 and s_rec / s_base >= SHARE_MIN_RATIO:
            r = C['chains'][name]
            hits.append(Hit(detector='dex_share_shift', key=name, severity='notable' if r.get('tier') in TRADEABLE else 'info',
                            usd=sum(d.get(x, 0) for x in rec) / 7,
                            title='%s took %.2f%% of all DEX volume this week, from %.2f%% over the four weeks before (x%.1f)' % (
                                name, 100 * s_rec, 100 * s_base, s_rec / s_base),
                            evidence={'chain': name, 'share_7d': s_rec, 'share_prior_28d': s_base, 'all_chains_dex_7d': T_rec,
                                      'tradeability': tradeability(r)}))
    return hits


def det_divergence(C, A):
    hits = []
    for name, r in C['chains'].items():
        s = r.get('series') or {}
        if not s.get('tx') or not s.get('dex'):
            continue
        t = surge_stats(s['tx'], recent=7)
        d = surge_stats(s['dex'], recent=7)
        if not t or not d:
            continue
        if t['ratio'] >= DIVERGE_UP and d['ratio'] <= DIVERGE_FLAT and t['delta'] >= FLOORS['tx']:
            kind, sev = 'activity_without_value', 'info'
        elif d['ratio'] >= DIVERGE_UP and t['ratio'] <= DIVERGE_FLAT and d['delta'] >= FLOORS['dex']:
            kind, sev = 'value_without_activity', 'notable' if r.get('tier') in TRADEABLE else 'info'
        else:
            continue
        hits.append(Hit(detector='activity_divergence', key='%s:%s' % (name, kind), severity=sev,
                        usd=d['delta'] if kind == 'value_without_activity' else None,
                        title='%s %s: transactions x%.2f, DEX volume x%.2f (last 7 days vs 28 before)' % (
                            name, kind.replace('_', ' '), t['ratio'], d['ratio']),
                        evidence={'chain': name, 'kind': kind, 'tx': rnd(t), 'dex': rnd(d), 'tradeability': tradeability(r),
                                  'reading': ('more transactions with no more value is bots, farming, spam or a points '
                                              'campaign' if kind == 'activity_without_value' else
                                              'more value through no more transactions is fewer, larger hands: a market '
                                              'maker, a fund, or one integrator routing size')}))
    return hits


def det_unregistered(C, A):
    hits = []
    for name, r in C['chains'].items():
        if r.get('slug') or r.get('tier') not in TRADEABLE:
            continue
        n = r['now']
        hits.append(Hit(detector='unregistered_active', key=name, severity='info', usd=n.get('dex_7d_avg') or n.get('dex_24h'),
                        title='%s is %s (DEX %s/day, stables %s) and has no probe in chain_registry.json' % (
                            name, r['tier'], m(n.get('dex_7d_avg') or n.get('dex_24h')), m(n.get('stables'))),
                        evidence={'chain': name, 'tradeability': tradeability(r), 'llama_key': r.get('llama_key'),
                                  'evm_chain_id': r.get('evm_chain_id')}))
    return hits


def load_series(exclude_window=None):
    rows = []
    if SERIES.exists():
        for line in SERIES.read_text().splitlines():
            if line.strip():
                x = json.loads(line)
                if exclude_window and x.get('window_end') == exclude_window:
                    continue
                rows.append(x)
    return rows


TX_HISTORY = ROOT / 'research' / 'chains' / 'tx_history.jsonl'
PROBE_BASE_DAYS, PROBE_MIN_HISTORY = 14, 7


def load_tx_history():
    """{chain slug: {YYYY-MM-DD: transactions}} from the probe's daily backfill and its own calendar-day readings."""
    out = collections.defaultdict(dict)
    if TX_HISTORY.exists():
        for line in TX_HISTORY.read_text().splitlines():
            if line.strip():
                x = json.loads(line)
                # a zero day from a chain that is never empty is a failed read, not a quiet day
                if x.get('ok') and x.get('count') is not None and x['count'] > 0:
                    out[x['chain']][x['day']] = float(x['count'])
    return out


def det_probe_history(C, A):
    """Transactions per day as the chain itself reports them, against the chain's own last two weeks.

    This is the detector for every chain the aggregators cannot count (BSC, Avalanche, Monad, HyperEVM, Sui, Aptos,
    Cardano, Stellar, XRPL, Hedera, Algorand, Bitcoin, ...): the backfill gives each a baseline on the day it is first
    probed, so a chain whose transactions go from 34k to 540k in two days is caught that week, not after a month.
    """
    H = load_tx_history()
    by_slug = {r.get('slug'): r for r in C['chains'].values() if r.get('slug')}
    stats = {slug: surge_stats(daily, recent=1, base_days=PROBE_BASE_DAYS, weekday=False, min_history=PROBE_MIN_HISTORY)
             for slug, daily in H.items()}
    mkt = market_ratios({(slug, 'tx', 1): st for slug, st in stats.items()}, min_chains=6)
    hits = []
    for slug, daily in H.items():
        st = stats[slug]
        if not st:
            continue
        r = by_slug.get(slug) or {}
        tier = r.get('tier')
        market = mkt.get(('tx', 1, st['last_day']))
        excess = (st['ratio'] / market) if market else st['ratio']
        st = dict(st, market_ratio=market, excess_ratio=excess)
        up = st['ratio'] >= D1_MIN_RATIO and st['delta'] >= FLOORS['tx'] and st['p_up'] <= max(MAX_P, 1.0 / (st['n_hist'] + 1))
        down = st['ratio'] <= DROP_MAX_RATIO and -st['delta'] >= FLOORS['tx']
        if not (up or down):
            continue
        prev = sorted(daily)[-4:-1]
        trail = ', '.join('%s %s' % (d[5:], m(daily[d], False)) for d in prev)
        if up:
            sev = ('info' if excess < MARKET_EXCESS else
                   'high' if tier in TRADEABLE and st['ratio'] >= HIGH_RATIO else
                   'notable' if tier in TRADEABLE + ('token_only',) else 'info')
            title = '%s transactions %s on %s vs a %s median over the %d days before (x%.1f%s; %s)' % (
                r.get('name') or slug, m(st['recent'], False), st['last_day'], m(st['base'], False),
                st['n_base'], st['ratio'],
                (', market x%.2f' % market) if market else '', trail)
            det = 'probe_tx_surge'
        else:
            sev, det = 'info', 'probe_tx_drop'
            title = '%s transactions fell to %s on %s from a %s median (x%.2f)' % (
                r.get('name') or slug, m(st['recent'], False), st['last_day'], m(st['base'], False), st['ratio'])
        hits.append(Hit(detector=det, key=slug, severity=sev, title=title,
                        evidence={'chain': slug, **rnd(st), 'days': {d: daily[d] for d in sorted(daily)[-15:]},
                                  'tradeability': tradeability(r) if r else None,
                                  'note': 'empirical p is limited by %d days of history' % st['n_hist']}))
    return hits


def det_probe(C, A, P):
    """Probe-on-probe: new assets with value, and transaction counts against previous probe readings."""
    if not P or not P.get('chains'):
        return []
    end = ((P.get('meta') or {}).get('window') or {}).get('end_utc')
    prev = collections.defaultdict(list)
    for x in load_series(exclude_window=end):
        prev[x['chain']].append(x)
    hits = []
    for slug, pr in P['chains'].items():
        if not pr.get('ok'):
            continue
        hist = sorted(prev.get(slug) or [], key=lambda x: x.get('window_end') or '')
        if not hist:
            continue
        fields = probe_fields(pr)
        seen = {a['asset'] for h in hist[-5:] for a in (h.get('assets') or [])}
        for a in fields['probe_top_assets']:
            usd = a.get('usd') or 0
            if usd < PROBE_NEW_ASSET_MIN_USD or a['asset'] in seen or str(a['asset']).startswith('native:'):
                continue
            if (a.get('top_block_share') or 0) > 0.5:
                continue   # one block scaled up is one transfer, not a flow
            hits.append(Hit(detector='probe_new_asset', key='%s:%s' % (slug, a['asset']), severity='notable', usd=usd,
                            title='%s on %s: %s/day of transfers, absent from the previous %d probe(s)' % (
                                a.get('symbol') or a['asset'][:12], slug, m(usd), min(5, len(hist))),
                            evidence={'chain': slug, 'asset': a, 'previous_windows': [h.get('window_end') for h in hist[-5:]]}))
    return hits


DETECTORS = [
    ('chain_surge', det_surge, 'a metric (DEX volume, fees, transactions, active addresses, TVL) against its trailing 28 days, empirical exceedance <= 5%'),
    ('chain_new', det_new_chain, 'first non-zero aggregator day within 60 days and already above the thin tier'),
    ('stable_inflow', det_stable_inflow, 'stablecoin float arriving on a chain, in total and per stablecoin'),
    ('dex_share_shift', det_share_shift, "a chain's share of all DEX volume up x1.5 against its four-week share"),
    ('activity_divergence', det_divergence, 'transactions and DEX volume moving apart over a week'),
    ('unregistered_active', det_unregistered, 'deep or tradeable chains with no direct probe yet'),
    ('probe_tx_surge', det_probe_history, "the chain's own daily transactions (probe + backfill) x2 against its previous 14 days"),
]


def cmd_detect(args):
    out = Path(args.out)
    C = load_census(out)
    A = load_json(out / 'analysis.json')
    P = load_json(out / 'probe.json')
    if not C or not A:
        raise SystemExit('run analyze first')
    hits, meta = [], []
    for name, fn, desc in DETECTORS:
        t0 = time.time()
        try:
            h = fn(C, A)
            err = None
        except Exception as e:
            h, err = [], '%s: %s' % (type(e).__name__, e)
        hits += h
        meta.append({'detector': name, 'hits': len(h), 'seconds': round(time.time() - t0, 3), 'error': err, 'description': desc})
    t0 = time.time()
    try:
        ph = det_probe(C, A, P)
        perr = None
    except Exception as e:
        ph, perr = [], '%s: %s' % (type(e).__name__, e)
    hits += ph
    meta.append({'detector': 'probe_new_asset', 'hits': len(ph), 'seconds': round(time.time() - t0, 3),
                 'error': perr if P else 'no probe.json',
                 'description': 'an asset carrying >= $5M/day on the probe that the previous probes did not see'})
    order = {'high': 0, 'notable': 1, 'info': 2}
    hits.sort(key=lambda h: (order.get(h.severity, 3), -(abs(h.usd) if h.usd else 0)))
    D = {'window': str(out), 'analysis_window': A.get('window'), 'detectors': meta, 'hits': [h.as_dict() for h in hits],
         'params': {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, tuple, dict)) and k not in ('METRICS',)}}
    (out / 'detectors.json').write_text(json.dumps(D, indent=1, default=str))
    L = ['# New-activity sweep — %s' % out, '',
         'Ran %d detectors; %d hit(s): %s.' % (len(meta), len(hits), ', '.join('%d %s' % (c, s) for s, c in
                                                                             sorted(collections.Counter(h.severity for h in hits).items(), key=lambda kv: order[kv[0]]))),
         '', '| detector | hits | what it looks for |', '|---|---:|---|']
    for x in meta:
        L.append('| `%s` | %d | %s%s |' % (x['detector'], x['hits'], x['description'], (' — **error** ' + x['error']) if x['error'] and x['detector'] != 'probe_new_asset' else ''))
    L.append('')
    for h in hits:
        if h.severity == 'info' and not args.all:
            continue
        L += ['### [%s] %s' % (h.severity, h.title), '', '`%s`' % h.identity(), '']
    if not args.all:
        L += ['', '%d info-level hits omitted (`--all` lists them).' % sum(1 for h in hits if h.severity == 'info')]
    (out / 'detectors.md').write_text('\n'.join(L) + '\n')
    for h in hits:
        if h.severity != 'info':
            print('[%-7s] %s' % (h.severity, h.title))
    print('wrote %s (%d hits)' % (out / 'detectors.json', len(hits)))


# ---------------------------------------------------------------------------------------------- verify

def cmd_verify(args):
    """Two readings of the same quantity, held against each other.

    tx-cross-source   the probe's transactions/day against every aggregator's figure for the same chain
    dex-breakdown     DefiLlama's per-chain breakdown summed against its own all-chain total
    llama-keys        inferred internal chain keys that two single-chain protocols disagree on
    registry-ids      registry identities that do not resolve to a census row
    solana-two-paths  the per-minute counter against the stratified block estimate, same window
    """
    out = Path(args.out)
    C, P = load_census(out), load_json(out / 'probe.json', {})
    checks = []

    def add(cid, ok, detail, kind='numeric'):
        checks.append({'id': cid, 'ok': bool(ok), 'kind': kind, 'detail': detail})

    by_slug = {r.get('slug'): r for r in C['chains'].values() if r.get('slug')}
    rows = []
    for slug, pr in (P.get('chains') or {}).items():
        if not pr.get('ok') or not (pr.get('tx') or {}).get('count'):
            continue
        f = probe_fields(pr)
        r = by_slug.get(slug)
        refs = {}
        win = pr.get('window') or {}
        day = calendar_day(win)
        if r:
            s = r.get('series') or {}
            for src in ('tx_growthepie', 'tx_l2beat', 'tx_tronscan', 'tx_nearblocks'):
                if not s.get(src):
                    continue
                if day:
                    # the probe read exactly one UTC day: compare with the aggregator's figure for that day, or not at all
                    if day in s[src]:
                        refs[src.replace('tx_', '')] = s[src][day]
                else:
                    v = overlap_mean(s[src], win)
                    if v is not None:
                        refs[src.replace('tx_', '') + ' (overlap)'] = v
            if r['now'].get('tx_24h_blockchair') and not day:
                refs['blockchair-24h'] = r['now']['tx_24h_blockchair']
        for src, ref in refs.items():
            if not ref:
                continue
            ratio = f['probe_tx'] / ref
            rows.append({'chain': slug, 'source': src, 'probe_per_day': f['probe_tx'], 'probe_se': f['probe_tx_se'],
                         'reference_per_day': ref, 'ratio': ratio, 'method': f['probe_tx_method']})
    tol = args.tolerance
    for x in rows:
        add('tx-cross-source:%s:%s' % (x['chain'], x['source']), abs(math.log(x['ratio'])) <= math.log(1 + tol),
            'probe %s/day (%s) vs %s %s/day: x%.3f' % (m(x['probe_per_day'], False), x['method'], x['source'],
                                                     m(x['reference_per_day'], False), x['ratio']))
    dexs = None
    rawp = out / 'raw' / 'llama_dexs.json.gz'
    if rawp.exists():
        import gzip
        with gzip.open(rawp, 'rt') as fh:
            dexs = json.load(fh)
        tot = sum(r['now'].get('dex_24h') or 0 for r in C['chains'].values())
        ref = dexs.get('total24h') or 0
        add('dex-breakdown', ref and abs(tot / ref - 1) <= 0.02, 'sum of per-chain 24h %s vs DefiLlama total24h %s (x%.4f)' % (m(tot), m(ref), (tot / ref) if ref else 0))
    contested = {k: v for k, v in (C.get('llama_keys') or {}).items() if v.get('contested')}
    add('llama-keys', len(contested) <= 5, '%d contested of %d inferred keys: %s' % (len(contested), len(C.get('llama_keys') or {}), ', '.join(sorted(contested))[:300]), 'identity')
    add('registry-ids', not C.get('warnings'), '; '.join(C.get('warnings') or [])[:600] or 'all registry identities resolve', 'identity')
    sol = (P.get('chains') or {}).get('solana')
    if sol and sol.get('ok'):
        tx = sol['tx']
        if tx.get('from_blocks') and tx.get('method') == 'exact-counter':
            ratio = tx['from_blocks'] / tx['count']
            k = abs(tx['from_blocks'] - tx['count']) / (tx.get('from_blocks_se') or 1)
            add('solana-two-paths', k <= 3, 'block estimate %s ±%s vs counter %s: x%.3f, %.1f standard errors' % (
                m(tx['from_blocks'], False), m(tx.get('from_blocks_se'), False), m(tx['count'], False), ratio, k))
    V = {'generated_utc': utc_now().isoformat(timespec='seconds'), 'tolerance': tol,
         'passed': sum(1 for c in checks if c['ok']), 'failed': sum(1 for c in checks if not c['ok']),
         'checks': checks, 'tx_cross_source': rows}
    (out / 'verify.json').write_text(json.dumps(V, indent=1, default=str))
    for c in checks:
        print('%-4s %-40s %s' % ('ok' if c['ok'] else 'FAIL', c['id'][:40], c['detail'][:150]))
    print('%d passed, %d failed' % (V['passed'], V['failed']))
    return 0


def calendar_day(win):
    """YYYY-MM-DD when the window is exactly one UTC day, else None."""
    try:
        s, e = int(win['start_ts']), int(win['end_ts'])
    except (KeyError, TypeError, ValueError):
        return None
    if s % 86400 == 0 and e - s == 86400:
        return dt.datetime.fromtimestamp(s, dt.timezone.utc).strftime('%Y-%m-%d')
    return None


def overlap_mean(daily, win):
    """A daily series averaged over the days a trailing window overlaps, weighted by the overlap."""
    s, e = int(win['start_ts']), int(win['end_ts'])
    tot = wsum = 0.0
    d = s - s % 86400
    while d < e:
        key = dt.datetime.fromtimestamp(d, dt.timezone.utc).strftime('%Y-%m-%d')
        w = (min(e, d + 86400) - max(s, d)) / 86400.0
        if key in daily and w > 0:
            tot += w * daily[key]
            wsum += w
        d += 86400
    return (tot / wsum) if wsum >= 0.5 else None


# ---------------------------------------------------------------------------------------------- series

def cmd_series(args):
    """Append this window's probe readings to research/chains/series.jsonl (one line per chain; re-run replaces)."""
    out = Path(args.out)
    P = load_json(out / 'probe.json')
    if not P:
        print('no probe.json; nothing appended')
        return
    end = ((P.get('meta') or {}).get('window') or {}).get('end_utc')
    keep = [x for x in load_series() if not (x.get('window_end') == end and x.get('out') == str(out))]
    new = []
    for slug, pr in sorted((P.get('chains') or {}).items()):
        if not pr.get('ok'):
            continue
        f = probe_fields(pr)
        new.append({'chain': slug, 'out': str(out), 'window_end': end, 'hours': f['probe_hours'],
                    'tx_per_day': f['probe_tx'], 'tx_se': f['probe_tx_se'], 'tx_method': f['probe_tx_method'],
                    'cumulative_total': f['probe_cumulative'], 'transfer_usd_per_day': f['probe_transfer_usd'],
                    'usd_by_class': f['probe_usd_by_class'],
                    'assets': [{'asset': a['asset'], 'symbol': a['symbol'], 'usd': a['usd'], 'transfers': a['transfers']}
                               for a in ((pr.get('transfers') or {}).get('assets') or [])[:40]]})
    SERIES.parent.mkdir(parents=True, exist_ok=True)
    SERIES.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in keep + new))
    print('series: %d rows (+%d from %s)' % (len(keep) + len(new), len(new), end))
    day = calendar_day((P.get('meta') or {}).get('window') or {})
    if day:
        H = {}
        if TX_HISTORY.exists():
            for line in TX_HISTORY.read_text().splitlines():
                if line.strip():
                    x = json.loads(line)
                    H[(x['chain'], x['day'])] = x
        n = 0
        for slug, pr in (P.get('chains') or {}).items():
            tx = pr.get('tx') or {}
            if pr.get('ok') and tx.get('count') is not None:
                H[(slug, day)] = {'chain': slug, 'day': day, 'ok': True, 'count': tx['count'], 'se': tx.get('se'),
                                  'method': tx.get('method'), 'samples': tx.get('sampled'), 'error': None,
                                  'probed_at': pr.get('probed_at'), 'source': 'probe'}
                n += 1
        TX_HISTORY.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in sorted(H.values(), key=lambda x: (x['chain'], x['day']))))
        print('tx history: %d chain-day rows from this probe (%s)' % (n, day))


# ---------------------------------------------------------------------------------------------- render

def cmd_render(args):
    out = Path(args.out)
    C, A = load_census(out), load_json(out / 'analysis.json')
    D, V = load_json(out / 'detectors.json', {}), load_json(out / 'verify.json', {})
    P = load_json(out / 'probe.json', {})
    w = A['window']
    L = ['# Chain activity — %s' % (w.get('last_utc') or '')[:10], '',
         'Census of %d chains from DefiLlama, growthepie, L2Beat, Blockchair, Tronscan, NEARBlocks, CoinGecko and '
         'Hyperliquid (days before %s UTC are complete); direct probe of %d registry chains over %s → %s (%.1f h).' % (
             C['n_chains'], C['today'], len((P.get('meta') or {}).get('ok') or []), w['first_utc'], w['last_utc'], w['hours']),
         '', 'Tiers (how reasonable it is to trade there): ' + ', '.join('%s %d' % (k, v) for k, v in sorted((C.get('tiers') or {}).items(), key=lambda kv: ['deep', 'tradeable', 'token_only', 'thin', 'inactive'].index(kv[0]))) + '.', '']
    L += ['## The list: chains by activity', '',
          'Ranked by the mean percentile across DEX volume, fees, stablecoin float, TVL and transactions (at least three '
          'of the five measured). DEX, fees and transactions from the aggregators are 7-day daily averages, except where '
          'an aggregator has the probe\'s own day ("same day"); probe columns are the direct reading of one UTC day, with '
          'its standard error where it is a sample. Transfer value is net per transaction (see the probe docstring); `†` '
          'marks an asset whose estimate comes mostly from one sampled block, i.e. one large transfer scaled up.', '',
          '| # | chain | family | tier | DEX/day | stables | TVL | fees/day | tx/day (aggregator) | tx/day (probe) | transfers/day (probe) | top assets moved (probe) |',
          '|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
    def label(r):
        n, sl = r['name'], r.get('slug')
        key = lambda x: ''.join(ch for ch in x.lower() if ch.isalnum())
        return n if not sl or key(sl) in key(n) else '%s (%s)' % (n, sl)

    def asset_list(r, k=3):
        return ', '.join('%s %s%s' % (a.get('symbol') or a['asset'][:8], m(a.get('usd')), '†' if (a.get('top_block_share') or 0) > 0.5 else '')
                         for a in (r.get('probe_top_assets') or [])[:k])

    for r in A['ranked'][:args.top]:
        top = asset_list(r)
        ptx = ''
        if r.get('probe_tx') is not None:
            ptx = m(r['probe_tx'], False) + (' ±%s' % m(r['probe_tx_se'], False) if r.get('probe_tx_se') else '')
        L.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            r['rank'], label(r), r.get('family') or '', r['tier'], m(r.get('dex_7d_avg')), m(r.get('stables')),
            m(r.get('tvl')), m(r.get('fees_7d_avg')),
            (m(r['tx_probe_day_aggregator'], False) + ' (%s, same day)' % r.get('tx_source')) if r.get('tx_probe_day_aggregator') is not None else
            ((m(r.get('tx_7d_avg'), False) + (' (%s)' % r['tx_source'] if r.get('tx_source') else '')) if r.get('tx_7d_avg') else ''),
            ptx, (m(r.get('probe_transfer_usd')) + ('' if r.get('probe_value_kind') == 'net' else ' (%s)' % r.get('probe_value_kind'))) if r.get('probe_transfer_usd') is not None else '', top))
    po = A.get('unranked_probe_only') or []
    if po:
        L += ['', 'Probed but outside the aggregator ranking: ' + '; '.join('%s %s tx/day (%s)' % (r['name'], m(r.get('probe_tx'), False), r.get('probe_tx_method')) for r in po)]
    by_slug = {r.get('slug'): r for r in A['ranked'] + po if r.get('slug')}
    probed = [by_slug[s] for s in (A.get('probe_ranked') or []) if s in by_slug]
    if probed:
        L += ['', '## The list, measured directly: every probed chain by transactions', '',
              'One row per registry chain the probe read, busiest first. `$/tx` is net transfer value per transaction: '
              'a chain with millions of transactions and cents per transaction is busy with bots, not with money. '
              '`bookkeeping` is the share of transactions sent to registry-listed oracle, validator-signing or block-builder '
              'contracts — real transactions that are not activity (the headline keeps them, as L2Beat does). '
              '`top target` is the contract that received the largest share of transactions (and of value): one '
              'address carrying most of a chain is one actor, however large the totals.', '',
              '| chain | family | tier | tx/day | method | bookkeeping | net transfers/day | $/tx | top target by txs | top target by value |',
              '|---|---|---|---:|---|---:|---:|---:|---|---|']
        for r in probed:
            tt, tv = r.get('probe_top_target_txs'), r.get('probe_top_target_value')
            L.append('| %s | %s | %s | %s%s | %s | %s | %s | %s | %s | %s |' % (
                label(r), r.get('family') or '', r.get('tier') or '', m(r['probe_tx'], False),
                (' ±%s' % m(r['probe_tx_se'], False)) if r.get('probe_tx_se') else '', r.get('probe_tx_method') or '',
                ('%.0f%%' % (100 * r['probe_bookkeeping_share'])) if r.get('probe_bookkeeping_share') is not None else '',
                (m(r.get('probe_transfer_usd')) + ('' if r.get('probe_value_kind') == 'net' else ' (%s)' % r.get('probe_value_kind'))) if r.get('probe_transfer_usd') is not None else '',
                ('$%.2f' % r['probe_usd_per_tx']) if r.get('probe_usd_per_tx') is not None and r['probe_usd_per_tx'] < 1e4 else m(r.get('probe_usd_per_tx')),
                ('`%s` %.0f%%' % (str(tt.get('to'))[:12], 100 * tt['share'])) if tt else '',
                ('`%s` %.0f%%' % (str(tv.get('to'))[:12], 100 * tv['share'])) if tv else ''))
    hits = D.get('hits') or []
    L += ['', '## New activity', '', 'Detector hits, most severe first (info-level in `detectors.md`). Every hit carries '
          'its chain\'s tier so a surge on an untradeable chain reads as such.', '']
    for h in hits:
        if h['severity'] == 'info':
            continue
        L.append('- **[%s]** %s  `%s`' % (h['severity'], h['title'], h['identity']))
    n_info = sum(1 for h in hits if h['severity'] == 'info')
    L += ['', '%d info-level hits (drops, divergences, thin chains, unregistered tradeable chains) are listed in `detectors.md`.' % n_info]
    if (P.get('chains') or {}):
        L += ['', '## What moved, by asset (probe)', '',
              'Transfer value per day, net per transaction: what each account gained, so routed hops and flash-loan round '
              'trips cancel while both legs of a swap count (UTXO chains and Blockchair rows are gross outputs; '
              'Hyperliquid is traded notional). ± is one standard error of the stratified estimate; `top` is the share of '
              'the sampled value that came from one block (above 0.5 the figure is one large transfer scaled up).', '',
              '| chain | asset | class | USD/day | ± | transfers/day | top |', '|---|---|---|---:|---:|---:|---:|']
        for slug in A.get('probe_ranked') or []:
            pr = P['chains'].get(slug) or {}
            f = probe_fields(pr)
            for a in f['probe_top_assets'][:5]:
                L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                    slug, a.get('symbol') or a['asset'][:10], a.get('class'), m(a.get('usd') and a['usd'] * 24 / f['probe_hours']),
                    m(a.get('usd_se') and a['usd_se'] * 24 / f['probe_hours']),
                    m(a.get('transfers') and a['transfers'] * 24 / f['probe_hours'], False) if a.get('transfers') is not None else '',
                    '%.2f' % a['top_block_share'] if a.get('top_block_share') is not None else ''))
    if V:
        L += ['', '## Cross-source agreement', '', '%d checks passed, %d failed (tolerance ±%.0f%% on transaction counts).' % (
            V['passed'], V['failed'], 100 * V['tolerance']), '', '| check | ok | detail |', '|---|---|---|']
        for c in V['checks']:
            L.append('| `%s` | %s | %s |' % (c['id'], 'ok' if c['ok'] else '**FAIL**', c['detail'].replace('|', '/')))
    if A.get('probe_failed'):
        L += ['', 'Probe failures: ' + '; '.join('%s (%s)' % (k, (v or '')[:80]) for k, v in A['probe_failed'].items())]
    (out / 'report.md').write_text('\n'.join(L) + '\n')
    print('wrote %s' % (out / 'report.md'))


# ---------------------------------------------------------------------------------------------- run

def cmd_run(args):
    date = utc_now().strftime('%Y-%m-%d')
    out = Path(args.out or ('research/%s/chains' % date))
    py = [sys.executable]
    steps = []
    if not args.skip_census:
        steps += [('census fetch', py + ['scripts/chain_census.py', 'fetch', '--out', str(out)]),
                  ('census build', py + ['scripts/chain_census.py', 'build', '--out', str(out)])]
    if not args.skip_probe:
        win = ['--hours', str(args.hours)] if args.hours else ['--day', args.day]
        steps += [('probe', py + ['scripts/chain_probe.py', 'run', '--out', str(out), '--samples', str(args.samples),
                                  '--workers', str(args.workers)] + win +
                   (['--chains', args.chains] if args.chains else []))]
    steps += [('analyze', py + ['scripts/chain_activity.py', 'analyze', '--out', str(out)]),
              ('detect', py + ['scripts/chain_activity.py', 'detect', '--out', str(out)]),
              ('verify', py + ['scripts/chain_activity.py', 'verify', '--out', str(out)]),
              ('render', py + ['scripts/chain_activity.py', 'render', '--out', str(out)]),
              ('series', py + ['scripts/chain_activity.py', 'series', '--out', str(out)]),
              ('ingest', py + ['scripts/findings.py', 'ingest', '--chain', 'chains', '--out', str(out)])]
    t0 = time.time()
    failed = []
    for name, cmd in steps:
        print('== %s' % name, flush=True)
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            failed.append(name)
            if name in ('census fetch', 'census build', 'analyze'):
                break
    D = load_json(out / 'detectors.json', {})
    V = load_json(out / 'verify.json', {})
    sev = collections.Counter(h['severity'] for h in D.get('hits') or [])
    line = '- %s `%s` hits=%s verify=%s/%s steps_failed=%s (%ds)\n' % (
        utc_now().isoformat(timespec='seconds'), out, dict(sev), V.get('passed'), (V.get('passed') or 0) + (V.get('failed') or 0),
        failed, time.time() - t0)
    if not LOG.exists():
        LOG.write_text('# Chain activity daily log\n\nOne line per pass of `scripts/chain_activity.py run`. Read this before a session.\n\n')
    with LOG.open('a') as f:
        f.write(line)
    print(line.strip())
    return 1 if failed else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('analyze'); a.add_argument('--out', required=True); a.add_argument('--top', type=int, default=60)
    b = sub.add_parser('detect'); b.add_argument('--out', required=True); b.add_argument('--all', action='store_true')
    c = sub.add_parser('verify'); c.add_argument('--out', required=True); c.add_argument('--tolerance', type=float, default=0.25)
    d = sub.add_parser('render'); d.add_argument('--out', required=True); d.add_argument('--top', type=int, default=60)
    e = sub.add_parser('series'); e.add_argument('--out', required=True)
    f = sub.add_parser('run')
    f.add_argument('--out'); f.add_argument('--samples', type=int, default=200)
    f.add_argument('--day', default='yesterday', help="probe a complete UTC day (default: yesterday), aligned with the census")
    f.add_argument('--hours', type=float, default=0, help='probe a trailing window of this many hours instead of --day')
    f.add_argument('--workers', type=int, default=6); f.add_argument('--chains')
    f.add_argument('--skip-census', action='store_true'); f.add_argument('--skip-probe', action='store_true')
    args = p.parse_args()
    return {'analyze': cmd_analyze, 'detect': cmd_detect, 'verify': cmd_verify, 'render': cmd_render,
            'series': cmd_series, 'run': cmd_run}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main() or 0)
