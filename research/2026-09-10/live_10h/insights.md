## Ten hours of Ethereum: turnover, priority fees, and narrow lending edges

**Window: 9 September 2026, 10:32–20:32 UTC** (14:32–00:32 Asia/Tbilisi). This is the trailing ten-hour window pinned
to the finalized head when collection began, not a moving window at report publication. The local session date is
10 September. Every block and log in blocks **25,939,239–25,942,222** is present: **2,984 blocks, 861,766 transactions,
2,365,900 logs**, and **257,466 distinct transaction senders**. [[verify: blocks]] [[verify: transactions]]
[[verify: logs]] [[verify: window-complete]] [[verify: activity-senders]]

ETH fell **1.04%**, decoded DEX turnover reached **$489.89m**, and covered lending protocols recorded only **$121 of
liquidated debt**. The most useful new finding concerns what the turnover measures: **four flash-funded roundtrips
created $34.62m of settled swap volume, 7.07% of the total, while extracting only $0.65 of WETH from the pools before
gas**. The new detector found the second pool after being written from the first example.

![ETH price, pool volume and base fee over the window](activity.png)

The chart uses the Uniswap v3 USDC/WETH 0.05% pool, not an exchange index. It opened at **2,491.52 USDC per ETH**,
reached **2,518.38**, traded as low as **2,459.37**, and closed at **2,465.68**, across 2,810 swaps and $47.39m of
USDC-side notional. The 15:00–15:30 UTC bucket combined $7.44m of that pool's turnover with the window's highest
base fee. The fee spike preceded the final leg down after 19:30; these observations do not establish a causal link.
Source: [activity tables](activity_tables.md), [event data](events.json).

| Decoded venue family | Gross priced swap volume |
|---|---:|
| Uniswap v4 | $188.99m |
| Uniswap v3 | $181.08m |
| Curve | $63.94m |
| v2-style | $52.91m |
| Balancer | $2.97m |

These are settled pool legs valued with the study's token registry and pinned price basis. Routed trades and recycled
capital can appear more than once; unsupported or unpriced assets are excluded. They are not unique customer spend.

### 1. Four transactions explain most of the v2-style turnover

