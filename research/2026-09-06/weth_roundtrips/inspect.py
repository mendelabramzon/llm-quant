"""Read-only investigation of five transactions from the user's live-log excerpt."""
import gzip
import json
import sys
import urllib.request
import urllib.error
import time
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = HERE.parent / 'live' / 'raw'
PREFIXES = ('0x48e7', '0x79b6', '0x1ce1', '0x53f3', '0x6afb')
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

def read(p):
    with (gzip.open(p, 'rt') if p.suffix == '.gz' else p.open()) as f:
        return json.load(f)

def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w') as f:
        json.dump(data, f, indent=2)

def rpc(method, params, label):
    p = HERE / 'raw' / (label + '.json')
    if p.exists():
        return read(p)
    req = urllib.request.Request('https://eth.drpc.org', data=json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode(),
        headers={'Content-Type': 'application/json', 'User-Agent': 'llm-quant research'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                obj = json.load(response)
            break
        except urllib.error.HTTPError:
            if attempt == 2:
                raise
            time.sleep(1)
    with (HERE / 'requests.jsonl').open('a') as f:
        f.write(json.dumps({'utc': datetime.now(timezone.utc).isoformat(),
            'provider': 'https://eth.drpc.org', 'method': method, 'params': params,
            'file': str(p.relative_to(HERE)), 'error': obj.get('error')}) + '\n')
    if 'error' in obj:
        raise RuntimeError(obj['error'])
    save(p, obj['result'])
    return obj['result']

def main():
    txs = []
    tokens = set()
    for n in range(25918255, 25918259):
        b = read(RAW / 'blocks' / f'{n}.json.gz')
        logs = read(RAW / 'logs' / f'{n}.json.gz')
        for t in b['transactions']:
            if not any(t['hash'].startswith(p) for p in PREFIXES):
                continue
            h = t['hash']
            ls = [l for l in logs if l['transactionHash'] == h]
            save(HERE / 'raw' / (h + '_local.json'), {'block': {k: v for k, v in b.items() if k != 'transactions'}, 'tx': t, 'logs': ls})
            tokens.update(l['address'] for l in ls if l['topics'] and l['topics'][0] == TRANSFER)
            r = rpc('eth_getTransactionReceipt', [h], h + '_receipt')
            assert r['blockHash'] == b['hash'] and int(r['status'], 16) == 1
            assert r['logs'] == ls
            tr = rpc('debug_traceTransaction', [h, {'tracer': 'callTracer', 'timeout': '40s'}], h + '_trace')
            df = rpc('debug_traceTransaction', [h, {'tracer': 'prestateTracer', 'tracerConfig': {'diffMode': True}, 'timeout': '40s'}], h + '_diff')
            print('collected', h, 'gas', int(r['gasUsed'], 16), flush=True)
            txs.append(h)
    for a in sorted(tokens):
        for name, selector in [('symbol', '0x95d89b41'), ('name', '0x06fdde03'), ('decimals', '0x313ce567')]:
            try:
                rpc('eth_call', [{'to': a, 'data': selector}, hex(25918258)], a + '_' + name)
            except RuntimeError as e:
                print('metadata error', a, name, str(e), flush=True)
    save(HERE / 'transactions.json', txs)
    feed = '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419'
    for n in range(25918255, 25918259):
        header = rpc('eth_getBlockByNumber', [hex(n), False], str(n) + '_header')
        assert header['hash'] == read(RAW / 'blocks' / f'{n}.json.gz')['hash']
        rpc('eth_call', [{'to': feed, 'data': '0xfeaf968c'}, hex(n)], str(n) + '_eth_usd')
    rpc('eth_call', [{'to': feed, 'data': '0x313ce567'}, hex(25918258)], 'eth_usd_decimals')
    rpc('eth_call', [{'to': feed, 'data': '0x7284e416'}, hex(25918258)], 'eth_usd_description')

if __name__ == '__main__':
    main()
