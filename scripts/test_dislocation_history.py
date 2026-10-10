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



# ----------------------------------------------------------------------------------------------------------------------
# The redemption surface (2026-10-09): every venue's sign convention, the queue waits, and the bid with locked capital
# ----------------------------------------------------------------------------------------------------------------------
WSTETH_NAV, WEETH_NAV, RETH_NAV = 1.2459, 1.1054, 1.1735


def surface_nav(key, n):
    return {'wsteth_nav': WSTETH_NAV, 'weeth_nav': WEETH_NAV, 'reth_nav': RETH_NAV, 'sdai_nav': SDAI_NAV,
            'susde_nav': SUSDE_NAV}.get(key)


def data_words(*vals):
    return '0x' + ''.join(enc_int(v) for v in vals)


class SurfaceLegs(unittest.TestCase):
    LIDO = dh.SURFACE['lido']
    EF = dh.SURFACE['etherfi']
    RP = dh.SURFACE['rocketpool']

    def test_v3_amounts_are_the_pools_view(self):
        # weETH pool: token0 WETH, token1 weETH. A holder sells 100 weETH (into the pool: +) for 110.4 WETH (out: -).
        meta = {'tokens': [dh.WETH, dh.WEETH], 'decimals': [18, 18], 'fee_bps': 1.0}
        log = {'topics': [dh.XTOPICS['V3Swap'], '0x' + '00' * 32, '0x' + '00' * 32],
               'data': data_words(-int(110.4 * 10 ** 18), 100 * 10 ** 18, 0, 0, 0)}
        legs = dh.legs_v3(log, meta, self.EF['targets'])
        self.assertEqual(legs[:2], ('sell', dh.WEETH))
        self.assertAlmostEqual(legs[2], 100.0)
        self.assertAlmostEqual(legs[4], 110.4)
        rec = dh.price_swap(self.EF, legs, 1, surface_nav)
        self.assertAlmostEqual(rec['price'], 1.104)
        self.assertAlmostEqual(rec['discount_bps'], 1e4 * (WEETH_NAV - 1.104) / WEETH_NAV)
        # the same amounts read with v4's sign convention would flip the side
        flipped = dh.legs_v3({**log, 'data': data_words(int(110.4 * 10 ** 18), -100 * 10 ** 18, 0, 0, 0)}, meta, self.EF['targets'])
        self.assertEqual(flipped[0], 'buy')

    def test_v4_native_eth_is_currency0_and_the_fee_rides_in_the_event(self):
        meta = {'pool_id': '0x' + '70' * 32, 'tokens': [dh.NATIVE, dh.RETH], 'decimals': [18, 18]}
        # swapper pays 10 rETH (negative) and receives 11.72 ETH: a sale, 1bp fee (100 hundredths of a bip)
        log = {'topics': [dh.XTOPICS['V4Swap'], meta['pool_id'], '0x' + '00' * 32],
               'data': data_words(int(11.72 * 10 ** 18), -10 * 10 ** 18, 0, 0, 0, 100)}
        legs = dh.legs_v4(log, meta, self.RP['targets'])
        self.assertEqual(legs[:2], ('sell', dh.RETH))
        self.assertEqual(legs[5], 1.0)
        rec = dh.price_swap(self.RP, legs, 1, surface_nav)
        self.assertAlmostEqual(rec['discount_bps'], 1e4 * (RETH_NAV - 1.172) / RETH_NAV)
        other = {**log, 'topics': [log['topics'][0], '0x' + '11' * 32, log['topics'][2]]}
        self.assertIsNone(dh.legs_v4(other, meta, self.RP['targets']))

    def test_fluid_direction_flag_and_mixed_decimals(self):
        ef_meta = {'tokens': [dh.WEETH, dh.ETH_SENTINEL], 'decimals': [18, 18], 'fee_bps': 0.83}
        # swap0to1 = false: token1 (ETH) in, token0 (weETH) out -> a purchase of weETH (the 2026-10-09 sample log)
        buy = dh.legs_fluid({'data': data_words(0, 4 * 10 ** 18, int(3.618 * 10 ** 18), 0)}, ef_meta, self.EF['targets'])
        self.assertEqual(buy[:2], ('buy', dh.WEETH))
        self.assertAlmostEqual(buy[4], 4.0)
        sell = dh.legs_fluid({'data': data_words(1, 10 ** 18, int(1.1 * 10 ** 18), 0)}, ef_meta, self.EF['targets'])
        self.assertEqual(sell[0], 'sell')
        usde = dh.SURFACE['usde']
        meta = {'tokens': [dh.USDE, dh.USDT], 'decimals': [18, 6], 'fee_bps': 1.0}
        # 15,490.08 USDT in (6 decimals), 15,481.06 USDe out (18 decimals): USDe bought at 1.000583 USDT
        legs = dh.legs_fluid({'data': data_words(0, 15_490_079_142, 15_481_055_780_094_033_000_000, 0)}, meta, usde['targets'])
        rec = dh.price_swap(usde, legs, 1, surface_nav)
        self.assertEqual(rec['side'], 'buy')
        self.assertAlmostEqual(rec['price'], 15_490.079142 / 15_481.055780094033, places=9)
        self.assertLess(rec['discount_bps'], 0)        # bought above par

    def test_curve_with_the_native_eth_sentinel_and_par_nav(self):
        meta = {'coins': [dh.ETH_SENTINEL, dh.STETH], 'decimals': [18, 18], 'fee_bps': 1.0}
        log = {'data': '0x' + enc_uint(1) + enc_uint(1000 * 10 ** 18) + enc_uint(0) + enc_uint(999 * 10 ** 18)}
        legs = dh.legs_curve(log, meta, self.LIDO['targets'])
        rec = dh.price_swap(self.LIDO, legs, 1, surface_nav)
        self.assertEqual((rec['side'], rec['token']), ('sell', 'stETH'))
        self.assertAlmostEqual(rec['discount_bps'], 10.0)

    def test_wsteth_is_priced_against_steth_per_token_not_par(self):
        meta = {'tokens': [dh.WSTETH, dh.WETH], 'decimals': [18, 18], 'fee_bps': 1.0}
        # sell 100 wstETH for 124.5 WETH: 7.1bp under a NAV of 1.2459, not 2,450bp over par
        log = {'topics': [dh.XTOPICS['V3Swap'], '0x' + '00' * 32, '0x' + '00' * 32],
               'data': data_words(100 * 10 ** 18, -int(124.5 * 10 ** 18), 0, 0, 0)}
        rec = dh.price_swap(self.LIDO, dh.legs_v3(log, meta, self.LIDO['targets']), 1, surface_nav)
        self.assertAlmostEqual(rec['discount_bps'], 1e4 * (WSTETH_NAV - 1.245) / WSTETH_NAV, places=6)
        self.assertLess(abs(rec['discount_bps']), 10)

    def test_quote_at_its_own_nav_and_unpriced_quotes(self):
        su = dh.SURFACE['susde']
        rec = dh.price_swap(su, ('sell', dh.SUSDE, 1000.0, dh.SDAI, 1054.5, 2.0), 1, surface_nav)
        self.assertAlmostEqual(rec['price'], 1054.5 * SDAI_NAV / 1000)
        self.assertIsNone(dh.price_swap(su, ('sell', dh.SUSDE, 1000.0, dh.WETH, 1.0, 2.0), 1, surface_nav))

    def test_orient_needs_exactly_one_target(self):
        t = {dh.STETH: {}, dh.WSTETH: {}}
        self.assertIsNone(dh.orient(dh.STETH, 1, dh.WSTETH, 1, t))
        self.assertIsNone(dh.orient(dh.WETH, 1, dh.USDC, 1, t))


