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

The redemption surface (2026-10-09). With `--assets`, the same four commands ask the question of every asset in
`SURFACE` (stETH/wstETH, weETH, rsETH, ezETH, rETH, syrupUSDC/USDT, sUSDe, USDe, and two same-block controls):
Curve, Uniswap v3/v4 and Fluid swaps priced in each asset's unit, queue waits measured from the protocols' own events
or counters, payouts checked against the NAV function, and a trade-by-trade bid with capital locked by the queue,
capped at the market-wide discount, its hurdle chosen on the first half of the window and scored on the second
(`backtest.choose_then_test`). Without `--assets` the sUSDe study runs exactly as before.

    uv run --with pycryptodome python scripts/dislocation_history.py collect --out research/2026-10-09/redemption_history --assets all
    uv run --with pycryptodome python scripts/dislocation_history.py nav     --out research/2026-10-09/redemption_history --assets all
    uv run --with pycryptodome python scripts/dislocation_history.py analyze --out research/2026-10-09/redemption_history --assets all
    uv run --with pycryptodome python scripts/dislocation_history.py render  --out research/2026-10-09/redemption_history --assets all
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
from live_rpc import RPC, RPCError, hx, word, sword, topic_addr, enc_uint, enc_addr  # noqa: E402


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


# ======================================================================================================================
# The redemption surface (2026-10-09): the sUSDe question asked of every claim a protocol redeems at NAV
# ======================================================================================================================
# Everything above is the sUSDe study and is left exactly as it was, so its numbers reproduce. Everything below asks the
# same question of every Ethereum asset whose issuer redeems it at NAV, instantly or behind a queue, with three changes
# the wider surface forced:
#
#   * the venues are Curve, Uniswap v3 and v4, and Fluid, and a swap is priced in the asset's unit (ETH for staking
#     tokens, dollars for the rest) against the NAV the protocol paid at that block;
#   * the bid is simulated trade by trade rather than once per episode, because a queue locks the capital: a bid that
#     fills on Monday into a 14-day queue cannot fill again on Tuesday, and that, not the offered volume, is what caps
#     a slow queue;
#   * every parameter the bid chooses (its hurdle) is chosen on the first half of the window and scored on the second,
#     through `backtest.choose_then_test`, so the headline is an out-of-sample number.
#
# The cost of buying behind a seller is two pool fees, not one: the seller's effective price already carries their fee,
# and buying the same amount back from the pool pays the mid plus a fee again, so the buyer's price is the seller's
# times (1 + f) / (1 - f).

ROOT_DIR = Path(__file__).resolve().parents[1]
SURFACE_FIRST_BLOCK = 24_650_913   # the sUSDe study's first block (2026-03-13 20:24 UTC): every asset shares its window
ETH_SENTINEL = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'   # Curve's and Fluid's name for native ether
NATIVE = '0x0000000000000000000000000000000000000000'         # Uniswap v4's name for native ether
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
STETH = '0xae7ab96520de3a18e5e111b5eaab095312d7fe84'
WSTETH = '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'
WEETH = '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee'
RSETH = '0xa1290d69c65a6fe4df752f95823fae25cb99e5a7'
EZETH = '0xbf5495efe5db9ce00f80364c8b423567e58d2110'
RETH = '0xae78736cd615f374d3085123a210448e74fc6393'
SYRUPUSDC = '0x80ac24aa929eaf5013f6436cda2a7ba190f5cc0b'
SYRUPUSDT = '0x356b8d89c1e1239cbbb9de4815c39a1474d5ba7d'
SFRXUSD = '0xcf62f905562626cfcdd2261162a51fd02fc9c5b6'
SUSDS = '0xa3931d71877c0e7a3148cb7eb4463524fec27fbd'
DOLA = '0x865377367054516e17014ccded1e7d814edc9ce4'
LIDO_WQ = '0x889edc2edab5f40e902b864ad4d7ade8e412f9b1'
ETHERFI_WRNFT = '0x7d5706f6ef3f89b3951e23e557cdfbc3239d4e2c'
ETHERFI_RM = '0xdadef1ffbfeaab4f68a9fd181395f68b4e4e7ae0'
KELP_ORACLE = '0x349a73444b1a310bae67ef67973022020d70020d'
KELP_WM = '0x62de59c08eb5dae4b7e6f7a8cad3006d6965ec16'
RENZO_RATE = '0x387dbc0fb00b26fb085aa658527d5be98302c84c'
RENZO_WQ = '0x5efc9d10e42fb517456f4ac41eb5e2ebe42c8918'
MAPLE_WM = {SYRUPUSDC: '0x1bc47a0dd0fdab96e9ef982fdf1f34dc6207cfe3', SYRUPUSDT: '0x86ebdf902d800f2a82038290b6dbb2a5ee29eb8c'}
SYMBOLS.update({ETH_SENTINEL: 'ETH', NATIVE: 'ETH', WETH: 'WETH', STETH: 'stETH', WSTETH: 'wstETH', WEETH: 'weETH',
                RSETH: 'rsETH', EZETH: 'ezETH', RETH: 'rETH', SYRUPUSDC: 'syrupUSDC', SYRUPUSDT: 'syrupUSDT',
                SFRXUSD: 'sfrxUSD', SUSDS: 'sUSDS', DOLA: 'DOLA'})

XTOPICS = {
    'CurveEx': TOPICS['CurveEx'], 'CurveExU': TOPICS['CurveExU'], 'V4Swap': TOPICS['V4Swap'],
    'V3Swap': keccak('Swap(address,address,int256,int256,uint160,uint128,int24)'),
    'FluidSwap': keccak('Swap(bool,uint256,uint256,address)'),
    'LidoRequested': keccak('WithdrawalRequested(uint256,address,address,uint256,uint256)'),
    'LidoFinalized': keccak('WithdrawalsFinalized(uint256,uint256,uint256,uint256,uint256)'),
    'MapleCreated': keccak('RequestCreated(uint256,address,uint256)'),
    'MapleProcessed': keccak('RequestProcessed(uint256,address,uint256,uint256)'),
    'EtherFiRedeemed': keccak('Redeemed(address,uint256,uint256,uint256,address)'),
    # What a redemption actually paid, to check each NAV function against the protocol's own payouts.
    'KelpQueued': keccak('AssetWithdrawalQueued(address,address,uint256,uint256)'),
    'KelpFinalized': keccak('AssetWithdrawalFinalized(address,address,uint256,uint256)'),
    'RenzoCreated': keccak('WithdrawRequestCreated(uint256,address,address,uint256,uint256,uint256,bool,uint256)'),
    'LidoClaimed': keccak('WithdrawalClaimed(uint256,address,address,uint256)'),
}

# Archive reads on the daily header grid. `scale` turns the returned word into a number; `every` thins a slow parameter.
STATE = {
    'wsteth_nav': {'to': WSTETH, 'data': sel('stEthPerToken()'), 'scale': 1e18},
    'weeth_nav': {'to': WEETH, 'data': sel('getRate()'), 'scale': 1e18},
    'etherfi_last_finalized': {'to': ETHERFI_WRNFT, 'data': sel('lastFinalizedRequestId()'), 'scale': 1},
    'etherfi_next_request': {'to': ETHERFI_WRNFT, 'data': sel('nextRequestId()'), 'scale': 1},
    'rseth_nav': {'to': KELP_ORACLE, 'data': sel('rsETHPrice()'), 'scale': 1e18},
    'kelp_next_locked': {'to': KELP_WM, 'data': sel('nextLockedNonce(address)') + enc_addr(ETH_SENTINEL), 'scale': 1},
    'kelp_next_unused': {'to': KELP_WM, 'data': sel('nextUnusedNonce(address)') + enc_addr(ETH_SENTINEL), 'scale': 1},
    'ezeth_nav': {'to': RENZO_RATE, 'data': sel('getRate()'), 'scale': 1e18},
    'renzo_cooldown': {'to': RENZO_WQ, 'data': sel('coolDownPeriod()'), 'scale': 1, 'every': 30},
    'reth_nav': {'to': RETH, 'data': sel('getExchangeRate()'), 'scale': 1e18},
    'reth_collateral': {'to': RETH, 'data': sel('getTotalCollateral()'), 'scale': 1e18},
    'syrupusdc_nav': {'to': SYRUPUSDC, 'data': sel('convertToAssets(uint256)') + enc_uint(10 ** 6), 'scale': 1e6},
    'syrupusdt_nav': {'to': SYRUPUSDT, 'data': sel('convertToAssets(uint256)') + enc_uint(10 ** 6), 'scale': 1e6},
    'sfrxusd_nav': {'to': SFRXUSD, 'data': SEL_CONVERT + enc_uint(10 ** 18), 'scale': 1e18},
    'susds_nav': {'to': SUSDS, 'data': SEL_CONVERT + enc_uint(10 ** 18), 'scale': 1e18},
    'susde_nav': {'to': SUSDE, 'data': SEL_CONVERT + enc_uint(10 ** 18), 'scale': 1e18},
    'sdai_nav': {'to': SDAI, 'data': SEL_CONVERT + enc_uint(10 ** 18), 'scale': 1e18},
}

