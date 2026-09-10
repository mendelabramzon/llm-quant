import unittest
from types import SimpleNamespace
from unittest.mock import patch
from detectors import nav_discount as n


class RedemptionGateTests(unittest.TestCase):
    def test_conditional_exit_does_not_enter_book_as_go(self):
        ctx=SimpleNamespace(analysis={'window':{'hours':5},'price_basis':{'ETH':2500},
            'peg':{'rETH':{'volume_usd':1e6,'vw_price':2970,'p10':2969,'p90':2971,'n':100}}})
        with patch.object(n,'_head',return_value={'rates':{'RETH':{'rate':1.2,'underlying':'ETH'}}}), \
             patch.object(n,'_gas',return_value=.3):
            h=n.scan(ctx)[0]
        self.assertGreater(h.economics['conditional_model_net_per_year_usd'],0)
        self.assertFalse(h.economics['go'])
        self.assertIsNone(h.economics['net_apr'])
        self.assertEqual(h.economics['net_per_year_usd'],0)
        self.assertEqual(h.economics['capacity_usd'],0)
        from detectors.run import digest
        self.assertIn('unquoted',digest([h],[],'.'))
