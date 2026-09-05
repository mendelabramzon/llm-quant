#!/usr/bin/env python3
"""Focused read-only follow-up queries motivated by the first sample."""
import collections
import gzip
import json
from pathlib import Path
import sys
import time
from onchain_probe import RPC, ROOT, hx, save, first_block_at, utc
from analyze_onchain import topic

OUT = ROOT / 'research/2026-09-05/followup'
ENDS = {'ethereum': 25910254, 'base': 50905727, 'arbitrum': 501959324,
        'optimism': 156501012}
POOLS = {
    'ethereum': ['0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640',
                 '0xe0554a476a092703abdb3ef35c80e0d76d32939f',
                 '0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b'],
    'base': ['0xb2cc224c1c9fee385f8ad6a55b4d94e92359dc59',
             '0x4e962bb3889bf030368f56810a9c96b83cb3e778',
             '0xb5f0b4ae66c14f7efaa9aa1468e8fc536a3e288c'],
    'arbitrum': ['0xc6f780497a95e246eb9449f5e4770916dcd6396a',
                 '0xd13040d4fe917ee704158cfcb3338dcd2838b245'],
    'optimism': ['0x478946bcd4a5a22b316470f5486fafb928c0ba25'],
}


def selector(s):
    return topic(s)[:10]


