#!/usr/bin/env python3
"""Deep-audit the UNVERIFIED custom vaults across chains.

An unverified contract has no source, so it is audited from bytecode. Two levers:
  1. Twin match by normalised code hash. Most unverified vaults are just unverified DEPLOYMENTS of known code — the same
     `norm_codehash` as a VERIFIED contract elsewhere (another address, or another chain). We build a global
     logic_hash -> verified-name map across every chain scanned; an unverified vault whose hash is in it IS that known
     (often audited) contract, no source review needed.
  2. For the genuinely novel unverified bytecode (no verified twin anywhere), an opcode/selector risk profile: dangerous
     opcodes (DELEGATECALL outside a proxy, SELFDESTRUCT, CALLCODE), the function-selector type guess, proxy/impl, the
     owner, and the native balance (is there value to drain?).

Enumerate active vaults per chain (Infura), fingerprint (bytecode_fingerprint), resolve proxies, check verification
(Etherscan V2 key), twin-match, and rank the novel-unverified by value for manual review.

    uv run --with pycryptodome python scripts/vault_deep_audit.py --chains base,bsc,polygon,optimism --blocks 25000
"""
import argparse
import collections
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bytecode_fingerprint as bf
import etherscan
from corevault_hunt import EVM, eps_for, rpc
from vault_audit import enumerate_vaults, batch_codes, batch_storage, classify, IMPL_SLOT

# dangerous opcodes to detect by walking runtime bytecode
DANGER = {0xf4: 'DELEGATECALL', 0xff: 'SELFDESTRUCT', 0xf2: 'CALLCODE', 0xf5: 'CREATE2', 0x32: 'ORIGIN'}
OWNER_GETTERS = ['owner()', 'getOwner()', 'admin()', 'governance()', 'owner', 'authority()']


def kk4(s):
    from Crypto.Hash import keccak
    k = keccak.new(digest_bits=256); k.update(s.encode()); return '0x' + k.hexdigest()[:8]


def dangerous_ops(code_hex):
    b = bytes.fromhex(code_hex[2:]) if code_hex and code_hex.startswith('0x') else b''
    found = set()
    i, n = 0, len(b)
    while i < n:
        op = b[i]
        if 0x60 <= op <= 0x7f:
            i += 1 + (op - 0x5f)
            continue
        if op in DANGER:
            found.add(DANGER[op])
        i += 1
    return sorted(found)


def call_first_addr(eps, addr, getters):
    for g in getters:
        r = rpc(eps, 'eth_call', [{'to': addr, 'data': kk4(g)}, 'latest'])
        if isinstance(r, str) and len(r) >= 42:
            a = '0x' + r[-40:]
            if int(a, 16) != 0:
                return g, a
    return None, None


def native_balance(eps, addr):
    r = rpc(eps, 'eth_getBalance', [addr, 'latest'])
    try:
        return int(r, 16) / 1e18
    except Exception:
        return None


def is_verified(chainid, addr):
    try:
        s = etherscan.source(chainid, addr)
        return bool(s.get('source')), (s.get('name'), s.get('implementation'))
    except Exception:
        return False, (None, None)


