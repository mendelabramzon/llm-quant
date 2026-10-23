"""Tests for the money-deciding pure functions of pm_rewards_mm (reward scoring, fills, rebates, holding, Kalshi LIP)."""
import math

import pytest

import pm_rewards_mm as M


class TestOrderScore:
    def test_docs_worked_example_first_side(self):
        # docs.polymarket.com/programs/liquidity-rewards, step 2: mid 0.50, v = 3c
        q = (M.order_score(3, 1) * 100 + M.order_score(3, 2) * 200 + M.order_score(3, 1) * 100)
        assert q == pytest.approx((2 / 3) ** 2 * 100 + (1 / 3) ** 2 * 200 + (2 / 3) ** 2 * 100)

    def test_at_mid_scores_full_and_at_max_spread_scores_zero(self):
        assert M.order_score(3, 0) == 1.0
        assert M.order_score(3, 3) == 0.0
        assert M.order_score(3, 4) == 0.0

    def test_multiplier_and_bad_inputs(self):
        assert M.order_score(4, 2, b=2.0) == pytest.approx(0.5)
        assert M.order_score(0, 0) == 0.0
        assert M.order_score(None, 1) == 0.0
        assert M.order_score(3, -0.5) == 0.0          # a bid above the midpoint cannot be resting
        assert M.order_score(3, -1e-12) == 1.0         # rounding noise at the midpoint


class TestMidAndSides:
    def test_adjusted_mid_ignores_small_levels(self):
        bids = [(0.49, 5), (0.48, 500)]
        asks = [(0.51, 500)]
        assert M.adjusted_mid(bids, asks, 100) == pytest.approx((0.48 + 0.51) / 2)
        assert M.adjusted_mid(bids, asks, 1) == pytest.approx(0.50)

    def test_adjusted_mid_falls_back_to_raw_touch(self):
        assert M.adjusted_mid([(0.40, 5)], [(0.60, 5)], 100) == pytest.approx(0.50)
        assert M.adjusted_mid([], [(0.6, 5)], 1) is None

    def test_side_scores_respect_min_size_and_max_spread(self):
        bids = [(0.49, 100), (0.48, 50), (0.45, 1000)]
        asks = [(0.51, 200)]
        q1, q2 = M.side_scores(bids, asks, 0.50, 3, 100)
        assert q1 == pytest.approx((2 / 3) ** 2 * 100)      # 0.48 below min size, 0.45 outside v
        assert q2 == pytest.approx((2 / 3) ** 2 * 200)

    def test_q_min_single_sided_rule(self):
        assert M.q_min(90, 0, 0.5) == pytest.approx(30)     # in [0.10, 0.90]: one side scores 1/c
        assert M.q_min(90, 0, 0.95) == 0                    # outside: two-sided only
        assert M.q_min(90, 60, 0.5) == 60
        assert M.q_min(90, 20, 0.5) == pytest.approx(30)
        assert M.q_min(90, 60, 0.05) == 60

    def test_competitor_bounds_bracket_any_split(self):
        # two makers, (60, 10) and (0, 50): totals (60, 60); true sum = max(10, 20) + 50/3
        true = M.q_min(60, 10, 0.5) + M.q_min(0, 50, 0.5)
        b = M.competitor_bounds(60, 60, 0.5)
        assert b['lower'] <= true <= b['upper']
        assert b['upper'] == 60
        b2 = M.competitor_bounds(90, 30, 0.95)
        assert b2 == {'upper': 30, 'lower': 0.0}

    def test_reward_share(self):
        assert M.reward_share(10, 90) == pytest.approx(0.1)
        assert M.reward_share(0, 90) == 0.0
        assert M.reward_share(10, 0) == 1.0


class TestQuotes:
    def test_quote_prices_on_grid_and_post_only(self):
        assert M.quote_prices(0.815, 0.5, 0.01) == (0.81, 0.82)
        assert M.quote_prices(0.50, 1.0, 0.01) == (0.49, 0.51)
        # a distance of zero at a half-tick midpoint lands on the touch, never through it
        assert M.quote_prices(0.505, 0.0, 0.01, best_bid=0.50, best_ask=0.51) == (0.50, 0.51)
        # tenth-cent tick
        bid, ask = M.quote_prices(0.0365, 0.5, 0.001)
        assert bid == pytest.approx(0.031) and ask == pytest.approx(0.042)

    def test_quote_prices_never_cross(self):
        bid, ask = M.quote_prices(0.50, 0.0, 0.01, best_bid=0.49, best_ask=0.50)
        assert bid <= 0.49 + 1e-9 and ask >= 0.50 - 1e-9

    def test_quote_capital(self):
        assert M.quote_capital(100, 0.49, 0.51) == pytest.approx(98.0)


