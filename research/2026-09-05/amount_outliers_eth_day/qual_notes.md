# Qualitative notes for the day-long Ethereum type loop

Written by the LLM (Claude, this session) after reading `packets.json` of each classify round, `stats.json`, `classified.json`, `residue.json`, the day-long address profiles, and per-transaction `show` output. Entries are keyed by transaction hash. Exact figures are copied from packet facts and decoded events; derived figures (sums, ratios) are marked approx. Contract identities that rest on model memory are listed under `unverified`. Each residue entry ends with the type it proposed; the rule and method then live in `scripts/type_registry.py`, and `rounds.json` records what the rule changed. Codex grew the registry on a five-hour window earlier the same day (`research/2026-09-05/amount_outliers_eth_5h`); its notes were not saved before its session ended, so its types carry their qualitative description in the registry only.

## synthesis
One day of Ethereum mainnet (2026-09-04 14:00 to 2026-09-05 14:00 UTC): 7,173 blocks, 1,793,396 transactions, 5,962,702 logs. The screen selected 67,572 transactions (65,290 by a position change of at least $10,000, 24,864 by gross priced legs of at least $100,000, 2,524 by an event-supported flash principal of at least $10,000), summing to $26.0B of largest position changes; 18,500 are at or above $100k, 3,434 at or above $1M, 333 at or above $10M; the median is $36,707 and the largest $389.4M. Receipts were fetched for the 7,852 no-log native transfers above the threshold; 13 had failed and were excluded.

The loop. Codex's registry from the five-hour window (58 types) typed 90.45% of the day's selected transactions and 92.95% of their USD on replay, leaving 6,455 transactions ($1.83B) in 1,765 residue clusters. Two rounds of LLM investigation on the residue added 22 mechanical types (custody vaults, payment rails, delegated-EOA execution, unregistered-token trades, settlements, sweeps, staking pools, sUSDe claims) and took coverage to 99.12% and 99.80%. A fourth round re-read one hash-sampled occurrence of every known type; it found three rules that over-reached (an Aave-fork rule accepting any four-argument Withdraw shape, an unpriced-trade rule swallowing vault deposits that mint receipt tokens, aggregator swaps landing in the bilateral-exchange type), fixed them, and added eight long-tail shapes; the final registry of 90 types covers 99.88% of transactions and 99.91% of USD, with 81 transactions ($24.6M) in 50 clusters left. Coverage measures rule matching, not verified intent: 58,094 of the 67,572 rows match more than one rule and registry order decides.

What the day was made of, by group of largest position changes: plain and helper-mediated transfers $9.54B (17,354 transactions), exchange flow $7.24B (23,334), stablecoin issuance and par conversion $2.98B (2,024), wallet infrastructure $1.66B (3,692), lending $1.66B (2,684), bridges $929M (3,330), custody and settlement contracts $778M (3,477), DEX trading $371M (5,598), vaults $334M, liquidity $185M, staking $131M, payments $76M, MEV $41M (2,425).

Exchange flow, the largest identifiable mechanism, was one-directional: 9,792 deposits into exchange-tagged wallets ($3.84B) against 7,139 withdrawals ($1.59B), a net inflow of $2.25B to wallets that receive from many sources and pay many destinations, plus 4,802 deposit-address sweeps ($1.06B) and 1,601 transfers between exchange-like wallets ($750M). The largest sink was contract 0xa9d1e08c… (6,889 bytes), which took $964M in 852 deposits and is also the origin of 729 batch payouts: an exchange's deposit-and-withdrawal contract. 0x28c6c062… took $639M in 2,142 deposits and paid $119M in 509 withdrawals; 0xcd531ae9… took $574M in 98. Deposits and withdrawals both peak in the first hours of the window (14:00 to 17:00 UTC: 836, 740, 682 deposits per hour) and trough between 23:00 and 03:00 UTC (about 285 per hour). The 14,356 plain transfers that carry no behavioural tag ($7.53B, median $40k, 88 of them above $10M) remain the largest class of unknown purpose: USDC $4.46B, USDT $1.41B, ETH $737M, cbBTC $292M; 1,346 come from wallets on their first or second transaction.

Stablecoin supply moved by hundreds of millions: USDC minted $542M and burned $409M (net +$133M), DAI minted $351M and burned $257M, USDS minted $60M and burned $95M, USDe +$26M and −$10M, RLUSD +$21.5M and −$7.5M; EURC (unregistered, priced from its swaps) minted $3.4M and burned $3.6M, Kraken's kBTC minted $3.2M, cbBTC minted $100M in nine transactions. The Sky peg-stability path converted $961M in 1,383 transactions, $490M of it in seven transactions between USDC and sUSDS. Bridges sent $527M out (LayerZero packets $188M, OFT sends $183M, CCTP v2 burns $173M, Arbitrum inbox $55M, OP portal $40M, LiFi $27M) and finalized $398M in (CCTP v2 mints $218M, LayerZero deliveries $144M). Lending: Aave v3 core $898M in 1,181 operations (USDC supplies $164M and withdrawals $150M, cbBTC supplies $91M, wstETH supplies $78M, USDT borrows $52M), Morpho Blue $178M in 943, and the Aave-v3 fork at 0xc13e21b6… (SparkLend by model memory) $273M in 83 operations of eight-figure size (wstETH withdrawals $74M, USDS repayments $71M, cbBTC supplies $42M, USDS borrows $39M).

Flash loans are the day's largest gross number and its smallest economic one: 1,386 flash-funded swap strategies borrowed $24.0B (Morpho 0xbbbb…: 1,301 loans, $22.1B; 0x26de7861…: 66 loans, $1.86B; Balancer: 68 loans, $32M), median loan $1.0M and maximum $399M, while the principal's observed net in priced assets is $0.00 at the median and at the 90th percentile and −$55k in sum: whatever these bots earn is paid in unpriced tokens, to the block builder in ETH, or not at all. 743 further flash loans ($22.3B) carried no swap. Sandwich candidates: 136 bracketing legs (79 front, 77 back) by five senders, 0xae2fc483… alone 47 legs around 27 intervening swaps, concentrated in two USDC/WETH pools; observed nets of $322 and $462 per bot over the day say the same thing about where the payoff sits. Atomic arbitrage without loans: 118 transactions with a median observed net of $1.91.

