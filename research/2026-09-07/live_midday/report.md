# Ethereum mainnet live scan: 2026-09-07T07:39:59+00:00 to 2026-09-07T12:39:59+00:00 UTC

Blocks 25924044 to 25925535 (1492 blocks, 5.00 h), 410,759 transactions, 1,214,881 logs. Prices at head block 25925583: ETH $2490, BTC $79k. Generated 2026-09-07T19:35:43+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

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
   Exchange net flow (corrected labels, 2026-09-07 re-run): stETH −$26.0M and ETH −$19.6M out; USDT +$16.0M in;
   USDC is now −$6.2M, not +$15M. The earlier figures counted 22 contracts as exchange deposit sinks because the
   behavioural rule tested "originated no transactions", which every contract satisfies. Gross USDC inflow fell
   from $823M to $497M on the same blocks. See `verify.json` and the note below.

5. **EIP-7702 set-code txs are now ~2% of all traffic** (8,194 type-0x4 txs), most routing through the
   ERC-4337 EntryPoint v0.8, dominated by one delegate implementation (0xe6b97aa1). Account-abstraction
   wallets are a structural share of mainnet now, not a curiosity.

6. **Robinhood Chain is still the #1 blob poster.** Its SequencerInbox 0xbd0d173e posted 2,271 blobs (757
   txs), edging out Base (2,256) and well ahead of OP Mainnet (1,126) and Arbitrum (402). 8,234 blobs total.

7. **The big "$15.8M BULL swap" is a bot wash.** MEV bot 0x00000f91 ran a BULL→WETH and WETH→BULL leg in the
   same block (25924144), same pool, netting ~zero — double-counted volume, not a whale dump.

8. **Flash-liquidity / MEV.** 823 Balancer flash loans ($18.7M notional). Atomic bot 0x76f30e3f withdrew
   $110.7M WETH from Aave across 4 txs (recurring flash-liquidity pattern). Leverage-to-exchange for this window
   is $0, not the $4.0M first reported: every hop that appeared to reach an exchange landed on a contract
   mislabelled as a deposit sink, and the largest was an Instadapp smart account forwarding inside its own
   transaction. The morning's StacyVault
   reward-timing flash-farmer (0x23fdc534 → 0x0fd368ed) is still live but slower: ~10 touches in 5h, down
   from ~30/hr this morning — still dust economics.

9. **A ~40k-transfer distribution.** 0x5a4fc9dd sent 20 batch txs of ~2,004 ERC-20 Transfer events each via
   0x5eef5946 — an airdrop / multisend campaign, the log-heaviest txs of the window.

## Nothing broke
Pegs held: USDT/USDC/USDS/USDG/crvUSD all within a few bp of par, GHO −9bp, wstETH steady ~$3,096.
One liquidation only (Morpho Blue, 0x25b6f5f1). No depeg, no cascade, no stress.

## Correction, 2026-09-07 (labels and verification)

Three numbers in this note changed after `scripts/labels.py` and `scripts/verify.py` landed, with no change to the
blocks. The address book derived exchange deposit sinks from a day-study profile using the test `sent == 0`, meaning
the address originated no transactions of its own. Every contract satisfies that structurally, so the rule tagged 25
addresses of which 22 forwarded value — among them the CoW settlement contract, the Uniswap Universal Router and a
Relay bridge depository. The rule now tests forwarding directly.

| headline | as first published | corrected |
|---|---:|---:|
| exchange gross inflow, USDC | $823.2M | $497.1M |
| exchange net flow, stables | +$44.0M | +$13.2M |
| exchange net flow, ETH | −$17.4M | −$19.6M |
| leverage-to-exchange | $4.0M | $0 |

Unaffected: the USDC issuance figures ($279.4M burned against $153.1M minted), the $104.0M CCTP send to Arbitrum, the
gas attribution and the rate table. All four are now re-derived from the raw blocks by `verify.py` through a separate
code path, and all 13 of its checks pass.

How much confidence the remaining flow numbers deserve is itself now reported. Exchange flow computed with model-memory
labels alone gives stables +$12.8M and ETH −$4.3M; adding behavioural labels gives +$13.2M and −$19.6M. On the earlier
five-hour window the same band runs from +$91.6M to −$24.8M, so the sign of that headline depends on which unverified
labels you accept.

