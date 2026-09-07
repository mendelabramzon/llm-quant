#!/usr/bin/env python3
"""Find CORE / cVault.finance-family reward vaults by BYTECODE, not by name or verified source.

Two source-free signals, both chain-agnostic and immune to unverified/renamed contracts:

  1. Selector fingerprint. A contract's dispatcher is a run of `PUSH4 <selector> ... EQ ... JUMPI`. Walking the runtime
     bytecode (respecting PUSH data) recovers the set of 4-byte selectors it implements. The CoreVault lineage carries a
     rare cluster — depositFor(address,uint256,uint256), withdrawFrom(...), setAllowanceForPoolToken(...),
     addPendingRewards(uint256), startNewEpoch(), setStrategyContractOrDistributionContractAllowance(address,uint256,address),
     massUpdatePools() — that ordinary MasterChef forks (Sushi/Pancake) do not have. Match >= 5 of these (depositFor and
     addPendingRewards mandatory) and it is almost certainly a CoreVault fork.

  2. Non-standard event topic. `setAllowanceForPoolToken` emits Approval(address,address,uint256,uint256) — a 4-arg
     Approval whose topic0 (0xb3fd5071…) differs from the ERC-20 3-arg Approval. `eth_getLogs` on that topic (or on the
     MasterChef Deposit(address,uint256,uint256) topic, then bytecode-filtered) ENUMERATES CoreVault forks across a chain
     with no candidate list at all.

Plus `norm_codehash`: runtime bytecode with trailing metadata stripped and PUSH20 address immediates zeroed, hashed — so
byte-identical forks that differ only in hardcoded token/pair addresses cluster to the same logic hash.

Reads are keyless public JSON-RPC (`eth_getCode`, `eth_getLogs`), so this works on any chain.

    uv run --with pycryptodome python scripts/bytecode_fingerprint.py fp --chain ethereum \
        --addresses 0x223Bc79156CBb0a6D175Ea6130Cb382D01868DF8,0x7ca9B4BAb4e16bEbEDCfF403f7397935d905f0D3
    uv run --with pycryptodome python scripts/bytecode_fingerprint.py enumerate --chain ethereum --from 25800000 --to 25924100
"""
import argparse
import json
import sys
import time
from pathlib import Path

from Crypto.Hash import keccak

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drpc import rpc as drpc_rpc
from etherscan import CHAIN_RPC

CHAIN_ID = {'ethereum': 1, 'bsc': 56, 'base': 8453, 'polygon': 137, 'arbitrum': 42161, 'optimism': 10}


def kk(s):
    k = keccak.new(digest_bits=256)
    k.update(s.encode() if isinstance(s, str) else s)
    return k.hexdigest()


def sel(sig):
    return '0x' + kk(sig)[:8]


# rare CoreVault-lineage selectors (the discriminating cluster) + mandatory pair
CORE_SELECTORS = {
    sel('depositFor(address,uint256,uint256)'): 'depositFor',
    sel('withdrawFrom(address,uint256,uint256)'): 'withdrawFrom',
    sel('setAllowanceForPoolToken(address,uint256,uint256)'): 'setAllowanceForPoolToken',
    sel('addPendingRewards(uint256)'): 'addPendingRewards',
    sel('startNewEpoch()'): 'startNewEpoch',
    sel('setStrategyContractOrDistributionContractAllowance(address,uint256,address)'): 'setStrategyContractAllowance',
    sel('massUpdatePools()'): 'massUpdatePools',
}
MANDATORY = {sel('depositFor(address,uint256,uint256)'), sel('addPendingRewards(uint256)')}
MASTERCHEF_HINT = {sel('poolLength()'), sel('poolInfo(uint256)'), sel('userInfo(uint256,address)'), sel('emergencyWithdraw(uint256)')}
TOPIC_APPROVAL4 = '0x' + kk('Approval(address,address,uint256,uint256)')   # non-standard 4-arg Approval
TOPIC_DEPOSIT = '0x' + kk('Deposit(address,uint256,uint256)')             # MasterChef deposit


def rpc(chain, method, params, timeout=30):
    eps = CHAIN_RPC.get(CHAIN_ID.get(chain, 1), (None, ['https://eth.drpc.org']))[1]
    try:
        return drpc_rpc(method, params, endpoints=eps, timeout=timeout, retries=2)
    except Exception:
        return None


def get_code(chain, addr):
    r = rpc(chain, 'eth_getCode', [addr, 'latest'])
    return r if isinstance(r, str) and r.startswith('0x') else None


def selectors(code_hex):
    """Set of PUSH4 immediates in the runtime bytecode (walks PUSH data correctly)."""
    if not code_hex or not code_hex.startswith('0x'):
        return set()
    b = bytes.fromhex(code_hex[2:])
    out = set()
    i, n = 0, len(b)
    while i < n:
        op = b[i]
        if 0x60 <= op <= 0x7f:              # PUSH1..PUSH32
            k = op - 0x5f
            if op == 0x63 and i + 5 <= n:   # PUSH4 -> a selector immediate
                out.add('0x' + b[i + 1:i + 5].hex())
            i += 1 + k
        else:
            i += 1
    return out


def strip_metadata(b):
    """Drop the Solidity CBOR metadata trailer (…a264/­a165… + 2-byte length) if present."""
    for marker in (b'\xa2\x64\x69\x70\x66\x73', b'\xa1\x65\x62\x7a\x7a\x72'):  # ipfs / bzzr
        idx = b.rfind(marker)
        if idx > 0:
            return b[:idx]
    return b


