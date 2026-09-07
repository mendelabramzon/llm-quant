#!/usr/bin/env python3
"""Etherscan V2 unified-API client — verified contract source across chains, reading the key from `etherscan_key.txt`.

The V2 API (https://api.etherscan.io/v2/api?chainid=<id>&...) is one key for every supported chain. On the FREE tier the
`contract` module (getsourcecode / getabi) works on all of them (Ethereum, BSC, Base, Polygon, Arbitrum, Optimism, ...),
while the `account`, `proxy` and `logs` modules are gated to a few chains (Ethereum, Polygon, Arbitrum observed). So use
this for verified SOURCE anywhere, and do on-chain reads (eth_call) through a public RPC per chain (see CHAIN_RPC).

The key is read from disk and never logged; error strings are returned as-is (Etherscan does not echo the key).
"""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_FILE = ROOT / 'etherscan_key.txt'
BASE = 'https://api.etherscan.io/v2/api'

# chainid -> name and a public JSON-RPC endpoint list for reads (no key needed)
CHAIN_RPC = {
    1: ('ethereum', ['https://eth.drpc.org', 'https://ethereum-rpc.publicnode.com', 'https://eth.merkle.io']),
    56: ('bsc', ['https://bsc-dataseed.bnbchain.org', 'https://bsc-dataseed1.defibit.io', 'https://binance.llamarpc.com', 'https://bsc.drpc.org']),
    137: ('polygon', ['https://polygon-rpc.com', 'https://polygon.drpc.org', 'https://polygon-bor-rpc.publicnode.com']),
    8453: ('base', ['https://mainnet.base.org', 'https://base.drpc.org', 'https://base-rpc.publicnode.com']),
    42161: ('arbitrum', ['https://arb1.arbitrum.io/rpc', 'https://arbitrum.drpc.org', 'https://arbitrum-one-rpc.publicnode.com']),
    10: ('optimism', ['https://mainnet.optimism.io', 'https://optimism.drpc.org', 'https://optimism-rpc.publicnode.com']),
}


def _key():
    return KEY_FILE.read_text().strip()


def get(chainid, params, timeout=30, retries=2):
    """Call the V2 API. Tolerant JSON parse (Etherscan leaves raw control chars in SourceCode)."""
    q = dict(params)
    q['chainid'] = chainid
    q['apikey'] = _key()
    url = BASE + '?' + urllib.parse.urlencode(q)
    last = None
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'llm-quant research'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode('utf-8', 'replace')
            return json.loads(body, strict=False)
        except Exception as e:
            last = str(e)[:120]
            time.sleep(0.8)
    return {'status': '0', 'message': 'transport', '_error': last}


def source(chainid, address, follow_proxy=True):
    """Return {name, source, proxy, implementation, compiler} for a verified contract, following a proxy to its impl."""
    d = get(chainid, {'module': 'contract', 'action': 'getsourcecode', 'address': address})
    res = d.get('result')
    if not isinstance(res, list) or not res:
        return {'name': None, 'source': '', 'error': d.get('message') or str(res)[:80]}
    r = res[0]
    out = {'name': r.get('ContractName') or None, 'source': r.get('SourceCode') or '',
           'proxy': r.get('Proxy') in ('1', 1), 'implementation': (r.get('Implementation') or '').strip() or None,
           'compiler': r.get('CompilerVersion')}
    if follow_proxy and out['proxy'] and out['implementation'] and ('depositFor' not in out['source']):
        impl = source(chainid, out['implementation'], follow_proxy=False)
        if impl.get('source'):
            impl['proxy'] = True
            impl['proxy_address'] = address
            return impl
    return out


def abi(chainid, address):
    d = get(chainid, {'module': 'contract', 'action': 'getabi', 'address': address})
    try:
        return json.loads(d.get('result')) if d.get('status') == '1' else None
    except Exception:
        return None


if __name__ == '__main__':
    import sys
    cid = int(sys.argv[1]) if len(sys.argv) > 1 else 56
    addr = sys.argv[2] if len(sys.argv) > 2 else '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82'
    s = source(cid, addr)
    print(CHAIN_RPC.get(cid, ('?',))[0], addr, '->', s.get('name'), 'src', len(s.get('source', '')), 'err', s.get('error'))
