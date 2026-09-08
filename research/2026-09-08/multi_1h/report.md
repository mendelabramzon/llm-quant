# One hour, ten chains: the dollar is one asset with ten prices, and nobody is arbitraging it

**Window.** 2026-09-08, 06:23–07:29 UTC. Ethereum mainnet block-by-block (300 blocks, 67,905 transactions, 237,996
logs, `research/2026-09-08/live_1h_b`) plus a logs-only trailing hour on ten EVMs — Ethereum, Base, Arbitrum, Optimism,
Polygon, Avalanche, BSC, Unichain, Linea, Scroll (`research/2026-09-08/multi_1h`). Both windows pass their verifiers:
13 numeric re-derivations and 6 identities on L1, 17 checks and 6 identities cross-chain, all green.

Three things are true in this hour, and each one is a different kind of surprise.

---

## 1. Ethereum's fee market has stopped pricing blockspace, and the money moved to the private auction

The base fee held at **0.049 gwei** through the hour, at **50.6% block fullness** against a 60M gas limit. That is
EIP-1559 doing exactly what it was built to do — targeting half-full blocks — and arriving at a price of essentially
zero. The whole chain burned **0.443 ETH ($1,098)** in an hour.

In the same hour users paid **3.068 ETH ($7,598)** in priority fees. The ratio is **6.92 to 1**: for every dollar the
protocol destroys, users hand almost seven to whoever builds the block.

That is not a rounding artifact of a few whales. The top five tippers are only 16.8% of the total. It is a
distribution that has come apart at both ends:

| priority fee paid | share of all gas used |
|---|---:|
| exactly zero | **35.6%** |
| ≤ 0.01 gwei | 18.0% |
| ≤ 0.1 gwei | 19.0% |
| ≤ 1 gwei | 18.3% |
| > 1 gwei | 9.2% |

The gas-weighted median transaction tips **0.0087 gwei**. Of the $7,598 paid, **$7,488 (98.5%) is spend above that median rate** — the revenue is a long tail of ordinary wallets whose fee estimators have not noticed that the base fee moved. The single busiest sender on the chain, [0x559432e1](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53),
sent 1,335 USDT transfers at a flat **2.10 gwei** — 42× the base fee — for $359 of tips in one hour, on an address
that is doing nothing time-sensitive at all.

