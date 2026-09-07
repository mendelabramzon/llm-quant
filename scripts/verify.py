#!/usr/bin/env python3
"""Adversarial re-derivation of a window's headline numbers, plus source-backed mechanism assertions.

The problem this solves. `live_scan analyze` is one large pass that produces every number in `report.md` and every claim
in `insights.md`. Nothing re-derives those numbers, so the confidence labels in the prose are asserted rather than
earned, and the two label bugs this project already hit were both found by hand.

Two kinds of check live here.

**Numeric checks** recompute a headline straight from the raw blocks and logs through `window_raw`, which shares nothing
with `live_scan.State` except the token table and the price basis. A mismatch means the aggregation drifted. The point is
not that the second number is more correct — it is that two independent readings agreeing is evidence, and one number
alone is not.

**Mechanism checks** take a claim in prose ("depositFor does not set lastDepositBlock", "that address is a smart account,
not an exchange") and assert the specific fact against verified source or the chain. These are the claims that carry the
most weight in a research note and have the least support, so each is written down as a named, re-runnable assertion
instead of being re-argued from traces every time.

**The label band** is what the provenance registry buys. Exchange flow is recomputed at each provenance tier, so the
report can say "net stable flow is +$40M using verified labels only, +$41M including model memory" rather than quoting
one number that silently depends on 47 unverified memory tags.

    uv run --with pycryptodome python scripts/verify.py --out research/2026-09-07/live_midday
    uv run --with pycryptodome python scripts/verify.py --out ... --mechanisms      also run the source-backed checks
"""
import argparse
import collections
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import labels as L
from window_raw import Window, median

ROOT = Path(__file__).resolve().parents[1]
ZERO = '0x' + '0' * 40
# CCTP v1 and v2 declare DepositForBurn with different signatures, so they hash to different topics. Watching only the
# v1 topic silently drops every v2 send, which is most of the current traffic.
CCTP_DEPOSIT_FOR_BURN = {'0x2fa9ca894982930190727e75500a97d8dc500233a5065e0f3126c48fbe0343c0',   # v1
                         '0x0c8c1cbdc5190613ebd485511d4e2812cfa45eecb79d845893331fedad5130a5'}   # v2
LENDING_POOLS = {'0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2': 'Aave v3',
                 '0xc13e21b648a5ee794902342038ff3adab66be987': 'SparkLend'}
USDC = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
CCTP_DOMAINS = {0: 'Ethereum', 1: 'Avalanche', 2: 'OP Mainnet', 3: 'Arbitrum', 4: 'Noble', 5: 'Solana', 6: 'Base',
                7: 'Polygon', 8: 'Sui', 9: 'Aptos', 10: 'Unichain', 11: 'Linea', 12: 'Codex', 13: 'Sonic', 14: 'World Chain'}


