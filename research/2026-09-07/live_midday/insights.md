# Onchain, last 5 hours — 2026-09-07 07:39:59 to 12:39:59 UTC

Blocks 25924044–25925535 (1,492 blocks, 410,759 txs, 1.21M logs) [[verify: blocks]] [[verify: transactions]] [[verify: logs]]. Collected in 9 min / 184k Infura credits.
This window is contiguous with the morning scan (which ended 07:39). It was a **quiet Monday**: base
fee 0.037–0.129 gwei (median 0.055), blocks ~51% full, ETH flat $2,482 → $2,493 (+0.5%, range
$2,478–$2,496). ~$189M priced DEX volume (v4 $85M, v3 $42M, v2 $38M, curve $23M). Only one liquidation.

## The interesting things

1. **Compound USDC is paying ~2x Aave.** Compound v3 USDC supply 6.91% / borrow 8.14% at 91% utilisation,
   versus Aave USDC 3.58% / 4.27% at 93% and Sky SSR 3.60%. A lender earns nearly double on Compound for the
   same asset; the gap is utilisation-driven and capacity-limited but persistent through the whole window.
   Ethena sUSDe implied 4.48%, Aave GHO borrow 4.00%. Spark USDT borrow is back to 3.52% — the morning's
   ALM-shock spike to 7.00% has fully normalised.

2. **Circle net-redeemed $126M USDC.** USDC burns $279M vs mints $153M in 5h (net −$126M supply)
   [[verify: usdc-burn]] [[verify: usdc-mint]]. Includes a
   clean $49M mint-then-burn round trip to 0x55fe002a in adjacent blocks (treasury plumbing).

3. **$104M USDC bridged to Arbitrum via CCTP** [[verify: cctp-largest]], 87 transfers, ~$100M of it to a single recipient
   0x968d48e3 (EOA). Plus $52M USDT out via LayerZero OFT. Largest cross-chain flow of the window.

4. **Binance 14 hot-wallet sweep.** 0x28c6c062 (Binance 14) aggregated 20,759 ETH across 244 deposits and
   swept 12,117 ETH in one tx to internal wallet 0x4976a4a0. Separately a Gnosis Safe 0x2ceb3e99 accumulated
   11,725 ETH (two transfers, no outflow) — custody/treasury build-up, not a market move.
   Exchange net flow (corrected labels; restated again 2026-09-08, see below)
   [[verify: exchange-net-eth]] [[verify: exchange-net-stables]]:
   stETH −$26.0M and ETH −$19.6M out; USDT +$25.8M in; USDC −$6.2M; stables +$23.0M net. The earlier figures counted 22 contracts as exchange deposit sinks because the
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
   is $0, not the $4.0M first reported [[verify: leverage-to-exchange]]: every hop that appeared to reach an exchange landed on a contract
   mislabelled as a deposit sink, and the largest was an Instadapp smart account forwarding inside its own
   transaction. The morning's StacyVault
   reward-timing flash-farmer (0x23fdc534 → 0x0fd368ed) [[verify: stacy-deposit-for]] is still live but slower: ~10 touches in 5h, down
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

Each row cites the recipe that re-derives it: gross inflow [[verify: exchange-gross-usdc]], stables
[[verify: exchange-net-stables]], ETH [[verify: exchange-net-eth]], leverage [[verify: leverage-to-exchange]].

| headline | as first published | corrected |
|---|---:|---:|
| exchange gross inflow, USDC | $823.2M | $497.1M |
| exchange net flow, stables | +$44.0M | +$13.2M (now +$23.0M, see below) |
| exchange net flow, ETH | −$17.4M | −$19.6M |
| leverage-to-exchange | $4.0M | $0 |

Unaffected: the USDC issuance figures ($279.4M burned against $153.1M minted) [[verify: usdc-burn]]
[[verify: usdc-mint]], the $104.0M CCTP send to Arbitrum [[verify: cctp-largest]], the gas attribution
[[verify: gas-top-target]] [[verify: gas-top-target-identity]] and the rate table [[verify: rate-gap-widest]]. All four are now re-derived from the raw blocks by `verify.py` through a separate
code path, and all 13 of its checks pass.

How much confidence the remaining flow numbers deserve is itself now reported. Exchange flow computed with model-memory
labels alone gives stables +$12.8M and ETH −$4.3M; adding behavioural labels gives +$13.2M and −$19.6M. On the earlier
five-hour window the same band runs from +$91.6M to −$24.8M, so the sign of that headline depends on which unverified
labels you accept.

A second correction landed alongside: the wallet this repo had been calling an "exchange hot wallet with USDG desk" is
the Relay solver identified in the [interchain study](../interchain/findings.md), and is now labelled a bridge rather
than an exchange [[verify: msca-not-exchange]] [[verify: no-contract-hot-wallets]]. That is the same class of error as the deposit-sink bug, found by a different route on the same day.

## What is checked, and what is not

Every `[[verify: id]]` above names a recipe in `scripts/verify.py` that re-derives that number from the raw blocks
through a path sharing no aggregation code with `analyze`. Running `live_scan verify --out <this window>` prints the
pair. The point of the markers is the numbers that *do not* carry one: the Compound-versus-Aave gap in item 1, the
EIP-7702 share in item 5, the blob counts in item 6, the wash-swap netting in item 7 and the distribution size in
item 9 are read straight from `analysis.json` with no second derivation. They are the honest backlog for the next
batch of checks, and until then they are stated on one reading only.

## Second correction, 2026-09-08 (the deposit sink that swept $10M)

`mislabelled_flow` flagged [0x3cc9…cf18](https://etherscan.io/address/0x3cc936b795a188f0e246cbb2d74c5bd190aecf18)
here at high severity — $170k in from five senders, $10.0M of USDT out in one leg — and again on the earlier
five-hour window, where the same address forwarded $99.99M. Blockscout says it is an externally-owned account, and its
`exchange_deposit` tag came from the day study's behaviour profile. Retiring that tag moves this window's numbers:

| headline | with the deposit-sink tag | corrected |
|---|---:|---:|
| exchange net flow, stables [[verify: exchange-net-stables]] | +$13.2M | **+$23.0M** |
| exchange net flow, USDT | +$16.0M | **+$25.8M** |
| exchange net flow, USDC | −$6.2M | −$6.2M |
| exchange net flow, ETH [[verify: exchange-net-eth]] | −$19.6M | −$19.6M |

The five-hour window took the larger hit — its entire USDC outflow was this one address — and the reasoning is written
up there. The point worth keeping from this window is that the detector saw it twice before anyone asked, which is the
difference between a ledger and a report.