The residue investigation found a layer the pilot could not see in two minutes: custody and settlement contracts whose Ethereum legs are one-sided by design. A custody system with four vault contracts sharing one ABI (sweep, signed payout, withdraw-to-caller) moved $248M in 410 calls; ERC-7821 execute() calls moved $366M in 412 transactions from accounts that `resolve` showed to be EIP-7702-delegated EOAs (19 designators among the ~400 addresses looked up), executed by operator EOAs paying the gas; contract payouts by operators $292M (1,263), relayed payments recorded by the contract $67M (368), forwarder sweeps from 1,431 per-customer contracts $52.5M (360), a cross-chain swap service whose calldata carries USDT(TRON)|<address>|0.05|bridgers| memos ($10.6M in 234 deposits; its payouts are typed separately), payment routers that split a fee of 74 basis points at the median. DEX volume outside pools: 668 bilateral exchanges through settlement contracts ($58.5M), of which USDC into USDG (Global Dollar, resolved from the token contract) accounts for 110 transactions and $14M, and the same hot wallet 0xf70da978… (nonce 4.78M) converted USDC to USDG through a 0x-Settler-style path in 154 swaps for $55M. Eighty-two tokens outside the registry were priced from their own swaps; the largest by volume are USDG ($11.6M), PST ($10.3M), AUSD ($5.3M), USDx, fxUSD, reUSD, DOLA, PEPE, bUSD0, wTAO, SPX6900 and mUSD.

Three quant findings the rules established. (1) A dollar threshold on Ethereum selects exchange plumbing first (34% of selected transactions), then custody infrastructure, then DeFi; the day-long address profile (transactions sent, distinct destinations, distinct sources, pass-through netting) separates them without any address list. (2) Gross volume and flash principal measure bot configuration; the position-change metric plus a same-asset lend-repay pairing is what isolates economic size. (3) Contract-mediated transfers need the direction of legs relative to the called contract (into it, out of it, through it, third party to third party) and the presence of a record event to be typed; those four features, with the actor tags, typed 99.9% of USD.

## feedback
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

## type aave_fork_lending_op
Every occurrence in the window is at pool 0xc13e21b648a5ee794902342038ff3adab66be987, which model memory identifies as the SparkLend pool (an Aave v3 fork run by the Sky ecosystem); the assets (USDS, cbBTC, wstETH) fit that memory. The inherited registry pinned aave_v3_op to the Aave core pool and registered a Spark family whose signature is identical to Aave's, so it could never match; these $10M-$33M positions therefore sat in the residue as the largest clusters by USD. The lending method separates supply, borrow, repay and withdraw; positions before and after are not visible, so leverage cannot be inferred.

## type custody_vault_abi_transfer
Four vault contracts (0x100ae042…, 0x367c42a6…, 0x3a5cc868…, 0xa4d65fd5…) share one ABI: sweep(address account, address token) pulls an approved client balance into the vault, payout(address to, uint256 amount, address token, uint256 deadline, uint256 nonce) sends under a signed instruction, and withdraw(address token, uint256 amount) hands tokens to the calling hot wallet. Operator EOAs with nonces in the hundreds of thousands drive them at flat tips. Single vault-to-vault movements of $12M-$28M are internal rebalancing, not customer flow; the sweep and withdraw legs are the customer-facing ones. Identity of the custodian is not established.

## type smart_account_execute_transfer
Selector execute(bytes32,bytes) with mode word ending 7821 0001 is ERC-7821 batch execution. The largest occurrences are USDC moves between a small set of account contracts (0xf90caf00…, 0x37e77355…, 0xafa1b5c1…, 0xd8eafb08…, 0x42bd41e6…) executed by one or two operator EOAs, then out to external addresses in round $5M-$10M pieces. The inherited eip7702_delegated rule kept only type-4 transactions, which is right for proving delegation, but it left this account-contract traffic untyped. Whether each account is a contract or a delegated EOA is answered by `resolve` for the packet addresses.

## type trade_against_unpriced_token
Two venues dominate: a 0x-Settler-style path (router 0xb92fe925…, settler 0x00000000000014aa…) whose only logs are anonymous, and a resolver-fill venue whose settlement contract 0x1111113ccf… emits per-account events the registry does not name. In both, the position-change metric sees only the priced side, so the transaction looks like a one-sided payment. The type is mechanical; pricing the other side needs the token in the registry or an implied price from pools.

## ethereum 0x2f3c690b65baaebdbaf819f137193e3a17795f0fdb7c2f5f1b54f42c3786d7e6
mechanism: ERC-7821 execute() on account contract 0xf90caf00… sending 11,054,870.43 USDC to account contract 0x37e77355…
confidence: high
unverified: who operates the account stack. resolve: 0xf90caf00…, 0x37e77355…, 0xafa1b5c1…, 0xd8eafb08… and 0x42bd41e6… all hold 23-byte EIP-7702 delegation designators, so they are delegated EOAs, not contracts.
type_proposed: smart_account_execute_transfer
rule_proposed: selector 0xe9ae5c53, only transfer events, every priced leg leaves the called account, no swap
method_proposed: custody_flow (gas payer versus asset owner, leg directions)
The operator EOA 0x4297b5… (nonce 17,263) calls execute with mode 0x…7821 0001 and a single transfer; the account nets −11,053,315.01 USD and the recipient account +11,053,315.01. Twenty transactions in the day use this account for $83.8M, and the recipient account itself sends $79.4M onward in 54 transactions (see 0xc343dc20…). Round amounts, one operator, accounts calling accounts: an institutional custody or treasury system built on smart accounts, moving USDC between its own tiers before external payouts.

## ethereum 0xc343dc20c47f06d5a6151b1e6e5994ddabbe19691e7c492bd2a26e6c02bdf982
mechanism: the next tier of the same account stack: 0x37e77355… pays 4,999,296.50 USDC to an external address by execute()
confidence: high
unverified: as above.
type_proposed: smart_account_execute_transfer
The account that received $11M in 0x2f3c690b… pays out in $5M pieces; the recipient 0x3f66eb… has no tags in the day profile, so it is a customer or a counterparty rather than another hub.