def norm_codehash(code_hex):
    """Logic hash: metadata stripped, PUSH20 (address) immediates zeroed → same value for forks differing only in
    hardcoded token/pair/router addresses."""
    if not code_hex or len(code_hex) < 4:
        return None
    b = bytearray(strip_metadata(bytes.fromhex(code_hex[2:])))
    i, n = 0, len(b)
    while i < n:
        op = b[i]
        if 0x60 <= op <= 0x7f:
            k = op - 0x5f
            if op == 0x73 and i + 21 <= n:   # PUSH20 -> zero it (address immediate)
                for j in range(i + 1, i + 21):
                    b[j] = 0
            i += 1 + k
        else:
            i += 1
    return kk(bytes(b))


def fingerprint(chain, addr):
    code = get_code(chain, addr)
    if not code or code == '0x':
        return {'address': addr, 'has_code': False}
    ss = selectors(code)
    matched = sorted(CORE_SELECTORS[s] for s in ss if s in CORE_SELECTORS)
    is_core = len(matched) >= 5 and MANDATORY.issubset(ss)
    return {
        'address': addr, 'has_code': True, 'code_bytes': (len(code) - 2) // 2,
        'core_selectors_matched': matched, 'n_matched': len(matched),
        'mandatory_present': MANDATORY.issubset(ss),
        'masterchef_hints': len(MASTERCHEF_HINT & ss),
        'is_corevault_fork': is_core, 'norm_codehash': norm_codehash(code)[:16],
    }


def enumerate_forks(chain, b_from, b_to, step=2000, use_deposit=False):
    """Scan eth_getLogs over [b_from,b_to] for the CoreVault fingerprint topic, then bytecode-confirm each emitter.
    Default topic = non-standard 4-arg Approval (high precision). --deposit widens to the MasterChef Deposit topic."""
    topic = TOPIC_DEPOSIT if use_deposit else TOPIC_APPROVAL4
    emitters = {}
    b = b_from
    while b <= b_to:
        hi = min(b + step - 1, b_to)
        logs = rpc(chain, 'eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(hi), 'topics': [topic]}], timeout=40)
        if isinstance(logs, list):
            for l in logs:
                a = (l.get('address') or '').lower()
                emitters[a] = emitters.get(a, 0) + 1
        b = hi + 1
        time.sleep(0.05)
    forks = []
    for a in emitters:
        fp = fingerprint(chain, a)
        if fp.get('is_corevault_fork'):
            fp['log_hits'] = emitters[a]
            forks.append(fp)
    return {'topic': topic, 'from': b_from, 'to': b_to, 'unique_emitters': len(emitters), 'confirmed_forks': forks}


def enumerate_offline(chain, logs_dir, use_deposit=True):
    """Enumerate CoreVault forks from an already-collected logs directory (live_collect / eth_day_collect output):
    every emitter of the fingerprint topic, bytecode-confirmed. No live logs endpoint needed."""
    import glob
    import gzip
    import os
    topics = {TOPIC_APPROVAL4} | ({TOPIC_DEPOSIT} if use_deposit else set())
    emitters = {}
    files = sorted(glob.glob(os.path.join(logs_dir, '*.json.gz')))
    for p in files:
        try:
            for l in json.load(gzip.open(p, 'rt')):
                if l.get('topics') and l['topics'][0] in topics:
                    a = l['address'].lower()
                    emitters[a] = emitters.get(a, 0) + 1
        except Exception:
            continue
    forks = []
    for a in emitters:
        fp = fingerprint(chain, a)
        if fp.get('is_corevault_fork'):
            fp['log_hits'] = emitters[a]
            forks.append(fp)
    return {'logs_dir': logs_dir, 'files': len(files), 'unique_emitters': len(emitters), 'confirmed_forks': forks}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('fp'); a.add_argument('--chain', default='ethereum'); a.add_argument('--addresses', required=True)
    e = sub.add_parser('enumerate'); e.add_argument('--chain', default='ethereum')
    e.add_argument('--from', dest='b_from', type=int, required=True); e.add_argument('--to', dest='b_to', type=int, required=True)
    e.add_argument('--step', type=int, default=2000); e.add_argument('--deposit', action='store_true')
    e.add_argument('--out', default='')
    o = sub.add_parser('enum-offline'); o.add_argument('--chain', default='ethereum'); o.add_argument('--logs', required=True); o.add_argument('--out', default='')
    args = ap.parse_args()
    if args.cmd == 'enum-offline':
        res = enumerate_offline(args.chain, args.logs)
        print('scanned %d log files, %d unique fingerprint-topic emitters; CORE forks:' % (res['files'], res['unique_emitters']))
        for f in res['confirmed_forks']:
            print('  %s matched=%d %s log_hits=%d logic=%s' % (f['address'], f['n_matched'], f['core_selectors_matched'], f['log_hits'], f['norm_codehash']))
        if args.out:
            Path(args.out).write_text(json.dumps(res, indent=1))
        return
    if args.cmd == 'fp':
        for addr in [x.strip() for x in args.addresses.split(',') if x.strip()]:
            r = fingerprint(args.chain, addr)
            print('%s  fork=%s  matched=%d %s  mc_hints=%s  bytes=%s  logic=%s' % (
                addr, r.get('is_corevault_fork'), r.get('n_matched', 0), r.get('core_selectors_matched'),
                r.get('masterchef_hints'), r.get('code_bytes'), r.get('norm_codehash')))
    else:
        res = enumerate_forks(args.chain, args.b_from, args.b_to, args.step, args.deposit)
        print(json.dumps({'topic': res['topic'], 'range': [res['from'], res['to']], 'unique_emitters': res['unique_emitters'],
                          'confirmed_forks': [{'address': f['address'], 'matched': f['core_selectors_matched'], 'log_hits': f['log_hits'], 'logic': f['norm_codehash']} for f in res['confirmed_forks']]}, indent=1))
        if args.out:
            Path(args.out).write_text(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
