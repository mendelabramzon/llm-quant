#!/usr/bin/env python3
"""Collect a block window from an Arbitrum Nitro / Orbit chain (e.g. Robinhood Chain, chain id 4663) into compact,
resumable chunk files: every block header, every transaction joined with its receipt, and a whitelist of logs.

Why a separate collector: Orbit chains run ~10 blocks/s, so a 10-hour window is ~360k blocks and ~6M transactions.
Storing raw blocks + receipts would be >15 GB; instead each 100-block unit is fetched (eth_getBlockByNumber full +
eth_getBlockReceipts, both batched) and reduced on the fly to one gzip JSONL file `data/<first_block>.jsonl.gz`:

    {"t":"b", ...}   block header: n, ts, gu (gasUsed), bf (baseFeePerGas), tx (count), l1 (l1BlockNumber), sz (size)
    {"t":"x", ...}   transaction + receipt: h, n, i, f (from), to, s (selector), v (value), g (gas limit), gp (gasPrice),
                     ty (type), nc (nonce), il (input length), in (input, first 512 bytes), gu (gasUsed),
                     l1g (gasUsedForL1), egp (effectiveGasPrice), st (status), nl (log count), ca (created contract)
    {"t":"l", ...}   kept log: h (tx hash), n, i (logIndex), a (address), tp (topics), d (data)
    {"t":"ta", ...}  per-unit aggregate of ERC-20 Transfer logs that were NOT kept: token -> [transfers, mints, burns,
                     distinct receivers (capped), sum of value as decimal string]
    {"t":"ea", ...}  per-unit aggregate of every log by "address|topic0" -> count (the full event landscape)

A log is kept in full when its address is in `--keep-address` (stock tokens, USDG, WETH, EntryPoints, ArbSys, ...),
or its topic0 is in KEEP_TOPICS (DEX swaps, pool creations, liquidity changes, user operations, L2->L1 messages,
ERC-721 transfers). Everything else is only counted.

Endpoints (chainlist, 2026-09-07): Blockmachine and PublicNode answer 100-block batches in well under a second but
rate-limit sustained load with HTTP 429 (parked for a second, next endpoint takes over); bloXroute is slower but steady;
the official public RPC allows ~1 request/s; dRPC's free endpoint rejects batches. Nothing is written except the chunk files and `manifest.json`.

    uv run python scripts/orbit_collect.py --out research/2026-09-07/robinhood_10h --first 56535399 --last 56892272 \
        --keep-address-file research/2026-09-07/robinhood_10h/keep_addresses.json
"""
import argparse
import collections
import concurrent.futures as cf
import gzip
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ENDPOINTS = ['https://rpc-robinhood.blockmachine.io', 'https://robinhood-rpc.publicnode.com', 'https://robinhood.rpc.blxrbdn.com', 'https://rpc.mainnet.chain.robinhood.com']
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
MIN_GAP = {'https://rpc-robinhood.blockmachine.io': 0.1, 'https://robinhood-rpc.publicnode.com': 0.3, 'https://robinhood.rpc.blxrbdn.com': 0.3, 'https://rpc.mainnet.chain.robinhood.com': 1.0, 'https://robinhood.drpc.org': 0.5}
BATCH_OK = {'https://rpc-robinhood.blockmachine.io': True, 'https://robinhood-rpc.publicnode.com': True, 'https://robinhood.rpc.blxrbdn.com': True, 'https://rpc.mainnet.chain.robinhood.com': True, 'https://robinhood.drpc.org': False}

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
ZERO32 = '0x' + '0' * 64
KEEP_TOPICS = {
    '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67': 'UniV3Swap',
    '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f': 'UniV4Swap',
    '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822': 'UniV2Swap',
    '0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118': 'UniV3PoolCreated',
    '0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438': 'UniV4Initialize',
    '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9': 'UniV2PairCreated',
    '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde': 'UniV3Mint',
    '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c': 'UniV3Burn',
    '0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec': 'UniV4ModifyLiquidity',
    '0x49628fd1471006c1482da88028e9ce4dbb080b815c9b0344d39e5a8e6ec1419f': 'UserOperationEvent',
    '0x3e7aafa77dbf186b7fd488006beff893744caa3c4f6f299e8a709fa2087374fc': 'L2ToL1Tx',
    '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c': 'WETHDeposit',
    '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65': 'WETHWithdrawal',
}


def hx(v):
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


