#!/usr/bin/env python3
"""Read a window's contracts from their bytecode: disassemble, resolve the proxy, and hand the LLM a packet it can judge.

Every other reader in this repo works from *events* — a contract is whatever its Transfer logs say it is. That is blind
to three things at once: a contract that emits nothing, a contract whose logs lie, and the code path that only fires
under a condition the window did not happen to hit. Bytecode does not have those blind spots. It is also always
available: `eth_getCode` answers for unverified contracts, for contracts whose source was verified against a different
compiler, and for the 0-byte-source bots that do most of the interesting work on this chain.

The instrument is four stages, each independently replayable:

  census   which contracts the window even contains — every top-level CREATE (address derived offline from sender+nonce,
           no traces needed), every EIP-7702 delegate authorized in the window, and the addresses the window actually
           spent gas on. Pure offline read of raw/blocks.
  fetch    `eth_getCode` for each, then FOLLOW THE PROXY: EIP-1167 clones (and the push0/Solady variants) read the
           implementation straight out of the runtime bytes; EIP-1967 / EIP-1822 / zeppelinos / Safe read it from the
           storage slot; EIP-2535 diamonds are asked for their facets; EIP-7702 delegations are the `0xef0100` prefix.
           A proxy whose logic is not followed is a contract read as its own dispatcher, which is worse than no read.
  analyze  a full linear-sweep disassembly (PUSH-aware, so PUSH data is never mistaken for code) into: the dispatcher's
           inbound selectors, the selectors it CALLS on other contracts, hardcoded addresses (joined to the repo's
           address book), embedded strings, compiler metadata, an opcode histogram, and ~30 structural facts —
           SELFDESTRUCT, DELEGATECALL, CREATE2, EXTCODECOPY, transient storage, tx.origin auth, COINBASE payment,
           storage-gated transfer paths. Each fact carries the pcs that produced it, so the LLM can be checked.
  packets  the compact evidence packet per contract: facts + selectors + strings + what it did in the window + verified
           source when Etherscan has it. Small enough that dozens fit in one context; specific enough to be wrong.

The verdict stage is deliberately not automated away. `verdicts` takes the LLM's JSON back and re-checks the parts of it
that are falsifiable — claimed selectors must exist in the dispatcher, claimed addresses must appear as immediates,
claimed behaviour must appear in the window — and marks the rest as unverified opinion. A verdict that cannot be checked
is still allowed; it is just labelled.

    uv run python scripts/bytecode_lens.py census  --out research/2026-09-08/live_10h
    uv run python scripts/bytecode_lens.py fetch   --out research/2026-09-08/live_10h
    uv run python scripts/bytecode_lens.py analyze --out research/2026-09-08/live_10h
    uv run python scripts/bytecode_lens.py packets --out research/2026-09-08/live_10h --top 40
    uv run python scripts/bytecode_lens.py one --address 0x...            # ad-hoc, no window needed
"""
import argparse
import collections
import gzip
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------------------------------------------------
# opcodes
# ---------------------------------------------------------------------------------------------------------------------
# name, immediate bytes. Covers Cancun/Prague (PUSH0, TLOAD/TSTORE, MCOPY, BLOBHASH, BLOBBASEFEE) and names the EOF
# opcodes so an EOF container is described rather than silently decoded as garbage.
OPS = {
    0x00: 'STOP', 0x01: 'ADD', 0x02: 'MUL', 0x03: 'SUB', 0x04: 'DIV', 0x05: 'SDIV', 0x06: 'MOD', 0x07: 'SMOD',
    0x08: 'ADDMOD', 0x09: 'MULMOD', 0x0a: 'EXP', 0x0b: 'SIGNEXTEND',
    0x10: 'LT', 0x11: 'GT', 0x12: 'SLT', 0x13: 'SGT', 0x14: 'EQ', 0x15: 'ISZERO', 0x16: 'AND', 0x17: 'OR',
    0x18: 'XOR', 0x19: 'NOT', 0x1a: 'BYTE', 0x1b: 'SHL', 0x1c: 'SHR', 0x1d: 'SAR',
    0x20: 'KECCAK256',
    0x30: 'ADDRESS', 0x31: 'BALANCE', 0x32: 'ORIGIN', 0x33: 'CALLER', 0x34: 'CALLVALUE', 0x35: 'CALLDATALOAD',
    0x36: 'CALLDATASIZE', 0x37: 'CALLDATACOPY', 0x38: 'CODESIZE', 0x39: 'CODECOPY', 0x3a: 'GASPRICE',
    0x3b: 'EXTCODESIZE', 0x3c: 'EXTCODECOPY', 0x3d: 'RETURNDATASIZE', 0x3e: 'RETURNDATACOPY', 0x3f: 'EXTCODEHASH',
    0x40: 'BLOCKHASH', 0x41: 'COINBASE', 0x42: 'TIMESTAMP', 0x43: 'NUMBER', 0x44: 'PREVRANDAO', 0x45: 'GASLIMIT',
    0x46: 'CHAINID', 0x47: 'SELFBALANCE', 0x48: 'BASEFEE', 0x49: 'BLOBHASH', 0x4a: 'BLOBBASEFEE',
    0x50: 'POP', 0x51: 'MLOAD', 0x52: 'MSTORE', 0x53: 'MSTORE8', 0x54: 'SLOAD', 0x55: 'SSTORE', 0x56: 'JUMP',
    0x57: 'JUMPI', 0x58: 'PC', 0x59: 'MSIZE', 0x5a: 'GAS', 0x5b: 'JUMPDEST', 0x5c: 'TLOAD', 0x5d: 'TSTORE',
    0x5e: 'MCOPY', 0x5f: 'PUSH0',
    0xa0: 'LOG0', 0xa1: 'LOG1', 0xa2: 'LOG2', 0xa3: 'LOG3', 0xa4: 'LOG4',
    0xd0: 'DATALOAD', 0xd1: 'DATALOADN', 0xd2: 'DATASIZE', 0xd3: 'DATACOPY',
    0xe0: 'RJUMP', 0xe1: 'RJUMPI', 0xe2: 'RJUMPV', 0xe3: 'CALLF', 0xe4: 'RETF', 0xe5: 'JUMPF',
    0xe6: 'DUPN', 0xe7: 'SWAPN', 0xe8: 'EXCHANGE', 0xec: 'EOFCREATE', 0xee: 'RETURNCODE',
    0xf0: 'CREATE', 0xf1: 'CALL', 0xf2: 'CALLCODE', 0xf3: 'RETURN', 0xf4: 'DELEGATECALL', 0xf5: 'CREATE2',
    0xf7: 'RETURNDATALOAD', 0xf8: 'EXTCALL', 0xf9: 'EXTDELEGATECALL', 0xfa: 'STATICCALL', 0xfb: 'EXTSTATICCALL',
    0xfd: 'REVERT', 0xfe: 'INVALID', 0xff: 'SELFDESTRUCT',
}
for _i in range(1, 33):
    OPS[0x5f + _i] = 'PUSH%d' % _i
for _i in range(1, 17):
    OPS[0x7f + _i] = 'DUP%d' % _i
    OPS[0x8f + _i] = 'SWAP%d' % _i

PUSH_LO, PUSH_HI = 0x60, 0x7f
TERMINATORS = {'STOP', 'RETURN', 'REVERT', 'INVALID', 'SELFDESTRUCT', 'JUMP'}


class Ins:
    """One decoded instruction: program counter, opcode byte, mnemonic, immediate bytes."""
    __slots__ = ('pc', 'op', 'name', 'imm')

    def __init__(self, pc, op, name, imm):
        self.pc, self.op, self.name, self.imm = pc, op, name, imm

    @property
    def val(self):
        return int.from_bytes(self.imm, 'big') if self.imm else None

    def __repr__(self):
        return '%04x %s%s' % (self.pc, self.name, ' 0x' + self.imm.hex() if self.imm else '')


def to_bytes(code_hex):
    if not code_hex or not isinstance(code_hex, str):
        return b''
    h = code_hex[2:] if code_hex.startswith('0x') else code_hex
    if len(h) % 2:
        h = h[:-1]
    try:
        return bytes.fromhex(h)
    except ValueError:
        return b''


def disassemble(code, stop_at=None):
    """Linear sweep, PUSH-aware. Returns (instructions, jumpdests, undecodable_bytes).

    Linear sweep is the honest choice here: a recursive-descent walk would need a stack model to follow computed jumps,
    and every wrong guess silently drops a function. Sweeping decodes some data as code, which shows up as `INVALID`
    density — reported rather than hidden.
    """
    ins, dests, bad = [], set(), 0
    i, n = 0, len(code) if stop_at is None else min(stop_at, len(code))
    while i < n:
        op = code[i]
        name = OPS.get(op)
        if name is None:
            bad += 1
            ins.append(Ins(i, op, 'UNKNOWN_%02x' % op, b''))
            i += 1
            continue
        if PUSH_LO <= op <= PUSH_HI:
            k = op - 0x5f
            imm = code[i + 1:i + 1 + k]
            ins.append(Ins(i, op, name, imm))
            i += 1 + k
        else:
            if name == 'JUMPDEST':
                dests.add(i)
            ins.append(Ins(i, op, name, b''))
            i += 1
    return ins, dests, bad


# ---------------------------------------------------------------------------------------------------------------------
# metadata / normalisation
# ---------------------------------------------------------------------------------------------------------------------
CBOR_MARKERS = (b'\xa2\x64ipfs', b'\xa1\x65bzzr', b'\xa2\x65bzzr', b'\xa3\x64ipfs')


def split_metadata(code):
    """(runtime, metadata) using the CBOR trailer's own 2-byte length, falling back to the marker search."""
    if len(code) > 2:
        ln = int.from_bytes(code[-2:], 'big')
        if 0 < ln < len(code) - 2:
            cand = code[-2 - ln:-2]
            if any(cand.startswith(m[:2]) for m in (b'\xa1', b'\xa2', b'\xa3')) and (b'ipfs' in cand or b'bzzr' in cand or b'solc' in cand):
                return code[:-2 - ln], cand
    for m in CBOR_MARKERS:
        idx = code.rfind(m)
        if idx > 0:
            return code[:idx], code[idx:]
    return code, b''


