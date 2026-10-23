#!/usr/bin/env python3
"""Tests for pm_wallet_skill.py on synthetic inputs: trade signing (a SELL is a purchase of the complement), payouts
and edge per dollar, the market-clustered ratio t, Spearman, buy-episode merging, the follower's entry cost, exit
proceeds and return (half-spread and the p(1-p) taker fee), hourly entry marks without look-ahead, the wallet-exit
rule (skip when the wallet is already out, exit at the mark after its sale), daily P&L series, band folding and the
book-side depth of the complement.

    uv run --with pytest --with pycryptodome python -m pytest scripts/test_pm_wallet_skill.py -q
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_wallet_skill as W  # noqa: E402

HOUR, DAY = W.HOUR, W.DAY


# ---------------------------------------------------------------------------------------------- signing and edge

def test_buy_is_a_purchase_of_the_same_outcome():
    assert W.as_purchase('BUY', 0, 0.3, 100) == (0, 0.3, 100)
    assert W.as_purchase('BUY', 1, 0.8, 5) == (1, 0.8, 5)


def test_sell_is_a_purchase_of_the_complement():
    o, q, s = W.as_purchase('SELL', 0, 0.3, 100)
    assert (o, s) == (1, 100)
    assert q == pytest.approx(0.7)
    o, q, s = W.as_purchase('SELL', 1, 0.95, 10)
    assert o == 0 and q == pytest.approx(0.05)


def test_payout_of_each_outcome():
    assert W.payout_of(0, 1.0) == 1.0 and W.payout_of(1, 1.0) == 0.0
    assert W.payout_of(0, 0.0) == 0.0 and W.payout_of(1, 0.0) == 1.0
    assert W.payout_of(0, 0.5) == 0.5 and W.payout_of(1, 0.5) == 0.5


def test_trade_edge_buy_and_sell_mirror():
    # buying YES at 0.3 when YES wins: +0.7 a share on 0.3 at risk
    e, c = W.trade_edge(*W.as_purchase('BUY', 0, 0.3, 100), payout0=1.0)
    assert e == pytest.approx(70.0) and c == pytest.approx(30.0)
    # selling YES at 0.3 when YES wins loses 0.7 a share (bought NO at 0.7, NO pays 0)
    e, c = W.trade_edge(*W.as_purchase('SELL', 0, 0.3, 100), payout0=1.0)
    assert e == pytest.approx(-70.0) and c == pytest.approx(70.0)
    # a round trip buy 0.3 / sell 0.6 nets +0.3 a share whatever the outcome
    for pay in (0.0, 1.0, 0.5):
        e1, _ = W.trade_edge(*W.as_purchase('BUY', 0, 0.3, 10), payout0=pay)
        e2, _ = W.trade_edge(*W.as_purchase('SELL', 0, 0.6, 10), payout0=pay)
        assert e1 + e2 == pytest.approx(3.0)


def test_mid_of_complement():
    assert W.mid_of(0, 0.62) == 0.62
    assert W.mid_of(1, 0.62) == pytest.approx(0.38)


# ---------------------------------------------------------------------------------------------- statistics

def test_ratio_t_estimate_and_clustering():
    R, t, n = W.ratio_t([(1.0, 10.0), (2.0, 10.0), (0.0, 10.0)])
    assert n == 3 and R == pytest.approx(0.1)
    # residuals e - R c: 0, 1, -1 -> var = 3/2 * 2 / 900
    assert t == pytest.approx(0.1 / math.sqrt(1.5 * 2 / 900.0))
    assert W.ratio_t([]) == (None, None, 0)
    R, t, n = W.ratio_t([(5.0, 10.0)])
    assert R == 0.5 and t is None and n == 1


def test_ratio_t_one_big_market_dominates():
    # many small winning markets and one large losing market: the ratio follows the dollars
    per = [(1.0, 10.0)] * 10 + [(-50.0, 100.0)]
    R, t, n = W.ratio_t(per)
    assert R == pytest.approx((10 - 50) / 200.0)


def test_spearman():
    assert W.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert W.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert W.spearman([1, 2], [1, 2]) is None
    r = W.spearman([1, 1, 2, 3], [1, 2, 3, 4])   # ties take average ranks
    assert -1 <= r <= 1 and r > 0.9


# ---------------------------------------------------------------------------------------------- episodes

def _b(ts, w='a', o=0, p=0.5, s=100):
    return {'ts': ts, 'wallet': w, 'outcome': o, 'price': p, 'size': s}


def test_buy_episodes_merge_within_an_hour_only():
    eps = W.buy_episodes([_b(0, p=0.4), _b(1800, p=0.5), _b(1800 + 3599, p=0.6), _b(1800 + 3599 + 3600, p=0.7)])
    assert len(eps) == 2
    e = eps[0]
    assert e['n'] == 3 and e['ts'] == 0 and e['last_ts'] == 5399
    assert e['shares'] == 300 and e['usd'] == pytest.approx(150.0) and e['vwap'] == pytest.approx(0.5)
    assert eps[1]['ts'] == 1800 + 3599 + 3600


def test_buy_episodes_split_by_wallet_and_outcome():
    eps = W.buy_episodes([_b(0, 'a', 0), _b(10, 'a', 1), _b(20, 'b', 0)])
    assert len(eps) == 3
    assert {(e['wallet'], e['outcome']) for e in eps} == {('a', 0), ('a', 1), ('b', 0)}


# ---------------------------------------------------------------------------------------------- follower money

def test_entry_cost_charges_half_spread_and_fee():
    cost, ask = W.entry_cost(0.40, 0.005, 0.05)
    assert ask == pytest.approx(0.405)
    assert cost == pytest.approx(0.405 + 0.05 * 0.405 * 0.595)
    cost, ask = W.entry_cost(0.999, 0.01, 0.0)       # capped below 1
    assert ask == pytest.approx(0.999)


def test_exit_proceeds_pays_half_spread_and_fee():
    pr, bid = W.exit_proceeds(0.60, 0.01, 0.04)
    assert bid == pytest.approx(0.59)
    assert pr == pytest.approx(0.59 - 0.04 * 0.59 * 0.41)
    pr, bid = W.exit_proceeds(0.001, 0.01, 0.0)       # floored
    assert bid == pytest.approx(0.001)


def test_follower_return_hold_and_exit():
    c, _ = W.entry_cost(0.5, 0.01, 0.05)
    assert W.follower_return(0.5, 1.0, 0.01, 0.05) == pytest.approx(1.0 / c - 1.0)
    assert W.follower_return(0.5, 0.0, 0.01, 0.05) == pytest.approx(-1.0)
    pr, _ = W.exit_proceeds(0.7, 0.01, 0.05)
    assert W.follower_return(0.5, 0.0, 0.01, 0.05, mid_out=0.7, hs_out=0.01) == pytest.approx(pr / c - 1.0)
    # a round trip at an unchanged mid loses the spread and two fees
    assert W.follower_return(0.5, 1.0, 0.01, 0.05, mid_out=0.5, hs_out=0.01) < 0


def test_entry_time_is_the_next_hourly_mark_after_the_delay():
    t = 10 * HOUR + 23 * 60
    assert W.entry_time(t, HOUR) == 12 * HOUR           # 11:23 -> 12:00
    assert W.entry_time(10 * HOUR, HOUR) == 11 * HOUR   # exactly on a mark
    assert W.entry_time(t, DAY) == 24 * HOUR + 11 * HOUR
    assert W.entry_time(t, HOUR) - t >= HOUR


def test_mid_at_uses_the_last_point_at_or_before():
    sx, sp = [0, 3600, 7200], [0.2, 0.3, 0.4]
    assert W.mid_at(sx, sp, 3600) == 0.3
    assert W.mid_at(sx, sp, 3599) == 0.2
    assert W.mid_at(sx, sp, -1) is None
    assert W.mid_at(sx, sp, 7200 + 4 * DAY) is None     # stale


def _market(trades, series, payout0=1.0, close=100 * HOUR, cat='politics'):
    m = {'id': 'm1', 'cat': cat, 'tags': [], 'payout0': payout0, 'close': close, 'rate': 0.04,
         'trades': sorted(trades), 'sx': [x[0] for x in series], 'sp': [x[1] for x in series], 'w': 1.0}
    m['_tx'] = [x[0] for x in m['trades']]
    return m


def _tbl():
    return {'old_half_spread': {}, 'new_half_spread': {'all|0.50-0.600': {'n': 10, 'median': 0.01, 'p75': 0.02},
                                                       'all|0.60-0.700': {'n': 10, 'median': 0.01, 'p75': 0.02},
                                                       'all|0.70-0.850': {'n': 10, 'median': 0.01, 'p75': 0.02}},
            'new_depth': {}}


def test_episode_records_hold_and_wallet_exit():
    # wallet 'a' buys YES at 10:30, sells at 20:30; mid series hourly rising 0.50 -> 0.70; YES wins
    series = [[h * HOUR, 0.5 + 0.2 * min(h, 30) / 30.0] for h in range(0, 100)]
    tr = [(int(10.5 * HOUR), 'a', 1, 0, 100.0, 0.55), (int(20.5 * HOUR), 'a', 0, 0, 100.0, 0.62)]
    m = _market(tr, series)
    eps, sells = W.market_episodes(m, 0)
    assert len(eps) == 1
    rec = W.episode_records(m, eps[0], sells, _tbl(), m['_tx'])
    r1 = rec['1h']
    assert r1['hold']['t_in'] == 12 * HOUR
    assert r1['hold']['mid_in'] == pytest.approx(0.5 + 0.2 * 12 / 30.0)
    assert r1['hold']['ret'] == pytest.approx(W.follower_return(r1['hold']['mid_in'], 1.0, 0.01, 0.04))
    assert r1['wexit']['t_out'] == 22 * HOUR                  # sale at 20:30, +1h -> 22:00
    assert r1['wexit']['mid_out'] == pytest.approx(0.5 + 0.2 * 22 / 30.0)
    # +1d: the sale (20:30) is seen at 20:30 + 1d, after the follower's entry at 11:00 + 1d -> exit at 21:00 + 1d
    rd = rec['1d']
    assert rd['hold']['t_in'] == 35 * HOUR and rd['wexit']['t_out'] == 45 * HOUR
    # leader's own return at its fill plus fee
    assert rec['leader'] == pytest.approx(1.0 / (0.55 + 0.04 * 0.55 * 0.45) - 1.0)


def test_wallet_exit_before_follower_entry_skips_the_copy():
    series = [[h * HOUR, 0.5] for h in range(0, 100)]
    tr = [(int(10.5 * HOUR), 'a', 1, 0, 100.0, 0.55), (int(10.6 * HOUR), 'a', 0, 0, 100.0, 0.5)]
    m = _market(tr, series)
    eps, sells = W.market_episodes(m, 0)
    rec = W.episode_records(m, eps[0], sells, _tbl(), m['_tx'])
    assert rec['1h']['wexit'] is None and rec['1h']['hold'] is not None


def test_no_entry_after_close_and_complement_outcome():
    series = [[h * HOUR, 0.3] for h in range(0, 12)]
    # wallet buys NO (outcome 1) at 0.7 at 10:30; market closes at 11:30 -> no +1h entry (12:00 >= close)
    tr = [(int(10.5 * HOUR), 'a', 1, 1, 100.0, 0.7)]
    m = _market(tr, series, payout0=0.0, close=11.5 * HOUR)
    eps, sells = W.market_episodes(m, 0)
    rec = W.episode_records(m, eps[0], sells, _tbl(), m['_tx'])
    assert rec['1h'] is None and rec['1d'] is None
    # same with a later close: entry on NO at 1 - 0.3
    m = _market(tr, series + [[h * HOUR, 0.3] for h in range(12, 50)], payout0=0.0, close=50 * HOUR)
    eps, sells = W.market_episodes(m, 0)
    rec = W.episode_records(m, eps[0], sells, _tbl(), m['_tx'])
    assert rec['1h']['hold']['mid_in'] == pytest.approx(0.7)
    assert rec['1h']['hold']['ret'] == pytest.approx(W.follower_return(0.7, 1.0, 0.01, 0.04))


def test_five_minute_reference_uses_another_wallets_trade():
    series = [[h * HOUR, 0.5] for h in range(0, 100)]
    t0 = int(10 * HOUR)
    tr = [(t0, 'a', 1, 0, 100.0, 0.55), (t0 + 200, 'b', 1, 0, 10.0, 0.9),      # too early
          (t0 + 400, 'a', 1, 0, 10.0, 0.56),                                    # same wallet: ignored
          (t0 + 500, 'c', 0, 0, 10.0, 0.52)]                                     # c sells YES at 0.52: YES bid
    m = _market(tr, series)
    ts, mid = W.ref_mid_5m(m, {'ts': t0, 'wallet': 'a', 'outcome': 0}, _tbl(), m['_tx'])
    assert ts == t0 + 500 and mid == pytest.approx(0.52 + 0.01)


# ---------------------------------------------------------------------------------------------- series, books

def test_daily_pnl_series_lands_pnl_on_close_day():
    rows = [{'t_in': 0.5 * DAY, 't_out': 2.5 * DAY, 'stake': 1.0, 'ret': 0.3}]
    s, k, capdays, pnl = W.daily_pnl_series(rows, 0, 3, ssr=0.0)
    assert pnl == pytest.approx(0.3)
    assert k == pytest.approx(3.0 / 4.0)        # open on days 0,1,2 of 4
    assert s[2] == pytest.approx(0.3 / k) and s[0] == 0 and s[3] == 0
    s, k, _, _ = W.daily_pnl_series(rows, 0, 3, ssr=0.0365)
    assert s[0] == pytest.approx(-0.0001)


def test_fold_band_symmetry():
    assert W.fold_band(0.12) == W.fold_band(0.88) == '0.85-0.900'
    assert W.fold_band(0.5) == '0.50-0.600'
    assert W.fold_band(0.999) is None


def test_book_stats_complement_ask():
    b = {'asks': [(0.62, 100.0), (0.63, 50.0)], 'bids': [(0.60, 200.0), (0.55, 10.0)]}
    st = W.book_stats(b)
    assert st['mid'] == pytest.approx(0.61) and st['half_spread'] == pytest.approx(0.01)
    assert st['ask0_usd'] == pytest.approx(62.0)
    assert st['ask1_usd'] == pytest.approx(0.40 * 200.0)   # NO ask = 1 - YES bid, with the bid's size
    assert W.book_stats({'asks': [(0.5, 1.0)], 'bids': [(0.5, 1.0)]}) is None


def test_half_spread_fallbacks():
    tbl = {'old_half_spread': {'all|0.90-0.950': {'n': 100, 'median': 0.01, 'p75': 0.02},
                               'sports|0.90-0.950': {'n': 3, 'median': 0.5, 'p75': 0.5}},
           'new_half_spread': {'politics|0.60-0.700': {'n': 8, 'median': 0.02, 'p75': 0.03}}, 'new_depth': {}}
    assert W.half_spread_of(tbl, 'sports', 0.07) == 0.01        # folded to 0.93; sports n < 5 -> 'all'
    assert W.half_spread_of(tbl, 'politics', 0.35) == 0.02      # folded to 0.65
    assert W.half_spread_of(tbl, 'culture', 0.55) == 0.005      # nothing measured -> one tick on a 0.01 grid


def test_select_requires_minimums_and_threshold():
    tab = {'a': {'n': 50, 'markets': 10, 't': 3.0, 't1d': 0.5},
           'b': {'n': 50, 'markets': 4, 't': 9.0, 't1d': 9.0},      # too few markets
           'c': {'n': 9, 'markets': 9, 't': 9.0, 't1d': 9.0},       # too few trades
           'd': {'n': 20, 'markets': 6, 't': 2.5, 't1d': 2.5},
           'e': {'n': 20, 'markets': 6, 't': 1.5, 't1d': None}}
    assert W.select(tab, 'edge', 2.0, 10) == ['a', 'd']
    assert W.select(tab, 'edge', 2.0, 1) == ['a']
    assert W.select(tab, 'mk1d', 1.0, 10) == ['d']


# ---------------------------------------------------------------------------------------------- event weights

def test_event_inclusion_prob():
    assert W.event_inclusion_prob([0.1]) == pytest.approx(0.1)
    assert W.event_inclusion_prob([0.1, 0.1]) == pytest.approx(1 - 0.81)
    assert W.event_inclusion_prob([0.0, 0.0]) == 0.0          # no member in the frame: never drawn
    assert W.event_inclusion_prob([1.0, 0.3]) == 1.0
    assert W.event_inclusion_prob([]) == 0.0


def test_event_completion_removes_winner_selection():
    # a 4-member neg-risk event where only the winner was big enough to be drawn: a YES buyer of every member at
    # fair prices breaks even over the complete event, but looks skilled on the drawn member alone
    prices, payouts = [0.4, 0.3, 0.2, 0.1], [0.0, 1.0, 0.0, 0.0]
    full = sum(W.trade_edge(0, q, 100, pay)[0] for q, pay in zip(prices, payouts))
    assert full == pytest.approx(0.0)
    drawn = W.trade_edge(0, prices[1], 100, payouts[1])[0]
    assert drawn > 0


# ---------------------------------------------------------------------------------------------- the variance floor

def test_ratio_t_floor_removes_the_infinite_t_of_a_clean_sweep():
    # five favourites bought at 0.9, all won: residuals are zero, so the cluster variance is zero
    per = [(10.0, 90.0)] * 5
    R, t, n = W.ratio_t(per)
    assert R == pytest.approx(10 / 90) and t is None
    v = W.null_var(100.0, 90.0, 100.0, 90.0)          # 100 shares of outcome 0 at 0.9: p(1-p) D^2 = 900
    assert v == pytest.approx(0.9 * 0.1 * 100 ** 2)
    R, t, n = W.ratio_t([(10.0, 90.0, v)] * 5)
    assert t == pytest.approx((50 / 450) / math.sqrt(5 * v / 450 ** 2))
    assert 0.5 < t < 1.0     # five fair 90% favourites all win 59% of the time: z = 50 / sqrt(4500) = 0.75


def test_null_var_round_trip_and_complement():
    # bought 0 and bought 1 in equal shares: no outcome exposure, floored at (1% of capital)^2
    assert W.null_var(0.0, 50.0, 100.0, 100.0) == pytest.approx(1.0)
    assert W.null_var(-100.0, 10.0, 100.0, 90.0) == pytest.approx(0.1 * 0.9 * 100 ** 2)


def test_mark_mid_reads_the_point_stamped_just_after_the_boundary():
    # points land seconds after each hour; an entry at 03:00 must read the 03:00:11 point, not 02:00:11
    sx = [h * HOUR + 11 for h in range(0, 6)]
    sp = [0.10 * h for h in range(0, 6)]
    assert W.mark_mid(sx, sp, 3 * HOUR) == pytest.approx(0.3)
    assert W.mid_at(sx, sp, 3 * HOUR) == pytest.approx(0.2)        # the old lookup: an hour early
    assert W.mark_mid(sx, sp, 3 * HOUR) == W.mid_at(sx, sp, 3 * HOUR + W.MARK_TOL)


def test_episode_entry_uses_the_mark_after_the_delay():
    series = [[h * HOUR + 11, 0.5 + 0.01 * h] for h in range(0, 60)]
    tr = [(int(1.75 * HOUR), 'a', 1, 0, 100.0, 0.5)]
    m = _market(tr, series)
    eps, sells = W.market_episodes(m, 0)
    rec = W.episode_records(m, eps[0], sells, _tbl(), m['_tx'])
    assert rec['1h']['hold']['t_in'] == 3 * HOUR
    assert rec['1h']['hold']['mid_in'] == pytest.approx(0.53)    # the 03:00:11 point
