The main hypothesis is confirmed for the historical sample: this actor reuses WETH collateral for profitable, same-block trading episodes financed through Aave. The economics are much less attractive than the visible token gains suggest. **The 20 episodes retain approximately $27.23 after direct fee-recipient payments and gas, from approximately $380.62 of gross WETH gains.** All 20 are positive, but the median retains only **$0.60**.

The mechanism is also clearer: **17 episodes combine a sandwich with just-in-time liquidity, and three use surrounding swaps without a matched liquidity position.** Explicit LP fees total only **1.145665 USDC and 0.027402 USDT**. Replaying the middle orders without the opening leg improves the measured output at an identified recipient or settlement contract in every episode. This supports a strategy based principally on price-dependent trading around other orders. It rejects interpreting these examples as ordinary lending or primarily LP fee farming.

This investigation follows priorities 1 and 2 of the [original hypothesis memo](../insights.md). It tests the specific 20 sequences selected there. It does not establish the memo's separate Relay inventory, persistent-leverage, or flash-other hypotheses, nor does it establish that a new participant could obtain these opportunities.

**The missing cost was an explicit payment in every closing transaction.**

| Component, summed over 20 episodes | ETH/WETH units | USD at the original study's marks |
|---|---:|---:|
| Gross WETH increase across the operator's three-account group | 0.154872896893232452 | $380.62 |
| Direct ETH payments to the respective block fee recipient | −0.141617341946688976 | −$348.04 |
| Actual receipt gas used × effective gas price | −0.002176324316683585 | −$5.35 |
| Retained ETH-equivalent cash | **0.011079230629859891** | **$27.23** |

The direct payments consume **91.44%** of gross WETH gains; execution gas consumes another **1.41%**. Only **7.15%** remains. The $8.76 gas-limit bound in the original memo was conservative, but gas was not the important missing expense. All 40 effective priority fees are zero, while all 20 closing traces contain a successful native transfer from the outer contract to the block's `miner`/fee-recipient address. There is exactly one positive native-value transfer in each pair. Fourteen pay `0xdadb0d80178819f2319190d340ce9a924f783711`, and six pay `0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97`.

Those are observed inclusion payments. The data does not allocate the recipient's proceeds between builder, proposer, or other parties. Nor does this episode ledger include subsequent rebates or off-chain arrangements.

The accounting group is sender `0x654fae4aa229d104cabead47e56703f58b174be4`, outer contract `0x000000000035b5e5ad9019092c665357240f594e`, and execution/Aave account `0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a`. Traces connect their funding and execution; the grouping is for these episodes, not an assertion about legal ownership or all accounts belonging to the operator. The original outer-contract WETH increase remains exactly 0.154867944752713209. Including the helper adds 0.000004952140519243 WETH, approximately 1.2 cents.

The calculation is `ΔWETH + Δnative ETH` across the group. Native state changes already include gas, so gas is not subtracted twice. Independent cash-flow reconciliation confirms that the same result equals `gross WETH − direct payments − receipt gas`. [ledger.json](ledger.json) retains exact raw units, every transaction hash, non-WETH movements and checks; [ledger.csv](ledger.csv) and [episodes.md](episodes.md) provide compact comparisons.

**Borrowed principal and residual positions do not explain the apparent profit.**

Historical view calls were executed immediately before opening and immediately after closing, not merely at block boundaries. Across all 40 boundaries, `getUserAccountData` reports zero debt for all three accounts; the touched variable-debt tokens also have zero balance and zero scaled balance. Underlying-token balance changes agree with the transfer ledger. Remaining collateral claims are dust: the helper's total Aave collateral is only 399–400 base-currency units, about $0.000004 with Aave's eight-decimal base convention. The complete raw claim balances and changes are retained in [balances.json](balances.json).

For every borrowed reserve, the liquidity and variable-borrow indexes emitted during the pair remain identical. Repayment exceeds borrowing by one or two raw units in all 20 episodes. That combines an observed financing cost with an observed zero ending debt balance. [financing.json](financing.json) preserves both the amounts and reserve-index evidence.

The historically executed Aave Pool implementation is `0x728a138a4823392c2efa55e028d434f526fe03cf`; its call traces also expose the linked execution libraries. The explorer-verified source bundle for that implementation contains the same-timestamp early return in `ReserveLogic.updateState`, rather than relying on today's repository branch. The source bundle and pinned historical runtime are saved in [sources](sources/) and [historical_code.json.gz](historical_code.json.gz). The event and state checks establish the actual outcomes independently of an interpretation of that source.

For all 17 LP positions, historical storage/getter calls verify **zero liquidity before opening, exactly the added liquidity before the middle order, and zero after closing**. Both v3 positions also have zero tokens owed before and after. There is no material unclosed LP inventory offsetting the retained cash. [positions.json](positions.json) preserves these measurements.

**Eight additional brief positions were hidden by missing Ekubo decoding.**

| Venue | Matched episodes |
|---|---:|
| Uniswap v4 | 7 |
| Uniswap v3 | 2 |
| Ekubo v3 | 6 |
| Ekubo v2 | 2 |
| Total | **17** |

