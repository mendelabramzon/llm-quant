#!/usr/bin/env python3
"""Offline "what happened" digest over a window of raw blocks and logs written by `live_collect.py` / `eth_day_collect.py`.

Complements `live_scan.py` (which values flows) with block-level facts that need no prices: the ETH/USD path read from the
Uniswap v3 USDC/WETH 0.05% pool tick by tick, gas and blob usage, builders, transaction types (incl. EIP-7702 set-code),
contract creations, new pools, validator withdrawals, the largest top-level ETH transfers, the most urgent transactions
(highest priority fee per gas) and the transactions with the most logs. Everything is deterministic and written to
`<out>/events.json`; `--md` also prints markdown tables.

    uv run python scripts/window_events.py --out research/2026-09-07/live_5h --bucket 15 --md
"""
import argparse
import collections
import datetime as dt
import gzip
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USDC_WETH_V3 = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'
T_V3_SWAP = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
T_V2_PAIR_CREATED = '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'
T_V3_POOL_CREATED = '0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'
T_V4_INITIALIZE = '0xdd466e674ea557f56295e2d0218a125ea4b4f0f6d3bb446b8c05f4d3d2c9a1a4'
T_ERC20_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
# Blob inbox labels are from memory, not verified on chain; they are printed with that caveat.
BLOB_INBOX_LABELS = {
    '0xff00000000000000000000000000000000008453': 'Base batch inbox',
    '0xff00000000000000000000000000000000000010': 'OP Mainnet batch inbox',
    '0x1c479675ad559dc151f6ec7ed3fbf8cee79582b6': 'Arbitrum One sequencer inbox',
    '0xff00000000000000000000000000000000007777777': 'Zora batch inbox',
    '0xff00000000000000000000000000000000000480': 'World Chain batch inbox',
    '0xff00000000000000000000000000000000001868': 'Soneium batch inbox',
    '0xff00000000000000000000000000000000000130': 'Unichain batch inbox',
    '0xff00000000000000000000000000000000057073': 'Ink batch inbox',
    '0xff00000000000000000000000000000000000034443': 'Mode batch inbox',
    '0x2f1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c': None,
    '0xd19d4b5d358258f05d7b411e21a1460d11b0876f': 'Linea message service',
    '0xa13baf47339d63b743e7da8741db5456dac1e556': 'Scroll rollup',
    '0x3dbb3aa9fd6d6e5c48fd30a6d6f3c0e7b4a6f4a2': None,
    '0xc662c410c0ecf747543f5ba90660f6abebd9c8c4': 'Starknet core',
    '0x32400084c286cf3e17e7b677ea9583e60a000324': 'zkSync Era diamond',
    '0x06a9ab27c7e2255df1815e6cc0168d7755feb19a': 'Taiko L1',
}


def hx(v):
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime('%H:%M')


