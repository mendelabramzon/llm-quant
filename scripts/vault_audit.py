#!/usr/bin/env python3
"""Enumerate, classify, and triage vaults across EVMs, then flag the ones worth a source audit.

Pipeline (reuses scripts/bytecode_fingerprint.py + scripts/etherscan.py + Infura via scripts/corevault_hunt.py):
  1. Enumerate ACTIVE vaults per chain from a recent window by their deposit/stake event topics (MasterChef,
     ERC-4626, Synthetix-staking). No name index needed.
  2. Fingerprint each emitter's runtime bytecode: the set of function selectors + a normalised code hash.
  3. Classify by selector signature (CORE-fork, MasterChef, ERC-4626, Beefy-style, Synthetix-staking, Curve-gauge,
     Yearn-v2, or unknown) and CLUSTER by normalised code hash — so the hundreds of active vaults collapse into a few
     dozen distinct implementations, one representative each to audit.
  4. Red-flag scan of each representative's verified source (Etherscan V2 key): delegatecall/selfdestruct/tx.origin,
     spot-reserve pricing, MasterChef migrator, arbitrary approvals, unguarded initialize, etc.

    uv run --with pycryptodome python scripts/vault_audit.py --chains ethereum,base,bsc,arbitrum --blocks 40000
"""
import argparse
import collections
import json
import sys
import time
from pathlib import Path

from Crypto.Hash import keccak

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bytecode_fingerprint as bf
import etherscan
from corevault_hunt import EVM, eps_for, rpc


def kk(s):
    k = keccak.new(digest_bits=256)
    k.update(s.encode())
    return k.hexdigest()


def sel(sig):
    return '0x' + kk(sig)[:8]


# event topics to enumerate active vaults
TOPICS = {
    'masterchef': '0x' + kk('Deposit(address,uint256,uint256)'),
    'erc4626': '0x' + kk('Deposit(address,address,uint256,uint256)'),
    'staking': '0x' + kk('Staked(address,uint256)'),
}

# type signatures: (selectors, min_hits, mandatory)
TYPES = {
    'core_fork': ([sel('depositFor(address,uint256,uint256)'), sel('addPendingRewards(uint256)'), sel('setAllowanceForPoolToken(address,uint256,uint256)'), sel('startNewEpoch()'), sel('setStrategyContractOrDistributionContractAllowance(address,uint256,address)'), sel('massUpdatePools()')], 5, [sel('depositFor(address,uint256,uint256)'), sel('addPendingRewards(uint256)')]),
    'masterchef': ([sel('poolLength()'), sel('poolInfo(uint256)'), sel('massUpdatePools()'), sel('deposit(uint256,uint256)'), sel('userInfo(uint256,address)'), sel('emergencyWithdraw(uint256)'), sel('updatePool(uint256)')], 4, [sel('poolInfo(uint256)')]),
    'erc4626': ([sel('asset()'), sel('totalAssets()'), sel('convertToShares(uint256)'), sel('convertToAssets(uint256)'), sel('deposit(uint256,address)'), sel('redeem(uint256,address,address)'), sel('maxDeposit(address)'), sel('previewDeposit(uint256)')], 4, [sel('asset()'), sel('totalAssets()')]),
    'beefy_vault': ([sel('want()'), sel('strategy()'), sel('getPricePerFullShare()'), sel('deposit(uint256)'), sel('withdraw(uint256)'), sel('earn()'), sel('balance()')], 4, [sel('getPricePerFullShare()')]),
    'synthetix_staking': ([sel('stake(uint256)'), sel('withdraw(uint256)'), sel('getReward()'), sel('rewardPerToken()'), sel('earned(address)'), sel('rewardsToken()'), sel('stakingToken()')], 4, [sel('rewardPerToken()'), sel('earned(address)')]),
    'curve_gauge': ([sel('deposit(uint256)'), sel('withdraw(uint256)'), sel('claim_rewards()'), sel('lp_token()'), sel('reward_tokens(uint256)'), sel('working_supply()')], 3, [sel('claim_rewards()')]),
    'yearn_v2': ([sel('pricePerShare()'), sel('deposit()'), sel('withdraw()'), sel('token()'), sel('totalAssets()'), sel('withdrawalQueue(uint256)')], 4, [sel('pricePerShare()')]),
}

