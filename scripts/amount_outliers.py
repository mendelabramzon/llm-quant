#!/usr/bin/env python3
"""Quant -> qual loop, second iteration: transactions that move large USD amounts.

prices   Bounded read-only RPC. Reads Chainlink USD feeds pinned at each chain's last sampled block
         (the feed's description() must match the expected pair before its answer is used) and the
         wstETH/stETH ratio, computes an in-sample ETH price from swaps in the factory-verified
         USDC/WETH pools as a cross-check, and writes prices.json. No key is written to output.
scan     Deterministic and offline. Values every top-level native transfer, every ERC-20 transfer of a
         registry token, and every WETH wrap/unwrap in USD; nets them per (address, asset) inside the
         transaction; ranks user transactions by three amount metrics; describes the population above
         the threshold (assets, shapes, repeated patterns, repeat actors); writes evidence packets for
         the top K per metric (at most one per repeated pattern) plus hash-sampled controls.
resolve  Bounded RPC: symbol/decimals for tokens in the packets (registry entries are checked against
         the chain) and code presence for addresses. Cached.
render   packets + prices + context + LLM-written qual_notes.md -> report.md.
show     Full decoded logs for one transaction (shared with gas_outliers).

The LLM reads packets.json, not raw blocks, and writes qual_notes.md. Exact numbers in the report come
from this code; the notes carry interpretation only.
"""
import argparse
import collections
from decimal import Decimal, getcontext
import hashlib
import json
from pathlib import Path
import statistics

from onchain_probe import ROOT, RPC, hx, save, utc, is_polygon_fee_log
from analyze_onchain import RUN, decode, signed, address as topic_address
from enrich_cases import decode_string, selector as sel4
from gas_outliers import (EXPLORERS, NATIVE, SYSTEM_TYPES, MINIMAL_PROXY, SAMPLE_EVENTS, gwei, native, short, tx_link,
                          addr_link, raw_blocks, rows_for, describe, position, event_view, parse_notes, show)

getcontext().prec = 50
WETH_DEPOSIT = '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'
WETH_WITHDRAWAL = '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'
ZERO = '0x' + '0' * 40
METRICS = {'position_change_usd': 'largest position change', 'gross_volume_usd': 'gross priced volume',
           'native_value_usd': 'native value sent'}
SWAP_FAMILIES = ('V2Swap', 'V3Swap', 'V4Swap')

# Asset registry: (chain, token address) -> (label, decimals, price key). Addresses are the canonical
# deployments as known to the author; `resolve` reads symbol() and decimals() from each contract and the
# report shows both when they differ. Price keys resolve through prices.json; 'USD' means assumed parity.
ASSETS = {
    'ethereum': {
        '0xdac17f958d2ee523a2206206994597c13d831ec7': ('USDT', 6, 'USDT'),
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': ('USDC', 6, 'USDC'),
        '0x6b175474e89094c44da98b954eedeac495271d0f': ('DAI', 18, 'DAI'),
        '0x4c9edd5852cd905f086c759e8383e09bff1e68b3': ('USDe', 18, 'USD'),
        '0xdc035d45d973e3ec169d2276ddab16f1e407384f': ('USDS', 18, 'USD'),
        '0x6c3ea9036406852006290770bedfcaba0e23a0e8': ('PYUSD', 6, 'USD'),
        '0x5f98805a4e8be255a32880fdec7f6728c6568ba0': ('LUSD', 18, 'USD'),
        '0xf939e0a03fb07f59a73314e73794be0e57ac1b4e': ('crvUSD', 18, 'USD'),
        '0xc5f0f7b66764f6ec8c8dff7ba683102295e16409': ('FDUSD', 18, 'USD'),
        '0x73a15fed60bf67631dc6cd7bc5b6e8da8190acf5': ('USD0', 18, 'USD'),
        '0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f': ('GHO', 18, 'USD'),
        '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': ('WETH', 18, 'ETH'),
        '0xae7ab96520de3a18e5e111b5eaab095312d7fe84': ('stETH', 18, 'STETH'),
        '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0': ('wstETH', 18, 'WSTETH'),
        '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599': ('WBTC', 8, 'BTC'),
        '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf': ('cbBTC', 8, 'BTC'),
        '0x514910771af9ca656af840dff83e8264ecf986ca': ('LINK', 18, 'LINK'),
        '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984': ('UNI', 18, 'UNI'),
        '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9': ('AAVE', 18, 'AAVE'),
    },
    'base': {
        '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913': ('USDC', 6, 'USDC'),
        '0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca': ('USDbC', 6, 'USD'),
        '0xfde4c96c8593536e31f229ea8f37b2ada2699bb2': ('USDT', 6, 'USDT'),
        '0x50c5725949a6f0c72e6c4a641f24049a917db0cb': ('DAI', 18, 'DAI'),
        '0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34': ('USDe', 18, 'USD'),
        '0x4200000000000000000000000000000000000006': ('WETH', 18, 'ETH'),
        '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf': ('cbBTC', 8, 'BTC'),
    },
    'arbitrum': {
        '0xaf88d065e77c8cc2239327c5edb3a432268e5831': ('USDC', 6, 'USDC'),
        '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8': ('USDC.e', 6, 'USD'),
        '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9': ('USDT', 6, 'USDT'),
        '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': ('DAI', 18, 'DAI'),
        '0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34': ('USDe', 18, 'USD'),
        '0x82af49447d8a07e3bd95bd0d56f35241523fbab1': ('WETH', 18, 'ETH'),
        '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f': ('WBTC', 8, 'BTC'),
        '0x912ce59144191c1204e64559fe8253a0e49e6548': ('ARB', 18, 'ARB'),
        '0xf97f4df75117a78c1a5a0dbb814af92458539fb4': ('LINK', 18, 'LINK'),
    },
    'optimism': {
        '0x0b2c639c533813f4aa9d7837caf62653d097ff85': ('USDC', 6, 'USDC'),
        '0x7f5c764cbc14f9669b88837ca1490cca17c31607': ('USDC.e', 6, 'USD'),
        '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58': ('USDT', 6, 'USDT'),
        '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': ('DAI', 18, 'DAI'),
        '0x4200000000000000000000000000000000000006': ('WETH', 18, 'ETH'),
        '0x68f180fcce6836688e9084f035309e29bf0a2095': ('WBTC', 8, 'BTC'),
        '0x4200000000000000000000000000000000000042': ('OP', 18, 'OP'),
    },
    'polygon': {
        '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359': ('USDC', 6, 'USDC'),
        '0x2791bca1f2de4661ed88a30c99a7a9449aa84174': ('USDC.e', 6, 'USD'),
        '0xc2132d05d31c914a87c6611c10748aeb04b58e8f': ('USDT', 6, 'USDT'),
        '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063': ('DAI', 18, 'DAI'),
        '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619': ('WETH', 18, 'ETH'),
        '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270': ('WPOL', 18, 'POL'),
        '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6': ('WBTC', 8, 'BTC'),
        '0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39': ('LINK', 18, 'LINK'),
    },
}
WETH = {c: next(a for a, (s, _, _) in reg.items() if s == 'WETH') for c, reg in ASSETS.items()}
NATIVE_KEY = collections.defaultdict(lambda: 'ETH', polygon='POL')
STABLE_KEYS = {'USD', 'USDC', 'USDT', 'DAI'}
# Chainlink aggregator proxies, candidates in order of preference. description() is read from the chain and
# must match before an answer is used; the first verified candidate wins.
FEEDS = {
    'ETH': [('ethereum', '0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419', ('ETH / USD',))],
    'BTC': [('ethereum', '0xf4030086522a5beea4988f8ca5b36dba2ced6c8a', ('BTC / USD',)),
            ('arbitrum', '0x6ce185860a4963106506c203335a2910413708e9', ('BTC / USD',)),
            ('polygon', '0xc907e116054ad103354f2d350fd2514433d57f6f', ('BTC / USD',))],
    'LINK': [('ethereum', '0x2c1d072e956affc0d435cb7ac38ef18d24d9127c', ('LINK / USD',))],
    'UNI': [('ethereum', '0x553303d460ee0afb37edff9be42922d8ff63220e', ('UNI / USD',))],
    'AAVE': [('ethereum', '0x547a514d5e3769680ce22b2361c10ea13619e8a9', ('AAVE / USD',))],
    'STETH': [('ethereum', '0xcfe54b5cd566ab89272946f602d76ea879cab4a8', ('STETH / USD',))],
    'USDC': [('ethereum', '0x8fffffd4afb6115b954bd326cbe7b4ba576818f6', ('USDC / USD',))],
    'USDT': [('ethereum', '0x3e7d1eab13ad0104d2750b8863b489d65364e32d', ('USDT / USD',))],
    'DAI': [('ethereum', '0xaed0c38402a5d19df6e4c03f4e2dced6e29c1ee9', ('DAI / USD',))],
    'POL': [('polygon', '0xab594600376ec9fd91f8e885dadf0ce036862de0', ('MATIC / USD', 'POL / USD'))],
    'ARB': [('arbitrum', '0xb2a824043730fe05f3da2efafa1cbbe83fa548d6', ('ARB / USD',))],
    'OP': [('optimism', '0x0d276fc14719f9292d5c1ea2198673d1f4269246', ('OP / USD',))],
}
WSTETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
USDC_ETH, WETH_ETH = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
MAX_LEGS, MAX_FLOWS = 16, 10