## ethereum 0x0eaf268feec4878c972f483d4a942672b55056e0bad1893be6009b220c4fe54c
mechanism: execute() on account 0xafa1b5c1… paying 2,000,087.78 USDT to a quiet address
confidence: high
type_proposed: smart_account_execute_transfer
Same ERC-7821 shape in USDT; 26 transactions and $26.4M through this account in the day.

## ethereum 0x37145e97b7d40dcfb6127ad6def2219ab9dad0cdc04503169ddde2ddba59b641
mechanism: execute() on account 0xd8eafb08… moving 9,998,593.00 USDC to account 0xafa1b5c1…
confidence: high
type_proposed: smart_account_execute_transfer
A third tier: 0xd8eafb08… feeds 0xafa1b5c1…, which then pays customers (0x0eaf268f…). Three transactions, $24.2M.

## ethereum 0x2c5e110f7420ad57334325b50c72cf112dc616c528953837a1f6d91fdf5775a3
mechanism: execute() on account 0x42bd41e6… paying 5,999,155.80 USDC to a pass-through address
confidence: high
type_proposed: smart_account_execute_transfer
The recipient 0x3e2d22… carries the pass_through tag (few sources, one destination, net zero over the day): the payout is forwarded on within the day, the signature of an exchange deposit address. Twenty-five transactions and $64.4M through this account.

## ethereum 0xf19bce7fb3d6342f5ba89a48af02c4438308df86bba0062b13299ec8735ba272
mechanism: custody vault sweep: 15,000,000.00 USDC pulled from 0x9ab0f0… into vault 0x100ae042… by sweep(account, token)
confidence: high
unverified: the custodian's identity; that 0x100ae042…, 0x367c42a6…, 0x3a5cc868… and 0xa4d65fd5… belong to one operator rests on the shared ABI and shared operator EOAs.
type_proposed: custody_vault_abi_transfer
rule_proposed: selector in {0x2da03409, 0x0dcd7a6c, 0x8568523a}, exactly one priced transfer entering or leaving the called contract, only transfer events
method_proposed: custody_flow
Operator 0xc08fb884… (nonce 218,459, bot_sender, very_high_nonce) calls sweep with the client address and the token; the vault pulls the approved balance. No event beyond the Transfer. The vault received $43.2M in 17 such sweeps in the day.

## ethereum 0x657573aa5f60a4f9457152fccecbe1d3e58a11972127fec35f22acd50ad095df
mechanism: custody vault payout: 27,857,717.28 USDC from vault 0x100ae042… to sibling vault 0x367c42a6… under a signed instruction (deadline 0x6aa45fd9, nonce 0x4650)
confidence: high
unverified: as above.
type_proposed: custody_vault_abi_transfer
The same operator, 11 nonces later, calls payout(to, amount, token, deadline, nonce); the deadline is a unix time about 51 days ahead (approx) and the nonce a counter, the shape of an off-chain-signed withdrawal instruction. Vault to vault, so an internal rebalance; 0x367c42a6… then pays 0xb5e4d2… $12M with the same selector.

## ethereum 0x98021d12fef21a332be6f984455b78562cae5fcae725b68cd6676fda896d898e
mechanism: vault 0x5392bd00… hands 9,846,533.00 USDC to the calling hot wallet 0x55fe002a… (nonce 1,679,595)
confidence: high
unverified: 0x55fe002a… as an exchange hot wallet is model memory; the day profile tags it many_sources and very_high_nonce. resolve: it is an EOA; the vault 0x5392bd00… is a contract.
type_proposed: custody_vault_abi_transfer (withdraw to caller)
The hot wallet refills itself from a vault contract: withdraw(token, amount) with the caller as recipient. Twelve transactions and $23.4M in the day through this vault; the hot wallet's own day net is what the exchange types measure.

## ethereum 0xb61db8643fa8bc3b41bf5761a4d6d4cab50b2e764acc588b645756d193c36328
mechanism: the same sweep ABI on vault 0xa4d65fd5…: 70,000.70 USDT pulled from a client address
confidence: high
type_proposed: custody_vault_abi_transfer
Operator 0xcc2bc4f5… (nonce 108,823) at a 2.75 gwei tip; 39 sweeps and $1.2M in the day on this vault.

## ethereum 0x0935211328a440f049f880bc68b1ae4b124f9f4397635d5c1cabaadade2b69b5
mechanism: 10,000,000.01 USDS repaid on the Aave-v3-fork pool 0xc13e21b6… with repayWithPermit
confidence: high
unverified: the pool as SparkLend is model memory; the event shapes are Aave v3's (Repay, ReserveDataUpdated, scaled debt Burn).
type_proposed: aave_fork_lending_op
rule_proposed: Aave-shaped pool events from an emitter other than the Aave core pool, no swap, no flash loan
method_proposed: lending
The borrower 0xb99a2c… sends USDS to the spToken contract 0xc02ab1…; nine such repayments in the day sum to $33.3M. Selector 0xee3e210b is repayWithPermit, so the user signed the allowance off-chain and paid one transaction.

## ethereum 0xed6b0b73bca195fdea578973cbf23c66cb639a1bee8f672c71d075ae9a786ead
mechanism: 32,694,693.83 USD of cbBTC supplied as collateral on the same fork pool
confidence: high
type_proposed: aave_fork_lending_op
supply() with ReserveUsedAsCollateralEnabled: the position is new for this reserve. Five cbBTC supplies in the day, $40.0M.

## ethereum 0x7025f9ba1dbfa8ecdb945661ba9397bc71a5f885cc69f8d6393c11004d65dd64
mechanism: 15,000,000.00 USDS borrowed on the fork pool
confidence: high
type_proposed: aave_fork_lending_op
borrow() mints variable debt to the borrower and pays USDS from the spToken contract; 21 borrows, $40.6M in the day. Read with the cbBTC and wstETH supplies, the pool is being used to borrow USDS against BTC and ETH collateral at eight-figure size.

## ethereum 0xa05d548304eb47de4314bf4812f4961c93f51402547bbc53626b9f04ceba9320
mechanism: wstETH worth 18,319,758.88 USD withdrawn from the fork pool
confidence: high
type_proposed: aave_fork_lending_op
withdraw() burns the scaled aToken and returns wstETH; six withdrawals, $66.8M.

