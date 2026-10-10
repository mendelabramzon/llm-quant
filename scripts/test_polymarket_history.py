#!/usr/bin/env python3
"""polymarket_history: every return, fee, annualisation and neg-risk formula on cases whose answer is known."""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import polymarket_history as P  # noqa: E402

DAY = P.DAY
T0 = 1_780_000_000.0


class Fees(unittest.TestCase):
    def test_docs_examples(self):
        # docs.polymarket.com/trading/fees: 100 shares; crypto 0.07 at 0.50 -> $1.75; at 0.10 -> $0.63;
        # sports 0.05 at 0.50 -> $1.25; politics 0.04 at 0.30 -> $0.84
        self.assertAlmostEqual(100 * P.fee_per_share(0.07, 0.5), 1.75)
        self.assertAlmostEqual(100 * P.fee_per_share(0.07, 0.1), 0.63)
        self.assertAlmostEqual(100 * P.fee_per_share(0.05, 0.5), 1.25)
        self.assertAlmostEqual(100 * P.fee_per_share(0.04, 0.3), 0.84)

    def test_geopolitics_is_free(self):
        self.assertEqual(P.fee_rate('politics', ['Geopolitics', 'Iran']), 0.0)
        self.assertEqual(P.fee_rate('politics', ['Politics']), 0.04)
        self.assertEqual(P.fee_rate('sports', []), 0.05)
        self.assertEqual(P.fee_rate('science_tech', ['Weather', 'Daily Temperature']), 0.05)
        self.assertEqual(P.fee_rate('science_tech', ['Tech', 'AI']), 0.04)
        self.assertEqual(P.fee_rate('economics', ['Finance', 'Stocks']), 0.04)
        self.assertEqual(P.fee_rate('crypto_price', ['Crypto']), 0.07)


class Returns(unittest.TestCase):
    def test_win_loss_and_fifty(self):
        self.assertAlmostEqual(P.trade_return(0.9, 1.0), 1 / 0.9 - 1)
        self.assertAlmostEqual(P.trade_return(0.9, 0.0), -1.0)
        self.assertAlmostEqual(P.trade_return(0.9, 0.5), 0.5 / 0.9 - 1)

    def test_spread_and_fee_are_paid_on_the_fill(self):
        px = 0.91
        cost = px + 0.05 * px * (1 - px)
        self.assertAlmostEqual(P.trade_return(0.9, 1.0, half_spread=0.01, rate=0.05), 1 / cost - 1)

    def test_fill_is_capped_below_one(self):
        self.assertAlmostEqual(P.trade_return(0.995, 1.0, half_spread=0.01), 1 / 0.999 - 1)

    def test_annualised_per_capital_day(self):
        # 5% earned over 36.5 capital-days is 50% a year
        self.assertAlmostEqual(P.annualised(0.05, 36.5), 0.5)
        self.assertIsNone(P.annualised(0.05, 0))


