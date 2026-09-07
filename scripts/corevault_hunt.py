#!/usr/bin/env python3
"""Cross-chain hunt for CoreVault forks: enumerate ACTIVE reward vaults per EVM, keep the CoreVault forks by bytecode,
and score exploitability where a chain preset exists.

Enumeration uses the local Infura keys (enabled for many EVMs): scan a recent window in <=10k-block chunks for the
MasterChef Deposit(address,uint256,uint256) topic, collect unique emitters, then bytecode-fingerprint each
(scripts/bytecode_fingerprint.py). A fork with no recent deposits has no reward flow, so "active" is the right filter.
For a confirmed fork on a chain with a full preset in corevault_scan.CHAINS, it is scored (blue-chip pools + reward-token
depth); on other EVMs the fork is reported with its bytecode match and deposit count for manual scoring.

    uv run --with pycryptodome python scripts/corevault_hunt.py --chains ethereum,optimism,linea,blast,scroll --blocks 60000
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import etherscan
import bytecode_fingerprint as bf
import corevault_scan as cs

# chain -> (chainid, infura network host). All verified reachable with the local keys.
EVM = {
    'ethereum': (1, 'mainnet'), 'bsc': (56, 'bsc-mainnet'), 'base': (8453, 'base-mainnet'),
    'polygon': (137, 'polygon-mainnet'), 'arbitrum': (42161, 'arbitrum-mainnet'), 'optimism': (10, 'optimism-mainnet'),
    'avalanche': (43114, 'avalanche-mainnet'), 'linea': (59144, 'linea-mainnet'), 'blast': (81457, 'blast-mainnet'),
    'mantle': (5000, 'mantle-mainnet'), 'scroll': (534352, 'scroll-mainnet'), 'zksync': (324, 'zksync-mainnet'),
    'celo': (42220, 'celo-mainnet'), 'opbnb': (204, 'opbnb-mainnet'), 'unichain': (130, 'unichain-mainnet'),
    'sei': (1329, 'sei-mainnet'),
}
DEPOSIT_TOPIC = bf.TOPIC_DEPOSIT


def infura_key():
    return re.findall(r'"([^"\s]+)"', (ROOT / 'infura_keys.txt').read_text())[0]


def eps_for(chain):
    return ['https://%s.infura.io/v3/%s' % (EVM[chain][1], infura_key())]


def rpc(eps, method, params, timeout=40, retries=2):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    for _ in range(retries + 1):
        for ep in eps:
            try:
                d = json.loads(urllib.request.urlopen(urllib.request.Request(ep, data=payload, headers={'Content-Type': 'application/json'}), timeout=timeout).read())
                if 'result' in d:
                    return d['result']
                if 'error' in d:
                    return {'_error': d['error']}
            except Exception as e:
                last = str(e)[:100]
        time.sleep(0.4)
    return {'_error': 'transport'}


def enumerate_active(eps, blocks, chunk=9500):
    latest = rpc(eps, 'eth_blockNumber', [])
    if not isinstance(latest, str):
        return None, {}
    latest = int(latest, 16)
    start = max(0, latest - blocks)
    emitters, b = {}, start
    while b <= latest:
        hi = min(b + chunk - 1, latest)
        res = rpc(eps, 'eth_getLogs', [{'fromBlock': hex(b), 'toBlock': hex(hi), 'topics': [DEPOSIT_TOPIC]}])
        if isinstance(res, list):
            for l in res:
                a = (l.get('address') or '').lower()
                emitters[a] = emitters.get(a, 0) + 1
        elif isinstance(res, dict) and res.get('_error') and hi > b:
            mid = (b + hi) // 2
            for lo2, hi2 in ((b, mid), (mid + 1, hi)):
                r2 = rpc(eps, 'eth_getLogs', [{'fromBlock': hex(lo2), 'toBlock': hex(hi2), 'topics': [DEPOSIT_TOPIC]}])
                if isinstance(r2, list):
                    for l in r2:
                        a = (l.get('address') or '').lower()
                        emitters[a] = emitters.get(a, 0) + 1
        b = hi + 1
        time.sleep(0.02)
    return (start, latest), emitters


def hunt_chain(chain, blocks):
    chainid, _ = EVM[chain]
    eps = eps_for(chain)
    etherscan.CHAIN_RPC[chainid] = (chain, eps)   # point bytecode_fingerprint reads at Infura
    bf.CHAIN_ID[chain] = chainid
    has_preset = chain in cs.CHAINS
    if has_preset:
        ch = cs.CHAINS[chain]
        cs.WETH, cs.BLUE, cs.FACTORIES, cs.NATIVE_USD = ch['weth'], ch['blue'], ch['factories'], ch['native_usd']
        cs.RPC_ENDPOINTS, cs.CHAINID, cs.CHAIN_NAME, cs.SOURCE_BACKEND = eps, chainid, chain, 'etherscan'
    rng, emitters = enumerate_active(eps, blocks)
    forks = []
    for addr in sorted(emitters, key=lambda x: -emitters[x]):
        fp = bf.fingerprint(chain, addr)
        if not fp.get('is_corevault_fork'):
            continue
        rec = {'address': addr, 'deposit_logs': emitters[addr], 'bytecode_matched': fp['n_matched'], 'logic_hash': fp['norm_codehash']}
        if has_preset:
            try:
                rec.update({k: v for k, v in cs.analyze_vault('', addr).items() if k not in ('address',)})
            except Exception as e:
                rec['score_error'] = str(e)[:100]
        forks.append(rec)
        time.sleep(0.04)
    return {'chain': chain, 'chainid': chainid, 'range': rng, 'emitters': len(emitters), 'scored': has_preset, 'forks': forks}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--chains', default='ethereum', help='comma list; "all" for every supported EVM')
    ap.add_argument('--blocks', type=int, default=60000)
    ap.add_argument('--out', default=str(ROOT / 'research' / '2026-09-07' / 'stacy_farm' / 'hunt_evm.json'))
    a = ap.parse_args()
    chains = list(EVM) if a.chains == 'all' else [c.strip() for c in a.chains.split(',') if c.strip() in EVM]
    results = []
    for c in chains:
        try:
            r = hunt_chain(c, a.blocks)
        except Exception as e:
            r = {'chain': c, 'error': str(e)[:150]}
        results.append(r)
        forks = r.get('forks', [])
        suit = [f for f in forks if f.get('EXPLOITABLE_AND_VALUABLE')]
        print('%-10s emitters=%-5s CORE_forks=%-2d suitable=%d %s' % (
            c, r.get('emitters', '-'), len(forks), len(suit),
            '' if not forks else '| ' + '; '.join('%s(matched %d, deposits %d%s)' % (
                f['address'][:10], f['bytecode_matched'], f['deposit_logs'],
                ', reward %s $%s liq $%s' % (f.get('reward_symbol'), f.get('reward_price_usd_est'), f.get('reward_liq_usd')) if r.get('scored') else '') for f in forks)))
    Path(a.out).write_text(json.dumps({'blocks': a.blocks, 'chains': results}, indent=1, default=str))
    total_forks = sum(len(r.get('forks', [])) for r in results)
    total_suit = sum(sum(1 for f in r.get('forks', []) if f.get('EXPLOITABLE_AND_VALUABLE')) for r in results)
    print('\n=== %d EVMs scanned, %d CoreVault forks, %d SUITABLE ===' % (len(chains), total_forks, total_suit))
    print('written', a.out)


if __name__ == '__main__':
    main()
