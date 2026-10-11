#!/usr/bin/env python3
"""The backtest harness on synthetic series whose answers are known."""
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B  # noqa: E402


def noise(n, mu=0.0, sd=1.0, seed=1):
    r = random.Random(seed)
    return [r.gauss(mu, sd) for _ in range(n)]


def ar1(n, phi, mu=0.0, sd=1.0, seed=2):
    r = random.Random(seed)
    x, out = 0.0, []
    for _ in range(n):
        x = phi * x + r.gauss(0, sd)
        out.append(mu + x)
    return out


class Perf(unittest.TestCase):
    def test_constant_series(self):
        p = B.perf([0.001] * 100, 365)
        self.assertAlmostEqual(p['ann_return'], 0.365)
        self.assertIsNone(p['sharpe'])          # zero variance: no Sharpe, not infinity
        self.assertEqual(p['max_drawdown'], 0.0)
        self.assertEqual(p['hit_rate'], 1.0)

    def test_drawdown_is_peak_to_trough_of_the_sum(self):
        self.assertAlmostEqual(B.max_drawdown([1, 1, -3, 1, -1, 2]), 3.0)
        self.assertAlmostEqual(B.max_drawdown([-1, -1]), 2.0)

    def test_hit_rate_ignores_flat_periods(self):
        p = B.perf([0, 0, 1, -1, 1, 0], 365)
        self.assertAlmostEqual(p['hit_rate'], 2 / 3)
        self.assertAlmostEqual(p['active_share'], 0.5)

    def test_none_and_nan_are_dropped(self):
        self.assertEqual(B.perf([1.0, None, float('nan'), 2.0], 1)['n'], 2)


class Inference(unittest.TestCase):
    def test_newey_west_wider_than_naive_on_autocorrelated_series(self):
        x = ar1(4000, 0.9, mu=0.05, seed=3)
        n = len(x)
        m = sum(x) / n
        naive_t = m / (math.sqrt(sum((v - m) ** 2 for v in x) / n) / math.sqrt(n))
        t, p = B.newey_west_t(x, lags=40)
        self.assertLess(abs(t), abs(naive_t) / 2.0)

    def test_newey_west_finds_a_real_mean(self):
        t, p = B.newey_west_t(noise(5000, mu=0.1, seed=4))
        self.assertGreater(t, 4)
        self.assertLess(p, 1e-4)

    def test_bootstrap_brackets_the_mean_and_is_reproducible(self):
        x = noise(800, mu=0.2, seed=5)
        a = B.block_bootstrap(x, n=500)
        b = B.block_bootstrap(x, n=500)
        self.assertEqual(a, b)
        self.assertLess(a['lo'], a['point'])
        self.assertGreater(a['hi'], a['point'])
        self.assertLess(a['p_le_0'], 0.01)

    def test_bootstrap_of_zero_mean_noise_is_not_significant(self):
        r = B.block_bootstrap(noise(800, seed=6), n=500)
        self.assertLess(r['lo'], 0)
        self.assertGreater(r['hi'], 0)


class MultipleTesting(unittest.TestCase):
    def test_bh_textbook_example(self):
        p = [0.01, 0.04, 0.03, 0.005, 0.2]
        rej, adj = B.bh(p, q=0.05)
        self.assertEqual(rej, [True, True, True, True, False])
        self.assertAlmostEqual(adj[3], 0.025)
        self.assertAlmostEqual(adj[1], 0.05)   # 0.04 x 5 / 4, then the running minimum from the top

    def test_bh_keeps_none(self):
        rej, adj = B.bh([None, 0.001], q=0.1)
        self.assertEqual(rej, [False, True])
        self.assertIsNone(adj[0])

    def test_expected_max_sharpe_grows_with_trials(self):
        self.assertEqual(B.expected_max_sharpe(1, 1.0), 0.0)
        self.assertLess(B.expected_max_sharpe(10, 1.0), B.expected_max_sharpe(1000, 1.0))
        self.assertAlmostEqual(B.expected_max_sharpe(100, 1.0), 2.53, places=1)

    def test_deflated_sharpe_punishes_the_best_of_many_noise_series(self):
        series = [noise(500, seed=s) for s in range(50)]
        best = max(series, key=lambda x: sum(x))
        self.assertLess(B.deflated_sharpe(best, 50), 0.9)
        self.assertGreater(B.deflated_sharpe(noise(500, mu=0.5, seed=99), 50), 0.99)


class Protocol(unittest.TestCase):
    def test_walk_forward_never_overlaps(self):
        folds = list(B.walk_forward(100, 40, 20))
        self.assertEqual(len(folds), 3)
        for tr, te in folds:
            self.assertTrue(set(tr).isdisjoint(te))
            self.assertEqual(tr.stop, te.start)

    def test_choose_then_test_picks_on_the_past_only(self):
        # 'late' is excellent in the second half only, 'early' in the first half only: the protocol must choose
        # 'early' and then report it doing badly out of sample.
        n = 2000
        early = noise(n // 2, mu=0.3, seed=10) + noise(n // 2, mu=-0.1, seed=11)
        late = noise(n // 2, mu=-0.1, seed=12) + noise(n // 2, mu=0.3, seed=13)
        r = B.choose_then_test({'early': early, 'late': late}, frac=0.5, periods_per_year=365)
        self.assertEqual(r['chosen'], 'early')
        self.assertLess(r['out_of_sample']['ann_return'], 0)
        self.assertEqual(r['oos_rank'], 2)
        self.assertTrue(r['in_sample_positive'])

    def test_bh_positive_survivors_exclude_significant_losers(self):
        # a strong loser passes the two-sided BH; only the winner passes the one-sided test for a positive mean
        n = 2000
        win = noise(n, mu=0.4, seed=31)
        lose = noise(n, mu=-0.4, seed=32)
        r = B.choose_then_test({'win': win, 'lose': lose}, frac=0.5, periods_per_year=365, key='ann_return')
        self.assertIn('lose', r['bh_survivors_full_sample'])
        self.assertEqual(r['bh_survivors_positive'], ['win'])

    def test_choose_then_test_flags_a_least_bad_choice(self):
        # every variant loses before the split; the chosen one is only the least bad, and the flag says so
        n = 2000
        a = noise(n // 2, mu=-0.2, seed=20) + noise(n // 2, mu=0.3, seed=21)
        b = noise(n // 2, mu=-0.5, seed=22) + noise(n // 2, mu=0.0, seed=23)
        r = B.choose_then_test({'a': a, 'b': b}, frac=0.5, periods_per_year=365, key='ann_return')
        self.assertEqual(r['chosen'], 'a')
        self.assertFalse(r['in_sample_positive'])
        self.assertGreater(r['out_of_sample']['ann_return'], 0)


if __name__ == '__main__':
    unittest.main()
