#!/usr/bin/env python3
"""Unit tests for the sUSDe discount history: the arithmetic that turns a swap log into a discount, and the episode rule.

Each of these pins a way the number could be wrong quietly: a reversed coin order turns every sale into a purchase; a
missed decimals difference (USDT has six) makes a 1.24 price read as 1.24e12; forgetting the sDAI leg's own NAV
reports a 15% "discount" on every sDAI/sUSDe trade; a v4 delta read with the wrong sign flips buyer and seller; an
hour with one trade has no spread and must borrow one rather than pass the significance test for free.

    uv run --with pycryptodome python scripts/test_dislocation_history.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dislocation_history as dh  # noqa: E402
from live_rpc import enc_uint  # noqa: E402

SUSDE_NAV, SDAI_NAV = 1.2466, 1.1812


def nav_at(tok, n):
    return {dh.SUSDE: SUSDE_NAV, dh.SDAI: SDAI_NAV}.get(tok, 1.0)


def enc_int(v, bits=256):
    return enc_uint(v if v >= 0 else (1 << bits) + v)


def curve_log(sold_i, sold, bought_i, bought, block=100, buyer='0x' + 'ab' * 20):
    return {'address': '0x167478921b907422f8e88b43c4af2b8bea278d3a', 'blockNumber': hex(block), 'logIndex': '0x1',
            'transactionHash': '0x' + 'cd' * 32, 'topics': [dh.TOPICS['CurveEx'], '0x' + '00' * 12 + buyer[2:]],
            'data': '0x' + enc_uint(sold_i) + enc_uint(sold) + enc_uint(bought_i) + enc_uint(bought)}


def v4_log(a0, a1, sqrtp, fee=101, block=100):
    return {'address': dh.V4_MANAGER, 'blockNumber': hex(block), 'logIndex': '0x2', 'transactionHash': '0x' + 'ef' * 32,
            'topics': [dh.TOPICS['V4Swap'], dh.POOLS[2]['pool_id'], '0x' + '00' * 12 + 'ab' * 20],
            'data': '0x' + enc_int(a0) + enc_int(a1) + enc_uint(sqrtp) + enc_uint(10 ** 20) + enc_int(-274000) + enc_uint(fee)}


CURVE_META = {**dh.POOLS[0], 'coins': [dh.SDAI, dh.SUSDE], 'decimals': [18, 18]}
V4_META = dh.POOLS[2]


class DiscountArithmetic(unittest.TestCase):
    def test_sell_below_nav_is_a_positive_discount_after_both_navs(self):
        # Sell 1,000 sUSDe (worth 1,246.6 USDe) for 1,054.5 sDAI (worth 1,245.6 DAI): 8.0bp below NAV.
        sdai_out = 1054.5
        s = dh.decode_curve(curve_log(1, 1000 * 10 ** 18, 0, int(sdai_out * 10 ** 18)), CURVE_META, nav_at)
        self.assertEqual(s['side'], 'sell')
        self.assertAlmostEqual(s['price'], sdai_out * SDAI_NAV / 1000, places=9)
        self.assertAlmostEqual(s['discount_bps'], 1e4 * (SUSDE_NAV - sdai_out * SDAI_NAV / 1000) / SUSDE_NAV, places=6)
        self.assertGreater(s['discount_bps'], 7.5)
        self.assertLess(s['discount_bps'], 8.5)
        self.assertAlmostEqual(s['usd'], 1000 * SUSDE_NAV)

    def test_forgetting_the_sdai_nav_would_invent_a_fifteen_percent_discount(self):
        s = dh.decode_curve(curve_log(1, 1000 * 10 ** 18, 0, int(1055.4 * 10 ** 18)), CURVE_META, nav_at)
        wrong = 1e4 * (SUSDE_NAV - 1055.4 / 1000) / SUSDE_NAV
        self.assertGreater(wrong, 1400)
        self.assertLess(abs(s['discount_bps']), 5)

    def test_buy_direction_and_reversed_coin_order(self):
        # Coins reversed: sUSDe is index 0. Buy: pay 1,000 sDAI (1,181.2 DAI), receive 946.5 sUSDe (1,179.9 USDe at NAV)
        # -> paid 1.24791 per sUSDe against a NAV of 1.2466 -> above NAV -> negative discount.
        meta = {**CURVE_META, 'coins': [dh.SUSDE, dh.SDAI]}
        s = dh.decode_curve(curve_log(1, 1000 * 10 ** 18, 0, int(946.5 * 10 ** 18)), meta, nav_at)
        self.assertEqual(s['side'], 'buy')
        self.assertAlmostEqual(s['price'], 1000 * SDAI_NAV / 946.5, places=9)
        self.assertAlmostEqual(s['discount_bps'], 1e4 * (SUSDE_NAV - 1000 * SDAI_NAV / 946.5) / SUSDE_NAV, places=6)
        self.assertLess(s['discount_bps'], 0)
        # the same amounts with the coin order the pool really has must not change the answer
        s2 = dh.decode_curve(curve_log(0, 1000 * 10 ** 18, 1, int(946.5 * 10 ** 18)), CURVE_META, nav_at)
        self.assertAlmostEqual(s2['discount_bps'], s['discount_bps'], places=9)
        self.assertEqual(s['other_symbol'], 'sDAI')

    def test_v4_sign_convention_and_usdt_decimals(self):
        # Caller pays 8,850 sUSDe (negative delta), receives 11,030 USDT (6 decimals): 1.24633 per sUSDe, 2.18bp below NAV.
        s = dh.decode_v4(v4_log(-8850 * 10 ** 18, 11030 * 10 ** 6, 0), V4_META, nav_at)
        self.assertEqual(s['side'], 'sell')
        self.assertAlmostEqual(s['price'], 11030 / 8850, places=9)
        self.assertAlmostEqual(s['discount_bps'], 1e4 * (SUSDE_NAV - 11030 / 8850) / SUSDE_NAV, places=6)
        self.assertGreater(s['discount_bps'], 2.0)
        self.assertLess(s['discount_bps'], 2.4)
        # a wrong decimals shift would put the price twelve orders of magnitude off
        self.assertLess(abs(s['price'] - SUSDE_NAV), 0.01)
        self.assertEqual(s['fee_bps'], 1.01)
        b = dh.decode_v4(v4_log(8850 * 10 ** 18, -11040 * 10 ** 6, 0), V4_META, nav_at)
        self.assertEqual(b['side'], 'buy')
        self.assertLess(b['discount_bps'], s['discount_bps'])

    def test_v4_mid_price_from_sqrt_price(self):
        # sqrtPriceX96 for 1.2466 USDT per sUSDe with an 18 -> 6 decimals shift.
        import math
        raw_price = 1.2466 * 10 ** (6 - 18)
        sqrtp = int(math.sqrt(raw_price) * 2 ** 96)
        s = dh.decode_v4(v4_log(-10 ** 21, 1246 * 10 ** 6, sqrtp), V4_META, nav_at)
        self.assertAlmostEqual(s['mid_discount_bps'], 0.0, delta=0.05)

    def test_same_sign_or_zero_deltas_are_not_swaps(self):
        self.assertIsNone(dh.decode_v4(v4_log(-10 ** 21, -10 ** 9, 0), V4_META, nav_at))
        self.assertIsNone(dh.decode_v4(v4_log(0, 10 ** 9, 0), V4_META, nav_at))
        other = dict(v4_log(-10 ** 21, 10 ** 9, 0))
        other['topics'] = [other['topics'][0], '0x' + '11' * 32, other['topics'][2]]
        self.assertIsNone(dh.decode_v4(other, V4_META, nav_at))

    def test_swap_discount_rejects_zero_and_missing_nav(self):
        self.assertEqual(dh.swap_discount(0, 1, 1, 1.2), (None, None))
        self.assertEqual(dh.swap_discount(1, 1, 1, 0), (None, None))

    def test_dust_threshold_is_applied_on_nav_notional(self):
        s = dh.decode_curve(curve_log(1, 700 * 10 ** 18, 0, int(738 * 10 ** 18)), CURVE_META, nav_at)
        self.assertLess(s['usd'], dh.MIN_TRADE_USD)
        s = dh.decode_curve(curve_log(1, 900 * 10 ** 18, 0, int(949 * 10 ** 18)), CURVE_META, nav_at)
        self.assertGreater(s['usd'], dh.MIN_TRADE_USD)


class Interpolation(unittest.TestCase):
    def test_linear_between_grid_points_and_clamped_outside(self):
        xs, ys = [100, 200, 300], [1.0, 1.1, 1.3]
        self.assertAlmostEqual(dh.interp(xs, ys, 150), 1.05)
        self.assertAlmostEqual(dh.interp(xs, ys, 250), 1.2)
        self.assertEqual(dh.interp(xs, ys, 50), 1.0)
        self.assertEqual(dh.interp(xs, ys, 400), 1.3)
        self.assertEqual(dh.interp([5], [2.0], 9), 2.0)

    def test_quantile(self):
        self.assertEqual(dh.pct([3, 1, 2], .5), 2)
        self.assertEqual(dh.pct([1, 3], .5), 2)
        self.assertEqual(dh.pct([7], .9), 7)
        self.assertIsNone(dh.pct([], .5))

    def test_gaps(self):
        self.assertEqual(dh.gaps([], 1, 10), [(1, 10)])
        self.assertEqual(dh.gaps([[1, 3], [7, 8]], 1, 10), [(4, 6), (9, 10)])
        self.assertEqual(dh.gaps([[1, 10]], 1, 10), [])
        self.assertEqual(dh.gaps([[0, 20]], 5, 10), [])


def hour(i, discounts, usd=20_000.0, sides=None):
    t0 = 1_760_000_000 - 1_760_000_000 % 3600
    out = []
    for j, d in enumerate(discounts):
        side = (sides or ['sell'] * len(discounts))[j]
        out.append({'ts': t0 + i * 3600 + 60 * j, 'usd': usd, 'discount_bps': d, 'side': side, 'nav': 1.2466})
    return out


class Episodes(unittest.TestCase):
    def test_hourly_series_weights_by_notional_and_tracks_sells(self):
        swaps = [{'ts': 3600, 'usd': 1000.0, 'discount_bps': 10.0, 'side': 'sell', 'nav': 1.2},
                 {'ts': 3700, 'usd': 3000.0, 'discount_bps': 2.0, 'side': 'buy', 'nav': 1.2}]
        r = dh.hourly_series(swaps)[0]
        self.assertAlmostEqual(r['vw_discount_bps'], 4.0)
        self.assertEqual(r['n_sell'], 1)
        self.assertEqual(r['max_sell_discount_bps'], 10.0)
        self.assertIsNone(r['spread_bps'])  # two trades: no spread of its own

    def test_episode_needs_net_edge_above_spread_and_bridges_small_gaps(self):
        swaps = []
        swaps += hour(0, [1.0, 1.5, 0.5])            # quiet
        swaps += hour(1, [9.0, 9.5, 8.5])            # net 6.3 > spread 1.0: qualifies
        swaps += hour(2, [9.0, 9.5, 8.5])            # qualifies
        # hours 3 and 4 empty (gap of 2, bridged)
        swaps += hour(5, [8.0, 8.0, 8.0])            # qualifies, zero spread
        swaps += hour(6, [4.0, 12.0, 0.0])           # vw 5.3, net 2.6 < spread 9.6: ends the episode
        swaps += hour(7, [7.0])                      # one trade: borrows the floor
        rows = dh.hourly_series(swaps)
        eps = dh.segment_episodes(rows, round_trip_bps=2.7, max_gap_hours=2)
        self.assertEqual(len(eps), 2)
        first = eps[0]
        self.assertEqual(first['qualifying_hours'], 3)
        self.assertEqual(first['duration_hours'], 5)
        self.assertAlmostEqual(first['sell_volume_usd'], 9 * 20_000.0)
        self.assertAlmostEqual(first['fillable_capped_usd'], 180_000.0)
        self.assertAlmostEqual(first['option_value_usd'], 180_000.0 * (first['vw_discount_bps'] - 2.7) / 1e4)
        # the lone-trade hour qualifies only because 7.0 - 2.7 exceeds the history's median spread (1.0)
        self.assertEqual(eps[1]['qualifying_hours'], 1)
        self.assertEqual(rows[-1]['spread_source'], 'history-median')

    def test_a_wide_gap_splits_episodes_and_a_lone_trade_cannot_pass_a_high_floor(self):
        swaps = hour(0, [9.0, 9.5, 8.5]) + hour(4, [9.0, 9.5, 8.5]) + hour(9, [5.0])
        rows = dh.hourly_series(swaps)
        eps = dh.segment_episodes(rows, round_trip_bps=2.7, floor_bps=5.0, max_gap_hours=2)
        self.assertEqual([e['qualifying_hours'] for e in eps], [1, 1])
        self.assertFalse(rows[-1]['qualifies'])

    def test_capacity_cap_binds_option_value(self):
        swaps = hour(0, [10.0] * 3, usd=500_000.0)
        eps = dh.segment_episodes(dh.hourly_series(swaps), round_trip_bps=2.7, floor_bps=1.0, cap_usd=600_000)
        self.assertEqual(len(eps), 1)
        self.assertAlmostEqual(eps[0]['fillable_usd'], 1_500_000.0)
        self.assertAlmostEqual(eps[0]['fillable_capped_usd'], 600_000.0)
        self.assertAlmostEqual(eps[0]['option_value_usd'], 600_000.0 * 7.3 / 1e4)

    def test_premium_hours_never_qualify(self):
        eps = dh.segment_episodes(dh.hourly_series(hour(0, [-3.0, -2.0, -4.0])), floor_bps=0.0)
        self.assertEqual(eps, [])


class UsdeBasis(unittest.TestCase):
    META = {**dh.BASIS_POOL, 'coins': [dh.USDE, dh.USDC], 'decimals': [18, 6]}

    def log(self, sold_i, sold, bought_i, bought, block=100):
        l = curve_log(sold_i, sold, bought_i, bought, block=block)
        l['address'] = dh.BASIS_POOL['address']
        return l

    def test_price_is_quote_per_usde_in_either_direction_with_six_decimal_quote(self):
        sell = dh.decode_basis(self.log(0, 10_000 * 10 ** 18, 1, 9_995 * 10 ** 6), self.META)      # USDe sold for USDC
        buy = dh.decode_basis(self.log(1, 10_005 * 10 ** 6, 0, 10_000 * 10 ** 18), self.META)      # USDC paid for USDe
        self.assertAlmostEqual(sell['price'], 0.9995)
        self.assertAlmostEqual(buy['price'], 1.0005)
        self.assertEqual(sell['usde'], 10_000)
        self.assertIsNone(dh.decode_basis(self.log(0, 1, 0, 1), self.META))

    def test_hourly_basis_is_volume_weighted_and_positive_below_par(self):
        swaps = [{'ts': 3600, 'usde': 1_000.0, 'quote': 999.0, 'price': .999},
                 {'ts': 3601, 'usde': 3_000.0, 'quote': 3_000.0, 'price': 1.0}]
        hb = dh.hourly_basis(swaps)
        self.assertAlmostEqual(hb[3600]['price'], 3999 / 4000)
        self.assertAlmostEqual(hb[3600]['basis_bps'], 2.5)
        self.assertEqual(hb[3600]['n'], 2)

    def test_basis_is_carried_forward_but_not_forever_and_never_backward(self):
        hb = {7200: {'basis_bps': 4.0}}
        self.assertEqual(dh.basis_at(hb, 7200), (4.0, 0))
        self.assertEqual(dh.basis_at(hb, 7200 + 5 * 3600), (4.0, 5))
        self.assertEqual(dh.basis_at(hb, 7200 + 25 * 3600, carry_hours=24), (None, None))
        self.assertEqual(dh.basis_at(hb, 3600), (None, None))

    def test_netting_the_basis_removes_a_usde_depeg_from_the_susde_discount(self):
        # sUSDe 12bp below NAV while USDe itself is 9bp below par: only 3bp is the cooldown discount.
        self.assertAlmostEqual(12.0 - dh.basis_at({0: {'basis_bps': 9.0}}, 0)[0], 3.0)


class PrintBound(unittest.TestCase):
    def test_a_thirty_percent_print_is_flagged_by_the_default_bound(self):
        self.assertGreater(3012.5, dh.MAX_PRINT_BPS)
        self.assertLess(43.1, dh.MAX_PRINT_BPS)

    def test_daily_cap_scales_with_days_spanned(self):
        swaps = []
        for h in range(0, 60):                      # a 60-hour episode, every hour qualifying
            swaps += hour(h, [10.0] * 3, usd=100_000.0)
        eps = dh.segment_episodes(dh.hourly_series(swaps), round_trip_bps=2.7, floor_bps=1.0, cap_usd=600_000)
        self.assertEqual(len(eps), 1)
        e = eps[0]
        self.assertEqual(e['days_spanned'], 3)
        self.assertAlmostEqual(e['fillable_capped_usd'], 600_000.0)
        self.assertAlmostEqual(e['fillable_capped_daily_usd'], 1_800_000.0)
        self.assertAlmostEqual(e['option_value_daily_cap_usd'], 3 * e['option_value_usd'])


if __name__ == '__main__':
    unittest.main()
