"""Offline tests for the UTXO, Blockchair, Tezos, Cardano and Hyperliquid chain adapters: the pure reductions, on
synthetic inputs whose answer is known, so a change to a reducer cannot pass by agreeing with itself on live data.

    uv run --with pycryptodome python -m pytest scripts/test_chain_adapters_misc.py -q
"""
import unittest

from chain_adapters import cardano, hyperliquid, tezos, utxo


def block(height, ts, txs, out_amt, reward, bid=None):
    return {'height': height, 'timestamp': ts, 'tx_count': txs, 'id': bid or 'h%d' % height,
            'extras': {'totalOutputAmt': out_amt, 'reward': reward, 'totalFees': 1000}}


class UtxoTests(unittest.TestCase):
    def test_window_is_by_header_time_and_survives_out_of_order_timestamps(self):
        # miners may stamp a later block earlier than its parent; selection is by each block's own time
        bl = [block(10, 1000, 5, 9e8, 1e8), block(11, 990, 3, 5e8, 1e8), block(12, 2000, 7, 6e8, 1e8)]
        rows = utxo.reduce_blocks(bl, 995, 2000)
        self.assertEqual([r['height'] for r in rows], [10])          # 11 is before the window, 12 is at its open end

    def test_coinbase_and_hogex_are_system_transactions(self):
        bl = [block(1, 100, 10, 1_000_000, 300), block(2, 101, 4, 600, 100)]
        rows = utxo.reduce_blocks(bl, 0, 1000, hogex_out={'h1': 900_000})
        r1, r2 = rows
        self.assertEqual(r1['user_tx'], 8)                             # coinbase and HogEx
        self.assertEqual(r1['gross_out'], 1_000_000 - 300 - 900_000)
        self.assertEqual(r2['user_tx'], 3)                             # coinbase only
        self.assertEqual(r2['gross_out'], 500)

    def test_gross_never_negative(self):
        rows = utxo.reduce_blocks([block(1, 100, 1, 50, 80)], 0, 1000)
        self.assertEqual(rows[0]['gross_out'], 0)
        self.assertEqual(rows[0]['user_tx'], 0)

    def test_hogex_with_pegouts_subtracts_only_the_v8_output(self):
        hog = {'vout': [{'scriptpubkey': '5820' + '11' * 32, 'value': 46_000_000_000_000},
                        {'scriptpubkey': '76a914' + '22' * 20 + '88ac', 'value': 43_693_850}]}
        self.assertTrue(utxo.is_hogex(hog))
        self.assertEqual(utxo.hogex_value(hog), 46_000_000_000_000)
        normal = {'vout': [{'scriptpubkey': '0014' + '33' * 20, 'value': 5}, {'scriptpubkey': '5820' + '44' * 32, 'value': 7}]}
        self.assertFalse(utxo.is_hogex(normal))                        # a v8 output that is not first is not a HogEx

    def test_blockchair_parse_flags_an_inconsistent_index(self):
        d = {'transactions_24h': 18805, 'volume_24h': 1_300_000_000_000_000_000, 'blocks': 6_550_142,
             'best_block_height': 6_408_102, 'best_block_time': '2026-10-09 14:11:40'}
        p = utxo.parse_blockchair(d, 8)
        self.assertTrue(p['index_inconsistent'])
        self.assertAlmostEqual(p['volume_24h_native'], 13_000_000_000.0)
        self.assertEqual(p['best_block_ts'], 1791555100)
        d2 = dict(d, blocks=6_408_103)
        self.assertFalse(utxo.parse_blockchair(d2, 8)['index_inconsistent'])


