#!/usr/bin/env python3
"""Offline tests for the payment/account-ledger probes (XRPL, Stellar, Hedera, Algorand): amount parsing, currency
codes, the net-per-transaction value rule, and the window arithmetic. Synthetic inputs only; no network.

    uv run --with pycryptodome python scripts/test_chain_adapters_ledgers.py
    uv run --with pycryptodome --with pytest python -m pytest scripts/test_chain_adapters_ledgers.py -q
"""
import collections
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chain_adapters import algorand, hedera, stellar, xrpl  # noqa: E402

USD_HEX = '0000000000000000000000005553440000000000'
RLUSD_HEX = '524C555344000000000000000000000000000000'
ISSUER = 'rIssuerIssuerIssuerIssuerIssuer'
USD = 'iou:%s.%s' % (USD_HEX, ISSUER)


def acct(account, before, after, kind='ModifiedNode'):
    if kind == 'CreatedNode':
        return {kind: {'LedgerEntryType': 'AccountRoot', 'NewFields': {'Account': account, 'Balance': str(after)}}}
    return {kind: {'LedgerEntryType': 'AccountRoot', 'FinalFields': {'Account': account, 'Balance': str(after)},
                   'PreviousFields': {'Balance': str(before)}}}


def line(low, high, before, after, cur='USD', low_limit='0', high_limit='0', kind='ModifiedNode'):
    fin = {'Balance': {'currency': cur, 'issuer': 'rrrrrrrrrrrrrrrrrrrrBZbvji', 'value': str(after)},
           'LowLimit': {'currency': cur, 'issuer': low, 'value': low_limit},
           'HighLimit': {'currency': cur, 'issuer': high, 'value': high_limit}}
    if kind == 'CreatedNode':
        return {kind: {'LedgerEntryType': 'RippleState', 'NewFields': fin}}
    prev = {'Balance': {'currency': cur, 'issuer': 'rrrrrrrrrrrrrrrrrrrrBZbvji', 'value': str(before)}}
    return {kind: {'LedgerEntryType': 'RippleState', 'FinalFields': fin, 'PreviousFields': prev}}


def net(meta):
    return xrpl.net_moved(xrpl.balance_changes(meta))


def ledger(txs, api2=True, close_time=844_870_780, index=107_540_549):
    out = []
    for tx, meta in txs:
        if api2:
            out.append({'tx_json': tx, 'meta': meta, 'hash': 'H'})
        else:
            d = dict(tx)
            d['metaData'] = meta
            out.append(d)
    return {'transactions': out, 'close_time': close_time, 'ledger_index': str(index)}


def pay(frm, to, amount):
    return {'type': 'payment', 'from': frm, 'to': to, 'amount': str(amount), 'asset_type': 'native'}


def rec(transfers=(), tokens=(), result='SUCCESS', txid='0.0.5-1-1', nonce=0, parent=None):
    return {'result': result, 'transaction_id': txid, 'nonce': nonce, 'parent_consensus_timestamp': parent,
            'transfers': [{'account': a, 'amount': v} for a, v in transfers],
            'token_transfers': [{'token_id': t, 'account': a, 'amount': v} for t, a, v in tokens]}


def stx(txn, **ad):
    d = {'txn': txn}
    d.update(ad)
    return d


class WindowSearch(unittest.TestCase):
    def test_locate_first_index_at_or_after(self):
        times, t = {}, 1_000_000
        for i in range(1, 20_001):
            t += 3 if i % 7 else 11            # uneven spacing
            times[i] = t
        head, head_ts = 20_000, times[20_000]
        targets = (times[1] - 100, times[1], times[5000] - 1, times[5000], times[12345] + 1, head_ts, head_ts + 50)
        for mod in (xrpl, stellar, algorand):
            for spu in (1.0, 3.9, 50.0):       # the seed rate may be badly wrong; the bracket must still find it
                for target in targets:
                    with self.subTest(mod=mod.__name__, spu=spu, target=target):
                        got = mod.locate(target, 1, head, head_ts, spu, times.__getitem__)
                        want = next((i for i in range(1, head + 1) if times[i] >= target), head)
                        self.assertEqual(got, want)


