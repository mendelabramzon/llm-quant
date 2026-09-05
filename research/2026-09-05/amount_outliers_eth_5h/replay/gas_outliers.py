#!/usr/bin/env python3
"""Quant -> qual proof of concept over the saved discovery sample.

scan     Deterministic. Per chain, rank non-system transactions by gas limit, priority
         fee (effective gas price minus block base fee), and total fee paid. Select the
         top K per metric, compute robust baselines, and write evidence packets.
resolve  Bounded read-only RPC follow-up: token symbol/decimals and code presence for
         addresses that appear in the packets. Cached; keys never written to output.
render   Merge packets, resolved context, and LLM-written qual_notes.md into report.md.

The LLM reads packets.json, not raw blocks, and writes qual_notes.md. Exact numbers in
the report come from this code; the notes carry interpretation only.
"""
import argparse
import bisect
import collections
from decimal import Decimal
import gzip
import json
from pathlib import Path
import re
import statistics

from onchain_probe import ROOT, RPC, hx, save, utc, is_polygon_fee_log
from analyze_onchain import RUN, decode
from enrich_cases import decode_string, selector as sel4

EXPLORERS = {'ethereum': 'https://etherscan.io', 'base': 'https://basescan.org',
             'arbitrum': 'https://arbiscan.io', 'optimism': 'https://optimistic.etherscan.io',
             'polygon': 'https://polygonscan.com'}
NATIVE = collections.defaultdict(lambda: 'ETH', polygon='POL')
# Chain-generated transactions carry no user gas decision; exclude them from baselines.
SYSTEM_TYPES = {'arbitrum': {'0x64', '0x65', '0x66', '0x68', '0x69', '0x6a'},
                'base': {'0x7e'}, 'optimism': {'0x7e'}}
METRICS = {'gas_limit': 'gas limit', 'priority_fee_wei': 'priority fee', 'fee_paid_wei': 'total fee paid'}
MINIMAL_PROXY = re.compile(r'^0x363d3d373d3d3d363d73([0-9a-f]{40})5af43d82803e903d91602b57fd5bf3$')
SAMPLE_EVENTS = 12


def gwei(wei):
    d = Decimal(wei) / Decimal(10**9)
    if abs(d) >= Decimal('0.01'):
        return str(d.quantize(Decimal('0.0001')))
    return format(d.normalize(), 'f') if d else '0'


def native(wei, unit):
    return str((Decimal(wei) / Decimal(10**18)).quantize(Decimal('0.000001'))) + ' ' + unit


def short(h):
    return h[:6] + '…' + h[-4:]


def tx_link(chain, h):
    return '[' + short(h) + '](' + EXPLORERS[chain] + '/tx/' + h + ')'


def addr_link(chain, a, label=None):
    if not a:
        return '—'
    return '[' + (label or short(a)) + '](' + EXPLORERS[chain] + '/address/' + a + ')'


def raw_blocks(sample):
    for cp in sorted((sample / 'raw').iterdir()):
        if cp.is_dir():
            for path in sorted(cp.glob('*.gz'), key=lambda p: int(p.name.split('.')[0])):
                with gzip.open(path, 'rt') as f:
                    yield cp.name, json.load(f), path


