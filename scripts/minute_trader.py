#!/usr/bin/env python3
"""Read-only Ethereum mainnet, minute-horizon quote-based paper experiment.

No signer, private key, approvals, or transaction submission. Quotes are not fills.
Run with: uv run --with pycryptodome python scripts/minute_trader.py --help
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from decimal import Decimal, getcontext
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import time

from Crypto.Hash import keccak
from live_rpc import RPC, hx

getcontext().prec = 60
D = Decimal
FACTORY = '0x1f98431c8ad98523631ae4a59f267346ea31f984'
QUOTER = '0x61ffe014ba17989e743c5f6cb21bf9697530b21e'
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
USDC = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
FEEDS = {
    WETH: ('0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419', 'ETH / USD', 7200),
    USDC: ('0x8fffffd4afb6115b954bd326cbe7b4ba576818f6', 'USDC / USD', 90000),
}
READ_METHODS = {'eth_chainId', 'eth_getBlockByNumber', 'eth_getLogs', 'eth_call', 'eth_gasPrice'}


def calldata(signature, *args):
    selector = keccak.new(digest_bits=256, data=signature.encode()).hexdigest()[:8]
    return '0x' + selector + ''.join(
        (a[2:] if isinstance(a, str) else f'{a:064x}').rjust(64, '0') for a in args)


SWAP_TOPIC = '0x' + keccak.new(digest_bits=256, data=b'Swap(address,address,int256,int256,uint160,uint128,int24)').hexdigest()


def words(raw):
    if not isinstance(raw, str) or not raw.startswith('0x') or len(raw) < 66 or (len(raw)-2) % 64:
        raise ValueError('Invalid ABI response')
    return [int(raw[i:i+64], 16) for i in range(2, len(raw), 64)]


def address(n):
    if not 0 <= n < 2**160:
        raise ValueError('Invalid ABI address')
    return f'0x{n:040x}'


def signed(n):
    return n - 2**256 if n >= 2**255 else n


def abi_string(raw):
    b = bytes.fromhex(raw[2:])
    if len(b) == 32:
        text = b.rstrip(b'\0').decode(errors='replace')
    else:
        offset = int.from_bytes(b[:32], 'big')
        length = int.from_bytes(b[offset:offset+32], 'big')
        if offset + 32 + length > len(b):
            raise ValueError('Invalid ABI string')
        text = b[offset+32:offset+32+length].decode(errors='replace')
    return re.sub(r'[^a-zA-Z0-9 /_.+-]', '?', text)[:64]


def utc(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()


def save(path, obj):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    temp.replace(path)


class Reader:
    """Whitelist RPC methods and retain credential-free responses for audit."""
    def __init__(self, out, max_credits):
        self.out = out
        (out / 'raw').mkdir(parents=True)
        self.rpc = RPC(max_credits=max_credits, timeout=15, interval=.1)
        self.cache = {}

    def batch(self, calls, cache=True):
        keys = [json.dumps(c, sort_keys=True) for c in calls]
        if any(m not in READ_METHODS for m, _ in calls):
            raise ValueError('Only read-only RPC methods are permitted')
        missing = list(dict.fromkeys(k for k in keys if not cache or k not in self.cache))
        for i in range(0, len(missing), 20):
            part = missing[i:i+20]
            values = self.rpc.batch([json.loads(k) for k in part], allow_errors=True)
            for key, value in zip(part, values):
                method, params = json.loads(key)
                name = hashlib.sha256((key + ('' if cache else str(time.time_ns()))).encode()).hexdigest()
                save(self.out / 'raw' / (name + '.json'), {'method': method, 'params': params, 'result': value})
                self.cache[key] = value
        return [self.cache[k] for k in keys]

    def get(self, method, params, cache=True):
        result = self.batch([(method, params)], cache=cache)[0]
        if isinstance(result, dict) and 'error' in result:
            raise RuntimeError('RPC request failed: ' + json.dumps(result['error']))
        if result is None:
            raise RuntimeError('RPC returned no result')
        return result

    def calls(self, items, block, gas=200000):
        return self.batch([('eth_call', [{'to': a, 'data': data, 'gas': hex(gas)}, hex(block)]) for a, data in items])

    def call(self, a, signature, *args, block):
        return words(self.get('eth_call', [{'to': a, 'data': calldata(signature, *args), 'gas': hex(1500000)}, hex(block)]))

    def head(self):
        h = self.get('eth_getBlockByNumber', ['latest', False], cache=False)
        if abs(time.time() - hx(h['timestamp'])) > 90:
            raise RuntimeError('Mainnet head is stale or local clock is inconsistent')
        return h

    def canonical(self, h):
        check = self.get('eth_getBlockByNumber', [h['number'], False], cache=False)
        if check['hash'] != h['hash']:
            raise RuntimeError('Reorg detected; stop this paper run and start a new directory')


@dataclass(frozen=True)
class Config:
    notional_usd: float = 1000
    cash_usd: float = 10000
    max_loss_usd: float = 200
    hold_seconds: int = 300
    min_hold_seconds: int = 120
    stop_bps: float = 100
    take_bps: float = 150
    slippage_bps: float = 20
    min_momentum_bps: float = 50
    max_cost_bps: float = 100
    max_pools: int = 10
    discovery_pools: int = 40
    interval: int = 30

    def validate(self):
        if any(not math.isfinite(float(v)) or v <= 0 for v in asdict(self).values()):
            raise ValueError('All configuration values must be finite and positive')
        if not 120 <= self.hold_seconds <= 600 or self.min_hold_seconds > self.hold_seconds:
            raise ValueError('Holding window must be 120–600 seconds')
        if self.notional_usd >= self.cash_usd or self.max_loss_usd >= self.cash_usd:
            raise ValueError('Virtual cash must exceed position size and loss threshold')
        if not 12 <= self.interval <= 60 or self.slippage_bps >= 10000:
            raise ValueError('Invalid poll interval or slippage')
        if self.max_pools > self.discovery_pools or self.discovery_pools > 100:
            raise ValueError('Invalid pool count')


def price(sqrt_price, quote_index, base_decimals, quote_decimals):
    if sqrt_price <= 0:
        raise ValueError('Uninitialized pool')
    ratio = (D(sqrt_price) / D(2**96))**2
    return (ratio if quote_index == 1 else 1 / ratio) * D(10)**(base_decimals-quote_decimals)


def reference_prices(r, h):
    result = {}
    n, ts = hx(h['number']), hx(h['timestamp'])
    results = r.calls([(feed, calldata(method)) for feed, _, _ in FEEDS.values()
                       for method in ('description()', 'decimals()', 'latestRoundData()')], n)
    for i, (token, (feed, description, max_age)) in enumerate(FEEDS.items()):
        raw = results[3*i:3*i+3]
        if abi_string(raw[0]) != description:
            raise ValueError('Unexpected reference feed')
        decimals = words(raw[1])[0]
        round_id, answer, _, updated, answered = words(raw[2])
        if decimals > 36 or signed(answer) <= 0 or not 0 <= ts-updated <= max_age or answered < round_id:
            raise ValueError('Invalid or stale reference price')
        result[token] = float(D(answer) / D(10)**decimals)
    if not .98 <= result[USDC] <= 1.02:
        raise ValueError('USDC outside the configured reference-price band')
    return result


def swap_logs(r, first, last, pools=None):
    query = {'fromBlock': hex(first), 'toBlock': hex(last), 'topics': [SWAP_TOPIC]}
    if pools:
        query['address'] = pools
    logs = r.get('eth_getLogs', [query])
    seen = set()
    for log in logs:
        key = (log['blockHash'], log['logIndex'])
        if log.get('removed') or key in seen or len(log['topics']) != 3 or len(words(log['data'])) != 5:
            raise ValueError('Invalid, removed, or duplicate swap log')
        seen.add(key)
    return logs


def discover(r, h, cfg):
    n = hx(h['number'])
    logs = swap_logs(r, n-74, n)
    counts = Counter(x['address'].lower() for x in logs)
    candidates = [p for p, _ in counts.most_common(cfg.discovery_pools)]
    methods = ['token0()', 'token1()', 'fee()']
    raw = r.calls([(p, calldata(m)) for p in candidates for m in methods], n)
    preliminary, exclusions = [], []
    for i, pool in enumerate(candidates):
        try:
            t0, t1 = (address(words(raw[3*i+j])[0]) for j in (0, 1))
            fee = words(raw[3*i+2])[0]
            quote = USDC if USDC in (t0, t1) else WETH if WETH in (t0, t1) else None
            if quote is None or not 0 < fee < 1000000:
                raise ValueError('No direct WETH/USDC quote or unsupported fee')
            preliminary.append({'pool': pool, 'token0': t0, 'token1': t1, 'fee': fee,
                                'quote': quote, 'base': t1 if quote == t0 else t0,
                                'quote_index': 0 if quote == t0 else 1, 'swaps': counts[pool]})
        except (ValueError, TypeError, KeyError):
            exclusions.append({'pool': pool, 'reason': 'unsupported metadata or pair'})
    checks = r.calls([(FACTORY, calldata('getPool(address,address,uint24)', p['token0'], p['token1'], p['fee']))
                      for p in preliminary], n)
    pools = []
    for p, check in zip(preliminary, checks):
        if isinstance(check, str) and address(words(check)[0]) == p['pool']:
            pools.append(p)
        else:
            exclusions.append({'pool': p['pool'], 'reason': 'not a canonical Uniswap v3 pool'})
    tokens = sorted({p[k] for p in pools for k in ('base', 'quote')})
    meta = r.calls([(t, calldata(m)) for t in tokens for m in ('decimals()', 'symbol()')], n)
    metadata = {}
    for i, token in enumerate(tokens):
        try:
            decimals = words(meta[2*i])[0]
            if decimals > 36:
                raise ValueError('Unsupported decimals')
            metadata[token] = {'decimals': decimals, 'symbol': abi_string(meta[2*i+1])}
        except (ValueError, TypeError, KeyError):
            continue
    refs = reference_prices(r, h)
    valid = []
    grouped = defaultdict(list)
    for log in logs:
        grouped[log['address'].lower()].append(log)
    for p in pools:
        if p['base'] not in metadata or p['quote'] not in metadata:
            exclusions.append({'pool': p['pool'], 'reason': 'invalid token metadata'})
            continue
        p['base_meta'], p['quote_meta'] = metadata[p['base']], metadata[p['quote']]
        p['pair'] = p['base_meta']['symbol'] + '/' + p['quote_meta']['symbol']
        p['discovery_quote_volume_usd'] = float(sum(
            abs(D(signed(words(x['data'])[p['quote_index']]))) for x in grouped[p['pool']]
        ) / D(10)**p['quote_meta']['decimals'] * D(str(refs[p['quote']])))
        valid.append(p)
    valid.sort(key=lambda p: p['discovery_quote_volume_usd'], reverse=True)
    r.canonical(h)
    return valid[:cfg.max_pools], {'head': h, 'swap_logs': len(logs), 'event_emitters': len(counts),
                                'metadata_candidates': len(candidates), 'verified_supported_pools': len(valid),
                                'excluded': exclusions, 'ranked_pools': valid}


def quote_data(p, amount, buying):
    a, b = (p['quote'], p['base']) if buying else (p['base'], p['quote'])
    return calldata('quoteExactInputSingle((address,address,uint256,uint24,uint160))',
                    a, b, int(amount), p['fee'], 0)


def quote_result(raw):
    result = words(raw)
    if len(result) != 4 or result[0] <= 0:
        raise ValueError('Empty or invalid quote')
    return result


def haircut(amount, bps):
    return int(D(amount) * (D(1) - D(str(bps))/10000))


def signal(row, cfg):
    """An unvalidated, fixed momentum hypothesis; never a predicted return."""
    if row.get('error'):
        return 'quote unavailable'
    if row['last_swap_age_seconds'] > 60 or row['return_3m_bps'] is None or row['return_1m_bps'] is None:
        return 'stale or insufficient activity'
    if row['cost_bps'] > cfg.max_cost_bps:
        return 'round-trip cost too high'
    if row['return_3m_bps'] < max(cfg.min_momentum_bps, 2*row['cost_bps']):
        return 'three-minute momentum below experimental threshold'
    if row['return_1m_bps'] <= 0 or row['buy_share_3m'] < .6 or row['swaps_3m'] < 5:
        return 'momentum not confirmed by recent flow'
    return 'paper candidate'


def snapshot(r, pools, cfg, previous=None, position=None):
    if previous:
        r.canonical(previous)
    h = r.head()
    n, ts = hx(h['number']), hx(h['timestamp'])
    refs = reference_prices(r, h)
    gas_price = hx(r.get('eth_gasPrice', [], cache=False))
    # Budget using at least twice base fee plus a 0.1 gwei priority allowance.
    gas_price = max(gas_price, 2*hx(h['baseFeePerGas']) + 100000000)
    logs = swap_logs(r, n-74, n, [p['pool'] for p in pools])
    block_numbers = sorted({hx(x['blockNumber']) for x in logs})
    headers = r.batch([('eth_getBlockByNumber', [hex(b), False]) for b in block_numbers])
    by_number = dict(zip(block_numbers, headers))
    events = defaultdict(list)
    for log in logs:
        block = by_number[hx(log['blockNumber'])]
        if block['hash'] != log['blockHash']:
            raise ValueError('Swap log and block hash mismatch')
        events[log['address'].lower()].append((hx(block['timestamp']), hx(log['logIndex']), words(log['data'])))
    states = r.calls([(p['pool'], calldata('slot0()')) for p in pools], n)
    rows = []
    for p, raw_state in zip(pools, states):
        row = {'pool': p['pool'], 'pair': p['pair'], 'base': p['base'], 'quote': p['quote']}
        try:
            state = words(raw_state)
            qindex = p['quote_index']
            bd, qd = p['base_meta']['decimals'], p['quote_meta']['decimals']
            spot = price(state[0], qindex, bd, qd)
            history = sorted(events[p['pool']])
            returns = {}
            for seconds in (60, 180):
                prior = [x for x in history if x[0] <= ts-seconds]
                old = prior[-1] if prior else None
                returns[seconds] = float((spot/price(old[2][2], qindex, bd, qd)-1)*10000) if old and ts-seconds-old[0] <= 60 else None
            recent = [x for x in history if ts-180 < x[0] <= ts]
            buy = sum(max(0, signed(x[2][qindex])) for x in recent)
            volume = sum(abs(signed(x[2][qindex])) for x in recent)
            q_usd = refs[p['quote']]
            amount = int(D(str(cfg.notional_usd))/D(str(q_usd))*D(10)**qd)
            row.update({'spot_quote_per_base': float(spot), 'quote_usd': q_usd,
                        'last_swap_age_seconds': ts-history[-1][0] if history else 10**9,
                        'return_1m_bps': returns[60], 'return_3m_bps': returns[180],
                        'swaps_3m': len(recent), 'buy_share_3m': buy/volume if volume else 0,
                        'quote_volume_3m_usd': volume/10**qd*q_usd,
                        'input_raw': str(amount),
                        'fee_bps_per_swap': p['fee']/100})
        except (ValueError, RuntimeError, TypeError, KeyError, IndexError) as exc:
            row['error'] = type(exc).__name__ + ': ' + str(exc)[:200]
        rows.append(row)
    # Entry quotes across pools are independent; reverse quotes depend on those amounts.
    eligible = [(p, row) for p, row in zip(pools, rows) if not row.get('error')]
    entries = r.calls([(QUOTER, quote_data(p, int(row['input_raw']), True)) for p, row in eligible], n, gas=1500000)
    exiting = []
    for (p, row), raw in zip(eligible, entries):
        try:
            entry = quote_result(raw)
            row['bought_raw'] = str(haircut(entry[0], cfg.slippage_bps))
            row['entry_gas_usd'] = (max(200000, entry[3]+120000)+60000)*gas_price/1e18*refs[WETH]
            exiting.append((p, row))
        except (ValueError, TypeError) as exc:
            row['error'] = 'entry quote: ' + str(exc)[:200]
    exits = r.calls([(QUOTER, quote_data(p, int(row['bought_raw']), False)) for p, row in exiting], n, gas=1500000)
    for (p, row), raw in zip(exiting, exits):
        try:
            sell = quote_result(raw)
            recovered = haircut(sell[0], cfg.slippage_bps)/10**p['quote_meta']['decimals']*row['quote_usd']
            row['exit_gas_usd'] = (max(200000, sell[3]+120000)+60000)*gas_price/1e18*refs[WETH]
            row['cost_bps'] = (cfg.notional_usd-recovered+row['entry_gas_usd']+row['exit_gas_usd'])/cfg.notional_usd*10000
        except (ValueError, TypeError) as exc:
            row['error'] = 'reverse quote: ' + str(exc)[:200]
    if position:
        for p, row in zip(pools, rows):
            if position['pool'] != p['pool']:
                continue
            try:
                raw = r.calls([(QUOTER, quote_data(p, int(position['bought_raw']), False))], n, gas=1500000)[0]
                sell = quote_result(raw)
                exit_gas = (max(200000, sell[3]+120000)+60000)*gas_price/1e18*refs[WETH]
                row['exit_value_usd'] = haircut(sell[0], cfg.slippage_bps)/10**p['quote_meta']['decimals']*refs[p['quote']]-exit_gas
            except (ValueError, TypeError) as exc:
                row['exit_error'] = str(exc)[:200]
    for row in rows:
        row['decision'] = signal(row, cfg)
    r.canonical(h)
    if time.time()-ts > 90:
        raise RuntimeError('Snapshot took too long to remain fresh')
    return {'head': h, 'timestamp': ts, 'utc': utc(ts), 'reference_usd': refs,
            'gas_budget_gwei': gas_price/1e9, 'rows': rows, 'rpc': r.rpc.stats()}


class PaperBook:
    def __init__(self, cfg):
        self.cfg = cfg
        self.cash = cfg.cash_usd
        self.position = None
        self.pending = None
        self.trades = []
        self.halted = False

    def step(self, snap, finishing=False, allow_entries=True):
        cfg, ts = self.cfg, snap['timestamp']
        rows = {r['pool']: r for r in snap['rows']}
        if self.position:
            p = self.position
            row = rows.get(p['pool'], {})
            # Failed exits stay open and block all new entries.
            if 'exit_value_usd' not in row or row.get('exit_error'):
                return 'position unresolved: exit quote unavailable'
            net = row['exit_value_usd']-p['spent_usd']
            bps = net/cfg.notional_usd*10000
            age = ts-p['opened_at']
            equity = self.cash+row['exit_value_usd']
            reason = ('session loss threshold' if cfg.cash_usd-equity >= cfg.max_loss_usd else
                      'stop threshold' if bps <= -cfg.stop_bps else
                      'time limit' if age >= cfg.hold_seconds else
                      'take profit' if age >= cfg.min_hold_seconds and bps >= cfg.take_bps else
                      'end of bounded trial' if finishing else None)
            if reason:
                self.cash += row['exit_value_usd']
                self.trades.append({**p, 'closed_at': ts, 'exit_value_usd': row['exit_value_usd'],
                                    'net_pnl_usd': net, 'held_seconds': age, 'reason': reason})
                self.position = None
                self.halted = cfg.cash_usd-self.cash >= cfg.max_loss_usd
                return 'paper exit: ' + reason
            return 'paper hold'
        if self.halted or finishing or not allow_entries:
            self.pending = None
            return 'halted' if self.halted else 'trial ended flat' if finishing else 'entry window closed'
        if self.pending:
            pool, observed_at = self.pending
            if ts <= observed_at:
                return 'waiting for a later block'
            row = rows.get(pool, {})
            self.pending = None
            if ts-observed_at <= 90 and row.get('decision') == 'paper candidate':
                spent = cfg.notional_usd+row['entry_gas_usd']
                if self.cash >= spent:
                    self.cash -= spent
                    self.position = {'pool': pool, 'pair': row['pair'], 'opened_at': ts,
                                     'signal_at': observed_at, 'bought_raw': row['bought_raw'],
                                     'spent_usd': spent, 'entry_cost_bps': row['cost_bps']}
                    return 'paper entry at a later snapshot'
        candidates = [r for r in snap['rows'] if r['decision'] == 'paper candidate']
        if candidates:
            best = max(candidates, key=lambda r: r['return_3m_bps']-2*r['cost_bps'])
            self.pending = (best['pool'], ts)
            return 'candidate queued for next snapshot'
        return 'no qualifying paper entry'

    def export(self):
        return {'mode': 'PAPER_ONLY', 'cash_usd': self.cash, 'position': self.position,
                'pending': self.pending, 'halted': self.halted, 'closed_trades': self.trades,
                'realized_pnl_usd': sum(t['net_pnl_usd'] for t in self.trades)}


def report(out, cfg, discovery, snap, book, status):
    lines = ['# Ethereum mainnet: minute-horizon paper trial', '',
             f'Status: **{status}**. Last observation: {snap["utc"]}, block {hx(snap["head"]["number"])}.', '',
             '**No real trades or wallet transactions. This fixed momentum hypothesis is unvalidated.**', '',
             f'Virtual cash ${cfg.cash_usd:,.0f}; position ${cfg.notional_usd:,.0f}; maximum planned holding time '
             f'{cfg.hold_seconds//60} minutes; {cfg.interval}-second polling. Stops may trigger earlier; outages can delay exits.', '',
             f'Discovery found {discovery["event_emitters"]} v3-shaped event emitters in 75 blocks. '
             f'Inspected the top {discovery["metadata_candidates"]} by swap count; '
             f'{discovery["verified_supported_pools"]} had verified Uniswap v3 identity and supported quote assets. '
             f'This trial watches {len(snap["rows"])} pools ranked by observed quote volume. '
             'The universe is fixed at startup; it does not cover all mainnet tokens or DEXs.', '',
             '| Pair | 3m move (bps) | Estimated round-trip cost (bps) | Decision |',
             '| --- | ---: | ---: | --- |']
    for row in snap['rows']:
        move = row.get('return_3m_bps')
        cost = row.get('cost_bps')
        lines.append(f'| {row["pair"]} | {move:.1f} | {cost:.1f} | {row["decision"]} |' if move is not None and cost is not None
                     else f'| {row["pair"]} | unavailable | {format(cost, ".1f") if cost is not None else "unavailable"} | {row["decision"]} |')
    lines += ['', f'Closed paper trades: {len(book.trades)}. Realized simulated P&L: '
              f'${sum(t["net_pnl_usd"] for t in book.trades):,.2f}. Open paper position: {bool(book.position)}.', '',
              'The entry rule requires a positive 1-minute move, at least five swaps in three minutes, '
              f'at least 60% quote-side buy volume, and a 3-minute rise exceeding both {cfg.min_momentum_bps:g} bps and twice the estimated cost. '
              'Past movement is not an expected return. Entry must still qualify at the next snapshot. '
              f'There is one position at a time; stop/take thresholds are {cfg.stop_bps/100:g}%/{cfg.take_bps/100:g}% net of modeled costs, '
              f'and the virtual session halts after a ${cfg.max_loss_usd:g} loss. Loss thresholds are triggers, not guarantees.', '',
              'Quotes include pool fees and pool price impact. The model additionally haircuts each output by '
              f'{cfg.slippage_bps:g} bps and charges a gas budget based on the observed gas market, '
              'router overhead, and one 60,000-gas approval allowance per leg. Gas is USD-accounted; '
              'native ETH funding, wrapping and quote-asset conversion are not modeled. '
              'Entry and reverse quotes use independent unchanged pool state, not a sequential executed round trip. '
              'Future quote marks omit the lasting effect of our hypothetical trades. '
              'Actual routing, execution latency, failed transactions, MEV, taxes, and token restrictions can change results. '
              'Quoter success and factory identity do not prove a token can be safely bought and sold by a wallet. '
              'WETH inventory and reference-feed timing also create valuation risk.', '',
              'RPC responses are saved under `raw/`; snapshots retain block hashes. '
              'Each snapshot rechecks its head and the previous snapshot head; reorgs or stale data stop the run. '
              'A failed exit remains an unresolved position. No paper result establishes a profitable strategy.', '',
              'Sources: [Uniswap QuoterV2 interface](https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/IQuoterV2.sol), '
              '[Quoter implementation](https://github.com/Uniswap/v3-periphery/blob/main/contracts/lens/QuoterV2.sol), '
              '[pool swap events](https://github.com/Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol).', '']
    (out / 'report.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True, help='New output directory; existing runs are never overwritten')
    parser.add_argument('--minutes', type=float, default=0, help='Bounded paper trial length; 0 takes one observation')
    parser.add_argument('--max-credits', type=int, default=150000)
    for name, field in Config.__dataclass_fields__.items():
        parser.add_argument('--'+name.replace('_', '-'), type=type(field.default), default=field.default)
    args = parser.parse_args()
    cfg = Config(**{name: getattr(args, name) for name in Config.__dataclass_fields__})
    cfg.validate()
    if not math.isfinite(args.minutes) or not 0 <= args.minutes <= 60 or args.max_credits <= 0:
        parser.error('Trial must be between 0 and 60 minutes with a positive RPC budget')
    args.out.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).read_bytes()
    (args.out / 'source.py').write_bytes(source)
    save(args.out / 'config.json', {**asdict(cfg), 'minutes': args.minutes, 'mode': 'PAPER_ONLY',
                                   'source_sha256': hashlib.sha256(source).hexdigest()})
    r = Reader(args.out, args.max_credits)
    book = PaperBook(cfg)
    snap = discovery = None
    status = 'initializing'
    try:
        if hx(r.get('eth_chainId', [], cache=False)) != 1:
            raise RuntimeError('Ethereum mainnet is required')
        h = r.head()
        if address(r.call(QUOTER, 'factory()', block=hx(h['number']))[0]) != FACTORY:
            raise RuntimeError('Unexpected Quoter factory')
        if address(r.call(QUOTER, 'WETH9()', block=hx(h['number']))[0]) != WETH:
            raise RuntimeError('Unexpected Quoter WETH')
        pools, discovery = discover(r, h, cfg)
        save(args.out / 'discovery.json', discovery)
        if not pools:
            raise RuntimeError('No supported verified pools found')
        print(json.dumps({'stage': 'discovered', 'pools': [p['pair'] for p in pools], 'rpc': r.rpc.stats()}), flush=True)
        deadline = time.monotonic()+args.minutes*60
        previous = h
        count = 0
        while True:
            started = time.monotonic()
            snap = snapshot(r, pools, cfg, previous, book.position)
            finishing = args.minutes == 0 or time.monotonic() >= deadline
            action = book.step(snap, finishing, deadline-time.monotonic() >= cfg.hold_seconds)
            previous = snap['head']
            count += 1
            save(args.out / f'snapshot_{count:04d}.json', snap)
            save(args.out / 'paper_book.json', book.export())
            status = 'completed' if finishing else 'running'
            report(args.out, cfg, discovery, snap, book, status)
            print(json.dumps({'utc': snap['utc'], 'action': action,
                              'candidates': [x['pair'] for x in snap['rows'] if x['decision'] == 'paper candidate'],
                              'closed_trades': len(book.trades), 'realized_pnl_usd': book.export()['realized_pnl_usd'],
                              'rpc': r.rpc.stats()}), flush=True)
            if finishing:
                break
            time.sleep(max(0, min(cfg.interval-(time.monotonic()-started), deadline-time.monotonic())))
    except (Exception, KeyboardInterrupt) as exc:
        status = 'stopped: ' + type(exc).__name__ + ': ' + r.rpc.clean(str(exc))
        save(args.out / 'error.json', {'status': status, 'rpc': r.rpc.stats()})
        save(args.out / 'paper_book.json', book.export())
        if snap and discovery:
            report(args.out, cfg, discovery, snap, book, status)
        print(json.dumps({'status': status}), flush=True)
        raise SystemExit(1)
    finally:
        save(args.out / 'run_status.json', {'status': status, 'rpc': r.rpc.stats(),
                                          'open_position': book.position is not None})


if __name__ == '__main__':
    main()