**What consumes the free half.** The largest single consumer of Ethereum blockspace this hour was
[0x6ef3ef48](https://etherscan.io/address/0x6ef3ef48e48cb00a87afe6132d920c498e34a229): 55 transactions, **747.8M gas —
8.2% of the entire chain-hour** — 80 logs each, every one emitted by
[0x06450dee](https://etherscan.io/address/0x06450dee7fd2fb8e39061434babcfc05599a6fb8), which reads back as **XEN**.
It paid **$2** in priority fees. Three more anonymous batch processors (a 227-transaction USDT/USDC multisend from a
single sender, a 295-transaction custom-event token, a 72-transaction claim router) take another 10%, also at
approximately zero tip. None of the five is a verified contract.

This is the mechanism, and it is worth stating plainly: **XEN's entire economic design is to convert gas into tokens.**
It is the textbook zero-reservation-price buyer of blockspace. It appears when gas is free and vanishes when it is not.
Blocks are half full because the marginal buyer of Ethereum blockspace is now an activity that only exists at a gas
price of zero — which is precisely why the price stays at zero. The fee market has found a fixed point where the
protocol's revenue is $1,098 an hour and the real clearing price of *position* inside a block is set in a private
auction the protocol does not see.

**For anything this repo prices, this is a live correction.** `economics.py` charges gas at the base fee
(`gas_gwei: 0.0491` on every hit in this window's detector sweep). For a transaction that has to land in a particular
block — a liquidation, a JIT mint, an arbitrage leg — the honest cost is the tip, and the tip is seven times larger.
At the sizes this repo has been finding, that still rounds to nothing; it will not always.

## 2. The same dollar pays 4.00% and 0.36% at the same instant, and it is worth 48 basis points to notice

USDC is one claim on one issuer, redeemable between chains in minutes over CCTP for a fee that is usually zero. So its
lending rate on eight chains is eight prices for one asset:

| chain | USDC supply APR | supplied | withdrawable |
|---|---:|---:|---:|
| base | **4.00%** | $183.8M | $17.9M |
| ethereum | 3.61% | $2.31B | $142.5M |
| avalanche | 3.29% | $61.2M | $7.6M |
| bsc | 2.88% | $14.2M | $2.6M |
| polygon | 2.81% | $30.0M | $12.2M |
| arbitrum | 2.67% | $174.2M | $32.4M |
| optimism | 2.56% | $11.3M | $2.3M |
| scroll | 0.36% | $250k | $65k |

A 3.64-percentage-point spread on $2.78 billion. It looks like the largest single mispricing this repo has measured.

It is worth **$177,794 a year**.

Two corrections take it there, and both of them are the point. The high side dilutes: a rate is a point on a kinked
curve, and Base's 4.00% survives about $15.8M of new supply before the marginal dollar earns less than what it left
behind. And the low side may not let you leave: Optimism's USDC reserve pays 2.56% on $11.3M of which **$2.3M is
withdrawable**, so the $18.5M the curve says is optimal cannot be moved at an eighth of that size. Capacity is
`min(high-side optimum, low-side withdrawable liquidity)`, and for seven of the twenty priced switches the binding
constraint is the second one.

Filling each destination once, cheapest source first, the entire cross-chain dollar complex — **$8.73B across 63
reserves on ten chains** — absorbs **$37.3M of capital for $177,794 a year. Forty-eight basis points.** The two largest
legs (USDC into Base out of Arbitrum, $79k; USDT into Ethereum out of BSC, $63k) are 80% of it. Taking the rows
independently would claim $279k; that overstates by 57%, because every row assumes the destination reserve is empty
and there is only one Base USDC reserve.

The finding generalises the strategy book's Ethereum-only result rather than overturning it: **on the dollar surface,
size and mispricing are mutually exclusive.** The $2.31B reserve pays the benchmark. The reserve paying 3.6pp over the
benchmark holds $250k and lets $65k out.

## 3. The bridge is not the arbitrageur — it runs the other way

If cross-chain rates were held together by capital chasing yield, CCTP flow should point at the high rates. Over this
hour it points away from them:

| chain | USDC supply APR | net CCTP USDC |
|---|---:|---:|
| arbitrum | 2.67% | **+$4.22M** |
| polygon | 2.81% | +$2.36M |
| optimism | 2.56% | +$242k |
| avalanche | 3.29% | +$91k |
| base | **4.00%** | −$251k |
| ethereum | 3.61% | **−$2.91M** |

Rank correlation between a chain's USDC rate and its net CCTP flow: **−0.57** over eight chains. The two
highest-paying chains are the only two net exporters; the chain with the second-lowest rate is the largest importer.

One hour and eight chains is not a law, and I will not claim it is. But the mechanism is legible and this repo has
already documented it from the other side: the addresses on both ends of CCTP are the same small set of solvers —
among the largest counterparties on each chain, eight addresses appear as both depositor and recipient, and the largest of them
([0x65c340eb](https://etherscan.io/address/0x65c340eb0688d8f8b64e9c6d580f312a97b615d8)) sent $1.29M and received
$3.27M in the same hour. That is **inventory rebalancing toward where users want to spend**, which has no reason to
correlate with where lending rates are high. CCTP volume is settlement, not arbitrage.

Which closes the loop with finding 2. The cross-chain dollar gap persists not because it is hard to bridge — bridging
is fast and nearly free — but because **the gap is too small to interest anyone large enough to close it, and the
people moving the most dollars across chains are not being paid to care about it.** The apparent inefficiency is an
equilibrium held in place by utilisation curves, not an opportunity waiting for an arbitrageur.

Two side observations from the same data. Circle's own issuance moved the opposite way from CCTP: Ethereum **destroyed
$7.84M** of USDC net this hour while the L2s created **$15.6M**, most of it ($9.3M) minted natively on Base rather than
bridged there. And **62% of all CCTP dollar sends left for chains outside this ten-chain scan** — $6.46M against
$3.98M staying inside it, including $2.40M to Circle domain 15 and $2.37M to domain 19, neither of which any scanned
chain could resolve. Whatever the interesting cross-chain flow is, most of it is going somewhere this scan does not
look.

---

## The gas market, ten chains

| chain | txs/hour | fullness | base fee (gwei) | base fee $/hour |
|---|---:|---:|---:|---:|
| polygon | 375,156 | 21.5% | 249.11 | **$1,978** |
| ethereum | 66,750 | 49.0% | 0.050 | $1,099 |
| base | 356,508 | 8.6% | 0.005 | $767 |
| arbitrum | 67,042 | n/a | 0.020 | $572 |
| avalanche | 65,584 | 9.8% | 0.090 | $10 |
| unichain | 31,089 | 1.1% | 0.0005 | $3 |
| optimism | 66,427 | 49.4% | 0.000005 | $0 |
| bsc | **976,400** | 63.3% | ~0 | $0 |
| linea | 1,197 | 0.0% | ~0 | $0 |
| scroll | 462 | 0.6% | 0.00012 | $0 |

Ten chains, one hour, **$4,429 of base fees between them.** BSC settled 976,400 transactions — 14.6× Ethereum — at
63% block fullness and collected nothing. Polygon out-earns Ethereum because its fee floor is denominated in a token
at $0.10 and has not been repriced; per unit of gas, Ethereum is still 5.2 times dearer than Polygon and 10.0 times
dearer than Base. A 100,000-gas transaction cost **$0.012 on Ethereum mainnet** in this window.

There is no congestion anywhere in this picture. Whatever constrains this system in 2026, it is not blockspace.

---

## What the window's own machinery caught, which is the other half of the job

Four defects, each of which changed a number, and each found by an assertion rather than by reading.

**`aToken.totalSupply()` is not the denominator Aave prices with.** Every capacity, width and best-size figure this
repo computes rests on utilisation, and utilisation was being read as `variableDebt.totalSupply() / aToken.totalSupply()`.
That ratio is close to right and occasionally very wrong, and which way it is wrong depends on the deployment's
version: Ethereum and Base reproduce their published borrow rate from the aToken total, Avalanche reproduces it from
`getVirtualUnderlyingBalance()` plus debt — the difference being unbacked aTokens the Portal has minted. On Avalanche's
GHO reserve that difference is 5,592 GHO on a $1.1M reserve, **0.46 percentage points of utilisation**, and it straddles
the 90% kink. The aToken ratio says 89.91% and a 4.50% borrow rate; the pool says 90.38% and **6.00%**. Half a percent
of measurement error became **151 basis points of rate**, because above the kink the curve is eighty times steeper than
below it. The fix is version-independent: invert the pool's own published borrow rate for the utilisation its curve was
evaluated at. The identity now closes on all 63 reserves.

**A reserve factor of 1.0 is not a supply market.** Aave's GHO reserve on Ethereum shows $135.2M "supplied" at a 0.00%
supply rate, because 100% of the borrow rate goes to the treasury — it is a facilitator mint, not anybody's deposit.
Compared against Base's 5.39% it produced the largest switch on the first pass, $12,798 a year, every dollar of it
imaginary. Excluded, and the exclusion is recorded rather than silent.

**A flat IRM cannot be inverted.** Aave's GHO strategy sets a governance-fixed 3.00% borrow rate with both slopes zero,
so the rate carries no information about utilisation and the inversion above returns whatever point the bisection
landed on. Detected by the supply identity failing on exactly one reserve out of 63, and handled explicitly.

**Two different tokens on Arbitrum both answer `symbol()` with "USDC".** The verifier's executability check looked up a
switch's source reserve by chain, asset and pool, matched the $190k bridged reserve instead of the $174M native one,
and correctly reported that a $15.8M move did not fit. Switches are now keyed by reserve address.

---

## What I would have the quant step build next

1. **Charge gas at the tip, not the base fee.** `economics.py` is understating the cost of an inclusion-sensitive
   transaction by roughly 7× in this regime. The gas-weighted tip distribution is already computed by
   `fee_census.py`; the right input is a percentile of it, chosen by how urgent the leg is.
2. **A `cross_chain_rate` detector**, so the switch book is re-priced every window instead of once in a dated session
   — the same failure the findings ledger fixed for findings and the strategy book has not yet fixed for itself.
3. **Extend the scan to the domains that took 62% of the flow.** Domains 15 and 19 are each larger than any single
   chain-to-chain leg inside the scan. A scan that cannot see where most of the money goes is measuring the residue.
4. **Withdrawable liquidity as a first-class risk, not a capacity input.** Seven of twenty switches are bound by it,
   and the 2026-09-08 strategy book already carries an Aave USDC reserve that goes to $503 of exit liquidity nightly.
   Exit is the scarce resource on this surface; rate is not.

---

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
