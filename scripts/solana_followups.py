#!/usr/bin/env python3
"""Offline follow-ups over a solana_collect window (the Solana counterpart of window_followups.py).

  profile   --addresses A,B,...   in/out counterparties per asset for each address (labelled), top destinations, timing
  program   --programs P,Q,...    shape of a program's transactions: payers, CU, accounts, data sizes, token movement, sample sigs
  token     --mints M,...         per-mint trade tape: buys/sells, traders, venues, implied price path

Writes followups.json into the window directory and prints a digest. Read-only, no RPC.
"""
import argparse
import collections
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import solana_decode as D  # noqa: E402
import solana_scan as S  # noqa: E402


def profile(out, addresses, prices):
    res = {a: {'in': collections.defaultdict(lambda: collections.defaultdict(float)), 'out': collections.defaultdict(lambda: collections.defaultdict(float)), 'in_n': collections.Counter(), 'out_n': collections.Counter(),
               'first': None, 'last': None, 'txs': 0, 'programs': collections.Counter(), 'as_payer': 0} for a in addresses}
    aset = set(addresses)
    for slot, p in S.block_files(out):
        b = S.load_json(p)
        ts = b['blockTime']
        for tx in b['transactions']:
            if tx['meta']['err'] is not None:
                continue
            keys = D.tx_keys(tx)
            hit = aset & set(keys)
            owners = None
            if not hit:
                owners = {a.get('owner') for a in (tx['meta'].get('postTokenBalances') or []) + (tx['meta'].get('preTokenBalances') or [])}
                hit = aset & owners
                if not hit:
                    continue
            f = S.tx_features(tx, keys, prices, ts // 60)
            for a in hit:
                r = res[a]
                r['txs'] += 1
                r['as_payer'] += f['payer'] == a
                r['first'] = ts if r['first'] is None else min(r['first'], ts)
                r['last'] = ts if r['last'] is None else max(r['last'], ts)
                for p_ in f['top_programs']:
                    if p_ not in S.SYSTEMISH:
                        r['programs'][S.name_of(p_)] += 1
                # native SOL: counterparties from sys transfers
                for fr, to, lam in f['sys_transfers']:
                    if to == a and fr != a:
                        r['in']['SOL'][fr] += lam / S.LAMPORTS
                        r['in_n']['SOL'] += 1
                    elif fr == a and to != a:
                        r['out']['SOL'][to] += lam / S.LAMPORTS
                        r['out_n']['SOL'] += 1
                # tokens: owner-level deltas; counterparty = the other owner with the opposite sign on the same mint
                mine = f['by_owner'].get(a, {})
                for mm, v in mine.items():
                    sym = S.SYM.get(mm, S.short(mm))
                    others = [(o, x) for o, d_ in f['by_owner'].items() if o != a for m2, x in d_.items() if m2 == mm and (x > 0) != (v > 0)]
                    cp = max(others, key=lambda t: abs(t[1]))[0] if others else (f['payer'] if f['payer'] != a else '?')
                    (r['in'] if v > 0 else r['out'])[sym][cp] += abs(v) / 10 ** S.DEC.get(mm, next((e['decimals'] for e in f['tok'].values() if e['mint'] == mm), 0))
                    (r['in_n'] if v > 0 else r['out_n'])[sym] += 1
    digest = {}
    for a, r in res.items():
        d = {'address': a, 'label': S.label(a), 'txs': r['txs'], 'as_payer': r['as_payer'], 'first_utc': S.utc(r['first']) if r['first'] else None, 'last_utc': S.utc(r['last']) if r['last'] else None, 'programs': r['programs'].most_common(8), 'assets': {}}
        for side in ('in', 'out'):
            for sym, cps in r[side].items():
                tot = sum(cps.values())
                top = sorted(cps.items(), key=lambda x: -x[1])[:6]
                d['assets'].setdefault(sym, {})[side] = {'total': round(tot, 4), 'n': r[side + '_n'][sym], 'unique': len(cps), 'top': [(c, S.label(c), round(v, 4)) for c, v in top]}
        digest[a] = d
    return digest


def program_shape(out, programs, prices, samples=3):
    res = {p: {'txs': 0, 'ok': 0, 'payers': collections.Counter(), 'cu': [], 'keys': [], 'data': [], 'token_move': 0, 'sol_move': 0, 'n_ix': [], 'sigs': [], 'logs': collections.Counter(), 'co': collections.Counter()} for p in programs}
    pset = set(programs)
    for slot, p_ in S.block_files(out):
        b = S.load_json(p_)
        for tx in b['transactions']:
            keys = D.tx_keys(tx)
            msg = tx['transaction']['message']
            tops = [keys[ix['programIdIndex']] for ix in msg['instructions'] if ix['programIdIndex'] < len(keys)]
            hit = pset & set(tops)
            if not hit:
                continue
            f = S.tx_features(tx, keys, prices, b['blockTime'] // 60)
            for pr in hit:
                r = res[pr]
                r['txs'] += 1
                r['ok'] += f['err'] is None
                r['payers'][f['payer']] += 1
                r['cu'].append(f['cu'])
                r['keys'].append(f['n_keys'])
                r['n_ix'].append(len(msg['instructions']))
                for ix in msg['instructions']:
                    if ix['programIdIndex'] < len(keys) and keys[ix['programIdIndex']] == pr:
                        r['data'].append(len(D.b58decode(ix['data'])) if ix.get('data') else 0)
                r['token_move'] += bool(any(e['delta_raw'] for e in f['tok'].values()))
                r['sol_move'] += any(abs(v) > 100000 for k_, v in f['sol'].items() if k_ != f['payer'] and k_ not in S.JITO_TIPS)
                for l in tx['meta'].get('logMessages') or []:
                    if l.startswith('Program log:') and 'Instruction:' not in l:
                        r['logs'][l[13:80]] += 1
                for q in f['programs']:
                    if q != pr and q not in S.SYSTEMISH:
                        r['co'][S.name_of(q)] += 1
                if len(r['sigs']) < samples and f['err'] is None:
                    r['sigs'].append(f['sig'])
    digest = {}
    for pr, r in res.items():
        n = max(r['txs'], 1)
        digest[pr] = {'program': pr, 'label': S.label(pr), 'txs': r['txs'], 'ok_share': r['ok'] / n, 'unique_payers': len(r['payers']), 'top_payers': r['payers'].most_common(5), 'cu_median': statistics.median(r['cu']) if r['cu'] else None,
                      'keys_median': statistics.median(r['keys']) if r['keys'] else None, 'ix_median': statistics.median(r['n_ix']) if r['n_ix'] else None, 'data_bytes_median': statistics.median(r['data']) if r['data'] else None,
                      'token_move_share': r['token_move'] / n, 'sol_move_share': r['sol_move'] / n, 'top_logs': r['logs'].most_common(6), 'co_programs': r['co'].most_common(8), 'sample_sigs': r['sigs']}
    return digest


def token_tape(out, mints, prices):
    res = {m: {'buys': 0, 'sells': 0, 'buy_usd': 0.0, 'sell_usd': 0.0, 'traders': collections.Counter(), 'venues': collections.Counter(), 'path': [], 'first': None, 'last': None, 'launch_sig': None} for m in mints}
    mset = set(mints)
    for slot, p in S.block_files(out):
        b = S.load_json(p)
        for tx in b['transactions']:
            if tx['meta']['err'] is not None:
                continue
            keys = D.tx_keys(tx)
            if not any(a['mint'] in mset for a in (tx['meta'].get('postTokenBalances') or [])):
                continue
            f = S.tx_features(tx, keys, prices, b['blockTime'] // 60)
            sold, bought = S.swap_legs(f)
            for m in mset & (set(sold) | set(bought)):
                r = res[m]
                r['first'] = b['blockTime'] if r['first'] is None else r['first']
                r['last'] = b['blockTime']
                if f['new_mints'] and r['launch_sig'] is None:
                    r['launch_sig'] = f['sig']
                other = [(mm, v) for mm, v in list(sold.items()) + list(bought.items()) if mm != m]
                usd = sum(u for u in (S.usd_of(mm, v, prices, b['blockTime'] // 60) for mm, v in other) if u)
                side = 'buy' if m in bought else 'sell'
                r[side + 's'] += 1
                r[side + '_usd'] += usd
                r['traders'][f['trader']] += 1
                for v in S.venues_of(f):
                    r['venues'][v] += 1
                amt = (bought.get(m) or sold.get(m) or 0)
                dec = next((e['decimals'] for e in f['tok'].values() if e['mint'] == m), 6)
                if usd and amt:
                    r['path'].append((b['blockTime'], usd / (amt / 10 ** dec), side, round(usd)))
    digest = {}
    for m, r in res.items():
        path = sorted(r['path'])
        digest[m] = {'mint': m, 'symbol': S.SYM.get(m), 'buys': r['buys'], 'sells': r['sells'], 'buy_usd': round(r['buy_usd']), 'sell_usd': round(r['sell_usd']), 'unique_traders': len(r['traders']), 'top_traders': r['traders'].most_common(8), 'venues': r['venues'].most_common(5),
                     'first_utc': S.utc(r['first']) if r['first'] else None, 'last_utc': S.utc(r['last']) if r['last'] else None, 'launch_sig': r['launch_sig'],
                     'price_first': path[0][1] if path else None, 'price_last': path[-1][1] if path else None, 'price_max': max(x[1] for x in path) if path else None, 'price_min': min(x[1] for x in path) if path else None, 'trades_priced': len(path)}
    return digest


def cluster(out, hub, prices):
    """Sybil check for a fan-in hub: who funded the wallets that sent SOL to `hub` (inside the window, before they sent)?"""
    senders = {}
    files = S.block_files(out)
    for slot, p in files:
        b = S.load_json(p)
        for tx in b['transactions']:
            if tx['meta']['err'] is not None:
                continue
            keys = D.tx_keys(tx)
            if hub not in keys:
                continue
            f = S.tx_features(tx, keys, None, 0)
            for fr, to, lam in f['sys_transfers']:
                if to == hub and fr != hub:
                    senders.setdefault(fr, [b['blockTime'], lam])
    funders = collections.Counter()
    funded = 0
    fund_amt = collections.defaultdict(float)
    sender_tokens = collections.Counter()
    for slot, p in files:
        b = S.load_json(p)
        for tx in b['transactions']:
            if tx['meta']['err'] is not None:
                continue
            keys = D.tx_keys(tx)
            hit = [k for k in keys if k in senders]
            if not hit:
                continue
            f = S.tx_features(tx, keys, None, 0)
            for fr, to, lam in f['sys_transfers']:
                if to in senders and fr not in senders and fr != hub and b['blockTime'] <= senders[to][0]:
                    funders[fr] += 1
                    fund_amt[fr] += lam / S.LAMPORTS
                    funded += 1
            for o, mm_ in f['by_owner'].items():
                if o in senders:
                    for mm in mm_:
                        sender_tokens[S.SYM.get(mm, mm)] += 1
    return {hub: {'senders': len(senders), 'sol_in': round(sum(v[1] for v in senders.values()) / S.LAMPORTS, 3), 'first_send_utc': S.utc(min(v[0] for v in senders.values())) if senders else None, 'last_send_utc': S.utc(max(v[0] for v in senders.values())) if senders else None,
                  'senders_funded_in_window': funded, 'unique_funders': len(funders), 'top_funders': [(a, S.label(a), n, round(fund_amt[a], 2)) for a, n in funders.most_common(8)], 'tokens_touched_by_senders': sender_tokens.most_common(8)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['profile', 'program', 'token', 'cluster'])
    ap.add_argument('--out', required=True)
    ap.add_argument('--addresses', default='')
    ap.add_argument('--programs', default='')
    ap.add_argument('--mints', default='')
    args = ap.parse_args()
    prices = S.Prices(args.out)
    if args.cmd == 'profile':
        d = profile(args.out, [a for a in args.addresses.split(',') if a], prices)
    elif args.cmd == 'program':
        d = program_shape(args.out, [a for a in args.programs.split(',') if a], prices)
    elif args.cmd == 'cluster':
        d = {}
        for a in [a for a in args.addresses.split(',') if a]:
            d.update(cluster(args.out, a, prices))
    else:
        d = token_tape(args.out, [a for a in args.mints.split(',') if a], prices)
    path = Path(args.out) / 'followups.json'
    allf = json.loads(path.read_text()) if path.exists() else {}
    allf[args.cmd] = {**allf.get(args.cmd, {}), **d}
    path.write_text(json.dumps(allf, indent=1, default=str))
    print(json.dumps(d, indent=1, default=str)[:12000])


if __name__ == '__main__':
    main()