def compiler_of(meta, code):
    """Compiler version out of the CBOR trailer: `solc` + 3 version bytes, or the vyper/solc text form."""
    blob = meta or code
    m = re.search(rb'solc\x43(...)', blob, re.S)
    if m:
        return 'solc %d.%d.%d' % tuple(m.group(1))
    m = re.search(rb'solc\x78.([0-9][\x20-\x7e]{2,20})', blob, re.S)
    if m:
        return 'solc ' + m.group(1).decode('ascii', 'replace')
    m = re.search(rb'vyper\x83(...)', blob, re.S)
    if m:
        return 'vyper %d.%d.%d' % tuple(m.group(1))
    if re.search(rb'vyper', blob):
        return 'vyper'
    return None


def logic_hash(code_hex):
    """Metadata stripped, PUSH20 immediates zeroed, keccak. Forks differing only in hardcoded addresses collide here.

    Same normalisation as `bytecode_fingerprint.norm_codehash`, so hashes are comparable across the two tools.
    """
    from bytecode_fingerprint import norm_codehash
    h = norm_codehash(code_hex)
    return h[:16] if h else None


def code_hash(code):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256)
    k.update(code)
    return '0x' + k.hexdigest()


def keccak_hex(s):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256)
    k.update(s.encode() if isinstance(s, str) else s)
    return k.hexdigest()


def selector_of(sig):
    return '0x' + keccak_hex(sig)[:8]


# ---------------------------------------------------------------------------------------------------------------------
# dispatcher: which selectors the contract answers, and which it calls on others
# ---------------------------------------------------------------------------------------------------------------------
DECIDERS = {'EQ', 'GT', 'LT', 'SUB', 'XOR'}
MASKS = {'0xffffffff', '0x00000000'}


CALL_OPS = {'CALL', 'STATICCALL', 'DELEGATECALL', 'CALLCODE', 'EXTCALL', 'EXTSTATICCALL', 'EXTDELEGATECALL'}


def scan_selectors(ins):
    """Split the PUSH4 immediates into inbound (dispatcher), outbound (call encoding) and custom-error selectors.

    A dispatcher entry is `... PUSH4 <sel> {EQ|GT|LT|SUB|XOR} ... PUSHn <dest> JUMPI`: solc's linear compare, solc's
    --via-ir binary search (whose pivots are real selectors too), and vyper's XOR form all take that shape.

    A PUSH4 that reaches an MSTORE is a selector being written into memory — but that is two different things wearing
    one shape. `PUSH4 <sel> PUSH1 0xe0 SHL … MSTORE … CALL` encodes an outbound call; `… MSTORE … REVERT` encodes a
    Solidity custom error. Whichever of CALL or REVERT the code reaches first decides which, because telling a reader
    that a contract *calls* `WhoAreYou()` on a counterparty, when it in fact *reverts* with that error, invents a
    dependency that is not there.
    """
    inbound, outbound, errors, other = {}, set(), set(), set()
    for i, x in enumerate(ins):
        if x.name != 'PUSH4':
            continue
        sel = '0x' + x.imm.hex()
        if sel in MASKS:
            continue
        nxt = ins[i + 1:i + 8]
        names = [o.name for o in nxt]
        if names and names[0] == 'AND':                      # a calldata mask, not a selector
            other.add(sel)
            continue
        decides = any(n in DECIDERS for n in names[:3])
        jumpi = 'JUMPI' in names
        if decides and jumpi:
            dest = None
            for j, o in enumerate(nxt):
                if o.name.startswith('PUSH') and o.imm and j + 1 < len(nxt) and nxt[j + 1].name == 'JUMPI':
                    dest = o.val
            inbound[sel] = dest
        elif 'MSTORE' in names[:6] and not jumpi:
            (errors if _reverts_first(ins, i) else outbound).add(sel)
        else:
            other.add(sel)
    # PUSH32 <sel><28 zero bytes> is the other common outbound encoding
    for x in ins:
        if x.name == 'PUSH32' and len(x.imm) == 32 and x.imm[4:] == b'\x00' * 28 and x.imm[:4] != b'\x00' * 4:
            outbound.add('0x' + x.imm[:4].hex())
    outbound = {s for s in outbound if s not in MASKS and plausible_selector(s)}
    errors = {s for s in errors if s not in MASKS and plausible_selector(s)}
    return inbound, outbound, errors, other - set(inbound) - outbound - errors


def _reverts_first(ins, i, window=70):
    """Does this memory-written selector reach a REVERT before it reaches a CALL? Then it is a custom error."""
    for o in ins[i + 1:i + 1 + window]:
        if o.name == 'REVERT':
            return True
        if o.name in CALL_OPS:
            return False
    return False


def plausible_selector(sel):
    """A selector is the first 4 bytes of a keccak hash, so it looks random. These do not:

    an all-printable word (`0x636f756e` is the ASCII "coun" of an embedded string), and a value with two or more
    trailing zero bytes (`0x19010000` is the EIP-712 prefix; a real selector lands there once in 65,536). Inbound
    selectors are never filtered — the dispatcher's own comparison is proof enough.
    """
    b = bytes.fromhex(sel[2:])
    if all(0x20 <= c <= 0x7e for c in b):
        return False
    if b[-2:] == b'\x00\x00':
        return False
    return True


def scan_topics(ins):
    """PUSH32 immediates that are reached by a LOG* — the event topics the contract can emit."""
    topics = set()
    for i, x in enumerate(ins):
        if x.name == 'PUSH32' and len(x.imm) == 32 and x.imm[:4] != b'\x00' * 4 and x.imm[28:] != b'\x00' * 4:
            for o in ins[i + 1:i + 12]:
                if o.name.startswith('LOG'):
                    topics.add('0x' + x.imm.hex())
                    break
    return topics


ZERO_ADDR = '0x' + '0' * 40


def scan_addresses(ins):
    """Address immediates, in first-seen order (dedup, zero/max dropped).

    Both encodings count. solc emits a hardcoded address as PUSH20 when it is used directly, but as a zero-padded
    PUSH32 when it is compared against a masked value — which is exactly the shape an authorisation check takes. A
    scanner that reads only PUSH20 therefore misses precisely the addresses that gate the contract.
    """
    seen, out = set(), []
    for x in ins:
        if x.name == 'PUSH32' and len(x.imm) == 32 and x.imm[:12] == b'\x00' * 12 and x.imm[12:] != b'\x00' * 20:
            a = '0x' + x.imm[12:].hex()
            if a not in seen and x.imm[12:] != b'\xff' * 20:
                seen.add(a)
                out.append(a)
            continue
        if x.name != 'PUSH20' or len(x.imm) != 20:
            continue
        a = '0x' + x.imm.hex()
        if a == ZERO_ADDR or x.imm == b'\xff' * 20 or a in seen:
            continue
        # a PUSH20 whose top bytes are zero is far more likely a number than an address, and one that is entirely
        # printable ASCII is a slice of an embedded revert string that happened to be pushed 20 bytes at a time
        if x.imm[0] == 0 and x.imm[1] == 0 and x.imm[2] == 0:
            continue
        if sum(1 for c in x.imm if 0x20 <= c <= 0x7e) >= 18:
            continue
        seen.add(a)
        out.append(a)
    return out


PRINTABLE = re.compile(rb'[\x20-\x7e]{6,}')
WORD = re.compile(r'[A-Za-z]{3,}')
SANE = re.compile(r"[A-Za-z0-9 .,:;_/@'()\[\]{}!?%$#&*+=<>|~^\\-]")
ALPHA_RUN = re.compile(r'[A-Za-z]+')
VOWELS = set('aeiou')


def _word_shaped(s, min_run):
    """Does any alphabetic run in `s` look like a word rather than a run of opcode mnemonics?

    POP is 'P', JUMP/JUMPDEST is 'V[' and PUSH2 is 'a', so compiled Solidity emits printable runs like `V[PPPPPV['`
    and `a'iWa'ha$EV[` by the hundred. A real word has a vowel, and is either all-caps (`ZERO_TGT`, `BAD_SIG`) or
    mostly lower case (`Executor`, `insufficient`); the opcode runs are neither.
    """
    for m in ALPHA_RUN.finditer(s):
        r = m.group()
        if not (set(r.lower()) & VOWELS):
            continue
        if r.isupper() and len(r) >= 3:
            return True
        if len(r) >= min_run and sum(1 for c in r if c.islower()) / len(r) >= 0.6:
            return True
    return False


def _looks_like_text(s, strict):
    """Is this printable run a string a human wrote, or an accident of the opcode alphabet?"""
    if not s or len(SANE.findall(s)) / len(s) < 0.75:
        return False
    if not _word_shaped(s, 4 if strict else 3):
        return False
    return not strict or len(s) >= 8 or ':' in s or ' ' in s


def scan_strings(code, ins=None, limit=40):
    """Embedded text: PUSH immediates first (those are data by construction), then the raw printable runs."""
    out, seen = [], set()

    def offer(s, strict):
        s = s.strip('\x00').strip()
        if len(s) < 4 or s in seen or not _looks_like_text(s, strict):
            return
        seen.add(s)
        out.append(s)

    for x in (ins or []):
        if not x.imm or len(x.imm) < 4:
            continue
        b = x.imm.strip(b'\x00')
        if len(b) >= 4 and all(0x20 <= c <= 0x7e for c in b):
            offer(b.decode('ascii', 'replace'), strict=False)
    for m in PRINTABLE.finditer(code):
        offer(m.group().decode('ascii', 'replace'), strict=True)
        if len(out) >= limit:
            break
    return out[:limit]


# ---------------------------------------------------------------------------------------------------------------------
# structural facts
# ---------------------------------------------------------------------------------------------------------------------
def _pcs(ins, names, limit=6):
    return ['%04x' % x.pc for x in ins if x.name in names][:limit]


def _near(ins, anchor, targets, window=8):
    """pcs where an `anchor` opcode is followed within `window` instructions by any of `targets`."""
    hits = []
    for i, x in enumerate(ins):
        if x.name != anchor:
            continue
        if any(o.name in targets for o in ins[i + 1:i + 1 + window]):
            hits.append('%04x' % x.pc)
    return hits