# ----------------------------------------------------------------------------------------------------------------------
# Numeric checks
# ----------------------------------------------------------------------------------------------------------------------
class Recompute:
    """One pass over the raw window that produces every headline this module checks.

    Deliberately written as one flat loop with no helper objects: the whole point is that it cannot share a bug with
    `live_scan.State`, so it does not share code with it either.
    """

    def __init__(self, w, exchanges):
        self.w = w
        self.ex = exchanges
        self.blocks = self.txs = self.logs = 0
        self.mint = collections.Counter()      # symbol -> USD minted (from the zero address)
        self.burn = collections.Counter()
        self.flow_in = collections.Counter()   # symbol -> USD into an exchange address
        self.flow_out = collections.Counter()
        self.gas_to = collections.Counter()
        self.cctp = collections.defaultdict(lambda: {'n': 0, 'usd': 0.0})
        self.rates = collections.defaultdict(list)
        self.transfers = []                    # kept for the leverage check, which needs to replay hops

    def run(self, min_usd=1e4):
        from window_raw import TRANSFER, RESERVE_DATA_UPDATED, hx, word, topic_addr, RAY
        w = self.w
        eth = w.prices.get('ETH')
        for b, logs in w.blocks():
            n, ts = hx(b['number']), hx(b['timestamp'])
            self.blocks += 1
            self.txs += len(b['transactions'])
            self.logs += len(logs)
            for t in b['transactions']:
                if t.get('to'):
                    self.gas_to[t['to'].lower()] += hx(t['gas'])
                v = hx(t.get('value', 0))
                if v and eth:
                    u = v / 1e18 * eth
                    if u >= min_usd and t.get('to'):
                        self._leg({'block': n, 'ts': ts, 'tx': t['hash'], 'token': 'ETH', 'sym': 'ETH',
                                   'from': t['from'].lower(), 'to': t['to'].lower(), 'raw': v, 'usd': u})
            for l in logs:
                tp = l['topics']
                if not tp:
                    continue
                if tp[0] == TRANSFER and len(tp) == 3 and len(l['data']) >= 66:
                    tok = l['address'].lower()
                    raw = word(l['data'], 0)
                    u = w.usd(tok, raw)
                    if u is None:
                        continue
                    sym = w.symbol(tok)
                    frm, to = topic_addr(tp[1]), topic_addr(tp[2])
                    if frm == ZERO:
                        self.mint[sym] += u
                    if to == ZERO:
                        self.burn[sym] += u
                    if u >= min_usd:
                        self._leg({'block': n, 'ts': ts, 'tx': l['transactionHash'], 'token': tok, 'sym': sym,
                                   'from': frm, 'to': to, 'raw': raw, 'usd': u})
                elif tp[0] == RESERVE_DATA_UPDATED and len(tp) >= 2:
                    venue = LENDING_POOLS.get(l['address'].lower())
                    if venue:
                        d = l['data']
                        self.rates[(venue, topic_addr(tp[1]))].append((n, word(d, 0) / RAY, word(d, 2) / RAY))
                elif tp[0] in CCTP_DEPOSIT_FOR_BURN:
                    # v1 indexes (nonce, burnToken, depositor); v2 indexes (burnToken, depositor, minFinalityThreshold).
                    # Both lay the unindexed body out as amount, mintRecipient, destinationDomain, so the amount is word
                    # 0 and the destination is word 2 in either version. The burn token is whichever topic is a token.
                    tok = next((topic_addr(t_) for t_ in tp[1:] if topic_addr(t_) in w.tokens), None)
                    if tok is None:
                        continue
                    u = w.usd(tok, word(l['data'], 0))
                    if u is None:
                        continue
                    dom = word(l['data'], 2)
                    key = (w.symbol(tok), CCTP_DOMAINS.get(dom, 'domain %s' % dom))
                    self.cctp[key]['n'] += 1
                    self.cctp[key]['usd'] += u
        return self

    def _leg(self, x):
        self.transfers.append(x)
        ti, to = x['from'] in self.ex, x['to'] in self.ex
        if to and not ti:
            self.flow_in[x['sym']] += x['usd']
        elif ti and not to:
            self.flow_out[x['sym']] += x['usd']


def exchange_set(min_tier=None):
    """Addresses whose flow counts as exchange flow, optionally cut at a provenance tier.

    Built from `live_scan.load_address_book()`, not from the registry file alone: the book also holds the behavioural
    and memory tiers, and those are most of the exchange set. Sharing the *label input* is deliberate — verify checks
    whether the aggregation is right, while the tier cut is what probes whether the labels are.
    """
    import live_scan
    book = live_scan.load_address_book()
    cut = L.TIERS.index(min_tier) if min_tier else len(L.TIERS)
    return {a for a, v in book.items()
            if v.get('kind') in L.EXCHANGE_KINDS and L.tier_rank(v.get('source')) <= cut}


