"""Check detector hits against canonical receipts and factory/reserve state; save bounded RPC evidence."""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[2] / 'scripts'))
from live_rpc import RPC, hx, word
from live_scan import sel, dec_str
from window_raw import Window

w = Window(OUT)
hits = [h for h in json.loads((OUT/'detectors.json').read_text())['hits']
        if h['detector'] == 'recycled_swap_volume']
old = {r['tx']: r for r in json.loads((OUT/'rpc_followup.json').read_text())['receipts']}
pools = json.loads((OUT/'pools.json').read_text())
rpc = RPC(log_path=OUT/'rpc_errors.jsonl', max_credits=15000)
rows = []
for hit in hits:
    pool = hit['key']
    tokens = pools[pool]['tokens']
    end = w.nums[-1]
    methods = [(pool, sel('factory()')), (tokens[0], sel('symbol()'))]
    factory_raw, symbol_raw = rpc.eth_calls(methods, hex(end))
    factory = '0x' + factory_raw[-40:]
    pair = rpc.eth_calls([(factory, sel('getPair(address,address)') +
                          tokens[0][2:].rjust(64,'0') + tokens[1][2:].rjust(64,'0'))], hex(end))[0]
    assert pair and '0x' + pair[-40:] == pool
    receipts = []
    for e in hit['evidence']['examples']:
        n, tx = e['block'], e['tx']
        b = w._read('blocks', n)
        r = old.get(tx)
        if r is None:
            raw = rpc.call('eth_getTransactionReceipt', [tx])
            gas, price = hx(raw['gasUsed']), hx(raw['effectiveGasPrice'])
            r = {'tx': tx, 'block': n, 'block_hash_matches': raw['blockHash'] == b['hash'],
                 'status': hx(raw['status']), 'gas_used': gas, 'effective_gas_gwei': price/1e9,
                 'priority_fee_eth': gas*(price-hx(b['baseFeePerGas']))/1e18,
                 'fee_eth': gas*price/1e18}
        assert r['block_hash_matches'] and r['status'] == 1
        receipts.append(r)
    reserves = []
    for n in [min(e['block'] for e in hit['evidence']['examples'])-1, end]:
        raw = rpc.eth_calls([(pool, sel('getReserves()'))], hex(n))[0]
        reserves.append({'block': n, 'raw': raw, 'values': [str(word(raw,i)) for i in range(3)]})
    priced_surplus = -sum(int(e['pool_net_priced_token_raw']) for e in hit['evidence']['examples'])/1e18
    # Independently sampled reserves must account for the entire WETH delta attributed by the log detector.
    assert tokens[1] == '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
    assert int(reserves[0]['values'][1]) - int(reserves[1]['values'][1]) == -sum(
        int(e['pool_net_priced_token_raw']) for e in hit['evidence']['examples'])
    fees = sum(r['fee_eth'] for r in receipts)
    rows.append({'pool':pool, 'symbol':dec_str(symbol_raw), 'tokens':tokens, 'factory':factory,
                 'factory_get_pair_matches':True, 'factory_get_pair_raw':pair,
                 'reserves':reserves, 'receipts':receipts,
                 'turnover_usd':hit['evidence']['gross_priced_leg_usd'],
                 'visible_weth_surplus_eth':priced_surplus, 'execution_fees_eth':fees,
                 'surplus_less_gas_usd':(priced_surplus-fees)*w.prices['ETH']})
result = {'window':str(OUT.relative_to(OUT.parents[2])), 'pinned_block':w.nums[-1], 'pools':rows,
          'note':'Surplus less gas omits other internal transfers/payments and unpriced assets; it is not complete operator profit.',
          'rpc':rpc.stats()}
(OUT/'roundtrip_evidence.json').write_text(json.dumps(result,indent=1))
print(json.dumps(result,indent=1))
