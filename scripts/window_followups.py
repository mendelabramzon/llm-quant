#!/usr/bin/env python3
"""Deterministic follow-up checks behind the 2026-09-07 five-hour insights (offline, over the raw blocks and logs).

Each check is a question the qualitative pass asked; the addresses are configured at the top so the same checks can be
re-pointed at another window. Writes `<out>/followups.json` and prints a markdown digest.

    uv run python scripts/window_followups.py --out research/2026-09-07/live_5h
"""
import argparse
import collections
import datetime as dt
import gzip
import json
from pathlib import Path

T_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
T_V4_SWAP = '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f'
POOL_MANAGER = '0x000000000004444c5dc75cb358380d2e3de08a90'
CONFIG = {
    # contracts whose call profile explains the 03:45-04:10 base-fee spike (tokenized-stock routers, verified names from Blockscout where given)
    'targets': {
        '0x4313c378cc91ea583c91387b9216e2c03096b27f': 'stock router A (TransparentUpgradeableProxy, impl 0xB8F6534F, unverified)',
        '0x5228ed975c6bcb53d2e221ba737362fd9add0b60': 'stock router B (proxy, impl 0xaB9d8404, unverified)',
        '0xf9280799c85d376e0425f6fb38e4a674e8bedb56': 'stock router C (unverified)',
        '0x00000000fd3a7b3fa5bcfa843c648714b11e089b': 'arb bot on the same pools',
        '0x4337084d9e255ff0702461cf8895ce9e3b5ff108': 'ERC-4337 EntryPoint v0.8',
        '0xccc88a9d1b4ed6b0eaba998850414b24f1c315be': 'router (Artificial Pepe / USDC flow)',
    },
    'spike_window': ('03:25:00', '04:25:00'),
    'tokens': {
        '0xc9eef266834730340a55b6cc24621b31baf55581': ('SPCXON', 18), '0x2d1f7226bd1f780af6b9a49dcc0ae00e8df4bdee': ('NVDAON', 18),
        '0xf6b1117ec07684d3958cad8beb1b302bfd21103f': ('TSLAON', 18), '0xfedc5f4a6c38211c1338aa411018dfaf26612c08': ('SPYON', 18),
        '0x75e2fc69ff2ac12af65ba7d321bbf4f878c535d2': ('STOCKER', 18), '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': ('USDC', 6),
        '0xdac17f958d2ee523a2206206994597c13d831ec7': ('USDT', 6), '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': ('WETH', 18),
        '0x0000000000000000000000000000000000000000': ('ETH', 18),
    },
    'stock_tokens': ['SPCXON', 'NVDAON', 'TSLAON', 'SPYON', 'STOCKER'],
    'eth_usd_fallback': 2500.0,
    'flash_bot_eoa': '0x23fdc534cfbbf7cfda0acb15e0e340939f319b6a',
    'mass_token_min_logs': 1000,
    'poison_min_eth': 1000.0,
    'poison_max_value_eth': 0.001,   # poisoning txs carry dust (1e-6 ETH observed), not strictly zero
    'spark_alm': '0x1601843c5e9bc251a3272907010afa41fa18347e',
    'stables': {'0xdac17f958d2ee523a2206206994597c13d831ec7': ('USDT', 6), '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': ('USDC', 6), '0xdc035d45d973e3ec169d2276ddab16f1e407384f': ('USDS', 18), '0x6b175474e89094c44da98b954eedeac495271d0f': ('DAI', 18)},
}


def hx(v):
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v or 0)


def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec='seconds')


def hms(ts):
    return utc(ts)[11:19]


