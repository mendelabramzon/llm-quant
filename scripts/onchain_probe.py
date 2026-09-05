#!/usr/bin/env python3
"""Bounded, read-only Infura collection. Standard library only; no key in output.

Save exact blocks/receipts and provenance, then analyze offline. This is a research
probe, not a production indexer. Never sends transactions or rotates API keys.
"""
import argparse
import collections
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
NETWORKS = {
    'ethereum': ('mainnet', 1), 'base': ('base-mainnet', 8453),
    'arbitrum': ('arbitrum-mainnet', 42161), 'optimism': ('optimism-mainnet', 10),
    'polygon': ('polygon-mainnet', 137),
}
COST = {'eth_chainId': 5, 'eth_getBlockReceipts': 1000, 'eth_getLogs': 255,
        'debug_traceTransaction': 1000}


def hx(v):
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


def utc(t=None):
    return dt.datetime.fromtimestamp(time.time() if t is None else t, dt.timezone.utc).isoformat()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


class RPCError(Exception):
    pass


class RPC:
    def __init__(self, out, key_index=0, max_credits=850000, interval=.3):
        content = (ROOT / 'infura_keys.txt').read_text()
        self.keys = re.findall(r'"([^"\s]+)"', content)
        if not self.keys:
            raise RPCError('No keys found in infura_keys.txt')
        self.key = self.keys[key_index]
        self.out, self.max_credits, self.interval = out, max_credits, interval
        self.lock, self.next_at, self.credits, self.counter = threading.Lock(), 0., 0, 0
        self.out.mkdir(parents=True, exist_ok=True)

    def clean(self, s):
        for k in self.keys:
            s = s.replace(k, '[REDACTED]')
        return re.sub(r'https?://\S+', '[URL REDACTED]', s)[:400]

    def batch(self, chain, calls, allow_errors=False):
        # Logical method credits, not HTTP batch count. Batching does not discount.
        estimated = sum(COST.get(m, 80) for m, p in calls)
        for attempt in range(4):
            with self.lock:
                if self.credits + estimated > self.max_credits:
                    raise RPCError('Configured credit estimate ceiling reached')
                self.credits += estimated
                ids = list(range(self.counter, self.counter + len(calls)))
                self.counter += len(calls)
                delay = max(0., self.next_at - time.monotonic())
                self.next_at = time.monotonic() + delay + max(self.interval, estimated / 400)
            if delay:
                time.sleep(delay)
            payload = [{'jsonrpc': '2.0', 'id': i, 'method': m, 'params': p}
                       for i, (m, p) in zip(ids, calls)]
            url = 'https://' + NETWORKS[chain][0] + '.infura.io/v3/' + self.key
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                         headers={'Content-Type': 'application/json'})
            started, stamp = time.monotonic(), utc()
            result, error, size, transient = None, None, 0, False
            partial = {}
            try:
                with urllib.request.urlopen(req, timeout=40) as response:
                    body = response.read()
                size = len(body)
                decoded = json.loads(body)
                if not isinstance(decoded, list):
                    raise RPCError(self.clean(json.dumps(decoded)))
                if any(not isinstance(x, dict) or 'id' not in x for x in decoded):
                    partial = {x['id']: x for x in decoded if isinstance(x, dict) and 'id' in x and 'result' in x}
                    invalid = [x for x in decoded if not isinstance(x, dict) or 'id' not in x]
                    raise RPCError('Invalid batch response: ' + self.clean(json.dumps(invalid)[:2000]))
                by_id = {x['id']: x for x in decoded}
                if set(by_id) != set(ids) or len(decoded) != len(ids):
                    raise RPCError('RPC response ID mismatch')
                result = [by_id[i] for i in ids]
                errors = [r['error'] for r in result if 'error' in r]
                if errors:
                    error = self.clean(json.dumps(errors))
                    transient = any(e.get('code') in (-32005, -32002) for e in errors)
            except urllib.error.HTTPError as exc:
                error = 'HTTP ' + str(exc.code)
                transient = exc.code in (429, 500, 502, 503, 504)
            except Exception as exc:
                error = self.clean(str(exc)) if isinstance(exc, RPCError) else type(exc).__name__
                transient = isinstance(exc, (urllib.error.URLError, TimeoutError, RPCError))
            record = {'chain': chain, 'observed_at': stamp, 'attempt': attempt + 1,
                      'calls': [{'method': m, 'params': p} for m, p in calls],
                      'estimated_credits': estimated, 'response_bytes': size,
                      'seconds': round(time.monotonic() - started, 3), 'error': error}
            with self.lock:
                with (self.out / 'rpc_requests.jsonl').open('a') as f:
                    f.write(json.dumps(record) + '\n')
            if result is None and error and error.startswith('Invalid batch response:') and len(calls) > 1:
                # Retain unambiguous successful IDs and refill only missing members,
                # one at a time. Never use response position to infer a missing ID.
                return [partial[i]['result'] if i in partial else self.call(chain, m, p, allow_errors)
                        for i, (m, p) in zip(ids, calls)]
            if transient and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            if result is None or (error and not allow_errors):
                raise RPCError(chain + ': ' + str(error))
            return [r if 'error' in r else r.get('result') for r in result]
        raise RPCError('Retry limit reached')

    def call(self, chain, method, params, allow_errors=False):
        return self.batch(chain, [(method, params)], allow_errors)[0]


