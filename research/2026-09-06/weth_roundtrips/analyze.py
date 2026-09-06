"""Offline accounting, cross-checking receipts, call traces and transaction state diffs."""
import collections
import json
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'raw'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
DEPOSIT = '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'
WITHDRAWAL = '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'

def read(name):
    return json.loads((RAW / (name + '.json')).read_text())

def hx(x):
    return int(x or '0x0', 16)

def string(x):
    b = bytes.fromhex(x[2:])
    return b[64:64 + int.from_bytes(b[32:64])].decode()

def walk(c, failed=False):
    failed = failed or bool(c.get('error'))
    if not failed:
        yield c
    for x in c.get('calls', []):
        yield from walk(x, failed)

def eth(wei):
    return str(Decimal(wei) / 10**18)

rows = []
assert string(read('eth_usd_description')) == 'ETH / USD'
feed_decimals = hx(read('eth_usd_decimals'))
for h in json.loads((HERE / 'transactions.json').read_text()):
    local = read(h + '_local')
    tx, block, logs = local['tx'], local['block'], local['logs']
    receipt, trace, diff = [read(h + '_' + suffix) for suffix in ('receipt', 'trace', 'diff')]
    assert receipt['logs'] == logs and receipt['blockHash'] == block['hash']
    assert hx(receipt['status']) == 1 and not trace.get('error')
    calls = list(walk(trace))
    bot, sender, builder = tx['to'], tx['from'], block['miner']
    payouts = [c for c in calls if c['type'] == 'CALL' and c['from'] == bot
               and c.get('input') == '0x' and hx(c.get('value'))]
    actors = {bot, sender} | {c['to'] for c in payouts if c['to'] != builder}
    native = 0
    for a in actors:
        pre, post = diff['pre'].get(a, {}), diff['post'].get(a, {})
        if 'balance' in post:
            native += hx(post['balance']) - hx(pre.get('balance'))
        else:
            assert 'balance' not in pre, (a, pre, post)
    trace_net = 0
    for c in calls:
        if c['type'] not in ('CALL', 'CREATE', 'CREATE2', 'SELFDESTRUCT'):
            continue
        value = hx(c.get('value'))
        trace_net += value * ((c.get('to') in actors) - (c.get('from') in actors))
    gas = hx(receipt['gasUsed']) * hx(receipt['effectiveGasPrice'])
    assert trace_net - gas == native
    bribe = sum(hx(c['value']) for c in payouts if c['to'] == builder)
    token_net = collections.Counter()
    for l in logs:
        tp = l['topics']
        if tp and tp[0] == TRANSFER and len(tp) == 3:
            value = hx(l['data'])
            token_net[l['address']] += value * (('0x' + tp[2][-40:] in actors) - ('0x' + tp[1][-40:] in actors))
        elif l['address'] == WETH and tp and tp[0] in (DEPOSIT, WITHDRAWAL) and '0x' + tp[1][-40:] in actors:
            token_net[WETH] += hx(l['data']) * (1 if tp[0] == DEPOSIT else -1)
    net_tokens = {}
    for a, value in token_net.items():
        sym = string(read(a + '_symbol'))
        decimals = hx(read(a + '_decimals'))
        net_tokens[sym] = str(Decimal(value) / 10**decimals)
    assert all(abs(Decimal(value)) <= Decimal('0.000002') for value in net_tokens.values())
    n = hx(block['number'])
    oracle = read(str(n) + '_eth_usd')[2:]
    words = [int(oracle[i:i+64], 16) for i in range(0, len(oracle), 64)]
    price = Decimal(words[1]) / 10**feed_decimals
    assert 0 < words[3] <= hx(block['timestamp']) and words[4] >= words[0]
    amounts = {'gross': native + gas + bribe, 'builder_payment': bribe, 'gas': gas, 'net': native}
    row = {'hash': h, 'block': n, 'transaction_index': hx(receipt['transactionIndex']),
           'sender': sender, 'bot': bot, 'builder': builder, 'accounted_addresses': sorted(actors),
           'gas_used': hx(receipt['gasUsed']), 'effective_gas_price_wei': hx(receipt['effectiveGasPrice']),
           'priority_fee_wei': hx(receipt['effectiveGasPrice']) - hx(block['baseFeePerGas']),
           'eth_usd': str(price), 'eth_usd_updated_at': words[3], 'token_dust_net': net_tokens,
           **{k + '_wei': str(v) for k, v in amounts.items()},
           **{k + '_eth': eth(v) for k, v in amounts.items()},
           **{k + '_usd': str(Decimal(v) / 10**18 * price) for k, v in amounts.items()}}
    rows.append(row)
    print(n, h[:8], ' '.join(f'{k} ${Decimal(row[k + "_usd"]):.6f}' for k in amounts), 'dust', net_tokens)
totals = {k + '_usd': str(sum(Decimal(r[k + '_usd']) for r in rows)) for k in amounts}
totals.update({k + '_eth': eth(sum(int(r[k + '_wei']) for r in rows)) for k in amounts})
result = {'method': 'Combined transaction-specific native balance changes of sender, execution contract and explicit non-builder payout recipients; cross-checked against successful native call flows minus receipt gas. Gross adds back gas and direct builder payment; pool fees already reflected in settlements. Token deltas are dust only.',
          'limitation': 'The five transactions only, excluding infrastructure and any other successful or failed transactions. Does not establish common ownership of different execution contracts. USD values mark native ETH at the historical Chainlink ETH/USD price; stablecoin dust excluded.',
          'rows': rows, 'totals': totals}
(HERE / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
print('TOTAL', totals)
