# Ethereum mainnet live scan: 2026-09-08T04:27:11+00:00 to 2026-09-08T05:27:11+00:00 UTC

Blocks 25930251 to 25930550 (300 blocks, 1.00 h), 65,627 transactions, 272,715 logs. Prices at head block 25930925: ETH $2474, BTC $79k. Generated 2026-09-08T06:48:09+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

# What the whole book is worth

Ethereum mainnet, **2026-09-08 04:29 to 05:27 UTC**, blocks 25,930,251–25,930,550 (300 blocks)
[[verify: blocks]] [[verify: transactions]] [[verify: logs]], with head reads at 05:29. A short window, collected to close the loop rather than to study the hour: twelve detectors run in
about five seconds, and **all seven** strategies in the book now re-price themselves from it — none is a memory.

## 1. Pendle, and the distinction that decides whether an implied yield is a trade

`detectors/fixed_vs_floating.py` discovers Pendle markets from the window's own `Swap` logs — the markets with live
flow, no hardcoded list and no API — reads each PT price through the PY oracle, and refuses to quote one whose
observation window `getOracleState` reports as unpopulated.

The classification is the point. A principal token's implied yield is a *term premium* only when the floating rate on
the same underlying is readable; otherwise it is the market's price of an issuer's credit, which this system has not
assessed. In this window:

| PT | implied | comparison | classification |
|---|---:|---|---|
| PT-sUSDS-26NOV2026 | 4.89% | Sky savings rate 3.60% | **term premium**, +129bp |
| PT-reUSD-10DEC2026 | 10.98% | — | credit spread |
| PT-trUSD-26NOV2026 | 10.07% | — | credit spread |

The eight markets that traded in the earlier 21:27–23:27 window were *all* credit spreads — implied yields of 6% to
23% with no comparable floating rate anywhere. Ranking Pendle by implied yield alone puts those at the top of a book;
the classifier is what keeps them out of it.

The matcher had to be fixed to do that honestly. Its first version matched underlyings by substring, so `USDE` inside
`SRUSDE` classified PT-srUSDe as a term premium on Ethena credit — a different issuer's product quoted as a rate view.
It now parses the asset segment of `PT-<asset>-<date>` and matches exactly. That is the error the detector exists to
prevent, committed by its own matcher.

## 2. The strategy book, sized — all seven re-pricing themselves

| strategy | net APR | capacity | per year |
|---|---:|---:|---:|
| Sky savings rate over Aave USDS | 3.48% | $1,000,000,000 | $34,800,000 |
| sUSDe cooldown redemption | 17.25% | $600,000 | $103,500 |
| Morpho USDT borrow vs Aave | 1.46% | $6,353,460 | $92,761 |
| USDG captive-flow v4 LP | 10.37% | $150,000 | $15,555 |
| PT-sUSDS fixed vs the savings rate | 0.64% | $1,000,000 | $6,400 |
| Compound v3 USDC over SparkLend | 0.39% | $1,400,000 | $5,460 |
| Aave USDtb supply | 2.39% | $227,400 | $5,435 |

**Excluding the savings rate — which is the benchmark, not an edge — the whole book is worth about $229,000 a year**,
and $103,500 of that is one trade whose annualisation assumes a million dollars of sUSDe is offered below NAV every
single day. Nothing here is stale: every row was re-priced from this window or the one before it.

The last hand number to fall was the largest. "Borrow USDT on Morpho rather than Aave" was quoted at 91bp on $24M —
$218,400 a year — from a single afternoon two days ago. Measured: **1.46pp on $6.35M, $92,761**. The rate gap is
*wider* than the hand note said and the capacity is a quarter of it, because $24M was the vault's size and $6.35M is
what is actually withdrawable. The detector also names what the hand note omitted: the cheapest Morpho USDT market
lends against **sUSDS at 96.5% LLTV**, so the rate is only available to a borrower who can post that collateral.

On an isolated-market venue that distinction is the whole thing. A pooled reserve lets any listed collateral reach any
rate; a Morpho market is a rate *for one collateral*, and quoting it without saying which is quoting a price nobody
can necessarily trade.

That is the honest state of the mainnet dollar opportunity set as this system currently measures it. It is not a
disappointing result; it is the result. An efficient market is supposed to look like this, and the value of the loop
is that the number is now derived rather than asserted — every row has legs `economics.py` priced, a capacity that
came from a rate curve or a traded volume rather than a pool balance, and a kill criterion.

## 3. Two strategies decayed inside the session, and the book caught both

| strategy | earlier today | now | why |
|---|---:|---:|---|
| Compound v3 USDC over SparkLend | 1.46% | **0.34%** | utilisation drifted 90.77% → 90.30% against a kink at exactly 90.0%; best size fell $1.4M → $405k |
| PT-sUSDS fixed vs the savings rate | 1.37% *(hand, 09-06)* | **0.64%** | the raw gap narrowed 137bp → 129bp, and the hand study did not net Pendle's entry impact |

The Compound row is the kink analysis playing out in hours: 0.47 percentage points of utilisation, and three quarters
of the opportunity is gone. The PT row is a modelling correction rather than a market move — and it required its own
correction first. Charging a Pendle purchase the constant-product impact overstates it by about two orders of
magnitude, because Pendle's AMM is a rate curve; the detector now applies an amplification of 50, anchored to the one
observation this repo has (a $1M order into a $3.5M pool taking "a real part of" 137bp), and says so. Replacing that
estimate with a measured quote-by-size read from the Pendle router is the obvious next improvement.

## 4. A gap in the provenance gate, found by falling into it

`head_state.json` is an input to `analyze` — the entire window is priced from it — and it was not fingerprinted. So
re-running `head` on an old window silently re-prices every dollar figure in an analysis that is not re-run, with the
labels and the token table both unchanged, meaning no existing gate could see it. It happened here: the 21:27–23:27
window ended up carrying a head read from 05:21 the next morning.