def rows_for(chain, data, path):
    block, receipts = data['block'], data['receipts']
    base_fee = hx(block.get('baseFeePerGas', 0))
    by_hash = {r['transactionHash']: r for r in receipts}
    for t in block['transactions']:
        r = by_hash.get(t['hash'])
        if r is None:
            continue
        typ = t.get('type', '0x0')
        eff = hx(r.get('effectiveGasPrice', t.get('gasPrice', 0)))
        gas_used, l1 = hx(r['gasUsed']), hx(r.get('l1Fee', 0))
        blob = hx(r.get('blobGasUsed', 0)) * hx(r.get('blobGasPrice', 0))
        yield {'chain': chain, 'block_number': hx(block['number']), 'block_hash': block['hash'],
               'timestamp': hx(block['timestamp']), 'transaction_hash': t['hash'],
               'transaction_index': hx(t['transactionIndex']), 'type': typ,
               'system': typ in SYSTEM_TYPES.get(chain, set()),
               'sender': t['from'].lower(), 'to': (t.get('to') or '').lower() or None,
               'contract_created': (r.get('contractAddress') or '').lower() or None,
               'value_wei': hx(t.get('value', 0)), 'nonce': hx(t.get('nonce', 0)),
               'selector': t.get('input', '0x')[:10], 'calldata_bytes': (len(t.get('input', '0x')) - 2) // 2,
               'status_ok': hx(r.get('status', 1)) == 1,
               'gas_limit': hx(t['gas']), 'gas_used': gas_used, 'base_fee_wei': base_fee,
               'effective_gas_price_wei': eff, 'priority_fee_wei': eff - base_fee,
               'max_fee_per_gas_wei': hx(t['maxFeePerGas']) if 'maxFeePerGas' in t else None,
               'max_priority_fee_per_gas_wei': hx(t['maxPriorityFeePerGas']) if 'maxPriorityFeePerGas' in t else None,
               'l1_fee_wei': l1, 'blob_fee_wei': blob, 'fee_paid_wei': gas_used * eff + l1 + blob,
               'log_count': len(r.get('logs', [])), 'raw_file': str(path.relative_to(ROOT))}


def describe(values):
    vs = sorted(values)
    med = statistics.median(vs)
    q = statistics.quantiles(vs, n=100, method='inclusive')
    return {'n': len(vs), 'min': vs[0], 'p50': med, 'p90': q[89], 'p95': q[94], 'p99': q[98], 'max': vs[-1],
            'mad': statistics.median(abs(v - med) for v in vs), '_sorted': vs}


def position(stat, x):
    z = None if not stat['mad'] else float((Decimal(x - stat['p50']) / Decimal(stat['mad'] * 1.4826)).quantize(Decimal('0.01')))
    return {'percentile_rank': round(100 * bisect.bisect_left(stat['_sorted'], x) / stat['n'], 2), 'robust_z': z}


def event_view(log, chain):
    d = decode(log)
    if chain == 'polygon' and is_polygon_fee_log(log):
        d = {'family': 'Polygon_native_fee_log'}
    return {'log_index': hx(log['logIndex']), 'emitter': log['address'].lower(),
            'topic0': log['topics'][0] if log.get('topics') else None, **d}


def net_flows(events, address):
    flows = collections.defaultdict(int)
    for e in events:
        if e['family'] == 'ERC20_Transfer_shape':
            flows[e['emitter']] += int(e['amount_raw']) * ((e['recipient'] == address) - (e['sender'] == address))
    return {k: str(v) for k, v in flows.items() if v}


