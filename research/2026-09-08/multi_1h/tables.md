## Deterministic tables — 10 chains, 06:28 to 07:28 UTC

Benchmark: **Sky savings rate (SSR), read on Ethereum at block 25931150 = 3.60%**. Every rate below is a supply APR; "priced utilisation" is inverted from the pool's own published borrow rate rather than taken from the aToken ratio (see `multichain.py`, `implied_utilisation`).


### The same dollar, across chains

| asset | chains | high | low | spread | supplied |
|---|---:|---|---|---:|---:|
| FRAX | 3 | avalanche 22.90% | arbitrum 0.40% | 22.51pp | $217k |
| GHO | 4 | base 5.39% | ethereum 1.57% | 3.82pp | $63.1M |
| USDC | 8 | base 4.00% | scroll 0.36% | 3.63pp | $2.78B |
| LUSD | 3 | optimism 2.64% | ethereum 0.54% | 2.10pp | $2.1M |
| USDe | 2 | avalanche 3.54% | ethereum 1.65% | 1.88pp | $661.0M |
| DAI | 4 | polygon 3.61% | arbitrum 1.98% | 1.63pp | $316.4M |
| USDT | 3 | ethereum 3.56% | optimism 2.70% | 0.86pp | $3.05B |
| sUSDe | 2 | avalanche 0.00% | ethereum 0.00% | 0.00pp | $213.4M |

### USDC reserve by reserve

| chain | supply APR | priced util | supplied | withdrawable | rate source |
|---|---:|---:|---:|---:|---|
| base | 4.00% | 0.9024 | $183.8M | $17.9M | window time-weighted |
| ethereum | 3.61% | 0.9382 | $2.31B | $142.5M | window time-weighted |
| avalanche | 3.29% | 0.8752 | $61.2M | $7.6M | window time-weighted |
| bsc | 2.88% | 0.8187 | $14.2M | $2.6M | head spot (unchecked: 3 updates) |
| polygon | 2.81% | 0.5933 | $30.0M | $12.2M | window time-weighted |
| arbitrum | 2.67% | 0.8140 | $174.2M | $32.4M | window time-weighted |
| optimism | 2.56% | 0.7998 | $11.3M | $2.3M | head spot (unchecked: 3 updates) |
| scroll | 0.36% | 0.7389 | $250k | $65k | head spot (unchecked: 1 updates) |

### Every cross-chain dollar switch that pays, filled once

Size is `min(the high side's optimum before it dilutes, the low side's withdrawable liquidity)`. Destinations are filled cheapest-source-first, because the rows compete for the same reserve.

| asset | earn on | move from | size | APR at size | leaving | $/year |
|---|---|---|---:|---:|---:|---:|
| USDC | base | arbitrum | $15.8M | 3.18% | 2.67% | $79k |
| USDT | ethereum | bsc | $10.3M | 3.54% | 2.93% | $63k |
| USDC | base | polygon | $6.1M | 2.99% | 2.81% | $11k |
| USDC | base | optimism | $2.3M | 2.93% | 2.56% | $8k |
| USDC | base | bsc | $780k | 2.90% | 2.88% | $169 |
| USDT | ethereum | optimism | $904k | 3.53% | 2.70% | $8k |
| DAI | polygon | arbitrum | $598k | 2.70% | 1.98% | $4k |
| GHO | base | ethereum | $307k | 2.47% | 1.57% | $3k |
| USDC | base | scroll | $65k | 2.90% | 0.36% | $2k |
| DAI | polygon | ethereum | $106k | 2.58% | 2.46% | $127 |
| LUSD | optimism | ethereum | $13k | 1.28% | 0.54% | $97 |
| FRAX | avalanche | arbitrum | $4k | 1.71% | 0.40% | $54 |
| LUSD | optimism | arbitrum | $3k | 1.13% | 0.99% | $4 |
| USDe | avalanche | ethereum | $2k | 2.43% | 1.65% | $16 |
| **total** | | | **$37.3M** | | | **$178k** |

Sum of the rows taken independently would say $279k — 57% higher, because each row assumes the destination reserve is empty.


### CCTP: where the dollars actually went, against where the yield is