## ethereum 0x985b3f156b073026d8f2afcdb8ee430e98d4239a79be428118120b76c924fd7b
mechanism: wstETH worth 18,625,088.20 USD supplied to the fork pool
confidence: high
type_proposed: aave_fork_lending_op
The supply half of a rotation: the same size class as the withdrawal above, a few hours apart, consistent with a position being moved or re-collateralised.

## ethereum 0x434ee6264b59a0dfe53ce517f0132eb61eadc700f3267bf35f512f22500df85f
mechanism: 10,003,810.42 USDS repaid with repay()
confidence: high
type_proposed: aave_fork_lending_op
Nine repays through selector 0x573ade81, $39.1M.

## ethereum 0x5cade5c4bf71de94d05c4baf4a9213270f32208ddc23e7c3ef7690cf09fa963c
mechanism: relayed payment batch with 32-byte references: 500,095.41 USDC from 0x977e5d… and 357.00 USDC from 0x68cf00… to 0xd15e62…, each followed by a record event from the contract
confidence: high
unverified: the service behind 0xec000064…; the references are opaque.
type_proposed: relayed_payment_recorded
rule_proposed: only transfer events plus custom events from the called contract; every priced leg is third party to third party
method_proposed: custody_flow
The sender 0xfac9a7b3… (bot_sender) owns none of the funds; the contract moves approved balances and emits (recipient, reference) per transfer. Fifty-six batches from two operators, $6.7M in the day: a payment rail settling instructions on approved balances, or an exchange paying withdrawals from customer sub-accounts.

## ethereum 0xef15784a397fb94bb50e9078a45fbe15c3e2dfc20f131491ce32c4249fac9943
mechanism: 100 ETH deposited into 0xd90e2f92… with a 32-byte recipient and a sequenced message (counter 48,280) from 0xa160cd…
confidence: medium
unverified: which chain or service the 32-byte recipient belongs to; the counter-and-timestamp event is the shape of a bridge message queue.
type_proposed: contract_deposit_recorded
rule_proposed: value or tokens enter the called contract only, a custom event is emitted, no swap
method_proposed: custody_flow
Sender nonce 11, tip 3 gwei. Seventy-four deposits of round ETH amounts from eight senders, $13.1M, all into this contract: a bridge-like deposit whose destination is off Ethereum. The generic type records the deposit; the protocol is not identified.

## ethereum 0xc5bb5b7625dcf10082435ea1c39aa2a9c12ea48cf52ea41a41dada30fd2c0918
mechanism: resolver-executed fill: 0x21cb49… pays 14,341.10 USDT through 0x77778576… and 0xe01ecf… delivers 157,602.94 1INCH (unpriced), with settlement events from 0x1111113ccf… per account and token
confidence: medium
unverified: 0x1111113ccf… and 0x77778576… as parts of 1inch's current fill infrastructure is model memory from the address prefix; the 1INCH token address 0x111111111117dc0aa78b770fa6a738034120c302 is model memory.
type_proposed: trade_against_unpriced_token
rule_proposed: no registered swap event, no flash loan; a net payer of a priced asset receives an unpriced token, or a net receiver of a priced asset sends one
method_proposed: swap (pairs show the priced side only)
The tx sender 0xf4d02174… (bot_sender) is a resolver; the taker's USDT reaches the maker net of 0.035852 USDT sent to 0x8063d4… as a fee, and the maker's 1INCH goes to the contract and on to the taker in the later logs. Implied price about 0.091 USDT per 1INCH (approx). 129 such fills through 0x77778576… in the day from two resolvers, all USDT; the registry now types them but cannot value the token side.

## ethereum 0x655eb229bb8dbc8c3e62be5f6c53b617351698ca5d7ac3853da6ab8e284aa55d
mechanism: the same venue through entry contract 0xd82461784e…: 14,782.01 USDT in and 14,781.24 out with a 0.76 USDT fee
confidence: medium
type_proposed: trade_against_unpriced_token
Fifty transactions and $716k; the dust ETH value (8.3e-16) and the 1inch-style events match the previous entry.

## ethereum 0xf7b24a4222de88b7b3db1451edcf81c64411e16ead580a8ae901d94a70477ce2
mechanism: custody vault 0xef4fb2… pays 532,139.10 USDC to settlement hub 0x555ce2… after eight approvers record the operation id in registry 0x949b3b…
confidence: medium
unverified: the operator; that 0x555ce2…, 0x33b41fe1… and 0x5c7bcd6e… are one system rests on shared counterparties and a shared 0x1237 constant in calldata and events.
type_proposed: contract_payout_by_operator (the vault is not the called contract, so the generic rule for tokens leaving the called contract does not fire; typed by operator_transfer_recorded)
The calldata names the vault and an operation id; registry 0x949b3b… emits one approval event per approver (eight) and an execution event; the vault emits seven records (id, recipient, amount, token). Multi-approver custody releasing inventory to a settlement hub, 44 times in the day for $2.9M.

## ethereum 0xc39ab8b0519b65a59bfe89d7057b3708b0f5092ba12289a9af2eaa9359574015
mechanism: payout processor: 0xf5e10380… pays 364,135.25 USDT to a fresh address with a record (id, account number 263,449, beneficiary) from 0xcd351d36…
confidence: high
unverified: the operator.
type_proposed: contract_payout_by_operator
rule_proposed: every priced leg leaves the called contract to addresses other than the sender, only transfer events
method_proposed: custody_flow
112 payouts from 37 operator EOAs, $7.6M, USDC and USDT, recipients mostly fresh: the withdrawal side of a custodial service.

## ethereum 0x15697afb421d8d980bdabdd7883b94e62bc0ad8aeb9369a747b12b973f152e60
mechanism: 400 ETH deposited into cross-chain swap service 0xc1d13492… with the memo USDT(TRON)|<TRON address>|0.05|bridgers|
confidence: high
unverified: "bridgers" as the SWFT/Bridgers aggregator is model memory; the memo format is read from calldata.
type_proposed: service_deposit_with_memo
rule_proposed: calldata holds a printable memo of 8+ characters, value or tokens enter the called contract, the contract emits its own event
method_proposed: custody_flow
A fresh wallet (nonce 2) sends 400 ETH ($981,873) with an order string naming the destination token, chain and address and a 0.05 fee parameter; the contract records it. The same contract pays out USDC and USDT by operator calls (0x80651b75…) and receives deposits (0xb32af712…): 45 native deposits ($2.8M), 46 token deposits ($2.3M) and 89 payouts ($14.9M) in the day. This is the mechanism the pilot could not see in two minutes: a swap service that settles off-chain, so its Ethereum legs are one-sided by design.

