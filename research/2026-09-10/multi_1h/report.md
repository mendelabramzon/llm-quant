_(no insights.md written yet)_

---

## Deterministic tables — 10 chains, 12:52 to 13:52 UTC

Benchmark: **Sky savings rate (SSR), read on Ethereum at block 25942222 = 3.60%**. Every rate below is a supply APR; "priced utilisation" is inverted from the pool's own published borrow rate rather than taken from the aToken ratio (see `multichain.py`, `implied_utilisation`).


### The same dollar, across chains

| asset | chains | high | low | spread | supplied |
|---|---:|---|---|---:|---:|
| FRAX | 3 | avalanche 23.10% | arbitrum 0.40% | 22.71pp | $217k |
| USDC | 9 | avalanche 7.19% | scroll 0.37% | 6.83pp | $2.78B |
| GHO | 3 | avalanche 9.44% | arbitrum 2.63% | 6.81pp | $3.2M |
| USDe | 2 | avalanche 3.59% | ethereum 1.04% | 2.55pp | $667.7M |
| LUSD | 3 | optimism 2.64% | ethereum 0.54% | 2.10pp | $2.1M |
| DAI | 4 | polygon 3.88% | arbitrum 1.91% | 1.97pp | $315.8M |
| USDT | 4 | ethereum 3.86% | optimism 2.85% | 1.01pp | $3.02B |
| USDS | 2 | ethereum 2.32% | base 1.71% | 0.61pp | $935.7M |
| sUSDS | 2 | base 0.00% | ethereum 0.00% | 0.00pp | $3.0M |
| sUSDe | 2 | avalanche 0.00% | ethereum 0.00% | 0.00pp | $196.7M |

### USDC reserve by reserve

| chain | supply APR | priced util | supplied | withdrawable | rate source |
|---|---:|---:|---:|---:|---|
| avalanche | 7.19% | 0.9409 | $59.3M | $3.5M | window time-weighted |
| ethereum | 3.71% | 0.9390 | $2.31B | $140.9M | window time-weighted |
| base | 3.70% | 0.8886 | $183.8M | $20.5M | window time-weighted |
| linea | 3.36% | 0.8737 | $1.6M | $207k | head spot (unchecked: 1 updates) |
| bsc | 3.11% | 0.8406 | $14.1M | $2.3M | window time-weighted |
| polygon | 2.87% | 0.5987 | $29.8M | $12.0M | window time-weighted |
| arbitrum | 2.74% | 0.8280 | $169.8M | $29.2M | window time-weighted |
| optimism | 2.62% | 0.8097 | $11.2M | $2.1M | window time-weighted |
| scroll | 0.37% | 0.7414 | $249k | $64k | head spot (unchecked: 0 updates) |

### Every cross-chain dollar switch that pays, filled once

Size is `min(the high side's optimum before it dilutes, the low side's withdrawable liquidity)`. Destinations are filled cheapest-source-first, because the rows compete for the same reserve.

| asset | earn on | move from | size | APR at size | leaving | $/year |
|---|---|---|---:|---:|---:|---:|
| USDT | ethereum | bsc | $10.2M | 3.70% | 3.01% | $71k |
| USDC | avalanche | optimism | $2.1M | 4.27% | 2.62% | $35k |
| USDC | avalanche | polygon | $3.7M | 3.23% | 2.87% | $13k |
| USDC | avalanche | bsc | $625k | 3.17% | 3.11% | $377 |
| USDC | avalanche | arbitrum | $2.4M | 2.95% | 2.74% | $5k |
| USDT | ethereum | optimism | $848k | 3.70% | 2.85% | $7k |
| DAI | polygon | arbitrum | $683k | 2.77% | 1.91% | $6k |
| USDC | avalanche | scroll | $64k | 2.94% | 0.37% | $2k |
| DAI | polygon | ethereum | $131k | 2.61% | 2.46% | $198 |
| GHO | avalanche | arbitrum | $99k | 3.17% | 2.63% | $537 |
| USDS | ethereum | base | $48k | 2.32% | 1.71% | $294 |
| USDT | ethereum | linea | $54k | 3.70% | 3.39% | $168 |
| LUSD | optimism | ethereum | $13k | 1.28% | 0.54% | $97 |
| FRAX | avalanche | arbitrum | $4k | 1.71% | 0.40% | $54 |
| LUSD | optimism | arbitrum | $3k | 1.13% | 0.99% | $4 |
| USDe | avalanche | ethereum | $4k | 1.94% | 1.04% | $40 |
| sUSDS | base | ethereum | $67k | 0.00% | 0.00% | $0 |
| **total** | | | **$21.1M** | | | **$141k** |

Sum of the rows taken independently would say $272k — 93% higher, because each row assumes the destination reserve is empty.


### CCTP: where the dollars actually went, against where the yield is

