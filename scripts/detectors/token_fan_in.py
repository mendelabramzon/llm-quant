"""Many wallets converging on one token recipient: exchange sweeps and coordinated consolidations.

Counts settled ERC-20 Transfer events without a USD threshold. Small individual transfers can dominate transaction
activity while remaining invisible to a large-dollar flow scan. This is a shape claim, not proof of common ownership.
"""
import collections
import json

from . import Hit
from window_raw import TRANSFER, topic_addr, word, hx

NAME = 'token_fan_in'
DESCRIPTION = 'settled token transfers from thousands of senders concentrated at one recipient'
MIN_SENDERS = 2000
MIN_TOKEN_SHARE = .6
ZERO = '0x' + '0'*40


def scan(ctx):
    rows = {}
    token_counts = collections.Counter()
    for b, logs in ctx.window.blocks():
        for l in logs:
            t = l.get('topics') or []
            if len(t) != 3 or t[0] != TRANSFER or len(l.get('data','')) != 66:
                continue
            sender, recipient = topic_addr(t[1]), topic_addr(t[2])
            amount = word(l['data'],0)
            if not amount or sender == recipient or sender == ZERO or recipient == ZERO:
                continue
            token = l['address'].lower()
            token_counts[token] += 1
            key = (token,recipient)
            row = rows.setdefault(key,{'count':0,'senders':set(),'raw':0,'first':hx(b['timestamp']),
                                      'last':hx(b['timestamp']),'buckets':collections.Counter(),'examples':[]})
            row['count'] += 1; row['senders'].add(sender); row['raw'] += amount
            row['last'] = hx(b['timestamp'])
            row['buckets'][hx(b['timestamp'])//900*900] += 1
            if len(row['examples']) < 3:
                row['examples'].append({'tx':l['transactionHash'],'block':hx(b['number']),'sender':sender,
                                        'raw':str(amount)})
    head = ctx.out/'head_state.json'
    metadata = json.loads(head.read_text()).get('tokens',{}) if head.exists() else {}
    hits = []
    for (token,recipient),row in rows.items():
        share = row['count']/token_counts[token]
        if len(row['senders']) < MIN_SENDERS or share < MIN_TOKEN_SHARE:
            continue
        symbol = ctx.window.symbol(token) or metadata.get(token,{}).get('symbol') or token[:12]
        dec = ctx.window.tokens.get(token, ('',None))[1] if token in ctx.window.tokens else metadata.get(token,{}).get('decimals')
        hits.append(Hit(detector=NAME, key=token+':'+recipient, severity='notable',
                        title='%s: %s settled transfers from %s senders converge on %s (%.1f%% of token transfers)' %
                              (symbol,format(row['count'],','),format(len(row['senders']),','),
                               ctx.label(recipient) or recipient[:12],100*share),
                        evidence={'token':token,'symbol':symbol,'recipient':recipient,'recipient_label':ctx.label(recipient),
                                  'transfers':row['count'],'unique_senders':len(row['senders']),
                                  'token_transfer_share':share,'total_raw':str(row['raw']),
                                  'total_units':row['raw']/10**dec if dec is not None else None,
                                  'first_timestamp':row['first'],'last_timestamp':row['last'],
                                  'buckets':dict(sorted(row['buckets'].items())),'examples':row['examples'],
                                  'note':'Settled positive non-mint/burn Transfer logs. Shared ownership, gas funders '
                                         'and deposit-versus-internal-sweep interpretation require follow-up.'}))
    return hits