class TezosTests(unittest.TestCase):
    def test_router_hop_nets_out_within_an_operation_group(self):
        a, r, b = {'address': 'tzA'}, {'address': 'KTrouter'}, {'address': 'tzB'}
        rows = [[1, 'opX', a, r, 100], [2, 'opX', r, b, 100], [3, 'opY', b, a, 30]]
        net, gross, n, groups = tezos.xtz_by_group(rows)
        self.assertEqual((net, gross, n, groups), (130, 230, 3, 2))

    def test_token_swap_legs_net_per_group_and_mints_count(self):
        id2hash = {10: 'opS', 11: 'opS'}
        rows = [
            # A pays 50 USDt into a pool and the pool pays the same 50 on to B, both inside one swap group: nets to 50
            [1, '50', 'KTusdt', '0', 'fa1.2', '6', 'USDt', 'tzA', 'KTpool', 10, None, None],
            [2, '50', 'KTusdt', '0', 'fa1.2', '6', 'USDt', 'KTpool', 'tzB', 11, None, None],
            # a mint (no sender) of 7 in its own group counts 7
            [3, '7', 'KTusdt', '0', 'fa1.2', '6', 'USDt', None, 'tzC', 12, None, None],
            # no transactionId: its own group
            [4, '1', 'KTnft', '9', 'fa2', '0', 'X', 'tzA', 'tzB', None, 77, None],
        ]
        t = tezos.tokens_by_group(rows, id2hash)
        self.assertEqual(t['KTusdt:0']['gross'], 107)
        self.assertEqual(t['KTusdt:0']['net'], 57)
        self.assertEqual(t['KTusdt:0']['n_groups'], 2)
        self.assertEqual(t['KTnft:9']['net'], 1)

    def test_only_fungible_token_id_zero_has_a_price_key(self):
        self.assertEqual(tezos.token_key('KT1X', '0'), 'tezos:KT1X')
        self.assertIsNone(tezos.token_key('KT1X', '5'))


class CardanoTests(unittest.TestCase):
    def test_change_to_the_same_stake_key_nets_out(self):
        tx = {'inputs': [{'value': '10000000', 'stake_addr': 'stakeA', 'payment_addr': {'bech32': 'addr1'},
                          'asset_list': [{'policy_id': 'pp', 'asset_name': '41', 'quantity': '500', 'decimals': 0}]}],
              'outputs': [{'value': '3000000', 'stake_addr': 'stakeB', 'payment_addr': {'bech32': 'addrB'}, 'asset_list': []},
                          # change to a different address under the same stake key
                          {'value': '6800000', 'stake_addr': 'stakeA', 'payment_addr': {'bech32': 'addr2'},
                           'asset_list': [{'policy_id': 'pp', 'asset_name': '41', 'quantity': '500', 'decimals': 0}]}]}
        f = cardano.fold_txs([tx])
        self.assertEqual(f['lovelace_gross'], 9_800_000)
        self.assertEqual(f['lovelace_net'], 3_000_000)                # only B gained; the 0.2 ADA fee is A's loss
        self.assertEqual(f['assets']['pp41']['gross'], 500)
        self.assertEqual(f['assets']['pp41']['net'], 0)               # the token came straight back
        self.assertEqual(f['netted'], 1)

    def test_transaction_without_inputs_is_not_netted(self):
        tx = {'inputs': [], 'outputs': [{'value': '5', 'payment_addr': {'bech32': 'a'}}]}
        f = cardano.fold_txs([tx])
        self.assertEqual((f['lovelace_gross'], f['lovelace_net'], f['netted'], f['lovelace_gross_netted']), (5, 0, 0, 0))

    def test_merge_rows_adds_totals(self):
        a = {'assets': [{'usd': 2}], 'unpriced_top': [], 'unpriced_assets': 1, 'unpriced_transfers': 3,
             'priced_usd': 2.0, 'usd_by_class': {'native': 2.0}, 'gross_priced_usd': 5.0}
        b = {'assets': [{'usd': 7}], 'unpriced_top': [{'transfers': 4}], 'unpriced_assets': 2, 'unpriced_transfers': 4,
             'priced_usd': 7.0, 'usd_by_class': {'native': 1.0, 'other': 6.0}, 'gross_priced_usd': 9.0}
        m = cardano.merge_rows(a, b)
        self.assertEqual(m['priced_usd'], 9.0)
        self.assertEqual(m['usd_by_class'], {'native': 3.0, 'other': 6.0})
        self.assertEqual(m['gross_priced_usd'], 14.0)
        self.assertEqual([r['usd'] for r in m['assets']], [7, 2])


