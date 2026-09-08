# Ten hours of Ethereum, and the thirty-four minutes that mattered

**Window.** 2026-09-07 22:26:23 → 2026-09-08 08:26:23 UTC. 2,993 blocks, 675,675 transactions, 2,371,958 logs.
`verify` passes: 13 numeric re-derivations and 7 identities, no failures, provenance gate green after a mid-session
registry edit.

Ten hours of mainnet is, on almost every measure, ten hours of nothing. ETH moved 1.7% end to end (2,489.88 → 2,472.99).
$250.0M of DEX volume. **One liquidation, for one dollar of debt**, across a lending complex holding several billion.
Block fullness sat between 49.8% and 52.0% in every half-hour bucket, and the median base fee ranged from 0.045 to
0.072 gwei — a 1.6x band across a full overnight cycle.

Two things happened anyway, and they are the report.

---

## 1. Thirty-four minutes across midnight, $397,310,079, and every leg reversed to the dollar

A prior window recorded, by hand, that Aave's USDC reserve had gone to 100% utilisation for about half an hour at
23:41 UTC with $503 of liquidity left, and filed it as a sentence. This session turned that sentence into a detector —
`liquidity_blackout`, which inverts each reserve's published borrow rate through its own IRM to recover the utilisation
the pool was priced at, and reports episodes where withdrawable liquidity collapses **along with the clock time they
happen**. A one-hour window can only ever see a fragment of a schedule; ten hours spanning midnight sees the whole
thing.

It fired on the first window that could contain it:

> **[high] Aave v3 USDC closed its exit at 23:47 UTC for 22 minutes: $55.4k withdrawable on a $2.3B reserve at
> 99.9976% utilisation.**

Following it back through the window's own transfers gives the entire mechanism, to the dollar:

| UTC | block | what |
|---|---:|---|
| 23:35:47 | 25928799 | `0x688cc76d` redeems **$245,571,215 of sUSDS** and receives **$245,529,853 USDC** — one atomic transaction through Sky's sUSDS → USDS → DAI → USDC plumbing |
| 23:37:47 | 25928809 | `0x56957e41` withdraws **$151,780,227 USDC** from Aave v3 — **100.16% of that reserve's median free liquidity** |
| 23:37:47 | 25928809 | `0x688cc76d` forwards its $245,529,853 to hub `0x31173ed1` |
| 23:38:59 | 25928815 | `0x56957e41` forwards its $151,780,227 to the same hub |
| 23:41:23 | 25928827 | the hub sends the consolidated **$397,310,079** to `0xf1edbf98` |
| 23:47:11 | 25928856 | Aave USDC utilisation peaks at **99.9976%**; borrow rate 4.273% → **14.296%**; $55,371 withdrawable on $2.31B |
| 00:03:59 | 25928939 | `0xf1edbf98` returns **$397,310,079**, exactly |
| 00:06:11 / 00:06:23 | 25928950/1 | the hub splits it back to the two feeders, exactly |
| 00:08:11 | 25928960 | $151,780,227 supplied back into Aave; the blackout ends at 00:08:47 |
| 00:09:35 | 25928967 | $245,529,853 USDC re-minted into sUSDS |

Nothing was traded. Nothing was earned. No position was opened anywhere else. All five addresses hold **zero USDC
now**, and all four of the non-protocol ones are EOAs with long histories (nonces 656 to 3,564) — operational wallets,
not fresh ones. The only quantity that changed over the thirty-four minutes is **where $397.3M of dollars were at
00:00 UTC**.

**What it costs, and who pays.** The account that emptied Aave gave up **$315** of supply interest over 30.4 minutes.
The account that unwound sUSDS came back with **$558 less** than it left with — within a dollar of the 34 minutes of
savings yield it skipped. Call it under **$900** all-in, plus gas that at 0.05 gwei is not worth naming.

Meanwhile, for the 21.6 minutes the reserve was shut:

* Aave's USDC borrowers paid **$8,879** more than they would have at the standing rate;
* the suppliers who stayed collected **$8,214** of it;
* and **nobody could withdraw from a $2.31 billion reserve**, because $55,371 was all that was left in it.

So a routine costing its operator under a thousand dollars moved roughly nine thousand from borrowers to suppliers and
took a multi-billion-dollar exit off the board for twenty-two minutes, every night. This is the third window in which
this repo has seen it — $389M on 2026-09-05/06, ~$152M out of Aave at 23:41 on 2026-09-07, $397.3M now — and the first
in which it has been traced end to end rather than inferred from a rate spike.

**What it is not.** This says nothing about intent, and nothing here identifies the operator. The measurement is that
$397.3M of yield-bearing dollar positions are unwound into plain USDC at a single address across the UTC midnight
boundary and rebuilt immediately afterwards. Reading that as balance-sheet presentation is an inference; reading it as
*a schedule* is not — the clock time is in the evidence, and the ledger's recurrence column will now keep score without
anyone having to remember.

**For strategy, the operative fact is the constraint, not the rate.** The 12.87% Aave USDC prints during the blackout
is worth about $55 on $10M for the half hour it exists and cannot be entered anyway. The finding is the other side:
**Aave's USDC reserve cannot be exited for roughly twenty minutes every night**, and any position whose exit leg is
that reserve either sizes to the trough or holds through it. That is the same lesson the cross-chain scan reached from
the other direction, where withdrawable liquidity — not rate — capped seven of twenty dollar switches.

---

## 2. The fee market: the one-hour result was not an artifact of a quiet hour

