# Where the dollar yield sits on mainnet right now

Live-scan follow-up, Sunday 6 September 2026, written by Claude (Fable 5.1) between 13:30 and 14:30 UTC while the live tailer kept running. The question was "find interesting market opportunities" in the live block stream. The morning session had already shown that price space is efficient and that same-asset rate gaps on Aave/Compound have small capacity; this pass looks where the morning did not: Morpho Blue's 228 isolated markets and Pendle's 45 fixed-rate markets, joined on the Pendle principal tokens that Morpho accepts as collateral.

State is pinned at finalized block **25,918,580 (13:23:35 UTC)** for every Morpho and Pendle read (`snapshot.json`); the head-state refresh of the live scanner is at 25,918,661 (13:39:47 UTC); one follow-up read is at 25,918,707 (13:48:59 UTC) and is labelled as such. Every number below is in [tables.md](tables.md), `morpho_markets.json`, `pendle_markets.json`, `../live/head_state.json` or the live log; the reading of them is mine and carries a stated confidence. Nothing was signed or broadcast.

## Summary, ranked by how clean the edge is

1. **Fixed beats floating on the safest savings tokens (high confidence on the numbers, small size).** PT-sUSDS-26NOV2026 pays 4.97% fixed against a 3.60% Sky savings rate on the same USDS: +137 bps, $2,913 per $1M over the 80 days to maturity before Pendle fees, in a $3.5M pool. PT-sUSDE-26NOV2026 pays 4.91% against Ethena's 4.43% vesting APR: +48 bps. PT-stETH-30DEC2027 is the mirror case at 2.06% fixed against 2.23% realized: fixed is below floating there.
2. **Spark's liquidity layer just made Morpho the cheapest place to borrow USDT (high confidence, measured before and after).** At 13:28 UTC it moved $25.5M USDT from Spark Savings USDT into its Morpho "Blue Chip USDT" vault. USDT/wstETH borrow APY fell from 3.53% to 3.12% and USDT/WBTC from 3.74% to 3.14%, with $24.2M and $17.2M withdrawable, while Aave USDT borrow is 4.26%. A $10M USDT borrow against wstETH costs about 3.35% on Morpho today (IRM curve, not a fork test): roughly $90k a year less than Aave.
3. **Morpho's dollar markets form a risk ladder with measurable capacity per rung (high confidence).** Aave USDC 3.59% → Morpho blue-chip collateral 4.29% size-weighted on $516M → RWA and second-tier stable collateral 5.4% to 6.5% → PT carry loops 20% to 34% levered. The safe rung's marginal capacity is small: +$10M into the $336M USDC/cbBTC market earns 3.80%, $55 a day over Aave; the crossover with Aave is near +$20M.
4. **No PT market on Morpho over-credits its collateral (high confidence).** In all 19 PT markets the oracle price is at or below the Pendle market price; the linear-discount oracles under-credit by 1% to 5%, so effective loan-to-value on market value is 82% to 91% rather than the nominal 86% to 94.5%.
5. **Thin-market spikes exist but are tiny:** DAI/sUSDe (LLTV 0.915) pays 10.5% on $592k; USDC/srRoyUSDC pays 40% at 99.9% utilisation because nobody will lend against that collateral.
6. **The big live alerts of the afternoon were mostly mechanics, not flow:** Morpho flash loans, Lido's daily oracle report, an $8 vault-rounding arbitrage on an $80.9M flash loan. The real flows were Spark's allocation, a $12.6M USDC burn by Coinbase, ETH leaving exchanges at about $9M an hour, and one WETH seller working a $58k clip every six minutes.

## 1. Fixed versus floating on the same asset

Pendle principal tokens (PT) redeem 1:1 into the underlying asset at maturity. The PT price is read from Pendle's on-chain PY/LP oracle as a 15-minute TWAP, and `getOracleState` confirmed the observation window is populated for every market (`TWAP ok` column). The implied APY is (1/price)^(365/days) − 1. The public Pendle API is stored as a cross-check only; its implied APY matched the on-chain read to the basis point in every market, which is a useful validation of the reader, not a data source.