def decode_string(v):
    if not isinstance(v, str) or not v.startswith('0x'):
        return None
    raw = bytes.fromhex(v[2:])
    if len(raw) == 32:
        text = raw.rstrip(b'\x00').decode(errors='replace')
    elif len(raw) >= 64:
        offset = int.from_bytes(raw[:32], 'big')
        if offset + 32 > len(raw):
            return None
        length = int.from_bytes(raw[offset:offset+32], 'big')
        if length > 512 or offset + 32 + length > len(raw):
            return None
        text = raw[offset+32:offset+32+length].decode(errors='replace')
    else:
        return None
    return ''.join(c if c.isprintable() else '?' for c in text)[:160]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rpc = RPC(OUT, max_credits=80000, interval=.8)
    metadata = json.loads((OUT/'metadata.json').read_text()) if (OUT/'metadata.json').exists() else {}
    for chain, pools in POOLS.items():
        if chain in metadata:
            continue
        block = rpc.call(chain, 'eth_getBlockByNumber', [hex(ENDS[chain]), False])
        tag = hex(ENDS[chain])
        info = {'asof_block': ENDS[chain], 'asof_hash': block['hash'], 'asof_utc': utc(hx(block['timestamp'])),
                'pools': {}, 'tokens': {}}
        for pool in pools:
            methods = ['token0()', 'token1()', 'factory()', 'fee()', 'tickSpacing()', 'liquidity()', 'slot0()']
            vals = rpc.batch(chain, [('eth_call', [{'to': pool, 'data': selector(m)}, tag]) for m in methods], allow_errors=True)
            rec = {'raw_calls': dict(zip(methods, vals)), 'address': pool}
            for i, m in enumerate(['token0', 'token1', 'factory']):
                v = vals[i]
                if isinstance(v, str) and len(v) == 66:
                    rec[m] = '0x' + v[-40:]
            for i, m in [(3, 'fee'), (4, 'tick_spacing'), (5, 'liquidity')]:
                if isinstance(vals[i], str) and len(vals[i]) == 66:
                    rec[m] = str(hx(vals[i]))
            info['pools'][pool] = rec
        tokens = sorted({rec[k] for rec in info['pools'].values() for k in ['token0', 'token1'] if k in rec})
        for token in tokens:
            methods = ['symbol()', 'name()', 'decimals()']
            vals = rpc.batch(chain, [('eth_call', [{'to': token, 'data': selector(m)}, tag]) for m in methods], allow_errors=True)
            info['tokens'][token] = {'symbol_untrusted': decode_string(vals[0]), 'name_untrusted': decode_string(vals[1]),
                                     'decimals': hx(vals[2]) if isinstance(vals[2], str) and len(vals[2]) == 66 else None,
                                     'raw_calls': dict(zip(methods, vals))}
        current = rpc.call(chain, 'eth_getBlockByNumber', [tag, False])
        info['asof_hash_rechecked'] = current['hash'] == info['asof_hash']
        metadata[chain] = info
        save(OUT/'metadata.json', metadata)
        print(json.dumps({'chain': chain, 'pool_metadata': len(pools), 'token_metadata': len(tokens)}), flush=True)

    if not (OUT / 'ethereum_factory_membership.json').exists():
        checks = []
        for pool, rec in metadata['ethereum']['pools'].items():
            data = selector('getPool(address,address,uint24)') + rec['token0'][2:].zfill(64) + rec['token1'][2:].zfill(64) + hex(int(rec['fee']))[2:].zfill(64)
            value = rpc.call('ethereum', 'eth_call', [{'to': '0x1f98431c8ad98523631ae4a59f267346ea31f984', 'data': data}, hex(ENDS['ethereum'])])
            checks.append({'pool': pool, 'factory': '0x1f98431c8ad98523631ae4a59f267346ea31f984',
                           'block': ENDS['ethereum'], 'call_data': data, 'result': value,
                           'membership_matches': '0x' + value[-40:] == pool})
        save(OUT / 'ethereum_factory_membership.json', checks)

    case_file = OUT / 'optimism_distribution_state.json'
    if not case_file.exists():
        n = 156500953
        with gzip.open(ROOT / 'research/2026-09-05/sample/raw/optimism/156500953.json.gz', 'rt') as f:
            block = json.load(f)
        txhash = '0x22b022eef97e2749a912f5a2c8051ffa5aab03f761ba95338d3a9b79df373e6a'
        receipt = next(r for r in block['receipts'] if r['transactionHash'] == txhash)
        logs = receipt['logs']
        token = logs[0]['address']
        recipients = ['0x' + x['topics'][3][-40:] for x in logs]
        samples = [recipients[i] for i in [0, len(recipients)//2, len(recipients)-1]]
        supports = selector('supportsInterface(bytes4)') + 'd9b67a26'.ljust(64, '0')
        calls = [('eth_call', [{'to': token, 'data': supports}, hex(n)])]
        specs = ['supports_erc1155']
        for addr in samples:
            for bn in [n-1, n]:
                data = selector('balanceOf(address,uint256)') + addr[2:].zfill(64) + hex(1)[2:].zfill(64)
                calls.append(('eth_call', [{'to': token, 'data': data}, hex(bn)]))
                specs.append({'recipient': addr, 'block': bn})
        result = rpc.batch('optimism', calls, allow_errors=True)
        save(case_file, {'transaction_hash': txhash, 'emitter': token, 'block_number': n,
                         'logs': len(logs), 'unique_recipients': len(set(recipients)),
                         'all_from_zero': all(hx(l['topics'][2]) == 0 for l in logs),
                         'token_id_and_amount_counts': dict(collections.Counter(l['data'] for l in logs)),
                         'state_checks': [{'query': q, 'result': r} for q, r in zip(specs, result)],
                         'state_scope': 'End of preceding block versus end of containing block; three sampled recipients.'})
        print('Optimism distribution state checks saved', flush=True)

    # Thirty-minute retrospective context, selected after seeing the two-minute sample.
    # This is explanatory context, not a held-out or unbiased validation sample.
    for chain in ['ethereum', 'base', 'arbitrum', 'optimism']:
        path = OUT / (chain + '_pool_context.json.gz')
        if path.exists():
            continue
        head = rpc.call(chain, 'eth_getBlockByNumber', [hex(ENDS[chain]), False])
        end_exclusive = 1788600803
        first = first_block_at(rpc, chain, end_exclusive - 1800, head)
        # Narrow emitter set; all event types preserved to see maintenance and swaps.
        logs = []
        ranges = []
        def get_range(a, b):
            result = rpc.call(chain, 'eth_getLogs', [{'address': POOLS[chain], 'fromBlock': hex(a), 'toBlock': hex(b)}], allow_errors=True)
            if isinstance(result, dict) and 'error' in result:
                if a == b:
                    raise ValueError('Single-block logs failed')
                mid = (a + b) // 2
                get_range(a, mid); get_range(mid+1, b)
                return
            if not isinstance(result, list):
                raise ValueError('Unexpected logs result')
            ranges.append({'from': a, 'to': b, 'logs': len(result)})
            logs.extend(result)
        # Arbitrum has a large number of blocks per unit of wall time.
        for a in range(first, ENDS[chain] + 1, 2000):
            get_range(a, min(a + 1999, ENDS[chain]))
        with gzip.open(path, 'wt') as f:
            json.dump({'chain': chain, 'start_block': first, 'end_block': ENDS[chain],
                       'start_timestamp': end_exclusive - 1800, 'end_timestamp_exclusive': end_exclusive,
                       'selected_addresses': POOLS[chain], 'ranges': ranges, 'logs': logs}, f)
        print(json.dumps({'chain': chain, 'context_logs': len(logs), 'context_start_block': first}), flush=True)


if __name__ == '__main__':
    if '--wait-for-sample' in sys.argv:
        for i in range(450):
            manifest = json.loads((ROOT / 'research/2026-09-05/sample/manifest.json').read_text())
            if not manifest.get('errors') and all('collection' in x for x in manifest['chains'].values()):
                break
            time.sleep(2)
        else:
            raise RuntimeError('Sample not complete within the wait limit')
    main()
