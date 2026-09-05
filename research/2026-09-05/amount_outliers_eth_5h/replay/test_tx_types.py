"""Regression cases for errors that materially change the amount-outlier interpretation."""
import copy
from decimal import Decimal
import unittest

import tx_types as T
from signatures import family
from analyze_onchain import topic


class Prices:
    def get(self, key, ts=None):
        return Decimal(1)


def row(legs):
    return {'t': 0, 'from': 'alice', 'to': 'bob', 'legs': legs, 'flash_emitters': []}


def leg(a, b, raw, index):
    return {'li': index, 'k': 'erc20', 'a': 'token', 's': 'USD', 'key': 'USD', 'f': a, 'r': b, 'raw': raw}


class InterpretationTests(unittest.TestCase):
    def test_round_trip_requires_lender_event(self):
        r = row([leg('lender', 'bob', 2000, 0), leg('bob', 'lender', 2001, 1)])
        T.value_legs(r, Prices(), lambda _: 0)
        self.assertEqual(r['flash_usd'], '0.00')
        r['flash_emitters'] = ['lender']
        T.value_legs(r, Prices(), lambda _: 0)
        self.assertEqual(r['flash_usd'], '2000.00')
        self.assertEqual(r['pc'], '1.00')

    def test_zero_address_is_not_an_economic_holder(self):
        r = row([leg(T.ZERO, 'alice', 12000, 0), leg('alice', T.ZERO, 11000, 1)])
        T.value_legs(r, Prices(), lambda _: 0)
        self.assertEqual(r['pc'], '1000.00')
        self.assertTrue(all(n[0] != T.ZERO for n in r['net']))

    def test_shared_router_does_not_imply_shared_actor(self):
        rows = [{'from': f'user{i}', 'to': 'router', 'i': i, 'h': str(i), 'sd': [('pool', d)]} for i, d in enumerate([1, 1, -1])]
        T.sandwiches(rows)
        self.assertTrue(all('sw' not in r for r in rows))
        rows[2]['from'] = rows[0]['from']
        T.sandwiches(rows)
        self.assertEqual(rows[1]['sw'][0]['role'], 'victim')

    def test_aave_shape_is_not_overwritten_by_fork_alias(self):
        self.assertEqual(family({'topics': [topic('Supply(address,address,address,uint256,uint16)')]}), 'AaveSupply')

    def test_v4_pools_on_same_manager_are_not_one_pool(self):
        p = T.swap_identity('manager', {'family': 'V4Swap', 'pool_id': 'pool_a'})
        q = T.swap_identity('manager', {'family': 'V4Swap', 'pool_id': 'pool_b'})
        rows = [{'from': sender, 'i': i, 'h': str(i), 'sd': [(pool, d)]}
                for i, (sender, pool, d) in enumerate([('actor', p, 1), ('user', q, 1), ('actor', p, -1)])]
        T.sandwiches(rows)
        self.assertTrue(all('sw' not in r for r in rows))
        rows[1]['sd'] = [(p, 1)]
        T.sandwiches(rows)
        self.assertEqual(rows[1]['sw'][0]['role'], 'victim')

    def test_vault_price_uses_whole_share(self):
        self.assertEqual(int(T.ONE, 16), 10 ** 18)

    def test_many_transfers_are_not_truncated_before_netting(self):
        legs = [dict(leg('a', 'b', i, i), usd=Decimal(i)) for i in range(200)]
        self.assertEqual(len(T.compact_legs(legs)), 200)


if __name__ == '__main__':
    unittest.main()
