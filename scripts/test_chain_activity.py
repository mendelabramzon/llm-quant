#!/usr/bin/env python3
"""Tests for the chain-activity framework: the estimators the probe stands on, the census joins, and the new-activity
detectors on synthetic series where the right answer is known (a surge that must fire, a flat or seasonal series that
must not, a missing reading that must not be read as zero).

    uv run --with pycryptodome python -m pytest scripts/test_chain_activity.py -q
"""
import datetime as dt
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chain_activity as CA  # noqa: E402
import chain_census as CC    # noqa: E402
from chain_adapters import asset_class, net_positive, sample_points, stratified_total, top_share  # noqa: E402


def days(n, end='2026-10-08'):
    e = dt.date.fromisoformat(end)
    return [(e - dt.timedelta(days=n - 1 - i)).isoformat() for i in range(n)]


def series(vals, end='2026-10-08'):
    return dict(zip(days(len(vals), end), vals))


# ---------------------------------------------------------------------------------------------- estimators

def test_sample_points_stratified_and_reproducible():
    a = sample_points(1000, 1999, 50, seed=7)
    b = sample_points(1000, 1999, 50, seed=7)
    assert a == b and len(a) == 50
    # one point per stratum of width 20
    assert all(1000 + 20 * h <= x <= 1000 + 20 * h + 19 for h, x in enumerate(a))
    assert sample_points(5, 9, 50) == [5, 6, 7, 8, 9]   # fewer units than samples: read them all


def test_stratified_total_exact_when_complete_and_unbiased_when_sampled():
    vals = [3, 1, 4, 1, 5, 9, 2, 6]
    t, se = stratified_total(vals, len(vals))
    assert t == sum(vals) and se == 0.0
    rng = random.Random(1)
    pop = [rng.expovariate(1 / 100) for _ in range(20000)]
    est = []
    for seed in range(30):
        pts = sample_points(0, len(pop) - 1, 200, seed=seed)
        est.append(stratified_total([pop[i] for i in pts], len(pop))[0])
    mean = sum(est) / len(est)
    assert abs(mean / sum(pop) - 1) < 0.03
    _, se = stratified_total([pop[i] for i in sample_points(0, len(pop) - 1, 200, seed=99)], len(pop))
    sd = math.sqrt(sum((e - mean) ** 2 for e in est) / (len(est) - 1))
    assert 0.5 < se / sd < 2.0   # the reported standard error is the right order of magnitude


def test_net_positive_cancels_hops_and_round_trips():
    assert net_positive([('a', 'b', 100)]) == 100
    # router hop: user -> router -> pool nets to one transfer of 100
    assert net_positive([('user', 'router', 100), ('router', 'pool', 100)]) == 100
    # flash loan repaid with a fee counts only the fee
    assert net_positive([('pool', 'bot', 1_000_000), ('bot', 'pool', 1_000_500)]) == 500
    # self transfer is nothing
    assert net_positive([('a', 'a', 5)]) == 0
    # a swap's leg in one asset: user pays the pool
    assert net_positive([('user', 'pool', 70)]) == 70


def test_top_share_and_asset_class():
    assert top_share([1, 1, 2]) == 0.5
    assert top_share([0, 0]) is None
    assert asset_class('USDC') == 'usd_stable' and asset_class('USD₮0') == 'usd_stable'
    assert asset_class('EURC') == 'eur_stable' and asset_class('cbBTC') == 'btc' and asset_class('wstETH') == 'eth'
    assert asset_class('WMON', ['MON']) == 'native' and asset_class('PEPE') == 'other'


# ---------------------------------------------------------------------------------------------- surge statistics

def flat_noisy(n, level=1e7, sd=0.08, seed=0, weekly=None):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        x = level * math.exp(rng.gauss(0, sd))
        if weekly and i % 7 in (5, 6):
            x *= weekly
        out.append(x)
    return out


