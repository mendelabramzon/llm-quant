# Insights: ten hours of Robinhood Chain (2026-09-07, 04:06–14:06 UTC)

Narrative written from `analysis.json`, `tables.md`, `followups.md` and the spot checks in `method.md`. Numbers are
for the window unless stated; "fees" are L2 base fees paid (the only fee on this chain).

1. **A $0.7M-per-ten-hours fee machine with a $62 cost of goods.** 3.23M user transactions (90/s, 0.101 s blocks,
   24M gas/s sustained) paid 279.2 ETH (~$696k) at a base fee of 0.30–0.44 gwei, 15× the chain's 0.02 gwei floor.
   The batch poster spent 0.025 ETH on Ethereum for the same window (1,605 batches, 4,815 blobs, blob price
   0.002–0.05 gwei): a revenue-to-settlement ratio of ~11,000:1. L1 data pricing is switched off in ArbOS
   (`gasUsedForL1` = 0 for every transaction), priority fees are ignored (0 of 175,818 bids above 3× base fee were
   charged), and failed transactions still paid 14.2 ETH. The fee account's daily accrual ran 1,300–2,700 ETH/day
   between 09-01 and 09-06 and has been decaying with the base fee (0.89 gwei on 09-04 → 0.31 now); the weekly sweep due
   today at 18:01 UTC will move ~11,700 ETH, 90% to a Robinhood-controlled address (which forwards to a BitGo
   forwarder) and 10% to the Arbitrum DAO's expansion-program safe on L1.

2. **The chain's biggest fee payer is a 31-wallet Relay solver fleet.** RelayApprovalProxyV3 took 185,834
   `permit2TransferAndMulticall` calls (5.7% of transactions) at 908k gas each and burned 54.5 ETH, 19.5% of all fees;
   31 EOAs with ~6,000 calls each sent 98% of them, ~1.9 ETH of gas apiece. The router behind it logged 990k
   `SolverCallExecuted` steps. On the user side, the RelayDepository received 143,571 USDG deposits ($42.9M, average
   $299) from more than 3,000 addresses plus 15,166 native deposits (3,971 ETH), and swept them out in 600 withdrawals:
   app-scale retail order flow executed by Relay's solvers through an aggregator executor (0x8f10b468, 342k `Exchange`
   events) that passes stock tokens and memecoins straight through. The canonical Arbitrum bridge did 250 deposits
   (733 ETH) and 19 withdrawals in the same window; Relay is the chain's real on- and off-ramp.

3. **An unverified 1%-fee router earned more than the sequencer.** 0x65050a9b (TransparentUpgradeableProxy, impl
   unverified, multi-DEX with PancakeSwap/Algebra callbacks) handled 345,782 `swap(...)` calls, 10.7% of all
   transactions, from 3,000+ senders of which 551 sent ≥100 each (28.5% of its traffic). Its `FeeCollected` events sum to
   167.7 ETH (~$418k) plus $13.8k USDG in ten hours, a flat 1% of the ETH leg (0.0002 ETH on a 0.02 ETH buy), implying
   ~16,800 ETH (~$42M) of ETH-side volume. That is 62% of the chain's entire gas revenue accruing to one anonymous
   contract owner; a sister deployment (0xe492912f) added 31k calls. Bitquery's 09-03 investigation saw the same router
   at 1.7M calls/day without identifying it; the calldata (a protocol-tagged route array) and the fee split match a
   trading-terminal or wallet backend, not an aggregator.

4. **Tokenized stocks: $268M moved, nothing issued.** 170 of 199 registry tokens transferred, 1.46M transfers
   (NVDA 353k, SPY 151k, AMD 92k, AAPL 91k) worth ~$268M at reference prices (NVDA $53M, GLD $41M, SPY $31M, AMC
   $14M, AAPL $11M), touching 38,883 addresses. 71% of transfers involve a Uniswap pool; 323k swaps put $59.8M through
   stock/USDG and stock/WETH pools, and Pons memecoin launches now use NVDA, AAPL, SHOP and SLV as the quote asset
   (cyberbeer/NVDA: 38.9k swaps). Zero mints, zero burns and zero admin or oracle events on any stock token, including
   through the 13:30 UTC US open: supply is fixed and all activity is secondary. The US open still doubled the chain:
   the 13:30 bucket had 141,562 transactions (1.9× the pre-open median), 80k stock transfers (2.6×), $14.4M of DEX
   volume and the window's only base-fee spike (0.437 gwei).

