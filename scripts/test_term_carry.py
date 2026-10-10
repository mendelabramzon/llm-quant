#!/usr/bin/env python3
"""Tests for term_carry.py on synthetic data: calendars, settlement days, annualisation, capital accounting, the
hold-to-expiry and carry simulators (signs, costs, rolls, hysteresis, venue switches, rebalancing), Boros scoring,
realised volatility, NAV interpolation, and the two timing bugs this study found (Deribit's 08:00 daily bars, and the
expiry a continuous quarterly series refers to on its roll day).

    python3 -m unittest scripts/test_term_carry.py
"""
import datetime as dt
import gzip
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import term_carry as T  # noqa: E402

UTC = dt.timezone.utc


def ms(s, h=0):
    return int(dt.datetime.strptime(s, '%Y-%m-%d').replace(hour=h, tzinfo=UTC).timestamp() * 1000)


def day(s):
    return ms(s) // T.DAY_MS


class Calendars(unittest.TestCase):
    def test_last_friday(self):
        self.assertEqual(T.last_friday(2025, 9), dt.date(2025, 9, 26))
        self.assertEqual(T.last_friday(2026, 12), dt.date(2026, 12, 25))
        self.assertEqual(T.last_friday(2024, 3), dt.date(2024, 3, 29))

    def test_quarterly_expiries_at_0800(self):
        e = T.quarterly_expiries(2025, 2025)
        self.assertEqual([T.ymd(x) for x in e], ['2025-03-28', '2025-06-27', '2025-09-26', '2025-12-26'])
        self.assertTrue(all((x % T.DAY_MS) == 8 * T.HOUR_MS for x in e))

    def test_nth_expiry_after_is_strict(self):
        e = T.quarterly_expiries(2025, 2026)
        sep = ms('2025-09-26', 8)
        self.assertEqual(T.nth_expiry_after(e, sep - 1), sep)               # one ms before: still the September
        self.assertEqual(T.ymd(T.nth_expiry_after(e, sep)), '2025-12-26')   # at the expiry: the next one
        self.assertEqual(T.ymd(T.nth_expiry_after(e, sep, 1)), '2026-03-27')

    def test_deribit_names(self):
        self.assertEqual(T.deribit_name('BTC', ms('2024-12-27', 8)), 'BTC-27DEC24')
        self.assertEqual(T.deribit_name('ETH', ms('2025-03-28', 8)), 'ETH-28MAR25')

    def test_cme_monthly(self):
        e = T.monthly_expiries(2026, 2026)
        self.assertEqual(len(e), 12)
        self.assertEqual(T.ymd(e[9]), '2026-10-30')


class Settlements(unittest.TestCase):
    def test_day_of_window(self):
        d = day('2025-10-01')
        self.assertEqual(T.day_of(ms('2025-10-01', 8) + 3), d)
        self.assertEqual(T.day_of(ms('2025-10-02') + 5), d)        # 00:00 next day closes day d
        self.assertEqual(T.day_of(ms('2025-10-01') + 7), d - 1)     # 00:00 of day d belongs to d-1

    def test_daily_sums_dedupes_by_hour(self):
        t = ms('2025-10-01', 8)
        s, n = T.daily_sums([(t, 1e-4), (t + 40, 2e-4), (ms('2025-10-01', 16), 3e-4)])
        d = day('2025-10-01')
        self.assertAlmostEqual(s[d], 5e-4)     # the duplicate settlement at 08:00 counted once (last wins)
        self.assertEqual(n[d], 2)

    def test_trailing_apr(self):
        f = {d: 0.0003 for d in range(100, 110)}
        self.assertAlmostEqual(T.trailing_apr(f, 110, 7), 0.0003 * 365)
        self.assertIsNone(T.trailing_apr(f, 103, 7))               # only three days of history


