#!/usr/bin/env python3
"""The temperature-ladder arithmetic on cases whose answers are known: buckets, probabilities, fees, fills, timing."""
import datetime as dt
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_weather as W  # noqa: E402


class Buckets(unittest.TestCase):
    def test_kalshi_strikes_map_to_inclusive_integer_ranges(self):
        # 'greater than 92' pays on 93+, 'less than 85' on 84-, 'between 91-92' on 91 and 92 (KXHIGHNY-26AUG13 rules)
        self.assertEqual(W.bucket_bounds('greater', 92, None), (93, None))
        self.assertEqual(W.bucket_bounds('less', None, 85), (None, 84))
        self.assertEqual(W.bucket_bounds('between', 91, 92), (91, 92))
        with self.assertRaises(ValueError):
            W.bucket_bounds('above', 1, 2)

    def test_a_ladder_partitions_the_integers(self):
        ladder = [W.bucket_bounds(*x) for x in [('less', None, 85), ('between', 85, 86), ('between', 87, 88),
                                                 ('between', 89, 90), ('between', 91, 92), ('greater', 92, None)]]
        for t in range(60, 110):
            self.assertEqual(sum(W.pays_yes(lo, hi, t) for lo, hi in ladder), 1, t)

    def test_polymarket_labels(self):
        self.assertEqual(W.pm_bucket('76-77°F'), (76, 77))
        self.assertEqual(W.pm_bucket('75°F or below'), (None, 75))
        self.assertEqual(W.pm_bucket('86°F or higher'), (86, None))
        self.assertEqual(W.pm_bucket('18°C'), (18, 18))
        self.assertEqual(W.pm_bucket('-2°C or below'), (None, -2))
        self.assertIsNone(W.pm_bucket('Other'))


class Probabilities(unittest.TestCase):
    def test_bucket_probabilities_sum_to_one_and_respect_rounding(self):
        ladder = [(None, 84), (85, 86), (87, 88), (89, 90), (91, 92), (93, None)]
        ps = [W.bucket_prob(lo, hi, 88.3, 2.1) for lo, hi in ladder]
        self.assertAlmostEqual(sum(ps), 1.0, places=12)
        # a single integer k owns [k - 0.5, k + 0.5): with mu exactly k and a tiny sd it is certain
        self.assertAlmostEqual(W.bucket_prob(88, 88, 88.0, 0.01), 1.0, places=6)
        self.assertAlmostEqual(W.bucket_prob(87, 88, 88.4, 0.01), 1.0, places=6)
        self.assertAlmostEqual(W.bucket_prob(89, 90, 88.4, 0.01), 0.0, places=6)
        # symmetric: mu at a boundary splits the mass
        self.assertAlmostEqual(W.bucket_prob(None, 88, 88.5, 1.0), 0.5, places=12)

    def test_randomised_pit_is_inside_the_observed_mass(self):
        lo = W.norm_cdf((70 - 0.5 - 71.2) / 2.0)
        hi = W.norm_cdf((70 + 0.5 - 71.2) / 2.0)
        self.assertAlmostEqual(W.pit_value(70, 71.2, 2.0, 0.0), lo)
        self.assertAlmostEqual(W.pit_value(70, 71.2, 2.0, 1.0), hi)

    def test_error_model_recovers_bias_and_spread(self):
        import random
        rng = random.Random(3)
        pairs = []
        for i in range(2000):
            x = rng.choice([1.5, 2.5, 3.5])
            pairs.append((1 + i % 365, 1.0 + rng.gauss(0, math.sqrt(1.0 + 0.5 * x * x)), x))
        m = W.fit_error_model(pairs)
        self.assertAlmostEqual(m['overall_bias'], 1.0, delta=0.1)
        self.assertAlmostEqual(m['bias'][180], 1.0, delta=0.3)
        self.assertAlmostEqual(m['c'], 0.5, delta=0.2)
        self.assertAlmostEqual(m['a'], 1.0, delta=0.6)


