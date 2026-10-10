#!/usr/bin/env python3
"""Do resting below-NAV limit orders actually fill during a liquid-staking dislocation? A check on CoW Protocol.

Why. research/2026-10-10/queue_book proposes running the queue bids as unescrowed signed limit orders: one WETH
balance backing standing bids for stETH, weETH and rsETH below NAV, filled by solvers when sellers arrive. The
simulation assumes a waiting bid is filled at the market's discount. This checks the implementation on the record:
during the April 2026 stETH episode (2026-04-19 → 05-09, the deepest of the two-year window), which CoW orders
bought liquid staking tokens with ETH, how long had they been resting, at what discount to NAV did they fill, and how
did that compare with the discount the venues showed at the time.

    uv run --with pycryptodome python scripts/cow_fill_check.py collect --out research/2026-10-10/cow_fill_check
    uv run --with pycryptodome python scripts/cow_fill_check.py orders  --out research/2026-10-10/cow_fill_check
    uv run --with pycryptodome python scripts/cow_fill_check.py analyze --out research/2026-10-10/cow_fill_check

Read-only: eth_getLogs through the local Infura keys (live_rpc), order details from CoW's public API.
"""
import argparse
import collections
import gzip
import json
import statistics
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_rpc                           # noqa: E402
import dislocation_history as D           # noqa: E402

SETTLEMENT = '0x9008d19f58aabd9ed0d60971565aa8510560ab41'
TRADE_TOPIC = D.keccak('Trade(address,address,address,uint256,uint256,uint256,bytes)')
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
ETH = '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
LSTS = {'0xae7ab96520de3a18e5e111b5eaab095312d7fe84': ('stETH', None),
        '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0': ('wstETH', 'wsteth_nav'),
        '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee': ('weETH', 'weeth_nav'),
        '0xa1290d69c65a6fe4df752f95823fae25cb99e5a7': ('rsETH', 'rseth_nav')}
EPISODE = (24_917_313, 25_054_113)       # 2026-04-19 → 2026-05-09 on the long window's daily grid
LONG = Path(__file__).resolve().parents[1] / 'research' / '2026-10-09' / 'redemption_history' / 'raw' / 'long'
COW_API = 'https://api.cow.fi/mainnet/api/v1/orders/'
STEP = 2_000