class Annualisation(unittest.TestCase):
    def test_locked_excess_capital_models(self):
        g, tau, b = 0.01, 36.5, 0.038                      # 1% over 36.5 days = 10% a year on notional
        self.assertAlmostEqual(T.locked_excess(g, tau, 'portfolio', b), 0.10 - b)
        self.assertAlmostEqual(T.locked_excess(g, tau, 'cash3x', b), 0.10 * 0.75 - b)
        self.assertAlmostEqual(T.locked_excess(g, tau, 'cme_tbill', b), (0.10 - b) / 1.4)
        self.assertAlmostEqual(T.locked_excess(g, tau, 'cme_idle', b), 0.10 / 1.4 - b)
        self.assertLess(T.locked_excess(-0.001, tau, 'portfolio', b), 0)

    def test_nav_daily_returns(self):
        r = 0.05
        pts = [(d * T.DAY_S, math.exp(r * d / 365.0)) for d in range(0, 40, 3)]
        out = T.nav_daily_returns(pts, 1, 30)
        self.assertEqual(len(out), 29)
        for v in out.values():
            self.assertAlmostEqual(v * 365, r, places=9)


def bn_rows(days, basis_by_day, S=100.0, exp_ms=None, tau=None):
    """rows in bn_basis_rows' shape with a front contract only."""
    out = {}
    for d in days:
        t_close = (d + 1) * T.DAY_MS
        e = exp_ms(d) if callable(exp_ms) else exp_ms
        out[d] = {'S': S, 'front': (S * (1 + basis_by_day(d)), e, (e - t_close) / T.DAY_MS, 1.0)}
    return out


class BasisSimulator(unittest.TestCase):
    def setUp(self):
        self.b = lambda d: T.SSR

    def test_hold_to_expiry_accrues_net_evenly(self):
        d0 = day('2025-01-01')
        exp = ms('2025-03-28', 8)
        rows = bn_rows(range(d0, d0 + 40), lambda d: 0.03, exp_ms=exp)
        days, ser, trades = T.simulate_basis(rows, 'binance', 'portfolio', self.b, 'front', 0.0)
        self.assertEqual(len(trades), 1)
        c_in, c_out, _ = T.basis_entry_costs('binance')
        tr = trades[0]
        self.assertAlmostEqual(tr['net'], 0.03 - c_in - c_out)
        # the day after entry onward: accrual minus the benchmark; the entry day itself earns the benchmark
        n = exp // T.DAY_MS - d0
        self.assertAlmostEqual(ser[0], 0.0)
        self.assertAlmostEqual(ser[1], tr['net'] / n - T.SSR / 365.0)
        self.assertAlmostEqual(sum(ser) + T.SSR / 365.0 * (len(ser) - 1), tr['net'] * (len(ser) - 1) / n, places=12)

    def test_threshold_blocks_entry_and_idle_earns_benchmark(self):
        d0 = day('2025-01-01')
        rows = bn_rows(range(d0, d0 + 30), lambda d: 0.002, exp_ms=ms('2025-03-28', 8))
        days, ser, trades = T.simulate_basis(rows, 'binance', 'portfolio', self.b, 'front', 0.0)
        self.assertEqual(trades, [])
        self.assertTrue(all(v == 0.0 for v in ser))

    def test_roll_saves_both_spot_fees(self):
        d0 = day('2025-03-01')
        e1, e2 = ms('2025-03-28', 8), ms('2025-06-27', 8)
        rows = bn_rows(range(d0, day('2025-04-20')), lambda d: 0.03,
                       exp_ms=lambda d: e1 if (d + 1) * T.DAY_MS <= e1 else e2)
        days, ser, trades = T.simulate_basis(rows, 'binance', 'portfolio', self.b, 'front', 0.0)
        self.assertEqual(len(trades), 2)
        self.assertTrue(trades[1]['rolled_from_previous'])
        c_in, c_out, c_spot = T.basis_entry_costs('binance')
        self.assertAlmostEqual(trades[1]['net'], 0.03 - (c_in - c_spot) - c_out)
        roll_day = e1 // T.DAY_MS
        # the previous trade's spot sale is refunded on the roll day (it was never made)
        i = days.index(roll_day)
        n1 = e1 // T.DAY_MS - trades[0]['entry_day']
        self.assertAlmostEqual(ser[i], trades[0]['net'] / n1 + c_spot - T.SSR / 365.0, places=12)

    def test_capital_scaling(self):
        d0 = day('2025-01-01')
        rows = bn_rows(range(d0, d0 + 10), lambda d: 0.03, exp_ms=ms('2025-03-28', 8))
        _, s1, _ = T.simulate_basis(rows, 'binance', 'portfolio', self.b, 'front', 0.0)
        _, s3, _ = T.simulate_basis(rows, 'binance', 'cash3x', self.b, 'front', 0.0)
        a1 = s1[2] + T.SSR / 365.0
        a3 = s3[2] + T.SSR / 365.0
        self.assertAlmostEqual(a3, a1 * 0.75)