class SurfaceWaits(unittest.TestCase):
    def test_lido_waits_map_requests_into_finalized_ranges(self):
        day = 86400
        reqs = {1: 0, 2: 3600, 3: 7200, 4: day, 5: 2 * day}
        fins = [(1, 3, day // 2), (4, 4, 3 * day)]
        w = dh.lido_waits(reqs, fins, end_ts=4 * day)
        self.assertAlmostEqual(w[1][1], 0.5)
        self.assertAlmostEqual(w[3][1], (day // 2 - 7200) / day)
        self.assertAlmostEqual(w[4][1], 2.0)
        self.assertIsNone(w[5][1])                 # still pending: censored
        self.assertAlmostEqual(w[5][2], 2.0)       # lower bound = end - request

    def test_pointer_waits_inclusive_and_exclusive_counters(self):
        day = 86400
        created = [(0, 10), (day, 20), (2 * day, 30), (3 * day, 30)]
        # inclusive: last finalized id. Ids 10..19 (created by day 1) are all final at day 3 (last finalized 25).
        final_incl = [(0, 5), (day, 9), (2 * day, 12), (3 * day, 25)]
        w = dh.pointer_waits(created, final_incl, True)
        self.assertEqual(w[0][0], day)
        self.assertAlmostEqual(w[0][1], 2.0)       # median id 14.5 passes at day 3 (25 + 1 > 14.5)
        # a same-sample finalization is one grid step, not zero
        same = dh.pointer_waits([(0, 10), (day, 20)], [(0, 5), (day, 30)], True)
        self.assertAlmostEqual(same[0][1], 1.0)
        self.assertAlmostEqual(w[1][1], 1.0)       # ids 20..29 (median 24.5) are final at day 3: 25 + 1 > 24.5
        # exclusive: first unfinalized id; the same numbers mean one id less is final.
        final_excl = [(0, 5), (day, 9), (2 * day, 15), (3 * day, 25)]
        w2 = dh.pointer_waits(created, final_excl, False)
        self.assertAlmostEqual(w2[0][1], 1.0)      # 15 > 14.5 at day 2

    def test_daily_wait_function_takes_the_median_and_carries_forward(self):
        day = 86400
        f, med = dh.daily_wait_fn([(10, 1.0, None), (20, 3.0, None), (30, None, 9.0), (3 * day + 5, 2.0, None)], 4.0)
        self.assertEqual(f(50), 3.0)               # median of 1, 3 and the censored 9
        self.assertEqual(f(2 * day), 3.0)          # no requests that day: inherit
        self.assertEqual(f(3 * day + 100), 2.0)
        g, _ = dh.daily_wait_fn([], 4.0)
        self.assertEqual(g(0), 4.0)


def sells(*rows):
    return [{'ts': t, 'usd': u, 'discount_bps': d, 'fee_bps': f} for t, u, d, f in rows]


class SurfaceBid(unittest.TestCase):
    ZERO = staticmethod(lambda ts: 0.0)

    def test_edge_pays_two_fees_and_the_wait(self):
        # 10bp discount, 1bp pool, 2-day queue at 1bp/day of carry: edge = 10 - 2 - 2 = 6bp
        fills, st = dh.simulate_bid(sells((0, 100_000, 10.0, 1.0)), 1_000_000, 0.0, lambda ts: 2.0, lambda ts: 1.0)
        self.assertEqual(len(fills), 1)
        self.assertAlmostEqual(fills[0]['edge_bps'], 6.0)
        self.assertAlmostEqual(fills[0]['value_usd'], 100_000 * 6 / 1e4 - dh.GAS_PER_FILL_USD)
        # the same discount on an asset that keeps earning while queued pays no carry
        fills, _ = dh.simulate_bid(sells((0, 100_000, 10.0, 1.0)), 1_000_000, 0.0, lambda ts: 2.0, lambda ts: 1.0, accrues=True)
        self.assertAlmostEqual(fills[0]['edge_bps'], 8.0)

    def test_locked_capital_misses_the_next_sell_until_the_queue_pays(self):
        day = 86400
        rows = sells((0, 600_000, 20.0, 0.0), (day, 600_000, 20.0, 0.0), (8 * day, 600_000, 20.0, 0.0))
        fills, st = dh.simulate_bid(rows, 1_000_000, 0.0, lambda ts: 7.0, self.ZERO)
        self.assertEqual([round(f['usd']) for f in fills], [600_000, 400_000, 600_000])
        self.assertAlmostEqual(st['missed_capital_usd'], 200_000)
        # an instant redemption never locks: all three fill in full
        fills, st = dh.simulate_bid(rows, 1_000_000, 0.0, self.ZERO, self.ZERO)
        self.assertEqual(sum(f['usd'] for f in fills), 1_800_000)

    def test_hurdle_daily_cap_gas_and_minimum(self):
        rows = sells((0, 400_000, 6.0, 1.0), (60, 400_000, 6.0, 1.0), (86_400, 4_000, 50.0, 0.0), (86_460, 50_000, 3.0, 1.0))
        fills, st = dh.simulate_bid(rows, 10_000_000, 2.0, self.ZERO, self.ZERO, daily_cap_usd_at=lambda ts: 600_000)
        # edge 4bp clears a 2bp hurdle; the day's cap leaves 200k for the second sell; the next day's $4k sale
        # qualifies but is under the minimum fill; the last sell's 1bp edge fails the hurdle
        self.assertEqual([round(f['usd']) for f in fills], [400_000, 200_000])
        self.assertAlmostEqual(st['missed_cap_usd'], 200_000)
        self.assertEqual(st['qualifying_sells'], 3)
        none, _ = dh.simulate_bid(sells((0, 20_000, 4.0, 0.0)), 1e6, 0.0, self.ZERO, self.ZERO)
        self.assertEqual(none, [])                 # $8 of edge does not pay $10 of gas

    def test_a_one_venue_dislocation_is_capped_at_the_market(self):
        # $10M sold 20bp under NAV on one pool while the other two venues trade at 1bp: an atomic arbitrage, not a
        # redemption trade. Capped at the median venue less one fee, the edge is 0bp and nothing fills.
        recs = [{'ts': 3600 * 10, 'usd': 10_000_000, 'discount_bps': 20.0, 'pool': 'v3'},
                {'ts': 3600 * 10 + 60, 'usd': 2_000_000, 'discount_bps': 1.0, 'pool': 'curve'},
                {'ts': 3600 * 9, 'usd': 1_000_000, 'discount_bps': 1.0, 'pool': 'fluid'}]
        mkt = dh.market_discount_fn(recs)
        self.assertEqual(mkt(3600 * 10 + 5), 1.0)
        rows = sells((3600 * 10, 10_000_000, 20.0, 1.0))
        capped, _ = dh.simulate_bid(rows, 30e6, 0.0, self.ZERO, self.ZERO, market_bps_at=mkt)
        uncapped, _ = dh.simulate_bid(rows, 30e6, 0.0, self.ZERO, self.ZERO)
        self.assertEqual(capped, [])
        self.assertAlmostEqual(uncapped[0]['edge_bps'], 18.0)
        # when every venue is down 28bp (April 2026) the cap is the market, and the fill survives at 27bp
        recs2 = [dict(r, discount_bps=28.0) for r in recs[1:]] + [dict(recs[0], discount_bps=45.0)]
        rows2 = sells((3600 * 10, 10_000_000, 45.0, 1.0))
        f2, _ = dh.simulate_bid(rows2, 30e6, 0.0, self.ZERO, self.ZERO, market_bps_at=dh.market_discount_fn(recs2))
        self.assertAlmostEqual(f2[0]['edge_bps'], 27.0)
        # a venue last seen more than six hours ago does not vote
        self.assertIsNone(dh.market_discount_fn(recs)(3600 * 20))

    def test_daily_values_and_capacity(self):
        v = dh.daily_values([{'ts': 86400 * 3 + 5, 'value_usd': 7.0}, {'ts': 86400 * 3 + 9, 'value_usd': 1.0}], 2, 4)
        self.assertEqual(v, [0.0, 8.0, 0.0, 0.0])
        self.assertEqual(dh.capacity_size({1: 50.0, 3: 95.0, 10: 100.0}), 3)
        self.assertIsNone(dh.capacity_size({1: 0.0, 3: -5.0}))


def addr_topic(a):
    return '0x' + '00' * 12 + a[2:]


class SurfacePayouts(unittest.TestCase):
    def test_kelp_payout_matched_to_its_request_and_priced_against_nav_at_the_request(self):
        nav = lambda key, n: {100: 1.08, 900: 1.081}[n] if key == 'rseth_nav' else None
        w = '0x' + 'ab' * 20
        q = {'address': dh.KELP_WM, 'blockNumber': hex(100), 'topics': [dh.XTOPICS['KelpQueued'], addr_topic(w), addr_topic(dh.ETH_SENTINEL), '0x' + '00' * 31 + '07'],
             'data': '0x' + enc_uint(10 ** 18)}
        f = {'address': dh.KELP_WM, 'blockNumber': hex(900), 'topics': [dh.XTOPICS['KelpFinalized'], addr_topic(w), addr_topic(dh.ETH_SENTINEL)],
             'data': '0x' + enc_uint(10 ** 18) + enc_uint(int(1.08 * 10 ** 18))}
        r = dh.redemption_check('kelp', [q, f], [], nav, None)
        self.assertEqual(r['n'], 1)
        self.assertAlmostEqual(r['median_bps_vs_nav_at_request'], 0.0, places=6)
        self.assertAlmostEqual(r['median_bps_vs_nav_at_payout'], 1e4 * (1.08 - 1.081) / 1.081, places=6)
        # an stETH-queue withdrawal is not an ETH payout and is ignored
        f2 = dict(f, topics=[f['topics'][0], f['topics'][1], addr_topic(dh.STETH)])
        self.assertEqual(dh.redemption_check('kelp', [q, f2], [], nav, None)['n'], 0)

    def test_renzo_request_rate_and_lido_one_to_one(self):
        nav = lambda key, n: 1.087 if key == 'ezeth_nav' else None
        d = '0x' + enc_uint(0) + enc_uint(int(dh.ETH_SENTINEL, 16)) + enc_uint(int(1.0859 * 10 ** 18)) + enc_uint(10 ** 18) + enc_uint(3) + enc_uint(0) + enc_uint(0)
        log = {'address': dh.RENZO_WQ, 'blockNumber': hex(5), 'topics': [dh.XTOPICS['RenzoCreated'], '0x' + '00' * 31 + '01'], 'data': d}
        r = dh.redemption_check('renzo', [log], [], nav, None)
        self.assertAlmostEqual(r['median_bps_vs_nav_at_request'], 1e4 * (1.0859 - 1.087) / 1.087, places=6)
        req = {'address': dh.LIDO_WQ, 'blockNumber': hex(1), 'topics': [dh.XTOPICS['LidoRequested'], '0x' + '00' * 31 + '09', addr_topic('0x' + '01' * 20), addr_topic('0x' + '01' * 20)],
               'data': '0x' + enc_uint(5 * 10 ** 18) + enc_uint(4 * 10 ** 18)}
        clm = {'address': dh.LIDO_WQ, 'blockNumber': hex(2), 'topics': [dh.XTOPICS['LidoClaimed'], '0x' + '00' * 31 + '09', addr_topic('0x' + '01' * 20), addr_topic('0x' + '01' * 20)],
               'data': '0x' + enc_uint(5 * 10 ** 18 - 1)}
        r = dh.redemption_check('lido', [clm], [req], None, None)
        self.assertEqual(r['n'], 1)
        self.assertAlmostEqual(r['median_bps_vs_nav_at_request'], 0.0, places=9)


class SurfaceRates(unittest.TestCase):
    def test_apr_from_nav_compounds_over_the_span(self):
        yr = 365 * 86400
        self.assertAlmostEqual(dh.apr_from_nav([(0, 1.0), (yr, 1.05)]), 0.05)
        self.assertAlmostEqual(dh.apr_from_nav([(0, 1.0), (yr // 2, 1.05 ** 0.5)]), 0.05, places=9)
        self.assertIsNone(dh.apr_from_nav([(0, 1.0)]))

    def test_trailing_rate_reads_the_last_week(self):
        day = 86400
        nav = [(i * day, 1.0 * (1.038 ** (i / 365.0)) if i < 20 else 1.038 ** (19 / 365.0) * (1.05 ** ((i - 19) / 365.0))) for i in range(40)]
        f = dh.trailing_rate_fn(nav, 7.0, 0.01)
        self.assertAlmostEqual(f(10 * day), 0.038, places=6)
        self.assertAlmostEqual(f(39 * day), 0.05, places=6)

    def test_max_nav_step(self):
        self.assertAlmostEqual(dh.max_nav_step_bps([(0, 1.0), (1, 1.0001), (2, 1.0001)]), 1.0)



# ----------------------------------------------------------------------------------------------------------------------
# The ether.fi payout check (2026-10-10): both event versions, finalization from the admin's counter, the step NAV
# ----------------------------------------------------------------------------------------------------------------------
def ef_log(topic, rid, words, block=100, li=0):
    return {'address': dh.ETHERFI_WRNFT, 'blockNumber': hex(block), 'logIndex': hex(li), 'transactionHash': '0x' + '%064x' % (block * 1000 + li),
            'topics': [topic, '0x' + '%064x' % rid], 'data': '0x' + ''.join(enc_uint(w) for w in words)}


OWNER = int('ab' * 20, 16)


class EtherFiPayouts(unittest.TestCase):
    def test_pure_keccak_matches_known_hashes(self):
        self.assertEqual(dh._keccak256_pure(b''), 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470')
        self.assertEqual('0x' + dh._keccak256_pure(b'Transfer(address,address,uint256)'),
                         '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')
        # 200 bytes spans two 136-byte blocks: the absorb loop must carry state across blocks
        self.assertEqual(len(dh._keccak256_pure(b'x' * 200)), 64)
        self.assertEqual(dh.EFTOPICS['Claimed'], '0x31712d805743a128cf0ab8cdf453da51797d2e6f674bd1e5d77d92e1518e4921')
        self.assertEqual(dh.EFTOPICS['Created'], '0xe8c5062a529781e00d69c769270eb1f1ae6feb921aa80d238bb7b4b919b1ab22')

    def test_both_event_versions_decode_to_the_same_payout(self):
        E = 10 ** 18
        logs = [
            # 2024 version: request with a 0.001 ETH fee; the claim emits paid + fee and the fee
            ef_log(dh.EFTOPICS['CreatedFee'], 7, [2 * E, int(1.8 * E), OWNER, E // 1000], block=100),
            ef_log(dh.EFTOPICS['ClaimedFee'], 7, [2 * E, int(1.79 * E), OWNER, E // 1000], block=300),
            # 2026 version: four fields, the claim emits the payout and the request's full shares
            ef_log(dh.EFTOPICS['Created'], 8, [3 * E, int(2.7 * E), OWNER], block=110),
            ef_log(dh.EFTOPICS['Claimed'], 8, [3 * E, int(2.7 * E), OWNER], block=310),
            ef_log(dh.EFTOPICS['Invalidated'], 9, [], block=120),
            {'address': dh.ETHERFI_WRNFT, 'blockNumber': hex(130), 'logIndex': '0x0', 'transactionHash': '0x1', 'data': '0x',
             'topics': [dh.EFTOPICS['Transfer'], '0x' + '%064x' % OWNER, '0x' + '%064x' % (OWNER + 1), '0x' + '%064x' % 8]},
            {'address': dh.ETHERFI_WRNFT, 'blockNumber': hex(131), 'logIndex': '0x0', 'transactionHash': '0x2', 'data': '0x',
             'topics': [dh.EFTOPICS['Transfer'], '0x' + '00' * 32, '0x' + '%064x' % OWNER, '0x' + '%064x' % 9]},
        ]
        req, clm, flags, transfers, unknown = dh.decode_etherfi_wrnft(logs)
        self.assertAlmostEqual(req[7]['fee'], 0.001)
        self.assertEqual(req[8]['fee'], 0.0)
        self.assertAlmostEqual(clm[7]['paid'], 1.999)          # amount - fee, not the emitted amount
        self.assertAlmostEqual(clm[8]['paid'], 3.0)
        self.assertEqual(req[7]['owner'], '0x' + 'ab' * 20)
        self.assertEqual(flags['invalidated'], [9])
        self.assertEqual(transfers, 1)                          # a mint is not a transfer between holders
        self.assertEqual(unknown, {})

    def test_finalization_is_the_first_admin_execution_covering_the_id_after_the_request(self):
        pts = [(100, 1000, 5), (200, 2000, 9), (300, 3000, 9), (400, 4000, 15)]
        reqs = {4: 50, 6: 150, 9: 190, 10: 250, 16: 410, 3: 120}
        f = dh.finalization_times(pts, reqs)
        self.assertEqual(f[4], (100, 1000))
        self.assertEqual(f[6], (200, 2000))
        self.assertEqual(f[9], (200, 2000))
        self.assertEqual(f[10], (400, 4000))
        self.assertNotIn(16, f)                                 # never covered: pending at the end
        self.assertEqual(f[3], (200, 2000))                     # covered already, but only executions after the request count

    def test_payout_records_price_against_request_and_payout_nav(self):
        reqs = {1: {'block': 100, 'amount': 1.1, 'share': 1.0, 'owner': 'a', 'fee': 0.0, 'version': 4},
                2: {'block': 100, 'amount': 2.2, 'share': 2.0, 'owner': 'a', 'fee': 0.0022, 'version': 5}}
        clm = {1: {'block': 400, 'paid': 1.1, 'fee': 0.0, 'owner': 'a'}, 2: {'block': 400, 'paid': 2.1978, 'fee': 0.0022, 'owner': 'b'}}
        steps = ([50, 300], [1.1, 1.1011])
        nav = lambda n: dh.step_at(steps[0], steps[1], n)
        recs = dh.etherfi_payout_records(reqs, clm, {1: (200, 86400 * 2), 2: (200, 86400 * 2)}, nav, None, lambda n: n * 0 + 86400 if n == 100 else 86400 * 5)
        r1, r2 = recs
        self.assertAlmostEqual(r1['rate_vs_rebase_nav_bps'], 0.0)
        self.assertAlmostEqual(r1['payout_vs_request_bps'], 0.0)
        self.assertAlmostEqual(r1['payout_vs_nav_at_payout_bps'], 1e4 * (1.1 / 1.1011 - 1))   # the yield the queue does not pay
        self.assertAlmostEqual(r1['wait_days'], 1.0)
        self.assertAlmostEqual(r2['fee_bps'], 10.0)
        self.assertAlmostEqual(r2['payout_vs_request_bps'], -10.0, places=6)
        self.assertTrue(r2['owner_changed'])

    def test_step_nav_is_flat_between_rebases_not_a_line(self):
        xs, ys = [100, 200], [1.0, 1.0001]
        self.assertEqual(dh.step_at(xs, ys, 150), 1.0)
        self.assertAlmostEqual(dh.interp(xs, ys, 150), 1.00005)  # the daily line puts half a step where none happened
        self.assertEqual(dh.step_at(xs, ys, 200), 1.0001)
        self.assertIsNone(dh.step_at(xs, ys, 99))

    def test_redeemed_fourth_word_changed_meaning_at_the_2026_upgrade(self):
        E = 10 ** 18
        # pre-2026-07: (amount 100, treasury 0.003, TO RECEIVER 99.7) -> a 30bp fee, not a 9,970bp one
        old = {'address': dh.ETHERFI_RM, 'blockNumber': hex(1), 'topics': [dh.EFTOPICS['Redeemed4'], '0x' + '00' * 32],
               'data': '0x' + enc_uint(100 * E) + enc_uint(3 * E // 1000) + enc_uint(int(99.7 * E))}
        x = dh.decode_redeemed(old)
        self.assertAlmostEqual(x['fee_bps'], 30.0, places=6)
        self.assertEqual(x['token'], 'ETH')
        # 2026-07 on: (amount 100, treasury 0.01, stakers 0.09, stETH) -> a 10bp fee
        new = {'address': dh.ETHERFI_RM, 'blockNumber': hex(2), 'topics': [dh.EFTOPICS['Redeemed'], '0x' + '00' * 32],
               'data': '0x' + enc_uint(100 * E) + enc_uint(E // 100) + enc_uint(9 * E // 100) + enc_uint(int(dh.STETH, 16))}
        y = dh.decode_redeemed(new)
        self.assertAlmostEqual(y['fee_bps'], 10.0, places=6)
        self.assertEqual(y['token'], 'stETH')
        self.assertAlmostEqual(y['to_receiver'], 99.9, places=6)

    def test_regime_table_splits_hours_at_the_cuts(self):
        recs = [{'ts': 3600 * h, 'usd': 1e5, 'discount_bps': d, 'side': 'sell', 'nav': 1.0} for h, d in
                [(0, 30.0), (1, 25.0), (2, 4.0), (10, 12.0), (11, 9.0), (12, 3.0)]]
        rows = dh.regime_table(recs, [('before', 0), ('after', 3600 * 10)])
        self.assertEqual([r['hours'] for r in rows], [3, 3])
        self.assertAlmostEqual(rows[0]['share_at_least_20bp'], 2 / 3)
        self.assertAlmostEqual(rows[1]['share_at_least_20bp'], 0.0)
        self.assertAlmostEqual(rows[1]['share_at_least_10bp'], 1 / 3)

    def test_weighted_median(self):
        self.assertEqual(dh._weighted_median([(1.0, 1.0), (5.0, 10.0), (2.0, 1.0)]), 5.0)
        self.assertIsNone(dh._weighted_median([]))


class NewAssets(unittest.TestCase):
    def test_oeth_cumulative_queue_waits(self):
        day = 86400
        reqs = [(0, 10, 1, 100), (day, 20, 1, 250), (2 * day, 30, 1, 400), (2 * day + 5, 30, 3, 401)]
        claim = [(0, 10, 2, 120),               # funded in the same block, after the request: the 600s delay binds
                 (3 * day, 40, 0, 300),         # covers the second request two days later
                 (4 * day, 50, 0, 400)]         # covers the third; the fourth (401) is never covered
        w = dh.cumulative_waits(reqs, claim, end_ts=5 * day, min_delay_s=600)
        self.assertAlmostEqual(w[0][1], 600 / day)
        self.assertAlmostEqual(w[1][1], 2.0)
        self.assertAlmostEqual(w[2][1], 2.0)
        self.assertIsNone(w[3][1])
        self.assertAlmostEqual(w[3][2], (5 * day - 2 * day - 5) / day)
        # a funding event logged BEFORE the request in the same block does not count for it
        w2 = dh.cumulative_waits([(0, 10, 5, 100)], [(0, 10, 2, 120), (day, 11, 0, 130)], end_ts=2 * day)
        self.assertAlmostEqual(w2[0][1], 1.0)

    def test_btc_wrapper_priced_in_btc_with_eight_decimals_both_sides(self):
        lb = dh.SURFACE['lbtc']
        meta = {'tokens': [dh.WBTC, dh.LBTC], 'decimals': [8, 8], 'fee_bps': 1.0}
        # Fluid swap0to1 = false: token1 (LBTC) in, token0 (WBTC) out -> a sale of 2 LBTC for 2.0080 WBTC
        legs = dh.legs_fluid({'data': data_words(0, 2 * 10 ** 8, 200_800_000, 0)}, meta, lb['targets'])
        self.assertEqual(legs[:2], ('sell', dh.LBTC))
        nav = lambda key, n: 1.0048 if key == 'lbtc_nav' else None
        rec = dh.price_swap(dict(lb, targets={dh.LBTC: {'symbol': 'LBTC', 'nav': 'lbtc_nav'}}), legs, 1, nav)
        self.assertAlmostEqual(rec['price'], 1.004)
        self.assertAlmostEqual(rec['discount_bps'], 1e4 * (1.0048 - 1.004) / 1.0048)   # 8bp under NAV, though 40bp over par
        tb = dh.SURFACE['tbtc']
        # tBTC has 18 decimals against WBTC's 8: a v3 sale of 1 tBTC for 0.9990 WBTC is 10bp under par, not 1e10x off
        m3 = {'tokens': [dh.TBTC, dh.WBTC], 'decimals': [18, 8], 'fee_bps': 1.0}
        log = {'topics': [dh.XTOPICS['V3Swap'], '0x' + '00' * 32, '0x' + '00' * 32], 'data': data_words(10 ** 18, -99_900_000, 0, 0, 0)}
        r3 = dh.price_swap(tb, dh.legs_v3(log, m3, tb['targets']), 1, nav)
        self.assertAlmostEqual(r3['discount_bps'], 10.0, places=6)

    def test_inverted_state_spec(self):
        self.assertTrue(dh.STATE['lbtc_nav']['invert'])
        self.assertGreater(dh.STATE['lbtc_nav']['first_block'], 0)


class LbtcPayouts(unittest.TestCase):
    def test_bech32_and_bech32m_addresses_from_scripts(self):
        # BIP-173 and BIP-350 test vectors
        self.assertEqual(dh.segwit_address('0014751e76e8199196d454941c45d1b3a323f1433bd6'), 'bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4')
        self.assertEqual(dh.segwit_address('5120' + '79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'),
                         'bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0')
        self.assertIsNone(dh.segwit_address('76a914' + '00' * 20 + '88ac'))      # P2PKH is not segwit

    def test_redeem_payload_decoding(self):
        script = '0014' + 'ab' * 20
        inner = 'aa3db85f' + dh.BITCOIN_LCHAIN + enc_uint(int(dh.LBTC, 16)) + enc_uint(int('11' * 20, 16)) + enc_uint(0xa0) + enc_uint(24_880_800) \
            + enc_uint(len(script) // 2) + script + '00' * 10
        outer = enc_uint(0x20) + enc_uint(len(inner) // 2) + inner
        log = {'topics': [dh.LBTC_TOPICS['MessageSent'], '0x' + '00' * 32], 'data': '0x' + outer, 'blockNumber': hex(7), 'transactionHash': '0x1'}
        r = dh.decode_lombard_redeem(log)
        self.assertEqual((r['amount_sats'], r['script'], r['to_bitcoin']), (24_880_800, script, True))
        old = {'topics': [dh.LBTC_TOPICS['UnstakeRequest'], '0x' + '00' * 32], 'blockNumber': hex(8), 'transactionHash': '0x2',
               'data': '0x' + enc_uint(0x40) + enc_uint(6_029_500) + enc_uint(len(script) // 2) + script + '00' * 10}
        self.assertEqual(dh.decode_lombard_redeem(old)['amount_sats'], 6_029_500)

    def test_payout_match_takes_the_rate_or_par_and_skips_unrelated_payments(self):
        pays = [(50, 39_243, 'dust'), (100, 25_006_458, 'payout'), (90, 24_880_800, 'before the request')]
        self.assertEqual(dh.match_btc_payout(95, 24_880_800, 1.00505, pays)[2], 'payout')
        self.assertEqual(dh.match_btc_payout(10, 6_029_500, 1.0, [(20, 6_029_500, 'par')])[2], 'par')
        self.assertIsNone(dh.match_btc_payout(10, 6_029_500, 1.0, [(20, 3_000_000, 'half')]))

if __name__ == '__main__':
    unittest.main()