class TestMoney:
    def test_maker_rebate_matches_fee_curve(self):
        # politics: feeRate 0.04, 25% rebate; 100 shares at 0.50 -> fee-equivalent $1.00, rebate $0.25
        assert M.maker_rebate(100, 0.5, 0.04, 0.25) == pytest.approx(0.25)
        assert M.maker_rebate(100, 0.5, 0.0, 0.25) == 0.0

    def test_rebate_rate_for(self):
        assert M.rebate_rate_for('crypto', 0.07) == 0.20
        assert M.rebate_rate_for('sports', 0.05) == 0.15
        assert M.rebate_rate_for('politics', 0.04) == 0.25
        assert M.rebate_rate_for('geopolitics', 0.0) == 0.0

    def test_holding_reward_docs_example(self):
        # help article: 30,000 Yes at $0.53 and 10,000 No at $0.45 is $20,400, ~$0.075697 an hour at 3.25%
        v = M.holding_reward(30000, 10000, 0.53, 1.0)
        assert 30000 * 0.53 + 10000 * 0.47 == pytest.approx(20600)   # mids of a coherent book sum to 1
        assert M.holding_reward(30000, 0, 0.53, 1.0) + M.holding_reward(0, 10000, 0.55, 1.0) == \
            pytest.approx(20400 * 0.0325 / 8760)
        assert v > 0

    def test_complete_set_earns_holding_on_one_dollar(self):
        assert M.holding_reward(1, 1, 0.3, 8760) == pytest.approx(0.0325)


class TestFills:
    def test_to_yes_terms(self):
        assert M.to_yes_terms(0.19, 'BUY', 1) == (pytest.approx(0.81), 'SELL')
        assert M.to_yes_terms(0.81, 'SELL', 0) == (0.81, 'SELL')

    def test_through_fill_needs_strictly_through_print(self):
        assert M.through_fill(0.50, 'bid', 0.50, 'SELL', 100, 50) == 0.0     # at the level: queue, no fill
        assert M.through_fill(0.50, 'bid', 0.49, 'SELL', 100, 50) == 50      # through: fill to remaining
        assert M.through_fill(0.50, 'bid', 0.49, 'BUY', 100, 50) == 0.0      # wrong taker side
        assert M.through_fill(0.52, 'ask', 0.53, 'BUY', 20, 50) == 20
        assert M.through_fill(0.52, 'ask', 0.53, 'BUY', 20, 0) == 0.0


class TestKalshiLIP:
    def test_reference_price_and_discount(self):
        levels = [(0.50, 100), (0.49, 100), (0.48, 300), (0.47, 1000)]
        sc, reached = M.lip_side_scores(levels, target=500, discount=0.5)
        # target/5 = 100 reached at 0.50 -> reference 0.50; the walk stops once 500 is reached (at 0.48)
        assert reached
        assert sc == [100, 50, 300 * 0.25, 0.0]

    def test_target_not_reached(self):
        sc, reached = M.lip_side_scores([(0.5, 10)], target=500, discount=0.5)
        assert not reached and sc == [10]

    def test_marginal_share(self):
        assert M.lip_marginal_share(100, 300) == pytest.approx(0.25)
        assert M.lip_marginal_share(100, 300, discount=0.5, ticks_beyond_ref=1) == pytest.approx(50 / 350)


def test_kalshi_fee_import_is_the_crossvenue_one():
    assert M.kalshi_fee(100, 0.5) == pytest.approx(1.75)
    assert math.isclose(M.kalshi_fee(1, 0.5), 0.02)


