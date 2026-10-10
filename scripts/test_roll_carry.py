#!/usr/bin/env python3
"""Expiry calendars, the front/second mapping, the weight formula and the carry P&L signs in roll_carry."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roll_carry as R  # noqa: E402

H = R.HOUR_MS
UTC = dt.timezone.utc


class Calendars(unittest.TestCase):
    def test_published_2026_expiries(self):
        # the three front expiries perp_refs.py recorded on 2026-09-10 from the exchanges' rules
        self.assertEqual(R.expiry('brent', 2026, 11), dt.date(2026, 9, 30))
        self.assertEqual(R.expiry('wti', 2026, 10), dt.date(2026, 9, 22))
        self.assertEqual(R.expiry('ng', 2026, 10), dt.date(2026, 9, 28))

    def test_wti_when_the_25th_is_a_weekend(self):
        # 2026-10-25 is a Sunday: back to Friday the 23rd, then three business days
        self.assertEqual(R.expiry('wti', 2026, 11), dt.date(2026, 10, 20))

    def test_brent_december_expires_end_october(self):
        self.assertEqual(R.expiry('brent', 2026, 12), dt.date(2026, 10, 30))

    def test_holiday_moves_an_expiry(self):
        # ICE Brent Feb-2027 expires on the last UK business day of December 2026: the 31st (28th is a holiday)
        self.assertEqual(R.expiry('brent', 2027, 2), dt.date(2026, 12, 31))
        # NG Jan-2027: 2027-01-01 is a Friday holiday; three business days before -> Tue 2026-12-29
        self.assertEqual(R.expiry('ng', 2027, 1), dt.date(2026, 12, 29))

    def test_front_second_switch_at_expiry(self):
        before = dt.datetime(2026, 9, 30, 12, tzinfo=UTC)
        after = dt.datetime(2026, 9, 30, 19, tzinfo=UTC)
        self.assertEqual(R.front_second('brent', before), ((2026, 11), (2026, 12)))
        self.assertEqual(R.front_second('brent', after), ((2026, 12), (2027, 1)))

    def test_symbols(self):
        self.assertEqual(R.contract_symbol('BZ', 2026, 12), 'BZZ26.NYM')
        self.assertEqual(R.contract_symbol('CL', 2027, 1), 'CLF27.NYM')


class Weights(unittest.TestCase):
    def test_weight_recovers_the_blend(self):
        f1, f2 = 105.0, 100.0
        oracle = 0.6 * f1 + 0.4 * f2
        self.assertAlmostEqual(R.front_weight(oracle, f1, f2), 0.6)

    def test_weight_refuses_a_flat_curve(self):
        self.assertIsNone(R.front_weight(100.1, 100.2, 100.0))


class PnL(unittest.TestCase):
    def test_long_is_paid_when_funding_is_negative(self):
        # funding -0.0004/h: longs receive 4bp an hour; perp and hedge move together
        self.assertAlmostEqual(R.hedged_return(+1, 0.01, 0.01, -0.0004), 0.0004)
        self.assertAlmostEqual(R.hedged_return(-1, 0.01, 0.01, -0.0004), -0.0004)

    def test_hedged_basis_sign(self):
        # the perp falls 50bp more than the hedge: the long loses it, the short gains it
        self.assertAlmostEqual(R.hedged_return(+1, -0.006, -0.001, 0.0), -0.005)
        self.assertAlmostEqual(R.hedged_return(-1, -0.006, -0.001, 0.0), 0.005)

    def test_step_is_a_loss_for_the_long_against_a_futures_hedge(self):
        # oracle rolls 10% of a 5% backwardated spread: index -0.5% while both futures are unchanged; the perp follows
        self.assertAlmostEqual(R.hedged_return(+1, -0.005, 0.0, 0.0), -0.005)


def synthetic_rows(rates, r_perp=0.0):
    t0 = 1_788_220_800_000
    return [{'t': t0 + i * H, 'rate': x, 'r_perp': r_perp, 'close': 100.0} for i, x in enumerate(rates)]


class Strategy(unittest.TestCase):
    def test_enters_on_the_paid_side_with_a_one_hour_lag_and_pays_costs(self):
        rates = [0.0] * 5 + [-0.0004] * 10           # longs paid 350% a year from hour 5
        rows = synthetic_rows(rates)
        rets, pos = R.strategy_returns(rows, [0.0] * len(rows), lookback_h=1, entry_apr=1.0, round_trip_bps=10,
                                       fut_bps_each_way=1.0)
        self.assertEqual(pos[5], 0)                   # hour 5 decides on hour 4's zero rate
        self.assertEqual(pos[6], 1)
        # entry hour: funding 4bp less half the round trip (5bp) and the futures commission (1bp)
        self.assertAlmostEqual(rets[6], 0.0004 - 0.0006)
        self.assertAlmostEqual(rets[7], 0.0004)

    def test_exits_when_the_rate_flips(self):
        rates = [-0.0004] * 5 + [0.0004] * 5
        rows = synthetic_rows(rates)
        _, pos = R.strategy_returns(rows, [0.0] * len(rows), lookback_h=1, entry_apr=1.0)
        self.assertEqual(pos[4], 1)
        self.assertEqual(pos[6], -1)                  # flipped to the newly paid side

    def test_unhedged_takes_the_perp_move(self):
        rows = synthetic_rows([-0.0004] * 4, r_perp=0.01)
        rets, _ = R.strategy_returns(rows, [0.0] * 4, 1, 1.0, round_trip_bps=0, fut_bps_each_way=0, hedged=False)
        self.assertAlmostEqual(rets[2], 0.0104)


class Panel(unittest.TestCase):
    def test_build_panel_aligns_bar_ends_and_maps_contracts(self):
        t0 = int(dt.datetime(2026, 9, 15, 10, tzinfo=UTC).timestamp() * 1000)
        candles = [{'t': t0 + i * H, 'c': 100.0 + i} for i in range(3)]
        funding = [{'time': t0 + (i + 1) * H + 5, 'fundingRate': -0.0001, 'premium': -0.01} for i in range(3)]
        fut = {'BZX26.NYM': {t0 + i * H: 104.0 for i in range(3)}, 'BZZ26.NYM': {t0 + i * H: 100.0 for i in range(3)},
               'BZ=F': {}}
        rows = R.build_panel('xyz:BRENTOIL', funding, candles, fut, 'brent')
        self.assertEqual(rows[0]['front'], 'BZX26.NYM')
        self.assertEqual(rows[0]['second'], 'BZZ26.NYM')
        self.assertAlmostEqual(rows[0]['oracle'], 100.0 / 0.99)
        self.assertAlmostEqual(rows[0]['w'], (100.0 / 0.99 - 100.0) / 4.0)
        self.assertAlmostEqual(rows[1]['r_perp'], 101.0 / 100.0 - 1.0)


class Schedule(unittest.TestCase):
    def test_the_measured_2026_rolls(self):
        days = lambda y, m: [t.date().isoformat() for t, _ in R.roll_steps(y, m)]
        self.assertEqual(days(2026, 9), ['2026-09-08', '2026-09-09', '2026-09-10', '2026-09-11', '2026-09-14'])
        self.assertEqual(days(2026, 10), ['2026-10-07', '2026-10-08', '2026-10-09', '2026-10-12', '2026-10-13'])
        self.assertEqual(days(2026, 8), ['2026-08-07', '2026-08-10', '2026-08-11', '2026-08-12', '2026-08-13'])
        self.assertEqual(days(2026, 7), ['2026-07-08', '2026-07-09', '2026-07-10', '2026-07-13', '2026-07-14'])
        self.assertEqual([round(w, 1) for _, w in R.roll_steps(2026, 9)], [0.8, 0.6, 0.4, 0.2, 0.0])

    def test_step_moves_with_us_daylight_time(self):
        self.assertEqual(R.roll_steps(2026, 9)[0][0].hour, 22)
        self.assertEqual(R.roll_steps(2026, 12)[0][0].hour, 23)

    def test_predicted_weight_through_a_roll_and_an_expiry(self):
        at = lambda *a: dt.datetime(*a, tzinfo=UTC)
        self.assertEqual(R.predicted_weight(at(2026, 9, 8, 12), 'brent'), 1.0)
        self.assertAlmostEqual(R.predicted_weight(at(2026, 9, 9, 3), 'brent'), 0.8)
        self.assertAlmostEqual(R.predicted_weight(at(2026, 9, 15, 3), 'brent'), 0.0)
        # X6 expired on 09-30: the calendar's front is now Z6, which rolls in October, so the weight is 1 again
        self.assertEqual(R.predicted_weight(at(2026, 9, 30, 20), 'brent'), 1.0)
        self.assertEqual(R.predicted_weight(at(2026, 9, 23, 3), 'wti'), 1.0)

    def test_window_pnl_signs_and_cost(self):
        rows = synthetic_rows([-0.0004] * 10)
        w = R.window_pnl(rows, [0.0] * 10, rows[0]['t'] - 1, rows[-1]['t'], +1, round_trip_bps=10, fut_bps_each_way=1)
        self.assertAlmostEqual(w['funding'], 0.004)
        self.assertAlmostEqual(w['cost'], 0.0012)
        self.assertAlmostEqual(w['net'], 0.004 - 0.0012)


class RefsCurve(unittest.TestCase):
    def test_perp_refs_curves_follow_the_calendar(self):
        import perp_refs
        c, e = perp_refs.energy_curves(dt.datetime(2026, 9, 10, 13, tzinfo=UTC))
        # exactly the literal list perp_refs carried on 2026-09-10
        self.assertEqual(c['BRENTOIL'], ['ICEEUR:BRNX2026', 'ICEEUR:BRNZ2026', 'ICEEUR:BRNF2027'])
        self.assertEqual(c['CL'], ['NYMEX:CLV2026', 'NYMEX:CLX2026', 'NYMEX:CLZ2026'])
        self.assertEqual(c['NATGAS'], ['NYMEX:NGV2026', 'NYMEX:NGX2026', 'NYMEX:NGZ2026'])
        self.assertEqual(e['BRENTOIL'][1], '2026-09-30')
        c2, _ = perp_refs.energy_curves(dt.datetime(2026, 10, 9, 13, tzinfo=UTC))
        self.assertEqual(c2['BRENTOIL'][0], 'ICEEUR:BRNZ2026')


if __name__ == '__main__':
    unittest.main()