Two fixes. `head` now refuses to read current state for a window collected long ago, because that mixes two
timeframes and nothing downstream would say so:

```
refusing: the head is 5007 blocks past this window (collected to 25925535, head 25930542, window 1491 blocks).
Reading state now would price a past window at present rates.
```

And `head` is now a provenance gate alongside labels, tokens and blocks, so an analysis whose head state moved
underneath it reports as stale before a single number is compared.

## 5. Everything else

- **JIT liquidity took 15.8% of pool fees in this window** ($26 of $168), against 0.06%–0.29% in the three previous
  ones. The absolute numbers are trivial and the share is not; it is the first window in which the per-window JIT hit
  cleared its 10% threshold, which is exactly the change the detector was written to notice.
- The dust-spam and airdrop campaigns continue at the same operators and the same cadence: 0xbeef007e to 5,666
  recipients, 0.0003 USDT to 2,568.
- `nav_discount` found nothing: no redeemable claim traded away from NAV by more than its round-trip cost in this
  hour, which is why the sUSDe strategy shows its last seen rate in brackets rather than a fresh one.

## What is checked, and what is not

The window aggregates are re-derived by `live_scan verify`. Everything in sections 1–3 comes from head reads and
contract calls at 05:29 UTC — no verify recipe re-derives a head read yet, so the entire rate and yield surface in
this note is a single reading. That remains the largest untagged surface in the system.


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) | curve | USDC/USDT | ? | 36 | $7.2M | – | $0 | – | – | – | – | – |
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 77 | $3.8M | $23 | $0 | $23 | $100.0B | 0.00% | 0.0% | 0.006% |
| [0x5b03…8e96](https://etherscan.io/address/0x5b03cccab7ba3010fa5cad23746cbf0794938e96) | curve | USDe/USDT | ? | 24 | $2.6M | – | $0 | – | – | – | – | – |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 233 | $1.9M | $964 | $0 | $964 | $506.0M | 1.66% | 335.3% | 0.276% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 784 | $1.3M | $125 | $1 | $124 | $105.5M | 1.03% | 206.7% | 0.631% |
| [0x13e1…43e1](https://etherscan.io/address/0x13e12bb0e6a2f1a3d6901a59a9d585e89a6243e1) | curve | frxUSD/crvUSD | ? | 17 | $1.2M | – | $0 | – | – | – | – | – |
| [0x4dec…d69e](https://etherscan.io/address/0x4dece678ceceb27446b35c672dc7d61f30bad69e) | curve | USDC/crvUSD | ? | 21 | $997k | – | $0 | – | – | – | – | – |
| [0xc061…1622](https://etherscan.io/address/0xc061caa073f3d95f80f8e5428d32d2d76f5e1622) | curve | USDC/USDG | ? | 19 | $899k | – | $0 | – | – | – | – | – |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 61 | $781k | $78 | $0 | $78 | $65.6B | 0.00% | 0.2% | 0.005% |
| 0x9035…eb4f | uni v4 | RLUSD/USDS | 0.00% | 5 | $700k | $4 | $0 | $4 | $40.0B | 0.00% | 0.0% | 0.002% |
| [0x390f…7bf4](https://etherscan.io/address/0x390f3595bca2df7d23783dfd126427cceb997bf4) | curve | USDT/crvUSD | ? | 27 | $664k | – | $0 | – | – | – | – | – |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 88 | $639k | $6 | $0 | $6 | $16.9B | 0.00% | 0.1% | 0.007% |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 66 | $559k | $279 | $0 | $279 | $202.8M | 1.20% | 242.3% | 0.290% |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 496 | $558k | $56 | $0 | $56 | $32.7M | 1.49% | 299.7% | 4.015% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 7 | $472k | $3 | $0 | $3 | $149.1B | 0.00% | 0.0% | 0.001% |
| 0xb90d…b716 | uni v4 | USDC/USDG | 0.01% | 17 | $434k | $36 | $0 | $36 | $13.3B | 0.00% | 0.5% | 0.010% |
| 0x7da1…7427 | uni v4 | USDC/USDG | 0.01% | 17 | $421k | $40 | $0 | $40 | $18.0B | 0.00% | 0.4% | 0.009% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 39 | $376k | $1128 | $0 | $1128 | $1.8B | 0.54% | 109.7% | 0.083% |
| 0x8aa4…4e47 | uni v4 | USDC/USDT | 0.00% | 13 | $295k | $4 | $0 | $4 | $19.4B | 0.00% | 0.0% | 0.005% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 142 | $283k | $141 | $0 | $141 | $56.9M | 2.17% | 437.5% | 0.281% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 45 | $251k | $3 | $0 | $3 | $10.9B | 0.00% | 0.0% | 0.005% |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.03% | 79 | $242k | $44 | $0 | $44 | $60.1M | 0.64% | 128.3% | 0.287% |
| [0xb31e…5bc3](https://etherscan.io/address/0xb31e70454bdf5bc3) | balancer | USDC/WETH | ? | 12 | $236k | – | $0 | – | – | – | – | – |
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 12 | $228k | – | $0 | – | – | – | – | – |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 23 | $216k | $7 | $0 | $7 | $8.4B | 0.00% | 0.1% | 0.010% |

Just-in-time liquidity: 13 episodes (mint and burn of identical liquidity inside one block), bracketing $18k of swaps and taking about $28 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 7 episodes, fees taken $23
- [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de): 3 episodes, fees taken $3
- [0x312c…09e1](https://etherscan.io/address/0x312c64ece077ca72a971e98669b1f77c90e309e1): 2 episodes, fees taken $2
- [0x3437…e4ab](https://etherscan.io/address/0x34373bba18aa058f889c3fc28329c0bfb4b3e4ab): 1 episodes, fees taken $0

Swap volume by venue: curve $14.3M (364), uniswap_v4 $9.3M (2890), uniswap_v3 $8.1M (5400), uniswap_v2_like $819k (2029), balancer $268k (61).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0x4dd6…ab8d (0x0000…0000/0xa85f…0b07, 31 swaps); 0xdbeb…8cb3 (0x0000…0000/0x8602…2148, 24 swaps); 0x15d6…1935 (0x0000…0000/0x3270…a4ca, 21 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 20 swaps); 0x1ba3…1365 (0x0000…0000/0x0a5a…2477, 13 swaps); 0x1271…75aa (0xb58e…21cb/0xcedb…f8e7, 12 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 12 swaps); 0x2287…1bba (0x0000…0000/0xdac1…1ec7, 12 swaps); 0xd4e5…909d (0x0000…0000/0xa0b8…eb48, 11 swaps); 0xc8e2…4078 (0x14d6…47a1/0x600d…fd3f, 10 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | tBTC | 0.00% | 0.26% | 0.2% | $134.9M | $205k |
| Aave v3 | EURC | 2.42% | 4.06% | 66.4% | $45.9M | $30.4M |
| Aave v3 | UNI | 0.00% | 0.17% | 1.1% | $3.3M | $36k |
| Aave v3 | WBTC | 0.00% | 0.34% | 2.8% | $2.7B | $74.5M |
| Aave v3 | GHO | 0.00% | 4.00% | 83.5% | $135.2M | $112.8M |
| Aave v3 | USDe | 1.65% | 5.84% | 37.8% | $661.0M | $249.7M |
| Aave v3 | LINK | 0.01% | 0.46% | 3.0% | $114.4M | $3.4M |
| Aave v3 | LUSD | 0.54% | 2.06% | 33.0% | $1.9M | $626k |
| Aave v3 | DAI | 3.07% | 4.71% | 86.8% | $131.6M | $114.1M |
| Aave v3 | PYUSD | 3.88% | 4.90% | 87.8% | $7.6M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.8B | $7.2M |
| Aave v3 | AAVE | 0.00% | 0.00% | 0.0% | $107.7M | $0 |
| Aave v3 | LBTC | 0.00% | 0.00% | 0.0% | $189.3M | $1337 |
| Aave v3 | RLUSD | 2.18% | 4.42% | 61.5% | $4.6M | $2.9M |
| Aave v3 | sDAI | 0.00% | 0.00% | 0.0% | $51k | $0 |
| Aave v3 | FRAX | 2.71% | 4.55% | 74.9% | $39k | $29k |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $266.5M | $0 |
| Aave v3 | MKR | 0.00% | 0.16% | 1.1% | $199k | $2103 |
| Aave v3 | USDC | 3.61% | 4.28% | 93.6% | $2.3B | $2.2B |
| Aave v3 | rsETH | 0.00% | 0.00% | 0.0% | $924.2M | $2873 |
| Aave v3 | rETH | 0.00% | 0.02% | 0.1% | $103.5M | $117k |
| Aave v3 | cbETH | 0.00% | 0.05% | 0.3% | $16.2M | $54k |
| Aave v3 | ezETH | 0.00% | 0.00% | 0.0% | – | – |
| Aave v3 | WETH | 1.41% | 2.02% | 82.3% | $5.3B | $4.4B |
| Aave v3 | USDtb | 8.07% | 12.12% | 83.3% | $15.4M | $12.9M |
| Aave v3 | ENS | 0.09% | 1.46% | 7.3% | $99k | $7236 |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.6% | $1.5B | $9.4M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $139k |
| Aave v3 | CRV | 0.47% | 5.77% | 12.5% | $2.9M | $361k |
| Aave v3 | USDT | 3.56% | 4.25% | 93.0% | $3.0B | $2.8B |
| Aave v3 | USDS | 0.12% | 5.52% | 3.0% | $11.2M | $335k |
| Aave v3 | USDG | 1.54% | 3.47% | 55.5% | $12.2M | $6.7M |
| Aave v3 | crvUSD | 0.99% | 2.91% | 42.4% | $186k | $79k |
| SparkLend | tBTC | 0.00% | 0.00% | 0.0% | $1.6M | $8 |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $141.7M | $328k |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $308.3M | $208.6M |
| SparkLend | PYUSD | 0.59% | 3.89% | 16.7% | $100.0M | $16.7M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9827 |
| SparkLend | LBTC | 0.00% | 5.00% | 0.0% | $262.9M | $0 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sDAI | 0.00% | 1.00% | 0.0% | $43k | $0 |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $25.6M | $23.6M |
| SparkLend | rsETH | 0.00% | 5.00% | 0.0% | $40k | $0 |
| SparkLend | sUSDS | 0.00% | 0.00% | 0.0% | $3.3M | $0 |
| SparkLend | rETH | 0.00% | 0.25% | 0.0% | $15.6M | $2028 |
| SparkLend | ezETH | 0.00% | 5.00% | 0.0% | – | – |
| SparkLend | WETH | 1.56% | 1.97% | 83.0% | $1.2B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.02% | 1.3% | $291.7M | $3.8M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $104.7M | $0 |
| SparkLend | USDT | 2.62% | 3.52% | 82.8% | $391.8M | $324.2M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $744.3M | $488.4M |
| SparkLend | USDG | 0.00% | 3.46% | 0.0% | $1 | $0 |
| Compound v3 USDC | base | 4.34% | 5.24% | 90.3% | $376.1M | $339.8M |
| Compound v3 USDT | base | 3.01% | 3.83% | 83.7% | $185.2M | $155.0M |
| Compound v3 WETH | base | 1.36% | 1.88% | 67.8% | $124.7M | $84.5M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.54% APR on $1.4B of USDe.

Rate curves: Aave v3 AAVE optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 0%; Aave v3 CRV optimal 45%, base 3.00%, slope1 10.00%, slope2 150.00%, reserve factor 35%; Aave v3 DAI optimal 92%, base 0.00%, slope1 5.00%, slope2 35.00%, reserve factor 25%; Aave v3 ENS optimal 45%, base 0.00%, slope1 9.00%, slope2 300.00%, reserve factor 20%; Aave v3 EURC optimal 90%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 10%; Aave v3 FRAX optimal 90%, base 0.00%, slope1 5.50%, slope2 40.00%, reserve factor 20%; Aave v3 GHO optimal 99%, base 4.00%, slope1 0.00%, slope2 0.00%, reserve factor 100%; Aave v3 LBTC optimal 45%, base 0.00%, slope1 4.00%, slope2 300.00%, reserve factor 50%; Aave v3 LINK optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 LUSD optimal 80%, base 0.00%, slope1 5.00%, slope2 50.00%, reserve factor 20%; Aave v3 MKR optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 PYUSD optimal 90%, base 1.00%, slope1 4.00%, slope2 50.00%, reserve factor 10%; Aave v3 RLUSD optimal 80%, base 2.50%, slope1 2.50%, slope2 50.00%, reserve factor 20%; Aave v3 UNI optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 USDC optimal 94%, base 0.00%, slope1 4.30%, slope2 10.00%, reserve factor 10%; Aave v3 USDG optimal 80%, base 0.00%, slope1 5.00%, slope2 30.00%, reserve factor 20%; Aave v3 USDS optimal 92%, base 5.50%, slope1 0.75%, slope2 35.00%, reserve factor 25%; Aave v3 USDT optimal 94%, base 0.00%, slope1 4.30%, slope2 10.00%, reserve factor 10%; Aave v3 USDe optimal 90%, base 5.00%, slope1 2.00%, slope2 12.00%, reserve factor 25%; Aave v3 USDtb optimal 80%, base 0.00%, slope1 4.00%, slope2 50.00%, reserve factor 20%; Aave v3 WBTC optimal 80%, base 0.25%, slope1 2.50%, slope2 300.00%, reserve factor 50%; Aave v3 WETH optimal 92%, base 0.00%, slope1 2.20%, slope2 6.00%, reserve factor 15%; Aave v3 cbBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 cbETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 crvUSD optimal 80%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 20%; Aave v3 ezETH optimal 45%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 15%; Aave v3 rETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 rsETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 sDAI optimal 90%, base 0.00%, slope1 5.00%, slope2 75.00%, reserve factor 20%; Aave v3 sUSDe optimal 90%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 20%; Aave v3 tBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 weETH optimal 30%, base 1.00%, slope1 7.00%, slope2 300.00%, reserve factor 45%; Aave v3 wstETH optimal 80%, base 0.00%, slope1 1.00%, slope2 40.00%, reserve factor 35%.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| SparkLend | USDS | 4 | 3.96% → 3.93% | 3.86% – 3.96% | 2.36% → 2.32% |
| Aave v3 | USDe | 25 | 5.85% → 5.84% | 5.84% – 5.85% | 1.69% → 1.65% |
| Aave v3 | USDC | 95 | 4.27% → 4.28% | 4.27% – 4.28% | 3.59% → 3.60% |
| Aave v3 | WETH | 41 | 2.02% → 2.02% | 2.02% – 2.02% | 1.41% → 1.41% |
| Aave v3 | USDT | 30 | 4.27% → 4.27% | 4.27% – 4.27% | 3.58% → 3.58% |
| Aave v3 | DAI | 3 | 4.71% → 4.71% | 4.71% – 4.71% | 3.07% → 3.07% |
| Aave v3 | WBTC | 6 | 0.34% → 0.34% | 0.34% – 0.34% | 0.00% → 0.00% |
| Aave v3 | cbBTC | 1 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| Aave v3 | wstETH | 9 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | GHO | 1 | 4.00% → 4.00% | 4.00% – 4.00% | 0.00% → 0.00% |
| Aave v3 | weETH | 3 | 1.00% → 1.00% | 1.00% – 1.00% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 1 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | RLUSD | 1 | 4.42% → 4.42% | 4.42% – 4.42% | 2.18% → 2.18% |
| Aave v3 | EURC | 1 | 4.06% → 4.06% | 4.06% – 4.06% | 2.42% → 2.42% |
| Aave v3 | 0xd11c…5ed8 | 1 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | USDT | 1 | 3.52% → 3.52% | 3.52% – 3.52% | 2.62% → 2.62% |
| Aave v3 | LBTC | 1 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | USDG | 1 | 3.65% → 3.65% | 3.65% – 3.65% | 1.70% → 1.70% |

Volumes by venue and kind: Aave v3: atomic supply $777k, borrow $7.9M, supply $16.9M, atomic withdraw $777k, withdraw $10.0M, repay $5.3M; SparkLend: borrow $4.0M, supply $6.1M, repay $8.0M, withdraw $12.2M.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25930525 | SparkLend | withdraw | USDS | $12.2M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x07e2…bad6](https://etherscan.io/tx/0x07e2e82dfb0aadab4dd7ff59e62e092012b6adbce5fe0c1b785328770b23bad6) |
| 25930516 | SparkLend | repay | USDS | $8.0M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0x3565…ec16](https://etherscan.io/tx/0x35652045acbfb04e32cae8c1d82031eee61416ef03749b200908e8171e8dec16) |
| 25930406 | Aave v3 | supply | USDe | $7.6M | [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) | [0x3ade…8479](https://etherscan.io/tx/0x3adefe648b55594c056a5dc16fca5d44f641217e010e3c23f1cf375608158479) |
| 25930442 | SparkLend | supply | USDS | $6.1M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x403b…1fe3](https://etherscan.io/tx/0x403b5cd7a714541df009abcb54bc99f4dd3efa050c3998e143fb4b7459361fe3) |
| 25930432 | SparkLend | borrow | USDS | $4.0M | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | [0xefc8…2b76](https://etherscan.io/tx/0xefc8f23fd31078622c2b0928bb20d307619e276b3250fe1417f7be16b5ed2b76) |
| 25930419 | Aave v3 | borrow | USDC | $2.0M | [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) | [0xc32c…aedc](https://etherscan.io/tx/0xc32cf5a1adf66b30e92779bc18271b414b89598ef87843943d6d4a0e9ddfaedc) |
| 25930491 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xf881…d2fb](https://etherscan.io/tx/0xf881494744850a557bc8d1b585fae75345d997b10c3619de7f1f47065f48d2fb) |
| 25930491 | Aave v3 | withdraw | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x7a9f…00e9](https://etherscan.io/tx/0x7a9fd3c75036517d4c89d91da150f3c1e9a0810269655c26146d2bb88af400e9) |
| 25930323 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x4b58…cad0](https://etherscan.io/tx/0x4b58bce0a9032124e62aa27fedf3ede8a897ed2fc23ecba6836dc62c3ebbcad0) |
| 25930252 | Aave v3 | borrow | WETH | $1.6M | [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | [0x100d…9776](https://etherscan.io/tx/0x100da1a49670cc42e57a88f723d4c9c2f824f4cfba57190eb23a811e51c59776) |
| 25930297 | Aave v3 | withdraw | weETH | $1.1M | [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) | [0x94a9…9e15](https://etherscan.io/tx/0x94a9317fea28ce5d84ebc6816fd17f68f8b2ec4ddb3a8a23fc382cde2bd59e15) |
| 25930326 | Aave v3 | supply | WETH | $756k | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | [0xa0ed…03e6](https://etherscan.io/tx/0xa0ed56b74e65bed45a69f4e1ef1dd4b80cadaa074083415f33d961e9804203e6) |
| 25930326 | Aave v3 | withdraw | WETH | $756k | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | [0x4d45…fe10](https://etherscan.io/tx/0x4d45503a42db1ee71f951896e58af9292f7b52926ab490dac5332fb72119fe10) |
| 25930326 | Aave v3 | repay | USDC | $610k | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | [0x4d45…fe10](https://etherscan.io/tx/0x4d45503a42db1ee71f951896e58af9292f7b52926ab490dac5332fb72119fe10) |
| 25930322 | Aave v3 | repay | USDT | $550k | [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) | [0xada1…03b3](https://etherscan.io/tx/0xada1bf6ce9dd70633b6b3fcc19f19443584dd230b56326120e0e32384d6f03b3) |
| 25930265 | Aave v3 | supply | wstETH | $439k | [0x36e8…069a](https://etherscan.io/address/0x36e8abde1a6c07475b94794ae36507c556eb069a) | [0x66be…ecb9](https://etherscan.io/tx/0x66be06f57f41d3b7c7f9d7489854379c9fc93dd21ed62cf38ad0dc4dfcccecb9) |
| 25930302 | Aave v3 | withdraw | sUSDe | $405k | [0x8661…20c6](https://etherscan.io/address/0x8661f478c6ccd6fae875084917f763e9c9cf20c6) | [0xe32a…cb4d](https://etherscan.io/tx/0xe32a4a42c6d33a5bdd0f50503585f16215a6dcbb9d9dc3f688eac85da1edcb4d) |
| 25930296 | Aave v3 | repay | USDe | $395k | [0x8661…20c6](https://etherscan.io/address/0x8661f478c6ccd6fae875084917f763e9c9cf20c6) | [0xa85a…ddfc](https://etherscan.io/tx/0xa85a4f19a6403430266ee9909d4f85fd7f79b993c5ca567ac84939c93108ddfc) |
| 25930268 | Aave v3 | repay | WBTC | $315k | [0x3178…b80c](https://etherscan.io/address/0x3178490d60b5cceaa5a79fd4d9050c7405bab80c) | [0x5efb…0f15](https://etherscan.io/tx/0x5efbe4a58adc78c97c1ac3eb1b02a1a1521cdcf58739eec791dabfcb2c2e0f15) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- SparkLend withdraw $12.2M USDS by [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) ([0x07e2…bad6](https://etherscan.io/tx/0x07e2e82dfb0aadab4dd7ff59e62e092012b6adbce5fe0c1b785328770b23bad6)): $126k → [DaiUsds (blockscout-verified)](https://etherscan.io/address/0x3225737a9bbb6473cb4a45b7244aca2befdb276a); $12.1M → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $101k → [DaiUsds (blockscout-verified)](https://etherscan.io/address/0x3225737a9bbb6473cb4a45b7244aca2befdb276a); $200k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90)
- SparkLend borrow $4.0M USDS by [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) ([0xefc8…2b76](https://etherscan.io/tx/0xefc8f23fd31078622c2b0928bb20d307619e276b3250fe1417f7be16b5ed2b76)): $4.0M → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)
- Aave v3 borrow $2.0M USDC by [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) ([0xc32c…aedc](https://etherscan.io/tx/0xc32cf5a1adf66b30e92779bc18271b414b89598ef87843943d6d4a0e9ddfaedc)): $470k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996); $1.5M → [0x3bbc…e0ec](https://etherscan.io/address/0x3bbcb84fcde71063d8c396e6c54f5dc3d19ee0ec)
- Aave v3 withdraw $1.8M WETH by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x7a9f…00e9](https://etherscan.io/tx/0x7a9fd3c75036517d4c89d91da150f3c1e9a0810269655c26146d2bb88af400e9)): $1.8M → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $1.8M → [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e)
- Aave v3 borrow $1.6M WETH by [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) ([0x100d…9776](https://etherscan.io/tx/0x100da1a49670cc42e57a88f723d4c9c2f824f4cfba57190eb23a811e51c59776)): $185k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $61k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $35k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $183k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 withdraw $1.1M weETH by [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) ([0x94a9…9e15](https://etherscan.io/tx/0x94a9317fea28ce5d84ebc6816fd17f68f8b2ec4ddb3a8a23fc382cde2bd59e15)): $1.1M → [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9)
- Aave v3 withdraw $756k WETH by [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ([0x4d45…fe10](https://etherscan.io/tx/0x4d45503a42db1ee71f951896e58af9292f7b52926ab490dac5332fb72119fe10)): $756k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 withdraw $405k sUSDe by [0x8661…20c6](https://etherscan.io/address/0x8661f478c6ccd6fae875084917f763e9c9cf20c6) ([0xe32a…cb4d](https://etherscan.io/tx/0xe32a4a42c6d33a5bdd0f50503585f16215a6dcbb9d9dc3f688eac85da1edcb4d)): $405k → [zero address (mint/burn) (known-canonical)](https://etherscan.io/address/0x0000000000000000000000000000000000000000)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| Aave v3 | [0xc468…4ca6](https://etherscan.io/address/0xc468315a2df54f9c076bd5cfe5002ba211f74ca6) | $117.9M | $103.2M | 1.062 | 5.8% |
| SparkLend | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | $127.3M | $44.8M | 2.442 | 59.0% |
| SparkLend | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | $98.8M | $14.9M | 5.705 | 82.5% |
| Aave v3 | [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | $7.4M | $6.8M | 1.035 | 3.3% |
| Aave v3 | [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) | $6.9M | $4.0M | 1.379 | 27.5% |
| SparkLend | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | $54.1M | $0 | ∞ | – |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| Aave v3 | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | $0 | $0 | ∞ | – |

Flash loans (events): BalFlash 42 ($83k).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb): 2 transactions, largest leg $756k, gross $777k; legs: WETH withdraw $777k

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 157 | $5.9M | 0.9997 | 0.999682 – 0.999737 | 0.999857 | -1.6 bps |
| USDS | 63 | $4.1M | 1.00005 | 1.00001 – 1.00006 | 1 | +0.5 bps |
| DAI | 36 | $3.7M | 1.00004 | 1.00002 – 1.00006 | 0.999575 | +4.7 bps |
| USDe | 48 | $2.9M | 0.999614 | 0.999535 – 0.999936 | 1 | -3.9 bps |
| crvUSD | 35 | $2.2M | 0.99986 | 0.999669 – 0.99995 | 1 | -1.4 bps |
| USDG | 59 | $1.8M | 0.999946 | 0.999907 – 0.999993 | 1 | -0.5 bps |
| frxUSD | 22 | $694k | 0.999973 | 0.999711 – 0.999999 | 1 | -0.3 bps |
| PYUSD | 3 | $482k | 1.00003 | 0.999788 – 1.00008 | 1 | +0.3 bps |
| RLUSD | 3 | $401k | 1.00019 | 1.00019 – 1.00019 | 1 | +1.9 bps |
| PAXG | 31 | $126k | 4429.21 | 4425.79 – 4436.36 | – | – |
| sUSDe | 15 | $88k | 1.24646 | 1.24583 – 1.2467 | 1.24705 | -4.7 bps |
| INJ | 29 | $64k | 6.53589 | 6.43341 – 6.6273 | – | – |
| ANYONE | 29 | $59k | 0.215567 | 0.208959 – 0.222462 | – | – |
| PEPE | 17 | $52k | 3.61064e-06 | 3.5981e-06 – 3.62167e-06 | – | – |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 188 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDT | $53.6M | $54.6M | $-1.0M |
| USDC | $48.9M | $49.5M | $-660k |
| ETH | $14.1M | $8.5M | $5.6M |
| USD1 | $4.0M | $0 | $4.0M |
| RLUSD | $100k | $3.3M | $-3.2M |
| UNI | $253k | $2.1M | $-1.8M |
| LINK | $1.8M | $315k | $1.5M |
| CRV | $607k | $0 | $607k |
| USDG | $96k | $312k | $-216k |
| AAVE | $106k | $36k | $70k |
| EURC | $0 | $118k | $-118k |
| WBTC | $55k | $20k | $36k |

By label: Coinbase 11 (model-memory) in $27.3M / out $33.8M; hot wallet (behaviour, day study) in $29.2M / out $20.7M; Binance 14 (model-memory) in $32.4M / out $6.0M; Coinbase 10 (model-memory) in $11.6M / out $9.2M; Binance 15 (model-memory) in $0 / out $16.6M; Gate.io (model-memory) in $11.3M / out $3.4M; Binance 16 (model-memory) in $0 / out $11.7M; hot wallet (day study, unidentified) (model-memory) in $6.5M / out $1.5M; Binance 18 (model-memory) in $0 / out $6.2M; Bitfinex 2 (model-memory) in $4.0M / out $1.5M; Binance 17 (model-memory) in $0 / out $4.9M; Bitget (model-memory) in $1.3M / out $881k.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25930284 | WBTC | $434.0M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x2577…ace9](https://etherscan.io/tx/0x25772f682cd81937886aaf18419a843aee81317deca048b4f140635b5f0aace9) |
| 25930284 | WBTC | $434.0M ×2 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x2577…ace9](https://etherscan.io/tx/0x25772f682cd81937886aaf18419a843aee81317deca048b4f140635b5f0aace9) |
| 25930508 | USDC | $95.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xd4ef…1b99](https://etherscan.io/tx/0xd4ef3e6214fe3be46e63f5d09a9d3791443888d4ea3f718beb818e376c3e1b99) |
| 25930508 | USDC | $95.5M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd4ef…1b99](https://etherscan.io/tx/0xd4ef3e6214fe3be46e63f5d09a9d3791443888d4ea3f718beb818e376c3e1b99) |
| 25930284 | USDC | $95.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x2577…ace9](https://etherscan.io/tx/0x25772f682cd81937886aaf18419a843aee81317deca048b4f140635b5f0aace9) |
| 25930284 | USDC | $95.1M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x2577…ace9](https://etherscan.io/tx/0x25772f682cd81937886aaf18419a843aee81317deca048b4f140635b5f0aace9) |
| 25930415 | USDC | $94.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x1837…b921](https://etherscan.io/tx/0x1837278bf14d717d8fe030f67ffee45dddc6ebd2aba21ac11ac8d5348936b921) |
| 25930415 | USDC | $94.5M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1837…b921](https://etherscan.io/tx/0x1837278bf14d717d8fe030f67ffee45dddc6ebd2aba21ac11ac8d5348936b921) |
| 25930319 | USDC | $86.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0x707c…2d58](https://etherscan.io/tx/0x707cbff493399542a71280a8628e1f61dc48fe226cc09111b3b2c0c748bd2d58) |
| 25930319 | USDC | $86.7M | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x707c…2d58](https://etherscan.io/tx/0x707cbff493399542a71280a8628e1f61dc48fe226cc09111b3b2c0c748bd2d58) |
| 25930443 | USDC | $85.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x88e7…0233](https://etherscan.io/tx/0x88e77fe40156b7aaf223e813270c510a568a399dc1185cacc97f75a630fd0233) |
| 25930443 | USDC | $85.8M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x88e7…0233](https://etherscan.io/tx/0x88e77fe40156b7aaf223e813270c510a568a399dc1185cacc97f75a630fd0233) |
| 25930327 | WBTC | $78.9M | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0x3805…7e5c](https://etherscan.io/address/0x3805dbbd0b847f3dee193ae546cc20caaf7e7e5c) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930327 | WBTC | $78.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xbfed…48f1](https://etherscan.io/address/0xbfedfd3c88bad9ef47dae4627ee054eab3a548f1) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930327 | WBTC | $78.9M | [0xbfed…48f1](https://etherscan.io/address/0xbfedfd3c88bad9ef47dae4627ee054eab3a548f1) | [0x3805…7e5c](https://etherscan.io/address/0x3805dbbd0b847f3dee193ae546cc20caaf7e7e5c) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930327 | WBTC | $78.9M | [0x3805…7e5c](https://etherscan.io/address/0x3805dbbd0b847f3dee193ae546cc20caaf7e7e5c) | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930327 | WBTC | $78.9M | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930327 | WBTC | $78.9M | [0x3805…7e5c](https://etherscan.io/address/0x3805dbbd0b847f3dee193ae546cc20caaf7e7e5c) | [0xbfed…48f1](https://etherscan.io/address/0xbfedfd3c88bad9ef47dae4627ee054eab3a548f1) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930327 | WBTC | $78.9M | [0xbfed…48f1](https://etherscan.io/address/0xbfedfd3c88bad9ef47dae4627ee054eab3a548f1) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x5d76…3815](https://etherscan.io/tx/0x5d76d0e304ec4551895d4fd5cacf6509ff72ef5571070ab502d9fdecbfec3815) |
| 25930323 | USDT | $38.4M | [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) | [0x72ec…f903](https://etherscan.io/address/0x72ec2e073324960a4ec15758bab80f9ffd53f903) | [0x4ff8…1692](https://etherscan.io/tx/0x4ff89904dbb22e9bf861125aa2df08b400da96b6b6ba1697c042dc9db3971692) |
| 25930295 | USDT | $29.3M | [0xccdc…a91e](https://etherscan.io/address/0xccdcfc4598f539408fc0393b42905c1e0d24a91e) | [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) | [0xe734…92e3](https://etherscan.io/tx/0xe734fdcf6c5bbacd586d6face91bcd70ee2cc2a87a4a52c8b5f69c7c158792e3) |
| 25930342 | USDT | $28.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xd648…fed0](https://etherscan.io/tx/0xd648b8c78708c504dd610811235005379a36aab5d09a65b99dd10ca728a4fed0) |
| 25930342 | USDT | $28.7M | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd648…fed0](https://etherscan.io/tx/0xd648b8c78708c504dd610811235005379a36aab5d09a65b99dd10ca728a4fed0) |
| 25930362 | USDT | $28.7M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xaa92…1c42](https://etherscan.io/tx/0xaa9291556f7109408080a8e244be94bd4357c53d1192b8089ed90b0ebac21c42) |
| 25930362 | USDT | $28.7M ×2 | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xaa92…1c42](https://etherscan.io/tx/0xaa9291556f7109408080a8e244be94bd4357c53d1192b8089ed90b0ebac21c42) |
| 25930538 | USDT | $28.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0000…e69d](https://etherscan.io/address/0x0000000000be226afde21672a5e4adc45692e69d) | [0x2176…7eac](https://etherscan.io/tx/0x2176b2e5bf4622d2a4ed1346033ec289cfe0db5182a4df4113ead66e69a27eac) |
| 25930538 | USDT | $28.7M | [0x0000…e69d](https://etherscan.io/address/0x0000000000be226afde21672a5e4adc45692e69d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x2176…7eac](https://etherscan.io/tx/0x2176b2e5bf4622d2a4ed1346033ec289cfe0db5182a4df4113ead66e69a27eac) |
| 25930284 | WETH | $28.4M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x2577…ace9](https://etherscan.io/tx/0x25772f682cd81937886aaf18419a843aee81317deca048b4f140635b5f0aace9) |
| 25930284 | WETH | $28.4M ×2 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x2577…ace9](https://etherscan.io/tx/0x25772f682cd81937886aaf18419a843aee81317deca048b4f140635b5f0aace9) |
| 25930262 | WETH | $25.8M ×3 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x9a52…f412](https://etherscan.io/tx/0x9a52d6f412be6ff529a3858bc8887674478c48d6fefd74274142d2aa178af412) |

Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0xbb06…0001](https://etherscan.io/address/0xbb0611fde3e968d138eb3e9e386d8103c4730001) | USDT → DAI | 5 | $271k | $60k | 252s | 0.54 | 0.13 | curve 5 |
| [0x0250…b9b6](https://etherscan.io/address/0x025080f14aa3305049f9ce08d7b92368d54cb9b6) | crvUSD → frxUSD | 5 | $300k | $45k | 168s | 0.53 | 0.48 | curve 5 |
| [0x0250…b9b6](https://etherscan.io/address/0x025080f14aa3305049f9ce08d7b92368d54cb9b6) | USDT → crvUSD | 5 | $300k | $45k | 168s | 0.53 | 0.48 | curve 5 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25930370 | curve | USDT → USDC | $1.2M | [0x75ed…ec28](https://etherscan.io/address/0x75ed83132a7c7af97dbe6d29efa396885e07ec28) | [0x8cfe…22cd](https://etherscan.io/tx/0x8cfe0a441290930ec9da32356e078b2708664c1ed194991d62826142721422cd) |

## E. Bridges, issuance, staking

Outbound: $16.6M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $8.7M (66).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| OFT | USDC | BNB | 10 | $7.8M | – |
| CCTP | USDC | Polygon | 12 | $3.7M | 0xf70da97812cb… $3.6M |
| CCTP | USDC | domain 15 | 6 | $1.9M | 0x65c340eb0688… $1.6M |
| CCTP | USDC | Avalanche | 1 | $1.5M | 0x3bbcb84fcde7… $1.5M |
| OFT | USDG | eid 30416 | 4 | $321k | – |
| CCTP | USDC | Arbitrum | 7 | $309k | 0x6a2abff960b6… $257k |
| OFT | USDT | BNB | 7 | $296k | – |
| CCTP | USDC | Solana | 15 | $265k | 122058680a4d6e… $203k |
| OFT | USDT | eid 30420 | 5 | $128k | – |
| OFT | USDe | eid 30383 | 2 | $110k | – |
| CCTP | USDC | Base | 23 | $81k | 0x769e68219798… $70k |
| CCTP | USDC | domain 31 | 1 | $21k | 0xea2368f8afbb… $21k |
| CCTP | USDC | domain 19 | 6 | $15k | 0xb21d281dedb1… $15k |
| CCTP | USDC | OP Mainnet | 1 | $12k | 0x3a6a72459518… $12k |
| OFT | USDT | eid 30274 | 1 | $11k | – |
| OFT | USDe | BNB | 1 | $8163 | – |
| OFT | AUSD | eid 30390 | 1 | $4038 | – |
| CCTP | USDC | Sui | 1 | $1092 | 39bb1dfbe50fba… $1092 |
| OFT | PYUSD | Arbitrum | 2 | $415 | – |
| OFT | USDC | Arbitrum | 1 | $200 | – |

Issuance totals: USDC burn $24.2M (84); USDC mint $32.2M (126). Largest: USDC mint $7.8M ([0xe0fb…7b94](https://etherscan.io/tx/0xe0fb76cb8febf41c063c0dd3b9988a410748f064c71530835bad0dad31e17b94)); USDC burn $5.0M ([0xa147…bb3a](https://etherscan.io/tx/0xa1478adc08ae84605e1c231c60447e0194e3153e0a13bbf431919e7bf49abb3a)); USDC mint $5.0M ([0xfa52…0818](https://etherscan.io/tx/0xfa524b2401076e147a3031868ac69f3233c10c6ad29fa4109ef2d6b1e2050818)); USDC burn $5.0M ([0x4de4…58f6](https://etherscan.io/tx/0x4de440d7c5c3e823994f0153c2945cc96ec9c2eea09d4566ce00da06be6d58f6)); USDC burn $3.3M ([0x2d78…fd32](https://etherscan.io/tx/0x2d7875fcf46c8b29205d7d5dfb01ad4214db541fad461ecfca2c32994115fd32)).


WETH wrapped 1851 ETH, unwrapped 2297 ETH; Lido staked 17.3 ETH, withdrawal requests 735.4 ETH; sUSDe cooldowns 2 for $412k.


## F. Gas market and block production

Base fee 0.051 → 0.049 gwei (min 0.042, median 0.05, max 0.071); blocks 51% full; median tip 0.025 gwei; 4.7% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 130,  Quasar (quasar.win)  66, Eureka (eurekabuilder.xyz) 47, BuilderNet 25, gethgo1.26.4linux 5, gethgo1.26.5linux 2.


Most active senders: [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 975, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x91d40e4818f4d4c57b4578d9eca6afc92ac8debe) 772, [0xeb94…9665](https://etherscan.io/address/0xeb943c230218e0da7b2ca18b81f7eb7fbbbe9665) 595, [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 466, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 351, [Relay solver / USDG inventory wallet (takes 100% of RelayDepository payouts on Ethereum and Robinhood Chain; Paxos mint-and-redeem counterparty on both) (etherscan-verified)](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) 350, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 346, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 288, [hot wallet (behaviour, day study)](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460) 252, [0x0dcc…ebcb](https://etherscan.io/address/0x0dcc12ce46cb992f7db6772c49bc74713eb7ebcb) 246.


Intent fills: OneInchFilled 228, UniXFill 31, CoWTrade 120. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