class Xrpl(unittest.TestCase):
    def test_currency_codes(self):
        self.assertEqual(xrpl.currency_hex('USD'), USD_HEX)
        self.assertEqual(xrpl.currency_hex(RLUSD_HEX.lower()), RLUSD_HEX)
        with self.assertRaises(ValueError):
            xrpl.currency_hex('TOOLONG')
        self.assertEqual(xrpl.iou_id('TOOLONG', ISSUER), 'iou:TOOLONG.%s' % ISSUER)   # never raises on odd codes
        self.assertEqual(xrpl.currency_symbol(USD_HEX), 'USD')
        self.assertEqual(xrpl.currency_symbol(RLUSD_HEX), 'RLUSD')
        self.assertEqual(xrpl.currency_symbol('03' + '11' * 19), 'AMM-LP')
        self.assertEqual(xrpl.currency_symbol('EUR'), 'EUR')

    def test_delivered_amount_forms(self):
        self.assertEqual(xrpl.delivered({'delivered_amount': '2500000'}), ('native:XRP', 2.5))
        self.assertEqual(xrpl.delivered({'DeliveredAmount': {'currency': 'USD', 'issuer': ISSUER, 'value': '12.5'}}),
                         (USD, 12.5))
        self.assertEqual(xrpl.delivered({'delivered_amount': {'mpt_issuance_id': 'ABC', 'value': '7'}}), ('mpt:ABC', 7.0))
        self.assertIsNone(xrpl.delivered({'delivered_amount': 'unavailable'}))
        self.assertIsNone(xrpl.delivered({}))

    def test_xrp_payment_nets_out_the_fee(self):
        m = {'AffectedNodes': [acct('rA', 100_000_000, 89_999_988), acct('rB', 5_000_000, 15_000_000)]}
        self.assertEqual(net(m), {'native:XRP': 10.0})

    def test_iou_holder_to_holder_issuance_and_redemption(self):
        # A is the low side of its line (holds 100 -> 60); B the high side of its line (-10 -> -50: B holds 50)
        self.assertAlmostEqual(net({'AffectedNodes': [line('rA', ISSUER, 100, 60), line(ISSUER, 'rB', -10, -50)]})[USD], 40.0)
        self.assertAlmostEqual(net({'AffectedNodes': [line(ISSUER, 'rB', -50, -75)]})[USD], 25.0)          # issuance
        self.assertAlmostEqual(net({'AffectedNodes': [line('rA', ISSUER, 60, 0)]})[USD], 60.0)             # redemption
        created = {'AffectedNodes': [line('rC', ISSUER, None, 5, kind='CreatedNode')]}
        self.assertAlmostEqual(net(created)[USD], 5.0)

    def test_cross_currency_self_payment_counts_the_conversion_not_a_loop(self):
        m = {'AffectedNodes': [acct('rA', 50_000_000, 44_999_990), acct('rMaker', 1_000_000, 6_000_000),
                               line('rA', ISSUER, 0, 7), line('rMaker', ISSUER, 20, 13)]}
        got = net(m)
        self.assertAlmostEqual(got['native:XRP'], 5.0)
        self.assertAlmostEqual(got[USD], 7.0)

    def test_reduce_ledger_partial_payment_failures_and_types(self):
        xrp_pay = ({'TransactionType': 'Payment', 'Amount': '999999999999999'},
                   {'TransactionResult': 'tesSUCCESS', 'delivered_amount': '34148538',
                    'AffectedNodes': [acct('rA', 100_000_000, 65_851_450), acct('rB', 0, 34_148_538, kind='CreatedNode')]})
        failed = ({'TransactionType': 'Payment', 'Amount': '5000000'},
                  {'TransactionResult': 'tecPATH_DRY', 'AffectedNodes': [acct('rC', 1_000_000, 999_988)]})
        offer = ({'TransactionType': 'OfferCreate'},
                 {'TransactionResult': 'tesSUCCESS', 'AffectedNodes': [acct('rD', 10_000_000, 7_999_988),
                                                                        acct('rE', 1_000_000, 3_000_000)]})
        for api2 in (True, False):
            with self.subTest(api2=api2):
                u = xrpl.reduce_ledger(ledger([xrp_pay, failed, offer], api2=api2))
                self.assertEqual((u['n'], u['ok']), (3, 2))
                self.assertEqual(u['types'], {'Payment': 2, 'OfferCreate': 1})
                count, amount, from_payments = u['assets']['native:XRP']
                self.assertEqual(count, 2)
                self.assertAlmostEqual(amount, 34.148538 + 2.0)
                self.assertAlmostEqual(from_payments, 34.148538)
                self.assertEqual(u['delivered'], {'native:XRP': [1, 34.148538]})   # delivered, never the 10^15 Amount
                self.assertEqual(u['ts'], 844_870_780 + xrpl.RIPPLE_EPOCH)

    def test_canonical_par_is_keyed_by_issuer_not_code(self):
        self.assertIn((RLUSD_HEX, 'rMxCKbEDwqr76QuheSUMdEGf4B9xJ8m5De'), xrpl.CANONICAL_PAR)
        self.assertNotIn((RLUSD_HEX, 'rLookalikeIssuerLookalikeIssuer'), xrpl.CANONICAL_PAR)


