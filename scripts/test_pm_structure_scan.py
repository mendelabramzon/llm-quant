"""Tests for pm_structure_scan: the template classifier, the ladder parser, the monotonicity trade and its fill,
the cost model and the dynamics signal. Every function here decides a label or a dollar."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_structure_scan as S  # noqa: E402
import polymarket_history as P  # noqa: E402


class Classify(unittest.TestCase):
    CASES = [
        ('Bitcoin Up or Down - April 28, 12:35AM-12:40AM ET', '', '', 'crypto_updown', 'updown'),
        ('Exact Score: Switzerland 2 - 3 Algeria?', 'Switzerland vs. Algeria - Exact Score', '', 'sports',
         'exact_score'),
        ('Will AS Roma vs. Atalanta BC end in a draw?', 'AS Roma vs. Atalanta BC', '', 'sports', 'sports_draw'),
        ('Counter-Strike: MOUZ vs Spirit - Map 1 Winner', 'Counter-Strike: MOUZ vs Spirit (BO3)', '', 'sports',
         'esports_map'),
        ('Spread: Utah (-13.5)', 'Arkansas vs. Utah', 'Spread -13.5', 'sports', 'sports_spread'),
        ('Indiana Fever vs. Las Vegas Aces: O/U 180.5', 'Indiana Fever vs. Las Vegas Aces', '', 'sports',
         'sports_total'),
        ('Luxembourg vs. Iceland: Both Teams to Score', 'Luxembourg vs. Iceland - More Markets', '', 'sports',
         'sports_prop'),
        ('Will Urawa Red Diamonds win on 2026-09-06?', 'Kashima Antlers vs. Urawa Red Diamonds', '', 'sports',
         'sports_match'),
        ('Will the Memphis Grizzlies win the 2025 NBA Finals?', 'NBA Champion', '', 'sports', 'futures_winner'),
        ('Will the highest temperature in Milan be 21°C on April 28?', '', '21°C', 'science_tech', 'weather_temp'),
        ('Will Elon Musk post 165-189 tweets from May 4 to May 6, 2026?', 'Elon Musk # tweets May 4 - May 6, 2026?',
         '165-189', 'politics', 'tweet_count'),
        ('Will Trump say "Insane Asylum" this week? (January 25)', 'What will Trump say this week (January 25)?', '',
         'politics', 'mention'),
        ("Will Trump's approval rating be between 45.5% and 45.9% on April 11?", '', '', 'politics', 'approval'),
        ('Kinetiq FDV above $250M one day after launch?', '', '$250M', 'crypto_price', 'fdv_launch'),
        ('Will the price of Bitcoin be between $86,000 and $88,000 on January 19?', '', '', 'crypto_price',
         'price_range'),
        ('Will Bitcoin dip to $78,000 on May 16?', 'What price will Bitcoin hit on May 16?', '↓ 78,000',
         'crypto_price', 'price_hit'),
        ('Will the price of Solana be above $190 on October 27?', 'Solana above ___ on October 27?', '190',
         'crypto_price', 'price_above'),
        ('Fed decreases interest rates by 50+ bps after June 2024 meeting?', '', '', 'politics', 'econ_release'),
        ("Will Domino's Pizza (DPZ) beat quarterly earnings?", '', '', 'economics', 'earnings'),
        ('Will Mikie Sherrill win by 3-6%?', 'New Jersey Governor Election Mikie Sherrill margin of victory', '',
         'elections', 'election_margin'),
        ('Will Lazarus Chakwera win the 2025 Malawi presidential election?', 'Malawi Presidential Election', '',
         'elections', 'election_winner'),
        ('SSI public model released by September 30, 2026?', 'SSI public model released by…?', 'September 30',
         'science_tech', 'release_by'),
        ('Will Google have the top AI model at the end of March 2026?', '', '', 'science_tech', 'ranking'),
        ('Will 125-149 ships transit the Strait of Hormuz between April 20-April 26?',
         'How many ships transit the Strait of Hormuz this week?', '125-149', 'politics', 'count_bucket'),
        ('Will Zelenskyy talk to Putin by August 31?', 'Will Zelenskyy talk to Putin by...?', 'August 31',
         'politics', 'drama_by_date'),
        ('Lisa Cook out as Fed Governor by September 30?', 'Lisa Cook out as Fed Governor by...?', '', 'politics',
         'drama_by_date'),
        ('Will Israel strike Lebanon on January 10, 2026?', 'Will Israel strike Lebanon on...?', 'January 10',
         'politics', 'drama_on_date'),
        ('US announces end of Iranian blockade by August 15, 2026?', '', '', 'politics', 'drama_by_date'),
    ]

    def test_cases(self):
        for q, et, g, cat, want in self.CASES:
            self.assertEqual(S.classify(q, et, g, cat), want, q)

    def test_every_template_is_listed(self):
        for _, _, _, _, want in self.CASES:
            self.assertIn(want, S.TEMPLATES)


class Ladders(unittest.TestCase):
    def m(self, q, g='', et='', outcomes=('Yes', 'No'), ev='E1', end='2026-06-30T00:00:00Z'):
        return {'question': q, 'groupItemTitle': g, 'event_title': et, 'event_id': ev, 'outcomes': list(outcomes),
                'endDate': end, 'id': q}

    def test_date_rung(self):
        a = S.ladder_rung(self.m('Will Anthropic IPO by June 30, 2026?', 'June 30, 2026', 'Will Anthropic IPO by...?'))
        b = S.ladder_rung(self.m('Will Anthropic IPO by July 31, 2026?', 'July 31, 2026', 'Will Anthropic IPO by...?'))
        self.assertEqual(a[0], 'date')
        self.assertEqual(a[1], b[1])            # same ladder key
        self.assertLess(a[2], b[2])             # June before July
        self.assertEqual(a[3], +1)              # P(by d) rises with d

    def test_strike_rung(self):
        a = S.ladder_rung(self.m('Will the price of Bitcoin be above $68,000 on April 24?', '68,000'))
        b = S.ladder_rung(self.m('Will the price of Bitcoin be above $70,000 on April 24?', '70,000'))
        self.assertEqual(a[0], 'strike')
        self.assertEqual(a[1], b[1])
        self.assertEqual((a[2], b[2]), (68000.0, 70000.0))
        self.assertEqual(a[3], -1)

    def test_touch_down_rises_with_strike(self):
        a = S.ladder_rung(self.m('Will Bitcoin dip to $60,000 on March 29?', '↓ 60,000'))
        self.assertEqual((a[0], a[3]), ('touch', +1))

    def test_total_and_spread(self):
        t = S.ladder_rung(self.m('Kings vs. Magic: O/U 228.5', 'O/U 228.5', outcomes=('Over', 'Under')))
        self.assertEqual((t[0], t[2], t[3], t[4]), ('total', 228.5, -1, 0))
        sp = S.ladder_rung(self.m('Spread: Pacers (-2.5)', 'Spread -2.5', outcomes=('Knicks', 'Pacers')))
        self.assertEqual((sp[0], sp[2], sp[3], sp[4]), ('spread', 2.5, -1, 1))   # Pacers are outcome 1

    def test_year_from_utc_end(self):
        # 'December 31' ending 2027-01-01 04:59Z is a 2026 deadline (pilot-snapshot bug)
        end = P.parse_ts('2027-01-01T04:59:00Z')
        self.assertEqual(S.parse_rung_date('December 31', end), 20261231)
        self.assertEqual(S.parse_rung_date('June 30, 2027', end), 20270630)
        a = S.ladder_rung(self.m('Iran leadership change by December 31?', 'December 31',
                                 'Iran leadership change by...?', end='2027-01-01T04:59:00Z'))
        b = S.ladder_rung(self.m('Iran leadership change by June 30, 2027?', 'June 30, 2027',
                                 'Iran leadership change by...?', end='2027-07-01T03:59:00Z'))
        self.assertLess(a[2], b[2])

    def test_year_after_opening_beats_bad_end_date(self):
        m = self.m('Iran x Israel/US conflict ends by December 31?', 'December 31', 'Iran x Israel/US conflict ends by...?',
                   end='2026-06-30T00:00:00Z')
        m['startDate'] = '2026-03-05T00:00:00Z'
        march = self.m('Iran x Israel/US conflict ends by March 31?', 'March 31', 'Iran x Israel/US conflict ends by...?',
                       end='2026-03-31T00:00:00Z')
        march['startDate'] = '2026-03-05T00:00:00Z'
        self.assertEqual(S.ladder_rung(m)[2], 20261231)
        self.assertLess(S.ladder_rung(march)[2], S.ladder_rung(m)[2])

    def test_spread_side_prefers_exact_team(self):
        self.assertEqual(S.spread_side('kansas', ['Kansas State', 'Kansas']), 1)
        self.assertEqual(S.spread_side('kansas state', ['Kansas State', 'Kansas']), 0)
        self.assertEqual(S.spread_side('1h spread: kansas state', ['Kansas', 'Kansas State']), 1)
        self.assertIsNone(S.spread_side('wildcats', ['Kansas State', 'Kansas']))

    def test_comparison_must_belong_to_rung(self):
        q = 'Will there be 0 earthquakes of 6.5 or above magnitude worldwide by February 15?'
        self.assertIsNone(S.ladder_rung(self.m(q, '0')))
        c = S.ladder_rung(self.m('Will Trump say "Border" 20 or more times during Michigan rally?', 'Border 20+ times'))
        self.assertEqual((c[0], c[2], c[3]), ('count', 20.0, -1))
        t = S.ladder_rung(self.m('Will a coin launched in 2026 end the year in the top 5?', 'Top 5'))
        self.assertEqual(t[3], +1)          # P(top N) rises with N
        h = S.ladder_rung(self.m('Will Gold (XAUUSD) hit (HIGH) $5,200 in April?', '↑ $5,200'))
        self.assertEqual((h[0], h[3]), ('touch', -1))

    def test_label_suffix_from_question(self):
        a = S.ladder_rung(self.m('Bitcoin above $126K on August 18?', '>126'))
        b = S.ladder_rung(self.m('Bitcoin above $116K on August 18?', '>116k'))
        self.assertEqual((a[2], b[2]), (126000.0, 116000.0))

    def test_reach_without_direction_is_not_a_ladder(self):
        self.assertIsNone(S.ladder_rung(self.m('Will Ethereum reach $2,250 in October?')))
        self.assertIsNotNone(S.ladder_rung(self.m('Will Ethereum reach $2,250 in October?', '↑ 2,250')))

    def test_buckets_are_not_ladders(self):
        self.assertIsNone(S.ladder_rung(self.m('Will the price of Bitcoin be between $93000 and $95000 on Feb 28?')))
        self.assertIsNone(S.ladder_rung(self.m('Will Elon Musk post 60-79 tweets from September 9 to 16?')))

    def test_parse_number(self):
        self.assertEqual(S.parse_number('$72,000'), 72000.0)
        self.assertEqual(S.parse_number('1.5B'), 1.5e9)
        self.assertEqual(S.parse_number('25+'), 25.0)
        self.assertEqual(S.parse_number('−1.5'), -1.5)

    def test_parse_rung_date(self):
        self.assertEqual(S.parse_rung_date('March 31, 2026', 2025), 20260331)
        self.assertEqual(S.parse_rung_date('June 30', 2026), 20260630)
        self.assertEqual(S.parse_rung_date('end of June', 2026), 20260631)

    def test_pairs_direction(self):
        # falling ladder (above k): the lower strike must be priced higher
        pr = S.ladder_pairs([(68000, -1, 'a'), (70000, -1, 'b')])
        self.assertEqual(pr, [('a', 'b')])
        # rising ladder (by d): the later date must be priced higher
        pr = S.ladder_pairs([(20260630, +1, 'jun'), (20260731, +1, 'jul')])
        self.assertEqual(pr, [('jul', 'jun')])
        # equal rungs (a duplicated listing) are not a pair
        self.assertEqual(S.ladder_pairs([(5, -1, 'x'), (5, -1, 'y')]), [])


class Fill(unittest.TestCase):
    def test_violation_fill_profit_and_fees(self):
        # must-be-higher member asks 0.40 for 100; must-be-lower member bids 0.45 for 50 (NO costs 0.55)
        hi = {'asks': [(0.40, 100.0)], 'bids': [(0.39, 10.0)]}
        lo = {'asks': [(0.46, 10.0)], 'bids': [(0.45, 50.0)]}
        f = S.violation_fill(hi, lo, 0.0, 0.0)
        self.assertAlmostEqual(f['sets'], 50.0)
        self.assertAlmostEqual(f['profit'], 50 * 0.05)
        g = S.violation_fill(hi, lo, 0.05, 0.05)
        fee = 0.05 * 0.40 * 0.60 + 0.05 * 0.55 * 0.45
        self.assertAlmostEqual(g['profit'], 50 * (0.05 - fee))
        # fees larger than the gap: nothing is bought
        h = S.violation_fill({'asks': [(0.40, 100.0)]}, {'bids': [(0.405, 100.0)]}, 0.05, 0.05)
        self.assertEqual(h['sets'], 0.0)

    def test_payoff_is_at_least_one(self):
        # YES(hi) + NO(lo) where hi must be >= lo: states (hi, lo) in {(1,1), (1,0), (0,0)} pay 1, 2, 1
        for pay_hi, pay_lo in ((1, 1), (1, 0), (0, 0)):
            self.assertGreaterEqual(pay_hi + 1 - pay_lo, 1)

    def test_mirror(self):
        b = {'asks': [(0.40, 5.0)], 'bids': [(0.38, 7.0)]}
        m = S.mirror(b)
        self.assertEqual(m['asks'], [(0.62, 7.0)])
        self.assertEqual(m['bids'], [(0.60, 5.0)])


class FillPrices(unittest.TestCase):
    def test_complement_trades_map_to_the_leg(self):
        tr = [{'asset': 'Y', 'side': 'BUY', 'price': '0.40'}, {'asset': 'N', 'side': 'SELL', 'price': '0.62'},
              {'asset': 'Y', 'side': 'SELL', 'price': '0.37'}, {'asset': 'N', 'side': 'BUY', 'price': '0.65'}]
        buy, sell = S.leg_fill_prices(tr, 'Y', 'N')
        self.assertEqual(sorted(round(x, 6) for x in buy), [0.38, 0.40])     # NO sold at 0.62 = YES bought at 0.38
        self.assertEqual(sorted(round(x, 6) for x in sell), [0.35, 0.37])    # NO bought at 0.65 = YES sold at 0.35


class Costs(unittest.TestCase):
    def test_entry_and_exit(self):
        self.assertAlmostEqual(S.entry_cost(0.50, 0.01, 0.05), 0.51 + 0.05 * 0.51 * 0.49)
        self.assertAlmostEqual(S.exit_value(0.50, 0.01, 0.05), 0.49 - 0.05 * 0.49 * 0.51)

    def test_bands(self):
        self.assertEqual(S.edge_band(0.07), S.edge_band(0.93))
        self.assertEqual(S.yes_band(0.05), '0.02-0.10')
        self.assertIsNone(S.yes_band(0.99))

    def test_half_spread_fallback(self):
        tab = {'mention|0.05-0.10': {'n': 5, 'median': 0.05},
               'politics|0.05-0.10': {'n': 40, 'median': 0.02},
               'all|0.05-0.10': {'n': 900, 'median': 0.01}}
        self.assertEqual(S.half_spread(tab, 'mention', 'politics', 0.93), 0.02)   # template too thin
        self.assertEqual(S.half_spread(tab, 'other', 'other', 0.07), 0.01)

    def test_template_trade_return(self):
        m = {'id': '1', 'event_id': 'e', 'cat': 'politics', 'tags': ['Politics'], 'outcomePrices': [0.0, 1.0],
             'closedTime': '2026-03-10T00:00:00Z', 'endDate': '2026-03-10T00:00:00Z',
             'startDate': '2026-01-01T00:00:00Z', 'volumeNum': 1e5}
        t0 = P.parse_ts('2026-03-09T00:00:00Z')
        fine = [[t0 - 3600, 0.20]]
        tr = S.template_trades(m, 'drama_by_date', 2.0, None, fine, {})
        one_day = [x for x in tr if x['h'] == '1d']
        no = [x for x in one_day if x['side'] == 1][0]
        yes = [x for x in one_day if x['side'] == 0][0]
        cost_no = 0.81 + 0.04 * 0.81 * 0.19        # NO mid 0.80 + default half-spread 0.01, politics fee 0.04
        self.assertAlmostEqual(no['ret'], 1.0 / cost_no - 1.0)
        self.assertAlmostEqual(yes['ret'], -1.0)
        self.assertEqual(no['band'], '0.10-0.25')


class Dynamics(unittest.TestCase):
    def test_signal_threshold(self):
        H = int(S.HOUR)
        grid = {0: 0.50, H: 0.52, 2 * H: 0.63, 3 * H: 0.60}
        self.assertEqual(S.dynamics_signals(grid, 1, 0.10), [(2 * H, 0.63 - 0.52)])
        self.assertEqual([t for t, _ in S.dynamics_signals(grid, 1, 0.02)], [H, 2 * H, 3 * H])

    def test_dyn_one_enters_next_hour_and_exits_at_bid(self):
        H = int(S.HOUR)
        grid = {0: 0.50, H: 0.62, 2 * H: 0.64, 8 * H: 0.70}
        r = S.dyn_one(grid, H, 0.12, 'mom', 6, 1.0, 100 * H, 100 * H, 'other', 'other', 0.0, {}, 1)
        self.assertEqual(r['entry_t'], 2 * H)                      # the next hour, not the signal hour
        self.assertAlmostEqual(r['ret'], (0.70 - 0.01) / (0.64 + 0.01) - 1.0)
        rev = S.dyn_one(grid, H, 0.12, 'rev', 'res', 1.0, 100 * H, 100 * H, 'other', 'other', 0.0, {}, 1)
        self.assertAlmostEqual(rev['ret'], 0.0 / (0.36 + 0.01) - 1.0)   # bought NO, YES won


class Weights(unittest.TestCase):
    def test_union_inclusion(self):
        pm, q = 0.2, 0.5
        self.assertAlmostEqual(1.0 / (1.0 - (1.0 - pm) * (1.0 - q)), 1.0 / 0.6)


if __name__ == '__main__':
    unittest.main()
