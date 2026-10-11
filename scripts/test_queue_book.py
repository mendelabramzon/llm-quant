"""queue_book: the shared-pool simulator must equal the per-asset one when there is one asset, add up when the
assets never overlap, and ration when they do; per-env chain costs; the five-asset window.

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_queue_book.py -q
    QB_DATA_TESTS=1 QUEUE_BOOK_LONG=<dir with swaps_lido/kelp> uv run --with pytest --with pycryptodome python -m pytest scripts/test_queue_book.py -q
"""
import os
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dislocation_history as D   # noqa: E402
import queue_book as Q            # noqa: E402


def _env(sells, wait=2.0, carry_bps_day=0.7, market=None, accrues=False, fee=0.0):
    return {'sells': sorted(sells, key=lambda s: s['ts']), 'wait': (lambda ts: wait), 'carry': (lambda ts: carry_bps_day),
            'market': market or (lambda ts: None), 'accrues': accrues, 'redemption_fee_bps': fee}


def _sells(n, seed, t0=1_700_000_000, span_days=60):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        out.append({'ts': t0 + rng.randrange(span_days * 86400), 'usd': rng.choice([2e4, 1e5, 5e5, 3e6]),
                    'discount_bps': rng.uniform(-5, 60), 'fee_bps': rng.choice([0.0, 1.0, 4.0]), 'pool': 'p', 'tx': '0x%x' % i})
    return sorted(out, key=lambda s: s['ts'])


def test_one_asset_reproduces_simulate_bid():
    sells = _sells(400, 1)
    market = (lambda ts: 25.0)
    for size in (1e5, 1e6, 5e6):
        for h in (0.0, 3.0, 10.0):
            ref, st_ref = D.simulate_bid(sells, size, h, lambda ts: 2.0, lambda ts: 0.7, market_bps_at=market)
            got, st = Q.simulate_book({'a': _env(sells, market=market)}, size, h)
            assert [(f['ts'], round(f['usd'], 6), round(f['value_usd'], 6)) for f in ref] == \
                   [(f['ts'], round(f['usd'], 6), round(f['value_usd'], 6)) for f in got]
            assert abs(st_ref['filled_usd'] - st['filled_usd']) < 1e-6


def test_disjoint_assets_add_up():
    a = _sells(150, 2, t0=1_700_000_000, span_days=30)
    b = _sells(150, 3, t0=1_700_000_000 + 60 * 86400, span_days=30)    # starts after every a-fill has been released
    size = 2e6
    fa, _ = Q.simulate_book({'a': _env(a)}, size, 0.0)
    fb, _ = Q.simulate_book({'b': _env(b)}, size, 0.0)
    fab, st = Q.simulate_book({'a': _env(a), 'b': _env(b)}, size, 0.0)
    assert abs(sum(f['value_usd'] for f in fa) + sum(f['value_usd'] for f in fb) - sum(f['value_usd'] for f in fab)) < 1e-6
    assert set(st['by_asset_value_usd']) == {'a', 'b'}