class Distribution(unittest.TestCase):
    def test_kernel_cdf_is_a_cdf_and_bucket_probabilities_still_sum_to_one(self):
        zs = [-2.0, -0.5, 0.0, 0.3, 1.8]
        F = W.kernel_cdf(zs, 0.3)
        self.assertAlmostEqual(F(-50), 0.0, places=9)
        self.assertAlmostEqual(F(50), 1.0, places=9)
        self.assertLess(F(-0.1), F(0.1))
        ladder = [(None, 84), (85, 86), (87, 88), (89, 90), (91, 92), (93, None)]
        ps = [W.bucket_prob(lo, hi, 88.3, 2.1, F) for lo, hi in ladder]
        self.assertAlmostEqual(sum(ps), 1.0, places=9)

    def test_predictive_applies_bias_and_seasonal_scale(self):
        m = {'bias': {d: 0.5 for d in range(1, 367)}, 'a': 1.0, 'c': 0.5, 'med_xnd': 2.0,
             'scale': {d: (4.0 if d == 196 else 1.0) for d in range(1, 367)}}
        mu, sd = W.predictive(m, '2026-07-15', 80.0, 2.0)        # day 196
        self.assertAlmostEqual(mu, 80.5)
        self.assertAlmostEqual(sd, math.sqrt(4.0 * (1.0 + 0.5 * 4.0)))
        mu, sd = W.predictive(m, '2026-07-16', 80.0, None)       # missing spread -> the training median
        self.assertAlmostEqual(sd, math.sqrt(1.0 + 0.5 * 4.0))

    def test_seasonal_variance_scale_tracks_a_seasonal_error(self):
        import random
        rng = random.Random(5)
        pairs = []
        for i in range(730):
            d = 1 + i % 365
            sd = 3.0 if 150 <= d <= 250 else 1.5
            pairs.append((d, rng.gauss(0, sd), 2.0))
        m = W.fit_error_model(pairs, seasonal_var=True)
        self.assertGreater(m['scale'][200], 1.5)
        self.assertLess(m['scale'][20], 0.8)
        flat = W.fit_error_model(pairs, seasonal_var=False)
        self.assertEqual(set(flat['scale'].values()), {1.0})


class Costs(unittest.TestCase):
    def test_half_spread_lookup_by_band_with_a_floor_on_sample_size(self):
        table = {'pm_half_spread': {W.pband(0.30): {'n': 10, 'median': 0.015}, W.pband(0.02): {'n': 3, 'median': 0.0}}}
        self.assertEqual(W.pm_hs_for(table, 0.30), 0.015)
        self.assertEqual(W.pm_hs_for(table, 0.02), 0.01)          # too few books: the default
        self.assertEqual(W.pband(0.05), '0.05-0.15')
        self.assertEqual(W.pband(0.999), '0.95-1.00')

    def test_kalshi_taker_cost_includes_the_rounded_fee(self):
        # 100 contracts at 40c: 0.07 * 100 * 0.4 * 0.6 = $1.68 -> 1.68c a contract
        self.assertAlmostEqual(W.kalshi_taker_cost(0.40), 0.4168)
        # 100 contracts at 1c: 0.07 * 100 * 0.01 * 0.99 = 0.0693 -> rounds up to $0.07
        self.assertAlmostEqual(W.kalshi_taker_cost(0.01), 0.0107)

    def test_polymarket_taker_cost(self):
        # weather rate 0.05 (market feeSchedule 2026-10-14): 50c pays 1.25c a share
        self.assertAlmostEqual(W.pm_taker_cost(0.5, 0.05), 0.5125)
        self.assertAlmostEqual(W.pm_taker_cost(0.5, 0.0), 0.5)

    def test_trade_pnl(self):
        self.assertAlmostEqual(W.trade_pnl(0.5, 1), 1.0)
        self.assertAlmostEqual(W.trade_pnl(0.5, 0), -1.0)

    def test_maker_fills_only_on_a_trade_through(self):
        self.assertFalse(W.maker_filled(0.30, [0.31, 0.30, None]))   # touching the level is not a fill (queue)
        self.assertTrue(W.maker_filled(0.30, [0.35, 0.29]))
        self.assertFalse(W.maker_filled(0.30, []))

    def test_floor_cent(self):
        self.assertEqual(W.floor_cent(0.379), 0.37)
        self.assertEqual(W.floor_cent(0.37), 0.37)


