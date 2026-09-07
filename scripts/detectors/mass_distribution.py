#!/usr/bin/env python3
"""One sender, thousands of recipients: airdrops, mint distributions and dust spam, and the campaign behind them.

The finding this makes permanent. The 2026-09-07 five-hour window contained twenty transactions carrying about two
thousand `Transfer` events each — the log-heaviest transactions of the window — and identifying them took a token-
centric one-off (`window_followups`: tokens with at least a thousand transfers, half of them from the zero address).
That code cannot fire on a different token or a different sender, and the shape it looked for is common enough to be
worth a standing check on three separate grounds.

  * A distribution is the setup for a sell wave. Thousands of funded wallets holding the same token is what a later
    coordinated dump looks like before it happens, and the Solana study found exactly that pattern after the fact.
  * It explains log and gas anomalies. A window whose log count jumps without a matching value story usually has one
    of these in it, and attributing the jump beats puzzling over it.
  * At the small end the same shape is dust spam. A fraction of a cent sent to ten thousand wallets is the token
    flavour of address poisoning — `address_poisoning` here only watches native-ETH dust, and this window's largest
    campaign by recipient count was 0.0003 USDT to 9,428 addresses, which that detector cannot see. It also pollutes
    holder counts and every "distinct recipient" metric the rest of the system computes.

Deliberately independent of the priced transfer stream: an airdropped token is almost never in the price table, and a
detector that only sees priced legs would miss every campaign that matters. It decodes `Transfer` topics directly.
"""
import collections

from . import Hit
from window_raw import TRANSFER, hx, word, topic_addr

NAME = 'mass_distribution'
DESCRIPTION = 'one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam'
SEVERITY = 'info'

ZERO = '0x' + '0' * 40
MIN_RECIPIENTS = 500     # below this it is a payout run, not a campaign
MIN_BATCHING = 20        # transfers per transaction; a campaign is batched, ordinary traffic is not
TOP = 8


def scan(ctx):
    pairs = collections.defaultdict(lambda: {'n': 0, 'recips': set(), 'txs': set(), 'blocks': set(),
                                             'carriers': collections.Counter(), 'amounts': []})
    for b, logs in ctx.window.blocks():
        n = hx(b['number'])
        to_of = {t['hash']: (t.get('to') or '').lower() for t in b['transactions']}
        for l in logs:
            tp = l['topics']
            if not tp or tp[0] != TRANSFER or len(tp) != 3 or len(l['data']) < 66:
                continue
            frm, to = topic_addr(tp[1]), topic_addr(tp[2])
            k = (l['address'].lower(), frm)
            d = pairs[k]
            d['n'] += 1
            d['recips'].add(to)
            d['txs'].add(l['transactionHash'])
            d['blocks'].add(n)
            d['carriers'][to_of.get(l['transactionHash'], '?')] += 1
            if len(d['amounts']) < 400:
                d['amounts'].append(word(l['data'], 0))

    rows = []
    for (token, sender), d in pairs.items():
        recips = len(d['recips'])
        if recips < MIN_RECIPIENTS:
            continue
        batching = d['n'] / max(len(d['txs']), 1)
        if batching < MIN_BATCHING:
            continue
        amts = sorted(d['amounts'])
        med = amts[len(amts) // 2] if amts else 0
        uniform = sum(1 for a in amts if a == med) / len(amts) if amts else 0.0
        carrier, carrier_n = (d['carriers'].most_common(1) or [(None, 0)])[0]
        usd_med = ctx.window.usd(token, med)
        # Dust is a value judgement, so make it in dollars wherever the token is priced. A raw-units test called a
        # 9,428-recipient run of 0.0003 USDT an airdrop, when a fraction of a cent to ten thousand wallets is the
        # token-transfer form of address poisoning: the victim later copies the sender out of their token history.
        kind = ('mint distribution' if sender == ZERO else
                'dust spam' if (usd_med is not None and usd_med < 0.01) or (uniform >= 0.9 and med <= 1) else
                'airdrop or multisend')
        rows.append({'token': token, 'token_symbol': ctx.window.symbol(token), 'sender': sender,
                     'sender_label': ctx.label(sender), 'kind': kind, 'transfers': d['n'], 'recipients': recips,
                     'txs': len(d['txs']), 'blocks': len(d['blocks']), 'transfers_per_tx': round(batching, 1),
                     'carrier_contract': carrier, 'carrier_label': ctx.label(carrier),
                     'carrier_share': round(carrier_n / d['n'], 3),
                     'median_raw_amount': str(med), 'uniform_amount_share': round(uniform, 3),
                     'usd_median': usd_med})
    if not rows:
        return []
    rows.sort(key=lambda r: -r['recipients'])
    return [Hit(detector=NAME, key='%s:%s' % (r['token'], r['sender']), usd=None,
                severity='notable' if r['recipients'] >= 2000 else 'info',
                title='%s: %s sent %s to %s recipients in %d txs (%.0f per tx)'
                      % (r['kind'], (r['sender_label'] or r['sender'])[:32],
                         r['token_symbol'] or r['token'][:10], format(r['recipients'], ','), r['txs'],
                         r['transfers_per_tx']),
                evidence=dict(r, why='a batched fan-out to this many wallets is a campaign; it explains log-count '
                                     'and gas anomalies, and a funded holder set is what a later coordinated sell '
                                     'looks like beforehand'))
            for r in rows[:TOP]]
