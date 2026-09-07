# Ethereum mainnet live scan: 2026-09-07T21:27:35+00:00 to 2026-09-07T23:27:35+00:00 UTC

Blocks 25928160 to 25928758 (599 blocks, 2.00 h), 141,411 transactions, 491,580 logs. Prices at head block 25928857: ETH $2486, BTC $79k. Generated 2026-09-07T23:55:33+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

# The dollar-yield surface, and what it is worth at size

Ethereum mainnet, **2026-09-07 21:27:35 to 23:27:35 UTC**, blocks 25,928,160–25,928,758 (599 blocks, 141,411
transactions, 491,580 logs) [[verify: blocks]] [[verify: transactions]] [[verify: logs]], plus head reads at
23:40 UTC. Written by Claude on 2026-09-08. Every number is in `analysis.json`, `head_state.json` or `detectors.json`;
`live_scan verify --out research/2026-09-08/live_2h` re-derives thirteen of them from the raw blocks through an
independent path and all thirteen pass. Nothing was signed or broadcast.

The window itself is unremarkable and that is useful: base fee 0.035–0.084 gwei (median 0.051), no liquidations,
exchange net flow −$5.5M in stables and −$3.0M in ETH [[verify: exchange-net-stables]] [[verify: exchange-net-eth]],
$7.1M of USDC minted against $6.8M burned [[verify: usdc-mint]] [[verify: usdc-burn]]. A quiet tape is the right
place to measure a *standing* surface, because nothing in it is a reaction to anything.

## 1. Two dollar markets on mainnet beat simply holding the savings rate. Both are small.

The right benchmark for a dollar is not the same dollar on another venue — it is the dollar an issuer will pay you for
in unlimited size at no venue risk. That is Sky's savings rate, **3.60%**. Measured against it, at the head:

| asset | venue | supply APR | vs savings rate | supplied | utilisation |
|---|---|---:|---:|---:|---:|
| **USDtb** | **Aave v3** | **8.05%** | **+4.45pp** | $15.4M | 83.2% |
| **USDC** | **Compound v3** | **5.69%** | **+2.09pp** | $374.4M | 90.8% |
| PYUSD | Aave v3 | 3.88% | +0.28pp | $7.6M | 87.8% |
| USDT | Aave v3 | 3.60% | +0.00pp | $2,962.9M | 93.6% |
| USDC | Aave v3 | 3.59% | −0.01pp | $2,156.3M | 100.0% |
| USDC | SparkLend | 3.54% | −0.06pp | $25.6M | 92.2% |
| DAI | Aave v3 | 3.07% | −0.53pp | $131.6M | 86.7% |
| USDT | Compound v3 | 3.00% | −0.60pp | $185.3M | 83.4% |
| USDT | SparkLend | 2.62% | −0.98pp | $391.8M | 82.8% |
| USDS | SparkLend | 2.32% | −1.28pp | $748.0M | 65.6% |
| USDe | Aave v3 | 1.72% | −1.88pp | $652.3M | 39.0% |
| PYUSD | SparkLend | 0.59% | −3.01pp | $100.0M | 16.7% |

Twenty-seven dollar-denominated reserves across Aave, SparkLend and Compound; **two of them pay more than doing
nothing.** Roughly $8.5B of supplied dollars sits in reserves paying *less* than the issuer's own savings rate. That is
the single most useful thing in this note, and it reframes every cross-venue rate finding this project has produced:
a gap between two venues is only an opportunity if the higher one clears the savings rate, and most do not.

Two of the recurring findings in the ledger fail exactly that test. "PYUSD pays 3.29pp more on Aave than SparkLend" is
true and worth **28bps** over the actual alternative, because SparkLend's PYUSD reserve is 16.7% utilised and paying
almost nothing. "DAI pays 0.61pp more on Aave than SparkLend" is a gap between 3.07% and 2.46%, **both below the
savings rate**. The detector was measuring the emptiness of the low venue.

## 2. The capacity of the best of them is $1.4M, not $94M.

Compound v3's USDC Comet sits at **90.77% utilisation against a kink at exactly 90.0%**. Read directly from the
contract's own `getSupplyRate`:

| utilisation | supply APR |
|---:|---:|
| 89.0% | 3.20% |
| 89.5% | 3.22% |
| **90.0% (kink)** | **3.24%** |
| 90.5% | 4.84% |
| 90.77% (now) | 5.70% |
| 91.0% | 6.44% |
| 92.0% | 9.63% |

The whole 5.69% headline lives in 0.77 percentage points of utilisation. Supplying into it moves you down that cliff:

| you supply | resulting utilisation | your APR | earned over the savings rate, per year |
|---:|---:|---:|---:|
| $100k | 90.74% | 5.61% | $2,012 |
| $1.0M | 90.53% | 4.92% | $13,169 |
| **$1.25M** | **90.46%** | **4.72%** | **$14,054** |
| $5.0M | 89.57% | 3.22% | −$18,774 |
| $50M | 80.07% | 2.88% | −$358,708 |

**$1.25M is the entire opportunity, and it is worth about $14,000 a year.** At $5M you are earning less than you would
have earned holding USDS and doing nothing.

The same arithmetic applied to Aave's USDtb reserve (IRM read on-chain: optimal 80%, base 0, slope1 4%, slope2 50%,
reserve factor 20%) gives **$227k of capacity worth $5.4k a year**. $626k of new supply takes utilisation to the kink
and the rate from 8.05% to 2.56% — below the savings rate.

So the honest summary of the mainnet dollar surface tonight: **the best two rates on the board are jointly worth about
$19,000 a year.** Everything larger pays less than the risk-free dollar.

## 3. Aave's $2.16B USDC reserve had $503 of exit liquidity at 23:41 UTC.

Caught live, read straight from the contract:

```
23:41:12 UTC   Aave v3 USDC   supply 12.87%   borrow 14.30%
supplied 2,156,510,591   borrowed 2,156,510,088   utilisation 1.000000   available 503
```

Supply fell from $2,308M to $2,156M while borrows did not move: an account withdrew about **$152M of USDC supply**,
taking a two-billion-dollar reserve to exactly 100% utilisation. This is the daily 23:30–00:10 UTC balance routine this
repo has been tracking since 2026-09-05, and it is the first time it has been captured at the head rather than
reconstructed from logs afterwards.

The 12.87% supply rate it prints is not an opportunity. It exists for about half an hour, and over that half hour
$10M of supply earns roughly **$55** more than it would at the savings rate. The finding is the other side of the same
fact: **for roughly thirty minutes every night, USDC cannot be withdrawn from Aave.** That is a hard operational
constraint on any strategy whose exit leg is that reserve — including the Compound-versus-Aave rotation above — and it
is now recorded as a risk on that strategy rather than as prose.

