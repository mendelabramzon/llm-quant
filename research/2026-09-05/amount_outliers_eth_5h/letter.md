# Ethereum mainnet amount outliers: five-hour transaction-type research

The study covers **5 September 2026, 11:22:48–16:22:48 UTC**, with the end excluded: **1,498 finalized Ethereum blocks, 392,428 transactions and 1,146,927 logs**. This is the fixed five-hour window chosen when collection began; resuming the research did not move it. No other chain is included.

The result is a reusable quantitative-to-qualitative loop. Known mechanisms run their existing investigation method. Unmatched transactions form a queue of clusters keyed by destination, selector, event shape and unknown event topics. Codex examined representative packets, followed primary documentation, added **12 bounded rules**, and replayed the entire candidate population. The final registry contains **58 categories, 54 observed** in this window. The replay produces per-transaction investigations and preserves alternative matches.

**10,170 transactions pass the amount screen. Of these, 9,160 (90.07%) receive a primary rule label; 1,010 remain unresolved in 472 clusters.** Labelled transactions account for 93.89% of the sum of largest observed asset changes. These are coverage measurements, not classification accuracy. Many labels identify a mechanism or execution pattern while ownership and commercial intent remain uncertain.

Read the [full evidence report](report.md), [qualitative investigations](qual_notes.md), [method](method.md), [final validation](validation.json), and [frozen replay code](replay/README.md).

## What counts as an amount outlier here

For every observed successful asset movement, net incoming and outgoing amounts **per address and per asset within the transaction**. Let P be the largest absolute dollar-valued net. Select P ≥ $10,000, or event-supported temporary loan principal ≥ $10,000, or gross priced legs ≥ $100,000. These are absolute research thresholds, not statistical significance tests or indicators of suspicious activity.

9,903 transactions meet the position-change threshold; another 267 are included by the supplemental conditions. There are 2,271 at or above $100,000 of position change, 266 at or above $1M, and 10 at or above $10M. Median P among selected transactions is $29,995.78; maximum P is $27,336,755.06.

The sum of P is **$1.531B**. It counts capital again when it moves in another transaction and can select an intermediary's delta. It is not unique capital, customer trading volume, profit, or an estimate of assets under management. Gross legs count routing, wrapping and loan repayment repeatedly.

## What the qualitative pass learned