def q2(x):
    return Decimal(x).quantize(Decimal('0.01'))


def usd(x):
    d = Decimal(x)
    sign, d = ('-' if d < 0 else ''), abs(d)
    return sign + '$' + (f"{d.quantize(Decimal('1')):,}" if d >= 1000 else f"{d.quantize(Decimal('0.01')):,}")


def amount(raw, dec):
    d = Decimal(raw) / Decimal(10) ** dec
    return f"{d.quantize(Decimal('0.01')):,}" if abs(d) >= 1000 else f"{d.quantize(Decimal('0.000001')):,}"


def sig3(x):
    return format(float(x), '.3g') if x else '0'


def extra_text(h):
    try:
        text = bytes.fromhex(h[2:]).decode('utf-8', errors='replace')
    except (ValueError, TypeError):
        return None
    printable = ''.join(c for c in text if c.isprintable())
    return printable if len(printable) >= 4 and len(printable) >= 0.6 * len(text) else None


def raw_blocks_for(sample, chain):
    for c, data, path in raw_blocks(sample):
        if c == chain:
            yield data, path


def eth_in_sample(sample):
    """ETH/USD from V3 swaps in the USDC/WETH pools whose factory membership the pilot verified."""
    meta_path = ROOT / 'research/2026-09-05/followup/metadata.json'
    if not meta_path.exists():
        return {'available': False}
    meta = json.loads(meta_path.read_text()).get('ethereum', {})
    pools = [a for a, p in meta.get('pools', {}).items() if p.get('token0') == USDC_ETH and p.get('token1') == WETH_ETH]
    obs = []
    for data, _ in raw_blocks_for(sample, 'ethereum'):
        for r in data['receipts']:
            for l in r.get('logs', []):
                if l['address'].lower() not in pools:
                    continue
                d = decode(l)
                if d['family'] == 'V3Swap' and 'sqrtPriceX96' in d:
                    p = (Decimal(d['sqrtPriceX96']) / Decimal(2 ** 96)) ** 2 * Decimal(10) ** (6 - 18)
                    obs.append((hx(l['blockNumber']), hx(l['logIndex']), 1 / p, abs(int(d['amount0_raw']))))
    obs.sort()
    if not obs:
        return {'available': False, 'pools': pools}
    ps = [o[2] for o in obs]
    f = lambda d: str(Decimal(d).quantize(Decimal('0.0001')))
    return {'available': True, 'pools': pools, 'swaps': len(obs), 'median_usdc_per_weth': f(statistics.median(ps)),
            'first': f(ps[0]), 'last': f(ps[-1]), 'min': f(min(ps)), 'max': f(max(ps)),
            'usdc_volume': str(sum(o[3] for o in obs) / Decimal(10 ** 6)), 'note': 'marginal post-swap prices, not executable quotes'}


def load_prices(out, sample):
    path = out / 'prices.json'
    table, source = {}, {}
    if path.exists():
        p = json.loads(path.read_text())
        for k, v in p['assets'].items():
            if v.get('usd') is not None:
                table[k], source[k] = Decimal(v['usd']), v.get('source', 'prices.json')
        meta = {'file': str(path.relative_to(ROOT)), 'generated_at': p['generated_at']}
    else:
        ins = eth_in_sample(sample)
        if ins.get('available'):
            table['ETH'], source['ETH'] = Decimal(ins['median_usdc_per_weth']), 'offline fallback: in-sample median of V3 swaps in verified USDC/WETH pools'
        meta = {'file': None, 'fallback': 'prices.json missing: ETH from in-sample swaps, stablecoins at parity, other assets unpriced'}
    for k in STABLE_KEYS:
        if k not in table:
            table[k], source[k] = Decimal(1), 'assumed parity'
    return table, source, meta


def prices(args):
    out, sample = Path(args.out), Path(args.sample)
    manifest = json.loads((sample / 'manifest.json').read_text())
    end_ts = manifest['end_timestamp']
    pins = {c: json.loads((sample / (c + '_manifest.json')).read_text())['last_block'] for c in EXPLORERS if (sample / (c + '_manifest.json')).exists()}
    rpc = RPC(out, max_credits=args.max_credits, interval=.5)
    previous = json.loads((out / 'prices.json').read_text())['assets'] if (out / 'prices.json').exists() else {}
    result = {'generated_at': utc(), 'sample_end_utc': manifest['end_utc'], 'pinned_blocks': pins, 'assets': {},
              'method': 'Chainlink aggregator proxy latestRoundData() at the pinned block; description() must match the expected pair; '
                        'latest is used only when the pinned call errors. Stablecoins without a feed are valued at parity by scan. '
                        'Verified entries from an earlier run are reused.'}
    for key, candidates in FEEDS.items():
        if previous.get(key, {}).get('usd'):
            result['assets'][key] = previous[key]
            continue
        tried = []
        for chain, agg, expected in candidates:
            pin = hex(pins[chain])
            calls = [('eth_call', [{'to': agg, 'data': sel4(m)}, pin]) for m in ('description()', 'decimals()', 'latestRoundData()')]
            vals, used = rpc.batch(chain, calls, allow_errors=True), pin
            if any(isinstance(v, dict) for v in vals):
                vals, used = rpc.batch(chain, [(m, [q, 'latest']) for m, (q, _) in calls], allow_errors=True), 'latest'
            desc = decode_string(vals[0]) if isinstance(vals[0], str) else None
            dec = hx(vals[1]) if isinstance(vals[1], str) and len(vals[1]) == 66 else None
            entry = {'chain': chain, 'feed': agg, 'expected_description': list(expected), 'description_onchain': desc, 'decimals': dec,
                     'block_tag': used, 'usd': None, 'verified': False, 'raw': vals}
            rd = vals[2]
            if isinstance(rd, str) and len(rd) == 2 + 5 * 64 and dec is not None:
                words = [int(rd[2 + i * 64:2 + (i + 1) * 64], 16) for i in range(5)]
                answer, updated = signed(words[1]), words[3]
                entry.update(round_id=str(words[0]), answer_raw=str(answer), updated_at=utc(updated), age_seconds_at_sample_end=end_ts - updated,
                             verified=desc in expected)
                if entry['verified'] and answer > 0:
                    entry['usd'] = str(Decimal(answer) / Decimal(10) ** dec)
                    entry['source'] = 'Chainlink ' + desc + ' on ' + chain + ' at block ' + (str(hx(used)) if used != 'latest' else 'latest')
            tried.append(entry)
            if entry['usd']:
                break
        result['assets'][key] = dict(tried[-1], rejected_candidates=[{k: v for k, v in t.items() if k != 'raw'} for t in tried[:-1]])
        print(json.dumps({'asset': key, 'usd': result['assets'][key]['usd'], 'description': result['assets'][key]['description_onchain'],
                          'chain': result['assets'][key]['chain'], 'block_tag': result['assets'][key]['block_tag']}), flush=True)
    pin = hex(pins['ethereum'])
    v = previous['WSTETH']['raw'] if previous.get('WSTETH', {}).get('usd') else rpc.call('ethereum', 'eth_call', [{'to': WSTETH, 'data': sel4('stEthPerToken()')}, pin], allow_errors=True)
    used = previous['WSTETH']['block_tag'] if previous.get('WSTETH', {}).get('usd') else pin
    if isinstance(v, dict):
        v, used = rpc.call('ethereum', 'eth_call', [{'to': WSTETH, 'data': sel4('stEthPerToken()')}, 'latest'], allow_errors=True), 'latest'
    steth = result['assets'].get('STETH', {}).get('usd')
    entry = {'chain': 'ethereum', 'contract': WSTETH, 'call': 'stEthPerToken()', 'block_tag': used, 'usd': None, 'verified': False, 'raw': v}
    if isinstance(v, str) and len(v) == 66 and steth:
        ratio = Decimal(hx(v)) / Decimal(10 ** 18)
        entry.update(ratio_steth_per_wsteth=str(ratio), usd=str(Decimal(steth) * ratio), verified=True,
                     source='STETH / USD feed times wstETH stEthPerToken() at block ' + (str(hx(used)) if used != 'latest' else 'latest'))
    result['assets']['WSTETH'] = entry
    result['in_sample'] = eth_in_sample(sample)
    result['assumed_parity'] = sorted({s for reg in ASSETS.values() for s, _, k in reg.values() if k == 'USD'})
    result['estimated_credits'] = rpc.credits
    save(out / 'prices.json', result)
    print(json.dumps({'priced': sorted(k for k, v in result['assets'].items() if v['usd']), 'unverified': sorted(k for k, v in result['assets'].items() if not v['usd']),
                      'in_sample_eth': result['in_sample'].get('median_usdc_per_weth'), 'credits': rpc.credits}, indent=2))


