#!/usr/bin/env python3
"""Address poisoning executed through EIP-7702 batches: dust from lookalike senders that no log-reader can see.

The finding this makes permanent. On the 2026-09-08 ten-hour window one relayer sent 2,258 transactions — roughly one
per block for the whole window — each carrying EIP-7702 authorizations for accounts it controls and a single
`executeBatch((address,uint256,bytes)[])` call. Inside those 2,258 transactions were 335,601 dust legs sprayed at 16,258
real wallets, and 30% of them came from a sender whose first four and last four hex characters match an address the
recipient had genuinely transacted with. The shuffled control is 0.03%, so the resemblance is the product, not chance.

Why the existing `address_poisoning` detector cannot see it. That one reads top-level transactions: a plain-value
transfer from a lookalike, following a large transfer. Here every leg is an *internal* call inside a batch, so there is
no transaction to read; the ERC-20 legs do emit `Transfer` logs, but they are spread over ~9,000 distinct delegated
sender accounts, no one of which crosses any mass-distribution threshold. The campaign is fragmented across senders
precisely so that per-sender counting finds nothing — and the fragmentation is affordable because EIP-7702 lets one
relayer pay gas for all of them.

So this detector reads the calldata instead. It decodes the batch structure from the transaction input, attributes each
leg to the delegated account that executes it, and asks the one question that separates dusting from paying someone:
does the sender look like a counterparty of the recipient? Resemblance is measured against the window's own transaction
and Transfer graph, so the answer is derived from the same blocks and needs no external history.

`executeBatch((address,uint256,bytes)[])` is the shape ERC-4337 and every 7702 batching wallet uses, so this reads the
whole family, not one operator's contract.
"""
import collections

from . import Hit
from window_raw import hx

NAME = 'delegated_dust'
DESCRIPTION = 'mass dust fan-out inside EIP-7702 / executeBatch calldata, from senders that mimic the recipient\'s counterparties'
SEVERITY = 'notable'

EXECUTE_BATCH = '0x34fcd5be'          # executeBatch((address,uint256,bytes)[])
TRANSFER_SEL = 'a9059cbb'
TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
MIN_LEGS = 500                        # a batching wallet does a few; a campaign does thousands
PREFIX = 4                            # what a truncated address shows, and what a victim copies
SUFFIX = 4
DUST_WEI = 10 ** 15                   # 0.001 ETH: above this it is a payment, not a lure


def _words(d):
    return [int(d[i * 64:(i + 1) * 64], 16) for i in range(len(d) // 64)]


def _batch(data):
    """Decode `executeBatch((address,uint256,bytes)[])` arguments. Malformed calldata yields nothing, never an error."""
    try:
        w = _words(data)
        off = w[0] // 32
        n = w[off]
        if n > 4096:
            return []
        out = []
        for k in range(n):
            e = off + 1 + w[off + 1 + k] // 32
            do = e + w[e + 2] // 32
            out.append(('0x%040x' % w[e], w[e + 1], data[(do + 1) * 64:(do + 1) * 64 + w[do] * 2]))
        return out
    except Exception:
        return []


def _legs(inp):
    """Every (executing account, recipient, wei, token) leg reachable from one transaction's calldata.

    Batches nest: the operator's outer batch calls delegated accounts, each of which runs its own inner batch. The
    executing account of an inner leg is the outer entry's target, which is the account whose delegation makes the call
    possible — and the address the victim will see as the sender.
    """
    out = []
    if not inp.startswith(EXECUTE_BATCH):
        return out
    for target, value, data in _batch(inp[10:]):
        if data[:8] == EXECUTE_BATCH[2:]:
            for t2, v2, d2 in _batch(data[8:]):
                if d2[:8] == TRANSFER_SEL and len(d2) >= 136:
                    out.append((target, '0x' + d2[8 + 24:8 + 64], 0, t2))
                elif not d2:
                    out.append((target, t2, v2, None))
        elif not data:
            out.append((inp, target, value, None))
    return out


def _looks_like(a, b):
    return a != b and a[2:2 + PREFIX] == b[2:2 + PREFIX] and a[-SUFFIX:] == b[-SUFFIX:]


def scan(ctx):
    legs = []
    counterparties = collections.defaultdict(set)
    for b, logs in ctx.window.blocks():
        ts = hx(b['timestamp'])
        for t in b['transactions']:
            to = (t.get('to') or '').lower()
            if to:
                counterparties[t['from'].lower()].add(to)
                counterparties[to].add(t['from'].lower())
            inp = t.get('input') or '0x'
            if len(inp) > 10 and inp.startswith(EXECUTE_BATCH):
                for sender, recip, wei, token in _legs(inp):
                    if wei <= DUST_WEI:
                        legs.append((t['from'].lower(), sender, recip, wei, token, t['hash'], ts))
        for l in logs:
            tp = l.get('topics') or []
            if tp and tp[0] == TRANSFER_TOPIC and len(tp) == 3:
                a, c = '0x' + tp[1][-40:], '0x' + tp[2][-40:]
                counterparties[a].add(c)
                counterparties[c].add(a)

    by_operator = collections.defaultdict(list)
    for op, sender, recip, wei, token, txh, ts in legs:
        by_operator[op].append((sender, recip, wei, token, txh, ts))

    hits = []
    for op, rows in sorted(by_operator.items(), key=lambda kv: -len(kv[1])):
        if len(rows) < MIN_LEGS:
            continue
        senders = {r[0] for r in rows}
        recips = {r[1] for r in rows}
        tokens = collections.Counter(r[3] for r in rows if r[3])
        tested = mimic = 0
        examples = []
        for sender, recip, wei, token, txh, ts in rows:
            cs = counterparties.get(recip)
            if not cs:
                continue
            tested += 1
            for c in cs:
                if c != sender and _looks_like(sender, c):
                    mimic += 1
                    if len(examples) < 4:
                        examples.append({'victim': recip, 'dust_from': sender, 'mimics': c, 'tx': txh})
                    break
        rate = mimic / tested if tested else 0.0
        hits.append(Hit(
            detector=NAME,
            title='%s sprayed %s dust legs from %s delegated accounts at %s wallets; %.1f%% of testable legs came from a lookalike of the recipient\'s own counterparty' % (
                ctx.label(op) or op[:10] + '…', format(len(rows), ','), format(len(senders), ','),
                format(len(recips), ','), 100 * rate),
            severity='high' if rate >= 0.05 and len(rows) >= 10_000 else SEVERITY,
            key=op,
            evidence={
                'operator': op, 'operator_label': ctx.label(op),
                'dust_legs': len(rows), 'executing_accounts': len(senders), 'recipients': len(recips),
                'legs_with_a_testable_recipient': tested, 'legs_from_a_lookalike_counterparty': mimic,
                'lookalike_rate': round(rate, 4),
                'tokens': {(ctx.label(k) or k): v for k, v in tokens.most_common(5)},
                'native_legs': sum(1 for r in rows if r[3] is None),
                'total_wei_moved': sum(r[2] for r in rows),
                'examples': examples,
                'note': 'lookalike = first %d and last %d hex characters shared with an address the recipient '
                        'transacted with inside this window; a victim copying from a truncated history sees the same '
                        'string. The rate is a floor: only in-window counterparties can be tested.' % (PREFIX, SUFFIX),
            }))
    return hits
