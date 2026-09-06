The strongest lead is a repeated strategy spanning several transactions, hidden inside the lending categories. I would allocate the next research effort to reconstructing complete strategy economics and execution quality before building an ETH directional signal from these outliers.

Follow-up: [the RPC accounting and counterfactual investigation](validation/findings.md) now tests the 20 sequences below. It finds approximately $27.23 retained after direct fee-recipient payments and actual gas, 17 verified brief LP positions, about $1.17 of explicit LP fees, and improved middle-order outputs in all 20 replays without the opening leg. The original hypotheses and their initial evidence are preserved below.

This follow-up uses the saved five-hour window. It adds calculations over `txs_big.jsonl.gz`, `all_matches_by_hash.json.gz`, the complete `txs_all.jsonl.gz`, and raw blocks/logs for 20 selected sequences. It does not change the original classifier. [evidence.json](evidence.json) preserves the calculations, transaction hashes, matched liquidity positions and Aave events. [analyze.py](analyze.py) reproduces them offline. The trading ideas below are hypotheses; no forward-return backtest or realized-PnL reconstruction has been performed.

**1. Ordinary lending is concealing a repeated trading strategy.**

Sender `0x654fae4aa229d104cabead47e56703f58b174be4` makes exactly 40 transactions in the complete saved window, all to `0x000000000035b5e5ad9019092c665357240f594e`. They form 20 same-block pairs, always separated by exactly one other transaction. Their primary labels are 29 lending-with-swap, nine ordinary Aave operations and two flash-funded lending adjustments.

The actor alone accounts for $50.671M, or 87.89%, of the $57.651M lending-with-swap category. Across all 40 transactions its summed largest changes are $72.985M. Each opening transaction sends approximately 711 WETH from the outer contract; each closing transaction returns approximately that amount. The strategy repeatedly uses around $1.75M of WETH rather than deploying tens of millions of independent capital.

Nine pairs have a positive liquidity addition followed by an exactly offsetting removal at the same pool, owner, ticks and, for v4, salt. Every one has a swap in that pool in the intervening transaction. These nine pairs have the event pattern of just-in-time liquidity. This establishes short liquidity lifetime and transaction ordering; it does not allocate the cash result between LP fees, trading, price displacement and other payments.

The first example is block 25,910,849:

| Transaction index | Observed action |
|---|---|
| 0 | Supply 710.933981 WETH to Aave; borrow 1,216,375.784357 USDC; swap; add v4 liquidity. |
| 1 | Another caller swaps through the same v4 pool as part of a route. |
| 2 | Remove the exact added liquidity; swap; repay 1,216,375.784358 USDC; withdraw the WETH collateral; return WETH to the outer contract. |

The Aave account is `0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a`. Across all 20 pairs, the decoded repayment exceeds the corresponding borrowing by only one or two raw token units per pair. This strongly supports temporary financing across transactions. It does not independently prove every starting or ending account balance.

The 20 paired changes at the outer contract sum to **0.154867944752713209 WETH**, approximately **$380.61** at the study's marks; the median paired cash increase is **$9.92**. These are observed WETH cash changes. Internal ETH payments, other controlled accounts, remaining claims and costs must be reconciled before calling them profit. In particular, token cash can increase while another account pays the builder.

The profit hypothesis is that capital can be reused for short trading/liquidity episodes with very little time-based financing expense. Unlike an ordinary flash loan, collateralized borrowing can remain open across an intervening transaction. Aave's current [reserve logic](https://github.com/aave-dao/aave-v3-origin/blob/main/src/contracts/protocol/libraries/logic/ReserveLogic.sol) avoids another interest-index update at the same timestamp; its [Pool documentation](https://aave.com/docs/aave-v3/smart-contracts/pool) describes collateralized borrowing and repayment. Historical implementation verification remains necessary. The observed one- or two-unit repayment difference is stronger evidence for these particular episodes than a general assertion about today's source.

The next experiment should reconcile these 20 episodes completely: before/after token and native balances, debt and collateral claims, position balances, gas and internal payments. Then simulate implementable alternatives with the state and transaction visibility available before inclusion. Reject replication if the retained margin disappears after builder payments, or if the relevant order flow was unavailable to us. An included historical sequence is not evidence that another participant could have won its inclusion.

**2. The economically interesting counterparty can be absent from the outlier dataset.**