class BasisRowsTiming(unittest.TestCase):
    """The two timing pins: Deribit's 1D bars close at 08:00 UTC, and a continuous quarterly series on the roll
    day already refers to the next contract."""

    def test_deribit_bar_keyed_to_its_0800_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            (raw / 'deribit').mkdir()
            exp = ms('2024-03-29', 8)
            tick = ms('2024-03-12', 8)                       # bar opening 2024-03-12 08:00, closing 03-13 08:00
            with gzip.open(raw / 'deribit' / 'fut_BTC-29MAR24_1d.json.gz', 'wt') as f:
                json.dump({'ticks': [tick], 'close': [74092.5], 'volume': [10.0], 'expiry': exp}, f)
            with gzip.open(raw / 'deribit' / 'delivery_btc_usd.json.gz', 'wt') as f:
                json.dump([{'date': '2024-03-12', 'delivery_price': 71000.0},
                           {'date': '2024-03-13', 'delivery_price': 73500.0}], f)
            rows = T.deribit_basis_rows(raw, 'BTC')
            d = day('2024-03-13')
            self.assertIn(d, rows)
            self.assertNotIn(day('2024-03-12'), rows)
            self.assertEqual(rows[d]['S'], 73500.0)
            F, e, tau, _ = rows[d]['front']
            self.assertEqual(e, exp)
            self.assertAlmostEqual(tau, 16.0)

    def test_binance_roll_day_refers_to_next_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            (raw / 'binance').mkdir()
            d_roll = day('2025-09-26')
            k = [[d * T.DAY_MS, 0, 0, 0, 100.0 + i, 1, 0, 1000.0] for i, d in enumerate(range(d_roll - 2, d_roll + 2))]
            for ct in ('CURRENT_QUARTER', 'NEXT_QUARTER'):
                with gzip.open(raw / 'binance' / ('cont_BTCUSDT_%s_1d.json.gz' % ct), 'wt') as f:
                    json.dump(k, f)
            with gzip.open(raw / 'binance' / 'index_BTCUSDT_1d.json.gz', 'wt') as f:
                json.dump([[d * T.DAY_MS, 0, 0, 0, 100.0] for d in range(d_roll - 2, d_roll + 2)], f)
            rows = T.bn_basis_rows(raw, 'BTCUSDT')
            self.assertEqual(T.ymd(rows[d_roll - 1]['front'][1]), '2025-09-26')
            self.assertEqual(T.ymd(rows[d_roll]['front'][1]), '2025-12-26')      # closed at 23:59 after the 08:00 roll
            self.assertEqual(T.ymd(rows[d_roll]['next'][1]), '2026-03-27')