def run(chains, blocks):
    twin = {}          # logic_hash -> verified name (global, cross-chain)
    per_chain = {}
    # pass 1: enumerate + fingerprint every chain, record clusters
    for chain in chains:
        chainid = EVM[chain][0]
        etherscan.CHAIN_RPC[chainid] = (chain, eps_for(chain))
        bf.CHAIN_ID[chain] = chainid
        eps = eps_for(chain)
        rng, emitters = enumerate_vaults(chain, blocks)
        top = [a for a, _ in emitters.most_common(500)]
        codes = batch_codes(eps, top)
        top = [a for a in top if codes.get(a) and codes[a] != '0x']
        impls = batch_storage(eps, top, IMPL_SLOT)
        impl_codes = batch_codes(eps, sorted(set(impls.values())))
        clusters = collections.defaultdict(list)
        eff = {}
        for a in top:
            impl = impls.get(a)
            code = impl_codes.get(impl) if impl and impl_codes.get(impl) not in (None, '0x') else codes.get(a)
            if not code or code == '0x':
                continue
            logic = (bf.norm_codehash(code) or '')[:16]
            typ, _ = classify(bf.selectors(code))
            clusters[logic].append(a)
            eff[a] = {'code': code, 'impl': impl, 'type': typ, 'logic': logic}
        per_chain[chain] = {'chainid': chainid, 'eps': eps, 'range': rng, 'clusters': clusters, 'eff': eff, 'emitters': emitters}
        print('  [%s] %d contracts, %d clusters' % (chain, len(eff), len(clusters)), flush=True)

    # pass 2: verification of one representative per cluster; build the global twin map
    for chain, d in per_chain.items():
        for logic, addrs in d['clusters'].items():
            ver, (name, _) = is_verified(d['chainid'], addrs[0])
            d.setdefault('verified', {})[logic] = (ver, name)
            if ver and name:
                twin.setdefault(logic, name)
            time.sleep(0.05)
        print('  [%s] verification checked (%d clusters)' % (chain, len(d['clusters'])), flush=True)

    # pass 3: novel-unverified = unverified representative AND logic hash has no verified twin anywhere
    findings = []
    for chain, d in per_chain.items():
        eps = d['eps']
        for logic, addrs in sorted(d['clusters'].items(), key=lambda kv: -len(kv[1])):
            ver, name = d['verified'][logic]
            if ver:
                continue
            if logic in twin:               # unverified but a verified twin exists -> known code
                findings.append({'chain': chain, 'logic': logic, 'status': 'twin-of-verified', 'twin_name': twin[logic], 'count': len(addrs), 'representative': addrs[0]})
                continue
            rep = addrs[0]
            e = d['eff'][rep]
            og, owner = call_first_addr(eps, rep, OWNER_GETTERS)
            bal = native_balance(eps, rep)
            danger = dangerous_ops(e['code'])
            # DELEGATECALL is expected for a proxy; flag it only if NOT a resolved proxy
            danger_notable = [x for x in danger if not (x == 'DELEGATECALL' and e['impl'])]
            findings.append({'chain': chain, 'logic': logic, 'status': 'NOVEL-UNVERIFIED', 'type': e['type'], 'count': len(addrs),
                             'representative': rep, 'proxy_impl': e['impl'], 'owner_getter': og, 'owner': owner,
                             'native_balance': bal, 'dangerous_ops': danger_notable, 'code_bytes': (len(e['code']) - 2) // 2,
                             'deposit_logs': d['emitters'][rep]})
            time.sleep(0.03)
    return per_chain, twin, findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--chains', default='base,bsc')
    ap.add_argument('--blocks', type=int, default=25000)
    ap.add_argument('--out', default=str(ROOT / 'research' / '2026-09-07' / 'vault_audit' / 'unverified_audit.json'))
    a = ap.parse_args()
    chains = [c.strip() for c in a.chains.split(',') if c.strip() in EVM]
    per_chain, twin, findings = run(chains, a.blocks)
    novel = [f for f in findings if f['status'] == 'NOVEL-UNVERIFIED']
    twins = [f for f in findings if f['status'] == 'twin-of-verified']
    print('\n=== unverified clusters: %d novel, %d are twins of verified code ===' % (len(novel), len(twins)))
    print('twins of known code:', dict(collections.Counter(f['twin_name'] for f in twins)))
    print('\nNOVEL-UNVERIFIED (ranked by native balance):')
    for f in sorted(novel, key=lambda f: -(f.get('native_balance') or 0)):
        print(' %-9s %s type=%-10s x%-2d bal=%s owner=%s danger=%s bytes=%s deposits=%s' % (
            f['chain'], f['representative'], f.get('type'), f['count'], (round(f['native_balance'], 4) if f.get('native_balance') else 0),
            (f.get('owner') or '-')[:12], ','.join(f.get('dangerous_ops') or []), f.get('code_bytes'), f.get('deposit_logs')))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({'blocks': a.blocks, 'twins_of_known': len(twins), 'novel': novel}, indent=1, default=str))
    print('written', a.out)


if __name__ == '__main__':
    main()
