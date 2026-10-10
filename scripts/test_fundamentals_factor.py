#!/usr/bin/env python3
"""Signal timing, portfolio construction, P&L signs and the detector replay in fundamentals_factor, on synthetic data."""
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fundamentals_factor as FF  # noqa: E402

D0 = FF.dnum('2024-01-01')          # a Monday


def flat_series(start, n, value):
    return {start + i: float(value) for i in range(n)}


class Missing(unittest.TestCase):
    def test_empty_stablecoin_reading_is_missing_not_zero(self):
        rows = FF._trim_stables([{'date': '86400', 'totalCirculatingUSD': {'peggedUSD': 5.0}},
                                 {'date': '172800', 'totalCirculatingUSD': {}},
                                 {'date': '259200', 'totalCirculatingUSD': {'peggedUSD': 7.0}}])
        self.assertEqual(rows[1], [172800, None])
        s = FF.chart_series(rows)
        self.assertEqual(sorted(s), [1, 3])        # day 2 is absent, not zero
        self.assertNotIn(2, s)

    def test_combine_stock_carries_a_member_forward_but_not_forever(self):
        a = {1: 10.0, 2: 10.0, 3: 10.0, 4: 10.0, 5: 10.0, 6: 10.0, 7: 10.0, 8: 10.0}
        b = {1: 5.0, 2: 5.0}                        # b stops reporting after day 2
        c = FF.combine([a, b], stock=True)
        self.assertEqual(c[3], 15.0)                # carried
        self.assertEqual(c[5], 15.0)                # three days of carry
        self.assertNotIn(6, c)                      # then the day is missing, not a $5 outflow
        f = FF.combine([a, b], stock=False)
        self.assertEqual(f[3], 10.0)                # a flow sums what is there


class Timing(unittest.TestCase):
    def setUp(self):
        n = 400
        self.fund = {'stables': {D0 - n + i: 1e8 * math.exp(0.002 * i) for i in range(n)},
                     'tvl': flat_series(D0 - n, n, 5e8), 'dex': flat_series(D0 - n, n, 1e6),
                     'fees': flat_series(D0 - n, n, 5e4)}
        self.row = {'mom_4w': 0.1, 'mom_12w': 0.2}
        self.total = flat_series(D0 - n, n, 1e11)

    def sig(self, fund):
        return FF.signals_for(('chains', 'x'), fund, self.row, D0, self.total)

    def test_signal_ignores_the_publication_lag_days(self):
        base = self.sig(self.fund)
        self.assertIsNotNone(base['stables_4w'])
        f2 = {k: dict(v) for k, v in self.fund.items()}
        for d in (D0 - 1, D0, D0 + 3):              # Sunday, Monday, later: not yet published at Monday 00:00
            f2['stables'][d] = 9e12
            f2['dex'][d] = 9e12
        self.assertEqual(self.sig(f2), base)
        f3 = {k: dict(v) for k, v in self.fund.items()}
        f3['stables'][D0 - FF.LAG_DAYS] = 9e12      # Saturday's reading is in
        f3['dex'][D0 - FF.LAG_DAYS] = 9e12
        s3 = self.sig(f3)
        self.assertGreater(s3['stables_4w'], base['stables_4w'])
        self.assertGreater(s3['dex_4w'], base['dex_4w'])

    def test_growth_is_the_log_change_of_window_means(self):
        s = self.sig(self.fund)
        self.assertAlmostEqual(s['stables_4w'], 0.002 * 28, places=6)
        self.assertAlmostEqual(s['dex_4w'], 0.0, places=12)

    def test_floor_removes_small_chains(self):
        f = dict(self.fund, dex=flat_series(D0 - 400, 400, 1e3))
        self.assertIsNone(self.sig(f)['dex_4w'])

    def test_week_return_uses_sunday_closes_and_realises_a_delisting(self):
        c = {D0 - 1: 100.0, D0 + 2: 90.0, D0 + 6: 110.0}
        vs = [('binance:XUSDT', 1.0, True, c, {})]
        r = FF.week_return(vs, D0)
        self.assertAlmostEqual(r[0], 0.10)
        c2 = {D0 - 1: 100.0, D0 + 2: 1.0}           # last print mid-week (the LUNA case)
        r2 = FF.week_return([('binance:LUNAUSDT', 1.0, True, c2, {})], D0)
        self.assertAlmostEqual(r2[0], -0.99)
        self.assertIsNone(FF.week_return([('binance:XUSDT', 1.0, True, {D0: 5.0, D0 + 6: 6.0}, {})], D0))

    def test_mondays(self):
        w = FF.mondays('2024-01-03', '2024-01-31')
        self.assertEqual([FF.dstr(x) for x in w], ['2024-01-08', '2024-01-15', '2024-01-22', '2024-01-29'])