| chain | net CCTP USDC | in | out | USDC APR | net USDC issued |
|---|---:|---:|---:|---:|---:|
| polygon | $3.6M | $5.3M | $1.7M | 2.87% | $3.4M |
| linea | $3k | $3k | $0 | 3.36% | $3k |
| bsc | $0 | $0 | $0 | 3.11% | $0 |
| scroll | $0 | $0 | $0 | 0.37% | $0 |
| unichain | $-189k | $233 | $189k | - | $-189k |
| base | $-417k | $1.2M | $1.6M | 3.70% | $-1.9M |
| arbitrum | $-1.5M | $5.0M | $6.6M | 2.74% | $-5.8M |
| avalanche | $-1.7M | $48k | $1.7M | 7.19% | $-446k |
| optimism | $-3.8M | $316k | $4.1M | 2.62% | $-5.8M |
| ethereum | $-4.6M | $8.4M | $13.0M | 3.71% | $-2.4M |

Rank correlation between a chain's USDC supply rate and its net CCTP flow this hour: **-0.27** (n=9). Negative means the dollars moved toward the lower rate.


### The gas market, ten chains, one hour

| chain | blocks | block time | txs/hour | fullness | base fee (gwei) | native $ | base fee $/hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| ethereum | 300 | 12.04s | 129,015 | 55.2% | 0.590791 | 2429.87 | $14174 |
| polygon | 2401 | 1.50s | 307,808 | 25.1% | 250.312490 | 0.09 | $2222 |
| base | 1801 | 2.00s | 594,090 | 14.3% | 0.005087 | 2466.15 | $1292 |
| arbitrum | 14395 | 0.25s | 106,763 | 0.0% | 0.020131 | 2466.15 | $924 |
| avalanche | 3392 | 1.06s | 46,697 | 7.9% | 0.114820 | 7.63 | $9 |
| unichain | 3601 | 1.00s | 47,773 | 1.8% | 0.000500 | 2466.15 | $5 |
| optimism | 1801 | 2.00s | 63,005 | 36.6% | 0.000058 | 2466.15 | $4 |
| bsc | 7997 | 0.45s | 1,016,685 | 58.6% | 0.000000 | 710.38 | $0 |
| linea | 558 | 6.46s | 930 | 0.0% | 0.000000 | 2466.15 | $0 |
| scroll | 757 | 4.76s | 858 | 1.1% | 0.000120 | 2466.15 | $0 |
| **total** | | | | | | | **$18630** |

Fullness is `gas used / gas limit` over evenly sampled headers; Arbitrum posts a sentinel gas limit so its share is not meaningful and is shown as n/a.


### Reserves excluded from the surface

| chain | asset | supplied | why |
|---|---|---:|---|
| ethereum | GHO | $135.2M | reserve factor 1.0: the whole borrow rate goes to the treasury, so this is a mint facility, not a supply market |

### Verification

`multichain.py verify` — 17 numeric checks, 6 identities, all_ok = **True**.

| identity | checked | failed | worst deviation |
|---|---:|---:|---:|
| utilisation equals borrowed / supplied | 63 | 0 | 0.00e+00 |
| supply APR equals borrow APR x priced utilisation x (1 - reserve factor) | 63 | 0 | 4.95e-04 |
| the reserve IRM reproduces the pool's published borrow rate at the inverted utilisation | 63 | 0 | 7.72e-04 |
| supply APR replays from the curve at the effective liquidity base | 63 | 0 | 4.95e-04 |
| the time-weighted rate lies between the window min and max | 12 | 0 | 0.00e+00 |
| every switch fits the source liquidity and its APR replays on the curve | 23 | 0 | 0.00e+00 |

**The liquidity base the pool actually prices at, versus the aToken ratio.** Reading `variableDebt.totalSupply() / aToken.totalSupply()` is close to right and occasionally very wrong; near a kink the error is multiplied by the slope.

| chain | asset | u (aToken) | u (priced) | gap | borrow-rate error if the aToken ratio is used |
|---|---|---:|---:|---:|---:|
| avalanche | GHO | 0.912716 | 0.917486 | +0.4770pp | 1.908pp |
| avalanche | FRAX | 0.962467 | 0.961365 | -0.1102pp | 0.441pp |
| bsc | USD1 | 0.441949 | 0.432984 | -0.8966pp | 0.056pp |
| arbitrum | USDC | 0.843333 | 0.838496 | -0.4837pp | 0.054pp |
| bsc | BUSD | 0.743913 | 0.733799 | -1.0114pp | 0.051pp |
| ethereum | USDtb | 0.814141 | 0.813998 | -0.0144pp | 0.036pp |
| bsc | USDT | 0.712647 | 0.706808 | -0.5839pp | 0.029pp |
| polygon | USDT0 | 0.929850 | 0.929375 | -0.0474pp | 0.028pp |

**Dollars leaving for domains outside this scan.** $17.2M burned for Circle domains no scanned chain resolved, against $11.7M for chains inside it.

| domain | USDC burned for it |
|---:|---:|
| 15 | $4.8M |
| 19 | $6.0M |
| 21 | $300 |
| 25 | $3 |
| 26 | $0 |
| 27 | $18k |
| 29 | $9k |
| 31 | $4 |
| 37 | $2k |
