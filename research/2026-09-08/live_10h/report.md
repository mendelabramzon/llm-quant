# Ethereum mainnet live scan: 2026-09-07T22:26:23+00:00 to 2026-09-08T08:26:23+00:00 UTC

Blocks 25928453 to 25931445 (2993 blocks, 10.00 h), 675,675 transactions, 2,371,958 logs. Prices at head block 25931629: ETH $2476, BTC $78k. Generated 2026-09-08T09:26:06+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

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


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [0x28cd…e563](https://etherscan.io/address/0x28cd762e49726a4f0725a2846c85d19462b3e563) | uni v2_like | 0x8e9d…cf3e/WETH | ? | 4 | $39.8M | $119k | $0 | $119k | – | – | – | – |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 2795 | $18.1M | $9045 | $64 | $8982 | $507.2M | 1.55% | 312.4% | 1.706% |
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 521 | $17.9M | $108 | $0 | $108 | $100.0B | 0.00% | 0.0% | 0.014% |
| [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) | curve | USDC/USDT | ? | 122 | $14.5M | – | $0 | – | – | – | – | – |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 8039 | $11.3M | $1128 | $3 | $1125 | $62.6M | 1.57% | 316.9% | 3.045% |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 1084 | $11.1M | $100 | $0 | $100 | $24.8B | 0.00% | 0.1% | 0.774% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 511 | $10.6M | $32k | $0 | $32k | $1.8B | 1.54% | 310.3% | 1.186% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 423 | $9.2M | $92 | $0 | $92 | $10.8B | 0.00% | 0.1% | 3.852% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 121 | $5.7M | $34 | $0 | $34 | $149.1B | 0.00% | 0.0% | 0.003% |
| [0x5b03…8e96](https://etherscan.io/address/0x5b03cccab7ba3010fa5cad23746cbf0794938e96) | curve | USDe/USDT | ? | 152 | $5.6M | – | $0 | – | – | – | – | – |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 5334 | $4.6M | $455 | $2 | $454 | $26.1M | 1.52% | 307.0% | 16.055% |
| [0x4dec…d69e](https://etherscan.io/address/0x4dece678ceceb27446b35c672dc7d61f30bad69e) | curve | USDC/crvUSD | ? | 175 | $4.4M | – | $0 | – | – | – | – | – |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 620 | $4.2M | $2083 | $0 | $2083 | $204.4M | 0.89% | 179.9% | 1.539% |
| 0xb203…448b | uni v4 | sUSDe/USDT | 0.01% | 161 | $4.1M | $414 | $0 | $414 | $5.5B | 0.01% | 1.3% | 0.050% |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 165 | $3.6M | $111 | $0 | $110 | $8.0B | 0.00% | 0.2% | 2.041% |
| [0xbafe…8e5d](https://etherscan.io/address/0xbafead7c60ea473758ed6c6021505e8bbd7e8e5d) | uni v3 | AUSD/USDC | 0.01% | 35 | $3.2M | $323 | $0 | $323 | $543.8B | 0.00% | 0.0% | 0.002% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 1181 | $2.6M | $1304 | $11 | $1293 | $65.7M | 1.72% | 347.2% | 1.716% |
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 119 | $2.4M | – | $0 | – | – | – | – | – |
| [0x13e1…43e1](https://etherscan.io/address/0x13e12bb0e6a2f1a3d6901a59a9d585e89a6243e1) | curve | frxUSD/crvUSD | ? | 53 | $2.4M | – | $0 | – | – | – | – | – |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 370 | $2.4M | $1219 | $0 | $1219 | $353.4M | 0.30% | 60.9% | 0.626% |
| 0x9035…eb4f | uni v4 | RLUSD/USDS | 0.00% | 31 | $2.4M | $14 | $0 | $14 | $40.0B | 0.00% | 0.0% | 0.003% |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 432 | $2.3M | $232 | $1 | $232 | $62.7B | 0.00% | 0.1% | 0.011% |
| [0xc061…1622](https://etherscan.io/address/0xc061caa073f3d95f80f8e5428d32d2d76f5e1622) | curve | USDC/USDG | ? | 56 | $2.1M | – | $0 | – | – | – | – | – |
| 0xe500…a657 | uni v4 | USDC/WETH | 0.03% | 718 | $2.0M | $343 | $0 | $343 | $62.4M | 0.48% | 96.9% | 1.709% |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.03% | 680 | $1.9M | $333 | $0 | $333 | $60.1M | 0.48% | 97.8% | 1.722% |
| 0x21c6…ca27 | uni v4 | ETH/USDC | 0.06% | 673 | $1.7M | $1070 | $0 | $1070 | $69.2M | 1.35% | 272.9% | 1.668% |
| [0x8ad5…e6d8](https://etherscan.io/address/0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8) | uni v3 | USDC/WETH | 0.30% | 276 | $1.7M | $5000 | $0 | $5000 | $279.5M | 1.57% | 315.7% | 1.183% |
| [0x390f…7bf4](https://etherscan.io/address/0x390f3595bca2df7d23783dfd126427cceb997bf4) | curve | USDT/crvUSD | ? | 181 | $1.4M | – | $0 | – | – | – | – | – |
| 0x50b0…5fa8 | uni v4 | ETH/USDT | 0.35% | 127 | $1.4M | $5006 | $0 | $5006 | $295.8M | 1.48% | 298.6% | 1.079% |
| 0xdce6…f78d | uni v4 | ETH/USDC | 0.35% | 133 | $1.4M | $4953 | $0 | $4953 | $284.0M | 1.53% | 307.8% | 1.086% |
| [0xb31e…5bc3](https://etherscan.io/address/0xb31e70454bdf5bc3) | balancer | USDC/WETH | ? | 93 | $1.4M | – | $0 | – | – | – | – | – |
| 0xb90d…b716 | uni v4 | USDC/USDG | 0.01% | 107 | $1.4M | $114 | $0 | $114 | $14.4B | 0.00% | 0.1% | 0.015% |
| [0x52c7…bc39](https://etherscan.io/address/0x52c77b0cb827afbad022e6d6caf2c44452edbc39) | uni v2_like | WETH/0xe0f6…c56c | ? | 296 | $1.3M | $3806 | $0 | $3806 | – | – | – | – |
| 0x8aa4…4e47 | uni v4 | ETH/USDT | 0.00% | 186 | $1.2M | $15 | $0 | $15 | $19.1B | 0.00% | 0.0% | 0.013% |
| [0xd0fc…6d78](https://etherscan.io/address/0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78) | uni v3 | UNI/USDC | 0.30% | 337 | $1.1M | $3347 | $0 | $3347 | $24.1M | 12.17% | 2451.8% | 5.841% |
| 0xdb4c…43b1 | uni v4 | ETH/0xc8fb…8888 | 0.00% | 1619 | $1.1M | $1 | $0 | $1 | $311k | 0.30% | 60.2% | – |
| 0x7233…ca73 | uni v4 | ETH/USDT | 0.06% | 632 | $1.0M | $627 | $0 | $627 | $37.5M | 1.47% | 295.3% | 1.658% |
| [0x1674…8d3a](https://etherscan.io/address/0x167478921b907422f8e88b43c4af2b8bea278d3a) | curve | sDAI/sUSDe | ? | 19 | $999k | – | $0 | – | – | – | – | – |
| 0x2287…1bba | uni v4 | ETH/USDT | 0.01% | 1820 | $870k | $109 | $0 | $109 | $88.9M | 0.11% | 21.6% | 528.822% |
| [0xe8f7…e124](https://etherscan.io/address/0xe8f7c89c5efa061e340f2d2f206ec78fd8f7e124) | uni v3 | WBTC/cbBTC | 0.01% | 31 | $809k | $81 | $0 | $81 | $45.5B | 0.00% | 0.0% | 0.007% |
| 0x7da1…7427 | uni v4 | USDC/USDG | 0.01% | 58 | $809k | $77 | $0 | $77 | $14.1B | 0.00% | 0.1% | 0.012% |
| [0x5906…9e9c](https://etherscan.io/address/0x5906fad82b9f9e9c) | balancer | WETH/USDT | ? | 52 | $784k | – | $0 | – | – | – | – | – |
| 0xb2b9…3a17 | uni v4 | ETH/USDC | 0.04% | 108 | $779k | $295 | $0 | $295 | $847.1M | 0.03% | 6.2% | 0.175% |
| [0x1d42…d801](https://etherscan.io/address/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801) | uni v3 | UNI/WETH | 0.30% | 435 | $769k | $2306 | $0 | $2306 | $19.1M | 10.60% | 2135.5% | 5.368% |
| [0xd51a…ae46](https://etherscan.io/address/0xd51a44d3fae010294c616388b506acda1bfaae46) | curve | WETH/USDT | ? | 513 | $699k | – | $0 | – | – | – | – | – |

Just-in-time liquidity: 276 episodes (mint and burn of identical liquidity inside one block), bracketing $514k of swaps and taking about $236 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 78 episodes, fees taken $85
- [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de): 30 episodes, fees taken $104
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 23 episodes, fees taken $2
- [0x27c2…2bf2](https://etherscan.io/address/0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2): 17 episodes, fees taken $5
- [0x3437…e4ab](https://etherscan.io/address/0x34373bba18aa058f889c3fc28329c0bfb4b3e4ab): 6 episodes, fees taken $0
- [0x1de4…4645](https://etherscan.io/address/0x1de4dd70b437de2ae7b628b3cae7bf9a0a9b4645): 6 episodes, fees taken $0
- [0x21f9…3782](https://etherscan.io/address/0x21f93d41012c040bb4151d36c3b0b69111f13782): 6 episodes, fees taken $0
- [0x4971…a452](https://etherscan.io/address/0x49719d256a5ea16bfa579ea16e95bea9fa41a452): 6 episodes, fees taken $0

Swap volume by venue: uniswap_v4 $82.9M (35492), uniswap_v3 $79.5M (59480), uniswap_v2_like $46.6M (22564), curve $38.5M (3376), balancer $2.5M (693).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0xdbeb…8cb3 (0x0000…0000/0x8602…2148, 355 swaps); 0x1271…75aa (0xb58e…21cb/0xcedb…f8e7, 292 swaps); 0x1b26…fdfa (0x0000…0000/0xa249…e63b, 257 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 209 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 178 swaps); 0x2287…1bba (0x0000…0000/0xdac1…1ec7, 173 swaps); 0x1ba3…1365 (0x0000…0000/0x0a5a…2477, 162 swaps); 0x17b3…4efd (0x5ab3…b691/0xdac1…1ec7, 121 swaps); 0x230e…804d (0x0000…0000/0xa0df…c845, 113 swaps); 0xd4e5…909d (0x14d6…47a1/0xa0b8…eb48, 108 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | tBTC | 0.00% | 0.26% | 0.2% | $134.3M | $205k |
| Aave v3 | EURC | 2.44% | 4.07% | 66.5% | $45.7M | $30.4M |
| Aave v3 | UNI | 0.00% | 0.17% | 1.1% | $3.2M | $36k |
| Aave v3 | WBTC | 0.00% | 0.33% | 2.5% | $2.7B | $67.5M |
| Aave v3 | GHO | 0.00% | 4.00% | 83.4% | $135.2M | $112.7M |
| Aave v3 | USDe | 1.65% | 5.84% | 37.6% | $661.0M | $248.7M |
| Aave v3 | LINK | 0.01% | 0.46% | 3.0% | $114.7M | $3.4M |
| Aave v3 | LUSD | 0.54% | 2.06% | 33.0% | $1.9M | $626k |
| Aave v3 | DAI | 3.07% | 4.72% | 86.8% | $131.6M | $114.2M |
| Aave v3 | PYUSD | 3.89% | 4.91% | 88.0% | $7.6M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.9B | $7.2M |
| Aave v3 | AAVE | 0.00% | 0.00% | 0.0% | $107.4M | $0 |
| Aave v3 | LBTC | 0.00% | 0.00% | 0.0% | $188.5M | $1332 |
| Aave v3 | RLUSD | 2.18% | 4.42% | 61.5% | $4.6M | $2.9M |
| Aave v3 | sDAI | 0.00% | 0.00% | 0.0% | $51k | $0 |
| Aave v3 | FRAX | 2.71% | 4.55% | 74.9% | $39k | $29k |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $265.0M | $0 |
| Aave v3 | MKR | 0.00% | 0.16% | 1.1% | $197k | $2084 |
| Aave v3 | USDC | 3.62% | 4.29% | 93.8% | $2.3B | $2.2B |
| Aave v3 | rsETH | 0.00% | 0.00% | 0.0% | $924.8M | $2874 |
| Aave v3 | rETH | 0.00% | 0.02% | 0.1% | $103.6M | $117k |
| Aave v3 | cbETH | 0.00% | 0.05% | 0.3% | $16.2M | $54k |
| Aave v3 | ezETH | 0.00% | 0.00% | 0.0% | – | – |
| Aave v3 | WETH | 1.42% | 2.02% | 82.5% | $5.3B | $4.4B |
| Aave v3 | USDtb | 5.62% | 8.58% | 81.8% | $15.4M | $12.6M |
| Aave v3 | ENS | 0.09% | 1.46% | 7.3% | $99k | $7236 |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.6% | $1.5B | $9.4M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $139k |
| Aave v3 | CRV | 0.47% | 5.77% | 12.5% | $2.9M | $361k |
| Aave v3 | USDT | 3.56% | 4.25% | 93.0% | $3.0B | $2.8B |
| Aave v3 | USDS | 0.12% | 5.52% | 3.0% | $11.2M | $335k |
| Aave v3 | USDG | 1.52% | 3.44% | 55.1% | $12.2M | $6.7M |
| Aave v3 | crvUSD | 0.99% | 2.91% | 42.4% | $186k | $79k |
| SparkLend | tBTC | 0.00% | 0.00% | 0.0% | $1.6M | $8 |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $141.1M | $327k |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $308.3M | $208.6M |
| SparkLend | PYUSD | 0.59% | 3.89% | 16.8% | $100.0M | $16.8M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9889 |
| SparkLend | LBTC | 0.00% | 5.00% | 0.0% | $261.8M | $0 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sDAI | 0.00% | 1.00% | 0.0% | $43k | $0 |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $26.2M | $24.1M |
| SparkLend | rsETH | 0.00% | 5.00% | 0.0% | $40k | $0 |
| SparkLend | sUSDS | 0.00% | 0.00% | 0.0% | $3.3M | $0 |
| SparkLend | rETH | 0.00% | 0.25% | 0.0% | $15.6M | $2029 |
| SparkLend | ezETH | 0.00% | 5.00% | 0.0% | – | – |
| SparkLend | WETH | 1.54% | 1.97% | 82.8% | $1.2B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.02% | 1.3% | $290.9M | $3.7M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $104.8M | $0 |
| SparkLend | USDT | 2.62% | 3.52% | 82.8% | $391.8M | $324.2M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $739.2M | $485.1M |
| SparkLend | USDG | 0.00% | 3.46% | 0.0% | $1 | $0 |
| Compound v3 USDC | base | 5.16% | 6.17% | 90.6% | $375.1M | $339.8M |
| Compound v3 USDT | base | 3.01% | 3.83% | 83.7% | $185.2M | $155.1M |
| Compound v3 WETH | base | 1.24% | 1.85% | 62.1% | $124.7M | $77.5M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.54% APR on $1.4B of USDe.

Rate curves: Aave v3 AAVE optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 0%; Aave v3 CRV optimal 45%, base 3.00%, slope1 10.00%, slope2 150.00%, reserve factor 35%; Aave v3 DAI optimal 92%, base 0.00%, slope1 5.00%, slope2 35.00%, reserve factor 25%; Aave v3 ENS optimal 45%, base 0.00%, slope1 9.00%, slope2 300.00%, reserve factor 20%; Aave v3 EURC optimal 90%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 10%; Aave v3 FRAX optimal 90%, base 0.00%, slope1 5.50%, slope2 40.00%, reserve factor 20%; Aave v3 GHO optimal 99%, base 4.00%, slope1 0.00%, slope2 0.00%, reserve factor 100%; Aave v3 LBTC optimal 45%, base 0.00%, slope1 4.00%, slope2 300.00%, reserve factor 50%; Aave v3 LINK optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 LUSD optimal 80%, base 0.00%, slope1 5.00%, slope2 50.00%, reserve factor 20%; Aave v3 MKR optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 PYUSD optimal 90%, base 1.00%, slope1 4.00%, slope2 50.00%, reserve factor 10%; Aave v3 RLUSD optimal 80%, base 2.50%, slope1 2.50%, slope2 50.00%, reserve factor 20%; Aave v3 UNI optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 USDC optimal 94%, base 0.00%, slope1 4.30%, slope2 10.00%, reserve factor 10%; Aave v3 USDG optimal 80%, base 0.00%, slope1 5.00%, slope2 30.00%, reserve factor 20%; Aave v3 USDS optimal 92%, base 5.50%, slope1 0.75%, slope2 35.00%, reserve factor 25%; Aave v3 USDT optimal 94%, base 0.00%, slope1 4.30%, slope2 10.00%, reserve factor 10%; Aave v3 USDe optimal 90%, base 5.00%, slope1 2.00%, slope2 12.00%, reserve factor 25%; Aave v3 USDtb optimal 80%, base 0.00%, slope1 4.00%, slope2 50.00%, reserve factor 20%; Aave v3 WBTC optimal 80%, base 0.25%, slope1 2.50%, slope2 300.00%, reserve factor 50%; Aave v3 WETH optimal 92%, base 0.00%, slope1 2.20%, slope2 6.00%, reserve factor 15%; Aave v3 cbBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 cbETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 crvUSD optimal 80%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 20%; Aave v3 ezETH optimal 45%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 15%; Aave v3 rETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 rsETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 sDAI optimal 90%, base 0.00%, slope1 5.00%, slope2 75.00%, reserve factor 20%; Aave v3 sUSDe optimal 90%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 20%; Aave v3 tBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 weETH optimal 30%, base 1.00%, slope1 7.00%, slope2 300.00%, reserve factor 45%; Aave v3 wstETH optimal 80%, base 0.00%, slope1 1.00%, slope2 40.00%, reserve factor 35%.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | USDC | 767 | 4.27% → 4.29% | 4.27% – 14.30% | 3.59% → 3.62% |
| Aave v3 | USDtb | 10 | 12.09% → 8.58% | 8.58% – 12.12% | 8.05% → 5.62% |
| SparkLend | USDT | 20 | 3.52% → 3.52% | 3.52% – 5.37% | 2.62% → 2.62% |
| Aave v3 | USDG | 20 | 3.64% → 3.41% | 3.41% – 4.92% | 1.69% → 1.49% |
| SparkLend | USDS | 24 | 3.93% → 3.93% | 3.86% – 3.96% | 2.32% → 2.32% |
| Aave v3 | RLUSD | 11 | 4.42% → 4.42% | 4.42% – 4.48% | 2.18% → 2.18% |
| Aave v3 | 0xaca9…35da | 3 | 4.24% → 4.27% | 4.24% – 4.27% | 2.55% → 2.59% |
| Aave v3 | USDe | 127 | 5.87% → 5.84% | 5.84% – 5.87% | 1.71% → 1.65% |
| Aave v3 | USDT | 387 | 4.28% → 4.25% | 4.25% – 4.28% | 3.60% → 3.56% |
| SparkLend | USDC | 9 | 4.27% → 4.27% | 4.26% – 4.28% | 3.54% → 3.54% |
| Aave v3 | EURC | 10 | 4.05% → 4.07% | 4.05% – 4.07% | 2.42% → 2.44% |
| Aave v3 | WETH | 449 | 2.02% → 2.02% | 2.00% – 2.02% | 1.41% → 1.41% |
| SparkLend | WETH | 28 | 1.96% → 1.97% | 1.96% – 1.97% | 1.55% → 1.54% |
| Aave v3 | WBTC | 91 | 0.34% → 0.33% | 0.33% – 0.34% | 0.00% → 0.00% |
| Aave v3 | LINK | 24 | 0.47% → 0.46% | 0.46% – 0.47% | 0.01% → 0.01% |
| Aave v3 | PYUSD | 3 | 4.90% → 4.91% | 4.90% – 4.91% | 3.87% → 3.89% |
| Aave v3 | DAI | 20 | 4.71% → 4.71% | 4.71% – 4.72% | 3.07% → 3.07% |
| SparkLend | PYUSD | 2 | 3.89% → 3.89% | 3.89% – 3.89% | 0.59% → 0.59% |
| Aave v3 | cbBTC | 39 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| Aave v3 | 0x59bc…9d34 | 11 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | wstETH | 79 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 50 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | wstETH | 11 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | WBTC | 3 | 0.01% → 0.01% | 0.01% – 0.01% | 0.00% → 0.00% |
| Aave v3 | AAVE | 17 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: supply $283.2M, withdraw $248.9M, borrow $43.2M, repay $40.4M, atomic supply $184.2M, atomic withdraw $180.5M, atomic borrow $1108, atomic repay $3; SparkLend: withdraw $98.1M, repay $20.5M, supply $93.3M, borrow $11.2M.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25928960 | Aave v3 | supply | USDC | $151.8M | [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) | [0xdc33…6e03](https://etherscan.io/tx/0xdc335da051c4d19c2eb7b27aac68edb78dffc83faade5b162c231f4dead86e03) |
| 25928809 | Aave v3 | withdraw | USDC | $151.8M | [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) | [0x21ba…56ba](https://etherscan.io/tx/0x21ba74b6e9440ba75ce31f6c1bd8e39a6d5d254bf49947801d9c04b567b056ba) |
| 25929394 | SparkLend | supply | USDT | $48.9M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x835a…b3ad](https://etherscan.io/tx/0x835af7ba8033fe6a9d7aa0c25e642e340d1582264d41d313161a8a115682b3ad) |
| 25928994 | SparkLend | withdraw | USDT | $48.7M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xec1e…2d98](https://etherscan.io/tx/0xec1e81fd3309a3b29143f6fde845a202a5f17451dc1e32aeec2e1771867e2d98) |
| 25930862 | SparkLend | supply | USDT | $18.0M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xf6fd…9594](https://etherscan.io/tx/0xf6fd901a3cc02426176f7b73b79b3635daeae4b5ef8aba4ae5a814659f179594) |
| 25928975 | Aave v3 | supply | USDT | $9.0M | [0x2906…715a](https://etherscan.io/address/0x29065a4c1f2f20d1e263930088890d6f49fe715a) | [0xc0b1…1964](https://etherscan.io/tx/0xc0b18a4ccc417b4fb4a422e637c1ecd11724d02fcd3abd2a98f703407b851964) |
| 25930516 | SparkLend | repay | USDS | $8.0M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0x3565…ec16](https://etherscan.io/tx/0x35652045acbfb04e32cae8c1d82031eee61416ef03749b200908e8171e8dec16) |
| 25930714 | Aave v3 | supply | USDT | $8.0M | [0x12bc…663e](https://etherscan.io/address/0x12bc7befc3035f64cdc8b16a91d74d6e816d663e) | [0x84b0…6082](https://etherscan.io/tx/0x84b0b2b76181d9fa1dd04cf0f56c3ff9e4b7130ac48ed8b15840f57d6b286082) |
| 25930568 | Aave v3 | supply | cbBTC | $8.0M | [0x933a…2833](https://etherscan.io/address/0x933adedd85824da75ec8a334a7907e69e7c02833) | [0xcc27…fd62](https://etherscan.io/tx/0xcc2774cdd4119ec1e6bdb0bc95eb4c9b576f0985f12adba4f8cff724616dfd62) |
| 25930406 | Aave v3 | supply | USDe | $7.6M | [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) | [0x3ade…8479](https://etherscan.io/tx/0x3adefe648b55594c056a5dc16fca5d44f641217e010e3c23f1cf375608158479) |
| 25931150 | Aave v3 | repay | WBTC | $6.7M | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | [0xf162…93ba](https://etherscan.io/tx/0xf16238bd1325dde31036d18abbf114985cf7f7c532c5bd6352d69153b89793ba) |
| 25931193 | Aave v3 | borrow | USDC | $5.0M | [0x1b36…1cd6](https://etherscan.io/address/0x1b36972588d214aea7b8f5322f349246bf571cd6) | [0x842c…e650](https://etherscan.io/tx/0x842cc08ed8f60c2f9a2076cae9cb784607a91923b0fdf39142af39183398e650) |
| 25930784 | Aave v3 | withdraw | cbBTC | $4.5M | [0x933a…2833](https://etherscan.io/address/0x933adedd85824da75ec8a334a7907e69e7c02833) | [0xaf67…bf43](https://etherscan.io/tx/0xaf6791563c6692698d251fecf2e7f8d9b1ba7a14df6d33b1e049ae057611bf43) |
| 25930818 | SparkLend | supply | cbBTC | $4.5M | [0x933a…2833](https://etherscan.io/address/0x933adedd85824da75ec8a334a7907e69e7c02833) | [0xbefc…d313](https://etherscan.io/tx/0xbefc87684a6d564a239f5ebc9604ff50116f901de8c696a0c44128c4cfd7d313) |
| 25931240 | Aave v3 | supply | wstETH | $4.4M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x1361…d002](https://etherscan.io/tx/0x1361f6390c8fd91d285c7ab57f68f52699bb0cd64b6645e18bea79cbd72ed002) |
| 25931068 | SparkLend | repay | USDS | $4.4M | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | [0x8c78…962b](https://etherscan.io/tx/0x8c78916a8a4f71121cabc499c514cd6a563cf16c984d3dd0135e4f6e7ea8962b) |
| 25930432 | SparkLend | borrow | USDS | $4.0M | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | [0xefc8…2b76](https://etherscan.io/tx/0xefc8f23fd31078622c2b0928bb20d307619e276b3250fe1417f7be16b5ed2b76) |
| 25931240 | Aave v3 | borrow | WETH | $4.0M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x1361…d002](https://etherscan.io/tx/0x1361f6390c8fd91d285c7ab57f68f52699bb0cd64b6645e18bea79cbd72ed002) |
| 25931240 | SparkLend | withdraw | wstETH | $4.0M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x1361…d002](https://etherscan.io/tx/0x1361f6390c8fd91d285c7ab57f68f52699bb0cd64b6645e18bea79cbd72ed002) |
| 25931323 | Aave v3 | repay | USDC | $3.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x3a3a…fbfa](https://etherscan.io/tx/0x3a3aa5ef2bb59f903c0b05b5aad8646e85333c3917291f21663a7b458958fbfa) |
| 25931323 | Aave v3 | borrow | USDC | $3.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x4a4b…66cd](https://etherscan.io/tx/0x4a4b07f549caa08413c90ff2c48993c20353e6cc5c4959ddb5cc922df41166cd) |
| 25931323 | Aave v3 | withdraw | USDT | $3.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x3a3a…fbfa](https://etherscan.io/tx/0x3a3aa5ef2bb59f903c0b05b5aad8646e85333c3917291f21663a7b458958fbfa) |
| 25928990 | SparkLend | withdraw | USDT | $3.5M | [0x176c…e9e2](https://etherscan.io/address/0x176caf15f1793fc16898458e0ba295ec6523e9e2) | [0x4651…020a](https://etherscan.io/tx/0x465191f21319acdf9e069091d97d4946559b6e88a7d03b541945987f1972020a) |
| 25929387 | Aave v3 | supply | WETH | $3.0M | [0xf78e…e2f3](https://etherscan.io/address/0xf78e6d431e5e51d7a63eb461021408b9b2d6e2f3) | [0x163e…48f8](https://etherscan.io/tx/0x163ec1cc58b63cfb56b2f6cf2862c7f937f0de9120aa579ac78caf55665748f8) |
| 25930681 | Aave v3 | supply | WETH | $2.5M | [0x12bc…663e](https://etherscan.io/address/0x12bc7befc3035f64cdc8b16a91d74d6e816d663e) | [0x4544…b3dd](https://etherscan.io/tx/0x454478abf71b600677ae42684806944aa47bf7d4289063be12d6587052bcb3dd) |
| 25929392 | SparkLend | supply | USDT | $2.3M | [0x176c…e9e2](https://etherscan.io/address/0x176caf15f1793fc16898458e0ba295ec6523e9e2) | [0x0da5…cc88](https://etherscan.io/tx/0x0da5bd1755673833d3ed2ce9292b46c184d93d8229f8ba3a38936711ed87cc88) |
| 25931431 | Aave v3 | supply | USDT | $2.0M | [0xbd42…9b9f](https://etherscan.io/address/0xbd42f7311b4c13ce003c44428060c4564c469b9f) | [0xc64d…40ae](https://etherscan.io/tx/0xc64d72a2d0102c8a0619badd5d3a835d445fbe9566b1008b8180753eed1e40ae) |
| 25930419 | Aave v3 | borrow | USDC | $2.0M | [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) | [0xc32c…aedc](https://etherscan.io/tx/0xc32cf5a1adf66b30e92779bc18271b414b89598ef87843943d6d4a0e9ddfaedc) |
| 25930250 | Aave v3 | supply | wstETH | $1.7M | [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | [0x33dd…49bf](https://etherscan.io/tx/0x33dd4d3eb2d4b09b477af8d6fb24b161ff64b0980e700cd55f35884a674c49bf) |
| 25930252 | Aave v3 | borrow | WETH | $1.6M | [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | [0x100d…9776](https://etherscan.io/tx/0x100da1a49670cc42e57a88f723d4c9c2f824f4cfba57190eb23a811e51c59776) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- Aave v3 withdraw $151.8M USDC by [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) ([0x21ba…56ba](https://etherscan.io/tx/0x21ba74b6e9440ba75ce31f6c1bd8e39a6d5d254bf49947801d9c04b567b056ba)): $151.8M → [midnight-routine hub: consolidates two feeder EOAs into one $397.3M USDC leg across 00:00 UTC and reverses it exactly (2026-09-08) (behaviour)](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18); $151.8M → [Aave v3 aEthUSDC — the reserve's aToken; symbol() read on chain (chain-read)](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c)
- SparkLend withdraw $48.7M USDT by [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) ([0xec1e…2d98](https://etherscan.io/tx/0xec1e81fd3309a3b29143f6fde845a202a5f17451dc1e32aeec2e1771867e2d98)): $48.7M → [Spark Savings USDT (spUSDT) (blockscout-verified)](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372); $464k → [AToken (via InitializableImmutableAdminUpgradeabilityProxy) (blockscout-verified)](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f)
- Aave v3 borrow $5.0M USDC by [0x1b36…1cd6](https://etherscan.io/address/0x1b36972588d214aea7b8f5322f349246bf571cd6) ([0x842c…e650](https://etherscan.io/tx/0x842cc08ed8f60c2f9a2076cae9cb784607a91923b0fdf39142af39183398e650)): $5.0M → [0x2835…62b1](https://etherscan.io/address/0x28355886a65848488cf0a3646fca395db0a762b1)
- Aave v3 withdraw $4.5M cbBTC by [0x933a…2833](https://etherscan.io/address/0x933adedd85824da75ec8a334a7907e69e7c02833) ([0xaf67…bf43](https://etherscan.io/tx/0xaf6791563c6692698d251fecf2e7f8d9b1ba7a14df6d33b1e049ae057611bf43)): $4.5M → [0xb397…c123](https://etherscan.io/address/0xb3973d459df38ae57797811f2a1fd061da1bc123)
- SparkLend borrow $4.0M USDS by [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) ([0xefc8…2b76](https://etherscan.io/tx/0xefc8f23fd31078622c2b0928bb20d307619e276b3250fe1417f7be16b5ed2b76)): $4.0M → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)
- Aave v3 borrow $4.0M WETH by [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) ([0x1361…d002](https://etherscan.io/tx/0x1361f6390c8fd91d285c7ab57f68f52699bb0cd64b6645e18bea79cbd72ed002)): $3.5M → [0x59cd…71db](https://etherscan.io/address/0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db); $886k → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb); $8.9M → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb)
- SparkLend withdraw $4.0M wstETH by [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) ([0x1361…d002](https://etherscan.io/tx/0x1361f6390c8fd91d285c7ab57f68f52699bb0cd64b6645e18bea79cbd72ed002)): $4.4M → [0x0b92…9371](https://etherscan.io/address/0x0b925ed163218f6662a35e0f0371ac234f9e9371); $494k → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb)
- Aave v3 borrow $3.8M USDC by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x4a4b…66cd](https://etherscan.io/tx/0x4a4b07f549caa08413c90ff2c48993c20353e6cc5c4959ddb5cc922df41166cd)): $3.8M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $3.8M → [Aave v3 aEthUSDC — the reserve's aToken; symbol() read on chain (chain-read)](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c); $49k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $49k → [Aave v3 aEthUSDC — the reserve's aToken; symbol() read on chain (chain-read)](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c)
- Aave v3 withdraw $3.8M USDT by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x3a3a…fbfa](https://etherscan.io/tx/0x3a3aa5ef2bb59f903c0b05b5aad8646e85333c3917291f21663a7b458958fbfa)): $16k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $3.8M → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a); $3.8M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90)
- SparkLend withdraw $3.5M USDT by [0x176c…e9e2](https://etherscan.io/address/0x176caf15f1793fc16898458e0ba295ec6523e9e2) ([0x4651…020a](https://etherscan.io/tx/0x465191f21319acdf9e069091d97d4946559b6e88a7d03b541945987f1972020a)): $3.5M → [0x310b…afaa](https://etherscan.io/address/0x310b7ea7475a0b449cfd73be81522f1b88efafaa)
- Aave v3 borrow $2.0M USDC by [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) ([0xc32c…aedc](https://etherscan.io/tx/0xc32cf5a1adf66b30e92779bc18271b414b89598ef87843943d6d4a0e9ddfaedc)): $470k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996); $1.5M → [0x3bbc…e0ec](https://etherscan.io/address/0x3bbcb84fcde71063d8c396e6c54f5dc3d19ee0ec)
- Aave v3 borrow $1.6M WETH by [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) ([0x100d…9776](https://etherscan.io/tx/0x100da1a49670cc42e57a88f723d4c9c2f824f4cfba57190eb23a811e51c59776)): $186k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $61k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $35k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $183k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 borrow $1.3M USDT by [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) ([0x9a1d…198d](https://etherscan.io/tx/0x9a1d73a9c7ebc687b93c07487794af59759ccc31e19e1180a3962bb80f2c198d)): $1.3M → [LayerZero OFT adapter (USDT0) (known-canonical)](https://etherscan.io/address/0x6c96de32cea08842dcc4058c14d3aaad7fa41dee)
- Aave v3 withdraw $1.1M weETH by [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) ([0x32ae…47fa](https://etherscan.io/tx/0x32ae10f66257119db47fcf6a71f335a049f342ca27f6a6935a135e0638ea47fa)): $1.1M → [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9); $1.1M → [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9)
- Aave v3 withdraw $1.1M weETH by [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) ([0x94a9…9e15](https://etherscan.io/tx/0x94a9317fea28ce5d84ebc6816fd17f68f8b2ec4ddb3a8a23fc382cde2bd59e15)): $1.1M → [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9)
- Aave v3 borrow $1.1M USDT by [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) ([0x68b1…2895](https://etherscan.io/tx/0x68b114486500288e3d665a2d9fdb31fe2bf9f90c7cfaa1f526faec43a1682895)): $257k → [LayerZero OFT adapter (USDT0) (known-canonical)](https://etherscan.io/address/0x6c96de32cea08842dcc4058c14d3aaad7fa41dee); $804k → [LayerZero OFT adapter (USDT0) (known-canonical)](https://etherscan.io/address/0x6c96de32cea08842dcc4058c14d3aaad7fa41dee)
- Aave v3 withdraw $996k sUSDe by [0x01b3…eaf7](https://etherscan.io/address/0x01b3ba0aa49c3daa72e25031bcd1b4029cf8eaf7) ([0x996b…0696](https://etherscan.io/tx/0x996b89abb063e5b59e1b6236d89d8e0c5c337aedb11888c7ddeaa4c7b9c60696)): $383k → [0x5e20…3131](https://etherscan.io/address/0x5e204cf45560a495988b5bccfd7347682c473131); $613k → [zero address (mint/burn) (known-canonical)](https://etherscan.io/address/0x0000000000000000000000000000000000000000)
- Aave v3 withdraw $900k sUSDe by [0x53fc…c6e0](https://etherscan.io/address/0x53fc326bfb5eadf013a6ca254cb5b4ded15ac6e0) ([0xeac4…05ce](https://etherscan.io/tx/0xeac45fce9762e8a7fbaec19a6f48c22ac1cdea899056f9830d7dc4ed4b7f05ce)): $829k → [0x0827…2085](https://etherscan.io/address/0x082738d007001080a00099a000004f3006152085); $70k → [0x6b57…401a](https://etherscan.io/address/0x6b579bacffea19b002271d448a62b161f754401a)
- Aave v3 withdraw $756k WETH by [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ([0x4d45…fe10](https://etherscan.io/tx/0x4d45503a42db1ee71f951896e58af9292f7b52926ab490dac5332fb72119fe10)): $756k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- SparkLend borrow $740k USDS by [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) ([0x18ad…8549](https://etherscan.io/tx/0x18ad2d1fbbbc3bf604bb476305bd5858b970bf2b8d33a3dce8e12785e74d8549)): $740k → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| Aave v3 | [0x4f87…0545](https://etherscan.io/address/0x4f87de7d21aef48090958f7342e1f69dff790545) | $193.3M | $173.3M | 1.060 | 5.6% |
| Aave v3 | [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) | $117.9M | $103.2M | 1.062 | 5.8% |
| SparkLend | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | $127.4M | $45.6M | 2.404 | 58.4% |
| Aave v3 | [0x1b36…1cd6](https://etherscan.io/address/0x1b36972588d214aea7b8f5322f349246bf571cd6) | $52.9M | $31.1M | 1.359 | 26.4% |
| Aave v3 | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | $24.7M | $22.1M | 1.028 | 2.7% |
| Aave v3 | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | $15.3M | $13.7M | 1.057 | 5.4% |
| Aave v3 | [0x418a…8888](https://etherscan.io/address/0x418aa6bf98a2b2bc93779f810330d88cde488888) | $16.3M | $7.5M | 1.802 | 44.5% |
| Aave v3 | [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | $7.4M | $6.8M | 1.035 | 3.3% |
| Aave v3 | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | $116.3M | $5.5M | 17.468 | 94.3% |
| Aave v3 | [0xd480…6d6a](https://etherscan.io/address/0xd480bb579f61edf044d0e86e33cb72310c816d6a) | $5.0M | $4.6M | 1.026 | 2.5% |
| Aave v3 | [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) | $6.9M | $4.0M | 1.379 | 27.5% |
| Aave v3 | [0xe904…672f](https://etherscan.io/address/0xe904a30cb6b54cd8e436edb7f0802573d2b5672f) | $5.4M | $2.1M | 2.156 | 53.6% |
| Aave v3 | [0x4c38…2d07](https://etherscan.io/address/0x4c38ac78bfdda318bd6f15312b34585b0ca72d07) | $2.0M | $701k | 2.250 | 55.6% |
| Aave v3 | [0x12bc…1711](https://etherscan.io/address/0x12bc3378994d0fabd0cc37199c3d9027ce751711) | $1.0M | $447k | 1.822 | 45.1% |
| Aave v3 | [0x7852…1a7c](https://etherscan.io/address/0x7852f22cefa8bd0d6a38a6dc3f76e6e88c091a7c) | $2 | $1 | 1.726 | 42.1% |
| Aave v3 | [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) | $193.3M | $0 | ∞ | – |
| SparkLend | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | $54.1M | $0 | ∞ | – |
| Aave v3 | [0x2906…715a](https://etherscan.io/address/0x29065a4c1f2f20d1e263930088890d6f49fe715a) | $11.5M | $0 | ∞ | – |
| Aave v3 | [0x12bc…663e](https://etherscan.io/address/0x12bc7befc3035f64cdc8b16a91d74d6e816d663e) | $11.7M | $0 | ∞ | – |
| Aave v3 | [0x933a…2833](https://etherscan.io/address/0x933adedd85824da75ec8a334a7907e69e7c02833) | $107k | $0 | ∞ | – |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| SparkLend | [0x176c…e9e2](https://etherscan.io/address/0x176caf15f1793fc16898458e0ba295ec6523e9e2) | $0 | $0 | ∞ | – |
| Aave v3 | [0xf78e…e2f3](https://etherscan.io/address/0xf78e6d431e5e51d7a63eb461021408b9b2d6e2f3) | $3.0M | $0 | ∞ | – |
| Aave v3 | [0xbd42…9b9f](https://etherscan.io/address/0xbd42f7311b4c13ce003c44428060c4564c469b9f) | $2.0M | $0 | ∞ | – |
| Aave v3 | [0x8d48…578b](https://etherscan.io/address/0x8d482fa571b8994252d18391d37990343fa3578b) | $1.5M | $0 | ∞ | – |

Liquidations: Aave v3 [0x1e8c…4c1d](https://etherscan.io/address/0x1e8c1f860f8d6f8eb52a85964d601c4769ac4c1d) debt $1, collateral $1 ([0xfd76…c427](https://etherscan.io/tx/0xfd76e2f691f2b18e4116d41d7842c7717b77674d3092827d58daad3dc6a9c427)).


Flash loans (events): BalFlash 1972 ($83.7M), MorphoFlash 13 ($15k).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a): 6 transactions, largest leg $31.0M, gross $178.7M; legs: WETH withdraw $178.7M, USDT withdraw $0
- Aave v3 account [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb): 4 transactions, largest leg $756k, gross $1.8M; legs: WETH withdraw $1.8M
- Aave v3 account [0xe947…d90f](https://etherscan.io/address/0xe947e01a0c8a15d84b1285258cd0b1788f81d90f): 1 transactions, largest leg $1108, gross $1108; legs: USDT borrow $1108
- Aave v3 account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588): 2 transactions, largest leg $544, gross $1087; legs: AAVE withdraw $1087

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 1123 | $32.5M | 0.999721 | 0.999673 – 0.999797 | 0.999857 | -1.4 bps |
| USDS | 411 | $21.9M | 1 | 0.999943 – 1.00005 | 1 | +0.0 bps |
| USDe | 308 | $9.6M | 0.999829 | 0.999686 – 0.99992 | 1 | -1.7 bps |
| DAI | 99 | $8.3M | 1.00001 | 0.999833 – 1.00007 | 0.999666 | +3.5 bps |
| crvUSD | 231 | $7.5M | 0.999782 | 0.999672 – 0.999947 | 1 | -2.2 bps |
| sUSDe | 161 | $5.1M | 1.24617 | 1.24595 – 1.24648 | 1.24706 | -7.1 bps |
| USDG | 270 | $5.0M | 1.00003 | 0.999904 – 1.00027 | 1 | +0.3 bps |
| AUSD | 38 | $3.6M | 0.999963 | 0.99987 – 1.0001 | 1 | -0.4 bps |
| PYUSD | 47 | $2.9M | 1.00004 | 0.999791 – 1.00005 | 1 | +0.4 bps |
| RLUSD | 19 | $1.2M | 1.00019 | 0.999969 – 1.0002 | 1 | +1.9 bps |
| frxUSD | 73 | $1.0M | 0.999947 | 0.999577 – 1.00001 | 1 | -0.5 bps |
| USD1 | 24 | $761k | 0.999671 | 0.999595 – 1.00008 | 1 | -3.3 bps |
| sDAI | 4 | $468k | 1.18132 | 1.18124 – 1.18149 | 1.17988 | +12.3 bps |
| PEPE | 128 | $385k | 3.60097e-06 | 3.57714e-06 – 3.62393e-06 | – | – |
| SKY | 214 | $312k | 0.0685368 | 0.0678458 – 0.0691878 | – | – |
| weETH | 14 | $290k | 2731.2 | 2730.64 – 2731.25 | 2731.29 | -0.3 bps |
| wstETH | 95 | $287k | 3078.1 | 3072.65 – 3080.58 | 3084.12 | -19.5 bps |
| USDtb | 7 | $231k | 1.00009 | 0.999869 – 1.0001 | 1 | +0.9 bps |
| sUSDS | 8 | $131k | 1.10937 | 1.10899 – 1.11189 | 1.10885 | +4.7 bps |
| rETH | 23 | $121k | 2893.68 | 2893.31 – 2894.49 | 2899.86 | -21.3 bps |
| CVX | 62 | $113k | 2.24277 | 2.22362 – 2.25403 | – | – |
| SOPH | 86 | $93k | 0.00989594 | 0.00840771 – 0.0106718 | – | – |
| PENDLE | 61 | $72k | 2.22128 | 2.19451 – 2.24785 | – | – |
| GHO | 31 | $57k | 0.999143 | 0.998765 – 0.999223 | 1 | -8.6 bps |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 194 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDT | $412.9M | $381.3M | $31.6M |
| USDC | $347.6M | $385.5M | $-37.9M |
| ETH | $178.1M | $180.2M | $-2.1M |
| RLUSD | $8.8M | $7.3M | $1.5M |
| USDG | $6.9M | $8.8M | $-1.9M |
| WBTC | $1.7M | $8.2M | $-6.6M |
| LINK | $3.3M | $5.6M | $-2.3M |
| UNI | $4.1M | $4.6M | $-531k |
| USD1 | $5.3M | $2.5M | $2.8M |
| EURC | $2.0M | $3.1M | $-1.1M |
| FDUSD | $1.0M | $1.8M | $-797k |
| cbBTC | $275k | $2.1M | $-1.8M |

By label: Coinbase 11 (model-memory) in $179.0M / out $199.2M; Binance 14 (model-memory) in $311.0M / out $61.0M; hot wallet (behaviour, day study) in $121.8M / out $136.1M; Coinbase 10 (model-memory) in $124.0M / out $124.6M; hot wallet (day study, unidentified) (model-memory) in $85.7M / out $59.2M; Bitfinex 2 (model-memory) in $42.1M / out $101.0M; Bitget (model-memory) in $50.4M / out $47.5M; Binance 16 (model-memory) in $0 / out $73.9M; Gate.io (model-memory) in $29.3M / out $29.2M; Binance 15 (model-memory) in $0 / out $49.3M; Binance 17 (model-memory) in $0 / out $37.9M; Binance 18 (model-memory) in $0 / out $34.1M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25928521 | WBTC | $436.6M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x1c31…907c](https://etherscan.io/tx/0x1c3198826c3af3ea8df4ff0f930c75d17909add76ca02a512b5e97baf39d907c) |
| 25928521 | WBTC | $436.6M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1c31…907c](https://etherscan.io/tx/0x1c3198826c3af3ea8df4ff0f930c75d17909add76ca02a512b5e97baf39d907c) |
| 25931440 | WBTC | $432.3M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x7a99…a6b7](https://etherscan.io/tx/0x7a992fd4991334bcbce8739ee3dc2d898ea52b74d6584f62daa2b77120cea6b7) |
| 25931440 | WBTC | $432.3M ×2 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x7a99…a6b7](https://etherscan.io/tx/0x7a992fd4991334bcbce8739ee3dc2d898ea52b74d6584f62daa2b77120cea6b7) |
| 25930974 | WBTC | $432.3M ×18 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xf58b…b300](https://etherscan.io/tx/0xf58bf674a17dfa04e8930e2bc8eb28e1b6b59e3f0639504bd883a2421068b300) |
| 25930974 | WBTC | $432.3M ×18 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xf58b…b300](https://etherscan.io/tx/0xf58bf674a17dfa04e8930e2bc8eb28e1b6b59e3f0639504bd883a2421068b300) |
| 25928551 | WBTC | $432.3M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x3f51…3590](https://etherscan.io/tx/0x3f51f183f02cccc5764623954c320834f578a2231ea46d09f9213f6ce2af3590) |
| 25928551 | WBTC | $432.3M ×2 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3f51…3590](https://etherscan.io/tx/0x3f51f183f02cccc5764623954c320834f578a2231ea46d09f9213f6ce2af3590) |
| 25928827 | USDC | $397.3M | [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) | [0xf1ed…56a8](https://etherscan.io/address/0xf1edbf98dda764ec51de3776371f0f7d6f6156a8) | [0xc70c…e50b](https://etherscan.io/tx/0xc70c84a4e5be96fbebbe362546a0f0a13a54d375306aca18b08b951fe214e50b) |
| 25928939 | USDC | $397.3M | [0xf1ed…56a8](https://etherscan.io/address/0xf1edbf98dda764ec51de3776371f0f7d6f6156a8) | [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) | [0x0cc0…a11c](https://etherscan.io/tx/0x0cc0004bf3138a8bf649c8a183d95f4e00cb2e6a36c082a01f0b6eec82eba11c) |
| 25928815 | DAI | $257.8M | [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042) | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0x1af1…be17](https://etherscan.io/tx/0x1af128aa5c4916ef36b368861637330bddc625695343ff2b38d7d3210fdbbe17) |
| 25928799 | sUSDS | $245.6M | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928967 | sUSDS | $245.6M | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928967 | USDS | $245.6M | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928967 | USDS | $245.6M | [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0) | [0xa393…7fbd](https://etherscan.io/address/0xa3931d71877c0e7a3148cb7eb4463524fec27fbd) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928799 | USDS | $245.6M | [0xa393…7fbd](https://etherscan.io/address/0xa3931d71877c0e7a3148cb7eb4463524fec27fbd) | [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928799 | USDS | $245.6M | [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0) | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928799 | USDS | $245.6M | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928967 | USDC | $245.5M | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928967 | USDC | $245.5M | [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0) | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928967 | USDC | $245.5M | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0x3730…7341](https://etherscan.io/address/0x37305b1cd40574e4c5ce33f8e8306be057fd7341) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928951 | USDC | $245.5M | [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | [0x2904…6367](https://etherscan.io/tx/0x2904ff6ad52b11a22b49ab63d174fe58df92c7561d97caa7d76ce24404f06367) |
| 25928799 | USDC | $245.5M | [0x3730…7341](https://etherscan.io/address/0x37305b1cd40574e4c5ce33f8e8306be057fd7341) | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928809 | USDC | $245.5M | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) | [0xd1c6…280a](https://etherscan.io/tx/0xd1c609f13d752db4f57f8293d5dbc007885d9f522809f4dab6afa15ff742280a) |
| 25928967 | DAI | $245.5M | [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042) | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928967 | DAI | $245.5M | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0xb41a…8d50](https://etherscan.io/tx/0xb41ab3f752365c6581b22bfe4ae27e1f5fc6297c9f01496e8d3c773871f18d50) |
| 25928799 | DAI | $245.5M | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928799 | DAI | $245.5M | [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) | [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042) | [0xab83…46d6](https://etherscan.io/tx/0xab83cc5d6dfaedf25bb851b6d8ec73c589d113112476fb4be68a26a3543c46d6) |
| 25928970 | DAI | $244.9M | [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) | [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042) | [0x583d…d28a](https://etherscan.io/tx/0x583d36097fad8e17c35a4699cb993a9e1c74247478a51e8ba19fc592b6abd28a) |
| 25928960 | USDC | $151.8M | [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) | [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) | [0xdc33…6e03](https://etherscan.io/tx/0xdc335da051c4d19c2eb7b27aac68edb78dffc83faade5b162c231f4dead86e03) |

Round trips (≥ $10M out and back within the window): $245.6M USDS from [0xa393…7fbd](https://etherscan.io/address/0xa3931d71877c0e7a3148cb7eb4463524fec27fbd) via [0xd0a6…39e0](https://etherscan.io/address/0xd0a61f2963622e992e6534bde4d52fd0a89f39e0), back after 34 min; $245.6M sUSDS from [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) via [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000), back after 34 min; $245.5M DAI from [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) via [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c), back after 34 min; $245.5M DAI from [0xa188…f98c](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c) via [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042), back after 34 min; $151.8M USDC from [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) via [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149), back after 30 min; $245.5M USDC from [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) via [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18), back after 29 min; $151.8M USDC from [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) via [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18), back after 27 min; $397.3M USDC from [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) via [0xf1ed…56a8](https://etherscan.io/address/0xf1edbf98dda764ec51de3776371f0f7d6f6156a8), back after 23 min; $48.7M USDT from [0xe7df…c92f](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f) via [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e), back after 80 min; $48.7M USDT from [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) via [0xe2e7…c372](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372), back after 80 min; $18.0M USDT from [0xe7df…c92f](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f) via [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e), back after 5 min; $18.0M USDT from [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) via [0xe2e7…c372](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372), back after 5 min.


Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0x75ed…ec28](https://etherscan.io/address/0x75ed83132a7c7af97dbe6d29efa396885e07ec28) | USDT → ETH | 4 | $315k | $79k | 7476s | 0.26 | 0.10 | uniswap_v4 4 |
| [0x16b5…a4e2](https://etherscan.io/address/0x16b58403d2768988c82eada42330785e1c1aa4e2) | PYUSD → USDS | 6 | $314k | $54k | 360s | 0.38 | 0.09 | uniswap_v4 6 |
| [Relay solver / USDG inventory wallet (takes 100% of RelayDepository payouts on Ethereum and Robinhood Chain; Paxos mint-and-redeem counterparty on both) (etherscan-verified)](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) | USDT → USDS | 4 | $319k | $68k | 9552s | 0.14 | 0.45 | uniswap_v4 4 |
| [0xdd04…72f2](https://etherscan.io/address/0xdd0400a6bcea1ce4e5db6f4c0be4c226193672f2) | WETH → weETH | 4 | $169k | $46k | 2136s | 0.29 | 0.31 | uniswap_v3 2, curve 2 |
| [0x0d22…b386](https://etherscan.io/address/0x0d2237fd78538b7829be568aebf44b07d670b386) | DAI → USDT | 4 | $300k | $75k | 744s | 0.39 | 0.33 | uniswap_v3 4 |
| [0xbaa3…0843](https://etherscan.io/address/0xbaa3ef11659d347aae75c7bb67e29f1f8bb90843) | WBTC → USDT | 4 | $140k | $28k | 3912s | 0.33 | 0.48 | uniswap_v3 4 |
| [0x0250…b9b6](https://etherscan.io/address/0x025080f14aa3305049f9ce08d7b92368d54cb9b6) | crvUSD → frxUSD | 5 | $300k | $45k | 168s | 0.53 | 0.48 | curve 5 |
| [0x0250…b9b6](https://etherscan.io/address/0x025080f14aa3305049f9ce08d7b92368d54cb9b6) | USDT → crvUSD | 5 | $300k | $45k | 168s | 0.53 | 0.48 | curve 5 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25929021 | uniswap_v2_like | 0x8e9d…cf3e → WETH | $9.9M | [0x666c…f486](https://etherscan.io/address/0x666c568fc0ae77ed624330bb5b54d5ca7426f486) | [0x3125…8137](https://etherscan.io/tx/0x312514c0e677bd00b7a62d889a8dd9c48fbc806acd7ce4ce7f233c7001ab8137) |
| 25931314 | uniswap_v2_like | 0x8e9d…cf3e → WETH | $9.9M | [0x5c09…33a9](https://etherscan.io/address/0x5c096ef846447cb935c5d247e4ab2a867ecc33a9) | [0x227d…e5c8](https://etherscan.io/tx/0x227de567bc351cd339b45d2a07b5fb320e2bf70cb18030fe89c22e9cce2de5c8) |
| 25929021 | uniswap_v2_like | WETH → 0x8e9d…cf3e | $9.9M | [0x666c…f486](https://etherscan.io/address/0x666c568fc0ae77ed624330bb5b54d5ca7426f486) | [0x3125…8137](https://etherscan.io/tx/0x312514c0e677bd00b7a62d889a8dd9c48fbc806acd7ce4ce7f233c7001ab8137) |
| 25931314 | uniswap_v2_like | WETH → 0x8e9d…cf3e | $9.9M | [0x5c09…33a9](https://etherscan.io/address/0x5c096ef846447cb935c5d247e4ab2a867ecc33a9) | [0x227d…e5c8](https://etherscan.io/tx/0x227de567bc351cd339b45d2a07b5fb320e2bf70cb18030fe89c22e9cce2de5c8) |
| 25931323 | uniswap_v4 | USDC → USDT | $3.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x4a4b…66cd](https://etherscan.io/tx/0x4a4b07f549caa08413c90ff2c48993c20353e6cc5c4959ddb5cc922df41166cd) |
| 25931323 | uniswap_v4 | USDT → USDC | $3.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x3a3a…fbfa](https://etherscan.io/tx/0x3a3aa5ef2bb59f903c0b05b5aad8646e85333c3917291f21663a7b458958fbfa) |
| 25930756 | uniswap_v4 | USDT → USDC | $2.1M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x751f…8c21](https://etherscan.io/tx/0x751fb08eab234d27a7adac5937dff48affd723aec829ea12350894666cd18c21) |
| 25930756 | uniswap_v4 | USDC → USDT | $2.1M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x7a2b…457b](https://etherscan.io/tx/0x7a2b1e438ae92c6f5d4ede2b4a9cd1edf996aeb1928741e3b8e459073f9c457b) |
| 25930904 | uniswap_v4 | USDC → USDT | $2.0M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xd2a3…aac5](https://etherscan.io/tx/0xd2a3ba68ab937807cf1efa21985f06d45badaa84e254514d4b845fd587c5aac5) |
| 25930904 | uniswap_v4 | USDT → USDC | $2.0M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x07e0…3dde](https://etherscan.io/tx/0x07e05d33abb65eae266b124268648d5d2dd6b0f837d71c604848fe23a9993dde) |
| 25930183 | curve | USDT → DAI | $1.5M | [0x75ed…ec28](https://etherscan.io/address/0x75ed83132a7c7af97dbe6d29efa396885e07ec28) | [0x9270…3fec](https://etherscan.io/tx/0x9270ec7e9d99bcd7878490cc6e1b501489d24d0d2f2ae3f7603d98af07d43fec) |
| 25929482 | curve | USDT → DAI | $1.2M | [0x75ed…ec28](https://etherscan.io/address/0x75ed83132a7c7af97dbe6d29efa396885e07ec28) | [0x1945…ff95](https://etherscan.io/tx/0x19456b14af46c58dd6c016ca4521310806c6d32202ef87e79bd53d162c4aff95) |
| 25930007 | curve | USDT → USDC | $1.2M | [0x75ed…ec28](https://etherscan.io/address/0x75ed83132a7c7af97dbe6d29efa396885e07ec28) | [0x9b71…f2a8](https://etherscan.io/tx/0x9b7194d2bbb7670ee8fefe64f6fafadee40e90fd262aacd40d0e81d2e073f2a8) |
| 25930370 | curve | USDT → USDC | $1.2M | [0x75ed…ec28](https://etherscan.io/address/0x75ed83132a7c7af97dbe6d29efa396885e07ec28) | [0x8cfe…22cd](https://etherscan.io/tx/0x8cfe0a441290930ec9da32356e078b2708664c1ed194991d62826142721422cd) |

## E. Bridges, issuance, staking

Outbound: $104.4M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $43.2M (665).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| CCTP | USDC | domain 15 | 41 | $11.6M | 0x65c340eb0688… $6.1M |
| OFT | USDC | BNB | 22 | $11.4M | – |
| CCTP | USDC | Polygon | 93 | $10.0M | 0xf70da97812cb… $7.0M |
| CCTP | USDC | Arbitrum | 100 | $7.9M | 0x65c340eb0688… $5.0M |
| OFT | USDT | eid 30383 | 9 | $6.9M | – |
| CCTP | USDC | Avalanche | 15 | $6.0M | 0x65c340eb0688… $4.5M |
| OFT | USDG | eid 30416 | 44 | $5.7M | – |
| OFT | USDG | eid 30274 | 9 | $5.5M | – |
| CCTP | USDC | domain 19 | 51 | $5.4M | 0x28355886a658… $5.0M |
| CCTP | USDC | Aptos | 6 | $5.0M | 64c815fa7c79a1… $5.0M |
| OFT | USDe | eid 30383 | 27 | $4.6M | – |
| OFT | USDT | Polygon | 10 | $3.3M | – |
| CCTP | USDC | Base | 228 | $3.2M | 0x000000000001… $866k |
| OFT | USDT | eid 30420 | 37 | $3.2M | – |
| CCTP | USDC | Solana | 106 | $2.6M | f90556882b2fe6… $1.2M |
| OFT | USDe | eid 30416 | 4 | $2.3M | – |
| OFT | USDe | Base | 1 | $1.4M | – |
| OFT | USDe | eid 30343 | 6 | $1.1M | – |
| OFT | USDT | eid 30390 | 2 | $1.0M | – |
| OFT | AUSD | eid 30390 | 5 | $1.0M | – |

Issuance totals: USDC burn $129.6M (785); USDC mint $140.1M (1194). Largest: USDC mint $50.0M ([0xb51b…0653](https://etherscan.io/tx/0xb51b4e2b8e96b2e8d0118f703d23839eb4b6365a83978a1e7ceef60ea78d0653)); USDC burn $7.8M ([0xbcb0…4e77](https://etherscan.io/tx/0xbcb0f4bcfa94c61ef252db30fded06cf95b9e7b4e559065e28b95ba02f114e77)); USDC mint $7.8M ([0xe0fb…7b94](https://etherscan.io/tx/0xe0fb76cb8febf41c063c0dd3b9988a410748f064c71530835bad0dad31e17b94)); USDC mint $7.0M ([0x50db…d649](https://etherscan.io/tx/0x50db340fb152ee089b4a05d70d2c7e542ca30536d64c17682082f6f6d4ffd649)); USDC burn $5.2M ([0x1548…c44d](https://etherscan.io/tx/0x154812473fcd50e460786498e3a278295a7dd12a234cf6d1142cdb84515bc44d)).


WETH wrapped 37195 ETH, unwrapped 33617 ETH; Lido staked 1683.3 ETH, withdrawal requests 925.0 ETH; sUSDe cooldowns 29 for $9.9M.


## F. Gas market and block production

Base fee 0.05 → 0.063 gwei (min 0.034, median 0.049, max 0.098); blocks 51% full; median tip 0.045 gwei; 4.5% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 1417,  Quasar (quasar.win)  609, Eureka (eurekabuilder.xyz) 335, BuilderNet 299, gethgo1.26.4linux 52, gethgo1.25.10linux 24.


Most active senders: [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 9100, [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 4683, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 3494, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 3461, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 3053, [Relay solver / USDG inventory wallet (takes 100% of RelayDepository payouts on Ethereum and Robinhood Chain; Paxos mint-and-redeem counterparty on both) (etherscan-verified)](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) 2588, [Binance 17 (model-memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 2508, [Binance 18 (model-memory)](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 2317, [hot wallet (behaviour, day study)](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460) 2268, [0x59aa…e16b](https://etherscan.io/address/0x59aab1bd0d26290274398c07b55955c15425e16b) 2258.


Intent fills: OneInchFilled 1975, CoWTrade 1281, UniXFill 368. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