| chain | net CCTP USDC | in | out | USDC APR | net USDC issued |
|---|---:|---:|---:|---:|---:|
| arbitrum | $4.2M | $7.2M | $2.9M | 2.67% | $3.1M |
| polygon | $2.4M | $2.4M | $43k | 2.81% | $2.0M |
| optimism | $242k | $301k | $59k | 2.56% | $432k |
| avalanche | $91k | $136k | $45k | 3.29% | $810k |
| linea | $1k | $3k | $2k | - | $1k |
| bsc | $0 | $0 | $0 | 2.88% | $0 |
| scroll | $0 | $0 | $0 | 0.36% | $0 |
| unichain | $-104k | $922 | $105k | - | $-104k |
| base | $-251k | $613k | $864k | 4.00% | $9.3M |
| ethereum | $-2.9M | $3.5M | $6.4M | 3.61% | $-7.8M |

Rank correlation between a chain's USDC supply rate and its net CCTP flow this hour: **-0.57** (n=8). Negative means the dollars moved toward the lower rate.


### The gas market, ten chains, one hour

| chain | blocks | block time | txs/hour | fullness | base fee (gwei) | native $ | base fee $/hour |
|---|---:|---:|---:|---:|---:|---:|---:|
| polygon | 2401 | 1.50s | 375,156 | 21.5% | 249.108385 | 0.10 | $1978 |
| ethereum | 300 | 12.04s | 66,750 | 49.0% | 0.050104 | 2476.66 | $1099 |
| base | 1801 | 2.00s | 356,508 | 8.6% | 0.005000 | 2476.66 | $767 |
| arbitrum | 14315 | 0.25s | 67,042 | 0.0% | 0.020061 | 2476.66 | $572 |
| avalanche | 3467 | 1.04s | 65,584 | 9.8% | 0.090111 | 8.05 | $10 |
| unichain | 3601 | 1.00s | 31,089 | 1.1% | 0.000500 | 2476.66 | $3 |
| optimism | 1801 | 2.00s | 66,427 | 49.4% | 0.000005 | 2476.66 | $0 |
| bsc | 8000 | 0.45s | 976,400 | 63.3% | 0.000000 | 755.27 | $0 |
| linea | 647 | 5.57s | 1,197 | 0.0% | 0.000000 | 2476.66 | $0 |
| scroll | 402 | 8.89s | 462 | 0.6% | 0.000120 | 2476.66 | $0 |
| **total** | | | | | | | **$4430** |

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
| supply APR equals borrow APR x priced utilisation x (1 - reserve factor) | 63 | 0 | 2.51e-04 |
| the reserve IRM reproduces the pool's published borrow rate at the inverted utilisation | 63 | 0 | 7.72e-04 |
| supply APR replays from the curve at the effective liquidity base | 63 | 0 | 2.51e-04 |
| the time-weighted rate lies between the window min and max | 10 | 0 | 0.00e+00 |
| every switch fits the source liquidity and its APR replays on the curve | 20 | 0 | 0.00e+00 |

**The liquidity base the pool actually prices at, versus the aToken ratio.** Reading `variableDebt.totalSupply() / aToken.totalSupply()` is close to right and occasionally very wrong; near a kink the error is multiplied by the slope.

| chain | asset | u (aToken) | u (priced) | gap | borrow-rate error if the aToken ratio is used |
|---|---|---:|---:|---:|---:|
| avalanche | GHO | 0.899113 | 0.903753 | +0.4639pp | 1.506pp |
| optimism | USDC | 0.835873 | 0.775793 | -6.0080pp | 0.367pp |
| avalanche | FRAX | 0.961582 | 0.960757 | -0.0825pp | 0.330pp |
| bsc | USD1 | 0.441903 | 0.432984 | -0.8919pp | 0.056pp |
| arbitrum | USDC | 0.834032 | 0.829497 | -0.4535pp | 0.050pp |
| bsc | BUSD | 0.743849 | 0.733799 | -1.0051pp | 0.050pp |
| bsc | USDT | 0.685917 | 0.680509 | -0.5408pp | 0.027pp |
| ethereum | FRAX | 0.748593 | 0.745100 | -0.3493pp | 0.021pp |

**Dollars leaving for domains outside this scan.** $6.5M burned for Circle domains no scanned chain resolved, against $4.0M for chains inside it.

| domain | USDC burned for it |
|---:|---:|
| 15 | $2.4M |
| 19 | $2.4M |
| 21 | $118k |
| 26 | $7 |
| 27 | $5k |
| 29 | $2k |
| 30 | $1k |
| 31 | $4k |