def build_packet(row, reasons, block, receipt, tx, stats, unit):
    chain = row['chain']
    events = [event_view(l, chain) for l in receipt.get('logs', [])]
    families = collections.Counter(e['family'] for e in events)
    emitters = collections.Counter(e['emitter'] for e in events)
    recipients = {e['recipient'] for e in events if 'recipient' in e}
    same_sender = [hx(t['transactionIndex']) for t in block['transactions']
                   if t['from'].lower() == row['sender'] and t['hash'] != tx['hash']]
    unknown_topics = collections.Counter((e['emitter'], e['topic0']) for e in events if e['family'] == 'unknown')
    facts = [{'id': 'F1', 'metric': 'gas_limit', 'value': row['gas_limit'], 'unit': 'gas'},
             {'id': 'F2', 'metric': 'gas_used', 'value': row['gas_used'], 'unit': 'gas'},
             {'id': 'F3', 'metric': 'effective_gas_price', 'value': gwei(row['effective_gas_price_wei']), 'unit': 'gwei'},
             {'id': 'F4', 'metric': 'block_base_fee', 'value': gwei(row['base_fee_wei']), 'unit': 'gwei'},
             {'id': 'F5', 'metric': 'priority_fee', 'value': gwei(row['priority_fee_wei']), 'unit': 'gwei'},
             {'id': 'F6', 'metric': 'fee_paid_total', 'value': native(row['fee_paid_wei'], unit), 'unit': unit,
              'components': {'execution_wei': str(row['gas_used'] * row['effective_gas_price_wei']),
                             'l1_fee_wei': str(row['l1_fee_wei']), 'blob_fee_wei': str(row['blob_fee_wei'])}},
             {'id': 'F7', 'metric': 'value_sent', 'value': native(row['value_wei'], unit), 'unit': unit},
             {'id': 'F8', 'metric': 'status', 'value': 'success' if row['status_ok'] else 'failed'},
             {'id': 'F9', 'metric': 'log_count', 'value': row['log_count']},
             {'id': 'F10', 'metric': 'position_in_block', 'value': str(row['transaction_index']) + '/' + str(len(block['transactions']))}]
    return {'episode_id': chain + ':' + row['block_hash'] + ':' + row['transaction_hash'],
            'chain': chain, 'explorer_tx': EXPLORERS[chain] + '/tx/' + row['transaction_hash'],
            'selection_reasons': reasons,
            'baseline_position': {m: position(stats[m], row[m]) for m in METRICS},
            'transaction': {k: row[k] for k in ['block_number', 'timestamp', 'transaction_hash', 'transaction_index', 'type',
                                                'sender', 'to', 'contract_created', 'nonce', 'selector', 'calldata_bytes',
                                                'status_ok', 'gas_limit', 'gas_used', 'log_count', 'raw_file']}
            | {'block_utc': utc(row['timestamp']), 'calldata_prefix': tx.get('input', '0x')[:10 + 128],
               'gas_limit_over_used': round(row['gas_limit'] / row['gas_used'], 2) if row['gas_used'] else None,
               'declared_max_fee_gwei': gwei(row['max_fee_per_gas_wei']) if row['max_fee_per_gas_wei'] is not None else None,
               'declared_max_priority_gwei': gwei(row['max_priority_fee_per_gas_wei']) if row['max_priority_fee_per_gas_wei'] is not None else None,
               'same_sender_other_indices_in_block': same_sender,
               'authorization_list_len': len(tx.get('authorizationList') or []) if tx.get('type') == '0x4' else None,
               'blob_count': len(tx.get('blobVersionedHashes') or []) or None,
               'block_gas_utilization': round(hx(block['gasUsed']) / hx(block['gasLimit']), 4)},
            'facts': facts,
            'events': {'families': dict(families), 'top_emitters': emitters.most_common(10),
                       'distinct_transfer_recipients': len(recipients),
                       'unknown_topics': [{'emitter': a, 'topic0': t, 'count': n} for (a, t), n in unknown_topics.most_common(8)],
                       'sample': events[:SAMPLE_EVENTS], 'truncated': max(0, len(events) - SAMPLE_EVENTS)},
            'erc20_net_flows': {'sender': net_flows(events, row['sender']),
                                'to': net_flows(events, row['to']) if row['to'] else {}},
            'missing': ['internal calls and native value transfers', 'revert reason', 'state before/after',
                        'verified contract identity (see context.json for code/symbol lookups)']}