Seventeen of the 20 intervening transactions fail the combined amount screen. Some have largest priced changes of only a few hundred dollars; one has zero priced net change. Their complete asset exposure is not necessarily small, because unpriced assets and internal native transfers remain incomplete. Three are selected, and one of those is primarily labelled PSM conversion rather than a sandwich-pattern counterparty.

This is a concrete reason to stop ranking opportunities by absolute transaction size. A small order in a thin or poorly routed market can matter more than a $20M transfer between deep inventory accounts. Once an interesting actor or liquidity episode is identified, inspect every intervening transaction and every relevant pool event, regardless of the amount threshold.

Two monetization paths deserve separate experiments. An execution engine or solver could improve realized fills by avoiding routes with recurring adverse execution, choosing more robust routes, or using better submission channels. A liquidity strategy could select pools and periods with attractive fee income after markout, rather than copying a position because it earned visible fees. Both require a counterfactual: replay the middle order from the pre-sequence state without the outer transactions, compare implementable alternative routes, and measure LP markouts at several horizons. A transient liquidity addition can improve execution while an accompanying swap worsens it; only the replay identifies the net effect.

Candidate features are order size relative to executable depth, tick gaps, route concentration, slippage tolerance, active liquidity changes, and prior actor-specific execution outcomes. Observed future bracketing is a label for research, not a feature available when the user submitted the order. Kill the strategy if any improvement disappears with realistic gas, fills, latency and quote availability.

**3. Cheap visible gas makes access to execution the likely bottleneck.**

All 40 transactions of the repeated actor pay zero priority fee. Summing gas limit times the recorded effective gas price gives a conservative upper bound of about **$8.76** for their execution-gas expense at the study's ETH marks. Gas limit is not gas used, and this bound excludes internal payments. In the primary flash-funded swap category, 132 of 160 transactions also pay zero priority fee.