| PT | days | PT/asset | implied fixed APY | floating comparison | source of floating | hold-to-maturity extra per $1M |
|---|---|---|---|---|---|---|
| PT-sUSDS-26NOV2026 | 80.4 | 0.98938 | **4.97%** | 3.60% APY | Sky `ssr`, head state | **+$2,913** |
| PT-sUSDE-26NOV2026 | 80.4 | 0.98950 | **4.91%** | 4.43% APR | sUSDe vesting, head state | **+$1,016** |
| PT-stETH-30DEC2027 | 479 | 0.97353 | 2.06% | 2.23% APR | Lido rebase at 12:00 UTC, block 25,918,274 | −$2,226 |
| PT-USDG-24SEP2026 | 17 | 0.99825 | 3.73% | not read | | |
| PT-srUSDe-22OCT2026 | 45 | 0.99350 | 5.38% | not read | | |

The sUSDS case is the interesting one. The underlying is the same USDS credit either way; the difference is that the savings rate is set by Sky governance and can move, while the PT locks 4.97% for 80 days. The market is pricing either an expected rise in the savings rate or a term premium; the trade is short enough that the second explanation is the likelier one. Pendle swap fee and price impact are not netted: the pool holds $3.5M (API figure), so a $1M order takes a real part of the 137 bps, and the position should be built in clips. Exit before maturity means selling the PT back into the same pool; holding to maturity means redeeming PT → sUSDS → USDS, which is atomic after expiry. This is a term-premium trade, not an arbitrage: Pendle contract risk is added on top of USDS risk.

The other implied yields in the table run from 5% to 25% on second-tier stables (USDx, sUSDx, reUSDe, USD3, apyUSD, STRCx). Those are not term premia; they are the market's price of each issuer's credit and of the points programmes attached to them. PT-ROY-JT-apyUSD at 289% is a junior tranche whose SY exchange rate has fallen below 1 (0.8407), so the number is a distressed price, not a yield.

**Levering the sUSDS trade on Morpho.** The USDS/PT-sUSDS market lends USDS at 3.52% against the PT (LLTV 0.915, effective 90.4% on market value): carry 1.45%, 8.75% at 80% of LLTV, but only $274k of USDS is available to borrow. The USDC/PT-sUSDS market has $1.7M available but borrows at 4.56%, leaving 0.41% of carry; USDT/PT-sUSDS is flat. The loop is real and small.

## 2. Spark's allocation and the borrow window it opened

The live tailer flagged a $25.5M USDT chain at block 25,918,603 (13:28:11 UTC, tx `0xc8e5…e794`). Decoded:

- The sender is a Safe (`0x8a25a24e…`) executed by `0x062ce42c…`, drawing on a Sky allocator vault with ilk `ARK-A`, whose ALM proxy is `0x1601843c…` (the same account holds $55.0M of collateral and no debt on SparkLend).
- USDT came out of **Spark Savings USDT** (`spUSDT`, `0xe2e7a17d…`) and went into the **Spark Blue Chip USDT Vault** (`sparkUSDTbc`, `0xb0c42411…`, a Morpho vault with an adapter at `0xef4cb7e8…`), which supplied four Morpho markets: USDT/wstETH $13.30M, USDT/WBTC $9.85M, USDT/sUSDS $2.27M, and $61k to a market outside the discovery set.

Effect, read from the deployed IRM before (block 25,918,580) and after (block 25,918,707):

| market | supplied before → after | utilisation | borrow APY | supply APY | withdrawable now |
|---|---|---|---|---|---|
| USDT/wstETH (LLTV 0.86) | $110.5M → $123.8M | 90.1% → 80.5% | **3.53% → 3.12%** | 3.19% → 2.51% | $24.2M |
| USDT/WBTC (0.86) | $76.1M → $86.0M | 90.3% → 79.9% | **3.74% → 3.14%** | 3.38% → 2.51% | $17.2M |
| USDT/sUSDS (0.965) | $19.8M → $22.1M | 90.4% → 81.1% | 3.72% → 3.10% | 3.36% → 2.51% | $4.2M |

