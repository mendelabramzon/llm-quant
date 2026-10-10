#!/usr/bin/env python3
"""funding_arb on synthetic series whose answers are known: settlement intervals, signs, fees, the state machine."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funding_arb as F  # noqa: E402

H = F.HOUR_MS
T0 = 1_788_220_800_000  # 2026-09-01 00:00 UTC


def venue(n, every, rate, prem=0.0, offset_ms=0, start=0, px=1.0):
    """A venue settling `rate` every `every` hours from hour `start`, with a flat premium and, unless px is None, a
    flat trade close (px=None leaves the leg to be priced through the premium indices)."""
    sett = [(T0 + j * H + offset_ms, rate) for j in range(start, n, every)]
    premium = {T0 + j * H: prem for j in range(n)}
    closes = {T0 + j * H: px for j in range(n)} if px is not None else {}
    return F.Venue(n).fill(T0, n, sett, premium, closes)


def flat(n, rate_a, rate_b, every_a=1, every_b=1):
    return F.Pair('X', venue(n, every_a, rate_a), venue(n, every_b, rate_b), n)


class Intervals(unittest.TestCase):
    def test_eight_hour_settlements_land_on_their_hours(self):
        v = venue(48, 8, 0.0001, offset_ms=5)      # Binance stamps a few ms after the boundary
        self.assertEqual([j for j, x in enumerate(v.pay) if x], [0, 8, 16, 24, 32, 40])
        self.assertEqual(v.interval_hours, {8: 5})
        self.assertTrue(all(v.live[:41]))

    def test_same_annual_rate_on_different_intervals_is_a_zero_spread(self):
        # 1.25bp an hour on A and 10bp every 8 hours on B are both 10.95% a year.
        p = F.Pair('X', venue(96, 1, 0.0000125), venue(96, 8, 0.0001), 96)
        for k in (24, 72):
            self.assertAlmostEqual(p.window(95, k), 0.0, places=12)
        # an 8-hour window holds exactly one 8-hour settlement wherever it sits
        self.assertAlmostEqual(p.window(47, 8), 0.0, places=12)

    def test_annualisation(self):
        p = flat(48, 0.0001, 0.0)
        self.assertAlmostEqual(p.window(47, 24), 0.0001 * F.HOURS_PER_YEAR)

    def test_window_tolerates_a_few_missing_hours_and_averages_over_the_rest(self):
        a = venue(100, 1, 0.0001)
        b = venue(100, 1, 0.0)
        p = F.Pair('X', a, b, 100)
        for j in (50, 51):                        # two unobservable hours in a 72-hour window: 97% covered
            p.av[j] = 0
            p.s[j] = 0.0
        p.S, p.AV = F.prefix(p.s), F.prefix(p.av)
        self.assertAlmostEqual(p.window(99, 72), 0.0001 * F.HOURS_PER_YEAR)
        for j in (52, 53, 54):                    # five: 93%, refused
            p.av[j] = 0
            p.s[j] = 0.0
        p.S, p.AV = F.prefix(p.s), F.prefix(p.av)
        self.assertIsNone(p.window(99, 72))

    def test_window_refuses_missing_hours(self):
        a = venue(48, 1, 0.0001)
        b = venue(48, 1, 0.0, start=10)            # B starts trading at hour 10
        p = F.Pair('X', a, b, 48)
        self.assertIsNone(p.window(20, 24))
        self.assertIsNotNone(p.window(40, 24))


class Signs(unittest.TestCase):
    def test_short_the_payer_long_the_receiver_collects(self):
        p = flat(200, 0.0002, 0.0)                 # longs pay 2bp an hour on A, nothing on B
        trs = F.simulate(p, 24, 0.5, 0.0, None, 4, 0.0, 0.0)
        self.assertEqual(trs[0]['d'], 1)          # short A, long B
        self.assertGreater(trs[0]['funding'], 0)

    def test_reverse_spread_reverses_the_position(self):
        p = flat(200, 0.0, 0.0002)
        trs = F.simulate(p, 24, 0.5, 0.0, None, 4, 0.0, 0.0)
        self.assertEqual(trs[0]['d'], -1)         # short B, long A
        self.assertGreater(trs[0]['funding'], 0)

    def test_settlements_counted_after_entry_through_exit(self):
        # decisions at hours 24 and 28: enter at 24 (does not take hour 24), exit at 28 (takes hour 28)
        p = flat(30, 0.001, 0.0)
        f, b = p.hold(24, 28)
        self.assertAlmostEqual(f, 4 * 0.001)

    def test_basis_sign_through_the_premium_proxy(self):
        n = 60
        a = venue(n, 1, 0.0, px=None)              # A has no trade closes: priced from B through the premiums
        b = venue(n, 1, 0.0)
        for j in range(30, n):                     # A's book rises 1% over its index at hour 30
            a.prem[j] = 0.01
        p = F.Pair('X', a, b, n)
        f, bas = p.hold(24, 40)
        self.assertAlmostEqual(bas, -0.01)         # short A loses when A's premium rises

    def test_fixed_quantity_basis_on_a_coin_that_halves(self):
        # Both legs halve; B halves 1% less. Short 1 of A and long 1 of B (in notional at entry) make
        # (0.505 - 1) - (0.5 - 1) = +0.5% of entry notional, not the log difference ln(1.01) ~ 1%.
        n = 50
        a = venue(n, 1, 0.0)
        b = venue(n, 1, 0.0)
        for j in range(30, n):
            a.px[j] = 0.5
            b.px[j] = 0.505
        p = F.Pair('X', a, b, n)
        self.assertAlmostEqual(p.hold(24, 40)[1], 0.005)

    def test_funding_scales_with_the_quantity_held(self):
        # 10bp an hour received on a position whose coin halves after 5 hours: 5 x 10bp + 5 x 5bp = 75bp.
        n = 40
        a = venue(n, 1, 0.001)
        b = venue(n, 1, 0.0)
        for j in range(25, n):
            a.px[j] = 0.5
            b.px[j] = 0.5
        p = F.Pair('X', a, b, n)
        self.assertAlmostEqual(p.hold(19, 29)[0], 0.0075)

    def test_synthesised_levels_are_in_the_legs_own_units(self):
        # HL TURBO is quoted per coin, Bybit 1000TURBOUSDT per 1,000 coins. A has real closes only every fourth hour;
        # the hours between are synthesised from B and must land in A's units, or the daily marks jump 1,000x.
        n = 48
        a = venue(n, 1, 0.0, px=None)
        b = venue(n, 1, 0.0, px=3.5)               # 1,000 coins at $0.0035
        for j in range(0, n, 4):
            a.px[j] = 0.0035
        p = F.Pair('X', a, b, n, unit_ratio=1 / 1000)
        self.assertTrue(all(abs(p.pa[j] - 0.0035) < 1e-12 for j in range(n)))
        trs = [{'d': 1, 'i': 4, 'e': 40, 'cost': 0.0}]
        pnl, cap = F.daily_pnl(p, trs, 2)
        self.assertTrue(all(abs(x) < 1e-12 for x in pnl))

    def test_daily_attribution_adds_up_to_the_trade(self):
        n = 24 * 5
        a = venue(n, 1, 0.0003)
        b = venue(n, 8, 0.0001)
        for j in range(n):
            a.px[j] = 1.0 + 0.002 * j
            b.px[j] = 1.0 + 0.0021 * j
        p = F.Pair('X', a, b, n)
        trs = [{'d': 1, 'i': 10, 'e': 100, 'cost': 0.0}]
        f, bas = p.hold(10, 100)
        pnl, cap = F.daily_pnl(p, trs, 5)
        self.assertAlmostEqual(sum(pnl), f + bas)


class Fees(unittest.TestCase):
    def test_round_trip_costs_and_daily_split(self):
        p = flat(24 * 10, 0.0002, 0.0)
        ce = cx = F.leg_cost(4.5, 1.0) + F.leg_cost(5.0, 1.0)
        trs = F.simulate(p, 24, 0.5, 0.0, 72, 4, ce, cx)
        self.assertTrue(trs)
        for t in trs:
            self.assertAlmostEqual(t['cost'], 2 * (5.5 + 6.0) / 1e4)
            self.assertAlmostEqual(t['net'], t['funding'] + t['basis'] - t['cost'])
        pnl, cap = F.daily_pnl(p, trs, 10)
        self.assertAlmostEqual(sum(pnl), sum(t['net'] for t in trs))
        self.assertAlmostEqual(sum(cap) * 24, sum(t['e'] - t['i'] for t in trs))


class StateMachine(unittest.TestCase):
    def switching_pair(self):
        n = 24 * 8
        a = venue(n, 1, 0.0)
        b = venue(n, 1, 0.0)
        for j in range(n):
            a.pay[j] = 0.0002 if j < 24 * 4 else -0.0002   # A pays longs for 4 days, then pays shorts
        return F.Pair('X', a, b, n)

    def test_hysteresis_on_a_day_long_signal(self):
        # 24-hour window: the held spread falls below 0 at hour 108 (11 paying hours against 13), but the reverse
        # trade needs |S| >= 50%, i.e. 16 of 24 hours the other way, first seen at the decision at hour 112.
        trs = F.simulate(self.switching_pair(), 24, 0.5, 0.0, None, 4, 0.0, 0.0)
        self.assertEqual([t['d'] for t in trs], [1, -1])
        self.assertEqual((trs[0]['e'], trs[1]['i']), (108, 112))
        self.assertTrue(trs[1]['forced'])                  # the second trade is closed at the end of data

    def test_flip_at_one_decision_on_a_short_signal(self):
        trs = F.simulate(self.switching_pair(), 4, 0.5, 0.0, None, 4, 0.0, 0.0)
        self.assertEqual([t['d'] for t in trs], [1, -1])
        self.assertEqual(trs[0]['e'], trs[1]['i'])
        self.assertEqual(trs[0]['e'], 100)

    def test_max_hold(self):
        p = flat(24 * 10, 0.0002, 0.0)
        trs = F.simulate(p, 24, 0.5, 0.0, 48, 4, 0.0, 0.0)
        self.assertTrue(all(t['e'] - t['i'] <= 48 for t in trs))
        self.assertGreater(len(trs), 2)

    def test_long_only_never_shorts_the_spot_leg(self):
        p = flat(24 * 5, 0.0, 0.0002)
        p.long_only = True
        self.assertEqual(F.simulate(p, 24, 0.5, 0.0, None, 4, 0.0, 0.0), [])

    def test_forced_exit_when_a_venue_disappears(self):
        n = 24 * 6
        a = venue(n, 1, 0.0002)
        b = venue(n, 1, 0.0)
        for j in range(24 * 3, n):                  # B delists after day 3
            b.live[j] = False
        p = F.Pair('X', a, b, n)
        trs = F.simulate(p, 24, 0.5, 0.0, None, 4, 0.0, 0.0)
        self.assertTrue(trs[-1]['forced'])
        self.assertLessEqual(trs[-1]['e'], 24 * 3)

    def test_decisions_only_on_step(self):
        p = flat(24 * 4, 0.0002, 0.0)
        for t in F.simulate(p, 24, 0.5, 0.0, 30, 4, 0.0, 0.0):
            self.assertEqual(t['i'] % 4, 0)


class Mapping(unittest.TestCase):
    def test_multipliers(self):
        self.assertEqual(F.cex_core('1000PEPE'), (1000, 'PEPE'))
        self.assertEqual(F.cex_core('SHIB1000'), (1000, 'SHIB'))
        self.assertEqual(F.cex_core('1MBABYDOGE'), (1_000_000, 'BABYDOGE'))
        self.assertEqual(F.cex_core('1000000MOG'), (1_000_000, 'MOG'))
        self.assertEqual(F.cex_core('1INCH'), (1, '1INCH'))
        self.assertEqual(F.hl_core('kPEPE'), (1000, 'PEPE'))
        self.assertEqual(F.hl_core('KAITO'), (1, 'KAITO'))

    def test_map_prefers_the_listing_that_is_still_alive(self):
        bn = [{'symbol': 'FOOUSDT', 'base': 'FOO', 'status': 'SETTLING', 'listed_ms': 0, 'delisted_ms': 100},
              {'symbol': '1000FOOUSDT', 'base': '1000FOO', 'status': 'TRADING', 'listed_ms': 0, 'delisted_ms': None}]
        m = F.map_symbols(['kFOO'], bn, [])
        self.assertEqual(m['kFOO']['binance'], '1000FOOUSDT')
        self.assertEqual(m['kFOO']['binance_alternatives'], ['FOOUSDT'])

    def test_price_ratio_identifies_units(self):
        a = venue(48, 1, 0.0)
        b = venue(48, 1, 0.0)
        a.px = [2.0] * 48                           # kFOO = 1000 FOO at $0.002
        b.px = [0.002] * 48
        self.assertAlmostEqual(F.price_ratio(a, b, 1000, 1), 1.0)


class Delisted(unittest.TestCase):
    def test_zero_rows_of_a_delisted_market_are_not_trading(self):
        self.assertFalse(F.hl_row_live({'fundingRate': '0.0', 'premium': '0.0'}))
        self.assertTrue(F.hl_row_live({'fundingRate': '0.0000125', 'premium': '0.0'}))
        self.assertTrue(F.hl_row_live({'fundingRate': '0.0', 'premium': '-0.0000001591'}))


class Books(unittest.TestCase):
    def test_slippage_and_capacity(self):
        mid = 100.0
        asks = [[100.05, 10], [100.10, 10], [100.50, 100]]       # $1,000.5, $1,001, $10,050
        self.assertAlmostEqual(F.slippage_bp(asks, mid, 500), 5.0)
        self.assertIsNone(F.slippage_bp(asks, mid, 1e6))          # deeper than the book shown
        q = F.max_size(asks, mid, 10.0)
        self.assertGreater(q, 1500)
        self.assertLessEqual(F.slippage_bp(asks, mid, q), 10.0 + 1e-6)
        self.assertAlmostEqual(F.depth_within(asks, mid, 10.0), 100.05 * 10 + 100.10 * 10)


if __name__ == '__main__':
    unittest.main()
