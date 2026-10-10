#!/usr/bin/env python3
"""Offline tests for the Cosmos, TON and NEAR chain adapters: the pure parsing and netting functions, on synthetic
inputs whose answers are known. No network.

    uv run --with pycryptodome python -m pytest scripts/test_chain_adapters_cosmos_ton_near.py -q
"""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chain_adapters import cosmos, near, ton  # noqa: E402


def b64(s):
    return base64.b64encode(s.encode()).decode()


# ---------------------------------------------------------------------------------------------- cosmos

def test_parse_coins_lists_and_denoms():
    assert cosmos.parse_coins('123uosmo,45ibc/27AB') == [(123, 'uosmo'), (45, 'ibc/27AB')]
    assert cosmos.parse_coins('7factory/osmo1abc/alloyed/allUSDC') == [(7, 'factory/osmo1abc/alloyed/allUSDC')]
    assert cosmos.parse_coins('10peggy0xdAC17F958D2ee523a2206206994597C13D831ec7') == \
        [(10, 'peggy0xdAC17F958D2ee523a2206206994597C13D831ec7')]
    # malformed members are dropped, not guessed
    assert cosmos.parse_coins('abc,12,,  ,5uatom') == [(5, 'uatom')]
    assert cosmos.parse_coins('') == [] and cosmos.parse_coins(None) == []


def test_event_attrs_decodes_base64_only_when_the_node_encodes():
    old = {'type': 'transfer', 'attributes': [{'key': b64('recipient'), 'value': b64('osmo1xyz')},
                                               {'key': b64('sender'), 'value': b64('osmo1abc')},
                                               {'key': b64('amount'), 'value': b64('5uosmo')}]}
    assert cosmos.event_attrs(old) == [('recipient', 'osmo1xyz'), ('sender', 'osmo1abc'), ('amount', '5uosmo')]
    # CometBFT 0.38 writes plain text; a plain value that happens to be valid base64 must survive
    new = {'type': 'transfer', 'attributes': [{'key': 'memo', 'value': 'test'}, {'key': 'amount', 'value': '5uosmo'}]}
    assert cosmos.event_attrs(new) == [('memo', 'test'), ('amount', '5uosmo')]


def test_transfer_legs_split_merged_events_in_either_order():
    one = {'attributes': [{'key': 'recipient', 'value': 'b'}, {'key': 'sender', 'value': 'a'},
                          {'key': 'amount', 'value': '1uatom'}, {'key': 'msg_index', 'value': '0'}]}
    assert cosmos.transfer_legs(one) == [('a', 'b', [(1, 'uatom')])]
    merged = {'attributes': [{'key': 'recipient', 'value': 'b'}, {'key': 'sender', 'value': 'a'},
                             {'key': 'amount', 'value': '1uatom'}, {'key': 'recipient', 'value': 'd'},
                             {'key': 'sender', 'value': 'c'}, {'key': 'amount', 'value': '2uatom,3uosmo'}]}
    assert cosmos.transfer_legs(merged) == [('a', 'b', [(1, 'uatom')]), ('c', 'd', [(2, 'uatom'), (3, 'uosmo')])]
    sender_first = {'attributes': [{'key': 'sender', 'value': 'a'}, {'key': 'recipient', 'value': 'b'},
                                   {'key': 'amount', 'value': '1uatom'}, {'key': 'sender', 'value': 'c'},
                                   {'key': 'recipient', 'value': 'd'}, {'key': 'amount', 'value': '2uatom'}]}
    assert cosmos.transfer_legs(sender_first) == [('a', 'b', [(1, 'uatom')]), ('c', 'd', [(2, 'uatom')])]


def test_module_address_matches_the_live_fee_collectors():
    # both addresses were read from live block results on 2026-10-09 (Osmosis) and are the well-known Hub collector
    assert cosmos.module_address('osmo', 'fee_collector') == 'osmo17xpfvakm2amg962yls6f84z3kell8c5lczssa0'
    assert cosmos.module_address('cosmos', 'fee_collector') == 'cosmos17xpfvakm2amg962yls6f84z3kell8c5lserqta'
    assert cosmos.hrp_of('osmo1ze3f954mtj30st8dw2qhylfvvtdv5q6x8zxxrj') == 'osmo'


def _transfer(snd, rcv, amount):
    return {'type': 'transfer', 'attributes': [{'key': 'recipient', 'value': rcv}, {'key': 'sender', 'value': snd},
                                               {'key': 'amount', 'value': amount}]}