A second correction landed alongside: the wallet this repo had been calling an "exchange hot wallet with USDG desk" is
the Relay solver identified in the [interchain study](../interchain/findings.md), and is now labelled a bridge rather
than an exchange. That is the same class of error as the deposit-sink bug, found by a different route on the same day.


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 731 | $33.2M | $299 | $0 | $298 | $39.1B | 0.00% | 0.3% | 206.617% |
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 283 | $20.8M | $125 | $0 | $125 | $100.0B | 0.00% | 0.0% | 0.011% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | ? | 4054 | $14.0M | – | $0 | – | $75.0M | – | – | 133.921% |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | ? | 1609 | $8.7M | – | $0 | – | $511.5M | – | – | 0.737% |
| [0x4f49…3c85](https://etherscan.io/address/0x4f493b7de8aac7d55f71853688b1f7c8f0243c85) | curve | USDC/USDT | ? | 137 | $8.1M | – | $0 | – | – | – | – | – |
| 0x8aa4…4e47 | uni v4 | USDC/USDT | 0.00% | 140 | $7.3M | $88 | $0 | $88 | $18.3B | 0.00% | 0.2% | 4.803% |
| [0xbebc…f1c7](https://etherscan.io/address/0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7) | curve | DAI/USDT | ? | 13 | $4.6M | – | $0 | – | – | – | – | – |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 49 | $3.6M | $22 | $0 | $22 | $149.1B | 0.00% | 0.0% | 0.004% |
| 0x9035…eb4f | uni v4 | RLUSD/USDS | 0.00% | 31 | $3.3M | $20 | $0 | $20 | $40.0B | 0.00% | 0.0% | 0.003% |
| [0xdc24…7022](https://etherscan.io/address/0xdc24316b9ae028f1497c275eb9192a3ea0f67022) | curve | ?/? | ? | 20 | $2.6M | – | $0 | – | – | – | – | – |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | ? | 230 | $2.4M | – | $0 | – | $281.7M | – | – | 0.573% |
| [0xe40a…9540](https://etherscan.io/address/0xe40af617c129e732798430c54b716e4ae3149540) | uni v2_like | 0x59d1…90b5/WETH | ? | 57 | $2.2M | $6647 | $0 | $6647 | – | – | – | – |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | ? | 218 | $2.0M | – | $0 | – | $1.8B | – | – | 0.226% |
| [0x21e2…843a](https://etherscan.io/address/0x21e27a5e5513d6e65c4f830167390997aa84843a) | curve | ?/? | ? | 34 | $1.7M | – | $0 | – | – | – | – | – |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 53 | $1.7M | $52 | $7 | $45 | $14.7B | 0.00% | 0.1% | 0.501% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 359 | $1.6M | $16 | $0 | $16 | $10.9B | 0.00% | 0.1% | 0.009% |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | ? | 2828 | $1.5M | – | $0 | – | $16.8M | – | – | 1.859% |
| 0xb90d…b716 | uni v4 | USDC/USDG | 0.01% | 53 | $1.4M | $113 | $0 | $113 | $18.1B | 0.00% | 0.2% | 0.009% |
| [0x1098…7daa](https://etherscan.io/address/0x109830a1aaad605bbf02a9dfa7b0b92ec2fb7daa) | uni v3 | wstETH/WETH | ? | 74 | $1.3M | – | $0 | – | $32.0B | – | – | 0.009% |
| 0xb203…448b | uni v4 | sUSDe/USDT | 0.01% | 69 | $1.2M | $125 | $0 | $125 | $3.5B | 0.01% | 1.3% | 0.051% |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | ? | 242 | $1.1M | – | $0 | – | $35.5B | – | – | 0.006% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | ? | 126 | $1.0M | – | $0 | – | $357.6M | – | – | 0.217% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | ? | 513 | $995k | – | $0 | – | $60.3M | – | – | 0.722% |
| [0xc061…1622](https://etherscan.io/address/0xc061caa073f3d95f80f8e5428d32d2d76f5e1622) | curve | USDC/USDG | ? | 10 | $937k | – | $0 | – | – | – | – | – |
| [0x5b03…8e96](https://etherscan.io/address/0x5b03cccab7ba3010fa5cad23746cbf0794938e96) | curve | USDe/USDT | ? | 41 | $733k | – | $0 | – | – | – | – | – |
| 0xb2b9…3a17 | uni v4 | EURC/USDC | 0.04% | 98 | $682k | $258 | $0 | $258 | $787.6M | 0.06% | 11.6% | 0.153% |
| [0xa6cc…93e8](https://etherscan.io/address/0xa6cc3c2531fdaa6ae1a3ca84c2855806728693e8) | uni v3 | LINK/WETH | ? | 186 | $665k | – | $0 | – | $63.8M | – | – | 1.993% |
| 0x9007…79b3 | uni v4 | WETH/USDT | 0.00% | 218 | $631k | $88 | $0 | $88 | $60.2M | 0.26% | 51.3% | 0.726% |
| 0x7233…ca73 | uni v4 | ETH/USDT | 0.06% | 264 | $588k | $367 | $0 | $367 | $61.8M | 1.04% | 209.7% | 0.796% |
| [0x4dec…d69e](https://etherscan.io/address/0x4dece678ceceb27446b35c672dc7d61f30bad69e) | curve | USDC/crvUSD | ? | 66 | $553k | – | $0 | – | – | – | – | – |
| [0xd0fc…6d78](https://etherscan.io/address/0xd0fc8ba7e267f2bc56044a7715a489d851dc6d78) | uni v3 | UNI/USDC | ? | 138 | $537k | – | $0 | – | $28.6M | – | – | 1.970% |
| 0x21c6…ca27 | uni v4 | ETH/USDC | 0.06% | 213 | $496k | $310 | $0 | $310 | $63.2M | 0.86% | 173.0% | 0.691% |
| 0xdb4c…43b1 | uni v4 | ETH/0xc8fb…8888 | 0.00% | 750 | $487k | $0 | $0 | $0 | $1.1M | 0.08% | 15.7% | – |
| [0xe6ff…e718](https://etherscan.io/address/0xe6ff8b9a37b0fab776134636d9981aa778c4e718) | uni v3 | WBTC/WETH | ? | 324 | $455k | – | $0 | – | $26.1M | – | – | 6.188% |
| [0xa70d…d593](https://etherscan.io/address/0xa70d458a4d9bc0e6571565faee18a48da5c0d593) | uni v2_like | 0xba10…4e3d/WETH | ? | 3 | $453k | $1358 | $0 | $1358 | – | – | – | – |
| 0x00b9…22d7 | uni v4 | ETH/USDC | 0.01% | 966 | $453k | $57 | $0 | $57 | $1.7M | 5.97% | 1202.1% | 30.988% |
| [0x0295…4d72](https://etherscan.io/address/0x02950460e2b9529d0e00284a5fa2d7bdf3fa4d72) | curve | USDe/USDC | ? | 13 | $422k | – | $0 | – | – | – | – | – |
| [0xb31e…5bc3](https://etherscan.io/address/0xb31e70454bdf5bc3) | balancer | USDC/WETH | ? | 32 | $407k | – | $0 | – | – | – | – | – |
| 0x7da1…7427 | uni v4 | USDC/USDG | 0.01% | 21 | $389k | $37 | $0 | $37 | $12.1B | 0.00% | 0.1% | 0.006% |
| 0x9f2d…fe7f | uni v4 | 0x98a8…4665/USDC | 0.06% | 30 | $370k | $231 | $0 | $231 | $48.1M | 0.84% | 169.7% | – |
| [0x18f1…e49b](https://etherscan.io/address/0x18f1a3b51abc0ccb8ee71ebcbd341b707f0de49b) | uni v2_like | 0x13df…8bf5/WETH | ? | 36 | $343k | $1030 | $0 | $1030 | – | – | – | – |
| [0x1d42…d801](https://etherscan.io/address/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801) | uni v3 | UNI/WETH | ? | 191 | $322k | – | $0 | – | $19.0M | – | – | 2.062% |
| [0x7ba8…4568](https://etherscan.io/address/0x7ba89bc658c07569cfa6d7947adaa80181a24568) | curve | 0x056b…5ecc/frxUSD | ? | 22 | $322k | – | $0 | – | – | – | – | – |
| [0xfaa3…ad12](https://etherscan.io/address/0xfaa318479b7755b2dbfdd34dc306cb28b420ad12) | uni v3 | UNI/WETH | ? | 680 | $317k | – | $0 | – | $7.2M | – | – | 7.580% |
| [0x433a…1bbc](https://etherscan.io/address/0x433a00819c771b33fa7223a5b3499b24fbcd1bbc) | uni v3 | 0x77e0…0a44/WETH | ? | 56 | $315k | – | $0 | – | $95.7M | – | – | – |

Just-in-time liquidity: 145 episodes (mint and burn of identical liquidity inside one block), bracketing $629k of swaps and taking about $44 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 42 episodes, fees taken $27
- [0x27c2…2bf2](https://etherscan.io/address/0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2): 13 episodes, fees taken $0
- [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de): 11 episodes, fees taken $6
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 9 episodes, fees taken $1
- [0x6159…cbb1](https://etherscan.io/address/0x6159af7a56d35da5efa508e0d90a435cbb59cbb1): 6 episodes, fees taken $0
- [0xab56…03e2](https://etherscan.io/address/0xab567bb4953ac3b184e6078dd8d3d1dbf2dc03e2): 3 episodes, fees taken $0
- [0xaaa0…ffff](https://etherscan.io/address/0xaaa0bf2e340c2125603b8ffd4ec30faea08effff): 3 episodes, fees taken $0
- [0xd840…37ba](https://etherscan.io/address/0xd840dbe718abc46c6c7704bd7ff16e69a23d37ba): 3 episodes, fees taken $0

Swap volume by venue: uniswap_v4 $84.7M (16987), uniswap_v3 $42.4M (28437), uniswap_v2_like $38.2M (13022), curve $22.6M (1446), balancer $806k (271).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0xdbeb…8cb3 (0x0000…0000/0x8602…2148, 488 swaps); 0x344b…4f7d (0x50d1…a4c9/0x77f5…8888, 269 swaps); 0x49e6…b4b8 (0x50d1…a4c9/0x5c67…b3b2, 217 swaps); 0x230e…804d (0x0000…0000/0xa0df…c845, 185 swaps); 0x1271…75aa (0xb58e…21cb/0xcedb…f8e7, 137 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 112 swaps); 0x6f2c…7a39 (0x0000…0000/0x41f3…abc7, 111 swaps); 0xce28…0c2f (0x0000…0000/0xa27e…62d2, 76 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 73 swaps); 0x459b…0a5b (0x0000…0000/0xeaa6…a69a, 71 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | WBTC | 0.00% | 0.34% | 2.8% | $2.7B | $75.4M |
| Aave v3 | GHO | 0.00% | 4.00% | 83.1% | $135.2M | $112.4M |
| Aave v3 | USDe | 1.65% | 5.36% | 40.9% | $651.7M | $266.8M |
| Aave v3 | LINK | 0.01% | 0.47% | 3.0% | $119.4M | $3.6M |
| Aave v3 | DAI | 3.04% | 4.69% | 86.4% | $131.8M | $113.8M |
| Aave v3 | PYUSD | 3.87% | 4.90% | 87.8% | $7.6M | $6.7M |
| Aave v3 | wstETH | 0.00% | 0.00% | 0.3% | $2.9B | $7.3M |
| Aave v3 | RLUSD | 2.18% | 4.42% | 61.5% | $4.6M | $2.9M |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $277.5M | $0 |
| Aave v3 | USDC | 3.58% | 4.27% | 93.3% | $2.3B | $2.2B |
| Aave v3 | WETH | 1.42% | 2.02% | 82.6% | $5.4B | $4.4B |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.6% | $1.5B | $9.6M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $140k |
| Aave v3 | USDT | 3.56% | 4.26% | 93.0% | $3.0B | $2.8B |
| Aave v3 | USDS | 0.12% | 5.52% | 3.0% | $11.2M | $335k |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $143.5M | $332k |
| SparkLend | GHO | 0.00% | 0.00% | – | – | – |
| SparkLend | USDe | 0.00% | 0.00% | – | – | – |
| SparkLend | LINK | 0.00% | 0.00% | – | – | – |
| SparkLend | DAI | 2.46% | 4.04% | 67.7% | $308.3M | $208.6M |
| SparkLend | PYUSD | 0.58% | 3.89% | 16.6% | $100.0M | $16.6M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.0B | $9939 |
| SparkLend | RLUSD | 0.00% | 3.46% | 0.0% | $1 | $0 |
| SparkLend | sUSDe | 0.00% | 0.00% | – | – | – |
| SparkLend | USDC | 3.54% | 4.27% | 92.2% | $25.6M | $23.6M |
| SparkLend | WETH | 1.55% | 1.97% | 83.1% | $1.2B | $1.0B |
| SparkLend | cbBTC | 0.00% | 0.02% | 1.3% | $286.4M | $3.8M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $105.4M | $0 |
| SparkLend | USDT | 2.62% | 3.52% | 82.8% | $390.9M | $323.4M |
| SparkLend | USDS | 2.32% | 3.93% | 65.6% | $747.4M | $490.4M |
| Compound v3 USDC | base | 6.91% | 8.14% | 91.1% | $372.7M | $339.7M |
| Compound v3 USDT | base | 3.02% | 3.83% | 83.9% | $184.0M | $154.5M |
| Compound v3 WETH | base | 1.36% | 1.88% | 67.8% | $125.5M | $85.1M |

Sky savings rate (sUSDS) 3.60% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.48% APR on $1.4B of USDe.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | PYUSD | 4 | 4.83% → 34.27% | 4.83% – 34.27% | 3.74% → 29.57% |
| SparkLend | USDT | 13 | 7.00% → 3.52% | 3.52% – 7.00% | 6.05% → 2.62% |
| Aave v3 | USDtb | 6 | 14.28% → 12.98% | 12.98% – 14.28% | 9.61% → 8.68% |
| Aave v3 | USDG | 14 | 3.07% → 3.53% | 3.07% – 3.62% | 1.20% → 1.60% |
| Aave v3 | RLUSD | 12 | 4.57% → 4.42% | 4.42% – 4.62% | 2.42% → 2.18% |
| SparkLend | USDS | 8 | 3.93% → 3.93% | 3.91% – 4.01% | 2.32% → 2.32% |
| Aave v3 | USDT | 245 | 4.22% → 4.26% | 4.22% – 4.26% | 3.50% → 3.56% |
| Aave v3 | USDe | 35 | 5.40% → 5.36% | 5.36% – 5.40% | 1.70% → 1.65% |
| SparkLend | WETH | 29 | 1.98% → 1.97% | 1.96% – 1.98% | 1.57% → 1.55% |
| Aave v3 | USDC | 467 | 4.27% → 4.27% | 4.26% – 4.27% | 3.59% → 3.58% |
| Aave v3 | WETH | 241 | 2.03% → 2.03% | 2.02% – 2.03% | 1.43% → 1.42% |
| Aave v3 | EURC | 7 | 3.86% → 3.87% | 3.86% – 3.87% | 2.19% → 2.21% |
| Aave v3 | DAI | 9 | 4.69% → 4.69% | 4.69% – 4.70% | 3.04% → 3.04% |
| Aave v3 | LINK | 18 | 0.48% → 0.47% | 0.47% – 0.48% | 0.01% → 0.01% |
| Aave v3 | wstETH | 119 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | WBTC | 61 | 0.34% → 0.34% | 0.34% – 0.34% | 0.00% → 0.00% |
| SparkLend | DAI | 1 | 4.04% → 4.04% | 4.04% – 4.04% | 2.46% → 2.46% |
| Aave v3 | UNI | 1 | 0.17% → 0.17% | 0.17% – 0.17% | 0.00% → 0.00% |
| Aave v3 | sUSDe | 12 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | wstETH | 3 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | 0x6874…2f38 | 3 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | cbBTC | 13 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| SparkLend | cbBTC | 1 | 0.02% → 0.02% | 0.02% – 0.02% | 0.00% → 0.00% |
| Aave v3 | AAVE | 8 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | weETH | 10 | 1.00% → 1.00% | 1.00% – 1.00% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: repay $30.5M, withdraw $55.2M, atomic withdraw $112.4M, atomic supply $119.7M, borrow $51.2M, supply $60.5M, atomic borrow $346, atomic repay $2; SparkLend: borrow $16.3M, supply $81.5M, withdraw $3.6M, repay $9.7M, atomic supply $6.1M, atomic borrow $4.7M, atomic repay $4.7M, atomic withdraw $6.1M.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 25924280 | SparkLend | supply | USDT | $46.4M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x6646…8aa2](https://etherscan.io/tx/0x66461186e0860bcab68dfb7dccbf4004e13a35f4bd0088549f37de77488d8aa2) |
| 25925035 | SparkLend | supply | USDS | $15.2M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x21ac…c0c5](https://etherscan.io/tx/0x21aca1a4a2ffde8ff4920de44a1be45726161d3d62b599e1174d40064002c0c5) |
| 25925024 | SparkLend | borrow | USDS | $10.0M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0x8ef2…0d3d](https://etherscan.io/tx/0x8ef241e107c47fb8bab38305387825a4756ace731bafe3364684cf064dac0d3d) |
| 25925377 | SparkLend | supply | WETH | $7.5M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0xf482…4a34](https://etherscan.io/tx/0xf48223b7de875f386ad10f7344b54da084bed97ec2cf8aa5776d0e3a7d6f4a34) |
| 25924261 | Aave v3 | borrow | USDT | $7.2M | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | [0x3e4a…db87](https://etherscan.io/tx/0x3e4a8bdbf01039cabe4871fcfb649e9d789f4bf8f8cf4e546f3ff99827b1db87) |
| 25924261 | SparkLend | repay | USDT | $7.2M | [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) | [0x3e4a…db87](https://etherscan.io/tx/0x3e4a8bdbf01039cabe4871fcfb649e9d789f4bf8f8cf4e546f3ff99827b1db87) |
| 25924738 | SparkLend | supply | WETH | $6.2M | [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) | [0x0169…2f68](https://etherscan.io/tx/0x0169a94b5d6429b6456f536d74767f5564bc508fb0b7a9f1c41986deeda62f68) |
| 25925464 | Aave v3 | withdraw | wstETH | $6.0M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0xaef6…b573](https://etherscan.io/tx/0xaef60a25ad010e5d4aed71c7df25ad189946d0aeffcb9515379bbfb41a9eb573) |
| 25925464 | SparkLend | supply | wstETH | $5.5M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0xaef6…b573](https://etherscan.io/tx/0xaef60a25ad010e5d4aed71c7df25ad189946d0aeffcb9515379bbfb41a9eb573) |
| 25925464 | Aave v3 | repay | WETH | $5.3M | [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) | [0xaef6…b573](https://etherscan.io/tx/0xaef60a25ad010e5d4aed71c7df25ad189946d0aeffcb9515379bbfb41a9eb573) |
| 25924470 | Aave v3 | repay | USDT | $4.9M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x0c61…7127](https://etherscan.io/tx/0x0c61075fbac7d21f780fa1d2abf84dc67204cf2698933fac974ab6e3c6e87127) |
| 25924470 | Aave v3 | borrow | USDT | $4.9M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x4573…d68f](https://etherscan.io/tx/0x4573a8d4f25c28216b0d11429589e8411ea32db006dc11c6e7556d5ce550d68f) |
| 25924470 | Aave v3 | withdraw | USDC | $4.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x0c61…7127](https://etherscan.io/tx/0x0c61075fbac7d21f780fa1d2abf84dc67204cf2698933fac974ab6e3c6e87127) |
| 25925478 | Aave v3 | withdraw | rsETH | $4.6M | [0x973d…1683](https://etherscan.io/address/0x973ddb8ee2c9cc87e853c8d46253840c63951683) | [0x75f6…75a5](https://etherscan.io/tx/0x75f69b4c740baf6c74225dd14f78ed3c0daa72a4fc57d99efb03cb30a10b75a5) |
| 25925467 | Aave v3 | repay | WETH | $4.3M | [0x973d…1683](https://etherscan.io/address/0x973ddb8ee2c9cc87e853c8d46253840c63951683) | [0x8621…e9b0](https://etherscan.io/tx/0x8621520bcca123808cfb43da2639c15498c726267be8d79dc4eb35cdb9e3e9b0) |
| 25924574 | Aave v3 | supply | USDe | $3.3M | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x7e1f…1759](https://etherscan.io/tx/0x7e1fbb9b52dd1b5b1bffd767d49c5117c9c152a268a76920e238f7cf8c311759) |
| 25924162 | Aave v3 | borrow | USDT | $3.3M | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x1604…5d8e](https://etherscan.io/tx/0x16045412fbbee32ef7711bbf328295963618c6de2d41f295840ab4b528b15d8e) |
| 25924155 | Aave v3 | repay | USDC | $3.3M | [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) | [0x7fdd…e06d](https://etherscan.io/tx/0x7fddb81212e7dee933106deacec590b5e0299970da5b7dc7b353f1c95d0fe06d) |
| 25925413 | Aave v3 | supply | wstETH | $3.0M | [0x852f…73c8](https://etherscan.io/address/0x852f79dad4e6c44a89be189dc3ecf51b3c5273c8) | [0xed12…1f1c](https://etherscan.io/tx/0xed12109289441550c06f2e87da7cc9a72bd06a536ad726be543a200e794e1f1c) |
| 25925413 | Aave v3 | borrow | WETH | $3.0M | [0x852f…73c8](https://etherscan.io/address/0x852f79dad4e6c44a89be189dc3ecf51b3c5273c8) | [0xed12…1f1c](https://etherscan.io/tx/0xed12109289441550c06f2e87da7cc9a72bd06a536ad726be543a200e794e1f1c) |
| 25925231 | Aave v3 | supply | wstETH | $2.5M | [0x852f…73c8](https://etherscan.io/address/0x852f79dad4e6c44a89be189dc3ecf51b3c5273c8) | [0xe19d…853e](https://etherscan.io/tx/0xe19da227633f9315528812238a86e6e9d009233d8fc91a87ac91ee63b07a853e) |
| 25924900 | Aave v3 | borrow | USDT | $2.4M | [0xf929…d1f9](https://etherscan.io/address/0xf929122994e177079c924631ba13fb280f5cd1f9) | [0xf17d…b45b](https://etherscan.io/tx/0xf17d59f9d87fcfa23770c6a4d5df214125f3503a73f62723e2555de33f86b45b) |
| 25924632 | SparkLend | withdraw | USDS | $2.1M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x6076…cebb](https://etherscan.io/tx/0x607614a7e2976a1d3ce65cb7e31cdaadc8c74d7947a7e0bc46d47d93aaadcebb) |
| 25924516 | Aave v3 | withdraw | USDG | $2.0M | [0xe106…0be5](https://etherscan.io/address/0xe1066ffcb6951bed71c1870c62b3759270510be5) | [0x289d…4434](https://etherscan.io/tx/0x289db527ffd40d1af5fd1af9bb741a7bf2417c428261dfeef4f39dfe385e4434) |
| 25924624 | SparkLend | repay | USDS | $1.4M | [0x8be4…89d9](https://etherscan.io/address/0x8be46b25d59616e594f0a9e20147fb14c1b989d9) | [0x8f50…4706](https://etherscan.io/tx/0x8f50a09e7aeefbc1293dafe2e2a6889dd53adbaad6db26310ef246f3c9b04706) |
| 25925450 | Aave v3 | supply | wstETH | $901k | [0x95e1…9568](https://etherscan.io/address/0x95e153c9677a2241868d80cd01e43b0b7ab39568) | [0x4d2e…7580](https://etherscan.io/tx/0x4d2e524651157091e5b77d839d1e11d88b95342f754750fe509dcee51f257580) |
| 25925116 | SparkLend | repay | WETH | $897k | [0x8be4…89d9](https://etherscan.io/address/0x8be46b25d59616e594f0a9e20147fb14c1b989d9) | [0xf090…e76e](https://etherscan.io/tx/0xf090efb0fe3f244a644e2c2e538c08aeaaf7e479b6ac77e6effb41826b7ae76e) |
| 25924637 | SparkLend | borrow | WETH | $897k | [0x8be4…89d9](https://etherscan.io/address/0x8be46b25d59616e594f0a9e20147fb14c1b989d9) | [0xf813…1952](https://etherscan.io/tx/0xf813fbcc4294fd07c6099b43021e51f7546f7baf5042c72b5dc0f58c754b1952) |
| 25924648 | Aave v3 | supply | WETH | $759k | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | [0xfda3…d566](https://etherscan.io/tx/0xfda326b5855dbd9a59a4f162b5e32c39083d7abc8767434acaf42f403bdfd566) |
| 25924648 | Aave v3 | withdraw | WETH | $759k | [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) | [0xf113…6b91](https://etherscan.io/tx/0xf113a4395daab09563afa3b596282c924451cc16aad42aecf0bedc184d5d6b91) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- SparkLend borrow $10.0M USDS by [0xb99a…bcf5](https://etherscan.io/address/0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5) ([0x8ef2…0d3d](https://etherscan.io/tx/0x8ef241e107c47fb8bab38305387825a4756ace731bafe3364684cf064dac0d3d)): $10.0M → [UsdsPsmWrapper (blockscout-verified)](https://etherscan.io/address/0xa188eec8f81263234da3622a406892f3d630f98c)
- Aave v3 borrow $7.2M USDT by [0x181c…a76d](https://etherscan.io/address/0x181cb55f872450d16ae858d532b4e35e50eaa76d) ([0x3e4a…db87](https://etherscan.io/tx/0x3e4a8bdbf01039cabe4871fcfb649e9d789f4bf8f8cf4e546f3ff99827b1db87)): $7.2M → [AToken (via InitializableImmutableAdminUpgradeabilityProxy) (blockscout-verified)](https://etherscan.io/address/0xe7df13b8e3d6740fe17cbe928c7334243d86c92f)
- Aave v3 withdraw $6.0M wstETH by [0xb8a4…715e](https://etherscan.io/address/0xb8a451107a9f87fde481d4d686247d6e43ed715e) ([0xaef6…b573](https://etherscan.io/tx/0xaef60a25ad010e5d4aed71c7df25ad189946d0aeffcb9515379bbfb41a9eb573)): $496k → [0xc035…e0c2](https://etherscan.io/address/0xc035a7cf15375ce2706766804551791ad035e0c2); $5.5M → [0x12b5…66e9](https://etherscan.io/address/0x12b54025c112aa61face2cdb7118740875a566e9)
- Aave v3 borrow $4.9M USDT by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x4573…d68f](https://etherscan.io/tx/0x4573a8d4f25c28216b0d11429589e8411ea32db006dc11c6e7556d5ce550d68f)): $4.9M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $4.9M → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a)
- Aave v3 withdraw $4.8M USDC by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0x0c61…7127](https://etherscan.io/tx/0x0c61075fbac7d21f780fa1d2abf84dc67204cf2698933fac974ab6e3c6e87127)): $50k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $4.8M → [0x98c2…6f5c](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c); $4.8M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90)
- Aave v3 withdraw $4.6M rsETH by [0x973d…1683](https://etherscan.io/address/0x973ddb8ee2c9cc87e853c8d46253840c63951683) ([0x75f6…75a5](https://etherscan.io/tx/0x75f69b4c740baf6c74225dd14f78ed3c0daa72a4fc57d99efb03cb30a10b75a5)): $4.6M → [0x62de…ec16](https://etherscan.io/address/0x62de59c08eb5dae4b7e6f7a8cad3006d6965ec16)
- Aave v3 borrow $3.3M USDT by [0xcf0a…cd69](https://etherscan.io/address/0xcf0a12cbd8088fc5f84ad431e71787157041cd69) ([0x1604…5d8e](https://etherscan.io/tx/0x16045412fbbee32ef7711bbf328295963618c6de2d41f295840ab4b528b15d8e)): $3.3M → [0x4243…3f37](https://etherscan.io/address/0x424323d25d30c687bdf79bb333da1d41c0373f37)
- Aave v3 borrow $3.0M WETH by [0x852f…73c8](https://etherscan.io/address/0x852f79dad4e6c44a89be189dc3ecf51b3c5273c8) ([0xed12…1f1c](https://etherscan.io/tx/0xed12109289441550c06f2e87da7cc9a72bd06a536ad726be543a200e794e1f1c)): $3.0M → [0x8f10…f996](https://etherscan.io/address/0x8f10b468b06c6fd214b65f87778827f7d113f996); $3.0M → [0x3524…3cc7](https://etherscan.io/address/0x352423e2fa5d5c99343d371c9e3bc56c87723cc7)
- Aave v3 borrow $2.4M USDT by [0xf929…d1f9](https://etherscan.io/address/0xf929122994e177079c924631ba13fb280f5cd1f9) ([0xf17d…b45b](https://etherscan.io/tx/0xf17d59f9d87fcfa23770c6a4d5df214125f3503a73f62723e2555de33f86b45b)): $2.4M → [0xd524…25da](https://etherscan.io/address/0xd524a29e10f6adae8df66392b3e1e49e497c25da)
- SparkLend withdraw $2.1M USDS by [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) ([0x6076…cebb](https://etherscan.io/tx/0x607614a7e2976a1d3ce65cb7e31cdaadc8c74d7947a7e0bc46d47d93aaadcebb)): $7.7M → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $3.0M → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $152k → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $393k → [DaiUsds (blockscout-verified)](https://etherscan.io/address/0x3225737a9bbb6473cb4a45b7244aca2befdb276a)
- Aave v3 withdraw $2.0M USDG by [0xe106…0be5](https://etherscan.io/address/0xe1066ffcb6951bed71c1870c62b3759270510be5) ([0x289d…4434](https://etherscan.io/tx/0x289db527ffd40d1af5fd1af9bb741a7bf2417c428261dfeef4f39dfe385e4434)): $2.0M → [CoW Protocol settlement (GPv2Settlement) (known-canonical)](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41)
- SparkLend borrow $897k WETH by [0x8be4…89d9](https://etherscan.io/address/0x8be46b25d59616e594f0a9e20147fb14c1b989d9) ([0xf813…1952](https://etherscan.io/tx/0xf813fbcc4294fd07c6099b43021e51f7546f7baf5042c72b5dc0f58c754b1952)): $6.2M → [0x59cd…71db](https://etherscan.io/address/0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db)
- Aave v3 withdraw $759k WETH by [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb) ([0xf113…6b91](https://etherscan.io/tx/0xf113a4395daab09563afa3b596282c924451cc16aad42aecf0bedc184d5d6b91)): $759k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $14k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 withdraw $748k sUSDe by [0x01b3…eaf7](https://etherscan.io/address/0x01b3ba0aa49c3daa72e25031bcd1b4029cf8eaf7) ([0xc3cf…639a](https://etherscan.io/tx/0xc3cfe6f137b8b027e4289c827dc243ac067f7074e5041623276b6e305c18639a)): $748k → [zero address (mint/burn) (known-canonical)](https://etherscan.io/address/0x0000000000000000000000000000000000000000)
- Aave v3 borrow $740k WETH by [0x9496…3423](https://etherscan.io/address/0x94963b928498be7f06637c3d57ea1e74d7f73423) ([0x3046…d7d2](https://etherscan.io/tx/0x30463278f1f53674d123230e8452cac9665bd14a1aaee0cce8215db04378d7d2)): $55k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 withdraw $676k WETH by [0xa462…27a1](https://etherscan.io/address/0xa462d9acaccb141ce7f17213b95198fe248c27a1) ([0xf272…e4ad](https://etherscan.io/tx/0xf2729492557a051ca807bc4094ef0a97085fb7bef7dfb548516087c97c21e4ad)): $676k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 borrow $640k USDT by [0x6041…34c5](https://etherscan.io/address/0x604117f0c94561231060f56cd2ddd16245d434c5) ([0xe38d…fd33](https://etherscan.io/tx/0xe38d40d0eb19b228a119445cf655428a82c5f8e67c88a1323b70da8be812fd33)): $254k → [0x9b6f…a9ed](https://etherscan.io/address/0x9b6f014ba4df10871302cb1a781ab1c423bca9ed); $386k → [0x9b6f…a9ed](https://etherscan.io/address/0x9b6f014ba4df10871302cb1a781ab1c423bca9ed); $640k → [Morpho Blue (known-canonical)](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb)
- Aave v3 withdraw $602k USDT by [0x7bc3…3af8](https://etherscan.io/address/0x7bc3485026ac48b6cf9baf0a377477fff5703af8) ([0xf6bb…421d](https://etherscan.io/tx/0xf6bbef2931f59a437b391305e1093dce2593d5862f2c5be7ee0e3e2412cc421d)): $600k → [0xb524…93bf](https://etherscan.io/address/0xb524d79cc76fdff645c3c841a5c006b30c6693bf)
- Aave v3 borrow $600k USDC by [0x95e1…9568](https://etherscan.io/address/0x95e153c9677a2241868d80cd01e43b0b7ab39568) ([0xd514…0ff1](https://etherscan.io/tx/0xd514394901975bfc1c660a37b8a745077cfb9af0bf4bdc624c9fae2aeb730ff1)): $300k → [CoW Protocol settlement (GPv2Settlement) (known-canonical)](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41); $300k → [CoW Protocol settlement (GPv2Settlement) (known-canonical)](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41)
- SparkLend withdraw $599k WETH by [0xbd7d…1704](https://etherscan.io/address/0xbd7d6a9ad7865463de44b05f04559f65e3b11704) ([0x08b1…601d](https://etherscan.io/tx/0x08b1b392777c82abec944877f1f257c07b96db03ac3507dca43e4520e62a601d)): $6.2M → [0x59cd…71db](https://etherscan.io/address/0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db)

Liquidations: Morpho Blue [0x25b6…b296](https://etherscan.io/address/0x25b6f5f1525f0074d53570ea2fb4cd9ee545b296) debt –, collateral – ([0x0b18…1d0a](https://etherscan.io/tx/0x0b1891e9bfbe4a4e07dfe9e244951d00c87413f23de2e4515d9776294fc31d0a)).


Flash loans (events): BalFlash 823 ($18.7M), MorphoFlash 3 ($0).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a): 4 transactions, largest leg $29.0M, gross $110.7M; legs: WETH withdraw $110.7M, USDC withdraw $0
- SparkLend account [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588): 2 transactions, largest leg $3.1M, gross $10.8M; legs: WBTC withdraw $6.1M, USDT borrow $4.7M
- Aave v3 account [0x9205…f0bb](https://etherscan.io/address/0x9205a569b0ff45df1e4f5ae48e21bc7f0656f0bb): 4 transactions, largest leg $760k, gross $1.7M; legs: WETH withdraw $1.7M
- Aave v3 account [0xe947…d90f](https://etherscan.io/address/0xe947e01a0c8a15d84b1285258cd0b1788f81d90f): 1 transactions, largest leg $346, gross $346; legs: LINK borrow $346
- Aave v3 account [0x9f80…3afd](https://etherscan.io/address/0x9f80282fddc150d4bc09456be61c93d849f83afd): 1 transactions, largest leg $20, gross $20; legs: WETH withdraw $20

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 902 | $52.3M | 0.999858 | 0.999824 – 0.999907 | 0.99996 | -1.0 bps |
| USDS | 224 | $24.5M | 0.999982 | 0.999946 – 1.00001 | 1 | -0.2 bps |
| DAI | 28 | $3.7M | 1.00005 | 0.999794 – 1.00005 | 0.999615 | +4.3 bps |
| USDe | 97 | $3.0M | 1.00001 | 0.99983 – 1.00004 | 1 | +0.1 bps |
| USDG | 74 | $2.8M | 0.999994 | 0.999921 – 1.00014 | 1 | -0.1 bps |
| RLUSD | 12 | $1.7M | 1.00019 | 1.00019 – 1.0002 | 1 | +1.9 bps |
| sUSDe | 91 | $1.7M | 1.24664 | 1.24623 – 1.2495 | 1.24693 | -2.3 bps |
| PYUSD | 25 | $1.5M | 1.00004 | 0.999886 – 1.00009 | 1 | +0.4 bps |
| wstETH | 53 | $1.3M | 3096.74 | 3095.72 – 3141.75 | 3099.85 | -10.0 bps |
| crvUSD | 83 | $714k | 0.99987 | 0.999863 – 1.00007 | 1 | -1.3 bps |
| AUSD | 6 | $519k | 0.99985 | 0.999784 – 0.999986 | 1 | -1.5 bps |
| weETH | 16 | $285k | 2747.24 | 2746.51 – 2747.12 | 2747.15 | +0.3 bps |
| GHO | 26 | $173k | 0.999058 | 0.99895 – 0.999157 | 1 | -9.4 bps |
| USD0 | 17 | $126k | 1.00419 | 0.998795 – 0.998995 | 1 | +41.9 bps |
| USDtb | 5 | $118k | 0.999922 | 0.999914 – 0.999932 | 1 | -0.8 bps |
| DOLA | 19 | $61k | 0.997324 | 0.997143 – 0.997511 | 1 | -26.8 bps |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 178 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDC | $497.1M | $503.3M | $-6.2M |
| USDT | $338.8M | $322.8M | $16.0M |
| ETH | $90.6M | $110.2M | $-19.6M |
| USDG | $15.1M | $13.0M | $2.0M |
| stETH | $352k | $26.3M | $-26.0M |
| RLUSD | $1.5M | $9.2M | $-7.7M |
| USDe | $9.0M | $199k | $8.8M |
| UNI | $3.6M | $3.5M | $94k |
| EURC | $2.9M | $2.4M | $484k |
| LINK | $2.7M | $2.2M | $497k |
| WBTC | $316k | $1.2M | $-894k |
| cbBTC | $959k | $175k | $784k |

By label: Coinbase 11 (model-memory) in $307.3M / out $312.6M; hot wallet (behaviour, day study) in $144.0M / out $184.9M; Binance 14 (model-memory) in $204.7M / out $92.7M; Coinbase 10 (model-memory) in $92.7M / out $87.4M; hot wallet (day study, unidentified) (model-memory) in $89.4M / out $81.8M; Bybit (model-memory) in $49.5M / out $26.2M; Bitfinex 2 (model-memory) in $15.9M / out $59.4M; Bitget (model-memory) in $26.2M / out $26.6M; Gate.io (model-memory) in $20.2M / out $19.7M; Binance 17 (model-memory) in $0 / out $31.8M; Binance 15 (model-memory) in $0 / out $28.4M; Binance 16 (model-memory) in $0 / out $23.3M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 25925535 | WBTC | $437.6M ×10 | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xf76d…c885](https://etherscan.io/tx/0xf76df2331b81df5e8171103b1484205dee782ef8e3611e987293b8313bd7c885) |
| 25925535 | WBTC | $437.6M ×10 | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xf76d…c885](https://etherscan.io/tx/0xf76df2331b81df5e8171103b1484205dee782ef8e3611e987293b8313bd7c885) |
| 25924283 | USDC | $200.0M | [0x38aa…b200](https://etherscan.io/address/0x38aaef3782910bdd9ea3566c839788af6ff9b200) | [0xee7a…4055](https://etherscan.io/address/0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055) | [0xc925…8cce](https://etherscan.io/tx/0xc92578c9878edeea0ce5332ecbf0bddb11951df0f729921b1a9e8f97bf4d8cce) |
| 25924394 | USDC | $166.0M | [0x4e67…3cac](https://etherscan.io/address/0x4e67722883ad992182e83b79bf06a93972963cac) | [0x3d09…0c37](https://etherscan.io/address/0x3d09d2354530466d32ed37c6ad19ea58504a0c37) | [0xaa28…1133](https://etherscan.io/tx/0xaa2842d5fe210aa29f9b10ffe01e57c5c6200870d629979bedc0531678871133) |
| 25925119 | USDC | $101.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) | [0x1bee…ff4d](https://etherscan.io/tx/0x1bee9adadfae8d24256a078b28f65b5b97ccb3b2efe25efe97c2c478728fff4d) |
| 25925119 | USDC | $101.9M | [0x0000…0cac](https://etherscan.io/address/0x00000f91109c4d0007e90000d9facad5298a0cac) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1bee…ff4d](https://etherscan.io/tx/0x1bee9adadfae8d24256a078b28f65b5b97ccb3b2efe25efe97c2c478728fff4d) |
| 25925176 | USDC | $101.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x7cb0…62ee](https://etherscan.io/address/0x7cb086ed4b6993edd4cad69983ccd012eb0562ee) | [0x3287…9eff](https://etherscan.io/tx/0x32875e40c698bf4ff428ba87dd77008fa5b79c45738f7a8f1e2ee3859ebc9eff) |
| 25925176 | USDC | $101.8M | [0x7cb0…62ee](https://etherscan.io/address/0x7cb086ed4b6993edd4cad69983ccd012eb0562ee) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x3287…9eff](https://etherscan.io/tx/0x32875e40c698bf4ff428ba87dd77008fa5b79c45738f7a8f1e2ee3859ebc9eff) |
| 25925278 | USDC | $101.0M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x51aa…6297](https://etherscan.io/tx/0x51aa152fc7e1ee4e2f6485ed8f7e8e1f3597505f916001f7e415dc0b1d9c6297) |
| 25925278 | USDC | $101.0M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x51aa…6297](https://etherscan.io/tx/0x51aa152fc7e1ee4e2f6485ed8f7e8e1f3597505f916001f7e415dc0b1d9c6297) |
| 25924306 | USDC | $101.0M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xf75a…3cc0](https://etherscan.io/tx/0xf75a8b96406f9eab2ae34c3928ca084062fe819fc0879b3a36951f4101243cc0) |
| 25924306 | USDC | $101.0M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xf75a…3cc0](https://etherscan.io/tx/0xf75a8b96406f9eab2ae34c3928ca084062fe819fc0879b3a36951f4101243cc0) |
| 25925535 | USDC | $101.0M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xf76d…c885](https://etherscan.io/tx/0xf76df2331b81df5e8171103b1484205dee782ef8e3611e987293b8313bd7c885) |
| 25925535 | USDC | $101.0M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xf76d…c885](https://etherscan.io/tx/0xf76df2331b81df5e8171103b1484205dee782ef8e3611e987293b8313bd7c885) |
| 25925143 | USDC | $100.6M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x87e5…6271](https://etherscan.io/tx/0x87e57dedc2779c69f9e7b2546f0d4fe7d96e8b1d31044bae5ce6771091486271) |
| 25925143 | USDC | $100.6M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x87e5…6271](https://etherscan.io/tx/0x87e57dedc2779c69f9e7b2546f0d4fe7d96e8b1d31044bae5ce6771091486271) |
| 25925020 | USDC | $100.3M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x968d…67b6](https://etherscan.io/tx/0x968db74d5dbbd5a02a5de2231df71833173ff5d545e0bc6c58a64daa86a967b6) |
| 25925020 | USDC | $100.3M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x968d…67b6](https://etherscan.io/tx/0x968db74d5dbbd5a02a5de2231df71833173ff5d545e0bc6c58a64daa86a967b6) |
| 25924891 | USDC | $100.0M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x4d75…8290](https://etherscan.io/tx/0x4d75c5e1f4fa0d2c7d8de48b1e2ac8327484d7f880de889324a8b4af068e8290) |
| 25924891 | USDC | $100.0M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x4d75…8290](https://etherscan.io/tx/0x4d75c5e1f4fa0d2c7d8de48b1e2ac8327484d7f880de889324a8b4af068e8290) |
| 25924658 | USDC | $100.0M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x06f8…d73f](https://etherscan.io/tx/0x06f813b12943a3b6bdd88d90afec3eeb698408b477784b4363228194f656d73f) |
| 25924658 | USDC | $100.0M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06f8…d73f](https://etherscan.io/tx/0x06f813b12943a3b6bdd88d90afec3eeb698408b477784b4363228194f656d73f) |
| 25924514 | USDC | $99.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xb5b5…8f8f](https://etherscan.io/tx/0xb5b5df3e2aba3e12f07b8c61f56e83c586e334d36a837a8507b553961aac8f8f) |
| 25924514 | USDC | $99.7M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xb5b5…8f8f](https://etherscan.io/tx/0xb5b5df3e2aba3e12f07b8c61f56e83c586e334d36a837a8507b553961aac8f8f) |
| 25924156 | USDC | $99.6M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xf71e…7c29](https://etherscan.io/tx/0xf71ee70405f0b4cdb2d0d281de3a3ced3a0f80ba379d1be82cd4e1f9e96a7c29) |
| 25924156 | USDC | $99.6M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xf71e…7c29](https://etherscan.io/tx/0xf71ee70405f0b4cdb2d0d281de3a3ced3a0f80ba379d1be82cd4e1f9e96a7c29) |
| 25924339 | USDC | $99.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x5e8e…f1cd](https://etherscan.io/tx/0x5e8ec919bc61b39bb1cf7499680dbb16dbaed1d5c2ef08afcefd722df17bf1cd) |
| 25924339 | USDC | $99.4M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x5e8e…f1cd](https://etherscan.io/tx/0x5e8ec919bc61b39bb1cf7499680dbb16dbaed1d5c2ef08afcefd722df17bf1cd) |
| 25924781 | USDC | $99.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0x5838…d0a2](https://etherscan.io/tx/0x5838c6373f5def112e169a114d685796ff40d14f70db1927c5e8b065944bd0a2) |
| 25924781 | USDC | $99.2M | [0x0fd3…c83d](https://etherscan.io/address/0x0fd368edd39d47823948d2cc54415dd2f151c83d) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x5838…d0a2](https://etherscan.io/tx/0x5838c6373f5def112e169a114d685796ff40d14f70db1927c5e8b065944bd0a2) |

Round trips (≥ $10M out and back within the window): $14.6M USDC from [0xd178…a121](https://etherscan.io/address/0xd178a90c41ff3dcffbfdef7de0baf76cbfe6a121) via [0x8e71…8232](https://etherscan.io/address/0x8e712469e6cb10f6a9008fdcf2ab46c3ccc08232), back after 82 min; $14.6M USDC from [0x8e71…8232](https://etherscan.io/address/0x8e712469e6cb10f6a9008fdcf2ab46c3ccc08232) via [0x549d…3425](https://etherscan.io/address/0x549d835356d92983abb76e4cae639f7857963425), back after 76 min; $49.0M USDC from [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) via [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8), back after 6 min; $49.0M USDC from [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) via [0x9649…6043](https://etherscan.io/address/0x9649788adfbdfc2bd39a0058be57ed36583c6043), back after 3 min; $48.0M USDC from [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) via [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8), back after 6 min; $48.0M USDC from [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) via [0x9649…6043](https://etherscan.io/address/0x9649788adfbdfc2bd39a0058be57ed36583c6043), back after 3 min; $20.0M USDC from [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000) via [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8), back after 6 min; $20.0M USDC from [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) via [0x9649…6043](https://etherscan.io/address/0x9649788adfbdfc2bd39a0058be57ed36583c6043), back after 3 min.


Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0x9cf2…6195](https://etherscan.io/address/0x9cf2b94caba0ab5ea0709c9aaa68716908236195) | frxUSD → 0x056b…5ecc | 4 | $140k | $34k | 12s | 0.00 | 0.29 | curve 4 |
| [0x5b43…efd1](https://etherscan.io/address/0x5b43453fce04b92e190f391a83136bfbecedefd1) | USDC → WETH | 4 | $119k | $30k | 3876s | 0.47 | 0.13 | uniswap_v3 4 |
| [hot wallet (behaviour, day study)](https://etherscan.io/address/0x50bf934781f63028c5c8ef49c4affe19a86d99b6) | USDT → USDC | 4 | $143k | $37k | 2256s | 0.35 | 0.30 | uniswap_v4 4 |
| [0xc8df…ebfe](https://etherscan.io/address/0xc8df1a5953aa7f62a35ff1501e0c10eb3c33ebfe) | USDC → WETH | 6 | $170k | $22k | 1944s | 0.45 | 0.35 | uniswap_v3 6 |
| [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13) | WETH → USDC | 5 | $1.7M | $317k | 174s | 0.51 | 0.49 | uniswap_v3 5 |
| [0x81dc…b824](https://etherscan.io/address/0x81dc771e308c76c3e06f635abed7fb24830fb824) | USDC → WETH | 5 | $247k | $36k | 4152s | 0.56 | 0.59 | uniswap_v3 5 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 25924144 | uniswap_v2_like | 0x8e9d…cf3e → WETH | $15.8M | [0x5c09…33a9](https://etherscan.io/address/0x5c096ef846447cb935c5d247e4ab2a867ecc33a9) | [0x0a59…26c1](https://etherscan.io/tx/0x0a5922649a66ebf9905d4c29934c87cdfe8285a3b15de1c18a5fb7c51e1c26c1) |
| 25924144 | uniswap_v2_like | WETH → 0x8e9d…cf3e | $15.8M | [0x5c09…33a9](https://etherscan.io/address/0x5c096ef846447cb935c5d247e4ab2a867ecc33a9) | [0x0a59…26c1](https://etherscan.io/tx/0x0a5922649a66ebf9905d4c29934c87cdfe8285a3b15de1c18a5fb7c51e1c26c1) |
| 25924717 | uniswap_v4 | USDT → USDC | $5.2M | [0x4d92…dada](https://etherscan.io/address/0x4d92a9835f4768aac92531cf1a638e444912dada) | [0x57dd…e1f7](https://etherscan.io/tx/0x57dd7e4b7f684d152c0110b94d25252906d7502d732dde8bee0e5e82a01fe1f7) |
| 25924717 | uniswap_v4 | USDC → USDT | $5.1M | [0x4d92…dada](https://etherscan.io/address/0x4d92a9835f4768aac92531cf1a638e444912dada) | [0x2caf…aee4](https://etherscan.io/tx/0x2caf4e1d4ed4498f521527ad67c5ef20da0de761ef3ccfe19e4551fb0cb9aee4) |
| 25924470 | uniswap_v4 | USDT → USDC | $4.9M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x4573…d68f](https://etherscan.io/tx/0x4573a8d4f25c28216b0d11429589e8411ea32db006dc11c6e7556d5ce550d68f) |
| 25924470 | uniswap_v4 | USDC → USDT | $4.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x0c61…7127](https://etherscan.io/tx/0x0c61075fbac7d21f780fa1d2abf84dc67204cf2698933fac974ab6e3c6e87127) |
| 25924047 | uniswap_v4 | USDT → USDC | $2.5M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xfff9…7df1](https://etherscan.io/tx/0xfff9b99b6e59b9da165ca65f0b83cb7dc3bfc2b1dea647d98590952b1ace7df1) |
| 25924047 | uniswap_v4 | USDC → USDT | $2.5M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x4c23…59e9](https://etherscan.io/tx/0x4c231ed7606f45caa1f1edfce30249f508b15350ef8189ce28daf243b25c59e9) |
| 25924740 | uniswap_v4 | USDC → USDT | $2.4M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x60e8…01f4](https://etherscan.io/tx/0x60e8431c831fcf6c04aa7a30ebf8a11f26d813cb92f1c2bda86122328bb101f4) |
| 25924740 | uniswap_v4 | USDT → USDC | $2.4M | [0xaf60…82fb](https://etherscan.io/address/0xaf606275e24fd27206df317b075a48c0750f82fb) | [0x0199…38b3](https://etherscan.io/tx/0x01998dc1cc80d64cd1c877d0a5302e6c9650269695cc5a5634bc4312d00638b3) |
| 25924375 | curve | USDT → DAI | $2.0M | [0xa883…a209](https://etherscan.io/address/0xa883710b6dbf008a1cc25722c54583e35884a209) | [0x25d1…1968](https://etherscan.io/tx/0x25d131eb906dccac5ebf85efc4ad5fecfd39f9b38f30c36f680c34dfbd161968) |
| 25924435 | uniswap_v3 | WETH → USDC | $1.8M | [0xc623…67c2](https://etherscan.io/address/0xc623b0b546bf3031ba88a583a46d5180df8d67c2) | [0xfea9…96b1](https://etherscan.io/tx/0xfea9aa1a7b6fcc350974b42721103713280989ba6edeb0853cb045e1128696b1) |
| 25924435 | uniswap_v3 | USDC → WETH | $1.8M | [0xc623…67c2](https://etherscan.io/address/0xc623b0b546bf3031ba88a583a46d5180df8d67c2) | [0xd3d8…9c95](https://etherscan.io/tx/0xd3d8c7f3579df8ff5bf5e735f1a2c5d38a7470295cda62432fe6f7f623ec9c95) |
| 25924144 | curve | USDT → DAI | $1.6M | [0x3980…a54d](https://etherscan.io/address/0x3980daa7eaad0b7e0c53cfc5c2760037270da54d) | [0x982c…5bd7](https://etherscan.io/tx/0x982c8c171fc9cdf5a250e353770e00e5380423953c592ed817b4516b35a95bd7) |
| 25924375 | uniswap_v4 | USDT → USDS | $1.4M | [0xa883…a209](https://etherscan.io/address/0xa883710b6dbf008a1cc25722c54583e35884a209) | [0x25d1…1968](https://etherscan.io/tx/0x25d131eb906dccac5ebf85efc4ad5fecfd39f9b38f30c36f680c34dfbd161968) |
| 25924156 | uniswap_v4 | USDS → USDT | $1.4M | [0x5c35…fce1](https://etherscan.io/address/0x5c3593481cba011737e36ded62f1797c9f6afce1) | [0x10c3…82ed](https://etherscan.io/tx/0x10c3709ca157d26e8e879da323d0a2f5f857f53d28ef517702b251c2d32382ed) |
| 25924387 | uniswap_v4 | USDS → USDT | $1.3M | [0xbee2…cccd](https://etherscan.io/address/0xbee242d3a94420551c65f5b16d9a1c918910cccd) | [0x053f…3c66](https://etherscan.io/tx/0x053f13eadfbac91c5faa98ff535efa353e7e736cb8c601f26a7de222f3443c66) |
| 25924144 | uniswap_v4 | USDT → USDS | $1.1M | [0x3980…a54d](https://etherscan.io/address/0x3980daa7eaad0b7e0c53cfc5c2760037270da54d) | [0x982c…5bd7](https://etherscan.io/tx/0x982c8c171fc9cdf5a250e353770e00e5380423953c592ed817b4516b35a95bd7) |
| 25924259 | uniswap_v2_like | 0x59d1…90b5 → WETH | $1.1M | [0xc54b…1097](https://etherscan.io/address/0xc54b77b28ee4d18cd3d93991f08b79bc85c71097) | [0x00dc…60eb](https://etherscan.io/tx/0x00dce6f5e257b25575c1a1d2ead3f7c68850d61d767efaee4f378168c92960eb) |
| 25924259 | uniswap_v2_like | WETH → 0x59d1…90b5 | $1.1M | [0xc54b…1097](https://etherscan.io/address/0xc54b77b28ee4d18cd3d93991f08b79bc85c71097) | [0xb86f…a680](https://etherscan.io/tx/0xb86f4933a820e799695b937f0436dfb64a3cf36625fbd1e85f33bbb22cbfa680) |

## E. Bridges, issuance, staking

Outbound: $194.2M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $29.8M (418).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| CCTP | USDC | Arbitrum | 87 | $104.0M | 0x968d48e3f318… $100.0M |
| OFT | USDT | eid 30383 | 5 | $30.3M | – |
| OFT | USDT | eid 30420 | 82 | $22.2M | – |
| CCTP | USDC | domain 21 | 7 | $6.4M | 0xd3abc2b51534… $6.4M |
| CCTP | USDC | Aptos | 6 | $5.0M | 64c815fa7c79a1… $5.0M |
| CCTP | USDC | Solana | 72 | $4.3M | 122058680a4d6e… $3.6M |
| CCTP | USDC | Polygon | 38 | $3.5M | 0xf70da97812cb… $2.9M |
| OFT | USDG | eid 30416 | 47 | $3.4M | – |
| CCTP | USDC | domain 15 | 20 | $1.9M | 0xc1062b7c5dc8… $970k |
| OFT | USDT | eid 30390 | 2 | $1.5M | – |
| OFT | USDT | Polygon | 9 | $1.4M | – |
| CCTP | USDC | Avalanche | 18 | $1.4M | 0x65c340eb0688… $707k |
| CCTP | USDC | Base | 133 | $1.3M | 0x721b5310ec76… $500k |
| CCTP | USDC | domain 19 | 25 | $1.3M | 0x4fd045534686… $1.1M |
| OFT | USDT | Arbitrum | 18 | $878k | – |
| OFT | USDe | eid 30383 | 6 | $729k | – |
| OFT | USDC | BNB | 5 | $600k | – |
| OFT | USDG | eid 30274 | 8 | $574k | – |
| OFT | USDT | BNB | 16 | $487k | – |
| OFT | PYUSD | Solana | 3 | $450k | – |

Issuance totals: USDC burn $279.4M (509); USDC mint $153.1M (703). Largest: USDC mint $49.0M ([0x5d19…8a34](https://etherscan.io/tx/0x5d1909575f34eceebe6f745aa3857c5c4520222c6f4309446569382fa9ee8a34)); USDC burn $49.0M ([0x9dd7…2bc0](https://etherscan.io/tx/0x9dd7a20dd527af11dae30c314d0b2fc05189b15136bc9e2e8fc1866a7cf42bc0)); USDC mint $48.0M ([0xde5a…ed3d](https://etherscan.io/tx/0xde5ad949d07bf3046fa6208fdcea6e9fdbdf2806cfd36c34506f201377fbed3d)); USDC burn $48.0M ([0x0bf8…d8ba](https://etherscan.io/tx/0x0bf83acb7380497f5c7b44ad302f1c55e8936c7c359bacdb208d0016e413d8ba)); USDC mint $20.0M ([0x79a8…a29e](https://etherscan.io/tx/0x79a8902a2e075f7ec35d262388cc455c084a54d2babb9ef6a55c94c82525a29e)).


WETH wrapped 33165 ETH, unwrapped 27735 ETH; Lido staked 788.1 ETH, withdrawal requests 1368.8 ETH; sUSDe cooldowns 17 for $3.8M.


## F. Gas market and block production

Base fee 0.077 → 0.086 gwei (min 0.037, median 0.055, max 0.129); blocks 51% full; median tip 0.059 gwei; 3.7% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 681,  Quasar (quasar.win)  297, BuilderNet 152, Eureka (eurekabuilder.xyz) 152, bombora.build  62, gethgo1.25.10linux 15.


Most active senders: [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 6555, [0xe883…dd91](https://etherscan.io/address/0xe8832a868c091263ed190a9f4be304a03895dd91) 3859, [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 3313, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 2329, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 2116, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 1948, [0xb2ea…1634](https://etherscan.io/address/0xb2eafb2d020af198ae4888f3a4d6af35cead1634) 1880, [Binance 17 (model-memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 1738, [Binance 18 (model-memory)](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 1588, [0xbb2f…37e0](https://etherscan.io/address/0xbb2f33f73ccc2c74e3fb9bb8eb75241ac15337e0) 1265.


Intent fills: OneInchFilled 994, CoWTrade 933, UniXFill 219. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