class Helpers(unittest.TestCase):
    def test_wilson(self):
        lo, hi = P.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)
        lo, hi = P.wilson(0, 10)
        self.assertAlmostEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)

    def test_as_of_respects_staleness(self):
        s = [[100, 0.4], [200, 0.5], [300, 0.6]]
        self.assertIsNone(P.as_of(s, 99))
        self.assertEqual(P.as_of(s, 250), 0.5)
        self.assertEqual(P.as_of(s, 300), 0.6)
        self.assertIsNone(P.as_of(s, 1000, max_stale=500))
        self.assertEqual(P.as_of(s, 700, max_stale=500), 0.6)

    def test_binary_payout(self):
        self.assertEqual(P.binary_payout({'outcomePrices': [1.0, 0.0]}), 1.0)
        self.assertEqual(P.binary_payout({'outcomePrices': [0.0, 1.0]}), 0.0)
        self.assertEqual(P.binary_payout({'outcomePrices': [0.5, 0.5]}), 0.5)
        self.assertIsNone(P.binary_payout({'outcomePrices': [0.3, 0.7]}))
        self.assertIsNone(P.binary_payout({'outcomePrices': [0.0, 0.0]}))

    def test_favourite_flips_the_payout(self):
        self.assertEqual(P.favourite(0.3, 1.0), (1, 0.7, 0.0))
        self.assertEqual(P.favourite(0.8, 1.0), (0, 0.8, 1.0))
        self.assertEqual(P.favourite(0.2, 0.5), (1, 0.8, 0.5))

    def test_parse_ts_formats(self):
        a = P.parse_ts('2026-04-05 06:15:11+00')
        b = P.parse_ts('2026-04-05T06:15:11Z')
        self.assertEqual(a, b)
        self.assertEqual(P.parse_ts('2026-04-05T06:15:11.123456Z'), b + 0.123456)
        self.assertIsNone(P.parse_ts(None))

    def test_categories(self):
        self.assertEqual(P.categorize(['Crypto', 'Up or Down'], 'Bitcoin Up or Down - 3PM'), 'crypto_updown')
        self.assertEqual(P.categorize(['NBA', 'Sports'], 'Lakers vs Celtics'), 'sports')
        self.assertEqual(P.categorize(['Crypto Prices'], 'Will BTC hit 150k?'), 'crypto_price')
        self.assertEqual(P.categorize([], 'x', 'Sports'), 'sports')
        self.assertEqual(P.categorize([], 'x'), 'other')

    def test_fine_window_never_exceeds_the_endpoint_limit(self):
        m = {'closedTime': '2026-04-05T00:00:00Z', 'acceptingOrdersTimestamp': '2026-01-01T00:00:00Z'}
        a, b, fid = P.fine_window(m)
        self.assertLessEqual(b - a, 14.5 * DAY + 1)
        self.assertEqual(fid, 60)
        m = {'closedTime': '2026-04-05T00:00:00Z', 'acceptingOrdersTimestamp': '2026-04-04T23:00:00Z'}
        a, b, fid = P.fine_window(m)
        self.assertEqual(fid, 5)

    def test_sampling_is_deterministic_and_weighted(self):
        uni = []
        for i in range(2000):
            uni.append({'id': str(i), 'cat': 'sports', 'volumeNum': 20000, 'outcomes': ['A', 'B'],
                        'clobTokenIds': ['1', '2'], 'outcomePrices': [1.0, 0.0],
                        'closedTime': '2026-04-05T00:00:00Z', 'endDate': '2026-04-04T00:00:00Z'})
        plan = P.sample_plan(uni, {'10k-100k': 500})
        self.assertAlmostEqual(plan[('sports', '10k-100k')][1], 0.25)
        s1, s2 = P.draw_sample(uni, plan), P.draw_sample(uni, plan)
        self.assertEqual(s1, s2)
        self.assertTrue(400 < len(s1) < 600)
        self.assertTrue(all(abs(r['weight'] - 4.0) < 1e-9 for r in s1))


class NegRisk(unittest.TestCase):
    def book(self, asks, bids):
        return {'asks': asks, 'bids': bids}

    def test_sums_and_top_size(self):
        bk = [self.book([(0.30, 100)], [(0.28, 50)]), self.book([(0.30, 40)], [(0.29, 70)]),
              self.book([(0.35, 80)], [(0.33, 10)])]
        s = P.neg_risk_sums(bk)
        self.assertAlmostEqual(s['sum_ask'], 0.95)
        self.assertAlmostEqual(s['sum_bid'], 0.90)
        self.assertEqual(s['ask_baskets'], 40)
        self.assertEqual(s['bid_baskets'], 10)

    def test_missing_side_makes_the_basket_unbuyable(self):
        s = P.neg_risk_sums([self.book([], [(0.2, 5)]), self.book([(0.5, 5)], [(0.4, 5)])])
        self.assertIsNone(s['sum_ask'])
        self.assertAlmostEqual(s['sum_bid'], 0.6)

    def test_buy_all_yes_walks_levels_until_unprofitable(self):
        # top: 0.30 + 0.30 + 0.35 = 0.95 for 40 sets; next level of member 2 at 0.36 -> 0.96 for 60 more sets;
        # member 2 then 0.45 -> 1.05: stop.
        bk = [self.book([(0.30, 1000)], []), self.book([(0.30, 40), (0.31, 1000)], []),
              self.book([(0.35, 100), (0.45, 1000)], [])]
        f = P.basket_fill(bk, 'ask')
        self.assertAlmostEqual(f['sets'], 100)
        self.assertAlmostEqual(f['cost'], 40 * 0.95 + 60 * 0.96)
        self.assertAlmostEqual(f['profit'], 100 - (40 * 0.95 + 60 * 0.96))

    def test_buy_all_no_profits_when_bids_sum_above_one(self):
        # bids 0.5, 0.4, 0.2 sum to 1.1: NO costs 0.5 + 0.6 + 0.8 = 1.9 per set and pays n - 1 = 2
        bk = [self.book([], [(0.5, 10)]), self.book([], [(0.4, 10)]), self.book([], [(0.2, 10)])]
        f = P.basket_fill(bk, 'bid')
        self.assertAlmostEqual(f['sets'], 10)
        self.assertAlmostEqual(f['cost'], 19.0)
        self.assertAlmostEqual(f['payout'], 20.0)
        self.assertAlmostEqual(f['profit'], 1.0)

    def test_fees_can_kill_a_thin_arbitrage(self):
        bk = [self.book([(0.495, 100)], []), self.book([(0.495, 100)], [])]
        self.assertGreater(P.basket_fill(bk, 'ask')['profit'], 0)
        self.assertEqual(P.basket_fill(bk, 'ask', rates=[0.05, 0.05])['sets'], 0)


