#!/usr/bin/env python3
"""Pair construction, alignment and P&L signs in hip3_pairs, on synthetic books."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hip3_pairs as P  # noqa: E402

H = P.HOUR_MS
T0 = 1_788_220_800_000


class Pairs(unittest.TestCase):
    def test_builder_pairs_only_and_both_with_oi(self):
        uni = [{'dex': 'xyz', 'coin': 'xyz:NBIS', 'oi': 1.0}, {'dex': 'io', 'coin': 'io:NBIS', 'oi': 2.0},
               {'dex': 'core', 'coin': 'NBIS', 'oi': 5.0}, {'dex': 'para', 'coin': 'para:NBIS', 'oi': 0.0}]
        self.assertEqual(P.pairs_in(uni), [('io:NBIS', 'xyz:NBIS')])

    def test_pair_return_signs(self):
        # A's longs pay 0.1%/h more than B's: short A / long B (p=-1) receives it when prices do not move
        self.assertAlmostEqual(P.pair_return(-1, 0.0, 0.0, 0.0012, 0.0002), 0.001)
        # and loses when A outperforms B by 50bp
        self.assertAlmostEqual(P.pair_return(-1, 0.006, 0.001, 0.0, 0.0), -0.005)

    def test_align_requires_consecutive_hours(self):
        a = {T0: (0.0, 100.0), T0 + H: (0.0, 101.0), T0 + 3 * H: (0.0, 102.0)}
        b = {T0: (0.0, 50.0), T0 + H: (0.0, 50.5), T0 + 3 * H: (0.0, 51.0)}
        rows = P.align(a, b)
        self.assertIsNone(rows[0]['ra'])
        self.assertAlmostEqual(rows[1]['ra'], 0.01)
        self.assertIsNone(rows[2]['ra'])           # the gap at T0+2H breaks the return

    def test_rule_enters_the_receiving_side_and_charges_both_legs(self):
        rows = [{'t': T0 + i * H, 'fa': 0.0010, 'fb': 0.0, 'ra': 0.0, 'rb': 0.0} for i in range(6)]
        rets, pos, entries = P.run_rule(rows, k=1, x=1.0, rt_a_bps=20, rt_b_bps=40)
        self.assertEqual(pos[0], 0)
        self.assertEqual(pos[1], -1)
        self.assertEqual(entries, 1)
        self.assertAlmostEqual(rets[1], 0.0010 - 0.0030)    # one hour of funding less half of 20bp + 40bp
        self.assertAlmostEqual(rets[2], 0.0010)


if __name__ == '__main__':
    unittest.main()
