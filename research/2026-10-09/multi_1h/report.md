_(no insights.md written yet)_

---

## Deterministic tables — 10 chains, 19:03 to 20:03 UTC

Benchmark: **Sky savings rate (read on-chain 2026-10-09 20:45 UTC) = 3.80%**. Every rate below is a supply APR; "priced utilisation" is inverted from the pool's own published borrow rate rather than taken from the aToken ratio (see `multichain.py`, `implied_utilisation`).


### The same dollar, across chains

| asset | chains | high | low | spread | supplied |
|---|---:|---|---|---:|---:|
| FRAX | 3 | avalanche 36.39% | arbitrum 0.39% | 36.00pp | $208k |
| USDS | 2 | base 24.64% | ethereum 2.70% | 21.94pp | $1.21B |
| USDC | 7 | avalanche 7.30% | bsc 3.11% | 4.18pp | $2.89B |
| DAI | 4 | polygon 4.42% | arbitrum 1.51% | 2.90pp | $268.2M |
| LUSD | 3 | optimism 2.66% | ethereum 0.56% | 2.10pp | $2.1M |
| GHO | 4 | base 3.55% | ethereum 1.49% | 2.06pp | $63.2M |
| USDe | 2 | avalanche 1.63% | ethereum 0.24% | 1.39pp | $332.3M |
| USDT | 3 | ethereum 3.55% | bsc 3.10% | 0.45pp | $2.79B |
| sUSDS | 2 | base 0.00% | ethereum 0.00% | 0.00pp | $3.0M |
| sUSDe | 2 | avalanche 0.00% | ethereum 0.00% | 0.00pp | $104.9M |

### USDC reserve by reserve

| chain | supply APR | priced util | supplied | withdrawable | rate source |
|---|---:|---:|---:|---:|---|
| avalanche | 7.30% | 0.9420 | $70.6M | $4.1M | window time-weighted |
| optimism | 4.84% | 0.9185 | $10.8M | $879k | head spot (unchecked: 3 updates) |
| ethereum | 4.34% | 0.9441 | $2.41B | $134.6M | window time-weighted |
| base | 4.08% | 0.9038 | $181.9M | $17.5M | window time-weighted |
| polygon | 3.17% | 0.6252 | $27.6M | $10.4M | window time-weighted |
| arbitrum | 3.16% | 0.8884 | $180.3M | $20.1M | window time-weighted |
| bsc | 3.11% | 0.8414 | $13.3M | $2.1M | window time-weighted |

### Every cross-chain dollar switch that pays, filled once

Size is `min(the high side's optimum before it dilutes, the low side's withdrawable liquidity)`. Destinations are filled cheapest-source-first, because the rows compete for the same reserve.

| asset | earn on | move from | size | APR at size | leaving | $/year |
|---|---|---|---:|---:|---:|---:|
| USDT | ethereum | bsc | $10.5M | 3.53% | 3.10% | $44k |
| USDC | avalanche | bsc | $1.8M | 5.15% | 3.11% | $37k |
| USDC | avalanche | arbitrum | $3.0M | 3.43% | 3.16% | $8k |
| USDC | avalanche | polygon | $1.5M | 3.29% | 3.17% | $2k |
| DAI | polygon | arbitrum | $822k | 2.89% | 1.51% | $11k |
| GHO | base | ethereum | $326k | 2.36% | 1.49% | $3k |
| DAI | polygon | ethereum | $17k | 2.87% | 2.85% | $4 |
| USDT | ethereum | optimism | $637k | 3.52% | 3.13% | $3k |
| DAI | polygon | optimism | $72k | 2.77% | 2.11% | $478 |
| USDS | base | ethereum | $1k | 13.47% | 2.70% | $146 |
| LUSD | optimism | ethereum | $13k | 1.29% | 0.56% | $96 |
| FRAX | avalanche | arbitrum | $4k | 1.81% | 0.39% | $59 |
| LUSD | optimism | arbitrum | $3k | 1.12% | 0.97% | $5 |
| USDe | avalanche | ethereum | $7k | 0.62% | 0.24% | $27 |
| sUSDS | base | ethereum | $43k | 0.00% | 0.00% | $0 |
| **total** | | | **$18.8M** | | | **$109k** |

Sum of the rows taken independently would say $228k — 109% higher, because each row assumes the destination reserve is empty.


### CCTP: where the dollars actually went, against where the yield is