def flows_for(chain, r, row, prices):
    reg, weth = ASSETS.get(chain, {}), WETH.get(chain)
    legs, unpriced, unpriced_max, families = [], collections.Counter(), {}, collections.Counter()
    if row['value_wei']:
        legs.append({'log_index': -1, 'kind': 'native', 'asset': 'native', 'symbol': NATIVE[chain], 'decimals': 18, 'key': NATIVE_KEY[chain],
                     'sender': row['sender'], 'recipient': row['to'] or row['contract_created'], 'amount_raw': row['value_wei']})
    for l in r.get('logs', []):
        d = decode(l)
        if chain == 'polygon' and is_polygon_fee_log(l):
            d = {'family': 'Polygon_native_fee_log'}
        families[d['family']] += 1
        ts, data, a = l.get('topics') or [], l.get('data', '0x'), l['address'].lower()
        if d['family'] == 'ERC20_Transfer_shape':
            if a in reg:
                sym, dec, key = reg[a]
                legs.append({'log_index': hx(l['logIndex']), 'kind': 'erc20', 'asset': a, 'symbol': sym, 'decimals': dec, 'key': key,
                             'sender': d['sender'], 'recipient': d['recipient'], 'amount_raw': int(d['amount_raw'])})
            else:
                unpriced[a] += 1
                unpriced_max[a] = max(unpriced_max.get(a, 0), int(d['amount_raw']))
        elif a == weth and len(ts) == 2 and len(data) == 66 and ts[0] in (WETH_DEPOSIT, WETH_WITHDRAWAL):
            sym, dec, key = reg[a]
            wrap = ts[0] == WETH_DEPOSIT
            legs.append({'log_index': hx(l['logIndex']), 'kind': 'wrap' if wrap else 'unwrap', 'asset': a, 'symbol': sym, 'decimals': dec, 'key': key,
                         'sender': None if wrap else topic_address(ts[1]), 'recipient': topic_address(ts[1]) if wrap else None, 'amount_raw': int(data, 16)})
    net = collections.defaultdict(lambda: [0, Decimal(0)])
    gross, priced_legs, no_price = Decimal(0), 0, collections.Counter()
    for leg in legs:
        price = prices.get(leg['key'])
        if price is None:
            leg['usd'] = None
            no_price[leg['symbol']] += 1
        else:
            leg['usd'] = Decimal(leg['amount_raw']) / Decimal(10) ** leg['decimals'] * price
            gross += leg['usd']
            priced_legs += 1
        for addr, sign in ((leg['sender'], -1), (leg['recipient'], 1)):
            if addr is not None:
                e = net[(addr, leg['asset'])]
                e[0] += sign * leg['amount_raw']
                if leg['usd'] is not None:
                    e[1] += sign * leg['usd']
    largest = None
    if net:
        (addr, asset), (raw_net, usd_net) = max(net.items(), key=lambda kv: (abs(kv[1][1]), kv[0]))
        meta = next(l for l in legs if l['asset'] == asset)
        largest = {'address': addr, 'asset': asset, 'symbol': meta['symbol'], 'decimals': meta['decimals'], 'net_raw': raw_net, 'net_usd': usd_net}
    native_usd = legs[0]['usd'] if legs and legs[0]['kind'] == 'native' and legs[0]['usd'] is not None else Decimal(0)
    touched = {row['sender']} | {x for x in (row['to'], row['contract_created']) if x} | {l[k] for l in legs for k in ('sender', 'recipient') if l[k]}
    return {'legs': legs, 'net': dict(net), 'largest': largest, 'position_change_usd': abs(largest['net_usd']) if largest else Decimal(0),
            'gross_volume_usd': gross, 'native_value_usd': native_usd, 'priced_legs': priced_legs, 'registry_legs_without_price': dict(no_price),
            'unpriced_transfers': dict(unpriced), 'unpriced_max_raw': unpriced_max, 'erc20_transfer_logs': families['ERC20_Transfer_shape'],
            'families': dict(families), 'has_swap': any(f in families for f in SWAP_FAMILIES),
            'distinct_recipients': len({l['recipient'] for l in legs if l['recipient']}),
            'mint_burn_legs': sum(ZERO in (l['sender'], l['recipient']) for l in legs),
            'assets': sorted({l['symbol'] for l in legs if l['usd'] is not None}), 'touched': touched}


def shape(row):
    if row['has_swap']:
        return 'swap'
    if row['mint_burn_legs']:
        return 'mint_or_burn'
    if row['distinct_recipients'] >= 5:
        return 'batch_payout'
    if row['priced_legs'] <= 2 and row['log_count'] <= 3:
        return 'plain_transfer'
    return 'contract_interaction'


def campaign_key(row):
    lg = row['largest']
    return '|'.join([row['to'] or 'create', row['selector'], lg['symbol'] if lg else '-', sig3(row['position_change_usd'])])