def leverage_to_exchange(transfers, followed, exchanges, book):
    """Re-derive `sum(to_exchange_usd)` for the ops the analysis already followed.

    The original walks proceeds forward from a borrow/withdraw receiver: any hop landing on an exchange counts, plus one
    forwarding hop through an *unlabelled* intermediary. This repeats that walk over an independently decoded transfer
    stream. It is the number the CoW mislabel moved by 5x, so it is the one most worth a second reading.

    The analysis records the reserve *symbol* rather than its address, so the token is recovered by symbol from the
    same token table both sides price with.
    """
    by_token_from = collections.defaultdict(list)
    by_symbol = {}
    for x in transfers:
        by_token_from[(x['token'], x['from'])].append(x)
        by_symbol.setdefault(x['sym'], x['token'])
    total = 0.0
    per_op = []
    for f in followed:
        o = f['op']
        recv = (o.get('receiver') or '').lower()
        tok = by_symbol.get(o.get('sym'))
        if not recv or not tok:
            continue
        hops = sorted([x for x in by_token_from.get((tok, recv), [])
                       if x['block'] >= o['block'] and x['ts'] - o['ts'] <= 3600], key=lambda x: x['block'])
        got = 0.0
        for x in hops[:12]:
            dst = x['to']
            if dst in exchanges:
                got += x['usd']
            elif dst not in book:   # chase a forwarding hop only through an unlabelled intermediary
                if any(y['block'] >= x['block'] and y['ts'] - x['ts'] <= 3600 and y['to'] in exchanges
                       for y in by_token_from.get((tok, dst), [])):
                    got += x['usd']
        per_op.append({'tx': o['tx'], 'sym': o.get('sym'), 'usd': round(got)})
        total += got
    return total, per_op


def close(a, b, tol=0.02, floor=1.0):
    if a is None or b is None:
        return False
    return abs(a - b) <= max(tol * max(abs(a), abs(b)), floor)