def make_panel(n_tok=12, n_weeks=60, seed=3, funding=0.0):
    rng = random.Random(seed)
    weeks = [D0 + 7 * i for i in range(n_weeks)]
    toks = {}
    for j in range(n_tok):
        rows = {R: {'ret': rng.gauss(0, 0.05), 'funding': funding, 'beta': 1.0, 'liquid': True} for R in weeks}
        toks[('chains', 't%02d' % j)] = {'rows': rows}
    btc = {R: {'ret': rng.gauss(0, 0.03), 'funding': 0.0} for R in weeks}
    return {'weeks': weeks, 'tokens': toks, 'btc': btc}


class Portfolio(unittest.TestCase):
    def test_terciles_equal_weight_dollar_neutral(self):
        sc = {('chains', 't%02d' % i): float(i) for i in range(10)}
        w = FF.ls_weights(sc)
        self.assertEqual(len(w), 6)
        self.assertAlmostEqual(sum(w.values()), 0.0)
        self.assertEqual({k[1] for k, x in w.items() if x > 0}, {'t07', 't08', 't09'})
        self.assertEqual({k[1] for k, x in w.items() if x < 0}, {'t00', 't01', 't02'})
        self.assertAlmostEqual(w[('chains', 't09')], 1 / 3)
        self.assertEqual(FF.ls_weights(dict(list(sc.items())[:8])), {})

    def test_pnl_signs(self):
        P = make_panel()
        good = {R: {k: tk['rows'][R]['ret'] for k, tk in P['tokens'].items()} for R in P['weeks']}   # foresight
        bad = {R: {k: -v for k, v in sc.items()} for R, sc in good.items()}
        g = FF.summarize(FF.run_book(P, good, cost_bps=0, cost_btc_bps=0))
        b = FF.summarize(FF.run_book(P, bad, cost_bps=0, cost_btc_bps=0))
        self.assertGreater(g['gross_ann'], 0)
        self.assertLess(b['gross_ann'], 0)
        self.assertAlmostEqual(g['gross_ann'], -b['gross_ann'])

    def test_longs_pay_positive_funding_shorts_receive(self):
        P = make_panel(funding=0.001)
        sc = {R: {k: float(i) for i, k in enumerate(sorted(P['tokens']))} for R in P['weeks']}
        rows = FF.run_book(P, sc, cost_bps=0, cost_btc_bps=0)
        # equal funding on both legs nets to zero in a dollar-neutral book
        self.assertTrue(all(abs(r['funding']) < 1e-12 for r in rows if r['active']))
        for k in list(P['tokens'])[-4:]:            # the top names (the longs) pay more
            for R in P['weeks']:
                P['tokens'][k]['rows'][R]['funding'] = 0.002
        rows = FF.run_book(P, sc, cost_bps=0, cost_btc_bps=0)
        self.assertTrue(all(r['funding'] < 0 for r in rows if r['active']))

    def test_turnover_counts_drift_and_costs_are_charged(self):
        P = make_panel()
        sc = {R: {k: float(i) for i, k in enumerate(sorted(P['tokens']))} for R in P['weeks']}
        rows = FF.run_book(P, sc, cost_bps=10, cost_btc_bps=0)
        self.assertAlmostEqual(rows[0]['turnover'], 2.0)          # opening $1 long and $1 short
        R0, R1 = P['weeks'][0], P['weeks'][1]
        w = FF.ls_weights(sc[R0])
        expect = sum(abs(x * P['tokens'][k]['rows'][R0]['ret']) for k, x in w.items())
        self.assertAlmostEqual(rows[1]['turnover'], expect)      # same names: only the drift is traded back
        self.assertAlmostEqual(rows[1]['cost'], 10 / 1e4 * expect)
        self.assertAlmostEqual(rows[1]['net'], rows[1]['gross'] + rows[1]['funding'] - rows[1]['cost'])

    def test_beta_hedge_offsets_the_legs_beta(self):
        P = make_panel()
        keys = sorted(P['tokens'])
        for i, k in enumerate(keys):
            for R in P['weeks']:
                P['tokens'][k]['rows'][R]['beta'] = 2.0 if i >= 8 else 0.5
        sc = {R: {k: float(i) for i, k in enumerate(keys)} for R in P['weeks']}
        rows = FF.run_book(P, sc, hedge='beta', cost_bps=0, cost_btc_bps=0)
        self.assertAlmostEqual(rows[0]['hedge'], -(2.0 - 0.5))   # long beta 2, short beta 0.5: sell 1.5 BTC

    def test_shuffled_signal_earns_about_nothing_gross(self):
        P = make_panel(n_tok=15, n_weeks=300, seed=9)
        good = {R: {k: tk['rows'][R]['ret'] for k, tk in P['tokens'].items()} for R in P['weeks']}
        pl = FF.placebo(P, good, 'dollar', cut=P['weeks'][150], reps=20)
        real = FF.summarize(FF.run_book(P, good))['ann_return']
        self.assertGreater(real, pl['full_p95'])
        self.assertLess(abs(pl['gross_mean']), 0.25 * FF.summarize(FF.run_book(P, good))['gross_ann'])

    def test_exclude_drops_a_token(self):
        P = make_panel()
        sc = {R: {k: float(i) for i, k in enumerate(sorted(P['tokens']))} for R in P['weeks']}
        top = sorted(P['tokens'])[-1]
        rows = FF.run_book(P, sc, exclude={top})
        self.assertTrue(all(top[1] not in r['long'] for r in rows if r['active']))