def first_block_at(rpc, chain, timestamp, head):
    """Find first block with timestamp >= target, including duplicate timestamps."""
    hi = hx(head['number'])
    back = 1024
    while True:
        lo = max(0, hi - back)
        b = rpc.call(chain, 'eth_getBlockByNumber', [hex(lo), False])
        if hx(b['timestamp']) < timestamp or lo == 0:
            break
        back *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        b = rpc.call(chain, 'eth_getBlockByNumber', [hex(mid), False])
        if hx(b['timestamp']) >= timestamp:
            hi = mid
        else:
            lo = mid
    return hi


POLYGON_FEE_ADDRESS = '0x0000000000000000000000000000000000001010'
POLYGON_FEE_TOPIC = '0x4dfe1bbbcf077ddc3e01291eea2d5c70c2b422b415d95645b9adcfd678cb1d63'


def is_polygon_fee_log(log):
    return (log['address'].lower() == POLYGON_FEE_ADDRESS and len(log.get('topics', [])) == 4
            and log['topics'][0] == POLYGON_FEE_TOPIC and len(log.get('data', '')) == 322)


def validate(block, receipts, chain=None):
    problems = []
    txs = block['transactions']
    expected = {t['hash']: t for t in txs}
    if len(receipts) != len(txs):
        problems.append('receipt_count_mismatch')
    if {r['transactionHash'] for r in receipts} != set(expected):
        problems.append('receipt_hash_set_mismatch')
    if len({r['transactionHash'] for r in receipts}) != len(receipts):
        problems.append('duplicate_receipt')
    log_ids = []
    for r in receipts:
        t = expected.get(r['transactionHash'])
        if r['blockHash'] != block['hash'] or r['blockNumber'] != block['number']:
            problems.append('receipt_wrong_block')
        if t and r['transactionIndex'] != t['transactionIndex']:
            problems.append('transaction_index_mismatch')
        application_logs = [l for l in r.get('logs', []) if not (chain == 'polygon' and is_polygon_fee_log(l))]
        if hx(r.get('status', 1)) == 0 and application_logs:
            problems.append('failed_receipt_has_logs')
        for log in r.get('logs', []):
            if (log['blockHash'] != block['hash'] or log['transactionHash'] != r['transactionHash']
                    or log['transactionIndex'] != r['transactionIndex']
                    or log['blockNumber'] != block['number'] or log.get('removed')):
                problems.append('log_provenance_mismatch')
            log_ids.append(hx(log['logIndex']))
    if len(log_ids) != len(set(log_ids)):
        problems.append('duplicate_log_index')
    if sum(hx(r['gasUsed']) for r in receipts) != hx(block['gasUsed']):
        problems.append('gas_used_sum_mismatch')
    return sorted(set(problems))


