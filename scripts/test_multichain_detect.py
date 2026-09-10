#!/usr/bin/env python3
"""The cross-chain switch detector's two rules, pinned on synthetic rows: capacity is a minimum, and go is a floor."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import multichain as M  # noqa: E402


def switch(asset, frm, to, opt, avail, apr_at_size, from_apr, to_apr, annual):
    movable = M.switch_capacity(opt, avail)
    return {'asset': asset, 'from': frm, 'to': to, 'unconstrained_size_usd': opt, 'from_available_usd': avail,
            'movable_usd': movable, 'apr_at_size': apr_at_size, 'from_apr': from_apr, 'to_apr': to_apr,
            'spread_pp': 100 * (to_apr - from_apr), 'annual_usd': annual,
            'binding': 'low-side withdrawable liquidity' if avail < opt else 'high-side rate dilution',
            'from_pool': '0xf', 'to_pool': '0xt', 'from_address': '0xa', 'to_address': '0xb',
            'from_supplied_usd': 1e7, 'to_supplied_usd': 1e8, 'from_utilisation': 0.8,
            'rate_source': {'from': 'window time-weighted', 'to': 'window time-weighted'}}


class CapacityRule(unittest.TestCase):
    def test_low_side_withdrawable_binds(self):
        self.assertEqual(M.switch_capacity(18_500_000, 2_300_000), 2_300_000)

    def test_high_side_optimum_binds(self):
        self.assertEqual(M.switch_capacity(15_800_000, 32_400_000), 15_800_000)

    def test_never_negative_or_none(self):
        self.assertEqual(M.switch_capacity(-5.0, 1e6), 0.0)
        self.assertEqual(M.switch_capacity(None, 1e6), 0.0)
        self.assertEqual(M.switch_capacity(1e6, None), 0.0)


class GoRule(unittest.TestCase):
    def test_floors(self):
        self.assertTrue(M.go_rule(300_000, 0.006))
        self.assertFalse(M.go_rule(200_000, 0.02))     # too small
        self.assertFalse(M.go_rule(5_000_000, 0.004))  # too thin
        self.assertFalse(M.go_rule(None, None))


class Hits(unittest.TestCase):
    def setUp(self):
        self.A = {
            'switches': [
                switch('USDC', 'arbitrum', 'base', 15_800_000, 32_400_000, 0.0318, 0.0267, 0.0400, 79_348),
                switch('USDC', 'optimism', 'base', 18_500_000, 2_300_000, 0.0330, 0.0256, 0.0400, 17_000),
                switch('USDC', 'scroll', 'base', 1_000_000, 65_000, 0.0390, 0.0036, 0.0400, 2_300),
            ],
            'switch_book': {'legs': [{'asset': 'USDC', 'from': 'arbitrum', 'to': 'base', 'size_usd': 15_800_000,
                                      'apr_at_size': 0.0318, 'from_apr': 0.0267, 'annual_usd': 79_348}],
                            'total_size_usd': 37_276_234.7, 'total_annual_usd': 177_793.5, 'sum_of_rows_annual_usd': 279_425.4},
            'surface': [{}] * 63, 'chains': {'base': {}, 'arbitrum': {}}, 'benchmark': {'apy': 0.036},
            'flow_vs_yield_spearman': {'rho': -0.57, 'n': 8},
        }

    def test_switch_hits_carry_capacity_and_go(self):
        hits = M.detect_hits(self.A)
        by = {h['key']: h for h in hits}
        self.assertEqual(set(by), {'USDC:arbitrum->base', 'USDC:optimism->base', 'USDC:scroll->base', 'book'})
        a = by['USDC:arbitrum->base']
        self.assertEqual(a['economics']['capacity_usd'], 15_800_000)
        self.assertAlmostEqual(a['economics']['net_apr'], 0.0318 - 0.0267)
        self.assertTrue(a['economics']['go'])
        self.assertEqual(a['severity'], 'notable')
        self.assertTrue(a['evidence']['capacity_matches_row'])
        o = by['USDC:optimism->base']
        self.assertEqual(o['economics']['capacity_usd'], 2_300_000)   # the low side's exit, not the curve's optimum
        self.assertEqual(o['economics']['binding'], 'low-side withdrawable liquidity')
        s = by['USDC:scroll->base']
        self.assertFalse(s['economics']['go'])                         # $65k is not a strategy
        self.assertEqual(s['severity'], 'info')

    def test_bridge_cost_is_charged_when_asked(self):
        hits = M.detect_hits(self.A, bridge_bps=10.0)
        a = next(h for h in hits if h['key'] == 'USDC:arbitrum->base')
        self.assertAlmostEqual(a['economics']['net_apr'], 0.0318 - 0.0267 - 0.001)

    def test_book_hit_is_blended(self):
        b = next(h for h in M.detect_hits(self.A) if h['key'] == 'book')
        self.assertAlmostEqual(b['economics']['net_apr'], 177_793.5 / 37_276_234.7)
        self.assertEqual(b['economics']['capacity_usd'], 37_276_234.7)
        self.assertEqual(b['evidence']['flow_vs_yield_spearman']['rho'], -0.57)
        self.assertEqual(b['evidence']['bindings'], {'high-side rate dilution': 1, 'low-side withdrawable liquidity': 2})
        self.assertFalse(b['economics']['go'])                        # 48bp blended is under the 50bp floor

    def test_window_bounds_span_the_chains(self):
        man = {'hours': 1.0, 'window': {'base': {'first_utc': '2026-09-08T06:29:53+00:00', 'last_utc': '2026-09-08T07:29:53+00:00'},
                                        'arbitrum': {'first_utc': '2026-09-08T06:28:25+00:00', 'last_utc': '2026-09-08T07:28:25+00:00'}}}
        w = M.window_bounds(man)
        self.assertEqual(w['first_utc'], '2026-09-08T06:28:25+00:00')
        self.assertEqual(w['last_utc'], '2026-09-08T07:29:53+00:00')
        self.assertEqual(w['chains'], ['arbitrum', 'base'])


if __name__ == '__main__':
    unittest.main()
