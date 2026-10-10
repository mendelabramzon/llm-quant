#!/usr/bin/env python3
"""Tests for hl_vault_skill.py on synthetic inputs: flow-adjusted step returns (Modified Dietz, closing steps,
wipe-outs, the large-flow fallback), the return index, grid alignment of holding windows, signals and ranking without
look-ahead, the follower account's profit share (cost-basis high-water mark, partial withdrawals), savings accrual
across years, rank correlation and the HAC regression.

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_hl_vault_skill.py -q
"""
import copy
import datetime as dt
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hl_vault_skill as H  # noqa: E402

UTC = dt.timezone.utc
DAY = H.DAY_MS


def ms(s, h=0):
    return int(dt.datetime.strptime(s, '%Y-%m-%d').replace(hour=h, tzinfo=UTC).timestamp() * 1000)


def make_vault(start, step_days, av, pnl, addr='0xa', closed=False, lc=0.1, rel='normal', leader='0xl'):
    """A cached vaultDetails record on a regular grid, parsed the way analyze() parses it."""
    ts = [ms(start) + int(i * step_days * DAY) for i in range(len(av))]
    rec = {'tier': 'core', 'fetched_at_ms': ts[-1], 'response': {
        'name': addr, 'vaultAddress': addr, 'leader': leader, 'isClosed': closed, 'allowDeposits': True,
        'relationship': {'type': rel}, 'leaderFraction': 0.1, 'leaderCommission': lc, 'followers': [],
        'portfolio': [['allTime', {'accountValueHistory': [[t, str(a)] for t, a in zip(ts, av)],
                                   'pnlHistory': [[t, str(p)] for t, p in zip(ts, pnl)]}]]}}
    return H.parse_vault(rec)


# ---------------------------------------------------------------------------------------------- step returns

def test_no_flow_steps_are_simple_returns_and_first_funding_step_has_none():
    r, flow, flags = H.step_returns([0, 100, 110, 99], [0, 0, 10, -1])
    assert r[0] is None and r[1] is None          # nothing at risk at the start of the funding step
    assert r[2] == pytest.approx(0.10)
    assert r[3] == pytest.approx(-0.10)
    assert flow[1] == pytest.approx(100) and flow[2] == pytest.approx(0)


def test_deposit_mid_step_uses_modified_dietz():
    # 100 at the start, 100 deposited during the step, 10 of P&L: r = 10 / (100 + 0.5 * 100)
    r, flow, flags = H.step_returns([100, 210], [0, 10])
    assert flow[1] == pytest.approx(100)
    assert r[1] == pytest.approx(10 / 150)
    assert flags[1] is None


def test_withdrawal_mid_step_uses_modified_dietz():
    r, _, _ = H.step_returns([200, 105], [0, 5])   # F = -100
    assert r[1] == pytest.approx(5 / 150)


def test_closing_step_earns_on_starting_equity_and_index_goes_flat():
    v = make_vault('2024-01-01', 14, [0, 100, 90, 0, 0], [0, 0, -10, -13, -13], closed=True)
    assert v['r'][2] == pytest.approx(-0.10)
    assert v['r'][3] == pytest.approx(-3 / 90)       # all P&L of the closing step was earned before the payout
    assert v['flags'][3] == 'closing'
    assert v['r'][4] is None                          # empty afterwards: no return, index flat
    assert v['idx'][4] == pytest.approx(v['idx'][3])
    assert v['idx'][3] == pytest.approx(0.9 * (1 - 3 / 90))


def test_wipeout_is_floored_and_index_stays_positive_for_a_refunded_vault():
    r, _, flags = H.step_returns([100, 0, 0], [0, -150, -150])
    assert r[1] == H.RET_FLOOR and flags[1] == 'wipeout'
    v = make_vault('2024-01-01', 7, [0, 100, 1, 101, 111], [0, 0, -99.5, -99.5, -89.5])
    assert all(x > 0 for x in v['idx'])
    assert v['r'][4] == pytest.approx(10 / 101)


