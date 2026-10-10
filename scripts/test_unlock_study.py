#!/usr/bin/env python3
"""Identity matching, event construction and trade P&L signs in unlock_study, on synthetic data."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import unlock_study as U  # noqa: E402

H, D = U.HOUR_MS, U.DAY_MS
T0 = 1_780_000_000_000 // H * H


def s_from(prices, rates=None, step=H):
    keys = [T0 + i * step for i in range(len(prices))]
    closes = dict(zip(keys, prices))
    fund = dict(zip(keys, rates or [0.0] * len(prices)))
    return keys, closes, fund


class Identity(unittest.TestCase):
    def test_price_check_removes_a_symbol_collision(self):
        idx = [{'tokenPrice': [{'symbol': 'W', 'price': 0.08}]}, {'tokenPrice': [{'symbol': 'ARB', 'price': 0.30}]}]
        uni = [{'dex': 'core', 'coin': 'W', 'mark': 0.30}, {'dex': 'core', 'coin': 'ARB', 'mark': 0.31}]
        m, rej = U.match_tokens(idx, uni)
        self.assertEqual(sorted(m), ['ARB'])
        self.assertEqual(rej, ['W'])

    def test_thousand_unit_tickers(self):
        self.assertEqual(U.hl_symbol_scale('kPEPE'), ('PEPE', 1000.0))
        self.assertEqual(U.hl_symbol_scale('KAITO'), ('KAITO', 1.0))
        idx = [{'tokenPrice': [{'symbol': 'PEPE', 'price': 0.00001}]}]
        m, _ = U.match_tokens(idx, [{'dex': 'core', 'coin': 'kPEPE', 'mark': 0.0101}])
        self.assertIn('kPEPE', m)


class Events(unittest.TestCase):
    def test_cliffs_merge_by_day_and_filter_categories(self):
        pf = {'metadata': {'events': [
            {'unlockType': 'cliff', 'category': 'insiders', 'timestamp': 1_780_000_100, 'noOfTokens': [10]},
            {'unlockType': 'cliff', 'category': 'privateSale', 'timestamp': 1_780_000_200, 'noOfTokens': [5, 5]},
            {'unlockType': 'cliff', 'category': 'airdrop', 'timestamp': 1_780_000_300, 'noOfTokens': [99]},
            {'unlockType': 'linear_start', 'category': 'insiders', 'timestamp': 1_780_000_400, 'noOfTokens': [7]}]}}
        ev = U.cliff_events(pf)
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]['tokens'], 20)
        self.assertEqual(ev[0]['categories'], ['insiders', 'privateSale'])

    def test_unlocked_on_sums_allocations_as_of_a_day(self):
        doc = {'data': [{'data': [{'timestamp': 100, 'unlocked': 1}, {'timestamp': 200, 'unlocked': 3}]},
                        {'data': [{'timestamp': 150, 'unlocked': 10}]}]}
        self.assertEqual(U.unlocked_on(doc, 199), 11)
        self.assertEqual(U.unlocked_on(doc, 99), 0)


class Trade(unittest.TestCase):
    def test_short_coin_long_btc_signs(self):
        n = 24 * 10
        coin = s_from([100.0 * math.exp(-0.10 * i / n) for i in range(n)], rates=[0.0001] * n)
        btc = s_from([50_000.0] * n, rates=[0.00005] * n)
        T = T0 + 5 * D
        tr = U.window_trade(coin, btc, T, -3, 3, rt_bps=10, btc_rt_bps=10)
        self.assertLess(tr['abnormal'], 0)                       # the coin fell against BTC
        self.assertAlmostEqual(tr['funding_short_received'], 0.0001 * 24 * 6, places=9)
        self.assertAlmostEqual(tr['funding_btc_long_paid'], 0.00005 * 24 * 6, places=9)
        self.assertAlmostEqual(tr['pnl'], -tr['abnormal'] + tr['funding_short_received'] - tr['funding_btc_long_paid'] - 0.002)
        self.assertGreater(tr['pnl'], 0)

    def test_missing_price_gives_none(self):
        coin = s_from([1.0] * 10)
        btc = s_from([1.0] * 10)
        self.assertIsNone(U.window_trade(coin, btc, T0 + 5 * D, -1, 1))


class Placebo(unittest.TestCase):
    def test_welch_t(self):
        self.assertIsNone(U.welch_t([1, 2], [1, 2, 3]))
        t = U.welch_t([1.0, 1.1, 0.9, 1.05], [0.0, 0.1, -0.1, 0.05])
        self.assertGreater(t, 10)


    def test_by_day_collapses_same_day_events(self):
        D = U.DAY_MS
        self.assertEqual(U.by_day([(D + 5, 1.0), (D + 9, 3.0), (3 * D, 5.0)]), [2.0, 5.0])


if __name__ == '__main__':
    unittest.main()
