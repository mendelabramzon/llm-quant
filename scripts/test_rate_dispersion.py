"""A rate-switch quote cannot use more liquidity than can leave its source."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from detectors import rate_dispersion as r


class LiquidityTests(unittest.TestCase):
    def test_cash_caps_claims_and_pause_overrides_cash(self):
        row = {'supplied_usd':100, 'borrowed_usd':20, 'available_usd':7}
        self.assertEqual(r.available_liquidity(row)[0], 7)
        self.assertEqual(r.available_liquidity(dict(row, available_usd=200))[0], 100)
        self.assertEqual(r.available_liquidity(dict(row, withdraw_enabled=False))[0], 0)

    def test_old_snapshots_use_explicit_estimate_and_unknown_is_not_unlimited(self):
        cash,basis = r.available_liquidity({'supplied_usd':100, 'borrowed_usd':80})
        self.assertEqual(cash,20)
        self.assertIn('estimated',basis)
        self.assertEqual(r.available_liquidity({'supplied_usd':100})[0],0)

    def test_capped_search_tests_exact_boundary_even_below_grid_start(self):
        fn = lambda x:.05-.000000001*x
        _,best = r.sized(fn,.01,1e8,limit=17.25)
        self.assertEqual(best['size_usd'],17.25)
        self.assertEqual(r.sized(fn,.01,1e8,limit=0),(None,None))

    def scan(self,source_cash=2e6,flat=False):
        ctx=SimpleNamespace(prices={'ETH':2500},gas_quote=lambda:{'gwei':1})
        source={'supply_apr':.01,'supplied_usd':20e6,'borrowed_usd':18e6,
                'available_usd':source_cash,'withdraw_enabled':True}
        high={'supply_apr':.05,'supplied_usd':1e9,'borrowed_usd':5e8,'dilutes':not flat}
        with patch.object(r,'_head_state',return_value={'lending':{}}), \
             patch.object(r,'_venue_table',return_value={('high','USDC'):high,('low','USDC'):source}), \
             patch.object(r,'_log_medians',return_value={}):
            return r.scan(ctx)[0]

    def test_full_quote_scores_capped_size_not_destination_optimum(self):
        hit=self.scan()
        self.assertEqual(hit.economics['size_usd'],2e6)
        self.assertGreater(hit.evidence['unconstrained_best_size']['size_usd'],2e6)
        self.assertLess(hit.economics['net_per_year_usd'],80000)
        self.assertIn('source liquidity capped',hit.title)

    def test_fixed_rate_uses_source_cash_not_synthetic_billion(self):
        hit=self.scan(flat=True)
        self.assertEqual(hit.economics['size_usd'],2e6)
        self.assertAlmostEqual(hit.economics['net_per_year_usd'],79999,delta=1)

    def test_no_cash_produces_no_go_not_a_positive_quote(self):
        hit=self.scan(source_cash=0)
        self.assertFalse(hit.economics['go'])
        self.assertIsNone(hit.economics['net_apr'])
        from detectors.run import digest
        self.assertIn('net APR unquoted',digest([hit],[],'.'))


if __name__=='__main__':
    unittest.main()
