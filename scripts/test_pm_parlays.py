#!/usr/bin/env python3
"""pm_parlays: combo fair value, fees, the maker's P&L, the quoting rule and the onchain decoder on known answers."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_parlays as P  # noqa: E402


class LegPricing(unittest.TestCase):
    def test_yes_and_no_legs(self):
        for a, b in zip(P.leg_prob(0.40, 0.42, 'yes'), (0.41, 0.40, 0.42)):
            self.assertAlmostEqual(a, b)
        mid, lo, hi = P.leg_prob(0.40, 0.42, 'no')
        self.assertAlmostEqual(mid, 0.59)
        self.assertAlmostEqual(lo, 0.58)
        self.assertAlmostEqual(hi, 0.60)

    def test_one_sided_or_wide_books_are_unpriced(self):
        # Kalshi candles show an empty ask as 0.999 and an empty bid as 0: neither is a price
        self.assertIsNone(P.leg_prob(0.0, 0.55, 'yes'))
        self.assertIsNone(P.leg_prob(0.30, 0.999, 'yes'))
        self.assertIsNone(P.leg_prob(0.30, 0.45, 'yes'))            # 15c wide > 10c cap
        self.assertIsNotNone(P.leg_prob(0.30, 0.45, 'yes', max_spread=0.2))
        self.assertIsNone(P.leg_prob(0.50, 0.49, 'yes'))            # crossed
        self.assertIsNone(P.leg_prob(None, 0.5, 'yes'))
        self.assertIsNone(P.leg_prob(0.4, 0.42, 'maybe'))

    def test_combo_fair_is_the_product_with_bounds(self):
        f = P.combo_fair([(0.5, 0.49, 0.51), (0.6, 0.59, 0.61), (0.8, 0.79, 0.81)])
        self.assertAlmostEqual(f[0], 0.24)
        self.assertAlmostEqual(f[1], 0.49 * 0.59 * 0.79)
        self.assertAlmostEqual(f[2], 0.51 * 0.61 * 0.81)
        self.assertIsNone(P.combo_fair([(0.5, 0.49, 0.51), None]))
        self.assertIsNone(P.combo_fair([]))

    def test_implied_margin(self):
        self.assertAlmostEqual(P.implied_margin(0.26, 0.2), 0.30)
        self.assertAlmostEqual(P.implied_margin(0.18, 0.2), -0.10)
        self.assertIsNone(P.implied_margin(0.2, None))
        self.assertIsNone(P.implied_margin(0.2, 0.0))


class Fees(unittest.TestCase):
    def test_combo_maker_fee_is_half_the_taker_rate_rounded_up_to_the_cent(self):
        # 100 contracts at 50c: taker 0.07*25 = $1.75; maker 0.035*25 = $0.875 -> $0.88 (the press "$0.88 cap")
        self.assertAlmostEqual(P.combo_taker_fee(100, 0.5), 1.75)
        self.assertAlmostEqual(P.combo_maker_fee(100, 0.5, True), 0.88)
        self.assertEqual(P.combo_maker_fee(100, 0.5, False), 0.0)
        # a 9c parlay, 100 contracts: 0.035*100*0.09*0.91 = 0.28665 -> $0.29, about 3.2% of the 9.00 premium
        self.assertAlmostEqual(P.combo_maker_fee(100, 0.09, True), 0.29)

    def test_which_trades_pay_the_maker_fee(self):
        before = P.parse_ts('2026-08-19T12:00:00Z')
        after = P.parse_ts('2026-08-21T12:00:00Z')
        self.assertFalse(P.maker_fee_applies('KXMVECROSSCATEGORY-S2026X-Y', before, 'actual'))
        self.assertTrue(P.maker_fee_applies('KXMVECROSSCATEGORY-S2026X-Y', after, 'actual'))
        self.assertTrue(P.maker_fee_applies('KXMVECROSSCATEGORY-S2026X-Y', before, 'current'))
        # the uncorrelated-NFL shard carries fee_type 'quadratic' (takers only)
        self.assertFalse(P.maker_fee_applies('KXMVECROSSCATEGORY0-S2026X-Y', after, 'current'))
        self.assertFalse(P.maker_fee_applies('KXMVENBASINGLEGAME-26OCT07PHXCHI-X', after, 'current'))

    def test_polymarket_combo_fee_matches_the_chain(self):
        # tx 0x556d2b6f...: requester bought 535.883204 YES for 229.99959 pUSD, FeeCharged 6.56422
        shares, usd = 535.883204, 229.99959
        self.assertAlmostEqual(P.pm_fee(shares, usd / shares), 6.56422, places=4)


class MakerPnl(unittest.TestCase):
    def test_selling_yes_to_a_parlay_buyer(self):
        # sold 100 YES at 0.10 with a 0.32 fee; the parlay lost: keep the 10.00 premium less the fee
        self.assertEqual(P.maker_pnl(0.10, 100, 'yes', 0.0, 0.32), (10.0 - 0.32, 90.0 + 0.32))
        pnl, cap = P.maker_pnl(0.10, 100, 'yes', 1.0, 0.32)
        self.assertAlmostEqual(pnl, -90.32)
        self.assertAlmostEqual(cap, 90.32)
        # a void leg settles the combo at a scalar value: 0.7 x $1
        pnl, _ = P.maker_pnl(0.10, 100, 'yes', 0.7, 0.0)
        self.assertAlmostEqual(pnl, -60.0)

    def test_buying_yes_from_a_cash_out(self):
        pnl, cap = P.maker_pnl(0.30, 10, 'no', 1.0, 0.0)
        self.assertAlmostEqual(pnl, 7.0)
        self.assertAlmostEqual(cap, 3.0)
        with self.assertRaises(ValueError):
            P.maker_pnl(0.3, 10, 'sideways', 1.0, 0.0)


class QuotingRule(unittest.TestCase):
    def test_own_quote_wins_only_below_the_print_and_fills_at_the_quote(self):
        # fair 0.10, m 0.05 -> quote 0.105; incumbent printed 0.12 -> we win at 0.105
        self.assertAlmostEqual(P.own_quote_fill(0.12, 0.10, 0.05), 0.105)
        # incumbent printed 0.104 < our 0.105 -> the incumbent keeps it
        self.assertIsNone(P.own_quote_fill(0.104, 0.10, 0.05))
        # a tie goes to the incumbent
        self.assertIsNone(P.own_quote_fill(0.105, 0.10, 0.05))
        # the quote rounds UP to the 0.001 grid: 0.0123456 * 1.1 = 0.01358 -> 0.014
        self.assertAlmostEqual(P.own_quote_fill(0.02, 0.0123456, 0.10), 0.014)
        self.assertIsNone(P.own_quote_fill(0.5, None, 0.1))
        self.assertIsNone(P.own_quote_fill(0.999, 0.95, 0.10))   # quote would be >= 1


class Classification(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(P.structure_of(['a', 'b', 'c']), 'cross')
        self.assertEqual(P.structure_of(['a', 'a']), 'same')
        self.assertEqual(P.structure_of(['a', 'a', 'b']), 'mixed')
        self.assertIsNone(P.structure_of([]))

    def test_game_lookup_by_event_then_by_game_code(self):
        ms = [{'id': 'g1', 'start': '2026-10-11T17:00:00Z', 'events': ['KXNFLGAME-26OCT11CINMIA', 'KXNFLTD-26OCT11CINMIA']},
              {'id': 'g2', 'start': '2026-10-11T17:05:00Z', 'events': ['KXMLBGAME-26OCT11NYYBOS']},
              {'id': 'g3', 'start': '2026-10-11T23:05:00Z', 'events': ['KXMLBTOTAL-26OCT11NYYBOS']}]   # doubleheader
        be, bc = P.milestone_index(ms)
        self.assertEqual(P.game_of('KXNFLGAME-26OCT11CINMIA', be, bc)[0], 'g1')
        # a team-scoped event not listed on the milestone falls back to the game code
        self.assertEqual(P.game_of('KXNFLTEAMFIRSTTD-26OCT11CINMIA-CIN', be, bc)[0], 'g1')
        # a doubleheader's shared code is ambiguous and dropped from the fallback; listed events still map
        self.assertIsNone(P.game_of('KXMLBSPREAD-26OCT11NYYBOS', be, bc))
        self.assertEqual(P.game_of('KXMLBTOTAL-26OCT11NYYBOS', be, bc)[0], 'g3')
        self.assertIsNone(P.game_of('KXBTC15M-26OCT140315', be, bc))
        self.assertEqual(P.game_code('KXNFLTD-26OCT11CHIGB'), '26OCT11CHIGB')

    def test_leg_book_is_the_last_candle_at_or_before_the_trade(self):
        m1 = [[100, 0.40, 0.42, None, 0], [160, None, None, None, 0], [220, 0.45, 0.47, None, 0]]
        h1 = [[50, 0.30, 0.33, None, 0]]
        self.assertEqual(P.leg_book_at(m1, h1, 219), (0.40, 0.42, 119))   # skips the None row at 160
        self.assertEqual(P.leg_book_at(m1, h1, 220), (0.45, 0.47, 0))
        self.assertEqual(P.leg_book_at(m1, h1, 99), (0.30, 0.33, 49))     # falls back to the hourly candle
        self.assertIsNone(P.leg_book_at(m1, h1, 10))
        self.assertIsNone(P.leg_book_at(None, None, 10))

    def test_windows_are_stratified_and_reproducible(self):
        w = P.sample_windows('2026-09-01', '2026-09-02', 6, 60)
        self.assertEqual(len(w), 12)
        self.assertEqual(w, P.sample_windows('2026-09-01', '2026-09-02', 6, 60))
        base = P.day_epoch('2026-09-01')
        for day, k, t0, t1 in w[:6]:
            self.assertEqual(t1 - t0, 60)
            self.assertTrue(base + k * 14400 <= t0 and t1 <= base + (k + 1) * 14400)


def _w(v):
    return '%064x' % v


def _log(block, idx, tx, topic0, topics, words):
    return {'blockNumber': hex(block), 'logIndex': hex(idx), 'transactionHash': tx,
            'topics': [topic0] + topics, 'data': '0x' + ''.join(_w(x) for x in words)}


def _t(addr):
    return '0x' + '0' * 24 + addr[2:]


class Decoder(unittest.TestCase):
    def test_a_buy_match_from_the_chain(self):
        # tx 0x556d2b6f... (block ~95,505,000): three makers buy NO, the requester buys YES and pays the fee
        ex, req = P.PM_EXCHANGE_V3, '0x662ae1662139394746b11b80d48414585560150e'
        m1, m2 = '0x893575c7d99542163c6b6e8a0fe5af0b6d217daa', '0x4ff8c8e5b1ba319fae0e2a36c061f1e43792ee54'
        yes, no = 0x0341, 0x0342
        oh = '0x' + '11' * 32
        logs = [
            _log(9, 1, '0xaa', P.TOPIC_ORDER_FILLED, [oh, _t(m1), _t(req)], [0, no, 299475225, 524475000, 0, 0, 0]),
            _log(9, 2, '0xaa', P.TOPIC_ORDER_FILLED, [oh, _t(m2), _t(req)], [0, no, 500000, 883821, 0, 0, 0]),
            _log(9, 3, '0xaa', P.TOPIC_FEE_CHARGED, [_t('0x115f48dc2a731aa16251c6d6e1befc42f92accc9')], [6564220]),
            _log(9, 4, '0xaa', P.TOPIC_ORDER_FILLED, [oh, _t(req), _t(ex)], [0, yes, 229999590, 535883204, 6564220, 0, 0]),
            _log(9, 5, '0xaa', P.TOPIC_ORDERS_MATCHED, [oh, _t(req)], [0, yes, 229999590, 535883204]),
        ]
        out = P.decode_matches(logs)
        self.assertEqual(len(out), 1)
        m = out[0]
        self.assertEqual(m['requester'], req)
        self.assertEqual(m['side'], 'BUY')
        self.assertAlmostEqual(m['usd'], 229.99959)
        self.assertAlmostEqual(m['shares'], 535.883204)
        self.assertAlmostEqual(m['price'], 229.99959 / 535.883204)
        self.assertAlmostEqual(m['fee'], 6.56422)
        self.assertEqual([f['maker'] for f in m['makers']], [m1, m2])

    def test_a_sell_match_and_two_matches_in_one_transaction(self):
        ex, req, mk = P.PM_EXCHANGE_V3, '0xeb5c5416bda924dcc88426525e82403e65acb6a3', '0x02d172a9edde24cc2206e81ec61c0c6a46cfcdae'
        oh = '0x' + '22' * 32
        logs = [
            _log(5, 1, '0xbb', P.TOPIC_ORDER_FILLED, [oh, _t(mk), _t(req)], [0, 7, 25948335, 61635000, 0, 0, 0]),
            _log(5, 2, '0xbb', P.TOPIC_ORDER_FILLED, [oh, _t(req), _t(ex)], [1, 7, 74643449, 27652442, 870410, 0, 0]),
            _log(5, 3, '0xbb', P.TOPIC_ORDER_FILLED, [oh, _t(mk), _t(req)], [0, 9, 1000000, 2000000, 0, 0, 0]),
            _log(5, 4, '0xbb', P.TOPIC_ORDER_FILLED, [oh, _t(req), _t(ex)], [0, 8, 1000000, 2000000, 25000, 0, 0]),
        ]
        out = P.decode_matches(logs)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]['side'], 'SELL')
        self.assertAlmostEqual(out[0]['usd'], 27.652442)
        self.assertAlmostEqual(out[0]['shares'], 74.643449)
        self.assertEqual(len(out[0]['makers']), 1)
        self.assertEqual(len(out[1]['makers']), 1)      # the second match only gets its own maker fill
        self.assertAlmostEqual(out[1]['price'], 0.5)


class PayoutZ(unittest.TestCase):
    def test_lottery_short_without_a_payout_is_not_significant(self):
        # 200 combos at fair 0.001 sold at 0.002 x 1,000 contracts, none paid: +$2 each, $400 in all
        fills = [('c%d' % i, -1000.0, 2.0, 0.001) for i in range(200)]
        z = P.payout_z(fills)
        self.assertAlmostEqual(z['pnl_usd'], 400.0)
        self.assertAlmostEqual(z['expected_payouts'], 0.2)
        # sd = sqrt(200 x 0.000999 x 1e6) = 447: one payout away from a loss
        self.assertAlmostEqual(z['payout_sd_usd'], math.sqrt(200 * 0.001 * 0.999 * 1e6))
        self.assertTrue(z['z'] < 1.0)

    def test_trades_on_one_combo_are_one_bet(self):
        z1 = P.payout_z([('a', -50.0, 1.0, 0.5), ('a', -50.0, 1.0, 0.5)])
        z2 = P.payout_z([('a', -50.0, 1.0, 0.5), ('b', -50.0, 1.0, 0.5)])
        self.assertAlmostEqual(z1['payout_sd_usd'], 50.0)            # 0.5 x 0.5 x 100^2
        self.assertAlmostEqual(z2['payout_sd_usd'], math.sqrt(2) * 25.0)
        self.assertEqual(z1['combos'], 1)
        # a maker who sold then bought back the same combo has no exposure left
        self.assertEqual(P.payout_z([('a', -50.0, 1.0, 0.5), ('a', 50.0, -0.5, 0.5)])['payout_sd_usd'], 0.0)


class Protocol(unittest.TestCase):
    def _row(self, day, price, settle, fair=0.1, side='yes', cnt=100.0, tk='KXMVECROSSCATEGORY0-S-X'):
        pnl, cap = P.maker_pnl(price, cnt, side, settle, 0.0)
        return {'day': day, 'price': price, 'settle': settle, 'fair': fair, 'taker_side': side, 'contracts': cnt,
                'ticker': tk, 'ts': P.parse_ts(day + 'T12:00:00Z'), 'pnl': pnl, 'cap': cap}

    def test_daily_series_at_print_and_at_own_quote(self):
        rows = [self._row('2026-09-01', 0.12, 0.0), self._row('2026-09-01', 0.12, 1.0), self._row('2026-09-03', 0.2, 0.0)]
        days = ['2026-09-01', '2026-09-02', '2026-09-03']
        ser, pnl_d, cap_d = P.daily_series(rows, days, lambda x: True)
        # day 1: +12 and -88 on capital 88 + 88
        self.assertAlmostEqual(ser[0], (12.0 - 88.0) / 176.0)
        self.assertEqual(ser[1], 0.0)
        self.assertAlmostEqual(ser[2], 20.0 / 80.0)
        # own quote at fair 0.1 x 1.05 = 0.105: wins all three (prints are above), fills at 0.105
        ser2, pnl2, _ = P.daily_series(rows, days, lambda x: True, price_fn=lambda x: P.own_quote_fill(x['price'], x['fair'], 0.05))
        self.assertAlmostEqual(pnl2['2026-09-01'], 10.5 - 89.5)
        self.assertAlmostEqual(pnl2['2026-09-03'], 10.5)

    def test_maker_fee_is_recharged_at_the_fill_price(self):
        r = self._row('2026-09-01', 0.5, 0.0, fair=0.4, tk='KXMVECROSSCATEGORY-S-X')
        _, pnl_d, _ = P.daily_series([r], ['2026-09-01'], lambda x: True)
        self.assertAlmostEqual(pnl_d['2026-09-01'], 50.0 - 0.88)

    def test_cluster_t(self):
        # five clusters with means 1.00..1.04: the clustered t is the mean over the between-cluster spread
        rows = [{'k': i % 5, 'v': 1.0 + 0.01 * (i % 5), 'w': 1.0} for i in range(30)]
        t, n = P.cluster_t(rows, lambda x: x['k'], lambda x: x['v'], lambda x: x['w'])
        self.assertEqual(n, 5)
        self.assertTrue(t > 50)
        # zero between-cluster variance leaves t undefined rather than infinite
        rows = [{'k': i % 5, 'v': 1.0 + 0.01 * (i % 3), 'w': 1.0} for i in range(30)]
        self.assertIsNone(P.cluster_t(rows, lambda x: x['k'], lambda x: x['v'], lambda x: x['w'])[0])
        # clusters at +1, -2, +3, -4 (ten rows each): mean -0.5, between-cluster spread large -> |t| < 1
        rows = [{'k': i % 4, 'v': (-1.0) ** i * (1 + i % 4), 'w': 1.0} for i in range(40)]
        t, _ = P.cluster_t(rows, lambda x: x['k'], lambda x: x['v'], lambda x: x['w'])
        self.assertTrue(-1.0 < t < 0.0)


if __name__ == '__main__':
    unittest.main()
