# Ethereum mainnet live scan: 2026-09-10T05:30:59+00:00 to 2026-09-10T10:30:47+00:00 UTC

Blocks 25944911 to 25946402 (1492 blocks, 5.00 h), 460,074 transactions, 1,338,947 logs. Prices at head block 25946402: ETH $2467, BTC $78k. Generated 2026-09-10T15:35:08+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

# Ethereum mainnet: a mass transfer burst, thin exits, and recycled volume

**Window: 10 September 2026, 05:30:48–10:30:48 UTC** (09:30:48–14:30:48 Tbilisi), pinned to the finalized head at the original request. This is the requested five-hour study resumed after a pause, not a rolling window at publication. Blocks **25,944,911–25,946,402** contain **460,074 transactions, 1,338,947 logs and 213,622 distinct senders**. Collection is complete; four canonical block-hash rechecks match. [[verify: blocks]] [[verify: transactions]] [[verify: logs]] [[verify: activity-senders]]

ETH slipped **0.53%**, from $2,480.23 to $2,467.07 in the observed USDC/WETH pool, while transaction activity accelerated sharply after 08:30. A large part of that increase was small LPT transfers converging on one address. The lending positions examined are mainly relative-value exposures; there were **zero decoded liquidations** in the covered Aave/Spark/Morpho events. Price source: [activity tables](activity_tables.md); liquidation source: [analysis](analysis.json).

![ETH price, transaction activity and base fees](activity.png)

## 72,446 wallets sent LPT to one recipient

**72,446 settled transfers from 72,446 distinct senders sent 161,357.65 LPT to `0x28c6c06298d514db089934071355e5743bf21d60`**, labelled Binance 14 in the existing model-memory registry. This is **99.91% of positive, non-mint/burn LPT transfers** in the window and **15.75% of all Ethereum transactions**. Exactly 72,443 occurred after 08:30, accounting for **28.28% of transactions in the final two hours**. Each matched a direct caller-to-LPT transfer transaction; these are settled movements, not merely calldata instructions. [Full cohort evidence](lpt_consolidation.json), [reusable detector](detectors.json).

