#!/usr/bin/env python3
"""Morpho Blue market rate map and Pendle fixed-yield map at one finalized block (read-only, block-pinned, replayable).

For every Morpho Blue market seen in the saved logs: current supply/borrow APY from the deployed IRM (`borrowRateView`),
utilisation, withdrawable liquidity, oracle price. For every Pendle market that traded in the live window (plus the
public Pendle list, kept only as a cross-check): PT price from Pendle's on-chain PY/LP oracle (15-minute TWAP), time to
maturity, implied fixed APY. Joins the two on PT collateral: fixed yield minus Morpho borrow cost (carry), and the
Morpho oracle price versus the Pendle market price (credit given versus market value).

Usage: uv run --with pycryptodome --with eth-abi python scripts/morpho_pendle_scan.py [--out DIR] [--offline]
"""
import argparse
import collections
import datetime as dt
import gzip
import json
import math
import urllib.request
from pathlib import Path

from eth_abi import encode
from non_mev_screen import Evidence, ROOT, calldata, digest, words, addr, string
from vault_oracle_scan import multicall, scalar, metadata, MORPHO, MULTICALL, MARKET_TOPICS

OUT = ROOT / 'research/2026-09-06/opportunities'
YEAR = 365 * 86400
IRM_SIG = 'borrowRateView((address,address,address,address,uint256),(uint128,uint128,uint128,uint128,uint128,uint128))'
PY_ORACLE = '0x9a9fa8338dd5e5b2188006f1cd2ef26d921650c2'  # Pendle PYLpOracle (mainnet); every read below is checked by getOracleState
PENDLE_SWAP = '0x' + digest('Swap(address,address,int256,int256,uint256,uint256)')
PENDLE_API = 'https://api-v2.pendle.finance/core/v1/1/markets/active'
TWAP = 900


def log_files(datasets, block):
    files = {}
    for ds in datasets:
        for p in (ROOT / ds / 'raw/logs').glob('*.json.gz'):
            n = int(p.name.split('.')[0])
            if n <= block:
                files[n] = p
    return files


def discover(out, block):
    path = out / 'discovery.json'
    if path.exists():
        return json.loads(path.read_text())
    prior = ROOT / 'research/2026-09-06/vault_oracles/discovery.json'
    ids = collections.Counter()
    if prior.exists():
        ids.update(json.loads(prior.read_text())['morpho_market_ids'])
    pendle = collections.Counter()
    files = log_files(['research/2026-09-06/live'], block)
    for n, p in sorted(files.items()):
        for l in json.loads(gzip.decompress(p.read_bytes())):
            t = l['topics']
            if not t:
                continue
            if l['address'] == MORPHO and t[0] in MARKET_TOPICS and len(t) > 1:
                ids[t[1]] += 1
            elif t[0] == PENDLE_SWAP and len(l['data']) == 2 + 4 * 64:
                pendle[l['address']] += 1
    d = {'scope': {'live_first_block': min(files), 'live_last_block': max(files), 'live_block_files': len(files),
                   'prior_discovery': str(prior.relative_to(ROOT)) if prior.exists() else None, 'state_block': block},
         'morpho_market_ids': dict(ids.most_common()), 'pendle_swap_emitters': dict(pendle.most_common())}
    path.write_text(json.dumps(d, indent=2) + '\n')
    return d


