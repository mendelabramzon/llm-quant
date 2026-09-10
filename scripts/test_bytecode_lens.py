#!/usr/bin/env python3
"""Synthetic controls for the bytecode lens: bytecode whose answer is known before the tool reads it.

Every one of these tests exists because the extractor got that case wrong first, on real mainnet code, and the error
was the kind that produces a *confident* wrong reading rather than a visible failure:

  * the operator that gates a mass EIP-7702 delegate is a zero-padded **PUSH32**, not a PUSH20, so an address scanner
    that reads only PUSH20 misses precisely the addresses that decide who may act;
  * `PUSH4 … MSTORE … REVERT` is a Solidity **custom error**, not an outbound call — read as a call it invents a
    dependency on a contract that does not exist;
  * POP is `P`, JUMP/JUMPDEST is `V[` and PUSH2 is `a`, so compiled Solidity is full of printable runs like
    `V[PPPPPV['` that any naive string scan reports as embedded text;
  * slot 0 of an ordinary implementation holds an initialiser flag, and reading `0x…01` out of it as a Safe singleton
    sends the whole analysis to an empty account.

An LLM reading a packet cannot tell any of those from the truth, which is the whole reason they are tested here rather
than left to be noticed downstream.

    uv run --with pycryptodome python scripts/test_bytecode_lens.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bytecode_lens as bl


def asm(*parts):
    """Assemble a hex body from mnemonic-ish fragments already written as hex."""
    return '0x' + ''.join(parts)


def push4(sel):
    return '63' + sel[2:]


def push32(v):
    return '7f' + v.rjust(64, '0')


def push20(a):
    return '73' + a[2:]


class Disassembly(unittest.TestCase):
    def test_push_data_is_never_decoded_as_code(self):
        """A PUSH32 whose immediate contains 0xff must not yield an INVALID instruction."""
        code = bl.to_bytes(asm(push32('ff' * 32), '00'))
        ins, _, bad = bl.disassemble(code)
        self.assertEqual([x.name for x in ins], ['PUSH32', 'STOP'])
        self.assertEqual(bad, 0)

    def test_truncated_push_immediate_does_not_crash(self):
        ins, _, _ = bl.disassemble(bl.to_bytes('0x7f' + 'ab' * 10))
        self.assertEqual(ins[0].name, 'PUSH32')
        self.assertEqual(len(ins[0].imm), 10)

    def test_modern_opcodes_are_named(self):
        ins, _, bad = bl.disassemble(bl.to_bytes('0x5f5c5d5e4950'))
        self.assertEqual([x.name for x in ins], ['PUSH0', 'TLOAD', 'TSTORE', 'MCOPY', 'BLOBHASH', 'POP'])
        self.assertEqual(bad, 0)


class Selectors(unittest.TestCase):
    def test_solidity_linear_dispatcher(self):
        sel = bl.selector_of('balanceOf(address)')
        ins, _, _ = bl.disassemble(bl.to_bytes(asm('80', push4(sel), '14', '61', '00aa', '57')))
        inbound, _, _, _ = bl.scan_selectors(ins)
        self.assertEqual(list(inbound), [sel])
        self.assertEqual(inbound[sel], 0xaa)

    def test_via_ir_binary_search_pivot_counts_as_a_selector(self):
        """solc --via-ir compares with GT against a real member of the selector set."""
        sel = bl.selector_of('transfer(address,uint256)')
        ins, _, _ = bl.disassemble(bl.to_bytes(asm('80', push4(sel), '11', '61', '0100', '57')))
        self.assertIn(sel, bl.scan_selectors(ins)[0])

    def test_outbound_call_selector(self):
        sel = bl.selector_of('balanceOf(address)')
        # PUSH4 sel; PUSH1 e0; SHL; PUSH1 00; MSTORE; ... STATICCALL
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push4(sel), '60e0', '1b', '6000', '52', '5f5f5f5f5f5f', 'fa')))
        _, outbound, errors, _ = bl.scan_selectors(ins)
        self.assertEqual(outbound, {sel})
        self.assertEqual(errors, set())

    def test_custom_error_is_not_an_outbound_call(self):
        """The bug this catches: `error WhoAreYou()` read as a call to WhoAreYou() on a counterparty."""
        sel = bl.selector_of('WhoAreYou()')
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push4(sel), '60e0', '1b', '6000', '52', '6004', '6000', 'fd')))
        _, outbound, errors, _ = bl.scan_selectors(ins)
        self.assertEqual(errors, {sel})
        self.assertEqual(outbound, set())

    def test_calldata_mask_is_not_a_selector(self):
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push4('0xffffffff'), '16')))
        inbound, outbound, errors, _ = bl.scan_selectors(ins)
        self.assertEqual((inbound, outbound, errors), ({}, set(), set()))

    def test_ascii_fragment_is_not_an_outbound_selector(self):
        """`0x636f756e` is the ASCII 'coun' of an embedded string, not a function."""
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push4('0x636f756e'), '6000', '52', '5f5f5f5f5f5f', 'f1')))
        self.assertEqual(bl.scan_selectors(ins)[1], set())

    def test_eip712_prefix_is_not_an_outbound_selector(self):
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push4('0x19010000'), '6000', '52', '5f5f5f5f5f5f', 'f1')))
        self.assertEqual(bl.scan_selectors(ins)[1], set())


class Addresses(unittest.TestCase):
    OP = '0x59aab1bd0d26290274398c07b55955c15425e16b'

    def test_push20_address(self):
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push20(self.OP), '14')))
        self.assertEqual(bl.scan_addresses(ins), [self.OP])

    def test_zero_padded_push32_address(self):
        """The shape solc emits for `tx.origin == <constant>` — and the one the first version missed entirely."""
        ins, _, _ = bl.disassemble(bl.to_bytes(asm('32', '6001600160a01b', '1b', '03', push32(self.OP[2:]), '16', '14')))
        self.assertEqual(bl.scan_addresses(ins), [self.OP])

    def test_ascii_run_pushed_as_push20_is_not_an_address(self):
        """20 printable bytes of a revert string, pushed whole, are not a counterparty."""
        ascii20 = b' balanceFiatToken: c'.hex()
        ins, _, _ = bl.disassemble(bl.to_bytes(asm('73' + ascii20)))
        self.assertEqual(bl.scan_addresses(ins), [])

    def test_zero_and_small_numbers_are_not_addresses(self):
        ins, _, _ = bl.disassemble(bl.to_bytes(asm(push20('0x' + '00' * 20), push20('0x' + '00' * 3 + 'de' * 17))))
        self.assertEqual(bl.scan_addresses(ins), [])


class Strings(unittest.TestCase):
    KEEP = ['Pausable: paused', 'ERC20: transfer amount exceeds balance', 'Delegated call failed',
            'LogicContract: unauthorized call', 'account: not from EntryPoint', 'insufficient gas', 'ZERO_TGT']
    DROP = ["V[PPPP", "aAcV[s", "a%OWa%Na%", "a'iWa'ha$EV[[a'u", "PPPPPV['", '[PPPPP', 'aKIV[', 'IaBvV[']

    def test_real_messages_survive(self):
        for s in self.KEEP:
            self.assertTrue(bl._looks_like_text(s, strict=True) or bl._looks_like_text(s, strict=False), s)

    def test_opcode_alphabet_runs_are_rejected(self):
        for s in self.DROP:
            self.assertFalse(bl._looks_like_text(s, strict=True), s)

    def test_strings_are_read_out_of_real_shaped_code(self):
        body = bl.to_bytes('0x' + b'V[PPPPPV['.hex() + b'\x00Pausable: paused\x00'.hex())
        self.assertEqual(bl.scan_strings(body), ['Pausable: paused'])


class Proxies(unittest.TestCase):
    IMPL = '0xbebebebebebebebebebebebebebebebebebebebe'

    def test_eip1167_standard(self):
        code = '0x363d3d373d3d3d363d73' + self.IMPL[2:] + '5af43d82803e903d91602b57fd5bf3'
        self.assertEqual(bl.clone_target(bl.to_bytes(code)), self.IMPL)
        self.assertEqual(bl.resolve_proxy(None, '0x' + '11' * 20, code),
                         [{'address': self.IMPL, 'via': 'eip1167-clone'}])

    def test_eip1167_push0_variant(self):
        code = '0x365f5f375f5f5f365f73' + self.IMPL[2:] + '5af43d5f5f3e5f3d91602a57fd5bf3'
        self.assertEqual(bl.clone_target(bl.to_bytes(code)), self.IMPL)

    def test_eip7702_delegation_designator(self):
        code = '0xef0100' + self.IMPL[2:]
        self.assertEqual(bl.resolve_proxy(None, '0x' + '11' * 20, code),
                         [{'address': self.IMPL, 'via': 'eip7702-delegation'}])
        ins, _, _ = bl.disassemble(bl.to_bytes(code))
        self.assertEqual(bl.shape_of(bl.to_bytes(code), ins, {}, {}, 0, set()), 'eip7702-delegation')

    def test_a_large_body_is_never_read_as_a_clone(self):
        code = '0x' + '5af4' + '73' + self.IMPL[2:] + '00' * 300
        self.assertIsNone(bl.clone_target(bl.to_bytes(code)))

    def test_non_delegating_code_is_not_probed_for_slots(self):
        """No DELEGATECALL means no proxy, so the walk must stop before it spends a single request."""
        class Boom:
            def call(self, *a, **k):
                raise AssertionError('resolve_proxy made an RPC call for a non-delegating contract')
            batch = call
        self.assertEqual(bl.resolve_proxy(Boom(), '0x' + '11' * 20, '0x' + '60806040' + '00' * 100), [])


class DataContracts(unittest.TestCase):
    """Data stored as contract code must never be read as a program.

    The first sweep of the 2026-09-08 window ranked three stored-data bodies as its three most capable contracts:
    SELFDESTRUCT, CALLCODE, CREATE2, transient storage, blob reads, all at once, from 13-24 KB of high-entropy bytes
    that a linear sweep turns into an opcode per byte. One of them begins with the gzip magic number.
    """

    def test_high_entropy_body_is_data_not_code(self):
        import hashlib
        blob = b'\x00' + b''.join(hashlib.sha256(bytes([i])).digest() for i in range(200))   # ~6.4 KB, no structure
        ins, dests, _ = bl.disassemble(blob)
        self.assertTrue(bl.is_data_contract(blob, ins, dests))

    def test_gzip_payload_is_named(self):
        blob = b'\x00\x1f\x8b\x08' + bytes(range(256)) * 12
        self.assertEqual(bl.data_payload(blob), 'gzip')
        ins, dests, _ = bl.disassemble(blob)
        self.assertIn('gzip', bl.shape_of(blob, ins, {}, {}, 0, dests))

    def test_ordinary_code_is_not_mistaken_for_data(self):
        """A body with a normal density of jump targets is code however dense its bytes are."""
        body = (b'\x5b' + b'\x60\x01\x60\x02\x01\x50') * 200         # JUMPDEST + a little arithmetic
        ins, dests, _ = bl.disassemble(body)
        self.assertFalse(bl.is_data_contract(body, ins, dests))

    def test_a_short_body_is_never_called_data(self):
        """Minimal proxies and 7702 designators have no jump targets either, and are certainly not blobs."""
        clone = bl.to_bytes('0x363d3d373d3d3d363d73' + 'be' * 20 + '5af43d82803e903d91602b57fd5bf3')
        ins, dests, _ = bl.disassemble(clone)
        self.assertFalse(bl.is_data_contract(clone, ins, dests))

    def test_data_contracts_report_no_facts_and_no_selectors(self):
        import hashlib
        blob = b'\x00' + b''.join(hashlib.sha256(i.to_bytes(2, 'big')).digest() for i in range(300))
        rec = bl.analyze_code('0x' + '11' * 20, '0x' + blob.hex())
        self.assertTrue(rec['is_data'])
        self.assertEqual(rec['facts'], {})
        self.assertEqual(rec['selectors_in'], [])
        self.assertEqual(rec['addresses'], [])


class Metadata(unittest.TestCase):
    def test_solc_version_and_split(self):
        code = bytes.fromhex('6080604052') + b'\xa2\x64ipfs' + b'X\x22\x12\x20' + b'\x11' * 32 + b'\x64solc\x43\x00\x08\x1a\x00\x33'
        runtime, meta = bl.split_metadata(code)
        self.assertEqual(runtime, bytes.fromhex('6080604052'))
        self.assertEqual(bl.compiler_of(meta, code), 'solc 0.8.26')

    def test_no_metadata_is_reported_as_none(self):
        runtime, meta = bl.split_metadata(bytes.fromhex('60806040523d3dfd'))
        self.assertEqual(meta, b'')
        self.assertIsNone(bl.compiler_of(meta, runtime))


class Authorizations(unittest.TestCase):
    def test_created_address_matches_the_known_vector(self):
        """keccak(rlp([sender, nonce]))[12:] — the standard example from the yellow paper's CREATE rule."""
        self.assertEqual(bl.rlp_created('0x6ac7ea33f8831ea9dcc53393aaa88b25a785dbf0', 0),
                         '0xcd234a471b72ba2f1ccf0a70fcaba648a5eecd8d')

    def test_authority_recovery_matches_a_real_mainnet_authorization(self):
        """A pinned mainnet tuple, and the address it must produce.

        This test exists because the round-trip version of it passed while the implementation was wrong. The digest
        omitted EIP-7702's `MAGIC = 0x05`; signing and recovering with the same wrong digest agrees with itself
        perfectly, and every authority recovered from a real transaction came out a uniformly random address. The
        authorization below is from Ethereum block 25,928,454, tx 0x067f8994…566d2, and the account it names carries
        `0xef0100 || 0xe6b97aa1…43ed` on chain — so this vector fails the moment the digest changes shape again.
        """
        try:
            import coincurve  # noqa: F401
        except ImportError:
            self.skipTest('coincurve not installed')
        got = bl.recover_authority({
            'chainId': '0x1', 'address': '0xe6b97aa1490c93c28a14d86c13c9dc9c950643ed', 'nonce': '0x13c',
            'r': '0xc1e860d8d121f544768c966f24e0a3798f9edf1177845517c2c1bbd09fa402f0',
            's': '0x11bc7dd9fd400b21ae741adc482914faa29011d927fad2c8f6f519d059e2a9c3',
            'yParity': '0x1'})
        self.assertEqual(got, '0xd4370f94d0602e4889ef74ea832d98e06a087b9e')

    def test_authority_recovery_round_trips(self):
        """Necessary but not sufficient: it agrees with itself. See the mainnet vector above for the real check."""
        try:
            from coincurve import PrivateKey
        except ImportError:
            self.skipTest('coincurve not installed')
        pk = PrivateKey.from_int(0x4646464646464646464646464646464646464646464646464646464646464646)
        who = '0x' + bl.keccak_hex(pk.public_key.format(compressed=False)[1:])[24:]
        delegate = '0x00000000219ab540356cbb839cbe05303d7705fa'
        sig = pk.sign_recoverable(bl.auth_digest(1, delegate, 7), hasher=None)
        got = bl.recover_authority({'chainId': '0x1', 'address': delegate, 'nonce': '0x7',
                                    'r': '0x' + sig[:32].hex(), 's': '0x' + sig[32:64].hex(),
                                    'yParity': hex(sig[64])})
        self.assertEqual(got, who)

    def test_magic_byte_is_present_in_the_digest(self):
        """Pin the exact byte string that is hashed, so dropping MAGIC cannot pass silently again."""
        d_with = bl.auth_digest(1, '0x' + '11' * 20, 3)
        payload = bl.rlp_int(1) + b'\x94' + b'\x11' * 20 + bl.rlp_int(3)
        expect = bytes.fromhex(bl.keccak_hex(b'\x05' + bytes([0xc0 + len(payload)]) + payload))
        self.assertEqual(d_with, expect)
        without = bytes.fromhex(bl.keccak_hex(bytes([0xc0 + len(payload)]) + payload))
        self.assertNotEqual(d_with, without)


class Facts(unittest.TestCase):
    def test_tx_origin_authorisation_is_detected(self):
        code = bl.to_bytes(asm('32', push32(Addresses.OP[2:]), '14', '61', '0089', '57'))
        ins, _, _ = bl.disassemble(code)
        facts = bl.extract_facts(code, ins, {})
        self.assertIn('origin_auth', facts)

    def test_a_plain_caller_check_is_not_tx_origin_auth(self):
        code = bl.to_bytes(asm('33', push32(Addresses.OP[2:]), '14', '61', '0089', '57'))
        ins, _, _ = bl.disassemble(code)
        facts = bl.extract_facts(code, ins, {})
        self.assertNotIn('origin_auth', facts)
        self.assertIn('caller_pin', facts)

    def test_shape_of_a_dispatcherless_body(self):
        code = bl.to_bytes('0x' + '5b' * 600)
        ins, dests, _ = bl.disassemble(code)
        self.assertTrue(bl.shape_of(code, ins, {}, {}, 0, dests).startswith('no-dispatcher'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