class HyperliquidTests(unittest.TestCase):
    def test_perp_rows_skip_dead_delisted_and_price_open_interest(self):
        meta = {'universe': [{'name': 'BTC'}, {'name': 'OLD', 'isDelisted': True}, {'name': 'xyz:GOLD'}]}
        ctxs = [{'dayNtlVlm': '100', 'dayBaseVlm': '1', 'markPx': '50', 'openInterest': '2', 'funding': '0.0001'},
                {'dayNtlVlm': '0', 'markPx': '1', 'openInterest': '0'},
                {'dayNtlVlm': '30', 'dayBaseVlm': '10', 'markPx': '3', 'openInterest': '4'}]
        rows = hyperliquid.perp_rows('', meta, ctxs)
        self.assertEqual([r['asset'] for r in rows], ['perp:BTC', 'perp:xyz:GOLD'])
        self.assertEqual(rows[0]['oi_usd'], 100.0)
        self.assertEqual(rows[0]['dex'], 'main')

    def test_spot_rows_map_indices_convert_quotes_and_fold_outcomes(self):
        spot_meta = {'tokens': [{'index': 0, 'name': 'USDC'}, {'index': 1, 'name': 'HYPE'}, {'index': 2, 'name': 'PURR'}],
                     'universe': [{'name': 'PURR/USDC', 'index': 0, 'tokens': [2, 0]},
                                  {'name': '@1', 'index': 1, 'tokens': [1, 0]},
                                  {'name': '@2', 'index': 2, 'tokens': [2, 1]}]}
        ctxs = [{'coin': 'PURR/USDC', 'dayNtlVlm': '10', 'markPx': '0.1'},
                {'coin': '@1', 'dayNtlVlm': '1000', 'markPx': '40'},
                {'coin': '@2', 'dayNtlVlm': '2', 'markPx': '0.0025'},    # quoted in HYPE: 2 HYPE = $80
                {'coin': '#5', 'dayNtlVlm': '3', 'markPx': '0.4'}, {'coin': '#6', 'dayNtlVlm': '0', 'markPx': '0.5'}]
        rows, outcome = hyperliquid.spot_rows(spot_meta, ctxs)
        by = {r['asset']: r for r in rows}
        self.assertEqual(by['spot:PURR/USDC']['usd'], 10.0)
        self.assertEqual(by['spot:HYPE/USDC']['usd'], 1000.0)
        self.assertEqual(by['spot:PURR/HYPE']['usd'], 80.0)
        self.assertEqual((outcome['markets'], outcome['traded'], outcome['usd']), (2, 1, 3.0))

    def test_height_search_finds_the_time_and_stops_at_the_head(self):
        head = 5_000_000
        t0 = 1_700_000_000_000

        def get_time(h):                       # ~14 blocks/s with a slow drift, nothing past the head
            if h > head or h < 1:
                return None
            return t0 + int(h * 1000 / 14.0) + (h // 100_000) * 37
        target = get_time(3_210_987)
        h, t, reads = hyperliquid.height_at(get_time, target, anchor=1_000_000, rate=10.0)
        self.assertLessEqual(abs(t - target), hyperliquid.TIME_TOLERANCE_MS)
        self.assertLess(reads, 30)
        h2, t2, _ = hyperliquid.height_at(get_time, get_time(head) + 3_600_000, anchor=1_000_000)
        self.assertEqual(h2, head)                                    # a time past the head answers the head
        h3, t3, _ = hyperliquid.height_at(get_time, get_time(200_000), anchor=4_000_000)
        self.assertLessEqual(abs(t3 - get_time(200_000)), hyperliquid.TIME_TOLERANCE_MS)


if __name__ == '__main__':
    unittest.main()
