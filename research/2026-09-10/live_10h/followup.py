"""Bounded RPC evidence for the window's highest-priority transactions and recycled WETH pool."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from live_rpc import RPC, hx, word
from live_scan import sel, dec_str

out = Path(__file__).resolve().parent
events = json.loads((out / 'events.json').read_text())
analysis = json.loads((out / 'analysis.json').read_text())
manifest = json.loads((out / 'manifest.json').read_text())
pool = '0xcb62c2d6894736d4216a41f5812bb9771de056d5'
swaps = [s for s in analysis['big_swaps'] if s['pool'] == pool]
txs = list(dict.fromkeys([s['tx'] for s in swaps] + [r['tx'] for r in events['urgent'][:5]]))
rpc = RPC(log_path=out/'rpc_errors.jsonl', max_credits=30000)
result = {'block': manifest['last_block'], 'receipts': [], 'canonical_hashes': [], 'calls': []}
nums = list(range(manifest['first_block'], manifest['last_block'] + 1, 500)) + [manifest['last_block']]
headers = json.loads((out/'blocks_manifest.json').read_text())['blocks']
hashes = {r['number']: r['hash'] for r in headers}
for n in nums:
    b = rpc.call('eth_getBlockByNumber', [hex(n), False])
    result['canonical_hashes'].append({'block': n, 'hash': b['hash'], 'matches': b['hash'] == hashes[n]})
for tx in txs:
    r = rpc.call('eth_getTransactionReceipt', [tx])
    n = hx(r['blockNumber'])
    header = next(b for b in headers if b['number'] == n)
    gas, price = hx(r['gasUsed']), hx(r['effectiveGasPrice'])
    result['receipts'].append({'tx': tx, 'block': n, 'block_hash_matches': r['blockHash'] == hashes[n],
                               'status': hx(r['status']), 'gas_used': gas, 'effective_gas_gwei': price/1e9,
                               'priority_fee_eth': gas * (price - header['base_fee_wei'])/1e18,
                               'fee_eth': gas * price/1e18})
calls = [(pool, m, manifest['last_block']) for m in ['factory()', 'token0()', 'token1()', 'getReserves()']]
calls += [(pool, 'getReserves()', min(s['block'] for s in swaps)-1)]
for token in ['0x622b6330f226bf08427dcad49c9ea9694604bf2d', '0x241ef98233ba8e525c3a77cfd561f36d3962ec0c',
              '0xa12cc123ba206d4031d1c7f6223d1c2ec249f4f3']:
    calls += [(token, m, manifest['last_block']) for m in ['symbol()', 'decimals()']]
for address, method, n in calls:
    r = rpc.eth_calls([(address, sel(method))], hex(n))[0]
    decoded = dec_str(r) if r and method == 'symbol()' else ([word(r,i) for i in range(3)] if r and method == 'getReserves()'
               else ('0x'+r[-40:] if r and method in ['factory()', 'token0()', 'token1()'] else word(r,0) if r else None))
    result['calls'].append({'address': address, 'method': method, 'block': n, 'raw': r, 'decoded': decoded})
result['rpc'] = rpc.stats()
(out/'rpc_followup.json').write_text(json.dumps(result, indent=1))
manifest['hash_recheck'] = {'sampled': len(nums), 'mismatches': [x['block'] for x in result['canonical_hashes'] if not x['matches']]}
(out/'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True))
print(json.dumps(result, indent=1))
if manifest['hash_recheck']['mismatches']:
    raise SystemExit('canonical hash mismatch')