def collect(args):
    out = Path(args.out)
    if (out / 'manifest.json').exists() and not args.resume:
        raise RPCError('Output manifest already exists; choose a new run directory')
    rpc = RPC(out, max_credits=args.max_credits, interval=args.interval)
    manifest = {'started_at': utc(), 'provider': 'Infura', 'window_seconds': args.seconds,
                'window_definition': '[start_timestamp, end_timestamp)',
                'finality_policy': 'latest minus safety lag; recheck hashes; not assumed finalized',
                'safety_lag_seconds': args.lag, 'chains': {}, 'errors': {}}
    for chain in ([] if args.resume else NETWORKS):
        cid, head, safe, finalized = rpc.batch(chain, [
            ('eth_chainId', []), ('eth_getBlockByNumber', ['latest', False]),
            ('eth_getBlockByNumber', ['safe', False]),
            ('eth_getBlockByNumber', ['finalized', False])], allow_errors=True)
        if not isinstance(cid, str) or hx(cid) != NETWORKS[chain][1]:
            raise RPCError('Unexpected chain ID: ' + chain)
        manifest['chains'][chain] = {'chain_id': hx(cid), 'head_at_start': head,
                                    'safe_at_start': safe, 'finalized_at_start': finalized}
    if args.resume:
        manifest = json.loads((out / 'manifest.json').read_text())
        start, end = manifest['start_timestamp'], manifest['end_timestamp']
    else:
        end = min(hx(x['head_at_start']['timestamp']) for x in manifest['chains'].values()) - args.lag
        start = end - args.seconds
        manifest.update(start_timestamp=start, end_timestamp=end, start_utc=utc(start), end_utc=utc(end))
    save(out / 'manifest.json', manifest)
    print(json.dumps({'window_start': utc(start), 'window_end_exclusive': utc(end)}), flush=True)

    def work(chain):
        info = manifest['chains'][chain]
        if (out / (chain + '_manifest.json')).exists():
            return json.loads((out / (chain + '_manifest.json')).read_text())
        if 'planned_first_block' in info:
            first, last = info['planned_first_block'], info['planned_last_block']
        else:
            first = first_block_at(rpc, chain, start, info['head_at_start'])
            last = first_block_at(rpc, chain, end, info['head_at_start']) - 1
            info.update(planned_first_block=first, planned_last_block=last)
        if last - first + 1 > args.max_blocks:
            raise RPCError('Per-chain block ceiling exceeded')
        print(json.dumps({'chain': chain, 'first': first, 'last': last, 'blocks': last-first+1}), flush=True)
        rows, previous, count_t, count_l = [], None, 0, 0
        for chunk_first in range(first, last + 1, 8):
            nums = list(range(chunk_first, min(chunk_first + 8, last + 1)))
            block_map = {}
            for n in nums:
                cached_block = out / 'raw' / chain / (str(n) + '.json.gz')
                if args.resume and cached_block.exists():
                    with gzip.open(cached_block, 'rt') as f:
                        block_map[n] = json.load(f)['block']
            missing = [n for n in nums if n not in block_map]
            if missing:
                fetched = rpc.batch(chain, [('eth_getBlockByNumber', [hex(n), True]) for n in missing])
                block_map.update({hx(b['number']): b for b in fetched})
            blocks = [block_map[n] for n in nums]
            small_txs = [t for b in blocks if 0 < len(b['transactions']) <= 12
                         and not (out / 'raw' / chain / (str(hx(b['number'])) + '.json.gz')).exists()
                         for t in b['transactions']]
            prefetched = {}
            for j in range(0, len(small_txs), 10):
                part = small_txs[j:j+10]
                rs = rpc.batch(chain, [('eth_getTransactionReceipt', [t['hash']]) for t in part])
                prefetched.update({r['transactionHash']: r for r in rs})
            for b in blocks:
                n, txs = hx(b['number']), b['transactions']
                cached = out / 'raw' / chain / (str(n) + '.json.gz')
                if cached.exists():
                    with gzip.open(cached, 'rt') as f:
                        old = json.load(f)
                    if old['block']['hash'] != b['hash']:
                        raise RPCError('Cached block hash changed')
                    receipts, method = old['receipts'], old['receipt_method']
                elif not txs:
                    receipts, method = [], 'empty_block'
                elif len(txs) <= 12:
                    receipts = [prefetched[t['hash']] for t in txs]
                    method = 'eth_getTransactionReceipt'
                else:
                    result = rpc.call(chain, 'eth_getBlockReceipts', [hex(n)], allow_errors=True)
                    if isinstance(result, dict) and 'error' in result:
                        receipts = []
                        for i in range(0, len(txs), 10):
                            receipts.extend(rpc.batch(chain, [('eth_getTransactionReceipt', [t['hash']]) for t in txs[i:i+10]]))
                        method = 'eth_getTransactionReceipt_fallback'
                    else:
                        receipts, method = result, 'eth_getBlockReceipts'
                issues = validate(b, receipts, chain)
                if previous and b['parentHash'] != previous:
                    issues.append('parent_hash_mismatch')
                previous = b['hash']
                payload = {'chain': chain, 'chain_id': info['chain_id'], 'fetched_at': utc(),
                           'receipt_method': method, 'block': b, 'receipts': receipts,
                           'quality_issues': issues}
                path = out / 'raw' / chain / (str(n) + '.json.gz')
                path.parent.mkdir(parents=True, exist_ok=True)
                with gzip.open(path, 'wt') as f:
                    json.dump(payload, f, separators=(',', ':'))
                logs = sum(len(r.get('logs', [])) for r in receipts)
                count_t += len(txs)
                count_l += logs
                rows.append({'number': n, 'hash': b['hash'], 'timestamp': hx(b['timestamp']),
                             'transactions': len(txs), 'receipts': len(receipts), 'logs': logs,
                             'quality_issues': issues, 'file': str(path.relative_to(out)),
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            if len(rows) % 40 == 0:
                print(json.dumps({'chain': chain, 'collected_blocks': len(rows), 'transactions': count_t}), flush=True)
        changed = []
        recheck_rows = [rows[0], rows[-1]] if args.boundary_recheck else rows
        for i in range(0, len(recheck_rows), 12):
            current = rpc.batch(chain, [('eth_getBlockByNumber', [hex(r['number']), False]) for r in recheck_rows[i:i+12]])
            changed.extend(r['number'] for r, b in zip(recheck_rows[i:i+12], current) if r['hash'] != b['hash'])
        final = rpc.call(chain, 'eth_getBlockByNumber', ['finalized', False], allow_errors=True)
        report = {'first_block': first, 'last_block': last, 'blocks': len(rows), 'transactions': count_t,
                  'logs': count_l, 'rechecked_at': utc(), 'hash_changes_on_recheck': changed,
                  'hash_recheck_scope': 'first and last; all stored parent links checked' if args.boundary_recheck else 'every block',
                  'finalized_at_recheck': final, 'block_files': rows}
        save(out / (chain + '_manifest.json'), report)
        print(json.dumps({'chain': chain, 'complete': True, 'blocks': len(rows),
                          'transactions': count_t, 'logs': count_l, 'hash_changes': changed}), flush=True)
        return report

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(work, c): c for c in NETWORKS}
        for future in concurrent.futures.as_completed(futures):
            chain = futures[future]
            try:
                report = future.result()
                manifest['chains'][chain]['collection'] = {k: v for k, v in report.items() if k != 'block_files'}
                manifest['errors'].pop(chain, None)
            except Exception as exc:
                manifest['errors'][chain] = rpc.clean(str(exc))
                print(json.dumps({'chain': chain, 'error': manifest['errors'][chain]}), flush=True)
            save(out / 'manifest.json', manifest)
    requests = [json.loads(line) for line in (out / 'rpc_requests.jsonl').read_text().splitlines()]
    manifest.update(finished_at=utc(), estimated_credits_upper_bound=sum(r['estimated_credits'] for r in requests),
                    logical_rpc_attempts=sum(len(r['calls']) for r in requests))
    save(out / 'manifest.json', manifest)
    print(json.dumps({'finished': True, 'estimated_credits_upper_bound': rpc.credits,
                      'logical_rpc_attempts': rpc.counter, 'errors': manifest['errors']}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-05' / 'sample'))
    p.add_argument('--seconds', type=int, default=120)
    p.add_argument('--lag', type=int, default=120)
    p.add_argument('--max-blocks', type=int, default=650)
    p.add_argument('--max-credits', type=int, default=850000)
    p.add_argument('--interval', type=float, default=.3)
    p.add_argument('--resume', action='store_true')
    p.add_argument('--boundary-recheck', action='store_true')
    args = p.parse_args()
    collect(args)


if __name__ == '__main__':
    main()