def test_surge_fires_on_a_jump_and_not_on_noise():
    base = flat_noisy(120, seed=1)
    st = CA.surge_stats(series(base + [base[-1] * 4]), recent=1)
    assert st['ratio'] > 3 and st['p_up'] <= 1 / 100
    quiet = CA.surge_stats(series(flat_noisy(121, seed=2)), recent=1)
    assert quiet['ratio'] < 1.5 and quiet['p_up'] > 0.05


def test_weekday_baseline_absorbs_a_weekly_cycle():
    # weekends at 30% of weekdays: a Monday is ~3.3x the weekend but not a surge against previous Mondays
    vals = flat_noisy(127, seed=3, weekly=0.3)
    d = days(len(vals))
    monday = max(i for i, x in enumerate(d) if dt.date.fromisoformat(x).weekday() == 0)
    s = series(vals[:monday + 1], end=d[monday])
    st = CA.surge_stats(s, recent=1, weekday=True)
    assert st['ratio'] < 1.5


def test_weekly_surge_and_spike_share():
    base = flat_noisy(100, seed=4)
    level = base + [x * 2.5 for x in flat_noisy(7, seed=5)]
    st = CA.surge_stats(series(level), recent=7)
    assert st['ratio'] > 2 and st['p_up'] <= 0.05 and st['max_day_excess_share'] < 0.3
    spike = base + [1e7] * 6 + [1.5e8]
    st2 = CA.surge_stats(series(spike), recent=7)
    assert st2['max_day_excess_share'] > CA.SPIKE_SHARE


def test_empirical_null_is_series_specific():
    # a chain that prints a 4x day every ten days: a 3x day there is routine, the same 3x on a quiet chain is not
    rng = random.Random(6)
    spiky = [1e7 * (4.0 if i % 10 == 5 else math.exp(rng.gauss(0, 0.05))) for i in range(149)] + [3e7]
    quiet = [1e7 * math.exp(rng.gauss(0, 0.05)) for i in range(149)] + [3e7]
    st_spiky = CA.surge_stats(series(spiky), recent=1, weekday=False)
    st_quiet = CA.surge_stats(series(quiet), recent=1, weekday=False)
    assert st_spiky['ratio'] > 2.5 and st_quiet['ratio'] > 2.5
    assert st_spiky['p_up'] > 0.05 and st_quiet['p_up'] < 0.01


def test_too_short_series_is_none():
    assert CA.surge_stats(series([1.0] * 10), recent=1) is None


# ---------------------------------------------------------------------------------------------- census pieces

def test_infer_llama_keys_from_single_chain_protocols():
    dexs = {'protocols': [
        {'chains': ['Avalanche'], 'breakdown24h': {'avax': {'p1': 1}}},
        {'chains': ['Avalanche'], 'breakdown24h': {'avax': {'p2': 1}}},
        {'chains': ['Gnosis'], 'breakdown24h': {'xdai': {'p3': 1}}},
        {'chains': ['Base', 'Ethereum'], 'breakdown24h': {'base': {'p4': 1}, 'ethereum': {'p4': 1}}},
    ]}
    k = CC.infer_llama_keys(dexs)
    assert k['avax']['name'] == 'Avalanche' and k['avax']['votes'] == 2 and k['xdai']['name'] == 'Gnosis'
    assert 'base' not in k   # multi-chain protocols cast no vote


def test_complete_days_drops_today_and_converts():
    ts = int(dt.datetime(2026, 10, 8, tzinfo=dt.timezone.utc).timestamp())
    out = CC.complete_days([[ts - 86400, 1], [ts, 2], [ts + 86400, 3]], '2026-10-09')
    assert out == {'2026-10-07': 1.0, '2026-10-08': 2.0}
    assert CC.complete_days([['2026-10-08', 5], ['2026-10-09', 6]], '2026-10-09') == {'2026-10-08': 5.0}


