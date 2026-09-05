"""Recompute memo facts and check the saved evidence without network access."""
import collections
from decimal import Decimal, getcontext
import gzip
import hashlib
import json
from pathlib import Path
from onchain_probe import ROOT, hx, save, validate, utc
from analyze_onchain import decode

BASE = ROOT / 'research/2026-09-05'
getcontext().prec = 60


def main():
    summary = json.loads((BASE / 'analysis/summary.json').read_text())
    with gzip.open(BASE / 'analysis/transactions.jsonl.gz', 'rt') as f:
        txs = [json.loads(l) for l in f]
    with gzip.open(BASE / 'analysis/events.jsonl.gz', 'rt') as f:
        events = [json.loads(l) for l in f]
    manifest = json.loads((BASE / 'sample/manifest.json').read_text())
    evidence = {'generated_at': utc(), 'chains': {}, 'cases': {}}
    for chain, s in summary.items():
        c = s['counts']
        rows = [t for t in txs if t['chain'] == chain]
        es = [e for e in events if e['chain'] == chain]
        burns = [e for e in es if e['family'] == 'V3Burn' and 'liquidity_delta' in e]
        mints = [e for e in es if e['family'] == 'V3Mint' and 'liquidity_delta' in e]
        system = [r for r in rows if (chain == 'arbitrum' and r['type'] == '0x6a') or
                  (chain in ['base', 'optimism'] and r['to'] == '0x4200000000000000000000000000000000000015')]
        data = {'blocks': c['blocks'], 'transactions': c['transactions'], 'receipts': c['receipts'],
                'logs': c['logs'], 'failed': c['failed'], 'failure_pct': s['failure_pct'],
                'unique_senders': s['unique_senders'], 'known_system_transactions': len(system),
                'failure_pct_excluding_known_system': 100 * (c['failed']-sum(t['failed'] for t in system)) / (len(rows)-len(system)),
                'raw_json_bytes': s['raw_json_bytes'], 'quality_issues': s['quality_issues'],
                'v3_burn_events': len(burns), 'v3_zero_burn_events': sum(e['liquidity_delta'] == '0' for e in burns),
                'v3_mint_events': len(mints), 'swap_events': sum(t['swaps'] for t in rows),
                'swap_transactions': sum(t['swaps'] > 0 for t in rows),
                'multiple_swap_transactions': sum(t['swaps'] > 1 for t in rows)}
        chainfile = BASE / 'sample' / (chain + '_manifest.json')
        if chainfile.exists():
            cm = json.loads(chainfile.read_text())
            data['canonical_hash_changes'] = cm['hash_changes_on_recheck']
            finalized = cm.get('finalized_at_recheck') or {}
            data['finalized_head_at_recheck'] = hx(finalized['number']) if 'number' in finalized else None
            data['entire_window_finalized_at_recheck'] = bool('number' in finalized and hx(finalized['number']) >= cm['last_block'])
            checks = collections.Counter()
            previous = None
            nums = []
            for b in cm['block_files']:
                path = BASE / 'sample' / b['file']
                checks['sha256_mismatches'] += hashlib.sha256(path.read_bytes()).hexdigest() != b['sha256']
                with gzip.open(path, 'rt') as f:
                    raw = json.load(f)
                block = raw['block']
                nums.append(hx(block['number']))
                checks['validation_issue_count'] += len(validate(block, raw['receipts'], chain))
                checks['outside_window'] += not (manifest['start_timestamp'] <= hx(block['timestamp']) < manifest['end_timestamp'])
                if previous:
                    checks['parent_mismatches'] += block['parentHash'] != previous
                previous = block['hash']
                cumulative = 0
                for r in sorted(raw['receipts'], key=lambda r: hx(r['transactionIndex'])):
                    cumulative += hx(r['gasUsed'])
                    checks['cumulative_gas_mismatches'] += cumulative != hx(r['cumulativeGasUsed'])
            checks['block_range_mismatch'] = nums != list(range(cm['first_block'], cm['last_block'] + 1))
            data['offline_integrity_checks'] = dict(checks)
        evidence['chains'][chain] = data

    op_es = [e for e in events if e['chain'] == 'optimism' and e['emitter'] == '0xb607c2d3896084128cb25a36d71959691e5a606c']
    op_rec = {e['recipient'] for e in op_es if 'recipient' in e}
    op_txs = {e['transaction_hash'] for e in op_es}
    evidence['cases']['optimism_distribution'] = {
        'logs_from_emitter': len(op_es), 'transactions': len(op_txs), 'unique_recipients': len(op_rec),
        'share_of_optimism_logs_pct': 100 * len(op_es) / summary['optimism']['counts']['logs'],
        'logs_per_transaction': dict(collections.Counter(e['transaction_hash'] for e in op_es)),
        'all_from_zero': all(e.get('sender') == '0x' + '0'*40 for e in op_es),
        'unique_token_ids': sorted({e.get('token_id') for e in op_es if 'token_id' in e})}

    poly = [e for e in events if e['chain'] == 'polygon' and e['family'] == 'CTFv2OrderFilled_shape']
    matches = [e for e in events if e['chain'] == 'polygon' and e['family'] == 'CTFv2OrdersMatched_shape']
    official = {'0xe111180000d2663c0091e4f400237545b87b996b', '0xe2222d279d744050d28e00520010520000310f59',
                '0xe3333700ca9d93003f00f0f71f8515005f6c00aa'}
    pc = {'official_fill_events': sum(e['emitter'] in official for e in poly),
          'official_match_events': sum(e['emitter'] in official for e in matches),
          'transactions_with_official_fills': len({e['transaction_hash'] for e in poly if e['emitter'] in official}),
          'unique_maker_addresses': len({e['maker'] for e in poly if e['emitter'] in official}),
          'unique_outcome_token_ids': len({e['token_id'] for e in poly if e['emitter'] in official}),
          'top_token_ids': collections.Counter(e['token_id'] for e in poly if e['emitter'] in official).most_common(5),
          'same_shape_on_base': sum(e['chain'] == 'base' and e['family'] == 'CTFv2OrderFilled_shape' for e in events)}
    evidence['cases']['polymarket'] = pc

    meta_path = BASE / 'followup/metadata.json'
    if meta_path.exists():
        metadata = json.loads(meta_path.read_text())
        pools = []
        for chain, meta in metadata.items():
            for addr, pool in meta['pools'].items():
                if not all(k in pool for k in ['token0', 'token1']):
                    continue
                d0 = meta['tokens'][pool['token0']]['decimals']; d1 = meta['tokens'][pool['token1']]['decimals']
                v3 = [e for e in events if e['chain'] == chain and e['emitter'] == addr and e['family'] == 'V3Swap' and 'amount0_raw' in e]
                if d0 is None or d1 is None:
                    continue
                rec = {'chain': chain, 'pool': addr, 'token0': pool['token0'], 'token1': pool['token1'],
                       'symbol0_untrusted': meta['tokens'][pool['token0']]['symbol_untrusted'],
                       'symbol1_untrusted': meta['tokens'][pool['token1']]['symbol_untrusted'],
                       'decimals0': d0, 'decimals1': d1, 'fee_millionths_at_end': pool.get('fee'),
                       'swap_events_in_discovery': len(v3),
                       'pool_net_token0_from_swaps': str(sum(Decimal(e['amount0_raw']) for e in v3) / Decimal(10)**d0),
                       'pool_net_token1_from_swaps': str(sum(Decimal(e['amount1_raw']) for e in v3) / Decimal(10)**d1)}
                slot = pool['raw_calls'].get('slot0()')
                if isinstance(slot, str) and len(slot) >= 66:
                    sq = hx(slot[:66])
                    p = (Decimal(sq)/Decimal(2**96))**2 * Decimal(10)**(d0-d1)
                    rec['end_token1_per_token0'] = str(p)
                    if pool['token0'] == '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' and pool['token1'] == '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2':
                        rec['end_usdc_per_weth'] = str(1/p)
                pools.append(rec)
        evidence['cases']['selected_pools'] = pools
        prices = [Decimal(p['end_usdc_per_weth']) for p in pools if 'end_usdc_per_weth' in p]
        if len(prices) == 2:
            evidence['cases']['ethereum_usdc_weth_gap_bps'] = str((max(prices)/min(prices)-1)*10000)
        # Compare the two event-based ledgers after excluding known non-swap effects.
        # Equality is diagnostic, not a protocol invariant: callbacks may overpay.
        groups = collections.defaultdict(list)
        eth_pools = metadata.get('ethereum', {}).get('pools', {})
        for e in events:
            if e['chain'] == 'ethereum':
                groups[e['transaction_hash']].append(e)
        reconciliation = {'checked_pool_transactions': 0, 'matched': 0, 'mismatches': []}
        for txhash, group in groups.items():
            for pool, info in eth_pools.items():
                swaps = [e for e in group if e['emitter'] == pool and e['family'] == 'V3Swap' and 'amount0_raw' in e]
                if not swaps or any(e['emitter'] == pool and e['family'] in ['V3Mint', 'V3Burn', 'V3Collect', 'V3Flash'] for e in group):
                    continue
                reconciliation['checked_pool_transactions'] += 1
                actual = []
                expected = []
                for idx in [0, 1]:
                    token = info['token'+str(idx)]
                    transfers = [e for e in group if e['emitter'] == token and e['family'] == 'ERC20_Transfer_shape']
                    net = sum(int(e['amount_raw']) * ((e['recipient'] == pool) - (e['sender'] == pool)) for e in transfers)
                    actual.append(net)
                    expected.append(sum(int(e['amount'+str(idx)+'_raw']) for e in swaps))
                if actual == expected:
                    reconciliation['matched'] += 1
                else:
                    reconciliation['mismatches'].append({'pool':pool,'transaction':txhash,'transfer_net':list(map(str,actual)),
                                                         'swap_delta':list(map(str,expected)),
                                                         'transfer_minus_swap_raw':list(map(str,[a-b for a,b in zip(actual,expected)])),
                                                         'tokens':[info['token0'],info['token1']],
                                                         'swap_log_indices':[e['log_index'] for e in swaps]})
        evidence['cases']['swap_transfer_reconciliation'] = reconciliation

    contexts = {}
    for path in (BASE/'followup').glob('*_pool_context.json.gz'):
        with gzip.open(path,'rt') as f:
            context = json.load(f)
        logs = context['logs']
        ds = [{**decode(l), 'emitter': l['address'], 'transaction_hash': l['transactionHash'], 'block_number': hx(l['blockNumber'])} for l in logs]
        pools = {}
        for addr in context['selected_addresses']:
            subset = [e for e in ds if e['emitter'].lower() == addr]
            burns = [e for e in subset if e['family']=='V3Burn' and 'liquidity_delta' in e]
            swaps = [e for e in subset if e['family']=='V3Swap' and 'tick' in e]
            pools[addr] = {'events': len(subset), 'families': dict(collections.Counter(e['family'] for e in subset)),
                           'burns': len(burns), 'zero_burns': sum(e['liquidity_delta']=='0' for e in burns),
                           'min_swap_tick': min((e['tick'] for e in swaps), default=None),
                           'max_swap_tick': max((e['tick'] for e in swaps), default=None)}
        logids=[(l['blockHash'],l['transactionHash'],hx(l['logIndex'])) for l in logs]
        selected = set(context['selected_addresses'])
        first_discovery = summary[context['chain']]['first_block']
        discovery_ids = {(e['block_hash'],e['transaction_hash'],e['log_index']) for e in events
                         if e['chain']==context['chain'] and e['emitter'] in selected}
        overlap_ids = {(l['blockHash'],l['transactionHash'],hx(l['logIndex'])) for l in logs
                       if hx(l['blockNumber'])>=first_discovery}
        ranges = sorted(context['ranges'],key=lambda r:r['from'])
        range_gaps = int(not ranges or ranges[0]['from']!=context['start_block'] or ranges[-1]['to']!=context['end_block'])
        range_gaps += sum(a['to']+1!=b['from'] for a,b in zip(ranges,ranges[1:]))
        contexts[context['chain']]={'start_block':context['start_block'],'end_block':context['end_block'],
                                    'logs':len(logs),'duplicates':len(logids)-len(set(logids)),
                                    'removed':sum(bool(l.get('removed')) for l in logs),
                                    'request_range_gaps':range_gaps,
                                    'out_of_range':sum(not(context['start_block']<=hx(l['blockNumber'])<=context['end_block']) for l in logs),
                                    'unexpected_emitters':sum(l['address'].lower() not in selected for l in logs),
                                    'discovery_overlap_missing':len(discovery_ids-overlap_ids),
                                    'discovery_overlap_extra':len(overlap_ids-discovery_ids),'pools':pools}
    evidence['contexts']=contexts
    reqs=[]
    for directory in ['sample','followup','diagnostic']:
        p=BASE/directory/'rpc_requests.jsonl'
        if p.exists():
            reqs.extend(json.loads(l) for l in p.read_text().splitlines())
    evidence['rpc']={'http_attempts':len(reqs),'logical_method_attempts':sum(len(r['calls']) for r in reqs),
                     'estimated_credits_upper_bound':sum(r['estimated_credits'] for r in reqs),
                     'response_bytes_including_retries':sum(r['response_bytes'] for r in reqs),
                     'http_attempts_with_error':sum(bool(r['error']) for r in reqs)}
    evidence['representation']={'raw_json_bytes':sum(s['raw_json_bytes'] for s in summary.values()),
                                 'candidate_file_bytes':(BASE/'analysis/candidates.json').stat().st_size,
                                 'candidate_transactions':len(json.loads((BASE/'analysis/candidates.json').read_text())),
                                 'summary_file_bytes':(BASE/'analysis/summary.json').stat().st_size}
    save(BASE/'analysis/research_evidence.json',evidence)
    print(json.dumps({'chains':evidence['chains'],'cases':{k:v for k,v in evidence['cases'].items() if k not in ['selected_pools','optimism_distribution']},
                      'rpc':evidence['rpc'],'representation':evidence['representation'],'contexts':contexts},indent=2))


if __name__=='__main__':
    main()
