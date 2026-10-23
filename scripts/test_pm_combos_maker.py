#!/usr/bin/env python3
"""pm_combos_maker: the money-deciding arithmetic on known answers (buyer terms of an incumbent position, leg prices at
entry, fair value with and without a same-game lift, the win rule, P&L, capital, the payout z, the capital grid)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pm_combos_maker as M  # noqa: E402
import pm_parlays as P  # noqa: E402


def pos(no_price, cost, payout, outcome_index=1):
    return {'outcome_index': outcome_index, 'entry_avg_price_usdc': no_price, 'gross_entry_cost_usdc': cost,
            'realized_payout_usdc': payout}


class BuyerTerms(unittest.TestCase):
    def test_maker_no_is_buyer_yes(self):
        # first record of 0x1109da04: NO at 0.877, $886.68, paid $1011.04 -> the buyer's YES at 0.123 lost
        yes, c, y = M.position_terms(pos(0.877, 886.680055, 1011.03769))
        self.assertAlmostEqual(yes, 0.123)
        self.assertAlmostEqual(c, 886.680055 / 0.877)
        self.assertAlmostEqual(y, 0.0, places=6)
        # NO lost: the buyer's YES paid 1
        yes, c, y = M.position_terms(pos(0.48, 76.768137, 0.0))
        self.assertAlmostEqual(yes, 0.52)
        self.assertAlmostEqual(y, 1.0)

    def test_partial_pays_the_leg_product(self):
        # RESOLVED_PARTIAL: one void leg (0.5) and the rest won -> NO pays 0.5, YES pays 0.5
        yes, c, y = M.position_terms(pos(0.437, 24.30726, 27.81151))
        self.assertAlmostEqual(y, 0.5, places=4)
        # two void legs -> YES pays 0.25
        yes, c, y = M.position_terms(pos(0.594, 1420.854804, 1794.00859))
        self.assertAlmostEqual(y, 0.25, places=4)
        self.assertAlmostEqual(M.leg_value('RESOLVED_PARTIAL') * M.leg_value('RESOLVED_PARTIAL') * M.leg_value('RESOLVED_WIN'), 0.25)

    def test_yes_side_and_bad_records_are_not_buyer_terms(self):
        self.assertIsNone(M.position_terms(pos(0.3, 10.0, 0.0, outcome_index=0)))
        self.assertIsNone(M.position_terms(pos(0.0, 10.0, 0.0)))
        self.assertIsNone(M.position_terms(pos(0.5, 10.0, None)))
        self.assertIsNone(M.position_terms(pos(0.5, 10.0, 25.0)))      # pays more than one per contract


class LegPrices(unittest.TestCase):
    def test_last_point_within_30_minutes(self):
        s = [[1000, 0.40], [1060, 0.42], [1120, 0.45]]
        self.assertEqual(M.leg_price_at(s, 1100), (0.42, 40))
        self.assertEqual(M.leg_price_at(s, 1120), (0.45, 0))           # a point at the entry second counts
        self.assertEqual(M.leg_price_at(s, 1120 + 1800), (0.45, 1800))
        self.assertIsNone(M.leg_price_at(s, 1120 + 1801))              # stale -> unpriced
        self.assertIsNone(M.leg_price_at(s, 999))                      # nothing before entry
        self.assertIsNone(M.leg_price_at([[1000, 1.0]], 1000))         # a decided leg is not a price
        self.assertIsNone(M.leg_price_at([], 1000))


class FairValue(unittest.TestCase):
    def test_cross_game_is_the_product(self):
        self.assertAlmostEqual(M.combo_fair([(None, [0.5]), (None, [0.6]), (None, [0.7])]), 0.21)
        self.assertIsNone(M.combo_fair([(None, [0.5]), (None, [None])]))
        self.assertIsNone(M.combo_fair([(None, [0.5]), (None, [1.0])]))

    def test_same_game_lift_and_frechet_clamp(self):
        g = [('ml:hi+spread:hi', [0.6, 0.5]), (None, [0.5])]
        self.assertIsNone(M.combo_fair(g))                              # no lift -> unpriced, never the naive product
        self.assertAlmostEqual(M.combo_fair(g, {'ml:hi+spread:hi': 1.5}), 0.6 * 0.5 * 1.5 * 0.5)
        # a lift that would push the joint above the smaller leg is clamped to it (spread implies moneyline)
        self.assertAlmostEqual(M.combo_fair(g, {'ml:hi+spread:hi': 3.0}), 0.5 * 0.5)
        # and below the lower Frechet bound max(0, 0.9 + 0.8 - 1) = 0.7
        self.assertAlmostEqual(M.combo_fair([('a+b', [0.9, 0.8])], {'a+b': 0.1}), 0.7)
        self.assertAlmostEqual(M.combo_fair([('x', [0.6, 0.5])], {}, default_lift=1.0), 0.3)

    def test_structure_and_buckets(self):
        self.assertEqual(M.structure(['a', 'b', 'c']), 'cross')
        self.assertEqual(M.structure(['a', 'a', 'c']), 'same')
        self.assertIsNone(M.structure(['a', None]))
        self.assertEqual([M.legs_bucket(n) for n in (1, 2, 3, 4, 6, 7, 32)], [None, '2-3', '2-3', '4-6', '4-6', '7+', '7+'])

    def test_signature_sides(self):
        legs = [{'ctype': M.coarse_type('moneyline'), 'side': M.leg_side('ml', 'Lakers', 0.62)},
                {'ctype': M.coarse_type('totals'), 'side': M.leg_side('total', 'Under', 0.5)}]
        self.assertEqual(M.group_signature(legs), 'ml:hi+total:under')
        self.assertEqual(M.coarse_type('tennis_set_handicap'), 'spread')
        self.assertEqual(M.coarse_type('tennis_match_totals'), 'total')


class WinRuleAndMoney(unittest.TestCase):
    def test_undercut_strictly_and_round_up(self):
        self.assertAlmostEqual(M.quote_fill(0.25, 0.2, 0.10), 0.22)
        self.assertAlmostEqual(M.quote_fill(0.25, 0.20001, 0.0), 0.201)  # rounded up to the 0.001 tick
        self.assertIsNone(M.quote_fill(0.22, 0.2, 0.10))                 # a tie goes to the incumbent
        self.assertIsNone(M.quote_fill(0.21, 0.2, 0.10))                 # above the incumbent: lost
        self.assertIsNone(M.quote_fill(0.95, 0.90, 0.02))                # above the 0.90909 BUY safety threshold
        self.assertIsNone(M.quote_fill(0.25, None, 0.0))

    def test_pnl_capital_and_notional_sizing(self):
        # the incumbent sold 100 YES at 0.25 ($25 notional); our 0.20 quote fills 125 contracts for the same $25
        cq = M.fill_contracts(0.25, 100.0, 0.20)
        self.assertAlmostEqual(cq, 125.0)
        self.assertAlmostEqual(M.quoter_pnl(0.20, 0.0, cq), 25.0)        # combo failed: keep the premium
        self.assertAlmostEqual(M.quoter_pnl(0.20, 1.0, cq), -100.0)      # combo paid: lose 1 - q per contract
        self.assertAlmostEqual(M.quoter_pnl(0.20, 0.5, cq), -37.5)       # partial
        self.assertAlmostEqual(M.quoter_capital(0.20, cq), 100.0)        # worst loss = collateral
        self.assertAlmostEqual(-M.quoter_pnl(0.20, 1.0, cq), M.quoter_capital(0.20, cq))


class Fills(unittest.TestCase):
    def test_fills_for_win_rule_sizing_and_cap(self):
        rows = [{'struct': 'cross', 'lb': '2-3', 'yes': 0.25, 'c': 100000.0, 'fair': 0.2, 'y': 0.0},   # $25k ticket
                {'struct': 'cross', 'lb': '2-3', 'yes': 0.20, 'c': 100.0, 'fair': 0.2, 'y': 1.0},      # q = 0.2 ties: lost
                {'struct': 'same', 'lb': '2-3', 'yes': 0.50, 'c': 100.0, 'fair': 0.2, 'y': 1.0}]       # other cell
        sel = lambda x: x['struct'] == 'cross'  # noqa: E731
        full = M.fills_for(rows, sel, 0.0)
        self.assertEqual(len(full), 1)
        x, q, pnl, cap, cq = full[0]
        self.assertAlmostEqual(q, 0.2)
        self.assertAlmostEqual(cq, 125000.0)                 # $25k notional at 0.2
        self.assertAlmostEqual(pnl, 25000.0)
        self.assertAlmostEqual(cap, 100000.0)
        x, q, pnl, cap, cq = M.fills_for(rows, sel, 0.0, size_cap=1000.0)[0]
        self.assertAlmostEqual(cq, 5000.0)                   # $1,000 of notional at 0.2
        self.assertAlmostEqual(pnl, 1000.0)
        self.assertAlmostEqual(cap, 4000.0)


class PayoutZ(unittest.TestCase):
    def test_unit_weights_match_pm_parlays(self):
        f = [('a', 1.0, 10.0, 2.0, 0.1), ('b', 1.0, 5.0, -4.5, 0.1), ('c', 1.0, 20.0, 4.0, 0.2)]
        mine = M.weighted_payout_z(f)
        ref = P.payout_z([('a', -10.0, 2.0, 0.1), ('b', -5.0, -4.5, 0.1), ('c', -20.0, 4.0, 0.2)])
        self.assertAlmostEqual(mine['z'], ref['z'])
        sd = math.sqrt(0.09 * 100 + 0.09 * 25 + 0.16 * 400)
        self.assertAlmostEqual(mine['payout_sd_usd'], sd)
        self.assertAlmostEqual(mine['z'], 1.5 / sd)

    def test_weights_scale_pnl_and_sd_alike(self):
        # a sampled fill standing for w population fills scales P&L by w and its sd by w: z does not inflate
        f1 = [('a', 1.0, 10.0, 2.0, 0.1), ('b', 1.0, 5.0, 1.0, 0.3)]
        f20 = [(k, 20.0, c, p, pr) for k, _, c, p, pr in f1]
        self.assertAlmostEqual(M.weighted_payout_z(f1)['z'], M.weighted_payout_z(f20)['z'])
        self.assertAlmostEqual(M.weighted_payout_z(f20)['pnl_usd'], 60.0)

    def test_dollar_z_alone_passes_a_lottery_short(self):
        # why the gate is the count z: 1,000 one-in-a-thousand shots sold at 0.002 that never paid reach a dollar
        # payout z of 2.0 with one expected payout (pm_parlays needed an extra expected-payouts >= 20 gate)
        f = [(str(i), 1.0, 1.0, 0.002, 0.001) for i in range(1000)]
        z = M.weighted_payout_z(f)
        self.assertGreater(z['z'], 2.0)

    def test_count_z_blocks_the_lottery_short(self):
        cz = M.payout_count_z([(1.0, 0.002, 0.0)] * 1000)
        self.assertAlmostEqual(cz['expected_at_quote'], 2.0)
        self.assertAlmostEqual(cz['z'], 2.0 / math.sqrt(1000 * 0.002 * 0.998))
        self.assertLess(cz['z'], 2.0)

    def test_count_z_passes_a_real_edge_and_ignores_weights_scale(self):
        # 400 fills quoted at 0.30 that paid 25% of the time: (120 - 100) / sqrt(400 x 0.21) = 2.18
        f = [(1.0, 0.30, 1.0)] * 100 + [(1.0, 0.30, 0.0)] * 300
        cz = M.payout_count_z(f)
        self.assertAlmostEqual(cz['z'], 20.0 / math.sqrt(84.0))
        self.assertAlmostEqual(M.payout_count_z([(7.0, q, y) for _, q, y in f])['z'], cz['z'])
        # no edge: paid exactly at the quoted rate -> z = 0
        self.assertAlmostEqual(M.payout_count_z([(1.0, 0.25, 1.0)] * 1 + [(1.0, 0.25, 0.0)] * 3)['z'], 0.0)


class CapitalAndTail(unittest.TestCase):
    def test_outstanding_grid(self):
        g = M.outstanding([(0, 100, 5.0), (50, 150, 3.0)], 0, 200, 50)
        self.assertEqual(g, [(0, 5.0), (50, 8.0), (100, 3.0), (150, 0.0), (200, 0.0)])

    def test_ruin_buffer(self):
        pnl = [10.0] * 98 + [-50.0, -200.0]
        self.assertAlmostEqual(M.ruin_buffer(pnl, 0.01), 50.0)   # one day in 100 loses more than 50
        self.assertAlmostEqual(M.ruin_buffer([1.0, 2.0], 0.01), 0.0)


if __name__ == '__main__':
    unittest.main()
