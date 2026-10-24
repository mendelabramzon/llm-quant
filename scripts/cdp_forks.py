#!/usr/bin/env python3
"""Liquity v2 forks across chains: where a redemption-indifferent (hedged) borrower is paid, and how much.

Why. On Liquity v2 the hedged min-rate trove is a rent (research/2026-10-23/stability_pools/findings.md): unhedged
borrowers pay to stand behind it in the redemption queue, 75% of their interest goes to the stability pool (SP), and
the redemption fee stays in the redeemed trove. Every fork of the same code carries the same rent at its own rates,
sizes and liquidity. This reads each fork's live state, generically, from its CollateralRegistry (addresses from
DefiLlama's registries/liquity.js), and the last 30 days of redemptions from the chain's explorer.

Per branch: collateral token and price, debt, collateral, CCR, SP deposits, average borrower rate (ActivePool
aggWeightedDebtSum / aggRecordedDebt), the 60 lowest-rate troves (the queue a new trove would join), the implied SP
yield (75% x avg rate x debt / SP deposits, the Liquity v2 split; forks may differ), shutdown state; per fork: the
stablecoin's price and DEX pools (GeckoTerminal), the current redemption rate.

    python3 scripts/cdp_forks.py snapshot          # -> research/2026-10-24/cdp_forks/snapshot.json
    python3 scripts/cdp_forks.py redemptions       # -> redemptions.json (30 days, explorer getLogs)
    python3 scripts/cdp_forks.py render            # -> tables to stdout
"""
import argparse
import json
import time
import urllib.request
from pathlib import Path

from dislocation_history import keccak, sel

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / '2026-10-24' / 'cdp_forks'

CHAINS = {   # rpc, chain id (Etherscan v2), llama coins key, geckoterminal network
    'ethereum': (['https://ethereum-rpc.publicnode.com', 'https://eth.drpc.org'], 1, 'ethereum', 'eth'),
    'arbitrum': (['https://arbitrum-one-rpc.publicnode.com', 'https://arb1.arbitrum.io/rpc'], 42161, 'arbitrum', 'arbitrum'),
    'base': (['https://base-rpc.publicnode.com', 'https://mainnet.base.org'], 8453, 'base', 'base'),
    'hyperevm': (['https://rpc.hyperliquid.xyz/evm', 'https://hyperliquid.drpc.org'], 999, 'hyperliquid', 'hyperevm'),
    'plasma': (['https://rpc.plasma.to', 'https://plasma.drpc.org'], 9745, 'plasma', 'plasma'),
    'scroll': (['https://rpc.scroll.io', 'https://scroll-rpc.publicnode.com'], 534352, 'scroll', 'scroll'),
    'flare': (['https://flare-api.flare.network/ext/C/rpc', 'https://flare.drpc.org'], 14, 'flare', 'flare'),
    'swellchain': (['https://swell-mainnet.alt.technology', 'https://rpc.ankr.com/swell'], 1923, 'swellchain', 'swellchain'),
}
FORKS = {   # DefiLlama registries/liquity.js, helperType v2
    'liquity-v2': [('ethereum', '0xf949982b91c8c61e952b3ba942cbbfaef5386684')],
    'felix': [('hyperevm', '0x9De1e57049c475736289Cb006212F3E1DCe4711B')],
    'enosys-loans': [('flare', '0x9474206bc035D03d142264fd9913d1D51246d3AC')],
    'asymmetry-usdaf': [('ethereum', '0xCFf0DcAb01563e5324ef9D0AdB0677d9C167d791'),
                        ('ethereum', '0x33D68055Cd54061991B2e98b9ab326fFCE4d60Fe')],
    'nerite': [('arbitrum', '0x7f7fbc2711c0d6e8ef757dbb82038032dd168e68')],
    'ebisu': [('ethereum', '0x5e159fAC2D137F7B83A12B9F30ac6aB2ba6d45E7'), ('plasma', '0x602096a2f43b43d11dcb3713702dda963c45adc6')],
    'quill': [('scroll', '0xcc4f29f9d1b03c8e77fc0057a120e2c370d6863d'), ('scroll', '0x358d90036e70542ae24b3813c0efecc1f8811442')],
    'orki': [('swellchain', '0xce9f80a0dcd51fb3dd4f0d6bec3afdcaea10c912')],
    'base-dollar': [('base', '0x7551ebfc8340b7f91874942be9c653733d4fb04f')],
    'defi-dollar': [('ethereum', '0x1ec9287465ef04a7486779e81370c15624c939e8')],
}
SP_SPLIT = 0.75
N_LOWEST = 60
T_RED = keccak('Redemption(uint256,uint256,uint256,uint256,uint256,uint256)')
T_FEE = keccak('RedemptionFeePaidToTrove(uint256,uint256)')


