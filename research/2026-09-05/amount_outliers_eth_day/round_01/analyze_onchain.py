#!/usr/bin/env python3
"""Offline descriptive features and candidate packets. No profitability claims."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import statistics
from Crypto.Hash import keccak
from onchain_probe import ROOT, hx, save, utc, validate, is_polygon_fee_log

RUN = ROOT / 'research/2026-09-05/sample'
OUT = ROOT / 'research/2026-09-05/analysis'
SIGNATURES = {
    'Transfer': 'Transfer(address,address,uint256)',
    'Approval': 'Approval(address,address,uint256)',
    'V2Swap': 'Swap(address,uint256,uint256,uint256,uint256,address)',
    'V2Sync': 'Sync(uint112,uint112)',
    'V2Mint': 'Mint(address,uint256,uint256)',
    'V2Burn': 'Burn(address,uint256,uint256,address)',
    'V3Swap': 'Swap(address,address,int256,int256,uint160,uint128,int24)',
    'V3Mint': 'Mint(address,address,int24,int24,uint128,uint256,uint256)',
    'V3Burn': 'Burn(address,int24,int24,uint128,uint256,uint256)',
    'V3Collect': 'Collect(address,address,int24,int24,uint128,uint128)',
    'V3Flash': 'Flash(address,address,uint256,uint256,uint256,uint256)',
    'V4Swap': 'Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)',
    'V4ModifyLiquidity': 'ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)',
    'AaveLiquidation': 'LiquidationCall(address,address,address,uint256,uint256,address,bool)',
    'AaveSupply': 'Supply(address,address,address,uint256,uint16)',
    'AaveBorrow': 'Borrow(address,address,address,uint256,uint8,uint256,uint16)',
    'AaveRepay': 'Repay(address,address,address,uint256,bool)',
    'ERC4626Deposit': 'Deposit(address,address,uint256,uint256)',
    'ERC4626Withdraw': 'Withdraw(address,address,address,uint256,uint256)',
    'WETHDeposit': 'Deposit(address,uint256)',
    'WETHWithdrawal': 'Withdrawal(address,uint256)',
    'ERC1155TransferSingle': 'TransferSingle(address,address,address,uint256,uint256)',
    'ERC1155TransferBatch': 'TransferBatch(address,address,address,uint256[],uint256[])',
    'UserOperation': 'UserOperationEvent(bytes32,address,address,uint256,bool,uint256,uint256)',
    'CTFv2OrderFilled_shape': 'OrderFilled(bytes32,address,address,uint8,uint256,uint256,uint256,uint256,bytes32,bytes32)',
    'CTFv2OrdersMatched_shape': 'OrdersMatched(bytes32,address,uint8,uint256,uint256,uint256)',
}


def topic(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()


TOPICS = {topic(s): name for name, s in SIGNATURES.items()}


def signed(x):
    return x - 2**256 if x >= 2**255 else x


def address(s):
    return '0x' + s[-40:].lower()


def decode(log):
    """Structural matches are candidate semantics, not verified protocol identity."""
    ts, data = log.get('topics', []), log.get('data', '0x')[2:]
    if not ts or len(data) % 64:
        return {'family': 'unknown'}
    name = TOPICS.get(ts[0], 'unknown')
    words = [int(data[i:i+64], 16) for i in range(0, len(data), 64)]
    result = {'family': name}
    if name == 'Transfer':
        if len(ts) == 3 and len(words) == 1:
            result.update(family='ERC20_Transfer_shape', sender=address(ts[1]), recipient=address(ts[2]), amount_raw=str(words[0]))
        elif len(ts) == 4 and not words:
            result.update(family='ERC721_Transfer_shape', sender=address(ts[1]), recipient=address(ts[2]), token_id=str(hx(ts[3])))
        else:
            result['family'] = 'Transfer_unrecognized_shape'
    elif name == 'V3Swap' and len(ts) == 3 and len(words) == 5:
        result.update(sender=address(ts[1]), recipient=address(ts[2]), amount0_raw=str(signed(words[0])),
                      amount1_raw=str(signed(words[1])), sqrtPriceX96=str(words[2]), liquidity=str(words[3]), tick=signed(words[4]))
    elif name == 'V4Swap' and len(ts) == 3 and len(words) == 6:
        result.update(pool_id=ts[1], sender=address(ts[2]), amount0_raw=str(signed(words[0])),
                      amount1_raw=str(signed(words[1])), sqrtPriceX96=str(words[2]), liquidity=str(words[3]),
                      tick=signed(words[4]), fee=words[5])
    elif name == 'V2Swap' and len(ts) == 3 and len(words) == 4:
        result.update(sender=address(ts[1]), recipient=address(ts[2]),
                      amount0_in_raw=str(words[0]), amount1_in_raw=str(words[1]),
                      amount0_out_raw=str(words[2]), amount1_out_raw=str(words[3]))
    elif name == 'V3Mint' and len(ts) == 4 and len(words) == 4:
        result.update(owner=address(ts[1]), tick_lower=signed(hx(ts[2])), tick_upper=signed(hx(ts[3])),
                      liquidity_delta=str(words[1]), amount0_raw=str(words[2]), amount1_raw=str(words[3]))
    elif name == 'V3Burn' and len(ts) == 4 and len(words) == 3:
        result.update(owner=address(ts[1]), tick_lower=signed(hx(ts[2])), tick_upper=signed(hx(ts[3])),
                      liquidity_delta=str(-words[0]), amount0_raw=str(words[1]), amount1_raw=str(words[2]))
    elif name == 'V4ModifyLiquidity' and len(ts) == 3 and len(words) == 4:
        result.update(pool_id=ts[1], owner=address(ts[2]), tick_lower=signed(words[0]), tick_upper=signed(words[1]),
                      liquidity_delta=str(signed(words[2])), salt=hex(words[3]))
    elif name == 'ERC1155TransferSingle' and len(ts) == 4 and len(words) == 2:
        result.update(operator=address(ts[1]), sender=address(ts[2]), recipient=address(ts[3]),
                      token_id=str(words[0]), amount_raw=str(words[1]))
    elif name == 'CTFv2OrderFilled_shape' and len(ts) == 4 and len(words) == 7:
        result.update(order_hash=ts[1], maker=address(ts[2]), taker=address(ts[3]),
                      side=words[0], token_id=str(words[1]), maker_amount_raw=str(words[2]),
                      taker_amount_raw=str(words[3]), fee_raw=str(words[4]))
    elif name == 'CTFv2OrdersMatched_shape' and len(ts) == 3 and len(words) == 4:
        result.update(order_hash=ts[1], taker_order_maker=address(ts[2]), side=words[0],
                      token_id=str(words[1]), maker_amount_raw=str(words[2]), taker_amount_raw=str(words[3]))
    return result


def top(counter, n=12):
    return [{'key': k, 'count': v} for k, v in counter.most_common(n)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary, candidates, all_tx, all_events = {}, [], [], []
    for cp in sorted((RUN / 'raw').iterdir()):
        if not cp.is_dir():
            continue
        chain = cp.name
        counts = collections.Counter()
        topics, emitters, families, senders, destinations, selectors = [collections.Counter() for _ in range(6)]
        failed_from, failed_to, failed_selector, pools, tokens = [collections.Counter() for _ in range(5)]
        quality, receipt_methods, tx_types = [collections.Counter() for _ in range(3)]
        fees, gas, tx_rows, times, utilizations, block_nums, raw_bytes = [], [], [], [], [], [], 0
        failed_gas, failed_fees = 0, 0
        for path in sorted(cp.glob('*.gz'), key=lambda p: int(p.name.split('.')[0])):
            with gzip.open(path, 'rt') as f:
                content = f.read()
                data = json.loads(content)
            raw_bytes += len(content.encode())
            block, receipts = data['block'], data['receipts']
            quality.update(validate(block, receipts, chain))
            receipt_methods[data['receipt_method']] += 1
            times.append(hx(block['timestamp']))
            block_nums.append(hx(block['number']))
            utilizations.append(hx(block['gasUsed']) / hx(block['gasLimit']))
            txs = {x['hash']: x for x in block['transactions']}
            counts['blocks'] += 1
            counts['transactions'] += len(txs)
            counts['receipts'] += len(receipts)
            for r in receipts:
                t = txs.get(r['transactionHash'])
                if not t:
                    counts['receipts_not_in_block_body'] += 1
                    continue
                sender, dest = t['from'].lower(), (t.get('to') or '[creation]').lower()
                sel = t.get('input', '0x')[:10]
                failure = hx(r.get('status', 1)) == 0
                g = hx(r['gasUsed'])
                f = g * hx(r.get('effectiveGasPrice', t.get('gasPrice', 0)))
                l1fee = hx(r.get('l1Fee', 0))
                blobfee = hx(r.get('blobGasUsed', 0)) * hx(r.get('blobGasPrice', 0))
                gas.append(g); fees.append(f)
                senders[sender] += 1; destinations[dest] += 1; selectors[sel] += 1
                tx_types[t.get('type', 'missing')] += 1
                counts['failed'] += failure
                counts['receipt_l1_fee_wei'] += l1fee
                counts['receipt_blob_fee_wei'] += blobfee
                counts['receipts_with_l1Fee'] += 'l1Fee' in r
                counts['receipts_with_operatorFee'] += 'operatorFee' in r
                if failure:
                    failed_from[sender] += 1; failed_to[dest] += 1; failed_selector[sel] += 1
                    failed_gas += g; failed_fees += f
                evs = []
                transfer_targets = set()
                transfer_amounts = collections.Counter()
                for log in r.get('logs', []):
                    dec = decode(log)
                    if chain == 'polygon' and is_polygon_fee_log(log):
                        dec = {'family': 'Polygon_native_fee_log'}
                        counts['native_fee_logs_in_failed_receipts'] += failure
                    ev = {'chain': chain, 'block_number': hx(block['number']), 'block_hash': block['hash'],
                          'timestamp': hx(block['timestamp']), 'transaction_hash': t['hash'],
                          'transaction_index': hx(t['transactionIndex']), 'log_index': hx(log['logIndex']),
                          'emitter': log['address'].lower(), 'topic0': log['topics'][0] if log['topics'] else None,
                          **dec}
                    evs.append(ev); all_events.append(ev)
                    counts['logs'] += 1
                    families[dec['family']] += 1
                    emitters[ev['emitter']] += 1
                    topics[ev['topic0']] += 1
                    if dec['family'] in ('V2Swap', 'V3Swap', 'V4Swap'):
                        pools[ev['emitter']] += 1
                    if dec['family'] == 'ERC20_Transfer_shape':
                        tokens[ev['emitter']] += 1
                        transfer_targets.add(dec['recipient'])
                        transfer_amounts[(ev['emitter'], dec['amount_raw'])] += 1
                        counts['zero_value_erc20_transfers'] += dec['amount_raw'] == '0'
                swaps = [e for e in evs if e['family'] in ('V2Swap', 'V3Swap', 'V4Swap')]
                transfers = [e for e in evs if e['family'] == 'ERC20_Transfer_shape']
                row = {'chain': chain, 'block_number': hx(block['number']), 'timestamp': hx(block['timestamp']),
                       'transaction_hash': t['hash'], 'transaction_index': hx(t['transactionIndex']),
                       'sender': sender, 'to': dest, 'selector': sel, 'type': t.get('type'), 'failed': failure,
                       'gas_used': g, 'execution_fee_wei': str(f), 'receipt_l1_fee_wei': str(l1fee),
                       'receipt_blob_fee_wei': str(blobfee), 'logs': len(evs), 'swaps': len(swaps),
                       'distinct_swap_emitters': len({e['emitter'] for e in swaps}),
                       'erc20_transfer_logs': len(transfers), 'transfer_recipients': len(transfer_targets),
                       'max_repeated_token_amount': max(transfer_amounts.values(), default=0),
                       'families': dict(collections.Counter(e['family'] for e in evs)),
                       'raw_file': str(path.relative_to(ROOT))}
                tx_rows.append(row); all_tx.append(row)
        n = counts['transactions']
        summary[chain] = {'counts': dict(counts), 'first_block': min(block_nums), 'last_block': max(block_nums),
                          'first_timestamp': min(times), 'last_timestamp': max(times),
                          'first_utc': utc(min(times)), 'last_utc': utc(max(times)),
                          'unique_senders': len(senders), 'unique_direct_destinations': len(destinations),
                          'failure_pct': round(100 * counts['failed'] / n, 4),
                          'failed_execution_gas_pct': round(100 * failed_gas / sum(gas), 4),
                          'execution_fee_wei_sum': str(sum(fees)), 'failed_execution_fee_wei_sum': str(failed_fees),
                          'execution_fee_wei_median': str(int(statistics.median(fees))),
                          'mean_block_gas_utilization': statistics.mean(utilizations),
                          'zero_log_tx_count': sum(t['logs'] == 0 for t in tx_rows),
                          'tx_with_swaps': sum(t['swaps'] > 0 for t in tx_rows),
                          'tx_with_multiple_swap_events': sum(t['swaps'] > 1 for t in tx_rows),
                          'top_senders': top(senders), 'top_direct_destinations': top(destinations),
                          'top_selectors': top(selectors), 'top_failed_senders': top(failed_from),
                          'top_failed_destinations': top(failed_to), 'top_failed_selectors': top(failed_selector),
                          'families': dict(families), 'top_topics': top(topics, 30),
                          'top_emitters': top(emitters, 20), 'swap_emitters': top(pools, 30),
                          'transfer_tokens': top(tokens, 25), 'quality_issues': dict(quality),
                          'receipt_methods': dict(receipt_methods), 'tx_types': dict(tx_types),
                          'raw_json_bytes': raw_bytes, 'sample_complete': (RUN / (chain + '_manifest.json')).exists()}
        selected = {}
        metrics = ['logs', 'swaps', 'transfer_recipients', 'max_repeated_token_amount', 'gas_used']
        for metric in metrics:
            for row in sorted(tx_rows, key=lambda r: r[metric], reverse=True)[:3]:
                selected.setdefault(row['transaction_hash'], {'selection_reasons': [], **row})['selection_reasons'].append(metric)
        for row in sorted(tx_rows, key=lambda r: hashlib.sha256(r['transaction_hash'].encode()).hexdigest())[:3]:
            selected.setdefault(row['transaction_hash'], {'selection_reasons': [], **row})['selection_reasons'].append('deterministic_hash_control')
        if failed_from:
            leader = failed_from.most_common(1)[0][0]
            for row in [r for r in tx_rows if r['sender'] == leader and r['failed']][:3]:
                selected.setdefault(row['transaction_hash'], {'selection_reasons': [], **row})['selection_reasons'].append('top_failed_sender')
        candidates.extend(selected.values())
    save(OUT / 'summary.json', summary)
    save(OUT / 'candidates.json', candidates)
    save(OUT / 'event_signatures.json', {topic(s): {'name': n, 'signature': s} for n, s in SIGNATURES.items()})
    for name, rows in [('transactions', all_tx), ('events', all_events)]:
        with gzip.open(OUT / (name + '.jsonl.gz'), 'wt') as f:
            for r in rows:
                f.write(json.dumps(r, separators=(',', ':')) + '\n')
    print(json.dumps({c: {'blocks':s['counts']['blocks'],'transactions':s['counts']['transactions'],
                          'logs':s['counts']['logs'],'quality_issues':s['quality_issues'],
                          'sample_complete':s['sample_complete']} for c,s in summary.items()},indent=2))


if __name__ == '__main__':
    main()