Last session measured, on a single morning hour, that Ethereum burned $1,098 while its users paid $7,598 to block
builders. Ten hours including the overnight peak say the same thing:

| | one hour (06:23–07:23) | ten hours (22:26–08:26) |
|---|---:|---:|
| base fee burned | $1,098 | **$11,334** |
| priority fees paid to builders | $7,598 | **$75,713** |
| ratio | 6.92× | **6.68×** |
| gas-weighted median tip | 0.0087 gwei | 0.0068 gwei |

The ratio never drops below 4.4 in any half-hour bucket, and the block-fullness series never leaves the 50% target.
That is the whole story in two numbers: **EIP-1559 is in perfect equilibrium at a price of nothing**, because the
marginal buyer of Ethereum blockspace has a reservation price of approximately zero and there is an unlimited supply of
it. Over ten hours, **17.6% of the sampled gas** went to four unverified batch contracts — the largest of them a batch minter
for **XEN**, whose economic design is literally to convert gas into tokens — which between them paid **$9** in priority
fees. Above them, a long tail of ordinary wallets whose fee estimators never noticed the base fee move pays essentially
all of the $75,713.

| priority fee | share of gas, 10h | share of gas, 1h |
|---|---:|---:|
| exactly zero | 8.4% | 9.0% |
| ≤ 0.01 gwei | 45.9% | 44.6% |
| **combined ≤ 0.01 gwei** | **54.3%** | **53.5%** |
| ≤ 0.1 gwei | 21.4% | 19.0% |
| ≤ 1 gwei | 16.2% | 18.3% |
| > 1 gwei | 8.1% | 9.1% |

**A correction to the previous report.** It said "35.6% of all gas paid exactly zero tip". That bucket used a 0.001
gwei cutoff, so it was not "exactly zero" — at a strict threshold the same hour reads 9.0% exactly zero and 44.6% at or
under 0.01 gwei. The substantive claim is unchanged and is now confirmed over ten hours: **more than half of Ethereum's
blockspace is bought for essentially nothing.** The label on one row was wrong.

---

## The rest of the ten hours, briefly

**Nothing is stressed.** One liquidation, $1 of debt. 1,972 Balancer flash loans moving $83.7M — the free-liquidity
carousel, still turning. Every dollar peg inside 30bp: USDT 0.99972 volume-weighted across $32.5M, USDS 1.00000,
crvUSD 0.99978, USDe 0.99983.

**Just-in-time liquidity is not the tax it is described as.** 276 JIT episodes took **$236 of $224,564** of pool fees —
0.11%. On this window a passive LP loses about a tenth of a percent of its fee income to JIT, which is smaller than the
rounding on its own price basis.

**Robinhood Chain is still Ethereum's largest customer for blob space**, and by a wider margin than the L2s it sits
above: 4,998 of 18,394 blobs (27.2%), ahead of Base (4,344) and OP Mainnet (3,920). That inbox had been carried in the
label registry as `known-canonical` since the Orbit study, but `window_events.py` kept its own hand-written table and
so printed the largest blob poster on Ethereum as "(unlabelled)" in every digest since. Fixed: the digest now falls
through to the registry, which is what a registry is for.

**Spam is the second-largest consumer of the chain.** In ten hours: XEN minted to 14,831 recipients across 149
transactions; one sender fanned a token to 24,563 recipients; another sent USDT dust to 21,149 addresses in 300
transactions; and 404 address-poisoning attempts trailed large transfers from 197 lookalike senders. All of it is
economic only because gas is free.

**Rates moved, slightly.** Compound v3 USDC now pays 1.62pp over SparkLend (the ledger's decay series for that pair now
has seven points and oscillates rather than trends), and a new one appeared this window: USDC borrows **3.87pp cheaper
on Aave v3 than on Compound v3**, with $154.7M withdrawable — which is a real refinancing, not a yield.

---

## What this window changed in the machinery

* **`detectors/liquidity_blackout.py`** — new. Turns a hand-observed nightly routine into a check that runs forever,
  reports the clock time, and lets the ledger decide whether an episode is a schedule or an accident. It found the
  routine on the first window that could contain one, and it is silent on the four windows that could not.
* **`fee_census.py --every N`** — a regular subsample, so a ten-hour census costs 753k credits instead of 3M. Rates and
  ratios need no scaling; totals are labelled as sampled, and the sample share is in the output.
* **Six registry entries**, five of them behavioural and from this window: sUSDS and Aave's aEthUSDC as token and
  protocol contracts (`solver_fingerprint` had been reporting the sUSDS token as an "unlabelled bot cycling $249.6M"),
  and the four addresses of the midnight routine, each described by what it did rather than by who it might be. Editing
  the registry made `verify` refuse to compare a number until `analyze` was re-run, which is the gate working.
* **`window_events.py` now consults the label registry** for blob inboxes instead of only its own table.

## What I would have the quant step do next

1. **Run the blackout detector against every saved window** — including the 2026-09-05 day study, which covers three
   midnights. Three consecutive nights make a schedule; ten make a fact you can trade around.
2. **Price the routine's externality as a standing risk on the strategy book.** Any leg that exits Aave USDC has a
   twenty-minute daily outage; that belongs in the kill criteria, not in prose.
3. **Charge gas at the tip.** Still open from the last session, and now measured over ten hours rather than one: an
   inclusion-sensitive leg costs about seven times the base fee.
4. **Watch whether the two feeders and the hub reappear tonight.** The ledger now has their keys; a second sighting
   turns an event into a pattern without anyone having to look.