def extract_facts(code, ins, hist):
    """~30 structural facts, each with the pcs that produced it. Evidence, not adjectives."""
    f = {}

    def add(key, pcs, note):
        if pcs:
            f[key] = {'pcs': pcs[:6], 'n': len(pcs), 'note': note}

    add('selfdestruct', _pcs(ins, {'SELFDESTRUCT'}), 'can destroy itself / force-send its balance')
    add('delegatecall', _pcs(ins, {'DELEGATECALL', 'EXTDELEGATECALL'}), 'executes another contract in its own storage')
    add('callcode', _pcs(ins, {'CALLCODE'}), 'deprecated CALLCODE')
    add('create', _pcs(ins, {'CREATE'}), 'deploys child contracts')
    add('create2', _pcs(ins, {'CREATE2', 'EOFCREATE'}), 'deploys at a precomputed address (counterfactual / metamorphic)')
    add('extcodecopy', _pcs(ins, {'EXTCODECOPY'}), 'copies another contract\'s code (clone factory or code check)')
    add('extcodesize', _pcs(ins, {'EXTCODESIZE'}), 'checks whether a caller is a contract')
    add('extcodehash', _pcs(ins, {'EXTCODEHASH'}), 'pins a counterparty by its exact code')
    add('transient_storage', _pcs(ins, {'TLOAD', 'TSTORE'}), 'transient storage (EIP-1153): reentrancy locks, flash accounting')
    add('mcopy', _pcs(ins, {'MCOPY'}), 'EIP-5656 memory copy (solc >= 0.8.25 / hand-written)')
    add('blob', _pcs(ins, {'BLOBHASH', 'BLOBBASEFEE'}), 'reads blob state')
    add('origin_auth', _near(ins, 'ORIGIN', {'EQ', 'SUB', 'XOR'}, 6), 'authorises on tx.origin')
    add('coinbase_pay', _near(ins, 'COINBASE', {'CALL', 'SELFBALANCE', 'BALANCE'}, 12), 'pays or reads the block builder (MEV)')
    add('timestamp_gate', _near(ins, 'TIMESTAMP', {'GT', 'LT', 'EQ'}, 5), 'branches on block.timestamp (deadline or window)')
    add('number_gate', _near(ins, 'NUMBER', {'GT', 'LT', 'EQ'}, 5), 'branches on block.number')
    add('gasprice_gate', _near(ins, 'GASPRICE', {'GT', 'LT', 'EQ'}, 5), 'branches on gas price (anti-frontrun or bribe sizing)')
    add('caller_pin', _near(ins, 'CALLER', {'EQ', 'SUB', 'XOR'}, 4), 'compares msg.sender against a stored/hardcoded value')
    add('balance_self', _pcs(ins, {'SELFBALANCE'}), 'reads its own ETH balance')
    add('static_only', _pcs(ins, {'STATICCALL', 'EXTSTATICCALL'}), 'makes read-only calls')
    add('chainid', _pcs(ins, {'CHAINID'}), 'reads chain id (EIP-712 domain or replay guard)')
    add('prevrandao', _pcs(ins, {'PREVRANDAO'}), 'reads PREVRANDAO (randomness / lottery)')
    add('blockhash', _pcs(ins, {'BLOCKHASH'}), 'reads a block hash (randomness / proof)')

    sload_revert = []
    for i, x in enumerate(ins):
        if x.name != 'SLOAD':
            continue
        seg = ins[i + 1:i + 14]
        if any(o.name == 'REVERT' for o in seg) and any(o.name in ('JUMPI', 'ISZERO') for o in seg):
            sload_revert.append('%04x' % x.pc)
    add('storage_gated_revert', sload_revert, 'reverts on a storage flag: pause, blocklist, or a trading switch')

    calls = hist.get('CALL', 0) + hist.get('STATICCALL', 0) + hist.get('DELEGATECALL', 0) + hist.get('EXTCALL', 0)
    if calls:
        f['outbound_calls'] = {'pcs': [], 'n': calls, 'note': 'call sites in the code'}
    if hist.get('SSTORE', 0) == 0 and len(ins) > 200:
        f['stateless'] = {'pcs': [], 'n': 0, 'note': 'never writes storage: a router, a lens, or a pure library'}
    return f


MAGIC = [(b'\x1f\x8b', 'gzip'), (b'PK\x03\x04', 'zip'), (b'\x89PNG', 'png'), (b'\xff\xd8\xff', 'jpeg'),
         (b'%PDF', 'pdf'), (b'GIF8', 'gif'), (b'BZh', 'bzip2'), (b'\xfd7zXZ', 'xz'), (b'RIFF', 'riff'),
         (b'<svg', 'svg'), (b'{"', 'json'), (b'\x00asm', 'wasm'), (b'\x28\xb5\x2f\xfd', 'zstd')]


def data_payload(code):
    """If this body is data rather than a program, name the format when its magic bytes give it away."""
    head = code[1:9] if code[:1] == b'\x00' else code[:8]
    for sig, name in MAGIC:
        if head.startswith(sig):
            return name
    return None


def is_data_contract(code, ins, dests):
    """Is this contract *data* stored as code — SSTORE2 and friends — rather than a program?

    The three highest-scoring contracts in the first sweep of this window were 13–24 KB bodies that claimed every
    capability at once: SELFDESTRUCT, CALLCODE, CREATE2, transient storage, blob reads, six sites each. They were
    nothing of the kind. A linear sweep over high-entropy bytes produces every opcode in proportion to its byte
    frequency, so 22 KB of stored data disassembles into 595 SELFDESTRUCTs and a `hardcoded address` of
    `0x39a93c48a99848a96848a90448a9a048a9024820`. One of them begins `0x00 1f 8b 08` — a STOP byte and then the gzip
    magic number.

    Byte entropy does not separate the two cleanly (compiled Solidity is itself dense). JUMPDEST density does, and by a
    wide margin: across the 1,072 bodies of the 2026-09-08 window, the 13 carrying the leading-STOP marker top out at
    0.57% JUMPDEST-per-instruction while ordinary code reaches 4.88% at its 10th percentile. Nothing lands in between,
    so the cut is at 1% — clear of both sides, and it catches one further blob that carries no STOP marker at all.
    """
    if len(code) <= 256:
        return False
    return len(dests) / max(1, len(ins)) < 0.01


DISPATCHER_PROLOGUE = ('CALLDATASIZE', 'CALLDATALOAD')


def shape_of(code, ins, inbound, hist, bad, dests):
    """The one-line shape: what kind of thing this bytecode is, before anyone reads a name."""
    n = len(code)
    if n == 0:
        return 'empty'
    if is_data_contract(code, ins, dests):
        fmt = data_payload(code)
        return 'data stored as code (%s%d bytes, %s)' % (fmt + ', ' if fmt else '', n,
                                                         'leading STOP' if code[:1] == b'\x00' else 'no jump targets')
    if n <= 64 and b'\x5a\xf4' in code:
        return 'minimal-proxy'
    if code[:3] == b'\xef\x01\x00':
        return 'eip7702-delegation'
    if code[:2] == b'\xef\x00':
        return 'eof-container'
    if len(inbound) == 0:
        return 'no-dispatcher (bespoke / fallback-only)' if n > 500 else 'tiny (%d bytes, no dispatcher)' % n
    if len(inbound) <= 2 and n > 2000:
        return 'near-dispatcherless (%d selectors, %d bytes)' % (len(inbound), n)
    if hist.get('DELEGATECALL', 0) and len(inbound) <= 3 and n < 1200:
        return 'proxy'
    if bad > max(20, len(ins) * 0.25):
        return 'mostly data / packed'
    return 'ordinary dispatcher (%d selectors)' % len(inbound)