## ethereum 0x80651b7515809c6e0d4a22631352aaf6f8ff51f9941829b38074dfa1298fc584
mechanism: payout side of the same service: 497,874.64 USDC from 0xc1d13492… to a fresh address, event with token and amount
confidence: high
type_proposed: contract_payout_by_operator
Operator 0x…(bot_sender, very_high_nonce); the recipient is fresh: a user receiving on Ethereum what they sent on another chain.

## ethereum 0xb32af7122ecb5aa5d0331785894cee8e0aa4cafcaeb5588ddacd827912e9c19c
mechanism: token deposit into the same service: 249,964.82 USDC from 0x94810f… with a deposit record
confidence: high
type_proposed: contract_deposit_recorded

## ethereum 0xbd1b8050ab0d63db8cfe994439038d9c461b09e893be8bc8a54e51bec123dc65
mechanism: exchange-scale hot wallet 0xf70da978… (nonce 4,782,114) sells 605,248.14 USDC through router 0xccc88a9d… and a 0x-Settler-style contract for 378,051.89 units of unregistered token 0xe3431676… plus a 226,996.63 USDC leg to 0x025a1375…
confidence: medium
unverified: 0x00000000000014aa… as a 0x Settler deployment and 0xb92fe925… as its allowance router are inferred from the anonymous log and the approve-encoded event. resolve: the token 0xe3431676… reports symbol USDG, name Global Dollar, 6 decimals; the settler is an 18,797-byte contract; the hot wallet is an EOA.
type_proposed: trade_against_unpriced_token
The hot wallet's USDC nets −605,162.98; the settler nets +378,166.35 USDC and pays the token; the residual USDC goes to 0x025a1375…, which may be a second fill or a fee. 81 transactions and $11.9M through this router from the same wallet in the day: an exchange converting USDC inventory into another dollar-like token.

## ethereum 0x36c56412ab267789f0a21499cdf9e93cd7b04c24d8ef12cf4a76ab05cffc805d
mechanism: Permit2 batch transferFrom: 205,578.05 USDT swept from ten addresses into 0xe4f9b0a8…
confidence: high
unverified: nothing beyond Permit2 itself, whose address is documented.
type_proposed: permit2_operator_transfer
rule_proposed: destination is the Permit2 contract, selector transferFrom single or batch, only transfer events
method_proposed: custody_flow
Operator 0xa99b5736… (nonce 20,723) consolidates customer balances that approved Permit2; 34 sweeps, $1.2M in the day.

## ethereum 0x717031756cf5facb0be14412d0c1efc1bc1bf3c8ebfbf01bc7c4d89343363936
mechanism: sUSDe cooldown claim: unstake(receiver) releases 10,033,001.47 USDe from silo 0x7fc7c91d… to 0xf078969e…
confidence: high
unverified: the silo address is read from the transfer; sUSDe's unstake semantics are model memory consistent with the single USDe leg.
type_proposed: susde_unstake_claim
rule_proposed: destination is the sUSDe contract, selector 0xf2888dbb, a USDe leg present
method_proposed: generic
Twenty-four claims, $17.9M in the day; the shares were burned when the cooldown started, so the registry's vault_withdraw rule (ERC-4626 Withdraw event) never sees them.

## ethereum 0xcb17d7ee45df09406014432b9629621720bf1d6294b0913b30dff97900d875b4
mechanism: delegated EOA 0x63d55efd… calling itself to settle USDT, USDC and WETH between four sub-accounts
confidence: high
unverified: nothing further. resolve: 0x63d55efd… holds a 23-byte designator delegating to 0x1c6841ea….
type_proposed: delegated_account_self_call
rule_proposed: destination equals sender and at least one log
method_proposed: custody_flow
An EOA can only emit logs when calling itself if it carries an EIP-7702 delegation. Nineteen self-calls, $317k of largest changes, moving inventory among 0x111f68…, 0x9303d9…, 0xe31950… and 0xe6f87b…: a market maker netting positions.

## ethereum 0x0584b19da7b81e8244927bf782fdaba66e538052f6ac59e42900304c9048acd0
mechanism: RFQ fill: taker 0x60dd465a… pays 100,000.00 USDT, maker 0x724c1cb2… pays 40.739555 WETH; settlement contract 0x8d90113a… records the order hash and delivers unwrapped ETH to the taker
confidence: high
unverified: the venue behind adapter 0x03f34be1… and settlement 0x8d90113a….
type_proposed: bilateral_exchange_settled
rule_proposed: no swap event, no flash loan, some address other than the destination nets negative in one priced asset and positive in another
method_proposed: swap
The maker is two-sided (−WETH, +USDT); the taker's ETH arrives by an internal transfer after the WETH Withdrawal, so the taker looks one-sided in receipts. 40.739555 WETH at the hourly feed is $99,939.69 against 100,004.39 USDT: a fill 6.5 basis points inside the feed (approx).

## ethereum 0xcdd5f68cb2a0eaf65baf2d5c591066f2464943ab2228f3915a869784eaf0f20a
mechanism: batched transferFrom sweep: 228,909.26 USDC from five customer addresses into 0xa9d1e08c… through 0x1bbe1be1…
confidence: high
type_proposed: operator_sweep_no_events
rule_proposed: only transfer events, every priced leg third party to a single recipient, no custom event
method_proposed: custody_flow
Operator 0xb56658… (nonce 43,890) at a flat 1 gwei; the helper emits nothing.

## ethereum 0xa1525f9f7f723ea7ecb93091d0dfd0ae10db04a41c08f67aaee214ea41c2a2e0
mechanism: the same sweep with one payer: 10,239,262.14 USDC from 0x7eb36c98… into 0xa9d1e08c… through 0x7dac2c6a…
confidence: high
type_proposed: operator_sweep_no_events
Eight transactions and $17.1M into the same collector by the same ABI (selector 0xb257b7af): the collector is a treasury being fed by customer sweeps.

