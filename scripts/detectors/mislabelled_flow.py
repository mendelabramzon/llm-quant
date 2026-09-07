#!/usr/bin/env python3
"""Addresses whose behaviour in this window contradicts the label the analysis is counting them under.

The finding this makes permanent. Exchange flow and leverage-to-exchange are computed from an address book, and a wrong
entry moves those headlines by multiples rather than percents. Three have been caught by hand so far: the CoW settlement
contract read as a CEX, an RLUSD treasury read as a CEX, and a "deposit sink" rule that matched every busy contract
because it tested `sent == 0`, which a contract satisfies structurally.

Rather than trusting that the registry is now correct, this detector tests the labels against the window itself, every
window. Three contradictions, in descending strength:

  * a **deposit sink that sends** — a sink is defined by not forwarding, so material outflow refutes the label;
  * a **hot wallet that only receives** — a hot wallet pays withdrawals out, so a pure receiver is a deposit address
    or a treasury, and counting it as a hot wallet puts its inflow on the wrong side of net flow;
  * a **counterparty-concentrated exchange** — a hot wallet serving one counterparty is plumbing, not a venue.

The point is not that these are always wrong. It is that each is a claim the data can argue with, and an argument that
runs automatically is worth more than one that ran once.
"""
import collections

from . import Hit

NAME = 'mislabelled_flow'
DESCRIPTION = 'address labels the window contradicts, which is how a headline moves by a multiple'
SEVERITY = 'high'

MIN_OUT_USD = 1e6          # outflow above which "deposit sink" is refuted
MIN_IN_USD = 5e6           # inflow above which a never-sending "hot wallet" is worth flagging
CONCENTRATION = 0.9        # share of flow through a single counterparty that makes a venue look like plumbing


def scan(ctx):
    flow = collections.defaultdict(lambda: {'in': 0.0, 'out': 0.0})
    peers = collections.defaultdict(collections.Counter)
    for x in ctx.transfers:
        flow[x['to']]['in'] += x['usd']
        flow[x['from']]['out'] += x['usd']
        peers[x['to']][x['from']] += x['usd']
        peers[x['from']][x['to']] += x['usd']

    hits = []
    for a, entry in ctx.book.items():
        kind = entry.get('kind')
        if kind not in ('exchange', 'exchange_deposit'):
            continue
        f = flow.get(a)
        if not f or (f['in'] + f['out']) <= 0:
            continue
        src = entry.get('source', 'unknown')
        # Behavioural labels read "deposit sink (behaviour, day study)", so a title built as "deposit sink %s" says it
        # twice. Where the label is only a restatement of the tag, the address is the more informative name.
        label = entry.get('label', a)
        if label.startswith(('deposit sink', 'hot wallet')):
            label = '%s (%s)' % (a, src)

        if kind == 'exchange_deposit' and f['out'] >= max(MIN_OUT_USD, 0.25 * f['in']):
            hits.append(Hit(
                detector=NAME, severity='high', usd=f['out'], key='%s:forwards' % a,
                title='deposit sink %s forwarded $%s in this window' % (label[:48], _m(f['out'])),
                evidence={'address': a, 'label': label, 'source': src, 'in_usd': round(f['in']),
                          'out_usd': round(f['out']),
                          'why': 'a deposit sink is defined by not forwarding; this one forwards, so its outflow is '
                                 'being counted as exchange outflow'}))

        if kind == 'exchange' and f['in'] >= MIN_IN_USD and f['out'] == 0:
            hits.append(Hit(
                detector=NAME, severity='notable', usd=f['in'], key='%s:receives-only' % a,
                title='hot wallet %s only received ($%s in, nothing out)' % (label[:48], _m(f['in'])),
                evidence={'address': a, 'label': label, 'source': src, 'in_usd': round(f['in']),
                          'why': 'a hot wallet pays withdrawals out; a pure receiver is a deposit address or a '
                                 'treasury, which puts this inflow on the wrong side of net flow'}))

        tot = f['in'] + f['out']
        if kind == 'exchange' and tot >= MIN_IN_USD:
            top, top_usd = (peers[a].most_common(1) or [(None, 0)])[0]
            if top and top_usd >= CONCENTRATION * tot:
                hits.append(Hit(
                    detector=NAME, severity='info', usd=tot, key='%s:one-counterparty' % a,
                    title='exchange %s moved %.0f%% of its flow with one counterparty' % (label[:44], 100 * top_usd / tot),
                    evidence={'address': a, 'label': label, 'source': src, 'counterparty': top,
                              'counterparty_label': ctx.label(top), 'share': round(top_usd / tot, 3),
                              'why': 'a venue serving one counterparty is plumbing between related accounts, not '
                                     'exchange flow'}))
    return hits


def _m(v):
    return format(round(v / 1e6, 1), ',') + 'M' if v >= 1e6 else format(round(v), ',')
