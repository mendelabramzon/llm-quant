#!/usr/bin/env python3
"""Unlabelled contracts that move size without holding it: the solver, router and MEV-bot tail.

The finding this makes permanent. Roughly 30% of the USD that moves through a window's large transfers touches an
address the registry cannot name — around $17B of endpoint flow in the 2026-09-07 midday window, with a $2.07B
contract at the top of the list. Every hand-labelling pass so far picked addresses off that list one at a time, and
the list is regenerated every window with different addresses on it. Naming them individually does not scale, and
leaving them unnamed is how a settlement contract gets counted as an exchange.

The way out is to stop asking *who* an address is and ask *what shape* it has, because the shapes that matter are
few and they are visible in the window itself:

  * **a contract**, proven by emitting a log or by being called with calldata while never originating a transaction —
    never inferred from "sends no transactions", the inference that made every busy contract a deposit sink. Some
    addresses appear only as transfer counterparties inside other contracts' calls, and for those the window holds no
    evidence either way; they are reported as unknown rather than guessed;
  * **pass-through**, meaning value that arrives in a transaction leaves in the same transaction. A solver, router or
    arbitrage bot ends each transaction flat; an exchange wallet, a treasury and a vault do not. This is the load-
    bearing signal and it is nearly impossible to fake, because holding is the whole difference;
  * **fan**, how many distinct counterparties and tokens it touches. This is a classifier, not a gate — the first
    version of this detector required five counterparties and thereby dropped the three largest entries in the tail,
    each a two-party pipe moving a billion dollars in a loop. Wide fan is a venue; a fan of one is a bot and its
    partner, which is the more interesting of the two;
  * **a vanity prefix** of leading zero bytes, which is a searcher paying to mine an address whose calldata is cheaper.
    Strong evidence when present, absent from plenty of real solvers, so it raises confidence rather than gating.

An address with the first three is a venue or a bot and its flow must not be counted as exchange flow; with the fourth
it is a searcher. The tail's other half is just as important and is reported alongside: an unlabelled address moving
comparable size that *does* retain what it receives is a wallet, a treasury or a vault, and that is the class where a
wrong guess moves a headline — both label bugs this project has hit were of exactly that kind. Separating the two is
the whole job here, because the same $200M of flow means opposite things depending on which it is.

Neither claim is an identity, so nothing here writes the registry — it produces the queue that `labels.py resolve`
then tries to name, ranked by how much a mislabel would cost.
"""
import collections

from . import Hit

NAME = 'solver_fingerprint'
DESCRIPTION = 'unlabelled contracts that pass value straight through: solvers, routers and searcher bots'
SEVERITY = 'notable'

MIN_USD = 25e6           # gross flow below which a mislabel cannot move a headline
MIN_TXS = 3              # enough transactions for the share to mean something; three $500M round trips is a shape,
                         # and the tail's third-largest entry has exactly four
PASS_TOL = 0.02          # |in - out| / max(in, out) inside one transaction, below which the address ended flat
MIN_PASS_SHARE = 0.6     # share of its transactions that end flat
WIDE_FAN = 5             # counterparties above which a pass-through address is a venue rather than a bot's partner
CYCLE_TOL = 0.02         # |retained| / received below which an address ends the *window* flat, if not each transaction
RETAIN_USD = 100e6       # an unlabelled address holding this much of what it received is the mislabel risk
TOP = 12