def scan(args):
    sample, out = Path(args.sample), Path(args.out)
    rows = collections.defaultdict(list)
    for chain, data, path in raw_blocks(sample):
        rows[chain].extend(rows_for(chain, data, path))
    stats, selected, activity = {}, {}, {}
    for chain, rs in rows.items():
        user = [r for r in rs if not r['system']]
        st = {m: describe([r[m] for r in user]) for m in METRICS}
        stats[chain] = {'transactions': len(rs), 'system_transactions': len(rs) - len(user), 'user_transactions': len(user),
                        'tx_types': dict(collections.Counter(r['type'] for r in rs)),
                        'metrics': {m: {k: v for k, v in s.items() if k != '_sorted'} for m, s in st.items()}}
        picks, skipped = {}, []
        for m in METRICS:
            if st[m]['max'] <= st[m]['p50']:
                skipped.append(m)  # no dispersion above the median: ranking would only reflect block order
                continue
            ranked = sorted(user, key=lambda r: (-r[m], r['block_number'], r['transaction_index']))[:args.top]
            for rank, r in enumerate(ranked, 1):
                picks.setdefault(r['transaction_hash'], {'row': r, 'reasons': []})['reasons'].append(
                    {'metric': m, 'rank': rank, 'value': r[m], 'ties_at_value': sum(u[m] == r[m] for u in user)})
        stats[chain]['skipped_metrics'] = skipped
        selected[chain] = (picks, st)
        # Repeated high-tip senders: who keeps paying above the chain's 95th percentile?
        cut = st['priority_fee_wei']['p95']
        high = [r for r in user if r['priority_fee_wei'] >= cut and cut > 0]
        by_sender = collections.defaultdict(list)
        for r in high:
            by_sender[r['sender']].append(r)
        act = []
        for s, hs in sorted(by_sender.items(), key=lambda kv: -len(kv[1]))[:8]:
            if len(hs) < 3:
                break
            act.append({'sender': s, 'high_tip_transactions': len(hs), 'all_transactions_in_sample': sum(r['sender'] == s for r in user),
                        'failed': sum(not r['status_ok'] for r in hs), 'distinct_destinations': len({r['to'] for r in hs}),
                        'median_priority_fee_gwei': gwei(int(statistics.median(r['priority_fee_wei'] for r in hs))),
                        'median_gas_limit': int(statistics.median(r['gas_limit'] for r in hs)),
                        'selectors': collections.Counter(r['selector'] for r in hs).most_common(3),
                        'example_transactions': [r['transaction_hash'] for r in hs[:3]]})
        activity[chain] = {'p95_priority_fee_gwei': gwei(cut), 'transactions_at_or_above_p95': len(high), 'repeat_senders': act}
    # Second pass: reopen only the raw files that hold selected transactions.
    need = collections.defaultdict(list)
    for chain, (picks, _) in selected.items():
        for h, p in picks.items():
            need[p['row']['raw_file']].append(h)
    packets = []
    for chain, data, path in raw_blocks(sample):
        rel = str(path.relative_to(ROOT))
        if rel not in need:
            continue
        picks, st = selected[chain]
        txs = {t['hash']: t for t in data['block']['transactions']}
        recs = {r['transactionHash']: r for r in data['receipts']}
        for h in need[rel]:
            packets.append(build_packet(picks[h]['row'], picks[h]['reasons'], data['block'], recs[h], txs[h], st, NATIVE[chain]))
    order = {c: i for i, c in enumerate(EXPLORERS)}
    packets.sort(key=lambda p: (order[p['chain']], p['transaction']['block_number'], p['transaction']['transaction_index']))
    save(out / 'stats.json', {'generated_at': utc(), 'sample': str(sample.relative_to(ROOT)), 'top_per_metric': args.top,
                              'metrics': METRICS, 'system_types_excluded': {k: sorted(v) for k, v in SYSTEM_TYPES.items()},
                              'chains': stats, 'high_tip_activity': activity})
    save(out / 'packets.json', packets)
    print(json.dumps({c: {'user_transactions': stats[c]['user_transactions'], 'selected': len(selected[c][0])} for c in stats}
                     | {'packets': len(packets)}, indent=2))