**Caller, asset owner and beneficiary must be separate roles.** A [20M USDT transfer](https://etherscan.io/tx/0x0fff7095c88bae0c4fc9ee2d14038b803e17f36c349dcde31cb9c9ab6cbd62f8) goes directly between third parties while both the gas payer and helper have zero token net. A second family uses account execution calls to send inventory held by the called account. The persistent method now extracts actual asset senders, recipients and leg directions. Contract-account execution has 210 occurrences and operator-mediated batches 70. Exchange ownership is not inferred from the execution ABI.

**Escrow funding, settlement release and trading-account payout are different economic events.** Relay deposits create settlement inventory; its allocator-authorized releases can replenish a solver. Aster treasury deposits and payouts move balances into or out of a trading system without exposing its trades or PnL. Rules combine deployment identity, event evidence and incoming/outgoing assets. References: [Relay depository](https://docs.relay.link/references/protocol/components/depository), [Relay deployments](https://docs.relay.link/references/protocol/addresses), [Aster contracts](https://docs.asterdex.com/overview/what-is-aster/our-smart-contracts).

**A deposit can repay debt.** The initial [Dolomite example](https://etherscan.io/tx/0x19f149ac2a151cf8855bb6452a3b419e3bacac4bf40de17f4f1352dfdbf6a338) routes 4,080,625.967555 USDC through a proxy. Two transfers produce about $8.16M of gross traffic but one account credit. The learned method decodes the documented LogDeposit account, market, deltaWei and signed newPar. Removing truncated unknown-event features exposed five more occurrences in other assets. Of the six credits, four leave positive principal, one leaves debt and one reaches zero. The next quantitative investigation of this family can distinguish those outcomes immediately. [Dolomite event documentation](https://docs.dolomite.io/developer-documentation/dolomite-margin-events).

**Temporary funding is different from lasting exposure.** A [Morpho-funded transaction](https://etherscan.io/tx/0x593cc846acfa8ab351b4ac8b8663206da87f51c798d3615f7e8927ce5b5d0016) has about $25.80M of matched loan principal and $51.60M of gross priced legs but only $49.29 of largest observed net change. A net-only screen would miss it. Loan detection now requires a lending event from the lender plus an ordered lend/repay pair. This remains a transfer-topology method, not a full loan ABI or balance proof. [Morpho events](https://github.com/morpho-org/morpho-blue/blob/main/src/libraries/EventsLib.sol).

**Positive cash is not automatically arbitrage.** One apparent positive-net multi-pool strategy also repays and withdraws from Aave; released collateral explains why a principal can end with more WETH. The new lending-with-swap category contains 74 occurrences, while flash-funded lending adjustments contain 10. The known method separates debt, collateral, trading and temporary funding. It does not compute account PnL from an incomplete cash vector.

**A source-chain message is not destination delivery.** The CCIP example sends roughly $2.315M of wstETH into a pool and pays only about $0.50 of native message fees. The rule identifies Ethereum initiation, with delivery unresolved. This avoids confusing a small transaction value with small economic size. [CCIP source](https://github.com/smartcontractkit/chainlink-ccip/blob/main/chains/evm/contracts/onRamp/OnRamp.sol).

**Liquidity collection is not necessarily a new withdrawal.** Collect without Burn/DecreaseLiquidity pays amounts already owed. Separating fees from principal owed after an earlier burn requires position history. Transactions with both swaps and liquidity changes get a combined type. The ordering audit also corrected Uniswap v4 pool identity: the manager address hosts many pools, so bracketing must use manager plus pool ID.

## Newly learned categories and their observed footprint

Counts are primary labels. Some newly learned types replace old broad labels, so this table is not the increase in coverage. Dollar totals are sums of P.

| Learned category | Transactions | Sum of P |
|---|---:|---:|
| lending-position adjustment with swaps | 74 | $57,650,942.46 |
| Dolomite margin-account deposit | 6 | $5,636,931.65 |
| Relay depository settlement withdrawal | 81 | $2,756,067.15 |
| deposit into Relay settlement escrow | 77 | $2,671,370.70 |
| Aster trading-treasury deposit | 17 | $4,420,782.90 |
| Aster trading-treasury payout | 10 | $5,693,827.86 |
| CCIP token-send request on Ethereum | 2 | $3,331,993.11 |
| contract-account token execution | 210 | $50,254,062.14 |
| operator-mediated token-transfer batch | 70 | $28,700,730.16 |
| flash-funded lending-position adjustment | 10 | $17,433,394.36 |
| liquidity management with an embedded swap | 94 | $12,225,424.59 |
| collection of tokens owed to a liquidity position | 5 | $602,328.07 |

## The learning loop, including corrections

The initial seed pass matched 8,745 transactions: 85.99% by count and 87.35% by summed P. After the qualitative investigations and audits, 9,160 match: 90.07% and 93.89%. That is **415 additional primary classifications**, alongside corrections to already classified cases. All rounds are retained in [rounds.json](rounds.json).

The audit returned a false WETH-wrap candidate to unknown because it had no canonical Deposit event; recognized CCTP burn as a bridge request before generic token burning; put verified CoW settlement ahead of a positive-net arbitrage shape; distinguished staking components from transactions with swaps; and separated collect-only payouts from fresh liquidity reductions. Seven unit regressions and saved real-transaction cases exercise these distinctions.

Every selected transaction has a method record in `investigations.jsonl.gz`. `all_matches_by_hash.json.gz` retains overlaps: 4,581 candidates match more than one rule. One primary label is useful for counting, but a complete explanation can require several labels. The evidence report contains packet-level notes for all 77 final representatives; protocol-specific investigations and earlier correction cases have additional notes. Packet review is not a source audit of every participant or an independent accuracy estimate.

## What remains unresolved

The 1,010 unmatched transactions represent $93.56M of summed P. They include repeated one-leg transfers through custom helpers, account calls with unverified historical delegation, native-value calls with opaque reference records, and paths involving assets or liabilities outside the decoded registry. Some transfer paths are already clear while their commercial meaning is not.

For example, a helper routes approximately $2.24M of USDC between third parties, and another router splits 53,430.641117 USDT into 53,035.559155 and 395.081962. The smaller leg is quantitatively fee-like, but calling it a merchant fee requires semantics not present in the transfers. Repeated equal-value payouts and onward sweeps also occur; equal amounts do not establish arbitrage, bridge completion or common ownership.

The queue is retained in [residue.json](residue.json). A later window applies the frozen known rules first. Novel clusters should be examined with verified contract code, historical implementations and custom account/message records; promote a rule only when its measurable conditions and failure cases are stated. The LLM step was performed by Codex in this session. The Python commands emit the hand-off packets and replay known methods; they do not run an unattended external LLM service.

## Scope and confidence

Full blocks and all logs were collected. Offline verification found no parent-link, index, timestamp or log-provenance issues; 16 sampled canonical block hashes matched. All 37 registered token addresses have checked onchain decimals. 1,416 large no-log native candidates have successful receipts, as do the final evidence packets. The [validation artifact](validation.json) records the exact consistency checks and targeted interpretation regressions.

ETH and BTC use five hourly endpoint marks; other feeds and wrapper rates use the window end, with identified stablecoins lacking feeds assumed at parity. These retrospective marks are unsuitable as contemporaneous backtest prices. Unverified implied token pricing is disabled. Smaller no-log native transfers are omitted from value profiles. Internal native transfers, pre/post balances, debt and collateral state, destination-chain outcomes and most unpriced assets remain outside the full census. Window-end code inspection does not prove code status at the transaction block.

The study establishes a reproducible discovery loop and a larger mechanism registry. It does not establish a validated classifier for beneficial ownership, intent or profitability, and five hours do not estimate long-run transaction frequencies.