class Calibration(unittest.TestCase):
    def test_logistic_recovers_a_known_slope(self):
        import random
        rng = random.Random(4)
        x, y = [], []
        for _ in range(4000):
            xi = rng.uniform(-3, 3)
            pz = 1 / (1 + math.exp(-(0.2 + 1.5 * xi)))
            x.append(xi)
            y.append(1.0 if rng.random() < pz else 0.0)
        a, b = P.logistic_fit(x, y, [1.0] * len(x))
        self.assertAlmostEqual(a, 0.2, delta=0.12)
        self.assertAlmostEqual(b, 1.5, delta=0.15)

    def test_perfectly_calibrated_favourites_give_slope_one(self):
        import random
        rng = random.Random(9)
        tr = []
        for i in range(3000):
            p = rng.uniform(0.5, 0.99)
            tr.append({'h': '1d', 'fifty': False, 'p': p, 'pay': 1.0 if rng.random() < p else 0.0, 'w': 1.0,
                       'event': str(i)})
        c = P.calibration_slope(tr, '1d', n_boot=50)
        self.assertAlmostEqual(c['b'], 1.0, delta=0.2)
        self.assertLess(c['b_lo'], 1.0)
        self.assertGreater(c['b_hi'], 1.0)


class NegRiskSummary(unittest.TestCase):
    def row(self, at, ev, aug=False, inc=False, yes=None, no=None, sa=1.1, sb=0.9):
        return {'at': at, 'event': ev, 'title': 't', 'augmented': aug, 'incomplete': inc, 'members_live': 3,
                'sum_ask': sa, 'sum_bid': sb, 'buy_all_yes': yes, 'buy_all_no': no}

    def test_classes_and_persistence(self):
        arb = {'sets': 10, 'cost': 9.5, 'payout': 10, 'profit': 0.5, 'ann_excess': 2.0}
        rows = [self.row('a', 'e1', yes=arb, sa=0.95), self.row('b', 'e1', yes=arb, sa=0.95),
                self.row('a', 'e2', aug=True, yes=dict(arb, profit=5.0), sa=0.5),
                self.row('a', 'e3', inc=True, yes=arb, sa=0.6), self.row('b', 'e4')]
        s = P.summarize_negrisk_live(rows)
        self.assertEqual(s['snapshots'], 2)
        self.assertEqual(s['clean']['arbs_after_fees'], 2)
        self.assertEqual(s['clean']['persistence_next_snapshot'], 1.0)   # e1 at 'a' is still there at 'b'
        self.assertEqual(s['augmented']['arbs_after_fees'], 1)
        self.assertEqual(s['incomplete']['arbs_after_fees'], 1)
        self.assertAlmostEqual(s['clean']['arb_profit_usd_per_snapshot'], 0.5)


class LagFlow(unittest.TestCase):
    def test_routes_are_split_and_losing_token_trades_ignored(self):
        tr = [{'asset': 'W', 'side': 'BUY', 'price': 0.98, 'size': 100, 'proxyWallet': 'a', 'timestamp': 1},
              {'asset': 'W', 'side': 'BUY', 'price': 0.99, 'size': 100, 'proxyWallet': 'b', 'timestamp': 2},
              {'asset': 'L', 'side': 'SELL', 'price': 0.01, 'size': 50, 'proxyWallet': 'b', 'timestamp': 3},
              {'asset': 'W', 'side': 'SELL', 'price': 0.99, 'size': 70, 'proxyWallet': 'c', 'timestamp': 4},
              {'asset': 'W', 'side': 'BUY', 'price': 0.50, 'size': 70, 'proxyWallet': 'c', 'timestamp': 5}]
        f = P.lag_flow_market(tr, 'W', 'L', min_price=0.9)
        self.assertEqual(f['taker_buys'], 2)
        self.assertAlmostEqual(f['pool_usd'], 100 * 0.02 + 100 * 0.01)
        self.assertAlmostEqual(f['volume_usd'], 98 + 99)
        self.assertEqual(f['maker_fills'], 1)
        self.assertAlmostEqual(f['maker_pool_usd'], 70 * 0.01)
        self.assertAlmostEqual(f['top_wallet_share'], 2.0 / 3.0)
        g = P.lag_flow_market(tr, 'W', 'L', min_price=0.9, rate=0.07)
        self.assertAlmostEqual(g['pool_usd'], 100 * (0.02 - 0.07 * 0.98 * 0.02) + 100 * (0.01 - 0.07 * 0.99 * 0.01))
        self.assertAlmostEqual(g['maker_pool_usd'], 0.7)   # makers pay no fee