class Replay(unittest.TestCase):
    def test_surge_replay_matches_the_framework_at_every_day(self):
        import chain_activity as CA
        rng = random.Random(5)
        series = {D0 + i: 1e6 * (1 + 0.3 * rng.random()) * (6 if i in (120, 171) else 1) for i in range(200)}
        for recent, weekday in ((1, True), (7, False)):
            rep = {x['day']: x for x in FF.surge_replay(series, recent, weekday)}
            for end in (60, 120, 121, 171, 199):
                sub = {FF.dstr(d): v for d, v in series.items() if d <= D0 + end}
                ref = CA.surge_stats(sub, recent=recent, weekday=weekday)
                got = rep[D0 + end]
                self.assertAlmostEqual(got['ratio'], ref['ratio'], places=9)
                self.assertAlmostEqual(got['p_up'], ref['p_up'], places=12)

    def test_surge_fires_on_the_spike_only(self):
        series = {D0 + i: 1e6 for i in range(200)}
        series[D0 + 150] = 5e6
        rep = {x['day']: x for x in FF.surge_replay(series, 1, True)}
        self.assertGreaterEqual(rep[D0 + 150]['ratio'], 2.0)
        self.assertLessEqual(rep[D0 + 150]['p_up'], 0.05)
        self.assertLess(rep[D0 + 149]['ratio'], 2.0)

    def test_stable_inflow_replay(self):
        s = {D0 + i: 100e6 for i in range(40)}
        for i in range(35, 40):
            s[D0 + i] = 130e6
        ev = FF.stable_replay(s)
        self.assertEqual(ev[0]['day'], D0 + 35)
        self.assertEqual(ev[0]['kind'], '7d')
        self.assertAlmostEqual(ev[0]['change'], 30e6)

    def test_event_trade_enters_one_full_day_after_the_data_day(self):
        D = D0 + 50
        closes = {d: 100.0 for d in range(D0, D0 + 120)}
        closes[D + 1] = 100.0          # entry: close of D+1
        closes[D] = 50.0               # the data day's own move is not captured
        closes[D + 8] = 120.0          # exit: close of D+1+7
        vol = {d: 1e7 for d in range(D0, D0 + 120)}
        key = ('chains', 'x')
        P = {'tokens': {key: {'venues': ['binance:XUSDT']}}}
        cache = {'vs': {key: [('binance:XUSDT', 1.0, True, closes, vol)]}, 'fund': {'binance:XUSDT': FF.Funding([])},
                 'btc': {d: 1.0 for d in range(D0, D0 + 120)}, 'btc_f': FF.Funding([])}
        x = FF.event_trade(P, key, D, 7, cost_bps=0, cost_btc_bps=0, raw=None, cache=cache)
        self.assertAlmostEqual(x['ret'], 0.20)
        self.assertAlmostEqual(x['pnl'], 0.20)