def test_tiers():
    assert CC.tier_of({'dex_7d_avg': 2e8}) == 'deep'
    assert CC.tier_of({'dex_7d_avg': 2e7, 'stables': 2e9}) == 'deep'
    assert CC.tier_of({'dex_7d_avg': 2e6, 'stables': 5e7}) == 'tradeable'
    assert CC.tier_of({'dex_7d_avg': 5e5, 'stables': 5e7, 'native_volume_24h': 5e7}) == 'token_only'
    assert CC.tier_of({'dex_7d_avg': 5e5}) == 'thin'
    assert CC.tier_of({}) == 'inactive'


def test_pct_ranks():
    r = CC.pct_ranks({'a': 1, 'b': 2, 'c': None, 'd': 0, 'e': 4})
    assert r['e'] == 1.0 and r['a'] == 1 / 3 and r['c'] is None and r['d'] is None


# ---------------------------------------------------------------------------------------------- detectors

def census_with(chains, today='2026-10-09'):
    return {'today': today, 'chains': chains}


def chain_row(name, tier='tradeable', **series_):
    return {'name': name, 'slug': name.lower(), 'tier': tier, 'now': {'dex_7d_avg': 5e6, 'stables': 1e8},
            'series': series_, 'stables_by_asset': [], 'activity': {'score': 0.5, 'n_axes': 5}}


def test_det_surge_positive_and_negative_controls():
    surge = flat_noisy(120, level=5e6, seed=7) + [5e7]
    flat = flat_noisy(121, level=5e6, seed=8)
    C = census_with({'Up': chain_row('Up', dex=series(surge)), 'Flat': chain_row('Flat', dex=series(flat))})
    hits = CA.det_surge(C, {})
    keys = {h.key for h in hits if h.detector == 'chain_surge'}
    assert 'Up:dex:d1' in keys and not any(k.startswith('Flat:') for k in keys)
    h = next(h for h in hits if h.key == 'Up:dex:d1')
    assert h.severity == 'high' and h.evidence['tradeability']['tier'] == 'tradeable'


def test_det_surge_respects_absolute_floor_and_tier():
    tiny = flat_noisy(120, level=1e4, seed=9) + [1e5]   # x10 but only +$90k a day: below the $1M floor
    C = census_with({'Tiny': chain_row('Tiny', dex=series(tiny))})
    assert not [h for h in CA.det_surge(C, {}) if h.detector == 'chain_surge']
    thin = flat_noisy(120, level=1e6, seed=10) + [2e7]
    C = census_with({'Thin': chain_row('Thin', tier='thin', dex=series(thin))})
    h = [h for h in CA.det_surge(C, {}) if h.key == 'Thin:dex:d1'][0]
    assert h.severity == 'info'   # a surge on a chain you cannot trade on is information, not an alert


def test_market_wide_surge_is_not_news_but_an_outlier_is():
    chains = {}
    for i in range(10):
        base = flat_noisy(120, level=5e6, seed=30 + i)
        chains['C%d' % i] = chain_row('C%d' % i, dex=series(base + [base[-1] * 2.6]))   # everyone x2.6 the same day
    out = flat_noisy(120, level=5e6, seed=99)
    chains['Out'] = chain_row('Out', dex=series(out + [out[-1] * 12]))
    hits = {h.key: h for h in CA.det_surge(census_with(chains), {}) if h.detector == 'chain_surge'}
    assert hits['Out:dex:d1'].severity == 'high' and hits['Out:dex:d1'].evidence['excess_ratio'] > 3
    assert all(hits[k].severity == 'info' for k in hits if k.startswith('C'))


