# Gas outliers: a quant scan followed by an LLM investigation

Proof of concept for one loop iteration. The deterministic step ranks every user transaction in the saved five-chain sample by three gas metrics and selects the top 3 per metric per chain. The qualitative step reads the resulting evidence packets and explains what each transaction did. Every number below is computed by `scripts/gas_outliers.py`; the prose under each transaction is the LLM's interpretation and is labelled with a confidence. Identity claims that rest on model memory rather than an onchain check are marked as such.

Sample: 2026-09-05T09:31:23+00:00 to 2026-09-05T09:33:23+00:00 (exclusive), the discovery window of the pilot. Chain-generated transactions (Arbitrum types 0x64-0x6a, OP Stack type 0x7e deposits) are excluded from baselines and selection. Priority fee means `effectiveGasPrice - baseFeePerGas` of the containing block. Total fee paid adds the reported L1 fee on OP Stack chains and blob fees on Ethereum.

## Chain baselines

| Chain | User txs | System txs | Median gas limit | P99 gas limit | Max gas limit | Median tip (gwei) | P99 tip (gwei) | Max tip (gwei) | Median fee paid | P99 fee paid | Max fee paid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ethereum | 2,742 | 0 | 70,000 | 5,247,560 | 16,698,639 | 0.0494 | 2.9308 | 36.4286 | 0.000008 ETH | 0.000601 ETH | 0.004349 ETH |
| base | 8,147 | 60 | 250,000 | 8,000,000 | 16,777,216 | 0.001 | 0.0448 | 1.2761 | 0.000001 ETH | 0.000015 ETH | 0.000621 ETH |
| arbitrum | 1,512 | 474 | 191,694 | 25,000,000 | 100,001,242 | 0 | 0 | 0 | 0.000001 ETH | 0.000037 ETH | 0.000095 ETH |
| optimism | 1,569 | 60 | 1,500,000 | 15,000,000 | 15,000,000 | 0.000000704 | 0.0111 | 0.1001 | 0.000000 ETH | 0.000008 ETH | 0.000014 ETH |
| polygon | 9,056 | 0 | 390,128 | 10,000,000 | 32,000,000 | 148.2000 | 805.0000 | 87924.0000 | 0.079469 POL | 1.079998 POL | 26.884237 POL |

## Cross-cutting observations (LLM)

Three kinds of transaction produce gas outliers in this window, and only one of them signals urgency.