def test_reduce_results_nets_per_transaction_and_separates_fees_and_plumbing():
    fee = cosmos.module_address('osmo', 'fee_collector')
    dist = cosmos.module_address('osmo', 'distribution')
    plumbing = {cosmos.module_address('osmo', m) for m in cosmos.PLUMBING_MODULES}
    res = {'txs_results': [
        # a swap routed through a router: user pays 100 uusdc, router forwards 100 to the pool, pool pays 7 uosmo
        {'code': 0, 'events': [_transfer('user', fee, '2uosmo'), _transfer('user', 'router', '100uusdc'),
                               _transfer('router', 'pool', '100uusdc'), _transfer('pool', 'user', '7uosmo')]},
        # a failed transaction moves nothing but is counted
        {'code': 5, 'events': [_transfer('x', 'y', '999uusdc')]},
    ], 'finalize_block_events': [_transfer(fee, dist, '50uosmo'), _transfer('vault', 'user2', '30uosmo')]}
    out = cosmos.reduce_results(res, fee, plumbing)
    assert out['txs'] == 2 and out['failed'] == 1
    assert out['tx']['uusdc'] == [2, 100, 200]          # two legs, net 100 (router passes through), gross 200
    assert out['tx']['uosmo'] == [1, 7, 7]
    assert out['fees']['uosmo'] == [1, 2, 2]
    assert out['block'] == {'uosmo': [1, 30, 30]}       # the fee-collector -> distribution sweep is plumbing


def test_time_denoms_and_classes():
    assert abs(cosmos.parse_time('2026-10-09T14:40:53.541362039Z') - 1791556853.541362) < 1e-3
    assert cosmos.thor_denom('btc-btc') == ('BTC', 'bitcoin')
    assert cosmos.thor_denom('eth-usdc-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48') == ('USDC', 'usd-coin')
    assert cosmos.thor_denom('eth/eth') == ('ETH', 'ethereum')
    assert cosmos.thor_denom('rune') == ('RUNE', 'thorchain')
    assert cosmos.display_exponent({'display': 'osmo', 'denom_units': [{'denom': 'uosmo', 'exponent': 0},
                                                                       {'denom': 'osmo', 'exponent': 6}]}) == 6
    assert cosmos.cosmos_class('USDC.n', None, 'other') == 'usd_stable'
    assert cosmos.cosmos_class('axlUSDC', None, 'other') == 'usd_stable'
    assert cosmos.cosmos_class('stATOM', None, 'other') == 'other'
    assert cosmos.cosmos_class('OSMO', None, 'native') == 'native'
    assert cosmos.trace_price_key([{'counterparty': {'chain_name': 'ethereum',
                                                     'base_denom': '0xA0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'}}]) == \
        'ethereum:0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
    assert cosmos.trace_price_key([{'type': 'synthetic', 'counterparty': {'chain_name': 'bitcoin', 'base_denom': 'sat'}}]) == \
        'coingecko:bitcoin'


# ---------------------------------------------------------------------------------------------- ton

def test_ton_addresses_and_jetton_amounts():
    assert ton.raw_upper('0:b113a9') == '0:B113A9'
    assert ton.workchain('-1:3333') == -1 and ton.workchain('0:ab') == 0 and ton.workchain(None) is None
    assert ton.jetton_amount({'amount': '161840971'}) == 161840971
    assert ton.jetton_amount({'amount': 'x'}) is None and ton.jetton_amount({}) is None


def test_reduce_jettons_skips_aborted_and_groups_by_master():
    recs = [{'jetton_master': '0:b113', 'amount': '100'}, {'jetton_master': '0:B113', 'amount': '50'},
            {'jetton_master': '0:b113', 'amount': '999', 'transaction_aborted': True},
            {'jetton_master': '0:aaaa', 'amount': 'bad'}]
    assert ton.reduce_jettons(recs) == {'0:B113': [2, 150]}