The two Ekubo emitters are `0x00000000000014aa86c5d3c41765bb24e11bd701` and `0xe0e0e08a6a4b9dc7bd67bcb7aade5cf48157d444`. Their identities agree with the protocol's [v3 deployment table](https://docs.ekubo.org/reference/contracts/evm-v3/) and [v2 deployment table](https://docs.ekubo.org/reference/contracts/evm-v2/). Their verified ABIs decode matching `PositionUpdated` additions/removals and `PositionFeesCollected` events. The middle swaps in those same pools use packed, topicless logs; the historical Core source specifies their encoding. This explains why the earlier event decoder missed them. [mechanics.json](mechanics.json) retains the decoded events, position keys and fee amounts.

The **$1.173067 of explicit LP fees**, valuing USDC and USDT at parity, is approximately **0.31%** of gross WETH gains. It is smaller than the $5.35 actual gas bill, even before the $348.04 direct payments. The fee calculation uses v4's returned `feesAccrued`, Ekubo's collected-fee events, and v3 collection minus withdrawn principal. The zero starting positions/owed amounts prevent old v3 fee claims from being mistaken for this episode's revenue. The remaining gross proceeds arise from trading and LP inventory conversion; a finer allocation among individual swaps, passive-LP effects and price displacement would need additional counterfactuals.

**The counterfactual rejects a benign execution-improvement interpretation for these sequences.**

For each middle transaction, I made two historical `debug_traceCall` executions at the original block hash. The actual-state execution uses the state immediately before the middle transaction. The counterfactual uses the state immediately before the actor's opening transaction, preserving all earlier transactions in the block. Sender, calldata, route, value, gas limit, fee settings and the block context stay the same. There are no balance, storage, code, price or route overrides. Geth documents the transaction-state selection in its [debug tracing API](https://geth.ethereum.org/docs/interacting-with-geth/rpc/ns-debug).

All **20 actual-state replays match the complete recorded call tree, gas used and ordered receipt logs exactly**. All 20 counterfactuals succeed. At the identified output destination, each produces more of the output asset without the opening leg. These destinations include settlement and routing contracts, so the result is not a claim of completed cross-chain delivery or universal wallet-level welfare. [audit.json](audit.json) identifies every measured destination and asset and preserves all raw comparisons. Other changed transfers remain available in the ledger/replay artifacts.

Examples from the unchanged routes:

| Block | Output asset | Actual output | Without opening leg | Improvement |
|---|---|---:|---:|---:|
| 25,910,849 | USDT | 9,708.973201 | 9,757.644323 | **48.671122 USDT** |
| 25,910,935 | Native ETH | 6.611261179774006519 | 6.622410320160302266 | **0.011149140386295747 ETH** |
| 25,910,990 | USDC | 4,081.913495 | 4,157.146860 | **75.233365 USDC** |
| 25,911,349 | USDT | 19,815.051681 | 19,934.080315 | **119.028634 USDT** |
| 25,911,995 | USDC | 463,903.962219 | 463,950.683007 | **46.720788 USDC** |

The median improvement across the 20 measured outputs is **101.24 basis points of actual output**. This is an unweighted, retrospective statistic over one operator's selected episodes. It includes the net effect of both the opening swap and any liquidity addition; it does not estimate the isolated effect of adding liquidity.

As a separate falsification check, the unchanged closing calldata reverts in all 20 cases if executed immediately after opening with the middle order omitted. That shows dependence on the middle order's state changes. It does not measure the result of an adapted emergency unwind or prove that no alternative closing trade could succeed.

**Verdict and research decision.**

| Hypothesis or interpretation | Result |
|---|---|
| Reusable collateral finances a repeated same-block trading strategy. | **Confirmed in these 20 episodes.** Financing indexes do not advance; debt is fully repaid. |
| Positive retained proceeds survive visible on-chain costs and material claim accounting. | **Confirmed, but only about $27.23 in total.** Median about $0.60. |
| The visible $380 is mostly retained profit. | **Rejected as an interpretation.** The original memo correctly left this unproven; direct payments absorb most of it. |
| The main opportunity here is LP fee harvesting. | **Rejected for this sample.** Explicit LP fees are about $1.17. |
| These liquidity additions improve the middle orders' net observed execution. | **Rejected for the full opening legs in this sample.** Removing them improves the measured output in 20/20 replays. |
| We can deploy this strategy profitably with accessible order flow. | **Unproven.** Historical execution does not establish visibility, bidding access or inclusion probability. |

I would not start a generic LP-fee replication project from this evidence. The next commercial test should concern execution protection or order-flow access: collect orders and executable quotes before submission, measure outcomes under the actual submission channels available to us, and record failed attempts and all inclusion costs. A strategy replication case requires evidence that our attainable conditional margin and inclusion probability cover those costs. The successful-episode ledger alone cannot supply that evidence.

The roughly 711 WETH collateral is real reused capital, and the observed accounts also hold ETH payment buffers. The retained proceeds are about 0.156 basis points of the WETH collateral over this selected window, before infrastructure, opportunity costs, future rebalancing, unsuccessful attempts and any later refunds. This is not an annualized return or an operator-wide profit statement. Dollar conversions reuse the original study's hourly endpoint marks for readability; all decisive accounting is in raw token/wei units, and no trading signal or forward-return test uses those retrospective marks.

The original Infura endpoint provided receipts but returned unavailable-method errors for tracing and errors for historical state. A public dRPC endpoint supplied the historical traces and view calls. All 60 new receipts match the original saved Infura logs; all 20 headers match the saved canonical block hashes. The last studied block was below the retrieved finalized head. RPC responses, capability failures, source bundles, scripts and a file-hash manifest are retained. See [README.md](README.md) for reproduction and the precise limits of this RPC-based evidence.
