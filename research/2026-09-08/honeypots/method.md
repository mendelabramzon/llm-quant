# Honeypot tokens: what they are, what the chain shows, and what a screen can honestly claim

Written 2026-09-08. Defensive research: the object is to recognise a token that traps buyers, from data this repo
already collects. Nothing here is a trading strategy, and the screen it produced is in
[`scripts/detectors/honeypot_signature.py`](../../../scripts/detectors/honeypot_signature.py).

## 1. The mechanisms

A honeypot is a token you can buy and cannot sell. Five families cover nearly all of them, and they differ in
*where* the block sits rather than in what the victim experiences.

| family | where the block sits | what a victim sees |
|---|---|---|
| **sell gate** | `transfer`/`transferFrom` reverts unless the sender is the pool, the deployer or a whitelist | the sale reverts |
| **blacklist** | buyers are added to a deny list, often *after* they buy, so the trap arms behind them | early sales work, later ones revert |
| **confiscatory tax** | a fee on transfer set to 90–100% on the sell side | the sale succeeds and returns almost nothing |
| **trading switch** | `tradingEnabled` flipped off, or `maxTxAmount`/`maxSellAmount` set below any real sale | reverts, or only dust sales pass |
| **liquidity rug** | not a contract trap at all: the LP is withdrawn | the sale reverts for want of a counterparty |

Two properties matter for detection. First, **the gate is usually disguised** — as a slippage guard, an anti-bot
cooldown, a "max wallet" limit — so reading the source is a judgement call even when the source is verified, and it
often is not. Second, **a proxy can add a gate after listing**, so a contract that was clean when audited is not
necessarily clean now. Both push toward evidence from behaviour rather than from code.

## 2. What the chain shows, and what it does not

This repo collects blocks with full transactions and `eth_getLogs` per block. It does **not** collect receipts, which
at first looks fatal: without a receipt there is no status flag, so how do you see a failed sale?

You see it as an absence. A reverted transaction emits no logs, so **a transaction that appears in a block with no
log carrying its hash either reverted or did nothing.** Across a normal window about **4.4% of transactions sent to a
swap router emit no logs**, which is the base rate a token has to beat to be interesting.

Three signals come out of the window, and the design point is that none of them is sufficient alone.

**Buyers without sellers** is the shape everyone reaches for and is close to useless by itself. In the 2026-09-07
five-hour window, dozens of tokens sit at a 20-buyers-to-2-sellers ratio and they are ordinary launches — including
the tokenized stocks of the stock-router swarm, where WMB (Williams Companies) shows 41 buyers and 2 sellers simply
because the venue was hours old. Nobody had tried to sell.

**Failed sale rate** is the discriminator, and its denominator is the sales actually *attempted*: the ones that
succeeded, plus the ones that reverted. A router call that bought the token is neither.

**Sell tax** catches the family that does not revert. A fee-on-transfer token splits the leg leaving the pool — the
trader's share one way, the fee to a tax wallet, the token contract or the zero address — so the pool emits more than
one Transfer of that token in one transaction.

## 3. Three wrong versions, and what each one taught

Every one of these produced a confident, plausible, wrong answer. They are written down because the failure modes are
the transferable part.

**Measuring the tax against the transaction's sender.** A fee-on-transfer token was to be detected by comparing what
left the pool against what reached the trader — taking "the trader" to be `tx.from`. Nearly every swap settles
through a router or a smart account rather than to the EOA, so the measure reported a **99% sell tax on WETH, USDC
and USDT**. The blue chips made it obvious; on a thin memecoin it would have read as a confirmed honeypot.

**Treating any multi-recipient leg as a fee.** Corrected to "the pool sent this token to more than one address, so
the smaller legs are the fee", it reported a **30% tax on MANA**, which an aggregator routes through two pools. The
fix is that a fee has a *beneficiary*: the same address every time. A split route's second recipient is a different
trader every time. A tax is now claimed only when the secondary legs concentrate on one or two addresses.

**Attributing a failure to every token named in the calldata.** An aggregator's calldata carries many addresses, so
one unrelated revert is charged to all of them. This put **Centrifuge's CFG at a 70% failure rate and Nym's NYM at
100%** — two real projects, flagged at `notable`. The rule that fixes it: **a failed sale must come from someone who
bought.** Only a sender the window has already seen receive that token out of a pool can be failing to sell it.

Each fix made the screen quieter. That is the direction a screen should move when it is being made honest, and it is
why the next section exists.

## 4. Proving it still fires

Three tightenings removed every false positive the screen had, and the last removed all of them at once. On seven
real windows — about thirteen hours of mainnet — it now reports **no proven honeypot and no high-severity claim at
all**. From the outside that is indistinguishable from a detector that can no longer fire.

So [`scripts/test_honeypot.py`](../../../scripts/test_honeypot.py) builds synthetic windows in the collector's own
on-disk format where the answer is known:

| control | construction | required |
|---|---|---|
| honeypot | 20 buyers, 0 sellers, 12 holders whose sales emit no logs | reported `high`, fail rate 1.0 |
| normal launch | 20 buyers, 6 successful sales | **never** `high` — this is the shape a naive ratio test fails on |
| stranger | 20 buyers, 15 failed router calls from addresses that never bought | not attributed: 0 attempts |

The first control failed on its first run — on the harness, not the detector. The helper built 40-character
addresses while a Transfer topic reads back at full width, so the buyer recorded from the log never matched the
transaction sender. It then failed a second time on a real bug in the detector: buy transactions were counted in the
denominator, so twenty buys against twelve blocked sales read as a 37% failure rate rather than 100%, which would
have buried a genuine honeypot below the threshold.

## 5. What the screen can and cannot claim

**It can say**: this token's holders attempted sales in this window and those sales reverted at a rate far above the
4.4% base; or, the token leaving the pool is being split to a consistent beneficiary, so there is a transfer fee of
measurable size. Both are statements about what happened to real buyers.

**It cannot say**: that a token is a honeypot when nobody has tried to sell it. Every candidate on real windows so
far is in exactly that state, reported at `info` as unproven, and the two that recur are BMC and PEPE — a lopsided
hour, not a trap.

**Known false positives**, named in every hit: a thin pool reverting on slippage; a legitimate anti-sniper cooldown
in a token's first minutes; and calldata that names several tokens, though the holder rule now removes most of that.

**The binding limitation is the window.** The screen only sees honeypots whose victims tried to sell inside the same
window, so an hour catches almost nothing and the natural cadence is a day. A token-focused follow-up — simulating a
sale against a fork at the current block, which is what the commercial checkers do — is the confirmation step this
screen is designed to feed rather than replace.