def scan(ctx):
    emitters, senders, called = ctx.accounts
    per_tx = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0]))   # addr -> tx -> [in, out]
    peers = collections.defaultdict(set)
    tokens = collections.defaultdict(set)
    gross = collections.Counter()
    for x in ctx.transfers:
        f, t, u = x['from'], x['to'], x['usd']
        per_tx[t][x['tx']][0] += u
        per_tx[f][x['tx']][1] += u
        peers[t].add(f)
        peers[f].add(t)
        tokens[t].add(x['sym'] or x['token'])
        tokens[f].add(x['sym'] or x['token'])
        gross[t] += u
        gross[f] += u

    rows = []
    for a, g in gross.most_common(600):
        if g < MIN_USD or a in ctx.book or a == '0x' + '0' * 40:
            continue
        legs = per_tx[a]
        if len(legs) < MIN_TXS:
            continue
        flat = sum(1 for i, o in legs.values() if max(i, o) > 0 and abs(i - o) <= PASS_TOL * max(i, o))
        share = flat / len(legs)
        tin = sum(i for i, _ in legs.values())
        tout = sum(o for _, o in legs.values())
        held = tin - tout
        zeros = _leading_zeros(a)
        # A log proves code. So does calldata sent to an address that never originates a transaction of its own —
        # necessary because a searcher bot commonly emits no events at all, and `emitters` alone would file it as an
        # externally-owned account, which is the class whose flow gets counted as an exchange.
        emits, calls, sends = a in emitters, a in called, a in senders
        # True, False, or None for "the window contains no evidence". The third case is common — an address that only
        # ever appears as a transfer counterparty inside someone else's call leaves no trace of its own — and guessing
        # it is how a bot contract gets filed as a wallet.
        is_contract = True if (emits or (calls and not sends)) else (False if (sends and not emits) else None)
        wide = len(peers[a]) >= WIDE_FAN
        if share >= MIN_PASS_SHARE:
            # Flat inside each transaction: nothing is ever held, not even between blocks.
            shape = 'pass-through'
            kind = (('venue' if wide else 'atomic bot pair') if is_contract
                    else ('eoa' if is_contract is False else 'unknown'))
            if zeros >= 4:
                kind = 'mev_bot'
        elif abs(held) <= CYCLE_TOL * max(tin, 1):
            # Flat over the window but not inside a transaction: a position opened and closed across blocks. The
            # window's largest atomic bot has this shape, and a per-transaction test alone misses it entirely.
            shape = 'cycles'
            kind = ('mev_bot' if zeros >= 4 else
                    ('bot' if is_contract else ('eoa' if is_contract is False else 'unknown')))
        elif held >= RETAIN_USD:
            shape = 'retains'
            kind = ('vault/treasury' if is_contract
                    else ('wallet' if is_contract is False else 'wallet or vault (unknown)'))
        else:
            continue
        rows.append({'address': a, 'shape': shape, 'gross_usd': round(g), 'txs': len(legs),
                     'counterparties': len(peers[a]), 'tokens': len(tokens[a]),
                     'pass_through_share': round(share, 3), 'received_usd': round(tin), 'sent_usd': round(tout),
                     'retained_usd': round(held), 'retention': round(held / max(tin, 1), 4),
                     'is_contract': is_contract, 'emits_logs': emits, 'receives_calldata': calls,
                     'originates_txs': sends, 'vanity_zeros': zeros, 'suggested_kind': kind})
    if not rows:
        return []
    rows.sort(key=lambda r: -r['gross_usd'])

    hits = []
    for r in rows[:TOP]:
        if r['shape'] == 'pass-through':
            title = ('unlabelled %s %s passed $%s through in %d txs (%.0f%% ended flat, %d counterparties)'
                     % (r['suggested_kind'], r['address'][:10], _m(r['gross_usd']), r['txs'],
                        100 * r['pass_through_share'], r['counterparties']))
            why = ('value arrives and leaves inside the same transaction, so this address holds nothing and its flow '
                   'is not exchange flow; %s'
                   % ('a %d-nibble zero prefix is a searcher-mined address' % r['vanity_zeros']
                      if r['vanity_zeros'] >= 4 else 'no vanity prefix, so the shape is the only claim'))
        elif r['shape'] == 'cycles':
            title = ('unlabelled %s %s cycled $%s and ended the window flat (%d txs, %d counterparties)'
                     % (r['suggested_kind'], r['address'][:10], _m(r['received_usd']), r['txs'],
                        r['counterparties']))
            why = ('it received and returned the same total across separate transactions, so it holds nothing over '
                   'the window even though no single transaction nets out: a position opened and closed across blocks')
        else:
            title = ('unlabelled %s %s kept $%s of $%s received across %d txs'
                     % (r['suggested_kind'], r['address'][:10], _m(r['retained_usd']), _m(r['received_usd']),
                        r['txs']))
            why = ('this address retains what it receives, so it is a wallet, treasury or vault — the class where a '
                   'wrong label moves a headline, since its inflow would count as exchange inflow')
        hits.append(Hit(
            detector=NAME, key=r['address'], usd=r['gross_usd'],
            severity='notable' if r['gross_usd'] >= 100e6 else 'info',
            title=title,
            evidence=dict(r, why=why,
                          next_step='labels.py resolve --out <window> tries to name it; unnamed, it still must not '
                                    'be counted as an exchange')))
    return hits


def _leading_zeros(a):
    s = a[2:]
    n = 0
    while n < len(s) and s[n] == '0':
        n += 1
    return n


def _m(v):
    for unit, scale in (('B', 1e9), ('M', 1e6), ('k', 1e3)):
        if v >= scale:
            return format(round(v / scale, 1), ',') + unit
    return format(round(v), ',')
