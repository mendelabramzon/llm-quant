# Ethereum mainnet live scan: 2026-09-07T02:39:11+00:00 to 2026-09-07T07:39:11+00:00 UTC

Blocks 25922548 to 25924040 (1493 blocks, 5.00 h), 365,859 transactions, 1,233,959 logs. Prices at head block 25924104: ETH $2484, BTC $79k. Generated 2026-09-07T23:19:12+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

## Insights (LLM narrative, written from `events.json`, `analysis.json`, `head_state.json` and `followups.json`)

Written by Claude on 2026-09-07 at 08:10 UTC for the window 02:39 to 07:39 UTC (blocks 25922548 to 25924040): five hours, 365,859 transactions, 1.23M logs [[verify: blocks]] [[verify: transactions]] [[verify: logs]], 130,500 distinct senders, blocks 51% full, base fee 0.03 to 1.01 gwei. Every number below is in the deterministic artifacts (`events.json` from `scripts/window_events.py`, `followups.json` from `scripts/window_followups.py`, `analysis.json` and `head_state.json` from `scripts/live_scan.py`); the readings are mine and carry a stated confidence. Contract names come from Blockscout's verified-source names or from the sites named; behavioural exchange labels are from the day study's address book.

### 1. Tape: ETH fell 1.9% in two legs and the arb bots paid 2,400 gwei to be first (high confidence)

ETH/USD read tick by tick from the USDC/WETH 0.05% pool: open $2,531.6, high $2,534.0 (02:39), low $2,482.6 (07:39), close $2,482.7. Two legs: 02:39 to 03:45 from 2,532 to 2,498, flat between 2,495 and 2,512 for three hours, then 07:15 to 07:39 from 2,500 to 2,483. The largest five-minute moves were 0.37% (02:52), 0.32% (02:39) and 0.32% (07:33).

