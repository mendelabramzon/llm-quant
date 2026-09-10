import argparse
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import live_scan
from verify import close


class EnrichmentTests(unittest.TestCase):
    def test_liquidity_reads_underlying_cash_and_honors_withdraw_pause(self):
        usdc = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
        row = {'aToken':'0x'+'1'*40,'config':(1<<56)|(1<<60)}
        comet = next(iter(live_scan.COMETS))
        hs = {'lending':{'Aave v3':{usdc:row}}, 'compound':{
            live_scan.COMETS[comet]:{'base_token':usdc}}}
        class FakeRPC:
            def eth_calls(self, items, block):
                self_block = block
                assert self_block == '0x123'
                vals = [7_000_000] if len(items)==1 else [11_000_000,1,0]
                return ['0x'+hex(x)[2:].rjust(64,'0') for x in vals]
        live_scan.liquidity_state(FakeRPC(),hs,'0x123')
        self.assertEqual(row['cash_usd'],7)
        self.assertEqual(row['available_usd'],0)
        self.assertFalse(row['supply_enabled'])
        comp = hs['compound'][live_scan.COMETS[comet]]
        self.assertEqual(comp['cash_usd'],11)
        self.assertEqual(comp['available_usd'],0)
        self.assertTrue(comp['supply_enabled'])

    def test_exact_verifier_checks_reject_one_block_and_fractional_eth_drift(self):
        self.assertTrue(close(2984, 2984, 0.0))
        self.assertFalse(close(2984, 2983, 0.0))
        self.assertFalse(close(12.35, 12.85, 0.0))
        self.assertFalse(close(.505, .995, 0.0))

    def test_enrichment_preserves_prices_and_reads_only_the_saved_block(self):
        class FakeRPC:
            blocks = []
            def eth_calls(self, items, block):
                self.blocks.append(block)
                # Aave account data: collateral, debt, available borrow, threshold, LTV, health factor.
                return ['0x' + ''.join(hex(x)[2:].rjust(64, '0') for x in
                                     (10**10, 5*10**9, 25*10**8, 8000, 7500, 16*10**17)) for _ in items]
            def stats(self):
                return {'credits': 80}
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)
            hs = {'block': 291, 'block_hash': 'pinned', 'timestamp': 123, 'feeds': {'ETH': {'usd': 2500}},
                  'rates': {}, 'lending': {}, 'compound': {}, 'tokens': {}, 'health': [], 'token_registry_mismatches': []}
            (out/'head_state.json').write_text(json.dumps(hs))
            (out/'analysis.json').write_text(json.dumps({'lending_ops': {'large_ops': [
                {'venue': 'Aave v3', 'usd': 1000000, 'account': '0x'+'1'*40}]}}))
            rpc = FakeRPC()
            with patch.object(live_scan, 'RPC', return_value=rpc), contextlib.redirect_stdout(io.StringIO()):
                live_scan.enrich(argparse.Namespace(out=d, max_credits=1000))
            after = json.loads((out/'head_state.json').read_text())
            for key in ('block', 'block_hash', 'timestamp', 'feeds', 'rates', 'lending', 'compound'):
                self.assertEqual(after[key], hs[key])
            self.assertEqual(set(rpc.blocks), {'0x123'})
            self.assertEqual(after['health'][0]['health_factor'], 1.6)
            self.assertEqual(after['health'][0]['ltv'], .75)
            self.assertEqual(after['health'][0]['available_borrow_usd'], 25)


if __name__ == '__main__':
    unittest.main()