class TestSimulation:
    R = {'v': 3.0, 'tick': 0.01, 'min_size': 10.0, 'rate': 24.0, 'fee_cat': 'politics', 'fee_rate': 0.04,
         'holding': False}

    def data(self, trades, mids):
        hours = sorted(mids)
        by_h = {}
        for t in trades:
            by_h.setdefault(int(t[0] // 3600) * 3600, []).append(t)
        return {'trades_by_hour': by_h, 'mids': mids, 'hours': hours}

    def test_no_trades_earns_reward_share_only(self):
        h = 3600 * 100
        d = self.data([], {h: 0.50, h + 3600: 0.50})
        res = M.simulate_market(self.R, d, comp_upper=0.0, frac=1 / 3, size_mult=1, vol_screen=False)
        pnl, cap, parts = res[h]
        # alone in the book: the whole hourly pool, 24/24 = $1
        assert parts['reward'] == pytest.approx(1.0)
        assert pnl == pytest.approx(1.0)
        assert cap == pytest.approx(10.0)

    def test_through_print_fills_and_marks_to_next_mid(self):
        h = 3600 * 100
        # quote at 1c from 0.50 -> bid 0.49 / ask 0.51; a taker sells 4 YES at 0.48 halfway through the hour
        d = self.data([(h + 1800, 0.48, 'SELL', 4.0)], {h: 0.50, h + 3600: 0.45})
        res = M.simulate_market(dict(self.R, rate=0.0), d, comp_upper=100.0, frac=1 / 3, size_mult=1,
                                vol_screen=False)
        pnl, cap, parts = res[h]
        assert parts['spread'] == pytest.approx(4 * 0.01)
        assert parts['rebate'] == pytest.approx(M.maker_rebate(4, 0.49, 0.04, 0.25))
        # bought 4 at 0.49, marked at 0.45
        assert pnl == pytest.approx(4 * (0.45 - 0.49) + parts['rebate'])

    def test_print_at_the_quote_does_not_fill(self):
        h = 3600 * 100
        d = self.data([(h + 10, 0.49, 'SELL', 50.0)], {h: 0.50, h + 3600: 0.40})
        res = M.simulate_market(dict(self.R, rate=0.0), d, comp_upper=1.0, frac=1 / 3, size_mult=1, vol_screen=False)
        assert res[h][0] == pytest.approx(0.0)

    def test_stale_quote_uses_previous_mid(self):
        h = 3600 * 100
        d = self.data([(h + 10, 0.55, 'BUY', 5.0)], {h - 3600: 0.50, h: 0.60, h + 3600: 0.60})
        # stale quote centred on 0.50 -> ask 0.51; a taker buying at 0.55 trades through it
        res = M.simulate_market(dict(self.R, rate=0.0), d, comp_upper=1.0, frac=1 / 3, size_mult=1,
                                vol_screen=False, stale=1)
        assert res[h][0] == pytest.approx(5 * (0.51 - 0.60) + M.maker_rebate(5, 0.51, 0.04, 0.25))


class TestKalshiSim:
    def test_reward_and_fill(self):
        h = 3600 * 200
        km = {'candles': [[h, 0.40, 0.42], [h + 3600, 0.40, 0.42]],
              'trades': [[h + 600, 0.39, 'no', 50.0]]}
        res = M.simulate_kalshi(km, usd_day=24.0, R_y=100.0, R_n=100.0, eligible=True, q=100, vol_screen=False)
        pnl, cap, parts = res[h]
        # YES bid share 1/2 until the fill at 10 min (then 50/150), NO side 1/2 all hour
        exp = (10 / 60) * (0.5 + 0.5) / 2 + (50 / 60) * (50 / 150 + 0.5) / 2
        assert parts['reward'] == pytest.approx(exp)
        assert parts['spread'] == pytest.approx(50 * (0.41 - 0.40))
        assert pnl == pytest.approx(exp + 50 * (0.41 - 0.40))

    def test_not_eligible_earns_nothing(self):
        h = 3600 * 200
        km = {'candles': [[h, 0.40, 0.42]], 'trades': []}
        res = M.simulate_kalshi(km, 24.0, 100.0, 100.0, False, 100, False)
        assert res[h][2]['reward'] == 0.0


def test_maker_fill_time():
    ser = [[10, 0.95], [20, 0.94], [30, 0.92], [40, 0.97]]
    assert M.maker_fill_time(ser, 10, 100, bid=0.94, hs=0.01) == 30
    assert M.maker_fill_time(ser, 10, 25, bid=0.94, hs=0.01) is None


def test_greedy_allocation_takes_best_marginal_first():
    rows = {'a': {'v': 3.0, 'min_size': 10.0, 'rate': 10.0}, 'b': {'v': 3.0, 'min_size': 10.0, 'rate': 1.0}}
    mk = {'a': {'comp_upper': 1000.0, 'joinable_share': 1.0, 'hs_cents': 0.0},
          'b': {'comp_upper': 1000.0, 'joinable_share': 1.0, 'hs_cents': 0.0}}
    out = M.greedy_allocation(mk, rows, '0.00', budgets=(500.0,), step=500.0)
    # first step goes to market a: 10 x 500/(500+1000)
    assert out['500']['usd_day'] == pytest.approx(10 * 500 / 1500)
    assert out['500']['markets'] == 1