def signed(h):
    v = int(h, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def read_gz(p):
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    out = Path(a.out)
    C = CONFIG
    nums = sorted(int(x.name.split('.')[0]) for x in (out / 'raw' / 'blocks').glob('*.json.gz') if (out / 'raw' / 'logs' / x.name).exists())
    pools = json.loads((out / 'pools.json').read_text()) if (out / 'pools.json').exists() else {}
    eth_usd = C['eth_usd_fallback']
    hs = out / 'head_state.json'
    if hs.exists():
        eth_usd = (json.loads(hs.read_text()).get('feeds', {}).get('ETH') or {}).get('usd') or eth_usd
    prof = {t: {'label': l, 'txs': 0, 'senders': set(), 'fresh_senders': set(), 'value_eth': 0.0, 'gas_limit': 0, 'gas_limit_spike': 0, 'gas_limit_pre_spike': 0, 'per_hour': collections.Counter(), 'selectors': collections.Counter()} for t, l in C['targets'].items()}
    router_targets = [t for t in C['targets'] if 'stock router' in C['targets'][t]]
    union_senders, union_fresh, nonce_hist, tx_by_sender = set(), set(), collections.Counter(), collections.Counter()
    eth_in = collections.defaultdict(list)
    v4 = collections.defaultdict(lambda: {'n': 0, 'a0': 0, 'a1': 0, 'senders': set(), 'last_sqrt': None})
    mint, burn = collections.Counter(), collections.Counter()
    bot_runs, bot_first_logs = [], None
    big_native, zero_value = [], []
    token_logs = collections.Counter()
    mass = collections.defaultdict(lambda: {'transfers': 0, 'recipients': set(), 'from_zero': 0, 'from_self': 0, 'txs': set()})
    alm = []
    t0, t1 = C['spike_window']
    for n in nums:
        b = read_gz(out / 'raw' / 'blocks' / (str(n) + '.json.gz'))
        logs = read_gz(out / 'raw' / 'logs' / (str(n) + '.json.gz'))
        ts = hx(b['timestamp'])
        h = hms(ts)
        txfrom = {t['hash']: t['from'] for t in b['transactions']}
        for t in b['transactions']:
            to = t.get('to') or ''
            v = hx(t['value'])
            if to in prof:
                q = prof[to]
                q['txs'] += 1
                q['senders'].add(t['from'])
                q['value_eth'] += v / 1e18
                q['gas_limit'] += hx(t['gas'])
                q['per_hour'][h[:2]] += 1
                q['selectors'][t['input'][:10]] += 1
                if hx(t['nonce']) < 5:
                    q['fresh_senders'].add(t['from'])
                if t0 <= h <= t1:
                    q['gas_limit_spike'] += hx(t['gas'])
                elif h < t0:
                    q['gas_limit_pre_spike'] += hx(t['gas'])
            if to in router_targets:
                union_senders.add(t['from'])
                tx_by_sender[t['from']] += 1
                nonce_hist[min(hx(t['nonce']) // 10, 10)] += 1
                if hx(t['nonce']) < 5:
                    union_fresh.add(t['from'])
            if v > 0 and t['input'] == '0x' and to:
                eth_in[to].append((t['from'], v / 1e18, ts))
                if v >= C['poison_min_eth'] * 1e18:
                    big_native.append({'utc': utc(ts), 'ts': ts, 'tx': t['hash'], 'from': t['from'], 'to': to, 'eth': round(v / 1e18, 3)})
            if v <= C['poison_max_value_eth'] * 1e18 and t['input'] == '0x' and to:
                zero_value.append((ts, t['from'], to, t['hash'], v / 1e18))
            if t['from'] == C['flash_bot_eoa']:
                bot_runs.append({'utc': utc(ts), 'tx': t['hash'], 'to': to, 'gas_limit': hx(t['gas'])})
        for l in logs:
            tp = l['topics'][0] if l['topics'] else ''
            if tp == T_V4_SWAP:
                toks = (pools.get(l['topics'][1], {}).get('tokens') or [None, None])
                syms = [C['tokens'].get(x, (None, 18))[0] for x in toks]
                if any(s in C['stock_tokens'] for s in syms):
                    d = l['data'][2:]
                    q = v4[l['topics'][1]]
                    q['n'] += 1
                    q['a0'] += abs(signed(d[0:64]))
                    q['a1'] += abs(signed(d[64:128]))
                    q['senders'].add(txfrom.get(l['transactionHash']))
                    q['toks'] = toks
                    q['last_sqrt'] = int(d[128:192], 16)
            if tp == T_TRANSFER and len(l['topics']) == 3:
                token_logs[l['address']] += 1
                if l['address'] in C['tokens'] and C['tokens'][l['address']][0] in C['stock_tokens']:
                    amt = int(l['data'], 16) / 1e18
                    if l['topics'][1].endswith('0' * 40):
                        mint[C['tokens'][l['address']][0]] += amt
                    if l['topics'][2].endswith('0' * 40):
                        burn[C['tokens'][l['address']][0]] += amt
                m = mass[l['address']]
                m['transfers'] += 1
                m['recipients'].add(l['topics'][2])
                m['txs'].add(l['transactionHash'])
                if l['topics'][1].endswith('0' * 40):
                    m['from_zero'] += 1
                if l['topics'][1][-40:] == l['address'][2:]:
                    m['from_self'] += 1
            if tp == T_TRANSFER and len(l['topics']) == 3 and l['address'] in C['stables']:
                fr, to2 = '0x' + l['topics'][1][-40:], '0x' + l['topics'][2][-40:]
                if C['spark_alm'] in (fr, to2):
                    sym, d = C['stables'][l['address']]
                    amt = int(l['data'], 16) / 10 ** d
                    if amt >= 1e6:
                        alm.append({'utc': utc(ts), 'tx': l['transactionHash'], 'tx_sender': txfrom.get(l['transactionHash']), 'token': sym, 'from': fr, 'to': to2, 'usd_m': round(amt / 1e6, 3)})
        if bot_runs and bot_first_logs is None and any(r['tx'] == l['transactionHash'] for r in bot_runs[:1] for l in logs[:1]) is False:
            pass
        if bot_runs and bot_first_logs is None:
            first = bot_runs[0]['tx']
            sel = [l for l in logs if l['transactionHash'] == first]
            if sel:
                bot_first_logs = [{'address': l['address'], 'topic0': l['topics'][0][:10], 'topics': ['0x' + x[-40:] for x in l['topics'][1:]], 'data0': l['data'][:66]} for l in sel]
    # summaries
    def fin(q):
        return {'label': q['label'], 'txs': q['txs'], 'senders': len(q['senders']), 'fresh_senders_nonce_lt_5': len(q['fresh_senders']), 'value_eth': round(q['value_eth'], 2), 'gas_limit_m': round(q['gas_limit'] / 1e6, 1),
                'gas_limit_m_in_spike_window': round(q['gas_limit_spike'] / 1e6, 1), 'gas_limit_m_before_spike_window': round(q['gas_limit_pre_spike'] / 1e6, 1), 'per_hour': dict(sorted(q['per_hour'].items())), 'selectors': q['selectors'].most_common(3)}
    funders = collections.Counter()
    funded, amounts = 0, []
    for w in union_fresh:
        for fr, v, ts in eth_in.get(w, []):
            funders[fr] += 1
            funded += 1
            amounts.append(v)
    pool_rows, total_one_side = [], 0.0
    for pid, q in sorted(v4.items(), key=lambda kv: -kv[1]['n']):
        s0, d0 = C['tokens'].get(q['toks'][0], ((q['toks'][0] or '?')[:10], 18))
        s1, d1 = C['tokens'].get(q['toks'][1], ((q['toks'][1] or '?')[:10], 18))
        g0, g1 = q['a0'] / 10 ** d0, q['a1'] / 10 ** d1
        usd = g0 / 2 if s0 in ('USDC', 'USDT') else g1 / 2 if s1 in ('USDC', 'USDT') else g0 / 2 * eth_usd if s0 in ('WETH', 'ETH') else g1 / 2 * eth_usd if s1 in ('WETH', 'ETH') else None
        px = (q['last_sqrt'] / 2 ** 96) ** 2 * 10 ** d0 / 10 ** d1 if q['last_sqrt'] else None
        total_one_side += usd or 0
        pool_rows.append({'pool': pid, 'pair': s0 + '/' + s1, 'swaps': q['n'], 'senders': len(q['senders']), 'gross_' + s0: round(g0, 2), 'gross_' + s1: round(g1, 2), 'one_side_usd': round(usd) if usd else None, 'last_price_t1_in_t0': px})
    poison = []
    for bt in big_native:
        for ts, fr, to, h, dv in zero_value:
            if 0 <= ts - bt['ts'] <= 3600 and to in (bt['from'], bt['to']):
                other = bt['to'] if to == bt['from'] else bt['from']
                if fr != other and (fr[:6] == other[:6] or fr[-4:] == other[-4:] or fr[:6] == to[:6]):
                    poison.append({'after_tx': bt['tx'], 'eth': bt['eth'], 'victim': to, 'lookalike': fr, 'mimics': other if (fr[:6] == other[:6] or fr[-4:] == other[-4:]) else to, 'seconds_after': ts - bt['ts'], 'value_eth': dv, 'tx': h})
    mass_rows = [{'token': t, 'transfers': m['transfers'], 'recipients': len(m['recipients']), 'from_zero': m['from_zero'], 'from_self': m['from_self'], 'txs': len(m['txs'])} for t, m in mass.items() if m['transfers'] >= C['mass_token_min_logs'] and (m['from_zero'] + m['from_self']) >= 0.5 * m['transfers']]
    res = {
        'window': {'first_block': nums[0], 'last_block': nums[-1], 'eth_usd_used': eth_usd},
        'spike_targets': {t: fin(q) for t, q in prof.items()},
        'stock_routers': {'senders_union': len(union_senders), 'fresh_senders_union': len(union_fresh), 'txs_by_sender_nonce_decile': sorted(nonce_hist.items()), 'top_senders': tx_by_sender.most_common(5),
                          'fresh_funded_in_window': funded, 'distinct_funders': len(funders), 'top_funders': funders.most_common(8), 'funding_eth_median': sorted(amounts)[len(amounts) // 2] if amounts else None},
        'stock_pools': {'pools': len(pool_rows), 'one_side_usd_total': round(total_one_side), 'rows': pool_rows[:40]},
        'stock_issuance': {'minted': {k: round(v, 2) for k, v in mint.items()}, 'burned': {k: round(v, 2) for k, v in burn.items()}},
        'flash_bot': {'eoa': C['flash_bot_eoa'], 'runs': bot_runs, 'first_run_logs': bot_first_logs},
        'poisoning': {'big_native_transfers': len(big_native), 'lookalike_dust_txs': poison},
        'mass_token_events': sorted(mass_rows, key=lambda r: -r['transfers'])[:10],
        'spark_alm': alm,
    }
    (out / 'followups.json').write_text(json.dumps(res, indent=1, default=str))
    print('## Spike targets (gas limit, M)')
    for t, q in res['spike_targets'].items():
        print('- %s %s: %d txs, %d senders (%d fresh), %.1f ETH value, gas %.0fM (%.0fM in %s-%s vs %.0fM before), per hour %s' % (t[:10], q['label'], q['txs'], q['senders'], q['fresh_senders_nonce_lt_5'], q['value_eth'], q['gas_limit_m'], q['gas_limit_m_in_spike_window'], t0[:5], t1[:5], q['gas_limit_m_before_spike_window'], q['per_hour']))
    s = res['stock_routers']
    print('\nStock routers: %d senders, %d fresh; %d fresh funded in-window by %d distinct funders (top %s), median funding %s ETH; nonce deciles %s' % (s['senders_union'], s['fresh_senders_union'], s['fresh_funded_in_window'], s['distinct_funders'], s['top_funders'][:3], s['funding_eth_median'], s['txs_by_sender_nonce_decile']))
    print('\nStock pools: %d pools, one-side USD total %s; issuance minted %s burned %s' % (res['stock_pools']['pools'], res['stock_pools']['one_side_usd_total'], res['stock_issuance']['minted'], res['stock_issuance']['burned']))
    for r in pool_rows[:8]:
        print('  ', r['pair'], r['swaps'], 'swaps', r['senders'], 'senders', 'one-side $', r['one_side_usd'], 'last px', round(r['last_price_t1_in_t0'], 4) if r['last_price_t1_in_t0'] else None)
    print('\nFlash bot runs: %d %s' % (len(bot_runs), [r['utc'][11:19] for r in bot_runs]))
    print('Poisoning: %d look-alike dust-value txs (<= %g ETH) after %d native transfers >= %.0f ETH' % (len(poison), C['poison_max_value_eth'], len(big_native), C['poison_min_eth']))
    for x in poison[:12]:
        print('  ', x['eth'], 'ETH', x['victim'][:10], '<-', x['lookalike'][:10], 'mimics', x['mimics'][:10], '+%ds' % x['seconds_after'])
    print('Mass token events:', res['mass_token_events'][:6])
    print('Spark ALM stablecoin legs >= $1M:')
    for x in alm[:40]:
        print('  ', x['utc'][11:19], x['tx'][:12], 'sender', x['tx_sender'][:10], x['token'], x['from'][:10], '->', x['to'][:10], x['usd_m'], 'M')


if __name__ == '__main__':
    main()