def chain_stats(chain, rs, thr, top, controls):
    user = [r for r in rs if not r['system']]
    priced = [r for r in user if r['position_change_usd'] > 0]
    big = [r for r in user if r['position_change_usd'] >= thr]
    st = {m: describe([float(r[m]) for r in priced]) for m in METRICS} if len(priced) >= 2 else {}
    erc20_total = sum(r['erc20_transfer_logs'] for r in user)
    erc20_priced = sum(sum(1 for l in r['legs'] if l['kind'] == 'erc20') for r in user)
    camps = collections.defaultdict(list)
    for r in big:
        camps[r['campaign_key']].append(r)
    pattern_count = collections.Counter(r['campaign_key'] for r in user)
    by_asset, by_shape, actors = collections.defaultdict(lambda: [0, Decimal(0)]), collections.Counter(), collections.defaultdict(lambda: {'n': 0, 'usd': Decimal(0), 'roles': collections.Counter(), 'hashes': []})
    for r in big:
        by_asset[r['largest']['symbol']][0] += 1
        by_asset[r['largest']['symbol']][1] += r['position_change_usd']
        by_shape[r['shape']] += 1
        for a, role in ((r['sender'], 'tx sender'), (r['largest']['address'], 'largest position')):
            if a == ZERO:
                continue
            x = actors[a]
            x['n'] += 1 if role == 'tx sender' or a != r['sender'] else 0
            x['roles'][role] += 1
            x['usd'] += r['position_change_usd'] if role == 'largest position' or a != r['largest']['address'] else 0
            if r['transaction_hash'] not in x['hashes']:
                x['hashes'].append(r['transaction_hash'])
    unpriced = collections.Counter()
    unpriced_max = {}
    for r in user:
        for a, n in r['unpriced_transfers'].items():
            unpriced[a] += n
            unpriced_max[a] = max(unpriced_max.get(a, 0), r['unpriced_max_raw'][a])
    no_price = collections.Counter()
    for r in user:
        no_price.update(r['registry_legs_without_price'])
    wnet = collections.defaultdict(lambda: [Decimal(0), Decimal(0)])  # (address, symbol) -> [net usd, gross through usd]
    for r in user:
        symof = {l['asset']: l['symbol'] for l in r['legs']}
        for (a, asset), (raw, u) in r['net'].items():
            wnet[(a, symof[asset])][0] += u
        for l in r['legs']:
            if l['usd'] is not None:
                for a in (l['sender'], l['recipient']):
                    if a:
                        wnet[(a, l['symbol'])][1] += abs(l['usd'])
    window_net = {a: {} for a in set(k[0] for k in wnet)}
    for (a, s), (n, g) in wnet.items():
        window_net[a][s] = {'net_usd': str(q2(n)), 'gross_through_usd': str(q2(g))}
    stats = {'transactions': len(rs), 'system_transactions': len(rs) - len(user), 'user_transactions': len(user),
             'with_priced_flow': len(priced), 'erc20_transfer_logs': erc20_total, 'erc20_transfer_logs_priced': erc20_priced,
             'erc20_coverage_pct': round(100 * erc20_priced / erc20_total, 2) if erc20_total else None,
             'metrics': {m: {k: v for k, v in s.items() if k != '_sorted'} for m, s in st.items()},
             'above_threshold': len(big), 'above_100k': sum(r['position_change_usd'] >= 100000 for r in user),
             'above_1m': sum(r['position_change_usd'] >= 1000000 for r in user),
             'sum_position_change_above_threshold_usd': str(q2(sum((r['position_change_usd'] for r in big), Decimal(0)))),
             'sum_gross_volume_all_user_usd': str(q2(sum((r['gross_volume_usd'] for r in user), Decimal(0)))),
             'distinct_patterns_above_threshold': len(camps),
             'by_asset': {k: {'transactions': v[0], 'sum_usd': str(q2(v[1]))} for k, v in sorted(by_asset.items(), key=lambda kv: -kv[1][1])},
             'by_shape': dict(by_shape.most_common()),
             'campaigns': [{'key': k, 'to': k.split('|')[0], 'selector': k.split('|')[1], 'asset': k.split('|')[2], 'typical_usd': k.split('|')[3],
                            'transactions': len(v), 'senders': len({r['sender'] for r in v}), 'share_of_above_threshold_pct': round(100 * len(v) / len(big), 1),
                            'blocks': [min(r['block_number'] for r in v), max(r['block_number'] for r in v)],
                            'failed': sum(not r['status_ok'] for r in v), 'shape': collections.Counter(r['shape'] for r in v).most_common(1)[0][0],
                            'examples': [r['transaction_hash'] for r in v[:3]]}
                           for k, v in sorted(camps.items(), key=lambda kv: (-len(kv[1]), kv[0])) if len(v) >= 2][:10],
             'repeat_actors': [{'address': a, 'transactions_above_threshold': len(x['hashes']), 'roles': dict(x['roles']),
                                'sum_position_change_usd': str(q2(x['usd'])), 'examples': x['hashes'][:3]}
                               for a, x in sorted(actors.items(), key=lambda kv: (-len(kv[1]['hashes']), kv[0])) if len(x['hashes']) >= 3][:8],
             'unpriced_tokens_top': [{'token': a, 'transfers': n, 'largest_raw': str(unpriced_max[a])} for a, n in unpriced.most_common(8)],
             'window_net_top': [{'address': a, 'symbol': sym, 'net_usd': str(q2(n)), 'gross_through_usd': str(q2(g))}
                                for (a, sym), (n, g) in sorted(wnet.items(), key=lambda kv: (-abs(kv[1][0]), kv[0])) if a != ZERO][:8],
             'window_gross_through_top': [{'address': a, 'symbol': sym, 'net_usd': str(q2(n)), 'gross_through_usd': str(q2(g)),
                                           'net_over_gross_pct': round(float(100 * abs(n) / g), 2) if g else None}
                                          for (a, sym), (n, g) in sorted(wnet.items(), key=lambda kv: (-kv[1][1], kv[0])) if a != ZERO][:8],
             'registry_legs_without_price': dict(no_price)}
    picks, skipped = {}, {}
    for m in METRICS:
        ranked = sorted([r for r in user if r[m] >= thr], key=lambda r: (-r[m], r['block_number'], r['transaction_index']))
        if not ranked:
            skipped[m] = 'no user transaction reaches the threshold on this metric'
            continue
        seen, rank = set(), 0
        for r in ranked:
            if r['campaign_key'] in seen:
                continue
            seen.add(r['campaign_key'])
            rank += 1
            picks.setdefault(r['transaction_hash'], {'row': r, 'reasons': []})['reasons'].append(
                {'metric': m, 'rank': rank, 'value_usd': str(q2(r[m])), 'same_pattern_in_window': pattern_count[r['campaign_key']]})
            if rank >= top:
                break
    pool = sorted([r for r in big if r['transaction_hash'] not in picks], key=lambda r: hashlib.sha256(r['transaction_hash'].encode()).hexdigest())
    used, n = {p['row']['campaign_key'] for p in picks.values()}, 0
    for r in pool:
        if r['campaign_key'] in used or n >= controls:
            continue
        used.add(r['campaign_key'])
        n += 1
        picks[r['transaction_hash']] = {'row': r, 'reasons': [{'metric': 'control', 'rank': n, 'value_usd': str(q2(r['position_change_usd'])),
                                                              'same_pattern_in_window': pattern_count[r['campaign_key']],
                                                              'note': 'deterministic hash sample from the population above the threshold, one per pattern, after the ranked picks'}]}
    stats['skipped_metrics'] = skipped
    return stats, picks, st, pattern_count, window_net


