_(no insights.md written yet)_

---

## Deterministic tables — 9 chains, 13:09 to 15:09 UTC

Benchmark: **Sky savings rate (SSR), read on Ethereum at block 26256177 = 3.80%**. Every rate below is a supply APR; "priced utilisation" is inverted from the pool's own published borrow rate rather than taken from the aToken ratio (see `multichain.py`, `implied_utilisation`).


### The same dollar, across chains

| asset | chains | high | low | spread | supplied |
|---|---:|---|---|---:|---:|
| USDS | 2 | base 91.23% | ethereum 2.68% | 88.55pp | $1.29B |
| USDC | 8 | linea 11.15% | scroll 0.06% | 11.09pp | $2.90B |
| DAI | 5 | polygon 3.96% | base 1.34% | 2.62pp | $272.1M |
| GHO | 4 | arbitrum 4.97% | ethereum 2.73% | 2.24pp | $57.2M |
| USDT | 3 | optimism 4.08% | ethereum 3.36% | 0.72pp | $2.86B |
| USDe | 2 | ethereum 0.23% | avalanche 0.03% | 0.20pp | $256.2M |
| sUSDS | 2 | base 0.00% | ethereum 0.00% | 0.00pp | $3.0M |
| sUSDe | 2 | avalanche 0.00% | ethereum 0.00% | 0.00pp | $104.1M |

### USDC reserve by reserve

| chain | supply APR | priced util | supplied | withdrawable | rate source |
|---|---:|---:|---:|---:|---|
| linea | 11.15% | 0.9813 | $1.1M | $21k | head spot (unchecked: 1 updates) |
| avalanche | 7.85% | 0.9530 | $69.1M | $3.2M | window time-weighted |
| optimism | 4.77% | 0.9178 | $10.6M | $868k | window time-weighted |
| base | 4.64% | 0.9114 | $189.9M | $16.8M | window time-weighted |
| ethereum | 3.86% | 0.9418 | $2.38B | $138.7M | window time-weighted |
| polygon | 3.29% | 0.6502 | $26.9M | $9.4M | window time-weighted |
| arbitrum | 2.44% | 0.7814 | $218.3M | $47.7M | window time-weighted |
| scroll | 0.06% | 0.7408 | $244k | $63k | head spot (unchecked: 0 updates) |

### Every cross-chain dollar switch that pays, filled once

Size is `min(the high side's optimum before it dilutes, the low side's withdrawable liquidity)`. Destinations are filled cheapest-source-first, because the rows compete for the same reserve.

| asset | earn on | move from | size | APR at size | leaving | $/year |
|---|---|---|---:|---:|---:|---:|
| DAI | polygon | arbitrum | $933k | 2.55% | 1.36% | $11k |
| USDC | linea | scroll | $63k | 6.23% | 0.06% | $4k |
| USDC | linea | arbitrum | $143k | 3.10% | 2.44% | $950 |
| USDS | base | ethereum | $4k | 44.33% | 2.68% | $2k |
| DAI | polygon | optimism | $71k | 2.48% | 2.12% | $251 |
| USDe | ethereum | avalanche | $261k | 0.23% | 0.03% | $532 |
| GHO | arbitrum | ethereum | $47k | 3.18% | 2.73% | $208 |
| USDT | optimism | ethereum | $90k | 3.52% | 3.36% | $143 |
| DAI | polygon | base | $940 | 2.48% | 1.34% | $11 |
| sUSDS | base | ethereum | $47k | 0.00% | 0.00% | $0 |
| **total** | | | **$1.7M** | | | **$19k** |

Sum of the rows taken independently would say $29k — 57% higher, because each row assumes the destination reserve is empty.


### CCTP: where the dollars actually went, against where the yield is

| chain | net CCTP USDC | in | out | USDC APR | net USDC issued |
|---|---:|---:|---:|---:|---:|
| ethereum | $30.5M | $41.5M | $11.0M | 3.86% | $-41.2M |
| arbitrum | $410k | $14.3M | $13.9M | 2.44% | $1.5M |
| avalanche | $336k | $3.0M | $2.6M | 7.85% | $2.1M |
| optimism | $258k | $660k | $402k | 4.77% | $383k |
| unichain | $70k | $74k | $4k | - | $70k |
| linea | $18k | $19k | $1k | 11.15% | $18k |
| scroll | $0 | $0 | $0 | 0.06% | $0 |
| polygon | $-1.2M | $541k | $1.7M | 3.29% | $-4.9M |
| base | $-2.2M | $1.6M | $3.8M | 4.64% | $-3.6M |

Rank correlation between a chain's USDC supply rate and its net CCTP flow this hour: **0.05** (n=8). Negative means the dollars moved toward the lower rate.