# The assets. Pools were chosen from GeckoTerminal's top pools by 24h volume on 2026-10-09 (`pools_discovered.json`),
# keeping only pools whose other side is the redemption unit at par (ETH/WETH, USDC/USDT) or a token whose NAV is read.
# `quotes` maps the other side's token to None (par in the unit) or to a STATE key (its own NAV in the unit).
# Fees: Curve `fee()` and Uniswap v3 `fee()` are read on chain at collection; v4 carries its fee in every Swap event;
# Fluid's come from its public API (`configs.fee`, hundredths of a basis point), and 1bp is assumed where the API does
# not list the pool.
ETH_QUOTES = {ETH_SENTINEL: None, WETH: None, NATIVE: None}
SURFACE = {
    'lido': {
        'label': 'stETH / wstETH (Lido)', 'unit': 'ETH',
        'targets': {STETH: {'symbol': 'stETH', 'nav': None}, WSTETH: {'symbol': 'wstETH', 'nav': 'wsteth_nav'}},
        'quotes': ETH_QUOTES,
        'pools': [{'name': 'curve-steth-eth', 'venue': 'curve', 'address': '0xdc24316b9ae028f1497c275eb9192a3ea0f67022'},
                  {'name': 'curve-steth-ng', 'venue': 'curve', 'address': '0x21e27a5e5513d6e65c4f830167390997aa84843a'},
                  {'name': 'fluid-wsteth-eth', 'venue': 'fluid', 'address': '0x0b1a513ee24972daef112bc777a5610d4325c9e7',
                   'tokens': [WSTETH, ETH_SENTINEL], 'decimals': [18, 18], 'fee_bps': 1.0, 'fee_source': 'Fluid API configs.fee=100'},
                  {'name': 'v3-wsteth-weth-1bp', 'venue': 'uniswap_v3', 'address': '0x109830a1aaad605bbf02a9dfa7b0b92ec2fb7daa'}],
        'redemption': {'path': 'Lido WithdrawalQueueERC721: request, wait for finalization, claim ETH', 'wait': 'lido',
                       'fee_bps': 0.0, 'accrues': False, 'permissioned': False,
                       'note': 'stETH stops earning at the request; the ETH owed is fixed then, lower only in bunker mode'}},
    'etherfi': {
        'label': 'weETH (ether.fi)', 'unit': 'ETH',
        'targets': {WEETH: {'symbol': 'weETH', 'nav': 'weeth_nav'}}, 'quotes': ETH_QUOTES,
        'pools': [{'name': 'fluid-weeth-eth', 'venue': 'fluid', 'address': '0x86f874212335af27c41cdb855c2255543d1499ce',
                   'tokens': [WEETH, ETH_SENTINEL], 'decimals': [18, 18], 'fee_bps': 0.83, 'fee_source': 'Fluid API configs.fee=83'},
                  {'name': 'curve-weeth-weth', 'venue': 'curve', 'address': '0xdb74dfdd3bb46be8ce6c33dc9d82777bcfc3ded5'},
                  {'name': 'v3-weeth-weth-1bp', 'venue': 'uniswap_v3', 'address': '0x202a6012894ae5c288ea824cbc8a9bfb26a49b93'}],
        'redemption': {'path': 'ether.fi WithdrawRequestNFT queue (unwrap weETH, request, wait for finalization, claim)',
                       'wait': 'pointer', 'created': 'etherfi_next_request', 'finalized': 'etherfi_last_finalized',
                       'finalized_inclusive': True, 'fee_bps': 0.0, 'accrues': False, 'permissioned': False,
                       'instant': {'fee_bps': 10.0, 'into': 'stETH', 'cap_per_day': 5000.0,
                                   'source': 'EtherFiRedemptionManager.tokenToRedemptionInfo(stETH) read 2026-10-10: exit fee 10bp, '
                                             'bucket 5,000; ETH output 30bp and unavailable at the read'},
                       'note': 'eETH stops earning at the request (amount fixed at request)'}},
    'kelp': {
        'label': 'rsETH (Kelp)', 'unit': 'ETH',
        'targets': {RSETH: {'symbol': 'rsETH', 'nav': 'rseth_nav'}}, 'quotes': ETH_QUOTES,
        'pools': [{'name': 'fluid-rseth-eth', 'venue': 'fluid', 'address': '0x276084527b801e00db8e4410504f9baf93f72c67',
                   'tokens': [RSETH, ETH_SENTINEL], 'decimals': [18, 18], 'fee_bps': 1.0, 'fee_source': 'assumed (pool not in the Fluid API list)'},
                  {'name': 'v4-rseth-eth-5bp', 'venue': 'uniswap_v4', 'pool_id': '0x3ffa23dc8cbb32957059d95efdc2722e1206e295fe72c90d4563721937921f5a',
                   'tokens': [NATIVE, RSETH]}],
        'redemption': {'path': 'Kelp LRTWithdrawalManager: queue rsETH for ETH, wait for the unlock, complete',
                       'wait': 'pointer', 'created': 'kelp_next_unused', 'finalized': 'kelp_next_locked',
                       'finalized_inclusive': False, 'fee_bps': 0.0, 'accrues': False, 'permissioned': False,
                       'note': 'amount fixed at the request; instant withdrawal exists in the contract (50bp) but was disabled for ETH at the 2026-10-10 read'}},
    'renzo': {
        'label': 'ezETH (Renzo)', 'unit': 'ETH',
        'targets': {EZETH: {'symbol': 'ezETH', 'nav': 'ezeth_nav'}}, 'quotes': ETH_QUOTES,
        'pools': [{'name': 'fluid-ezeth-eth', 'venue': 'fluid', 'address': '0xdd72157a021804141817d46d9852a97addfb9f59',
                   'tokens': [EZETH, ETH_SENTINEL], 'decimals': [18, 18], 'fee_bps': 1.0, 'fee_source': 'assumed (pool not in the Fluid API list)'}],
        'redemption': {'path': 'Renzo WithdrawQueue: request, wait coolDownPeriod, claim', 'wait': 'seconds', 'key': 'renzo_cooldown',
                       'fee_bps': 0.0, 'accrues': False, 'permissioned': False, 'note': 'coolDownPeriod read on chain'}},
    'rocketpool': {
        'label': 'rETH (Rocket Pool)', 'unit': 'ETH',
        'targets': {RETH: {'symbol': 'rETH', 'nav': 'reth_nav'}}, 'quotes': ETH_QUOTES,
        'pools': [{'name': 'v3-reth-weth-1bp', 'venue': 'uniswap_v3', 'address': '0x553e9c493678d8606d6a5ba284643db2110df823'},
                  {'name': 'v4-reth-eth-1bp', 'venue': 'uniswap_v4', 'pool_id': '0x70946c979da3e5587a00b3a750cc76902d187894501ba9e8be9efd1849b6e0b7',
                   'tokens': [NATIVE, RETH]},
                  {'name': 'curve-reth-weth', 'venue': 'curve', 'address': '0x9efe1a1cbd6ca51ee8319afc4573d253c3b732af'}],
        'redemption': {'path': 'rETH.burn(): instant, only up to getTotalCollateral() (rETH balance plus deposit-pool excess)',
                       'wait': 'instant', 'daily_cap_state': 'reth_collateral', 'fee_bps': 0.0, 'accrues': False, 'permissioned': False}},
    'maple_usdc': {
        'label': 'syrupUSDC (Maple)', 'unit': 'USD',
        'targets': {SYRUPUSDC: {'symbol': 'syrupUSDC', 'nav': 'syrupusdc_nav'}}, 'quotes': {USDC: None},
        'pools': [{'name': 'v4-syrupusdc-usdc-8bp', 'venue': 'uniswap_v4', 'pool_id': '0xcdb422a853a4fa2deb364317db92ad76d1cb7a8e1b82a32219bcb41720a90228',
                   'tokens': [SYRUPUSDC, USDC]},
                  {'name': 'fluid-syrupusdc-usdc', 'venue': 'fluid', 'address': '0x79eea4a1be86c43a9a9c4384b0b28a07af24ae29',
                   'tokens': [SYRUPUSDC, USDC], 'decimals': [6, 6], 'fee_bps': 5.0, 'fee_source': 'Fluid API configs.fee=500'}],
        'redemption': {'path': 'Maple WithdrawalManager queue: requestRedeem, processed by the pool delegate', 'wait': 'maple',
                       'wm': MAPLE_WM[SYRUPUSDC], 'fee_bps': 0.0, 'accrues': True, 'permissioned': False,
                       'note': 'shares are redeemed at the exchange rate when processed, so the position keeps earning while queued'}},
    'maple_usdt': {
        'label': 'syrupUSDT (Maple)', 'unit': 'USD',
        'targets': {SYRUPUSDT: {'symbol': 'syrupUSDT', 'nav': 'syrupusdt_nav'}}, 'quotes': {USDT: None},
        'pools': [{'name': 'v4-syrupusdt-usdt-8bp', 'venue': 'uniswap_v4', 'pool_id': '0xd861038a98942312d1495dd1313fb66c7e7de48f549a15edf3a45decf7338e1d',
                   'tokens': [SYRUPUSDT, USDT]}],
        'redemption': {'path': 'Maple WithdrawalManager queue', 'wait': 'maple', 'wm': MAPLE_WM[SYRUPUSDT], 'fee_bps': 0.0,
                       'accrues': True, 'permissioned': False, 'note': 'as syrupUSDC'}},
    'frax': {
        'label': 'sfrxUSD (Frax) — instant control', 'unit': 'USD',
        'targets': {SFRXUSD: {'symbol': 'sfrxUSD', 'nav': 'sfrxusd_nav'}}, 'quotes': {FRXUSD: None},
        'pools': [{'name': 'curve-sfrxusd-frxusd', 'venue': 'curve', 'address': '0xf292eb6c5dcb693eaaf392d0562a01c3710e5978'}],
        'redemption': {'path': 'ERC-4626 redeem into frxUSD, same block', 'wait': 'instant', 'fee_bps': 0.0, 'accrues': False,
                       'permissioned': False, 'control': True,
                       'note': 'the unit is frxUSD itself, so the discount needs no dollar basis; an atomic arbitrage, i.e. a control'}},
    'sky': {
        'label': 'sUSDS (Sky) — instant control', 'unit': 'USD',
        'targets': {SUSDS: {'symbol': 'sUSDS', 'nav': 'susds_nav'}}, 'quotes': {DOLA: None, FRXUSD: None, USDT: None},
        'pools': [{'name': 'curve-dola-susds', 'venue': 'curve', 'address': '0x8b83c4aa949254895507d09365229bc3a8c7f710'},
                  {'name': 'curve-frxusd-susds', 'venue': 'curve', 'address': '0x81a2612f6dea269a6dd1f6deab45c5424ee2c4b7'},
                  {'name': 'curve-susds-usdt', 'venue': 'curve', 'address': '0x00836fe54625be242bcfa286207795405ca4fd10'}],
        'redemption': {'path': 'ERC-4626 redeem into USDS, same block', 'wait': 'instant', 'fee_bps': 0.0, 'accrues': False,
                       'permissioned': False, 'control': True,
                       'note': 'DOLA and frxUSD are taken at par, so their own basis is inside the measured discount'}},
    'usde': {
        'label': 'USDe (Ethena) — permissioned redemption', 'unit': 'USD',
        'targets': {USDE: {'symbol': 'USDe', 'nav': None}}, 'quotes': {USDC: None, USDT: None},
        'pools': [{'name': 'curve-usdt-usde', 'venue': 'curve', 'address': '0x5b03cccab7ba3010fa5cad23746cbf0794938e96'},
                  {'name': 'curve-usde-usdc', 'venue': 'curve', 'address': '0x02950460e2b9529d0e00284a5fa2d7bdf3fa4d72'},
                  {'name': 'v3-usde-usdc-1bp', 'venue': 'uniswap_v3', 'address': '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a'},
                  {'name': 'fluid-usde-usdt', 'venue': 'fluid', 'address': '0xf063bd202e45d6b2843102cb4ece339026645d4a',
                   'tokens': [USDE, USDT], 'decimals': [18, 6], 'fee_bps': 1.0, 'fee_source': 'Fluid API configs.fee=100'}],
        'redemption': {'path': 'EthenaMinting.redeem: same block, approved redeemers only', 'wait': 'instant', 'fee_bps': 0.0,
                       'accrues': False, 'permissioned': True,
                       'note': 'the Uniswap v4 USDe/USDC 0.003% pool (~$13M/day) is not read: too many swaps for this pass'}},
    'susde': {
        'label': 'sUSDe (Ethena) — the 2026-09-10 study, extended', 'unit': 'USD',
        'targets': {SUSDE: {'symbol': 'sUSDe', 'nav': 'susde_nav'}}, 'quotes': {USDT: None, FRXUSD: None, SDAI: 'sdai_nav'},
        'pools': [{**POOLS[0]}, {**POOLS[1]}, {**POOLS[2], 'tokens': [SUSDE, USDT]}],
        'legacy_raw': 'raw/susde_legacy', 'basis': True,
        'redemption': {'path': 'cooldownShares, wait cooldownDuration (1 day), unstake to USDe, sell USDe on Curve',
                       'wait': 'constant', 'days': 1.0, 'fee_bps': 0.0, 'accrues': False, 'permissioned': False,
                       'exit_cap_usd_per_day': CAPACITY_CAP_USD,
                       'note': 'USDe is fixed at the cooldown; the exit sells USDe, so discounts are netted of its hourly basis'}},
}
# ezETH and the rest of the long tail (cbETH ~$2k/day, pufETH ~$16k/day, eETH none) are kept or dropped by volume.
SKIPPED = {
    'cbETH': 'Curve and Uniswap v3 pools trade ~$2.4k a day together, and unwrapping is a Coinbase account action',
    'pufETH': 'pools trade ~$16k a day; the vault exit fee read 0 but the daily withdrawal limit was not read',
    'eETH': 'no pool with volume; it trades as weETH',
    'sDAI': 'its only live pool is against sUSDe; sUSDS is the Sky control',
    'USDe v4 0.003%': 'about $13M a day of swaps, too many logs for this pass; the other four USDe venues are read',
}

