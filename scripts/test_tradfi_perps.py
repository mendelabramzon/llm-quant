#!/usr/bin/env python3
"""Tests for tradfi_perps.py on synthetic data: Binance's funding formula and its interval accounting, the US-hours
calendar, twin matching (units, splits, pre-IPO marks), and the signs and time alignment of every P&L the study
reports (the daily two-perp carry, the hourly always-on pair, the off-hours excursions)."""
import datetime as dt
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import funding_arb as FA  # noqa: E402
import tradfi_perps as T  # noqa: E402

H = T.HOUR_MS


def ms(s):
    return int(dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


class FormulaTest(unittest.TestCase):
    def test_dead_zone_without_interest(self):
        # Binance TradFi reports interestRate 0: inside +-0.05% the rate is exactly zero, beyond it P -/+ 0.05%
        self.assertEqual(T.bn_formula(0.0004, 0.0), 0.0)
        self.assertEqual(T.bn_formula(-0.0004, 0.0), 0.0)
        self.assertAlmostEqual(T.bn_formula(0.00087535, 0.0), 0.00037535)
        self.assertAlmostEqual(T.bn_formula(-0.0009, 0.0), -0.0004)

    def test_interest_leg_and_caps(self):
        # with the crypto interest leg (0.01% per 8 h, 0.005% per 4 h) a quiet premium pays the interest exactly
        self.assertAlmostEqual(T.bn_formula(0.0001, 0.0001), 0.0001)
        self.assertAlmostEqual(T.bn_formula(0.0001, 0.0001, h=4), 0.00005)
        self.assertAlmostEqual(T.bn_formula(0.03, 0.0, cap=0.02, floor=-0.02), 0.02)
        self.assertAlmostEqual(T.bn_formula(-0.03, 0.0, h=4, cap=0.005, floor=-0.005), -0.005)

    def test_four_hour_interval_scaling(self):
        # CLUSDT, a 4-hour symbol: a settlement whose window premium was -14.85bp printed -4.9bp; the scaled form gives
        # (P + c)/2 = -4.93bp, the unscaled one -9.85bp. Same premium, same annual rate whatever the interval.
        self.assertAlmostEqual(T.bn_formula(-0.001485, 0.0, h=4), -0.000493, places=6)
        self.assertAlmostEqual(T.bn_formula(0.0015, 0.0, h=4) * 2, T.bn_formula(0.0015, 0.0, h=8))

    def test_window_premium_linear_weights(self):
        T0 = ms('2026-06-01T08:00:00')
        prem = {T0 - 1 * H: (0.001,) * 4, T0: (0.003,) * 4}       # hours ending 07:00 and 08:00
        # h = 2: weights 1 and 3 -> (0.001 + 3 * 0.003) / 4
        self.assertAlmostEqual(T.window_premium(prem, T0, 2), 0.0025)
        self.assertAlmostEqual(T.window_premium(prem, T0, 2, weighting='flat'), 0.002)
        # under three quarters of the hours covered -> None
        self.assertIsNone(T.window_premium(prem, T0, 8))

    def test_hourly_accrual_preserves_total(self):
        t = ms('2026-06-01T00:00:00')
        sett = [(t, 0.0008), (t + 8 * H, 0.0), (t + 16 * H, 0.0004)]
        acc = T.bn_hourly_accrual(sett)
        self.assertAlmostEqual(sum(acc.values()), 0.0012)
        self.assertAlmostEqual(acc[t + 16 * H], 0.0004 / 8)
        self.assertAlmostEqual(acc[t + 9 * H], 0.0004 / 8)       # the 16:00 settlement pays for 09:00..16:00
        self.assertNotIn(t + 17 * H, acc)

    def test_interest_regime_detection(self):
        t = ms('2026-01-01T00:00:00')
        sett = [(t + i * 4 * H, 0.00005) for i in range(30)] + [(ms('2026-02-01T00:00:00') + i * 4 * H, 0.0)
                                                                 for i in range(30)]
        reg = T.interest_regimes(sett)
        self.assertTrue(reg['2026-01'])
        self.assertFalse(reg['2026-02'])

    def test_formula_check_reproduces_synthetic(self):
        t = ms('2026-06-01T00:00:00')
        prem, sett = {}, []
        for i in range(1, 25):
            p = 0.0012 if i <= 8 else 0.0002
            prem[t + i * H] = (p, p, p, p)
        sett = [(t + 8 * H, 0.0007), (t + 16 * H, 0.0), (t + 24 * H, 0.0)]
        res = T.formula_check({'sett': sett, 'prem': prem}, 0.02, -0.02)
        self.assertEqual(res['checked'], 3)
        # a 4-hour symbol: the same premium pays half per settlement, and the implied clamp is still 0.05%
        sett4 = [(t + 4 * H, 0.00035), (t + 8 * H, 0.00035), (t + 12 * H, 0.0)]
        res4 = T.formula_check({'sett': sett4, 'prem': prem}, 0.005, -0.005)
        self.assertEqual(res4['within_0.5bp'], 3)
        self.assertAlmostEqual(res4['clamp_estimates'][0], 0.0005)
        self.assertEqual(res['within_0.5bp'], 3)
        self.assertEqual(res['zero_class_agree'], 3)
        self.assertAlmostEqual(res['clamp_estimates'][0], 0.0005)


class CalendarTest(unittest.TestCase):
    def setUp(self):
        days = [dt.date(2026, 10, 8), dt.date(2026, 10, 9), dt.date(2026, 10, 12), dt.date(2026, 10, 13)]
        self.st = T.HourState(days)

    def test_session_offhours_weekend(self):
        # 2026-10-09 is a Friday in US daylight time: open 13:30 UTC, close 20:00 UTC
        self.assertEqual(self.st(ms('2026-10-09T15:00:00')), 'session')
        self.assertEqual(self.st(ms('2026-10-09T03:00:00')), 'offhours')      # Thursday night
        self.assertEqual(self.st(ms('2026-10-10T12:00:00')), 'weekend')       # Saturday
        self.assertEqual(self.st(ms('2026-10-09T21:00:00')), 'weekend')       # Friday after the close
        self.assertEqual(self.st(ms('2026-10-09T13:00:00')), 'offhours')      # the hour 12:00-13:00, before the open
        self.assertEqual(self.st(ms('2026-10-09T14:00:00')), 'session')       # 13:00-14:00, midpoint at the open

    def test_winter_open(self):
        days = [dt.date(2026, 11, 30), dt.date(2026, 12, 1), dt.date(2026, 12, 2)]
        st = T.HourState(days)
        self.assertEqual(st(ms('2026-12-01T14:00:00')), 'offhours')          # 09:30 ET is 14:30 UTC in winter
        self.assertEqual(st(ms('2026-12-01T15:00:00')), 'session')


class MatchTest(unittest.TestCase):
    def test_same_proxy_reject(self):
        daily = {d: 0.9995 for d in range(100, 130)}
        self.assertEqual(T.classify_ratio(daily, 'TSLA', 'TSLA')[0], 'same')
        idx = {d: 10.02 for d in range(100, 130)}
        kind, ur, _, _ = T.classify_ratio(idx, 'SP500', 'SPY')
        self.assertEqual(kind, 'proxy')
        self.assertAlmostEqual(ur, 10.02)
        # the same ratio on names that are not an index/ETF twin is a different asset
        self.assertEqual(T.classify_ratio(idx, 'FOO', 'FOO')[0], 'reject')

    def test_pre_ipo_marks_rejected(self):
        # io:ANTH vs ANTHROPICUSDT sat 2.6% apart: with a 3% tolerance it passed as a twin (bug fixed: 1%)
        daily = {d: 1.0263 for d in range(100, 150)}
        self.assertEqual(T.classify_ratio(daily, 'ANTH', 'ANTHROPIC')[0], 'reject')

    def test_split_break_starts_after(self):
        daily = {d: (0.5 if d < 120 else 1.0) for d in range(100, 140)}
        kind, ur, start, info = T.classify_ratio(daily, 'X', 'X')
        self.assertEqual(kind, 'same')
        self.assertEqual(start, 120)
        self.assertEqual(info['breaks'], 20)

    def test_ratio_profile_uses_common_hours(self):
        hl = {d * T.DAY_MS + h * H: 100.0 for d in (10, 11) for h in range(24)}
        bn = {d * T.DAY_MS + h * H: 50.0 for d in (11,) for h in range(24)}
        prof = T.ratio_profile(hl, bn)
        self.assertEqual(list(prof), [11])
        self.assertAlmostEqual(prof[11], 2.0)


def market(px, rate, n=None):
    return {'px': px, 'n': n or {t: 1 for t in px}, 'usd': {t: 1e6 for t in px}, 'rate': rate, 'prem': {},
            'avg': {}, 'px4': {}, 'usd4': {}}


class DailyPairTest(unittest.TestCase):
    def test_funding_signs_and_alignment(self):
        import equity_offhours as EO
        days = [dt.date(2026, 10, 6), dt.date(2026, 10, 7)]
        c0, c1 = EO.close_ms(days[0]), EO.close_ms(days[1])
        hl_px = {c0: 100.0, c1: 102.0}
        bn_px = {c0: 100.0, c1: 102.0}
        # HL pays 1bp an hour to shorts; Binance charges longs 5bp at 00:00, 08:00, 16:00 UTC
        hl_rate = {c0 + k * H: 0.0001 for k in range(1, 25)}
        hl_rate[c0] = 0.05                     # paid at the first close: before the position, must not count
        bn_rate = {ms('2026-10-07T00:00:00'): 0.0005, ms('2026-10-07T08:00:00'): 0.0005,
                   ms('2026-10-07T16:00:00'): 0.0005}
        rows = T.pair_carry_days(market(hl_px, hl_rate), market(bn_px, bn_rate), days)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertAlmostEqual(r['f_hl'], 0.0024)
        self.assertAlmostEqual(r['f_bn'], 0.0015)
        self.assertAlmostEqual(r['pnl'], 0.0024 - 0.0015)    # equal moves: no basis
        self.assertAlmostEqual(r['spread'], 0.0009)

    def test_basis_sign(self):
        import equity_offhours as EO
        days = [dt.date(2026, 10, 6), dt.date(2026, 10, 7)]
        c0, c1 = EO.close_ms(days[0]), EO.close_ms(days[1])
        # HL rises 2%, Binance 1%: short HL / long Binance loses 1%
        rows = T.pair_carry_days(market({c0: 100.0, c1: 102.0}, {}), market({c0: 100.0, c1: 101.0}, {}), days)
        self.assertAlmostEqual(rows[0]['pnl'], -0.01)

    def test_bad_basis_skipped(self):
        import equity_offhours as EO
        days = [dt.date(2026, 10, 6), dt.date(2026, 10, 7)]
        c0, c1 = EO.close_ms(days[0]), EO.close_ms(days[1])
        rows = T.pair_carry_days(market({c0: 100.0, c1: 100.0}, {}), market({c0: 100.0, c1: 50.0}, {}), days)
        self.assertEqual(rows, [])


def venue(n, t0, pay_every, rate, px, prem=0.0):
    v = FA.Venue(n)
    sett = [(t0 + j * H, rate) for j in range(0, n, pay_every)]
    v.fill(t0, n, sett, {t0 + j * H: prem for j in range(n)}, {t0 + j * H: px(j) for j in range(n)})
    return v


class HourlyPairTest(unittest.TestCase):
    def test_always_on_signs(self):
        t0, n = ms('2026-06-01T00:00:00'), 24 * 20
        A = venue(n, t0, 1, 0.0001, lambda j: 100.0)                # HL: 1bp an hour to shorts
        Bv = venue(n, t0, 8, 0.0, lambda j: 100.0 * (1 + 0.0001 * j))  # Binance: no funding, drifts up
        pr = FA.Pair('X', A, Bv, n, a_name='hl', b_name='bn')
        tr = T.simulate_fixed(pr, 1, 4, 0.0, 0.0)
        self.assertEqual(len(tr), 1)
        self.assertGreater(tr[0]['funding'], 0)                     # short HL collects HL's funding
        self.assertGreater(tr[0]['basis'], 0)                       # long Binance gains when Binance rises
        tr2 = T.simulate_fixed(pr, -1, 4, 0.0, 0.0)
        self.assertAlmostEqual(tr2[0]['funding'], -tr[0]['funding'])
        self.assertAlmostEqual(tr2[0]['basis'], -tr[0]['basis'])

    def test_always_on_funding_alignment(self):
        # flat prices: (e - i] hours of 1bp on unit notional, the entry hour's own payment excluded
        t0, n = ms('2026-06-01T00:00:00'), 24 * 20
        A = venue(n, t0, 1, 0.0001, lambda j: 100.0)
        Bv = venue(n, t0, 8, 0.0, lambda j: 100.0)
        pr = FA.Pair('X', A, Bv, n, a_name='hl', b_name='bn')
        tr = T.simulate_fixed(pr, 1, 4, 0.0, 0.0)
        self.assertAlmostEqual(tr[0]['funding'], 0.0001 * (tr[0]['e'] - tr[0]['i']), places=9)
        self.assertEqual(tr[0]['basis'], 0.0)

    def test_costs_charged_once_per_round_trip(self):
        t0, n = ms('2026-06-01T00:00:00'), 24 * 10
        A = venue(n, t0, 1, 0.0, lambda j: 100.0)
        Bv = venue(n, t0, 8, 0.0, lambda j: 100.0)
        pr = FA.Pair('X', A, Bv, n)
        tr = T.simulate_fixed(pr, 1, 4, 0.0003, 0.0003)
        self.assertAlmostEqual(tr[0]['net'], -0.0006)


class OffHoursTest(unittest.TestCase):
    def test_excursions_two_perp_vs_broker(self):
        import equity_offhours as EO
        days = [dt.date(2026, 10, 8), dt.date(2026, 10, 9)]
        p = EO.closed_periods(days)[0]
        hours = range(p['close_ms'] - 2 * H, p['post_ms'] + 2 * H, H)
        # both perps rally 5% overnight together; Binance lags by 0.2% for one hour
        hl = {t: (100.0 if t <= p['close_ms'] else 105.0) for t in hours}
        bn = {t: (100.0 if t <= p['close_ms'] else 105.0) for t in hours}
        lag = p['close_ms'] + 3 * H
        bn[lag] = 105.0 / 1.002
        mh = market(hl, {})
        b = {'px': bn, 'qv': {t: 1.0 for t in bn}}
        rows = T.closed_period_rows(mh, b, [p], 0)
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertAlmostEqual(r['perp_up'], 0.05)                  # the broker hedge's short is 5% under water
        self.assertAlmostEqual(r['basis_up'], 0.002, places=6)      # the two-perp hedge's worst is the lag
        self.assertAlmostEqual(r['basis_gap_open'], 0.0)

    def test_proxy_units(self):
        import equity_offhours as EO
        days = [dt.date(2026, 10, 8), dt.date(2026, 10, 9)]
        p = EO.closed_periods(days)[0]
        hours = range(p['close_ms'] - 2 * H, p['post_ms'] + 2 * H, H)
        hl = {t: 7000.0 for t in hours}                             # index points
        bn = {t: 700.0 for t in hours}                              # the ETF
        rows = T.closed_period_rows(market(hl, {}), {'px': bn, 'qv': {t: 1.0 for t in bn}}, [p], 0, ur=10.0)
        self.assertAlmostEqual(rows[0]['basis_up'], 0.0)

    def test_quantiles(self):
        q = T.quantiles([i / 100 for i in range(101)])
        self.assertAlmostEqual(q['p50'], 0.5)
        self.assertAlmostEqual(q['max'], 1.0)
        self.assertEqual(q['n'], 101)


class BookTest(unittest.TestCase):
    def test_merged_side_prefers_fine_when_it_reaches(self):
        mid = 100.0
        fine = [[99.99, 10.0], [99.7, 10.0]]       # reaches 30bp
        coarse = [[99.9, 100.0]]
        self.assertIs(T.merged_side(fine, coarse, mid, 25), fine)
        fine2 = [[99.99, 10.0]]
        self.assertIs(T.merged_side(fine2, coarse, mid, 25), coarse)

    def test_book_summary(self):
        bids = [[99.95, 10.0], [99.8, 10.0]]
        asks = [[100.05, 10.0], [100.3, 10.0]]
        s = T.book_summary(bids, asks, bids, asks)
        self.assertAlmostEqual(s['half_spread_bp'], 5.0)
        self.assertAlmostEqual(s['bid']['depth25'], 99.95 * 10 + 99.8 * 10)
        self.assertAlmostEqual(s['ask']['depth10'], 100.05 * 10)


if __name__ == '__main__':
    unittest.main()