The most urgent transactions of the window sit exactly on those moves: the CEX-DEX arb contracts [0x51c7…2a7f](https://etherscan.io/address/0x51c72848c68a965f66fa7a88855f9f7784502a7f) and [0x93c3…dd17](https://etherscan.io/address/0x93c30e6e09f698cfea99b09b5166ed90cfaedd17) were paid tips of 2,406, 1,155, 656, 506 and 366 gwei at 02:39:11 (block positions 0 to 3), 1,098 gwei at 06:08 and 649 gwei at 07:33, against a window median tip of 0.07 gwei. That is the price of the first slot after a centralized-exchange move, and it only appears when the price moves. Tagged exchange wallets took in ETH on the way down: ETH +$12.8M net (in $99.6M, out $86.8M) and WETH +$0.2M; USDT +$74.8M net; USDC +$2.0M net [[verify: exchange-net-eth]] [[verify: exchange-net-stables]]. (These figures have been restated twice as labels were corrected — see the two correction sections below — rather than left to contradict them.) Binance 14's three internal transfers of 10.9k to 11.7k ETH to Binance 15, 16 and 17 ($82M at 03:02 and 06:22) are the largest native transfers of the window and are not counted as flow.

### 2. A tokenized-stock swarm pushed the base fee up ten times for forty minutes (high confidence on the flow, medium on the operator)

The base fee was 0.03 to 0.15 gwei for most of the window and 0.77 to 1.01 gwei from 03:45 to 04:10 UTC. Blocks were not fuller on average (47% to 59%); they carried fewer and heavier transactions (14,798 in the 03:45 quarter-hour against 22,711 at 03:15). The heavy transactions are calls to three unverified proxy contracts that route swaps through Uniswap v4 with ERC-6909 claim tokens and log a fee on every swap through a "FeeEscrow" ([0x0b94…b8da](https://etherscan.io/address/0x0b943b855912214f0a73ca80b73deaccea1ab8da), 14,260 fee events): [0x4313…b27f](https://etherscan.io/address/0x4313c378cc91ea583c91387b9216e2c03096b27f), [0x5228…0b60](https://etherscan.io/address/0x5228ed975c6bcb53d2e221ba737362fd9add0b60) and [0xf928…db56](https://etherscan.io/address/0xf9280799c85d376e0425f6fb38e4a674e8bedb56). Between 03:25 and 04:25 they took 2,300M, 327M and 549M of gas limit against 129M, 18M and 27M in the 46 minutes before: an eighteen-fold jump. Over the five hours: 5,756 calls from 1,127 distinct wallets, 200 of them with nonce below 5 and 3,729 calls from wallets with nonce 100 or more; 281 ETH of value attached (about $700k).

The tokens are Ondo's tokenized stocks, BeaconProxies deployed by [0xE60F…3caB](https://etherscan.io/address/0xE60F44AA6b7084d5Ca05D0e9145921e94bc23caB): NVDAON (NVIDIA), TSLAON (Tesla), SPCXON (SpaceX) and SPYON (S&P 500 ETF), plus "Stockereum.fun" (STOCKER), a launchpad whose site describes launching fixed-supply tokens into permanent Uniswap v4 markets against a tokenized stock. 58 v4 pools were touched. NVDAON/USDC did 1,278 swaps from 476 senders for $289k one-side; USDC/SPCXON 761 swaps, 303 senders, $70k; STOCKER/USDC 306 swaps, 190 senders, $82k; about thirty launch-token pools with 10^9-supply tokens against SPCXON, SPYON and TSLAON did the rest. Total one-side volume across all stock pools: about $540k in five hours, $100 to $150 per swap. Last prices: NVDAON 233.06 USDC, SPCXON 152.5 USDT, SPYON 0.311 ETH (about $775). Ondo minted 550 NVDAON, 138 SPCXON, 46 TSLAON and 45 SPYON in the window (about $200k of primary issuance) and burned 78 NVDAON.

Reading: a retail launchpad frenzy in tokenized-stock pairs, not an institutional flow and not one sybil operator. Of the 200 fresh wallets, 61 were funded by plain ETH transfers inside the window from 51 distinct sources (median 0.02 ETH, the busiest source funded four), including Binance 15, Bitget and Gate.io hot wallets. It moved half a million dollars and cost every mainnet user ten times the gas for forty minutes: about 4,000 swaps at 1.1M gas each. Its arb counterparty is one bot contract, [0x0000…089b](https://etherscan.io/address/0x00000000fd3a7b3fa5bcfa843c648714b11e089b), 180 calls of 16M gas from one EOA on the same pools. For the captive-flow LP thesis these pools are the opposite of captive: tiny toxic tickets with a platform fee escrow in front of the LP. The same hour, ERC-4337 EntryPoint v0.8 ([0x4337…f108](https://etherscan.io/address/0x4337084d9e255ff0702461cf8895ce9e3b5ff108), 2,141 bundles from 30 bundlers) and router [0xccc8…15be](https://etherscan.io/address/0xccc88a9d1b4ed6b0eaba998850414b24f1c315be) (2,319 calls, 214 senders) were trading "Artificial Pepe" against USDC through smart accounts: a second bot swarm, 3.7x its pre-spike gas.

### 3. Robinhood Chain is the biggest blob poster on Ethereum right now (high confidence)

7,616 blobs in 1,493 blocks (5.1 per block; 82.6% of blocks carry blobs). The largest poster is [0xbd0d…ba96](https://etherscan.io/address/0xbd0d173eeb87d57a09521c24388a12789f33ba96), an Arbitrum Nitro SequencerInbox proxy that Robinhood's own chain documentation lists as Robinhood Chain's sequencer inbox: 2,169 blobs in 723 batches (three per batch, one every 25 seconds) from batch poster [0xdaa5…87f4](https://etherscan.io/address/0xdaa526086787d9debe1d7f3ffdb1fe50cf8687f4), 28.5% of all blobs, ahead of Base (1,992, 26.2%), OP Mainnet (925), Arbitrum One (345), World Chain (315) and Unichain (159). Seven other unlabelled inboxes posted 76 to 270 blobs each. A chain that launched on 1 July is now the single largest consumer of Ethereum data space, at least in this window; the daily series is a request below.

### 4. Spark's liquidity layer pulled $46M of USDT out of SparkLend into its savings vault and doubled the SparkLend USDT rate (high confidence)

At 07:20:47 (block 25923948) one transaction, sent by the relayer [0x062c…6ffe](https://etherscan.io/address/0x062ce42cae04c51d04e77e3d64cc8953a2296ffe) through the Safe [0x8a25…39ab](https://etherscan.io/address/0x8a25a24ede9482c4fc0738f99611be58f1c839ab), had the Spark ALMProxy ([0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e), verified name) withdraw $46.4M USDT from SparkLend, redeem $28.7M USDT from Spark's own Morpho VaultV2 "Spark Blue Chip USDT Vault" ([0xb0c4…5b91](https://etherscan.io/address/0xb0c424116172b55cbb6dd3136f5989f7959e5b91), sparkUSDTbc, in four legs of $13.8M, $3.7M, $11.2M and $36k), mint 250,000 USDS through Sky's allocator and swap it to USDT on Uniswap v4, and move the $75.35M USDT into the Spark Savings USDT vault ([0xe2e7…c372](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372), a SparkVault). So Spark moved USDT between three of its own products, out of the lending market and the Morpho vault into the savings vault, and the lending market's borrowers pay for it. The same relayer runs the ALM's scheduled USDS-to-RLUSD buys described in section 7. SparkLend USDT went from 2.62% supply / 3.52% borrow to 6.05% / 7.00% at 96% utilisation [[verify: rate-gap-widest]] ($344M supplied, $331M borrowed) and stayed there to the head. Three and a half minutes earlier (07:17:11) [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) had refinanced $7.19M of USDT debt from Aave (4.22%) to SparkLend (3.52%) in one transaction; it now pays 7.00%. The same ALM supplied $15.2M USDS to SparkLend at 06:59 and [0xb99a…cbcf](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) borrowed $10M USDS there at 06:58.

The rate table at the head: USDT borrow Compound v3 3.81%, Aave 4.22%, SparkLend 7.00%; USDC supply Aave 3.59% against Compound v3 5.49% (borrow 6.54% at 90.7% utilisation), so the USDC dispersion widened from 1.2 to 1.9 points since yesterday. Yesterday's Aave PYUSD spike is gone: supply 3.75% (was 23.3%), the reserve was repaid, though it flashed to 25.8% borrow for one block at 02:59. Aave's USDtb reserve read 9.6% supply / 14.3% borrow on its only update. Sky's savings rate 3.60%, Ethena 4.47%.

### 5. The largest active borrower is 1.4% from liquidation, and the debt swaps follow the rate table (high confidence on the numbers)

Health factors at the head for accounts that acted in the window: [0xd938…48dd](https://etherscan.io/address/0xd93814273b33dd33b32cd345225cfb65deb048dd) holds $237.6M of collateral against $217.8M of debt on Aave v3 at a 93% liquidation threshold (E-mode), health factor 1.015. It withdrew $2.8M USDe at 04:05 and repaid $2.6M USDT at 04:20: a USDe-collateral, USDT-debt loop that is de-risking in small steps, 1.4% from liquidation. [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) on SparkLend ($29.4M debt) is at 1.035 and [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) on Aave ($10.8M) at 1.026 after swapping $3.6M of USDT debt into USDC debt.

Debt moved toward the cheaper dollar all window: [0x13ff…55b7](https://etherscan.io/address/0x13ffb3286d8d371785e6288588be88e4356555b7) borrowed $2.9M WETH (2.03%) and repaid $2.9M USDT (4.22%) in one transaction, settling through CoW; [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) repaid and re-borrowed $5.1M USDT while supplying $5.1M USDC in one block. [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) ($355M collateral, $181M debt, health factor 1.62) borrowed $10M USDT at 02:44 into a Safe that sold $885k through CoW and wrapped 4,000 ETH at 04:15. One liquidation in five hours ($13k of LINK debt). The "leverage to exchange" pipeline, after applying the new verified-label registry (`scripts/address_labels.json`, which retags CoW Protocol's settlement contract as a venue rather than a deposit sink and no longer chases borrowed funds through it), reads $277k of genuinely exchange-bound proceeds across 31 followed operations [[verify: leverage-to-exchange]]. Two corrections stack here: the registry retagged CoW settlement, taking $25.7M to $5.3M, and the deposit-sink rule fix below took $5.3M to $277k by retiring the forwarding contracts that the remaining hops landed on. This is the address-book fix that was the first request of this study, now implemented.

### 6. A flash-loan bot is farming a memecoin's MasterChef with $175M of Morpho liquidity every half hour (mechanism: medium confidence)

Eight runs (03:20, 04:29, 05:12, 05:40, 06:09, 06:37, 07:00, 07:29) by [0x23fd…9b6a](https://etherscan.io/address/0x23fdc534cfbbf7cfda0acb15e0e340939f319b6a) through [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d), 1.5M gas each. Each run flash-borrows from Morpho Blue, fee-free, 10,907 WETH ($27M), 102.7M USDC and 551 WBTC ($44M): the $100M+ round trips at the top of the large-transfer table. It mints Uniswap v2 liquidity in USDC/WETH and WBTC/WETH, deposits the LP tokens into "StacyVault" ([0x223b…8df8](https://etherscan.io/address/0x223bc79156cbb0a6d175ea6130cb382d01868df8), MasterChef Deposit and Withdraw events on pool ids 3 and 4), receives about 2,400 STACY per pool ("Stacy", [0xf12e…b327](https://etherscan.io/address/0xf12ec0d3dab64ddefbdc96474bde25af3fe1b327), 436 holders; the deployer [0x8aef…9a08](https://etherscan.io/address/0x8aEf57fe9d16BE8F24df37ab56da6eC18f7e9a08) receives 12,004 STACY per run), stakes and unstakes the STACY in [0x2222…8ae6](https://etherscan.io/address/0x222207e931d7bf38466c395da30e632872a98ae6), withdraws the LP, burns it and repays Morpho, all in one transaction. The verified source (Blockscout) explains why this pays: StacyVault is a fork of the CORE vault, not a per-block MasterChef. Rewards arrive in lumps (the STACY token's transfer fee and a `cherryPop` function that moves about 1% of the STACY/WETH pair's reserves per day into the vault; the 240,180 STACY that leave the pair for the vault in each run, with 2,424 to the caller, are that trigger) and every update hands the whole accumulated lump to whoever is staked at that instant, pro-rata to stake with no time weighting. The vault's authors added a same-block guard (`withdraw` requires `block.number > lastDepositBlock`), but `depositFor` never sets `lastDepositBlock` [[verify: stacy-deposit-for]], so a bot that calls `depositFor` on itself withdraws in the same transaction; the 75% of rewards sent to a lock contract came back out in the same transaction too. The STACY/WETH pair is thin, so the dollar take is small; the pattern is the point. Yesterday's $3.5B Balancer bot ([0x1124…e0ae](https://etherscan.io/address/0x11246c5b75b3a88b05f0238ced6cd9b8afc7e0ae), zero runs in this window) and this one are the same trade: an accounting artefact that regenerates between runs, harvested with free flash liquidity.

### 7. Large moves, and the poisoning bots that follow them within seconds (high confidence on the facts, identities unresolved)

[0xd3a2…c4a1](https://etherscan.io/address/0xd3a22590f8243f8e83ac230d1842c9af0404c4a1) (126,783 ETH, $315M) sent 10,000 ETH to [0x3a3c…1dc8](https://etherscan.io/address/0x3a3c006053a9b40286b9951a11be4c5808c11dc8) at 07:37:35, which forwarded 1,926.5 ETH to [0xcde5…9b90](https://etherscan.io/address/0xcde5d48fca07f9c52300d2e65632dd71ed169b90) 72 seconds later. [0x98ad…ba9d](https://etherscan.io/address/0x98adef6f2ac8572ec48965509d69a8dd5e8bba9d) (88,070 ETH, $219M) had sent the same wallet 4,571 ETH at 07:24:47 after transferring it a dozen tokens (UNI, ENA, USDe, ZRO, USDT among them) one every 24 seconds; the transit wallet forwarded the tokens on and sent 2.6 ETH to Binance 14. Two large treasuries consolidating through one transit wallet that fans out is the shape of an exchange or custodian hot-wallet migration; none of the addresses carries a label. [0x434a…45ac](https://etherscan.io/address/0x434aaa7c02874e614149ad572a05cffd007145ac) sent 4,000 ETH to [0xf6fa…c12c](https://etherscan.io/address/0xf6fa2ba6f5764e3be4aeaae646898a5baf54c12c) at 06:51; the Safe [0x54d2…6029](https://etherscan.io/address/0x54d250405d22e858d125ce2c1affc7d73afe6029) wrapped 4,000 ETH at 04:15; [0xc882…f071](https://etherscan.io/address/0xc882b111a75c0c657fc507c04fbfcd2cc984f071) sent 3,650 ETH to a Gate.io-tagged wallet.

Address-poisoning bots followed: the matcher in `followups.json` finds 26 dust transactions (0.000001 ETH, empty calldata) from look-alike addresses aimed at the parties of the 32 native transfers of 1,000 ETH or more in the window, the first typically 24 to 60 seconds after the transfer. Examples: 24 seconds after the 10,000 ETH transfer, [0x3a3c…1dc8](https://etherscan.io/address/0x3a3c2c6ea2a5042c4d493f5e3bab6d5536b01dc8) (same first four hex characters as the recipient) sent one to the sender; six look-alikes of both parties (0x434a3f8b, 0x434a605a, 0x434a5994, 0x434aaf8f, 0xf6fad56f, 0xf6fac854) hit the 4,000 ETH pair over the next 40 minutes; two 0xbd19… look-alikes sent the Safe six of them after its wrap. Three look-alikes hit the sender of a 3,651 ETH transfer to Gate.io 24 seconds after it, and five hit the sender of a 3,526 ETH transfer within five minutes. Anyone who copies a counterparty address out of recent history is the target.

Stablecoin block moves: $129M USDC hopped through four unlabelled pass-through EOAs (0x0f89…, 0x763c…, 0x7702…, 0x4e67…) at 05:35 and again at 06:52; $100M RLUSD left [0x6242…dc9f](https://etherscan.io/address/0x62425cd6bdcb6bfe51558ea465b063486b70dc9f) (14,290 ETH) in four $25M clips at 07:19 to two EOAs. RLUSD is 61% of the exchange-flow "out" figure only because that wallet carries a behavioural hot-wallet tag; it looks like an issuer or treasury wallet, the second address-book fix. Meanwhile a scheduled seller rotated RLUSD into USDS into USDT in $300k clips every 23 minutes ([0x7f32…b888](https://etherscan.io/address/0x7f324545c481f8c150802103a8ee94014251b888), $1.2M) while the Spark ALM relayer [0x062c…6ffe](https://etherscan.io/address/0x062ce42cae04c51d04e77e3d64cc8953a2296ffe) bought RLUSD with freshly minted USDS in $200k clips on Uniswap v4 (seven clips, $1.4M; the same relayer executed the SparkLend withdrawal of section 4), so Spark's liquidity layer is one of the RLUSD buyers; RLUSD printed 1.8 bps over USDC.

### 8. Everything else worth a line

- Pegs (volume-weighted swap prices at the head): USDT 0.99986, USDS 0.99995, USDe 0.99995, USDG 1.00002, PYUSD 1.00002, DAI 0.99999, GHO 0.99863 (−14 bps), USD1 0.99951 (−5 bps), RLUSD 1.00018; sUSDe 1.24657 against NAV 1.2469 (−2.6 bps); wstETH and weETH at NAV; rETH $2,904.3 against NAV $2,909.5 (−18 bps).
- Passive LP: the USDC/WETH 0.05% v3 pool earned 2.19% APR full-range-equivalent over the window on $12.9M of volume (yesterday's quiet hour: 0.72%); WETH/USDT 0.05% 3.09%. Just-in-time liquidity: 144 episodes, $229 of fees taken, 55 of them by [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13).
- Bridges out: USDe OFT $7.2M to eid 30383; CCTP USDC to Polygon $6.9M (72% to the USDG-desk hot wallet [0xf70d…dbef](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef), as in the day study), Arbitrum $4.8M, Solana $0.9M; USDT0 $1.9M to eid 30420.
- Cheap-gas farming: XEN Crypto minted 100.9B tokens to 4,536 addresses (78 transactions, eight of them batches of 400 mints by [0xc87a…](https://etherscan.io/address/0xc87a8df3)); "Watt2Trade (WATTOIN)" dusted 10,530 addresses with 12,044 transfers in 40 transactions of 501 or 1,002 transfers. 271 contracts were created ([0x80d0…](https://etherscan.io/address/0x80d04079) 30, [0x9bcd…](https://etherscan.io/address/0x9bcd8076) 20, one every 15 minutes); 21 new pools (18 v2-style, 3 v3, among them Artificial Pepe/WETH 1% and a launch token against SPCXON at 0.3%).
- Transaction types: 5,715 type-4 (EIP-7702 set-code, 1.6% of all), 2,571 type-3 blob carriers. Builders: Titan 49.7%, Quasar 20.7%, BuilderNet 15.1%, Eureka 4.8%. Validator withdrawals: 23,888 for 1,443.6 ETH, of which 26 full exits totalling 1,040 ETH, 596 ETH of it between 05:45 and 06:00.
- The Balancer flash-loan working capital of the day study is still there: 583 Balancer flash loans ($29.0M), the 1inch resolver.

### Requests to the quant step

1. Address book (DONE this session): `scripts/address_labels.json` now retags [0x9008…ab41](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41) as CoW Protocol settlement (venue), 0x62425cd6… as an RLUSD treasury/issuer candidate, and adds the Robinhood Chain inbox, the Ondo stock tokens, StacyVault, spUSDT, the Spark Blue Chip USDT vault and the Spark ALMProxy; `live_scan` counts only `kind` in {exchange, exchange_deposit} as exchange flow. Still to add: the Stockereum routers and FeeEscrow, and provenance for the memory-only CEX labels.
2. Make the gas-hog attribution automatic: a per-5-minute series of gas limit by target with the spike-versus-baseline ratio (the one-off version is `scripts/window_followups.py`), so a base-fee spike names its cause in the live log.
3. Trace one StacyVault run and one stock-router swap through dRPC `debug_traceTransaction` to settle the reward mechanism and the FeeEscrow's take per swap.
4. A tokenized-stock monitor: on-chain prices of NVDAON, TSLAON, SPCXON and SPYON against the underlying's last close and the Robinhood Chain venues, mints and burns per day, v4 pool depth. The on-chain price of a stock outside market hours is a new kind of dislocation to measure (SPCXON traded 152 to 154 across USDT and USDC pools here).
5. A daily blob-share table per inbox with verified labels; Robinhood's share against Base is the number to watch.

## Correction, 2026-09-07 (labels and verification)

The exchange-flow and leverage figures in this note were recomputed after the deposit-sink heuristic in
`load_address_book` was corrected: it tested `sent == 0` ("originated no transactions"), which every contract satisfies,
so 22 forwarding contracts were being counted as exchange deposit sinks. On the same blocks the window now reads USDC
−$97.9M and USDT +$74.8M net, ETH +$12.8M net, and leverage-to-exchange $277k across 31 followed operations
[[verify: leverage-to-exchange]]. (The USDC figure was corrected again the next day — see the section below.)

All 13 checks in `verify.py` re-derive these from the raw blocks through an independent path and pass. The label band
was unusually wide on this window: net stable flow read **+$91.6M** using model-memory labels alone and **−$24.8M**
once behavioural labels were included — a sign flip driven entirely by label confidence. The section below explains
what that spread actually was.

The detector sweep (`detectors.md`) independently reattributed the base-fee spike: the fee peaked at 1.012 gwei, 15.1x
the 0.067 gwei window median, across 202 blocks, and `0x4313c378` — the tokenized-stock router named by hand in the
original note — holds 12.3% of requested gas inside the spike against 2.6% outside it. The detector was not given that
address.

## What is checked, and what is not

The `[[verify: id]]` markers above name recipes in `scripts/verify.py` that re-derive that number from the raw blocks
through a path sharing no aggregation code with `analyze`; `live_scan verify --out <this window>` prints both readings
side by side. Most of this note carries no marker, and that is the useful part of the count: the tape prices in
section 1, the gas-share arithmetic in section 2, the blob counts in section 3, the health factors in section 5, the
StacyVault flash sizes in section 6 and the poisoning-bot counts in section 7 are single readings out of
`analysis.json`, `events.json` and `followups.json`. Tagging them means writing the check first.

## Second correction, 2026-09-08 (one address was the whole USDC outflow)

The `mislabelled_flow` detector flagged the same address in this window and the midday one, both times at high
severity: [0x3cc9…cf18](https://etherscan.io/address/0x3cc936b795a188f0e246cbb2d74c5bd190aecf18), tagged
`exchange_deposit` by the day study, received $196k of small legs here and forwarded **$99.99M of USDC in a single
transaction**. Blockscout says it is an externally-owned account. Its destination,
[0xc906…8ac1](https://etherscan.io/address/0xc906895c8833481571118f0c59877bff6be38ac1), is a verified Gnosis Safe,
which forwarded the whole amount on again.

Counting that leg as exchange outflow is wrong under either reading of the address. If it is an exchange deposit
address, the sweep goes to exchange infrastructure and the leg is internal, not an outflow. If it is not, the leg is
not exchange flow at all. Both readings agree, so the tag was retired without having to settle the identity: it is now
`eoa`, and the Safe is registered with its verified name.

| headline, five-hour window | with the deposit-sink tag | corrected |
|---|---:|---:|
| exchange net flow, stables [[verify: exchange-net-stables]] | −$24.8M | **+$75.2M** |
| exchange net flow, USDC | −$97.9M | **+$2.0M** |
| exchange net flow, USDT | +$74.8M | +$74.8M |
| exchange net flow, ETH [[verify: exchange-net-eth]] | +$12.8M | +$12.8M |
| label band, model-memory → behaviour | +$91.6M → −$24.8M | +$91.6M → +$75.2M |

One behaviour-tier tag on one address was the entire USDC outflow of the window and the whole of the sign flip in the
label band. The band that made this note flag its own uncertainty was measuring a single bad label, and the corrected
band no longer changes sign.

This is the third mislabel of the same family — after the CoW settlement contract and the deposit-sink rule itself —
and the first found by a detector rather than by hand, on the second window it appeared in. That is the loop working
as intended: the rule that produced the tag was fixed in the code, the tag it left behind was caught by the check that
tests labels against the window's own behaviour, and the ledger recorded that it recurred before anyone looked.


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 477 | $25.4M | $229 | $0 | $228 | $39.2B | 0.00% | 0.2% | 67.426% |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 3756 | $12.9M | $6462 | $61 | $6401 | $511.1M | 2.19% | 441.8% | 2.070% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 471 | $10.4M | $31k | $0 | $31k | $1.8B | 3.09% | 623.5% | 1.563% |
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 196 | $10.3M | $62 | $0 | $62 | $100.0B | 0.00% | 0.0% | 0.010% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 50 | $5.9M | $35 | $0 | $35 | $149.1B | 0.00% | 0.0% | 0.004% |
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 53 | $5.7M | – | $0 | – | – | – | – | – |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 4454 | $5.5M | $555 | $0 | $554 | $49.9M | 1.95% | 392.2% | 2.164% |
| 0x5459…df9a | uni v4 | tBTC/cbBTC | 0.01% | 13 | $5.0M | $623 | $0 | $623 | $14.9B | 0.01% | 1.5% | 0.055% |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 2643 | $4.2M | $419 | $1 | $418 | $35.7M | 2.05% | 412.9% | 24.736% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 290 | $3.9M | $39 | $0 | $39 | $10.8B | 0.00% | 0.1% | 2.374% |
| 0x9035…eb4f | uni v4 | RLUSD/USDS | 0.00% | 26 | $2.9M | $18 | $0 | $18 | $40.0B | 0.00% | 0.0% | 0.004% |
| [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) | curve | DAI/USDC | ? | 52 | $2.8M | – | $0 | – | – | – | – | – |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 265 | $2.7M | $1366 | $0 | $1366 | $283.4M | 0.84% | 170.0% | 1.404% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 233 | $2.1M | $1061 | $0 | $1061 | $355.9M | 0.52% | 105.2% | 0.580% |
| [0x73a3…b38b](https://etherscan.io/address/0x73a38006d23517a1d383c88929b2014f8835b38b) | uni v3 | tBTC/WBTC | 0.01% | 75 | $2.1M | $211 | $0 | $211 | $6.2B | 0.01% | 1.2% | 0.051% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 661 | $1.9M | $953 | $5 | $948 | $73.8M | 2.25% | 453.3% | 2.145% |
| [0x5b03…8e96](https://etherscan.io/address/0x5b03cccab7ba3010fa5cad23746cbf0794938e96) | curve | USDe/USDT | ? | 42 | $1.8M | – | $0 | – | – | – | – | – |
| 0xdce6…f78d | uni v4 | ETH/USDC | 0.35% | 108 | $1.8M | $6148 | $0 | $6148 | $289.9M | 3.71% | 748.2% | 1.639% |
| [0x8ad5…e6d8](https://etherscan.io/address/0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8) | uni v3 | USDC/WETH | 0.30% | 649 | $1.7M | $5154 | $0 | $5154 | $273.0M | 3.31% | 666.1% | 1.565% |
| [0xa6cc…93e8](https://etherscan.io/address/0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8) | uni v3 | LINK/WETH | 0.30% | 348 | $1.6M | $4763 | $0 | $4763 | $63.8M | 13.07% | 2633.2% | 4.448% |
| [0xd0fc…6d78](https://etherscan.io/address/0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78) | uni v3 | UNI/USDC | 0.30% | 208 | $1.6M | $4668 | $0 | $4668 | $31.6M | 25.85% | 5209.4% | 5.029% |
| 0x50b0…5fa8 | uni v4 | ETH/USDT | 0.35% | 88 | $1.5M | $5386 | $0 | $5386 | $298.8M | 3.16% | 635.9% | 1.463% |
| 0x21c6…ca27 | uni v4 | ETH/USDC | 0.06% | 433 | $1.3M | $813 | $0 | $813 | $72.7M | 1.96% | 394.7% | 2.047% |
| 0xe500…a657 | uni v4 | USDC/WETH | 0.03% | 325 | $1.2M | $211 | $0 | $211 | $62.3M | 0.59% | 119.5% | 2.039% |
| [0xf4d0…96d7](https://etherscan.io/address/0xf4d0cf32908b2c7f1021339c43df0f77f06896d7) | curve | 0x2323…aa71/USDC | ? | 16 | $1.2M | – | $0 | – | – | – | – | – |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.03% | 321 | $1.1M | $184 | $0 | $184 | $60.4M | 0.53% | 107.8% | 1.934% |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 67 | $1.1M | $33 | $0 | $33 | $10.5B | 0.00% | 0.1% | 0.019% |
| [0x21e2…843a](https://etherscan.io/address/0x21e27a5e5513d6e65c4f830167390997aa84843a) | curve | ?/? | ? | 45 | $1.1M | – | $0 | – | – | – | – | – |
| [0x7ac9…796a](https://etherscan.io/address/0x7ac940038125796a) | balancer | WBTC/USDT | ? | 39 | $1.0M | – | $0 | – | – | – | – | – |
| [0xb7ec…6726](https://etherscan.io/address/0xb7ecb2aa52aa64a717180e030241bc75cd946726) | curve | tBTC/WBTC | ? | 21 | $956k | – | $0 | – | – | – | – | – |
| [0x1d42…d801](https://etherscan.io/address/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801) | uni v3 | UNI/WETH | 0.30% | 294 | $900k | $2700 | $0 | $2700 | $18.9M | 24.98% | 5033.4% | 3.608% |
| [0xdc24…7022](https://etherscan.io/address/0xdc24316b9ae028f1497c275eb9192a3ea0f67022) | curve | ?/? | ? | 16 | $889k | – | $0 | – | – | – | – | – |
| 0x00b9…22d7 | uni v4 | ETH/USDC | 0.01% | 1333 | $888k | $111 | $0 | $111 | $26.0M | 0.74% | 150.1% | 68.464% |
| [0xdb74…ded5](https://etherscan.io/address/0xdb74dfdd3bb46be8ce6c33dc9d82777bcfc3ded5) | curve | WETH/weETH | ? | 11 | $854k | – | $0 | – | – | – | – | – |
| [0x0b59…6460](https://etherscan.io/address/0x0b599ebf4e05af48b56d38e2dde520570c366460) | uni v3 | WBTC/LBTC | 0.01% | 13 | $790k | $79 | $0 | $79 | $1.6B | 0.01% | 1.8% | 0.445% |
| [0xe8f7…e124](https://etherscan.io/address/0xe8f7c89c5efa061e340f2d2f206ec78fd8f7e124) | uni v3 | WBTC/cbBTC | 0.01% | 9 | $755k | $75 | $0 | $75 | $47.5B | 0.00% | 0.1% | 0.006% |
| [0xc061…1622](https://etherscan.io/address/0xc061caa073f3d95f80f8e5428d32d2d76f5e1622) | curve | USDC/USDG | ? | 16 | $678k | – | $0 | – | – | – | – | – |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 259 | $665k | $67 | $0 | $66 | $31.1B | 0.00% | 0.1% | 0.004% |
| 0x8aa4…4e47 | uni v4 | ETH/USDT | 0.00% | 142 | $641k | $8 | $0 | $8 | $18.1B | 0.00% | 0.0% | 0.005% |
| [0x383e…8559](https://etherscan.io/address/0x383e6b4437b59fff47b619cba855ca29342a8559) | curve | PYUSD/USDC | ? | 69 | $641k | – | $0 | – | – | – | – | – |
| [0x4dec…d69e](https://etherscan.io/address/0x4dece678ceceb27446b35c672dc7d61f30bad69e) | curve | USDC/crvUSD | ? | 78 | $577k | – | $0 | – | – | – | – | – |
| 0xff14…3b72 | uni v4 | NVDAon/USDC | 1.00% | 1206 | $566k | $5658 | $0 | $5658 | $5.0M | 197.95% | 39885.9% | 2.492% |
| 0x5993…615e | uni v4 | ETH/WBTC | 0.06% | 133 | $558k | $349 | $0 | $349 | $119.2M | 0.51% | 103.2% | 0.541% |
| 0xb90d…b716 | uni v4 | USDC/USDG | 0.01% | 43 | $548k | $45 | $0 | $45 | $20.7B | 0.00% | 0.1% | 0.006% |
| [0xb31e…5bc3](https://etherscan.io/address/0xb31e70454bdf5bc3) | balancer | USDC/WETH | ? | 32 | $535k | – | $0 | – | – | – | – | – |

Just-in-time liquidity: 144 episodes (mint and burn of identical liquidity inside one block), bracketing $364k of swaps and taking about $235 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 55 episodes, fees taken $108
- [0x27c2…2bf2](https://etherscan.io/address/0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2): 11 episodes, fees taken $21
- [0x7556…b063](https://etherscan.io/address/0x7556699aa8e6a7c9c69bcfaf9debd05f8192b063): 9 episodes, fees taken $0
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 8 episodes, fees taken $1
- [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de): 8 episodes, fees taken $67
- [0xe204…4ae5](https://etherscan.io/address/0xe20446cccbfd5f9038e747f1dea8016ecbd94ae5): 6 episodes, fees taken $0
- [0xce54…f556](https://etherscan.io/address/0xce54f65abb8b61b83c14cbe97de97fce75bbf556): 3 episodes, fees taken $0
- [0x87a9…db07](https://etherscan.io/address/0x87a97b7766f9f0c22adbf44f89188fb00159db07): 3 episodes, fees taken $0

Swap volume by venue: uniswap_v4 $74.4M (23255), uniswap_v3 $61.8M (36411), curve $21.1M (2234), uniswap_v2_like $8.5M (13969), balancer $1.9M (457).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0xdbeb…8cb3 (0x0000…0000/0x8602…2148, 1956 swaps); 0x6f2c…7a39 (0x0000…0000/0x41f3…abc7, 432 swaps); 0x1271…75aa (0xb58e…21cb/0xcedb…f8e7, 237 swaps); 0xfabe…8a17 (0x0000…0000/0xf76c…7531, 208 swaps); 0xef50…8e75 (0xc9ee…5581/0xe413…36e4, 177 swaps); 0x459b…0a5b (0x0000…0000/0xeaa6…a69a, 162 swaps); 0x21d3…b860 (0x0000…0000/0x833c…9223, 147 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 121 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 119 swaps); 0xd47e…4e09 (0x0000…0000/0xe35c…e51d, 117 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | WBTC | 0.00% | 0.34% | 2.8% | $2.7B | $75.4M |
| Aave v3 | GHO | 0.00% | 4.00% | 83.0% | $135.2M | $112.2M |
| Aave v3 | USDe | 1.70% | 5.40% | 41.9% | $640.3M | $268.5M |
| Aave v3 | LINK | 0.01% | 0.48% | 3.1% | $119.7M | $3.7M |
| Aave v3 | DAI | 3.04% | 4.69% | 86.4% | $131.8M | $113.8M |
| Aave v3 | PYUSD | 3.75% | 4.83% | 86.2% | $7.7M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.9B | $7.3M |
| Aave v3 | RLUSD | 2.17% | 4.42% | 61.5% | $4.6M | $2.9M |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $280.0M | $0 |
| Aave v3 | USDC | 3.59% | 4.27% | 93.4% | $2.3B | $2.2B |
| Aave v3 | WETH | 1.43% | 2.03% | 82.7% | $5.3B | $4.4B |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.6% | $1.5B | $9.6M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $139k |
| Aave v3 | USDT | 3.50% | 4.22% | 92.2% | $3.0B | $2.7B |
| Aave v3 | USDS | 0.12% | 5.52% | 3.0% | $11.2M | $335k |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $143.1M | $331k |
| SparkLend | GHO | 0.00% | 0.00% | – | – | – |
| SparkLend | USDe | 0.00% | 0.00% | – | – | – |
| SparkLend | LINK | 0.00% | 0.00% | – | – | – |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $308.2M | $208.6M |
| SparkLend | PYUSD | 0.58% | 3.89% | 16.6% | $100.0M | $16.6M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9939 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sUSDe | 0.00% | 0.00% | – | – | – |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $25.6M | $23.6M |
| SparkLend | WETH | 1.57% | 1.98% | 83.5% | $1.2B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.02% | 1.3% | $285.7M | $3.8M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $105.2M | $0 |
| SparkLend | USDT | 6.05% | 7.00% | 96.0% | $344.4M | $330.6M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $733.4M | $481.2M |
| Compound v3 USDC | base | 5.49% | 6.54% | 90.7% | $373.1M | $338.4M |
| Compound v3 USDT | base | 3.00% | 3.81% | 83.2% | $185.4M | $154.2M |
| Compound v3 WETH | base | 1.37% | 1.88% | 68.5% | $125.2M | $85.7M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.47% APR on $1.4B of USDe.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | PYUSD | 8 | 4.83% → 4.83% | 4.54% – 25.76% | 3.75% → 3.75% |
| SparkLend | USDT | 16 | 3.52% → 7.00% | 3.52% – 7.00% | 2.62% → 6.05% |
| Aave v3 | USDG | 15 | 3.35% → 3.05% | 3.05% – 3.35% | 1.44% → 1.19% |
| Aave v3 | RLUSD | 3 | 4.42% → 4.42% | 4.42% – 4.56% | 2.17% → 2.17% |
| SparkLend | USDS | 9 | 3.93% → 3.93% | 3.93% – 4.01% | 2.32% → 2.32% |
| Aave v3 | USDS | 2 | 5.52% → 5.57% | 5.52% – 5.57% | 0.12% → 0.36% |
| Aave v3 | USDT | 203 | 4.22% → 4.22% | 4.22% – 4.24% | 3.51% → 3.50% |
| Aave v3 | USDC | 414 | 4.27% → 4.27% | 4.26% – 4.28% | 3.60% → 3.59% |
| Aave v3 | USDe | 26 | 5.41% → 5.40% | 5.40% – 5.42% | 1.72% → 1.70% |
| Aave v3 | WETH | 293 | 2.03% → 2.03% | 2.02% – 2.03% | 1.42% → 1.43% |
| SparkLend | USDC | 8 | 4.27% → 4.27% | 4.27% – 4.28% | 3.54% → 3.54% |
| Aave v3 | EURC | 6 | 3.86% → 3.86% | 3.85% – 3.86% | 2.20% → 2.19% |
| Aave v3 | LINK | 21 | 0.48% → 0.48% | 0.48% – 0.48% | 0.01% → 0.01% |
| SparkLend | WETH | 19 | 1.97% → 1.98% | 1.97% – 1.98% | 1.57% → 1.57% |
| Aave v3 | cbBTC | 11 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| Aave v3 | CRV | 2 | 5.77% → 5.77% | 5.77% – 5.77% | 0.47% → 0.47% |
| Aave v3 | tBTC | 5 | 0.26% → 0.26% | 0.26% – 0.26% | 0.00% → 0.00% |
| Aave v3 | WBTC | 34 | 0.34% → 0.34% | 0.34% – 0.34% | 0.00% → 0.00% |
| Aave v3 | wstETH | 17 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | USDtb | 1 | 14.27% → 14.27% | 14.27% – 14.27% | 9.60% → 9.60% |
| Aave v3 | GHO | 9 | 4.00% → 4.00% | 4.00% – 4.00% | 0.00% → 0.00% |
| Aave v3 | 0x6874…2f38 | 7 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 3 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | cbBTC | 11 | 0.02% → 0.02% | 0.02% – 0.02% | 0.00% → 0.00% |
| Aave v3 | rETH | 4 | 0.02% → 0.02% | 0.02% – 0.02% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: withdraw $64.3M, borrow $36.5M, repay $42.9M, supply $52.0M, atomic withdraw $174.9M, atomic supply $177.8M, atomic borrow $2.9M, atomic repay $335; SparkLend: supply $16.4M, borrow $18.1M, repay $517k, withdraw $47.4M, atomic supply $12.0M, atomic borrow $9.8M, atomic repay $9.8M, atomic withdraw $12.0M.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25923948 | SparkLend | withdraw | USDT | $46.4M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0xc0ce…b35c](https://etherscan.io/tx/0xc0ce97bdae9884eea677214ad02bbfb1674e9c6022d2a105161d406e03c0b35c) |
| 25923840 | SparkLend | supply | USDS | $15.2M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x6ef9…2aca](https://etherscan.io/tx/0x6ef999aae3d3ff05f92227626bdae9f32fee2f783d6ccf133967c3e98b652aca) |
| 25923837 | SparkLend | borrow | USDS | $10.0M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0x90bf…0697](https://etherscan.io/tx/0x90bf401836573b998354eec588e023bdfbd7bdbedeae74510d3b471fb4490697) |
| 25922576 | Aave v3 | borrow | USDT | $10.0M | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | [0x45b9…1708](https://etherscan.io/tx/0x45b91ca15010efb6468b20ed42038785fb64eb996e34fab82538c49b55881708) |
| 25923930 | SparkLend | borrow | USDT | $7.2M | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | [0xd10b…f8f4](https://etherscan.io/tx/0xd10ba1aa15fb2825b6e82cc685fbc8447357e20e63351f2edaf1c9de3bcbf8f4) |
| 25923930 | Aave v3 | repay | USDT | $7.2M | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | [0xd10b…f8f4](https://etherscan.io/tx/0xd10ba1aa15fb2825b6e82cc685fbc8447357e20e63351f2edaf1c9de3bcbf8f4) |
| 25923961 | Aave v3 | repay | USDT | $5.1M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xbce2…98cc](https://etherscan.io/tx/0xbce28d04cdd31823e1fab81defb0f41a2a05d8a90724828033e56dcbbbed98cc) |
| 25923961 | Aave v3 | borrow | USDT | $5.1M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x1978…4cf6](https://etherscan.io/tx/0x1978c9e59ca801c96e5703159142d4161bb5b5c649f0dfb0d992262cdaf84cf6) |
| 25923961 | Aave v3 | supply | USDC | $5.1M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x1978…4cf6](https://etherscan.io/tx/0x1978c9e59ca801c96e5703159142d4161bb5b5c649f0dfb0d992262cdaf84cf6) |
| 25923999 | Aave v3 | repay | USDT | $3.6M | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0xedda…ae65](https://etherscan.io/tx/0xedda71ed71e9ee3f73b4e62d684098d41bd01763ea4e459556be660603b2ae65) |
| 25924006 | Aave v3 | borrow | USDC | $3.6M | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x27f0…e75d](https://etherscan.io/tx/0x27f0a0a347846390f6fcc66b49db2b4ff9115bde04a46c05f2d439feef45e75d) |
| 25923312 | Aave v3 | repay | USDC | $3.3M | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x547b…096a](https://etherscan.io/tx/0x547ba8c2f2acd91e196740b941cb3cc3d3b36750013d72fd93e807bb3420096a) |
| 25923838 | Aave v3 | repay | USDT | $2.9M | [0x13ff…55b7](https://etherscan.io/address/0x13ffb3286d8d371785e6288588be88e4356555b7) | [0xd5b3…8e3e](https://etherscan.io/tx/0xd5b33de96ec0865dd108f5c6051f679010e85f3980dcd7c8968a555558058e3e) |
| 25923838 | Aave v3 | borrow | WETH | $2.9M | [0x13ff…55b7](https://etherscan.io/address/0x13ffb3286d8d371785e6288588be88e4356555b7) | [0xd5b3…8e3e](https://etherscan.io/tx/0xd5b33de96ec0865dd108f5c6051f679010e85f3980dcd7c8968a555558058e3e) |
| 25922976 | Aave v3 | withdraw | USDe | $2.8M | [0xd938…48dd](https://etherscan.io/address/0xd93814273b33dd33b32cd345225cfb65deb048dd) | [0x6cd1…faa8](https://etherscan.io/tx/0x6cd1c1c1b7e2843e419424b4ea8c83fd838c7d0f1a4c7a43154a8a25f79efaa8) |
| 25922915 | Aave v3 | withdraw | cbBTC | $2.7M | [0xfd81…a62a](https://etherscan.io/address/0xfd81b27d9796a1ba7d7171ea70010c9befb2a62a) | [0x9c4c…4c7c](https://etherscan.io/tx/0x9c4c4b2148d90438430b0ba96c1ec68571363f085092672bb654ac14a2364c7c) |
| 25923052 | Aave v3 | repay | USDT | $2.6M | [0xd938…48dd](https://etherscan.io/address/0xd93814273b33dd33b32cd345225cfb65deb048dd) | [0xce6c…4926](https://etherscan.io/tx/0xce6c21da0b5aa2582b3c22453d49e9881436d510c1c5fe310a743ec61c604926) |
| 25922612 | Aave v3 | supply | USDC | $2.3M | [0xf63b…c3d1](https://etherscan.io/address/0xf63bc7e7e3f85c2596894e408c0ef19e4a22c3d1) | [0xc3da…b7a0](https://etherscan.io/tx/0xc3dac236390ed07135aab673661229f8fd337ff7bddeb00777287b9489efb7a0) |
| 25923655 | Aave v3 | supply | USDT | $2.1M | [0x5a41…28e8](https://etherscan.io/address/0x5a41d2cdf4ce4ca39d2152e6fd05a8253c2e28e8) | [0xacd2…a91f](https://etherscan.io/tx/0xacd290616189faad3875a83233bf72c43af8347e496a59496194ad36070da91f) |
| 25922560 | Aave v3 | withdraw | tBTC | $2.0M | [0xfd81…a62a](https://etherscan.io/address/0xfd81b27d9796a1ba7d7171ea70010c9befb2a62a) | [0xab8a…3c76](https://etherscan.io/tx/0xab8a352fcc1f9f2bd67b1ba835fc68824e19e9e5e4031fa3ef250e4b0eec3c76) |
| 25922577 | Aave v3 | supply | cbBTC | $2.0M | [0xfd81…a62a](https://etherscan.io/address/0xfd81b27d9796a1ba7d7171ea70010c9befb2a62a) | [0x2ff9…c75b](https://etherscan.io/tx/0x2ff92eba2fe33b500599f2031ce95cde0e76fe0b8410df265fde547c8570c75b) |
| 25922778 | Aave v3 | withdraw | WETH | $1.4M | [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) | [0xe2ab…ad61](https://etherscan.io/tx/0xe2ab52584d4c3cf9f3a8a4a3633809db7533e96b29bfb85dff5b8d339895ad61) |
| 25922992 | Aave v3 | withdraw | USDT | $1.1M | [0x1f5b…19ee](https://etherscan.io/address/0x1f5bd76d597c7fd18848c7b89c6b26f23e4e19ee) | [0xacbf…2e7e](https://etherscan.io/tx/0xacbf503f6df138773bcb64ef40acc711bfcc2280effe7832b2c9c292f58d2e7e) |
| 25922924 | Aave v3 | supply | WETH | $1.1M | [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) | [0x71cb…9cee](https://etherscan.io/tx/0x71cbf7299974f6169561e578d7861252bc8bc45f8dddcd58a132949de5409cee) |
| 25922924 | Aave v3 | withdraw | WETH | $1.1M | [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) | [0x1463…1a74](https://etherscan.io/tx/0x14630df59cc5dccd4eab5fc6e1e0a72daf07b0b863813d93d9743e0c9c021a74) |
| 25923476 | Aave v3 | supply | WETH | $1.0M | [0x2a2e…3947](https://etherscan.io/address/0x2a2eb5aa8b6911f6b87ab2dbb37d3e9edd153947) | [0x10d2…20eb](https://etherscan.io/tx/0x10d23ea39f5107a1dc385dafba8be18cdc91e5b56b83c57df3a0056369c620eb) |
| 25923175 | SparkLend | supply | wstETH | $993k | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x3d47…0853](https://etherscan.io/tx/0x3d4784e8f095c9861b7bb5ee93eeab9485343b6bbd346e22cb9ad87d41500853) |
| 25923175 | SparkLend | borrow | WETH | $889k | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0x3d47…0853](https://etherscan.io/tx/0x3d4784e8f095c9861b7bb5ee93eeab9485343b6bbd346e22cb9ad87d41500853) |
| 25922924 | Aave v3 | repay | USDC | $838k | [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) | [0x1463…1a74](https://etherscan.io/tx/0x14630df59cc5dccd4eab5fc6e1e0a72daf07b0b863813d93d9743e0c9c021a74) |
| 25923364 | Aave v3 | withdraw | USDT | $796k | [0x5d78…be12](https://etherscan.io/address/0x5d7823e7f027fecbf56bc3538757fc8331eebe12) | [0xbe7d…cda9](https://etherscan.io/tx/0xbe7d2356e5f38a8e47ddac94aaaa226d091edd349d957fad295e42963d8bcda9) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- SparkLend withdraw $46.4M USDT by [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) ([0xc0ce…b35c](https://etherscan.io/tx/0xc0ce97bdae9884eea677214ad02bbfb1674e9c6022d2a105161d406e03c0b35c)): $75.4M → [Spark Savings USDT (spUSDT) (blockscout-verified)](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372); $162k → [Spark Savings USDT (spUSDT) (blockscout-verified)](https://etherscan.io/address/0xe2e7a17dff93280dec073c995595155283e3c372)
- SparkLend borrow $10.0M USDS by [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) ([0x90bf…0697](https://etherscan.io/tx/0x90bf401836573b998354eec588e023bdfbd7bdbedeae74510d3b471fb4490697)): $10.0M → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)
- Aave v3 borrow $10.0M USDT by [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) ([0x45b9…1708](https://etherscan.io/tx/0x45b91ca15010efb6468b20ed42038785fb64eb996e34fab82538c49b55881708)): $10.0M → [0x54d2…6029](https://etherscan.io/address/0x54d250405d22e858d125ce2c1affc7d73afe6029)
- SparkLend borrow $7.2M USDT by [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) ([0xd10b…f8f4](https://etherscan.io/tx/0xd10ba1aa15fb2825b6e82cc685fbc8447357e20e63351f2edaf1c9de3bcbf8f4)): $7.2M → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a)
- Aave v3 borrow $5.1M USDT by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x1978…4cf6](https://etherscan.io/tx/0x1978c9e59ca801c96e5703159142d4161bb5b5c649f0dfb0d992262cdaf84cf6)): $5.1M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $5.1M → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a)
- Aave v3 borrow $2.9M WETH by [0x13ff…55b7](https://etherscan.io/address/0x13ffb3286d8d371785e6288588be88e4356555b7) ([0xd5b3…8e3e](https://etherscan.io/tx/0xd5b33de96ec0865dd108f5c6051f679010e85f3980dcd7c8968a555558058e3e)): $2.9M → [CoW Protocol settlement (GPv2Settlement) (known-canonical)](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41); $2.9M → [0x68c8…4eb8](https://etherscan.io/address/0x68c83eef09b6364f7429b09d404cf9be015c4eb8); $2.9M → [0xdecc…f192](https://etherscan.io/address/0xdecc46a4b09162f5369c5c80383aaa9159bcf192); $11k → [0x13ff…55b7](https://etherscan.io/address/0x13ffb3286d8d371785e6288588be88e4356555b7)
- Aave v3 withdraw $2.8M USDe by [0xd938…48dd](https://etherscan.io/address/0xd93814273b33dd33b32cd345225cfb65deb048dd) ([0x6cd1…faa8](https://etherscan.io/tx/0x6cd1c1c1b7e2843e419424b4ea8c83fd838c7d0f1a4c7a43154a8a25f79efaa8)): $2.8M → [0x50cf…5c4a](https://etherscan.io/address/0x50cfe7c1938db66a1a6d2e86d36f39fbef3d5c4a)
- Aave v3 withdraw $2.0M tBTC by [0xfd81…a62a](https://etherscan.io/address/0xfd81b27d9796a1ba7d7171ea70010c9befb2a62a) ([0xab8a…3c76](https://etherscan.io/tx/0xab8a352fcc1f9f2bd67b1ba835fc68824e19e9e5e4031fa3ef250e4b0eec3c76)): $2.0M → [CoW Protocol settlement (GPv2Settlement) (known-canonical)](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41)
- Aave v3 withdraw $1.1M USDT by [0x1f5b…19ee](https://etherscan.io/address/0x1f5bd76d597c7fd18848c7b89c6b26f23e4e19ee) ([0xacbf…2e7e](https://etherscan.io/tx/0xacbf503f6df138773bcb64ef40acc711bfcc2280effe7832b2c9c292f58d2e7e)): $1.1M → [0x217e…60a3](https://etherscan.io/address/0x217e42ceb2eae9ecb788fdf0e31c806c531760a3)
- Aave v3 withdraw $1.1M WETH by [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) ([0x1463…1a74](https://etherscan.io/tx/0x14630df59cc5dccd4eab5fc6e1e0a72daf07b0b863813d93d9743e0c9c021a74)): $1.1M → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- SparkLend borrow $889k WETH by [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) ([0x3d47…0853](https://etherscan.io/tx/0x3d4784e8f095c9861b7bb5ee93eeab9485343b6bbd346e22cb9ad87d41500853)): $1.3M → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb); $2.7M → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb)
- Aave v3 withdraw $796k USDT by [0x5d78…be12](https://etherscan.io/address/0x5d7823e7f027fecbf56bc3538757fc8331eebe12) ([0xbe7d…cda9](https://etherscan.io/tx/0xbe7d2356e5f38a8e47ddac94aaaa226d091edd349d957fad295e42963d8bcda9)): $796k → [0x217e…60a3](https://etherscan.io/address/0x217e42ceb2eae9ecb788fdf0e31c806c531760a3)
- Aave v3 withdraw $757k WETH by [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ([0x930c…644a](https://etherscan.io/tx/0x930ccd7cd103feaffc9a12388c361c5527130321b80c7f1a14f7ef409713644a)): $757k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- SparkLend withdraw $753k cbBTC by [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) ([0x0a30…a9d4](https://etherscan.io/tx/0x0a301f4aff79fde4ff9f5009b41f4bed62925a73056b613596524fdee0d9a9d4)): $277k → [0x3358…9a98](https://etherscan.io/address/0x3358895b340a41c0075c66530e2587cfc89a9a98) → forwarded to Coinbase 10 (model-memory); $475k → [MainnetSettler (blockscout-verified)](https://etherscan.io/address/0x0889e9327b98d7d1be3c301a4585ff3330502c9a) **[to exchange $277k]**
- Aave v3 borrow $750k USDT by [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) ([0x36a8…451e](https://etherscan.io/tx/0x36a81704dc679e5664554b0bb36766e9fe8c443f11b115642cdd25985eeb451e)): $750k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996); $500k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996); $250k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996)
- Aave v3 borrow $750k USDT by [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) ([0x7303…5943](https://etherscan.io/tx/0x730392f88a3e5c04210bd33604193f45aac209d72efd46554280561534d35943)): $500k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996); $250k → [router or solver (shape: pass-through, 136 txs, 70% flat, 120 counterparties, $215M gross) (behaviour-2026-09-08-fingerprint)](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996)
- Aave v3 withdraw $746k WETH by [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) ([0x2783…f960](https://etherscan.io/tx/0x27839e6be175941916a4b5b851a3b4000be627812a3b9e0c5e8ca5e1c0daf960)): $198k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 borrow $700k USDT by [0x1d7d…1dcb](https://etherscan.io/address/0x1d7ddad2aefa66aadede4822f5f81f0adadd1dcb) ([0x3c45…0e8b](https://etherscan.io/tx/0x3c450d3a35a324bf0f01157365543709b1fd5b29d681f8054fea302c90bd0e8b)): $100k → [0x99c4…1778](https://etherscan.io/address/0x99c4a351b59f3348be4b05d638acb0a727b01778)
- Aave v3 withdraw $657k WETH by [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0xc7f8…1f5d](https://etherscan.io/tx/0xc7f801da5df7e53a0c9f8375ca20867630b1216d0008adb827c3b5a392231f5d)): $657k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $657k → [0x45e9…9215](https://etherscan.io/address/0x45e9b04942176a513b22acc1ced75c34d2fd9215); $13k → [0x59cd…71db](https://etherscan.io/address/0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db); $13k → [0x45e9…9215](https://etherscan.io/address/0x45e9b04942176a513b22acc1ced75c34d2fd9215)
- Aave v3 borrow $631k USDS by [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ([0x7750…6522](https://etherscan.io/tx/0x775025b24320fe1790d909884d7235407564dc35cdd9a31cc05bbdb05d436522)): $631k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $631k → [0x32a6…4259](https://etherscan.io/address/0x32a6268f9ba3642dda7892add74f1d34469a4259)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| Aave v3 | [0xd938…48dd](https://etherscan.io/address/0xd93814273b33dd33b32cd345225cfb65deb048dd) | $237.6M | $217.8M | 1.015 | 1.4% |
| Aave v3 | [0x9992…f242](https://etherscan.io/address/0x99926ab8e1b589500ae87977632f13cf7f70f242) | $355.4M | $180.7M | 1.624 | 38.4% |
| SparkLend | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | $114.4M | $42.8M | 2.296 | 56.4% |
| SparkLend | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | $32.7M | $29.4M | 1.035 | 3.4% |
| Aave v3 | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | $12.1M | $10.8M | 1.026 | 2.5% |
| SparkLend | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | $18.4M | $7.2M | 2.154 | 53.6% |
| Aave v3 | [0x6cc6…c4bd](https://etherscan.io/address/0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd) | $10.0M | $5.6M | 1.430 | 30.1% |
| Aave v3 | [0x13ff…55b7](https://etherscan.io/address/0x13ffb3286d8d371785e6288588be88e4356555b7) | $5.3M | $3.0M | 1.389 | 28.0% |
| Aave v3 | [0x1d7d…1dcb](https://etherscan.io/address/0x1d7ddad2aefa66aadede4822f5f81f0adadd1dcb) | $4.5M | $1.2M | 2.921 | 65.8% |
| Aave v3 | [0xfd81…a62a](https://etherscan.io/address/0xfd81b27d9796a1ba7d7171ea70010c9befb2a62a) | $4.3M | $1.2M | 2.992 | 66.6% |
| Aave v3 | [0x01b3…eaf7](https://etherscan.io/address/0x01b3ba0aa49c3daa72e25031bcd1b4029cf8eaf7) | $1.7M | $1.0M | 1.563 | 36.0% |
| SparkLend | [0xca68…487a](https://etherscan.io/address/0xca686974913389d42f3c5f61010503daccdb487a) | $388k | $249k | 1.279 | 21.8% |
| Aave v3 | [0xb704…96f7](https://etherscan.io/address/0xb7040ffadb77219d9bc7d5fc9e9f848c83cc96f7) | $19k | $13k | 1.188 | 15.8% |
| Aave v3 | [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) | $4 | $0 | 290.435 | 99.7% |
| SparkLend | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | $54.7M | $0 | ∞ | – |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| Aave v3 | [0xf63b…c3d1](https://etherscan.io/address/0xf63bc7e7e3f85c2596894e408c0ef19e4a22c3d1) | $12.3M | $0 | ∞ | – |
| Aave v3 | [0x5a41…28e8](https://etherscan.io/address/0x5a41d2cdf4ce4ca39d2152e6fd05a8253c2e28e8) | $0 | $0 | ∞ | – |
| Aave v3 | [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) | $0 | $0 | ∞ | – |
| Aave v3 | [0x1f5b…19ee](https://etherscan.io/address/0x1f5bd76d597c7fd18848c7b89c6b26f23e4e19ee) | $0 | $0 | ∞ | – |
| Aave v3 | [0x2a2e…3947](https://etherscan.io/address/0x2a2eb5aa8b6911f6b87ab2dbb37d3e9edd153947) | $1.0M | $0 | ∞ | – |
| Aave v3 | [0x5d78…be12](https://etherscan.io/address/0x5d7823e7f027fecbf56bc3538757fc8331eebe12) | $0 | $0 | ∞ | – |
| Aave v3 | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | $0 | $0 | ∞ | – |
| Aave v3 | [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) | $0 | $0 | ∞ | – |

Liquidations: Aave v3 [0xb704…96f7](https://etherscan.io/address/0xb7040ffadb77219d9bc7d5fc9e9f848c83cc96f7) debt $13k, collateral $14k ([0xf314…f0d8](https://etherscan.io/tx/0xf314484f39fea2c1a0fd5716348a30414a667e17f9be482dacef8d4028b0f0d8)).


Flash loans (events): BalFlash 583 ($29.0M), MorphoFlash 1 ($0).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a): 6 transactions, largest leg $30.1M, gross $175.5M; legs: WETH withdraw $172.6M, USDC borrow $2.9M, USDC withdraw $0
- SparkLend account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588): 4 transactions, largest leg $3.4M, gross $21.7M; legs: cbBTC withdraw $12.0M, USDT borrow $5.5M, USDS borrow $4.2M
- Aave v3 account [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb): 2 transactions, largest leg $782k, gross $2.3M; legs: WETH withdraw $2.3M
- Aave v3 account [0xe72b…bcc8](https://etherscan.io/address/0xe72b71f97a4ceb0077e468054b788163e72abcc8): 1 transactions, largest leg $32k, gross $32k; legs: USDe borrow $32k

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 555 | $36.4M | 0.999857 | 0.999826 – 0.999943 | 0.99996 | -1.0 bps |
| USDS | 152 | $14.7M | 0.999953 | 0.999935 – 1 | 1 | -0.5 bps |
| USDe | 141 | $3.7M | 0.99995 | 0.999761 – 1.00005 | 1 | -0.5 bps |
| PYUSD | 49 | $3.4M | 1.00002 | 0.999883 – 1.00011 | 1 | +0.2 bps |
| DAI | 41 | $2.0M | 0.999986 | 0.999795 – 1.00003 | 0.999606 | +3.8 bps |
| RLUSD | 13 | $1.4M | 1.00018 | 1.00017 – 1.00019 | 1 | +1.8 bps |
| USDG | 57 | $1.3M | 1.00002 | 0.999962 – 1.00018 | 1 | +0.2 bps |
| crvUSD | 84 | $1.3M | 1.00002 | 0.999848 – 1.00006 | 1 | +0.2 bps |
| weETH | 14 | $899k | 2740.02 | 2739.69 – 2740.23 | 2740.29 | -1.0 bps |
| wTAO | 275 | $864k | 268.096 | 265.312 – 271.592 | – | – |
| CVX | 174 | $604k | 2.24465 | 2.17954 – 2.33891 | – | – |
| sUSDe | 23 | $547k | 1.24657 | 1.2463 – 1.24667 | 1.2469 | -2.7 bps |
| wstETH | 62 | $511k | 3088.16 | 3062.68 – 3090.28 | 3099.69 | -37.2 bps |
| NVDAon | 370 | $489k | 233.22 | 230.143 – 236.691 | – | – |
| Mog | 122 | $413k | 1.15143e-07 | 1.11241e-07 – 1.17445e-07 | – | – |
| rETH | 28 | $361k | 2904.3 | 2903.38 – 2904.92 | 2909.45 | -17.7 bps |
| AUSD | 6 | $224k | 0.999871 | 0.999786 – 0.999986 | 1 | -1.3 bps |
| AP | 189 | $215k | 0.00239643 | 0.0013635 – 0.004013 | – | – |
| SKY | 117 | $188k | 0.0693019 | 0.0686354 – 0.0699389 | – | – |
| USD1 | 11 | $184k | 0.999509 | 0.998881 – 0.99995 | 1 | -4.9 bps |
| PEPE | 51 | $160k | 3.56934e-06 | 3.5473e-06 – 3.5891e-06 | – | – |
| CFG | 109 | $159k | 0.127722 | 0.119133 – 0.133987 | – | – |
| GHO | 17 | $146k | 0.998635 | 0.998702 – 0.999257 | 1 | -13.7 bps |
| STOCKER | 90 | $128k | 0.00345479 | 0.00244081 – 0.00444187 | – | – |
| frxUSD | 26 | $96k | 0.999926 | 0.999737 – 1.00003 | 1 | -0.7 bps |
| 1INCH | 79 | $88k | 0.0940705 | 0.0927245 – 0.0959211 | – | – |
| LIT | 77 | $71k | 4.38687 | 4.3378 – 4.43308 | – | – |
| ENA | 55 | $63k | 0.173458 | 0.171544 – 0.174766 | – | – |
| TSLAon | 58 | $54k | 357.389 | 353.182 – 363.538 | – | – |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 188 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDT | $281.5M | $206.8M | $74.8M |
| ETH | $99.6M | $86.8M | $12.8M |
| USDC | $90.9M | $88.8M | $2.0M |
| cbBTC | $7.3M | $4.3M | $3.0M |
| RLUSD | $5.0M | $5.9M | $-889k |
| LINK | $4.1M | $3.2M | $906k |
| UNI | $2.2M | $2.9M | $-716k |
| WBTC | $3.8M | $722k | $3.1M |
| CRV | $1.5M | $703k | $831k |
| AAVE | $1.8M | $393k | $1.4M |
| USD1 | $2.0M | $191k | $1.8M |
| USDG | $318k | $1.4M | $-1.1M |

By label: Binance 14 (model-memory) in $224.2M / out $37.2M; hot wallet (behaviour, day study) in $60.5M / out $94.8M; Bitget (model-memory) in $86.9M / out $52.7M; Coinbase 10 (model-memory) in $52.0M / out $37.0M; Coinbase 11 (model-memory) in $33.7M / out $33.4M; Gate.io (model-memory) in $23.4M / out $21.5M; Binance 17 (model-memory) in $0 / out $33.0M; Bitfinex 2 (model-memory) in $2.1M / out $30.0M; hot wallet (day study, unidentified) (model-memory) in $14.4M / out $17.3M; Binance 15 (model-memory) in $0 / out $19.0M; Binance 16 (model-memory) in $0 / out $10.3M; Binance 18 (model-memory) in $0 / out $9.2M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25922752 | WBTC | $436.5M ×8 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xc3d8…43ad](https://etherscan.io/tx/0xc3d889a052582e767ac24e81117182726a4de7e522523ec9f5656a084eb443ad) |
| 25922752 | WBTC | $436.5M ×8 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xc3d8…43ad](https://etherscan.io/tx/0xc3d889a052582e767ac24e81117182726a4de7e522523ec9f5656a084eb443ad) |
| 25923300 | WBTC | $396.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x71ce…a14a](https://etherscan.io/tx/0x71ce3c7ff045bd673b59dee19896238898b870578fac1a718389745927e5a14a) |
| 25923300 | WBTC | $396.8M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x71ce…a14a](https://etherscan.io/tx/0x71ce3c7ff045bd673b59dee19896238898b870578fac1a718389745927e5a14a) |
| 25923542 | USDC | $129.0M | [0x7702…63de](https://etherscan.io/address/0x77021d475e36b3ab1921a0e3a8380f069d3263de) | [0x4e67…3cac](https://etherscan.io/address/0x4e67722883ad992182e83b79bf06a93972963cac) | [0x19b7…a498](https://etherscan.io/tx/0x19b75e4833dd6201b96cb3c60e0d53f902b1450f50e6bd1130a2f6bbdee3a498) |
| 25923157 | USDC | $129.0M | [0x0f89…fcbf](https://etherscan.io/address/0x0f896345b538ac140ac84f3367a65a34efd8fcbf) | [0x763c…c131](https://etherscan.io/address/0x763c1967c7016fbfa2611c9503fd9f1bb12ac131) | [0x5a46…30e5](https://etherscan.io/tx/0x5a46f14d5ea4b05b958bff48f2daff5ad9f24598c779e59d27d2cad4dc5f30e5) |
| 25923162 | USDC | $129.0M | [0x763c…c131](https://etherscan.io/address/0x763c1967c7016fbfa2611c9503fd9f1bb12ac131) | [0x7702…63de](https://etherscan.io/address/0x77021d475e36b3ab1921a0e3a8380f069d3263de) | [0xfdf1…2841](https://etherscan.io/tx/0xfdf1c1d96d5fa9698c7d4b8be1c87ad9f16177cf16494fdc814cda04f4352841) |
| 25923493 | USDC | $106.0M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x7966…ee94](https://etherscan.io/address/0x7966319bab61f7d6473a64277897885893c2ee94) | [0x540b…9ea7](https://etherscan.io/tx/0x540b754e41b418f4b1b00de53e519bad6591cb2e245d6e4ca345a89387e89ea7) |
| 25923493 | USDC | $106.0M | [0x7966…ee94](https://etherscan.io/address/0x7966319bab61f7d6473a64277897885893c2ee94) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x540b…9ea7](https://etherscan.io/tx/0x540b754e41b418f4b1b00de53e519bad6591cb2e245d6e4ca345a89387e89ea7) |
| 25923309 | USDC | $105.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x3aaa…cfef](https://etherscan.io/tx/0x3aaad86d22af8309bcc11850fb2391459fdaf49319950e8a579acc0daa17cfef) |
| 25923309 | USDC | $105.7M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3aaa…cfef](https://etherscan.io/tx/0x3aaad86d22af8309bcc11850fb2391459fdaf49319950e8a579acc0daa17cfef) |
| 25923445 | USDC | $104.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x9235…4027](https://etherscan.io/tx/0x9235071d21d5483dd1976d2cc3fa05462bb261876986b3edec385415e1c64027) |
| 25923445 | USDC | $104.8M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x9235…4027](https://etherscan.io/tx/0x9235071d21d5483dd1976d2cc3fa05462bb261876986b3edec385415e1c64027) |
| 25923588 | USDC | $104.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x7e39…7fab](https://etherscan.io/tx/0x7e39b3cfe6f9be7fe54b73c627d049cd4ea7e16f7ad1209d5e7de50d1d757fab) |
| 25923588 | USDC | $104.5M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x7e39…7fab](https://etherscan.io/tx/0x7e39b3cfe6f9be7fe54b73c627d049cd4ea7e16f7ad1209d5e7de50d1d757fab) |
| 25923729 | USDC | $103.3M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x834a…4fac](https://etherscan.io/tx/0x834a8f6de598aa4c8f4375cf3754b8a0511832fc4d9653f4bda8f6e475694fac) |
| 25923729 | USDC | $103.3M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x834a…4fac](https://etherscan.io/tx/0x834a8f6de598aa4c8f4375cf3754b8a0511832fc4d9653f4bda8f6e475694fac) |
| 25923093 | USDC | $102.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xb152…0e42](https://etherscan.io/tx/0xb1523be0438ef4c7b93e2d7dfca0bea6d33d0d2841575df14c1f03099efb0e42) |
| 25923093 | USDC | $102.7M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xb152…0e42](https://etherscan.io/tx/0xb1523be0438ef4c7b93e2d7dfca0bea6d33d0d2841575df14c1f03099efb0e42) |
| 25922556 | USDC | $101.8M ×2 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xa65b…0976](https://etherscan.io/tx/0xa65b4f219d47f759777a4651cf6e3cec4a157ee73fa45b400a7da9e770450976) |
| 25922556 | USDC | $101.8M ×2 | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xa65b…0976](https://etherscan.io/tx/0xa65b4f219d47f759777a4651cf6e3cec4a157ee73fa45b400a7da9e770450976) |
| 25922752 | USDC | $100.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xc3d8…43ad](https://etherscan.io/tx/0xc3d889a052582e767ac24e81117182726a4de7e522523ec9f5656a084eb443ad) |
| 25922752 | USDC | $100.9M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xc3d8…43ad](https://etherscan.io/tx/0xc3d889a052582e767ac24e81117182726a4de7e522523ec9f5656a084eb443ad) |
| 25923987 | USDC | $100.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xd484…72cf](https://etherscan.io/tx/0xd484a1e349665883d81fc76ca96f19c00f55340acff73203efd8cab4236372cf) |
| 25923987 | USDC | $100.9M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd484…72cf](https://etherscan.io/tx/0xd484a1e349665883d81fc76ca96f19c00f55340acff73203efd8cab4236372cf) |
| 25923685 | USDC | $100.0M | [0xc906…8ac1](https://etherscan.io/address/0xc906895c8833481571118f0c59877bff6be38ac1) | [0xbcb3…0e49](https://etherscan.io/address/0xbcb302a64adb7f2c8697e17c1e948f5b058f0e49) | [0x5a84…430c](https://etherscan.io/tx/0x5a8446a1c35067e1a205ed40024be1c88a481e707e804ea37706bfbb530c430c) |
| 25922897 | USDC | $100.0M | [0x3cc9…cf18](https://etherscan.io/address/0x3cc936b795a188f0e246cbb2d74c5bd190aecf18) | [0xc906…8ac1](https://etherscan.io/address/0xc906895c8833481571118f0c59877bff6be38ac1) | [0xd226…b7a4](https://etherscan.io/tx/0xd22617e14a5939eff5165f8e702d38d4190097f5796eb303a447f8479141b7a4) |
| 25923842 | USDC | $98.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x008e…3b5a](https://etherscan.io/tx/0x008e3a6b64bd029911c5f3e3cc2db01121c515f310c08a077429537aabbd3b5a) |
| 25923842 | USDC | $98.5M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x008e…3b5a](https://etherscan.io/tx/0x008e3a6b64bd029911c5f3e3cc2db01121c515f310c08a077429537aabbd3b5a) |
| 25923224 | USDC | $96.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xfdc5…9086](https://etherscan.io/tx/0xfdc543a53da51bcdfdf9cad96a907bbeb49e67477e661cb168e7a0e7e98e9086) |

Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0x7f32…b888](https://etherscan.io/address/0x7f324545c481f8c150802103a8ee94014251b888) | RLUSD → USDS | 4 | $1.2M | $299k | 1404s | 0.10 | 0.00 | uniswap_v4 4 |
| [0x7f32…b888](https://etherscan.io/address/0x7f324545c481f8c150802103a8ee94014251b888) | USDS → USDT | 4 | $664k | $172k | 1404s | 0.10 | 0.06 | uniswap_v4 4 |
| [0x2835…06f1](https://etherscan.io/address/0x283504f935274046827e023fafc74b328c9c06f1) | WETH → weETH | 4 | $348k | $87k | 120s | 0.00 | 0.43 | curve 4 |
| [0xd9d8…1609](https://etherscan.io/address/0xd9d8f818a7a71ed0e1fe936b991508b0e88b1609) | WETH → USDC | 4 | $143k | $31k | 6252s | 0.25 | 0.34 | uniswap_v3 4 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25923961 | uniswap_v4 | USDT → USDC | $5.1M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x1978…4cf6](https://etherscan.io/tx/0x1978c9e59ca801c96e5703159142d4161bb5b5c649f0dfb0d992262cdaf84cf6) |
| 25923961 | uniswap_v4 | USDC → USDT | $5.1M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xbce2…98cc](https://etherscan.io/tx/0xbce28d04cdd31823e1fab81defb0f41a2a05d8a90724828033e56dcbbbed98cc) |
| 25922935 | uniswap_v4 | USDT → USDC | $2.9M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x60f0…9bab](https://etherscan.io/tx/0x60f00d15dfdeb8c186b7d3a8113f054aa75c593bdad6381f9ab8f6e7adc39bab) |
| 25922935 | uniswap_v4 | USDC → USDT | $2.9M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xff4b…4ac6](https://etherscan.io/tx/0xff4b6648ea9c106c83e542e09e6e2db0994b0acc9b88d07f6f3083fb9cf04ac6) |
| 25923555 | uniswap_v4 | USDC → USDT | $2.8M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x4a7c…8e61](https://etherscan.io/tx/0x4a7c9cd2cea79f5a0efad144426c55f63f67a9fe2ef3591d3a0d45bf73328e61) |
| 25923555 | uniswap_v4 | USDT → USDC | $2.8M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x003b…23ec](https://etherscan.io/tx/0x003bc10e95a3da3788ea7e23e5f4dcc9b80f5177ce9b2bc00bfb0a7281b923ec) |
| 25923322 | uniswap_v2_like | 0x622b…bf2d → WETH | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0x9312…8b5e](https://etherscan.io/tx/0x93123bb354aea3a4a6936749ef70a3cf03c38eae68e2cbbaf76202066e938b5e) |
| 25923322 | uniswap_v2_like | WETH → 0x622b…bf2d | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0x9312…8b5e](https://etherscan.io/tx/0x93123bb354aea3a4a6936749ef70a3cf03c38eae68e2cbbaf76202066e938b5e) |
| 25923300 | uniswap_v4 | cbBTC → tBTC | $2.3M | [0xa79a…dd4c](https://etherscan.io/address/0xa79a356b01ef805b3089b4fe67447b96c7e6dd4c) | [0x21b1…a37f](https://etherscan.io/tx/0x21b1ffc0e5c7354f7c9ae5741bc4ff387e945b22fd6b3a4f9355391ea97da37f) |
| 25923763 | uniswap_v4 | USDT → USDS | $2.1M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x9418…7c3f](https://etherscan.io/tx/0x9418b81ff5053ec3b1b572f26515010032a91200a167d46be9d6025c9fb37c3f) |
| 25923763 | uniswap_v4 | USDS → USDT | $2.1M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x8dfa…86e1](https://etherscan.io/tx/0x8dfabf4231a5002029a553ce8bd0b4be2b90301976c1b650686121f6c71486e1) |
| 25923763 | curve | USDT → USDC | $2.1M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x8dfa…86e1](https://etherscan.io/tx/0x8dfabf4231a5002029a553ce8bd0b4be2b90301976c1b650686121f6c71486e1) |
| 25923763 | curve | USDC → USDT | $2.1M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x9418…7c3f](https://etherscan.io/tx/0x9418b81ff5053ec3b1b572f26515010032a91200a167d46be9d6025c9fb37c3f) |
| 25923094 | uniswap_v4 | USDC → USDT | $1.6M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x8b73…80f6](https://etherscan.io/tx/0x8b738035358543afb1e017880a64688dffbef39ba78a80758d5fb4309e1880f6) |
| 25923094 | uniswap_v4 | USDT → USDC | $1.6M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xf107…8f6f](https://etherscan.io/tx/0xf1072040ecf19a09006bbd6e5f69320c47263e2c310e674157eff0cb2b1c8f6f) |
| 25922569 | uniswap_v4 | tBTC → cbBTC | $1.4M | [0xa784…d46c](https://etherscan.io/address/0xa7842153fde380a864726d0e91f14f6ffab7d46c) | [0xe08c…d990](https://etherscan.io/tx/0xe08c28d26859b41e975e7666e18af8c63fdf75c5cf61a0a393e876e6c4a8d990) |
| 25922785 | uniswap_v3 | 0x27c4…3bde → WETH | $1.3M | [0x9ee1…40df](https://etherscan.io/address/0x9ee180b5d418c300bd61f19bae0f85b1e37040df) | [0x71ae…f149](https://etherscan.io/tx/0x71ae0b027183dc4ee45e0b8cc47c0ba32d93f4555f3b3ab3eee8315e808ef149) |
| 25922548 | uniswap_v3 | USDT → WETH | $1.0M | [0xff59…a77e](https://etherscan.io/address/0xff5910ab899d4d8ca4ff3b99f93a62bddbeda77e) | [0x2e33…a51b](https://etherscan.io/tx/0x2e33d2ffa027c833ee01cc3ce984550ec924a4ca889e9f5980fde0639c07a51b) |

## E. Bridges, issuance, staking

Outbound: $35.2M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $23.2M (336).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| OFT | USDe | eid 30383 | 5 | $7.2M | – |
| CCTP | USDC | Polygon | 33 | $6.9M | 0xf70da97812cb… $4.9M |
| CCTP | USDC | Arbitrum | 38 | $4.8M | 0x0ec7ca94416c… $2.6M |
| OFT | sUSDe | eid 30383 | 2 | $4.1M | – |
| OFT | USDC | BNB | 4 | $2.1M | – |
| OFT | USDT | eid 30420 | 30 | $1.9M | – |
| OFT | USDT | Arbitrum | 11 | $1.4M | – |
| CCTP | USDC | Solana | 47 | $925k | d90f00909acb43… $598k |
| OFT | WBTC | eid 30390 | 1 | $793k | – |
| OFT | USDG | eid 30416 | 21 | $695k | – |
| CCTP | USDC | domain 15 | 20 | $622k | 0xc1062b7c5dc8… $273k |
| OFT | PYUSD | Arbitrum | 16 | $605k | – |
| OFT | USDT | Polygon | 6 | $584k | – |
| OFT | USDG | eid 30274 | 6 | $557k | – |
| OFT | USDG | eid 30339 | 2 | $520k | – |
| OFT | USDT | eid 30383 | 2 | $448k | – |
| CCTP | USDC | domain 19 | 29 | $298k | 0xb21d281dedb1… $116k |
| CCTP | USDC | OP Mainnet | 15 | $205k | 0x3a6a72459518… $114k |
| OFT | USDC | eid 30401 | 6 | $101k | – |
| OFT | USDG | Solana | 1 | $100k | – |

Issuance totals: USDC burn $34.7M (369); USDC mint $25.2M (555). Largest: USDC burn $9.0M ([0xb801…a377](https://etherscan.io/tx/0xb8010003eb0d6a2007bfda19a5ff558df1342d72c9d5f3d0d946afcfa694a377)); USDC mint $5.0M ([0x3c8a…42d2](https://etherscan.io/tx/0x3c8a0a0d0a1c943a43205522d840393e7df7303cafc79b99ed91bb68100742d2)); USDC mint $2.9M ([0x678c…707e](https://etherscan.io/tx/0x678c469351080f1d646e1220ab4980e71efea87071a3e0e5f541a6a865a1707e)); USDC burn $2.6M ([0x2049…6428](https://etherscan.io/tx/0x204981256104f8e3ab9a5a25c92175518c9a24de6082e602ce66c2f185676428)); USDC burn $2.4M ([0xa800…9649](https://etherscan.io/tx/0xa800858faf5b7678f3748eb8bde1c37e3e5e7769be1124da72c62b91b0b09649)).


WETH wrapped 31413 ETH, unwrapped 27714 ETH; Lido staked 168.6 ETH, withdrawal requests 1242.0 ETH; sUSDe cooldowns 9 for $1.7M.


## F. Gas market and block production

Base fee 0.037 → 0.076 gwei (min 0.033, median 0.067, max 1.012); blocks 51% full; median tip 0.072 gwei; 5.0% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 742,  Quasar (quasar.win)  309, BuilderNet 225, Eureka (eurekabuilder.xyz) 72, bobTheBuilder.xyz 16, gethgo1.26.4linux 14.


Most active senders: [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 5100, [0xe883…dd91](https://etherscan.io/address/0xe8832a868c091263ed190a9f4be304a03895dd91) 3107, [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 2534, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 1928, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 1909, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 1721, [hot wallet (behaviour, day study)](https://etherscan.io/address/0xb23360ccdd9ed1b15d45e5d3824bb409c8d7c460) 1288, [Binance 17 (model-memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 1227, [0x4838…5f97](https://etherscan.io/address/0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97) 1205, [Binance 18 (model-memory)](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 1170.


Intent fills: OneInchFilled 1207, CoWTrade 828, UniXFill 203. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

