# Profit without transaction-ordering races

Ethereum mainnet, finalized block **25,918,293**, **6 September 2026, 12:25:59 UTC**. This is a pinned research snapshot, not an executable current quote. The working sizes are $100k and $1M because no capital amount was specified.

**The strongest fit is an unleveraged allocator of the same asset across lending venues, sized using the rate after our deposit.** A real USDC rate gap exists, but its attractive capacity is approximately $0.83M in this snapshot, not the $10M–$50M suggested by the earlier memo. Larger idle-capital improvements exist for holders earning very low rates on USDS and PYUSD. The sUSDe cooldown trade is currently too marginal to justify its exit-price exposure.

These strategies earn from holding capital over time. They do not need a sandwich, a backrun, first liquidation access, or a builder payment. Other suppliers can still compete away their returns. Nothing found establishes guaranteed profit or a durable high-return business on small capital.

## 1. USDC: a real gap with a surprisingly small capacity

The contracts read as follows:

| Market | Current supply APR | Historical comparison |
|---|---:|---|
| Aave v3 USDC | 3.5971% | Actual income-index growth annualizes to 3.6013% over six hours and 3.8127% over 24 hours |
| Compound v3 USDC | 4.8732% | Spot rate was 5.3178% six hours earlier and 4.4517% 24 hours earlier |

The historical Compound observations are two spot samples, not a time-weighted return or proof that the spread remained positive continuously. Aave's observations are realized accrual for a continuously held aToken. They are different measurements.

Compound's supply curve is steep near the current utilization. New supply lowers utilization and the rate paid on the entire new position. Calling `getSupplyRate()` at the resulting utilization gives:

| USDC moved from an existing, withdrawable Aave position | Compound APR after deposit | Extra income/day over staying in Aave | Extra income over seven days, after gas budget |
|---:|---:|---:|---:|
| $10,000 | 4.8655% | $0.35 | $2.09 |
| $100,000 | 4.7957% | $3.28 | $22.64 |
| $1,000,000 | 4.0996% | $13.77 | $96.02 |
| $10,000,000 | 3.1733% | **−$116.11** | **−$813.14** |

These are constant-rate scenarios, not forecasts. They exclude infrastructure, taxes, and losses from protocol or issuer events. The combined execution budget is 600,000 gas, using this block's base fee plus 0.1 gwei and its Chainlink ETH/USD mark: **$0.346**. It is a budget, not an estimated or paid live transaction fee. Aave-held collateral backing debt is not freely movable.

The objective is `amount × (destination_rate_after_deposit − source_rate)`, not the highest displayed APR. A $10k-spaced grid peaks at **$830,000**, paying about **4.2308%**, or **$14.41/day extra** relative to the current Aave rate. This is roughly $5,260 at an unchanged annual run rate; it is not a one-year profit forecast. Adding approximately $10M can make this trade worse than doing nothing.

This behavior follows Compound's separate utilization-based supply curve, which was reconstructed from its on-chain parameters and checked against the deployed `getSupplyRate()` for all seven tested sizes. [Compound interest-rate documentation](https://docs.compound.finance/interest-rates/).

**Fork verification:** five tests passed against deployed contracts at the same block. For a fresh $1M funded deposit, one day on an unchanged fork produced **112.317973 USDC** on Compound versus **98.465658 USDC** on Aave: **13.852315 USDC extra before gas**. This differs slightly from the table because a fresh Aave deposit also dilutes Aave's rate; the table's baseline is an already-held Aave position. Both paths actually withdrew their balance in the fork.

The adverse test adds another supplier's $10M after one hour. Our Compound income then falls to **87.780696 USDC**, below the Aave alternative. The test proves that positive entry carry does not lock future profit. Funding is assigned with a test cheatcode; future blocks contain no organic activity unless explicitly simulated. [Test source](fork/test/PatientSupply.t.sol), [complete output](fork_proof.txt).

## 2. Other same-asset inefficiencies

These are conditional improvements for capital already held at the source, not a reason to buy every token in the table. Current-rate savings are measured against the source's current rate, with the destination diluted by the proposed deposit.

| Existing position → destination | Size | Source APR → destination APR after deposit | Extra income/day before gas |
|---|---:|---:|---:|
| SparkLend USDT → Aave USDT | $1M | 2.6186% → 3.5635% | $25.89 |
| SparkLend USDT → Aave USDT | $10M | 2.6186% → 3.5420% | $252.98 |
| Compound USDT → Aave USDT | $1M | 2.9926% → 3.5635% | $15.64 |
| SparkLend PYUSD → Aave PYUSD | $100k | 0.5793% → 3.6373% | $8.38 |
| SparkLend PYUSD → Aave PYUSD | $1M | 0.5793% → 2.9994% | $66.30 |
| SparkLend DAI → Aave DAI | $1M | 2.4592% → 2.9825% | $14.34 |