class Timing(unittest.TestCase):
    def test_event_date_from_ticker(self):
        self.assertEqual(W.kalshi_event_date('KXHIGHNY-26AUG13'), '2026-08-13')
        self.assertIsNone(W.kalshi_event_date('KXHIGHNY'))

    def test_local_decision_times_follow_daylight_saving(self):
        # 16:00 New York the day before: 20:00 UTC in summer, 21:00 UTC in winter
        t = W.local_ts('2026-07-15', -1, 16, 'America/New_York')
        self.assertEqual(dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(), '2026-07-14T20:00:00+00:00')
        t = W.local_ts('2026-01-15', -1, 16, 'America/New_York')
        self.assertEqual(dt.datetime.fromtimestamp(t, dt.timezone.utc).isoformat(), '2026-01-14T21:00:00+00:00')

    def test_forecast_at_never_uses_a_run_before_it_is_published(self):
        T = 1_000_000.0
        runs = [(T - 10 * 3600, 70.0, 2.0), (T - 3 * 3600, 71.0, 2.0), (T - 2 * 3600, 72.0, 2.0)]
        # lag 2.5 h: the run 2 h old is not out yet, the 3 h old one is
        self.assertEqual(W.forecast_at(runs, T)[1], 71.0)
        self.assertIsNone(W.forecast_at([(T - 40 * 3600, 70.0, 2.0)], T))   # too old

    def test_candle_and_price_lookups_are_as_of(self):
        cs = [{'t': 100}, {'t': 3700}, {'t': 7300}]
        self.assertEqual(W.candle_at(cs, 3700)['t'], 3700)
        self.assertEqual(W.candle_at(cs, 3699)['t'], 100)
        self.assertIsNone(W.candle_at(cs, 50))
        ps = [[3660, 0.4], [7260, 0.5]]
        self.assertEqual(W.price_at(ps, 3600), 0.4)       # the point a minute after the hour is the hour's price
        self.assertEqual(W.price_at(ps, 7200), 0.5)
        self.assertIsNone(W.price_at(ps, 0))


class Diagnostics(unittest.TestCase):
    def test_implied_mean_uses_normalised_mids_and_bucket_centres(self):
        rows = []
        for lo, hi, mid in [(None, 69, 0.0), (70, 71, 0.5), (72, 73, 0.5), (74, None, 0.0)]:
            rows.append({'venue': 'polymarket', 'key': 'NYC', 'date': 'd', 'dec': 'd1_16', 'lo': lo, 'hi': hi,
                         'mid': mid, 'obs': 71, 'mu': 72.0})
        out = W.implied_mean_diag(rows)['polymarket|d1_16']
        # implied = 0.5 * 70.5 + 0.5 * 72.5 = 71.5 -> bias +0.5 against 71; model 72 -> +1
        self.assertAlmostEqual(out['market_bias'], 0.5)
        self.assertAlmostEqual(out['model_bias'], 1.0)
        self.assertAlmostEqual(out['market_minus_model_mean'], -0.5)


class Metar(unittest.TestCase):
    def test_daily_max_is_local_day_and_rounded(self):
        tz = 'America/New_York'
        # 2026-07-15 local: 04:00Z is 00:00 EDT; 03:51Z belongs to the 14th
        def ts(h, m):
            return dt.datetime(2026, 7, 15, h, m, tzinfo=dt.timezone.utc).timestamp()
        rows = [(ts(3, 51), 99.0), (ts(4, 51), 80.06), (ts(18, 51), 84.92), (ts(19, 12), 85.5)]
        mx = W.metar_daily_max(rows, tz)
        self.assertEqual(mx['2026-07-15'], 86)                 # 85.5 rounds half up
        self.assertEqual(mx['2026-07-14'], 99)
        self.assertEqual(W.metar_daily_max(rows, tz, minute=51)['2026-07-15'], 85)
        # whole-degree C body group: 85.5F = 29.72C -> 30C -> 86F
        self.assertAlmostEqual(W.f_to_wholec_f(85.5), 86.0)