def resolve(args):
    out = Path(args.out)
    packets = json.loads((out / 'packets.json').read_text())
    ctx_path = out / 'context.json'
    ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {'tokens': {}, 'code': {}, 'asof': {}}
    rpc = RPC(out, max_credits=args.max_credits, interval=.5)
    for chain in EXPLORERS:
        ps = [p for p in packets if p['chain'] == chain]
        if not ps:
            continue
        tokens = collections.Counter()
        addresses = set()
        for p in ps:
            for emitter, n in p['events']['top_emitters']:
                if any(e['emitter'] == emitter and e['family'] == 'ERC20_Transfer_shape' for e in p['events']['sample']) \
                        or emitter in p['erc20_net_flows']['sender'] or emitter in p['erc20_net_flows']['to']:
                    tokens[emitter] += n
            addresses.update(a for a in [p['transaction']['to'], p['transaction']['contract_created']] if a)
            addresses.update(e for e, _ in p['events']['top_emitters'][:3])
        tokens = [t for t, _ in tokens.most_common(args.max_tokens)]
        pin = hex(max(p['transaction']['block_number'] for p in ps))
        ctx['asof'].setdefault(chain, {'pinned_block': hx(pin), 'fallback': 'latest when the pinned call errors', 'observed_at': utc()})
        tok = ctx['tokens'].setdefault(chain, {})
        for t in [t for t in tokens if t not in tok]:
            calls = [('eth_call', [{'to': t, 'data': sel4('symbol()')}, pin]), ('eth_call', [{'to': t, 'data': sel4('decimals()')}, pin])]
            vals = rpc.batch(chain, calls, allow_errors=True)
            used = pin
            if any(isinstance(v, dict) for v in vals):
                vals = rpc.batch(chain, [(m, [q, 'latest']) for m, (q, _) in calls], allow_errors=True)
                used = 'latest'
            tok[t] = {'symbol_untrusted': decode_string(vals[0]) if isinstance(vals[0], str) else None,
                      'decimals': hx(vals[1]) if isinstance(vals[1], str) and len(vals[1]) == 66 else None,
                      'block_tag': used, 'raw': vals}
        code = ctx['code'].setdefault(chain, {})
        todo = sorted(a for a in addresses if a not in code)
        for i in range(0, len(todo), 10):
            part = todo[i:i + 10]
            vals = rpc.batch(chain, [('eth_getCode', [a, pin]) for a in part], allow_errors=True)
            for a, v in zip(part, vals):
                if isinstance(v, dict):
                    v = rpc.call(chain, 'eth_getCode', [a, 'latest'], allow_errors=True)
                if isinstance(v, str):
                    m = MINIMAL_PROXY.match(v)
                    code[a] = {'code_bytes': (len(v) - 2) // 2, 'is_contract': len(v) > 2,
                               'minimal_proxy_target': ('0x' + m.group(1)) if m else None}
                else:
                    code[a] = {'error': str(v)[:200]}
        save(ctx_path, ctx)
        print(json.dumps({'chain': chain, 'tokens': len(tok), 'code_lookups': len(code), 'credits_so_far': rpc.credits}), flush=True)


def parse_notes(path):
    notes = {}
    if not path.exists():
        return notes
    for block in re.split(r'^## ', path.read_text(), flags=re.M)[1:]:
        head, _, rest = block.partition('\n')
        parts = head.split()
        if not parts:
            continue
        if len(parts) < 2 or not parts[1].startswith('0x'):
            notes[parts[0].lower()] = {'body': rest.strip()}  # named section such as synthesis or feedback
            continue
        meta, body = {}, []
        lines = rest.strip('\n').split('\n')
        i = 0
        while i < len(lines) and re.match(r'^[a-z_]+: ', lines[i]):
            k, _, v = lines[i].partition(': ')
            meta[k] = v.strip()
            i += 1
        body = '\n'.join(lines[i:]).strip()
        notes[parts[1].lower()] = {'chain': parts[0], **meta, 'body': body}
    return notes


def fmt_token(chain, ctx, addr, raw):
    info = ctx.get('tokens', {}).get(chain, {}).get(addr, {})
    sym, dec = info.get('symbol_untrusted'), info.get('decimals')
    v = Decimal(raw)
    if dec is not None:
        v = v / Decimal(10 ** dec)
    amount = ('+' if v > 0 else '') + str(v.quantize(Decimal('0.000001')) if dec is not None else v)
    return amount + ' ' + (sym or short(addr)) + ('' if dec is not None else ' (raw)')


