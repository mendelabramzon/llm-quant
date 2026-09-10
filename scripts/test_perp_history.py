#!/usr/bin/env python3
"""Sign conventions and segmentation in perp_history, pinned with synthetic series where the answer is known."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perp_history as P  # noqa: E402

H = P.HOUR_MS
T0 = 1_788_220_800_000  # 2026-09-01 00:00 UTC


def series(rates, closes=None, premiums=None):
    closes = closes or [100.0] * len(rates)
    premiums = premiums or [0.0] * len(rates)
    return [{'t': T0 + k * H, 'rate': r, 'premium': p, 'close': c, 'open': c, 'high': c, 'low': c,
             'volume_usd': 1.0, 'trades': 1} for k, (r, c, p) in enumerate(zip(rates, closes, premiums))]


class SignConventions(unittest.TestCase):
    def test_negative_funding_pays_longs(self):
        self.assertEqual(P.paid_side(-1e-4), 'long')
        self.assertEqual(P.paid_side(2e-4), 'short')
        self.assertAlmostEqual(P.received(-1e-4, 'long'), 1e-4)
        self.assertAlmostEqual(P.received(-1e-4, 'short'), -1e-4)
        self.assertAlmostEqual(P.received(3e-4, 'short'), 3e-4)

    def test_hold_accumulates_funding_and_mark(self):
        # long entered at close 100; the mark rises 1% over two hours; each hour pays the long 0.05%.
        S = series([-5e-4, -5e-4, -5e-4], closes=[100.0, 100.5, 101.0])
        r = P.hold(S, 0, 'long')
        self.assertEqual(r['hours'], 2)
        self.assertAlmostEqual(r['funding'], 1e-3)
        self.assertAlmostEqual(r['mark'], 0.01)
        self.assertAlmostEqual(r['total'], 0.011)
        # the same hours on the short side: paying the funding and losing the move
        r = P.hold(S, 0, 'short')
        self.assertAlmostEqual(r['total'], -0.011)

    def test_hold_hedged_proxy_uses_premium_change(self):
        S = series([-5e-4, -5e-4], closes=[100.0, 100.0], premiums=[-0.005, -0.007])
        r = P.hold(S, 0, 'long')
        # premium widened from -50bp to -70bp: a long hedged in the oracle loses 20bp and collects 5bp
        self.assertAlmostEqual(r['hedged_proxy'], 5e-4 - 0.002)

    def test_hold_drawdown(self):
        S = series([0.0, 0.0, 0.0, 0.0], closes=[100.0, 102.0, 99.0, 101.0])
        r = P.hold(S, 0, 'long')
        self.assertAlmostEqual(r['max_drawdown'], -0.03)  # from +2% to -1%


class Episodes(unittest.TestCase):
    def test_segments_on_sign_and_threshold(self):
        apr100 = 1.0 / P.HOURS_PER_YEAR
        rates = [0.0, -2 * apr100, -2 * apr100, -2 * apr100, 0.5 * apr100, 3 * apr100, 3 * apr100, 0.0]
        S = series(rates)
        eps = P.episodes(S, min_apr=1.0)
        self.assertEqual([(e['side'], e['hours']) for e in eps], [('long', 3), ('short', 2)])
        # held from the close before the run to the close of the first sub-threshold hour: three payments of 2x
        # to the long, then one hour at +0.5x that the long pays
        self.assertAlmostEqual(eps[0]['funding_received'], (3 * 2 - 0.5) * apr100)
        self.assertAlmostEqual(eps[0]['mean_apr'], 2.0)
        self.assertEqual(eps[0]['exit_t'], S[4]['t'])
        self.assertAlmostEqual(eps[1]['funding_received'], (3 + 3 + 0.0) * apr100)

    def test_gap_in_hours_breaks_a_run(self):
        apr100 = 1.0 / P.HOURS_PER_YEAR
        S = series([-2 * apr100] * 4)
        S[2]['t'] += H  # a missing hour between index 1 and 2
        S[3]['t'] += H
        eps = P.episodes(S, min_apr=1.0)
        self.assertEqual([e['hours'] for e in eps], [2, 2])

    def test_flip_lookahead(self):
        apr100 = 1.0 / P.HOURS_PER_YEAR
        S = series([-2 * apr100, -2 * apr100] + [0.1 * apr100] * 3)
        eps = P.episodes(S, min_apr=1.0)
        self.assertTrue(eps[0]['sign_flipped_within_72h'])

    def test_longest_run(self):
        apr100 = 1.0 / P.HOURS_PER_YEAR
        S = series([-2 * apr100, -2 * apr100, 2 * apr100, -2 * apr100, -2 * apr100, -2 * apr100])
        self.assertEqual(P.longest_run(S, 1.0), 3)


class Snaps(unittest.TestCase):
    def test_snap_reports_implied_oracle_move(self):
        # premium goes from -0.7% to 0 while the mark is unchanged: the implied oracle fell by ~0.7%
        S = series([-1e-3, 0.0], closes=[100.0, 100.0], premiums=[-0.007, 0.0])
        sn = P.premium_snaps(S, min_jump=0.004)
        self.assertEqual(len(sn), 1)
        self.assertAlmostEqual(sn[0]['mark_move'], 0.0)
        self.assertAlmostEqual(sn[0]['implied_oracle_move'], math.log(1 / 1.00704934), places=5)  # 100/(1-0.007) -> 100

    def test_small_moves_ignored(self):
        S = series([0.0, 0.0], premiums=[0.001, 0.002])
        self.assertEqual(P.premium_snaps(S, min_jump=0.004), [])


class Alignment(unittest.TestCase):
    def test_hour_rounding_and_candle_alignment(self):
        self.assertEqual(P.hour_of(T0 + 19), T0)
        self.assertEqual(P.hour_of(T0 + H - 5), T0 + H)
        fund = [{'time': T0 + H + 19, 'fundingRate': '-0.0001', 'premium': '-0.001'}]
        cand = [{'t': T0, 'c': '100', 'o': '99', 'h': '101', 'l': '98', 'v': '10', 'n': 3},
                {'t': T0 + H, 'c': '105', 'o': '100', 'h': '106', 'l': '99', 'v': '10', 'n': 3}]
        S = P.hourly_series(fund, cand)
        self.assertEqual(len(S), 1)
        self.assertEqual(S[0]['t'], T0 + H)
        self.assertEqual(S[0]['close'], 100.0)  # the candle that ENDED at T0+1h, not the one that started there
        self.assertEqual(S[0]['volume_usd'], 1000.0)

    def test_merge_rows_dedupes(self):
        old = [{'time': 1, 'x': 'a'}, {'time': 2, 'x': 'b'}]
        new = [{'time': 2, 'x': 'B'}, {'time': 3, 'x': 'c'}]
        m = P.merge_rows(old, new, 'time')
        self.assertEqual([r['x'] for r in m], ['a', 'B', 'c'])


if __name__ == '__main__':
    unittest.main()