Configuration artifacts. Most gas-limit outliers are round numbers chosen by tooling: 2^24 on Base (#10, #11, #13), 32,000,000 on Arbitrum and Polygon (#17, #19, #33, #36, #37), 15,000,000 on Optimism (#23 to #25), 16,698,639 for an Ethereum bot fleet (#4, #6, #7) and 100,001,242 for a Chainlink node (#20). Limit-to-used ratios run from 1.3 to 803. Many tip outliers are flat presets rather than bids: exactly 2 gwei for eight repeat senders on Ethereum, 1.0 gwei on Base (#14, #15, #16), 0.1001 gwei on Optimism (#27 to #29), 5,000 gwei on Polygon (#32). A sender whose tip never varies is not expressing urgency, whatever the multiple of the base fee.

Ordering competition. Where the tip varies within a sender, or a transaction sits at the top of the block, the mechanism is a race. Two Ethereum top-of-block transactions react to the trade immediately before them: #1 backruns a FOLD fill, and #3 pays the builder 0.002975 ETH behind a FOLD purchase, with the payment recipient equal to the block's miner. A Base bot pays 255 times the base fee for one opportunity and a median 0.0047 gwei otherwise (#12). A Polygon proposer pays 88,175 gwei per gas to be first on a UMA resolution request (#35), and a 7702 relayer escalates to 10,940 gwei inside one block (#34). On Polygon the validator sorts by gas price, so both extreme tips land at index 0; on Ethereum the builders placed the two high-tip transactions at index 1, directly behind the transaction they react to.

Automated fleets. The same contract is called by rotating EOAs: three wallets for the Ethereum arbitrage fleet, three for the Optimism per-block loop, four GMX keepers, seven callers of the Base per-id contract, 70 relayer EOAs for the Polymarket hub. Sender counts overstate actors. One Optimism keeper alone (#30) sent 107 transactions in the window, about 7 percent of the chain's user transactions.

The priority-fee metric carries no information on Arbitrum, where every transaction pays the base fee and the scan skipped the metric; little on OP Stack chains, where the base fee is around a thousand wei and tips run from 1 wei to 0.1 gwei; and a strong ordering signal on Polygon and Ethereum. For the flagged transactions the L1 data component of OP Stack fees was under 1 percent of the total; it matters for the median transaction, not for these outliers. Gas-limit ranking surfaced the two mechanisms that fee ranking would never find: the near-free Optimism compute loop (#23) and the Chainlink 100M-limit report (#20).

Hypotheses for the quant step, each falsifiable on a longer sample. (1) On Ethereum, transactions with a tip above the chain P99 at index 1 or 2 share a token with the index-0 transaction far more often than random transactions do, and the effect disappears for high-tip transactions beyond index 10. (2) Senders with zero tip variance over five or more transactions show no better placement and no lower failure rate than median-tip senders, so they should be excluded from any urgency feature. (3) The Optimism per-block loop runs continuously and consumes a stable share of block gas, so utilization on that chain overstates demand by that share.

## Ethereum

| # | Transaction | Selected for | From | To | Gas limit / used | Eff. price (gwei) | Tip (gwei) | Fee paid | Status | Logs | Mechanism (LLM) |
|---:|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| 1 | [0x53c5…c77e](https://etherscan.io/tx/0x53c5a374bc2fcc7cd7a3b2403d8906cc69008a1bb833ff08067838a5b198c77e) | total fee paid #2 | [0x315d…9eba](https://etherscan.io/address/0x315d2ee4fccda0def532ef4108ff57204f8d9eba) | [0x447a…5d73](https://etherscan.io/address/0x447a03c131c0a97a8b8d548e3cd81aec4ce05d73) | 316,578 / 140,079 | 18.3403 | 18.2682 | 0.002569 ETH | success | 3 | top-of-block backrun of a FOLD trade on Uniswap V4 |
| 2 | [0xbb85…4b8b](https://etherscan.io/tx/0xbb85f0f3ec69e5445673408b41bb7927e15aedecc8151ba60da3509b8e204b8b) | priority fee #1 (2 tied) | [0x8d02…ba16](https://etherscan.io/address/0x8d02bb7ffd0ae9f6cf9004f290edcc96cd58ba16) | [0x8d02…ba16](https://etherscan.io/address/0x8d02bb7ffd0ae9f6cf9004f290edcc96cd58ba16) | 21,000 / 21,000 | 36.5006 | 36.4286 | 0.000767 ETH | success | 0 | transaction cancellation or nonce management by an EOA |
| 3 | [0x53a6…ee6a](https://etherscan.io/tx/0x53a64ed68331561b9097c8243df85af6922f40fc4a1f749c4920a6f9fad4ee6a) | priority fee #3 | [0xcce3…fea5](https://etherscan.io/address/0xcce3469e745112fb018cc2158f68717b98ccfea5) | [0x22b1…f46e](https://etherscan.io/address/0x22b19704e575d5e776608c5283e88606a546f46e) | 320,000 / 32,015 | 20.0658 | 20.0000 | 0.000642 ETH | success | 1 | explicit payment to the block builder behind a FOLD purchase |
| 4 | [0x2af8…925c](https://etherscan.io/tx/0x2af8ff2c02d0479482c6314524f4447ead63c53a9b0c141c0ef6f7142816925c) | gas limit #1 (2 tied) | [0xec82…c0b5](https://etherscan.io/address/0xec82f2c025d627df346487d858c726bcdd3dc0b5) | [0xce8b…528b](https://etherscan.io/address/0xce8b69d410e3241280ea8d0b1f71ba6840c4528b) | 16,698,639 / 376,310 | 0.0698 | 0.000161155 | 0.000026 ETH | success | 9 | flash-loan arbitrage between two Uniswap V4 ELA pools |
| 5 | [0x7733…de41](https://etherscan.io/tx/0x773374f66aea53100bc30a92c07ae53c5c6d1e6ee941685f6baf44b62c4ade41) | total fee paid #1 | [0xa6ef…b867](https://etherscan.io/address/0xa6efdcdef0da0fc6be701684aaa951530df9b867) | [0x8fea…b4f6](https://etherscan.io/address/0x8feab81d36e7576107d5de0758c1b839be31b4f6) | 2,882,599 / 1,696,814 | 2.5633 | 2.4986 | 0.004349 ETH | success | 40 | aggregator-routed purchase of uPEG with 0.2 ETH split across V3 and V4 pools |
| 6 | [0xd620…f50f](https://etherscan.io/tx/0xd620890c9ce91144a831b23deb3af3a7b4f7cd5499511caad2e8995ce39af50f) | gas limit #2 (2 tied) | [0x6ddf…9c15](https://etherscan.io/address/0x6ddf06ad881919d0be73ad73b42e847ca6a69c15) | [0xce8b…528b](https://etherscan.io/address/0xce8b69d410e3241280ea8d0b1f71ba6840c4528b) | 16,698,639 / 723,440 | 0.0648 | 0.000160702 | 0.000047 ETH | success | 24 | flash-loan arbitrage across three Uniswap V4 uPEG pools in the block of the retail buy |
| 7 | [0x3321…b8ad](https://etherscan.io/tx/0x33212e50252603613a2b0b6ccbd0a926fdce45e865fc706bb1653a6eb710b8ad) | gas limit #3 | [0x9535…81ae](https://etherscan.io/address/0x953503d27e0cdf2e27775e4c49dc875b47ee81ae) | [0xce8b…528b](https://etherscan.io/address/0xce8b69d410e3241280ea8d0b1f71ba6840c4528b) | 16,678,412 / 1,072,960 | 0.0648 | 0.000160702 | 0.000070 ETH | success | 12 | flash-loan triangular arbitrage uPEG to USDT to WETH in the block of the retail buy |
| 8 | [0xf7c4…00bd](https://etherscan.io/tx/0xf7c4dd2c481c40e7cc772384781af86dfbf3b017b5eaa31b52463e68b1b800bd) | priority fee #2 (2 tied) | [0x8d02…ba16](https://etherscan.io/address/0x8d02bb7ffd0ae9f6cf9004f290edcc96cd58ba16) | [0x8d02…ba16](https://etherscan.io/address/0x8d02bb7ffd0ae9f6cf9004f290edcc96cd58ba16) | 21,000 / 21,000 | 36.4933 | 36.4286 | 0.000766 ETH | success | 0 | transaction cancellation or nonce management, second of a pair |
| 9 | [0x1280…49b9](https://etherscan.io/tx/0x12802ed453d708a5145c909a8a44011daf89f8d0be7411236faedfee382849b9) | total fee paid #3 | [0xd844…552a](https://etherscan.io/address/0xd84455fd51122d336e39bb5d32dde23b80a4552a) | [0x0000…2734](https://etherscan.io/address/0x0000000000001ff3684f28c67538d4d072c22734) | 1,333,400 / 958,506 | 2.0693 | 2.0000 | 0.001983 ETH | success | 43 | aggregator sale of 1,000 RAIL for ETH through a split route |

Repeated high-tip senders (three or more transactions at or above the chain P95 tip of 2.0000 gwei):

| Sender | High-tip txs | All txs in sample | Failed | Distinct destinations | Median tip (gwei) | Median gas limit | Top selectors | Examples |
|---|---:|---:|---:|---:|---:|---:|---|---|
| [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) | 31 | 61 | 0 | 1 | 2.0260 | 210,000 | 0xa9059cbb ×31 | [0xe1bc…a4f0](https://etherscan.io/tx/0xe1bc17bd77b23f59a10501f86e8d7f28b066e36ee6dca87531e8887f71c8a4f0) [0x738b…882c](https://etherscan.io/tx/0x738b57f49be6fcbd824f2d59466cd6adcab44edd881b1c7cd860b30ccb02882c) [0xd96a…4914](https://etherscan.io/tx/0xd96acd5cf2a6c6aa2cf4cd0bba032c406d49421a9e61cee13ab38307f69c4914) |
| [0x05ff…f381](https://etherscan.io/address/0x05ff6964d21e5dae3b1010d5ae0465b3c450f381) | 8 | 8 | 0 | 2 | 2.0000 | 147,463 | 0xb61d27f6 ×7, 0x ×1 | [0x1657…c4e5](https://etherscan.io/tx/0x1657c2da8683e649d280a57f86a4ec3f089e715a2bde70461f83dd781e7ec4e5) [0x3890…1541](https://etherscan.io/tx/0x3890f71bbb90b4c5e4ee6ad7332ed274b0f3764354dab568aa21c2f9b15d1541) [0x6927…6784](https://etherscan.io/tx/0x692741ee1927ad6a83f29bf15fc614cec78521b494de33f81cd0522a37d16784) |
| [0xc3c7…6907](https://etherscan.io/address/0xc3c7de27812e5246845fc90a50412199f2e46907) | 6 | 6 | 0 | 4 | 2.0000 | 342,863 | 0x095ea7b3 ×3, 0x3ce33bff ×3 | [0xca3d…b13c](https://etherscan.io/tx/0xca3d1e0889d375d2c5a5fec695d14d2dcae8fde27c2d9a2da970e3155f65b13c) [0x5221…b967](https://etherscan.io/tx/0x522116678a3e1fc2c64323c095b87a28a0ce9e35aed2523a400ae3f812d7b967) [0x6ee7…0690](https://etherscan.io/tx/0x6ee7bbe13b063be60cd82ef75764da71f697db2b30fffd095798d4b378140690) |
| [0x18e2…82f6](https://etherscan.io/address/0x18e296053cbdf986196903e889b7dca7a73882f6) | 6 | 6 | 0 | 1 | 2.0000 | 90,000 | 0xa9059cbb ×6 | [0x4a71…2b7d](https://etherscan.io/tx/0x4a71f54a44da4fc54430150d71d43d99c2ae6f54a435f7061714b00c219f2b7d) [0x3596…0c47](https://etherscan.io/tx/0x359655e54a0a6620b497a9608d59e2831f1e0122692d7a20ac52faf7fa4a0c47) [0x3754…4ed8](https://etherscan.io/tx/0x37543a55eceef6d580974378f2a115a0a635a8dbedbad10244eb8fdcd8d24ed8) |
| [0xd47a…e624](https://etherscan.io/address/0xd47a1bdc6872ad2fd16e50149baa9924c653e624) | 6 | 6 | 0 | 5 | 2.0000 | 60,500 | 0x ×3, 0xa9059cbb ×3 | [0x9a79…b6ce](https://etherscan.io/tx/0x9a7907567b24abef026cde8480c373561d88f7d242692ce0f81cefc19234b6ce) [0xc2f6…fc0b](https://etherscan.io/tx/0xc2f68aca5b6c5643cfc159e999e567addd46a9ab52b58bb8b363fcb2d4d7fc0b) [0xaae8…7328](https://etherscan.io/tx/0xaae8fec9eb0437cadc7e3add4c87780fedccaaebbb12330a0936432263987328) |
| [0xaa8b…3efb](https://etherscan.io/address/0xaa8ba7d4611437141192e7ceced531bc0a133efb) | 5 | 5 | 0 | 1 | 2.0000 | 96,046 | 0xa9059cbb ×5 | [0x4b34…fd20](https://etherscan.io/tx/0x4b34dd680eb7d9551f5eefeb73121b8462abcf9bdffef10c8690b2f79551fd20) [0x8608…5065](https://etherscan.io/tx/0x86089cd41f9c11044c4f4e3def26b2709ccc205d00e043b9df7f1c744cb25065) [0x35ff…5f82](https://etherscan.io/tx/0x35ffb1e1c0e37132247312705dbfd3824dd5c4744baa047ff99ebe9547c35f82) |
| [0x8637…3c19](https://etherscan.io/address/0x8637d3d215fbae518c4135e4a5ca125703fc3c19) | 5 | 5 | 0 | 2 | 2.0000 | 573,657 | 0x5f575529 ×4, 0x095ea7b3 ×1 | [0x0469…1289](https://etherscan.io/tx/0x046937f06915b32bef17babe7bc9835999167ec86d2ad8aff0cbc601086d1289) [0xf609…ebd5](https://etherscan.io/tx/0xf6097d673db4183b7c09c0764dd07c84dff20dc04b1a009bf554571e1844ebd5) [0x0cf1…16ab](https://etherscan.io/tx/0x0cf130e28e1c6f912e29d3785d1eb9faa2d1fa99f0d1e914580648fb2af116ab) |
| [0xf30b…0eb0](https://etherscan.io/address/0xf30ba13e4b04ce5dc4d254ae5fa95477800f0eb0) | 4 | 4 | 0 | 4 | 2.0000 | 31,500 | 0x ×4 | [0x1f79…3692](https://etherscan.io/tx/0x1f79851f2316cb18f9dee8bb8ac8552c8340aff84ea58821cf4b368249653692) [0x0cfb…b7f2](https://etherscan.io/tx/0x0cfbf730b628610c2a2b1c3a6cfa0ee35e479530ca9ac23696a90a039095b7f2) [0xdb2f…32c3](https://etherscan.io/tx/0xdb2f5dde732576a62a3e7d70b0ca47cd022fa14b60a59829f27dc620c47e32c3) |

### Investigations

#### 1. [0x53c5…c77e](https://etherscan.io/tx/0x53c5a374bc2fcc7cd7a3b2403d8906cc69008a1bb833ff08067838a5b198c77e): top-of-block backrun of a FOLD trade on Uniswap V4

Facts: block 25,910,247 at 2026-09-05T09:31:47+00:00, position 1/230, type 0x2, success. Gas limit 316,578 (chain percentile 82.86), used 140,079. Effective price 18.3403 gwei against base fee 0.0721 gwei, so tip 18.2682 gwei (percentile 99.85). Fee paid 0.002569 ETH (percentile 99.93). Value sent 0.000000 ETH. Destination is a contract. Selector `0x742a7783`, calldata 129 bytes, 3 logs.

Decoded event families: ERC20_Transfer_shape ×2, V4Swap ×1. Distinct transfer recipients: 2.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: -300.000000 USDC.

Interpretation (LLM, confidence medium): The bot contract swapped 300 USDC for 5,733.87 FOLD on the Uniswap V4 PoolManager (pool fee field 6883, a dynamic-fee pool) and delivered the FOLD to a third address encoded in calldata. It sits at index 1 with an 18.27 gwei tip against a 0.07 gwei base fee, immediately behind index 0, a 1inch-routed trade that moved FOLD, USDT and USDC through a V4 pool and the V3 USDC/USDT pool. The tip buys the slot behind that trade: the bot paid 0.00257 ETH to capture the price impact the fill left behind. Sender nonce 800,210 marks a long-running bot. FOLD appears again two blocks later in #3.

Unverified: operator identity; the causal link to the index-0 trade is inferred from adjacency and the shared token, not from a bundle record.

#### 2. [0xbb85…4b8b](https://etherscan.io/tx/0xbb85f0f3ec69e5445673408b41bb7927e15aedecc8151ba60da3509b8e204b8b): transaction cancellation or nonce management by an EOA

Facts: block 25,910,247 at 2026-09-05T09:31:47+00:00, position 204/230, type 0x2, success. Gas limit 21,000 (chain percentile 0.0), used 21,000. Effective price 36.5006 gwei against base fee 0.0721 gwei, so tip 36.4286 gwei (percentile 99.93). Fee paid 0.000767 ETH (percentile 99.38). Value sent 0.000000 ETH. Destination is an EOA. Selector `0x`, calldata 0 bytes, 0 logs.

Decoded event families: none.

Interpretation (LLM, confidence medium): A zero-value transfer from an EOA to itself, 21,000 gas, with a 36.43 gwei tip while the base fee is 0.07 gwei. That is the shape of cancel-and-replace: a wallet resubmits nonce N as an empty self-transfer at a higher price to displace a stuck transaction. The same EOA repeats it five blocks later with the next nonce (#8), so two consecutive pending transactions were replaced. Despite the highest tip on the chain in this window it landed at position 204 of 230: builders do not order by tip alone. Nonce 61,773 says an active account, not a high-frequency bot.

Unverified: whether a pending transaction with the same nonce existed; only mempool data would show it.

#### 3. [0x53a6…ee6a](https://etherscan.io/tx/0x53a64ed68331561b9097c8243df85af6922f40fc4a1f749c4920a6f9fad4ee6a): explicit payment to the block builder behind a FOLD purchase

Facts: block 25,910,249 at 2026-09-05T09:32:11+00:00, position 1/137, type 0x2, success. Gas limit 320,000 (chain percentile 82.9), used 32,015. Effective price 20.0658 gwei against base fee 0.0658 gwei, so tip 20.0000 gwei (percentile 99.89). Fee paid 0.000642 ETH (percentile 99.09). Value sent 0.002975 ETH. Destination is a contract. Selector `0x41664c4d`, calldata 4 bytes, 1 log.

Decoded event families: unknown ×1.

Interpretation (LLM, confidence high): The 985-byte destination contract forwards the transaction value to an address and logs (recipient, amount). The logged recipient 0x9522…afe5 equals the miner field of block 25,910,249, whose extraData reads beaverbuild.org, so the 0.002975 ETH went to the builder that produced the block. Index 0 of the same block is a 1.235 ETH purchase of FOLD through two Uniswap V4 swaps at a 0.1 gwei tip. A buy followed at index 1 by a separate payment transaction with a 20 gwei tip is how sniper tooling secures top-of-block placement for a token purchase. With #1, two of the three highest Ethereum tips in the window are FOLD-related ordering competition.

Unverified: which party assembled the bundle; whether the index-0 buyer and this payer are the same operator.

#### 4. [0x2af8…925c](https://etherscan.io/tx/0x2af8ff2c02d0479482c6314524f4447ead63c53a9b0c141c0ef6f7142816925c): flash-loan arbitrage between two Uniswap V4 ELA pools

Facts: block 25,910,251 at 2026-09-05T09:32:35+00:00, position 2/60, type 0x2, success. Gas limit 16,698,639 (chain percentile 99.93), used 376,310. Effective price 0.0698 gwei against base fee 0.0697 gwei, so tip 0.000161155 gwei (percentile 15.5). Fee paid 0.000026 ETH (percentile 69.84). Value sent 0.000000 ETH. Destination is a contract. Selector `0xce5937d7`, calldata 996 bytes, 9 logs.

Decoded event families: ERC20_Transfer_shape ×4, V4Swap ×2, WETHDeposit ×1, WETHWithdrawal ×1, unknown ×1. Distinct transfer recipients: 3.

Interpretation (LLM, confidence high): Balancer V2 Vault lends 0.011505 WETH to the bot contract (FlashLoan event at the end). The bot unwraps it, buys 108.031 ELA in V4 pool 0xe5be… for 0.011505 of currency0, sells the same ELA in V4 pool 0x3708… for 0.020081 of currency0, wraps the proceeds and repays Balancer. The gross spread is about 0.0086 ETH before any builder payment, on a 0.000026 ETH fee. The 16,698,639 gas limit against 376,310 used is a fixed fleet setting: three different EOAs call this contract in the window with the same limit and the same 0.00016 gwei tip (#6, #7). The packet's ERC-20 net flow shows zero for WETH because the profit moved through WETH deposit and withdraw events, which the flow calculation does not count.

Unverified: how the builder was compensated; there is no meaningful priority fee and no visible coinbase transfer.

#### 5. [0x7733…de41](https://etherscan.io/tx/0x773374f66aea53100bc30a92c07ae53c5c6d1e6ee941685f6baf44b62c4ade41): aggregator-routed purchase of uPEG with 0.2 ETH split across V3 and V4 pools

Facts: block 25,910,252 at 2026-09-05T09:32:47+00:00, position 5/392, type 0x2, success. Gas limit 2,882,599 (chain percentile 97.7), used 1,696,814. Effective price 2.5633 gwei against base fee 0.0647 gwei, so tip 2.4986 gwei (percentile 98.69). Fee paid 0.004349 ETH (percentile 99.96). Value sent 0.200000 ETH. Destination is a contract. Selector `0x0c307f76`, calldata 4,708 bytes, 40 logs.

Decoded event families: ERC20_Transfer_shape ×16, unknown ×14, V4Swap ×4, WETHWithdrawal ×3, V3Swap ×2, WETHDeposit ×1. Distinct transfer recipients: 9.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: +2.409196 uPEG | destination: -0.199200 WETH.

Interpretation (LLM, confidence medium): A low-activity account (nonce 553) sends 0.2 ETH to a router that wraps it and splits the order: legs through the WETH/USDT V3 pool, a V4 WETH/uPEG pool (fee 10000), a V3 uPEG/WETH pool and further legs in the remaining logs, with 0.1992 WETH forwarded per calldata and 0.0008 ETH retained as fee. The sender ends with +2.409 uPEG. A 2.5 gwei tip is about 38 times the base fee and, with 1.7 million gas for the route, makes this the largest fee on Ethereum in the window at 0.00435 ETH. The purchase moved the V4 uPEG pool to tick 25,021; two arbitrage transactions later in the same block (#6, #7) trade uPEG back across pools.

Unverified: which aggregator; the router emits a swap-record event signature that also appears on Base (#16) and is not in the decoder.

#### 6. [0xd620…f50f](https://etherscan.io/tx/0xd620890c9ce91144a831b23deb3af3a7b4f7cd5499511caad2e8995ce39af50f): flash-loan arbitrage across three Uniswap V4 uPEG pools in the block of the retail buy

Facts: block 25,910,252 at 2026-09-05T09:32:47+00:00, position 156/392, type 0x2, success. Gas limit 16,698,639 (chain percentile 99.93), used 723,440. Effective price 0.0648 gwei against base fee 0.0647 gwei, so tip 0.000160702 gwei (percentile 15.43). Fee paid 0.000047 ETH (percentile 78.26). Value sent 0.000000 ETH. Destination is a contract. Selector `0xce5937d7`, calldata 1,092 bytes, 24 logs.

Decoded event families: ERC20_Transfer_shape ×8, unknown ×8, V4Swap ×4, WETHDeposit ×2, WETHWithdrawal ×2. Distinct transfer recipients: 3.

Interpretation (LLM, confidence high): Same fleet contract as #4 from a second EOA. Two Balancer flash loans (0.005948 and 0.001085 WETH): buy uPEG in pool 0x94af… (the pool #5 bought into, now at tick 25,017), sell it in pool 0xe051…; then buy in 0xe051… and sell in 0x5c8a…. Returned amounts exceed the loans by roughly 0.0001 and 0.00002 ETH. This is the mechanical response to the price impact of #5, landing at index 156 of the same block. Two unknown emitters (0x6bea…, 0x08a4…) log around each swap and look like a V4 hook and a per-sender accounting contract.

Unverified: builder compensation, as in #4.

#### 7. [0x3321…b8ad](https://etherscan.io/tx/0x33212e50252603613a2b0b6ccbd0a926fdce45e865fc706bb1653a6eb710b8ad): flash-loan triangular arbitrage uPEG to USDT to WETH in the block of the retail buy

Facts: block 25,910,252 at 2026-09-05T09:32:47+00:00, position 295/392, type 0x2, success. Gas limit 16,678,412 (chain percentile 99.89), used 1,072,960. Effective price 0.0648 gwei against base fee 0.0647 gwei, so tip 0.000160702 gwei (percentile 15.43). Fee paid 0.000070 ETH (percentile 84.28). Value sent 0.000000 ETH. Destination is a contract. Selector `0xce5937d7`, calldata 2,084 bytes, 12 logs.

Decoded event families: ERC20_Transfer_shape ×6, V4Swap ×3, WETHDeposit ×1, WETHWithdrawal ×1, unknown ×1. Distinct transfer recipients: 3.

Interpretation (LLM, confidence high): Third EOA of the same fleet, index 295 of the same block as #5 and #6. Balancer lends 0.017825 WETH; the bot buys 0.2152 uPEG in pool 0x94af… (tick now 25,006), sells it for 44.20 USDT in V4 pool 0xda43…, converts the USDT to 0.017986 WETH in V4 pool 0x2287… (fee 125) and repays. The spread is about 0.00016 ETH. Three fleet transactions across two blocks each retained under 0.01 ETH; the fleet's economics rest on volume and near-zero tips, not on individual trades.

Unverified: builder compensation.

#### 8. [0xf7c4…00bd](https://etherscan.io/tx/0xf7c4dd2c481c40e7cc772384781af86dfbf3b017b5eaa31b52463e68b1b800bd): transaction cancellation or nonce management, second of a pair

Facts: block 25,910,252 at 2026-09-05T09:32:47+00:00, position 388/392, type 0x2, success. Gas limit 21,000 (chain percentile 0.0), used 21,000. Effective price 36.4933 gwei against base fee 0.0647 gwei, so tip 36.4286 gwei (percentile 99.93). Fee paid 0.000766 ETH (percentile 99.34). Value sent 0.000000 ETH. Destination is an EOA. Selector `0x`, calldata 0 bytes, 0 logs.

Decoded event families: none.

Interpretation (LLM, confidence medium): Identical shape to #2 with the next nonce (61,774), five blocks later, the same 36.43 gwei tip, landing at position 388 of 392. Two consecutive replacements one minute apart suggest a batch of pending transactions abandoned at once.

Unverified: as #2.

#### 9. [0x1280…49b9](https://etherscan.io/tx/0x12802ed453d708a5145c909a8a44011daf89f8d0be7411236faedfee382849b9): aggregator sale of 1,000 RAIL for ETH through a split route

Facts: block 25,910,254 at 2026-09-05T09:33:11+00:00, position 31/286, type 0x2, success. Gas limit 1,333,400 (chain percentile 95.3), used 958,506. Effective price 2.0693 gwei against base fee 0.0693 gwei, so tip 2.0000 gwei (percentile 89.75). Fee paid 0.001983 ETH (percentile 99.89). Value sent 0.000000 ETH. Destination is a contract. Selector `0x2213bc0b`, calldata 5,924 bytes, 43 logs.

Decoded event families: ERC20_Transfer_shape ×23, unknown ×5, Approval ×4, V2Swap ×4, V2Sync ×4, V3Swap ×2, WETHWithdrawal ×1. Distinct transfer recipients: 13.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: -1000.000000 RAIL.

Interpretation (LLM, confidence medium): The sender moves 1,000 RAIL into a settlement contract, which splits it across four V2 pools (RAIL/DAI 75, RAIL/WETH 349.93 and 525.04, RAIL/renBTC 50.03), then converts the DAI leg through a stable pool and the renBTC leg through Curve-shaped TokenExchange events, unwrapping to ETH at the end (one WETHWithdrawal, and no ERC-20 arrives at the sender). The 2.0 gwei tip is the common flat preset on Ethereum in this window, paid exactly by eight repeat senders, so the fee rank comes from 958,506 gas for the route rather than urgency.

Unverified: the destination 0x0000…2734 as the 0x AllowanceHolder and 0xd718…091f as its Settler are model memory; the exec(operator, token, amount, target, data) calldata layout matches that memory. The Curve TokenExchange identification of topic 0x8b3e96f2… is also from memory.

## Base

| # | Transaction | Selected for | From | To | Gas limit / used | Eff. price (gwei) | Tip (gwei) | Fee paid | Status | Logs | Mechanism (LLM) |
|---:|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| 10 | [0x9e5f…046b](https://basescan.org/tx/0x9e5f7bd9211997b9ebcd99cc2c5b932d95d24ba3eb9e6342c022e207b594046b) | gas limit #1 (11 tied) | [0xec33…9788](https://basescan.org/address/0xec336742a19a9d0d046a83603491e4ae08329788) | [0xf397…755d](https://basescan.org/address/0xf397910f005151b09644228573a4353818d3755d) | 16,777,216 / 252,928 | 0.006 | 0.001 | 0.000002 ETH | success | 3 | scheduled keeper calling a per-id function with a fixed 2^24 gas limit |
| 11 | [0x49a7…0995](https://basescan.org/tx/0x49a7002c06db41e7b3ff150f76240162d9c269aeab1243a745282f1eea920995) | gas limit #2 (11 tied) | [0xec33…9788](https://basescan.org/address/0xec336742a19a9d0d046a83603491e4ae08329788) | [0xf397…755d](https://basescan.org/address/0xf397910f005151b09644228573a4353818d3755d) | 16,777,216 / 254,908 | 0.006 | 0.001 | 0.000002 ETH | success | 3 | scheduled keeper, second call (see #10) |
| 12 | [0x3a3f…9ed4](https://basescan.org/tx/0x3a3f6674bfdedd7402be76cfbd74957801fa88ef8df714b59933b847ef149ed4) | priority fee #1, total fee paid #3 | [0x4ac2…c6d7](https://basescan.org/address/0x4ac2c2b62fb70377cf5fa33b374157c16eb7c6d7) | [0x278d…f8d2](https://basescan.org/address/0x278d858f05b94576c1e6f73285886876ff6ef8d2) | 600,002 / 211,766 | 1.2811 | 1.2761 | 0.000271 ETH | success | 3 | single-pool WETH to ZEN purchase by a bot with a price limit and a competitive tip |
| 13 | [0xc1de…a5d9](https://basescan.org/tx/0xc1decf57896945066db1abcd1a05abd9c51b54d67d7c2ca7bf789ff42ebda5d9) | gas limit #3 (11 tied) | [0xec33…9788](https://basescan.org/address/0xec336742a19a9d0d046a83603491e4ae08329788) | [0xf397…755d](https://basescan.org/address/0xf397910f005151b09644228573a4353818d3755d) | 16,777,216 / 265,184 | 0.006 | 0.001 | 0.000002 ETH | success | 3 | scheduled keeper, third call (see #10) |
| 14 | [0xcf71…1986](https://basescan.org/tx/0xcf71a3d29148de2e33c360bacd568fdba1695d6c88ad56a8e40e3d0fd94f1986) | total fee paid #2 | [0x0b94…c9f0](https://basescan.org/address/0x0b946e493752bcd9a4b8fd8399a20b1b11ccc9f0) | [0xcf77…4e43](https://basescan.org/address/0xcf77a3ba9a5ca399b7c97c74d54e5b1beb874e43) | 900,000 / 474,561 | 1.0050 | 1.0000 | 0.000477 ETH | success | 11 | Aerodrome router swap USDC to WETH to DAG by a user with a flat 1 gwei tip |
| 15 | [0xa066…77cf](https://basescan.org/tx/0xa0667c13a15017a2e3e6bd2b465c38d484c2f8067c3fc8a2db0e17717f1077cf) | priority fee #2 | [0x684f…52e1](https://basescan.org/address/0x684f5f118ed7d0e00b1c0a27dcdce6e37cf652e1) | [0xf851…5e7f](https://basescan.org/address/0xf851feb6e1149efe41a15a025ce7c0c0481c5e7f) | 164,236 / 122,026 | 1.0100 | 1.0050 | 0.000123 ETH | success | 2 | batched stablecoin disbursement from a clone wallet with a hard-coded legacy gas price |
| 16 | [0xefb4…2c5b](https://basescan.org/tx/0xefb4cb5c399251f32102f7ccbe5ad3f3b6d71e594f3f8308eee8c62ede132c5b) | priority fee #3, total fee paid #1 | [0xb1e2…9019](https://basescan.org/address/0xb1e2c361cf6aca3d1dd5449ea5a1bfce96d89019) | [0x4a5c…d6c1](https://basescan.org/address/0x4a5c2f8edf362470b47735547e763f131e00d6c1) | 907,795 / 618,062 | 1.0050 | 1.0000 | 0.000621 ETH | success | 15 | buy ANYONE on Aerodrome and bridge it to Ethereum through LayerZero OFT in one transaction |

Repeated high-tip senders (three or more transactions at or above the chain P95 tip of 0.0147 gwei):

| Sender | High-tip txs | All txs in sample | Failed | Distinct destinations | Median tip (gwei) | Median gas limit | Top selectors | Examples |
|---|---:|---:|---:|---:|---:|---:|---|---|
| [0xe86f…cd5d](https://basescan.org/address/0xe86f1d3f2f52b7a0b9fdfcc614d060beed32cd5d) | 60 | 120 | 0 | 1 | 0.0248 | 260,000 | 0xc806a16e ×60 | [0x4553…4800](https://basescan.org/tx/0x45531b8fb50666bff381bab4ca9e0c6b94803d0f1cee75f516c1099e29474800) [0xab8e…93d5](https://basescan.org/tx/0xab8ee4dd267b902cd1e4cb4c1cd5dc04c9ecb41fcf547777931f78866b9393d5) [0x3acd…b25c](https://basescan.org/tx/0x3acd79bdb93475703421320a430fdb133a8f93fba23a5a9f3445d2e33368b25c) |
| [0x1f67…c957](https://basescan.org/address/0x1f6791653247bf9c8c09598e6b1a1aec3aaec957) | 60 | 60 | 0 | 1 | 0.0200 | 70,000 | 0x7b84f330 ×60 | [0xda2a…fb4e](https://basescan.org/tx/0xda2a7619a385c5a91af8c9e382f904f2cd1c955755ac93bb069757572813fb4e) [0x35d8…29a9](https://basescan.org/tx/0x35d8d01e654f9034b5f9b70c14dfa1d4424ba300f30bb8d60c48dd806aa529a9) [0x2425…b5f0](https://basescan.org/tx/0x24257b4987476fbe3a2cf6f9e49ab89eeb318463acf144176111dc176237b5f0) |
| [0x3304…566a](https://basescan.org/address/0x3304e22ddaa22bcdc5fca2269b418046ae7b566a) | 15 | 15 | 0 | 12 | 0.1150 | 84,000 | 0x ×8, 0xa9059cbb ×5, 0xb61d27f6 ×2 | [0x6dc4…be2b](https://basescan.org/tx/0x6dc49686232273eff1207bcab509b94bf774c8be1fecf4602e574482450abe2b) [0xfa16…6fc9](https://basescan.org/tx/0xfa16701f52ad8f0ab57c55fda306c245ce04cb2f240e8c6abb93415f85546fc9) [0x7b69…cdee](https://basescan.org/tx/0x7b69c7db6d3d9178b49514ed7dcf7ccadc846beb525d5271eb4883233ce7cdee) |
| [0xf9b6…af41](https://basescan.org/address/0xf9b6a1eb0190bf76274b0876957ee9f4f508af41) | 11 | 11 | 0 | 2 | 0.0460 | 500,000 | 0xcac88ea9 ×7, 0x04e45aaf ×4 | [0x144b…0df7](https://basescan.org/tx/0x144b9d5b57977ec5d1e4c361f5a069121f83beb86c02cb7e2f07332cf33d0df7) [0xe461…252d](https://basescan.org/tx/0xe4610a4134a8ba37119a6b2c8542054c8cafadb3fc6c03a9afda66bd8a84252d) [0xc953…9d24](https://basescan.org/tx/0xc95302e2780e3017e59aa751c0d6ac88f4c794ff09ef3d34b4b68c5b37609d24) |
| [0x575c…a4bf](https://basescan.org/address/0x575cf154924f07c10a74b46fecfeb02e8763a4bf) | 6 | 9 | 3 | 4 | 0.1450 | 550,000 | 0x3593564c ×3, 0x095ea7b3 ×1, 0xc04b8d59 ×1 | [0x7988…5c89](https://basescan.org/tx/0x7988aefc1e94faea7535ec6675fb0aa3543ad258312671367c28f739ac9a5c89) [0xef89…2d21](https://basescan.org/tx/0xef891b5dc73d6b65606c979f6120becedb85dbb21f138e6b88b37b63e2612d21) [0x5598…ed18](https://basescan.org/tx/0x55980311038662ea6c10578fcd63a453f46549c29e3c939a2f71886037f4ed18) |
| [0xbaed…439f](https://basescan.org/address/0xbaed383ede0e5d9d72430661f3285daa77e9439f) | 5 | 5 | 0 | 5 | 0.4000 | 90,000 | 0x ×3, 0xa9059cbb ×2 | [0x18ba…2958](https://basescan.org/tx/0x18ba33e3847a9e344b712f0ac418c6930d9c3e1ea894502e6299dd4723262958) [0x4af9…bcb8](https://basescan.org/tx/0x4af90a0a393b5f22397ddea08ab2c992f79970c59eeb9de9be80a37249d8bcb8) [0xb935…86f9](https://basescan.org/tx/0xb935b2e84214635f3545c4cce49f27503d586f4587ad50557697c02f90e086f9) |
| [0x4ac2…c6d7](https://basescan.org/address/0x4ac2c2b62fb70377cf5fa33b374157c16eb7c6d7) | 4 | 20 | 0 | 1 | 0.1082 | 600,002 | 0xa00597a0 ×4 | [0x3a3f…9ed4](https://basescan.org/tx/0x3a3f6674bfdedd7402be76cfbd74957801fa88ef8df714b59933b847ef149ed4) [0x0036…8c0f](https://basescan.org/tx/0x0036de2a0b5bd02653a83a9d72efaed35fc09a2d3f18af91e54931b249b78c0f) [0x43d3…4bf9](https://basescan.org/tx/0x43d32c5dd7be4f9cc41229c0ed060acd25adab5d1e2993ac64f7b985de004bf9) |
| [0xac64…5fb9](https://basescan.org/address/0xac6427822309e857b064a6636faf9f3e01c05fb9) | 4 | 4 | 0 | 2 | 0.0200 | 178,388 | 0x415a9735 ×2, 0xa9059cbb ×2 | [0x10bd…8f02](https://basescan.org/tx/0x10bd15a0d6582a8597ce4be06d43ce145cf2974862ad220cd9b4cd319e4a8f02) [0xfc78…4e1b](https://basescan.org/tx/0xfc78ae38a5f6e584864a36b9846f802d4e22188cc5c1d3965613eeaa00304e1b) [0x67d8…a75a](https://basescan.org/tx/0x67d81d135a6d0b00cd2237e64d12e512d5acf099414bbf6c704f6116ced2a75a) |

### Investigations

#### 10. [0x9e5f…046b](https://basescan.org/tx/0x9e5f7bd9211997b9ebcd99cc2c5b932d95d24ba3eb9e6342c022e207b594046b): scheduled keeper calling a per-id function with a fixed 2^24 gas limit

Facts: block 50,905,670 at 2026-09-05T09:31:27+00:00, position 98/121, type 0x2, success. Gas limit 16,777,216 (chain percentile 99.86), used 252,928. Effective price 0.006 gwei against base fee 0.005 gwei, so tip 0.001 gwei (percentile 36.5). Fee paid 0.000002 ETH (percentile 76.63). Value sent 0.000000 ETH. Destination is a contract. Selector `0xde09e7cf`, calldata 36 bytes, 3 logs.

Decoded event families: unknown ×3.

Interpretation (LLM, confidence low): The gas limit is exactly 16,777,216 (2^24), a client-library default, against about 253,000 used. The single uint256 argument (67,873 here; 67,832 and 67,872 in #11 and #13) indexes something, and the three logs record that id, the sender, a counter and a timestamp about 12 minutes ahead of the block, so each call opens or settles a timed round. The contract received 20 calls from 7 senders in the window without a failure, so several operators service it cooperatively. Nonce 132,369 and one call every few blocks say automation. Eleven transactions in the window share the 2^24 limit.

Unverified: protocol identity; none of the three event signatures is in the decoder.

#### 11. [0x49a7…0995](https://basescan.org/tx/0x49a7002c06db41e7b3ff150f76240162d9c269aeab1243a745282f1eea920995): scheduled keeper, second call (see #10)

Facts: block 50,905,673 at 2026-09-05T09:31:33+00:00, position 55/172, type 0x2, success. Gas limit 16,777,216 (chain percentile 99.86), used 254,908. Effective price 0.006 gwei against base fee 0.005 gwei, so tip 0.001 gwei (percentile 36.5). Fee paid 0.000002 ETH (percentile 76.7). Value sent 0.000000 ETH. Destination is a contract. Selector `0xde09e7cf`, calldata 36 bytes, 3 logs.

Decoded event families: unknown ×3.

Interpretation (LLM, confidence low): Second call of the same keeper as #10, id 67,832, same limit, tip and event shape.

Unverified: as #10.

#### 12. [0x3a3f…9ed4](https://basescan.org/tx/0x3a3f6674bfdedd7402be76cfbd74957801fa88ef8df714b59933b847ef149ed4): single-pool WETH to ZEN purchase by a bot with a price limit and a competitive tip

Facts: block 50,905,673 at 2026-09-05T09:31:33+00:00, position 77/172, type 0x2, success. Gas limit 600,002 (chain percentile 76.48), used 211,766. Effective price 1.2811 gwei against base fee 0.005 gwei, so tip 1.2761 gwei (percentile 99.99). Fee paid 0.000271 ETH (percentile 99.96). Value sent 0.000000 ETH. Destination is a contract. Selector `0xa00597a0`, calldata 199 bytes, 3 logs.

Decoded event families: ERC20_Transfer_shape ×2, V3Swap ×1. Distinct transfer recipients: 2.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: -1.875242 WETH; +637.944627 ZEN.

Interpretation (LLM, confidence medium): The 687-byte bot contract sells 1.875241 WETH for 637.94 ZEN in one concentrated-liquidity pool. Calldata carries the amount, a sqrtPrice limit close to the post-swap price, the pool address and a deadline about three minutes out. The 1.276 gwei tip is about 255 times the base fee and the highest on Base in the window, while the same sender's other 19 transactions in the window pay a median 0.0047 gwei. The bot bids high only for this opportunity, which is the behaviour of an arbitrageur competing for ordering, not a flat configuration.

Unverified: the other leg of the trade (an off-chain venue or another transaction); the pool is an EIP-1167 clone of 0xec8e…5831, which by memory is the Aerodrome Slipstream pool implementation.

#### 13. [0xc1de…a5d9](https://basescan.org/tx/0xc1decf57896945066db1abcd1a05abd9c51b54d67d7c2ca7bf789ff42ebda5d9): scheduled keeper, third call (see #10)

Facts: block 50,905,675 at 2026-09-05T09:31:37+00:00, position 89/128, type 0x2, success. Gas limit 16,777,216 (chain percentile 99.86), used 265,184. Effective price 0.006 gwei against base fee 0.005 gwei, so tip 0.001 gwei (percentile 36.5). Fee paid 0.000002 ETH (percentile 77.19). Value sent 0.000000 ETH. Destination is a contract. Selector `0xde09e7cf`, calldata 36 bytes, 3 logs.

Decoded event families: unknown ×3.

Interpretation (LLM, confidence low): Third call of the same keeper as #10, id 67,872.

Unverified: as #10.

#### 14. [0xcf71…1986](https://basescan.org/tx/0xcf71a3d29148de2e33c360bacd568fdba1695d6c88ad56a8e40e3d0fd94f1986): Aerodrome router swap USDC to WETH to DAG by a user with a flat 1 gwei tip

Facts: block 50,905,682 at 2026-09-05T09:31:51+00:00, position 1/125, type 0x2, success. Gas limit 900,000 (chain percentile 82.17), used 474,561. Effective price 1.0050 gwei against base fee 0.005 gwei, so tip 1.0000 gwei (percentile 99.91). Fee paid 0.000477 ETH (percentile 99.98). Value sent 0.000000 ETH. Destination is a contract. Selector `0xcac88ea9`, calldata 452 bytes, 11 logs.

Decoded event families: unknown ×6, ERC20_Transfer_shape ×5. Distinct transfer recipients: 5.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: -201.971344 USDC; +28543.272306 DAG.

Interpretation (LLM, confidence high): 201.97 USDC enters the USDC/WETH pool (0.6059 USDC fee to the pool fee contract), 0.0819 WETH moves to the WETH/DAG pool, and 28,543.27 DAG returns to the sender. The 1.0 gwei tip, about 200 times the base fee, at index 1 of the block looks like a wallet "fast" preset or a script; the account's only other transaction in the window (nonce 240) pays the same tip, so it is a setting rather than a bid for this trade.

Unverified: 0xcf77…4e43 as the Aerodrome Router is model memory; the swapExactTokensForTokens selector and the Fees, Sync and Swap event triplet on both pools match Velodrome-style pools. The tip's cause is inferred from the sender's other transaction.

#### 15. [0xa066…77cf](https://basescan.org/tx/0xa0667c13a15017a2e3e6bd2b465c38d484c2f8067c3fc8a2db0e17717f1077cf): batched stablecoin disbursement from a clone wallet with a hard-coded legacy gas price

Facts: block 50,905,689 at 2026-09-05T09:32:05+00:00, position 53/130, type 0x0, success. Gas limit 164,236 (chain percentile 47.27), used 122,026. Effective price 1.0100 gwei against base fee 0.005 gwei, so tip 1.0050 gwei (percentile 99.98). Fee paid 0.000123 ETH (percentile 99.85). Value sent 0.000000 ETH. Destination is a contract, an EIP-1167 minimal proxy to [0xcbfe…11bd](https://basescan.org/address/0xcbfe93b82207b0ea8b46b46432e372b86cf511bd). Selector `0x47e1da2a`, calldata 644 bytes, 2 logs.

Decoded event families: ERC20_Transfer_shape ×2. Distinct transfer recipients: 2.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: -2500.000000 cNGN.

Interpretation (LLM, confidence high): A legacy (type 0) transaction at 1.01 gwei calls a batch-transfer function with parallel arrays; the clone wallet (EIP-1167 to 0xcbfe…11bd) sends 2,495.95 cNGN to one address and 4.05 cNGN to another, a payout plus a fee of about 0.16 percent. The effective tip is about 201 times the base fee because a legacy transaction has no separate tip field; a backend that fixed 1.01 gwei long ago overpays on every block. No urgency is involved.

Unverified: operator identity; cNGN is the token's self-reported symbol.

#### 16. [0xefb4…2c5b](https://basescan.org/tx/0xefb4cb5c399251f32102f7ccbe5ad3f3b6d71e594f3f8308eee8c62ede132c5b): buy ANYONE on Aerodrome and bridge it to Ethereum through LayerZero OFT in one transaction

Facts: block 50,905,718 at 2026-09-05T09:33:03+00:00, position 1/162, type 0x2, success. Gas limit 907,795 (chain percentile 82.45), used 618,062. Effective price 1.0050 gwei against base fee 0.005 gwei, so tip 1.0000 gwei (percentile 99.96). Fee paid 0.000621 ETH (percentile 99.99). Value sent 0.000000 ETH. Destination is a contract. Selector `0xe587456a`, calldata 1,700 bytes, 15 logs.

Decoded event families: unknown ×10, ERC20_Transfer_shape ×5. Distinct transfer recipients: 4.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: +0.000000 ANYONE.

Interpretation (LLM, confidence high): The bot receives 0.169860 WETH, swaps it in the Aerodrome WETH/ANYONE pool for 2,722.97 ANYONE, then burns 2,722.969364 ANYONE to the zero address while the LayerZero endpoint (0x1a44…728c) emits a PacketSent-shaped event and the token emits an OFTSent-shaped event whose data carries destination endpoint id 30101. The bot keeps only dust. This is cross-chain inventory movement: buy where cheap, sell on the destination chain. The 1.0 gwei tip at index 1 and the largest fee on Base (0.000621 ETH) buy priority for the buy leg; the same EOA's previous transaction one block earlier paid 0.001 gwei.

Unverified: the WETH source 0x15b1…d013 (no flash-loan event, so probably the bot's own vault); that a matching sell occurs on Ethereum; the LayerZero EndpointV2 address and the PacketSent and OFTSent topics are model memory, and the destination id 30101 as Ethereum is from LayerZero's published endpoint table.

## Arbitrum

Not ranked by priority fee: no user transaction in this window exceeded the chain median, so a ranking would only reflect block order.

| # | Transaction | Selected for | From | To | Gas limit / used | Eff. price (gwei) | Tip (gwei) | Fee paid | Status | Logs | Mechanism (LLM) |
|---:|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| 17 | [0xde8d…e32d](https://arbiscan.io/tx/0xde8d2a775dfcc2bf918321e8030d5e48f0516faff2491938b30ce4ff9728e32d) | gas limit #2 (6 tied) | [0xfd58…65e7](https://arbiscan.io/address/0xfd581289a10e1a8c09bb0be6913a2856b21365e7) | [0x8080…def6](https://arbiscan.io/address/0x8080808080dab95efed788a9214e400ba552def6) | 32,000,000 / 835,159 | 0.0200 | 0 | 0.000017 ETH | success | 4 | automated keeper submitting batched operations with the 32M gas limit; identity unknown |
| 18 | [0x1b39…6a31](https://arbiscan.io/tx/0x1b396c2cb0e8516853aa590cd0ddd9a906f6a7e186e7d5b908cdcbaca5af6a31) | total fee paid #3 | [0x8e66…abbf](https://arbiscan.io/address/0x8e66ee36f2c7b9461f50aa0b53ef0e4e47f4abbf) | [0xa5d2…f4eb](https://arbiscan.io/address/0xa5d2d45228ee2e3a18ab122b2ce84997d008f4eb) | 31,902,895 / 3,433,790 | 0.0200 | 0 | 0.000069 ETH | success | 31 | GMX V2 keeper executing orders with Chainlink Data Streams price reports |
| 19 | [0x58b6…8140](https://arbiscan.io/tx/0x58b6cb0d71d2670293d188e252f82adbd0f426014fdd7a5c3e2fb1ee087f8140) | gas limit #3 (6 tied) | [0xfd58…65e7](https://arbiscan.io/address/0xfd581289a10e1a8c09bb0be6913a2856b21365e7) | [0x8080…def6](https://arbiscan.io/address/0x8080808080dab95efed788a9214e400ba552def6) | 32,000,000 / 159,453 | 0.0204 | 0 | 0.000003 ETH | success | 2 | automated keeper, lighter payload (see #17) |
| 20 | [0xb5ea…d2fb](https://arbiscan.io/tx/0xb5ead73120b4e0aa7e097bdda851a60488c30ec03f517cb060a876adbeead2fb) | gas limit #1 | [0xd499…d793](https://arbiscan.io/address/0xd499ec90377a7f797392bd4499eb2464ccf8d793) | [0x86be…43e3](https://arbiscan.io/address/0x86be76a0fa2bd3ecb69330cbb4fd1f62c48f43e3) | 100,001,242 / 124,454 | 0.0200 | 0 | 0.000002 ETH | success | 2 | Chainlink OCR2 transmit (oracle report) with a 100M gas limit |
| 21 | [0x5042…9da9](https://arbiscan.io/tx/0x50424772d6381d1536d79fae9aa7c21b52fa1d382990bba6ffa2dfa8c5cc9da9) | total fee paid #1 | [0x2218…cac5](https://arbiscan.io/address/0x2218482ceff6a899689dcf5dd45823d308dccac5) | [0x662a…b89c](https://arbiscan.io/address/0x662a623d4529a438c05e848b2723847af063b89c) | 8,000,000 / 4,754,135 | 0.0200 | 0 | 0.000095 ETH | success | 66 | Superfluid distribution-agreement interaction, likely a liquidity-mover call earning a small reward |
| 22 | [0xfddd…7432](https://arbiscan.io/tx/0xfdddfb85031d418d32a31def6f3dd126fcf07ad81b8229aa25f33693e1ec7432) | total fee paid #2 | [0xc539…3700](https://arbiscan.io/address/0xc539cb358a58ac67185baad4d5e3f7fcfc903700) | [0xa5d2…f4eb](https://arbiscan.io/address/0xa5d2d45228ee2e3a18ab122b2ce84997d008f4eb) | 31,903,635 / 4,503,288 | 0.0200 | 0 | 0.000090 ETH | success | 43 | GMX V2 keeper executing orders, second keeper (see #18) |

### Investigations

#### 17. [0xde8d…e32d](https://arbiscan.io/tx/0xde8d2a775dfcc2bf918321e8030d5e48f0516faff2491938b30ce4ff9728e32d): automated keeper submitting batched operations with the 32M gas limit; identity unknown

Facts: block 501,958,943 at 2026-09-05T09:31:47+00:00, position 4/5, type 0x2, success. Gas limit 32,000,000 (chain percentile 99.54), used 835,159. Effective price 0.0200 gwei against base fee 0.0200 gwei, so tip 0 gwei (percentile 0.0). Fee paid 0.000017 ETH (percentile 96.3). Value sent 0.000000 ETH. Destination is a contract. Selector `0x1e0a95af`, calldata 1,348 bytes, 4 logs.

Decoded event families: unknown ×4.

Interpretation (LLM, confidence low): Six transactions from one EOA (nonce above 1.08 million) to a 1,201-byte contract in six blocks, all with a 32,000,000 limit, using 155,000 to 835,000 gas. Two other 1,201-byte contracts emit alongside it, so the target is one of a set of identical instances. The logged key 0x7ebb…6da0 followed by 0x000002ffffff embeds an address and looks like a pool or order identifier. On Arbitrum the gas limit also covers the L1 data component, so the round 32M is a keeper convention rather than an estimate.

Unverified: everything beyond the mechanics; none of the four event signatures is in the decoder.

#### 18. [0x1b39…6a31](https://arbiscan.io/tx/0x1b396c2cb0e8516853aa590cd0ddd9a906f6a7e186e7d5b908cdcbaca5af6a31): GMX V2 keeper executing orders with Chainlink Data Streams price reports

Facts: block 501,959,024 at 2026-09-05T09:32:07+00:00, position 3/6, type 0x0, success. Gas limit 31,902,895 (chain percentile 99.4), used 3,433,790. Effective price 0.0200 gwei against base fee 0.0200 gwei, so tip 0 gwei (percentile 0.0). Fee paid 0.000069 ETH (percentile 99.8). Value sent 0.000000 ETH. Destination is a contract. Selector `0x7ebc83f7`, calldata 3,635 bytes, 31 logs.

Decoded event families: unknown ×27, ERC20_Transfer_shape ×4. Distinct transfer recipients: 3.

Interpretation (LLM, confidence high): A legacy transaction from a keeper (nonce 450,793) with a 31.9M gas limit. Three report-verification events keyed by 0x0003-prefixed feed ids come first, then three EventLog1 records carrying token addresses (WETH, USDC, a third market token), consistent with oracle price updates. A burst of EventLog1 and EventLog2 records keyed to account 0x947c…d2ad and order keys follows, and 147 USDC leaves the OrderVault to that account: an order executed with collateral or fee returned. Arbitrum charges no tip, so the fee rank is pure gas (3.43M).

Unverified: contract identities are model memory: EventEmitter 0xc8ee…22fb, OrderVault 0x31ef…40d5, the EventLog1 and EventLog2 topics, and the 0x0003-prefixed feed ids on emitter 0x2237…fb83 as Data Streams report verifications.

#### 19. [0x58b6…8140](https://arbiscan.io/tx/0x58b6cb0d71d2670293d188e252f82adbd0f426014fdd7a5c3e2fb1ee087f8140): automated keeper, lighter payload (see #17)

Facts: block 501,959,082 at 2026-09-05T09:32:22+00:00, position 1/3, type 0x2, success. Gas limit 32,000,000 (chain percentile 99.54), used 159,453. Effective price 0.0204 gwei against base fee 0.0204 gwei, so tip 0 gwei (percentile 0.0). Fee paid 0.000003 ETH (percentile 77.58). Value sent 0.000000 ETH. Destination is a contract. Selector `0x1e0a95af`, calldata 804 bytes, 2 logs.

Decoded event families: unknown ×2.

Interpretation (LLM, confidence low): Same keeper as #17 with a lighter payload (159,453 gas); the limit-to-used ratio of about 200 shows how little the limit says about the work.

Unverified: as #17.

#### 20. [0xb5ea…d2fb](https://arbiscan.io/tx/0xb5ead73120b4e0aa7e097bdda851a60488c30ec03f517cb060a876adbeead2fb): Chainlink OCR2 transmit (oracle report) with a 100M gas limit

Facts: block 501,959,099 at 2026-09-05T09:32:26+00:00, position 1/7, type 0x0, success. Gas limit 100,001,242 (chain percentile 99.93), used 124,454. Effective price 0.0200 gwei against base fee 0.0200 gwei, so tip 0 gwei (percentile 0.0). Fee paid 0.000002 ETH (percentile 58.6). Value sent 0.000000 ETH. Destination is a contract. Selector `0xb1dc65a4`, calldata 1,060 bytes, 2 logs.

Decoded event families: unknown ×2.

Interpretation (LLM, confidence high): The target emits Transmitted with config digest 0x00010bed… and epoch 0x4fcde, the signature of OCR2 report delivery. The 100,001,242 gas limit against 124,454 used (ratio about 803) is a node-side setting; Chainlink nodes on Arbitrum submit with very large limits because the L1 component of gas is uncertain. Legacy type, zero tip. The first log, from 0x1301…438c, records a value and a timestamp keyed by an indexed 61-bit number and is the payload consumer.

Unverified: which feed or product sits behind the two contracts; the transmit selector 0xb1dc65a4 and the Transmitted(configDigest, epoch) event are recognised from memory.

#### 21. [0x5042…9da9](https://arbiscan.io/tx/0x50424772d6381d1536d79fae9aa7c21b52fa1d382990bba6ffa2dfa8c5cc9da9): Superfluid distribution-agreement interaction, likely a liquidity-mover call earning a small reward

Facts: block 501,959,123 at 2026-09-05T09:32:32+00:00, position 3/5, type 0x2, success. Gas limit 8,000,000 (chain percentile 96.96), used 4,754,135. Effective price 0.0200 gwei against base fee 0.0200 gwei, so tip 0 gwei (percentile 0.0). Fee paid 0.000095 ETH (percentile 99.93). Value sent 0.000000 ETH. Destination is a contract. Selector `0xfe2f34f0`, calldata 2,308 bytes, 66 logs.

Decoded event families: unknown ×50, ERC20_Transfer_shape ×15, V3Swap ×1. Distinct transfer recipients: 10.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: +0.031448 USND; +0.000113 ETHx.

Interpretation (LLM, confidence medium): Both tokens emit ERC-777 Sent alongside every Transfer, which marks them as Superfluid super tokens (ETHx is Superfluid's wrapped native symbol). The caller's contract pulls 6.39 USND from one account and 0.0000972 ETHx from another, returns 0.226 USND, and the distribution-agreement contract updates pool memberships while the LI.FI Diamond (0x1231…4eae) executes a leg. The caller ends with +0.0314 USND and +0.000113 ETHx, the shape of a keeper bonus. 4.75M gas makes it the largest fee on Arbitrum (0.000095 ETH), with no tip because the chain has none.

Unverified: GDAv1 at 0x1e29…ba02 and the roles of 0x52f0…55cf and 0x7da6…3879 are model memory; the reward interpretation rests on the two small residual transfers to the caller.

#### 22. [0xfddd…7432](https://arbiscan.io/tx/0xfdddfb85031d418d32a31def6f3dd126fcf07ad81b8229aa25f33693e1ec7432): GMX V2 keeper executing orders, second keeper (see #18)

Facts: block 501,959,320 at 2026-09-05T09:33:21+00:00, position 3/6, type 0x0, success. Gas limit 31,903,635 (chain percentile 99.47), used 4,503,288. Effective price 0.0200 gwei against base fee 0.0200 gwei, so tip 0 gwei (percentile 0.0). Fee paid 0.000090 ETH (percentile 99.87). Value sent 0.000000 ETH. Destination is a contract. Selector `0x7ebc83f7`, calldata 4,755 bytes, 43 logs.

Decoded event families: unknown ×36, ERC20_Transfer_shape ×7. Distinct transfer recipients: 5.

Interpretation (LLM, confidence high): A different keeper EOA (nonce 811,501) executing orders through the same handler with 4.5M gas; four keeper EOAs called the handler in the window.

Unverified: as #18.

## Optimism

| # | Transaction | Selected for | From | To | Gas limit / used | Eff. price (gwei) | Tip (gwei) | Fee paid | Status | Logs | Mechanism (LLM) |
|---:|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| 23 | [0xaa91…1765](https://optimistic.etherscan.io/tx/0xaa91d3d3b93e1b3a4de882c84ca97d7ee1b9e93e71c060db0885111a48461765) | gas limit #1 (60 tied) | [0xd98d…8644](https://optimistic.etherscan.io/address/0xd98d3d712a5fbdfccfe149ff6905b7ccb4e98644) | [0x2a78…357e](https://optimistic.etherscan.io/address/0x2a783e166edb6c937ed28ab42a26cc796412357e) | 15,000,000 / 7,384,115 | 0.000001418 | 0.000000001 | 0.000000 ETH | success | 1 | deterministic heavy-compute call once per block, rotated across three wallets, at near-zero cost |
| 24 | [0x5a9b…f803](https://optimistic.etherscan.io/tx/0x5a9b3dd0255f1a335994fc8fef945a53fca7756d4a2e83c021bf12e9a56cf803) | gas limit #2 (60 tied) | [0x8a76…56ef](https://optimistic.etherscan.io/address/0x8a769fae92cb371f10fdfae931e2789a67fd56ef) | [0x2a78…357e](https://optimistic.etherscan.io/address/0x2a783e166edb6c937ed28ab42a26cc796412357e) | 15,000,000 / 7,384,115 | 0.00000142 | 0.000000001 | 0.000000 ETH | success | 1 | per-block compute loop, second wallet (see #23) |
| 25 | [0xb1d6…0de9](https://optimistic.etherscan.io/tx/0xb1d6213a2adc39db776068a1bce139ced7c55309edaeec6d8491c83f418c0de9) | gas limit #3 (60 tied) | [0x6b1c…4c17](https://optimistic.etherscan.io/address/0x6b1c1446d08034bd11ec1ec4ed28073415054c17) | [0x2a78…357e](https://optimistic.etherscan.io/address/0x2a783e166edb6c937ed28ab42a26cc796412357e) | 15,000,000 / 7,384,115 | 0.000001418 | 0.000000001 | 0.000000 ETH | success | 1 | per-block compute loop, third wallet (see #23) |
| 26 | [0x7081…3129](https://optimistic.etherscan.io/tx/0x708132e124e438307fa0a9a5426aeb479a67f7fa8487823dd216679b70f03129) | total fee paid #1 | [0xb428…3730](https://optimistic.etherscan.io/address/0xb42833d6edd1241474d33ea99906fd4cbe893730) | [0xac6b…e55e](https://optimistic.etherscan.io/address/0xac6bca0bb66d4587171cfc77b19e5e68f74de55e) | 4,371,790 / 2,799,365 | 0.005001415 | 0.005 | 0.000014 ETH | success | 9 | keeper-executed user withdrawal from a USDC vault, principal plus accrual |
| 27 | [0xa0c2…8ef3](https://optimistic.etherscan.io/tx/0xa0c2421f1da1388be1f3160c9e57a3cf1a99b43ae97adbc0a30945e226798ef3) | priority fee #1 | [0xacd0…435a](https://optimistic.etherscan.io/address/0xacd03d601e5bb1b275bb94076ff46ed9d753435a) | [0xee7a…4055](https://optimistic.etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) | 161,760 / 79,085 | 0.1001 | 0.1001 | 0.000008 ETH | success | 1 | high-volume payout operator moving USDC through a forwarder with a flat 0.1 gwei tip |
| 28 | [0x69a8…789d](https://optimistic.etherscan.io/tx/0x69a83902191326d9e101758be77bcde2d5fde7c6b18eb92d0dc84828d1da789d) | priority fee #3 | [0xacd0…435a](https://optimistic.etherscan.io/address/0xacd03d601e5bb1b275bb94076ff46ed9d753435a) | [0x94b0…8e58](https://optimistic.etherscan.io/address/0x94b008aa00579c1307b0ef2c499ad98a8ce58e58) | 70,220 / 34,750 | 0.1001 | 0.1001 | 0.000003 ETH | success | 1 | high-volume payout operator, direct USDT transfer (see #27) |
| 29 | [0x2ae6…0679](https://optimistic.etherscan.io/tx/0x2ae6f8fadb924d7ad30dc5c31bc7bd5037c2be2cc04c995cfc45f07d32360679) | priority fee #2 | [0xacd0…435a](https://optimistic.etherscan.io/address/0xacd03d601e5bb1b275bb94076ff46ed9d753435a) | [0xee7a…4055](https://optimistic.etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) | 196,182 / 96,161 | 0.1001 | 0.1001 | 0.000010 ETH | success | 1 | high-volume payout operator, USDC through the forwarder (see #27) |
| 30 | [0xfc98…6d6f](https://optimistic.etherscan.io/tx/0xfc98f6c0580d8e8f48b385625861ebfb90e49325efc8640095991af0ea776d6f) | total fee paid #3 | [0xdc45…4b46](https://optimistic.etherscan.io/address/0xdc45db93c3fc37272f40812bba9c4bad91344b46) | [0x7ca0…45f0](https://optimistic.etherscan.io/address/0x7ca0b75e67e33c0014325b739a8d019c4fe445f0) | 3,721,836 / 2,411,391 | 0.005001408 | 0.005 | 0.000012 ETH | success | 10 | keeper-executed user withdrawal, second keeper of the same system (see #26) |
| 31 | [0xf66e…8723](https://optimistic.etherscan.io/tx/0xf66e374921da17d8178587c18382d4cf7c1df003801085ef4b1abe36c6268723) | total fee paid #2 | [0xb428…3730](https://optimistic.etherscan.io/address/0xb42833d6edd1241474d33ea99906fd4cbe893730) | [0xac6b…e55e](https://optimistic.etherscan.io/address/0xac6bca0bb66d4587171cfc77b19e5e68f74de55e) | 4,371,753 / 2,792,112 | 0.00500141 | 0.005 | 0.000014 ETH | success | 9 | keeper-executed user withdrawal (see #26) |

Repeated high-tip senders (three or more transactions at or above the chain P95 tip of 0.008 gwei):

| Sender | High-tip txs | All txs in sample | Failed | Distinct destinations | Median tip (gwei) | Median gas limit | Top selectors | Examples |
|---|---:|---:|---:|---:|---:|---:|---|---|
| [0x9438…6cb9](https://optimistic.etherscan.io/address/0x94387751a464c073889ec2c0380519dc42f16cb9) | 60 | 120 | 0 | 1 | 0.0111 | 300,000 | 0xc806a16e ×60 | [0x492e…571f](https://optimistic.etherscan.io/tx/0x492e93ff94e55bf6d90e4d762fa49193513061bfee77c7940e17d7c5dfe8571f) [0x647d…5fa6](https://optimistic.etherscan.io/tx/0x647d9d6a444074db72e40c5158c3da7ba1c9847741baa6e1dc36776c1c985fa6) [0x5cc0…11b8](https://optimistic.etherscan.io/tx/0x5cc047444c0b68d93fc8b076ebd09de0c5435794467a193c928de8b25d7b11b8) |
| [0x33b1…c10b](https://optimistic.etherscan.io/address/0x33b12dd75f66933acd6438594d80cf91cacdc10b) | 4 | 4 | 0 | 1 | 0.0100 | 1,000,000 | 0x81002ee2 ×1, 0xc102132e ×1, 0xc1021330 ×1 | [0x12ad…b450](https://optimistic.etherscan.io/tx/0x12ad8e7ab97c839ba05380b8d44068dc36731905d91eae173f7d278e2d11b450) [0x29d1…f613](https://optimistic.etherscan.io/tx/0x29d15f6e39a29f59f0fd3018b0bc7ee02452eb3bcda89d2d63eb98f296f8f613) [0x539b…59a3](https://optimistic.etherscan.io/tx/0x539b30dbee7ce7946b7ad6825c595a862b3d67ba4d94d7aaac6aff527b9059a3) |
| [0xacd0…435a](https://optimistic.etherscan.io/address/0xacd03d601e5bb1b275bb94076ff46ed9d753435a) | 3 | 3 | 0 | 2 | 0.1001 | 161,760 | 0xb61d27f6 ×2, 0xa9059cbb ×1 | [0xa0c2…8ef3](https://optimistic.etherscan.io/tx/0xa0c2421f1da1388be1f3160c9e57a3cf1a99b43ae97adbc0a30945e226798ef3) [0x69a8…789d](https://optimistic.etherscan.io/tx/0x69a83902191326d9e101758be77bcde2d5fde7c6b18eb92d0dc84828d1da789d) [0x2ae6…0679](https://optimistic.etherscan.io/tx/0x2ae6f8fadb924d7ad30dc5c31bc7bd5037c2be2cc04c995cfc45f07d32360679) |
| [0x7812…fb88](https://optimistic.etherscan.io/address/0x78126dac3a2c08479d2196741da77f56ca8cfb88) | 3 | 3 | 2 | 1 | 0.0136 | 1,620,000 | 0x2f139e4f ×3 | [0x5792…7d22](https://optimistic.etherscan.io/tx/0x5792f6b861b51594a2ab0882745c04b6e51be82909a12ce2bc39dd2eda897d22) [0x7f73…85ac](https://optimistic.etherscan.io/tx/0x7f73ead544f95deaa9dad39fbc6dbeb36fa4c2e05a0b09b6c6f29e1498fb85ac) [0x0e38…9471](https://optimistic.etherscan.io/tx/0x0e38fb5586af3987c47ac9a9ebb23eb0e8cda298347fea390c9547712e739471) |

### Investigations

#### 23. [0xaa91…1765](https://optimistic.etherscan.io/tx/0xaa91d3d3b93e1b3a4de882c84ca97d7ee1b9e93e71c060db0885111a48461765): deterministic heavy-compute call once per block, rotated across three wallets, at near-zero cost

Facts: block 156,500,953 at 2026-09-05T09:31:23+00:00, position 11/28, type 0x2, success. Gas limit 15,000,000 (chain percentile 96.18), used 7,384,115. Effective price 0.000001418 gwei against base fee 0.000001417 gwei, so tip 0.000000001 gwei (percentile 0.0). Fee paid 0.000000 ETH (percentile 52.2). Value sent 0.000000 ETH. Destination is a contract. Selector `0x3eaf5d9f`, calldata 4 bytes, 1 log.

Decoded event families: unknown ×1.

Interpretation (LLM, confidence medium): The contract 0x2a78…357e received exactly 60 calls in the 60 Optimism blocks of the window from three EOAs taking turns (20 each, nonces near 92,000), every call using between 7,384,083 and 7,384,115 gas with a 15,000,000 limit and a priority fee of 1 wei. The base fee is about 1,400 wei, so 7.4M gas costs about 1e10 wei, and with the L1 data fee the whole call costs about 0.00000001 ETH. A fixed loop of this size repeated every block by a wallet rotation is the signature of on-chain "mining" or gas-farming schemes that exploit near-free L2 execution. Gas-limit ranking surfaces it; fee ranking never would.

Unverified: what the contract computes; the single event (block number, 1, -9791, 7576515) is not decoded.

#### 24. [0x5a9b…f803](https://optimistic.etherscan.io/tx/0x5a9b3dd0255f1a335994fc8fef945a53fca7756d4a2e83c021bf12e9a56cf803): per-block compute loop, second wallet (see #23)

Facts: block 156,500,954 at 2026-09-05T09:31:25+00:00, position 9/22, type 0x2, success. Gas limit 15,000,000 (chain percentile 96.18), used 7,384,115. Effective price 0.00000142 gwei against base fee 0.000001419 gwei, so tip 0.000000001 gwei (percentile 0.0). Fee paid 0.000000 ETH (percentile 53.09). Value sent 0.000000 ETH. Destination is a contract. Selector `0x3eaf5d9f`, calldata 4 bytes, 1 log.

Decoded event families: unknown ×1.

Interpretation (LLM, confidence medium): Second wallet of the rotation described in #23; identical gas usage.

Unverified: as #23.

#### 25. [0xb1d6…0de9](https://optimistic.etherscan.io/tx/0xb1d6213a2adc39db776068a1bce139ced7c55309edaeec6d8491c83f418c0de9): per-block compute loop, third wallet (see #23)

Facts: block 156,500,955 at 2026-09-05T09:31:27+00:00, position 10/25, type 0x2, success. Gas limit 15,000,000 (chain percentile 96.18), used 7,384,115. Effective price 0.000001418 gwei against base fee 0.000001417 gwei, so tip 0.000000001 gwei (percentile 0.0). Fee paid 0.000000 ETH (percentile 52.2). Value sent 0.000000 ETH. Destination is a contract. Selector `0x3eaf5d9f`, calldata 4 bytes, 1 log.

Decoded event families: unknown ×1.

Interpretation (LLM, confidence medium): Third wallet of the rotation described in #23.

Unverified: as #23.

#### 26. [0x7081…3129](https://optimistic.etherscan.io/tx/0x708132e124e438307fa0a9a5426aeb479a67f7fa8487823dd216679b70f03129): keeper-executed user withdrawal from a USDC vault, principal plus accrual

Facts: block 156,500,963 at 2026-09-05T09:31:43+00:00, position 8/29, type 0x2, success. Gas limit 4,371,790 (chain percentile 91.78), used 2,799,365. Effective price 0.005001415 gwei against base fee 0.000001415 gwei, so tip 0.005 gwei (percentile 86.68). Fee paid 0.000014 ETH (percentile 99.94). Value sent 0.000000 ETH. Destination is a contract. Selector `0x34246468`, calldata 3,748 bytes, 9 logs. Same sender also at block positions 22.

Decoded event families: unknown ×7, ERC20_Transfer_shape ×2. Distinct transfer recipients: 2.

Interpretation (LLM, confidence medium): The keeper (nonce 1,437,900; 21 transactions in the window) calls a tiny entry contract with 3,748 bytes of calldata. A pool contract updates an index and sends 0.477892 USDC to an intermediary, which forwards it to user 0x4344…39c2; paired events record 477,487 then 477,892 units, so the user recovered a principal plus about 0.08 percent. A registry emits a completion record with a timestamp. The fee comes from 2.8M gas at a 0.005 gwei tip, several thousand times the base fee; the L1 data fee is negligible here. A second keeper for the same system (#30) sent 107 transactions in the window, about 7 percent of all user transactions on Optimism.

Unverified: protocol identity; the 122-byte entry contract and the 1,419-byte pool contracts have no registered signatures, and the 3.7 KB calldata (presumably a signed request plus oracle data) was not decoded.

#### 27. [0xa0c2…8ef3](https://optimistic.etherscan.io/tx/0xa0c2421f1da1388be1f3160c9e57a3cf1a99b43ae97adbc0a30945e226798ef3): high-volume payout operator moving USDC through a forwarder with a flat 0.1 gwei tip

Facts: block 156,500,968 at 2026-09-05T09:31:53+00:00, position 21/26, type 0x2, success. Gas limit 161,760 (chain percentile 16.32), used 79,085. Effective price 0.1001 gwei against base fee 0.000001411 gwei, so tip 0.1001 gwei (percentile 99.94). Fee paid 0.000008 ETH (percentile 98.92). Value sent 0.000000 ETH. Destination is a contract. Selector `0xb61d27f6`, calldata 228 bytes, 1 log.

Decoded event families: ERC20_Transfer_shape ×1.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: -34638.030000 USDC.

Interpretation (LLM, confidence high): The EOA's nonce is 8,245,120, one of the highest in the sample, and it sends through a 209-byte forwarder with execute(token, value, data): 34,638.03 USDC here, 500 USDC in #29, and a direct 46,488.91 USDT transfer in #28, all within one minute. The 0.1001 gwei tip is identical across the three and about nine times the chain P99; the total cost is 0.000008 ETH. The outlier is a configuration choice by an exchange-style withdrawal system, not competition.

Unverified: operator identity.

#### 28. [0x69a8…789d](https://optimistic.etherscan.io/tx/0x69a83902191326d9e101758be77bcde2d5fde7c6b18eb92d0dc84828d1da789d): high-volume payout operator, direct USDT transfer (see #27)

Facts: block 156,500,991 at 2026-09-05T09:32:39+00:00, position 26/31, type 0x2, success. Gas limit 70,220 (chain percentile 6.76), used 34,750. Effective price 0.1001 gwei against base fee 0.000001409 gwei, so tip 0.1001 gwei (percentile 99.81). Fee paid 0.000003 ETH (percentile 92.22). Value sent 0.000000 ETH. Destination is a contract. Selector `0xa9059cbb`, calldata 68 bytes, 1 log.

Decoded event families: ERC20_Transfer_shape ×1.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: -46488.908640 USDT.

Interpretation (LLM, confidence high): Same operator as #27, a direct transfer of 46,488.91 USDT from the EOA.

Unverified: as #27.

#### 29. [0x2ae6…0679](https://optimistic.etherscan.io/tx/0x2ae6f8fadb924d7ad30dc5c31bc7bd5037c2be2cc04c995cfc45f07d32360679): high-volume payout operator, USDC through the forwarder (see #27)

Facts: block 156,500,998 at 2026-09-05T09:32:53+00:00, position 18/25, type 0x2, success. Gas limit 196,182 (chain percentile 16.57), used 96,161. Effective price 0.1001 gwei against base fee 0.000001409 gwei, so tip 0.1001 gwei (percentile 99.87). Fee paid 0.000010 ETH (percentile 99.04). Value sent 0.000000 ETH. Destination is a contract. Selector `0xb61d27f6`, calldata 228 bytes, 1 log.

Decoded event families: ERC20_Transfer_shape ×1.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: -500.000000 USDC.

Interpretation (LLM, confidence high): Same operator as #27, 500 USDC through the forwarder.

Unverified: as #27.

#### 30. [0xfc98…6d6f](https://optimistic.etherscan.io/tx/0xfc98f6c0580d8e8f48b385625861ebfb90e49325efc8640095991af0ea776d6f): keeper-executed user withdrawal, second keeper of the same system (see #26)

Facts: block 156,501,008 at 2026-09-05T09:33:13+00:00, position 8/28, type 0x2, success. Gas limit 3,721,836 (chain percentile 91.59), used 2,411,391. Effective price 0.005001408 gwei against base fee 0.000001408 gwei, so tip 0.005 gwei (percentile 86.68). Fee paid 0.000012 ETH (percentile 99.81). Value sent 0.000000 ETH. Destination is a contract. Selector `0x4e309099`, calldata 708 bytes, 10 logs. Same sender also at block positions 2.

Decoded event families: unknown ×7, ERC20_Transfer_shape ×3. Distinct transfer recipients: 3.

Interpretation (LLM, confidence medium): A second entry contract of the same 122-byte shape, called by a keeper whose nonce is 5,526,818 and which sent 107 transactions in the window. User 0xd5cf…9d3a receives 30.485989 USDC out of the pool (recorded as 30,404,957 then 30,485,989 units) plus 0.914579 USDC from a separate fund, and the registry logs a request id with status 1. Two keepers and two entry points serving the same pools suggest a large automated service with sharded submitters.

Unverified: as #26.

#### 31. [0xf66e…8723](https://optimistic.etherscan.io/tx/0xf66e374921da17d8178587c18382d4cf7c1df003801085ef4b1abe36c6268723): keeper-executed user withdrawal (see #26)

Facts: block 156,501,010 at 2026-09-05T09:33:17+00:00, position 8/27, type 0x2, success. Gas limit 4,371,753 (chain percentile 91.71), used 2,792,112. Effective price 0.00500141 gwei against base fee 0.00000141 gwei, so tip 0.005 gwei (percentile 86.68). Fee paid 0.000014 ETH (percentile 99.87). Value sent 0.000000 ETH. Destination is a contract. Selector `0x34246468`, calldata 3,748 bytes, 9 logs.

Decoded event families: unknown ×7, ERC20_Transfer_shape ×2. Distinct transfer recipients: 2.

Interpretation (LLM, confidence medium): Same keeper and entry contract as #26, for user 0x525b…2041 per calldata, 2.79M gas.

Unverified: as #26.

## Polygon

| # | Transaction | Selected for | From | To | Gas limit / used | Eff. price (gwei) | Tip (gwei) | Fee paid | Status | Logs | Mechanism (LLM) |
|---:|---|---|---|---|---:|---:|---:|---:|---|---:|---|
| 32 | [0xcdff…40d2](https://polygonscan.com/tx/0xcdff86da13662b15b57190e07bf9feb39a12117ba3224b39f53bff19b4c040d2) | priority fee #3 | [0xdffc…a880](https://polygonscan.com/address/0xdffc80f1edcaac53bede97b47527ef13a81da880) | [0x3c49…3359](https://polygonscan.com/address/0x3c499c542cef5e3811e1192ce70d8cc03d5c3359) | 100,000 / 60,191 | 5000.0000 | 4753.4386 | 0.300955 POL | success | 2 | payout wallet with a flat 5,000 gwei gas price taking position 0 in the block |
| 33 | [0x9c20…8d8f](https://polygonscan.com/tx/0x9c20b2dd35f34f7d0231de40488a53f414086661b675e22057f9d13787bd8d8f) | gas limit #1 (4 tied) | [0xbce3…6eb8](https://polygonscan.com/address/0xbce303a32d4b067d53a3e743ed1f22890e976eb8) | [0xd216…f494](https://polygonscan.com/address/0xd216153c06e857cd7f72665e0af1d7d82172f494) | 32,000,000 / 2,560,472 | 324.5614 | 78.0000 | 0.831030 POL | success | 48 | Polymarket relayer executing a neg-risk position conversion through a user's proxy wallet |
| 34 | [0xb03a…ff62](https://polygonscan.com/tx/0xb03af3867ed43d01081c76feb2e80282b874ec13a207b7f51b5cdcb70e57ff62) | priority fee #2 | [0x9f3d…a212](https://polygonscan.com/address/0x9f3d8b0d320deafe327f1eda5cfa20b98966a212) | [0x9f3d…a212](https://polygonscan.com/address/0x9f3d8b0d320deafe327f1eda5cfa20b98966a212) | 99,234 / 46,000 | 11188.7231 | 10939.8604 | 0.514681 POL | success | 1 | relayer submitting EIP-7702 delegations for another account with escalating gas in one block |
| 35 | [0x2878…1289](https://polygonscan.com/tx/0x2878e165fd31899d635a20993722463f59826ca539d1da651f6835e963e71289) | priority fee #1, total fee paid #1 | [0xd9d8…05fc](https://polygonscan.com/address/0xd9d8a147a13aa1a1785a0098ae97554743c905fc) | [0x94f7…6faf](https://polygonscan.com/address/0x94f7ef03ec6b2028bf80facabf8c997bfde36faf) | 400,000 / 304,895 | 88175.3945 | 87924.0000 | 26.884237 POL | success | 4 | race to be first proposer on a UMA Optimistic Oracle YES_OR_NO_QUERY request, 750 USDC.e bond |
| 36 | [0x1db4…6277](https://polygonscan.com/tx/0x1db46a66979eab538e967f35460dfcd6b4645fde58b2f61d68d54d5660de6277) | gas limit #2 (4 tied), total fee paid #2 | [0x0b49…5193](https://polygonscan.com/address/0x0b49b3a41283bb78ebac770e7d31473b80ba5193) | [0xd216…f494](https://polygonscan.com/address/0xd216153c06e857cd7f72665e0af1d7d82172f494) | 32,000,000 / 21,069,094 | 406.4541 | 155.9920 | 8.563620 POL | success | 2 | relayed call through the Polymarket hub consuming 21M gas with no visible effect |
| 37 | [0xdc69…1c67](https://polygonscan.com/tx/0xdc691e350bf76d74ace1f96ae775664d386bcc3f35a99c33a0634a2783931c67) | gas limit #3 (4 tied) | [0x5eea…6cf3](https://polygonscan.com/address/0x5eeab5b61e31e187c66b972bde786712ecc06cf3) | [0xd216…f494](https://polygonscan.com/address/0xd216153c06e857cd7f72665e0af1d7d82172f494) | 32,000,000 / 1,898,820 | 414.5390 | 162.6960 | 0.787135 POL | success | 42 | Polymarket relayer executing a neg-risk position conversion (see #33) |
| 38 | [0x9147…059f](https://polygonscan.com/tx/0x91478029cafd0fe49804d92526cd4a56d7125dc02695782958006d9c18fc059f) | total fee paid #3 | [0x8882…f27d](https://polygonscan.com/address/0x8882fa54c206a438dec70b6bc3811fac6282f27d) | [0xca11…ca11](https://polygonscan.com/address/0xca11bde05977b3631167028862be2a173976ca11) | 13,584,931 / 10,362,493 | 309.8022 | 60.4422 | 3.210323 POL | success | 1087 | Multicall3 batch of 155 unstake-and-forward operations consolidating LGNS to one recipient |

Repeated high-tip senders (three or more transactions at or above the chain P95 tip of 400.0000 gwei):

| Sender | High-tip txs | All txs in sample | Failed | Distinct destinations | Median tip (gwei) | Median gas limit | Top selectors | Examples |
|---|---:|---:|---:|---:|---:|---:|---|---|
| [0x1c62…6894](https://polygonscan.com/address/0x1c62a58a11d88d71f936e0ee799eaebd74546894) | 75 | 75 | 0 | 75 | 494.7000 | 21,000 | 0x ×75 | [0xc188…9655](https://polygonscan.com/tx/0xc188e23fab2a442ee51a61d605bdcbaacd7f4ca3b969d4cc074196edf8499655) [0xaf13…213b](https://polygonscan.com/tx/0xaf1359e6f521b9946133398eb6fcf6b8866cd6a223302e72fc11622830f4213b) [0xcbf6…b1bf](https://polygonscan.com/tx/0xcbf682cfe1c0cd8d008f059d9cd0d02c67c1d463af8db7122e165d7fcb0bb1bf) |
| [0xccec…2f99](https://polygonscan.com/address/0xccec50fdab5bc3e75d969183266e8904fe2b2f99) | 26 | 26 | 0 | 1 | 805.0000 | 21,000 | 0x ×26 | [0x3f0f…9c72](https://polygonscan.com/tx/0x3f0f3db9ae1d1ee6340a4db63b70d25c3f1e58ef21e94fcc7d24fc375d509c72) [0xc7bc…5f11](https://polygonscan.com/tx/0xc7bc2c0b85c6ecd32fff2379cd221b99b78c7ab6db9bc6db62c461dbcbf85f11) [0xb856…3ee5](https://polygonscan.com/tx/0xb856af973532049809127121264fb6e835cda7b8ee6d08dca62a0e82666c3ee5) |
| [0xf0f8…4e10](https://polygonscan.com/address/0xf0f8a97a37460d18ab3f0557569a2d72b1844e10) | 26 | 26 | 0 | 1 | 805.0000 | 21,000 | 0x ×26 | [0x5d11…1bb8](https://polygonscan.com/tx/0x5d11227b3c4843e00636aa25dfbf1f73db031953c84bec888f9c2d0f4e751bb8) [0x04a9…8a64](https://polygonscan.com/tx/0x04a94252c91ac9bb25077f0e5917bfd6ad55a0693d242034221b9bf776f88a64) [0x8d4f…783a](https://polygonscan.com/tx/0x8d4f013f6256ef6e227e8dcb7841591c426edbfde8ecbdebde0a9ccd5d3a783a) |
| [0x343d…749a](https://polygonscan.com/address/0x343d752bb710c5575e417edb3f9fa06241a4749a) | 21 | 21 | 0 | 1 | 924.3220 | 420,000 | 0xa9059cbb ×21 | [0x15d2…c4f2](https://polygonscan.com/tx/0x15d24bc69c7eccc06aa892ced7c79118efe2e39031bc7de736de742dcfbec4f2) [0x6131…ec04](https://polygonscan.com/tx/0x6131bdad0d523898199ca864e83429572c63ef5d11ec13cac53e113486e3ec04) [0xaaf1…a2dd](https://polygonscan.com/tx/0xaaf14f790052630e487953b2eb677bbaa80dc388a4765950b4379bb1b79fa2dd) |
| [0xeba3…65f4](https://polygonscan.com/address/0xeba33d81583ac30eab08a3f457edd58daa8065f4) | 19 | 30 | 0 | 1 | 488.0880 | 200,000 | 0xf3c91c83 ×19 | [0xe923…456b](https://polygonscan.com/tx/0xe923aadbb7a4333b57db26dc4fb7496e5ec7dce2be152a9476133a70fa26456b) [0x792f…8284](https://polygonscan.com/tx/0x792f1d3674c93bde19ec457510e1a14eda43f7fcf3540a7bcb338298ae7f8284) [0x6cff…0bd3](https://polygonscan.com/tx/0x6cffbd64d519ad7b71816554341291fd7f202bd8ff04b70d606ea2372b920bd3) |
| [0x501c…5646](https://polygonscan.com/address/0x501c43b2510da0ca6572e05b479e530ce3985646) | 16 | 24 | 0 | 15 | 963.4932 | 21,000 | 0x ×16 | [0xa3c3…2e5f](https://polygonscan.com/tx/0xa3c351bbba0891aa8fd74f5a85105f5ff43819da323fd9193e84cd7bbfe02e5f) [0xdfc1…bf6d](https://polygonscan.com/tx/0xdfc1f1ed200727dae5cf4a54991285e0b90c17b572c3cbec50e00cdc9027bf6d) [0xe4d6…a642](https://polygonscan.com/tx/0xe4d6e1f746b34f03cedd6e4b1f7a842c67a6134891ebe9459fad8c7cd983a642) |
| [0x0570…16c9](https://polygonscan.com/address/0x057089e02e1781016c882d682729c84352fd16c9) | 7 | 15 | 7 | 1 | 439.0910 | 65,000 | 0xa9059cbb ×7 | [0x1ea8…8403](https://polygonscan.com/tx/0x1ea89c8dffb734269eb6f2236dfa0d4a24ab4738e2a434d34c43c25a68848403) [0xc0a2…8d04](https://polygonscan.com/tx/0xc0a24eaac344dfab5e358c257eec5b7f1c7a8877077a1c98ff036c29ceb88d04) [0x00f8…38e8](https://polygonscan.com/tx/0x00f8f7f9227def48fee02aed281765c6ee2b8f9ab3d2935d40058ca5e24738e8) |
| [0xbaff…51d7](https://polygonscan.com/address/0xbaff6cfecfcb282e9177f1fff9047be7321851d7) | 7 | 8 | 0 | 1 | 497.7840 | 600,000 | 0x68c7450f ×7 | [0xa219…de40](https://polygonscan.com/tx/0xa2196218bfb54b552135ab5cf2b48263293a1a6e26915bd02aaffc06574ade40) [0x34fb…5715](https://polygonscan.com/tx/0x34fb2bf7b3ca52b7ce5741b5670d3336c0f322a0fbbd5e65905c9c7d6bc75715) [0xf895…26fb](https://polygonscan.com/tx/0xf8957d404c00f8638d7f9554eb501e93292b0e2f247aa35255f8d2299ec126fb) |

### Investigations

#### 32. [0xcdff…40d2](https://polygonscan.com/tx/0xcdff86da13662b15b57190e07bf9feb39a12117ba3224b39f53bff19b4c040d2): payout wallet with a flat 5,000 gwei gas price taking position 0 in the block

Facts: block 93,263,767 at 2026-09-05T09:31:24+00:00, position 0/99, type 0x2, success. Gas limit 100,000 (chain percentile 24.45), used 60,191. Effective price 5000.0000 gwei against base fee 246.5614 gwei, so tip 4753.4386 gwei (percentile 99.97). Fee paid 0.300955 POL (percentile 94.19). Value sent 0.000000 POL. Destination is a contract. Selector `0xa9059cbb`, calldata 68 bytes, 2 logs.

Decoded event families: ERC20_Transfer_shape ×1, Polygon_native_fee_log ×1.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: -47.230000 USDC.

Interpretation (LLM, confidence high): A 47.23 USDC (native) transfer, 60,191 gas, effective price 5,000 gwei against a 246.6 gwei base fee, landing at index 0. Polygon validators order by gas price, so a flat 5,000 gwei guarantees the top slot for 0.30 POL. The sender's three transactions in the window all pay the same tip, and its nonce (757,875) says a payout system. Polygon's high nominal gwei culture appears throughout the repeat-sender table: many 21,000-gas transfers at 400 to 960 gwei.

Unverified: operator identity.

#### 33. [0x9c20…8d8f](https://polygonscan.com/tx/0x9c20b2dd35f34f7d0231de40488a53f414086661b675e22057f9d13787bd8d8f): Polymarket relayer executing a neg-risk position conversion through a user's proxy wallet

Facts: block 93,263,767 at 2026-09-05T09:31:24+00:00, position 65/99, type 0x2, success. Gas limit 32,000,000 (chain percentile 99.96), used 2,560,472. Effective price 324.5614 gwei against base fee 246.5614 gwei, so tip 78.0000 gwei (percentile 20.33). Fee paid 0.831030 POL (percentile 98.38). Value sent 0.000000 POL. Destination is a contract. Selector `0x405cec67`, calldata 900 bytes, 48 logs.

Decoded event families: ERC1155TransferBatch ×16, ERC20_Transfer_shape ×16, unknown ×15, Polygon_native_fee_log ×1. Distinct transfer recipients: 6.

Interpretation (LLM, confidence high): Calldata names a user proxy wallet and Polymarket's proxy wallet factory; the relayer EOA (nonce 567,461) pays gas so the user does not. Inside, 110 WCOL are minted to the NegRiskAdapter and split ten at a time into 11 conditions of one neg-risk market (11 PositionSplit events, 16 ERC-1155 batch transfers), which is how converting NO positions across questions into YES positions and collateral works. The 32,000,000 gas limit is the relayer fleet setting: the hub received 120 relayed calls from 70 relayer EOAs in the window, median 288,000 gas.

Unverified: the relay-hub role of 0xd216…f494 is inferred from the call shape (user proxy and the proxy wallet factory 0xab45…4052 in calldata) and from the TransactionRelayed-shaped event; ConditionalTokens 0x4d97…6045, NegRiskAdapter 0xd91e…5296 and the PositionSplit topic are model memory.

#### 34. [0xb03a…ff62](https://polygonscan.com/tx/0xb03af3867ed43d01081c76feb2e80282b874ec13a207b7f51b5cdcb70e57ff62): relayer submitting EIP-7702 delegations for another account with escalating gas in one block

Facts: block 93,263,781 at 2026-09-05T09:31:45+00:00, position 75/113, type 0x4, success. Gas limit 99,234 (chain percentile 24.37), used 46,000. Effective price 11188.7231 gwei against base fee 248.8626 gwei, so tip 10939.8604 gwei (percentile 99.98). Fee paid 0.514681 POL (percentile 97.61). Value sent 0.000000 POL. Destination is an EOA. Selector `0x`, calldata 0 bytes, 1 log. Same sender also at block positions 74, 76, 77, 78, 79.

Decoded event families: Polygon_native_fee_log ×1.

Interpretation (LLM, confidence high): A type-4 transaction with one authorization: delegate to 0xe965…db7c, authority nonce 218,162, so the authority is a different, well-used account rather than the sender (sender nonce 62,956). Gas used 46,000 equals 21,000 plus a 25,000 authorization charge. The sender submitted six such transactions in this single block (positions 74 to 79), four of which failed, with tips between roughly 160 and 10,940 gwei. Authorizations take effect even when execution reverts, so the repeats and the gas escalation look like a race to install or replace a delegation on a contested account, the pattern seen when a leaked key is fought over by sweeper bots. Polygon had 192 type-4 transactions in the window; the top delegate target (0xf5a7…8bfe, 89 authorizations from three relayers) is the same helper contract called 155 times in #38.

Unverified: the authority address behind the authorization (needs signature recovery); who controls delegate target 0xe965…db7c; the reason four of the six attempts reverted.

#### 35. [0x2878…1289](https://polygonscan.com/tx/0x2878e165fd31899d635a20993722463f59826ca539d1da651f6835e963e71289): race to be first proposer on a UMA Optimistic Oracle YES_OR_NO_QUERY request, 750 USDC.e bond

Facts: block 93,263,782 at 2026-09-05T09:31:46+00:00, position 0/126, type 0x2, success. Gas limit 400,000 (chain percentile 50.87), used 304,895. Effective price 88175.3945 gwei against base fee 251.3945 gwei, so tip 87924.0000 gwei (percentile 99.99). Fee paid 26.884237 POL (percentile 99.99). Value sent 0.000000 POL. Destination is a contract. Selector `0xcaf8e6fc`, calldata 676 bytes, 4 logs.

Decoded event families: Approval ×1, ERC20_Transfer_shape ×1, Polygon_native_fee_log ×1, unknown ×1.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): destination: -750.000000 USDC.

Interpretation (LLM, confidence high): The event data begins with the bytes of "YES_OR_NO_QUERY", UMA's identifier for Polymarket resolutions, followed by a request timestamp of 2026-09-03 20:44:31 UTC and ancillary data. The proposer contract moves exactly 750 USDC.e into the oracle contract as the proposal bond. The sender paid 88,175 gwei per gas (tip 87,924 gwei, about 350 times the base fee), 26.88 POL in total, to take index 0 of the block. Only the first valid proposal earns the proposer reward, so proposers bid for the top slot the moment a market becomes resolvable. This is the largest fee on Polygon in the window by a factor of three.

Unverified: 0x2c03…58b1 as an Optimistic Oracle proxy and 0x6507…f2a7 as a Polymarket adapter are inferred; the proposed answer and the market question inside the 2 KB ancillary data were not decoded; the 750 USDC bond as Polymarket's standard is model memory.

#### 36. [0x1db4…6277](https://polygonscan.com/tx/0x1db46a66979eab538e967f35460dfcd6b4645fde58b2f61d68d54d5660de6277): relayed call through the Polymarket hub consuming 21M gas with no visible effect

Facts: block 93,263,799 at 2026-09-05T09:32:12+00:00, position 25/81, type 0x2, success. Gas limit 32,000,000 (chain percentile 99.96), used 21,069,094. Effective price 406.4541 gwei against base fee 250.4621 gwei, so tip 155.9920 gwei (percentile 57.4). Fee paid 8.563620 POL (percentile 99.98). Value sent 0.000000 POL. Destination is a contract. Selector `0x405cec67`, calldata 900 bytes, 2 logs.

Decoded event families: Polygon_native_fee_log ×1, unknown ×1.

Interpretation (LLM, confidence low): Same relayer hub as #33 and #37, but 21,069,094 gas produced a single hub event (relayer, user proxy 0x91e2…3e62, factory, inner selector 0x34ee9791, status 0, charge 1) and nothing else. Among the hub's 120 relayed calls in the window this is the only one above 10M gas (median 288,000). Either the inner operation is a heavy computation without events, or the inner call exhausted its gas and the hub swallowed the failure while the outer transaction reports success. 8.56 POL was spent. A transaction trace is the cheapest next query.

Unverified: whether the inner call reverted; the TransactionRelayed-shaped status word reads 0, which in GSN-style hubs means success, yet no state-changing events were emitted.

#### 37. [0xdc69…1c67](https://polygonscan.com/tx/0xdc691e350bf76d74ace1f96ae775664d386bcc3f35a99c33a0634a2783931c67): Polymarket relayer executing a neg-risk position conversion (see #33)

Facts: block 93,263,802 at 2026-09-05T09:32:16+00:00, position 39/96, type 0x2, success. Gas limit 32,000,000 (chain percentile 99.96), used 1,898,820. Effective price 414.5390 gwei against base fee 251.8430 gwei, so tip 162.6960 gwei (percentile 64.76). Fee paid 0.787135 POL (percentile 98.3). Value sent 0.000000 POL. Destination is a contract. Selector `0x405cec67`, calldata 900 bytes, 42 logs.

Decoded event families: ERC1155TransferBatch ×14, ERC20_Transfer_shape ×14, unknown ×13, Polygon_native_fee_log ×1. Distinct transfer recipients: 6.

Interpretation (LLM, confidence high): Same relayer hub and operation as #33 for another user proxy (0x11d7…6db): 14 batch transfers, 9 PositionSplits, 1.9M gas.

Unverified: as #33.

#### 38. [0x9147…059f](https://polygonscan.com/tx/0x91478029cafd0fe49804d92526cd4a56d7125dc02695782958006d9c18fc059f): Multicall3 batch of 155 unstake-and-forward operations consolidating LGNS to one recipient

Facts: block 93,263,812 at 2026-09-05T09:32:31+00:00, position 73/86, type 0x2, success. Gas limit 13,584,931 (chain percentile 99.27), used 10,362,493. Effective price 309.8022 gwei against base fee 249.3601 gwei, so tip 60.4422 gwei (percentile 17.19). Fee paid 3.210323 POL (percentile 99.97). Value sent 0.000000 POL. Destination is a contract. Selector `0x82ad56cb`, calldata 38,468 bytes, 1087 logs.

Decoded event families: ERC20_Transfer_shape ×466, Approval ×310, unknown ×310, Polygon_native_fee_log ×1. Distinct transfer recipients: 4.

ERC-20 net flows from transfer events (symbols are self-reported and untrusted): sender: +0.349705 LGNS.

Interpretation (LLM, confidence medium): The sender calls Multicall3 aggregate3 with 155 calls to helper 0xf5a7…8bfe, each producing the same seven-event pattern: two sLGNS approvals, sLGNS from escrow 0x25a4…8b07 to staking contract 0x1964…1bfc, LGNS back to the escrow, LGNS forwarded to 0xd080…00c7, and a helper record with the amount (1.467808 LGNS, 1.747383 LGNS and so on). 1,087 logs and 10.36M gas for 3.21 POL. The same helper is the delegate target of 89 EIP-7702 authorizations in the window from three relayer EOAs, so one operator controls many accounts through delegation and batches their claims: activity that a naive count would read as hundreds of users, the pattern the pilot memo flagged in its first finding.

Unverified: whether the 155 positions belong to distinct wallets; the role of helper 0xf5a7…8bfe; what LGNS and sLGNS are beyond their self-reported symbols. Multicall3 at 0xca11…ca11 and the aggregate3 selector are recognised from memory.

## What the quant step handed over, and what came back

Packets: 38. Annotated: 38. LLM confidence: high ×18, medium ×14, low ×6.

Artifacts: `packets.json` (evidence packets with fact IDs and baseline positions), `stats.json` (per-chain baselines and repeat-sender activity), `context.json` (bounded RPC lookups: token symbol/decimals, code presence, pinned block), `qual_notes.md` (LLM notes keyed by transaction hash), `rpc_requests.jsonl` (every follow-up request with estimated credits; no keys).

### Requests from the qualitative step back to the quant step (LLM)

1. Count WETH Deposit and Withdrawal events as native-to-WETH conversions in net-flow accounting. The ERC-20-only flow showed zero WETH change for #4, #6 and #7 and hid the retained arbitrage profit.
2. Add per-sender tip variance, and the number of distinct senders calling the same (destination, selector) pair with near-identical gas usage. Both separate configuration and fleets from urgency before a packet reaches the LLM.
3. Attach block context to each packet: builder or coinbase, and a one-line summary of the index-0 transaction. Both Ethereum top-of-block investigations needed them and had to request them separately.
4. For type-4 transactions include the authorization list (delegate target, authority nonce) and the count of same-sender type-4 transactions in the block; recover the authority address from the signature.
5. Register the event signatures recognised from memory in this pass so the next iteration decodes them deterministically: Balancer V2 FlashLoan, Velodrome-style Swap, Fees and Sync, LayerZero V2 PacketSent and OFTSent, GMX V2 EventLog1 and EventLog2, Chainlink OCR2 Transmitted, UMA Optimistic Oracle ProposePrice, GSN-style TransactionRelayed, Gnosis CTF PositionSplit, ERC-777 Sent. Each needs an address or source check before promotion to the mechanism registry.
6. Next bounded queries: a transaction trace for #36 (21M gas, no visible effect); code or label lookup for the Optimism keeper system (#26, #30, #31) and the Base per-id contract (#10); a check over several hours whether the Optimism loop (#23) is continuous.
7. Uniswap V4 swaps identify pools only by id. Index PoolManager Initialize events so a pool id resolves to its two currencies and fee tier; without that, three of the Ethereum packets needed manual reading of transfer pairs.

Limitations: the sample is a single two-minute window, so "outlier" means outlier within it, not historically unusual. Receipts do not show internal calls, native value moved by contracts, or revert reasons, so payments to block builders and the cause of failures are inferred, not observed. Token symbols come from the token contracts themselves. Contract identities named in the notes without an onchain check are model memory and should be treated as hypotheses.