def test_large_two_way_flows_use_the_conservative_bound():
    # A $2.4k vault took in and paid out ~$0.5M inside one step and booked $569k of P&L (seen in the data):
    # Dietz would give +47,900%; the fallback divides by the largest capital plausibly at risk.
    a0, a1, dp = 2378.0, 137795.0, 569238.0
    r, flow, flags = H.step_returns([a0, a1], [0, dp])
    assert flags[1] == 'dietz_fallback'
    assert r[1] == pytest.approx(dp / max(a0 + max(flow[1], 0), a1))
    # a big loss after deposits: the deposits were at risk, so the denominator includes them
    r2, flow2, flags2 = H.step_returns([62260, 4999], [0, -167346])
    assert flags2[1] == 'dietz_fallback'
    assert r2[1] == pytest.approx(-167346 / (62260 + flow2[1]))
    assert -1 < r2[1] < -0.9


def test_extreme_return_without_flows_is_kept():
    r, _, flags = H.step_returns([5708, 87219], [0, 81511])
    assert r[1] == pytest.approx(81511 / 5708)
    assert flags[1] == 'gt100pct'


def test_twr_index_ignores_flows():
    # +10% then a 10x deposit then +10% again: the index is 1.21 whatever the money did
    v = make_vault('2024-01-01', 7, [0, 100, 110, 1110, 1221], [0, 0, 10, 10, 121])
    assert v['r'][3] == pytest.approx(0.0)
    assert v['idx'][-1] == pytest.approx(1.21)


# ---------------------------------------------------------------------------------------------- grid alignment

def test_month_arithmetic_and_grid_lookups():
    assert H.add_months(ms('2024-01-31'), 1) == ms('2024-02-29')
    assert H.add_months(ms('2024-03-01'), -3) == ms('2023-12-01')
    assert H.month_start(ms('2025-07-19', 13)) == ms('2025-07-01')
    ts = [ms('2024-01-01'), ms('2024-01-15'), ms('2024-01-29')]
    assert H.last_le(ts, ms('2024-01-20')) == 1
    assert H.first_ge(ts, ms('2024-01-20')) == 2
    assert H.first_ge(ts, ms('2024-01-15')) == 1 and H.last_le(ts, ms('2024-01-15')) == 1
    assert H.last_le(ts, ms('2023-12-31')) is None and H.first_ge(ts, ms('2024-02-01')) is None


def test_holding_window_starts_at_or_after_the_decision_and_chains():
    # 2-week grid starting 2024-01-03: decision 2024-03-01 -> first point >= it is 2024-03-13
    av = [0] + [100.0 * 1.01 ** i for i in range(1, 30)]
    pnl = [0, 0] + [av[i] - av[1] for i in range(2, 30)]
    v = make_vault('2024-01-03', 14, av, pnl)
    t0, t1, t2 = ms('2024-03-01'), ms('2024-04-01'), ms('2024-05-01')
    w1, w2 = H.forward_window(v, t0, t1), H.forward_window(v, t1, t2)
    assert w1[0] >= t0 and w1[1] >= t1 and w2[0] == w1[1]          # contiguous, never before the decision
    assert w1[0] - t0 < 14 * DAY
    r1, r2 = H.forward_return(v, t0, t1), H.forward_return(v, t1, t2)
    b0, b1 = H.first_ge(v['ts'], t0), H.first_ge(v['ts'], t1)
    assert r1 == pytest.approx(1.01 ** (b1 - b0) - 1)
    b2 = H.first_ge(v['ts'], t2)
    assert (1 + r1) * (1 + r2) == pytest.approx(1.01 ** (b2 - b0))


def test_forward_return_of_a_vault_empty_at_entry_is_cash():
    v = make_vault('2024-01-01', 7, [0, 100, 0, 0, 0, 0, 0], [0, 0, -5, -5, -5, -5, -5], closed=True)
    assert H.forward_return(v, ms('2024-01-20'), ms('2024-02-05')) == 0.0