def utc_full(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec='seconds')


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def signed(word_hex):
    v = int(word_hex, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def extra_text(b):
    try:
        t = bytes.fromhex(b.get('extraData', '0x')[2:]).decode('utf-8', 'replace')
        t = ''.join(c if 32 <= ord(c) < 127 else '' for c in t).strip()
        return t or '(none)'
    except Exception:
        return '(undecodable)'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', required=True)
    p.add_argument('--bucket', type=int, default=15, help='minutes per bucket for the series')
    p.add_argument('--first', type=int)
    p.add_argument('--last', type=int)
    p.add_argument('--md', action='store_true')
    a = p.parse_args()
    out = Path(a.out)
    nums = sorted(int(x.name.split('.')[0]) for x in (out / 'raw' / 'blocks').glob('*.json.gz'))
    nums = [n for n in nums if (a.first is None or n >= a.first) and (a.last is None or n <= a.last) and (out / 'raw' / 'logs' / (str(n) + '.json.gz')).exists()]
    if not nums:
        raise SystemExit('no complete blocks in ' + str(out))
    bsec = a.bucket * 60
    buckets = collections.OrderedDict()
    builders = collections.Counter()
    tx_types = collections.Counter()
    creations = []
    blob_by_to = collections.defaultdict(lambda: {'txs': 0, 'blobs': 0, 'senders': set()})
    withdrawals = {'n': 0, 'eth': 0.0, 'large': []}
    eth_transfers = []
    urgent = []
    price_path = []      # (ts, block, price, usd volume proxy = |amount0|/1e6)
    new_pools = []
    log_heavy = collections.Counter()
    tx_by_hash_meta = {}
    senders = set()
    n_tx = n_logs = 0
    first_ts = last_ts = None
    gas_used_total = gas_limit_total = 0
    for n in nums:
        b = read_gz(out / 'raw' / 'blocks' / (str(n) + '.json.gz'))
        logs = read_gz(out / 'raw' / 'logs' / (str(n) + '.json.gz'))
        ts = hx(b['timestamp'])
        first_ts = ts if first_ts is None else first_ts
        last_ts = ts
        base = hx(b['baseFeePerGas'])
        gu, gl = hx(b['gasUsed']), hx(b['gasLimit'])
        gas_used_total += gu
        gas_limit_total += gl
        blobs = hx(b.get('blobGasUsed', '0x0')) // 131072
        k = (ts // bsec) * bsec
        bk = buckets.setdefault(k, {'from_utc': utc(k), 'blocks': 0, 'txs': 0, 'logs': 0, 'base_fee_gwei': [], 'fullness': [], 'blobs': 0, 'eth_px': [], 'v3_usdc_weth_usd': 0.0, 'withdrawn_eth': 0.0})
        bk['blocks'] += 1
        bk['txs'] += len(b['transactions'])
        bk['logs'] += len(logs)
        bk['base_fee_gwei'].append(base / 1e9)
        bk['fullness'].append(gu / gl if gl else 0)
        bk['blobs'] += blobs
        builders[extra_text(b)] += 1
        n_tx += len(b['transactions'])
        n_logs += len(logs)
        for w in b.get('withdrawals', []):
            amt = hx(w['amount']) / 1e9
            withdrawals['n'] += 1
            withdrawals['eth'] += amt
            bk['withdrawn_eth'] += amt
            if amt >= 1.0:
                withdrawals['large'].append({'block': n, 'utc': utc_full(ts), 'validator': hx(w['validatorIndex']), 'address': w['address'], 'eth': round(amt, 4)})
        for t in b['transactions']:
            tx_types[t.get('type', '0x0')] += 1
            senders.add(t['from'])
            tip = min(hx(t.get('maxPriorityFeePerGas', t.get('gasPrice', '0x0'))), max(0, hx(t.get('maxFeePerGas', t.get('gasPrice', '0x0'))) - base)) if t.get('type') in ('0x2', '0x3', '0x4') else max(0, hx(t.get('gasPrice', '0x0')) - base)
            tx_by_hash_meta[t['hash']] = (t['from'], t.get('to'), hx(t['gas']))
            if t.get('to') is None:
                creations.append({'block': n, 'utc': utc_full(ts), 'tx': t['hash'], 'from': t['from'], 'input_bytes': (len(t.get('input', '0x')) - 2) // 2, 'nonce': hx(t['nonce'])})
            if t.get('type') == '0x3':
                d = blob_by_to[t.get('to')]
                d['txs'] += 1
                d['blobs'] += len(t.get('blobVersionedHashes', []) or [])
                d['senders'].add(t['from'])
            v = hx(t.get('value', '0x0'))
            if v >= 100 * 10 ** 18:
                eth_transfers.append({'block': n, 'utc': utc_full(ts), 'tx': t['hash'], 'from': t['from'], 'to': t.get('to'), 'eth': round(v / 1e18, 3), 'input_bytes': (len(t.get('input', '0x')) - 2) // 2})
            if tip >= 5 * 10 ** 9:
                urgent.append({'block': n, 'utc': utc_full(ts), 'tx': t['hash'], 'from': t['from'], 'to': t.get('to'), 'tip_gwei': round(tip / 1e9, 2), 'gas_limit': hx(t['gas']), 'max_tip_eth_at_limit': round(tip * hx(t['gas']) / 1e18, 4), 'index': hx(t['transactionIndex'])})
        per_tx_logs = collections.Counter()
        for l in logs:
            per_tx_logs[l['transactionHash']] += 1
            tp = l['topics'][0] if l['topics'] else None
            if tp == T_V3_SWAP and l['address'].lower() == USDC_WETH_V3:
                d = l['data'][2:]
                amount0 = signed(d[0:64])
                sqrtp = int(d[128:192], 16)
                pr = (sqrtp / 2 ** 96) ** 2
                if pr > 0:
                    px = 1e12 / pr
                    price_path.append((ts, n, px, abs(amount0) / 1e6))
                    bk['eth_px'].append(px)
                    bk['v3_usdc_weth_usd'] += abs(amount0) / 1e6
            elif tp == T_V2_PAIR_CREATED and len(l['topics']) == 3:
                new_pools.append({'venue': 'v2-style', 'factory': l['address'], 'block': n, 'utc': utc_full(ts), 'token0': '0x' + l['topics'][1][-40:], 'token1': '0x' + l['topics'][2][-40:], 'pool': '0x' + l['data'][26:66], 'tx': l['transactionHash']})
            elif tp == T_V3_POOL_CREATED and len(l['topics']) == 4:
                new_pools.append({'venue': 'v3-style', 'factory': l['address'], 'block': n, 'utc': utc_full(ts), 'token0': '0x' + l['topics'][1][-40:], 'token1': '0x' + l['topics'][2][-40:], 'fee': int(l['topics'][3], 16) / 1e6, 'pool': '0x' + l['data'][-40:], 'tx': l['transactionHash']})
            elif tp == T_V4_INITIALIZE and len(l['topics']) == 4:
                d = l['data'][2:]
                new_pools.append({'venue': 'uniswap_v4', 'manager': l['address'], 'block': n, 'utc': utc_full(ts), 'pool_id': l['topics'][1], 'token0': '0x' + l['topics'][2][-40:], 'token1': '0x' + l['topics'][3][-40:], 'fee': int(d[0:64], 16) / 1e6, 'hook': '0x' + d[64 + 24:128], 'tx': l['transactionHash']})
        for h, c in per_tx_logs.items():
            if c >= 200:
                log_heavy[h] = c
    # summaries
    series = []
    for k, bk in buckets.items():
        px = bk['eth_px']
        series.append({'from_utc': bk['from_utc'], 'blocks': bk['blocks'], 'txs': bk['txs'], 'logs': bk['logs'],
                       'base_fee_gwei_median': round(statistics.median(bk['base_fee_gwei']), 4), 'base_fee_gwei_max': round(max(bk['base_fee_gwei']), 4),
                       'fullness': round(statistics.mean(bk['fullness']), 3), 'blobs': bk['blobs'],
                       'eth_open': round(px[0], 2) if px else None, 'eth_high': round(max(px), 2) if px else None, 'eth_low': round(min(px), 2) if px else None, 'eth_close': round(px[-1], 2) if px else None,
                       'v3_usdc_weth_usd': round(bk['v3_usdc_weth_usd']), 'withdrawn_eth': round(bk['withdrawn_eth'], 2)})
    moves = []
    # largest move over any 5-minute span of the tick path
    pp = price_path
    j = 0
    for i in range(len(pp)):
        while j < len(pp) and pp[j][0] - pp[i][0] <= 300:
            j += 1
        if j - 1 > i:
            seg = pp[i:j]
            hi = max(seg, key=lambda x: x[2])
            lo = min(seg, key=lambda x: x[2])
            moves.append((abs(hi[2] - lo[2]) / lo[2], pp[i][0], hi, lo))
    top_moves = []
    for m in sorted(moves, key=lambda m: -m[0]):
        lo_b, hi_b = min(m[2][1], m[3][1]), max(m[2][1], m[3][1])
        if any(not (hi_b < min(k[2][1], k[3][1]) - 25 or lo_b > max(k[2][1], k[3][1]) + 25) for k in top_moves):
            continue
        top_moves.append(m)
        if len(top_moves) == 5:
            break
    res = {
        'window': {'first_block': nums[0], 'last_block': nums[-1], 'blocks': len(nums), 'first_utc': utc_full(first_ts), 'last_utc': utc_full(last_ts), 'hours': round((last_ts - first_ts + 12) / 3600, 3),
                   'transactions': n_tx, 'logs': n_logs, 'unique_senders': len(senders), 'gas_used': gas_used_total, 'fullness': round(gas_used_total / gas_limit_total, 4)},
        'eth_price': {'open': round(pp[0][2], 2) if pp else None, 'close': round(pp[-1][2], 2) if pp else None, 'high': round(max(x[2] for x in pp), 2) if pp else None, 'low': round(min(x[2] for x in pp), 2) if pp else None,
                      'swaps': len(pp), 'usd_volume': round(sum(x[3] for x in pp)),
                      'largest_5min_moves': [{'pct': round(m[0] * 100, 3), 'from_utc': utc_full(m[1]), 'high': round(m[2][2], 2), 'high_block': m[2][1], 'low': round(m[3][2], 2), 'low_block': m[3][1]} for m in top_moves]},
        'series': series,
        'builders': builders.most_common(),
        'tx_types': dict(tx_types),
        'blobs': {'total': sum(v['blobs'] for v in blob_by_to.values()), 'by_inbox': sorted([{'to': k, 'label': BLOB_INBOX_LABELS.get(k), 'txs': v['txs'], 'blobs': v['blobs'], 'senders': sorted(v['senders'])} for k, v in blob_by_to.items()], key=lambda r: -r['blobs'])},
        'contract_creations': {'n': len(creations), 'by_creator': collections.Counter(c['from'] for c in creations).most_common(10), 'largest': sorted(creations, key=lambda c: -c['input_bytes'])[:10]},
        'new_pools': new_pools,
        'withdrawals': {'n': withdrawals['n'], 'eth': round(withdrawals['eth'], 2), 'large_n': len(withdrawals['large']), 'large_eth': round(sum(w['eth'] for w in withdrawals['large']), 2), 'largest': sorted(withdrawals['large'], key=lambda w: -w['eth'])[:10]},
        'eth_transfers_100plus': sorted(eth_transfers, key=lambda x: -x['eth'])[:25],
        'urgent': sorted(urgent, key=lambda x: -x['tip_gwei'])[:25],
        'log_heavy': [{'tx': h, 'logs': c, 'from': tx_by_hash_meta.get(h, (None,))[0], 'to': tx_by_hash_meta.get(h, (None, None))[1]} for h, c in log_heavy.most_common(15)],
    }
    (out / 'events.json').write_text(json.dumps(res, indent=1))
    if a.md:
        w = res['window']
        print('## Window: blocks %d to %d, %s to %s UTC (%.2f h), %s txs, %s logs, %s unique senders, blocks %.0f%% full\n' % (w['first_block'], w['last_block'], w['first_utc'], w['last_utc'], w['hours'], f"{w['transactions']:,}", f"{w['logs']:,}", f"{w['unique_senders']:,}", w['fullness'] * 100))
        e = res['eth_price']
        print('ETH/USD from the v3 USDC/WETH 0.05%% pool: open %s, high %s, low %s, close %s over %d swaps ($%s).\n' % (e['open'], e['high'], e['low'], e['close'], e['swaps'], f"{e['usd_volume']:,}"))
        print('| from UTC | blocks | txs | base fee med (gwei) | max | full | blobs | ETH open | high | low | close | v3 USDC/WETH $ | withdrawn ETH |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|')
        for s in series:
            print('| %s | %d | %d | %.4f | %.4f | %.0f%% | %d | %s | %s | %s | %s | %s | %.1f |' % (s['from_utc'], s['blocks'], s['txs'], s['base_fee_gwei_median'], s['base_fee_gwei_max'], s['fullness'] * 100, s['blobs'], s['eth_open'], s['eth_high'], s['eth_low'], s['eth_close'], f"{s['v3_usdc_weth_usd']:,}", s['withdrawn_eth']))
        print('\nLargest 5-minute ETH moves: ' + '; '.join('%.2f%% from %s (%s at %d to %s at %d)' % (m['pct'], m['from_utc'][11:19], m['high'] if m['high_block'] > m['low_block'] else m['low'], min(m['high_block'], m['low_block']), m['low'] if m['high_block'] > m['low_block'] else m['high'], max(m['high_block'], m['low_block'])) for m in e['largest_5min_moves']))
        print('\nBuilders: ' + ', '.join('%s %d' % (b, c) for b, c in res['builders'][:8]))
        print('Transaction types: ' + ', '.join('%s %d' % (k, v) for k, v in sorted(res['tx_types'].items())))
        print('\nBlobs: %d total. ' % res['blobs']['total'] + '; '.join('%s %s: %d blobs in %d txs' % (r['to'][:10], r['label'] or '(unlabelled inbox)', r['blobs'], r['txs']) for r in res['blobs']['by_inbox'][:12]) + ' (labels from memory, unverified)')
        c = res['contract_creations']
        print('\nContract creations: %d; top creators: ' % c['n'] + ', '.join('%s %d' % (a_[:10], k) for a_, k in c['by_creator'][:6]))
        print('New pools: %d (%s)' % (len(new_pools), ', '.join('%s %d' % (v, k) for v, k in collections.Counter(x['venue'] for x in new_pools).items())))
        wd = res['withdrawals']
        print('Validator withdrawals: %d for %.1f ETH, of which %d of at least 1 ETH totalling %.1f ETH' % (wd['n'], wd['eth'], wd['large_n'], wd['large_eth']))
        print('\n| largest top-level ETH transfers | UTC | from | to | ETH |\n|---|---|---|---|---|')
        for x in res['eth_transfers_100plus'][:15]:
            print('| %s | %s | %s | %s | %s |' % (x['tx'][:12], x['utc'][11:19], x['from'][:10], (x['to'] or 'create')[:10], f"{x['eth']:,.1f}"))
        print('\n| most urgent (tip per gas) | UTC | from | to | tip gwei | gas limit | idx |\n|---|---|---|---|---|---|---|')
        for x in res['urgent'][:15]:
            print('| %s | %s | %s | %s | %.1f | %s | %d |' % (x['tx'][:12], x['utc'][11:19], x['from'][:10], (x['to'] or 'create')[:10], x['tip_gwei'], f"{x['gas_limit']:,}", x['index']))
        print('\n| log-heavy txs | logs | from | to |\n|---|---|---|---|')
        for x in res['log_heavy'][:10]:
            print('| %s | %d | %s | %s |' % (x['tx'][:12], x['logs'], (x['from'] or '')[:10], (x['to'] or '')[:10]))


if __name__ == '__main__':
    main()
