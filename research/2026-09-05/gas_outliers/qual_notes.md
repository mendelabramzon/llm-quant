# Qualitative notes for the gas-outlier packets

Written by the LLM after reading `packets.json`, `context.json`, `stats.json`, and per-transaction `show` output. Each entry is keyed by transaction hash. Exact figures quoted here are copied from decoded events and packet facts; anything derived (differences, ratios, multiples) is approximate and marked as such. Contract identities that rest on model memory rather than an onchain check are listed under `unverified`.

## synthesis
Three kinds of transaction produce gas outliers in this window, and only one of them signals urgency.

Configuration artifacts. Most gas-limit outliers are round numbers chosen by tooling: 2^24 on Base (#10, #11, #13), 32,000,000 on Arbitrum and Polygon (#17, #19, #33, #36, #37), 15,000,000 on Optimism (#23 to #25), 16,698,639 for an Ethereum bot fleet (#4, #6, #7) and 100,001,242 for a Chainlink node (#20). Limit-to-used ratios run from 1.3 to 803. Many tip outliers are flat presets rather than bids: exactly 2 gwei for eight repeat senders on Ethereum, 1.0 gwei on Base (#14, #15, #16), 0.1001 gwei on Optimism (#27 to #29), 5,000 gwei on Polygon (#32). A sender whose tip never varies is not expressing urgency, whatever the multiple of the base fee.

Ordering competition. Where the tip varies within a sender, or a transaction sits at the top of the block, the mechanism is a race. Two Ethereum top-of-block transactions react to the trade immediately before them: #1 backruns a FOLD fill, and #3 pays the builder 0.002975 ETH behind a FOLD purchase, with the payment recipient equal to the block's miner. A Base bot pays 255 times the base fee for one opportunity and a median 0.0047 gwei otherwise (#12). A Polygon proposer pays 88,175 gwei per gas to be first on a UMA resolution request (#35), and a 7702 relayer escalates to 10,940 gwei inside one block (#34). On Polygon the validator sorts by gas price, so both extreme tips land at index 0; on Ethereum the builders placed the two high-tip transactions at index 1, directly behind the transaction they react to.

Automated fleets. The same contract is called by rotating EOAs: three wallets for the Ethereum arbitrage fleet, three for the Optimism per-block loop, four GMX keepers, seven callers of the Base per-id contract, 70 relayer EOAs for the Polymarket hub. Sender counts overstate actors. One Optimism keeper alone (#30) sent 107 transactions in the window, about 7 percent of the chain's user transactions.

The priority-fee metric carries no information on Arbitrum, where every transaction pays the base fee and the scan skipped the metric; little on OP Stack chains, where the base fee is around a thousand wei and tips run from 1 wei to 0.1 gwei; and a strong ordering signal on Polygon and Ethereum. For the flagged transactions the L1 data component of OP Stack fees was under 1 percent of the total; it matters for the median transaction, not for these outliers. Gas-limit ranking surfaced the two mechanisms that fee ranking would never find: the near-free Optimism compute loop (#23) and the Chainlink 100M-limit report (#20).

Hypotheses for the quant step, each falsifiable on a longer sample. (1) On Ethereum, transactions with a tip above the chain P99 at index 1 or 2 share a token with the index-0 transaction far more often than random transactions do, and the effect disappears for high-tip transactions beyond index 10. (2) Senders with zero tip variance over five or more transactions show no better placement and no lower failure rate than median-tip senders, so they should be excluded from any urgency feature. (3) The Optimism per-block loop runs continuously and consumes a stable share of block gas, so utilization on that chain overstates demand by that share.

## feedback
1. Count WETH Deposit and Withdrawal events as native-to-WETH conversions in net-flow accounting. The ERC-20-only flow showed zero WETH change for #4, #6 and #7 and hid the retained arbitrage profit.
2. Add per-sender tip variance, and the number of distinct senders calling the same (destination, selector) pair with near-identical gas usage. Both separate configuration and fleets from urgency before a packet reaches the LLM.
3. Attach block context to each packet: builder or coinbase, and a one-line summary of the index-0 transaction. Both Ethereum top-of-block investigations needed them and had to request them separately.
4. For type-4 transactions include the authorization list (delegate target, authority nonce) and the count of same-sender type-4 transactions in the block; recover the authority address from the signature.
5. Register the event signatures recognised from memory in this pass so the next iteration decodes them deterministically: Balancer V2 FlashLoan, Velodrome-style Swap, Fees and Sync, LayerZero V2 PacketSent and OFTSent, GMX V2 EventLog1 and EventLog2, Chainlink OCR2 Transmitted, UMA Optimistic Oracle ProposePrice, GSN-style TransactionRelayed, Gnosis CTF PositionSplit, ERC-777 Sent. Each needs an address or source check before promotion to the mechanism registry.
6. Next bounded queries: a transaction trace for #36 (21M gas, no visible effect); code or label lookup for the Optimism keeper system (#26, #30, #31) and the Base per-id contract (#10); a check over several hours whether the Optimism loop (#23) is continuous.
7. Uniswap V4 swaps identify pools only by id. Index PoolManager Initialize events so a pool id resolves to its two currencies and fee tier; without that, three of the Ethereum packets needed manual reading of transfer pairs.

## ethereum 0x53c5a374bc2fcc7cd7a3b2403d8906cc69008a1bb833ff08067838a5b198c77e
mechanism: top-of-block backrun of a FOLD trade on Uniswap V4
confidence: medium
unverified: operator identity; the causal link to the index-0 trade is inferred from adjacency and the shared token, not from a bundle record.
The bot contract swapped 300 USDC for 5,733.87 FOLD on the Uniswap V4 PoolManager (pool fee field 6883, a dynamic-fee pool) and delivered the FOLD to a third address encoded in calldata. It sits at index 1 with an 18.27 gwei tip against a 0.07 gwei base fee, immediately behind index 0, a 1inch-routed trade that moved FOLD, USDT and USDC through a V4 pool and the V3 USDC/USDT pool. The tip buys the slot behind that trade: the bot paid 0.00257 ETH to capture the price impact the fill left behind. Sender nonce 800,210 marks a long-running bot. FOLD appears again two blocks later in #3.

## ethereum 0xbb85f0f3ec69e5445673408b41bb7927e15aedecc8151ba60da3509b8e204b8b
mechanism: transaction cancellation or nonce management by an EOA
confidence: medium
unverified: whether a pending transaction with the same nonce existed; only mempool data would show it.
A zero-value transfer from an EOA to itself, 21,000 gas, with a 36.43 gwei tip while the base fee is 0.07 gwei. That is the shape of cancel-and-replace: a wallet resubmits nonce N as an empty self-transfer at a higher price to displace a stuck transaction. The same EOA repeats it five blocks later with the next nonce (#8), so two consecutive pending transactions were replaced. Despite the highest tip on the chain in this window it landed at position 204 of 230: builders do not order by tip alone. Nonce 61,773 says an active account, not a high-frequency bot.

## ethereum 0x53a64ed68331561b9097c8243df85af6922f40fc4a1f749c4920a6f9fad4ee6a
mechanism: explicit payment to the block builder behind a FOLD purchase
confidence: high
unverified: which party assembled the bundle; whether the index-0 buyer and this payer are the same operator.
The 985-byte destination contract forwards the transaction value to an address and logs (recipient, amount). The logged recipient 0x9522…afe5 equals the miner field of block 25,910,249, whose extraData reads beaverbuild.org, so the 0.002975 ETH went to the builder that produced the block. Index 0 of the same block is a 1.235 ETH purchase of FOLD through two Uniswap V4 swaps at a 0.1 gwei tip. A buy followed at index 1 by a separate payment transaction with a 20 gwei tip is how sniper tooling secures top-of-block placement for a token purchase. With #1, two of the three highest Ethereum tips in the window are FOLD-related ordering competition.

## ethereum 0x2af8ff2c02d0479482c6314524f4447ead63c53a9b0c141c0ef6f7142816925c
mechanism: flash-loan arbitrage between two Uniswap V4 ELA pools
confidence: high
unverified: how the builder was compensated; there is no meaningful priority fee and no visible coinbase transfer.
Balancer V2 Vault lends 0.011505 WETH to the bot contract (FlashLoan event at the end). The bot unwraps it, buys 108.031 ELA in V4 pool 0xe5be… for 0.011505 of currency0, sells the same ELA in V4 pool 0x3708… for 0.020081 of currency0, wraps the proceeds and repays Balancer. The gross spread is about 0.0086 ETH before any builder payment, on a 0.000026 ETH fee. The 16,698,639 gas limit against 376,310 used is a fixed fleet setting: three different EOAs call this contract in the window with the same limit and the same 0.00016 gwei tip (#6, #7). The packet's ERC-20 net flow shows zero for WETH because the profit moved through WETH deposit and withdraw events, which the flow calculation does not count.

## ethereum 0x773374f66aea53100bc30a92c07ae53c5c6d1e6ee941685f6baf44b62c4ade41
mechanism: aggregator-routed purchase of uPEG with 0.2 ETH split across V3 and V4 pools
confidence: medium
unverified: which aggregator; the router emits a swap-record event signature that also appears on Base (#16) and is not in the decoder.
A low-activity account (nonce 553) sends 0.2 ETH to a router that wraps it and splits the order: legs through the WETH/USDT V3 pool, a V4 WETH/uPEG pool (fee 10000), a V3 uPEG/WETH pool and further legs in the remaining logs, with 0.1992 WETH forwarded per calldata and 0.0008 ETH retained as fee. The sender ends with +2.409 uPEG. A 2.5 gwei tip is about 38 times the base fee and, with 1.7 million gas for the route, makes this the largest fee on Ethereum in the window at 0.00435 ETH. The purchase moved the V4 uPEG pool to tick 25,021; two arbitrage transactions later in the same block (#6, #7) trade uPEG back across pools.

## ethereum 0xd620890c9ce91144a831b23deb3af3a7b4f7cd5499511caad2e8995ce39af50f
mechanism: flash-loan arbitrage across three Uniswap V4 uPEG pools in the block of the retail buy
confidence: high
unverified: builder compensation, as in #4.
Same fleet contract as #4 from a second EOA. Two Balancer flash loans (0.005948 and 0.001085 WETH): buy uPEG in pool 0x94af… (the pool #5 bought into, now at tick 25,017), sell it in pool 0xe051…; then buy in 0xe051… and sell in 0x5c8a…. Returned amounts exceed the loans by roughly 0.0001 and 0.00002 ETH. This is the mechanical response to the price impact of #5, landing at index 156 of the same block. Two unknown emitters (0x6bea…, 0x08a4…) log around each swap and look like a V4 hook and a per-sender accounting contract.

## ethereum 0x33212e50252603613a2b0b6ccbd0a926fdce45e865fc706bb1653a6eb710b8ad
mechanism: flash-loan triangular arbitrage uPEG to USDT to WETH in the block of the retail buy
confidence: high
unverified: builder compensation.
Third EOA of the same fleet, index 295 of the same block as #5 and #6. Balancer lends 0.017825 WETH; the bot buys 0.2152 uPEG in pool 0x94af… (tick now 25,006), sells it for 44.20 USDT in V4 pool 0xda43…, converts the USDT to 0.017986 WETH in V4 pool 0x2287… (fee 125) and repays. The spread is about 0.00016 ETH. Three fleet transactions across two blocks each retained under 0.01 ETH; the fleet's economics rest on volume and near-zero tips, not on individual trades.

## ethereum 0xf7c4dd2c481c40e7cc772384781af86dfbf3b017b5eaa31b52463e68b1b800bd
mechanism: transaction cancellation or nonce management, second of a pair
confidence: medium
unverified: as #2.
Identical shape to #2 with the next nonce (61,774), five blocks later, the same 36.43 gwei tip, landing at position 388 of 392. Two consecutive replacements one minute apart suggest a batch of pending transactions abandoned at once.

## ethereum 0x12802ed453d708a5145c909a8a44011daf89f8d0be7411236faedfee382849b9
mechanism: aggregator sale of 1,000 RAIL for ETH through a split route
confidence: medium
unverified: the destination 0x0000…2734 as the 0x AllowanceHolder and 0xd718…091f as its Settler are model memory; the exec(operator, token, amount, target, data) calldata layout matches that memory. The Curve TokenExchange identification of topic 0x8b3e96f2… is also from memory.
The sender moves 1,000 RAIL into a settlement contract, which splits it across four V2 pools (RAIL/DAI 75, RAIL/WETH 349.93 and 525.04, RAIL/renBTC 50.03), then converts the DAI leg through a stable pool and the renBTC leg through Curve-shaped TokenExchange events, unwrapping to ETH at the end (one WETHWithdrawal, and no ERC-20 arrives at the sender). The 2.0 gwei tip is the common flat preset on Ethereum in this window, paid exactly by eight repeat senders, so the fee rank comes from 958,506 gas for the route rather than urgency.

## base 0x9e5f7bd9211997b9ebcd99cc2c5b932d95d24ba3eb9e6342c022e207b594046b
mechanism: scheduled keeper calling a per-id function with a fixed 2^24 gas limit
confidence: low
unverified: protocol identity; none of the three event signatures is in the decoder.
The gas limit is exactly 16,777,216 (2^24), a client-library default, against about 253,000 used. The single uint256 argument (67,873 here; 67,832 and 67,872 in #11 and #13) indexes something, and the three logs record that id, the sender, a counter and a timestamp about 12 minutes ahead of the block, so each call opens or settles a timed round. The contract received 20 calls from 7 senders in the window without a failure, so several operators service it cooperatively. Nonce 132,369 and one call every few blocks say automation. Eleven transactions in the window share the 2^24 limit.

## base 0x49a7002c06db41e7b3ff150f76240162d9c269aeab1243a745282f1eea920995
mechanism: scheduled keeper, second call (see #10)
confidence: low
unverified: as #10.
Second call of the same keeper as #10, id 67,832, same limit, tip and event shape.

## base 0x3a3f6674bfdedd7402be76cfbd74957801fa88ef8df714b59933b847ef149ed4
mechanism: single-pool WETH to ZEN purchase by a bot with a price limit and a competitive tip
confidence: medium
unverified: the other leg of the trade (an off-chain venue or another transaction); the pool is an EIP-1167 clone of 0xec8e…5831, which by memory is the Aerodrome Slipstream pool implementation.
The 687-byte bot contract sells 1.875241 WETH for 637.94 ZEN in one concentrated-liquidity pool. Calldata carries the amount, a sqrtPrice limit close to the post-swap price, the pool address and a deadline about three minutes out. The 1.276 gwei tip is about 255 times the base fee and the highest on Base in the window, while the same sender's other 19 transactions in the window pay a median 0.0047 gwei. The bot bids high only for this opportunity, which is the behaviour of an arbitrageur competing for ordering, not a flat configuration.

## base 0xc1decf57896945066db1abcd1a05abd9c51b54d67d7c2ca7bf789ff42ebda5d9
mechanism: scheduled keeper, third call (see #10)
confidence: low
unverified: as #10.
Third call of the same keeper as #10, id 67,872.

## base 0xcf71a3d29148de2e33c360bacd568fdba1695d6c88ad56a8e40e3d0fd94f1986
mechanism: Aerodrome router swap USDC to WETH to DAG by a user with a flat 1 gwei tip
confidence: high
unverified: 0xcf77…4e43 as the Aerodrome Router is model memory; the swapExactTokensForTokens selector and the Fees, Sync and Swap event triplet on both pools match Velodrome-style pools. The tip's cause is inferred from the sender's other transaction.
201.97 USDC enters the USDC/WETH pool (0.6059 USDC fee to the pool fee contract), 0.0819 WETH moves to the WETH/DAG pool, and 28,543.27 DAG returns to the sender. The 1.0 gwei tip, about 200 times the base fee, at index 1 of the block looks like a wallet "fast" preset or a script; the account's only other transaction in the window (nonce 240) pays the same tip, so it is a setting rather than a bid for this trade.

## base 0xa0667c13a15017a2e3e6bd2b465c38d484c2f8067c3fc8a2db0e17717f1077cf
mechanism: batched stablecoin disbursement from a clone wallet with a hard-coded legacy gas price
confidence: high
unverified: operator identity; cNGN is the token's self-reported symbol.
A legacy (type 0) transaction at 1.01 gwei calls a batch-transfer function with parallel arrays; the clone wallet (EIP-1167 to 0xcbfe…11bd) sends 2,495.95 cNGN to one address and 4.05 cNGN to another, a payout plus a fee of about 0.16 percent. The effective tip is about 201 times the base fee because a legacy transaction has no separate tip field; a backend that fixed 1.01 gwei long ago overpays on every block. No urgency is involved.

## base 0xefb4cb5c399251f32102f7ccbe5ad3f3b6d71e594f3f8308eee8c62ede132c5b
mechanism: buy ANYONE on Aerodrome and bridge it to Ethereum through LayerZero OFT in one transaction
confidence: high
unverified: the WETH source 0x15b1…d013 (no flash-loan event, so probably the bot's own vault); that a matching sell occurs on Ethereum; the LayerZero EndpointV2 address and the PacketSent and OFTSent topics are model memory, and the destination id 30101 as Ethereum is from LayerZero's published endpoint table.
The bot receives 0.169860 WETH, swaps it in the Aerodrome WETH/ANYONE pool for 2,722.97 ANYONE, then burns 2,722.969364 ANYONE to the zero address while the LayerZero endpoint (0x1a44…728c) emits a PacketSent-shaped event and the token emits an OFTSent-shaped event whose data carries destination endpoint id 30101. The bot keeps only dust. This is cross-chain inventory movement: buy where cheap, sell on the destination chain. The 1.0 gwei tip at index 1 and the largest fee on Base (0.000621 ETH) buy priority for the buy leg; the same EOA's previous transaction one block earlier paid 0.001 gwei.

## arbitrum 0xde8d2a775dfcc2bf918321e8030d5e48f0516faff2491938b30ce4ff9728e32d
mechanism: automated keeper submitting batched operations with the 32M gas limit; identity unknown
confidence: low
unverified: everything beyond the mechanics; none of the four event signatures is in the decoder.
Six transactions from one EOA (nonce above 1.08 million) to a 1,201-byte contract in six blocks, all with a 32,000,000 limit, using 155,000 to 835,000 gas. Two other 1,201-byte contracts emit alongside it, so the target is one of a set of identical instances. The logged key 0x7ebb…6da0 followed by 0x000002ffffff embeds an address and looks like a pool or order identifier. On Arbitrum the gas limit also covers the L1 data component, so the round 32M is a keeper convention rather than an estimate.

## arbitrum 0x1b396c2cb0e8516853aa590cd0ddd9a906f6a7e186e7d5b908cdcbaca5af6a31
mechanism: GMX V2 keeper executing orders with Chainlink Data Streams price reports
confidence: high
unverified: contract identities are model memory: EventEmitter 0xc8ee…22fb, OrderVault 0x31ef…40d5, the EventLog1 and EventLog2 topics, and the 0x0003-prefixed feed ids on emitter 0x2237…fb83 as Data Streams report verifications.
A legacy transaction from a keeper (nonce 450,793) with a 31.9M gas limit. Three report-verification events keyed by 0x0003-prefixed feed ids come first, then three EventLog1 records carrying token addresses (WETH, USDC, a third market token), consistent with oracle price updates. A burst of EventLog1 and EventLog2 records keyed to account 0x947c…d2ad and order keys follows, and 147 USDC leaves the OrderVault to that account: an order executed with collateral or fee returned. Arbitrum charges no tip, so the fee rank is pure gas (3.43M).

## arbitrum 0x58b6cb0d71d2670293d188e252f82adbd0f426014fdd7a5c3e2fb1ee087f8140
mechanism: automated keeper, lighter payload (see #17)
confidence: low
unverified: as #17.
Same keeper as #17 with a lighter payload (159,453 gas); the limit-to-used ratio of about 200 shows how little the limit says about the work.

## arbitrum 0xb5ead73120b4e0aa7e097bdda851a60488c30ec03f517cb060a876adbeead2fb
mechanism: Chainlink OCR2 transmit (oracle report) with a 100M gas limit
confidence: high
unverified: which feed or product sits behind the two contracts; the transmit selector 0xb1dc65a4 and the Transmitted(configDigest, epoch) event are recognised from memory.
The target emits Transmitted with config digest 0x00010bed… and epoch 0x4fcde, the signature of OCR2 report delivery. The 100,001,242 gas limit against 124,454 used (ratio about 803) is a node-side setting; Chainlink nodes on Arbitrum submit with very large limits because the L1 component of gas is uncertain. Legacy type, zero tip. The first log, from 0x1301…438c, records a value and a timestamp keyed by an indexed 61-bit number and is the payload consumer.

## arbitrum 0x50424772d6381d1536d79fae9aa7c21b52fa1d382990bba6ffa2dfa8c5cc9da9
mechanism: Superfluid distribution-agreement interaction, likely a liquidity-mover call earning a small reward
confidence: medium
unverified: GDAv1 at 0x1e29…ba02 and the roles of 0x52f0…55cf and 0x7da6…3879 are model memory; the reward interpretation rests on the two small residual transfers to the caller.
Both tokens emit ERC-777 Sent alongside every Transfer, which marks them as Superfluid super tokens (ETHx is Superfluid's wrapped native symbol). The caller's contract pulls 6.39 USND from one account and 0.0000972 ETHx from another, returns 0.226 USND, and the distribution-agreement contract updates pool memberships while the LI.FI Diamond (0x1231…4eae) executes a leg. The caller ends with +0.0314 USND and +0.000113 ETHx, the shape of a keeper bonus. 4.75M gas makes it the largest fee on Arbitrum (0.000095 ETH), with no tip because the chain has none.

## arbitrum 0xfdddfb85031d418d32a31def6f3dd126fcf07ad81b8229aa25f33693e1ec7432
mechanism: GMX V2 keeper executing orders, second keeper (see #18)
confidence: high
unverified: as #18.
A different keeper EOA (nonce 811,501) executing orders through the same handler with 4.5M gas; four keeper EOAs called the handler in the window.

## optimism 0xaa91d3d3b93e1b3a4de882c84ca97d7ee1b9e93e71c060db0885111a48461765
mechanism: deterministic heavy-compute call once per block, rotated across three wallets, at near-zero cost
confidence: medium
unverified: what the contract computes; the single event (block number, 1, -9791, 7576515) is not decoded.
The contract 0x2a78…357e received exactly 60 calls in the 60 Optimism blocks of the window from three EOAs taking turns (20 each, nonces near 92,000), every call using between 7,384,083 and 7,384,115 gas with a 15,000,000 limit and a priority fee of 1 wei. The base fee is about 1,400 wei, so 7.4M gas costs about 1e10 wei, and with the L1 data fee the whole call costs about 0.00000001 ETH. A fixed loop of this size repeated every block by a wallet rotation is the signature of on-chain "mining" or gas-farming schemes that exploit near-free L2 execution. Gas-limit ranking surfaces it; fee ranking never would.

## optimism 0x5a9b3dd0255f1a335994fc8fef945a53fca7756d4a2e83c021bf12e9a56cf803
mechanism: per-block compute loop, second wallet (see #23)
confidence: medium
unverified: as #23.
Second wallet of the rotation described in #23; identical gas usage.

## optimism 0xb1d6213a2adc39db776068a1bce139ced7c55309edaeec6d8491c83f418c0de9
mechanism: per-block compute loop, third wallet (see #23)
confidence: medium
unverified: as #23.
Third wallet of the rotation described in #23.

## optimism 0x708132e124e438307fa0a9a5426aeb479a67f7fa8487823dd216679b70f03129
mechanism: keeper-executed user withdrawal from a USDC vault, principal plus accrual
confidence: medium
unverified: protocol identity; the 122-byte entry contract and the 1,419-byte pool contracts have no registered signatures, and the 3.7 KB calldata (presumably a signed request plus oracle data) was not decoded.
The keeper (nonce 1,437,900; 21 transactions in the window) calls a tiny entry contract with 3,748 bytes of calldata. A pool contract updates an index and sends 0.477892 USDC to an intermediary, which forwards it to user 0x4344…39c2; paired events record 477,487 then 477,892 units, so the user recovered a principal plus about 0.08 percent. A registry emits a completion record with a timestamp. The fee comes from 2.8M gas at a 0.005 gwei tip, several thousand times the base fee; the L1 data fee is negligible here. A second keeper for the same system (#30) sent 107 transactions in the window, about 7 percent of all user transactions on Optimism.

## optimism 0xa0c2421f1da1388be1f3160c9e57a3cf1a99b43ae97adbc0a30945e226798ef3
mechanism: high-volume payout operator moving USDC through a forwarder with a flat 0.1 gwei tip
confidence: high
unverified: operator identity.
The EOA's nonce is 8,245,120, one of the highest in the sample, and it sends through a 209-byte forwarder with execute(token, value, data): 34,638.03 USDC here, 500 USDC in #29, and a direct 46,488.91 USDT transfer in #28, all within one minute. The 0.1001 gwei tip is identical across the three and about nine times the chain P99; the total cost is 0.000008 ETH. The outlier is a configuration choice by an exchange-style withdrawal system, not competition.

## optimism 0x69a83902191326d9e101758be77bcde2d5fde7c6b18eb92d0dc84828d1da789d
mechanism: high-volume payout operator, direct USDT transfer (see #27)
confidence: high
unverified: as #27.
Same operator as #27, a direct transfer of 46,488.91 USDT from the EOA.

## optimism 0x2ae6f8fadb924d7ad30dc5c31bc7bd5037c2be2cc04c995cfc45f07d32360679
mechanism: high-volume payout operator, USDC through the forwarder (see #27)
confidence: high
unverified: as #27.
Same operator as #27, 500 USDC through the forwarder.

## optimism 0xfc98f6c0580d8e8f48b385625861ebfb90e49325efc8640095991af0ea776d6f
mechanism: keeper-executed user withdrawal, second keeper of the same system (see #26)
confidence: medium
unverified: as #26.
A second entry contract of the same 122-byte shape, called by a keeper whose nonce is 5,526,818 and which sent 107 transactions in the window. User 0xd5cf…9d3a receives 30.485989 USDC out of the pool (recorded as 30,404,957 then 30,485,989 units) plus 0.914579 USDC from a separate fund, and the registry logs a request id with status 1. Two keepers and two entry points serving the same pools suggest a large automated service with sharded submitters.

## optimism 0xf66e374921da17d8178587c18382d4cf7c1df003801085ef4b1abe36c6268723
mechanism: keeper-executed user withdrawal (see #26)
confidence: medium
unverified: as #26.
Same keeper and entry contract as #26, for user 0x525b…2041 per calldata, 2.79M gas.

## polygon 0xcdff86da13662b15b57190e07bf9feb39a12117ba3224b39f53bff19b4c040d2
mechanism: payout wallet with a flat 5,000 gwei gas price taking position 0 in the block
confidence: high
unverified: operator identity.
A 47.23 USDC (native) transfer, 60,191 gas, effective price 5,000 gwei against a 246.6 gwei base fee, landing at index 0. Polygon validators order by gas price, so a flat 5,000 gwei guarantees the top slot for 0.30 POL. The sender's three transactions in the window all pay the same tip, and its nonce (757,875) says a payout system. Polygon's high nominal gwei culture appears throughout the repeat-sender table: many 21,000-gas transfers at 400 to 960 gwei.

## polygon 0x9c20b2dd35f34f7d0231de40488a53f414086661b675e22057f9d13787bd8d8f
mechanism: Polymarket relayer executing a neg-risk position conversion through a user's proxy wallet
confidence: high
unverified: the relay-hub role of 0xd216…f494 is inferred from the call shape (user proxy and the proxy wallet factory 0xab45…4052 in calldata) and from the TransactionRelayed-shaped event; ConditionalTokens 0x4d97…6045, NegRiskAdapter 0xd91e…5296 and the PositionSplit topic are model memory.
Calldata names a user proxy wallet and Polymarket's proxy wallet factory; the relayer EOA (nonce 567,461) pays gas so the user does not. Inside, 110 WCOL are minted to the NegRiskAdapter and split ten at a time into 11 conditions of one neg-risk market (11 PositionSplit events, 16 ERC-1155 batch transfers), which is how converting NO positions across questions into YES positions and collateral works. The 32,000,000 gas limit is the relayer fleet setting: the hub received 120 relayed calls from 70 relayer EOAs in the window, median 288,000 gas.

## polygon 0xb03af3867ed43d01081c76feb2e80282b874ec13a207b7f51b5cdcb70e57ff62
mechanism: relayer submitting EIP-7702 delegations for another account with escalating gas in one block
confidence: high
unverified: the authority address behind the authorization (needs signature recovery); who controls delegate target 0xe965…db7c; the reason four of the six attempts reverted.
A type-4 transaction with one authorization: delegate to 0xe965…db7c, authority nonce 218,162, so the authority is a different, well-used account rather than the sender (sender nonce 62,956). Gas used 46,000 equals 21,000 plus a 25,000 authorization charge. The sender submitted six such transactions in this single block (positions 74 to 79), four of which failed, with tips between roughly 160 and 10,940 gwei. Authorizations take effect even when execution reverts, so the repeats and the gas escalation look like a race to install or replace a delegation on a contested account, the pattern seen when a leaked key is fought over by sweeper bots. Polygon had 192 type-4 transactions in the window; the top delegate target (0xf5a7…8bfe, 89 authorizations from three relayers) is the same helper contract called 155 times in #38.

## polygon 0x2878e165fd31899d635a20993722463f59826ca539d1da651f6835e963e71289
mechanism: race to be first proposer on a UMA Optimistic Oracle YES_OR_NO_QUERY request, 750 USDC.e bond
confidence: high
unverified: 0x2c03…58b1 as an Optimistic Oracle proxy and 0x6507…f2a7 as a Polymarket adapter are inferred; the proposed answer and the market question inside the 2 KB ancillary data were not decoded; the 750 USDC bond as Polymarket's standard is model memory.
The event data begins with the bytes of "YES_OR_NO_QUERY", UMA's identifier for Polymarket resolutions, followed by a request timestamp of 2026-09-03 20:44:31 UTC and ancillary data. The proposer contract moves exactly 750 USDC.e into the oracle contract as the proposal bond. The sender paid 88,175 gwei per gas (tip 87,924 gwei, about 350 times the base fee), 26.88 POL in total, to take index 0 of the block. Only the first valid proposal earns the proposer reward, so proposers bid for the top slot the moment a market becomes resolvable. This is the largest fee on Polygon in the window by a factor of three.

## polygon 0x1db46a66979eab538e967f35460dfcd6b4645fde58b2f61d68d54d5660de6277
mechanism: relayed call through the Polymarket hub consuming 21M gas with no visible effect
confidence: low
unverified: whether the inner call reverted; the TransactionRelayed-shaped status word reads 0, which in GSN-style hubs means success, yet no state-changing events were emitted.
Same relayer hub as #33 and #37, but 21,069,094 gas produced a single hub event (relayer, user proxy 0x91e2…3e62, factory, inner selector 0x34ee9791, status 0, charge 1) and nothing else. Among the hub's 120 relayed calls in the window this is the only one above 10M gas (median 288,000). Either the inner operation is a heavy computation without events, or the inner call exhausted its gas and the hub swallowed the failure while the outer transaction reports success. 8.56 POL was spent. A transaction trace is the cheapest next query.

## polygon 0xdc691e350bf76d74ace1f96ae775664d386bcc3f35a99c33a0634a2783931c67
mechanism: Polymarket relayer executing a neg-risk position conversion (see #33)
confidence: high
unverified: as #33.
Same relayer hub and operation as #33 for another user proxy (0x11d7…6db): 14 batch transfers, 9 PositionSplits, 1.9M gas.

## polygon 0x91478029cafd0fe49804d92526cd4a56d7125dc02695782958006d9c18fc059f
mechanism: Multicall3 batch of 155 unstake-and-forward operations consolidating LGNS to one recipient
confidence: medium
unverified: whether the 155 positions belong to distinct wallets; the role of helper 0xf5a7…8bfe; what LGNS and sLGNS are beyond their self-reported symbols. Multicall3 at 0xca11…ca11 and the aggregate3 selector are recognised from memory.
The sender calls Multicall3 aggregate3 with 155 calls to helper 0xf5a7…8bfe, each producing the same seven-event pattern: two sLGNS approvals, sLGNS from escrow 0x25a4…8b07 to staking contract 0x1964…1bfc, LGNS back to the escrow, LGNS forwarded to 0xd080…00c7, and a helper record with the amount (1.467808 LGNS, 1.747383 LGNS and so on). 1,087 logs and 10.36M gas for 3.21 POL. The same helper is the delegate target of 89 EIP-7702 authorizations in the window from three relayer EOAs, so one operator controls many accounts through delegation and batches their claims: activity that a naive count would read as hundreds of users, the pattern the pilot memo flagged in its first finding.