def build_packet(row, reasons, block, receipt, tx, st, rows_in_chain, touch, pattern_count, prices, price_source, thr, window_net):
    chain, unit = row['chain'], NATIVE[row['chain']]
    events = [event_view(l, chain) for l in receipt.get('logs', [])]
    emitters = collections.Counter(e['emitter'] for e in events)
    unknown_topics = collections.Counter((e['emitter'], e['topic0']) for e in events if e['family'] == 'unknown')
    same_sender = [hx(t['transactionIndex']) for t in block['transactions'] if t['from'].lower() == row['sender'] and t['hash'] != tx['hash']]
    miner = (block.get('miner') or '').lower()
    lg = row['largest']
    roles = lambda a: [n for n, ok in (('tx sender', a == row['sender']), ('tx destination', a == row['to']), ('created contract', a == row['contract_created']),
                                        ('zero address', a == ZERO), ('block miner', a == miner), ('WETH contract', a == WETH.get(chain))) if ok]
    flows = sorted(row['net'].items(), key=lambda kv: (-abs(kv[1][1]), kv[0]))
    meta = {l['asset']: (l['symbol'], l['decimals']) for l in row['legs']}
    net_flows = [{'address': a, 'roles': roles(a), 'asset': asset, 'symbol': meta[asset][0], 'net_amount': amount(raw, meta[asset][1]),
                  'net_usd': str(q2(u)) if any(l['asset'] == asset and l['usd'] is not None for l in row['legs']) else None}
                 for (a, asset), (raw, u) in flows[:MAX_FLOWS]]
    legs = [{'log_index': l['log_index'] if l['log_index'] >= 0 else None, 'kind': l['kind'], 'symbol': l['symbol'], 'asset': l['asset'],
             'sender': l['sender'], 'recipient': l['recipient'], 'amount': amount(l['amount_raw'], l['decimals']),
             'usd': str(q2(l['usd'])) if l['usd'] is not None else None} for l in row['legs'][:MAX_LEGS]]
    by_sender = [r for r in rows_in_chain.values() if r['sender'] == row['sender'] and not r['system']]
    counterparty = lg['address'] if lg and lg['address'] != row['sender'] else None
    if lg and counterparty is None:
        big_leg = max((l for l in row['legs'] if l['usd'] is not None), key=lambda l: l['usd'], default=None)
        if big_leg:
            counterparty = big_leg['recipient'] if big_leg['sender'] == row['sender'] else big_leg['sender']
    cp_hashes = touch.get(counterparty, set()) if counterparty else set()
    idx0 = next((r for r in rows_in_chain.values() if r['block_number'] == row['block_number'] and r['transaction_index'] == 0), None)
    fee_usd = Decimal(row['fee_paid_wei']) / Decimal(10 ** 18) * prices[NATIVE_KEY[chain]] if NATIVE_KEY[chain] in prices else None
    facts = [{'id': 'F1', 'metric': 'position_change_usd', 'value': str(q2(row['position_change_usd'])), 'unit': 'USD',
              'detail': {'address': lg['address'], 'roles': roles(lg['address']), 'asset': lg['asset'], 'symbol': lg['symbol'],
                         'net_amount': amount(lg['net_raw'], lg['decimals']), 'direction': 'received' if lg['net_raw'] > 0 else 'sent'} if lg else None},
             {'id': 'F2', 'metric': 'gross_volume_usd', 'value': str(q2(row['gross_volume_usd'])), 'unit': 'USD', 'priced_legs': row['priced_legs']},
             {'id': 'F3', 'metric': 'native_value', 'value': native(row['value_wei'], unit), 'usd': str(q2(row['native_value_usd']))},
             {'id': 'F4', 'metric': 'unpriced_erc20_transfers', 'value': sum(row['unpriced_transfers'].values()), 'tokens': len(row['unpriced_transfers']),
              'registry_legs_without_price': row['registry_legs_without_price']},
             {'id': 'F5', 'metric': 'status', 'value': 'success' if row['status_ok'] else 'failed'},
             {'id': 'F6', 'metric': 'log_count', 'value': row['log_count']},
             {'id': 'F7', 'metric': 'position_in_block', 'value': str(row['transaction_index']) + '/' + str(len(block['transactions']))},
             {'id': 'F8', 'metric': 'fee_paid', 'value': native(row['fee_paid_wei'], unit), 'usd': str(q2(fee_usd)) if fee_usd is not None else None},
             {'id': 'F9', 'metric': 'distinct_transfer_recipients', 'value': row['distinct_recipients']},
             {'id': 'F10', 'metric': 'same_pattern_in_window', 'value': pattern_count[row['campaign_key']],
              'pattern': 'destination, selector, asset of the largest position, amount to three significant figures'},
             {'id': 'F11', 'metric': 'shape', 'value': row['shape']}]
    return {'episode_id': chain + ':' + row['block_hash'] + ':' + row['transaction_hash'], 'chain': chain,
            'explorer_tx': EXPLORERS[chain] + '/tx/' + row['transaction_hash'], 'selection_reasons': reasons,
            'baseline_position': {m: position(st[m], float(row[m])) for m in METRICS if m in st},
            'baseline_population': 'user transactions with any priced flow on this chain in the window',
            'transaction': {k: row[k] for k in ['block_number', 'timestamp', 'transaction_hash', 'transaction_index', 'type', 'sender', 'to',
                                                'contract_created', 'nonce', 'selector', 'calldata_bytes', 'status_ok', 'gas_limit', 'gas_used',
                                                'log_count', 'raw_file']}
            | {'block_utc': utc(row['timestamp']), 'calldata_prefix': tx.get('input', '0x')[:10 + 128],
               'effective_gas_price_gwei': gwei(row['effective_gas_price_wei']), 'priority_fee_gwei': gwei(row['priority_fee_wei']),
               'same_sender_other_indices_in_block': same_sender,
               'authorization_list_len': len(tx.get('authorizationList') or []) if tx.get('type') == '0x4' else None},
            'block': {'miner': miner, 'extra_data_text': extra_text(block.get('extraData', '0x')), 'transactions': len(block['transactions']),
                      'gas_utilization': round(hx(block['gasUsed']) / hx(block['gasLimit']), 4),
                      'index0': None if idx0 is None or idx0['transaction_hash'] == row['transaction_hash'] else
                      {'transaction_hash': idx0['transaction_hash'], 'sender': idx0['sender'], 'to': idx0['to'], 'selector': idx0['selector'],
                       'native_value': native(idx0['value_wei'], unit), 'position_change_usd': str(q2(idx0['position_change_usd'])),
                       'largest_symbol': idx0['largest']['symbol'] if idx0['largest'] else None, 'shape': idx0['shape']}},
            'facts': facts, 'prices_used': {l['key']: {'usd': str(prices[l['key']]), 'source': price_source[l['key']]} for l in row['legs'] if l['key'] in prices},
            'net_flows': net_flows, 'net_flows_truncated': max(0, len(flows) - MAX_FLOWS),
            'legs': legs, 'legs_truncated': max(0, len(row['legs']) - MAX_LEGS),
            'unpriced': [{'token': a, 'transfers': n, 'largest_raw': str(row['unpriced_max_raw'][a])}
                         for a, n in sorted(row['unpriced_transfers'].items(), key=lambda kv: (-kv[1], kv[0]))[:6]],
            'events': {'families': row['families'], 'top_emitters': emitters.most_common(10),
                       'unknown_topics': [{'emitter': a, 'topic0': t, 'count': n} for (a, t), n in unknown_topics.most_common(8)],
                       'sample': events[:SAMPLE_EVENTS], 'truncated': max(0, len(events) - SAMPLE_EVENTS)},
            'sender_window': {'transactions': len(by_sender), 'above_threshold': sum(r['position_change_usd'] >= thr for r in by_sender),
                              'sum_position_change_usd': str(q2(sum((r['position_change_usd'] for r in by_sender), Decimal(0)))),
                              'distinct_destinations': len({r['to'] for r in by_sender}), 'failed': sum(not r['status_ok'] for r in by_sender)},
            'counterparty_window': None if not counterparty else
            {'address': counterparty, 'roles': roles(counterparty), 'transactions_touching': len(cp_hashes),
             'above_threshold_touching': sum(rows_in_chain[h]['position_change_usd'] >= thr for h in cp_hashes if h in rows_in_chain),
             'as_tx_sender': sum(rows_in_chain[h]['sender'] == counterparty for h in cp_hashes if h in rows_in_chain)},
            'window_net': {a: window_net.get(a, {}) for a in dict.fromkeys(x for x in [row['sender'], row['to'], lg['address'] if lg else None, counterparty] if x and x != ZERO)},
            'window_net_definition': 'net USD change of each (address, asset) summed over every user transaction in the window, with the gross USD that passed through',
            'missing': ['internal calls and native value moved by contracts (only top-level value is counted)',
                        'prices for tokens outside the registry (listed under unpriced)', 'revert reason', 'state before/after',
                        'verified contract identity (see context.json for code/symbol lookups)']}


def scan(args):
    sample, out = Path(args.sample), Path(args.out)
    thr = Decimal(args.threshold)
    prices, price_source, price_meta = load_prices(out, sample)
    rows, touch = collections.defaultdict(dict), collections.defaultdict(lambda: collections.defaultdict(set))
    for chain, data, path in raw_blocks(sample):
        recs = {r['transactionHash']: r for r in data['receipts']}
        for row in rows_for(chain, data, path):
            row.update(flows_for(chain, recs[row['transaction_hash']], row, prices))
            row['shape'], row['campaign_key'] = shape(row), campaign_key(row)
            rows[chain][row['transaction_hash']] = row
            for a in row['touched']:
                touch[chain][a].add(row['transaction_hash'])
    stats, selected = {}, {}
    for chain, rs in rows.items():
        stats[chain], picks, st, pattern_count, window_net = chain_stats(chain, list(rs.values()), thr, args.top, args.controls)
        selected[chain] = (picks, st, pattern_count, window_net)
    need = collections.defaultdict(list)
    for chain, (picks, _, _, _) in selected.items():
        for h, p in picks.items():
            need[p['row']['raw_file']].append(h)
    packets = []
    for chain, data, path in raw_blocks(sample):
        rel = str(path.relative_to(ROOT))
        if rel not in need:
            continue
        picks, st, pattern_count, window_net = selected[chain]
        txs = {t['hash']: t for t in data['block']['transactions']}
        recs = {r['transactionHash']: r for r in data['receipts']}
        for h in need[rel]:
            packets.append(build_packet(picks[h]['row'], picks[h]['reasons'], data['block'], recs[h], txs[h], st, rows[chain], touch[chain],
                                        pattern_count, prices, price_source, thr, window_net))
    order = {c: i for i, c in enumerate(EXPLORERS)}
    packets.sort(key=lambda p: (order[p['chain']], p['transaction']['block_number'], p['transaction']['transaction_index']))
    save(out / 'stats.json', {'generated_at': utc(), 'sample': str(sample.relative_to(ROOT)), 'threshold_usd': str(thr), 'top_per_metric': args.top,
                              'controls_per_chain': args.controls, 'metrics': METRICS,
                              'metric_definitions': {'position_change_usd': 'largest absolute net USD change of any single (address, asset) pair inside the transaction; '
                                                                            'counts top-level native value, registry ERC-20 transfers and WETH wrap/unwrap',
                                                     'gross_volume_usd': 'sum of all priced legs; routed and flash-loan legs count every time they move',
                                                     'native_value_usd': 'top-level transaction value at the native price'},
                              'prices_used': {k: {'usd': str(v), 'source': price_source[k]} for k, v in sorted(prices.items())}, 'price_meta': price_meta,
                              'registry': {c: {a: {'label': s, 'decimals': d, 'price_key': k} for a, (s, d, k) in reg.items()} for c, reg in ASSETS.items()},
                              'system_types_excluded': {k: sorted(v) for k, v in SYSTEM_TYPES.items()}, 'chains': stats})
    save(out / 'packets.json', packets)
    print(json.dumps({c: {'user_transactions': stats[c]['user_transactions'], 'above_threshold': stats[c]['above_threshold'],
                          'patterns': stats[c]['distinct_patterns_above_threshold'], 'selected': len(selected[c][0])} for c in stats}
                     | {'packets': len(packets), 'prices': price_meta}, indent=2))