| Pool | Roundtrips | Gross turnover | Pool WETH lost, USD | Visible surplus less execution gas |
|---|---:|---:|---:|---:|
| [7AΩ∞ / WETH](https://etherscan.io/address/0xcb62c2d6894736d4216a41f5812bb9771de056d5) | 3 | $14,796,862 | $0.2922 | $0.0970 |
| [BULL / WETH](https://etherscan.io/address/0x28cd762e49726a4f0725a2846c85d19462b3e563) | 1 | $19,819,951 | $0.3581 | $0.1967 |

Together these account for **65.43% of v2-style volume**. Both pairs are confirmed by `getPair` on the canonical
Uniswap v2 factory. The detector checks actual WETH Transfer logs against the Swap amounts, and the follow-up checks
successful receipts, canonical block hashes, and historical reserves. The turnover really settled.

In [the first 7AΩ∞ transaction](https://etherscan.io/tx/0xf50f34a5a0885bff97fca92e6b48b07e413dc1124587ca01deca3f0b26b25992),
roughly 1,000 WETH arrives through a Balancer flash loan, buys almost the pool's entire token inventory, and is recovered
by selling the same tokens after a small token-side reserve reduction. The loan is repaid, leaving roughly
0.0000396 WETH. The sequence repeats three times. This pool started with only **0.02301 WETH** on its WETH side.
Its WETH reserve ends lower, not $44,391 higher as a naive `turnover × 0.3%` dollar-fee interpretation would suggest.

The [BULL transaction](https://etherscan.io/tx/0x2d1fc502cbd8c511b2919aadcc0e013a453ae902ea268ef1d91abfc8ad513e40)
uses **4,018.4 WETH from Morpho** against a pool with only **0.03601 WETH**, removes 1% of the tiny remaining token
reserve between the two swaps, and repays the flash loan. Its priced surplus before gas is about $0.36.

**Interpretation:** gross fee amounts valued at temporary execution prices do not establish realizable LP income through
these extreme price reversals. Keep the gross volume, flag the recycling, and measure retained balances separately.
The combined **$0.2936 after gas** is visible WETH surplus less transaction fees; other internal payments and unpriced
assets are not included, so this is not a complete operator-profit calculation. This is a data-quality finding, not
an attractive trading strategy. [RPC and reserve evidence](roundtrip_evidence.json), [reusable detector](../../../scripts/detectors/recycled_swap_volume.py).

### 2. Cheap base fees coexist with expensive priority

Execution base-fee burn, summed over **every block**, was **12.3571 ETH**, about **$30,474** at the pinned ETH/USD feed.
Gas used was **90.402bn**, or **50.50% of the aggregate gas limit**. [[verify: execution-burn]] [[verify: activity-gas]]
[[verify: activity-fullness]] This is close to the fee mechanism's target of half the maximum gas limit; it does not
by itself demonstrate underutilization. [Ethereum fee specification overview](https://ethereum.org/developers/docs/gas/).

The receipt census covers every fourth produced block: **746 blocks, 215,777 transactions**, with complete transaction
sets and gas totals verified against each sampled block. Within that sample, users paid **13.6231 ETH in tips** versus
**3.0712 ETH burned**, a **4.44× ratio**. Multiplying sampled tips by four gives a **54.49 ETH estimate** for the whole
window; it is an extrapolation from a systematic sample, not an exact total or a statistical confidence interval.

| Gas-weighted observed effective fee, including tips | gwei |
|---|---:|
| Median | 0.2370 |
| 75th percentile | 0.7064 |
| 90th percentile | 2.0578 |
| 99th percentile | 4.0048 |

Only **6.97% of sampled gas paid exactly zero tip**; **33.16% paid at most 0.01 gwei**, while **13.92% paid more than
1 gwei**. Failed transactions consumed **1.86% of sampled gas**. USDT and USDC contracts together consumed **13.63%**
of sampled gas by top-level destination; that is contract attribution, not a complete classification of internal work.

The highest per-gas tip in the full block scan belongs to a
[BAIT sale at 18:30:47 UTC](https://etherscan.io/tx/0xad4ec59b8712ec25d1984d650bc7a20f98c2ebc8168bf1beca4a152423c8888b):
the receipt confirms **0.6434 ETH of tips, about $1,587**, to receive 34.746 WETH from its pool, while the block base
fee was around 0.059 gwei. That proves a costly priority purchase, not the buyer's profit or the reason for urgency.

The economics detectors now use the observed effective-fee p75 for ordinary actions and p90 for competing JIT
execution, with provenance and window checks. These are sensitivity scenarios, not inclusion guarantees. Tips here
exclude direct builder/proposer payments, other MEV transfers, and blob fees. [Fee census](fee_census.json),
[priority transaction receipts](rpc_followup.json).

### 3. Lending: little liquidation, meaningful liquidity allocation

The covered Aave, Spark and Morpho decoders found **two liquidations**, repaying **$120.87** in total:
[$115.70 on Morpho](https://etherscan.io/tx/0x298de3c17d38c28b49dbd13421ce32e577ef77859fc0b55a78061fd7f8204d5f)
and [$5.17 on Aave](https://etherscan.io/tx/0xb49b76b284ec18934ac02ef4cc040880587290a75e82784b3c71b98058ea9d51).
Morpho's collateral token is unpriced here. These counts say little liquidation was observed in this coverage; they
do not establish the absence of leverage or stress everywhere on Ethereum.

Of **49 selected active borrower/venue records** queried at the endpoint, two large Aave accounts merit monitoring:

| Account | Debt | Health factor | Uniform collateral-value decline to HF=1 |
|---|---:|---:|---:|
| [0xcf0a12cb…](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | $26.425m | 1.02001 | 1.96% |
| [0xca686974…](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | $8.273m | 1.02350 | 2.30% |

The last column holds debt values and liquidation thresholds fixed. It is **not an ETH-price liquidation threshold**:
correlated collateral and debt prices can move together, and the asset composition was not decomposed. All 49 records
pass the health-factor and LTV consistency checks. [[verify: head-health-identity]]

There was also sizeable balance-sheet movement. Account
[0x99926ab8…](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) withdrew 10,000 WETH from Aave,
supplied 16,000 WETH to Spark, then borrowed $20m of USDT; its endpoint Spark debt was $46.0m at HF 1.199.
Spark's labelled allocator supplied **$50.15m** and **$39.56m** of USDT, then withdrew **$46.87m** later in the window.
Spark's observed USDT supply rate moved from **6.08%** to **3.39%**, with a **2.62%** low. This rate is visibly tied to
large liquidity movements. No blackout detector fired; the window does not span the previously documented midnight routine.

### 4. What remains worth investigating at real size

The endpoint rate comparison uses **Sky's 3.60% savings rate as a benchmark**, with issuer, conversion and contract risk;
it is not a risk-free asset. These are conditional research candidates, not executable quotes.

| Candidate | Measured economics | Constraint / next check |
|---|---|---|
| Compound USDC supply | 4.524% at the endpoint; the saved curve puts the best tested size versus 3.60% near **$615k**, worth **$2.8k/year** if unchanged | $1m takes the rate to 3.758%; $5m to 3.212%. Recheck borrows and the kink; one pinned state is not persistence. |
| Aave USDtb supply | 4.879% headline; **$74.5k** best tested size, about **$481/year** over the benchmark | Only 15 reserve updates, below the detector's de-spiking threshold. A small borrower repayment can erase the edge. |
| Existing USDT supply, Compound → Aave | 3.087% versus 3.632% at the endpoint | The detector's **$120.9m** destination optimum exceeds Compound's **$25.9m** supplied-minus-borrowed balance. Actual source liquidity, position ownership and changing source rates constrain any switch. |
| USDC/USDT v3 LP | At $1m and the retrospectively selected **±0.015%** band, about **$122.50** modeled fees less divergence over these ten hours | Only about **$81** above the benchmark before gas/rebalancing. The 10.73% annualization assumes repetition of an exceptionally narrow observed range. |
| USDC/USDG v4 LP | At $1m and **±0.024%**, about **$93.70** modeled window income, **$53** above the benchmark | Top taker supplied 57.65% of observed volume. Recheck flow recurrence, tick-valid placement, hooks and price excursions. |

A raw annualized LP ranking is not sufficient: bandwidth chosen after seeing the window, tick spacing, adverse
selection and rebalancing remain material. The unknown-token rows printing triple-digit annual rates do not have enough
identity and execution evidence to promote. JIT captured only about **$269** across 194 detected episodes; the aggregate
pool-fee denominator includes modeled fee values, including the recycling example, so its printed share is not a measured
share of realized LP profits.

The existing [strategy book](strategy_book.txt) now has seven linked strategies re-quoted from this window. The sUSDe
redemption finding was absent; two unlinked strategies retain historical quotes rather than acquiring invented current
ones. [Capacity calculations](summary.json), [detector economics](detectors.json).

### 5. Exchange flow, pegs, blobs and automated activity

Labelled exchanges show **$72.43m net stablecoin outflow** and **$24.32m net native ETH inflow** on priced legs at least
$10,000. [[verify: exchange-net-stables]] [[verify: exchange-net-eth]] The stablecoin sign survives removing behavioural
labels: **−$77.21m** on the model-memory tier alone. However, the verified-only tier covers only one exchange address,
so this is label-dependent evidence, not a fully verified exchange census. Native ETH excludes internal transfers and
does not have complete receipt-status coverage. Transfers to an exchange also do not prove a sale.

Gross USDC exchange inflow was **$1.7145bn**, including a
[268m-USDC transfer to the Coinbase-labelled wallet](https://etherscan.io/tx/0xcb49d1a9bac5baa89a55281be14f291ad8db89403268a06b943ed26c5e0bb9d5).
[[verify: exchange-gross-usdc]] USDC zero-address mint and burn totals were roughly **468.65m and 463.28m tokens**;
these include bridge operations and cannot be read directly as new fiat subscriptions. [[verify: usdc-mint]]
[[verify: usdc-burn]] The largest CCTP destination aggregate was **$30.0m to Aptos**, almost entirely one recipient.
[[verify: cctp-largest]] All decoded outbound bridge families totalled $160.8m; the $88.34m inbound figure covers CCTP
only, so subtracting these would not produce a comparable net bridge flow.

Large dollar markets stayed near par: volume-weighted USDT **0.999756**, USDS **0.999936**, USDG **0.999903**, and
USDe **0.999859**. The exception worth a separate check is **legacy FRAX at 0.99207**, about 79bp below par, on only
$120k across 72 priced swaps. That is a thin-market observation, not a demonstrated redemption arbitrage; frxUSD is
a different token and traded close to par. USD0's 1.0202 VWAP versus 0.9990 median is another small-sample outlier,
not enough evidence for a broad premium claim.

The chain carried **22,821 blobs**: Base posted **8,078 (35.4%)**, Robinhood Chain **6,381 (28.0%)**, and together
they account for **63.4%**. [[verify: activity-blobs]] [[verify: blob-header-identity]] Builder extra-data strings
attribute 48.5% of blocks to Titan, 19.2% to Quasar and 14.4% to BuilderNet; these are self-reported block tags, not
validator ownership. Consensus withdrawals totalled **7,377.66 ETH**, including 5,316.9 ETH in the 19:00 bucket.
Withdrawals alone do not establish selling. [[verify: activity-withdrawals]]

The existing delegated-dust detector also found a large continuing campaign: one operator's calldata encodes
**175,378 transfer legs** targeting **20,729 wallets**, through **11,956 executing accounts**. Of 84,483 legs with
in-window counterparties available to test, 27,872 (**33.0%**) use a sender matching the first four and last four hex
characters of another counterparty. This is strong evidence of address-poisoning intent. Calldata counts describe
encoded attempts; complete internal execution and recipient losses were not established. [Examples and detector evidence](detectors.md).

### Reproducibility and next research steps

The [method](method.md) records commands, coverage and price basis. Raw block/log integrity passes; seven distributed
canonical-header rechecks match. The final verifier independently recomputes **21 aggregate checks** and passes
**eight groups of protocol identities**, including the corrected Aave account-data decoder. The detector sweep ran
**16 detectors with 68 hits and no errors**. A passing check supports its named recipe, not every inference in this report.

Infrastructure now pins collection/resume boundaries and state reads, enriches discovered borrowers without moving
the price basis, batches RPC state reads concurrently, rejects incomplete receipt samples, prices execution with
observed tips, and detects recycled swap volume. Exact verifier comparisons now have zero absolute tolerance;
previously the default one-unit allowance could hide a one-block or sub-ETH discrepancy. Tests and validation are
recorded in [validation.json](validation.json).

The next useful work is targeted: decompose the two low-HF accounts' collateral/debt exposure; quote lending rates at
multiple historical points and constrain single-chain switches by the source's exit liquidity; and extend the new
roundtrip detector into a complete balance-delta fee measurement. The present evidence supports monitoring these
mechanisms. It does not establish a large, persistent, executable arbitrage.