class CarrySimulator(unittest.TestCase):
    def setUp(self):
        self.bench = lambda d: T.SSR
        self.days = list(range(1000, 1100))

    def run_(self, f, rule, K=1.0, p=None, closes=None, highs=None, lev=None, sched=None, f2=None, extra=None):
        fb = {'a': f} if f2 is None else {'a': f, 'b': f2}
        pb = {'a': p or {}} if f2 is None else {'a': p or {}, 'b': {}}
        pc = {'a': 0.0005} if f2 is None else {'a': 0.0005, 'b': 0.0004}
        return T.simulate_carry(self.days, fb, pb, rule, 0.001, pc, K, self.bench, schedule=sched, extra=extra,
                                closes=closes, highs=highs, lev=lev)

    def test_always_on_constant_funding(self):
        f = {d: 0.0004 for d in range(990, 1100)}
        ex, inpos, st = self.run_(f, {'kind': 'always'})
        self.assertTrue(all(inpos))
        self.assertAlmostEqual(ex[0], 0.0004 - 0.0015 - T.SSR / 365)        # entry cost on the first day
        self.assertAlmostEqual(ex[50], 0.0004 - T.SSR / 365)
        self.assertAlmostEqual(ex[-1], 0.0004 - 0.0015 - T.SSR / 365)       # closed at the end of the sample
        self.assertEqual(st['entries'], 1)

    def test_capital_divides_carry_not_benchmark(self):
        f = {d: 0.0004 for d in range(990, 1100)}
        ex, _, _ = self.run_(f, {'kind': 'always'}, K=4.0 / 3.0)
        self.assertAlmostEqual(ex[50], 0.0004 * 0.75 - T.SSR / 365)

    def test_threshold_exits_on_negative_funding_with_hysteresis(self):
        f = {d: (0.0004 if d < 1040 else -0.0002) for d in range(990, 1100)}
        rule = {'kind': 'thr', 'k': 7, 'x': 0.0, 'h': 0.02}
        ex, inpos, st = self.run_(f, rule)
        self.assertTrue(inpos[0])
        self.assertFalse(inpos[-1])
        self.assertEqual(st['exits'], 1)
        exit_i = inpos.index(False)
        # exits only once the trailing week has fallen below SSR - 2pp
        sig = T.trailing_apr(f, self.days[exit_i], 7)
        self.assertLess(sig, T.SSR - 0.02)
        self.assertGreaterEqual(T.trailing_apr(f, self.days[exit_i - 1], 7), T.SSR - 0.02)
        self.assertAlmostEqual(ex[exit_i], -0.0015)                         # exit day: benchmark minus the exit cost
        self.assertAlmostEqual(ex[exit_i + 5], 0.0)

    def test_basis_mark_telescopes(self):
        f = {d: 0.0 for d in range(990, 1100)}
        p = {d: 0.001 * ((d % 3) - 1) for d in range(990, 1100)}
        ex, _, st = self.run_(f, {'kind': 'always'}, p=p)
        self.assertAlmostEqual(st['basis'], p[999] - p[1099])

    def test_venue_switch_costs_two_perp_sides(self):
        f = {d: 0.0004 for d in range(990, 1100)}
        sched = {d: ('a' if d < 1050 else 'b') for d in self.days}
        ex, _, st = self.run_(f, {'kind': 'always'}, sched=sched, f2=f)
        self.assertEqual(st['switches'], 1)
        self.assertAlmostEqual(ex[50], 0.0004 - 0.0009 - T.SSR / 365)

    def test_rebalance_and_liquidation_diagnostic(self):
        f = {d: 0.0 for d in range(990, 1100)}
        closes = {d: 100.0 * (1.25 if d >= 1030 else 1.0) for d in range(990, 1100)}
        highs = {d: closes[d] * (1.4 if d == 1060 else 1.0) for d in range(990, 1100)}
        ex, _, st = self.run_(f, {'kind': 'always'}, K=4.0 / 3.0, closes=closes, highs=highs, lev=3.0)
        self.assertEqual(st['rebalances'], 1)
        self.assertEqual(st['liq_near'], 1)
        self.assertAlmostEqual(ex[30], -(0.25 * 0.0015) / (4.0 / 3.0) - T.SSR / 365)

    def test_portfolio_margin_borrow_cost(self):
        f = {d: 0.0 for d in range(990, 1100)}
        closes = {d: 100.0 * (1.10 if d >= 1030 else 1.0) for d in range(990, 1100)}
        ex, _, st = T.simulate_carry(self.days, {'a': f}, {'a': {}}, {'kind': 'always'}, 0.001, {'a': 0.0005}, 1.0,
                                     self.bench, closes=closes, theta=0.25, borrow_apr=0.055, borrow_base=0.10)
        self.assertEqual(st['rebalances'], 0)                        # a 10% rise stays inside the 25% band
        self.assertAlmostEqual(ex[10], -0.10 * 0.055 / 365 - T.SSR / 365)
        self.assertAlmostEqual(ex[50], -(0.10 + 0.10) * 0.055 / 365 - T.SSR / 365)

    def test_reference_price_set_when_prices_start_after_entry(self):
        f = {d: 0.0 for d in range(990, 1100)}
        closes = {d: 100.0 * (1.10 if d >= 1060 else 1.0) for d in range(1040, 1100)}   # no prices before 1040
        _, _, st = T.simulate_carry(self.days, {'a': f}, {'a': {}}, {'kind': 'always'}, 0.001, {'a': 0.0005}, 1.0,
                                    self.bench, closes=closes, theta=0.25, borrow_apr=0.055, borrow_base=0.10)
        n_priced = sum(1 for d in self.days if d in closes and (d - 1) in closes or d == 1041)
        self.assertGreater(st['borrow'], 0.0)                         # charged once prices exist
        self.assertAlmostEqual(st['borrow'], sum(
            (0.10 + max(0.0, closes[d] / 100.0 - 1.0)) * 0.055 / 365 for d in self.days if d >= 1041))

    def test_staking_extra_accrues_only_while_held(self):
        f = {d: (0.0004 if d < 1040 else -0.0004) for d in range(990, 1100)}
        extra = {d: 0.0001 for d in range(990, 1100)}
        rule = {'kind': 'thr', 'k': 7, 'x': 0.0, 'h': 0.02}
        _, inpos, st = self.run_(f, rule, extra=extra)
        self.assertAlmostEqual(st['extra'], 0.0001 * sum(1 for x in inpos if x))


