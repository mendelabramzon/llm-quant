"""Large same-pool round trips whose token positions close inside one transaction.

Gross settled swap volume can be real without representing fresh demand or realizable LP income. The motivating
window has three 1,000-WETH flash-funded round trips, $14.8M of turnover, and only cents of WETH left over. Keep the
gross turnover, but expose the recycling and do not treat turnover times an assumed fee as the pool's USD profit.
"""
import collections
import json

from . import Hit
from window_raw import hx, word, topic_addr, TRANSFER

NAME = 'recycled_swap_volume'
DESCRIPTION = 'large same-transaction, same-pool v2-style swaps with nearly closed token positions'
SWAP = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
MIN_VOLUME = 1e6


def closed_roundtrip(swaps, tokens, usd):
    if len(swaps) < 2 or len(tokens) != 2:
        return None
    incoming = [sum(s[i] for s in swaps) for i in (0, 1)]
    outgoing = [sum(s[i] for s in swaps) for i in (2, 3)]
    if not all(incoming) or not all(outgoing):
        return None
    # Both assets return almost completely, not merely an arbitrage route that ends in a different asset.
    closure = [abs(a-b) / max(a, b) for a, b in zip(incoming, outgoing)]
    if max(closure) > 1e-5:
        return None
    priced = [(i, usd(t, incoming[i] + outgoing[i])) for i, t in enumerate(tokens)]
    priced = [(i, v) for i, v in priced if v is not None]
    if not priced:
        return None
    i, gross = max(priced, key=lambda pair: pair[1])
    if gross < MIN_VOLUME:
        return None
    return {'gross_priced_leg_usd': gross, 'priced_token': tokens[i],
            'pool_net_priced_token_raw': str(incoming[i] - outgoing[i]),
            'pool_net_priced_token_usd': usd(tokens[i], incoming[i] - outgoing[i]),
            'closure_fractions': closure, 'incoming': incoming, 'outgoing': outgoing}


def scan(ctx):
    p = ctx.out / 'pools.json'
    pools = json.loads(p.read_text()) if p.exists() else {}
    found = collections.defaultdict(list)
    for block, logs in ctx.window.blocks():
        by = collections.defaultdict(list)
        transfers = collections.defaultdict(lambda: [0, 0])
        for log in logs:
            topics = log.get('topics') or []
            if not topics:
                continue
            tx, addr = log['transactionHash'], log['address'].lower()
            if topics[0] == SWAP and len(log['data']) >= 258:
                by[(tx, addr)].append([word(log['data'], i) for i in range(4)])
            elif topics[0] == TRANSFER and len(topics) == 3 and len(log['data']) >= 66:
                amount = word(log['data'], 0)
                transfers[(tx, topic_addr(topics[2]), addr)][0] += amount
                transfers[(tx, topic_addr(topics[1]), addr)][1] += amount
        senders = {t['hash']: t['from'].lower() for t in block['transactions']}
        for (tx, pool), swaps in by.items():
            tokens = pools.get(pool, {}).get('tokens') or []
            hit = closed_roundtrip(swaps, tokens, ctx.window.usd)
            if not hit:
                continue
            i = tokens.index(hit['priced_token'])
            # Require actual priced token transfers, not just an arbitrary contract emitting a Swap-shaped event.
            settled = transfers[(tx, pool, tokens[i])]
            if settled != [hit['incoming'][i], hit['outgoing'][i]]:
                continue
            del hit['incoming'], hit['outgoing']
            found[pool].append({'tx': tx, 'block': hx(block['number']), 'sender': senders[tx], **hit})
    hits = []
    for pool, rows in found.items():
        gross = sum(r['gross_priced_leg_usd'] for r in rows)
        hits.append(Hit(detector=NAME, key=pool, severity='notable', usd=gross,
                        title='$%s of settled turnover in %d same-pool atomic round trips; token positions almost close' %
                              (format(round(gross), ','), len(rows)),
                        evidence={'pool': pool, 'roundtrips': len(rows), 'gross_priced_leg_usd': gross,
                                  'pool_net_priced_token_usd': sum(r['pool_net_priced_token_usd'] for r in rows),
                                  'examples': rows[:10],
                                  'note': 'Gross turnover is preserved. Net here is only the pool’s priced token delta; '
                                          'it excludes gas and other assets. A fee-rate times gross turnover estimate '
                                          'does not measure realizable LP profit through these price round trips.'}))
    return hits