class Pool:
    """Round-robin over endpoints with per-endpoint pacing and parking on errors."""

    def __init__(self, endpoints, log_path=None):
        self.eps = endpoints
        self.next = {e: 0. for e in endpoints}
        self.park = {e: 0. for e in endpoints}
        self.lock = threading.Lock()
        self.requests = 0
        self.errors = 0
        self.log_path = Path(log_path) if log_path else None

    def _pick(self, batch):
        while True:
            with self.lock:
                now = time.monotonic()
                cands = [e for e in self.eps if self.park[e] <= now and (not batch or BATCH_OK.get(e, True))]
                if cands:
                    e = min(cands, key=lambda x: self.next[x])
                    wait = max(0., self.next[e] - now)
                    self.next[e] = max(now, self.next[e]) + MIN_GAP.get(e, 0.2)
                    return e, wait
                wait = max(0.05, min(self.park.values()) - now)
            time.sleep(wait)

    def _log(self, ep, msg):
        with self.lock:
            self.errors += 1
        if self.log_path:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps({'t': time.time(), 'ep': ep, 'err': msg[:300]}) + '\n')

    def rpc(self, payload, timeout=180, retries=10):
        batch = isinstance(payload, list)
        last = None
        for attempt in range(retries):
            e, wait = self._pick(batch)
            if wait:
                time.sleep(wait)
            req = urllib.request.Request(e, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'Accept-Encoding': 'gzip', 'User-Agent': UA})
            try:
                with self.lock:
                    self.requests += 1
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                d = json.loads(body)
                if batch and isinstance(d, dict):
                    last = 'batch answered with object: ' + str(d)[:150]
                    self._log(e, last)
                    with self.lock:
                        self.park[e] = time.monotonic() + 5
                    continue
                return d
            except urllib.error.HTTPError as ex:
                last = 'HTTP %d' % ex.code
                self._log(e, last)
                with self.lock:
                    self.park[e] = time.monotonic() + (1.0 if ex.code == 429 else 5)
            except Exception as ex:
                last = str(ex)[:160]
                self._log(e, last)
                with self.lock:
                    self.park[e] = time.monotonic() + 3
        raise RuntimeError('rpc failed after retries: %s' % last)

    def batch(self, calls):
        """calls: list of (method, params). Returns results in order; raises if any member failed."""
        r = self.rpc([{'jsonrpc': '2.0', 'id': i, 'method': m, 'params': p} for i, (m, p) in enumerate(calls)])
        out = [None] * len(calls)
        for x in r:
            if isinstance(x, dict) and x.get('result') is not None:
                out[x['id']] = x['result']
        missing = [i for i, v in enumerate(out) if v is None]
        if missing:
            raise RuntimeError('batch missing %d/%d members (e.g. %s)' % (len(missing), len(calls), str([x for x in r if isinstance(x, dict) and x.get('error')][:1])[:200]))
        return out


def reduce_unit(blocks, receipts, keep_addr):
    """Turn full blocks + receipts of one unit into JSONL lines."""
    lines = []
    tagg = {}
    eagg = collections.Counter()
    for b, rcs in zip(blocks, receipts):
        n = hx(b['number'])
        ts = hx(b['timestamp'])
        lines.append(json.dumps({'t': 'b', 'n': n, 'ts': ts, 'gu': hx(b['gasUsed']), 'bf': hx(b.get('baseFeePerGas', '0x0')), 'tx': len(b['transactions']), 'l1': hx(b.get('l1BlockNumber', '0x0')), 'sz': hx(b.get('size', '0x0'))}, separators=(',', ':')))
        rmap = {r['transactionHash']: r for r in rcs}
        for i, tx in enumerate(b['transactions']):
            r = rmap.get(tx['hash'], {})
            inp = tx.get('input') or '0x'
            rec = {'t': 'x', 'h': tx['hash'], 'n': n, 'i': i, 'f': tx['from'], 'to': tx.get('to'), 's': inp[:10] if len(inp) >= 10 else None,
                   'v': tx.get('value', '0x0'), 'g': hx(tx['gas']), 'gp': hx(tx.get('gasPrice', '0x0')), 'ty': tx.get('type'), 'nc': hx(tx['nonce']),
                   'il': len(inp) // 2 - 1, 'in': inp[:1034], 'gu': hx(r.get('gasUsed', '0x0')), 'l1g': hx(r.get('gasUsedForL1', '0x0')),
                   'egp': hx(r.get('effectiveGasPrice', '0x0')), 'st': hx(r.get('status', '0x0')), 'nl': len(r.get('logs') or []), 'ca': r.get('contractAddress')}
            lines.append(json.dumps(rec, separators=(',', ':')))
            for lg in r.get('logs') or []:
                tp = lg.get('topics') or []
                t0 = tp[0] if tp else None
                a = lg['address'].lower()
                eagg[a + '|' + (t0 or '')] += 1
                if a in keep_addr or (t0 in KEEP_TOPICS) or (t0 == TRANSFER and len(tp) == 4):
                    lines.append(json.dumps({'t': 'l', 'h': tx['hash'], 'n': n, 'i': hx(lg['logIndex']), 'a': a, 'tp': tp, 'd': lg.get('data', '0x')}, separators=(',', ':')))
                elif t0 == TRANSFER and len(tp) == 3:
                    agg = tagg.get(a)
                    if agg is None:
                        agg = tagg[a] = [0, 0, 0, set(), 0]
                    agg[0] += 1
                    if tp[1] == ZERO32:
                        agg[1] += 1
                    if tp[2] == ZERO32:
                        agg[2] += 1
                    if len(agg[3]) < 2000:
                        agg[3].add(tp[2])
                    try:
                        agg[4] += hx(lg.get('data', '0x0')) if len(lg.get('data', '0x')) <= 66 else 0
                    except ValueError:
                        pass
    lines.append(json.dumps({'t': 'ta', 'v': {k: [v[0], v[1], v[2], len(v[3]), str(v[4])] for k, v in tagg.items()}}, separators=(',', ':')))
    lines.append(json.dumps({'t': 'ea', 'v': dict(eagg)}, separators=(',', ':')))
    return lines


