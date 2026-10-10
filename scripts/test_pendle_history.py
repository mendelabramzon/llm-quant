#!/usr/bin/env python3
"""pendle_history: every sign convention, payoff and the AMM quote, pinned on synthetic inputs with known answers."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pendle_history as P  # noqa: E402

DAY = P.DAY
T0 = 1_735_689_600  # 2025-01-01 00:00 UTC


def market(rows, expiry, **kw):
    m = {'key': '1-0xm', 'name': 'TEST', 'cls': 'stable', 'points': False, 'protocol': 'X', 'expiry': expiry,
         'fee_rate': 0.0, 'scalar_root': 20.0, 'und_key': '1-0xund', 'und_symbol': 'sTEST', 'acct_symbol': 'USDC',
         'rows': rows}
    m.update(kw)
    return m


def flat_rows(start, n, **vals):
    base = {'implied': 0.08, 'und': 0.05, 'und_int': 0.05, 'und_rew': 0.0, 'pt': 0.97, 'sy': 1.0, 'yt': 0.03,
            'tvl': 5e6, 'total_tvl': 5e6, 'vol': 0.0, 'total_pt': 2e6, 'total_sy': 3e6}
    base.update(vals)
    return [dict(base, t=start + k * DAY) for k in range(n)]


class Payoffs(unittest.TestCase):
    def test_pt_fixed_return_is_the_implied_rate_compounded(self):
        self.assertAlmostEqual(P.pt_fixed_return(0.10, 365), 0.10)
        self.assertAlmostEqual(P.pt_fixed_return(0.10, 182.5), math.sqrt(1.1) - 1)
        self.assertIsNone(P.pt_fixed_return(0.10, 0))
        self.assertIsNone(P.pt_fixed_return(None, 30))

    def test_compound_daily_matches_an_annual_rate(self):
        self.assertAlmostEqual(P.compound_daily([0.10] * 365), 0.10, places=9)
        self.assertAlmostEqual(P.compound_daily([]), 0.0)

    def test_annualise_is_simple(self):
        self.assertAlmostEqual(P.annualise(0.01, 36.5), 0.10)
        self.assertIsNone(P.annualise(None, 10))

    def test_yt_earns_the_implied_rate_on_its_cost_when_floating_equals_implied(self):
        # YT costs 1 - (1+i)^-t and collects (1+i)^t - 1: the ratio is (1+i)^t, the implied rate on the cost.
        i, days = 0.08, 120
        flt = (1 + i) ** (days / 365) - 1
        self.assertAlmostEqual(P.yt_interest_return(flt, i, days, yield_fee=0.0), flt, places=12)
        # The yield fee is a haircut on the interest, so it costs 5% of the payoff, not 5 points of return.
        r = P.yt_interest_return(flt, i, days, yield_fee=0.05)
        self.assertAlmostEqual(1 + r, 0.95 * (1 + flt), places=12)

    def test_yt_loses_everything_when_floating_stops(self):
        self.assertAlmostEqual(P.yt_interest_return(0.0, 0.08, 90), -1.0)


class AMM(unittest.TestCase):
    def test_tiny_buy_pays_only_the_fee(self):
        imp, days, fee = 0.10, 180, 0.002
        after, pt = P.pt_buy_quote(imp, days, 1e7, 1e7, 20.0, fee, 1.0)
        self.assertAlmostEqual(after, (1 + imp) / (1 + fee) - 1, places=6)

    def test_no_fee_tiny_buy_is_the_quoted_rate(self):
        after, _ = P.pt_buy_quote(0.10, 180, 1e7, 1e7, 20.0, 0.0, 1e-3)
        self.assertAlmostEqual(after, 0.10, places=7)

    def test_impact_lowers_the_rate_monotonically(self):
        rates = [P.pt_buy_quote(0.10, 180, 1e6, 1e6, 20.0, 0.0, s)[0] for s in (1e3, 1e4, 1e5, 3e5)]
        self.assertTrue(all(a > b for a, b in zip(rates, rates[1:])), rates)

    def test_quote_satisfies_the_curve(self):
        imp, days, tp, ta, sr, s = 0.12, 90, 4e6, 6e6, 25.0, 5e5
        after, dpt = P.pt_buy_quote(imp, days, tp, ta, sr, 0.0, s)
        t = days / 365
        e0 = (1 + imp) ** t
        n = tp + ta
        e = e0 + (P.logit((tp - dpt) / n) - P.logit(tp / n)) / (sr / t)
        self.assertAlmostEqual(dpt, s * e, places=6)          # PT bought = cash x post-trade exchange rate
        self.assertAlmostEqual(after, e ** (1 / t) - 1, places=9)

    def test_capacity_is_interior_on_a_shallow_pool_and_the_largest_size_on_a_deep_one(self):
        days = 120.0
        imp = 0.10
        pt_price = (1 + imp) ** (-days / 365)
        def row(total):
            return {'t': T0, 'implied': imp, 'pt': pt_price, 'sy': 1.0, 'total_pt': total, 'total_sy': total}
        m = market([], T0 + int(days) * DAY, fee_rate=0.0, scalar_root=20.0)
        _, best_deep = P.capacity_curve(m, row(1e9), 0.04)
        self.assertEqual(best_deep['size_usd'], P.SIZES[-1])
        curve, best_shallow = P.capacity_curve(m, row(2e6), 0.04)
        self.assertLess(best_shallow['size_usd'], P.SIZES[-1])
        edges = [c['edge'] for c in curve if c['edge'] is not None]
        self.assertTrue(all(a >= b for a, b in zip(edges, edges[1:])))   # bigger buys get a worse rate

    def test_size_the_pool_cannot_fill(self):
        self.assertEqual(P.pt_buy_quote(0.10, 180, 1e5, 1e5, 20.0, 0.0, 1e6), (None, None))

    def test_last_day_sentinel_prices_nothing(self):
        self.assertIsNone(P.asset_usd_price({'pt': 0.9962, 'implied': -1.0}, 1.0))
        self.assertIsNone(P.asset_usd_price({'pt': 0.9962, 'implied': -0.99999}, 1.0))

    def test_pool_conversion_round_trips(self):
        days = 73.0
        row = {'implied': 0.10, 'pt': 1.0 / 1.10 ** (days / 365), 'sy': 1.05, 'total_pt': 100.0, 'total_sy': 200.0}
        self.assertAlmostEqual(P.asset_usd_price(row, days), 1.0)
        tp, ta = P.pool_in_asset(row, days)
        self.assertAlmostEqual(tp, 100.0)
        self.assertAlmostEqual(ta, 210.0)                     # 200 SY x 1.05 asset per SY


class Recovery(unittest.TestCase):
    def test_ratio_is_market_over_api_sy(self):
        prices = [{'t': T0 + k * DAY, 'p': 0.05} for k in range(10)]
        r, n = P.recovery_ratio(prices, T0 + 2 * DAY, 1.2659)
        self.assertAlmostEqual(r, 0.05 / 1.2659)
        self.assertEqual(n, 9)                                # [t-1d, t+7d] inclusive
        self.assertEqual(P.recovery_ratio([], T0, 1.0), (None, 0))

    def test_first_break(self):
        sy = [{'t': T0 + k * DAY, 'p': 1.0} for k in range(20)]
        px = [{'t': T0 + k * DAY, 'p': 1.0 if k < 12 else 0.3} for k in range(20)]
        self.assertEqual(P.first_break(px, sy, 0.9), T0 + 12 * DAY)
        self.assertIsNone(P.first_break(px, sy, 0.9, end=T0 + 5 * DAY))

    def test_market_recovery_statuses(self):
        exp = T0 + 60 * DAY
        rows = flat_rows(T0, 61, sy=1.25)
        healthy = [{'t': T0 + k * DAY, 'p': 1.25} for k in range(70)]
        crashed = [{'t': T0 + k * DAY, 'p': 1.25 if k < 30 else 0.06} for k in range(70)]
        offset = [{'t': T0 + k * DAY, 'p': 1.0} for k in range(70)]   # wrong token: off by 20% from day one
        m = market(rows, exp)
        self.assertEqual(P.market_recovery(m, {'1-0xund': {'prices': healthy}})['status'], 'ok')
        r = P.market_recovery(m, {'1-0xund': {'prices': crashed}})
        self.assertEqual(r['status'], 'default')
        self.assertAlmostEqual(r['ratio'], 0.06 / 1.25)
        self.assertEqual(r['break_day'], T0 + 30 * DAY)
        self.assertEqual(P.market_recovery(m, {'1-0xund': {'prices': offset}})['status'], 'unmapped')
        late_only = [{'t': T0 + k * DAY, 'p': 1.25} for k in range(55, 70)]  # no early anchor, healthy at maturity
        self.assertEqual(P.market_recovery(m, {'1-0xund': {'prices': late_only}})['status'], 'ok_unanchored')
        self.assertEqual(P.market_recovery(m, {})['status'], 'no_price')

    def test_a_rebasing_token_under_a_growing_wrapper_is_not_a_default(self):
        exp = T0 + 200 * DAY
        rows = flat_rows(T0, 200)
        for k, r in enumerate(rows):
            r['sy'] = 1.025 * (1.045 ** (k / 365 * 2))      # the wrapper's rate grows; the aToken stays at $1
        prices = [{'t': T0 + k * DAY, 'p': 1.0} for k in range(230)]
        r = P.market_recovery(market(rows, exp), {'1-0xund': {'prices': prices}})
        self.assertLess(r['ratio'], 0.98)
        self.assertEqual(r['status'], 'ok')
        self.assertAlmostEqual(r['token_drop'], 1.0)


class AccountingUnit(unittest.TestCase):
    def test_first_acct_break_reads_the_unit_price_from_each_row(self):
        exp = T0 + 100 * DAY
        rows = []
        for k in range(100):
            left = 100 - k
            unit = 1.0 if k < 40 else 0.90          # the accounting asset loses 10% on day 40
            rows.append({'t': T0 + k * DAY, 'implied': 0.08, 'pt': unit * 1.08 ** (-left / 365)})
        m = market(rows, exp)
        self.assertEqual(P.first_acct_break(m, T0, 1.0, 0.95), T0 + 40 * DAY)
        self.assertIsNone(P.first_acct_break(m, T0, 1.0, 0.85))

    def test_early_unit_price_tells_a_dollar_from_a_token(self):
        exp = T0 + 100 * DAY
        dollar = [{'t': T0 + k * DAY, 'implied': 0.1, 'pt': 1.10 ** (-(100 - k) / 365)} for k in range(40)]
        ena = [{'t': T0 + k * DAY, 'implied': 0.1, 'pt': 0.30 * 1.10 ** (-(100 - k) / 365)} for k in range(40)]
        self.assertAlmostEqual(P.early_unit_price(dollar, exp), 1.0)
        self.assertAlmostEqual(P.early_unit_price(ena, exp), 0.30)
        self.assertIsNone(P.early_unit_price(dollar, None))


class UnitMove(unittest.TestCase):
    def test_api_reading_when_the_yield_token_is_priced(self):
        # USDX-like: the ratio already carries the collapse, the market move of the same token must not be applied.
        self.assertEqual(P.unit_move('default', 1.0, 0.05), (1.0, 'api'))
        # USD0++-like: the API marked the unit at market, the ratio reads ~1.
        self.assertEqual(P.unit_move('ok', 0.93, 0.93), (0.93, 'api'))

    def test_market_reading_without_a_yield_token_price(self):
        self.assertEqual(P.unit_move('no_price', 1.0, 0.30), (0.30, 'market'))
        self.assertEqual(P.unit_move('unmapped', 0.999, 1.004), (1.0, 'market'))

    def test_noise_and_absence(self):
        self.assertEqual(P.unit_move('ok', 0.995, None), (1.0, 'api'))
        self.assertEqual(P.unit_move('no_price', None, None), (1.0, None))


class Blocked(unittest.TestCase):
    def test_pt_buyers_in_a_collapsed_market(self):
        exp = T0 + 100 * DAY
        txs = [{'action': 'BUY_PT', 'timestamp': '2025-01-11T00:00:00Z', 'value': 1000.0, 'impliedApy': 0.12},
               {'action': 'SELL_PT', 'timestamp': '2025-01-12T00:00:00Z', 'value': 500.0, 'impliedApy': 0.12},
               {'action': 'BUY_PT', 'timestamp': '2025-06-01T00:00:00Z', 'value': 9.0, 'impliedApy': 0.12}]  # after expiry
        prices = [{'t': T0 + k * DAY, 'p': 1.07 if k < 60 else 0.002} for k in range(130)]
        rows = P.blocked_trade_returns(txs, exp, prices, er_now=1.07, bench={T0: 0.04}, dollar=True)
        self.assertEqual(len(rows), 1)                         # sells and post-expiry rows are not PT purchases
        r = rows[0]
        self.assertAlmostEqual(r['days'], 90.0)
        self.assertAlmostEqual(r['recovery'], 0.002 / 1.07)
        self.assertAlmostEqual(r['realised'], (1 + r['fixed']) * r['recovery'] - 1)
        self.assertAlmostEqual(r['excess'], r['realised'] - (1.04 ** (90 / 365) - 1), places=12)

    def test_unit_is_the_token_when_the_rate_is_one(self):
        exp = T0 + 30 * DAY
        txs = [{'action': 'BUY_PT', 'timestamp': '2025-01-01T00:00:00Z', 'value': 100.0, 'impliedApy': 0.10}]
        prices = [{'t': T0 + k * DAY, 'p': 1.0 if k < 20 else 0.5} for k in range(60)]
        r = P.blocked_trade_returns(txs, exp, prices, er_now=1.0, bench={}, dollar=True)[0]
        self.assertAlmostEqual(r['recovery'], 0.5)
        self.assertIsNone(r['excess'])                         # no benchmark history: priced, not compared


class Series(unittest.TestCase):
    def test_floating_over_compounds_and_reports_coverage(self):
        rows = flat_rows(T0, 10, und_int=0.0365)
        del rows[4]
        m = market(rows, T0 + 10 * DAY)
        r, cov = P.floating_over(m, T0, T0 + 10 * DAY)
        self.assertAlmostEqual(r, (1.0365) ** (10 / 365) - 1, places=12)   # the gap is forward-filled
        self.assertAlmostEqual(cov, 0.9)

    def test_trailing_mean_needs_enough_days(self):
        m = market(flat_rows(T0, 10, und_int=0.04), T0 + 30 * DAY)
        self.assertAlmostEqual(P.trailing_mean(m, T0 + 9 * DAY), 0.04)
        self.assertIsNone(P.trailing_mean(m, T0 + 2 * DAY))

    def test_sky_benchmark_is_the_daily_median(self):
        a = market(flat_rows(T0, 3, und_int=0.04), T0 + 99 * DAY, und_symbol='sUSDS')
        b = market(flat_rows(T0, 3, und_int=0.06), T0 + 99 * DAY, und_symbol='sDAI')
        c = market(flat_rows(T0, 3, und_int=0.50), T0 + 99 * DAY, und_symbol='sUSDe')
        bench = P.sky_benchmark([a, b, c])
        self.assertAlmostEqual(bench[T0], 0.05)
        self.assertAlmostEqual(P.bench_over(bench, T0, T0 + 3 * DAY), 1.05 ** (3 / 365) - 1, places=12)
        self.assertIsNone(P.bench_over(bench, T0 - DAY, T0 + DAY))

    def test_asset_class(self):
        self.assertEqual(P.asset_class(['ethena', 'stables'], 'sUSDe'), 'ethena')
        self.assertEqual(P.asset_class(['stables', 'points'], 'USD0++'), 'stable')
        self.assertEqual(P.asset_class(['eth'], 'weETH'), 'eth')
        self.assertEqual(P.asset_class([], 'LP rsETH (Deprecated)'), 'eth')
        self.assertEqual(P.asset_class([], 'PENDLE-LPT'), 'other')


class Legs(unittest.TestCase):
    def trade(self, **kw):
        tr = {'fixed_net': 0.02, 'floating': 0.01, 'bench': 0.008, 'recovery': 1.0, 'yt': 0.5, 'days': 100,
              't0': T0, 'T': T0 + 100 * DAY, 'break_day': None}
        tr.update(kw)
        return tr

    def test_float_mode(self):
        x, j = P.trade_legs(self.trade(), 'float')
        self.assertAlmostEqual(x, 0.01)
        self.assertEqual(j, 0.0)
        x, _ = P.trade_legs(self.trade(recovery=0.1), 'float')    # a default hits both legs: only the gap is scaled
        self.assertAlmostEqual(x, 0.001)

    def test_bench_mode_books_the_default_as_a_jump(self):
        x, j = P.trade_legs(self.trade(), 'bench')
        self.assertAlmostEqual(x, 0.012)
        self.assertEqual(j, 0.0)
        x, j = P.trade_legs(self.trade(recovery=0.05), 'bench')
        self.assertAlmostEqual(j, 1.02 * (0.05 - 1))
        self.assertAlmostEqual(x, 0.012 + j)
        self.assertEqual(P.trade_legs(self.trade(bench=None), 'bench'), (None, None))

    def test_yt_mode(self):
        x, j = P.trade_legs(self.trade(), 'yt')
        self.assertAlmostEqual(x, 0.5 - 0.008)
        x, j = P.trade_legs(self.trade(recovery=0.0), 'yt')
        self.assertAlmostEqual(x, -1.0 - 0.008)

    def paths(self, n, imp, flt=0.0, bench=0.0, imp_entry=None, yt_imp=None):
        imp_entry = imp if imp_entry is None else imp_entry
        pt = [(1 + imp_entry) ** (-n / 365)] + [(1 + imp) ** (-(n - k) / 365) for k in range(1, n)] + [1.0]
        f = (1 + flt) ** (1 / 365) - 1
        b = (1 + bench) ** (1 / 365) - 1
        yt0 = 1 - (1 + (yt_imp if yt_imp is not None else imp)) ** (-n / 365)
        return {'n': n, 'pt': pt, 'flt': [f] * n, 'bench': [b] * n, 'yt0': yt0}

    def test_mark_to_market_sums_to_the_held_to_maturity_result(self):
        n, imp, flt = 40, 0.09, 0.05
        tr = self.trade(t0=T0, T=T0 + n * DAY, days=n, _paths=self.paths(n, imp, flt=flt, bench=0.04))
        xs = P.trade_daily(tr, 'float')
        self.assertEqual(len(xs), n)
        fixed = (1 + imp) ** (n / 365) - 1
        self.assertAlmostEqual(sum(xs), fixed - n * ((1 + flt) ** (1 / 365) - 1), places=12)
        xb = P.trade_daily(tr, 'bench')
        self.assertAlmostEqual(sum(xb), fixed - n * ((1.04) ** (1 / 365) - 1), places=12)

    def test_mark_to_market_moves_with_the_implied_rate(self):
        n = 30
        p = self.paths(n, 0.10)
        p['pt'][10] = (1 + 0.20) ** (-(n - 10) / 365)   # the implied jumps to 20% for one day: PT marks down, then back
        tr = self.trade(t0=T0, T=T0 + n * DAY, days=n, _paths=p)
        xs = P.trade_daily(tr, 'float')
        self.assertLess(xs[9], 0)
        self.assertGreater(xs[10], 0)

    def test_bench_default_jump_and_scaling(self):
        n, imp, rec = 20, 0.10, 0.5
        tr = self.trade(t0=T0, T=T0 + n * DAY, days=n, recovery=rec, break_day=T0 + 5 * DAY,
                        _paths=self.paths(n, imp, bench=0.0))
        xs = P.trade_daily(tr, 'bench')
        fixed = (1 + imp) ** (n / 365) - 1
        self.assertAlmostEqual(sum(xs), rec * (1 + fixed) - 1, places=12)
        self.assertLess(xs[5], -0.4)

    def test_yt_daily_sums_to_the_interest_payoff(self):
        n, imp, flt = 50, 0.08, 0.12
        tr = self.trade(t0=T0, T=T0 + n * DAY, days=n, yield_fee=0.05, _paths=self.paths(n, imp, flt=flt, bench=0.0))
        xs = P.trade_daily(tr, 'yt')
        y0 = 1 - (1 + imp) ** (-n / 365)
        interest = n * ((1 + flt) ** (1 / 365) - 1) * 0.95
        self.assertAlmostEqual(sum(xs), interest / y0 - 1, places=10)

    def test_portfolio_respects_the_cutoff(self):
        cutoff = T0 + 50 * DAY
        axis = list(range(T0, T0 + 120 * DAY, DAY))
        ins = self.trade(t0=T0, T=T0 + 10 * DAY, days=10, _paths=self.paths(10, 0.0365, flt=0.0))
        straddle = self.trade(t0=T0 + 40 * DAY, T=T0 + 70 * DAY, days=30, _paths=self.paths(30, 0.5))
        oos = self.trade(t0=T0 + 60 * DAY, T=T0 + 80 * DAY, days=20, _paths=self.paths(20, 0.0730, flt=0.0))
        s = P.portfolio_series([ins, straddle, oos], 'float', axis, cutoff, T0 + 119 * DAY)
        self.assertAlmostEqual(sum(s[:10]), 1.0365 ** (10 / 365) - 1, places=10)
        self.assertEqual(s[10], 0.0)
        self.assertEqual(s[45], 0.0)                  # the straddling trade never appears
        self.assertAlmostEqual(sum(s[60:80]), 1.0730 ** (20 / 365) - 1, places=10)
        self.assertEqual(s[80], 0.0)

    def test_portfolio_tvl_weighting(self):
        axis = list(range(T0, T0 + 30 * DAY, DAY))
        a = self.trade(t0=T0, T=T0 + 10 * DAY, days=10, tvl=3e6, _paths=self.paths(10, 0.10))
        b = self.trade(t0=T0, T=T0 + 10 * DAY, days=10, tvl=1e6, _paths=self.paths(10, 0.30))
        s = P.portfolio_series([a, b], 'float', axis, T0, T0 + 29 * DAY, weight='tvl')
        exp = 0.75 * (1.10 ** (10 / 365) - 1) + 0.25 * (1.30 ** (10 / 365) - 1)
        self.assertAlmostEqual(sum(s), exp, places=6)

    def test_portfolio_weights_trades_entered_the_same_day_equally(self):
        axis = list(range(T0, T0 + 30 * DAY, DAY))
        a = self.trade(t0=T0, T=T0 + 10 * DAY, days=10, _paths=self.paths(10, 0.10))
        b = self.trade(t0=T0, T=T0 + 10 * DAY, days=10, _paths=self.paths(10, 0.30))
        s = P.portfolio_series([a, b], 'float', axis, T0, T0 + 29 * DAY)
        exp = ((1.10 ** (10 / 365) - 1) + (1.30 ** (10 / 365) - 1)) / 2
        self.assertAlmostEqual(sum(s), exp, places=6)


if __name__ == '__main__':
    unittest.main()