def test_forward_return_none_when_grid_does_not_reach_the_exit():
    v = make_vault('2024-01-01', 7, [0, 100, 101], [0, 0, 1])
    assert H.forward_return(v, ms('2024-01-05'), ms('2024-03-01')) is None


def test_signals_use_only_points_at_or_before_t():
    av = [0] + [1000.0 * (1 + 0.02 * ((-1) ** i)) * 1.01 ** i for i in range(1, 60)]
    pnl = [0, 0] + [av[i] - av[1] for i in range(2, 60)]
    v = make_vault('2024-01-01', 7, av, pnl)
    t = ms('2024-08-01')
    s0 = H.signals_at(v, t)
    a = H.last_le(v['ts'], t)
    # rewrite every point after t (a crash, a flood of deposits): no signal may move
    av2, pnl2 = list(av), list(pnl)
    for k in range(a + 1, len(av)):
        av2[k] = av[k] * 7.0
        pnl2[k] = pnl[k] - 5000.0
    w = make_vault('2024-01-01', 7, av2, pnl2)
    s1 = H.signals_at(w, t)
    assert s0 == s1
    assert s0['ret3'] == pytest.approx(v['idx'][a] / v['idx'][H.last_le(v['ts'], H.add_months(t, -3))] - 1)
    assert s0['size'] == pytest.approx(av[a])


def test_selection_is_deterministic_and_ignores_missing_signals():
    c = [('0xb', 0.5, 1.0), ('0xa', 0.5, 1.0), ('0xc', None, 1.0), ('0xd', 0.1, 1.0), ('0xe', -1.0, 1.0)]
    assert [x[0] for x in H.select_top(c, 0.5)] == ['0xa', '0xb']
    assert [x[0] for x in H.select_top(c, 0.01)] == ['0xa']     # at least one
    assert H.select_top([('0xa', None, 1.0)], 0.2) == []


def test_eligibility_age_threshold_and_hlp_exclusion():
    v = make_vault('2024-01-01', 7, [0] + [20000.0] * 60, [0] * 61)
    assert not H.eligible(v, ms('2024-06-01'), 1e4)            # younger than 6 months
    assert H.eligible(v, ms('2024-08-01'), 1e4)
    assert not H.eligible(v, ms('2024-08-01'), 1e5)            # too small
    h = make_vault('2024-01-01', 7, [0] + [2e6] * 60, [0] * 61, rel='child')
    assert h['excluded'] and not H.eligible(h, ms('2024-08-01'), 1e4)


# ---------------------------------------------------------------------------------------------- profit share

def test_profit_share_on_gain_over_cost_basis():
    acct = H.FollowerAccount(100.0)
    acct.rebalance({'v': 1.0}, {'v': 0.1})
    acct.grow({'v': 0.20})
    assert acct.nav() == pytest.approx(118.0)                  # 120 less 10% of the 20 gain
    acct.rebalance({}, {})
    assert acct.cash == pytest.approx(118.0) and acct.fees_paid == pytest.approx(2.0)


def test_high_water_mark_is_the_followers_basis():
    acct = H.FollowerAccount(100.0)
    acct.rebalance({'v': 1.0}, {'v': 0.1})
    acct.grow({'v': -0.20})
    assert acct.nav() == pytest.approx(80.0)
    acct.grow({'v': 0.25})                                     # back to 100: no profit, no fee
    assert acct.nav() == pytest.approx(100.0)
    acct.grow({'v': 0.10})
    assert acct.nav() == pytest.approx(110 - 1.0)