# ---------------------------------------------------------------------------------------------------------------------
# selector names
# ---------------------------------------------------------------------------------------------------------------------
KNOWN_SIGS = """
name() symbol() decimals() totalSupply() balanceOf(address) transfer(address,uint256)
transferFrom(address,address,uint256) approve(address,uint256) allowance(address,address)
increaseAllowance(address,uint256) decreaseAllowance(address,uint256) mint(address,uint256) burn(uint256)
burnFrom(address,uint256) permit(address,address,uint256,uint256,uint8,bytes32,bytes32) nonces(address) DOMAIN_SEPARATOR()
owner() transferOwnership(address) renounceOwnership() pendingOwner() acceptOwnership()
hasRole(bytes32,address) grantRole(bytes32,address) revokeRole(bytes32,address) DEFAULT_ADMIN_ROLE()
pause() unpause() paused() setPaused(bool) blacklist(address) isBlacklisted(address) setFee(uint256) setTaxes(uint256,uint256)
implementation() upgradeTo(address) upgradeToAndCall(address,bytes) proxiableUUID() admin() changeAdmin(address)
facets() facetAddresses() facetAddress(bytes4) diamondCut((address,uint8,bytes4[])[],address,bytes)
masterCopy() setup(address[],uint256,address,bytes,address,address,uint256,address) execTransaction(address,uint256,bytes,uint8,uint256,uint256,uint256,address,address,bytes)
deposit() deposit(uint256) deposit(uint256,address) withdraw(uint256) withdraw(uint256,address,address)
redeem(uint256,address,address) mint(uint256,address) asset() totalAssets() convertToShares(uint256) convertToAssets(uint256)
previewDeposit(uint256) previewRedeem(uint256) maxWithdraw(address) maxRedeem(address)
swapExactTokensForTokens(uint256,uint256,address[],address,uint256)
swapExactETHForTokens(uint256,address[],address,uint256)
swapExactTokensForTokensSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)
addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)
removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)
getReserves() token0() token1() factory() getPair(address,address) createPair(address,address) sync() skim(address)
swap(uint256,uint256,address,bytes) swap(address,bool,int256,uint160,bytes) slot0() liquidity() fee() tickSpacing()
exactInputSingle((address,address,uint24,address,uint256,uint256,uint160))
exactInput((bytes,address,uint256,uint256)) multicall(bytes[]) multicall(uint256,bytes[])
uniswapV2Call(address,uint256,uint256,bytes) uniswapV3SwapCallback(int256,int256,bytes)
pancakeV3SwapCallback(int256,int256,bytes) algebraSwapCallback(int256,int256,bytes)
unlock(bytes) unlockCallback(bytes) take(address,address,uint256) settle() sync(address)
flashLoan(address,address,uint256,bytes) flashLoanSimple(address,address,uint256,bytes)
executeOperation(address[],uint256[],uint256[],address,bytes) onFlashLoan(address,address,uint256,uint256,bytes)
supply(address,uint256,address,uint16) borrow(address,uint256,uint256,uint16,address) repay(address,uint256,uint256,address)
liquidationCall(address,address,address,uint256,bool) getReserveData(address) getUserAccountData(address)
mint(uint256) redeemUnderlying(uint256) borrowBalanceCurrent(address) exchangeRateStored() supplyRatePerBlock()
exchange(int128,int128,uint256,uint256) get_dy(int128,int128,uint256) add_liquidity(uint256[2],uint256)
handleOps((address,uint256,bytes,bytes,bytes32,uint256,bytes32,bytes,bytes)[],address)
innerHandleOp(bytes,(uint256,address,bytes32,uint256,uint256,uint256,uint256,uint256,uint256),bytes)
validateUserOp((address,uint256,bytes,bytes,bytes32,uint256,bytes32,bytes,bytes),bytes32,uint256)
execute(address,uint256,bytes) execute(bytes,bytes[]) executeBatch(address[],uint256[],bytes[])
execute((address,uint256,bytes)[]) entryPoint() isValidSignature(bytes32,bytes)
settle(address[],uint256[],(uint256,uint256,address,uint256,uint256,uint32,bytes32,uint256,bool,bytes)[],((address,uint256,bytes)[],(address,uint256,bytes)[],(address,uint256,bytes)[]))
transferAndCall(address,uint256,bytes) onTokenTransfer(address,uint256,bytes) tokensReceived(address,address,address,uint256,bytes,bytes)
safeTransferFrom(address,address,uint256) safeTransferFrom(address,address,uint256,bytes) setApprovalForAll(address,bool)
isApprovedForAll(address,address) ownerOf(uint256) tokenURI(uint256) supportsInterface(bytes4)
balanceOfBatch(address[],uint256[]) safeBatchTransferFrom(address,address,uint256[],uint256[],bytes)
withdraw(uint256,uint256) rescueTokens(address,uint256) sweep(address) sweepToken(address,uint256,address)
recoverERC20(address,uint256) claim() claimRewards() harvest() compound() rebalance() poke() update()
setImplementation(address) initialize() initialize(address) initialize(address,address) initialize(address,bytes)
receiveFlashLoan(address[],uint256[],uint256[],bytes) getAmountsOut(uint256,address[]) quote(uint256,uint256,uint256)
Error(string) Panic(uint256) depositFor(address,uint256,uint256) withdrawFrom(address,uint256,uint256) addPendingRewards(uint256) massUpdatePools()
poolLength() poolInfo(uint256) userInfo(uint256,address) emergencyWithdraw(uint256) pendingRewards(uint256,address)
"""


def known_selectors():
    m = {}
    for sig in KNOWN_SIGS.split():
        sig = sig.strip()
        if '(' in sig:
            m.setdefault(selector_of(sig), sig)
    return m


SIG_CACHE = ROOT / 'scripts' / 'selector_cache.json'


def load_sig_cache():
    if SIG_CACHE.exists():
        try:
            return json.loads(SIG_CACHE.read_text())
        except Exception:
            return {}
    return {}


def resolve_signatures(selectors, online=False, kind='function'):
    """selector -> signature, from the local table, a disk cache, and (opt-in) openchain.xyz.

    The network lookup is opt-in because a name is not evidence: it is a hint the LLM stage is allowed to use and the
    verdict stage never relies on. Everything fetched is cached to disk so a re-run is offline and identical.
    """
    import urllib.request
    out = dict(known_selectors()) if kind == 'function' else {}
    cache = load_sig_cache()
    names = {}
    unknown = []
    for s in selectors:
        if s in out:
            names[s] = out[s]
        elif s in cache:
            if cache[s]:
                names[s] = cache[s]
        else:
            unknown.append(s)
    if online and unknown:
        for i in range(0, len(unknown), 50):
            part = unknown[i:i + 50]
            url = ('https://api.openchain.xyz/signature-database/v1/lookup?filter=true&%s=' % kind) + ','.join(part)
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'llm-quant research'})
                with urllib.request.urlopen(req, timeout=25) as r:
                    d = json.loads(r.read())
                res = (d.get('result') or {}).get(kind, {})
                for s in part:
                    hits = res.get(s) or []
                    cache[s] = hits[0]['name'] if hits else ''
                    if cache[s]:
                        names[s] = cache[s]
            except Exception:
                for s in part:
                    cache.setdefault(s, '')
            time.sleep(0.25)
        SIG_CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True))
    return names


# ---------------------------------------------------------------------------------------------------------------------
# proxies
# ---------------------------------------------------------------------------------------------------------------------
SLOTS = {
    'eip1967.implementation': '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc',
    'eip1967.beacon': '0xa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6cb3582b35133d50',
    'eip1967.admin': '0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103',
    'eip1822.proxiable': '0xc5f16f0fcc639fa48a6947836d9850f504798523bf8c9a3a87d5876cf622bcf7',
    'zeppelinos.implementation': '0x7050c9e0f4ca769c69bd3a8ef740bc37934f8e2c036e5a723fd8ee048ed3f8c3',
    'safe.singleton': '0x' + '0' * 64,
}
SEL_IMPLEMENTATION = selector_of('implementation()')
SEL_MASTERCOPY = selector_of('masterCopy()')
SEL_FACET_ADDRESSES = selector_of('facetAddresses()')
SEL_CHILD_IMPL = SEL_IMPLEMENTATION


def slot_addr(word_hex):
    if not word_hex or len(word_hex) < 66:
        return None
    a = '0x' + word_hex[-40:].lower()
    return None if a == ZERO_ADDR else a


def clone_target(code):
    """The implementation baked into a minimal-proxy body, across the EIP-1167 variants.

    Any short body that DELEGATECALLs (`5af4`) and carries exactly one PUSH20 is a clone of that PUSH20, whichever
    dialect emitted it — the standard 45-byte form, the push0 form, Solady's, and the immutable-args forms all fit.
    """
    if len(code) > 200 or b'\x5a\xf4' not in code:
        return None
    ins, _, _ = disassemble(code)
    addrs = [x for x in ins if x.name == 'PUSH20' and len(x.imm) == 20 and x.imm != b'\x00' * 20]
    if len(addrs) == 1:
        return '0x' + addrs[0].imm.hex()
    return None


def _code(rpc, addr, cache):
    a = addr.lower()
    if cache is not None and a in cache:
        return cache[a]
    c = rpc.call('eth_getCode', [a, 'latest'], allow_errors=True) if rpc else None
    c = c if isinstance(c, str) and c.startswith('0x') else '0x'
    if cache is not None:
        cache[a] = c
    return c


def resolve_proxy(rpc, addr, code_hex, depth=0, seen=None, cache=None, slots=None, probes=None):
    """Follow the proxy to the code that actually runs. Returns the chain of {address, via} steps.

    Order matters. Bytecode-derived answers (EIP-7702, EIP-1167) come first, because a clone has no storage slots to
    read and a 7702 account's storage belongs to the EOA rather than the delegate. Standard slots come next. The Safe
    `slot 0` read comes last and only for a body small enough to be a proxy at all — slot 0 of an ordinary implementation
    holds an initializer flag, and reading `0x…01` as an address is how a proxy walk ends up analysing an empty account.

    Every candidate is confirmed to HAVE code before it is accepted, for the same reason.
    """
    seen = seen if seen is not None else set()
    a0 = addr.lower()
    if a0 in seen or depth > 4:
        return []
    seen.add(a0)
    code = to_bytes(code_hex)
    if cache is not None:
        cache.setdefault(a0, code_hex)

    def step(target, via, require_code=True):
        t = (target or '').lower()
        if not t or t == ZERO_ADDR or t == a0 or t in seen:
            return None
        c = _code(rpc, t, cache) if rpc is not None else '0x'
        if rpc is not None and require_code and len(c) <= 4:
            return None
        tail = resolve_proxy(rpc, t, c, depth + 1, seen, cache, slots, probes) if rpc is not None else []
        return [{'address': t, 'via': via}] + tail

    if code[:3] == b'\xef\x01\x00' and len(code) == 23:
        t = '0x' + code[3:].hex()
        return step(t, 'eip7702-delegation') or [{'address': t, 'via': 'eip7702-delegation'}]
    tgt = clone_target(code)
    if tgt:
        return step(tgt, 'eip1167-clone') or [{'address': tgt, 'via': 'eip1167-clone'}]
    if rpc is None:
        return []
    if 'DELEGATECALL' not in {x.name for x in disassemble(code)[0]}:
        return []

    # the four standard slots in one round trip: a proxy answers at most one of them, and asking separately quadrupled
    # the request count for a walk that runs over every contract in the window
    order = ('eip1967.implementation', 'eip1822.proxiable', 'zeppelinos.implementation', 'eip1967.beacon')
    if slots is not None and a0 in slots:
        mine = slots[a0]                        # prefilled by the bulk pass in `fetch`
    else:
        words = rpc.batch([('eth_getStorageAt', [a0, SLOTS[k], 'latest']) for k in order], allow_errors=True)
        mine = {k: slot_addr(w if isinstance(w, str) else None) for k, w in zip(order, words)}
    for name in order[:3]:
        r = step(mine[name], name)
        if r:
            return r
    b = mine['eip1967.beacon']
    if b and len(_code(rpc, b, cache)) > 4:
        r = rpc.call('eth_call', [{'to': b, 'data': SEL_IMPLEMENTATION}, 'latest'], allow_errors=True)
        sub = step(slot_addr(r if isinstance(r, str) else None), 'beacon.implementation()')
        if sub:
            return [{'address': b, 'via': 'eip1967.beacon'}] + sub
    # a real proxy is a small body; a 20 KB contract that happens to DELEGATECALL is a diamond or a library user, and
    # asking each of those two questions over a whole window is what gets the endpoint to start refusing
    if len(code) > 2000:
        return []
    for sel, via in ((SEL_IMPLEMENTATION, 'implementation()'), (SEL_MASTERCOPY, 'masterCopy()')):
        if probes is not None and a0 in probes:
            got = probes[a0].get(via)
        else:
            r = rpc.call('eth_call', [{'to': a0, 'data': sel}, 'latest'], allow_errors=True)
            got = slot_addr(r if isinstance(r, str) else None)
        sub = step(got, via)
        if sub:
            return sub
    if len(code) <= 256:
        if probes is not None and a0 in probes:
            got = probes[a0].get('safe.singleton(slot0)')
        else:
            w = rpc.call('eth_getStorageAt', [a0, SLOTS['safe.singleton'], 'latest'], allow_errors=True)
            got = slot_addr(w if isinstance(w, str) else None)
        sub = step(got, 'safe.singleton(slot0)')
        if sub:
            return sub
    return []


