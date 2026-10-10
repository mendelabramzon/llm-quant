"""Offline tests for the Sui, Aptos and Starknet probe adapters: decoders, window arithmetic, netting.

    uv run --with pycryptodome python -m pytest scripts/test_chain_adapters_move.py -q
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chain_adapters import net_positive, stratified_total  # noqa: E402
from chain_adapters._search import kary_first_at, ratio_estimate, seeded_bracket  # noqa: E402
from chain_adapters import aptos, starknet, sui  # noqa: E402


class SearchTests(unittest.TestCase):
    def setUp(self):
        # timestamps of heights 0..9999: 4 per second with a stall (heights 5000-5099 share one second)
        self.ts = {}
        t = 1_000_000.0
        for h in range(10_000):
            if not 5000 <= h < 5100:
                t += 0.25
            self.ts[h] = t
        self.reads = 0

    def read(self, xs):
        self.reads += 1
        return {x: self.ts.get(x) for x in xs}

    def test_kary_finds_the_first_height_at_or_after(self):
        for target_h in (0, 1, 777, 5000, 5099, 5100, 9999):
            target = self.ts[target_h]
            got = kary_first_at(self.read, 0, 9999, target, fanout=50)
            self.assertEqual(got, min(h for h in self.ts if self.ts[h] >= target), target_h)

    def test_kary_settles_in_a_few_rounds(self):
        self.reads = 0
        kary_first_at(self.read, 0, 9999, self.ts[6543], fanout=50)
        self.assertLessEqual(self.reads, 4)

    def test_kary_skips_unreadable_heights(self):
        holes = {h: v for h, v in self.ts.items() if h % 7}
        got = kary_first_at(lambda xs: {x: holes.get(x) for x in xs}, 0, 9999, self.ts[4242], fanout=30)
        self.assertEqual(got, min(h for h in holes if holes[h] >= self.ts[4242]))

    def test_seeded_bracket_holds_the_target_even_with_a_bad_rate(self):
        target = self.ts[1234]
        for rate in (4.0, 1.0, 40.0):
            lo, hi = seeded_bracket(lambda x: self.ts.get(x), target, 9999, self.ts[9999], rate, min_span=50)
            self.assertLess(self.ts[lo], target)
            self.assertGreaterEqual(self.ts[hi], target)

    def test_ratio_estimator_is_exact_when_the_share_is_constant(self):
        xs = [10, 20, 30, 40]
        ys = [6, 12, 18, 24]                      # exactly 60% everywhere
        y, se = ratio_estimate(ys, xs, 1000, N=100)
        self.assertAlmostEqual(y, 600.0)
        self.assertAlmostEqual(se, 0.0)

    def test_ratio_estimator_error_shrinks_with_the_population_correction(self):
        xs, ys = [10, 12, 9, 11, 10], [5, 8, 4, 7, 5]
        _, se_big = ratio_estimate(ys, xs, 1000, N=10_000)
        _, se_small = ratio_estimate(ys, xs, 1000, N=6)
        self.assertGreater(se_big, se_small)
        self.assertEqual(ratio_estimate([], [], 10), (None, None))


class SuiTests(unittest.TestCase):
    def tx(self, kind, status='SUCCESS', changes=()):
        return {'digest': 'd', 'kind': {'__typename': kind},
                'effects': {'status': status, 'balanceChanges': {'nodes': [
                    {'coinType': {'repr': ct}, 'amount': str(a)} for ct, a in changes]}}}

    def test_only_successful_user_transactions_carry_value(self):
        SUI, USDC = '0x2::sui::SUI', '0xdba3::usdc::USDC'
        txs = [self.tx('ConsensusCommitPrologueTransaction'),
               self.tx('ProgrammableSystemTransaction', changes=[(SUI, 999)]),
               self.tx('ProgrammableTransaction', changes=[(USDC, -100), (USDC, 100), (SUI, -5)]),
               self.tx('ProgrammableTransaction', changes=[(USDC, 40), (USDC, 60)]),
               self.tx('ProgrammableTransaction', status='FAILURE', changes=[(SUI, 10_000)])]
        r = sui.reduce_checkpoint(txs)
        self.assertEqual((r['n_all'], r['n_user'], r['n_fail']), (5, 3, 1))
        self.assertEqual(r['coins'], {USDC: [3, 200]})

    def test_timestamps_parse_to_unix_seconds(self):
        self.assertAlmostEqual(sui.parse_ts('2026-10-09T14:41:37.337Z'), 1791556897.337, places=3)


class AptosTests(unittest.TestCase):
    STORE_A, STORE_B, ROUTER = '0x' + 'a1' * 32, '0x' + 'b2' * 32, '0x' + 'c3' * 32
    USDC = '0xbae207659db88bea0cbead6da0ed00aac12edcdda169e591cd41c94180b46f3b'

    def store_change(self, store, meta):
        return {'type': 'write_resource', 'address': store,
                'data': {'type': aptos.FA_STORE, 'data': {'metadata': {'inner': meta}, 'balance': '1'}}}

    def ev(self, kind, store, amount):
        return {'type': kind, 'data': {'store': store, 'amount': str(amount)}, 'guid': {}}

    def test_address_normalisation_follows_aip40(self):
        self.assertEqual(aptos.norm_addr('0xA'), '0xa')
        self.assertEqual(aptos.norm_addr('0x000000000000000000000000000000000000000000000000000000000000000a'), '0xa')
        self.assertEqual(aptos.norm_addr('0x10'), '0x' + '0' * 62 + '10')

    def test_a_transfer_counts_once_and_a_router_hop_nets_to_zero(self):
        t = {'type': 'user_transaction', 'success': True,
             'changes': [self.store_change(s, self.USDC) for s in (self.STORE_A, self.STORE_B, self.ROUTER)],
             'events': [self.ev(aptos.FA_WITHDRAW, self.STORE_A, 100), self.ev(aptos.FA_DEPOSIT, self.ROUTER, 100),
                        self.ev(aptos.FA_WITHDRAW, self.ROUTER, 100), self.ev(aptos.FA_DEPOSIT, self.STORE_B, 100)]}
        r = aptos.reduce_block([t])
        deposits, net, gross = r['assets'][self.USDC]
        self.assertEqual((deposits, net, gross), (2, 100, 200))

    def test_unresolved_stores_keep_their_net_for_a_later_lookup(self):
        t = {'type': 'user_transaction', 'success': True, 'changes': [],
             'events': [self.ev(aptos.FA_DEPOSIT, self.STORE_A, 70), self.ev(aptos.FA_WITHDRAW, self.STORE_A, 20)]}
        r = aptos.reduce_block([t])
        self.assertEqual(r['assets'], {})
        self.assertEqual(r['unresolved'][aptos.norm_addr(self.STORE_A)], [1, 50, 70])

    def test_system_and_failed_transactions(self):
        txs = [{'type': 'block_metadata_transaction'}, {'type': 'block_epilogue_transaction'},
               {'type': 'some_future_system_transaction'},
               {'type': 'user_transaction', 'success': False, 'events': [self.ev(aptos.FA_DEPOSIT, self.STORE_A, 5)]}]
        r = aptos.reduce_block(txs)
        self.assertEqual((r['n_all'], r['n_system'], r['n_user'], r['n_fail']), (4, 3, 1, 1))
        self.assertEqual(r['assets'], {})

    def test_legacy_coin_events_net_per_account(self):
        coin = '0x1::aptos_coin::AptosCoin'
        acct = '0x' + 'd4' * 32
        t = {'type': 'user_transaction', 'success': True, 'changes': [],
             'events': [{'type': aptos.COIN_DEPOSIT, 'data': {'account': acct, 'coin_type': coin, 'amount': '30'}},
                        {'type': aptos.COIN_WITHDRAW, 'data': {'account': acct, 'coin_type': coin, 'amount': '10'}}]}
        self.assertEqual(aptos.reduce_block([t])['assets'][coin], [1, 20, 30])

    def test_guid_coin_events_resolve_through_the_write_set(self):
        coin = '0x1::aptos_coin::AptosCoin'
        acct = '0x' + 'e5' * 32
        store = {'type': 'write_resource', 'address': acct,
                 'data': {'type': aptos.COIN_STORE_PREFIX + coin + '>', 'data': {
                     'deposit_events': {'guid': {'id': {'addr': acct, 'creation_num': '2'}}},
                     'withdraw_events': {'guid': {'id': {'addr': acct, 'creation_num': '3'}}}}}}
        t = {'type': 'user_transaction', 'success': True, 'changes': [store],
             'events': [{'type': aptos.COIN_DEPOSIT_LEGACY, 'guid': {'account_address': acct, 'creation_number': '2'},
                         'data': {'amount': '9'}}]}
        self.assertEqual(aptos.reduce_block([t])['assets'][coin], [1, 9, 9])


class StarknetTests(unittest.TestCase):
    TOKEN = '0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8'

    def cairo1(self, frm, to, amount, tx='0x1'):
        return {'from_address': self.TOKEN, 'transaction_hash': tx,
                'keys': [starknet.TRANSFER_SEL, hex(frm), hex(to)], 'data': [hex(amount & ((1 << 128) - 1)), hex(amount >> 128)]}

    def cairo0(self, frm, to, amount, tx='0x1'):
        return {'from_address': self.TOKEN, 'transaction_hash': tx, 'keys': [starknet.TRANSFER_SEL],
                'data': [hex(frm), hex(to), hex(amount & ((1 << 128) - 1)), hex(amount >> 128)]}

    def test_transfer_selector_is_sn_keccak(self):
        self.assertEqual(int(starknet.TRANSFER_SEL, 16),
                         0x99cd8bde557814842a3121e8ddfd433a539b8c9f14bf31ebf108d12e6196e9)

    def test_both_layouts_decode_and_u256_high_word_counts(self):
        big = (5 << 128) + 7
        for make in (self.cairo1, self.cairo0):
            tok, frm, to, amt = starknet.decode_transfer(make(1, 2, big))
            self.assertEqual((tok, amt), (starknet.norm_addr(self.TOKEN), big))
            self.assertEqual((frm, to), (starknet.norm_addr('0x1'), starknet.norm_addr('0x2')))

    def test_nft_and_foreign_events_are_not_fungible_transfers(self):
        nft = {'from_address': self.TOKEN, 'keys': [starknet.TRANSFER_SEL, '0x1', '0x2', '0x5', '0x0'], 'data': []}
        other = {'from_address': self.TOKEN, 'keys': ['0x1234'], 'data': ['0x1', '0x2', '0x3', '0x0']}
        self.assertIsNone(starknet.decode_transfer(nft))
        self.assertIsNone(starknet.decode_transfer(other))

    def test_net_per_transaction_cancels_a_flash_loan_and_keeps_gross(self):
        ev = [self.cairo1(0xA, 0xB, 1000, tx='0x9'), self.cairo1(0xB, 0xA, 1003, tx='0x9'),   # flash loan + 3 fee
              self.cairo1(0xC, 0xD, 50, tx='0x8')]                                             # a plain transfer
        sums = starknet.block_token_sums(ev)
        self.assertEqual(sums[starknet.norm_addr(self.TOKEN)], [3, 3 + 50, 2053])

    def test_short_strings_and_byte_arrays(self):
        self.assertEqual(starknet.decode_short_string([hex(int.from_bytes(b'STRK', 'big'))]), 'STRK')
        word = int.from_bytes(b'x' * 31, 'big')
        self.assertEqual(starknet.decode_short_string(['0x1', hex(word), hex(int.from_bytes(b'ab', 'big')), '0x2']),
                         'x' * 31 + 'ab')
        self.assertIsNone(starknet.decode_short_string([]))


class ConventionTests(unittest.TestCase):
    def test_net_positive_matches_the_balance_delta_view(self):
        # A -> router -> B : the router nets out; what B gained is the value moved
        self.assertEqual(net_positive([('A', 'R', 10), ('R', 'B', 10)]), 10)
        self.assertEqual(net_positive([('A', 'A', 10)]), 0)

    def test_stratified_total_is_exact_on_a_full_read(self):
        self.assertEqual(stratified_total([1, 2, 3], 3), (6.0, 0.0))


if __name__ == '__main__':
    unittest.main()
