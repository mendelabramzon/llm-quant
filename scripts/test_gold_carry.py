"""Tests for gold_carry.py: the carry with explicit capital, premium marking, funding annualisation per venue convention,
and rule selection without look-ahead.

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_gold_carry.py -q
"""
import datetime as dt
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gold_carry as G  # noqa: E402

DAY = G.DAY_MS
HOUR = G.HOUR_MS


def ms(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


# ---------------------------------------------------------------------------------------------- funding conventions

@pytest.mark.parametrize('hours', [1, 4, 8])
def test_funding_apr_matches_per_settlement_convention(hours):
    """A constant rate r per settlement, paid every h hours for a year, annualises to r x 8760 / h whatever the venue's
    interval (Hyperliquid 1 h, Binance/Bybit 4 h, OKX 8 h)."""
    r = 1e-5
    t0 = ms('2026-01-01 00:00')
    ev = [(t0 + k * hours * HOUR, r) for k in range(1, 8760 // hours + 1)]
    assert G.settlement_hours(ev) == hours
    want = r * 8760.0 / hours
    assert G.funding_apr(ev) == pytest.approx(want, rel=1e-3)
    assert G.apr_per_settlement(r, hours) == pytest.approx(want)


def test_daily_funding_window_is_left_open_right_closed():
    """A settlement stamped at d+1 00:00 (a few ms late) pays for day d; one at 00:00 of d belongs to d-1."""
    d = ms('2026-03-10 00:00') // DAY
    ev = [(d * DAY + 3, 1.0), ((d + 1) * DAY + 5, 2.0), (d * DAY + 4 * HOUR + 2, 4.0)]
    f, n = G.daily_funding(ev)
    assert f[d - 1] == 1.0
    assert f[d] == 6.0 and n[d] == 2


def test_daily_funding_cuts_after_delisting():
    t0 = ms('2026-06-16 00:00')
    ev = [(t0 + k * HOUR, 1e-5) for k in range(1, 48)]
    f, _ = G.daily_funding(ev, t_max=t0 + 10 * HOUR)
    assert sum(f.values()) == pytest.approx(10 * 1e-5)


def test_hl_formula_reproduces_floor_and_clamp():
    # Inside the band the interest leg is paid: 0.01%/8h x multiplier.
    assert G.hl_formula(0.0, 1.0, 0.0001, 0.0005) == pytest.approx(1.25e-5)
    assert G.hl_formula(0.0001, 0.5, 0.0001, 0.0003) == pytest.approx(6.25e-6)
    # Far above the band the premium passes through, less the band.
    assert G.hl_formula(0.002, 1.0, 0.0001, 0.0005) == pytest.approx((0.002 - 0.0005) / 8)


# ---------------------------------------------------------------------------------------------- premium marking

def test_day_return_equals_fixed_quantity_pnl():
    """(F/F_prev) b - b_prev is exactly the P&L of q ounces long token / short perp per unit of opening notional."""
    F0, F1, T0, T1 = 4000.0, 4200.0, 4004.0, 4195.0       # gold +5%, token premium +10bp -> -11.9bp
    q = 1.0
    pnl = q * ((T1 - T0) - (F1 - F0))
    b0, b1 = T0 / F0 - 1.0, T1 / F1 - 1.0
    assert G.day_return(F0, F1, b0, b1, 0.0) == pytest.approx(pnl / (q * F0), rel=1e-12)


def _leg(days, F, T, f, cost_perp=0.0, cost_token=0.0, mm=0.01, hourly=False):
    return {'F': F, 'T': T, 'f': f, 'hi': {}, 'days': days, 'cost_perp': cost_perp, 'cost_token': cost_token,
            'mm': mm, 'hourly': hourly}


def test_token_premium_change_is_marked_and_gold_move_cancels():
    """Zero funding; gold rises 10% while the token goes from +10bp to -10bp over spot: the hedge loses about 20bp of
    notional (plus the tiny cross term), whatever gold did."""
    d0 = 20000
    days = list(range(d0, d0 + 10))
    F = {d: 4000.0 * (1.0 + 0.01 * (d - d0 + 1)) for d in range(d0 - 1, d0 + 10)}
    prem = {d: 0.001 - 0.0002 * (d - d0 + 1) for d in range(d0 - 1, d0 + 10)}
    T = {d: F[d] * (1.0 + prem[d]) for d in F}
    f = {d: 0.0 for d in days}
    ex, _, st = G.simulate(days, {'v': _leg(days, F, T, f)}, G.RULES[0], 'collateral', lambda d: 0.0)
    total = sum(ex)
    assert total == pytest.approx(prem[days[-1]] - prem[d0 - 1], abs=2e-5)
    assert st['entries'] == 1


# ---------------------------------------------------------------------------------------------- capital

@pytest.mark.parametrize('model,mm,K', [('collateral', 0.05, 1.0), ('cash10', 0.02, 1.12), ('cash20', 0.05, 1.25)])
def test_capital_per_notional(model, mm, K):
    assert G.capital_per_notional(model, mm) == pytest.approx(K)


@pytest.mark.parametrize('model', ['collateral', 'cash10', 'cash20'])
def test_constant_funding_excess_on_capital(model):
    """Flat prices, constant funding f a day, no costs: the excess is f x 365 / K - SSR, on the capital K."""
    d0 = 20000
    days = list(range(d0, d0 + 365))
    F = {d: 4000.0 for d in range(d0 - 1, d0 + 365)}
    T = dict(F)
    fday = 0.08 / 365.0
    f = {d: fday for d in days}
    leg = _leg(days, F, T, f, mm=0.02)
    ex, _, _ = G.simulate(days, {'v': leg}, G.RULES[0], model, G.bench_const)
    K = G.capital_per_notional(model, 0.02)
    assert sum(ex) == pytest.approx(0.08 / K - G.SSR, rel=1e-9)


def test_costs_entry_exit_and_rebalance():
    """Entry and exit pay one side of both legs each; a 6% move with cash10 (rebalance at 5%) pays 6% of a side."""
    d0 = 20000
    days = list(range(d0, d0 + 3))
    F = {d0 - 1: 4000.0, d0: 4000.0, d0 + 1: 4240.0, d0 + 2: 4240.0}
    T = dict(F)
    f = {d: 0.0 for d in days}
    ct, cp = 0.001, 0.0005
    leg = _leg(days, F, T, f, cost_perp=cp, cost_token=ct, mm=0.02)
    ex, _, st = G.simulate(days, {'v': leg}, G.RULES[0], 'cash10', lambda d: 0.0)
    K = G.capital_per_notional('cash10', 0.02)
    assert st['rebalances'] == 1
    assert sum(ex) * K == pytest.approx(-(2 * (ct + cp) + 0.06 * (ct + cp)), rel=1e-9)


def test_late_hours_only_hit_hourly_venues():
    d0 = 20000
    days = list(range(d0, d0 + 2))
    F = {d: 4000.0 for d in range(d0 - 1, d0 + 2)}
    f = {d: 0.0024 for d in days}
    for hourly, want in ((True, 0.0024 * (1 - 1 / 24.0) + 0.0024), (False, 0.0048)):
        leg = _leg(days, F, dict(F), f, hourly=hourly)
        ex, _, _ = G.simulate(days, {'v': leg}, G.RULES[0], 'collateral', lambda d: 0.0, late_hours=1.0)
        assert sum(ex) == pytest.approx(want)


# ---------------------------------------------------------------------------------------------- no look-ahead

def test_trailing_apr_uses_only_past_days():
    f = {d: 0.001 for d in range(100)}
    base = G.trailing_apr(f, 50, 7)
    f2 = dict(f)
    for d in range(50, 100):
        f2[d] = 10.0                                 # the decision day and the future are irrelevant
    assert G.trailing_apr(f2, 50, 7) == base == pytest.approx(0.365)


def test_threshold_rule_decision_ignores_the_day_it_acts_on():
    d0 = 1000
    days = list(range(d0, d0 + 60))
    F = {d: 4000.0 for d in range(d0 - 1, d0 + 60)}
    f = {d: (0.20 / 365.0 if d < d0 + 30 else 0.0) for d in range(d0 - 40, d0 + 60)}
    leg = _leg(days, F, dict(F), f)
    rule = next(r for r in G.RULES if r['name'] == 'trail7d_x2pp')
    _, flags, _ = G.simulate(days, {'v': leg}, rule, 'collateral', G.bench_const)
    i = days.index(d0 + 30)
    assert flags[i]                                  # day d0+30 pays nothing, but nobody could know at 00:00
    f2 = dict(f)
    f2[d0 + 30] = -1.0
    leg2 = _leg(days, F, dict(F), f2)
    _, flags2, _ = G.simulate(days, {'v': leg2}, rule, 'collateral', G.bench_const)
    assert flags2[:i + 1] == flags[:i + 1]


def test_delay_shifts_decisions():
    d0 = 1000
    days = list(range(d0, d0 + 40))
    F = {d: 4000.0 for d in range(d0 - 1, d0 + 40)}
    f = {d: (0.0 if d < d0 + 10 else 0.30 / 365.0) for d in range(d0 - 40, d0 + 40)}
    leg = _leg(days, F, dict(F), f)
    rule = next(r for r in G.RULES if r['name'] == 'trail7d_x0pp')
    _, a, _ = G.simulate(days, {'v': leg}, rule, 'collateral', G.bench_const)
    _, b, _ = G.simulate(days, {'v': leg}, rule, 'collateral', G.bench_const, delay=1)
    assert a.index(True) + 1 == b.index(True)


def test_best_venue_schedule_has_no_look_ahead():
    days = list(range(19700, 19800))
    fa = {d: 0.0003 for d in range(19600, 19800)}
    fb = {d: 0.0001 for d in range(19600, 19800)}
    s1 = G.best_venue_schedule({'a': fa, 'b': fb}, days)
    fb2 = dict(fb)
    for d in range(19760, 19800):
        fb2[d] = 1.0
    s2 = G.best_venue_schedule({'a': fa, 'b': fb2}, days)
    assert all(s1[d] == s2[d] for d in days if d < 19760)


def test_choose_then_test_picks_on_first_half_only():
    """The harness's choice must not move when only the test half changes."""
    n = 200
    good_is = [0.001] * 100 + [-0.001] * 100
    bad_is = [-0.001] * 100 + [0.002] * 100
    noise = [((i * 7919) % 13 - 6) * 1e-5 for i in range(n)]
    v1 = {'a': [x + e for x, e in zip(good_is, noise)], 'b': [x + e for x, e in zip(bad_is, noise)]}
    assert G.B.choose_then_test(v1, frac=0.5, periods_per_year=365)['chosen'] == 'a'
    v2 = {'a': v1['a'][:100] + [-0.01] * 100, 'b': v1['b']}
    assert G.B.choose_then_test(v2, frac=0.5, periods_per_year=365)['chosen'] == 'a'


# ---------------------------------------------------------------------------------------------- calendars and data

def test_spot_open_calendar():
    assert not G.spot_open(ms('2026-10-10 12:00'))           # Saturday
    assert not G.spot_open(ms('2026-10-11 21:00'))           # Sunday 17:00 ET
    assert G.spot_open(ms('2026-10-11 22:00'))               # Sunday 18:00 ET (EDT)
    assert not G.spot_open(ms('2026-10-09 21:00'))           # Friday 17:00 ET
    assert not G.spot_open(ms('2026-10-07 21:00'))           # the daily 17:00-18:00 ET break
    assert G.spot_open(ms('2026-10-07 14:00'))


@pytest.mark.parametrize('when,contract', [('2026-01-27 15:00', '2026-02'), ('2026-01-28 15:00', '2026-04'),
                                           ('2026-07-28 15:00', '2026-08'), ('2026-07-29 15:00', '2026-12'),
                                           ('2026-10-09 15:00', '2026-12'), ('2025-11-26 15:00', '2026-02')])
def test_contract_for_matches_observed_gc_rolls(when, contract):
    assert G.contract_for(ms(when))[0] == contract


def test_closes_from_drops_zero_volume_trade_bars_only():
    rows = [[0, 1, 2, 0.5, 1.5, 0.0], [HOUR, 1, 2, 0.5, 1.6, 10.0]]
    c, _ = G.closes_from(rows, 'trade')
    assert list(c) == [2 * HOUR]
    c2, _ = G.closes_from(rows, 'index')
    assert list(c2) == [HOUR, 2 * HOUR]
    hl = [{'t': 0, 'c': '5', 'h': '6', 'v': '0.0'}, {'t': HOUR, 'c': '5.1', 'h': '6', 'v': '3'}]
    c3, _ = G.closes_from(hl, 'trade')
    assert c3 == {2 * HOUR: 5.1}


def test_depth_and_walk_cost():
    asks = [(100.0, 10.0), (100.2, 10.0), (101.0, 100.0)]
    assert G.depth_usd(asks, 100.0, 25) == pytest.approx(100.0 * 10 + 100.2 * 10)
    assert G.walk_cost(asks, 100.0, 1000.0) == pytest.approx(0.0)
    assert G.walk_cost(asks, 100.0, 2002.0) == pytest.approx(1002.0 * 20.0 / 2002.0)
    assert G.walk_cost(asks, 100.0, 1e9) is None


def test_premium_cross_term_is_small():
    """The cross term (F/F_prev - 1) b is second order: a 2% day with a 30bp premium moves the mark by 0.6bp."""
    b = 0.003
    assert abs(G.day_return(1.0, 1.02, b, b, 0.0) - 0.0) == pytest.approx(0.02 * b)
    assert math.isclose(G.day_return(1.0, 1.0, b, b, 0.0), 0.0)