Aave USDT borrow is 4.26% and Compound USDT 3.81% at the same time. Morpho was already the cheapest USDT on mainnet against blue-chip collateral; the allocation widened the gap to 114 bps. The Adaptive Curve IRM closes it from both sides: borrowers who take the liquidity push utilisation back toward 90% (a $10M borrow against wstETH lifts utilisation to 88.6% and the rate to about 3.35%), and while utilisation sits at 80% the rate-at-target itself decays at roughly 1.4% a day relative. So this is a window measured in days, opened by a scheduled allocator whose deposits the live scanner sees the block they land. That is the loop-shaped finding of the afternoon: **a large Morpho vault deposit is a borrow signal**, and the post-deposit rate is one IRM call away.

## 3. The ladder: Morpho rates by loan asset and collateral

228 markets were read; 103 hold at least $1M; the dollar-stable markets hold $2.2B. Because the Adaptive Curve IRM targets 90% utilisation in every market, nearly every market sits at 89% to 91% and the rate is what borrowers of that collateral are willing to pay. The size-weighted picture against the pooled venues (head state 13:39 UTC):

| loan asset | Morpho blue-chip collateral (cbBTC, WBTC, wstETH, WETH, weETH, rETH, LBTC, tBTC, kBTC) | Morpho all markets ≥ $1M | Aave v3 | SparkLend | Compound v3 |
|---|---|---|---|---|---|
| USDC | 4.29% on $516M ($52M free) | 5.10% on $937M | 3.59% | 3.54% | 4.82% |
| USDT | 3.28% on $217M ($21M free) | 3.35% on $321M | 3.57% | 2.62% | 2.99% |
| PYUSD | 3.62% on $207M | 4.79% on $582M | 3.72% | 0.58% | – |
| RLUSD | 3.14% on $307M | 3.21% on $323M | 2.17% | 0.00% | – |

Reading it as an allocator:

- **USDC.** Blue-chip Morpho pays 70 bps over Aave, but the rung is shallow. The scanner re-calls the IRM with the supply enlarged: USDC/cbBTC ($336M) goes 4.28% → 3.98% (+$1M) → 3.80% (+$10M) → 3.61% (+$20M) → 3.13% (+$50M). Over Aave's 3.59% that is $10, $55, $8 and −$631 a day. Spreading $1M into each of ten blue-chip markets is at most about $100 a day on $10M, since the smaller markets dilute faster. Compound USDC at 4.82% is still the best small-size home for USDC (the morning screen put its useful capacity at $0.83M). The extra 70 bps also buys a different risk: one collateral, one oracle, 86% LLTV, no safety module, and bad debt socialised to that market's lenders.
- **USDT.** Morpho pays *less* than Aave on the supply side (3.28% versus 3.57%) and charges less on the borrow side; that is what a liquidity layer that supplies $25M at a time does. A USDT lender should be on Aave; a USDT borrower with wstETH or WBTC collateral should be on Morpho (section 2).
- **PYUSD.** $582M is lent on Morpho, three quarters of it against three collaterals: Hastra PRIME ($194M at 5.70%), Kraken kBTC ($135M at 3.10%) and sUSDe ($88M at 5.83%). PYUSD/PRIME pays 5.70% now, 5.02% after +$1M and 4.16% after +$10M; Aave PYUSD is 3.72%. PRIME is a Hastra token whose liquidation path is not established here; the rate is the market's price for that. The morning's Aave PYUSD reserve at 23% has normalised to 3.72% at 85.9% utilisation.
- **The upper rungs.** USDC against PayFi Strategy Token (PST) 5.06%, Midas Fasanara ONE 5.45%, Pareto FalconX tranche 5.38%, USD3 5.73%, Re Protocol reUSD 5.54%, Origin OETH 6.85%, dCOMP 9.05%, apyUSD 8.84%, Midas M1 9.26%. Every one of these is a lender pricing an RWA or synthetic-dollar issuer; none is a free spread. Capacity is small: +$1M typically drops the rate by 0.5 to 2 points.
- **wARS** markets (Argentine peso stable) pay 17% to 24% to lenders and charge 20% to 26% to borrowers who post USDC, USDT, wstETH or WBTC to short the peso. It is the on-chain peso carry; a dollar lender earns it only if the peso holds.