class Stellar(unittest.TestCase):
    def test_asset_ids(self):
        self.assertEqual(stellar.asset_id({'asset_type': 'native'}), 'native:XLM')
        self.assertEqual(stellar.asset_id({'asset_type': 'credit_alphanum4', 'asset_code': 'USDC', 'asset_issuer': 'GA5Z'}),
                         'USDC-GA5Z')
        self.assertEqual(stellar.asset_id({'source_asset_type': 'native'}, 'source_'), 'native:XLM')
        self.assertIsNone(stellar.asset_id({'asset_type': 'credit_alphanum4'}))

    def test_payments_net_and_gross(self):
        self.assertEqual(stellar.legs(pay('GA', 'GB', '12.5')), ([('native:XLM', 12.5)], [('native:XLM', 12.5)]))
        self.assertEqual(stellar.legs(pay('GA', 'GA', '12.5')), ([], [('native:XLM', 12.5)]))   # to oneself: nothing
        swap = {'type': 'path_payment_strict_send', 'from': 'GA', 'to': 'GB', 'amount': '9.7',
                'asset_type': 'credit_alphanum4', 'asset_code': 'USDC', 'asset_issuer': 'GI',
                'source_asset_type': 'native', 'source_amount': '50'}
        n, g = stellar.legs(swap)
        self.assertEqual(n, [('USDC-GI', 9.7)])                                              # the received leg only
        self.assertEqual(g, [('USDC-GI', 9.7), ('native:XLM', 50.0)])
        loop = {'type': 'path_payment_strict_receive', 'from': 'GA', 'to': 'GA', 'amount': '100.5',
                'asset_type': 'native', 'source_asset_type': 'native', 'source_amount': '100'}
        n, g = stellar.legs(loop)
        self.assertEqual(len(n), 1)
        self.assertAlmostEqual(n[0][1], 0.5)                                                 # only the loop's gain
        self.assertEqual(g, [('native:XLM', 100.5)])
        self.assertEqual(stellar.legs(dict(loop, amount='99'))[0], [('native:XLM', 0.0)])    # a loss counts nothing
        self.assertEqual(stellar.legs(dict(swap, to='GA'))[0], [('USDC-GI', 9.7)])           # self-conversion

    def test_other_payment_kinds(self):
        self.assertEqual(stellar.legs({'type': 'create_account', 'starting_balance': '1.5'}),
                         ([('native:XLM', 1.5)], [('native:XLM', 1.5)]))
        self.assertEqual(stellar.legs({'type': 'account_merge', 'into': 'GB'}), ([], []))
        ihf = {'type': 'invoke_host_function', 'asset_balance_changes': [
            {'type': 'transfer', 'from': 'GA', 'to': 'CB', 'amount': '3', 'asset_type': 'native'},
            {'type': 'transfer', 'from': 'CB', 'to': 'CB', 'amount': '4', 'asset_type': 'native'},
            {'type': 'mint', 'to': 'GA', 'amount': '5', 'asset_type': 'native'}]}
        self.assertEqual(stellar.legs(ihf), ([('native:XLM', 3.0)], [('native:XLM', 3.0), ('native:XLM', 4.0)]))
        self.assertEqual(stellar.legs({'type': 'payment', 'amount': 'not-a-number', 'asset_type': 'native'}), ([], []))

    def test_paging_cursor_and_header_sums(self):
        self.assertEqual(stellar.cursor_after(64854232), 278546805447196672)   # Horizon's token, served 2026-10-09
        recs = [{'sequence': s, 'successful_transaction_count': 10, 'failed_transaction_count': 2,
                 'operation_count': 30, 'tx_set_operation_count': 40} for s in (99, 100, 101, 101, 102, 103)]
        tot, seqs = stellar.sum_headers(recs, 100, 102)
        self.assertEqual(seqs, [100, 101, 102])                                # in window, each counted once
        self.assertEqual(tot, {'successful': 30, 'failed': 6, 'operations': 90, 'tx_set_operations': 120})
        self.assertEqual(stellar.ts_iso('2026-10-09T14:42:22Z'), 1791556942)

    def test_canonical_par_needs_the_issuer(self):
        self.assertIn('USDC-GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN', stellar.CANONICAL_PAR)
        self.assertNotIn('USDC-GLOOKALIKE', stellar.CANONICAL_PAR)


