# Onchain, last 5 hours — 2026-09-07 07:39:59 to 12:39:59 UTC

Blocks 25924044–25925535 (1,492 blocks, 410,759 txs, 1.21M logs). Collected in 9 min / 184k Infura credits.
This window is contiguous with the morning scan (which ended 07:39). It was a **quiet Monday**: base
fee 0.037–0.129 gwei (median 0.055), blocks ~51% full, ETH flat $2,482 → $2,493 (+0.5%, range
$2,478–$2,496). ~$189M priced DEX volume (v4 $85M, v3 $42M, v2 $38M, curve $23M). Only one liquidation.

## The interesting things

1. **Compound USDC is paying ~2x Aave.** Compound v3 USDC supply 6.91% / borrow 8.14% at 91% utilisation,
   versus Aave USDC 3.58% / 4.27% at 93% and Sky SSR 3.60%. A lender earns nearly double on Compound for the
   same asset; the gap is utilisation-driven and capacity-limited but persistent through the whole window.
   Ethena sUSDe implied 4.48%, Aave GHO borrow 4.00%. Spark USDT borrow is back to 3.52% — the morning's
   ALM-shock spike to 7.00% has fully normalised.

2. **Circle net-redeemed $126M USDC.** USDC burns $279M vs mints $153M in 5h (net −$126M supply). Includes a
   clean $49M mint-then-burn round trip to 0x55fe002a in adjacent blocks (treasury plumbing).

3. **$104M USDC bridged to Arbitrum via CCTP**, 87 transfers, ~$100M of it to a single recipient
   0x968d48e3 (EOA). Plus $52M USDT out via LayerZero OFT. Largest cross-chain flow of the window.

4. **Binance 14 hot-wallet sweep.** 0x28c6c062 (Binance 14) aggregated 20,759 ETH across 244 deposits and
   swept 12,117 ETH in one tx to internal wallet 0x4976a4a0. Separately a Gnosis Safe 0x2ceb3e99 accumulated
   11,725 ETH (two transfers, no outflow) — custody/treasury build-up, not a market move.
   Exchange net flow (verified-label filtered): stETH −$26M, ETH −$17M out; USDT +$25M, USDC +$15M in.

5. **EIP-7702 set-code txs are now ~2% of all traffic** (8,194 type-0x4 txs), most routing through the
   ERC-4337 EntryPoint v0.8, dominated by one delegate implementation (0xe6b97aa1). Account-abstraction
   wallets are a structural share of mainnet now, not a curiosity.

6. **Robinhood Chain is still the #1 blob poster.** Its SequencerInbox 0xbd0d173e posted 2,271 blobs (757
   txs), edging out Base (2,256) and well ahead of OP Mainnet (1,126) and Arbitrum (402). 8,234 blobs total.

7. **The big "$15.8M BULL swap" is a bot wash.** MEV bot 0x00000f91 ran a BULL→WETH and WETH→BULL leg in the
   same block (25924144), same pool, netting ~zero — double-counted volume, not a whale dump.

8. **Flash-liquidity / MEV.** 823 Balancer flash loans ($18.7M notional). Atomic bot 0x76f30e3f withdrew
   $110.7M WETH from Aave across 4 txs (recurring flash-liquidity pattern). The morning's StacyVault
   reward-timing flash-farmer (0x23fdc534 → 0x0fd368ed) is still live but slower: ~10 touches in 5h, down
   from ~30/hr this morning — still dust economics.

9. **A ~40k-transfer distribution.** 0x5a4fc9dd sent 20 batch txs of ~2,004 ERC-20 Transfer events each via
   0x5eef5946 — an airdrop / multisend campaign, the log-heaviest txs of the window.

## Nothing broke
Pegs held: USDT/USDC/USDS/USDG/crvUSD all within a few bp of par, GHO −9bp, wstETH steady ~$3,096.
One liquidation only (Morpho Blue, 0x25b6f5f1). No depeg, no cascade, no stress.