# red flags to scan verified source for
REDFLAGS = {
    'delegatecall': 'delegatecall', 'selfdestruct': 'selfdestruct', 'tx.origin': 'tx.origin',
    'spot_reserve_pricing': 'getReserves(', 'blockhash_rng': 'blockhash(', 'timestamp_use': 'block.timestamp',
    'masterchef_migrator': 'function migrate(', 'arbitrary_approve': '.approve(', 'unguarded_initialize': 'function initialize(',
    'assembly': 'assembly', 'balanceOf_accounting': '.balanceOf(address(this))', 'onlyOwner': 'onlyOwner',
}


def classify(selset):
    best, best_score, scores = 'unknown', 0.0, {}
    for name, (sigs, minhit, mand) in TYPES.items():
        hits = sum(1 for s in sigs if s in selset)
        ok = hits >= minhit and all(m in selset for m in mand)
        scores[name] = hits
        if ok and hits > best_score:
            best, best_score = name, hits
    return best, scores


def enumerate_vaults(chain, blocks, chunk=9500):
    eps = eps_for(chain)
    latest = rpc(eps, 'eth_blockNumber', [])
    if not isinstance(latest, str):
        return None, {}
    latest = int(latest, 16)
    start = max(0, latest - blocks)
    emitters = collections.Counter()
    for tkey, topic in TOPICS.items():
        b = start
        while b <= latest:
            hi = min(b + chunk - 1, latest)
            res = rpc(eps, 'eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(hi), 'topics': [topic]}])
            if isinstance(res, list):
                for l in res:
                    emitters[(l.get('address') or '').lower()] += 1
            elif isinstance(res, dict) and res.get('_error') and hi > b:
                mid = (b + hi) // 2
                for lo2, hi2 in ((b, mid), (mid + 1, hi)):
                    r2 = rpc(eps, 'eth_getLogs', [{'fromBlock': hex(lo2), 'toBlock': hex(hi2), 'topics': [topic]}])
                    if isinstance(r2, list):
                        for l in r2:
                            emitters[(l.get('address') or '').lower()] += 1
            b = hi + 1
            time.sleep(0.02)
    return (start, latest), emitters


def scan_source(chainid, addr):
    try:
        src = (etherscan.source(chainid, addr).get('source') or '')
    except Exception:
        src = ''
    if not src:
        return {'verified': False, 'flags': []}
    GENERIC = {'onlyOwner', 'assembly', 'timestamp_use', 'delegatecall'}
    flags = [name for name, needle in REDFLAGS.items() if needle in src and name not in GENERIC]
    return {'verified': True, 'src_len': len(src), 'flags': flags, 'onlyOwner_count': src.count('onlyOwner')}


def batch_codes(eps, addrs, batch=20):
    import urllib.request
    out = {}
    for k in range(0, len(addrs), batch):
        chunk = addrs[k:k + batch]
        payload = json.dumps([{'jsonrpc': '2.0', 'id': j, 'method': 'eth_getCode', 'params': [a, 'latest']} for j, a in enumerate(chunk)]).encode()
        for ep in eps:
            try:
                d = json.loads(urllib.request.urlopen(urllib.request.Request(ep, data=payload, headers={'Content-Type': 'application/json'}), timeout=40).read())
                for item in d:
                    a = chunk[item.get('id', 0)]
                    r = item.get('result')
                    if isinstance(r, str):
                        out[a] = r
                break
            except Exception:
                continue
        time.sleep(0.03)
    return out


IMPL_SLOT = '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'   # EIP-1967 implementation


def batch_storage(eps, addrs, slot, batch=20):
    import urllib.request
    out = {}
    for k in range(0, len(addrs), batch):
        chunk = addrs[k:k + batch]
        payload = json.dumps([{'jsonrpc': '2.0', 'id': j, 'method': 'eth_getStorageAt', 'params': [a, slot, 'latest']} for j, a in enumerate(chunk)]).encode()
        for ep in eps:
            try:
                d = json.loads(urllib.request.urlopen(urllib.request.Request(ep, data=payload, headers={'Content-Type': 'application/json'}), timeout=40).read())
                for item in d:
                    a = chunk[item.get('id', 0)]
                    r = item.get('result')
                    if isinstance(r, str) and len(r) >= 42:
                        impl = '0x' + r[-40:]
                        if int(impl, 16) != 0:
                            out[a] = impl
                break
            except Exception:
                continue
        time.sleep(0.03)
    return out


def hunt_chain(chain, blocks):
    chainid = EVM[chain][0]
    etherscan.CHAIN_RPC[chainid] = (chain, eps_for(chain))
    bf.CHAIN_ID[chain] = chainid
    rng, emitters = enumerate_vaults(chain, blocks)
    print('  [%s] enumerated %d unique emitters, fingerprinting...' % (chain, len(emitters)), flush=True)
    vaults = []
    clusters = collections.defaultdict(list)
    top = [a for a, _ in emitters.most_common(600)]
    eps = eps_for(chain)
    codes = batch_codes(eps, top)
    top = [a for a in top if codes.get(a) and codes[a] != '0x']
    impls = batch_storage(eps, top, IMPL_SLOT)                     # EIP-1967 proxy -> implementation
    impl_codes = batch_codes(eps, sorted(set(impls.values())))
    print('  [%s] %d contracts, %d proxies resolved; classifying...' % (chain, len(top), len(impls)), flush=True)
    for addr in top:
        hits = emitters[addr]
        impl = impls.get(addr)
        code = impl_codes.get(impl) if impl and impl_codes.get(impl) not in (None, '0x') else codes.get(addr)
        if not code or code == '0x':
            continue
        ss = bf.selectors(code)
        typ, scores = classify(ss)
        logic = bf.norm_codehash(code)
        rec = {'address': addr, 'type': typ, 'proxy': bool(impl), 'impl': impl, 'deposit_logs': hits, 'logic_hash': (logic or '')[:16], 'code_bytes': (len(code) - 2) // 2, 'core_matched': scores.get('core_fork', 0)}
        vaults.append(rec)
        clusters[(typ, rec['logic_hash'])].append(addr)
        time.sleep(0.02)
    # one representative per cluster, source-scanned
    cluster_rows = []
    ordered = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
    print('  [%s] %d clusters; source-scanning top 20 representatives...' % (chain, len(ordered)), flush=True)
    rep_impl = {v['address']: v.get('impl') for v in vaults}
    for ci, ((typ, logic), addrs) in enumerate(ordered):
        rep = addrs[0]
        scan = scan_source(chainid, rep_impl.get(rep) or rep) if ci < 24 else {'verified': None, 'flags': []}
        cluster_rows.append({'type': typ, 'logic_hash': logic, 'count': len(addrs), 'representative': rep,
                             'verified': scan['verified'], 'redflags': scan.get('flags', []), 'members': addrs[:8]})
        time.sleep(0.05)
    by_type = collections.Counter(v['type'] for v in vaults)
    return {'chain': chain, 'chainid': chainid, 'range': rng, 'vaults': len(vaults), 'by_type': dict(by_type),
            'clusters': cluster_rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--chains', default='ethereum')
    ap.add_argument('--blocks', type=int, default=40000)
    ap.add_argument('--out', default=str(ROOT / 'research' / '2026-09-07' / 'vault_audit' / 'classification.json'))
    a = ap.parse_args()
    chains = list(EVM) if a.chains == 'all' else [c.strip() for c in a.chains.split(',') if c.strip() in EVM]
    results = []
    for c in chains:
        try:
            r = hunt_chain(c, a.blocks)
        except Exception as e:
            r = {'chain': c, 'error': str(e)[:150]}
        results.append(r)
        print('%-10s vaults=%-4s types=%s clusters=%s' % (c, r.get('vaults', '-'), r.get('by_type'), len(r.get('clusters', []))))
        for cl in (r.get('clusters') or [])[:12]:
            print('   %-18s x%-3d %s  flags=%s  %s' % (cl['type'], cl['count'], cl['representative'], ','.join(cl['redflags']), '' if cl['verified'] else '(unverified)'))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({'blocks': a.blocks, 'chains': results}, indent=1, default=str))
    print('written', a.out)


if __name__ == '__main__':
    main()