The median transfer was **2.1502 LPT**; the 10th–90th percentile range was **2.1067–2.1732 LPT**. 41,207 sending transactions had nonce 1. Concentration, amount similarity and timing are consistent with coordinated consolidation. They do **not** establish common ownership, new users, selling, or an internal exchange sweep. The in-window native-transfer funding graph finds only 54 cohort senders funded by the leading unlabelled candidate, far too few to attribute the whole operation to it. A representative settled transfer is [this transaction](https://etherscan.io/tx/0x6dc3680eff947f69c26ef11ffb5331b5e6199a0fd0511490bac2157ad1b9b595).

The receipt sample includes 17,425 LPT calls, all successful, consuming **4.70% of sampled execution gas**. Their sampled execution fees were just **0.11385 ETH**. Many small transfers can dominate transaction counts without dominating fees. The existing $10,000 priced-flow filter missed this pattern; the new `token_fan_in` detector scans settled ERC-20 transfers without requiring a USD price. LPT totals remain in token units because this study has no validated LPT/USD basis. [Receipt evidence](burst_evidence.json).

## Fees rose, but the main economic fee was still the tip

Total execution burn was **3.46297 ETH**, approximately **$8,543**, calculated from every block header. Fullness was **50.93% of maximum block gas**, close to the fee mechanism's target. This figure alone does not establish spare capacity. [[verify: execution-burn]] [[verify: activity-gas]] [[verify: activity-fullness]]

The systematic every-fourth-block receipt sample covers **373 blocks and 113,684 transactions**. It measures **4.14510 ETH of tips against 0.84591 ETH burned: 4.90×**. These are sampled amounts. Gas-weighted effective-fee p75/p90 were **0.3046/1.3115 gwei**, including tips; 43.65% of sampled gas paid at most 0.01 gwei in priority fees, and 5.87% paid exactly zero. Each sampled receipt set matches its block transactions and gas total. Direct builder/proposer payments and blob fees are outside these execution-tip figures. [Fee census](fee_census.json).

The 08:30 bucket contained **41,020 transactions**, versus 18,938 in the preceding bucket. Median base fee rose from **0.0512 to 0.1504 gwei**, with LPT contributing 11,863 transactions in the 08:30 bucket. USDT activity also rose; attributing the entire fee spike to LPT would overstate the evidence. The existing gas-concentration detector measures requested gas, whereas the receipt figures above measure gas actually used. [Activity tables](activity_tables.md).

## Large low-HF positions are basis trades

Pinned token balances and protocol oracle prices reconcile to aggregate collateral and debt for all three accounts below, with discrepancies below one millionth of a dollar. These are selected borrowers, not a census of all Ethereum positions. [Reproducible exposure checks](borrower_followup.py), [results](borrower_followup.json). Aggregate health identities also pass. [[verify: head-health-identity]]

| Account | Venue | Collateral | Debt | Health factor |
|---|---|---|---|---:|
| `0x3883d8…e4d7` | Spark | 105,113.74 wstETH ($322.49m) | 119,065.66 WETH ($293.73m) | 1.02106 |
| `0xcf0a12…cd69` | Aave v3 | $16.85m USDe + $16.82m sUSDe | $12.74m USDC + $17.56m USDT | 1.02224 |
| `0xca6869…487a` | Aave v3 | 2,910.43 wstETH ($8.93m) | 3,359.72 WETH ($8.29m) | 1.02346 |

For the Spark account, a **2.06% fall in oracle-valued collateral relative to the debt**, holding quantities and thresholds fixed, would take HF to 1. Both legs have ETH exposure, so an equal ETH/USD fall in both does not cause that deterioration. The analogous Aave wstETH/WETH buffer is 2.29%; the USDe/sUSDe account's uniform collateral-value buffer is 2.18% against fixed debt. Market discounts need not transmit one-for-one into protocol oracle marks. [Aave's health-factor definition](https://aave.com/help/borrowing/liquidations) supports this calculation; token composition comes from the pinned RPC evidence, not the web page.

The window also shows collateral moving between venues, including one transaction with **5,000 wstETH supplied and 8,400 WETH borrowed on Spark**, alongside Aave WETH repayment and wstETH withdrawal. This supports active position management, without proving the ultimate owner or intent. [Transaction](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08).

## Two tempting signals failed closer inspection

**The apparent PYUSD blackout was a software error.** The first sweep reported 24 minutes with only about $70,935 available. Raw logs instead show high borrowing rates followed by normal rates **later in the same block**, in two separate transactions. The summary sorted tuples by rate rather than log index; the detector carried the wrong terminal rate forward. Historical `getReserveData` reads confirm approximately **4.919% borrow APR and 896,452.48 PYUSD cash** at the close of both affected blocks and at the window endpoint. The corrected detector uses complete end-of-block updates; the false episode is removed. [Ordered logs and historical state](liquidity_followup.json).

**rETH's discount has no meaningful direct redemption capacity at the endpoint.** It traded at a 48.53bp volume-weighted discount to endpoint NAV across $1.206m of observed swaps. But `getTotalCollateral()` returns just **0.000000034007438397 ETH** available for the direct burn path. [Rocket Pool's contract](https://github.com/rocket-pool/rocketpool/blob/master/contracts/contract/token/RocketTokenRETH.sol) includes rETH-contract ETH plus deposit-pool excess in that view and checks it before burning. The initial detector's $1.92m/year model assumed the exit existed. It now returns **no-go**, with conditional arithmetic separated from quoted capacity and earnings. Future liquidity, market exits and longer holding strategies require separate analysis. [Pinned exit read](liquidity_followup.json).

## Rate switches are much smaller after source liquidity is enforced

The scanner now reads underlying cash and withdrawal flags for Aave, Spark and Compound. These are aggregate source ceilings; ownership, collateral constraints, destination caps and liquidity when exiting remain unmeasured. Rates and borrows are held fixed in these models. [Pinned state](head_state.json), [rate detector evidence](detectors.json).

| Switch | Sized capital | Modeled annual gain over source | Binding interpretation |
|---|---:|---:|---|
| Aave USDS → Sky SSR | $8.79m | $292,589 | Source cash; removed the former synthetic $1bn sizing |
| Compound USDT → Aave | $27.15m | $156,024 | Source cash; destination-only optimum was $138.67m / $438,031 |
| Spark USDC → Compound | $0.935m | $6,950 | Destination-rate dilution; about 4.285% after sizing |

Compound's endpoint USDC rate is **5.004%**, but a $1m deposit lowers the modeled rate to **4.235%** and a $5m deposit to **3.217%**. The $0.935m switch earns only about **$6,400/year above the 3.60% Sky benchmark** before accounting for risk differences. PYUSD's $4.40m modeled switch earns 1.749% after dilution, below that benchmark. Endpoint rate gaps are conditional repricing opportunities, not a forecast that the rate persists for a year. [Sampled Compound curve](head_state.json).

## Turnover and flows need their qualifiers

Covered gross DEX volume was **$176.39m**: Uniswap v4 $112.79m, v3 $32.76m, Curve $17.43m, v2-style pools $12.27m, Balancer $1.15m. These are priced swap legs; routed trades can contribute multiple legs. [Decoded venue totals](analysis.json).

Two settled round trips in the recurring `7AΩ∞/WETH` pool generated **$9.868m**, or **5.59% of all priced volume**, while the pool lost only **$0.19269 of WETH before gas**. The detector verifies WETH Transfer settlement against the swaps. Volume-times-fee arithmetic here does not establish LP income, and this pool delta does not establish the sender's total profit. [First round trip](https://etherscan.io/tx/0x066d84a75b617eb0cd9f4ae2878f8db9933ee76dbb4fb639a7118c76b6a014c1), [second](https://etherscan.io/tx/0xbfb13f71e2ae58e0483a6ccaafe09cf56a890b523fabc61a149308ac693101a2), [settlement calculations](detectors.json).

Labelled exchanges show **+$97.15m net stablecoin inflow**, including approximately +$87.25m USDT and +$7.52m USDC. The label sensitivity matters: restricting to model-memory-or-better labels gives **+$111.64m**; the strictly source-verified subset contains only one exchange address and cannot support a market-wide inference. Native ETH's reported **−$1.01m** uses top-level value transfers and does not include internal execution. A deposit is not proof of buying or selling. [[verify: exchange-net-stables]] [[verify: exchange-net-eth]]

There were **10,734 blobs**, led by OP Mainnet (3,055), Base (3,012) and Robinhood Chain (1,692). Consensus withdrawals totalled **14,628.24 ETH**; this does not establish sales or complete validator exits. Titan's self-declared builder string appeared on 740 of 1,492 blocks; that is builder attribution, not validator ownership. [[verify: activity-blobs]] [[verify: activity-withdrawals]]

The existing delegated-dust detector also recorded **119,982 encoded transfer legs**. Among 37,409 testable sender/recipient comparisons, 33.38% matched the lookalike-address rule. These are calldata attempts and pattern matches, not verified losses or a complete internal execution census. [Detector digest](detectors.md).

The infrastructure changes make the main findings repeatable: settled token fan-in detection; source-capped rate sizing; borrower deduplication by account **and venue**; chronological lending-rate summaries; and redemption-availability gating. [Method and commands](method.md), [validation](validation.json), [full generated report](report.md).


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

**Recycled turnover:** the detector found same-pool atomic round trips in 1 pool(s). For flagged rows, `fees*` is only gross volume times an assumed tier; realized passive income is unmeasured. Token balance changes through the round trip can contradict that USD fee estimate. See [detector evidence](detectors.md).

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 436 | $27.3M | $164 | $0 | $164 | $100.0B | 0.00% | 0.1% | 0.009% |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 195 | $24.8M | $768 | $0 | $768 | $18.1B | 0.01% | 1.5% | 0.025% |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 606 | $24.3M | $219 | $0 | $218 | $38.6B | 0.00% | 0.2% | 1.530% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 51 | $12.1M | $73 | $0 | $72 | $149.6B | 0.00% | 0.0% | 0.010% |
| [0xcb62…56d5](https://etherscan.io/address/0xcb62c2d6894736d4216a41f5812bb9771de056d5) | uni v2_like | 0x622b…bf2d/WETH | ? | 4 | $9.9M | $30k* | $0 | unmeasured* | – | – | – | – |
| [0x5b03…8e96](https://etherscan.io/address/0x5b03cccab7ba3010fa5cad23746cbf0794938e96) | curve | USDe/USDT | ? | 166 | $8.7M | – | $0 | – | – | – | – | – |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 1486 | $6.7M | $3327 | $7 | $3320 | $513.6M | 1.13% | 228.2% | 0.762% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 266 | $6.5M | $65 | $0 | $65 | $10.9B | 0.00% | 0.2% | 2.581% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 2918 | $6.4M | $636 | $4 | $632 | $52.4M | 2.11% | 426.2% | 10.098% |
| 0x8aa4…4e47 | uni v4 | USDC/USDT | 0.00% | 207 | $2.8M | $34 | $0 | $34 | $18.9B | 0.00% | 0.1% | 0.008% |
| 0xcdb4…0228 | uni v4 | 0x80ac…cc0b/USDC | 0.10% | 13 | $2.2M | $2083 | $0 | $2083 | $4.0B | 0.09% | 18.5% | – |
| 0x5459…df9a | uni v4 | tBTC/cbBTC | 0.01% | 7 | $2.2M | $269 | $0 | $269 | $21.4B | 0.00% | 0.4% | 0.024% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 175 | $2.0M | $999 | $0 | $999 | $353.7M | 0.50% | 99.7% | 0.236% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 467 | $1.8M | $5450 | $0 | $5450 | $1.8B | 0.53% | 105.8% | 0.251% |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 210 | $1.8M | $894 | $0 | $894 | $248.0M | 0.63% | 127.3% | 0.736% |
| [0xbafe…8e5d](https://etherscan.io/address/0xbafead7c60ea473758ed6c6021505e8bbd7e8e5d) | uni v3 | AUSD/USDC | 0.01% | 22 | $1.6M | $163 | $0 | $163 | $543.8B | 0.00% | 0.0% | 0.001% |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 840 | $1.5M | $148 | $0 | $148 | $98.4B | 0.00% | 0.1% | 0.003% |
| [0xf4d0…96d7](https://etherscan.io/address/0xf4d0cf32908b2c7f1021339c43df0f77f06896d7) | curve | 0x2323…aa71/USDC | ? | 13 | $1.5M | – | $0 | – | – | – | – | – |
| [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) | curve | DAI/USDT | ? | 27 | $1.4M | – | $0 | – | – | – | – | – |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 2125 | $1.4M | $138 | $4 | $134 | $57.3M | 0.41% | 82.4% | 2.419% |
| 0xe500…a657 | uni v4 | USDC/WETH | 0.00% | 381 | $1.1M | $42 | $0 | $42 | $62.3M | 0.12% | 23.8% | 0.818% |
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 89 | $1.0M | – | $0 | – | – | – | – | – |
| [0xe080…8a0d](https://etherscan.io/address/0xe080027bd47353b5d1639772b4a75e9ed3658a0d) | curve | rETH/0xf1c9…0e38 | ? | 26 | $1.0M | – | $0 | – | – | – | – | – |
| [0xe6d7…e76a](https://etherscan.io/address/0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a) | uni v3 | USDe/USDC | 0.01% | 36 | $1000k | $100 | $9 | $91 | $12.2B | 0.00% | 0.3% | 0.011% |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.00% | 348 | $975k | $53 | $0 | $53 | $60.0M | 0.15% | 31.0% | 0.785% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 701 | $870k | $435 | $12 | $423 | $52.8M | 1.40% | 282.7% | 0.761% |
| 0x7094…e0b7 | uni v4 | ETH/rETH | 0.01% | 66 | $800k | $100 | $0 | $100 | $196.0M | 0.09% | 18.0% | 0.576% |
| [0x05be…8bb7](https://etherscan.io/address/0x05befa958db531090a5671e9da59fc7e4dc38bb7) | uni v3 | USDT/UNCN | 0.30% | 1545 | $784k | $2352 | $1 | $2352 | $330k | 1248.79% | 251629.5% | 2244.765% |
| [0x73a3…b38b](https://etherscan.io/address/0x73a38006d23517a1d383c88929b2014f8835b38b) | uni v3 | tBTC/WBTC | 0.01% | 28 | $780k | $78 | $0 | $78 | $5.8B | 0.00% | 0.5% | 0.036% |
| [0x4dec…d69e](https://etherscan.io/address/0x4dece678ceceb27446b35c672dc7d61f30bad69e) | curve | USDC/crvUSD | ? | 85 | $686k | – | $0 | – | – | – | – | – |
| [0xd51a…ae46](https://etherscan.io/address/0xd51a44d3fae010294c616388b506acda1bfaae46) | curve | WBTC/USDT | ? | 269 | $632k | – | $0 | – | – | – | – | – |
| 0x63bb…d1e7 | uni v4 | USDe/USDT | 0.01% | 58 | $590k | $34 | $0 | $34 | $1.6B | 0.00% | 0.7% | 0.021% |
| 0x21c6…ca27 | uni v4 | ETH/USDC | 0.06% | 195 | $546k | $341 | $0 | $341 | $62.4M | 0.96% | 193.0% | 0.728% |
| [0xb31e…5bc3](https://etherscan.io/address/0xb31e70454bdf5bc3) | balancer | USDC/WETH | ? | 37 | $533k | – | $0 | – | – | – | – | – |
| [0x1d42…d801](https://etherscan.io/address/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801) | uni v3 | UNI/WETH | 0.30% | 186 | $482k | $1447 | $0 | $1447 | $67.1M | 3.78% | 762.0% | 1.676% |
| 0xdb4c…43b1 | uni v4 | ETH/0xc8fb…8888 | 0.00% | 750 | $482k | $0 | $0 | $0 | $252k | 0.34% | 67.5% | – |
| [0xe8f7…e124](https://etherscan.io/address/0xe8f7c89c5efa061e340f2d2f206ec78fd8f7e124) | uni v3 | WBTC/cbBTC | 0.01% | 18 | $446k | $45 | $0 | $45 | $26.2B | 0.00% | 0.1% | 0.011% |
| [0x390f…7bf4](https://etherscan.io/address/0x390f3595bca2df7d23783dfd126427cceb997bf4) | curve | USDT/crvUSD | ? | 88 | $431k | – | $0 | – | – | – | – | – |
| 0xbf8f…adc6 | uni v4 | WBTC/cbBTC | 0.01% | 33 | $381k | $24 | $0 | $24 | $8.0B | 0.00% | 0.1% | 0.015% |
| [0x52c7…bc39](https://etherscan.io/address/0x52c77b0cb827afbad022e6d6caf2c44452edbc39) | uni v2_like | WETH/SPX | ? | 195 | $343k | $1028 | $0 | $1028 | – | – | – | – |
| [0x5906…9e9c](https://etherscan.io/address/0x5906fad82b9f9e9c) | balancer | WETH/USDT | ? | 16 | $327k | – | $0 | – | – | – | – | – |
| 0x72da…f169 | uni v4 | USDC/mUSD | 0.00% | 64 | $324k | $0 | $0 | $0 | $79.5B | 0.00% | 0.0% | 0.001% |
| 0x2287…1bba | uni v4 | ETH/USDT | 0.01% | 638 | $322k | $40 | $0 | $40 | $3.2M | 2.22% | 447.3% | 25.696% |
| [0xb7ec…6726](https://etherscan.io/address/0xb7ecb2aa52aa64a717180e030241bc75cd946726) | curve | tBTC/WBTC | ? | 13 | $320k | – | $0 | – | – | – | – | – |
| [0xd0fc…6d78](https://etherscan.io/address/0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78) | uni v3 | UNI/USDC | 0.30% | 103 | $315k | $946 | $0 | $946 | $23.9M | 6.94% | 1399.0% | 2.148% |

Just-in-time liquidity: 164 episodes (mint and burn of identical liquidity inside one block), bracketing $1.5M of swaps and taking about $109 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 70 episodes, fees taken $83
- [0x27c2…2bf2](https://etherscan.io/address/0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2): 16 episodes, fees taken $4
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 8 episodes, fees taken $1
- [0x5c09…33a9](https://etherscan.io/address/0x5c096ef846447cb935c5d247e4ab2a867ecc33a9): 8 episodes, fees taken $0
- [0xc54b…1097](https://etherscan.io/address/0xc54b77b28ee4d18cd3d93991f08b79bc85c71097): 6 episodes, fees taken $20
- [0xcfb4…76c4](https://etherscan.io/address/0xcfb481dad0a5acf826e317b4423ee6f0cd3876c4): 6 episodes, fees taken $0
- [0x16ae…f830](https://etherscan.io/address/0x16aeed360095f8ede2ee49b796f5915f03adf830): 6 episodes, fees taken $0
- [0xaaa0…ffff](https://etherscan.io/address/0xaaa0bf2e340c2125603b8ffd4ec30faea08effff): 3 episodes, fees taken $0

Swap volume by venue: uniswap_v4 $112.8M (14343), uniswap_v3 $32.8M (25816), curve $17.4M (1748), uniswap_v2_like $12.3M (10999), balancer $1.1M (247).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0x230e…804d (0x0000…0000/0xa0df…c845, 151 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 105 swaps); 0xda9a…a115 (0x0000…0000/0x1964…d08c, 64 swaps); 0x2eca…8e80 (0x4dc2…c277/0xa1aa…7272, 55 swaps); 0xd4e5…909d (0x14d6…47a1/0xa0b8…eb48, 54 swaps); 0x2287…1bba (0x0000…0000/0xdac1…1ec7, 53 swaps); 0x1ba3…1365 (0x0000…0000/0x0a5a…2477, 44 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 44 swaps); 0x15d6…1935 (0x0000…0000/0x3270…a4ca, 42 swaps); 0x553f…4ffc (0xc02a…6cc2/0xfe0c…c0eb, 41 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | tBTC | 0.00% | 0.26% | 0.2% | $134.0M | $204k |
| Aave v3 | EURC | 2.33% | 3.98% | 65.1% | $47.0M | $30.6M |
| Aave v3 | UNI | 0.00% | 0.17% | 1.1% | $2.8M | $31k |
| Aave v3 | WBTC | 0.00% | 0.32% | 2.4% | $2.6B | $62.4M |
| Aave v3 | GHO | 0.00% | 4.00% | 83.4% | $135.2M | $112.8M |
| Aave v3 | USDe | 1.06% | 6.25% | 22.6% | $667.8M | $150.8M |
| Aave v3 | LINK | 0.02% | 0.56% | 3.6% | $98.7M | $3.6M |
| Aave v3 | LUSD | 0.54% | 2.06% | 33.0% | $1.9M | $626k |
| Aave v3 | DAI | 3.08% | 4.72% | 86.9% | $131.5M | $114.3M |
| Aave v3 | PYUSD | 3.90% | 4.92% | 88.2% | $7.6M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.8B | $7.2M |
| Aave v3 | AAVE | 0.00% | 0.00% | 0.0% | $102.0M | $0 |
| Aave v3 | LBTC | 0.00% | 0.00% | 0.0% | $209.5M | $1325 |
| Aave v3 | RLUSD | 2.00% | 4.31% | 58.1% | $4.6M | $2.7M |
| Aave v3 | sDAI | 0.00% | 0.00% | 0.0% | $51k | $0 |
| Aave v3 | FRAX | 2.71% | 4.55% | 74.9% | $39k | $29k |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $251.5M | $0 |
| Aave v3 | MKR | 0.00% | 0.16% | 1.1% | $178k | $1880 |
| Aave v3 | USDC | 3.71% | 4.39% | 93.9% | $2.3B | $2.2B |
| Aave v3 | rsETH | 0.00% | 0.00% | 0.0% | $921.5M | $2864 |
| Aave v3 | rETH | 0.00% | 0.02% | 0.1% | $103.6M | $117k |
| Aave v3 | cbETH | 0.00% | 0.05% | 0.3% | $16.1M | $54k |
| Aave v3 | ezETH | 0.00% | 0.00% | 0.0% | – | – |
| Aave v3 | WETH | 1.47% | 2.06% | 83.9% | $5.2B | $4.4B |
| Aave v3 | USDtb | 4.88% | 7.49% | 81.4% | $15.5M | $12.6M |
| Aave v3 | ENS | 0.09% | 1.46% | 7.3% | $92k | $6727 |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.7% | $1.4B | $9.2M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $138k |
| Aave v3 | CRV | 0.45% | 5.70% | 12.2% | $2.7M | $324k |
| Aave v3 | USDT | 3.83% | 4.52% | 94.1% | $3.0B | $2.8B |
| Aave v3 | USDS | 0.27% | 5.55% | 6.5% | $9.4M | $613k |
| Aave v3 | USDG | 1.08% | 2.91% | 46.6% | $10.9M | $5.1M |
| Aave v3 | crvUSD | 0.99% | 2.91% | 42.4% | $186k | $79k |
| SparkLend | tBTC | 0.00% | 0.00% | 0.0% | $1.6M | $8 |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $140.3M | $325k |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $307.7M | $208.2M |
| SparkLend | PYUSD | 0.61% | 3.90% | 17.4% | $100.0M | $17.4M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9850 |
| SparkLend | LBTC | 0.00% | 5.00% | 0.0% | $225.3M | $0 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sDAI | 0.00% | 1.00% | 0.0% | $43k | $0 |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $26.2M | $24.2M |
| SparkLend | rsETH | 0.00% | 5.00% | 0.0% | $40k | $0 |
| SparkLend | sUSDS | 0.00% | 0.00% | 0.0% | $3.3M | $0 |
| SparkLend | rETH | 0.00% | 0.25% | 0.0% | $15.5M | $2022 |
| SparkLend | ezETH | 0.00% | 5.00% | 0.0% | – | – |
| SparkLend | WETH | 1.40% | 1.89% | 78.0% | $1.3B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.01% | 0.4% | $331.3M | $1.4M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $104.4M | $0 |
| SparkLend | USDT | 3.39% | 4.00% | 94.2% | $339.5M | $319.9M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $927.1M | $608.3M |
| SparkLend | USDG | 0.00% | 3.46% | 0.0% | $1 | $0 |
| Compound v3 USDC | base | 5.00% | 5.99% | 90.6% | $375.5M | $340.1M |
| Compound v3 USDT | base | 3.09% | 3.88% | 85.7% | $181.8M | $155.8M |
| Compound v3 WETH | base | 1.35% | 1.87% | 67.3% | $124.3M | $83.6M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.67% APR on $1.3B of USDe.

Rate curves: Aave v3 AAVE optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 0%; Aave v3 CRV optimal 45%, base 3.00%, slope1 10.00%, slope2 150.00%, reserve factor 35%; Aave v3 DAI optimal 92%, base 0.00%, slope1 5.00%, slope2 35.00%, reserve factor 25%; Aave v3 ENS optimal 45%, base 0.00%, slope1 9.00%, slope2 300.00%, reserve factor 20%; Aave v3 EURC optimal 90%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 10%; Aave v3 FRAX optimal 90%, base 0.00%, slope1 5.50%, slope2 40.00%, reserve factor 20%; Aave v3 GHO optimal 99%, base 4.00%, slope1 0.00%, slope2 0.00%, reserve factor 100%; Aave v3 LBTC optimal 45%, base 0.00%, slope1 4.00%, slope2 300.00%, reserve factor 50%; Aave v3 LINK optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 LUSD optimal 80%, base 0.00%, slope1 5.00%, slope2 50.00%, reserve factor 20%; Aave v3 MKR optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 PYUSD optimal 90%, base 1.00%, slope1 4.00%, slope2 50.00%, reserve factor 10%; Aave v3 RLUSD optimal 80%, base 2.50%, slope1 2.50%, slope2 50.00%, reserve factor 20%; Aave v3 UNI optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 USDC optimal 94%, base 0.00%, slope1 4.40%, slope2 10.00%, reserve factor 10%; Aave v3 USDG optimal 80%, base 0.00%, slope1 5.00%, slope2 30.00%, reserve factor 20%; Aave v3 USDS optimal 92%, base 5.50%, slope1 0.75%, slope2 35.00%, reserve factor 25%; Aave v3 USDT optimal 94%, base 0.00%, slope1 4.40%, slope2 10.00%, reserve factor 10%; Aave v3 USDe optimal 90%, base 6.00%, slope1 1.00%, slope2 12.00%, reserve factor 25%; Aave v3 USDtb optimal 80%, base 0.00%, slope1 4.00%, slope2 50.00%, reserve factor 20%; Aave v3 WBTC optimal 80%, base 0.25%, slope1 2.50%, slope2 300.00%, reserve factor 50%; Aave v3 WETH optimal 92%, base 0.00%, slope1 2.20%, slope2 6.00%, reserve factor 15%; Aave v3 cbBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 cbETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 crvUSD optimal 80%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 20%; Aave v3 ezETH optimal 45%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 15%; Aave v3 rETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 rsETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 sDAI optimal 90%, base 0.00%, slope1 5.00%, slope2 75.00%, reserve factor 20%; Aave v3 sUSDe optimal 90%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 20%; Aave v3 tBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 weETH optimal 30%, base 1.00%, slope1 7.00%, slope2 300.00%, reserve factor 45%; Aave v3 wstETH optimal 80%, base 0.00%, slope1 1.00%, slope2 40.00%, reserve factor 35%.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | PYUSD | 4 | 39.43% → 4.92% | 4.92% – 50.32% | 34.38% → 3.90% |
| Aave v3 | USDG | 20 | 2.71% → 2.91% | 2.71% – 3.01% | 0.94% → 1.08% |
| Aave v3 | USDT | 227 | 4.43% → 4.52% | 4.39% – 4.63% | 3.75% → 3.83% |
| Aave v3 | USDS | 4 | 5.68% → 5.55% | 5.55% – 5.68% | 0.92% → 0.27% |
| SparkLend | USDS | 30 | 3.93% → 3.93% | 3.91% – 3.99% | 2.32% → 2.32% |
| Aave v3 | USDC | 408 | 4.39% → 4.39% | 4.38% – 4.45% | 3.71% → 3.71% |
| Aave v3 | USDe | 80 | 6.30% → 6.25% | 6.25% – 6.30% | 1.27% → 1.06% |
| SparkLend | WETH | 21 | 1.86% → 1.89% | 1.86% – 1.90% | 1.35% → 1.40% |
| Aave v3 | LINK | 10 | 0.53% → 0.56% | 0.53% – 0.56% | 0.01% → 0.02% |
| Aave v3 | DAI | 11 | 4.72% → 4.72% | 4.72% – 4.75% | 3.08% → 3.08% |
| Aave v3 | WETH | 251 | 2.05% → 2.06% | 2.04% – 2.06% | 1.45% → 1.47% |
| Aave v3 | EURC | 14 | 3.99% → 3.98% | 3.98% – 3.99% | 2.34% → 2.33% |
| SparkLend | USDT | 14 | 4.00% → 4.00% | 4.00% – 4.02% | 3.40% → 3.39% |
| SparkLend | DAI | 5 | 4.04% → 4.04% | 4.04% – 4.04% | 2.46% → 2.46% |
| Aave v3 | WBTC | 36 | 0.32% → 0.32% | 0.32% – 0.32% | 0.00% → 0.00% |
| Aave v3 | RLUSD | 1 | 4.31% → 4.31% | 4.31% – 4.31% | 2.00% → 2.00% |
| SparkLend | WBTC | 2 | 0.01% → 0.01% | 0.01% – 0.01% | 0.00% → 0.00% |
| Aave v3 | wstETH | 25 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | wstETH | 9 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | PYUSD | 3 | 3.90% → 3.90% | 3.90% – 3.90% | 0.61% → 0.61% |
| Aave v3 | AAVE | 5 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | GHO | 7 | 4.00% → 4.00% | 4.00% – 4.00% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 7 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | USDC | 5 | 4.27% → 4.27% | 4.27% – 4.27% | 3.54% → 3.54% |
| Aave v3 | XAUt | 3 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: withdraw $108.5M, borrow $53.6M, supply $53.5M, repay $87.6M, atomic withdraw $224.9M, atomic supply $234.6M; SparkLend: supply $120.4M, borrow $49.7M, repay $7.5M, withdraw $28.8M.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25944941 | Aave v3 | withdraw | WETH | $24.7M | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | [0x0f09…660c](https://etherscan.io/tx/0x0f09025aa0bbe946669c7d0cc4fd50a4187eb7ab79fb4421b19585fbff42660c) |
| 25944946 | SparkLend | supply | WETH | $24.7M | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | [0x2b02…7c75](https://etherscan.io/tx/0x2b02f363ab59b3e3977b68e98eca8e788dba833009dace6290806d105aab7c75) |
| 25945759 | Aave v3 | repay | WETH | $22.2M | [0x893a…0080](https://etherscan.io/address/0x893aa69fbaa1ee81b536f0fbe3a3453e86290080) | [0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08) |
| 25946139 | Aave v3 | borrow | WETH | $21.1M | [0x7cd8…3465](https://etherscan.io/address/0x7cd8547daac215dfb00ba4be6c1b34bda3423465) | [0xfe8b…f7da](https://etherscan.io/tx/0xfe8bb15bac7a0ea6b8c3bedc023d3c0ed54e7b9865da563c6f8e3af0e09bf7da) |
| 25945759 | SparkLend | borrow | WETH | $20.7M | [0x3883…e4d7](https://etherscan.io/address/0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7) | [0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08) |
| 25945759 | Aave v3 | withdraw | wstETH | $18.4M | [0x893a…0080](https://etherscan.io/address/0x893aa69fbaa1ee81b536f0fbe3a3453e86290080) | [0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08) |
| 25946111 | SparkLend | supply | wstETH | $18.4M | [0x1676…0d9a](https://etherscan.io/address/0x1676d23711186076fa74aa53511dda750a1f0d9a) | [0xcdba…04c9](https://etherscan.io/tx/0xcdbab2abcf8e500fa47783b199fbd4d522b6b8d691a04bd3f8b4ca73ebdd04c9) |
| 25945759 | SparkLend | withdraw | wstETH | $15.4M | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | [0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08) |
| 25945759 | SparkLend | supply | wstETH | $15.4M | [0x3883…e4d7](https://etherscan.io/address/0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7) | [0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08) |
| 25944955 | SparkLend | supply | USDS | $15.3M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xe5a9…633d](https://etherscan.io/tx/0xe5a953e18b7c3c9f8dd73f1a5ad1432fd066d6ff4e6a194fa3e493268e3c633d) |
| 25945904 | SparkLend | supply | USDS | $15.2M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xa3b3…fcee](https://etherscan.io/tx/0xa3b33178f2d7e86e59ad331d3fe4a237ef9cf1615d24bc77b92a07faaf93fcee) |
| 25945829 | SparkLend | supply | LBTC | $14.9M | [0x219d…ded1](https://etherscan.io/address/0x219de81f5d9b30f4759459c81c3cf47abaa0ded1) | [0xe011…91ce](https://etherscan.io/tx/0xe0115a36d10fc44e9549ea66a325d80bd78bef8ff10943654bd4960ac31691ce) |
| 25945043 | Aave v3 | repay | USDe | $10.0M | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | [0xad8b…a402](https://etherscan.io/tx/0xad8b731a9b0413234e3f1913c4b64a16bcb716e5cc74e553f6ae34d4630da402) |
| 25945897 | SparkLend | borrow | USDS | $10.0M | [0x219d…ded1](https://etherscan.io/address/0x219de81f5d9b30f4759459c81c3cf47abaa0ded1) | [0xe9dc…3c72](https://etherscan.io/tx/0xe9dc9afb194d55047f3a3b6b0c58a0bc092f481b2a8ff9bcc3ac9c9b7ac23c72) |
| 25946139 | SparkLend | supply | USDS | $7.6M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xa2e1…ff78](https://etherscan.io/tx/0xa2e107b90ae25cbc1526d5f124c5c0bade15c4638b5a71312757472418cfff78) |
| 25945756 | Aave v3 | repay | USDe | $5.4M | [0x2cc5…44b0](https://etherscan.io/address/0x2cc58a703ad070f6668abaaa19411e0f4ad544b0) | [0x6821…b910](https://etherscan.io/tx/0x68211e8406cde31abe3c2e404cfc6cdc219891de68e904b0878dbfdf75a8b910) |
| 25946132 | SparkLend | borrow | USDS | $5.0M | [0x1676…0d9a](https://etherscan.io/address/0x1676d23711186076fa74aa53511dda750a1f0d9a) | [0xdf3d…01e8](https://etherscan.io/tx/0xdf3d729f73f74d2f6069922cd9e7208eedfcbedbc1b671fc91edd5f0c7b201e8) |
| 25944949 | Aave v3 | repay | USDT | $5.0M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0xd260…bac8](https://etherscan.io/tx/0xd260512243e54c21bcdb2305e7d8c07e7c14046c6207033f7b6ca622a08ebac8) |
| 25945371 | Aave v3 | supply | USDC | $4.8M | [0x272b…0359](https://etherscan.io/address/0x272b9f86a60226ba7e365b2f07c0478b43010359) | [0xfc4e…a5b2](https://etherscan.io/tx/0xfc4ed33cc0d420192934ce87092fbfd294b850d5208e9e0434c839c06d57a5b2) |
| 25945355 | Aave v3 | withdraw | USDT | $4.6M | [0xb81a…5bfd](https://etherscan.io/address/0xb81a0e6c38c3fec8a171cfe9631f60127a0c5bfd) | [0x1b62…fc6d](https://etherscan.io/tx/0x1b62bf5a6f3af0bd1a790c8e4f9c8c6e1542fb7afb2caf34b0282c063651fc6d) |
| 25945660 | Aave v3 | withdraw | USDT | $4.0M | [0xaaf9…a45b](https://etherscan.io/address/0xaaf9f14f20145ad50db369e52b2793bfeb18a45b) | [0x4ba7…e8ab](https://etherscan.io/tx/0x4ba71ceaaa9b1b8ab2f5fde5d87e389d0dc0ffe141844ddd55e693dfa153e8ab) |
| 25945563 | Aave v3 | repay | USDC | $3.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xb9ea…1aab](https://etherscan.io/tx/0xb9eab99f43548554f11a21aa77d3da078d09be2af81085fefc17e1f6baad1aab) |
| 25945563 | Aave v3 | borrow | USDC | $3.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xf561…49d5](https://etherscan.io/tx/0xf561a3d7c73d5d1d92f4d0c14222007ffdde56379b167298429c66cfcb2249d5) |
| 25945563 | Aave v3 | withdraw | USDT | $3.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xb9ea…1aab](https://etherscan.io/tx/0xb9eab99f43548554f11a21aa77d3da078d09be2af81085fefc17e1f6baad1aab) |
| 25946026 | SparkLend | withdraw | wstETH | $3.4M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x677b…d24c](https://etherscan.io/tx/0x677b0d2b2429d0833ac70420386db3e584ac54cea18b42daad9e46f2acadd24c) |
| 25946337 | SparkLend | supply | wstETH | $3.3M | [0x95e1…9568](https://etherscan.io/address/0x95e153c9677a2241868d80cd01e43b0b7ab39568) | [0x4031…ac70](https://etherscan.io/tx/0x40314bd2366baa4e7af9dfc5b3848f60a3487f15ca1d3ceeabca095a3021ac70) |
| 25945154 | SparkLend | withdraw | WETH | $3.3M | [0xfca3…0151](https://etherscan.io/address/0xfca3f21d60d5bc8b4c5c35f169bb5b6402510151) | [0xdf77…5154](https://etherscan.io/tx/0xdf770466a774def73f45c27cab5515adb2674e86561b643118d712c99f375154) |
| 25946026 | SparkLend | repay | WETH | $3.1M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x677b…d24c](https://etherscan.io/tx/0x677b0d2b2429d0833ac70420386db3e584ac54cea18b42daad9e46f2acadd24c) |
| 25945351 | Aave v3 | repay | WETH | $2.8M | [0xb81a…5bfd](https://etherscan.io/address/0xb81a0e6c38c3fec8a171cfe9631f60127a0c5bfd) | [0xe5e2…b9e5](https://etherscan.io/tx/0xe5e2c2c5e218c248311882d3107483ce5ad0ecc53863750a89afcde63957b9e5) |
| 25946045 | Aave v3 | withdraw | USDC | $2.5M | [0xe7bf…fe0a](https://etherscan.io/address/0xe7bf38c635426caacfa95966c4c6064e7637fe0a) | [0x126a…0c91](https://etherscan.io/tx/0x126afb2d089a990f8f2c2476a5ee27cb8c8b3d8e705784ec4c193f1dbcb10c91) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- Aave v3 withdraw $24.7M WETH by [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) ([0x0f09…660c](https://etherscan.io/tx/0x0f09025aa0bbe946669c7d0cc4fd50a4187eb7ab79fb4421b19585fbff42660c)): $24.7M → [0x59cd…71db](https://etherscan.io/address/0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db)
- SparkLend borrow $20.7M WETH by [0x3883…e4d7](https://etherscan.io/address/0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7) ([0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08)): $20.7M → [0x277c…ccc5](https://etherscan.io/address/0x277c6a642564a91ff78b008022d65683cee5ccc5)
- SparkLend withdraw $15.4M wstETH by [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) ([0xa531…cd08](https://etherscan.io/tx/0xa53101388b721b2e14691e80a6f5a617942f702c66b7e68515e1bb9a7b37cd08)): $21.5M → [0x277c…ccc5](https://etherscan.io/address/0x277c6a642564a91ff78b008022d65683cee5ccc5)
- SparkLend borrow $10.0M USDS by [0x219d…ded1](https://etherscan.io/address/0x219de81f5d9b30f4759459c81c3cf47abaa0ded1) ([0xe9dc…3c72](https://etherscan.io/tx/0xe9dc9afb194d55047f3a3b6b0c58a0bc092f481b2a8ff9bcc3ac9c9b7ac23c72)): $10.0M → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)
- SparkLend borrow $5.0M USDS by [0x1676…0d9a](https://etherscan.io/address/0x1676d23711186076fa74aa53511dda750a1f0d9a) ([0xdf3d…01e8](https://etherscan.io/tx/0xdf3d729f73f74d2f6069922cd9e7208eedfcbedbc1b671fc91edd5f0c7b201e8)): $5.0M → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)
- Aave v3 withdraw $4.6M USDT by [0xb81a…5bfd](https://etherscan.io/address/0xb81a0e6c38c3fec8a171cfe9631f60127a0c5bfd) ([0x1b62…fc6d](https://etherscan.io/tx/0x1b62bf5a6f3af0bd1a790c8e4f9c8c6e1542fb7afb2caf34b0282c063651fc6d)): $4.6M → [0x2cfa…9f87](https://etherscan.io/address/0x2cfacdf9dfbe701d6b006256884c7ba8a31c9f87) → forwarded to Binance 14 (model-memory); $1.9M → [0x2cfa…9f87](https://etherscan.io/address/0x2cfacdf9dfbe701d6b006256884c7ba8a31c9f87) → forwarded to Binance 14 (model-memory) **[to exchange $6.5M]**
- Aave v3 withdraw $4.0M USDT by [0xaaf9…a45b](https://etherscan.io/address/0xaaf9f14f20145ad50db369e52b2793bfeb18a45b) ([0x4ba7…e8ab](https://etherscan.io/tx/0x4ba71ceaaa9b1b8ab2f5fde5d87e389d0dc0ffe141844ddd55e693dfa153e8ab)): $4.0M → [0xefa4…2110](https://etherscan.io/address/0xefa417562cd30c2a571f6f27223657bba76d2110) → forwarded to Binance 14 (model-memory) **[to exchange $4.0M]**
- Aave v3 borrow $3.8M USDC by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xf561…49d5](https://etherscan.io/tx/0xf561a3d7c73d5d1d92f4d0c14222007ffdde56379b167298429c66cfcb2249d5)): $3.8M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $3.8M → [Aave v3 aEthUSDC — the reserve's aToken; symbol() read on chain (chain-read)](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c)
- Aave v3 withdraw $3.8M USDT by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xb9ea…1aab](https://etherscan.io/tx/0xb9eab99f43548554f11a21aa77d3da078d09be2af81085fefc17e1f6baad1aab)): $3.8M → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a); $3.8M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $44k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $44k → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a)
- SparkLend withdraw $3.4M wstETH by [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) ([0x677b…d24c](https://etherscan.io/tx/0x677b0d2b2429d0833ac70420386db3e584ac54cea18b42daad9e46f2acadd24c)): $984k → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb); $2.5M → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb)
- SparkLend withdraw $3.3M WETH by [0xfca3…0151](https://etherscan.io/address/0xfca3f21d60d5bc8b4c5c35f169bb5b6402510151) ([0xdf77…5154](https://etherscan.io/tx/0xdf770466a774def73f45c27cab5515adb2674e86561b643118d712c99f375154)): $3.3M → [0xc564…ddb0](https://etherscan.io/address/0xc56413869c6cdf96496f2b1ef801fedbdfa7ddb0)
- Aave v3 withdraw $2.5M USDC by [0xe7bf…fe0a](https://etherscan.io/address/0xe7bf38c635426caacfa95966c4c6064e7637fe0a) ([0x126a…0c91](https://etherscan.io/tx/0x126afb2d089a990f8f2c2476a5ee27cb8c8b3d8e705784ec4c193f1dbcb10c91)): $2.5M → [0xa315…25fa](https://etherscan.io/address/0xa315f99fe08f5356ee1ed9d344b0d82de35525fa)
- SparkLend borrow $2.4M USDS by [0x95e1…9568](https://etherscan.io/address/0x95e153c9677a2241868d80cd01e43b0b7ab39568) ([0x50c5…eb5b](https://etherscan.io/tx/0x50c54265bf13bd58ab763d29bef05bd5b6e6412ada568fcd6246c4f24d66eb5b)): $2.4M → [0xba5d…a352](https://etherscan.io/address/0xba5d9cc840745aeeeeedac5712e32f13ab8ea352)
- Aave v3 withdraw $1.9M USDT by [0xb81a…5bfd](https://etherscan.io/address/0xb81a0e6c38c3fec8a171cfe9631f60127a0c5bfd) ([0xcfea…a016](https://etherscan.io/tx/0xcfea69cd663953c4fa968cbdf1dcd99af004b2090239b86ebf313330a5caa016)): $1.9M → [0x2cfa…9f87](https://etherscan.io/address/0x2cfacdf9dfbe701d6b006256884c7ba8a31c9f87) → forwarded to Binance 14 (model-memory) **[to exchange $1.9M]**
- Aave v3 borrow $1.1M USDC by [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) ([0x5424…e123](https://etherscan.io/tx/0x542440ec02c4ab840ab4ec8bd294a37d835ba80b2ad1852de9cc729cb74ce123)): $650k → [0x50cf…5c4a](https://etherscan.io/address/0x50cfe7c1938db66a1a6d2e86d36f39fbef3d5c4a); $416k → [0x50cf…5c4a](https://etherscan.io/address/0x50cfe7c1938db66a1a6d2e86d36f39fbef3d5c4a)
- Aave v3 withdraw $1.0M WETH by [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) ([0xbaa9…8300](https://etherscan.io/tx/0xbaa948312d6acb49d4b98960ff439430f344272171c5837179d2133e47858300)): $1.0M → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $1.0M → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 borrow $1000k USDT by [0xf633…ef59](https://etherscan.io/address/0xf6335f7ed06f99d5596c153f9242ee4b8e09ef59) ([0x45b3…b18d](https://etherscan.io/tx/0x45b34efd05cbf8cf2e0af5a19de1c80874708e7d09223bbf3d143c138df9b18d)): $1000k → [0x4a6d…edb3](https://etherscan.io/address/0x4a6d972359e55d78bf88e09c61c517d9a892edb3)
- Aave v3 withdraw $862k sUSDe by [0x8714…1e13](https://etherscan.io/address/0x8714d57fbbdbd202b10cafdf562996a2ed961e13) ([0x467a…6c95](https://etherscan.io/tx/0x467afbdca85115c2c55daddf6ed314dbf3b3c9873e050ca56d55ef6f2d276c95)): $862k → [zero address (mint/burn) (known-canonical)](https://etherscan.io/address/0x0000000000000000000000000000000000000000)
- Aave v3 borrow $750k USDC by [0xe73f…5929](https://etherscan.io/address/0xe73fcbcf1450395bdae5eaea4201f17bdcdb5929) ([0x9173…bd84](https://etherscan.io/tx/0x9173931a7cf94f7dd9ca5c848f8b66c2f87946d29808a529551e3da4ef03bd84)): $750k → [0x1baf…6591](https://etherscan.io/address/0x1bafc757238bfc62f94d3ba4d4b415dc9ea96591)
- Aave v3 withdraw $701k USDC by [0xb00a…1902](https://etherscan.io/address/0xb00a793a1fbcc73882fb942d1b509ea603e91902) ([0xde01…ef25](https://etherscan.io/tx/0xde01a345873f50caa57941efa101f27b8b2496a8747214b13e0822ff7f00ef25)): $701k → [0x3783…b0f2](https://etherscan.io/address/0x37837719f82e820d6b7a819cadf24426c8a4b0f2)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| SparkLend | [0x3883…e4d7](https://etherscan.io/address/0x3883d8cdcdda03784908cfa2f34ed2cf1604e4d7) | $322.5M | $293.7M | 1.021 | 2.1% |
| Aave v3 | [0x893a…0080](https://etherscan.io/address/0x893aa69fbaa1ee81b536f0fbe3a3453e86290080) | $306.6M | $269.3M | 1.082 | 7.5% |
| Aave v3 | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | $239.3M | $129.0M | 1.529 | 34.6% |
| SparkLend | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | $190.3M | $77.6M | 2.084 | 52.0% |
| SparkLend | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | $113.5M | $74.0M | 1.319 | 24.2% |
| SparkLend | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | $39.3M | $35.3M | 1.035 | 3.4% |
| Aave v3 | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | $33.7M | $30.3M | 1.022 | 2.2% |
| SparkLend | [0x219d…ded1](https://etherscan.io/address/0x219de81f5d9b30f4759459c81c3cf47abaa0ded1) | $52.6M | $27.7M | 1.425 | 29.8% |
| Aave v3 | [0x7cd8…3465](https://etherscan.io/address/0x7cd8547daac215dfb00ba4be6c1b34bda3423465) | $22.7M | $21.1M | 1.022 | 2.1% |
| Aave v3 | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | $66.2M | $19.5M | 2.750 | 63.6% |
| SparkLend | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | $98.6M | $5.7M | 14.747 | 93.2% |
| SparkLend | [0x1676…0d9a](https://etherscan.io/address/0x1676d23711186076fa74aa53511dda750a1f0d9a) | $18.4M | $5.0M | 3.093 | 67.7% |
| Aave v3 | [0xe73f…5929](https://etherscan.io/address/0xe73fcbcf1450395bdae5eaea4201f17bdcdb5929) | $7.8M | $4.8M | 1.276 | 21.6% |
| Aave v3 | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | $32.1M | $4.0M | 6.661 | 85.0% |
| Aave v3 | [0x2cc5…44b0](https://etherscan.io/address/0x2cc58a703ad070f6668abaaa19411e0f4ad544b0) | $5.1M | $3.7M | 1.306 | 23.4% |
| Aave v3 | [0xaa24…594e](https://etherscan.io/address/0xaa2461f0f0a3de5feaf3273eae16def861cf594e) | $22.4M | $2.4M | 7.842 | 87.2% |
| SparkLend | [0x95e1…9568](https://etherscan.io/address/0x95e153c9677a2241868d80cd01e43b0b7ab39568) | $3.3M | $2.4M | 1.178 | 15.1% |
| SparkLend | [0x4f0a…b9a9](https://etherscan.io/address/0x4f0aa5900b8292273b2f9a178d5468f8048bb9a9) | $23.8M | $2.0M | 10.123 | 90.1% |
| Aave v3 | [0x256c…98cd](https://etherscan.io/address/0x256c75846b4b605acaf5cf8b05ae8d239eb298cd) | $2.1M | $1.9M | 1.011 | 1.1% |
| Aave v3 | [0xf633…ef59](https://etherscan.io/address/0xf6335f7ed06f99d5596c153f9242ee4b8e09ef59) | $4.3M | $1.6M | 2.086 | 52.1% |
| SparkLend | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | $2.9M | $1.0M | 2.458 | 59.3% |
| Aave v3 | [0x8714…1e13](https://etherscan.io/address/0x8714d57fbbdbd202b10cafdf562996a2ed961e13) | $1.1M | $975k | 1.022 | 2.1% |
| Aave v3 | [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) | $3 | $0 | 290.267 | 99.7% |
| SparkLend | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | $53.1M | $0 | ∞ | – |
| Aave v3 | [0x272b…0359](https://etherscan.io/address/0x272b9f86a60226ba7e365b2f07c0478b43010359) | $4.8M | $0 | ∞ | – |

Flash loans (events): MorphoFlash 49 ($0), BalFlash 268 ($22.2M).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a): 6 transactions, largest leg $39.0M, gross $224.9M; legs: WETH withdraw $224.9M, USDT withdraw $0
- Aave v3 account [0x0bfc…1202](https://etherscan.io/address/0x0bfc9d54fc184518a81162f8fb99c2eaca081202): 1 transactions, largest leg $3823, gross $3823; legs: WETH withdraw $3823

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 1071 | $36.5M | 0.999647 | 0.999604 – 0.999802 | 0.999808 | -1.6 bps |
| USDe | 412 | $35.0M | 0.999794 | 0.999673 – 0.999931 | 1 | -2.1 bps |
| USDS | 399 | $32.8M | 1.00004 | 1.00001 – 1.00008 | 1 | +0.4 bps |
| PYUSD | 29 | $6.6M | 1.00016 | 0.999845 – 1.0002 | 1 | +1.6 bps |
| AUSD | 19 | $1.6M | 0.999892 | 0.999761 – 1.00011 | 1 | -1.1 bps |
| rETH | 100 | $1.2M | 2875.85 | 2868.24 – 2879.74 | 2889.87 | -48.5 bps |
| crvUSD | 146 | $1.2M | 0.999549 | 0.997677 – 0.999847 | 1 | -4.5 bps |
| DAI | 39 | $878k | 1.00007 | 0.999871 – 1.0001 | 0.999609 | +4.6 bps |
| UNCN | 428 | $574k | 1.57801 | 0.822367 – 2.12573 | – | – |
| GHO | 44 | $387k | 0.998795 | 0.998062 – 0.999133 | 1 | -12.0 bps |
| SPX | 112 | $332k | 0.489852 | 0.48508 – 0.49405 | – | – |
| sUSDe | 24 | $326k | 1.2472 | 1.24678 – 1.25044 | 1.24738 | -1.5 bps |
| mUSD | 5 | $319k | 0.999891 | 0.999889 – 0.999892 | – | – |
| XAUt | 216 | $289k | 4405.89 | 4389.65 – 4418.99 | – | – |
| ASTEROID | 98 | $252k | 1.69039e-05 | 1.63504e-05 – 1.79521e-05 | – | – |
| PAXG | 161 | $247k | 4408.58 | 4391.2 – 4422.83 | – | – |
| frxUSD | 33 | $191k | 1.00004 | 0.999622 – 1.00014 | 1 | +0.4 bps |
| REZ | 144 | $173k | 0.0034975 | 0.0034153 – 0.0035802 | – | – |
| wstETH | 65 | $173k | 3067.91 | 3062.83 – 3072.45 | 3071.94 | -13.1 bps |
| NEWT | 116 | $160k | 0.0486886 | 0.0449788 – 0.0525339 | – | – |
| weETH | 6 | $131k | 2721.7 | 2721.23 – 2721.83 | 2721.92 | -0.8 bps |
| LIT | 82 | $128k | 4.51546 | 4.46361 – 4.56066 | – | – |
| LDO | 89 | $119k | 0.371242 | 0.369562 – 0.373308 | – | – |
| SKY | 101 | $114k | 0.0603216 | 0.0595889 – 0.0609899 | – | – |
| USDG | 22 | $108k | 1.00014 | 1.00002 – 1.00023 | 1 | +1.4 bps |
| FWA | 25 | $90k | 0.0132876 | 0.0125938 – 0.0144297 | – | – |
| DOLA | 12 | $78k | 0.996965 | 0.996862 – 0.997143 | 1 | -30.3 bps |
| LSK | 64 | $78k | 0.124597 | 0.115827 – 0.133611 | – | – |
| PEPE | 30 | $58k | 3.4293e-06 | 3.41712e-06 – 3.44903e-06 | – | – |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 194 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDT | $376.2M | $289.0M | $87.2M |
| USDC | $236.9M | $229.4M | $7.5M |
| ETH | $115.0M | $116.0M | $-1.0M |
| EURC | $7.0M | $8.2M | $-1.3M |
| RLUSD | $7.2M | $4.0M | $3.2M |
| UNI | $3.3M | $3.1M | $133k |
| USD1 | $3.0M | $3.1M | $-32k |
| cbBTC | $2.5M | $2.6M | $-140k |
| WBTC | $1.7M | $2.6M | $-947k |
| LINK | $726k | $1.6M | $-829k |
| FDUSD | $543k | $1.1M | $-557k |
| USDG | $376k | $944k | $-568k |

By label: Binance 14 (model-memory) in $237.9M / out $44.3M; hot wallet (behaviour, day study) in $103.7M / out $136.1M; Coinbase 10 (model-memory) in $118.2M / out $107.9M; hot wallet (day study, unidentified) (model-memory) in $99.3M / out $83.2M; Coinbase 11 (model-memory) in $77.6M / out $82.4M; Bitget (model-memory) in $57.0M / out $26.3M; Bitfinex 2 (model-memory) in $33.9M / out $21.4M; Binance 15 (model-memory) in $0 / out $41.4M; Gate.io (model-memory) in $17.1M / out $19.4M; Binance 18 (model-memory) in $0 / out $33.3M; Binance 17 (model-memory) in $0 / out $29.8M; Binance 16 (model-memory) in $0 / out $27.5M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25946211 | WBTC | $433.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xc4dd…a9a7](https://etherscan.io/tx/0xc4dd4db814eaf2f5cf2263ab82ba8a0387a98ef8ee1f523f39f3f678caf5a9a7) |
| 25946211 | WBTC | $433.7M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xc4dd…a9a7](https://etherscan.io/tx/0xc4dd4db814eaf2f5cf2263ab82ba8a0387a98ef8ee1f523f39f3f678caf5a9a7) |
| 25945259 | WBTC | $433.6M ×4 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x3465…5f03](https://etherscan.io/tx/0x3465a550945c280ec13458030ab8542ce49ef00d120114ee25bf7421fe495f03) |
| 25945259 | WBTC | $433.6M ×4 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3465…5f03](https://etherscan.io/tx/0x3465a550945c280ec13458030ab8542ce49ef00d120114ee25bf7421fe495f03) |
| 25944981 | WBTC | $433.6M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xecdb…5bc3](https://etherscan.io/tx/0xecdb4a74fd7d10dd9b0f410d8133b9abaed33e4cdccd2a2aa357cb3015a15bc3) |
| 25944981 | WBTC | $433.6M ×2 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xecdb…5bc3](https://etherscan.io/tx/0xecdb4a74fd7d10dd9b0f410d8133b9abaed33e4cdccd2a2aa357cb3015a15bc3) |
| 25946020 | WBTC | $430.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0x8847…e239](https://etherscan.io/tx/0x8847f6bf9735dfe492aad4f53d91224d7527f994f4fa94a0217c67e43d01e239) |
| 25946020 | WBTC | $430.2M | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8847…e239](https://etherscan.io/tx/0x8847f6bf9735dfe492aad4f53d91224d7527f994f4fa94a0217c67e43d01e239) |
| 25945587 | WBTC | $394.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x0c34…a4be](https://etherscan.io/tx/0x0c3437bdf25fa65ef5aaf0b9ab81c32653d7057ed2fdae7e7198bd581406a4be) |
| 25945587 | WBTC | $394.2M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0c34…a4be](https://etherscan.io/tx/0x0c3437bdf25fa65ef5aaf0b9ab81c32653d7057ed2fdae7e7198bd581406a4be) |
| 25945710 | USDC | $99.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x8cb3…8248](https://etherscan.io/tx/0x8cb3e7c13db15c955a124ee7093df1c83347691c07d45805e824b56b658a8248) |
| 25945710 | USDC | $99.7M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8cb3…8248](https://etherscan.io/tx/0x8cb3e7c13db15c955a124ee7093df1c83347691c07d45805e824b56b658a8248) |
| 25945644 | USDC | $99.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x01e9…6450](https://etherscan.io/tx/0x01e9cbd2c3237afa7d0b6602a4439657195f5b031925bff50a650d4f5dac6450) |
| 25945644 | USDC | $99.7M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x01e9…6450](https://etherscan.io/tx/0x01e9cbd2c3237afa7d0b6602a4439657195f5b031925bff50a650d4f5dac6450) |
| 25945308 | USDC | $99.6M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x06ff…1221](https://etherscan.io/tx/0x06ffa8770b0f32b360f971632df61de666d2f4b4af0ede883a1f05f92fd51221) |
| 25945308 | USDC | $99.6M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06ff…1221](https://etherscan.io/tx/0x06ffa8770b0f32b360f971632df61de666d2f4b4af0ede883a1f05f92fd51221) |
| 25945564 | USDC | $98.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xaa17…7e52](https://etherscan.io/tx/0xaa17f5500ab2d491085243f13c8aeae772de3d60c3aeb13245854c0fce2f7e52) |
| 25945564 | USDC | $98.8M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xaa17…7e52](https://etherscan.io/tx/0xaa17f5500ab2d491085243f13c8aeae772de3d60c3aeb13245854c0fce2f7e52) |
| 25945401 | USDC | $98.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x3e96…1945](https://etherscan.io/tx/0x3e96e09a2e7f938a362e3fac9ba89074bccbd2566a9d992a6d3f964b34ca1945) |
| 25945401 | USDC | $98.7M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3e96…1945](https://etherscan.io/tx/0x3e96e09a2e7f938a362e3fac9ba89074bccbd2566a9d992a6d3f964b34ca1945) |
| 25945259 | USDC | $98.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x3465…5f03](https://etherscan.io/tx/0x3465a550945c280ec13458030ab8542ce49ef00d120114ee25bf7421fe495f03) |
| 25945259 | USDC | $98.5M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3465…5f03](https://etherscan.io/tx/0x3465a550945c280ec13458030ab8542ce49ef00d120114ee25bf7421fe495f03) |
| 25946211 | USDC | $98.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xc4dd…a9a7](https://etherscan.io/tx/0xc4dd4db814eaf2f5cf2263ab82ba8a0387a98ef8ee1f523f39f3f678caf5a9a7) |
| 25946211 | USDC | $98.5M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xc4dd…a9a7](https://etherscan.io/tx/0xc4dd4db814eaf2f5cf2263ab82ba8a0387a98ef8ee1f523f39f3f678caf5a9a7) |
| 25945116 | USDC | $98.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x6203…f32c](https://etherscan.io/tx/0x6203108b53f661ee7ade546a7262cb73bff5777b5b1d8a367bc67028637bf32c) |
| 25945116 | USDC | $98.4M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x6203…f32c](https://etherscan.io/tx/0x6203108b53f661ee7ade546a7262cb73bff5777b5b1d8a367bc67028637bf32c) |
| 25944981 | USDC | $98.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xecdb…5bc3](https://etherscan.io/tx/0xecdb4a74fd7d10dd9b0f410d8133b9abaed33e4cdccd2a2aa357cb3015a15bc3) |
| 25944981 | USDC | $98.2M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xecdb…5bc3](https://etherscan.io/tx/0xecdb4a74fd7d10dd9b0f410d8133b9abaed33e4cdccd2a2aa357cb3015a15bc3) |
| 25946020 | USDC | $93.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0x8847…e239](https://etherscan.io/tx/0x8847f6bf9735dfe492aad4f53d91224d7527f994f4fa94a0217c67e43d01e239) |
| 25946020 | USDC | $93.9M | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8847…e239](https://etherscan.io/tx/0x8847f6bf9735dfe492aad4f53d91224d7527f994f4fa94a0217c67e43d01e239) |

Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0x555c…c35b](https://etherscan.io/address/0x555ce236c0220695b68341bc48c68d52210cc35b) | USDT → USDS | 4 | $120k | $30k | 5016s | 0.18 | 0.00 | uniswap_v4 4 |
| [0x6f0a…3926](https://etherscan.io/address/0x6f0a91ef8adeb54db0e63be507747ab9a31d3926) | WETH → USDC | 4 | $179k | $39k | 3060s | 0.37 | 0.35 | uniswap_v3 4 |
| [0xebed…7255](https://etherscan.io/address/0xebedc8e9ff409b23dd251f87ccbffa8075f87255) | USDC → WETH | 4 | $162k | $42k | 4548s | 0.43 | 0.29 | uniswap_v3 4 |
| [0xc8df…ebfe](https://etherscan.io/address/0xc8df1a5953aa7f62a35ff1501e0c10eb3c33ebfe) | USDC → WETH | 6 | $208k | $26k | 2352s | 0.55 | 0.54 | uniswap_v3 6 |
| [0x6f0a…3926](https://etherscan.io/address/0x6f0a91ef8adeb54db0e63be507747ab9a31d3926) | USDC → WETH | 6 | $218k | $29k | 2700s | 0.59 | 0.52 | uniswap_v3 6 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25945563 | uniswap_v4 | USDC → USDT | $3.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xf561…49d5](https://etherscan.io/tx/0xf561a3d7c73d5d1d92f4d0c14222007ffdde56379b167298429c66cfcb2249d5) |
| 25945563 | uniswap_v4 | USDT → USDC | $3.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xb9ea…1aab](https://etherscan.io/tx/0xb9eab99f43548554f11a21aa77d3da078d09be2af81085fefc17e1f6baad1aab) |
| 25946257 | uniswap_v4 | USDC → USDT | $3.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xf4e7…3a96](https://etherscan.io/tx/0xf4e7267edb596ff88fd03f6b686eecfd305ab56e80c5b81fc7e6cda154593a96) |
| 25946257 | uniswap_v4 | USDT → USDC | $3.7M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x91ca…e02a](https://etherscan.io/tx/0x91cafccab89dafee8216ec80cb96856266681f0837709dd58f4769b6604be02a) |
| 25945231 | uniswap_v2_like | 0x622b…bf2d → WETH | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0x066d…14c1](https://etherscan.io/tx/0x066d84a75b617eb0cd9f4ae2878f8db9933ee76dbb4fb639a7118c76b6a014c1) |
| 25946094 | uniswap_v2_like | 0x622b…bf2d → WETH | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0xbfb1…01a2](https://etherscan.io/tx/0xbfb13f71e2ae58e0483a6ccaafe09cf56a890b523fabc61a149308ac693101a2) |
| 25945231 | uniswap_v2_like | WETH → 0x622b…bf2d | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0x066d…14c1](https://etherscan.io/tx/0x066d84a75b617eb0cd9f4ae2878f8db9933ee76dbb4fb639a7118c76b6a014c1) |
| 25946094 | uniswap_v2_like | WETH → 0x622b…bf2d | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0xbfb1…01a2](https://etherscan.io/tx/0xbfb13f71e2ae58e0483a6ccaafe09cf56a890b523fabc61a149308ac693101a2) |
| 25946308 | uniswap_v4 | USDC → USDT | $2.2M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xab43…9285](https://etherscan.io/tx/0xab432e5e31dd84585a12e882e8989840d25235cc5c3b83bed3bd6893dbb89285) |
| 25946308 | uniswap_v4 | USDT → USDC | $2.2M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xe7cc…6f28](https://etherscan.io/tx/0xe7cc245d61d92fa156bd0e2cb5852f9064086189d8e1666ea01c9ad4e6016f28) |
| 25946344 | uniswap_v4 | USDS → PYUSD | $1.4M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x6633…a37d](https://etherscan.io/tx/0x66338159aa635df0ea686bc2c0180677d5f583a01dd84b0ec3594e38055aa37d) |
| 25946344 | uniswap_v4 | PYUSD → USDS | $1.4M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xaf9e…243d](https://etherscan.io/tx/0xaf9e1c7a6d6d4f5a5fba77054140edb487c8662cf53c7e5d2ba2866acd79243d) |
| 25946142 | uniswap_v4 | USDS → PYUSD | $1.4M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xc333…ebec](https://etherscan.io/tx/0xc33344d0efda0cba680728d7973d8a2588fd20dbd7a922a6c98576754a68ebec) |
| 25946142 | uniswap_v4 | PYUSD → USDS | $1.4M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xf7d5…1118](https://etherscan.io/tx/0xf7d5e09326c28312606f4eadefc22e56efa68ac65e7763e66231f5e4a6981118) |
| 25946344 | uniswap_v4 | USDS → PYUSD | $1.3M | [0x20a3…658d](https://etherscan.io/address/0x20a37c7cf1733f40d9b1811ea75b3976c394658d) | [0xfaab…aa41](https://etherscan.io/tx/0xfaab02bc8e0b7a94fb1b2c6b2df683008f9c3a0f33f4b2c72d87270865e1aa41) |
| 25945957 | uniswap_v4 | USDS → USDT | $1.3M | [0x815f…4748](https://etherscan.io/address/0x815f5bb257e88b67216a344c7c83a3ea4ee74748) | [0xcbf0…4cb5](https://etherscan.io/tx/0xcbf0d2a631fd03c2788beec52d1a654fb45be4e6bc14c3042ebe0dff99544cb5) |
| 25945055 | uniswap_v4 | tBTC → cbBTC | $1.2M | [0x77f1…6511](https://etherscan.io/address/0x77f123c2659ca25f5aec26f4f91c89c92d046511) | [0xfe5f…350a](https://etherscan.io/tx/0xfe5fdca7142bec4245c21ce781d948ae0783ef3d1a8bcb1dd140d3459e5e350a) |
| 25946344 | uniswap_v4 | 0x80ac…cc0b → USDC | $1.1M | [0x20a3…658d](https://etherscan.io/address/0x20a37c7cf1733f40d9b1811ea75b3976c394658d) | [0xfaab…aa41](https://etherscan.io/tx/0xfaab02bc8e0b7a94fb1b2c6b2df683008f9c3a0f33f4b2c72d87270865e1aa41) |

## E. Bridges, issuance, staking

Outbound: $39.0M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $26.3M (358).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| CCTP | USDC | Polygon | 56 | $5.8M | 0xf70da97812cb… $3.6M |
| CCTP | USDC | Aptos | 6 | $5.0M | 64c815fa7c79a1… $5.0M |
| CCTP | USDC | domain 15 | 18 | $4.1M | 0x424a31a57f7c… $3.7M |
| OFT | USDT | eid 30383 | 3 | $3.6M | – |
| OFT | USDT | eid 30420 | 52 | $2.3M | – |
| CCTP | USDC | Arbitrum | 68 | $2.0M | 0x1513d47cdf61… $674k |
| OFT | USDG | eid 30274 | 3 | $1.8M | – |
| CCTP | USDC | Sui | 6 | $1.6M | d7aa5d40262e00… $1.6M |
| OFT | USDT | eid 30390 | 3 | $1.5M | – |
| OFT | USDT | Arbitrum | 6 | $1.3M | – |
| OFT | USDG | eid 30416 | 51 | $1.1M | – |
| OFT | USDe | eid 30383 | 6 | $1.0M | – |
| OFT | USDC | BNB | 2 | $1000k | – |
| OFT | USDe | eid 30390 | 7 | $770k | – |
| CCTP | USDC | Solana | 73 | $758k | 3f0f231d22633b… $230k |
| CCTP | USDC | Base | 191 | $741k | 0x2ce910fbba65… $476k |
| OFT | USDT | Polygon | 5 | $526k | – |
| OFT | USDe | Solana | 2 | $467k | – |
| OFT | USDe | Base | 3 | $456k | – |
| CCTP | USDC | OP Mainnet | 29 | $455k | 0x3a6a72459518… $395k |

Issuance totals: USDC burn $74.5M (566); USDC mint $42.4M (596). Largest: USDC burn $8.9M ([0x187f…0390](https://etherscan.io/tx/0x187fd6e1d7db1c45a017b98da6ae18fb16ae1053f8fbaae19656152206c00390)); USDC burn $8.0M ([0xfc58…c17f](https://etherscan.io/tx/0xfc58faede3405f2e1cd2a3257edc8f62a2eca36f212adc56f6a86012bd71c17f)); USDC burn $5.0M ([0xf8c4…bfe0](https://etherscan.io/tx/0xf8c406a0b28918f85795e8cba7a0d35223bd5487f651b780cf16714100d9bfe0)); USDC burn $4.9M ([0xb6c1…6eb6](https://etherscan.io/tx/0xb6c128f577b01167fad58e6290fdf2fe1a18b59bb5ab257640da1c3491e46eb6)); USDC mint $4.7M ([0xb955…6ae0](https://etherscan.io/tx/0xb9551a40577599366bff1ee395c081483448a99dc6b55aa52a97e5f0e3626ae0)).


WETH wrapped 32766 ETH, unwrapped 38507 ETH; Lido staked 1351.5 ETH, withdrawal requests 4605.9 ETH; sUSDe cooldowns 16 for $5.5M.


## F. Gas market and block production

Base fee 0.056 → 0.199 gwei (min 0.04, median 0.057, max 0.244); blocks 51% full; median tip 0.100 gwei; 2.7% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 740,  Quasar (quasar.win)  257, BuilderNet 146, Eureka (eurekabuilder.xyz) 132, bombora.build  66, gethgo1.26.4linux 24.


Most active senders: [0x9430…daf8](https://etherscan.io/address/0x9430801ebaf509ad49202aabc5f5bc6fd8a3daf8) 9287, [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 6164, [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 3228, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 2309, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 2130, [0x8d18…835a](https://etherscan.io/address/0x8d18d00074dd99de3e3f22210b705b9b0a19835a) 1800, [Binance 17 (model-memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 1622, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 1504, [Binance 18 (model-memory)](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 1441, [0x59aa…e16b](https://etherscan.io/address/0x59aab1bd0d26290274398c07b55955c15425e16b) 1172.


Intent fills: UniXFill 174, CoWTrade 665, OneInchFilled 774. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