class Hedera(unittest.TestCase):
    def test_account_numbers(self):
        self.assertEqual(hedera.account_num('0.0.802'), 802)
        self.assertEqual(hedera.account_num('0.0.10618649'), 10618649)
        self.assertEqual(hedera.account_num('bogus'), -1)

    def test_fees_and_rewards_are_not_value(self):
        # the 1-tinybar spam shape seen live: the payer pays a fee to 0.0.802 and one tinybar to a user account
        spam = rec([('0.0.802', 108552), ('0.0.3229', -108553), ('0.0.3230', 1)])
        self.assertEqual(hedera.positive_value(hedera.record_changes(spam)), {'native:HBAR': 1})
        self.assertEqual(hedera.record_changes(rec([('0.0.5000', 10)], result='INSUFFICIENT_PAYER_BALANCE')), {})
        tok = rec(tokens=[('0.0.456858', '0.0.3', 7), ('0.0.456858', '0.0.4000', -7)])
        self.assertEqual(hedera.positive_value(hedera.record_changes(tok)), {'0.0.456858': 7})   # the rule is HBAR-only

    def test_merges_a_transactions_records_before_netting(self):
        child1 = rec(tokens=[('0.0.T', '0.0.5000', -100), ('0.0.T', '0.0.6000', 100)], nonce=1, parent='1.1')
        child2 = rec(tokens=[('0.0.T', '0.0.6000', -100), ('0.0.T', '0.0.7000', 100)], nonce=2, parent='1.1')
        merged = {}
        for r in (child1, child2):
            hedera.merge_changes(merged, hedera.record_changes(r))
        self.assertEqual(hedera.positive_value(merged), {'0.0.T': 100})       # the router 0.0.6000 nets to zero
        gross = sum(hedera.positive_value(hedera.record_changes(r))['0.0.T'] for r in (child1, child2))
        self.assertEqual(gross, 200)
        self.assertTrue(hedera.is_child(child1))
        self.assertFalse(hedera.is_child(rec()))

    def test_page_ranges_cover_the_window(self):
        self.assertEqual(hedera.page_ranges(100, 349, size=100), [(100, 199), (200, 299), (300, 349)])
        self.assertEqual(sum(hi - lo + 1 for lo, hi in hedera.page_ranges(1, 43_200)), 43_200)


class Algorand(unittest.TestCase):
    def test_transfer_kinds(self):
        acc = {'types': collections.Counter(), 'n': 0, 'inner': 0, 'assets': {}}
        moves = []
        algorand.walk(stx({'type': 'pay', 'snd': 'A', 'rcv': 'B', 'amt': 2_000_000, 'close': 'C'}, ca=500_000), acc, moves)
        algorand.walk(stx({'type': 'axfer', 'snd': 'A', 'arcv': 'A', 'xaid': 31566704}), acc, moves)     # an opt-in
        algorand.walk(stx({'type': 'axfer', 'snd': 'CLAWBACK', 'asnd': 'D', 'arcv': 'E', 'xaid': 7, 'aamt': 9}), acc, moves)
        self.assertEqual(moves, [('native:ALGO', 'A', 'B', 2_000_000), ('native:ALGO', 'A', 'C', 500_000), ('7', 'D', 'E', 9)])
        self.assertEqual((acc['n'], acc['inner']), (3, 0))
        self.assertEqual(acc['types'], {'pay': 1, 'axfer': 2})

    def test_group_netting_swap_and_round_trip(self):
        swap = [stx({'type': 'pay', 'snd': 'USER', 'rcv': 'POOL', 'amt': 100, 'grp': 'g1'}),
                stx({'type': 'appl', 'snd': 'USER', 'grp': 'g1'},
                    dt={'itx': [stx({'type': 'axfer', 'snd': 'POOL', 'arcv': 'USER', 'xaid': 31566704, 'aamt': 50})]})]
        loop = [stx({'type': 'pay', 'snd': 'BOT', 'rcv': 'P1', 'amt': 1000, 'grp': 'g2'}),
                stx({'type': 'appl', 'snd': 'BOT', 'grp': 'g2'},
                    dt={'itx': [stx({'type': 'pay', 'snd': 'P1', 'rcv': 'BOT', 'amt': 1000})]})]
        solo = [stx({'type': 'pay', 'snd': 'X', 'rcv': 'Y', 'amt': 7}), stx({'type': 'pay', 'snd': 'Y', 'rcv': 'X', 'amt': 7})]
        u = algorand.reduce_block({'txns': swap + loop + solo, 'ts': 1791557013})
        self.assertEqual(u['assets']['31566704'], [1, 50, 50])
        count, net_v, gross = u['assets']['native:ALGO']
        self.assertEqual(net_v, 100 + 7 + 7)         # the swap's leg and two unrelated solo payments; the loop nets out
        self.assertEqual((gross, count), (100 + 2000 + 14, 3))
        self.assertEqual((u['n'], u['inner'], u['top'], u['groups']), (8, 2, 6, 4))

    def test_window_count_is_a_counter_difference(self):
        # tc(r) includes round r, so rounds first..last are tc(last) - tc(first - 1); the live hour of 2026-10-09
        self.assertEqual(algorand.window_count(3_735_009_501, 3_734_944_715), 64_786)


if __name__ == '__main__':
    unittest.main(verbosity=1)
