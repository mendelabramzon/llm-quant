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