def resolve(args):
    out = Path(args.out)
    packets = json.loads((out / 'packets.json').read_text())
    stats = json.loads((out / 'stats.json').read_text())
    ctx_path = out / 'context.json'
    ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {'tokens': {}, 'code': {}, 'asof': {}}
    rpc = RPC(out, max_credits=args.max_credits, interval=.5)
    for chain in EXPLORERS:
        ps = [p for p in packets if p['chain'] == chain]
        if not ps:
            continue
        tokens, addresses = collections.Counter(), set()
        for p in ps:
            for l in p['legs']:
                if l['asset'] != 'native':
                    tokens[l['asset']] += 1
            for u in p['unpriced']:
                tokens[u['token']] += u['transfers']
            addresses.update(a for a in [p['transaction']['to'], p['transaction']['contract_created']] if a)
            addresses.update(f['address'] for f in p['net_flows'][:3] if f['address'] != ZERO)
            if p['counterparty_window']:
                addresses.add(p['counterparty_window']['address'])
        for u in stats['chains'].get(chain, {}).get('unpriced_tokens_top', [])[:5]:
            tokens[u['token']] += u['transfers']
        tokens = [t for t, _ in tokens.most_common(args.max_tokens)]
        pin = hex(max(p['transaction']['block_number'] for p in ps))
        ctx['asof'].setdefault(chain, {'pinned_block': hx(pin), 'fallback': 'latest when the pinned call errors', 'observed_at': utc()})
        tok = ctx['tokens'].setdefault(chain, {})
        for t in [t for t in tokens if t not in tok]:
            calls = [('eth_call', [{'to': t, 'data': sel4('symbol()')}, pin]), ('eth_call', [{'to': t, 'data': sel4('decimals()')}, pin])]
            vals, used = rpc.batch(chain, calls, allow_errors=True), pin
            if any(isinstance(v, dict) for v in vals):
                vals, used = rpc.batch(chain, [(m, [q, 'latest']) for m, (q, _) in calls], allow_errors=True), 'latest'
            entry = {'symbol_untrusted': decode_string(vals[0]) if isinstance(vals[0], str) else None,
                     'decimals': hx(vals[1]) if isinstance(vals[1], str) and len(vals[1]) == 66 else None, 'block_tag': used, 'raw': vals}
            reg = ASSETS.get(chain, {}).get(t)
            if reg:
                entry.update(registry_label=reg[0], registry_decimals=reg[1],
                             symbol_matches_registry=(entry['symbol_untrusted'] or '').lower() == reg[0].lower(),
                             decimals_match_registry=entry['decimals'] == reg[1])
            tok[t] = entry
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
                    code[a] = {'code_bytes': (len(v) - 2) // 2, 'is_contract': len(v) > 2, 'minimal_proxy_target': ('0x' + m.group(1)) if m else None}
                else:
                    code[a] = {'error': str(v)[:200]}
        save(ctx_path, ctx)
        print(json.dumps({'chain': chain, 'tokens': len(tok), 'code_lookups': len(code), 'credits_so_far': rpc.credits}), flush=True)
    mismatches = [(c, a, v['registry_label'], v['symbol_untrusted']) for c, toks in ctx['tokens'].items() for a, v in toks.items()
                  if 'registry_label' in v and not (v['symbol_matches_registry'] and v['decimals_match_registry'])]
    print(json.dumps({'registry_mismatches': mismatches}))


def sym(chain, ctx, asset, label):
    info = ctx.get('tokens', {}).get(chain, {}).get(asset, {})
    s = info.get('symbol_untrusted')
    return label if not s or s.lower() == label.lower() else label + ' (onchain symbol ' + s + ')'


def code_desc(chain, ctx, a):
    code = ctx.get('code', {}).get(chain, {})
    if a not in code:
        return 'of unknown code status'
    if code[a].get('is_contract'):
        return 'a contract' + (', an EIP-1167 minimal proxy to ' + addr_link(chain, code[a]['minimal_proxy_target']) if code[a].get('minimal_proxy_target') else '')
    return 'an EOA' if 'error' not in code[a] else 'of unknown code status'


def render(args):
    out = Path(args.out)
    packets = json.loads((out / 'packets.json').read_text())
    stats = json.loads((out / 'stats.json').read_text())
    prices = json.loads((out / 'prices.json').read_text()) if (out / 'prices.json').exists() else None
    ctx = json.loads((out / 'context.json').read_text()) if (out / 'context.json').exists() else {}
    notes = parse_notes(out / 'qual_notes.md')
    manifest = json.loads((RUN / 'manifest.json').read_text())
    thr = Decimal(stats['threshold_usd'])
    L = ['# Large amounts: a quant scan in USD followed by an LLM investigation\n']
    L.append('Second iteration of the research loop over the saved five-chain sample. The deterministic step values every top-level native transfer, '
             'every ERC-20 transfer of a registry token and every WETH wrap or unwrap in USD, nets them per address and asset inside each transaction, '
             'and treats a user transaction as large when some single address changed a single asset position by at least ' + usd(thr) + '. '
             'It ranks the population by three metrics, selects the top ' + str(stats['top_per_metric']) + ' per metric per chain with at most one '
             'transaction per repeated pattern, adds ' + str(stats['controls_per_chain']) + ' hash-sampled controls per chain, and hands evidence packets '
             'to the qualitative step. Every number below is computed by `scripts/amount_outliers.py`; the prose under each transaction is the LLM\'s '
             'interpretation and carries a confidence. Identity claims that rest on model memory rather than an onchain check are marked as such.\n')
    L.append('Sample: ' + manifest['start_utc'] + ' to ' + manifest['end_utc'] + ' (exclusive). Chain-generated transactions (Arbitrum types 0x64-0x6a, '
             'OP Stack type 0x7e) are excluded; none of them carries value in this window. Metrics: **largest position change** is the largest absolute net '
             'USD change of one (address, asset) pair within the transaction, so a fair swap of $50k USDC into WETH scores $50k and a flash loan that is '
             'repaid scores zero; **gross priced volume** sums every priced leg, so routed and borrowed value counts each time it moves; **native value** '
             'is the top-level transaction value. Internal native transfers made by contracts are invisible in receipts and are not counted.\n')
    L.append('## Prices used\n')
    L.append('| Price key | USD | Source |')
    L.append('|---|---:|---|')
    for k, v in stats['prices_used'].items():
        L.append('| ' + k + ' | ' + f"{Decimal(v['usd']):,.4f}" + ' | ' + v['source'] + ' |')
    L.append('')
    if prices:
        ages = [(k, v.get('age_seconds_at_sample_end')) for k, v in prices['assets'].items() if v.get('usd') and v.get('age_seconds_at_sample_end') is not None]
        bad = [k for k, v in prices['assets'].items() if not v.get('usd')]
        ins = prices.get('in_sample', {})
        L.append('Feed answers are the latest round at each chain\'s last sampled block; ages at the sample end run from ' +
                 f"{min(a for _, a in ages):,}" + ' to ' + f"{max(a for _, a in ages):,}" + ' seconds. ' +
                 ('Feeds that failed verification and were not used: ' + ', '.join(bad) + '. ' if bad else '') +
                 'Assumed parity for ' + ', '.join(prices.get('assumed_parity', [])) + '. ' +
                 (('In-sample cross-check: ' + str(ins['swaps']) + ' V3 swaps in the two factory-verified USDC/WETH pools on Ethereum gave a median of ' +
                   ins['median_usdc_per_weth'] + ' USDC per WETH (range ' + ins['min'] + ' to ' + ins['max'] + ') against the feed\'s ' +
                   f"{Decimal(prices['assets']['ETH']['usd']):,.2f}" + '.') if ins.get('available') and prices['assets'].get('ETH', {}).get('usd') else '') + '\n')
    L.append('## Chain baselines\n')
    L.append('| Chain | User txs | With priced flow | ERC-20 legs priced | ≥ ' + usd(thr) + ' | ≥ $100k | ≥ $1M | Patterns ≥ ' + usd(thr) +
             ' | Sum of largest changes ≥ ' + usd(thr) + ' | Median largest change (priced txs) | P99 | Max |')
    L.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')
    for chain in EXPLORERS:
        s = stats['chains'].get(chain)
        if not s:
            continue
        m = s['metrics'].get('position_change_usd', {})
        L.append('| ' + chain + ' | ' + f"{s['user_transactions']:,} | {s['with_priced_flow']:,} | " + (str(s['erc20_coverage_pct']) + '%' if s['erc20_coverage_pct'] is not None else '—') +
                 f" | {s['above_threshold']:,} | {s['above_100k']:,} | {s['above_1m']:,} | {s['distinct_patterns_above_threshold']:,} | " +
                 usd(s['sum_position_change_above_threshold_usd']) + ' | ' + (usd(m['p50']) if m else '—') + ' | ' + (usd(m['p99']) if m else '—') + ' | ' + (usd(m['max']) if m else '—') + ' |')
    L.append('')
    L.append('"ERC-20 legs priced" is the share of ERC-20 transfer logs on registry tokens; the rest are unpriced and listed per chain below. '
             '"Patterns" counts distinct (destination, selector, asset, amount to three significant figures) combinations among the transactions above the threshold, '
             'so a bot repeating one move contributes one pattern.\n')
    if 'synthesis' in notes:
        L.append('## Cross-cutting observations (LLM)\n')
        L.append(notes['synthesis']['body'] + '\n')
    counter, conf_counts = 0, collections.Counter()
    for chain in EXPLORERS:
        ps = [p for p in packets if p['chain'] == chain]
        s = stats['chains'].get(chain)
        if not s:
            continue
        L.append('## ' + chain.capitalize() + '\n')
        L.append('### Population above ' + usd(thr) + '\n')
        if s['above_threshold']:
            L.append('| Asset of largest position | Transactions | Sum of largest changes |')
            L.append('|---|---:|---:|')
            for a, v in s['by_asset'].items():
                L.append('| ' + sym(chain, ctx, next((addr for addr, x in stats['registry'][chain].items() if x['label'] == a), a), a) + f" | {v['transactions']:,} | " + usd(v['sum_usd']) + ' |')
            L.append('')
            L.append('Shapes (heuristic: swap events present; mint or burn leg; five or more recipients; at most two priced legs and three logs; otherwise contract interaction): ' +
                     ', '.join(f'{k} ×{v}' for k, v in s['by_shape'].items()) + '.\n')
        else:
            L.append('No user transaction reaches the threshold on this chain.\n')
        if s['campaigns']:
            L.append('Repeated patterns (two or more transactions above the threshold with the same destination, selector, asset and amount to three significant figures):\n')
            L.append('| Destination | Selector | Asset | Typical amount | Txs | Senders | Failed | Share of population | Blocks | Shape | Examples |')
            L.append('|---|---|---|---:|---:|---:|---:|---:|---|---|---|')
            for c in s['campaigns']:
                L.append('| ' + (addr_link(chain, c['to']) if c['to'] != 'create' else 'creation') + ' | `' + c['selector'] + '` | ' + c['asset'] + ' | ' + usd(c['typical_usd']) +
                         f" | {c['transactions']} | {c['senders']} | {c['failed']} | {c['share_of_above_threshold_pct']}% | {c['blocks'][0]:,}-{c['blocks'][1]:,} | {c['shape']} | " +
                         ' '.join(tx_link(chain, h) for h in c['examples']) + ' |')
            L.append('')
        if s['repeat_actors']:
            L.append('Addresses in three or more transactions above the threshold (as transaction sender or as the address with the largest position change):\n')
            L.append('| Address | Txs above threshold | Roles | Sum of largest changes | Examples |')
            L.append('|---|---:|---|---:|---|')
            for a in s['repeat_actors']:
                L.append('| ' + addr_link(chain, a['address']) + f" | {a['transactions_above_threshold']} | " + ', '.join(f'{k} ×{v}' for k, v in a['roles'].items()) +
                         ' | ' + usd(a['sum_position_change_usd']) + ' | ' + ' '.join(tx_link(chain, h) for h in a['examples']) + ' |')
            L.append('')
        if s.get('window_gross_through_top'):
            L.append('Window-level flows: the addresses with the most priced value passing through them over the two minutes, with their net change. '
                     'A small net over a large gross marks value that cycles rather than moves:\n')
            L.append('| Address | Asset | Gross through | Net over the window | Net as % of gross |')
            L.append('|---|---|---:|---:|---:|')
            for w in s['window_gross_through_top']:
                L.append('| ' + addr_link(chain, w['address']) + ' | ' + w['symbol'] + ' | ' + usd(w['gross_through_usd']) + ' | ' + usd(w['net_usd']) + ' | ' +
                         (str(w['net_over_gross_pct']) + '%' if w['net_over_gross_pct'] is not None else '—') + ' |')
            L.append('')
            L.append('Largest net changes over the window: ' + '; '.join(addr_link(chain, w['address']) + ' ' + usd(w['net_usd']) + ' ' + w['symbol'] for w in s['window_net_top']) + '.\n')
        if s['unpriced_tokens_top']:
            L.append('Most-transferred unpriced tokens (candidates for the registry): ' + ', '.join(
                addr_link(chain, u['token'], sym(chain, ctx, u['token'], short(u['token']))) + ' ×' + str(u['transfers']) for u in s['unpriced_tokens_top'][:6]) + '.' +
                     (' Registry legs left unpriced for want of a feed: ' + ', '.join(f'{k} ×{v}' for k, v in s['registry_legs_without_price'].items()) + '.' if s['registry_legs_without_price'] else '') + '\n')
        for m, why in s.get('skipped_metrics', {}).items():
            L.append('Not ranked by ' + METRICS[m] + ': ' + why + '.\n')
        if not ps:
            continue
        L.append('### Selected transactions\n')
        L.append('| # | Transaction | Selected for | From | To | Largest position change | Gross volume | Native value | Status | Logs | Mechanism (LLM) |')
        L.append('|---:|---|---|---|---|---|---:|---:|---|---:|---|')
        start = counter
        for p in ps:
            counter += 1
            t, f = p['transaction'], {x['metric']: x for x in p['facts']}
            note = notes.get(t['transaction_hash'].lower(), {})
            reasons = ', '.join((METRICS.get(r['metric'], 'control') + (' #' + str(r['rank']) if r['metric'] != 'control' else '') +
                                 (' (pattern ×' + str(r['same_pattern_in_window']) + ')' if r.get('same_pattern_in_window', 1) > 1 else '')) for r in p['selection_reasons'])
            to = addr_link(chain, t['to']) if t['to'] else ('created ' + addr_link(chain, t['contract_created']) if t['contract_created'] else 'creation')
            d = f['position_change_usd']['detail']
            lp = (('+' if d['direction'] == 'received' else '−') + usd(f['position_change_usd']['value']) + ' ' + sym(chain, ctx, d['asset'], d['symbol']) + ' at ' +
                  addr_link(chain, d['address']) + (' (' + ', '.join(d['roles']) + ')' if d['roles'] else '')) if d else '—'
            if note:
                conf_counts[note.get('confidence', 'unstated')] += 1
            L.append(f"| {counter} | {tx_link(chain, t['transaction_hash'])} | {reasons} | {addr_link(chain, t['sender'])} | {to} | {lp} | " +
                     usd(f['gross_volume_usd']['value']) + ' | ' + f['native_value']['value'] + ' | ' + f['status']['value'] + f" | {t['log_count']} | " +
                     note.get('mechanism', '_not yet annotated_') + ' |')
        L.append('')
        L.append('### Investigations\n')
        n = start
        for p in ps:
            n += 1
            t, f, h = p['transaction'], {x['metric']: x for x in p['facts']}, p['transaction']['transaction_hash']
            note, pos, b = notes.get(h.lower(), {}), p['baseline_position'], p['block']
            L.append(f"#### {n}. {tx_link(chain, h)}: " + note.get('mechanism', 'not yet annotated') + '\n')
            d = f['position_change_usd']['detail']
            facts = ('Facts: block ' + f"{t['block_number']:,}" + ' at ' + t['block_utc'] + ', position ' + f['position_in_block']['value'] + ', type ' + t['type'] + ', ' +
                     f['status']['value'] + '. ')
            if d:
                facts += ('Largest position change: ' + addr_link(chain, d['address']) + (' (' + ', '.join(d['roles']) + ')' if d['roles'] else '') + ' ' + d['direction'] + ' ' +
                          d['net_amount'] + ' ' + sym(chain, ctx, d['asset'], d['symbol']) + ' net, ' + usd(f['position_change_usd']['value']) +
                          (' (chain percentile ' + str(pos['position_change_usd']['percentile_rank']) + ' among priced transactions)' if 'position_change_usd' in pos else '') + '. ')
            facts += ('Gross priced volume ' + usd(f['gross_volume_usd']['value']) + ' over ' + str(f['gross_volume_usd']['priced_legs']) + ' priced legs' +
                      (' (percentile ' + str(pos['gross_volume_usd']['percentile_rank']) + ')' if 'gross_volume_usd' in pos else '') + '. Native value ' + f['native_value']['value'] +
                      ' (' + usd(f['native_value']['usd']) + '). Fee paid ' + f['fee_paid']['value'] + (' (' + usd(f['fee_paid']['usd']) + ')' if f['fee_paid']['usd'] else '') +
                      ' at ' + t['effective_gas_price_gwei'] + ' gwei. Destination is ' + ('a contract creation' if not t['to'] else code_desc(chain, ctx, t['to'])) +
                      '. Selector `' + t['selector'] + '`, calldata ' + f"{t['calldata_bytes']:,}" + ' bytes, ' + str(t['log_count']) + (' log' if t['log_count'] == 1 else ' logs') +
                      ', ' + str(f['distinct_transfer_recipients']['value']) + (' distinct transfer recipient' if f['distinct_transfer_recipients']['value'] == 1 else ' distinct transfer recipients') + ', shape ' + f['shape']['value'] + '. ' +
                      ('Same pattern appears ' + str(f['same_pattern_in_window']['value']) + ' times in the window. ' if f['same_pattern_in_window']['value'] > 1 else '') +
                      (str(f['unpriced_erc20_transfers']['value']) + ' unpriced ERC-20 transfers on ' + str(f['unpriced_erc20_transfers']['tokens']) + ' tokens. ' if f['unpriced_erc20_transfers']['value'] else '') +
                      ('Same sender also at block positions ' + ', '.join(map(str, t['same_sender_other_indices_in_block'])) + '. ' if t['same_sender_other_indices_in_block'] else '') +
                      (str(t['authorization_list_len']) + ' EIP-7702 authorizations. ' if t.get('authorization_list_len') else ''))
            sw = p['sender_window']
            facts += ('Sender: ' + str(sw['transactions']) + ' transactions in the window, ' + str(sw['above_threshold']) + ' above the threshold, ' + usd(sw['sum_position_change_usd']) +
                      ' summed, ' + str(sw['distinct_destinations']) + (' destination' if sw['distinct_destinations'] == 1 else ' destinations') + (', ' + str(sw['failed']) + ' failed' if sw['failed'] else '') + '. ')
            cw = p['counterparty_window']
            if cw:
                facts += ('Counterparty ' + addr_link(chain, cw['address']) + (' (' + ', '.join(cw['roles']) + ')' if cw['roles'] else '') + ' is ' + code_desc(chain, ctx, cw['address']) +
                          ' touched by ' + str(cw['transactions_touching']) + ' transactions in the window, ' + str(cw['above_threshold_touching']) + ' above the threshold, sender of ' +
                          str(cw['as_tx_sender']) + '. ')
            facts += ('Block miner ' + addr_link(chain, b['miner']) + (' ("' + b['extra_data_text'] + '")' if b['extra_data_text'] else '') + ', utilization ' + str(b['gas_utilization']) + '.' +
                      ((' Index 0 of the block: ' + tx_link(chain, b['index0']['transaction_hash']) + ' from ' + addr_link(chain, b['index0']['sender']) + ' to ' +
                        (addr_link(chain, b['index0']['to']) if b['index0']['to'] else 'creation') + ', selector `' + b['index0']['selector'] + '`, largest change ' +
                        usd(b['index0']['position_change_usd']) + (' ' + b['index0']['largest_symbol'] if b['index0']['largest_symbol'] else '') + ', shape ' + b['index0']['shape'] + '.') if b['index0'] else ''))
            L.append(facts)
            wn = [(a, sym, v) for a, d in p.get('window_net', {}).items() for sym, v in d.items() if abs(Decimal(v['gross_through_usd'])) >= thr]
            if wn:
                L.append('\nOver the whole window: ' + '; '.join(addr_link(chain, a) + ' ' + usd(v['net_usd']) + ' ' + sym + ' net on ' + usd(v['gross_through_usd']) + ' through'
                                                          for a, sym, v in sorted(wn, key=lambda x: -Decimal(x[2]['gross_through_usd']))[:8]) + '.')
            if p['net_flows']:
                L.append('\nNet flows by address and asset (USD at the prices above): ' + '; '.join(
                    addr_link(chain, x['address']) + (' [' + ', '.join(x['roles']) + ']' if x['roles'] else '') + ' ' + ('+' if not x['net_amount'].startswith('-') else '') + x['net_amount'] + ' ' +
                    sym(chain, ctx, x['asset'], x['symbol']) + (' (' + usd(x['net_usd']) + ')' if x['net_usd'] is not None else ' (unpriced)') for x in p['net_flows']) +
                         ('; and ' + str(p['net_flows_truncated']) + ' more' if p['net_flows_truncated'] else '') + '.')
            if p['legs']:
                L.append('\nPriced legs in order: ' + '; '.join(
                    ('[' + str(x['log_index']) + '] ' if x['log_index'] is not None else '[value] ') + x['kind'] + ' ' + x['amount'] + ' ' + x['symbol'] +
                    (' (' + usd(x['usd']) + ')' if x['usd'] else '') + ' ' + (short(x['sender']) if x['sender'] else 'native') + ' to ' + (short(x['recipient']) if x['recipient'] else 'native')
                    for x in p['legs']) + ('; and ' + str(p['legs_truncated']) + ' more' if p['legs_truncated'] else '') + '.')
            if p['unpriced']:
                L.append('\nUnpriced ERC-20 transfers: ' + ', '.join(addr_link(chain, u['token'], sym(chain, ctx, u['token'], short(u['token']))) + ' ×' + str(u['transfers']) +
                                                                  ' (largest raw ' + u['largest_raw'] + ')' for u in p['unpriced']) + '.')
            fam = ', '.join(f'{k} ×{v}' for k, v in sorted(p['events']['families'].items(), key=lambda kv: -kv[1]))
            L.append('\nDecoded event families: ' + (fam or 'none') + '.')
            if note:
                L.append('\nInterpretation (LLM, confidence ' + note.get('confidence', 'unstated') + '): ' + note['body'])
                if note.get('unverified'):
                    L.append('\nUnverified: ' + note['unverified'])
            else:
                L.append('\n_No qualitative note yet for this transaction._')
            L.append('')
    L.append('## What the quant step handed over, and what came back\n')
    L.append('Packets: ' + str(len(packets)) + '. Annotated: ' + str(sum(1 for p in packets if p['transaction']['transaction_hash'].lower() in notes)) + '. LLM confidence: ' +
             ', '.join(f'{k} ×{v}' for k, v in conf_counts.most_common()) + '.\n')
    L.append('Artifacts: `prices.json` (feed readings with verification, in-sample cross-check), `packets.json` (evidence packets with fact IDs, net flows, ordered legs, block context, '
             'sender and counterparty activity), `stats.json` (per-chain baselines, population census, repeated patterns, repeat actors, unpriced tokens), `context.json` (bounded RPC lookups: '
             'token symbol/decimals with registry checks, code presence, pinned block), `qual_notes.md` (LLM notes keyed by transaction hash), `rpc_requests.jsonl` (every follow-up request '
             'with estimated credits; no keys).\n')
    if 'feedback' in notes:
        L.append('### Requests from the qualitative step back to the quant step (LLM)\n')
        L.append(notes['feedback']['body'] + '\n')
    L.append('Limitations: the sample is one two-minute window, so "large" means large within it. Only top-level native value is visible; ETH moved by contracts, including the native side of '
             'Uniswap V4 swaps and of WETH wraps, is not counted. Prices are single feed readings pinned at the sample end and stablecoins outside the feed set are taken at parity, so amounts '
             'are approximate to within the feed staleness and any depeg. Tokens outside the registry are unpriced, so a large movement of such a token is invisible to the ranking and appears '
             'only in the unpriced lists. Token symbols come from the token contracts themselves. Contract identities named in the notes without an onchain check are model memory and should '
             'be treated as hypotheses.\n')
    (out / 'report.md').write_text('\n'.join(L) + '\n')
    print(json.dumps({'report': str((out / 'report.md').relative_to(ROOT)), 'packets': len(packets),
                      'annotated': sum(1 for p in packets if p['transaction']['transaction_hash'].lower() in notes),
                      'sections': sorted(k for k in notes if not k.startswith('0x'))}))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['prices', 'scan', 'resolve', 'render', 'show'])
    p.add_argument('hashes', nargs='*', help='show: transaction hashes to print')
    p.add_argument('--max-logs', type=int, default=24)
    p.add_argument('--calldata-chars', type=int, default=400)
    p.add_argument('--data-chars', type=int, default=200)
    p.add_argument('--sample', default=str(RUN))
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-05' / 'amount_outliers'))
    p.add_argument('--threshold', default='10000', help='USD threshold for the population census and controls')
    p.add_argument('--top', type=int, default=3, help='transactions per metric per chain, at most one per repeated pattern')
    p.add_argument('--controls', type=int, default=2, help='hash-sampled controls per chain from the population above the threshold')
    p.add_argument('--max-credits', type=int, default=30000)
    p.add_argument('--max-tokens', type=int, default=30, help='token metadata lookups per chain')
    args = p.parse_args()
    {'prices': prices, 'scan': scan, 'resolve': resolve, 'render': render, 'show': show}[args.command](args)


if __name__ == '__main__':
    main()
