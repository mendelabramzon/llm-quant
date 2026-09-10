#!/usr/bin/env python3
"""sUSDe secondary-market discount history: how often, how deep, and for how much the claim traded below NAV.

Why. The `susde-cooldown-redemption` strategy is a standing bid that earns only when a dislocation opens, so its value
is frequency x depth x fillable volume, not a rate read off a trailing window. Every window so far re-measured the
discount for a few hours and found nothing, which is the expected result for an event-driven edge and says nothing
about the event. This script reads the pools' own swap logs over months, prices each swap against the NAV the
protocol paid at that block, and segments the hourly series into episodes with the same significance rule the
`nav_discount` detector applies, so the history and the detector are comparable.

    uv run --with pycryptodome python scripts/dislocation_history.py collect --out research/2026-09-10/susde_history --days 180
    uv run --with pycryptodome python scripts/dislocation_history.py nav     --out research/2026-09-10/susde_history
    uv run --with pycryptodome python scripts/dislocation_history.py analyze --out research/2026-09-10/susde_history
    uv run --with pycryptodome python scripts/dislocation_history.py render  --out research/2026-09-10/susde_history

Data. Logs and headers come from Infura through `live_rpc.RPC` (key rotation, 10,000-block range cap handled by
adaptive splitting, one process). Historical NAV comes from public archive endpoints through `drpc.py`, one call at a
time, daily samples interpolated linearly between (sUSDe NAV drifts one to three basis points a day, so the
interpolation error is under a basis point). All reads are read-only; keys are never written.

Conventions. `discount_bps` is positive when sUSDe traded BELOW NAV. `side` is `sell` when sUSDe went INTO the pool
(a holder sold; the price a patient buyer could have hit) and `buy` when it came out. The other leg is valued at its
own NAV when it is sDAI and at par when it is a dollar stablecoin. Swaps under `MIN_TRADE_USD` of NAV notional are
dust and excluded.
"""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from Crypto.Hash import keccak as _keccak  # noqa: E402

import drpc  # noqa: E402
from live_rpc import RPC, RPCError, hx, word, sword, topic_addr, enc_uint  # noqa: E402


def keccak(s):
    return '0x' + _keccak.new(digest_bits=256, data=s.encode()).hexdigest()


def sel(sig):
    return keccak(sig)[:10]


SUSDE = '0x9d39a5de30e57443bff2a8307a4256c8797a3497'
SDAI = '0x83f20f44975d03b1b09e64809b757c47f942beea'
USDT = '0xdac17f958d2ee523a2206206994597c13d831ec7'
FRXUSD = '0xcacd6fd266af91b8aed52accc382b4e165586e29'
USDE = '0x4c9edd5852cd905f086c759e8383e09bff1e68b3'
USDC = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
V4_MANAGER = '0x000000000004444c5dc75cb358380d2e3de08a90'

# Venues, chosen from the saved windows' own volume tables (research/2026-09-*/*/analysis.json, `lp` rows naming
# sUSDe): the v4 sUSDe/USDT pool carried ~$8.4M across seven windows, the Curve sDAI/sUSDe pool (the fork proof's
# venue) ~$1.3M, the Curve sUSDe/frxUSD pool ~$0.5M. A second, smaller v4 sUSDe/USDT pool is left out.
POOLS = [
    {'name': 'curve-sdai-susde', 'venue': 'curve', 'address': '0x167478921b907422f8e88b43c4af2b8bea278d3a'},
    {'name': 'curve-susde-frxusd', 'venue': 'curve', 'address': '0x47ab5f9d8c9c7d002a92320f23a696d348c56a7f'},
    {'name': 'v4-susde-usdt', 'venue': 'uniswap_v4',
     'pool_id': '0xb20351bcf606dcc3525d2ed36760a86a5dec7423b77d41125bd4a416ba93448b',
     'currency0': SUSDE, 'currency1': USDT, 'decimals': [18, 6]},
]
# The strategy exits by selling USDe, so a discount on sUSDe is only capturable net of USDe's own price against the
# dollar. The Curve USDe/USDC pool gives that basis hour by hour; USDC is taken at par.
BASIS_POOL = {'name': 'curve-usde-usdc', 'venue': 'curve', 'address': '0x02950460e2b9529d0e00284a5fa2d7bdf3fa4d72', 'usde': USDE}
# NAV-bearing legs: token -> key in nav.json. Everything else on the other side of an sUSDe swap is taken at par.
NAV_TOKENS = {SUSDE: 'susde', SDAI: 'sdai'}
SYMBOLS = {SUSDE: 'sUSDe', SDAI: 'sDAI', USDT: 'USDT', FRXUSD: 'frxUSD', USDE: 'USDe', USDC: 'USDC'}

TOPICS = {
    'CurveEx': keccak('TokenExchange(address,int128,uint256,int128,uint256)'),
    'CurveExU': keccak('TokenExchange(address,uint256,uint256,uint256,uint256)'),
    'V4Swap': keccak('Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)'),
}
SEL_CONVERT = sel('convertToAssets(uint256)')
SEL_COINS = sel('coins(uint256)')
SEL_COINS_I128 = sel('coins(int128)')
SEL_DECIMALS = sel('decimals()')

ROUND_TRIP_BPS = 2.7        # two Curve legs, measured on the 2026-09-06 fork (research/2026-09-06/strategy)
MIN_TRADE_USD = 1000.0      # below this a swap is dust, not a price
CAPACITY_CAP_USD = 600_000  # the USDe exit depth the strategy is capped by
KILL_BPS = 10.0             # the book's kill criterion: no ask below NAV - 10bp in 30 days
KILL_MIN_USD = 10_000.0     # an ask has to be a size before it counts against the criterion
BLOCKS_PER_DAY = 7200
RANGE_CAP = 10_000          # Infura's eth_getLogs block-range cap, even with address and topic filters
MIN_TRADES_FOR_SPREAD = 3   # an hour with fewer trades has no spread of its own; it borrows the history's median
MAX_PRINT_BPS = 100.0       # a single print further from NAV than this is a venue running out of liquidity, not a market price
BASIS_CARRY_HOURS = 24      # an hour without a USDe/USDC trade inherits the last basis up to this far back


def utc(ts=None):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if ts is not None else \
        dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_json(path, default=None):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=1, sort_keys=True) + '\n')


def interp(xs, ys, x):
    """Linear interpolation on a sorted grid, clamped to the ends. Pure, so the tests can pin it."""
    if not xs:
        raise ValueError('empty grid')
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= x:
            lo = mid
        else:
            hi = mid
    span = xs[hi] - xs[lo]
    return ys[lo] + (ys[hi] - ys[lo]) * (x - xs[lo]) / span if span else ys[lo]