SIZES_USD = [100_000, 300_000, 1_000_000, 3_000_000, 10_000_000, 30_000_000]
HURDLES_BPS = [0.0, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
GAS_PER_FILL_USD = 10.0           # buy + request + claim at 2026 gas, generously
MIN_FILL_USD = 5_000.0
FEE_LEGS = 2.0                    # the seller's fee is inside their price; buying it back pays the mid plus a fee again
CAPACITY_SHARE = 0.9              # capacity: the smallest tested size that earns this share of the best size's value
ETH_STAKING_FALLBACK = 0.026
SSR_FALLBACK = 0.038              # sUSDS.ssr() read 2026-10-09 (coordinator); the history uses the sUSDS NAV itself


# ---------------------------------------------------------------------------------------------------------------- legs
def orient(tin, ain, tout, aout, targets):
    """(side, target, target_amount, other, other_amount) for a swap that moves exactly one target token, else None.
    `sell` means the target went into the pool: a holder sold the claim, which is the price a patient bid can match."""
    if tin in targets and tout not in targets:
        return 'sell', tin, ain, tout, aout
    if tout in targets and tin not in targets:
        return 'buy', tout, aout, tin, ain
    return None


def legs_curve(log, meta, targets):
    d = log['data']
    if len(d) < 2 + 64 * 4:
        return None
    i, sold, j, bought = word(d, 0), word(d, 1), word(d, 2), word(d, 3)
    coins, decs = meta['coins'], meta['decimals']
    if i >= len(coins) or j >= len(coins) or i == j:
        return None
    o = orient(coins[i], sold / 10 ** decs[i], coins[j], bought / 10 ** decs[j], targets)
    return None if o is None else o + (meta['fee_bps'],)


def legs_v3(log, meta, targets):
    """Uniswap v3 amounts are the POOL's deltas: positive means the swapper paid that token in."""
    if len(log['topics']) != 3:
        return None
    d = log['data']
    a0, a1 = sword(d, 0), sword(d, 1)
    if a0 == 0 or a1 == 0 or (a0 > 0) == (a1 > 0):
        return None
    (t0, t1), (d0, d1) = meta['tokens'], meta['decimals']
    x0, x1 = abs(a0) / 10 ** d0, abs(a1) / 10 ** d1
    o = orient(t0, x0, t1, x1, targets) if a0 > 0 else orient(t1, x1, t0, x0, targets)
    return None if o is None else o + (meta['fee_bps'],)


def legs_v4(log, meta, targets):
    """Uniswap v4 amounts are the SWAPPER's deltas: negative means paid into the pool (the opposite sign of v3)."""
    tp = log['topics']
    if len(tp) != 3 or tp[1] != meta['pool_id']:
        return None
    d = log['data']
    a0, a1 = sword(d, 0), sword(d, 1)
    if a0 == 0 or a1 == 0 or (a0 < 0) == (a1 < 0):
        return None
    (t0, t1), (d0, d1) = meta['tokens'], meta['decimals']
    x0, x1 = abs(a0) / 10 ** d0, abs(a1) / 10 ** d1
    o = orient(t0, x0, t1, x1, targets) if a0 < 0 else orient(t1, x1, t0, x0, targets)
    return None if o is None else o + (word(d, 5) / 100.0,)


def legs_fluid(log, meta, targets):
    """Fluid DEX `Swap(bool swap0to1, uint256 amountIn, uint256 amountOut, address to)`, amounts in token decimals."""
    d = log['data']
    if len(d) < 2 + 64 * 3:
        return None
    s01, ain, aout = word(d, 0), word(d, 1), word(d, 2)
    (t0, t1), (d0, d1) = meta['tokens'], meta['decimals']
    if s01:
        o = orient(t0, ain / 10 ** d0, t1, aout / 10 ** d1, targets)
    else:
        o = orient(t1, ain / 10 ** d1, t0, aout / 10 ** d0, targets)
    return None if o is None else o + (meta['fee_bps'],)


LEGS = {'curve': legs_curve, 'uniswap_v3': legs_v3, 'uniswap_v4': legs_v4, 'fluid': legs_fluid}


def price_swap(asset, legs, block, nav_at):
    """Discount of one swap to the target's NAV in the asset's unit. `nav_at(key, block)` reads a STATE series."""
    side, tgt, ta, other, oa, fee_bps = legs
    spec = asset['targets'][tgt]
    if other not in asset['quotes'] or ta <= 0 or oa <= 0:
        return None
    tnav = 1.0 if spec['nav'] is None else nav_at(spec['nav'], block)
    q = asset['quotes'][other]
    onav = 1.0 if q is None else nav_at(q, block)
    if not tnav or not onav:
        return None
    price = oa * onav / ta
    return {'side': side, 'token': spec['symbol'], 'amount': ta, 'other_symbol': SYMBOLS.get(other, other), 'other': oa,
            'nav': tnav, 'price': price, 'discount_bps': 1e4 * (tnav - price) / tnav, 'unit_value': ta * tnav,
            'fee_bps': fee_bps}


# ------------------------------------------------------------------------------------------------- redemption waits
def lido_waits(requests, finals, end_ts):
    """Request id -> (request ts, wait in days or None if still pending at `end_ts`, lower bound in days).

    `requests` is {id: ts}; `finals` is [(from_id, to_id, ts)] from `WithdrawalsFinalized`, which finalizes a contiguous
    id range. A request's wait is the first finalization whose range holds it, minus its own request time.
    """
    fins = sorted(finals)
    out = {}
    for rid, ts in requests.items():
        lo, hi, hit = 0, len(fins) - 1, None
        while lo <= hi:
            mid = (lo + hi) // 2
            a, b, t = fins[mid]
            if rid < a:
                hi = mid - 1
            elif rid > b:
                lo = mid + 1
            else:
                hit = t
                break
        if hit is not None and hit >= ts:
            out[rid] = (ts, (hit - ts) / 86400.0, None)
        else:
            out[rid] = (ts, None, (end_ts - ts) / 86400.0)
    return out


def pointer_waits(samples_created, samples_final, final_inclusive, floor_days=1.0):
    """Waits from two monotone counters sampled on a grid: `created` is the next id to be assigned, `final` the last
    finalized id (`final_inclusive`) or the first unfinalized one. Ids created between two samples take the later
    sample's time; they count as finalized at the first sample whose counter has passed their median id. Resolution is
    the grid step, so a wait is never reported below `floor_days` (a same-day finalization counts as one day rather
    than none). Returns [(created_ts, wait_days or None, lower_bound_days)]."""
    sc = sorted(samples_created)
    sf = dict(samples_final)
    ts_grid = [t for t, _ in sc]
    nxt_unfin = [(sf.get(t) + 1 if final_inclusive else sf.get(t)) if sf.get(t) is not None else None for t in ts_grid]
    out = []
    for i in range(1, len(sc)):
        c0, c1 = sc[i - 1][1], sc[i][1]
        if c1 is None or c0 is None or c1 <= c0:
            continue
        mid = (c0 + c1 - 1) / 2.0
        hit = None
        for j in range(i, len(sc)):
            if nxt_unfin[j] is not None and nxt_unfin[j] > mid:
                hit = j
                break
        if hit is None:
            out.append((ts_grid[i], None, (ts_grid[-1] - ts_grid[i]) / 86400.0))
        else:
            out.append((ts_grid[i], max(floor_days, (ts_grid[hit] - ts_grid[i]) / 86400.0), None))
    return out


def daily_wait_fn(points, default_days):
    """A step function ts -> wait days from [(ts, wait or None, lower_bound)]: the median by UTC day, censored waits
    entering at their lower bound, days without requests inheriting the previous day."""
    by = collections.defaultdict(list)
    for ts, w, lb in points:
        by[ts // 86400].append(w if w is not None else lb)
    days = sorted(by)
    med = {d: statistics.median(by[d]) for d in days}

    def f(ts):
        d = ts // 86400
        if d in med:
            return med[d]
        k = None
        lo, hi = 0, len(days) - 1
        while lo <= hi:
            m = (lo + hi) // 2
            if days[m] <= d:
                k = m
                lo = m + 1
            else:
                hi = m - 1
        return med[days[k]] if k is not None else (med[days[0]] if days else default_days)
    return f, med


# ------------------------------------------------------------------------------------------------------- the bid
def simulate_bid(sells, size_usd, hurdle_bps, wait_days_at, carry_bps_per_day_at, accrues=False, fee_legs=FEE_LEGS,
                 redemption_fee_bps=0.0, gas_usd=GAS_PER_FILL_USD, min_fill_usd=MIN_FILL_USD, daily_cap_usd_at=None,
                 market_bps_at=None):
    """Back-run every sell whose edge clears the hurdle, with capital that the redemption locks.

    Each sell (chronological; `ts`, `usd` notional at NAV, `discount_bps`, `fee_bps`) is matched at the seller's price
    plus `fee_legs` pool fees, for at most its own size, the capital not locked in earlier redemptions, and what is left
    of a daily exit cap. Edge = discount - fee_legs x fee - wait x carry (zero when the position accrues while queued) -
    redemption fee. A fill locks its capital for the wait. Returns (fills, stats).

    `market_bps_at(ts)` caps the discount at the market's (the median venue's) less one fee. A sale that knocks one
    pool 20bp under NAV while the other venues sit at 1bp is an atomic cross-venue arbitrage, which searchers take in
    the same block; a patient bid that redeems is only paid for the part of the discount the whole market shows.
    """
    import heapq
    heap, locked = [], 0.0
    used = collections.defaultdict(float)
    fills = []
    st = {'qualifying_sells': 0, 'qualifying_usd': 0.0, 'filled_usd': 0.0, 'missed_capital_usd': 0.0, 'missed_cap_usd': 0.0}
    for s in sells:
        while heap and heap[0][0] <= s['ts']:
            locked -= heapq.heappop(heap)[1]
        wait = wait_days_at(s['ts'])
        carry = 0.0 if accrues else wait * carry_bps_per_day_at(s['ts'])
        disc = s['discount_bps'] - fee_legs * s['fee_bps']
        if market_bps_at is not None:
            m = market_bps_at(s['ts'])
            if m is not None:
                disc = min(disc, m - s['fee_bps'])
        edge = disc - carry - redemption_fee_bps
        if edge <= hurdle_bps or s['usd'] * edge / 1e4 <= gas_usd:
            continue
        st['qualifying_sells'] += 1
        st['qualifying_usd'] += s['usd']
        avail = max(0.0, size_usd - locked)
        day = s['ts'] // 86400
        cap_left = float('inf') if daily_cap_usd_at is None else max(0.0, daily_cap_usd_at(s['ts']) - used[day])
        fill = min(s['usd'], avail, cap_left)
        if fill < s['usd']:
            if avail <= cap_left:
                st['missed_capital_usd'] += s['usd'] - fill
            else:
                st['missed_cap_usd'] += s['usd'] - fill
        value = fill * edge / 1e4 - gas_usd
        if fill < min_fill_usd or value <= 0:
            continue
        used[day] += fill
        st['filled_usd'] += fill
        fills.append({'ts': s['ts'], 'usd': fill, 'edge_bps': edge, 'value_usd': value, 'wait_days': wait,
                      'discount_bps': s['discount_bps'], 'pool': s.get('pool'), 'tx': s.get('tx')})
        if wait > 0:
            heapq.heappush(heap, (s['ts'] + wait * 86400.0, fill))
            locked += fill
    return fills, st


def market_discount_fn(records, lookback_hours=6):
    """ts -> the median, across venues, of each venue's most recent hourly volume-weighted discount (all trades, both
    sides) within `lookback_hours`; None when no venue traded. The median, not the minimum: an oracle-centred pool can
    print near NAV with little depth behind it while the rest of the market trades far lower (weETH, April 2026)."""
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))
    for r in records:
        a = acc[r['pool']][r['ts'] // 3600 * 3600]
        a[0] += r['discount_bps'] * r['usd']
        a[1] += r['usd']
    venues = {v: (sorted(hs), {h: x[0] / x[1] for h, x in hs.items() if x[1]}) for v, hs in acc.items()}

    def f(ts):
        h = ts // 3600 * 3600
        vals = []
        for hours, vw in venues.values():
            j = _bisect_right(hours, h) - 1
            if j >= 0 and h - hours[j] <= lookback_hours * 3600:
                vals.append(vw[hours[j]])
        return statistics.median(vals) if vals else None
    return f


def daily_values(fills, first_day, n_days):
    v = [0.0] * n_days
    for f in fills:
        k = int(f['ts'] // 86400) - first_day
        if 0 <= k < n_days:
            v[k] += f['value_usd']
    return v


def capacity_size(values_by_size, share=CAPACITY_SHARE):
    """The smallest size whose value reaches `share` of the best size's; None when nothing earns."""
    best = max(values_by_size.values(), default=0.0)
    if best <= 0:
        return None
    for size in sorted(values_by_size):
        if values_by_size[size] >= share * best:
            return size
    return None


def apr_from_nav(series, days_min=1.0):
    """Annualised growth of a NAV series [(ts, nav)] across its span (compounded), None if too short."""
    s = sorted((t, v) for t, v in series if v)
    if len(s) < 2 or (s[-1][0] - s[0][0]) < days_min * 86400:
        return None
    yrs = (s[-1][0] - s[0][0]) / (365.0 * 86400)
    return (s[-1][1] / s[0][1]) ** (1.0 / yrs) - 1.0


def trailing_rate_fn(series, window_days=7.0, fallback=None):
    """ts -> annual rate implied by the NAV over the trailing `window_days` (compounded); `fallback` before history."""
    s = sorted((t, v) for t, v in series if v)
    ts = [t for t, _ in s]

    def f(t):
        if len(s) < 2:
            return fallback
        j = max(0, min(len(s) - 1, _bisect_right(ts, t) - 1))
        i = j
        while i > 0 and ts[j] - ts[i] < window_days * 86400:
            i -= 1
        if j == i:
            j = min(len(s) - 1, i + 1)
        r = apr_from_nav([s[i], s[j]], days_min=0.5)
        return r if r is not None else fallback
    return f


def _bisect_right(xs, x):
    lo, hi = 0, len(xs)
    while lo < hi:
        m = (lo + hi) // 2
        if xs[m] <= x:
            lo = m + 1
        else:
            hi = m
    return lo


# --------------------------------------------------------------------------------------------- surface: collect
def surface_pool_metadata(rpc, keys):
    """Coins, decimals and fees for every pool of the selected assets, read at latest and written to pools.json."""
    dec_cache = {ETH_SENTINEL: 18, NATIVE: 18}

    def decimals(tok):
        if tok not in dec_cache:
            dec_cache[tok] = word(rpc.call('eth_call', [{'to': tok, 'data': SEL_DECIMALS}, 'latest']), 0)
        return dec_cache[tok]

    out = {}
    for k in keys:
        a = SURFACE[k]
        metas = []
        for p in a['pools']:
            m = dict(p)
            if p['venue'] == 'curve':
                coins = []
                for i in range(4):
                    r = rpc.call('eth_call', [{'to': p['address'], 'data': SEL_COINS + enc_uint(i)}, 'latest'], allow_errors=True)
                    if isinstance(r, dict) or r in (None, '0x'):
                        r = rpc.call('eth_call', [{'to': p['address'], 'data': SEL_COINS_I128 + enc_uint(i)}, 'latest'], allow_errors=True)
                    if isinstance(r, dict) or r in (None, '0x'):
                        break
                    coins.append('0x' + r[-40:])
                fee = rpc.call('eth_call', [{'to': p['address'], 'data': sel('fee()')}, 'latest'])
                m.update({'coins': coins, 'decimals': [decimals(c) for c in coins], 'fee_bps': word(fee, 0) / 1e6,
                          'fee_source': 'fee() at latest'})
                m['symbols'] = [SYMBOLS.get(c, c) for c in coins]
            elif p['venue'] == 'uniswap_v3':
                t0 = '0x' + rpc.call('eth_call', [{'to': p['address'], 'data': sel('token0()')}, 'latest'])[-40:]
                t1 = '0x' + rpc.call('eth_call', [{'to': p['address'], 'data': sel('token1()')}, 'latest'])[-40:]
                fee = rpc.call('eth_call', [{'to': p['address'], 'data': sel('fee()')}, 'latest'])
                m.update({'tokens': [t0, t1], 'decimals': [decimals(t0), decimals(t1)], 'fee_bps': word(fee, 0) / 100.0,
                          'fee_source': 'fee() at latest'})
            elif p['venue'] == 'uniswap_v4':
                m.update({'decimals': [decimals(t) for t in p['tokens']], 'fee_source': 'per swap, from the event'})
            else:
                m['decimals'] = p.get('decimals') or [decimals(t) for t in p['tokens']]
            if p['venue'] != 'curve':
                m['symbols'] = [SYMBOLS.get(t, t) for t in m['tokens']]
            toks = m.get('coins') or m.get('tokens')
            if not any(t in a['targets'] for t in toks) or not any(t in a['quotes'] for t in toks):
                raise RPCError('%s/%s: pool tokens %s do not pair a target with a priced quote' % (k, p['name'], toks))
            metas.append(m)
        out[k] = metas
    return out


def surface_streams(keys, metas):
    """One log stream per venue across all selected assets (one getLogs pass serves every asset), plus the queues."""
    by = collections.defaultdict(list)
    for k in keys:
        if SURFACE[k].get('legacy_raw'):
            continue
        for m in metas[k]:
            by[m['venue']].append(m)
    streams = []
    if by['curve']:
        streams.append({'name': 'x_curve', 'address': sorted({m['address'] for m in by['curve']}),
                        'topics': [[XTOPICS['CurveEx'], XTOPICS['CurveExU']]]})
    if by['uniswap_v3']:
        streams.append({'name': 'x_v3', 'address': sorted({m['address'] for m in by['uniswap_v3']}), 'topics': [[XTOPICS['V3Swap']]]})
    if by['uniswap_v4']:
        streams.append({'name': 'x_v4', 'address': [V4_MANAGER], 'topics': [[XTOPICS['V4Swap']], sorted({m['pool_id'] for m in by['uniswap_v4']})]})
    if by['fluid']:
        streams.append({'name': 'x_fluid', 'address': sorted({m['address'] for m in by['fluid']}), 'topics': [[XTOPICS['FluidSwap']]]})
    qa, qt = [], []
    if 'lido' in keys:
        qa.append(LIDO_WQ)
        qt += [XTOPICS['LidoRequested'], XTOPICS['LidoFinalized']]
    if any(SURFACE[k]['redemption'].get('wait') == 'maple' for k in keys):
        qa += sorted({SURFACE[k]['redemption']['wm'] for k in keys if SURFACE[k]['redemption'].get('wait') == 'maple'})
        qt += [XTOPICS['MapleCreated'], XTOPICS['MapleProcessed']]
    if 'etherfi' in keys:
        qa.append(ETHERFI_RM)
        qt.append(XTOPICS['EtherFiRedeemed'])
    if qa:
        streams.append({'name': 'x_queues', 'address': sorted(set(qa)), 'topics': [sorted(set(qt))]})
    ra, rt = [], []
    if 'kelp' in keys:
        ra.append(KELP_WM)
        rt += [XTOPICS['KelpQueued'], XTOPICS['KelpFinalized']]
    if 'renzo' in keys:
        ra.append(RENZO_WQ)
        rt.append(XTOPICS['RenzoCreated'])
    if 'lido' in keys:
        ra.append(LIDO_WQ)
        rt.append(XTOPICS['LidoClaimed'])
    if ra:
        streams.append({'name': 'x_redeem', 'address': sorted(set(ra)), 'topics': [sorted(set(rt))]})
    return streams


def surface_keys(arg):
    if arg in (None, '', 'all'):
        return list(SURFACE)
    keys = [k.strip() for k in arg.split(',') if k.strip()]
    bad = [k for k in keys if k not in SURFACE]
    if bad:
        raise SystemExit('unknown assets %s; known: %s' % (bad, ', '.join(SURFACE)))
    return keys


def cmd_surface_collect(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    keys = surface_keys(args.assets)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    log_f = (out / 'collect.log').open('a')

    def log(obj):
        line = json.dumps(obj, default=str)
        print(line, flush=True)
        log_f.write(line + '\n')
        log_f.flush()

    man = read_json(out / 'manifest.json', {}) or {}
    if man.get('first_block') and not args.reset:
        first, last = man['first_block'], man['last_block']
        log({'resume': True, 'first_block': first, 'last_block': last})
    else:
        head = rpc.call('eth_getBlockByNumber', ['finalized', False])
        last = hx(head['number'])
        first = args.first_block
        man = {'chain': 'ethereum', 'chain_id': 1, 'first_block': first, 'last_block': last, 'end_tag': 'finalized',
               'last_block_utc': utc(hx(head['timestamp'])), 'collect_started': utc(), 'raw_files': {}}
        log({'first_block': first, 'last_block': last, 'last_block_utc': man['last_block_utc']})
    man['endpoints'] = {'logs_headers_state_latest': 'Infura mainnet JSON-RPC, local keys rotated, never written',
                        'archive_state': 'public endpoints in drpc.ENDPOINTS, one call at a time (see nav)'}
    metas = read_json(out / 'pools.json', {}) or {}
    missing = [k for k in keys if k not in metas]
    if missing:
        metas.update(surface_pool_metadata(rpc, missing))
        write_json(out / 'pools.json', metas)
    grid = list(range(first, last, BLOCKS_PER_DAY)) + [last]
    headers = read_json(out / 'headers.json', {}) or {}
    todo = [n for n in grid if str(n) not in headers]
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
    streams = surface_streams(keys, metas)
    man.setdefault('streams', {})
    try:
        for s in streams:
            if args.only and s['name'] not in args.only.split(','):
                continue
            man['streams'][s['name']] = {'address': s['address'], 'topics': s['topics'],
                                         **collect_stream(rpc, out, s, first, last, args.batch, log)}
    finally:
        man['rpc'] = rpc.stats()
        man['collect_finished'] = utc()
        man['assets_collected'] = sorted(set(man.get('assets_collected', [])) | set(keys))
        man['complete'] = {s['name']: not gaps(load_done(out / 'raw' / s['name']), first, last) for s in streams}
        for s in streams:
            d = out / 'raw' / s['name']
            man['raw_files'][s['name']] = {p.name: sha256(p) for p in sorted(d.glob('*.json.gz'))}
        man['topics'] = XTOPICS
        write_json(out / 'manifest.json', man)
        log({'complete': man['complete'], **man['rpc']})


def cmd_surface_nav(args):
    """Archive reads of every STATE key the selected assets need, on the daily header grid, two endpoints in parallel,
    plus the daily ETH/USD price (DefiLlama) for the ETH-denominated assets."""
    import threading
    import queue as _queue
    import urllib.request
    out = Path(args.out)
    keys = surface_keys(args.assets)
    headers = read_json(out / 'headers.json')
    if not headers:
        raise SystemExit('run collect first (nav needs the header grid)')
    grid = sorted(int(k) for k in headers)
    need = set()
    for k in keys:
        a = SURFACE[k]
        need |= {t['nav'] for t in a['targets'].values() if t['nav']}
        need |= {q for q in a['quotes'].values() if q}
        r = a['redemption']
        need |= {r[x] for x in ('created', 'finalized', 'key', 'daily_cap_state') if r.get(x)}
    need |= {'susds_nav', 'wsteth_nav'}           # the two benchmarks: Sky savings rate and Lido's staking rate
    state = read_json(out / 'state.json', {'samples': {}, 'errors': []})
    for key in need:
        state['samples'].setdefault(key, [])
    tasks = _queue.Queue()
    for key in sorted(need):
        spec = STATE[key]
        have = {s['block'] for s in state['samples'][key]}
        every = spec.get('every', 1)
        pts = [n for i, n in enumerate(grid) if (i % every == 0 or n == grid[-1])]
        for n in pts:
            if n not in have:
                tasks.put((key, n))
    total = tasks.qsize()
    endpoints = list(args.endpoints.split(',')) if args.endpoints else ['https://eth.drpc.org', 'https://eth.merkle.io']
    lock = threading.Lock()
    done = [0]
    t0 = time.monotonic()

    def worker(ep):
        others = [e for e in endpoints if e != ep]
        while True:
            try:
                key, n = tasks.get_nowait()
            except _queue.Empty:
                return
            spec = STATE[key]
            errs = []
            r, used = None, None
            for attempt in range(3):
                r, used = archive_call(spec['to'], spec['data'], n, [ep] + others, errs)
                if r:
                    break
                time.sleep(2 * (attempt + 1))
            with lock:
                if r:
                    state['samples'][key].append({'block': n, 'ts': headers[str(n)]['ts'], 'value': int(r[:66], 16) / spec['scale'],
                                                  'endpoint': used})
                else:
                    state['errors'].extend([dict(e, key=key) for e in errs[-2:]])
                done[0] += 1
                if done[0] % 100 == 0 or done[0] == total:
                    for v in state['samples'].values():
                        v.sort(key=lambda s: s['block'])
                    write_json(out / 'state.json', state)
                    print(json.dumps({'sampled': done[0], 'of': total, 'errors': len(state['errors']),
                                      'elapsed_s': round(time.monotonic() - t0)}), flush=True)
            time.sleep(0.15)

    th = [threading.Thread(target=worker, args=(ep,)) for ep in endpoints]
    for t in th:
        t.start()
    for t in th:
        t.join()
    for v in state['samples'].values():
        v.sort(key=lambda s: s['block'])
    state['method'] = ('eth_call of each STATE key at the daily header grid through public archive endpoints, one call at a '
                       'time; NAVs are interpolated linearly between samples in the analysis')
    state['coverage'] = {k: {'samples': len(v), 'first': v[0]['value'] if v else None, 'last': v[-1]['value'] if v else None}
                         for k, v in sorted(state['samples'].items())}
    write_json(out / 'state.json', state)
    # ETH/USD by day, for dollar notionals of the ETH-denominated assets.
    first_ts, last_ts = headers[str(grid[0])]['ts'], headers[str(grid[-1])]['ts']
    # DefiLlama's chart endpoint refuses long spans (a 744-day request answered 400), so it is read in 300-day pages.
    prices, urls, start = {}, [], first_ts - 86400
    while start <= last_ts + 86400:
        span = min(300, int((last_ts + 2 * 86400 - start) / 86400) + 1)
        url = 'https://coins.llama.fi/chart/coingecko:ethereum?start=%d&span=%d&period=1d' % (start, span)
        req = urllib.request.Request(url, headers={'User-Agent': 'llm-quant research'})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
        for pnt in d['coins']['coingecko:ethereum']['prices']:
            prices[pnt['timestamp']] = pnt
        urls.append(url)
        start += span * 86400
    prices = [prices[t] for t in sorted(prices)]
    write_json(out / 'eth_usd.json', {'source': urls, 'fetched': utc(), 'prices': prices})
    print(json.dumps({'state': state['coverage'], 'eth_usd_days': len(prices)}, indent=1))


# --------------------------------------------------------------------------------------------- surface: analyze
def load_stream(out, name):
    """Logs of one stream directory under `out/raw`, in block order."""
    d = out / 'raw' / name
    if not d.exists():
        return
    for p in sorted(d.glob('*.json.gz'), key=lambda p: int(p.name.split('_')[0])):
        with gzip.open(p, 'rt') as f:
            for l in json.load(f):
                yield l


def surface_swaps(out, k, metas, nav_at, ts_at, unit_usd_at, first_block, last_block, max_print_bps=MAX_PRINT_BPS):
    """Every priced swap of asset `k` in [first_block, last_block], with its discount, notional and fee."""
    a = SURFACE[k]
    if a.get('legacy_raw'):
        base = out / a['legacy_raw']
        sources = [('curve', base), ('v4', base)]
    else:
        sources = [('x_curve', out), ('x_v3', out), ('x_v4', out), ('x_fluid', out)]
    by_addr = {m['address']: m for m in metas if m.get('address')}
    by_pid = {m['pool_id']: m for m in metas if m.get('pool_id')}
    swaps, skipped = [], collections.Counter()
    for stream, base in sources:
        for l in load_stream(base, stream):
            n = hx(l['blockNumber'])
            if n < first_block or n > last_block:
                continue
            addr = l['address'].lower()
            if addr == V4_MANAGER:
                m = by_pid.get(l['topics'][1]) if len(l['topics']) > 1 else None
            else:
                m = by_addr.get(addr)
            if m is None:
                continue
            legs = LEGS[m['venue']](l, m, a['targets'])
            if legs is None:
                skipped['undecodable'] += 1
                continue
            rec = price_swap(a, legs, n, nav_at)
            if rec is None:
                skipped['unpriced'] += 1
                continue
            ts = ts_at(n)
            rec.update({'block': n, 'tx': l['transactionHash'], 'li': hx(l['logIndex']), 'pool': m['name'], 'venue': m['venue'],
                        'ts': ts, 'utc': utc(ts), 'unit_usd': unit_usd_at(ts)})
            rec['usd'] = rec['unit_value'] * rec['unit_usd']
            if rec['usd'] < MIN_TRADE_USD:
                skipped['dust'] += 1
                continue
            rec['excluded_print'] = abs(rec['discount_bps']) > max_print_bps
            swaps.append(rec)
    swaps.sort(key=lambda s: (s['block'], s['li']))
    return swaps, skipped


def surface_basis(out, k, metas_legacy, ts_at, first_block, last_block):
    """Hourly USDe basis from the legacy basis stream (sUSDe only)."""
    a = SURFACE[k]
    meta = next((m for m in metas_legacy if m.get('usde')), None)
    if not (a.get('basis') and meta):
        return {}
    bs = []
    for l in load_stream(out / a['legacy_raw'], 'basis'):
        b = decode_basis(l, meta)
        if b and b['usde'] >= MIN_TRADE_USD and first_block <= b['block'] <= last_block and abs(1.0 - b['price']) * 1e4 <= MAX_PRINT_BPS:
            b['ts'] = ts_at(b['block'])
            bs.append(b)
    return hourly_basis(bs)


def wait_model(k, out, state, queue_logs, ts_at, end_ts):
    """(ts -> wait days, summary) for asset k, from the measured queue where one exists."""
    r = SURFACE[k]['redemption']
    kind = r['wait']
    pts = []
    if kind == 'instant':
        return (lambda ts: 0.0), {'kind': 'instant', 'median_days': 0.0}
    if kind == 'constant':
        d = r['days']
        return (lambda ts, d=d: d), {'kind': 'constant', 'median_days': d}
    if kind == 'seconds':
        vals = [s['value'] / 86400.0 for s in state['samples'].get(r['key'], [])]
        series = [(s['ts'], s['value'] / 86400.0) for s in state['samples'].get(r['key'], [])]
        series.sort()
        tsx = [t for t, _ in series]

        def f(ts):
            if not series:
                return 14.0
            j = max(0, _bisect_right(tsx, ts) - 1)
            return series[j][1]
        return f, {'kind': 'parameter', 'samples': len(vals), 'values_days': sorted(set(round(v, 3) for v in vals)),
                   'median_days': statistics.median(vals) if vals else None}
    if kind == 'lido':
        reqs, fins = {}, []
        for l in queue_logs:
            if l['address'].lower() != LIDO_WQ:
                continue
            t0 = l['topics'][0]
            if t0 == XTOPICS['LidoRequested']:
                reqs[int(l['topics'][1], 16)] = ts_at(hx(l['blockNumber']))
            elif t0 == XTOPICS['LidoFinalized']:
                fins.append((int(l['topics'][1], 16), int(l['topics'][2], 16), ts_at(hx(l['blockNumber']))))
        w = lido_waits(reqs, fins, end_ts)
        pts = list(w.values())
    elif kind == 'pointer':
        sc = [(s['ts'], s['value']) for s in state['samples'].get(r['created'], [])]
        sf = [(s['ts'], s['value']) for s in state['samples'].get(r['finalized'], [])]
        pts = pointer_waits(sc, sf, r['finalized_inclusive'])
    elif kind == 'maple':
        created, processed = {}, {}
        wm = r['wm']
        for l in queue_logs:
            if l['address'].lower() != wm:
                continue
            t0 = l['topics'][0]
            rid = int(l['topics'][1], 16)
            if t0 == XTOPICS['MapleCreated']:
                created.setdefault(rid, ts_at(hx(l['blockNumber'])))
            elif t0 == XTOPICS['MapleProcessed']:
                processed[rid] = ts_at(hx(l['blockNumber']))
        for rid, ts in created.items():
            if rid in processed and processed[rid] >= ts:
                pts.append((ts, (processed[rid] - ts) / 86400.0, None))
            else:
                pts.append((ts, None, (end_ts - ts) / 86400.0))
    done = [w for _, w, _ in pts if w is not None]
    cens = [lb for _, w, lb in pts if w is None]
    f, by_day = daily_wait_fn(pts, 3.0)
    by_month = collections.defaultdict(list)
    for ts, w, lb in pts:
        by_month[utc(ts)[:7]].append(w if w is not None else lb)
    return f, {'kind': kind, 'requests': len(pts), 'finalized': len(done), 'pending_at_end': len(cens),
               'median_days': statistics.median(done) if done else None, 'p90_days': pct(done, 0.9) if done else None,
               'max_days': max(done) if done else None, 'pending_lower_bound_max_days': max(cens) if cens else None,
               'by_month_median_days': {m: statistics.median(v) for m, v in sorted(by_month.items())}}


def redemption_check(k, redeem_logs, queue_logs, nav_at, ts_at):
    """What the protocol actually paid per unit redeemed, against the NAV function the study prices discounts with.

    Kelp: `AssetWithdrawalFinalized` (amountReceived / amountBurned) matched to the same withdrawer's
    `AssetWithdrawalQueued` of the same rsETH amount. Renzo: `WithdrawRequestCreated` (amountToRedeem /
    ezETHAmountLocked, fixed at the request). Lido: `WithdrawalClaimed` ETH per `WithdrawalRequested` stETH. Each is
    reported in basis points against the NAV at the request block, so a persistent gap would mean the discount the
    study measures is partly a payout the protocol never makes.
    """
    diffs, diffs_final = [], []
    if k == 'kelp':
        queued = collections.defaultdict(list)
        for l in redeem_logs:
            if l['address'].lower() != KELP_WM or len(l['topics']) < 3:
                continue
            if '0x' + l['topics'][2][-40:] != ETH_SENTINEL:
                continue
            n = hx(l['blockNumber'])
            if l['topics'][0] == XTOPICS['KelpQueued']:
                queued[('0x' + l['topics'][1][-40:], word(l['data'], 0))].append(n)
            elif l['topics'][0] == XTOPICS['KelpFinalized']:
                burned, received = word(l['data'], 0), word(l['data'], 1)
                key = ('0x' + l['topics'][1][-40:], burned)
                if not burned or not queued.get(key):
                    continue
                qn = queued[key].pop(0)
                rate = received / burned
                nq, nf = nav_at('rseth_nav', qn), nav_at('rseth_nav', n)
                diffs.append(1e4 * (rate - nq) / nq)
                diffs_final.append(1e4 * (rate - nf) / nf)
    elif k == 'renzo':
        for l in redeem_logs:
            if l['address'].lower() != RENZO_WQ or l['topics'][0] != XTOPICS['RenzoCreated']:
                continue
            d = l['data']
            claim_token = '0x' + d[2 + 64 * 1 + 24: 2 + 64 * 2]
            redeem, locked = word(d, 2), word(d, 3)
            if claim_token != ETH_SENTINEL or not locked:
                continue
            n = hx(l['blockNumber'])
            nav = nav_at('ezeth_nav', n)
            diffs.append(1e4 * (redeem / locked - nav) / nav)
    elif k == 'lido':
        req = {}
        for l in queue_logs:
            if l['address'].lower() == LIDO_WQ and l['topics'][0] == XTOPICS['LidoRequested']:
                req[int(l['topics'][1], 16)] = word(l['data'], 0)
        for l in redeem_logs:
            if l['address'].lower() != LIDO_WQ or l['topics'][0] != XTOPICS['LidoClaimed']:
                continue
            rid = int(l['topics'][1], 16)
            if req.get(rid):
                diffs.append(1e4 * (word(l['data'], 0) / req[rid] - 1.0))
    else:
        return None
    if not diffs:
        return {'n': 0}
    return {'n': len(diffs), 'median_bps_vs_nav_at_request': statistics.median(diffs), 'p10_bps': pct(diffs, 0.1),
            'p90_bps': pct(diffs, 0.9), 'min_bps': min(diffs), 'max_bps': max(diffs),
            'median_bps_vs_nav_at_payout': statistics.median(diffs_final) if diffs_final else None}


def queue_activity(k, queue_logs, ts_at):
    """Counts and amounts by month of the protocol-side flows that bound or compete with the bid: Lido withdrawal
    requests (stETH), ether.fi instant redemptions through its RedemptionManager (eETH redeemed, by output token)."""
    out = collections.defaultdict(lambda: {'count': 0, 'amount': 0.0})
    for l in queue_logs:
        t0, a = l['topics'][0], l['address'].lower()
        m = utc(ts_at(hx(l['blockNumber'])))[:7]
        if k == 'lido' and a == LIDO_WQ and t0 == XTOPICS['LidoRequested']:
            out[m]['count'] += 1
            out[m]['amount'] += word(l['data'], 0) / 1e18
        elif k == 'etherfi' and a == ETHERFI_RM and t0 == XTOPICS['EtherFiRedeemed']:
            tok = '0x' + l['data'][2 + 64 * 3 + 24: 2 + 64 * 4]
            key = '%s %s' % (m, SYMBOLS.get(tok, tok))
            out[key]['count'] += 1
            out[key]['amount'] += word(l['data'], 0) / 1e18
    return dict(sorted(out.items())) if out else None


def weekly_by_pool(records, first_ts):
    """{week start (UTC date): {pool: [volume-weighted discount bp, volume $, swaps]}} over all priced trades."""
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0, 0]))
    for r in records:
        w = first_ts + (r['ts'] - first_ts) // (7 * 86400) * 7 * 86400
        a = acc[utc(w)[:10]][r['pool']]
        a[0] += r['discount_bps'] * r['usd']
        a[1] += r['usd']
        a[2] += 1
    return {w: {p: [x[0] / x[1] if x[1] else None, x[1], x[2]] for p, x in sorted(pools.items())} for w, pools in sorted(acc.items())}


