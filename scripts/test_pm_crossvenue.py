#!/usr/bin/env python3
"""The cross-venue arbitrage arithmetic on books whose answers are known."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_crossvenue as X  # noqa: E402


class Fees(unittest.TestCase):
    def test_kalshi_fee_matches_the_documented_example_and_rounds_up_to_the_cent(self):
        # docs.kalshi.com fee rounding: a 1-contract buy at $0.055 has a model fee of $0.00363825
        self.assertAlmostEqual(0.07 * 1 * 0.055 * 0.945, 0.00363825)
        self.assertEqual(X.kalshi_fee(1, 0.055), 0.01)
        # 100 contracts at 50c: 0.07 * 100 * 0.25 = $1.75 exactly, no rounding
        self.assertAlmostEqual(X.kalshi_fee(100, 0.50), 1.75)
        # a series with a half multiplier
        self.assertAlmostEqual(X.kalshi_fee(100, 0.50, multiplier=0.5), 0.88)   # 0.875 rounds up

    def test_polymarket_fee_matches_the_published_tables(self):
        # docs.polymarket.com/trading/fees, 100 shares: sports 50c -> $1.25, crypto 10c -> $0.63, politics 90c -> $0.36
        self.assertAlmostEqual(X.polymarket_fee(100, 0.50, 0.05), 1.25)
        self.assertAlmostEqual(round(X.polymarket_fee(100, 0.10, 0.07), 2), 0.63)
        self.assertAlmostEqual(round(X.polymarket_fee(100, 0.90, 0.04), 2), 0.36)
        self.assertEqual(X.polymarket_fee(100, 0.5, 0.0), 0.0)

    def test_pm_fee_rate_from_market_fields(self):
        self.assertEqual(X.pm_fee_rate({'feesEnabled': False, 'feeSchedule': {'rate': 0.05, 'exponent': 1}}), 0.0)
        self.assertEqual(X.pm_fee_rate({'feesEnabled': True, 'feeSchedule': {'rate': '0.04', 'exponent': 1}}), 0.04)
        self.assertEqual(X.pm_fee_rate({'feesEnabled': True, 'feeType': 'sports_fees_v3'}), 0.05)
        with self.assertRaises(ValueError):
            X.pm_fee_rate({'feesEnabled': True, 'feeSchedule': {'rate': 0.04, 'exponent': 2}})


class Books(unittest.TestCase):
    def test_kalshi_asks_are_the_complement_of_the_other_side_bids(self):
        ob = {'orderbook_fp': {'yes_dollars': [['0.40', '100'], ['0.42', '50']],
                               'no_dollars': [['0.55', '30'], ['0.56', '20']]}}
        yes_asks, no_asks = X.kalshi_asks(ob)
        self.assertEqual(yes_asks, [(0.44, 20.0), (0.45, 30.0)])     # best NO bid 0.56 -> YES ask 0.44
        self.assertEqual(no_asks, [(0.58, 50.0), (0.60, 100.0)])     # best YES bid 0.42 -> NO ask 0.58

    def test_kalshi_legacy_cents_form(self):
        yes_asks, no_asks = X.kalshi_asks({'orderbook': {'yes': [[40, 10]], 'no': [[55, 5]]}})
        self.assertEqual(yes_asks, [(0.45, 5.0)])
        self.assertEqual(no_asks, [(0.60, 10.0)])

    def test_pm_asks_sorted_best_first(self):
        b = {'asks': [{'price': '0.62', 'size': '10'}, {'price': '0.61', 'size': '5'}, {'price': '0.7', 'size': '0'}]}
        self.assertEqual(X.pm_asks(b), [(0.61, 5.0), (0.62, 10.0)])


class Pair(unittest.TestCase):
    def test_touch_profit_after_both_fees(self):
        # YES on Kalshi at 0.44 (50 contracts), NO on Polymarket at 0.52 (80 shares): 4c gross gap on 50 pairs
        kf = lambda c, p: X.kalshi_fee(c, p)
        pf = lambda c, p: X.polymarket_fee(c, p, 0.05)
        t = X.touch([(0.44, 50.0)], [(0.52, 80.0)], kf, pf)
        self.assertEqual(t['contracts'], 50.0)
        self.assertAlmostEqual(t['gross_gap'], 0.04)
        fees = X.kalshi_fee(50, 0.44) + 50 * 0.05 * 0.52 * 0.48
        self.assertAlmostEqual(t['fees'], fees)
        self.assertAlmostEqual(t['profit'], 50 - 50 * 0.96 - fees)

    def test_walk_stops_when_the_marginal_pair_no_longer_pays(self):
        leg1 = [(0.40, 10.0), (0.45, 10.0), (0.50, 100.0)]
        leg2 = [(0.50, 15.0), (0.52, 100.0)]
        zero = lambda p: 0.0
        nofee = lambda c, p: 0.0
        w = X.walk(leg1, leg2, zero, zero, nofee, nofee)
        # pairs: 10 @ (0.40+0.50), 5 @ (0.45+0.50), 5 @ (0.45+0.52); next 0.50+0.52 > 1 stops
        self.assertAlmostEqual(w['contracts'], 20.0)
        self.assertAlmostEqual(w['profit'], 10 * 0.10 + 5 * 0.05 + 5 * 0.03)

    def test_walk_respects_fees_in_the_marginal_decision(self):
        w = X.walk([(0.49, 10.0)], [(0.50, 10.0)], lambda p: 0.006, lambda p: 0.006,
                   lambda c, p: 0.006 * c, lambda c, p: 0.006 * c)
        self.assertIsNone(w)          # 1c gross gap, 1.2c of fees: nothing pays

    def test_annualise_floors_the_horizon_and_nets_the_savings_rate(self):
        r, net = X.annualise(1.0, 100.0, 0.25)
        self.assertAlmostEqual(r, 0.01 * 365)                      # floored at one day
        self.assertAlmostEqual(net, 0.01 * 365 - X.SSR)
        r, net = X.annualise(2.0, 100.0, 73.0)
        self.assertAlmostEqual(r, 0.02 * 5)


class Text(unittest.TestCase):
    def test_tokens_drop_stopwords_and_accents(self):
        self.assertEqual(X.tokens('Will Luiz Inácio Lula da Silva win the 2026 election?'),
                         {'luiz', 'inacio', 'lula', 'da', 'silva'})


class NLegs(unittest.TestCase):
    def test_touch_n_matches_the_two_leg_touch(self):
        kf = lambda c, p: X.kalshi_fee(c, p)
        pf = lambda c, p: X.polymarket_fee(c, p, 0.05)
        a = X.touch([(0.44, 50.0)], [(0.52, 80.0)], kf, pf)
        b = X.touch_n([[(0.44, 50.0)], [(0.52, 80.0)]], [kf, pf])
        self.assertAlmostEqual(a['profit'], b['profit'])
        self.assertEqual(b['contracts'], 50.0)

    def test_three_leg_bucket_set_pays_one_in_every_state(self):
        # bucket YES 0.30, Above-low NO 0.20, Above-high YES 0.45: the set costs 0.95 and pays $1 whatever prints
        t = X.touch_n([[(0.30, 10.0)], [(0.20, 10.0)], [(0.45, 10.0)]], [lambda c, p: 0.0] * 3, payout=1.0)
        self.assertAlmostEqual(t['profit'], 10 * 0.05)
        # its complement pays $2 in every state
        t2 = X.touch_n([[(0.71, 5.0)], [(0.81, 5.0)], [(0.56, 5.0)]], [lambda c, p: 0.0] * 3, payout=2.0)
        self.assertAlmostEqual(t2['gross_gap'], 2.0 - 2.08)

    def test_walk_n_three_legs(self):
        legs = [[(0.30, 5.0), (0.32, 5.0)], [(0.20, 10.0)], [(0.45, 3.0), (0.50, 10.0)]]
        w = X.walk_n(legs, [lambda p: 0.0] * 3, [lambda c, p: 0.0] * 3)
        # 3 sets at 0.95, 2 at 1.00 (stop: not < 1)
        self.assertAlmostEqual(w['contracts'], 3.0)
        self.assertAlmostEqual(w['profit'], 3 * 0.05)

    def test_structures_pair_kalshi_yes_with_the_polymarket_complement(self):
        m = {'class': 'football', 'rules_match': 'near-identical', 'reason': 'r', 'kalshi_event': 'E',
             'kalshi_title': 't', 'pm_event': 'p', 'pm_title': 'pt', 'kalshi_close': None, 'pm_close': None,
             'kalshi_label': 'A', 'pm_label': 'A', 'kalshi_ticker': 'E-A', 'pm_yes_token': 'tokA',
             'pm_no_token': 'tokB', 'pm_fee_rate': 0.05, 'kalshi_fee_multiplier': 1}
        s = X.structures([m], [])
        self.assertEqual([(l.get('side'), l.get('token')) for l in s[0]['legs']], [('yes', None), (None, 'tokB')])
        self.assertEqual([(l.get('side'), l.get('token')) for l in s[1]['legs']], [('no', None), (None, 'tokA')])


class History(unittest.TestCase):
    def test_gap_series_picks_the_better_direction_after_fees(self):
        kc = {7200: {'yes_bid': 0.40, 'yes_ask': 0.42, 'volume': 10.0}}
        # Polymarket at 0.50: Kalshi YES 0.42 + Polymarket NO 0.50 (+0 half spread) -> gross 8c
        rows = X.gap_series(kc, {7200: 0.50}, 0.0, 0.0, 1)
        self.assertEqual(rows[0]['dir'], 'kalshi_yes')
        self.assertAlmostEqual(rows[0]['net'], 0.08 - 0.07 * 0.42 * 0.58)
        # Polymarket at 0.30: Kalshi NO 0.60 + Polymarket YES 0.30 -> gross 10c
        rows = X.gap_series(kc, {7200: 0.30}, 0.0, 0.0, 1)
        self.assertEqual(rows[0]['dir'], 'kalshi_no')
        self.assertAlmostEqual(rows[0]['net'], 0.10 - 0.07 * 0.60 * 0.40)

    def test_half_spread_reduces_the_gap(self):
        kc = {7200: {'yes_bid': 0.40, 'yes_ask': 0.42, 'volume': 0.0}}
        a = X.gap_series(kc, {7200: 0.50}, 0.0, 0.0, 1)[0]['net']
        b = X.gap_series(kc, {7200: 0.50}, 0.01, 0.0, 1)[0]['net']
        self.assertAlmostEqual(a - b, 0.01, places=2)

    def test_episodes_join_consecutive_hours(self):
        rows = [{'t': 3600 * k, 'net': v} for k, v in enumerate([0.01, 0.02, -0.01, 0.03, -0.02])]
        ep = X.episodes(rows)
        self.assertEqual([(e['hours'], round(e['peak'], 2)) for e in ep], [(2, 0.02), (1, 0.03)])


class Windows(unittest.TestCase):
    def test_pm_history_terminates_with_a_fractional_end(self):
        import tempfile
        calls = []
        old = X.http_json
        X.http_json = lambda url, venue, cache=None, **kw: calls.append(url) or {'history': []}
        try:
            with tempfile.TemporaryDirectory() as d:
                X.pm_history('tok', 1_000_000, 1_000_000 + 20 * 86400 + 0.75, Path(d))
        finally:
            X.http_json = old
        self.assertEqual(len(calls), 2)          # two 14-day windows, then stop


class Spreads(unittest.TestCase):
    def test_half_spread_from_a_books_snapshot(self):
        import tempfile, json
        screen = [{'id': 'K-1:no', 'touch': {'prices': [0.58, 0.44]}},     # Polymarket YES ask 0.44
                  {'id': 'K-1:yes', 'touch': {'prices': [0.43, 0.60]}}]    # Polymarket NO ask 0.60 -> YES bid 0.40
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / 'books.json'
            f.write_text(json.dumps({'screen': screen}))
            self.assertAlmostEqual(X.pm_half_spreads(f)['K-1'], 0.02)


class Alignment(unittest.TestCase):
    def test_polymarket_points_stamp_to_the_boundary_they_follow(self):
        import tempfile, json
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d)
            (raw / 'history' / 'polymarket').mkdir(parents=True)
            (raw / 'history' / 'polymarket' / 'tok.json').write_text(json.dumps([{'t': 7200 + 32, 'p': 0.4}]))
            self.assertEqual(X.pm_history('tok', 0, 10000, raw), {7200: 0.4})


class Liquidity(unittest.TestCase):
    def test_wide_kalshi_book_or_wide_polymarket_market_is_not_a_price(self):
        self.assertTrue(X.liquid({'k_spread': 0.01}, {'pm_half_spread_used': 0.005}))
        self.assertFalse(X.liquid({'k_spread': 0.20}, {'pm_half_spread_used': 0.005}))
        self.assertFalse(X.liquid({'k_spread': None}, {'pm_half_spread_used': 0.005}))
        self.assertFalse(X.liquid({'k_spread': 0.01}, {'pm_half_spread_used': 0.05}))


if __name__ == '__main__':
    unittest.main()