def diamond_facets(rpc, addr, inbound):
    """EIP-2535: if the dispatcher answers facetAddresses(), ask it — the real code is spread across the facets."""
    if SEL_FACET_ADDRESSES not in inbound or rpc is None:
        return []
    r = rpc.call('eth_call', [{'to': addr, 'data': SEL_FACET_ADDRESSES}, 'latest'], allow_errors=True)
    if not isinstance(r, str) or len(r) < 130:
        return []
    body = r[2:]
    n = int(body[64:128], 16)
    return ['0x' + body[128 + i * 64 + 24:128 + (i + 1) * 64] for i in range(min(n, 64))]


# ---------------------------------------------------------------------------------------------------------------------
# census: which contracts the window contains
# ---------------------------------------------------------------------------------------------------------------------
def hx(v):
    if isinstance(v, str):
        return int(v, 16)
    return int(v or 0)


def rlp_created(sender, nonce):
    """CREATE address = keccak(rlp([sender, nonce]))[12:] — derived offline, so top-level deploys need no traces.

    (CREATE2 children stay invisible without a tracing endpoint; `census` reports how many CREATE2-capable factories
    were called so the gap is visible rather than assumed away.)
    """
    a = bytes.fromhex(sender[2:])
    if nonce == 0:
        n = b'\x80'
    elif nonce < 0x80:
        n = bytes([nonce])
    else:
        b = nonce.to_bytes((nonce.bit_length() + 7) // 8, 'big')
        n = bytes([0x80 + len(b)]) + b
    payload = b'\x94' + a + n
    body = bytes([0xc0 + len(payload)]) + payload
    return '0x' + keccak_hex(body)[24:]


AUTH_MAGIC = b'\x05'


def rlp_int(n):
    if n == 0:
        return b'\x80'
    if n < 0x80:
        return bytes([n])
    b = n.to_bytes((n.bit_length() + 7) // 8, 'big')
    return bytes([0x80 + len(b)]) + b


def auth_digest(chain_id, address, nonce):
    """EIP-7702 signing digest: keccak(MAGIC || rlp([chain_id, address, nonce])), MAGIC = 0x05.

    The magic byte is not decoration. Without it the recovery still round-trips against itself — sign with the same
    wrong digest, recover the same address — while every authority recovered from a real transaction is a different,
    uniformly random address that owns nothing and matches nothing. The only test that catches that is one that checks
    a recovered authority against the chain, which is why `test_bytecode_lens` pins a real mainnet authorization.
    """
    payload = rlp_int(chain_id) + b'\x94' + bytes.fromhex(address[2:]) + rlp_int(nonce)
    body = (bytes([0xc0 + len(payload)]) if len(payload) <= 55 else
            bytes([0xf7 + (len(payload).bit_length() + 7) // 8]) + len(payload).to_bytes((len(payload).bit_length() + 7) // 8, 'big'))
    return bytes.fromhex(keccak_hex(AUTH_MAGIC + body + payload))


def recover_authority(a):
    """The EOA that actually signed a 7702 authorization tuple.

    The transaction's `from` is the *submitter* — usually a relayer paying gas for someone else's delegation, so
    counting submitters and calling them accounts is how you turn one relayer into a crowd, or a crowd into one.
    The authority is only recoverable by running ecrecover over the tuple, which is what this does.
    """
    try:
        from coincurve import PublicKey
    except ImportError:
        return None
    try:
        digest = auth_digest(hx(a.get('chainId', 0)), (a['address']).lower(), hx(a.get('nonce', 0)))
        r, sg = hx(a['r']), hx(a['s'])
        v = hx(a.get('yParity', a.get('v', 0)))
        sig = r.to_bytes(32, 'big') + sg.to_bytes(32, 'big') + bytes([v])
        pk = PublicKey.from_signature_and_message(sig, digest, hasher=None)
        return '0x' + keccak_hex(pk.format(compressed=False)[1:])[24:]
    except Exception:
        return None


class WindowScan:
    """One pass over raw/blocks + raw/logs, accumulating everything the contract census needs."""

    def __init__(self, out, limit=None):
        self.out = Path(out)
        self.raw = self.out / 'raw'
        nums = sorted(int(p.name.split('.')[0]) for p in (self.raw / 'blocks').glob('*.json.gz'))
        self.nums = nums[:limit] if limit else nums
        self.deploys = []              # top-level CREATEs
        self.auth = collections.Counter()             # 7702 delegate -> authorization count
        self.auth_submitters = collections.defaultdict(set)   # who paid the gas
        self.auth_signers = collections.defaultdict(set)      # who actually signed the delegation (ecrecover)
        self.recover = False
        self.tx_count = collections.Counter()
        self.gas = collections.Counter()
        self.value = collections.Counter()
        self.senders = collections.defaultdict(set)
        self.logs = collections.Counter()
        self.topics = collections.defaultdict(set)
        self.first_seen = {}
        self.total_gas = 0
        self.n_tx = 0

    def _read(self, kind, n):
        with gzip.open(self.raw / kind / ('%d.json.gz' % n), 'rt') as f:
            return json.load(f)

    def run(self, progress=None):
        for i, n in enumerate(self.nums):
            b = self._read('blocks', n)
            for t in b['transactions']:
                self.n_tx += 1
                g = hx(t['gas'])
                self.total_gas += g
                if t.get('to') is None:
                    addr = rlp_created(t['from'].lower(), hx(t['nonce']))
                    self.deploys.append({'address': addr, 'creator': t['from'].lower(), 'tx': t['hash'],
                                         'block': hx(t['blockNumber']), 'ts': hx(t.get('blockTimestamp', 0)),
                                         'init_bytes': max(0, (len(t.get('input', '0x')) - 2) // 2),
                                         'value_eth': hx(t.get('value', 0)) / 1e18, 'gas': g})
                else:
                    to = t['to'].lower()
                    self.tx_count[to] += 1
                    self.gas[to] += g
                    self.value[to] += hx(t.get('value', 0))
                    if len(self.senders[to]) < 4096:
                        self.senders[to].add(t['from'].lower())
                    self.first_seen.setdefault(to, hx(t['blockNumber']))
                for a in t.get('authorizationList') or []:
                    d = (a.get('address') or '').lower()
                    if d and d != ZERO_ADDR:
                        self.auth[d] += 1
                        if len(self.auth_submitters[d]) < 8192:
                            self.auth_submitters[d].add(t['from'].lower())
                        if self.recover:
                            who = recover_authority(a)
                            if who:
                                self.auth_signers[d].add(who)
            for l in self._read('logs', n):
                a = l['address'].lower()
                self.logs[a] += 1
                tp = l.get('topics') or []
                if tp and len(self.topics[a]) < 32:
                    self.topics[a].add(tp[0])
                self.first_seen.setdefault(a, n)
            if progress and i % 250 == 0:
                progress(i, len(self.nums))
        return self

    def activity(self, addr):
        a = addr.lower()
        return {'txs': self.tx_count.get(a, 0), 'gas': self.gas.get(a, 0),
                'gas_share': round(self.gas.get(a, 0) / self.total_gas, 6) if self.total_gas else 0,
                'senders': len(self.senders.get(a, ())), 'value_eth': round(self.value.get(a, 0) / 1e18, 4),
                'logs': self.logs.get(a, 0), 'topic0s': len(self.topics.get(a, ())),
                'first_block': self.first_seen.get(a)}


def cmd_census(args):
    out = Path(args.out)
    t0 = time.time()
    w = WindowScan(out, args.limit_blocks)
    w.recover = args.recover_authorities
    w.run(
        progress=lambda i, n: print('  %d/%d blocks' % (i, n), file=sys.stderr))
    cand = {}

    def offer(addr, why, extra=None):
        a = addr.lower()
        r = cand.setdefault(a, {'address': a, 'why': [], **w.activity(a)})
        if why not in r['why']:
            r['why'].append(why)
        if extra:
            r.update(extra)

    for d in w.deploys:
        offer(d['address'], 'deployed-in-window',
              {'creator': d['creator'], 'deploy_tx': d['tx'], 'deploy_block': d['block'],
               'init_bytes': d['init_bytes'], 'deploy_value_eth': round(d['value_eth'], 4)})
    for a, n in w.auth.most_common():
        offer(a, 'eip7702-delegate', {'authorizations': n, 'submitters': len(w.auth_submitters[a]),
                                      'authorities': len(w.auth_signers[a]) if w.recover else None})
    for a, _ in w.gas.most_common(args.top_gas):
        offer(a, 'top-gas')
    for a, _ in w.logs.most_common(args.top_logs):
        offer(a, 'top-logs')
    for a, _ in w.tx_count.most_common(args.top_calls):
        offer(a, 'top-calls')

    res = {'window': str(out), 'blocks': len(w.nums), 'first_block': w.nums[0], 'last_block': w.nums[-1],
           'txs': w.n_tx, 'total_gas': w.total_gas, 'deploys': len(w.deploys),
           'distinct_7702_delegates': len(w.auth), 'authorizations': sum(w.auth.values()),
           'distinct_call_targets': len(w.tx_count), 'distinct_emitters': len(w.logs),
           'candidates': sorted(cand.values(), key=lambda r: -r['gas']),
           'built_s': round(time.time() - t0, 1)}
    d = out / 'contracts'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'census.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != 'candidates'}, indent=1))
    print('candidates: %d -> %s' % (len(cand), d / 'census.json'))


# ---------------------------------------------------------------------------------------------------------------------
# fetch: code + proxy chains
# ---------------------------------------------------------------------------------------------------------------------
def open_rpc(log=None):
    from live_rpc import RPC
    return RPC(log_path=log, max_credits=2_000_000)


def cmd_fetch(args):
    out = Path(args.out)
    d = out / 'contracts'
    census = json.loads((d / 'census.json').read_text())
    addrs = [c['address'] for c in census['candidates']]
    if args.limit:
        addrs = addrs[:args.limit]
    rpc = open_rpc(out / 'rpc_errors.jsonl')
    code = {}
    # follow proxies for everything that has code; the chain's terminal address is what `analyze` reads
    chains = {}

    # Everything the proxy walk needs, asked for in bulk. The walk itself then runs offline against the answers.
    # Read per contract, these are three to six serialized round trips each and the endpoint starts throttling a few
    # hundred contracts in; batched, the whole window is a couple of hundred requests.
    def bulk(calls, label, size=args.batch, workers=args.workers):
        """Issue `calls` as concurrent JSON-RPC batches, results in request order.

        One batch of forty took forty seconds against the endpoint, so a window's few thousand reads is an hour of
        waiting on latency rather than on data. Batches are independent, the client rotates a key per batch and is
        already lock-guarded, so the fix is to have several in flight at once.
        """
        import concurrent.futures as cf
        parts = [calls[i:i + size] for i in range(0, len(calls), size)]
        got, done = [None] * len(parts), 0
        with cf.ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            futs = {ex.submit(rpc.batch, part, True): i for i, part in enumerate(parts)}
            for f in cf.as_completed(futs):
                i = futs[f]
                try:
                    got[i] = f.result()
                except Exception as e:
                    print('  %s batch %d failed: %s' % (label, i, str(e)[:80]), file=sys.stderr)
                    got[i] = [None] * len(parts[i])
                done += 1
                if done % 5 == 0 or done == len(parts):
                    print('  %s %d/%d batches' % (label, done, len(parts)), file=sys.stderr, flush=True)
        return [r for part in got for r in part]

    for a, r in zip(addrs, bulk([('eth_getCode', [a, 'latest']) for a in addrs], 'code')):
        code[a] = r if isinstance(r, str) and r.startswith('0x') else '0x'
    cache = dict(code)
    live = [a for a in addrs if len(code.get(a, '0x')) > 4]

    # Two rounds, because the answers open new questions: an implementation reached from a proxy can itself be a proxy,
    # and if its slots were not prefetched the walk falls back to one serialized read per implementation — which is the
    # slow path this whole structure exists to avoid.
    order = ('eip1967.implementation', 'eip1822.proxiable', 'zeppelinos.implementation', 'eip1967.beacon')
    slots, probes, delegating_all = {}, {}, set()
    frontier = list(live)
    for rnd in (1, 2):
        delegating = [a for a in frontier
                      if a not in slots and len(cache.get(a, '0x')) > 4
                      and 'DELEGATECALL' in {x.name for x in disassemble(to_bytes(cache[a]))[0]}]
        if not delegating:
            break
        delegating_all.update(delegating)
        slot_calls = [(a, k) for a in delegating for k in order]
        for (a, k), w in zip(slot_calls, bulk([('eth_getStorageAt', [a, SLOTS[k], 'latest']) for a, k in slot_calls],
                                              'slots r%d' % rnd)):
            slots.setdefault(a, {})[k] = slot_addr(w if isinstance(w, str) else None)

        # only a contract with no standard slot and a proxy-sized body is worth asking directly
        ask = [a for a in delegating if not any(slots.get(a, {}).values()) and len(cache[a]) <= 4002]
        probe_calls = ([(a, SEL_IMPLEMENTATION, 'implementation()') for a in ask]
                       + [(a, SEL_MASTERCOPY, 'masterCopy()') for a in ask]
                       + [(a, None, 'safe.singleton(slot0)') for a in ask if len(cache[a]) <= 514])
        for (a, _, via), r in zip(probe_calls, bulk(
                [(('eth_call', [{'to': a, 'data': sel}, 'latest']) if sel else
                  ('eth_getStorageAt', [a, SLOTS['safe.singleton'], 'latest'])) for a, sel, _ in probe_calls],
                'probes r%d' % rnd)):
            probes.setdefault(a, {})[via] = slot_addr(r if isinstance(r, str) else None)

        # every address those answers point at, plus the bytecode-derived targets, fetched before the next round
        targets = ({v for a in delegating for v in slots.get(a, {}).values() if v}
                   | {v for a in ask for v in probes.get(a, {}).values() if v}
                   | {t for a in frontier for t in [clone_target(to_bytes(cache.get(a, '0x')))] if t}
                   | {'0x' + to_bytes(cache.get(a, '0x'))[3:].hex() for a in frontier
                      if to_bytes(cache.get(a, '0x'))[:3] == b'\xef\x01\x00' and len(to_bytes(cache[a])) == 23})
        todo = sorted(t for t in targets if t not in cache)
        for t, c in zip(todo, bulk([('eth_getCode', [t, 'latest']) for t in todo], 'impl-code r%d' % rnd)):
            cache[t] = c if isinstance(c, str) and c.startswith('0x') else '0x'
        frontier = todo

    for i, a in enumerate(live):
        ch = resolve_proxy(rpc, a, code[a], cache=cache, slots=slots, probes=probes)
        if ch:
            chains[a] = ch
        if i % 200 == 0:
            print('  walk %d/%d (%d chains)' % (i, len(live), len(chains)), file=sys.stderr)
    extra = {k: v for k, v in cache.items() if k not in code}
    code.update(extra)
    with gzip.open(d / 'code.json.gz', 'wt') as f:
        json.dump(code, f)
    (d / 'proxies.json').write_text(json.dumps(chains, indent=1))
    empty = sum(1 for a in addrs if len(code.get(a, '0x')) <= 4)
    stats = {'requested': len(addrs), 'with_code': len(addrs) - empty, 'no_code_eoa': empty,
             'delegating': len(delegating_all), 'proxy_chains': len(chains), 'implementations_fetched': len(extra),
             'rpc': rpc.stats()}
    (d / 'fetch.json').write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


# ---------------------------------------------------------------------------------------------------------------------
# analyze: disassemble, score
# ---------------------------------------------------------------------------------------------------------------------
CAPABILITY_WEIGHTS = {
    'selfdestruct': 14, 'callcode': 8, 'create2': 7, 'extcodecopy': 5, 'origin_auth': 12, 'coinbase_pay': 10,
    'delegatecall': 4, 'transient_storage': 5, 'gasprice_gate': 6, 'prevrandao': 6, 'blockhash': 3,
    'storage_gated_revert': 3, 'create': 3, 'blob': 4, 'extcodehash': 2,
}


def analyze_code(addr, code_hex, activity=None, chain_hint=None):
    """Everything derivable from the bytes alone. No names, no source, no labels — those are joined in later."""
    code = to_bytes(code_hex)
    runtime, meta = split_metadata(code)
    ins, dests, bad = disassemble(runtime)
    hist = collections.Counter(x.name.rstrip('0123456789') if x.name.startswith(('PUSH', 'DUP', 'SWAP', 'LOG')) else x.name
                               for x in ins)
    inbound, outbound, errors, other = scan_selectors(ins)
    data = is_data_contract(runtime, ins, dests)
    # A linear sweep over stored data yields an opcode for every byte, so its "facts" are byte frequencies wearing
    # the names of instructions. Reporting them would be inventing capabilities out of a JPEG.
    facts = {} if data else extract_facts(runtime, ins, hist)
    rec = {
        'address': addr,
        'code_bytes': len(code),
        'runtime_bytes': len(runtime),
        'codehash': code_hash(code),
        'logic_hash': logic_hash(code_hex),
        'compiler': compiler_of(meta, code[-200:] if len(code) > 200 else code),
        'has_metadata': bool(meta),
        'shape': shape_of(runtime, ins, inbound, hist, bad, dests),
        'is_data': data,
        'data_payload': data_payload(runtime) if data else None,
        'instructions': len(ins),
        'jumpdests': len(dests),
        'undecodable': bad,
        'opcodes': dict(hist.most_common(24)),
        'selectors_in': [] if data else sorted(inbound),
        'selectors_out': [] if data else sorted(outbound),
        'selectors_error': sorted(errors),
        'selectors_other': sorted(other)[:24],
        'event_topics': [] if data else sorted(scan_topics(ins))[:24],
        'addresses': [] if data else scan_addresses(ins)[:40],
        'strings': scan_strings(runtime, ins if not data else None),
        'facts': facts,
    }
    if activity:
        rec['window'] = activity
    if chain_hint:
        rec['proxy_chain'] = chain_hint
    return rec


def score(rec, clones, labels_by_addr):
    """Rank by how much a human researcher would learn from reading it, and say why in words.

    The score is a sorting device, never a claim. Every point of it is attached to a reason string that names the
    evidence, so a packet that scores high for the wrong reason is visible as such.
    """
    pts, why = 0, []
    f = rec.get('facts', {})
    w = rec.get('window', {}) or {}
    shape = rec.get('shape', '')

    if rec.get('is_data'):
        pts = 12 + (6 if rec.get('data_payload') else 0) + min(10, rec.get('runtime_bytes', 0) // 4096)
        why = ['%d bytes of data stored as contract code%s' % (
            rec.get('runtime_bytes', 0), ', ' + rec['data_payload'] + ' payload' if rec.get('data_payload') else '')]
        if 'deployed-in-window' in (rec.get('why') or []):
            why.append('written in this window by %s' % (rec.get('creator') or 'an unknown deployer'))
        return pts, why

    for k, weight in CAPABILITY_WEIGHTS.items():
        if k in f:
            pts += weight
            why.append('%s (%d sites)' % (k, f[k]['n']))

    if shape.startswith('no-dispatcher') or shape.startswith('near-dispatcherless'):
        pts += 18
        why.append('%s: hand-written, no ABI to read' % shape.split(' ')[0])
    if not rec.get('has_metadata') and rec.get('runtime_bytes', 0) > 400:
        pts += 8
        why.append('no compiler metadata (hand-written Yul/assembly or stripped)')
    if rec.get('undecodable', 0) > max(24, rec.get('instructions', 1) * 0.3):
        pts += 4
        why.append('%d undecodable bytes: packed data or anti-disassembly' % rec['undecodable'])

    n_clone = clones.get(rec.get('logic_hash'), 1)
    if n_clone >= 8:
        pts += 6
        why.append('mass-produced: %d addresses share this logic hash' % n_clone)
    elif n_clone == 1 and rec.get('runtime_bytes', 0) > 1500:
        pts += 5
        why.append('one-off logic hash: not a known fork')

    gs = w.get('gas_share') or 0
    if gs >= 0.002:
        pts += min(20, int(gs * 2000))
        why.append('%.2f%% of window gas' % (gs * 100))
    if (w.get('senders') or 0) >= 200:
        pts += 5
        why.append('%d distinct senders' % w['senders'])
    if (w.get('value_eth') or 0) >= 100:
        pts += 5
        why.append('%.0f ETH received directly' % w['value_eth'])
    if (w.get('logs') or 0) == 0 and (w.get('txs') or 0) >= 20:
        pts += 8
        why.append('%d calls and zero logs: emits nothing an event reader can see' % w['txs'])

    if 'authorizations' in rec:
        pts += min(16, 4 + rec['authorizations'] // 8)
        why.append('EIP-7702 delegate: %d authorizations, %d submitters, %s signing EOAs' % (rec['authorizations'], rec.get('submitters', 0), rec.get('authorities') if rec.get('authorities') is not None else 'unrecovered'))
    if 'deployed-in-window' in (rec.get('why') or []):
        pts += 6
        why.append('deployed inside the window')
    if rec.get('proxy_chain'):
        why.append('proxy -> ' + ' -> '.join(s['via'] for s in rec['proxy_chain']))
    if not labels_by_addr.get(rec['address']):
        pts += 2
        why.append('unlabelled in the address book')
    else:
        why.append('labelled: ' + labels_by_addr[rec['address']]['label'])
    return pts, why


def cmd_analyze(args):
    out = Path(args.out)
    d = out / 'contracts'
    census = json.loads((d / 'census.json').read_text())
    with gzip.open(d / 'code.json.gz', 'rt') as f:
        code = json.load(f)
    chains = json.loads((d / 'proxies.json').read_text()) if (d / 'proxies.json').exists() else {}
    import labels as labels_mod
    reg = labels_mod.load()
    labels_by_addr = {k.lower(): v for k, v in reg.items()}

    by_addr = {c['address']: c for c in census['candidates']}
    recs = []
    for c in census['candidates']:
        a = c['address']
        ch = chains.get(a) or []
        target = ch[-1]['address'].lower() if ch else a
        tcode = code.get(target, code.get(a, '0x'))
        if len(tcode) <= 4:
            # a candidate with no code is an EOA that received calls, or a contract that self-destructed since
            continue
        rec = analyze_code(a, tcode, activity={k: c[k] for k in
                                              ('txs', 'gas', 'gas_share', 'senders', 'value_eth', 'logs', 'topic0s', 'first_block')
                                              if k in c},
                           chain_hint=ch)
        rec['why'] = c.get('why', [])
        rec['analyzed_address'] = target
        rec['proxy_bytes'] = (len(code.get(a, '0x')) - 2) // 2 if ch else None
        for k in ('creator', 'deploy_tx', 'deploy_block', 'init_bytes', 'authorizations', 'submitters', 'authorities'):
            if k in c:
                rec[k] = c[k]
        recs.append(rec)

    clones = collections.Counter(r['logic_hash'] for r in recs if r.get('logic_hash'))
    for r in recs:
        r['clone_count'] = clones.get(r.get('logic_hash'), 1)
        r['score'], r['score_why'] = score(r, clones, labels_by_addr)
        lb = labels_by_addr.get(r['address'])
        r['label'] = lb['label'] if lb else None
        r['label_kind'] = lb['kind'] if lb else None
    recs.sort(key=lambda r: -r['score'])

    sel_all = sorted({s for r in recs for s in r['selectors_in']} | {s for r in recs for s in r['selectors_out']}
                     | {s for r in recs for s in r.get('selectors_error', [])})
    names = resolve_signatures(sel_all, online=args.resolve_sigs)
    topics_all = sorted({t for r in recs for t in r['event_topics']})
    tnames = resolve_signatures(topics_all, online=args.resolve_sigs, kind='event')

    res = {'window': str(out), 'contracts': len(recs), 'built': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'shape_census': dict(collections.Counter(r['shape'].split(' (')[0] for r in recs).most_common()),
           'compiler_census': dict(collections.Counter(r['compiler'] or 'none/unknown' for r in recs).most_common(12)),
           'clone_clusters': [{'logic_hash': h, 'n': n} for h, n in clones.most_common(10) if n > 1],
           'selector_names': names, 'topic_names': tnames, 'records': recs}
    (d / 'analysis.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ('records', 'selector_names', 'topic_names')}, indent=1))
    print('\ntop by score:')
    for r in recs[:args.top]:
        print('  %5d %s %-34s %s' % (r['score'], r['address'], (r['label'] or '-')[:34], '; '.join(r['score_why'][:3])))


# ---------------------------------------------------------------------------------------------------------------------
# packets: the evidence the LLM reads
# ---------------------------------------------------------------------------------------------------------------------
def fetch_source(addr, chainid=1, max_chars=12000):
    try:
        import etherscan
        s = etherscan.source(chainid, addr)
    except Exception as e:
        return {'verified': False, 'error': str(e)[:80]}
    src = s.get('source') or ''
    if not src:
        return {'verified': False}
    return {'verified': True, 'name': s.get('name'), 'compiler': s.get('compiler'),
            'proxy': s.get('proxy'), 'implementation': s.get('implementation'),
            'chars': len(src), 'source': src[:max_chars]}


def packet_of(rec, names, tnames, labels_by_addr, source=None):
    """One contract, compressed to what a reader needs and nothing else."""
    def nm(s):
        return '%s %s' % (s, names.get(s, '?'))
    p = {
        'address': rec['address'],
        'analyzed': rec['analyzed_address'],
        'label': rec.get('label'),
        'why_selected': rec.get('why'),
        'score': rec['score'],
        'score_why': rec['score_why'],
        'shape': rec['shape'],
        'is_data': rec.get('is_data'),
        'data_payload': rec.get('data_payload'),
        'runtime_bytes': rec['runtime_bytes'],
        'compiler': rec['compiler'],
        'clone_count': rec['clone_count'],
        'window': rec.get('window'),
        'proxy_chain': [{'via': s['via'], 'address': s['address'], 'label': (labels_by_addr.get(s['address'].lower()) or {}).get('label')}
                        for s in (rec.get('proxy_chain') or [])],
        'facts': {k: v['note'] + ' @' + ','.join(v['pcs'][:3]) for k, v in rec['facts'].items()},
        'selectors_in': [nm(s) for s in rec['selectors_in'][:60]],
        'selectors_out': [nm(s) for s in rec['selectors_out'][:40]],
        'selectors_error': [nm(s) for s in rec.get('selectors_error', [])[:24]],
        'events': ['%s %s' % (t[:12] + '…', tnames.get(t, '?')) for t in rec['event_topics'][:16]],
        'addresses': [{'a': a, 'label': (labels_by_addr.get(a) or {}).get('label')} for a in rec['addresses'][:24]],
        'strings': rec['strings'][:24],
        'opcodes': rec['opcodes'],
    }
    for k in ('creator', 'deploy_tx', 'deploy_block', 'authorizations', 'submitters', 'authorities'):
        if k in rec:
            p[k] = rec[k]
    if source:
        p['source'] = source
    return p


def packet_md(p):
    L = ['## %s  — score %d' % (p['address'], p['score']),
         '',
         '- **shape**: %s, %d bytes, %s, %s' % (p['shape'], p['runtime_bytes'], p['compiler'] or 'no metadata',
                                                'unique logic' if p['clone_count'] == 1 else '%d clones' % p['clone_count']),
         '- **label**: %s' % (p['label'] or '_unlabelled_'),
         '- **selected because**: %s' % ', '.join(p['why_selected'] or []),
         '- **rank reasons**: %s' % '; '.join(p['score_why'])]
    w = p.get('window') or {}
    if w:
        L.append('- **window**: %d calls, %d senders, %.3f%% of gas, %s ETH in, %d logs (%d topic0s)' % (
            w.get('txs', 0), w.get('senders', 0), 100 * (w.get('gas_share') or 0), w.get('value_eth', 0),
            w.get('logs', 0), w.get('topic0s', 0)))
    if p.get('proxy_chain'):
        L.append('- **proxy**: ' + ' → '.join('%s (%s%s)' % (s['address'], s['via'], ', ' + s['label'] if s['label'] else '') for s in p['proxy_chain']))
    if p.get('authorizations'):
        L.append('- **EIP-7702**: %d authorizations in this window, %d gas-paying submitters, %s distinct signing EOAs' % (
            p['authorizations'], p.get('submitters', 0), p.get('authorities') if p.get('authorities') is not None else 'unrecovered'))
    if p.get('deploy_tx'):
        L.append('- **deployed**: block %s by %s, tx %s' % (p.get('deploy_block'), p.get('creator'), p['deploy_tx']))
    if p['facts']:
        L += ['- **facts**:'] + ['  - `%s` — %s' % (k, v) for k, v in p['facts'].items()]
    if p['selectors_in']:
        L.append('- **answers**: ' + ', '.join(p['selectors_in']))
    if p['selectors_out']:
        L.append('- **calls out**: ' + ', '.join(p['selectors_out']))
    if p.get('selectors_error'):
        L.append('- **reverts with**: ' + ', '.join(p['selectors_error']))
    if p['events']:
        L.append('- **emits**: ' + ', '.join(p['events']))
    if p['addresses']:
        L.append('- **hardcoded addresses**: ' + ', '.join('%s%s' % (a['a'], ' [%s]' % a['label'] if a['label'] else '') for a in p['addresses']))
    if p['strings']:
        L.append('- **strings**: ' + ' | '.join('`%s`' % s.replace('`', "'") for s in p['strings']))
    L.append('- **opcodes**: ' + ', '.join('%s=%d' % (k, v) for k, v in list(p['opcodes'].items())[:14]))
    src = p.get('source')
    if src and src.get('verified'):
        L += ['', '<details><summary>verified source: %s (%s, %d chars)</summary>' % (src.get('name'), src.get('compiler'), src.get('chars')),
              '', '```solidity', src['source'][:8000], '```', '</details>']
    elif src:
        L.append('- **source**: not verified on Etherscan')
    L.append('')
    return '\n'.join(L)


def cmd_packets(args):
    out = Path(args.out)
    d = out / 'contracts'
    a = json.loads((d / 'analysis.json').read_text())
    import labels as labels_mod
    labels_by_addr = {k.lower(): v for k, v in labels_mod.load().items()}
    recs = a['records']
    if args.address:
        want = {x.strip().lower() for x in args.address.split(',')}
        recs = [r for r in recs if r['address'] in want]
    else:
        recs = recs[:args.top]
    packets = []
    for i, r in enumerate(recs):
        src = None
        if args.source:
            src = fetch_source(r['analyzed_address'], args.chainid)
            time.sleep(0.22)
            if i % 10 == 0:
                print('  source %d/%d' % (i, len(recs)), file=sys.stderr)
        packets.append(packet_of(r, a['selector_names'], a['topic_names'], labels_by_addr, src))
    (d / 'packets.json').write_text(json.dumps({'window': str(out), 'n': len(packets), 'packets': packets}, indent=1))
    md = ['# Bytecode packets — %s' % out, '',
          'Built by `scripts/bytecode_lens.py`. Every line below is derived from the runtime bytecode, the window\'s raw',
          'blocks, or Etherscan\'s verified source — nothing here is a guess. `?` after a selector means no signature is',
          'known for it locally.', '']
    md += [packet_md(p) for p in packets]
    (d / 'packets.md').write_text('\n'.join(md))
    print('wrote %d packets -> %s (%.0f KB)' % (len(packets), d / 'packets.md', (d / 'packets.md').stat().st_size / 1024))


# ---------------------------------------------------------------------------------------------------------------------
# verdicts: check what the LLM said against what the bytes say
# ---------------------------------------------------------------------------------------------------------------------
def cmd_verdicts(args):
    out = Path(args.out)
    d = out / 'contracts'
    a = json.loads((d / 'analysis.json').read_text())
    by = {r['address']: r for r in a['records']}
    verdicts = json.loads(Path(args.file).read_text())
    if isinstance(verdicts, dict):
        verdicts = verdicts.get('verdicts', [])
    rows, npass, nfail = [], 0, 0
    for v in verdicts:
        addr = (v.get('address') or '').lower()
        r = by.get(addr)
        checks = []
        if not r:
            checks.append({'claim': 'address analysed', 'ok': False, 'detail': 'not in analysis.json'})
        else:
            have_in, have_out = set(r['selectors_in']), set(r['selectors_out']) | set(r.get('selectors_error', []))
            for s in v.get('selectors') or []:
                s = s.lower().split()[0]
                checks.append({'claim': 'selector %s present' % s, 'ok': s in have_in or s in have_out,
                               'detail': 'in' if s in have_in else ('out' if s in have_out else 'absent from both sets')})
            have_addr = {x.lower() for x in r['addresses']} | {s['address'].lower() for s in (r.get('proxy_chain') or [])}
            for x in v.get('addresses') or []:
                x = x.lower()
                checks.append({'claim': 'address %s is an immediate' % x, 'ok': x in have_addr,
                               'detail': 'found' if x in have_addr else 'not a PUSH20 immediate or proxy step'})
            for s in v.get('strings') or []:
                checks.append({'claim': 'string %r embedded' % s, 'ok': any(s in t for t in r['strings']),
                               'detail': 'found' if any(s in t for t in r['strings']) else 'absent'})
            for k in v.get('facts') or []:
                checks.append({'claim': 'fact %s' % k, 'ok': k in r['facts'],
                               'detail': r['facts'][k]['note'] if k in r['facts'] else 'not extracted'})
            for k, op, val in (v.get('window_checks') or []):
                got = (r.get('window') or {}).get(k)
                ok = got is not None and ({'>=': got >= val, '<=': got <= val, '==': got == val}.get(op, False))
                checks.append({'claim': 'window.%s %s %s' % (k, op, val), 'ok': ok, 'detail': 'actual %s' % got})
        ok = all(c['ok'] for c in checks) if checks else None
        npass += sum(1 for c in checks if c['ok'])
        nfail += sum(1 for c in checks if not c['ok'])
        rows.append({'address': addr, 'verdict': v.get('verdict'), 'mechanism': v.get('mechanism'),
                     'confidence': v.get('confidence'), 'checks': checks, 'all_checks_pass': ok,
                     'unchecked_opinion': v.get('note')})
    res = {'window': str(out), 'verdicts': len(rows), 'checks_passed': npass, 'checks_failed': nfail, 'rows': rows}
    (d / 'verdicts_checked.json').write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, indent=1))
    for r in rows:
        bad = [c for c in r['checks'] if not c['ok']]
        flag = 'OK ' if not bad else 'FAIL'
        print('%s %s %s' % (flag, r['address'], (r['mechanism'] or '')[:70]))
        for c in bad:
            print('      x %s — %s' % (c['claim'], c['detail']))


# ---------------------------------------------------------------------------------------------------------------------
# one: ad-hoc single contract, no window needed
# ---------------------------------------------------------------------------------------------------------------------
def cmd_one(args):
    rpc = open_rpc()
    addr = args.address.lower()
    code = rpc.call('eth_getCode', [addr, 'latest'], allow_errors=True)
    if not isinstance(code, str) or len(code) <= 4:
        print(json.dumps({'address': addr, 'has_code': False}))
        return
    cache = {addr: code}
    chain = resolve_proxy(rpc, addr, code, cache=cache)
    target, tcode = addr, code
    for stp in chain:                       # the deepest step that has code is the one that runs
        c = cache.get(stp['address'].lower(), '0x')
        if len(c) > 4:
            target, tcode = stp['address'].lower(), c
    rec = analyze_code(addr, tcode, chain_hint=chain)
    rec['analyzed_address'] = target
    rec['clone_count'] = 1
    rec['score'], rec['score_why'] = 0, []
    import labels as labels_mod
    lb = {k.lower(): v for k, v in labels_mod.load().items()}
    names = resolve_signatures(rec['selectors_in'] + rec['selectors_out'], online=args.resolve_sigs)
    tn = resolve_signatures(rec['event_topics'], online=args.resolve_sigs, kind='event')
    src = fetch_source(target, args.chainid) if args.source else None
    p = packet_of(rec, names, tn, lb, src)
    if args.json:
        print(json.dumps(p, indent=1))
    else:
        print(packet_md(p))
    if args.disasm:
        ins, _, _ = disassemble(split_metadata(to_bytes(tcode))[0])
        if ':' in args.disasm:                       # a pc window, e.g. --disasm 0x40:0x90
            lo, hi = (int(v, 0) for v in args.disasm.split(':'))
            ins = [x for x in ins if lo <= x.pc <= hi]
        else:
            ins = ins[:int(args.disasm, 0)]
        for x in ins:
            print(repr(x))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('census', help='enumerate the window\'s contracts (offline)')
    c.add_argument('--out', required=True); c.add_argument('--limit-blocks', type=int, default=0)
    c.add_argument('--top-gas', type=int, default=250); c.add_argument('--top-logs', type=int, default=150)
    c.add_argument('--top-calls', type=int, default=150)
    c.add_argument('--recover-authorities', action='store_true',
                   help='ecrecover every EIP-7702 authorization to the EOA that signed it (needs coincurve)')
    f = sub.add_parser('fetch', help='eth_getCode + proxy resolution for the census')
    f.add_argument('--out', required=True); f.add_argument('--limit', type=int, default=0)
    f.add_argument('--batch', type=int, default=100, help='JSON-RPC calls per batch')
    f.add_argument('--workers', type=int, default=6, help='batches in flight at once')
    an = sub.add_parser('analyze', help='disassemble, extract facts, score')
    an.add_argument('--out', required=True); an.add_argument('--top', type=int, default=25)
    an.add_argument('--resolve-sigs', action='store_true', help='look unknown selectors up at openchain.xyz (cached)')
    pk = sub.add_parser('packets', help='write the LLM evidence packets')
    pk.add_argument('--out', required=True); pk.add_argument('--top', type=int, default=30)
    pk.add_argument('--address', default=''); pk.add_argument('--source', action='store_true')
    pk.add_argument('--chainid', type=int, default=1)
    vd = sub.add_parser('verdicts', help='check LLM verdicts against the bytes and the window')
    vd.add_argument('--out', required=True); vd.add_argument('--file', required=True)
    on = sub.add_parser('one', help='ad-hoc: analyse a single address')
    on.add_argument('--address', required=True); on.add_argument('--source', action='store_true')
    on.add_argument('--json', action='store_true')
    on.add_argument('--disasm', default='', help='N instructions, or a pc window like 0x40:0x90')
    on.add_argument('--resolve-sigs', action='store_true'); on.add_argument('--chainid', type=int, default=1)
    args = ap.parse_args()
    {'census': cmd_census, 'fetch': cmd_fetch, 'analyze': cmd_analyze, 'packets': cmd_packets,
     'verdicts': cmd_verdicts, 'one': cmd_one}[args.cmd](args)


if __name__ == '__main__':
    main()
