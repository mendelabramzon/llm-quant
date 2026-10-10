"""Core math of nav_wrappers: look-through NAV with debt / preferred / convertibles, the three mNAV ratios, hedge
accounting of a discount trade, split bases of restated XBRL comparatives, fee interpolation, the XBRL capital rule,
event windows and the trust rule's entry/exit logic. Synthetic data only; no network."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nav_wrappers as N  # noqa: E402


# ---------------------------------------------------------------- look-through NAV and the three ratios

def test_lookthrough_nav_subtracts_debt_and_preferred():
    nav, ds, eq = N.lookthrough_nav(coins=100.0, price=50_000.0, cash=1e6, debt=2e6, pref=1e6, shares=1e6)
    assert eq == pytest.approx(5e6 + 1e6 - 2e6 - 1e6)
    assert ds == 1e6
    assert nav == pytest.approx(3.0)


def test_convertible_is_debt_out_of_the_money_and_shares_in_the_money():
    # $10M face converting at $20/share
    nav_otm, ds_otm, _ = N.lookthrough_nav(1000.0, 10_000.0, shares=1e6, converts=[(10e6, 20.0)], stock_price=15.0)
    assert ds_otm == 1e6
    assert nav_otm == pytest.approx((10e6 - 10e6) / 1e6)
    nav_itm, ds_itm, _ = N.lookthrough_nav(1000.0, 10_000.0, shares=1e6, converts=[(10e6, 20.0)], stock_price=25.0)
    assert ds_itm == pytest.approx(1e6 + 10e6 / 20.0)
    assert nav_itm == pytest.approx(10e6 / 1.5e6)
    # never both: debt removed when converted
    assert nav_itm > nav_otm


def test_mnav_variants_mstr_like_gap():
    # coins worth 70, market cap 65, debt 6.7, preferred 13.9, cash 5.7 (in $B, per share basis 1 share)
    v = N.mnav_variants(price=65.0, shares=1.0, coins=1.0, coin_price=70.0, cash=5.7, debt=6.7, pref=13.9)
    assert v['naive'] == pytest.approx(65 / 70)
    assert v['ev'] == pytest.approx((65 + 6.7 + 13.9 - 5.7) / 70)
    assert v['true'] == pytest.approx(65 / (70 + 5.7 - 6.7 - 13.9))
    assert v['naive'] < 1 < v['true']                 # a dashboard "discount" that is a premium


def test_mnav_negative_equity_flagged():
    v = N.mnav_variants(price=1.0, shares=1.0, coins=1.0, coin_price=10.0, debt=12.0)
    assert v['negative_equity'] and v['true'] is None


# ---------------------------------------------------------------- hedge accounting

def _flat_funding(n):
    return [0.0] * n


def test_nav_hedge_captures_discount_at_convergence_with_flat_coin():
    prices = [70.0, 100.0]              # trust closes from a 30% discount to NAV
    coin = [100.0, 100.0]
    cps = [1.0, 1.0]
    r = N.hedged_path(prices, coin, cps, _flat_funding(2), 0, 1, margin=1 / 3, perp_fee=0.0)
    n0 = (1 / 70.0) * 1.0 * 100.0      # coin notional short per $ of trust
    assert r['capital'] == pytest.approx(1 + n0 / 3)
    assert r['total'] == pytest.approx((100 / 70 - 1) / r['capital'])


def test_nav_hedge_is_net_short_the_discount_while_it_persists():
    # constant 30% discount, coin +50%: NAV hedge P&L = d1 * coin return / (1 + d0) per $ of trust
    prices = [70.0, 105.0]
    coin = [100.0, 150.0]
    r = N.hedged_path(prices, coin, [1.0, 1.0], _flat_funding(2), 0, 1, margin=0.0, perp_fee=0.0)
    assert r['total'] == pytest.approx((-0.30 * 0.5) / 0.70)
    # dollar hedge (hedge units = price / coin price) is flat when the discount is constant
    hu = [p / c for p, c in zip(prices, coin)]
    r2 = N.hedged_path(prices, coin, hu, _flat_funding(2), 0, 1, margin=0.0, perp_fee=0.0)
    assert r2['total'] == pytest.approx(0.0, abs=1e-12)


def test_short_receives_positive_funding_and_pays_costs():
    prices, coin, cps = [100.0, 100.0], [100.0, 100.0], [1.0, 1.0]
    r = N.hedged_path(prices, coin, cps, [0.0, 0.001], 0, 1, margin=0.0, cost_in=0.01, cost_out=0.01, perp_fee=0.0005)
    # +0.1% funding on $1 short, minus 1% + 1% wrapper costs, minus 2 x 5bp perp
    assert r['total'] == pytest.approx(0.001 - 0.01 - 0.01 - 0.0005 - 0.0005)


def test_distribution_is_credited_to_the_holder():
    # a 10% coin distribution: price and coin per share drop 10%, holder receives the coin value
    prices, coin, cps = [100.0, 90.0], [100.0, 100.0], [1.0, 0.9]
    r = N.hedged_path(prices, coin, cps, [0.0, 0.0], 0, 1, margin=0.0, perp_fee=0.0, dist=[0.0, 10.0])
    assert r['total'] == pytest.approx(0.0, abs=1e-12)


def test_excess_over_savings_rate_uses_calendar_gap():
    prices, coin = [100.0, 100.0, 100.0], [1.0, 1.0, 1.0]
    dates = ['2024-01-05', '2024-01-08', '2024-01-09']        # Friday -> Monday is 3 days
    r = N.hedged_path(prices, coin, [0.0] * 3, [0.0] * 3, 0, 2, margin=0.0, perp_fee=0.0,
                      ssr=lambda d: 0.0365, dates=dates)
    assert r['excess_total'] == pytest.approx(-0.0365 * 4 / 365.0)


# ---------------------------------------------------------------- split bases, fees, interpolation

def test_split_factor_after():
    splits = [('2018-01-29', 91.0), ('2026-02-06', 0.05)]
    assert N.split_factor_after('2017-12-31', splits) == pytest.approx(91 * 0.05)
    assert N.split_factor_after('2020-01-01', splits) == pytest.approx(0.05)
    assert N.split_factor_after('2026-03-01', splits) == 1.0


def test_fix_split_basis_handles_restated_comparatives():
    # latest filing after the split: values already post-split; an old period restated (post-split) and one
    # original pre-split value both resolve to the same continuous path
    fee = 0.02
    true_cps = lambda days_back: 0.001 * math.exp(fee * days_back / 365.25)
    raw = [('2017-09-30', true_cps(1000) * 91, '2017-11-01'),      # original pre-split filing
           ('2017-12-31', true_cps(900), '2021-03-05'),            # restated in a later filing
           ('2020-06-30', true_cps(0), '2020-08-07')]
    fixed = N.fix_split_basis([(a, v, f) for a, v, f in raw], [('2018-01-29', 91.0)], fee)
    assert fixed[0][1] == pytest.approx(true_cps(1000))
    assert fixed[1][1] == pytest.approx(true_cps(900))
    assert fixed[2][1] == pytest.approx(true_cps(0))


def test_interp_log_between_and_beyond_anchors():
    anchors = [('2024-01-01', 1.0), ('2025-01-01', 0.98)]
    mid = N.interp_log(anchors, '2024-07-01', 0.02)
    assert 0.98 < mid < 1.0
    assert N.interp_log(anchors, '2026-01-01', 0.02) == pytest.approx(0.98 * math.exp(-0.02 * 365 / 365.25))
    assert N.interp_log(anchors, '2023-01-01', 0.02) == pytest.approx(1.0 * math.exp(0.02 * 365 / 365.25))


# ---------------------------------------------------------------- XBRL rules

def test_capital_rule_takes_largest_total_debt_not_the_sum():
    end = '2026-06-30'
    tv = {'LongTermDebt': {end: {'val': 100.0}},
          'LongTermDebtNoncurrent': {end: {'val': 60.0}}, 'LongTermDebtCurrent': {end: {'val': 40.0}},
          'ConvertibleLongTermNotesPayable': {end: {'val': 90.0}},
          'ShortTermBorrowings': {end: {'val': 5.0}},
          'CashAndCashEquivalentsAtCarryingValue': {end: {'val': 7.0}},
          'TemporaryEquityCarryingAmountAttributableToParent': {end: {'val': 2e6}},
          'PreferredStockValue': {end: {'val': 10.0}}}
    c = N.capital_from_xbrl(None, end, tv)
    assert c['debt'] == pytest.approx(100.0 + 5.0)
    assert c['cash'] == 7.0
    assert c['pref'] == 2e6
    tv2 = {'PreferredStockValue': {end: {'val': 524.0}}}
    assert N.capital_from_xbrl(None, end, tv2)['pref'] == 0.0      # par-value noise ignored


def test_xbrl_original_keeps_the_first_filing_of_each_period():
    facts = {'facts': {'us-gaap': {'X': {'units': {'shares': [
        {'end': '2025-06-30', 'val': 10, 'filed': '2026-02-01', 'form': '10-K'},
        {'end': '2025-06-30', 'val': 200, 'filed': '2025-08-10', 'form': '10-Q'},
        {'end': '2025-06-30', 'start': '2025-04-01', 'val': 1, 'filed': '2025-08-09', 'form': '10-Q'}]}}}}}
    out = N.xbrl_original(facts, 'X')
    assert out['2025-06-30']['val'] == 200


# ---------------------------------------------------------------- event windows and rules

def _series(discs, nav=100.0, coin=100.0):
    rows = []
    for i, d in enumerate(discs):
        date = '2024-01-%02d' % (i + 1)
        rows.append({'date': date, 'close': nav * (1 + d), 'high': nav * (1 + d), 'low': nav * (1 + d),
                     'dollar_volume': 5e7, 'coin_px': coin, 'cps': nav / coin, 'nav': nav, 'disc': d, 'funding': 0.0,
                     'dist_cash': 0.0})
    return {'ticker': 'TST', 'coin': 'BTC', 'rows': rows}


def test_event_trade_windows_and_late_entry():
    ts = _series([-0.30, -0.30, -0.20, -0.10, 0.0])
    base = N.event_trade(ts, '2024-01-01', '2024-01-05', margin=0.0, perp_fee=0.0)
    late = N.event_trade(ts, '2024-01-01', '2024-01-05', margin=0.0, perp_fee=0.0, skip=2)
    assert base['entry'] == '2024-01-01' and base['exit'] == '2024-01-05'
    assert late['entry'] == '2024-01-03'
    # 5bp floor per side on liquid names; the exit cost is charged on the exit notional (1/70 x 100)
    gross = 100 / 70 - 1 - 0.0005 - 0.0005 * 100 / 70
    assert base['return_on_capital'] == pytest.approx(gross, rel=1e-6)
    assert late['return_on_capital'] < base['return_on_capital']


def test_rule_backtest_enters_below_trigger_and_exits_above_half():
    ts = _series([-0.02, -0.12, -0.12, -0.04, -0.04])
    events = [{'ticker': 'TST', 'filing_public': '2024-01-01', 'listed': None}]
    out, log = N.rule_backtest({'TST': ts}, events, 0.10, True, margin=0.0, perp_fee=0.0)
    assert log[0]['entry'] == '2024-01-02' and log[0]['exit'] == '2024-01-04'
    # held over 01-03 (flat) and 01-04 (discount -12% -> -4%): excess on those days, zero elsewhere
    assert out['2024-01-01'] == 0.0 and out['2024-01-05'] == 0.0
    assert out['2024-01-04'] > 0


def test_dat_forward_beta_hedge_is_neutral_at_constant_true_mnav():
    # levered DAT: coins 2 per share, debt 100 per share; true mNAV held at 0.8 while the coin rises 10%
    rows = []
    for k, c in enumerate([100.0, 110.0]):
        nav = 2 * c - 100.0
        rows.append({'date': '2025-12-0%d' % (k + 1), 'price': 0.8 * nav, 'coin_px': c, 'cps': 2.0, 'nav': nav,
                     'funding': 0.0, 'adv_usd': 1e9})
    dd = {'rows': rows}
    r = N.dat_forward(dd, 0, 1, hedge='beta', margin=0.0)
    cost = 2 * (0.0005 + 0.0005 * (200 / 100.0))
    assert r == pytest.approx(-cost - N.ssr_for('2025-12-02') / 365.0, abs=1e-9)
    # the asset hedge is net short (1 - m) of the coin value: it loses when the coin rises
    ra = N.dat_forward(dd, 0, 1, hedge='asset', margin=0.0)
    assert ra < r


def test_abdi_ranaldo_zero_for_constant_prices():
    assert N.abdi_ranaldo_spread([10.0] * 5, [10.0] * 5, [10.0] * 5) == 0.0