class Backtest(unittest.TestCase):
    def test_daily_series_annualises_to_the_capital_day_rate(self):
        tr = [{'t': T0, 'close': T0 + 9 * DAY, 'w': 1.0}]
        s, k, cap = P.daily_series(tr, [0.1], T0, T0 + 9 * DAY, ssr=0.0)
        self.assertEqual(len(s), 10)
        self.assertAlmostEqual(k, 1.0)
        self.assertAlmostEqual(sum(s), 0.1)
        s2, _, _ = P.daily_series(tr, [0.1], T0, T0 + 9 * DAY, ssr=0.0365)
        self.assertAlmostEqual(sum(s2), 0.1 - 10 * 0.0365 / 365)

    def test_summarize_weights_and_rates(self):
        tr = [{'t': T0, 'close': T0 + 10 * DAY, 'w': 1.0, 'pay': 1.0, 'p': 0.9, 'event': 'a'},
              {'t': T0, 'close': T0 + 10 * DAY, 'w': 3.0, 'pay': 0.0, 'p': 0.9, 'event': 'b'}]
        r = [1 / 0.9 - 1, -1.0]
        s = P.summarize(tr, r)
        self.assertAlmostEqual(s['win_rate'], 0.25)
        self.assertAlmostEqual(s['mean_return'], (r[0] - 3.0) / 4.0)
        self.assertAlmostEqual(s['ann_return'], (r[0] - 3.0) / 40.0 * 365)
        self.assertAlmostEqual(s['ann_excess'], s['ann_return'] - P.SSR)

    def test_entries_use_the_scheduled_end_and_only_past_prices(self):
        # A market scheduled to end at E, closing at C = E + 2 days. The price is 0.6 until E - 2 days, then 0.93;
        # after E it goes to 0.985 and stays. The 7d entry must see 0.6, the 1d entry 0.93, and strategy C at 0.98
        # must enter at the first post-E point at or above 0.98, never before E.
        E = T0 + 20 * DAY
        C = E + 2 * DAY
        with tempfile.TemporaryDirectory() as d:
            m = {'id': 'm1', 'event_id': 'e1', 'cat': 'politics', 'tags': ['Politics'], 'volumeNum': 2e5,
                 'outcomes': ['Yes', 'No'], 'clobTokenIds': ['1', '2'], 'outcomePrices': [1.0, 0.0],
                 'endDate': P.utc(E), 'closedTime': P.utc(C), 'acceptingOrdersTimestamp': P.utc(T0),
                 'umaResolutionStatuses': []}
            coarse = [[int(T0 + k * 12 * 3600), 0.6] for k in range(36)]
            fine = [[int(E - 14 * DAY + k * 3600), 0.6 if k < 12 * 24 else 0.93] for k in range(14 * 24)]
            fine += [[int(E + k * 3600), 0.97 if k < 3 else 0.985] for k in range(1, 40)]
            P.write_gz(P.price_path(d, 'm1', 'c'), coarse)
            P.write_gz(P.price_path(d, 'm1', 'f'), fine)
            A, Cr, meta = P.build_trades(d, {'m1': m}, [{'id': 'm1', 'weight': 1.0}])
        byh = {t['h']: t for t in A}
        self.assertAlmostEqual(byh['7d']['p'], 0.6)
        self.assertAlmostEqual(byh['1d']['p'], 0.93)
        self.assertAlmostEqual(byh['6h']['p'], 0.93)
        c98 = [t for t in Cr if t['th'] == 0.98][0]
        self.assertGreaterEqual(c98['t'], E)
        self.assertAlmostEqual(c98['p'], 0.985)
        self.assertEqual(c98['t'], int(E + 3 * 3600))
        c95 = [t for t in Cr if t['th'] == 0.95][0]
        self.assertEqual(c95['t'], int(E + 3600))        # 0.97 clears 0.95 at the first post-E point
        self.assertAlmostEqual(c95['p'], 0.97)
        self.assertEqual(byh['3d']['p'], 0.6)
        self.assertEqual(byh['7d']['pay'], 1.0)

    def test_cluster_bootstrap_is_reproducible(self):
        tr = [{'t': T0, 'close': T0 + DAY, 'w': 1.0, 'event': str(i % 7)} for i in range(50)]
        r = [0.01 if i % 3 else -0.02 for i in range(50)]
        self.assertEqual(P.cluster_bootstrap(tr, r, n=200), P.cluster_bootstrap(tr, r, n=200))


if __name__ == '__main__':
    unittest.main()