| chain | net CCTP USDC | in | out | USDC APR | net USDC issued |
|---|---:|---:|---:|---:|---:|
| base | $820k | $1.5M | $675k | 4.08% | $9.4M |
| optimism | $72k | $243k | $171k | 4.84% | $74k |
| polygon | $62k | $1.3M | $1.2M | 3.17% | $9.7M |
| linea | $221 | $363 | $142 | - | $221 |
| bsc | $0 | $0 | $0 | 3.11% | $0 |
| scroll | $0 | $0 | $0 | - | $0 |
| unichain | $-113k | $8 | $113k | - | $-113k |
| arbitrum | $-652k | $2.2M | $2.8M | 3.16% | $291k |
| avalanche | $-1.3M | $669k | $2.0M | 7.30% | $-679k |
| ethereum | $-1.4M | $3.0M | $4.3M | 4.34% | $-70.1M |

Rank correlation between a chain's USDC supply rate and its net CCTP flow this hour: **-0.14** (n=7). Negative means the dollars moved toward the lower rate.


### The gas market, ten chains, one hour

| chain | blocks | block time | txs/hour | fullness | base fee (gwei) | native $ | base fee $/hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| ethereum | 300 | 12.04s | 81,125 | 51.5% | 0.277313 | 2483.18 | $6273 |
| polygon | 2401 | 1.50s | 173,032 | 18.3% | 248.142707 | 0.10 | $1722 |
| avalanche | 3243 | 1.11s | 8,053 | 1.0% | 5.011827 | 10.15 | $132 |
| arbitrum | 13611 | 0.27s | 71,004 | 0.0% | 0.020037 | - | - |
| base | 1801 | 2.00s | 283,838 | 9.0% | 0.005006 | - | - |
| bsc | 8001 | 0.45s | 431,387 | 13.7% | 0.000000 | 737.32 | $0 |
| linea | 407 | 8.86s | 516 | 0.0% | 0.000000 | - | - |
| optimism | 1801 | 2.00s | 55,711 | 37.1% | 0.000001 | - | - |
| scroll | 355 | 10.05s | 396 | 0.9% | 0.000120 | - | - |
| unichain | 3601 | 1.00s | 29,768 | 1.1% | 0.000500 | - | - |
| **total** | | | | | | | **$8127** |

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
| supply APR equals borrow APR x priced utilisation x (1 - reserve factor) | 63 | 0 | 1.91e-04 |
| the reserve IRM reproduces the pool's published borrow rate at the inverted utilisation | 63 | 0 | 1.93e-03 |
| supply APR replays from the curve at the effective liquidity base | 63 | 0 | 1.91e-04 |
| the time-weighted rate lies between the window min and max | 10 | 0 | 0.00e+00 |
| every switch fits the source liquidity and its APR replays on the curve | 21 | 0 | 0.00e+00 |

**The liquidity base the pool actually prices at, versus the aToken ratio.** Reading `variableDebt.totalSupply() / aToken.totalSupply()` is close to right and occasionally very wrong; near a kink the error is multiplied by the slope.

| chain | asset | u (aToken) | u (priced) | gap | borrow-rate error if the aToken ratio is used |
|---|---|---:|---:|---:|---:|
| arbitrum | USDC | 0.934888 | 0.920796 | -1.4091pp | 5.637pp |
| bsc | FDUSD | 0.867058 | 0.858517 | -0.8541pp | 3.417pp |
| ethereum | FRAX | 0.964402 | 0.956752 | -0.7650pp | 3.060pp |
| base | USDS | 0.830516 | 0.829021 | -0.1495pp | 1.495pp |
| avalanche | FRAX | 1.002432 | 0.999999 | -0.2433pp | 0.973pp |
| polygon | USDC | 0.878206 | 0.872141 | -0.6066pp | 0.067pp |
| bsc | USD1 | 0.442556 | 0.432984 | -0.9572pp | 0.060pp |
| bsc | BUSD | 0.744745 | 0.733799 | -1.0946pp | 0.055pp |

**Dollars leaving for domains outside this scan.** $6.0M burned for Circle domains no scanned chain resolved, against $5.3M for chains inside it.

| domain | USDC burned for it |
|---:|---:|
| 15 | $535k |
| 16 | $200 |
| 18 | $782 |
| 19 | $2.8M |
| 21 | $10k |
| 25 | $448 |
| 26 | $1.3M |
| 27 | $6k |
| 29 | $2k |
| 32 | $111 |
