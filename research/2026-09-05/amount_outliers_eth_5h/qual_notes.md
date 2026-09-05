# Qualitative investigations and rule feedback

These notes are the LLM investigation performed by Codex during this session. Amounts and movements come from saved Ethereum transactions and logs; protocol attributions use the linked primary references. Confidence in a transfer mechanism is distinct from confidence in ownership, intent, or profitability. Rules are screening rules, not a validated intent classifier.

## synthesis

The most useful taxonomy describes **which economic position changes**: an asset changes hands, is exchanged, becomes collateral, repays debt, becomes a share claim, enters liquidity, or initiates a cross-chain claim. A second layer describes execution: relayer, account contract, temporary funding, batch, or router. A single transaction can occupy several layers; retain all matches and use one primary type only for non-overlapping counts.

Three recurring mistakes would change the research conclusion. First, the gas payer is often different from the asset owner. Second, a large gross amount may be temporary borrowing or a deposit routed through an intermediary. Third, a positive cash delta can be withdrawn collateral, borrowed inventory or a settlement fee. It is not necessarily profit. The review therefore promoted role-aware transfer methods, lending-plus-swap methods, and a dedicated internal-account decoder, while tightening several inherited rules.

The largest individual position change is about $27.34M. That figure ranks observed address/asset deltas. The sum across the window counts repeated movements of capital. It must not be described as unique capital, trading volume or profit. The supplemental screen is necessary: the $25.80M flash-funded example below has only about $49 of largest observed net change.

## type operator_token_batch

An operator calls a small helper with a batch interface, but tokens move directly from the asset owner to the beneficiary. The $20M USDT example has zero token net at both the gas payer and the helper. The reusable method identifies the largest actual asset sender, classifies each leg as from the called account, into it, or between third parties, and reports recipients separately. The rule pins the observed helper, selector and completion topic. It does not establish common ownership or the commercial purpose of the transfer.

## type contract_token_execution

An account executes token transfers under an external caller's instruction. Calldata and outgoing transfers corroborate the execution mechanism. Code presence at the window end supports the account interpretation for inspected representatives; it is not a historical code proof for every occurrence. The rule only recognizes three observed execution selectors with Transfer/Approval logs and priced token legs leaving the called account. A selector alone, or a mixture involving swaps and debt, does not satisfy it. Unpriced activity remains a limitation.

## type relay_deposit

