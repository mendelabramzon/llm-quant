# Ethereum mainnet live scan: 2026-09-06T13:16:23+00:00 to 2026-09-06T14:16:23+00:00 UTC

Blocks 25918544 to 25918844 (301 blocks, 1.00 h), 81,912 transactions, 256,739 logs. Prices at head block 25918661: ETH $2497, BTC $80k. Generated 2026-09-06T14:16:40+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

## Insights (LLM narrative, written from `analysis.json`, `head_state.json` and `midnight_2026-09-06.json`)

Written by Claude on 2026-09-06 after the first hour (10:06 to 11:06 UTC, a quiet Sunday morning: base fee 0.04 to 0.06 gwei, blocks 51% full). Every number below is in the deterministic tables further down or in the JSON artifacts; the reading of them is mine and carries a stated confidence. The question asked was where a patient actor, not a block builder or a latency bot, can extract value.

### 1. The midnight balance routine is daily, and it is the cleanest recurring rate event on the chain (high confidence)

The routine found in the 2026-09-04/05 day study recurred last night, checked with targeted log queries (`midnight_2026-09-06.json`):

| time UTC | leg | amount | effect |
|---|---|---|---|
| 23:34:35 | [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) withdraws USDC from Aave v3 | $151.0M (was $144.0M the night before) | Aave USDC variable borrow APR 4.27% → 14.29%, supply APR 3.60% → 12.8% |
| 23:36 to 23:39 | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) redeems sUSDS through the PSM | $245.5M | |
| 23:41 | hub [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) sends the pool to [0xf1ed…56a8](https://etherscan.io/address/0xf1edbf98dda764ec51de3776371f0f7d6f6156a8) | $396.5M | held across 00:00 UTC |
| 00:05:59 / 00:06:23 | hub returns to both legs | $151.0M and $245.5M | |
| 00:08:23 | Aave re-supply | $151.0M | borrow APR back to 4.27% at 00:08:59 |

Two consecutive nights with the same addresses, the same order and a 34 to 42 minute hold make this a scheduled process, not a coincidence. The entity is unidentified; its float grew $7M day over day. What can be done with it:

- **Borrowers.** Variable USDC debt on Aave costs 14.3% instead of 4.3% for about 35 minutes every day: 0.8 bps of principal per day, 0.29% a year, $29k a year per $10M. Repaying before 23:34 and re-borrowing after 00:10 captures it. Anyone running a stablecoin loop on Aave USDC should schedule around it.
- **Liquidity denial.** The Aave USDC reserve was at 93.5% utilisation at the head ($2,304M supplied, $2,154M borrowed), so about $150M is withdrawable. The routine takes essentially all of it. A vault, liquidator or redemption queue that needs Aave USDC between 23:35 and 00:10 UTC will fail or pay the maximum rate. That is a risk-management fact for anyone whose contingency plan is "withdraw from Aave".
- **Rate-sampling pollution.** Any product that samples Aave USDC rates (fixed-rate markets, rate oracles, allocators chasing APR) sees a 3.3x spike for 35 minutes a day. Allocators that react to it misallocate; a strategy that fades their reaction has an edge.
- **Suppliers** gain the mirror image, about 0.1 bps a day; just-in-time supply only pays if it is free to run, which at today's gas it nearly is (see section 6).

### 2. One bot cycles $3.5B of free flash liquidity through Aave, Maker and a private Balancer pool 30 times an hour for $759 a run (mechanism: medium-low confidence; sizes: high)

The largest lending events of the hour are not lending. Account [0xfccc…275c](https://etherscan.io/address/0xfccc10ad36a653c34f12a2e15bbbd7a7c9de275c), called by EOA [0x1124…e0ae](https://etherscan.io/address/0x11246c5b75b3a88b05f0238ced6cd9b8afc7e0ae) with a 16.78M gas limit and a 0.1 gwei tip, ran 30 times in the hour (roughly every two minutes). Decoding one run ([0x22b3…329e](https://etherscan.io/tx/0x22b3622da496c954c69fa0ccd3f2ebea430615a983fc3c1ec1f85444e53e329e)):

- Flash loans, all fee-free: SparkLend 82,318 WETH, 99.99M DAI, 968,523 wstETH (99.9% of the spwstETH supply), 3,565 cbBTC, 242.9M USDS; Maker DssFlash 499.5M DAI; Morpho 5,562 WBTC; Uniswap v2 flash swaps of 3.5M REQ.
- Supplies WBTC, wstETH and cbBTC to Aave core, borrows 323,787 WETH (about $810M, most of the reserve's available liquidity: Aave WETH borrow APR 2.02% → 8.19% and supply APR 1.42% → 6.79% inside the transaction, reverted by the repayment at the end), joins 25,446 wstETH into a Maker vault and draws 44.5M DAI, converts USDS to DAI and back.
- Parks 402,105 WETH, 885M DAI and 3.85M REQ in an 801-byte holder contract ([0x1926…b7f8](https://etherscan.io/address/0x1926fed1865ac081d83e441c32c4fff53b27b7f8)) for the middle of the transaction.
- Runs a geometric ladder of tiny swaps (each 1.5x the previous input, each returning two thirds of the previous USDC) and 30 join/exit cycles of dust through a Balancer pool ([0x69d4…9bf5](https://etherscan.io/address/0x69d460e01070a7ba1bc363885bc8f4f0daa19bf5)) with only 100 BPT outstanding.
- Unwinds everything and pays the EOA: $2,084 in the first run of the hour, decaying by about 8% a run to $1,148, $22,760 over the hour. Gas per run is about 16.7M × 0.145 gwei ≈ 0.0024 ETH ≈ $6.

Reading (medium-low confidence): a rounding or accounting surplus that regenerates slowly and is drained at a fixed fraction per run; the flash liquidity is there to make the ladder large enough for the surplus to be worth a transaction. Without call traces the exact source of the $759 cannot be allocated between the Maker, Aave and Balancer legs, and this is the first request to the quant step. Three things are established regardless of mechanism:

1. **Free flash liquidity exists at $3B+ size** (SparkLend charges no premium, Maker's DssFlash is free up to its ceiling, Morpho is free). Any atomic strategy on mainnet now costs gas only, and gas for a 16.7M-gas transaction is $6 at this base fee. The binding constraint on atomic strategies is the opportunity, never the capital.
2. **The Aave WETH rate is spiked thirty times an hour.** The reserve's borrow rate reads 8.19% for the duration of each transaction; anything that samples `currentVariableBorrowRate` or `currentLiquidityRate` at those instants (rate oracles, fixed-rate AMMs, dashboards, allocators) is polluted. Combined with section 1, on-chain rate readings on Aave should be time-weighted, never spot.
3. It is not competing with anyone: the transactions pay 0.1 gwei and are included by Titan, Quasar and BuilderNet alike. This is the class of edge worth looking for: accounting artefacts with a slow-regenerating source, not price arbitrage.

### 3. Where the rates are, and where a patient allocator earns the spread (high confidence on the numbers)

Head-state reads (`getReserveData`, Compound `getSupplyRate`, Sky `ssr`), 11:10 UTC:

| stablecoin supply | APR | utilisation | size |
|---|---|---|---|
| Aave v3 PYUSD | **23.31%** (borrow 27.41%) | 94.5% | $7.8M supplied |
| Compound v3 USDC | 4.79% (borrow 5.75%) | 90.5% | |
| SparkLend USDT | 4.12% (borrow 4.80%) | 95.3% | $339M |
| Aave v3 USDC | 3.60% (borrow 4.28%) | 93.5% | $2,304M |
| sUSDS (Sky savings rate) | 3.60% APY | | |
| Aave v3 USDT | 3.56% (borrow 4.25%) | 93.0% | $2,965M |
| Aave v3 DAI | 3.03% (borrow 4.68%) | 86.2% | $132M |
| Compound v3 USDT | 2.99% (borrow **3.81%**) | 83.1% | |
| SparkLend DAI | 2.46% (borrow 4.04%) | 67.7% | $308M |
| SparkLend USDS | 2.32% (borrow 3.93%) | 65.6% | $713M |

- **Thin-reserve spikes.** Aave's PYUSD reserve pays 23% because one borrower took it to 94.5% of $7.8M. The capacity is small: about $400k of new supply brings utilisation to 90% and the rate to the kink; but PYUSD trades at 1.0001 in the window, so the position is a par asset earning 6x the market rate until the borrower repays. A monitor that lists reserves above the kink, with the capacity left before the kink, is cheap to run and catches these every day.
- **Cross-venue dispersion is about one point** and persists because moving supply costs attention, not money: Compound USDC 4.79% versus Aave USDC 3.60%; SparkLend USDT 4.12% versus Aave USDT 3.56%. The cheapest stablecoin borrow is Compound USDT at 3.81% (and SparkLend USDS 3.93%), the best supply Compound USDC at 4.79%; that is a 0.9 to 1.0 point carry between two dollars on the same venue, before the collateral cost of the borrow. This is a yield-routing business at $10M to $50M size, not a trade; the day-to-day work is watching `ReserveDataUpdated`.
- **Rates move on visible flows.** Aave USDT's borrow rate fell from 4.57% to 4.26% within the hour on a single $38.0M repayment by [0xb99a…2c4c](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) (an account with $50.8M collateral and $20.0M debt after the repayment). Near the kink a $38M flow moves the rate 31 bps, and flows of that size are visible in the mempool and in the block before anyone re-allocates.
- **ETH carry.** Borrowing WETH costs 1.88% on Compound, 1.98% on SparkLend, 2.02% on Aave against wstETH collateral; that is the levered staking loop everybody runs, and its spread over staking yield is under one point. Not new, listed for completeness.

### 4. Leverage to exchanges, again (medium confidence on intent, high on the flow)

In a quiet hour: [0x3290…b7e0](https://etherscan.io/address/0x3290b7e095e756ee0fa9f51c4087c9f6546ee4fb) borrowed $5.00M USDT on Aave at 10:53 UTC and it reached Binance 14 (label from memory) through a deposit address within the hour; the account holds $35.3M of collateral against $17.0M of debt (health factor 1.56, liquidation 36% below). Two smaller cases ($500k DAI borrowed, $301k USDC withdrawn) went to behaviour-tagged deposit sinks. That is $5.5M of borrowed or withdrawn stablecoins shipped to venues in one Sunday hour, the same pipeline the day study measured at $58M of borrows a day. The series is worth keeping daily: it measures leverage demand before it shows up in perpetual funding.

The exchange netflow of the hour was USDT −$17.2M (withdrawn from tagged wallets), USDC +$7.5M, ETH +$12.2M and WETH +$1.5M (deposited). The day study found hourly netflow uninformative for the next hour's return; nothing here changes that, and the address book is still behavioural plus memory labels.

### 5. Prices versus NAV: one real discount, one broken peg, everything else at par (high confidence)

Volume-weighted implied prices from every priced swap, against Chainlink and NAV reads at the head: USDS 0.99994, USDG 1.00006 (so USDG sits at par, confirming the day study's reading that its apparent premium was USDC below par), USDT 1.0000, PYUSD 1.0001, crvUSD 1.0002, GHO 0.99915 (−8.5 bps; a GHO borrower can buy debt back below par), weETH −1 bps to NAV, wstETH +5 bps.

- **rsETH trades 37 bps below Kelp's exchange rate** ($2,690 against $2,700). Unstaking rsETH takes 7 to 10 days, so the discount alone is about 13% annualised on capital that is otherwise earning the restaking yield. The capacity is the pool depth ($53k traded in the hour, three swaps), so this is a small, patient trade, not a book. It is exactly the shape of inefficiency that latency bots leave alone.
- **msETH (Metronome's synthetic ETH) trades at 0.50 ETH** across 39 Curve swaps ($85k). That is a broken peg, not an arbitrage: the only party who gains is an msETH debtor buying back at half price. Flagged so nobody prices msETH at parity.

### 6. Passive LP earns almost nothing at these volumes, and JIT is not the reason (high confidence for this hour)

Verified swap volume in the hour, after excluding hooked Uniswap v4 pools whose reported deltas are virtual (section 7): Uniswap v3 $5.1M, Curve $1.7M, v2-style $0.6M, v4 under $2M. The USDC/WETH 0.05% pool did $1.18M in 199 swaps and earned $590 of fees on $719M of full-range-equivalent liquidity: 0.72% APR for a full-range position, 145% gross for a ±1% band, before any impermanent loss (ETH moved 0.25% in the hour). Just-in-time liquidity was present (25 episodes, bot [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13) minted $725k of liquidity around a $1.2k swap) and took $57 of fees in total. In quiet hours the problem for a passive LP is the volume, not the bots. The LP table below is kept in the live report because the same numbers in a volatile hour tell a different story.

### 7. Two data-quality findings that matter for anyone reading Ethereum flow

- **Uniswap v4 hook pools emit swap deltas that never moved.** Three pools with hooks (tokens 0xb225…2087, 0x5993…17f3, 0xaaee…1c7a) reported $124M, $106M and $40M single swaps whose actual settlement was a $158 PYUSD trade routed by [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be). The scanner now requires ERC-20 movement through the PoolManager, or transaction value plus WETH unwrapped for native ETH, of at least the reported size before it counts a hooked-pool swap. Any v4 volume figure that does not do this is inflated by launchpad hooks.
- **Blockspace is nearly free and the biggest consumers are unlabeled.** Median tip 0.046 gwei, 4.3% of transactions pay zero tip, and the top gas buyers of the hour are the USDT contract (2.5B gas), then [0x7ec8…](https://etherscan.io/address/0x7ec8a30a34b86927dc77b302603d1d53e640bef7), 0xb828…, 0x0de8… at 1.4 to 1.6B gas each, unidentified. At this price a 16.7M-gas transaction costs $6 (section 2), which is why the flash bot can afford a $759 edge thirty times an hour.

### 8. What was not there

No liquidations on Aave, SparkLend or Morpho in the hour. No TWAP-like programmes (four or more regular swaps by one sender with low dispersion). USDC net issuance near zero (many sub-$1M mints and burns). Lido staked 75 ETH against 10 ETH of withdrawal requests. No sUSDe cooldowns. Bridge outflow $10.4M, half of it $5.0M of USDC to a single Aptos recipient. Builders: Titan 38%, Quasar 18%, Eureka 16%, BuilderNet 12%.

### Ranked strategy candidates (non-MEV)

1. **Rate-dispersion allocator with thin-reserve alerts** (section 3): ~1 point over the average stablecoin rate at $10M to $50M, plus occasional 20%+ spikes in thin reserves; event-driven on `ReserveDataUpdated`. Competition is low because it is a business, not a trade.
2. **Midnight window** (section 1): 0.29% a year saved on Aave USDC debt by scheduling; a daily read on a $400M float; a hard fact for liquidity contingency plans; fade allocators that chase the spike.
3. **Discounted redeemables** (section 5): rsETH −37 bps for a 7 to 10 day queue; GHO −8.5 bps for GHO debtors. Small capacity, zero latency competition.
4. **Leverage-to-exchange series** (section 4): keep building it; the hourly reading is a signal candidate, not yet a signal.
5. **Accounting-artefact hunting** (section 2): the flash bot proves the class is live and worth $20k an hour to one actor. The next step is to trace one run, not to copy it.
6. **Passive LP**: not at these volumes (section 6).

### Requests to the quant step

1. Trace one run of the flash bot on a trace-capable endpoint (the day study used a public dRPC endpoint for `debug_traceCall`) and allocate the $759 between the Maker, Aave and Balancer legs; identify the Balancer pool's other LPs.
2. Rate series at five-minute resolution across Aave, SparkLend, Compound and Sky, with capacity-to-kink per reserve; alert when a reserve trades above its kink (the PYUSD case).
3. Daily midnight check at 00:30 UTC (the `midnight` command), with the float and the two legs as a series.
4. Label the v4 hooks 0x2da8…a0cc, 0x8f10…f996 and 0x6131…; label the gas buyers 0x7ec8…, 0xb828…, 0x0de8…; label the deposit addresses 0xcde5…, 0x19c3… and hot wallet 0xa9ac….
5. Keep the live scan running through a volatile hour and through 23:30 to 00:15 UTC to see the LP table and the rate table under stress.


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) | curve | DAI/USDC | ? | 34 | $5.0M | – | $0 | – | – | – | – | – |
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 61 | $3.4M | $21 | $0 | $21 | $100.0B | 0.00% | 0.0% | 0.010% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 886 | $1.3M | $132 | $0 | $132 | $143.9M | 0.80% | 161.6% | 1.344% |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 265 | $1.3M | $632 | $0 | $632 | $506.6M | 1.09% | 219.6% | 0.404% |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 161 | $1.3M | $11 | $0 | $11 | $31.4B | 0.00% | 0.1% | 0.010% |
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 28 | $1.1M | – | $0 | – | – | – | – | – |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 9 | $1.0M | $6 | $0 | $6 | $149.1B | 0.00% | 0.0% | 0.001% |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 90 | $751k | $75 | $0 | $75 | $34.9B | 0.00% | 0.4% | 0.008% |
| 0xbf8f…adc6 | uni v4 | WBTC/cbBTC | 0.01% | 10 | $729k | $46 | $0 | $46 | $36.9B | 0.00% | 0.2% | 0.008% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 38 | $679k | $2038 | $0 | $2038 | $1.8B | 1.01% | 202.7% | 0.153% |
| [0xc061…1622](https://etherscan.io/address/0xc061caa073f3d95f80f8e5428d32d2d76f5e1622) | curve | USDC/USDG | ? | 16 | $577k | – | $0 | – | – | – | – | – |
| 0x8aa4…4e47 | uni v4 | ETH/USDT | 0.00% | 26 | $494k | $6 | $0 | $6 | $19.3B | 0.00% | 0.1% | 0.010% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 76 | $439k | $220 | $0 | $220 | $356.6M | 0.54% | 108.3% | 0.195% |
| 0xb90d…b716 | uni v4 | USDC/USDG | 0.01% | 13 | $356k | $29 | $0 | $29 | $9.0B | 0.00% | 0.6% | 0.008% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 64 | $355k | $4 | $0 | $4 | $10.5B | 0.00% | 0.1% | 0.010% |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 19 | $353k | $11 | $0 | $11 | $6.9B | 0.00% | 0.3% | 0.012% |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 596 | $300k | $30 | $0 | $30 | $10.5M | 2.48% | 500.6% | 1.346% |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 34 | $295k | $148 | $0 | $148 | $346.0M | 0.37% | 75.0% | 0.227% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 148 | $213k | $106 | $0 | $106 | $57.2M | 1.62% | 326.9% | 0.480% |
| 0x72da…f169 | uni v4 | USDC/mUSD | 0.00% | 12 | $203k | $0 | $0 | $0 | $49.8B | 0.00% | 0.0% | 0.001% |

Just-in-time liquidity: 25 episodes (mint and burn of identical liquidity inside one block), bracketing $20k of swaps and taking about $25 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 12 episodes, fees taken $23
- [0x94ba…a73d](https://etherscan.io/address/0x94ba4795a6d182f5d4a82ef08664c8ab2f1ba73d): 3 episodes, fees taken $0
- [0x0a79…a303](https://etherscan.io/address/0x0a79798576190304ebbf17632912532e3f0ea303): 3 episodes, fees taken $0
- [0x7a2c…0686](https://etherscan.io/address/0x7a2c7ae37a9c2b623c0fdb3d8e88d7b4bb5f0686): 3 episodes, fees taken $0
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 2 episodes, fees taken $0
- [0xc54b…1097](https://etherscan.io/address/0xc54b77b28ee4d18cd3d93991f08b79bc85c71097): 1 episodes, fees taken $2
- [0xaaa0…ffff](https://etherscan.io/address/0xaaa0bf2e340c2125603b8ffd4ec30faea08effff): 1 episodes, fees taken $0

Swap volume by venue: uniswap_v4 $10.9M (3521), curve $7.8M (401), uniswap_v3 $7.8M (6392), uniswap_v2_like $732k (3249), balancer $53k (57).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0x230e…804d (0x0000…0000/0xa0df…c845, 54 swaps); 0x1271…75aa (0xb58e…21cb/0xcedb…f8e7, 50 swaps); 0xdf47…aebf (0x0000…0000/0x999b…5108, 35 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 26 swaps); 0xce28…0c2f (0x0000…0000/0xa27e…62d2, 23 swaps); 0x17b3…4efd (0x5ab3…b691/0xdac1…1ec7, 15 swaps); 0x1ba3…1365 (0x0000…0000/0x0a5a…2477, 15 swaps); 0x2287…1bba (0x0000…0000/0xdac1…1ec7, 14 swaps); 0xc21b…416d (0x38ee…8a6a/0x98a8…4665, 14 swaps); 0xd4e5…909d (0x14d6…47a1/0xa0b8…eb48, 10 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | WBTC | 0.00% | 0.34% | 2.9% | $2.7B | $77.4M |
| Aave v3 | GHO | 0.00% | 4.00% | 82.8% | $135.2M | $111.9M |
| Aave v3 | USDe | 1.77% | 5.45% | 43.4% | $646.7M | $280.5M |
| Aave v3 | LINK | 0.01% | 0.48% | 3.1% | $111.4M | $3.4M |
| Aave v3 | DAI | 3.03% | 4.68% | 86.2% | $131.8M | $113.6M |
| Aave v3 | PYUSD | 3.72% | 4.82% | 85.9% | $7.8M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.9B | $7.3M |
| Aave v3 | RLUSD | 2.17% | 4.42% | 61.5% | $4.6M | $2.9M |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $288.8M | $0 |
| Aave v3 | USDC | 3.59% | 4.27% | 93.4% | $2.3B | $2.2B |
| Aave v3 | WETH | 1.42% | 2.02% | 82.5% | $5.4B | $4.4B |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.7% | $1.5B | $9.8M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $140k |
| Aave v3 | USDT | 3.57% | 4.26% | 93.1% | $3.0B | $2.8B |
| Aave v3 | USDS | 0.12% | 5.52% | 3.0% | $11.3M | $335k |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $144.3M | $334k |
| SparkLend | GHO | 0.00% | 0.00% | – | – | – |
| SparkLend | USDe | 0.00% | 0.00% | – | – | – |
| SparkLend | LINK | 0.00% | 0.00% | – | – | – |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $308.2M | $208.5M |
| SparkLend | PYUSD | 0.58% | 3.89% | 16.6% | $100.0M | $16.6M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9970 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sUSDe | 0.00% | 0.00% | – | – | – |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $25.6M | $23.6M |
| SparkLend | WETH | 1.57% | 1.98% | 83.4% | $1.2B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.02% | 1.3% | $289.1M | $3.8M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $105.7M | $0 |
| SparkLend | USDT | 2.62% | 3.52% | 82.8% | $387.3M | $320.5M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $713.3M | $468.0M |
| Compound v3 USDC | base | 4.82% | 5.78% | 90.5% | $373.0M | $337.5M |
| Compound v3 USDT | base | 2.99% | 3.81% | 83.1% | $185.4M | $154.0M |
| Compound v3 WETH | base | 1.36% | 1.88% | 67.8% | $125.8M | $85.3M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.43% APR on $1.4B of USDe.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | USDC | 94 | 4.28% → 4.27% | 4.19% – 4.28% | 3.60% → 3.59% |
| Aave v3 | USDe | 15 | 5.45% → 5.43% | 5.43% – 5.45% | 1.77% → 1.75% |
| Aave v3 | USDT | 52 | 4.26% → 4.26% | 4.26% – 4.26% | 3.57% → 3.57% |
| Aave v3 | WETH | 39 | 2.02% → 2.02% | 2.02% – 2.02% | 1.42% → 1.42% |
| Aave v3 | CRV | 2 | 5.77% → 5.77% | 5.77% – 5.77% | 0.47% → 0.47% |
| Aave v3 | LINK | 3 | 0.48% → 0.48% | 0.48% – 0.48% | 0.01% → 0.01% |
| Aave v3 | WBTC | 14 | 0.34% → 0.34% | 0.34% – 0.34% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 3 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | cbBTC | 7 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| SparkLend | WETH | 6 | 1.98% → 1.98% | 1.98% – 1.98% | 1.57% → 1.57% |
| SparkLend | DAI | 4 | 4.04% → 4.04% | 4.04% – 4.04% | 2.46% → 2.46% |
| Aave v3 | wstETH | 5 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | EURC | 2 | 3.87% → 3.87% | 3.87% – 3.87% | 2.20% → 2.20% |
| Aave v3 | RLUSD | 1 | 4.42% → 4.42% | 4.42% – 4.42% | 2.17% → 2.17% |
| Aave v3 | USDG | 1 | 3.20% → 3.20% | 3.20% – 3.20% | 1.31% → 1.31% |
| Aave v3 | GHO | 1 | 4.00% → 4.00% | 4.00% – 4.00% | 0.00% → 0.00% |
| SparkLend | USDT | 1 | 3.52% → 3.52% | 3.52% – 3.52% | 2.62% → 2.62% |
| SparkLend | PYUSD | 1 | 3.89% → 3.89% | 3.89% – 3.89% | 0.58% → 0.58% |
| SparkLend | USDS | 1 | 3.93% → 3.93% | 3.93% – 3.93% | 2.32% → 2.32% |
| Aave v3 | tBTC | 1 | 0.26% → 0.26% | 0.26% – 0.26% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: supply $53.5M, withdraw $56.3M, borrow $2.1M, repay $4.5M; SparkLend: withdraw $14k, borrow $300, supply $3957.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25918680 | Aave v3 | supply | USDC | $46.4M | [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) | [0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d) |
| 25918680 | Aave v3 | withdraw | USDC | $46.4M | [0xd4fa…d23e](https://etherscan.io/address/0xd4fa2d31b7968e448877f69a96de69f5de8cd23e) | [0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d) |
| 25918761 | Aave v3 | withdraw | sUSDe | $2.6M | [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) | [0x2a4b…3ec6](https://etherscan.io/tx/0x2a4b887380744e07e49a65f65c8b289f9bf448234715ccb3cfe9632c131f3ec6) |
| 25918744 | Aave v3 | repay | USDe | $2.3M | [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) | [0x0b8e…f8e5](https://etherscan.io/tx/0x0b8effa370896607440d232cc2ccc446d81d100e92d1b89bdbd192f393c7f8e5) |
| 25918740 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x30ef…c679](https://etherscan.io/tx/0x30efdfa0842bb7345e20e89748169f1af45b1a4e1fda7c65b72576293e8ec679) |
| 25918740 | Aave v3 | withdraw | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xb748…1677](https://etherscan.io/tx/0xb7483fad6a2768445c245770047fd0876c4be85b28f0e0be25ea757796141677) |
| 25918714 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xd5a1…cd9a](https://etherscan.io/tx/0xd5a12b69f4cdb6b26b7a1291d9438d852ad2f410fe7c738c24df4b3c5136cd9a) |
| 25918689 | Aave v3 | supply | USDT | $955k | [0x7b0f…a423](https://etherscan.io/address/0x7b0f8287137c664976172782ecb1af77f82ea423) | [0x1d36…1a63](https://etherscan.io/tx/0x1d36090a1c68da11fd24ab8239d7b9fcf93f9a2018e06f1ae64127219e731a63) |
| 25918657 | Aave v3 | withdraw | USDT | $900k | [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) | [0xf6a5…bfc7](https://etherscan.io/tx/0xf6a52ec494bf7708c03dc61f9a8fbece6715c483c3659d6b76fc8df99c20bfc7) |
| 25918657 | Aave v3 | supply | USDC | $899k | [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) | [0xf6a5…bfc7](https://etherscan.io/tx/0xf6a52ec494bf7708c03dc61f9a8fbece6715c483c3659d6b76fc8df99c20bfc7) |
| 25918665 | Aave v3 | withdraw | USDC | $898k | [0xfd08…76ca](https://etherscan.io/address/0xfd087771b4b0defba68bac616dd9209b798976ca) | [0xdad2…048a](https://etherscan.io/tx/0xdad2c3be993c875bcab74c931bf8c9a13b69c6064a6f372a00c9248a4926048a) |
| 25918742 | Aave v3 | repay | USDC | $600k | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x06c0…a7ce](https://etherscan.io/tx/0x06c0b6a0303d190e7f3ee03ac2d18b0cd45a485f9eaadeefd22b3d1105b5a7ce) |
| 25918783 | Aave v3 | borrow | USDT | $596k | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x2505…c2f1](https://etherscan.io/tx/0x2505ef8143a5447e93aee163165d881ee1774e070e23271b872a0931a801c2f1) |
| 25918596 | Aave v3 | borrow | USDT | $500k | [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) | [0xe168…c006](https://etherscan.io/tx/0xe168cd3146ec1c39be2d5cafc1322a95cb167192db7455ffc77bf92a2302c006) |
| 25918593 | Aave v3 | repay | WETH | $489k | [0x4f87…0545](https://etherscan.io/address/0x4f87de7d21aef48090958f7342e1f69dff790545) | [0xc8f8…463e](https://etherscan.io/tx/0xc8f8c88cd6a80ae052ec034264f17303bf4948a7b7e8a8a2fecb2c2ff9c2463e) |
| 25918685 | Aave v3 | withdraw | WBTC | $407k | [0xba5b…76e1](https://etherscan.io/address/0xba5b1a301706969d1ea25f917db7c2d22c3776e1) | [0x3e80…1881](https://etherscan.io/tx/0x3e80c85719560df788634f0aba4f576bb208d2d612b945192d6b8238b2a31881) |
| 25918672 | Aave v3 | supply | WETH | $293k | [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) | [0xd3ef…da8b](https://etherscan.io/tx/0xd3ef195fa49d1bfa9beba748fe871de6beeec4e80642eea53b085040f006da8b) |
| 25918672 | Aave v3 | withdraw | WETH | $293k | [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) | [0x2eda…0f5a](https://etherscan.io/tx/0x2eda30f39ac76d7ba9508292aae2aebd8d0bddb275e314597b261ffdd6330f5a) |
| 25918554 | Aave v3 | supply | USDC | $255k | [0xa61e…c569](https://etherscan.io/address/0xa61ef367d6de25753da50d396ef103ae6517c569) | [0xa02a…9c05](https://etherscan.io/tx/0xa02ad3075c05101837ca6408a68ccc8a41a5b5c2f0c7a0e7621e6b8d47439c05) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- Aave v3 withdraw $46.4M USDC by [0xd4fa…d23e](https://etherscan.io/address/0xd4fa2d31b7968e448877f69a96de69f5de8cd23e) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d)): $46.4M → [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c); $46.4M → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb); $10k → [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) → forwarded to deposit sink (behaviour, day study); $10k → [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) → forwarded to deposit sink (behaviour, day study) **[to exchange $100k]**
- Aave v3 withdraw $2.6M sUSDe by [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) ([0x2a4b…3ec6](https://etherscan.io/tx/0x2a4b887380744e07e49a65f65c8b289f9bf448234715ccb3cfe9632c131f3ec6)): $2.6M → [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000)
- Aave v3 withdraw $1.8M WETH by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xb748…1677](https://etherscan.io/tx/0xb7483fad6a2768445c245770047fd0876c4be85b28f0e0be25ea757796141677)): $1.8M → [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $26k → [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b); $1.8M → [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e)
- Aave v3 withdraw $900k USDT by [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) ([0xf6a5…bfc7](https://etherscan.io/tx/0xf6a52ec494bf7708c03dc61f9a8fbece6715c483c3659d6b76fc8df99c20bfc7)): $900k → [0x4d4e…c791](https://etherscan.io/address/0x4d4e14fbdf6bb02b6e036f86f120f00abe41c791); $124k → [0x4ddf…75e1](https://etherscan.io/address/0x4ddf368080cd7946db5b459ad591c350158175e1); $35k → [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) → forwarded to deposit sink (behaviour, day study); $63k → [0x4ddf…75e1](https://etherscan.io/address/0x4ddf368080cd7946db5b459ad591c350158175e1) **[to exchange $35k]**
- Aave v3 withdraw $898k USDC by [0xfd08…76ca](https://etherscan.io/address/0xfd087771b4b0defba68bac616dd9209b798976ca) ([0xdad2…048a](https://etherscan.io/tx/0xdad2c3be993c875bcab74c931bf8c9a13b69c6064a6f372a00c9248a4926048a)): $898k → [deposit sink (behaviour, day study)](https://etherscan.io/address/0x4a6c312ec70e8747a587ee860a0353cd42be0ae0) **[to exchange $898k]**
- Aave v3 borrow $596k USDT by [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) ([0x2505…c2f1](https://etherscan.io/tx/0x2505ef8143a5447e93aee163165d881ee1774e070e23271b872a0931a801c2f1)): $602k → [0x6c96…1dee](https://etherscan.io/address/0x6c96de32cea08842dcc4058c14d3aaad7fa41dee)
- Aave v3 borrow $500k USDT by [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) ([0xe168…c006](https://etherscan.io/tx/0xe168cd3146ec1c39be2d5cafc1322a95cb167192db7455ffc77bf92a2302c006)): $500k → [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) → forwarded to deposit sink (behaviour, day study) **[to exchange $500k]**
- Aave v3 withdraw $293k WETH by [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x2eda…0f5a](https://etherscan.io/tx/0x2eda30f39ac76d7ba9508292aae2aebd8d0bddb275e314597b261ffdd6330f5a)): $293k → [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $293k → [0x45e9…9215](https://etherscan.io/address/0x45e9b04942176a513b22acc1ced75c34d2fd9215)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| Aave v3 | [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) | $3.8M | $1.8M | 1.672 | 40.2% |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| Aave v3 | [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) | $3818 | $0 | ∞ | – |
| Aave v3 | [0xfd08…76ca](https://etherscan.io/address/0xfd087771b4b0defba68bac616dd9209b798976ca) | $0 | $0 | ∞ | – |
| SparkLend | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | $55.0M | $0 | ∞ | – |
| SparkLend | [0x8113…82d3](https://etherscan.io/address/0x81133a5d99fd133be1c0d16ec72aee5c83fe82d3) | $0 | $0 | ∞ | – |

Flash loans (events): BalFlash 38 ($6.0M).


## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 207 | $6.6M | 0.999904 | 0.999867 – 0.999978 | 1.00008 | -1.8 bps |
| USDS | 45 | $3.9M | 1.00003 | 0.999963 – 1.00007 | 1 | +0.3 bps |
| DAI | 40 | $2.4M | 1.00006 | 0.999837 – 1.00008 | 0.999677 | +3.8 bps |
| USDG | 42 | $1.1M | 0.999976 | 0.9999 – 1.00017 | 1 | -0.2 bps |
| USDe | 22 | $602k | 0.999842 | 0.999807 – 1.00005 | 1 | -1.6 bps |
| PYUSD | 3 | $530k | 1.0001 | 1.0001 – 1.00011 | 1 | +1.0 bps |
| USD1 | 4 | $513k | 0.999863 | 0.999823 – 1.00133 | 1 | -1.4 bps |
| mUSD | 3 | $202k | 0.999857 | 0.999852 – 0.999857 | – | – |
| LDO | 69 | $144k | 0.416773 | 0.414017 – 0.419495 | – | – |
| wTAO | 41 | $122k | 245.56 | 244.39 – 245.978 | – | – |
| weETH | 5 | $118k | 2753.91 | 2753.91 – 2753.92 | 2753.96 | -0.2 bps |
| wstETH | 12 | $102k | 3103.82 | 3102.32 – 3104.18 | 3109.45 | -18.1 bps |
| RAIL | 28 | $93k | 2.36772 | 2.32793 – 2.40813 | – | – |
| AZTEC | 24 | $85k | 0.0149597 | 0.0148149 – 0.0151329 | – | – |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 120 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDC | $58.0M | $56.8M | $1.2M |
| USDT | $27.0M | $56.3M | $-29.3M |
| ETH | $12.2M | $26.4M | $-14.2M |
| WETH | $6.4M | $7.7M | $-1.3M |
| cbBTC | $4.4M | $2.2M | $2.2M |
| WBTC | $3.3M | $3.0M | $227k |
| USDG | $1.8M | $2.6M | $-797k |
| DAI | $2.1M | $1.9M | $200k |
| USDS | $1.8M | $1.8M | $0 |
| USDe | $1.0M | $1.0M | $0 |
| RLUSD | $242k | $1.0M | $-800k |
| PYUSD | $531k | $531k | $0 |

By label: deposit sink (behaviour, day study) in $46.1M / out $44.5M; Coinbase 11 (memory) in $23.0M / out $30.6M; Binance 16 (memory) in $0 / out $30.9M; Binance 14 (memory) in $17.3M / out $4.6M; hot wallet (behaviour, day study) in $4.8M / out $14.3M; exchange deposit contract (day study, unidentified) in $9.2M / out $6.4M; Binance 15 (memory) in $0 / out $12.3M; Coinbase 10 (memory) in $8.2M / out $4.1M; Gate.io (memory) in $3.8M / out $5.0M; hot wallet (day study, unidentified) in $6.2M / out $1.6M; exchange hot wallet with USDG desk (day study) in $1.2M / out $2.8M; Binance 20 (memory) in $0 / out $3.1M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25918684 | WBTC | $440.5M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e) |
| 25918684 | WBTC | $440.5M ×2 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e) |
| 25918684 | USDC | $106.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e) |
| 25918684 | USDC | $106.1M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e) |
| 25918830 | USDC | $106.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd) |
| 25918830 | USDC | $106.1M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd) |
| 25918670 | WBTC | $80.9M | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) | [0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067) |
| 25918670 | WBTC | $80.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) | [0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067) |
| 25918670 | WBTC | $80.9M | [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067) |
| 25918670 | WBTC | $80.9M | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067) |
| 25918670 | WBTC | $80.9M | [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067) |
| 25918680 | USDC | $46.4M | [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) | [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) | [0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d) |
| 25918680 | USDC | $46.4M | [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) | [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) | [0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d) |
| 25918680 | USDC | $46.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) | [0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d) |
| 25918680 | USDC | $46.4M | [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d) |
| 25918675 | ETH | $36.8M | [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) | [0x21a3…5549](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) | [0x2392…aaaf](https://etherscan.io/tx/0x239224012d163401de098beea6bfaeb5129d4d60f110c0dd8d4005f71f2eaaaf) |
| 25918756 | USDT | $28.4M | [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) | [0x98ad…ba9d](https://etherscan.io/address/0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d) | [0xae35…9548](https://etherscan.io/tx/0xae35398be3eaffc1354a8112d09bc13780c7ac568ab1b7ddd52c9e020d4d9548) |
| 25918830 | WETH | $27.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd) |
| 25918830 | WETH | $27.4M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd) |
| 25918684 | WETH | $27.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e) |
| 25918684 | WETH | $27.4M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e) |
| 25918603 | USDT | $25.5M | [0xe2e7…c372](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372) | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794) |
| 25918818 | WETH | $25.0M ×3 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x6acd…7528](https://etherscan.io/tx/0x6acd40e395b2117055283e6fe3369f4e007bae65bf392fb452609cf4dd247528) |
| 25918818 | WETH | $25.0M ×3 | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x6acd…7528](https://etherscan.io/tx/0x6acd40e395b2117055283e6fe3369f4e007bae65bf392fb452609cf4dd247528) |
| 25918832 | WETH | $25.0M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0x218f…aeda](https://etherscan.io/tx/0x218f4db1fc368c68f58ba9ef2f62cdf12615f05d79a3d0f6b785aefc330caeda) |
| 25918832 | WETH | $25.0M ×2 | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x218f…aeda](https://etherscan.io/tx/0x218f4db1fc368c68f58ba9ef2f62cdf12615f05d79a3d0f6b785aefc330caeda) |
| 25918554 | WETH | $24.9M ×10 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x57fb…fd5f](https://etherscan.io/tx/0x57fb54e8a4885f7187ae538e28c7a81e8ba362553a1d87d971b4f46248f1fd5f) |
| 25918554 | WETH | $24.9M ×10 | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x57fb…fd5f](https://etherscan.io/tx/0x57fb54e8a4885f7187ae538e28c7a81e8ba362553a1d87d971b4f46248f1fd5f) |
| 25918562 | WETH | $24.9M ×6 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0x8cdd…419d](https://etherscan.io/tx/0x8cdd4a202e806b783640add949b049bd157ba84ec94d8fd1c404393454c5419d) |
| 25918562 | WETH | $24.9M ×6 | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8cdd…419d](https://etherscan.io/tx/0x8cdd4a202e806b783640add949b049bd157ba84ec94d8fd1c404393454c5419d) |

Round trips (≥ $10M out and back within the window): $12.6M USDC from [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) via [0x3b5b…e4b7](https://etherscan.io/address/0x3b5b1991c1c274573ae729cd31f3a6bb1f60e4b7), back after 3 min.


Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25918780 | curve | USDT → USDC | $2.7M | [0x1570…7099](https://etherscan.io/address/0x1570bc3abaa351e07fe6f73ea19aa81d7b827099) | [0x2dc9…9669](https://etherscan.io/tx/0x2dc959aa1590c7b1c203a18f51e9ca5f726b7c9b404e91c1fe1436f61f109669) |

## E. Bridges, issuance, staking

Outbound: $6.4M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $2.1M (92).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| CCTP | USDC | Polygon | 12 | $1.6M | 0xf70da97812cb… $1.6M |
| CCTP | USDC | domain 15 | 6 | $1.2M | 0x424a31a57f7c… $1.1M |
| CCTP | USDC | Avalanche | 30 | $1.2M | 0x65c340eb0688… $706k |
| OFT | USDT | eid 30390 | 1 | $602k | – |
| OFT | USDT | eid 30420 | 4 | $384k | – |
| OFT | USDe | eid 30383 | 2 | $313k | – |
| OFT | USDG | eid 30274 | 3 | $260k | – |
| OFT | USDT | Arbitrum | 2 | $195k | – |
| CCTP | USDC | Arbitrum | 15 | $157k | 0x6a2abff960b6… $103k |
| CCTP | USDC | Solana | 4 | $80k | 11e29a6044a68b… $75k |
| CCTP | USDC | Base | 26 | $77k | 0x5bea6572ccb4… $60k |
| OFT | USDG | eid 30416 | 6 | $76k | – |
| OFT | USDG | Solana | 1 | $74k | – |
| OFT | PYUSD | Arbitrum | 2 | $60k | – |
| CCTP | USDC | OP Mainnet | 14 | $55k | 0xdedb0e722e69… $22k |
| CCTP | USDC | Sui | 3 | $50k | 39bb1dfbe50fba… $50k |
| OFT | USDT | eid 30274 | 1 | $6825 | – |
| CCTP | USDC | domain 19 | 10 | $5332 | 0xb21d281dedb1… $3626 |
| OFT | USDC | Base | 2 | $841 | – |
| OFT | USDe | eid 30416 | 1 | $140 | – |

Issuance totals: USDC mint $6.7M (155); USDC burn $18.0M (134). Largest: USDC burn $12.6M ([0x2fed…2d25](https://etherscan.io/tx/0x2fedfb9b74f7af11b9b55c9d3926e7c70caf7ae9732c6d09bc44e3c548922d25)); USDC mint $4.6M ([0xe9fa…5796](https://etherscan.io/tx/0xe9fa754cc99891c1e643ff97417fa30b7c469642d23a0c06258306ac09295796)); USDC burn $1.1M ([0x961a…c1ad](https://etherscan.io/tx/0x961af976495ed25705739027e656c32bb1f8cb6c8018db16efa16eeba801c1ad)); USDC mint $990k ([0xb0b0…30af](https://etherscan.io/tx/0xb0b0424fb1f5c2f5f05b7e395603dd49ba30fd939d0dd64d1249c385f94130af)); USDC burn $809k ([0xc941…39a7](https://etherscan.io/tx/0xc941a98de9a5d40ac9e57fbcc514c5dae9daef8bbf645cd015e4e777984a39a7)).


WETH wrapped 7098 ETH, unwrapped 4833 ETH; Lido staked 170.3 ETH, withdrawal requests 9.0 ETH; sUSDe cooldowns 6 for $3.3M.


## F. Gas market and block production

Base fee 0.069 → 0.054 gwei (min 0.039, median 0.057, max 0.093); blocks 50% full; median tip 0.073 gwei; 5.1% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 157,  Quasar (quasar.win)  36, BuilderNet 34, Eureka (eurekabuilder.xyz) 24, bombora.build  15, gethgo1.25.10linux 6.


Most active senders: [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 1351, [0xe883…dd91](https://etherscan.io/address/0xe8832a868c091263ed190a9f4be304a03895dd91) 760, [Binance 14 (memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 684, [Binance 15 (memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 566, [Binance 16 (memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 468, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 419, [Binance 17 (memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 393, [Binance 18 (memory)](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 349, [0xfa84…8eea](https://etherscan.io/address/0xfa84720dc394a14434a86cf0d12973a7fa6e8eea) 342, [0xbb2f…37e0](https://etherscan.io/address/0xbb2f33f73ccc2c74e3fb9bb8eb75241ac15337e0) 260.


Intent fills: OneInchFilled 220, CoWTrade 171, UniXFill 62. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.


---

## G. Live log

Live log started 2026-09-06T11:49:53+00:00 UTC at block 25917895. One line per block with anything notable; a rolling re-analysis of the trailing 1.0 h every 10 blocks rewrites the sections above.

- **25918028** 11:32:59 base 0.05 gwei, 23 txs, bobTheBuilder.xyz
- **25918029** 11:33:11 base 0.04 gwei, 378 txs, erigon-3.6.0-ecc2ad99
- **25918030** 11:33:23 base 0.04 gwei, 483 txs, Titan (titanbuilder.xyz)
  - transfer $11.4M sUSDe [0xa711…6d69](https://etherscan.io/address/0xa711a3a64f2b2d7e05dc3f564d3862d7499c6d69) → [0xb221…dc61](https://etherscan.io/address/0xb22161a2222ae7008cb3c54f819025031b1bdc61) ([0x054d…b60b](https://etherscan.io/tx/0x054d26e60bb91ede47184e931bb99337598565a922a447e20cccc9023356b60b))
- **25918031** 11:33:35 base 0.05 gwei, 271 txs, Titan (titanbuilder.xyz)
- **25918032** 11:33:47 base 0.05 gwei, 213 txs, Titan (titanbuilder.xyz)
- **25918033** 11:33:59 base 0.05 gwei, 277 txs, Titan (titanbuilder.xyz)
- **25918034** 11:34:11 base 0.05 gwei, 391 txs, Eureka (eurekabuilder.xyz)
- **25918035** 11:34:23 base 0.05 gwei, 244 txs,  Quasar (quasar.win) 
- **25918036** 11:34:35 base 0.05 gwei, 325 txs, Eureka (eurekabuilder.xyz)
  - JIT 1 episode(s), $25 of swaps bracketed, fees taken $1
- **25918037** 11:34:47 base 0.05 gwei, 194 txs, Titan (titanbuilder.xyz)
- **25918038** 11:34:59 base 0.05 gwei, 271 txs, Titan (titanbuilder.xyz)
  - transfer $11.4M sUSDe [0xb221…dc61](https://etherscan.io/address/0xb22161a2222ae7008cb3c54f819025031b1bdc61) → [0x31b7…b95a](https://etherscan.io/address/0x31b7d5a2b1ce1871dd642f6aecc0ef68d126b95a) ([0xb19f…c377](https://etherscan.io/tx/0xb19fb0edef0d74a6e5f28909d72333409aff35a656affdfaaf12bf72ad6fc377))
- **25918039** 11:35:11 base 0.05 gwei, 260 txs, Titan (titanbuilder.xyz)
  - JIT 3 episode(s), $555 of swaps bracketed, fees taken $0
- **25918040** 11:35:23 base 0.05 gwei, 218 txs, Titan (titanbuilder.xyz)
- **25918041** 11:35:35 base 0.05 gwei, 242 txs, Titan (titanbuilder.xyz)
- **25918042** 11:35:47 base 0.05 gwei, 293 txs,  Quasar (quasar.win) 
  - transfer $11.4M sUSDe [0x31b7…b95a](https://etherscan.io/address/0x31b7d5a2b1ce1871dd642f6aecc0ef68d126b95a) → [0x211c…e5d2](https://etherscan.io/address/0x211cc4dd073734da055fbf44a2b4667d5e5fe5d2) ([0x74ae…fb3f](https://etherscan.io/tx/0x74ae722379a0134bd96957bb18dd5d5f9dcf5c16d09e4fcc23d5145d3fbdfb3f))
  - bridge OFT $11.4M sUSDe → eid 30383 ([0x74ae…fb3f](https://etherscan.io/tx/0x74ae722379a0134bd96957bb18dd5d5f9dcf5c16d09e4fcc23d5145d3fbdfb3f))
- **25918043** 11:35:59 base 0.05 gwei, 148 txs, Titan (titanbuilder.xyz)
- **25918044** 11:36:11 base 0.05 gwei, 92 txs, gethgo1.25.10linux
- **25918045** 11:36:23 base 0.05 gwei, 231 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x2c86…6efe](https://etherscan.io/tx/0x2c861655ffbd96362731d04337d20dae58eb0ecb3abcd86ac460f4f90de06efe))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x2c86…6efe](https://etherscan.io/tx/0x2c861655ffbd96362731d04337d20dae58eb0ecb3abcd86ac460f4f90de06efe))
- **25918046** 11:36:35 base 0.05 gwei, 258 txs, Titan (titanbuilder.xyz)
- **25918047** 11:36:47 base 0.05 gwei, 195 txs, BuilderNet
- **25918048** 11:36:59 base 0.05 gwei, 225 txs, Titan (titanbuilder.xyz)
- **25918049** 11:37:11 base 0.05 gwei, 223 txs, bombora.build 
- **25918050** 11:37:23 base 0.05 gwei, 281 txs, Titan (titanbuilder.xyz)
- **25918051** 11:37:35 base 0.05 gwei, 152 txs, Titan (titanbuilder.xyz)
- **25918052** 11:37:47 base 0.05 gwei, 244 txs, Titan (titanbuilder.xyz)
- **25918053** 11:37:59 base 0.05 gwei, 192 txs, Eureka (eurekabuilder.xyz)
- **25918054** 11:38:11 base 0.05 gwei, 241 txs, Titan (titanbuilder.xyz)
- **25918055** 11:38:23 base 0.05 gwei, 163 txs, Titan (titanbuilder.xyz)
- **25918056** 11:38:35 base 0.05 gwei, 200 txs, Titan (titanbuilder.xyz)
- **25918057** 11:38:47 base 0.05 gwei, 60 txs, gethgo1.26.4linux
- **25918058** 11:38:59 base 0.04 gwei, 273 txs, BuilderNet
- **25918059** 11:39:11 base 0.05 gwei, 235 txs, Eureka (eurekabuilder.xyz)
- **25918060** 11:39:23 base 0.05 gwei, 278 txs, BuilderNet
  - transfer $10.0M USDT [0xcffa…0703](https://etherscan.io/address/0xcffad3200574698b78f32232aa9d63eabd290703) → [0xde46…3aea](https://etherscan.io/address/0xde46bd6efc4e44ba1b75ab5e9d12f49ee60d3aea) ([0x3906…6a9d](https://etherscan.io/tx/0x3906c5b640fc5da9a73f06b179b3b6863a10c19b283a9d9f9b168e9e1ed96a9d))
- **25918061** 11:39:35 base 0.05 gwei, 76 txs, BuilderNet
- **25918062** 11:39:47 base 0.05 gwei, 349 txs,  Quasar (quasar.win) 
- **25918063** 11:39:59 base 0.05 gwei, 192 txs, Titan (titanbuilder.xyz)
- **25918064** 11:40:11 base 0.05 gwei, 256 txs, Eureka (eurekabuilder.xyz)
- **25918065** 11:40:23 base 0.05 gwei, 183 txs, bombora.build 
- **25918066** 11:40:35 base 0.05 gwei, 301 txs, Eureka (eurekabuilder.xyz)
- **25918067** 11:40:47 base 0.06 gwei, 171 txs,  Quasar (quasar.win) 
- **25918068** 11:40:59 base 0.06 gwei, 112 txs, Powered by bloXroute
- **25918069** 11:41:11 base 0.06 gwei, 118 txs, Nethermind v1.39.0
- **25918070** 11:41:23 base 0.05 gwei, 266 txs, Eureka (eurekabuilder.xyz)
  - transfer $80.9M WBTC [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) → [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) ([0xeb9d…f7df](https://etherscan.io/tx/0xeb9d2308f6792efed345ef93b99f458dc2a5fab1dce269d19c9794a474aaf7df))
  - transfer $80.9M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) ([0xeb9d…f7df](https://etherscan.io/tx/0xeb9d2308f6792efed345ef93b99f458dc2a5fab1dce269d19c9794a474aaf7df))
  - transfer $80.9M WBTC [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) → [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) ([0xeb9d…f7df](https://etherscan.io/tx/0xeb9d2308f6792efed345ef93b99f458dc2a5fab1dce269d19c9794a474aaf7df))
  - transfer $80.9M WBTC [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) → [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) ([0xeb9d…f7df](https://etherscan.io/tx/0xeb9d2308f6792efed345ef93b99f458dc2a5fab1dce269d19c9794a474aaf7df))
  - transfer $80.9M WBTC [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xeb9d…f7df](https://etherscan.io/tx/0xeb9d2308f6792efed345ef93b99f458dc2a5fab1dce269d19c9794a474aaf7df))
- **25918071** 11:41:35 base 0.05 gwei, 300 txs, Titan (titanbuilder.xyz)
- **25918072** 11:41:47 base 0.06 gwei, 317 txs,  Quasar (quasar.win) 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x569c…dc36](https://etherscan.io/tx/0x569cd5d1d231a2d5107f39aa927cb560efbc96685cc5e15623d4f4595a6fdc36))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x569c…dc36](https://etherscan.io/tx/0x569cd5d1d231a2d5107f39aa927cb560efbc96685cc5e15623d4f4595a6fdc36))
- **25918073** 11:41:59 base 0.06 gwei, 225 txs,  Quasar (quasar.win) 
- **25918074** 11:42:11 base 0.06 gwei, 130 txs, beaverbuild.org
- **25918075** 11:42:23 base 0.05 gwei, 316 txs,  Quasar (quasar.win) 
- **25918076** 11:42:35 base 0.06 gwei, 159 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x61fb…cb31](https://etherscan.io/tx/0x61fbcab652639054c2b12706b44f43c723978a1417101f3716c82d62b89fcb31))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x61fb…cb31](https://etherscan.io/tx/0x61fbcab652639054c2b12706b44f43c723978a1417101f3716c82d62b89fcb31))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xbc16…885c](https://etherscan.io/tx/0xbc16eeccfc9704c732e4abfaf2812e5c29a7a33e424021724946b31a1614885c))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xbc16…885c](https://etherscan.io/tx/0xbc16eeccfc9704c732e4abfaf2812e5c29a7a33e424021724946b31a1614885c))
- **25918077** 11:42:47 base 0.06 gwei, 293 txs,  Quasar (quasar.win) 
- **25918078** 11:42:59 base 0.06 gwei, 322 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x2b26…5a3e](https://etherscan.io/tx/0x2b263ec7f2f6c42cc34cc93fc575b1a9a54607b76398c9704a1365c8b56c5a3e))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x2b26…5a3e](https://etherscan.io/tx/0x2b263ec7f2f6c42cc34cc93fc575b1a9a54607b76398c9704a1365c8b56c5a3e))
  - transfer $10.0M USDT [0xde46…3aea](https://etherscan.io/address/0xde46bd6efc4e44ba1b75ab5e9d12f49ee60d3aea) → [Binance 14 (memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) ([0xd881…9dbc](https://etherscan.io/tx/0xd881dcaa5cb066e25ee4927c29780be59653e0eb1b155198c41c258cc0be9dbc))
- **25918079** 11:43:11 base 0.06 gwei, 178 txs, Titan (titanbuilder.xyz)
- **25918080** 11:43:23 base 0.06 gwei, 244 txs,  Quasar (quasar.win) 
- **25918081** 11:43:35 base 0.06 gwei, 219 txs, BuilderNet
- **25918082** 11:43:47 base 0.06 gwei, 72 txs, gethgo1.26.4linux
- **25918083** 11:43:59 base 0.05 gwei, 252 txs, Titan (titanbuilder.xyz)
- **25918084** 11:44:11 base 0.06 gwei, 187 txs, Titan (titanbuilder.xyz)
  - JIT 2 episode(s), $22k of swaps bracketed, fees taken $0
- **25918085** 11:44:23 base 0.06 gwei, 222 txs, Eureka (eurekabuilder.xyz)
- **25918086** 11:44:35 base 0.07 gwei, 142 txs, BuilderNet
- **25918087** 11:44:47 base 0.07 gwei, 152 txs, BuilderNet
- **25918088** 11:44:59 base 0.06 gwei, 366 txs, Eureka (eurekabuilder.xyz)
- **25918089** 11:45:11 base 0.06 gwei, 246 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xd549…746a](https://etherscan.io/tx/0xd549bd8b6c3bf46f8f5ac72feab95f64e4f7ec63f764cd7ca2e6a293eca4746a))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xd549…746a](https://etherscan.io/tx/0xd549bd8b6c3bf46f8f5ac72feab95f64e4f7ec63f764cd7ca2e6a293eca4746a))
- **25918090** 11:45:23 base 0.07 gwei, 65 txs, BuilderNet
- **25918091** 11:45:35 base 0.06 gwei, 219 txs, Titan (titanbuilder.xyz)
- **25918092** 11:45:47 base 0.06 gwei, 233 txs, BuilderNet
- **25918093** 11:45:59 base 0.06 gwei, 229 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x43ea…8a63](https://etherscan.io/tx/0x43ea9ae729492b7ec75b56ab97ce6c364487e6336a500b45f2724bb0ffe38a63))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x43ea…8a63](https://etherscan.io/tx/0x43ea9ae729492b7ec75b56ab97ce6c364487e6336a500b45f2724bb0ffe38a63))
- **25918094** 11:46:11 base 0.06 gwei, 225 txs, Titan (titanbuilder.xyz)
- **25918095** 11:46:23 base 0.07 gwei, 114 txs, Titan (titanbuilder.xyz)
- **25918096** 11:46:35 base 0.07 gwei, 256 txs, BuilderNet
  - JIT 3 episode(s), $9 of swaps bracketed, fees taken $0
- **25918097** 11:46:47 base 0.07 gwei, 427 txs, BuilderNet
- **25918098** 11:46:59 base 0.08 gwei, 235 txs, Titan (titanbuilder.xyz)
- **25918099** 11:47:11 base 0.07 gwei, 284 txs, Eureka (eurekabuilder.xyz)
- **25918100** 11:47:23 base 0.08 gwei, 215 txs, Eureka (eurekabuilder.xyz)
- **25918101** 11:47:35 base 0.08 gwei, 230 txs, Titan (titanbuilder.xyz)
- **25918102** 11:47:47 base 0.08 gwei, 175 txs, Titan (titanbuilder.xyz)
- **25918103** 11:47:59 base 0.07 gwei, 220 txs, Titan (titanbuilder.xyz)
  - JIT 3 episode(s), $537 of swaps bracketed, fees taken $0
- **25918104** 11:48:11 base 0.07 gwei, 285 txs, bombora.build 
- **25918105** 11:48:23 base 0.07 gwei, 251 txs, Titan (titanbuilder.xyz)
- **25918106** 11:48:35 base 0.07 gwei, 270 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $122 of swaps bracketed, fees taken $1
- **25918107** 11:48:47 base 0.08 gwei, 250 txs, Titan (titanbuilder.xyz)
  - lending Aave v3 supply $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xc530…d61a](https://etherscan.io/tx/0xc5305434a9304ca1426be2fbe91d269a73a87a8232c6bad02b5eeb35b414d61a))
  - lending Aave v3 withdraw $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x7eff…873b](https://etherscan.io/tx/0x7eff58619d6b77a31ed1bf17b63a55d220b3e78886631bbdf5e536a80731873b))
- **25918108** 11:48:59 base 0.07 gwei, 259 txs, bombora.build 
- **25918109** 11:49:11 base 0.07 gwei, 216 txs, BuilderNet
- **25918110** 11:49:23 base 0.07 gwei, 334 txs,  Quasar (quasar.win) 
- **25918111** 11:49:35 base 0.07 gwei, 256 txs, Titan (titanbuilder.xyz)
- **25918112** 11:49:47 base 0.07 gwei, 15 txs, bobTheBuilder.xyz
  - transfer $8.3M wstETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $8.3M wstETH [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x0b92…9371](https://etherscan.io/address/0x0b925ed163218f6662a35e0f0371ac234f9e9371) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $8.3M wstETH [0x0b92…9371](https://etherscan.io/address/0x0b925ed163218f6662a35e0f0371ac234f9e9371) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $8.3M wstETH [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $8.3M wstETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $8.3M wstETH [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x0b92…9371](https://etherscan.io/address/0x0b925ed163218f6662a35e0f0371ac234f9e9371) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $8.3M wstETH [0x0b92…9371](https://etherscan.io/address/0x0b925ed163218f6662a35e0f0371ac234f9e9371) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $8.3M wstETH [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $6.5M USDC [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $6.5M USDC [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $6.5M USDC [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $6.5M USDC [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $6.5M USDT [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $6.5M USDT [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $6.5M USDT [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $6.5M USDC [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $6.5M USDT [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $6.5M USDC [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - transfer $6.5M USDC [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) → [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - transfer $6.5M USDC [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) → [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - lending Aave v3 supply $8.3M wstETH account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - lending Aave v3 borrow $6.5M USDC account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - lending Aave v3 repay $6.5M USDC account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - lending Aave v3 withdraw $8.3M wstETH account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - lending Aave v3 supply $8.3M wstETH account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - lending Aave v3 borrow $6.5M USDC account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - lending Aave v3 repay $6.5M USDC account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - lending Aave v3 withdraw $8.3M wstETH account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - swap $6.5M USDT → USDC on uniswap_v4 by [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) ([0x894e…8c19](https://etherscan.io/tx/0x894e3cbad4ea38428a93326dde7b81fd85f8e7801b3216f03aecc77ce3878c19))
  - swap $6.5M USDC → USDT on uniswap_v4 by [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) ([0xaefd…99d7](https://etherscan.io/tx/0xaefd5edf6bf93020a6ff4e732d86b184962f4ce3d34582cb98b683d7949199d7))
  - JIT 1 episode(s), $14k of swaps bracketed, fees taken $0
- **25918113** 11:49:59 base 0.06 gwei, 463 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $430 of swaps bracketed, fees taken $0
- **25918114** 11:50:11 base 0.07 gwei, 320 txs,  Quasar (quasar.win) 
  - JIT 1 episode(s), $242 of swaps bracketed, fees taken $0
- **25918115** 11:50:23 base 0.07 gwei, 205 txs, Titan (titanbuilder.xyz)
- **25918116** 11:50:35 base 0.08 gwei, 307 txs, Titan (titanbuilder.xyz)
- **25918117** 11:50:47 base 0.08 gwei, 160 txs, Titan (titanbuilder.xyz)
- **25918118** 11:50:59 base 0.07 gwei, 247 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xf0ef…1575](https://etherscan.io/tx/0xf0ef15f24a1c75cb5a0efd89d6c5c3b4a7c241d389bc6658aa524c8715931575))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xf0ef…1575](https://etherscan.io/tx/0xf0ef15f24a1c75cb5a0efd89d6c5c3b4a7c241d389bc6658aa524c8715931575))
- **25918119** 11:51:11 base 0.07 gwei, 268 txs, Titan (titanbuilder.xyz)
- **25918120** 11:51:23 base 0.08 gwei, 241 txs, Titan (titanbuilder.xyz)
- **25918121** 11:51:35 base 0.08 gwei, 226 txs, Titan (titanbuilder.xyz)
- **25918122** 11:51:47 base 0.08 gwei, 285 txs, BuilderNet
- **25918123** 11:51:59 base 0.08 gwei, 230 txs,  Quasar (quasar.win) 
- **25918124** 11:52:11 base 0.08 gwei, 251 txs, Titan (titanbuilder.xyz)
- **25918125** 11:52:23 base 0.08 gwei, 258 txs, Eureka (eurekabuilder.xyz)
- **25918126** 11:52:35 base 0.08 gwei, 204 txs,  Quasar (quasar.win) 
- **25918127** 11:52:47 base 0.08 gwei, 219 txs, Titan (titanbuilder.xyz)
- **25918128** 11:52:59 base 0.07 gwei, 276 txs,  Quasar (quasar.win) 
- **25918129** 11:53:11 base 0.07 gwei, 274 txs, Titan (titanbuilder.xyz)
- **25918130** 11:53:23 base 0.07 gwei, 164 txs, Titan (titanbuilder.xyz)
- **25918131** 11:53:35 base 0.07 gwei, 250 txs, Titan (titanbuilder.xyz)
  - JIT 2 episode(s), $263 of swaps bracketed, fees taken $0
- **25918132** 11:53:47 base 0.07 gwei, 188 txs, Eureka (eurekabuilder.xyz)
- **25918133** 11:53:59 base 0.07 gwei, 76 txs, 0xe556…1f58
- **25918134** 11:54:11 base 0.06 gwei, 298 txs, Titan (titanbuilder.xyz)
- **25918135** 11:54:23 base 0.07 gwei, 228 txs,  Quasar (quasar.win) 
- **25918136** 11:54:35 base 0.07 gwei, 160 txs, Nethermind v1.39.2
- **25918137** 11:54:47 base 0.06 gwei, 310 txs, Titan (titanbuilder.xyz)
- **25918138** 11:54:59 base 0.06 gwei, 218 txs,  Quasar (quasar.win) 
- **25918139** 11:55:11 base 0.06 gwei, 198 txs,  Quasar (quasar.win) 
- re-analysed blocks 25917839 to 25918139 at 12:00:02 UTC: 6837 priced swaps, 28 JIT episodes, 5 lending ops ≥$250k, exchange net $20.8M stables / $99k ETH
- **25918140** 11:55:23 base 0.06 gwei, 212 txs, Titan (titanbuilder.xyz)
- **25918141** 11:55:35 base 0.06 gwei, 207 txs, bombora.build 
- **25918142** 11:55:47 base 0.06 gwei, 225 txs, Titan (titanbuilder.xyz)
- **25918143** 11:55:59 base 0.07 gwei, 240 txs,  Quasar (quasar.win) 
- **25918144** 11:56:11 base 0.07 gwei, 190 txs, Titan (titanbuilder.xyz)
- **25918145** 11:56:23 base 0.07 gwei, 208 txs, Titan (titanbuilder.xyz)
- **25918146** 11:56:35 base 0.07 gwei, 261 txs, Eureka (eurekabuilder.xyz)
- **25918147** 11:56:47 base 0.07 gwei, 219 txs, Titan (titanbuilder.xyz)
- **25918148** 11:56:59 base 0.07 gwei, 237 txs,  Quasar (quasar.win) 
- **25918149** 11:57:11 base 0.07 gwei, 202 txs, Eureka (eurekabuilder.xyz)
- **25918150** 11:57:23 base 0.07 gwei, 199 txs,  Quasar (quasar.win) 
- **25918151** 11:57:35 base 0.07 gwei, 89 txs, 0x08a9…6eac
- **25918152** 11:57:47 base 0.06 gwei, 76 txs, Titan (titanbuilder.xyz)
- **25918153** 11:57:59 base 0.05 gwei, 369 txs, Titan (titanbuilder.xyz)
- **25918154** 11:58:11 base 0.06 gwei, 193 txs, Titan (titanbuilder.xyz)
- **25918155** 11:58:23 base 0.06 gwei, 174 txs, Titan (titanbuilder.xyz)
- **25918156** 11:58:35 base 0.06 gwei, 228 txs, Titan (titanbuilder.xyz)
- **25918157** 11:58:47 base 0.06 gwei, 221 txs, Titan (titanbuilder.xyz)
- **25918158** 11:58:59 base 0.06 gwei, 135 txs, BuilderNet
- **25918159** 11:59:11 base 0.06 gwei, 239 txs, Titan (titanbuilder.xyz)
- **25918160** 11:59:23 base 0.06 gwei, 149 txs, BuilderNet
- **25918161** 11:59:35 base 0.05 gwei, 108 txs, gethgo1.26.4linux
- **25918162** 11:59:47 base 0.05 gwei, 329 txs, Titan (titanbuilder.xyz)
  - transfer $440.8M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $440.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $106.5M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $106.5M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $27.5M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $27.5M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xa2b8…826c](https://etherscan.io/tx/0xa2b849d48753d69338d1252d7c4c5d9867f91c694f29882deb062235d033826c))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xa2b8…826c](https://etherscan.io/tx/0xa2b849d48753d69338d1252d7c4c5d9867f91c694f29882deb062235d033826c))
  - transfer $13.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.8M WBTC [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.7M WETH [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.7M WETH [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.7M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
  - transfer $13.7M USDC [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x32ec…67ab](https://etherscan.io/tx/0x32ecec4526762575d12ceaa2bb0da6e050c1cdbc4118dab017d06f1bce3667ab))
- **25918163** 11:59:59 base 0.05 gwei, 260 txs, BuilderNet
- re-analysed blocks 25917863 to 25918163 at 12:01:03 UTC: 6757 priced swaps, 25 JIT episodes, 6 lending ops ≥$250k, exchange net $17.6M stables / $-249k ETH
- **25918164** 12:00:11 base 0.05 gwei, 396 txs, Titan (titanbuilder.xyz)
- **25918165** 12:00:23 base 0.06 gwei, 233 txs, BuilderNet
- **25918166** 12:00:35 base 0.06 gwei, 458 txs,  Quasar (quasar.win) 
- **25918167** 12:00:47 base 0.06 gwei, 241 txs, Titan (titanbuilder.xyz)
- **25918168** 12:00:59 base 0.06 gwei, 218 txs, BuilderNet
  - transfer $7.2M USDC [hot wallet (day study, unidentified)](https://etherscan.io/address/0x05ff6964d21e5dae3b1010d5ae0465b3c450f381) → [0x2744…a22b](https://etherscan.io/address/0x2744dfd9898f0babbc570cc594bbbc84b487a22b) ([0x6c3d…222f](https://etherscan.io/tx/0x6c3d91e46c79da5de6263a06743601f4b033a0a09510a8d7c274ad164201222f))
- **25918169** 12:01:11 base 0.06 gwei, 329 txs,  Quasar (quasar.win) 
- **25918170** 12:01:23 base 0.07 gwei, 252 txs, Titan (titanbuilder.xyz)
- **25918171** 12:01:35 base 0.06 gwei, 216 txs, Titan (titanbuilder.xyz)
- **25918172** 12:01:47 base 0.06 gwei, 116 txs, gethgo1.26.4linux
- **25918173** 12:01:59 base 0.06 gwei, 276 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25917873 to 25918173 at 12:02:10 UTC: 6742 priced swaps, 19 JIT episodes, 6 lending ops ≥$250k, exchange net $11.6M stables / $-558k ETH
- **25918174** 12:02:11 base 0.06 gwei, 248 txs, Titan (titanbuilder.xyz)
- **25918175** 12:02:23 base 0.06 gwei, 226 txs, Titan (titanbuilder.xyz)
  - JIT 2 episode(s), $3910 of swaps bracketed, fees taken $0
- **25918176** 12:02:35 base 0.06 gwei, 242 txs, Titan (titanbuilder.xyz)
- **25918177** 12:02:47 base 0.06 gwei, 210 txs, 0x388c…9297
- **25918178** 12:02:59 base 0.06 gwei, 206 txs, BuilderNet
- **25918179** 12:03:11 base 0.06 gwei, 341 txs, Eureka (eurekabuilder.xyz)
- **25918180** 12:03:23 base 0.06 gwei, 287 txs, Titan (titanbuilder.xyz)
- **25918181** 12:03:35 base 0.06 gwei, 190 txs, Titan (titanbuilder.xyz)
- **25918182** 12:03:47 base 0.06 gwei, 250 txs, bombora.build 
  - JIT 3 episode(s), $120 of swaps bracketed, fees taken $0
- **25918183** 12:03:59 base 0.06 gwei, 242 txs, Titan (titanbuilder.xyz)
  - lending Aave v3 supply $1.0M USDT account [0x4d43…c672](https://etherscan.io/address/0x4d431856295413906075dd40266d83624e09c672) ([0xd676…c2fa](https://etherscan.io/tx/0xd676e3335d67baf681d6040b6e2e3122cd7ac814d3a59c17651019284081c2fa))
- re-analysed blocks 25917883 to 25918183 at 12:04:21 UTC: 6688 priced swaps, 23 JIT episodes, 7 lending ops ≥$250k, exchange net $3.1M stables / $-1.0M ETH
- **25918184** 12:04:11 base 0.06 gwei, 207 txs, BuilderNet
- **25918185** 12:04:23 base 0.06 gwei, 293 txs, Titan (titanbuilder.xyz)
- **25918186** 12:04:35 base 0.06 gwei, 319 txs, Titan (titanbuilder.xyz)
- **25918187** 12:04:47 base 0.06 gwei, 395 txs,  Quasar (quasar.win) 
- **25918188** 12:04:59 base 0.06 gwei, 249 txs,  Quasar (quasar.win) 
- **25918189** 12:05:11 base 0.06 gwei, 317 txs, BuilderNet
- **25918190** 12:05:23 base 0.07 gwei, 140 txs, BuilderNet
- **25918191** 12:05:35 base 0.06 gwei, 412 txs, Titan (titanbuilder.xyz)
  - swap $2.5M WETH → 0x622b…bf2d on uniswap_v2_like by [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) ([0x4141…a858](https://etherscan.io/tx/0x4141c0449ead1777e6a1dbaef6e4079f348711fd3019dbc9b3b8da144e70a858))
  - swap $2.5M 0x622b…bf2d → WETH on uniswap_v2_like by [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) ([0x4141…a858](https://etherscan.io/tx/0x4141c0449ead1777e6a1dbaef6e4079f348711fd3019dbc9b3b8da144e70a858))
- **25918192** 12:05:47 base 0.07 gwei, 266 txs, Titan (titanbuilder.xyz)
- **25918193** 12:05:59 base 0.07 gwei, 229 txs, Titan (titanbuilder.xyz)
- **25918194** 12:06:11 base 0.07 gwei, 313 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25917894 to 25918194 at 12:06:26 UTC: 6699 priced swaps, 23 JIT episodes, 7 lending ops ≥$250k, exchange net $3.5M stables / $-734k ETH
- **25918195** 12:06:23 base 0.07 gwei, 256 txs, Titan (titanbuilder.xyz)
- **25918196** 12:06:35 base 0.07 gwei, 285 txs, 0x345d…78ee
- **25918197** 12:06:47 base 0.07 gwei, 330 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $25 of swaps bracketed, fees taken $0
- **25918198** 12:06:59 base 0.07 gwei, 248 txs, Titan (titanbuilder.xyz)
- **25918199** 12:07:11 base 0.07 gwei, 209 txs, Titan (titanbuilder.xyz)
- **25918200** 12:07:23 base 0.07 gwei, 71 txs, Titan (titanbuilder.xyz)
- **25918201** 12:07:35 base 0.07 gwei, 354 txs, Titan (titanbuilder.xyz)
- **25918202** 12:07:47 base 0.07 gwei, 334 txs, Eureka (eurekabuilder.xyz)
- **25918203** 12:07:59 base 0.07 gwei, 196 txs, Titan (titanbuilder.xyz)
- **25918204** 12:08:11 base 0.07 gwei, 247 txs, Titan (titanbuilder.xyz)
- **25918205** 12:08:23 base 0.07 gwei, 256 txs,  Quasar (quasar.win) 
- re-analysed blocks 25918028 to 25918205 at 12:08:37 UTC: 6968 priced swaps, 24 JIT episodes, 7 lending ops ≥$250k, exchange net $5.6M stables / $-534k ETH
- **25918206** 12:08:35 base 0.07 gwei, 149 txs, BuilderNet
  - JIT 1 episode(s), $349 of swaps bracketed, fees taken $0
- **25918207** 12:08:47 base 0.07 gwei, 311 txs, BuilderNet
  - lending Aave v3 supply $1.2M wstETH account [0xf8f5…e912](https://etherscan.io/address/0xf8f59620f260583e833d43a1940e6d210d0ce912) ([0x3f20…d166](https://etherscan.io/tx/0x3f209443b4f59a1af4859a3340d12a0a41b481a4bf01134ec615adaf950ad166))
  - lending Aave v3 borrow $1.0M WETH account [0xf8f5…e912](https://etherscan.io/address/0xf8f59620f260583e833d43a1940e6d210d0ce912) ([0x3f20…d166](https://etherscan.io/tx/0x3f209443b4f59a1af4859a3340d12a0a41b481a4bf01134ec615adaf950ad166))
- **25918208** 12:08:59 base 0.07 gwei, 159 txs, Builder+ btcs.com | ethgas.com
- **25918209** 12:09:11 base 0.07 gwei, 192 txs, Titan (titanbuilder.xyz)
  - transfer $11.4M sUSDe [0xa711…6d69](https://etherscan.io/address/0xa711a3a64f2b2d7e05dc3f564d3862d7499c6d69) → [0xb221…dc61](https://etherscan.io/address/0xb22161a2222ae7008cb3c54f819025031b1bdc61) ([0x6e94…a609](https://etherscan.io/tx/0x6e94f243d8f5a82429b8f68570895300cc8d8748930705bc170ee5910f07a609))
- **25918210** 12:09:23 base 0.07 gwei, 310 txs, Titan (titanbuilder.xyz)
- **25918211** 12:09:35 base 0.07 gwei, 78 txs, Nethermind v1.39.3
- **25918212** 12:09:47 base 0.06 gwei, 141 txs, Titan (titanbuilder.xyz)
  - transfer $5.0M ETH [0x8d6e…8b59](https://etherscan.io/address/0x8d6ecbc74a448ed85a19d68d27be078fd4b88b59) → [0xef25…e815](https://etherscan.io/address/0xef25d6f7e6bf59f21cceeb8d5f78f9f59db7e815) ([0xcdaf…5630](https://etherscan.io/tx/0xcdaf1a32c101189a663997d8ef049345b3877976333fc33ea4f4aae60c735630))
- **25918213** 12:09:59 base 0.06 gwei, 406 txs, Titan (titanbuilder.xyz)
  - transfer $107.4M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) ([0x90fa…06d4](https://etherscan.io/tx/0x90fade6b63402923f658fdde6b32a210b81640cbbd27328f3507e4135c1206d4))
  - transfer $107.4M USDC [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x90fa…06d4](https://etherscan.io/tx/0x90fade6b63402923f658fdde6b32a210b81640cbbd27328f3507e4135c1206d4))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x4aec…9536](https://etherscan.io/tx/0x4aece014ae05115250f9d386eb768bf03a05e4deb3a2b65eb8441bde31439536))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x4aec…9536](https://etherscan.io/tx/0x4aece014ae05115250f9d386eb768bf03a05e4deb3a2b65eb8441bde31439536))
- **25918214** 12:10:11 base 0.07 gwei, 218 txs, Titan (titanbuilder.xyz)
- **25918215** 12:10:23 base 0.07 gwei, 203 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918215 at 12:10:39 UTC: 7444 priced swaps, 25 JIT episodes, 9 lending ops ≥$250k, exchange net $8.8M stables / $-540k ETH
- **25918216** 12:10:35 base 0.07 gwei, 266 txs, Titan (titanbuilder.xyz)
- **25918217** 12:10:47 base 0.07 gwei, 253 txs, Titan (titanbuilder.xyz)
  - transfer $11.4M sUSDe [0xb221…dc61](https://etherscan.io/address/0xb22161a2222ae7008cb3c54f819025031b1bdc61) → [0x31b7…b95a](https://etherscan.io/address/0x31b7d5a2b1ce1871dd642f6aecc0ef68d126b95a) ([0x932e…8a3e](https://etherscan.io/tx/0x932e78816646c1dbb925b1cf76c8649a0eb849d81a04714a4cb4dedf96448a3e))
- **25918218** 12:10:59 base 0.07 gwei, 324 txs,  Quasar (quasar.win) 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xf383…becc](https://etherscan.io/tx/0xf3838b61a0ff35d400529691649ce81eb5716143725dac7601978e3b0f87becc))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xf383…becc](https://etherscan.io/tx/0xf3838b61a0ff35d400529691649ce81eb5716143725dac7601978e3b0f87becc))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xa86f…e050](https://etherscan.io/tx/0xa86f6873467d807485c06f494058d0131a7555a4dbc1b73eba2010fe78b1e050))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xa86f…e050](https://etherscan.io/tx/0xa86f6873467d807485c06f494058d0131a7555a4dbc1b73eba2010fe78b1e050))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x0b0a…257e](https://etherscan.io/tx/0x0b0a89fe13bd11078986e46ece5bd5cc61fde8a6a8535010606dcd0d4a5c257e))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x0b0a…257e](https://etherscan.io/tx/0x0b0a89fe13bd11078986e46ece5bd5cc61fde8a6a8535010606dcd0d4a5c257e))
- **25918219** 12:11:11 base 0.07 gwei, 127 txs, besu 26.8.0
- **25918220** 12:11:23 base 0.06 gwei, 117 txs, Nethermind v1.39.3
- **25918221** 12:11:35 base 0.05 gwei, 179 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xd89d…7f78](https://etherscan.io/tx/0xd89d1f40d68fda5bc7421401187b134d5a4b8c7d8e1ed1dd0cd17c63c0ba7f78))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xd89d…7f78](https://etherscan.io/tx/0xd89d1f40d68fda5bc7421401187b134d5a4b8c7d8e1ed1dd0cd17c63c0ba7f78))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xaa98…6ffb](https://etherscan.io/tx/0xaa987caa52c1e73269da2f1ed80e850e2113dacbca2bd789aebc46401bab6ffb))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xaa98…6ffb](https://etherscan.io/tx/0xaa987caa52c1e73269da2f1ed80e850e2113dacbca2bd789aebc46401bab6ffb))
- **25918222** 12:11:47 base 0.05 gwei, 397 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x9bc4…c24e](https://etherscan.io/tx/0x9bc4bae30c9a3492d2f1eb73296298fd25fc872edeeac480968210405ff1c24e))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x9bc4…c24e](https://etherscan.io/tx/0x9bc4bae30c9a3492d2f1eb73296298fd25fc872edeeac480968210405ff1c24e))
- **25918223** 12:11:59 base 0.06 gwei, 210 txs, Titan (titanbuilder.xyz)
  - transfer $6.0M sUSDe [0x31b7…b95a](https://etherscan.io/address/0x31b7d5a2b1ce1871dd642f6aecc0ef68d126b95a) → [0x211c…e5d2](https://etherscan.io/address/0x211cc4dd073734da055fbf44a2b4667d5e5fe5d2) ([0xb635…f9ac](https://etherscan.io/tx/0xb635b559de6ff4a3c5620cf6cc7a82a32356c37a19f5900805d9f7e81678f9ac))
  - bridge OFT $6.0M sUSDe → eid 30383 ([0xb635…f9ac](https://etherscan.io/tx/0xb635b559de6ff4a3c5620cf6cc7a82a32356c37a19f5900805d9f7e81678f9ac))
  - JIT 3 episode(s), $420 of swaps bracketed, fees taken $0
- **25918224** 12:12:11 base 0.06 gwei, 246 txs, Titan (titanbuilder.xyz)
  - lending Aave v3 supply $1.0M wstETH account [0xf8f5…e912](https://etherscan.io/address/0xf8f59620f260583e833d43a1940e6d210d0ce912) ([0xf717…7a02](https://etherscan.io/tx/0xf7170ba1349552480043c2cf2549fecf440ff66812716a008e8b3fbfc47d7a02))
- **25918225** 12:12:23 base 0.06 gwei, 316 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918028 to 25918225 at 12:12:38 UTC: 7886 priced swaps, 28 JIT episodes, 11 lending ops ≥$250k, exchange net $5.7M stables / $-616k ETH
- **25918226** 12:12:35 base 0.07 gwei, 199 txs, BuilderNet
- **25918227** 12:12:47 base 0.06 gwei, 184 txs, BuilderNet
- **25918228** 12:12:59 base 0.06 gwei, 295 txs, Titan (titanbuilder.xyz)
- **25918229** 12:13:11 base 0.06 gwei, 356 txs, Titan (titanbuilder.xyz)
- **25918230** 12:13:23 base 0.07 gwei, 211 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x351e…bf80](https://etherscan.io/tx/0x351e4a75229489e6baa407bb9d1f8c3028b931a60085187a934bacd9bd73bf80))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x351e…bf80](https://etherscan.io/tx/0x351e4a75229489e6baa407bb9d1f8c3028b931a60085187a934bacd9bd73bf80))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xfade…8cb5](https://etherscan.io/tx/0xfadeaa5d26ae5fd9d7109d7c067610eb03c46424acbd49ce2dd29019f7368cb5))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xfade…8cb5](https://etherscan.io/tx/0xfadeaa5d26ae5fd9d7109d7c067610eb03c46424acbd49ce2dd29019f7368cb5))
- **25918231** 12:13:35 base 0.07 gwei, 186 txs, Titan (titanbuilder.xyz)
- **25918232** 12:13:47 base 0.06 gwei, 187 txs, BuilderNet
  - swap $2.2M USDS → USDT on uniswap_v4 by [0x63d7…b51d](https://etherscan.io/address/0x63d7325a767846c810276d09d032aa3b846ab51d) ([0xe6ba…6223](https://etherscan.io/tx/0xe6baa9974d31f32a4326fa79f54160490ec416199663d65b6da611648f9b6223))
- **25918233** 12:13:59 base 0.06 gwei, 76 txs, BuilderNet
- **25918234** 12:14:11 base 0.06 gwei, 352 txs, Titan (titanbuilder.xyz)
- **25918235** 12:14:23 base 0.06 gwei, 198 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918235 at 12:14:37 UTC: 8292 priced swaps, 28 JIT episodes, 12 lending ops ≥$250k, exchange net $6.4M stables / $-569k ETH
- **25918236** 12:14:35 base 0.06 gwei, 70 txs, BuilderNet
- **25918237** 12:14:47 base 0.06 gwei, 451 txs, Titan (titanbuilder.xyz)
- **25918238** 12:14:59 base 0.06 gwei, 218 txs, Titan (titanbuilder.xyz)
- **25918239** 12:15:11 base 0.06 gwei, 280 txs, Titan (titanbuilder.xyz)
- **25918240** 12:15:23 base 0.07 gwei, 266 txs, Titan (titanbuilder.xyz)
- **25918241** 12:15:35 base 0.07 gwei, 330 txs, Eureka (eurekabuilder.xyz)
- **25918242** 12:15:47 base 0.07 gwei, 226 txs, Titan (titanbuilder.xyz)
- **25918243** 12:15:59 base 0.07 gwei, 231 txs, Titan (titanbuilder.xyz)
- **25918244** 12:16:11 base 0.08 gwei, 244 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xff3f…c3a3](https://etherscan.io/tx/0xff3fa97eb7708de200e04be0ef7bd0cd1ca16055fc34da011db0cf679103c3a3))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xff3f…c3a3](https://etherscan.io/tx/0xff3fa97eb7708de200e04be0ef7bd0cd1ca16055fc34da011db0cf679103c3a3))
- **25918245** 12:16:23 base 0.08 gwei, 284 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918028 to 25918245 at 12:16:42 UTC: 8928 priced swaps, 28 JIT episodes, 13 lending ops ≥$250k, exchange net $6.1M stables / $-571k ETH
- **25918246** 12:16:35 base 0.09 gwei, 248 txs, Titan (titanbuilder.xyz)
- **25918247** 12:16:47 base 0.10 gwei, 126 txs, Titan (titanbuilder.xyz)
- **25918248** 12:16:59 base 0.10 gwei, 421 txs,  Quasar (quasar.win) 
- **25918249** 12:17:11 base 0.10 gwei, 124 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x626b…5e4e](https://etherscan.io/tx/0x626be59ef79a787510260289ff197d308444218247f6bc41097c5d5ca43c5e4e))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x626b…5e4e](https://etherscan.io/tx/0x626be59ef79a787510260289ff197d308444218247f6bc41097c5d5ca43c5e4e))
- **25918250** 12:17:23 base 0.10 gwei, 293 txs, BuilderNet
- **25918251** 12:17:35 base 0.11 gwei, 353 txs, Titan (titanbuilder.xyz)
- **25918252** 12:17:47 base 0.11 gwei, 409 txs,  Quasar (quasar.win) 
- **25918253** 12:17:59 base 0.12 gwei, 84 txs, Nethermind v1.37.1
- **25918254** 12:18:11 base 0.11 gwei, 388 txs, Titan (titanbuilder.xyz)
- **25918255** 12:18:23 base 0.11 gwei, 265 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x48e7…3e71](https://etherscan.io/tx/0x48e76f2a95b299a50b500fef292aec3d18c13275d8db0d039226523568a93e71))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x48e7…3e71](https://etherscan.io/tx/0x48e76f2a95b299a50b500fef292aec3d18c13275d8db0d039226523568a93e71))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x79b6…ef44](https://etherscan.io/tx/0x79b6e003c7875cd6b8f6a5d5a12185bc1f77923d0885d415fc58ad518bceef44))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x79b6…ef44](https://etherscan.io/tx/0x79b6e003c7875cd6b8f6a5d5a12185bc1f77923d0885d415fc58ad518bceef44))
- **25918256** 12:18:35 base 0.12 gwei, 198 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x1ce1…94c0](https://etherscan.io/tx/0x1ce14251154eaa92ad3afbf54ca108bcf95b91229973e29e3988bf4ccbe894c0))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x1ce1…94c0](https://etherscan.io/tx/0x1ce14251154eaa92ad3afbf54ca108bcf95b91229973e29e3988bf4ccbe894c0))
- re-analysed blocks 25918028 to 25918256 at 12:18:52 UTC: 9543 priced swaps, 28 JIT episodes, 14 lending ops ≥$250k, exchange net $6.1M stables / $375k ETH
- **25918257** 12:18:47 base 0.12 gwei, 114 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x53f3…b76c](https://etherscan.io/tx/0x53f35442939398107ff25290484902a29eb515aa7683724a7928f117e80bb76c))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x53f3…b76c](https://etherscan.io/tx/0x53f35442939398107ff25290484902a29eb515aa7683724a7928f117e80bb76c))
- **25918258** 12:18:59 base 0.12 gwei, 276 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x6afb…bbd4](https://etherscan.io/tx/0x6afb8db6c1a4d5f1ed76b7b8c9b0eb7fd0733844f3f0551c7500c02facb3bbd4))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x6afb…bbd4](https://etherscan.io/tx/0x6afb8db6c1a4d5f1ed76b7b8c9b0eb7fd0733844f3f0551c7500c02facb3bbd4))
- **25918259** 12:19:11 base 0.12 gwei, 151 txs, Titan (titanbuilder.xyz)
- **25918260** 12:19:23 base 0.12 gwei, 309 txs,  Quasar (quasar.win) 
- **25918261** 12:19:35 base 0.12 gwei, 258 txs, Titan (titanbuilder.xyz)
- **25918262** 12:19:47 base 0.13 gwei, 221 txs, BuilderNet
- **25918263** 12:19:59 base 0.13 gwei, 186 txs, Titan (titanbuilder.xyz)
- **25918264** 12:20:11 base 0.13 gwei, 265 txs, Titan (titanbuilder.xyz)
- **25918265** 12:20:23 base 0.14 gwei, 176 txs, BuilderNet
- **25918266** 12:20:35 base 0.14 gwei, 275 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918266 at 12:20:55 UTC: 10074 priced swaps, 28 JIT episodes, 14 lending ops ≥$250k, exchange net $5.2M stables / $1.2M ETH
- **25918267** 12:20:47 base 0.14 gwei, 200 txs, Titan (titanbuilder.xyz)
- **25918268** 12:20:59 base 0.14 gwei, 163 txs, 0xd73d…be4a
- **25918269** 12:21:11 base 0.13 gwei, 321 txs, Titan (titanbuilder.xyz)
- **25918270** 12:21:23 base 0.14 gwei, 136 txs, BuilderNet
- **25918271** 12:21:35 base 0.13 gwei, 291 txs,  Quasar (quasar.win) 
- **25918272** 12:21:47 base 0.14 gwei, 234 txs, Titan (titanbuilder.xyz)
- **25918273** 12:21:59 base 0.14 gwei, 280 txs, Eureka (eurekabuilder.xyz)
- **25918274** 12:22:11 base 0.14 gwei, 239 txs,  Quasar (quasar.win) 
  - transfer $17.7M stETH [0x889e…f9b1](https://etherscan.io/address/0x889edc2edab5f40e902b864ad4d7ade8e412f9b1) → [0xe76c…573a](https://etherscan.io/address/0xe76c52750019b80b43e36df30bf4060eb73f573a) ([0x314f…4de4](https://etherscan.io/tx/0x314f6a49de7906164617d8ecd026f17c72d8a88933097ef6d895beb11be04de4))
- **25918275** 12:22:23 base 0.14 gwei, 210 txs, Eureka (eurekabuilder.xyz)
  - transfer $40.1M USDT [Binance 14 (memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) → [Binance 16 (memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) ([0x8c8f…d27a](https://etherscan.io/tx/0x8c8f5b04f36764cd6ae9fab5ca4155de7fb43e6acf7c329968a0df316559d27a))
- **25918276** 12:22:35 base 0.14 gwei, 159 txs, BuilderNet
- **25918277** 12:22:47 base 0.15 gwei, 281 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918277 at 12:23:01 UTC: 10605 priced swaps, 28 JIT episodes, 14 lending ops ≥$250k, exchange net $3.9M stables / $1.8M ETH
- **25918278** 12:22:59 base 0.15 gwei, 260 txs, Eureka (eurekabuilder.xyz)
- **25918279** 12:23:11 base 0.15 gwei, 85 txs, BuilderNet
- **25918280** 12:23:23 base 0.14 gwei, 261 txs, Titan (titanbuilder.xyz)
- **25918281** 12:23:35 base 0.14 gwei, 327 txs, Eureka (eurekabuilder.xyz)
- **25918282** 12:23:47 base 0.16 gwei, 94 txs, Eureka (eurekabuilder.xyz)
- **25918283** 12:23:59 base 0.15 gwei, 288 txs, Titan (titanbuilder.xyz)
- **25918284** 12:24:11 base 0.15 gwei, 129 txs, BuilderNet
  - JIT 1 episode(s), $115 of swaps bracketed, fees taken $0
- **25918285** 12:24:23 base 0.14 gwei, 308 txs, Titan (titanbuilder.xyz)
- **25918286** 12:24:35 base 0.15 gwei, 65 txs, gethgo1.25.1linux
- **25918287** 12:24:47 base 0.13 gwei, 284 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x3469…452f](https://etherscan.io/tx/0x3469920abb89533567168bdfd27c4df1919389534f9e6ae127ceae9419ae452f))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x3469…452f](https://etherscan.io/tx/0x3469920abb89533567168bdfd27c4df1919389534f9e6ae127ceae9419ae452f))
- re-analysed blocks 25918028 to 25918287 at 12:25:02 UTC: 11128 priced swaps, 29 JIT episodes, 14 lending ops ≥$250k, exchange net $4.2M stables / $2.0M ETH
- **25918288** 12:24:59 base 0.14 gwei, 230 txs, Titan (titanbuilder.xyz)
- **25918289** 12:25:11 base 0.14 gwei, 278 txs, Titan (titanbuilder.xyz)
- **25918290** 12:25:23 base 0.14 gwei, 209 txs, Titan (titanbuilder.xyz)
- **25918291** 12:25:35 base 0.13 gwei, 239 txs, Titan (titanbuilder.xyz)
- **25918292** 12:25:47 base 0.14 gwei, 97 txs, Eureka (eurekabuilder.xyz)
- **25918293** 12:25:59 base 0.13 gwei, 419 txs, Titan (titanbuilder.xyz)
- **25918294** 12:26:11 base 0.13 gwei, 117 txs, BuilderNet
- **25918295** 12:26:23 base 0.13 gwei, 358 txs, Titan (titanbuilder.xyz)
- **25918296** 12:26:35 base 0.13 gwei, 218 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x2ccd…2544](https://etherscan.io/tx/0x2ccdffee6d59e80751d1052fcd0e16d36c740108f8304caad6776b99dd462544))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x2ccd…2544](https://etherscan.io/tx/0x2ccdffee6d59e80751d1052fcd0e16d36c740108f8304caad6776b99dd462544))
- **25918297** 12:26:47 base 0.13 gwei, 228 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918297 at 12:27:06 UTC: 11633 priced swaps, 29 JIT episodes, 17 lending ops ≥$250k, exchange net $5.4M stables / $2.4M ETH
- **25918298** 12:26:59 base 0.13 gwei, 358 txs, Eureka (eurekabuilder.xyz)
- **25918299** 12:27:11 base 0.13 gwei, 240 txs, Titan (titanbuilder.xyz)
- **25918300** 12:27:23 base 0.13 gwei, 224 txs, BuilderNet
- **25918301** 12:27:35 base 0.13 gwei, 230 txs, BuilderNet
- **25918302** 12:27:47 base 0.13 gwei, 445 txs, bombora.build 
- **25918303** 12:27:59 base 0.13 gwei, 257 txs, Titan (titanbuilder.xyz)
- **25918304** 12:28:11 base 0.13 gwei, 181 txs, BuilderNet
- **25918305** 12:28:23 base 0.13 gwei, 138 txs, ethgas-realtime-rpc
- **25918306** 12:28:35 base 0.12 gwei, 264 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xccb5…b0f9](https://etherscan.io/tx/0xccb53dd1da1a4fc5d5908b471081266b6ab3cb0570b0d23f4e500de0ca78b0f9))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xccb5…b0f9](https://etherscan.io/tx/0xccb53dd1da1a4fc5d5908b471081266b6ab3cb0570b0d23f4e500de0ca78b0f9))
- **25918307** 12:28:47 base 0.12 gwei, 233 txs, Eureka (eurekabuilder.xyz)
- **25918308** 12:28:59 base 0.12 gwei, 243 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918308 at 12:29:12 UTC: 12179 priced swaps, 29 JIT episodes, 17 lending ops ≥$250k, exchange net $7.2M stables / $2.3M ETH
- **25918309** 12:29:11 base 0.12 gwei, 197 txs, Titan (titanbuilder.xyz)
- **25918310** 12:29:23 base 0.11 gwei, 210 txs, Titan (titanbuilder.xyz)
- **25918311** 12:29:35 base 0.11 gwei, 204 txs, Titan (titanbuilder.xyz)
- **25918312** 12:29:47 base 0.11 gwei, 214 txs, Titan (titanbuilder.xyz)
- **25918313** 12:29:59 base 0.11 gwei, 161 txs, besu 26.5.0-RC2
- **25918314** 12:30:11 base 0.10 gwei, 363 txs, BuilderNet
- **25918315** 12:30:23 base 0.10 gwei, 384 txs, Titan (titanbuilder.xyz)
- **25918316** 12:30:35 base 0.11 gwei, 218 txs, beaverbuild.org
- **25918317** 12:30:47 base 0.10 gwei, 314 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x88fd…1af4](https://etherscan.io/tx/0x88fd29836217ed825083e34d5502d2db1a397dcbb35f4c894da739e5f8581af4))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x88fd…1af4](https://etherscan.io/tx/0x88fd29836217ed825083e34d5502d2db1a397dcbb35f4c894da739e5f8581af4))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x783f…34fe](https://etherscan.io/tx/0x783f6aa3f512f69a6a281a4027829882b8148f0f9c986f0cded25497944334fe))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x783f…34fe](https://etherscan.io/tx/0x783f6aa3f512f69a6a281a4027829882b8148f0f9c986f0cded25497944334fe))
- **25918318** 12:30:59 base 0.10 gwei, 188 txs, besu 26.7.1
- re-analysed blocks 25918028 to 25918318 at 12:31:19 UTC: 12572 priced swaps, 29 JIT episodes, 17 lending ops ≥$250k, exchange net $6.8M stables / $2.3M ETH
- **25918319** 12:31:11 base 0.09 gwei, 388 txs, Titan (titanbuilder.xyz)
- **25918320** 12:31:23 base 0.10 gwei, 110 txs, gethgo1.25.1linux
- **25918321** 12:31:35 base 0.09 gwei, 373 txs, BuilderNet
- **25918322** 12:31:47 base 0.09 gwei, 236 txs, BuilderNet
- **25918323** 12:31:59 base 0.09 gwei, 164 txs, BuilderNet
  - JIT 1 episode(s), $0 of swaps bracketed, fees taken $0
- **25918324** 12:32:11 base 0.09 gwei, 223 txs, BuilderNet
- **25918325** 12:32:23 base 0.09 gwei, 229 txs, Titan (titanbuilder.xyz)
- **25918326** 12:32:35 base 0.09 gwei, 392 txs, Nethermind v1.37.1
- **25918327** 12:32:47 base 0.09 gwei, 212 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $299 of swaps bracketed, fees taken $2
- **25918328** 12:32:59 base 0.10 gwei, 401 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918028 to 25918328 at 12:33:15 UTC: 13120 priced swaps, 31 JIT episodes, 18 lending ops ≥$250k, exchange net $6.1M stables / $2.1M ETH
- **25918329** 12:33:11 base 0.10 gwei, 309 txs, Titan (titanbuilder.xyz)
- **25918330** 12:33:23 base 0.10 gwei, 124 txs, Nethermind v1.39.3
- **25918331** 12:33:35 base 0.10 gwei, 373 txs, Titan (titanbuilder.xyz)
- **25918332** 12:33:47 base 0.10 gwei, 270 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xf1cf…3ac1](https://etherscan.io/tx/0xf1cffdd5f00c7ee660c6b1e5228f8d55c91c6e981814b67bfcd5f759150c3ac1))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xf1cf…3ac1](https://etherscan.io/tx/0xf1cffdd5f00c7ee660c6b1e5228f8d55c91c6e981814b67bfcd5f759150c3ac1))
- **25918333** 12:33:59 base 0.10 gwei, 262 txs,  Quasar (quasar.win) 
- **25918334** 12:34:11 base 0.10 gwei, 98 txs, Bitget(https://www.bitget.com/)
- **25918335** 12:34:23 base 0.09 gwei, 348 txs, Titan (titanbuilder.xyz)
- **25918336** 12:34:35 base 0.10 gwei, 450 txs,  Quasar (quasar.win) 
- **25918337** 12:34:47 base 0.10 gwei, 295 txs, Titan (titanbuilder.xyz)
- **25918338** 12:34:59 base 0.09 gwei, 211 txs,  Quasar (quasar.win) 
- **25918339** 12:35:11 base 0.09 gwei, 116 txs, Nethermind v1.35.3
- re-analysed blocks 25918039 to 25918339 at 12:35:25 UTC: 13089 priced swaps, 30 JIT episodes, 17 lending ops ≥$250k, exchange net $6.2M stables / $2.2M ETH
- **25918340** 12:35:23 base 0.08 gwei, 302 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x7e29…c918](https://etherscan.io/tx/0x7e29d8d60fe81db55dc89fe25cabd579ec587972b4e484fb0549d6f7d0e8c918))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x7e29…c918](https://etherscan.io/tx/0x7e29d8d60fe81db55dc89fe25cabd579ec587972b4e484fb0549d6f7d0e8c918))
- **25918341** 12:35:35 base 0.09 gwei, 109 txs, builder.ultrasound.money
- **25918342** 12:35:47 base 0.08 gwei, 340 txs, BuilderNet
- **25918343** 12:35:59 base 0.09 gwei, 197 txs, bombora.build 
- **25918344** 12:36:11 base 0.09 gwei, 229 txs, BuilderNet
- **25918345** 12:36:23 base 0.09 gwei, 261 txs, Titan (titanbuilder.xyz)
- **25918346** 12:36:35 base 0.09 gwei, 273 txs, Titan (titanbuilder.xyz)
- **25918347** 12:36:47 base 0.09 gwei, 55 txs, gethgo1.25.12linux
- **25918348** 12:36:59 base 0.08 gwei, 467 txs, BuilderNet
- **25918349** 12:37:11 base 0.08 gwei, 309 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918049 to 25918349 at 12:37:33 UTC: 13151 priced swaps, 27 JIT episodes, 17 lending ops ≥$250k, exchange net $5.8M stables / $2.0M ETH
- **25918350** 12:37:23 base 0.08 gwei, 249 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $0 of swaps bracketed, fees taken $0
- **25918351** 12:37:35 base 0.08 gwei, 163 txs, boba-builder.com
- **25918352** 12:37:47 base 0.08 gwei, 285 txs, BuilderNet
- **25918353** 12:37:59 base 0.08 gwei, 133 txs, Titan (titanbuilder.xyz)
- **25918354** 12:38:11 base 0.08 gwei, 460 txs, Titan (titanbuilder.xyz)
- **25918355** 12:38:23 base 0.08 gwei, 225 txs, Eureka (eurekabuilder.xyz)
- **25918356** 12:38:35 base 0.08 gwei, 289 txs, Titan (titanbuilder.xyz)
- **25918357** 12:38:47 base 0.08 gwei, 187 txs, Titan (titanbuilder.xyz)
- **25918358** 12:38:59 base 0.08 gwei, 279 txs,  Quasar (quasar.win) 
- **25918359** 12:39:11 base 0.08 gwei, 285 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918059 to 25918359 at 12:39:26 UTC: 13354 priced swaps, 28 JIT episodes, 17 lending ops ≥$250k, exchange net $6.3M stables / $2.0M ETH
- **25918360** 12:39:23 base 0.07 gwei, 234 txs, Titan (titanbuilder.xyz)
- **25918361** 12:39:35 base 0.07 gwei, 85 txs, gethgo1.25.12linux
- **25918362** 12:39:47 base 0.06 gwei, 322 txs, Titan (titanbuilder.xyz)
  - transfer $440.8M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $440.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $106.2M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $106.2M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $27.5M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $27.5M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.8M WBTC [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.7M WETH [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.7M WETH [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.7M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
  - transfer $13.7M USDC [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0xc1b2…7b19](https://etherscan.io/tx/0xc1b20f69a3368085001ea095effc28b8e050be7af52aa87bd020964cc4007b19))
- **25918363** 12:39:59 base 0.07 gwei, 198 txs, Titan (titanbuilder.xyz)
- **25918364** 12:40:11 base 0.07 gwei, 276 txs, Titan (titanbuilder.xyz)
- **25918365** 12:40:23 base 0.07 gwei, 252 txs, Titan (titanbuilder.xyz)
- **25918366** 12:40:35 base 0.07 gwei, 363 txs, Titan (titanbuilder.xyz)
- **25918367** 12:40:47 base 0.07 gwei, 143 txs, BuilderNet
  - JIT 1 episode(s), $976 of swaps bracketed, fees taken $0
- **25918368** 12:40:59 base 0.07 gwei, 225 txs, BuilderNet
- **25918369** 12:41:11 base 0.07 gwei, 481 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918069 to 25918369 at 12:41:34 UTC: 13439 priced swaps, 29 JIT episodes, 18 lending ops ≥$250k, exchange net $6.4M stables / $2.1M ETH
- **25918370** 12:41:23 base 0.07 gwei, 169 txs, besu 26.8.1
- **25918371** 12:41:35 base 0.07 gwei, 99 txs, BuilderNet
  - transfer $80.9M WBTC [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) → [0x0000…e69d](https://etherscan.io/address/0x0000000000be226afde21672a5e4adc45692e69d) ([0x261c…067d](https://etherscan.io/tx/0x261cbff0dfe8dfafeee319753ecd1fba09614700eba611bf5366a8e724d5067d))
  - transfer $80.9M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0000…e69d](https://etherscan.io/address/0x0000000000be226afde21672a5e4adc45692e69d) ([0x261c…067d](https://etherscan.io/tx/0x261cbff0dfe8dfafeee319753ecd1fba09614700eba611bf5366a8e724d5067d))
  - transfer $80.9M WBTC [0x0000…e69d](https://etherscan.io/address/0x0000000000be226afde21672a5e4adc45692e69d) → [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) ([0x261c…067d](https://etherscan.io/tx/0x261cbff0dfe8dfafeee319753ecd1fba09614700eba611bf5366a8e724d5067d))
  - transfer $80.9M WBTC [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) → [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) ([0x261c…067d](https://etherscan.io/tx/0x261cbff0dfe8dfafeee319753ecd1fba09614700eba611bf5366a8e724d5067d))
  - transfer $80.9M WBTC [0x0000…e69d](https://etherscan.io/address/0x0000000000be226afde21672a5e4adc45692e69d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x261c…067d](https://etherscan.io/tx/0x261cbff0dfe8dfafeee319753ecd1fba09614700eba611bf5366a8e724d5067d))
  - lending Aave v3 supply $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x1a62…1eb9](https://etherscan.io/tx/0x1a62db3938cd349663a5d6ac4894582746199c629b757deef33a7826a9c51eb9))
  - lending Aave v3 withdraw $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x45b7…b7c2](https://etherscan.io/tx/0x45b7e9bab8e9ea5fd196cef98347c93d9bc98cae179a4f86dc1130cd2953b7c2))
  - JIT 1 episode(s), $22k of swaps bracketed, fees taken $2
- **25918372** 12:41:47 base 0.07 gwei, 459 txs, Titan (titanbuilder.xyz)
- **25918373** 12:42:11 base 0.07 gwei, 447 txs,  Quasar (quasar.win) 
- **25918374** 12:42:23 base 0.08 gwei, 254 txs, Titan (titanbuilder.xyz)
- **25918375** 12:42:35 base 0.08 gwei, 259 txs, Titan (titanbuilder.xyz)
- **25918376** 12:42:47 base 0.08 gwei, 247 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $943 of swaps bracketed, fees taken $10
- **25918377** 12:42:59 base 0.09 gwei, 268 txs,  Quasar (quasar.win) 
- **25918378** 12:43:11 base 0.08 gwei, 286 txs, Titan (titanbuilder.xyz)
- **25918379** 12:43:23 base 0.08 gwei, 211 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $1346 of swaps bracketed, fees taken $0
- re-analysed blocks 25918079 to 25918379 at 12:43:43 UTC: 13495 priced swaps, 32 JIT episodes, 19 lending ops ≥$250k, exchange net $-5.0M stables / $2.2M ETH
- **25918380** 12:43:35 base 0.09 gwei, 285 txs,  Quasar (quasar.win) 
- **25918381** 12:43:47 base 0.09 gwei, 265 txs,  Quasar (quasar.win) 
- **25918382** 12:43:59 base 0.09 gwei, 235 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x26d8…0e31](https://etherscan.io/tx/0x26d863d814b01f6ba35375c3b1b3f049c12d03662d2331e6f54fb8534ea80e31))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x26d8…0e31](https://etherscan.io/tx/0x26d863d814b01f6ba35375c3b1b3f049c12d03662d2331e6f54fb8534ea80e31))
- **25918383** 12:44:11 base 0.09 gwei, 166 txs, Titan (titanbuilder.xyz)
- **25918384** 12:44:23 base 0.09 gwei, 151 txs, 0x388c…9297
- **25918385** 12:44:35 base 0.08 gwei, 354 txs, Titan (titanbuilder.xyz)
- **25918386** 12:44:47 base 0.09 gwei, 246 txs, Eureka (eurekabuilder.xyz)
- **25918387** 12:44:59 base 0.09 gwei, 49 txs, gethgo1.26.4linux
- **25918388** 12:45:11 base 0.08 gwei, 325 txs, BuilderNet
  - JIT 1 episode(s), $243 of swaps bracketed, fees taken $0
- **25918389** 12:45:23 base 0.09 gwei, 216 txs, bombora.build 
- **25918390** 12:45:35 base 0.08 gwei, 246 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918090 to 25918390 at 12:45:50 UTC: 13320 priced swaps, 31 JIT episodes, 19 lending ops ≥$250k, exchange net $-3.4M stables / $2.1M ETH
- **25918391** 12:45:47 base 0.08 gwei, 215 txs, Titan (titanbuilder.xyz)
- **25918392** 12:45:59 base 0.08 gwei, 228 txs,  Quasar (quasar.win) 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x038b…9d83](https://etherscan.io/tx/0x038ba39dfe22159c192a160ac00d9ad4b1418236c2a0b53f97609cb3bc329d83))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x038b…9d83](https://etherscan.io/tx/0x038ba39dfe22159c192a160ac00d9ad4b1418236c2a0b53f97609cb3bc329d83))
- **25918393** 12:46:11 base 0.08 gwei, 271 txs, Titan (titanbuilder.xyz)
  - JIT 4 episode(s), $0 of swaps bracketed, fees taken $0
- **25918394** 12:46:23 base 0.09 gwei, 311 txs, Eureka (eurekabuilder.xyz)
- **25918395** 12:46:35 base 0.09 gwei, 130 txs, Nethermind v1.39.3
- **25918396** 12:46:47 base 0.08 gwei, 368 txs, Titan (titanbuilder.xyz)
- **25918397** 12:46:59 base 0.09 gwei, 101 txs, BuilderNet
- **25918398** 12:47:11 base 0.08 gwei, 382 txs, Titan (titanbuilder.xyz)
- **25918399** 12:47:23 base 0.09 gwei, 219 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $299 of swaps bracketed, fees taken $3
- **25918400** 12:47:35 base 0.09 gwei, 394 txs,  Quasar (quasar.win) 
- re-analysed blocks 25918100 to 25918400 at 12:47:56 UTC: 13134 priced swaps, 33 JIT episodes, 19 lending ops ≥$250k, exchange net $-3.8M stables / $2.0M ETH
- **25918401** 12:47:47 base 0.09 gwei, 189 txs, boba-builder.com
- **25918402** 12:47:59 base 0.08 gwei, 308 txs, bombora.build 
- **25918403** 12:48:11 base 0.08 gwei, 449 txs, Titan (titanbuilder.xyz)
- **25918404** 12:48:23 base 0.09 gwei, 77 txs, BuilderNet
- **25918405** 12:48:35 base 0.08 gwei, 427 txs, Titan (titanbuilder.xyz)
- **25918406** 12:48:47 base 0.08 gwei, 149 txs, Nethermind v1.38.1
- **25918407** 12:48:59 base 0.08 gwei, 185 txs, 0xe940…4a3c
- **25918408** 12:49:11 base 0.07 gwei, 293 txs, Builder+ btcs.com | ethgas.com
- **25918409** 12:49:23 base 0.08 gwei, 409 txs, Titan (titanbuilder.xyz)
  - transfer $107.2M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) ([0xc037…ee54](https://etherscan.io/tx/0xc03748d3af2696a6055ea391fda63c9c77e480c6c79fc802ebcb55ace6ddee54))
  - transfer $107.2M USDC [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc037…ee54](https://etherscan.io/tx/0xc03748d3af2696a6055ea391fda63c9c77e480c6c79fc802ebcb55ace6ddee54))
- **25918410** 12:49:35 base 0.08 gwei, 145 txs, Titan (titanbuilder.xyz)
  - lending Aave v3 supply $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xfb17…7b37](https://etherscan.io/tx/0xfb1789dba534d9cc106c49f50dda4964661e15bdddd21de59e691ad968fd7b37))
  - lending Aave v3 borrow $1.3M USDC account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xfb17…7b37](https://etherscan.io/tx/0xfb1789dba534d9cc106c49f50dda4964661e15bdddd21de59e691ad968fd7b37))
  - lending Aave v3 repay $1.3M USDC account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xbb57…bd5b](https://etherscan.io/tx/0xbb575ee19af9283b14bc514eb3d3299325d89e120d601d236cce54e90950bd5b))
  - lending Aave v3 withdraw $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xbb57…bd5b](https://etherscan.io/tx/0xbb575ee19af9283b14bc514eb3d3299325d89e120d601d236cce54e90950bd5b))
  - JIT 1 episode(s), $50k of swaps bracketed, fees taken $0
- re-analysed blocks 25918110 to 25918410 at 12:49:52 UTC: 13107 priced swaps, 30 JIT episodes, 19 lending ops ≥$250k, exchange net $-3.4M stables / $2.1M ETH
- **25918411** 12:49:47 base 0.08 gwei, 392 txs, Titan (titanbuilder.xyz)
- **25918412** 12:49:59 base 0.08 gwei, 167 txs, 0xe940…4a3c
- **25918413** 12:50:11 base 0.08 gwei, 182 txs, 0xa559…8a15
- **25918414** 12:50:23 base 0.07 gwei, 314 txs, BuilderNet
- **25918415** 12:50:35 base 0.08 gwei, 416 txs, Titan (titanbuilder.xyz)
- **25918416** 12:50:47 base 0.09 gwei, 197 txs, Titan (titanbuilder.xyz)
- **25918417** 12:50:59 base 0.08 gwei, 218 txs, Titan (titanbuilder.xyz)
- **25918418** 12:51:11 base 0.08 gwei, 207 txs, BuilderNet
- **25918419** 12:51:23 base 0.08 gwei, 416 txs, Eureka (eurekabuilder.xyz)
- **25918420** 12:51:35 base 0.08 gwei, 66 txs, reth/v2.5.2/linux
- re-analysed blocks 25918120 to 25918420 at 12:51:55 UTC: 13197 priced swaps, 27 JIT episodes, 19 lending ops ≥$250k, exchange net $-4.7M stables / $2.0M ETH
- **25918421** 12:51:47 base 0.07 gwei, 110 txs, gethgo1.25.12linux
- **25918422** 12:51:59 base 0.07 gwei, 416 txs, Titan (titanbuilder.xyz)
- **25918423** 12:52:11 base 0.07 gwei, 327 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $2141 of swaps bracketed, fees taken $0
- **25918424** 12:52:23 base 0.07 gwei, 290 txs, bombora.build 
- **25918425** 12:52:35 base 0.07 gwei, 310 txs, BuilderNet
- **25918426** 12:52:47 base 0.07 gwei, 112 txs, gethgo1.26.4linux
- **25918427** 12:52:59 base 0.06 gwei, 152 txs, gethgo1.25.10linux
- **25918428** 12:53:11 base 0.06 gwei, 127 txs, gethgo1.25.10linux
- **25918429** 12:53:23 base 0.05 gwei, 329 txs, Titan (titanbuilder.xyz)
  - transfer $25.1M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) ([0xaad5…69c3](https://etherscan.io/tx/0xaad5846efd195c92f3d9d6f9c311193e66d5548637f596a9932219f2f38369c3))
  - transfer $25.1M WETH [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xaad5…69c3](https://etherscan.io/tx/0xaad5846efd195c92f3d9d6f9c311193e66d5548637f596a9932219f2f38369c3))
- **25918430** 12:53:35 base 0.06 gwei, 332 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x6663…109d](https://etherscan.io/tx/0x66631101b8e7e59725fa789e7fc2946c5729eb58bb7078a4196f539802c7109d))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x6663…109d](https://etherscan.io/tx/0x66631101b8e7e59725fa789e7fc2946c5729eb58bb7078a4196f539802c7109d))
- re-analysed blocks 25918130 to 25918430 at 12:53:56 UTC: 13239 priced swaps, 28 JIT episodes, 18 lending ops ≥$250k, exchange net $-9.7M stables / $2.0M ETH
- **25918431** 12:53:47 base 0.07 gwei, 198 txs, BuilderNet
- **25918432** 12:53:59 base 0.06 gwei, 119 txs, BuilderNet
- **25918433** 12:54:11 base 0.06 gwei, 460 txs, Titan (titanbuilder.xyz)
- **25918434** 12:54:23 base 0.07 gwei, 76 txs, Titan (titanbuilder.xyz)
- **25918435** 12:54:35 base 0.06 gwei, 406 txs, Titan (titanbuilder.xyz)
- **25918436** 12:54:47 base 0.07 gwei, 277 txs, Titan (titanbuilder.xyz)
  - transfer $107.2M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) ([0x7c8d…48d5](https://etherscan.io/tx/0x7c8d00d2a8c99200a1e59951bf4ae0f25ffbb1b9f6f113f642ff18d77ff948d5))
  - transfer $107.2M USDC [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x7c8d…48d5](https://etherscan.io/tx/0x7c8d00d2a8c99200a1e59951bf4ae0f25ffbb1b9f6f113f642ff18d77ff948d5))
- **25918437** 12:54:59 base 0.07 gwei, 180 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xec27…6455](https://etherscan.io/tx/0xec27f39add3fc80bc886170e615ccb662d82a18e46764c81b7f95ad9a36c6455))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xec27…6455](https://etherscan.io/tx/0xec27f39add3fc80bc886170e615ccb662d82a18e46764c81b7f95ad9a36c6455))
- **25918438** 12:55:11 base 0.07 gwei, 233 txs, Titan (titanbuilder.xyz)
- **25918439** 12:55:23 base 0.07 gwei, 326 txs, BuilderNet
- **25918440** 12:55:35 base 0.07 gwei, 265 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918140 to 25918440 at 12:55:56 UTC: 13365 priced swaps, 26 JIT episodes, 18 lending ops ≥$250k, exchange net $-12.0M stables / $2.1M ETH
- **25918441** 12:55:47 base 0.07 gwei, 217 txs, Titan (titanbuilder.xyz)
- **25918442** 12:55:59 base 0.08 gwei, 156 txs, Titan (titanbuilder.xyz)
- **25918443** 12:56:11 base 0.07 gwei, 295 txs, Eureka (eurekabuilder.xyz)
- **25918444** 12:56:23 base 0.08 gwei, 192 txs, Titan (titanbuilder.xyz)
- **25918445** 12:56:35 base 0.08 gwei, 361 txs,  Quasar (quasar.win) 
- **25918446** 12:56:47 base 0.08 gwei, 202 txs, Titan (titanbuilder.xyz)
- **25918447** 12:56:59 base 0.08 gwei, 141 txs, Titan (titanbuilder.xyz)
- **25918448** 12:57:11 base 0.08 gwei, 297 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $167 of swaps bracketed, fees taken $1
- **25918449** 12:57:23 base 0.09 gwei, 201 txs, Titan (titanbuilder.xyz)
- **25918450** 12:57:35 base 0.08 gwei, 278 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918150 to 25918450 at 12:57:55 UTC: 13491 priced swaps, 27 JIT episodes, 17 lending ops ≥$250k, exchange net $-11.9M stables / $2.0M ETH
- **25918451** 12:57:47 base 0.08 gwei, 218 txs, Titan (titanbuilder.xyz)
- **25918452** 12:57:59 base 0.09 gwei, 175 txs, Titan (titanbuilder.xyz)
- **25918453** 12:58:11 base 0.09 gwei, 212 txs, bombora.build 
- **25918454** 12:58:23 base 0.09 gwei, 233 txs, Titan (titanbuilder.xyz)
- **25918455** 12:58:35 base 0.09 gwei, 354 txs, Titan (titanbuilder.xyz)
- **25918456** 12:58:47 base 0.09 gwei, 184 txs, Titan (titanbuilder.xyz)
- **25918457** 12:58:59 base 0.09 gwei, 276 txs,  Quasar (quasar.win) 
- **25918458** 12:59:11 base 0.08 gwei, 75 txs, BuilderNet
  - JIT 1 episode(s), $4833 of swaps bracketed, fees taken $0
- **25918459** 12:59:23 base 0.08 gwei, 323 txs, Titan (titanbuilder.xyz)
- **25918460** 12:59:35 base 0.08 gwei, 299 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918160 to 25918460 at 12:59:52 UTC: 13491 priced swaps, 28 JIT episodes, 17 lending ops ≥$250k, exchange net $-9.8M stables / $2.4M ETH
- **25918461** 12:59:47 base 0.08 gwei, 185 txs, Eureka (eurekabuilder.xyz)
- **25918462** 12:59:59 base 0.08 gwei, 238 txs,  Quasar (quasar.win) 
  - JIT 1 episode(s), $97 of swaps bracketed, fees taken $0
- **25918463** 13:00:11 base 0.07 gwei, 469 txs, Titan (titanbuilder.xyz)
- **25918464** 13:00:23 base 0.08 gwei, 283 txs, Eureka (eurekabuilder.xyz)
- **25918465** 13:00:35 base 0.08 gwei, 223 txs, bombora.build 
- **25918466** 13:00:47 base 0.08 gwei, 302 txs, bombora.build 
- **25918467** 13:00:59 base 0.08 gwei, 366 txs,  Quasar (quasar.win) 
- **25918468** 13:01:11 base 0.08 gwei, 254 txs, Titan (titanbuilder.xyz)
- **25918469** 13:01:23 base 0.07 gwei, 225 txs, Titan (titanbuilder.xyz)
- **25918470** 13:01:35 base 0.07 gwei, 398 txs,  Quasar (quasar.win) 
- **25918471** 13:01:47 base 0.07 gwei, 218 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918171 to 25918471 at 13:02:05 UTC: 13440 priced swaps, 29 JIT episodes, 16 lending ops ≥$250k, exchange net $-1.2M stables / $2.6M ETH
- **25918472** 13:01:59 base 0.07 gwei, 322 txs, Titan (titanbuilder.xyz)
- **25918473** 13:02:11 base 0.07 gwei, 181 txs, Titan (titanbuilder.xyz)
- **25918474** 13:02:23 base 0.07 gwei, 402 txs, Eureka (eurekabuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x4f66…5e8d](https://etherscan.io/tx/0x4f6610749130c123c704d520fa5ccf8d56035d9820a3b53d245c4a1818235e8d))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x4f66…5e8d](https://etherscan.io/tx/0x4f6610749130c123c704d520fa5ccf8d56035d9820a3b53d245c4a1818235e8d))
- **25918475** 13:02:35 base 0.07 gwei, 284 txs, Titan (titanbuilder.xyz)
- **25918476** 13:02:47 base 0.07 gwei, 171 txs, Titan (titanbuilder.xyz)
- **25918477** 13:02:59 base 0.07 gwei, 220 txs, Titan (titanbuilder.xyz)
- **25918478** 13:03:11 base 0.07 gwei, 228 txs, Titan (titanbuilder.xyz)
- **25918479** 13:03:23 base 0.07 gwei, 232 txs, Titan (titanbuilder.xyz)
- **25918480** 13:03:35 base 0.06 gwei, 208 txs, Titan (titanbuilder.xyz)
- **25918481** 13:03:47 base 0.06 gwei, 401 txs, bombora.build 
- re-analysed blocks 25918181 to 25918481 at 13:04:08 UTC: 13503 priced swaps, 27 JIT episodes, 17 lending ops ≥$250k, exchange net $-4.6M stables / $2.8M ETH
- **25918482** 13:03:59 base 0.06 gwei, 335 txs, Titan (titanbuilder.xyz)
- **25918483** 13:04:11 base 0.06 gwei, 261 txs, Titan (titanbuilder.xyz)
- **25918484** 13:04:23 base 0.06 gwei, 261 txs, bombora.build 
- **25918485** 13:04:35 base 0.06 gwei, 245 txs, bombora.build 
- **25918486** 13:04:47 base 0.06 gwei, 190 txs, ethgas-realtime-rpc
- **25918487** 13:04:59 base 0.06 gwei, 389 txs, Titan (titanbuilder.xyz)
- **25918488** 13:05:11 base 0.06 gwei, 324 txs, Titan (titanbuilder.xyz)
- **25918489** 13:05:23 base 0.06 gwei, 303 txs, Titan (titanbuilder.xyz)
- **25918490** 13:05:35 base 0.06 gwei, 318 txs, bombora.build 
- **25918491** 13:05:47 base 0.06 gwei, 255 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918191 to 25918491 at 13:06:04 UTC: 13552 priced swaps, 24 JIT episodes, 17 lending ops ≥$250k, exchange net $-4.8M stables / $3.1M ETH
- **25918492** 13:05:59 base 0.06 gwei, 179 txs, besu 26.8.1
- **25918493** 13:06:11 base 0.06 gwei, 389 txs, Titan (titanbuilder.xyz)
- **25918494** 13:06:23 base 0.07 gwei, 213 txs, Titan (titanbuilder.xyz)
- **25918495** 13:06:35 base 0.07 gwei, 185 txs, BuilderNet
- **25918496** 13:06:47 base 0.06 gwei, 176 txs, BuilderNet
- **25918497** 13:06:59 base 0.07 gwei, 170 txs, BuilderNet
- **25918498** 13:07:11 base 0.06 gwei, 705 txs, Eureka (eurekabuilder.xyz)
- **25918499** 13:07:23 base 0.07 gwei, 94 txs, Titan (titanbuilder.xyz)
- **25918500** 13:07:35 base 0.06 gwei, 431 txs, Titan (titanbuilder.xyz)
- **25918501** 13:07:47 base 0.07 gwei, 91 txs, BuilderNet
- re-analysed blocks 25918201 to 25918501 at 13:08:08 UTC: 13613 priced swaps, 23 JIT episodes, 18 lending ops ≥$250k, exchange net $-6.8M stables / $2.9M ETH
- **25918502** 13:07:59 base 0.06 gwei, 421 txs, Titan (titanbuilder.xyz)
- **25918503** 13:08:11 base 0.06 gwei, 258 txs, BuilderNet
- **25918504** 13:08:23 base 0.07 gwei, 328 txs, Titan (titanbuilder.xyz)
- **25918505** 13:08:35 base 0.07 gwei, 383 txs,  Quasar (quasar.win) 
- **25918506** 13:08:47 base 0.07 gwei, 256 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xc800…8098](https://etherscan.io/tx/0xc8005c1a7e33396237d7d8a4cfe91b5d158daa53c90b3c84992bc45a89d48098))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc800…8098](https://etherscan.io/tx/0xc8005c1a7e33396237d7d8a4cfe91b5d158daa53c90b3c84992bc45a89d48098))
- **25918507** 13:08:59 base 0.07 gwei, 211 txs,  Quasar (quasar.win) 
- **25918508** 13:09:11 base 0.06 gwei, 289 txs,  Quasar (quasar.win) 
- **25918509** 13:09:23 base 0.06 gwei, 261 txs, Eureka (eurekabuilder.xyz)
- **25918510** 13:09:35 base 0.06 gwei, 264 txs, Titan (titanbuilder.xyz)
- **25918511** 13:09:47 base 0.06 gwei, 184 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918211 to 25918511 at 13:10:04 UTC: 13690 priced swaps, 22 JIT episodes, 20 lending ops ≥$250k, exchange net $-10.0M stables / $2.9M ETH
- **25918512** 13:09:59 base 0.06 gwei, 202 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $0 of swaps bracketed, fees taken $0
- **25918513** 13:10:11 base 0.06 gwei, 236 txs, Builder+ www.btcs.com/builder
  - JIT 1 episode(s), $192 of swaps bracketed, fees taken $1
- **25918514** 13:10:23 base 0.06 gwei, 306 txs,  Quasar (quasar.win) 
- **25918515** 13:10:35 base 0.06 gwei, 251 txs, Titan (titanbuilder.xyz)
- **25918516** 13:10:47 base 0.07 gwei, 240 txs, bombora.build 
- **25918517** 13:10:59 base 0.06 gwei, 303 txs,  Quasar (quasar.win) 
- **25918518** 13:11:11 base 0.06 gwei, 272 txs, Eureka (eurekabuilder.xyz)
- **25918519** 13:11:23 base 0.06 gwei, 81 txs, Nethermind v1.38.1
- **25918520** 13:11:35 base 0.06 gwei, 318 txs, Eureka (eurekabuilder.xyz)
  - transfer $107.2M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x7966…ee94](https://etherscan.io/address/0x7966319bab61f7d6473a64277897885893c2ee94) ([0xfb7d…1818](https://etherscan.io/tx/0xfb7de02d97d4b5348ad0033c8e568cf3b5baba0148b315a1d0f82affaded1818))
  - transfer $107.2M USDC [0x7966…ee94](https://etherscan.io/address/0x7966319bab61f7d6473a64277897885893c2ee94) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xfb7d…1818](https://etherscan.io/tx/0xfb7de02d97d4b5348ad0033c8e568cf3b5baba0148b315a1d0f82affaded1818))
- **25918521** 13:11:47 base 0.06 gwei, 257 txs,  Quasar (quasar.win) 
- re-analysed blocks 25918221 to 25918521 at 13:12:08 UTC: 13752 priced swaps, 24 JIT episodes, 20 lending ops ≥$250k, exchange net $-4.7M stables / $3.1M ETH
- **25918522** 13:11:59 base 0.06 gwei, 168 txs, BuilderNet
- **25918523** 13:12:11 base 0.06 gwei, 320 txs, Titan (titanbuilder.xyz)
- **25918524** 13:12:23 base 0.06 gwei, 205 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $50 of swaps bracketed, fees taken $6
- **25918525** 13:12:35 base 0.06 gwei, 289 txs, Titan (titanbuilder.xyz)
- **25918526** 13:12:47 base 0.06 gwei, 66 txs, BuilderNet
- **25918527** 13:12:59 base 0.06 gwei, 457 txs, Titan (titanbuilder.xyz)
  - transfer $440.8M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $440.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $106.0M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $106.0M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $27.5M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $27.5M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.8M WBTC [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.7M WETH [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.7M WETH [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.7M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
  - transfer $13.7M USDC [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x4cdc…98c5](https://etherscan.io/tx/0x4cdcb7bbde937c4f4cef871232e604d4314619b8d3af9036ddc35852609a98c5))
- **25918528** 13:13:11 base 0.06 gwei, 250 txs, Titan (titanbuilder.xyz)
- **25918529** 13:13:23 base 0.06 gwei, 202 txs, Titan (titanbuilder.xyz)
- **25918530** 13:13:35 base 0.06 gwei, 284 txs, bombora.build 
- **25918531** 13:13:47 base 0.06 gwei, 190 txs, BuilderNet
  - JIT 1 episode(s), $71 of swaps bracketed, fees taken $8
- re-analysed blocks 25918231 to 25918531 at 13:14:03 UTC: 13681 priced swaps, 23 JIT episodes, 19 lending ops ≥$250k, exchange net $2.2M stables / $3.2M ETH
- **25918532** 13:13:59 base 0.06 gwei, 208 txs, Titan (titanbuilder.xyz)
- **25918533** 13:14:11 base 0.06 gwei, 242 txs, Titan (titanbuilder.xyz)
- **25918534** 13:14:23 base 0.07 gwei, 53 txs, BuilderNet
- **25918535** 13:14:35 base 0.06 gwei, 432 txs, Titan (titanbuilder.xyz)
- **25918536** 13:14:47 base 0.07 gwei, 227 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x57d5…9733](https://etherscan.io/tx/0x57d5f6ed39c7a4e28ccd590724a05a2275afa6e83298a728b0d7a658bb1d9733))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x57d5…9733](https://etherscan.io/tx/0x57d5f6ed39c7a4e28ccd590724a05a2275afa6e83298a728b0d7a658bb1d9733))
- **25918537** 13:14:59 base 0.07 gwei, 426 txs, bombora.build 
- **25918538** 13:15:11 base 0.07 gwei, 243 txs, Eureka (eurekabuilder.xyz)
  - JIT 6 episode(s), $30 of swaps bracketed, fees taken $0
- **25918539** 13:15:23 base 0.07 gwei, 80 txs, gethgo1.26.4linux
- **25918540** 13:15:35 base 0.06 gwei, 290 txs, Titan (titanbuilder.xyz)
- **25918541** 13:15:47 base 0.06 gwei, 261 txs, bombora.build 
- re-analysed blocks 25918241 to 25918541 at 13:16:05 UTC: 13527 priced swaps, 29 JIT episodes, 17 lending ops ≥$250k, exchange net $-55k stables / $3.1M ETH
- **25918542** 13:15:59 base 0.06 gwei, 441 txs, BuilderNet
  - JIT 1 episode(s), $579 of swaps bracketed, fees taken $0
- **25918543** 13:16:11 base 0.06 gwei, 251 txs, Titan (titanbuilder.xyz)
- **25918544** 13:16:23 base 0.07 gwei, 261 txs, bombora.build 
- **25918545** 13:16:35 base 0.07 gwei, 216 txs, BuilderNet
- **25918546** 13:16:47 base 0.07 gwei, 344 txs, Titan (titanbuilder.xyz)
- **25918547** 13:16:59 base 0.07 gwei, 205 txs, Titan (titanbuilder.xyz)
- **25918548** 13:17:11 base 0.07 gwei, 268 txs, Eureka (eurekabuilder.xyz)
- **25918549** 13:17:23 base 0.07 gwei, 232 txs, Titan (titanbuilder.xyz)
- **25918550** 13:17:35 base 0.07 gwei, 196 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $56 of swaps bracketed, fees taken $7
- **25918551** 13:17:47 base 0.06 gwei, 147 txs, Nethermind v1.36.0
- re-analysed blocks 25918251 to 25918551 at 13:18:06 UTC: 13295 priced swaps, 31 JIT episodes, 16 lending ops ≥$250k, exchange net $-234k stables / $2.2M ETH
- **25918552** 13:17:59 base 0.06 gwei, 130 txs, Titan (titanbuilder.xyz)
- **25918553** 13:18:11 base 0.06 gwei, 396 txs, Eureka (eurekabuilder.xyz)
- **25918554** 13:18:23 base 0.07 gwei, 248 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x57fb…fd5f](https://etherscan.io/tx/0x57fb54e8a4885f7187ae538e28c7a81e8ba362553a1d87d971b4f46248f1fd5f))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x57fb…fd5f](https://etherscan.io/tx/0x57fb54e8a4885f7187ae538e28c7a81e8ba362553a1d87d971b4f46248f1fd5f))
- **25918555** 13:18:35 base 0.07 gwei, 318 txs,  Quasar (quasar.win) 
- **25918556** 13:18:47 base 0.07 gwei, 218 txs, Titan (titanbuilder.xyz)
- **25918557** 13:18:59 base 0.07 gwei, 257 txs, Titan (titanbuilder.xyz)
- **25918558** 13:19:11 base 0.07 gwei, 195 txs, BuilderNet
- **25918559** 13:19:23 base 0.07 gwei, 205 txs, Titan (titanbuilder.xyz)
- **25918560** 13:19:35 base 0.07 gwei, 257 txs, Eureka (eurekabuilder.xyz)
- **25918561** 13:19:47 base 0.07 gwei, 227 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918261 to 25918561 at 13:20:07 UTC: 13254 priced swaps, 31 JIT episodes, 17 lending ops ≥$250k, exchange net $134k stables / $-800k ETH
- **25918562** 13:19:59 base 0.07 gwei, 196 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x8cdd…419d](https://etherscan.io/tx/0x8cdd4a202e806b783640add949b049bd157ba84ec94d8fd1c404393454c5419d))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x8cdd…419d](https://etherscan.io/tx/0x8cdd4a202e806b783640add949b049bd157ba84ec94d8fd1c404393454c5419d))
- **25918563** 13:20:11 base 0.07 gwei, 263 txs, Titan (titanbuilder.xyz)
- **25918564** 13:20:23 base 0.07 gwei, 170 txs, Titan (titanbuilder.xyz)
- **25918565** 13:20:35 base 0.07 gwei, 341 txs, Titan (titanbuilder.xyz)
- **25918566** 13:20:47 base 0.07 gwei, 378 txs,  Quasar (quasar.win) 
- **25918567** 13:20:59 base 0.07 gwei, 210 txs, Eureka (eurekabuilder.xyz)
- **25918568** 13:21:11 base 0.07 gwei, 216 txs, Titan (titanbuilder.xyz)
- **25918569** 13:21:23 base 0.07 gwei, 267 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x932c…c629](https://etherscan.io/tx/0x932c7999b633ec3e125f3bb82abbf9024d049616c18f5d522f18635b4c0ec629))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x932c…c629](https://etherscan.io/tx/0x932c7999b633ec3e125f3bb82abbf9024d049616c18f5d522f18635b4c0ec629))
- **25918570** 13:21:35 base 0.07 gwei, 234 txs,  Quasar (quasar.win) 
- **25918571** 13:21:47 base 0.07 gwei, 248 txs, Eureka (eurekabuilder.xyz)
- re-analysed blocks 25918271 to 25918571 at 13:22:02 UTC: 13248 priced swaps, 31 JIT episodes, 17 lending ops ≥$250k, exchange net $5.5M stables / $148k ETH
- **25918572** 13:21:59 base 0.07 gwei, 213 txs, Titan (titanbuilder.xyz)
- **25918573** 13:22:11 base 0.07 gwei, 271 txs, Titan (titanbuilder.xyz)
- **25918574** 13:22:23 base 0.07 gwei, 334 txs, Titan (titanbuilder.xyz)
- **25918575** 13:22:35 base 0.07 gwei, 460 txs, Titan (titanbuilder.xyz)
- **25918576** 13:22:47 base 0.07 gwei, 319 txs, Titan (titanbuilder.xyz)
- **25918577** 13:22:59 base 0.07 gwei, 317 txs, Titan (titanbuilder.xyz)
- **25918578** 13:23:11 base 0.08 gwei, 310 txs, Titan (titanbuilder.xyz)
  - JIT 3 episode(s), $6 of swaps bracketed, fees taken $0
- **25918579** 13:23:23 base 0.08 gwei, 110 txs, gethgo1.25.10linux
- **25918580** 13:23:35 base 0.07 gwei, 343 txs, Titan (titanbuilder.xyz)
- **25918581** 13:23:47 base 0.07 gwei, 267 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918281 to 25918581 at 13:24:07 UTC: 13274 priced swaps, 34 JIT episodes, 17 lending ops ≥$250k, exchange net $8.5M stables / $-1.0M ETH
- **25918582** 13:23:59 base 0.07 gwei, 79 txs, BuilderNet
- **25918583** 13:24:11 base 0.07 gwei, 433 txs, Titan (titanbuilder.xyz)
- **25918584** 13:24:23 base 0.08 gwei, 289 txs, Titan (titanbuilder.xyz)
- **25918585** 13:24:35 base 0.08 gwei, 325 txs, Titan (titanbuilder.xyz)
- **25918586** 13:24:47 base 0.08 gwei, 225 txs, Titan (titanbuilder.xyz)
- **25918587** 13:24:59 base 0.08 gwei, 392 txs,  Quasar (quasar.win) 
- **25918588** 13:25:11 base 0.08 gwei, 314 txs, Titan (titanbuilder.xyz)
- **25918589** 13:25:23 base 0.08 gwei, 228 txs, Titan (titanbuilder.xyz)
- **25918590** 13:25:35 base 0.08 gwei, 256 txs, Titan (titanbuilder.xyz)
- **25918591** 13:25:47 base 0.09 gwei, 311 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918291 to 25918591 at 13:26:04 UTC: 13278 priced swaps, 33 JIT episodes, 14 lending ops ≥$250k, exchange net $6.1M stables / $-3.8M ETH
- **25918592** 13:25:59 base 0.09 gwei, 86 txs, gethgo1.26.4linux
- **25918593** 13:26:11 base 0.08 gwei, 404 txs, Eureka (eurekabuilder.xyz)
- **25918594** 13:26:23 base 0.08 gwei, 292 txs, Titan (titanbuilder.xyz)
- **25918595** 13:26:35 base 0.09 gwei, 296 txs, Titan (titanbuilder.xyz)
- **25918596** 13:26:47 base 0.09 gwei, 248 txs, Titan (titanbuilder.xyz)
- **25918597** 13:26:59 base 0.09 gwei, 292 txs, Titan (titanbuilder.xyz)
- **25918598** 13:27:11 base 0.09 gwei, 258 txs, Titan (titanbuilder.xyz)
- **25918599** 13:27:23 base 0.09 gwei, 227 txs, bombora.build 
- **25918600** 13:27:35 base 0.09 gwei, 92 txs, BuilderNet
- **25918601** 13:27:47 base 0.08 gwei, 427 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918301 to 25918601 at 13:28:11 UTC: 13226 priced swaps, 33 JIT episodes, 16 lending ops ≥$250k, exchange net $3.1M stables / $-4.4M ETH
- **25918602** 13:27:59 base 0.09 gwei, 178 txs, Titan (titanbuilder.xyz)
- **25918603** 13:28:11 base 0.09 gwei, 218 txs, Titan (titanbuilder.xyz)
  - transfer $25.5M USDT [0xe2e7…c372](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372) → [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
  - transfer $13.3M USDT [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) → [0xb0c4…5b91](https://etherscan.io/address/0xb0c424116172b55cbb6dd3136f5989f7959e5b91) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
  - transfer $13.3M USDT [0xb0c4…5b91](https://etherscan.io/address/0xb0c424116172b55cbb6dd3136f5989f7959e5b91) → [0xef4c…8a6a](https://etherscan.io/address/0xef4cb7e87f212f128f0b24cf35861e52b3c78a6a) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
  - transfer $13.3M USDT [0xef4c…8a6a](https://etherscan.io/address/0xef4cb7e87f212f128f0b24cf35861e52b3c78a6a) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
  - transfer $9.8M USDT [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) → [0xb0c4…5b91](https://etherscan.io/address/0xb0c424116172b55cbb6dd3136f5989f7959e5b91) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
  - transfer $9.8M USDT [0xb0c4…5b91](https://etherscan.io/address/0xb0c424116172b55cbb6dd3136f5989f7959e5b91) → [0xef4c…8a6a](https://etherscan.io/address/0xef4cb7e87f212f128f0b24cf35861e52b3c78a6a) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
  - transfer $9.8M USDT [0xef4c…8a6a](https://etherscan.io/address/0xef4cb7e87f212f128f0b24cf35861e52b3c78a6a) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xc8e5…e794](https://etherscan.io/tx/0xc8e505103085feb94318ff7e6a2ec9549337f5eb5498f7323927777b3306e794))
- **25918604** 13:28:23 base 0.08 gwei, 288 txs,  Quasar (quasar.win) 
- **25918605** 13:28:35 base 0.08 gwei, 289 txs, Titan (titanbuilder.xyz)
- **25918606** 13:28:47 base 0.08 gwei, 255 txs, Titan (titanbuilder.xyz)
- **25918607** 13:28:59 base 0.08 gwei, 320 txs, Titan (titanbuilder.xyz)
- **25918608** 13:29:11 base 0.08 gwei, 292 txs,  Quasar (quasar.win) 
- **25918609** 13:29:23 base 0.08 gwei, 252 txs,  Quasar (quasar.win) 
  - transfer $7.5M ETH [Binance 15 (memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) → [0x8546…9a9c](https://etherscan.io/address/0x85464b207d7c1fce8da13d2f3d950c796e399a9c) ([0x0d9c…4e69](https://etherscan.io/tx/0x0d9caf462c2edfeb0f5feb7672115f4e991b63d52b191a9aec4502705dfc4e69))
- **25918610** 13:29:35 base 0.08 gwei, 237 txs,  Quasar (quasar.win) 
- **25918611** 13:29:47 base 0.08 gwei, 231 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918311 to 25918611 at 13:30:06 UTC: 13087 priced swaps, 33 JIT episodes, 16 lending ops ≥$250k, exchange net $2.5M stables / $-11.4M ETH
- **25918612** 13:29:59 base 0.08 gwei, 232 txs, bombora.build 
- **25918613** 13:30:11 base 0.07 gwei, 576 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $653 of swaps bracketed, fees taken $1
- **25918614** 13:30:23 base 0.08 gwei, 471 txs,  Quasar (quasar.win) 
- **25918615** 13:30:35 base 0.09 gwei, 46 txs, BuilderNet
- **25918616** 13:30:47 base 0.08 gwei, 407 txs, Titan (titanbuilder.xyz)
- **25918617** 13:30:59 base 0.08 gwei, 382 txs, Titan (titanbuilder.xyz)
- **25918618** 13:31:11 base 0.08 gwei, 142 txs, gethgo1.25.10linux
- **25918619** 13:31:23 base 0.07 gwei, 426 txs,  Quasar (quasar.win) 
- **25918620** 13:31:35 base 0.08 gwei, 245 txs, Titan (titanbuilder.xyz)
- **25918621** 13:31:47 base 0.08 gwei, 223 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918321 to 25918621 at 13:32:05 UTC: 13174 priced swaps, 34 JIT episodes, 16 lending ops ≥$250k, exchange net $8.1M stables / $-10.1M ETH
- **25918622** 13:31:59 base 0.08 gwei, 283 txs, Eureka (eurekabuilder.xyz)
- **25918623** 13:32:11 base 0.08 gwei, 280 txs,  Quasar (quasar.win) 
- **25918624** 13:32:23 base 0.08 gwei, 280 txs, BuilderNet
- **25918625** 13:32:35 base 0.08 gwei, 332 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $4043 of swaps bracketed, fees taken $3
- **25918626** 13:32:47 base 0.08 gwei, 192 txs, Titan (titanbuilder.xyz)
- **25918627** 13:32:59 base 0.07 gwei, 334 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xd55f…70a4](https://etherscan.io/tx/0xd55fd628bb0e5d9e781c6357ddfa0eaf1c7cd0c65fea6768e149b46868bf70a4))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xd55f…70a4](https://etherscan.io/tx/0xd55fd628bb0e5d9e781c6357ddfa0eaf1c7cd0c65fea6768e149b46868bf70a4))
- **25918628** 13:33:11 base 0.07 gwei, 290 txs, Titan (titanbuilder.xyz)
- **25918629** 13:33:23 base 0.07 gwei, 259 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x2c33…9254](https://etherscan.io/tx/0x2c33b669fd272283e63e5e0648285481d51238ce118e4d1bfca02b4ecddd9254))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x2c33…9254](https://etherscan.io/tx/0x2c33b669fd272283e63e5e0648285481d51238ce118e4d1bfca02b4ecddd9254))
- **25918630** 13:33:35 base 0.07 gwei, 93 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $75 of swaps bracketed, fees taken $0
- **25918631** 13:33:47 base 0.07 gwei, 423 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $6227 of swaps bracketed, fees taken $9
- re-analysed blocks 25918331 to 25918631 at 13:34:08 UTC: 13179 priced swaps, 35 JIT episodes, 15 lending ops ≥$250k, exchange net $9.2M stables / $-9.5M ETH
- **25918632** 13:33:59 base 0.07 gwei, 222 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $25 of swaps bracketed, fees taken $0
- **25918633** 13:34:11 base 0.07 gwei, 53 txs, BuilderNet
- **25918634** 13:34:23 base 0.06 gwei, 247 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xe32b…e3d0](https://etherscan.io/tx/0xe32b6ea8fc44f001763482dd91bc6473559b13132417d462c729e9006de8e3d0))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xe32b…e3d0](https://etherscan.io/tx/0xe32b6ea8fc44f001763482dd91bc6473559b13132417d462c729e9006de8e3d0))
- **25918635** 13:34:35 base 0.06 gwei, 146 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x8e40…c7fa](https://etherscan.io/tx/0x8e40a8c0bbf04180e3132280b29e61b25130e22342927d72dd8056a385a7c7fa))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x8e40…c7fa](https://etherscan.io/tx/0x8e40a8c0bbf04180e3132280b29e61b25130e22342927d72dd8056a385a7c7fa))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x2191…48a5](https://etherscan.io/tx/0x2191f5c4083c047f95941bd7ec60d1b6c6740cd3c8d67466a636ad7ef4ab48a5))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x2191…48a5](https://etherscan.io/tx/0x2191f5c4083c047f95941bd7ec60d1b6c6740cd3c8d67466a636ad7ef4ab48a5))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x109b…23c5](https://etherscan.io/tx/0x109b508c9daec521cbd834f2fb2c85d8f73b47ad030c097eb6d81c2ddffa23c5))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x109b…23c5](https://etherscan.io/tx/0x109b508c9daec521cbd834f2fb2c85d8f73b47ad030c097eb6d81c2ddffa23c5))
- **25918636** 13:34:47 base 0.06 gwei, 86 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x9bff…522f](https://etherscan.io/tx/0x9bffb4ed29a37255c3b5618025b355889edf4dd5f117eb32099268d9bfb0522f))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x9bff…522f](https://etherscan.io/tx/0x9bffb4ed29a37255c3b5618025b355889edf4dd5f117eb32099268d9bfb0522f))
  - JIT 1 episode(s), $3664 of swaps bracketed, fees taken $2
- **25918637** 13:34:59 base 0.06 gwei, 560 txs, Eureka (eurekabuilder.xyz)
- **25918638** 13:35:11 base 0.07 gwei, 298 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $1994 of swaps bracketed, fees taken $1
- **25918639** 13:35:23 base 0.07 gwei, 195 txs, Titan (titanbuilder.xyz)
- **25918640** 13:35:35 base 0.08 gwei, 334 txs, Eureka (eurekabuilder.xyz)
  - transfer $7.0M USDC [0x260b…4cea](https://etherscan.io/address/0x260b364fe0d3d37e6fd3cda0fa50926a06c54cea) → [0x3167…6c68](https://etherscan.io/address/0x316773753754e128d39924e74119053005ce6c68) ([0xe7b3…f101](https://etherscan.io/tx/0xe7b3f0a39ce731574096b47136a9956307a064f0a3ab234444c2f197bb6bf101))
- **25918641** 13:35:47 base 0.08 gwei, 192 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918341 to 25918641 at 13:36:05 UTC: 13397 priced swaps, 38 JIT episodes, 15 lending ops ≥$250k, exchange net $4.4M stables / $-8.8M ETH
- **25918642** 13:35:59 base 0.07 gwei, 184 txs, Nethermind v1.39.2
- **25918643** 13:36:11 base 0.07 gwei, 375 txs, Eureka (eurekabuilder.xyz)
  - transfer $7.0M USDC [0x3167…6c68](https://etherscan.io/address/0x316773753754e128d39924e74119053005ce6c68) → [0xcd53…ca7b](https://etherscan.io/address/0xcd531ae9efcce479654c4926dec5f6209531ca7b) ([0x9fdd…da67](https://etherscan.io/tx/0x9fdd31b09d25727b8245d6d310fc3ab0a5bc1ad688bf4661d5255c325873da67))
- **25918644** 13:36:23 base 0.07 gwei, 227 txs, Titan (titanbuilder.xyz)
- **25918645** 13:36:35 base 0.07 gwei, 296 txs, Titan (titanbuilder.xyz)
- **25918646** 13:36:47 base 0.07 gwei, 305 txs,  Quasar (quasar.win) 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xcb0c…e6b3](https://etherscan.io/tx/0xcb0c651b2205a751946d3c21f118ccb9d5ce32490a71f32e8bd2e4a9938be6b3))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xcb0c…e6b3](https://etherscan.io/tx/0xcb0c651b2205a751946d3c21f118ccb9d5ce32490a71f32e8bd2e4a9938be6b3))
- **25918647** 13:36:59 base 0.08 gwei, 70 txs, gethgo1.25.10linux
- **25918648** 13:37:11 base 0.07 gwei, 169 txs, Titan (titanbuilder.xyz)
- **25918649** 13:37:23 base 0.06 gwei, 411 txs, Titan (titanbuilder.xyz)
- **25918650** 13:37:35 base 0.07 gwei, 215 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x9dc2…cd24](https://etherscan.io/tx/0x9dc2a19d3585609effe5df573c27e320c243265a2c104523454e7f98c406cd24))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x9dc2…cd24](https://etherscan.io/tx/0x9dc2a19d3585609effe5df573c27e320c243265a2c104523454e7f98c406cd24))
- **25918651** 13:37:47 base 0.07 gwei, 253 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $58 of swaps bracketed, fees taken $0
- re-analysed blocks 25918351 to 25918651 at 13:38:07 UTC: 13341 priced swaps, 38 JIT episodes, 15 lending ops ≥$250k, exchange net $9.1M stables / $-9.3M ETH
- **25918652** 13:37:59 base 0.07 gwei, 90 txs, BuilderNet
- **25918653** 13:38:11 base 0.06 gwei, 366 txs, Titan (titanbuilder.xyz)
- **25918654** 13:38:23 base 0.07 gwei, 356 txs, Eureka (eurekabuilder.xyz)
- **25918655** 13:38:35 base 0.07 gwei, 235 txs, Eureka (eurekabuilder.xyz)
- **25918656** 13:38:47 base 0.06 gwei, 235 txs, Eureka (eurekabuilder.xyz)
- **25918657** 13:38:59 base 0.06 gwei, 208 txs, BuilderNet
- **25918658** 13:39:11 base 0.06 gwei, 246 txs, Eureka (eurekabuilder.xyz)
- **25918659** 13:39:23 base 0.06 gwei, 250 txs, Titan (titanbuilder.xyz)
- **25918660** 13:39:35 base 0.06 gwei, 212 txs, bombora.build 
- **25918661** 13:39:47 base 0.06 gwei, 323 txs,  Quasar (quasar.win) 
- re-analysed blocks 25918361 to 25918661 at 13:40:10 UTC: 13301 priced swaps, 38 JIT episodes, 17 lending ops ≥$250k, exchange net $12.2M stables / $-9.3M ETH
- **25918662** 13:39:59 base 0.06 gwei, 396 txs, Titan (titanbuilder.xyz)
- **25918663** 13:40:11 base 0.06 gwei, 267 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $243 of swaps bracketed, fees taken $0
- **25918664** 13:40:23 base 0.06 gwei, 301 txs, Eureka (eurekabuilder.xyz)
- **25918665** 13:40:35 base 0.06 gwei, 298 txs, bombora.build 
- **25918666** 13:40:47 base 0.06 gwei, 171 txs, gethgo1.26.4linux
- **25918667** 13:40:59 base 0.05 gwei, 425 txs, Titan (titanbuilder.xyz)
- **25918668** 13:41:11 base 0.06 gwei, 407 txs,  Quasar (quasar.win) 
- **25918669** 13:41:23 base 0.06 gwei, 190 txs, builder.ultrasound.money
- **25918670** 13:41:35 base 0.06 gwei, 344 txs, BuilderNet
  - transfer $80.9M WBTC [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) → [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) ([0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067))
  - transfer $80.9M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) ([0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067))
  - transfer $80.9M WBTC [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) → [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) ([0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067))
  - transfer $80.9M WBTC [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) → [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) ([0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067))
  - transfer $80.9M WBTC [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x846e…d067](https://etherscan.io/tx/0x846e7148728cfefe3600ea560deba243bf87931d1fcbbdb241808bc88d36d067))
  - transfer $12.6M USDC [Coinbase 11 (memory)](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) → [0x3b5b…e4b7](https://etherscan.io/address/0x3b5b1991c1c274573ae729cd31f3a6bb1f60e4b7) ([0xac27…5aee](https://etherscan.io/tx/0xac27f92745ec329d692ad1bd24a34b4996cd67a85bc221b0e96f4db86b485aee))
- **25918671** 13:41:47 base 0.06 gwei, 380 txs,  Quasar (quasar.win) 
- re-analysed blocks 25918371 to 25918671 at 13:42:09 UTC: 13277 priced swaps, 38 JIT episodes, 17 lending ops ≥$250k, exchange net $-34k stables / $-9.5M ETH
- **25918672** 13:41:59 base 0.06 gwei, 311 txs, Titan (titanbuilder.xyz)
- **25918673** 13:42:11 base 0.06 gwei, 182 txs, BuilderNet
- **25918674** 13:42:23 base 0.06 gwei, 451 txs,  Quasar (quasar.win) 
- **25918675** 13:42:35 base 0.06 gwei, 364 txs,  Quasar (quasar.win) 
  - transfer $36.9M ETH [Binance 14 (memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) → [Binance 15 (memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) ([0x2392…aaaf](https://etherscan.io/tx/0x239224012d163401de098beea6bfaeb5129d4d60f110c0dd8d4005f71f2eaaaf))
- **25918676** 13:42:47 base 0.06 gwei, 324 txs,  Quasar (quasar.win) 
- **25918677** 13:42:59 base 0.06 gwei, 414 txs, Titan (titanbuilder.xyz)
- **25918678** 13:43:11 base 0.06 gwei, 196 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xbace…7a23](https://etherscan.io/tx/0xbace059af1fed5940fed6ee28124569b6913f30e3a6d3787f94f5c2a45497a23))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xbace…7a23](https://etherscan.io/tx/0xbace059af1fed5940fed6ee28124569b6913f30e3a6d3787f94f5c2a45497a23))
- **25918679** 13:43:23 base 0.06 gwei, 428 txs, Titan (titanbuilder.xyz)
- **25918680** 13:43:35 base 0.06 gwei, 186 txs, Titan (titanbuilder.xyz)
  - transfer $46.4M USDC [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) → [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d))
  - transfer $46.4M USDC [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) → [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d))
  - transfer $46.4M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d))
  - transfer $46.4M USDC [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d))
  - lending Aave v3 supply $46.4M USDC account [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d))
  - lending Aave v3 withdraw $46.4M USDC account [0xd4fa…d23e](https://etherscan.io/address/0xd4fa2d31b7968e448877f69a96de69f5de8cd23e) ([0x38d6…268d](https://etherscan.io/tx/0x38d60e0cc2d441ed537cb8c2b1c05466abae6e656d220be9a43ca9e9b63e268d))
- **25918681** 13:43:47 base 0.06 gwei, 336 txs,  Quasar (quasar.win) 
  - transfer $20.0M USDT [0x2d4d…7bb4](https://etherscan.io/address/0x2d4d2a025b10c09bdbd794b4fce4f7ea8c7d7bb4) → [0xb873…313c](https://etherscan.io/address/0xb8734a14fbd4aa2d44e6aa830405ffc861ba313c) ([0x47c9…f99a](https://etherscan.io/tx/0x47c9a297df7f2f1b95d3ec11f02893f6e07bb7f0d80dfaa3b84191fa625af99a))
- re-analysed blocks 25918381 to 25918681 at 13:44:08 UTC: 13142 priced swaps, 35 JIT episodes, 21 lending ops ≥$250k, exchange net $3.5M stables / $-8.9M ETH
- **25918682** 13:43:59 base 0.06 gwei, 71 txs, besu 26.8.1
- **25918683** 13:44:11 base 0.06 gwei, 206 txs, besu 26.8.1
  - transfer $12.6M USDC [0x3b5b…e4b7](https://etherscan.io/address/0x3b5b1991c1c274573ae729cd31f3a6bb1f60e4b7) → [Coinbase 11 (memory)](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) ([0x7dab…2681](https://etherscan.io/tx/0x7dab0aa07172caef89c3260abbc8b7f5a63705b231e98d69b617f48df8ae2681))
- **25918684** 13:44:23 base 0.05 gwei, 367 txs, Titan (titanbuilder.xyz)
  - transfer $440.8M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $440.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $106.1M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $106.1M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $27.5M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $27.5M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.8M WBTC [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.7M WETH [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.7M WETH [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.7M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
  - transfer $13.7M USDC [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x1c1f…fc8e](https://etherscan.io/tx/0x1c1f27d1426620e41436be83e99e3dfd4e1948e2f290f43703ac53f83de4fc8e))
- **25918685** 13:44:35 base 0.06 gwei, 281 txs, bombora.build 
- **25918686** 13:44:47 base 0.05 gwei, 306 txs, Titan (titanbuilder.xyz)
- **25918687** 13:44:59 base 0.05 gwei, 235 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xaacb…7d3a](https://etherscan.io/tx/0xaacb00f216a309378af59a2ad8c6efeb4743a9136ee0d2731d7daf446a157d3a))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xaacb…7d3a](https://etherscan.io/tx/0xaacb00f216a309378af59a2ad8c6efeb4743a9136ee0d2731d7daf446a157d3a))
- **25918688** 13:45:11 base 0.05 gwei, 270 txs, Titan (titanbuilder.xyz)
  - transfer $12.6M USDC [Coinbase 11 (memory)](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) → [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) ([0x2fed…2d25](https://etherscan.io/tx/0x2fedfb9b74f7af11b9b55c9d3926e7c70caf7ae9732c6d09bc44e3c548922d25))
  - issuance USDC burn $12.6M ([0x2fed…2d25](https://etherscan.io/tx/0x2fedfb9b74f7af11b9b55c9d3926e7c70caf7ae9732c6d09bc44e3c548922d25))
- **25918689** 13:45:23 base 0.05 gwei, 297 txs,  Quasar (quasar.win) 
- **25918690** 13:45:35 base 0.06 gwei, 235 txs, Titan (titanbuilder.xyz)
- **25918691** 13:45:47 base 0.06 gwei, 234 txs, Eureka (eurekabuilder.xyz)
- **25918692** 13:45:59 base 0.06 gwei, 68 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xeebc…dd96](https://etherscan.io/tx/0xeebc5764ab5e5bb9627c3c30915b5dfedf3606ffdde02e8b1f0bdcb6c505dd96))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xeebc…dd96](https://etherscan.io/tx/0xeebc5764ab5e5bb9627c3c30915b5dfedf3606ffdde02e8b1f0bdcb6c505dd96))
- re-analysed blocks 25918392 to 25918692 at 13:46:18 UTC: 13165 priced swaps, 34 JIT episodes, 23 lending ops ≥$250k, exchange net $82k stables / $-9.1M ETH
- **25918693** 13:46:11 base 0.05 gwei, 351 txs, Titan (titanbuilder.xyz)
- **25918694** 13:46:23 base 0.06 gwei, 144 txs, 0x388c…9297
- **25918695** 13:46:35 base 0.05 gwei, 392 txs, Eureka (eurekabuilder.xyz)
- **25918696** 13:46:47 base 0.06 gwei, 132 txs, 0x4675…a263
- **25918697** 13:46:59 base 0.05 gwei, 464 txs, Eureka (eurekabuilder.xyz)
- **25918698** 13:47:11 base 0.05 gwei, 249 txs, BuilderNet
- **25918699** 13:47:23 base 0.05 gwei, 221 txs, Titan (titanbuilder.xyz)
- **25918700** 13:47:35 base 0.05 gwei, 105 txs, 0x345d…78ee
- **25918701** 13:47:47 base 0.05 gwei, 308 txs, BuilderNet
- **25918702** 13:47:59 base 0.05 gwei, 285 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918402 to 25918702 at 13:48:16 UTC: 13273 priced swaps, 29 JIT episodes, 23 lending ops ≥$250k, exchange net $-740k stables / $-8.9M ETH
- **25918703** 13:48:11 base 0.05 gwei, 203 txs, reth/v2.5.2/linux
- **25918704** 13:48:23 base 0.05 gwei, 268 txs, Titan (titanbuilder.xyz)
- **25918705** 13:48:35 base 0.05 gwei, 155 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $750 of swaps bracketed, fees taken $0
- **25918706** 13:48:47 base 0.05 gwei, 285 txs, Titan (titanbuilder.xyz)
- **25918707** 13:48:59 base 0.05 gwei, 234 txs, bombora.build 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xdeae…d640](https://etherscan.io/tx/0xdeaeecf6985428f9730bd3364f695d338bb52c68ac410a5d3eae6d641a3fd640))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xdeae…d640](https://etherscan.io/tx/0xdeaeecf6985428f9730bd3364f695d338bb52c68ac410a5d3eae6d641a3fd640))
- **25918708** 13:49:11 base 0.05 gwei, 310 txs, Titan (titanbuilder.xyz)
- **25918709** 13:49:23 base 0.05 gwei, 228 txs,  Quasar (quasar.win) 
- **25918710** 13:49:35 base 0.05 gwei, 227 txs, Titan (titanbuilder.xyz)
- **25918711** 13:49:47 base 0.05 gwei, 292 txs,  Quasar (quasar.win) 
- **25918712** 13:49:59 base 0.05 gwei, 159 txs, BuilderNet
- re-analysed blocks 25918412 to 25918712 at 13:50:20 UTC: 13223 priced swaps, 29 JIT episodes, 20 lending ops ≥$250k, exchange net $-1.7M stables / $-8.9M ETH
- **25918713** 13:50:11 base 0.05 gwei, 325 txs, Titan (titanbuilder.xyz)
- **25918714** 13:50:23 base 0.05 gwei, 75 txs, BuilderNet
  - lending Aave v3 supply $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xd5a1…cd9a](https://etherscan.io/tx/0xd5a12b69f4cdb6b26b7a1291d9438d852ad2f410fe7c738c24df4b3c5136cd9a))
  - lending Aave v3 withdraw $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xd539…f8dc](https://etherscan.io/tx/0xd53988049b7480bba7db023ac795ac4808b87514fbc940f6693224844da9f8dc))
  - JIT 1 episode(s), $16 of swaps bracketed, fees taken $0
- **25918715** 13:50:35 base 0.05 gwei, 203 txs, reth/v2.4.1/linux
- **25918716** 13:50:47 base 0.05 gwei, 175 txs, gethgo1.26.4linux
- **25918717** 13:50:59 base 0.04 gwei, 439 txs, Titan (titanbuilder.xyz)
- **25918718** 13:51:11 base 0.05 gwei, 312 txs, bombora.build 
- **25918719** 13:51:23 base 0.05 gwei, 343 txs, Titan (titanbuilder.xyz)
- **25918720** 13:51:35 base 0.05 gwei, 189 txs, BuilderNet
- **25918721** 13:51:47 base 0.05 gwei, 337 txs, Titan (titanbuilder.xyz)
- **25918722** 13:51:59 base 0.05 gwei, 58 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918422 to 25918722 at 13:52:15 UTC: 13229 priced swaps, 30 JIT episodes, 22 lending ops ≥$250k, exchange net $-588k stables / $-9.2M ETH
- **25918723** 13:52:11 base 0.04 gwei, 381 txs, Titan (titanbuilder.xyz)
- **25918724** 13:52:23 base 0.05 gwei, 89 txs, gethgo1.25.1linux
- **25918725** 13:52:35 base 0.04 gwei, 363 txs, Titan (titanbuilder.xyz)
- **25918726** 13:52:47 base 0.05 gwei, 320 txs, bombora.build 
- **25918727** 13:52:59 base 0.04 gwei, 327 txs, BuilderNet
- **25918728** 13:53:11 base 0.05 gwei, 339 txs, Titan (titanbuilder.xyz)
- **25918729** 13:53:23 base 0.05 gwei, 64 txs, gethgo1.25.10linux
- **25918730** 13:53:35 base 0.04 gwei, 190 txs, Nethermind v1.39.2
- **25918731** 13:53:47 base 0.04 gwei, 401 txs, Titan (titanbuilder.xyz)
- **25918732** 13:53:59 base 0.04 gwei, 314 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $239 of swaps bracketed, fees taken $0
- re-analysed blocks 25918432 to 25918732 at 13:54:17 UTC: 13159 priced swaps, 30 JIT episodes, 22 lending ops ≥$250k, exchange net $5.7M stables / $-9.2M ETH
- **25918733** 13:54:11 base 0.04 gwei, 151 txs, gethgo1.25.7linux
- **25918734** 13:54:23 base 0.04 gwei, 415 txs, Titan (titanbuilder.xyz)
- **25918735** 13:54:35 base 0.04 gwei, 440 txs, bombora.build 
- **25918736** 13:54:47 base 0.04 gwei, 327 txs, Titan (titanbuilder.xyz)
- **25918737** 13:54:59 base 0.04 gwei, 272 txs,  Quasar (quasar.win) 
- **25918738** 13:55:11 base 0.04 gwei, 140 txs, 0x123b…a806
- **25918739** 13:55:23 base 0.04 gwei, 294 txs,  Quasar (quasar.win) 
- **25918740** 13:55:35 base 0.04 gwei, 224 txs, BuilderNet
  - lending Aave v3 supply $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x30ef…c679](https://etherscan.io/tx/0x30efdfa0842bb7345e20e89748169f1af45b1a4e1fda7c65b72576293e8ec679))
  - lending Aave v3 withdraw $1.8M WETH account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xb748…1677](https://etherscan.io/tx/0xb7483fad6a2768445c245770047fd0876c4be85b28f0e0be25ea757796141677))
  - JIT 1 episode(s), $1077 of swaps bracketed, fees taken $0
- **25918741** 13:55:47 base 0.04 gwei, 243 txs,  Quasar (quasar.win) 
- **25918742** 13:55:59 base 0.04 gwei, 199 txs, bombora.build 
- **25918743** 13:56:11 base 0.04 gwei, 219 txs, bombora.build 
- re-analysed blocks 25918443 to 25918743 at 13:56:48 UTC: 13015 priced swaps, 31 JIT episodes, 24 lending ops ≥$250k, exchange net $4.4M stables / $-9.4M ETH
- **25918744** 13:56:23 base 0.04 gwei, 311 txs, Titan (titanbuilder.xyz)
  - lending Aave v3 repay $2.3M USDe account [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) ([0x0b8e…f8e5](https://etherscan.io/tx/0x0b8effa370896607440d232cc2ccc446d81d100e92d1b89bdbd192f393c7f8e5))
- **25918745** 13:56:35 base 0.04 gwei, 268 txs, Titan (titanbuilder.xyz)
- **25918746** 13:56:47 base 0.04 gwei, 308 txs, Titan (titanbuilder.xyz)
- **25918747** 13:56:59 base 0.04 gwei, 231 txs, Titan (titanbuilder.xyz)
- **25918748** 13:57:11 base 0.04 gwei, 103 txs, BuilderNet
- **25918749** 13:57:23 base 0.04 gwei, 448 txs,  Quasar (quasar.win) 
- **25918750** 13:57:35 base 0.05 gwei, 248 txs, Titan (titanbuilder.xyz)
- **25918751** 13:57:47 base 0.04 gwei, 76 txs, gethgo1.25.10linux
- **25918752** 13:57:59 base 0.04 gwei, 145 txs, Nethermind v1.39.2
- **25918753** 13:58:11 base 0.04 gwei, 143 txs, BuilderNet
- re-analysed blocks 25918453 to 25918753 at 13:58:29 UTC: 12940 priced swaps, 30 JIT episodes, 25 lending ops ≥$250k, exchange net $4.4M stables / $-9.5M ETH
- **25918754** 13:58:23 base 0.04 gwei, 549 txs, Titan (titanbuilder.xyz)
- **25918755** 13:58:35 base 0.05 gwei, 291 txs, Titan (titanbuilder.xyz)
- **25918756** 13:58:47 base 0.05 gwei, 420 txs, Eureka (eurekabuilder.xyz)
  - transfer $28.4M USDT [Binance 16 (memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) → [0x98ad…ba9d](https://etherscan.io/address/0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d) ([0xae35…9548](https://etherscan.io/tx/0xae35398be3eaffc1354a8112d09bc13780c7ac568ab1b7ddd52c9e020d4d9548))
- **25918757** 13:58:59 base 0.05 gwei, 138 txs, 0x2112…f5d8
- **25918758** 13:59:11 base 0.05 gwei, 399 txs, Titan (titanbuilder.xyz)
- **25918759** 13:59:23 base 0.05 gwei, 194 txs, BuilderNet
- **25918760** 13:59:35 base 0.05 gwei, 440 txs, Eureka (eurekabuilder.xyz)
- **25918761** 13:59:47 base 0.05 gwei, 317 txs, Titan (titanbuilder.xyz)
  - lending Aave v3 withdraw $2.6M sUSDe account [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) ([0x2a4b…3ec6](https://etherscan.io/tx/0x2a4b887380744e07e49a65f65c8b289f9bf448234715ccb3cfe9632c131f3ec6))
- **25918762** 13:59:59 base 0.05 gwei, 261 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x95a5…1afb](https://etherscan.io/tx/0x95a5388998cd8ff794a83749cf5c14e4bca1b994da29869052f893f4faee1afb))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x95a5…1afb](https://etherscan.io/tx/0x95a5388998cd8ff794a83749cf5c14e4bca1b994da29869052f893f4faee1afb))
- **25918763** 14:00:11 base 0.05 gwei, 6 txs, bobTheBuilder.xyz
- re-analysed blocks 25918463 to 25918763 at 14:00:32 UTC: 12978 priced swaps, 28 JIT episodes, 26 lending ops ≥$250k, exchange net $-22.6M stables / $-9.4M ETH
- **25918764** 14:00:23 base 0.05 gwei, 638 txs, Eureka (eurekabuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x31ea…dc20](https://etherscan.io/tx/0x31eaa3c8458c16ffbab1010d1178930ddf2db7bd85e53b178b15843b5667dc20))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x31ea…dc20](https://etherscan.io/tx/0x31eaa3c8458c16ffbab1010d1178930ddf2db7bd85e53b178b15843b5667dc20))
- **25918765** 14:00:35 base 0.05 gwei, 325 txs, bombora.build 
- **25918766** 14:00:47 base 0.05 gwei, 544 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xa671…5380](https://etherscan.io/tx/0xa6714cc617b4e3bd55cc1583908efcaad323c90204ac14620f0076a04d9a5380))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xa671…5380](https://etherscan.io/tx/0xa6714cc617b4e3bd55cc1583908efcaad323c90204ac14620f0076a04d9a5380))
- **25918767** 14:00:59 base 0.06 gwei, 309 txs, Titan (titanbuilder.xyz)
- **25918768** 14:01:11 base 0.06 gwei, 266 txs, BuilderNet
- **25918769** 14:01:23 base 0.06 gwei, 238 txs, Titan (titanbuilder.xyz)
- **25918770** 14:01:35 base 0.05 gwei, 359 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x60a2…1938](https://etherscan.io/tx/0x60a29629a6a1f33cdc3354fe46e3bfa9de14bda1f7f27fb16b1a142d86b01938))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x60a2…1938](https://etherscan.io/tx/0x60a29629a6a1f33cdc3354fe46e3bfa9de14bda1f7f27fb16b1a142d86b01938))
  - JIT 1 episode(s), $101 of swaps bracketed, fees taken $0
- **25918771** 14:01:47 base 0.06 gwei, 369 txs, BuilderNet
- **25918772** 14:01:59 base 0.06 gwei, 205 txs, Titan (titanbuilder.xyz)
- **25918773** 14:02:11 base 0.06 gwei, 327 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918473 to 25918773 at 14:02:27 UTC: 13154 priced swaps, 29 JIT episodes, 25 lending ops ≥$250k, exchange net $-22.1M stables / $-9.4M ETH
- **25918774** 14:02:23 base 0.06 gwei, 267 txs, Titan (titanbuilder.xyz)
- **25918775** 14:02:35 base 0.06 gwei, 75 txs, BuilderNet
- **25918776** 14:02:47 base 0.06 gwei, 145 txs, BuilderNet
- **25918777** 14:02:59 base 0.05 gwei, 563 txs, Titan (titanbuilder.xyz)
  - JIT 1 episode(s), $770 of swaps bracketed, fees taken $3
- **25918778** 14:03:11 base 0.06 gwei, 145 txs, gethgo1.25.10linux
- **25918779** 14:03:23 base 0.05 gwei, 350 txs, Titan (titanbuilder.xyz)
- **25918780** 14:03:35 base 0.05 gwei, 200 txs, Titan (titanbuilder.xyz)
  - swap $2.7M USDT → USDC on curve by [0x1570…7099](https://etherscan.io/address/0x1570bc3abaa351e07fe6f73ea19aa81d7b827099) ([0x2dc9…9669](https://etherscan.io/tx/0x2dc959aa1590c7b1c203a18f51e9ca5f726b7c9b404e91c1fe1436f61f109669))
- **25918781** 14:03:47 base 0.05 gwei, 471 txs,  Quasar (quasar.win) 
- **25918782** 14:03:59 base 0.05 gwei, 197 txs, Titan (titanbuilder.xyz)
- **25918783** 14:04:11 base 0.05 gwei, 416 txs, Eureka (eurekabuilder.xyz)
  - JIT 3 episode(s), $33 of swaps bracketed, fees taken $0
- re-analysed blocks 25918483 to 25918783 at 14:04:26 UTC: 13246 priced swaps, 33 JIT episodes, 25 lending ops ≥$250k, exchange net $-22.4M stables / $-9.3M ETH
- **25918784** 14:04:23 base 0.06 gwei, 270 txs, Titan (titanbuilder.xyz)
- **25918785** 14:04:35 base 0.05 gwei, 292 txs, Titan (titanbuilder.xyz)
- **25918786** 14:04:47 base 0.05 gwei, 110 txs, gethgo1.25.1linux
- **25918787** 14:04:59 base 0.05 gwei, 495 txs,  Quasar (quasar.win) 
- **25918788** 14:05:11 base 0.05 gwei, 131 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xb780…cbd7](https://etherscan.io/tx/0xb780c7b8a3975a278ec122f036d7276a80d982b324135d09086f7900c672cbd7))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xb780…cbd7](https://etherscan.io/tx/0xb780c7b8a3975a278ec122f036d7276a80d982b324135d09086f7900c672cbd7))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x80a6…cc80](https://etherscan.io/tx/0x80a6888b573c84180dd2f3e3f89d4770c645a167d847b23c1eb8eafced47cc80))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x80a6…cc80](https://etherscan.io/tx/0x80a6888b573c84180dd2f3e3f89d4770c645a167d847b23c1eb8eafced47cc80))
- **25918789** 14:05:23 base 0.05 gwei, 71 txs, Titan (titanbuilder.xyz)
- **25918790** 14:05:35 base 0.05 gwei, 722 txs, Eureka (eurekabuilder.xyz)
- **25918791** 14:05:47 base 0.05 gwei, 221 txs, BuilderNet
- **25918792** 14:05:59 base 0.05 gwei, 402 txs, Titan (titanbuilder.xyz)
- **25918793** 14:06:11 base 0.05 gwei, 287 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918493 to 25918793 at 14:06:29 UTC: 13443 priced swaps, 33 JIT episodes, 24 lending ops ≥$250k, exchange net $-21.8M stables / $-9.3M ETH
- **25918794** 14:06:23 base 0.06 gwei, 402 txs,  Quasar (quasar.win) 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xb093…e08f](https://etherscan.io/tx/0xb093339d40ebbb90dddf93b53225abb5e34e190e20a578f1263593fc1425e08f))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xb093…e08f](https://etherscan.io/tx/0xb093339d40ebbb90dddf93b53225abb5e34e190e20a578f1263593fc1425e08f))
- **25918795** 14:06:35 base 0.06 gwei, 234 txs, Titan (titanbuilder.xyz)
- **25918796** 14:06:47 base 0.06 gwei, 230 txs, Titan (titanbuilder.xyz)
- **25918797** 14:06:59 base 0.06 gwei, 264 txs, Titan (titanbuilder.xyz)
- **25918798** 14:07:11 base 0.06 gwei, 288 txs, Titan (titanbuilder.xyz)
- **25918799** 14:07:23 base 0.06 gwei, 59 txs, BuilderNet
- **25918800** 14:07:35 base 0.05 gwei, 340 txs, Titan (titanbuilder.xyz)
  - transfer $6.7M USDT [0x0402…6e14](https://etherscan.io/address/0x04020c290dee056ea509eac517c0c047f28e6e14) → [0x93b1…3fad](https://etherscan.io/address/0x93b13a84d0e99ea80456176e9f2bf0a5a8bb3fad) ([0x9f82…7f3e](https://etherscan.io/tx/0x9f829e944b5afb8b4dedb9cf1e58dede9712502598b50bb98b35980bff4e7f3e))
- **25918801** 14:07:47 base 0.06 gwei, 235 txs, Titan (titanbuilder.xyz)
- **25918802** 14:07:59 base 0.06 gwei, 90 txs, gethgo1.25.1linux
- **25918803** 14:08:11 base 0.05 gwei, 325 txs, Titan (titanbuilder.xyz)
- re-analysed blocks 25918503 to 25918803 at 14:08:32 UTC: 13456 priced swaps, 33 JIT episodes, 21 lending ops ≥$250k, exchange net $-21.5M stables / $-9.1M ETH
- **25918804** 14:08:23 base 0.05 gwei, 372 txs, Titan (titanbuilder.xyz)
- **25918805** 14:08:35 base 0.06 gwei, 282 txs, Titan (titanbuilder.xyz)
- **25918806** 14:08:47 base 0.05 gwei, 280 txs, Titan (titanbuilder.xyz)
- **25918807** 14:08:59 base 0.06 gwei, 235 txs, Titan (titanbuilder.xyz)
- **25918808** 14:09:11 base 0.05 gwei, 543 txs,  Quasar (quasar.win) 
- **25918809** 14:09:23 base 0.06 gwei, 205 txs, Titan (titanbuilder.xyz)
- **25918810** 14:09:35 base 0.05 gwei, 245 txs, Titan (titanbuilder.xyz)
  - JIT 3 episode(s), $30 of swaps bracketed, fees taken $0
- **25918811** 14:09:47 base 0.05 gwei, 235 txs, Titan (titanbuilder.xyz)
- **25918812** 14:09:59 base 0.06 gwei, 262 txs, bombora.build 
- **25918813** 14:10:11 base 0.05 gwei, 100 txs, gethgo1.26.0linux
- re-analysed blocks 25918513 to 25918813 at 14:10:32 UTC: 13395 priced swaps, 35 JIT episodes, 19 lending ops ≥$250k, exchange net $-22.5M stables / $-9.3M ETH
- **25918814** 14:10:23 base 0.05 gwei, 334 txs, Titan (titanbuilder.xyz)
- **25918815** 14:10:35 base 0.05 gwei, 385 txs,  Quasar (quasar.win) 
- **25918816** 14:10:47 base 0.06 gwei, 178 txs, bombora.build 
- **25918817** 14:10:59 base 0.05 gwei, 272 txs, Titan (titanbuilder.xyz)
- **25918818** 14:11:11 base 0.05 gwei, 198 txs, BuilderNet
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x6acd…7528](https://etherscan.io/tx/0x6acd40e395b2117055283e6fe3369f4e007bae65bf392fb452609cf4dd247528))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x6acd…7528](https://etherscan.io/tx/0x6acd40e395b2117055283e6fe3369f4e007bae65bf392fb452609cf4dd247528))
- **25918819** 14:11:23 base 0.05 gwei, 268 txs, Titan (titanbuilder.xyz)
- **25918820** 14:11:35 base 0.05 gwei, 175 txs, reth/v2.3.0/linux
- **25918821** 14:11:47 base 0.05 gwei, 504 txs, BuilderNet
- **25918822** 14:11:59 base 0.06 gwei, 323 txs, Titan (titanbuilder.xyz)
- **25918823** 14:12:11 base 0.06 gwei, 145 txs, 0x0e33…87c2
- re-analysed blocks 25918523 to 25918823 at 14:12:33 UTC: 13483 priced swaps, 34 JIT episodes, 19 lending ops ≥$250k, exchange net $-25.3M stables / $-10.8M ETH
- **25918824** 14:12:23 base 0.05 gwei, 361 txs, Titan (titanbuilder.xyz)
- **25918825** 14:12:35 base 0.06 gwei, 347 txs,  Quasar (quasar.win) 
- **25918826** 14:12:47 base 0.06 gwei, 116 txs, gethgo1.26.4linux
- **25918827** 14:12:59 base 0.05 gwei, 279 txs, Builder+ www.btcs.com/builder
- **25918828** 14:13:11 base 0.05 gwei, 162 txs, 0x123b…a806
- **25918829** 14:13:23 base 0.05 gwei, 146 txs, BuilderNet
- **25918830** 14:13:35 base 0.05 gwei, 252 txs, Titan (titanbuilder.xyz)
  - transfer $440.8M WBTC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $440.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $106.1M USDC [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $106.1M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $27.5M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $27.5M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.8M WBTC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.8M WBTC [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.7M WETH [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.7M WETH [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.7M WETH [0xbb2b…d940](https://etherscan.io/address/0xbb2b8038a1640196fbe3e38816f3e67cba72d940) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.7M USDC [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) → [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
  - transfer $13.7M USDC [0xb4e1…c9dc](https://etherscan.io/address/0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc) → [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ([0x33de…82dd](https://etherscan.io/tx/0x33de7901b503c6983a5df564a03d3a5f4b53f2ba0dbe1a8be77756078d5682dd))
- **25918831** 14:13:47 base 0.05 gwei, 560 txs, Titan (titanbuilder.xyz)
- **25918832** 14:13:59 base 0.05 gwei, 241 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0x218f…aeda](https://etherscan.io/tx/0x218f4db1fc368c68f58ba9ef2f62cdf12615f05d79a3d0f6b785aefc330caeda))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x218f…aeda](https://etherscan.io/tx/0x218f4db1fc368c68f58ba9ef2f62cdf12615f05d79a3d0f6b785aefc330caeda))
- **25918833** 14:14:11 base 0.05 gwei, 372 txs,  Quasar (quasar.win) 
- re-analysed blocks 25918533 to 25918833 at 14:14:28 UTC: 13538 priced swaps, 32 JIT episodes, 19 lending ops ≥$250k, exchange net $-30.9M stables / $-14.1M ETH
- **25918834** 14:14:23 base 0.05 gwei, 237 txs, Titan (titanbuilder.xyz)
- **25918835** 14:14:35 base 0.05 gwei, 275 txs, Titan (titanbuilder.xyz)
- **25918836** 14:14:47 base 0.05 gwei, 185 txs, Titan (titanbuilder.xyz)
- **25918837** 14:14:59 base 0.05 gwei, 299 txs,  Quasar (quasar.win) 
- **25918838** 14:15:11 base 0.05 gwei, 190 txs, Titan (titanbuilder.xyz)
- **25918839** 14:15:23 base 0.05 gwei, 454 txs, Titan (titanbuilder.xyz)
- **25918840** 14:15:35 base 0.05 gwei, 421 txs,  Quasar (quasar.win) 
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ([0xa610…795e](https://etherscan.io/tx/0xa610d9b7fb30a276c10a65f25ccc73a9781a0ab3a889d60b817ce77447c8795e))
  - transfer $25.0M WETH [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xa610…795e](https://etherscan.io/tx/0xa610d9b7fb30a276c10a65f25ccc73a9781a0ab3a889d60b817ce77447c8795e))
- **25918841** 14:15:47 base 0.05 gwei, 272 txs, Titan (titanbuilder.xyz)
- **25918842** 14:15:59 base 0.05 gwei, 287 txs,  Quasar (quasar.win) 
- **25918843** 14:16:11 base 0.05 gwei, 303 txs, Titan (titanbuilder.xyz)
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0x8c88…0b09](https://etherscan.io/tx/0x8c8841f6a482de8fbcf712b79ca9fae017b4a8852787296f183e19e673870b09))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0x8c88…0b09](https://etherscan.io/tx/0x8c8841f6a482de8fbcf712b79ca9fae017b4a8852787296f183e19e673870b09))
  - transfer $25.0M WETH [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) → [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ([0xffd7…8b72](https://etherscan.io/tx/0xffd7be03d590987a20e521bf7b792c143a5bc7e2dd7c41636166757dfd298b72))
  - transfer $25.0M WETH [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) → [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ([0xffd7…8b72](https://etherscan.io/tx/0xffd7be03d590987a20e521bf7b792c143a5bc7e2dd7c41636166757dfd298b72))
- **25918844** 14:16:23 base 0.05 gwei, 222 txs, Nethermind v1.36.0