class Boros(unittest.TestCase):
    def market(self, mr, u, maturity_day):
        return {'id': 1, 'symbol': 'X', 'maturity': maturity_day * T.DAY_S, 'asset': 'BTC', 'venue': 'binance',
                'token': 'BTC', 'stream': 'binance:BTCUSDT', 'taker_fee': 0.0005, 'settle_fee': 0.001, 'k_im': 0.645, 'floor': 0.08,
                't_thresh': 432000, 'u': u, 'mr': mr, 'data': {}, 'state': None}

    def test_receive_fixed_sign_and_annualisation(self):
        T0 = 2000
        u = {d: 0.08 for d in range(1900, T0 + 5)}
        m = self.market({1950: 0.10}, u, T0)
        tr = T.boros_trades([m], T.boros_streams([m]), now_day=2100, half_spread=0.0)
        self.assertEqual(len(tr), 1)
        t = tr[0]
        self.assertAlmostEqual(t['spread'], 0.02)
        self.assertAlmostEqual(t['rf_pnl'], (0.02 - 0.0015) * 50 / 365.0)
        self.assertAlmostEqual(t['pf_pnl'], (-0.02 - 0.0015) * 50 / 365.0)
        self.assertAlmostEqual(t['im_per_notional'], 0.10 * 0.645 * 50 / 365.0)

    def test_unmatured_and_uncovered_markets_are_not_scored(self):
        u = {d: 0.08 for d in range(1900, 1960)}
        m = self.market({1950: 0.10}, u, 2000)
        self.assertEqual(T.boros_trades([m], T.boros_streams([m]), now_day=1990), [])   # not yet matured
        self.assertEqual(T.boros_trades([m], T.boros_streams([m]), now_day=2100), [])   # floating not covered

    def test_rule_filters(self):
        tr = [{'trail7': 0.05, 'implied': 0.10}, {'trail7': 0.10, 'implied': 0.04}, {'trail7': None, 'implied': 0.1}]
        self.assertEqual(len(T.boros_rule(tr, 'rf', 0.02)), 1)
        self.assertEqual(len(T.boros_rule(tr, 'pf', 0.05)), 1)


class VolAndMisc(unittest.TestCase):
    def test_realized_vol_forward(self):
        t0 = ms('2025-01-01')
        r = 0.01
        closes = [(t0 + i * T.HOUR_MS, 100.0 * math.exp(r * (i % 2))) for i in range(30 * 24 + 1)]   # +r, -r, ...
        rv = T.realized_vol_forward(closes, t0, 30)
        self.assertAlmostEqual(rv, r * math.sqrt(8760.0), places=9)

    def test_selectors_pinned(self):
        self.assertEqual(T.SEL, {'convertToAssets': '0x07a2d13a', 'dsr': '0x487bf082', 'stEthPerToken': '0x035faf82'})

    def test_depth_usd(self):
        bids = [[100.0, 1.0], [99.95, 2.0], [99.0, 5.0]]
        self.assertAlmostEqual(T.depth_usd(bids, 100.0, 10), 100.0 + 199.9)
        self.assertAlmostEqual(T.depth_usd([[100.0, 500.0]], 100.0, 10, qty_in_usd=True), 500.0)

    def test_concentration(self):
        s = [0.0] * 70
        s[3] = 1.0
        self.assertAlmostEqual(T.concentration(s), 1.0)
        self.assertIsNone(T.concentration([-1.0] * 14))


if __name__ == '__main__':
    unittest.main()