def test_overlapping_assets_share_the_pool():
    t = 1_700_000_000
    a = [{'ts': t, 'usd': 1e6, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    b = [{'ts': t + 3600, 'usd': 1e6, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    fills, st = Q.simulate_book({'a': _env(a, wait=5.0), 'b': _env(b, wait=5.0)}, 1e6, 0.0)
    assert [f['asset'] for f in fills] == ['a']                     # b arrives while a's capital is still queued
    assert st['missed_capital_usd'] == 1e6
    fills, _ = Q.simulate_book({'a': _env(a, wait=5.0), 'b': _env(b, wait=5.0)}, 2e6, 0.0)
    assert [f['asset'] for f in fills] == ['a', 'b']


def test_locked_daily_counts_the_wait():
    fills = [{'ts': 10 * 86400 + 100, 'usd': 5.0, 'wait_days': 2.0}, {'ts': 11 * 86400, 'usd': 1.0, 'wait_days': 0.5}]
    v = Q.locked_daily(fills, 9, 6)
    assert v == [0.0, 5.0, 6.0, 5.0, 0.0, 0.0]


def test_env_costs_replace_the_defaults_for_that_asset_only():
    sells = _sells(300, 4)
    market = (lambda ts: 25.0)
    plain = _env(sells, market=market)
    priced = dict(_env(sells, market=market), gas_usd=1.0, min_fill_usd=1_000.0)
    for size in (2e5, 3e6):
        ref, st_ref = Q.simulate_book({'a': plain}, size, 2.0, gas_usd=1.0, min_fill_usd=1_000.0)
        got, st = Q.simulate_book({'a': priced}, size, 2.0)            # the env's own costs, default arguments
        assert [(f['ts'], f['usd'], f['value_usd']) for f in ref] == [(f['ts'], f['usd'], f['value_usd']) for f in got]
        assert st_ref['filled_usd'] == st['filled_usd']
    # in a book, each asset pays its own chain's gas; an env without costs is priced exactly as before
    t = 1_700_000_000
    a = [{'ts': t, 'usd': 4_000.0, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    b = [{'ts': t + 60, 'usd': 4_000.0, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    fills, _ = Q.simulate_book({'a': _env(a, wait=1.0, carry_bps_day=0.0),
                                'b': dict(_env(b, wait=1.0, carry_bps_day=0.0), gas_usd=1.0, min_fill_usd=1_000.0)}, 1e7, 0.0)
    assert [f['asset'] for f in fills] == ['b']                       # a's $4k is under the $5k Ethereum minimum
    assert abs(fills[0]['value_usd'] - (4_000.0 * 30.0 / 1e4 - 1.0)) < 1e-12


def test_common_window_is_the_intersection_in_whole_days():
    e1 = {'first_ts': 10 * 86400 + 3600, 'last_ts': 40 * 86400 + 7200}
    e2 = {'first_ts': 20 * 86400, 'last_ts': 50 * 86400 - 1}             # a whole-day window (kHYPE's shape)
    first_ts, last_ts, first_day, n_days = Q.common_window({'a': e1, 'b': e2})
    assert (first_ts, last_ts, first_day, n_days) == (20 * 86400, 40 * 86400 + 7200, 20, 21)
    assert Q.common_window({'b': e2})[2:] == (20, 30)                  # alone, the whole-day window is kept exactly


# ---------------------------------------------------------------------------------------------- saved-data checks
# Opt-in (they read the studies' saved files, ~15-60 s): QB_DATA_TESTS=1, and QUEUE_BOOK_LONG=<dir with swaps_lido/kelp>
# for the four-asset regression.
DATA = os.environ.get('QB_DATA_TESTS') == '1'


@pytest.mark.skipif(not DATA or not (Q.KHYPE_DIR / 'raw' / 'khype_swaps').exists(), reason='QB_DATA_TESTS=1 and queue_bids_alt raw data')
def test_khype_env_reproduces_queue_bids_alt_on_saved_data():
    env = Q.load_khype_env(Q.KHYPE_DIR)
    ref = D.read_json(Q.KHYPE_DIR / 'analysis.json')['queue_bids']['khype']['grid']['10000000']
    _, _, first_day, n_days = Q.common_window({'khype': env})
    r, _ = Q.run_choice({'khype': env}, 10_000_000, first_day, n_days)
    assert r['chosen_hurdle'] == ref['chosen_hurdle'] and r['out_of_sample_usd_per_year'] == ref['out_of_sample_usd_per_year']


@pytest.mark.skipif(not DATA or not os.environ.get('QUEUE_BOOK_LONG'), reason='QB_DATA_TESTS=1 and QUEUE_BOOK_LONG')
def test_all4_still_earns_409889_at_15m_on_its_own_window():
    envs = Q.load_default_envs(Path(os.environ['QUEUE_BOOK_LONG']))
    reg = Q.regression_all4(envs)
    assert reg['ok'] and int(round(reg['out_of_sample_usd_per_year'])) == 409_889


def test_env_delay_is_a_floor_for_that_asset_only():
    t = 1_700_000_000
    sells = [{'ts': t + 3600 * i, 'usd': 1e5, 'discount_bps': 30.0, 'fee_bps': 0.0} for i in range(30)]
    m = (lambda ts: 30.0 if ts >= t + 10 * 3600 else None)          # the market only shows the edge from hour 10
    late = dict(_env(sells, wait=0.0, market=m), delay_s=5 * 3600)
    f_env, _ = Q.simulate_book({'a': late}, 1e9, 0.0)
    f_arg, _ = Q.simulate_book({'a': _env(sells, wait=0.0, market=m)}, 1e9, 0.0, delay_s=5 * 3600)
    assert [f['ts'] for f in f_env] == [f['ts'] for f in f_arg] and f_env[0]['ts'] == t + 15 * 3600
    other = _env([dict(s, ts=s['ts'] + 1) for s in sells], wait=0.0, market=m)
    f_both, _ = Q.simulate_book({'a': late, 'b': other}, 1e9, 0.0)
    assert min(f['ts'] for f in f_both if f['asset'] == 'b') == t + 1                 # b is on time (no median: no cap)
    assert min(f['ts'] for f in f_both if f['asset'] == 'a') == t + 15 * 3600


def test_rotated_env_waits_and_pays_for_the_crossing():
    base = dict(_env([], wait=7.0, carry_bps_day=0.6 + 10.0 / 7.0), carry_stake=(lambda ts: 0.6))   # 10bp fee folded in
    r = Q.rotated_env(base, 86400)
    assert r['wait'](0) == 8.0 and r['delay_s'] == 86400
    assert abs(r['wait'](0) * r['carry'](0) - (7.0 * 0.6 + 10.0 + 1.0 * 0.6)) < 1e-12   # the fee once, the stake for 8 days
    assert ('_edges', 2.0, True, 0) not in r


def test_locked_end_of_day_is_an_instant():
    d0 = 100
    fills = [{'ts': (d0 + 1) * 86400 + 100, 'usd': 5.0, 'wait_days': 2.0},       # held over the ends of days 1 and 2
             {'ts': (d0 + 2) * 86400 + 10, 'usd': 1.0, 'wait_days': 0.25},       # released the same day: never at a day's end
             {'ts': (d0 + 3) * 86400 - 3600, 'usd': 2.0, 'wait_days': 1.0 / 24}]  # released exactly at midnight: free
    assert Q.locked_end_of_day(fills, d0, 5) == [0.0, 5.0, 5.0, 0.0, 0.0]
    assert Q.locked_daily(fills, d0, 5) == [0.0, 5.0, 8.0, 7.0, 0.0]           # the touch count double-counts turnover


# ---------------------------------------------------------------------------------------------- next-hour pricing
def test_window_fns_are_strict_and_tie_ordered():
    H = 1_700_002_800                                                  # an hour boundary
    trades = [(H + 10, 'b', 5.0, 100.0), (H + 10, 'a', 9.0, 50.0), (H + 20, 'a', 3.0, 150.0), (H - 60, 'c', 40.0, 1e6)]
    med, first = Q.trade_window_fns(trades)
    # venue a: (9*50 + 3*150) / 200 = 4.5; venue b: 5.0; venue c traded before H and is not carried forward
    assert abs(med(H, H + 3600) - 4.75) < 1e-12
    assert first(H, H + 3600) == 9.0                                   # same second: ties ordered by pool name
    assert med(H + 3600, H + 7200) is None and first(H + 3600, H + 7200) is None


def test_later_hour_buys_at_the_boundary_at_the_later_price():
    H = 1_700_002_800
    sells = [{'ts': H - 1200, 'usd': 1e5, 'discount_bps': 30.0, 'fee_bps': 1.0},     # qualifies at 28bp in its own hour
             {'ts': H + 600, 'usd': 1e5, 'discount_bps': 30.0, 'fee_bps': 1.0}]      # its next hour has no trade: skipped
    later = [(H + 100, 'p', 12.0, 1e6), (H + 200, 'q', 20.0, 1e6), (H + 300, 'p', 14.0, 1e6)]
    env = _env(sells, wait=2.0, carry_bps_day=0.5, market=lambda ts: 30.0)
    env['market_in'], env['first_in'] = Q.trade_window_fns(later)
    fills, st = Q.simulate_book({'a': env}, 1e7, 1.0, later='hour')
    assert len(fills) == 1 and fills[0]['ts'] == H and fills[0]['sell_ts'] == H - 1200
    # later median: venue p 13bp, q 20bp -> 16.5; edge = min(30 - 2, 16.5 - 1) - 2 days x 0.5bp = 14.5bp
    assert abs(fills[0]['edge_bps'] - 14.5) < 1e-12 and st['later_missing'] == 1
    f1, _ = Q.simulate_book({'a': env}, 1e7, 1.0, later='hour', later_price='first')
    assert abs(f1[0]['edge_bps'] - (min(28.0, 12.0 - 1.0) - 1.0)) < 1e-12             # the first trade after H: 12bp
    f2, st2 = Q.simulate_book({'a': env}, 1e7, 15.0, later='hour')                    # 14.5bp no longer clears 15bp
    assert f2 == [] and st2['later_below_hurdle'] == 1
    f0, _ = Q.simulate_book({'a': env}, 1e7, 1.0)                                      # the default is untouched
    assert [f['ts'] for f in f0] == [H - 1200, H + 600] and abs(f0[0]['edge_bps'] - 27.0) < 1e-12


def test_later_capital_locks_from_the_purchase():
    H = 1_700_002_800
    sells = [{'ts': H - 100, 'usd': 1e6, 'discount_bps': 30.0, 'fee_bps': 0.0},
             {'ts': H + 3600 - 100, 'usd': 1e6, 'discount_bps': 30.0, 'fee_bps': 0.0}]
    env = _env(sells, wait=1.0 / 24 - 1.0 / 86400, carry_bps_day=0.0, market=lambda ts: 30.0)   # released a second before the next buy
    env['market_in'], env['first_in'] = Q.trade_window_fns([(H + 5, 'p', 30.0, 1.0), (H + 3605, 'p', 30.0, 1.0)])
    fills, st = Q.simulate_book({'a': env}, 1e6, 0.0, later='hour')
    assert [f['ts'] for f in fills] == [H, H + 3600] and st['missed_capital_usd'] == 0.0


def test_persistence_counts_the_later_edge():
    H = 1_700_002_800
    sells = [{'ts': H - 100, 'usd': 1e5, 'discount_bps': 30.0, 'fee_bps': 0.0},       # next hour still 20bp: persists
             {'ts': H + 3500, 'usd': 3e5, 'discount_bps': 30.0, 'fee_bps': 0.0},      # next hour 0.5bp: recovered
             {'ts': H + 7300, 'usd': 1e5, 'discount_bps': 30.0, 'fee_bps': 0.0}]      # no trade next hour
    env = _env(sells, wait=0.0, market=lambda ts: 30.0)
    env['market_in'], env['first_in'] = Q.trade_window_fns([(H + 10, 'p', 20.0, 1.0), (H + 3610, 'p', 0.5, 1.0)])
    p = Q.persistence(env, hurdle_bps=1.0, delays=('hour',))['hour|median']['all']
    assert p['qualifying'] == 3 and abs(p['still_clear_share'] - 1 / 3) < 1e-12 and abs(p['still_clear_usd_share'] - 0.2) < 1e-12
    assert abs(p['later_missing_share'] - 1 / 3) < 1e-12 and abs(p['still_clear_share_of_those_traded'] - 0.5) < 1e-12