This is consistent with specialized inclusion arrangements or direct builder payments; zero tip alone cannot establish either. Flashbots documents both [ordered bundles](https://docs.flashbots.net/flashbots-auction/advanced/understanding-bundles) and [direct coinbase payments](https://docs.flashbots.net/flashbots-auction/advanced/coinbase-payment).

The business implication is to measure retained surplus and accessible opportunities before optimizing gas or implementing another generic arbitrage scanner. The visible cash increase is only about 2.2 basis points of the roughly $1.75M reused WETH over this particular window, before the missing costs and positions. That is not an annualized return or a complete capital-efficiency estimate. A better scanner may be commercially irrelevant if builders or incumbent order-flow relationships capture the surplus.

An experiment should report gross strategy proceeds, explicit gas, internal builder/proposer payments, other transfers, retained PnL and required capital separately. Estimate inclusion probability from live shadow submissions or appropriate auction evidence; it cannot be inferred from a dataset of successful included transactions. If most surplus is auctioned away, prioritize distinctive routing, inventory or customer execution advantages.

**4. Mechanism coverage is hiding additional discovery candidates.**

Only 10 selected transactions have sandwich-pattern execution as their primary label, but 88 match the underlying pattern rule: 42 are primarily liquidity-with-swap, 34 lending-with-swap, two flash-funded lending and ten the sandwich type. These are candidate transaction legs, not 88 independent or validated profitable strategies.

Similarly, 214 selected transactions match the flash-funded swap rule, compared with 160 primary labels. There are 300 selected transactions with detected flash principal; 182 have largest priced net changes below $10,000. Of the 300, 261 contain unknown event topics and 204 contain unpriced assets. This does not imply that all unknown events matter economically; it shows that a familiar primary mechanism can coexist with an unexplained strategy.

The 84 primary flash-other transactions are a useful bounded queue: 83 have unknown events, and 51 call `0xd82461784eb72d4b67cbab077989eb215315e272`. Another 19 call `0xcb0151ac9479a6a0261622baa63ae843c9793d45`. Lack of a recognized swap is not proof of no trade. Unrecognized venues, liabilities, redemptions or nonstandard settlement may explain the cash flow.

The profit hypothesis is that reusable pricing or settlement mechanisms can be discovered in already classified transactions, where a coverage-driven research process would stop investigating. Rank candidate clusters by recurrence, degree of economic closure, retained cash after costs, plausible accessible flow and the cost of decoding their missing claims. Do not rank solely by unresolved dollar volume. First decode historical implementations and economically material unknown events for the two concentrated flash-other destinations. Reject a candidate if its cash receipt is explained by principal withdrawal, liability creation or an offsetting position loss.

**5. A slower opportunity is the price of settlement inventory.**

The study has 77 Relay deposits with $2.671M of summed largest changes and 81 settlement withdrawals with $2.756M. All 81 withdrawals have the same caller, `0xf70da97812cb96acdf810712aa562db8dfa3dbef`. This concentration identifies a tractable settlement-inventory account to study; it does not prove that one solver dominates all Relay activity or that the account earned the difference between the two totals.

Relay's [solver guide](https://docs.relay.link/references/protocol/guides/for-solvers) explains that solvers front destination capital and can withdraw on a chain according to inventory needs, regardless of the original deposit chain. Its [depository documentation](https://docs.relay.link/references/protocol/components/depository) distinguishes deposits from authorized settlement withdrawals. Consequently, Ethereum inflow minus outflow is neither a user demand measure nor solver profit, and withdrawals need not pair one-for-one with local deposits.

The hypothesis is that route-specific inventory scarcity raises executable spreads, and replenishment later reduces them. The tradeable quantity would be a spread or the value of providing inventory, rather than ETH's direction. Link quote timestamps, origin deposits, destination fills, Hub credits, withdrawals and actual token balances across chains. Test whether inventory depletion predicts wider quotes, and whether replenishment precedes their normalization at a lag long enough to trade. Control for volatility, network fees, other solvers and common market moves. Reject it if the price adjustment occurs before any signal we could observe, or if adverse selection, financing and rebalancing costs absorb the spread.

This would require new data beyond the present Ethereum-only window. Source-chain observations do not establish destination delivery, and deposits or withdrawals can be effects of already completed trading.

**6. Persistent leverage may predict pressure; transaction labels cannot.**

Removing the largest repeated operator reduces lending-with-swap from $57.651M to $6.979M and from 74 to 45 transactions. Other repeated operators remain, so the remainder is not automatically organic borrower activity. A signal that reads all of the original amount as deleveraging pressure would largely be measuring temporary trading finance.

A more useful hypothesis is that persistent, constrained balance-sheet changes predict subsequent order flow. Selling collateral to repay debt can indicate a forced seller; borrowing an asset to sell it can create short exposure; borrowing stablecoins to buy collateral can increase leverage. The same generic supply/borrow/repay events can occur in all of these paths. Reconstruct the asset direction, beneficiary, complete collateral and debt state, health-factor distance and whether the change reverses within the block. The Dolomite examples provide another warning: four credits leave positive principal, one leaves debt and one reaches zero.

Test subsequent same-account selling and market returns after confirmed persistent changes, using controls matched on prior price movement, volatility, liquidity and account type. Enter only after the event and required confirmation become available. Reject the directional hypothesis if it merely reflects price declines already in progress or loses its effect after removing temporary financing and treasury activity. Lending actions at constrained accounts may support liquidation monitoring even when they have no market-wide directional value.

**Research allocation and acceptance criteria.**

| Priority | Work | Decision it should resolve |
|---|---|---|
| 1 | Reconcile the 20 repeated sequences, including traces and actual receipts. | Does retained profit survive costs and claim accounting, and where does it originate? |
| 2 | Replay their 20 middle orders and nine matched liquidity lifetimes. | Can routing or liquidity selection capture an accessible improvement? |
| 3 | Decode the two concentrated flash-other destinations. | Is there a repeatable, economically unexplained venue or settlement mechanism? |
| 4 | Build a cross-chain quote/inventory event history for the Relay account. | Do inventory-driven spreads persist long enough to monetize? |
| 5 | Test persistent leverage changes after removing temporary episodes. | Is there forward pressure beyond ordinary momentum and volatility? |

Every backtest needs point-in-time data. The study uses hourly endpoint or window-end marks, and its hot-wallet/pass-through tags use the whole five-hour window. Both prices and actor features can leak future information. Rebuild actor features from preceding history and use prices or executable quotes available at the actual decision time. Keep later days untouched by hypothesis selection, group overlapping episodes by actor/pool/block, report concentration, and include unsuccessful execution attempts where observable. Twenty sequences by one operator are not 20 independent validations of an accessible strategy.

The practical output to optimize is expected retained profit at deployable size: probability of obtaining a usable fill times conditional net proceeds, less failed-attempt costs, financing and the value of tied-up capital. The next useful deliverable is a ledger of complete strategy episodes with a defensible cost model and falsifiable entry conditions. Raising classification coverage above 90% is useful only insofar as it helps build that ledger.