### The gas market, ten chains, one hour

| chain | blocks | block time | txs/hour | fullness | base fee (gwei) | native $ | base fee $/hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| ethereum | 600 | 12.02s | 160,240 | 47.5% | 0.216861 | 2395.86 | $8726 |
| base | 3601 | 2.00s | 1,243,725 | 17.4% | 0.006981 | 2395.86 | $4287 |
| polygon | 4801 | 1.50s | 573,079 | 24.1% | 247.802651 | 0.09 | $4233 |
| arbitrum | 28057 | 0.26s | 231,470 | 0.0% | 0.020088 | 2395.86 | $1661 |
| avalanche | 8646 | 0.83s | 51,011 | 2.9% | 2.658730 | 9.08 | $520 |
| unichain | 7201 | 1.00s | 64,089 | 1.2% | 0.000500 | 2395.86 | $6 |
| scroll | 1313 | 5.49s | 1,816 | 1.1% | 0.000120 | 2395.86 | $0 |
| linea | 934 | 7.70s | 1,479 | 0.0% | 0.000000 | 2395.86 | $0 |
| optimism | 3601 | 2.00s | 134,317 | 27.6% | 0.000000 | 2395.86 | $0 |
| **total** | | | | | | | **$19433** |

Fullness is `gas used / gas limit` over evenly sampled headers; Arbitrum posts a sentinel gas limit so its share is not meaningful and is shown as n/a.


### Reserves excluded from the surface

| chain | asset | supplied | why |
|---|---|---:|---|
| arbitrum | FRAX | $49k | reserve factor 1.0: the whole borrow rate goes to the treasury, so this is a mint facility, not a supply market |
| arbitrum | LUSD | $72k | reserve factor 1.0: the whole borrow rate goes to the treasury, so this is a mint facility, not a supply market |
| ethereum | GHO | $135.3M | reserve factor 1.0: the whole borrow rate goes to the treasury, so this is a mint facility, not a supply market |
| ethereum | LUSD | $1.9M | reserve factor 1.0: the whole borrow rate goes to the treasury, so this is a mint facility, not a supply market |
| ethereum | FRAX | $30k | reserve factor 1.0: the whole borrow rate goes to the treasury, so this is a mint facility, not a supply market |

### Verification

`multichain.py verify` — 17 numeric checks, 6 identities, all_ok = **True**.

| identity | checked | failed | worst deviation |
|---|---:|---:|---:|
| utilisation equals borrowed / supplied | 60 | 0 | 0.00e+00 |
| supply APR equals borrow APR x priced utilisation x (1 - reserve factor) | 60 | 0 | 1.85e-04 |
| the reserve IRM reproduces the pool's published borrow rate at the inverted utilisation | 60 | 0 | 1.93e-03 |
| supply APR replays from the curve at the effective liquidity base | 60 | 0 | 1.85e-04 |
| the time-weighted rate lies between the window min and max | 10 | 0 | 0.00e+00 |
| every switch fits the source liquidity and its APR replays on the curve | 19 | 0 | 0.00e+00 |

**The liquidity base the pool actually prices at, versus the aToken ratio.** Reading `variableDebt.totalSupply() / aToken.totalSupply()` is close to right and occasionally very wrong; near a kink the error is multiplied by the slope.

| chain | asset | u (aToken) | u (priced) | gap | borrow-rate error if the aToken ratio is used |
|---|---|---:|---:|---:|---:|
| optimism | USDT | 0.931796 | 0.915956 | -1.5840pp | 11.880pp |
| optimism | DAI | 0.827694 | 0.773923 | -5.3771pp | 10.565pp |
| base | USDS | 0.910967 | 0.907675 | -0.3293pp | 3.293pp |
| avalanche | FRAX | 1.002900 | 0.998248 | -0.4652pp | 1.861pp |
| optimism | USDC | 0.804460 | 0.743586 | -6.0875pp | 0.372pp |
| ethereum | USDT | 0.950525 | 0.950411 | -0.0114pp | 0.034pp |
| optimism | USDT | 0.904056 | 0.904363 | +0.0307pp | 0.031pp |
| arbitrum | USDC | 0.927655 | 0.927720 | +0.0065pp | 0.026pp |

**Dollars leaving for domains outside this scan.** $19.9M burned for Circle domains no scanned chain resolved, against $13.6M for chains inside it.

| domain | USDC burned for it |
|---:|---:|
| 15 | $800k |
| 16 | $7k |
| 19 | $8.4M |
| 21 | $24k |
| 22 | $88k |
| 25 | $11k |
| 26 | $4.7M |
| 27 | $67k |
| 29 | $1k |
| 31 | $8k |
| 37 | $327 |
