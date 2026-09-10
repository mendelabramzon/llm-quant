#!/usr/bin/env python3
"""The roll-premium detector on synthetic curves where the arithmetic is known."""
import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perp_scan as P  # noqa: E402


def args(out, **kw):
    d = dict(out=out, size_usd=1e5, horizon_h=24, roll_days=10.0, min_spread_pct=1.0)
    d.update(kw)
    return argparse.Namespace(**d)


def market(coin, funding_hourly, premium, ask=1.77e6, bid=3.2e6, rt=12.6, oi_cap=5e8, oi=2.4e8):
    return {'coin': coin, 'delisted': False, 'funding_hourly': funding_hourly, 'premium': premium,
            'oi_cap_usd': oi_cap, 'oi_usd': oi,
            'book': {'round_trip_bps_100k': rt, 'ask_depth_25bp_usd': ask, 'bid_depth_25bp_usd': bid}}


def curve(coin, w_o, w_m, spread_pct):
    return {coin: {'implied_front_weight_oracle_median': w_o, 'implied_front_weight_mark_median': w_m,
                   'front_over_second_pct_median': spread_pct, 'last': {'contracts': {}}, 'front_expiry': None}}


class RollPremium(unittest.TestCase):
    def run_det(self, assets, curves, tape_rows=None):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'refs_curve.json').write_text(json.dumps({'rows': curves}))
            if tape_rows is not None:
                (Path(d) / 'tape.json').write_text(json.dumps({'rows': tape_rows}))
            return P.det_roll_premium({'assets': assets}, args(d))

    def test_backwardation_pays_longs_net_of_step(self):
        # Brent-like: oracle 0.60 front weight, book 0.45, spread +4.67%, funding -0.0437%/h (longs paid)
        hits = self.run_det([market('xyz:BRENTOIL', -0.000437, -0.0070)], curve('xyz:BRENTOIL', 0.60, 0.45, 4.67))
        self.assertEqual(len(hits), 1)
        h = hits[0]
        e = h['evidence']
        self.assertAlmostEqual(e['lead'], 0.15, places=6)
        self.assertAlmostEqual(e['predicted_premium'], -0.15 * 0.0467, places=6)
        self.assertTrue(e['curve_fits'])
        ec = h['economics']
        self.assertEqual(ec['side_paid'], 'long')
        self.assertAlmostEqual(ec['funding_apr'], 0.000437 * 24 * 365, places=6)
        self.assertAlmostEqual(ec['roll_step_apr'], 0.0467 / 10 * 365, places=6)
        self.assertTrue(ec['net_apr'] > 1.0)
        self.assertTrue(ec['go'])
        self.assertEqual(ec['capacity_usd'], 1.77e6)   # ask side for a long, below the cap headroom

    def test_contango_pays_shorts_and_step_still_costs(self):
        hits = self.run_det([market('xyz:NATGAS', 0.000396, 0.0066, bid=33e3)], curve('xyz:NATGAS', 0.59, 0.46, -4.69))
        h = hits[0]
        self.assertAlmostEqual(h['evidence']['predicted_premium'], 0.13 * 0.0469, places=6)
        self.assertEqual(h['economics']['side_paid'], 'short')
        self.assertAlmostEqual(h['economics']['roll_step_apr'], 0.0469 / 10 * 365, places=6)
        self.assertFalse(h['economics']['go'])           # the bid side is $33k of depth
        self.assertEqual(h['economics']['capacity_usd'], 33e3)

    def test_curve_that_does_not_fit_is_declined(self):
        # the book sits where the curve says but the observed premium is three times larger: not a roll
        hits = self.run_det([market('xyz:CL', -0.0012, -0.020)], curve('xyz:CL', 0.61, 0.44, 3.9))
        self.assertFalse(hits[0]['evidence']['curve_fits'])
        self.assertFalse(hits[0]['economics']['go'])

    def test_tape_gap_preferred_over_snapshot(self):
        hits = self.run_det([market('xyz:BRENTOIL', -0.000437, -0.0030)], curve('xyz:BRENTOIL', 0.60, 0.45, 4.67),
                            tape_rows=[{'coin': 'xyz:BRENTOIL', 'gap_bps_mean': -70.0}])
        self.assertEqual(hits[0]['evidence']['observed_from'], 'tape')
        self.assertAlmostEqual(hits[0]['evidence']['observed_premium'], -0.0070, places=9)

    def test_flat_curve_and_missing_file_give_nothing(self):
        self.assertEqual(self.run_det([market('xyz:GOLD', 0.00001, 0.0001)], curve('xyz:GOLD', 0.99, 0.93, -0.75)), [])
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(P.det_roll_premium({'assets': []}, args(d)), [])


if __name__ == '__main__':
    unittest.main()