def render(args):
    out = Path(args.out)
    packets = json.loads((out / 'packets.json').read_text())
    stats = json.loads((out / 'stats.json').read_text())
    ctx = json.loads((out / 'context.json').read_text()) if (out / 'context.json').exists() else {}
    notes = parse_notes(out / 'qual_notes.md')
    manifest = json.loads((RUN / 'manifest.json').read_text())
    L = []
    L.append('# Gas outliers: a quant scan followed by an LLM investigation\n')
    L.append('Proof of concept for one loop iteration. The deterministic step ranks every user transaction in the saved '
             'five-chain sample by three gas metrics and selects the top ' + str(stats['top_per_metric']) + ' per metric per chain. '
             'The qualitative step reads the resulting evidence packets and explains what each transaction did. '
             'Every number below is computed by `scripts/gas_outliers.py`; the prose under each transaction is the LLM\'s interpretation '
             'and is labelled with a confidence. Identity claims that rest on model memory rather than an onchain check are marked as such.\n')
    L.append('Sample: ' + manifest['start_utc'] + ' to ' + manifest['end_utc'] + ' (exclusive), the discovery window of the pilot. '
             'Chain-generated transactions (Arbitrum types 0x64-0x6a, OP Stack type 0x7e deposits) are excluded from baselines and selection. '
             'Priority fee means `effectiveGasPrice - baseFeePerGas` of the containing block. Total fee paid adds the reported L1 fee on OP Stack chains and blob fees on Ethereum.\n')
    L.append('## Chain baselines\n')
    L.append('| Chain | User txs | System txs | Median gas limit | P99 gas limit | Max gas limit | Median tip (gwei) | P99 tip (gwei) | Max tip (gwei) | Median fee paid | P99 fee paid | Max fee paid |')
    L.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for chain in EXPLORERS:
        s = stats['chains'].get(chain)
        if not s:
            continue
        m, u = s['metrics'], NATIVE[chain]
        L.append('| ' + chain + ' | ' + f"{s['user_transactions']:,} | {s['system_transactions']:,} | "
                 f"{int(m['gas_limit']['p50']):,} | {int(m['gas_limit']['p99']):,} | {m['gas_limit']['max']:,} | "
                 f"{gwei(int(m['priority_fee_wei']['p50']))} | {gwei(int(m['priority_fee_wei']['p99']))} | {gwei(m['priority_fee_wei']['max'])} | "
                 f"{native(int(m['fee_paid_wei']['p50']), u)} | {native(int(m['fee_paid_wei']['p99']), u)} | {native(m['fee_paid_wei']['max'], u)} |")
    L.append('')
    if 'synthesis' in notes:
        L.append('## Cross-cutting observations (LLM)\n')
        L.append(notes['synthesis']['body'] + '\n')
    counter = 0
    mech_counts = collections.Counter()
    for chain in EXPLORERS:
        ps = [p for p in packets if p['chain'] == chain]
        if not ps:
            continue
        L.append('## ' + chain.capitalize() + '\n')
        for m in stats['chains'][chain].get('skipped_metrics', []):
            L.append('Not ranked by ' + METRICS[m] + ': no user transaction in this window exceeded the chain median, so a ranking would only reflect block order.\n')
        L.append('| # | Transaction | Selected for | From | To | Gas limit / used | Eff. price (gwei) | Tip (gwei) | Fee paid | Status | Logs | Mechanism (LLM) |')
        L.append('|---:|---|---|---|---|---:|---:|---:|---:|---|---:|---|')
        start = counter
        for p in ps:
            counter += 1
            t = p['transaction']
            note = notes.get(t['transaction_hash'].lower(), {})
            f = {x['metric']: x for x in p['facts']}
            reasons = ', '.join(METRICS[r['metric']] + ' #' + str(r['rank']) + (' (' + str(r['ties_at_value']) + ' tied)' if r.get('ties_at_value', 1) > 1 else '')
                                for r in p['selection_reasons'])
            to = addr_link(chain, t['to']) if t['to'] else ('created ' + addr_link(chain, t['contract_created']) if t['contract_created'] else 'creation')
            mech = note.get('mechanism', '_not yet annotated_')
            if note:
                mech_counts[note.get('confidence', 'unstated')] += 1
            L.append(f"| {counter} | {tx_link(chain, t['transaction_hash'])} | {reasons} | {addr_link(chain, t['sender'])} | {to} | "
                     f"{t['gas_limit']:,} / {t['gas_used']:,} | {f['effective_gas_price']['value']} | {f['priority_fee']['value']} | "
                     f"{f['fee_paid_total']['value']} | {f['status']['value']} | {t['log_count']} | {mech} |")
        L.append('')
        act = stats['high_tip_activity'].get(chain, {})
        if act.get('repeat_senders'):
            L.append('Repeated high-tip senders (three or more transactions at or above the chain P95 tip of ' + act['p95_priority_fee_gwei'] + ' gwei):\n')
            L.append('| Sender | High-tip txs | All txs in sample | Failed | Distinct destinations | Median tip (gwei) | Median gas limit | Top selectors | Examples |')
            L.append('|---|---:|---:|---:|---:|---:|---:|---|---|')
            for a in act['repeat_senders']:
                L.append(f"| {addr_link(chain, a['sender'])} | {a['high_tip_transactions']} | {a['all_transactions_in_sample']} | {a['failed']} | {a['distinct_destinations']} | "
                         f"{a['median_priority_fee_gwei']} | {a['median_gas_limit']:,} | {', '.join(s + ' ×' + str(n) for s, n in a['selectors'])} | "
                         f"{' '.join(tx_link(chain, h) for h in a['example_transactions'])} |")
            L.append('')
        L.append('### Investigations\n')
        n = start
        for p in ps:
            n += 1
            t = p['transaction']
            h = t['transaction_hash']
            note = notes.get(h.lower(), {})
            f = {x['metric']: x for x in p['facts']}
            L.append(f"#### {n}. {tx_link(chain, h)}: " + note.get('mechanism', 'not yet annotated') + '\n')
            pos = p['baseline_position']
            code = ctx.get('code', {}).get(chain, {})
            to_desc = 'a contract creation' if not t['to'] else ('a contract' if code.get(t['to'], {}).get('is_contract') else ('an EOA' if t['to'] in code else 'of unknown code status'))
            proxy = code.get(t['to'] or '', {}).get('minimal_proxy_target')
            L.append('Facts: block ' + f"{t['block_number']:,}" + ' at ' + t['block_utc'] + ', position ' + f['position_in_block']['value'] +
                     ', type ' + t['type'] + ', ' + f['status']['value'] + '. Gas limit ' + f"{t['gas_limit']:,}" + ' (chain percentile ' +
                     str(pos['gas_limit']['percentile_rank']) + '), used ' + f"{t['gas_used']:,}" + '. Effective price ' + f['effective_gas_price']['value'] +
                     ' gwei against base fee ' + f['block_base_fee']['value'] + ' gwei, so tip ' + f['priority_fee']['value'] + ' gwei (percentile ' +
                     str(pos['priority_fee_wei']['percentile_rank']) + '). Fee paid ' + f['fee_paid_total']['value'] + ' (percentile ' +
                     str(pos['fee_paid_wei']['percentile_rank']) + '). Value sent ' + f['value_sent']['value'] + '. Destination is ' + to_desc +
                     (', an EIP-1167 minimal proxy to ' + addr_link(chain, proxy) if proxy else '') + '. Selector `' + t['selector'] + '`, calldata ' +
                     f"{t['calldata_bytes']:,}" + ' bytes, ' + str(t['log_count']) + (' log.' if t['log_count'] == 1 else ' logs.') +
                     (' Same sender also at block positions ' + ', '.join(map(str, t['same_sender_other_indices_in_block'])) + '.' if t['same_sender_other_indices_in_block'] else ''))
            fam = ', '.join(f'{k} ×{v}' for k, v in sorted(p['events']['families'].items(), key=lambda kv: -kv[1]))
            L.append('\nDecoded event families: ' + (fam or 'none') + '.' +
                     (' Distinct transfer recipients: ' + str(p['events']['distinct_transfer_recipients']) + '.' if p['events']['distinct_transfer_recipients'] > 1 else ''))
            flows = p['erc20_net_flows']
            if flows['sender'] or flows['to']:
                parts = []
                if flows['sender']:
                    parts.append('sender: ' + '; '.join(fmt_token(chain, ctx, a, v) for a, v in flows['sender'].items()))
                if flows['to']:
                    parts.append('destination: ' + '; '.join(fmt_token(chain, ctx, a, v) for a, v in flows['to'].items()))
                L.append('\nERC-20 net flows from transfer events (symbols are self-reported and untrusted): ' + ' | '.join(parts) + '.')
            if note:
                L.append('\nInterpretation (LLM, confidence ' + note.get('confidence', 'unstated') + '): ' + note['body'])
                if note.get('unverified'):
                    L.append('\nUnverified: ' + note['unverified'])
            else:
                L.append('\n_No qualitative note yet for this transaction._')
            L.append('')
    L.append('## What the quant step handed over, and what came back\n')
    L.append('Packets: ' + str(len(packets)) + '. Annotated: ' + str(sum(1 for p in packets if p["transaction"]["transaction_hash"].lower() in notes)) + '. LLM confidence: ' +
             ', '.join(f'{k} ×{v}' for k, v in mech_counts.most_common()) + '.\n')
    L.append('Artifacts: `packets.json` (evidence packets with fact IDs and baseline positions), `stats.json` (per-chain baselines and repeat-sender activity), '
             '`context.json` (bounded RPC lookups: token symbol/decimals, code presence, pinned block), `qual_notes.md` (LLM notes keyed by transaction hash), '
             '`rpc_requests.jsonl` (every follow-up request with estimated credits; no keys).\n')
    if 'feedback' in notes:
        L.append('### Requests from the qualitative step back to the quant step (LLM)\n')
        L.append(notes['feedback']['body'] + '\n')
    L.append('Limitations: the sample is a single two-minute window, so "outlier" means outlier within it, not historically unusual. Receipts do not show internal calls, '
             'native value moved by contracts, or revert reasons, so payments to block builders and the cause of failures are inferred, not observed. Token symbols come from the '
             'token contracts themselves. Contract identities named in the notes without an onchain check are model memory and should be treated as hypotheses.\n')
    (out / 'report.md').write_text('\n'.join(L) + '\n')
    print(json.dumps({'report': str((out / 'report.md').relative_to(ROOT)), 'packets': len(packets),
                      'annotated': sum(1 for p in packets if p['transaction']['transaction_hash'].lower() in notes),
                      'sections': sorted(k for k in notes if not k.startswith('0x'))}))