def batched(pool, calls, sizes=(100, 25, 5, 1)):
    """Run calls in batches; when an endpoint drops members ("response too large"), retry the missing ones in smaller batches."""
    out = [None] * len(calls)
    todo = list(range(len(calls)))
    for size in sizes:
        still = []
        for i in range(0, len(todo), size):
            idx = todo[i:i + size]
            try:
                res = pool.batch([calls[j] for j in idx])
                for j, v in zip(idx, res):
                    out[j] = v
            except RuntimeError:
                still.extend(idx)
        todo = still
        if not todo:
            break
    if todo:
        raise RuntimeError('unresolvable members: %d (e.g. %s)' % (len(todo), calls[todo[0]][1]))
    return out


def fetch_unit(pool, out, first, count, keep_addr):
    nums = list(range(first, first + count))
    path = out / 'data' / ('%d.jsonl.gz' % first)
    if path.exists():
        return 0, 0
    blocks = batched(pool, [('eth_getBlockByNumber', [hex(n), True]) for n in nums])
    for n, b in zip(nums, blocks):
        if hx(b['number']) != n:
            raise RuntimeError('block %d mismatch' % n)
    receipts = batched(pool, [('eth_getBlockReceipts', [hex(n)]) for n in nums])
    for b, rcs in zip(blocks, receipts):
        if len(rcs) != len(b['transactions']):
            raise RuntimeError('receipt count mismatch at %s' % b['number'])
    lines = reduce_unit(blocks, receipts, keep_addr)
    tmp = path.with_suffix('.tmp')
    with gzip.open(tmp, 'wt') as f:
        f.write('\n'.join(lines) + '\n')
    tmp.replace(path)
    return len(nums), sum(len(b['transactions']) for b in blocks)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', required=True)
    p.add_argument('--first', type=int, required=True)
    p.add_argument('--last', type=int, required=True)
    p.add_argument('--unit', type=int, default=100)
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--endpoints', default=','.join(DEFAULT_ENDPOINTS))
    p.add_argument('--keep-address-file', default=None, help='JSON list of addresses whose logs are kept in full')
    p.add_argument('--chain-name', default='robinhood')
    a = p.parse_args()
    out = Path(a.out)
    (out / 'data').mkdir(parents=True, exist_ok=True)
    keep_addr = set()
    if a.keep_address_file:
        keep_addr = {x.lower() for x in json.loads(Path(a.keep_address_file).read_text())}
    pool = Pool(a.endpoints.split(','), log_path=out / 'rpc_errors.jsonl')
    chain_id = hx(pool.rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_chainId', 'params': []})['result'])
    version = pool.rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'web3_clientVersion', 'params': []}).get('result')
    mpath = out / 'manifest.json'
    manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
    manifest.update({'chain': a.chain_name, 'chain_id': chain_id, 'client': version, 'first_block': a.first, 'last_block': a.last, 'unit': a.unit,
                     'endpoints': a.endpoints.split(','), 'keep_addresses': sorted(keep_addr), 'keep_topics': KEEP_TOPICS,
                     'collect_started': manifest.get('collect_started') or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
    mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    units = [(f, min(a.unit, a.last - f + 1)) for f in range(a.first, a.last + 1, a.unit)]
    todo = [u for u in units if not (out / 'data' / ('%d.jsonl.gz' % u[0])).exists()]
    print(json.dumps({'chain_id': chain_id, 'client': version, 'units': len(units), 'todo': len(todo), 'blocks': a.last - a.first + 1}), flush=True)
    started = time.monotonic()
    done_blocks = done_txs = 0
    failures = []
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(fetch_unit, pool, out, f, c, keep_addr): f for f, c in todo}
        for k, fut in enumerate(cf.as_completed(futs)):
            try:
                nb, nt = fut.result()
                done_blocks += nb
                done_txs += nt
            except Exception as exc:
                failures.append((futs[fut], str(exc)[:200]))
            if (k + 1) % 50 == 0 or k + 1 == len(futs):
                el = time.monotonic() - started
                print(json.dumps({'units_done': k + 1, 'blocks': done_blocks, 'txs': done_txs, 'elapsed_s': round(el), 'blocks_per_s': round(done_blocks / max(el, 1)), 'requests': pool.requests, 'errors': pool.errors, 'failed_units': len(failures)}), flush=True)
    manifest.update({'collect_finished': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'failed_units': failures[:50], 'requests': pool.requests, 'rpc_errors': pool.errors})
    mpath.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    if failures:
        print('FAILED units: %d (re-run to resume)' % len(failures), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