def pct(values, q):
    """Quantile with linear interpolation between order statistics; q in [0, 1]."""
    v = sorted(values)
    if not v:
        return None
    if len(v) == 1:
        return v[0]
    pos = q * (len(v) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (pos - lo)


# ----------------------------------------------------------------------------------------------------------------------
# Discount arithmetic
# ----------------------------------------------------------------------------------------------------------------------
def swap_discount(susde_amount, other_amount, other_nav, susde_nav):
    """Price paid or received per sUSDe in underlying-dollar terms, and the discount to NAV in basis points.

    `other_amount * other_nav` is the dollar value of the other leg (sDAI at its own NAV, a stablecoin at par).
    Positive discount means sUSDe changed hands below the value the protocol pays on redemption.
    """
    if susde_amount <= 0 or other_amount <= 0 or not susde_nav:
        return None, None
    price = other_amount * other_nav / susde_amount
    return price, 1e4 * (susde_nav - price) / susde_nav


def decode_curve(log, meta, nav_at):
    """One Curve TokenExchange -> swap record or None. `meta` carries coins/decimals; `nav_at(token, block)`."""
    d = log['data']
    sold_i, sold, bought_i, bought = word(d, 0), word(d, 1), word(d, 2), word(d, 3)
    coins, decs = meta['coins'], meta['decimals']
    if sold_i >= len(coins) or bought_i >= len(coins):
        return None
    tok_in, tok_out = coins[sold_i], coins[bought_i]
    if SUSDE not in (tok_in, tok_out) or tok_in == tok_out:
        return None
    n = hx(log['blockNumber'])
    amt_in, amt_out = sold / 10 ** decs[sold_i], bought / 10 ** decs[bought_i]
    if tok_in == SUSDE:
        side, susde_amt, other, other_tok = 'sell', amt_in, amt_out, tok_out
    else:
        side, susde_amt, other, other_tok = 'buy', amt_out, amt_in, tok_in
    susde_nav = nav_at(SUSDE, n)
    other_nav = nav_at(other_tok, n) if other_tok in NAV_TOKENS else 1.0
    price, disc = swap_discount(susde_amt, other, other_nav, susde_nav)
    if price is None:
        return None
    return {'block': n, 'tx': log['transactionHash'], 'li': hx(log['logIndex']), 'pool': meta['name'],
            'venue': 'curve', 'side': side, 'susde': susde_amt, 'other': other, 'other_symbol': SYMBOLS.get(other_tok, other_tok),
            'other_nav': other_nav, 'nav': susde_nav, 'price': price, 'discount_bps': disc,
            'usd': susde_amt * susde_nav, 'trader': topic_addr(log['topics'][1]) if len(log['topics']) > 1 else None,
            'mid_discount_bps': None}


def decode_v4(log, meta, nav_at):
    """One PoolManager Swap for the target pool -> swap record or None.

    v4 deltas are from the caller's view: negative = paid into the pool, positive = taken out. currency0 < currency1
    by address, so for this pool currency0 is sUSDe and currency1 is USDT. The post-swap sqrtPriceX96 gives the pool's
    marginal price, which a buyer could quote against before paying the fee; it is recorded as `mid_discount_bps`.
    """
    tp = log['topics']
    if len(tp) != 3 or tp[1] != meta['pool_id']:
        return None
    d = log['data']
    a0, a1, sqrtp = sword(d, 0), sword(d, 1), word(d, 2)
    if a0 == 0 or a1 == 0 or (a0 < 0) == (a1 < 0):
        return None
    n = hx(log['blockNumber'])
    dec0, dec1 = meta['decimals']
    amt0, amt1 = abs(a0) / 10 ** dec0, abs(a1) / 10 ** dec1
    if meta['currency0'] == SUSDE:
        susde_amt, other, other_tok, side = amt0, amt1, meta['currency1'], ('sell' if a0 < 0 else 'buy')
        mid = (sqrtp / 2 ** 96) ** 2 * 10 ** (dec0 - dec1)
    else:
        susde_amt, other, other_tok, side = amt1, amt0, meta['currency0'], ('sell' if a1 < 0 else 'buy')
        mid = 1.0 / ((sqrtp / 2 ** 96) ** 2 * 10 ** (dec0 - dec1)) if sqrtp else 0.0
    susde_nav = nav_at(SUSDE, n)
    other_nav = nav_at(other_tok, n) if other_tok in NAV_TOKENS else 1.0
    price, disc = swap_discount(susde_amt, other, other_nav, susde_nav)
    if price is None:
        return None
    mid_disc = 1e4 * (susde_nav - mid * other_nav) / susde_nav if mid else None
    return {'block': n, 'tx': log['transactionHash'], 'li': hx(log['logIndex']), 'pool': meta['name'],
            'venue': 'uniswap_v4', 'side': side, 'susde': susde_amt, 'other': other, 'other_symbol': SYMBOLS.get(other_tok, other_tok),
            'other_nav': other_nav, 'nav': susde_nav, 'price': price, 'discount_bps': disc,
            'usd': susde_amt * susde_nav, 'trader': topic_addr(tp[2]), 'mid_discount_bps': mid_disc,
            'fee_bps': word(d, 5) / 100.0}


def decode_basis(log, meta):
    """One USDe/stable TokenExchange -> {'block', 'usde', 'quote', 'price'} with the quote at par, or None."""
    d = log['data']
    sold_i, sold, bought_i, bought = word(d, 0), word(d, 1), word(d, 2), word(d, 3)
    coins, decs = meta['coins'], meta['decimals']
    if sold_i >= len(coins) or bought_i >= len(coins) or sold_i == bought_i or USDE not in (coins[sold_i], coins[bought_i]):
        return None
    amt_in, amt_out = sold / 10 ** decs[sold_i], bought / 10 ** decs[bought_i]
    usde, quote = (amt_in, amt_out) if coins[sold_i] == USDE else (amt_out, amt_in)
    if usde <= 0 or quote <= 0:
        return None
    return {'block': hx(log['blockNumber']), 'usde': usde, 'quote': quote, 'price': quote / usde}


def hourly_basis(basis_swaps):
    """USDe price per UTC hour, volume-weighted (total quote / total USDe); basis_bps positive when USDe is below par."""
    by = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for b in basis_swaps:
        h = b['ts'] // 3600 * 3600
        by[h][0] += b['quote']
        by[h][1] += b['usde']
        by[h][2] += 1
    return {h: {'price': q / u, 'basis_bps': 1e4 * (1 - q / u), 'usde': u, 'n': n} for h, (q, u, n) in by.items() if u}


def basis_at(hourly, h, carry_hours=BASIS_CARRY_HOURS):
    """The most recent hourly basis at or before hour `h`, at most `carry_hours` old; None when there is none."""
    for k in range(carry_hours + 1):
        b = hourly.get(h - 3600 * k)
        if b:
            return b['basis_bps'], k
    return None, None


# ----------------------------------------------------------------------------------------------------------------------
# Hourly series and episodes
# ----------------------------------------------------------------------------------------------------------------------
def hourly_series(swaps):
    """Bucket priced swaps into UTC hours. Discounts are volume-weighted by NAV notional."""
    by = collections.defaultdict(list)
    for s in swaps:
        by[s['ts'] // 3600 * 3600].append(s)
    rows = []
    for h in sorted(by):
        xs = by[h]
        vol = sum(s['usd'] for s in xs)
        sells = [s for s in xs if s['side'] == 'sell']
        sell_vol = sum(s['usd'] for s in sells)
        discs = [s['discount_bps'] for s in xs]
        rows.append({
            'hour': h, 'hour_utc': utc(h), 'n': len(xs), 'n_sell': len(sells), 'volume_usd': vol, 'sell_volume_usd': sell_vol,
            'vw_discount_bps': sum(s['discount_bps'] * s['usd'] for s in xs) / vol if vol else None,
            'vw_sell_discount_bps': sum(s['discount_bps'] * s['usd'] for s in sells) / sell_vol if sell_vol else None,
            'max_sell_discount_bps': max((s['discount_bps'] for s in sells), default=None),
            'max_sell_trade_usd': max((s['usd'] for s in sells), default=0.0),
            'p10_discount_bps': pct(discs, 0.10), 'p90_discount_bps': pct(discs, 0.90),
            'spread_bps': (pct(discs, 0.90) - pct(discs, 0.10)) if len(xs) >= MIN_TRADES_FOR_SPREAD else None,
            'nav': sum(s['nav'] * s['usd'] for s in xs) / vol if vol else None,
        })
    return rows


def noise_floor(rows):
    """The history's typical hourly p10-p90 spread, used where an hour has too few trades to have one of its own."""
    spreads = [r['spread_bps'] for r in rows if r['spread_bps'] is not None]
    return statistics.median(spreads) if spreads else 0.0


def segment_episodes(rows, round_trip_bps=ROUND_TRIP_BPS, floor_bps=None, max_gap_hours=2, cap_usd=CAPACITY_CAP_USD):
    """Consecutive hours whose volume-weighted discount clears the round trip AND its own price spread.

    This is `nav_discount`'s significance rule applied hour by hour: net = vw_discount - round_trip must exceed the
    hour's p10-p90 spread (significance >= 1). Hours with no trades are silent, not disqualifying: up to `max_gap_hours`
    of them may sit inside an episode. An hour with trades that fails the rule ends it.
    """
    floor = noise_floor(rows) if floor_bps is None else floor_bps
    qual = []
    for r in rows:
        vw = r['vw_discount_bps']
        spread = r['spread_bps'] if r['spread_bps'] is not None else floor
        net = (vw - round_trip_bps) if vw is not None else None
        ok = vw is not None and net > 0 and net > spread
        r['net_bps'] = net
        r['spread_used_bps'] = spread
        r['spread_source'] = 'hour' if r['spread_bps'] is not None else 'history-median'
        r['significance'] = (net / spread) if (net is not None and spread > 0) else (None if net is None else float('inf'))
        r['qualifies'] = ok
        qual.append(ok)
    episodes, cur = [], None
    for r in rows:
        if r['qualifies']:
            if cur and (r['hour'] - cur['hours'][-1]['hour']) // 3600 - 1 > max_gap_hours:
                episodes.append(cur)
                cur = None
            if cur is None:
                cur = {'hours': []}
            cur['hours'].append(r)
        elif cur is not None:
            episodes.append(cur)
            cur = None
    if cur:
        episodes.append(cur)
    out = []
    for e in episodes:
        hs = e['hours']
        vol = sum(h['volume_usd'] for h in hs)
        sell = sum(h['sell_volume_usd'] for h in hs)
        vw = sum((h['vw_discount_bps'] or 0) * h['volume_usd'] for h in hs) / vol if vol else 0.0
        net = vw - round_trip_bps
        fill = min(sell, cap_usd)
        # The exit depth is a per-day constraint (the USDe pool refills through arbitrage and the cooldown is one day),
        # so a position inside a multi-day episode can be refilled: the second number caps at `cap_usd` per day spanned.
        days_spanned = max(1, -(-((hs[-1]['hour'] - hs[0]['hour']) // 3600 + 1) // 24))
        fill_daily = min(sell, cap_usd * days_spanned)
        out.append({
            'start_utc': hs[0]['hour_utc'], 'end_utc': utc(hs[-1]['hour'] + 3600), 'start': hs[0]['hour'],
            'duration_hours': (hs[-1]['hour'] - hs[0]['hour']) // 3600 + 1, 'qualifying_hours': len(hs),
            'trades': sum(h['n'] for h in hs), 'volume_usd': vol, 'sell_volume_usd': sell,
            'vw_discount_bps': vw, 'net_bps': net,
            'max_sell_discount_bps': max((h['max_sell_discount_bps'] for h in hs if h['max_sell_discount_bps'] is not None), default=None),
            'fillable_usd': sell, 'fillable_capped_usd': fill, 'option_value_usd': fill * net / 1e4,
            'days_spanned': days_spanned, 'fillable_capped_daily_usd': fill_daily, 'option_value_daily_cap_usd': fill_daily * net / 1e4,
            'min_significance': min((h['significance'] for h in hs if h['significance'] is not None), default=None),
        })
    return out


# ----------------------------------------------------------------------------------------------------------------------
# collect
# ----------------------------------------------------------------------------------------------------------------------
def load_done(d):
    return read_json(d / 'done.json', [])


def gaps(done, first, last):
    covered = sorted((a, b) for a, b in done)
    out, cur = [], first
    for a, b in covered:
        if b < cur:
            continue
        if a > cur:
            out.append((cur, min(a - 1, last)))
        cur = max(cur, b + 1)
        if cur > last:
            break
    if cur <= last:
        out.append((cur, last))
    return out


def collect_stream(rpc, out, stream, first, last, batch_size, log):
    d = out / 'raw' / stream['name']
    d.mkdir(parents=True, exist_ok=True)
    done = load_done(d)
    pending = collections.deque()
    for a, b in gaps(done, first, last):
        for s in range(a, b + 1, RANGE_CAP):
            pending.append((s, min(s + RANGE_CAP - 1, b)))
    total, splits, entries, t0 = len(pending), 0, 0, time.monotonic()
    fetched = 0
    while pending:
        chunk = [pending.popleft() for _ in range(min(batch_size, len(pending)))]
        calls = [('eth_getLogs', [{'fromBlock': hex(a), 'toBlock': hex(b), 'address': stream['address'], 'topics': stream['topics']}])
                 for a, b in chunk]
        try:
            res = rpc.batch(calls, allow_errors=True)
        except RPCError as exc:
            msg = rpc.clean(str(exc))
            if 'ceiling' in msg:
                raise
            # A whole-batch failure after retries: halve every member and try again, one at a time.
            log({'batch_error': msg, 'ranges': chunk})
            for a, b in reversed(chunk):
                if a < b:
                    mid = (a + b) // 2
                    pending.appendleft((mid + 1, b))
                    pending.appendleft((a, mid))
                    splits += 1
                else:
                    raise
            continue
        for (a, b), r in zip(chunk, res):
            if isinstance(r, dict) and 'error' in r:
                err = r['error']
                data = err.get('data') if isinstance(err.get('data'), dict) else {}
                if a < b:
                    to = hx(data['to']) if 'to' in data else None
                    cut = to if (to is not None and a <= to < b) else (a + b) // 2
                    pending.appendleft((cut + 1, b))
                    pending.appendleft((a, cut))
                    splits += 1
                    continue
                raise RPCError('logs %d: %s' % (a, rpc.clean(json.dumps(err))))
            logs = r or []
            with gzip.open(d / ('%d_%d.json.gz' % (a, b)), 'wt') as f:
                json.dump(logs, f)
            done.append([a, b])
            entries += len(logs)
            fetched += 1
        write_json(d / 'done.json', done)
        if fetched % 20 == 0 or not pending:
            log({'stream': stream['name'], 'ranges_done': fetched, 'of_initial': total, 'splits': splits, 'logs': entries,
                 'elapsed_s': round(time.monotonic() - t0), **rpc.stats()})
    return {'ranges': len(done), 'splits': splits, 'log_entries_this_run': entries}


def pool_metadata(rpc):
    """Coin order and decimals for each Curve pool, read at latest; the v4 pool key is fixed by address order."""
    metas = []
    for p in POOLS + [BASIS_POOL]:
        if p['venue'] == 'curve':
            coins = []
            for i in range(4):
                r = rpc.call('eth_call', [{'to': p['address'], 'data': SEL_COINS + enc_uint(i)}, 'latest'], allow_errors=True)
                if isinstance(r, dict) or r in (None, '0x'):
                    r = rpc.call('eth_call', [{'to': p['address'], 'data': SEL_COINS_I128 + enc_uint(i)}, 'latest'], allow_errors=True)
                if isinstance(r, dict) or r in (None, '0x'):
                    break
                coins.append('0x' + r[-40:])
            want = p.get('usde', SUSDE)
            if want not in coins:
                raise RPCError('%s: %s is not a coin of the pool (%s)' % (p['name'], SYMBOLS.get(want, want), coins))
            decs = []
            for c in coins:
                r = rpc.call('eth_call', [{'to': c, 'data': SEL_DECIMALS}, 'latest'])
                decs.append(word(r, 0))
            metas.append({**p, 'coins': coins, 'decimals': decs, 'symbols': [SYMBOLS.get(c, c) for c in coins]})
        else:
            metas.append({**p, 'symbols': [SYMBOLS.get(p['currency0']), SYMBOLS.get(p['currency1'])]})
    return metas


def cmd_collect(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    log_f = (out / 'collect.log').open('a')

    def log(obj):
        line = json.dumps(obj, default=str)
        print(line, flush=True)
        log_f.write(line + '\n')
        log_f.flush()

    man = read_json(out / 'manifest.json', {})
    if man.get('first_block') and not args.reset:
        first, last = man['first_block'], man['last_block']
        log({'resume': True, 'first_block': first, 'last_block': last})
    else:
        head = rpc.call('eth_getBlockByNumber', ['finalized', False])
        last = hx(head['number'])
        first = last - args.days * BLOCKS_PER_DAY
        man = {'chain': 'ethereum', 'chain_id': 1, 'first_block': first, 'last_block': last, 'end_tag': 'finalized',
               'last_block_utc': utc(hx(head['timestamp'])), 'requested_days': args.days,
               'collect_started': utc(), 'raw_files': {}}
        log({'first_block': first, 'last_block': last, 'last_block_utc': man['last_block_utc']})
    man['endpoints'] = {'logs_headers_state_latest': 'Infura mainnet JSON-RPC, local keys rotated, never written',
                        'archive_state': 'public endpoints in drpc.ENDPOINTS, one call at a time (see nav)'}
    man['pools'] = pool_metadata(rpc)
    write_json(out / 'pools.json', man['pools'])

    # Header grid: one header a day plus both ends, for block <-> time interpolation.
    grid = list(range(first, last, BLOCKS_PER_DAY)) + [last]
    headers = read_json(out / 'headers.json', {}) or {}
    have = {int(k) for k in headers}
    todo = [n for n in grid if n not in have]
    for i in range(0, len(todo), 10):
        chunk = todo[i:i + 10]
        res = rpc.batch([('eth_getBlockByNumber', [hex(n), False]) for n in chunk])
        for n, b in zip(chunk, res):
            if not b or hx(b['number']) != n:
                raise RPCError('header %d missing' % n)
            headers[str(n)] = {'ts': hx(b['timestamp']), 'hash': b['hash']}
        write_json(out / 'headers.json', headers)
    man['headers'] = {'count': len(headers), 'step_blocks': BLOCKS_PER_DAY,
                      'first_utc': utc(headers[str(first)]['ts']), 'last_utc': utc(headers[str(last)]['ts'])}
    log({'headers': man['headers']})

    streams = [
        {'name': 'curve', 'address': [p['address'] for p in POOLS if p['venue'] == 'curve'],
         'topics': [[TOPICS['CurveEx'], TOPICS['CurveExU']]]},
        {'name': 'v4', 'address': [V4_MANAGER],
         'topics': [[TOPICS['V4Swap']], [p['pool_id'] for p in POOLS if p['venue'] == 'uniswap_v4']]},
        {'name': 'basis', 'address': [BASIS_POOL['address']], 'topics': [[TOPICS['CurveEx'], TOPICS['CurveExU']]]},
    ]
    man['streams'] = {}
    try:
        for s in streams:
            man['streams'][s['name']] = {'address': s['address'], 'topics': s['topics'], **collect_stream(rpc, out, s, first, last, args.batch, log)}
    finally:
        man['rpc'] = rpc.stats()
        man['collect_finished'] = utc()
        man['complete'] = all(not gaps(load_done(out / 'raw' / s['name']), first, last) for s in streams)
        for s in streams:
            d = out / 'raw' / s['name']
            man['raw_files'][s['name']] = {p.name: sha256(p) for p in sorted(d.glob('*.json.gz'))}
        man['topics'] = TOPICS
        write_json(out / 'manifest.json', man)
        log({'complete': man['complete'], **man['rpc']})


# ----------------------------------------------------------------------------------------------------------------------
# nav
# ----------------------------------------------------------------------------------------------------------------------
def archive_call(to, data, block, endpoints, errors):
    """eth_call at a historical block through public endpoints, one at a time. Returns (hex, endpoint) or (None, None)."""
    for ep in endpoints:
        try:
            r = drpc.rpc('eth_call', [{'to': to, 'data': data}, hex(block)], endpoints=[ep], timeout=60, retries=1)
            if r and r != '0x':
                return r, ep
            errors.append({'block': block, 'endpoint': ep, 'error': 'empty result'})
        except drpc.Revert as exc:
            errors.append({'block': block, 'endpoint': ep, 'error': 'revert-or-missing-state: ' + str(exc)[:160]})
        except Exception as exc:
            errors.append({'block': block, 'endpoint': ep, 'error': type(exc).__name__ + ': ' + str(exc)[:160]})
        time.sleep(0.3)
    return None, None


def cmd_nav(args):
    out = Path(args.out)
    headers = read_json(out / 'headers.json')
    if not headers:
        raise SystemExit('run collect first (nav needs the header grid)')
    # The grid carries both ends of the range, so nav can run while collect is still pulling logs. It never writes the
    # manifest: collect owns that file until it finishes, and analyze copies the NAV coverage in afterwards.
    grid = sorted(int(k) for k in headers)
    first, last = grid[0], grid[-1]
    nav = read_json(out / 'nav.json', {'samples': [], 'errors': [], 'probe': {}})
    have = {s['block'] for s in nav['samples']}
    data = SEL_CONVERT + enc_uint(10 ** 18)
    endpoints = list(args.endpoints.split(',')) if args.endpoints else list(drpc.ENDPOINTS)

    # Probe: does each endpoint answer historical state 90 days back and at the start of the range?
    probe = {}
    for depth_name, n in (('90d', last - 90 * BLOCKS_PER_DAY), ('start', first)):
        probe[depth_name] = {'block': n, 'endpoints': {}}
        for ep in endpoints:
            errs = []
            r, _ = archive_call(SUSDE, data, n, [ep], errs)
            probe[depth_name]['endpoints'][ep] = ('ok %.6f' % (int(r, 16) / 1e18)) if r else (errs[-1]['error'] if errs else 'no answer')
    nav['probe'] = probe
    ok_eps = [ep for ep in endpoints if str(probe['start']['endpoints'].get(ep, '')).startswith('ok')] or \
             [ep for ep in endpoints if str(probe['90d']['endpoints'].get(ep, '')).startswith('ok')] or endpoints
    nav['endpoints_in_order'] = ok_eps
    print(json.dumps({'probe': probe, 'using': ok_eps}, indent=1), flush=True)

    t0 = time.monotonic()
    for i, n in enumerate(grid):
        if n in have:
            continue
        sample = {'block': n, 'ts': headers[str(n)]['ts'], 'utc': utc(headers[str(n)]['ts'])}
        errs = []
        for tok, key in NAV_TOKENS.items():
            r, ep = None, None
            for attempt in range(3):
                r, ep = archive_call(tok, data, n, ok_eps, errs)
                if r:
                    break
                time.sleep(3 * (attempt + 1))
            if r:
                sample[key] = int(r, 16) / 1e18
                sample[key + '_endpoint'] = ep
            time.sleep(0.25)
        if 'susde' in sample:
            nav['samples'].append(sample)
        else:
            nav['errors'].extend(errs[-2:])
        if i % 10 == 0 or n == grid[-1]:
            nav['samples'].sort(key=lambda s: s['block'])
            write_json(out / 'nav.json', nav)
            print(json.dumps({'sampled': len(nav['samples']), 'of': len(grid), 'errors': len(nav['errors']), 'elapsed_s': round(time.monotonic() - t0)}), flush=True)
    nav['samples'].sort(key=lambda s: s['block'])
    s = nav['samples']
    nav['method'] = ('convertToAssets(1e18) on sUSDe and sDAI at each daily header block via public archive endpoints; '
                     'linear interpolation between samples in the analysis (sUSDe NAV drifts 1-3bp/day, so the error is under 1bp)')
    nav['coverage'] = {'first_block': s[0]['block'] if s else None, 'last_block': s[-1]['block'] if s else None,
                       'samples': len(s), 'grid': len(grid), 'sdai_samples': sum(1 for x in s if 'sdai' in x),
                       'susde_nav_first': s[0].get('susde') if s else None, 'susde_nav_last': s[-1].get('susde') if s else None}
    write_json(out / 'nav.json', nav)
    print(json.dumps(nav['coverage'], indent=1))


# ----------------------------------------------------------------------------------------------------------------------
# analyze
# ----------------------------------------------------------------------------------------------------------------------
def load_raw(out, stream):
    d = out / 'raw' / stream
    if not d.exists():
        return
    for p in sorted(d.glob('*.json.gz'), key=lambda p: int(p.name.split('_')[0])):
        with gzip.open(p, 'rt') as f:
            for l in json.load(f):
                yield l


def distribution(values):
    return {'p50': pct(values, .5), 'p90': pct(values, .9), 'p99': pct(values, .99), 'p99_9': pct(values, .999),
            'max': max(values) if values else None, 'min': min(values) if values else None}


def episode_block(swaps, rows, days, max_gap_hours, months):
    """Everything the summary reports about one discount series: distribution, episodes, option value."""
    floor = noise_floor(rows)
    episodes = segment_episodes(rows, ROUND_TRIP_BPS, floor, max_gap_hours, CAPACITY_CAP_USD)
    episodes.sort(key=lambda e: e['start'])
    vw = [r['vw_discount_bps'] for r in rows if r['vw_discount_bps'] is not None]
    mx = [r['max_sell_discount_bps'] for r in rows if r['max_sell_discount_bps'] is not None]
    sells = [s for s in swaps if s['side'] == 'sell']
    below_rt = [s for s in sells if s['discount_bps'] > ROUND_TRIP_BPS]
    per_month = collections.Counter(e['start_utc'][:7] for e in episodes)
    option = sum(e['option_value_usd'] for e in episodes)
    option_daily = sum(e['option_value_daily_cap_usd'] for e in episodes)
    trade_level = sum(s['usd'] * (s['discount_bps'] - ROUND_TRIP_BPS) / 1e4 for s in below_rt)
    sell_vol = sum(s['usd'] for s in sells)
    option_by_month = collections.defaultdict(float)
    for e in episodes:
        option_by_month[e['start_utc'][:7]] += e['option_value_usd']
    days_with_entry = len({(r['hour'] // 86400) for r in rows if r.get('qualifies')})
    return {
        'hours_with_trades': len(rows), 'noise_floor_spread_bps': floor,
        'days_with_a_qualifying_hour': days_with_entry, 'share_of_days_with_a_qualifying_hour': days_with_entry / days if days else None,
        'median_episode_hours': statistics.median([e['duration_hours'] for e in episodes]) if episodes else None,
        'option_value_by_month_usd': {m: option_by_month.get(m, 0.0) for m in months},
        'hourly_vw_discount_bps': {**distribution(vw), 'share_above_round_trip': sum(1 for x in vw if x > ROUND_TRIP_BPS) / len(vw) if vw else None,
                                   'share_at_least_5bp': sum(1 for x in vw if x >= 5) / len(vw) if vw else None,
                                   'share_at_least_10bp': sum(1 for x in vw if x >= 10) / len(vw) if vw else None,
                                   'share_at_least_20bp': sum(1 for x in vw if x >= 20) / len(vw) if vw else None},
        'hourly_max_sell_discount_bps': distribution(mx),
        'trade_discount_bps': {'sell_p50': pct([s['discount_bps'] for s in sells], .5), 'sell_p90': pct([s['discount_bps'] for s in sells], .9),
                               'sell_p99': pct([s['discount_bps'] for s in sells], .99), 'sell_max': max((s['discount_bps'] for s in sells), default=None),
                               'buy_p50': pct([s['discount_bps'] for s in swaps if s['side'] == 'buy'], .5)},
        'sells_below_nav_minus_round_trip': {'count': len(below_rt), 'usd': sum(s['usd'] for s in below_rt),
                                             'share_of_sell_volume': (sum(s['usd'] for s in below_rt) / sell_vol) if sell_vol else None},
        'episodes': {'count': len(episodes), 'per_month': {m: per_month.get(m, 0) for m in months},
                     'total_fillable_usd': sum(e['fillable_usd'] for e in episodes), 'total_fillable_capped_usd': sum(e['fillable_capped_usd'] for e in episodes),
                     'hours_in_episodes': sum(e['qualifying_hours'] for e in episodes),
                     'option_value_usd_history': option, 'option_value_usd_per_year': option * 365 / days if days else None,
                     'option_value_daily_cap_usd_history': option_daily, 'option_value_daily_cap_usd_per_year': option_daily * 365 / days if days else None,
                     'total_fillable_capped_daily_usd': sum(e['fillable_capped_daily_usd'] for e in episodes),
                     'trade_level_upper_bound_usd_history': trade_level, 'trade_level_upper_bound_usd_per_year': trade_level * 365 / days if days else None,
                     'deepest': sorted(episodes, key=lambda e: -(e['max_sell_discount_bps'] or -1e9))[:10],
                     'most_valuable': sorted(episodes, key=lambda e: -e['option_value_usd'])[:10]},
        'deepest_sell_trades': sorted(sells, key=lambda s: -s['discount_bps'])[:15],
    }, episodes, rows


def kill_slices(sells, first_ts, last_ts, field='discount_bps'):
    slices, t = [], first_ts
    while t < last_ts:
        end = min(t + 30 * 86400, last_ts)
        in_slice = [s for s in sells if t <= s['ts'] < end and s.get(field) is not None]
        sized = [s for s in in_slice if s['usd'] >= KILL_MIN_USD]
        deep = [s for s in sized if s[field] >= KILL_BPS]
        deep_any = [s for s in in_slice if s[field] >= KILL_BPS]
        best = max(sized, key=lambda s: s[field], default=None)
        slices.append({'start_utc': utc(t), 'end_utc': utc(end), 'days': round((end - t) / 86400, 1), 'partial': (end - t) < 30 * 86400 - 1,
                       'sells': len(in_slice), 'sells_at_least_10k': len(sized),
                       'max_sell_discount_bps_10k': best[field] if best else None,
                       'max_sell_discount_tx': best['tx'] if best else None, 'max_sell_discount_utc': best['utc'] if best else None,
                       'sells_10k_at_or_below_nav_minus_10bp': len(deep), 'sells_any_size_at_or_below_nav_minus_10bp': len(deep_any),
                       'usd_10k_at_or_below_nav_minus_10bp': sum(s['usd'] for s in deep),
                       'kill_criterion_met': not deep})
        t = end
    return slices


def cmd_analyze(args):
    out = Path(args.out)
    man = read_json(out / 'manifest.json')
    headers = read_json(out / 'headers.json')
    nav = read_json(out / 'nav.json')
    pools = read_json(out / 'pools.json')
    if not (man and headers and nav and pools):
        raise SystemExit('run collect and nav first')
    hb = sorted(int(k) for k in headers)
    hts = [headers[str(n)]['ts'] for n in hb]
    samples = [s for s in nav['samples'] if 'susde' in s]
    if not samples:
        raise SystemExit('no NAV samples')
    nb = [s['block'] for s in samples]
    grids = {SUSDE: (nb, [s['susde'] for s in samples]),
             SDAI: ([s['block'] for s in samples if 'sdai' in s], [s['sdai'] for s in samples if 'sdai' in s])}
    # The history is only as long as the NAV series: a swap before the first sample cannot be priced honestly.
    nav_first, nav_last = nb[0], nb[-1]

    def nav_at(tok, n):
        xs, ys = grids[tok]
        return interp(xs, ys, n)

    def ts_at(n):
        return int(round(interp(hb, hts, n)))

    swaps, skipped, excluded = [], collections.Counter(), []
    for stream, decode in (('curve', decode_curve), ('v4', decode_v4)):
        for l in load_raw(out, stream):
            n = hx(l['blockNumber'])
            if n < nav_first or n > nav_last:
                skipped['outside-nav-range'] += 1
                continue
            addr = l['address'].lower()
            if stream == 'curve':
                meta = next((m for m in pools if m['venue'] == 'curve' and m['address'] == addr), None)
            else:
                meta = next((m for m in pools if m['venue'] == 'uniswap_v4' and len(l['topics']) == 3 and l['topics'][1] == m['pool_id']), None)
            if meta is None:
                skipped['unknown-pool'] += 1
                continue
            s = decode(l, meta, nav_at)
            if s is None:
                skipped['undecodable'] += 1
                continue
            if s['usd'] < MIN_TRADE_USD:
                skipped['dust'] += 1
                continue
            s['ts'] = ts_at(n)
            s['utc'] = utc(s['ts'])
            s['excluded_print'] = abs(s['discount_bps']) > args.max_print_bps
            swaps.append(s)
    swaps.sort(key=lambda s: (s['block'], s['li']))

    # USDe basis: the price the exit leg realises, per hour.
    basis_meta = next((m for m in pools if m.get('usde')), None)
    basis_swaps, basis_excluded = [], []
    if basis_meta:
        for l in load_raw(out, 'basis'):
            b = decode_basis(l, basis_meta)
            if b and b['usde'] >= MIN_TRADE_USD and nav_first <= b['block'] <= nav_last:
                b['ts'] = ts_at(b['block'])
                if abs(1.0 - b['price']) * 1e4 > args.max_print_bps:
                    basis_excluded.append(b)       # the same venue-failure bound as the sUSDe prints
                    continue
                basis_swaps.append(b)
    basis_hours = hourly_basis(basis_swaps)
    for s in swaps:
        bb, age = basis_at(basis_hours, s['ts'] // 3600 * 3600)
        s['usde_basis_bps'] = bb
        s['usde_basis_age_hours'] = age
        s['discount_net_basis_bps'] = (s['discount_bps'] - bb) if bb is not None else None
    with gzip.open(out / 'discounts.jsonl.gz', 'wt') as f:
        for s in swaps:
            f.write(json.dumps(s) + '\n')

    kept = [s for s in swaps if not s['excluded_print']]
    excluded = [s for s in swaps if s['excluded_print']]
    first_ts, last_ts = ts_at(nav_first), ts_at(nav_last)
    days = (last_ts - first_ts) / 86400.0
    months = sorted({utc(t)[:7] for t in range(first_ts, last_ts + 1, 86400)})

    raw_block, raw_eps, raw_rows = episode_block(kept, hourly_series(kept), days, args.max_gap_hours, months)
    netted = [dict(s, discount_bps=s['discount_net_basis_bps'], raw_discount_bps=s['discount_bps'])
              for s in kept if s['discount_net_basis_bps'] is not None]
    net_block, net_eps, net_rows = episode_block(netted, hourly_series(netted), days, args.max_gap_hours, months) if netted else (None, [], [])

    sells = [s for s in kept if s['side'] == 'sell']
    by_pool = {}
    for m in pools:
        if m.get('usde'):
            continue
        xs = [s for s in kept if s['pool'] == m['name']]
        if not xs:
            by_pool[m['name']] = {'swaps': 0}
            continue
        vol = sum(s['usd'] for s in xs)
        by_pool[m['name']] = {'swaps': len(xs), 'volume_usd': vol, 'sell_volume_usd': sum(s['usd'] for s in xs if s['side'] == 'sell'),
                              'vw_discount_bps': sum(s['discount_bps'] * s['usd'] for s in xs) / vol,
                              'median_discount_bps': statistics.median(s['discount_bps'] for s in xs),
                              'median_sell_discount_bps': statistics.median([s['discount_bps'] for s in xs if s['side'] == 'sell'] or [0]),
                              'median_buy_discount_bps': statistics.median([s['discount_bps'] for s in xs if s['side'] == 'buy'] or [0]),
                              'first_utc': xs[0]['utc'], 'last_utc': xs[-1]['utc']}
    monthly = []
    for mth in months:
        xs = [s for s in kept if s['utc'][:7] == mth]
        ss = [s for s in xs if s['side'] == 'sell']
        vol, sv = sum(s['usd'] for s in xs), sum(s['usd'] for s in ss)
        bh = [b for h, b in basis_hours.items() if utc(h)[:7] == mth]
        bu = sum(b['usde'] for b in bh)
        nx = [s for s in xs if s['discount_net_basis_bps'] is not None]
        nv = sum(s['usd'] for s in nx)
        monthly.append({'month': mth, 'swaps': len(xs), 'volume_usd': vol, 'sell_volume_usd': sv,
                        'vw_discount_bps': sum(s['discount_bps'] * s['usd'] for s in xs) / vol if vol else None,
                        'vw_sell_discount_bps': sum(s['discount_bps'] * s['usd'] for s in ss) / sv if sv else None,
                        'share_sell_vol_at_least_5bp': sum(s['usd'] for s in ss if s['discount_bps'] >= 5) / sv if sv else None,
                        'share_sell_vol_at_least_10bp': sum(s['usd'] for s in ss if s['discount_bps'] >= 10) / sv if sv else None,
                        'share_sell_vol_at_least_20bp': sum(s['usd'] for s in ss if s['discount_bps'] >= 20) / sv if sv else None,
                        'usde_basis_bps_vw': (sum(b['basis_bps'] * b['usde'] for b in bh) / bu) if bu else None,
                        'usde_basis_hours': len(bh), 'usde_volume_usd': bu,
                        'vw_discount_net_basis_bps': sum(s['discount_net_basis_bps'] * s['usd'] for s in nx) / nv if nv else None})

    summary = {
        'generated': utc(), 'first_block': nav_first, 'last_block': nav_last, 'first_utc': utc(first_ts), 'last_utc': utc(last_ts),
        'days_covered': round(days, 2), 'blocks_in_manifest': [man['first_block'], man['last_block']],
        'swaps_priced': len(kept), 'sells': len(sells), 'buys': len(kept) - len(sells), 'skipped': dict(skipped),
        'excluded_prints': {'bound_bps': args.max_print_bps, 'count': len(excluded), 'usd': sum(s['usd'] for s in excluded),
                            'prints': [{k: s[k] for k in ('utc', 'pool', 'side', 'usd', 'price', 'nav', 'discount_bps', 'tx')} for s in excluded]},
        'volume_usd': sum(s['usd'] for s in kept), 'sell_volume_usd': sum(s['usd'] for s in sells),
        'hours_in_history': int(days * 24), 'round_trip_bps': ROUND_TRIP_BPS, 'capacity_cap_usd': CAPACITY_CAP_USD,
        'max_gap_hours': args.max_gap_hours, 'min_trade_usd': MIN_TRADE_USD,
        'raw': raw_block,
        'net_of_usde_basis': net_block,
        'basis': {'pool': basis_meta['name'] if basis_meta else None, 'swaps': len(basis_swaps), 'hours': len(basis_hours),
                  'excluded_prints': len(basis_excluded), 'excluded_usde': sum(b['usde'] for b in basis_excluded),
                  'usde_volume_usd': sum(b['usde'] for b in basis_swaps),
                  'hourly_basis_bps': distribution([b['basis_bps'] for b in basis_hours.values()]),
                  'swaps_with_basis': sum(1 for s in kept if s['discount_net_basis_bps'] is not None),
                  'swaps_without_basis': sum(1 for s in kept if s['discount_net_basis_bps'] is None)},
        'kill_criterion': {'rule': 'no sUSDe sell of at least $%d at or below NAV - %.0fbp in a 30-day slice' % (KILL_MIN_USD, KILL_BPS),
                           'slices': kill_slices(sells, first_ts, last_ts),
                           'slices_net_of_basis': kill_slices(sells, first_ts, last_ts, 'discount_net_basis_bps')},
        'by_pool': by_pool, 'monthly': monthly,
        'nav': {'susde_first': samples[0]['susde'], 'susde_last': samples[-1]['susde'], 'samples': len(samples)},
        'assumptions': [
            'NAV is sampled once a day and interpolated linearly between samples; sUSDe NAV vests continuously and drifts 1-3bp a day, so the error is under 1bp.',
            'Swap timestamps are interpolated from one header a day; hourly buckets can be misassigned by a few minutes at their edges.',
            'The sDAI leg is valued at its own NAV in DAI and DAI at par; USDT, frxUSD and USDC are taken at par. A stablecoin trading off par moves the measured discount one for one.',
            'The raw discount includes USDe’s own price against the dollar. The strategy exits by selling USDe, so the series net of the hourly Curve USDe/USDC price is the capturable one; hours without a USDe/USDC trade inherit the last basis up to %d hours back.' % BASIS_CARRY_HOURS,
            'Discounts are effective trade prices including the pool fee paid by that trader. A buyer stepping in after a seller pays the fee again; the 2.7bp round trip is meant to cover the buy leg and the USDe exit.',
            'Single prints more than %.0fbp from NAV are a venue running out of liquidity, not a market for sUSDe; they are listed and excluded from the series.' % args.max_print_bps,
            'Three sUSDe pools are read. Volume on other venues, over-the-counter flow and direct Ethena redemptions are not seen, so fillable volume is a lower bound on what was offered and an upper bound on what one bid could have taken from these pools.',
            'In an AMM the volume sold during an episode is what pushed the price down; a bid that absorbs it also lifts the price, so fillable volume is a generous capacity.',
            'Hours with fewer than %d trades borrow the history-wide median hourly p10-p90 spread as their noise floor.' % MIN_TRADES_FOR_SPREAD,
            'Uniswap v4 deltas are taken from the Swap event; the saved live windows confirmed this pool settles those deltas as real transfers through the PoolManager.',
        ],
    }
    for k in ('slices', 'slices_net_of_basis'):
        summary['kill_criterion'][k + '_met'] = sum(1 for x in summary['kill_criterion'][k] if x['kill_criterion_met'])
    summary['kill_criterion']['slices_total'] = len(summary['kill_criterion']['slices'])
    write_json(out / 'hourly.json', {'raw': raw_rows, 'net_of_usde_basis': net_rows,
                                     'usde_basis': [{'hour': h, 'hour_utc': utc(h), **b} for h, b in sorted(basis_hours.items())]})
    write_json(out / 'episodes.json', {'params': {'round_trip_bps': ROUND_TRIP_BPS, 'noise_floor_spread_bps_raw': raw_block['noise_floor_spread_bps'],
                                                  'noise_floor_spread_bps_net': net_block['noise_floor_spread_bps'] if net_block else None,
                                                  'max_gap_hours': args.max_gap_hours, 'capacity_cap_usd': CAPACITY_CAP_USD,
                                                  'min_trade_usd': MIN_TRADE_USD, 'max_print_bps': args.max_print_bps},
                                       'episodes': raw_eps, 'episodes_net_of_usde_basis': net_eps})
    write_json(out / 'summary.json', summary)
    man['analysis'] = {'generated': summary['generated'], 'swaps_priced': len(kept), 'episodes_raw': len(raw_eps), 'episodes_net': len(net_eps)}
    man['nav'] = nav.get('coverage')
    man['archive_probe'] = nav.get('probe')
    man['archive_endpoints_in_order'] = nav.get('endpoints_in_order')
    man['file_hashes'] = {p.name: sha256(p) for p in sorted(out.glob('*.json')) + sorted(out.glob('*.jsonl.gz')) if p.name != 'manifest.json'}
    write_json(out / 'manifest.json', man)
    for label, blk in (('raw', raw_block), ('net_of_usde_basis', net_block)):
        if not blk:
            continue
        e = blk['episodes']
        print(json.dumps({label: {'hours_with_trades': blk['hours_with_trades'], 'noise_floor_bps': round(blk['noise_floor_spread_bps'], 2),
                                  'hourly_vw': {k: (round(v, 2) if isinstance(v, float) else v) for k, v in blk['hourly_vw_discount_bps'].items()},
                                  'hourly_max_sell': {k: (round(v, 2) if isinstance(v, float) else v) for k, v in blk['hourly_max_sell_discount_bps'].items()},
                                  'episodes': e['count'], 'per_month': e['per_month'], 'hours_in_episodes': e['hours_in_episodes'],
                                  'fillable_capped_usd': round(e['total_fillable_capped_usd']),
                                  'option_value_usd_per_year': round(e['option_value_usd_per_year']),
                                  'option_value_daily_cap_usd_per_year': round(e['option_value_daily_cap_usd_per_year']),
                                  'trade_level_upper_bound_usd_per_year': round(e['trade_level_upper_bound_usd_per_year'])}}, indent=1))
    print(json.dumps({'excluded_prints': summary['excluded_prints']['count'], 'basis': {k: v for k, v in summary['basis'].items() if k != 'hourly_basis_bps'},
                      'basis_dist': {k: (round(v, 2) if isinstance(v, float) else v) for k, v in summary['basis']['hourly_basis_bps'].items()},
                      'kill_slices_met_raw': '%d/%d' % (summary['kill_criterion']['slices_met'], summary['kill_criterion']['slices_total']),
                      'kill_slices_met_net': '%d/%d' % (summary['kill_criterion']['slices_net_of_basis_met'], summary['kill_criterion']['slices_total'])}, indent=1))


# ----------------------------------------------------------------------------------------------------------------------
# render
# ----------------------------------------------------------------------------------------------------------------------
def fmt_usd(v):
    return '-' if v is None else '$%s' % format(round(v), ',')


def fmt_bps(v):
    return '-' if v is None else '%.1f' % v


def fmt_pct(v):
    return '-' if v is None else '%.0f%%' % (100 * v)


def render_block(title, blk, note):
    L = ['## %s' % title, '', note, '',
         'Hours with at least one priced trade: %d. Noise floor (median hourly p10-p90 spread): %.2fbp.' % (blk['hours_with_trades'], blk['noise_floor_spread_bps']), '',
         '| series | p50 | p90 | p99 | p99.9 | max | min |', '|---|---:|---:|---:|---:|---:|---:|']
    for name, key in (('volume-weighted discount, all trades', 'hourly_vw_discount_bps'), ('deepest sell of the hour', 'hourly_max_sell_discount_bps')):
        d = blk[key]
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (name, fmt_bps(d['p50']), fmt_bps(d['p90']), fmt_bps(d['p99']), fmt_bps(d['p99_9']), fmt_bps(d['max']), fmt_bps(d['min'])))
    h = blk['hourly_vw_discount_bps']
    t = blk['trade_discount_bps']
    L += ['', 'Share of trading hours with a VW discount above the round trip %s, at least 5bp %s, 10bp %s, 20bp %s. Per trade: sells p50 %sbp, p90 %sbp, p99 %sbp, max %sbp; buys p50 %sbp.' % (
        fmt_pct(h['share_above_round_trip']), fmt_pct(h['share_at_least_5bp']), fmt_pct(h['share_at_least_10bp']), fmt_pct(h['share_at_least_20bp']),
        fmt_bps(t['sell_p50']), fmt_bps(t['sell_p90']), fmt_bps(t['sell_p99']), fmt_bps(t['sell_max']), fmt_bps(t['buy_p50']))]
    b = blk['sells_below_nav_minus_round_trip']
    L += ['', 'Sells below NAV minus the round trip: %d trades, %s, %s of sell volume.' % (b['count'], fmt_usd(b['usd']), fmt_pct(b['share_of_sell_volume'])), '']
    e = blk['episodes']
    L += ['| month | episodes | option value |', '|---|---:|---:|'] + ['| %s | %d | %s |' % (m, n, fmt_usd(blk['option_value_by_month_usd'].get(m))) for m, n in e['per_month'].items()]
    L += ['', 'Days with at least one qualifying hour: %d of %.0f (%s); median episode length %s hours.' % (
        blk['days_with_a_qualifying_hour'], blk['days_with_a_qualifying_hour'] / blk['share_of_days_with_a_qualifying_hour'] if blk['share_of_days_with_a_qualifying_hour'] else 0,
        fmt_pct(blk['share_of_days_with_a_qualifying_hour']), '-' if blk['median_episode_hours'] is None else '%.0f' % blk['median_episode_hours'])]
    L += ['', 'Episodes %d, hours inside episodes %d, fillable sell volume %s (%s after the per-episode cap).' % (
        e['count'], e['hours_in_episodes'], fmt_usd(e['total_fillable_usd']), fmt_usd(e['total_fillable_capped_usd'])),
          '**Option value over the history %s, annualised %s a year** with one %s fill per episode; %s a year if the position is refilled once a day inside a multi-day episode (%s fillable). Trade-level upper bound (every sell below the round trip bought at its own price, uncapped, no competition): %s a year.' % (
              fmt_usd(e['option_value_usd_history']), fmt_usd(e['option_value_usd_per_year']), fmt_usd(CAPACITY_CAP_USD), fmt_usd(e['option_value_daily_cap_usd_per_year']),
              fmt_usd(e['total_fillable_capped_daily_usd']), fmt_usd(e['trade_level_upper_bound_usd_per_year'])), '']
    L += ['### Ten deepest episodes', '', '| start (UTC) | hours | trades | VW discount bp | deepest sell bp | sell volume | net bp | option value | min significance |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for x in e['deepest']:
        L.append('| %s | %d | %d | %s | %s | %s | %s | %s | %s |' % (x['start_utc'], x['duration_hours'], x['trades'], fmt_bps(x['vw_discount_bps']),
                                                                     fmt_bps(x['max_sell_discount_bps']), fmt_usd(x['sell_volume_usd']), fmt_bps(x['net_bps']),
                                                                     fmt_usd(x['option_value_usd']), '-' if x['min_significance'] is None else '%.2f' % x['min_significance']))
    L += ['', '### Ten most valuable episodes', '', '| start (UTC) | hours | VW discount bp | sell volume | capped | net bp | option value | daily-cap option value |', '|---|---:|---:|---:|---:|---:|---:|---:|']
    for x in e['most_valuable']:
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s |' % (x['start_utc'], x['duration_hours'], fmt_bps(x['vw_discount_bps']), fmt_usd(x['sell_volume_usd']),
                                                               fmt_usd(x['fillable_capped_usd']), fmt_bps(x['net_bps']), fmt_usd(x['option_value_usd']), fmt_usd(x['option_value_daily_cap_usd'])))
    L += ['', '### Fifteen deepest sells', '', '| when (UTC) | pool | sUSDe | notional at NAV | price | NAV | discount bp | tx |', '|---|---|---:|---:|---:|---:|---:|---|']
    for s in blk['deepest_sell_trades']:
        L.append('| %s | %s | %s | %s | %.5f | %.5f | %s | [%s](https://etherscan.io/tx/%s) |' % (
            s['utc'][:16], s['pool'], format(round(s['susde']), ','), fmt_usd(s['usd']), s['price'], s['nav'], fmt_bps(s['discount_bps']), s['tx'][:10], s['tx']))
    return L + ['']


def render_slices(title, slices, met, total):
    L = ['### %s' % title, '', 'Met in %d of %d slices.' % (met, total), '',
         '| slice start | days | sells >= $10k | deepest sell >= $10k (bp) | when | sells >= $10k at NAV-10bp or deeper | any size | verdict |',
         '|---|---:|---:|---:|---|---:|---:|---|']
    for s in slices:
        L.append('| %s | %.0f%s | %d | %s | %s | %d (%s) | %d | %s |' % (
            s['start_utc'][:10], s['days'], '*' if s['partial'] else '', s['sells_at_least_10k'], fmt_bps(s['max_sell_discount_bps_10k']),
            (s['max_sell_discount_utc'] or '-')[:16], s['sells_10k_at_or_below_nav_minus_10bp'], fmt_usd(s['usd_10k_at_or_below_nav_minus_10bp']),
            s['sells_any_size_at_or_below_nav_minus_10bp'], 'criterion met (kill)' if s['kill_criterion_met'] else 'not met (keep)'))
    return L + ['', '* partial slice', '']


def cmd_render(args):
    out = Path(args.out)
    S = read_json(out / 'summary.json')
    if not S:
        raise SystemExit('run analyze first')
    L = ['# sUSDe discount history, tables', '',
         'Window %s to %s (blocks %d to %d, %.1f days). %d priced swaps (%d sells, %d buys), %s traded at NAV; %d dust swaps under %s skipped; %d prints beyond %.0fbp excluded (%s).' % (
             S['first_utc'], S['last_utc'], S['first_block'], S['last_block'], S['days_covered'], S['swaps_priced'], S['sells'], S['buys'], fmt_usd(S['volume_usd']),
             S['skipped'].get('dust', 0), fmt_usd(S['min_trade_usd']), S['excluded_prints']['count'], S['excluded_prints']['bound_bps'], fmt_usd(S['excluded_prints']['usd'])),
         'Round trip %.1fbp, capacity cap %s per episode, gaps of up to %d empty hours allowed inside an episode. sUSDe NAV %.6f at the start, %.6f at the end (%d daily samples).' % (
             S['round_trip_bps'], fmt_usd(S['capacity_cap_usd']), S['max_gap_hours'], S['nav']['susde_first'], S['nav']['susde_last'], S['nav']['samples']), '']
    L += render_block('A. Raw discount to NAV (the other leg at its NAV or at par)', S['raw'],
                      'This is the number the `nav_discount` detector measures on a window. It includes USDe’s own price against the dollar.')
    if S.get('net_of_usde_basis'):
        bs = S['basis']
        d = bs['hourly_basis_bps']
        L += render_block('B. Discount net of the USDe basis (what a cooldown redemption that exits into a dollar captures)', S['net_of_usde_basis'],
                          'Each swap’s discount less the same hour’s USDe price gap to par on Curve USDe/USDC (%d swaps, %s of USDe, %d hours, %d prints beyond the bound excluded; hourly basis p50 %sbp, p90 %sbp, p99 %sbp, max %sbp, min %sbp). %d swaps had a basis within 24h, %d did not.' % (
                              bs['swaps'], fmt_usd(bs['usde_volume_usd']), bs['hours'], bs['excluded_prints'], fmt_bps(d['p50']), fmt_bps(d['p90']), fmt_bps(d['p99']), fmt_bps(d['max']), fmt_bps(d['min']),
                              bs['swaps_with_basis'], bs['swaps_without_basis']))
    L += ['## C. Month by month', '', '| month | swaps | sell volume | VW discount bp | VW sell discount bp | sell vol >= 5bp | >= 10bp | >= 20bp | USDe basis bp (VW) | VW discount net of basis bp |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for m in S['monthly']:
        L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (m['month'], m['swaps'], fmt_usd(m['sell_volume_usd']), fmt_bps(m['vw_discount_bps']), fmt_bps(m['vw_sell_discount_bps']),
                                                                         fmt_pct(m['share_sell_vol_at_least_5bp']), fmt_pct(m['share_sell_vol_at_least_10bp']), fmt_pct(m['share_sell_vol_at_least_20bp']),
                                                                         fmt_bps(m['usde_basis_bps_vw']), fmt_bps(m['vw_discount_net_basis_bps'])))
    k = S['kill_criterion']
    L += ['', '## D. Kill criterion by 30-day slice', '', k['rule'] + '.', '']
    L += render_slices('Raw discount', k['slices'], k['slices_met'], k['slices_total'])
    if k.get('slices_net_of_basis'):
        L += render_slices('Net of the USDe basis', k['slices_net_of_basis'], k['slices_net_of_basis_met'], k['slices_total'])
    L += ['## E. By pool (raw)', '', '| pool | swaps | volume | sell volume | VW discount bp | median bp | median sell bp | median buy bp | first | last |', '|---|---:|---:|---:|---:|---:|---:|---:|---|---|']
    for name, p in S['by_pool'].items():
        if p.get('swaps'):
            L.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (name, p['swaps'], fmt_usd(p['volume_usd']), fmt_usd(p['sell_volume_usd']), fmt_bps(p['vw_discount_bps']),
                                                                             fmt_bps(p['median_discount_bps']), fmt_bps(p['median_sell_discount_bps']), fmt_bps(p['median_buy_discount_bps']),
                                                                             p['first_utc'][:10], p['last_utc'][:10]))
        else:
            L.append('| %s | 0 | - | - | - | - | - | - | - | - |' % name)
    ex = S['excluded_prints']
    L += ['', '## F. Prints excluded as venue liquidity failures (beyond %.0fbp)' % ex['bound_bps'], '', '| when (UTC) | pool | side | notional at NAV | price | NAV | discount bp | tx |', '|---|---|---|---:|---:|---:|---:|---|']
    for s in ex['prints']:
        L.append('| %s | %s | %s | %s | %.5f | %.5f | %s | [%s](https://etherscan.io/tx/%s) |' % (s['utc'][:16], s['pool'], s['side'], fmt_usd(s['usd']), s['price'], s['nav'], fmt_bps(s['discount_bps']), s['tx'][:10], s['tx']))
    L += ['', '## Assumptions', ''] + ['- ' + a for a in S['assumptions']]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')
    if not (out / 'findings.md').exists() or args.force_findings:
        (out / 'findings.md').write_text('# sUSDe discount history: findings\n\n(write the interpretation here; every number is in tables.md and summary.json)\n')
        print('wrote a findings.md skeleton')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('collect')
    a.add_argument('--out', required=True)
    a.add_argument('--days', type=int, default=180)
    a.add_argument('--batch', type=int, default=4, help='eth_getLogs ranges per HTTP request')
    a.add_argument('--max-credits', type=int, default=300_000)
    a.add_argument('--reset', action='store_true', help='ignore a saved block range and pin a new one')
    b = sub.add_parser('nav')
    b.add_argument('--out', required=True)
    b.add_argument('--endpoints', help='comma-separated archive endpoints; default drpc.ENDPOINTS')
    c = sub.add_parser('analyze')
    c.add_argument('--out', required=True)
    c.add_argument('--max-gap-hours', type=int, default=2)
    c.add_argument('--max-print-bps', type=float, default=MAX_PRINT_BPS)
    d = sub.add_parser('render')
    d.add_argument('--out', required=True)
    d.add_argument('--force-findings', action='store_true')
    args = p.parse_args()
    {'collect': cmd_collect, 'nav': cmd_nav, 'analyze': cmd_analyze, 'render': cmd_render}[args.cmd](args)


if __name__ == '__main__':
    main()
