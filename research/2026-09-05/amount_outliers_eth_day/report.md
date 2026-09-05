# Transaction types on Ethereum mainnet over the research window: a quant taxonomy grown by LLM investigation

Ethereum only, one full day (24 hours). The deterministic step (`scripts/tx_types.py`) values successful logged native transfers, receipt-confirmed large no-log native transfers, every ERC-20 transfer of a registry token and every WETH wrap or unwrap in USD, nets them per address and asset inside each transaction, and calls a transaction large when one address changed one asset position by at least $10,000. Supplemental candidates have event-supported flash principal at least that size or gross priced legs at least ten times that size. Every selected transaction is then typed by the rules in `scripts/type_registry.py`: each type is a qualitative description of what happens, a quantitative rule that recognises it, and an investigation method that runs on every occurrence. Transactions no rule matches form the residue; the residue is clustered by destination, selector and event shape, and the LLM investigates the largest clusters, writes `qual_notes.md`, and adds rules. The registry after this pass holds 90 types. Numbers below are computed; prose marked LLM is interpretation with a stated confidence.

Window: 2026-09-04T14:00:00+00:00 to 2026-09-05T14:00:00+00:00 (exclusive), blocks 25,904,413 to 25,911,585: 7,173 blocks, 1,793,396 transactions, 5,962,702 logs. Logs establish successful execution; receipts confirm every no-log native-value candidate above the threshold and the packet transactions. 67,572 transactions pass the combined screen; 65,290 have a position change at or above $10,000 (18,500 at or above $100k, 3,434 at or above $1M, 333 at or above $10M), summing to $26,001,438,369 of largest position changes; the median large transaction is $36,707 and the largest $389,437,444.

## Prices

| Key | USD | Source |
|---|---:|---|
| AAVE | 129.5530 | Chainlink AAVE / USD at block 25911585 |
| BTC | 79,717.0742 | Chainlink hourly series (24 points), window-end 79717.07424139 |
| CBETH | 2,799.9455 | ETH times exchangeRate() at block 25911585 |
| CRV | 0.3609 | Chainlink CRV / USD at block 25911585 |
| DAI | 0.9997 | Chainlink DAI / USD at block 25911585 |
| ENS | 5.8148 | Chainlink ENS / USD at block 25911585 |
| ETH | 2,458.8262 | Chainlink hourly series (24 points), window-end 2458.82623187 |
| LINK | 11.8513 | Chainlink LINK / USD at block 25911585 |
| MKR | 1,555.7418 | Chainlink MKR / USD at block 25911585 |
| RETH | 2,879.5021 | ETH times getExchangeRate() at block 25911585 |
| SDAI | 1.1798 | DAI times convertToAssets(uint256) at block 25911585 |
| STETH | 2,455.7384 | Chainlink STETH / USD at block 25911585 |
| SUSDE | 1.2466 | USD times convertToAssets(uint256) at block 25911585 |
| SUSDS | 1.1086 | USD times convertToAssets(uint256) at block 25911585 |
| UNI | 6.2378 | Chainlink UNI / USD at block 25911585 |
| USD | 1.0000 | assumed parity |
| USDC | 0.9999 | Chainlink USDC / USD at block 25911585 |
| USDT | 1.0000 | Chainlink USDT / USD at block 25911585 |
| WEETH | 2,712.0975 | ETH times getRate() at block 25911585 |
| WSTETH | 3,053.2931 | STETH times stEthPerToken() at block 25911585 |

82 tokens outside the registry were priced from their own swaps against priced assets (token outside the registry with at least 20 single-token-in single-token-out swaps against a priced asset and at least $100000 of priced volume; price is the median per unit at 18 decimals. A leg valued this way equals (leg raw amount / swap raw amount) times the swap USD, so the USD does not depend on the assumed decimals; only displayed token amounts do). They are labelled IMPL in the tables; decimals are assumed to be 18, so a token with other decimals is mis-scaled until `resolve` reports it. Largest by volume: [USDG (self-reported)](https://etherscan.io/address/0xe343167631d89b6ffc58b88d6b7fb0228795491d) $11,612,448 over 724 swaps, [PST (self-reported)](https://etherscan.io/address/0x22ae3d9a738471f405169af055d31c687087d4c7) $10,253,870 over 34 swaps, [AUSD (self-reported)](https://etherscan.io/address/0x00000000efe302beaa2b3e6e1b18d08d69a9012a) $5,303,453 over 91 swaps, [USDx (self-reported)](https://etherscan.io/address/0xa1fa7777974312f7d801a8880714a218f76233f8) $3,771,843 over 313 swaps, [fxUSD (self-reported)](https://etherscan.io/address/0x085780639cc2cacd35e474e71f4d000e2405d8f6) $1,878,376 over 197 swaps, [reUSD (self-reported)](https://etherscan.io/address/0x5086bf358635b81d8c47c66d1c8b9e567db70c72) $1,834,381 over 117 swaps, [DOLA (self-reported)](https://etherscan.io/address/0x865377367054516e17014ccded1e7d814edc9ce4) $1,809,193 over 189 swaps, [PEPE (self-reported)](https://etherscan.io/address/0x6982508145454ce325ddbe47a25d4ec3d2311933) $1,726,483 over 730 swaps.

Cross-check: 25,333 V3 swaps in the two factory-verified USDC/WETH pools give hourly median prices whose deviation from the hourly feed reading is 0 to 43 basis points.

## The taxonomy after this pass

Coverage: 67,491 of 67,572 large transactions (99.88%) and $25,976,878,775 of $26,001,438,369 (99.91%) are typed; the residue is 81 transactions in 50 clusters.

| Round | Label | Types | Typed | Coverage by count | Coverage by USD | Residue clusters |
|---:|---|---:|---:|---:|---:|---:|
| 1 | round 1: inherited registry (Codex, 58 types) replayed on the day | 58 | 61,117 | 90.45% | 92.95% | 1,765 |
| 2 | round 2: first batch of day types (custody, payments, smart accounts, Aave-fork, unpriced trades) | 71 | 66,589 | 98.55% | 99.45% | 558 |
| 3 | round 3: second batch (settlements, sweeps, staking pools, sUSDe claims, self-calls) | 80 | 66,976 | 99.12% | 99.8% | 431 |
| 4 | round 4: audit corrections (aggregator swaps, receipt tokens, Aave-fork tightened) and long-tail shapes | 90 | 67,491 | 99.88% | 99.91% | 50 |

| Group | Transactions | Sum of largest changes |
|---|---:|---:|
| transfer | 17,354 | $9,544,972,445 |
| exchange_flow | 23,334 | $7,237,159,076 |
| stablecoin | 2,024 | $2,980,458,130 |
| wallet | 3,692 | $1,655,172,625 |
| lending | 2,684 | $1,655,158,810 |
| bridge | 3,330 | $928,783,539 |
| custody | 3,477 | $778,231,028 |
| dex | 5,598 | $370,639,982 |
| vault | 825 | $333,999,321 |
| liquidity | 1,007 | $184,677,973 |
| staking | 311 | $130,873,582 |
| payments | 440 | $75,632,310 |
| mev | 2,425 | $41,202,630 |
| settlement | 888 | $37,080,297 |
| unknown | 81 | $24,559,594 |
| trading_custody | 87 | $21,829,141 |
| nft | 15 | $1,007,887 |

| Type | Group | Txs | Share | Sum | Share of USD | Rule (quantitative) | Origin |
|---|---|---:|---:|---:|---:|---|---|
| plain transfer without a behavioural subtype | transfer | 14,356 | 21.25% | $7,526,643,843 | 28.95% | plain transfer with no actor tag matched above | seeded 2026-09-05 from event shapes, before the window run |
| deposit into an exchange-like wallet | exchange_flow | 9,792 | 14.49% | $3,841,865,960 | 14.78% | plain transfer whose recipient has the hot_wallet or many_sources tag | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #11 |
| withdrawal from an exchange-like hot wallet | exchange_flow | 7,139 | 10.57% | $1,589,605,814 | 6.11% | plain transfer whose sender has the hot_wallet tag (>= 100 transactions to >= 50 distinct destinations in the window) | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #2, #9 |
| sweep of a deposit address | exchange_flow | 4,802 | 7.11% | $1,055,285,811 | 4.06% | plain transfer where either side is a pass-through address (few sources, one destination, net zero over the window) | seeded 2026-09-05 from event shapes, before the window run |
| stablecoin issuance | stablecoin | 280 | 0.41% | $1,049,940,957 | 4.04% | a registry stablecoin transferred from the zero address for at least the threshold, no swap, no flash loan | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) (USDS mint inside the PSM path) |
| token moved by an operator (transferFrom) | transfer | 1,385 | 2.05% | $996,348,874 | 3.83% | selector transferFrom with at most two logs and no swap | seeded 2026-09-05 from event shapes, before the window run |
| par conversion through a peg-stability module | stablecoin | 1,383 | 2.05% | $961,233,749 | 3.7% | BuyGem/SellGem event, or DSNote events with USDC and DAI/USDS legs and a mint or burn | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #6 |
| one sender paying many recipients | transfer | 939 | 1.39% | $936,807,003 | 3.6% | five or more distinct recipients, no swap, the principal only pays out | seeded 2026-09-05 from event shapes, before the window run |
| Aave v3 supply, borrow, repay, withdraw or liquidation | lending | 1,181 | 1.75% | $897,789,601 | 3.45% | an Aave pool event, no swap, no flash loan; event emitter must be the documented Ethereum Core pool | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #10 |
| stablecoin redemption | stablecoin | 204 | 0.3% | $790,827,207 | 3.04% | a registry stablecoin transferred to the zero address for at least the threshold, no swap, no flash loan | seeded 2026-09-05 from event shapes, before the window run |
| transfer between high-connectivity wallets | exchange_flow | 1,601 | 2.37% | $750,401,491 | 2.89% | plain native or single-token transfer; sender and recipient both carry hot_wallet or many_sources tags | seeded 2026-09-05 from event shapes, before the window run |
| contract-account token execution | wallet | 1,593 | 2.36% | $734,610,485 | 2.83% | one of three observed execution selectors; only Transfer/Approval events; all priced legs are token outflows from the called account | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| deposit into a bridge toward another chain | bridge | 2,361 | 3.49% | $526,980,424 | 2.03% | a bridge-deposit event family | seeded 2026-09-05 from event shapes, before the window run |
| bridge withdrawal finalized on Ethereum | bridge | 963 | 1.43% | $397,581,357 | 1.53% | a bridge-withdrawal event family | seeded 2026-09-05 from event shapes, before the window run |
| ERC-7821 execute() moving the account's own tokens | wallet | 412 | 0.61% | $366,443,636 | 1.41% | selector execute(bytes32,bytes), only transfer events, every priced leg leaves the called account | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| account-abstraction bundle | wallet | 710 | 1.05% | $300,341,199 | 1.16% | UserOperationEvent | seeded 2026-09-05 from event shapes, before the window run |
| contract-held tokens paid out by an operator call | custody | 1,262 | 1.87% | $288,628,470 | 1.11% | every priced leg leaves the called contract to addresses other than the sender, only transfer events | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| lending operation on an Aave-v3-fork pool | lending | 83 | 0.12% | $273,280,464 | 1.05% | Aave-shaped pool event together with ReserveDataUpdated from an emitter other than the core pool, no swap, no flash loan | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| custody vault sweep or payout by its operator ABI | custody | 410 | 0.61% | $247,615,237 | 0.95% | one of three custody selectors (sweep, payout, withdraw), exactly one priced transfer that enters or leaves the called contract, only transfer events | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| lending-position adjustment with swaps | lending | 336 | 0.5% | $242,350,608 | 0.93% | swap events plus a lending-position event, without a matched flash-loan pair | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| Morpho Blue market operation | lending | 943 | 1.4% | $178,404,971 | 0.69% | a Morpho Blue market event, no swap, no flash loan; event emitter must be the documented Ethereum Morpho Blue contract | seeded 2026-09-05 from event shapes, before the window run |
| multisig (Safe) execution | wallet | 268 | 0.4% | $123,066,370 | 0.47% | ExecutionSuccess or ExecutionFromModuleSuccess event | seeded 2026-09-05 from event shapes, before the window run |
| user swap through a router | dex | 855 | 1.27% | $117,843,622 | 0.45% | swap event(s), no flash loan, the sending EOA nets negative in one asset and positive in another, destination is not the pool itself | seeded 2026-09-05 from event shapes, before the window run |
| withdrawal from an ERC-4626 vault | vault | 268 | 0.4% | $116,130,330 | 0.45% | ERC-4626 Withdraw event, no swap | seeded 2026-09-05 from event shapes, before the window run |
| deposit into an ERC-4626 vault | vault | 198 | 0.29% | $113,844,102 | 0.44% | ERC-4626 Deposit event, no swap | seeded 2026-09-05 from event shapes, before the window run |
| wrapped BTC issuance or redemption | stablecoin | 18 | 0.03% | $105,233,336 | 0.4% | a BTC wrapper minted from or burned to the zero address for at least the threshold, no swap | seeded 2026-09-05 from event shapes, before the window run |
| operator-mediated token-transfer batch | wallet | 432 | 0.64% | $97,438,885 | 0.37% | observed helper address, four-array selector and completion topic, with direct non-mint token legs outside the helper | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| validator deposit | staking | 199 | 0.29% | $73,614,431 | 0.28% | DepositEvent from the deposit contract | seeded 2026-09-05 from event shapes, before the window run |
| issuance or redemption of a token priced from its own swaps | stablecoin | 139 | 0.21% | $73,222,882 | 0.28% | an implied-priced token minted from or burned to the zero address for at least the threshold, no swap | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| liquidity management with an embedded swap | liquidity | 438 | 0.65% | $68,380,411 | 0.26% | swap events and mint/burn/collect/modify-liquidity events in the same transaction | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| swap with an unclear principal | dex | 1,485 | 2.2% | $66,862,040 | 0.26% | swap event(s) not matched by the rules above | seeded 2026-09-05 from event shapes, before the window run |
| relayed transfer of approved funds recorded by the contract | payments | 360 | 0.53% | $64,985,221 | 0.25% | only transfer events plus custom events from the called contract; every priced leg is third party to third party | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| deposit into a contract that records it | custody | 481 | 0.71% | $61,078,436 | 0.23% | value or tokens enter the called contract only, a custom event is emitted, no swap | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| swap by a contract principal | dex | 1,532 | 2.27% | $58,918,826 | 0.23% | swap event(s), no flash loan, the destination contract nets negative in one asset and positive in another | seeded 2026-09-05 from event shapes, before the window run |
| Uniswap v4 liquidity change | liquidity | 226 | 0.33% | $58,628,449 | 0.23% | ModifyLiquidity event | seeded 2026-09-05 from event shapes, before the window run |
| two-party exchange through a settlement contract without a swap event | dex | 668 | 0.99% | $58,507,936 | 0.23% | no swap event, no flash loan, some address other than the destination nets negative in one priced asset and positive in another, two or more priced assets | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| operator-mediated transfer with custom events | custody | 290 | 0.43% | $53,807,058 | 0.21% | only transfer events plus custom events; priced ERC-20 legs present; no rule above matched | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| sweep of per-customer forwarder contracts into a collector | custody | 359 | 0.53% | $52,444,224 | 0.2% | every priced leg is paid by an address that emits a custom event in the same transaction and is neither the sender nor the destination | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| deposit that mints an unpriced receipt token | vault | 157 | 0.23% | $46,763,701 | 0.18% | no swap event, an unpriced token minted from the zero address, some address nets negative in a priced asset | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| flash-funded lending-position adjustment | lending | 54 | 0.08% | $37,818,504 | 0.15% | event-supported flash pair plus lending supply/borrow/repay/withdraw events | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| ETH wrapped into WETH | transfer | 324 | 0.48% | $36,861,067 | 0.14% | actual canonical WETH Deposit leg, optionally native input, and one log | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #5 |
| call on an EIP-7702 delegated account | wallet | 243 | 0.36% | $32,630,041 | 0.13% | transaction type 0x4 (execution selector alone does not prove account delegation) | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #7 |
| sender's own tokens sent through a contract call | transfer | 231 | 0.34% | $29,601,625 | 0.11% | only transfer events, every priced leg is paid by the sender to addresses other than the destination | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| CoW Protocol batch settlement | dex | 380 | 0.56% | $28,123,688 | 0.11% | Trade event from the settlement contract; event emitter must be the documented Ethereum settlement contract | seeded 2026-09-05 from event shapes, before the window run |
| withdrawal that burns an unpriced receipt token | vault | 90 | 0.13% | $27,573,047 | 0.11% | no swap event, an unpriced token burned to the zero address, some address nets positive in a priced asset | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| liquidity provided to a pool | liquidity | 165 | 0.24% | $27,522,063 | 0.11% | a liquidity-add event family and no removal family | seeded 2026-09-05 from event shapes, before the window run |
| batched transferFrom sweep into one collector | custody | 91 | 0.13% | $25,968,567 | 0.1% | only transfer events, every priced leg is third party to a single recipient, no custom event | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| liquidity withdrawn from a pool | liquidity | 155 | 0.23% | $25,422,908 | 0.1% | a liquidity-remove event family | seeded 2026-09-05 from event shapes, before the window run |
| contract pays its own tokens to the calling address | custody | 133 | 0.2% | $22,833,903 | 0.09% | every priced leg goes from the called contract to the transaction sender, only transfer events | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| intent, limit-order or RFQ fill | dex | 469 | 0.69% | $22,360,527 | 0.09% | UniswapX Fill, 1inch OrderFilled or 0x fill events | seeded 2026-09-05 from event shapes, before the window run |
| flash-loan-funded swap strategy | mev | 1,386 | 2.05% | $20,294,068 | 0.08% | a flash-loan pair (same asset lent and repaid between the same two parties inside the transaction) and at least one swap event; lender must also emit a flash-loan event | pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #3, #8 |
| deposit into Relay settlement escrow | settlement | 444 | 0.66% | $20,055,499 | 0.08% | Relay deposit event from the documented Ethereum depository plus an incoming priced leg | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| WETH unwrapped into ETH | transfer | 111 | 0.16% | $18,344,381 | 0.07% | the only leg is a WETH Withdrawal, one log | seeded 2026-09-05 from event shapes, before the window run |
| sUSDe cooldown claim (unstake) | vault | 24 | 0.04% | $17,908,746 | 0.07% | destination is the sUSDe contract, selector unstake(address) 0xf2888dbb, a USDe leg is present | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| Relay depository settlement withdrawal | settlement | 444 | 0.66% | $17,024,798 | 0.07% | RelayCallExecuted emitted by the documented Ethereum depository plus a positive token outflow from that address | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| stake into a StakingRewards-style contract | staking | 8 | 0.01% | $14,850,122 | 0.06% | Staked event and tokens entering the called contract, no swap | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| Dolomite margin-account deposit | lending | 26 | 0.04% | $13,807,745 | 0.05% | official DolomiteMargin Ethereum address, documented LogDeposit topic and incoming assets; decode account, market, deltaWei and newPar | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| Lido withdrawal request or claim | staking | 23 | 0.03% | $13,475,141 | 0.05% | WithdrawalRequested or WithdrawalClaimed event | seeded 2026-09-05 from event shapes, before the window run |
| withdrawal from a StakingRewards-style contract | staking | 11 | 0.02% | $12,275,080 | 0.05% | Withdrawn event and tokens leaving the called contract, no swap | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| Compound v3 operation | lending | 61 | 0.09% | $11,706,915 | 0.05% | a Comet event, no swap, no flash loan | seeded 2026-09-05 from event shapes, before the window run |
| stETH wrapped or unwrapped | staking | 27 | 0.04% | $11,365,281 | 0.04% | wstETH minted or burned with a stETH leg and no swap | seeded 2026-09-05 from event shapes, before the window run |
| payment routed through a contract that splits off a fee | payments | 80 | 0.12% | $10,647,089 | 0.04% | one asset enters the called contract and leaves it to two or more recipients within 1%; the smallest share is at most 10% | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| deposit into a service contract with a routing memo | custody | 234 | 0.35% | $10,639,315 | 0.04% | calldata holds a printable memo of 8+ characters; value or tokens enter the called contract; the contract emits its own event | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| Aster trading-treasury payout | trading_custody | 18 | 0.03% | $9,190,068 | 0.04% | observed withdrawal topic at the documented Ethereum Aster treasury plus outgoing tokens | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| swap sent straight to the pool | dex | 75 | 0.11% | $8,546,110 | 0.03% | the destination emits the swap event | seeded 2026-09-05 from event shapes, before the window run |
| ETH deposited, wrapped and forwarded by a router | vault | 67 | 0.1% | $8,502,253 | 0.03% | top-level value, a WETH Deposit credited to the called contract and WETH legs leaving it, no swap | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| Aster trading-treasury deposit | trading_custody | 34 | 0.05% | $8,136,542 | 0.03% | observed deposit topic at the documented Ethereum Aster treasury plus incoming value | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| sandwich-pattern candidate | mev | 136 | 0.2% | $7,691,373 | 0.03% | same block, same pool: actor swaps direction d at index i, a stranger swaps d at index k, the actor swaps -d at index j > k (scan marks front/back) | seeded 2026-09-05 from event shapes, before the window run |
| deposit into a contract without a record event | custody | 19 | 0.03% | $7,158,104 | 0.03% | only transfer events, every priced leg enters the called contract, no custom event | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| swap recorded by an aggregator or venue event | dex | 118 | 0.17% | $6,414,457 | 0.02% | an aggregator swap event family is present, no flash loan | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| WETH received by a contract and paid out as ETH | custody | 100 | 0.15% | $5,425,558 | 0.02% | a WETH Withdrawal by the called contract or by a contract that emits its own event, at most WETH legs into the called contract, no swap | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| swap inside sandwich-pattern candidate | mev | 42 | 0.06% | $4,798,890 | 0.02% | swap in a pool between the front and back legs of a sandwich (scan marks victim) | seeded 2026-09-05 from event shapes, before the window run |
| collection of tokens owed to a liquidity position | liquidity | 23 | 0.03% | $4,724,141 | 0.02% | Collect event with no Burn/DecreaseLiquidity and no swap in this transaction | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| flash loan without a swap | mev | 743 | 1.1% | $4,633,471 | 0.02% | a flash-loan pair and no swap event | seeded 2026-09-05 from event shapes, before the window run |
| withdrawal recorded with the observed Aster withdrawal topic | trading_custody | 35 | 0.05% | $4,502,531 | 0.02% | the observed Aster withdrawal topic from any emitter with priced token legs | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| CCIP token-send request on Ethereum | bridge | 6 | 0.01% | $4,221,758 | 0.02% | documented Ethereum CCIP router and ccipSend selector, message event, and a sender token outflow | five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05 |
| ETH staked with Lido | staking | 27 | 0.04% | $4,029,801 | 0.02% | Submitted event | seeded 2026-09-05 from event shapes, before the window run |
| positive observed-net multi-pool strategy | mev | 118 | 0.17% | $3,784,828 | 0.01% | two or more swap events across two or more pools, no flash loan, the principal contract nets >= 0 in every priced asset and > 0 in one, the EOA nets nothing | seeded 2026-09-05 from event shapes, before the window run |
| position or order opened with an NFT receipt | vault | 21 | 0.03% | $3,277,142 | 0.01% | an ERC-721 transfer, a priced leg paid by the sender, no swap, no marketplace event | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| trade whose other side is a token outside the registry | dex | 16 | 0.02% | $3,062,776 | 0.01% | no registered swap event, no flash loan; some net payer of a priced asset receives an unpriced token, or a net receiver of a priced asset sends one | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| other liquid-staking or restaking operation | staking | 16 | 0.02% | $1,263,725 | 0.0% | Rocket Pool, EigenLayer or ether.fi events, or an LST minted or burned | seeded 2026-09-05 from event shapes, before the window run |
| operator moving approved tokens through Permit2 | custody | 34 | 0.05% | $1,181,077 | 0.0% | destination is the documented Permit2 contract, selector is transferFrom (single or batch), only transfer events | day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| ETH sent with calldata into a contract that emits nothing | custody | 54 | 0.08% | $1,053,852 | 0.0% | top-level value, calldata, no logs, destination tagged contract_like or router_like | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| NFT sale | nft | 15 | 0.02% | $1,007,887 | 0.0% | marketplace event plus a priced leg and no swap; an NFT transfer alone does not establish a sale | seeded 2026-09-05 from event shapes, before the window run |
| delegated EOA executing a batch on itself | wallet | 33 | 0.05% | $605,189 | 0.0% | destination equals sender and at least one log | day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| deposit recorded with a Relay-style deposit event | custody | 10 | 0.01% | $397,228 | 0.0% | Relay-style deposit event from any emitter with value or tokens entering the called contract | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| claim of vested, distributed or reward tokens | transfer | 8 | 0.01% | $365,653 | 0.0% | a Claimed-style event family with tokens leaving the called contract, no swap | day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day |
| contract creation carrying value | wallet | 1 | 0.0% | $36,820 | 0.0% | no destination | seeded 2026-09-05 from event shapes, before the window run |

Registered types with no occurrence in this window: Spark (Aave-fork) operation, Balancer pool join or exit.

## What the window showed (LLM)

One day of Ethereum mainnet (2026-09-04 14:00 to 2026-09-05 14:00 UTC): 7,173 blocks, 1,793,396 transactions, 5,962,702 logs. The screen selected 67,572 transactions (65,290 by a position change of at least $10,000, 24,864 by gross priced legs of at least $100,000, 2,524 by an event-supported flash principal of at least $10,000), summing to $26.0B of largest position changes; 18,500 are at or above $100k, 3,434 at or above $1M, 333 at or above $10M; the median is $36,707 and the largest $389.4M. Receipts were fetched for the 7,852 no-log native transfers above the threshold; 13 had failed and were excluded.

The loop. Codex's registry from the five-hour window (58 types) typed 90.45% of the day's selected transactions and 92.95% of their USD on replay, leaving 6,455 transactions ($1.83B) in 1,765 residue clusters. Two rounds of LLM investigation on the residue added 22 mechanical types (custody vaults, payment rails, delegated-EOA execution, unregistered-token trades, settlements, sweeps, staking pools, sUSDe claims) and took coverage to 99.12% and 99.80%. A fourth round re-read one hash-sampled occurrence of every known type; it found three rules that over-reached (an Aave-fork rule accepting any four-argument Withdraw shape, an unpriced-trade rule swallowing vault deposits that mint receipt tokens, aggregator swaps landing in the bilateral-exchange type), fixed them, and added eight long-tail shapes; the final registry of 90 types covers 99.88% of transactions and 99.91% of USD, with 81 transactions ($24.6M) in 50 clusters left. Coverage measures rule matching, not verified intent: 58,094 of the 67,572 rows match more than one rule and registry order decides.

What the day was made of, by group of largest position changes: plain and helper-mediated transfers $9.54B (17,354 transactions), exchange flow $7.24B (23,334), stablecoin issuance and par conversion $2.98B (2,024), wallet infrastructure $1.66B (3,692), lending $1.66B (2,684), bridges $929M (3,330), custody and settlement contracts $778M (3,477), DEX trading $371M (5,598), vaults $334M, liquidity $185M, staking $131M, payments $76M, MEV $41M (2,425).

Exchange flow, the largest identifiable mechanism, was one-directional: 9,792 deposits into exchange-tagged wallets ($3.84B) against 7,139 withdrawals ($1.59B), a net inflow of $2.25B to wallets that receive from many sources and pay many destinations, plus 4,802 deposit-address sweeps ($1.06B) and 1,601 transfers between exchange-like wallets ($750M). The largest sink was contract 0xa9d1e08c… (6,889 bytes), which took $964M in 852 deposits and is also the origin of 729 batch payouts: an exchange's deposit-and-withdrawal contract. 0x28c6c062… took $639M in 2,142 deposits and paid $119M in 509 withdrawals; 0xcd531ae9… took $574M in 98. Deposits and withdrawals both peak in the first hours of the window (14:00 to 17:00 UTC: 836, 740, 682 deposits per hour) and trough between 23:00 and 03:00 UTC (about 285 per hour). The 14,356 plain transfers that carry no behavioural tag ($7.53B, median $40k, 88 of them above $10M) remain the largest class of unknown purpose: USDC $4.46B, USDT $1.41B, ETH $737M, cbBTC $292M; 1,346 come from wallets on their first or second transaction.

Stablecoin supply moved by hundreds of millions: USDC minted $542M and burned $409M (net +$133M), DAI minted $351M and burned $257M, USDS minted $60M and burned $95M, USDe +$26M and −$10M, RLUSD +$21.5M and −$7.5M; EURC (unregistered, priced from its swaps) minted $3.4M and burned $3.6M, Kraken's kBTC minted $3.2M, cbBTC minted $100M in nine transactions. The Sky peg-stability path converted $961M in 1,383 transactions, $490M of it in seven transactions between USDC and sUSDS. Bridges sent $527M out (LayerZero packets $188M, OFT sends $183M, CCTP v2 burns $173M, Arbitrum inbox $55M, OP portal $40M, LiFi $27M) and finalized $398M in (CCTP v2 mints $218M, LayerZero deliveries $144M). Lending: Aave v3 core $898M in 1,181 operations (USDC supplies $164M and withdrawals $150M, cbBTC supplies $91M, wstETH supplies $78M, USDT borrows $52M), Morpho Blue $178M in 943, and the Aave-v3 fork at 0xc13e21b6… (SparkLend by model memory) $273M in 83 operations of eight-figure size (wstETH withdrawals $74M, USDS repayments $71M, cbBTC supplies $42M, USDS borrows $39M).

Flash loans are the day's largest gross number and its smallest economic one: 1,386 flash-funded swap strategies borrowed $24.0B (Morpho 0xbbbb…: 1,301 loans, $22.1B; 0x26de7861…: 66 loans, $1.86B; Balancer: 68 loans, $32M), median loan $1.0M and maximum $399M, while the principal's observed net in priced assets is $0.00 at the median and at the 90th percentile and −$55k in sum: whatever these bots earn is paid in unpriced tokens, to the block builder in ETH, or not at all. 743 further flash loans ($22.3B) carried no swap. Sandwich candidates: 136 bracketing legs (79 front, 77 back) by five senders, 0xae2fc483… alone 47 legs around 27 intervening swaps, concentrated in two USDC/WETH pools; observed nets of $322 and $462 per bot over the day say the same thing about where the payoff sits. Atomic arbitrage without loans: 118 transactions with a median observed net of $1.91.

The residue investigation found a layer the pilot could not see in two minutes: custody and settlement contracts whose Ethereum legs are one-sided by design. A custody system with four vault contracts sharing one ABI (sweep, signed payout, withdraw-to-caller) moved $248M in 410 calls; ERC-7821 execute() calls moved $366M in 412 transactions from accounts that `resolve` showed to be EIP-7702-delegated EOAs (19 designators among the ~400 addresses looked up), executed by operator EOAs paying the gas; contract payouts by operators $292M (1,263), relayed payments recorded by the contract $67M (368), forwarder sweeps from 1,431 per-customer contracts $52.5M (360), a cross-chain swap service whose calldata carries USDT(TRON)|<address>|0.05|bridgers| memos ($10.6M in 234 deposits; its payouts are typed separately), payment routers that split a fee of 74 basis points at the median. DEX volume outside pools: 668 bilateral exchanges through settlement contracts ($58.5M), of which USDC into USDG (Global Dollar, resolved from the token contract) accounts for 110 transactions and $14M, and the same hot wallet 0xf70da978… (nonce 4.78M) converted USDC to USDG through a 0x-Settler-style path in 154 swaps for $55M. Eighty-two tokens outside the registry were priced from their own swaps; the largest by volume are USDG ($11.6M), PST ($10.3M), AUSD ($5.3M), USDx, fxUSD, reUSD, DOLA, PEPE, bUSD0, wTAO, SPX6900 and mUSD.

Three quant findings the rules established. (1) A dollar threshold on Ethereum selects exchange plumbing first (34% of selected transactions), then custody infrastructure, then DeFi; the day-long address profile (transactions sent, distinct destinations, distinct sources, pass-through netting) separates them without any address list. (2) Gross volume and flash principal measure bot configuration; the position-change metric plus a same-asset lend-repay pairing is what isolates economic size. (3) Contract-mediated transfers need the direction of legs relative to the called contract (into it, out of it, through it, third party to third party) and the presence of a record event to be typed; those four features, with the actor tags, typed 99.9% of USD.

## Known types, investigated with their known method

### lending

#### lending-position adjustment with swaps (336 transactions, $242,350,608)

What happens: Collateral or debt changes alongside a trade. A positive cash balance can be released collateral or newly borrowed inventory rather than arbitrage income; inspect supply, debt and withdrawal records separately.

Rule: swap events plus a lending-position event, without a matched flash-loan pair. Method: `lending`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $270,809, p90 $1,745,160, max $2,244,660. Gross priced volume $778,039,002. 43 distinct senders, 37 principals, 35 destinations. By asset of the largest position: WETH ×239 ($218,605,661), PYUSD ×16 ($11,859,665), sUSDe ×6 ($2,044,740), IMPL:0x22ae…d4c7 ×2 ($2,000,056), USDe ×8 ($1,600,000). Hourly counts from the window start: 11 11 16 9 23 25 14 11 13 11 10 9 14 39 13 4 18 8 11 12 4 11 12 27.

Operations: AaveRepay WETH ×141 $134,692,717; AaveSupply WETH ×96 $83,847,082; MorphoBorrow PYUSD ×16 $11,859,665; MorphoBorrow IMPL:0x22ae…d4c7 ×2 $2,000,056; AaveWithdraw sUSDe ×2 $1,992,287; AaveBorrow USDe ×8 $1,600,000; MorphoRepay sUSDS ×10 $1,178,617; AaveWithdraw GHO ×3 $1,161,739; MorphoRepay IMPL:0x35d8…9bc0 ×5 $660,211; AaveRepay rETH ×2 $566,611; AaveSupply rETH ×3 $527,919; AaveBorrow USDC ×1 $351,832.

Top destinations: [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e) ×102; [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ×64; [0x45e9…9215](https://etherscan.io/address/0x45e9b04942176a513b22acc1ced75c34d2fd9215) ×51; [0xf34e…bf7a](https://etherscan.io/address/0xf34eea240836c04120732218bb9cf12d790bbf7a) ×18; [0xf82e…4263](https://etherscan.io/address/0xf82ef4080a53b71093f9c470676fc80e2adc4263) ×18.

Largest examples: [0xe909…1875](https://etherscan.io/tx/0xe9090e53f864ced967070f4981a84fc012c1141eef58717ec34d8065aa381875) $2,244,660 WETH at 0x45e9…9215; [0x277b…3185](https://etherscan.io/tx/0x277b4462214b152c00fd6c4f61a81151143b572323c08d844f6e4afa0c593185) $2,244,553 WETH at 0x4d5f…14e8; [0xe895…96e2](https://etherscan.io/tx/0xe89548980abc9ff2ba8b7eb49a7d557cfa139c5b27b10da5133715bf05a496e2) $1,750,715 WETH at 0x0000…594e; [0xed07…a712](https://etherscan.io/tx/0xed07f6c5d56c729e98ed39619c288513d3bd867611cc10ee4518be2a0547a712) $1,750,711 WETH at 0x0000…594e; [0x8dfc…fa73](https://etherscan.io/tx/0x8dfc44fabf7e7c2f92172a38f0d288847a3652730f38f224931e0ac3dbc1fa73) $1,750,603 WETH at 0x0000…594e; [0x3a5f…0c32](https://etherscan.io/tx/0x3a5f52892ef8dd01f3f24a4822654fe15834ccbecc99c2ff34e400be14f10c32) $1,750,603 WETH at 0x4d5f…14e8.

#### Dolomite margin-account deposit (26 transactions, $13,807,745)

What happens: USDC passes through a deposit proxy into DolomiteMargin, which credits a numbered account. The account balance is an internal signed principal record, so a second ERC-20 share transfer is not required. The two transfer legs are one deposit.

Rule: official DolomiteMargin Ethereum address, documented LogDeposit topic and incoming assets; decode account, market, deltaWei and newPar. Method: `dolomite`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $395,889, p90 $1,053,512, max $4,080,052. Gross priced volume $29,448,910. 12 distinct senders, 12 principals, 1 destinations. By asset of the largest position: USDC ×8 ($7,086,840), USD1 ×10 ($3,546,483), ETH ×4 ($1,833,500), weETH ×3 ($945,034), wstETH ×1 ($395,889). Hourly counts from the window start: 1 0 1 0 0 0 0 4 1 1 2 0 3 0 0 0 0 2 2 1 2 0 4 2.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"from_called_contract": 26, "into_called_contract": 26}.

Decoded internal account updates: `[{"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "159999700160048532551176", "hash": "0xdd3c693f676e53b9711fda97838d2f096978d475283d209edc9d0b5b462b8119", "market_id": 1, "new_principal_signed": "154352794770001145243332", "owner": "0xd09a7afe50088781fd662bab9fe6916721c527a4"}, {"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "78573961341890005001000", "hash": "0x0f3065942702cbc54cc980ca2bc700bee8f654daeea3c7e9e0e10b1eeefa7efe", "market_id": 1, "new_principal_signed": "75804916695842270370398", "owner": "0x5695c8bb097b5fbac94c91f0193629c70797f468"}, {"account_number": "94110266977286693526971178171535580530373710976132974459847452468602802595618", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "500411400650", "hash": "0xe33890be8ca736e5356691cf667ae71a4b9ce80c0545a4684ef3696691776706", "market_id": 2, "new_principal_signed": "3454416697893", "owner": "0xade9339add86f2cc3214f232b9fe0445afc11307"}, {"account_number": "94109464780756587469648495259853447236488171397284408387891583390999089070835", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "300000000350000000550000", "hash": "0xc85af3b01b8fd418b255aacdb2f44d904eb29645fa159419ab6783f7f7669060", "market_id": 1, "new_principal_signed": "1157684504409564453779212", "owner": "0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba"}, {"account_number": "94110266977286693526971178171535580530373710976132974459847452468602802595618", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "200000000500", "hash": "0xa6f01924c55c02b6c9d168d7eb7a791a3cdb1a99d6be451ce369f3f35299d941", "market_id": 2, "new_principal_signed": "3645136471914", "owner": "0xade9339add86f2cc3214f232b9fe0445afc11307"}, {"account_number": "94109464780756587469648495259853447236488171397284408387891583390999089070835", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "150000000000000000000000", "hash": "0x4efab52689a6500e903275dc8803fb03a1b6b4b3ac784f4694c9e47b3d4cf934", "market_id": 1, "new_principal_signed": "1302387775724266624488631", "owner": "0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba"}, {"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "30000895764", "hash": "0xeda9a78efaa979f85154d61f3d2446bff1f1976add72911d570daf05da11eeec", "market_id": 2, "new_principal_signed": "60580350530", "owner": "0xd0cb56309f657d3c1ccddca7913114ee42056175"}, {"account_number": "94109464780756587469648495259853447236488171397284408387891583390999089070835", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "300000015127", "hash": "0x7b3a448c851db1c85dbcc05e2aee3d4a945663be6373f4ec2f3d61cffaecac35", "market_id": 2, "new_principal_signed": "-323282192457", "owner": "0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba"}, {"account_number": "94110266977286693526971178171535580530373710976132974459847452468602802595618", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "573116676714", "hash": "0xb7e65414c797a091788eb20b2d5e6ecb8081441a1f5d78b916d50d93dc76a43e", "market_id": 2, "new_principal_signed": "3905576179688", "owner": "0xade9339add86f2cc3214f232b9fe0445afc11307"}, {"account_number": "94109464780756587469648495259853447236488171397284408387891583390999089070835", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "692862237551080000350000", "hash": "0xdad980dea3be10829be6a6365bdf31de18b61c85e0f8e42b12bd4614c5c55a45", "market_id": 1, "new_principal_signed": "1295500041079233828914274", "owner": "0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba"}, {"account_number": "53264756084238574596407218404090591947306947719361835666810431113172161309949", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "249180000000000000000", "hash": "0xd2a5fac7e51c73448bc085d2ac44fd7c77d35ebfd8c764602c50e973f32913e6", "market_id": 0, "new_principal_signed": "-2842117998378197971738", "owner": "0xc98b5ef1ab3587e2c53013c822252578b9a056e2"}, {"account_number": "53264756084238574596407218404090591947306947719361835666810431113172161309949", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "260000000000000000000", "hash": "0xe7c180f95816e25c32a8822d335b9f6ddf5d4afab285236ffbb384e1e1361996", "market_id": 0, "new_principal_signed": "-2586676894602863537535", "owner": "0xc98b5ef1ab3587e2c53013c822252578b9a056e2"}, {"account_number": "53264756084238574596407218404090591947306947719361835666810431113172161309949", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "10400000000000000000", "hash": "0xf2cb3849e497a6593567e3890e3c9bb9b418988f9caab20c55953eb94c38b403", "market_id": 6, "new_principal_signed": "2716793969720015152323", "owner": "0xc98b5ef1ab3587e2c53013c822252578b9a056e2"}, {"account_number": "94109464780756587469648495259853447236488171397284408387891583390999089070835", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "350022001073", "hash": "0x5cd10e2fb147479f940595c5284f1b494e90fa5300384ac7848669c28a1d517a", "market_id": 2, "new_principal_signed": "-57982549", "owner": "0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba"}, {"account_number": "94110266977286693526971178171535580530373710976132974459847452468602802595618", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "1342954705264160571114312", "hash": "0x05691c1288ee54d83cabfacdded5a140f6848c2248543d08961cb29491d4e9aa", "market_id": 1, "new_principal_signed": "-659698869035933489053473", "owner": "0xade9339add86f2cc3214f232b9fe0445afc11307"}, {"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "399998020124897453138765", "hash": "0xe6a252cba5bc3f110a38188435ca1db6a852f804910f3086191e7c8de524b64c", "market_id": 1, "new_principal_signed": "385863446700230159017687", "owner": "0xc9bc1b308d8e1cc4e9bd660855143ecc61126eca"}, {"account_number": "94109761471852241449275364111252423827609347414343229674885197273671365186271", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "129659774572962543692", "hash": "0x9dc898998bb69b196aae8d4d8c2b16d561a96095aba2328832c18b493e6a676b", "market_id": 20, "new_principal_signed": "219459774572962543692", "owner": "0xe6705fccaf951870ef24463c88a81f31610efba4"}, {"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "12555000015299500014018", "hash": "0x0efb790e4ee11607c96f78706152c4d8f561845367b7a2650ec19c4ec6f02341", "market_id": 1, "new_principal_signed": "465803302937010530097689", "owner": "0x7e13ac7462cbc62440a91dd2654f1c2d1fc9180e"}, {"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "1053660245629", "hash": "0xbfbbc68fda9811a5ced4713f0ca556c40d63d8441e07b98f85080ad4d021a1ca", "market_id": 2, "new_principal_signed": "1004722696985", "owner": "0x6981cdef34aaafdc0fe50d7a73fffbb85415da22"}, {"account_number": "94110266977286693526971178171535580530373710976132974459847452468602802595618", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "355248423930250000000000", "hash": "0x950db41a8ae52069fe74d349c3b09f81cba769e2c46f8b1ff770f0b8bb3975d3", "market_id": 1, "new_principal_signed": "-327202480801047184397852", "owner": "0xade9339add86f2cc3214f232b9fe0445afc11307"}, {"account_number": "94109761471852241449275364111252423827609347414343229674885197273671365186271", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "74000000000000000000", "hash": "0x3ea31fbe779e5872632c7026145444be9ecf8fe390481b78c4af4d23f8296ae8", "market_id": 0, "new_principal_signed": "-161124820699726407386", "owner": "0xe6705fccaf951870ef24463c88a81f31610efba4"}, {"account_number": "94109346425474554652466529019160272746682138221897286713754651229573376193268", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "168449897206319512962", "hash": "0x568c139874e568fc4fe7f641388e45075b7570dce326d8f56aa933470da7ec42", "market_id": 6, "new_principal_signed": "1006035935043416417648", "owner": "0xe6705fccaf951870ef24463c88a81f31610efba4"}, {"account_number": "94109761471852241449275364111252423827609347414343229674885197273671365186271", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "164003085836927234331", "hash": "0xbfab93a1d6f770012c597a6e9d20cd515028da66f9db0733b36c717156689519", "market_id": 0, "new_principal_signed": "0", "owner": "0xe6705fccaf951870ef24463c88a81f31610efba4"}, {"account_number": "94109346425474554652466529019160272746682138221897286713754651229573376193268", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "169601366919591344576", "hash": "0x6ebb5e0e1f1bcb129f787e9d215415f70c57f667acaaa28e16ef5f6e6e92a74d", "market_id": 6, "new_principal_signed": "1175637301963007762224", "owner": "0xe6705fccaf951870ef24463c88a81f31610efba4"}, {"account_number": "32240150336664509314013882100458201794439878083374431556084268488477773350727", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "54290806684000000000000", "hash": "0xc2ee881d8500bd2677dde6518c9e6615fce5c83600d9dbd88a7d215294ad6948", "market_id": 1, "new_principal_signed": "714133979961053183105360", "owner": "0x71389dacf73a752f16139f3a49f62569dfe215b0"}, {"account_number": "0", "asset_source": "0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff", "delta_wei_signed": "4080625967555", "hash": "0x19f149ac2a151cf8855bb6452a3b419e3bacac4bf40de17f4f1352dfdbf6a338", "market_id": 2, "new_principal_signed": "3891060986173", "owner": "0x1ed39244d59f3ee811d3f1997dd78e194ca1fa78"}]`. Principal units differ from token units because of interest indexing.

Top destinations: [0xf8b2…2dff](https://etherscan.io/address/0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff) ×26.

Largest examples: [0x19f1…a338](https://etherscan.io/tx/0x19f149ac2a151cf8855bb6452a3b419e3bacac4bf40de17f4f1352dfdbf6a338) $4,080,052 USDC at 0x1ed3…fa78; [0x0569…e9aa](https://etherscan.io/tx/0x05691c1288ee54d83cabfacdded5a140f6848c2248543d08961cb29491d4e9aa) $1,342,955 USD1 at 0xade9…1307; [0xbfbb…a1ca](https://etherscan.io/tx/0xbfbbc68fda9811a5ced4713f0ca556c40d63d8441e07b98f85080ad4d021a1ca) $1,053,512 USDC at 0x6981…da22; [0xdad9…5a45](https://etherscan.io/tx/0xdad980dea3be10829be6a6365bdf31de18b61c85e0f8e42b12bd4614c5c55a45) $692,862 USD1 at 0xd24c…95ba; [0xe7c1…1996](https://etherscan.io/tx/0xe7c180f95816e25c32a8822d335b9f6ddf5d4afab285236ffbb384e1e1361996) $637,772 ETH at 0xf8b2…2dff; [0xd2a5…13e6](https://etherscan.io/tx/0xd2a5fac7e51c73448bc085d2ac44fd7c77d35ebfd8c764602c50e973f32913e6) $611,231 ETH at 0xf8b2…2dff.

#### flash-funded lending-position adjustment (54 transactions, $37,818,504)

What happens: Temporary borrowing enables a lending-position change. Read collateral and debt events separately from repayment of the temporary loan; a negative cash net may be newly supplied collateral, not a trading loss.

Rule: event-supported flash pair plus lending supply/borrow/repay/withdraw events. Method: `flash_lending`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $120,029, p90 $2,019,364, max $8,181,155. Gross priced volume $722,939,590. 32 distinct senders, 20 principals, 21 destinations. By asset of the largest position: wstETH ×7 ($14,540,638), USDC ×23 ($9,439,836), USDT ×9 ($8,483,410), WETH ×6 ($4,636,237), GHO ×5 ($446,286). Hourly counts from the window start: 6 2 0 0 1 3 8 12 3 1 0 2 0 2 0 3 0 0 0 2 0 1 3 5.

Lenders: [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) 54 loans, $142,195,927; [0xba12…f2c8](https://etherscan.io/address/0xba12222222228d8ba445958a75a0704d566bf2c8) 2 loans, $27,993. Loan size median $110,374, max $28,667,949; assets USDC ×12, USDS ×1, USDT ×18, WETH ×22, wstETH ×3. Principal net per transaction: median $0.00, p90 $740,602, sum $8,370. Gross volume without the loan legs $438,491,751. Pools per transaction: 0: 10, 1: 11, 2: 19, 3: 6, 4: 4, 5: 1, 6: 1, 10: 1, 12: 1.

Operations: AaveSupply wstETH ×7 $14,540,638; AaveSupply USDT ×8 $8,442,903; AaveSupply USDC ×9 $7,166,484; AaveSupply WETH ×6 $4,636,237; AaveWithdraw USDC ×13 $2,185,554; AaveWithdraw GHO ×5 $446,286; AaveWithdraw USDe ×1 $144,062; AaveRepay USDC ×1 $87,798; MorphoRepay sUSDS ×1 $70,957; MorphoBorrow USDS ×1 $49,975; AaveWithdraw USDT ×1 $40,507; AaveWithdraw IMPL:0x0655…4367 ×1 $7,103.

Top destinations: [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ×9; [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ×8; [0xb6f5…9dab](https://etherscan.io/address/0xb6f54caed61c318027c022c47b94baf139a99dab) ×7; [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) ×5; [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e) ×4.

Largest examples: [0xa5e5…aae7](https://etherscan.io/tx/0xa5e59bdc4b93cac9a23f441bda0e59bfa294f20b74986bd5acabd9926505aae7) $8,181,155 wstETH at 0xa175…ae94; [0xbd91…bc88](https://etherscan.io/tx/0xbd914907b5185c72e86db35aa9d1f5d4417f1d952e00a4d3d918b5afabedbc88) $3,424,230 wstETH at 0x0b92…9371; [0x71f1…3a28](https://etherscan.io/tx/0x71f1ed1361ab7d018d31c2862184b83b6ebc4206951574e5ea3d7ce3ea5c3a28) $3,294,482 USDT at 0x0000…8a90; [0x0cd2…fed4](https://etherscan.io/tx/0x0cd296fb5fc64475ec5f2eadffd1ca1a4e6ceca1943d1e6e335b3fc01d0cfed4) $3,294,445 USDT at 0x2387…086a; [0x4256…2096](https://etherscan.io/tx/0x4256d12b405b0785484d98a240e58ffcb9925335e647c77e3517c8f72eee2096) $2,019,580 USDC at 0x0000…8a90; [0x7ed0…41ac](https://etherscan.io/tx/0x7ed0d187bfbf358ea14b49202d2418e3f65a6c1920090406d8943843196c41ac) $2,019,364 USDC at 0x98c2…6f5c.

#### Aave v3 supply, borrow, repay, withdraw or liquidation (1,181 transactions, $897,789,601)

What happens: A user changes a lending position: supplies collateral (aToken minted), borrows (debt token minted), repays (debt burned), withdraws (aToken burned), or is liquidated (collateral seized by a liquidator who repays debt).

Rule: an Aave pool event, no swap, no flash loan; event emitter must be the documented Ethereum Core pool. Method: `lending`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #10.

Largest position change: median $70,000, p90 $752,442, max $143,979,739. Gross priced volume $1,007,963,342. 435 distinct senders, 425 principals, 83 destinations. By asset of the largest position: USDC ×235 ($367,960,554), cbBTC ×31 ($138,393,062), USDT ×370 ($117,025,675), wstETH ×30 ($112,469,338), WETH ×103 ($50,426,321). Hourly counts from the window start: 50 61 72 61 36 47 42 39 31 67 53 26 59 66 23 26 23 46 46 49 47 25 61 125.

Operations: AaveSupply USDC ×78 $164,478,031; AaveWithdraw USDC ×56 $150,183,062; AaveSupply cbBTC ×16 $90,982,805; AaveSupply wstETH ×13 $77,622,871; AaveBorrow USDT ×96 $52,200,676; AaveWithdraw cbBTC ×12 $47,077,123; AaveSupply WETH ×45 $42,285,574; AaveBorrow USDC ×55 $37,177,346; AaveWithdraw wstETH ×16 $34,681,798; AaveWithdraw USDT ×114 $32,786,454; AaveRepay USDe ×85 $30,724,412; AaveRepay USDT ×40 $17,206,422.

Top destinations: [0x8787…a4e2](https://etherscan.io/address/0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2) ×850; [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) ×69; [0x63ff…068b](https://etherscan.io/address/0x63ff95c79bf61486c600eb8af4cce4c0a9a4068b) ×31; [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e) ×23; [0xaf6e…b8ad](https://etherscan.io/address/0xaf6e0473f86360a91fc88564927372cdf999b8ad) ×18.

Largest examples: [0x6417…8d84](https://etherscan.io/tx/0x6417417aee8d4e8aec5ac5fd69ecb00b3dd46db9fae3fbd79b893c31d0bc8d84) $143,979,739 USDC at 0x98c2…6f5c; [0xf587…d2b9](https://etherscan.io/tx/0xf587c3e5c4801753453bd258b4d3c36ebce22b1a4f11f46c06f3ce0701b1d2b9) $143,979,739 USDC at 0x98c2…6f5c; [0x377b…14e1](https://etherscan.io/tx/0x377b7e43781227086fd46b092c20e8feffbf1bf0e78deca4dc5eb1ce1c2814e1) $44,656,167 cbBTC at 0xf506…6ec6; [0x59c6…3859](https://etherscan.io/tx/0x59c6ac85fafe9ed6e5a770b76517db548600c2289335e075e48603b1597d3859) $44,656,167 cbBTC at 0xf506…6ec6; [0xf2ad…bf5b](https://etherscan.io/tx/0xf2adf2bb141c25677dad15cf866d1d53c5592a292921eaf984ce82241ffebf5b) $44,656,167 cbBTC at 0xf506…6ec6; [0xd67e…3230](https://etherscan.io/tx/0xd67e26185b54930cad18b6f1e910d532be9e73b90e3c083def8627f834903230) $24,996,482 USDC at 0xf506…6ec6.

#### Morpho Blue market operation (943 transactions, $178,404,971)

What happens: Supply, withdraw, borrow, repay, collateral movement or liquidation on a Morpho Blue market (or a MetaMorpho vault that routes to one).

Rule: a Morpho Blue market event, no swap, no flash loan; event emitter must be the documented Ethereum Morpho Blue contract. Method: `lending`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $26,002, p90 $359,951, max $17,206,737. Gross priced volume $922,581,457. 275 distinct senders, 273 principals, 120 destinations. By asset of the largest position: USDC ×624 ($73,190,396), PYUSD ×38 ($66,410,491), USDT ×74 ($7,206,068), WETH ×27 ($5,738,323), sUSDe ×22 ($4,480,099). Hourly counts from the window start: 58 65 42 47 42 45 44 20 25 35 32 33 19 38 39 26 29 46 46 44 45 28 28 67.

Operations: MorphoSupply USDC ×390 $32,083,746; MorphoSupply PYUSD ×14 $31,788,047; MorphoWithdraw USDC ×163 $30,893,903; MorphoWithdraw PYUSD ×8 $25,169,824; MorphoRepay PYUSD ×11 $9,216,616; MorphoBorrow USDC ×41 $6,813,637; MorphoBorrow sUSDe ×21 $4,455,166; MorphoRepay IMPL:0x73e0…db98 ×1 $3,907,186; MorphoSupply USDT ×40 $3,524,141; MorphoRepay USDC ×30 $3,399,110; MorphoWithdraw WETH ×12 $2,883,991; MorphoSupply WETH ×12 $2,787,603.

Top destinations: [0x6566…0245](https://etherscan.io/address/0x6566194141eefa99af43bb5aa71460ca2dc90245) ×263; [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) ×91; [0x9e91…f9e1](https://etherscan.io/address/0x9e9110cfd24cd851ea5bc73a27975b33e308f9e1) ×83; [0xa5fc…97e2](https://etherscan.io/address/0xa5fc0f9bae6171409e7b1e8a144e4b68e50d97e2) ×27; [0xfd32…c75d](https://etherscan.io/address/0xfd32fa2ca22c76dd6e550706ad913fc6ce91c75d) ×25.

Largest examples: [0x1dc9…b8ef](https://etherscan.io/tx/0x1dc9180ce5a213124054c610877a02bdb38662ca907ae1e487442ee0d957b8ef) $17,206,737 PYUSD at 0xbbbb…ffcb; [0xf815…799b](https://etherscan.io/tx/0xf8156902e5fb4229fce1f85b0a38cd5a7744f17b357026079ae6ed6eb317799b) $13,531,524 PYUSD at 0xbbbb…ffcb; [0xc671…6e89](https://etherscan.io/tx/0xc671f88a3be98e85f48a7d0998f43cc2a9f45d5f5be2f369a9aea9dc6b306e89) $5,384,219 PYUSD at 0xbbbb…ffcb; [0x0021…f4d5](https://etherscan.io/tx/0x0021938c4d2f5146f427d47d03351f13087567699eba6d5f8d447f975ae8f4d5) $4,080,051 USDC at 0xbbbb…ffcb; [0xacf6…875a](https://etherscan.io/tx/0xacf6ded12b801988f68478ac5c6666d61d0b0b71943fa111c382841d2d80875a) $4,080,038 USDC at 0xbbbb…ffcb; [0x913d…7d78](https://etherscan.io/tx/0x913db973195ec5ec2e74dc35e82ccb0ff6f5d331dd83df90cb38cbda98387d78) $3,907,186 IMPL:0x73e0…db98 at 0xbbbb…ffcb.

#### Compound v3 operation (61 transactions, $11,706,915)

What happens: Supply or withdraw of base asset or collateral on a Comet market.

Rule: a Comet event, no swap, no flash loan. Method: `lending`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $63,850, p90 $611,250, max $1,999,719. Gross priced volume $25,274,354. 37 distinct senders, 39 principals, 11 destinations. By asset of the largest position: USDC ×23 ($4,446,675), IMPL:0x8653…9ce4 ×4 ($1,790,817), ETH ×4 ($1,742,370), wstETH ×5 ($1,414,285), WETH ×4 ($1,066,614). Hourly counts from the window start: 8 3 7 3 4 1 4 0 2 1 1 1 3 1 0 0 1 1 9 0 5 0 2 4.

Operations: CompoundV3Withdraw USDC ×8 $3,474,745; CompoundV3Withdraw IMPL:0x8653…9ce4 ×4 $1,790,817; CompoundV3Supply ETH ×3 $1,724,629; CompoundV3WithdrawCollateral wstETH ×1 $783,872; CompoundV3Supply USDC ×13 $771,958; CompoundV3Withdraw WETH ×2 $635,917; CompoundV3Supply wstETH ×3 $456,955; CompoundV3Withdraw USDT ×8 $425,540; CompoundV3WithdrawCollateral WETH ×1 $408,555; CompoundV3WithdrawCollateral WBTC ×3 $318,663; CompoundV3WithdrawCollateral USDC ×2 $199,972; CompoundV3Withdraw wstETH ×1 $173,458.

Top destinations: [0xc3d6…cdc3](https://etherscan.io/address/0xc3d688b66703497daa19211eedff47f25384cdc3) ×16; [0x3afd…0840](https://etherscan.io/address/0x3afdc9bca9213a35503b077a6072f3d0d5ab0840) ×12; [0xa397…00c7](https://etherscan.io/address/0xa397a8c2086c554b531c02e29f3291c9704b00c7) ×8; [0x852f…73c8](https://etherscan.io/address/0x852f79dad4e6c44a89be189dc3ecf51b3c5273c8) ×5; [0xb9e6…2714](https://etherscan.io/address/0xb9e62cb9b4ce8ec13c886fae67369da417ee2714) ×5.

Largest examples: [0xfe18…44ab](https://etherscan.io/tx/0xfe184b946228b2d12a5f3b388671e295535941d5d536de19b2107782c09144ab) $1,999,719 USDC at 0xc3d6…cdc3; [0x7c9f…aaed](https://etherscan.io/tx/0x7c9fd07ca52968d155057529aaff13d0e6a10ccbefc9eb3e2b56cbba8deeaaed) $791,879 IMPL:0x8653…9ce4 at 0x7447…92ef; [0x3e7d…2634](https://etherscan.io/tx/0x3e7db7efef5c9a4454a7b20f9068a430eb9d0e6f7fed2605a0639a19be822634) $783,872 wstETH at 0xa175…ae94; [0x84aa…31b5](https://etherscan.io/tx/0x84aaa497396ee34a64b7f91aaa9336a99cb16d7bcdc43b12e6c4322e200131b5) $704,665 ETH at 0xc98b…56e2; [0xedd7…7b90](https://etherscan.io/tx/0xedd7319f129a3d29f3b3bf90aafb7147790ffd1de3fab994322f1ca6b5827b90) $624,204 IMPL:0x8653…9ce4 at 0x7447…92ef; [0xffdb…7717](https://etherscan.io/tx/0xffdbe95226cd40a637fc83f245bd909988e68fc1e9131b15d33237e059fc7717) $611,409 ETH at 0xc98b…56e2.

#### lending operation on an Aave-v3-fork pool (83 transactions, $273,280,464)

What happens: Supply, borrow, repay, withdraw or liquidation with Aave v3 event shapes emitted by a pool other than the documented Aave core pool. The window's occurrences are all at 0xc13e21b6…be987, which model memory identifies as the SparkLend pool; positions are USDS, cbBTC and wstETH in the $10M-$33M range.

Rule: Aave-shaped pool event together with ReserveDataUpdated from an emitter other than the core pool, no swap, no flash loan. Method: `lending`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day. The inherited spark_op rule looked for a SparkSupply family that can never match because its signature equals AaveSupply; this entry replaces it.

Largest position change: median $377,763, p90 $10,000,053, max $32,694,694. Gross priced volume $277,582,908. 33 distinct senders, 35 principals, 6 destinations. By asset of the largest position: USDS ×26 ($110,754,728), wstETH ×8 ($99,031,276), cbBTC ×4 ($46,326,804), RLUSD ×6 ($8,229,344), USDC ×4 ($2,074,645). Hourly counts from the window start: 5 5 9 5 2 1 8 2 0 1 4 2 4 3 1 0 4 8 11 4 1 0 2 1.

Operations: AaveWithdraw wstETH ×5 $73,660,988; AaveRepay USDS ×15 $71,484,668; AaveSupply cbBTC ×2 $42,263,873; AaveBorrow USDS ×11 $39,270,060; AaveSupply wstETH ×3 $25,370,288; AaveRepay RLUSD ×5 $8,127,200; AaveWithdraw cbBTC ×2 $4,062,932; AaveSupply ETH ×9 $2,017,737; AaveWithdraw USDC ×3 $1,674,702; AaveRepay USDT ×3 $961,248; AaveRepay GHO ×1 $709,875; AaveWithdraw WETH ×4 $696,000.

Top destinations: [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) ×58; [0xbd7d…1704](https://etherscan.io/address/0xbd7d6a9ad7865463de44b05f04559f65e3b11704) ×11; [0xae05…32c8](https://etherscan.io/address/0xae05cd22df81871bc7cc2a04becfb516bfe332c8) ×10; [0x3167…4299](https://etherscan.io/address/0x3167c452fa3fa1e5c16bb83bc0fde4519c464299) ×2; [0x4e03…58b1](https://etherscan.io/address/0x4e033931ad43597d96d6bcc25c280717730b58b1) ×1.

Largest examples: [0xed6b…6ead](https://etherscan.io/tx/0xed6b0b73bca195fdea578973cbf23c66cb639a1bee8f672c71d075ae9a786ead) $32,694,694 cbBTC at 0xf506…6ec6; [0x985b…fd7b](https://etherscan.io/tx/0x985b3f156b073026d8f2afcdb8ee430e98d4239a79be428118120b76c924fd7b) $18,625,088 wstETH at 0xb656…5514; [0xa05d…9320](https://etherscan.io/tx/0xa05d548304eb47de4314bf4812f4961c93f51402547bbc53626b9f04ceba9320) $18,319,759 wstETH at 0xb656…5514; [0x4a72…9f39](https://etherscan.io/tx/0x4a72eef88567dec8e43ac34e6ee62543be05347bb7af5ffb684f8e99bde59f39) $18,319,759 wstETH at 0xb656…5514; [0x9bc3…ea16](https://etherscan.io/tx/0x9bc3c90fde11cf942aaba19d863baa5262395d690f96d2701cd04ba1f365ea16) $16,793,112 wstETH at 0xb656…5514; [0x7025…dd64](https://etherscan.io/tx/0x7025f9ba1dbfa8ecdb945661ba9397bc71a5f885cc69f8d6393c11004d65dd64) $15,000,000 USDS at 0xf506…6ec6.

LLM note on this type: Audit: the hash-sampled occurrence (0xfe63eda3…) was a 1,167-byte contract 0x4c21b757… paying USDC with a four-argument Withdraw event, which is the same ABI shape as Aave's Withdraw. Round 4 requires ReserveDataUpdated in the same transaction; the type fell from 86 to 83 occurrences ($273M), all at 0xc13e21b6…, and the three 0x4c21b757… payouts ($7.2M) are back in the residue.

### settlement

#### Relay depository settlement withdrawal (444 transactions, $17,024,798)

What happens: An allocator-authorized execute call releases escrowed tokens to a solver or nominated recipient. This is settlement inventory returning from the depository; it does not by itself prove a new user bridge withdrawal.

Rule: RelayCallExecuted emitted by the documented Ethereum depository plus a positive token outflow from that address. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $19,300, p90 $90,509, max $510,399. Gross priced volume $17,024,798. 1 distinct senders, 1 principals, 1 destinations. By asset of the largest position: USDC ×302 ($10,009,947), USDT ×127 ($6,244,664), IMPL:0xe343…491d ×8 ($542,611), WETH ×2 ($115,040), IMPL:0xaca9…35da ×2 ($61,493). Hourly counts from the window start: 42 29 29 19 18 23 17 15 15 19 18 17 30 8 9 11 15 22 13 18 16 12 12 17.

Largest observed asset sender differs from the gas payer in 444 transactions. Transfer-leg directions: {"from_called_contract": 444}.

Top destinations: [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) ×444.

Largest examples: [0x707c…d54a](https://etherscan.io/tx/0x707cddab20d5ff369c71f470dfa033877ffb31a6b6d7e259030b120f052ad54a) $510,399 USDT at 0xf70d…dbef; [0x5636…9661](https://etherscan.io/tx/0x5636afc29e74c01d4c8c366d7c16deb7e91a55a97fd1aee7fbf7967460fd9661) $500,046 USDT at 0xf70d…dbef; [0x533e…98b6](https://etherscan.io/tx/0x533e1b7934c317c5bcf2448773dbd7a5f57b93896b640dabf3c645d08d6498b6) $477,139 USDT at 0xf70d…dbef; [0x2c85…11c8](https://etherscan.io/tx/0x2c8537b3f19b64cdde32f4f6ec7577f6cbf1f0a561fe6156c5a4b2f3036811c8) $323,496 IMPL:0xe343…491d at 0xf70d…dbef; [0xbdbf…978c](https://etherscan.io/tx/0xbdbfa3420c8b136822d30a2d633ae1bf69ae2d230297298b45cb8d62e712978c) $321,509 USDC at 0xf70d…dbef; [0x4d88…2006](https://etherscan.io/tx/0x4d88590a4090c115e014215af5ab8821f85b6514062d4e648fa5750ec70a2006) $299,773 USDC at 0xf70d…dbef.

#### deposit into Relay settlement escrow (444 transactions, $20,055,499)

What happens: Tokens or native ETH enter the depository and an order identifier is recorded. A separate solver fill and settlement can happen later; destination execution is outside this Ethereum-only study.

Rule: Relay deposit event from the documented Ethereum depository plus an incoming priced leg. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $18,450, p90 $74,421, max $1,103,515. Gross priced volume $28,121,257. 219 distinct senders, 287 principals, 32 destinations. By asset of the largest position: ETH ×127 ($9,141,342), USDC ×164 ($6,743,800), USDT ×127 ($3,367,210), IMPL:0xe343…491d ×6 ($419,905), IMPL:0xe172…f904 ×10 ($180,982). Hourly counts from the window start: 45 28 30 21 16 23 18 10 17 26 17 15 17 5 13 8 18 23 9 24 15 16 13 17.

Largest observed asset sender differs from the gas payer in 177 transactions. Transfer-leg directions: {"from_called_contract": 65, "into_called_contract": 275, "third_party_to_third_party": 795}.

Top destinations: [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) ×221; [0x4337…f108](https://etherscan.io/address/0x4337084d9e255ff0702461cf8895ce9e3b5ff108) ×133; [0x89c6…f818](https://etherscan.io/address/0x89c6340b1a1f4b25d36cd8b063d49045caf3f818) ×14; [0x8d04…184b](https://etherscan.io/address/0x8d04cc7e86e687854eb41d9d43512b655b93184b) ×13; [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) ×10.

Largest examples: [0xb708…642e](https://etherscan.io/tx/0xb708a25fda1e4525090022cd0e5293379e8ea976269684bb182c9e889e4e642e) $1,103,515 ETH at 0xc3dd…2966; [0xb468…0461](https://etherscan.io/tx/0xb468b0651f4b73fa49dd42f7439aec678b135e87ea313be7cafbfaf88fa00461) $1,103,515 ETH at 0xc3dd…2966; [0x2418…9b7b](https://etherscan.io/tx/0x241869ff605e0f61a25f74f1c1f13b30775abcf5b4a240af6eab5bfa84b89b7b) $1,103,515 ETH at 0xc3dd…2966; [0xf035…f544](https://etherscan.io/tx/0xf0356bc4d1132c98a8d1bff587148ac648998a63338106535ad7a902b7fef544) $1,103,515 ETH at 0xc3dd…2966; [0x5a14…e4aa](https://etherscan.io/tx/0x5a14c9d1dcadf379f4529b69ff89a8e42f297cea3f443815db9625a91b3de4aa) $1,103,515 ETH at 0xc3dd…2966; [0x4d8e…9639](https://etherscan.io/tx/0x4d8e52056da9a58f6e86dc8e8edb3ac05103e9d4f8931fe903b2c98bc2189639) $612,818 ETH at 0xc3dd…2966.

### trading custody

#### Aster trading-treasury deposit (34 transactions, $8,136,542)

What happens: A user funds the documented trading treasury. A balance claim is created in the trading system; this transfer does not show a trade, a leverage change or a profit.

Rule: observed deposit topic at the documented Ethereum Aster treasury plus incoming value. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $100,004, p90 $391,960, max $2,432,975. Gross priced volume $8,136,542. 24 distinct senders, 24 principals, 1 destinations. By asset of the largest position: USDT ×31 ($8,087,322), USDC ×3 ($49,220). Hourly counts from the window start: 2 7 2 1 0 1 1 0 0 0 0 0 1 3 0 0 0 0 0 0 5 2 4 5.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"into_called_contract": 34}.

Top destinations: [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) ×34.

Largest examples: [0x6e0e…30cc](https://etherscan.io/tx/0x6e0e2178c8be7adf8378e31b96fbefcfdd72dce974a6eddfff0f3ec66f5230cc) $2,432,975 USDT at 0x604d…736e; [0x9ab5…6795](https://etherscan.io/tx/0x9ab578056349cbb44f9bd8aae747501bddd4c048d5dfef22a04f894aa8886795) $1,500,041 USDT at 0x604d…736e; [0x25bd…9430](https://etherscan.io/tx/0x25bd97ce01832dd4a8395a545ea07cc408f52f59fc100c91267d2f66a01b9430) $1,055,138 USDT at 0x604d…736e; [0x0e16…b16d](https://etherscan.io/tx/0x0e167dcd74e5f0e06ef82ddfe1be047e82ac33bad9ba6f904f3fa2dd67c6b16d) $391,960 USDT at 0xf728…aa38; [0x2d21…8242](https://etherscan.io/tx/0x2d21ba3c0d44d58b6a9900289f7b6b446a866eaadf943f8e930b0afcea238242) $280,012 USDT at 0xb946…5eeb; [0xe8f0…c57a](https://etherscan.io/tx/0xe8f08d5e93b9b1f09a50676c557debb4cb0b62ba285522d39bac82e117ecc57a) $230,010 USDT at 0xd9ba…5360.

#### Aster trading-treasury payout (18 transactions, $9,190,068)

What happens: The treasury releases tokens to a beneficiary following a relayed instruction. Ethereum records the payout, not the preceding account PnL or trades.

Rule: observed withdrawal topic at the documented Ethereum Aster treasury plus outgoing tokens. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $59,992, p90 $2,432,976, max $3,800,141. Gross priced volume $9,190,068. 2 distinct senders, 1 principals, 1 destinations. By asset of the largest position: USDT ×15 ($9,123,840), USDC ×2 ($41,228), USD1 ×1 ($24,999). Hourly counts from the window start: 1 3 3 0 0 1 0 1 1 1 0 0 0 0 0 1 1 0 0 0 0 1 1 3.

Largest observed asset sender differs from the gas payer in 18 transactions. Transfer-leg directions: {"from_called_contract": 18}.

Top destinations: [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) ×18.

Largest examples: [0x4c6c…a0f0](https://etherscan.io/tx/0x4c6cc1f54110227a5865d74dfc27d3ca1d47d82c6c39c6033c07cd55d288a0f0) $3,800,141 USDT at 0x604d…736e; [0xb708…f346](https://etherscan.io/tx/0xb7088fb88b3ede51e3d05e68abc1919194aade3da9da60672f104645769cf346) $2,432,976 USDT at 0x7ba0…6bd6; [0x53dd…ed55](https://etherscan.io/tx/0x53dd0218d2b53a375d1a90f7ebb4ed8ee918a8ca457896c51c88bc909c6eed55) $1,100,048 USDT at 0x99db…6e14; [0xacb9…592b](https://etherscan.io/tx/0xacb9fc942200ad3abfba9d122d89c18bcbff6d3836dd0aa26ba05b964905592b) $675,150 USDT at 0x604d…736e; [0xc631…1716](https://etherscan.io/tx/0xc6315c317cb55f62cc92269f154e854c98b646f9ccfd2519daca43581dc51716) $572,424 USDT at 0xb5de…6b78; [0xe4ca…c6a3](https://etherscan.io/tx/0xe4cabc8aeb065ad230e26bf3e7c9447d663eeffb06f642e0aae7cd45731fc6a3) $149,981 USDT at 0x7ba0…6bd6.

#### withdrawal recorded with the observed Aster withdrawal topic (35 transactions, $4,502,531)

What happens: Strategy or treasury contracts other than the documented Aster treasury emit the same withdrawal topic as tokens leave them to a user: the inherited rule pins one address, this entry records the shape.

Rule: the observed Aster withdrawal topic from any emitter with priced token legs. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $59,257, p90 $285,559, max $855,450. Gross priced volume $6,159,713. 29 distinct senders, 28 principals, 9 destinations. By asset of the largest position: WETH ×7 ($1,769,903), sUSDe ×3 ($906,451), IMPL:0xe343…491d ×8 ($667,884), USDT ×4 ($320,043), WBTC ×1 ($239,213). Hourly counts from the window start: 4 1 3 1 0 0 4 3 0 0 1 1 0 1 2 0 2 2 1 1 2 0 4 2.

Largest observed asset sender differs from the gas payer in 35 transactions. Transfer-leg directions: {"from_called_contract": 1, "into_called_contract": 7, "third_party_to_third_party": 28}.

Top destinations: [0x94e7…c485](https://etherscan.io/address/0x94e7a5dcbe816e498b89ab752661904e2f56c485) ×14; [0xe68a…42be](https://etherscan.io/address/0xe68ab4f90fe026b9873f5f276ed2d7efbbbe42be) ×6; [0x973a…5a08](https://etherscan.io/address/0x973a023a77420ba610f06b3858ad991df6d85a08) ×5; [0xba1b…08af](https://etherscan.io/address/0xba1b3d55d249692b669a164024a838309b7508af) ×3; [0x774b…e989](https://etherscan.io/address/0x774b9655413c34809c1f1b16b654465a89ebe989) ×3.

Largest examples: [0xb22d…5183](https://etherscan.io/tx/0xb22de4dca4c01e2397387fa00c3a313cf1e22f32a76d818968d53a266e815183) $855,450 WETH at 0xcca8…26c9; [0x5658…ff4b](https://etherscan.io/tx/0x565839fd081cd6d1513e138299916be2d3b984b756b6d037278f443ff4c2ff4b) $440,062 sUSDe at 0x7ac0…140e; [0x181b…80ae](https://etherscan.io/tx/0x181b698b516960667afe08846ebd08583ad4e26b56ae2ca436e037a754cd80ae) $315,518 sUSDe at 0x7ac0…140e; [0x59c1…5652](https://etherscan.io/tx/0x59c100fc6cfee102f2a635f5e67f110325933e35a514dded2f2eedb55a225652) $285,559 WETH at 0x9438…f931; [0xd3bb…4e54](https://etherscan.io/tx/0xd3bb5e1d83bf618e737fe586e4ed331e99ce0e61fbff0035990e80783f4a4e54) $250,782 USDT at 0xcca8…26c9; [0x26c9…93f1](https://etherscan.io/tx/0x26c981d338db199c271468b07787550df06d4877046c63c024908e75ea8e93f1) $239,213 WBTC at 0x9738…5934.

### bridge

#### CCIP token-send request on Ethereum (6 transactions, $4,221,758)

What happens: A sender locks tokens in a token pool and pays a separate message fee through the CCIP router. The emitted message proves initiation, not delivery on the other chain.

Rule: documented Ethereum CCIP router and ccipSend selector, message event, and a sender token outflow. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $783,872, p90 $2,312,477, max $2,312,477. Gross priced volume $4,437,237. 5 distinct senders, 5 principals, 1 destinations. By asset of the largest position: wstETH ×3 ($4,111,635), USDC ×2 ($76,823), GHO ×1 ($33,300). Hourly counts from the window start: 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 0 0 1 1 0 0 0 0 2.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"from_called_contract": 6, "into_called_contract": 6, "third_party_to_third_party": 10}.

Top destinations: [0x8022…6f7d](https://etherscan.io/address/0x80226fc0ee2b096224eeac085bb9a8cba1146f7d) ×6.

Largest examples: [0x114a…062d](https://etherscan.io/tx/0x114a12c8221f7a99e8bca12f5a33f5797d1c8b8cd3af3e965354f208a943062d) $2,312,477 wstETH at 0xca68…487a; [0x1733…44b9](https://etherscan.io/tx/0x17334a9c4f7e6cfb62fce7a8d092dd1eb4bf8844279e118c256187cd53ad44b9) $1,015,286 wstETH at 0xc98b…56e2; [0x8833…ec9d](https://etherscan.io/tx/0x8833be2cce67b405470243c241af5ab49d64ee67215d77393fedca7992faec9d) $783,872 wstETH at 0xc98b…56e2; [0xab33…7a38](https://etherscan.io/tx/0xab33c8270726c81073d35c5e7ded4ad620f1cb6cea6af06278d5301f6d347a38) $61,825 USDC at 0x447f…dcc9; [0x9f28…6fa9](https://etherscan.io/tx/0x9f2887f28d913256d43ab9d92c5eb2a7fb573d02db0761d4c7ef15e340606fa9) $33,300 GHO at 0xb7e3…e2bf; [0x9239…5dcf](https://etherscan.io/tx/0x9239640413b7f6c9738d9771f31a6d68dbfd8146fb5f9825fd67d18df9d45dcf) $14,998 USDC at 0x4988…e409.

#### deposit into a bridge toward another chain (2,361 transactions, $526,980,424)

What happens: Value is locked or burned on Ethereum and a message is sent so that it is released on another chain: an L2 deposit, a CCTP burn, a LayerZero packet.

Rule: a bridge-deposit event family. Method: `bridge`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $49,024, p90 $499,925, max $20,000,878. Gross priced volume $1,060,540,837. 869 distinct senders, 899 principals, 156 destinations. By asset of the largest position: USDC ×833 ($240,723,425), USDT ×321 ($62,504,841), ETH ×585 ($41,435,020), WETH ×203 ($33,705,979), USDe ×64 ($33,435,516). Hourly counts from the window start: 172 152 128 143 119 110 102 87 94 87 104 91 58 60 72 78 96 88 89 104 84 70 87 86.

By event family: LZPacketSent ×538 $188,244,817; OFTSent ×485 $182,943,098; CCTPv2DepositForBurn ×521 $172,552,452; CCTPDepositForBurn ×96 $54,904,671; ArbInboxMessageDelivered ×446 $54,789,242; OPTransactionDeposited ×159 $40,272,218; LiFiTransferStartedObserved ×356 $26,674,410; LineaMessageSent ×39 $14,824,382; ZkSyncNewPriorityRequest ×40 $14,535,846; AcrossFundsDeposited ×392 $13,968,318; ArbDepositInitiated ×98 $12,125,027; OPETHDepositInitiated ×30 $5,997,528; OPETHBridgeInitiated ×30 $5,997,528; WormholeLogMessagePublished ×64 $5,549,100; OPERC20DepositInitiated ×57 $5,069,298; OPERC20BridgeInitiated ×56 $5,041,798; PolygonLockedERC20 ×30 $4,526,915; SocketBridge ×11 $1,731,370; StarknetLogMessageToL2 ×2 $516,567; PolygonLockedEther ×4 $123,975; LZPacketDelivered ×1 $26,917; CCTPMintAndWithdraw ×1 $17,642; CCTPv2MintAndWithdraw ×2 $6,097.

Top destinations: [0x28b5…cf5d](https://etherscan.io/address/0x28b5a0e9c621a5badaa536219b3a228c8168cf5d) ×273; [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) ×215; [0x1a07…7a2d](https://etherscan.io/address/0x1a07cc4bd17e0118bdb54d70990d2158abad7a2d) ×202; [0x89c6…f818](https://etherscan.io/address/0x89c6340b1a1f4b25d36cd8b063d49045caf3f818) ×161; [0x1231…4eae](https://etherscan.io/address/0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae) ×117.

Largest examples: [0x6d54…d97d](https://etherscan.io/tx/0x6d54bc9f87b0a823eb25335cd98073e7b3e30e4a596ac39285847dee244cd97d) $20,000,878 USDT at 0xb873…313c; [0x9130…e977](https://etherscan.io/tx/0x91308e4951ac22ca133413f10ff4359948dfac25d9ad988021b0d87b6cabe977) $18,000,000 PYUSD at 0x1be4…57d7; [0x9058…2f5a](https://etherscan.io/tx/0x90581ef4bdc697c7feb9fb38de9e268f59bd312f2386d4e03b09558865232f5a) $16,403,448 stETH at 0xe76c…573a; [0x359a…10c8](https://etherscan.io/tx/0x359a078bb559a1f53049acb3caf222d93a9497573c5897403abf730f914710c8) $11,425,460 USDS at 0xc02a…4359; [0x54f6…84e0](https://etherscan.io/tx/0x54f65f00ccff95fd301175398a4853a87a43e22750c8782d6115075b092684e0) $11,418,706 sUSDe at 0x31b7…b95a; [0x2092…d7c0](https://etherscan.io/tx/0x2092b95ae5e48303e2ec652f397e806e95957035da819436e3f6bcd62359d7c0) $11,418,706 sUSDe at 0x31b7…b95a.

#### bridge withdrawal finalized on Ethereum (963 transactions, $397,581,357)

What happens: Value locked elsewhere is released on Ethereum: an L2 withdrawal finalized, a CCTP mint, an OFT receipt, a relayer fill.

Rule: a bridge-withdrawal event family. Method: `bridge`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $66,617, p90 $990,059, max $20,500,900. Gross priced volume $628,613,530. 156 distinct senders, 323 principals, 24 destinations. By asset of the largest position: USDC ×556 ($263,789,302), USDT ×159 ($55,237,002), USDe ×46 ($34,170,359), sUSDe ×20 ($19,295,271), IMPL:0xe343…491d ×98 ($18,748,901). Hourly counts from the window start: 76 50 60 58 41 37 52 48 31 48 47 43 28 29 17 20 26 25 60 43 39 20 34 31.

By event family: CCTPv2MintAndWithdraw ×475 $218,340,941; LZPacketDelivered ×391 $143,837,619; OFTReceived ×388 $143,766,973; CCTPMintAndWithdraw ×54 $30,177,744; PolygonExitedERC20 ×8 $4,015,062; OPRelayedMessage ×5 $729,864; OPWithdrawalFinalized ×5 $729,864; OPETHBridgeFinalized ×1 $564,153; ArbOutBoxTransactionExecuted ×29 $396,431; OPERC20BridgeFinalized ×4 $165,711; PolygonExitedEther ×1 $83,696.

Top destinations: [0x1732…3059](https://etherscan.io/address/0x173272739bd7aa6e4e214714048a9fe699453059) ×391; [0x81d4…4b64](https://etherscan.io/address/0x81d40f21f12a8f0e3252bccb954d722d4c464b64) ×312; [0x214c…adf3](https://etherscan.io/address/0x214c19fbcdfb683f2c726b4bbaf24ab483bfadf3) ×57; [0xca11…ca11](https://etherscan.io/address/0xca11bde05977b3631167028862be2a173976ca11) ×41; [0x0a99…8f81](https://etherscan.io/address/0x0a992d191deec32afe36203ad87d7d289a738f81) ×33.

Largest examples: [0xcd6c…eb93](https://etherscan.io/tx/0xcd6c3b72b63930887dcb8f2c58b1e3677fc8acfeb35ed44e481cfcae448aeb93) $20,500,900 USDT at 0xa711…6d69; [0x8717…1ce6](https://etherscan.io/tx/0x8717d79a9592bcd4b1532266c829a63d4d903318c6f544ff55bca1aabd9a1ce6) $12,977,812 USDC at 0x3730…7341; [0x1c1b…8f78](https://etherscan.io/tx/0x1c1b94f4befc345f952a14b10368f7858d841248ce8f48c4381d1506aadd8f78) $8,999,992 USDe at 0xe69f…3abb; [0xdfe8…44ad](https://etherscan.io/tx/0xdfe88c42a8f4d64781fe1d868ca304d07dac5005c3b558d0d36aff8704e044ad) $8,998,694 USDC at 0xe69f…3abb; [0xeaf1…1415](https://etherscan.io/tx/0xeaf1995ad1b0780602877b6922454bfe6d607ce9a99f33cc8f13723742c01415) $8,998,693 USDC at 0xe69f…3abb; [0x3a4e…3719](https://etherscan.io/tx/0x3a4e97cea3fe9e6eae872c53c46e2dd51e887b13feae3268d72de09ccab03719) $8,998,692 USDC at 0xe69f…3abb.

### wallet

#### contract-account token execution (1,593 transactions, $734,610,485)

What happens: The fee-paying sender instructs an account contract to move its token inventory to one or several recipients. Separating caller, asset owner and beneficiary prevents counting the relayer as the payer. Exchange ownership is unresolved.

Rule: one of three observed execution selectors; only Transfer/Approval events; all priced legs are token outflows from the called account. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $94,475, p90 $990,059, max $19,997,185. Gross priced volume $734,610,485. 24 distinct senders, 25 principals, 24 destinations. By asset of the largest position: USDC ×1532 ($717,709,994), USDT ×2 ($7,937,963), WBTC ×1 ($2,455,344), UNI ×9 ($2,147,749), LINK ×10 ($1,944,118). Hourly counts from the window start: 135 130 97 120 118 79 116 82 59 44 40 40 44 27 45 39 49 54 53 56 23 49 58 36.

Largest observed asset sender differs from the gas payer in 1593 transactions. Transfer-leg directions: {"from_called_contract": 2102}.

Top destinations: [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) ×797; [0x2744…a22b](https://etherscan.io/address/0x2744dfd9898f0babbc570cc594bbbc84b487a22b) ×388; [0x445f…bd97](https://etherscan.io/address/0x445f16314284b43dfa1fd3cd77b9dea4a1bebd97) ×187; [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) ×65; [0x1dfc…e1d4](https://etherscan.io/address/0x1dfc6bec8499fcb5e3151c7c6d27feb9d7eae1d4) ×31.

Largest examples: [0x725c…3a26](https://etherscan.io/tx/0x725cb670c7bd32c30eb2b54105d912ab0cfbf33ce6885b15d14275e43fdb3a26) $19,997,185 USDC at 0x1dfc…e1d4; [0x5298…0f8a](https://etherscan.io/tx/0x5298f4c802949fa329f2c4d985276980db729a2a76d6876d4137887be1470f8a) $12,153,124 USDC at 0x6709…24a6; [0x6ae5…775c](https://etherscan.io/tx/0x6ae55f414d087bb4f6dd7bc457b793180ddda1f363a86b441d4b8d90e841775c) $11,998,311 USDC at 0x4ed3…db1d; [0x3f95…2454](https://etherscan.io/tx/0x3f95e84eca2d9ec0b3c40809ba06aed03530894048cd47988ad21da5ba782454) $9,998,593 USDC at 0xee7a…4055; [0x1dd9…83dd](https://etherscan.io/tx/0x1dd926d5e1201a869fc3668fda819163bd4e78cb263078627c03c79681de83dd) $9,998,593 USDC at 0xcde5…9b90; [0x4537…c445](https://etherscan.io/tx/0x45378066beb7b4081dcf6d8cad272cfa05e24c4f29f00492234fe7ceb554c445) $9,998,593 USDC at 0x409f…86ef.

#### operator-mediated token-transfer batch (432 transactions, $97,438,885)

What happens: A helper moves tokens directly between third-party addresses. The transaction sender and helper can both have zero token net. The $20M example is a single USDT movement under a batch interface, not $20M owned by the gas payer.

Rule: observed helper address, four-array selector and completion topic, with direct non-mint token legs outside the helper. Method: `custody_flow`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $38,847, p90 $564,360, max $5,375,244. Gross priced volume $97,438,885. 6 distinct senders, 184 principals, 1 destinations. By asset of the largest position: USDT ×166 ($49,607,498), USDC ×266 ($47,831,387). Hourly counts from the window start: 52 41 35 33 23 20 18 18 14 9 17 12 10 11 6 18 7 20 10 11 8 12 15 12.

Largest observed asset sender differs from the gas payer in 432 transactions. Transfer-leg directions: {"third_party_to_third_party": 549}.

Top destinations: [0xee39…63b5](https://etherscan.io/address/0xee39678386f5bfc68df2c65656ec8e23f60063b5) ×432.

Largest examples: [0xb1a2…6608](https://etherscan.io/tx/0xb1a2088233f7ab495e3c6b77bcb4d04afa545a9beed16a7435dbea266a186608) $5,375,244 USDC at 0xbace…0437; [0x2e1a…9c7a](https://etherscan.io/tx/0x2e1a8895c331ddc8ec0f0c67cd0f8e7518f076a8c2b400df4991612012b99c7a) $4,072,569 USDT at 0xaa8b…3efb; [0xc53a…3a62](https://etherscan.io/tx/0xc53a56aef531560e11fb9ac13355e86c84379b9086d0ff8607b829de00303a62) $3,478,435 USDT at 0xaa8b…3efb; [0x515d…bf45](https://etherscan.io/tx/0x515db812fa594400c878b7ec922d8b5b726ee539f38125b6c7d85e0ad2f2bf45) $3,000,132 USDT at 0xaa8b…3efb; [0x6378…c3ef](https://etherscan.io/tx/0x6378329e4223fd43e3a3838995e1d72501f73452ba904c8069d8e9604587c3ef) $3,000,132 USDT at 0xaa8b…3efb; [0x489c…4573](https://etherscan.io/tx/0x489c6a9e783e4c16f783a6498269436babe775b3dbefe7e0550344bf39cb4573) $3,000,132 USDT at 0xaa8b…3efb.

#### account-abstraction bundle (710 transactions, $300,341,199)

What happens: A bundler submits user operations to the EntryPoint; the value moves on behalf of smart accounts.

Rule: UserOperationEvent. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $35,107, p90 $267,558, max $34,765,241. Gross priced volume $301,361,374. 42 distinct senders, 345 principals, 4 destinations. By asset of the largest position: USDC ×397 ($237,873,412), USDT ×274 ($54,216,697), WBTC ×1 ($6,721,171), WETH ×29 ($1,145,818), IMPL:0xa2cd…fb18 ×1 ($131,594). Hourly counts from the window start: 77 66 65 94 42 40 38 27 24 31 11 15 15 4 6 11 19 15 19 11 22 12 19 27.

Top destinations: [0x0000…a032](https://etherscan.io/address/0x0000000071727de22e5e9d8baf0edac6f37da032) ×478; [0x5ff1…2789](https://etherscan.io/address/0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789) ×161; [0x4337…f108](https://etherscan.io/address/0x4337084d9e255ff0702461cf8895ce9e3b5ff108) ×62; [0x4337…d009](https://etherscan.io/address/0x433709009b8330fda32311df1c2afa402ed8d009) ×9.

Largest examples: [0x8c68…5cee](https://etherscan.io/tx/0x8c68f6cf210dfe898f1ba902430aede591de383a9f7bb3e8bf15717a3fc35cee) $34,765,241 USDC at 0x63be…0a5d; [0xbfbe…c973](https://etherscan.io/tx/0xbfbeb2ae9bd840a48d74f43d431debe8e27af592368e8a038e5881dfbee7c973) $34,765,241 USDC at 0x5014…bebb; [0x9afa…3d0a](https://etherscan.io/tx/0x9afad0ed9af14636926eff3c585f6d957de082a20dbc0e5fdb94d7e59d583d0a) $29,995,779 USDC at 0x95ad…2c7f; [0x92ce…3a36](https://etherscan.io/tx/0x92ceb6e45458af99f2fd62a574b68996842f2592a466da3291f9cec2ca4d3a36) $29,995,779 USDC at 0x3356…5836; [0x9020…6cf0](https://etherscan.io/tx/0x9020cedff6a53b6ceab666aa7f981fb83ee2aa7a8f5125fd7f26391221596cf0) $12,000,527 USDT at 0x95ad…2c7f; [0x3da3…5395](https://etherscan.io/tx/0x3da355e4711a7889bb556d164d5964dc4215482850967561e3551d2d54125395) $10,000,439 USDT at 0x963b…0ad0.

#### call on an EIP-7702 delegated account (243 transactions, $32,630,041)

What happens: A type-4 transaction sets or uses a delegation, or a relayer calls execute() on an EOA that carries a delegation designator; the account owner moves value without paying gas.

Rule: transaction type 0x4 (execution selector alone does not prove account delegation). Method: `generic`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #7.

Largest position change: median $36,703, p90 $260,022, max $4,083,000. Gross priced volume $36,349,895. 72 distinct senders, 105 principals, 97 destinations. By asset of the largest position: USDC ×86 ($18,480,399), USDT ×126 ($13,270,294), WETH ×27 ($788,811), IMPL:0xaca9…35da ×1 ($50,495), LINK ×2 ($23,712). Hourly counts from the window start: 18 18 19 12 8 10 14 17 13 9 6 9 8 4 5 9 6 8 10 15 8 6 6 5.

Top destinations: [0x2228…6f74](https://etherscan.io/address/0x2228e5704b637131a3798a186caf18366c146f74) ×44; [0x5c3b…0ab4](https://etherscan.io/address/0x5c3b4bc50b211af4d2444169c50688a4f1cd0ab4) ×36; [0x21bc…aac9](https://etherscan.io/address/0x21bc354b5a5502df3097e8838eaab5eb0b06aac9) ×14; [0xf5e5…4c7b](https://etherscan.io/address/0xf5e5b03bd2a986b520e33073838ddc2e47dc4c7b) ×11; [0x9a74…2f0f](https://etherscan.io/address/0x9a74442ad2d0c8c2ca035a6f9b6122a085e72f0f) ×11.

Largest examples: [0x2ec8…8cc4](https://etherscan.io/tx/0x2ec865eb16f46fd1effbe2c2647bca8987170e613beceb30a08aea822c738cc4) $4,083,000 USDC at 0xf5e5…4c7b; [0xe2a1…9b74](https://etherscan.io/tx/0xe2a13dffa575e8913c4c0415f3e910037cf9e627704184b3bf2d52e4f1689b74) $2,036,319 USDC at 0x39f6…2ba3; [0x420d…526e](https://etherscan.io/tx/0x420d33f3449a48608f3d096e2e3153a5ffaf755c814eabd7cdf4a004855f526e) $2,020,985 USDC at 0xf5e5…4c7b; [0x64ba…7c90](https://etherscan.io/tx/0x64ba02656c8c200a773b7bfa808153bb053ed37d8802e9edc06bb6d4cb937c90) $2,019,186 USDC at 0x8bac…6567; [0x08a9…c8c6](https://etherscan.io/tx/0x08a924b55139021940c902c4b38e7dbf077eb4f2c3fb2bb5d821bcb731c0c8c6) $1,337,754 USDC at 0xf5e5…4c7b; [0xfbdf…c27f](https://etherscan.io/tx/0xfbdf510f61c9f8fb99eb9e612a8cbb3a506057aeeacdafc5f1c89efce8d1c27f) $1,023,379 USDT at 0x39f6…2ba3.

#### multisig (Safe) execution (268 transactions, $123,066,370)

What happens: Owners of a Safe execute a signed transaction from the Safe: a transfer, a contract call, a treasury operation.

Rule: ExecutionSuccess or ExecutionFromModuleSuccess event. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $51,264, p90 $579,021, max $11,418,706. Gross priced volume $130,067,446. 149 distinct senders, 166 principals, 148 destinations. By asset of the largest position: sUSDe ×4 ($45,674,671), USDC ×138 ($43,641,604), USDT ×87 ($20,266,801), IMPL:0x5886…81f1 ×1 ($6,125,431), WETH ×7 ($2,487,820). Hourly counts from the window start: 24 61 24 17 15 23 6 11 6 7 4 5 11 7 2 2 9 7 2 5 3 5 8 4.

Top destinations: [0x5846…d791](https://etherscan.io/address/0x58468fe6a341e1a8b904fc47c882923b6e23d791) ×23; [0x8a25…39ab](https://etherscan.io/address/0x8a25a24ede9482c4fc0738f99611be58f1c839ab) ×14; [0x0933…b9ac](https://etherscan.io/address/0x09332755c6ece5f8a9c3ca6b71650902c523b9ac) ×11; [0x5af5…f07d](https://etherscan.io/address/0x5af5194b4b0909eb978e3cf1e25333852277f07d) ×9; [0x411b…9faf](https://etherscan.io/address/0x411b461ebf4f74c391091eb4668dc4741d4a9faf) ×6.

Largest examples: [0xda12…d340](https://etherscan.io/tx/0xda1206e8c75eecf9c25aa0f83836071ffc0dee9010d3c52d61dcaa9c7621d340) $11,418,706 sUSDe at 0xb221…dc61; [0xb100…dc62](https://etherscan.io/tx/0xb10079278675b2881c8eb233e5e375a973bdf4b7ae9ffb14b5bfc6522beddc62) $11,418,706 sUSDe at 0xb221…dc61; [0xc66a…67dd](https://etherscan.io/tx/0xc66a238f9239c62d9a42e1a28fd3ccbbab1a85a0f31ccbf8b8377c39dcf767dd) $11,418,630 sUSDe at 0xb221…dc61; [0x9cde…6202](https://etherscan.io/tx/0x9cde22889bd49c10dbac600270a716fa3a59be910252c13ad653ad6cb1d36202) $11,418,630 sUSDe at 0xb221…dc61; [0x2e9d…97f7](https://etherscan.io/tx/0x2e9d0bfda523ea7c4961d8ad681ff5319daf7449e6da93db72f66039e13397f7) $9,298,691 USDC at 0xce84…f228; [0xe429…6930](https://etherscan.io/tx/0xe429ea47c57a3f9460817a248369ffba78b4b6200dbe7d7550fa7019b0b16930) $6,125,431 IMPL:0x5886…81f1 at 0xe6b2…78cc.

#### contract creation carrying value (1 transactions, $36,820)

What happens: A new contract is deployed and funded in the same transaction.

Rule: no destination. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $36,820, p90 $36,820, max $36,820. Gross priced volume $36,820. 1 distinct senders, 1 principals, 1 destinations. By asset of the largest position: ETH ×1 ($36,820). Hourly counts from the window start: 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.

Top destinations: — ×1.

Largest examples: [0x691a…65b0](https://etherscan.io/tx/0x691a2c9aff5a97ee47c9fe451d94bc5a5adfc32b00464a9d3309ae7260e465b0) $36,820 ETH at 0xee6b…54eb.

#### ERC-7821 execute() moving the account's own tokens (412 transactions, $366,443,636)

What happens: An EOA calls execute(bytes32 mode, bytes executionData) on an account and the account transfers tokens it holds. `resolve` found 23-byte EIP-7702 delegation designators on every account address in the packets (0xf90caf00…, 0x37e77355…, 0xafa1b5c1…, 0xd8eafb08…, 0x42bd41e6…, 0xc51e9af6…): these are EOAs delegated to an ERC-7821 implementation, executed by operator EOAs that pay the gas. The largest occurrences are USDC moves of $5M-$11M between the tiers of one custody stack.

Rule: selector execute(bytes32,bytes), only transfer events, every priced leg leaves the called account. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $123,064, p90 $2,000,088, max $11,053,315. Gross priced volume $366,443,636. 36 distinct senders, 125 principals, 150 destinations. By asset of the largest position: USDC ×260 ($310,796,025), USDT ×129 ($55,129,259), IMPL:0x7ddc…1989 ×8 ($295,540), CRV ×6 ($86,826), UNI ×4 ($48,691). Hourly counts from the window start: 31 48 43 30 44 50 32 11 7 12 12 9 12 3 6 6 11 5 3 8 8 7 5 9.

Largest observed asset sender differs from the gas payer in 412 transactions. Transfer-leg directions: {"from_called_contract": 412}.

Top destinations: [0x37e7…d046](https://etherscan.io/address/0x37e773558f127e782fdf5e4189ba28d67f72d046) ×54; [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8) ×26; [0x42bd…4484](https://etherscan.io/address/0x42bd41e6fd5229ec704ab8b03756c00fa8364484) ×25; [0xf90c…6019](https://etherscan.io/address/0xf90caf0030256cf8a2a100a92ede0c5b8c636019) ×20; [0xf6eb…2512](https://etherscan.io/address/0xf6eb23f42ee774b3c5f6cd416e5647ea78542512) ×12.

Largest examples: [0x2f3c…d7e6](https://etherscan.io/tx/0x2f3c690b65baaebdbaf819f137193e3a17795f0fdb7c2f5f1b54f42c3786d7e6) $11,053,315 USDC at 0xf90c…6019; [0x3714…b641](https://etherscan.io/tx/0x37145e97b7d40dcfb6127ad6def2219ab9dad0cdc04503169ddde2ddba59b641) $9,998,593 USDC at 0xd8ea…a46b; [0xb020…67e9](https://etherscan.io/tx/0xb02081c62cc789639922c6fb61ae56aa1de9988f452954e2f5d1d216c06567e9) $9,998,593 USDC at 0xd8ea…a46b; [0x5ab9…a138](https://etherscan.io/tx/0x5ab9fcbec4018d57d54dd8cce0fa2009c07da7ed7e6074345fed40ebcbd0a138) $9,997,593 USDC at 0xf90c…6019; [0x2d12…0603](https://etherscan.io/tx/0x2d12ccb9c04ab251ec7224a71009bff577591f9c7fcb9cefef9f87f202b30603) $9,509,822 USDC at 0xf90c…6019; [0x3372…beaa](https://etherscan.io/tx/0x3372323078d6dfa13e707ff5266b1be537a6222da5b939442681e8982d22beaa) $7,998,075 USDC at 0xf90c…6019.

LLM note on this type: Selector execute(bytes32,bytes) with mode word ending 7821 0001 is ERC-7821 batch execution. The largest occurrences are USDC moves between a small set of account contracts (0xf90caf00…, 0x37e77355…, 0xafa1b5c1…, 0xd8eafb08…, 0x42bd41e6…) executed by one or two operator EOAs, then out to external addresses in round $5M-$10M pieces. The inherited eip7702_delegated rule kept only type-4 transactions, which is right for proving delegation, but it left this account-contract traffic untyped. Whether each account is a contract or a delegated EOA is answered by `resolve` for the packet addresses.

#### delegated EOA executing a batch on itself (33 transactions, $605,189)

What happens: The transaction sender and destination are the same address and the call emits logs, which is only possible when the EOA carries an EIP-7702 delegation: the account executes a batch of transfers or settlements from its own code. Seen settling market-making inventory between several sub-accounts.

Rule: destination equals sender and at least one log. Method: `custody_flow`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $15,725, p90 $29,996, max $36,206. Gross priced volume $1,444,843. 11 distinct senders, 13 principals, 11 destinations. By asset of the largest position: USDC ×12 ($192,131), WETH ×9 ($172,471), USDT ×9 ($168,973), IMPL:0xe343…491d ×3 ($71,613). Hourly counts from the window start: 7 4 3 1 0 1 2 0 0 1 5 1 1 0 1 3 0 1 0 0 2 0 0 0.

Largest observed asset sender differs from the gas payer in 24 transactions. Transfer-leg directions: {"from_called_contract": 18, "into_called_contract": 5, "third_party_to_third_party": 160}.

Top destinations: [0x63d5…11cc](https://etherscan.io/address/0x63d55efde46799dc91cfa16c4be443ada07e11cc) ×19; [0xf94e…e85d](https://etherscan.io/address/0xf94e5cdf41247e268d4847c30a0dc2893b33e85d) ×5; [0x092c…cc72](https://etherscan.io/address/0x092cd1a6d222a167f5d0767e6444c8b45c92cc72) ×1; [0x98ec…8418](https://etherscan.io/address/0x98ecaa0129a9d0f52c476d95262cb6dfa2f98418) ×1; [0x5520…dadf](https://etherscan.io/address/0x55208d1607e51a59a5c24435acb8a8938c25dadf) ×1.

Largest examples: [0xb47c…e06f](https://etherscan.io/tx/0xb47c5bf86b6af702b940c7b465a4a17fe8b739d4ecd88860b0992f5294cbe06f) $36,206 IMPL:0xe343…491d at 0xf94e…e85d; [0x2947…7e8e](https://etherscan.io/tx/0x29473a4a428496877040d1831ab05702c915671893c06a1924606892f3b87e8e) $35,410 WETH at 0xd0d0…dc1c; [0xb9a1…50f9](https://etherscan.io/tx/0xb9a1616b20b5ed538ab53bd1a40d7628928ba9bfda478b28b3eb05adaa9750f9) $34,308 USDT at 0x98ec…8418; [0xce4b…046d](https://etherscan.io/tx/0xce4b3a2703621e1a66bd36af55074a0e39041d61b5fcd8d8cb6dbb8b91b8046d) $29,996 USDC at 0xfd19…78ea; [0xcb17…75b4](https://etherscan.io/tx/0xcb17d7ee45df09406014432b9629621720bf1d6294b0913b30dff97900d875b4) $29,270 USDT at 0xe319…7b27; [0x7c3e…c97b](https://etherscan.io/tx/0x7c3ee6de1951af5d44ce9760e5d175a7316b1b5627d2b3ec96e439434933c97b) $29,100 USDC at 0xf94e…e85d.

### liquidity

#### liquidity management with an embedded swap (438 transactions, $68,380,411)

What happens: One transaction combines a trade with a liquidity change. The swap can rebalance inventory used by the position; trading and liquidity legs must be investigated together.

Rule: swap events and mint/burn/collect/modify-liquidity events in the same transaction. Method: `generic`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $60,600, p90 $539,315, max $1,000,648. Gross priced volume $9,186,983,089. 98 distinct senders, 82 principals, 54 destinations. By asset of the largest position: WETH ×206 ($42,662,533), USDC ×99 ($10,516,096), crvUSD ×19 ($8,471,639), USDT ×43 ($4,840,850), WBTC ×3 ($771,487). Hourly counts from the window start: 14 19 36 9 8 17 21 30 21 9 22 18 13 21 9 17 14 12 14 21 16 17 18 42.

Top destinations: [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×206; [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ×52; [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ×45; [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ×13; [0xfc74…3db0](https://etherscan.io/address/0xfc741c4258aaa097b281fecfb4ef9c012fa73db0) ×11.

Largest examples: [0xa0ab…2bf3](https://etherscan.io/tx/0xa0ab99a8c9e057faed61f9fa3f30474902193582cfa819a49d55dddffc602bf3) $1,000,648 WETH at 0xa462…27a1; [0x7907…4ac2](https://etherscan.io/tx/0x79076161a62650376ab42d044842b0fc41342c11000a9edd28ea82a35f714ac2) $1,000,646 WETH at 0xa462…27a1; [0xde27…cc2e](https://etherscan.io/tx/0xde274b4d406dd8205cd214bb9ea2271f5bc1af5aeba56660aa64cd1969d3cc2e) $819,831 WETH at 0xe055…939f; [0xe3c4…7331](https://etherscan.io/tx/0xe3c4d50bd72543f1e7cf948473ec2e99f1afe72f2e4255a90d7b7a14087f7331) $819,735 WETH at 0xe055…939f; [0x9098…ddf2](https://etherscan.io/tx/0x90982fe203e0099e3ea3d61b627fe36cadd025162feef536409bb1946bd2ddf2) $745,420 WETH at 0x9205…f0bb; [0xa49d…9996](https://etherscan.io/tx/0xa49d9f7ab1465fcfb38f467a85a09e1814da28db8c74ef01171dd1758fe49996) $745,412 WETH at 0x9205…f0bb.

#### collection of tokens owed to a liquidity position (23 transactions, $4,724,141)

What happens: A pool or position manager pays tokens already owed. Without a positive liquidity burn in this transaction, this is not evidence of new liquidity removal; owed principal from an earlier burn and fees require position history to separate.

Rule: Collect event with no Burn/DecreaseLiquidity and no swap in this transaction. Method: `generic`. Origin: five-hour LLM investigation; round_01 packets and qual_notes.md, 2026-09-05.

Largest position change: median $81,623, p90 $699,033, max $934,421. Gross priced volume $4,766,282. 12 distinct senders, 12 principals, 1 destinations. By asset of the largest position: IMPL:0xb58e…21cb ×2 ($1,362,542), WBTC ×1 ($934,421), cbBTC ×1 ($933,132), WETH ×12 ($662,704), LBTC ×2 ($351,454). Hourly counts from the window start: 1 0 1 1 1 0 0 0 0 0 5 0 0 0 0 0 3 2 2 1 2 1 0 3.

Top destinations: [0xc364…fe88](https://etherscan.io/address/0xc36442b4a4522e871399cd717abdd847ab11fe88) ×23.

Largest examples: [0xab0b…344a](https://etherscan.io/tx/0xab0b17b03aeddc50923ea9daa11eb040b80ef39cfd7653d33535d7d8ca47344a) $934,421 WBTC at 0xe8f7…e124; [0xf335…5451](https://etherscan.io/tx/0xf3355ebf8ff6913575492f526b512d7d10a13dd5bfbd36d561f4e51c41e85451) $933,132 cbBTC at 0xe8f7…e124; [0x8420…201c](https://etherscan.io/tx/0x8420a8428499d244a067984dc3f68e3e0b91268e1c1c9d677d44e5690f30201c) $699,033 IMPL:0xb58e…21cb at 0x8e43…8cef; [0xfb3c…4bb5](https://etherscan.io/tx/0xfb3c8db76ae820d5b0f9478c3f381318f93c1ce0a0e0000fb7d261e568cd4bb5) $663,509 IMPL:0xb58e…21cb at 0x8e43…8cef; [0x11d1…09c6](https://etherscan.io/tx/0x11d1852f7ce8b3167c13c240159079b569e522398052b9524b83155f594a09c6) $295,896 tBTC at 0x85d3…a683; [0xf70e…9dad](https://etherscan.io/tx/0xf70e218a537e113e14e7423f7a96e2c0d8de702d477f03f0827a1429c8dc9dad) $175,837 LBTC at 0x7e6b…d4c1.

#### liquidity provided to a pool (165 transactions, $27,522,063)

What happens: Tokens go into a pool and a position (NFT, LP token or Curve shares) comes back.

Rule: a liquidity-add event family and no removal family. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $52,560, p90 $667,392, max $2,092,506. Gross priced volume $44,885,436. 87 distinct senders, 86 principals, 30 destinations. By asset of the largest position: USDC ×38 ($10,540,294), WETH ×39 ($3,570,149), ETH ×23 ($3,317,103), USDT ×18 ($2,118,728), crvUSD ×5 ($1,946,466). Hourly counts from the window start: 14 9 18 10 2 7 8 3 7 5 11 4 6 3 1 4 3 8 7 4 11 4 4 12.

Top destinations: [0xc364…fe88](https://etherscan.io/address/0xc36442b4a4522e871399cd717abdd847ab11fe88) ×89; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×19; [0x8dad…2379](https://etherscan.io/address/0x8dadb69f952479c4515657a877a1ecfd85c72379) ×9; [0x7a25…488d](https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d) ×5; [0x2401…6fdf](https://etherscan.io/address/0x2401c39d7ba9e283668a53fcc7b8f5fd9e716fdf) ×4.

Largest examples: [0xa242…1e18](https://etherscan.io/tx/0xa242583abfc045c965be8b07280000255f690522be1561d4417dea9d27d01e18) $2,092,506 ETH at 0xe9bf…902f; [0x9bca…fb0b](https://etherscan.io/tx/0x9bcaaf7ccd5843468d8ed352572eea4266c2715dc11d59007fa6b160b630fb0b) $1,286,548 USDC at 0xfe94…a14b; [0x84dd…220c](https://etherscan.io/tx/0x84dd5a7e15c5fb745673394478929c9516f2520995e6bb7cc26daf7224ee220c) $934,327 WBTC at 0xe8f7…e124; [0x4f39…a2cc](https://etherscan.io/tx/0x4f39f7ac883c0cdca3b51e180216eaa29b91568e8e3853c0bae3e3a51c60a2cc) $933,743 cbBTC at 0xe8f7…e124; [0x220c…407a](https://etherscan.io/tx/0x220cf0d99cb1eaf32a53ea5e4935d5471e44c5834e1e3a84296bed777056407a) $773,646 USDC at 0x7faa…f10c; [0xbea1…5304](https://etherscan.io/tx/0xbea104af9694ddd916ec9599b1740e99fb48e0608e1ea3282712207344c35304) $758,102 USDT at 0x882a…30d5.

#### liquidity withdrawn from a pool (155 transactions, $25,422,908)

What happens: A position is burned or decreased and the tokens plus fees return to the owner.

Rule: a liquidity-remove event family. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $34,639, p90 $688,638, max $2,104,022. Gross priced volume $41,878,154. 99 distinct senders, 101 principals, 28 destinations. By asset of the largest position: USDC ×39 ($12,626,982), WETH ×68 ($8,577,370), USDT ×15 ($1,668,998), WBTC ×3 ($973,495), USDe ×1 ($470,938). Hourly counts from the window start: 7 10 22 3 2 3 5 4 6 7 6 2 11 2 4 6 6 2 7 8 9 9 8 6.

Top destinations: [0xc364…fe88](https://etherscan.io/address/0xc36442b4a4522e871399cd717abdd847ab11fe88) ×76; [0x7a25…488d](https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d) ×24; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×12; [0x8dad…2379](https://etherscan.io/address/0x8dadb69f952479c4515657a877a1ecfd85c72379) ×9; [0x556b…d59e](https://etherscan.io/address/0x556b9306565093c855aea9ae92a594704c2cd59e) ×4.

Largest examples: [0x98d2…9be1](https://etherscan.io/tx/0x98d256d3ecd86c81b0cb15ca56bd08f91e3886835689fb51649b2faba6779be1) $2,104,022 WETH at 0x1d42…d801; [0x6848…e6a4](https://etherscan.io/tx/0x684836ee7fff595cbaaa9ff2c3b55cdb07f4776d17c22037e4b7b358efc6e6a4) $1,263,914 USDC at 0x383e…8559; [0x2911…340b](https://etherscan.io/tx/0x29114b4e8569a652a38b81a41a55f18b57086466a2ce92d58196a5726f40340b) $1,134,388 USDC at 0xfe94…a14b; [0x4cfa…1d05](https://etherscan.io/tx/0x4cfa1cc4655c0fa6d3557bab9e5224da006fae457a4675ebb6d217ef7dbb1d05) $826,726 WBTC at 0x882a…30d5; [0xd0f4…9e3e](https://etherscan.io/tx/0xd0f450bbe0d8d8bb34b24b03129ee62b3a1fc79f008e9ec8069b507aef849e3e) $773,599 USDC at 0x7faa…f10c; [0x3502…5008](https://etherscan.io/tx/0x3502f00c7df937db67881f09f8e7de78da17ad7d29740bb5c1094c0cd0575008) $752,442 USDT at 0x882a…30d5.

#### Uniswap v4 liquidity change (226 transactions, $58,628,449)

What happens: ModifyLiquidity on the v4 pool manager.

Rule: ModifyLiquidity event. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $57,299, p90 $234,804, max $9,775,265. Gross priced volume $75,193,953. 82 distinct senders, 81 principals, 12 destinations. By asset of the largest position: PYUSD ×4 ($24,207,977), IMPL:0x22ae…d4c7 ×4 ($14,480,505), USDC ×74 ($6,566,779), WETH ×13 ($3,913,763), USDT ×50 ($3,323,330). Hourly counts from the window start: 15 11 10 9 9 12 19 6 3 10 12 6 10 4 5 13 15 8 11 5 9 3 7 14.

Top destinations: [0xbd21…ee9e](https://etherscan.io/address/0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e) ×186; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×19; [0x2e6e…3bda](https://etherscan.io/address/0x2e6e879648293e939aa68ba4c6c129a1be733bda) ×4; [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ×4; [0x3a0b…bc2b](https://etherscan.io/address/0x3a0be729eaf6382e9daaa9e0938c83731525bc2b) ×3.

Largest examples: [0x7cb2…3c85](https://etherscan.io/tx/0x7cb2da1c9c9eca7d0913c8334bdc8e2cff7836a1474ee143ba4a2d22d4813c85) $9,775,265 PYUSD at 0x7a9e…cb98; [0x325d…2227](https://etherscan.io/tx/0x325d691a5da257534463df3dd44f1e135a757fcebd887a497214ba44cdb22227) $7,477,699 PYUSD at 0x7a9e…cb98; [0xd524…c0da](https://etherscan.io/tx/0xd524d0d336e51a526dc6000ded9be2930a54d0e0035975ebda186bad5c96c0da) $6,938,338 PYUSD at 0x7a9e…cb98; [0x8bb1…e8f8](https://etherscan.io/tx/0x8bb18239a89252f081db2f758aa5091cdabc49f2a77bf7d2827a79c76b70e8f8) $5,370,172 IMPL:0x22ae…d4c7 at 0x7a9e…cb98; [0x765b…c7a3](https://etherscan.io/tx/0x765b4cfc653001121a28b0058a662006a0b8cce2f3f8a71f2f3b8bde0e49c7a3) $5,096,552 IMPL:0x22ae…d4c7 at 0x7a9e…cb98; [0x85aa…3bf0](https://etherscan.io/tx/0x85aab76541ca30848ac6873db2e79471c92fe9b3f426d6c97af1dcab6b173bf0) $4,003,766 IMPL:0x22ae…d4c7 at 0x7a9e…cb98.

### dex

#### CoW Protocol batch settlement (380 transactions, $28,123,688)

What happens: A solver settles one or more signed orders against pools or its own inventory in one transaction; users' tokens move through the settlement contract.

Rule: Trade event from the settlement contract; event emitter must be the documented Ethereum settlement contract. Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $24,996, p90 $185,153, max $1,086,014. Gross priced volume $193,061,892. 64 distinct senders, 88 principals, 13 destinations. By asset of the largest position: USDC ×99 ($6,408,525), WETH ×42 ($4,421,583), USDT ×54 ($3,437,079), sUSDe ×10 ($3,221,971), stETH ×16 ($1,916,534). Hourly counts from the window start: 33 29 21 24 14 19 17 24 5 18 16 12 7 6 4 9 14 17 12 16 9 11 16 27.

Pairs (sold -> bought): ? -> ? ×203 $15,713,112; ? -> USDT ×33 $1,358; ? -> USDC ×31 $959.71; ? -> WETH ×14 $541.65; ? -> IMPL:0x35d8…9bc0+USD0 ×3 $415.84; ? -> wstETH ×3 $319.22; ? -> IMPL:0x98a8…4665 ×3 $145.47; ? -> UNI ×5 $110.43. Size median $10,190, p90 $100,088. Destinations: [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) ×185; [0x8f58…5cb7](https://etherscan.io/address/0x8f5835e9d756c9bd934bce527157a4b0ef3c5cb7) ×89; [0xb222…157a](https://etherscan.io/address/0xb222da0f9c22ad2addcb0b0d6b150f398e44157a) ×37; [0xbee1…cccc](https://etherscan.io/address/0xbee162fa5ae892be74f3f3e01c23da89adbccccc) ×25; [0x1921…77de](https://etherscan.io/address/0x1921e0ff550c09066edd4df05d304151c45e77de) ×21; [0xa9d6…2392](https://etherscan.io/address/0xa9d635ef85bc37eb9ff9d6165481ea230ed32392) ×9. Pools per transaction: 0: 205, 1: 72, 2: 30, 3: 17, 4: 16, 5: 12, 6: 28. Sandwiched: 0.

Largest examples: [0x44bf…dd78](https://etherscan.io/tx/0x44bf4a3f114f229a0e79ea4ee40392c6d9e264697da4a283cc8fcc4200f3dd78) $1,086,014 WETH at 0x2a2e…3947; [0x7c18…7054](https://etherscan.io/tx/0x7c18408a7a0fe6507d24ceb202db656157a6cb133f810c25c18d9bb0499a7054) $857,685 WETH at 0x4f20…fe64; [0x6912…5cdf](https://etherscan.io/tx/0x69128109c3b3fa33bb2074e4a49fab5f55b7c5b45687a3a711912a8a67d25cdf) $705,070 WETH at 0x51c7…2a7f; [0xb78b…f6fb](https://etherscan.io/tx/0xb78be479f0bb03e2ce7df71c0181f0cacb9c14411b189c456bbe74e274b6f6fb) $678,317 sUSDe at 0x17b6…376f; [0x7024…40e4](https://etherscan.io/tx/0x7024b1dfcda88ac2349743051a3369988b582d0ba9ec011bc09af60da15240e4) $675,824 sUSDe at 0x17b6…376f; [0x7292…5ff5](https://etherscan.io/tx/0x7292bd4ecc04c51b8840c4d8cffc1caeea3b9e07c35745265582c5c21aa35ff5) $623,317 sUSDe at 0x17b6…376f.

#### intent, limit-order or RFQ fill (469 transactions, $22,360,527)

What happens: A filler or market maker executes a user's signed order (UniswapX, 1inch limit orders, 0x RFQ): the user gets a quoted amount, the filler sources it.

Rule: UniswapX Fill, 1inch OrderFilled or 0x fill events. Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $20,555, p90 $100,158, max $981,281. Gross priced volume $3,290,692,300. 144 distinct senders, 195 principals, 50 destinations. By asset of the largest position: USDT ×97 ($5,116,427), USDC ×128 ($4,561,814), WETH ×80 ($3,378,572), WBTC ×62 ($2,301,024), DAI ×5 ($2,108,773). Hourly counts from the window start: 49 27 32 31 11 21 18 19 8 13 11 11 23 20 8 13 19 23 25 31 12 14 17 13.

Pairs (sold -> bought): ? -> ? ×322 $14,811,810; WETH -> USDT ×14 $597,207; tBTC -> USDC ×1 $398,678; IMPL:0x4580…af78 -> USDC ×2 $319,210; USDC -> USDT ×4 $312,020; WETH -> USDC ×12 $301,531; ETH -> USDC ×2 $280,978; USDC -> UNI ×3 $276,496. Size median $19,200, p90 $100,018. Destinations: [0x225a…dc17](https://etherscan.io/address/0x225a38bc71102999dd13478bfabd7c4d53f2dc17) ×166; [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ×46; [0xbee3…a000](https://etherscan.io/address/0xbee3211ab312a8d065c4fef0247448e17a8da000) ×37; [0x33b4…629c](https://etherscan.io/address/0x33b41fe18d3a39046ad672f8a0c8c415454f629c) ×34; [0xcd74…db88](https://etherscan.io/address/0xcd74725122b3f1c776521a8af4183e41c012db88) ×33; [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×24. Pools per transaction: 0: 295, 1: 66, 2: 44, 3: 12, 4: 19, 5: 5, 6: 28. Sandwiched: 0.

Largest examples: [0x14c9…48fc](https://etherscan.io/tx/0x14c99e5e584f1885220e4c71ba834655da1e042567d1dc392234c2787d0948fc) $981,281 DAI at 0x51c7…2a7f; [0xd455…1017](https://etherscan.io/tx/0xd45589ea504c0311b4064af1eed74013f60a31539ebfe0255e0d3f318cd81017) $500,279 WETH at 0x51c7…2a7f; [0x9870…e495](https://etherscan.io/tx/0x987094576ef9c40b2d5cb59f949c2d69311a0adaafd67f3288e54716abb6e495) $500,022 USDT at 0x51c7…2a7f; [0xf0f9…a485](https://etherscan.io/tx/0xf0f976b23ade35d4ac0947c1d197b881bbfbfac6aa88a3e880fce7ef7720a485) $499,833 DAI at 0x7b4f…4e20; [0xf36f…ea54](https://etherscan.io/tx/0xf36f2e1d0323ec71662e1b6a34c96ec44c735c365af3bddebb7a8888c64fea54) $499,833 DAI at 0x7b4f…4e20; [0x68be…de75](https://etherscan.io/tx/0x68bef0cbed6ec62aaedad1d8168ed76d7eb65a4de044e44957e5948967f6de75) $398,678 tBTC at 0x05ec…0055.

#### user swap through a router (855 transactions, $117,843,622)

What happens: An externally owned account sells one asset and receives another in one transaction through a router or aggregator; the EOA's own balances change on both sides.

Rule: swap event(s), no flash loan, the sending EOA nets negative in one asset and positive in another, destination is not the pool itself. Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $39,994, p90 $342,476, max $2,625,752. Gross priced volume $655,248,544. 453 distinct senders, 453 principals, 68 destinations. By asset of the largest position: USDC ×194 ($34,821,053), IMPL:0xe343…491d ×77 ($29,156,819), USDe ×75 ($15,578,572), USDT ×120 ($12,780,234), ETH ×82 ($4,632,159). Hourly counts from the window start: 63 52 52 41 44 41 37 46 25 46 41 33 32 37 20 14 21 34 28 26 23 19 35 45.

Pairs (sold -> bought): IMPL:0xe343…491d -> USDC ×62 $28,735,528; USDC -> IMPL:0xe343…491d ×92 $26,636,169; USDT -> USDC ×73 $11,393,026; USDe -> USDC ×40 $9,864,754; USDC -> USDe ×21 $4,030,762; USDC -> USDT ×50 $3,230,704; ETH -> USDC ×50 $2,831,287; cbBTC -> tBTC ×1 $2,625,752. Size median $39,994, p90 $342,476. Destinations: [0x4c82…2cca](https://etherscan.io/address/0x4c82d1fbfe28c977cbb58d8c7ff8fcf9f70a2cca) ×122; [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) ×109; [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×101; [0x6a00…1068](https://etherscan.io/address/0x6a000f20005980200259b80c5102003040001068) ×98; [0x0000…2734](https://etherscan.io/address/0x0000000000001ff3684f28c67538d4d072c22734) ×92; [0x0889…2c9a](https://etherscan.io/address/0x0889e9327b98d7d1be3c301a4585ff3330502c9a) ×36. Pools per transaction: 1: 366, 2: 173, 3: 135, 4: 75, 5: 42, 6: 64. Sandwiched: 0.

Largest examples: [0xa970…9485](https://etherscan.io/tx/0xa970931baee117305389f8e13fb959e0f5143466a08cc50c1c11151e91059485) $2,625,752 tBTC at 0xa79a…dd4c; [0xaa0d…e253](https://etherscan.io/tx/0xaa0d6fc14d9477fcb6ead62b66fcd72e967a7ad2e6bdc1d11e7be5036baae253) $2,400,105 USDT at 0xbebc…f1c7; [0xe191…5c4f](https://etherscan.io/tx/0xe191b2d8a352945b5ef0b4219b28103ce2719f84f5292f3b84b49d6f351a5c4f) $2,347,913 IMPL:0xe343…491d at 0xf70d…dbef; [0xfdea…2a13](https://etherscan.io/tx/0xfdeafa559e5241dbde53e02ea4ecdc674628b945e16e22b07190c0b16cab2a13) $2,000,088 USDT at 0xbebc…f1c7; [0x7469…3d63](https://etherscan.io/tx/0x7469c042ad3c5e08cbda59747046def2dbbf2bccff66b018a48820316d823d63) $1,800,079 USDT at 0xbebc…f1c7; [0x81bf…f747](https://etherscan.io/tx/0x81bf3252188523e5a794c71ff58a4b0007256a7d378cf41c57425badfc4df747) $1,791,585 IMPL:0xe343…491d at 0xf70d…dbef.

#### swap by a contract principal (1,532 transactions, $58,918,826)

What happens: A contract (smart wallet, vault, bot, treasury) is the party whose balances change on both sides of a swap; the EOA only pays gas.

Rule: swap event(s), no flash loan, the destination contract nets negative in one asset and positive in another. Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $19,973, p90 $81,401, max $981,725. Gross priced volume $160,651,888. 186 distinct senders, 29 principals, 26 destinations. By asset of the largest position: WETH ×675 ($25,286,879), USDC ×255 ($9,914,055), USDT ×136 ($7,909,475), WBTC ×241 ($6,552,926), UNI ×68 ($2,295,836). Hourly counts from the window start: 306 166 109 82 29 59 51 50 31 28 50 38 32 43 42 53 36 57 54 72 35 14 32 63.

Pairs (sold -> bought): WETH -> USDC ×218 $6,479,630; USDC -> WETH ×203 $5,882,708; WETH -> USDT ×42 $3,561,536; USDC -> USDT ×27 $3,396,622; WETH -> UNI ×71 $3,295,724; USDT -> WETH ×37 $2,313,083; WBTC -> USDT ×95 $2,292,729; UNI -> WETH ×60 $2,151,912. Size median $19,582, p90 $73,342. Destinations: [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) ×761; [0xbdb3…47b6](https://etherscan.io/address/0xbdb3ba9ffe392549e1f8658dd2630c141fdf47b6) ×526; [0x0000…fad4](https://etherscan.io/address/0x0000000aa232009084bd71a5797d089aa4edfad4) ×70; [0xeff6…a167](https://etherscan.io/address/0xeff6cb8b614999d130e537751ee99724d01aa167) ×40; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×37; [0xbee3…a000](https://etherscan.io/address/0xbee3211ab312a8d065c4fef0247448e17a8da000) ×28. Pools per transaction: 1: 1080, 2: 96, 3: 17, 4: 25, 5: 10, 6: 304. Sandwiched: 0.

Largest examples: [0xd3ff…b575](https://etherscan.io/tx/0xd3ffb80f0a5e64dd326ae27e49524199032fc95be920519722f621a61677b575) $981,725 USDe at 0xbca3…5afa; [0x7c4f…31a9](https://etherscan.io/tx/0x7c4f083b58212113a44030df83fcf023f712856581668d9d1bf3c6ee123331a9) $575,019 WETH at 0xbdb3…47b6; [0xe6e1…e707](https://etherscan.io/tx/0xe6e1e1ab2e4bb7415bc4bef544fd4efa7cd3d38f98c6976c09d4fe2a79c5e707) $512,848 WETH at 0x51c7…2a7f; [0x3e5b…40b4](https://etherscan.io/tx/0x3e5b9ed903ff845fe6285a7a8b6e4095a3a61a4ddc1bb395dd021e49c79840b4) $426,824 WETH at 0xbdb3…47b6; [0xa808…cb28](https://etherscan.io/tx/0xa8081ab0b35dd7067cd36cf8614f57f42567c6d5e9e83cf1c6f4ad1d662acb28) $400,000 USDT at 0xbca3…5afa; [0x3d92…49e3](https://etherscan.io/tx/0x3d92c8a37def355d51fd3da20fe86a21c3ee5098e6522adf8efd5b2d166a49e3) $399,947 USDT at 0xbca3…5afa.

#### swap sent straight to the pool (75 transactions, $8,546,110)

What happens: The transaction calls the pool contract itself rather than a router: a bot or an integrator that handles callbacks itself.

Rule: the destination emits the swap event. Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $99,919, p90 $112,998, max $1,247,920. Gross priced volume $17,090,290. 25 distinct senders, 25 principals, 5 destinations. By asset of the largest position: USDC ×6 ($3,639,282), IMPL:0x22ae…d4c7 ×18 ($1,817,763), IMPL:0xa1fa…33f8 ×27 ($1,463,623), USDT ×22 ($1,419,871), IMPL:0x2323…aa71 ×2 ($205,570). Hourly counts from the window start: 18 1 7 5 5 21 2 5 0 0 0 0 0 0 1 4 3 0 2 0 0 1 0 0.

Pairs (sold -> bought): USDC -> IMPL:0x0000…012a ×3 $2,527,027; IMPL:0x22ae…d4c7 -> USDC ×19 $1,930,764; IMPL:0xa1fa…33f8 -> USDT ×29 $1,654,209; IMPL:0x0000…012a -> USDC ×1 $979,149; USDT -> IMPL:0xa1fa…33f8 ×9 $850,401; USDT -> DAI ×11 $378,885; IMPL:0x2323…aa71 -> USDC ×2 $205,570; USDC -> IMPL:0x2323…aa71 ×1 $20,106. Size median $99,919, p90 $112,998. Destinations: [0xe521…6c45](https://etherscan.io/address/0xe521ba88837b2726e5343cca91ada6f19f356c45) ×38; [0x40d6…5328](https://etherscan.io/address/0x40d66b5f8f1521f97c2aca54dd200fe3ca035328) ×19; [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) ×11; [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) ×4; [0xf4d0…96d7](https://etherscan.io/address/0xf4d0cf32908b2c7f1021339c43df0f77f06896d7) ×3. Pools per transaction: 1: 75. Sandwiched: 0.

Largest examples: [0x153e…3d2d](https://etherscan.io/tx/0x153e31ec524d937f4756553e91f9526b6604d3e0ab80d69d9d15a135d4e23d2d) $1,247,920 USDC at 0xa994…3827; [0xd5a0…5e99](https://etherscan.io/tx/0xd5a038a630965934b1b7911798929a16b82432490d4d76afb67cd9b8946a5e99) $979,149 USDC at 0xb00f…f58d; [0xdc41…063b](https://etherscan.io/tx/0xdc41b776cbb029076e51e670a9ac01b5679729d9d16f76cfb4dee6f0138e063b) $979,149 USDC at 0xb00f…f58d; [0x3aaf…4040](https://etherscan.io/tx/0x3aaf694892834d209cf76f16709a847ed5501b78c6579d0698cb155157034040) $299,958 USDC at 0xd920…fd23; [0x57c4…b662](https://etherscan.io/tx/0x57c4517477f4686a501ea0af5948aa0b89dac855248e4e85e4bfe6557cbeb662) $200,841 USDT at 0xe521…6c45; [0x8019…88d8](https://etherscan.io/tx/0x80196fdcea5402042cb0da4f1a63e3ced9a2c7b9f4bd46800418a14f70bf88d8) $195,404 IMPL:0x2323…aa71 at 0xf4d0…96d7.

#### swap with an unclear principal (1,485 transactions, $66,862,040)

What happens: Swap events are present but neither the EOA nor the destination ends two-sided: the beneficiary is a third address, or the priced legs are incomplete.

Rule: swap event(s) not matched by the rules above. Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $21,098, p90 $93,017, max $999,859. Gross priced volume $2,024,804,615. 601 distinct senders, 426 principals, 146 destinations. By asset of the largest position: USDC ×355 ($26,587,618), USDT ×275 ($10,346,416), WETH ×249 ($5,601,017), WBTC ×97 ($4,570,456), crvUSD ×54 ($4,494,261). Hourly counts from the window start: 160 127 74 71 68 53 50 69 66 56 64 68 53 54 39 37 37 43 75 84 43 26 31 37.

Pairs (sold -> bought): ? -> ? ×904 $42,874,346; USDC -> ? ×84 $5,513,555; ETH -> ? ×99 $4,335,180; USDT -> ? ×87 $2,885,262; cbBTC -> ? ×6 $508,713; wstETH -> ? ×4 $499,569; ? -> USDC ×94 $457,004; IMPL:0xe343…491d -> ? ×23 $425,883. Size median $19,172, p90 $87,447. Destinations: [0x93c3…dd17](https://etherscan.io/address/0x93c30e6e09f698cfea99b09b5166ed90cfaedd17) ×238; [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×85; [0xec6f…23db](https://etherscan.io/address/0xec6fc9be2d5e505b40a2df8b0622cd25333823db) ×70; [0x8d04…184b](https://etherscan.io/address/0x8d04cc7e86e687854eb41d9d43512b655b93184b) ×62; [0x2d83…aded](https://etherscan.io/address/0x2d83ff1cb1c79c68fe530d35f439a92a645faded) ×59; [0xcbc6…8bf2](https://etherscan.io/address/0xcbc6ec2db48b469b6bd93816701bc5089da78bf2) ×58. Pools per transaction: 1: 963, 2: 225, 3: 113, 4: 50, 5: 39, 6: 95. Sandwiched: 0.

Largest examples: [0x5b74…ce9a](https://etherscan.io/tx/0x5b7429eed39e01d618bc0125f91388e630fb4862424f75565add854c5568ce9a) $999,859 USDC at 0x2ae2…78ae; [0xf97d…2c7f](https://etherscan.io/tx/0xf97d46fb2727f020394f681d4d35dab1f0ca7bc8bf6f611a253de4d421c62c7f) $995,874 USDC at 0xbebc…f1c7; [0xca92…1e9f](https://etherscan.io/tx/0xca92320e415ad712e00ec03ad21d9dcb846015324217bbd581a56bd4e8db1e9f) $995,729 USDC at 0xbebc…f1c7; [0x38c5…4efe](https://etherscan.io/tx/0x38c534cb198cf9b7970c64b554ed843f5116a5fba3b4a83192f6c019e4c44efe) $995,719 USDC at 0x82f6…66b7; [0xad71…4ce4](https://etherscan.io/tx/0xad71383886ea9c9d8cb08e51f97beccdc7c69812d9d439d2e4d802eeb6ed4ce4) $995,714 USDC at 0xbebc…f1c7; [0xffd4…11fd](https://etherscan.io/tx/0xffd451e9e1dc41f253fdb3727290d4479e4155966b7b32490f3b89b74e4d11fd) $995,709 USDC at 0xbebc…f1c7.

#### swap recorded by an aggregator or venue event (118 transactions, $6,414,457)

What happens: An aggregator router (Kyber-style Swapped/Exchange, LiFi generic swap, 0x TransformedERC20, DODO) records the trade in its own event while the pools it used may emit no registered swap event. The audit found such transactions typed as bilateral exchanges; this entry precedes that rule.

Rule: an aggregator swap event family is present, no flash loan. Method: `swap`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $35,869, p90 $105,892, max $514,898. Gross priced volume $30,175,543. 74 distinct senders, 75 principals, 20 destinations. By asset of the largest position: USDC ×45 ($1,929,892), USDT ×13 ($1,620,815), IMPL:0xe343…491d ×18 ($986,672), sUSDe ×6 ($707,011), USDe ×15 ($474,002). Hourly counts from the window start: 6 8 8 4 6 7 3 11 5 10 11 5 6 4 1 4 4 3 2 1 2 2 5 0.

Pairs (sold -> bought): USDT -> USDC ×7 $1,235,696; IMPL:0xe343…491d -> USDC ×12 $917,591; sUSDe -> USDe ×4 $635,784; USDC -> ? ×15 $600,173; ? -> ? ×15 $497,779; USDC -> IMPL:0xe343…491d ×12 $462,783; ETH -> USDC ×9 $446,838; USDC -> USDT ×6 $330,042. Size median $28,996, p90 $105,875. Destinations: [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×55; [0x89c6…f818](https://etherscan.io/address/0x89c6340b1a1f4b25d36cd8b063d49045caf3f818) ×11; [0x5523…227e](https://etherscan.io/address/0x5523985926aa12ba58dc5ad00ddca99678d7227e) ×10; [0x8d04…184b](https://etherscan.io/address/0x8d04cc7e86e687854eb41d9d43512b655b93184b) ×9; [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) ×6; [0x97ca…3ea5](https://etherscan.io/address/0x97caca78ac2a94c67643d07843f85afaa44a3ea5) ×4. Pools per transaction: 0: 118. Sandwiched: 0.

Largest examples: [0xa762…179c](https://etherscan.io/tx/0xa7623fc9d8a30c887766c647ce8572ac68ece7486d9bb23e6b0736b95aeb179c) $514,898 USDT at 0xe3d4…f2ef; [0x9ca7…5c90](https://etherscan.io/tx/0x9ca780f56dfb1f8e40775e0b026523faae30b2d8b9e9510e5356fa5ec3e25c90) $500,017 USDT at 0x5470…121e; [0x9b55…b4d1](https://etherscan.io/tx/0x9b55d7d6ef916b67893d454429c273bca8f75a383460abe8c63ad7b707d7b4d1) $224,394 sUSDe at 0x9484…4396; [0x3f39…2397](https://etherscan.io/tx/0x3f3908246a0839e730490d3f7d76787a5f3f596d3cd08b542165b8b192862397) $200,037 USDC at 0xcefc…cae5; [0x6d69…5643](https://etherscan.io/tx/0x6d6977e4fc3503ee692f379a48871372d5b6c1eb9123e5940a8610b1f38b5643) $174,464 IMPL:0xe343…491d at 0x9fea…b899; [0x3be0…fe11](https://etherscan.io/tx/0x3be00dff23ea95c85e81b5b108efea00cd9d5daf209922ce7e9950e85c86fe11) $162,062 sUSDe at 0x9484…4396.

#### trade whose other side is a token outside the registry (16 transactions, $3,062,776)

What happens: An address pays a priced asset and receives a token the scan cannot price (or the reverse) in one transaction, through a venue that emits no registered swap event: 0x-Settler-style anonymous logs, resolver fills that record per-account settlement events, OTC contracts. The trade is real but only one side is valued, so the position change overstates what the principal gave up.

Rule: no registered swap event, no flash loan; some net payer of a priced asset receives an unpriced token, or a net receiver of a priced asset sends one. Method: `swap`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $40,257, p90 $960,489, max $992,846. Gross priced volume $3,189,859. 13 distinct senders, 13 principals, 11 destinations. By asset of the largest position: USDC ×6 ($2,038,638), ETH ×4 ($676,877), WBTC ×1 ($196,694), USDT ×3 ($103,060), LINK ×1 ($25,006). Hourly counts from the window start: 2 3 3 0 0 1 3 0 2 0 0 0 0 0 0 1 0 0 0 1 0 0 0 0.

Pairs (sold -> bought): ? -> USDC ×5 $1,993,645; ETH -> ? ×4 $676,877; ? -> WBTC ×1 $196,694; ? -> USDT ×2 $66,421; USDC -> ? ×1 $44,994; USDT -> ? ×1 $36,639; ? -> LINK ×1 $25,006; ? -> crvUSD ×1 $22,500. Size median $40,257, p90 $960,489. Destinations: [0xe655…e62e](https://etherscan.io/address/0xe655790552c68f2871eb44b2cfe3dcfe6a63e62e) ×3; [0xb47e…3bbb](https://etherscan.io/address/0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb) ×2; [0x0796…0000](https://etherscan.io/address/0x07964f135f276412b3182a3b2407b8dd45000000) ×2; [0x0bc3…4173](https://etherscan.io/address/0x0bc305e7e13113caed3f5486849e9518a1cc4173) ×2; [0x8199…27d7](https://etherscan.io/address/0x81994b9607e06ab3d5cf3afff9a67374f05f27d7) ×1; [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) ×1. Pools per transaction: 0: 16. Sandwiched: 0.

Largest examples: [0x5d48…867a](https://etherscan.io/tx/0x5d482c0bfaf955dab09787b8cc25b6f05003055ff006aa401ae9586cd0f5867a) $992,846 USDC at 0x7140…28c4; [0xe006…f847](https://etherscan.io/tx/0xe00625fa39afa975bed9ec7e18a792802c7af7b3724dee1cd138c378bde3f847) $960,489 USDC at 0x7140…28c4; [0x6e12…db84](https://etherscan.io/tx/0x6e12cdfa0ea3ae134c6d107775a409cda448ac3bb71b0b4c132fdd7d60f1db84) $396,218 ETH at 0xfe0e…fe17; [0x7ff6…196a](https://etherscan.io/tx/0x7ff6eb7cdf9ea6d4c83f29f7517c9215e411d4b1275518516f8a2f4e3882196a) $197,495 ETH at 0xfe0e…fe17; [0x3a72…8083](https://etherscan.io/tx/0x3a72ce2187371f9722347fba1a96f1d40dc364738d8abd63825dcd5f53d78083) $196,694 WBTC at 0xccf4…dd6a; [0x8bab…cf46](https://etherscan.io/tx/0x8bab5c6cc3387399b5c5b214fcf3d7eb6a62b1e5eb38fa0a74858d0a1f4bcf46) $44,994 USDC at 0xbefc…afa1.

LLM note on this type: Audit: the hash-sampled occurrence (0x248d3c15…) was a deposit of WETH into 0xbad1b632… that minted an unpriced receipt token, not a trade. Round 4 excludes unpriced legs minted from or burned to the zero address and adds receipt_token_minted_deposit and receipt_token_burned_withdrawal ahead of this type; the type fell from 219 to 16 occurrences.

#### two-party exchange through a settlement contract without a swap event (668 transactions, $58,507,936)

What happens: One party pays asset X and receives asset Y while a counterparty does the reverse, both through a contract that records the order (RFQ fill, OTC settlement, limit-order match). No pool is involved, so no registered swap event fires; the ETH side may be delivered by unwrapping, which is invisible in receipts.

Rule: no swap event, no flash loan, some address other than the destination nets negative in one priced asset and positive in another, two or more priced assets. Method: `swap`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $30,743, p90 $139,875, max $9,998,593. Gross priced volume $234,537,295. 197 distinct senders, 178 principals, 55 destinations. By asset of the largest position: USDC ×181 ($32,731,297), IMPL:0xe343…491d ×87 ($8,126,063), ETH ×37 ($4,390,548), USDT ×74 ($3,897,739), WETH ×69 ($3,824,377). Hourly counts from the window start: 29 23 30 22 16 23 20 15 23 42 44 14 13 15 13 14 8 18 97 119 10 16 14 30.

Pairs (sold -> bought): USDC -> IMPL:0xe343…491d ×110 $14,273,197; USDC -> USDtb ×3 $14,198,002; IMPL:0xe343…491d -> USDC ×61 $5,762,870; ? -> ? ×198 $5,252,784; ETH -> USDC ×15 $3,458,660; USDT -> USDC ×39 $2,436,484; USDC -> ? ×22 $1,974,456; USDC -> USDT ×22 $1,760,192. Size median $30,313, p90 $138,958. Destinations: [0x7777…df17](https://etherscan.io/address/0x7777857616fb37f0cfa262e9bb945e828312df17) ×129; [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) ×88; [0x0000…2734](https://etherscan.io/address/0x0000000000001ff3684f28c67538d4d072c22734) ×58; [0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272) ×51; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×47; [0x03f3…9659](https://etherscan.io/address/0x03f34be1bf910116595db1b11e9d1b2ca5d59659) ×38. Pools per transaction: 0: 668. Sandwiched: 0.

Largest examples: [0x3e25…9a2c](https://etherscan.io/tx/0x3e25820bb33cbf543188a7291349c531f5d094c83b09b53b312aca6cf9519a2c) $9,998,593 USDC at 0xb32d…f0fb; [0x8528…5b97](https://etherscan.io/tx/0x85284a221482646a472203e71311760254d2ec5fa2d8805efaaf167c4ecd5b97) $3,999,437 USDC at 0xb32d…f0fb; [0xfd30…ade1](https://etherscan.io/tx/0xfd30f347409bed8d5caa29fc91f031d8c1954b0dc42e0d2d630666a6b7f3ade1) $1,006,874 ETH at 0xf70d…dbef; [0x31fd…0a00](https://etherscan.io/tx/0x31fde1f3bd5eaded5d467c6cfce8c310dddbc7ad1074acf0d47adf5f48c80a00) $995,704 USDC at 0x82f6…66b7; [0x7491…bacc](https://etherscan.io/tx/0x7491fdaa94017df3566c6f3baf6d0bc9f395cdc1cb13356abae2158168dfbacc) $788,596 ETH at 0xf70d…dbef; [0xf115…8c5f](https://etherscan.io/tx/0xf1150cc1182e2445e8d3bfc43da13cde9aca76e65d7753fcccc26a4e2b7d8c5f) $750,027 USDC at 0x5019…9966.

LLM note on this type: Audit: the hash-sampled occurrence (0x9ca780f5…) was an aggregator swap through 0x6131b5fa… that records a Swapped event; the two-sided party was an intermediate contract. Round 4 adds dex_swap_aggregator_event ahead of it (118 transactions); the type fell from 802 to 668 occurrences.

### stablecoin

#### par conversion through a peg-stability module (1,383 transactions, $961,233,749)

What happens: A user exchanges one dollar stablecoin for another at exactly 1:1 through a protocol reserve (Sky PSM: USDS or DAI against USDC), typically burning one and drawing the other from a pocket; fee zero or a few basis points.

Rule: BuyGem/SellGem event, or DSNote events with USDC and DAI/USDS legs and a mint or burn. Method: `psm`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #6.

Largest position change: median $99,967, p90 $671,573, max $245,506,505. Gross priced volume $7,906,398,433. 571 distinct senders, 448 principals, 180 destinations. By asset of the largest position: sUSDS ×22 ($496,867,341), USDS ×570 ($213,055,533), USDC ×367 ($145,720,266), USDT ×165 ($48,303,482), USDe ×53 ($14,708,413). Hourly counts from the window start: 44 72 60 84 80 74 107 82 44 39 60 62 37 53 49 24 49 64 71 51 43 39 32 63.

Directions: USDC -> sUSDS ×4 $246,509,790; sUSDS -> USDC ×3 $245,617,034; ? -> ? ×501 $165,036,164; USDC -> USDS ×35 $83,721,320; USDS -> USDC ×43 $42,619,653; PYUSD -> USDC ×27 $18,068,640; ETH -> ? ×55 $17,254,664; USDT -> USDC ×83 $15,186,452; USDC -> USDT ×59 $14,935,793; ? -> USDT ×29 $12,253,958; USDC -> PYUSD ×30 $11,408,864; USDC -> ? ×49 $9,002,799; WETH -> ? ×9 $8,853,521; IMPL:0xe343…491d -> PYUSD ×17 $8,543,199; USDe -> USDC ×14 $8,434,622; USDT -> ? ×44 $5,876,970; ? -> USDC ×63 $5,597,198; USDT -> RLUSD ×9 $4,341,439; RLUSD -> USDT ×14 $3,762,954; ETH -> USDC ×21 $3,564,464; DAI -> ? ×30 $3,028,323; PYUSD -> USDe ×15 $3,005,208; IMPL:0xe343…491d -> USDT ×11 $2,390,342; ETH -> USDT ×16 $2,127,596; sUSDe -> USDe ×3 $2,099,588; ? -> USDS ×1 $1,547,838; USDT -> USDe ×12 $1,446,107; USDC -> USDe ×5 $1,288,995; USDC -> DAI ×21 $1,254,475; USDT -> IMPL:0xe343…491d ×14 $1,033,904; RLUSD -> USDC ×7 $1,031,779; USDC -> RLUSD ×7 $944,751; DAI -> USDT ×8 $867,082; USDT -> DAI ×7 $859,305; USDe -> sUSDe ×9 $648,672; USDC -> sUSDe ×6 $595,986; USDT -> IMPL:0x0000…012a ×7 $550,025; USDT -> sUSDe ×2 $530,580; PYUSD -> ? ×4 $503,398; sUSDe -> USDC ×3 $462,294; sUSDS -> IMPL:0xe343…491d ×1 $425,524; USDe -> USDT ×1 $251,350; PYUSD -> USDT ×5 $238,650; PYUSD -> sUSDe ×3 $228,638; USDe -> USDT+sDAI ×1 $220,152; RLUSD -> USDC+USDT ×1 $201,374; IMPL:0x6874…2f38 -> USDC ×1 $200,567; ? -> PYUSD ×4 $190,042; DAI -> USDC ×8 $182,997; USDT -> PYUSD ×2 $170,928; RLUSD -> USDe ×1 $160,008; ? -> sUSDe ×1 $150,871; ETH -> DAI ×8 $150,121; crvUSD -> ? ×3 $150,019; ETH+IMPL:0x6982…1933 -> ? ×1 $147,270; crvUSD -> USDC ×1 $100,195; USDT -> frxUSD ×2 $99,954; USDC -> RLUSD+WETH ×1 $99,904; PYUSD -> IMPL:0xe343…491d ×2 $98,218; ETH+USDT -> ? ×3 $77,170; ? -> USDC+USDT ×2 $71,087; USDS -> USDT ×1 $70,000; WBTC -> USDC ×1 $50,457; ? -> USDC+USDT+sDAI ×1 $48,777; ETH -> USDS ×1 $44,194; WETH -> DAI ×1 $41,603; IMPL:0xa1fa…33f8 -> USDC ×2 $40,322; USDC -> IMPL:0xa1fa…33f8 ×2 $40,000; USDC -> WETH ×1 $35,002; WETH -> USDC+USDS+USDT ×1 $34,249; WETH -> USDC ×1 $31,879; IMPL:0x5086…0c72 -> USDC ×1 $27,872; ? -> WETH ×1 $26,980; IMPL:0x4580…af78 -> DAI ×1 $26,601; LINK -> USDC ×1 $25,122; IMPL:0x8653…9ce4 -> IMPL:0x0857…d8f6 ×1 $24,938; USDT -> IMPL:0x85f1…f6a4 ×1 $24,625; USDT -> LINK ×1 $20,235; WETH -> USDT ×1 $19,935; sDAI -> ? ×1 $19,596; USDC -> WBTC ×1 $19,185; frxUSD -> USDT ×1 $16,000; UNI -> USDC ×1 $15,662; USDS -> WETH ×1 $15,000; ? -> DAI ×1 $13,523; AAVE -> IMPL:0x232c…4ee2 ×1 $12,955; ? -> IMPL:0x6440…b01d+USDC+USDS ×1 $11,946; IMPL:0xe343…491d -> ? ×1 $10,456; USDS -> ? ×1 $10,317; USDC -> IMPL:0x594d…5bfa ×1 $10,081; USDS -> WBTC ×1 $10,000; ? -> wstETH ×1 $7,734; ? -> WBTC ×1 $7,718.

Top destinations: [0x8a25…39ab](https://etherscan.io/address/0x8a25a24ede9482c4fc0738f99611be58f1c839ab) ×134; [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×105; [0xcb01…3d45](https://etherscan.io/address/0xcb0151ac9479a6a0261622baa63ae843c9793d45) ×95; [0x4c82…2cca](https://etherscan.io/address/0x4c82d1fbfe28c977cbb58d8c7ff8fcf9f70a2cca) ×93; [0x0000…2734](https://etherscan.io/address/0x0000000000001ff3684f28c67538d4d072c22734) ×81.

Largest examples: [0xd2bf…3ec6](https://etherscan.io/tx/0xd2bf4e2edbb298cbb070f44cbbf5c6ce578b87f933372932b93882a30ce13ec6) $245,506,505 sUSDS at 0x688c…5cbf; [0x8973…0e7f](https://etherscan.io/tx/0x8973f5d326636075ba4d921632fc5b4435ac3f8fb29a075fa039efd7f2a90e7f) $245,505,818 sUSDS at 0x688c…5cbf; [0x0ce6…4be4](https://etherscan.io/tx/0x0ce6843c42b48bb0589ad6a26afa8d9eee4772b76b7e6b6dbb5146867abd4be4) $25,002,417 USDC at 0x3730…7341; [0x796b…c357](https://etherscan.io/tx/0x796b6e46013cb7bd8c480b82e7df3d5c45894a21a79707c53dc44fdc0142c357) $15,000,000 USDS at 0xf506…6ec6; [0xb328…4546](https://etherscan.io/tx/0xb328fe72c76d8c6c0974df48727600c039d0485df2b46531b9b0f119c6f54546) $10,000,000 USDS at 0xb99a…bcf5; [0x7bbf…887e](https://etherscan.io/tx/0x7bbfa2d8747980b74389ea4db74e58d3b4af878dd311eef63029001407ec887e) $10,000,000 USDS at 0xf506…6ec6.

#### stablecoin issuance (280 transactions, $1,049,940,957)

What happens: The issuer creates new supply: tokens appear from the zero address, usually into the issuer's treasury, and reach the market in later transactions. This records token supply mechanics. Conversion, vault and credit operations can also mint or burn tokens; external fiat issuance or redemption is not established.

Rule: a registry stablecoin transferred from the zero address for at least the threshold, no swap, no flash loan. Method: `mint_burn`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) (USDS mint inside the PSM path).

Largest position change: median $250,703, p90 $2,999,578, max $254,923,991. Gross priced volume $1,256,191,629. 41 distinct senders, 49 principals, 18 destinations. By asset of the largest position: USDC ×173 ($542,125,986), DAI ×5 ($350,503,395), USDS ×27 ($58,796,049), USDT ×4 ($51,913,705), USDe ×59 ($24,948,468). Hourly counts from the window start: 18 14 18 15 12 12 19 14 7 14 13 8 12 12 5 2 10 6 8 19 4 9 5 24.

By token: USDC minted $542,068,832, burned $0.00, net $542,068,832 in 173 txs; DAI minted $350,559,420, burned $97,643, net $350,461,777 in 11 txs; USDS minted $59,772,002, burned $56,043, net $59,715,959 in 28 txs; USDe minted $25,924,714, burned $0.00, net $25,924,714 in 62 txs; RLUSD minted $21,500,000, burned $0.00, net $21,500,000 in 3 txs; sUSDS minted $4,646,441, burned $0.00, net $4,646,441 in 11 txs; frxUSD minted $140,798, burned $0.00, net $140,798 in 8 txs; USD1 minted $12,555, burned $0.00, net $12,555 in 1 txs.

Top destinations: [0x2222…c205](https://etherscan.io/address/0x2222222d7164433c4c09b0b0d809a9b52c04c205) ×86; [0xe349…62d3](https://etherscan.io/address/0xe3490297a08d6fc8da46edb7b6142e4f461b62d3) ×62; [0xec2c…a7c7](https://etherscan.io/address/0xec2c96e75b09e29b66bf2ee5c37fa749ef9aa7c7) ×42; [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×35; [0x8a25…39ab](https://etherscan.io/address/0x8a25a24ede9482c4fc0738f99611be58f1c839ab) ×21.

Largest examples: [0x2340…fdc0](https://etherscan.io/tx/0x2340f232f6b6cd68f88bb5cde0022273929c1fe906f0bbce65528d6e2e94fdc0) $254,923,991 DAI at 0xf6e7…3042; [0x0234…d91b](https://etherscan.io/tx/0x023487c4d6087c82711717d836838af392e3bc79005a948af32d22b549eed91b) $98,986,071 USDC at 0x55fe…44b8; [0xda6a…9b50](https://etherscan.io/tx/0xda6a8bb489552459e778fb5f3ec3df8dcdf0ede809520521778bb4f409989b50) $61,991,277 USDC at 0x55fe…44b8; [0x4805…4d21](https://etherscan.io/tx/0x4805950eedf3c5be467af8663f0a3e0e92df5a5dfd8fe176379a4f3604954d21) $50,937,413 USDT at 0xe7df…c92f; [0x95d9…627d](https://etherscan.io/tx/0x95d91a3033175c31a6d40545c928ecb33f6627621b2563f07c07783cf487627d) $49,992,965 USDC at 0x55fe…44b8; [0xdb34…56a3](https://etherscan.io/tx/0xdb34795fa29a133ca6b09e58dc1f61d76a667eb07f52b741fc24bc42613356a3) $49,992,965 USDC at 0x55fe…44b8.

#### stablecoin redemption (204 transactions, $790,827,207)

What happens: Supply is destroyed: tokens go to the zero address, the issuer having received them from a redeeming customer earlier. This records token supply mechanics. Conversion, vault and credit operations can also mint or burn tokens; external fiat issuance or redemption is not established.

Rule: a registry stablecoin transferred to the zero address for at least the threshold, no swap, no flash loan. Method: `mint_burn`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $340,107, p90 $7,620,253, max $236,481,143. Gross priced volume $1,080,213,261. 22 distinct senders, 19 principals, 13 destinations. By asset of the largest position: USDC ×155 ($408,919,226), DAI ×2 ($257,447,517), USDS ×21 ($94,626,034), PYUSD ×2 ($11,498,032), USDe ×6 ($9,857,876). Hourly counts from the window start: 26 25 16 22 18 11 11 5 6 4 9 5 7 4 2 2 3 2 4 5 4 4 3 6.

By token: USDC minted $0.00, burned $408,919,140, net -$408,919,140 in 155 txs; DAI minted $39,987, burned $257,447,517, net -$257,407,530 in 6 txs; USDS minted $9,025, burned $95,375,532, net -$95,366,507 in 26 txs; PYUSD minted $0.00, burned $11,498,032, net -$11,498,032 in 2 txs; USDe minted $0.00, burned $9,857,876, net -$9,857,876 in 6 txs; RLUSD minted $0.00, burned $7,510,000, net -$7,510,000 in 2 txs; sUSDS minted $0.00, burned $749,536, net -$749,536 in 5 txs; frxUSD minted $0.00, burned $149,531, net -$149,531 in 10 txs; LUSD minted $0.00, burned $69,409, net -$69,409 in 1 txs.

Top destinations: [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×123; [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) ×32; [0x8a25…39ab](https://etherscan.io/address/0x8a25a24ede9482c4fc0738f99611be58f1c839ab) ×22; [0xe349…62d3](https://etherscan.io/address/0xe3490297a08d6fc8da46edb7b6142e4f461b62d3) ×6; [0x9a87…a0b0](https://etherscan.io/address/0x9a873656c19efecbfb4f9fab5b7acdeab466a0b0) ×4.

Largest examples: [0xf424…4856](https://etherscan.io/tx/0xf4244137db07ad46b9b2f99a81486571ca5c5aab0e754b37ed7dc8f86a994856) $236,481,143 DAI at 0xf6e7…3042; [0x833c…4061](https://etherscan.io/tx/0x833ca8114c60a8f3d4386cd327ce43ba8c9e7a455bbd42e2baea4802ee3e4061) $49,994,472 USDC at 0x55fe…44b8; [0xd7a7…0fa1](https://etherscan.io/tx/0xd7a7aed710308279a5da4e60f1c1a4636dbef6ef6d25906ae8ea787f94fe0fa1) $39,086,065 USDC at 0x55fe…44b8; [0x390e…5b19](https://etherscan.io/tx/0x390ec16ad6e45e96a9a2fca5493c13a41e6eb9057b7f5cf8f4e7a1f315395b19) $30,583,686 USDC at 0x55fe…44b8; [0xb684…f813](https://etherscan.io/tx/0xb684cf55680709759554b2c4a9039524b172d4250cdf9b0f3e6ddec3f7b1f813) $25,138,666 USDC at 0x55fe…44b8; [0x62c3…e35e](https://etherscan.io/tx/0x62c34dbe318b0a9a05d59a71998d510db24022db8406ff381473ebc04094e35e) $23,996,623 USDC at 0x55fe…44b8.

#### wrapped BTC issuance or redemption (18 transactions, $105,233,336)

What happens: A custodian or bridge mints or burns a BTC-backed token (WBTC, cbBTC, tBTC, LBTC) against bitcoin moved off-chain.

Rule: a BTC wrapper minted from or burned to the zero address for at least the threshold, no swap. Method: `mint_burn`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $4,885,430, p90 $15,817,175, max $15,938,830. Gross priced volume $105,305,522. 9 distinct senders, 10 principals, 7 destinations. By asset of the largest position: cbBTC ×9 ($100,486,519), tBTC ×5 ($3,381,278), LBTC ×4 ($1,365,539). Hourly counts from the window start: 0 0 2 2 4 5 1 1 0 0 1 1 0 0 1 0 0 0 0 0 0 0 0 0.

By token: cbBTC minted $100,486,519, burned $0.00, net $100,486,519 in 9 txs; tBTC minted $397,414, burned $3,040,086, net -$2,642,672 in 5 txs; LBTC minted $158,650, burned $1,206,905, net -$1,048,254 in 4 txs.

Top destinations: [0x0000…31e7](https://etherscan.io/address/0x000000000cbdc84a73055389d392710263bb31e7) ×9; [0x8236…4494](https://etherscan.io/address/0x8236a87084f8b84306f72007f36f2618a5634494) ×2; [0x1808…3a88](https://etherscan.io/address/0x18084fba666a33d37592fa2633fd49a74dd93a88) ×2; [0x535e…140f](https://etherscan.io/address/0x535e01f948458e0b64f9db2a01da6f32e240140f) ×2; [0x8328…f54a](https://etherscan.io/address/0x8328446602cb4c3b2b4a25beca6488e947b6f54a) ×1.

Largest examples: [0x6d89…cd20](https://etherscan.io/tx/0x6d89f674d426d3bbf0c4021ee1d6be38aba53b636a1ea06f2f4a91e43131cd20) $15,938,830 cbBTC at 0xa9d1…3e43; [0x446a…e239](https://etherscan.io/tx/0x446af23a57213e0d2c6b2ba8561c183a1a7f07a071c57644e7e2467ae881e239) $15,817,175 cbBTC at 0xa9d1…3e43; [0x0c1b…61fe](https://etherscan.io/tx/0x0c1b9f62c3994cd8339495c39b39244b02c07b2cc90257417c81f2311afa61fe) $15,145,593 cbBTC at 0xa9d1…3e43; [0x2220…eec6](https://etherscan.io/tx/0x2220df2fc12a030d4c46713d46337d4dc7dcad0b8cf01bd07c119493bc03eec6) $14,427,455 cbBTC at 0xa9d1…3e43; [0xd6c3…fd12](https://etherscan.io/tx/0xd6c3a0c7a14f838ddbf7a36e29357f98a022d9f1c0ea37c40efd453484aafd12) $13,149,973 cbBTC at 0xa9d1…3e43; [0x1717…375f](https://etherscan.io/tx/0x1717c4a6906d80ff2909cd0e281c6f308e1074585228f57bcff5175439f7375f) $8,381,931 cbBTC at 0xa9d1…3e43.

#### issuance or redemption of a token priced from its own swaps (139 transactions, $73,222,882)

What happens: Supply of a token outside the registry is created or destroyed for at least the threshold, valued at its in-sample price; the window's cases are dollar-pegged tokens minted or burned by their issuer contracts.

Rule: an implied-priced token minted from or burned to the zero address for at least the threshold, no swap. Method: `mint_burn`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $62,596, p90 $1,741,876, max $5,248,718. Gross priced volume $92,051,144. 44 distinct senders, 37 principals, 22 destinations. By asset of the largest position: IMPL:0xe343…491d ×7 ($30,696,294), IMPL:0x22ae…d4c7 ×32 ($17,920,294), IMPL:0x1aba…c33c ×14 ($7,004,108), IMPL:0x5086…0c72 ×8 ($4,715,630), IMPL:0x73e0…db98 ×2 ($3,189,539). Hourly counts from the window start: 8 6 11 9 16 21 10 5 1 0 3 1 3 5 2 0 1 2 5 3 2 4 11 10.

By token: IMPL:0xe343…491d minted $21,146,900, burned $9,549,394, net $11,597,506 in 7 txs; IMPL:0x22ae…d4c7 minted $17,920,294, burned $0.00, net $17,920,294 in 32 txs; IMPL:0x1aba…c33c minted $3,369,309, burned $3,634,799, net -$265,490 in 14 txs; IMPL:0x5086…0c72 minted $5,351,922, burned $0.00, net $5,351,922 in 17 txs; IMPL:0x73e0…db98 minted $3,189,539, burned $0.00, net $3,189,539 in 2 txs; IMPL:0x2323…aa71 minted $1,952,326, burned $801,591, net $1,150,735 in 8 txs; IMPL:0x437c…b291 minted $1,550,619, burned $0.00, net $1,550,619 in 2 txs; IMPL:0xaca9…35da minted $560,353, burned $987,120, net -$426,768 in 6 txs; IMPL:0x01a8…50ad minted $1,165,263, burned $0.00, net $1,165,263 in 36 txs; IMPL:0xd166…2df7 minted $0.00, burned $1,049,829, net -$1,049,829 in 1 txs; IMPL:0x5e84…aa1f minted $0.00, burned $366,291, net -$366,291 in 1 txs; IMPL:0x77e0…0a44 minted $18,815, burned $228,670, net -$209,855 in 2 txs; IMPL:0x6435…5160 minted $0.00, burned $161,789, net -$161,789 in 3 txs; IMPL:0x4206…668f minted $0.00, burned $62,565, net -$62,565 in 3 txs; IMPL:0x6440…b01d minted $49,918, burned $0.00, net $49,918 in 2 txs; IMPL:0x2b59…eb39 minted $0.00, burned $31,882, net -$31,882 in 1 txs; IMPL:0xab5e…befa minted $0.00, burned $31,821, net -$31,821 in 1 txs; IMPL:0x85f1…f6a4 minted $0.00, burned $29,329, net -$29,329 in 1 txs.

Top destinations: [0x5523…227e](https://etherscan.io/address/0x5523985926aa12ba58dc5ad00ddca99678d7227e) ×36; [0x26d3…73c5](https://etherscan.io/address/0x26d3681dfc9e4c8c79cfbf461adec8a21d5d73c5) ×32; [0x4691…3093](https://etherscan.io/address/0x4691c475be804fa85f91c2d6d0adf03114de3093) ×17; [0x1aba…c33c](https://etherscan.io/address/0x1abaea1f7c830bd89acc67ec4af516284b1bc33c) ×14; [0x0bc3…4173](https://etherscan.io/address/0x0bc305e7e13113caed3f5486849e9518a1cc4173) ×8.

Largest examples: [0x5f3a…0477](https://etherscan.io/tx/0x5f3a9ff3fea516180f5f02903fe3ef4b30e471ca12ad55041dff107fc3170477) $5,248,718 IMPL:0xe343…491d at 0xf845…abb7; [0x3f2b…f14c](https://etherscan.io/tx/0x3f2b543e87cb92808f7cf867924ea2a1832c019467a5ac6bd2f94e919fd6f14c) $5,230,556 IMPL:0xe343…491d at 0x264b…97b5; [0xd934…abc8](https://etherscan.io/tx/0xd9348131c3400d49e216c72564bc7021a9a711c4a3946f0f9db848c1150babc8) $5,102,268 IMPL:0x22ae…d4c7 at 0x7a9e…cb98; [0x4224…9fc6](https://etherscan.io/tx/0x4224c5ad67d967526bc1f6be4b3754782cbaa546fbfafd94022b4ea0eb769fc6) $5,000,979 IMPL:0x22ae…d4c7 at 0x7a9e…cb98; [0xa815…2649](https://etherscan.io/tx/0xa8151f32c3c3c9e0f19da054ec66e61de22daa9b653611ca8989ac1ddeb02649) $4,854,396 IMPL:0xe343…491d at 0x264b…97b5; [0xef3d…4e9f](https://etherscan.io/tx/0xef3dcf49afffc215ff3f29afd592cdce41699c53e77d92433dfe6a5ed1d24e9f) $4,560,926 IMPL:0xe343…491d at 0x264b…97b5.

LLM note on this type: resolve named the tokens: 0x1abaea1f… is EURC (Euro Coin, 6 decimals; $3.4M minted and $3.6M burned in the day) and 0x73e0c0d4… is kBTC (Kraken Wrapped Bitcoin, 8 decimals; $3.2M minted in two transactions). Issuance of unregistered tokens is visible only because their pools gave an implied price; EURC needs a EUR feed to be valued properly.

### mev

#### sandwich-pattern candidate (136 transactions, $7,691,373)

What happens: The same sending address trades opposite directions around another sender in one pool and block. This is a sandwich candidate; coordinated ownership, profit and the counterfactual execution price remain unproved.

Rule: same block, same pool: actor swaps direction d at index i, a stranger swaps d at index k, the actor swaps -d at index j > k (scan marks front/back). Method: `sandwich`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $48,036, p90 $118,421, max $220,017. Gross priced volume $16,960,592. 12 distinct senders, 13 principals, 10 destinations. By asset of the largest position: WETH ×98 ($5,486,881), USDT ×18 ($1,103,950), USDC ×18 ($1,047,167), WBTC ×2 ($53,375). Hourly counts from the window start: 8 16 38 2 8 10 0 4 0 0 4 4 2 6 2 2 12 2 6 4 0 2 4 0.

Bracketing senders: [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13) 47 legs, 27 intervening swaps, observed principal net $321.97; [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) 32 legs, 16 intervening swaps, observed principal net $462.42; [0x1111…3911](https://etherscan.io/address/0x11111215b72e894c60f24e91ac2c8ccb1d373911) 18 legs, 9 intervening swaps, observed principal net $19.70; [0x595c…3b2c](https://etherscan.io/address/0x595caa1ce7d8cb5df54c017d07d86ed0e24a3b2c) 14 legs, 9 intervening swaps, observed principal net $0.00; [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) 10 legs, 5 intervening swaps, observed principal net $66.42; [0x4cd4…d03e](https://etherscan.io/address/0x4cd4499d6e6a0eb8995a2cabd400d1ad35c4d03e) 4 legs, 2 intervening swaps, observed principal net $9,700; [0xc54b…1097](https://etherscan.io/address/0xc54b77b28ee4d18cd3d93991f08b79bc85c71097) 2 legs, 1 intervening swaps, observed principal net $1.48; [0x0b75…1672](https://etherscan.io/address/0x0b75abafb0ba585666d034dfd2d9d59136c31672) 2 legs, 1 intervening swaps, observed principal net $0.40. Pools: [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) ×45; [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) ×40; [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) / pool 0x2287…1bba ×22; [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) / pool 0x00b9…22d7 ×10; [0xe6ff…e718](https://etherscan.io/address/0xe6ff8b9a37b0fab776134636d9981aa778c4e718) ×10; [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) / pool 0xdb4c…43b1 ×4.

Top destinations: [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×47; [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ×32; [0x6720…31d2](https://etherscan.io/address/0x672061b75f770331b0c7c2a566a9ac0a9ba331d2) ×18; [0x6338…41a7](https://etherscan.io/address/0x6338afee3ff32599bff2ce3d8b7604bd6d6a41a7) ×14; [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e) ×10.

Largest examples: [0xc006…6830](https://etherscan.io/tx/0xc0061a84f8bd6067621b2d1f213bc4b4c8a1b44093757b01fb73d69616d56830) $220,017 USDT at 0x1f2f…f387; [0xc042…fdfd](https://etherscan.io/tx/0xc042b42dae4028e1321296626f0400d0713d3148fa0c9a43174743a5089bfdfd) $211,313 WETH at 0xc7bb…0e9b; [0x9067…2633](https://etherscan.io/tx/0x90675f8cbf6a2fed6964a380377e58fd8242e9abe630ad7cf689e64317fe2633) $210,875 WETH at 0xc7bb…0e9b; [0xdeef…dc75](https://etherscan.io/tx/0xdeef1b453773f8b1a530ec353be91d733b34d8f90d95f72453758399049adc75) $209,001 WETH at 0xe055…939f; [0x900c…affa](https://etherscan.io/tx/0x900cff2ab2f2c4a118e99ec7cdafcc913e8e98ad30f180a799747cbbf01aaffa) $208,972 WETH at 0xe055…939f; [0x11f9…cedc](https://etherscan.io/tx/0x11f9bb5e1a03ff45cf7b37fb59195e7ac2ab81c6efe8e47e81ca63b064b9cedc) $207,485 WETH at 0xe055…939f.

#### swap inside sandwich-pattern candidate (42 transactions, $4,798,890)

What happens: A swap lies inside the detected same-sender round trip. Price harm requires replay against the state without the surrounding trades.

Rule: swap in a pool between the front and back legs of a sandwich (scan marks victim). Method: `swap`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $24,949, p90 $299,192, max $1,000,044. Gross priced volume $30,122,442. 29 distinct senders, 29 principals, 15 destinations. By asset of the largest position: USDT ×6 ($2,101,601), sUSDe ×8 ($1,505,435), USDe ×1 ($299,998), ETH ×10 ($271,884), USDC ×8 ($249,683). Hourly counts from the window start: 4 2 5 0 4 2 1 2 1 1 2 0 3 6 1 0 3 0 1 1 0 1 0 2.

Pairs (sold -> bought): USDT -> RLUSD ×2 $1,791,914; sUSDe -> USDe ×8 $1,505,435; USDC -> USDe ×1 $299,998; USDT -> USDe ×1 $239,737; USDC -> IMPL:0x5086…0c72 ×1 $200,028; ETH -> USDT ×6 $194,589; USDC -> USDT ×1 $130,082; ETH -> USDC ×5 $105,281. Size median $24,949, p90 $299,192. Destinations: [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×13; [0x4c82…2cca](https://etherscan.io/address/0x4c82d1fbfe28c977cbb58d8c7ff8fcf9f70a2cca) ×9; [0x68b3…fc45](https://etherscan.io/address/0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45) ×4; [0x66a9…a8af](https://etherscan.io/address/0x66a9893cc07d91d95644aedd05d03f95e1dba8af) ×3; [0x0000…2734](https://etherscan.io/address/0x0000000000001ff3684f28c67538d4d072c22734) ×3; [0x288f…c6ab](https://etherscan.io/address/0x288fbaef5547d9599f1ee9d000451cbd0458c6ab) ×1. Pools per transaction: 1: 2, 2: 5, 3: 5, 4: 6, 5: 9, 6: 15. Sandwiched: 42.

Largest examples: [0x28f9…9e96](https://etherscan.io/tx/0x28f9fa743786237d9c96060934f1632edd4c591b87633b7da888dcaa6a999e96) $1,000,044 USDT at 0xcf0a…cd69; [0xc451…1a6d](https://etherscan.io/tx/0xc451ed03b5f29e47a85b7b259389b7ecf14f4ca5bb5e90dc0f712f7636b71a6d) $791,870 USDT at 0xcf0a…cd69; [0x932a…31a0](https://etherscan.io/tx/0x932affc8538db0b888e52cdad8c2b7cc651b5bb035a7f19df6e375d7e34231a0) $324,055 sUSDe at 0x5e20…3131; [0x577f…e224](https://etherscan.io/tx/0x577ff27a97cf93d54c732214debce5b327095cec05964fff651231286880e224) $299,998 USDe at 0xcb92…f941; [0xc574…28e5](https://etherscan.io/tx/0xc57428bcf6d468aa84866981a6a31cbdc553b9917eff5ff40c922274e00528e5) $299,192 sUSDe at 0x5e20…3131; [0x2f11…af10](https://etherscan.io/tx/0x2f11b087bf64dc9f60deee32c8b42179b6dc9044e9ac91ff432d18a46e4baf10) $274,260 sUSDe at 0x5e20…3131.

#### flash-loan-funded swap strategy (1,386 transactions, $20,294,068)

What happens: An event-emitting lender sends tokens and receives at least the same amount back, while swaps occur. This establishes temporary funding plus trading; leverage adjustment or liquidation can have the same shape, so arbitrage profit is not assumed.

Rule: a flash-loan pair (same asset lent and repaid between the same two parties inside the transaction) and at least one swap event; lender must also emit a flash-loan event. Method: `flash_loan`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #3, #8.

Largest position change: median $49.28, p90 $48,998, max $298,635. Gross priced volume $85,309,012,614. 260 distinct senders, 217 principals, 90 destinations. By asset of the largest position: USDT ×223 ($8,571,109), USDC ×286 ($6,226,824), WETH ×412 ($1,267,200), USDe ×20 ($997,871), sUSDe ×28 ($864,430). Hourly counts from the window start: 51 62 95 33 59 54 38 40 29 15 35 37 42 119 37 38 24 34 70 249 128 34 24 39.

Lenders: [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) 1301 loans, $22,073,531,923; [0x26de…9ee1](https://etherscan.io/address/0x26de7861e213a5351f6ed767d00e0839930e9ee1) 66 loans, $1,860,200,004; [0xa428…fb6a](https://etherscan.io/address/0xa428723ee8ffd87088c36121d72100b43f11fb6a) 5 loans, $37,140,312; [0xba12…f2c8](https://etherscan.io/address/0xba12222222228d8ba445958a75a0704d566bf2c8) 68 loans, $32,228,927. Loan size median $999,859, max $399,377,555; assets USDC ×372, USDT ×176, WBTC ×36, WETH ×592, cbBTC ×174, crvUSD ×66. Principal net per transaction: median $0.00, p90 $0.00, sum -$55,070. Gross volume without the loan legs $37,302,810,283. Pools per transaction: 1: 561, 2: 271, 3: 302, 4: 98, 5: 66, 6: 40, 7: 13, 8: 9, 9: 8, 10: 10, 11: 5, 12: 1, 19: 1, 20: 1.

Top destinations: [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) ×321; [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ×214; [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) ×203; [0x8554…7c00](https://etherscan.io/address/0x85541934b8a3bfb111e6d2c86ebdaa5882d87c00) ×141; [0xb82a…97d4](https://etherscan.io/address/0xb82aac6aecc9a8edf12345a3b1ec874575da97d4) ×102.

Largest examples: [0x976e…6b7b](https://etherscan.io/tx/0x976e4782739f9cc13f4493fc150e4a14f6a661439d368439c862cefc9ee26b7b) $298,635 USDT at 0x585d…8b4f; [0x0cc1…b5a8](https://etherscan.io/tx/0x0cc174cc961c4c6a63211c9b55f6e97ff9b072223da0f5cb39cf07c616f1b5a8) $296,412 sUSDe at 0x4691…3093; [0xaeed…a987](https://etherscan.io/tx/0xaeed9c4e5d79894ec181f13f4282b6866a2052408027431ea270add981c4a987) $293,512 USDT at 0xe873…d710; [0x95b4…b5c4](https://etherscan.io/tx/0x95b4b74fb4131846ea65aa0024a875df01dc1c8c309afd0e86eba641d459b5c4) $290,480 USDC at 0xe873…d710; [0xda12…d78e](https://etherscan.io/tx/0xda126fe9b3231f1960369169d7e0f64d38603bac3955dec5f882f2133ed6d78e) $249,204 USDe at 0x4691…3093; [0xd4db…4cc4](https://etherscan.io/tx/0xd4db13fa50c345607cbd36af5cc3be508cfb702a6ba27ee612bc55b62e164cc4) $201,585 USDC at 0xe873…d710.

#### flash loan without a swap (743 transactions, $4,633,471)

What happens: A flash loan used for something other than a pool trade: a collateral swap, a self-liquidation, a debt refinance, or a balance check.

Rule: a flash-loan pair and no swap event. Method: `flash_loan`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $1.88, p90 $22,542, max $203,191. Gross priced volume $62,473,431,054. 60 distinct senders, 23 principals, 21 destinations. By asset of the largest position: USDT ×64 ($2,965,098), USDC ×63 ($1,079,850), WETH ×72 ($348,280), crvUSD ×7 ($134,491), USDe ×1 ($83,897). Hourly counts from the window start: 6 8 15 3 11 9 7 3 7 4 124 56 5 70 82 38 5 6 15 29 166 40 8 26.

Lenders: [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) 301 loans, $22,273,431,758; [0xba12…f2c8](https://etherscan.io/address/0xba12222222228d8ba445958a75a0704d566bf2c8) 519 loans, $19,368,882. Loan size median $35,352, max $439,339,303; assets AAVE ×51, USDC ×362, WBTC ×38, WETH ×135, cbBTC ×6, wstETH ×226. Principal net per transaction: median $1.09, p90 $1.93, sum $1,390. Gross volume without the loan legs $17,887,829,774. Pools per transaction: 0: 743.

Top destinations: [0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272) ×488; [0xcb01…3d45](https://etherscan.io/address/0xcb0151ac9479a6a0261622baa63ae843c9793d45) ×80; [0xb82a…97d4](https://etherscan.io/address/0xb82aac6aecc9a8edf12345a3b1ec874575da97d4) ×48; [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) ×38; [0x147a…1e7f](https://etherscan.io/address/0x147a429fbd403794587ff971207e684f5e141e7f) ×28.

Largest examples: [0x0f04…1dba](https://etherscan.io/tx/0x0f04b2c0836b4cbaa7cc62e69e011e5020863362380630de96fc04febbc11dba) $203,191 USDT at 0x585d…8b4f; [0xa7de…3e73](https://etherscan.io/tx/0xa7ded7e0a0957c83069ca0dead47913ae7e6dd2d77e4155b2e2f57a070b43e73) $196,384 USDT at 0x7718…baf1; [0xdf90…48e1](https://etherscan.io/tx/0xdf90cbfe0f8c00bedf845c0154a6eb949792decf93808051385afd73762a48e1) $164,210 USDT at 0x585d…8b4f; [0xc2a0…7660](https://etherscan.io/tx/0xc2a0cd5ff21c96fa9daf2e6c244fc4731b65366802ad1c247bf9e91619a57660) $138,081 USDT at 0x585d…8b4f; [0xf026…4f0c](https://etherscan.io/tx/0xf026010c340bac00cf3763b759afd1ca628d29046d2635ad23063781b4eb4f0c) $124,808 USDT at 0x7718…baf1; [0xdf8f…56cf](https://etherscan.io/tx/0xdf8f0574d366289776dc877169a9fcc503c5069e17b0d09365548eb77d7a56cf) $114,512 USDT at 0x7718…baf1.

#### positive observed-net multi-pool strategy (118 transactions, $3,784,828)

What happens: The selected principal has a positive observed priced-asset net after multiple pool interactions. This is an arbitrage candidate; missing assets, internal ETH, claims, gas and bribes prevent a profit conclusion.

Rule: two or more swap events across two or more pools, no flash loan, the principal contract nets >= 0 in every priced asset and > 0 in one, the EOA nets nothing. Method: `arbitrage`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $22,689, p90 $49,567, max $316,308. Gross priced volume $21,864,653. 25 distinct senders, 13 principals, 13 destinations. By asset of the largest position: USDC ×38 ($1,440,859), USDT ×14 ($713,320), rETH ×13 ($497,727), WETH ×20 ($470,631), WBTC ×28 ($464,811). Hourly counts from the window start: 14 21 13 6 3 16 5 9 2 3 1 1 0 5 3 0 0 0 8 3 2 0 0 3.

Principal net: median $1.91, p90 $60.22, sum $1,854. Principals: [0x8f40…71a7](https://etherscan.io/address/0x8f40082c34812db98681c63db3bbeb29dbe871a7) ×63 observed net $626.64; [0x2d83…aded](https://etherscan.io/address/0x2d83ff1cb1c79c68fe530d35f439a92a645faded) ×18 observed net $4.41; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×13 observed net $1,153; [0x0000…fad4](https://etherscan.io/address/0x0000000aa232009084bd71a5797d089aa4edfad4) ×6 observed net $18.06; [0x42e2…4748](https://etherscan.io/address/0x42e213a3ad048e899b89ea8cb11d21bc97b84748) ×5 observed net $33.25; [0x5523…227e](https://etherscan.io/address/0x5523985926aa12ba58dc5ad00ddca99678d7227e) ×4 observed net $1.00.

Top destinations: [0x8f40…71a7](https://etherscan.io/address/0x8f40082c34812db98681c63db3bbeb29dbe871a7) ×63; [0x2d83…aded](https://etherscan.io/address/0x2d83ff1cb1c79c68fe530d35f439a92a645faded) ×18; [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387) ×13; [0x0000…fad4](https://etherscan.io/address/0x0000000aa232009084bd71a5797d089aa4edfad4) ×6; [0x42e2…4748](https://etherscan.io/address/0x42e213a3ad048e899b89ea8cb11d21bc97b84748) ×5.

Largest examples: [0x3fa0…ab5c](https://etherscan.io/tx/0x3fa0c0e16207693b423461f9f47c7d294974bd2ded14a3378603a578485bab5c) $316,308 USDC at 0x88e6…5640; [0xc201…df37](https://etherscan.io/tx/0xc201bb6a0b20ecb339a543fb7dad507937b529434525f535a141fa9fe0aedf37) $267,318 USDT at 0x35c9…b636; [0x7de7…0b23](https://etherscan.io/tx/0x7de75618165b39dad13091ddf03721d0080effc8f04eb7ce40f3146aa6df0b23) $124,182 WETH at 0xd315…6293; [0xd6b2…7394](https://etherscan.io/tx/0xd6b2befd71caabcd0115fb2f27bc952c122c8111d9f9eaca1ae39bac8d037394) $99,209 rETH at 0x553e…f823; [0x1493…bfd1](https://etherscan.io/tx/0x149354c697a7b5ab97756c770aff78e327e896f647764a2397bd676e3079bfd1) $79,970 USDC at 0x88e6…5640; [0xb37d…4974](https://etherscan.io/tx/0xb37df0dff6c9e105f63683118a81ab94c759bbae4c6a4571a2c49e98dd964974) $67,998 sUSDe at 0x5c2a…2972.

### staking

#### ETH staked with Lido (27 transactions, $4,029,801)

What happens: ETH is sent to the Lido pool and stETH is minted to the sender; from here the ETH is queued for validators.

Rule: Submitted event. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $31,997, p90 $245,574, max $2,103,999. Gross priced volume $9,097,982. 27 distinct senders, 27 principals, 3 destinations. By asset of the largest position: ETH ×6 ($2,703,417), stETH ×19 ($1,276,557), wstETH ×2 ($49,827). Hourly counts from the window start: 0 3 0 2 0 0 2 0 2 2 0 0 0 0 1 0 1 6 0 2 2 1 1 2.

Top destinations: [0xae7a…fe84](https://etherscan.io/address/0xae7ab96520de3a18e5e111b5eaab095312d7fe84) ×23; [0xa88f…dd0d](https://etherscan.io/address/0xa88f0329c2c4ce51ba3fc619bbf44efe7120dd0d) ×3; [0x1111…2a65](https://etherscan.io/address/0x111111125421ca6dc452d289314280a0f8842a65) ×1.

Largest examples: [0x11da…ffdc](https://etherscan.io/tx/0x11daf0d3f250b3f39960fa3ed8dfa3fa2eaf47818681dba60fa2e964ea11ffdc) $2,103,999 ETH at 0xf2a6…42f0; [0x11da…816a](https://etherscan.io/tx/0x11da2e167fc8c25cfa0faeba6e0109ed2fa4a97ccb57065d32efce05f239816a) $288,812 ETH at 0xae7a…fe84; [0xfdc9…77e5](https://etherscan.io/tx/0xfdc9ff9b71a51526699743ce5b036113dd96d9bc2bd5e76d8e9fcc9d3b9e77e5) $245,574 stETH at 0xb11b…1fc4; [0x7e5d…59ef](https://etherscan.io/tx/0x7e5df76f9e1fa7d0421b4ce465b1d26e436e727a925dc6dbf09e3ad6b24659ef) $245,574 stETH at 0xfafc…0c2a; [0xb267…8141](https://etherscan.io/tx/0xb2679cd2cee8f0ed82a7ab67ec5c16c810bfdf995ea442fd45d90c740c468141) $240,939 ETH at 0xccf3…c7e6; [0xe015…49c6](https://etherscan.io/tx/0xe01524ad8bb8df12a6269b7cc5c150c206137699e5fef971c7610f768fe649c6) $147,344 stETH at 0x5023…48fc.

#### Lido withdrawal request or claim (23 transactions, $13,475,141)

What happens: A stETH holder asks to exit (stETH locked, a request NFT issued) or claims finalized ETH.

Rule: WithdrawalRequested or WithdrawalClaimed event. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $251,216, p90 $1,129,718, max $4,781,654. Gross priced volume $20,828,574. 12 distinct senders, 13 principals, 4 destinations. By asset of the largest position: stETH ×17 ($8,404,806), WETH ×2 ($3,292,268), wstETH ×4 ($1,778,068). Hourly counts from the window start: 1 2 1 0 1 0 0 2 2 0 2 1 0 1 0 2 1 0 1 1 0 0 4 1.

Top destinations: [0x889e…f9b1](https://etherscan.io/address/0x889edc2edab5f40e902b864ad4d7ade8e412f9b1) ×10; [0x85b7…acc6](https://etherscan.io/address/0x85b78aca6deae198fbf201c82daf6ca21942acc6) ×6; [0x6802…657c](https://etherscan.io/address/0x68025a4615407993a680102b08a23a61d11c657c) ×4; [0x1b7a…6fff](https://etherscan.io/address/0x1b7a4c3797236a1c37f8741c0be35c2c72736fff) ×3.

Largest examples: [0x10fd…be8b](https://etherscan.io/tx/0x10fda64f8b4f096d2528084371f9b6b9b254f7ca3c504b074a96bf35fc40be8b) $4,781,654 stETH at 0x889e…f9b1; [0x8e79…88d0](https://etherscan.io/tx/0x8e7951f73bd38f83c9acaba94f96ebe5f5011a34e6b0ba04d3eecbb5bc2b88d0) $3,041,051 WETH at 0x6802…657c; [0x11fa…525f](https://etherscan.io/tx/0x11fa8a6ec0fe72426ee3832721c512472f1cf1cd9301fc2116adb89ccad9525f) $1,129,718 wstETH at 0x90f4…46f7; [0x53be…3ee8](https://etherscan.io/tx/0x53be0b25e576109384ff35cac841b562538a23315ba20b54e9fa54f953943ee8) $988,629 stETH at 0x889e…f9b1; [0xab5b…ab5d](https://etherscan.io/tx/0xab5b704be6a3694c652ff354f8e1afec088827ec00761584b51b9d529a9dab5d) $528,670 stETH at 0x889e…f9b1; [0x0d00…7105](https://etherscan.io/tx/0x0d0006fa1f31364495dc39861456e67f88159f526fda3084c083ef68ce687105) $369,152 stETH at 0x889e…f9b1.

#### stETH wrapped or unwrapped (27 transactions, $11,365,281)

What happens: stETH is exchanged for wstETH (or back) at the current share rate; a wallet changes the form of its staked ETH, usually before a DeFi deposit.

Rule: wstETH minted or burned with a stETH leg and no swap. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $184,743, p90 $1,014,968, max $1,014,968. Gross priced volume $63,348,883. 16 distinct senders, 16 principals, 7 destinations. By asset of the largest position: weETH ×11 ($9,701,842), wstETH ×15 ($1,417,837), stETH ×1 ($245,602). Hourly counts from the window start: 2 2 0 0 0 0 0 1 0 1 0 0 0 1 0 1 0 2 1 4 0 0 12 0.

Top destinations: [0x7f39…2ca0](https://etherscan.io/address/0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0) ×11; [0xcfc6…a7a2](https://etherscan.io/address/0xcfc6d9bd7411962bfe7145451a7ef71a24b6a7a2) ×11; [0x0889…2c9a](https://etherscan.io/address/0x0889e9327b98d7d1be3c301a4585ff3330502c9a) ×1; [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) ×1; [0xb7b4…b1e6](https://etherscan.io/address/0xb7b4ab065c45de1fca6a5a2899be98d196e9b1e6) ×1.

Largest examples: [0x80ba…91c5](https://etherscan.io/tx/0x80bab8e49785e86bf7bfae3d8eca6ad01ece9d7293607b53c9f543beb4dc91c5) $1,014,968 weETH at 0xc98b…56e2; [0x328c…05fb](https://etherscan.io/tx/0x328cac0de236cda99bdc087075202cfda8bbabb8e77b7d63e586ec2d1b1105fb) $1,014,968 weETH at 0xc98b…56e2; [0x5f60…dd65](https://etherscan.io/tx/0x5f60f699f1c13a7cef6fba76cb18eda27abe1ac0221beffc1cc5e791ed2fdd65) $1,014,968 weETH at 0xc98b…56e2; [0xe615…7a1e](https://etherscan.io/tx/0xe615bf3eb4e91cc0dc27057d5a275953fe5f0694c83f957aaaf211c9e15a7a1e) $1,014,968 weETH at 0xc98b…56e2; [0xb008…3277](https://etherscan.io/tx/0xb00806712f16b5286e4d4b9db96ce5b3bad8c79e641e6a69da096d44c60c3277) $1,014,968 weETH at 0xc98b…56e2; [0x4477…bf0e](https://etherscan.io/tx/0x44774d6a996087a3afa0dc0358c21f861ee61f6e5e79d803f75e7ad8cf3ebf0e) $1,014,968 weETH at 0xc98b…56e2.

#### validator deposit (199 transactions, $73,614,431)

What happens: ETH is deposited into the beacon deposit contract to activate or top up validators.

Rule: DepositEvent from the deposit contract. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $78,497, p90 $486,185, max $7,852,938. Gross priced volume $73,614,431. 167 distinct senders, 167 principals, 12 destinations. By asset of the largest position: ETH ×199 ($73,614,431). Hourly counts from the window start: 3 4 3 4 0 4 12 3 111 20 2 10 2 3 1 2 4 1 1 2 2 0 2 3.

Top destinations: [0x0000…05fa](https://etherscan.io/address/0x00000000219ab540356cbb839cbe05303d7705fa) ×167; [0xcd7a…6756](https://etherscan.io/address/0xcd7a6c118ac8f6544bc5076f2d8fb86d2c546756) ×7; [0x8b0d…aa62](https://etherscan.io/address/0x8b0d88b8be3c15d746feb0b1f18c883c03b6aa62) ×5; [0xd523…be34](https://etherscan.io/address/0xd523794c879d9ec028960a231f866758e405be34) ×4; [0xf007…5227](https://etherscan.io/address/0xf0075b3cf8953d3e23b0ef65960913fd97eb5227) ×3.

Largest examples: [0x3bd6…8daa](https://etherscan.io/tx/0x3bd60fa3a738c2931bf44b7cec5657e9336c8d06215000e983410212dbed8daa) $7,852,938 ETH at 0xd200…2b55; [0xcc5d…3f5c](https://etherscan.io/tx/0xcc5dad45330902b9d7b18238318768a13123f0c9f5e873da82d14aa2e8e63f5c) $7,810,174 ETH at 0xefe9…4340; [0xaf22…1fb6](https://etherscan.io/tx/0xaf2260d9d4c0b78a601c2568b709c363d116029f412cd1eec5568988258d1fb6) $4,419,378 ETH at 0xd724…6ab0; [0xce49…a13e](https://etherscan.io/tx/0xce49186bac0e93e71729cb020b3f845d4fc5995fc54649673801bfeac6e9a13e) $4,419,378 ETH at 0xd724…6ab0; [0x11cf…8021](https://etherscan.io/tx/0x11cf95082d01b2043217c97a6193ec522e0930b5600799e31a7816a3a7fd8021) $4,419,378 ETH at 0xd724…6ab0; [0x9b7f…fc94](https://etherscan.io/tx/0x9b7feb097f84850c8488d42fbf6cd2676396372e9d651e41b576961597c0fc94) $4,419,378 ETH at 0x2305…a23d.

#### other liquid-staking or restaking operation (16 transactions, $1,263,725)

What happens: Minting or burning of rETH, cbETH, weETH, or a deposit into EigenLayer or ether.fi.

Rule: Rocket Pool, EigenLayer or ether.fi events, or an LST minted or burned. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $57,799, p90 $174,062, max $467,194. Gross priced volume $4,129,699. 11 distinct senders, 11 principals, 7 destinations. By asset of the largest position: weETH ×11 ($974,715), rETH ×5 ($289,009). Hourly counts from the window start: 2 0 0 1 1 5 0 0 1 0 0 0 0 0 0 1 1 0 0 1 1 0 1 1.

Top destinations: [0x3633…e95c](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) ×5; [0xcfc6…a7a2](https://etherscan.io/address/0xcfc6d9bd7411962bfe7145451a7ef71a24b6a7a2) ×4; [0xd1a5…6e09](https://etherscan.io/address/0xd1a557fe9d49d047a2318c05a13523e4b9e56e09) ×2; [0xfbfe…be38](https://etherscan.io/address/0xfbfe6b9cee0e555bad7e2e7309effc75200cbe38) ×2; [0xf9f7…bcca](https://etherscan.io/address/0xf9f7969c357ce6dfd7973098ea0d57173592bcca) ×1.

Largest examples: [0x6ce8…40c8](https://etherscan.io/tx/0x6ce81d41e8e6ba466e53ef888ad52c1f43f9c1b150c2646f9adde99e5a6540c8) $467,194 weETH at 0xd1a5…6e09; [0xe2cf…20d3](https://etherscan.io/tx/0xe2cf6b7bbb9a57ae135262e27dc8fcbf71ecb3701014fef72266ccb7a39220d3) $174,062 weETH at 0x6802…657c; [0x3374…9f7f](https://etherscan.io/tx/0x3374d56272de8c864c0e27b4eba4274ac12053e1a77ac39fdaf362219e089f7f) $73,766 weETH at 0x31eb…2b76; [0x27dd…5dfa](https://etherscan.io/tx/0x27ddee97920ed36d39174681e79479de37dcd7c84640c880d78f201488705dfa) $70,080 weETH at 0x38b9…38aa; [0x5b28…3835](https://etherscan.io/tx/0x5b28bdb8ff09d3e820071fe43474fb496fd3e1afbfd4d68d7e60d5e1008a3835) $57,823 rETH at 0xba13…9ba9; [0xd2f3…454e](https://etherscan.io/tx/0xd2f3855faabe1727d2976f3fd159f45fc151c857a7632a9bb1fce6a9245d454e) $57,823 rETH at 0xba13…9ba9.

#### stake into a StakingRewards-style contract (8 transactions, $14,850,122)

What happens: Tokens enter the called contract and it emits Staked(address,uint256): a farm or rewards contract records the position; rewards accrue off the ledger.

Rule: Staked event and tokens entering the called contract, no swap. Method: `generic`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $1,796,000, p90 $4,382,679, max $4,382,679. Gross priced volume $14,850,122. 3 distinct senders, 3 principals, 1 destinations. By asset of the largest position: USDS ×8 ($14,850,122). Hourly counts from the window start: 1 0 0 0 0 0 0 0 0 0 1 1 1 0 0 0 0 0 2 0 1 1 0 0.

Top destinations: [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) ×8.

Largest examples: [0xb365…7e5a](https://etherscan.io/tx/0xb365042c1d62728a8fb7ceb05cc27493da37b0975ba3f5b65cb2d0c7709a7e5a) $4,382,679 USDS at 0xcf0a…cd69; [0x9d6f…6269](https://etherscan.io/tx/0x9d6fa40c702837c05e3508c30e53447a366502a1200107127c5f75f56f7e6269) $3,093,065 USDS at 0xcf0a…cd69; [0x44dd…d3c9](https://etherscan.io/tx/0x44dd66d905a173002c3b1ad87be17677fd0fd54f7d1ca971025ffe81226ed3c9) $1,970,248 USDS at 0xd6c7…fe9b; [0xbde8…d806](https://etherscan.io/tx/0xbde85795a59ce34d26e36745372d39a92f266ff13f08a885010ed967ce9dd806) $1,796,000 USDS at 0xcf0a…cd69; [0xc715…203b](https://etherscan.io/tx/0xc715a50afe514b0c2d04c1bbe78cf15e1d22748f11b08ffe5f30f3a5328f203b) $1,700,000 USDS at 0xcf0a…cd69; [0xa824…8958](https://etherscan.io/tx/0xa8249ea8251bc198c0118cfe1e27ed6e47784350133103f6a2b4caf37b9e8958) $689,535 USDS at 0x4e41…c86a.

#### withdrawal from a StakingRewards-style contract (11 transactions, $12,275,080)

What happens: The called contract emits Withdrawn(address,uint256) and returns tokens to the staker.

Rule: Withdrawn event and tokens leaving the called contract, no swap. Method: `generic`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $786,000, p90 $2,871,065, max $3,350,000. Gross priced volume $12,275,080. 5 distinct senders, 5 principals, 1 destinations. By asset of the largest position: USDS ×11 ($12,275,080). Hourly counts from the window start: 0 0 0 0 0 0 0 0 0 0 0 0 0 2 0 4 0 1 1 2 0 0 0 1.

Top destinations: [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) ×11.

Largest examples: [0x6a19…da1f](https://etherscan.io/tx/0x6a19ed872756db0240e4c790e3fe66d240ebfd8a5cb97deb0e51114f854cda1f) $3,350,000 USDS at 0xcf0a…cd69; [0xa48e…ca2b](https://etherscan.io/tx/0xa48e430f473c5063a99d42955d09cf83efc43b89e38ee4d5bbc89a0fcd12ca2b) $2,871,065 USDS at 0xcf0a…cd69; [0x8dfc…3bb3](https://etherscan.io/tx/0x8dfc5facbeac3ab059d11853fa61be828778940aa048745cee8a0bf626a73bb3) $1,700,000 USDS at 0x4e41…c86a; [0xe6e9…f0ea](https://etherscan.io/tx/0xe6e95cf5fc7e6208fe4f58e19c82828df5fdea0647796206dc2411141a38f0ea) $1,600,000 USDS at 0xf54a…de92; [0xf4db…cda4](https://etherscan.io/tx/0xf4dbb8a131bfe867acf8cb35138a854d76914006ca4b8a99130d6d9d7cc0cda4) $1,000,000 USDS at 0xcf0a…cd69; [0xa114…9675](https://etherscan.io/tx/0xa11490578ddb3da16ae103c39356fb4c4948b76042e9011d10709f8ad3f39675) $786,000 USDS at 0xcf0a…cd69.

### vault

#### deposit into an ERC-4626 vault (198 transactions, $113,844,102)

What happens: Assets go into a vault and shares are minted to the depositor (yield vaults, sUSDe, sDAI, MetaMorpho).

Rule: ERC-4626 Deposit event, no swap. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $81,578, p90 $585,192, max $25,000,000. Gross priced volume $181,979,825. 131 distinct senders, 130 principals, 68 destinations. By asset of the largest position: PYUSD ×13 ($40,592,874), sUSDe ×5 ($29,059,469), USDS ×13 ($16,027,970), USDC ×57 ($11,242,953), crvUSD ×37 ($5,269,289). Hourly counts from the window start: 17 18 13 8 8 7 10 6 4 5 11 2 3 8 8 8 5 3 13 12 5 6 5 13.

Top destinations: [0x6566…0245](https://etherscan.io/address/0x6566194141eefa99af43bb5aa71460ca2dc90245) ×20; [0x604e…711e](https://etherscan.io/address/0x604e586f17ce106b64185a7a0d2c1da5bace711e) ×16; [0x0c9a…e383](https://etherscan.io/address/0x0c9a3dd6b8f28529d72d7f9ce918d493519ee383) ×11; [0xecce…c25a](https://etherscan.io/address/0xeccef525b3063705da5075a1ce5de1892d24c25a) ×9; [0x134c…df76](https://etherscan.io/address/0x134ccaaa4f1e4552ec8aecb9e4a2360ddcf8df76) ×9.

Largest examples: [0xba9e…1fd7](https://etherscan.io/tx/0xba9e2d11712d1a1d583359144794dd35919d4e4207506434cf87a56288971fd7) $25,000,000 PYUSD at 0xb576…9fb2; [0x7852…6801](https://etherscan.io/tx/0x7852171614ec38369dbe9510a205f2ea7994d1133d1cf4672bb8d312159d6801) $20,002,393 sUSDe at 0xa711…6d69; [0x8e35…7d8f](https://etherscan.io/tx/0x8e35d2bf3ab1d4891c73d4b20da410a85b3d10b3e8f00f2151328dd9080e7d8f) $9,995,864 USDS at 0x99cd…eeb9; [0x3b9a…faf1](https://etherscan.io/tx/0x3b9ace99882098b4b7bbbe77eb1e68019d42e7d06bee1c39674fd2938b6efaf1) $8,870,220 sUSDe at 0x295f…689e; [0x526e…47d0](https://etherscan.io/tx/0x526e483dc7d8a9262626768953d87b1790641f3a1b6cdba473da1daf61e847d0) $8,184,018 PYUSD at 0xb576…9fb2; [0x5f82…b046](https://etherscan.io/tx/0x5f82e52912bf0607964245ecf0d9858f92084e1381c3d85421b1f7205490b046) $5,965,200 PYUSD at 0xc5e0…9720.

#### withdrawal from an ERC-4626 vault (268 transactions, $116,130,330)

What happens: Shares are burned and assets return to the owner.

Rule: ERC-4626 Withdraw event, no swap. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $95,559, p90 $799,887, max $18,000,000. Gross priced volume $195,308,223. 184 distinct senders, 195 principals, 70 destinations. By asset of the largest position: PYUSD ×18 ($46,801,235), sUSDe ×49 ($30,655,885), USDC ×65 ($14,741,965), USDS ×11 ($5,619,324), USDT ×22 ($4,498,927). Hourly counts from the window start: 31 18 17 11 14 10 11 5 11 5 16 10 6 7 8 2 8 6 11 18 10 7 10 16.

Top destinations: [0x9d39…3497](https://etherscan.io/address/0x9d39a5de30e57443bff2a8307a4256c8797a3497) ×36; [0xad95…595f](https://etherscan.io/address/0xad958c4c0c90bf0216e0f5472f074a9ab30f595f) ×28; [0x9fb7…1b33](https://etherscan.io/address/0x9fb7b4477576fe5b32be4c1843afb1e55f251b33) ×19; [0x604e…711e](https://etherscan.io/address/0x604e586f17ce106b64185a7a0d2c1da5bace711e) ×15; [0x0c9a…e383](https://etherscan.io/address/0x0c9a3dd6b8f28529d72d7f9ce918d493519ee383) ×14.

Largest examples: [0x8221…d0a5](https://etherscan.io/tx/0x82217e067af579e854f1d3d88840711078c163b2964d859680e9e46cc0a6d0a5) $18,000,000 PYUSD at 0xb576…9fb2; [0x9942…e654](https://etherscan.io/tx/0x99425159f3730ee8b52fa9bb123266f88fdcedfb2c135a1863df6b55280de654) $15,125,467 PYUSD at 0xc5e0…9720; [0xe593…3669](https://etherscan.io/tx/0xe593a7084c0ad1b71f6acbd00c413cea9284e68af8bab234eab5aa98d77b3669) $11,469,036 sUSDe at 0x5c2c…210f; [0x41cf…fc3a](https://etherscan.io/tx/0x41cf2b1d1993e56453994807fe8dad505b4a7fd94a2a1db54a9971a047b9fc3a) $4,880,284 PYUSD at 0xc5e0…9720; [0x5cca…4e7a](https://etherscan.io/tx/0x5cca0c603a1d7267b209d9d5d7241837fa4c30c4b3e8340189843338e2d44e7a) $3,753,603 USDC at 0x3b18…9fcd; [0xfb8f…1e1b](https://etherscan.io/tx/0xfb8f8817ed98af0c9a3a0223291838e63751e47a4421f01a40b490ca48271e1b) $3,000,157 USDS at 0x31db…fa01.

#### deposit that mints an unpriced receipt token (157 transactions, $46,763,701)

What happens: A priced asset leaves the principal and a token the registry cannot price is minted in the same transaction: shares of a vault, fund or pool whose events the registry does not name. The audit found these typed as trades; a minted receipt is a claim, not a counterparty payment.

Rule: no swap event, an unpriced token minted from the zero address, some address nets negative in a priced asset. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $40,029, p90 $479,394, max $15,000,000. Gross priced volume $4,776,832,384. 97 distinct senders, 97 principals, 59 destinations. By asset of the largest position: USDC ×35 ($17,788,889), PYUSD ×3 ($15,231,845), IMPL:0x5086…0c72 ×4 ($4,982,748), WBTC ×15 ($1,814,547), IMPL:0x98a8…4665 ×4 ($1,763,339). Hourly counts from the window start: 32 19 9 8 2 5 0 2 3 6 4 3 19 3 4 0 7 3 3 4 4 5 4 8.

Largest observed asset sender differs from the gas payer in 52 transactions. Transfer-leg directions: {"from_called_contract": 949, "into_called_contract": 2185, "third_party_to_third_party": 156}.

Top destinations: [0xae56…8ea2](https://etherscan.io/address/0xae563e3f8219521950555f5962419c8919758ea2) ×15; [0x8888…f946](https://etherscan.io/address/0x888888888889758f76e7103c6cbf23abbf58f946) ×13; [0x0000…87ac](https://etherscan.io/address/0x0000000000a39bb272e79075ade125fd351887ac) ×13; [0x0c04…f54d](https://etherscan.io/address/0x0c04e26262a4d979c17a1d2eee184eb6800df54d) ×12; [0x7a3d…2aad](https://etherscan.io/address/0x7a3ddeac7a0ae6dfa9391c764499a3564f3c2aad) ×10.

Largest examples: [0x0491…8af8](https://etherscan.io/tx/0x049190947cecff27e95ce77df1264d982dc8d8d92c78950ab8d94e93819a8af8) $15,000,000 PYUSD at 0x9761…1cca; [0x2f88…8cc5](https://etherscan.io/tx/0x2f880611c93a6e486957dc33a2dba5e6cb2adec28f56cf12327c082238188cc5) $4,299,748 IMPL:0x5086…0c72 at 0x971b…dda0; [0x2077…2974](https://etherscan.io/tx/0x207731e51f3867d2a147bcde43052dd0188ea6270a02a71434def9a6ca552974) $3,499,507 USDC at 0xc08f…a2c6; [0xf230…e2fe](https://etherscan.io/tx/0xf230c2dc7d6075026d52c6871753a1418ab9270353269ee891b7e2e08cbfe2fe) $3,049,071 USDC at 0x1440…bd90; [0x4a8b…4e11](https://etherscan.io/tx/0x4a8b02422bb84073224138fbc691cea6aff6b7b6a1d9264b5d0d360ea0594e11) $2,301,080 USDC at 0xf674…856c; [0x74d3…7cb7](https://etherscan.io/tx/0x74d3be508e4a6b71ff57be56cd498c5fcd5e499ba88571d20db0f47aac8a7cb7) $1,499,789 USDC at 0x774a…8807.

LLM note on this type: The audit sample of stablecoin_mint (0xe671775b…) and the residue head at 0x4f95c5ba… (0x9bc7d36e…) both show a priced deposit paired with a mint of a token the registry does not know; resolve named the second one USTB (Invesco short-duration US government fund token, 6 decimals): 620,502.52 USDC bought 55,393.83 USTB, about $11.20 per share (approx). Receipt tokens are claims, not counterparties; the type ranks after the lending rules because aTokens are minted receipts too.

#### withdrawal that burns an unpriced receipt token (90 transactions, $27,573,047)

What happens: The reverse: an unpriced token is burned and a priced asset reaches the principal.

Rule: no swap event, an unpriced token burned to the zero address, some address nets positive in a priced asset. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $50,283, p90 $693,897, max $3,083,658. Gross priced volume $35,811,845. 47 distinct senders, 49 principals, 30 destinations. By asset of the largest position: USDC ×25 ($12,338,752), crvUSD ×14 ($8,939,626), WBTC ×4 ($2,465,038), IMPL:0x0857…d8f6 ×3 ($1,453,650), WETH ×16 ($778,030). Hourly counts from the window start: 6 11 9 2 2 5 5 7 7 0 3 0 6 3 0 0 7 3 1 3 2 1 2 5.

Largest observed asset sender differs from the gas payer in 80 transactions. Transfer-leg directions: {"from_called_contract": 37, "into_called_contract": 18, "third_party_to_third_party": 76}.

Top destinations: [0x8888…f946](https://etherscan.io/address/0x888888888889758f76e7103c6cbf23abbf58f946) ×15; [0xae56…8ea2](https://etherscan.io/address/0xae563e3f8219521950555f5962419c8919758ea2) ×15; [0xbc6d…ffe2](https://etherscan.io/address/0xbc6dbe2c5f172bbb736aa58cfa9bfcb20c85ffe2) ×12; [0x6ad0…66cc](https://etherscan.io/address/0x6ad038ca6c04e885630851278ca0a856ad9a66cc) ×5; [0x0c9a…e383](https://etherscan.io/address/0x0c9a3dd6b8f28529d72d7f9ce918d493519ee383) ×4.

Largest examples: [0x0bb5…1eea](https://etherscan.io/tx/0x0bb514b886525a626db3108e8c03f30c758042f5007d6a7756167afbf15f1eea) $3,083,658 USDC at 0xdddd…6f3f; [0xc827…becb](https://etherscan.io/tx/0xc827a0de9bfc9effbeb033a5fae2be7aac8547fb97de40c572f4b331241dbecb) $3,049,071 USDC at 0xf5de…73e8; [0x43ae…470b](https://etherscan.io/tx/0x43ae566604f39859ac51e611d41500e8bce36fafc33506c48f48618083aa470b) $3,011,766 USDC at 0x7a9e…cb98; [0x67e4…76c2](https://etherscan.io/tx/0x67e4a47890c96149e4b5f7f000675971a5479536acc31f67e9b04993233276c2) $1,117,983 WBTC at 0xe3d4…f2ef; [0x0d3f…9de9](https://etherscan.io/tx/0x0d3f730cd16c44f89e53380bb6957a3aafde1365f0d3e055d6f3350002269de9) $1,007,978 USDC at 0xcf25…68fb; [0xf82a…4885](https://etherscan.io/tx/0xf82a9f7530df8ccfd9fb906e1ff409e0eb24e8cc20f87c6f59b3046cd03a4885) $841,649 WBTC at 0xe3d4…f2ef.

#### position or order opened with an NFT receipt (21 transactions, $3,277,142)

What happens: A priced asset leaves the sender and an ERC-721 is minted to the sender: a position, order or vault share represented as an NFT (the window's case routes WBTC into a 0x-Settler-style contract and mints the receipt).

Rule: an ERC-721 transfer, a priced leg paid by the sender, no swap, no marketplace event. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $57,176, p90 $367,029, max $753,678. Gross priced volume $4,009,809. 18 distinct senders, 18 principals, 10 destinations. By asset of the largest position: IMPL:0xe343…491d ×7 ($951,433), USDC ×6 ($832,526), WBTC ×1 ($753,678), IMPL:0x5e84…aa1f ×1 ($367,029), IMPL:0xd166…2df7 ×5 ($351,609). Hourly counts from the window start: 1 2 3 1 1 0 1 0 0 0 4 0 0 0 0 1 1 0 3 2 0 1 0 0.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"from_called_contract": 8, "into_called_contract": 2, "third_party_to_third_party": 25}.

Top destinations: [0x02d9…b66d](https://etherscan.io/address/0x02d9876a21af7545f8632c3af76ec90b5ad4b66d) ×6; [0xd166…2df7](https://etherscan.io/address/0xd166337499e176bbc38a1fbd113ab144e5bd2df7) ×5; [0xf94e…e85d](https://etherscan.io/address/0xf94e5cdf41247e268d4847c30a0dc2893b33e85d) ×3; [0xa741…5da3](https://etherscan.io/address/0xa741a32f9dcfe6adba088fd0f97e90742d7d5da3) ×1; [0x82ba…27bd](https://etherscan.io/address/0x82ba8da44cd5261762e629dd5c605b17715727bd) ×1.

Largest examples: [0x9bc5…47b3](https://etherscan.io/tx/0x9bc56beb2effb64a90f4ca6f35dcc2e533639c96f855c0e05ce9df90c3c647b3) $753,678 WBTC at 0x71f1…14b0; [0x5d4c…7760](https://etherscan.io/tx/0x5d4c605a5b6b70684bedb28b4c61da56936eb9367973061b62de7a50f5f67760) $617,953 USDC at 0x71f1…14b0; [0x7f12…6e7f](https://etherscan.io/tx/0x7f122ba7a8d3458bb6e6f80d07791943af1ec5b2071acc4ea921b61e5a796e7f) $367,029 IMPL:0x5e84…aa1f at 0xf1c7…cb8b; [0x6971…a1aa](https://etherscan.io/tx/0x6971a1f25b15c4f6f610f893be511796581aedac42cfe30019d1c594fb18a1aa) $224,888 IMPL:0xe343…491d at 0x31a6…c6b4; [0xa012…a1bd](https://etherscan.io/tx/0xa0128db9c80476713dd852ea1c92dfcfac3964ad096edd169a6adf8c36c3a1bd) $223,210 IMPL:0xe343…491d at 0xf5f5…ae91; [0xf1b5…08f0](https://etherscan.io/tx/0xf1b542a05b18c1825aefbbdcf7b3dc1935d40a07a973dc2da7d8de54f47f08f0) $199,910 IMPL:0xd166…2df7 at 0x6d34…d23b.

#### sUSDe cooldown claim (unstake) (24 transactions, $17,908,746)

What happens: After the cooldown, unstake(receiver) on the sUSDe contract releases USDe from the silo to the receiver; the shares were burned when the cooldown started, so this transaction shows only the USDe leaving the silo.

Rule: destination is the sUSDe contract, selector unstake(address) 0xf2888dbb, a USDe leg is present. Method: `generic`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $178,664, p90 $1,465,545, max $10,033,001. Gross priced volume $17,908,746. 24 distinct senders, 24 principals, 1 destinations. By asset of the largest position: USDe ×24 ($17,908,746). Hourly counts from the window start: 0 0 2 2 2 3 0 2 3 0 0 0 1 0 0 2 0 0 1 1 2 2 0 1.

Top destinations: [0x9d39…3497](https://etherscan.io/address/0x9d39a5de30e57443bff2a8307a4256c8797a3497) ×24.

Largest examples: [0x7170…3936](https://etherscan.io/tx/0x717031756cf5facb0be14412d0c1efc1bc1bf3c8ebfbf01bc7c4d89343363936) $10,033,001 USDe at 0xf078…f19e; [0x31ca…5e60](https://etherscan.io/tx/0x31ca5a0b7b36e65d9f053434242f42d39c0cb2a585caa7d601a921d3f78d5e60) $1,938,219 USDe at 0xcf7e…c904; [0x3ee8…71d0](https://etherscan.io/tx/0x3ee841e40b031b12081fa392fb46658324d839a8f2f044300d9d7241ba2a71d0) $1,465,545 USDe at 0x8b41…cdd7; [0x6c2c…14bb](https://etherscan.io/tx/0x6c2c4995571675f42fa2820105ddea3164fee25838d268840ec804f069bb14bb) $825,409 USDe at 0x7fc7…3425; [0xc6a4…8bb4](https://etherscan.io/tx/0xc6a44c60bbabea18a3da6e3a6dee458afd2f56aaa17b79cc115513820d998bb4) $648,036 USDe at 0xed8c…7968; [0x78b9…a8ce](https://etherscan.io/tx/0x78b9cd93b6672bf77a2c43f64e96ddb7edcde14c2b428dd7d6a03ffe5185a8ce) $436,243 USDe at 0x9eb8…2595.

#### ETH deposited, wrapped and forwarded by a router (67 transactions, $8,502,253)

What happens: Native value enters the called contract, which wraps it and passes the WETH on to a vault or strategy that records shares or totals in its own events. A deposit into a yield product whose events the registry does not name.

Rule: top-level value, a WETH Deposit credited to the called contract and WETH legs leaving it, no swap. Method: `custody_flow`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $36,800, p90 $196,097, max $1,996,222. Gross priced volume $25,939,713. 42 distinct senders, 42 principals, 12 destinations. By asset of the largest position: ETH ×46 ($7,325,317), WETH ×21 ($1,176,936). Hourly counts from the window start: 6 5 7 7 2 1 2 2 2 3 4 1 0 0 2 2 2 4 3 3 4 2 1 2.

Largest observed asset sender differs from the gas payer in 14 transactions. Transfer-leg directions: {"from_called_contract": 93, "into_called_contract": 67}.

Top destinations: [0xe68a…42be](https://etherscan.io/address/0xe68ab4f90fe026b9873f5f276ed2d7efbbbe42be) ×19; [0xb92f…ff4f](https://etherscan.io/address/0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f) ×13; [0xac9f…d405](https://etherscan.io/address/0xac9f360ae85469b27aeddeafc579ef2d052ad405) ×12; [0x829e…77d4](https://etherscan.io/address/0x829eac83b5287a665b9859bf8aa7f09467af77d4) ×11; [0xee03…5b86](https://etherscan.io/address/0xee030ec6f4307411607e55acd08e628ae6655b86) ×3.

Largest examples: [0x6279…96f9](https://etherscan.io/tx/0x62795aca91efec61eb7b22cf39cb2b95f544a9f39698714fd528eb3b3e5596f9) $1,996,222 ETH at 0xe68a…42be; [0x955f…52ae](https://etherscan.io/tx/0x955ff8d4258744947eafcba8dcffb7bf724312db98b75a0d586d3f9719fd52ae) $976,757 ETH at 0xe68a…42be; [0x5003…db8d](https://etherscan.io/tx/0x5003f6314688f0006d5b46201b2d8a08c408092f112c4ea0b9cbd9eeb8fcdb8d) $961,284 ETH at 0xfe34…1adb; [0xc1f5…1f12](https://etherscan.io/tx/0xc1f5a1f76b362c901cb6cecc023fce6023b35ebe87721a88ef4061722cd51f12) $655,141 ETH at 0xbee4…beee; [0xd18d…0d64](https://etherscan.io/tx/0xd18d0262fe95a7551a96e2bfbdcf66084f8a4bb66bdfabb6d84e79a808920d64) $534,782 ETH at 0xac9f…d405; [0xe0e0…b441](https://etherscan.io/tx/0xe0e0ad624e21254fb3360f0199588713f4fc41ad5793e8f0591a4326c040b441) $246,401 ETH at 0xe68a…42be.

### nft

#### NFT sale (15 transactions, $1,007,887)

What happens: An ERC-721 or ERC-1155 changes hands against ETH or WETH through a marketplace.

Rule: marketplace event plus a priced leg and no swap; an NFT transfer alone does not establish a sale. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $18,195, p90 $149,979, max $631,561. Gross priced volume $1,010,947. 14 distinct senders, 14 principals, 4 destinations. By asset of the largest position: USDT ×1 ($631,561), USDC ×2 ($174,975), WETH ×7 ($123,855), ETH ×5 ($77,496). Hourly counts from the window start: 0 1 1 0 1 3 1 0 2 1 0 1 0 0 0 1 1 1 0 0 0 0 0 1.

Top destinations: [0x0000…b395](https://etherscan.io/address/0x0000000000000068f116a894984e2db1123eb395) ×12; [0x5ff1…2789](https://etherscan.io/address/0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789) ×1; [0x39da…d541](https://etherscan.io/address/0x39da41747a83aee658334415666f3ef92dd0d541) ×1; [0x4524…45d8](https://etherscan.io/address/0x4524011801bb496deaaf675eed123ed2ba5945d8) ×1.

Largest examples: [0x8661…6a5e](https://etherscan.io/tx/0x866190ecf466767ed8341dfda651e4b6d890adbcc7e8a85508544c5c66f96a5e) $631,561 USDT at 0xa435…2e4f; [0x3d50…3336](https://etherscan.io/tx/0x3d501ebd5b04fbbd37cf7ec2afe99baf79c4d2f6cabf4dae17a943eb7bda3336) $149,979 USDC at 0x2793…cb86; [0x1db7…3709](https://etherscan.io/tx/0x1db72a917b1f9f973c8d427f621297b377edfda9526e4fa49e06a64d51343709) $24,996 USDC at 0xff3f…617e; [0x75d6…fb25](https://etherscan.io/tx/0x75d61beb822588cec24eeb8a8c0f43027457914d87b284001d164f016e0efb25) $23,752 ETH at 0xad30…be64; [0x3df8…70ef](https://etherscan.io/tx/0x3df86a14f3aaa3d8f4cc69722d736e39db5418013efba074792f66deb18e70ef) $23,027 WETH at 0xbdba…9558; [0x99c4…2ce1](https://etherscan.io/tx/0x99c44c4320a6336236f902a1ed678ad668289201a500ca8a4dfe1ef40c652ce1) $21,049 WETH at 0xea94…b685.

### transfer

#### ETH wrapped into WETH (324 transactions, $36,861,067)

What happens: A wallet converts ETH to its ERC-20 form, usually inventory management by a trading wallet before a pool or bridge operation.

Rule: actual canonical WETH Deposit leg, optionally native input, and one log. Method: `transfer`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #5.

Largest position change: median $29,982, p90 $161,010, max $2,432,705. Gross priced volume $54,094,766. 58 distinct senders, 58 principals, 9 destinations. By asset of the largest position: WETH ×101 ($19,627,368), ETH ×223 ($17,233,699). Hourly counts from the window start: 20 16 17 26 13 12 11 13 14 11 15 10 10 8 9 14 17 11 14 18 8 9 11 17.

Sizes: 100k-1M ×58, 10k-100k ×257, 1M-10M ×9; native ×0, token ×324; fresh sender in 9, fresh counterparty in 0.

Top counterparties: [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) ×216 $16,566,410; [0x447a…5d73](https://etherscan.io/address/0x447a03c131c0a97a8b8d548e3cd81aec4ce05d73) ×6 $654,969; [0xc0b7…5a2e](https://etherscan.io/address/0xc0b7d8de1c2c7ebfc483d72b5750cf07a4e85a2e) ×1 $12,320.

Top destinations: [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) ×216; [0xfd03…b7f0](https://etherscan.io/address/0xfd03abcadaf3f930fa4e37eb2f6ea3a44a41b7f0) ×73; [0xad03…f0c7](https://etherscan.io/address/0xad03abc6223e9def79b3feb624f54303a372f0c7) ×14; [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) ×8; [0x447a…5d73](https://etherscan.io/address/0x447a03c131c0a97a8b8d548e3cd81aec4ce05d73) ×6.

Largest examples: [0x9bff…5924](https://etherscan.io/tx/0x9bff0a406563f50fc941e9b76d38447c13a5c4a97be947935a935e8f2fd55924) $2,432,705 WETH at 0x51c7…2a7f; [0xac2e…e1d2](https://etherscan.io/tx/0xac2e39d6e83be1ad938b27b05937bdc2c31d7715e611d8e4ee8aa4b12f2ee1d2) $2,347,438 WETH at 0x51c7…2a7f; [0x8efb…b3d8](https://etherscan.io/tx/0x8efbf7fd913817512023d624abaef8ae0e49876cd8432acc54ab990d911fb3d8) $2,173,567 WETH at 0x51c7…2a7f; [0x3334…d6d3](https://etherscan.io/tx/0x3334daaa0923f182d5e8169b76e46348ca030e544ad995c9063acdb124f8d6d3) $2,151,308 WETH at 0x51c7…2a7f; [0x4709…d93e](https://etherscan.io/tx/0x47092b0adb82d70c9c1936588fd88ff0155529df1d96eea5e114da33b853d93e) $2,137,613 WETH at 0x51c7…2a7f; [0xcf09…a1a8](https://etherscan.io/tx/0xcf0915d89ba24d215682b3413db5c09d298579fce6fc1b8d255502492fc2a1a8) $2,123,670 WETH at 0x51c7…2a7f.

#### WETH unwrapped into ETH (111 transactions, $18,344,381)

What happens: The reverse conversion.

Rule: the only leg is a WETH Withdrawal, one log. Method: `transfer`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $36,576, p90 $245,336, max $2,907,232. Gross priced volume $18,344,381. 41 distinct senders, 41 principals, 5 destinations. By asset of the largest position: WETH ×111 ($18,344,381). Hourly counts from the window start: 8 6 4 3 4 7 2 6 3 4 8 6 3 1 6 4 5 7 5 2 4 4 5 4.

Sizes: 100k-1M ×12, 10k-100k ×94, 1M-10M ×5; native ×0, token ×111; fresh sender in 2, fresh counterparty in 0.

Top destinations: [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) ×102; [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) ×4; [0xbee3…a000](https://etherscan.io/address/0xbee3211ab312a8d065c4fef0247448e17a8da000) ×3; [0x29ff…dfee](https://etherscan.io/address/0x29ffcd598123eba08839e10cb9ad23dc28f2dfee) ×1; [0x2e10…cc71](https://etherscan.io/address/0x2e104fb25676c7c3e3a5a648865cca1db15dcc71) ×1.

Largest examples: [0x513a…0b13](https://etherscan.io/tx/0x513a32f3d95b444e551f450a80ec329b2dffdc4b50398956d47895c76d9a0b13) $2,907,232 WETH at 0x51c7…2a7f; [0xfdbd…561c](https://etherscan.io/tx/0xfdbdb874cb1c41d079511d53e9a927f23c061edea84fa85afa943564f4aa561c) $2,407,338 WETH at 0x51c7…2a7f; [0x9619…e630](https://etherscan.io/tx/0x96193e3b8f463c635cf91977f7cafaf05464aefc8c7117426f21f085cb8ce630) $2,144,237 WETH at 0x51c7…2a7f; [0x7637…80eb](https://etherscan.io/tx/0x7637190d5a561034d55c30e5cb2e80aac38535da170503da2852b411317480eb) $2,128,320 WETH at 0x51c7…2a7f; [0x80d9…9b21](https://etherscan.io/tx/0x80d9dc54be1c632a8d35990a6be6df68c8f3ee956be18ea5c6e4adf0de7f9b21) $1,362,012 WETH at 0xbee3…a000; [0x79a0…aebd](https://etherscan.io/tx/0x79a098c46073c9d38b536f7fe6209acbb47ea8dc48ad4576f8e9913b6639aebd) $976,144 WETH at 0xb3c5…4dda.

#### one sender paying many recipients (939 transactions, $936,807,003)

What happens: One transaction distributes an asset to five or more addresses: exchange batch withdrawals, payroll, airdrops, rewards.

Rule: five or more distinct recipients, no swap, the principal only pays out. Method: `generic`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $44,857, p90 $1,023,737, max $71,823,586. Gross priced volume $983,622,274. 61 distinct senders, 60 principals, 34 destinations. By asset of the largest position: USDC ×383 ($701,966,854), USDT ×272 ($108,983,872), cbBTC ×33 ($103,047,343), IMPL:0x232c…4ee2 ×18 ($4,709,668), AAVE ×17 ($3,630,347). Hourly counts from the window start: 72 100 69 68 50 54 52 50 41 34 34 33 34 25 30 33 15 12 22 17 20 19 27 28.

Top destinations: [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) ×729; [0xa322…59b3](https://etherscan.io/address/0xa3222357a0eccf60c73606170be6c99adecb59b3) ×44; [0xfaf1…83f8](https://etherscan.io/address/0xfaf17849fb05a11a4e233f221bac99ca43fc83f8) ×36; [0x09c3…d818](https://etherscan.io/address/0x09c30cdcdd971423cb3ba757a47d56c35d06d818) ×28; [0x663d…c251](https://etherscan.io/address/0x663dc15d3c1ac63ff12e45ab68fea3f0a883c251) ×13.

Largest examples: [0x6962…b950](https://etherscan.io/tx/0x6962b81128e24da658091f171ef4443af2797a472335af1257edeb77d8b5b950) $71,823,586 USDC at 0xa9d1…3e43; [0x8083…906b](https://etherscan.io/tx/0x80839214f65ecf4959b40463993d5f3d633814c7f67451ed02b87c90c59b906b) $52,767,213 USDC at 0xa9d1…3e43; [0xf332…8cf0](https://etherscan.io/tx/0xf332efb54082a697eaba84780f97716905dd80e1dc06977ff89c6d848b4b8cf0) $50,379,903 USDC at 0xa9d1…3e43; [0xec5c…48fa](https://etherscan.io/tx/0xec5c6ff06bd4db0f0e8c6dd692cc5db75a65839ad43d3ab9fd1c0fda816748fa) $50,008,032 USDC at 0xa9d1…3e43; [0xa70b…6be5](https://etherscan.io/tx/0xa70b9f76be240fb7b70c6cbae4bea96ee3128ab7b68a3400806a3a51b47e6be5) $50,007,286 USDC at 0xa9d1…3e43; [0x5f75…0046](https://etherscan.io/tx/0x5f7529402ebd08c8764ced6e7498cfc9f67f6c1e3fee2073ed4d3d48278e0046) $46,947,845 USDC at 0xa9d1…3e43.

#### plain transfer without a behavioural subtype (14,356 transactions, $7,526,643,843)

What happens: A native or single-token transfer whose parties show no exchange-like, bot-like or pass-through behaviour over the window: OTC settlement, custody movement, a person moving funds. The largest class of unknown purpose; the profile of each side is the only evidence.

Rule: plain transfer with no actor tag matched above. Method: `transfer`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $39,994, p90 $500,836, max $389,437,444. Gross priced volume $7,540,623,867. 6,913 distinct senders, 6,913 principals, 985 destinations. By asset of the largest position: USDC ×4942 ($4,459,056,528), USDT ×5390 ($1,414,489,650), ETH ×1673 ($736,615,330), cbBTC ×27 ($291,976,027), wstETH ×18 ($100,023,152). Hourly counts from the window start: 1482 1425 1215 1019 788 791 726 511 410 379 352 375 321 289 283 325 349 486 493 568 411 405 444 509.

Sizes: 100k-1M ×3160, 10M+ ×88, 10k-100k ×10293, 1M-10M ×815; native ×1673, token ×12667; fresh sender in 1346, fresh counterparty in 985.

Top counterparties: [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) ×4 $803,226,331; [0xf1ed…56a8](https://etherscan.io/address/0xf1edbf98dda764ec51de3776371f0f7d6f6156a8) ×1 $389,437,444; [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) ×3 $246,347,214; [0x47b8…e0a9](https://etherscan.io/address/0x47b869d84df9ee2a04dd546ae4c79d80508ae0a9) ×3 $147,979,176; [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) ×1 $143,979,739; [0x15ab…de48](https://etherscan.io/address/0x15abb66ba754f05cbc0165a64a11cded1543de48) ×4 $136,710,122.

Top destinations: [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) ×5390; [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×4942; [0x1f98…f984](https://etherscan.io/address/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984) ×181; [0x57e1…6061](https://etherscan.io/address/0x57e114b691db790c35207b2e685d4a43181e6061) ×162; [0xfaba…9be3](https://etherscan.io/address/0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3) ×157.

Largest examples: [0x64a8…da77](https://etherscan.io/tx/0x64a84fd6497c5c1dbfef5a5ed88efc7061e1e057514178aa22d5a15d4824da77) $389,437,444 USDC at 0xf1ed…56a8; [0x828c…2093](https://etherscan.io/tx/0x828c49a31ca85ab347cc441e31ebf199f793f0465438c41592d6ad24c7342093) $389,437,444 USDC at 0xf1ed…56a8; [0xd114…07c3](https://etherscan.io/tx/0xd114e389e9fb6c4a258c024317ea2157956ae83a6a7a1b5df2a7d391eee507c3) $245,457,705 USDC at 0x688c…5cbf; [0x1682…95bf](https://etherscan.io/tx/0x168250500b1cea038f042d04f860afcfc1ac54c74753bbecf4f9de1aa8eb95bf) $245,457,705 USDC at 0x688c…5cbf; [0x1c97…29a7](https://etherscan.io/tx/0x1c97c7557e446f04ca1a3d32ea86cc75613ff3ad8ce51ee287bba2d5b24629a7) $143,979,739 USDC at 0x5695…0149; [0x0f13…77eb](https://etherscan.io/tx/0x0f1365d77eee69dd4780159c2cc47b0e6ed0c07ec009cf0bbec9359d80fc77eb) $143,979,739 USDC at 0x5695…0149.

#### token moved by an operator (transferFrom) (1,385 transactions, $996,348,874)

What happens: A contract or operator moves a user's approved tokens: custody sweeps, subscription pulls, protocol deposits that do not emit their own event.

Rule: selector transferFrom with at most two logs and no swap. Method: `transfer`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $45,162, p90 $699,902, max $98,986,071. Gross priced volume $996,348,874. 158 distinct senders, 269 principals, 32 destinations. By asset of the largest position: USDC ×727 ($893,267,642), USDT ×285 ($49,720,669), IMPL:0xe343…491d ×37 ($32,869,095), IMPL:0x6982…1933 ×45 ($3,317,231), IMPL:0x1aba…c33c ×18 ($3,002,633). Hourly counts from the window start: 146 138 112 102 82 75 72 50 50 40 42 30 40 31 35 50 32 40 35 45 40 22 38 38.

Sizes: 100k-1M ×313, 10M+ ×18, 10k-100k ×949, 1M-10M ×105; native ×0, token ×1302; fresh sender in 0, fresh counterparty in 60.

Top counterparties: [0xb8d4…c31d](https://etherscan.io/address/0xb8d4a4dfaa73c2c81868bf8c86a0f197c92cc31d) ×2 $120,982,975; [0x1d3f…4d41](https://etherscan.io/address/0x1d3f6f8ae6f02271db0f0173b1cf5ba3f6404d41) ×3 $76,989,166; [0x47b8…e0a9](https://etherscan.io/address/0x47b869d84df9ee2a04dd546ae4c79d80508ae0a9) ×1 $74,989,448; [0xc0a2…265a](https://etherscan.io/address/0xc0a2bc76be4cfda76594dcae17894317be2b265a) ×1 $49,992,965; [0x774a…8807](https://etherscan.io/address/0x774ae279c21b6a17a6e2bd5ab5398ff98f398807) ×7 $49,621,543; [0x5014…bebb](https://etherscan.io/address/0x5014fbb0360e03c1ce6c8a0b815823f1dbc3bebb) ×1 $34,765,241.

Top destinations: [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×727; [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) ×285; [0x6982…1933](https://etherscan.io/address/0x6982508145454ce325ddbe47a25d4ec3d2311933) ×45; [0xfaba…9be3](https://etherscan.io/address/0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3) ×38; [0x232c…4ee2](https://etherscan.io/address/0x232ce3bd40fcd6f80f3d55a522d03f25df784ee2) ×37.

Largest examples: [0xeb47…08a8](https://etherscan.io/tx/0xeb4734715db27df740a49109a67a6c9f4cc562e11fdc539ff3dbb4b8a1e208a8) $98,986,071 USDC at 0xb8d4…c31d; [0x92be…e63b](https://etherscan.io/tx/0x92be2d9979e8d85e2e7f76dd490dc9692b1be487791051d36e640aa7b082e63b) $74,989,448 USDC at 0xa850…4ed3; [0xd844…9294](https://etherscan.io/tx/0xd844bdf3f8c11c7e1505c2cf82a7d3378b73ed9f0055484438a47f48f3ef9294) $49,992,965 USDC at 0xc0a2…265a; [0x7602…63b2](https://etherscan.io/tx/0x7602429a5c8da4e940bd62e21e69a3d62fbf63df74e855674df4c229df1063b2) $40,095,040 USDC at 0x774a…8807; [0xff6e…0d50](https://etherscan.io/tx/0xff6e0bef63404d2d4c7e0e765f3137ded62e7ef899a5ac26b934574959090d50) $36,494,864 USDC at 0x47b8…e0a9; [0x1085…b19b](https://etherscan.io/tx/0x108581b2971a0274a0f0d50c23ede5e1036ba81ff20b03893bd1dc9777feb19b) $36,494,864 USDC at 0x47b8…e0a9.

#### claim of vested, distributed or reward tokens (8 transactions, $365,653)

What happens: The called contract pays tokens it holds and emits a Claimed-style event: vesting, airdrop or reward distribution.

Rule: a Claimed-style event family with tokens leaving the called contract, no swap. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $20,006, p90 $195,404, max $195,404. Gross priced volume $365,653. 5 distinct senders, 5 principals, 2 destinations. By asset of the largest position: IMPL:0x2323…aa71 ×7 ($354,255), PYUSD ×1 ($11,399). Hourly counts from the window start: 1 0 0 0 0 0 4 0 0 0 0 0 0 0 0 1 0 0 1 0 0 0 0 1.

Largest observed asset sender differs from the gas payer in 8 transactions. Transfer-leg directions: {"from_called_contract": 8}.

Top destinations: [0x4bc9…3d2e](https://etherscan.io/address/0x4bc9fec04f0f95e9b42a3ef18f3c96fb57923d2e) ×7; [0x3ef3…d9ae](https://etherscan.io/address/0x3ef3d8ba38ebe18db133cec108f4d14ce00dd9ae) ×1.

Largest examples: [0x32f2…364e](https://etherscan.io/tx/0x32f2101692a4009a70ef5bd1c18bf46cb74a2871237894813c976043b865364e) $195,404 IMPL:0x2323…aa71 at 0xe413…d177; [0x43d2…7df0](https://etherscan.io/tx/0x43d2d8ca5fb93662eb4d341d6a21ec86e3cd69d5a3f6e770edc7d9ef93cc7df0) $70,052 IMPL:0x2323…aa71 at 0xc163…42bc; [0xb2f9…f2dc](https://etherscan.io/tx/0xb2f97a433356e096311f99fa372e082d7e3aad329ff241fb10a39c646f7cf2dc) $29,984 IMPL:0x2323…aa71 at 0xc163…42bc; [0xef60…d3c9](https://etherscan.io/tx/0xef60b40c6eccb9a70d64cb2040e65bd4b52797d0e319a40f5cde10e719b5d3c9) $20,006 IMPL:0x2323…aa71 at 0xc163…42bc; [0x1cce…0585](https://etherscan.io/tx/0x1ccecd473fc19dbe3a6e16a402324f0cfa8fa57e3e231dd783ad924ff8d00585) $18,639 IMPL:0x2323…aa71 at 0xdf6c…5e02; [0xb282…49f2](https://etherscan.io/tx/0xb2827a10b463af93b16a2ea97c37a03090bb22a0a24fa000ee0f5cbf420d49f2) $11,399 PYUSD at 0x3ef3…d9ae.

#### sender's own tokens sent through a contract call (231 transactions, $29,601,625)

What happens: The transaction sender's tokens move to fewer than five recipients through a helper contract (multisend, app-specific transfer) that emits nothing else.

Rule: only transfer events, every priced leg is paid by the sender to addresses other than the destination. Method: `custody_flow`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $39,872, p90 $163,324, max $8,136,292. Gross priced volume $29,870,701. 91 distinct senders, 91 principals, 31 destinations. By asset of the largest position: USDC ×96 ($9,449,833), weETH ×1 ($8,136,292), USDT ×73 ($7,504,060), IMPL:0xe343…491d ×20 ($2,599,166), WBTC ×19 ($984,356). Hourly counts from the window start: 31 21 16 10 12 12 6 8 5 6 4 7 6 8 4 5 12 11 10 5 11 4 6 11.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"into_called_contract": 1, "third_party_to_third_party": 446}.

Top destinations: [0xfaf1…83f8](https://etherscan.io/address/0xfaf17849fb05a11a4e233f221bac99ca43fc83f8) ×58; [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) ×45; [0x94e7…c485](https://etherscan.io/address/0x94e7a5dcbe816e498b89ab752661904e2f56c485) ×28; [0x973a…5a08](https://etherscan.io/address/0x973a023a77420ba610f06b3858ad991df6d85a08) ×20; [0xf41b…8a56](https://etherscan.io/address/0xf41b389e0c1950dc0b16c9498eae77131cc08a56) ×19.

Largest examples: [0x82dc…9bf8](https://etherscan.io/tx/0x82dc7aa4ff6981fdd0ed247ea6e9fac6879f2f06ebf9b5e3fdbb8c18d3429bf8) $8,136,292 weETH at 0xcca8…26c9; [0x974b…5434](https://etherscan.io/tx/0x974b0f9c8305f9b4e869c46c9af3d5f5c203f61ef202d0a8d13dd72aa4c55434) $3,199,550 USDC at 0x7fb6…796e; [0x124f…9130](https://etherscan.io/tx/0x124fd09b51d67724728b03174313724b6158e3c2d4f0c955dc45e0fdca4c9130) $1,200,093 USDT at 0x9642…5d4e; [0x9b19…a675](https://etherscan.io/tx/0x9b19ac5a7d0dbe3a759c3b4c2d645124cdc0b80feda075715a3180fb420ca675) $1,002,492 USDT at 0x9642…5d4e; [0x29fe…c04e](https://etherscan.io/tx/0x29fe6982260e0059689bca889b2c621a1b5d4d1154d21f78fdb497846cdcc04e) $987,865 USDT at 0x9642…5d4e; [0x2a6e…e113](https://etherscan.io/tx/0x2a6ea04fbf11ee6ebe4f9eea9572478b229308290935394b0c5d7bad88afe113) $509,058 USDT at 0x9642…5d4e.

### exchange flow

#### transfer between high-connectivity wallets (1,601 transactions, $750,401,491)

What happens: Value moves between two high-connectivity addresses. Shared ownership or exchange identity cannot be established from these five-hour activity profiles.

Rule: plain native or single-token transfer; sender and recipient both carry hot_wallet or many_sources tags. Method: `exchange`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $32,968, p90 $337,014, max $43,900,443. Gross priced volume $750,401,491. 99 distinct senders, 99 principals, 109 destinations. By asset of the largest position: USDT ×291 ($331,095,132), ETH ×492 ($283,306,926), USDC ×225 ($59,377,697), RLUSD ×8 ($12,734,018), UNI ×86 ($12,338,190). Hourly counts from the window start: 147 100 123 88 58 63 58 63 57 42 57 52 62 80 37 48 60 51 54 73 72 47 48 61.

Sizes: 100k-1M ×310, 10M+ ×14, 10k-100k ×1213, 1M-10M ×64; native ×492, token ×1097; fresh sender in 0, fresh counterparty in 7.

Net inflow to exchange-tagged wallets over the window $0.00; hourly: $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00 $0.00.

Wallets: [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 107 txs, in $0.00, out $464,275,489 (LINK ×17, ETH ×17, USDT ×16); [0xcffa…0703](https://etherscan.io/address/0xcffad3200574698b78f32232aa9d63eabd290703) 8 txs, in $0.00, out $43,686,836 (IMPL:0x6874…2f38 ×1, ETH ×1, IMPL:0x4580…af78 ×1); [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) 64 txs, in $0.00, out $23,080,955 (USDC ×63, IMPL:0x1aba…c33c ×1); [0xc17a…a753](https://etherscan.io/address/0xc17a40852e4bfe04bc81af355fdf132c539ba753) 32 txs, in $0.00, out $21,856,362 (USDT ×11, IMPL:0x6982…1933 ×4, IMPL:0x6874…2f38 ×3); [0x9696…6976](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 16 txs, in $0.00, out $16,076,640 (ETH ×10, USDT ×6); [0x0510…cfe7](https://etherscan.io/address/0x0510b1a8b756836e0563358737d445aa8589cfe7) 51 txs, in $0.00, out $15,586,606 (USDC ×51); [0x4976…2327](https://etherscan.io/address/0x4976a4a02f38326660d17bf34b431dc6e2eb2327) 14 txs, in $0.00, out $12,258,762 (ETH ×14); [0x3cc9…cf18](https://etherscan.io/address/0x3cc936b795a188f0e246cbb2d74c5bd190aecf18) 5 txs, in $0.00, out $11,768,673 (USDT ×2, USDe ×2, IMPL:0xa2cd…fb18 ×1).

Top counterparties: [0x56ed…b17f](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) ×3 $115,842,594; [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) ×13 $111,083,661; [0x9696…6976](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) ×3 $108,473,089; [0x4976…2327](https://etherscan.io/address/0x4976a4a02f38326660d17bf34b431dc6e2eb2327) ×2 $57,653,969; [0x21a3…5549](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) ×11 $57,133,347; [0x4634…9758](https://etherscan.io/address/0x46340b20830761efd32832a74d7169b29feb9758) ×8 $43,686,836.

Top destinations: [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) ×291; [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×225; [0x1f98…f984](https://etherscan.io/address/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984) ×86; [0x5149…86ca](https://etherscan.io/address/0x514910771af9ca656af840dff83e8264ecf986ca) ×74; [0xfaba…9be3](https://etherscan.io/address/0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3) ×60.

Largest examples: [0xcf77…8040](https://etherscan.io/tx/0xcf77a2467c257f625664f84fbbb6154fce1ec8955054e1727ca736e147bc8040) $43,900,443 USDT at 0x56ed…b17f; [0xc83a…a4dc](https://etherscan.io/tx/0xc83a6a2c9b358ab5c03135ea7a9b51113f454054c5cf826fb16c29d62e01a4dc) $43,222,564 USDT at 0x56ed…b17f; [0x7e78…4031](https://etherscan.io/tx/0x7e786bbcca37b4c2aa564415d74876491609e3ae87799d1f8e4f2f47c9f04031) $40,815,563 USDT at 0x28c6…1d60; [0x10b4…26b8](https://etherscan.io/tx/0x10b4f7cedbe547f7e14a95f8d4c553623436a3fb19cb1c87eb0b8748bdff26b8) $40,463,308 USDT at 0xdfd5…963d; [0xbe11…3aea](https://etherscan.io/tx/0xbe118b7e24aa833768abf9b6b3d34e3f1b786c6cbe2f9a8ba8a03ce4b38c3aea) $40,229,988 USDT at 0x9696…6976; [0x06f9…6d9d](https://etherscan.io/tx/0x06f95dec2bf15fe53fbac113fe72180cf94bf2cdf8b52c2f2a48e13474b46d9d) $40,094,281 USDT at 0x9696…6976.

#### withdrawal from an exchange-like hot wallet (7,139 transactions, $1,589,605,814)

What happens: A hot wallet that sends to many destinations pays out to a customer address; the recipient is usually quiet. Exchange identity and customer intent are hypotheses; distributions, treasury operations and other services can share this behaviour.

Rule: plain transfer whose sender has the hot_wallet tag (>= 100 transactions to >= 50 distinct destinations in the window). Method: `exchange`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #2, #9.

Largest position change: median $34,079, p90 $400,018, max $50,002,194. Gross priced volume $1,589,605,814. 170 distinct senders, 170 principals, 1,220 destinations. By asset of the largest position: USDT ×2573 ($767,412,096), ETH ×2074 ($356,612,157), USDC ×1004 ($270,773,632), IMPL:0xe343…491d ×65 ($53,482,294), IMPL:0x6874…2f38 ×75 ($24,540,365). Hourly counts from the window start: 613 548 491 393 367 345 353 311 238 192 236 192 230 214 213 217 194 249 286 287 223 245 226 276.

Sizes: 100k-1M ×1648, 10M+ ×12, 10k-100k ×5208, 1M-10M ×271; native ×2074, token ×5061; fresh sender in 0, fresh counterparty in 699.

Net inflow to exchange-tagged wallets over the window -$1,589,605,814; hourly: -$108,564,068 -$135,802,825 -$125,189,131 -$72,774,896 -$172,778,955 -$105,748,884 -$114,051,184 -$51,869,794 -$57,706,861 -$37,565,708 -$131,167,907 -$23,096,289 -$38,247,969 -$41,918,426 -$36,721,982 -$29,917,019 -$36,062,015 -$51,982,180 -$44,145,302 -$29,416,679 -$31,760,558 -$30,634,182 -$37,894,982 -$44,588,021.

Wallets: [0x7713…35ec](https://etherscan.io/address/0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec) 64 txs, in $0.00, out $163,882,163 (USDT ×39, USDC ×14, ETH ×8); [0xaa8b…3efb](https://etherscan.io/address/0xaa8ba7d4611437141192e7ceced531bc0a133efb) 243 txs, in $0.00, out $151,557,402 (USDT ×243); [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 509 txs, in $0.00, out $118,748,045 (USDT ×228, ETH ×120, LINK ×29); [0x21a3…5549](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 535 txs, in $0.00, out $94,950,162 (USDT ×253, ETH ×114, LINK ×35); [0x56ed…b17f](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 332 txs, in $0.00, out $90,398,100 (USDT ×247, ETH ×85); [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 418 txs, in $0.00, out $79,059,433 (USDT ×171, ETH ×116, UNI ×24); [0xf819…73aa](https://etherscan.io/address/0xf8191d98ae98d2f7abdfb63a9b0b812b93c873aa) 161 txs, in $0.00, out $77,863,285 (LINK ×30, IMPL:0xfaba…9be3 ×19, IMPL:0xa2cd…fb18 ×19); [0x05ff…f381](https://etherscan.io/address/0x05ff6964d21e5dae3b1010d5ae0465b3c450f381) 4 txs, in $0.00, out $77,490,928 (USDC ×4).

Top counterparties: [0x1468…b65c](https://etherscan.io/address/0x14681e4e26f1b5b5774ae3b7f694ff08bbbeb65c) ×13 $79,328,570; [0x2744…a22b](https://etherscan.io/address/0x2744dfd9898f0babbc570cc594bbbc84b487a22b) ×4 $77,490,928; [0xeae7…a4f4](https://etherscan.io/address/0xeae7380dd4cef6fbd1144f49e4d1e6964258a4f4) ×61 $62,172,856; [0xea6d…ae1c](https://etherscan.io/address/0xea6df897fc8ea83d2b81391abec672ae1cfbae1c) ×5 $54,659,871; [0x6aea…5065](https://etherscan.io/address/0x6aea888bcf4fd52213e9d03e7c69a45d98b35065) ×3 $52,337,807; [0x5f2d…64b9](https://etherscan.io/address/0x5f2d3a7eff1af3754bc033d8b80e189a54db64b9) ×44 $44,028,288.

Top destinations: [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) ×2573; [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×1004; [0x232c…4ee2](https://etherscan.io/address/0x232ce3bd40fcd6f80f3d55a522d03f25df784ee2) ×172; [0x5149…86ca](https://etherscan.io/address/0x514910771af9ca656af840dff83e8264ecf986ca) ×147; [0x1f98…f984](https://etherscan.io/address/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984) ×123.

Largest examples: [0x4e91…ff64](https://etherscan.io/tx/0x4e919c5efe1fc2a219290d54aced631526959ccf96bda8e8b5534f9ae773ff64) $50,002,194 USDT at 0xaa8b…3efb; [0x9495…9ab9](https://etherscan.io/tx/0x9495d2ce7c122f3ab3d7810cc61b569dee7c331ac5b2bb53d8430b865f039ab9) $50,002,192 USDT at 0xea6d…ae1c; [0xba80…d005](https://etherscan.io/tx/0xba804941ae2412f3d506ad13f3315f301d1de9df5ffc25098476c5d65d22d005) $47,010,220 USDC at 0x2744…a22b; [0xe3f4…e18e](https://etherscan.io/tx/0xe3f4f10f007c68af31cf6fb5e777492b2dd1a67a04a93b9ab91f7edc9922e18e) $18,041,484 USDC at 0x2744…a22b; [0xe04b…b4a6](https://etherscan.io/tx/0xe04b147e509d3ab5e3b87ccacc390f27af3a4ae6f933e9148c09990a56f3b4a6) $14,736,798 USDT at 0x98ad…ba9d; [0x142a…7935](https://etherscan.io/tx/0x142acdf539200d4b576d36b63109f9125e80c206697a008c46e81bea244a7935) $13,282,603 IMPL:0x6874…2f38 at 0xb99a…bcf5.

#### deposit into an exchange-like wallet (9,792 transactions, $3,841,865,960)

What happens: A customer or a deposit address sends to a wallet that receives from many sources over the window. Exchange identity and customer intent are hypotheses; distributions, treasury operations and other services can share this behaviour.

Rule: plain transfer whose recipient has the hot_wallet or many_sources tag. Method: `exchange`. Origin: pilot iteration 2 (2-minute sample, 2026-09-05 09:31 UTC) #11.

Largest position change: median $38,002, p90 $524,122, max $120,005,267. Gross priced volume $3,841,865,960. 5,387 distinct senders, 5,387 principals, 186 destinations. By asset of the largest position: USDC ×2487 ($1,860,309,957), USDT ×3566 ($1,217,283,830), ETH ×1933 ($565,194,768), IMPL:0xe343…491d ×66 ($34,715,849), IMPL:0x232c…4ee2 ×180 ($18,484,130). Hourly counts from the window start: 836 740 682 628 480 486 480 442 364 285 284 285 270 287 247 293 274 315 353 397 349 293 336 386.

Sizes: 100k-1M ×2234, 10M+ ×51, 10k-100k ×7020, 1M-10M ×487; native ×1933, token ×7855; fresh sender in 1356, fresh counterparty in 3.

Net inflow to exchange-tagged wallets over the window $3,841,865,960; hourly: $375,914,848 $300,323,910 $340,144,794 $191,498,771 $220,542,019 $511,026,328 $346,679,805 $166,744,548 $320,546,420 $86,027,908 $196,955,216 $50,131,738 $37,739,829 $69,015,289 $58,010,623 $61,931,916 $48,160,976 $57,622,403 $81,572,963 $109,845,206 $73,289,737 $39,972,131 $56,184,330 $41,984,251.

Wallets: [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) 852 txs, in $964,182,520, out $0.00 (USDC ×279, USDT ×270, ETH ×102); [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 2142 txs, in $638,620,789, out $0.00 (USDT ×1231, ETH ×458, LINK ×65); [0xcd53…ca7b](https://etherscan.io/address/0xcd531ae9efcce479654c4926dec5f6209531ca7b) 98 txs, in $574,328,876, out $0.00 (USDC ×69, USDT ×13, ETH ×6); [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) 599 txs, in $343,913,966, out $0.00 (USDC ×599); [0x7713…35ec](https://etherscan.io/address/0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec) 85 txs, in $184,619,359, out $0.00 (USDT ×60, USDC ×12, ETH ×10); [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 219 txs, in $160,253,306, out $0.00 (USDT ×219); [0xa9ac…4573](https://etherscan.io/address/0xa9ac43f5b5e38155a288d1a01d2cbc4478e14573) 99 txs, in $64,379,904, out $0.00 (ETH ×99); [0x445f…bd97](https://etherscan.io/address/0x445f16314284b43dfa1fd3cd77b9dea4a1bebd97) 125 txs, in $59,445,533, out $0.00 (USDC ×125).

Top counterparties: [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) ×852 $964,182,520; [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) ×2142 $638,620,789; [0xcd53…ca7b](https://etherscan.io/address/0xcd531ae9efcce479654c4926dec5f6209531ca7b) ×98 $574,328,876; [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) ×599 $343,913,966; [0x7713…35ec](https://etherscan.io/address/0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec) ×85 $184,619,359; [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) ×219 $160,253,306.

Top destinations: [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) ×3566; [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×2487; [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) ×458; [0x1f98…f984](https://etherscan.io/address/0x1f9840a85d5af5bf1d1762f925bdaddc4201f984) ×186; [0x232c…4ee2](https://etherscan.io/address/0x232ce3bd40fcd6f80f3d55a522d03f25df784ee2) ×180.

Largest examples: [0x505a…252c](https://etherscan.io/tx/0x505a62c7abf4bea7fc2210ad0d31d0a63240d4eb4d7e5ec3fc43dbbf8110252c) $120,005,267 USDT at 0x7713…35ec; [0x56fe…6c9f](https://etherscan.io/tx/0x56fec119ab391baebcacace2976b5408b145da67ef6de95c8973388379576c9f) $71,819,884 USDC at 0xcd53…ca7b; [0xc5b1…267c](https://etherscan.io/tx/0xc5b11b089ceb534a38b89ae027502019accf5c67212dd610e4c9e2a559c0267c) $66,760,846 USDC at 0xa9d1…3e43; [0x7a30…b54c](https://etherscan.io/tx/0x7a3005022fb9f490023e3a3ad4c05b018ca987d66aae7bf257e3df22b66fb54c) $65,520,986 USDC at 0xfff2…b5ce; [0x63be…fba4](https://etherscan.io/tx/0x63be98fea5fef022bd4a7f11ea2d2ab27833d1d42a026409b2720bcbeed1fba4) $54,042,114 ETH at 0xa9d1…3e43; [0xac22…2a9a](https://etherscan.io/tx/0xac22a3a633220b0c5851c7cb70c38eb26786ff3dc562acc0d2d02589ea072a9a) $53,992,402 USDC at 0xcd53…ca7b.

LLM note on this type: The largest sink, 0xa9d1e08c…, is a 6,889-byte contract that received $964M in 852 deposits and paid 729 batch payouts in the day: one contract for both directions of an exchange's customer flow. The type's rule (recipient tagged hot_wallet or many_sources) does not distinguish an EOA hot wallet from such a contract; the audit sample (0xe711719f…) deposited into 0xee7ae85f…, also a contract with many sources.

#### sweep of a deposit address (4,802 transactions, $1,055,285,811)

What happens: A pass-through address forwards what it received to a collector: exchange back-office consolidation. Exchange identity and customer intent are hypotheses; distributions, treasury operations and other services can share this behaviour.

Rule: plain transfer where either side is a pass-through address (few sources, one destination, net zero over the window). Method: `exchange`. Origin: seeded 2026-09-05 from event shapes, before the window run.

Largest position change: median $30,001, p90 $248,319, max $49,992,965. Gross priced volume $1,055,285,811. 3,186 distinct senders, 3,186 principals, 1,345 destinations. By asset of the largest position: USDC ×1036 ($541,047,547), USDT ×1717 ($268,640,971), ETH ×1588 ($189,938,509), USDe ×76 ($23,661,384), WBTC ×13 ($5,648,092). Hourly counts from the window start: 398 404 359 303 257 231 245 195 279 133 117 167 113 93 93 123 154 151 129 161 188 156 172 181.

Sizes: 100k-1M ×802, 10M+ ×11, 10k-100k ×3862, 1M-10M ×127; native ×1588, token ×3213; fresh sender in 782, fresh counterparty in 1244.

Net inflow to exchange-tagged wallets over the window -$302,335,178; hourly: -$13,552,464 -$4,701,014 -$2,996,693 -$219,893 -$3,393,904 -$153,597,973 -$56,088,182 -$521,432 -$55,627,536 -$26,638 -$104,809 -$1,833,952 -$810,716 -$575,539 -$1,390,560 -$3,500,880 -$487,125 -$798,117 -$321,541 -$669,450 -$62,859 -$256,294 -$194,848 -$602,759.

Wallets: [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) 12 txs, in $0.00, out $207,231,687 (USDC ×12); [0xcd53…ca7b](https://etherscan.io/address/0xcd531ae9efcce479654c4926dec5f6209531ca7b) 24 txs, in $0.00, out $75,017,382 (USDC ×16, ETH ×3, UNI ×2); [0x549d…3425](https://etherscan.io/address/0x549d835356d92983abb76e4cae639f7857963425) 16 txs, in $0.00, out $37,838,554 (ETH ×6, USDC ×5, RLUSD ×3); [0x29c9…71a1](https://etherscan.io/address/0x29c97b183ec6776ecd6975050c00862f930171a1) 5 txs, in $0.00, out $33,142,455 (USDT ×5); [0xb5e4…c24e](https://etherscan.io/address/0xb5e4d21240e9356cafc3a1261d10383f62dfc24e) 7 txs, in $0.00, out $22,000,966 (USDT ×7); [0xceb6…66ea](https://etherscan.io/address/0xceb69f6342ece283b2f5c9088ff249b5d0ae66ea) 6 txs, in $0.00, out $15,675,318 (ETH ×6); [0xaaf9…a45b](https://etherscan.io/address/0xaaf9f14f20145ad50db369e52b2793bfeb18a45b) 4 txs, in $0.00, out $15,000,658 (USDT ×4); [0x059b…2dea](https://etherscan.io/address/0x059b02159f6743efc33a87b08bb5099374762dea) 2 txs, in $0.00, out $14,998,812 (USDT ×1, USDC ×1).

Top counterparties: [0x28c5…151a](https://etherscan.io/address/0x28c5b0445d0728bc25f143f8eba5c5539fae151a) ×4 $199,971,860; [0x2d3e…f504](https://etherscan.io/address/0x2d3e6f78efca59f15220b4478cfc5d06daaff504) ×3 $53,992,402; [0x4705…8dbb](https://etherscan.io/address/0x47057c2a6f0a7cbdc865697a6412dae6c6148dbb) ×5 $33,142,455; [0x7c1c…46ab](https://etherscan.io/address/0x7c1c091f8999eb921c45914ec48bd2d2fd7846ab) ×5 $19,500,856; [0x3f0b…2b5d](https://etherscan.io/address/0x3f0b86ffca24d869773447ba2f6f1c83ee372b5d) ×2 $18,432,354; [0xea59…a524](https://etherscan.io/address/0xea59bb2a900558a8c459fad77b72327ab892a524) ×2 $15,997,749.

Top destinations: [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) ×1717; [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) ×1036; [0x4c9e…68b3](https://etherscan.io/address/0x4c9edd5852cd905f086c759e8383e09bff1e68b3) ×76; [0xc183…9d72](https://etherscan.io/address/0xc18360217d8f7ab5e7c516566761ea12ce7f9d72) ×45; [0xa2cd…fb18](https://etherscan.io/address/0xa2cd3d43c775978a96bdbf12d733d5a1ed94fb18) ×43.

Largest examples: [0x16f2…27e4](https://etherscan.io/tx/0x16f262d6b1866ffaffdb4b724aefe3d0aba6fda71b587784e5755186d32727e4) $49,992,965 USDC at 0x55fe…44b8; [0xb19d…2ead](https://etherscan.io/tx/0xb19d9e1cad23e51585562427b6c192874e2003de842a84e0425c86ddad522ead) $49,992,965 USDC at 0x55fe…44b8; [0x1617…21f4](https://etherscan.io/tx/0x161794fb12fba5c41557b7a45033533814619ffd09d1a29f376473c5d58821f4) $49,992,965 USDC at 0x55fe…44b8; [0x0668…efc9](https://etherscan.io/tx/0x06681e6b69d870a46c7e849df4d89a2ccf949fc901f700d396917a4051f7efc9) $49,992,965 USDC at 0x55fe…44b8; [0xb6b2…9fbf](https://etherscan.io/tx/0xb6b295a67cf097b1cf392b7757480694cee51fb108363551eb69cf1e69b49fbf) $32,402,720 USDC at 0xcd53…ca7b; [0xbd5a…08b5](https://etherscan.io/tx/0xbd5ad4e21259fe82750032b0ce32271a6be5147a810013a1e5543d5a8a9308b5) $19,996,997 USDC at 0xcd53…ca7b.

### custody

#### deposit recorded with a Relay-style deposit event (10 transactions, $397,228)

What happens: A depository other than the documented Relay contract emits the same RelayNativeDeposit or RelayErc20Deposit shape as value enters it; the inherited relay_deposit rule pins one address, this entry records the shape wherever it appears.

Rule: Relay-style deposit event from any emitter with value or tokens entering the called contract. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $13,000, p90 $244,139, max $244,139. Gross priced volume $397,228. 9 distinct senders, 9 principals, 3 destinations. By asset of the largest position: ETH ×10 ($397,228). Hourly counts from the window start: 1 2 0 1 0 0 0 0 0 0 0 0 1 0 0 3 0 1 0 0 0 1 0 0.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"into_called_contract": 10}.

Top destinations: [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) ×7; [0x50c4…5909](https://etherscan.io/address/0x50c4e75a512f2a14a7b304787adf79c4531a5909) ×2; [0x0000…2734](https://etherscan.io/address/0x0000000000001ff3684f28c67538d4d072c22734) ×1.

Largest examples: [0x02cc…daf0](https://etherscan.io/tx/0x02cce819b4b2249527aab17ca8a372aa6cebbb675da3c3ffb62e25623e7edaf0) $244,139 ETH at 0x5629…9e34; [0x7abc…ca84](https://etherscan.io/tx/0x7abc3358c46e0d2fb4461603697e98c64ee6c61db749c0dd2b45d63bdbc5ca84) $49,979 ETH at 0xf786…9abd; [0x904a…0d24](https://etherscan.io/tx/0x904a2ca066f4f91d37a6ca55d255df1e62338f3e2cb63c6b30d0bc6a31ed0d24) $17,656 ETH at 0xf70d…9eb3; [0x5217…5ea1](https://etherscan.io/tx/0x52172417f835ebe63da396f1a03a5105e708caeb0254fd9e68e1cc49a39b5ea1) $14,720 ETH at 0x24d6…6aa6; [0xf7d0…e5dc](https://etherscan.io/tx/0xf7d0cf52687a9ff8298df978e3334bc541f13b9082b7af073a782d949fdbe5dc) $13,000 ETH at 0xcc6f…b316; [0x04ee…0831](https://etherscan.io/tx/0x04ee32d0eca26c00f26bcb18f58f1955752e332eab17827bf1fb9502539a0831) $12,274 ETH at 0xa7dc…3d0f.

#### operator moving approved tokens through Permit2 (34 transactions, $1,181,077)

What happens: A relayer calls Permit2's transferFrom with a batch of (owner, recipient, amount, token) entries; users' tokens move under Permit2 allowances into one collector. The gas payer owns nothing; the asset owners approved Permit2 earlier. Seen as exchange or bridge deposit sweeps.

Rule: destination is the documented Permit2 contract, selector is transferFrom (single or batch), only transfer events. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $16,710, p90 $87,785, max $205,587. Gross priced volume $1,182,027. 4 distinct senders, 4 principals, 1 destinations. By asset of the largest position: USDT ×29 ($826,225), USDC ×5 ($354,852). Hourly counts from the window start: 3 4 1 3 2 0 0 1 2 1 0 0 1 0 1 1 2 0 0 3 1 5 1 2.

Largest observed asset sender differs from the gas payer in 34 transactions. Transfer-leg directions: {"third_party_to_third_party": 607}.

Top destinations: [0x0000…8ba3](https://etherscan.io/address/0x000000000022d473030f116ddee9f6b43ac78ba3) ×34.

Largest examples: [0x36c5…805d](https://etherscan.io/tx/0x36c56412ab267789f0a21499cdf9e93cd7b04c24d8ef12cf4a76ab05cffc805d) $205,587 USDT at 0xe4f9…4a03; [0xea4b…68ab](https://etherscan.io/tx/0xea4b9c7c1d297766874d56c7be4c1cf5504d09ae1c1b6c5abe972b3bcbc568ab) $148,630 USDC at 0x935d…e6a9; [0x45d5…be44](https://etherscan.io/tx/0x45d57b805f0376dbeb746abb3cdfea6030380ca80642723f3a874789c183be44) $137,143 USDC at 0xb9af…164e; [0x3b4d…a6e3](https://etherscan.io/tx/0x3b4d5a7eb43a4bd633a35954e137612ede66b61bc9cbd0deea1cd552cf32a6e3) $87,785 USDT at 0x773b…18d5; [0x989e…303f](https://etherscan.io/tx/0x989ecc1ece4235453baea44c380717517fd003c809d1a3652cdc04fdb2a4303f) $83,826 USDT at 0x935d…e6a9; [0xe34b…9a4c](https://etherscan.io/tx/0xe34b9e1631d004c9003671448cce136940229c969eed3b41af6b0485d70a9a4c) $44,688 USDC at 0xb9af…164e.

#### custody vault sweep or payout by its operator ABI (410 transactions, $247,615,237)

What happens: A vault contract of one custody system either pulls an approved balance from a client address (sweep) or pays out under a signed instruction with deadline and nonce, or hands tokens to the calling hot wallet. Four vaults share the ABI; single transfers of $15M-$28M USDC between vaults are internal rebalancing.

Rule: one of three custody selectors (sweep, payout, withdraw), exactly one priced transfer that enters or leaves the called contract, only transfer events. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $62,964, p90 $1,030,823, max $27,853,798. Gross priced volume $247,615,237. 30 distinct senders, 51 principals, 63 destinations. By asset of the largest position: USDC ×161 ($186,205,892), USDT ×211 ($55,798,278), UNI ×5 ($1,549,415), IMPL:0x1aba…c33c ×2 ($1,033,492), WBTC ×5 ($997,828). Hourly counts from the window start: 55 34 56 46 28 33 39 20 6 6 9 6 6 6 11 6 1 11 10 8 4 2 4 3.

Largest observed asset sender differs from the gas payer in 410 transactions. Transfer-leg directions: {"from_called_contract": 239, "into_called_contract": 171}.

Top destinations: [0x3a5c…d597](https://etherscan.io/address/0x3a5cc8689d1b0cef2c317bc5c0ad6ce88b27d597) ×62; [0xbd02…75b8](https://etherscan.io/address/0xbd02c51150a4ab6ce97b9de2025644594f3e75b8) ×53; [0xa4d6…757c](https://etherscan.io/address/0xa4d65fd5017bb20904603f0a174bbbd04f81757c) ×41; [0x1522…e428](https://etherscan.io/address/0x1522900b6dafac587d499a862861c0869be6e428) ×34; [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) ×33.

Largest examples: [0x6575…95df](https://etherscan.io/tx/0x657573aa5f60a4f9457152fccecbe1d3e58a11972127fec35f22acd50ad095df) $27,853,798 USDC at 0x367c…dca0; [0xf19b…a272](https://etherscan.io/tx/0xf19bce7fb3d6342f5ba89a48af02c4438308df86bba0062b13299ec8735ba272) $14,997,890 USDC at 0x9ab0…9d0a; [0x769b…1d6f](https://etherscan.io/tx/0x769bd270389ec44ff18a5f0113fb5c9abbc7c82bf3f5a4d75660b368f4961d6f) $11,998,307 USDC at 0xb5e4…c24e; [0xfe96…7868](https://etherscan.io/tx/0xfe9646df34b8fd299e3d000b35f8579959966b05a7d9e20ac21d9cdb6a4b7868) $10,398,532 USDC at 0x367c…dca0; [0xaeaf…f56a](https://etherscan.io/tx/0xaeafa8befec9f7a7d928d3792598744a87b72a93cefe952cd897e6f60509f56a) $10,398,532 USDC at 0x3e55…ef0f; [0x34d6…b02e](https://etherscan.io/tx/0x34d6abf01c4317875ce590afe724d646df997f226191f109f5ea454ca469b02e) $9,998,588 USDC at 0xf5d5…7e15.

LLM note on this type: Four vault contracts (0x100ae042…, 0x367c42a6…, 0x3a5cc868…, 0xa4d65fd5…) share one ABI: sweep(address account, address token) pulls an approved client balance into the vault, payout(address to, uint256 amount, address token, uint256 deadline, uint256 nonce) sends under a signed instruction, and withdraw(address token, uint256 amount) hands tokens to the calling hot wallet. Operator EOAs with nonces in the hundreds of thousands drive them at flat tips. Single vault-to-vault movements of $12M-$28M are internal rebalancing, not customer flow; the sweep and withdraw legs are the customer-facing ones. Identity of the custodian is not established.

#### sweep of per-customer forwarder contracts into a collector (359 transactions, $52,444,224)

What happens: The paying address of every transfer is itself a contract that emits an event as it forwards: a deposit-forwarder pattern where each customer has a tiny contract and an operator sweeps them into a hub. The hub is the counterparty with many sources.

Rule: every priced leg is paid by an address that emits a custom event in the same transaction and is neither the sender nor the destination. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $47,128, p90 $300,652, max $4,231,562. Gross priced volume $60,127,763. 79 distinct senders, 80 principals, 24 destinations. By asset of the largest position: USDC ×137 ($21,098,320), IMPL:0x232c…4ee2 ×31 ($7,123,227), USDT ×84 ($5,664,077), WETH ×41 ($5,152,197), IMPL:0xe343…491d ×34 ($4,686,981). Hourly counts from the window start: 22 23 17 27 7 28 20 47 10 8 13 5 6 9 8 5 12 18 9 17 6 12 12 18.

Largest observed asset sender differs from the gas payer in 359 transactions. Transfer-leg directions: {"into_called_contract": 326, "third_party_to_third_party": 335}.

Top destinations: [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) ×64; [0x16dd…7972](https://etherscan.io/address/0x16dd80d93c88549c5f774691cb66ddffae6a7972) ×60; [0x33b4…629c](https://etherscan.io/address/0x33b41fe18d3a39046ad672f8a0c8c415454f629c) ×47; [0x1161…c32c](https://etherscan.io/address/0x116193c58b40d50687c0433b2aa0cc4ae00bc32c) ×40; [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) ×36.

Largest examples: [0xf35b…c5ae](https://etherscan.io/tx/0xf35b69c9c4aeb98cde8417110802a6e8a4db37541050a3973093b425b5efc5ae) $4,231,562 USDC at 0x4691…3093; [0x0e26…37c7](https://etherscan.io/tx/0x0e26fa43e35d9249dda1647d2220234e2404af3f4b6597712d0e5201655837c7) $2,899,592 USDC at 0xcf61…d81a; [0xf7fc…8b66](https://etherscan.io/tx/0xf7fcead8d5eb7a39b32017e86940da4e0fd88b39c06ff42ae5cdb7939cc38b66) $2,360,082 IMPL:0x232c…4ee2 at 0x3b4d…5ca7; [0x41d5…a953](https://etherscan.io/tx/0x41d570bc2d214fa9bfce8298ec5b5917fdd4fee6c1e202f7d69cd65bbac3a953) $1,985,419 WETH at 0xcca8…26c9; [0xf1da…0d76](https://etherscan.io/tx/0xf1dae0485e4f6290ab8a7690b8f48d9da621ad187971489be9c13fc782b50d76) $1,342,955 USD1 at 0xd24c…95ba; [0xbf5a…2e6e](https://etherscan.io/tx/0xbf5affb6521d56e571bb9a910779ac12ad4f9fdf21bfaae2c6133efb24792e6e) $1,333,473 USDC at 0x6981…da22.

#### deposit into a service contract with a routing memo (234 transactions, $10,639,315)

What happens: Value enters a contract that records the deposit, and the calldata carries a printable memo such as a destination chain, token and address (for example USDT(TRON)|<address>|0.05|bridgers|): a cross-chain swap or off-chain delivery order. The contract pays out on other orders through operator calls.

Rule: calldata holds a printable memo of 8+ characters; value or tokens enter the called contract; the contract emits its own event. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $22,387, p90 $87,622, max $981,873. Gross priced volume $10,639,315. 138 distinct senders, 138 principals, 14 destinations. By asset of the largest position: ETH ×118 ($4,997,059), USDT ×41 ($2,920,939), USDC ×42 ($2,113,160), DAI ×24 ($365,429), WETH ×9 ($242,727). Hourly counts from the window start: 15 9 11 16 13 12 11 14 6 9 4 3 2 13 7 11 9 11 9 7 10 9 12 11.

Largest observed asset sender differs from the gas payer in 3 transactions. Transfer-leg directions: {"into_called_contract": 273, "third_party_to_third_party": 1}.

Top destinations: [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) ×91; [0xd37b…7146](https://etherscan.io/address/0xd37bbe5744d730a1d98d8dc97c42f0ca46ad7146) ×47; [0xb300…028d](https://etherscan.io/address/0xb300000b72deaeb607a12d5f54773d1c19c7028d) ×39; [0xb8f2…81a8](https://etherscan.io/address/0xb8f275fbf7a959f4bce59999a2ef122a099e81a8) ×27; [0xb685…895b](https://etherscan.io/address/0xb685760ebd368a891f27ae547391f4e2a289895b) ×16.

Largest examples: [0x1569…2e60](https://etherscan.io/tx/0x15697afb421d8d980bdabdd7883b94e62bc0ad8aeb9369a747b12b973f152e60) $981,873 ETH at 0xc1d1…a1b5; [0x3680…b8fc](https://etherscan.io/tx/0x368032e876eb5612e8f7a049e4bc94e0a0a268c78dfbaecc9601367cbf14b8fc) $487,584 ETH at 0xc1d1…a1b5; [0x419e…ff3c](https://etherscan.io/tx/0x419ef2adbcf45f4f53b336bc8b0ed8d8362c1e59677ebd0aefa96267903eff3c) $481,799 USDT at 0xb685…895b; [0xaacf…eb46](https://etherscan.io/tx/0xaacf3d07a88bfd6eafa838969b2e6ead5441c5f37a26359330493cc92b5deb46) $398,968 USDT at 0xd37b…7146; [0x419c…9bfb](https://etherscan.io/tx/0x419cc9e360cb1c62265c67902430441216a403aef522684dacc9cf6ca0209bfb) $302,640 ETH at 0xd37b…7146; [0xb32a…c19c](https://etherscan.io/tx/0xb32af7122ecb5aa5d0331785894cee8e0aa4cafcaeb5588ddacd827912e9c19c) $249,965 USDC at 0xc1d1…a1b5.

#### ETH sent with calldata into a contract that emits nothing (54 transactions, $1,053,852)

What happens: A confirmed-successful call carrying ETH into a contract that is called by many and emits no log: a deposit contract without events (exchange, bridge or staking router). The window's cases are bots paying 13-52 ETH per call to one contract, dozens of times.

Rule: top-level value, calldata, no logs, destination tagged contract_like or router_like. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $14,903, p90 $30,731, max $128,407. Gross priced volume $1,053,852. 6 distinct senders, 6 principals, 3 destinations. By asset of the largest position: ETH ×54 ($1,053,852). Hourly counts from the window start: 7 5 6 5 4 3 5 1 2 1 3 2 1 1 0 1 0 1 1 1 0 1 1 2.

Largest observed asset sender differs from the gas payer in 0 transactions. Transfer-leg directions: {"into_called_contract": 54}.

Top destinations: [0x5cb1…f5fa](https://etherscan.io/address/0x5cb16a393b9b43c590953b51058edab1bde0f5fa) ×31; [0x09c3…d818](https://etherscan.io/address/0x09c30cdcdd971423cb3ba757a47d56c35d06d818) ×22; [0x66a9…a8af](https://etherscan.io/address/0x66a9893cc07d91d95644aedd05d03f95e1dba8af) ×1.

Largest examples: [0xe55a…15d6](https://etherscan.io/tx/0xe55a42ac30a3c82d6f9a730721a5d78b6093fd23a706f18c4ea2af4b06b515d6) $128,407 ETH at 0x5cb1…f5fa; [0x0664…a7b8](https://etherscan.io/tx/0x06648bfc7818307bdbf6ccfcc6088ef45ed78e411e1892e94ded4dcf040ba7b8) $49,180 ETH at 0x5cb1…f5fa; [0x59de…0c7b](https://etherscan.io/tx/0x59de88eb23989c1197bddec88d37d30ca340c418a0f0b5ad90007f14dacd0c7b) $46,141 ETH at 0x5cb1…f5fa; [0x8292…c020](https://etherscan.io/tx/0x8292a37b37560fda03efedde02c1e48fdf4ca70673699e03a95c48fea82ec020) $36,816 ETH at 0x66a9…a8af; [0xdd2d…1a53](https://etherscan.io/tx/0xdd2dd41265f5eaf4b17d4ad71717c1f4109503e147cd2e08c71e38ebacc81a53) $32,766 ETH at 0x4b84…0ccd; [0xe42f…9e5c](https://etherscan.io/tx/0xe42f76a190cf27e16725c48a7f04b3d956ffaf3e352919e35ba0db1701329e5c) $30,731 ETH at 0xb233…c460.

#### deposit into a contract without a record event (19 transactions, $7,158,104)

What happens: Tokens enter the called contract and nothing else happens: vault top-ups by hot wallets, converter deposits, escrow funding.

Rule: only transfer events, every priced leg enters the called contract, no custom event. Method: `custody_flow`. Origin: day run round 4 (Claude): audit corrections and long-tail shapes, qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $50,340, p90 $2,516,607, max $2,997,580. Gross priced volume $8,649,074. 5 distinct senders, 5 principals, 5 destinations. By asset of the largest position: IMPL:0xa1fa…33f8 ×1 ($2,997,580), USDC ×1 ($2,516,607), WETH ×14 ($1,490,969), UNI ×1 ($115,726), DAI ×2 ($37,222). Hourly counts from the window start: 2 2 1 0 0 2 0 1 2 1 1 1 0 0 3 0 1 1 0 0 1 0 0 0.

Largest observed asset sender differs from the gas payer in 6 transactions. Transfer-leg directions: {"into_called_contract": 19}.

Top destinations: [0x2209…321e](https://etherscan.io/address/0x22095bfda9c91d6b0db6df8f807e8f24d610321e) ×8; [0xc4e9…20aa](https://etherscan.io/address/0xc4e9f84297d2e6e92d0d81ee5f1257652ec320aa) ×5; [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) ×4; [0xad95…595f](https://etherscan.io/address/0xad958c4c0c90bf0216e0f5472f074a9ab30f595f) ×1; [0x0000…98a9](https://etherscan.io/address/0x000000000000fea5f4b241f9e77b4d43b76798a9) ×1.

Largest examples: [0xc491…09a3](https://etherscan.io/tx/0xc491813c667a7eb09e02062645e679c7c6a50bbcc73e13be9713bb13640909a3) $2,997,580 IMPL:0xa1fa…33f8 at 0xc59e…74c5; [0xa7d2…8495](https://etherscan.io/tx/0xa7d2c7cd422c0578aaf195b0c71cae5e0dd99dcd7189e68cd60071a13b6f8495) $2,516,607 USDC at 0x94da…a93b; [0x9de6…6e86](https://etherscan.io/tx/0x9de6f7152f1ee18493a2dbabc21dfbdc256655d079da1256b6b897b3d4f16e86) $713,152 WETH at 0xe873…d710; [0x219d…d2c0](https://etherscan.io/tx/0x219d574ce33ae586d915ea4208ae5b838137a98f21fae9995ae31d628809d2c0) $221,904 WETH at 0xe873…d710; [0x8d58…0eab](https://etherscan.io/tx/0x8d587ac32c6c9ca140369d8a3d0b86b00980daa8faa1a0c2cac54b0c7f430eab) $115,726 UNI at 0x94da…a93b; [0x20f5…fe1c](https://etherscan.io/tx/0x20f570addef4cba9d5efb1f08a5155fe62871321a6bc2e9d1a0b3edd20e3fe1c) $92,177 WETH at 0xe873…d710.

#### WETH received by a contract and paid out as ETH (100 transactions, $5,425,558)

What happens: WETH enters the called contract and the contract unwraps it in the same transaction; the ETH then leaves by an internal transfer that receipts do not show. The visible payer is often a liquidity wallet filling a cross-chain or off-chain order; the beneficiary is only visible in the contract's own event.

Rule: a WETH Withdrawal by the called contract or by a contract that emits its own event, at most WETH legs into the called contract, no swap. Method: `custody_flow`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $24,744, p90 $84,880, max $611,409. Gross priced volume $8,952,150. 24 distinct senders, 21 principals, 15 destinations. By asset of the largest position: WETH ×100 ($5,425,558). Hourly counts from the window start: 4 5 6 8 6 1 4 4 6 4 4 3 7 5 3 3 2 1 4 5 6 5 1 3.

Largest observed asset sender differs from the gas payer in 17 transactions. Transfer-leg directions: {"into_called_contract": 70, "third_party_to_third_party": 10}.

Top destinations: [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) ×49; [0xe742…ea88](https://etherscan.io/address/0xe742f9df04a61ac0a6aea0b87d3c3b96ac6eea88) ×14; [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) ×10; [0x0000…6a56](https://etherscan.io/address/0x0000317bec33af037b5fab2028f52d14658f6a56) ×8; [0x8fea…b4f6](https://etherscan.io/address/0x8feab81d36e7576107d5de0758c1b839be31b4f6) ×4.

Largest examples: [0x1f83…ce48](https://etherscan.io/tx/0x1f83c85f9ecf806e959c845929e4498f5123877e23bf9116e40ea22acf5bce48) $611,409 WETH at 0x5567…a075; [0x3d45…9c7a](https://etherscan.io/tx/0x3d4597ec0177c9207163054b0eb8bbbdb5f175786552f71ba3cf2f86cdc39c7a) $436,740 WETH at 0xf820…fd70; [0x11f9…dd1b](https://etherscan.io/tx/0x11f9bbe15ab7f4484079075066dccd29a89b334ac86bce59bf9a3d31ca75dd1b) $367,946 WETH at 0x5567…a075; [0x69fc…6049](https://etherscan.io/tx/0x69fcf1a890db40352ed29507601218be92663f86aea8fe695e1c9451bd326049) $283,603 WETH at 0x2e69…898d; [0xa499…9022](https://etherscan.io/tx/0xa499c0e706f7afa6821f4b782efca8339e5e2479fcd564a7842a062aef349022) $256,533 WETH at 0xf820…fd70; [0x1487…eede](https://etherscan.io/tx/0x1487e05d09ac7645b2b16af064fc0a824b63cdbd44c1fb7e2c74b415b9e1eede) $205,726 WETH at 0xf820…fd70.

#### batched transferFrom sweep into one collector (91 transactions, $25,968,567)

What happens: An operator pulls approved balances from one or several customer addresses into a single collector in one call; nothing else happens and no event beyond the transfers is emitted. Exchange or payment-service deposit consolidation.

Rule: only transfer events, every priced leg is third party to a single recipient, no custom event. Method: `custody_flow`. Origin: day run round 3 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $36,731, p90 $215,736, max $10,237,821. Gross priced volume $25,972,128. 22 distinct senders, 23 principals, 23 destinations. By asset of the largest position: USDC ×45 ($21,842,986), USDT ×39 ($3,495,805), LINK ×4 ($493,293), UNI ×1 ($93,442), AAVE ×1 ($22,801). Hourly counts from the window start: 8 6 11 7 3 4 5 1 5 5 4 1 1 4 5 2 2 4 1 2 0 2 7 1.

Largest observed asset sender differs from the gas payer in 91 transactions. Transfer-leg directions: {"third_party_to_third_party": 405}.

Top destinations: [0x1bbe…7e5d](https://etherscan.io/address/0x1bbe1be1fb532a010762665cfcbed31595367e5d) ×12; [0x6d99…59b8](https://etherscan.io/address/0x6d99ce24079e03ec9436042a727bffe7e39659b8) ×12; [0xfc27…3143](https://etherscan.io/address/0xfc27cd13b432805f47c90a16646d402566bd3143) ×12; [0x7dac…0d38](https://etherscan.io/address/0x7dac2c6a4b0ec57431844b8f78d2d612bb1e0d38) ×8; [0xd1d6…7366](https://etherscan.io/address/0xd1d61c7aabe6e08ba852e226430b73612d1b7366) ×7.

Largest examples: [0xa152…a2e0](https://etherscan.io/tx/0xa1525f9f7f723ea7ecb93091d0dfd0ae10db04a41c08f67aaee214ea41c2a2e0) $10,237,821 USDC at 0xa9d1…3e43; [0x0ae2…aa8f](https://etherscan.io/tx/0x0ae29368e11284724ff7cefeb7e50b5f5d90af329e60741abc782f1afb91aa8f) $6,022,219 USDC at 0xa9d1…3e43; [0x9bfc…5c71](https://etherscan.io/tx/0x9bfceb7bdcec40722f638aa1222101e4e31dc369985f4bb9fb3ccaaa92315c71) $2,788,223 USDC at 0x02c6…a819; [0x9a2e…8e22](https://etherscan.io/tx/0x9a2e33c9740d2adac5b8a50c7f96eeb9fe32ad3a4be171c1d3cc720edc588e22) $800,235 USDT at 0x39f6…2ba3; [0x12e3…b680](https://etherscan.io/tx/0x12e3aa3e846ffd4dd8420eca3cabbac2e3bd7c011f3cf39502d0a44a6058b680) $652,058 USDC at 0xa9d1…3e43; [0xf3be…0ce7](https://etherscan.io/tx/0xf3be24071cfa169e78f42d9e707cc717c79ada089a648c9756cead3f8cfc0ce7) $476,610 USDT at 0x1ce2…fac4.

#### deposit into a contract that records it (481 transactions, $61,078,436)

What happens: Native value or tokens enter the called contract, nothing leaves, and the contract (or a registry it calls) emits its own event: custody hubs, bridge-like escrows, staking or trading-platform treasuries. What the deposit buys is not visible on Ethereum.

Rule: value or tokens enter the called contract only, a custom event is emitted, no swap. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $49,171, p90 $244,996, max $3,889,522. Gross priced volume $61,546,834. 231 distinct senders, 209 principals, 116 destinations. By asset of the largest position: ETH ×302 ($46,322,269), USDC ×96 ($8,457,487), USDT ×52 ($2,984,700), IMPL:0x2323…aa71 ×7 ($2,653,921), IMPL:0x232c…4ee2 ×3 ($168,437). Hourly counts from the window start: 47 29 24 29 30 32 21 34 19 16 12 19 4 5 12 35 10 9 18 17 11 24 10 14.

Largest observed asset sender differs from the gas payer in 58 transactions. Transfer-leg directions: {"into_called_contract": 524, "third_party_to_third_party": 30}.

Top destinations: [0xd90e…f31b](https://etherscan.io/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b) ×71; [0xf5e1…2bcc](https://etherscan.io/address/0xf5e10380213880111522dd0efd3dbb45b9f62bcc) ×51; [0xfa70…a4b9](https://etherscan.io/address/0xfa7093cdd9ee6932b4eb2c9e1cde7ce00b1fa4b9) ×30; [0xb0af…13ea](https://etherscan.io/address/0xb0af00ff84755e9093472814492f32f42a8613ea) ×29; [0xba3c…adec](https://etherscan.io/address/0xba3cb449bd2b4adddbc894d8697f5170800eadec) ×27.

Largest examples: [0xe644…5363](https://etherscan.io/tx/0xe6442f4f234f707ce104cdc59d248dcf60325607ee99f78c60964928f2755363) $3,889,522 ETH at 0xceb6…66ea; [0x42ac…087c](https://etherscan.io/tx/0x42ac7fb7ee69b81284d313aa0463a813f3ae3c35ad8ea9bf7b8785cb1354087c) $3,682,023 ETH at 0xebe2…9541; [0xc3db…651c](https://etherscan.io/tx/0xc3dbcf5ce37f1c1a059ad034dd0118a9e0851aa7fa0750445f546ccea017651c) $2,088,634 ETH at 0x5970…8fd2; [0x5f0c…d942](https://etherscan.io/tx/0x5f0cd52d9f4697c55e5b61a06fa91d0a166c90e4fecb5c6b124556d23c6dd942) $2,010,754 USDC at 0x87e3…9b93; [0x7124…6a3c](https://etherscan.io/tx/0x71245feeae9f881ccbeefe6c79b7b0175174a93602e86b499ff107428d816a3c) $2,009,647 ETH at 0xe1db…905f; [0x3f92…f62d](https://etherscan.io/tx/0x3f924d4f17d2d11b87db76f71cba38c73e325ac71f5d51421d8e744d49c5f62d) $1,952,326 IMPL:0x2323…aa71 at 0xd166…2df7.

#### contract pays its own tokens to the calling address (133 transactions, $22,833,903)

What happens: The called contract sends tokens it holds to the transaction sender: a hot wallet replenishing itself from a vault, or an owner draining a contract.

Rule: every priced leg goes from the called contract to the transaction sender, only transfer events. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $32,644, p90 $247,478, max $6,074,258. Gross priced volume $22,856,799. 47 distinct senders, 47 principals, 45 destinations. By asset of the largest position: USDC ×31 ($9,047,623), USDT ×39 ($7,861,678), wstETH ×4 ($1,381,483), IMPL:0x232c…4ee2 ×22 ($1,301,731), IMPL:0x2323…aa71 ×1 ($1,050,775). Hourly counts from the window start: 20 9 8 6 4 6 5 0 4 5 4 4 5 8 2 5 7 6 2 5 1 4 5 8.

Largest observed asset sender differs from the gas payer in 133 transactions. Transfer-leg directions: {"from_called_contract": 376}.

Top destinations: [0x40ff…2960](https://etherscan.io/address/0x40ffe85a28dc9993541449464d7529a922142960) ×36; [0x3b4d…5ca7](https://etherscan.io/address/0x3b4d794a66304f130a4db8f2551b0070dfcf5ca7) ×26; [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3) ×9; [0x3ee1…a585](https://etherscan.io/address/0x3ee18b2214aff97000d974cf647e7c347e8fa585) ×7; [0x9bf5…3237](https://etherscan.io/address/0x9bf51f33955ec70f87c4b5c49441815589043237) ×3.

Largest examples: [0x6250…49fd](https://etherscan.io/tx/0x6250038d6aef234d9ce040caeafd5fb16c6999864b2798746b24b0ae02ed49fd) $6,074,258 USDT at 0x4ea1…f4d6; [0x92ac…435d](https://etherscan.io/tx/0x92aca2ad9cf5203a68dd301233a5d844757e2709dee3984362ab8c91f195435d) $3,129,480 USDC at 0x4ea1…f4d6; [0xb763…0931](https://etherscan.io/tx/0xb76323cea7a1ee8dbdf4f355f7d984a8875a2ef7b729b1f32c89c89ed1660931) $1,999,719 USDC at 0x87cf…c01d; [0xc3e3…f1cf](https://etherscan.io/tx/0xc3e312df575532b070bc4b1a01cab6e20f330f41916e1ad84d604ea4ea3bf1cf) $1,199,831 USDC at 0xcce6…a2df; [0x4a26…00b3](https://etherscan.io/tx/0x4a269228f567abe5cdfe5c0f8c8bccd4d75e79736c5fdfd277ac842be35000b3) $1,050,775 IMPL:0x2323…aa71 at 0xd166…2df7; [0x99f6…4354](https://etherscan.io/tx/0x99f6ebe01af27a8f093c921cb6a03863440f52e7f7b6292ebede9d4ef0de4354) $819,756 USDC at 0xf70d…dbef.

#### contract-held tokens paid out by an operator call (1,262 transactions, $288,628,470)

What happens: An operator EOA calls a contract that pays tokens it holds to other addresses, usually with a per-payment record: withdrawal processors, treasury payouts, settlement of cross-chain orders. The recipient profile says whether the money reaches a fresh address (customer) or another hub.

Rule: every priced leg leaves the called contract to addresses other than the sender, only transfer events. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $41,325, p90 $369,023, max $21,506,975. Gross priced volume $289,734,046. 188 distinct senders, 297 principals, 295 destinations. By asset of the largest position: USDC ×512 ($140,921,015), USDT ×522 ($67,806,612), RLUSD ×11 ($37,779,069), PYUSD ×6 ($30,402,202), LINK ×19 ($1,744,216). Hourly counts from the window start: 101 124 102 103 87 77 72 75 50 33 34 36 21 16 20 34 26 25 36 54 32 23 34 47.

Largest observed asset sender differs from the gas payer in 1262 transactions. Transfer-leg directions: {"from_called_contract": 1697}.

Top destinations: [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) ×98; [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) ×90; [0xf5e1…2bcc](https://etherscan.io/address/0xf5e10380213880111522dd0efd3dbb45b9f62bcc) ×60; [0xfd03…b7f0](https://etherscan.io/address/0xfd03abcadaf3f930fa4e37eb2f6ea3a44a41b7f0) ×48; [0xbee3…a000](https://etherscan.io/address/0xbee3211ab312a8d065c4fef0247448e17a8da000) ×39.

Largest examples: [0x75a5…13cc](https://etherscan.io/tx/0x75a585f7f6bebbe2e439753d9467218da83a9f6f73a622643682876fb9cb13cc) $21,506,975 USDC at 0xb6c9…3d85; [0x51c6…3c10](https://etherscan.io/tx/0x51c61ca6bdecec9d9f76a639ee9ded567ca59ef948a2a4d1b549ae9f8c2a3c10) $20,000,000 RLUSD at 0xfbca…0bb6; [0x5e1e…8a4f](https://etherscan.io/tx/0x5e1ed760aefc00f756f8b4ea57b5869df0830cd230ff5782d4af546b3a618a4f) $17,632,134 USDC at 0x8454…9181; [0x7330…8a8f](https://etherscan.io/tx/0x73301cd220325e3219a70d298d523c5fffa5c7557f5fd98d5213e3f50c7c8a8f) $15,000,000 PYUSD at 0xcf61…d81a; [0x13f2…f36e](https://etherscan.io/tx/0x13f297e3d9f1a95ef82192d4652b77a382506f644f7d894f7eadd7a340eef36e) $13,000,000 PYUSD at 0xcf61…d81a; [0x3a28…4f23](https://etherscan.io/tx/0x3a2898ed7eb7d742fd7a47aa3fa0402cfb55adecff7877ae4a767f963ea74f23) $7,000,000 RLUSD at 0x9cbd…5329.

#### operator-mediated transfer with custom events (290 transactions, $53,807,058)

What happens: Tokens move between third parties, or into and out of a contract, in a transfer-only transaction that also emits custom events the registry does not name. The residual mechanical shape of custody and settlement infrastructure.

Rule: only transfer events plus custom events; priced ERC-20 legs present; no rule above matched. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $34,848, p90 $165,007, max $14,524,635. Gross priced volume $115,170,582. 149 distinct senders, 142 principals, 50 destinations. By asset of the largest position: USDC ×127 ($37,183,853), IMPL:0x232c…4ee2 ×6 ($4,989,868), USDT ×59 ($3,441,224), PYUSD ×3 ($3,351,342), IMPL:0xe343…491d ×15 ($1,701,707). Hourly counts from the window start: 27 27 23 17 17 17 15 12 8 9 10 9 9 5 8 6 6 11 7 10 19 4 11 3.

Largest observed asset sender differs from the gas payer in 109 transactions. Transfer-leg directions: {"from_called_contract": 186, "into_called_contract": 183, "third_party_to_third_party": 479}.

Top destinations: [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) ×33; [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) ×27; [0xc0c3…45a0](https://etherscan.io/address/0xc0c3bc532690af8922a2f260c6e1deb6cfab45a0) ×25; [0x5523…227e](https://etherscan.io/address/0x5523985926aa12ba58dc5ad00ddca99678d7227e) ×15; [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) ×14.

Largest examples: [0xfe97…50e3](https://etherscan.io/tx/0xfe975916d22888f5c98158b8446c2dd54568c2a4bf449d046e60e0be3c4250e3) $14,524,635 USDC at 0xa42f…126b; [0xf6aa…2728](https://etherscan.io/tx/0xf6aa4f44559a659071dd6a86b795fe457fc129cf2db0760755acc2d785ea2728) $14,198,002 USDC at 0xc39a…b8b9; [0xd537…4af8](https://etherscan.io/tx/0xd537e16d88a757f4137d021a170228c06c4ae3582684fc58577fe9fe92aa4af8) $2,292,434 PYUSD at 0x11af…0943; [0x06e3…a909](https://etherscan.io/tx/0x06e34acce9d9a5a0567736f602952dc5ff9cc957eaf2600bc34f5e3463eca909) $1,904,381 IMPL:0x232c…4ee2 at 0xb918…466c; [0x8307…0703](https://etherscan.io/tx/0x830790ff046cc412c06fd268d74b1a5871ec937588b228979be428d814ab0703) $1,523,506 IMPL:0x232c…4ee2 at 0x522f…355a; [0xf10f…5ed1](https://etherscan.io/tx/0xf10f4cf04b7b8f2fe1840390bf3cccf21b8389443a8e6250ac10e4470da35ed1) $1,333,069 IMPL:0x232c…4ee2 at 0x3c1d…5a20.

### payments

#### payment routed through a contract that splits off a fee (80 transactions, $10,647,089)

What happens: A payer's tokens enter a router and leave it in the same transaction to a merchant and one or more fee takers; the router keeps nothing and records the invoice in its own events. The fee is the smallest share, under a tenth of the amount.

Rule: one asset enters the called contract and leaves it to two or more recipients within 1%; the smallest share is at most 10%. Method: `fee_split`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $49,464, p90 $499,820, max $999,692. Gross priced volume $25,304,944. 29 distinct senders, 65 principals, 7 destinations. By asset of the largest position: USDT ×51 ($9,266,188), USDC ×16 ($700,081), sUSDe ×5 ($367,904), USDe ×2 ($127,553), WETH ×4 ($100,244). Hourly counts from the window start: 0 3 5 5 3 4 2 2 0 0 0 1 3 3 3 4 2 0 3 2 12 3 12 8.

Fee share: median 73.93 bps, p90 143.87 bps over 80 routed payments; 60 distinct payers (6 paid three or more times). Fee takers: [0x8443…ff9a](https://etherscan.io/address/0x8443e89848ef39017184c42171388674c551ff9a) ×37; [0x0070…10cc](https://etherscan.io/address/0x00700052c0608f670705380a4900e0a8080010cc) ×13; [0x7b0e…1490](https://etherscan.io/address/0x7b0ef8f2d93211f2e62f3e96f5b088dd7efd1490) ×9; [0xcc01…3f85](https://etherscan.io/address/0xcc01ef33f793ff0a8da26d19b2c4428f62753f85) ×5. Main recipients: [0xc7b9…bd2d](https://etherscan.io/address/0xc7b9a5d1f94f1815a0945baa63aefa6ce391bd2d) ×11; [0xcf7c…7c9c](https://etherscan.io/address/0xcf7c5deadb997b2a82f4c2d11ed5d3ab22257c9c) ×8; [0x8de0…8de9](https://etherscan.io/address/0x8de0d3ed331ce1f29c8df04726d424a015f38de9) ×5; [0xc46a…b6e7](https://etherscan.io/address/0xc46a0f5124bfe05c61216a10f32663b76cccb6e7) ×4.

Largest observed asset sender differs from the gas payer in 65 transactions. Transfer-leg directions: {"from_called_contract": 166, "into_called_contract": 93, "third_party_to_third_party": 94}.

Top destinations: [0x8d04…184b](https://etherscan.io/address/0x8d04cc7e86e687854eb41d9d43512b655b93184b) ×37; [0x6a00…1068](https://etherscan.io/address/0x6a000f20005980200259b80c5102003040001068) ×16; [0xb6a0…922d](https://etherscan.io/address/0xb6a043999757019c54583e04b4ad4fd0e181922d) ×9; [0x6946…a22d](https://etherscan.io/address/0x69460570c93f9de5e2edbc3052bf10125f0ca22d) ×7; [0xcb01…3d45](https://etherscan.io/address/0xcb0151ac9479a6a0261622baa63ae843c9793d45) ×5.

Largest examples: [0x3122…d559](https://etherscan.io/tx/0x3122063609d522de5426d399605a0f539396400b73ebe75e2c30fcf027ebd559) $999,692 USDT at 0xf121…d83a; [0x4b9e…6d7c](https://etherscan.io/tx/0x4b9e5475c779734a8b738d26c6a23efa7d54dbeada594ae720fd86deb0546d7c) $999,692 USDT at 0xee2d…9604; [0xc7f5…caf5](https://etherscan.io/tx/0xc7f516cce8c5538d8ecdc0890ac9b279ca20305e9875a63dd63f9041c464caf5) $999,692 USDT at 0xb174…2820; [0x9957…cee5](https://etherscan.io/tx/0x995756a2efa02e65cbe530629bccacc463145210a42662dd56cca871dc45cee5) $999,692 USDT at 0xbc21…c5b8; [0xdaa9…2642](https://etherscan.io/tx/0xdaa98762bad62d3eb60529c2c30b4ddfad06a21cf7565f2760c46f939e432642) $499,820 USDT at 0xf94b…d1aa; [0xb498…8808](https://etherscan.io/tx/0xb498636326e00b07645f30dda0b2472de9e15379a05052e58300ac7881e28808) $499,820 USDT at 0xa204…13cc.

#### relayed transfer of approved funds recorded by the contract (360 transactions, $64,985,221)

What happens: An operator moves tokens from payers to recipients that are all third parties, and the called contract emits one record (often a 32-byte reference) per transfer. Neither the gas payer nor the contract holds the funds: a payment rail or settlement service executing instructions on approved balances.

Rule: only transfer events plus custom events from the called contract; every priced leg is third party to third party. Method: `custody_flow`. Origin: day run round 2 (Claude), qual_notes.md of research/2026-09-05/amount_outliers_eth_day.

Largest position change: median $35,339, p90 $216,912, max $15,000,000. Gross priced volume $77,555,787. 114 distinct senders, 131 principals, 48 destinations. By asset of the largest position: USDC ×205 ($26,826,167), PYUSD ×9 ($26,060,589), USDT ×42 ($3,739,302), IMPL:0xe343…491d ×23 ($2,274,484), wstETH ×8 ($2,033,804). Hourly counts from the window start: 25 29 25 25 20 24 16 14 14 7 9 11 9 8 7 4 15 11 10 14 19 13 13 18.

Largest observed asset sender differs from the gas payer in 359 transactions. Transfer-leg directions: {"into_called_contract": 7, "third_party_to_third_party": 651}.

Top destinations: [0xec00…a6df](https://etherscan.io/address/0xec000064576f9c95a8623bc0eff3db6d296ea6df) ×56; [0x43de…98aa](https://etherscan.io/address/0x43de2d77bf8027e25dbd179b491e8d64f38398aa) ×52; [0x9ccc…b294](https://etherscan.io/address/0x9ccc2f3ecde026230e11a5c8799ac7524f2bb294) ×42; [0x6661…887a](https://etherscan.io/address/0x666156ab52bb9984f5c3985726f048dd4a73887a) ×25; [0x26d3…73c5](https://etherscan.io/address/0x26d3681dfc9e4c8c79cfbf461adec8a21d5d73c5) ×20.

Largest examples: [0xa808…ce10](https://etherscan.io/tx/0xa8086f9829e39b42b5c8f4a0adc2dcb574669c61dec6b98b5028016d4592ce10) $15,000,000 PYUSD at 0xc5e0…9720; [0xd686…e1cf](https://etherscan.io/tx/0xd686c0949199c6537f582caf03401b975eb3b27dcf40508a7c6ccdaf340ce1cf) $5,965,200 PYUSD at 0xc5e0…9720; [0xa66e…29ae](https://etherscan.io/tx/0xa66e52e23cf4683d10ad815a054d4e6ca338176481cd71be7d3fda08ee5729ae) $5,000,000 PYUSD at 0xc5e0…9720; [0x5623…79f4](https://etherscan.io/tx/0x56235fb1b9fd7482d16034c4357af0a5ff6376e9ed2cfc6dd2c966b84dc379f4) $2,242,291 USDC at 0xe3a2…53c1; [0x32cc…4462](https://etherscan.io/tx/0x32cc75fa335c9b3475786a8edd9660add83747403112bf5382c5beab32264462) $2,242,190 USDC at 0xbd22…855e; [0xee25…f41c](https://etherscan.io/tx/0xee259f3372a857b09e4e57b3e89ad414bcf086b9adfa887517b05ee53693f41c) $2,242,190 USDC at 0xe3a2…53c1.

## Residue: what no rule matched, and what the LLM found

81 transactions ($24,559,594) in 50 clusters keyed by destination, selector and event shape. Largest clusters:

| Cluster | Destination | Selector | Shape | Txs | Senders | Sum | Assets | Representative |
|---|---|---|---|---:|---:|---:|---|---|
| 5c60c2f8be | [0xceda…366d](https://etherscan.io/address/0xceda2d856238aa0d12f6329de20b9115f07c366d) | `0x71dc0cf9` | transfers-only | 9 | 1 | $354,040 | USDe ×9 | [0xde01…2fcf](https://etherscan.io/tx/0xde017d5628fc4fb92055d6242e12c2d510f73143b8a607131cd3da79e6f12fcf) |
| 2715da933b | [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3) | `0xbcaeadb6` | WETHDeposit; unknown=0x576dcb24693ce268755564d0b539845212a2e052e80b6a958db4920b0 | 6 | 1 | $88,405 | WETH ×6 | [0xf8da…a1c1](https://etherscan.io/tx/0xf8da96d0de077e2f483c86fb3e9e2bdd3b500cab4b3daa8e596f75ec40d5a1c1) |
| d79f2e2e18 | [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) | `0x3ce33bff` | SafeReceived; unknown=0x4e96fb90a89341a56db7ad2bbf04c715bbf20be6a9a9e764671f718c | 5 | 4 | $195,065 | ETH ×5 | [0x06b4…7c02](https://etherscan.io/tx/0x06b4047508a4274305b7bc26e5270fb2a0c858dc5a2bd47ce1a898b974ae7c02) |
| a6c521a9a2 | [0x9188…96e5](https://etherscan.io/address/0x9188db2825bd0ad76a2ba3aba21274428dc696e5) | `0x5bebe4ee` | transfers-only | 4 | 1 | $247,956 | USDC ×2, USDT ×2 | [0xcbb9…856d](https://etherscan.io/tx/0xcbb98d3f046c46b84e263402077b5a2ca6adec5bea276649f3791d8a7d0a856d) |
| a58db0475e | [0x4c21…54cf](https://etherscan.io/address/0x4c21b7577c8fe8b0b0669165ee7c8f67fa1454cf) | `0x866f1f02` | AaveWithdraw | 3 | 1 | $7,206,327 | USDC ×3 | [0x543b…807e](https://etherscan.io/tx/0x543b8c6b6c919ca86889e455114d6ebd87e2c8549cfca7f6cbd4829db0cf807e) |
| e804966209 | [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) | `0x56688700` | Sync3 | 3 | 1 | $9,998,593 | IMPL:0x0000…012a ×3 | [0x8504…fd9b](https://etherscan.io/tx/0x8504dbcc6e925140f38876dc69ba3aef130426440084c8bdc31abd540789fd9b) |
| 46bdda75a5 | [0xbb60…8df7](https://etherscan.io/address/0xbb605dc51cac7eca64001651ac71c2c002308df7) | `0x` | WETHDeposit | 2 | 1 | $70,420 | ETH ×2 | [0x43a0…3ff3](https://etherscan.io/tx/0x43a0c9031eb1883ff4196ce58d701cb357e7eaa57b49aa73a70ae0d774f03ff3) |
| 9db54c43ad | [0xf2e6…da6b](https://etherscan.io/address/0xf2e6ed63bb255e51b64337c67fb4898aa979da6b) | `0xc4b06ece` | WETHDeposit; unknown=0x469059a9fd182ad3741bdd67b925e15056d35262609ea83393db7e8fb | 2 | 2 | $48,860 | WETH ×2 | [0x944e…0df4](https://etherscan.io/tx/0x944e3e94dca322dc9c9bb1feedba7fc96c80b0fc4f7b40bb752dee2a3a050df4) |
| 9e7aa7869f | [0xbbd8…a4f4](https://etherscan.io/address/0xbbd8d82fea76afc62984498929a1db52cffea4f4) | `0x` | WETHDeposit | 2 | 1 | $132,078 | ETH ×2 | [0x604e…5877](https://etherscan.io/tx/0x604e9590419b8e151e259e948bee5512777619e218d48d0ffe44a0429d695877) |
| ae0ca90295 | [0xa60b…c248](https://etherscan.io/address/0xa60b5146e44ff755e32bd51532842ceb41d0c248) | `0x81c197ed` | transfers-only | 2 | 2 | $262,744 | LINK ×2 | [0x2c27…6145](https://etherscan.io/tx/0x2c271b08d702d1fb098eb0438adca4e65137e7c02c98b0fa0e5e63113b426145) |
| da503b5f56 | [0x5149…86ca](https://etherscan.io/address/0x514910771af9ca656af840dff83e8264ecf986ca) | `0x4000aea0` | ERC20TransferWithData,GDeposit_auu | 2 | 2 | $66,858 | LINK ×2 | [0x2634…1d6b](https://etherscan.io/tx/0x2634638463e844904e31bd14a4bf1d2d6888d82264ece221d81bba97f5be1d6b) |
| f4977392bf | [0x8cc5…9027](https://etherscan.io/address/0x8cc5c24a1666d3214340050315b82b2b6b0d9027) | `0x0f129fd7` | WETHDeposit; unknown=0x6771236b150af063b0a9c8523b694e47d0a3a8511cfe7fbbdbf65484b | 2 | 2 | $32,255 | WETH ×2 | [0x7278…da6f](https://etherscan.io/tx/0x72785634a1c4f2a16f35cd8cac859f1beb093b9c4d1118ea4819c475a1e1da6f) |
| f6ab6c4a03 | [0x7799…9195](https://etherscan.io/address/0x7799905deebca738038984ce341fb1b226769195) | `0x` | SafeReceived | 2 | 2 | $181,911 | ETH ×2 | [0x097f…6df2](https://etherscan.io/tx/0x097f74cda0a7f98689f0d83445beff33b106407f794d8a57b8a12fe8b4cf6df2) |
| 06b208c38a | [0xddc7…60ea](https://etherscan.io/address/0xddc796a66e8b83d0bccd97df33a6ccfba8fd60ea) | `0xefb15bae` | ERC20TransferWithData; unknown=0x16aadfd997cc8ab0f2890a6c7fe1ea76bdb61f8c74cc386 | 1 | 1 | $26,559 | LINK ×1 | [0x6390…3354](https://etherscan.io/tx/0x63909e2b130332a1cc60b303ce528d15aa7ff41d8deeafaae339d1e70e9e3354) |
| 07d08b3497 | [0xf127…edc8](https://etherscan.io/address/0xf1272dcb5172b9cf2b39b223ab394243d608edc8) | `0x` | SafeReceived | 1 | 1 | $24,505 | ETH ×1 | [0x3f09…2b60](https://etherscan.io/tx/0x3f098987899f867c476ef41045243449b469c846ef3892e7ff0239f3f5122b60) |
| 1c28f1c23a | [0x9a3e…528d](https://etherscan.io/address/0x9a3ed7007809cfd666999e439076b4ce4120528d) | `0xb1dc65a4` | ChainlinkTransmitted; unknown=0x2717ead6b9200dd235aad468c9809ea400fe33ac69b5bfaa | 1 | 1 | $10,567 | USDC ×1 | [0x39d2…c148](https://etherscan.io/tx/0x39d280cbe69e01cfb1cabebbff1987e916c823da58cf2f79fccbff000ad4c148) |
| 1fb4e4cdf2 | [0xbbd6…c7af](https://etherscan.io/address/0xbbd6e0ac7d5ec6e2d0c871ea7a79f888b4dcc7af) | `0x` | WETHDeposit | 1 | 1 | $32,635 | ETH ×1 | [0x3eca…89e6](https://etherscan.io/tx/0x3eca375a5109f662d66f10e221cafc325103e29bd2c4ad0d927d581a98f289e6) |
| 225cd20b45 | [0xe6e1…a2f8](https://etherscan.io/address/0xe6e1247eef260ff75d99dec17ac0fa8fb31aa2f8) | `0x` | SafeReceived | 1 | 1 | $13,462 | ETH ×1 | [0x4015…4ecf](https://etherscan.io/tx/0x40152fac441dbee060196ba37edb46e88e90e0ea1acdb5f13d4dfaa68f384ecf) |
| 2762cf0b5a | [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) | `0x3ce33bff` | SafeReceived; unknown=0x012c155f3836c4edb9222305b909a109f9efa46288efffe40a0e66da | 1 | 1 | $22,077 | ETH ×1 | [0xfe54…2681](https://etherscan.io/tx/0xfe549c60027e4ce749d4a024c7fd6106558e7d86f38f5dc72b16f454aeb32681) |
| 3fcb5efbf9 | [0xa428…fb6a](https://etherscan.io/address/0xa428723ee8ffd87088c36121d72100b43f11fb6a) | `0xaf1beac3` | MorphoAccrueInterest,MorphoWithdrawCollateral | 1 | 1 | $140,556 | IMPL:0x35d8…9bc0 ×1 | [0x79ab…74b5](https://etherscan.io/tx/0x79abe41140e4252dbd6b56aab6ded4e07ba3098758f6172496a03dbd454f74b5) |
| 4f556fce5d | [0x12e5…155d](https://etherscan.io/address/0x12e5179df245e1a3cdd41c024a4174b3b395155d) | `0x` | SafeReceived | 1 | 1 | $99,026 | ETH ×1 | [0xd90a…606c](https://etherscan.io/tx/0xd90ae22832d1b4946ad14248c692ab976e456ad7984b902a8a2aaf403cef606c) |
| 51f3dbbde7 | [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) | `0x1e10eeaf` | Sync3; unknown=0xdef014699163b7bead46a730f8a9a0eea8d6db419a3caffda46f99d65546d90 | 1 | 1 | $3,999,437 | USDC ×1 | [0x3de4…dd8d](https://etherscan.io/tx/0x3de4c0e52ca82b938ed0437b32849f269ec176e814a7a8d32c60ca1ecddcdd8d) |
| 5e58b1c83d | [0xbb6d…782a](https://etherscan.io/address/0xbb6d0a1b1d267f1fea605ed502ce938cf185782a) | `0x` | WETHDeposit | 1 | 1 | $76,773 | ETH ×1 | [0xfc2e…95f8](https://etherscan.io/tx/0xfc2ee3f8010052b388dab66181e06ed5d8fdc3c68a10e9bba549110f5f6295f8) |
| 6637357c46 | [0xbb58…1e1c](https://etherscan.io/address/0xbb584544fcad145f65c9ee671a527ba560021e1c) | `0x` | WETHDeposit | 1 | 1 | $48,999 | ETH ×1 | [0xc117…d795](https://etherscan.io/tx/0xc11709729f4c3897200bd562ec604e6ee5d0772d7be215c9cc0c70cd30bbd795) |
| 69397339db | [0xf82e…4263](https://etherscan.io/address/0xf82ef4080a53b71093f9c470676fc80e2adc4263) | `0xa6b41ec4` | MorphoAccrueInterest; unknown=0x003d5fea7147843a952736a57f88f9e5565759fb750f34a8 | 1 | 1 | $230,529 | USDT ×1 | [0xae8f…1a7e](https://etherscan.io/tx/0xae8feb731ed5395675a937a731d023b48d75c9b5d99157d71cb97cee85371a7e) |

### R1. [0x3de4…dd8d](https://etherscan.io/tx/0x3de4c0e52ca82b938ed0437b32849f269ec176e814a7a8d32c60ca1ecddcdd8d): 4,000,000.00 USDC withdrawn from the AUSD/USDC converter 0xa19d9d64… by 0xf3c1cc8e…, with a Sync(uint256,uint256) reserve update and a withdraw record

Selected for residue cluster USD #3. Cluster 51f3dbbde7: 1 transactions from 1 senders, $3,999,437, shape Sync3; unknown=0xdef014699163b7bead46a730f8a9a0eea8d6db419a3caffda46f99d65546d90a. Block 25,904,465 at 2026-09-04T14:10:35+00:00, index 146/247, type 0x2, success. From [0xfc86…3085](https://etherscan.io/address/0xfc86ef5407c1823c64ffab81dc15e2d3085e3085) (an EOA; window profile: no tags, 1 sent to 1 destinations, nonce 78 to 78) to [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) (a contract of 1,171 bytes; never_sends, pool, called 11 times in the window). Selector `0x1e10eeaf`, calldata 68 bytes, value 0 ETH, 3 logs, tip 0.429779808 gwei. Largest position change $3,999,437 (USDC at [0xf3c1…d0b0](https://etherscan.io/address/0xf3c1cc8eef9f4a38cd7a8de03c51ea2cf09ed0b0)); gross $3,999,437; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) nets USDC -$3,999,437 against [0xf3c1…d0b0](https://etherscan.io/address/0xf3c1cc8eef9f4a38cd7a8de03c51ea2cf09ed0b0) (an EOA; no tags).

Net flows: [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) -4,000,000.00 USDC (-$3,999,437); [0xf3c1…d0b0](https://etherscan.io/address/0xf3c1cc8eef9f4a38cd7a8de03c51ea2cf09ed0b0) +4,000,000.00 USDC ($3,999,437).

Event families: ERC20_Transfer_shape ×1, Sync3 ×1, unknown ×1. Unknown topics: [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) 0xdef014699163b7be… ×1.

Interpretation (LLM, confidence medium): 

Unverified: as 0x8504dbcc….

Proposed type: `par conversion keyed on the converter (feedback 1)`

### R2. [0x8504…fd9b](https://etherscan.io/tx/0x8504dbcc6e925140f38876dc69ba3aef130426440084c8bdc31abd540789fd9b): 4,000,000.00 AUSD deposited into converter 0xa19d9d64…, which also paid 4,000,000.00 USDC to another user (0x3de4c0e5…): a two-asset par facility

Selected for residue cluster size #6, residue cluster USD #1. Cluster e804966209: 3 transactions from 1 senders, $9,998,593, shape Sync3, other examples [0xecbe…1892](https://etherscan.io/tx/0xecbe363a2878aebaabc01404fa6ca51d0ee6e629604859d922c0c5369ada1892) [0x5bf1…4e23](https://etherscan.io/tx/0x5bf1b651b367aae900b3bdf53c56975bf0f857b7a6354085e9c8c500257a4e23). Block 25,904,477 at 2026-09-04T14:12:59+00:00, index 344/537, type 0x2, success. From [0x080f…9cf5](https://etherscan.io/address/0x080f646713bce0da8c08770d407818de47639cf5) (an EOA; window profile: no tags, 7 sent to 2 destinations, nonce 239 to 245) to [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) (a contract of 1,171 bytes; never_sends, pool, called 11 times in the window). Selector `0x56688700`, calldata 68 bytes, value 0 ETH, 2 logs, tip 0.00105 gwei. Largest position change $3,999,437 (IMPL:0x0000…012a at [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9)); gross $3,999,437; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x080f…9cf5](https://etherscan.io/address/0x080f646713bce0da8c08770d407818de47639cf5) nets IMPL:0x0000…012a -$3,999,437 against [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) (a contract of 1,171 bytes; never_sends, pool).

Net flows: [0x080f…9cf5](https://etherscan.io/address/0x080f646713bce0da8c08770d407818de47639cf5) -0.000004 IMPL:0x0000…012a (-$3,999,437); [0xa19d…57a9](https://etherscan.io/address/0xa19d9d64ece53a3a85e2c30725d31d09bec157a9) +0.000004 IMPL:0x0000…012a ($3,999,437).

Event families: ERC20_Transfer_shape ×1, Sync3 ×1.

Interpretation (LLM, confidence medium): Three deposits ($10.0M) and one withdrawal ($4.0M) in the day; the contract is 1,171 bytes.

Unverified: the operator of the converter; AUSD's identity comes from resolve (symbol AUSD, 6 decimals).

Proposed type: `a par-conversion type keyed on the converter, once its Sync(uint256,uint256) and withdraw events are registered`

### R3. [0x2c27…6145](https://etherscan.io/tx/0x2c271b08d702d1fb098eb0438adca4e65137e7c02c98b0fa0e5e63113b426145): 20,969.96 LINK ($248,522) withdrawn from 0xa60b5146… to the caller with a Withdraw(address,uint256) event

Selected for residue cluster size #10, residue cluster USD #6. Cluster ae0ca90295: 2 transactions from 2 senders, $262,744, shape transfers-only, other examples [0xb5b2…db3d](https://etherscan.io/tx/0xb5b2d8ad8ded6ce3cd6d915f07734c3202725f9646af9cfda20e787fcbd8db3d). Block 25,904,523 at 2026-09-04T14:22:23+00:00, index 198/570, type 0x0, success. From [0x4a47…a601](https://etherscan.io/address/0x4a470942dd7a44c6574666f8bda47ce33c19a601) (an EOA; window profile: no tags, 2 sent to 2 destinations, nonce 2,407 to 2,408) to [0xa60b…c248](https://etherscan.io/address/0xa60b5146e44ff755e32bd51532842ceb41d0c248) (a contract of 170 bytes; never_sends, called 3 times in the window). Selector `0x81c197ed`, calldata 260 bytes, value 0 ETH, 2 logs, tip 0.197626368 gwei. Largest position change $248,522 (LINK at [0xa60b…c248](https://etherscan.io/address/0xa60b5146e44ff755e32bd51532842ceb41d0c248)); gross $248,522; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x4a47…a601](https://etherscan.io/address/0x4a470942dd7a44c6574666f8bda47ce33c19a601) nets LINK $248,522 against [0xa60b…c248](https://etherscan.io/address/0xa60b5146e44ff755e32bd51532842ceb41d0c248) (a contract of 170 bytes; never_sends).

Net flows: [0x4a47…a601](https://etherscan.io/address/0x4a470942dd7a44c6574666f8bda47ce33c19a601) +20,969.96 LINK ($248,522); [0xa60b…c248](https://etherscan.io/address/0xa60b5146e44ff755e32bd51532842ceb41d0c248) -20,969.96 LINK (-$248,522).

Event families: ERC20_Transfer_shape ×1, WithdrawAU ×1.

Interpretation (LLM, confidence medium): 

Unverified: the contract (a staking or vault contract for LINK).

Proposed type: `custody_withdrawal_to_operator once the two-argument Withdraw family is allowed in transfer-only rules (feedback 9)`

### R4. [0x7278…da6f](https://etherscan.io/tx/0x72785634a1c4f2a16f35cd8cac859f1beb093b9c4d1118ea4819c475a1e1da6f): not yet annotated

Selected for residue cluster size #12. Cluster f4977392bf: 2 transactions from 2 senders, $32,255, shape WETHDeposit; unknown=0x6771236b150af063b0a9c8523b694e47d0a3a8511cfe7fbbdbf65484bc0d8254, other examples [0x9795…79b0](https://etherscan.io/tx/0x97956e8634ce3995a0263537cc78dc49a1c1ab76102fdab0c34ec489c2c979b0). Block 25,904,555 at 2026-09-04T14:28:47+00:00, index 218/423, type 0x2, success. From [0x7c5f…3727](https://etherscan.io/address/0x7c5fcb01f18c3acff94a4a86deb79eff870b3727) (an EOA; window profile: bot_sender, 47 sent to 2 destinations, nonce 12,393 to 12,439) to [0x8cc5…9027](https://etherscan.io/address/0x8cc5c24a1666d3214340050315b82b2b6b0d9027) (a contract of 18,056 bytes; contract_like, never_sends, router_like, called 1787 times in the window). Selector `0x0f129fd7`, calldata 100 bytes, value 0 ETH, 2 logs, tip 0.058470324 gwei. Largest position change $18,955 (WETH at [0x8cc5…9027](https://etherscan.io/address/0x8cc5c24a1666d3214340050315b82b2b6b0d9027)); gross $18,955; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x8cc5…9027](https://etherscan.io/address/0x8cc5c24a1666d3214340050315b82b2b6b0d9027) nets WETH $18,955.

Net flows: [0x8cc5…9027](https://etherscan.io/address/0x8cc5c24a1666d3214340050315b82b2b6b0d9027) +7.766430 WETH ($18,955).

Event families: WETHDeposit ×1, unknown ×1. Unknown topics: [0x8cc5…9027](https://etherscan.io/address/0x8cc5c24a1666d3214340050315b82b2b6b0d9027) 0x6771236b150af063… ×1.

_No qualitative note yet for this transaction._

### R5. [0x604e…5877](https://etherscan.io/tx/0x604e9590419b8e151e259e948bee5512777619e218d48d0ffe44a0429d695877): not yet annotated

Selected for residue cluster size #9, residue cluster USD #12. Cluster 9e7aa7869f: 2 transactions from 1 senders, $132,078, shape WETHDeposit, other examples [0x27ac…7faa](https://etherscan.io/tx/0x27ac822009ab29de7a1bdd1d220ce81f3142951bb87129cb33db7e74f5137faa). Block 25,904,745 at 2026-09-04T15:06:47+00:00, index 240/357, type 0x2, success. From [0x9fed…2722](https://etherscan.io/address/0x9fedf67538d0e0b9093efef2124eca8bb6932722) (an EOA; window profile: hot_wallet, very_high_nonce, 176 sent to 126 destinations, nonce 83,086 to 83,261) to [0xbbd8…a4f4](https://etherscan.io/address/0xbbd8d82fea76afc62984498929a1db52cffea4f4) (a contract of 64 bytes; never_sends, called 2 times in the window). Selector `0x`, calldata 0 bytes, value 37 ETH, 1 logs, tip 0.060767851 gwei. Largest position change $90,774 (ETH at [0xbbd8…a4f4](https://etherscan.io/address/0xbbd8d82fea76afc62984498929a1db52cffea4f4)); gross $90,774; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x9fed…2722](https://etherscan.io/address/0x9fedf67538d0e0b9093efef2124eca8bb6932722) nets ETH -$90,774 against [0xbbd8…a4f4](https://etherscan.io/address/0xbbd8d82fea76afc62984498929a1db52cffea4f4) (a contract of 64 bytes; never_sends).

Net flows: [0x9fed…2722](https://etherscan.io/address/0x9fedf67538d0e0b9093efef2124eca8bb6932722) -37.000000 ETH (-$90,774); [0xbbd8…a4f4](https://etherscan.io/address/0xbbd8d82fea76afc62984498929a1db52cffea4f4) +37.000000 ETH ($90,774).

Event families: WETHDeposit ×1.

_No qualitative note yet for this transaction._

### R6. [0x5d15…ed5f](https://etherscan.io/tx/0x5d15ebe0ed0a82145d14a49f2327d975671a3e989c025690e72205b65dc2ed5f): not yet annotated

Selected for residue cluster USD #13. Cluster bcd7d92216: 1 transactions from 1 senders, $100,000, shape Withdrawn; unknown=0x40dadaa36c6c2e3d7317e24757451ffb2d603d875f0ad5e92c5dd156573b1873. Block 25,904,935 at 2026-09-04T15:44:59+00:00, index 34/362, type 0x2, success. From [0x7ac3…c183](https://etherscan.io/address/0x7ac34681f6aaeb691e150c43ee494177c0e2c183) (an EOA delegated (EIP-7702) to [0x63c0…e32b](https://etherscan.io/address/0x63c0c19a282a1b52b07dd5a65b58948a07dae32b); window profile: no tags, 4 sent to 4 destinations, nonce 5,665 to 5,668) to [0xdb9b…7db3](https://etherscan.io/address/0xdb9b1e94b5b69df7e401ddbede43491141047db3) (a contract of 11,503 bytes; contract_like, never_sends, router_like, called 1012 times in the window). Selector `0xcef6d209`, calldata 1,444 bytes, value 0 ETH, 3 logs, tip 2 gwei. Largest position change $100,000 (USDS at [0x7ac3…c183](https://etherscan.io/address/0x7ac34681f6aaeb691e150c43ee494177c0e2c183)); gross $100,000; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x7ac3…c183](https://etherscan.io/address/0x7ac34681f6aaeb691e150c43ee494177c0e2c183) nets USDS $100,000 against [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) (a contract of 5,705 bytes; contract_like, never_sends).

Net flows: [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) -100,000.00 USDS (-$100,000); [0x7ac3…c183](https://etherscan.io/address/0x7ac34681f6aaeb691e150c43ee494177c0e2c183) +100,000.00 USDS ($100,000).

Event families: ERC20_Transfer_shape ×1, Withdrawn ×1, unknown ×1. Unknown topics: [0xdb9b…7db3](https://etherscan.io/address/0xdb9b1e94b5b69df7e401ddbede43491141047db3) 0x40dadaa36c6c2e3d… ×1.

_No qualitative note yet for this transaction._

### R7. [0x543b…807e](https://etherscan.io/tx/0x543b8c6b6c919ca86889e455114d6ebd87e2c8549cfca7f6cbd4829db0cf807e): 1,167-byte contract 0x4c21b757… pays 4,207,339.95 USDC to 0x774ae279… and emits an Aave-shaped four-argument Withdraw event

Selected for residue cluster size #5, residue cluster USD #2. Cluster a58db0475e: 3 transactions from 1 senders, $7,206,327, shape AaveWithdraw, other examples [0xfe63…dda6](https://etherscan.io/tx/0xfe63eda39fa055e708c680d87fdd48438fe8bcf49c02bf633c742578b8ffdda6) [0xd385…e1db](https://etherscan.io/tx/0xd38529fbaa5b352e9f1143db4daac844e0e337dae3e8e0da73800147536fe1db). Block 25,904,993 at 2026-09-04T15:56:47+00:00, index 227/278, type 0x2, success. From [0x8cf4…0765](https://etherscan.io/address/0x8cf40e96e7d7fd8a7a9bef70d3882fbbc4d40765) (an EOA; window profile: no tags, 3 sent to 1 destinations, nonce 666 to 668) to [0x4c21…54cf](https://etherscan.io/address/0x4c21b7577c8fe8b0b0669165ee7c8f67fa1454cf) (a contract of 1,167 bytes; never_sends, called 6 times in the window). Selector `0x866f1f02`, calldata 36 bytes, value 0 ETH, 2 logs, tip 0.0015 gwei. Largest position change $4,206,748 (USDC at [0x774a…8807](https://etherscan.io/address/0x774ae279c21b6a17a6e2bd5ab5398ff98f398807)); gross $4,206,748; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x4c21…54cf](https://etherscan.io/address/0x4c21b7577c8fe8b0b0669165ee7c8f67fa1454cf) nets USDC -$4,206,748 against [0x774a…8807](https://etherscan.io/address/0x774ae279c21b6a17a6e2bd5ab5398ff98f398807) (an EOA; never_sends).

Net flows: [0x4c21…54cf](https://etherscan.io/address/0x4c21b7577c8fe8b0b0669165ee7c8f67fa1454cf) -4,207,339.95 USDC (-$4,206,748); [0x774a…8807](https://etherscan.io/address/0x774ae279c21b6a17a6e2bd5ab5398ff98f398807) +4,207,339.95 USDC ($4,206,748).

Event families: AaveWithdraw ×1, ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence medium): Three transactions, $7.2M; the audit of aave_fork_lending_op caught this shape.

Unverified: the contract's purpose; 0x774ae279… also receives USDC from tokenized-fund wallets (0x9bc7d36e…), so it may be a fund-subscription hub.

Proposed type: `contract_payout_by_operator once record-event families with Aave shapes are allowed in transfer-only rules (left in the residue by round 4 on purpose)`

### R8. [0xe4ea…8819](https://etherscan.io/tx/0xe4ea78d0b1f9c1d2dd40c9064df231c86ff617a70a95019c44f63a82ce388819): not yet annotated

Selected for residue cluster USD #5. Cluster e7871cfccc: 1 transactions from 1 senders, $323,959, shape SafeReceived. Block 25,905,040 at 2026-09-04T16:06:23+00:00, index 141/346, type 0x2, success. From [0xab05…9c87](https://etherscan.io/address/0xab05688bb7617c66de62a91aa9aa92ed86499c87) (an EOA; window profile: no tags, 1 sent to 1 destinations, nonce 6 to 6) to [0xb35f…861c](https://etherscan.io/address/0xb35f2e5c1d4f05aee27376d6b064d577b2d1861c) (a contract of 171 bytes; never_sends, called 1 times in the window). Selector `0x`, calldata 0 bytes, value 131.476468533157212087 ETH, 1 logs, tip 2.05811801 gwei. Largest position change $323,959 (ETH at [0xb35f…861c](https://etherscan.io/address/0xb35f2e5c1d4f05aee27376d6b064d577b2d1861c)); gross $323,959; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xab05…9c87](https://etherscan.io/address/0xab05688bb7617c66de62a91aa9aa92ed86499c87) nets ETH -$323,959 against [0xb35f…861c](https://etherscan.io/address/0xb35f2e5c1d4f05aee27376d6b064d577b2d1861c) (a contract of 171 bytes; never_sends).

Net flows: [0xab05…9c87](https://etherscan.io/address/0xab05688bb7617c66de62a91aa9aa92ed86499c87) -131.476469 ETH (-$323,959); [0xb35f…861c](https://etherscan.io/address/0xb35f2e5c1d4f05aee27376d6b064d577b2d1861c) +131.476469 ETH ($323,959).

Event families: SafeReceived ×1.

_No qualitative note yet for this transaction._

### R9. [0x2634…1d6b](https://etherscan.io/tx/0x2634638463e844904e31bd14a4bf1d2d6888d82264ece221d81bba97f5be1d6b): not yet annotated

Selected for residue cluster size #11. Cluster da503b5f56: 2 transactions from 2 senders, $66,858, shape ERC20TransferWithData,GDeposit_auu, other examples [0xec88…0041](https://etherscan.io/tx/0xec8819f42f614b1acfbeec5cd13c2f58995c778078f7b73e5b29f11e46f80041). Block 25,905,237 at 2026-09-04T16:45:47+00:00, index 208/371, type 0x2, success. From [0xc9cf…b5d8](https://etherscan.io/address/0xc9cf07be20704fa5a11e9abc74c1175165c5b5d8) (an EOA; window profile: no tags, 1 sent to 1 destinations, nonce 25 to 25) to [0x5149…86ca](https://etherscan.io/address/0x514910771af9ca656af840dff83e8264ecf986ca) (a contract of 3,153 bytes; contract_like, never_sends, called 3099 times in the window). Selector `0x4000aea0`, calldata 484 bytes, value 0 ETH, 3 logs, tip 2 gwei. Largest position change $55,772 (LINK at [0xddc7…60ea](https://etherscan.io/address/0xddc796a66e8b83d0bccd97df33a6ccfba8fd60ea)); gross $55,772; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xc9cf…b5d8](https://etherscan.io/address/0xc9cf07be20704fa5a11e9abc74c1175165c5b5d8) nets LINK -$55,772 against [0xddc7…60ea](https://etherscan.io/address/0xddc796a66e8b83d0bccd97df33a6ccfba8fd60ea) (a contract of 708 bytes; never_sends).

Net flows: [0xc9cf…b5d8](https://etherscan.io/address/0xc9cf07be20704fa5a11e9abc74c1175165c5b5d8) -4,706.00 LINK (-$55,772); [0xddc7…60ea](https://etherscan.io/address/0xddc796a66e8b83d0bccd97df33a6ccfba8fd60ea) +4,706.00 LINK ($55,772).

Event families: ERC20TransferWithData ×1, ERC20_Transfer_shape ×1, GDeposit_auu ×1.

_No qualitative note yet for this transaction._

### R10. [0x3f09…2b60](https://etherscan.io/tx/0x3f098987899f867c476ef41045243449b469c846ef3892e7ff0239f3f5122b60): not yet annotated

Selected for residue cluster size #15. Cluster 07d08b3497: 1 transactions from 1 senders, $24,505, shape SafeReceived. Block 25,905,326 at 2026-09-04T17:03:47+00:00, index 179/183, type 0x2, success. From [0x8b10…c0fe](https://etherscan.io/address/0x8b1030a7de8c207a936e78ac5f1655630413c0fe) (an EOA; window profile: no tags, 8 sent to 6 destinations, nonce 1,991 to 1,998) to [0xf127…edc8](https://etherscan.io/address/0xf1272dcb5172b9cf2b39b223ab394243d608edc8) (a contract of 171 bytes; never_sends, called 1 times in the window). Selector `0x`, calldata 0 bytes, value 10 ETH, 1 logs, tip 0.0002 gwei. Largest position change $24,505 (ETH at [0xf127…edc8](https://etherscan.io/address/0xf1272dcb5172b9cf2b39b223ab394243d608edc8)); gross $24,505; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x8b10…c0fe](https://etherscan.io/address/0x8b1030a7de8c207a936e78ac5f1655630413c0fe) nets ETH -$24,505 against [0xf127…edc8](https://etherscan.io/address/0xf1272dcb5172b9cf2b39b223ab394243d608edc8) (a contract of 171 bytes; never_sends).

Net flows: [0x8b10…c0fe](https://etherscan.io/address/0x8b1030a7de8c207a936e78ac5f1655630413c0fe) -10.000000 ETH (-$24,505); [0xf127…edc8](https://etherscan.io/address/0xf1272dcb5172b9cf2b39b223ab394243d608edc8) +10.000000 ETH ($24,505).

Event families: SafeReceived ×1.

_No qualitative note yet for this transaction._

### R11. [0x944e…0df4](https://etherscan.io/tx/0x944e3e94dca322dc9c9bb1feedba7fc96c80b0fc4f7b40bb752dee2a3a050df4): not yet annotated

Selected for residue cluster size #8. Cluster 9db54c43ad: 2 transactions from 2 senders, $48,860, shape WETHDeposit; unknown=0x469059a9fd182ad3741bdd67b925e15056d35262609ea83393db7e8fb5a05ab1,0x7063ee7ac21ca792eb7d62d3a65598a5c986c4b0f7bd701aa453eb8a1387c956,0xccddf04ef3d8e97da0086a98ecc5d9facb21a818ce07ede3ab135dd12301443b, other examples [0xb2d5…256c](https://etherscan.io/tx/0xb2d5f8cd427fc6cec5ed7ff62d00453d5186ac7cafd5c31daf2315774d80256c). Block 25,905,670 at 2026-09-04T18:13:11+00:00, index 140/349, type 0x2, success. From [0x7535…c05b](https://etherscan.io/address/0x753553071c45bfd953862a96c31a2aa4184dc05b) (an EOA delegated (EIP-7702) to [0xe40c…6fa4](https://etherscan.io/address/0xe40ccb2d94975c51bff0c004efdfd9b3a5796fa4); window profile: no tags, 3 sent to 2 destinations, nonce 4,536 to 4,538) to [0xf2e6…da6b](https://etherscan.io/address/0xf2e6ed63bb255e51b64337c67fb4898aa979da6b) (a contract of 170 bytes; contract_like, never_sends, called 27 times in the window). Selector `0xc4b06ece`, calldata 68 bytes, value 0 ETH, 4 logs, tip 0.229188108 gwei. Largest position change $24,453 (WETH at [0x0000…6a56](https://etherscan.io/address/0x0000317bec33af037b5fab2028f52d14658f6a56)); gross $24,453; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x0000…6a56](https://etherscan.io/address/0x0000317bec33af037b5fab2028f52d14658f6a56) nets nothing priced.

Net flows: [0x0000…6a56](https://etherscan.io/address/0x0000317bec33af037b5fab2028f52d14658f6a56) +9.995407 WETH ($24,453).

Event families: unknown ×3, WETHDeposit ×1. Unknown topics: [0x0000…6a56](https://etherscan.io/address/0x0000317bec33af037b5fab2028f52d14658f6a56) 0x469059a9fd182ad3… ×1; [0x0007…d0de](https://etherscan.io/address/0x00071196a9129b7068404523e2047ef79f4ed0de) 0x7063ee7ac21ca792… ×1; [0xf2e6…da6b](https://etherscan.io/address/0xf2e6ed63bb255e51b64337c67fb4898aa979da6b) 0xccddf04ef3d8e97d… ×1.

_No qualitative note yet for this transaction._

### R12. [0x6f56…8e87](https://etherscan.io/tx/0x6f567cd118a3e01dec11c49b54179eeb9389a13f1948f159d44819a663df8e87): not yet annotated

Selected for control #2. Cluster d7fb1074a9: 1 transactions from 1 senders, $12,232, shape SafeReceived. Block 25,905,699 at 2026-09-04T18:18:59+00:00, index 39/315, type 0x2, success. From [0x536c…1c65](https://etherscan.io/address/0x536c4921d1aafde6a5cda882fb5ca046f3601c65) (an EOA; window profile: hot_wallet, very_high_nonce, 353 sent to 253 destinations, nonce 73,160 to 73,512) to [0x8318…b50d](https://etherscan.io/address/0x83187eece14abbe704b66651ab72e40670eab50d) (a contract of 171 bytes; never_sends, called 4 times in the window). Selector `0x`, calldata 0 bytes, value 4.999903 ETH, 1 logs, tip 2.032 gwei. Largest position change $12,232 (ETH at [0x8318…b50d](https://etherscan.io/address/0x83187eece14abbe704b66651ab72e40670eab50d)); gross $12,232; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x536c…1c65](https://etherscan.io/address/0x536c4921d1aafde6a5cda882fb5ca046f3601c65) nets ETH -$12,232 against [0x8318…b50d](https://etherscan.io/address/0x83187eece14abbe704b66651ab72e40670eab50d) (a contract of 171 bytes; never_sends).

Net flows: [0x536c…1c65](https://etherscan.io/address/0x536c4921d1aafde6a5cda882fb5ca046f3601c65) -4.999903 ETH (-$12,232); [0x8318…b50d](https://etherscan.io/address/0x83187eece14abbe704b66651ab72e40670eab50d) +4.999903 ETH ($12,232).

Event families: SafeReceived ×1.

_No qualitative note yet for this transaction._

### R13. [0xcbb9…856d](https://etherscan.io/tx/0xcbb98d3f046c46b84e263402077b5a2ca6adec5bea276649f3791d8a7d0a856d): operator 0xa4c542fc… (nonce 39,773) moves 110,772.07 USDT of 0x1ce24ad9…'s approved balance to four recipients (109,999.50 to the main one) through 0x9188db28…, no events

Selected for residue cluster size #4, residue cluster USD #7. Cluster a6c521a9a2: 4 transactions from 1 senders, $247,956, shape transfers-only, other examples [0x8f94…f39b](https://etherscan.io/tx/0x8f942c1c6c15f3940092fab0efc94360b74ffc093e3885952bdc19284465f39b) [0x7dc5…07a2](https://etherscan.io/tx/0x7dc57b8e3e9f2a699caac10322130aad93c5c42d135bcc76e4fa8238e91b07a2) [0xa80e…2e07](https://etherscan.io/tx/0xa80ecfa9e717ddb6e2289360d1af67277a2428474ffbdbd2c4222ad58b6b2e07). Block 25,906,701 at 2026-09-04T21:39:47+00:00, index 228/299, type 0x0, success. From [0xa4c5…b7c5](https://etherscan.io/address/0xa4c542fc03ab644b35d0ef51bc3c58380f78b7c5) (an EOA; window profile: bot_sender, 55 sent to 2 destinations, nonce 39,746 to 39,800) to [0x9188…96e5](https://etherscan.io/address/0x9188db2825bd0ad76a2ba3aba21274428dc696e5) (a contract of 4,808 bytes; contract_like, never_sends, called 43 times in the window). Selector `0x5bebe4ee`, calldata 964 bytes, value 0 ETH, 4 logs, tip 0.005761173 gwei. Largest position change $110,772 (USDT at [0x1ce2…fac4](https://etherscan.io/address/0x1ce24ad9908a0964acc91b8edbd104dd6f9ffac4)); gross $110,772; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x1ce2…fac4](https://etherscan.io/address/0x1ce24ad9908a0964acc91b8edbd104dd6f9ffac4) nets nothing priced against [0x8951…7564](https://etherscan.io/address/0x8951179b3a28c508fb431cee275bce69ae4c7564) (an EOA; no tags).

Net flows: [0x1ce2…fac4](https://etherscan.io/address/0x1ce24ad9908a0964acc91b8edbd104dd6f9ffac4) -110,767.21 USDT (-$110,772); [0x8951…7564](https://etherscan.io/address/0x8951179b3a28c508fb431cee275bce69ae4c7564) +109,999.50 USDT ($110,004); [0xecc4…5d6b](https://etherscan.io/address/0xecc4cb490f3159cf155afa2c2e0e9cb84e5e5d6b) +742.780000 USDT ($742.81); [0xe1b1…57f6](https://etherscan.io/address/0xe1b1817ba558e30916801d0fa5fa55f113a257f6) +21.530000 USDT ($21.53); [0xf012…1da7](https://etherscan.io/address/0xf012dab8772f61901f51681db2f40bb883481da7) +3.395758 USDT ($3.40).

Event families: ERC20_Transfer_shape ×4.

Interpretation (LLM, confidence high): Four transactions, $248k.

Proposed type: `extend operator_sweep_no_events to one payer and several recipients (feedback 9)`

### R14. [0x097f…6df2](https://etherscan.io/tx/0x097f74cda0a7f98689f0d83445beff33b106407f794d8a57b8a12fe8b4cf6df2): not yet annotated

Selected for residue cluster size #13, residue cluster USD #10. Cluster f6ab6c4a03: 2 transactions from 2 senders, $181,911, shape SafeReceived, other examples [0x8783…27f5](https://etherscan.io/tx/0x878323fec91ce8394d5b4b515f5c3c4b6631c14bf2f1d84ecb99b56331bf27f5). Block 25,907,187 at 2026-09-04T23:17:11+00:00, index 50/255, type 0x2, success. From [0x0d07…92fe](https://etherscan.io/address/0x0d0707963952f2fba59dd06f2b425ace40b492fe) (an EOA; window profile: hot_wallet, many_sources, very_high_nonce, 4257 sent to 661 destinations, nonce 10,119,086 to 10,123,342) to [0x7799…9195](https://etherscan.io/address/0x7799905deebca738038984ce341fb1b226769195) (a contract of 171 bytes; never_sends, called 7 times in the window). Selector `0x`, calldata 0 bytes, value 44.0561112 ETH, 1 logs, tip 1 gwei. Largest position change $107,991 (ETH at [0x7799…9195](https://etherscan.io/address/0x7799905deebca738038984ce341fb1b226769195)); gross $107,991; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x0d07…92fe](https://etherscan.io/address/0x0d0707963952f2fba59dd06f2b425ace40b492fe) nets ETH -$107,991 against [0x7799…9195](https://etherscan.io/address/0x7799905deebca738038984ce341fb1b226769195) (a contract of 171 bytes; never_sends).

Net flows: [0x0d07…92fe](https://etherscan.io/address/0x0d0707963952f2fba59dd06f2b425ace40b492fe) -44.056111 ETH (-$107,991); [0x7799…9195](https://etherscan.io/address/0x7799905deebca738038984ce341fb1b226769195) +44.056111 ETH ($107,991).

Event families: SafeReceived ×1.

_No qualitative note yet for this transaction._

### R15. [0xd90a…606c](https://etherscan.io/tx/0xd90ae22832d1b4946ad14248c692ab976e456ad7984b902a8a2aaf403cef606c): not yet annotated

Selected for residue cluster USD #14. Cluster 4f556fce5d: 1 transactions from 1 senders, $99,026, shape SafeReceived. Block 25,907,574 at 2026-09-05T00:34:59+00:00, index 97/203, type 0x2, success. From [0x8989…bfe6](https://etherscan.io/address/0x8989e326d68d17660ff54543f4a88130a6f1bfe6) (an EOA; window profile: many_sources, 43 sent to 30 destinations, nonce 1,418 to 1,460) to [0x12e5…155d](https://etherscan.io/address/0x12e5179df245e1a3cdd41c024a4174b3b395155d) (a contract of 171 bytes; never_sends, called 2 times in the window). Selector `0x`, calldata 0 bytes, value 40.34 ETH, 1 logs, tip 1 gwei. Largest position change $99,026 (ETH at [0x8989…bfe6](https://etherscan.io/address/0x8989e326d68d17660ff54543f4a88130a6f1bfe6)); gross $99,026; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x8989…bfe6](https://etherscan.io/address/0x8989e326d68d17660ff54543f4a88130a6f1bfe6) nets ETH -$99,026 against [0x12e5…155d](https://etherscan.io/address/0x12e5179df245e1a3cdd41c024a4174b3b395155d) (a contract of 171 bytes; never_sends).

Net flows: [0x12e5…155d](https://etherscan.io/address/0x12e5179df245e1a3cdd41c024a4174b3b395155d) +40.340000 ETH ($99,026); [0x8989…bfe6](https://etherscan.io/address/0x8989e326d68d17660ff54543f4a88130a6f1bfe6) -40.340000 ETH (-$99,026).

Event families: SafeReceived ×1.

_No qualitative note yet for this transaction._

### R16. [0x06b4…7c02](https://etherscan.io/tx/0x06b4047508a4274305b7bc26e5270fb2a0c858dc5a2bd47ce1a898b974ae7c02): 24.877885 ETH from a fresh wallet into 0x0439e60f…, a Safe-like contract (SafeReceived) that forwards the order to the cross-chain swap service 0xc1d13492… through aggregator 0x9a47f328…

Selected for residue cluster size #3, residue cluster USD #9. Cluster d79f2e2e18: 5 transactions from 4 senders, $195,065, shape SafeReceived; unknown=0x4e96fb90a89341a56db7ad2bbf04c715bbf20be6a9a9e764671f718c4697649a,0x6ded982279c8387ad8a63e73385031a3807c1862e633f06e09d11bcb6e282f60,0x831bac9533a2034226daa21109dbd4f887674f0fe4877e1a8b35b3ffe1bdce76, other examples [0xed27…49fe](https://etherscan.io/tx/0xed2741979ab8feb9ced666b56defff474015139941f70cfb6e4cbb1267bb49fe) [0xfdd6…f2d7](https://etherscan.io/tx/0xfdd6d4e1e5630c8ae0b5a932d75f5e1cc8b28df752f3373cbde3a2aa9d9ff2d7) [0x5e9a…1f5c](https://etherscan.io/tx/0x5e9ac0f1ef072c515e8f70b98091b89e5a6aace5854e54b55038cfb8b8171f5c). Block 25,908,333 at 2026-09-05T03:06:59+00:00, index 114/514, type 0x2, success. From [0x19da…7aa0](https://etherscan.io/address/0x19da87b37b600c3074b5a29972ac3dffd9937aa0) (an EOA; window profile: no tags, 2 sent to 1 destinations, nonce 2 to 3) to [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) (a contract of 6,000 bytes; contract_like, many_sources, never_sends, router_like, called 7532 times in the window). Selector `0x3ce33bff`, calldata 837 bytes, value 24.877885149064160037 ETH, 4 logs, tip 2.100000001 gwei. Largest position change $61,029 (ETH at [0x19da…7aa0](https://etherscan.io/address/0x19da87b37b600c3074b5a29972ac3dffd9937aa0)); gross $61,029; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x19da…7aa0](https://etherscan.io/address/0x19da87b37b600c3074b5a29972ac3dffd9937aa0) nets ETH -$61,029 against [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) (a contract of 6,000 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) +24.877885 ETH ($61,029); [0x19da…7aa0](https://etherscan.io/address/0x19da87b37b600c3074b5a29972ac3dffd9937aa0) -24.877885 ETH (-$61,029).

Event families: unknown ×3, SafeReceived ×1. Unknown topics: [0x9a47…ed16](https://etherscan.io/address/0x9a47f3289794e9bbc6a3c571f6d96ad4e7baed16) 0x6ded982279c8387a… ×1; [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) 0x4e96fb90a89341a5… ×1; [0x9a47…ed16](https://etherscan.io/address/0x9a47f3289794e9bbc6a3c571f6d96ad4e7baed16) 0x831bac9533a20342… ×1.

Interpretation (LLM, confidence medium): Five such deposits ($195k) and seven with a Relay-style deposit event ($91k).

Unverified: the aggregator; 0x9a47f328… emits its two events about 8,400 times a day.

Proposed type: `service_deposit_with_memo would catch it if the memo were in the outer calldata; here the order string sits inside the aggregator's inner call`

### R17. [0xae8f…1a7e](https://etherscan.io/tx/0xae8feb731ed5395675a937a731d023b48d75c9b5d99157d71cb97cee85371a7e): not yet annotated

Selected for residue cluster USD #8. Cluster 69397339db: 1 transactions from 1 senders, $230,529, shape MorphoAccrueInterest; unknown=0x003d5fea7147843a952736a57f88f9e5565759fb750f34a8e58cbc215034c64c,0x7120161a7b3d31251e01294ab351ef15a41b91659a36032e4641bb89b121e321,0xb5b9244c6ced1f40da658794a27cce7a0fb4184569b3916665b60044d25bb0b4. Block 25,908,558 at 2026-09-05T03:51:59+00:00, index 177/206, type 0x2, success. From [0x9cf2…6195](https://etherscan.io/address/0x9cf2b94caba0ab5ea0709c9aaa68716908236195) (an EOA; window profile: bot_sender, 164 sent to 1 destinations, nonce 7,394 to 7,557) to [0xf82e…4263](https://etherscan.io/address/0xf82ef4080a53b71093f9c470676fc80e2adc4263) (a contract of 2,973 bytes; contract_like, never_sends, router_like, called 164 times in the window). Selector `0xa6b41ec4`, calldata 1,540 bytes, value 0 ETH, 5 logs, tip 0.0001 gwei. Largest position change $230,529 (USDT at [0x587d…1304](https://etherscan.io/address/0x587d5dd0c48193f2e548f64ab5a7919253c41304)); gross $230,529; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x587d…1304](https://etherscan.io/address/0x587d5dd0c48193f2e548f64ab5a7919253c41304) nets nothing priced against [0x31ba…37a3](https://etherscan.io/address/0x31bacbbf2c5a364c345055fe47556d42f42937a3) (an EOA; no tags).

Net flows: [0x31ba…37a3](https://etherscan.io/address/0x31bacbbf2c5a364c345055fe47556d42f42937a3) +230,519.26 USDT ($230,529); [0x587d…1304](https://etherscan.io/address/0x587d5dd0c48193f2e548f64ab5a7919253c41304) -230,519.26 USDT (-$230,529).

Event families: unknown ×3, ERC20_Transfer_shape ×1, MorphoAccrueInterest ×1. Unknown topics: [0xf82e…4263](https://etherscan.io/address/0xf82ef4080a53b71093f9c470676fc80e2adc4263) 0x003d5fea7147843a… ×1; [0xf82e…4263](https://etherscan.io/address/0xf82ef4080a53b71093f9c470676fc80e2adc4263) 0xb5b9244c6ced1f40… ×1; [0x870a…00bc](https://etherscan.io/address/0x870ac11d48b15db9a138cf899d20f13f79ba00bc) 0x7120161a7b3d3125… ×1.

_No qualitative note yet for this transaction._

### R18. [0x6390…3354](https://etherscan.io/tx/0x63909e2b130332a1cc60b303ce528d15aa7ff41d8deeafaae339d1e70e9e3354): not yet annotated

Selected for residue cluster size #14. Cluster 06b208c38a: 1 transactions from 1 senders, $26,559, shape ERC20TransferWithData; unknown=0x16aadfd997cc8ab0f2890a6c7fe1ea76bdb61f8c74cc386c92818a2b1767006a,0x2522be42592f34e2ca9797604751c6950bec2b2edd55de8bdaede606557b67fe,0xa6b1f21803a1471cf6981bffc4c07ff6610f2b88efc44f62b96dca65a63d3d27,0xb4caaf29adda3eefee3ad552a8e85058589bf834c7466cae4ee58787f70589ed. Block 25,908,587 at 2026-09-05T03:57:47+00:00, index 20/250, type 0x2, success. From [0xf5c0…1ad4](https://etherscan.io/address/0xf5c08d55a77063ac4e5e18f1a470804088be1ad4) (an EOA; window profile: no tags, 8 sent to 7 destinations, nonce 3,925 to 3,932) to [0xddc7…60ea](https://etherscan.io/address/0xddc796a66e8b83d0bccd97df33a6ccfba8fd60ea) (a contract of 708 bytes; never_sends, called 8 times in the window). Selector `0xefb15bae`, calldata 388 bytes, value 0 ETH, 8 logs, tip 5 gwei. Largest position change $26,559 (LINK at [0xbc10…db5e](https://etherscan.io/address/0xbc10f2e862ed4502144c7d632a3459f49dfcdb5e)); gross $79,677; swaps 0 in 0 pools; 3 distinct recipients. Principal [0xbc10…db5e](https://etherscan.io/address/0xbc10f2e862ed4502144c7d632a3459f49dfcdb5e) nets nothing priced against [0xb8b2…3cd5](https://etherscan.io/address/0xb8b295df2cd735b15be5eb419517aa626fc43cd5) (a contract of 680 bytes; never_sends).

Net flows: [0xb8b2…3cd5](https://etherscan.io/address/0xb8b295df2cd735b15be5eb419517aa626fc43cd5) -2,241.00 LINK (-$26,559); [0xbc10…db5e](https://etherscan.io/address/0xbc10f2e862ed4502144c7d632a3459f49dfcdb5e) +2,241.00 LINK ($26,559); [0x9f5d…a3b5](https://etherscan.io/address/0x9f5d3ae6025ba135cf6dc16aee0f4ceda5eca3b5) +0.000000 LINK ($0.00); [0xac12…c1b5](https://etherscan.io/address/0xac12290b097f6893322f5430627e472131fbc1b5) +0.000000 LINK ($0.00).

Event families: unknown ×4, ERC20_Transfer_shape ×3, ERC20TransferWithData ×1. Unknown topics: [0x9969…d813](https://etherscan.io/address/0x996913c8c08472f584ab8834e925b06d0eb1d813) 0xa6b1f21803a1471c… ×1; [0x9969…d813](https://etherscan.io/address/0x996913c8c08472f584ab8834e925b06d0eb1d813) 0x16aadfd997cc8ab0… ×1; [0xbc10…db5e](https://etherscan.io/address/0xbc10f2e862ed4502144c7d632a3459f49dfcdb5e) 0xb4caaf29adda3eef… ×1; [0xddc7…60ea](https://etherscan.io/address/0xddc796a66e8b83d0bccd97df33a6ccfba8fd60ea) 0x2522be42592f34e2… ×1.

_No qualitative note yet for this transaction._

### R19. [0x43a0…3ff3](https://etherscan.io/tx/0x43a0c9031eb1883ff4196ce58d701cb357e7eaa57b49aa73a70ae0d774f03ff3): not yet annotated

Selected for residue cluster size #7. Cluster 46bdda75a5: 2 transactions from 1 senders, $70,420, shape WETHDeposit, other examples [0x160f…8b38](https://etherscan.io/tx/0x160fbf972126dfe1703dd555a8216ac2a6fe1719d5579fad507321b007e98b38). Block 25,908,610 at 2026-09-05T04:02:23+00:00, index 163/166, type 0x2, success. From [0x0294…a11c](https://etherscan.io/address/0x0294e5bccec487802a7150263464db408d01a11c) (an EOA; window profile: no tags, 3 sent to 1 destinations, nonce 10,202 to 10,204) to [0xbb60…8df7](https://etherscan.io/address/0xbb605dc51cac7eca64001651ac71c2c002308df7) (a contract of 64 bytes; never_sends, called 3 times in the window). Selector `0x`, calldata 0 bytes, value 17.431428141455536696 ETH, 1 logs, tip 0.001 gwei. Largest position change $42,746 (ETH at [0xbb60…8df7](https://etherscan.io/address/0xbb605dc51cac7eca64001651ac71c2c002308df7)); gross $42,746; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x0294…a11c](https://etherscan.io/address/0x0294e5bccec487802a7150263464db408d01a11c) nets ETH -$42,746 against [0xbb60…8df7](https://etherscan.io/address/0xbb605dc51cac7eca64001651ac71c2c002308df7) (a contract of 64 bytes; never_sends).

Net flows: [0x0294…a11c](https://etherscan.io/address/0x0294e5bccec487802a7150263464db408d01a11c) -17.431428 ETH (-$42,746); [0xbb60…8df7](https://etherscan.io/address/0xbb605dc51cac7eca64001651ac71c2c002308df7) +17.431428 ETH ($42,746).

Event families: WETHDeposit ×1.

_No qualitative note yet for this transaction._

### R20. [0x79ab…74b5](https://etherscan.io/tx/0x79abe41140e4252dbd6b56aab6ded4e07ba3098758f6172496a03dbd454f74b5): not yet annotated

Selected for residue cluster USD #11. Cluster 3fcb5efbf9: 1 transactions from 1 senders, $140,556, shape MorphoAccrueInterest,MorphoWithdrawCollateral. Block 25,909,229 at 2026-09-05T06:06:35+00:00, index 118/242, type 0x2, success. From [0x9149…a356](https://etherscan.io/address/0x914906d5465deac8916a226ccea3bcfa6a67a356) (an EOA; window profile: no tags, 11 sent to 6 destinations, nonce 656 to 666) to [0xa428…fb6a](https://etherscan.io/address/0xa428723ee8ffd87088c36121d72100b43f11fb6a) (a contract of 17,201 bytes; flash_lender, never_sends, called 1 times in the window). Selector `0xaf1beac3`, calldata 324 bytes, value 0 ETH, 3 logs, tip 0.6 gwei. Largest position change $140,556 (IMPL:0x35d8…9bc0 at [0xa428…fb6a](https://etherscan.io/address/0xa428723ee8ffd87088c36121d72100b43f11fb6a)); gross $140,556; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x9149…a356](https://etherscan.io/address/0x914906d5465deac8916a226ccea3bcfa6a67a356) nets IMPL:0x35d8…9bc0 $140,556 against [0xa428…fb6a](https://etherscan.io/address/0xa428723ee8ffd87088c36121d72100b43f11fb6a) (a contract of 17,201 bytes; flash_lender, never_sends).

Net flows: [0x9149…a356](https://etherscan.io/address/0x914906d5465deac8916a226ccea3bcfa6a67a356) +145,040.89 IMPL:0x35d8…9bc0 ($140,556); [0xa428…fb6a](https://etherscan.io/address/0xa428723ee8ffd87088c36121d72100b43f11fb6a) -145,040.89 IMPL:0x35d8…9bc0 (-$140,556).

Event families: ERC20_Transfer_shape ×1, MorphoAccrueInterest ×1, MorphoWithdrawCollateral ×1.

_No qualitative note yet for this transaction._

### R21. [0xde01…2fcf](https://etherscan.io/tx/0xde017d5628fc4fb92055d6242e12c2d510f73143b8a607131cd3da79e6f12fcf): sUSDe cooldown claim routed into a vault: 66,244.17 USDe leaves the silo to 0xe620afb6… and on to 0xceda2d85… in one call

Selected for residue cluster size #1, residue cluster USD #4. Cluster 5c60c2f8be: 9 transactions from 1 senders, $354,040, shape transfers-only, other examples [0x96c0…2677](https://etherscan.io/tx/0x96c0e78e95fca861cfb2477f682ff221f206cb4852a9a4bd4870ac0db8852677) [0x33ff…d79b](https://etherscan.io/tx/0x33ff9df3a2c473308483f035776a011a7524ddec5106bf74462f9660bfd1d79b) [0x1a6a…cfb5](https://etherscan.io/tx/0x1a6ab07cf3af43b224a9b37c7664b4659d7bce8877799de37ac3c6abeb5acfb5). Block 25,910,092 at 2026-09-05T09:00:47+00:00, index 99/277, type 0x2, success. From [0x7392…f38b](https://etherscan.io/address/0x739212d5bafe6aac8be49a60b7d003bd41dbf38b) (an EOA; window profile: no tags, 145 sent to 11 destinations, nonce 17,607 to 17,751) to [0xceda…366d](https://etherscan.io/address/0xceda2d856238aa0d12f6329de20b9115f07c366d) (a contract of 1,747 bytes; contract_like, never_sends, called 71 times in the window). Selector `0x71dc0cf9`, calldata 68 bytes, value 0 ETH, 2 logs, tip 1 gwei. Largest position change $66,244 (USDe at [0xceda…366d](https://etherscan.io/address/0xceda2d856238aa0d12f6329de20b9115f07c366d)); gross $132,488; swaps 0 in 0 pools; 2 distinct recipients. Principal [0xceda…366d](https://etherscan.io/address/0xceda2d856238aa0d12f6329de20b9115f07c366d) nets USDe $66,244 against [0x7fc7…3425](https://etherscan.io/address/0x7fc7c91d556b400afa565013e3f32055a0713425) (a contract of 534 bytes; never_sends).

Net flows: [0x7fc7…3425](https://etherscan.io/address/0x7fc7c91d556b400afa565013e3f32055a0713425) -66,244.17 USDe (-$66,244); [0xceda…366d](https://etherscan.io/address/0xceda2d856238aa0d12f6329de20b9115f07c366d) +66,244.17 USDe ($66,244); [0xe620…90f0](https://etherscan.io/address/0xe620afb67223ae03c260112ae21a717af94c90f0) +0.000000 USDe ($0.00).

Event families: ERC20_Transfer_shape ×2.

Interpretation (LLM, confidence high): Nine transactions, $354k.

Proposed type: `susde_unstake_claim generalised to claims made through a router (the receiver is a contract, the destination is not sUSDe)`

### R22. [0xfc2e…95f8](https://etherscan.io/tx/0xfc2ee3f8010052b388dab66181e06ed5d8fdc3c68a10e9bba549110f5f6295f8): not yet annotated

Selected for control #3. Cluster 5e58b1c83d: 1 transactions from 1 senders, $76,773, shape WETHDeposit. Block 25,910,973 at 2026-09-05T11:57:11+00:00, index 96/270, type 0x2, success. From [0x922c…3eb3](https://etherscan.io/address/0x922c3800c278c5d45e282f6b83fe0bfc713e3eb3) (an EOA delegated (EIP-7702) to [0x63c0…e32b](https://etherscan.io/address/0x63c0c19a282a1b52b07dd5a65b58948a07dae32b); window profile: pass_through, 1 sent to 1 destinations, nonce 620 to 620) to [0xbb6d…782a](https://etherscan.io/address/0xbb6d0a1b1d267f1fea605ed502ce938cf185782a) (a contract of 64 bytes; never_sends, called 1 times in the window). Selector `0x`, calldata 0 bytes, value 31.277 ETH, 1 logs, tip 0.900099283 gwei. Largest position change $76,773 (ETH at [0xbb6d…782a](https://etherscan.io/address/0xbb6d0a1b1d267f1fea605ed502ce938cf185782a)); gross $76,773; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x922c…3eb3](https://etherscan.io/address/0x922c3800c278c5d45e282f6b83fe0bfc713e3eb3) nets ETH -$76,773 against [0xbb6d…782a](https://etherscan.io/address/0xbb6d0a1b1d267f1fea605ed502ce938cf185782a) (a contract of 64 bytes; never_sends).

Net flows: [0x922c…3eb3](https://etherscan.io/address/0x922c3800c278c5d45e282f6b83fe0bfc713e3eb3) -31.277000 ETH (-$76,773); [0xbb6d…782a](https://etherscan.io/address/0xbb6d0a1b1d267f1fea605ed502ce938cf185782a) +31.277000 ETH ($76,773).

Event families: WETHDeposit ×1.

_No qualitative note yet for this transaction._

### R23. [0x918d…172c](https://etherscan.io/tx/0x918d6273203b32d1294c76639791b1738666228c933b1cb5312573dcc9bb172c): not yet annotated

Selected for control #1. Cluster 7acd231ee3: 1 transactions from 1 senders, $19,233, shape WETHDeposit. Block 25,911,048 at 2026-09-05T12:12:23+00:00, index 174/349, type 0x2, success. From [0xd638…da4f](https://etherscan.io/address/0xd638d4c9d4f434df60c671f758f6655c0771da4f) (an EOA; window profile: pass_through, 1 sent to 1 destinations, nonce 113 to 113) to [0xbb0f…ba5b](https://etherscan.io/address/0xbb0f6873d946e7d5779cc7dab1b2302283f5ba5b) (a contract of 64 bytes; never_sends, called 1 times in the window). Selector `0x`, calldata 0 bytes, value 7.832 ETH, 1 logs, tip 0.6 gwei. Largest position change $19,233 (ETH at [0xd638…da4f](https://etherscan.io/address/0xd638d4c9d4f434df60c671f758f6655c0771da4f)); gross $19,233; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xd638…da4f](https://etherscan.io/address/0xd638d4c9d4f434df60c671f758f6655c0771da4f) nets ETH -$19,233 against [0xbb0f…ba5b](https://etherscan.io/address/0xbb0f6873d946e7d5779cc7dab1b2302283f5ba5b) (a contract of 64 bytes; never_sends).

Net flows: [0xbb0f…ba5b](https://etherscan.io/address/0xbb0f6873d946e7d5779cc7dab1b2302283f5ba5b) +7.832000 ETH ($19,233); [0xd638…da4f](https://etherscan.io/address/0xd638d4c9d4f434df60c671f758f6655c0771da4f) -7.832000 ETH (-$19,233).

Event families: WETHDeposit ×1.

_No qualitative note yet for this transaction._

### R24. [0xf8da…a1c1](https://etherscan.io/tx/0xf8da96d0de077e2f483c86fb3e9e2bdd3b500cab4b3daa8e596f75ec40d5a1c1): not yet annotated

Selected for residue cluster size #2, residue cluster USD #15. Cluster 2715da933b: 6 transactions from 1 senders, $88,405, shape WETHDeposit; unknown=0x576dcb24693ce268755564d0b539845212a2e052e80b6a958db4920b057f367c, other examples [0xbb53…6f63](https://etherscan.io/tx/0xbb53c2852114e6e41cb5f912ea9f56d9550d360696a9883fb83449320d5b6f63) [0x59e0…21d8](https://etherscan.io/tx/0x59e0cb8854284383e68e90bae6d1541e7c6a0df839a1ad19301665234abc21d8) [0xf5e4…177c](https://etherscan.io/tx/0xf5e477699051a0327bd3309ae2cd411f2be4e5ad6afcd0d857e6ea873a37177c). Block 25,911,474 at 2026-09-05T13:37:47+00:00, index 305/335, type 0x2, success. From [0xac9d…084f](https://etherscan.io/address/0xac9da6761ef80644a3bb9ab7e590cf4e64be084f) (an EOA; window profile: no tags, 136 sent to 38 destinations, nonce 3,301 to 3,436) to [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3) (a contract of 24,345 bytes; contract_like, never_sends, router_like, called 1645 times in the window). Selector `0xbcaeadb6`, calldata 36 bytes, value 0 ETH, 2 logs, tip 0.000092663 gwei. Largest position change $14,753 (WETH at [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3)); gross $14,753; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3) nets WETH $14,753.

Net flows: [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3) +6.000000 WETH ($14,753).

Event families: WETHDeposit ×1, unknown ×1. Unknown topics: [0x09fc…69d3](https://etherscan.io/address/0x09fc9b7545020f6a51d113e495e0a451597969d3) 0x576dcb24693ce268… ×1.

_No qualitative note yet for this transaction._

## Residue of earlier rounds: the investigations that produced the new types

These packets were selected by earlier classify runs (archived under round_XX/) and are the evidence behind the types added on this run; after the new rules they are no longer residue.

### E25. [0xc343…f982](https://etherscan.io/tx/0xc343dc20c47f06d5a6151b1e6e5994ddabbe19691e7c492bd2a26e6c02bdf982): the next tier of the same account stack: 0x37e77355… pays 4,999,296.50 USDC to an external address by execute() (selected in round_01)

Selected for residue cluster size #9, residue cluster USD #2. Cluster fedb697fd3: 54 transactions from 1 senders, $79,356,389, shape transfers-only, other examples [0xc86c…ce86](https://etherscan.io/tx/0xc86c2f2fdd5083a666b40c3b4a8199249da9db3e6b2a0567f3738f601452ce86) [0xd4bd…be90](https://etherscan.io/tx/0xd4bda26533636ab75267b39ecb42a0792224c0b5733502a199fd65299f71be90) [0x6752…8bf6](https://etherscan.io/tx/0x675221b9cca2f4b2c5edc29d41269ace00a09f13a740741ae4fae835d5cf8bf6). Block 25,904,570 at 2026-09-04T14:31:47+00:00, index 106/276, type 0x2, status not fetched. From [0x4297…79b2](https://etherscan.io/address/0x4297b5812b4583138889a2d094db0c72eafa79b2) (unknown code status; window profile: no tags, 112 sent to 5 destinations, nonce 17,248 to 17,359) to [0x37e7…d046](https://etherscan.io/address/0x37e773558f127e782fdf5e4189ba28d67f72d046) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); contract_like, never_sends, called 62 times in the window). Selector `0xe9ae5c53`, calldata 516 bytes, value 0 ETH, 1 logs, tip 0.218959406 gwei. Largest position change $4,999,296 (USDC at [0x3f66…6a2a](https://etherscan.io/address/0x3f66eb72b4224fbefd8712ca83cd2940b10f6a2a)); gross $4,999,296; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x37e7…d046](https://etherscan.io/address/0x37e773558f127e782fdf5e4189ba28d67f72d046) nets USDC -$4,999,296 against [0x3f66…6a2a](https://etherscan.io/address/0x3f66eb72b4224fbefd8712ca83cd2940b10f6a2a) (unknown code status; no tags).

Net flows: [0x37e7…d046](https://etherscan.io/address/0x37e773558f127e782fdf5e4189ba28d67f72d046) -5,000,000.00 USDC (-$4,999,296); [0x3f66…6a2a](https://etherscan.io/address/0x3f66eb72b4224fbefd8712ca83cd2940b10f6a2a) +5,000,000.00 USDC ($4,999,296).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): The account that received $11M in 0x2f3c690b… pays out in $5M pieces; the recipient 0x3f66eb… has no tags in the day profile, so it is a customer or a counterparty rather than another hub.

Unverified: as above.

Proposed type: `smart_account_execute_transfer`

### E26. [0x0935…69b5](https://etherscan.io/tx/0x0935211328a440f049f880bc68b1ae4b124f9f4397635d5c1cabaadade2b69b5): 10,000,000.01 USDS repaid on the Aave-v3-fork pool 0xc13e21b6… with repayWithPermit (selected in round_01)

Selected for residue cluster USD #11. Cluster 4a4288942f: 9 transactions from 4 senders, $33,333,007, shape AaveRepay,AaveReserveDataUpdated,AaveScaledBurn, other examples [0xa995…7253](https://etherscan.io/tx/0xa995fb8315c53d1d143ea32a08c4444234a12c9b52f75ad163e2ad7ee5a67253) [0x37b4…c5b6](https://etherscan.io/tx/0x37b49edf9bafd3827b0d64ef3bedb0fc32f7ea63866e352b4d0d3157bc7cc5b6) [0xe17a…aae7](https://etherscan.io/tx/0xe17ad753c669eb65744d526b547b0b4b9e77ca2882da3e03c309206a56aaaae7). Block 25,904,657 at 2026-09-04T14:49:11+00:00, index 95/335, type 0x2, status not fetched. From [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) (unknown code status; window profile: no tags, 9 sent to 3 destinations, nonce 12,160 to 12,168) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0xee3e210b`, calldata 260 bytes, value 0 ETH, 6 logs, tip 0.041994776 gwei. Largest position change $10,000,000 (USDS at [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359)); gross $10,000,000; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) nets USDS -$10,000,000 against [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359) (unknown code status; never_sends).

Net flows: [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) -10,000,000.01 USDS (-$10,000,000); [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359) +10,000,000.01 USDS ($10,000,000).

Unpriced ERC-20 transfers: [0x8c14…449e](https://etherscan.io/address/0x8c147debea24fb98ade8dda4bf142992928b449e) ×1 (largest raw 9998642280081700033538064).

Event families: ERC20_Transfer_shape ×2, AaveRepay ×1, AaveReserveDataUpdated ×1, AaveScaledBurn ×1, Approval ×1.

Interpretation (LLM, confidence high): The borrower 0xb99a2c… sends USDS to the spToken contract 0xc02ab1…; nine such repayments in the day sum to $33.3M. Selector 0xee3e210b is repayWithPermit, so the user signed the allowance off-chain and paid one transaction.

Unverified: the pool as SparkLend is model memory; the event shapes are Aave v3's (Repay, ReserveDataUpdated, scaled debt Burn).

Proposed type: `aave_fork_lending_op`. Rule: Aave-shaped pool events from an emitter other than the Aave core pool, no swap, no flash loan. Method: lending

### E27. [0x2f3c…d7e6](https://etherscan.io/tx/0x2f3c690b65baaebdbaf819f137193e3a17795f0fdb7c2f5f1b54f42c3786d7e6): ERC-7821 execute() on account contract 0xf90caf00… sending 11,054,870.43 USDC to account contract 0x37e77355… (selected in round_01)

Selected for residue cluster USD #1. Cluster 0e4b43e00b: 20 transactions from 1 senders, $83,809,145, shape transfers-only, other examples [0x5ab9…a138](https://etherscan.io/tx/0x5ab9fcbec4018d57d54dd8cce0fa2009c07da7ed7e6074345fed40ebcbd0a138) [0x2d12…0603](https://etherscan.io/tx/0x2d12ccb9c04ab251ec7224a71009bff577591f9c7fcb9cefef9f87f202b30603) [0x3372…beaa](https://etherscan.io/tx/0x3372323078d6dfa13e707ff5266b1be537a6222da5b939442681e8982d22beaa). Block 25,904,811 at 2026-09-04T15:19:59+00:00, index 94/161, type 0x2, status not fetched. From [0x4297…79b2](https://etherscan.io/address/0x4297b5812b4583138889a2d094db0c72eafa79b2) (unknown code status; window profile: no tags, 112 sent to 5 destinations, nonce 17,248 to 17,359) to [0xf90c…6019](https://etherscan.io/address/0xf90caf0030256cf8a2a100a92ede0c5b8c636019) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); contract_like, never_sends, called 21 times in the window). Selector `0xe9ae5c53`, calldata 516 bytes, value 0 ETH, 1 logs, tip 0.027318226 gwei. Largest position change $11,053,315 (USDC at [0xf90c…6019](https://etherscan.io/address/0xf90caf0030256cf8a2a100a92ede0c5b8c636019)); gross $11,053,315; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf90c…6019](https://etherscan.io/address/0xf90caf0030256cf8a2a100a92ede0c5b8c636019) nets USDC -$11,053,315 against [0x37e7…d046](https://etherscan.io/address/0x37e773558f127e782fdf5e4189ba28d67f72d046) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); contract_like, never_sends).

Net flows: [0x37e7…d046](https://etherscan.io/address/0x37e773558f127e782fdf5e4189ba28d67f72d046) +11,054,870.43 USDC ($11,053,315); [0xf90c…6019](https://etherscan.io/address/0xf90caf0030256cf8a2a100a92ede0c5b8c636019) -11,054,870.43 USDC (-$11,053,315).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): The operator EOA 0x4297b5… (nonce 17,263) calls execute with mode 0x…7821 0001 and a single transfer; the account nets −11,053,315.01 USD and the recipient account +11,053,315.01. Twenty transactions in the day use this account for $83.8M, and the recipient account itself sends $79.4M onward in 54 transactions (see 0xc343dc20…). Round amounts, one operator, accounts calling accounts: an institutional custody or treasury system built on smart accounts, moving USDC between its own tiers before external payouts.

Unverified: who operates the account stack. resolve: 0xf90caf00…, 0x37e77355…, 0xafa1b5c1…, 0xd8eafb08… and 0x42bd41e6… all hold 23-byte EIP-7702 delegation designators, so they are delegated EOAs, not contracts.

Proposed type: `smart_account_execute_transfer`. Rule: selector 0xe9ae5c53, only transfer events, every priced leg leaves the called account, no swap. Method: custody_flow (gas payer versus asset owner, leg directions)

### E28. [0x3714…b641](https://etherscan.io/tx/0x37145e97b7d40dcfb6127ad6def2219ab9dad0cdc04503169ddde2ddba59b641): execute() on account 0xd8eafb08… moving 9,998,593.00 USDC to account 0xafa1b5c1… (selected in round_01)

Selected for residue cluster USD #14. Cluster 7496ce9425: 3 transactions from 1 senders, $24,196,595, shape transfers-only, other examples [0xb020…67e9](https://etherscan.io/tx/0xb02081c62cc789639922c6fb61ae56aa1de9988f452954e2f5d1d216c06567e9) [0xc956…f329](https://etherscan.io/tx/0xc956feeb56d1d4737d1938823af7ed113e61adae69cbdd59f8ba79750969f329). Block 25,904,813 at 2026-09-04T15:20:23+00:00, index 105/203, type 0x2, status not fetched. From [0x7259…2b25](https://etherscan.io/address/0x72594c22d0667e3d7124948e2b56cb505e0d2b25) (unknown code status; window profile: no tags, 63 sent to 17 destinations, nonce 4,574 to 4,636) to [0xd8ea…a46b](https://etherscan.io/address/0xd8eafb08da0686e820d1283afb441a1bf8e6a46b) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); never_sends, called 3 times in the window). Selector `0xe9ae5c53`, calldata 516 bytes, value 0 ETH, 1 logs, tip 0.00011 gwei. Largest position change $9,998,593 (USDC at [0xd8ea…a46b](https://etherscan.io/address/0xd8eafb08da0686e820d1283afb441a1bf8e6a46b)); gross $9,998,593; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xd8ea…a46b](https://etherscan.io/address/0xd8eafb08da0686e820d1283afb441a1bf8e6a46b) nets USDC -$9,998,593 against [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); contract_like, never_sends).

Net flows: [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8) +10,000,000.00 USDC ($9,998,593); [0xd8ea…a46b](https://etherscan.io/address/0xd8eafb08da0686e820d1283afb441a1bf8e6a46b) -10,000,000.00 USDC (-$9,998,593).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): A third tier: 0xd8eafb08… feeds 0xafa1b5c1…, which then pays customers (0x0eaf268f…). Three transactions, $24.2M.

Proposed type: `smart_account_execute_transfer`

### E29. [0x536d…48ba](https://etherscan.io/tx/0x536d093b77168769bbfd3fb482401d890a59b5ca59af5210d6db759a6da148ba): liquidity wallet 0x07ae85… (nonce 748,430) pays 121,691.56 USD of WETH into 0x5c7bcd6e…, which unwraps it and pays ETH to the order's recipient; the event names source and destination tokens and both amounts (selected in round_01)

Selected for residue cluster size #12. Cluster f176ea43dc: 49 transactions from 3 senders, $1,691,667, shape WETHWithdrawal; unknown=0x44b559f101f8fbcc8a0ea43fa91a05a729a5ea6e14a7c75aa750374690137208, other examples [0x999f…039d](https://etherscan.io/tx/0x999f8e63a0ba9eb33c6d080cf21eddbbb859a248d3bdaea403364532295e039d) [0xf209…e69d](https://etherscan.io/tx/0xf209a30edffa8bb848375064e17e16a012825b6875a37a87106af150c2c2e69d) [0xeb91…f122](https://etherscan.io/tx/0xeb9118a84b907723b32b68ebd6a042fa985763089806616237980689a375f122). Block 25,904,907 at 2026-09-04T15:39:23+00:00, index 251/267, type 0x2, status not fetched. From [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) (an EOA; window profile: very_high_nonce, 2141 sent to 15 destinations, nonce 746,164 to 748,304) to [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) (a contract of 680 bytes; contract_like, many_sources, never_sends, router_like, called 9900 times in the window). Selector `0xdeff4b24`, calldata 516 bytes, value 0 ETH, 3 logs, tip 0.00001 gwei. Largest position change $121,692 (WETH at [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67)); gross $243,383; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) nets WETH -$121,692 against [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) (a contract of 680 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) -49.601997 WETH (-$121,692); [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) +0.000000 WETH ($0.00).

Event families: ERC20_Transfer_shape ×1, WETHWithdrawal ×1, unknown ×1. Unknown topics: [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) 0x44b559f101f8fbcc… ×1.

Interpretation (LLM, confidence medium): Forty-nine such fills in ETH ($1.7M) and 45 in USDC/USDT ($2.2M) through this contract in the day, all paid by two or three liquidity wallets: a cross-chain transfer service settling on Ethereum out of inventory.

Unverified: the service; the pilot listed 0x07ae85… among hot-wallet candidates.

Proposed type: `contract_unwrap_payout`. Rule: WETH legs into the called contract and a WETH Withdrawal by that contract, no swap. Method: custody_flow

### E30. [0x2c5e…75a3](https://etherscan.io/tx/0x2c5e110f7420ad57334325b50c72cf112dc616c528953837a1f6d91fdf5775a3): execute() on account 0x42bd41e6… paying 5,999,155.80 USDC to a pass-through address (selected in round_01)

Selected for residue cluster USD #4. Cluster 4c679a5a1d: 25 transactions from 1 senders, $64,389,743, shape transfers-only, other examples [0x2ac6…5da3](https://etherscan.io/tx/0x2ac6f4197c45dde5a1bd21a7368385839c65fe16b9ecd8b86e54bcaf750f5da3) [0x768a…7e8a](https://etherscan.io/tx/0x768a6dbdd02034df250ca4c96dc9d5c48bf4f0951c01ea2e94b03c575e0c7e8a) [0x1455…22f8](https://etherscan.io/tx/0x1455fcd8a1fc2f258010f9cbbb9381bc678d29d1520c0770d985220d18c022f8). Block 25,905,098 at 2026-09-04T16:17:59+00:00, index 226/264, type 0x2, status not fetched. From [0x4297…79b2](https://etherscan.io/address/0x4297b5812b4583138889a2d094db0c72eafa79b2) (unknown code status; window profile: no tags, 112 sent to 5 destinations, nonce 17,248 to 17,359) to [0x42bd…4484](https://etherscan.io/address/0x42bd41e6fd5229ec704ab8b03756c00fa8364484) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); contract_like, never_sends, called 25 times in the window). Selector `0xe9ae5c53`, calldata 516 bytes, value 0 ETH, 1 logs, tip 0.01 gwei. Largest position change $5,999,156 (USDC at [0x42bd…4484](https://etherscan.io/address/0x42bd41e6fd5229ec704ab8b03756c00fa8364484)); gross $5,999,156; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x42bd…4484](https://etherscan.io/address/0x42bd41e6fd5229ec704ab8b03756c00fa8364484) nets USDC -$5,999,156 against [0x3e2d…efce](https://etherscan.io/address/0x3e2d2263c9d44f14c113938bbde53e2178a2efce) (unknown code status; pass_through).

Net flows: [0x3e2d…efce](https://etherscan.io/address/0x3e2d2263c9d44f14c113938bbde53e2178a2efce) +6,000,000.00 USDC ($5,999,156); [0x42bd…4484](https://etherscan.io/address/0x42bd41e6fd5229ec704ab8b03756c00fa8364484) -6,000,000.00 USDC (-$5,999,156).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): The recipient 0x3e2d22… carries the pass_through tag (few sources, one destination, net zero over the day): the payout is forwarded on within the day, the signature of an exchange deposit address. Twenty-five transactions and $64.4M through this account.

Proposed type: `smart_account_execute_transfer`

### E31. [0xb32a…c19c](https://etherscan.io/tx/0xb32af7122ecb5aa5d0331785894cee8e0aa4cafcaeb5588ddacd827912e9c19c): token deposit into the same service: 249,964.82 USDC from 0x94810f… with a deposit record (selected in round_01)

Selected for residue cluster size #13. Cluster bb06257e79: 46 transactions from 32 senders, $2,265,516, shape transfers-only; unknown=0x45f377f845e1cc76ae2c08f990e15d58bcb732db46f92a4852b956580c3a162f, other examples [0x5004…d651](https://etherscan.io/tx/0x500458379b99cf28b9f82691b22ff34e1cc6287b35e3dc42cbf1d62dc92ed651) [0xe038…f5ec](https://etherscan.io/tx/0xe0387338c5e52ad69e1d412004f73675cda2b325a21d24ad10016f9c2fdef5ec) [0xe165…2ffd](https://etherscan.io/tx/0xe16522d35160690a23c7bfecc2af5687333e8ddc811a7c984257ec073e6b2ffd). Block 25,905,641 at 2026-09-04T18:07:23+00:00, index 261/527, type 0x2, status not fetched. From [0x9481…b5f1](https://etherscan.io/address/0x94810ffed4cb88e5be4bcb17b7a346c90ec5b5f1) (unknown code status; window profile: no tags, 1 sent to 1 destinations, nonce 8 to 8) to [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends, called 3200 times in the window). Selector `0x9ddf93bb`, calldata 356 bytes, value 0 ETH, 2 logs, tip 1 gwei. Largest position change $249,965 (USDC at [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5)); gross $249,965; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x9481…b5f1](https://etherscan.io/address/0x94810ffed4cb88e5be4bcb17b7a346c90ec5b5f1) nets USDC -$249,965 against [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends).

Net flows: [0x9481…b5f1](https://etherscan.io/address/0x94810ffed4cb88e5be4bcb17b7a346c90ec5b5f1) -250,000.00 USDC (-$249,965); [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) +250,000.00 USDC ($249,965).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) 0x45f377f845e1cc76… ×1.

Interpretation (LLM, confidence high): 

Proposed type: `contract_deposit_recorded`

### E32. [0xf19b…a272](https://etherscan.io/tx/0xf19bce7fb3d6342f5ba89a48af02c4438308df86bba0062b13299ec8735ba272): custody vault sweep: 15,000,000.00 USDC pulled from 0x9ab0f0… into vault 0x100ae042… by sweep(account, token) (selected in round_01)

Selected for residue cluster USD #5. Cluster 66cba131ba: 17 transactions from 1 senders, $43,233,266, shape transfers-only, other examples [0xaeaf…f56a](https://etherscan.io/tx/0xaeafa8befec9f7a7d928d3792598744a87b72a93cefe952cd897e6f60509f56a) [0xbbb0…e44b](https://etherscan.io/tx/0xbbb0357dee81603d9ad816d544f5aaedb06e821e9165539bc2c27a6a68f7e44b) [0x43bf…93e6](https://etherscan.io/tx/0x43bf9d116ac147ca77781862a0c3388d64268cabbdc2773ce51e264ef54c93e6). Block 25,905,955 at 2026-09-04T19:10:23+00:00, index 193/250, type 0x2, status not fetched. From [0xc08f…952f](https://etherscan.io/address/0xc08fb884576cc89957e9058ef11587c468c2952f) (unknown code status; window profile: bot_sender, very_high_nonce, 126 sent to 2 destinations, nonce 218,420 to 218,545) to [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) (a contract (minimal proxy to [0xe8e8…3d7e](https://etherscan.io/address/0xe8e847cf573fc8ed75621660a36affd18c543d7e)) of 45 bytes; contract_like, never_sends, called 81 times in the window). Selector `0x2da03409`, calldata 68 bytes, value 0 ETH, 1 logs, tip 0.000051032 gwei. Largest position change $14,997,890 (USDC at [0x9ab0…9d0a](https://etherscan.io/address/0x9ab0f0d489d6dea8997d903f3d6f5a7fad1e9d0a)); gross $14,997,890; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) nets USDC $14,997,890 against [0x9ab0…9d0a](https://etherscan.io/address/0x9ab0f0d489d6dea8997d903f3d6f5a7fad1e9d0a) (unknown code status; never_sends).

Net flows: [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) +15,000,000.00 USDC ($14,997,890); [0x9ab0…9d0a](https://etherscan.io/address/0x9ab0f0d489d6dea8997d903f3d6f5a7fad1e9d0a) -15,000,000.00 USDC (-$14,997,890).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): Operator 0xc08fb884… (nonce 218,459, bot_sender, very_high_nonce) calls sweep with the client address and the token; the vault pulls the approved balance. No event beyond the Transfer. The vault received $43.2M in 17 such sweeps in the day.

Unverified: the custodian's identity; that 0x100ae042…, 0x367c42a6…, 0x3a5cc868… and 0xa4d65fd5… belong to one operator rests on the shared ABI and shared operator EOAs.

Proposed type: `custody_vault_abi_transfer`. Rule: selector in {0x2da03409, 0x0dcd7a6c, 0x8568523a}, exactly one priced transfer entering or leaving the called contract, only transfer events. Method: custody_flow

### E33. [0x9802…898e](https://etherscan.io/tx/0x98021d12fef21a332be6f984455b78562cae5fcae725b68cd6676fda896d898e): vault 0x5392bd00… hands 9,846,533.00 USDC to the calling hot wallet 0x55fe002a… (nonce 1,679,595) (selected in round_01)

Selected for residue cluster USD #15. Cluster 71ab56d187: 12 transactions from 1 senders, $23,406,339, shape transfers-only, other examples [0xba82…1285](https://etherscan.io/tx/0xba82983e6907188093f2894ead2abcc617b20ebd73c6fb348906f69deb901285) [0xefc2…26ea](https://etherscan.io/tx/0xefc29303b3619bac68a24d2bf5b41bad59f25b53329441b6156279ac050126ea) [0x3d0c…45c5](https://etherscan.io/tx/0x3d0c1dc796565cebfe2441b5434ca48c201d90f581f59e073cde177ed5b045c5). Block 25,905,989 at 2026-09-04T19:17:11+00:00, index 44/232, type 0x2, status not fetched. From [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) (an EOA; window profile: many_sources, very_high_nonce, 983 sent to 22 destinations, nonce 1,679,050 to 1,680,032) to [0x5392…6799](https://etherscan.io/address/0x5392bd00571157fa11103b0ee6d492c9563a6799) (a contract of 957 bytes; never_sends, called 12 times in the window). Selector `0x8568523a`, calldata 68 bytes, value 0 ETH, 1 logs, tip 2.25 gwei. Largest position change $9,845,148 (USDC at [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8)); gross $9,845,148; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) nets USDC $9,845,148 against [0x5392…6799](https://etherscan.io/address/0x5392bd00571157fa11103b0ee6d492c9563a6799) (a contract of 957 bytes; never_sends).

Net flows: [0x5392…6799](https://etherscan.io/address/0x5392bd00571157fa11103b0ee6d492c9563a6799) -9,846,533.00 USDC (-$9,845,148); [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) +9,846,533.00 USDC ($9,845,148).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): The hot wallet refills itself from a vault contract: withdraw(token, amount) with the caller as recipient. Twelve transactions and $23.4M in the day through this vault; the hot wallet's own day net is what the exchange types measure.

Unverified: 0x55fe002a… as an exchange hot wallet is model memory; the day profile tags it many_sources and very_high_nonce. resolve: it is an EOA; the vault 0x5392bd00… is a contract.

Proposed type: `custody_vault_abi_transfer (withdraw to caller)`

### E34. [0x1569…2e60](https://etherscan.io/tx/0x15697afb421d8d980bdabdd7883b94e62bc0ad8aeb9369a747b12b973f152e60): 400 ETH deposited into cross-chain swap service 0xc1d13492… with the memo USDT(TRON)|<TRON address>|0.05|bridgers| (selected in round_01)

Selected for residue cluster size #15. Cluster bd86c440c9: 45 transactions from 37 senders, $2,808,944, shape transfers-only; unknown=0x4e96fb90a89341a56db7ad2bbf04c715bbf20be6a9a9e764671f718c4697649a, other examples [0x3680…b8fc](https://etherscan.io/tx/0x368032e876eb5612e8f7a049e4bc94e0a0a268c78dfbaecc9601367cbf14b8fc) [0x9162…d879](https://etherscan.io/tx/0x9162e1b31c9bff3e997dc4d56fd08675f40edcba4e8e13888bd8ed800555d879) [0x171e…6fda](https://etherscan.io/tx/0x171e77b5c47fb38c4c5067850bdd606654497125b27df42a532f84f9e6a06fda). Block 25,906,063 at 2026-09-04T19:31:59+00:00, index 136/233, type 0x0, status not fetched. From [0x3b7b…ae23](https://etherscan.io/address/0x3b7bd05459171920fb68521effadf2428054ae23) (unknown code status; window profile: fresh, 4 sent to 1 destinations, nonce 0 to 3) to [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends, called 3200 times in the window). Selector `0x16b3b4c2`, calldata 292 bytes, value 400 ETH, 1 logs, tip 0.040500188 gwei. Largest position change $981,873 (ETH at [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5)); gross $981,873; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x3b7b…ae23](https://etherscan.io/address/0x3b7bd05459171920fb68521effadf2428054ae23) nets ETH -$981,873 against [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends).

Net flows: [0x3b7b…ae23](https://etherscan.io/address/0x3b7bd05459171920fb68521effadf2428054ae23) -400.000000 ETH (-$981,873); [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) +400.000000 ETH ($981,873).

Event families: unknown ×1. Unknown topics: [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) 0x4e96fb90a89341a5… ×1.

Interpretation (LLM, confidence high): A fresh wallet (nonce 2) sends 400 ETH ($981,873) with an order string naming the destination token, chain and address and a 0.05 fee parameter; the contract records it. The same contract pays out USDC and USDT by operator calls (0x80651b75…) and receives deposits (0xb32af712…): 45 native deposits ($2.8M), 46 token deposits ($2.3M) and 89 payouts ($14.9M) in the day. This is the mechanism the pilot could not see in two minutes: a swap service that settles off-chain, so its Ethereum legs are one-sided by design.

Unverified: "bridgers" as the SWFT/Bridgers aggregator is model memory; the memo format is read from calldata.

Proposed type: `service_deposit_with_memo`. Rule: calldata holds a printable memo of 8+ characters, value or tokens enter the called contract, the contract emits its own event. Method: custody_flow

### E35. [0x6575…95df](https://etherscan.io/tx/0x657573aa5f60a4f9457152fccecbe1d3e58a11972127fec35f22acd50ad095df): custody vault payout: 27,857,717.28 USDC from vault 0x100ae042… to sibling vault 0x367c42a6… under a signed instruction (deadline 0x6aa45fd9, nonce 0x4650) (selected in round_01)

Selected for residue cluster USD #7. Cluster ba77168c7e: 16 transactions from 1 senders, $41,056,535, shape transfers-only, other examples [0xba95…f7e2](https://etherscan.io/tx/0xba95e65b6285e40810337a38e60142fde6386824da1713d37cb64b2057d8f7e2) [0x293b…19a5](https://etherscan.io/tx/0x293b881681feafefdfe280e82a65fc8f9b0812435d07235dbfc774abff0a19a5) [0x6fca…2976](https://etherscan.io/tx/0x6fca7ca74f278c32938d6d0445325753cd32c9ba93cdf25807de26f42d492976). Block 25,906,249 at 2026-09-04T20:09:11+00:00, index 408/410, type 0x2, status not fetched. From [0xc08f…952f](https://etherscan.io/address/0xc08fb884576cc89957e9058ef11587c468c2952f) (unknown code status; window profile: bot_sender, very_high_nonce, 126 sent to 2 destinations, nonce 218,420 to 218,545) to [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) (a contract (minimal proxy to [0xe8e8…3d7e](https://etherscan.io/address/0xe8e847cf573fc8ed75621660a36affd18c543d7e)) of 45 bytes; contract_like, never_sends, called 81 times in the window). Selector `0x0dcd7a6c`, calldata 324 bytes, value 0 ETH, 1 logs, tip 0.008427751 gwei. Largest position change $27,853,798 (USDC at [0x367c…dca0](https://etherscan.io/address/0x367c42a6f261ec54ffbecf5f41c226be12a3dca0)); gross $27,853,798; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) nets USDC -$27,853,798 against [0x367c…dca0](https://etherscan.io/address/0x367c42a6f261ec54ffbecf5f41c226be12a3dca0) (a contract (minimal proxy to [0xe8e8…3d7e](https://etherscan.io/address/0xe8e847cf573fc8ed75621660a36affd18c543d7e)) of 45 bytes; contract_like, never_sends).

Net flows: [0x100a…29ba](https://etherscan.io/address/0x100ae042ef0ea159ecc3513e9a378ff21f3829ba) -27,857,717.28 USDC (-$27,853,798); [0x367c…dca0](https://etherscan.io/address/0x367c42a6f261ec54ffbecf5f41c226be12a3dca0) +27,857,717.28 USDC ($27,853,798).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): The same operator, 11 nonces later, calls payout(to, amount, token, deadline, nonce); the deadline is a unix time about 51 days ahead (approx) and the nonce a counter, the shape of an off-chain-signed withdrawal instruction. Vault to vault, so an internal rebalance; 0x367c42a6… then pays 0xb5e4d2… $12M with the same selector.

Unverified: as above.

Proposed type: `custody_vault_abi_transfer`

### E36. [0xed6b…6ead](https://etherscan.io/tx/0xed6b0b73bca195fdea578973cbf23c66cb639a1bee8f672c71d075ae9a786ead): 32,694,693.83 USD of cbBTC supplied as collateral on the same fork pool (selected in round_01)

Selected for residue cluster USD #9. Cluster b0c6074ba0: 5 transactions from 4 senders, $40,039,216, shape AaveReserveDataUpdated,AaveScaledMint,AaveSupply,ReserveUsedAsCollateralEnabled, other examples [0xfdcd…31ae](https://etherscan.io/tx/0xfdcdbbe5a5f8b1a660d4abd26e8d988f9136eeb2249008e7481ed1f7f19a31ae) [0x6dd4…bdf0](https://etherscan.io/tx/0x6dd486cffafe143ad682300b1e25b16a47ae4e940fb950987defe35176bbbdf0) [0xa60f…6e9a](https://etherscan.io/tx/0xa60fdaabe5cf58aef756e10797ebf98a453e472642c35d9c9a922bd3720b6e9a). Block 25,906,285 at 2026-09-04T20:16:23+00:00, index 78/370, type 0x2, status not fetched. From [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) (unknown code status; window profile: no tags, 22 sent to 6 destinations, nonce 286 to 307) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0x617ba037`, calldata 132 bytes, value 0 ETH, 6 logs, tip 0.622984489 gwei. Largest position change $32,694,694 (cbBTC at [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6)); gross $32,694,694; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) nets cbBTC -$32,694,694 against [0xb397…c123](https://etherscan.io/address/0xb3973d459df38ae57797811f2a1fd061da1bc123) (unknown code status; never_sends).

Net flows: [0xb397…c123](https://etherscan.io/address/0xb3973d459df38ae57797811f2a1fd061da1bc123) +410.000000 cbBTC ($32,694,694); [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) -410.000000 cbBTC (-$32,694,694).

Unpriced ERC-20 transfers: [0xb397…c123](https://etherscan.io/address/0xb3973d459df38ae57797811f2a1fd061da1bc123) ×1 (largest raw 41000000000).

Event families: ERC20_Transfer_shape ×2, AaveReserveDataUpdated ×1, AaveScaledMint ×1, AaveSupply ×1, ReserveUsedAsCollateralEnabled ×1.

Interpretation (LLM, confidence high): supply() with ReserveUsedAsCollateralEnabled: the position is new for this reserve. Five cbBTC supplies in the day, $40.0M.

Proposed type: `aave_fork_lending_op`

### E37. [0x7025…dd64](https://etherscan.io/tx/0x7025f9ba1dbfa8ecdb945661ba9397bc71a5f885cc69f8d6393c11004d65dd64): 15,000,000.00 USDS borrowed on the fork pool (selected in round_01)

Selected for residue cluster USD #8. Cluster f41c4b5b29: 21 transactions from 14 senders, $40,582,524, shape AaveBorrow,AaveReserveDataUpdated,AaveScaledMint, other examples [0x8dc1…9b65](https://etherscan.io/tx/0x8dc1f91323c387091be13878f0919e4089a9171259af07792f2dbae733669b65) [0x93cb…99cc](https://etherscan.io/tx/0x93cb8b864646701ec64aaa8db893f830c835612c388f06385e768c2b111899cc) [0x0070…2951](https://etherscan.io/tx/0x007011709499e0479f6283785266f1d019147cb8407928908a24c34371f12951). Block 25,906,295 at 2026-09-04T20:18:23+00:00, index 61/429, type 0x2, status not fetched. From [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) (unknown code status; window profile: no tags, 22 sent to 6 destinations, nonce 286 to 307) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0xa415bcad`, calldata 164 bytes, value 0 ETH, 5 logs, tip 0.644044902 gwei. Largest position change $15,000,000 (USDS at [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6)); gross $15,000,000; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) nets USDS $15,000,000 against [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359) (unknown code status; never_sends).

Net flows: [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359) -15,000,000.00 USDS (-$15,000,000); [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) +15,000,000.00 USDS ($15,000,000).

Unpriced ERC-20 transfers: [0x8c14…449e](https://etherscan.io/address/0x8c147debea24fb98ade8dda4bf142992928b449e) ×1 (largest raw 15000000000000000000000000).

Event families: ERC20_Transfer_shape ×2, AaveBorrow ×1, AaveReserveDataUpdated ×1, AaveScaledMint ×1.

Interpretation (LLM, confidence high): borrow() mints variable debt to the borrower and pays USDS from the spToken contract; 21 borrows, $40.6M in the day. Read with the cbBTC and wstETH supplies, the pool is being used to borrow USDS against BTC and ETH collateral at eight-figure size.

Proposed type: `aave_fork_lending_op`

### E38. [0x107f…bb7e](https://etherscan.io/tx/0x107f8d0f8149744d1dcac349e59df45c3476bace47b109bf2447d29fffa8bb7e): the token variant: 172,901.87 USDC from 0x07ae85… to 0x036189…, recorded by 0x5c7bcd6e… (selected in round_01)

Selected for residue cluster size #14. Cluster 5dc1cf7ad6: 45 transactions from 4 senders, $2,175,715, shape transfers-only; unknown=0x44b559f101f8fbcc8a0ea43fa91a05a729a5ea6e14a7c75aa750374690137208, other examples [0x72b5…3ac7](https://etherscan.io/tx/0x72b5a79cebd1a64f16ba6e2bf835d70d2774ebd058a027abff712df444873ac7) [0x27cf…3fce](https://etherscan.io/tx/0x27cf783305997830b34bce837ca8f9d54d16db96f93504188ccdac722e613fce) [0x6752…7e91](https://etherscan.io/tx/0x67524d3f797bc070033008602024868b1fec7dc0a72f526a8c7741610f567e91). Block 25,906,470 at 2026-09-04T20:53:23+00:00, index 217/271, type 0x2, status not fetched. From [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) (an EOA; window profile: very_high_nonce, 2141 sent to 15 destinations, nonce 746,164 to 748,304) to [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) (a contract of 680 bytes; contract_like, many_sources, never_sends, router_like, called 9900 times in the window). Selector `0xdeff4b24`, calldata 516 bytes, value 0 ETH, 2 logs, tip 0.00001 gwei. Largest position change $172,902 (USDC at [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67)); gross $172,902; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) nets USDC -$172,902 against [0x0361…c7cf](https://etherscan.io/address/0x0361897d757d13a4afad64a2e1bc561b96a8c7cf) (unknown code status; hot_wallet, many_sources).

Net flows: [0x0361…c7cf](https://etherscan.io/address/0x0361897d757d13a4afad64a2e1bc561b96a8c7cf) +172,926.20 USDC ($172,902); [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) -172,926.20 USDC (-$172,902).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) 0x44b559f101f8fbcc… ×1.

Interpretation (LLM, confidence medium): The recipient carries hot_wallet and many_sources tags: the transfer lands in another exchange-like wallet, so this is inventory moving between two exchange-connected systems, not a retail withdrawal.

Proposed type: `contract_payout_by_operator`

### E39. [0xdbaf…be49](https://etherscan.io/tx/0xdbaf97b0ec87c6bafcae3d1cb796ba0f593361785a5918c94054742aefd3be49): hot wallet 0x5f65f7b6…'s vault contract pays 1,006,797.66 USDT to a customer address (selected in round_01)

Selected for residue cluster size #6. Cluster 852206e4f2: 64 transactions from 1 senders, $4,441,323, shape transfers-only; unknown=0x18e614c03fae7d4f0ad0790905bc76b8690e946c477b2b8970403bcad27a9b96, other examples [0xb7ca…636c](https://etherscan.io/tx/0xb7ca58a349cefb298ab444b3c4f751366ce3fe0a035a3a04301b4a97aed3636c) [0xd8b9…53d1](https://etherscan.io/tx/0xd8b9e245ae32f971bbe6ef8b1e8bdd1af9040a97172bb84b10ff639d6ee453d1) [0x9b0e…c195](https://etherscan.io/tx/0x9b0e74890ed4e50bd291f2531da25ea55d83b97b17f9fed0975a34b973c2c195). Block 25,906,538 at 2026-09-04T21:06:59+00:00, index 197/249, type 0x2, status not fetched. From [0xf517…5d82](https://etherscan.io/address/0xf51710015536957a01f32558402902a2d9c35d82) (an EOA; window profile: hot_wallet, very_high_nonce, 565 sent to 116 destinations, nonce 678,510 to 679,074) to [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) (a contract of 6,529 bytes; contract_like, never_sends, called 375 times in the window). Selector `0xdfd1fb7a`, calldata 196 bytes, value 0 ETH, 2 logs, tip 0.008817471 gwei. Largest position change $1,006,798 (USDT at [0xecba…ff39](https://etherscan.io/address/0xecbac8014b1dcf9594dab517e9f33715d069ff39)); gross $1,006,798; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) nets USDT -$1,006,798 against [0xecba…ff39](https://etherscan.io/address/0xecbac8014b1dcf9594dab517e9f33715d069ff39) (unknown code status; no tags).

Net flows: [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) -1,006,753.48 USDT (-$1,006,798); [0xecba…ff39](https://etherscan.io/address/0xecbac8014b1dcf9594dab517e9f33715d069ff39) +1,006,753.48 USDT ($1,006,798).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0x5f65…e932](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932) 0x18e614c03fae7d4f… ×1.

Interpretation (LLM, confidence high): The sender is tagged hot_wallet and very_high_nonce and calls its own contract 100 times in the day ($8.4M): an exchange paying withdrawals from a contract-held balance instead of the EOA.

Proposed type: `contract_payout_by_operator`

### E40. [0x373f…259c](https://etherscan.io/tx/0x373f6b4e54191f2751976143b6bb1b5ca554d2664756ed3523e08199c0b5259c): forwarder sweep: 159,977.49 USDC from per-customer forwarder 0xd1b241… (which emits its own event) into hub 0xf4e147db… (selected in round_01)

Selected for residue cluster size #5. Cluster 54df6744fb: 64 transactions from 26 senders, $1,661,320, shape transfers-only; unknown=0xc5a41753c75e78aa0647fa86c7e2223d6c47e245e2f99e78ea1ee8b878a21f4e, other examples [0xa0ac…58d1](https://etherscan.io/tx/0xa0acd504f4dd1c274c41ea2f9cc2a5425d01c9dda48a0cac44399562106958d1) [0x803f…5cdd](https://etherscan.io/tx/0x803fad81b2bea83e8428ddb93d38226d05fd754b91dcd51d328fb48ba0d45cdd) [0x7446…eaf1](https://etherscan.io/tx/0x7446051b5fd4f27d12443c8f9cff6ae24bf5f3378b1df9f25043daa76135eaf1). Block 25,906,748 at 2026-09-04T21:49:11+00:00, index 302/318, type 0x2, status not fetched. From [0x957a…2fd1](https://etherscan.io/address/0x957a670ece294ddf71c6a9c030432db013082fd1) (unknown code status; window profile: bot_sender, 51 sent to 1 destinations, nonce 19,219 to 19,269) to [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) (a contract of 135 bytes; contract_like, many_sources, never_sends, called 1552 times in the window). Selector `0x7b0eb57d`, calldata 196 bytes, value 0 ETH, 2 logs, tip 0 gwei. Largest position change $159,977 (USDC at [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf)); gross $159,977; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) nets USDC $159,977 against [0xd1b2…c884](https://etherscan.io/address/0xd1b2413c59cca16e5569f4c53e097872c1adc884) (unknown code status; never_sends).

Net flows: [0xd1b2…c884](https://etherscan.io/address/0xd1b2413c59cca16e5569f4c53e097872c1adc884) -160,000.00 USDC (-$159,977); [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) +160,000.00 USDC ($159,977).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xd1b2…c884](https://etherscan.io/address/0xd1b2413c59cca16e5569f4c53e097872c1adc884) 0xc5a41753c75e78aa… ×1.

Interpretation (LLM, confidence high): 1,431 distinct forwarders emit this event in the day; 61 sweeps above the threshold, $1.6M, into a hub tagged many_sources.

Proposed type: `forwarder_sweep`. Rule: every priced leg is paid by an address that emits a custom event in the same transaction and is neither the sender nor the destination. Method: custody_flow

### E41. [0x8065…c584](https://etherscan.io/tx/0x80651b7515809c6e0d4a22631352aaf6f8ff51f9941829b38074dfa1298fc584): payout side of the same service: 497,874.64 USDC from 0xc1d13492… to a fresh address, event with token and amount (selected in round_01)

Selected for residue cluster size #3. Cluster d51c9aa044: 90 transactions from 1 senders, $14,991,820, shape transfers-only; unknown=0x7bf0873174a9cc6b28e039b52e74903dd59d650205f32748e3c3dd6b9918ea87, other examples [0xc0e8…ec14](https://etherscan.io/tx/0xc0e8e94ebc4b5bf15fd444af2ca4803ad0b63bfc16ebc7ef09e18aa36852ec14) [0x6b83…a250](https://etherscan.io/tx/0x6b8355da173f706345b82700af0ef6d4f5fc8c4bf753a94f8eca73567d5fa250) [0x6633…03e7](https://etherscan.io/tx/0x66331615631a445f7530e0f2d9616c0e3ce7dbcefdaf7cafbaf835f6ffcb03e7). Block 25,906,829 at 2026-09-04T22:05:23+00:00, index 81/216, type 0x0, status not fetched. From [0x04d6…a303](https://etherscan.io/address/0x04d6f7027ae7ce52654aa21bfb67802f0c9ea303) (unknown code status; window profile: bot_sender, very_high_nonce, 1177 sent to 1 destinations, nonce 55,119 to 56,295) to [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends, called 3200 times in the window). Selector `0xd9caed12`, calldata 100 bytes, value 0 ETH, 2 logs, tip 0.039997925 gwei. Largest position change $497,875 (USDC at [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5)); gross $497,875; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) nets USDC -$497,875 against [0x82f6…66b7](https://etherscan.io/address/0x82f6a4469e952018f19dac627cecc4c597f366b7) (unknown code status; fresh).

Net flows: [0x82f6…66b7](https://etherscan.io/address/0x82f6a4469e952018f19dac627cecc4c597f366b7) +497,944.70 USDC ($497,875); [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) -497,944.70 USDC (-$497,875).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) 0x7bf0873174a9cc6b… ×1.

Interpretation (LLM, confidence high): Operator 0x…(bot_sender, very_high_nonce); the recipient is fresh: a user receiving on Ethereum what they sent on another chain.

Proposed type: `contract_payout_by_operator`

### E42. [0x0eaf…e54c](https://etherscan.io/tx/0x0eaf268feec4878c972f483d4a942672b55056e0bad1893be6009b220c4fe54c): execute() on account 0xafa1b5c1… paying 2,000,087.78 USDT to a quiet address (selected in round_01)

Selected for residue cluster USD #13. Cluster 25817e35b1: 26 transactions from 1 senders, $26,397,153, shape transfers-only, other examples [0x6ac9…ecf0](https://etherscan.io/tx/0x6ac9d7e1ad552544aa359d0eb4b9e7b297a7d61f86f09ecff45bfc410dd3ecf0) [0x7adc…2b2c](https://etherscan.io/tx/0x7adc65bbaea34b87f1862377392f1af9146d10893ddc41d7892c0eceda352b2c) [0x4df1…c8b6](https://etherscan.io/tx/0x4df13e5c1e72b1515b3df4f7643ca8564520ad7a63ac949c5ccaf39ec16ac8b6). Block 25,907,320 at 2026-09-04T23:43:59+00:00, index 293/335, type 0x2, status not fetched. From [0x7259…2b25](https://etherscan.io/address/0x72594c22d0667e3d7124948e2b56cb505e0d2b25) (unknown code status; window profile: no tags, 63 sent to 17 destinations, nonce 4,574 to 4,636) to [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); contract_like, never_sends, called 26 times in the window). Selector `0xe9ae5c53`, calldata 516 bytes, value 0 ETH, 1 logs, tip 0.000075592 gwei. Largest position change $2,000,088 (USDT at [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8)); gross $2,000,088; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8) nets USDT -$2,000,088 against [0x2b46…2277](https://etherscan.io/address/0x2b4693e72624b4bf4cfa5b33e9a09d42b71a2277) (unknown code status; never_sends).

Net flows: [0x2b46…2277](https://etherscan.io/address/0x2b4693e72624b4bf4cfa5b33e9a09d42b71a2277) +2,000,000.00 USDT ($2,000,088); [0xafa1…c7b8](https://etherscan.io/address/0xafa1b5c1b14aeccbaf6e66aa6baca9f59a80c7b8) -2,000,000.00 USDT (-$2,000,088).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): Same ERC-7821 shape in USDT; 26 transactions and $26.4M through this account in the day.

Proposed type: `smart_account_execute_transfer`

### E43. [0x985b…fd7b](https://etherscan.io/tx/0x985b3f156b073026d8f2afcdb8ee430e98d4239a79be428118120b76c924fd7b): wstETH worth 18,625,088.20 USD supplied to the fork pool (selected in round_01)

Selected for residue cluster USD #12. Cluster 8edb90a8fe: 2 transactions from 2 senders, $28,194,267, shape AaveReserveDataUpdated,AaveScaledMint,AaveSupply, other examples [0x006d…4b2e](https://etherscan.io/tx/0x006d7693c27a9396907d236aa338d7bc531a23f0c93bd62f5a828f571ae14b2e). Block 25,907,591 at 2026-09-05T00:38:23+00:00, index 76/270, type 0x2, status not fetched. From [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) (unknown code status; window profile: no tags, 22 sent to 3 destinations, nonce 54 to 75) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0x617ba037`, calldata 132 bytes, value 0 ETH, 6 logs, tip 0.15 gwei. Largest position change $18,625,088 (wstETH at [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514)); gross $18,625,088; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) nets wstETH -$18,625,088 against [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9) (unknown code status; never_sends).

Net flows: [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9) +6,100.00 wstETH ($18,625,088); [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) -6,100.00 wstETH (-$18,625,088).

Unpriced ERC-20 transfers: [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9) ×1 (largest raw 6100000001000013284533).

Event families: ERC20_Transfer_shape ×2, AaveReserveDataUpdated ×1, AaveScaledMint ×1, AaveSupply ×1, Approval ×1.

Interpretation (LLM, confidence high): The supply half of a rotation: the same size class as the withdrawal above, a few hours apart, consistent with a position being moved or re-collateralised.

Proposed type: `aave_fork_lending_op`

### E44. [0xc39a…4015](https://etherscan.io/tx/0xc39ab8b0519b65a59bfe89d7057b3708b0f5092ba12289a9af2eaa9359574015): payout processor: 0xf5e10380… pays 364,135.25 USDT to a fresh address with a record (id, account number 263,449, beneficiary) from 0xcd351d36… (selected in round_01)

Selected for residue cluster size #2. Cluster 712a936e9f: 112 transactions from 37 senders, $7,554,477, shape transfers-only; unknown=0xe2688b6900b89a8dc9b790e8ad7e598062004db7e424b7781144ffccf76c734b, other examples [0x26e5…1e3d](https://etherscan.io/tx/0x26e52a99f68ef949915bf3690be9676fb842e3801e998f43b07cb6d15db91e3d) [0x5eb3…82cf](https://etherscan.io/tx/0x5eb316cd8725065807806343acd0da535b3c229e311b180b1f4a79becd2682cf) [0x55de…6ed9](https://etherscan.io/tx/0x55de2c49e7e8d069da6d7a6d610d29d20610586b83e5c43a2a526889b69d6ed9). Block 25,907,774 at 2026-09-05T01:15:11+00:00, index 261/332, type 0x2, status not fetched. From [0x6622…7a5e](https://etherscan.io/address/0x6622da9ac8a8ab8664597f926370bb1eaead7a5e) (unknown code status; window profile: no tags, 5 sent to 1 destinations, nonce 1,295 to 1,299) to [0xf5e1…2bcc](https://etherscan.io/address/0xf5e10380213880111522dd0efd3dbb45b9f62bcc) (a contract of 19,788 bytes; contract_like, many_sources, never_sends, called 473 times in the window). Selector `0x5f8c0f9a`, calldata 388 bytes, value 0 ETH, 2 logs, tip 0.000032265 gwei. Largest position change $364,151 (USDT at [0xf5e1…2bcc](https://etherscan.io/address/0xf5e10380213880111522dd0efd3dbb45b9f62bcc)); gross $364,151; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf5e1…2bcc](https://etherscan.io/address/0xf5e10380213880111522dd0efd3dbb45b9f62bcc) nets USDT -$364,151 against [0xa296…e2ae](https://etherscan.io/address/0xa296273627b59951affa1a77a80ce57ae85ae2ae) (unknown code status; fresh).

Net flows: [0xa296…e2ae](https://etherscan.io/address/0xa296273627b59951affa1a77a80ce57ae85ae2ae) +364,135.25 USDT ($364,151); [0xf5e1…2bcc](https://etherscan.io/address/0xf5e10380213880111522dd0efd3dbb45b9f62bcc) -364,135.25 USDT (-$364,151).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xcd35…08be](https://etherscan.io/address/0xcd351d3626dc244730796a3168d315168ebf08be) 0xe2688b6900b89a8d… ×1.

Interpretation (LLM, confidence high): 112 payouts from 37 operator EOAs, $7.6M, USDC and USDT, recipients mostly fresh: the withdrawal side of a custodial service.

Unverified: the operator.

Proposed type: `contract_payout_by_operator`. Rule: every priced leg leaves the called contract to addresses other than the sender, only transfer events. Method: custody_flow

### E45. [0x5cad…963c](https://etherscan.io/tx/0x5cade5c4bf71de94d05c4baf4a9213270f32208ddc23e7c3ef7690cf09fa963c): relayed payment batch with 32-byte references: 500,095.41 USDC from 0x977e5d… and 357.00 USDC from 0x68cf00… to 0xd15e62…, each followed by a record event from the contract (selected in round_01)

Selected for residue cluster size #8. Cluster da4dc36eaa: 56 transactions from 2 senders, $6,678,026, shape transfers-only; unknown=0xbb062c23e818de8ea9c157514eb098052cf36904bbe431cd50d4ec92264ca3ac, other examples [0xce26…c781](https://etherscan.io/tx/0xce26d8f2f8c5d8270a484e125a614e1d441dcddabb2136c25128354bdff3c781) [0xc4a1…3852](https://etherscan.io/tx/0xc4a11b3c154f1e7852cad136f69ec4154b5ea8ed4aa973689b5c39c408f53852) [0xcf4c…f9f3](https://etherscan.io/tx/0xcf4c6608910ebcae95b00017723ba92263c803d54047645a4aa1b77dfed2f9f3). Block 25,908,848 at 2026-09-05T04:50:11+00:00, index 266/295, type 0x2, status not fetched. From [0xfac9…986a](https://etherscan.io/address/0xfac9a7b366c2c65a9093379443be1443217c986a) (unknown code status; window profile: bot_sender, 120 sent to 3 destinations, nonce 2,551 to 2,670) to [0xec00…a6df](https://etherscan.io/address/0xec000064576f9c95a8623bc0eff3db6d296ea6df) (a contract of 22,537 bytes; contract_like, never_sends, called 307 times in the window). Selector `0x7af10029`, calldata 900 bytes, value 0 ETH, 4 logs, tip 0.001 gwei. Largest position change $500,382 (USDC at [0xd15e…76c7](https://etherscan.io/address/0xd15e62e64c1265dfb753ed6e7c76cb5ff8f276c7)); gross $500,382; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xd15e…76c7](https://etherscan.io/address/0xd15e62e64c1265dfb753ed6e7c76cb5ff8f276c7) nets nothing priced against [0x977e…876c](https://etherscan.io/address/0x977e5d181cb1b55a56d43c2d95150e54c805876c) (unknown code status; never_sends).

Net flows: [0xd15e…76c7](https://etherscan.io/address/0xd15e62e64c1265dfb753ed6e7c76cb5ff8f276c7) +500,452.41 USDC ($500,382); [0x977e…876c](https://etherscan.io/address/0x977e5d181cb1b55a56d43c2d95150e54c805876c) -500,095.41 USDC (-$500,025); [0x68cf…8df8](https://etherscan.io/address/0x68cf003fa320c27e4ae65a52ae153a8486a68df8) -357.001440 USDC (-$356.95).

Event families: ERC20_Transfer_shape ×2, unknown ×2. Unknown topics: [0xec00…a6df](https://etherscan.io/address/0xec000064576f9c95a8623bc0eff3db6d296ea6df) 0xbb062c23e818de8e… ×2.

Interpretation (LLM, confidence high): The sender 0xfac9a7b3… (bot_sender) owns none of the funds; the contract moves approved balances and emits (recipient, reference) per transfer. Fifty-six batches from two operators, $6.7M in the day: a payment rail settling instructions on approved balances, or an exchange paying withdrawals from customer sub-accounts.

Unverified: the service behind 0xec000064…; the references are opaque.

Proposed type: `relayed_payment_recorded`. Rule: only transfer events plus custom events from the called contract; every priced leg is third party to third party. Method: custody_flow

### E46. [0x124f…9130](https://etherscan.io/tx/0x124fd09b51d67724728b03174313724b6158e3c2d4f0c955dc45e0fdca4c9130): exchange hot wallet 0x9642b2… paying five withdrawals (1,200,052.57 USDT the largest) through payout contract 0xfaf17849…, one record event per payment (selected in round_01)

Selected for residue cluster size #10. Cluster 39aa199fbd: 52 transactions from 1 senders, $6,733,326, shape transfers-only; unknown=0xb3349ab5b902cf72320ce6e5e6112326ffdf4011716c381b8820cda70d1f0bc2, other examples [0x9b19…a675](https://etherscan.io/tx/0x9b19ac5a7d0dbe3a759c3b4c2d645124cdc0b80feda075715a3180fb420ca675) [0x29fe…c04e](https://etherscan.io/tx/0x29fe6982260e0059689bca889b2c621a1b5d4d1154d21f78fdb497846cdcc04e) [0x2a6e…e113](https://etherscan.io/tx/0x2a6ea04fbf11ee6ebe4f9eea9572478b229308290935394b0c5d7bad88afe113). Block 25,909,232 at 2026-09-05T06:07:11+00:00, index 33/289, type 0x0, status not fetched. From [0x9642…5d4e](https://etherscan.io/address/0x9642b23ed1e01df1092b92641051881a322f5d4e) (an EOA; window profile: hot_wallet, many_sources, very_high_nonce, 4078 sent to 1276 destinations, nonce 3,477,038 to 3,481,115) to [0xfaf1…83f8](https://etherscan.io/address/0xfaf17849fb05a11a4e233f221bac99ca43fc83f8) (a contract of 170 bytes; contract_like, never_sends, called 567 times in the window). Selector `0x6b13fcb1`, calldata 708 bytes, value 0 ETH, 12 logs, tip 0.80973417 gwei. Largest position change $1,200,093 (USDT at [0x9642…5d4e](https://etherscan.io/address/0x9642b23ed1e01df1092b92641051881a322f5d4e)); gross $1,200,430; swaps 0 in 0 pools; 3 distinct recipients. Principal [0x9642…5d4e](https://etherscan.io/address/0x9642b23ed1e01df1092b92641051881a322f5d4e) nets USDC -$336.95, USDT -$1,200,093 against [0xf8f0…59ef](https://etherscan.io/address/0xf8f01185ac7a0de8512683a00eb1e30d7adb59ef) (unknown code status; pass_through).

Net flows: [0x9642…5d4e](https://etherscan.io/address/0x9642b23ed1e01df1092b92641051881a322f5d4e) -1,200,040.75 USDT (-$1,200,093); [0xf8f0…59ef](https://etherscan.io/address/0xf8f01185ac7a0de8512683a00eb1e30d7adb59ef) +1,199,999.91 USDT ($1,200,053); [0x9642…5d4e](https://etherscan.io/address/0x9642b23ed1e01df1092b92641051881a322f5d4e) -337.000000 USDC (-$336.95); [0xbd94…4e76](https://etherscan.io/address/0xbd94a53bf7f3d4b168db4a23733c7b9599d44e76) +337.000000 USDC ($336.95); [0x848c…3213](https://etherscan.io/address/0x848c4a304ba3b4a3f563bb80c8ccbf5ff8243213) +40.840854 USDT ($40.84).

Unpriced ERC-20 transfers: [0xbba3…3099](https://etherscan.io/address/0xbba39fd2935d5769116ce38d46a71bde9cf03099) ×1 (largest raw 1400000000000000000000), [0x455e…c3f6](https://etherscan.io/address/0x455e53cbb86018ac2b8092fdcd39d8444affc3f6) ×1 (largest raw 1669403000000000032768).

Event families: ERC20_Transfer_shape ×5, unknown ×5, Approval ×2. Unknown topics: [0xfaf1…83f8](https://etherscan.io/address/0xfaf17849fb05a11a4e233f221bac99ca43fc83f8) 0xb3349ab5b902cf72… ×5.

Interpretation (LLM, confidence high): The hot wallet's own tokens move by transferFrom through the helper; 58 batches, $7.5M in the day.

Unverified: the exchange.

Proposed type: `sender_tokens_via_contract (fewer than five recipients per batch fall below batch_payout)`

### E47. [0xef15…9943](https://etherscan.io/tx/0xef15784a397fb94bb50e9078a45fbe15c3e2dfc20f131491ce32c4249fac9943): 100 ETH deposited into 0xd90e2f92… with a 32-byte recipient and a sequenced message (counter 48,280) from 0xa160cd… (selected in round_01)

Selected for residue cluster size #4. Cluster 2dc868ee9b: 74 transactions from 8 senders, $13,052,230, shape transfers-only; unknown=0xa945e51eec50ab98c161376f0db4cf2aeba3ec92755fe2fcd388bdbbb80ff196,0xfa28df43db3553771f7209dcef046f3bdfea15870ab625dcda30ac58b82b4008, other examples [0x332a…af2e](https://etherscan.io/tx/0x332a90ba4f0e4c806c12ce0d54b8d62bc5973a691d66f55b6eb0305ef193af2e) [0x61c7…34b7](https://etherscan.io/tx/0x61c78cade3ec8fbcd84a36d5dd11b3185da4d460e752a4a565edaaffc4cc34b7) [0x8655…e715](https://etherscan.io/tx/0x8655f098579fab3522acbd46279411b9e72fb62e68e91b6fbf9636659edee715). Block 25,909,501 at 2026-09-05T07:00:59+00:00, index 10/210, type 0x2, status not fetched. From [0x7b4f…4e20](https://etherscan.io/address/0x7b4f24a4522bc2aee9d1686ffb7d6c9dac514e20) (unknown code status; window profile: no tags, 6 sent to 2 destinations, nonce 5 to 11) to [0xd90e…f31b](https://etherscan.io/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b) (a contract of 5,725 bytes; contract_like, never_sends, called 381 times in the window). Selector `0x13d98d13`, calldata 132 bytes, value 100 ETH, 2 logs, tip 3 gwei. Largest position change $245,487 (ETH at [0xd90e…f31b](https://etherscan.io/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b)); gross $245,487; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x7b4f…4e20](https://etherscan.io/address/0x7b4f24a4522bc2aee9d1686ffb7d6c9dac514e20) nets ETH -$245,487 against [0xd90e…f31b](https://etherscan.io/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b) (a contract of 5,725 bytes; contract_like, never_sends).

Net flows: [0x7b4f…4e20](https://etherscan.io/address/0x7b4f24a4522bc2aee9d1686ffb7d6c9dac514e20) -100.000000 ETH (-$245,487); [0xd90e…f31b](https://etherscan.io/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b) +100.000000 ETH ($245,487).

Event families: unknown ×2. Unknown topics: [0xa160…f291](https://etherscan.io/address/0xa160cdab225685da1d56aa342ad8841c3b53f291) 0xa945e51eec50ab98… ×1; [0xd90e…f31b](https://etherscan.io/address/0xd90e2f925da726b50c4ed8d0fb90ad053324f31b) 0xfa28df43db355377… ×1.

Interpretation (LLM, confidence medium): Sender nonce 11, tip 3 gwei. Seventy-four deposits of round ETH amounts from eight senders, $13.1M, all into this contract: a bridge-like deposit whose destination is off Ethereum. The generic type records the deposit; the protocol is not identified.

Unverified: which chain or service the 32-byte recipient belongs to; the counter-and-timestamp event is the shape of a bridge message queue.

Proposed type: `contract_deposit_recorded`. Rule: value or tokens enter the called contract only, a custom event is emitted, no swap. Method: custody_flow

### E48. [0x655e…a55d](https://etherscan.io/tx/0x655eb229bb8dbc8c3e62be5f6c53b617351698ca5d7ac3853da6ab8e284aa55d): the same venue through entry contract 0xd82461784e…: 14,782.01 USDT in and 14,781.24 out with a 0.76 USDT fee (selected in round_01)

Selected for residue cluster size #11. Cluster 4dd8519c8e: 50 transactions from 1 senders, $717,300, shape transfers-only; unknown=0x3ad61047071575417c75e3311e5d46ff042e292b5dd8769ff18b4b254098ca7a,0x3f18354abbd5306dd1665c2c90f614a4559e39dd620d04fbe5458e613b6588f3,0x54bc5c027d15d7aa8ae083f994ab4411d2f223291672ecd3a344f3d92dcaf8b2,0x94f12331a652cdc1d25595d1aefbc92047ce9a15c97ee89d37a0a6b46943b8f0, other examples [0xd976…faa1](https://etherscan.io/tx/0xd97617df9f537369e19316ed4f419304379c5d7010d6608c0feeaf760521faa1) [0x0530…24b9](https://etherscan.io/tx/0x0530afa2678f1d84bcc0606b1a5239ec5c4115d455731d9e9688df39bf5424b9) [0x9b95…285c](https://etherscan.io/tx/0x9b95204ce3a9eea49e0b194eee23cc8e8e607c54062ef496fda7c8c9d35b285c). Block 25,909,909 at 2026-09-05T08:23:47+00:00, index 108/396, type 0x2, status not fetched. From [0x0e00…c0e4](https://etherscan.io/address/0x0e0052a184fd59c6b7e1e99d739802ecb3aec0e4) (unknown code status; window profile: no tags, 1756 sent to 5 destinations, nonce 43,287 to 45,042) to [0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272) (a contract of 141 bytes; contract_like, never_sends, router_like, called 1802 times in the window). Selector `0xbad401db`, calldata 1,764 bytes, value 8.32E-16 ETH, 25 logs, tip 0.05 gwei. Largest position change $14,805 (IMPL:0x1111…c302 at [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950)); gross $73,978; swaps 0 in 0 pools; 5 distinct recipients. Principal [0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272) nets USDT $0.76 against [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950) (unknown code status; no tags).

Net flows: [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950) -162,432.81 IMPL:0x1111…c302 (-$14,805); [0x21cb…a67e](https://etherscan.io/address/0x21cb492117ba484303da6108c31c6c12f573a67e) +162,432.40 IMPL:0x1111…c302 ($14,805); [0x21cb…a67e](https://etherscan.io/address/0x21cb492117ba484303da6108c31c6c12f573a67e) -14,781.36 USDT (-$14,782); [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950) +14,780.56 USDT ($14,781); [0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272) +0.764849 USDT ($0.76); [0x8063…614a](https://etherscan.io/address/0x8063d4faf54bf8c898dc6ddc689c76ab12b4614a) +0.406082 IMPL:0x1111…c302 ($0.04); [0x8063…614a](https://etherscan.io/address/0x8063d4faf54bf8c898dc6ddc689c76ab12b4614a) +0.036951 USDT ($0.04); [0x0e00…c0e4](https://etherscan.io/address/0x0e0052a184fd59c6b7e1e99d739802ecb3aec0e4) -0.000000 ETH ($0.00).

Event families: Approval ×9, unknown ×9, ERC20_Transfer_shape ×7. Unknown topics: [0x1111…a90a](https://etherscan.io/address/0x1111113ccf1426a8e30e2bff5e005d929bf6a90a) 0x3ad6104707157541… ×4; [0x1111…a90a](https://etherscan.io/address/0x1111113ccf1426a8e30e2bff5e005d929bf6a90a) 0x3f18354abbd5306d… ×2; [0x1111…c0de](https://etherscan.io/address/0x111111338c5091e8440b67b168bae16a668ac0de) 0x54bc5c027d15d7aa… ×2; [0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272) 0x94f12331a652cdc1… ×1.

Interpretation (LLM, confidence medium): Fifty transactions and $716k; the dust ETH value (8.3e-16) and the 1inch-style events match the previous entry.

Proposed type: `trade_against_unpriced_token`

### E49. [0x434e…f85f](https://etherscan.io/tx/0x434ee6264b59a0dfe53ce517f0132eb61eadc700f3267bf35f512f22500df85f): 10,003,810.42 USDS repaid with repay() (selected in round_01)

Selected for residue cluster USD #10. Cluster 0c3fdc2742: 9 transactions from 4 senders, $39,112,908, shape AaveRepay,AaveReserveDataUpdated,AaveScaledBurn, other examples [0x65fb…91e6](https://etherscan.io/tx/0x65fb58e517c2c60a8ff5c251139f7d6ec528f7d7bfcbe7b9642f0b7736a391e6) [0xbf9a…a197](https://etherscan.io/tx/0xbf9a027b3ba02b4e7b38ba77b48cc2b28d222b42e1b113e2c27da62c68d9a197) [0x582b…f943](https://etherscan.io/tx/0x582bda07f0aba02e4b1646b3c1c8716731e2ff92f9b1efe5bf2f7a62d9e2f943). Block 25,909,918 at 2026-09-05T08:25:35+00:00, index 70/215, type 0x2, status not fetched. From [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) (unknown code status; window profile: no tags, 22 sent to 3 destinations, nonce 54 to 75) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0x573ade81`, calldata 132 bytes, value 0 ETH, 5 logs, tip 0.15 gwei. Largest position change $10,003,810 (USDS at [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359)); gross $10,003,810; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) nets USDS -$10,003,810 against [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359) (unknown code status; never_sends).

Net flows: [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) -10,003,810.42 USDS (-$10,003,810); [0xc02a…4359](https://etherscan.io/address/0xc02ab1a5eaa8d1b114ef786d9bde108cd4364359) +10,003,810.42 USDS ($10,003,810).

Unpriced ERC-20 transfers: [0x8c14…449e](https://etherscan.io/address/0x8c147debea24fb98ade8dda4bf142992928b449e) ×1 (largest raw 10003761294592791645702152).

Event families: ERC20_Transfer_shape ×2, AaveRepay ×1, AaveReserveDataUpdated ×1, AaveScaledBurn ×1.

Interpretation (LLM, confidence high): Nine repays through selector 0x573ade81, $39.1M.

Proposed type: `aave_fork_lending_op`

### E50. [0xa05d…9320](https://etherscan.io/tx/0xa05d548304eb47de4314bf4812f4961c93f51402547bbc53626b9f04ceba9320): wstETH worth 18,319,758.88 USD withdrawn from the fork pool (selected in round_01)

Selected for residue cluster USD #3. Cluster 48a3edd075: 6 transactions from 3 senders, $66,781,294, shape AaveReserveDataUpdated,AaveScaledBurn,AaveWithdraw, other examples [0x4a72…9f39](https://etherscan.io/tx/0x4a72eef88567dec8e43ac34e6ee62543be05347bb7af5ffb684f8e99bde59f39) [0x9bc3…ea16](https://etherscan.io/tx/0x9bc3c90fde11cf942aaba19d863baa5262395d690f96d2701cd04ba1f365ea16) [0x6141…33f5](https://etherscan.io/tx/0x6141cf404019eda6030ceea1b86da3519abc81300f953239388b0515718d33f5). Block 25,909,920 at 2026-09-05T08:25:59+00:00, index 77/342, type 0x2, status not fetched. From [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) (unknown code status; window profile: no tags, 22 sent to 3 destinations, nonce 54 to 75) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0x69328dec`, calldata 100 bytes, value 0 ETH, 5 logs, tip 0.15 gwei. Largest position change $18,319,759 (wstETH at [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514)); gross $18,319,759; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) nets wstETH $18,319,759 against [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9) (unknown code status; never_sends).

Net flows: [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9) -6,000.00 wstETH (-$18,319,759); [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) +6,000.00 wstETH ($18,319,759).

Unpriced ERC-20 transfers: [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9) ×1 (largest raw 5999999999999999842189).

Event families: ERC20_Transfer_shape ×2, AaveReserveDataUpdated ×1, AaveScaledBurn ×1, AaveWithdraw ×1.

Interpretation (LLM, confidence high): withdraw() burns the scaled aToken and returns wstETH; six withdrawals, $66.8M.

Proposed type: `aave_fork_lending_op`

### E51. [0xc5bb…0918](https://etherscan.io/tx/0xc5bb5b7625dcf10082435ea1c39aa2a9c12ea48cf52ea41a41dada30fd2c0918): resolver-executed fill: 0x21cb49… pays 14,341.10 USDT through 0x77778576… and 0xe01ecf… delivers 157,602.94 1INCH (unpriced), with settlement events from 0x1111113ccf… per account and token (selected in round_01)

Selected for residue cluster size #1. Cluster 3bdf9a2aed: 129 transactions from 2 senders, $1,808,933, shape transfers-only; unknown=0x0361623e26af064e2386d06ed99a1614502fd38c9a9d0213383638d3ee415b53,0x3ad61047071575417c75e3311e5d46ff042e292b5dd8769ff18b4b254098ca7a,0x3f18354abbd5306dd1665c2c90f614a4559e39dd620d04fbe5458e613b6588f3,0x45459b564f95bd7b130b9f63294e652c40d23fd67d26360dff8f6d8cf55ca323,0x54bc5c027d15d7aa8ae083f994ab4411d2f223291672ecd3a344f3d92dcaf8b2, other examples [0x097d…0408](https://etherscan.io/tx/0x097dd0f2896f63434291e39800acd2de94a940542e405644a9761c6144840408) [0x3a97…4cbc](https://etherscan.io/tx/0x3a9723d0b902304bc1e091432799fed3e416bba47dff1f37f0d08bc75bae4cbc) [0xcc00…2626](https://etherscan.io/tx/0xcc00a559e0441a1ece56c821c3b687fc650593d2727102d73bdd030e723e2626). Block 25,909,925 at 2026-09-05T08:26:59+00:00, index 143/280, type 0x2, status not fetched. From [0xf4d0…e0bf](https://etherscan.io/address/0xf4d02174bdaa72dcd126da640cb57411aadde0bf) (unknown code status; window profile: bot_sender, 310 sent to 1 destinations, nonce 10,390 to 10,699) to [0x7777…df17](https://etherscan.io/address/0x7777857616fb37f0cfa262e9bb945e828312df17) (a contract of 17,769 bytes; contract_like, never_sends, called 490 times in the window). Selector `0x3fa72595`, calldata 1,892 bytes, value 0 ETH, 27 logs, tip 0.019214264 gwei. Largest position change $14,365 (IMPL:0x1111…c302 at [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950)); gross $57,413; swaps 0 in 0 pools; 5 distinct recipients. Principal [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950) nets nothing priced against [0x7777…df17](https://etherscan.io/address/0x7777857616fb37f0cfa262e9bb945e828312df17) (a contract of 17,769 bytes; contract_like, never_sends).

Net flows: [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950) -157,602.94 IMPL:0x1111…c302 (-$14,365); [0x21cb…a67e](https://etherscan.io/address/0x21cb492117ba484303da6108c31c6c12f573a67e) +157,594.39 IMPL:0x1111…c302 ($14,364); [0x21cb…a67e](https://etherscan.io/address/0x21cb492117ba484303da6108c31c6c12f573a67e) -14,341.10 USDT (-$14,342); [0xe01e…5950](https://etherscan.io/address/0xe01ecff2f6c4f2416e83e6861e8abf79b1c95950) +14,341.06 USDT ($14,342); [0x6f52…1065](https://etherscan.io/address/0x6f52a1decc650b28435ddc9793dc85f869061065) +8.154693 IMPL:0x1111…c302 ($0.74); [0x8063…614a](https://etherscan.io/address/0x8063d4faf54bf8c898dc6ddc689c76ab12b4614a) +0.393987 IMPL:0x1111…c302 ($0.04); [0x8063…614a](https://etherscan.io/address/0x8063d4faf54bf8c898dc6ddc689c76ab12b4614a) +0.035852 USDT ($0.04); [0x7777…df17](https://etherscan.io/address/0x7777857616fb37f0cfa262e9bb945e828312df17) +0.000000 IMPL:0x1111…c302 ($0.00).

Event families: unknown ×11, Approval ×9, ERC20_Transfer_shape ×7. Unknown topics: [0x1111…a90a](https://etherscan.io/address/0x1111113ccf1426a8e30e2bff5e005d929bf6a90a) 0x3ad6104707157541… ×4; [0x1111…a90a](https://etherscan.io/address/0x1111113ccf1426a8e30e2bff5e005d929bf6a90a) 0x3f18354abbd5306d… ×2; [0x1111…c0de](https://etherscan.io/address/0x111111338c5091e8440b67b168bae16a668ac0de) 0x54bc5c027d15d7aa… ×2; [0x7777…df17](https://etherscan.io/address/0x7777857616fb37f0cfa262e9bb945e828312df17) 0x0361623e26af064e… ×2; [0x7777…df17](https://etherscan.io/address/0x7777857616fb37f0cfa262e9bb945e828312df17) 0x45459b564f95bd7b… ×1.

Interpretation (LLM, confidence medium): The tx sender 0xf4d02174… (bot_sender) is a resolver; the taker's USDT reaches the maker net of 0.035852 USDT sent to 0x8063d4… as a fee, and the maker's 1INCH goes to the contract and on to the taker in the later logs. Implied price about 0.091 USDT per 1INCH (approx). 129 such fills through 0x77778576… in the day from two resolvers, all USDT; the registry now types them but cannot value the token side.

Unverified: 0x1111113ccf… and 0x77778576… as parts of 1inch's current fill infrastructure is model memory from the address prefix; the 1INCH token address 0x111111111117dc0aa78b770fa6a738034120c302 is model memory.

Proposed type: `trade_against_unpriced_token`. Rule: no registered swap event, no flash loan; a net payer of a priced asset receives an unpriced token, or a net receiver of a priced asset sends one. Method: swap (pairs show the priced side only)

### E52. [0xcb17…75b4](https://etherscan.io/tx/0xcb17d7ee45df09406014432b9629621720bf1d6294b0913b30dff97900d875b4): delegated EOA 0x63d55efd… calling itself to settle USDT, USDC and WETH between four sub-accounts (selected in round_02)

Selected for residue cluster size #4. Cluster f73234740b: 19 transactions from 1 senders, $316,760, shape transfers-only, other examples [0xaaa9…1bdd](https://etherscan.io/tx/0xaaa92aaf4fc5239d456df47baa070fd2dabed0e97a1070e3cd22fd52e58c1bdd) [0x87b2…eead](https://etherscan.io/tx/0x87b2bd95f1528ca5e91072bce8044b3da1c3e32e4626a5570483915a2cc0eead) [0x1ef5…e225](https://etherscan.io/tx/0x1ef512589d2d8c8a809baad4662ba80dc3a7c05a2165d5207f1052eb1772e225). Block 25,904,954 at 2026-09-04T15:48:47+00:00, index 155/303, type 0x2, status not fetched. From [0x63d5…11cc](https://etherscan.io/address/0x63d55efde46799dc91cfa16c4be443ada07e11cc) (an EOA delegated (EIP-7702) to [0x1c68…2158](https://etherscan.io/address/0x1c6841ea2df98fe8423bc4808e72e16461012158); window profile: bot_sender, 385 sent to 1 destinations, nonce 18,302 to 18,686) to [0x63d5…11cc](https://etherscan.io/address/0x63d55efde46799dc91cfa16c4be443ada07e11cc) (an EOA delegated (EIP-7702) to [0x1c68…2158](https://etherscan.io/address/0x1c6841ea2df98fe8423bc4808e72e16461012158); bot_sender, called 388 times in the window). Selector `0xdc248ef3`, calldata 1,924 bytes, value 0 ETH, 10 logs, tip 0.02 gwei. Largest position change $29,270 (USDT at [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27)); gross $70,851; swaps 0 in 0 pools; 4 distinct recipients. Principal [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) nets nothing priced against [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) (an EOA delegated (EIP-7702) to [0x3525…d1ff](https://etherscan.io/address/0x3525f1c4ba12279747fb7f06a2291d406508d1ff); contract_like, never_sends, router_like).

Net flows: [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) +29,268.34 USDT ($29,270); [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) -27,116.61 USDT (-$27,118); [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) -17,663.41 USDC (-$17,661); [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) +5.546816 WETH ($13,608); [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) +13,508.11 USDC ($13,506); [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) -4.730555 WETH (-$11,606); [0x111f…dcd4](https://etherscan.io/address/0x111f686ff7e5361e87d632376a82d894a33fdcd4) -8,309.33 USDT (-$8,310); [0x9303…6e7d](https://etherscan.io/address/0x9303d901bbe63310ae5adbb2f3b6d78f82776e7d) +6,157.60 USDT ($6,158).

Event families: ERC20_Transfer_shape ×10.

Interpretation (LLM, confidence high): An EOA can only emit logs when calling itself if it carries an EIP-7702 delegation. Nineteen self-calls, $317k of largest changes, moving inventory among 0x111f68…, 0x9303d9…, 0xe31950… and 0xe6f87b…: a market maker netting positions.

Unverified: nothing further. resolve: 0x63d55efd… holds a 23-byte designator delegating to 0x1c6841ea….

Proposed type: `delegated_account_self_call`. Rule: destination equals sender and at least one log. Method: custody_flow

### E53. [0x7170…3936](https://etherscan.io/tx/0x717031756cf5facb0be14412d0c1efc1bc1bf3c8ebfbf01bc7c4d89343363936): sUSDe cooldown claim: unstake(receiver) releases 10,033,001.47 USDe from silo 0x7fc7c91d… to 0xf078969e… (selected in round_02)

Selected for residue cluster size #2, residue cluster USD #1. Cluster 9370f771cb: 24 transactions from 24 senders, $17,908,746, shape transfers-only, other examples [0x31ca…5e60](https://etherscan.io/tx/0x31ca5a0b7b36e65d9f053434242f42d39c0cb2a585caa7d601a921d3f78d5e60) [0x3ee8…71d0](https://etherscan.io/tx/0x3ee841e40b031b12081fa392fb46658324d839a8f2f044300d9d7241ba2a71d0) [0x6c2c…14bb](https://etherscan.io/tx/0x6c2c4995571675f42fa2820105ddea3164fee25838d268840ec804f069bb14bb). Block 25,905,586 at 2026-09-04T17:55:59+00:00, index 7/186, type 0x2, status not fetched. From [0xf078…f19e](https://etherscan.io/address/0xf078969e55cabf9ae3f26afeb5ec627b4430f19e) (unknown code status; window profile: no tags, 5 sent to 3 destinations, nonce 2,376 to 2,380) to [0x9d39…3497](https://etherscan.io/address/0x9d39a5de30e57443bff2a8307a4256c8797a3497) (a contract of 17,299 bytes; contract_like, never_sends, called 137 times in the window). Selector `0xf2888dbb`, calldata 36 bytes, value 0 ETH, 1 logs, tip 3.3 gwei. Largest position change $10,033,001 (USDe at [0xf078…f19e](https://etherscan.io/address/0xf078969e55cabf9ae3f26afeb5ec627b4430f19e)); gross $10,033,001; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf078…f19e](https://etherscan.io/address/0xf078969e55cabf9ae3f26afeb5ec627b4430f19e) nets USDe $10,033,001 against [0x7fc7…3425](https://etherscan.io/address/0x7fc7c91d556b400afa565013e3f32055a0713425) (a contract of 534 bytes; never_sends).

Net flows: [0x7fc7…3425](https://etherscan.io/address/0x7fc7c91d556b400afa565013e3f32055a0713425) -10,033,001.47 USDe (-$10,033,001); [0xf078…f19e](https://etherscan.io/address/0xf078969e55cabf9ae3f26afeb5ec627b4430f19e) +10,033,001.47 USDe ($10,033,001).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): Twenty-four claims, $17.9M in the day; the shares were burned when the cooldown started, so the registry's vault_withdraw rule (ERC-4626 Withdraw event) never sees them.

Unverified: the silo address is read from the transfer; sUSDe's unstake semantics are model memory consistent with the single USDe leg.

Proposed type: `susde_unstake_claim`. Rule: destination is the sUSDe contract, selector 0xf2888dbb, a USDe leg present. Method: generic

### E54. [0xa152…a2e0](https://etherscan.io/tx/0xa1525f9f7f723ea7ecb93091d0dfd0ae10db04a41c08f67aaee214ea41c2a2e0): the same sweep with one payer: 10,239,262.14 USDC from 0x7eb36c98… into 0xa9d1e08c… through 0x7dac2c6a… (selected in round_02)

Selected for residue cluster USD #2. Cluster 78bea70f8d: 8 transactions from 1 senders, $17,096,026, shape transfers-only, other examples [0x0ae2…aa8f](https://etherscan.io/tx/0x0ae29368e11284724ff7cefeb7e50b5f5d90af329e60741abc782f1afb91aa8f) [0x00b6…3384](https://etherscan.io/tx/0x00b6cb2822e4c4f64aa55838ddc69654da2e0d8d8f894f730947dca2efa53384) [0x0b86…6281](https://etherscan.io/tx/0x0b86763e91ce2e25294f95c4ea6faa764bbf00b9b824c3698d8dd269cca56281). Block 25,906,054 at 2026-09-04T19:30:11+00:00, index 50/235, type 0x2, status not fetched. From [0xce40…95c4](https://etherscan.io/address/0xce4066e366442441d67c20cf1395229e718495c4) (unknown code status; window profile: no tags, 18 sent to 2 destinations, nonce 30,477 to 30,494) to [0x7dac…0d38](https://etherscan.io/address/0x7dac2c6a4b0ec57431844b8f78d2d612bb1e0d38) (a contract of 4,224 bytes; never_sends, called 17 times in the window). Selector `0xb257b7af`, calldata 420 bytes, value 0 ETH, 1 logs, tip 0.921912178 gwei. Largest position change $10,237,821 (USDC at [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43)); gross $10,237,821; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) nets nothing priced against [0x7eb3…dadf](https://etherscan.io/address/0x7eb36c98663d653c1f91aef78a05d989c066dadf) (unknown code status; never_sends).

Net flows: [0x7eb3…dadf](https://etherscan.io/address/0x7eb36c98663d653c1f91aef78a05d989c066dadf) -10,239,262.14 USDC (-$10,237,821); [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) +10,239,262.14 USDC ($10,237,821).

Event families: ERC20_Transfer_shape ×1.

Interpretation (LLM, confidence high): Eight transactions and $17.1M into the same collector by the same ABI (selector 0xb257b7af): the collector is a treasury being fed by customer sweeps.

Proposed type: `operator_sweep_no_events`

### E55. [0xcdd5…f20a](https://etherscan.io/tx/0xcdd5f68cb2a0eaf65baf2d5c591066f2464943ab2228f3915a869784eaf0f20a): batched transferFrom sweep: 228,909.26 USDC from five customer addresses into 0xa9d1e08c… through 0x1bbe1be1… (selected in round_02)

Selected for residue cluster size #7. Cluster 40c28283eb: 12 transactions from 1 senders, $997,354, shape transfers-only, other examples [0x9740…c704](https://etherscan.io/tx/0x974034788561d1ea1d054d28e277b2799b0df18dcace4223482eabb02f99c704) [0xf2a3…87df](https://etherscan.io/tx/0xf2a302aba6e0b4f8d46e522da5797d98ded2b97f3b3527e6bbee40baa69087df) [0xc87d…5b45](https://etherscan.io/tx/0xc87dc69cb6ed0529fb04aeeefc92bead528f395bc6bb88c5e989e07af01d5b45). Block 25,910,813 at 2026-09-05T11:25:11+00:00, index 12/229, type 0x2, status not fetched. From [0xb566…4963](https://etherscan.io/address/0xb56658564a2381d6664850c2c14a5dedb11b4963) (unknown code status; window profile: no tags, 26 sent to 1 destinations, nonce 43,865 to 43,890) to [0x1bbe…7e5d](https://etherscan.io/address/0x1bbe1be1fb532a010762665cfcbed31595367e5d) (a contract of 4,224 bytes; contract_like, never_sends, called 26 times in the window). Selector `0xb257b7af`, calldata 1,700 bytes, value 0 ETH, 5 logs, tip 0.954308133 gwei. Largest position change $228,877 (USDC at [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43)); gross $228,877; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) nets nothing priced against [0x8e89…7de0](https://etherscan.io/address/0x8e8933b7ca5d88798af90a13282bee8e63957de0) (unknown code status; never_sends).

Net flows: [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) +228,909.26 USDC ($228,877); [0x8e89…7de0](https://etherscan.io/address/0x8e8933b7ca5d88798af90a13282bee8e63957de0) -125,864.05 USDC (-$125,846); [0x4efb…4800](https://etherscan.io/address/0x4efbc2fbf78e570bf9ea2c6dfcfa3626a4464800) -89,192.70 USDC (-$89,180); [0xb92a…d83c](https://etherscan.io/address/0xb92addb207c35af1dff0ec8d08b95a60dc50d83c) -11,331.49 USDC (-$11,330); [0xfe83…2eda](https://etherscan.io/address/0xfe83e0599c031e9b7e55bb743625ac86d5c22eda) -2,278.68 USDC (-$2,278); [0x17c8…c940](https://etherscan.io/address/0x17c8ad359f942222dc827d9f2e842da54bddc940) -242.337541 USDC (-$242.30).

Event families: ERC20_Transfer_shape ×5.

Interpretation (LLM, confidence high): Operator 0xb56658… (nonce 43,890) at a flat 1 gwei; the helper emits nothing.

Proposed type: `operator_sweep_no_events`. Rule: only transfer events, every priced leg third party to a single recipient, no custom event. Method: custody_flow

## Known-type audit: one hash-sampled occurrence per type, re-read by the LLM

Each known type contributes one deterministic sample so that the rule can be checked against a transaction it matched, not only against the transactions it was written for. A note that disagrees with the type is a correction request for the registry.

### A56. [0x4e4a…394e](https://etherscan.io/tx/0x4e4a2ccee2e37f8eab5ff65bad0c4aacd778e914c6227f1594cab5abc57f394e): not yet annotated

Selected for known type audit (sender_tokens_via_contract). Cluster audit-sender_tokens_via_contract: 231 transactions from 91 senders, $29,601,625, shape transfers-only. Block 25,904,452 at 2026-09-04T14:07:59+00:00, index 225/413, type 0x2, success. From [0xd501…ec35](https://etherscan.io/address/0xd501ccbdb70ce518b2da68c685045fa54458ec35) (an EOA; window profile: no tags, 10 sent to 2 destinations, nonce 700 to 709) to [0xf41b…8a56](https://etherscan.io/address/0xf41b389e0c1950dc0b16c9498eae77131cc08a56) (a contract of 24,568 bytes; contract_like, never_sends, called 218 times in the window). Selector `0x65e03b9c`, calldata 1,060 bytes, value 0 ETH, 3 logs, tip 2.4 gwei. Largest position change $46,390 (USDC at [0xd501…ec35](https://etherscan.io/address/0xd501ccbdb70ce518b2da68c685045fa54458ec35)); gross $46,390; swaps 0 in 0 pools; 2 distinct recipients. Principal [0xd501…ec35](https://etherscan.io/address/0xd501ccbdb70ce518b2da68c685045fa54458ec35) nets USDC -$46,390 against [0x9a29…bc63](https://etherscan.io/address/0x9a293c63d2efd35983e8b6c9f88084f4cbf7bc63) (an EOA; no tags).

Net flows: [0xd501…ec35](https://etherscan.io/address/0xd501ccbdb70ce518b2da68c685045fa54458ec35) -46,397.01 USDC (-$46,390); [0x9a29…bc63](https://etherscan.io/address/0x9a293c63d2efd35983e8b6c9f88084f4cbf7bc63) +46,389.36 USDC ($46,383); [0x4169…5562](https://etherscan.io/address/0x4169447a424ec645f8a24dccfd8328f714dd5562) +7.645155 USDC ($7.64).

Event families: ERC20_Transfer_shape ×2, unknown ×1. Unknown topics: [0xf41b…8a56](https://etherscan.io/address/0xf41b389e0c1950dc0b16c9498eae77131cc08a56) 0x05ff99c6f7e97b6a… ×1.

_No qualitative note yet for this transaction._

### A57. [0x9f2a…5544](https://etherscan.io/tx/0x9f2a736c918d3b9e5dc55b64213d5ac992690dc34e060ef596a21e96f2c75544): not yet annotated

Selected for known type audit (relay_settlement_withdrawal). Cluster audit-relay_settlement_withdrawal: 444 transactions from 1 senders, $17,024,798, shape RelayCallExecuted. Block 25,904,463 at 2026-09-04T14:10:11+00:00, index 30/321, type 0x2, success. From [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) (an EOA; window profile: hot_wallet, very_high_nonce, 5575 sent to 508 destinations, nonce 4,780,333 to 4,785,907) to [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) (a contract of 8,628 bytes; contract_like, many_sources, never_sends, called 28191 times in the window). Selector `0x2d9fb478`, calldata 612 bytes, value 0 ETH, 2 logs, tip 0.552554708 gwei. Largest position change $20,892 (USDT at [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef)); gross $20,892; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) nets USDT $20,892 against [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) (a contract of 8,628 bytes; contract_like, many_sources, never_sends).

Net flows: [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) -20,890.68 USDT (-$20,892); [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) +20,890.68 USDT ($20,892).

Event families: ERC20_Transfer_shape ×1, RelayCallExecuted ×1.

_No qualitative note yet for this transaction._

### A58. [0xdb6c…dc2e](https://etherscan.io/tx/0xdb6c610943e231d60840ec9766a0f57d2eddb0fd7909cd305c57b6153e22dc2e): not yet annotated

Selected for known type audit (custody_vault_abi_transfer). Cluster audit-custody_vault_abi_transfer: 410 transactions from 30 senders, $247,615,237, shape transfers-only. Block 25,904,480 at 2026-09-04T14:13:35+00:00, index 197/202, type 0x0, success. From [0xb02c…f8fc](https://etherscan.io/address/0xb02c6c40a798184d5e012fbb1dc698977671f8fc) (an EOA; window profile: bot_sender, very_high_nonce, 756 sent to 2 destinations, nonce 503,396 to 504,151) to [0x3a5c…d597](https://etherscan.io/address/0x3a5cc8689d1b0cef2c317bc5c0ad6ce88b27d597) (a contract of 3,575 bytes; contract_like, many_sources, never_sends, called 730 times in the window). Selector `0x0dcd7a6c`, calldata 324 bytes, value 0 ETH, 1 logs, tip 1.081574779 gwei. Largest position change $10,002 (USDT at [0x66c7…4225](https://etherscan.io/address/0x66c7319655be04b8b4b9123602da6d5276544225)); gross $10,002; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x3a5c…d597](https://etherscan.io/address/0x3a5cc8689d1b0cef2c317bc5c0ad6ce88b27d597) nets USDT -$10,002 against [0x66c7…4225](https://etherscan.io/address/0x66c7319655be04b8b4b9123602da6d5276544225) (an EOA; no tags).

Net flows: [0x3a5c…d597](https://etherscan.io/address/0x3a5cc8689d1b0cef2c317bc5c0ad6ce88b27d597) -10,002.00 USDT (-$10,002); [0x66c7…4225](https://etherscan.io/address/0x66c7319655be04b8b4b9123602da6d5276544225) +10,002.00 USDT ($10,002).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A59. [0x0142…a948](https://etherscan.io/tx/0x01423463f4424dcec1152ed045c9567d54bb11e27d5334507a3109d37b7ca948): not yet annotated

Selected for known type audit (deposit_sweep). Cluster audit-deposit_sweep: 4,802 transactions from 3,186 senders, $1,055,285,811, shape transfers-only. Block 25,904,483 at 2026-09-04T14:14:11+00:00, index 112/396, type 0x2, success. From [0xe215…0488](https://etherscan.io/address/0xe215e5ebd0f8cbdd74b9b7afe3441967c0170488) (an EOA; window profile: no tags, 1 sent to 1 destinations, nonce 464 to 464) to [0xdac1…1ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) (a contract of 11,075 bytes; contract_like, never_sends, called 351027 times in the window). Selector `0xa9059cbb`, calldata 68 bytes, value 0 ETH, 1 logs, tip 2 gwei. Largest position change $50,643 (USDT at [0xe215…0488](https://etherscan.io/address/0xe215e5ebd0f8cbdd74b9b7afe3441967c0170488)); gross $50,643; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xe215…0488](https://etherscan.io/address/0xe215e5ebd0f8cbdd74b9b7afe3441967c0170488) nets USDT -$50,643 against [0x4fd3…7545](https://etherscan.io/address/0x4fd3f4e8e5256f5e88a4c51b83acf2dae8127545) (an EOA; pass_through).

Net flows: [0x4fd3…7545](https://etherscan.io/address/0x4fd3f4e8e5256f5e88a4c51b83acf2dae8127545) +50,640.52 USDT ($50,643); [0xe215…0488](https://etherscan.io/address/0xe215e5ebd0f8cbdd74b9b7afe3441967c0170488) -50,640.52 USDT (-$50,643).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A60. [0x20b4…1305](https://etherscan.io/tx/0x20b4e3c4925f8a0abf3ae322a7d687d09325133739e855fefc12b6a11f4f1305): not yet annotated

Selected for known type audit (operator_sweep_no_events). Cluster audit-operator_sweep_no_events: 91 transactions from 22 senders, $25,968,567, shape transfers-only. Block 25,904,487 at 2026-09-04T14:15:11+00:00, index 129/427, type 0x2, success. From [0x5eb8…c5e3](https://etherscan.io/address/0x5eb8825ca3cc1d3ac309abac112e97e90dbdc5e3) (an EOA; window profile: no tags, 7 sent to 1 destinations, nonce 13,934 to 13,940) to [0x64f6…bed2](https://etherscan.io/address/0x64f689339a19fccf8228f78c6a784540b35fbed2) (a contract of 4,224 bytes; never_sends, called 7 times in the window). Selector `0xb257b7af`, calldata 1,700 bytes, value 0 ETH, 5 logs, tip 0.616300077 gwei. Largest position change $11,335 (USDC at [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43)); gross $11,335; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) nets nothing priced against [0x81cf…10c4](https://etherscan.io/address/0x81cf166841f345d0fd52e4771955e44e27ae10c4) (a contract (minimal proxy to [0x70fa…9b7b](https://etherscan.io/address/0x70faa150f2ca41edda9d99d367ca32eec90b9b7b)) of 45 bytes; never_sends).

Net flows: [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) +11,336.17 USDC ($11,335); [0x81cf…10c4](https://etherscan.io/address/0x81cf166841f345d0fd52e4771955e44e27ae10c4) -6,114.06 USDC (-$6,113); [0xbf8d…e886](https://etherscan.io/address/0xbf8d73be612d69ef3333c537c4ca4feca378e886) -3,449.70 USDC (-$3,449); [0xede6…8cc6](https://etherscan.io/address/0xede69cf77eeab4577b97c69af2f95735fc2b8cc6) -1,196.59 USDC (-$1,196); [0xe1ae…1066](https://etherscan.io/address/0xe1ae81ae129441d118bdc8ada4e6c6e101141066) -399.958572 USDC (-$399.90); [0x418b…41c8](https://etherscan.io/address/0x418bac92778a51004d06151148dacdbbd11a41c8) -175.857719 USDC (-$175.83).

Event families: ERC20_Transfer_shape ×5.

_No qualitative note yet for this transaction._

### A61. [0xff71…9af7](https://etherscan.io/tx/0xff71496ba20a90006bb61e4217028dbaab37564d8ea359b77d528b2e9af19af7): audit of contract_deposit_recorded: 298 ETH ($727,322) from hot wallet 0xdfd5293d… into 0xd59d7a96…, which emits Deposited(address,uint256,bytes)

Selected for known type audit (contract_deposit_recorded). Cluster audit-contract_deposit_recorded: 481 transactions from 231 senders, $61,078,436, shape GDeposited_aub. Block 25,904,527 at 2026-09-04T14:23:11+00:00, index 73/437, type 0x2, success. From [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) (an EOA; window profile: hot_wallet, very_high_nonce, 8772 sent to 1889 destinations, nonce 15,183,970 to 15,192,741) to [0xd59d…12d2](https://etherscan.io/address/0xd59d7a9698eff3e68e0af7e803d4ed35e7ed12d2) (a contract (minimal proxy to [0x059f…5ded](https://etherscan.io/address/0x059ffafdc6ef594230de44f824e2bd0a51ca5ded)) of 45 bytes; never_sends, called 4 times in the window). Selector `0x`, calldata 0 bytes, value 298 ETH, 2 logs, tip 1 gwei. Largest position change $727,322 (ETH at [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d)); gross $727,322; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) nets ETH -$727,322 against [0xd59d…12d2](https://etherscan.io/address/0xd59d7a9698eff3e68e0af7e803d4ed35e7ed12d2) (a contract (minimal proxy to [0x059f…5ded](https://etherscan.io/address/0x059ffafdc6ef594230de44f824e2bd0a51ca5ded)) of 45 bytes; never_sends).

Net flows: [0xd59d…12d2](https://etherscan.io/address/0xd59d7a9698eff3e68e0af7e803d4ed35e7ed12d2) +298.000000 ETH ($727,322); [0xdfd5…963d](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) -298.000000 ETH (-$727,322).

Event families: GDeposited_aub ×1, unknown ×1. Unknown topics: [0xd59d…12d2](https://etherscan.io/address/0xd59d7a9698eff3e68e0af7e803d4ed35e7ed12d2) 0x69b31548dea9b3b7… ×1.

Interpretation (LLM, confidence medium): The rule holds: value enters the called contract, nothing leaves, the contract records it. An exchange committing ETH to a contract-based product.

Unverified: 0xdfd5293d… as a Binance hot wallet is model memory (it was a hot-wallet candidate in the pilot); the deposit contract's product (staking or bridge) is not identified.

### A62. [0x0ae7…2adf](https://etherscan.io/tx/0x0ae7b80b2606d2e16a304b012334b1c3095d987a72be46ddc465e5cdf06d2adf): not yet annotated

Selected for known type audit (atomic_arbitrage). Cluster audit-atomic_arbitrage: 118 transactions from 25 senders, $3,784,828, shape BalancerSwap,V3Swap. Block 25,904,587 at 2026-09-04T14:35:11+00:00, index 0/306, type 0x2, success. From [0xf6b4…59ec](https://etherscan.io/address/0xf6b4cbf5f6211645cb251ab5e111f0a8881259ec) (an EOA; window profile: bot_sender, 103 sent to 1 destinations, nonce 26,530 to 26,632) to [0x8f40…71a7](https://etherscan.io/address/0x8f40082c34812db98681c63db3bbeb29dbe871a7) (a contract of 8,489 bytes; contract_like, never_sends, router_like, called 243 times in the window). Selector `0xc0433cf8`, calldata 1,828 bytes, value 1.25E-16 ETH, 8 logs, tip 0 gwei. Largest position change $19,501 (USDT at [0xd315…6293](https://etherscan.io/address/0xd315a9c38ec871068fec378e4ce78af528c76293)); gross $77,700; swaps 2 in 2 pools; 4 distinct recipients. Principal [0x8f40…71a7](https://etherscan.io/address/0x8f40082c34812db98681c63db3bbeb29dbe871a7) nets WBTC $2.51 against [0xd315…6293](https://etherscan.io/address/0xd315a9c38ec871068fec378e4ce78af528c76293) (a contract of 24,563 bytes; never_sends, pool).

Net flows: [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) +19,499.83 USDT ($19,501); [0xd315…6293](https://etherscan.io/address/0xd315a9c38ec871068fec378e4ce78af528c76293) -19,499.83 USDT (-$19,501); [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) -0.245930 WBTC (-$19,349); [0xd315…6293](https://etherscan.io/address/0xd315a9c38ec871068fec378e4ce78af528c76293) +0.245898 WBTC ($19,347); [0x8f40…71a7](https://etherscan.io/address/0x8f40082c34812db98681c63db3bbeb29dbe871a7) +0.000032 WBTC ($2.51); [0x8f40…71a7](https://etherscan.io/address/0x8f40082c34812db98681c63db3bbeb29dbe871a7) +0.000000 ETH ($0.00); [0xf6b4…59ec](https://etherscan.io/address/0xf6b4cbf5f6211645cb251ab5e111f0a8881259ec) -0.000000 ETH ($0.00); [0xe9c4…cc8a](https://etherscan.io/address/0xe9c4af01ea41d520feb44f69a7160d3576ebcc8a) +0.000000 WBTC ($0.00).

Event families: ERC20_Transfer_shape ×5, BalancerSwap ×1, V3Swap ×1, unknown ×1. Unknown topics: [0x7ac9…568c](https://etherscan.io/address/0x7ac940038125796a7819652136c3f16db9b5568c) 0x9b97792d4bc68bb4… ×1.

_No qualitative note yet for this transaction._

### A63. [0x3a72…8083](https://etherscan.io/tx/0x3a72ce2187371f9722347fba1a96f1d40dc364738d8abd63825dcd5f53d78083): not yet annotated

Selected for known type audit (trade_against_unpriced_token). Cluster audit-trade_against_unpriced_token: 16 transactions from 13 senders, $3,062,776, shape transfers-only. Block 25,904,597 at 2026-09-04T14:37:11+00:00, index 598/660, type 0x2, success. From [0x963e…a4a8](https://etherscan.io/address/0x963eb0638a2fe075269b4e83f886e89d855ea4a8) (an EOA; window profile: no tags, 19 sent to 15 destinations, nonce 1,409 to 1,427) to [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) (a contract of 7,765 bytes; never_sends, called 1 times in the window). Selector `0x852a12e3`, calldata 36 bytes, value 0 ETH, 5 logs, tip 0.001 gwei. Largest position change $196,694 (WBTC at [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a)); gross $196,694; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x963e…a4a8](https://etherscan.io/address/0x963eb0638a2fe075269b4e83f886e89d855ea4a8) nets WBTC $196,694 against [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) (a contract of 7,765 bytes; never_sends).

Net flows: [0x963e…a4a8](https://etherscan.io/address/0x963eb0638a2fe075269b4e83f886e89d855ea4a8) +2.500000 WBTC ($196,694); [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) -2.500000 WBTC (-$196,694).

Unpriced ERC-20 transfers: [cWBTC (self-reported)](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) ×1 (largest raw 12450209738).

Event families: unknown ×3, ERC20_Transfer_shape ×2. Unknown topics: [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) 0x4dec04e750ca1153… ×1; [0x3d98…cd3b](https://etherscan.io/address/0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b) 0x2caecd17d02f56fa… ×1; [0xccf4…dd6a](https://etherscan.io/address/0xccf4429db6322d5c611ee964527d42e5d685dd6a) 0xe5b754fb1abb7f01… ×1.

_No qualitative note yet for this transaction._

### A64. [0x103a…7bfe](https://etherscan.io/tx/0x103abe4c0f238e78d6c26979e98dd62cf43ac5f2f8cd77c4656e1f31e66c7bfe): not yet annotated

Selected for known type audit (deposit_with_nft_receipt). Cluster audit-deposit_with_nft_receipt: 21 transactions from 18 senders, $3,277,142, shape ERC721_Transfer_shape. Block 25,904,624 at 2026-09-04T14:42:35+00:00, index 97/559, type 0x2, success. From [0xe469…6f3c](https://etherscan.io/address/0xe469d2c8fc404e9b4f59f3f0845ed5f69a4d6f3c) (an EOA; window profile: no tags, 15 sent to 6 destinations, nonce 29 to 43) to [0xa741…5da3](https://etherscan.io/address/0xa741a32f9dcfe6adba088fd0f97e90742d7d5da3) (a contract of 24,559 bytes; never_sends, called 6 times in the window). Selector `0x9cb90ba6`, calldata 356 bytes, value 0 ETH, 13 logs, tip 0.6 gwei. Largest position change $20,866 (wstETH at [0xe469…6f3c](https://etherscan.io/address/0xe469d2c8fc404e9b4f59f3f0845ed5f69a4d6f3c)); gross $29,954; swaps 0 in 0 pools; 5 distinct recipients. Principal [0xe469…6f3c](https://etherscan.io/address/0xe469d2c8fc404e9b4f59f3f0845ed5f69a4d6f3c) nets IMPL:0x6440…b01d $8,990, WETH -$91.53, wstETH -$20,866 against [0x531a…19a0](https://etherscan.io/address/0x531a8f99c70d6a56a7cee02d6b4281650d7919a0) (a contract of 5,555 bytes; never_sends).

Net flows: [0x531a…19a0](https://etherscan.io/address/0x531a8f99c70d6a56a7cee02d6b4281650d7919a0) +6.834074 wstETH ($20,866); [0xe469…6f3c](https://etherscan.io/address/0xe469d2c8fc404e9b4f59f3f0845ed5f69a4d6f3c) -6.834074 wstETH (-$20,866); [0xe469…6f3c](https://etherscan.io/address/0xe469d2c8fc404e9b4f59f3f0845ed5f69a4d6f3c) +9,000.00 IMPL:0x6440…b01d ($8,990); [0x8c44…db1f](https://etherscan.io/address/0x8c44fba379d8a8608c0e29b2729deb75a981db1f) +0.037500 WETH ($91.53); [0xe469…6f3c](https://etherscan.io/address/0xe469d2c8fc404e9b4f59f3f0845ed5f69a4d6f3c) -0.037500 WETH (-$91.53); [0x9502…e56b](https://etherscan.io/address/0x9502b7c397e9aa22fe9db7ef7daf21cd2aebe56b) +4.958413 IMPL:0x6440…b01d ($4.95); [0x807d…eee1](https://etherscan.io/address/0x807def5e7d057df05c796f4bc75c3fe82bd6eee1) +1.652804 IMPL:0x6440…b01d ($1.65).

Event families: unknown ×6, ERC20_Transfer_shape ×5, Approval ×1, ERC721_Transfer_shape ×1. Unknown topics: [0xa741…5da3](https://etherscan.io/address/0xa741a32f9dcfe6adba088fd0f97e90742d7d5da3) 0x3942babd464ceb1c… ×1; [0xa741…5da3](https://etherscan.io/address/0xa741a32f9dcfe6adba088fd0f97e90742d7d5da3) 0x649442545e0f313a… ×1; [0x9502…e56b](https://etherscan.io/address/0x9502b7c397e9aa22fe9db7ef7daf21cd2aebe56b) 0xe367a96648d02811… ×1; [0x531a…19a0](https://etherscan.io/address/0x531a8f99c70d6a56a7cee02d6b4281650d7919a0) 0x9bbe217b4113a0fc… ×1; [0xa289…8b22](https://etherscan.io/address/0xa2895d6a3bf110561dfe4b71ca539d84e1928b22) 0x0fba2673863b12c7… ×1; [0xa289…8b22](https://etherscan.io/address/0xa2895d6a3bf110561dfe4b71ca539d84e1928b22) 0x962110f281c12137… ×1.

_No qualitative note yet for this transaction._

### A65. [0x0e42…135c](https://etherscan.io/tx/0x0e42f56d8ae51a91e9b0eab540c78d5f84e2414368cd9d977d24922556f0135c): not yet annotated

Selected for known type audit (plain_transfer_eoa). Cluster audit-plain_transfer_eoa: 14,356 transactions from 6,913 senders, $7,526,643,843, shape transfers-only. Block 25,904,699 at 2026-09-04T14:57:35+00:00, index 178/235, type 0x2, success. From [0xf6f4…cd6a](https://etherscan.io/address/0xf6f455d16e61776d032bbb194ebf97b5cfa3cd6a) (an EOA; window profile: no tags, 1 sent to 1 destinations, nonce 11 to 11) to [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) (a contract of 2,186 bytes; contract_like, never_sends, called 165686 times in the window). Selector `0xa9059cbb`, calldata 68 bytes, value 0 ETH, 1 logs, tip 1 gwei. Largest position change $150,679 (USDC at [0xf6f4…cd6a](https://etherscan.io/address/0xf6f455d16e61776d032bbb194ebf97b5cfa3cd6a)); gross $150,679; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf6f4…cd6a](https://etherscan.io/address/0xf6f455d16e61776d032bbb194ebf97b5cfa3cd6a) nets USDC -$150,679 against [0xdb80…6061](https://etherscan.io/address/0xdb8093a6c4890c85026bec69324167d2edd76061) (an EOA; no tags).

Net flows: [0xdb80…6061](https://etherscan.io/address/0xdb8093a6c4890c85026bec69324167d2edd76061) +150,700.00 USDC ($150,679); [0xf6f4…cd6a](https://etherscan.io/address/0xf6f455d16e61776d032bbb194ebf97b5cfa3cd6a) -150,700.00 USDC (-$150,679).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A66. [0x7985…5b04](https://etherscan.io/tx/0x7985b7d07a288d8e0f18ae3e9fd6dc7b73cbc7eff51c31f79b356899fef05b04): not yet annotated

Selected for known type audit (weth_unwrap). Cluster audit-weth_unwrap: 111 transactions from 41 senders, $18,344,381, shape WETHWithdrawal. Block 25,904,795 at 2026-09-04T15:16:47+00:00, index 413/487, type 0x2, success. From [0xbdd5…1fc6](https://etherscan.io/address/0xbdd50e6f8b34593b1fa8d5e59e9e01b9de531fc6) (an EOA; window profile: bot_sender, 91 sent to 2 destinations, nonce 2,312 to 2,402) to [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) (a contract of 3,124 bytes; contract_like, many_sources, never_sends, called 7138 times in the window). Selector `0x2e1a7d4d`, calldata 36 bytes, value 0 ETH, 1 logs, tip 1E-9 gwei. Largest position change $26,221 (WETH at [0xbdd5…1fc6](https://etherscan.io/address/0xbdd50e6f8b34593b1fa8d5e59e9e01b9de531fc6)); gross $26,221; swaps 0 in 0 pools; 0 distinct recipients. Principal [0xbdd5…1fc6](https://etherscan.io/address/0xbdd50e6f8b34593b1fa8d5e59e9e01b9de531fc6) nets WETH -$26,221.

Net flows: [0xbdd5…1fc6](https://etherscan.io/address/0xbdd50e6f8b34593b1fa8d5e59e9e01b9de531fc6) -10.687888 WETH (-$26,221).

Event families: WETHWithdrawal ×1.

_No qualitative note yet for this transaction._

### A67. [0x9ca7…5c90](https://etherscan.io/tx/0x9ca780f56dfb1f8e40775e0b026523faae30b2d8b9e9510e5356fa5ec3e25c90): audit of bilateral_exchange_settled (now dex_swap_aggregator_event): 500,016.94 USDT sold through aggregator router 0x6131b5fa…, which records Swapped and Exchange events; the two-sided party was an intermediate contract

Selected for known type audit (dex_swap_aggregator_event). Cluster audit-dex_swap_aggregator_event: 118 transactions from 74 senders, $6,414,457, shape AggregatorSwapped,GExchange_aua. Block 25,904,800 at 2026-09-04T15:17:47+00:00, index 31/209, type 0x2, success. From [0x5470…121e](https://etherscan.io/address/0x547090eb068220b3da1f7b611ef21723caa4121e) (an EOA; window profile: no tags, 4 sent to 4 destinations, nonce 649 to 652) to [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) (a contract of 18,652 bytes; contract_like, many_sources, never_sends, router_like, called 1823 times in the window). Selector `0xe21fd0e9`, calldata 10,468 bytes, value 0 ETH, 19 logs, tip 0.020911034 gwei. Largest position change $500,017 (USDT at [0x5470…121e](https://etherscan.io/address/0x547090eb068220b3da1f7b611ef21723caa4121e)); gross $1,999,911; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x5470…121e](https://etherscan.io/address/0x547090eb068220b3da1f7b611ef21723caa4121e) nets USDC $499,938, USDT -$500,017 against [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) (a contract of 13,529 bytes; many_sources, never_sends).

Net flows: [0x5470…121e](https://etherscan.io/address/0x547090eb068220b3da1f7b611ef21723caa4121e) -499,995.00 USDT (-$500,017); [0x5470…121e](https://etherscan.io/address/0x547090eb068220b3da1f7b611ef21723caa4121e) +500,008.70 USDC ($499,938); [0x35c9…b636](https://etherscan.io/address/0x35c9a4dae1ff05788f24b5b32721d89340cbb636) +479,995.20 USDT ($480,016); [0x35c9…b636](https://etherscan.io/address/0x35c9a4dae1ff05788f24b5b32721d89340cbb636) -480,008.07 USDC (-$479,941); [0x2e69…898d](https://etherscan.io/address/0x2e69797d37e888d62974a1ffa20816a5f55f898d) +19,999.80 USDT ($20,001); [0x2e69…898d](https://etherscan.io/address/0x2e69797d37e888d62974a1ffa20816a5f55f898d) -20,000.62 USDC (-$19,998); [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) +0.000000 USDC ($0.00); [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) +0.000000 USDT ($0.00).

Event families: unknown ×9, ERC20_Transfer_shape ×8, AggregatorSwapped ×1, GExchange_aua ×1. Unknown topics: [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) 0xa6fee24309b1d83d… ×3; [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) 0xc035da294269ae5a… ×2; [0x35c9…b636](https://etherscan.io/address/0x35c9a4dae1ff05788f24b5b32721d89340cbb636) 0x143f1f8e861fbded… ×2; [0xab3c…0b9b](https://etherscan.io/address/0xab3cbdeeaf9266d79f9c7a1eaad28e95cc810b9b) 0x0c7ba9d42e073afa… ×1; [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) 0x095e66fa4dd6a6f7… ×1.

Interpretation (LLM, confidence high): This sample is why round 4 added the aggregator-event type ahead of the bilateral rule.

Unverified: 0x6131b5fa… as KyberSwap's MetaAggregationRouterV2 is model memory.

### A68. [0x066f…78c6](https://etherscan.io/tx/0x066f65c9eef76246e134c7787c8d4257c87e832ddc7afbda44f2280abc2b78c6): not yet annotated

Selected for known type audit (aster_treasury_withdrawal). Cluster audit-aster_treasury_withdrawal: 18 transactions from 2 senders, $9,190,068, shape AsterWithdrawalObserved. Block 25,904,813 at 2026-09-04T15:20:23+00:00, index 188/203, type 0x2, success. From [0xef9c…77ab](https://etherscan.io/address/0xef9c62ed74150c63d07573e5f9140107166777ab) (an EOA; window profile: bot_sender, 83 sent to 1 destinations, nonce 37,008 to 37,090) to [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) (a contract of 855 bytes; contract_like, many_sources, never_sends, called 418 times in the window). Selector `0x0cd4b1fe`, calldata 900 bytes, value 0 ETH, 2 logs, tip 0.054636452 gwei. Largest position change $50,002 (USDT at [0xa684…b080](https://etherscan.io/address/0xa68403c26645361a3b7f086f76d51fd10c78b080)); gross $50,002; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) nets USDT -$50,002 against [0xa684…b080](https://etherscan.io/address/0xa68403c26645361a3b7f086f76d51fd10c78b080) (an EOA; no tags).

Net flows: [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) -49,999.49 USDT (-$50,002); [0xa684…b080](https://etherscan.io/address/0xa68403c26645361a3b7f086f76d51fd10c78b080) +49,999.49 USDT ($50,002).

Event families: AsterWithdrawalObserved ×1, ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A69. [0xc01a…0528](https://etherscan.io/tx/0xc01ad30b470541cbc2432bc2cc3fd6f226dc24fddc96180f1a384492e7380528): not yet annotated

Selected for known type audit (permit2_operator_transfer). Cluster audit-permit2_operator_transfer: 34 transactions from 4 senders, $1,181,077, shape transfers-only. Block 25,904,904 at 2026-09-04T15:38:47+00:00, index 252/268, type 0x2, success. From [0xa99b…2076](https://etherscan.io/address/0xa99b5736e482e5982d809ca6596bf7147a522076) (an EOA; window profile: no tags, 17 sent to 7 destinations, nonce 20,707 to 20,723) to [0x0000…8ba3](https://etherscan.io/address/0x000000000022d473030f116ddee9f6b43ac78ba3) (a contract of 9,152 bytes; contract_like, never_sends, called 685 times in the window). Selector `0x0d58b1db`, calldata 1,988 bytes, value 0 ETH, 15 logs, tip 0.004 gwei. Largest position change $13,519 (USDC at [0xe4f9…4a03](https://etherscan.io/address/0xe4f9b0a83eb4552508ad9bf8c83662d1c7004a03)); gross $13,519; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xe4f9…4a03](https://etherscan.io/address/0xe4f9b0a83eb4552508ad9bf8c83662d1c7004a03) nets nothing priced against [0xc46c…ac65](https://etherscan.io/address/0xc46c053eb92d43e3add37ea5e64c76a78907ac65) (an EOA; never_sends).

Net flows: [0xe4f9…4a03](https://etherscan.io/address/0xe4f9b0a83eb4552508ad9bf8c83662d1c7004a03) +13,520.97 USDC ($13,519); [0xc46c…ac65](https://etherscan.io/address/0xc46c053eb92d43e3add37ea5e64c76a78907ac65) -10,000.00 USDC (-$9,999); [0x8b52…bb86](https://etherscan.io/address/0x8b52e9e999a1e7a59e74a2feeae3350e584bbb86) -983.102635 USDC (-$982.96); [0x7555…6898](https://etherscan.io/address/0x7555cbb5aa120dd55b9025b35fd0823ea88b6898) -470.000000 USDC (-$469.93); [0x2fce…ba9f](https://etherscan.io/address/0x2fcedb9943990bb335c956d012a13c7f8e27ba9f) -345.043995 USDC (-$345.00); [0x0a81…3cd6](https://etherscan.io/address/0x0a81cae9009ae37427f397894ed6fd8b5fc93cd6) -230.006123 USDC (-$229.97); [0x5e6c…1115](https://etherscan.io/address/0x5e6caf3bd306db5a3df6db915e04bcfff24f1115) -200.851329 USDC (-$200.82); [0x9e24…4927](https://etherscan.io/address/0x9e2497f033d276a2ca272eef5cd31daf8df44927) -200.422645 USDC (-$200.39).

Event families: ERC20_Transfer_shape ×15.

_No qualitative note yet for this transaction._

### A70. [0x4c6d…5c88](https://etherscan.io/tx/0x4c6d71d827d3a5c76757e64d0ef489369245a1c7c123efe92aa4c1521e585c88): not yet annotated

Selected for known type audit (exchange_internal_transfer). Cluster audit-exchange_internal_transfer: 1,601 transactions from 99 senders, $750,401,491, shape transfers-only. Block 25,905,025 at 2026-09-04T16:03:11+00:00, index 49/384, type 0x2, success. From [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) (an EOA; window profile: many_sources, very_high_nonce, 983 sent to 22 destinations, nonce 1,679,050 to 1,680,032) to [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) (a contract of 2,186 bytes; contract_like, never_sends, called 165686 times in the window). Selector `0xa9059cbb`, calldata 68 bytes, value 0 ETH, 1 logs, tip 2.25 gwei. Largest position change $149,406 (USDC at [0xa7af…e05d](https://etherscan.io/address/0xa7af2a159cebdb41aa72fd562cbd5cf32798e05d)); gross $149,406; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) nets USDC -$149,406 against [0xa7af…e05d](https://etherscan.io/address/0xa7af2a159cebdb41aa72fd562cbd5cf32798e05d) (an EOA; many_sources).

Net flows: [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) -149,426.58 USDC (-$149,406); [0xa7af…e05d](https://etherscan.io/address/0xa7af2a159cebdb41aa72fd562cbd5cf32798e05d) +149,426.58 USDC ($149,406).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A71. [0x8a6a…c8d7](https://etherscan.io/tx/0x8a6a50ba15f64f99eb288be0194792af1e1a9a6437dafa53d1b73b1c4292c8d7): not yet annotated

Selected for known type audit (liquidity_remove). Cluster audit-liquidity_remove: 155 transactions from 99 senders, $25,422,908, shape V3Burn,V3Collect,V3DecreaseLiquidity,V3NFPMCollect. Block 25,905,046 at 2026-09-04T16:07:35+00:00, index 108/385, type 0x2, success. From [0x8337…3596](https://etherscan.io/address/0x833777562a32978ca07c11885aeb58bf9c4c3596) (an EOA; window profile: no tags, 9 sent to 5 destinations, nonce 82 to 90) to [0xc364…fe88](https://etherscan.io/address/0xc36442b4a4522e871399cd717abdd847ab11fe88) (a contract of 24,384 bytes; contract_like, many_sources, never_sends, router_like, called 1123 times in the window). Selector `0xac9650d8`, calldata 548 bytes, value 0 ETH, 6 logs, tip 2 gwei. Largest position change $23,568 (WBTC at [0x9db9…425b](https://etherscan.io/address/0x9db9e0e53058c89e5b94e29621a205198648425b)); gross $29,654; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x8337…3596](https://etherscan.io/address/0x833777562a32978ca07c11885aeb58bf9c4c3596) nets USDT $6,085, WBTC $23,568 against [0x9db9…425b](https://etherscan.io/address/0x9db9e0e53058c89e5b94e29621a205198648425b) (a contract of 22,142 bytes; never_sends, pool).

Net flows: [0x8337…3596](https://etherscan.io/address/0x833777562a32978ca07c11885aeb58bf9c4c3596) +0.295718 WBTC ($23,568); [0x9db9…425b](https://etherscan.io/address/0x9db9e0e53058c89e5b94e29621a205198648425b) -0.295718 WBTC (-$23,568); [0x8337…3596](https://etherscan.io/address/0x833777562a32978ca07c11885aeb58bf9c4c3596) +6,085.13 USDT ($6,085); [0x9db9…425b](https://etherscan.io/address/0x9db9e0e53058c89e5b94e29621a205198648425b) -6,085.13 USDT (-$6,085).

Event families: ERC20_Transfer_shape ×2, V3Burn ×1, V3Collect ×1, V3DecreaseLiquidity ×1, V3NFPMCollect ×1.

_No qualitative note yet for this transaction._

### A72. [0xa1ca…3f11](https://etherscan.io/tx/0xa1ca84a918df401a63e9bd9076f6151501e7c6176d0146cac3fe48699d523f11): not yet annotated

Selected for known type audit (vault_deposit). Cluster audit-vault_deposit: 198 transactions from 131 senders, $113,844,102, shape ERC4626Deposit. Block 25,905,108 at 2026-09-04T16:19:59+00:00, index 342/367, type 0x2, success. From [0x954d…8fc1](https://etherscan.io/address/0x954de9824b3c0d8d4f0efd3e46d5891689608fc1) (an EOA; window profile: no tags, 13 sent to 7 destinations, nonce 753 to 765) to [0x9fb7…1b33](https://etherscan.io/address/0x9fb7b4477576fe5b32be4c1843afb1e55f251b33) (a contract of 19,617 bytes; contract_like, never_sends, called 57 times in the window). Selector `0x6e553f65`, calldata 68 bytes, value 0 ETH, 4 logs, tip 1E-7 gwei. Largest position change $250,617 (USDC at [0x954d…8fc1](https://etherscan.io/address/0x954de9824b3c0d8d4f0efd3e46d5891689608fc1)); gross $250,617; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x954d…8fc1](https://etherscan.io/address/0x954de9824b3c0d8d4f0efd3e46d5891689608fc1) nets USDC -$250,617 against [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) (a contract of 4,462 bytes; many_sources, never_sends).

Net flows: [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) +250,652.17 USDC ($250,617); [0x954d…8fc1](https://etherscan.io/address/0x954de9824b3c0d8d4f0efd3e46d5891689608fc1) -250,652.17 USDC (-$250,617).

Unpriced ERC-20 transfers: [fUSDC (self-reported)](https://etherscan.io/address/0x9fb7b4477576fe5b32be4c1843afb1e55f251b33) ×1 (largest raw 206342825946).

Event families: ERC20_Transfer_shape ×2, ERC4626Deposit ×1, unknown ×1. Unknown topics: [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) 0x4d93b232a24e82b2… ×1.

_No qualitative note yet for this transaction._

### A73. [0x666d…47de](https://etherscan.io/tx/0x666dc0260ff0337dba108e9a5d34f3b8ed1c0d53181cdb6c0530151ed5f747de): not yet annotated

Selected for known type audit (liquidity_with_swap). Cluster audit-liquidity_with_swap: 438 transactions from 98 senders, $68,380,411, shape ERC721_Transfer_shape,EntryPointBeforeExecution,SafeModuleSuccess,UserOperation,V3IncreaseLiquidity,V3Mint,V3Swap. Block 25,905,111 at 2026-09-04T16:20:35+00:00, index 113/330, type 0x2, success. From [0xce54…f556](https://etherscan.io/address/0xce54f65abb8b61b83c14cbe97de97fce75bbf556) (an EOA; window profile: very_high_nonce, 3944 sent to 4 destinations, nonce 50,184 to 54,127) to [0x0000…a032](https://etherscan.io/address/0x0000000071727de22e5e9d8baf0edac6f37da032) (a contract of 16,035 bytes; contract_like, never_sends, router_like, called 16413 times in the window). Selector `0x765e827f`, calldata 9,572 bytes, value 0 ETH, 143 logs, tip 0.01 gwei. Largest position change $18,094 (WETH at [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f)); gross $65,713; swaps 9 in 2 pools; 5 distinct recipients. Principal [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) nets nothing priced against [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) (a contract of 22,142 bytes; many_sources, never_sends, pool).

Net flows: [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) -7.343443 WETH (-$18,094); [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) +7.343443 WETH ($18,094); [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) +18,026.77 USDC ($18,024); [0x2bf5…322b](https://etherscan.io/address/0x2bf5ae9e230a81243b56e951f093328cb03f322b) -8,820.95 USDC (-$8,820); [0x2515…cd6b](https://etherscan.io/address/0x25154ea5f0070661b6406d218bf00ca47367cd6b) -4,606.71 USDC (-$4,606); [0x40e2…f16e](https://etherscan.io/address/0x40e2b1e7ed8a7c52fbf95e8b50390fc99896f16e) -4,599.11 USDC (-$4,598); [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) -0.000154 WBTC (-$12.26); [0x2bf5…322b](https://etherscan.io/address/0x2bf5ae9e230a81243b56e951f093328cb03f322b) +0.000100 WBTC ($7.96).

Event families: SafeModuleSuccess ×39, unknown ×39, Approval ×24, ERC20_Transfer_shape ×21, V3Swap ×9, ERC721_Transfer_shape ×3, V3IncreaseLiquidity ×3, V3Mint ×3, EntryPointBeforeExecution ×1, UserOperation ×1. Unknown topics: [0x18a5…7e1b](https://etherscan.io/address/0x18a5aef2a1f49e5bd726626c76dd0aa8e9747e1b) 0xbbff709987512d10… ×18; [0x18a5…7e1b](https://etherscan.io/address/0x18a5aef2a1f49e5bd726626c76dd0aa8e9747e1b) 0x51d227421d0c4d5d… ×6; [0x0000…8ba3](https://etherscan.io/address/0x000000000022d473030f116ddee9f6b43ac78ba3) 0xda9fa7c1b00402c1… ×6; [0x231c…dd3d](https://etherscan.io/address/0x231c2027bbda204f557a7ace70a234cc33f4dd3d) 0x51d227421d0c4d5d… ×6; [0x231c…dd3d](https://etherscan.io/address/0x231c2027bbda204f557a7ace70a234cc33f4dd3d) 0x971f0df02a5f88a1… ×3.

_No qualitative note yet for this transaction._

### A74. [0xf391…0355](https://etherscan.io/tx/0xf391953eed7e8492180ae073e9465989866c0ad64e62fadeae2aa749fbba0355): not yet annotated

Selected for known type audit (dex_swap_direct_pool). Cluster audit-dex_swap_direct_pool: 75 transactions from 25 senders, $8,546,110, shape CurveTokenExchange. Block 25,905,184 at 2026-09-04T16:35:11+00:00, index 118/344, type 0x2, success. From [0x3d5e…bfdf](https://etherscan.io/address/0x3d5e4af8ef2fb321f4cf35475e75172155bdbfdf) (an EOA delegated (EIP-7702) to [0x63c0…e32b](https://etherscan.io/address/0x63c0c19a282a1b52b07dd5a65b58948a07dae32b); window profile: pass_through, 5 sent to 5 destinations, nonce 249 to 253) to [0xe521…6c45](https://etherscan.io/address/0xe521ba88837b2726e5343cca91ada6f19f356c45) (a contract of 23,635 bytes; contract_like, never_sends, pool, router_like, called 126 times in the window). Selector `0x3df02124`, calldata 132 bytes, value 0 ETH, 3 logs, tip 2 gwei. Largest position change $17,974 (IMPL:0xa1fa…33f8 at [0xe521…6c45](https://etherscan.io/address/0xe521ba88837b2726e5343cca91ada6f19f356c45)); gross $35,947; swaps 1 in 1 pools; 2 distinct recipients. Principal [0x3d5e…bfdf](https://etherscan.io/address/0x3d5e4af8ef2fb321f4cf35475e75172155bdbfdf) nets IMPL:0xa1fa…33f8 -$17,974, USDT $17,973 against [0xe521…6c45](https://etherscan.io/address/0xe521ba88837b2726e5343cca91ada6f19f356c45) (a contract of 23,635 bytes; contract_like, never_sends, pool, router_like).

Net flows: [0x3d5e…bfdf](https://etherscan.io/address/0x3d5e4af8ef2fb321f4cf35475e75172155bdbfdf) -17,988.25 IMPL:0xa1fa…33f8 (-$17,974); [0xe521…6c45](https://etherscan.io/address/0xe521ba88837b2726e5343cca91ada6f19f356c45) +17,988.25 IMPL:0xa1fa…33f8 ($17,974); [0x3d5e…bfdf](https://etherscan.io/address/0x3d5e4af8ef2fb321f4cf35475e75172155bdbfdf) +17,972.44 USDT ($17,973); [0xe521…6c45](https://etherscan.io/address/0xe521ba88837b2726e5343cca91ada6f19f356c45) -17,972.44 USDT (-$17,973).

Event families: ERC20_Transfer_shape ×2, CurveTokenExchange ×1.

_No qualitative note yet for this transaction._

### A75. [0xef3d…4e9f](https://etherscan.io/tx/0xef3dcf49afffc215ff3f29afd592cdce41699c53e77d92433dfe6a5ed1d24e9f): audit of operator_transfer_recorded (now unregistered_token_mint_burn): 4,560,925.55 USDG minted from the zero address to 0x264b… by a call on the token contract itself

Selected for known type audit (unregistered_token_mint_burn). Cluster audit-unregistered_token_mint_burn: 139 transactions from 44 senders, $73,222,882, shape transfers-only. Block 25,905,203 at 2026-09-04T16:38:59+00:00, index 109/337, type 0x2, success. From [0xf845…abb7](https://etherscan.io/address/0xf845a0a05cbd91ac15c3e59d126de5dfbc2aabb7) (an EOA; window profile: no tags, 9 sent to 2 destinations, nonce 3,478 to 3,486) to [0xe343…491d](https://etherscan.io/address/0xe343167631d89b6ffc58b88d6b7fb0228795491d) (a contract of 708 bytes; contract_like, never_sends, called 1516 times in the window). Selector `0x076bdc36`, calldata 68 bytes, value 0 ETH, 2 logs, tip 0.22869398 gwei. Largest position change $4,560,926 (IMPL:0xe343…491d at [0x264b…97b5](https://etherscan.io/address/0x264bd8291fae1d75db2c5f573b07faa6715997b5)); gross $4,560,926; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x264b…97b5](https://etherscan.io/address/0x264bd8291fae1d75db2c5f573b07faa6715997b5) nets nothing priced against [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) (unknown code status; no tags).

Net flows: [0x264b…97b5](https://etherscan.io/address/0x264bd8291fae1d75db2c5f573b07faa6715997b5) +0.000005 IMPL:0xe343…491d ($4,560,926).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xe343…491d](https://etherscan.io/address/0xe343167631d89b6ffc58b88d6b7fb0228795491d) 0xf5c174d57843e57f… ×1.

Interpretation (LLM, confidence high): Issuance of a dollar token the registry did not know; it was valued through the token's own pools (724 swaps, $11.6M).

Unverified: the issuer; resolve reports symbol USDG and name Global Dollar with 6 decimals.

### A76. [0xca95…2c9d](https://etherscan.io/tx/0xca959363c60d67cf2af6fa94ab47cd34e1c64fe61db71690c02856c0535b2c9d): not yet annotated

Selected for known type audit (erc20_transfer_from). Cluster audit-erc20_transfer_from: 1,385 transactions from 158 senders, $996,348,874, shape transfers-only. Block 25,905,259 at 2026-09-04T16:50:23+00:00, index 34/99, type 0x2, success. From [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) (an EOA; window profile: many_sources, very_high_nonce, 983 sent to 22 destinations, nonce 1,679,050 to 1,680,032) to [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) (a contract of 2,186 bytes; contract_like, never_sends, called 165686 times in the window). Selector `0x23b872dd`, calldata 100 bytes, value 0 ETH, 1 logs, tip 2.25 gwei. Largest position change $29,996 (USDC at [0xa6c5…6b61](https://etherscan.io/address/0xa6c522963e3496a776e2db7880acc5e21dd56b61)); gross $29,996; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) nets USDC $29,996 against [0xa6c5…6b61](https://etherscan.io/address/0xa6c522963e3496a776e2db7880acc5e21dd56b61) (an EOA; never_sends).

Net flows: [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) +30,000.00 USDC ($29,996); [0xa6c5…6b61](https://etherscan.io/address/0xa6c522963e3496a776e2db7880acc5e21dd56b61) -30,000.00 USDC (-$29,996).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A77. [0x2a25…2936](https://etherscan.io/tx/0x2a2598d4353373f6d1588605dcadb69c9c66a7b1c569b283cc5d2b84efe82936): not yet annotated

Selected for known type audit (aave_fork_lending_op). Cluster audit-aave_fork_lending_op: 83 transactions from 33 senders, $273,280,464, shape AaveRepay,AaveReserveDataUpdated,AaveScaledBurn. Block 25,905,299 at 2026-09-04T16:58:23+00:00, index 83/288, type 0x2, success. From [0x3c33…07af](https://etherscan.io/address/0x3c333e429f672db3b372105c19185648d03a07af) (an EOA; window profile: no tags, 8 sent to 5 destinations, nonce 220 to 227) to [0xc13e…e987](https://etherscan.io/address/0xc13e21b648a5ee794902342038ff3adab66be987) (a contract of 2,400 bytes; contract_like, never_sends, called 86 times in the window). Selector `0x573ade81`, calldata 132 bytes, value 0 ETH, 5 logs, tip 0.215625 gwei. Largest position change $600,179 (USDT at [0xe7df…c92f](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f)); gross $600,179; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x3c33…07af](https://etherscan.io/address/0x3c333e429f672db3b372105c19185648d03a07af) nets USDT -$600,179 against [0xe7df…c92f](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f) (a contract of 2,400 bytes; never_sends).

Net flows: [0x3c33…07af](https://etherscan.io/address/0x3c333e429f672db3b372105c19185648d03a07af) -600,153.11 USDT (-$600,179); [0xe7df…c92f](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f) +600,153.11 USDT ($600,179).

Unpriced ERC-20 transfers: [variableDebtUSDT (self-reported)](https://etherscan.io/address/0x529b6158d1d2992e3129f7c69e81a7c677dc3b12) ×1 (largest raw 600002994709).

Event families: ERC20_Transfer_shape ×2, AaveRepay ×1, AaveReserveDataUpdated ×1, AaveScaledBurn ×1.

_No qualitative note yet for this transaction._

### A78. [0xf8d2…d480](https://etherscan.io/tx/0xf8d22d46c0029b9d5930b722666b19a7c30815014991ff8623aba2beb6d0d480): audit of intent_or_rfq_fill: a UniswapX fill in which the filler pays 30,001.32 USDT and sources 29,756.99 USD of PEPE at the implied price

Selected for known type audit (intent_or_rfq_fill). Cluster audit-intent_or_rfq_fill: 469 transactions from 144 senders, $22,360,527, shape UniswapXFill. Block 25,905,319 at 2026-09-04T17:02:23+00:00, index 1/438, type 0x2, success. From [0x6f12…818a](https://etherscan.io/address/0x6f12b91bf6da752ada71b7a1a622c57d8a48818a) (an EOA; window profile: bot_sender, very_high_nonce, 158 sent to 1 destinations, nonce 102,904 to 103,061) to [0x225a…dc17](https://etherscan.io/address/0x225a38bc71102999dd13478bfabd7c4d53f2dc17) (a contract of 8,647 bytes; contract_like, many_sources, never_sends, called 316 times in the window). Selector `0xbc4a02e4`, calldata 1,860 bytes, value 0 ETH, 7 logs, tip 1.999599999 gwei. Largest position change $30,001 (USDT at [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f)); gross $119,517; swaps 0 in 0 pools; 3 distinct recipients. Principal [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) nets nothing priced against [0x479e…a68d](https://etherscan.io/address/0x479e0956f9f7f3d72fc4068e061de6954eeba68d) (an EOA delegated (EIP-7702) to [0x0000…030e](https://etherscan.io/address/0x000000005c84f8fd50b21cac312528a64437030e); never_sends).

Net flows: [0x479e…a68d](https://etherscan.io/address/0x479e0956f9f7f3d72fc4068e061de6954eeba68d) -30,000.00 USDT (-$30,001); [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) +30,000.00 USDT ($30,001); [0x479e…a68d](https://etherscan.io/address/0x479e0956f9f7f3d72fc4068e061de6954eeba68d) +8,456,211,937.81 IMPL:0x6982…1933 ($29,757); [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) -8,456,211,937.81 IMPL:0x6982…1933 (-$29,757); [0x225a…dc17](https://etherscan.io/address/0x225a38bc71102999dd13478bfabd7c4d53f2dc17) +0.000000 IMPL:0x6982…1933 ($0.00); [0x225a…dc17](https://etherscan.io/address/0x225a38bc71102999dd13478bfabd7c4d53f2dc17) +0.000000 USDT ($0.00).

Event families: ERC20_Transfer_shape ×4, Approval ×2, UniswapXFill ×1.

Interpretation (LLM, confidence high): The unpriced side is valued here because PEPE had 730 swaps against priced assets in the day; the rule and the price feed agree.

### A79. [0xaa71…095f](https://etherscan.io/tx/0xaa71163841d340702717153da0010e8bfd386503c33f3cfd98fc75d32624095f): not yet annotated

Selected for known type audit (contract_unwrap_payout). Cluster audit-contract_unwrap_payout: 100 transactions from 24 senders, $5,425,558, shape WETHWithdrawal. Block 25,905,456 at 2026-09-04T17:29:59+00:00, index 379/394, type 0x2, success. From [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) (an EOA; window profile: very_high_nonce, 2141 sent to 15 destinations, nonce 746,164 to 748,304) to [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) (a contract of 680 bytes; contract_like, many_sources, never_sends, router_like, called 9900 times in the window). Selector `0xdeff4b24`, calldata 516 bytes, value 0 ETH, 3 logs, tip 0.00001 gwei. Largest position change $36,356 (WETH at [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67)); gross $72,713; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) nets WETH -$36,356 against [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) (a contract of 680 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0x07ae…0e67](https://etherscan.io/address/0x07ae8551be970cb1cca11dd7a11f47ae82e70e67) -14.836172 WETH (-$36,356); [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) +0.000000 WETH ($0.00).

Event families: ERC20_Transfer_shape ×1, WETHWithdrawal ×1, unknown ×1. Unknown topics: [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) 0x44b559f101f8fbcc… ×1.

_No qualitative note yet for this transaction._

### A80. [0x5217…5ea1](https://etherscan.io/tx/0x52172417f835ebe63da396f1a03a5105e708caeb0254fd9e68e1cc49a39b5ea1): not yet annotated

Selected for known type audit (relay_style_deposit_observed). Cluster audit-relay_style_deposit_observed: 10 transactions from 9 senders, $397,228, shape RelayNativeDeposit,SafeReceived. Block 25,905,511 at 2026-09-04T17:40:59+00:00, index 84/214, type 0x2, success. From [0x24d6…6aa6](https://etherscan.io/address/0x24d655a4ed48bfd4291de041a1f81a11ca456aa6) (an EOA; window profile: fresh, pass_through, 1 sent to 1 destinations, nonce 0 to 0) to [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) (a contract of 6,000 bytes; contract_like, many_sources, never_sends, router_like, called 7532 times in the window). Selector `0x3ce33bff`, calldata 645 bytes, value 6.00681363821543303 ETH, 4 logs, tip 2.100000001 gwei. Largest position change $14,720 (ETH at [0x24d6…6aa6](https://etherscan.io/address/0x24d655a4ed48bfd4291de041a1f81a11ca456aa6)); gross $14,720; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x24d6…6aa6](https://etherscan.io/address/0x24d655a4ed48bfd4291de041a1f81a11ca456aa6) nets ETH -$14,720 against [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) (a contract of 6,000 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0x0439…c3f1](https://etherscan.io/address/0x0439e60f02a8900a951603950d8d4527f400c3f1) +6.006814 ETH ($14,720); [0x24d6…6aa6](https://etherscan.io/address/0x24d655a4ed48bfd4291de041a1f81a11ca456aa6) -6.006814 ETH (-$14,720).

Event families: unknown ×2, RelayNativeDeposit ×1, SafeReceived ×1. Unknown topics: [0x9a47…ed16](https://etherscan.io/address/0x9a47f3289794e9bbc6a3c571f6d96ad4e7baed16) 0x6ded982279c8387a… ×1; [0x9a47…ed16](https://etherscan.io/address/0x9a47f3289794e9bbc6a3c571f6d96ad4e7baed16) 0x831bac9533a20342… ×1.

_No qualitative note yet for this transaction._

### A81. [0x8ae2…7fd2](https://etherscan.io/tx/0x8ae271114c4bc2ef23b4545161e09c86de921ba965d7224754871da969877fd2): not yet annotated

Selected for known type audit (operator_token_batch). Cluster audit-operator_token_batch: 432 transactions from 6 senders, $97,438,885, shape transfers-only. Block 25,905,524 at 2026-09-04T17:43:35+00:00, index 47/235, type 0x2, success. From [0x5060…b54c](https://etherscan.io/address/0x5060720e59dd975b16318a2f664eee645515b54c) (an EOA; window profile: hot_wallet, 602 sent to 129 destinations, nonce 4,947 to 5,548) to [0xee39…63b5](https://etherscan.io/address/0xee39678386f5bfc68df2c65656ec8e23f60063b5) (a contract of 122 bytes; contract_like, never_sends, called 3383 times in the window). Selector `0xe4c705e9`, calldata 388 bytes, value 0 ETH, 2 logs, tip 2 gwei. Largest position change $199,972 (USDC at [0x5dc8…dbdb](https://etherscan.io/address/0x5dc80f3d8bf2d1d26f93068cf0bdb9d9ff19dbdb)); gross $199,972; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x5dc8…dbdb](https://etherscan.io/address/0x5dc80f3d8bf2d1d26f93068cf0bdb9d9ff19dbdb) nets nothing priced against [0x05ff…f381](https://etherscan.io/address/0x05ff6964d21e5dae3b1010d5ae0465b3c450f381) (an EOA; hot_wallet, many_sources, very_high_nonce).

Net flows: [0x05ff…f381](https://etherscan.io/address/0x05ff6964d21e5dae3b1010d5ae0465b3c450f381) +200,000.00 USDC ($199,972); [0x5dc8…dbdb](https://etherscan.io/address/0x5dc80f3d8bf2d1d26f93068cf0bdb9d9ff19dbdb) -200,000.00 USDC (-$199,972).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xee39…63b5](https://etherscan.io/address/0xee39678386f5bfc68df2c65656ec8e23f60063b5) 0xdf423376f9b0ab36… ×1.

_No qualitative note yet for this transaction._

### A82. [0x18e0…cfde](https://etherscan.io/tx/0x18e074ab8541206202d2f372eaf901625bc133b7b5d40b1b493bbb530615cfde): not yet annotated

Selected for known type audit (swap_other). Cluster audit-swap_other: 1,485 transactions from 601 senders, $66,862,040, shape V4Swap,WETHWithdrawal. Block 25,905,562 at 2026-09-04T17:51:11+00:00, index 3/117, type 0x2, success. From [0x7049…8957](https://etherscan.io/address/0x7049a18279500a25864c509137d7de4ff0048957) (an EOA; window profile: bot_sender, very_high_nonce, 94 sent to 1 destinations, nonce 76,035 to 76,128) to [0x93c3…dd17](https://etherscan.io/address/0x93c30e6e09f698cfea99b09b5166ed90cfaedd17) (a contract of 24,313 bytes; contract_like, never_sends, router_like, called 3640 times in the window). Selector `0x0fe20a3f`, calldata 196 bytes, value 0 ETH, 4 logs, tip 0 gwei. Largest position change $23,916 (WETH at [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f)); gross $71,689; swaps 1 in 1 pools; 2 distinct recipients. Principal [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) nets nothing priced against [0x93c3…dd17](https://etherscan.io/address/0x93c30e6e09f698cfea99b09b5166ed90cfaedd17) (a contract of 24,313 bytes; contract_like, never_sends, router_like).

Net flows: [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) -9.759682 WETH (-$23,916); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) -23,859.92 USDC (-$23,857); [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) +23,859.92 USDC ($23,857); [0x93c3…dd17](https://etherscan.io/address/0x93c30e6e09f698cfea99b09b5166ed90cfaedd17) +0.000000 WETH ($0.00).

Event families: ERC20_Transfer_shape ×2, V4Swap ×1, WETHWithdrawal ×1.

_No qualitative note yet for this transaction._

### A83. [0xbe99…cc8a](https://etherscan.io/tx/0xbe994ecd00c8b86851f1e6eae774aa6aed0f6a1b209615d16339be8e2e05cc8a): not yet annotated

Selected for known type audit (lending_with_swap). Cluster audit-lending_with_swap: 336 transactions from 43 senders, $242,350,608, shape AaveRepay,AaveReserveDataUpdated,AaveScaledBurn,AaveWithdraw,ReserveUsedAsCollateralDisabled,V3Swap,V4ModifyLiquidity,V4Swap. Block 25,905,895 at 2026-09-04T18:58:23+00:00, index 2/249, type 0x2, success. From [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) (an EOA; window profile: bot_sender, very_high_nonce, 366 sent to 1 destinations, nonce 86,834 to 87,199) to [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) (a contract of 20,518 bytes; contract_like, many_sources, never_sends, router_like, called 366 times in the window). Selector `0x8b578ac6`, calldata 2,468 bytes, value 5.38E-16 ETH, 20 logs, tip 18.890372239 gwei. Largest position change $381,994 (WETH at [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb)); gross $997,695; swaps 2 in 2 pools; 3 distinct recipients. Principal [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) nets USDT $462.86, WETH $381,994 against [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) (a contract of 2,400 bytes; contract_like, never_sends). Sandwich marks: [{"front": "0xa452743d90278b5f32a7dbb3d7854d8c5f145ed1f61f28357d596b54701a1ca3", "pool": "0x000000000004444c5dc75cb358380d2e3de08a90:0x2287a9620adcbf6250dc71be9ee9b2d3a1ec85a464fc6f5c06669e8d07b61bba", "role": "back", "victim": "0x6817885ce62fdc32eada28a4df9c8e76a9275b7f746831c4dc92d4b1c31a3f28", "v.

Net flows: [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) +156.142630 WETH ($381,994); [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) -156.119973 WETH (-$381,938); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) -308,068.71 USDT (-$308,082); [0x2387…086a](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a) +307,550.33 USDT ($307,564); [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) +462.839919 USDT ($462.86); [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) +55.541208 USDT ($55.54); [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) -0.022657 WETH (-$55.43); [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) -0.000000 ETH ($0.00).

Unpriced ERC-20 transfers: [variableDebtEthUSDT (self-reported)](https://etherscan.io/address/0x6df1c1e379bc5a00a7b4c6e67a203333772f45a8) ×1 (largest raw 307550330680), [aEthWETH (self-reported)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) ×1 (largest raw 156119972764619046912).

Event families: ERC20_Transfer_shape ×8, AaveReserveDataUpdated ×2, AaveScaledBurn ×2, Approval ×2, AaveRepay ×1, AaveWithdraw ×1, ReserveUsedAsCollateralDisabled ×1, V3Swap ×1, V4ModifyLiquidity ×1, V4Swap ×1.

_No qualitative note yet for this transaction._

### A84. [0xd2f3…454e](https://etherscan.io/tx/0xd2f3855faabe1727d2976f3fd159f45fc151c857a7632a9bb1fce6a9245d454e): audit of restaking_or_lst_other: a bot (very_high_nonce) wraps ETH, moves it through an Aave reserve and mints or burns an LST inside one atomic strategy

Selected for known type audit (restaking_or_lst_other). Cluster audit-restaking_or_lst_other: 16 transactions from 11 senders, $1,263,725, shape AaveReserveDataUpdated,AaveScaledMint,AaveSupply,ERC4626Deposit,RocketTokensBurned,WETHDeposit,WETHWithdrawal. Block 25,905,947 at 2026-09-04T19:08:47+00:00, index 17/160, type 0x0, success. From [0x0124…bc10](https://etherscan.io/address/0x0124d0fa0dfb1430dfcff16ec6a96945e7a0bc10) (an EOA; window profile: bot_sender, very_high_nonce, 40 sent to 1 destinations, nonce 152,574 to 152,613) to [0x3633…e95c](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) (an EOA delegated (EIP-7702) to [0xd5c7…ce8d](https://etherscan.io/address/0xd5c74a2e83c754f849876847606570f15b4cce8d); contract_like, many_sources, never_sends, router_like, called 91 times in the window). Selector `0xca8bd1f9`, calldata 836 bytes, value 0 ETH, 18 logs, tip 0 gwei. Largest position change $57,823 (rETH at [0xba13…9ba9](https://etherscan.io/address/0xba1333333333a1ba1108e8412f11850a5c319ba9)); gross $404,111; swaps 0 in 0 pools; 4 distinct recipients. Principal [0xba13…9ba9](https://etherscan.io/address/0xba1333333333a1ba1108e8412f11850a5c319ba9) nets nothing priced against [0x3633…e95c](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) (an EOA delegated (EIP-7702) to [0xd5c7…ce8d](https://etherscan.io/address/0xd5c74a2e83c754f849876847606570f15b4cce8d); contract_like, many_sources, never_sends, router_like).

Net flows: [0xba13…9ba9](https://etherscan.io/address/0xba1333333333a1ba1108e8412f11850a5c319ba9) -20.080805 rETH (-$57,823); [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) +23.456432 WETH ($57,578); [0x0bfc…1202](https://etherscan.io/address/0x0bfc9d54fc184518a81162f8fb99c2eaca081202) +0.000000 WETH ($0.00); [0x3633…e95c](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) +0.000000 rETH ($0.00); [0x3633…e95c](https://etherscan.io/address/0x36331e299247e5d0d3261e1d9852f6e0cffee95c) +0.000000 WETH ($0.00).

Unpriced ERC-20 transfers: [waEthWETH (self-reported)](https://etherscan.io/address/0x0bfc9d54fc184518a81162f8fb99c2eaca081202) ×2 (largest raw 21915873790827204262), [aEthWETH (self-reported)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) ×1 (largest raw 23456859705810843783).

Event families: ERC20_Transfer_shape ×7, WETHDeposit ×2, WETHWithdrawal ×2, AaveReserveDataUpdated ×1, AaveScaledMint ×1, AaveSupply ×1, Approval ×1, ERC4626Deposit ×1, RocketTokensBurned ×1, unknown ×1. Unknown topics: [0xba13…9ba9](https://etherscan.io/address/0xba1333333333a1ba1108e8412f11850a5c319ba9) 0x0874b2d545cb271c… ×1.

Interpretation (LLM, confidence medium): The label misdescribes this occurrence: the LST mint is a leg of an arbitrage, not a staking decision. Sixteen occurrences, $1.3M, so the correction is cheap and deferred to the next run.

Proposed type: `exclude bot_sender and very_high_nonce senders from restaking_or_lst_other, or rank the atomic-strategy rules before it`

### A85. [0xe4fd…428b](https://etherscan.io/tx/0xe4fde5b6fac329943c7b0274cd982105ddb14b03c0a2244f08a2f815e146428b): audit of sandwich_attack: bot EOA 0x3ee92cd0… through 0x9205a569… sells WBTC for WETH ($12,602.65) around a stranger's swap in the same pool and block

Selected for known type audit (sandwich_attack). Cluster audit-sandwich_attack: 136 transactions from 12 senders, $7,691,373, shape V3Swap. Block 25,906,139 at 2026-09-04T19:47:11+00:00, index 27/254, type 0x2, success. From [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) (an EOA; window profile: bot_sender, very_high_nonce, 366 sent to 1 destinations, nonce 86,834 to 87,199) to [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) (a contract of 20,518 bytes; contract_like, many_sources, never_sends, router_like, called 366 times in the window). Selector `0x8b578ac6`, calldata 452 bytes, value 3.55E-16 ETH, 3 logs, tip 0 gwei. Largest position change $12,603 (WETH at [0xe6ff…e718](https://etherscan.io/address/0xe6ff8b9a37b0fab776134636d9981aa778c4e718)); gross $25,157; swaps 1 in 1 pools; 2 distinct recipients. Principal [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) nets WBTC $12,555, WETH -$12,603 against [0xe6ff…e718](https://etherscan.io/address/0xe6ff8b9a37b0fab776134636d9981aa778c4e718) (a contract of 22,142 bytes; many_sources, never_sends, pool). Sandwich marks: [{"back": "0x2aea825a28901a81c45ccbd73c388bcb51c0c15c58f1ebcf760f3ce790e7f6f5", "pool": "0xe6ff8b9a37b0fab776134636d9981aa778c4e718", "role": "front", "victim": "0xa569351613580d3b44e3d86f15d552d2f7400b9268e77399f57c5fc281965c6f", "victim_index": 28, "victims": 1}].

Net flows: [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) -5.134129 WETH (-$12,603); [0xe6ff…e718](https://etherscan.io/address/0xe6ff8b9a37b0fab776134636d9981aa778c4e718) +5.134129 WETH ($12,603); [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) +0.157530 WBTC ($12,555); [0xe6ff…e718](https://etherscan.io/address/0xe6ff8b9a37b0fab776134636d9981aa778c4e718) -0.157530 WBTC (-$12,555); [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) -0.000000 ETH ($0.00); [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) +0.000000 ETH ($0.00).

Event families: ERC20_Transfer_shape ×2, V3Swap ×1.

Interpretation (LLM, confidence medium): The scan's bracketing rule holds; the economics are outside receipts.

Unverified: profit; the observed net of this bot over its 32 legs is $462, so the payoff is either in the unwrapped ETH or paid to the builder.

### A86. [0x691a…65b0](https://etherscan.io/tx/0x691a2c9aff5a97ee47c9fe451d94bc5a5adfc32b00464a9d3309ae7260e465b0): not yet annotated

Selected for known type audit (contract_creation). Cluster audit-contract_creation: 1 transactions from 1 senders, $36,820, shape value-only. Block 25,906,154 at 2026-09-04T19:50:11+00:00, index 154/403, type 0x2, success. From [0xee6b…54eb](https://etherscan.io/address/0xee6ba7de7f934ba5a1a417a67412801d6eb654eb) (an EOA; window profile: no tags, 7 sent to 3 destinations, nonce 8 to 14) to creation of [0x43c0…81b3](https://etherscan.io/address/0x43c09d101c7d3159b24502fdbaaca62124f081b3). Selector `0x60806040`, calldata 837 bytes, value 15 ETH, 0 logs, tip 0.6 gwei. Largest position change $36,820 (ETH at [0xee6b…54eb](https://etherscan.io/address/0xee6ba7de7f934ba5a1a417a67412801d6eb654eb)); gross $36,820; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xee6b…54eb](https://etherscan.io/address/0xee6ba7de7f934ba5a1a417a67412801d6eb654eb) nets ETH -$36,820 against [0x43c0…81b3](https://etherscan.io/address/0x43c09d101c7d3159b24502fdbaaca62124f081b3) (an EOA; never_sends).

Net flows: [0x43c0…81b3](https://etherscan.io/address/0x43c09d101c7d3159b24502fdbaaca62124f081b3) +15.000000 ETH ($36,820); [0xee6b…54eb](https://etherscan.io/address/0xee6ba7de7f934ba5a1a417a67412801d6eb654eb) -15.000000 ETH (-$36,820).

Event families: none.

_No qualitative note yet for this transaction._

### A87. [0x4a60…1b18](https://etherscan.io/tx/0x4a60d67b773b569bf30b92f989942035c0e717f115855fce83048dabebd51b18): not yet annotated

Selected for known type audit (contract_payout_by_operator). Cluster audit-contract_payout_by_operator: 1,262 transactions from 188 senders, $288,628,470, shape transfers-only. Block 25,906,155 at 2026-09-04T19:50:23+00:00, index 210/244, type 0x2, success. From [0xa00e…e4af](https://etherscan.io/address/0xa00e5aee3fb82158ab4d6a1d2d8494813efae4af) (an EOA; window profile: no tags, 8 sent to 3 destinations, nonce 744 to 751) to [0xfbca…0bb6](https://etherscan.io/address/0xfbca8b5f5794456b59ad4177e5b212d0db600bb6) (a contract of 4,889 bytes; never_sends, called 3 times in the window). Selector `0x11858c7a`, calldata 644 bytes, value 0 ETH, 2 logs, tip 0.000038655 gwei. Largest position change $1,000,000 (RLUSD at [0xfbca…0bb6](https://etherscan.io/address/0xfbca8b5f5794456b59ad4177e5b212d0db600bb6)); gross $1,000,000; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xfbca…0bb6](https://etherscan.io/address/0xfbca8b5f5794456b59ad4177e5b212d0db600bb6) nets RLUSD -$1,000,000 against [0xa1d0…d688](https://etherscan.io/address/0xa1d01ae763b6355144280f371eeca5742492d688) (an EOA; no tags).

Net flows: [0xa1d0…d688](https://etherscan.io/address/0xa1d01ae763b6355144280f371eeca5742492d688) +1,000,000.00 RLUSD ($1,000,000); [0xfbca…0bb6](https://etherscan.io/address/0xfbca8b5f5794456b59ad4177e5b212d0db600bb6) -1,000,000.00 RLUSD (-$1,000,000).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xfbca…0bb6](https://etherscan.io/address/0xfbca8b5f5794456b59ad4177e5b212d0db600bb6) 0x12755f149014f092… ×1.

_No qualitative note yet for this transaction._

### A88. [0x748d…67af](https://etherscan.io/tx/0x748df9d39469963cf5c3ac666abd92404ac96d6b1279164f21f41596f21e67af): not yet annotated

Selected for known type audit (wrapped_btc_mint_burn). Cluster audit-wrapped_btc_mint_burn: 18 transactions from 9 senders, $105,233,336, shape transfers-only. Block 25,906,261 at 2026-09-04T20:11:35+00:00, index 186/263, type 0x2, success. From [0x4533…2c19](https://etherscan.io/address/0x45332eee9b495b1dda896fd53112eaacc10b2c19) (an EOA; window profile: no tags, 4 sent to 3 destinations, nonce 4,120 to 4,123) to [0x5d4d…dbde](https://etherscan.io/address/0x5d4d83aab53b7e7ca915aeb2d4d3f4e03823dbde) (a contract of 2,214 bytes; never_sends, called 1 times in the window). Selector `0xb6e92015`, calldata 1,284 bytes, value 0 ETH, 13 logs, tip 1.5 gwei. Largest position change $15,949 (tBTC at [0x3ee1…a585](https://etherscan.io/address/0x3ee18b2214aff97000d974cf647e7c347e8fa585)); gross $31,897; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x3ee1…a585](https://etherscan.io/address/0x3ee18b2214aff97000d974cf647e7c347e8fa585) nets nothing priced against [0x5d4d…dbde](https://etherscan.io/address/0x5d4d83aab53b7e7ca915aeb2d4d3f4e03823dbde) (a contract of 2,214 bytes; never_sends).

Net flows: [0x3ee1…a585](https://etherscan.io/address/0x3ee18b2214aff97000d974cf647e7c347e8fa585) -0.200000 tBTC (-$15,949); [0x5d4d…dbde](https://etherscan.io/address/0x5d4d83aab53b7e7ca915aeb2d4d3f4e03823dbde) +0.000000 tBTC ($0.00).

Event families: unknown ×8, Approval ×3, ERC20_Transfer_shape ×2. Unknown topics: [0x65fb…9fc6](https://etherscan.io/address/0x65fbae61ad2c8836ffbfb502a0da41b0789d9fc6) 0x4163d0b06696468b… ×2; [0x65fb…9fc6](https://etherscan.io/address/0x65fbae61ad2c8836ffbfb502a0da41b0789d9fc6) 0x2fe5e8e779601073… ×2; [0x3ee1…a585](https://etherscan.io/address/0x3ee18b2214aff97000d974cf647e7c347e8fa585) 0xcaf280c8cfeba144… ×1; [0x9c07…e3cd](https://etherscan.io/address/0x9c070027cdc9dc8f82416b2e5314e11dfb4fe3cd) 0x68751a4c3821398c… ×1; [0x5e48…8e7b](https://etherscan.io/address/0x5e4861a80b55f035d899f66772117f00fa0e8e7b) 0x97a0199072f48723… ×1; [0x5d4d…dbde](https://etherscan.io/address/0x5d4d83aab53b7e7ca915aeb2d4d3f4e03823dbde) 0xae8d85ba71600399… ×1.

_No qualitative note yet for this transaction._

### A89. [0xa97d…aea0](https://etherscan.io/tx/0xa97d03a63e9900464537cbc1983bd8603291f575937443b67e7eb24494a9aea0): not yet annotated

Selected for known type audit (morpho_op). Cluster audit-morpho_op: 943 transactions from 275 senders, $178,404,971, shape MorphoSupplyCollateral. Block 25,906,284 at 2026-09-04T20:16:11+00:00, index 107/239, type 0x2, success. From [0x9f0d…f952](https://etherscan.io/address/0x9f0dca77e93a980750a6d1102c54d4713d7df952) (an EOA; window profile: pass_through, 98 sent to 4 destinations, nonce 1,430 to 1,527) to [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) (a contract of 15,623 bytes; contract_like, flash_lender, many_sources, never_sends, called 273 times in the window). Selector `0x238d6579`, calldata 292 bytes, value 0 ETH, 3 logs, tip 2 gwei. Largest position change $20,058 (IMPL:0x22ae…d4c7 at [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb)); gross $20,058; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x9f0d…f952](https://etherscan.io/address/0x9f0dca77e93a980750a6d1102c54d4713d7df952) nets IMPL:0x22ae…d4c7 -$20,058 against [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) (a contract of 15,623 bytes; contract_like, flash_lender, many_sources, never_sends).

Net flows: [0x9f0d…f952](https://etherscan.io/address/0x9f0dca77e93a980750a6d1102c54d4713d7df952) -0.000000 IMPL:0x22ae…d4c7 (-$20,058); [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) +0.000000 IMPL:0x22ae…d4c7 ($20,058).

Event families: Approval ×1, ERC20_Transfer_shape ×1, MorphoSupplyCollateral ×1.

_No qualitative note yet for this transaction._

### A90. [0x198d…784f](https://etherscan.io/tx/0x198d1dfae41e92a976ff5f48eee037bd5ffa310736d2bfc6e3b1fd5485fe784f): not yet annotated

Selected for known type audit (contract_token_execution). Cluster audit-contract_token_execution: 1,593 transactions from 24 senders, $734,610,485, shape transfers-only. Block 25,906,447 at 2026-09-04T20:48:47+00:00, index 70/384, type 0x2, success. From [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) (an EOA; window profile: hot_wallet, many_sources, very_high_nonce, 13267 sent to 1945 destinations, nonce 18,134,426 to 18,147,692) to [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) (a contract of 209 bytes; contract_like, many_sources, never_sends, called 3705 times in the window). Selector `0xb61d27f6`, calldata 228 bytes, value 0 ETH, 1 logs, tip 1 gwei. Largest position change $709,959 (USDC at [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055)); gross $709,959; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) nets USDC -$709,959 against [0xbee3…a000](https://etherscan.io/address/0xbee3211ab312a8d065c4fef0247448e17a8da000) (a contract of 1,855 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0xbee3…a000](https://etherscan.io/address/0xbee3211ab312a8d065c4fef0247448e17a8da000) +710,059.40 USDC ($709,959); [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) -710,059.40 USDC (-$709,959).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A91. [0xef60…d3c9](https://etherscan.io/tx/0xef60b40c6eccb9a70d64cb2040e65bd4b52797d0e319a40f5cde10e719b5d3c9): not yet annotated

Selected for known type audit (claim_distribution). Cluster audit-claim_distribution: 8 transactions from 5 senders, $365,653, shape ClaimedIAU,ERC721_Transfer_shape. Block 25,906,454 at 2026-09-04T20:50:11+00:00, index 140/227, type 0x2, success. From [0xc163…42bc](https://etherscan.io/address/0xc163632549ce4e38386a02bc1734c04f0fc142bc) (an EOA; window profile: no tags, 17 sent to 8 destinations, nonce 249 to 265) to [0x4bc9…3d2e](https://etherscan.io/address/0x4bc9fec04f0f95e9b42a3ef18f3c96fb57923d2e) (a contract of 163 bytes; never_sends, called 18 times in the window). Selector `0x379607f5`, calldata 36 bytes, value 0 ETH, 3 logs, tip 0.021876286 gwei. Largest position change $20,006 (IMPL:0x2323…aa71 at [0xc163…42bc](https://etherscan.io/address/0xc163632549ce4e38386a02bc1734c04f0fc142bc)); gross $20,006; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xc163…42bc](https://etherscan.io/address/0xc163632549ce4e38386a02bc1734c04f0fc142bc) nets IMPL:0x2323…aa71 $20,006 against [0x4bc9…3d2e](https://etherscan.io/address/0x4bc9fec04f0f95e9b42a3ef18f3c96fb57923d2e) (a contract of 163 bytes; never_sends).

Net flows: [0x4bc9…3d2e](https://etherscan.io/address/0x4bc9fec04f0f95e9b42a3ef18f3c96fb57923d2e) -0.000000 IMPL:0x2323…aa71 (-$20,006); [0xc163…42bc](https://etherscan.io/address/0xc163632549ce4e38386a02bc1734c04f0fc142bc) +0.000000 IMPL:0x2323…aa71 ($20,006).

Event families: ClaimedIAU ×1, ERC20_Transfer_shape ×1, ERC721_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A92. [0x0940…66a6](https://etherscan.io/tx/0x094034dfad0d39fe704417f5f7a5bc43d3789bd202f56271b1ec2f64779866a6): not yet annotated

Selected for known type audit (liquidity_add). Cluster audit-liquidity_add: 165 transactions from 87 senders, $27,522,063, shape V2Mint,V2PairCreated,WETHDeposit. Block 25,906,501 at 2026-09-04T20:59:35+00:00, index 42/204, type 0x0, success. From [0x581d…0f89](https://etherscan.io/address/0x581da5508cddb6fb2831a80628fb8c2988890f89) (an EOA; window profile: fresh, 8 sent to 4 destinations, nonce 0 to 7) to [0x7a25…488d](https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d) (a contract of 21,943 bytes; contract_like, many_sources, never_sends, router_like, called 6481 times in the window). Selector `0xf305d719`, calldata 196 bytes, value 4.1 ETH, 8 logs, tip 0.011920983 gwei. Largest position change $10,066 (WETH at [0xf622…c9ab](https://etherscan.io/address/0xf6228c5c8bb5e58d6cdc899138f740d59f9fc9ab)); gross $30,199; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x581d…0f89](https://etherscan.io/address/0x581da5508cddb6fb2831a80628fb8c2988890f89) nets ETH -$10,066 against [0x7a25…488d](https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d) (a contract of 21,943 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0x581d…0f89](https://etherscan.io/address/0x581da5508cddb6fb2831a80628fb8c2988890f89) -4.100000 ETH (-$10,066); [0x7a25…488d](https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d) +4.100000 ETH ($10,066); [0xf622…c9ab](https://etherscan.io/address/0xf6228c5c8bb5e58d6cdc899138f740d59f9fc9ab) +4.100000 WETH ($10,066); [0x7a25…488d](https://etherscan.io/address/0x7a250d5630b4cf539739df2c5dacb4c659f2488d) +0.000000 WETH ($0.00).

Unpriced ERC-20 transfers: [UNI-V2 (self-reported)](https://etherscan.io/address/0xf6228c5c8bb5e58d6cdc899138f740d59f9fc9ab) ×2 (largest raw 56223660499828717573448087), [RPK (self-reported)](https://etherscan.io/address/0x1b89793a273d20a7f09f2c61b289a07d6241e04e) ×1 (largest raw 771000000000000000000000000000000).

Event families: ERC20_Transfer_shape ×4, V2Mint ×1, V2PairCreated ×1, V2Sync ×1, WETHDeposit ×1.

_No qualitative note yet for this transaction._

### A93. [0x74ec…c728](https://etherscan.io/tx/0x74eccc26e4b4a5a3a796b91c7ca20030b56127a062fa5968db4d0f7dec90c728): not yet annotated

Selected for known type audit (cow_settlement). Cluster audit-cow_settlement: 380 transactions from 64 senders, $28,123,688, shape CoWInteraction,CoWSettlement,CoWTrade,PSMSellGem. Block 25,906,669 at 2026-09-04T21:33:23+00:00, index 37/274, type 0x2, success. From [0x5ed8…eaab](https://etherscan.io/address/0x5ed864e8f37dcb4f79c5172a815d1b3a9147eaab) (an EOA delegated (EIP-7702) to [0x74cb…8d14](https://etherscan.io/address/0x74cb78b2fb77b3f47a1a8ebb33a915b0f5658d14); window profile: bot_sender, 274 sent to 1 destinations, nonce 3,313 to 3,586) to [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) (a contract of 16,165 bytes; contract_like, many_sources, never_sends, router_like, called 1330 times in the window). Selector `0x13d79a0b`, calldata 1,452 bytes, value 0 ETH, 8 logs, tip 0.4 gwei. Largest position change $11,314 (USDC at [0x3730…7341](https://etherscan.io/address/0x37305b1cd40574e4c5ce33f8e8306be057fd7341)); gross $45,252; swaps 0 in 0 pools; 3 distinct recipients. Principal [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) nets DAI $0.53 against [0x2a42…f52c](https://etherscan.io/address/0x2a426b6b4589a3a44a053da440c45ff41e16f52c) (an EOA; no tags).

Net flows: [0x2a42…f52c](https://etherscan.io/address/0x2a426b6b4589a3a44a053da440c45ff41e16f52c) -11,315.72 USDC (-$11,314); [0x3730…7341](https://etherscan.io/address/0x37305b1cd40574e4c5ce33f8e8306be057fd7341) +11,315.72 USDC ($11,314); [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042) -11,315.72 DAI (-$11,312); [0x2a42…f52c](https://etherscan.io/address/0x2a426b6b4589a3a44a053da440c45ff41e16f52c) +11,315.19 DAI ($11,311); [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) +0.534644 DAI ($0.53); [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) +0.000000 USDC ($0.00).

Event families: ERC20_Transfer_shape ×4, CoWInteraction ×1, CoWSettlement ×1, CoWTrade ×1, PSMSellGem ×1.

_No qualitative note yet for this transaction._

### A94. [0x7b4a…2d10](https://etherscan.io/tx/0x7b4ad5b5a1bccb5e91721e85ad3e3a34a2f39e4575384c961f997ae5c4022d10): audit of dex_swap_user: hot wallet 0xf70da978… sells 100,024.22 USDC for USDG through router 0xccc88a9d… with a Uniswap v4 swap

Selected for known type audit (dex_swap_user). Cluster audit-dex_swap_user: 855 transactions from 453 senders, $117,843,622, shape V4Swap. Block 25,906,670 at 2026-09-04T21:33:35+00:00, index 12/213, type 0x2, success. From [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) (an EOA; window profile: hot_wallet, very_high_nonce, 5575 sent to 508 destinations, nonce 4,780,333 to 4,785,907) to [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) (a contract of 7,746 bytes; contract_like, never_sends, router_like, called 8931 times in the window). Selector `0x0a2b8f36`, calldata 4,068 bytes, value 0 ETH, 19 logs, tip 0.256163107 gwei. Largest position change $100,025 (IMPL:0xe343…491d at [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef)); gross $600,148; swaps 1 in 1 pools; 6 distinct recipients. Principal [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) nets IMPL:0xe343…491d $100,025, USDC -$100,024 against [0x0889…2c9a](https://etherscan.io/address/0x0889e9327b98d7d1be3c301a4585ff3330502c9a) (a contract of 23,619 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) +0.000000 IMPL:0xe343…491d ($100,025); [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) -100,038.30 USDC (-$100,024); [0x0000…d701](https://etherscan.io/address/0x00000000000014aa86c5d3c41765bb24e11bd701) -0.000000 IMPL:0xe343…491d (-$42,511); [0x0000…d701](https://etherscan.io/address/0x00000000000014aa86c5d3c41765bb24e11bd701) +42,516.28 USDC ($42,510); [0x025a…a62f](https://etherscan.io/address/0x025a13752ec1fb6c0e441e5d7b1678bb5f9ca62f) -0.000000 IMPL:0xe343…491d (-$37,509); [0x025a…a62f](https://etherscan.io/address/0x025a13752ec1fb6c0e441e5d7b1678bb5f9ca62f) +37,514.36 USDC ($37,509); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) -0.000000 IMPL:0xe343…491d (-$20,005); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) +20,007.66 USDC ($20,005).

Event families: ERC20_Transfer_shape ×10, unknown ×6, Approval ×1, V4Swap ×1, anonymous ×1. Unknown topics: [0xb92f…ff4f](https://etherscan.io/address/0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f) 0x93485dcd31a905e3… ×3; [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) 0xafbab204e8271965… ×1; [0x025a…a62f](https://etherscan.io/address/0x025a13752ec1fb6c0e441e5d7b1678bb5f9ca62f) 0x103ed084e94a44c8… ×1; [0xb92f…ff4f](https://etherscan.io/address/0xb92fe925dc43a0ecde6c8b1a2709c170ec4fff4f) 0xafbab204e8271965… ×1.

Interpretation (LLM, confidence high): The same wallet's larger conversions went through the 0x-Settler path with no swap event (0xbd1b8050…); together they are 154 swaps and $55M of USDC into USDG in the day.

### A95. [0x8586…dfa9](https://etherscan.io/tx/0x8586680ede2a89c9d66f79d0508786627675824fa16607c0476638d74bd6dfa9): not yet annotated

Selected for known type audit (aster_style_withdrawal_observed). Cluster audit-aster_style_withdrawal_observed: 35 transactions from 29 senders, $4,502,531, shape AsterWithdrawalObserved. Block 25,906,740 at 2026-09-04T21:47:35+00:00, index 118/365, type 0x2, success. From [0x0665…fb33](https://etherscan.io/address/0x0665eecff6d58534e9fc207541a205d79d3dfb33) (an EOA; window profile: no tags, 8 sent to 4 destinations, nonce 144 to 151) to [0x6540…84dc](https://etherscan.io/address/0x65407b940966954b23dfa3caa5c0702bb42984dc) (a contract of 1,419 bytes; never_sends, called 9 times in the window). Selector `0x0ad58d2f`, calldata 100 bytes, value 0 ETH, 5 logs, tip 0.6 gwei. Largest position change $226,551 (IMPL:0x6874…2f38 at [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9)); gross $226,551; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x0665…fb33](https://etherscan.io/address/0x0665eecff6d58534e9fc207541a205d79d3dfb33) nets IMPL:0x6874…2f38 $226,551 against [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9) (a contract of 1,419 bytes; many_sources, never_sends).

Net flows: [0x0665…fb33](https://etherscan.io/address/0x0665eecff6d58534e9fc207541a205d79d3dfb33) +0.000000 IMPL:0x6874…2f38 ($226,551); [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9) -0.000000 IMPL:0x6874…2f38 (-$226,551).

Event families: unknown ×3, AsterWithdrawalObserved ×1, ERC20_Transfer_shape ×1. Unknown topics: [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9) 0xa1facf110ded5028… ×1; [0xcca8…26c9](https://etherscan.io/address/0xcca852bc40e560adc3b1cc58ca5b55638ce826c9) 0x535be2ff85ab4c5d… ×1; [0x6540…84dc](https://etherscan.io/address/0x65407b940966954b23dfa3caa5c0702bb42984dc) 0x837314749a845903… ×1.

_No qualitative note yet for this transaction._

### A96. [0x18ee…01b4](https://etherscan.io/tx/0x18eed51e23e18cdfab042902a70197fc90a6639ead63c322c45606bdd57401b4): not yet annotated

Selected for known type audit (beacon_deposit). Cluster audit-beacon_deposit: 199 transactions from 167 senders, $73,614,431, shape BeaconDeposit. Block 25,906,833 at 2026-09-04T22:06:11+00:00, index 46/328, type 0x2, success. From [0x2cee…6037](https://etherscan.io/address/0x2ceeda9dc047bc7d9a08b5e829e81204c9fc6037) (an EOA; window profile: fresh, pass_through, 1 sent to 1 destinations, nonce 0 to 0) to [0x0000…05fa](https://etherscan.io/address/0x00000000219ab540356cbb839cbe05303d7705fa) (a contract of 6,358 bytes; contract_like, many_sources, never_sends, called 169 times in the window). Selector `0x22895118`, calldata 404 bytes, value 32 ETH, 1 logs, tip 0.939927523 gwei. Largest position change $78,497 (ETH at [0x2cee…6037](https://etherscan.io/address/0x2ceeda9dc047bc7d9a08b5e829e81204c9fc6037)); gross $78,497; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x2cee…6037](https://etherscan.io/address/0x2ceeda9dc047bc7d9a08b5e829e81204c9fc6037) nets ETH -$78,497 against [0x0000…05fa](https://etherscan.io/address/0x00000000219ab540356cbb839cbe05303d7705fa) (a contract of 6,358 bytes; contract_like, many_sources, never_sends).

Net flows: [0x0000…05fa](https://etherscan.io/address/0x00000000219ab540356cbb839cbe05303d7705fa) +32.000000 ETH ($78,497); [0x2cee…6037](https://etherscan.io/address/0x2ceeda9dc047bc7d9a08b5e829e81204c9fc6037) -32.000000 ETH (-$78,497).

Event families: BeaconDeposit ×1.

_No qualitative note yet for this transaction._

### A97. [0x3df8…70ef](https://etherscan.io/tx/0x3df86a14f3aaa3d8f4cc69722d736e39db5418013efba074792f66deb18e70ef): not yet annotated

Selected for known type audit (nft_trade). Cluster audit-nft_trade: 15 transactions from 14 senders, $1,007,887, shape ERC721_Transfer_shape,SeaportOrderFulfilled. Block 25,907,097 at 2026-09-04T22:58:59+00:00, index 128/201, type 0x2, success. From [0xbdba…9558](https://etherscan.io/address/0xbdba56dac0c99fa9a020045d9ccc774ed2489558) (an EOA; window profile: no tags, 16 sent to 7 destinations, nonce 3,500 to 3,515) to [0x0000…b395](https://etherscan.io/address/0x0000000000000068f116a894984e2db1123eb395) (a contract of 23,981 bytes; contract_like, many_sources, never_sends, called 5856 times in the window). Selector `0x87201b41`, calldata 30,248 bytes, value 0 ETH, 61 logs, tip 0.000290688 gwei. Largest position change $23,027 (WETH at [0xbdba…9558](https://etherscan.io/address/0xbdba56dac0c99fa9a020045d9ccc774ed2489558)); gross $23,492; swaps 0 in 0 pools; 2 distinct recipients. Principal [0xbdba…9558](https://etherscan.io/address/0xbdba56dac0c99fa9a020045d9ccc774ed2489558) nets WETH $23,027 against [0x1be0…e043](https://etherscan.io/address/0x1be0836c271c87f6c2b528f65977e67e4363e043) (an EOA; no tags).

Net flows: [0xbdba…9558](https://etherscan.io/address/0xbdba56dac0c99fa9a020045d9ccc774ed2489558) +9.387180 WETH ($23,027); [0xb5be…45bf](https://etherscan.io/address/0xb5be918f7412ab7358064e0cfca78c03e53645bf) -2.790000 WETH (-$6,844); [0x1be0…e043](https://etherscan.io/address/0x1be0836c271c87f6c2b528f65977e67e4363e043) -0.943000 WETH (-$2,313); [0xb0a7…a0a1](https://etherscan.io/address/0xb0a71e3fb31c23ce349b228288c156c412f7a0a1) -0.942000 WETH (-$2,311); [0x26c9…0e1d](https://etherscan.io/address/0x26c9720097679c6c6910287effe329da2c440e1d) -0.671000 WETH (-$1,646); [0xc510…f289](https://etherscan.io/address/0xc5105ef851ecd29f82858d817f8d3aa77433f289) -0.667000 WETH (-$1,636); [0x5a8e…caa1](https://etherscan.io/address/0x5a8e4ec3c2fe1f3369d0704acbad5cb34d00caa1) -0.664000 WETH (-$1,629); [0x1e7f…3e05](https://etherscan.io/address/0x1e7fbb0bda316496e55664140c3239a843983e05) -0.661000 WETH (-$1,621).

Event families: ERC20_Transfer_shape ×16, Approval ×15, ERC721_Transfer_shape ×15, SeaportOrderFulfilled ×15.

_No qualitative note yet for this transaction._

### A98. [0x3548…b349](https://etherscan.io/tx/0x3548a8f942a6e1bdc56dc6c938fade5e056745945f43655a39c86eefd5edb349): not yet annotated

Selected for known type audit (smart_account_execute_transfer). Cluster audit-smart_account_execute_transfer: 412 transactions from 36 senders, $366,443,636, shape transfers-only. Block 25,907,403 at 2026-09-05T00:00:47+00:00, index 249/305, type 0x2, success. From [0xfa17…d27f](https://etherscan.io/address/0xfa176be60ee2227268030d245c4214599431d27f) (an EOA; window profile: hot_wallet, 990 sent to 640 destinations, nonce 34,411 to 35,400) to [0xc51e…cb08](https://etherscan.io/address/0xc51e9af67c16a7176e244d8803a32aaf1430cb08) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); many_sources, called 113 times in the window). Selector `0xe9ae5c53`, calldata 516 bytes, value 0 ETH, 1 logs, tip 0.006544821 gwei. Largest position change $140,740 (USDT at [0xc51e…cb08](https://etherscan.io/address/0xc51e9af67c16a7176e244d8803a32aaf1430cb08)); gross $140,740; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xc51e…cb08](https://etherscan.io/address/0xc51e9af67c16a7176e244d8803a32aaf1430cb08) nets USDT -$140,740 against [0x783a…b49e](https://etherscan.io/address/0x783a045d2fbe37ce593c0c19e5b32b1504f5b49e) (an EOA delegated (EIP-7702) to [0x0000…b16b](https://etherscan.io/address/0x0000fb7702036ff9f76044a501ac1aa74cbab16b); no tags).

Net flows: [0x783a…b49e](https://etherscan.io/address/0x783a045d2fbe37ce593c0c19e5b32b1504f5b49e) +140,733.81 USDT ($140,740); [0xc51e…cb08](https://etherscan.io/address/0xc51e9af67c16a7176e244d8803a32aaf1430cb08) -140,733.81 USDT (-$140,740).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A99. [0x6e01…7c53](https://etherscan.io/tx/0x6e01389e4952f8bfba78df65dff3ea5164a7aa339769c0633a2ee4db61fb7c53): not yet annotated

Selected for known type audit (bridge_out). Cluster audit-bridge_out: 2,361 transactions from 869 senders, $526,980,424, shape ArbInboxMessageDelivered,ArbMessageDelivered,WETHWithdrawal. Block 25,907,472 at 2026-09-05T00:14:35+00:00, index 306/329, type 0x2, success. From [0x418b…5071](https://etherscan.io/address/0x418b184995be83093aef2c2d5f347b5e0fc35071) (an EOA; window profile: bot_sender, 36 sent to 1 destinations, nonce 251 to 286) to [0xad03…f0c7](https://etherscan.io/address/0xad03abc6223e9def79b3feb624f54303a372f0c7) (a contract of 18,817 bytes; contract_like, never_sends, called 634 times in the window). Selector `0xc4e9f452`, calldata 868 bytes, value 0 ETH, 3 logs, tip 0.000009993 gwei. Largest position change $19,989 (WETH at [0xad03…f0c7](https://etherscan.io/address/0xad03abc6223e9def79b3feb624f54303a372f0c7)); gross $19,989; swaps 0 in 0 pools; 0 distinct recipients. Principal [0xad03…f0c7](https://etherscan.io/address/0xad03abc6223e9def79b3feb624f54303a372f0c7) nets WETH -$19,989.

Net flows: [0xad03…f0c7](https://etherscan.io/address/0xad03abc6223e9def79b3feb624f54303a372f0c7) -8.142863 WETH (-$19,989).

Event families: ArbInboxMessageDelivered ×1, ArbMessageDelivered ×1, WETHWithdrawal ×1.

_No qualitative note yet for this transaction._

### A100. [0xd3e3…11c8](https://etherscan.io/tx/0xd3e3b9bf72424daac2aa18f1e1801efcd7f9516c1e1031f71c72a4c0d32a11c8): not yet annotated

Selected for known type audit (psm_conversion). Cluster audit-psm_conversion: 1,383 transactions from 571 senders, $961,233,749, shape DSNote,GJoin_aau,PSMBuyGem,V4Swap. Block 25,907,476 at 2026-09-05T00:15:23+00:00, index 69/222, type 0x2, success. From [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) (an EOA; window profile: no tags, 36 sent to 6 destinations, nonce 248 to 283) to [0x4c82…2cca](https://etherscan.io/address/0x4c82d1fbfe28c977cbb58d8c7ff8fcf9f70a2cca) (a contract of 24,546 bytes; contract_like, many_sources, never_sends, router_like, called 6514 times in the window). Selector `0x3593564c`, calldata 2,650 bytes, value 0 ETH, 20 logs, tip 0.15 gwei. Largest position change $100,019 (USDC at [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5)); gross $830,150; swaps 3 in 3 pools; 6 distinct recipients. Principal [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) nets USDC $100,019, USDT -$100,004 against [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) (a contract of 24,009 bytes; many_sources, never_sends, pool).

Net flows: [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) +100,033.53 USDC ($100,019); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) +100,000.00 USDT ($100,004); [0x882a…30d5](https://etherscan.io/address/0x882a709563b1cbb711fd285ece751564e56830d5) -100,000.00 USDT (-$100,004); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) -90,030.19 USDS (-$90,030); [0x3730…7341](https://etherscan.io/address/0x37305b1cd40574e4c5ce33f8e8306be057fd7341) -90,030.19 USDC (-$90,018); [0xf6e7…3042](https://etherscan.io/address/0xf6e72db5454dd049d0788e411b06cfaf16853042) +90,030.19 DAI ($90,000); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) -10,003.34 USDC (-$10,002); [0x958a…e888](https://etherscan.io/address/0x958a0904940f744f8c6b72c043ceee3ea34ae888) +0.000000 USDS ($0.00).

Event families: ERC20_Transfer_shape ×11, DSNote ×3, V4Swap ×3, GJoin_aau ×1, PSMBuyGem ×1, unknown ×1. Unknown topics: [0x958a…e888](https://etherscan.io/address/0x958a0904940f744f8c6b72c043ceee3ea34ae888) 0x6150bb53cd76c570… ×1.

_No qualitative note yet for this transaction._

### A101. [0x248d…a14c](https://etherscan.io/tx/0x248d3c15c9d9e53b089a593c57f1184c7b222608b6686d851cad7495d412a14c): audit of trade_against_unpriced_token (now receipt_token_minted_deposit): 244,464.27 USD of WETH deposited into 0xbad1b632…, which emits Deposit(address,uint256,uint256) and mints a receipt token

Selected for known type audit (receipt_token_minted_deposit). Cluster audit-receipt_token_minted_deposit: 157 transactions from 97 senders, $46,763,701, shape GDeposit_auu. Block 25,907,620 at 2026-09-05T00:44:11+00:00, index 208/257, type 0x2, success. From [0xe47c…7c6f](https://etherscan.io/address/0xe47c34cdbba71e9441414eee4afd35904e587c6f) (an EOA; window profile: no tags, 3 sent to 2 destinations, nonce 10 to 12) to [0xbad1…8353](https://etherscan.io/address/0xbad1b632e90ce02af868f07c572adb067eb98353) (a contract of 21,999 bytes; never_sends, called 1 times in the window). Selector `0xb6b55f25`, calldata 36 bytes, value 0 ETH, 5 logs, tip 0.001 gwei. Largest position change $244,464 (WETH at [0xe47c…7c6f](https://etherscan.io/address/0xe47c34cdbba71e9441414eee4afd35904e587c6f)); gross $244,464; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xe47c…7c6f](https://etherscan.io/address/0xe47c34cdbba71e9441414eee4afd35904e587c6f) nets WETH -$244,464 against [0xbad1…8353](https://etherscan.io/address/0xbad1b632e90ce02af868f07c572adb067eb98353) (a contract of 21,999 bytes; never_sends).

Net flows: [0xbad1…8353](https://etherscan.io/address/0xbad1b632e90ce02af868f07c572adb067eb98353) +99.587000 WETH ($244,464); [0xe47c…7c6f](https://etherscan.io/address/0xe47c34cdbba71e9441414eee4afd35904e587c6f) -99.587000 WETH (-$244,464).

Unpriced ERC-20 transfers: [wmtWETH (self-reported)](https://etherscan.io/address/0xbad1b632e90ce02af868f07c572adb067eb98353) ×1 (largest raw 99587000000000000000).

Event families: ERC20_Transfer_shape ×2, unknown ×2, GDeposit_auu ×1. Unknown topics: [0xbad1…8353](https://etherscan.io/address/0xbad1b632e90ce02af868f07c572adb067eb98353) 0x18247a393d0531b6… ×1; [0xbad1…8353](https://etherscan.io/address/0xbad1b632e90ce02af868f07c572adb067eb98353) 0x9385f9ff65bcd2fb… ×1.

Interpretation (LLM, confidence high): This sample is why round 4 separated minted receipts from traded tokens.

### A102. [0x9908…1ae2](https://etherscan.io/tx/0x990821c3073639b1482031f09c7f2f49673b7db503a776a4081dfcc59b811ae2): not yet annotated

Selected for known type audit (operator_transfer_recorded). Cluster audit-operator_transfer_recorded: 290 transactions from 149 senders, $53,807,058, shape transfers-only. Block 25,907,675 at 2026-09-05T00:55:11+00:00, index 13/252, type 0x2, success. From [0xebf6…d433](https://etherscan.io/address/0xebf6d047effda8665bf0006a960790b09ac1d433) (an EOA; window profile: no tags, 3 sent to 2 destinations, nonce 611 to 613) to [0x8888…e3ce](https://etherscan.io/address/0x8888888199b2df864bf678259607d6d5ebb4e3ce) (a contract of 141 bytes; contract_like, never_sends, called 26 times in the window). Selector `0xfaadb53b`, calldata 228 bytes, value 0 ETH, 4 logs, tip 1.013632563 gwei. Largest position change $29,995 (USDC at [0xebf6…d433](https://etherscan.io/address/0xebf6d047effda8665bf0006a960790b09ac1d433)); gross $59,990; swaps 0 in 0 pools; 2 distinct recipients. Principal [0xebf6…d433](https://etherscan.io/address/0xebf6d047effda8665bf0006a960790b09ac1d433) nets USDC -$29,995 against [0x8888…e3ce](https://etherscan.io/address/0x8888888199b2df864bf678259607d6d5ebb4e3ce) (a contract of 141 bytes; contract_like, never_sends).

Net flows: [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) +29,999.00 USDC ($29,995); [0xebf6…d433](https://etherscan.io/address/0xebf6d047effda8665bf0006a960790b09ac1d433) -29,999.00 USDC (-$29,995); [0x8888…e3ce](https://etherscan.io/address/0x8888888199b2df864bf678259607d6d5ebb4e3ce) +0.000000 USDC ($0.00).

Event families: ERC20_Transfer_shape ×2, unknown ×2. Unknown topics: [0x8888…e3ce](https://etherscan.io/address/0x8888888199b2df864bf678259607d6d5ebb4e3ce) 0x2eef4ec627e0f99d… ×1; [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) 0x4174a9435a04d04d… ×1.

_No qualitative note yet for this transaction._

### A103. [0x19cf…66be](https://etherscan.io/tx/0x19cf38e11030761d5b8ba23306063f98fc8709ad1c86fdc8ec95f02ded4666be): not yet annotated

Selected for known type audit (receipt_token_burned_withdrawal). Cluster audit-receipt_token_burned_withdrawal: 90 transactions from 47 senders, $27,573,047, shape DSNote,Withdrawn. Block 25,907,680 at 2026-09-05T00:56:11+00:00, index 72/249, type 0x2, success. From [0x109f…5774](https://etherscan.io/address/0x109f30842cdd088349f560b8053e124b79685774) (an EOA; window profile: no tags, 6 sent to 3 destinations, nonce 806 to 811) to [0xce01…a6a3](https://etherscan.io/address/0xce01c90de7fd1bcfa39e237fe6d8d9f569e8a6a3) (a contract of 15,134 bytes; contract_like, never_sends, called 40 times in the window). Selector `0xbf0700fe`, calldata 132 bytes, value 0 ETH, 11 logs, tip 0.15 gwei. Largest position change $47,125 (IMPL:0x5607…9279 at [0x929d…a6f9](https://etherscan.io/address/0x929d9a1435662357f54adcf64dcee4d6b867a6f9)); gross $141,375; swaps 0 in 0 pools; 3 distinct recipients. Principal [0x109f…5774](https://etherscan.io/address/0x109f30842cdd088349f560b8053e124b79685774) nets IMPL:0x5607…9279 $47,125 against [0x929d…a6f9](https://etherscan.io/address/0x929d9a1435662357f54adcf64dcee4d6b867a6f9) (a contract of 4,218 bytes; no tags).

Net flows: [0x109f…5774](https://etherscan.io/address/0x109f30842cdd088349f560b8053e124b79685774) +700,000.00 IMPL:0x5607…9279 ($47,125); [0x929d…a6f9](https://etherscan.io/address/0x929d9a1435662357f54adcf64dcee4d6b867a6f9) -700,000.00 IMPL:0x5607…9279 (-$47,125); [0x0f23…cc86](https://etherscan.io/address/0x0f23de72e1581857eacd6308aebb69cf3a49cc86) +0.000000 IMPL:0x5607…9279 ($0.00); [0xce01…a6a3](https://etherscan.io/address/0xce01c90de7fd1bcfa39e237fe6d8d9f569e8a6a3) +0.000000 IMPL:0x5607…9279 ($0.00).

Unpriced ERC-20 transfers: [lsSKY (self-reported)](https://etherscan.io/address/0xf9a9cfd3229e985b91f99bc866d42938044ffa1c) ×2 (largest raw 700000000000000000000000).

Event families: ERC20_Transfer_shape ×5, unknown ×3, DSNote ×2, Withdrawn ×1. Unknown topics: [0x929d…a6f9](https://etherscan.io/address/0x929d9a1435662357f54adcf64dcee4d6b867a6f9) 0xce6c5af8fd109993… ×1; [0x0f23…cc86](https://etherscan.io/address/0x0f23de72e1581857eacd6308aebb69cf3a49cc86) 0xce6c5af8fd109993… ×1; [0xce01…a6a3](https://etherscan.io/address/0xce01c90de7fd1bcfa39e237fe6d8d9f569e8a6a3) 0xde1819362eecc26f… ×1.

_No qualitative note yet for this transaction._

### A104. [0x66d3…a16f](https://etherscan.io/tx/0x66d34a62b9078df714e37d916ae5d09e240e1012dd3f1b83d6da3f70ee88a16f): not yet annotated

Selected for known type audit (service_deposit_with_memo). Cluster audit-service_deposit_with_memo: 234 transactions from 138 senders, $10,639,315, shape transfers-only. Block 25,907,831 at 2026-09-05T01:26:35+00:00, index 124/180, type 0x2, success. From [0xecd1…f3c3](https://etherscan.io/address/0xecd1c1bf58ed8913aa11c550fa4d5e8bdf87f3c3) (an EOA; window profile: fresh, 4 sent to 3 destinations, nonce 0 to 3) to [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends, called 3200 times in the window). Selector `0x9ddf93bb`, calldata 356 bytes, value 0 ETH, 2 logs, tip 1 gwei. Largest position change $10,256 (USDC at [0xecd1…f3c3](https://etherscan.io/address/0xecd1c1bf58ed8913aa11c550fa4d5e8bdf87f3c3)); gross $10,256; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xecd1…f3c3](https://etherscan.io/address/0xecd1c1bf58ed8913aa11c550fa4d5e8bdf87f3c3) nets USDC -$10,256 against [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) (a contract of 4,635 bytes; contract_like, many_sources, never_sends).

Net flows: [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) +10,257.18 USDC ($10,256); [0xecd1…f3c3](https://etherscan.io/address/0xecd1c1bf58ed8913aa11c550fa4d5e8bdf87f3c3) -10,257.18 USDC (-$10,256).

Event families: ERC20_Transfer_shape ×1, unknown ×1. Unknown topics: [0xc1d1…a1b5](https://etherscan.io/address/0xc1d13492285eb664951e201bf7c80c7c6318a1b5) 0x45f377f845e1cc76… ×1.

_No qualitative note yet for this transaction._

### A105. [0x947f…0979](https://etherscan.io/tx/0x947fbbda4554c60255f21d6f93c35befce0a6405fffa6728796a47fd83c30979): not yet annotated

Selected for known type audit (delegated_account_self_call). Cluster audit-delegated_account_self_call: 33 transactions from 11 senders, $605,189, shape transfers-only. Block 25,907,839 at 2026-09-05T01:28:11+00:00, index 94/224, type 0x2, success. From [0x63d5…11cc](https://etherscan.io/address/0x63d55efde46799dc91cfa16c4be443ada07e11cc) (an EOA delegated (EIP-7702) to [0x1c68…2158](https://etherscan.io/address/0x1c6841ea2df98fe8423bc4808e72e16461012158); window profile: bot_sender, 385 sent to 1 destinations, nonce 18,302 to 18,686) to [0x63d5…11cc](https://etherscan.io/address/0x63d55efde46799dc91cfa16c4be443ada07e11cc) (an EOA delegated (EIP-7702) to [0x1c68…2158](https://etherscan.io/address/0x1c6841ea2df98fe8423bc4808e72e16461012158); bot_sender, called 388 times in the window). Selector `0xdc248ef3`, calldata 1,124 bytes, value 0 ETH, 5 logs, tip 0.02 gwei. Largest position change $12,946 (USDT at [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27)); gross $30,925; swaps 0 in 0 pools; 3 distinct recipients. Principal [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) nets nothing priced against [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) (an EOA delegated (EIP-7702) to [0x3525…d1ff](https://etherscan.io/address/0x3525f1c4ba12279747fb7f06a2291d406508d1ff); contract_like, never_sends, router_like).

Net flows: [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) +12,945.57 USDT ($12,946); [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) -10,068.64 USDC (-$10,067); [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) +10,068.64 USDC ($10,067); [0x9303…6e7d](https://etherscan.io/address/0x9303d901bbe63310ae5adbb2f3b6d78f82776e7d) +3.223317 WETH ($7,911); [0x9303…6e7d](https://etherscan.io/address/0x9303d901bbe63310ae5adbb2f3b6d78f82776e7d) -7,906.44 USDT (-$7,907); [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) -5,039.13 USDT (-$5,039); [0xe6f8…728b](https://etherscan.io/address/0xe6f87b8eae04944d5209d0ba290e7067050b728b) -2.048985 WETH (-$5,029); [0xe319…7b27](https://etherscan.io/address/0xe3195053f15aae88bb69c7ece0f4922e3e5a7b27) -1.174332 WETH (-$2,882).

Event families: ERC20_Transfer_shape ×5.

_No qualitative note yet for this transaction._

### A106. [0x482c…8b17](https://etherscan.io/tx/0x482cd9f853b123f6652a7e1e4f5b140b2ff2107fecaa4ff8324c678a0ad68b17): audit of stablecoin_burn: 349,948.76 USDC burned through 0x77777777dcc4…, which also takes a 2.00 USDC fee; a cross-chain departure that burns rather than locks

Selected for known type audit (stablecoin_burn). Cluster audit-stablecoin_burn: 204 transactions from 22 senders, $790,827,207, shape USDCBurn. Block 25,908,153 at 2026-09-05T02:30:59+00:00, index 34/205, type 0x2, success. From [0x5cf6…c22b](https://etherscan.io/address/0x5cf6f78fe084cca5e3938f184729532509f1c22b) (an EOA; window profile: bot_sender, 74 sent to 1 destinations, nonce 26,800 to 26,873) to [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) (a contract of 163 bytes; contract_like, never_sends, called 106 times in the window). Selector `0x8ec3dbb9`, calldata 1,348 bytes, value 0 ETH, 4 logs, tip 1.5 gwei. Largest position change $349,951 (USDC at [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee)); gross $349,951; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) nets USDC -$349,951 against [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) (unknown code status; no tags).

Net flows: [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) -350,000.00 USDC (-$349,951); [0xfbaf…b95c](https://etherscan.io/address/0xfbaf3a19b1c02b8bef52a7e9fa855c86c69ab95c) +2.000000 USDC ($2.00).

Event families: ERC20_Transfer_shape ×2, USDCBurn ×1, unknown ×1. Unknown topics: [0x7777…00ee](https://etherscan.io/address/0x77777777dcc4d5a8b6e418fd04d8997ef11000ee) 0x12ee2719e7e2dec9… ×1.

Interpretation (LLM, confidence medium): The type is right about supply mechanics (USDC left circulation on Ethereum) and silent about where it reappears.

Unverified: the burner; the CCTP DepositForBurn family did not match, so either the signature differs from the registered one or the burner is another minter-authorised bridge.

### A107. [0xe711…2def](https://etherscan.io/tx/0xe711719f943f95385aff5768b8712c9336eeeb6856cd29a28a8d6fa1e1b52def): not yet annotated

Selected for known type audit (exchange_deposit). Cluster audit-exchange_deposit: 9,792 transactions from 5,387 senders, $3,841,865,960, shape transfers-only. Block 25,908,263 at 2026-09-05T02:52:59+00:00, index 211/275, type 0x2, success. From [0xe678…91d9](https://etherscan.io/address/0xe67821b76985007b4cf744b0f045c8933b3e91d9) (an EOA; window profile: no tags, 18 sent to 11 destinations, nonce 18,628 to 18,645) to [0xa0b8…eb48](https://etherscan.io/address/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48) (a contract of 2,186 bytes; contract_like, never_sends, called 165686 times in the window). Selector `0xa9059cbb`, calldata 68 bytes, value 0 ETH, 1 logs, tip 0.2 gwei. Largest position change $499,930 (USDC at [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055)); gross $499,930; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xe678…91d9](https://etherscan.io/address/0xe67821b76985007b4cf744b0f045c8933b3e91d9) nets USDC -$499,930 against [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) (a contract of 209 bytes; contract_like, many_sources, never_sends).

Net flows: [0xe678…91d9](https://etherscan.io/address/0xe67821b76985007b4cf744b0f045c8933b3e91d9) -500,000.00 USDC (-$499,930); [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) +500,000.00 USDC ($499,930).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A108. [0x556a…a964](https://etherscan.io/tx/0x556a96744666979aa137a38f2847d01001dede6f8cee8fa10740f2780e03a964): not yet annotated

Selected for known type audit (sandwich_victim). Cluster audit-sandwich_victim: 42 transactions from 29 senders, $4,798,890, shape AggregatorSwapped,CurveTokenExchange,ERC4626Withdraw,FluidSwap,GExchange_aua,V3Swap,V4Swap. Block 25,908,402 at 2026-09-05T03:20:47+00:00, index 4/30, type 0x2, success. From [0x5e20…3131](https://etherscan.io/address/0x5e204cf45560a495988b5bccfd7347682c473131) (an EOA; window profile: no tags, 49 sent to 7 destinations, nonce 231 to 279) to [0x6131…37b5](https://etherscan.io/address/0x6131b5fae19ea4f9d964eac0408e4408b66337b5) (a contract of 18,652 bytes; contract_like, many_sources, never_sends, router_like, called 1823 times in the window). Selector `0xe21fd0e9`, calldata 28,356 bytes, value 0 ETH, 140 logs, tip 0.001314167 gwei. Largest position change $124,663 (sUSDe at [0x5e20…3131](https://etherscan.io/address/0x5e204cf45560a495988b5bccfd7347682c473131)); gross $887,607; swaps 25 in 15 pools; 16 distinct recipients. Principal [0x5e20…3131](https://etherscan.io/address/0x5e204cf45560a495988b5bccfd7347682c473131) nets USDe $124,504, sUSDe -$124,663 against [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) (a contract of 13,529 bytes; many_sources, never_sends). Sandwich marks: [{"back": "0x75fab4186469d5f8a8a61e743ff8622bcd3660653b4c8555a62a3baf75a6e1f7", "front": "0xc73613b125a22339c2931d4296f2f2708179894e1718aa0fd7cfdfa1fe324568", "pool": "0x000000000004444c5dc75cb358380d2e3de08a90:0x56fc29b86900aa0afa6e20b020429bffba1105cfb45070492c67529b46eb48c1", "role": "victim"}, {.

Net flows: [0x5e20…3131](https://etherscan.io/address/0x5e204cf45560a495988b5bccfd7347682c473131) -100,000.00 sUSDe (-$124,663); [0x5e20…3131](https://etherscan.io/address/0x5e204cf45560a495988b5bccfd7347682c473131) +124,504.50 USDe ($124,504); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) +52,030.31 sUSDe ($64,863); [0x9ed0…6d20](https://etherscan.io/address/0x9ed0780e697d7bb92360a45951f3481dd06d6d20) -64,814.22 USDe (-$64,814); [0x9ed0…6d20](https://etherscan.io/address/0x9ed0780e697d7bb92360a45951f3481dd06d6d20) +64,819.83 USDC ($64,811); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) -61,138.34 USDT (-$61,141); [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) -42,474.41 USDC (-$42,468); [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) +42,462.94 USDT ($42,465).

Event families: ERC20_Transfer_shape ×62, unknown ×49, CurveTokenExchange ×10, V4Swap ×10, FluidSwap ×3, ERC4626Withdraw ×2, V3Swap ×2, AggregatorSwapped ×1, GExchange_aua ×1. Unknown topics: [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) 0xa6fee24309b1d83d… ×30; [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) 0x4d93b232a24e82b2… ×6; [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996) 0xc035da294269ae5a… ×5; [0x9484…4396](https://etherscan.io/address/0x948462ce2b2eae59c65d9f2f94b3d8de4fbd4396) 0xcd8b75a7fb6cb82a… ×1; [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) 0x1b3d7edb2e9c0b0e… ×1; [0x4440…c0c4](https://etherscan.io/address/0x4440854b2d02c57a0dc5c58b7a884562d875c0c4) 0x105f30fcab1c07f2… ×1.

_No qualitative note yet for this transaction._

### A109. [0xfd2d…72a1](https://etherscan.io/tx/0xfd2db4bd4880f53d3af641c770189b5a248b6d5f66dd76aba3bfa154cc7172a1): not yet annotated

Selected for known type audit (bridge_in). Cluster audit-bridge_in: 963 transactions from 156 senders, $397,581,357, shape CCTPv2MintAndWithdraw,USDCMint. Block 25,908,542 at 2026-09-05T03:48:47+00:00, index 188/265, type 0x2, success. From [0x7087…1ef8](https://etherscan.io/address/0x708704d33ace3dafbed28f150a56ce9d124b1ef8) (an EOA; window profile: bot_sender, 280 sent to 2 destinations, nonce 20,622 to 20,901) to [0x214c…adf3](https://etherscan.io/address/0x214c19fbcdfb683f2c726b4bbaf24ab483bfadf3) (a contract of 11,555 bytes; contract_like, never_sends, called 220 times in the window). Selector `0x1b1062b8`, calldata 2,052 bytes, value 0 ETH, 12 logs, tip 0.00001 gwei. Largest position change $24,937 (USDC at [0x3b4d…5ca7](https://etherscan.io/address/0x3b4d794a66304f130a4db8f2551b0070dfcf5ca7)); gross $74,811; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x3b4d…5ca7](https://etherscan.io/address/0x3b4d794a66304f130a4db8f2551b0070dfcf5ca7) nets nothing priced against [0xdd52…259e](https://etherscan.io/address/0xdd52f8134f85f3979fba24387ce0cec05937259e) (a contract of 4,398 bytes; never_sends).

Net flows: [0x3b4d…5ca7](https://etherscan.io/address/0x3b4d794a66304f130a4db8f2551b0070dfcf5ca7) +24,940.51 USDC ($24,937); [0x109d…60c9](https://etherscan.io/address/0x109db572e719fa363dc53fbaf3617422159060c9) -3.491671 USDC (-$3.49); [0x6efa…7bee](https://etherscan.io/address/0x6efa3205a385420cf1cfd6b725b48f96117a7bee) +3.491670 USDC ($3.49); [0x214c…adf3](https://etherscan.io/address/0x214c19fbcdfb683f2c726b4bbaf24ab483bfadf3) +0.000000 USDC ($0.00); [0xdd52…259e](https://etherscan.io/address/0xdd52f8134f85f3979fba24387ce0cec05937259e) +0.000000 USDC ($0.00).

Event families: ERC20_Transfer_shape ×5, unknown ×4, USDCMint ×2, CCTPv2MintAndWithdraw ×1. Unknown topics: [0x81d4…4b64](https://etherscan.io/address/0x81d40f21f12a8f0e3252bccb954d722d4c464b64) 0xff48c13eda96b1cc… ×1; [0x3b4d…5ca7](https://etherscan.io/address/0x3b4d794a66304f130a4db8f2551b0070dfcf5ca7) 0xefdd379e3e15772f… ×1; [0x3b4d…5ca7](https://etherscan.io/address/0x3b4d794a66304f130a4db8f2551b0070dfcf5ca7) 0x493c3b8240368e83… ×1; [0x214c…adf3](https://etherscan.io/address/0x214c19fbcdfb683f2c726b4bbaf24ab483bfadf3) 0xb88fc27be67e678f… ×1.

_No qualitative note yet for this transaction._

### A110. [0x0466…7cff](https://etherscan.io/tx/0x0466ac217fab3dd3b3ff2d33f26809a5bd930a641861401d91661738bf2d7cff): not yet annotated

Selected for known type audit (compound_v3_op). Cluster audit-compound_v3_op: 61 transactions from 37 senders, $11,706,915, shape CompoundV3Supply. Block 25,908,568 at 2026-09-05T03:53:59+00:00, index 216/253, type 0x0, success. From [0xd23f…8661](https://etherscan.io/address/0xd23f1ee2e67e4eb8b39624697bf1a530f0d78661) (an EOA; window profile: no tags, 4 sent to 3 destinations, nonce 7 to 10) to [0xc3d6…cdc3](https://etherscan.io/address/0xc3d688b66703497daa19211eedff47f25384cdc3) (a contract of 1,878 bytes; contract_like, never_sends, called 53 times in the window). Selector `0xf2b9fdb8`, calldata 68 bytes, value 0 ETH, 3 logs, tip 0.001196702 gwei. Largest position change $208,218 (USDC at [0xd23f…8661](https://etherscan.io/address/0xd23f1ee2e67e4eb8b39624697bf1a530f0d78661)); gross $208,218; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xd23f…8661](https://etherscan.io/address/0xd23f1ee2e67e4eb8b39624697bf1a530f0d78661) nets USDC -$208,218 against [0xc3d6…cdc3](https://etherscan.io/address/0xc3d688b66703497daa19211eedff47f25384cdc3) (a contract of 1,878 bytes; contract_like, never_sends).

Net flows: [0xc3d6…cdc3](https://etherscan.io/address/0xc3d688b66703497daa19211eedff47f25384cdc3) +208,247.03 USDC ($208,218); [0xd23f…8661](https://etherscan.io/address/0xd23f1ee2e67e4eb8b39624697bf1a530f0d78661) -208,247.03 USDC (-$208,218).

Unpriced ERC-20 transfers: [cUSDCv3 (self-reported)](https://etherscan.io/address/0xc3d688b66703497daa19211eedff47f25384cdc3) ×1 (largest raw 208247031316).

Event families: ERC20_Transfer_shape ×2, CompoundV3Supply ×1.

_No qualitative note yet for this transaction._

### A111. [0x9de6…6e86](https://etherscan.io/tx/0x9de6f7152f1ee18493a2dbabc21dfbdc256655d079da1256b6b897b3d4f16e86): not yet annotated

Selected for known type audit (contract_deposit_no_event). Cluster audit-contract_deposit_no_event: 19 transactions from 5 senders, $7,158,104, shape WETHWithdrawal. Block 25,908,755 at 2026-09-05T04:31:35+00:00, index 288/319, type 0x2, success. From [0xe873…d710](https://etherscan.io/address/0xe8736af1926e9d8f5a6602fbbb0893b26436d710) (an EOA; window profile: no tags, 140 sent to 13 destinations, nonce 24,363 to 24,502) to [0xc4e9…20aa](https://etherscan.io/address/0xc4e9f84297d2e6e92d0d81ee5f1257652ec320aa) (a contract of 2,787 bytes; never_sends, called 5 times in the window). Selector `0xa158657c`, calldata 68 bytes, value 0 ETH, 2 logs, tip 0 gwei. Largest position change $713,152 (WETH at [0xe873…d710](https://etherscan.io/address/0xe8736af1926e9d8f5a6602fbbb0893b26436d710)); gross $1,426,303; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xe873…d710](https://etherscan.io/address/0xe8736af1926e9d8f5a6602fbbb0893b26436d710) nets WETH -$713,152 against [0xc4e9…20aa](https://etherscan.io/address/0xc4e9f84297d2e6e92d0d81ee5f1257652ec320aa) (a contract of 2,787 bytes; never_sends).

Net flows: [0xe873…d710](https://etherscan.io/address/0xe8736af1926e9d8f5a6602fbbb0893b26436d710) -290.814663 WETH (-$713,152); [0xc4e9…20aa](https://etherscan.io/address/0xc4e9f84297d2e6e92d0d81ee5f1257652ec320aa) +0.000000 WETH ($0.00).

Event families: ERC20_Transfer_shape ×1, WETHWithdrawal ×1.

_No qualitative note yet for this transaction._

### A112. [0x15de…134c](https://etherscan.io/tx/0x15de0a23446ccfb58259ddcfa454a92cd6b70b43f03d774a0c820f2e9fa8134c): not yet annotated

Selected for known type audit (native_deposit_wrapped_forwarded). Cluster audit-native_deposit_wrapped_forwarded: 67 transactions from 42 senders, $8,502,253, shape WETHDeposit. Block 25,908,851 at 2026-09-05T04:50:47+00:00, index 41/44, type 0x2, success. From [0xb1ef…11eb](https://etherscan.io/address/0xb1ef30da6a5bded575a1f2b1022c1c9116dd11eb) (an EOA; window profile: fresh, 1 sent to 1 destinations, nonce 0 to 0) to [0xac9f…d405](https://etherscan.io/address/0xac9f360ae85469b27aeddeafc579ef2d052ad405) (a contract of 9,617 bytes; contract_like, never_sends, called 173 times in the window). Selector `0xe4899c13`, calldata 868 bytes, value 13.539917028842304 ETH, 7 logs, tip 0.003992531 gwei. Largest position change $33,203 (ETH at [0xb1ef…11eb](https://etherscan.io/address/0xb1ef30da6a5bded575a1f2b1022c1c9116dd11eb)); gross $99,610; swaps 0 in 0 pools; 3 distinct recipients. Principal [0xb1ef…11eb](https://etherscan.io/address/0xb1ef30da6a5bded575a1f2b1022c1c9116dd11eb) nets ETH -$33,203 against [0xac9f…d405](https://etherscan.io/address/0xac9f360ae85469b27aeddeafc579ef2d052ad405) (a contract of 9,617 bytes; contract_like, never_sends).

Net flows: [0xac9f…d405](https://etherscan.io/address/0xac9f360ae85469b27aeddeafc579ef2d052ad405) +13.539917 ETH ($33,203); [0xb1ef…11eb](https://etherscan.io/address/0xb1ef30da6a5bded575a1f2b1022c1c9116dd11eb) -13.539917 ETH (-$33,203); [0xfa70…a4b9](https://etherscan.io/address/0xfa7093cdd9ee6932b4eb2c9e1cde7ce00b1fa4b9) +13.506067 WETH ($33,120); [0xe8a8…ff40](https://etherscan.io/address/0xe8a8b458bcd1ececc6b6b58f80929b29ccecff40) +0.033850 WETH ($83.01); [0xac9f…d405](https://etherscan.io/address/0xac9f360ae85469b27aeddeafc579ef2d052ad405) +0.000000 WETH ($0.00).

Event families: Approval ×2, ERC20_Transfer_shape ×2, unknown ×2, WETHDeposit ×1. Unknown topics: [0xfa70…a4b9](https://etherscan.io/address/0xfa7093cdd9ee6932b4eb2c9e1cde7ce00b1fa4b9) 0x29696e3cb1956aca… ×1; [0xfa70…a4b9](https://etherscan.io/address/0xfa7093cdd9ee6932b4eb2c9e1cde7ce00b1fa4b9) 0x3a5b9dc26075a380… ×1.

_No qualitative note yet for this transaction._

### A113. [0x882b…2832](https://etherscan.io/tx/0x882b046d5d8b8e5a5164e03adfe61404771dd8ce44055290c313552ef3232832): not yet annotated

Selected for known type audit (erc4337_bundle). Cluster audit-erc4337_bundle: 710 transactions from 42 senders, $300,341,199, shape EntryPointBeforeExecution,UserOperation. Block 25,908,938 at 2026-09-05T05:08:11+00:00, index 80/164, type 0x2, success. From [0x4337…f038](https://etherscan.io/address/0x4337012eaf1f862b8dbdc6b62a01782ae01ef038) (an EOA; window profile: bot_sender, very_high_nonce, 1064 sent to 3 destinations, nonce 87,141 to 88,204) to [0x0000…a032](https://etherscan.io/address/0x0000000071727de22e5e9d8baf0edac6f37da032) (a contract of 16,035 bytes; contract_like, never_sends, router_like, called 16413 times in the window). Selector `0x765e827f`, calldata 1,764 bytes, value 0 ETH, 7 logs, tip 0.055379806 gwei. Largest position change $11,001 (USDT at [0x068a…1ca0](https://etherscan.io/address/0x068a4e6642e78c00ca290731d370233ab01f1ca0)); gross $11,001; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x068a…1ca0](https://etherscan.io/address/0x068a4e6642e78c00ca290731d370233ab01f1ca0) nets nothing priced against [0xdf17…bd34](https://etherscan.io/address/0xdf17613203f9f82830b5253df005d95a3d64bd34) (an EOA; no tags).

Net flows: [0x068a…1ca0](https://etherscan.io/address/0x068a4e6642e78c00ca290731d370233ab01f1ca0) -11,000.06 USDT (-$11,001); [0xdf17…bd34](https://etherscan.io/address/0xdf17613203f9f82830b5253df005d95a3d64bd34) +11,000.00 USDT ($11,000); [0x4b74…d72a](https://etherscan.io/address/0x4b742ad5ca91969e82aefb80072ae59121a3d72a) +0.060917 USDT ($0.06).

Event families: Approval ×2, ERC20_Transfer_shape ×2, EntryPointBeforeExecution ×1, UserOperation ×1, unknown ×1. Unknown topics: [0x7777…834c](https://etherscan.io/address/0x777777777777aec03fd955926dbf81597e66834c) 0x7a270f29ae17e8e2… ×1.

_No qualitative note yet for this transaction._

### A114. [0x28c2…87c4](https://etherscan.io/tx/0x28c25660cab98bee029a2d1356d50b09a876021aba59ad1ae4d594e3139287c4): not yet annotated

Selected for known type audit (payment_router_fee_split). Cluster audit-payment_router_fee_split: 80 transactions from 29 senders, $10,647,089, shape transfers-only. Block 25,908,984 at 2026-09-05T05:17:23+00:00, index 58/188, type 0x2, success. From [0x78a5…5179](https://etherscan.io/address/0x78a57679a434a2caa3046335195130af6c5a5179) (an EOA; window profile: no tags, 10 sent to 2 destinations, nonce 1,123 to 1,132) to [0x6818…6b46](https://etherscan.io/address/0x6818809eefce719e480a7526d76bd3e561526b46) (a contract of 122 bytes; contract_like, never_sends, called 88 times in the window). Selector `0x8a44121e`, calldata 772 bytes, value 0 ETH, 6 logs, tip 0.1 gwei. Largest position change $11,474 (USDC at [0xb419…ce86](https://etherscan.io/address/0xb419c2867ab3cbc78921660cb95150d95a94ce86)); gross $22,949; swaps 0 in 0 pools; 3 distinct recipients. Principal [0xb419…ce86](https://etherscan.io/address/0xb419c2867ab3cbc78921660cb95150d95a94ce86) nets nothing priced against [0x6818…6b46](https://etherscan.io/address/0x6818809eefce719e480a7526d76bd3e561526b46) (a contract of 122 bytes; contract_like, never_sends).

Net flows: [0xb419…ce86](https://etherscan.io/address/0xb419c2867ab3cbc78921660cb95150d95a94ce86) -11,476.00 USDC (-$11,474); [0x0c36…6df8](https://etherscan.io/address/0x0c363eea8a195c69a3d2c0f6b512c0fc5bbb6df8) +11,464.52 USDC ($11,463); [0x1454…f9b5](https://etherscan.io/address/0x145444c66a32a0464059d400dc488ccf4704f9b5) +11.476000 USDC ($11.47); [0x6818…6b46](https://etherscan.io/address/0x6818809eefce719e480a7526d76bd3e561526b46) +0.000000 USDC ($0.00).

Event families: ERC20_Transfer_shape ×3, unknown ×3. Unknown topics: [0xb419…ce86](https://etherscan.io/address/0xb419c2867ab3cbc78921660cb95150d95a94ce86) 0xcb249c8292372bd1… ×1; [0xb419…ce86](https://etherscan.io/address/0xb419c2867ab3cbc78921660cb95150d95a94ce86) 0x75e161b3e824b114… ×1; [0x6818…6b46](https://etherscan.io/address/0x6818809eefce719e480a7526d76bd3e561526b46) 0xe9b67844a7bb6e6a… ×1.

_No qualitative note yet for this transaction._

### A115. [0xb636…83b3](https://etherscan.io/tx/0xb63667848976e1f03f2ab4204100ffdefd30599d4929eda8f21beafcc8c283b3): not yet annotated

Selected for known type audit (eip7702_delegated). Cluster audit-eip7702_delegated: 243 transactions from 72 senders, $32,630,041, shape transfers-only. Block 25,909,025 at 2026-09-05T05:25:35+00:00, index 158/171, type 0x4, success. From [0xfc04…0457](https://etherscan.io/address/0xfc04fb6b93e0550f1607d5927d7a4ccac36c0457) (an EOA; window profile: bot_sender, 88 sent to 1 destinations, nonce 24,805 to 24,892) to [0x2228…6f74](https://etherscan.io/address/0x2228e5704b637131a3798a186caf18366c146f74) (an EOA delegated (EIP-7702) to [0x7785…0b2f](https://etherscan.io/address/0x7785a22facd31db653ba4928f1d5b81d093f0b2f); contract_like, never_sends, called 88 times in the window). Selector `0x74fa4121`, calldata 292 bytes, value 0 ETH, 1 logs, tip 0.00015 gwei, 1 authorizations. Largest position change $39,995 (USDT at [0xb3d8…c838](https://etherscan.io/address/0xb3d80c2e71a2af26f163f06317c14e854710c838)); gross $39,995; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x2228…6f74](https://etherscan.io/address/0x2228e5704b637131a3798a186caf18366c146f74) nets USDT -$39,995 against [0xb3d8…c838](https://etherscan.io/address/0xb3d80c2e71a2af26f163f06317c14e854710c838) (an EOA; no tags).

Net flows: [0x2228…6f74](https://etherscan.io/address/0x2228e5704b637131a3798a186caf18366c146f74) -39,993.10 USDT (-$39,995); [0xb3d8…c838](https://etherscan.io/address/0xb3d80c2e71a2af26f163f06317c14e854710c838) +39,993.10 USDT ($39,995).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A116. [0x2f8c…5e3a](https://etherscan.io/tx/0x2f8ca8b1cd5bdc3943227608961aa1a1e29794f3eefb481519da41a1ff135e3a): not yet annotated

Selected for known type audit (liquidity_v4). Cluster audit-liquidity_v4: 226 transactions from 82 senders, $58,628,449, shape V4ModifyLiquidity. Block 25,909,056 at 2026-09-05T05:31:47+00:00, index 89/236, type 0x2, success. From [0x7774…1288](https://etherscan.io/address/0x7774a7d0f27d8c48c0a6c7bdd853a0d6a5b71288) (an EOA; window profile: no tags, 18 sent to 4 destinations, nonce 259 to 276) to [0xbd21…ee9e](https://etherscan.io/address/0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e) (a contract of 23,877 bytes; contract_like, many_sources, never_sends, router_like, called 2694 times in the window). Selector `0xdd46508f`, calldata 708 bytes, value 0 ETH, 3 logs, tip 0.002 gwei. Largest position change $75,224 (USDC at [0x7774…1288](https://etherscan.io/address/0x7774a7d0f27d8c48c0a6c7bdd853a0d6a5b71288)); gross $150,170; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x7774…1288](https://etherscan.io/address/0x7774a7d0f27d8c48c0a6c7bdd853a0d6a5b71288) nets IMPL:0xe343…491d -$74,946, USDC -$75,224 against [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) (a contract of 24,009 bytes; many_sources, never_sends, pool).

Net flows: [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) +75,234.27 USDC ($75,224); [0x7774…1288](https://etherscan.io/address/0x7774a7d0f27d8c48c0a6c7bdd853a0d6a5b71288) -75,234.27 USDC (-$75,224); [0x0000…8a90](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90) +0.000000 IMPL:0xe343…491d ($74,946); [0x7774…1288](https://etherscan.io/address/0x7774a7d0f27d8c48c0a6c7bdd853a0d6a5b71288) -0.000000 IMPL:0xe343…491d (-$74,946).

Event families: ERC20_Transfer_shape ×2, V4ModifyLiquidity ×1.

_No qualitative note yet for this transaction._

### A117. [0xf4db…cda4](https://etherscan.io/tx/0xf4dbb8a131bfe867acf8cb35138a854d76914006ca4b8a99130d6d9d7cc0cda4): not yet annotated

Selected for known type audit (staking_pool_withdraw). Cluster audit-staking_pool_withdraw: 11 transactions from 5 senders, $12,275,080, shape Withdrawn. Block 25,909,113 at 2026-09-05T05:43:11+00:00, index 235/285, type 0x2, success. From [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) (an EOA; window profile: no tags, 104 sent to 13 destinations, nonce 1,434 to 1,537) to [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) (a contract of 5,705 bytes; contract_like, never_sends, called 44 times in the window). Selector `0x2e1a7d4d`, calldata 36 bytes, value 0 ETH, 2 logs, tip 0.000137264 gwei. Largest position change $1,000,000 (USDS at [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69)); gross $1,000,000; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) nets USDS $1,000,000 against [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) (a contract of 5,705 bytes; contract_like, never_sends).

Net flows: [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) -1,000,000.00 USDS (-$1,000,000); [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) +1,000,000.00 USDS ($1,000,000).

Event families: ERC20_Transfer_shape ×1, Withdrawn ×1.

_No qualitative note yet for this transaction._

### A118. [0x7cbf…e66b](https://etherscan.io/tx/0x7cbfc4351f61778ea63c4080c818e1163512b667b3827e917a03be2db6c8e66b): not yet annotated

Selected for known type audit (native_call_into_contract_silent). Cluster audit-native_call_into_contract_silent: 54 transactions from 6 senders, $1,053,852, shape value-only. Block 25,909,192 at 2026-09-05T05:59:11+00:00, index 238/255, type 0x2, success. From [0xb233…c460](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460) (an EOA; window profile: hot_wallet, very_high_nonce, 7368 sent to 3841 destinations, nonce 4,022,879 to 4,030,246) to [0x09c3…d818](https://etherscan.io/address/0x09c30cdcdd971423cb3ba757a47d56c35d06d818) (a contract of 109 bytes; contract_like, never_sends, called 1511 times in the window). Selector `0x318adb8b`, calldata 452 bytes, value 6.12590093 ETH, 0 logs, tip 0.000159827 gwei. Largest position change $15,008 (ETH at [0xb233…c460](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460)); gross $15,008; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xb233…c460](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460) nets ETH -$15,008 against [0x09c3…d818](https://etherscan.io/address/0x09c30cdcdd971423cb3ba757a47d56c35d06d818) (a contract of 109 bytes; contract_like, never_sends).

Net flows: [0x09c3…d818](https://etherscan.io/address/0x09c30cdcdd971423cb3ba757a47d56c35d06d818) +6.125901 ETH ($15,008); [0xb233…c460](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460) -6.125901 ETH (-$15,008).

Event families: none.

_No qualitative note yet for this transaction._

### A119. [0x31a7…c551](https://etherscan.io/tx/0x31a71213ae5e9b968afb93a668b428f83faa4c97cb923d726e573b33e6f5c551): not yet annotated

Selected for known type audit (relay_deposit). Cluster audit-relay_deposit: 444 transactions from 219 senders, $20,055,499, shape EntryPointBeforeExecution,RelayErc20Deposit,UserOperation. Block 25,909,202 at 2026-09-05T06:01:11+00:00, index 159/399, type 0x2, success. From [0x4337…44cc](https://etherscan.io/address/0x4337007ab182ebe9cdb0bc4b96734c32176d44cc) (an EOA; window profile: bot_sender, very_high_nonce, 1030 sent to 3 destinations, nonce 77,472 to 78,501) to [0x4337…f108](https://etherscan.io/address/0x4337084d9e255ff0702461cf8895ce9e3b5ff108) (a contract of 21,738 bytes; contract_like, never_sends, router_like, called 12054 times in the window). Selector `0x765e827f`, calldata 1,316 bytes, value 0 ETH, 5 logs, tip 0.023461391 gwei. Largest position change $19,996 (USDC at [0xecdb…6cdc](https://etherscan.io/address/0xecdbde77e3556beaf2b79cb07527cdaa3dec6cdc)); gross $19,996; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xecdb…6cdc](https://etherscan.io/address/0xecdbde77e3556beaf2b79cb07527cdaa3dec6cdc) nets nothing priced against [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) (a contract of 8,628 bytes; contract_like, many_sources, never_sends).

Net flows: [0x4cd0…bc31](https://etherscan.io/address/0x4cd00e387622c35bddb9b4c962c136462338bc31) +19,999.20 USDC ($19,996); [0xecdb…6cdc](https://etherscan.io/address/0xecdbde77e3556beaf2b79cb07527cdaa3dec6cdc) -19,999.20 USDC (-$19,996).

Event families: Approval ×1, ERC20_Transfer_shape ×1, EntryPointBeforeExecution ×1, RelayErc20Deposit ×1, UserOperation ×1.

_No qualitative note yet for this transaction._

### A120. [0xd551…29c8](https://etherscan.io/tx/0xd5511c00d1bccd25ef5cfeec9b0fed5a2318e4cc892a47cfa2c3d59e1a3829c8): not yet annotated

Selected for known type audit (custody_withdrawal_to_operator). Cluster audit-custody_withdrawal_to_operator: 133 transactions from 47 senders, $22,833,903, shape transfers-only. Block 25,909,251 at 2026-09-05T06:10:59+00:00, index 1/235, type 0x0, success. From [0x05cd…eb3d](https://etherscan.io/address/0x05cdb1526f6e224e02919a4c018d9784ea25eb3d) (an EOA; window profile: hot_wallet, many_sources, very_high_nonce, 376 sent to 141 destinations, nonce 405,577 to 405,952) to [0x9c79…7e20](https://etherscan.io/address/0x9c79a33d6ece43b8c5e57bbd05dd72dd1fe27e20) (a contract of 333 bytes; never_sends, called 1 times in the window). Selector `0x1be19560`, calldata 36 bytes, value 0 ETH, 1 logs, tip 1.546726267 gwei. Largest position change $49,992 (USDC at [0x9c79…7e20](https://etherscan.io/address/0x9c79a33d6ece43b8c5e57bbd05dd72dd1fe27e20)); gross $49,992; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x05cd…eb3d](https://etherscan.io/address/0x05cdb1526f6e224e02919a4c018d9784ea25eb3d) nets USDC $49,992 against [0x9c79…7e20](https://etherscan.io/address/0x9c79a33d6ece43b8c5e57bbd05dd72dd1fe27e20) (a contract of 333 bytes; never_sends).

Net flows: [0x05cd…eb3d](https://etherscan.io/address/0x05cdb1526f6e224e02919a4c018d9784ea25eb3d) +49,999.40 USDC ($49,992); [0x9c79…7e20](https://etherscan.io/address/0x9c79a33d6ece43b8c5e57bbd05dd72dd1fe27e20) -49,999.40 USDC (-$49,992).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A121. [0x7961…9011](https://etherscan.io/tx/0x7961e2d418a29a4b1fb2a84169a388fe03286895de0d7a59b3d5161cb2d79011): not yet annotated

Selected for known type audit (safe_execution). Cluster audit-safe_execution: 268 transactions from 149 senders, $123,066,370, shape SafeExecutionSuccess. Block 25,909,442 at 2026-09-05T06:49:11+00:00, index 242/315, type 0x2, success. From [0x18bc…5dcd](https://etherscan.io/address/0x18bc99757f0bf8da83907c755df1ed809d9c5dcd) (an EOA; window profile: no tags, 5 sent to 5 destinations, nonce 1,545 to 1,549) to [0x7527…7de1](https://etherscan.io/address/0x7527eda208674d9ea02b49fea7c294f367387de1) (a contract of 171 bytes; never_sends, called 1 times in the window). Selector `0x6a761202`, calldata 964 bytes, value 0 ETH, 3 logs, tip 0.002502932 gwei. Largest position change $23,555 (USDT at [0x7527…7de1](https://etherscan.io/address/0x7527eda208674d9ea02b49fea7c294f367387de1)); gross $23,555; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x7527…7de1](https://etherscan.io/address/0x7527eda208674d9ea02b49fea7c294f367387de1) nets USDT -$23,555 against [0x858f…ce9e](https://etherscan.io/address/0x858fc326e09eb3cf1588da963b8100ea91c3ce9e) (a contract of 171 bytes; never_sends).

Net flows: [0x7527…7de1](https://etherscan.io/address/0x7527eda208674d9ea02b49fea7c294f367387de1) -23,554.00 USDT (-$23,555); [0x858f…ce9e](https://etherscan.io/address/0x858fc326e09eb3cf1588da963b8100ea91c3ce9e) +23,000.00 USDT ($23,001); [0x1eb0…01e8](https://etherscan.io/address/0x1eb0e5c4a2a0609c0eb3c167541bcb90107e01e8) +554.000000 USDT ($554.02).

Event families: ERC20_Transfer_shape ×2, SafeExecutionSuccess ×1.

_No qualitative note yet for this transaction._

### A122. [0x18b7…bed8](https://etherscan.io/tx/0x18b7ab2c2457b6b89f97b5256d79b39cb08694ea99214a0330e10b1a8ba2bed8): not yet annotated

Selected for known type audit (lido_stake). Cluster audit-lido_stake: 27 transactions from 27 senders, $4,029,801, shape LidoSubmitted,LidoTransferShares. Block 25,909,511 at 2026-09-05T07:02:59+00:00, index 60/249, type 0x2, success. From [0x438f…5acf](https://etherscan.io/address/0x438fe220bdf3d26822972147112d2b72c4825acf) (an EOA; window profile: fresh, 1 sent to 1 destinations, nonce 1 to 1) to [0xae7a…fe84](https://etherscan.io/address/0xae7ab96520de3a18e5e111b5eaab095312d7fe84) (a contract of 1,035 bytes; contract_like, many_sources, never_sends, called 452 times in the window). Selector `0xa1903eab`, calldata 36 bytes, value 16.5 ETH, 3 logs, tip 0.015628338 gwei. Largest position change $40,520 (stETH at [0x438f…5acf](https://etherscan.io/address/0x438fe220bdf3d26822972147112d2b72c4825acf)); gross $81,025; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x438f…5acf](https://etherscan.io/address/0x438fe220bdf3d26822972147112d2b72c4825acf) nets ETH -$40,505, stETH $40,520 against [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) (unknown code status; no tags).

Net flows: [0x438f…5acf](https://etherscan.io/address/0x438fe220bdf3d26822972147112d2b72c4825acf) +16.500000 stETH ($40,520); [0x438f…5acf](https://etherscan.io/address/0x438fe220bdf3d26822972147112d2b72c4825acf) -16.500000 ETH (-$40,505); [0xae7a…fe84](https://etherscan.io/address/0xae7ab96520de3a18e5e111b5eaab095312d7fe84) +16.500000 ETH ($40,505).

Event families: ERC20_Transfer_shape ×1, LidoSubmitted ×1, LidoTransferShares ×1.

_No qualitative note yet for this transaction._

### A123. [0xcce9…b959](https://etherscan.io/tx/0xcce9bb928068e8378cd1e2fa19b361a23fed46cf406de10a90547a692c5cb959): not yet annotated

Selected for known type audit (dex_swap_contract). Cluster audit-dex_swap_contract: 1,532 transactions from 186 senders, $58,918,826, shape V3Swap. Block 25,909,666 at 2026-09-05T07:34:35+00:00, index 2/88, type 0x2, success. From [0x5a21…4b72](https://etherscan.io/address/0x5a210aa8ce06570a7a97646368343c1fa7484b72) (an EOA; window profile: bot_sender, very_high_nonce, 47 sent to 1 destinations, nonce 73,770 to 73,816) to [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) (a contract of 20,805 bytes; contract_like, many_sources, never_sends, router_like, called 8356 times in the window). Selector `0x771d503f`, calldata 260 bytes, value 0 ETH, 3 logs, tip 3.520042138 gwei. Largest position change $15,287 (WBTC at [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f)); gross $30,535; swaps 1 in 1 pools; 2 distinct recipients. Principal [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) nets WBTC -$15,287, WETH $15,249 against [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) (a contract of 22,142 bytes; many_sources, never_sends, pool).

Net flows: [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) +0.191715 WBTC ($15,287); [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) -0.191715 WBTC (-$15,287); [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) -6.211563 WETH (-$15,249); [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) +6.211563 WETH ($15,249).

Event families: ERC20_Transfer_shape ×2, V3Swap ×1.

_No qualitative note yet for this transaction._

### A124. [0x5cd1…517a](https://etherscan.io/tx/0x5cd10e2fb147479f940595c5284f1b494e90fa5300384ac7848669c28a1d517a): not yet annotated

Selected for known type audit (dolomite_account_deposit). Cluster audit-dolomite_account_deposit: 26 transactions from 12 senders, $13,807,745, shape transfers-only. Block 25,909,720 at 2026-09-05T07:45:35+00:00, index 232/234, type 0x2, success. From [0xd24c…95ba](https://etherscan.io/address/0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba) (an EOA; window profile: no tags, 17 sent to 5 destinations, nonce 794 to 810) to [0xf8b2…2dff](https://etherscan.io/address/0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff) (a contract of 2,976 bytes; contract_like, never_sends, called 63 times in the window). Selector `0xb6f32e03`, calldata 164 bytes, value 0 ETH, 11 logs, tip 0.033199418 gwei. Largest position change $349,973 (USDC at [0xd24c…95ba](https://etherscan.io/address/0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba)); gross $699,946; swaps 0 in 0 pools; 2 distinct recipients. Principal [0xd24c…95ba](https://etherscan.io/address/0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba) nets USDC -$349,973 against [0xf8b2…2dff](https://etherscan.io/address/0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff) (a contract of 2,976 bytes; contract_like, never_sends).

Net flows: [0x003c…b97d](https://etherscan.io/address/0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d) +350,022.00 USDC ($349,973); [0xd24c…95ba](https://etherscan.io/address/0xd24c03ba0f33793f8f7e4a38b76a3938cd2495ba) -350,022.00 USDC (-$349,973); [0xf8b2…2dff](https://etherscan.io/address/0xf8b2c637a68cf6a17b1df9f8992eebeff63d2dff) +0.000000 USDC ($0.00).

Event families: unknown ×8, ERC20_Transfer_shape ×2, Approval ×1. Unknown topics: [0x003c…b97d](https://etherscan.io/address/0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d) 0x247e2f5b851dd23e… ×2; [0x003c…b97d](https://etherscan.io/address/0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d) 0x223e16b9e4703ea2… ×2; [0x003c…b97d](https://etherscan.io/address/0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d) 0x97c9b88667051113… ×2; [0x003c…b97d](https://etherscan.io/address/0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d) 0x91b01baeee3a24b5… ×1; [0x003c…b97d](https://etherscan.io/address/0x003ca23fd5f0ca87d01f6ec6cd14a8ae60c2b97d) 0x2bad8bc95088af2c… ×1.

_No qualitative note yet for this transaction._

### A125. [0x31ca…5e60](https://etherscan.io/tx/0x31ca5a0b7b36e65d9f053434242f42d39c0cb2a585caa7d601a921d3f78d5e60): not yet annotated

Selected for known type audit (susde_unstake_claim). Cluster audit-susde_unstake_claim: 24 transactions from 24 senders, $17,908,746, shape transfers-only. Block 25,909,816 at 2026-09-05T08:04:59+00:00, index 175/203, type 0x2, success. From [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) (an EOA; window profile: no tags, 23 sent to 13 destinations, nonce 1,166 to 1,188) to [0x9d39…3497](https://etherscan.io/address/0x9d39a5de30e57443bff2a8307a4256c8797a3497) (a contract of 17,299 bytes; contract_like, never_sends, called 137 times in the window). Selector `0xf2888dbb`, calldata 36 bytes, value 0 ETH, 1 logs, tip 0.000931553 gwei. Largest position change $1,938,219 (USDe at [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904)); gross $1,938,219; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) nets USDe $1,938,219 against [0x7fc7…3425](https://etherscan.io/address/0x7fc7c91d556b400afa565013e3f32055a0713425) (a contract of 534 bytes; never_sends).

Net flows: [0x7fc7…3425](https://etherscan.io/address/0x7fc7c91d556b400afa565013e3f32055a0713425) -1,938,219.27 USDe (-$1,938,219); [0xcf7e…c904](https://etherscan.io/address/0xcf7e7c56614b6e22b0043895a37e3858971ec904) +1,938,219.27 USDe ($1,938,219).

Event families: ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A126. [0xd13f…de13](https://etherscan.io/tx/0xd13f9b341340d5efd6d2c76452c037545c2fc3498778c915c52071479d0cde13): audit of relayed_payment_recorded: liquidity wallet 0xfd03abca… pays 84,880.29 USD of WETH into 0x5c7bcd6e… through adapter 0x9ccc2f3e…, and 0x5c7bcd6e… unwraps it for the beneficiary

Selected for known type audit (relayed_payment_recorded). Cluster audit-relayed_payment_recorded: 360 transactions from 114 senders, $64,985,221, shape WETHWithdrawal. Block 25,909,843 at 2026-09-05T08:10:23+00:00, index 1/320, type 0x2, success. From [0x8b56…9aff](https://etherscan.io/address/0x8b5606469e21c75edd7c74d1c7a65824675d9aff) (an EOA; window profile: bot_sender, very_high_nonce, 2069 sent to 1 destinations, nonce 332,652 to 334,720) to [0x9ccc…b294](https://etherscan.io/address/0x9ccc2f3ecde026230e11a5c8799ac7524f2bb294) (a contract of 212 bytes; contract_like, never_sends, router_like, called 2069 times in the window). Selector `0x1bc74526`, calldata 1,060 bytes, value 0 ETH, 7 logs, tip 2.420789646 gwei. Largest position change $84,880 (WETH at [0xfd03…b7f0](https://etherscan.io/address/0xfd03abcadaf3f930fa4e37eb2f6ea3a44a41b7f0)); gross $169,761; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xfd03…b7f0](https://etherscan.io/address/0xfd03abcadaf3f930fa4e37eb2f6ea3a44a41b7f0) nets nothing priced against [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) (a contract of 680 bytes; contract_like, many_sources, never_sends, router_like).

Net flows: [0xfd03…b7f0](https://etherscan.io/address/0xfd03abcadaf3f930fa4e37eb2f6ea3a44a41b7f0) -34.553644 WETH (-$84,880); [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) +0.000000 WETH ($0.00).

Event families: anonymous ×2, unknown ×2, Approval ×1, ERC20_Transfer_shape ×1, WETHWithdrawal ×1. Unknown topics: [0x5c7b…35c5](https://etherscan.io/address/0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5) 0x44b559f101f8fbcc… ×1; [0x9ccc…b294](https://etherscan.io/address/0x9ccc2f3ecde026230e11a5c8799ac7524f2bb294) 0x9fe6c83e48d06102… ×1.

Interpretation (LLM, confidence medium): 

Proposed type: `contract_unwrap_payout should also accept an unwrap by a contract that is not the destination when it received the WETH in the same transaction (precedence quirk; the mechanism is the cross-chain fill of 0x536d093b…)`

### A127. [0xb3bc…095e](https://etherscan.io/tx/0xb3bc8ea16bc3b8337e36154fa2c924e42ca9b49b9adf50423fa71f34af5e095e): not yet annotated

Selected for known type audit (bilateral_exchange_settled). Cluster audit-bilateral_exchange_settled: 668 transactions from 197 senders, $58,507,936, shape transfers-only. Block 25,909,898 at 2026-09-05T08:21:35+00:00, index 284/318, type 0x2, success. From [0x7bf6…6c29](https://etherscan.io/address/0x7bf6e86eea9b360a49066d7fdf12c9d2f3bc6c29) (an EOA; window profile: no tags, 14 sent to 7 destinations, nonce 8,812 to 8,825) to [0x6a00…1068](https://etherscan.io/address/0x6a000f20005980200259b80c5102003040001068) (a contract of 24,562 bytes; contract_like, many_sources, never_sends, router_like, called 1198 times in the window). Selector `0xe3ead59e`, calldata 708 bytes, value 0 ETH, 5 logs, tip 0.15 gwei. Largest position change $79,719 (WBTC at [0x7bf6…6c29](https://etherscan.io/address/0x7bf6e86eea9b360a49066d7fdf12c9d2f3bc6c29)); gross $318,682; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x7bf6…6c29](https://etherscan.io/address/0x7bf6e86eea9b360a49066d7fdf12c9d2f3bc6c29) nets WBTC $79,719, cbBTC -$79,622 against [0x0000…d701](https://etherscan.io/address/0x00000000000014aa86c5d3c41765bb24e11bd701) (a contract of 18,797 bytes; many_sources, never_sends).

Net flows: [0x0000…d701](https://etherscan.io/address/0x00000000000014aa86c5d3c41765bb24e11bd701) -1.000167 WBTC (-$79,719); [0x7bf6…6c29](https://etherscan.io/address/0x7bf6e86eea9b360a49066d7fdf12c9d2f3bc6c29) +1.000167 WBTC ($79,719); [0x0000…d701](https://etherscan.io/address/0x00000000000014aa86c5d3c41765bb24e11bd701) +0.998959 cbBTC ($79,622); [0x7bf6…6c29](https://etherscan.io/address/0x7bf6e86eea9b360a49066d7fdf12c9d2f3bc6c29) -0.998959 cbBTC (-$79,622); [0x006d…b000](https://etherscan.io/address/0x006d0e0d006109f0020f3050000a713780b7b000) +0.000000 cbBTC ($0.00); [0x6a00…1068](https://etherscan.io/address/0x6a000f20005980200259b80c5102003040001068) +0.000000 WBTC ($0.00).

Event families: ERC20_Transfer_shape ×4, anonymous ×1.

_No qualitative note yet for this transaction._

### A128. [0xe671…9eb6](https://etherscan.io/tx/0xe671775b2eae2fe77f915075d7fab86a57bbc6ec80ecd8332d3219c733189eb6): audit of stablecoin_mint: 19,997.19 USDC minted from the zero address to 0xd15e62… and forwarded, by a bot calling minter contract 0xec2c96e7…: a bridge arrival that mints

Selected for known type audit (stablecoin_mint). Cluster audit-stablecoin_mint: 280 transactions from 41 senders, $1,049,940,957, shape USDCMint. Block 25,909,898 at 2026-09-05T08:21:35+00:00, index 310/318, type 0x2, success. From [0x80fb…a135](https://etherscan.io/address/0x80fbefbee7e2bb2ac085f082674dc8c0bccfa135) (an EOA; window profile: bot_sender, very_high_nonce, 280 sent to 1 destinations, nonce 53,982 to 54,261) to [0xec2c…a7c7](https://etherscan.io/address/0xec2c96e75b09e29b66bf2ee5c37fa749ef9aa7c7) (a contract of 4,432 bytes; contract_like, never_sends, called 688 times in the window). Selector `0xdb5c7e88`, calldata 2,660 bytes, value 0.000456969769673704 ETH, 14 logs, tip 0.01 gwei. Largest position change $19,997 (USDC at [0x5d87…3ccb](https://etherscan.io/address/0x5d87666c346d99566d4238e14b89b1f344323ccb)); gross $59,993; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x80fb…a135](https://etherscan.io/address/0x80fbefbee7e2bb2ac085f082674dc8c0bccfa135) nets ETH -$1.12 against [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) (unknown code status; no tags).

Net flows: [0x5d87…3ccb](https://etherscan.io/address/0x5d87666c346d99566d4238e14b89b1f344323ccb) +20,000.00 USDC ($19,997); [0x80fb…a135](https://etherscan.io/address/0x80fbefbee7e2bb2ac085f082674dc8c0bccfa135) -0.000457 ETH (-$1.12); [0xec2c…a7c7](https://etherscan.io/address/0xec2c96e75b09e29b66bf2ee5c37fa749ef9aa7c7) +0.000457 ETH ($1.12); [0x645d…91ca](https://etherscan.io/address/0x645dadd5bf354526b68a2befd9a305f7e03b91ca) +0.000000 USDC ($0.00); [0xd15e…76c7](https://etherscan.io/address/0xd15e62e64c1265dfb753ed6e7c76cb5ff8f276c7) +0.000000 USDC ($0.00).

Event families: unknown ×9, ERC20_Transfer_shape ×3, Approval ×1, USDCMint ×1. Unknown topics: [0xec2c…a7c7](https://etherscan.io/address/0xec2c96e75b09e29b66bf2ee5c37fa749ef9aa7c7) 0x3c4422e7013dcec5… ×1; [0xec2c…a7c7](https://etherscan.io/address/0xec2c96e75b09e29b66bf2ee5c37fa749ef9aa7c7) 0x8a887d1329b2ab70… ×1; [0x2222…c205](https://etherscan.io/address/0x2222222d7164433c4c09b0b0d809a9b52c04c205) 0xbb312ce0cc311b2c… ×1; [0xec00…a6df](https://etherscan.io/address/0xec000064576f9c95a8623bc0eff3db6d296ea6df) 0xc471de166a60c0b8… ×1; [0xec00…a6df](https://etherscan.io/address/0xec000064576f9c95a8623bc0eff3db6d296ea6df) 0xe6d8040a8a6bc519… ×1; [0xc005…d239](https://etherscan.io/address/0xc005dc82818d67af737725bd4bf75435d065d239) 0x769f711d20c67915… ×1.

Interpretation (LLM, confidence medium): stablecoin_mint counts every USDC mint, so the $542M of USDC issuance in the day mixes Circle's own mints with bridge arrivals through authorised minters; bridge_in needs the bridge's event to separate them.

Unverified: the bridge; nine unregistered events accompany the mint.

### A129. [0xb365…7e5a](https://etherscan.io/tx/0xb365042c1d62728a8fb7ceb05cc27493da37b0975ba3f5b65cb2d0c7709a7e5a): 4,382,679.35 USDS staked into rewards contract 0x4e41488c… (Staked event plus a referral event)

Selected for known type audit (staking_pool_stake). Cluster audit-staking_pool_stake: 8 transactions from 3 senders, $14,850,122, shape Staked. Block 25,909,975 at 2026-09-05T08:36:59+00:00, index 260/384, type 0x2, success. From [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) (an EOA; window profile: no tags, 104 sent to 13 destinations, nonce 1,434 to 1,537) to [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) (a contract of 5,705 bytes; contract_like, never_sends, called 44 times in the window). Selector `0x42ea02c1`, calldata 68 bytes, value 0 ETH, 3 logs, tip 0.000891248 gwei. Largest position change $4,382,679 (USDS at [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69)); gross $4,382,679; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) nets USDS -$4,382,679 against [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) (a contract of 5,705 bytes; contract_like, never_sends).

Net flows: [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) +4,382,679.35 USDS ($4,382,679); [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) -4,382,679.35 USDS (-$4,382,679).

Event families: ERC20_Transfer_shape ×1, Staked ×1, unknown ×1. Unknown topics: [0x4e41…c86a](https://etherscan.io/address/0x4e41488c19cd35eb4de3083fc3e204854c75c86a) 0x16902e34d01e8d5f… ×1.

Interpretation (LLM, confidence medium): Eight stakes ($14.9M) and 11 withdrawals ($12.3M) on this contract in the day.

Unverified: which Sky farm this is; StakingRewards-style events are generic.

Proposed type: `staking_pool_stake`. Rule: Staked event and tokens entering the called contract, no swap. Method: generic

### A130. [0x54ca…1cc1](https://etherscan.io/tx/0x54caf55222aa88ad7d4fc0f9ae25a142e4328faf9c067f85fd7a8047227b1cc1): not yet annotated

Selected for known type audit (weth_wrap). Cluster audit-weth_wrap: 324 transactions from 58 senders, $36,861,067, shape WETHDeposit. Block 25,910,135 at 2026-09-05T09:09:23+00:00, index 272/343, type 0x2, success. From [0xd0d0…5bea](https://etherscan.io/address/0xd0d08887e8a5b16049534a7f3fc1de92848f5bea) (an EOA; window profile: no tags, 145 sent to 13 destinations, nonce 20,974 to 21,118) to [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) (a contract of 3,124 bytes; contract_like, many_sources, never_sends, called 7138 times in the window). Selector `0xd0e30db0`, calldata 4 bytes, value 20 ETH, 1 logs, tip 0.011 gwei. Largest position change $49,159 (ETH at [0xd0d0…5bea](https://etherscan.io/address/0xd0d08887e8a5b16049534a7f3fc1de92848f5bea)); gross $98,319; swaps 0 in 0 pools; 2 distinct recipients. Principal [0xd0d0…5bea](https://etherscan.io/address/0xd0d08887e8a5b16049534a7f3fc1de92848f5bea) nets ETH -$49,159, WETH $49,159 against [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) (a contract of 3,124 bytes; contract_like, many_sources, never_sends).

Net flows: [0xc02a…6cc2](https://etherscan.io/address/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2) +20.000000 ETH ($49,159); [0xd0d0…5bea](https://etherscan.io/address/0xd0d08887e8a5b16049534a7f3fc1de92848f5bea) +20.000000 WETH ($49,159); [0xd0d0…5bea](https://etherscan.io/address/0xd0d08887e8a5b16049534a7f3fc1de92848f5bea) -20.000000 ETH (-$49,159).

Event families: WETHDeposit ×1.

_No qualitative note yet for this transaction._

### A131. [0x2105…dfae](https://etherscan.io/tx/0x2105a12fcecbd752fa7a87728ad1eb49ecf172ad338130afda8c5b0b4a55dfae): not yet annotated

Selected for known type audit (wsteth_wrap_unwrap). Cluster audit-wsteth_wrap_unwrap: 27 transactions from 16 senders, $11,365,281, shape LidoTransferShares. Block 25,910,175 at 2026-09-05T09:17:23+00:00, index 164/191, type 0x2, success. From [0x0bea…36a0](https://etherscan.io/address/0x0bea4ec415378f6f76f6b3e72b88c3915c9b36a0) (an EOA; window profile: no tags, 3 sent to 2 destinations, nonce 72 to 74) to [0x7f39…2ca0](https://etherscan.io/address/0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0) (a contract of 6,492 bytes; contract_like, never_sends, called 192 times in the window). Selector `0xea598cb0`, calldata 36 bytes, value 0 ETH, 4 logs, tip 0.15 gwei. Largest position change $68,107 (wstETH at [0x0bea…36a0](https://etherscan.io/address/0x0bea4ec415378f6f76f6b3e72b88c3915c9b36a0)); gross $136,209; swaps 0 in 0 pools; 2 distinct recipients. Principal [0x0bea…36a0](https://etherscan.io/address/0x0bea4ec415378f6f76f6b3e72b88c3915c9b36a0) nets stETH -$68,102, wstETH $68,107 against [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) (unknown code status; no tags).

Net flows: [0x0bea…36a0](https://etherscan.io/address/0x0bea4ec415378f6f76f6b3e72b88c3915c9b36a0) +22.305921 wstETH ($68,107); [0x0bea…36a0](https://etherscan.io/address/0x0bea4ec415378f6f76f6b3e72b88c3915c9b36a0) -27.731930 stETH (-$68,102); [0x7f39…2ca0](https://etherscan.io/address/0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0) +27.731930 stETH ($68,102).

Event families: ERC20_Transfer_shape ×2, Approval ×1, LidoTransferShares ×1.

_No qualitative note yet for this transaction._

### A132. [0x2031…acdf](https://etherscan.io/tx/0x2031bdb93e252abec242a66150597bc07440887ab073ec8bbfbc6f2be7b2acdf): not yet annotated

Selected for known type audit (flash_loan_other). Cluster audit-flash_loan_other: 743 transactions from 60 senders, $4,633,471, shape MorphoFlashLoan,WETHDeposit,WETHWithdrawal. Block 25,910,185 at 2026-09-05T09:19:23+00:00, index 5/66, type 0x2, success. From [0xc35a…620b](https://etherscan.io/address/0xc35aae31ee189c92a06cebd74c802a231fc4620b) (an EOA; window profile: no tags, 16 sent to 1 destinations, nonce 1,017 to 1,032) to [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) (a contract of 18,725 bytes; contract_like, many_sources, never_sends, router_like, called 968 times in the window). Selector `0xdd225095`, calldata 932 bytes, value 0 ETH, 17 logs, tip 0 gwei. Largest position change $1.26 (cbBTC at [0x8a4f…d77f](https://etherscan.io/address/0x8a4f252812dff2a8636e4f7eb249d8fc2e3bd77f)); gross $185,286, flash-loan legs $23,153; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x8a4f…d77f](https://etherscan.io/address/0x8a4f252812dff2a8636e4f7eb249d8fc2e3bd77f) nets nothing priced against [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) (a contract of 5,914 bytes; never_sends).

Net flows: [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) -0.000016 cbBTC (-$1.26); [0x8a4f…d77f](https://etherscan.io/address/0x8a4f252812dff2a8636e4f7eb249d8fc2e3bd77f) +0.000016 cbBTC ($1.26); [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) +0.000000 USDC ($0.00); [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) +0.000000 USDT ($0.00); [0x8a4f…d77f](https://etherscan.io/address/0x8a4f252812dff2a8636e4f7eb249d8fc2e3bd77f) +0.000000 WETH ($0.00); [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) +0.000000 USDC ($0.00); [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) +0.000000 WETH ($0.00); [0x950f…a86f](https://etherscan.io/address/0x950fd558f47e234a2fde23b7d61f7ccdbcb4a86f) +0.000000 cbBTC ($0.00).

Event families: ERC20_Transfer_shape ×10, unknown ×4, MorphoFlashLoan ×1, WETHDeposit ×1, WETHWithdrawal ×1. Unknown topics: [0x5979…3320](https://etherscan.io/address/0x5979458912f80b96d30d4220af8e2e4925a33320) 0x1eeaa4acf3c225a4… ×3; [0x8a4f…d77f](https://etherscan.io/address/0x8a4f252812dff2a8636e4f7eb249d8fc2e3bd77f) 0x143f1f8e861fbded… ×1.

_No qualitative note yet for this transaction._

### A133. [0xa35f…8d9b](https://etherscan.io/tx/0xa35f36207204fef2692429d8b64c2621d19bf1a3d21512ed0377e35fc8328d9b): not yet annotated

Selected for known type audit (lido_withdrawal). Cluster audit-lido_withdrawal: 23 transactions from 12 senders, $13,475,141, shape ERC721_Transfer_shape,LidoTransferShares,LidoWithdrawalRequested. Block 25,910,252 at 2026-09-05T09:32:47+00:00, index 159/392, type 0x2, success. From [0x1077…e5a7](https://etherscan.io/address/0x107723ec0a863671fcad7ae6eb27a0a6db88e5a7) (an EOA; window profile: no tags, 4 sent to 4 destinations, nonce 462 to 465) to [0x889e…f9b1](https://etherscan.io/address/0x889edc2edab5f40e902b864ad4d7ade8e412f9b1) (a contract of 2,497 bytes; contract_like, many_sources, never_sends, called 110 times in the window). Selector `0xd6681042`, calldata 132 bytes, value 0 ETH, 5 logs, tip 0.6 gwei. Largest position change $17,428 (stETH at [0x889e…f9b1](https://etherscan.io/address/0x889edc2edab5f40e902b864ad4d7ade8e412f9b1)); gross $17,428; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x1077…e5a7](https://etherscan.io/address/0x107723ec0a863671fcad7ae6eb27a0a6db88e5a7) nets stETH -$17,428 against [0x889e…f9b1](https://etherscan.io/address/0x889edc2edab5f40e902b864ad4d7ade8e412f9b1) (a contract of 2,497 bytes; contract_like, many_sources, never_sends).

Net flows: [0x1077…e5a7](https://etherscan.io/address/0x107723ec0a863671fcad7ae6eb27a0a6db88e5a7) -7.097046 stETH (-$17,428); [0x889e…f9b1](https://etherscan.io/address/0x889edc2edab5f40e902b864ad4d7ade8e412f9b1) +7.097046 stETH ($17,428).

Event families: Approval ×1, ERC20_Transfer_shape ×1, ERC721_Transfer_shape ×1, LidoTransferShares ×1, LidoWithdrawalRequested ×1.

_No qualitative note yet for this transaction._

### A134. [0xcff5…204f](https://etherscan.io/tx/0xcff5fec9aa6638459f1a7492d86cb753749de42628e18755dce9329c1723204f): audit of exchange_withdrawal: hot wallet 0xa02f… (very_high_nonce) sends 16.2407 ETH to 0x4b84f19b…, itself a bot_sender that later pays 13-ETH calls into the silent contract 0x09c30cdc…

Selected for known type audit (exchange_withdrawal). Cluster audit-exchange_withdrawal: 7,139 transactions from 170 senders, $1,589,605,814, shape value-only. Block 25,910,393 at 2026-09-05T10:00:59+00:00, index 131/190, type 0x2, success. From [0xa02f…9f64](https://etherscan.io/address/0xa02fe00c9660bdc3363efbebb98c4d8deafd9f64) (an EOA; window profile: hot_wallet, very_high_nonce, 1818 sent to 603 destinations, nonce 204,141 to 205,958) to [0x4b84…0ccd](https://etherscan.io/address/0x4b84f19b944322df5593b9d8457b67569f7c0ccd) (an EOA; bot_sender, called 11 times in the window). Selector `0x`, calldata 0 bytes, value 16.24079836 ETH, 0 logs, tip 0.000133452 gwei. Largest position change $39,929 (ETH at [0xa02f…9f64](https://etherscan.io/address/0xa02fe00c9660bdc3363efbebb98c4d8deafd9f64)); gross $39,929; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xa02f…9f64](https://etherscan.io/address/0xa02fe00c9660bdc3363efbebb98c4d8deafd9f64) nets ETH -$39,929 against [0x4b84…0ccd](https://etherscan.io/address/0x4b84f19b944322df5593b9d8457b67569f7c0ccd) (an EOA; bot_sender).

Net flows: [0x4b84…0ccd](https://etherscan.io/address/0x4b84f19b944322df5593b9d8457b67569f7c0ccd) +16.240798 ETH ($39,929); [0xa02f…9f64](https://etherscan.io/address/0xa02fe00c9660bdc3363efbebb98c4d8deafd9f64) -16.240798 ETH (-$39,929).

Event families: none.

Interpretation (LLM, confidence medium): A withdrawal that funds an automated wallet rather than a customer; the tags show the chain but not its purpose.

### A135. [0xa80e…2ea5](https://etherscan.io/tx/0xa80ea988a3d77a607a9ac03c1af3c01d79df495805f6caee40502ac03e222ea5): audit of flash_loan_arbitrage: 110,910.06 USDC borrowed from Morpho, traded through a Fluid pool and USDT, repaid; observed net near zero

Selected for known type audit (flash_loan_arbitrage). Cluster audit-flash_loan_arbitrage: 1,386 transactions from 260 senders, $20,294,068, shape FluidSwap,MorphoFlashLoan. Block 25,910,486 at 2026-09-05T10:19:47+00:00, index 12/286, type 0x2, success. From [0x0250…b9b6](https://etherscan.io/address/0x025080f14aa3305049f9ce08d7b92368d54cb9b6) (an EOA; window profile: bot_sender, 79 sent to 1 destinations, nonce 21,324 to 21,402) to [0xcb01…3d45](https://etherscan.io/address/0xcb0151ac9479a6a0261622baa63ae843c9793d45) (a contract of 19,430 bytes; contract_like, never_sends, router_like, called 308 times in the window). Selector `0x64cd187f`, calldata 1,988 bytes, value 0 ETH, 32 logs, tip 0 gwei. Largest position change $110,917 (USDT at [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f)); gross $887,297, flash-loan legs $110,910; swaps 1 in 1 pools; 7 distinct recipients. Principal [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) nets nothing priced against [0x8de0…8de9](https://etherscan.io/address/0x8de0d3ed331ce1f29c8df04726d424a015f38de9) (a contract of 15,648 bytes; many_sources, never_sends).

Net flows: [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) -110,912.55 USDT (-$110,917); [0x585d…8b4f](https://etherscan.io/address/0x585d44727129b9c69791b10238ca605932938b4f) +110,925.66 USDC ($110,910); [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) +94,505.01 USDT ($94,509); [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) -94,516.62 USDC (-$94,503); [0x35c9…b636](https://etherscan.io/address/0x35c9a4dae1ff05788f24b5b32721d89340cbb636) +16,407.54 USDT ($16,408); [0x35c9…b636](https://etherscan.io/address/0x35c9a4dae1ff05788f24b5b32721d89340cbb636) -16,409.62 USDC (-$16,407); [0xef48…8819](https://etherscan.io/address/0xef482680be137edba1f6fea4516d314282318819) +0.577184 USDC ($0.58); [0x8de0…8de9](https://etherscan.io/address/0x8de0d3ed331ce1f29c8df04726d424a015f38de9) +0.000000 USDC ($0.00).

Event families: ERC20_Transfer_shape ×13, Approval ×12, unknown ×5, FluidSwap ×1, MorphoFlashLoan ×1. Unknown topics: [0x5979…3320](https://etherscan.io/address/0x5979458912f80b96d30d4220af8e2e4925a33320) 0x1eeaa4acf3c225a4… ×2; [0x52aa…e497](https://etherscan.io/address/0x52aa899454998be5b000ad077a46bbe360f4e497) 0x4d93b232a24e82b2… ×2; [0x35c9…b636](https://etherscan.io/address/0x35c9a4dae1ff05788f24b5b32721d89340cbb636) 0x143f1f8e861fbded… ×1.

Interpretation (LLM, confidence high): The event-supported lend-repay pairing holds and the observed net says nothing about the bot's profit, as the method documents.

### A136. [0x8053…2c4d](https://etherscan.io/tx/0x8053f5163012d6200d69c4f72dfd470c9e303cdf5b2848a8fbd908c3534c2c4d): not yet annotated

Selected for known type audit (aster_treasury_deposit). Cluster audit-aster_treasury_deposit: 34 transactions from 24 senders, $8,136,542, shape AsterDepositObserved. Block 25,910,526 at 2026-09-05T10:27:47+00:00, index 131/206, type 0x2, success. From [0x27e3…d51c](https://etherscan.io/address/0x27e3a09f2284160ca311e7edcd6312564e94d51c) (an EOA; window profile: pass_through, 2 sent to 1 destinations, nonce 6 to 7) to [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) (a contract of 855 bytes; contract_like, many_sources, never_sends, called 418 times in the window). Selector `0x0efe6a8b`, calldata 100 bytes, value 0 ETH, 2 logs, tip 0.1 gwei. Largest position change $210,009 (USDT at [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e)); gross $210,009; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x27e3…d51c](https://etherscan.io/address/0x27e3a09f2284160ca311e7edcd6312564e94d51c) nets USDT -$210,009 against [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) (a contract of 855 bytes; contract_like, many_sources, never_sends).

Net flows: [0x27e3…d51c](https://etherscan.io/address/0x27e3a09f2284160ca311e7edcd6312564e94d51c) -210,000.00 USDT (-$210,009); [0x604d…736e](https://etherscan.io/address/0x604dd02d620633ae427888d41bfd15e38483736e) +210,000.00 USDT ($210,009).

Event families: AsterDepositObserved ×1, ERC20_Transfer_shape ×1.

_No qualitative note yet for this transaction._

### A137. [0x8fa7…12d9](https://etherscan.io/tx/0x8fa7a40296616e49ace7ed4712b75e2ea74860f361cadecf5a72e9795f2b12d9): not yet annotated

Selected for known type audit (vault_withdraw). Cluster audit-vault_withdraw: 268 transactions from 184 senders, $116,130,330, shape ERC4626Withdraw. Block 25,910,813 at 2026-09-05T11:25:11+00:00, index 223/229, type 0x2, success. From [0xfb2c…2b62](https://etherscan.io/address/0xfb2c579c1d5f82c7b0f2a3479e5f9bc26bd22b62) (an EOA; window profile: no tags, 27 sent to 4 destinations, nonce 36,249 to 36,275) to [0x86eb…eb8c](https://etherscan.io/address/0x86ebdf902d800f2a82038290b6dbb2a5ee29eb8c) (a contract of 155 bytes; never_sends, called 12 times in the window). Selector `0xb4dc8294`, calldata 36 bytes, value 0 ETH, 6 logs, tip 0 gwei. Largest position change $171,289 (USDT at [0x3960…5294](https://etherscan.io/address/0x39603d55ac4511cfb13bd4709b48b1c25beb5294)); gross $171,289; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x3960…5294](https://etherscan.io/address/0x39603d55ac4511cfb13bd4709b48b1c25beb5294) nets nothing priced against [0x356b…ba7d](https://etherscan.io/address/0x356b8d89c1e1239cbbb9de4815c39a1474d5ba7d) (a contract of 11,660 bytes; never_sends).

Net flows: [0x356b…ba7d](https://etherscan.io/address/0x356b8d89c1e1239cbbb9de4815c39a1474d5ba7d) -171,281.20 USDT (-$171,289); [0x3960…5294](https://etherscan.io/address/0x39603d55ac4511cfb13bd4709b48b1c25beb5294) +171,281.20 USDT ($171,289).

Unpriced ERC-20 transfers: [syrupUSDT (self-reported)](https://etherscan.io/address/0x356b8d89c1e1239cbbb9de4815c39a1474d5ba7d) ×1 (largest raw 150000000000).

Event families: unknown ×3, ERC20_Transfer_shape ×2, ERC4626Withdraw ×1. Unknown topics: [0x86eb…eb8c](https://etherscan.io/address/0x86ebdf902d800f2a82038290b6dbb2a5ee29eb8c) 0x9fa30b5e853dc5c9… ×1; [0x86eb…eb8c](https://etherscan.io/address/0x86ebdf902d800f2a82038290b6dbb2a5ee29eb8c) 0x5fa4d8243d9549d3… ×1; [0x0cda…e21a](https://etherscan.io/address/0x0cda32e08b48bfddbc7ee96b44b09cf286f9e21a) 0x7ad3c51fdfaa55fa… ×1.

_No qualitative note yet for this transaction._

### A138. [0xfdef…ad5f](https://etherscan.io/tx/0xfdefa6f5b98d54388ca3d928db273822145e490b08bb2bf693a07c736950ad5f): not yet annotated

Selected for known type audit (batch_payout). Cluster audit-batch_payout: 939 transactions from 61 senders, $936,807,003, shape transfers-only. Block 25,911,222 at 2026-09-05T12:47:11+00:00, index 9/302, type 0x2, success. From [0x7830…6f43](https://etherscan.io/address/0x7830c87c02e56aff27fa8ab1241711331fa86f43) (an EOA; window profile: bot_sender, very_high_nonce, 2750 sent to 1 destinations, nonce 3,662,215 to 3,664,964) to [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) (a contract of 6,889 bytes; contract_like, many_sources, never_sends, called 3802 times in the window). Selector `0xca350aa6`, calldata 2,884 bytes, value 0 ETH, 29 logs, tip 0.925062722 gwei. Largest position change $14,523 (USDC at [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43)); gross $21,116; swaps 0 in 0 pools; 28 distinct recipients. Principal [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) nets IMPL:0x5732…d668 -$265.36, IMPL:0x6982…1933 -$2,956, USDC -$14,523, USDT -$3,371 against [0x36db…5a3b](https://etherscan.io/address/0x36db572874e0750a80ad993047e90c8c05305a3b) (an EOA; fresh, pass_through).

Net flows: [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) -14,524.84 USDC (-$14,523); [0x36db…5a3b](https://etherscan.io/address/0x36db572874e0750a80ad993047e90c8c05305a3b) +10,000.00 USDC ($9,999); [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) -3,371.02 USDT (-$3,371); [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) -840,104,669.45 IMPL:0x6982…1933 (-$2,956); [0x0f56…e2e2](https://etherscan.io/address/0x0f565c89b61c629a4da8b738999c0b2f6e85e2e2) +2,137.48 USDC ($2,137); [0xda90…2bf7](https://etherscan.io/address/0xda90fb313475715f4391b253548526a787222bf7) +438,610,388.22 IMPL:0x6982…1933 ($1,543); [0x566b…36b8](https://etherscan.io/address/0x566b30470d7ad97419a48900dc869bd7148736b8) +401,494,281.22 IMPL:0x6982…1933 ($1,413); [0x3434…15ea](https://etherscan.io/address/0x3434951b8d05609524105e56b2e1ddce816b15ea) +1,015.55 USDC ($1,015).

Unpriced ERC-20 transfers: [OCEAN (self-reported)](https://etherscan.io/address/0x967da4048cd07ab37855c090aaf366e4ce1b9f48) ×1 (largest raw 4263098644630000000000).

Event families: ERC20_Transfer_shape ×29.

_No qualitative note yet for this transaction._

### A139. [0x114a…062d](https://etherscan.io/tx/0x114a12c8221f7a99e8bca12f5a33f5797d1c8b8cd3af3e965354f208a943062d): not yet annotated

Selected for known type audit (ccip_token_send). Cluster audit-ccip_token_send: 6 transactions from 5 senders, $4,221,758, shape CCIPMessageSentObserved,WETHDeposit. Block 25,911,289 at 2026-09-05T13:00:35+00:00, index 66/261, type 0x2, success. From [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) (an EOA; window profile: no tags, 3 sent to 3 destinations, nonce 4,449 to 4,451) to [0x8022…6f7d](https://etherscan.io/address/0x80226fc0ee2b096224eeac085bb9a8cba1146f7d) (a contract of 11,130 bytes; contract_like, never_sends, called 102 times in the window). Selector `0x96f4e9f9`, calldata 548 bytes, value 0.000204773514059542 ETH, 7 logs, tip 0.6 gwei. Largest position change $2,312,477 (wstETH at [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a)); gross $2,312,478; swaps 0 in 0 pools; 3 distinct recipients. Principal [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) nets ETH -$0.50, wstETH -$2,312,477 against [0xa586…9fa7](https://etherscan.io/address/0xa586a732394a1affcf15b972cd47c936033c9fa7) (a contract of 22,889 bytes; never_sends).

Net flows: [0xa586…9fa7](https://etherscan.io/address/0xa586a732394a1affcf15b972cd47c936033c9fa7) +757.371326 wstETH ($2,312,477); [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) -757.371326 wstETH (-$2,312,477); [0x8022…6f7d](https://etherscan.io/address/0x80226fc0ee2b096224eeac085bb9a8cba1146f7d) +0.000205 ETH ($0.50); [0x9138…aeca](https://etherscan.io/address/0x913814782144864e523c3fdb78e3ca25d2c2aeca) +0.000205 WETH ($0.50); [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) -0.000205 ETH (-$0.50); [0x8022…6f7d](https://etherscan.io/address/0x80226fc0ee2b096224eeac085bb9a8cba1146f7d) +0.000000 WETH ($0.00).

Event families: ERC20_Transfer_shape ×2, unknown ×2, Approval ×1, CCIPMessageSentObserved ×1, WETHDeposit ×1. Unknown topics: [0xa586…9fa7](https://etherscan.io/address/0xa586a732394a1affcf15b972cd47c936033c9fa7) 0x1871cdf8010e63f2… ×1; [0xa586…9fa7](https://etherscan.io/address/0xa586a732394a1affcf15b972cd47c936033c9fa7) 0x9f1ec8c880f76798… ×1.

_No qualitative note yet for this transaction._

### A140. [0xfb3c…4bb5](https://etherscan.io/tx/0xfb3c8db76ae820d5b0f9478c3f381318f93c1ce0a0e0000fb7d261e568cd4bb5): not yet annotated

Selected for known type audit (liquidity_collect_only). Cluster audit-liquidity_collect_only: 23 transactions from 12 senders, $4,724,141, shape V3Collect,V3NFPMCollect. Block 25,911,417 at 2026-09-05T13:26:23+00:00, index 159/325, type 0x2, success. From [0x32a5…3c26](https://etherscan.io/address/0x32a5fb05b9f5eb0c64f68affcd1c33ebbe763c26) (an EOA; window profile: no tags, 10 sent to 1 destinations, nonce 4,978 to 4,987) to [0xc364…fe88](https://etherscan.io/address/0xc36442b4a4522e871399cd717abdd847ab11fe88) (a contract of 24,384 bytes; contract_like, many_sources, never_sends, router_like, called 1123 times in the window). Selector `0xfc6f7865`, calldata 132 bytes, value 0 ETH, 4 logs, tip 0.025915877 gwei. Largest position change $663,509 (IMPL:0xb58e…21cb at [0x8e43…8cef](https://etherscan.io/address/0x8e4318e2cb1ae291254b187001a59a1f8ac78cef)); gross $701,623; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x32a5…3c26](https://etherscan.io/address/0x32a5fb05b9f5eb0c64f68affcd1c33ebbe763c26) nets IMPL:0xb58e…21cb $663,509, USDT $38,113 against [0x8e43…8cef](https://etherscan.io/address/0x8e4318e2cb1ae291254b187001a59a1f8ac78cef) (a contract of 22,142 bytes; never_sends, pool).

Net flows: [0x32a5…3c26](https://etherscan.io/address/0x32a5fb05b9f5eb0c64f68affcd1c33ebbe763c26) +536,477.89 IMPL:0xb58e…21cb ($663,509); [0x8e43…8cef](https://etherscan.io/address/0x8e4318e2cb1ae291254b187001a59a1f8ac78cef) -536,477.89 IMPL:0xb58e…21cb (-$663,509); [0x32a5…3c26](https://etherscan.io/address/0x32a5fb05b9f5eb0c64f68affcd1c33ebbe763c26) +38,111.62 USDT ($38,113); [0x8e43…8cef](https://etherscan.io/address/0x8e4318e2cb1ae291254b187001a59a1f8ac78cef) -38,111.62 USDT (-$38,113).

Event families: ERC20_Transfer_shape ×2, V3Collect ×1, V3NFPMCollect ×1.

_No qualitative note yet for this transaction._

### A141. [0xb975…0d86](https://etherscan.io/tx/0xb975683a862450e905a8f3bbc2927c22c8d476c243cc9148288c6520a4b50d86): not yet annotated

Selected for known type audit (aave_v3_op). Cluster audit-aave_v3_op: 1,181 transactions from 435 senders, $897,789,601, shape AaveRepay,AaveReserveDataUpdated,AaveScaledBurn. Block 25,911,470 at 2026-09-05T13:36:59+00:00, index 109/200, type 0x0, success. From [0x5d99…2c66](https://etherscan.io/address/0x5d99551ce4a2c1467adf632474424e7e22c72c66) (an EOA; window profile: no tags, 51 sent to 16 destinations, nonce 2,868 to 2,918) to [0x8787…a4e2](https://etherscan.io/address/0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2) (a contract of 2,400 bytes; contract_like, never_sends, called 2070 times in the window). Selector `0x573ade81`, calldata 132 bytes, value 0 ETH, 5 logs, tip 0.025137761 gwei. Largest position change $99,986 (USDC at [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c)); gross $99,986; swaps 0 in 0 pools; 1 distinct recipients. Principal [0x5d99…2c66](https://etherscan.io/address/0x5d99551ce4a2c1467adf632474424e7e22c72c66) nets USDC -$99,986 against [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) (a contract of 2,400 bytes; contract_like, many_sources, never_sends).

Net flows: [0x5d99…2c66](https://etherscan.io/address/0x5d99551ce4a2c1467adf632474424e7e22c72c66) -100,000.09 USDC (-$99,986); [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c) +100,000.09 USDC ($99,986).

Unpriced ERC-20 transfers: [variableDebtEthUSDC (self-reported)](https://etherscan.io/address/0x72e95b8931767c79ba4eee721354d6e99a61d004) ×1 (largest raw 100000000002).

Event families: ERC20_Transfer_shape ×2, AaveRepay ×1, AaveReserveDataUpdated ×1, AaveScaledBurn ×1.

_No qualitative note yet for this transaction._

### A142. [0xfe29…3559](https://etherscan.io/tx/0xfe293d931611d7066e70a53a3fdfde064a163774d44a55bf3f01107897bd3559): not yet annotated

Selected for known type audit (forwarder_sweep). Cluster audit-forwarder_sweep: 359 transactions from 79 senders, $52,444,224, shape transfers-only. Block 25,911,543 at 2026-09-05T13:51:35+00:00, index 457/494, type 0x2, success. From [0x1b1e…db82](https://etherscan.io/address/0x1b1ea339ae1825ec995e29a40cb8ce497181db82) (an EOA; window profile: bot_sender, 51 sent to 1 destinations, nonce 6,977 to 7,027) to [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) (a contract of 135 bytes; contract_like, many_sources, never_sends, called 1552 times in the window). Selector `0x7b0eb57d`, calldata 228 bytes, value 0 ETH, 4 logs, tip 0 gwei. Largest position change $30,056 (USDT at [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf)); gross $30,056; swaps 0 in 0 pools; 1 distinct recipients. Principal [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) nets USDT $30,056 against [0xd300…db3f](https://etherscan.io/address/0xd300243876b5de69d4cd16429b4d5ebf2a33db3f) (a contract of 242 bytes; never_sends).

Net flows: [0xf4e1…d8cf](https://etherscan.io/address/0xf4e147db314947fc1275a8cbb6cde48c510cd8cf) +30,055.00 USDT ($30,056); [0xd300…db3f](https://etherscan.io/address/0xd300243876b5de69d4cd16429b4d5ebf2a33db3f) -30,000.00 USDT (-$30,001); [0x969d…6876](https://etherscan.io/address/0x969d412d3e86e715d843c5cb3f34e66df06d6876) -55.000000 USDT (-$55.00).

Event families: ERC20_Transfer_shape ×2, unknown ×2. Unknown topics: [0x969d…6876](https://etherscan.io/address/0x969d412d3e86e715d843c5cb3f34e66df06d6876) 0xc5a41753c75e78aa… ×1; [0xd300…db3f](https://etherscan.io/address/0xd300243876b5de69d4cd16429b4d5ebf2a33db3f) 0xc5a41753c75e78aa… ×1.

_No qualitative note yet for this transaction._

### A143. [0xaef5…4749](https://etherscan.io/tx/0xaef5aedfe316784db2413644b75ab893babaaa40dee154bd7e2fbb4430304749): not yet annotated

Selected for known type audit (flash_funded_lending). Cluster audit-flash_funded_lending: 54 transactions from 32 senders, $37,818,504, shape AaveBorrow,AaveReserveDataUpdated,AaveScaledBurn,AaveScaledMint,AaveSupply,AaveWithdraw,MorphoFlashLoan,ReserveUsedAsCollateralEnabled. Block 25,911,556 at 2026-09-05T13:54:11+00:00, index 7/245, type 0x2, success. From [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) (an EOA; window profile: bot_sender, very_high_nonce, 366 sent to 1 destinations, nonce 86,834 to 87,199) to [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) (a contract of 20,518 bytes; contract_like, many_sources, never_sends, router_like, called 366 times in the window). Selector `0x41ef3691`, calldata 1,220 bytes, value 2.66E-16 ETH, 40 logs, tip 0 gwei. Largest position change $787,259 (WETH at [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)); gross $1,142,485, flash-loan legs $56,334; swaps 0 in 0 pools; 4 distinct recipients. Principal [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) nets WETH -$747,890 against [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) (a contract of 2,400 bytes; contract_like, never_sends).

Net flows: [0x4d5f…14e8](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) +320.176836 WETH ($787,259); [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) -304.165318 WETH (-$747,890); [0x2387…086a](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a) -45,257.84 USDT (-$45,260); [0xacdb…6d07](https://etherscan.io/address/0xacdb27b266142223e1e676841c1e809255fc6d07) +45,257.84 USDT ($45,260); [0xacdb…6d07](https://etherscan.io/address/0xacdb27b266142223e1e676841c1e809255fc6d07) -16.011519 WETH (-$39,370); [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de) -0.000000 ETH ($0.00); [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) +0.000000 ETH ($0.00); [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) +0.000000 USDT ($0.00).

Unpriced ERC-20 transfers: [aEthWETH (self-reported)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8) ×4 (largest raw 304165333705020302955), [variableDebtEthUSDT (self-reported)](https://etherscan.io/address/0x6df1c1e379bc5a00a7b4c6e67a203333772f45a8) ×1 (largest raw 45257841947).

Event families: ERC20_Transfer_shape ×14, Approval ×8, AaveReserveDataUpdated ×5, AaveScaledMint ×4, AaveSupply ×3, AaveBorrow ×1, AaveScaledBurn ×1, AaveWithdraw ×1, MorphoFlashLoan ×1, ReserveUsedAsCollateralEnabled ×1, unknown ×1. Unknown topics: [0xacdb…6d07](https://etherscan.io/address/0xacdb27b266142223e1e676841c1e809255fc6d07) 0x19b47279256b2a23… ×1.

_No qualitative note yet for this transaction._

## Other transactions the LLM decoded

Transactions read with `show` during the investigation that are not representatives of any packet; they support the notes above.

- [0xb61d…6328](https://etherscan.io/tx/0xb61db8643fa8bc3b41bf5761a4d6d4cab50b2e764acc588b645756d193c36328): the same sweep ABI on vault 0xa4d65fd5…: 70,000.70 USDT pulled from a client address (confidence high). Operator 0xcc2bc4f5… (nonce 108,823) at a 2.75 gwei tip; 39 sweeps and $1.2M in the day on this vault.
- [0xf7b2…7ce2](https://etherscan.io/tx/0xf7b24a4222de88b7b3db1451edcf81c64411e16ead580a8ae901d94a70477ce2): custody vault 0xef4fb2… pays 532,139.10 USDC to settlement hub 0x555ce2… after eight approvers record the operation id in registry 0x949b3b… (confidence medium). The calldata names the vault and an operation id; registry 0x949b3b… emits one approval event per approver (eight) and an execution event; the vault emits seven records (id, recipient, amount, token). Multi-approver custody releasing inventory to a settlement hub, 44 times in the day for $2.9M.
- [0xbd1b…dc65](https://etherscan.io/tx/0xbd1b8050ab0d63db8cfe994439038d9c461b09e893be8bc8a54e51bec123dc65): exchange-scale hot wallet 0xf70da978… (nonce 4,782,114) sells 605,248.14 USDC through router 0xccc88a9d… and a 0x-Settler-style contract for 378,051.89 units of unregistered token 0xe3431676… plus a 226,996.63 USDC leg to 0x025a1375… (confidence medium). The hot wallet's USDC nets −605,162.98; the settler nets +378,166.35 USDC and pays the token; the residual USDC goes to 0x025a1375…, which may be a second fill or a fee. 81 transactions and $11.9M through this router from the same wallet in the day: an exchange converting USDC inventory into another dollar-like token.
- [0x36c5…805d](https://etherscan.io/tx/0x36c56412ab267789f0a21499cdf9e93cd7b04c24d8ef12cf4a76ab05cffc805d): Permit2 batch transferFrom: 205,578.05 USDT swept from ten addresses into 0xe4f9b0a8… (confidence high). Operator 0xa99b5736… (nonce 20,723) consolidates customer balances that approved Permit2; 34 sweeps, $1.2M in the day.
- [0x0584…acd0](https://etherscan.io/tx/0x0584b19da7b81e8244927bf782fdaba66e538052f6ac59e42900304c9048acd0): RFQ fill: taker 0x60dd465a… pays 100,000.00 USDT, maker 0x724c1cb2… pays 40.739555 WETH; settlement contract 0x8d90113a… records the order hash and delivers unwrapped ETH to the taker (confidence high). The maker is two-sided (−WETH, +USDT); the taker's ETH arrives by an internal transfer after the WETH Withdrawal, so the taker looks one-sided in receipts. 40.739555 WETH at the hourly feed is $99,939.69 against 100,004.39 USDT: a fill 6.5 basis points inside the feed (approx).
- [0x6279…96f9](https://etherscan.io/tx/0x62795aca91efec61eb7b22cf39cb2b95f544a9f39698714fd528eb3b3e5596f9): 810.151862 ETH deposited through router 0xe68ab4f9…, wrapped, and forwarded to strategy 0xcca852bc…, which records totals; share token 0x94e7a5dc… records the credit to the depositor (confidence medium). Sender nonce 299 deposits $1,996,222; 11 deposits, $2.5M through this router in the day.
- [0x5623…79f4](https://etherscan.io/tx/0x56235fb1b9fd7482d16034c4357af0a5ff6376e9ed2cfc6dd2c966b84dc379f4): executor contract 0xa5e1a817… moves 2,242,606.65 USDC from 0xe3a25228… to 0xbd22c4c7… and logs (0, 1) (confidence medium). An execute(bytes,bytes[]) call with one instruction; the asset owner approved the executor. Four transactions, $9.0M.
- [0x21be…577c](https://etherscan.io/tx/0x21be55c51f1f149976b220fe9605265c9e25bda6b22d84faacda6f2e08e2577c): payment router 0x8d04cc7e…: 53,430.64 USDT from payer 0x750dcd… splits into 53,035.56 to merchant 0xc7b9a5… and 395.08 to fee collector 0x8443e8… (0.74 percent, approx), with invoice events from registry 0xbccfef37… (confidence high). The transaction sender 0x50bf9347… (nonce 29,800) is a relayer, not the payer: the payer approved the router and the processor executes. Thirty-seven payments, $8.3M through this router in the day.

## What the quant step handed over, and what came back

Packets: 112. Annotated: 21. LLM confidence: high ×34, medium ×18. Actor tags seen among the parties of large transactions: many_sources ×31224, never_sends ×29989, very_high_nonce ×29923, hot_wallet ×19028, bot_sender ×14465, pass_through ×12090, contract_like ×11764, fresh ×7204, router_like ×4007, pool ×3691, flash_lender ×1728.

Artifacts in this directory: `prices.json`, `stats.json` (window, prices, implied prices, in-sample check, registry), `txs_all.jsonl.gz` (every transaction with its legs; not committed), `txs_big.jsonl.gz` (the population above the threshold with full features), `addresses.json.gz` (window-wide profiles of every address that touches a large transaction), `classified.json` (per-type investigation output), `types_by_hash.json.gz`, `residue.json`, `packets.json`, `rounds.json` (coverage after each classify run), `context.json` (bounded RPC lookups), `qual_notes.md` (LLM notes keyed by transaction hash, with `type`, `synthesis` and `feedback` sections), `rpc_requests.jsonl` (every request, no keys).

### Requests from the qualitative step back to the quant step (LLM)

1. Register the swap events of venues that traded without a registered swap family: the 0x-Settler-style contracts (anonymous logs at 0x00000000000014aa…, router 0xb92fe925…), the resolver-fill settlement events at 0x1111113ccf…, Solidly-style pools with Sync(uint256,uint256), and the AUSD/USDC converter 0xa19d9d64…; then trade_against_unpriced_token and bilateral_exchange_settled become two-sided swap types.
2. Add to the asset registry, with feeds or rates: USDG (0xe3431676…, 6 decimals), AUSD (0x00000000efe3…), PST, USDx, fxUSD, reUSD, DOLA, mUSD, bUSD0 at parity checks; EURC with a EUR feed; USTB (fund NAV); kBTC at the BTC feed. Keep implied pricing for PEPE, SPX6900 and wTAO.
3. Sender-cluster netting (open since iteration 2): group operator EOAs by the contract they drive (the custody ABI system, the 7702 account stack, the Bridgers service) and report system-level nets and hourly flows.
4. Persist an address book across days from the profiles (hot_wallet, many_sources, pass_through tags with their statistics) so exchange net inflow becomes a daily series and the 14,356 untagged plain transfers can be re-tagged when their counterparties become active.
5. Split plain_transfer_eoa by the recipient's later behaviour over longer windows (dormant, forwards within a day, becomes a hot wallet) and by round amounts; it is 29% of the day's USD.
6. Trace-based follow-ups: the flash-loan bots' payoff (observed priced net is at or below zero); the silent ETH deposits into 0x5cb16a39… and 0x09c30cdc… (13 to 52 ETH per call, no logs); the 100-ETH deposits with 32-byte recipients into 0xd90e2f92…; the 1,167-byte contract 0x4c21b757… that pays USDC with an Aave-shaped Withdraw event.
7. Record the secondary matches: 58,094 rows match more than one rule; report the most common pairs (exchange_deposit versus deposit_sweep, contract_payout versus custody types) and fix precedence explicitly rather than by list order.
8. Extend statuses to fetch receipts for no-log native transfers of any size that touch profiled addresses: 544,825 native legs were dropped from address nets for want of a receipt.
9. Allow the two-argument Deposit/Withdraw record families in transfer-only shapes (the LINK withdrawal at 0xa60b5146… and the 8 remaining Deposit-recorded cases) and add an operator batch type for one payer to several recipients without events (0x9188db28…).
10. Re-run the final registry on the next day without new rules to measure drift; the four-round trace in rounds.json is the baseline.

Coverage measures rule matching, not classification accuracy or verified economic intent. Multiple matching types are retained in `all_matches_by_hash.json.gz`; primary labels use registry order. Every selected occurrence has a record in `investigations.jsonl.gz`. No-log native transfers below the selection threshold are not receipt-resolved, and their value is excluded from address flow profiles.

Limitations: only top-level ETH value is visible, so ETH moved by contracts (including the ETH side of Uniswap v4 swaps and of WETH unwraps forwarded onward) is not counted. Tokens outside the registry are unpriced unless they had enough swaps against priced assets, and implied prices assume 18 decimals. Prices are hourly for ETH and BTC and window-end for the rest; stablecoins outside the feed set are taken at parity. Transaction status is inferred from the presence of logs or checked in receipts for large native candidates and packets. Hourly endpoint marks are retrospective and must not be used as contemporaneous prices in a trading backtest. Actor tags are behavioural proxies over the research window, not identities. Contract identities named in the notes without an onchain check are model memory. A rule matches the first type in registry order, so a transaction that does two things is typed by whichever rule comes first.

