# Strategy-oriented findings from one day of Ethereum

Window: 2026-09-04 14:00 to 2026-09-05 14:00 UTC, blocks 25,904,413 to 25,911,585, the same data as `report.md`. Written by Claude on 2026-09-05 and 2026-09-06 after re-reading `letter.md`, `report.md` and `qual_notes.md` with one question: what in this day could seed a strategy. Every number below was computed from `txs_big.jsonl.gz`, `txs_all.jsonl.gz`, `addresses.json.gz`, the raw per-block logs in `../eth_day/raw/logs`, and read-only Infura calls; prose marked LLM is interpretation with a stated confidence. Exchange names are model memory unless the profile itself says so, and are flagged as such. The analysis scripts lived in the session scratchpad and are described in the appendix so the quant step can re-implement them.

Ranked by usefulness: (1) a scripted midnight balance routine that empties Aave's USDC pool for 42 minutes every day, (2) whales borrowing exchange-margin stablecoins against wstETH and cbBTC and shipping them to exchanges within minutes, (3) rate dislocations between Spark and Aave and a negative-carry regime for the Ethena loop, (4) a map of where dollars leave Ethereum to, concentrated in a handful of wallets. Section 5 lists what was tested and did not hold up, including everything MEV-related.

## 1. The midnight snapshot routine

The largest transaction of the day, $389,437,444 of USDC, is one leg of a round trip that assembles a balance at one address across 00:00 UTC and unwinds it half an hour later.

