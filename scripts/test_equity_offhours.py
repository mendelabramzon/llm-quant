#!/usr/bin/env python3
"""equity_offhours on cases whose answers are known: the US session calendar (DST, holidays, half days), the builder
funding formula and implied oracle, session rows built from a synthetic market, and the sign of every P&L leg."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import equity_offhours as E  # noqa: E402

H = E.HOUR_MS
D = dt.date


def utc_ms(y, mo, d, h, mi=0):
    return int(dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone.utc).timestamp() * 1000)


class Calendar(unittest.TestCase):
    def test_dst_boundaries(self):
        self.assertFalse(E.us_dst(D(2026, 3, 6)))     # Friday before the second Sunday of March
        self.assertTrue(E.us_dst(D(2026, 3, 9)))      # Monday after it
        self.assertTrue(E.us_dst(D(2026, 10, 30)))
        self.assertFalse(E.us_dst(D(2026, 11, 2)))    # first Sunday of November 2026 is the 1st
        self.assertTrue(E.us_dst(D(2025, 10, 31)))
        self.assertFalse(E.us_dst(D(2025, 11, 3)))    # 2025's first Sunday of November is the 2nd

    def test_session_times(self):
        self.assertEqual(E.open_ms(D(2026, 7, 6)), utc_ms(2026, 7, 6, 13, 30))
        self.assertEqual(E.close_ms(D(2026, 7, 6)), utc_ms(2026, 7, 6, 20))
        self.assertEqual(E.open_ms(D(2026, 1, 5)), utc_ms(2026, 1, 5, 14, 30))
        self.assertEqual(E.close_ms(D(2026, 1, 5)), utc_ms(2026, 1, 5, 21))
        self.assertEqual(E.close_ms(D(2025, 11, 28)), utc_ms(2025, 11, 28, 18))   # half day, 13:00 EST

    def test_weekend_across_dst_switch_is_an_hour_shorter(self):
        p = E.closed_periods([D(2026, 3, 5), D(2026, 3, 6), D(2026, 3, 9)])
        self.assertEqual([x['kind'] for x in p], ['overnight', 'weekend'])
        self.assertEqual(p[0]['closed_hours'], 17.5)
        self.assertEqual(p[1]['closed_hours'], 64.5)
        self.assertEqual(p[1]['pre_ms'], utc_ms(2026, 3, 9, 13))
        self.assertEqual(p[1]['post_ms'], utc_ms(2026, 3, 9, 14))

    def test_holidays_and_half_days(self):
        p = E.closed_periods([D(2026, 9, 4), D(2026, 9, 8)])          # Labor Day
        self.assertEqual(p[0]['kind'], 'holiday')
        self.assertEqual(p[0]['closed_hours'], 89.5)
        p = E.closed_periods([D(2026, 6, 18), D(2026, 6, 22)])        # Juneteenth on a Friday
        self.assertEqual(p[0]['kind'], 'holiday')
        p = E.closed_periods([D(2025, 12, 24), D(2025, 12, 26)])      # half day, then Christmas
        self.assertEqual(p[0]['kind'], 'holiday')
        self.assertTrue(p[0]['half_day_close'])
        self.assertEqual(p[0]['close_ms'], utc_ms(2025, 12, 24, 18))
        self.assertEqual(p[0]['closed_hours'], 44.5)


class FundingAndOracle(unittest.TestCase):
    def test_formula_reproduces_observed_rows(self):
        # xyz:TSLA rows from the 2026-10-09 store: (premium, rate)
        for prem, rate in ((4.747e-4, 1.092e-5), (4.031e-4, 6.445e-6), (-3.047059e-4, -2.941e-7), (3.408e-4, 6.25e-6)):
            self.assertAlmostEqual(E.funding_rate(prem), rate, delta=0.01 * abs(rate) + 2e-9)

    def test_per_dex_parameters(self):
        # mkts:US500 in the dead zone pays a 5%-a-year interest leg; io:SNDK fits trade.xyz's parameters
        self.assertAlmostEqual(E.funding_rate(-0.00016194, *E.funding_params('mkts:US500')), 5.7078e-06, places=9)
        self.assertAlmostEqual(E.funding_rate(0.0006355803, *E.funding_params('io:SNDK')), 2.09738e-05, places=9)
        self.assertEqual(E.funding_params('para:AVGO'), (0.6, 0.0001))

    def test_dead_zone_pays_the_interest_leg(self):
        for p in (-0.0002, 0.0, 0.0001, 0.0004):
            self.assertAlmostEqual(E.funding_rate(p), 6.25e-6)

    def test_implied_oracle(self):
        self.assertAlmostEqual(E.implied_oracle(101.0, 0.01), 100.0)
        self.assertIsNone(E.implied_oracle(None, 0.01))

    def test_fee_schedule(self):
        self.assertAlmostEqual(E.taker_fee_bps('enabled', 1.0), 0.9)
        self.assertAlmostEqual(E.taker_fee_bps(None, 1.0), 9.0)
        self.assertAlmostEqual(E.taker_fee_bps(None, 2.0), 18.0)
        self.assertAlmostEqual(E.taker_fee_bps('enabled', 0.5), 0.675)


def synthetic_market(prices, rates=None, start=None):
    """prices: {hour boundary ms: price}; every hour gets a candle with 100 trades."""
    m = {'coin': 'xyz:TEST', 'px': {}, 'avg': {}, 'n': {}, 'usd': {}, 'prem': {}, 'rate': {}}
    for T, p in prices.items():
        m['px'][T], m['avg'][T], m['n'][T], m['usd'][T] = p, p, 100, 1e6
        m['prem'][T] = 0.0
        m['rate'][T] = (rates or {}).get(T, 6.25e-6)
    m['first'], m['last'] = min(prices), max(prices)
    return m


class Sessions(unittest.TestCase):
    def setUp(self):
        self.periods = E.closed_periods([D(2026, 7, 6), D(2026, 7, 7)])
        p = self.periods[0]
        t0 = p['close_ms'] - 3 * H
        prices = {t0 + k * H: 100.0 for k in range(0, 30)}
        prices[p['close_ms']] = 100.0
        prices[p['pre_ms']] = 101.0       # perp up 1% by 30 min before the open
        prices[p['post_ms']] = 102.0
        prices[p['post2_ms']] = 102.5
        prices[p['close1_ms']] = 103.0
        self.m = synthetic_market(prices)
        self.ref = {'2026-07-06': {'open': 99.0, 'close': 100.0}, '2026-07-07': {'open': 102.0, 'close': 103.0}}

    def test_row_values(self):
        r = E.session_rows(self.m, self.ref, self.periods)[0]
        self.assertAlmostEqual(r['gap'], 0.02)
        self.assertAlmostEqual(r['r_off'], 0.01)
        self.assertAlmostEqual(r['unpriced'], 102.0 / 101.0 - 1)
        self.assertAlmostEqual(r['r_open'], 102.0 / 101.0 - 1)
        self.assertFalse(r['bad_basis'])
        # 17 boundaries from the 20:00 close to 13:00, each paying the 6.25e-6 interest leg
        self.assertEqual(r['funding_closed_hours'], 17)
        self.assertAlmostEqual(r['funding_closed'], 17 * 6.25e-6)

    def test_index_scale_only_affects_the_basis_check(self):
        ref = {d: {'open': v['open'] / 10.0, 'close': v['close'] / 10.0} for d, v in self.ref.items()}   # ETF units
        r0 = E.session_rows(self.m, self.ref, self.periods)[0]
        r1 = E.session_rows(self.m, ref, self.periods, scale=10.0)[0]
        self.assertFalse(r1['bad_basis'])
        for k in ('gap', 'r_off', 'unpriced', 'r_open'):
            self.assertAlmostEqual(r0[k], r1[k])
        self.assertTrue(E.session_rows(self.m, ref, self.periods)[0]['bad_basis'])

    def test_bad_basis_is_flagged(self):
        ref = dict(self.ref)
        ref['2026-07-06'] = {'open': 99.0, 'close': 50.0}            # a split the perp did not follow
        r = E.session_rows(self.m, ref, self.periods)[0]
        self.assertTrue(r['bad_basis'])

    def test_stale_lookup(self):
        m = synthetic_market({0: 10.0, H: 11.0})
        self.assertEqual(E.px_at(m, 3 * H), (11.0, 2))
        self.assertEqual(E.px_at(m, 4 * H), (None, None))


class PnLSigns(unittest.TestCase):
    def test_trade_return(self):
        row = {'r_open': 0.01, 'funding_pre_post': 1e-4}
        self.assertAlmostEqual(E.trade_return(row, +1, 'post', 10.0), 0.01 - 1e-4 - 1e-3)
        self.assertAlmostEqual(E.trade_return(row, -1, 'post', 10.0), -0.01 + 1e-4 - 1e-3)
        self.assertIsNone(E.trade_return(row, +1, 'post', None))

    def test_follow_and_fade_are_mirror_images_before_costs(self):
        by = {'2026-07-07': [{'coin': 'a', 'kind': 'overnight', 'r_off': 0.02, 'r_open': 0.01, 'r_open2': 0.01,
                              'r_day': 0.01, 'funding_pre_post': 0.0, 'funding_pre_post2': 0.0,
                              'funding_pre_close1': 0.0}]}
        s, v, _ = E.family_open(by, lambda c, side, ex: 0.0, ks=(0.0,), exits=('post',), subsets=('all',))
        self.assertAlmostEqual(v['follow|k=0|exit=post|all'][0], 0.01)
        self.assertAlmostEqual(v['fade|k=0|exit=post|all'][0], -0.01)

    def test_hedged_family_trades_the_residual(self):
        z = {'funding_pre_post': 0.0, 'funding_pre_post2': 0.0, 'funding_pre_close1': 0.0, 'r_open2': None,
             'r_day': None, 'kind': 'overnight'}
        name = dict(z, coin='xyz:A', r_off=0.02, r_open=0.01)
        idx = dict(z, coin='xyz:IDX', r_off=0.01, r_open=0.004)
        by = {'d': [name, idx]}
        s, v, t = E.family_open(by, lambda c, side, ex: 0.0, ks=(0.0,), exits=('post',), subsets=('all',),
                                hedge={'d': idx}, hedge_coin='xyz:IDX')
        self.assertAlmostEqual(v['hedged|follow|k=0|exit=post|all'][0], 0.006)
        self.assertAlmostEqual(v['hedged|fade|k=0|exit=post|all'][0], -0.006)
        self.assertEqual(len(t['hedged|follow|k=0|exit=post|all']), 1)     # the index itself is never a name leg

    def test_threshold_keeps_small_moves_flat(self):
        by = {'d': [{'coin': 'a', 'kind': 'overnight', 'r_off': 0.004, 'r_open': 0.01, 'r_open2': None, 'r_day': None,
                     'funding_pre_post': 0.0, 'funding_pre_post2': 0.0, 'funding_pre_close1': 0.0}]}
        s, v, t = E.family_open(by, lambda c, side, ex: 0.0, ks=(0.005,), exits=('post',), subsets=('all',))
        self.assertEqual(v['follow|k=0.005|exit=post|all'], [0.0])
        self.assertEqual(t['follow|k=0.005|exit=post|all'], [])


class Carry(unittest.TestCase):
    def test_hedged_carry_is_funding_plus_dividend(self):
        days = [D(2026, 7, 6), D(2026, 7, 7), D(2026, 7, 8)]
        prices = {}
        t0 = E.close_ms(days[0]) - 2 * H
        for k in range(0, 60):
            prices[t0 + k * H] = 100.0
        m = synthetic_market(prices)
        # both legs flat; the stock goes ex a $0.50 dividend on the 8th and drops by it, the perp drops with the oracle
        for T in list(m['px']):
            if T >= E.close_ms(days[1]) + H:
                m['px'][T] = 99.5
        ref = {'2026-07-06': {'open': 100.0, 'close': 100.0}, '2026-07-07': {'open': 100.0, 'close': 100.0},
               '2026-07-08': {'open': 99.5, 'close': 99.5}}
        divs = [{'ex_date': '2026-07-08', 'amount': 0.5}]
        out = E.carry_days(m, ref, days, divs)
        self.assertEqual(len(out), 2)
        self.assertAlmostEqual(out[0]['pnl'], 24 * 6.25e-6)                    # one day of the interest leg
        # day 2: stock -0.5% + 0.5% dividend, perp -0.5% (the short gains it), plus funding
        self.assertAlmostEqual(out[1]['pnl'], 24 * 6.25e-6 + 0.005)
        self.assertEqual(out[1]['mark'], '1h')

    def test_family_selects_on_the_past_only(self):
        days = [D(2026, 7, 1) + dt.timedelta(days=i) for i in range(60)]
        hi = [{'d': d.isoformat(), 'funding': 0.0004, 'pnl': 0.0004, 'vol_usd': 2e6} for d in days]
        lo = [{'d': d.isoformat(), 'funding': 0.0, 'pnl': 0.0, 'vol_usd': 2e6} for d in days]
        thin = [{'d': d.isoformat(), 'funding': 0.001, 'pnl': 0.001, 'vol_usd': 1e4} for d in days]
        dl, v, mem, raw = E.family_carry({'hi': hi, 'lo': lo, 'thin': thin}, {}, days,
                                         {'hi': 0.0, 'lo': 0.0, 'thin': 0.0}, capital_per_notional=1.0, ssr=0.0,
                                         rebalance=20, vol_floors=(1e6,), rules=('trail_8pct',))
        ser = v['carry|trail_8pct|vol>=1M']
        self.assertEqual(ser[:20], [0.0] * 20)                                 # no history yet: flat
        self.assertAlmostEqual(ser[25], 0.0004)                                # 'hi' trails ~10%/yr, 'lo' 0
        self.assertEqual(mem['carry|trail_8pct|vol>=1M'][1][1], ['hi'])         # 'thin' pays more but trades $10k a day


class Persistence(unittest.TestCase):
    def test_constant_funding_is_perfectly_persistent(self):
        days = [D(2026, 7, 1) + dt.timedelta(days=i) for i in range(80)]
        t0, t1 = E.close_ms(days[0]) - 24 * H, E.close_ms(days[-1])
        ms = {}
        for k, apr in enumerate((0.0, 0.03, 0.06, 0.09, 0.12, 0.15)):
            ms['n%d' % k] = {'rate': {T: apr / 8760 for T in range(t0, t1 + 1, H)}}
        r = E.funding_persistence(ms, days, rebalance=21, trail=30, fwd=21, thresh=0.08)
        self.assertGreaterEqual(len(r['rebalances']), 1)
        self.assertAlmostEqual(r['mean_spearman'], 1.0)
        self.assertAlmostEqual(r['mean_fwd_apr_selected'], 0.12, places=6)   # the 9%, 12% and 15% names
        self.assertAlmostEqual(r['mean_fwd_apr_all'], 0.075, places=6)


class Books(unittest.TestCase):
    def test_walk_and_depth(self):
        levels = [[{'px': '99.9', 'sz': '100'}, {'px': '99.5', 'sz': '100'}],
                  [{'px': '100.1', 'sz': '100'}, {'px': '100.5', 'sz': '100'}]]
        c, u = E.walk_cost_bps(levels, 'buy', 100.0, 5000)
        self.assertAlmostEqual(c, 10.0)
        self.assertEqual(u, 0.0)
        c, u = E.walk_cost_bps(levels, 'buy', 100.0, 1e6)
        self.assertGreater(u, 0.9)
        s = E.book_summary(levels)
        self.assertAlmostEqual(s['spread_bps'], 20.0)
        self.assertAlmostEqual(s['depth25_ask_usd'], 10010.0)   # only the 100.1 level is within 25bp of 100


class Stats(unittest.TestCase):
    def test_spearman(self):
        self.assertAlmostEqual(E.spearman([(1, 10), (2, 20), (3, 25), (4, 40)]), 1.0)
        self.assertAlmostEqual(E.spearman([(1, 4), (2, 3), (3, 2), (4, 1)]), -1.0)


class Discovery(unittest.TestCase):
    def test_half_priced(self):
        rows = []
        for k in range(40):
            g = (k - 20) / 1000.0
            rows.append({'d1': '2026-07-%02d' % (k % 28 + 1), 'coin': 'c%d' % (k % 3), 'gap': g, 'r_off': 0.5 * g,
                         'unpriced': g - 0.5 * g})
        s = E.discovery_stats(rows)
        self.assertAlmostEqual(s['share_priced'], 0.5)
        self.assertAlmostEqual(s['gap_on_perp_slope'], 2.0)
        self.assertAlmostEqual(s['gap_on_perp_r2'], 1.0)


if __name__ == '__main__':
    unittest.main()