def test_reduce_transactions_nets_per_trace_and_drops_masterchain():
    def tx(acct, src, dst, value, trace, aborted=False):
        return {'account': acct, 'trace_id': trace, 'hash': acct + trace,
                'description': {'aborted': aborted},
                'in_msg': {'source': src, 'destination': dst, 'value': str(value)}}
    txs = [
        tx('0:A', None, '0:A', 0, 't1'),                       # the signed external message that starts trace t1
        tx('0:R', '0:A', '0:R', 5_000_000_000, 't1'),          # A sends 5 TON to a router...
        tx('0:B', '0:R', '0:B', 5_000_000_000, 't1'),          # ...which passes it on to B
        tx('-1:333', '-1:000', '-1:333', 2_700_000_000, 't2'),  # elector plumbing on the masterchain
        tx('0:C', '0:D', '0:C', 1_000_000_000, 't3', aborted=True),
    ]
    out = ton.reduce_transactions(txs)
    assert out['txs'] == 4 and out['external'] == 1 and out['aborted'] == 1
    assert out['gross'] == 11_000_000_000
    assert out['net'] == 6_000_000_000                         # 5 (A->B through R) + 1 (D->C)
    assert out['traces'] == 2


def test_jetton_symbol_from_index_metadata():
    md = {'0:ABC': {'token_info': [{'type': 'jetton_masters', 'symbol': 'pGRAM', 'extra': {'decimals': '9'}}]}}
    assert ton.jetton_symbol(md, '0:abc') == ('pGRAM', 9)
    assert ton.jetton_symbol({}, '0:abc') == (None, None)


# ---------------------------------------------------------------------------------------------- near

def _fc(method, args, deposit='0'):
    return {'FunctionCall': {'method_name': method, 'args': b64(json.dumps(args)), 'deposit': deposit, 'gas': 1}}


def test_decode_args_and_action_moves():
    assert near.decode_args(b64('{"receiver_id": "bob.near", "amount": "5"}')) == {'receiver_id': 'bob.near', 'amount': '5'}
    assert near.decode_args(b64('not json')) == {} and near.decode_args(None) == {}
    acts = [{'Transfer': {'deposit': '2000000000000000000000000'}},
            _fc('ft_transfer', {'receiver_id': 'bob.near', 'amount': '1500000'}, deposit='1'),
            _fc('near_deposit', {}, deposit='3'),
            'CreateAccount']
    assert near.action_moves('alice.near', 'usdt.tether-token.near', acts) == [
        ('native', 'alice.near', 'usdt.tether-token.near', 2 * 10 ** 24),
        ('usdt.tether-token.near', 'alice.near', 'bob.near', 1500000),   # the one-yocto security deposit is not value
        ('native', 'alice.near', 'usdt.tether-token.near', 3)]


def test_reduce_chunks_counts_signed_transactions_once_and_nets_per_block():
    token = 'usdt.tether-token.near'
    chunks = [{
        'transactions': [{'signer_id': 'alice.near', 'receiver_id': token,
                          'actions': [_fc('ft_transfer_call', {'receiver_id': 'dex.near', 'amount': '100'}, '1')]}],
        'receipts': [
            # the same transaction's actions routed to the token's shard: already counted from the transaction
            {'predecessor_id': 'alice.near', 'receiver_id': token,
             'receipt': {'Action': {'signer_id': 'alice.near',
                                    'actions': [_fc('ft_transfer_call', {'receiver_id': 'dex.near', 'amount': '100'}, '1')]}}},
            # the dex, a contract, forwards the tokens on: a contract-created receipt, counted
            {'predecessor_id': 'dex.near', 'receiver_id': token,
             'receipt': {'Action': {'signer_id': 'alice.near',
                                    'actions': [_fc('ft_transfer', {'receiver_id': 'pool.near', 'amount': '100'}, '1')]}}},
            {'predecessor_id': 'system', 'receiver_id': 'alice.near',
             'receipt': {'Action': {'signer_id': 'system', 'actions': [{'Transfer': {'deposit': '5'}}]}}},
            {'predecessor_id': 'dex.near', 'receiver_id': 'alice.near', 'receipt': {'Data': {'data_id': 'x'}}},
        ]}]
    out = near.reduce_chunks(chunks)
    assert out['txs'] == 1 and out['receipts'] == 3 and out['refunds'] == 1
    # alice -> dex -> pool inside one block nets to 100 (alice paid, pool received); gross counts both hops
    assert out['assets'][token] == [2, 100, 200]
    assert 'native' not in out['assets']


def test_omft_names_are_identities():
    assert near.omft_identity('eth-0xdac17f958d2ee523a2206206994597c13d831ec7.omft.near') == \
        ('ethereum:0xdac17f958d2ee523a2206206994597c13d831ec7', None, None)
    assert near.omft_identity('btc.omft.near') == ('coingecko:bitcoin', 'BTC', 8)
    assert near.omft_identity('qtc.omft.near') is None and near.omft_identity('wrap.near') is None


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-q']))