def run_numeric(out, min_usd=1e4):
    w = Window(out)
    A = w.analysis
    if not A:
        raise SystemExit('no analysis.json in %s — run `live_scan analyze` first' % out)
    ex = exchange_set()
    R = Recompute(w, ex).run(min_usd=min_usd)

    checks = []

    def add(name, mine, theirs, tol=0.02, note=''):
        checks.append({'check': name, 'recomputed': mine, 'analysis': theirs, 'ok': close(mine, theirs, tol),
                       'tolerance': tol, 'note': note})

    win = A['window']
    add('blocks analysed', R.blocks, win['blocks'], 0.0)
    add('transactions', R.txs, win['transactions'], 0.0)
    add('logs', R.logs, win['logs'], 0.0)

    iss = A.get('issuance', {}).get('totals', {})
    add('USDC minted (USD, from the zero address)', round(R.mint['USDC']), iss.get('USDC mint', {}).get('usd'), 0.01)
    add('USDC burned (USD, to the zero address)', round(R.burn['USDC']), iss.get('USDC burn', {}).get('usd'), 0.01)

    ba = A['exchange_flow']['by_asset']
    stable = {'USDT', 'USDC', 'DAI', 'USDS', 'USDe', 'PYUSD', 'RLUSD', 'GHO', 'USDG', 'crvUSD', 'FDUSD', 'frxUSD',
              'USD1', 'AUSD', 'sUSDe', 'sUSDS'}
    mine_stable = sum(R.flow_in[s] - R.flow_out[s] for s in stable)
    theirs_stable = sum(v['net'] for k, v in ba.items() if k in stable)
    add('exchange net flow, stables (USD)', round(mine_stable), theirs_stable, 0.03)
    add('exchange net flow, ETH (USD)', round(R.flow_in['ETH'] - R.flow_out['ETH']), ba.get('ETH', {}).get('net'), 0.03)
    add('exchange gross in, USDC (USD)', round(R.flow_in['USDC']), ba.get('USDC', {}).get('in'), 0.03)

    import live_scan
    book = live_scan.load_address_book()
    lev_mine, per_op = leverage_to_exchange(R.transfers, A['lending_ops']['proceeds_followed'], ex, book)
    lev_theirs = sum(f['to_exchange_usd'] for f in A['lending_ops']['proceeds_followed'])
    add('leverage-to-exchange (USD followed to a CEX)', round(lev_mine), lev_theirs, 0.05,
        'replays the proceeds walk over an independently decoded transfer stream')

    br = {(r['token'], r['destination']): r for r in A['bridges']['out'] if r['kind'] == 'CCTP'}
    if R.cctp:
        key, val = max(R.cctp.items(), key=lambda kv: kv[1]['usd'])
        add('largest CCTP send: %s -> %s (USD)' % key, round(val['usd']), (br.get(key) or {}).get('usd'), 0.02)

    tg = A['top_gas_targets'][0] if A.get('top_gas_targets') else None
    if tg:
        add('gas requested by the top target %s' % tg['address'][:10], R.gas_to[tg['address']], tg['gas'], 0.0)
        top_mine = R.gas_to.most_common(1)[0][0]
        checks.append({'check': 'top gas target is the same address', 'recomputed': top_mine[:12],
                       'analysis': tg['address'][:12], 'ok': top_mine == tg['address'], 'tolerance': 0, 'note': ''})

    # rate dispersion: same asset, different venue, last observed borrow APR
    disp_mine = {}
    sym_of = {a: w.symbol(a) for a in {r for _, r in R.rates}}
    by_sym = collections.defaultdict(dict)
    for (venue, reserve), pts in R.rates.items():
        if pts and sym_of.get(reserve):
            by_sym[sym_of[reserve]][venue] = pts[-1][2]
    for sym, vs in by_sym.items():
        if len(vs) > 1:
            disp_mine[sym] = max(vs.values()) - min(vs.values())
    lr = collections.defaultdict(dict)
    for r in A['lending_rates']:
        lr[r['sym']][r['venue']] = r['borrow_last']
    disp_theirs = {s: max(v.values()) - min(v.values()) for s, v in lr.items() if len(v) > 1}
    if disp_mine:
        s = max(disp_mine, key=lambda k: disp_mine[k])
        add('widest Aave/Spark borrow-rate gap (%s, pp)' % s, round(disp_mine[s] * 100, 3),
            round(disp_theirs.get(s, 0) * 100, 3), 0.05)

    # label-provenance band: the same headline computed at each tier of label confidence
    band = []
    for tier in L.TIERS:
        exs = exchange_set(tier)
        if not exs:
            continue
        fin = collections.Counter()
        fout = collections.Counter()
        for x in R.transfers:
            ti, to = x['from'] in exs, x['to'] in exs
            if to and not ti:
                fin[x['sym']] += x['usd']
            elif ti and not to:
                fout[x['sym']] += x['usd']
        band.append({'min_tier': tier, 'exchange_addresses': len(exs),
                     'stables_net_usd': round(sum(fin[s] - fout[s] for s in stable)),
                     'eth_net_usd': round(fin['ETH'] - fout['ETH'])})
    return checks, band, R


# ----------------------------------------------------------------------------------------------------------------------
# Mechanism checks — a prose claim turned into a re-runnable assertion
# ----------------------------------------------------------------------------------------------------------------------
def m_stacy_deposit_for(_):
    """Claim: StacyVault's `depositFor` never writes `lastDepositBlock`, so a flash depositor skips the lock.

    This was established by reading the verified source by hand. Asserting it here means the claim is re-checked, and
    an upgrade or a re-verification that changes the function is caught instead of silently invalidating the note.
    """
    import etherscan
    s = etherscan.source(1, '0x223bc79156cbb0a6d175ea6130cb382d01868df8')
    src = s.get('source') or ''
    if not src:
        return False, 'source unavailable: %s' % s.get('error')
    m = re.search(r'function\s+depositFor\s*\(.*?\n(.*?)\n\s{4}\}', src, re.S)
    if not m:
        return False, 'depositFor not found in the verified source'
    body = m.group(1)
    sets_lock = 'lastDepositBlock' in body
    return (not sets_lock), ('depositFor %s lastDepositBlock' % ('SETS' if sets_lock else 'does not set'))