## ethereum 0x62795aca91efec61eb7b22cf39cb2b95f544a9f39698714fd528eb3b3e5596f9
mechanism: 810.151862 ETH deposited through router 0xe68ab4f9…, wrapped, and forwarded to strategy 0xcca852bc…, which records totals; share token 0x94e7a5dc… records the credit to the depositor
confidence: medium
unverified: the product; the router also carries the observed Aster withdrawal topic in other transactions, so this may be Aster's ETH vault.
type_proposed: native_deposit_wrapped_forwarded
rule_proposed: top-level value, a WETH Deposit credited to the called contract and WETH legs leaving it, no swap
method_proposed: custody_flow
Sender nonce 299 deposits $1,996,222; 11 deposits, $2.5M through this router in the day.

## ethereum 0xb365042c1d62728a8fb7ceb05cc27493da37b0975ba3f5b65cb2d0c7709a7e5a
mechanism: 4,382,679.35 USDS staked into rewards contract 0x4e41488c… (Staked event plus a referral event)
confidence: medium
unverified: which Sky farm this is; StakingRewards-style events are generic.
type_proposed: staking_pool_stake
rule_proposed: Staked event and tokens entering the called contract, no swap
method_proposed: generic
Eight stakes ($14.9M) and 11 withdrawals ($12.3M) on this contract in the day.

## ethereum 0x124fd09b51d67724728b03174313724b6158e3c2d4f0c955dc45e0fdca4c9130
mechanism: exchange hot wallet 0x9642b2… paying five withdrawals (1,200,052.57 USDT the largest) through payout contract 0xfaf17849…, one record event per payment
confidence: high
unverified: the exchange.
type_proposed: sender_tokens_via_contract (fewer than five recipients per batch fall below batch_payout)
The hot wallet's own tokens move by transferFrom through the helper; 58 batches, $7.5M in the day.

## ethereum 0x373f6b4e54191f2751976143b6bb1b5ca554d2664756ed3523e08199c0b5259c
mechanism: forwarder sweep: 159,977.49 USDC from per-customer forwarder 0xd1b241… (which emits its own event) into hub 0xf4e147db…
confidence: high
type_proposed: forwarder_sweep
rule_proposed: every priced leg is paid by an address that emits a custom event in the same transaction and is neither the sender nor the destination
method_proposed: custody_flow
1,431 distinct forwarders emit this event in the day; 61 sweeps above the threshold, $1.6M, into a hub tagged many_sources.

## ethereum 0x536d093b77168769bbfd3fb482401d890a59b5ca59af5210d6db759a6da148ba
mechanism: liquidity wallet 0x07ae85… (nonce 748,430) pays 121,691.56 USD of WETH into 0x5c7bcd6e…, which unwraps it and pays ETH to the order's recipient; the event names source and destination tokens and both amounts
confidence: medium
unverified: the service; the pilot listed 0x07ae85… among hot-wallet candidates.
type_proposed: contract_unwrap_payout
rule_proposed: WETH legs into the called contract and a WETH Withdrawal by that contract, no swap
method_proposed: custody_flow
Forty-nine such fills in ETH ($1.7M) and 45 in USDC/USDT ($2.2M) through this contract in the day, all paid by two or three liquidity wallets: a cross-chain transfer service settling on Ethereum out of inventory.

## ethereum 0x107f8d0f8149744d1dcac349e59df45c3476bace47b109bf2447d29fffa8bb7e
mechanism: the token variant: 172,901.87 USDC from 0x07ae85… to 0x036189…, recorded by 0x5c7bcd6e…
confidence: medium
type_proposed: contract_payout_by_operator
The recipient carries hot_wallet and many_sources tags: the transfer lands in another exchange-like wallet, so this is inventory moving between two exchange-connected systems, not a retail withdrawal.

## ethereum 0xdbaf97b0ec87c6bafcae3d1cb796ba0f593361785a5918c94054742aefd3be49
mechanism: hot wallet 0x5f65f7b6…'s vault contract pays 1,006,797.66 USDT to a customer address
confidence: high
type_proposed: contract_payout_by_operator
The sender is tagged hot_wallet and very_high_nonce and calls its own contract 100 times in the day ($8.4M): an exchange paying withdrawals from a contract-held balance instead of the EOA.

## ethereum 0x56235fb1b9fd7482d16034c4357af0a5ff6376e9ed2cfc6dd2c966b84dc379f4
mechanism: executor contract 0xa5e1a817… moves 2,242,606.65 USDC from 0xe3a25228… to 0xbd22c4c7… and logs (0, 1)
confidence: medium
unverified: the executor's owner.
type_proposed: relayed_payment_recorded
An execute(bytes,bytes[]) call with one instruction; the asset owner approved the executor. Four transactions, $9.0M.

## ethereum 0x21be55c51f1f149976b220fe9605265c9e25bda6b22d84faacda6f2e08e2577c
mechanism: payment router 0x8d04cc7e…: 53,430.64 USDT from payer 0x750dcd… splits into 53,035.56 to merchant 0xc7b9a5… and 395.08 to fee collector 0x8443e8… (0.74 percent, approx), with invoice events from registry 0xbccfef37…
confidence: high
unverified: the payment processor.
type_proposed: payment_router_fee_split
rule_proposed: one asset enters the called contract and leaves it to two or more recipients within 1 percent; the smallest share is at most 10 percent
method_proposed: fee_split
The transaction sender 0x50bf9347… (nonce 29,800) is a relayer, not the payer: the payer approved the router and the processor executes. Thirty-seven payments, $8.3M through this router in the day.

## type trade_against_unpriced_token
Audit: the hash-sampled occurrence (0x248d3c15…) was a deposit of WETH into 0xbad1b632… that minted an unpriced receipt token, not a trade. Round 4 excludes unpriced legs minted from or burned to the zero address and adds receipt_token_minted_deposit and receipt_token_burned_withdrawal ahead of this type; the type fell from 219 to 16 occurrences.

## type aave_fork_lending_op
Audit: the hash-sampled occurrence (0xfe63eda3…) was a 1,167-byte contract 0x4c21b757… paying USDC with a four-argument Withdraw event, which is the same ABI shape as Aave's Withdraw. Round 4 requires ReserveDataUpdated in the same transaction; the type fell from 86 to 83 occurrences ($273M), all at 0xc13e21b6…, and the three 0x4c21b757… payouts ($7.2M) are back in the residue.