class Rule(unittest.TestCase):
    def row(self, **kw):
        r = {'venue': 'kalshi', 'dec': 'd0_08', 'result': 1, 'type': 'interior', 'p': 0.60, 'ask': 0.45, 'bid': 0.40,
             'ask1': 0.55, 'bid1': 0.50, 'later_ask_low': [0.50, 0.44], 'later_bid_high': [0.41],
             'later_ask_low1': [0.60], 'later_bid_high1': [0.52], 'date': '2026-05-01', 'key': 'X', 'id': 'X-1',
             'hold_days': 1.0, 'T': 0}
        r.update(kw)
        return r

    def test_taker_buys_the_side_with_edge_and_books_the_payout(self):
        tr = W.trades_for([self.row()], ('kalshi', 'd0_08', 0.10, 'taker', 'all'))
        self.assertEqual(len(tr), 1)
        self.assertEqual(tr[0]['side'], 'yes')
        self.assertAlmostEqual(tr[0]['cost'], W.kalshi_taker_cost(0.45))
        self.assertEqual(tr[0]['payout'], 1)
        # NO side: model 0.20 for YES, YES bid 0.70 -> NO costs 0.30 + fee against 0.80
        tr = W.trades_for([self.row(p=0.20, ask=0.75, bid=0.70, result=0)], ('kalshi', 'd0_08', 0.10, 'taker', 'all'))
        self.assertEqual([t['side'] for t in tr], ['no'])
        self.assertEqual(tr[0]['payout'], 1)
        # bucket-type filter
        self.assertEqual(W.trades_for([self.row()], ('kalshi', 'd0_08', 0.10, 'taker', 'tail')), [])

    def test_late_entry_reprices_and_can_drop_the_trade(self):
        self.assertEqual(W.trades_for([self.row()], ('kalshi', 'd0_08', 0.10, 'taker', 'all'), late=True), [])

    def test_maker_rests_below_the_ask_and_needs_a_trade_through(self):
        tr = W.trades_for([self.row()], ('kalshi', 'd0_08', 0.10, 'maker', 'all'))
        # limit = min(0.60 - 0.10, 0.45 - 0.01) = 0.44; later ask low 0.44 is not below it -> no YES fill
        self.assertEqual(tr, [])
        tr = W.trades_for([self.row(later_ask_low=[0.43])], ('kalshi', 'd0_08', 0.10, 'maker', 'all'))
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]['cost'], 0.44)

    def test_polymarket_taker_pays_half_spread_and_fee(self):
        table = {'pm_half_spread': {W.pband(0.30): {'n': 10, 'median': 0.01}}}
        r = {'venue': 'polymarket', 'dec': 'd1_16', 'result': 0, 'type': 'interior', 'p': 0.50, 'mid': 0.30,
             'mid1': 0.31, 'fee_rate': 0.05, 'date': '2026-05-01', 'key': 'NYC', 'id': 'm', 'hold_days': 1.5, 'T': 0}
        tr = W.trades_for([r], ('polymarket', 'd1_16', 0.10, 'taker', 'all'), table)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]['cost'], 0.31 + 0.05 * 0.31 * 0.69)
        self.assertEqual(tr[0]['payout'], 0)

    def test_polymarket_maker_rests_below_the_ask_and_needs_a_later_ask_below_it(self):
        table = {'pm_half_spread': {W.pband(0.30): {'n': 10, 'median': 0.01}, W.pband(0.20): {'n': 10, 'median': 0.01}}}
        r = {'venue': 'polymarket', 'dec': 'd1_16', 'result': 1, 'type': 'interior', 'p': 0.50, 'mid': 0.30,
             'mid1': 0.31, 'fee_rate': 0.05, 'date': '2026-05-01', 'key': 'NYC', 'id': 'm', 'hold_days': 1.5, 'T': 0,
             'later_mids': [0.29, 0.28], 'later_mids1': [0.40]}
        v = ('polymarket', 'd1_16', 0.10, 'maker', 'all')
        # YES limit = min(0.50 - 0.10, 0.31 - 0.01) = 0.30; later ask proxies 0.30, 0.29 -> 0.29 < 0.30 fills
        tr = W.trades_for([r], v, table)
        self.assertEqual([(t['side'], round(t['cost'], 3)) for t in tr], [('yes', 0.3)])
        # an hour later the asks never go below the limit
        self.assertEqual(W.trades_for([r], v, table, late=True), [])

    def test_constant_capital_series_has_the_sign_of_pooled_profit(self):
        # a tiny stake that pays 10x and a large stake that loses: per-day-stake mean is positive, pooled is not
        trades = [{'date': '2026-01-01', 'payout': 1, 'cost': 0.1}, {'date': '2026-01-02', 'payout': 0, 'cost': 0.9},
                  {'date': '2026-05-01', 'payout': 0, 'cost': 0.5}]
        days = ['2026-01-01', '2026-01-02', '2026-05-01']
        ratio = W.daily_series(trades, days)
        self.assertGreater(sum(ratio[:2]), 0)                          # +9.0 and -1.0
        const = W.daily_pnl_series(trades, days, cutoff='2026-04-01')
        base = (0.1 + 0.9) / 2                                          # mean in-sample daily stake
        self.assertAlmostEqual(const[0], 0.9 / base)
        self.assertAlmostEqual(const[1], -0.9 / base)
        self.assertAlmostEqual(sum(const[:2]), 0.0)                     # pooled in-sample profit is zero
        self.assertAlmostEqual(const[2], -0.5 / base)

    def test_daily_series_is_profit_over_capital_by_day(self):
        trades = [{'date': 'a', 'payout': 1, 'cost': 0.5}, {'date': 'a', 'payout': 0, 'cost': 0.5},
                  {'date': 'c', 'payout': 0, 'cost': 0.25}]
        self.assertEqual(W.daily_series(trades, ['a', 'b', 'c']), [0.0, 0.0, -1.0])


if __name__ == '__main__':
    unittest.main()
