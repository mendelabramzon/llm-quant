#!/usr/bin/env python3
"""Transaction-type loop over the research window of Ethereum mainnet: large USD movements, typed.

prices    Bounded RPC. Chainlink USD feeds (ETH and BTC hourly, others at the window end), wstETH and other
          exchange rates at the window end. Cached in prices.json; verified entries are reused.
scan      Offline over raw blocks + logs. Values every top-level native transfer, registry ERC-20 transfer and WETH
          wrap/unwrap in USD; nets them per (address, asset); detects flash loans (same asset lent and repaid between
          the same two parties inside one transaction) and same-block sandwiches; derives in-sample prices for tokens
          outside the registry from their swaps against priced assets; profiles every address that touches a large
          transaction over the whole window. Writes txs_all.jsonl.gz, txs_big.jsonl.gz, addresses.json.gz, stats.json.
classify  Offline, fast. Applies the rules of replay/type_registry.py to every transaction above the threshold, runs
          the known investigation method of each type, clusters the unclassified residue and writes classified.json,
          residue.json, packets.json (evidence for the residue representatives) and appends to rounds.json.
resolve   Bounded RPC for packet transactions: receipt (status, gas used), code presence and EIP-7702 designators,
          token symbol/decimals. Cached in context.json.
render    classified + packets + context + qual_notes.md -> report.md.
show      Decoded logs of one transaction (hash, or hash@block).

The LLM reads packets, writes qual_notes.md, and turns each note into a registry entry (rule + method); classify
re-runs in seconds. Numbers in the report come from this code; the notes carry interpretation.
"""
import argparse
import bisect
import collections
from decimal import Decimal, getcontext
import gzip
import hashlib
import json
from pathlib import Path
import re
import statistics

from onchain_probe import ROOT, RPC, hx, save, utc
from analyze_onchain import decode, signed, address as topic_address
from enrich_cases import decode_string, selector as sel4
from signatures import family as log_family
from amount_outliers import ASSETS as PILOT_ASSETS, FEEDS as PILOT_FEEDS, WETH_DEPOSIT, WETH_WITHDRAWAL, ZERO, q2, usd, amount, extra_text
from gas_outliers import MINIMAL_PROXY, parse_notes as _parse_notes
import type_registry as REG

getcontext().prec = 50
CHAIN = 'ethereum'
EXPLORER = 'https://etherscan.io'
DAY = ROOT / 'research' / '2026-09-05' / 'eth_5h'
OUT_DEFAULT = ROOT / 'research' / '2026-09-05' / 'amount_outliers_eth_5h'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
USDC = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
SWAP_FAMILIES = ('V2Swap', 'V3Swap', 'V4Swap', 'CurveTokenExchange', 'CurveTokenExchangeU', 'CurveTokenExchangeUnderlying',
                 'BalancerSwap', 'DODOSwap', 'FluidSwap', 'BancorTokensTraded', 'MaverickSwap')
MAX_UNPRICED_LEGS = 40
MAX_LEGS_STORED = 120

# Asset registry for Ethereum: the pilot's entries plus stablecoins at parity, BTC wrappers at the BTC feed, and
# rate-bearing tokens whose rate is read once at the window end (RATES). Addresses are as known to the author;
# `resolve` checks symbol()/decimals() for tokens that reach the packets.
ASSETS = dict(PILOT_ASSETS['ethereum'])
ASSETS.update({
    '0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d': ('USD1', 18, 'USD'),
    '0x8292bb45bf1ee4d140127049757c2e0ff06317ed': ('RLUSD', 18, 'USD'),
    '0x0000000000085d4780b73119b644ae5ecd22b376': ('TUSD', 18, 'USD'),
    '0x8e870d67f660d95d5be530380d0ec0bd388289e1': ('USDP', 18, 'USD'),
    '0x853d955acef822db058eb8505911ed77f175b99e': ('FRAX', 18, 'USD'),
    '0xcacd6fd266af91b8aed52accc382b4e165586e29': ('frxUSD', 18, 'USD'),
    '0xc139190f447e929f090edeb554d95abb8b18ac1c': ('USDtb', 18, 'USD'),
    '0x18084fba666a33d37592fa2633fd49a74dd93a88': ('tBTC', 18, 'BTC'),
    '0x8236a87084f8b84306f72007f36f2618a5634494': ('LBTC', 8, 'BTC'),
    '0xa3931d71877c0e7a3148cb7eb4463524fec27fbd': ('sUSDS', 18, 'SUSDS'),
    '0x83f20f44975d03b1b09e64809b757c47f942beea': ('sDAI', 18, 'SDAI'),
    '0x9d39a5de30e57443bff2a8307a4256c8797a3497': ('sUSDe', 18, 'SUSDE'),
    '0xae78736cd615f374d3085123a210448e74fc6393': ('rETH', 18, 'RETH'),
    '0xbe9895146f7af43049ca1c1ae358b0541ea49704': ('cbETH', 18, 'CBETH'),
    '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee': ('weETH', 18, 'WEETH'),
    '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2': ('MKR', 18, 'MKR'),
    '0xd533a949740bb3306d119cc777fa900ba034cd52': ('CRV', 18, 'CRV'),
    '0xc18360217d8f7ab5e7c516566761ea12ce7f9d72': ('ENS', 18, 'ENS'),
})
FEEDS = {k: [c for c in v if c[0] == 'ethereum'] for k, v in PILOT_FEEDS.items() if any(c[0] == 'ethereum' for c in v)}
FEEDS['BTC'] = [('ethereum', '0xf4030086522a5beea4988f8ca5b36dbc97bee88c', ('BTC / USD',))]
FEEDS.update({
    'MKR': [('ethereum', '0xec1d1b3b0443256cc3860e24a46f108e699484aa', ('MKR / USD',))],
    'CRV': [('ethereum', '0xcd627aa160a6fa45eb793d19ef54f5062f20f33f', ('CRV / USD',))],
    'ENS': [('ethereum', '0x5c00128d4d1c2f4f652c267d7bcdd7ac99c16e16', ('ENS / USD',))],
})
HOURLY = ('ETH', 'BTC')
# rate-bearing tokens: price key -> (contract, method, underlying price key)
RATES = {
    'WSTETH': ('0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0', 'stEthPerToken()', 'STETH'),
    'RETH': ('0xae78736cd615f374d3085123a210448e74fc6393', 'getExchangeRate()', 'ETH'),
    'CBETH': ('0xbe9895146f7af43049ca1c1ae358b0541ea49704', 'exchangeRate()', 'ETH'),
    'WEETH': ('0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee', 'getRate()', 'ETH'),
    'SUSDS': ('0xa3931d71877c0e7a3148cb7eb4463524fec27fbd', 'convertToAssets(uint256)', 'USD'),
    'SDAI': ('0x83f20f44975d03b1b09e64809b757c47f942beea', 'convertToAssets(uint256)', 'DAI'),
    'SUSDE': ('0x9d39a5de30e57443bff2a8307a4256c8797a3497', 'convertToAssets(uint256)', 'USD'),
}
STABLE_KEYS = {'USD', 'USDC', 'USDT', 'DAI'}
ONE = (10 ** 18).to_bytes(32, 'big').hex()
WINDOW_HOURS = 5
ACTIVE_SAMPLE = DAY


def read_gz(path):
    with gzip.open(path, 'rt') as f:
        return json.load(f)


def short(h):
    return h[:6] + '…' + h[-4:]


def parse_notes(path):
    notes = _parse_notes(path)
    if path.exists():
        for section in re.split(r'^## ', path.read_text(), flags=re.M)[1:]:
            heading, _, body = section.partition('\n')
            if heading.startswith('type '):
                notes[heading.strip()] = {'body': body.strip()}
    notes.pop('type', None)
    return notes


def tx_link(h):
    return '[' + short(h) + '](' + EXPLORER + '/tx/' + h + ')'


def addr_link(a, label=None):
    if a and ':' in a:
        emitter, pool_id = a.split(':', 1)
        return addr_link(emitter, label or short(emitter)) + ' / pool ' + short(pool_id)
    return '—' if not a else '[' + (label or short(a)) + '](' + EXPLORER + '/address/' + a + ')'


def blocks_index(day):
    m = json.loads((day / 'blocks_manifest.json').read_text())
    return m['blocks']


def keccak(b):
    from Crypto.Hash import keccak as K
    return K.new(digest_bits=256, data=b).digest()