def test_det_stable_inflow_missing_history_is_not_new():
    row = chain_row('X', stables=series(flat_noisy(60, level=1e8, sd=0.001, seed=11)))
    row['stables_by_asset'] = [
        {'symbol': 'GAP', 'usd': 5e8, 'prev_day': 4.9e8, 'prev_week': 4.8e8, 'prev_month': None, 'peg': 'peggedUSD'},
        {'symbol': 'NEW', 'usd': 5e7, 'prev_day': 1e6, 'prev_week': 0.0, 'prev_month': 0.0, 'peg': 'peggedUSD'},
        {'symbol': 'UP', 'usd': 2e8, 'prev_day': 1.9e8, 'prev_week': 1e8, 'prev_month': 9e7, 'peg': 'peggedUSD'}]
    keys = {h.key for h in CA.det_stable_inflow(census_with({'X': row}), {})}
    assert 'X:NEW:new' in keys and 'X:UP' in keys
    assert not any('GAP' in k for k in keys)   # a gap in DefiLlama's history is not a launch


def test_det_stable_inflow_catches_a_step_older_than_a_week():
    vals = [1e8] * 40 + [4e8] * 20   # a $300M step twenty days ago, flat since
    keys = {h.key for h in CA.det_stable_inflow(census_with({'S': chain_row('S', stables=series(vals))}), {})}
    assert 'S:30d' in keys and 'S' not in keys


def test_det_new_chain():
    young = series([0] * 80 + [2e6] * 40)                    # first non-zero 40 days before today
    old = series([2e6] * 120)
    C = census_with({'Young': chain_row('Young', dex=young), 'Old': chain_row('Old', dex=old)})
    keys = {h.key for h in CA.det_new_chain(C, {})}
    assert keys == {'Young'}


def test_det_divergence():
    tx = flat_noisy(100, level=1e6, seed=12) + [3e6] * 7
    dex = flat_noisy(107, level=5e6, seed=13)
    C = census_with({'Bots': chain_row('Bots', tx=series(tx), dex=series(dex))})
    h = CA.det_divergence(C, {})
    assert [x.key for x in h] == ['Bots:activity_without_value']


def test_det_probe_history_catches_a_two_day_jump(tmp_path, monkeypatch):
    # the Cardano shape of 2026-10-06..08: two weeks near 35k a day, then 327k, then 543k
    import json as _json
    hist = tmp_path / 'tx_history.jsonl'
    rows = []
    vals = flat_noisy(13, level=35_000, seed=14) + [326_661, 542_532]
    for d, v in zip(days(len(vals)), vals):
        rows.append({'chain': 'cardano', 'day': d, 'ok': True, 'count': v})
    flat = flat_noisy(15, level=1e6, seed=15)
    for d, v in zip(days(len(flat)), flat):
        rows.append({'chain': 'steady', 'day': d, 'ok': True, 'count': v})
    hist.write_text(''.join(_json.dumps(r) + '\n' for r in rows))
    monkeypatch.setattr(CA, 'TX_HISTORY', hist)
    C = census_with({'Cardano': dict(chain_row('Cardano'), slug='cardano'), 'Steady': dict(chain_row('Steady'), slug='steady')})
    hits = CA.det_probe_history(C, {})
    assert [h.key for h in hits] == ['cardano']
    assert hits[0].detector == 'probe_tx_surge' and hits[0].evidence['ratio'] > 10 and hits[0].severity == 'high'


def test_calendar_day_and_overlap_mean():
    d0 = int(dt.datetime(2026, 10, 8, tzinfo=dt.timezone.utc).timestamp())
    assert CA.calendar_day({'start_ts': d0, 'end_ts': d0 + 86400}) == '2026-10-08'
    assert CA.calendar_day({'start_ts': d0 + 60, 'end_ts': d0 + 86460}) is None
    daily = {'2026-10-07': 100.0, '2026-10-08': 200.0}
    # a trailing day that is three quarters 10-08 and one quarter 10-09 (missing): only the covered part counts
    assert CA.overlap_mean(daily, {'start_ts': d0 + 21600, 'end_ts': d0 + 108000}) == 200.0
    # half 10-07, half 10-08
    assert CA.overlap_mean(daily, {'start_ts': d0 - 43200, 'end_ts': d0 + 43200}) == 150.0
    assert CA.overlap_mean({}, {'start_ts': d0, 'end_ts': d0 + 86400}) is None


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-q']))