class Client:
    def __init__(self, chain):
        self.urls, self.i, self.n = CHAINS[chain][0], 0, 0

    def call(self, to, data):
        body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call',
                           'params': [{'to': to, 'data': data}, 'latest']}).encode()
        for attempt in range(6):
            url = self.urls[(self.i + attempt) % len(self.urls)]
            try:
                req = urllib.request.Request(url, body, {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as r:
                    j = json.loads(r.read())
                self.n += 1
                if 'error' in j:
                    return None
                return j.get('result')
            except Exception:
                time.sleep(0.5 * (attempt + 1))
        return None

    def num(self, to, sig, *args):
        r = self.call(to, sel(sig) + ''.join(_w(a) for a in args))
        return int(r[2:66], 16) if r and len(r) >= 66 else None

    def addr(self, to, sig, *args):
        v = self.num(to, sig, *args)
        return None if v is None else '0x%040x' % v

    def words(self, to, sig, *args):
        r = self.call(to, sel(sig) + ''.join(_w(a) for a in args))
        return [int(r[2 + 64 * i:66 + 64 * i], 16) for i in range((len(r) - 2) // 64)] if r and len(r) > 2 else None

    def string(self, to, sig):
        r = self.call(to, sel(sig))
        if not r or len(r) < 130:
            return None
        try:
            n = int(r[66:130], 16)
            return bytes.fromhex(r[130:130 + 2 * n]).decode(errors='replace')
        except ValueError:
            return bytes.fromhex(r[2:66]).rstrip(b'\0').decode(errors='replace')


def _w(v):
    if isinstance(v, str):
        return v[2:].lower().rjust(64, '0')
    return '%064x' % int(v)


def get_json(url, tries=3):
    for a in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0',
                                                                             'Accept': 'application/json'}), timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            time.sleep(2 * (a + 1))
    return None


def prices(chain, addrs):
    key = CHAINS[chain][2]
    q = ','.join(f'{key}:{a}' for a in addrs)
    j = get_json(f'https://coins.llama.fi/prices/current/{q}') or {}
    return {k.split(':', 1)[1].lower(): v.get('price') for k, v in j.get('coins', {}).items()}


def branch_state(c, reg, i):
    tm = c.addr(reg, 'getTroveManager(uint256)', i)
    tok = c.addr(reg, 'getToken(uint256)', i)
    b = {'i': i, 'tm': tm, 'token': tok, 'symbol': c.string(tok, 'symbol()'), 'decimals': c.num(tok, 'decimals()')}
    b['sp'] = c.addr(tm, 'stabilityPool()')
    b['ap'] = c.addr(tm, 'activePool()')
    b['sorted'] = c.addr(tm, 'sortedTroves()')
    b['bo'] = c.addr(tm, 'borrowerOperations()')
    b['debt'] = (c.num(tm, 'getEntireBranchDebt()') or 0) / 1e18
    b['coll'] = (c.num(tm, 'getEntireBranchColl()') or 0) / 10 ** (b['decimals'] or 18)
    b['ccr'] = (c.num(tm, 'CCR()') or 0) / 1e18
    b['mcr'] = (c.num(b['bo'], 'MCR()') or 0) / 1e18 if b['bo'] else None
    b['shutdown'] = c.num(tm, 'shutdownTime()')
    b['n_troves'] = c.num(tm, 'getTroveIdsCount()')
    b['sp_deposits'] = (c.num(b['sp'], 'getTotalBoldDeposits()') or c.num(b['sp'], 'getTotalfeUSDDeposits()') or 0) / 1e18
    w, rd = c.num(b['ap'], 'aggWeightedDebtSum()'), c.num(b['ap'], 'aggRecordedDebt()')
    b['avg_rate'] = w / rd / 1e18 if w and rd else None
    # the queue a new trove joins: lowest-rate troves first (SortedTroves tail)
    low, tid = [], c.num(b['sorted'], 'getLast()')
    while tid and len(low) < N_LOWEST:
        d = c.words(tm, 'getLatestTroveData(uint256)', tid)
        if d:
            low.append({'rate': d[6] / 1e18, 'debt': d[0] / 1e18, 'coll': d[1] / 10 ** (b['decimals'] or 18)})
        tid = c.num(b['sorted'], 'getPrev(uint256)', tid)
    b['lowest'] = low
    if b['avg_rate'] and b['sp_deposits']:
        b['sp_apr_est'] = SP_SPLIT * b['avg_rate'] * b['debt'] / b['sp_deposits']
    return b


def snapshot(args):
    OUT.mkdir(parents=True, exist_ok=True)
    out = {}
    for fork, regs in FORKS.items():
        if args.only and fork not in args.only.split(','):
            continue
        for chain, reg in regs:
            c = Client(chain)
            try:
                f = fork_state(c, fork, chain, reg)
            except Exception as e:                   # one broken fork must not stop the census
                print(f'{fork} {chain} {reg}: {type(e).__name__} {e}')
                continue
            if f:
                out[f'{fork}:{chain}:{reg}'] = f
    prev = json.loads((OUT / 'snapshot.json').read_text()) if args.only and (OUT / 'snapshot.json').exists() else {}
    prev.update(out)
    (OUT / 'snapshot.json').write_text(json.dumps(prev, indent=1))


def fork_state(c, fork, chain, reg):
    n = c.num(reg, 'totalCollaterals()')
    if not n:
        print(f'{fork} {chain} {reg}: no totalCollaterals (dead or different ABI)')
        return None
    branches = [branch_state(c, reg, i) for i in range(n)]
    bold = c.addr(reg, 'boldToken()')
    for b in branches:
        bold = bold or c.addr(reg, 'feUSDToken()') or c.addr(b['sp'], 'boldToken()')  # Felix renames it
    if not bold:
        print(f'{fork} {chain}: stablecoin address not found')
        return None
    f = {'fork': fork, 'chain': chain, 'registry': reg, 'stable': bold, 'stable_symbol': c.string(bold, 'symbol()'),
         'stable_supply': (c.num(bold, 'totalSupply()') or 0) / 1e18,
         'redemption_rate': (c.num(reg, 'getRedemptionRateWithDecay()') or 0) / 1e18,
         'branches': branches}
    px = prices(chain, [bold] + [b['token'] for b in f['branches']])
    f['stable_price'] = px.get(bold.lower())
    for b in f['branches']:
        b['price'] = px.get(b['token'].lower())
    gt = get_json(f'https://api.geckoterminal.com/api/v2/networks/{CHAINS[chain][3]}/tokens/{bold}/pools?page=1')
    f['pools'] = [{'name': p['attributes']['name'], 'address': p['attributes']['address'],
                   'reserve_usd': float(p['attributes'].get('reserve_in_usd') or 0),
                   'vol24h': float((p['attributes'].get('volume_usd') or {}).get('h24') or 0),
                   'dex': p['relationships']['dex']['data']['id']}
                  for p in (gt or {}).get('data', [])][:8]
    time.sleep(2.1)
    print(f"{fork:16s} {chain:10s} {f['stable_symbol']} supply {f['stable_supply']/1e6:7.2f}M px {f['stable_price']} "
          f"redemption rate {f['redemption_rate']*100:.2f}% calls {c.n}")
    for b in f['branches']:
        print(f"   {b['symbol']:10s} debt {b['debt']/1e6:7.3f}M SP {b['sp_deposits']/1e6:7.3f}M avg {100*(b['avg_rate'] or 0):5.2f}% "
              f"SP~{100*(b.get('sp_apr_est') or 0):5.1f}% MCR {b['mcr']} CCR {b['ccr']} shut {b['shutdown']} "
              f"lowest {[round(x['rate']*100, 2) for x in b['lowest'][:5]]}")
    return f


T_OP = keccak('TroveOperation(uint256,uint8,uint256,uint256,uint256,int256,uint256,int256)')
LOG_RPC = {'hyperevm': (['https://rpc.hyperliquid.xyz/evm', 'https://rpc.hypurrscan.io',     # urls, max range,
                         'https://hyperliquid-json-rpc.stakely.io'], 1_000, 1.0),            # block seconds
           'ethereum': (['https://ethereum-rpc.publicnode.com'], 10_000, 12.0),
           'base': (['https://base-rpc.publicnode.com'], 10_000, 2.0),
           'arbitrum': (['https://arbitrum-one-rpc.publicnode.com'], 50_000, 0.25)}
BLOCKSCOUT = {'flare': 'https://flare-explorer.flare.network/api'}


def _rpc(url, method, params):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    req = urllib.request.Request(url, body, {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def logs_rpc(chain, addrs, topic, days):
    """Fixed-range getLogs, chunks spread over the chain's endpoints in parallel (HyperEVM caps a query at 1,000
    blocks, ~17 minutes)."""
    from concurrent.futures import ThreadPoolExecutor
    urls, span, secs = LOG_RPC[chain]
    head = None
    for attempt in range(10):
        try:
            head = int(_rpc(urls[attempt % len(urls)], 'eth_blockNumber', [])['result'], 16)
            break
        except (KeyError, OSError, ValueError):
            time.sleep(2)
    lo = head - int(days * 86400 / secs)
    starts = list(range(lo, head + 1, span))

    def one(i):
        a = starts[i]
        for attempt in range(8):
            url = urls[(i + attempt) % len(urls)]
            try:
                r = _rpc(url, 'eth_getLogs', [{'address': addrs, 'topics': [topic if isinstance(topic, list) else [topic]], 'fromBlock': hex(a),
                                               'toBlock': hex(min(a + span - 1, head))}])
                if 'result' in r:
                    return r['result']
            except Exception:
                pass
            time.sleep(0.5 * (attempt + 1))
        print(f'  {chain}: gave up on {a}', flush=True)
        return []

    out = []
    with ThreadPoolExecutor(len(urls) * 2) as ex:
        for n, res in enumerate(ex.map(one, range(len(starts)))):
            out += res
            if n % 200 == 0:
                print(f'  {chain} {n}/{len(starts)} chunks ({len(out)} logs)', flush=True)
    return out, head


def logs_blockscout(chain, addrs, topic, days, window=50_000):
    """Blockscout getLogs in fixed block windows (paging one huge range is slow); Flare blocks ~1.8 s."""
    base, out = BLOCKSCOUT[chain], []
    head = int(get_json(f'{base}?module=block&action=eth_block_number')['result'], 16)
    lo = head - int(days * 86400 / 1.8)
    for a in addrs:
        for w in range(lo, head + 1, window):
            page = 1
            while True:
                j = get_json(f'{base}?module=logs&action=getLogs&fromBlock={w}&toBlock={min(w + window - 1, head)}'
                             f'&address={a}&topic0={topic}&page={page}&offset=1000') or {}
                res = j.get('result') or []
                out += [dict(x, address=a) for x in res]
                if len(res) < 1000:
                    break
                page += 1
        print(f'  {chain} {a[:10]} {len(out)} logs', flush=True)
    for x in out:                                   # Blockscout returns decimal-free hex fields like the RPC
        x.setdefault('transactionHash', x.get('transactionHash'))
    return out, head


def redemptions(args):
    snap = json.loads((OUT / 'snapshot.json').read_text())
    path = OUT / f"redemptions_{args.only or 'all'}.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for key, f in snap.items():
        if args.only and f['fork'] not in args.only.split(','):
            continue
        ch = f['chain']
        tms = [b['tm'] for b in f['branches'] if b['debt'] > 1000]
        if not tms or (ch not in LOG_RPC and ch not in BLOCKSCOUT):
            continue
        getter = logs_blockscout if ch in BLOCKSCOUT else logs_rpc
        if getter is logs_rpc:                       # one pass for both events: the RPC's range cap is the cost
            both, _ = logs_rpc(ch, tms, [T_OP, T_RED], args.days)
            ops = [x for x in both if x['topics'][0] == T_OP]
            reds = [x for x in both if x['topics'][0] == T_RED]
        else:
            ops, _ = getter(ch, tms, T_OP, args.days)
            reds, _ = getter(ch, tms, T_RED, args.days)
        sym = {b['tm'].lower(): b['symbol'] for b in f['branches']}
        rows = []
        for lg in ops:
            d = lg['data']
            if int(d[2:66], 16) != 6:                # op 6 = redeemCollateral
                continue
            debt = int(d[2 + 64 * 4:66 + 64 * 4], 16)
            debt = debt - (1 << 256) if debt >> 255 else debt
            rows.append({'branch': sym.get(lg['address'].lower()), 'tx': lg['transactionHash'],
                         'block': int(lg['blockNumber'], 16), 'rate': int(d[66:130], 16) / 1e18, 'debt': -debt / 1e18})
        fees = []
        for lg in reds:
            d = lg['data']
            w = [int(d[2 + 64 * i:66 + 64 * i], 16) for i in range(6)]
            fees.append({'branch': sym.get(lg['address'].lower()), 'tx': lg['transactionHash'], 'actual': w[1] / 1e18,
                         'fee': w[3] / (w[2] + w[3]) if w[2] + w[3] else None})
        res[key] = {'days': args.days, 'ops': rows, 'red': fees}
        by = {}
        for r in rows:
            by.setdefault(r['branch'], []).append(r)
        print(f"{f['fork']:14s} {ch:9s} redemption txs {len(fees):4d} redeemed {sum(x['actual'] for x in fees)/1e6:7.3f}M "
              f"in {args.days}d", {b: (len(v), round(sum(x['debt'] for x in v) / 1e3), round(max(x['rate'] for x in v) * 100, 2))
                                   for b, v in by.items()}, flush=True)
        path.write_text(json.dumps(res))


# One $10k trade per candidate branch: hedged trove at the floor rate, minted stable sold for more collateral, all
# collateral shorted on Hyperliquid. c and k are set from MCR and the hedge coin's volatility (see findings: c=1.5,
# k=5 had no liquidation on ETH since 2025-05 with a 5% rebalance band; HYPE moves ~2x ETH, so c 1.9, k 3).
# stake: the collateral's own yield; sale: cost to sell the stable today (book/pool, measured); fixed: $ per year of
# gas + bridging for ~150-250 rebalances (Ethereum ~$3 each; HyperEVM<->HyperCore transfers ~free; Flare<->HL via a
# bridge ~$2 each).
CANDIDATES = [
    # fork, branch symbol, hedge coin, stake, c, k, sale cost, fixed $/yr, venue note
    ('liquity-v2', 'rETH', 'ETH', 0.022, 1.5, 5, 0.0049, 450, 'Ethereum; BOLD 0.9956 on Curve (+4bp fee)'),
    ('liquity-v2', 'wstETH', 'ETH', 0.0222, 1.5, 5, 0.0049, 450, 'Ethereum; BOLD 0.9956 on Curve (+4bp fee)'),
    ('liquity-v2', 'WETH', 'ETH', 0.0, 1.35, 5, 0.0049, 450, 'Ethereum'),
    ('felix', 'feUBTC', 'BTC', 0.0, 1.6, 5, 0.0010, 40, 'HyperEVM; feUSD 0.999 bid on HyperCore spot ($79k)'),
    ('felix', 'kHYPE', 'HYPE', 0.023, 1.9, 3, 0.0010, 40, 'HyperEVM'),
    ('felix', 'wstHYPE', 'HYPE', 0.022, 1.9, 3, 0.0010, 40, 'HyperEVM'),
    ('felix', 'WHYPE', 'HYPE', 0.0, 1.9, 3, 0.0010, 40, 'HyperEVM'),
    ('enosys-loans', 'FXRP', 'XRP', 0.0, 1.5, 4, 0.0125, 300, 'Flare; CDP 0.988 on Enosys v3 (+5bp fee)'),
]


def trades(args):
    snap = json.loads((OUT / 'snapshot.json').read_text())
    fund = json.loads((OUT / 'hl_funding.json').read_text())
    red = {}
    for p_ in OUT.glob('redemptions_*.json'):
        red.update(json.loads(p_.read_text()))
    E, r, rows = args.equity, 0.0051, []
    for fork, sym, coin, stake, c, k, sale, fixed, note in CANDIDATES:
        key, f = next((k_, v) for k_, v in snap.items() if v['fork'] == fork and any(b['symbol'] == sym for b in v['branches']))
        b = next(x for x in f['branches'] if x['symbol'] == sym)
        lev = 1 / (1 - 1 / c + 1 / k)
        X, D, M = lev * E, lev * E / c, lev * E / k
        fnd = min(fund[coin]['90d'], fund[coin]['30d'])
        carry = X * (stake + fnd) - D * r
        entry = D * sale + D * 0.06 * 7 / 365        # one sale + the 7-day upfront fee (6% cap)
        net = carry - entry - fixed
        ahead = sum(x['debt'] for x in b['lowest'] if x['rate'] <= r + 1e-9)
        unbacked = {x['symbol']: max(0.0, x['debt'] - x['sp_deposits']) for x in f['branches']}
        share = unbacked[sym] / sum(unbacked.values()) if sum(unbacked.values()) else 0.0
        rr = red.get(key, {})
        red30 = sum(x['debt'] for x in rr.get('ops', []) if x['branch'] == sym)
        rows.append({'fork': fork, 'chain': f['chain'], 'branch': sym, 'hedge': coin, 'price': b['price'],
                     'stable': f['stable_symbol'], 'stable_px': f['stable_price'], 'avg_rate': b['avg_rate'],
                     'lowest_rate': b['lowest'][0]['rate'] if b['lowest'] else None, 'ahead_at_or_below_r': ahead,
                     'sp_apr_est': b.get('sp_apr_est'), 'redemption_share': share, 'redeemed_30d': red30 if rr else None,
                     'mcr': b['mcr'], 'c': c, 'k': k, 'lev': lev, 'coll_usd': X, 'coll_units': X / b['price'],
                     'debt': D, 'margin': M, 'funding': fnd, 'stake': stake, 'carry': carry, 'entry': entry,
                     'fixed': fixed, 'net_year1': net, 'roe': net / E, 'liq_move': 1 - b['mcr'] / c, 'note': note})
        x = rows[-1]
        print(f"{fork:12s} {sym:7s} lev {lev:.2f} coll ${X:,.0f} ({X / b['price']:.4f} {sym}) debt {D:,.0f} margin {M:,.0f} "
              f"fund {fnd*100:.2f}% carry ${carry:,.0f} entry ${entry:,.0f} fixed ${fixed} -> ${net:,.0f}/yr "
              f"({net / E * 100:.1f}%, ${net / 12:,.0f}/mo) liq at -{x['liq_move']*100:.0f}% ahead ${ahead/1e3:,.0f}k "
              f"red-share {share*100:.0f}% red30d {red30/1e3 if rr else float('nan'):.0f}k")
    (OUT / f'trades_{int(E)}.json').write_text(json.dumps(rows, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('snapshot')
    s.add_argument('--only', default='')
    s.set_defaults(fn=snapshot)
    r = sub.add_parser('redemptions')
    r.add_argument('--only', default='')
    r.add_argument('--days', type=float, default=30)
    r.set_defaults(fn=redemptions)
    t = sub.add_parser('trades')
    t.add_argument('--equity', type=float, default=1e4)
    t.set_defaults(fn=trades)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