It is also a warning about every rate this system reads. A spot read of Aave USDC taken at 23:41 would have entered
the ledger as a 9.3-percentage-point cross-venue gap. The de-spiker caught it (`0.05pp on window medians`) — but only
after two bugs were fixed, below.

## 4. Three corrections to this system's own machinery, each of which changed a number

Written up because the loop's value is in what it catches, including in itself.

**The de-spiker was comparing supply rates against borrow medians.** `analysis.json` stores each rate point as
`[block, supply_apr, borrow_apr]`, and both `rate_dispersion` and the new detector read index 2 — the borrow rate —
when de-spiking a supply rate. It survived a shipped detector because both sides of the comparison were wrong in the
same direction, so the gap still looked plausible. Fixed: the USDT Aave-over-Spark gap went from 1.66pp to **0.98pp**.

**The venue pair was chosen on spot rates and then de-spiked.** During the nightly spike the highest USDC venue is
whichever reserve is momentarily starved, so the comparison became Aave-over-Spark, the de-spiker correctly called it
a spot artifact — and the real standing finding, Compound-over-Spark, was never compared at all. The spike did not
merely add a false finding; it **hid a true one**. Fixed by selecting the pair on de-spiked rates.

**Capacity was modelled with a smooth curve on markets that have a cliff.** `rate_dispersion` modelled dilution as
`r·S/(S+X)`, which cannot express a kink. On Compound USDC that reported **$93.8M of capacity worth $945k a year**
against a true **$1.4M worth $15k** — a 63x overstatement of the number that decides whether a strategy is worth
doing. Fixed by pricing against each venue's real model: Aave and SparkLend from the reserve's own IRM parameters,
Compound from its `getSupplyRate` sampled across utilisations at head time. The detector's ladder now reproduces the
on-chain reads to two decimal places.

Two supporting changes made those possible: the head now discovers reserves from `getReservesList()` instead of a
hardcoded fifteen-symbol list — which is why USDtb, the highest dollar rate on the board, was invisible to every size
check until today — and it fetches each reserve's IRM parameters, which had been silently returning nothing.

## 5. What is proposed, and what it is worth

The strategy book (`research/strategies.jsonl`, `scripts/strategies.py`) now holds every strategy this repo has
produced, each with legs, capacity, kill criteria and a quote series. Ranked at this window:

| strategy | status | net APR | capacity | quote age |
|---|---|---:|---:|---:|
| USDG captive-flow v4 LP | fork-proven | 15.80% | $150k | 28h |
| Sky savings rate over Aave USDS | monitored | 3.48% | $1B | current |
| Aave USDtb supply | proposed | 2.36% | $227k | current |
| PT-sUSDS fixed vs the savings rate | proposed | 1.37% | $1M | 35h |
| Compound v3 USDC over SparkLend | monitored | 1.05% | $1.4M | current |
| sUSDe cooldown redemption | fork-proven | standing bid | $600k | 35h |
| Morpho USDT borrow vs Aave | proposed | 0.91% | $24M | **stale** |

Two were retired on economics rather than on mechanism and are not shown: mainnet JIT liquidity (the entire field
nets ~$6k a year at a 10% win rate) and the StacyVault reward harvest ($7.42 a run — the bug is real and still
asserted by `verify`, and it pays nothing).

The shape of that table is the finding. **The largest edges are the smallest positions.** The 15.8% LP is a $150k
idea; the $1B-capacity idea pays 3.48% and is a savings account. Nothing in the book is simultaneously large and
mispriced, which is what an efficient dollar market is supposed to look like, and it is worth stating plainly rather
than implying otherwise by quoting headline rates.

**Only three of the seven have a quote a detector produced.** The other four were measured once in a dated session and
have not been re-measured since; the Morpho USDT borrow spread is already past its staleness threshold. That gives the
next round of work an ordering principle: write the detector that re-prices the highest strategy in the book that
nothing re-prices — the captive-flow LP first, then the Pendle fixed-versus-floating gap, then the sUSDe ask against
NAV.

## 6. Everything else in the window

- **Two atomic bot pairs passed $480M each through 7 transactions, ending exactly flat** (0x04ca7a7e, 0x26de7861 —
  the second returned $240,000,001 against $240,000,001 received, to the dollar). Both are contracts, neither is
  labelled, and their flow is not exchange flow.
- **Address poisoning continues** at the same background rate; `mass_distribution` again finds the 0.0003-USDT dust
  campaign, now at a smaller scale in a two-hour window.
- **JIT liquidity took $3.86 of pool fees** across 44 episodes — 0.06% of fees, consistent with the two 2026-09-07
  windows. Still not a tax on passive LPs.
- **No liquidations, no mislabelled-flow hits.** The address book survived this window without a contradiction, which
  it did not manage on either 2026-09-07 window.

## What is checked, and what is not

