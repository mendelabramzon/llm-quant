#!/usr/bin/env python3
"""Address-poisoning: a dust transfer from a lookalike address, sent minutes after a large transfer, to be copied later.

The finding this makes permanent. Poisoning bots watch for a large plain-value transfer, then send a near-zero transfer
from an address whose first or last characters match one of the two parties, hoping the victim later copies the attacker
address out of their transaction history. It was matched by hand on the 2026-09-07 five-hour window with the addresses
and thresholds written into the script.

The generalised check keeps the shape and drops the specifics: index every large plain transfer, then look for dust
transfers in the following hour whose sender resembles one of that transfer's parties without being it. Resemblance is
the same prefix or suffix a wallet interface shows when it truncates an address, which is exactly the thing the attack
exploits.

Dust rather than strictly zero: the observed bots send around a millionth of an ether, not nothing, because a zero-value
transfer is easier for a wallet to hide.
"""
import collections

from . import Hit
from window_raw import hx

NAME = 'address_poisoning'
DESCRIPTION = 'lookalike dust transfers that follow a large transfer, aimed at a later copy-paste'
SEVERITY = 'info'

BIG_ETH = 100.0          # a transfer this size is worth poisoning
DUST_ETH = 0.001         # observed bots send ~1e-6 ETH, not zero
WINDOW_S = 3600
PREFIX = 6               # characters a truncated address shows on each side
SUFFIX = 4


def scan(ctx):
    big, dust = [], []
    for b, _ in ctx.window.blocks():
        ts = hx(b['timestamp'])
        for t in b['transactions']:
            to = (t.get('to') or '').lower()
            if not to or t.get('input', '0x') != '0x':
                continue
            v = hx(t.get('value', 0)) / 1e18
            if v >= BIG_ETH:
                big.append({'ts': ts, 'tx': t['hash'], 'from': t['from'].lower(), 'to': to, 'eth': v})
            elif 0 <= v <= DUST_ETH:
                dust.append({'ts': ts, 'tx': t['hash'], 'from': t['from'].lower(), 'to': to, 'eth': v})
    if not big or not dust:
        return []

    by_target = collections.defaultdict(list)
    for d in dust:
        by_target[d['to']].append(d)

    matches, attackers = [], collections.Counter()
    for bt in big:
        for victim, other in ((bt['from'], bt['to']), (bt['to'], bt['from'])):
            for d in by_target.get(victim, []):
                if not (0 <= d['ts'] - bt['ts'] <= WINDOW_S) or d['from'] == other:
                    continue
                if _lookalike(d['from'], other):
                    attackers[d['from']] += 1
                    matches.append({'big_tx': bt['tx'], 'big_eth': round(bt['eth'], 2), 'victim': victim,
                                    'impersonated': other, 'attacker': d['from'], 'dust_tx': d['tx'],
                                    'seconds_after': d['ts'] - bt['ts']})
    if not matches:
        return []
    top = attackers.most_common(6)
    # Identity is the *condition*, not the sender. Every lookalike address is disposable — generated to resemble one
    # target and abandoned — so keying on the busiest sender would file each window's campaign as a brand-new finding
    # and the ledger would never show poisoning as the standing background hazard it is. The senders live in evidence.
    return [Hit(detector=NAME, severity='info', usd=None, key='campaign',
                title='%d poisoning attempt(s) from %d lookalike sender(s) after large transfers'
                      % (len(matches), len(attackers)),
                evidence={'matches': matches[:12], 'top_senders': top,
                          'rule': 'dust <= %g ETH within %ds of a >= %g ETH plain transfer, from an address sharing '
                                  'the first %d or last %d hex characters of the counterparty'
                                  % (DUST_ETH, WINDOW_S, BIG_ETH, PREFIX, SUFFIX)})]


def _lookalike(a, b):
    """True when a wallet's truncated rendering of `a` could be mistaken for `b`."""
    if a == b:
        return False
    return a[2:2 + PREFIX] == b[2:2 + PREFIX] or a[-SUFFIX:] == b[-SUFFIX:]