## 4. Oracle audit on PT collateral

Morpho markets on PT collateral use either the Pendle TWAP itself or a linear-discount oracle that prices the PT at 1 minus a fixed annual discount times time to maturity. The join shows which is which and what it means for credit:

| loan / PT | market PT/asset | Morpho oracle | oracle ÷ market | effective LLTV on market value |
|---|---|---|---|---|
| USDC / PT-USD3-17DEC2026 | 0.96453 | 0.91662 | 0.950 | 81.7% (nominal 86%) |
| USDC / PT-strUSD-26NOV2026 | 0.97571 | 0.94834 | 0.972 | 83.6% |
| USDC / PT-trUSD-26NOV2026 | 0.97899 | 0.95054 | 0.971 | 91.8% (nominal 94.5%) |
| USDC / PT-sUSDS-26NOV2026 | 0.98938 | 0.97135 | 0.982 | 89.8% |
| USDC / PT-reUSD-10DEC2026 | 0.97362 | 0.97362 | 1.000 | 91.5% |
| USDC / PT-sUSDE-26NOV2026 | 0.98950 | 0.98678 | 0.997 | 91.2% |

No ratio exceeds 1.000, so no PT market on Morpho hands out more credit than the PT is worth on Pendle today. For lenders that is the reassuring finding; for borrowers it means the nominal LLTV overstates the leverage available. It also removes one hoped-for edge: there is no "borrow against an oracle that is richer than the market" position to take.

The PT carry table in `tables.md` ranks all 19 markets by fixed yield minus borrow cost. The top rows (PT-srUSDat 7.9% carry, apxUSD/PT-apyUSD 7.7%, USDC/PT-USD3 7.0%, AUSD/PT-reUSD 6.8%) are all second-tier issuers, and their levered figures of 27% to 34% at 80% of LLTV are the yield the market pays for holding that issuer's credit at 3x to 4x. The largest liquid one is USDC/PT-reUSD-10DEC2026 ($12.4M available, carry 3.4%, 20% levered).

## 5. Thin-market spikes and stuck markets

- **DAI/sUSDe, LLTV 0.915**: 11.33% borrow, 10.50% supply on $592k at 92.6% utilisation, $43k withdrawable. Blue-chip collateral, small pot: $200k of new supply takes utilisation to 69% and the supply APY to about 6.5% (IRM curve), still double Aave DAI's 3.03%. Worth a standing bid at that size, nothing more.
- **USDC/srRoyUSDC**: 40.08% borrow at 99.9% utilisation, $1.9k free. Lenders cannot withdraw; the IRM raises rate-at-target about 15% a day relative while utilisation stays at 100%. Nobody supplies because the collateral (Senior Royco USDC, oracle 1.028) has no liquidation path anyone trusts. This is what a stuck Morpho market looks like, and the reason the utilisation table in `tables.md` should be read with the collateral in mind.
- **AUSD/sUSDat** pays 9.25% on $8.0M, 7.50% after +$1M.

## 6. What the afternoon's big alerts really were

The live log for 10:06 to 13:46 UTC carried 242 transfer alerts of $5M or more. Decoded, most were mechanics:

- The repeating **$25.0M WETH round trips** through `0xbbbb…ffcb` are Morpho flash loans of two cycle-arbitrage contracts (the same pattern the earlier session traced to $38 of profit on five loans).
- The **$80.9M WBTC round trip** (block 25,918,371, tx `0x261c…067d`) is a 1,011 WBTC Morpho flash loan that deposits into and redeems from a WBTC vault (`0xb40dc920…`) and keeps 0.0001 WBTC, about $8.
- The **$17.7M stETH transfer** (block 25,918,274) is inside Lido's daily oracle report: the rebase event in that transaction gives a user APR of 2.232% for the 86,400-second frame, which is the floating leg used in section 1.
- The **$13.8M WBTC / $13.7M WETH / $13.7M USDC** triangles by `0x0fd3…c83d` recurred three times in the window and are one contract's round trips inside single transactions (not decoded further).
- Real flows: **Spark's $25.5M** (section 2); **Coinbase 11 burned $12.6M USDC** at 13:45 UTC; **Binance 15 sent 3,000 ETH ($7.5M)** to an unlabeled address at 13:29; exchange net flow over the trailing hour was −$9.1M ETH and about flat in stables; **`0x9eb9e9b2…` sold WETH for USDC in five $58k clips six minutes apart** on Uniswap v3 (a TWAP, the only scheduled programme in the window); sUSDe trades 4.2 bps under NAV (tighter than the 5 to 9 bps of the day study); three sUSDe cooldowns for $362k.
- Data quality: the 33-events-per-block emitter `0xc10fc8fa…` (topic `0xf57b0de3…`, 12,895 events in the last hour, no ERC-20 interface) is still unlabeled and is the largest undecoded log source; XEN (`0x06450dee…`) accounts for the next two topics; `0x49628fd1…`/`0xbb47ee3e…` are ERC-4337 EntryPoint v0.7 and v0.8 user operations.

## 7. What was not verified, and what to do next

Not verified: Pendle fees and price impact at size (quotes were not pulled); the liquidation liquidity of PRIME, PST, kBTC, USD3, reUSD and the other RWA collaterals; the identity of the `ARK-A` allocator beyond the on-chain naming of its vaults; the borrow-side post-borrow rate (computed from the IRM curve, not from a state-modified call like the supply side). The supply-side simulation holds rate-at-target fixed; the IRM's drift over the following days is described, not simulated. Morpho's supply APY is borrow APY × utilisation × (1 − fee), which is exact at the instant read.

Requests to the quant step, in order:

1. Wire large Morpho `Supply`/`Withdraw` events (vault adapters, ≥ $5M) into the live tailer with the IRM rate before and after, so allocator flow becomes a standing borrow-window alert.
2. Daily series of PT-sUSDS and PT-sUSDE implied APY against the Sky savings rate and the Ethena vesting APR; alert when the premium exceeds 100 bps.
3. Pendle exact-size quotes (router `swapExactTokenForPt`) at $100k / $500k / $1M for the two blue-chip PTs, to net fees and impact against the term premium.
4. Fork test of the USDS/PT-sUSDS loop at $200k (the liquidity cap) with a one-day hold, in the style of `non_mev/fork`.
5. Label `0xc10fc8fa…` and the Hastra PRIME / PST / kBTC liquidation paths before any lending at the upper rungs.

## Reproduction

```sh
# pinned replay of this snapshot (block from snapshot.json; raw/ cache; no network needed after the first run)
uv run --with pycryptodome --with eth-abi python scripts/morpho_pendle_scan.py --offline

# a new snapshot at the current finalized block, in a new directory
uv run --with pycryptodome --with eth-abi python scripts/morpho_pendle_scan.py --out research/<date>/opportunities --sizes 1e6,5e6,1e7,2e7,3e7,5e7
```

Inputs: `discovery.json` (228 Morpho market ids from the day study plus the live logs; 17 Pendle markets that traded in the live window), `pendle_api.json` (cross-check list), `raw/` (every RPC response, keyed by request hash), `../live/head_state.json` (Aave, SparkLend, Compound, Sky, Ethena reads at 25,918,661). Public RPC only (dRPC, publicnode); no Infura credits were used by the scanner.