def test_partial_withdrawal_crystallises_pro_rata_and_keeps_nav():
    acct = H.FollowerAccount(100.0)
    acct.rebalance({'v': 1.0}, {'v': 0.1})
    acct.grow({'v': 0.20})
    nav = acct.nav()
    acct.rebalance({'v': 0.5}, {'v': 0.1})
    assert acct.nav() == pytest.approx(nav)
    assert acct.fees_paid == pytest.approx(1.0)                 # half of the 2.0 owed
    e, b, c = acct.pos['v']
    assert e == pytest.approx(60.0) and b == pytest.approx(50.0)
    acct.rebalance({'v': 1.0}, {'v': 0.1})                    # add back: basis rises with the deposit
    e, b, _ = acct.pos['v']
    assert e - b == pytest.approx(10.0) and acct.nav() == pytest.approx(nav)


def test_cash_earns_the_given_rate_and_rebalancing_between_vaults():
    acct = H.FollowerAccount(1.0)
    acct.rebalance({'a': 0.5, 'b': 0.5}, {'a': 0.1, 'b': 0.0})
    acct.grow({'a': 0.10, 'b': 0.10})
    assert acct.nav() == pytest.approx(0.5 * 1.1 - 0.1 * 0.05 + 0.55)
    acct.rebalance({'b': 1.0}, {'b': 0.0})
    assert 'a' not in acct.pos and acct.cash == pytest.approx(0.0, abs=1e-12)
    a2 = H.FollowerAccount(1.0)
    a2.rebalance({}, {})
    a2.grow({}, cash_return=0.01)
    assert a2.nav() == pytest.approx(1.01)


# ---------------------------------------------------------------------------------------------- benchmark, stats

def test_savings_accrual_splits_calendar_years():
    one = H.savings_accrual(ms('2024-12-01'), ms('2025-01-01'))
    assert one == pytest.approx(0.078 * 31 / 365)
    two = H.savings_accrual(ms('2024-12-16'), ms('2025-01-16'))
    assert two == pytest.approx(0.078 * 16 / 365 + 0.055 * 15 / 365)
    assert H.savings_accrual(ms('2026-01-01'), ms('2026-02-01'), const=0.038) == pytest.approx(0.038 * 31 / 365)


def test_spearman_and_ols():
    assert H.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert H.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert H.spearman([1, 1, 2, 2], [1, 2, 3, 4]) == pytest.approx(0.894427, abs=1e-5)
    xs = [0.1 * i for i in range(20)]
    res = H.ols_hac([1 + 2 * x for x in xs], [[1.0, x] for x in xs])
    assert res['coef'][0] == pytest.approx(1.0) and res['coef'][1] == pytest.approx(2.0) and res['r2'] == pytest.approx(1.0)


def test_run_strategy_end_to_end_on_a_synthetic_panel():
    months = [ms('2025-01-01'), ms('2025-02-01')]

    def row(sig, fwd, size=2e5):
        return {'sig': {k: sig for k in H.SIGNALS}, 'size': size, 'fwd': fwd, 'fwd_late': fwd, 'win': None,
                'btc': 0.0, 'hype': None, 'elig': {'u10k': True, 'u100k': True}, 'closed_now': False,
                'closed_in': False, 'lc': 0.1, 'flagged': [], 'tier': 'core', 'allow_now': True, 'delay_days': 0}

    panel = {months[0]: {'a': row(1.0, 0.10), 'b': row(0.0, -0.05)},
             months[1]: {'a': row(1.0, 0.0), 'b': row(0.0, 0.0)}}
    recs = H.run_strategy(panel, months, 'u100k', 'ret3', 0.5, 'ew')
    assert recs[0]['n_selected'] == 1 and recs[0]['top'] == ['a']
    assert recs[0]['gross'] == pytest.approx(0.10)
    assert recs[0]['net'] == pytest.approx(0.09)                # 10% of the 10% gain is owed
    market = H.run_strategy(panel, months, 'u100k')
    assert market[0]['gross'] == pytest.approx(0.025)


def test_precommit_hash_is_stable():
    assert H.precommit_hash() == H.precommit_hash(copy.deepcopy(H.PRECOMMIT))
    assert H.PRECOMMIT['n_variants'] == len(list(H.variant_names())) == 56