def exit_capacity_summary(state, key):
    """For a redemption that only pays out of a balance (rETH.burn needs getTotalCollateral): how often it could pay."""
    if not key:
        return None
    xs = state['samples'].get(key) or []
    if not xs:
        return None
    pos = [x for x in xs if x['value'] > 1.0]
    return {'key': key, 'samples': len(xs), 'max': max(x['value'] for x in xs), 'first': xs[0]['value'], 'last': xs[-1]['value'],
            'share_of_days_above_1': len(pos) / len(xs), 'share_of_days_above_100': sum(1 for x in xs if x['value'] > 100.0) / len(xs),
            'last_day_above_1_utc': utc(pos[-1]['ts'])[:10] if pos else None}


def max_nav_step_day(series):
    """The UTC date of the sample that ends the largest NAV step."""
    s = sorted(series)
    steps = [(abs(1e4 * (b[1] - a[1]) / a[1]), b[0]) for a, b in zip(s, s[1:]) if a[1]]
    return utc(max(steps)[1])[:10] if steps else None


def max_nav_step_bps(series):
    """Largest change between consecutive NAV samples, in bps: the bound on linear-interpolation error."""
    s = sorted(series)
    steps = [abs(1e4 * (b[1] - a[1]) / a[1]) for a, b in zip(s, s[1:]) if a[1]]
    return max(steps) if steps else None