The `[[verify: id]]` markers name recipes in `scripts/verify.py` that re-derive that number from the raw blocks
through a path sharing no aggregation code with `analyze`. The rate table in section 1, the capacity ladders in
section 2 and the live blackout read in section 3 are head reads and direct contract calls, not window aggregates;
they carry no marker because no recipe re-derives them yet, and a `getSupplyRate` ladder is the obvious next check to
write. The Compound and Sky rates cannot be de-spiked at all — neither venue emits rate-update logs — so those two
rows are single readings by construction.


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 19 | $4.7M | – | $0 | – | – | – | – | – |
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 78 | $3.6M | $21 | $0 | $21 | $100.0B | 0.00% | 0.0% | 0.003% |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 1136 | $3.4M | $1695 | $0 | $1695 | $510.6M | 1.45% | 292.4% | 0.694% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 1744 | $3.1M | $309 | $1 | $308 | $67.5M | 1.99% | 402.1% | 1.725% |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 108 | $2.3M | $1139 | $0 | $1139 | $205.3M | 2.43% | 488.7% | 1.308% |
| [0x4dec…d69e](https://etherscan.io/address/0x4dece678ceceb27446b35c672dc7d61f30bad69e) | curve | USDC/crvUSD | ? | 33 | $2.1M | – | $0 | – | – | – | – | – |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 39 | $1.7M | $53 | $0 | $53 | $16.7B | 0.00% | 0.3% | 0.009% |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 231 | $1.3M | $12 | $0 | $12 | $39.9B | 0.00% | 0.0% | 0.004% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 103 | $1.2M | $3725 | $0 | $3725 | $1.8B | 0.91% | 183.2% | 0.278% |
| 0xb203…448b | uni v4 | sUSDe/USDT | 0.01% | 29 | $863k | $87 | $0 | $87 | $4.0B | 0.01% | 1.9% | 0.039% |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 1000 | $720k | $72 | $1 | $71 | $23.8M | 1.31% | 264.7% | 2.489% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 84 | $627k | $314 | $0 | $314 | $355.3M | 0.39% | 77.8% | 0.247% |
| [0x5b03…8e96](https://etherscan.io/address/0x5b03cccab7ba3010fa5cad23746cbf0794938e96) | curve | USDe/USDT | ? | 21 | $508k | – | $0 | – | – | – | – | – |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 200 | $426k | $213 | $0 | $213 | $57.8M | 1.61% | 324.5% | 0.656% |
| [0x5018…b61f](https://etherscan.io/address/0x5018be882dcce5e3f2f3b0913ae2096b9b3fb61f) | curve | 0x0857…d8f6/USDC | ? | 12 | $406k | – | $0 | – | – | – | – | – |
| [0x4068…bd59](https://etherscan.io/address/0x4068038ab5490063a3ead93b3712ed082e62bd59) | uni v3 | ICP/WETH | 0.05% | 248 | $377k | $188 | $9 | $180 | $26.3M | 2.99% | 602.1% | 4.765% |
| 0x9a5c…5167 | uni v4 | UNI/USDC | 0.35% | 63 | $358k | $1254 | $0 | $1254 | $24.0M | 22.90% | 4613.6% | 3.006% |
| 0xe500…a657 | uni v4 | USDC/WETH | 0.00% | 116 | $355k | $72 | $0 | $72 | $62.7M | 0.50% | 101.2% | 0.641% |
| [0xd51a…ae46](https://etherscan.io/address/0xd51a44d3fae010294c616388b506acda1bfaae46) | curve | WETH/USDT | ? | 140 | $341k | – | $0 | – | – | – | – | – |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.00% | 108 | $330k | $63 | $0 | $63 | $60.1M | 0.46% | 92.8% | 0.646% |
| 0x21c6…ca27 | uni v4 | ETH/USDC | 0.06% | 128 | $310k | $194 | $0 | $194 | $60.5M | 1.40% | 282.0% | 0.642% |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 88 | $306k | $31 | $0 | $31 | $50.1B | 0.00% | 0.1% | 0.002% |
| [0x1674…8d3a](https://etherscan.io/address/0x167478921b907422f8e88b43c4af2b8bea278d3a) | curve | sDAI/sUSDe | ? | 3 | $300k | – | $0 | – | – | – | – | – |
| [0x1d42…d801](https://etherscan.io/address/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801) | uni v3 | UNI/WETH | 0.30% | 109 | $291k | $873 | $0 | $873 | $18.9M | 20.19% | 4068.3% | 2.181% |
| 0x7233…ca73 | uni v4 | ETH/USDT | 0.06% | 129 | $275k | $172 | $0 | $172 | $52.1M | 1.44% | 290.5% | 0.638% |
| 0x8aa4…4e47 | uni v4 | USDC/USDT | 0.00% | 40 | $256k | $3 | $0 | $3 | $18.1B | 0.00% | 0.0% | 0.002% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 12 | $256k | $2 | $0 | $2 | $149.1B | 0.00% | 0.0% | 0.001% |
| [0xd0fc…6d78](https://etherscan.io/address/0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78) | uni v3 | UNI/USDC | 0.30% | 54 | $246k | $738 | $0 | $738 | $10.9M | 29.68% | 5981.3% | 3.013% |
| [0x73a3…b38b](https://etherscan.io/address/0x73a38006d23517a1d383c88929b2014f8835b38b) | uni v3 | tBTC/WBTC | 0.01% | 42 | $246k | $25 | $0 | $25 | $8.8B | 0.00% | 0.2% | 0.004% |
| 0x053f…90da | uni v4 | ETH/UNI | 0.35% | 45 | $235k | $821 | $0 | $821 | $14.9M | 24.03% | 4842.6% | 2.090% |
| 0xdb4c…43b1 | uni v4 | ETH/0xc8fb…8888 | 0.00% | 333 | $219k | $0 | $0 | $0 | $951k | 0.10% | 20.3% | – |
| [0x8ad5…e6d8](https://etherscan.io/address/0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8) | uni v3 | USDC/WETH | 0.30% | 67 | $211k | $632 | $0 | $632 | $280.0M | 0.99% | 198.9% | 0.294% |

Just-in-time liquidity: 44 episodes (mint and burn of identical liquidity inside one block), bracketing $45k of swaps and taking about $15 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 15 episodes, fees taken $10
- [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de): 9 episodes, fees taken $2
- [0x27c2…2bf2](https://etherscan.io/address/0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2): 4 episodes, fees taken $1
- [0x58c7…55f1](https://etherscan.io/address/0x58c75e1031040910a676c4fd30837e5f8a0b55f1): 3 episodes, fees taken $0
- [0xaaa0…ffff](https://etherscan.io/address/0xaaa0bf2e340c2125603b8ffd4ec30faea08effff): 2 episodes, fees taken $0
- [0xab56…03e2](https://etherscan.io/address/0xab567bb4953ac3b184e6078dd8d3d1dbf2dc03e2): 2 episodes, fees taken $1
- [0x0796…b971](https://etherscan.io/address/0x079628b8b81cd51e269dac0c1ec8655f889eb971): 2 episodes, fees taken $0
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 2 episodes, fees taken $0

Swap volume by venue: uniswap_v3 $16.3M (12489), uniswap_v4 $12.6M (7355), curve $8.9M (609), uniswap_v2_like $915k (4622), balancer $245k (144).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0x059b…aca0 (0x6653…e059/0xf6b1…103f, 160 swaps); 0xdbeb…8cb3 (0x0000…0000/0x8602…2148, 142 swaps); 0x230e…804d (0x0000…0000/0xa0df…c845, 107 swaps); 0x1271…75aa (0xb58e…21cb/0xcedb…f8e7, 98 swaps); 0xd1d6…b157 (0x0000…0000/0x2fb6…e0cc, 96 swaps); 0x1b26…fdfa (0x0000…0000/0xa249…e63b, 84 swaps); 0x459b…0a5b (0x0000…0000/0xeaa6…a69a, 45 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 43 swaps); 0x17b3…4efd (0x5ab3…b691/0xdac1…1ec7, 42 swaps); 0x1ba3…1365 (0x0000…0000/0x0a5a…2477, 39 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | tBTC | 0.00% | 0.26% | 0.2% | $135.6M | $207k |
| Aave v3 | EURC | 2.42% | 4.05% | 66.3% | $45.9M | $30.4M |
| Aave v3 | UNI | 0.00% | 0.17% | 1.1% | $3.2M | $35k |
| Aave v3 | WBTC | 0.00% | 0.34% | 2.8% | $2.7B | $75.2M |
| Aave v3 | GHO | 0.00% | 4.00% | 83.3% | $135.2M | $112.6M |
| Aave v3 | USDe | 1.72% | 5.87% | 39.0% | $652.3M | $254.5M |
| Aave v3 | LINK | 0.01% | 0.47% | 3.0% | $115.2M | $3.4M |
| Aave v3 | LUSD | 0.54% | 2.06% | 33.0% | $1.9M | $626k |
| Aave v3 | DAI | 3.07% | 4.71% | 86.7% | $131.6M | $114.1M |
| Aave v3 | PYUSD | 3.88% | 4.90% | 87.8% | $7.6M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.9B | $7.2M |
| Aave v3 | AAVE | 0.00% | 0.00% | 0.0% | $108.4M | $0 |
| Aave v3 | LBTC | 0.00% | 0.00% | 0.0% | $190.4M | $1345 |
| Aave v3 | RLUSD | 2.18% | 4.42% | 61.5% | $4.6M | $2.9M |
| Aave v3 | sDAI | 0.00% | 0.00% | 0.0% | $51k | $0 |
| Aave v3 | FRAX | 2.71% | 4.55% | 74.9% | $39k | $29k |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $268.8M | $0 |
| Aave v3 | MKR | 0.00% | 0.16% | 1.1% | $199k | $2105 |
| Aave v3 | USDC | 12.87% | 14.30% | 100.0% | $2.2B | $2.2B |
| Aave v3 | rsETH | 0.00% | 0.00% | 0.0% | $928.6M | $2886 |
| Aave v3 | rETH | 0.00% | 0.02% | 0.1% | $103.9M | $118k |
| Aave v3 | cbETH | 0.00% | 0.05% | 0.3% | $16.3M | $54k |
| Aave v3 | ezETH | 0.00% | 0.00% | 0.0% | – | – |
| Aave v3 | WETH | 1.41% | 2.02% | 82.3% | $5.4B | $4.4B |
| Aave v3 | USDtb | 8.05% | 12.09% | 83.2% | $15.4M | $12.9M |
| Aave v3 | ENS | 0.09% | 1.46% | 7.3% | $97k | $7093 |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.6% | $1.5B | $9.6M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $139k |
| Aave v3 | CRV | 0.47% | 5.77% | 12.5% | $2.9M | $364k |
| Aave v3 | USDT | 3.60% | 4.28% | 93.6% | $3.0B | $2.8B |
| Aave v3 | USDS | 0.12% | 5.52% | 3.0% | $11.2M | $335k |
| Aave v3 | USDG | 1.69% | 3.64% | 58.2% | $12.3M | $7.1M |
| Aave v3 | crvUSD | 0.99% | 2.91% | 42.4% | $186k | $79k |
| SparkLend | tBTC | 0.00% | 0.00% | 0.0% | $1.6M | $8 |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $142.4M | $330k |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $308.3M | $208.6M |
| SparkLend | PYUSD | 0.59% | 3.89% | 16.7% | $100.0M | $16.7M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9905 |
| SparkLend | LBTC | 0.00% | 5.00% | 0.0% | $264.3M | $0 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sDAI | 0.00% | 1.00% | 0.0% | $43k | $0 |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $25.6M | $23.6M |
| SparkLend | rsETH | 0.00% | 5.00% | 0.0% | $40k | $0 |
| SparkLend | sUSDS | 0.00% | 0.00% | 0.0% | $3.3M | $0 |
| SparkLend | rETH | 0.00% | 0.25% | 0.0% | $15.7M | $2037 |
| SparkLend | ezETH | 0.00% | 5.00% | 0.0% | – | – |
| SparkLend | WETH | 1.56% | 1.97% | 83.0% | $1.2B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.02% | 1.3% | $285.3M | $3.8M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $105.0M | $0 |
| SparkLend | USDT | 2.62% | 3.52% | 82.8% | $391.8M | $324.2M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $748.0M | $490.8M |
| SparkLend | USDG | 0.00% | 3.46% | 0.0% | $1 | $0 |
| Compound v3 USDC | base | 5.69% | 6.76% | 90.8% | $374.4M | $339.8M |
| Compound v3 USDT | base | 3.00% | 3.82% | 83.4% | $185.3M | $154.5M |
| Compound v3 WETH | base | 1.36% | 1.88% | 67.8% | $125.2M | $84.9M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.52% APR on $1.4B of USDe.

Rate curves: Aave v3 AAVE optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 0%; Aave v3 CRV optimal 45%, base 3.00%, slope1 10.00%, slope2 150.00%, reserve factor 35%; Aave v3 DAI optimal 92%, base 0.00%, slope1 5.00%, slope2 35.00%, reserve factor 25%; Aave v3 ENS optimal 45%, base 0.00%, slope1 9.00%, slope2 300.00%, reserve factor 20%; Aave v3 EURC optimal 90%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 10%; Aave v3 FRAX optimal 90%, base 0.00%, slope1 5.50%, slope2 40.00%, reserve factor 20%; Aave v3 GHO optimal 99%, base 4.00%, slope1 0.00%, slope2 0.00%, reserve factor 100%; Aave v3 LBTC optimal 45%, base 0.00%, slope1 4.00%, slope2 300.00%, reserve factor 50%; Aave v3 LINK optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 LUSD optimal 80%, base 0.00%, slope1 5.00%, slope2 50.00%, reserve factor 20%; Aave v3 MKR optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 PYUSD optimal 90%, base 1.00%, slope1 4.00%, slope2 50.00%, reserve factor 10%; Aave v3 RLUSD optimal 80%, base 2.50%, slope1 2.50%, slope2 50.00%, reserve factor 20%; Aave v3 UNI optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 USDC optimal 94%, base 0.00%, slope1 4.30%, slope2 10.00%, reserve factor 10%; Aave v3 USDG optimal 80%, base 0.00%, slope1 5.00%, slope2 30.00%, reserve factor 20%; Aave v3 USDS optimal 92%, base 5.50%, slope1 0.75%, slope2 35.00%, reserve factor 25%; Aave v3 USDT optimal 94%, base 0.00%, slope1 4.30%, slope2 10.00%, reserve factor 10%; Aave v3 USDe optimal 90%, base 5.00%, slope1 2.00%, slope2 12.00%, reserve factor 25%; Aave v3 USDtb optimal 80%, base 0.00%, slope1 4.00%, slope2 50.00%, reserve factor 20%; Aave v3 WBTC optimal 80%, base 0.25%, slope1 2.50%, slope2 300.00%, reserve factor 50%; Aave v3 WETH optimal 92%, base 0.00%, slope1 2.20%, slope2 6.00%, reserve factor 15%; Aave v3 cbBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 cbETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 crvUSD optimal 80%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 20%; Aave v3 ezETH optimal 45%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 15%; Aave v3 rETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 rsETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 sDAI optimal 90%, base 0.00%, slope1 5.00%, slope2 75.00%, reserve factor 20%; Aave v3 sUSDe optimal 90%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 20%; Aave v3 tBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 weETH optimal 30%, base 1.00%, slope1 7.00%, slope2 300.00%, reserve factor 45%; Aave v3 wstETH optimal 80%, base 0.00%, slope1 1.00%, slope2 40.00%, reserve factor 35%.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | USDe | 37 | 5.90% → 5.87% | 5.87% – 5.90% | 1.79% → 1.72% |
| Aave v3 | LINK | 9 | 0.47% → 0.47% | 0.46% – 0.47% | 0.01% → 0.01% |
| Aave v3 | DAI | 6 | 4.71% → 4.71% | 4.71% – 4.72% | 3.07% → 3.07% |
| Aave v3 | EURC | 5 | 4.05% → 4.05% | 4.05% – 4.05% | 2.41% → 2.42% |
| Aave v3 | USDG | 6 | 3.64% → 3.64% | 3.64% – 3.64% | 1.69% → 1.69% |
| Aave v3 | USDC | 126 | 4.27% → 4.27% | 4.27% – 4.27% | 3.59% → 3.59% |
| SparkLend | USDC | 2 | 4.27% → 4.27% | 4.27% – 4.27% | 3.54% → 3.54% |
| Aave v3 | WETH | 103 | 2.02% → 2.02% | 2.02% – 2.02% | 1.41% → 1.41% |
| Aave v3 | USDT | 63 | 4.28% → 4.28% | 4.28% – 4.28% | 3.60% → 3.60% |
| Aave v3 | AAVE | 4 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | WETH | 14 | 1.96% → 1.96% | 1.96% – 1.96% | 1.55% → 1.55% |
| Aave v3 | 0x6874…2f38 | 1 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | GHO | 3 | 4.00% → 4.00% | 4.00% – 4.00% | 0.00% → 0.00% |
| Aave v3 | WBTC | 31 | 0.34% → 0.34% | 0.34% – 0.34% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 9 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | wstETH | 12 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | 0x59bc…9d34 | 7 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | wstETH | 8 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | USDtb | 1 | 12.09% → 12.09% | 12.09% – 12.09% | 8.05% → 8.05% |
| SparkLend | WBTC | 2 | 0.01% → 0.01% | 0.01% – 0.01% | 0.00% → 0.00% |
| Aave v3 | cbBTC | 2 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| SparkLend | cbBTC | 2 | 0.02% → 0.02% | 0.02% – 0.02% | 0.00% → 0.00% |
| Aave v3 | 0xf1c9…0e38 | 1 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | RLUSD | 1 | 4.42% → 4.42% | 4.42% – 4.42% | 2.18% → 2.18% |

Volumes by venue and kind: Aave v3: withdraw $14.6M, repay $11.1M, supply $8.0M, borrow $2.8M, atomic borrow $228, atomic repay $1; SparkLend: supply $76k, withdraw $75k, repay $61k.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25928231 | Aave v3 | withdraw | sUSDe | $7.8M | [0x5c2c…210f](https://etherscan.io/address/0x5c2c1aa8cebdeb2225e93481f93469ac8e1d210f) | [0x2e1f…b9aa](https://etherscan.io/tx/0x2e1f9e2db68c33f7c1159f87b3bef027f454cd8ac89350372f98ea3eac5fb9aa) |
| 25928208 | Aave v3 | repay | USDe | $4.5M | [0x5c2c…210f](https://etherscan.io/address/0x5c2c1aa8cebdeb2225e93481f93469ac8e1d210f) | [0xd372…a4ac](https://etherscan.io/tx/0xd372578cd816d2767c6a3677a711f7d777e9a14cb0559f5962f7731aaa09a4ac) |
| 25928696 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x45ec…3614](https://etherscan.io/tx/0x45eca231d4cb02e3afd1251fc265b932735565330b77272cf75634109bc43614) |
| 25928696 | Aave v3 | withdraw | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xa52b…fab8](https://etherscan.io/tx/0xa52be9bf099bf59e16d276823f230de4d6e27d2ed64633446b5bfd5abdb0fab8) |
| 25928688 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x8e0d…0088](https://etherscan.io/tx/0x8e0d4f6e732635534c481413962a4ce5dce1a3cab3087c890a16c1ecb7b10088) |
| 25928362 | Aave v3 | repay | USDe | $1.4M | [0x9014…be71](https://etherscan.io/address/0x901431e0303426d5f28180f0fb2c616e97d3be71) | [0x5f23…c391](https://etherscan.io/tx/0x5f23c670fe3634133a0a63f53bdad0bb01e3609e3d9e6858471c1b7dfabfc391) |
| 25928376 | Aave v3 | repay | USDe | $730k | [0x1b89…e7b1](https://etherscan.io/address/0x1b89772bbdc3d87e44087e4527a3ef7c5881e7b1) | [0x2bfd…814e](https://etherscan.io/tx/0x2bfd6d7e11cee5ae962ca9d06e0234b817d00671441b86c60fb02943cd3a814e) |
| 25928306 | Aave v3 | repay | USDe | $713k | [0xcaab…ec1e](https://etherscan.io/address/0xcaab6ff98989fdd4f47e7db6152e6fb47994ec1e) | [0x1d4f…0895](https://etherscan.io/tx/0x1d4f34157e480782108b2cdd2c07a8c3edcb7a4b732d1e60bdba374940290895) |
| 25928437 | Aave v3 | repay | USDe | $678k | [0x705d…fd89](https://etherscan.io/address/0x705d90c6af56ab7eb6d19078b08200e767dafd89) | [0x6cec…6dbe](https://etherscan.io/tx/0x6cecb934aea7f21d9d79f492c37ad08131a9696be40957f2f7d41becf7fd6dbe) |
| 25928688 | Aave v3 | supply | WETH | $651k | [0xde6a…c055](https://etherscan.io/address/0xde6a36a42234fe10d2bae1a354d871c68c23c055) | [0x0492…7a06](https://etherscan.io/tx/0x0492cba417aef737f7b8b07d8c1fe59d1f94440e8835e4a7c47d22280c2b7a06) |
| 25928408 | Aave v3 | supply | wstETH | $581k | [0xb95c…24e3](https://etherscan.io/address/0xb95c3358392523b954dd91fd84cacf206be424e3) | [0x0dd4…47a3](https://etherscan.io/tx/0x0dd468daa906f9659d1cb4d0b02ad2a3c82dd281816f9596c575bb56fd3b47a3) |
| 25928426 | Aave v3 | repay | USDe | $530k | [0x390e…2e14](https://etherscan.io/address/0x390e1e11f736840e92d6a6167223b18bc3b92e14) | [0x4ee6…40d1](https://etherscan.io/tx/0x4ee61c02a82e7566c1e27119bb1be0df161e39d10e3f38a480f634e5300740d1) |
| 25928408 | Aave v3 | borrow | GHO | $287k | [0xb95c…24e3](https://etherscan.io/address/0xb95c3358392523b954dd91fd84cacf206be424e3) | [0x0dd4…47a3](https://etherscan.io/tx/0x0dd468daa906f9659d1cb4d0b02ad2a3c82dd281816f9596c575bb56fd3b47a3) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- Aave v3 withdraw $7.8M sUSDe by [0x5c2c…210f](https://etherscan.io/address/0x5c2c1aa8cebdeb2225e93481f93469ac8e1d210f) ([0x2e1f…b9aa](https://etherscan.io/tx/0x2e1f9e2db68c33f7c1159f87b3bef027f454cd8ac89350372f98ea3eac5fb9aa)): $4.0M → [zero address (mint/burn) (known-canonical)](https://etherscan.io/address/0x0000000000000000000000000000000000000000); $3.8M → [0x50cf…5c4a](https://etherscan.io/address/0x50cfe7c1938db66a1a6d2e86d36f39fbef3d5c4a)
- Aave v3 withdraw $1.8M WETH by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xa52b…fab8](https://etherscan.io/tx/0xa52be9bf099bf59e16d276823f230de4d6e27d2ed64633446b5bfd5abdb0fab8)): $1.8M → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $66k → [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b); $1.8M → [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e)
- Aave v3 borrow $287k GHO by [0xb95c…24e3](https://etherscan.io/address/0xb95c3358392523b954dd91fd84cacf206be424e3) ([0x0dd4…47a3](https://etherscan.io/tx/0x0dd468daa906f9659d1cb4d0b02ad2a3c82dd281816f9596c575bb56fd3b47a3)): $287k → [0x18ef…d96a](https://etherscan.io/address/0x18efe565a5373f430e2f809b97de30335b3ad96a); $287k → [0xe78c…8336](https://etherscan.io/address/0xe78c05c508405207ecc256781b9415e6de1c8336)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| Aave v3 | [0xcaab…ec1e](https://etherscan.io/address/0xcaab6ff98989fdd4f47e7db6152e6fb47994ec1e) | $3.6M | $1.8M | 1.630 | 38.7% |
| Aave v3 | [0xb95c…24e3](https://etherscan.io/address/0xb95c3358392523b954dd91fd84cacf206be424e3) | $581k | $287k | 1.640 | 39.0% |
| Aave v3 | [0x5c2c…210f](https://etherscan.io/address/0x5c2c1aa8cebdeb2225e93481f93469ac8e1d210f) | $0 | $0 | ∞ | – |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| Aave v3 | [0x9014…be71](https://etherscan.io/address/0x901431e0303426d5f28180f0fb2c616e97d3be71) | $0 | $0 | ∞ | – |
| Aave v3 | [0x1b89…e7b1](https://etherscan.io/address/0x1b89772bbdc3d87e44087e4527a3ef7c5881e7b1) | $0 | $0 | ∞ | – |
| Aave v3 | [0x705d…fd89](https://etherscan.io/address/0x705d90c6af56ab7eb6d19078b08200e767dafd89) | $0 | $0 | ∞ | – |
| Aave v3 | [0xde6a…c055](https://etherscan.io/address/0xde6a36a42234fe10d2bae1a354d871c68c23c055) | $651k | $0 | ∞ | – |
| Aave v3 | [0x390e…2e14](https://etherscan.io/address/0x390e1e11f736840e92d6a6167223b18bc3b92e14) | $0 | $0 | ∞ | – |

Flash loans (events): BalFlash 988 ($46.4M), MorphoFlash 11 ($15k).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0xa673…e35a](https://etherscan.io/address/0xa6736593c1649b08add626f54744fa44133ae35a): 1 transactions, largest leg $228, gross $228; legs: USDG borrow $228

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 197 | $6.7M | 0.999813 | 0.999785 – 0.999817 | 0.999857 | -0.4 bps |
| USDS | 52 | $3.8M | 0.999947 | 0.999931 – 0.999962 | 1 | -0.5 bps |
| crvUSD | 45 | $2.3M | 0.999662 | 0.997592 – 0.999905 | 1 | -3.4 bps |
| USDe | 57 | $2.1M | 0.999866 | 0.999799 – 0.99996 | 1 | -1.3 bps |
| sUSDe | 21 | $973k | 1.24611 | 1.24582 – 1.24649 | 1.247 | -7.1 bps |
| ICP | 132 | $353k | 3.01783 | 2.99735 – 3.04214 | – | – |
| AUSD | 8 | $205k | 0.999985 | 0.999915 – 1.0001 | 1 | -0.2 bps |
| USDG | 19 | $147k | 1.00011 | 0.999966 – 1.00022 | 1 | +1.1 bps |
| SPCXon | 98 | $102k | 151.335 | 149.334 – 153.995 | – | – |
| PEPE | 37 | $93k | 3.59575e-06 | 3.57834e-06 – 3.60937e-06 | – | – |
| frxUSD | 16 | $63k | 0.999979 | 0.999673 – 1.0001 | 1 | -0.2 bps |
| weETH | 4 | $52k | 2742.45 | 2741.9 – 2742.47 | 2742.55 | -0.4 bps |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 188 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDT | $50.8M | $58.0M | $-7.2M |
| ETH | $25.3M | $28.3M | $-3.0M |
| USDC | $16.6M | $18.9M | $-2.3M |
| UNI | $2.9M | $2.0M | $978k |
| RLUSD | $3.7M | $96k | $3.6M |
| cbBTC | $2.0M | $1.5M | $448k |
| LINK | $422k | $967k | $-545k |
| EURC | $341k | $0 | $341k |
| USDG | $330k | $0 | $330k |
| ENS | $69k | $151k | $-82k |
| WBTC | $73k | $147k | $-74k |
| cbETH | $0 | $148k | $-148k |

By label: Binance 14 (model-memory) in $37.5M / out $6.4M; hot wallet (behaviour, day study) in $19.4M / out $22.7M; Bitfinex 2 (model-memory) in $9.1M / out $21.6M; Coinbase 10 (model-memory) in $14.5M / out $11.5M; Coinbase 5 (model-memory) in $6.8M / out $5.0M; Coinbase 11 (model-memory) in $5.4M / out $5.7M; Gate.io (model-memory) in $4.3M / out $4.1M; Binance 16 (model-memory) in $0 / out $6.9M; hot wallet (day study, unidentified) (model-memory) in $3.7M / out $2.3M; Binance 18 (model-memory) in $0 / out $5.8M; Binance 17 (model-memory) in $0 / out $5.6M; Bybit (model-memory) in $0 / out $5.5M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25928331 | WBTC | $440.8M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbfb0…76a2](https://etherscan.io/tx/0xbfb0504c4934583c84cd772d07493781f180cd947c4825e7d19cfd0cf65c76a2) |
| 25928331 | WBTC | $440.8M ×2 | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xbfb0…76a2](https://etherscan.io/tx/0xbfb0504c4934583c84cd772d07493781f180cd947c4825e7d19cfd0cf65c76a2) |
| 25928233 | WBTC | $436.4M ×4 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xe212…d2e8](https://etherscan.io/tx/0xe2126d392dc78dfdd82c4fa11b0da04fa45a59ff13917e4b4dae4b73b902d2e8) |
| 25928233 | WBTC | $436.4M ×4 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xe212…d2e8](https://etherscan.io/tx/0xe2126d392dc78dfdd82c4fa11b0da04fa45a59ff13917e4b4dae4b73b902d2e8) |
| 25928341 | WBTC | $396.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x975d…326b](https://etherscan.io/tx/0x975d00982557b220bc96b03928993e1ad82d4b34b91931b507f457cc2bf6326b) |
| 25928341 | WBTC | $396.7M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x975d…326b](https://etherscan.io/tx/0x975d00982557b220bc96b03928993e1ad82d4b34b91931b507f457cc2bf6326b) |
| 25928661 | USDC | $98.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x7966…ee94](https://etherscan.io/address/0x7966319bab61f7d6473a64277897885893c2ee94) | [0x3348…948a](https://etherscan.io/tx/0x33482cec2cfa07a43859395990f95b5e63c466563830e6f4daf38a1734e3948a) |
| 25928661 | USDC | $98.1M | [0x7966…ee94](https://etherscan.io/address/0x7966319bab61f7d6473a64277897885893c2ee94) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3348…948a](https://etherscan.io/tx/0x33482cec2cfa07a43859395990f95b5e63c466563830e6f4daf38a1734e3948a) |
| 25928663 | USDC | $98.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xd80c…d329](https://etherscan.io/tx/0xd80c8d74c55db0885854c297969c866f60b2fc6b987179ea412293588865d329) |
| 25928663 | USDC | $98.1M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd80c…d329](https://etherscan.io/tx/0xd80c8d74c55db0885854c297969c866f60b2fc6b987179ea412293588865d329) |
| 25928233 | USDC | $98.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xe212…d2e8](https://etherscan.io/tx/0xe2126d392dc78dfdd82c4fa11b0da04fa45a59ff13917e4b4dae4b73b902d2e8) |
| 25928233 | USDC | $98.1M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xe212…d2e8](https://etherscan.io/tx/0xe2126d392dc78dfdd82c4fa11b0da04fa45a59ff13917e4b4dae4b73b902d2e8) |
| 25928377 | USDC | $97.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x0dd4…fe48](https://etherscan.io/tx/0x0dd472b525219a4575d90d42ef0b53dbc4d00bb4afca72992b8286510264fe48) |
| 25928377 | USDC | $97.8M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0dd4…fe48](https://etherscan.io/tx/0x0dd472b525219a4575d90d42ef0b53dbc4d00bb4afca72992b8286510264fe48) |
| 25928551 | USDC | $97.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x3f51…3590](https://etherscan.io/tx/0x3f51f183f02cccc5764623954c320834f578a2231ea46d09f9213f6ce2af3590) |
| 25928551 | USDC | $97.4M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3f51…3590](https://etherscan.io/tx/0x3f51f183f02cccc5764623954c320834f578a2231ea46d09f9213f6ce2af3590) |
| 25928689 | USDC | $97.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xdccd…ede5](https://etherscan.io/tx/0xdccdc6d8701b450e8c0c9e87ed19d2eca01657bdafb22d38242e175ffb21ede5) |
| 25928689 | USDC | $97.2M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xdccd…ede5](https://etherscan.io/tx/0xdccdc6d8701b450e8c0c9e87ed19d2eca01657bdafb22d38242e175ffb21ede5) |
| 25928202 | USDC | $89.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xad82…d942](https://etherscan.io/tx/0xad82cc4f462bbb594d3481acfc7396a9e0a7ecce83232761742ec3bfc0bed942) |
| 25928202 | USDC | $89.4M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xad82…d942](https://etherscan.io/tx/0xad82cc4f462bbb594d3481acfc7396a9e0a7ecce83232761742ec3bfc0bed942) |
| 25928237 | USDC | $89.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xcb03…0fb2](https://etherscan.io/tx/0xcb03b7d2de4513a16c054d77f61faab2b5595ab6118436fa0a5229d3add20fb2) |
| 25928237 | USDC | $89.2M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xcb03…0fb2](https://etherscan.io/tx/0xcb03b7d2de4513a16c054d77f61faab2b5595ab6118436fa0a5229d3add20fb2) |
| 25928266 | USDC | $89.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0x6478…c5fb](https://etherscan.io/tx/0x647899171e9bb0f1f92259bd18c93f4db54112807183572effad5c7d0d51c5fb) |
| 25928266 | USDC | $89.1M | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x6478…c5fb](https://etherscan.io/tx/0x647899171e9bb0f1f92259bd18c93f4db54112807183572effad5c7d0d51c5fb) |
| 25928341 | USDC | $88.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0x3a3d…7844](https://etherscan.io/tx/0x3a3d432b931c2ed9a7d905c8a6a8dac7ac1854df124255a2505bce90fc7e7844) |
| 25928341 | USDC | $88.9M | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3a3d…7844](https://etherscan.io/tx/0x3a3d432b931c2ed9a7d905c8a6a8dac7ac1854df124255a2505bce90fc7e7844) |
| 25928342 | USDC | $88.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xec3f…c737](https://etherscan.io/tx/0xec3f9678fe1880e2a54ee1026f83b8f507a9e1fae5c6aad11b231284c7f0c737) |
| 25928342 | USDC | $88.9M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xec3f…c737](https://etherscan.io/tx/0xec3f9678fe1880e2a54ee1026f83b8f507a9e1fae5c6aad11b231284c7f0c737) |
| 25928453 | USDC | $88.8M ×3 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x8c68…8ff8](https://etherscan.io/tx/0x8c68763a35a2c4e92975d98034ec8928037367a4249d84ae3d676e6dbf958ff8) |
| 25928453 | USDC | $88.8M ×3 | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8c68…8ff8](https://etherscan.io/tx/0x8c68763a35a2c4e92975d98034ec8928037367a4249d84ae3d676e6dbf958ff8) |

Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) | WETH → USDC | 4 | $591k | $160k | 36s | 0.44 | 0.17 | uniswap_v3 4 |
| [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) | USDC → WETH | 4 | $583k | $156k | 36s | 0.44 | 0.17 | uniswap_v3 4 |
| [0xeaa9…8e51](https://etherscan.io/address/0xeaa9ebddd373c4bd8bb92dfcc9c7e7fcdb268e51) | WETH → USDC | 4 | $223k | $46k | 1332s | 0.47 | 0.48 | uniswap_v3 4 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25928217 | curve | USDT → USDC | $1.9M | [0x4cd4…d03e](https://etherscan.io/address/0x4cd4499d6e6a0eb8995a2cabd400d1ad35c4d03e) | [0x85d8…b71e](https://etherscan.io/tx/0x85d858993c407f825cce609f6bb2331a7c17c882e8aac46497aecdf140ebb71e) |
| 25928217 | curve | USDC → USDT | $1.9M | [0x4cd4…d03e](https://etherscan.io/address/0x4cd4499d6e6a0eb8995a2cabd400d1ad35c4d03e) | [0xb158…45fd](https://etherscan.io/tx/0xb15883b18df28bf1bc7aa11e86043ea56fb46ee8405d8697d27655f44a1545fd) |

## E. Bridges, issuance, staking

Outbound: $16.7M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $5.2M (114).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| OFT | USDe | eid 30383 | 8 | $8.7M | – |
| OFT | sUSDe | eid 30383 | 1 | $3.8M | – |
| CCTP | USDC | Polygon | 12 | $1.1M | 0xf70da97812cb… $1.1M |
| OFT | USDT | eid 30383 | 3 | $511k | – |
| OFT | USDe | Solana | 3 | $372k | – |
| OFT | USDG | eid 30274 | 4 | $359k | – |
| CCTP | USDC | Arbitrum | 12 | $345k | 0x6a2abff960b6… $159k |
| CCTP | USDC | Base | 49 | $252k | 0x406f3b5f7745… $86k |
| OFT | USDT | eid 30390 | 1 | $214k | – |
| OFT | PYUSD | Arbitrum | 2 | $207k | – |
| OFT | USDT | Polygon | 4 | $197k | – |
| OFT | USDT | eid 30420 | 6 | $162k | – |
| OFT | USDG | eid 30416 | 6 | $109k | – |
| CCTP | USDC | OP Mainnet | 7 | $95k | 0x3a6a72459518… $84k |
| CCTP | USDC | domain 15 | 4 | $82k | 0xc1062b7c5dc8… $45k |
| OFT | EURC | eid 30410 | 1 | $62k | – |
| CCTP | USDC | Solana | 17 | $52k | bad3ca5933dd68… $20k |
| CCTP | USDC | domain 19 | 8 | $24k | 0xc1062b7c5dc8… $21k |
| OFT | USDT | Arbitrum | 6 | $24k | – |
| CCTP | USDC | World Chain | 2 | $15k | 0x07ae8551be97… $13k |

Issuance totals: USDC burn $6.8M (136); USDC mint $7.1M (209). Largest: USDC burn $2.3M ([0xed1b…0226](https://etherscan.io/tx/0xed1b177d6d3a62edd4ad68200fa9c5fd0f97dc720d36d0f6dfd1cde595430226)); USDC burn $2.0M ([0x516b…6887](https://etherscan.io/tx/0x516becc9a6f5a7673d059a3cfe09feecca73b9fe9fd3fa66701a89ce11f96887)); USDC mint $1.0M ([0xf567…9f4c](https://etherscan.io/tx/0xf5678b2a91918979351fd108a7c042d88435ea87f91a24e58fc3d6128ea49f4c)); USDC mint $990k ([0x04a9…58fa](https://etherscan.io/tx/0x04a99762dc664a8d5b3c7403170f896c9eaede8a41296dec4c29295e575a58fa)); USDC mint $990k ([0xb5d6…a2fa](https://etherscan.io/tx/0xb5d66270ec19fd3baf13e112fb4825a9b30fc6b8c5e0eb82091f81c08ba3a2fa)).


WETH wrapped 8824 ETH, unwrapped 9090 ETH; Lido staked 26.8 ETH, withdrawal requests 33.0 ETH; sUSDe cooldowns 8 for $9.6M.


## F. Gas market and block production

Base fee 0.044 → 0.042 gwei (min 0.035, median 0.051, max 0.084); blocks 51% full; median tip 0.061 gwei; 4.2% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 307,  Quasar (quasar.win)  90, Eureka (eurekabuilder.xyz) 66, BuilderNet 61, gethgo1.26.4linux 12, besu 26.8.1 9.


Most active senders: [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 972, [0x0e00…c0e4](https://etherscan.io/address/0x0e0052a184fd59c6b7e1e99d739802ecb3aec0e4) 882, [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 872, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 838, [0x316f…241b](https://etherscan.io/address/0x316fb96cbe2fb52dbe679d75b928fcfad858241b) 709, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 656, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 656, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x264bd8291fae1d75db2c5f573b07faa6715997b5) 572, [0x4838…5f97](https://etherscan.io/address/0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97) 547, [Relay solver / USDG inventory wallet (takes 100% of RelayDepository payouts on Ethereum and Robinhood Chain; Paxos mint-and-redeem counterparty on both) (etherscan-verified)](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) 509.


Intent fills: CoWTrade 250, OneInchFilled 362, UniXFill 51. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