5. **A stock-token market maker with 22 counterparties.** Contract 0x51c72848 turned over 10,681 WETH in and 10,978
   out (~$54M) plus SPCX, NVDA, AAPL, QQQ, MU, PLTR, TSLA, SPY, AMD, INTC and CRCL, all against a few takers; it
   holds 1,175 WETH, $654k USDG and stock inventory, and is topped up in 350–750 ETH clips from a 5,600-ETH whale
   (0x53091256 → 0x97b237ff / 0xbc8a0f5e → venue). On-chain stock prices from their USDG pools track the reference
   within 0.5% (NVDA 233.5 → 231.5 vs 232.47) except TSLA, which traded at $371.1 against a $355.45 reference for the
   whole window (+4.4%, 6,663 price points), and RCAT (+4.4%).

6. **DEX: 2.5M swaps, one dominant pool, a new pool every seven seconds.** 1.07M v3, 1.39M v4 and 45k v2 swaps in
   3,338 active v3 and 10,612 active v4 pools. Priced volume $356M, of which the 1-bp WETH/USDG v3 pool alone is $185M
   (399k swaps, 269 traders): the chain's ETH/USD venue, and the on-chain ETH price (2,484–2,511) it prints. 5,156 v4
   pools, 210 v3 pools and 87 v2 pairs were created in ten hours: 3,960 hookless, 678 Doppler, 138 PonsV2MemeHook.
   PonsV2LaunchFactory/LaunchAndBuy ran ~8,300 calls at 2.7–3.9M gas each (8.5 ETH), one launch every ~8 s; a single
   sniper EOA (0x49bbf2b7) sent 34,331 transactions, 10,331 of them straight at the Pons hook.

7. **USDG is the settlement asset and DeFi is live.** 2.46M USDG transfers ($1.07B), 42k addresses; Paxos minted
   $7.09M and burned $3.52M on-chain (net +$3.57M issued on Robinhood Chain in ten hours). Morpho Blue moved $24.0M
   in / $23.9M out, steakUSDG $19.1M each way in $4.5–4.7M rebalancing clips, the ethenaUSDG vault $3.6M in / $4.5M
   out, Spark's spUSDG vault netted +$3.55M, and a ZkLighter bridge proxy +$1.26M. One EOA-to-EOA transfer of
   $12.2M at 11:52 was the largest.

8. **Account abstraction is a first-class rail.** 161,449 user operations (97.4% success) from 49,264 smart accounts,
   75% through EntryPoint v0.8 via 100 vanity-prefixed bundler EOAs (0x4337…), 23% through v0.7 via 22 bundlers; 93%
   pay their own gas, a VerifyingPaymaster sponsors 5.5%, Pimlico's singleton paymaster 0.6%. `handleOps` burned 27.7
   ETH (9.9% of fees). EIP-7702 set-code transactions were 38,779 (1.2%) from 4,773 delegated EOAs.

9. **Bots pay to fail, and pay to bid.** 285k transactions reverted (8.8%). The reverts concentrate in a dozen MEV
   contracts with 38–100% failure rates (a v4 quoter/executor 0x1521027b at 81%, "getRich" 0xb0550000 at 90%, multi-DEX
   callback bots at 50–56%, and one wallet, 0x82d82125, whose 16,648 transactions all failed and cost 1.34 ETH).
   175,818 transactions (5.4%) from 9,674 senders bid ≥3× the base fee, up to 3,000 gwei (8,721×); Nitro's
   first-come-first-served ordering ignores every one of them.

10. **Aggregators and terminals fill the rest.** Uniswap's UniversalRouter (176,583 calls, 9.8% failed), SwapRouter02
    (79,707), V2 router (31,695) and v4 PositionManager (41,398; 29,538 position NFTs minted), OKX DexRouter (64,689),
    KyberSwap (184,915 swaps), 0x AllowanceHolder (23,276), Axiom's trade router (93,276 calls, 2,100 ETH of value from
    143 heavy senders), and an unverified launchpad router 0xed090594 (66,360 calls).

11. **Noise floor.** 178k ERC-721 transfers, led by SeaDrop mints (Frost MysteryBox 10,000, PonsBug 7,211, Robinhood
    Mingos 5,555); 2,783 contract creations, 409 by one EOA; mass distributions of a MEME token (2,000 distinct
    receivers per 100 blocks) and two fake "USDG" DropERC20 tokens (500+ receivers per 100 blocks), the address-poisoning
    pattern seen on mainnet; a SchiffyGoldClaims airdrop.

12. **Open question.** `ArbGasInfo.getGasAccountingParams` reports a 7M gas/s speed limit while the chain sustained
    24M gas/s at a stable base fee; the published Nitro pricing formula cannot produce that, so the effective
    parameters are not the ones exposed by the precompile (Bitquery reports the same gap).
