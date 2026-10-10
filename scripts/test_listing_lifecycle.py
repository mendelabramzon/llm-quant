#!/usr/bin/env python3
"""Tests for listing_lifecycle.py on synthetic data: P&L signs, time alignment, units, and the bugs fixed on the way.

    python3 -m unittest scripts/test_listing_lifecycle.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import listing_lifecycle as L  # noqa: E402

DAY = L.DAY_MS
HOUR = L.HOUR_MS
T0 = L.ms_of('2025-01-01')


def candles(start_ms, closes, vols=None):
    """Daily candleSnapshot rows opening at start_ms, one per close; a volume of 0 makes a zero-trade bar."""
    out = []
    for i, c in enumerate(closes):
        v = 1000.0 if vols is None else vols[i]
        out.append({'t': start_ms + i * DAY, 'T': start_ms + (i + 1) * DAY - 1, 'c': str(c), 'o': str(c), 'h': str(c),
                    'l': str(c), 'v': str(v), 'n': 10 if v else 0})
    return out


def world(coins, data_end=None):
    """A bare World: {coin: (candle rows, {day: summed funding}, listing_ms, last_live_ms or None)}."""
    W = object.__new__(L.World)
    W.daily, W.fday, W.fcnt, W.frows, W.calendar = {}, {}, {}, {}, {}
    W.delisted = set()
    for c, (rows, fday, listing, last) in coins.items():
        W.daily[c] = L.Daily(rows)
        W.fday[c] = fday
        W.fcnt[c] = {k: 24 for k in fday}
        W.frows[c] = []
        W.calendar[c] = {'coin': c, 'listing_ms': listing, 'last_live_ms': last, 'cohort': 'new_token',
                         'delisted': last is not None}
        if last is not None:
            W.delisted.add(c)
    W.data_end = data_end or max(d.last() for d in W.daily.values())
    W._basket_fday = {}
    return W


COSTS = {'coin_rt': lambda c: 0.002, 'btc_rt': 0.001, 'basket_rt': 0.0015}


class TestCalendar(unittest.TestCase):
    def test_zero_volume_bars_before_listing_are_dropped(self):
        # candleSnapshot fills the days before a market opened with zero-trade bars: the listing is the first traded day
        rows = candles(T0, [5.0, 5.0, 5.0, 2.0, 2.2], vols=[0, 0, 0, 100, 100])
        d = L.Daily(rows)
        self.assertEqual(d.first_traded_open, T0 + 3 * DAY)
        self.assertIsNone(d.at(T0 + 2 * DAY))          # no price before the market traded
        self.assertEqual(d.at(T0 + 4 * DAY), 2.0)       # close of the first traded day, keyed by its end
        self.assertEqual(d.first_bar_open, T0)

    def test_entry_is_close_of_day_d_plus_1(self):
        L_day = T0
        self.assertEqual(L.entry_time(L_day, 1), T0 + 2 * DAY)
        self.assertEqual(L.entry_time(L_day, 7, offset_days=90), T0 + 98 * DAY)

    def test_cohort_tags(self):
        cex = {'OLD': {'binance': T0 - 400 * DAY}, 'NEW': {'binance': T0}, 'PRE': {'bybit': T0 + 10 * DAY}}
        self.assertEqual(L.tag_listing('OLD', T0, cex), 'established')
        self.assertEqual(L.tag_listing('NEW', T0, cex), 'new_token')
        self.assertEqual(L.tag_listing('PRE', T0, cex), 'prelaunch')
        self.assertEqual(L.tag_listing('NONE', T0, cex), 'hl_only')
        self.assertEqual(L.tag_listing('RENDER', T0, cex), 'migration')
        # thousand-unit tickers match the CEX core name
        self.assertEqual(L.hl_core_name('kPEPE'), 'PEPE')

    def test_live_row(self):
        self.assertFalse(L.hl_row_live({'fundingRate': '0.0', 'premium': '0.0'}))
        self.assertTrue(L.hl_row_live({'fundingRate': '0.0000125', 'premium': '0.0'}))


class TestListingTrade(unittest.TestCase):
    def setUp(self):
        n = 400
        flat = candles(T0, [100.0] * n)
        # NEW lists on day 300 and falls from 10 to 8 between its entry and exit
        new = candles(T0 + 300 * DAY, [10.0] * 3 + [8.0] * 97)
        self.W = world({'BTC': (flat, {}, T0, None), 'NEW': (new, {}, T0 + 300 * DAY, None)})

    def test_short_profits_when_coin_falls_against_flat_hedge(self):
        te = T0 + 302 * DAY                               # close of the listing's second day: price 10
        tr = L.listing_trade(self.W, 'NEW', te, 5, 'btc', COSTS)
        self.assertAlmostEqual(tr['coin_return'], -0.2)
        self.assertAlmostEqual(tr['hedge_return'], 0.0)
        # no funding rows: both legs are charged the interest-only floor for the 5 missing days
        self.assertAlmostEqual(tr['funding_short_received'], 5 * L.FLOOR_RATE_DAY)
        self.assertAlmostEqual(tr['funding_hedge_paid'], 5 * L.FLOOR_RATE_DAY)
        self.assertAlmostEqual(tr['pnl'], 0.2 - 0.002 - 0.001)

    def test_funding_sign_and_price_weighting(self):
        te = T0 + 302 * DAY
        # +1% a day paid by longs: the short receives it, on a notional that shrinks to 0.8 once the price drops
        # (the close ending day 303 is still 10; from day 304 on it is 8)
        self.W.fday['NEW'] = {te + k * DAY: 0.01 for k in range(5)}
        tr = L.listing_trade(self.W, 'NEW', te, 5, 'btc', COSTS)
        self.assertAlmostEqual(tr['funding_short_received'], 0.01 * (1.0 + 1.0 + 3 * 0.8))
        self.assertEqual(tr['funding_days_missing'], 0)
        # negative funding: the short pays
        self.W.fday['NEW'] = {te + k * DAY: -0.01 for k in range(5)}
        tr2 = L.listing_trade(self.W, 'NEW', te, 5, 'btc', COSTS)
        self.assertLess(tr2['pnl'], tr['pnl'])
        self.assertAlmostEqual(tr2['funding_short_received'], -0.01 * (1.0 + 1.0 + 3 * 0.8))

    def test_delisted_coin_closes_at_its_last_close(self):
        te = T0 + 302 * DAY
        self.W.calendar['NEW']['last_live_ms'] = T0 + 310 * DAY - 14 * HOUR
        tr = L.listing_trade(self.W, 'NEW', te, 60, 'btc', COSTS)
        self.assertTrue(tr['closed_early'])
        self.assertEqual(tr['tx'], T0 + 310 * DAY)
        self.assertAlmostEqual(tr['coin_return'], -0.2)

    def test_max_adverse_uses_daily_highs_after_entry(self):
        rows = candles(T0 + 300 * DAY, [10.0] * 3 + [8.0] * 97)
        rows[4]['h'] = '25.0'                             # a squeeze to 25 intraday on the 5th day, closing at 8
        self.W.daily['NEW'] = L.Daily(rows)
        tr = L.listing_trade(self.W, 'NEW', T0 + 302 * DAY, 5, 'btc', COSTS)
        self.assertAlmostEqual(tr['max_adverse'], 1.5)
        self.assertAlmostEqual(tr['coin_return'], -0.2)   # the close-to-close P&L does not see it
        st = L.squeeze_stats([dict(tr, pnl=0.1)])
        self.assertEqual(st['share_over_100pct'], 1.0)

    def test_hedge_loss_reduces_pnl(self):
        rising = candles(T0, [100.0] * 302 + [90.0] * 98)    # the hedge falls 10% over the window
        self.W.daily['BTC'] = L.Daily(rising)
        tr = L.listing_trade(self.W, 'NEW', T0 + 302 * DAY, 5, 'btc', COSTS)
        self.assertAlmostEqual(tr['hedge_return'], -0.1)
        self.assertAlmostEqual(tr['pnl'], 0.2 - 0.1 - 0.003)


class TestBasket(unittest.TestCase):
    def test_members_need_age_and_delisted_close_at_last(self):
        n = 400
        coins = {
            'BTC': (candles(T0, [1.0] * n), {}, T0, None),
            'OLD': (candles(T0, [10.0] * 200 + [20.0] * 200), {}, T0, None),                 # +100% at day 200
            'DEAD': (candles(T0, [10.0] * 210), {}, T0, T0 + 210 * DAY),                     # delisted on day 210
            'YOUNG': (candles(T0 + 150 * DAY, [5.0] * 250), {}, T0 + 150 * DAY, None),       # too young at day 190
        }
        W = world(coins)
        mem = W.basket_members(T0 + 190 * DAY)
        self.assertEqual(sorted(mem), ['DEAD', 'OLD'])                    # BTC is not an alt; YOUNG is not seasoned
        r, n_ = W.basket_return(T0 + 190 * DAY, T0 + 300 * DAY)
        self.assertEqual(n_, 2)
        self.assertAlmostEqual(r, (1.0 + 0.0) / 2)                        # DEAD closed flat at its last close


class TestNotices(unittest.TestCase):
    def test_settlement_sentence(self):
        text = ('Binance Futures will close all positions and conduct an automatic settlement on USDⓈ-M MYROUSDT and '
                '1000XUSDT Perpetual Contracts at  2025-11-14 09:00 (UTC) . The contracts will be delisted after the '
                'settlement is complete. Users are  not allowed  to open new positions for the aforementioned '
                'contract(s) starting from  2025-11-14 08:30 (UTC) . During the final hour ...')
        rows, tokens = L.parse_delisting(text, 'Binance Futures Will Delist USDⓈ-M MYROUSDT and 1000XUSDT Perpetual Contracts')
        got = {r['symbol']: (r['settle_ms'], r['reduce_only_ms']) for r in rows}
        self.assertEqual(sorted(got), ['1000XUSDT', 'MYROUSDT'])
        self.assertEqual(got['MYROUSDT'], (L.ms_of('2025-11-14T09:00:00+00:00'), L.ms_of('2025-11-14T08:30:00+00:00')))
        self.assertEqual(tokens, [])

    def test_as_below_list(self):
        text = ('Binance Futures will close all positions and conduct an automatic settlement the following perpetual '
                'contract(s) as below: 2026-10-05 09:00 (UTC) : USDⓈ-M PROMPTUSDT, PUMPBTCUSDT and 1000000BOBUSDT '
                'Perpetual Contracts The contract(s) will be delisted after the settlement is complete. Users are  not '
                'allowed  to open new non-reduce only orders for the aforementioned contract(s) as below: 2026-10-05 '
                '08:30 (UTC) : USDⓈ-M PROMPTUSDT, PUMPBTCUSDT and 1000000BOBUSDT Perpetual Contracts During ...')
        rows, _ = L.parse_delisting(text)
        self.assertEqual(sorted(r['symbol'] for r in rows), ['1000000BOBUSDT', 'PROMPTUSDT', 'PUMPBTCUSDT'])
        self.assertTrue(all(r['settle_ms'] == L.ms_of('2026-10-05T09:00:00+00:00') for r in rows))
        self.assertTrue(all(r['reduce_only_ms'] == L.ms_of('2026-10-05T08:30:00+00:00') for r in rows))

    def test_spot_notice_aforementioned_tokens(self):
        text = ('Futures Binance Futures will close all positions and conduct an automatic settlement on the contracts '
                'of the aforementioned token(s) at  2026-08-26 09:00 (UTC) . The contracts will be delisted after the '
                'settlement is complete.')
        rows, tokens = L.parse_delisting(text, 'Binance Will Delist ICX, SCRT, STORJ on 2026-09-03')
        self.assertEqual(tokens, ['ICX', 'SCRT', 'STORJ'])
        self.assertEqual(rows[0]['symbol'], None)
        self.assertEqual(rows[0]['settle_ms'], L.ms_of('2026-08-26T09:00:00+00:00'))
        syms = [{'symbol': 'ICXUSDT', 'baseAsset': 'ICX', 'contractType': 'PERPETUAL'},
                {'symbol': '1000SCRTUSDT', 'baseAsset': '1000SCRT', 'contractType': 'PERPETUAL'},
                {'symbol': 'STORJUSD_PERP', 'baseAsset': 'STORJ', 'contractType': 'DELIVERY'}]
        self.assertEqual(L.resolve_tokens(tokens, syms), ['1000SCRTUSDT', 'ICXUSDT'])

    def test_notice_filter(self):
        self.assertTrue(L.is_delisting_notice('Binance Will Delist ACX, HFT on 2026-08-17'))
        self.assertTrue(L.is_delisting_notice('Binance Futures Will Delist USDⓈ-M AERGOUSDT Perpetual Contract'))
        self.assertFalse(L.is_delisting_notice('Binance Margin And Loan Will Delist TST & IOTX on 2026-07-10'))
        self.assertFalse(L.is_delisting_notice('Binance Alpha Will Remove SUP'))


class TestDelistingTrades(unittest.TestCase):
    def hourly(self, start, closes):
        return L.Hourly([[start + i * HOUR - HOUR, 0, 0, 0, c, 1000.0] for i, c in enumerate(closes)])

    def test_drift_short_profits_when_coin_falls(self):
        px = self.hourly(T0, [1.0] * 10 + [0.5] * 10)
        fund = [(T0 + 12 * HOUR, -0.02)]            # one settlement of -2%: the short pays it
        tr = L.drift_trade(px, fund, 0.0, T0 + 5 * HOUR, T0 + 15 * HOUR, 0.001, 0.001)
        self.assertAlmostEqual(tr['coin_return'], -0.5)
        self.assertAlmostEqual(tr['funding_short_received'], -0.02)
        self.assertAlmostEqual(tr['pnl'], 0.5 - 0.02 - L.FLOOR_RATE_H * 10 - 0.002)

    def test_pair_trade_signs(self):
        a = self.hourly(T0, [1.0] * 20)                      # short leg flat
        b = self.hourly(T0, [1.0] * 10 + [1.1] * 10)         # long leg +10%
        fa = [(T0 + 8 * HOUR, 0.01)]                         # short venue's longs pay 1%: received
        fb = [(T0 + 8 * HOUR, 0.002)]                        # long venue: paid
        tr = L.pair_trade(a, fa, b, fb, T0 + 2 * HOUR, T0 + 15 * HOUR, 0.003)
        self.assertAlmostEqual(tr['funding'], 0.008)
        self.assertAlmostEqual(tr['basis'], 0.1)
        self.assertAlmostEqual(tr['pnl'], 0.108 - 0.003)
        # a settlement exactly at entry is not received; one exactly at exit is
        self.assertAlmostEqual(L.settlements_between([(10, 1.0), (20, 2.0)], 10, 20), 2.0)

    def test_inferred_announcement(self):
        start = T0
        vols = [100.0] * (30 * 24)
        last = start + 30 * 24 * HOUR
        k = 30 * 24 - 30                                     # a burst 30 hours before the last hour
        for i in range(k, k + 6):
            vols[i] = 50_000.0
        h = L.Hourly([[start + i * HOUR, 0, 0, 0, 1.0, v] for i, v in enumerate(vols)])
        A = L.infer_hl_announcement(h, last)
        self.assertIsNotNone(A)
        self.assertLessEqual(abs(A - (start + (k + 1) * HOUR)), 2 * HOUR)


class TestCosts(unittest.TestCase):
    def test_round_trip_and_extrapolation(self):
        mid = 100.0
        bids = [(99.9, 100.0), (99.8, 100.0)]                # $9,990 + $9,980 shown
        asks = [(100.1, 100.0), (100.2, 100.0)]
        fine = (mid, bids, asks)
        rt = L.round_trip_bp(fine, None, 5_000)
        self.assertAlmostEqual(rt, 2 * 4.5 + 10.0 + 10.0, places=6)     # fees + 10bp a side inside the first level
        # beyond the shown book: linear in size, never cheaper per dollar than the largest fillable size
        big = L.round_trip_bp(fine, None, 40_000)
        self.assertGreater(big, L.round_trip_bp(fine, None, 19_000))
        self.assertIsNone(L.round_trip_bp(fine, None, 40_000, extrapolate=False))
        self.assertFalse(L.fillable(fine, None, 40_000))

    def test_depth_cost_monotonic(self):
        c = [L.bn_cost_bp(u, 1e6, 5.0, 3.0, 0.02) for u in (10_000, 50_000, 100_000)]
        self.assertTrue(c[0] < c[1] < c[2])

    def test_week_groups(self):
        pairs = [(0, 1.0), (DAY, 3.0), (8 * DAY, 5.0)]
        self.assertEqual(L.by_group_means(pairs), [2.0, 5.0])


if __name__ == '__main__':
    unittest.main()