The exact unrounded values are in `all_same_asset_routes` in [evidence.json](evidence.json). Source cash, destination supply caps, asset identities/decimals, active/frozen/paused flags, and rate parameters were read. Wallet ownership, debt constraints, approvals, and future withdrawal liquidity were not established. Aave allows withdrawal only within available account and reserve constraints. [Aave Pool documentation](https://aave.com/docs/aave-v3/smart-contracts/pool).

Two cautions are supported by the actual accrual history:

- Spark USDT's **24-hour realized supply rate annualizes to 4.7005%**, despite the 2.6186% current quote. A strategy that traded from yesterday's average would choose differently. The present gap may be short-lived.
- Aave PYUSD's **24-hour realized rate annualizes to 4.8362%**, and its current rate is 3.7216%. The earlier 23% alert was a transient rate, not a sustained return. Our $1M deposit would cut today's rate to approximately 3.0%.

**USDS provides a larger idle-capital improvement.** Aave has about **11.28M USDS supplied**, earning only **0.1231% APR**. The sUSDS savings contract reports **3.6000% APY**; its `asset()` is USDS, and the queried unrestricted address's `maxDeposit()` returns the maximum uint256. The fork deposited 1M USDS, waited one day at unchanged governance settings, and redeemed **1,000,096.900979 USDS**. That is approximately **$93.53/day more** than the current Aave USDS accrual, assuming USDS at parity and the position can be moved.

This is ordinary savings yield and idle-capital optimization, not a pricing arbitrage. The savings rate is governance-set; USDS, protocol, and redemption risks remain. APY and APR are intentionally distinguished: the one-day fork accrual is used for the dollar comparison. The savings vault is `0xa3931d71877c0e7a3148cb7eb4463524fec27fbd`.

## 3. Midnight USDC withdrawal: real, but only a few dollars per million

The observed entity withdrew **151M USDC** at **23:34:35 UTC** and re-supplied it at **00:08:23 UTC**. The borrow rate briefly approached 14.30% from approximately 4.27%.

I independently re-requested and matched all **74 reserve-rate events** from the saved 75-minute window. Within a block/timestamp, only the final rate applies to subsequent elapsed time; temporary flash-loan spikes must not be averaged as if they persisted. There are 64 distinct event timestamps. The integrated excess over the pre-event baseline was:

| Effect of this episode | Per $1M | Basis points of principal |
|---|---:|---:|
| Extra supplier interest | **$5.95** | **0.05955 bps** |
| Extra variable-borrow cost | **$6.44** | **0.06437 bps** |

Independent before/after income and debt indexes agree with those integrals within $0.001 per million. [Midnight evidence](midnight.json).

The old narrative's **0.8 bps/day** borrower figure is about **12.4× too high**. Repeating this observed episode every day would add approximately **0.235 percentage points/year** to borrowing cost; two observed nights do not establish that future recurrence.

Use this for scheduling existing debt or liquidity, not as the main profit engine. A supplier needs roughly $58k just to cover the $0.346 gas budget from this episode's excess interest, before its own rate impact or other costs. A borrower must include the cost of replacement funding or the foregone yield on cash used for repayment. Large new deposits or repayments also suppress the spike. Supply in advance and exit when normal liquidity returns; chasing its first block would reintroduce timing competition.

## 4. sUSDe redemption: reject the current trade at meaningful size

The protocol still reports a **86,400-second cooldown**. The two Curve pools' coin order, sDAI and sUSDe underlying assets, exact-size entry quote, `previewRedeem()`, and exact-size USDe→USDT exit quote were checked at the same block.

| Starting sDAI, valued in redeemable DAI | Quoted proceeds minus cost, before carry/gas | After 5% annual capital charge and gas budget |
|---:|---:|---:|
| $10,000 | +$1.91 | +$0.20 |
| $100,000 | +$10.72 | **−$3.32** |
| $250,000 | −$31.33 | **−$65.92** |
| $500,000 | −$127,323.03 | **−$127,391.87** |

The last row exposes the shallow **specific exit pool**, not all global USDe liquidity. At that size its USDe→USDT quote deteriorates drastically. The entry is sDAI valued in DAI, while the exit is USDT: the table assumes parity, has no DAI/USDT basis hedge, and does not include acquiring starting sDAI. Today's exit quote also does not guarantee tomorrow's price. A mere 10 bps adverse exit move turns the $10k case into a roughly **$9.81 loss** after carry and gas.

The cooldown converts shares into a claim on **USDe**, not guaranteed USD. The dynamic cooldown policy can change, and unstaking locks the claim for the applicable period. [Ethena staking security mechanics](https://docs.ethena.fi/solution-design/staking-usde/user-security-measures), [2026 governance update](https://gov.ethenafoundation.com/t/ethena-s-march-and-april-2026-governance-update/791).

Keep this as a dislocation watchlist. Entry should require an exact-size projected surplus exceeding the capital cost, an explicit exit-price stress, all execution costs, and a meaningful minimum profit. No artificial stressed seller is included in the numbers above. Previous fork tests that first created a selloff demonstrate a possible mechanism, not a currently available opportunity.

## 5. Corrections that change strategy selection

- **Cooldown does not exclude MEV operators.** A firm can maintain inventory and compete for the discounted entry even when settlement takes days. Time exposure changes the financing requirement; it does not guarantee uncontested access.
- **Low priority fee does not establish low competition.** The separate [five-transaction reconstruction](../weth_roundtrips/findings.md) found $73.29 in direct builder payments against $111.87 gross trading proceeds, despite zero priority fees. Do not copy the conspicuous flash-loan bots based on gas tips.
- **Flash principal is not profit or accessible capacity.** A permissioned fee waiver, repayment obligation, collateral requirement, or inclusion constraint can matter. Free flash liquidity cannot finance a multi-day position.
- **A stablecoin yield spread is not automatically a leveraged arbitrage.** Collateral consumes capital, rates change at both venues, and different stablecoins introduce basis exposure. This screen takes no leverage and assumes no borrow/supply loop.
- **An ETH short does not hedge a USDe-specific depeg.** It is not included as protection in these calculations.

## 6. What to implement and operate

Use the included read-only scanner as the research component of a **same-asset cash allocator**. Its output covers nine improving source/destination routes at the observed spot rates and includes their post-deposit economics; some sizes within an otherwise promising route are negative.

1. Keep observations every 15–60 minutes and record each proposed decision before seeing later returns. A fresh output directory pins a new finalized snapshot. The current artifact is one snapshot with historical checks, not an ongoing service.
2. Rank incremental income at our actual size, subtracting both entry and exit costs. Limit exposure by available source cash, destination deposit headroom, portfolio concentration, and a separate withdrawal-liquidity buffer. Protocol-wide cash is not a guarantee that our funds remain withdrawable.
3. Require persistence and a profit floor. For example, the $100k USDC move earns only about $22.64 over seven unchanged days after the gas budget; a recurring operational cost can consume that. At $1M, allocating approximately $0.83M maximizes this snapshot's incremental USDC income, with the remainder at the baseline venue.
4. Track realized interest, rate changes caused by our deposits, time stuck in a position, and total fees. Exit or resize when the marginal advantage disappears. The adverse fork test supplies an explicit example of that failure mode.
5. Paper-trade for at least a week before deciding whether the observed dollars justify operation. Compare against a fixed same-asset baseline; don't annualize a single favorable hour into a promised return.

For capital below $100k, the observed USDC optimization is only a few dollars per day at best. For larger capital, the useful edge is careful allocation and avoiding idle balances; the current evidence does not support a scalable high-return arbitrage independent of market risk.

## Evidence and reproduction

The new work is isolated here and in [scripts/non_mev_screen.py](../../../scripts/non_mev_screen.py). Existing strategy notes and scanner files were preserved.

- [evidence.json](evidence.json): 12 Aave/Spark reserves, two Compound markets, same-asset routes, savings state, exact-size redemption quotes, and assumptions.
- [raw/](raw/): 265 request records including successful responses and retrieval/unsupported-method errors. Contract state uses public RPC; a bounded fallback uses existing local Infura configuration for historical logs. No keys are stored.
- [sha256.json](sha256.json): raw-record hashes. Historical block hashes and the finalized snapshot hash are retained. These are RPC observations, not local consensus verification.
- [validation.json](validation.json): byte-identical offline replay, all raw hashes checked, 74 matched historical logs, 12 rate-curve checks, and the five passing fork tests.
- [fork/test/PatientSupply.t.sol](fork/test/PatientSupply.t.sol): five economic tests, including size dilution, exit, later competing supply, and same-underlying savings redemption.
- [fork_proof.txt](fork_proof.txt): five passes with measured token returns. Foundry 1.5.1; forge-std commit `df98778116f87d110af4ec37ca529a6aec917c74`; Solidity 0.8.24.

```sh
# Fully offline replay of this snapshot:
uv run --with pycryptodome python scripts/non_mev_screen.py --offline

# New snapshot, with a new directory rather than overwriting these observations:
uv run --with pycryptodome python scripts/non_mev_screen.py --out research/new-non-mev-snapshot

# Fetch test dependency when it is absent (lib/ is ignored):
forge install --root research/2026-09-06/non_mev/fork \
  foundry-rs/forge-std@df98778116f87d110af4ec37ca529a6aec917c74 --no-git

# Local fork simulation; does not broadcast:
forge test --root research/2026-09-06/non_mev/fork \
  --fork-url https://eth.drpc.org --fork-block-number 25918293 -vv
```

The fork provider must support archive reads. Publicnode rejected the archive request in this run; dRPC completed the tests. Provider availability may change. No live wallet was funded, no contracts were deployed to mainnet, and no transaction was submitted.