## type bilateral_exchange_settled
Audit: the hash-sampled occurrence (0x9ca780f5…) was an aggregator swap through 0x6131b5fa… that records a Swapped event; the two-sided party was an intermediate contract. Round 4 adds dex_swap_aggregator_event ahead of it (118 transactions); the type fell from 802 to 668 occurrences.

## type receipt_token_minted_deposit
The audit sample of stablecoin_mint (0xe671775b…) and the residue head at 0x4f95c5ba… (0x9bc7d36e…) both show a priced deposit paired with a mint of a token the registry does not know; resolve named the second one USTB (Invesco short-duration US government fund token, 6 decimals): 620,502.52 USDC bought 55,393.83 USTB, about $11.20 per share (approx). Receipt tokens are claims, not counterparties; the type ranks after the lending rules because aTokens are minted receipts too.

## type unregistered_token_mint_burn
resolve named the tokens: 0x1abaea1f… is EURC (Euro Coin, 6 decimals; $3.4M minted and $3.6M burned in the day) and 0x73e0c0d4… is kBTC (Kraken Wrapped Bitcoin, 8 decimals; $3.2M minted in two transactions). Issuance of unregistered tokens is visible only because their pools gave an implied price; EURC needs a EUR feed to be valued properly.

## type exchange_deposit
The largest sink, 0xa9d1e08c…, is a 6,889-byte contract that received $964M in 852 deposits and paid 729 batch payouts in the day: one contract for both directions of an exchange's customer flow. The type's rule (recipient tagged hot_wallet or many_sources) does not distinguish an EOA hot wallet from such a contract; the audit sample (0xe711719f…) deposited into 0xee7ae85f…, also a contract with many sources.

## ethereum 0x543b8c6b6c919ca86889e455114d6ebd87e2c8549cfca7f6cbd4829db0cf807e
mechanism: 1,167-byte contract 0x4c21b757… pays 4,207,339.95 USDC to 0x774ae279… and emits an Aave-shaped four-argument Withdraw event
confidence: medium
unverified: the contract's purpose; 0x774ae279… also receives USDC from tokenized-fund wallets (0x9bc7d36e…), so it may be a fund-subscription hub.
type_proposed: contract_payout_by_operator once record-event families with Aave shapes are allowed in transfer-only rules (left in the residue by round 4 on purpose)
Three transactions, $7.2M; the audit of aave_fork_lending_op caught this shape.

## ethereum 0x8504dbcc6e925140f38876dc69ba3aef130426440084c8bdc31abd540789fd9b
mechanism: 4,000,000.00 AUSD deposited into converter 0xa19d9d64…, which also paid 4,000,000.00 USDC to another user (0x3de4c0e5…): a two-asset par facility
confidence: medium
unverified: the operator of the converter; AUSD's identity comes from resolve (symbol AUSD, 6 decimals).
type_proposed: a par-conversion type keyed on the converter, once its Sync(uint256,uint256) and withdraw events are registered
Three deposits ($10.0M) and one withdrawal ($4.0M) in the day; the contract is 1,171 bytes.

## ethereum 0x06b4047508a4274305b7bc26e5270fb2a0c858dc5a2bd47ce1a898b974ae7c02
mechanism: 24.877885 ETH from a fresh wallet into 0x0439e60f…, a Safe-like contract (SafeReceived) that forwards the order to the cross-chain swap service 0xc1d13492… through aggregator 0x9a47f328…
confidence: medium
unverified: the aggregator; 0x9a47f328… emits its two events about 8,400 times a day.
type_proposed: service_deposit_with_memo would catch it if the memo were in the outer calldata; here the order string sits inside the aggregator's inner call
Five such deposits ($195k) and seven with a Relay-style deposit event ($91k).

## ethereum 0xcbb98d3f046c46b84e263402077b5a2ca6adec5bea276649f3791d8a7d0a856d
mechanism: operator 0xa4c542fc… (nonce 39,773) moves 110,772.07 USDT of 0x1ce24ad9…'s approved balance to four recipients (109,999.50 to the main one) through 0x9188db28…, no events
confidence: high
type_proposed: extend operator_sweep_no_events to one payer and several recipients (feedback 9)
Four transactions, $248k.

## ethereum 0x2c271b08d702d1fb098eb0438adca4e65137e7c02c98b0fa0e5e63113b426145
mechanism: 20,969.96 LINK ($248,522) withdrawn from 0xa60b5146… to the caller with a Withdraw(address,uint256) event
confidence: medium
unverified: the contract (a staking or vault contract for LINK).
type_proposed: custody_withdrawal_to_operator once the two-argument Withdraw family is allowed in transfer-only rules (feedback 9)

## ethereum 0xde017d5628fc4fb92055d6242e12c2d510f73143b8a607131cd3da79e6f12fcf
mechanism: sUSDe cooldown claim routed into a vault: 66,244.17 USDe leaves the silo to 0xe620afb6… and on to 0xceda2d85… in one call
confidence: high
type_proposed: susde_unstake_claim generalised to claims made through a router (the receiver is a contract, the destination is not sUSDe)
Nine transactions, $354k.

## ethereum 0x3de4c0e52ca82b938ed0437b32849f269ec176e814a7a8d32c60ca1ecddcdd8d
mechanism: 4,000,000.00 USDC withdrawn from the AUSD/USDC converter 0xa19d9d64… by 0xf3c1cc8e…, with a Sync(uint256,uint256) reserve update and a withdraw record
confidence: medium
unverified: as 0x8504dbcc….
type_proposed: par conversion keyed on the converter (feedback 1)

## ethereum 0xff71496ba20a90006bb61e4217028dbaab37564d8ea359b77d528b2e9af19af7
mechanism: audit of contract_deposit_recorded: 298 ETH ($727,322) from hot wallet 0xdfd5293d… into 0xd59d7a96…, which emits Deposited(address,uint256,bytes)
confidence: medium
unverified: 0xdfd5293d… as a Binance hot wallet is model memory (it was a hot-wallet candidate in the pilot); the deposit contract's product (staking or bridge) is not identified.
The rule holds: value enters the called contract, nothing leaves, the contract records it. An exchange committing ETH to a contract-based product.