def pendle_api(out):
    """Public list of active Pendle markets. Cross-check only; not an on-chain observation."""
    path = out / 'pendle_api.json'
    if path.exists():
        return json.loads(path.read_text())
    try:
        req = urllib.request.Request(PENDLE_API, headers={'User-Agent': 'llm-quant research'})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
        rec = {'fetched_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': PENDLE_API, 'markets': d.get('markets', d)}
    except Exception as exc:
        rec = {'fetched_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'source': PENDLE_API, 'error': str(exc)[:200], 'markets': []}
    path.write_text(json.dumps(rec, indent=1) + '\n')
    return rec


def apy(rate_per_sec):
    return math.exp(rate_per_sec * YEAR) - 1


def morpho_markets(e, ids, block):
    res = multicall(e, [(MORPHO, calldata(sig, i)) for i in ids for sig in ['idToMarketParams(bytes32)', 'market(bytes32)']], block)
    rows = []
    for k, i in enumerate(ids):
        p = words(res[2 * k]) if res[2 * k] else None
        s = words(res[2 * k + 1]) if res[2 * k + 1] else None
        if not p or not s or not p[0]:
            continue
        rows.append({'id': i, 'loan': addr(p[0]), 'collateral': addr(p[1]), 'oracle': addr(p[2]), 'irm': addr(p[3]), 'lltv': p[4] / 1e18,
                     'params_raw': p, 'market_raw': s, 'supply_assets_raw': s[0], 'supply_shares_raw': s[1], 'borrow_assets_raw': s[2],
                     'borrow_shares_raw': s[3], 'last_update': s[4], 'fee': s[5] / 1e18})
    # IRM rates: only for markets with a deployed IRM; the call is the same view Morpho uses on accrual
    calls = []
    for r in rows:
        p, s = r['params_raw'], r['market_raw']
        data = '0x' + digest(IRM_SIG)[:8] + encode(['(address,address,address,address,uint256)', '(uint128,uint128,uint128,uint128,uint128,uint128)'],
                                                   [(addr(p[0]), addr(p[1]), addr(p[2]), addr(p[3]), p[4]), tuple(s[:6])]).hex()
        calls.append((r['irm'], data))
        calls.append((r['oracle'], calldata('price()')))
    res = multicall(e, calls, block)
    tokens = metadata(e, sorted({r['loan'] for r in rows} | {r['collateral'] for r in rows if int(r['collateral'], 16)}), block)
    for k, r in enumerate(rows):
        rate = scalar(res[2 * k])
        price = scalar(res[2 * k + 1])
        r['borrow_rate_per_sec'] = rate / 1e18 if rate is not None else None
        r['borrow_apy'] = apy(r['borrow_rate_per_sec']) if rate is not None else None
        sup, bor = r['supply_assets_raw'], r['borrow_assets_raw']
        r['utilisation'] = bor / sup if sup else 0.
        r['supply_apy'] = r['borrow_apy'] * r['utilisation'] * (1 - r['fee']) if r['borrow_apy'] is not None else None
        r['loan_metadata'] = tokens.get(r['loan'])
        r['collateral_metadata'] = tokens.get(r['collateral'])
        ld = (r['loan_metadata'] or {}).get('decimals')
        cd = (r['collateral_metadata'] or {}).get('decimals')
        if ld is not None:
            r['supply_units'] = sup / 10 ** ld
            r['borrow_units'] = bor / 10 ** ld
            r['liquidity_units'] = (sup - bor) / 10 ** ld
        r['oracle_price_raw'] = price
        if price is not None and ld is not None and cd is not None:
            r['oracle_loan_per_collateral'] = price / 10 ** (36 + ld - cd)
        for key in ('params_raw', 'market_raw'):
            r[key] = [str(x) for x in r[key]]
    return rows, tokens


def pendle_markets(e, addresses, block, now):
    rows = []
    res = multicall(e, [(a, calldata(s)) for a in addresses for s in ['readTokens()', 'expiry()', 'isExpired()']], block)
    for k, a in enumerate(addresses):
        rt = res[3 * k]
        if not rt or len(rt) < 2 + 3 * 64:
            continue
        sy, pt, yt = [addr(w) for w in words(rt)[:3]]
        rows.append({'market': a, 'sy': sy, 'pt': pt, 'yt': yt, 'expiry': scalar(res[3 * k + 1]), 'is_expired': scalar(res[3 * k + 2])})
    tokens = metadata(e, sorted({r['pt'] for r in rows} | {r['sy'] for r in rows}), block)
    calls = []
    for r in rows:
        calls.append((PY_ORACLE, calldata('getPtToAssetRate(address,uint32)', r['market'], TWAP)))
        calls.append((PY_ORACLE, calldata('getPtToSyRate(address,uint32)', r['market'], TWAP)))
        calls.append((PY_ORACLE, calldata('getOracleState(address,uint32)', r['market'], TWAP)))
        calls.append((r['sy'], calldata('exchangeRate()')))
        calls.append((r['sy'], calldata('assetInfo()')))
    res = multicall(e, calls, block)
    for k, r in enumerate(rows):
        pa, ps, st, ex, ai = res[5 * k: 5 * k + 5]
        r['pt_symbol'] = (tokens.get(r['pt']) or {}).get('symbol')
        r['sy_symbol'] = (tokens.get(r['sy']) or {}).get('symbol')
        r['pt_to_asset'] = scalar(pa) / 1e18 if pa else None
        r['pt_to_sy'] = scalar(ps) / 1e18 if ps else None
        if st and len(st) >= 2 + 3 * 64:
            w = words(st)
            r['oracle_state'] = {'increase_cardinality_required': bool(w[0]), 'cardinality_required': w[1], 'oldest_observation_satisfied': bool(w[2])}
        r['sy_exchange_rate'] = scalar(ex) / 1e18 if ex else None
        if ai and len(ai) >= 2 + 3 * 64:
            w = words(ai)
            r['sy_asset'] = {'type': w[0], 'address': addr(w[1]), 'decimals': w[2]}
        r['days_to_maturity'] = (r['expiry'] - now) / 86400 if r['expiry'] else None
        ok = r['pt_to_asset'] and r['days_to_maturity'] and r['days_to_maturity'] > 0 and (r.get('oracle_state') or {}).get('oldest_observation_satisfied')
        r['implied_apy'] = (1 / r['pt_to_asset']) ** (365 / r['days_to_maturity']) - 1 if ok else None
        r['implied_apr_simple'] = (1 / r['pt_to_asset'] - 1) * 365 / r['days_to_maturity'] if ok else None
    return rows, tokens


def dilution(e, morpho, block, sizes):
    """Instantaneous supply APY after adding `size` loan units to a market, from the same IRM view with the supply enlarged.
    The IRM's rate-at-target is unchanged by a deposit; only the utilisation term moves. Drift of rate-at-target over the
    following days (toward the 90% target) is not simulated."""
    focus = [r for r in morpho if r.get('supply_units') and r['supply_units'] >= 5e6 and r.get('borrow_apy') is not None
             and (r.get('loan_metadata') or {}).get('decimals') in (6, 18) and (r.get('loan_metadata') or {}).get('symbol') in
             {'USDC', 'USDT', 'PYUSD', 'RLUSD', 'USDS', 'DAI', 'AUSD'}]
    calls = []
    for r in focus:
        p = [int(x) for x in r['params_raw']]
        m = [int(x) for x in r['market_raw']]
        dec = r['loan_metadata']['decimals']
        for size in sizes:
            mm = list(m)
            mm[0] = m[0] + int(size * 10 ** dec)
            data = '0x' + digest(IRM_SIG)[:8] + encode(['(address,address,address,address,uint256)', '(uint128,uint128,uint128,uint128,uint128,uint128)'],
                                                       [(addr(p[0]), addr(p[1]), addr(p[2]), addr(p[3]), p[4]), tuple(mm[:6])]).hex()
            calls.append((r['irm'], data))
    res = multicall(e, calls, block)
    k = 0
    for r in focus:
        r['after_deposit'] = []
        for size in sizes:
            rate = scalar(res[k]); k += 1
            if rate is None:
                r['after_deposit'].append({'size': size}); continue
            b = apy(rate / 1e18)
            u = r['borrow_assets_raw'] / (r['supply_assets_raw'] + size * 10 ** r['loan_metadata']['decimals'])
            r['after_deposit'].append({'size': size, 'utilisation': u, 'borrow_apy': b, 'supply_apy': b * u * (1 - r['fee'])})
    return focus


def join(morpho, pendle, api):
    by_pt = {r['pt']: r for r in pendle}
    api_by_addr = {}
    for m in api.get('markets', []):
        try:
            api_by_addr[m['address'].lower()] = m
        except (KeyError, AttributeError):
            pass
    for r in pendle:
        m = api_by_addr.get(r['market'])
        if m:
            d = m.get('details', {})
            r['api'] = {'name': m.get('name'), 'implied_apy': d.get('impliedApy'), 'underlying_apy': d.get('underlyingApy'),
                        'liquidity_usd': d.get('liquidity'), 'aggregated_apy': d.get('aggregatedApy')}
    for r in morpho:
        p = by_pt.get(r['collateral'])
        if not p:
            continue
        r['pendle'] = {'market': p['market'], 'pt_to_asset': p['pt_to_asset'], 'implied_apy': p['implied_apy'], 'days_to_maturity': p['days_to_maturity'],
                       'underlying_apy_api': (p.get('api') or {}).get('underlying_apy')}
        op = r.get('oracle_loan_per_collateral')
        if op and p['pt_to_asset']:
            # the loan token is a dollar stable in every PT market seen; oracle/market ratio then compares credit given to market value
            r['pendle']['oracle_over_market'] = op / p['pt_to_asset']
            r['pendle']['effective_lltv_on_market_value'] = r['lltv'] * op / p['pt_to_asset']
        if p['implied_apy'] is not None and r.get('borrow_apy') is not None:
            spread = p['implied_apy'] - r['borrow_apy']
            r['pendle']['carry_spread'] = spread
            ltv = 0.8 * r['pendle'].get('effective_lltv_on_market_value', r['lltv'])
            lev = 1 / (1 - ltv)
            r['pendle']['leverage_at_80pct_of_lltv'] = lev
            # levered fixed yield: PT yield on gross position minus borrow cost on the debt, per unit of equity
            r['pendle']['levered_apy_at_80pct_of_lltv'] = p['implied_apy'] * lev - r['borrow_apy'] * (lev - 1)
    return morpho, pendle


def fmt_pct(x, d=2):
    return '–' if x is None else f'{100 * x:.{d}f}%'


def fmt_usd(x):
    if x is None:
        return '–'
    for unit, div in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if abs(x) >= div:
            return f'${x / div:,.1f}{unit}'
    return f'${x:,.0f}'


def tables(morpho, pendle, head, block, ts, sizes):
    lines = [f'# Morpho market rates and Pendle fixed yields at block {block:,} ({dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()})', '']
    sym = lambda r, k: ((r.get(k + '_metadata') or {}).get('symbol') or r[k][:10])
    lending = {}
    for venue, d in (head.get('lending') or {}).items():
        for a, v in d.items():
            lending[(venue, v.get('sym', a))] = v
    comp = head.get('compound') or {}
    stable = {'USDC', 'USDT', 'USDS', 'DAI', 'PYUSD', 'RLUSD', 'AUSD', 'USDe', 'frxUSD', 'EURC', 'EURCV', 'USDtb', 'USR', 'eUSD', 'apxUSD'}
    lines += ['## Morpho markets by loan asset (supply ≥ $1M or borrow ≥ $500k), current IRM rate', '',
              '| loan | collateral | LLTV | supplied | borrowed | util | liquidity | borrow APY | supply APY | oracle px | id |', '|---|---|---|---|---|---|---|---|---|---|---|']
    big = [r for r in morpho if r.get('supply_units') is not None and (r['supply_units'] >= 1e6 or r['borrow_units'] >= 5e5)]
    big.sort(key=lambda r: (sym(r, 'loan'), -r['supply_units']))
    for r in big:
        lines.append(f"| {sym(r, 'loan')} | {sym(r, 'collateral')} | {r['lltv']:.3f} | {fmt_usd(r['supply_units'])} | {fmt_usd(r['borrow_units'])} | {fmt_pct(r['utilisation'], 1)} | {fmt_usd(r['liquidity_units'])} | {fmt_pct(r['borrow_apy'])} | {fmt_pct(r['supply_apy'])} | {r.get('oracle_loan_per_collateral', float('nan')):.5f} | {r['id'][:10]} |")
    lines += ['', '(units are the loan token; stables are shown as dollars, WETH/WBTC markets in token units)', '']
    lines += ['## Best supply APY per loan asset versus Aave v3 / SparkLend / Compound v3 (reserves ≥ $1M)', '',
              '| asset | Morpho best (market, liquidity) | Morpho size-weighted | Aave v3 | SparkLend | Compound v3 |', '|---|---|---|---|---|---|']
    by_loan = collections.defaultdict(list)
    for r in morpho:
        if r.get('supply_units') and r['supply_units'] >= 1e6 and r.get('supply_apy') is not None:
            by_loan[sym(r, 'loan')].append(r)
    for asset, rs in sorted(by_loan.items(), key=lambda kv: -sum(r['supply_units'] for r in kv[1])):
        best = max(rs, key=lambda r: r['supply_apy'])
        w = sum(r['supply_units'] * r['supply_apy'] for r in rs) / sum(r['supply_units'] for r in rs)
        aave = lending.get(('Aave v3', asset), {}).get('supply_apr')
        spark = lending.get(('SparkLend', asset), {}).get('supply_apr')
        c = comp.get(f'Compound v3 {asset}', {}).get('supply_apr')
        lines.append(f"| {asset} | {fmt_pct(best['supply_apy'])} ({sym(best, 'collateral')}, {fmt_usd(best['liquidity_units'])} free) | {fmt_pct(w)} on {fmt_usd(sum(r['supply_units'] for r in rs))} | {fmt_pct(aave)} | {fmt_pct(spark)} | {fmt_pct(c)} |")
    lines += ['', '## Supply APY after a new deposit (markets ≥ $5M in the major dollar stables; IRM re-read with the supply enlarged)', '',
              '| loan | collateral | supplied | supply APY now | ' + ' | '.join('+' + fmt_usd(s) for s in sizes) + ' |', '|---|---|---|---|' + '---|' * len(sizes)]
    for r in sorted([r for r in morpho if r.get('after_deposit')], key=lambda r: (sym(r, 'loan'), -r['supply_units'])):
        cells = ' | '.join(fmt_pct(x.get('supply_apy')) + (f" (u {100 * x['utilisation']:.0f}%)" if x.get('utilisation') is not None else '') for x in r['after_deposit'])
        lines.append(f"| {sym(r, 'loan')} | {sym(r, 'collateral')} | {fmt_usd(r['supply_units'])} | {fmt_pct(r['supply_apy'])} | {cells} |")
    lines += ['', '## Markets at or above the IRM target (utilisation ≥ 90%): rate rising, withdrawals constrained', '',
              '| loan | collateral | supplied | util | liquidity | borrow APY | supply APY |', '|---|---|---|---|---|---|---|']
    for r in sorted([r for r in morpho if r.get('supply_units') and r['supply_units'] >= 5e5 and r['utilisation'] >= 0.9], key=lambda r: -r['utilisation']):
        lines.append(f"| {sym(r, 'loan')} | {sym(r, 'collateral')} | {fmt_usd(r['supply_units'])} | {fmt_pct(r['utilisation'], 1)} | {fmt_usd(r['liquidity_units'])} | {fmt_pct(r['borrow_apy'])} | {fmt_pct(r['supply_apy'])} |")
    lines += ['', '## Pendle markets (those that traded in the live window plus the public active list): PT price and implied fixed APY (on-chain 15-min TWAP oracle)', '',
              '| PT | days left | PT/asset | implied APY | TWAP ok | Pendle API implied | API underlying APY | API liquidity |', '|---|---|---|---|---|---|---|---|']
    for r in sorted(pendle, key=lambda r: -(r['implied_apy'] or -1)):
        a = r.get('api') or {}
        lines.append(f"| {r['pt_symbol']} | {r['days_to_maturity']:.0f} | {r['pt_to_asset'] if r['pt_to_asset'] is None else round(r['pt_to_asset'], 5)} | {fmt_pct(r['implied_apy'])} | {'yes' if (r.get('oracle_state') or {}).get('oldest_observation_satisfied') else 'no'} | {fmt_pct(a.get('implied_apy'))} | {fmt_pct(a.get('underlying_apy'))} | {fmt_usd(a.get('liquidity_usd'))} |")
    lines += ['', '## PT collateral on Morpho: fixed yield versus borrow cost, oracle credit versus market value', '',
              '| loan | PT | market PT/asset | Morpho oracle px | oracle/market | eff. LLTV on mkt value | PT implied APY | borrow APY | carry | lev @80% LLTV | levered APY | liquidity |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in sorted([r for r in morpho if r.get('pendle')], key=lambda r: -(r['pendle'].get('carry_spread') or -9)):
        p = r['pendle']
        lines.append(f"| {sym(r, 'loan')} | {sym(r, 'collateral')} | {p['pt_to_asset']:.5f} | {r.get('oracle_loan_per_collateral', float('nan')):.5f} | {p.get('oracle_over_market', float('nan')):.4f} | {fmt_pct(p.get('effective_lltv_on_market_value'), 1)} | {fmt_pct(p['implied_apy'])} | {fmt_pct(r['borrow_apy'])} | {fmt_pct(p.get('carry_spread'))} | {p.get('leverage_at_80pct_of_lltv', float('nan')):.2f}x | {fmt_pct(p.get('levered_apy_at_80pct_of_lltv'))} | {fmt_usd(r['liquidity_units'])} |")
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=OUT)
    p.add_argument('--offline', action='store_true')
    p.add_argument('--block', type=int, help='pin the state block (default: the existing snapshot.json in --out, else the finalized head)')
    p.add_argument('--sizes', default='1e6,1e7,5e7', help='deposit sizes (loan units) for the post-deposit supply APY simulation')
    a = p.parse_args()
    e = Evidence(a.out, a.offline)
    assert e.get('eth_chainId', []) == '0x1'
    snap = a.out / 'snapshot.json'
    if a.block is None and snap.exists():
        a.block = json.loads(snap.read_text())['number']
    h = e.get('eth_getBlockByNumber', [hex(a.block) if a.block else 'finalized', False])
    block, ts = int(h['number'], 16), int(h['timestamp'], 16)
    (a.out / 'snapshot.json').write_text(json.dumps({'number': block, 'hash': h['hash'], 'timestamp': ts}, indent=2) + '\n')
    d = discover(a.out, block)
    api = pendle_api(a.out)
    print(json.dumps({'block': block, 'morpho_ids': len(d['morpho_market_ids']), 'pendle_emitters': len(d['pendle_swap_emitters']), 'api_markets': len(api.get('markets', []))}), flush=True)
    morpho, mtokens = morpho_markets(e, sorted(d['morpho_market_ids']), block)
    print('morpho markets read', len(morpho), flush=True)
    addresses = sorted(set(d['pendle_swap_emitters']) | {m['address'].lower() for m in api.get('markets', []) if isinstance(m, dict) and m.get('address')})
    pendle, ptokens = pendle_markets(e, addresses, block, ts)
    print('pendle markets read', len(pendle), flush=True)
    morpho, pendle = join(morpho, pendle, api)
    sizes = [float(x) for x in a.sizes.split(',')]
    dilution(e, morpho, block, sizes)
    head = json.loads((ROOT / 'research/2026-09-06/live/head_state.json').read_text())
    (a.out / 'morpho_markets.json').write_text(json.dumps({'block': block, 'markets': morpho, 'tokens': mtokens}, indent=1) + '\n')
    (a.out / 'pendle_markets.json').write_text(json.dumps({'block': block, 'markets': pendle, 'tokens': ptokens}, indent=1) + '\n')
    (a.out / 'tables.md').write_text(tables(morpho, pendle, head, block, ts, sizes))
    print(json.dumps({'requests': e.requests, 'cache_hits': e.hits, 'head_state_block': head.get('block')}), flush=True)


if __name__ == '__main__':
    main()