def show(args):
    """Bounded episode retrieval for the qualitative step: one transaction, all decoded logs."""
    out = Path(args.out)
    packets = {p['transaction']['transaction_hash']: p for p in json.loads((out / 'packets.json').read_text())}
    for h in args.hashes:
        p = packets.get(h.lower())
        if not p:
            print('not in packets:', h)
            continue
        with gzip.open(ROOT / p['transaction']['raw_file'], 'rt') as f:
            data = json.load(f)
        tx = next(t for t in data['block']['transactions'] if t['hash'] == h.lower())
        rec = next(r for r in data['receipts'] if r['transactionHash'] == h.lower())
        print('=' * 110)
        print(p['chain'], h, 'block', p['transaction']['block_number'], 'index', p['transaction']['transaction_index'])
        skip = {'input', 'accessList', 'authorizationList', 'blobVersionedHashes', 'r', 's', 'v', 'yParity', 'hash', 'blockHash'}
        print(json.dumps({k: v for k, v in tx.items() if k not in skip}))
        if tx.get('authorizationList'):
            print('authorizationList:', json.dumps(tx['authorizationList'])[:1500])
        print('input:', tx.get('input', '0x')[:args.calldata_chars], '| bytes', (len(tx.get('input', '0x')) - 2) // 2)
        logs = rec.get('logs', [])
        for i, l in enumerate(logs):
            if i >= args.max_logs:
                print('  ...', len(logs) - args.max_logs, 'more logs')
                break
            e = event_view(l, p['chain'])
            extra = {k: v for k, v in e.items() if k not in ('log_index', 'emitter', 'topic0', 'family')}
            print(f"  [{e['log_index']}] {e['emitter']} {e['family']} {json.dumps(extra) if extra else ''}")
            if e['family'] == 'unknown':
                print('       topics', ' '.join(l['topics']))
                print('       data', l['data'][:args.data_chars], '| bytes', (len(l['data']) - 2) // 2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['scan', 'resolve', 'render', 'show'])
    p.add_argument('hashes', nargs='*', help='show: transaction hashes to print')
    p.add_argument('--max-logs', type=int, default=24)
    p.add_argument('--calldata-chars', type=int, default=400)
    p.add_argument('--data-chars', type=int, default=200)
    p.add_argument('--sample', default=str(RUN))
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-05' / 'gas_outliers'))
    p.add_argument('--top', type=int, default=3, help='transactions per metric per chain')
    p.add_argument('--max-credits', type=int, default=30000)
    p.add_argument('--max-tokens', type=int, default=25, help='token metadata lookups per chain')
    args = p.parse_args()
    {'scan': scan, 'resolve': resolve, 'render': render, 'show': show}[args.command](args)


if __name__ == '__main__':
    main()