## ethereum 0x9ca780f56dfb1f8e40775e0b026523faae30b2d8b9e9510e5356fa5ec3e25c90
mechanism: audit of bilateral_exchange_settled (now dex_swap_aggregator_event): 500,016.94 USDT sold through aggregator router 0x6131b5fa…, which records Swapped and Exchange events; the two-sided party was an intermediate contract
confidence: high
unverified: 0x6131b5fa… as KyberSwap's MetaAggregationRouterV2 is model memory.
This sample is why round 4 added the aggregator-event type ahead of the bilateral rule.

## ethereum 0xef3dcf49afffc215ff3f29afd592cdce41699c53e77d92433dfe6a5ed1d24e9f
mechanism: audit of operator_transfer_recorded (now unregistered_token_mint_burn): 4,560,925.55 USDG minted from the zero address to 0x264b… by a call on the token contract itself
confidence: high
unverified: the issuer; resolve reports symbol USDG and name Global Dollar with 6 decimals.
Issuance of a dollar token the registry did not know; it was valued through the token's own pools (724 swaps, $11.6M).

## ethereum 0xf8d22d46c0029b9d5930b722666b19a7c30815014991ff8623aba2beb6d0d480
mechanism: audit of intent_or_rfq_fill: a UniswapX fill in which the filler pays 30,001.32 USDT and sources 29,756.99 USD of PEPE at the implied price
confidence: high
The unpriced side is valued here because PEPE had 730 swaps against priced assets in the day; the rule and the price feed agree.

## ethereum 0xd2f3855faabe1727d2976f3fd159f45fc151c857a7632a9bb1fce6a9245d454e
mechanism: audit of restaking_or_lst_other: a bot (very_high_nonce) wraps ETH, moves it through an Aave reserve and mints or burns an LST inside one atomic strategy
confidence: medium
type_proposed: exclude bot_sender and very_high_nonce senders from restaking_or_lst_other, or rank the atomic-strategy rules before it
The label misdescribes this occurrence: the LST mint is a leg of an arbitrage, not a staking decision. Sixteen occurrences, $1.3M, so the correction is cheap and deferred to the next run.

## ethereum 0xe4fde5b6fac329943c7b0274cd982105ddb14b03c0a2244f08a2f815e146428b
mechanism: audit of sandwich_attack: bot EOA 0x3ee92cd0… through 0x9205a569… sells WBTC for WETH ($12,602.65) around a stranger's swap in the same pool and block
confidence: medium
unverified: profit; the observed net of this bot over its 32 legs is $462, so the payoff is either in the unwrapped ETH or paid to the builder.
The scan's bracketing rule holds; the economics are outside receipts.

## ethereum 0x7b4ad5b5a1bccb5e91721e85ad3e3a34a2f39e4575384c961f997ae5c4022d10
mechanism: audit of dex_swap_user: hot wallet 0xf70da978… sells 100,024.22 USDC for USDG through router 0xccc88a9d… with a Uniswap v4 swap
confidence: high
The same wallet's larger conversions went through the 0x-Settler path with no swap event (0xbd1b8050…); together they are 154 swaps and $55M of USDC into USDG in the day.

## ethereum 0x248d3c15c9d9e53b089a593c57f1184c7b222608b6686d851cad7495d412a14c
mechanism: audit of trade_against_unpriced_token (now receipt_token_minted_deposit): 244,464.27 USD of WETH deposited into 0xbad1b632…, which emits Deposit(address,uint256,uint256) and mints a receipt token
confidence: high
This sample is why round 4 separated minted receipts from traded tokens.

## ethereum 0x482cd9f853b123f6652a7e1e4f5b140b2ff2107fecaa4ff8324c678a0ad68b17
mechanism: audit of stablecoin_burn: 349,948.76 USDC burned through 0x77777777dcc4…, which also takes a 2.00 USDC fee; a cross-chain departure that burns rather than locks
confidence: medium
unverified: the burner; the CCTP DepositForBurn family did not match, so either the signature differs from the registered one or the burner is another minter-authorised bridge.
The type is right about supply mechanics (USDC left circulation on Ethereum) and silent about where it reappears.

## ethereum 0xd13f9b341340d5efd6d2c76452c037545c2fc3498778c915c52071479d0cde13
mechanism: audit of relayed_payment_recorded: liquidity wallet 0xfd03abca… pays 84,880.29 USD of WETH into 0x5c7bcd6e… through adapter 0x9ccc2f3e…, and 0x5c7bcd6e… unwraps it for the beneficiary
confidence: medium
type_proposed: contract_unwrap_payout should also accept an unwrap by a contract that is not the destination when it received the WETH in the same transaction (precedence quirk; the mechanism is the cross-chain fill of 0x536d093b…)

## ethereum 0xe671775b2eae2fe77f915075d7fab86a57bbc6ec80ecd8332d3219c733189eb6
mechanism: audit of stablecoin_mint: 19,997.19 USDC minted from the zero address to 0xd15e62… and forwarded, by a bot calling minter contract 0xec2c96e7…: a bridge arrival that mints
confidence: medium
unverified: the bridge; nine unregistered events accompany the mint.
stablecoin_mint counts every USDC mint, so the $542M of USDC issuance in the day mixes Circle's own mints with bridge arrivals through authorised minters; bridge_in needs the bridge's event to separate them.

## ethereum 0xcff5fec9aa6638459f1a7492d86cb753749de42628e18755dce9329c1723204f
mechanism: audit of exchange_withdrawal: hot wallet 0xa02f… (very_high_nonce) sends 16.2407 ETH to 0x4b84f19b…, itself a bot_sender that later pays 13-ETH calls into the silent contract 0x09c30cdc…
confidence: medium
A withdrawal that funds an automated wallet rather than a customer; the tags show the chain but not its purpose.

## ethereum 0xa80ea988a3d77a607a9ac03c1af3c01d79df495805f6caee40502ac03e222ea5
mechanism: audit of flash_loan_arbitrage: 110,910.06 USDC borrowed from Morpho, traded through a Fluid pool and USDT, repaid; observed net near zero
confidence: high
The event-supported lend-repay pairing holds and the observed net says nothing about the bot's profit, as the method documents.