class Plumbing(unittest.TestCase):
    def test_funding_window_is_half_open(self):
        f = FF.Funding([[100, 0.1], [200, 0.2], [300, 0.3]])
        self.assertAlmostEqual(f.window(100, 300), 0.5)
        self.assertAlmostEqual(f.window(0, 100), 0.1)
        self.assertIsNone(f.window(0, 50))

    def test_book_cost_walks_levels(self):
        mid = 100.0
        asks = [[100.1, 10], [100.5, 100]]           # $1,001 at 10bp, then 50bp
        self.assertAlmostEqual(FF.book_cost_bps(asks, 1001.0, mid), 10.0, places=6)
        self.assertGreater(FF.book_cost_bps(asks, 5000.0, mid), 10.0)
        self.assertIsNone(FF.book_cost_bps(asks, 1e9, mid))

    def test_pct_rank_ties(self):
        r = FF.pct_rank({'a': 1, 'b': 1, 'c': 3})
        self.assertAlmostEqual(r['a'], 1.5 / 3)
        self.assertAlmostEqual(r['c'], 1.0)

    def test_venue_candidates_prefixes(self):
        v = FF.venue_candidates('PEPE', {'1000PEPEUSDT'}, {'kPEPE'})
        self.assertIn(('binance', '1000PEPEUSDT', 1000.0), v)
        self.assertIn(('hl', 'kPEPE', 1000.0), v)
        self.assertEqual(FF.venue_candidates('dYdX', {'DYDXUSDT'}, set()), [('binance', 'DYDXUSDT', 1.0)])
        self.assertEqual(FF.symbol_scale('1000LUNCUSDT'), 1000.0)
        self.assertEqual(FF.symbol_scale('LUNAUSDT'), 1.0)


if __name__ == '__main__':
    unittest.main()


class StaleBars(unittest.TestCase):
    def test_zero_volume_bars_after_a_delisting_do_not_shadow_the_live_venue(self):
        import gzip
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            (raw / 'klines').mkdir()
            (raw / 'hl_candles').mkdir()
            ms = lambda d: d * 86400 * 1000  # noqa: E731
            # Binance: traded until D0+10, then flat zero-volume bars (what TONUSDT, FTMUSDT, MKRUSDT do)
            bn = [[ms(D0 - 40 + i), '1', '1', '1', '2.0', '0', 0, '9000000'] for i in range(50)]
            bn += [[ms(D0 + 10 + i), '2', '2', '2', '2.0', '0', 0, '0'] for i in range(1, 30)]
            with gzip.open(raw / 'klines' / 'TONUSDT.json.gz', 'wt') as f:
                json.dump(bn, f)
            hl = [{'t': ms(D0 - 40 + i), 'c': str(1.0 + 0.01 * i), 'v': '9000000'} for i in range(70)]
            with gzip.open(raw / 'hl_candles' / 'GRAM.json.gz', 'wt') as f:
                json.dump(hl, f)
            vs = FF.venue_series(raw, [{'venue': 'binance', 'symbol': 'TONUSDT', 'scale': 1.0},
                                       {'venue': 'hl', 'symbol': 'GRAM', 'scale': 1.0}])
            self.assertEqual(max(vs[0][3]), D0 + 9)                 # the stale tail is gone
            w = FF.week_return(vs, D0 + 21)                          # a week after the delisting
            self.assertEqual(w[1], 'hl:GRAM')
            dr = FF.daily_returns(vs)
            self.assertGreater(dr[D0 + 20], 0)                        # from the live venue, not a flat zero


class IdentityDay(unittest.TestCase):
    def test_check_day_ignores_untraded_bars(self):
        # Hyperliquid's pre-listing bars and Binance's post-delisting bars carry a price but no volume
        closes = {'2025-01-%02d' % i: (5.0, 0.0) for i in range(1, 29)}
        closes.update({'2025-02-%02d' % i: (1.0, 1e6) for i in range(1, 4)})
        self.assertEqual(FF.check_day(closes), '2025-02-02')
        self.assertIsNone(FF.check_day({'2025-01-01': (5.0, 0.0)}))