def decode_trade(log):
    """GPv2 Trade(owner indexed, sellToken, buyToken, sellAmount, buyAmount, feeAmount, orderUid)."""
    d = log['data'][2:]
    w = [d[i * 64:(i + 1) * 64] for i in range(len(d) // 64)]
    uid_len = int(w[6], 16)
    uid = '0x' + ''.join(w[7:])[:uid_len * 2]
    return {'block': int(log['blockNumber'], 16), 'tx': log['transactionHash'], 'owner': '0x' + log['topics'][1][-40:],
            'sell_token': '0x' + w[0][-40:], 'buy_token': '0x' + w[1][-40:], 'sell_amount': int(w[2], 16),
            'buy_amount': int(w[3], 16), 'fee_amount': int(w[4], 16), 'uid': uid}


def cmd_collect(args):
    out = Path(args.out)
    (out / 'logs').mkdir(parents=True, exist_ok=True)
    rpc = live_rpc.RPC(log_path=out / 'rpc_errors.jsonl')
    first, last = EPISODE
    n = 0
    for a in range(first, last + 1, STEP):
        b = min(last, a + STEP - 1)
        p = out / 'logs' / ('%d_%d.json.gz' % (a, b))
        if p.exists():
            continue
        logs = rpc.call('eth_getLogs', [{'address': SETTLEMENT, 'topics': [TRADE_TOPIC], 'fromBlock': hex(a), 'toBlock': hex(b)}])
        keep = []
        for l in logs:
            t = decode_trade(l)
            if t['buy_token'] in LSTS or t['sell_token'] in LSTS:
                keep.append(t)
        with gzip.open(p, 'wt') as f:
            json.dump({'trades_in_range': len(logs), 'lst_trades': keep}, f)
        n += 1
        print(a, b, len(logs), len(keep), flush=True)
    print('ranges fetched', n, rpc.stats())


def load_trades(out):
    rows, total = [], 0
    for p in sorted((Path(out) / 'logs').glob('*.json.gz'), key=lambda p: int(p.name.split('_')[0])):
        with gzip.open(p, 'rt') as f:
            d = json.load(f)
        total += d['trades_in_range']
        rows += d['lst_trades']
    return rows, total


def cmd_orders(args):
    out = Path(args.out)
    trades, _ = load_trades(out)
    cache_p = out / 'orders.json.gz'
    cache = {}
    if cache_p.exists():
        with gzip.open(cache_p, 'rt') as f:
            cache = json.load(f)
    todo = sorted({t['uid'] for t in trades if t['buy_token'] in LSTS and t['sell_token'] in (WETH, ETH)} - set(cache))
    for i, uid in enumerate(todo):
        req = urllib.request.Request(COW_API + uid, headers={'User-Agent': 'llm-quant research', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                cache[uid] = json.loads(r.read())
        except Exception as e:                     # an order the API no longer serves is a gap, not a guess
            cache[uid] = {'error': str(e)[:200]}
        time.sleep(0.25)
        if i % 50 == 49:
            with gzip.open(cache_p, 'wt') as f:
                json.dump(cache, f)
            print(i + 1, 'of', len(todo), flush=True)
    with gzip.open(cache_p, 'wt') as f:
        json.dump(cache, f)
    print('orders cached', len(cache))


def cmd_analyze(args):
    out = Path(args.out)
    trades, total = load_trades(out)
    with gzip.open(out / 'orders.json.gz', 'rt') as f:
        orders = json.load(f)
    headers = D.read_json(LONG / 'headers.json')
    state = D.read_json(LONG / 'state.json')
    hb = sorted(int(x) for x in headers)
    hts = [headers[str(n)]['ts'] for n in hb]

    def ts_at(n):
        return D.interp(hb, hts, n)
    navs = {k: ([s['block'] for s in v], [s['value'] for s in v]) for k, v in state['samples'].items() if v}
    # the venue-median discount per asset, from the per-asset studies' priced swaps
    markets = {}
    for sym, key, path in (('stETH', 'lido', None), ('wstETH', 'lido', None), ('weETH', 'etherfi_ev', 'etherfi_long'),
                           ('rsETH', 'kelp', None)):
        d = Path(args.swaps_long) if path is None else LONG.parents[3] / '2026-10-10' / 'queue_bids_ext' / 'raw' / path
        p = d / ('swaps_%s.jsonl.gz' % key)
        if p.exists():
            with gzip.open(p, 'rt') as f:
                markets[sym] = D.market_discount_fn([json.loads(l) for l in f])
    buys, sells = [], []
    for t in trades:
        lst = t['buy_token'] if t['buy_token'] in LSTS else t['sell_token']
        sym, navk = LSTS[lst]
        nav = 1.0 if navk is None else D.interp(*navs[navk], t['block'])
        ts = ts_at(t['block'])
        if t['buy_token'] in LSTS and t['sell_token'] in (WETH, ETH):
            eth_paid = (t['sell_amount'] + t['fee_amount']) / 1e18
            got = t['buy_amount'] / 1e18
            disc = (1 - eth_paid / (got * nav)) * 1e4 if got else None
            o = orders.get(t['uid'], {})
            created = o.get('creationDate')
            age_h = None
            if created:
                import datetime as dt
                c = dt.datetime.fromisoformat(created.replace('Z', '+00:00')).timestamp()
                age_h = (ts - c) / 3600.0
            limit_disc = None
            if o.get('sellAmount') and o.get('buyAmount') and o.get('kind') == 'sell':
                limit_disc = (1 - int(o['sellAmount']) / 1e18 / (int(o['buyAmount']) / 1e18 * nav)) * 1e4
            m = markets.get(sym)
            buys.append({'sym': sym, 'block': t['block'], 'ts': ts, 'eth': eth_paid, 'discount_bps': disc,
                         'class': o.get('class') or ('?' if 'error' in o else None), 'age_hours': age_h,
                         'limit_discount_bps': limit_disc, 'partially_fillable': o.get('partiallyFillable'),
                         'market_bps': m(int(ts)) if m else None, 'owner': t['owner'], 'tx': t['tx']})
        elif t['sell_token'] in LSTS and t['buy_token'] in (WETH, ETH):
            got = t['buy_amount'] / 1e18
            sold = (t['sell_amount'] + t['fee_amount']) / 1e18
            sells.append({'sym': sym, 'eth': got, 'discount_bps': (1 - got / (sold * nav)) * 1e4 if sold else None})

    def summ(xs):
        xs = [x for x in xs if x is not None]
        return {'n': len(xs), 'p10': D.pct(xs, 0.1), 'p50': statistics.median(xs) if xs else None, 'p90': D.pct(xs, 0.9)} if xs else {'n': 0}
    by_class = collections.defaultdict(list)
    for b in buys:
        by_class[b['class']].append(b)
    res = {'generated': D.utc(), 'episode_blocks': EPISODE, 'settlement_trades_in_episode': total,
           'lst_buys_with_eth': len(buys), 'lst_sells_for_eth': len(sells),
           'sells_eth': sum(s['eth'] for s in sells), 'sells_discount_bps': summ([s['discount_bps'] for s in sells]),
           'by_class': {}}
    for c, xs in sorted(by_class.items(), key=lambda kv: -sum(b['eth'] for b in kv[1])):
        rest = [b for b in xs if b['age_hours'] is not None and b['age_hours'] >= 1.0]
        res['by_class'][str(c)] = {
            'trades': len(xs), 'eth': sum(b['eth'] for b in xs), 'owners': len({b['owner'] for b in xs}),
            'discount_bps': summ([b['discount_bps'] for b in xs]),
            'age_hours': summ([b['age_hours'] for b in xs]),
            'rested_1h_plus': {'trades': len(rest), 'eth': sum(b['eth'] for b in rest),
                               'discount_bps': summ([b['discount_bps'] for b in rest]),
                               'limit_discount_bps': summ([b['limit_discount_bps'] for b in rest]),
                               'fill_minus_market_bps': summ([b['discount_bps'] - b['market_bps'] for b in rest
                                                              if b['discount_bps'] is not None and b['market_bps'] is not None])},
            'by_symbol_eth': {s: sum(b['eth'] for b in xs if b['sym'] == s) for s in sorted({b['sym'] for b in xs})}}
    deep = sorted([b for b in buys if b['age_hours'] and b['age_hours'] >= 1.0 and (b['discount_bps'] or 0) >= 20],
                  key=lambda b: -b['eth'])[:10]
    res['largest_rested_fills_at_20bp_plus'] = [{k: b[k] for k in ('sym', 'block', 'eth', 'discount_bps', 'limit_discount_bps',
                                                                    'market_bps', 'age_hours', 'class', 'tx')} for b in deep]
    D.write_json(out / 'analysis.json', res)
    print(json.dumps(res, indent=1)[:6000])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('collect', 'orders', 'analyze'):
        s = sub.add_parser(name)
        s.add_argument('--out', required=True)
        if name == 'analyze':
            s.add_argument('--swaps-long', required=True, help='directory with swaps_lido/kelp.jsonl.gz (queue_book --long)')
    args = p.parse_args()
    {'collect': cmd_collect, 'orders': cmd_orders, 'analyze': cmd_analyze}[args.cmd](args)


if __name__ == '__main__':
    main()