def cmd_surface_analyze(args):
    import backtest as B
    out = Path(args.out)
    keys = surface_keys(args.assets)
    man = read_json(out / 'manifest.json')
    headers = read_json(out / 'headers.json')
    state = read_json(out / 'state.json')
    metas = read_json(out / 'pools.json')
    ethp = read_json(out / 'eth_usd.json')
    if not (man and headers and state and metas and ethp):
        raise SystemExit('run collect and nav first')
    hb = sorted(int(k) for k in headers)
    hts = [headers[str(n)]['ts'] for n in hb]
    first_block, last_block = man['first_block'], man['last_block']
    first_ts, last_ts = headers[str(first_block)]['ts'], headers[str(last_block)]['ts']

    def ts_at(n):
        return int(round(interp(hb, hts, n)))

    grids = {key: ([s['block'] for s in v], [s['value'] for s in v]) for key, v in state['samples'].items() if v}

    def nav_at(key, n):
        g = grids.get(key)
        return interp(g[0], g[1], n) if g else None

    ex, ey = [p['timestamp'] for p in ethp['prices']], [p['price'] for p in ethp['prices']]

    def eth_usd(ts):
        return interp(ex, ey, ts)

    # Benchmarks, both measured: Lido's staking rate from wstETH's NAV, and the Sky savings rate from sUSDS's NAV.
    lido_series = [(s['ts'], s['value']) for s in state['samples'].get('wsteth_nav', [])]
    ssr_series = [(s['ts'], s['value']) for s in state['samples'].get('susds_nav', [])]
    staking_apr = apr_from_nav(lido_series) or ETH_STAKING_FALLBACK
    ssr_fn = trailing_rate_fn(ssr_series, 1.0, SSR_FALLBACK)
    ssr_window = apr_from_nav(ssr_series)
    ssr_latest = ssr_fn(last_ts)

    def carry_fn(unit):
        if unit == 'ETH':
            return lambda ts: staking_apr / 365.0 * 1e4
        return lambda ts: (ssr_fn(ts) or SSR_FALLBACK) / 365.0 * 1e4

    queue_logs = list(load_stream(out, 'x_queues'))
    redeem_logs = list(load_stream(out, 'x_redeem'))
    n_days = int((last_ts - first_ts) // 86400) + 1
    first_day = first_ts // 86400
    split_day = first_day + B.cutoff_index(n_days, 0.5)
    results = {}
    variants_tried = 0
    for k in keys:
        a = SURFACE[k]
        r = a['redemption']
        t_start = time.monotonic()
        unit_usd_at = eth_usd if a['unit'] == 'ETH' else (lambda ts: 1.0)
        metas_k = metas.get(k) or []
        if a.get('legacy_raw') and not metas_k:
            lp = read_json(out / a['legacy_raw'] / 'pools.json') or []
            metas_k = [dict(m, tokens=[SUSDE, USDT], fee_bps=None) if m['venue'] == 'uniswap_v4' else dict(m, fee_bps=fee_from_legacy(m))
                       for m in lp if not m.get('usde')]
            for m in metas_k:
                if m['venue'] == 'uniswap_v4':
                    m['decimals'] = m.get('decimals') or [18, 6]
        swaps, skipped = surface_swaps(out, k, metas_k, nav_at, ts_at, unit_usd_at, first_block, last_block, args.max_print_bps)
        # Orientation check: a pool whose median trade sits far from NAV has its tokens the wrong way round.
        suspect = {}
        for m in metas_k:
            xs = [s['discount_bps'] for s in swaps if s['pool'] == m['name']]
            if len(xs) >= 20 and abs(statistics.median(xs)) > 200:
                suspect[m['name']] = statistics.median(xs)
        if suspect:
            raise SystemExit('%s: pools priced far from NAV (token order?): %s' % (k, suspect))
        hourly_b = surface_basis(out, k, read_json(out / a['legacy_raw'] / 'pools.json') if a.get('legacy_raw') else [], ts_at,
                                 first_block, last_block) if a.get('basis') else {}
        if a.get('basis'):
            for s in swaps:
                bb, age = basis_at(hourly_b, s['ts'] // 3600 * 3600)
                s['basis_bps'] = bb
                s['raw_discount_bps'] = s['discount_bps']
                s['discount_bps'] = (s['discount_bps'] - bb) if bb is not None else None
            swaps = [s for s in swaps if s['discount_bps'] is not None]
        kept = [s for s in swaps if not s['excluded_print']]
        excluded = [s for s in swaps if s['excluded_print']]
        sells = [s for s in kept if s['side'] == 'sell']
        wait_fn, wait_summary = wait_model(k, out, state, queue_logs, ts_at, last_ts)
        carry = carry_fn(a['unit'])
        cap_fn = None
        if r.get('exit_cap_usd_per_day'):
            cap_fn = (lambda ts, c=r['exit_cap_usd_per_day']: c)
        elif r.get('daily_cap_state'):
            ck = r['daily_cap_state']
            cap_fn = (lambda ts, ck=ck: (nav_at(ck, interp(hts, hb, ts)) or 0.0) * eth_usd(ts))
        market_fn = market_discount_fn(kept)
        grid_res = {}
        for size in SIZES_USD:
            variants = {}
            per = {}
            for h in HURDLES_BPS:
                kw = dict(accrues=r.get('accrues', False), redemption_fee_bps=r.get('fee_bps', 0.0), daily_cap_usd_at=cap_fn)
                fills, st = simulate_bid(sells, size, h, wait_fn, carry, market_bps_at=market_fn, **kw)
                raw_fills, _ = simulate_bid(sells, size, h, wait_fn, carry, **kw)
                series = daily_values(fills, first_day, n_days)
                variants['h=%g' % h] = series
                per['h=%g' % h] = {'fills': fills, 'stats': st, 'series': series, 'per_print': daily_values(raw_fills, first_day, n_days)}
            variants_tried += len(variants)
            ct = B.choose_then_test(variants, frac=0.5, periods_per_year=365, key='ann_return')
            chosen = ct['chosen']
            oos = variants[chosen][ct['cutoff_index']:]
            boot = B.block_bootstrap(oos, block=7, n=2000)
            fills = per[chosen]['fills']
            pp = per[chosen]['per_print']
            grid_res[size] = {
                'per_print_upper_bound_oos_usd_per_year': sum(pp[ct['cutoff_index']:]) * 365.0 / max(1, n_days - ct['cutoff_index']),
                'per_print_upper_bound_full_usd_per_year': sum(pp) * 365.0 / n_days,
                'chosen_hurdle': chosen, 'in_sample_usd_per_year': ct['in_sample'].get('ann_return'),
                'out_of_sample_usd_per_year': ct['out_of_sample'].get('ann_return'), 'oos_rank_of_chosen': ct['oos_rank'],
                'oos_ci95_usd_per_year': [boot['lo'] * 365 if boot['lo'] is not None else None, boot['hi'] * 365 if boot['hi'] is not None else None],
                'oos_share_of_bootstraps_le_0': boot['p_le_0'], 'oos_t': ct['oos_t'],
                'full_period_usd_per_year': sum(variants[chosen]) * 365.0 / n_days,
                'best_oos_hurdle': max(variants, key=lambda v: sum(variants[v][ct['cutoff_index']:])),
                'by_hurdle_full_usd': {v: sum(x) for v, x in variants.items()},
                'by_hurdle_oos_usd': {v: sum(x[ct['cutoff_index']:]) for v, x in variants.items()},
                'fills': len(fills), 'fills_oos': sum(1 for f in fills if f['ts'] // 86400 >= split_day),
                'filled_usd': per[chosen]['stats']['filled_usd'], 'stats': per[chosen]['stats'],
                'median_edge_bps': statistics.median([f['edge_bps'] for f in fills]) if fills else None,
                'value_by_month_usd': {m: sum(f['value_usd'] for f in fills if utc(f['ts'])[:7] == m)
                                       for m in sorted({utc(t)[:7] for t in range(first_ts, last_ts + 1, 86400)})},
                'top_fills': sorted(fills, key=lambda f: -f['value_usd'])[:8],
                '_fills_all': fills,
            }
        # The correction the market cap makes, on the record: the largest per-print fills it removes at $10M, h=0.
        raw10, _ = simulate_bid(sells, 10_000_000, 0.0, wait_fn, carry, accrues=r.get('accrues', False),
                                redemption_fee_bps=r.get('fee_bps', 0.0), daily_cap_usd_at=cap_fn)
        removed = []
        fee_of = {(x['ts'], x.get('tx')): x['fee_bps'] for x in sells}
        for f in raw10:
            m = market_fn(f['ts'])
            fee = fee_of.get((f['ts'], f['tx']), 0.0)
            carry_f = 0.0 if r.get('accrues') else f['wait_days'] * carry(f['ts'])
            capped = (min(f['discount_bps'] - FEE_LEGS * fee, m - fee) if m is not None else f['discount_bps'] - FEE_LEGS * fee) - carry_f - r.get('fee_bps', 0.0)
            capped_value = max(0.0, f['usd'] * capped / 1e4 - GAS_PER_FILL_USD) if capped > 0 else 0.0
            if capped_value < f['value_usd']:
                removed.append({'utc': utc(f['ts']), 'pool': f['pool'], 'usd': f['usd'], 'discount_bps': f['discount_bps'],
                                'market_median_bps': m, 'per_print_value_usd': f['value_usd'], 'capped_value_usd': capped_value,
                                'removed_entirely': capped <= 0, 'tx': f['tx']})
        removed.sort(key=lambda x: -(x['per_print_value_usd'] - x['capped_value_usd']))
        oos_by_size = {s: max(0.0, g['out_of_sample_usd_per_year'] or 0.0) for s, g in grid_res.items()}
        cap = capacity_size(oos_by_size)
        at = grid_res[cap] if cap else None
        last_day = first_day + n_days - 1
        for g in grid_res.values():
            g['trailing_90d_usd_per_year'] = sum(f['value_usd'] for f in g.pop('_fills_all') if f['ts'] // 86400 > last_day - 90) * 365.0 / 90
        if cap is None:
            binding = 'nothing qualifies out of sample'
        elif r.get('permissioned'):
            binding = 'redemption is permissioned'
        elif at['stats']['missed_cap_usd'] > at['stats']['missed_capital_usd'] and at['stats']['missed_cap_usd'] > 0:
            binding = 'exit or redemption capacity per day'
        elif cap == SIZES_USD[-1] and at['stats']['missed_capital_usd'] > 0:
            binding = 'capital locked in the queue (still growing at the largest size tested)'
        else:
            binding = 'offered volume below NAV (more capital adds little)'
        hrs = hourly_series([dict(s) for s in kept])
        vw = [h['vw_discount_bps'] for h in hrs if h['vw_discount_bps'] is not None]
        fees = [s['fee_bps'] for s in kept if s['fee_bps'] is not None]
        med_fee = statistics.median(fees) if fees else 0.0
        med_wait = wait_summary.get('median_days') or 0.0
        rt = FEE_LEGS * med_fee + (0.0 if r.get('accrues') else med_wait * carry(last_ts))
        eps = segment_episodes(hrs, rt, None, 2, cap or SIZES_USD[0])
        by_pool = {}
        for m in metas_k:
            xs = [s for s in kept if s['pool'] == m['name']]
            vol = sum(s['usd'] for s in xs)
            by_pool[m['name']] = {'swaps': len(xs), 'volume_usd': vol, 'sell_volume_usd': sum(s['usd'] for s in xs if s['side'] == 'sell'),
                                  'vw_discount_bps': sum(s['discount_bps'] * s['usd'] for s in xs) / vol if vol else None,
                                  'median_sell_discount_bps': statistics.median([s['discount_bps'] for s in xs if s['side'] == 'sell'] or [0]),
                                  'fee_bps': m.get('fee_bps'), 'fee_source': m.get('fee_source')}
        nav_keys = [t['nav'] for t in a['targets'].values() if t['nav']]
        results[k] = {
            'label': a['label'], 'unit': a['unit'], 'redemption': {kk: vv for kk, vv in r.items() if kk not in ('wm',)},
            'swaps_priced': len(kept), 'sells': len(sells), 'skipped': dict(skipped),
            'volume_usd': sum(s['usd'] for s in kept), 'sell_volume_usd': sum(s['usd'] for s in sells),
            'excluded_prints': {'count': len(excluded), 'usd': sum(s['usd'] for s in excluded),
                                'prints': [{x: s[x] for x in ('utc', 'pool', 'side', 'usd', 'price', 'nav', 'discount_bps', 'tx')} for s in excluded[:20]]},
            'by_pool': by_pool,
            'nav_max_daily_step_bps': {key: max_nav_step_bps([(s['ts'], s['value']) for s in state['samples'].get(key, [])]) for key in nav_keys},
            'nav_max_daily_step_utc': {key: max_nav_step_day([(s['ts'], s['value']) for s in state['samples'].get(key, [])]) for key in nav_keys},
            'nav_unchanged_days': {key: sum(1 for a, b in zip(state['samples'].get(key, []), state['samples'].get(key, [])[1:]) if a['value'] == b['value'])
                                   for key in nav_keys},
            'hourly_vw_discount_bps': {**distribution(vw),
                                       'share_at_least_5bp': sum(1 for x in vw if x >= 5) / len(vw) if vw else None,
                                       'share_at_least_10bp': sum(1 for x in vw if x >= 10) / len(vw) if vw else None,
                                       'share_at_least_20bp': sum(1 for x in vw if x >= 20) / len(vw) if vw else None},
            'hours_with_trades': len(hrs),
            'sell_discount_bps': {'p50': pct([s['discount_bps'] for s in sells], .5), 'p90': pct([s['discount_bps'] for s in sells], .9),
                                  'p99': pct([s['discount_bps'] for s in sells], .99), 'max': max((s['discount_bps'] for s in sells), default=None)},
            'wait': wait_summary, 'carry_bps_per_day_latest': carry(last_ts), 'median_fee_bps': med_fee,
            'redemption_check': redemption_check(k, redeem_logs, queue_logs, nav_at, ts_at),
            'queue_activity_by_month': queue_activity(k, queue_logs, ts_at),
            'exit_capacity_state': exit_capacity_summary(state, r.get('daily_cap_state')),
            'market_cap_effect_at_10m_h0': {'fills_reduced': len(removed), 'fills_removed': sum(1 for x in removed if x['removed_entirely']),
                                            'per_print_value_usd': sum(x['per_print_value_usd'] for x in removed),
                                            'capped_value_usd': sum(x['capped_value_usd'] for x in removed),
                                            'largest_reductions': removed[:6]},
            'weekly_by_pool': weekly_by_pool(kept, first_ts),
            'round_trip_bps_for_episodes': rt,
            'episodes': {'count': len(eps), 'median_hours': statistics.median([e['duration_hours'] for e in eps]) if eps else None,
                         'hours_in_episodes': sum(e['qualifying_hours'] for e in eps),
                         'deepest': sorted(eps, key=lambda e: -(e['max_sell_discount_bps'] or -1e9))[:5]},
            'simulation': {str(s): g for s, g in grid_res.items()},
            'capacity_usd': cap, 'binding_constraint': binding,
            'oos_usd_per_year_at_capacity': at['out_of_sample_usd_per_year'] if at else 0.0,
            'oos_ci95_at_capacity': at['oos_ci95_usd_per_year'] if at else None,
            'in_sample_usd_per_year_at_capacity': at['in_sample_usd_per_year'] if at else None,
            'trailing_90d_usd_per_year_at_capacity': at['trailing_90d_usd_per_year'] if at else 0.0,
            'chosen_hurdle_at_capacity': at['chosen_hurdle'] if at else None,
            'seconds': round(time.monotonic() - t_start, 1),
        }
        print(json.dumps({'asset': k, 'swaps': len(kept), 'sells': len(sells), 'capacity': cap,
                          'oos_usd_per_year': round(results[k]['oos_usd_per_year_at_capacity']),
                          'is_usd_per_year': round(results[k]['in_sample_usd_per_year_at_capacity'] or 0),
                          'wait_median_days': wait_summary.get('median_days'), 'binding': binding,
                          'hourly_vw': {x: (round(v, 2) if isinstance(v, float) else v) for x, v in results[k]['hourly_vw_discount_bps'].items()}}),
              flush=True)
    prior = read_json(out / 'analysis.json', {}) or {}
    assets = dict(prior.get('assets') or {})
    assets.update(results)
    ranking = sorted(assets, key=lambda x: -(assets[x]['oos_usd_per_year_at_capacity'] or 0.0))
    analysis = {
        'generated': utc(), 'first_block': first_block, 'last_block': last_block, 'first_utc': utc(first_ts), 'last_utc': utc(last_ts),
        'days': n_days, 'split_utc': utc(split_day * 86400),
        'benchmarks': {'eth_staking_apr_lido_window': staking_apr, 'ssr_apy_window': ssr_window, 'ssr_apy_latest': ssr_latest,
                       'ssr_note': 'Sky savings rate measured day by day from the sUSDS NAV: 3.60% until 2026-10-06, 3.80% from 2026-10-07 (sUSDS.ssr() read 3.80% on 2026-10-09); the backtest charges each day its own rate, forward quotes use the latest'},
        'parameters': {'sizes_usd': SIZES_USD, 'hurdles_bps': HURDLES_BPS, 'gas_per_fill_usd': GAS_PER_FILL_USD,
                       'min_fill_usd': MIN_FILL_USD, 'fee_legs': FEE_LEGS, 'capacity_share': CAPACITY_SHARE,
                       'max_print_bps': args.max_print_bps, 'min_trade_usd': MIN_TRADE_USD, 'bootstrap_block_days': 7},
        'variants_tried': (prior.get('variants_tried_by_asset') or {}) | {k: len(SIZES_USD) * len(HURDLES_BPS) for k in keys},
        'ranking': [{'asset': x, 'oos_usd_per_year_at_capacity': assets[x]['oos_usd_per_year_at_capacity'],
                     'capacity_usd': assets[x]['capacity_usd'], 'binding_constraint': assets[x]['binding_constraint']} for x in ranking],
        'skipped': SKIPPED, 'assets': assets,
    }
    analysis['variants_tried_by_asset'] = analysis.pop('variants_tried')
    analysis['variants_tried_total'] = sum(analysis['variants_tried_by_asset'].values())
    # The book's sUSDe quote came from the 2026-09-10 method (one capped fill per episode). Re-run unchanged on the
    # extended window, it is the like-for-like re-quote; the simulation above is the stricter, out-of-sample reading.
    leg = read_json(out / SURFACE['susde']['legacy_raw'] / 'summary.json')
    if leg:
        analysis['susde_legacy_requote'] = {
            'method': 'scripts/dislocation_history.py collect/nav/analyze (the 2026-09-10 method) on the extended window',
            'first_utc': leg['first_utc'], 'last_utc': leg['last_utc'], 'days': leg['days_covered'],
            'capacity_cap_usd': leg['capacity_cap_usd'], 'round_trip_bps': leg['round_trip_bps'],
            'raw': {'option_value_usd_per_year': leg['raw']['episodes']['option_value_usd_per_year'],
                    'option_value_daily_cap_usd_per_year': leg['raw']['episodes']['option_value_daily_cap_usd_per_year'],
                    'episodes': leg['raw']['episodes']['count'], 'by_month_usd': leg['raw']['option_value_by_month_usd']},
            'net_of_usde_basis': {'option_value_usd_per_year': leg['net_of_usde_basis']['episodes']['option_value_usd_per_year'],
                                  'option_value_daily_cap_usd_per_year': leg['net_of_usde_basis']['episodes']['option_value_daily_cap_usd_per_year'],
                                  'option_value_usd_history': leg['net_of_usde_basis']['episodes']['option_value_usd_history'],
                                  'trade_level_upper_bound_usd_per_year': leg['net_of_usde_basis']['episodes']['trade_level_upper_bound_usd_per_year'],
                                  'episodes': leg['net_of_usde_basis']['episodes']['count'],
                                  'by_month_usd': leg['net_of_usde_basis']['option_value_by_month_usd']},
            'hourly_vw_discount_bps_raw': leg['raw']['hourly_vw_discount_bps'],
            'hourly_vw_discount_bps_net': leg['net_of_usde_basis']['hourly_vw_discount_bps'],
            'kill_slices_met_net': '%d/%d' % (leg['kill_criterion']['slices_net_of_basis_met'], leg['kill_criterion']['slices_total']),
        }
        # The book's kill test for this row: net option value over the trailing 90 days, annualised, at the $600k cap.
        eps = (read_json(out / SURFACE['susde']['legacy_raw'] / 'episodes.json') or {}).get('episodes_net_of_usde_basis') or []
        cut = int(dt.datetime.fromisoformat(leg['last_utc'].replace('Z', '+00:00')).timestamp()) - 90 * 86400
        analysis['susde_legacy_requote']['trailing_90d_net_usd_per_year'] = sum(e['option_value_usd'] for e in eps if e['start'] >= cut) * 365.0 / 90
        old = read_json(ROOT_DIR / 'research' / '2026-09-10' / 'susde_history' / 'summary.json')
        if old:
            analysis['susde_legacy_requote']['previous_study'] = {
                'path': 'research/2026-09-10/susde_history', 'days': old['days_covered'], 'last_utc': old['last_utc'],
                'net_option_value_usd_per_year': old['net_of_usde_basis']['episodes']['option_value_usd_per_year']}
        lt = out / SURFACE['susde']['legacy_raw'] / 'tables.md'
        if lt.exists():
            (out / 'susde_legacy_tables.md').write_text(lt.read_text())
    write_json(out / 'analysis.json', analysis)
    man['analysis'] = {'generated': analysis['generated'], 'assets': sorted(assets)}
    man['file_hashes'] = {p.name: sha256(p) for p in sorted(out.glob('*.json')) if p.name != 'manifest.json'}
    write_json(out / 'manifest.json', man)


def fee_from_legacy(m):
    """sUSDe's Curve pools: fees read 2026-10-10 (sDAI/sUSDe 2bp, sUSDe/frxUSD 1bp); the legacy pools.json has none."""
    return {'curve-sdai-susde': 2.0, 'curve-susde-frxusd': 1.0}.get(m['name'], 1.0)


def cmd_surface_render(args):
    out = Path(args.out)
    A = read_json(out / 'analysis.json')
    if not A:
        raise SystemExit('run analyze first')
    L = ['# The redemption surface, tables', '',
         'Window %s to %s (blocks %d to %d, %d days); parameters chosen on days before %s and scored after. ETH staking '
         'benchmark %.2f%% (Lido, measured over the window); Sky savings rate %.2f%% over the window, %.2f%% on the last '
         'day. %d variants tried in all.' % (A['first_utc'], A['last_utc'], A['first_block'], A['last_block'], A['days'],
                                                   A['split_utc'][:10], 100 * A['benchmarks']['eth_staking_apr_lido_window'],
                                                   100 * (A['benchmarks']['ssr_apy_window'] or 0), 100 * (A['benchmarks']['ssr_apy_latest'] or 0),
                                                   A['variants_tried_total']), '',
         '## Ranking by out-of-sample value at capacity', '',
         '| asset | unit | hourly VW discount p50 / p90 / p99 (bp) | sell p50 / p90 / p99 (bp) | wait (median days) | capacity | OOS $/yr at capacity | 95% CI | in-sample $/yr | binding constraint |',
         '|---|---|---|---|---:|---:|---:|---|---:|---|']
    for row in A['ranking']:
        x = A['assets'][row['asset']]
        h, s = x['hourly_vw_discount_bps'], x['sell_discount_bps']
        ci = x.get('oos_ci95_at_capacity') or [None, None]
        L.append('| %s | %s | %s / %s / %s | %s / %s / %s | %s | %s | %s | %s to %s | %s | %s |' % (
            x['label'], x['unit'], fmt_bps(h['p50']), fmt_bps(h['p90']), fmt_bps(h['p99']), fmt_bps(s['p50']), fmt_bps(s['p90']), fmt_bps(s['p99']),
            '-' if x['wait'].get('median_days') is None else '%.2f' % x['wait']['median_days'], fmt_usd(x['capacity_usd']),
            fmt_usd(x['oos_usd_per_year_at_capacity']), fmt_usd(ci[0]), fmt_usd(ci[1]), fmt_usd(x['in_sample_usd_per_year_at_capacity']),
            x['binding_constraint']))
    for k in [r['asset'] for r in A['ranking']]:
        x = A['assets'][k]
        L += ['', '## %s' % x['label'], '', 'Redemption: %s. Fee %sbp; %s while queued; %s.' % (
            x['redemption']['path'], x['redemption'].get('fee_bps', 0), 'keeps earning' if x['redemption'].get('accrues') else 'earns nothing',
            'permissioned' if x['redemption'].get('permissioned') else 'open to anyone'),
              'Wait: %s.' % json.dumps({kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in x['wait'].items() if kk != 'by_month_median_days'}),
              'Swaps priced %d (%d sells), %s traded, %s sold; %d prints beyond the bound excluded (%s). NAV max daily step: %s.' % (
                  x['swaps_priced'], x['sells'], fmt_usd(x['volume_usd']), fmt_usd(x['sell_volume_usd']), x['excluded_prints']['count'],
                  fmt_usd(x['excluded_prints']['usd']), ', '.join('%s %sbp' % (kk, fmt_bps(vv)) for kk, vv in x['nav_max_daily_step_bps'].items()) or 'par'),
              '', '| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |', '|---|---:|---:|---:|---:|---:|---:|']
        for name, p in x['by_pool'].items():
            L.append('| %s | %d | %s | %s | %s | %s | %s |' % (name, p['swaps'], fmt_usd(p['volume_usd']), fmt_usd(p['sell_volume_usd']),
                                                           fmt_bps(p['vw_discount_bps']), fmt_bps(p['median_sell_discount_bps']),
                                                           '-' if p['fee_bps'] is None else '%.2f' % p['fee_bps']))
        L += ['', '| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |',
              '|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|']
        for size, g in sorted(x['simulation'].items(), key=lambda kv: float(kv[0])):
            ci = g['oos_ci95_usd_per_year']
            L.append('| %s | %s | %s | %s | %s to %s | %s | %d | %d (%d) | %s | %s | %s |' % (
                fmt_usd(float(size)), g['chosen_hurdle'], fmt_usd(g['in_sample_usd_per_year']), fmt_usd(g['out_of_sample_usd_per_year']),
                fmt_usd(ci[0]), fmt_usd(ci[1]), fmt_usd(g.get('trailing_90d_usd_per_year')), g['oos_rank_of_chosen'], g['fills'], g['fills_oos'],
                fmt_bps(g['median_edge_bps']), fmt_usd(g['stats']['missed_capital_usd']), fmt_usd(g['stats']['missed_cap_usd'])))
        if x['capacity_usd']:
            g = x['simulation'][str(x['capacity_usd'])]
            L += ['', 'Value by month at capacity (%s, %s): %s.' % (fmt_usd(x['capacity_usd']), g['chosen_hurdle'],
                                                                   ', '.join('%s %s' % (m, fmt_usd(v)) for m, v in g['value_by_month_usd'].items()))]
    L += ['', '## Not read', ''] + ['- %s: %s' % (k, v) for k, v in A['skipped'].items()]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'tables.md')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('collect')
    a.add_argument('--out', required=True)
    a.add_argument('--days', type=int, default=180)
    a.add_argument('--batch', type=int, default=4, help='eth_getLogs ranges per HTTP request')
    a.add_argument('--max-credits', type=int, default=300_000)
    a.add_argument('--reset', action='store_true', help='ignore a saved block range and pin a new one')
    a.add_argument('--assets', help='the redemption surface: comma list of %s, or all' % ', '.join(SURFACE))
    a.add_argument('--first-block', type=int, default=SURFACE_FIRST_BLOCK, help='surface only: first block of the window')
    a.add_argument('--only', help='surface only: comma list of stream names to collect')
    b = sub.add_parser('nav')
    b.add_argument('--out', required=True)
    b.add_argument('--endpoints', help='comma-separated archive endpoints; default drpc.ENDPOINTS')
    b.add_argument('--assets', help='the redemption surface (see collect)')
    c = sub.add_parser('analyze')
    c.add_argument('--out', required=True)
    c.add_argument('--max-gap-hours', type=int, default=2)
    c.add_argument('--max-print-bps', type=float, default=MAX_PRINT_BPS)
    c.add_argument('--assets', help='the redemption surface (see collect)')
    d = sub.add_parser('render')
    d.add_argument('--out', required=True)
    d.add_argument('--force-findings', action='store_true')
    d.add_argument('--assets', help='the redemption surface (see collect)')
    args = p.parse_args()
    if getattr(args, 'assets', None):
        {'collect': cmd_surface_collect, 'nav': cmd_surface_nav, 'analyze': cmd_surface_analyze, 'render': cmd_surface_render}[args.cmd](args)
    else:
        {'collect': cmd_collect, 'nav': cmd_nav, 'analyze': cmd_analyze, 'render': cmd_render}[args.cmd](args)


if __name__ == '__main__':
    main()