def m_msca_not_exchange(_):
    """Claim: 0xee7ae85f is a modular smart-contract account, not the exchange deposit contract it was tagged as.

    The behavioural tag came from a "many senders, never sends" profile in the day study; in the midday window it sent
    $244M. The assertion checks the implementation behind the proxy, which is the fact that settles it.
    """
    r = L.resolve_one('0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055', use_etherscan=False)
    if not r:
        return False, 'could not resolve'
    name = (r.get('name') or '')
    return ('MSCA' in name or 'Account' in name), 'implementation resolves to %r' % name


def m_registry_has_no_contract_hot_wallets(_):
    """Claim: no address counted as a CEX *hot wallet* is a contract.

    A hot wallet is an externally-owned account, so this is the invariant behind the exchange-flow number. It reads the
    audit report rather than re-fetching, so run `labels.py audit` first for a fresh answer.
    """
    p = ROOT / 'scripts' / 'labels_audit.json'
    if not p.exists():
        return False, 'no labels_audit.json — run `labels.py audit`'
    d = json.loads(p.read_text())
    c = d.get('contradictions', [])
    return (not c), ('%d contradiction(s); audit checked %d exchange tags' % (len(c), d.get('checked', 0)))


MECHANISMS = {
    'stacy-deposit-for': m_stacy_deposit_for,
    'msca-not-exchange': m_msca_not_exchange,
    'no-contract-hot-wallets': m_registry_has_no_contract_hot_wallets,
}


def run_mechanisms(out, only=None):
    rows = []
    for name, fn in MECHANISMS.items():
        if only and name not in only:
            continue
        try:
            ok, detail = fn(out)
        except Exception as e:
            ok, detail = False, 'check raised: %s' % str(e)[:120]
        rows.append({'id': name, 'ok': bool(ok), 'detail': detail,
                     'claim': (fn.__doc__ or '').strip().split('\n')[0].replace('Claim: ', '')})
    return rows


# ----------------------------------------------------------------------------------------------------------------------
def fmt(v):
    if isinstance(v, float):
        return format(round(v, 3), ',')
    if isinstance(v, int):
        return format(v, ',')
    return str(v)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--out', required=True, help='window directory with raw/ and analysis.json')
    p.add_argument('--min-usd', type=float, default=1e4)
    p.add_argument('--mechanisms', action='store_true', help='also run the source-backed mechanism assertions')
    p.add_argument('--only', nargs='*', help='run only these mechanism ids')
    a = p.parse_args()

    t0 = time.monotonic()
    checks, band, R = run_numeric(a.out, a.min_usd)
    mech = run_mechanisms(a.out, a.only) if (a.mechanisms or a.only) else []

    print('%-52s %18s %18s  %s' % ('check', 'recomputed', 'analysis', ''))
    for c in checks:
        print('%-52s %18s %18s  %s' % (c['check'][:52], fmt(c['recomputed']), fmt(c['analysis']),
                                       'ok' if c['ok'] else 'MISMATCH'))
    print('\nlabel-provenance band (the same headline at each confidence cut):')
    print('  %-20s %6s %20s %20s' % ('labels used', 'addrs', 'stables net USD', 'ETH net USD'))
    for b in band:
        print('  %-20s %6d %20s %20s' % (b['min_tier'], b['exchange_addresses'], fmt(b['stables_net_usd']), fmt(b['eth_net_usd'])))
    if mech:
        print('\nmechanism assertions:')
        for m in mech:
            print('  [%s] %-26s %s' % ('ok' if m['ok'] else 'FAIL', m['id'], m['detail']))

    n_bad = sum(1 for c in checks if not c['ok']) + sum(1 for m in mech if not m['ok'])
    res = {'window': str(a.out), 'checks': checks, 'label_band': band, 'mechanisms': mech,
           'all_ok': n_bad == 0, 'failures': n_bad, 'seconds': round(time.monotonic() - t0, 1)}
    (Path(a.out) / 'verify.json').write_text(json.dumps(res, indent=1) + '\n')
    print('\n%s — %d check(s) failed, %.1fs, wrote %s' % ('ALL OK' if n_bad == 0 else 'FAILURES', n_bad,
                                                          res['seconds'], Path(a.out) / 'verify.json'))
    sys.exit(1 if n_bad else 0)


if __name__ == '__main__':
    main()