def rlp_bytes(b):
    if len(b) == 1 and b[0] < 0x80:
        return b
    if len(b) < 56:
        return bytes([0x80 + len(b)]) + b
    ln = len(b).to_bytes((len(b).bit_length() + 7) // 8, 'big')
    return bytes([0xb7 + len(ln)]) + ln + b


def created_address(sender, nonce):
    n = b'' if nonce == 0 else nonce.to_bytes((nonce.bit_length() + 7) // 8, 'big')
    payload = rlp_bytes(bytes.fromhex(sender[2:])) + rlp_bytes(n)
    return '0x' + keccak(bytes([0xc0 + len(payload)]) + payload)[-20:].hex()


# ---------------------------------------------------------------- prices
def prices(args):
    out, day = Path(args.out), Path(args.day)
    manifest = json.loads((day / 'manifest.json').read_text())
    blocks = blocks_index(day)
    start, end = manifest['start_timestamp'], manifest['end_timestamp']
    pins = []
    for h in range(1, (end - start + 3599) // 3600 + 1):
        cut = min(start + h * 3600, end)
        cand = [b for b in blocks if b['timestamp'] < cut]
        if cand:
            pins.append((h, cand[-1]['number'], cand[-1]['timestamp']))
    last = blocks[-1]['number']
    rpc = RPC(out, key_index=manifest.get('key_index', 0), max_credits=args.max_credits, interval=.3)
    previous = json.loads((out / 'prices.json').read_text()) if (out / 'prices.json').exists() else {'assets': {}, 'hourly': {}}
    if previous.get('pinned_block', last) != last:
        raise ValueError('Cached prices belong to a different window')
    result = {'generated_at': utc(), 'window': {'start_utc': manifest['start_utc'], 'end_utc': manifest['end_utc']}, 'pinned_block': last,
              'hour_pins': [{'hour': h, 'block': n, 'timestamp': t, 'utc': utc(t)} for h, n, t in pins], 'assets': {}, 'hourly': {},
              'method': 'Chainlink aggregator proxy latestRoundData() at the pinned block; description() must match the expected pair. '
                        'ETH and BTC are read at the last block of every hour; other feeds at the window end. Rate-bearing tokens use one '
                        'exchange-rate call at the window end times the underlying price. Stablecoins without a feed are valued at parity by scan.'}

    def read_feed(agg, expected, pin):
        calls = [('eth_call', [{'to': agg, 'data': sel4(m)}, hex(pin)]) for m in ('description()', 'decimals()', 'latestRoundData()')]
        vals = rpc.batch(CHAIN, calls, allow_errors=True)
        desc = decode_string(vals[0]) if isinstance(vals[0], str) else None
        dec = hx(vals[1]) if isinstance(vals[1], str) and len(vals[1]) == 66 else None
        entry = {'feed': agg, 'expected_description': list(expected), 'description_onchain': desc, 'decimals': dec, 'block': pin, 'usd': None, 'verified': False}
        rd = vals[2]
        if isinstance(rd, str) and len(rd) == 2 + 5 * 64 and dec is not None:
            words = [int(rd[2 + i * 64:2 + (i + 1) * 64], 16) for i in range(5)]
            answer, updated = signed(words[1]), words[3]
            pin_ts = next(b['timestamp'] for b in blocks if b['number'] == pin)
            fresh = 0 < updated <= pin_ts and pin_ts - updated <= 172800 and words[4] >= words[0]
            entry.update(round_id=str(words[0]), answer_raw=str(answer), updated_at=utc(updated), age_seconds=pin_ts-updated, verified=desc in expected and fresh)
            if entry['verified'] and answer > 0:
                entry['usd'] = str(Decimal(answer) / Decimal(10) ** dec)
                entry['source'] = 'Chainlink ' + desc + ' at block ' + str(pin)
        return entry

    for key, candidates in FEEDS.items():
        if previous['assets'].get(key, {}).get('usd'):
            result['assets'][key] = previous['assets'][key]
        else:
            tried = []
            for _, agg, expected in candidates:
                tried.append(read_feed(agg, expected, last))
                if tried[-1]['usd']:
                    break
            result['assets'][key] = dict(tried[-1], rejected_candidates=tried[:-1])
        print(json.dumps({'asset': key, 'usd': result['assets'][key]['usd'], 'description': result['assets'][key]['description_onchain']}), flush=True)
        if key in HOURLY and result['assets'][key]['usd']:
            agg = result['assets'][key]['feed']
            series = previous['hourly'].get(key) or []
            done = {s['block'] for s in series if s.get('usd')}
            for h, n, t in pins:
                if n in done:
                    continue
                e = read_feed(agg, tuple(result['assets'][key]['expected_description']), n)
                series.append({'hour': h, 'block': n, 'timestamp': t, 'usd': e['usd'], 'updated_at': e.get('updated_at')})
            result['hourly'][key] = sorted(series, key=lambda s: s['block'])
            print(json.dumps({'asset': key, 'hourly_points': len(series), 'priced': sum(1 for s in series if s['usd'])}), flush=True)
    for key, (contract, method, under) in RATES.items():
        if previous['assets'].get(key, {}).get('usd'):
            result['assets'][key] = previous['assets'][key]
            continue
        data = sel4(method) + (ONE if '(uint256)' in method else '')
        v = rpc.call(CHAIN, 'eth_call', [{'to': contract, 'data': data}, hex(last)], allow_errors=True)
        base = result['assets'].get(under, {}).get('usd') if under != 'USD' else '1'
        entry = {'contract': contract, 'call': method, 'underlying': under, 'block': last, 'usd': None, 'verified': False, 'raw': v if isinstance(v, str) else str(v)[:200]}
        if isinstance(v, str) and len(v) == 66 and base:
            ratio = Decimal(hx(v)) / Decimal(10 ** 18)
            if Decimal('0.5') < ratio < Decimal(3):
                entry.update(rate=str(ratio), usd=str(Decimal(base) * ratio), verified=True, source=under + ' times ' + method + ' at block ' + str(last))
        result['assets'][key] = entry
        print(json.dumps({'asset': key, 'usd': entry['usd'], 'rate': entry.get('rate')}), flush=True)
    result['assumed_parity'] = sorted({s for s, _, k in ASSETS.values() if k == 'USD'})
    result['registry_validation'] = {}
    for a, (label, decimals, _) in ASSETS.items():
        vals = rpc.batch(CHAIN, [('eth_call', [{'to': a, 'data': sel4(m)}, hex(last)]) for m in ('symbol()', 'decimals()')], allow_errors=True)
        dec = hx(vals[1]) if isinstance(vals[1], str) and len(vals[1]) == 66 else None
        result['registry_validation'][a] = {'label': label, 'symbol_untrusted': decode_string(vals[0]) if isinstance(vals[0], str) else None,
                                            'decimals': dec, 'expected_decimals': decimals, 'decimals_match': dec == decimals, 'block': last}
    result['estimated_credits'] = rpc.credits
    save(out / 'prices.json', result)


class PriceTable:
    """USD price per key; ETH and BTC vary by hour, everything else is a single window-end reading."""

    def __init__(self, out, start):
        self.start = start
        self.flat, self.source, self.hourly = {}, {}, {}
        path = out / 'prices.json'
        self.meta = {'file': None}
        if path.exists():
            p = json.loads(path.read_text())
            self.meta = {'file': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path), 'generated_at': p['generated_at']}
            for k, v in p['assets'].items():
                if v.get('usd'):
                    self.flat[k], self.source[k] = Decimal(v['usd']), v.get('source', 'prices.json')
            for k, series in p.get('hourly', {}).items():
                pts = [(s['timestamp'], Decimal(s['usd'])) for s in series if s.get('usd')]
                if pts:
                    self.hourly[k] = sorted(pts)
                    self.source[k] = 'Chainlink hourly series (' + str(len(pts)) + ' points), window-end ' + str(self.flat.get(k))
        for k in STABLE_KEYS:
            if k not in self.flat:
                self.flat[k], self.source[k] = Decimal(1), 'assumed parity'
        self.implied = {}

    def get(self, key, ts=None):
        if key in self.hourly and ts is not None:
            pts = self.hourly[key]
            i = bisect.bisect_left([t for t, _ in pts], ts)
            return pts[min(i, len(pts) - 1)][1]
        if key in self.flat:
            return self.flat[key]
        return self.implied.get(key)

    def used(self):
        d = {k: {'usd': str(v), 'source': self.source[k]} for k, v in sorted(self.flat.items())}
        for k, v in self.implied.items():
            d[k] = {'usd': str(v), 'source': self.source[k]}
        return d


def statuses(args):
    """Confirm every no-log native-value candidate above the amount threshold before counting value."""
    out, day = Path(args.out), Path(args.day)
    manifest = json.loads((day / 'manifest.json').read_text())
    prices = PriceTable(out, manifest['start_timestamp'])
    path = out / 'native_status.json'
    cached = json.loads(path.read_text()) if path.exists() else {}
    pending = []
    for b in blocks_index(day):
        block = read_gz(day / 'raw' / 'blocks' / (str(b['number']) + '.json.gz'))
        logs = read_gz(day / 'raw' / 'logs' / (str(b['number']) + '.json.gz'))
        logged = {l['transactionHash'] for l in logs}
        p = prices.get('ETH', b['timestamp'])
        if p is None:
            raise ValueError('ETH price required')
        for t in block['transactions']:
            if t['hash'] not in logged and Decimal(hx(t.get('value', 0))) / Decimal(10 ** 18) * p >= Decimal(args.threshold) and t['hash'] not in cached:
                pending.append((t['hash'], block['hash']))
    rpc = RPC(out, key_index=manifest.get('key_index', 0), max_credits=args.max_credits)
    print(json.dumps({'native_receipts_needed': len(pending)}), flush=True)
    for i in range(0, len(pending), 10):
        part = pending[i:i+10]
        vals = rpc.batch(CHAIN, [('eth_getTransactionReceipt', [h]) for h, _ in part])
        for (h, bh), v in zip(part, vals):
            if not v or v.get('blockHash') != bh or v.get('transactionHash') != h:
                raise ValueError('Receipt provenance mismatch')
            cached[h] = {'status': 'success' if hx(v['status']) else 'failed', 'block_hash': bh,
                         'gas_used': hx(v['gasUsed']), 'effective_gas_price_wei': hx(v['effectiveGasPrice'])}
        save(path, cached)
    print(json.dumps({'receipts': len(cached), 'failed': sum(v['status']=='failed' for v in cached.values()), 'credits': rpc.credits}), flush=True)


# ---------------------------------------------------------------- scan phase A: per-transaction rows
def effective_price(t, base_fee):
    if 'maxFeePerGas' in t:
        return min(hx(t['maxFeePerGas']), base_fee + hx(t.get('maxPriorityFeePerGas', 0)))
    return hx(t.get('gasPrice', 0))


def swap_direction(d):
    f = d['family']
    if f == 'V3Swap':
        return 1 if int(d.get('amount0_raw', 0)) > 0 else -1
    if f == 'V2Swap':
        return 1 if int(d.get('amount0_in_raw', 0)) > 0 else -1
    if f == 'V4Swap':
        return 1 if int(d.get('amount0_raw', 0)) < 0 else -1
    return 0


def swap_identity(address, decoded):
    # A v4 PoolManager hosts many pools; its address alone is not a pool identity.
    return address + ':' + decoded['pool_id'] if decoded['family'] == 'V4Swap' else address


def tx_row(block, t, logs, prices, ts):
    """Features of one transaction from its block record and its logs. Registry prices only; unpriced legs kept compactly."""
    sender, to = t['from'].lower(), (t.get('to') or '').lower() or None
    value = hx(t.get('value', 0))
    base_fee = hx(block.get('baseFeePerGas', 0))
    eff = effective_price(t, base_fee)
    nonce = hx(t.get('nonce', 0))
    row = {'h': t['hash'], 'b': hx(block['number']), 'i': hx(t['transactionIndex']), 't': ts, 'from': sender, 'to': to, 'v': str(value), 'n': nonce,
           'sel': t.get('input', '0x')[:10], 'cd': (len(t.get('input', '0x')) - 2) // 2, 'ty': t.get('type', '0x0'), 'gl': hx(t['gas']),
           'eff': eff, 'tip': eff - base_fee, 'auth': len(t.get('authorizationList') or []), 'blobs': len(t.get('blobVersionedHashes') or []),
           'created': created_address(sender, nonce) if to is None else None, 'lc': len(logs)}
    fam = collections.Counter()
    legs, unpriced, emitters, unknown = [], {}, set(), collections.Counter()
    swaps, pool_in, pool_out = [], collections.defaultdict(list), collections.defaultdict(list)
    e721 = e1155 = 0
    if value:
        legs.append({'li': -1, 'k': 'native', 'a': 'native', 's': 'ETH', 'key': 'ETH', 'f': sender, 'r': to or row['created'], 'raw': value})
    for l in logs:
        a = l['address'].lower()
        emitters.add(a)
        f = log_family(l)
        fam[f] += 1
        ts_ = l.get('topics') or []
        if f == 'Transfer':
            d = decode(l)
            f = d['family']
            fam['Transfer'] -= 1
            fam[f] += 1
            if f == 'ERC20_Transfer_shape':
                raw = int(d['amount_raw'])
                if a in ASSETS:
                    sym, dec, key = ASSETS[a]
                    legs.append({'li': hx(l['logIndex']), 'k': 'erc20', 'a': a, 's': sym, 'key': key, 'f': d['sender'], 'r': d['recipient'], 'raw': raw})
                else:
                    u = unpriced.setdefault(a, [0, 0, []])
                    u[0] += 1
                    u[1] = max(u[1], raw)
                    if len(u[2]) < MAX_UNPRICED_LEGS:
                        u[2].append([hx(l['logIndex']), d['sender'], d['recipient'], str(raw)])
                pool_in[d['recipient']].append((a, raw))
                pool_out[d['sender']].append((a, raw))
            elif f == 'ERC721_Transfer_shape':
                e721 += 1
        elif f in ('ERC1155TransferSingle', 'ERC1155TransferBatch'):
            e1155 += 1
        elif a == WETH and len(ts_) == 2 and ts_[0] in (WETH_DEPOSIT, WETH_WITHDRAWAL) and len(l.get('data', '0x')) == 66:
            wrap = ts_[0] == WETH_DEPOSIT
            who = topic_address(ts_[1])
            legs.append({'li': hx(l['logIndex']), 'k': 'wrap' if wrap else 'unwrap', 'a': WETH, 's': 'WETH', 'key': 'ETH', 'f': None if wrap else who,
                         'r': who if wrap else None, 'raw': int(l['data'], 16)})
        elif f in SWAP_FAMILIES:
            d = decode(l)
            swaps.append((a, swap_identity(a, d), swap_direction(d)))
        elif f == 'unknown':
            unknown[(a, ts_[0])] += 1
    fam = {k: v for k, v in fam.items() if v}
    # what the non-transfer events say: registry tokens named in their topics or data, and whether a leg amount is echoed
    leg_words = {format(l['raw'], '064x') for l in legs if l['raw']}
    evt_tokens, evt_echo, evt_tokens_hits = set(), False, 0
    for l in logs:
        f = log_family(l)
        if f in ('Transfer', 'Approval') or f in SWAP_FAMILIES:
            continue
        words = [w[2:] for w in (l.get('topics') or [])[1:]] + [l['data'][2 + i:2 + i + 64] for i in range(0, len(l.get('data', '0x')) - 2, 64)]
        for w in words:
            if len(w) != 64:
                continue
            if w.startswith('0' * 24) and ('0x' + w[24:]) in ASSETS:
                evt_tokens.add('0x' + w[24:])
                evt_tokens_hits += 1
            elif w in leg_words:
                evt_echo = True
    # implied price observations: a swap emitter that received exactly one token and sent exactly one token
    implied = []
    for pool, _, _ in swaps:
        ins, outs = pool_in.get(pool, []), pool_out.get(pool, [])
        if len(ins) == 1 and len(outs) == 1 and ins[0][0] != outs[0][0]:
            (ta, ra), (tb, rb) = ins[0], outs[0]
            for x, rx, y, ry in ((ta, ra, tb, rb), (tb, rb, ta, ra)):
                if x in ASSETS and y not in ASSETS and rx and ry:
                    sym, dec, key = ASSETS[x]
                    p = prices.get(key, ts)
                    if p is not None:
                        usd_x = Decimal(rx) / Decimal(10) ** dec * p
                        implied.append([y, str(usd_x), str(ry)])
    memo = ''
    if row['cd'] > 36:
        try:
            raw = bytes.fromhex(t.get('input', '0x')[10:])
        except ValueError:
            raw = b''
        runs = re.findall(rb'[\x20-\x7e]{8,}', raw)
        memo = max(runs, key=len).decode('ascii')[:120] if runs else ''
    row.update(fam=fam, em=len(emitters), legs=legs, unp=unpriced, swaps=len(swaps), pools=sorted({p for p, _, _ in swaps}), memo=memo,
               pool_ids=sorted({p for _, p, _ in swaps}),
               flash_emitters=sorted({l['address'].lower() for l in logs if log_family(l) in ('MorphoFlashLoan', 'BalancerFlashLoan', 'AaveFlashLoan', 'V3Flash')}),
               event_emitters={f: sorted({l['address'].lower() for l in logs if log_family(l) == f}) for f in fam if f not in ('ERC20_Transfer_shape', 'ERC721_Transfer_shape', 'Approval', 'unknown')},
               sd=[[p, d] for _, p, d in swaps], rc721=e721, rc1155=e1155,
               unk=[[a, tp, n] for (a, tp), n in unknown.most_common()], impl=implied,
               to_em=(to in emitters) if to else False, pool_to=any(p == to for p, _, _ in swaps) if to else False,
               evt_tokens=sorted(evt_tokens), evt_echo=evt_echo)
    return row


def value_legs(row, prices, decimals_of):
    """Price legs, net per (address, asset), flash-loan pairs, largest position. Mutates and returns the row."""
    ts = row['t']
    legs = row['legs']
    for leg in legs:
        p = prices.get(leg['key'], ts)
        dec = 18 if leg['k'] == 'native' else decimals_of(leg['a'])
        leg['usd'] = None if p is None else Decimal(leg['raw']) / Decimal(10) ** dec * p
        leg['dec'] = dec
        leg['fl'] = None
    # flash loans: A -> B amount X at log i, B -> A amount Y >= X at log j > i, same asset, both priced, X >= $1,000
    by_pair = collections.defaultdict(list)
    for idx, leg in enumerate(legs):
        if leg['k'] == 'erc20' and leg['f'] and leg['r'] and leg['f'] != ZERO and leg['r'] != ZERO and leg['usd'] is not None:
            by_pair[(leg['a'], leg['f'], leg['r'])].append(idx)
    flash = []
    used = set()
    for (asset, a, b), idxs in by_pair.items():
        if a == b:
            continue
        if a not in row.get('flash_emitters', []):
            continue
        back = by_pair.get((asset, b, a))
        if not back:
            continue
        for i in idxs:
            if i in used or legs[i]['usd'] < 1000:
                continue
            j = next((j for j in back if j > i and j not in used and legs[j]['raw'] >= legs[i]['raw']), None)
            if j is None:
                continue
            used.update((i, j))
            legs[i]['fl'], legs[j]['fl'] = 'borrow', 'repay'
            flash.append({'a': asset, 's': legs[i]['s'], 'lender': a, 'borrower': b, 'raw': str(legs[i]['raw']), 'usd': str(q2(legs[i]['usd'])),
                          'fee_raw': str(legs[j]['raw'] - legs[i]['raw'])})
    net = collections.defaultdict(lambda: [0, Decimal(0)])
    gross = gross_xf = Decimal(0)
    priced = 0
    mb = collections.defaultdict(lambda: [Decimal(0), Decimal(0)])
    for leg in legs:
        if leg['usd'] is not None:
            gross += leg['usd']
            priced += 1
            if not leg['fl']:
                gross_xf += leg['usd']
            if leg['f'] == ZERO:
                mb[leg['s']][0] += leg['usd']
            if leg['r'] == ZERO:
                mb[leg['s']][1] += leg['usd']
        for who, sign in ((leg['f'], -1), (leg['r'], 1)):
            if who is not None and who != ZERO:
                e = net[(who, leg['a'])]
                e[0] += sign * leg['raw']
                if leg['usd'] is not None:
                    e[1] += sign * leg['usd']
    largest = None
    if net:
        (who, asset), (raw, u) = max(net.items(), key=lambda kv: (abs(kv[1][1]), kv[0]))
        meta = next(l for l in legs if l['a'] == asset)
        largest = {'addr': who, 'a': asset, 's': meta['s'], 'dec': meta['dec'], 'raw': str(raw), 'usd': str(q2(u))}
    sym = {l['a']: l['s'] for l in legs}
    fnet, tnet = collections.defaultdict(Decimal), collections.defaultdict(Decimal)
    for (who, asset), (raw, u) in net.items():
        if who == row['from']:
            fnet[sym[asset]] += u
        if row['to'] and who == row['to']:
            tnet[sym[asset]] += u
    native_usd = legs[0]['usd'] if legs and legs[0]['k'] == 'native' and legs[0]['usd'] is not None else Decimal(0)
    row.update(pc=str(q2(abs(Decimal(largest['usd'])))) if largest else '0', lg=largest, gross=str(q2(gross)), gross_xf=str(q2(gross_xf)),
               flash=flash, flash_usd=str(q2(sum((Decimal(f['usd']) for f in flash), Decimal(0)))), priced=priced,
               net=[[who, asset, sym[asset], str(raw), str(q2(u))] for (who, asset), (raw, u) in sorted(net.items(), key=lambda kv: (-abs(kv[1][1]), kv[0]))[:24]],
               fnet={k: str(q2(v)) for k, v in fnet.items() if abs(v) >= Decimal('0.01')}, tnet={k: str(q2(v)) for k, v in tnet.items() if abs(v) >= Decimal('0.01')},
               mb={k: [str(q2(a)), str(q2(b))] for k, (a, b) in mb.items()}, native_usd=str(q2(native_usd)),
               rcpt=len({l['r'] for l in legs if l['r']}), assets=sorted({l['s'] for l in legs if l['usd'] is not None}))
    return row


def compact_legs(legs):
    return [{'li': l['li'], 'k': l['k'], 'a': l['a'], 's': l['s'], 'key': l['key'], 'f': l['f'], 'r': l['r'], 'raw': str(l['raw']),
             'usd': str(q2(l['usd'])) if l.get('usd') is not None else None, 'fl': l.get('fl')} for l in legs]


def sandwiches(rows):
    """Same-block round trips through one pool by one actor with a stranger's swap in between."""
    by_pool = collections.defaultdict(list)
    for r in rows:
        actors = {r['from']}
        for pool, d in r['sd']:
            if d == 0:
                continue
            by_pool[pool].append((r['i'], actors, d, r))
    for pool, seq in by_pool.items():
        seq.sort(key=lambda x: x[0])
        for x in range(len(seq)):
            i, actors_i, d_i, r_i = seq[x]
            for y in range(x + 2, len(seq)):
                j, actors_j, d_j, r_j = seq[y]
                if actors_i & actors_j and d_j == -d_i:
                    victims = [seq[k] for k in range(x + 1, y) if not (seq[k][1] & actors_i) and seq[k][2] == d_i]
                    if victims:
                        v = victims[0][3]
                        r_i.setdefault('sw', []).append({'role': 'front', 'pool': pool, 'victim': v['h'], 'victim_index': v['i'], 'back': r_j['h'], 'victims': len(victims)})
                        r_j.setdefault('sw', []).append({'role': 'back', 'pool': pool, 'victim': v['h'], 'victim_index': v['i'], 'front': r_i['h'], 'victims': len(victims)})
                        for vv in victims:
                            vv[3].setdefault('sw', []).append({'role': 'victim', 'pool': pool, 'front': r_i['h'], 'back': r_j['h']})
                    break


def scan(args):
    out, day = Path(args.out), Path(args.day)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((day / 'manifest.json').read_text())
    blocks = blocks_index(day)
    if not manifest.get('complete') or manifest.get('quality_issues'):
        raise ValueError('A complete, verified collection is required before scan')
    if args.limit:
        blocks = blocks[:args.limit]
    prices = PriceTable(out, manifest['start_timestamp'])
    validation = json.loads((out / 'prices.json').read_text()).get('registry_validation', {})
    mismatches = [a for a in ASSETS if not validation.get(a, {}).get('decimals_match')]
    if mismatches:
        raise ValueError('Unverified registry decimals: ' + ', '.join(mismatches))
    status_path = out / 'native_status.json'
    native_status = json.loads(status_path.read_text()) if status_path.exists() else {}
    decimals_of = lambda a: ASSETS[a][1] if a in ASSETS else 18
    thr = Decimal(args.threshold)
    # Phase A: rows for every transaction, registry prices, implied-price observations
    implied_obs = collections.defaultdict(list)
    counts = collections.Counter()
    tmp_all = out / 'txs_all.jsonl.gz'
    pool_eth = []
    verified_pools = set()
    meta_path = ROOT / 'research/2026-09-05/followup/metadata.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text()).get('ethereum', {})
        verified_pools = {a for a, p in meta.get('pools', {}).items() if p.get('token0') == USDC and p.get('token1') == WETH}
    with gzip.open(tmp_all, 'wt') as fa:
        for bi, binfo in enumerate(blocks):
            n = binfo['number']
            block = read_gz(day / 'raw' / 'blocks' / (str(n) + '.json.gz'))
            logs = read_gz(day / 'raw' / 'logs' / (str(n) + '.json.gz'))
            by_tx = collections.defaultdict(list)
            for l in logs:
                by_tx[l['transactionHash']].append(l)
                if l['address'].lower() in verified_pools:
                    d = decode(l)
                    if d['family'] == 'V3Swap':
                        p = (Decimal(d['sqrtPriceX96']) / Decimal(2 ** 96)) ** 2 * Decimal(10) ** (6 - 18)
                        pool_eth.append((hx(block['timestamp']), 1 / p, abs(int(d['amount0_raw']))))
            ts = hx(block['timestamp'])
            rows = []
            for t in block['transactions']:
                r = tx_row(block, t, by_tx.get(t['hash'], []), prices, ts)
                r['status'] = 'success_from_logs' if r['lc'] else native_status.get(r['h'], {}).get('status', 'unknown')
                if not r['lc'] and int(r['v']) and r['status'] != 'success':
                    counts['native_unconfirmed_or_failed'] += 1
                    r['legs'] = [l for l in r['legs'] if l['k'] != 'native']
                value_legs(r, prices, decimals_of)
                for y, usd_x, ry in r.pop('impl'):
                    implied_obs[y].append((ts, Decimal(usd_x), int(ry)))
                rows.append(r)
            sandwiches(rows)
            for r in rows:
                r['legs'] = compact_legs(r['legs'])
                r['unp'] = {a: [c, str(m), lst] for a, (c, m, lst) in r['unp'].items()}
                fa.write(json.dumps(r, separators=(',', ':')) + '\n')
            counts['blocks'] += 1
            counts['transactions'] += len(rows)
            counts['logs'] += len(logs)
            if bi % 500 == 0:
                print(json.dumps({'phase': 'A', 'blocks': counts['blocks'], 'transactions': counts['transactions']}), flush=True)
    # Phase B: implied prices for tokens outside the registry (median USD per token unit at 18 decimals, per token, whole window)
    implied = {}
    for tok, obs in implied_obs.items():
        vol = sum(u for _, u, _ in obs)
        if len(obs) >= args.implied_min_swaps and vol >= Decimal(args.implied_min_volume):
            per_unit = [u / (Decimal(raw) / Decimal(10 ** 18)) for _, u, raw in obs if raw]
            if per_unit:
                implied[tok] = {'usd_per_1e18': str(statistics.median(per_unit)), 'swaps': len(obs), 'usd_volume': str(q2(vol)),
                                'p10': str(sorted(per_unit)[len(per_unit) // 10]), 'p90': str(sorted(per_unit)[len(per_unit) * 9 // 10])}
    print(json.dumps({'phase': 'B', 'implied_priced_tokens': len(implied), 'candidates': len(implied_obs)}), flush=True)
    # Phase C: re-value unpriced legs of every transaction with implied prices (decimals assumed 18; corrected by resolve for
    # packet tokens), select the population above the threshold, profile the addresses it touches over the whole window.
    for tok, e in implied.items():
        prices.implied['IMPL:' + tok] = Decimal(e['usd_per_1e18'])
        prices.source['IMPL:' + tok] = 'in-sample median of ' + str(e['swaps']) + ' swaps against priced assets, $' + e['usd_volume'] + ' volume; 18 decimals assumed'
    big, interesting = [], set()
    all_emitters = set()
    with gzip.open(tmp_all, 'rt') as fa:
        for line in fa:
            r = json.loads(line)
            if r['unp'] and any(a in implied for a in r['unp']):
                legs = [dict(l, raw=int(l['raw'])) for l in r['legs']]
                for a, (c, m, lst) in r['unp'].items():
                    if a in implied:
                        for li, f, t_, raw in lst:
                            legs.append({'li': li, 'k': 'erc20', 'a': a, 's': 'IMPL:' + short(a), 'key': 'IMPL:' + a, 'f': f, 'r': t_, 'raw': int(raw)})
                legs.sort(key=lambda l: l['li'])
                r['legs'] = legs
                value_legs(r, prices, decimals_of)
                r['legs'] = compact_legs(legs)
                r['unp'] = {a: v for a, v in r['unp'].items() if a not in implied}
                r['revalued'] = True
            r['selection'] = [key for key, limit in (('pc', thr), ('flash_usd', thr), ('gross', thr * 10)) if Decimal(r[key]) >= limit]
            if r['selection']:
                big.append(r)
                interesting.add(r['from'])
                if r['to']:
                    interesting.add(r['to'])
                for l in r['legs']:
                    for who in (l['f'], l['r']):
                        if who and who != ZERO:
                            interesting.add(who)
    print(json.dumps({'phase': 'C', 'above_threshold': len(big), 'interesting_addresses': len(interesting)}), flush=True)
    A = collections.defaultdict(lambda: {'sent': 0, 'to': set(), 'n_min': None, 'n_max': None, 'tips': [], 'val_usd': Decimal(0), 'sel': collections.Counter(),
                                         'hours': set(), 'touched': 0, 'net': collections.defaultdict(Decimal), 'gross': collections.defaultdict(Decimal),
                                         'in_from': set(), 'out_to': set(), 'first': None, 'last': None, 'big': 0, 'big_usd': Decimal(0), 'as_to': 0,
                                         'flash_lent': Decimal(0), 'swaps_as_to': 0, 'pool_swaps': 0, 'created': 0})
    start = manifest['start_timestamp']
    with gzip.open(tmp_all, 'rt') as fa:
        for line in fa:
            r = json.loads(line)
            parties = {r['from']} | ({r['to']} if r['to'] else set()) | {w for l in r['legs'] for w in (l['f'], l['r']) if w}
            hit = parties & interesting
            if not hit:
                continue
            isbig = Decimal(r['pc']) >= thr
            hour = (r['t'] - start) // 3600
            if r['from'] in hit:
                s = A[r['from']]
                s['sent'] += 1
                if r['to']:
                    s['to'].add(r['to'])
                else:
                    s['created'] += 1
                s['n_min'] = r['n'] if s['n_min'] is None else min(s['n_min'], r['n'])
                s['n_max'] = r['n'] if s['n_max'] is None else max(s['n_max'], r['n'])
                s['tips'].append(r['tip'])
                s['val_usd'] += Decimal(r['native_usd'])
                s['sel'][r['sel']] += 1
                s['hours'].add(hour)
            if r['to'] and r['to'] in hit:
                A[r['to']]['as_to'] += 1
                if r['swaps']:
                    A[r['to']]['swaps_as_to'] += 1
            for p in r['pools']:
                if p in hit:
                    A[p]['pool_swaps'] += 1
            for who in hit:
                s = A[who]
                s['touched'] += 1
                s['first'] = r['b'] if s['first'] is None else min(s['first'], r['b'])
                s['last'] = r['b'] if s['last'] is None else max(s['last'], r['b'])
                if isbig:
                    s['big'] += 1
                    s['big_usd'] += Decimal(r['pc'])
            for l in r['legs']:
                if l['usd'] is None:
                    continue
                u = Decimal(l['usd'])
                if l['f'] in hit:
                    s = A[l['f']]
                    s['net'][l['s']] -= u
                    s['gross'][l['s']] += u
                    if l['r']:
                        s['out_to'].add(l['r'])
                    if l['fl'] == 'borrow':
                        s['flash_lent'] += u
                if l['r'] in hit:
                    s = A[l['r']]
                    s['net'][l['s']] += u
                    s['gross'][l['s']] += u
                    if l['f']:
                        s['in_from'].add(l['f'])
    addresses = {}
    for a, s in A.items():
        tips = sorted(s['tips'])
        addresses[a] = {'sent': s['sent'], 'to_distinct': len(s['to']), 'created': s['created'], 'nonce_min': s['n_min'], 'nonce_max': s['n_max'],
                        'tip_median_gwei': str(Decimal(tips[len(tips) // 2]) / Decimal(10 ** 9)) if tips else None,
                        'tip_p10_gwei': str(Decimal(tips[len(tips) // 10]) / Decimal(10 ** 9)) if tips else None,
                        'tip_p90_gwei': str(Decimal(tips[len(tips) * 9 // 10]) / Decimal(10 ** 9)) if tips else None,
                        'native_sent_usd': str(q2(s['val_usd'])), 'selectors': s['sel'].most_common(3), 'hours_active': len(s['hours']),
                        'touched': s['touched'], 'as_to': s['as_to'], 'swaps_as_to': s['swaps_as_to'], 'pool_swaps': s['pool_swaps'],
                        'big': s['big'], 'big_usd': str(q2(s['big_usd'])), 'flash_lent_usd': str(q2(s['flash_lent'])),
                        'net': {k: str(q2(v)) for k, v in sorted(s['net'].items(), key=lambda kv: -abs(kv[1]))[:12]},
                        'gross': {k: str(q2(v)) for k, v in sorted(s['gross'].items(), key=lambda kv: -kv[1])[:12]},
                        'in_from_distinct': len(s['in_from']), 'out_to_distinct': len(s['out_to']), 'first_block': s['first'], 'last_block': s['last']}
    with gzip.open(out / 'addresses.json.gz', 'wt') as f:
        json.dump(addresses, f, separators=(',', ':'))
    big.sort(key=lambda r: (r['b'], r['i']))
    with gzip.open(out / 'txs_big.jsonl.gz', 'wt') as f:
        for r in big:
            f.write(json.dumps(r, separators=(',', ':')) + '\n')
    pool_eth.sort()
    hourly = collections.defaultdict(list)
    for ts_, p, _ in pool_eth:
        hourly[(ts_ - start) // 3600].append(p)
    eth_check = {'swaps': len(pool_eth), 'pools': sorted(verified_pools),
                 'hourly_median_usdc_per_weth': {str(h): str(Decimal(statistics.median(v)).quantize(Decimal('0.01'))) for h, v in sorted(hourly.items())},
                 'feed_hourly': {str(s['hour']): s['usd'] for s in (json.loads((out / 'prices.json').read_text()).get('hourly', {}).get('ETH', []) if (out / 'prices.json').exists() else [])}}
    pcs = sorted(Decimal(r['pc']) for r in big)
    stats = {'generated_at': utc(), 'day': str(day.relative_to(ROOT)) if day.is_relative_to(ROOT) else str(day), 'window': {'start_utc': manifest['start_utc'], 'end_utc': manifest['end_utc'],
             'first_block': blocks[0]['number'], 'last_block': blocks[-1]['number']}, 'threshold_usd': str(thr), 'counts': dict(counts),
             'above_threshold': len(big), 'above_100k': sum(1 for p in pcs if p >= 100000), 'above_1m': sum(1 for p in pcs if p >= 1000000),
             'selection_counts': dict(collections.Counter(key for r in big for key in r['selection'])),
             'selection_rule': 'pc >= threshold OR event-supported flash principal >= threshold OR gross >= 10 * threshold',
             'above_10m': sum(1 for p in pcs if p >= 10000000), 'sum_position_change_above_threshold_usd': str(q2(sum(pcs))),
             'p50_above_threshold': str(pcs[len(pcs) // 2]) if pcs else None, 'p99_above_threshold': str(pcs[len(pcs) * 99 // 100]) if pcs else None,
             'max_position_change': str(pcs[-1]) if pcs else None, 'interesting_addresses': len(addresses),
             'prices_used': prices.used(), 'price_meta': prices.meta, 'implied_prices': implied, 'eth_in_sample': eth_check,
             'registry': {a: {'label': s, 'decimals': d, 'price_key': k} for a, (s, d, k) in ASSETS.items()},
             'implied_price_rule': 'token outside the registry with at least ' + str(args.implied_min_swaps) + ' single-token-in single-token-out swaps '
                                   'against a priced asset and at least $' + str(args.implied_min_volume) + ' of priced volume; price is the median per unit at 18 decimals. '
                                   'A leg valued this way equals (leg raw amount / swap raw amount) times the swap USD, so the USD does not depend on the assumed decimals; only displayed token amounts do',
             'flash_loan_rule': 'ERC-20 legs A->B of X and B->A of Y>=X on the same asset inside one transaction, borrow first, X >= $1,000',
             'sandwich_rule': 'same block, same pool: actor swaps in direction d at index i, a stranger swaps in direction d at k, the actor swaps -d at j>k'}
    save(out / 'stats.json', stats)
    print(json.dumps({'blocks': counts['blocks'], 'transactions': counts['transactions'], 'above_threshold': len(big), 'addresses_profiled': len(addresses),
                      'implied_priced_tokens': len(implied), 'sum_above_threshold': stats['sum_position_change_above_threshold_usd']}, indent=2))


# ---------------------------------------------------------------- classify
class Ctx:
    """What a rule can see for one transaction above the threshold."""
    ZERO = ZERO

    def __init__(self, r, profiles, thr):
        self.r, self.thr = r, thr
        self.flash = Decimal(r['flash_usd'])
        self.assets = set(r['assets'])
        self.fnet = {k: Decimal(v) for k, v in r['fnet'].items()}
        self.tnet = {k: Decimal(v) for k, v in r['tnet'].items()}
        if self.fnet:
            self.principal, self.pnet = r['from'], self.fnet
        elif self.tnet:
            self.principal, self.pnet = r['to'], self.tnet
        else:
            self.principal, self.pnet = (r['lg']['addr'] if r['lg'] else r['from']), {}
        self.from_tags = REG.actor_tags(profiles.get(r['from']))
        self.to_tags = REG.actor_tags(profiles.get(r['to'])) if r['to'] else set()
        big = max((l for l in r['legs'] if l['usd'] is not None), key=lambda l: Decimal(l['usd']), default=None)
        self.cp = None
        if big:
            self.cp = big['r'] if big['f'] == self.principal else big['f']
        self.cp_tags = REG.actor_tags(profiles.get(self.cp)) if self.cp else set()
        legs = r['legs']
        self.plain = ((int(r['v']) > 0 and r['lc'] == 0 and r['cd'] == 0) or
                      (r['sel'] == '0xa9059cbb' and r['lc'] == 1 and len(legs) == 1 and legs[0]['k'] == 'erc20' and int(r['v']) == 0))
        self.custom_emitters = {a for a, _, _ in r.get('unk', [])} | {a for f, es in r.get('event_emitters', {}).items() if f.startswith('G') or f == 'DSNote' for a in es}
        self.erc20_legs = [l for l in legs if l['k'] == 'erc20' and l['usd'] is not None]
        self.legs_out_of_to = [l for l in self.erc20_legs if r['to'] and l['f'] == r['to']]
        self.legs_into_to = [l for l in self.erc20_legs if r['to'] and l['r'] == r['to']]
        self.legs_third_party = [l for l in self.erc20_legs if l['f'] not in (r['from'], r['to'], ZERO) and l['r'] not in (r['to'], ZERO)]
        self.transfers_only = set(r['fam']) <= {'ERC20_Transfer_shape', 'Approval', 'LidoTransferShares', 'WETHDeposit', 'WETHWithdrawal', 'unknown', 'anonymous', 'DSNote',
                                                'PermitTransfer', 'USDCMint', 'USDCBurn', 'TetherIssue', 'TetherRedeem', 'ERC777Sent', 'ERC721_Transfer_shape'} | {f for f in r['fam'] if f.startswith('G')}
        self.unpriced_minted, self.unpriced_burned = set(), set()
        for tok, v in r['unp'].items():
            for _, snd, rec, raw in v[2]:
                if int(raw) and snd == ZERO:
                    self.unpriced_minted.add(rec)
                if int(raw) and rec == ZERO:
                    self.unpriced_burned.add(snd)
        self.wrap_legs = [l for l in legs if l['k'] == 'wrap']
        self.unwrap_legs = [l for l in legs if l['k'] == 'unwrap']
        signs = collections.defaultdict(set)
        for who, _, _, _, u in r['net']:
            if who != ZERO and who != r['to'] and Decimal(u):
                signs[who].add(Decimal(u) > 0)
        self.two_sided_parties = {who for who, ss in signs.items() if len(ss) == 2}

    def has(self, *fams):
        return any(f in self.r['fam'] for f in fams)

    def has_at(self, address, *fams):
        return any(address in self.r.get('event_emitters', {}).get(f, []) for f in fams)

    @staticmethod
    def two_sided(net):
        return any(v < 0 for v in net.values()) and any(v > 0 for v in net.values())

    def legs_only(self, kinds):
        return bool(self.r['legs']) and {l['k'] for l in self.r['legs']} <= kinds


def classify_row(r, profiles, thr):
    c = Ctx(r, profiles, thr)
    matches = []
    for t in REG.TYPES:
        try:
            if t['rule'](c):
                matches.append(t['id'])
        except Exception as exc:  # a rule that errors must not hide a transaction
            r.setdefault('rule_errors', []).append(t['id'] + ': ' + type(exc).__name__)
    r['matching_types'] = matches
    return (matches[0] if matches else 'unknown'), c


def quantiles(vals):
    vs = sorted(vals)
    if not vs:
        return {}
    pick = lambda q: str(q2(vs[min(len(vs) - 1, int(q * len(vs)))]))
    return {'n': len(vs), 'min': str(q2(vs[0])), 'p25': pick(.25), 'p50': pick(.5), 'p75': pick(.75), 'p90': pick(.9), 'max': str(q2(vs[-1])), 'sum': str(q2(sum(vs)))}


def example(r, c=None):
    return {'hash': r['h'], 'block': r['b'], 'index': r['i'], 'utc': utc(r['t']), 'from': r['from'], 'to': r['to'], 'selector': r['sel'],
            'position_change_usd': r['pc'], 'largest': (r['lg']['s'] + ' at ' + short(r['lg']['addr'])) if r['lg'] else None, 'gross_usd': r['gross']}


def method_generic(rows, ctxs, start, thr):
    pcs = [Decimal(r['pc']) for r in rows]
    hours = collections.Counter((r['t'] - start) // 3600 for r in rows)
    top = sorted(rows, key=lambda r: -Decimal(r['pc']))[:6]
    return {'transactions': len(rows), 'position_change': quantiles(pcs), 'gross_priced_usd': str(q2(sum(Decimal(r['gross']) for r in rows))),
            'distinct_senders': len({r['from'] for r in rows}), 'distinct_principals': len({c.principal for c in ctxs}),
            'distinct_destinations': len({r['to'] for r in rows}),
            'by_asset': [{'asset': s, 'transactions': n, 'sum_usd': str(q2(u))} for s, (n, u) in
                         sorted(collections.Counter(), key=lambda x: x)] if False else
            [{'asset': s, 'transactions': v[0], 'sum_usd': str(q2(v[1]))} for s, v in sorted(
                {k: v for k, v in ((s, [sum(1 for r in rows if r['lg'] and r['lg']['s'] == s), sum(Decimal(r['pc']) for r in rows if r['lg'] and r['lg']['s'] == s)])
                                   for s in {r['lg']['s'] for r in rows if r['lg']})}.items(), key=lambda kv: -kv[1][1])[:8]],
            'hourly': [hours.get(h, 0) for h in range(WINDOW_HOURS)], 'top_destinations': [{'to': a, 'transactions': n} for a, n in collections.Counter(r['to'] for r in rows).most_common(5)],
            'examples': [example(r) for r in top]}


def method_transfer(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    buckets = collections.Counter()
    for r in rows:
        p = Decimal(r['pc'])
        buckets['10k-100k' if p < 100000 else '100k-1M' if p < 1000000 else '1M-10M' if p < 10000000 else '10M+'] += 1
    m.update(size_buckets=dict(buckets), fresh_sender=sum('fresh' in c.from_tags for c in ctxs), fresh_counterparty=sum('fresh' in c.cp_tags for c in ctxs),
             native=sum(1 for r in rows if int(r['v']) > 0 and r['lc'] == 0), token=sum(1 for r in rows if r['lc'] == 1),
             top_recipients=[{'address': a, 'transactions': n, 'sum_usd': str(q2(u))} for a, (n, u) in sorted(
                 {a: [sum(1 for c in ctxs if c.cp == a), sum(Decimal(c.r['pc']) for c in ctxs if c.cp == a)] for a in {c.cp for c in ctxs if c.cp}}.items(),
                 key=lambda kv: -kv[1][1])[:8]])
    return m


def method_exchange(rows, ctxs, start, thr):
    m = method_transfer(rows, ctxs, start, thr)
    wallets = collections.defaultdict(lambda: {'in': Decimal(0), 'out': Decimal(0), 'n': 0, 'assets': collections.Counter()})
    hourly = collections.defaultdict(Decimal)
    for r, c in zip(rows, ctxs):
        ex_from, ex_to = c.from_tags & REG.EXCHANGE, c.cp_tags & REG.EXCHANGE
        p = Decimal(r['pc'])
        sym = r['lg']['s'] if r['lg'] else '?'
        if ex_from and not ex_to:
            w = wallets[r['from']]
            w['out'] += p
            hourly[(r['t'] - start) // 3600] -= p
        elif ex_to and not ex_from:
            w = wallets[c.cp]
            w['in'] += p
            hourly[(r['t'] - start) // 3600] += p
        else:
            w = wallets[r['from']]
            w['out'] += p
        w['n'] += 1
        w['assets'][sym] += 1
    m.update(wallets=[{'address': a, 'transactions': w['n'], 'in_usd': str(q2(w['in'])), 'out_usd': str(q2(w['out'])), 'net_usd': str(q2(w['in'] - w['out'])),
                       'assets': w['assets'].most_common(3)} for a, w in sorted(wallets.items(), key=lambda kv: -(kv[1]['in'] + kv[1]['out']))[:12]],
             hourly_net_inflow_usd=[str(q2(hourly.get(h, Decimal(0)))) for h in range(WINDOW_HOURS)],
             net_inflow_usd=str(q2(sum(hourly.values(), Decimal(0)))))
    return m


def method_flash(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    lenders = collections.defaultdict(lambda: [0, Decimal(0)])
    loans, profits, npools = [], [], []
    for r, c in zip(rows, ctxs):
        for f in r['flash']:
            lenders[f['lender']][0] += 1
            lenders[f['lender']][1] += Decimal(f['usd'])
            loans.append(Decimal(f['usd']))
        profits.append(sum(c.pnet.values(), Decimal(0)))
        npools.append(len(r.get('pool_ids', r['pools'])))
    m.update(lenders=[{'address': a, 'loans': n, 'sum_usd': str(q2(u))} for a, (n, u) in sorted(lenders.items(), key=lambda kv: -kv[1][1])[:8]],
             loan_size=quantiles(loans), principal_net=quantiles(profits), pools_per_tx=dict(collections.Counter(npools)),
             loan_assets=dict(collections.Counter(f['s'] for r in rows for f in r['flash']).most_common(6)),
             gross_ex_flash_usd=str(q2(sum(Decimal(r['gross_xf']) for r in rows))))
    return m


def method_sandwich(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    bots = collections.defaultdict(lambda: {'n': 0, 'profit': Decimal(0), 'victims': set()})
    pools = collections.Counter()
    for r, c in zip(rows, ctxs):
        b = bots[r['from']]
        b['n'] += 1
        b['profit'] += sum(c.pnet.values(), Decimal(0))
        for s in r.get('sw', []):
            if s['role'] in ('front', 'back'):
                b['victims'].add(s['victim'])
                pools[s['pool']] += 1
    m.update(bots=[{'address': a, 'legs': b['n'], 'victims': len(b['victims']), 'net_usd_over_legs': str(q2(b['profit']))}
                   for a, b in sorted(bots.items(), key=lambda kv: -kv[1]['n'])[:8]], pools=[{'pool': p, 'legs': n} for p, n in pools.most_common(8)],
             front_legs=sum(1 for r in rows for s in r.get('sw', []) if s['role'] == 'front'), back_legs=sum(1 for r in rows for s in r.get('sw', []) if s['role'] == 'back'))
    return m


def method_arbitrage(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    bots = collections.defaultdict(lambda: [0, Decimal(0)])
    for r, c in zip(rows, ctxs):
        bots[c.principal][0] += 1
        bots[c.principal][1] += sum(c.pnet.values(), Decimal(0))
    m.update(principal_net=quantiles([sum(c.pnet.values(), Decimal(0)) for c in ctxs]), pools_per_tx=dict(collections.Counter(len(r.get('pool_ids', r['pools'])) for r in rows)),
             bots=[{'address': a, 'transactions': n, 'net_usd': str(q2(u))} for a, (n, u) in sorted(bots.items(), key=lambda kv: -kv[1][0])[:8]])
    return m


def method_swap(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    pairs = collections.defaultdict(lambda: [0, Decimal(0)])
    sizes = []
    for r, c in zip(rows, ctxs):
        sold = [k for k, v in c.pnet.items() if v < 0]
        bought = [k for k, v in c.pnet.items() if v > 0]
        key = ('+'.join(sorted(sold)) or '?') + ' -> ' + ('+'.join(sorted(bought)) or '?')
        size = max([abs(v) for v in c.pnet.values()] or [Decimal(r['pc'])])
        pairs[key][0] += 1
        pairs[key][1] += size
        sizes.append(size)
    m.update(pairs=[{'pair': k, 'transactions': n, 'sum_usd': str(q2(u))} for k, (n, u) in sorted(pairs.items(), key=lambda kv: -kv[1][1])[:10]],
             size=quantiles(sizes), routers=[{'to': a, 'transactions': n} for a, n in collections.Counter(r['to'] for r in rows).most_common(8)],
             pools_per_tx=dict(sorted(collections.Counter(min(len(r.get('pool_ids', r['pools'])), 6) for r in rows).items())),
             sandwiched=sum(1 for r in rows if any(s['role'] == 'victim' for s in r.get('sw', []))))
    return m


def method_mint_burn(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    per = collections.defaultdict(lambda: [Decimal(0), Decimal(0), 0])
    for r in rows:
        for s, (a, b) in r['mb'].items():
            per[s][0] += Decimal(a)
            per[s][1] += Decimal(b)
            per[s][2] += 1
    m.update(by_token=[{'asset': s, 'minted_usd': str(q2(a)), 'burned_usd': str(q2(b)), 'net_usd': str(q2(a - b)), 'transactions': n}
                       for s, (a, b, n) in sorted(per.items(), key=lambda kv: -(kv[1][0] + kv[1][1]))])
    return m


def method_psm(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    d = collections.defaultdict(lambda: [0, Decimal(0)])
    for r, c in zip(rows, ctxs):
        sold = '+'.join(sorted(k for k, v in c.pnet.items() if v < 0)) or '?'
        bought = '+'.join(sorted(k for k, v in c.pnet.items() if v > 0)) or '?'
        d[sold + ' -> ' + bought][0] += 1
        d[sold + ' -> ' + bought][1] += Decimal(r['pc'])
    m.update(directions=[{'direction': k, 'transactions': n, 'sum_usd': str(q2(u))} for k, (n, u) in sorted(d.items(), key=lambda kv: -kv[1][1])])
    return m


def method_bridge(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    fams = collections.defaultdict(lambda: [0, Decimal(0)])
    for r in rows:
        for f in r['fam']:
            if f in REG.BRIDGE_OUT or f in REG.BRIDGE_IN:
                fams[f][0] += 1
                fams[f][1] += Decimal(r['pc'])
    m.update(by_family=[{'family': f, 'transactions': n, 'sum_usd': str(q2(u))} for f, (n, u) in sorted(fams.items(), key=lambda kv: -kv[1][1])])
    return m


def method_lending(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    ops = collections.defaultdict(lambda: [0, Decimal(0)])
    for r in rows:
        f = next((f for f in ('AaveSupply', 'AaveBorrow', 'AaveRepay', 'AaveWithdraw', 'AaveLiquidation', 'MorphoSupply', 'MorphoWithdraw', 'MorphoBorrow',
                              'MorphoRepay', 'MorphoSupplyCollateral', 'MorphoWithdrawCollateral', 'MorphoLiquidate', 'CompoundV3Supply', 'CompoundV3Withdraw',
                              'CompoundV3SupplyCollateral', 'CompoundV3WithdrawCollateral', 'SparkSupply') if f in r['fam']), '?')
        sym = r['lg']['s'] if r['lg'] else '?'
        ops[f + ' ' + sym][0] += 1
        ops[f + ' ' + sym][1] += Decimal(r['pc'])
    m.update(operations=[{'operation': k, 'transactions': n, 'sum_usd': str(q2(u))} for k, (n, u) in sorted(ops.items(), key=lambda kv: -kv[1][1])[:12]])
    return m


def method_custody_flow(rows, ctxs, start, thr):
    m = method_generic(rows, ctxs, start, thr)
    owners, recipients, directions = collections.Counter(), collections.Counter(), collections.Counter()
    different = 0
    samples = []
    for r in rows:
        out = collections.defaultdict(Decimal)
        for l in r['legs']:
            if l['usd'] is None or l['f'] in (None, ZERO) or l['r'] in (None, ZERO):
                continue
            out[l['f']] += Decimal(l['usd'])
            recipients[l['r']] += 1
            directions['from_called_contract' if l['f']==r['to'] else 'into_called_contract' if l['r']==r['to'] else 'third_party_to_third_party'] += 1
        owner = max(out, key=out.get) if out else None
        if owner:
            owners[owner] += 1
            different += owner != r['from']
        if len(samples)<6:
            samples.append({'hash':r['h'], 'gas_payer':r['from'], 'largest_observed_asset_sender':owner, 'called_contract':r['to']})
    m.update(owner_differs_from_gas_payer=different, leg_directions=dict(directions),
             asset_senders=owners.most_common(8), recipients=recipients.most_common(8), role_examples=samples)
    return m


def method_flash_lending(rows, ctxs, start, thr):
    m = method_flash(rows, ctxs, start, thr)
    m['operations'] = method_lending(rows, ctxs, start, thr)['operations']
    m['interpretation_limit'] = 'Cash deltas omit debt and collateral claims. They are not profit.'
    return m


def method_dolomite(rows, ctxs, start, thr):
    m = method_custody_flow(rows, ctxs, start, thr)
    updates = []
    for r in rows:
        logs = read_gz(ACTIVE_SAMPLE / 'raw' / 'logs' / (str(r['b']) + '.json.gz'))
        for l in logs:
            if l['transactionHash'] != r['h'] or l['address'].lower() != '0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d' or not l.get('topics') or l['topics'][0] != '0x2bad8bc95088af2c247b30fa2b2e6a0886f88625e0945cd3051008e0e270198f':
                continue
            data = l['data'][2:]
            if len(data) != 7*64 or len(l['topics']) != 2:
                raise ValueError('Unexpected Dolomite LogDeposit layout')
            w = [int(data[i:i+64],16) for i in range(0,len(data),64)]
            updates.append({'hash':r['h'], 'owner':topic_address(l['topics'][1]), 'account_number':str(w[0]), 'market_id':w[1],
                            'delta_wei_signed':str(w[3] if w[2] else -w[3]), 'new_principal_signed':str(w[5] if w[4] else -w[5]),
                            'asset_source':'0x'+data[6*64+24:7*64]})
    m['account_updates'] = updates
    m['resulting_account_states'] = dict(collections.Counter('debt_remaining' if int(u['new_principal_signed']) < 0 else 'zero_balance' if int(u['new_principal_signed']) == 0 else 'positive_balance' for u in updates))
    return m


def method_fee_split(rows, ctxs, start, thr):
    """Payment routers: fee share in basis points, main recipient, payer and fee-taker concentration."""
    m = method_custody_flow(rows, ctxs, start, thr)
    bps, takers, merchants, payers = [], collections.Counter(), collections.Counter(), collections.Counter()
    for r, c in zip(rows, ctxs):
        total_in = sum(Decimal(l['usd']) for l in c.legs_into_to)
        outs = collections.defaultdict(Decimal)
        for l in c.legs_out_of_to:
            outs[l['r']] += Decimal(l['usd'])
        if not outs or total_in <= 0:
            continue
        main = max(outs, key=outs.get)
        fee = total_in - outs[main]
        bps.append(fee / total_in * 10000)
        merchants[main] += 1
        for a in outs:
            if a != main:
                takers[a] += 1
        for l in c.legs_into_to:
            payers[l['f']] += 1
    m.update(fee_bps=quantiles(bps), fee_takers=takers.most_common(6), main_recipients=merchants.most_common(6), payers_distinct=len(payers),
             repeat_payers=sum(1 for _, n in payers.items() if n >= 3))
    return m


METHODS = {'generic': method_generic, 'fee_split': method_fee_split, 'transfer': method_transfer, 'exchange': method_exchange, 'flash_loan': method_flash, 'sandwich': method_sandwich,
           'custody_flow': method_custody_flow, 'flash_lending': method_flash_lending, 'dolomite': method_dolomite,
           'arbitrage': method_arbitrage, 'swap': method_swap, 'mint_burn': method_mint_burn, 'psm': method_psm, 'bridge': method_bridge, 'lending': method_lending}
IGNORE_SHAPE = {'ERC20_Transfer_shape', 'Approval', 'V2Sync', 'unknown', 'anonymous', 'Transfer_unrecognized_shape', 'DepositAU', 'WithdrawAU'}


def shape_of(r):
    return ','.join(sorted(f for f in r['fam'] if f not in IGNORE_SHAPE)) or ('value-only' if int(r['v']) > 0 and r['lc'] == 0 else 'transfers-only')


def novelty_shape(r):
    """Do not merge different unknown topics just because they share a router and selector."""
    unknown = ','.join(sorted({topic for _, topic, _ in r.get('unk', [])}))
    return shape_of(r) + ('; unknown=' + unknown if unknown else '')


def load_big(out):
    with gzip.open(out / 'txs_big.jsonl.gz', 'rt') as f:
        return [json.loads(l) for l in f]


def load_profiles(out):
    with gzip.open(out / 'addresses.json.gz', 'rt') as f:
        return json.load(f)


def classify(args):
    global WINDOW_HOURS, ACTIVE_SAMPLE
    out, day = Path(args.out), Path(args.day)
    ACTIVE_SAMPLE = day
    stats = json.loads((out / 'stats.json').read_text())
    manifest = json.loads((day / 'manifest.json').read_text())
    WINDOW_HOURS = (manifest['end_timestamp'] - manifest['start_timestamp'] + 3599) // 3600
    start, thr = manifest['start_timestamp'], Decimal(stats['threshold_usd'])
    rows, profiles = load_big(out), load_profiles(out)
    by_type, ctx_of = collections.defaultdict(list), {}
    for r in rows:
        tid, c = classify_row(r, profiles, thr)
        r['type'] = tid
        by_type[tid].append(r)
        ctx_of[r['h']] = c
    total_n, total_usd = len(rows), sum(Decimal(r['pc']) for r in rows)
    types_out = []
    for t in REG.TYPES:
        rs = by_type.get(t['id'], [])
        entry = {k: t[k] for k in ('id', 'group', 'name', 'what', 'rule_text', 'method', 'origin', 'quant_notes')}
        entry.update(transactions=len(rs), sum_usd=str(q2(sum(Decimal(r['pc']) for r in rs))),
                     share_count_pct=round(100 * len(rs) / total_n, 2) if total_n else 0,
                     share_usd_pct=round(float(100 * sum(Decimal(r['pc']) for r in rs) / total_usd), 2) if total_usd else 0)
        if rs:
            entry['investigation'] = METHODS[t['method']](rs, [ctx_of[r['h']] for r in rs], start, thr)
        types_out.append(entry)
    unknown = by_type.get('unknown', [])
    clusters = collections.defaultdict(list)
    for r in unknown:
        clusters[(r['to'] or 'create', r['sel'], novelty_shape(r))].append(r)
    cl = []
    for (to, sel, shape), rs in clusters.items():
        rs.sort(key=lambda r: -Decimal(r['pc']))
        cl.append({'id': hashlib.sha256((to + sel + shape).encode()).hexdigest()[:10], 'to': to, 'selector': sel, 'shape': shape, 'transactions': len(rs),
                   'sum_usd': str(q2(sum(Decimal(r['pc']) for r in rs))), 'senders': len({r['from'] for r in rs}),
                   'assets': dict(collections.Counter(r['lg']['s'] for r in rs if r['lg']).most_common(3)), 'representative': rs[0]['h'],
                   'examples': [r['h'] for r in rs[:4]], 'rows': rs})
    by_count = sorted(cl, key=lambda c: (-c['transactions'], c['id']))
    by_usd = sorted(cl, key=lambda c: (-Decimal(c['sum_usd']), c['id']))
    chosen, reasons = [], {}
    for rank, c in enumerate(by_count[:args.top], 1):
        reasons.setdefault(c['id'], []).append({'metric': 'residue cluster size', 'rank': rank})
        if c['id'] not in [x['id'] for x in chosen]:
            chosen.append(c)
    for rank, c in enumerate(by_usd[:args.top], 1):
        reasons.setdefault(c['id'], []).append({'metric': 'residue cluster USD', 'rank': rank})
        if c['id'] not in [x['id'] for x in chosen]:
            chosen.append(c)
    rest = sorted([c for c in cl if c['id'] not in reasons], key=lambda c: hashlib.sha256(c['id'].encode()).hexdigest())
    for rank, c in enumerate(rest[:args.controls], 1):
        reasons[c['id']] = [{'metric': 'control', 'rank': rank, 'note': 'hash-sampled residue cluster'}]
        chosen.append(c)
    if args.audit_known:
        for tid, rs in sorted(by_type.items()):
            if tid == 'unknown':
                continue
            r = min(rs, key=lambda r: hashlib.sha256(r['h'].encode()).hexdigest())
            c = {'id': 'audit-' + tid, 'to': r['to'], 'selector': r['sel'], 'shape': shape_of(r), 'transactions': len(rs),
                 'sum_usd': str(q2(sum(Decimal(x['pc']) for x in rs))), 'senders': len({x['from'] for x in rs}),
                 'assets': {}, 'representative': r['h'], 'examples': [r['h']], 'rows': [r]}
            reasons[c['id']] = [{'metric': 'known type audit', 'type': tid}]
            chosen.append(c)
    # evidence packets for the representatives, read from the raw blocks
    need = collections.defaultdict(list)
    for c in chosen:
        need[c['rows'][0]['b']].append((c['rows'][0], c))
    packets = []
    for b, items in sorted(need.items()):
        block = read_gz(day / 'raw' / 'blocks' / (str(b) + '.json.gz'))
        logs = read_gz(day / 'raw' / 'logs' / (str(b) + '.json.gz'))
        txs = {t['hash']: t for t in block['transactions']}
        for r, c in items:
            packets.append(build_packet(r, c, reasons[c['id']], block, txs[r['h']], [l for l in logs if l['transactionHash'] == r['h']], ctx_of[r['h']], profiles, stats))
    packets.sort(key=lambda p: (p['transaction']['block'], p['transaction']['index']))
    coverage = {'transactions': total_n, 'sum_usd': str(q2(total_usd)), 'classified': total_n - len(unknown), 'classified_usd': str(q2(total_usd - sum(Decimal(r['pc']) for r in unknown))),
                'coverage_count_pct': round(100 * (total_n - len(unknown)) / total_n, 2) if total_n else 0,
                'coverage_usd_pct': round(float(100 * (total_usd - sum(Decimal(r['pc']) for r in unknown)) / total_usd), 2) if total_usd else 0,
                'unknown': len(unknown), 'unknown_usd': str(q2(sum(Decimal(r['pc']) for r in unknown))), 'residue_clusters': len(cl), 'types_in_registry': len(REG.TYPES),
                'types_with_occurrences': sum(1 for t in types_out if t['transactions'])}
    groups = collections.defaultdict(lambda: [0, Decimal(0)])
    for t in types_out:
        groups[t['group']][0] += t['transactions']
        groups[t['group']][1] += Decimal(t['sum_usd'])
    groups['unknown'] = [len(unknown), sum(Decimal(r['pc']) for r in unknown)]
    rule_errors = collections.Counter(e for r in rows for e in r.get('rule_errors', []))
    save(out / 'classified.json', {'generated_at': utc(), 'threshold_usd': str(thr), 'coverage': coverage,
                                    'multiple_matches': sum(len(r.get('matching_types', [])) > 1 for r in rows),
                                    'groups': [{'group': g, 'transactions': n, 'sum_usd': str(q2(u))} for g, (n, u) in sorted(groups.items(), key=lambda kv: -kv[1][1])],
                                    'types': types_out, 'rule_errors': dict(rule_errors), 'actor_tag_counts': dict(collections.Counter(t for c in ctx_of.values() for t in c.from_tags | c.cp_tags))})
    save(out / 'residue.json', {'generated_at': utc(), 'clusters': [{k: v for k, v in c.items() if k != 'rows'} for c in by_count],
                                'top_by_usd': [c['id'] for c in by_usd], 'selected': [c['id'] for c in chosen]})
    save(out / 'packets.json', packets)
    typed = {r['h']: r['type'] for r in rows}
    with gzip.open(out / 'types_by_hash.json.gz', 'wt') as f:
        json.dump(typed, f, separators=(',', ':'))
    with gzip.open(out / 'all_matches_by_hash.json.gz', 'wt') as f:
        json.dump({r['h']: r.get('matching_types', []) for r in rows}, f, separators=(',', ':'))
    with gzip.open(out / 'investigations.jsonl.gz', 'wt') as f:
        for r in rows:
            c = ctx_of[r['h']]
            t = REG.by_id().get(r['type'])
            record = {'hash': r['h'], 'block': r['b'], 'type': r['type'], 'method': t['method'] if t else 'llm_queue',
                      'matching_types': r['matching_types'], 'status': r['status'], 'selection': r['selection'],
                      'position_change_usd': r['pc'], 'gross_usd': r['gross'], 'gross_ex_flash_usd': r['gross_xf'],
                      'gross_to_position_ratio': str(q2(Decimal(r['gross']) / Decimal(r['pc']))) if Decimal(r['pc']) else None,
                      'principal': c.principal, 'principal_observed_net_usd': {k: str(v) for k, v in c.pnet.items()},
                      'events': r['fam'], 'event_emitters': r.get('event_emitters', {}), 'flash': r['flash'], 'mint_burn': r['mb'],
                      'swaps': r['swaps'], 'pools': r.get('pool_ids', r['pools']), 'unpriced_tokens': list(r['unp']),
                      'semantic_status': 'unknown' if not t else 'rule_match_not_validated_intent'}
            f.write(json.dumps(record, separators=(',', ':')) + '\n')
    rounds_path = out / 'rounds.json'
    rounds = json.loads(rounds_path.read_text()) if rounds_path.exists() else []
    rounds.append({'round': len(rounds) + 1, 'at': utc(), 'label': args.label,
                   'registry_sha256': hashlib.sha256(Path(REG.__file__).read_bytes()).hexdigest(),
                   'code_sha256': {name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
                                   for name in ('tx_types.py', 'type_registry.py', 'signatures.py', 'analyze_onchain.py')}, **coverage})
    save(rounds_path, rounds)
    import shutil
    archive = out / ('round_' + str(len(rounds)).zfill(2))
    archive.mkdir(exist_ok=True)
    for name in ('tx_types.py', 'signatures.py', 'analyze_onchain.py'):
        shutil.copy2(Path(__file__).parent / name, archive / name)
    for name in ('classified.json', 'residue.json', 'packets.json', 'types_by_hash.json.gz'):
        shutil.copy2(out / name, archive / name)
    shutil.copy2(Path(REG.__file__), archive / 'type_registry.py')
    print(json.dumps({'coverage': coverage, 'packets': len(packets), 'round': len(rounds)}, indent=2))


def event_view(l):
    d = decode(l)
    fam = log_family(l)
    if d['family'] == 'unknown':
        d = {'family': fam}
    e = {'log_index': hx(l['logIndex']), 'emitter': l['address'].lower(), 'topic0': l['topics'][0] if l.get('topics') else None, **d}
    if e['family'] == 'ERC20_Transfer_shape' and e['emitter'] in ASSETS:
        e['symbol'] = ASSETS[e['emitter']][0]
        e['amount'] = amount(int(e['amount_raw']), ASSETS[e['emitter']][1])
    return e


def profile_view(profiles, a):
    p = profiles.get(a)
    if not p:
        return None
    v = {k: p[k] for k in ('sent', 'to_distinct', 'nonce_min', 'nonce_max', 'tip_median_gwei', 'hours_active', 'touched', 'as_to', 'in_from_distinct',
                           'out_to_distinct', 'big', 'big_usd', 'swaps_as_to', 'pool_swaps', 'flash_lent_usd', 'native_sent_usd', 'selectors')}
    v['net'], v['gross'] = p['net'], p['gross']
    v['tags'] = sorted(REG.actor_tags(p))
    return v


def build_packet(r, cluster, reasons, block, tx, logs, c, profiles, stats):
    events = [event_view(l) for l in logs]
    unknown_topics = collections.Counter((e['emitter'], e['topic0']) for e in events if e['family'] == 'unknown')
    miner = (block.get('miner') or '').lower()
    return {'episode_id': CHAIN + ':' + block['hash'] + ':' + r['h'], 'explorer_tx': EXPLORER + '/tx/' + r['h'], 'selection_reasons': reasons,
            'cluster': {k: v for k, v in cluster.items() if k not in ('rows', 'representative')} | {'other_examples': [x['h'] for x in cluster['rows'][1:4]]},
            'transaction': {'block': r['b'], 'index': r['i'], 'of': len(block['transactions']), 'utc': utc(r['t']), 'hash': r['h'], 'type': r['ty'], 'from': r['from'],
                            'to': r['to'], 'created': r['created'], 'nonce': r['n'], 'selector': r['sel'], 'calldata_bytes': r['cd'],
                            'calldata_prefix': tx.get('input', '0x')[:10 + 192], 'value_eth': str(Decimal(r['v']) / Decimal(10 ** 18)), 'gas_limit': r['gl'],
                            'effective_gas_price_gwei': str(Decimal(r['eff']) / Decimal(10 ** 9)), 'priority_fee_gwei': str(Decimal(r['tip']) / Decimal(10 ** 9)),
                            'authorization_list_len': r['auth'], 'blobs': r['blobs'], 'log_count': r['lc']},
            'facts': {'position_change_usd': r['pc'], 'largest': r['lg'], 'gross_usd': r['gross'], 'gross_ex_flash_usd': r['gross_xf'], 'flash_usd': r['flash_usd'],
                      'flash': r['flash'], 'native_usd': r['native_usd'], 'swaps': r['swaps'], 'pools': r.get('pool_ids', r['pools']), 'distinct_recipients': r['rcpt'],
                      'mint_burn': r['mb'], 'from_net': r['fnet'], 'to_net': r['tnet'], 'principal': c.principal, 'counterparty': c.cp, 'sandwich': r.get('sw'),
                      'shape': shape_of(r), 'assets': r['assets'], 'erc721_transfers': r['rc721'], 'erc1155_transfers': r['rc1155'], 'revalued': r.get('revalued', False)},
            'legs': r['legs'][:24], 'legs_truncated': max(0, len(r['legs']) - 24), 'net_flows': r['net'][:12],
            'unpriced': [{'token': a, 'transfers': v[0], 'largest_raw': v[1], 'sample': v[2][:3]} for a, v in sorted(r['unp'].items(), key=lambda kv: -kv[1][0])[:6]],
            'events': {'families': r['fam'], 'sample': events[:20], 'truncated': max(0, len(events) - 20),
                       'unknown_topics': [{'emitter': a, 'topic0': t, 'count': n} for (a, t), n in unknown_topics.most_common(6)]},
            'actors': {'from': profile_view(profiles, r['from']), 'from_tags': sorted(c.from_tags), 'to': profile_view(profiles, r['to']) if r['to'] else None,
                       'to_tags': sorted(c.to_tags), 'counterparty': profile_view(profiles, c.cp) if c.cp else None, 'counterparty_tags': sorted(c.cp_tags)},
            'block': {'miner': miner, 'extra_data_text': extra_text(block.get('extraData', '0x')), 'transactions': len(block['transactions']),
                      'gas_utilization': round(hx(block['gasUsed']) / hx(block['gasLimit']), 4), 'base_fee_gwei': str(Decimal(hx(block.get('baseFeePerGas', 0))) / Decimal(10 ** 9))},
            'missing': ['receipt status and gas used (resolve fetches them for packets)', 'internal calls and contract-moved ETH', 'prices for unpriced tokens',
                        'verified contract identity (resolve fetches code presence)']}


# ---------------------------------------------------------------- resolve
DESIGNATOR = re.compile(r'^0xef0100([0-9a-f]{40})$')


def resolve(args):
    out, day = Path(args.out), Path(args.day)
    manifest = json.loads((day / 'manifest.json').read_text())
    packets = json.loads((out / 'packets.json').read_text())
    stats = json.loads((out / 'stats.json').read_text())
    ctx_path = out / 'context.json'
    ctx = json.loads(ctx_path.read_text()) if ctx_path.exists() else {'receipts': {}, 'code': {}, 'tokens': {}, 'asof': {}}
    rpc = RPC(out, key_index=manifest.get('key_index', 0), max_credits=args.max_credits, interval=.3)
    pin = hex(stats['window']['last_block'])
    ctx['asof'].setdefault('pinned_block', stats['window']['last_block'])
    hashes = [p['transaction']['hash'] for p in packets if p['transaction']['hash'] not in ctx['receipts']] + [h for h in args.hashes if h not in ctx['receipts']]
    for i in range(0, len(hashes), 10):
        part = hashes[i:i + 10]
        vals = rpc.batch(CHAIN, [('eth_getTransactionReceipt', [h]) for h in part], allow_errors=True)
        for h, v in zip(part, vals):
            if isinstance(v, dict) and 'status' in v:
                ctx['receipts'][h] = {'status_ok': hx(v['status']) == 1, 'gas_used': hx(v['gasUsed']), 'effective_gas_price_wei': hx(v.get('effectiveGasPrice', 0)),
                                      'contract_address': (v.get('contractAddress') or '').lower() or None, 'logs': len(v.get('logs', []))}
            else:
                ctx['receipts'][h] = {'error': str(v)[:200]}
    addresses = set()
    tokens = collections.Counter()
    for p in packets:
        addresses.update(a for a in [p['transaction']['from'], p['transaction']['to'], p['transaction']['created'], p['facts']['counterparty'], p['facts']['principal']] if a)
        addresses.update(f[0] for f in p['net_flows'][:4])
        for u in p['unpriced']:
            tokens[u['token']] += u['transfers']
        for l in p['legs']:
            if l['key'].startswith('IMPL:'):
                tokens[l['a']] += 1
    for t in list(stats.get('implied_prices', {}))[:args.max_tokens]:
        tokens[t] += 1
    for t in args.tokens:
        tokens[t.lower()] += 1000
    addresses.update(a.lower() for a in args.addresses)
    todo = sorted(a for a in addresses if a not in ctx['code'] and a != ZERO)
    for i in range(0, len(todo), 10):
        part = todo[i:i + 10]
        vals = rpc.batch(CHAIN, [('eth_getCode', [a, pin]) for a in part], allow_errors=True)
        for a, v in zip(part, vals):
            if isinstance(v, str):
                m, d = MINIMAL_PROXY.match(v), DESIGNATOR.match(v)
                ctx['code'][a] = {'code_bytes': (len(v) - 2) // 2, 'is_contract': len(v) > 2 and not d, 'eip7702_delegate': ('0x' + d.group(1)) if d else None,
                                  'minimal_proxy_target': ('0x' + m.group(1)) if m else None}
            else:
                ctx['code'][a] = {'error': str(v)[:200]}
    for t in [t for t, _ in tokens.most_common(args.max_tokens) if t not in ctx['tokens']]:
        calls = [('eth_call', [{'to': t, 'data': sel4('symbol()')}, pin]), ('eth_call', [{'to': t, 'data': sel4('decimals()')}, pin]), ('eth_call', [{'to': t, 'data': sel4('name()')}, pin])]
        vals = rpc.batch(CHAIN, calls, allow_errors=True)
        entry = {'symbol_untrusted': decode_string(vals[0]) if isinstance(vals[0], str) else None,
                 'decimals': hx(vals[1]) if isinstance(vals[1], str) and len(vals[1]) == 66 else None,
                 'name_untrusted': decode_string(vals[2]) if isinstance(vals[2], str) else None}
        if t in ASSETS:
            entry.update(registry_label=ASSETS[t][0], registry_decimals=ASSETS[t][1], symbol_matches_registry=(entry['symbol_untrusted'] or '').lower() == ASSETS[t][0].lower(),
                         decimals_match_registry=entry['decimals'] == ASSETS[t][1])
        ctx['tokens'][t] = entry
    ctx['asof']['observed_at'] = utc()
    save(ctx_path, ctx)
    print(json.dumps({'receipts': len(ctx['receipts']), 'code': len(ctx['code']), 'tokens': len(ctx['tokens']), 'credits': rpc.credits,
                      'designators': [a for a, v in ctx['code'].items() if v.get('eip7702_delegate')],
                      'registry_mismatches': [(a, v['registry_label'], v['symbol_untrusted'], v['decimals']) for a, v in ctx['tokens'].items()
                                              if 'registry_label' in v and not (v['symbol_matches_registry'] and v['decimals_match_registry'])]}))


# ---------------------------------------------------------------- render
def code_desc(ctx, a):
    code = ctx.get('code', {}).get(a or '', None)
    if not code:
        return 'unknown code status'
    if code.get('eip7702_delegate'):
        return 'an EOA delegated (EIP-7702) to ' + addr_link(code['eip7702_delegate'])
    if code.get('is_contract'):
        return 'a contract' + (' (minimal proxy to ' + addr_link(code['minimal_proxy_target']) + ')' if code.get('minimal_proxy_target') else '') + \
            ' of ' + f"{code['code_bytes']:,}" + ' bytes'
    return 'an EOA' if 'error' not in code else 'unknown code status'


def tok_label(ctx, a, fallback):
    t = ctx.get('tokens', {}).get(a, {})
    s = t.get('symbol_untrusted')
    return (s + ' (self-reported)') if s else fallback


def fmt_tags(tags):
    return ', '.join(tags) if tags else 'no tags'


def render(args):
    out, day = Path(args.out), Path(args.day)
    stats = json.loads((out / 'stats.json').read_text())
    cls = json.loads((out / 'classified.json').read_text())
    residue = json.loads((out / 'residue.json').read_text())
    packets = json.loads((out / 'packets.json').read_text())
    rounds = json.loads((out / 'rounds.json').read_text()) if (out / 'rounds.json').exists() else []
    ctx = json.loads((out / 'context.json').read_text()) if (out / 'context.json').exists() else {}
    manifest = json.loads((day / 'manifest.json').read_text())
    notes = parse_notes(out / 'qual_notes.md')
    thr = Decimal(stats['threshold_usd'])
    cov = cls['coverage']
    L = ['# Transaction types on Ethereum mainnet over the research window: a quant taxonomy grown by LLM investigation\n']
    hours = (manifest['end_timestamp'] - manifest['start_timestamp']) / 3600
    L.append('Ethereum only, ' + (f'{hours:g} hours' if hours != 24 else 'one full day (24 hours)') + '. The deterministic step (`replay/tx_types.py`) values successful logged native transfers, receipt-confirmed large no-log native transfers, every '
             'ERC-20 transfer of a registry token and every WETH wrap or unwrap in USD, nets them per address and asset inside each transaction, and calls a transaction '
             'large when one address changed one asset position by at least ' + usd(thr) + '. Supplemental candidates have event-supported flash principal at least that size or gross priced legs at least ten times that size. Every selected transaction is then typed by the rules in '
             '`replay/type_registry.py`: each type is a qualitative description of what happens, a quantitative rule that recognises it, and an investigation method '
             'that runs on every occurrence. Transactions no rule matches form the residue; the residue is clustered by destination, selector and event shape, and the '
             'LLM investigates the largest clusters, writes `qual_notes.md`, and adds rules. The registry after this pass holds ' + str(cov['types_in_registry']) +
             ' types. Numbers below are computed; prose marked LLM is interpretation with a stated confidence.\n')
    w = stats['window']
    L.append('Window: ' + manifest['start_utc'] + ' to ' + manifest['end_utc'] + ' (exclusive), blocks ' + f"{w['first_block']:,}" + ' to ' + f"{w['last_block']:,}" +
             ': ' + f"{stats['counts']['blocks']:,}" + ' blocks, ' + f"{stats['counts']['transactions']:,}" + ' transactions, ' + f"{stats['counts']['logs']:,}" +
             ' logs. Logs establish successful execution; receipts confirm every no-log native-value candidate above the threshold and the packet transactions. ' +
             f"{stats['above_threshold']:,}" + ' transactions pass the combined screen; ' + f"{stats['selection_counts'].get('pc', 0):,}" + ' have a position change at or above ' + usd(thr) + ' (' + f"{stats['above_100k']:,}" + ' at or above $100k, ' +
             f"{stats['above_1m']:,}" + ' at or above $1M, ' + f"{stats['above_10m']:,}" + ' at or above $10M), summing to ' + usd(stats['sum_position_change_above_threshold_usd']) +
             ' of largest position changes; the median large transaction is ' + usd(stats['p50_above_threshold']) + ' and the largest ' + usd(stats['max_position_change']) + '.\n')
    L.append('## Prices\n')
    L.append('| Key | USD | Source |')
    L.append('|---|---:|---|')
    for k, v in stats['prices_used'].items():
        if not k.startswith('IMPL:'):
            L.append('| ' + k + ' | ' + f"{Decimal(v['usd']):,.4f}" + ' | ' + v['source'] + ' |')
    L.append('')
    impl = stats.get('implied_prices', {})
    if impl:
        L.append(str(len(impl)) + ' tokens outside the registry were priced from their own swaps against priced assets (' + stats['implied_price_rule'] + '). ' +
                 'They are labelled IMPL in the tables; decimals are assumed to be 18, so a token with other decimals is mis-scaled until `resolve` reports it. ' +
                 'Largest by volume: ' + ', '.join(addr_link(a, tok_label(ctx, a, short(a))) + ' $' + f"{Decimal(e['usd_volume']):,.0f}" + ' over ' + str(e['swaps']) + ' swaps'
                                                  for a, e in sorted(impl.items(), key=lambda kv: -Decimal(kv[1]['usd_volume']))[:8]) + '.\n')
    ins = stats.get('eth_in_sample', {})
    if ins.get('swaps'):
        pairs = [(h, ins['hourly_median_usdc_per_weth'][h], ins['feed_hourly'].get(str(int(h) + 1))) for h in ins['hourly_median_usdc_per_weth']]
        devs = [abs(Decimal(m) / Decimal(f) - 1) * 10000 for _, m, f in pairs if f]
        L.append('Cross-check: ' + f"{ins['swaps']:,}" + ' V3 swaps in the two factory-verified USDC/WETH pools give hourly median prices whose deviation from the hourly feed reading is ' +
                 (f"{min(devs):.0f} to {max(devs):.0f} basis points" if devs else 'not computable') + '.\n')
    L.append('## The taxonomy after this pass\n')
    L.append('Coverage: ' + f"{cov['classified']:,}" + ' of ' + f"{cov['transactions']:,}" + ' large transactions (' + str(cov['coverage_count_pct']) + '%) and ' +
             usd(cov['classified_usd']) + ' of ' + usd(cov['sum_usd']) + ' (' + str(cov['coverage_usd_pct']) + '%) are typed; the residue is ' + f"{cov['unknown']:,}" +
             ' transactions in ' + f"{cov['residue_clusters']:,}" + ' clusters.\n')
    if rounds:
        L.append('| Round | Label | Types | Typed | Coverage by count | Coverage by USD | Residue clusters |')
        L.append('|---:|---|---:|---:|---:|---:|---:|')
        for r in rounds:
            L.append(f"| {r['round']} | {r.get('label') or ''} | {r['types_in_registry']} | {r['classified']:,} | {r['coverage_count_pct']}% | {r['coverage_usd_pct']}% | {r['residue_clusters']:,} |")
        L.append('')
    L.append('| Group | Transactions | Sum of largest changes |')
    L.append('|---|---:|---:|')
    for g in cls['groups']:
        L.append('| ' + g['group'] + f" | {g['transactions']:,} | " + usd(g['sum_usd']) + ' |')
    L.append('')
    L.append('| Type | Group | Txs | Share | Sum | Share of USD | Rule (quantitative) | Origin |')
    L.append('|---|---|---:|---:|---:|---:|---|---|')
    for t in sorted(cls['types'], key=lambda t: -Decimal(t['sum_usd'])):
        if t['transactions']:
            L.append('| ' + t['name'] + ' | ' + t['group'] + f" | {t['transactions']:,} | {t['share_count_pct']}% | " + usd(t['sum_usd']) + f" | {t['share_usd_pct']}% | " +
                     t['rule_text'] + ' | ' + t['origin'] + ' |')
    L.append('')
    zero = [t['name'] for t in cls['types'] if not t['transactions']]
    if zero:
        L.append('Registered types with no occurrence in this window: ' + ', '.join(zero) + '.\n')
    if cls.get('rule_errors'):
        L.append('Rule errors: ' + json.dumps(cls['rule_errors']) + '.\n')
    if 'synthesis' in notes:
        L.append('## What the window showed (LLM)\n')
        L.append(notes['synthesis']['body'] + '\n')
    L.append('## Known types, investigated with their known method\n')
    groups = collections.OrderedDict()
    for t in cls['types']:
        if t['transactions']:
            groups.setdefault(t['group'], []).append(t)
    for g, ts in groups.items():
        L.append('### ' + g.replace('_', ' ') + '\n')
        for t in ts:
            inv = t['investigation']
            L.append('#### ' + t['name'] + ' (' + f"{t['transactions']:,}" + ' transactions, ' + usd(t['sum_usd']) + ')\n')
            L.append('What happens: ' + t['what'] + '\n')
            L.append('Rule: ' + t['rule_text'] + '. Method: `' + t['method'] + '`. Origin: ' + t['origin'] + '.' + (' ' + t['quant_notes'] if t['quant_notes'] else '') + '\n')
            pcq = inv['position_change']
            L.append('Largest position change: median ' + usd(pcq['p50']) + ', p90 ' + usd(pcq['p90']) + ', max ' + usd(pcq['max']) + '. Gross priced volume ' + usd(inv['gross_priced_usd']) +
                     '. ' + f"{inv['distinct_senders']:,}" + ' distinct senders, ' + f"{inv['distinct_principals']:,}" + ' principals, ' + f"{inv['distinct_destinations']:,}" +
                     ' destinations. By asset of the largest position: ' + ', '.join(a['asset'] + ' ×' + str(a['transactions']) + ' (' + usd(a['sum_usd']) + ')' for a in inv['by_asset'][:5]) +
                     '. Hourly counts from the window start: ' + ' '.join(str(x) for x in inv['hourly']) + '.')
            extra = []
            if 'size_buckets' in inv:
                extra.append('Sizes: ' + ', '.join(f'{k} ×{v}' for k, v in inv['size_buckets'].items()) + '; native ×' + str(inv['native']) + ', token ×' + str(inv['token']) +
                             '; fresh sender in ' + str(inv['fresh_sender']) + ', fresh counterparty in ' + str(inv['fresh_counterparty']) + '.')
            if 'wallets' in inv:
                extra.append('Net inflow to exchange-tagged wallets over the window ' + usd(inv['net_inflow_usd']) + '; hourly: ' + ' '.join(usd(x) for x in inv['hourly_net_inflow_usd']) + '.')
                extra.append('Wallets: ' + '; '.join(addr_link(x['address']) + ' ' + str(x['transactions']) + ' txs, in ' + usd(x['in_usd']) + ', out ' + usd(x['out_usd']) +
                                                   ' (' + ', '.join(a + ' ×' + str(n) for a, n in x['assets']) + ')' for x in inv['wallets'][:8]) + '.')
            if 'top_recipients' in inv and inv['top_recipients']:
                extra.append('Top counterparties: ' + '; '.join(addr_link(x['address']) + ' ×' + str(x['transactions']) + ' ' + usd(x['sum_usd']) for x in inv['top_recipients'][:6]) + '.')
            if 'lenders' in inv:
                extra.append('Lenders: ' + '; '.join(addr_link(x['address']) + ' ' + str(x['loans']) + ' loans, ' + usd(x['sum_usd']) for x in inv['lenders']) + '. Loan size median ' +
                             usd(inv['loan_size'].get('p50', 0)) + ', max ' + usd(inv['loan_size'].get('max', 0)) + '; assets ' + ', '.join(f'{k} ×{v}' for k, v in inv['loan_assets'].items()) +
                             '. Principal net per transaction: median ' + usd(inv['principal_net'].get('p50', 0)) + ', p90 ' + usd(inv['principal_net'].get('p90', 0)) + ', sum ' +
                             usd(inv['principal_net'].get('sum', 0)) + '. Gross volume without the loan legs ' + usd(inv['gross_ex_flash_usd']) + '. Pools per transaction: ' +
                             ', '.join(f'{k}: {v}' for k, v in sorted(inv['pools_per_tx'].items(), key=lambda kv: int(kv[0]))) + '.')
            if 'bots' in inv and t['method'] == 'sandwich':
                extra.append('Bracketing senders: ' + '; '.join(addr_link(x['address']) + ' ' + str(x['legs']) + ' legs, ' + str(x['victims']) + ' intervening swaps, observed principal net ' + usd(x['net_usd_over_legs']) for x in inv['bots']) +
                             '. Pools: ' + '; '.join(addr_link(x['pool']) + ' ×' + str(x['legs']) for x in inv['pools'][:6]) + '.')
            if 'bots' in inv and t['method'] == 'arbitrage':
                extra.append('Principal net: median ' + usd(inv['principal_net'].get('p50', 0)) + ', p90 ' + usd(inv['principal_net'].get('p90', 0)) + ', sum ' + usd(inv['principal_net'].get('sum', 0)) +
                             '. Principals: ' + '; '.join(addr_link(x['address']) + ' ×' + str(x['transactions']) + ' observed net ' + usd(x['net_usd']) for x in inv['bots'][:6]) + '.')
            if 'pairs' in inv:
                extra.append('Pairs (sold -> bought): ' + '; '.join(x['pair'] + ' ×' + str(x['transactions']) + ' ' + usd(x['sum_usd']) for x in inv['pairs'][:8]) + '. Size median ' +
                             usd(inv['size'].get('p50', 0)) + ', p90 ' + usd(inv['size'].get('p90', 0)) + '. Destinations: ' + '; '.join(addr_link(x['to']) + ' ×' + str(x['transactions']) for x in inv['routers'][:6]) +
                             '. Pools per transaction: ' + ', '.join(f'{k}: {v}' for k, v in inv['pools_per_tx'].items()) + '. Inside a sandwich-pattern candidate: ' + str(inv['sandwiched']) + '.')
            if 'by_token' in inv:
                extra.append('By token: ' + '; '.join(x['asset'] + ' minted ' + usd(x['minted_usd']) + ', burned ' + usd(x['burned_usd']) + ', net ' + usd(x['net_usd']) + ' in ' + str(x['transactions']) + ' txs' for x in inv['by_token']) + '.')
            if 'directions' in inv:
                extra.append('Directions: ' + '; '.join(x['direction'] + ' ×' + str(x['transactions']) + ' ' + usd(x['sum_usd']) for x in inv['directions']) + '.')
            if 'by_family' in inv:
                extra.append('By event family: ' + '; '.join(x['family'] + ' ×' + str(x['transactions']) + ' ' + usd(x['sum_usd']) for x in inv['by_family']) + '.')
            if 'operations' in inv:
                extra.append('Operations: ' + '; '.join(x['operation'] + ' ×' + str(x['transactions']) + ' ' + usd(x['sum_usd']) for x in inv['operations']) + '.')
            if 'fee_bps' in inv and inv['fee_bps']:
                extra.append('Fee share: median ' + inv['fee_bps'].get('p50', '0') + ' bps, p90 ' + inv['fee_bps'].get('p90', '0') + ' bps over ' + str(inv['fee_bps'].get('n', 0)) +
                             ' routed payments; ' + str(inv['payers_distinct']) + ' distinct payers (' + str(inv['repeat_payers']) + ' paid three or more times). Fee takers: ' +
                             '; '.join(addr_link(a) + ' ×' + str(n) for a, n in inv['fee_takers'][:4]) + '. Main recipients: ' + '; '.join(addr_link(a) + ' ×' + str(n) for a, n in inv['main_recipients'][:4]) + '.')
            if 'owner_differs_from_gas_payer' in inv:
                extra.append('Largest observed asset sender differs from the gas payer in ' + str(inv['owner_differs_from_gas_payer']) + ' transactions. Transfer-leg directions: ' + json.dumps(inv['leg_directions']) + '.')
            if 'account_updates' in inv:
                extra.append('Decoded internal account updates: `' + json.dumps(inv['account_updates']) + '`. Principal units differ from token units because of interest indexing.')
            if inv['top_destinations'] and 'pairs' not in inv:
                extra.append('Top destinations: ' + '; '.join(addr_link(x['to']) + ' ×' + str(x['transactions']) for x in inv['top_destinations']) + '.')
            for e in extra:
                L.append('\n' + e)
            L.append('\nLargest examples: ' + '; '.join(tx_link(x['hash']) + ' ' + usd(x['position_change_usd']) + (' ' + x['largest'] if x['largest'] else '') for x in inv['examples']) + '.')
            key = 'type ' + t['id']
            if key in notes:
                L.append('\nLLM note on this type: ' + notes[key]['body'])
            L.append('')
    L.append('## Residue: what no rule matched, and what the LLM found\n')
    L.append(f"{cov['unknown']:,}" + ' transactions (' + usd(cov['unknown_usd']) + ') in ' + f"{cov['residue_clusters']:,}" + ' clusters keyed by destination, selector and event shape. Most frequent clusters:\n')
    L.append('| Cluster | Destination | Selector | Shape | Txs | Senders | Sum | Assets | Representative |')
    L.append('|---|---|---|---|---:|---:|---:|---|---|')
    for c in residue['clusters'][:25]:
        L.append('| ' + c['id'] + ' | ' + (addr_link(c['to']) if c['to'] != 'create' else 'creation') + ' | `' + c['selector'] + '` | ' + c['shape'][:80] + f" | {c['transactions']:,} | {c['senders']:,} | " +
                 usd(c['sum_usd']) + ' | ' + ', '.join(f'{k} ×{v}' for k, v in c['assets'].items()) + ' | ' + tx_link(c['representative']) + ' |')
    L.append('')
    conf = collections.Counter()
    n = 0
    is_audit = lambda p: any(r['metric'] == 'known type audit' for r in p['selection_reasons'])
    seen_hashes = {p['transaction']['hash'] for p in packets}
    earlier = []
    for rd in sorted(out.glob('round_*/packets.json')):
        for p in json.loads(rd.read_text()):
            h = p['transaction']['hash']
            if h not in seen_hashes and h.lower() in notes and not is_audit(p):
                p['_round'] = rd.parent.name
                earlier.append(p)
                seen_hashes.add(h)
    ordered = [p for p in packets if not is_audit(p)] + earlier + [p for p in packets if is_audit(p)]
    audit_started = earlier_started = False
    for p in ordered:
        if '_round' in p and not earlier_started:
            earlier_started = True
            L.append('## Residue of earlier rounds: the investigations that produced the new types\n')
            L.append('These packets were selected by earlier classify runs (archived under round_XX/) and are the evidence behind the types added on this run; '
                     'after the new rules they are no longer residue.\n')
        if is_audit(p) and not audit_started:
            audit_started = True
            L.append('## Known-type audit: hash-sampled occurrences reviewed at packet level\n')
            L.append('Each known type contributes one deterministic sample so that the rule can be checked against a transaction it matched, not only against the '
                     'transactions it was written for. A note that disagrees with the type is a correction request for the registry.\n')
        n += 1
        t, f, a = p['transaction'], p['facts'], p['actors']
        note = notes.get(t['hash'].lower(), {})
        rc = ctx.get('receipts', {}).get(t['hash'], {})
        label = ('A' if is_audit(p) else 'E' if '_round' in p else 'R') + str(n)
        L.append(f"### {label}. {tx_link(t['hash'])}: " + note.get('mechanism', 'not yet annotated') + (' (selected in ' + p['_round'] + ')' if '_round' in p else '') + '\n')
        reasons = ', '.join(r['metric'] + (' #' + str(r['rank']) if 'rank' in r else '') + (' (' + r['type'] + ')' if 'type' in r else '') for r in p['selection_reasons'])
        cl = p['cluster']
        facts = ('Selected for ' + reasons + '. Cluster ' + cl['id'] + ': ' + f"{cl['transactions']:,}" + ' transactions from ' + f"{cl['senders']:,}" + ' senders, ' + usd(cl['sum_usd']) +
                 ', shape ' + cl['shape'] + (', other examples ' + ' '.join(tx_link(h) for h in cl['other_examples']) if cl['other_examples'] else '') + '. ')
        facts += ('Block ' + f"{t['block']:,}" + ' at ' + t['utc'] + ', index ' + str(t['index']) + '/' + str(t['of']) + ', type ' + t['type'] + ', ' +
                  ('success' if rc.get('status_ok') else 'failed' if rc.get('status_ok') is False else 'status not fetched') + '. From ' + addr_link(t['from']) + ' (' + code_desc(ctx, t['from']) +
                  '; window profile: ' + fmt_tags(a['from_tags']) + (', ' + str(a['from']['sent']) + ' sent to ' + str(a['from']['to_distinct']) + ' destinations, nonce ' + f"{a['from']['nonce_min']:,}" +
                  ' to ' + f"{a['from']['nonce_max']:,}" if a['from'] and a['from']['sent'] else '') + ') to ' + (addr_link(t['to']) + ' (' + code_desc(ctx, t['to']) + '; ' + fmt_tags(a['to_tags']) +
                  (', called ' + str(a['to']['as_to']) + ' times in the window' if a['to'] else '') + ')' if t['to'] else 'creation of ' + addr_link(t['created'])) + '. Selector `' + t['selector'] + '`, calldata ' +
                  f"{t['calldata_bytes']:,}" + ' bytes, value ' + t['value_eth'] + ' ETH, ' + str(t['log_count']) + ' logs, tip ' + t['priority_fee_gwei'] + ' gwei' +
                  (', ' + str(t['authorization_list_len']) + ' authorizations' if t['authorization_list_len'] else '') + '. ')
        lg = f['largest']
        facts += ('Largest position change ' + usd(f['position_change_usd']) + (' (' + lg['s'] + ' at ' + addr_link(lg['addr']) + ')' if lg else '') + '; gross ' + usd(f['gross_usd']) +
                  (', flash-loan legs ' + usd(f['flash_usd']) if Decimal(f['flash_usd']) else '') + '; swaps ' + str(f['swaps']) + ' in ' + str(len(f['pools'])) + ' pools; ' +
                  str(f['distinct_recipients']) + ' distinct recipients. Principal ' + addr_link(f['principal']) + ' nets ' +
                  (', '.join(f'{k} {usd(v)}' for k, v in (f['from_net'] if f['principal'] == t['from'] else f['to_net']).items()) or 'nothing priced') +
                  (' against ' + addr_link(f['counterparty']) + ' (' + code_desc(ctx, f['counterparty']) + '; ' + fmt_tags(a['counterparty_tags']) + ')' if f['counterparty'] else '') + '.')
        if f['sandwich']:
            facts += ' Sandwich marks: ' + json.dumps(f['sandwich'])[:300] + '.'
        L.append(facts)
        if p['net_flows']:
            L.append('\nNet flows: ' + '; '.join(addr_link(x[0]) + ' ' + ('+' if not x[3].startswith('-') else '') + amount(int(x[3]), ASSETS[x[1]][1] if x[1] in ASSETS else 18) + ' ' + x[2] +
                                             ' (' + usd(x[4]) + ')' for x in p['net_flows'][:8]) + '.')
        if p['unpriced']:
            L.append('\nUnpriced ERC-20 transfers: ' + ', '.join(addr_link(u['token'], tok_label(ctx, u['token'], short(u['token']))) + ' ×' + str(u['transfers']) + ' (largest raw ' + u['largest_raw'] + ')' for u in p['unpriced']) + '.')
        fam = ', '.join(f'{k} ×{v}' for k, v in sorted(p['events']['families'].items(), key=lambda kv: -kv[1]))
        L.append('\nEvent families: ' + (fam or 'none') + '.' + (' Unknown topics: ' + '; '.join(addr_link(u['emitter']) + ' ' + u['topic0'][:18] + '… ×' + str(u['count']) for u in p['events']['unknown_topics']) + '.'
                                                              if p['events']['unknown_topics'] else ''))
        if note:
            conf[note.get('confidence', 'unstated')] += 1
            L.append('\nInterpretation (LLM, confidence ' + note.get('confidence', 'unstated') + '): ' + note['body'])
            if note.get('unverified'):
                L.append('\nUnverified: ' + note['unverified'])
            if note.get('type_proposed'):
                L.append('\nProposed type: `' + note['type_proposed'] + '`' + ('. Rule: ' + note['rule_proposed'] if note.get('rule_proposed') else '') +
                         ('. Method: ' + note['method_proposed'] if note.get('method_proposed') else '') + ('. Status: ' + note['status'] if note.get('status') else ''))
        else:
            L.append('\n_No qualitative note yet for this transaction._')
        L.append('')
    extra_notes = [(h, v) for h, v in notes.items() if h.startswith('0x') and h not in {x.lower() for x in seen_hashes}]
    if extra_notes:
        L.append('## Other transactions the LLM decoded\n')
        L.append('Transactions read with `show` during the investigation that are not representatives of any packet; they support the notes above.\n')
        for h, v in extra_notes:
            L.append('- ' + tx_link(h) + ': ' + v.get('mechanism', '') + (' (confidence ' + v['confidence'] + ')' if v.get('confidence') else '') + '. ' + v['body'])
        L.append('')
    L.append('## What the quant step handed over, and what came back\n')
    L.append('Packets: ' + str(len(packets)) + '. Annotated: ' + str(sum(1 for p in packets if p['transaction']['hash'].lower() in notes)) + '. LLM confidence: ' +
             ', '.join(f'{k} ×{v}' for k, v in conf.most_common()) + '. Actor tags seen among the parties of large transactions: ' +
             ', '.join(f'{k} ×{v}' for k, v in sorted(cls['actor_tag_counts'].items(), key=lambda kv: -kv[1])) + '.\n')
    L.append('Artifacts in this directory: `prices.json`, `stats.json` (window, prices, implied prices, in-sample check, registry), `txs_all.jsonl.gz` (every transaction with '
             'its legs; not committed), `txs_big.jsonl.gz` (the population above the threshold with full features), `addresses.json.gz` (window-wide profiles of every address '
             'that touches a large transaction), `classified.json` (per-type investigation output), `types_by_hash.json.gz`, `residue.json`, `packets.json`, `rounds.json` '
             '(coverage after each classify run), `context.json` (bounded RPC lookups), `qual_notes.md` (LLM notes keyed by transaction hash, with `type`, `synthesis` and '
             '`feedback` sections), `rpc_requests.jsonl` (every request, no keys).\n')
    if 'feedback' in notes:
        L.append('### Requests from the qualitative step back to the quant step (LLM)\n')
        L.append(notes['feedback']['body'] + '\n')
    L.append('Coverage measures rule matching, not classification accuracy or verified economic intent. Multiple matching types are retained in `all_matches_by_hash.json.gz`; primary labels use registry order. Every selected occurrence has a record in `investigations.jsonl.gz`. No-log native transfers below the selection threshold are not receipt-resolved, and their value is excluded from address flow profiles.\n')
    L.append('Limitations: only top-level ETH value is visible, so ETH moved by contracts (including the ETH side of Uniswap v4 swaps and of WETH unwraps forwarded onward) is '
             'not counted. Tokens outside the registry are unpriced unless they had enough swaps against priced assets, and implied prices assume 18 decimals. Prices are '
             'hourly for ETH and BTC and window-end for the rest; stablecoins outside the feed set are taken at parity. Transaction status is inferred from the presence of '
             'logs or checked in receipts for large native candidates and packets. Hourly endpoint marks are retrospective and must not be used as contemporaneous prices in a trading backtest. Actor tags are behavioural proxies over the research window, not identities. Contract identities named in the notes without an onchain '
             'check are model memory. A rule matches the first type in registry order, so a transaction that does two things is typed by whichever rule comes first.\n')
    (out / 'report.md').write_text('\n'.join(L) + '\n')
    print(json.dumps({'report': str((out / 'report.md').relative_to(ROOT)), 'packets': len(packets), 'annotated': sum(1 for p in packets if p['transaction']['hash'].lower() in notes),
                      'sections': sorted(k for k in notes if not k.startswith('0x'))}))


# ---------------------------------------------------------------- show
def find_block(out, h):
    for path in (out / 'txs_big.jsonl.gz', out / 'txs_all.jsonl.gz'):
        if not path.exists():
            continue
        with gzip.open(path, 'rt') as f:
            for line in f:
                if h in line:
                    r = json.loads(line)
                    if r['h'] == h:
                        return r['b'], r
    return None, None


def show(args):
    out, day = Path(args.out), Path(args.day)
    for spec in args.hashes:
        h, _, b = spec.lower().partition('@')
        row = None
        if b:
            b = int(b)
        else:
            b, row = find_block(out, h)
        if b is None:
            print('not found:', h)
            continue
        block = read_gz(day / 'raw' / 'blocks' / (str(b) + '.json.gz'))
        logs = [l for l in read_gz(day / 'raw' / 'logs' / (str(b) + '.json.gz')) if l['transactionHash'] == h]
        tx = next(t for t in block['transactions'] if t['hash'] == h)
        print('=' * 110)
        print(h, 'block', b, 'index', hx(tx['transactionIndex']), 'of', len(block['transactions']), utc(hx(block['timestamp'])))
        skip = {'input', 'accessList', 'authorizationList', 'blobVersionedHashes', 'r', 's', 'v', 'yParity', 'hash', 'blockHash', 'blockNumber', 'transactionIndex', 'chainId'}
        print(json.dumps({k: v for k, v in tx.items() if k not in skip}))
        if tx.get('authorizationList'):
            print('authorizationList:', json.dumps(tx['authorizationList'])[:1200])
        print('input:', tx.get('input', '0x')[:args.calldata_chars], '| bytes', (len(tx.get('input', '0x')) - 2) // 2)
        if row:
            print('features:', json.dumps({k: row[k] for k in ('pc', 'gross', 'flash_usd', 'swaps', 'pools', 'fnet', 'tnet', 'mb', 'rcpt', 'assets') if k in row}))
            print('net:', json.dumps(row['net'][:10]))
        for i, l in enumerate(logs):
            if i >= args.max_logs:
                print('  ...', len(logs) - args.max_logs, 'more logs')
                break
            e = event_view(l)
            extra = {k: v for k, v in e.items() if k not in ('log_index', 'emitter', 'topic0', 'family')}
            print(f"  [{e['log_index']}] {e['emitter']} {e['family']} {json.dumps(extra) if extra else ''}")
            if e['family'] in ('unknown', 'anonymous', 'DSNote'):
                print('       topics', ' '.join(l['topics']))
                print('       data', l['data'][:args.data_chars], '| bytes', (len(l['data']) - 2) // 2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['prices', 'statuses', 'scan', 'classify', 'resolve', 'render', 'show'])
    p.add_argument('hashes', nargs='*', help='show: transaction hashes (hash or hash@block); resolve: extra hashes for receipts')
    p.add_argument('--day', default=str(DAY))
    p.add_argument('--out', default=str(OUT_DEFAULT))
    p.add_argument('--threshold', default='10000')
    p.add_argument('--limit', type=int, default=0, help='scan: first N blocks only')
    p.add_argument('--implied-min-swaps', type=int, default=1000000000)
    p.add_argument('--implied-min-volume', default='100000')
    p.add_argument('--top', type=int, default=12, help='classify: residue clusters per ranking metric')
    p.add_argument('--controls', type=int, default=3)
    p.add_argument('--audit-known', action='store_true', help='include one hash-sampled representative of each known type')
    p.add_argument('--label', default='', help='classify: label for rounds.json')
    p.add_argument('--addresses', nargs='*', default=[], help='resolve: extra addresses for code lookups')
    p.add_argument('--tokens', nargs='*', default=[], help='resolve: extra token addresses for symbol/decimals lookups')
    p.add_argument('--max-credits', type=int, default=60000)
    p.add_argument('--max-tokens', type=int, default=40)
    p.add_argument('--max-logs', type=int, default=40)
    p.add_argument('--calldata-chars', type=int, default=400)
    p.add_argument('--data-chars', type=int, default=200)
    args = p.parse_args()
    {'prices': prices, 'statuses': statuses, 'scan': scan, 'classify': classify, 'resolve': resolve, 'render': render, 'show': show}[args.command](args)


if __name__ == '__main__':
    main()