| Time UTC | Actor | Step | Transaction |
|---|---|---|---|
| 23:34:47 | [0x5695…0149](https://etherscan.io/address/0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149) | withdraws $143,979,739 USDC from Aave v3 (`withdraw`, aToken burned) | [0x6417…8d84](https://etherscan.io/tx/0x6417417aee8d4e8aec5ac5fd69ecb00b3dd46db9fae3fbd79b893c31d0bc8d84) |
| 23:36:47 | [0x688c…5cbf](https://etherscan.io/address/0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf) | redeems $245,506,505 sUSDS; the PSM path converts USDS to DAI to USDC at par | [0xd2bf…3ec6](https://etherscan.io/tx/0xd2bf4e2edbb298cbb070f44cbbf5c6ce578b87f933372932b93882a30ce13ec6) |
| 23:38:47 | same | sends $144.0M USDC to the hub | [0x1c97…29a7](https://etherscan.io/tx/0x1c97c7557e446f04ca1a3d32ea86cc75613ff3ad8ce51ee287bba2d5b24629a7) |
| 23:39:11 | same | sends $245.5M USDC to the hub | [0xd114…07c3](https://etherscan.io/tx/0xd114e389e9fb6c4a258c024317ea2157956ae83a6a7a1b5df2a7d391eee507c3) |
| 23:41:47 | hub [0x3117…bf18](https://etherscan.io/address/0x31173ed183e5a9450c3671018ec4d770c8a8bf18) | sends $389.4M to [0xf1ed…56a8](https://etherscan.io/address/0xf1edbf98dda764ec51de3776371f0f7d6f6156a8) | [0x64a8…da77](https://etherscan.io/tx/0x64a84fd6497c5c1dbfef5a5ed88efc7061e1e057514178aa22d5a15d4824da77) |
| 00:06:35 | 0xf1ed…56a8 | returns $389.4M to the hub | [0x828c…2093](https://etherscan.io/tx/0x828c49a31ca85ab347cc441e31ebf199f793f0465438c41592d6ad24c7342093) |
| 00:13:11 and 00:13:23 | hub | returns $245.5M and $144.0M to the two sources | [0x1682…95bf](https://etherscan.io/tx/0x168250500b1cea038f042d04f860afcfc1ac54c74753bbecf4f9de1aa8eb95bf), [0x0f13…77eb](https://etherscan.io/tx/0x0f1365d77eee69dd4780159c2cc47b0e6ed0c07ec009cf0bbec9359d80fc77eb) |
| 00:16:59 | 0x5695…0149 | re-supplies $143,979,739 to Aave (`supply`, aToken minted) | [0xf587…d2b9](https://etherscan.io/tx/0xf587c3e5c4801753453bd258b4d3c36ebce22b1a4f11f46c06f3ce0701b1d2b9) |
| 00:18:23 | 0x688c…5cbf | converts back and re-mints $245,505,818 sUSDS | [0x8973…0e7f](https://etherscan.io/tx/0x8973f5d326636075ba4d921632fc5b4435ac3f8fb29a075fa039efd7f2a90e7f) |

Facts established:

- The Aave leg is a withdrawal of the entity's own deposit, not a loan. The first transaction carries `Withdraw` and a scaled-token burn, the last carries `Supply` and a scaled-token mint. An earlier message in this session called it a borrow; that was wrong.
- Aave's USDC reserve reacted exactly as its rate curve dictates. From the `ReserveDataUpdated` logs, the variable borrow APR was 4.29% at 23:34:47 before the withdrawal and 14.27% in the same block after it, with supply APR going from 3.62% to 12.84%; both stayed there until the re-supply at 00:16:59, when they returned to 4.29% and 3.61%. The live rate strategy ([0x9ec6…fdfb](https://etherscan.io/address/0x9ec6f08190dea04a54f8afc53db96134e5e3fdfb)) has optimal utilisation 94%, slope 4.30% up to the kink, a further 10.00 points from 94% to 100%, and a 14.30% maximum. The pool held about $2,305M supplied against $2,154M borrowed when read on 2026-09-06 (93.4%), so removing $144M of supply takes utilisation to roughly 100%. In plain terms, Aave had almost no withdrawable USDC for 42 minutes.
- The round trip earns nothing. Forgone Aave supply yield on $144M for 42 minutes is about $416; the sUSDS side forgoes its savings rate for the same span. The only effect is that one wallet holds $389.4M of unencumbered USDC at midnight UTC.
- Nonces suggest a long-running schedule. The midnight wallet has nonce 652 and sent once in the day; the hub 3,554 and sent four times; the Aave address 760 and three; the sUSDS address 3,421 and seven. At those rates the addresses have been doing this for one to two and a half years. This is inference from one day (LLM, medium confidence); the next collected day should confirm the recurrence.

Interpretation (LLM, medium confidence): a balance cut-off. Candidates are an attestation or audit time, a proof-of-reserves snapshot, a fund NAV time, or a counterparty's daily collateral check. The identity of the entity is not readable from the chain.

Why it is useful:

- Predictability. A 42-minute liquidity shock in the largest USDC lending pool, at a known time, every day, is the raw material strategies are built from.
- Aave borrowers. A variable-rate USDC borrower pays 14.3% instead of 4.3% for 42 minutes daily, about 0.8 bps of principal per day, or 0.29% a year, roughly $8k a day on a $100M loan. Repaying before 23:34 and re-borrowing after 00:17 avoids it. Suppliers gain the mirror image, worth about 0.1 bps a day, so just-in-time supply only pays if it is free to run.
- Liquidity denial. Anything that must pull USDC from Aave between 23:35 and 00:17 fails or pays the maximum: vault reallocations, liquidation bots funding from Aave, redemption queues. Any Aave USDC APR reading sampled in that window is an artifact; allocators that chase it will misallocate.
- Sky. $245.5M leaves the PSM at 23:36 and returns at 00:18. Models of USDS peg stress or PSM buffer capacity, and USDC/USDS arbitrage, must exclude the window; sUSDS supply shows a daily $245M notch that is not a redemption.
- Observation. Once the address set is known, the midnight balance is a daily read on that entity's float and which yield venues it uses.

## 2. Leverage flowing to exchanges

Of the 48 lending operations in the day that paid at least $500k of stablecoins to the caller ($303.6M across 25 addresses), $58.1M were genuine borrows that reached an exchange deposit path within an hour, and $167.3M were withdrawals of the caller's own deposits routed the same way, $144.0M of which is the snapshot above. Event kinds were verified from `Borrow` and `Withdraw` families, and destinations from the profile of the first-hop address.

| Address | Collateral and venue | Action | Amount | Where it went | Lag |
|---|---|---|---|---|---|
| [0x29c9…71a1](https://etherscan.io/address/0x29c97b183ec6776ecd6975050c00862f930171a1) | wstETH, moved from SparkLend to Aave overnight with its partner [0xb656…5514](https://etherscan.io/address/0xb6569cf7c07921438349489ff7cc1e5fa9825514) | borrowed USDT on Aave in six clips of $4M to $10M | $37.1M | $33.1M to [0x4705…8dbb](https://etherscan.io/address/0x47057c2a6f0a7cbdc865697a6412dae6c6148dbb), a deposit address that sweeps to Binance 14 ([0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60), label from memory) | under 2 min |
| [0xaaf9…a45b](https://etherscan.io/address/0xaaf9f14f20145ad50db369e52b2793bfeb18a45b) | Aave | withdrew its own USDT supply | $15.0M | deposit address sweeping to Binance 14 | under 1 min |
| [0xf506…6ec6](https://etherscan.io/address/0xf50623b782fb0c7cd3966b20f6ecb7d791a36ec6) | $95.6M cbBTC received at 19:58 ([0x369f…781c](https://etherscan.io/tx/0x369f669b5f58773c8796245003af199bde006659feffb814f703bf5e1bf6781c)), $42.3M posted on SparkLend and $44.7M on Aave | borrowed $25M USDS on SparkLend ([0x7025…dd64](https://etherscan.io/tx/0x7025f9ba1dbfa8ecdb945661ba9397bc71a5f885cc69f8d6393c11004d65dd64), converted to USDC through the PSM) and $25M USDC on Aave ([0xd67e…3230](https://etherscan.io/tx/0xd67e26185b54930cad18b6f1e910d532be9e73b90e3c083def8627f834903230)) | $50.0M | $90M USDC in four pieces to [0x76e5…b308](https://etherscan.io/address/0x76e50320502e6e78c9a07f30564de4032c71b308), a pass-through into exchange contract [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43); $115.2M passed that address in the day | under 5 min |
| Coinbase 10 ([0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8), label from memory) | | plain transfers | $200.0M | four $50M pieces through sweep address [0x28c5…151a](https://etherscan.io/address/0x28c5b0445d0728bc25f143f8eba5c5539fae151a) into the same 0xa9d1…3e43 contract, 19:41 to 22:06 | 5 min |

Notes (LLM): the wstETH pair repaid USDS on SparkLend at 3.93% and borrowed USDT on Aave at 4.41%, the more expensive loan, which says they wanted the currency exchanges take as margin rather than the cheapest dollar (medium confidence). The cbBTC address did not sell any BTC; it raised $50M against it and shipped $90M. The contract 0xa9d1…3e43 is the day's largest deposit sink ($964M in 852 deposits) and is unidentified.

Why it is useful:

- A daily series of borrowed-stables-to-exchange is a direct measure of leverage demand and should lead perpetual funding and basis; withdrawals-to-exchange is a separate series measuring DeFi yield being pulled back to venues.
- Each position has a computable liquidation level from its posted collateral; the wstETH pair and the cbBTC address are worth following.
- The exchange sinks 0xa9d1…3e43 and [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) ($343.9M of USDC deposits) are the addresses to label first.

## 3. Rate dislocations

Read from the pools on 2026-09-06 after the window; intraday ranges are from the `ReserveDataUpdated` logs.

| Market | Supply APR | Borrow APR | Utilisation | Supplied | Intraday borrow range |
|---|---|---|---|---|---|
| SparkLend USDT | 6.05% | 7.00% | 96.0% | $341M | 3.52% to 5.72% |
| Aave v3 USDT | 3.73% | 4.41% | 94.1% | $2,958M | 4.23% to 5.27% |
| Aave v3 USDC | 3.59% | 4.27% | 93.4% | $2,306M | 4.24% to 14.30% |
| Aave v3 USDe | 1.86% | 5.50% | 45.0% | $647M | 4.56% to 5.56% |
| SparkLend USDS | 2.32% | 3.93% | 65.6% | $705M | 3.84% to 4.05% |
| sUSDe NAV growth | 4.37% annualised from 1.2464850 to 1.2466343 in 24h | | | | |

- USDT earns 2.3 points more on SparkLend than on Aave for the same risk class. The Spark market is a tenth the size and at 96% utilisation, so the gap closes as tens of millions move in; it is a yield pickup at institutional size, not retail.
- Borrowing USDe on Aave at 5.5% against sUSDe yielding 4.37% is negative carry. That matches the day's sUSDe cooldown exits of $17.9M and $6.6M of sUSDe sold into pools at 6 to 9 bps below NAV (value-weighted 8.6 bps, 9.1 bps for trades above $100k). Expect the loop to keep unwinding and the discount to persist while borrow exceeds yield (LLM, medium confidence).

## 4. Where dollars leave Ethereum

Decoded from `DepositForBurn` (destination domain in the third data word) and `OFTSent` (destination endpoint id in the first data word) over all 5.96M logs. Domain names above 12 and non-standard endpoint ids are model memory and unverified.

| Route | Amount | Concentration |
|---|---|---|
| CCTP USDC burns, all | $217.0M | |
| to Polygon (domain 7) | $53.0M, 244 burns | 85% ($45.0M, 92 burns) to one recipient, [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef), the exchange hot wallet discussed below |
| to Solana (5) | $36.9M, 260 | 35% to one recipient |
| to Aptos (9) | $35.0M, 42 | 100% to one recipient |
| to domain 15 (Monad by memory) | $23.6M, 119 | top 4 recipients 74% |
| to domain 19 (HyperEVM by memory) | $20.0M, 135 | one $10.0M transfer plus 99 transfers to one address |
| to Base (6) | $19.3M, 568 | retail-sized |
| to Arbitrum (3), OP Mainnet (2), Avalanche (1) | $12.7M, $12.5M, $3.2M | |
| USDT0 OFT ([0x6c96…1dee](https://etherscan.io/address/0x6c96de32cea08842dcc4058c14d3aaad7fa41dee)) | $44.8M, 131 sends | 72% to endpoint 30383 |
| USDe OFT | $33.5M, 86 | $24M from one bridge contract [0x50cf…5c4a](https://etherscan.io/address/0x50cfe7c1938db66a1a6d2e86d36f39fbef3d5c4a) to endpoints 30383, 30390, 30168 |
| USDG OFT ([0x147b…f9c4](https://etherscan.io/address/0x147bde4f997f0d4c7544ed0c55eacf1e5e6bf9c4)) | $30.7M, 291 | 95% to endpoint 30416 |
| USDC OFT (0xc026…89c7) | $12.3M | 80% to BNB Chain |

The classic L2s together took $44M of CCTP flow; Solana, Aptos and the two newer domains took $116M. Inbound, the largest single pattern was $90.0M of USDC arriving by CCTP in ten $9.0M mints to [0xe69f…3abb](https://etherscan.io/address/0xe69f81b825d7dc31ee9becef4dbeab5cf30e3abb) between 23:40 and 00:26 and forwarded within two minutes each to the exchange deposit contract 0xee7a…4055.

The wallet [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) deserves its own line. Profile: 5,575 transactions sent to 508 destinations, nonce 4.79M, active every hour. In the day it received $33.2M of USDC minted by Circle, bought $33.8M of USDG with USDC at 3.5 bps over the USDC price in 138 fills through router [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) (fillers: 0x Settler $18.2M, [0x025a…a62f](https://etherscan.io/address/0x025a13752ec1fb6c0e441e5d7b1678bb5f9ca62f) $9.3M, Uniswap v4 $3.9M), sold $26.4M of USDG for USDC at about 2 bps over, bridged $22.5M of USDG out through the USDG OFT, and was the recipient of the $45.0M of USDC burned toward Polygon. USDG is therefore trading at USD par; the apparent premium is mostly USDC sitting 1.4 bps below par on the Chainlink feed. This is an exchange with a USDG desk and a Polygon on-ramp business (LLM, high confidence on the flows, identity unknown). Polygon USDC from a single exchange at $45M a day is the natural proxy for Polymarket funding.

A smaller loop: [0x65c3…15d8](https://etherscan.io/address/0x65c340eb0688d8f8b64e9c6d580f312a97b615d8) bridges USDT in through the USDT0 adapter in $2M pieces and deposits each to the exchange sweeper [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) within a minute, then sends USDT back out, a cross-chain, cross-exchange inventory cycle.

## 5. Tested and not useful, or corrected

- Informed flow. For 1,665 two-sided ETH/stablecoin trades of at least $10k, signed forward returns at 25, 150, 300 and 900 blocks were measured against the last USDC/WETH pool price in a prior block, with the unconditional drift removed. Nothing survives once the 14:00 to 17:00 rally is excluded: every group sits within 2 bps with t-statistics below 2. The hit rates that looked striking (a USDT/WETH pool counterparty at 99%, a contract at 18%) are one episode. On-chain ETH flow by count is CEX-DEX arbitrage fleets: [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) takes 8,356 calls a day from EOAs that each send to it alone; [0x93c3…dd17](https://etherscan.io/address/0x93c30e6e09f698cfea99b09b5166ed90cfaedd17), [0xbdb3…47b6](https://etherscan.io/address/0xbdb3ba9ffe392549e1f8658dd2630c141fdf47b6) and [0x225a…dc17](https://etherscan.io/address/0x225a38bc71102999dd13478bfabd7c4d53f2dc17) are the same shape.
- Hourly exchange netflow versus next-hour ETH return: correlation 0.38 for ETH and −0.08 for stablecoins on 23 hours, not significant.
- Execution quality. User-facing venues fill within ±5 bps of the block-open pool mid; RFQ and bilateral fills beat it by 5 to 10 bps; flash-loan arbitrage pays 2 to 3 bps against the stale pool. No retail leakage to harvest above $10k.
- MEV. The "sandwich" bots are just-in-time liquidity and lending-position bots (bot [0x1f2f…f387](https://etherscan.io/address/0x1f2f10d1c40777ae1da742455c65828ff36df387): 1,404 transactions, 206 liquidity-with-swap, 47 sandwich legs, visible day net +$47k mostly in sDAI). Flash-loan bots show zero token net and near-zero net WETH unwrap. Receipts for 374 MEV transactions show a median priority fee of 0 gwei and median gas cost of $0.13 to $0.61, so payoff and builder payment move by internal ETH transfers and are invisible without traces. Titan built about 60% of those blocks, then BuilderNet, Quasar, Eureka. Archive balance calls failed on all Infura keys that evening, so day P&L could not be measured.
- 488 of the 743 "flash loan without a swap" are one 1inch resolver ([0xd824…e272](https://etherscan.io/address/0xd82461784eb72d4b67cbab077989eb215315e272), sender 0x0e0052a1…, 1,802 transactions a day) using free Balancer flash loans as fill working capital. Re-type them.
- Stablecoin pricing. EURC trades 1.6 bps below the Chainlink EUR feed. AUSD sits 1.4 bps below par with a par converter, negligible. DOLA 25 bps, USDf 23 bps, BOLD 11 bps, USD0++ 3.1% and apxUSD 2.8% below par have no par redemption or, for apxUSD, an unresolved identity while it sits as Morpho collateral. scrvUSD trades 8 bps over NAV.
- Exchange netflow as computed by the report ($2.25B net inflow) is contaminated: [0xcd53…ca7b](https://etherscan.io/address/0xcd531ae9efcce479654c4926dec5f6209531ca7b) took $574M of "deposits", sends to only 29 destinations, and feeds addresses that Coinbase pulls from by `transferFrom` ([0x774a…c59f](https://etherscan.io/address/0x774ae279c2f7f0eb4fc61dba7d5b4c9e5f7ec59f) and others); it is a treasury or prime-broker hub, not an exchange. Coinbase 10 received $501.9M of Circle mints and burned $404.2M itself, so USDC mint volume mostly measures one exchange's own balancing.
- Exchange deposit attribution in an earlier session message put $1.47B on the USDC contract; that was a leg-matching bug, since fixed; the recipients table in section 2 of this file is correct.

## 6. Caveats

One day of data; every "daily" claim is nonce arithmetic until the next day is collected. Exchange labels (Binance 14, Coinbase 10) and bridge domain names above 12 are model memory. The two large exchange deposit contracts and the midnight entity are unidentified. Historical-state RPC was unavailable, so nothing here depends on archive balances; everything comes from logs, transfers and current state. Statistical tests on one day are episode-driven and reported as negative for that reason.

## 7. Requests to the quant step

1. Round-trip detector: flag amounts of at least $10M that return to their source within two hours, and emit the midnight routine as a daily series (size, addresses, Aave and PSM legs). Verify recurrence on the next collected day.
2. Utilisation-shock series from `ReserveDataUpdated` for Aave and SparkLend stable reserves (topic `0x804c9b84…897a`, data words 0 and 2 are supply and variable borrow rates in ray), with the rate-curve parameters read once per day.
3. Borrowed-stables-to-exchange series: lending ops with `Borrow` events whose proceeds reach a hot wallet, deposit contract or pass-through within 60 minutes; keep withdrawals as a separate series. Compute liquidation prices for positions above $20M.
4. Bridge destination series: CCTP by domain and top recipients, OFT by adapter and endpoint id; resolve endpoint ids 30383, 30390, 30416, 30420, 30168 and domains 15 and 19 from LayerZero and Circle documentation rather than memory.
5. Rate spread series Spark versus Aave per asset, and the Ethena carry (Aave USDe borrow minus sUSDe NAV growth) alongside the sUSDe pool discount.
6. Address book: label 0xa9d1…3e43, 0xee7a…4055, 0xcd53…ca7b, 0xf70d…dbef and the midnight set; stop counting treasury hubs as exchange inflow.
7. Registry: re-type the 1inch resolver flash loans and the just-in-time liquidity bots; add a `withdraw` versus `borrow` split to the lending method's output.
8. Infra: an archive or trace-capable endpoint for bot balance deltas; key rotation on -32005.

## Appendix: method notes

- Block-open mid: for each block, the last USDC/WETH swap price in the two pools [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) and [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) from the full census (24,525 swaps); a trade's reference is the close of the latest prior block within 10 blocks. Execution cost in bps is (ref − px)/ref for sells and (px − ref)/ref for buys; forward returns use the same series at +25, +150, +300 and +900 blocks, signed by trade direction, minus the unconditional mean forward return over all blocks.
- Two-sided principal: the transaction sender if its net is opposite-signed in WETH and one of USDC/USDT with no other asset moving, else the first such address; pools appear as principals when they are the only two-sided party, which is why pool addresses show up in the informed-flow tables.
- Lending event kinds: `Borrow`, `Withdraw`, `Supply`, `Repay` families from `signatures.py`; the first-hop classification uses the profile of the receiving address (hot wallet if at least 100 sends to 50 destinations; pass-through if it sends to exactly one destination; many-sources contract if at least 50 sources and no sends).
- CCTP `DepositForBurn` v1 and v2: amount is data word 0, mint recipient word 1, destination domain word 2. `OFTSent`: destination endpoint id word 0, amount sent word 1; the token is `token()` of the adapter or `symbol()` of the emitter.
- Aave rate strategy: `getOptimalUsageRatio`, `getVariableRateSlope1`, `getVariableRateSlope2`, `getMaxVariableBorrowRate` on the reserve's strategy contract, values in ray.
- Nonce arithmetic: nonce at window end divided by transactions sent in the window gives the number of days at that cadence; it assumes a constant cadence and is a screen, not a proof.
- Scratchpad scripts, in order of use: `pool_px.py` (block price series), `informed_trades` analysis, `borrow_to_cex.py`, `follow.py`, `bridges.py`, `logs2.py` (rate updates, CCTP recipients, OFT senders), `receipts.py`, `mev_pnl.py` (blocked on archive access), `rpc.py` (key rotation).