An asset enters the documented Relay depository and a deposit identifier is recorded. The asset becomes settlement inventory or escrow associated with an order. A separate fill may occur elsewhere. The rule combines the official Ethereum address, the documented deposit event and incoming value. See [Relay deployments](https://docs.relay.link/references/protocol/addresses) and [depository ABI](https://docs.relay.link/references/protocol/contracts/evm-depository).

## type relay_settlement_withdrawal

The depository releases funds under an allocator-authorized execution. The observed recipient may be a solver replenishing its inventory. Calling this a user bridge withdrawal would skip the settlement relationship. Match the documented emitter and RelayCallExecuted event plus outgoing tokens; then inspect the beneficiary and amounts. The [depository mechanism](https://docs.relay.link/references/protocol/components/depository) and [solver guide](https://docs.relay.link/references/protocol/guides/for-solvers) support this interpretation. Destination execution is not observed here.

## type aster_treasury_deposit

Funds enter Aster's documented Ethereum trading treasury. This is funding of a trading-system balance, not an onchain trade or a demonstrated leverage change. The observed deposit topic plus incoming funds at that specific deployment is the persistent recognition rule. Attribution is supported by [Aster's contract list](https://docs.asterdex.com/overview/what-is-aster/our-smart-contracts); the event is labelled observed because its full semantic ABI has not been independently established here.

## type aster_treasury_withdrawal

The same treasury pays a beneficiary after a relayed instruction. The payout can include principal, earnings, or a combination; the Ethereum transfer does not reveal the prior trading account. Keep the gas payer separate from the recipient. Require the documented Ethereum treasury, observed withdrawal topic and outgoing token legs. This rule is specific to that deployment, not any chain that happens to use the same address.

## type ccip_token_send

A token holder requests cross-chain delivery through the Ethereum CCIP router. The large token leg enters a pool while a much smaller fee is paid separately. A message event proves a source-chain request. It does not prove delivery or minting on the destination. Match router address, ccipSend selector, message event and sender token outflow, then retain message identifiers for a future cross-chain investigation. References: [Ethereum router address in the bridge documentation](https://docs.katana.network/katana/technical-reference/bridging/) and [CCIP OnRamp source](https://github.com/smartcontractkit/chainlink-ccip/blob/main/chains/evm/contracts/onRamp/OnRamp.sol).

## type dolomite_account_deposit

The user sends USDC through a proxy into DolomiteMargin. The economic result is an internal account credit; an ERC-20 receipt-token transfer is unnecessary. The new method decodes owner, account number, market, signed deltaWei and signed newPar from LogDeposit. DeltaWei is a token amount; newPar is interest-indexed principal and must not be read as the same unit. The first pass found one USDC example. Preserving all unknown topics in the final scan exposed five additional occurrences in WETH, weETH and USD1. The same documented decoder succeeded on all six; these are within-window corroboration, not an out-of-time validation set. Four resulting principal balances are positive, one remains negative and one reaches zero. In particular, an incoming deposit can repay debt rather than create new supplied collateral. References: [core deployments](https://docs.dolomite.io/smart-contract-addresses/core-immutable) and [margin events](https://docs.dolomite.io/developer-documentation/dolomite-margin-events).

## type flash_funded_lending

Temporary borrowing supports collateral and debt adjustments. Identify the loan and its repayment, then separately inventory supply, borrow, repay and withdraw events. A cash outflow into an aToken reserve may create a collateral claim; interpreting it as a loss discards the other side of the position. The method combines flash-loan statistics with lending operations. Before/after debt and collateral balances would be required to calculate leverage and account health.

## type lending_with_swap

A position adjustment can release collateral or borrow tokens while also trading. This family must precede an apparent positive-net arbitrage shape. The deterministic method identifies lending operations and retains swap evidence; the qualitative question becomes which claim was exchanged for which cash flow. Positive cash is insufficient to establish income. The generic event-family match does not identify every Aave fork, so protocol-specific conclusions still require emitter verification.

## type liquidity_with_swap

Liquidity management and inventory trading occur together. A swap can prepare token proportions for a position, rebalance an existing position, or accompany its exit. Count both mechanisms. A transaction-local record does not establish just-in-time liquidity, fee extraction or a farming strategy; that requires matching position IDs and liquidity lifetimes across transactions.

## type liquidity_collect_only

A Collect event pays tokens already owed. Without Burn or DecreaseLiquidity in the transaction it is not evidence of newly removed liquidity. The payment may include fees, principal owed from a prior burn, or both. Future investigation should pair the position's historical accrual and burn records with this collection.

## ethereum 0x0fff7095c88bae0c4fc9ee2d14038b803e17f36c349dcde31cb9c9ab6cbd62f8
mechanism: Operator-mediated movement of 20 million USDT
confidence: high for the observed transfer mechanism; ownership unresolved

Exactly 20,000,000 USDT moves from 0x17dc4d78e8abca9408c43541beb3c8215655403a to 0xaa8ba7d4611437141192e7ceced531bc0a133efb. The gas payer calls helper 0xee39678386f5bfc68df2c65656ec8e23f60063b5 using selector 0xe4c705e9 and four dynamic arrays. Its completion event accompanies the direct third-party transfer. Neither caller nor helper owns the transferred amount according to these logs. A separate hash-sampled occurrence, [0xaa63d920…](https://etherscan.io/tx/0xaa63d92016a516de6444e4340856bae91adacd757a2b776c1dcfbc5eb76b1cd3), repeats the shape at approximately $11,363, supporting a rule that is independent of the original amount.

## ethereum 0xfec01dde6895fad8be1546bfbb88bf41ba3a2a3ee45c6e853af05814e60faa40
mechanism: Account contract sends its USDC inventory under an external caller's instruction
confidence: high for asset roles; low for organizational identity

The called account 0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055 sends exactly 2,225,999.4 USDC. Its execute(address,uint256,bytes) calldata contains a nested token transfer. The account has 209 bytes of code at the window-end inspection. The gas payer is a different address. The [hash-sampled second occurrence](https://etherscan.io/tx/0x3506bc93aea5ac2c47c5ff15aa7164078b57bcbe19d052fda5b73279f1dc5fb7) has about $59,991 of position change and matches the same bounded transfer rule. Repeated account-to-account movements may be treasury rebalancing, but common ownership is not established.

## ethereum 0x4d88590a4090c115e014215af5ab8821f85b6514062d4e648fa5750ec70a2006
mechanism: Relay settlement inventory released to a recipient
confidence: high for depository release; medium for solver role

The documented depository sends 299,815.497068 USDC to 0xf70da97812cb96acdf810712aa562db8dfa3dbef, also the transaction caller. RelayCallExecuted accompanies the transfer. The documented allocator execution mechanism explains why the caller can receive a large amount without being the original depositor. A second [sampled withdrawal](https://etherscan.io/tx/0xc2eea794efbd3c4236b6f10c7ca19a35076c651589947051317fac5bf17295a7) repeats the pattern. The paired deposit family is illustrated by [a 10,000 USDT deposit](https://etherscan.io/tx/0x594d7cdaa9cd5902d658dc8aa1d98f7f53942713dcde30312ca0300d7ebbaf3a).

## ethereum 0x9ab578056349cbb44f9bd8aae747501bddd4c048d5dfef22a04f894aa8886795
mechanism: Funding an Aster trading-system balance
confidence: high for treasury attribution and transfer; account effect inferred

The user sends 1,499,975.07 USDT into Aster's documented Ethereum treasury. The deposit topic identifies the sender and token. This provides a reusable deposit signature, while the actual trading balance ledger is outside the observed transfer logs.

## ethereum 0x4c6cc1f54110227a5865d74dfc27d3ca1d47d82c6c39c6033c07cd55d288a0f0
mechanism: Aster treasury payout to a beneficiary
confidence: high for payout; prior trading result unknown

The treasury sends 3,799,974.5 USDT to a beneficiary distinct from the gas-paying operator. The observed withdrawal topic records an identifier, beneficiary and token. This transfer cannot be read as $3.8M of profit; the user's original capital and prior account history are missing.

## ethereum 0x114a12c8221f7a99e8bca12f5a33f5797d1c8b8cd3af3e965354f208a943062d
mechanism: CCIP request locks wstETH and pays a separate message fee
confidence: high for Ethereum initiation; destination completion unobserved

757.371326073454579542 wstETH, valued around $2.315M, enters a token pool. The top-level native fee is only 0.000204773514059542 ETH, around $0.50, and is wrapped and forwarded on the message path. The router's ccipSend call and CCIP message event explain the large token movement and tiny native value. Gross transfer accounting must not combine the bridged principal and repeated fee-routing legs as new capital.

## ethereum 0x19f149ac2a151cf8855bb6452a3b419e3bacac4bf40de17f4f1352dfdbf6a338
mechanism: USDC deposit credited to a Dolomite internal account
confidence: high for documented event decoding; five further within-window occurrences

4,080,625.967555 USDC travels from the user through a proxy into DolomiteMargin. Two transfers produce about $8.160M gross traffic, but about $4.080M of largest position change. LogDeposit credits account 0, market 2, with positive deltaWei 4080625967555 and newPar 3891060986173. The source field identifies the proxy. Interest-index updates explain why principal units differ; they are not a second deposit. The new dedicated decoder can investigate subsequent occurrences without another LLM interpretation of this ABI.

## ethereum 0x593cc846acfa8ab351b4ac8b8663206da87f51c798d3615f7e8927ce5b5d0016
mechanism: Large temporary funding with little observed net displacement
confidence: high for ordered lender round trip; incomplete strategy accounting

Matched Morpho funding is approximately $25.801M and gross priced legs approximately $51.602M, while the largest observed address/asset net is about $49.29. A position-change-only screen would miss the operation. The unpriced token and WETH withdrawal mean the full economic result is unresolved; the visible residual is not profit. Preserve the flash principal, repayment and non-loan legs as separate measurements.

## ethereum 0xaef5aedfe316784db2413644b75ab893babaaa40dee154bd7e2fbb4430304749
mechanism: Temporary funding used during a lending adjustment
confidence: high for flash and lending combination; leverage change unmeasured

The transaction borrows and returns about 22.911 WETH temporarily, while Aave events record three supplies, one borrow and one withdrawal. The large negative observed cash net at the helper accompanies collateral supply. Calling it a trading loss would omit the collateral claim. The new flash_funded_lending rule investigates debt and collateral operations separately from the temporary funding.

## ethereum 0x90c68d21460c9752b8bbe536a8e052627b0069c71299cc908d177288d28891df
mechanism: Lending-position adjustment that superficially resembles arbitrage
confidence: high for repay/withdraw and swaps; profit not established

Aave Repay and Withdraw events occur with three swaps and about $1.748M of positive observed WETH cash at the selected principal. This was an overly broad positive-net multi-pool candidate. The new lending_with_swap type takes priority because released collateral can explain the cash. Determining account PnL requires its liabilities and prior collateral position.

## ethereum 0x84421f1ca5d985b7c4fdd57e4d20fb947bdb8ad9aaaf99833e2e29b8ff5d3655
mechanism: Native-value contract call with an unresolved custom record
confidence: high that this is not established WETH wrapping; purpose unresolved

The transaction sends 14.528253197062476 ETH with selector 0x810c705b and one custom log. There is no canonical WETH Deposit event. The previous rule mistook native value plus one log for wrapping. The revised rule requires a real wrap leg and returns this case to the unknown queue. A route-like string in the custom log does not prove the service identity or completion.

## ethereum 0xfcb06a2e24b43beadff24dca822a2e9f6abfb58f74faf45ab7e7df3410a7addd
mechanism: Source-chain CCTP burn for a bridge request
confidence: high for the event-supported mechanism

USDC Burn occurs with CCTPv2DepositForBurn. A generic stablecoin redemption label would miss the cross-chain claim. Bridge initiation now precedes generic supply destruction. Ethereum alone does not establish destination minting.

## ethereum 0xb48219e059fd1c60de893fbae1583b71909dd380b4a35fa8d2581a2acd9ecb58
mechanism: CoW settlement with residual settlement balances
confidence: high for documented settlement; residual economic ownership unresolved

CoW Trade and Settlement events accompany small positive residual balances. The inherited positive-net rule could call these arbitrage. The verified CoW settlement rule now takes priority. Settlement fees, residual inventory and strategy profit must be distinguished using the actual solver and order accounting.

## ethereum 0xfb3c8db76ae820d5b0f9478c3f381318f93c1ce0a0e0000fb7d261e568cd4bb5
mechanism: Liquidity position collects tokens already owed
confidence: high for collection; fee-versus-principal split unresolved

About 38,113.29 USDT is collected without a Burn event in this transaction. This supports collect-only rather than newly removed liquidity. Historical position records are needed to distinguish accrued fees from principal owed after an earlier burn.

## ethereum 0x56235fb1b9fd7482d16034c4357af0a5ff6376e9ed2cfc6dd2c966b84dc379f4
mechanism: Unresolved helper-mediated third-party transfer
confidence: high for asset path; low for service purpose

A call to 0xa5e1a817… with selector 0x24856bc3 accompanies a roughly $2.24M USDC transfer between third parties. Related occurrences make this a high-value research cluster. The transfer mechanism is clear, but the helper's business role is not established. Do not promote a bridge, exchange or arbitrage label without verified code, decoded authorization and a corresponding liability or settlement record.

## ethereum 0x21be55c51f1f149976b220fe9605265c9e25bda6b22d84faacda6f2e08e2577c
mechanism: Unresolved routed payout with a small secondary recipient
confidence: high for split amounts; fee interpretation provisional

The router pulls 53,430.641117 USDT, sends 53,035.559155 to one recipient and 395.081962 to another, retaining zero. The smaller share is about 0.7394% and is fee-like. A split is measurable; a merchant payment or service fee is an interpretation that needs contract semantics. This remains in the unknown queue instead of being relabelled solely to increase coverage.

## feedback

Implemented feedback: verify native candidate receipts and token decimals; fix the BTC feed and vault-share unit; preserve all priced legs before netting; exclude the zero address from economic holders; require lender events for flash pairs; avoid actor identity from a shared router; distinguish v4 pools by manager plus pool ID; retain complete unknown topics; preserve overlapping labels; add 12 rules and a Dolomite account decoder; prioritize bridge and settlement mechanisms; audit actual wrapping, staking-with-swaps and collect-only cases.

Remaining uncertainty is explicit work for later windows. For unfamiliar high-value clusters, retrieve verified source and historical implementation, decode custom liabilities and authorization, and add a falsifiable rule only after a second occurrence or a clearly marked single-example test. For MEV and PnL, obtain internal native traces and before/after balances, debt and collateral, then replay the counterfactual execution. For bridge delivery, follow the message on the destination chain only in a separately authorized broader study. Those missing facts cannot be reconstructed reliably from Ethereum transfer logs alone.

## ethereum 0xbfab93a1d6f770012c597a6e9d20cd515028da66f9db0733b36c717156689519
mechanism: Dolomite deposit brings a signed account balance to zero
confidence: high for event-decoded account credit

The decoder learned from the USDC example also reads this WETH deposit: market 0, deltaWei 164003085836927234331 and newPar 0, credited to the same numbered account that earlier had negative principal. A zero resulting principal is materially different from newly supplied positive collateral. Another 74 WETH deposit leaves negative principal of -161124820699726407386. Thus the quantitative investigation must retain the sign and resulting account state, not just the word Deposit. Four of the six observed credits leave positive principal, one negative and one zero.

## ethereum 0x8fa7a40296616e49ace7ed4712b75e2ea74860f361cadecf5a72e9795f2b12d9
mechanism: withdrawal from an ERC-4626 vault — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $171,288.72; event families: ERC20_Transfer_shape ×2, ERC4626Withdraw ×1, unknown ×3. A withdrawal-shaped event accompanies assets leaving the reserve for a recipient. The principal exchanges a share or internal claim for cash; the cash is not automatically income. Share identity and pre-withdrawal holdings are not reconstructed for every account.

## ethereum 0x55114460ee91ab4bbb48c7090e8b7d06cb5f18f3a3982facaea7b395d618d1a9
mechanism: liquidity management with an embedded swap — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $690,376.78; event families: Approval ×2, ERC20_Transfer_shape ×2, V4ModifyLiquidity ×1, V4Swap ×1, WETHDeposit ×2. ModifyLiquidity and Swap coexist in this representative. The transaction manages liquidity while exchanging inventory. Its positive visible WETH does not establish strategy profit because native settlement and position claims are incomplete.

## ethereum 0xe0c62c06d396e637f4907577a43309a2dcb959f0f35fb33f951d3805a1140f8b
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $143,743.15; event families: ERC20_Transfer_shape ×1, unknown ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0x7ec99e46f693398023fe5d8803a22bcdc57e7fb6e05be0052c81a2cc685643b2
mechanism: swap sent straight to the pool — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $30,110.39; event families: CurveTokenExchange ×1, ERC20_Transfer_shape ×2. The called destination itself emits a Curve exchange event. This establishes direct pool interaction. The counterasset may be outside the priced registry; a large one-sided priced delta can therefore overstate economic exposure.

## ethereum 0x51c226f9ff9905a223da2b65a2b84cd616ee05fe7772a27f915fb8be4e1d8dbb
mechanism: withdrawal from an exchange-like hot wallet — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $13,603.33; event families: no logs. The transfer is observable; exchange withdrawal is a behavioural hypothesis derived from the sender profile. A distributor or treasury can have the same pattern. Do not treat the wallet label as verified identity.

## ethereum 0x3506bc93aea5ac2c47c5ff15aa7164078b57bcbe19d052fda5b73279f1dc5fb7
mechanism: contract-account token execution — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $59,990.96; event families: ERC20_Transfer_shape ×1. An account executes token transfers under an external caller's instruction. Calldata and outgoing transfers corroborate the execution mechanism. Code presence at the window end supports the account interpretation for inspected representatives; it is not a historical code proof for every occurrence. The rule only recognizes three observed execution selectors with Transfer/Approval logs and priced token legs leaving the called account. A selector alone, or a mixture involving swaps and debt, does not satisfy it. Unpriced activity remains a limitation.

## ethereum 0x1e04f1fe931101c7b27d938196dd5a00bd281ea8398175bd3d0ab297c4d8bf0c
mechanism: account-abstraction bundle — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $65,195.28; event families: ERC20_Transfer_shape ×1, EntryPointBeforeExecution ×1, UserOperation ×1, unknown ×1. UserOperation and EntryPoint events identify account-abstraction execution. That is an execution layer: the economic event here is a token transfer by an account inside the bundle, not a transfer of the bundler inventory.

## ethereum 0x4c091278e2c33d02c7944bf4bb0c3c51d1e19789f554129ba74b5c5623b414bc
mechanism: Compound v3 operation — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $20,774.48; event families: CompoundV3Withdraw ×1, ERC20_Transfer_shape ×1. The Compound-shaped Withdraw record accompanies a USDC outflow. Withdrawal can reduce supplied principal or increase borrowing depending on the account state; the event and cash alone do not prove a debt-free exit. Protocol deployment identity is not independently checked for every emitter in this generic rule.

## ethereum 0x9d969b2bf01875baaa16d2c2770027f6d98fef1e914a3a4a176c0a9a1856dabd
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $653,929.59; event families: ERC20_Transfer_shape ×1, unknown ×4. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0x7192f4554cb41d51f11b8758e63dbc04e9d1fa35009ba8342118fb669d37e6c5
mechanism: Native payment carrying reference data
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $65,466.12; event families: no logs. No event establishes a contract operation. Calldata can be a payment reference. Window-end code inspection cannot prove historical code status, so this remains unresolved.

## ethereum 0xb65e2c95b108dd355b06f86a62e4e2fe6018ed9281fc0b63a1c5970c976db788
mechanism: Lido withdrawal request or claim — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $328,502.73; event families: ERC20_Transfer_shape ×1, ERC721_Transfer_shape ×1, LidoTransferShares ×1, LidoWithdrawalRequested ×1, unknown ×1. WithdrawalRequested plus locked stETH and an NFT supports an exit request. It is not finalized ETH receipt. The claim requires a later finalization and collection.

## ethereum 0xaa63d92016a516de6444e4340856bae91adacd757a2b776c1dcfbc5eb76b1cd3
mechanism: operator-mediated token-transfer batch — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $11,362.91; event families: ERC20_Transfer_shape ×1, unknown ×1. An operator calls a small helper with a batch interface, but tokens move directly from the asset owner to the beneficiary. The $20M USDT example has zero token net at both the gas payer and the helper. The reusable method identifies the largest actual asset sender, classifies each leg as from the called account, into it, or between third parties, and reports recipients separately. The rule pins the observed helper, selector and completion topic. It does not establish common ownership or the commercial purpose of the transfer.

## ethereum 0x4cdc25aaf3063232605d83b0ccaa76c8a5cb1f361ff876c90abf22c5b58fa273
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $76,678.82; event families: ERC20_Transfer_shape ×8, unknown ×8. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0xfdefa6f5b98d54388ca3d928db273822145e490b08bb2bf693a07c736950ad5f
mechanism: one sender paying many recipients — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $14,522.80; event families: ERC20_Transfer_shape ×29. Many transfer legs distribute the called account inventory across recipients. Count recipients and their shares, not just transaction value. Payroll, exchange withdrawal processing and treasury distribution cannot be distinguished from the shape alone.

## ethereum 0xf8b542f25af89d6e443efbd1561feff4ad9b26f4bb2803545f5ab77848f2f815
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $61,736.82; event families: ERC20_Transfer_shape ×1, unknown ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0x7bd2a01d6e392d1f2c93f2b17d00654ac7c134671461db303cb6ce22476b0953
mechanism: call on an EIP-7702 delegated account — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $12,348.26; event families: ERC20_Transfer_shape ×6. The transaction envelope is type 0x4. It proves the authorization-list mechanism is present, not ownership of every participating account or the intent of its transfers. An execute selector alone would not meet this rule.

## ethereum 0x31317c580fcb678a2cf3d1ecfaaf0e76b5caf22b7dd38f600cf6485c30d38840
mechanism: stablecoin issuance — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $577,455.29; event families: ERC20_Transfer_shape ×1, USDCMint ×1, unknown ×1. A stablecoin mint is observable. The receiver gains token supply, but the custom event may encode settlement or a bridge message. External dollar issuance is not established and the complete business type may be narrower than this mechanical label.

## ethereum 0x4fe91f834e6b25df200d0febdb87e457b71e67e0153babf65e6978602b3db9d4
mechanism: NFT sale — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $14,399.38; event families: ERC20_Transfer_shape ×5, ERC721_Transfer_shape ×3, SeaportOrderFulfilled ×3. SeaportOrderFulfilled plus NFT and WETH movements supports marketplace exchange. The largest address delta can aggregate several orders; it is not automatically the price of one NFT.

## ethereum 0x6b6e032f2a75b70ed87e1d894c4e8d131c36a7b96ea7912944c7f3b4bb614ee7
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $1,336,425.40; event families: Approval ×1, ERC20_Transfer_shape ×4, unknown ×7. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0xe0387338c5e52ad69e1d412004f73675cda2b325a21d24ad10016f9c2fdef5ec
mechanism: Unresolved incoming funds to the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $200,008.78; event families: ERC20_Transfer_shape ×1, unknown ×1. The destination receives a priced asset. A deposit, escrow top-up, purchase or debt repayment can share this flow. Decode the custom record and identify the claim or liability created before promoting an economic type.

## ethereum 0xd1421db708c1c054372ced23dca39577f33d816f84ee23127cac7064391c96f6
mechanism: Uniswap v4 liquidity change — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $72,913.76; event families: ERC20_Transfer_shape ×2, ERC721_Transfer_shape ×1, PermitTransfer ×2, V4ModifyLiquidity ×1. ModifyLiquidity and position-token evidence support a v4 position change. The manager address is shared by many pools; pool ID is required for strategy history. Native settlement may be missing from transfer logs.

## ethereum 0x2be999b8f670d1d24c03beafbd4ffd6ff8e9a72713e48bdd82077d7dc34730cb
mechanism: swap with an unclear principal — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $71,090.69; event families: Approval ×1, ERC20_Transfer_shape ×6, V3Swap ×1, WETHWithdrawal ×1, unknown ×2. A swap occurs, but neither caller nor called contract has a complete two-sided priced vector. A third-party beneficiary, unknown token or internal ETH can explain the missing side. Trace actual transfer endpoints before choosing the principal.

## ethereum 0x651f7bf5092f3d03cfdde0014ca1d2a8dbda43cdf1b8e17e2de53a7c8c0e23a9
mechanism: plain transfer without a behavioural subtype — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $134,981.01; event families: ERC20_Transfer_shape ×1. A simple asset transfer is the supported mechanism. This rule does not prove that both endpoints lack code or establish why the payment occurred; the historical EOA identifier is only a registry key.

## ethereum 0x5f0cd52d9f4697c55e5b61a06fa91d0a166c90e4fecb5c6b124556d23c6dd942
mechanism: Unresolved incoming funds to the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $2,010,754.05; event families: ERC20_Transfer_shape ×2, unknown ×2. The destination receives a priced asset. A deposit, escrow top-up, purchase or debt repayment can share this flow. Decode the custom record and identify the claim or liability created before promoting an economic type.

## ethereum 0xcbadb24d61bdae869df7688bd1b8d46488fd0ff5aba0658b6db37dd7eca94575
mechanism: transfer between high-connectivity wallets — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $10,196.61; event families: ERC20_Transfer_shape ×1. The two high-connectivity profiles explain the classification. They do not establish that both wallets have the same owner or that this is an internal exchange movement.

## ethereum 0xb975683a862450e905a8f3bbc2927c22c8d476c243cc9148288c6520a4b50d86
mechanism: Aave v3 supply, borrow, repay, withdraw or liquidation — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $99,986.02; event families: AaveRepay ×1, AaveReserveDataUpdated ×1, AaveScaledBurn ×1, ERC20_Transfer_shape ×2. Repay at the pinned Aave core pool accompanies USDC entering the reserve and a debt-token burn. This is a liability reduction rather than consumption or a trading loss. Before/after debt state would quantify the remaining obligation.

## ethereum 0x594d7cdaa9cd5902d658dc8aa1d98f7f53942713dcde30312ca0300d7ebbaf3a
mechanism: deposit into Relay settlement escrow — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $10,000.44; event families: ERC20_Transfer_shape ×1, RelayErc20Deposit ×1. An asset enters the documented Relay depository and a deposit identifier is recorded. The asset becomes settlement inventory or escrow associated with an order. A separate fill may occur elsewhere. The rule combines the official Ethereum address, the documented deposit event and incoming value. See [Relay deployments](https://docs.relay.link/references/protocol/addresses) and [depository ABI](https://docs.relay.link/references/protocol/contracts/evm-depository).

## ethereum 0xc2eea794efbd3c4236b6f10c7ca19a35076c651589947051317fac5bf17295a7
mechanism: Relay depository settlement withdrawal — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $11,246.41; event families: ERC20_Transfer_shape ×1, RelayCallExecuted ×1. The depository releases funds under an allocator-authorized execution. The observed recipient may be a solver replenishing its inventory. Calling this a user bridge withdrawal would skip the settlement relationship. Match the documented emitter and RelayCallExecuted event plus outgoing tokens; then inspect the beneficiary and amounts. The [depository mechanism](https://docs.relay.link/references/protocol/components/depository) and [solver guide](https://docs.relay.link/references/protocol/guides/for-solvers) support this interpretation. Destination execution is not observed here.

## ethereum 0x6d6e73757ffff36ca1366a2db3b66e9af3241680b7ef53da3d56f2db8e43a32a
mechanism: deposit into an exchange-like wallet — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $10,590.24; event families: ERC20_Transfer_shape ×1. The receiver has the many-source profile used by this rule. The actual transfer is supported, while exchange identity and customer-deposit purpose remain hypotheses.

## ethereum 0x3e797135a6e3c4a8081fb41a1c61fd200a55d03ff981fe35f8e11c8641e6e946
mechanism: liquidity withdrawn from a pool — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $59,146.70; event families: ERC20_Transfer_shape ×3, V3Burn ×1, V3Collect ×1, V3DecreaseLiquidity ×1, V3NFPMCollect ×1, WETHWithdrawal ×1. Burn/DecreaseLiquidity and Collect occur together, supporting a liquidity reduction followed by payment. The WETH withdrawal makes internal ETH relevant, and the returned amount is not all fee income.

## ethereum 0x5e50d8446acddf5a1b19e2259bc8ff8e814d56ec3dc902378c08c5290f37fbfc
mechanism: token moved by an operator (transferFrom) — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $31,025.99; event families: ERC20_Transfer_shape ×1. The transferFrom call separates the operator paying gas from the token owner named in calldata and logs. Ownership movement is measurable; the commercial relationship and prior authorization history require follow-up.

## ethereum 0x0e167dcd74e5f0e06ef82ddfe1be047e82ac33bad9ba6f904f3fa2dd67c6b16d
mechanism: Aster trading-treasury deposit — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $391,960.50; event families: AsterDepositObserved ×1, ERC20_Transfer_shape ×1. Funds enter Aster's documented Ethereum trading treasury. This is funding of a trading-system balance, not an onchain trade or a demonstrated leverage change. The observed deposit topic plus incoming funds at that specific deployment is the persistent recognition rule. Attribution is supported by [Aster's contract list](https://docs.asterdex.com/overview/what-is-aster/our-smart-contracts); the event is labelled observed because its full semantic ABI has not been independently established here.

## ethereum 0xdab83a7baaefb0969143fbc79797893d25b646b0ab3fb47e78d5e6df7c068906
mechanism: deposit into an ERC-4626 vault — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $11,461.11; event families: ERC20_Transfer_shape ×2, ERC4626Deposit ×1, unknown ×2. The deposit-shaped event and underlying movement support creation of a vault claim. Underlying and shares must be treated as two representations of capital, and gross legs do not measure fresh inflow.

## ethereum 0x77f4184a35d35f88d400dfaf3326fadf985f09745bd12f61b9e419d25fb9f29c
mechanism: flash loan without a swap — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $0.00; event families: Approval ×10, BalancerFlashLoan ×1, ERC20_Transfer_shape ×9, unknown ×9. A Balancer loan and repayment are observable despite effectively zero priced net. Numerous unknown events remain. The absence of registered Swap events means no recognized swap, not proof that no trade occurred.

## ethereum 0x6dbfa2acacbf8380bd226116b19f686d68cc10db3eb4d743c96a4a30be60e94a
mechanism: sweep of a deposit address — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $17,783.77; event families: ERC20_Transfer_shape ×1. The source has the pass-through profile: little retained window net and concentration into one destination. This supports consolidation as a hypothesis. Opening balances, ownership and off-window activity are unknown.

## ethereum 0xb75c1181b350fc8d9ed9f19e3a65ef415efdfd4b86169112154c71ef913f5161
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $68,002.98; event families: ERC20_Transfer_shape ×1, unknown ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0xd3c533ec3299d58bb434688c75716d53f335fb0164405b4ae95db1500caef5ac
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $2,254,607.83; event families: ERC20_Transfer_shape ×6, unknown ×6. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0x6773405492693dcb69381df1d8e3ca70f288b30ae151b794b7b0d82e0d26efa3
mechanism: swap inside sandwich-pattern candidate — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $24,581.20; event families: ERC20_Transfer_shape ×4, V2Swap ×1, V2Sync ×1, V3Swap ×1, WETHDeposit ×1. This swap lies between the identified bracketing legs. The observed ordering does not quantify harm; replay the pool state without those legs before claiming a worse execution.

## ethereum 0xd5aed2decd70bce18c7a0289e266d2b3829fa9c7dde2a6e15280b261d24ef8af
mechanism: stETH wrapped or unwrapped — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $49,709.02; event families: AggregatorSwapped ×1, Approval ×1, ERC20_Transfer_shape ×5, LidoTransferShares ×2, WETHWithdrawal ×1, unknown ×4. The wrapper conversion is a component of this transaction. AggregatorSwapped and WETHWithdrawal also appear, so this is not a pure representation change. The wrapper rule recognizes its component; the full route needs the aggregator ABI and missing native legs.

## ethereum 0x340585e4871d17a24f0f99760890c47e18132b604159eec2473532ef273f04f7
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $997,043.27; event families: ERC20_Transfer_shape ×1, unknown ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0x14f5b4e81404fa47c7372022c1f5271c22404b359c6b04147ed28125ba0912d4
mechanism: Aster trading-treasury payout — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $78,233.28; event families: AsterWithdrawalObserved ×1, ERC20_Transfer_shape ×1. The same treasury pays a beneficiary after a relayed instruction. The payout can include principal, earnings, or a combination; the Ethereum transfer does not reveal the prior trading account. Keep the gas payer separate from the recipient. Require the documented Ethereum treasury, observed withdrawal topic and outgoing token legs. This rule is specific to that deployment, not any chain that happens to use the same address.

## ethereum 0xa82a7e2707ab5eb08ad3da1818180fb494d87f38822a6a5c0d287ce37a76d01d
mechanism: par conversion through a peg-stability module — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $48,642.77; event families: Approval ×10, DSNote ×3, ERC20_Transfer_shape ×14, MorphoFlashLoan ×1, PSMBuyGem ×1, V4Swap ×1, unknown ×3. PSMBuyGem appears together with Morpho flash funding and a v4 swap. A reserve conversion is part of a larger atomic route. The primary PSM label must not be read as a simple fee-free user conversion or as excluding temporary funding.

## ethereum 0xa4cbeccb176710bd9b98a1d0b2f055d1dda69bb15b770756cca516db0b0021d5
mechanism: multisig (Safe) execution — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $24,986.48; event families: ERC20_Transfer_shape ×1, SafeExecutionSuccess ×1. SafeExecutionSuccess records account execution while the account transfers its own inventory. The external caller is not the economic payer merely because it submitted the transaction.

## ethereum 0x7112aefaf1c053491953def1c60e9e293dc5514846ee85f6f5091b0fd84567db
mechanism: lending-position adjustment with swaps — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $10,204.45; event families: AaveReserveDataUpdated ×2, AaveScaledBurn ×1, AaveScaledMint ×1, AaveSupply ×1, AaveWithdraw ×1, Approval ×4, ERC20_Transfer_shape ×15, ERC4626Deposit ×1, ERC4626Withdraw ×1, V2Swap ×1, V2Sync ×1, V3Swap ×1, unknown ×1. Aave Supply/Withdraw, ERC-4626 operations and swaps coexist. The account moves capital between lending and vault claims while trading. The negative USDC cash delta is paired with position changes, so it is not a standalone loss.

## ethereum 0xc3f3ef739de84f541bc510d7eaeb28578edfe49e53509d653f638b33a637395a
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $57,357.51; event families: ERC20_Transfer_shape ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0x3b35f8d7748fd595199b1b45e9110e832fd422dc2afc966e4d2a752233ef305e
mechanism: Morpho Blue market operation — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $499,929.65; event families: ERC20_Transfer_shape ×5, ERC4626Withdraw ×1, MorphoAccrueInterest ×1, MorphoWithdraw ×1, unknown ×4. The Morpho withdrawal appears inside an ERC-4626 withdrawal path. This primary lending label records the downstream market operation; a vault claim is also being redeemed. Both matches must remain available.

## ethereum 0xc12b9f1e7a97b5ddc0528b7b67d0a6451490e1a05919fdb17e2a114307b97bc2
mechanism: liquidity provided to a pool — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $71,258.97; event families: ERC20_Transfer_shape ×1, ERC721_Transfer_shape ×1, V3IncreaseLiquidity ×1, V3Mint ×1. Mint and IncreaseLiquidity accompany capital entering a pool and an NFT position. The NFT represents a position, not a marketplace purchase. Duration and fee yield need position history.

## ethereum 0x8db21aa8588c2ccc017edcbe4ac96595d59870367ffa5cd62f1c874bb8c02b25
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $501,116.88; event families: ERC20_Transfer_shape ×1, unknown ×1. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0x53b3d3efbaef177d98068dd9927aafb3615d6421f68e121bb476d8424734e6fe
mechanism: positive observed-net multi-pool strategy — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $17,210.95; event families: BalancerSwap ×1, ERC20_Transfer_shape ×5, V3Swap ×1, unknown ×1. Multiple pool events and positive observed principal net support a candidate strategy. Unknown events, missing native transfers, unpriced positions and fees prevent an economic profit conclusion.

## ethereum 0xe26d69a9a8f2441cc49ef9f6cb4c3bc67778f3e41d6bb587c7a5ee54dda3935b
mechanism: intent, limit-order or RFQ fill — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $23,496.69; event families: Approval ×2, CurveTokenExchangeU ×1, DODOSwap ×1, ERC20_Transfer_shape ×63, UniswapXFill ×1, V2Swap ×1, V2Sync ×1, V3Swap ×7, V4Swap ×5, WETHDeposit ×1, WETHWithdrawal ×2, anonymous ×2, unknown ×12. UniswapXFill appears with a long multi-venue route. The user order and solver inventory are separate economic objects. Repeated routed legs do not imply the user traded the gross summed amount.

## ethereum 0xfebfe1c22170b48e8c0852b9be2e10ac8c29649edc3cce420a7dc761ea4062b8
mechanism: other liquid-staking or restaking operation — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $49,217.22; event families: Approval ×4, ERC20_Transfer_shape ×4, ERC721_Transfer_shape ×1, LidoTransferShares ×2, unknown ×5. The token mint/burn path supports an LST or restaking-related operation. The NFT and custom records indicate a richer position or withdrawal request. A generic LST label does not prove a new validator deposit or immediate cash exit.

## ethereum 0xb0bbda9deb0bee9554141d77d11c5864b5695f73bf9cedb2586945893fbdaed2
mechanism: ETH wrapped into WETH — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $17,477.23; event families: WETHDeposit ×1. The canonical WETH Deposit event is present. It supports creation of WETH for the credited address. The ETH source can be internal to a calling contract, so a missing top-level ETH debit is not free value creation.

## ethereum 0xd8ea92ab8b28075a75b2cddc0f010c66e599fac010cb5331d3590f4a23833518
mechanism: sandwich-pattern candidate — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $12,738.20; event families: ERC20_Transfer_shape ×2, V3Swap ×1. The detector found same-sender opposite-direction bracketing in one pool and block. Packet evidence supports an ordering candidate. Profit, coordinated beneficial ownership and execution harm require state replay.

## ethereum 0xb36ab2c35024c7b4c8b78825bdd7131c884c79d93586fc55c8ef78c07dba2770
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $199,899.19; event families: ERC20_Transfer_shape ×1, unknown ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0xfc92bf66acd76e215c57d49c19cd0b06de20476636c5e5c73f00c71feeca930a
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $199,899.19; event families: ERC20_Transfer_shape ×1, unknown ×1. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0x2ab480dd9ad48677343d36602cbf3338de7ae76d0769b967f7ae7e423c84ea3e
mechanism: Unresolved asset payout from the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $502,617.18; event families: ERC20_Transfer_shape ×1, unknown ×1. The called address loses a priced asset and a beneficiary receives it. Custom records or execution data may encode an authorization or liability, but their semantics are not established. A payout method can measure the asset path; identifying a withdrawal, settlement or transfer between related owners needs verified code and account history.

## ethereum 0x24608c7a8b4223345d421b1aa373311f6a75b0e904af183165e9005170d53365
mechanism: stablecoin redemption — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $164,492.79; event families: DSNote ×6, ERC20_Transfer_shape ×6, ERC4626Withdraw ×1, SafeExecutionSuccess ×1, unknown ×5. Token supply decreases inside a Safe and ERC-4626 withdrawal path. This primary type records a burn component; it does not prove external fiat redemption. The vault and account-execution evidence must accompany the interpretation.

## ethereum 0x807620e60e0819d110c9c14edcb3cd6cc757b3c9c96a4d31e509b1b3b9bcf25f
mechanism: swap by a contract principal — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $10,640.04; event families: ERC20_Transfer_shape ×4, V4Swap ×2, anonymous ×1. The called account has opposite asset deltas and v4 swaps. It substitutes inventory through pools. Use v4 pool IDs and account for missing native settlement before measuring route economics.

## ethereum 0x3f29f7c70d3a759e88bcb9dbd0f00dac1848ad819496ef99d430a8b036c9267f
mechanism: bridge withdrawal finalized on Ethereum — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $101,675.69; event families: CCTPMintAndWithdraw ×1, ERC20_Transfer_shape ×1, USDCMint ×1, unknown ×1. CCTP MintAndWithdraw and USDC mint support inbound token release on Ethereum. The mint is the local completion mechanism of a cross-domain claim, not proof of fresh external dollar issuance.

## ethereum 0x0c5725b45d88f2c3670eab871390a18c3cf456056f8df4466eabbff7f878166b
mechanism: deposit into a bridge toward another chain — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $15,012.82; event families: AcrossFundsDeposited ×1, WETHDeposit ×1. A bridge deposit event accompanies value entering the source-side mechanism. WETH creation can be an internal conversion of the same native amount. Destination delivery is outside this Ethereum-only study.

## ethereum 0xcd51ec30432d3ecb2de2961c7d4ef66ce3af73576de0d01909c474d5ba72c34d
mechanism: CoW Protocol batch settlement — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $40,074.60; event families: Approval ×1, CoWInteraction ×2, CoWSettlement ×1, CoWTrade ×1, ERC20_Transfer_shape ×4, unknown ×1. Trade and Settlement at the documented CoW contract identify solver settlement. Separate user fills from solver fees and routed pool inventory before estimating trade size or profit.

## ethereum 0x68ca1f11d84ac9f523e63d549767d3465bcc32fda85dd54f6cbda83a8eb87d2b
mechanism: Unresolved incoming funds to the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $123,481.30; event families: ERC20_Transfer_shape ×1, unknown ×1. The destination receives a priced asset. A deposit, escrow top-up, purchase or debt repayment can share this flow. Decode the custom record and identify the claim or liability created before promoting an economic type.

## ethereum 0xa1fe42dc63c251fd9350b86f363b82aedc9034db35fd96290f1e8df5da2114b3
mechanism: user swap through a router — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $22,500.00; event families: CurveTokenExchange ×1, ERC20_Transfer_shape ×9, ERC4626Withdraw ×1, unknown ×4. The sender has opposite signed deltas across assets and a swap event. ERC-4626 withdrawal in this representative indicates a combined redemption and trade. A two-sided cash vector is not a complete portfolio return.

## ethereum 0x5d928fdb3e054e39815138b55e723ee0831fe7586287d9a23f91a4d55a491a82
mechanism: ETH staked with Lido — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $12,267.09; event families: ERC20_Transfer_shape ×1, LidoSubmitted ×1, LidoTransferShares ×1. Submitted with native ETH entering Lido and stETH-related records supports a liquid-staking deposit. The resulting token is a claim on pooled staked ETH, not a second independent inflow.

## ethereum 0x64b7f1e671684f98ec9dd7b9c8a9bc21abf74609902e2650b9a9128634ba6f8f
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $183,524.92; event families: ERC20_Transfer_shape ×1, unknown ×1. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0xc22deaa850a192f9d880f37b52ab1d8960e041e684ba9e694269571fa3364034
mechanism: Unresolved incoming funds to the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $40,061.36; event families: unknown ×1. The destination receives a priced asset. A deposit, escrow top-up, purchase or debt repayment can share this flow. Decode the custom record and identify the claim or liability created before promoting an economic type.

## ethereum 0xd8211b4174ac2b4d552fe0c166906a74ac42b57cf25dd2115439e0d338e3c4ae
mechanism: Unresolved transfer between third-party addresses
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $87,495.22; event families: Approval ×1, ERC20_Transfer_shape ×5, unknown ×5. The gas payer and called helper are not the main priced asset endpoints. The quantitative path is an operator-mediated movement. Service identity and authorization semantics remain unknown; repeated amounts alone do not establish a bridge, exchange or profitable cycle.

## ethereum 0xe03f9ee3b994289a46cf2884a8b9d6d8a2426601ee873777c75d76c00a805464
mechanism: Unresolved incoming funds to the called account
confidence: transfer path observed; economic type unresolved

Packet evidence: largest observed address/asset change $1,230,400.10; event families: unknown ×1. The destination receives a priced asset. A deposit, escrow top-up, purchase or debt repayment can share this flow. Decode the custom record and identify the claim or liability created before promoting an economic type.

## ethereum 0x029957ff904ac0065bc2f4ba587fcf08caed40c1abd6c863d91b95e4082954e3
mechanism: validator deposit — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $1,340,890.03; event families: BeaconDeposit ×1, unknown ×1. DepositEvent accompanies a large native-value call through an intermediary. The event supports a validator deposit component. The top-level value is not independently proven to equal the amount sent internally to the beacon deposit contract.

## ethereum 0x5e2fc4b51a5d54154438b59d49320df05879c3af6cc0282518d0db9f8e781aac
mechanism: WETH unwrapped into ETH — known-method packet review
confidence: packet-level corroboration; economic intent not independently validated

Packet evidence: largest observed address/asset change $80,798.25; event families: WETHWithdrawal ×1. Canonical WETH Withdrawal destroys the WETH representation. Its ETH return is internal and missing from the full transfer census. A negative WETH delta is not a loss.
