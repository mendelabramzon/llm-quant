#!/usr/bin/env python3
"""Tests for the economics harness and the label registry's provenance rules.

The arithmetic in `economics.py` decides whether an opportunity is reported as real, so its failure mode is silent: a
wrong break-even or a mis-scaled edge produces a plausible number that nobody re-derives. These tests pin the cases that
have actually gone wrong — a flat reward priced as if it scaled with size, a break-even search that assumed net grows
monotonically with size, and a race that pays gas only on its wins.

    uv run --with pycryptodome python scripts/test_economics.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import economics as E
import labels as L


class TestLeg(unittest.TestCase):
    def test_no_depth_means_no_impact(self):
        self.assertEqual(E.Leg('redeem at NAV').impact_bps(1e9), 0.0)

    def test_constant_product_impact_grows_with_size(self):
        leg = E.Leg('swap', depth_usd=1e6)
        small, big = leg.impact_bps(1e3), leg.impact_bps(1e5)
        self.assertLess(small, big)
        self.assertAlmostEqual(small, 1e4 * (1e-3 / 1.001), places=3)

    def test_amplification_flattens_a_stable_pool(self):
        plain = E.Leg('curve', depth_usd=6e5)
        amped = E.Leg('curve', depth_usd=6e5, amplification=100)
        self.assertLess(amped.impact_bps(1e5), plain.impact_bps(1e5) / 50)

    def test_custom_curve_overrides_depth(self):
        leg = E.Leg('x', depth_usd=1e6, impact_curve=lambda s: 42.0)
        self.assertEqual(leg.impact_bps(123), 42.0)


class TestNet(unittest.TestCase):
    def test_flat_edge_does_not_scale_with_size(self):
        """A reward harvest nets the same whatever notional the flash loan carries."""
        opp = E.Opportunity(name='harvest', edge_usd=7.6, gas_units=0)
        a = E.net_at(opp, 1e3, 0.06, 2500)[0]
        b = E.net_at(opp, 1e6, 0.06, 2500)[0]
        self.assertAlmostEqual(a, b)
        self.assertAlmostEqual(a, 7.6)

    def test_bps_edge_scales_with_size(self):
        opp = E.Opportunity(name='spread', edge_bps=100, gas_units=0)
        self.assertAlmostEqual(E.net_at(opp, 1e6, 0.06, 2500)[0], 1e4)

    def test_edges_add(self):
        opp = E.Opportunity(name='both', edge_bps=100, edge_usd=50, gas_units=0)
        self.assertAlmostEqual(E.net_at(opp, 1e6, 0.06, 2500)[0], 1e4 + 50)

    def test_gas_is_subtracted_at_the_quoted_base_fee(self):
        opp = E.Opportunity(name='g', edge_usd=0, gas_units=1_000_000)
        net = E.net_at(opp, 1.0, 1.0, 2500)[0]
        self.assertAlmostEqual(net, -1_000_000 * 1e-9 * 2500)


class TestBreakEven(unittest.TestCase):
    def test_break_even_is_found_below_the_optimum(self):
        """Impact makes net non-monotonic; searching up to capacity reported "never profitable" for real strategies."""
        opp = E.Opportunity(name='thin', edge_bps=35, gas_units=450_000,
                            legs=[E.Leg('buy', depth_usd=6e5, capacity_usd=6e5)])
        be = E.break_even_size(opp, 0.06, 2490)
        self.assertIsNotNone(be)
        self.assertGreater(E.net_at(opp, be * 1.05, 0.06, 2490)[0], 0)

    def test_no_profitable_size_returns_none(self):
        opp = E.Opportunity(name='hopeless', edge_bps=1, gas_units=50_000_000,
                            legs=[E.Leg('buy', depth_usd=1e4, capacity_usd=1e4)])
        self.assertIsNone(E.break_even_size(opp, 50.0, 2500))

    def test_optimum_is_interior_when_a_leg_has_depth(self):
        opp = E.Opportunity(name='interior', edge_bps=100, gas_units=0,
                            legs=[E.Leg('buy', depth_usd=1e6, capacity_usd=1e8)])
        best, _ = E.optimal_size(opp, 0.06, 2500)
        self.assertLess(best, 1e8)
        self.assertGreater(best, 0)


class TestScore(unittest.TestCase):
    def test_dust_is_rejected_however_good_the_apr_looks(self):
        """The StacyVault farm: mechanically live, $7.42 a run, and not worth running."""
        opp = E.Opportunity(name='dust', edge_usd=7.6, gas_units=1_200_000, capital_locked_usd=1000.0,
                            runs_per_day=24, race=True, competitors=1)
        v = E.score(opp, gas_gwei=0.06, eth_usd=2490, min_net_usd=50.0)
        self.assertFalse(v.go)
        self.assertIn('dust', v.reason)

    def test_a_race_pays_gas_on_losing_attempts(self):
        """Two identical strategies, one contended: the race must annualise worse than the held position."""
        kw = dict(edge_usd=100.0, gas_units=1_000_000, capital_locked_usd=1e4, runs_per_day=10, competitors=3)
        race = E.score(E.Opportunity(name='race', race=True, **kw), gas_gwei=5.0, eth_usd=2500, min_net_usd=0)
        held = E.score(E.Opportunity(name='held', race=False, **kw), gas_gwei=5.0, eth_usd=2500, min_net_usd=0)
        self.assertLess(race.annual_net_usd, held.annual_net_usd)

    def test_locked_capital_caps_the_run_count(self):
        opp = E.Opportunity(name='locked', edge_bps=50, gas_units=0, capital_days=7, runs_per_day=100)
        v = E.score(opp, size_usd=1e5, gas_gwei=0.06, eth_usd=2500, min_net_usd=0)
        self.assertLessEqual(v.effective_runs_per_year, 365 / 7 + 1e-6)

    def test_capacity_caps_the_traded_size(self):
        opp = E.Opportunity(name='capped', edge_bps=100, gas_units=0,
                            legs=[E.Leg('a', capacity_usd=1e4), E.Leg('b', capacity_usd=5e3)])
        v = E.score(opp, size_usd=1e9, gas_gwei=0.06, eth_usd=2500, min_net_usd=0)
        self.assertEqual(v.size_usd, 5e3)

    def test_flat_edge_reports_that_size_does_not_matter(self):
        v = E.score(E.Opportunity(name='flat', edge_usd=1000.0, gas_units=0), gas_gwei=0.06, eth_usd=2500)
        self.assertFalse(v.size_matters)

    def test_known_opportunities_all_score(self):
        for v in E.rank(E.known_opportunities(), gas_gwei=0.06, eth_usd=2490):
            self.assertIsInstance(v.net_apr, float)
            self.assertTrue(v.reason)


class TestLabelProvenance(unittest.TestCase):
    def test_tiers_are_ordered_strongest_first(self):
        self.assertLess(L.tier_rank('known-canonical'), L.tier_rank('model-memory'))
        self.assertLess(L.tier_rank('blockscout-verified'), L.tier_rank('behaviour-2026-09-07'))

    def test_unknown_source_falls_to_the_weakest_tier(self):
        self.assertEqual(L.tier_of('something-made-up'), 'behaviour')

    def test_a_weaker_source_never_overwrites_a_stronger_one(self):
        reg = {'labels': {'0xa': {'label': 'canonical', 'kind': 'venue', 'source': 'known-canonical'}}}
        self.assertFalse(L.put(reg, '0xA', 'guess', 'exchange', 'behaviour-2026-09-07'))
        self.assertEqual(reg['labels']['0xa']['label'], 'canonical')

    def test_a_stronger_source_upgrades(self):
        reg = {'labels': {'0xb': {'label': 'guess', 'kind': 'exchange', 'source': 'behaviour-2026-09-07'}}}
        self.assertTrue(L.put(reg, '0xb', 'GPv2Settlement', 'venue', 'blockscout-verified'))
        self.assertEqual(reg['labels']['0xb']['kind'], 'venue')

    def test_name_rules_beat_the_token_symbol_shortcut(self):
        """A Uniswap v2 pair exposes an ERC-20 symbol but is a venue, not a token."""
        self.assertEqual(L.infer_kind('UniswapV2Pair', token_symbol='UNI-V2'), 'venue')
        self.assertEqual(L.infer_kind('PlasmaVault', token_symbol='PV'), 'vault')
        self.assertEqual(L.infer_kind('AToken', token_symbol='aUSDC'), 'token')

    def test_a_psm_wrapper_is_not_a_token_just_because_its_name_contains_usd(self):
        self.assertEqual(L.infer_kind('UsdsPsmWrapper'), 'protocol')

    def test_registry_on_disk_is_valid(self):
        for a, v in L.load_registry()['labels'].items():
            self.assertEqual(a, a.lower(), a)
            self.assertIn(v.get('kind'), L.KINDS, a)
            self.assertTrue(v.get('source'), a)


if __name__ == '__main__':
    unittest.main(verbosity=1)
