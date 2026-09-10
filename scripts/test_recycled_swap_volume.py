import unittest
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from detectors.recycled_swap_volume import closed_roundtrip, scan, SWAP, TRANSFER


class RecyclingTests(unittest.TestCase):
    def usd(self, token, amount):
        return amount * 2500 if token == 'WETH' else None

    def test_closed_roundtrip_is_turnover_without_new_demand(self):
        r = closed_roundtrip([[0, 1000, 100000, 0], [100000, 0, 0, 1000.00004]],
                             ['TOKEN', 'WETH'], self.usd)
        self.assertAlmostEqual(r['gross_priced_leg_usd'], 5000000.1)
        self.assertAlmostEqual(r['pool_net_priced_token_usd'], -.1)

    def test_directional_trade_and_material_inventory_change_are_not_recycling(self):
        self.assertIsNone(closed_roundtrip([[0, 1000, 100000, 0]], ['TOKEN', 'WETH'], self.usd))
        self.assertIsNone(closed_roundtrip([[0, 1000, 100000, 0], [100000, 0, 0, 900]],
                                          ['TOKEN', 'WETH'], self.usd))

    def test_unknown_prices_are_not_invented(self):
        self.assertIsNone(closed_roundtrip([[0, 1000, 100000, 0], [100000, 0, 0, 1000]],
                                          ['A', 'B'], self.usd))

    def test_swap_shaped_logs_require_matching_settlement(self):
        pool, token, weth, sender = ['0x' + c*40 for c in '1234']
        def data(*words):
            return '0x' + ''.join(hex(v)[2:].rjust(64, '0') for v in words)
        swaps = [{'transactionHash':'tx', 'address':pool, 'topics':[SWAP], 'data':data(*v)}
                 for v in ([0,1000,100000,0],[100000,0,0,1000])]
        transfers = [{'transactionHash':'tx', 'address':weth,
                      'topics':[TRANSFER, data(int(a,16)), data(int(b,16))], 'data':data(1000)}
                     for a,b in [(sender,pool),(pool,sender)]]
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out/'pools.json').write_text(json.dumps({pool:{'tokens':[token,weth]}}))
            for logs, expected in [(swaps,0),(swaps+transfers[:1],0),(swaps+transfers,1)]:
                window = SimpleNamespace(usd=lambda t, v: v*2500 if t == weth else None,
                                         blocks=lambda:iter([({'number':'0x1','transactions':[
                                             {'hash':'tx','from':sender}]},logs)]))
                self.assertEqual(len(scan(SimpleNamespace(out=out,window=window))), expected)


if __name__ == '__main__':
    unittest.main()
