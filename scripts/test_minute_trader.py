"""Economic accounting, causal paper entries, and failure handling."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

import minute_trader as M


def row(**extra):
    return {'pool': 'pool', 'pair': 'TOKEN/USDC', 'decision': 'paper candidate',
            'return_3m_bps': 200, 'return_1m_bps': 80, 'cost_bps': 50,
            'buy_share_3m': .8, 'swaps_3m': 8, 'last_swap_age_seconds': 12,
            'entry_gas_usd': 2, 'bought_raw': '1000000000000000000', **extra}


def snap(ts, **extra):
    return {'timestamp': ts, 'rows': [row(**extra)]}


class MinuteTradingTests(unittest.TestCase):
    def test_decimal_and_token_order(self):
        # token0 USDC (6 decimals), token1 WETH (18 decimals), 2500 USDC/ETH.
        sqrt_price = int((M.D(10)**12 / 2500).sqrt()*M.D(2**96))
        self.assertAlmostEqual(float(M.price(sqrt_price, 0, 18, 6)), 2500)
        self.assertAlmostEqual(float(M.price(sqrt_price, 1, 6, 18)), 1/2500)

    def test_signed_pool_deltas(self):
        self.assertEqual(M.signed(2**256-100), -100)
        self.assertEqual(M.signed(100), 100)

    def test_haircut_rounds_down(self):
        self.assertEqual(M.haircut(1001, 20), 998)

    def test_costs_staleness_and_missing_history_block_entries(self):
        cfg = M.Config()
        self.assertEqual(M.signal(row(), cfg), 'paper candidate')
        for changes in ({'cost_bps': 120}, {'last_swap_age_seconds': 61},
                        {'return_3m_bps': None}, {'return_1m_bps': -1},
                        {'buy_share_3m': .4}, {'swaps_3m': 4}, {'error': 'revert'}):
            self.assertNotEqual(M.signal(row(**changes), cfg), 'paper candidate')

    def test_causal_entry_and_actual_amount_exit_accounting(self):
        book = M.PaperBook(M.Config())
        self.assertEqual(book.step(snap(1000)), 'candidate queued for next snapshot')
        book.step(snap(1000))
        self.assertIsNone(book.position)
        book.step(snap(1030))
        self.assertEqual(book.cash, 8998)
        self.assertEqual(book.position['opened_at'], 1030)
        book.step(snap(1060, exit_value_usd=1008))
        self.assertIsNotNone(book.position)
        book.step(snap(1330, exit_value_usd=1008))
        self.assertIsNone(book.position)
        self.assertEqual(book.cash, 10006)
        self.assertEqual(book.trades[0]['net_pnl_usd'], 6)
        self.assertEqual(book.trades[0]['reason'], 'time limit')

    def test_exit_failure_keeps_position_open(self):
        book = M.PaperBook(M.Config())
        book.step(snap(1000))
        book.step(snap(1030))
        action = book.step(snap(2000, error='sell reverted'), finishing=True)
        self.assertIn('unresolved', action)
        self.assertIsNotNone(book.position)
        self.assertEqual(book.trades, [])
        self.assertEqual(book.cash, 8998)

    def test_entry_quote_failure_does_not_prevent_valid_position_exit(self):
        book = M.PaperBook(M.Config())
        book.step(snap(1000))
        book.step(snap(1030))
        book.step(snap(1330, error='new entry quote failed', exit_value_usd=1005))
        self.assertIsNone(book.position)
        self.assertEqual(book.trades[0]['net_pnl_usd'], 3)

    def test_loss_halt_and_early_stop(self):
        book = M.PaperBook(M.Config(max_loss_usd=20))
        book.step(snap(1000))
        book.step(snap(1030))
        book.step(snap(1060, exit_value_usd=970))
        self.assertTrue(book.halted)
        self.assertEqual(book.trades[0]['net_pnl_usd'], -32)
        self.assertEqual(book.step(snap(2000)), 'halted')
        self.assertIsNone(book.pending)

    def test_signal_must_still_qualify_at_entry(self):
        book = M.PaperBook(M.Config())
        book.step(snap(1000))
        book.step(snap(1030, decision='round-trip cost too high'))
        self.assertIsNone(book.position)
        self.assertIsNone(book.pending)

    def test_old_pending_and_late_entries_are_not_filled(self):
        book = M.PaperBook(M.Config())
        book.step(snap(1000))
        book.step(snap(1200))
        self.assertIsNone(book.position)
        book.step(snap(1230), allow_entries=False)
        self.assertIsNone(book.position)
        self.assertIsNone(book.pending)

    def test_read_only_boundary(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(M, 'RPC') as rpc:
            reader = M.Reader(Path(directory), 1000)
            with self.assertRaises(ValueError):
                reader.get('eth_sendRawTransaction', ['0x00'])
            rpc.return_value.batch.assert_not_called()

    def test_reorg_and_stale_head_rejection(self):
        reader = object.__new__(M.Reader)
        reader.get = lambda *args, **kwargs: {'hash': 'replacement'}
        with self.assertRaisesRegex(RuntimeError, 'Reorg'):
            reader.canonical({'hash': 'original', 'number': '0x1'})
        reader.get = lambda *args, **kwargs: {'timestamp': hex(1000)}
        with patch.object(M.time, 'time', return_value=1091):
            with self.assertRaisesRegex(RuntimeError, 'stale'):
                reader.head()

    def test_invalid_risk_configuration(self):
        for cfg in (M.Config(notional_usd=10000), M.Config(hold_seconds=60),
                    M.Config(slippage_bps=10000), M.Config(cash_usd=float('nan'))):
            with self.assertRaises(ValueError):
                cfg.validate()


if __name__ == '__main__':
    unittest.main()
