#!/usr/bin/env python3
"""Tokens you can buy and cannot sell: the on-chain signature of a honeypot, from a window's own blocks and logs.

A honeypot is a token whose contract lets a victim buy and then blocks, taxes or reverts their sale. The families are
few and they all reduce to the same observable outcome:

  * **a sell gate** — `transfer`/`transferFrom` reverts unless the sender is whitelisted, the pool, or the deployer;
  * **a blacklist** — buyers are added to a deny list, often only after they buy, so the trap arms behind them;
  * **a confiscatory tax** — the sale succeeds and returns a few percent of its value, which is a honeypot in economics
    if not in mechanism;
  * **a trading switch** — `tradingEnabled` is flipped off, or `maxTxAmount` set below any realistic sale;
  * **a rug rather than a trap** — liquidity is pulled, so the sale reverts for lack of a counterparty.

Detecting this by reading the contract is the usual approach and it is an arms race: the source is often unverified,
the gate is often disguised as a slippage or bot check, and a proxy can add one after listing. The window itself is
harder to fake, because it records what actually happened to real buyers.

**Three signals, and none of them is sufficient alone — which is the whole design.**

`buyers_without_sellers` is the shape everyone reaches for first, and on its own it is close to useless: a token
launched an hour ago has forty buyers and two sellers because nobody has tried to sell yet, not because they cannot.
This window has dozens of such tokens at a 20:2 ratio and they are ordinary launches.

`failed_sell_rate` is the discriminator, and its denominator is the sales that were *attempted* — the ones that
succeeded plus the ones that reverted. A router call that bought the token is neither, and counting it as one buries
the finding: twenty buys against twelve blocked sales reads as 37% rather than 100%. A transaction sent to a swap router that emitted **no logs at all** either
reverted or did nothing, and reverts are what a sell gate produces. Receipts are not collected and are not needed: a
reverted transaction leaves a transaction with no logs. Roughly 4% of router-targeted transactions in a normal window
emit no logs, so the base rate is known and a token far above it is the finding.

Attributing a failure to a token is the delicate part. Naming it in the calldata is not enough — an aggregator's
calldata carries many addresses, so one unrelated revert gets charged to all of them, and that alone put Centrifuge's
CFG at a 70% "failure rate" and Nym's NYM at 100%. The rule that fixes it is that **a failed sale must come from
someone who bought.** Only a sender the window has already seen receive that token out of a pool can be failing to
sell it; anyone else calling a router that happens to mention the token is doing something unrelated.

`sell_tax` catches the family that does not revert. A fee-on-transfer token splits the leg leaving the pool: the
trader's share goes one way and the fee goes to a tax wallet, the token contract or the zero address, so the pool
emits **more than one Transfer of that token in the same transaction** and the smaller recipients are the fee. That
framing survives routing, but not on its own: an aggregator filling one order from two pools also sends the token to
two recipients, which reads as a fee split and is not one. What separates them is *who* the smaller leg goes to. A
transfer fee has a beneficiary — a tax wallet, the token contract, the zero address — and it is the same address every
time; a split route's second recipient is a different trader each time. So a tax is claimed only when the secondary
legs concentrate on one or two addresses across the whole window.

Two versions of this were wrong before that. The first asked what reached the transaction's *sender*, and since nearly
every swap settles through a router rather than to the EOA, it reported a 99% tax on WETH, USDC and USDT. The second
dropped the concentration test and reported a 30% tax on MANA, which routes through two pools. The blue chips made
both obvious; a thin memecoin would not have.

The severity ladder requires the combination: buyers present *and* sales attempted *and* those attempts failing or
being taxed away. A token nobody has tried to sell is reported at `info` as unproven, never as a honeypot, because
the evidence for the claim does not exist yet.

**This is a screen, not a verdict.** The false positives are real and named in each hit: a token can revert sales
because of slippage in a thin pool, because of a legitimate anti-sniper cooldown in its first minutes, or because the
calldata heuristic attributed someone else's failure to it. Confirming one means reading the contract or simulating a
sale, which `verify`'s `honeypot-source-gate` assertion does for the top hit.
"""
import collections

from . import Hit
from window_raw import hx, word, topic_addr

NAME = 'honeypot_signature'
DESCRIPTION = 'tokens whose buyers cannot sell: reverting sales, confiscatory taxes, buyers without sellers'
SEVERITY = 'high'

TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
V2_SWAP = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'
V3_SWAP = '0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67'
MIN_BUYERS = 10           # fewer than this and the ratio is noise
MIN_ATTEMPTS = 5          # sales must have been *tried* before "cannot sell" means anything
HIGH_FAIL = 0.5           # share of attempts that emitted no logs
HIGH_TAX = 0.10           # share of a swap's token leg that never reaches the trader
BASE_FAIL_RATE = 0.044    # measured: share of all router-targeted txs in a normal window that emit no logs
TOP = 8


def scan(ctx):
    routers = {a for a, v in ctx.book.items() if v.get('kind') == 'venue'}
    routers |= {'0x7a250d5630b4cf539739df2c5dacb4c659f2488d',   # Uniswap v2 Router 02
                '0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad',   # Universal Router
                '0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45',   # SwapRouter02
                '0x66a9893cc07d91d95644aedd05d03f95e1dba8af'}   # Universal Router v2

    tokens = set()
    buyers = collections.defaultdict(set)
    sellers = collections.defaultdict(set)
    buy_n = collections.Counter()
    sell_n = collections.Counter()
    attempts = collections.Counter()
    fails = collections.Counter()
    taxed_out = collections.Counter()     # token leaving a pool in a buy, summed over transactions
    taxed_primary = collections.Counter()  # of that, the largest single recipient per transaction
    fee_recipients = collections.defaultdict(collections.Counter)   # token -> secondary recipient -> amount
    first_seen = {}
    router_calls = []
    sell_txs = collections.defaultdict(set)   # token -> transactions containing a successful sale of it

    for b, logs in ctx.window.blocks():
        n = hx(b['number'])
        by_tx = collections.defaultdict(list)
        for l in logs:
            tokens.add(l['address'].lower())
            by_tx[l['transactionHash']].append(l)
        for h, ls in by_tx.items():
            pools = {l['address'].lower() for l in ls if l['topics'] and l['topics'][0] in (V2_SWAP, V3_SWAP)}
            if not pools:
                continue
            out_legs = collections.defaultdict(collections.Counter)   # token -> recipient -> amount out of a pool
            for l in ls:
                tp = l['topics']
                if not tp or tp[0] != TRANSFER or len(tp) != 3 or len(l['data']) < 66:
                    continue
                tok, frm, to = l['address'].lower(), topic_addr(tp[1]), topic_addr(tp[2])
                amt = word(l['data'], 0)
                first_seen.setdefault(tok, n)
                if frm in pools and to not in pools:
                    buyers[tok].add(to)
                    buy_n[tok] += 1
                    out_legs[tok][to] += amt
                elif to in pools and frm not in pools:
                    sellers[tok].add(frm)
                    sell_n[tok] += 1
                    sell_txs[tok].add(h)
            # Within one transaction, a token leaving a pool to several recipients is a fee split: the trader takes
            # the largest share and the rest is the tax. One recipient means no fee on that leg.
            for tok, recips in out_legs.items():
                tot = sum(recips.values())
                if not tot:
                    continue
                taxed_out[tok] += tot
                top = max(recips, key=lambda r: recips[r])
                taxed_primary[tok] += recips[top]
                for r, amt in recips.items():
                    if r != top:
                        fee_recipients[tok][r] += amt

        with_logs = set(by_tx)
        for t in b['transactions']:
            to = (t.get('to') or '').lower()
            if to not in routers:
                continue
            d = t.get('input') or ''
            # Addresses named in the calldata, kept only where the window has seen that address emit a Transfer.
            # Without that intersection the ABI's own offsets and small integers read as addresses.
            named = {'0x' + d[i + 24:i + 64] for i in range(10, len(d) - 63, 64)
                     if d[i:i + 24] == '0' * 24 and d[i + 24:i + 64] != '0' * 40}
            if named:
                # Attribution is deferred: it needs the complete buyer set, which is only known after the whole
                # window has been read.
                router_calls.append((t['from'].lower(), named, t['hash'] not in with_logs, t['hash']))

    # A sale was attempted when it either succeeded or reverted, so the denominator is exactly those two. A router
    # call that *bought* the token is neither, and counting it as one — which the first version did — buries a real
    # honeypot: twenty buys against twelve blocked sales reads as a 37% failure rate instead of 100%.
    for frm, named, failed, h in router_calls:
        if not failed:
            continue          # a successful call is counted through its own swap legs below, if it was a sale
        for a in (named & tokens):
            if frm not in buyers[a]:
                continue      # not a holder, so not a sale of this token
            fails[a] += 1
    for a in tokens:
        attempts[a] = fails[a] + len(sell_txs[a])

    hits = []
    for tok in tokens:
        nb, ns = len(buyers[tok]), len(sellers[tok])
        if nb < MIN_BUYERS:
            continue
        att, fl = attempts[tok], fails[tok]
        fail_rate = fl / att if att else None
        out, got = taxed_out[tok], taxed_primary[tok]
        tax = (1 - got / out) if out and got else None
        # Does the smaller leg go to the same place every time? A fee has one beneficiary; a split route does not.
        fees = fee_recipients[tok]
        fee_total = sum(fees.values())
        top_fee, top_fee_amt = (fees.most_common(1) or [(None, 0)])[0]
        fee_concentration = (top_fee_amt / fee_total) if fee_total else None
        fee_looks_real = (fee_concentration is not None and fee_concentration >= 0.8 and len(fees) <= 3)
        seller_ratio = ns / nb

        # A token nobody has tried to sell cannot be shown to block sales, however lopsided its buyer count.
        proven = att >= MIN_ATTEMPTS
        blocked = proven and fail_rate is not None and fail_rate >= HIGH_FAIL
        confiscatory = tax is not None and tax >= HIGH_TAX and fee_looks_real
        lopsided = seller_ratio <= 0.10

        if not (blocked or confiscatory or (lopsided and proven)):
            continue
        if blocked and lopsided:
            sev, verdict = 'high', 'buyers cannot sell: sales are attempted and revert'
        elif confiscatory and lopsided:
            sev, verdict = 'high', 'sales succeed and return little: a tax honeypot'
        elif blocked or confiscatory:
            sev, verdict = 'notable', 'sales fail or are taxed, but sellers do exist — a gate on some holders, or a thin pool'
        else:
            sev, verdict = 'info', 'buyers far outnumber sellers and sales were attempted, but none is shown to fail'

        hits.append(Hit(
            detector=NAME, key=tok, severity=sev, usd=None,
            title='%s: %d buyers, %d sellers%s%s — %s'
                  % (ctx.window.symbol(tok) or tok[:12], nb, ns,
                     (', %.0f%% of %d sell attempts emitted no logs' % (100 * fail_rate, att)) if fail_rate else '',
                     (', %.0f%% of the token leg never reached the buyer' % (100 * tax)) if confiscatory else '',
                     verdict),
            evidence={'token': tok, 'symbol': ctx.window.symbol(tok), 'label': ctx.label(tok),
                      'distinct_buyers': nb, 'distinct_sellers': ns, 'seller_to_buyer_ratio': round(seller_ratio, 4),
                      'buy_legs': buy_n[tok], 'sell_legs': sell_n[tok],
                      'router_calls_naming_it': att, 'of_which_emitted_no_logs': fl,
                      'fail_rate': None if fail_rate is None else round(fail_rate, 3),
                      'window_base_fail_rate': BASE_FAIL_RATE,
                      'buy_leg_retention': None if tax is None else round(1 - tax, 4),
                      'fee_beneficiary': top_fee, 'distinct_secondary_recipients': len(fees),
                      'fee_concentration': None if fee_concentration is None else round(fee_concentration, 3),
                      'fee_is_a_fee_not_a_split_route': fee_looks_real,
                      'buy_leg_tax': None if tax is None else round(tax, 4),
                      'first_seen_block': first_seen.get(tok),
                      'verdict': verdict,
                      'why': 'a transaction that emitted no logs reverted or did nothing, and a sell gate is what '
                             'produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it '
                             'is never the finding on its own',
                      'false_positives': 'a thin pool reverting on slippage, an anti-sniper cooldown in a token’s '
                                         'first minutes, and calldata that names several tokens so a failure is '
                                         'attributed to all of them. Confirm by reading the contract or simulating '
                                         'a sale before treating this as a verdict.'}))
    order = {'high': 0, 'notable': 1, 'info': 2}
    hits.sort(key=lambda h: (order[h.severity], -h.evidence['distinct_buyers']))
    return hits[:TOP]
