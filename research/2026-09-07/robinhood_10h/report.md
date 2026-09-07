# Robinhood Chain, ten hours: 2026-09-07 04:06–14:06 UTC

Robinhood Chain is an Arbitrum Orbit L2 (chain id 4663, Nitro v3.11, ~0.1 s blocks, ETH gas, USDG as the dollar).
This window covers blocks 56,535,399–56,892,272 (356,874 blocks), from the middle of the US night through the first 36
minutes of the regular US session (opens 13:30 UTC). Every block, every transaction with its receipt, and every log
of 217 tracked contracts (the 199 stock tokens, USDG, WETH, EntryPoints, fee distributors, the main routers) plus every
DEX/AA/bridge event were collected; the rest of the logs were counted. Method, endpoints and limitations are in
[method.md](method.md); the deterministic tables are in [tables.md](tables.md), the external checks (L1 cost, fee
accounts, registry, identities) in [followups.md](followups.md), the narrative in [insights.md](insights.md).

## Headline

| | |
|---|---|
| Blocks / block time | 356,874 / 0.101 s |
| Transactions | 3,588,610 total; 3,229,934 user (89.7/s); 358,426 ArbOS internal; 250 L1-initiated |
| Gas | 865.8 G (24.05 M gas/s; 268k per user tx) |
| Fees paid | 279.2 ETH ≈ $696k at the on-chain ETH price ($2,494); $0.216 per user tx; 14.2 ETH of it by reverted txs |
| Base fee | 0.302–0.437 gwei, median 0.322 (floor 0.02); only spike at the 13:30 UTC market open |
| Unique senders | 223,005 (peak 25,279 in the 13:30 bucket) |
| Failed transactions | 284,969 (8.8%) |
| Contract creations | 2,783 (409 by one EOA) |
| L1 cost of the window | 1,605 batches, 4,815 blobs (631 MB), 0.0249 ETH ≈ $62 (blob price 0.002–0.05 gwei) |
| Fee revenue : L1 cost | ~11,000 : 1 |

The window's demand, by who pays gas: a Relay solver fleet (19.5% of fees), an anonymous 1%-fee swap router (14.3%),
ERC-4337 bundlers (9.9%), Axiom (3.9%), Uniswap's UniversalRouter (3.8%), OKX's DexRouter (3.6%), an unverified
launchpad router (3.1%), Multicall3 (2.0%), Pons launch contracts (3.1%). The rest is a long tail of 200k wallets.

## 1. Fee economics and where the money goes

- Fees are pure L2 base fee. `ArbGasInfo.getPricesInWei` returns 0 per L1 calldata byte and `gasUsedForL1` is 0 on
  every receipt; `effectiveGasPrice` equals the block base fee on 100% of transactions, so the 175,818 transactions
  (5.4%, 9,674 senders) that bid ≥3× the base fee, up to 3,000 gwei (8,721×), paid nothing extra. Nitro orders
  first-come-first-served; the bidding is inherited Ethereum reflex.
- The base fee left its 0.02 gwei floor around 08-24 and ran 0.31–0.89 gwei since 09-01 (six-hour samples in
  followups.md); this window sat at 0.30–0.34 with the decay continuing. The network fee account (RewardDistributor
  0xbc5c3a7a) accrued 1,300–2,700 ETH per day from 09-01 to 09-06 and held 11,652 ETH at 09-06 close; at this window's
  rate the run-rate is ~700 ETH/day, so revenue is falling with the fee while transaction counts hold near 12M/day.
- Distribution: both fee accounts are RewardDistributors paying 90% to 0x8b3511B4 (a Robinhood-side EOA that forwards
  to a BitGo ForwarderV4) and 10% to an ArbChildToParentRewardRouter whose L1 target is a Gnosis Safe holding 351 ETH,
  the Arbitrum DAO's expansion-program share. A keeper calls `distributeRewards` every Monday around 18:01 UTC; the
  08-31 sweep paid 1,009 + 112 ETH (network) and 276 + 31 ETH (infra). Today's sweep, due four hours after the window,
  will be ~10× the last one. No distribution events fell inside the window.
- Ethereum side: the batch poster paid 0.0034 ETH of blob fees and 0.0215 ETH of execution fees for 4,815 blobs
  (BPO2 blob-fee schedule, calibrated to 0.0% error on sampled receipts). Batch cadence rose from 121–159 per hour to
  216 in the 13:00 hour with the market-open burst.

## 2. The Relay solver fleet

RelayApprovalProxyV3 (0xccc88a9d, verified) received 185,834 `permit2TransferAndMulticall` calls at 908k gas each and
burned 54.5 ETH, the largest single gas sink. 31 EOAs with 5,700–6,500 calls each sent 98.2% of them; each solver spent
~1.9 ETH of gas in ten hours. RelayRouterV3 (0xb92fe925) emitted 990,253 `SolverCallExecuted` steps and 207k
`FundsMovement` events. The user side is the RelayDepository (0x4cd00e38): 143,571 USDG deposits worth $42.9M (average
$299) from more than 3,000 addresses and 15,166 native deposits worth 3,971 ETH, swept out in 600 withdrawals. Fills
delivered WETH to 1,581 distinct addresses and stock tokens (AMC, FIG, GME, IBM, DJT) to dozens each; the executor
contract 0x8f10b468 that the solvers call (342k `Exchange` events, owner-only role admin) passes stock tokens and
memecoins through symmetrically (AMC 222k tokens in and out, NVDA 10k with 161 counterparties). Bitquery's 09-03
investigation saw this proxy as an unidentified "settlement contract" paying 15% of the chain's fees; it is Relay, and
the deposit sizes say the flow is retail-sized app order flow rather than arbitrage. The canonical Arbitrum bridge saw
250 L1→L2 deposits (733 ETH) and 19 L2→L1 messages in the same window.

## 3. The 1% router

0x65050a9b (TransparentUpgradeableProxy, unverified implementation 0x655d2294 with PancakeSwap/Algebra/Uniswap
callbacks, `factoryV2/V3`, `feeRate`, pause) took 345,782 `swap(route[],...)` calls: 10.7% of all user transactions,
40.0 ETH of gas, 7,942 ETH of msg.value. 3,000+ distinct senders; 551 of them sent ≥100 calls (28.5% of its traffic,
the top one 1,495). Every swap emits `FeeCollected(token, payer, amount, timestamp)`: 330,581 events in native ETH
summing to 167.7 ETH (~$418k) and 10,277 in USDG summing to $13.8k, a flat 1% of the input (0.0002 ETH on a 0.02 ETH
buy), so ~16,800 ETH (~$42M) of ETH-side volume went through it. That fee income is 62% of the sequencer's whole gas
take for the window, accruing to an owner that is not verified anywhere. Through it moved WETH (17,052 in/out, 975
counterparties), NVDA (24k tokens, 41,634 transfers, 633 counterparties), AMC, DJT, GME and SNAP stock tokens and the
day's memecoins. A sister deployment (0xe492912f, 30,995 calls) shares the ABI.

## 4. Tokenized stocks

| | |
|---|---|
| Active tokens | 170 of 199 in the registry ("X • Robinhood Token", BeaconProxy → verified `Stock` impl 0xb35490d6) |
| Transfers | 1,459,531 (NVDA 352,681; SPY 150,825; AMD 92,399; AAPL 91,158; SLV 57,597; GOOGL 54,723) |
| Value moved | ~$268M at Blockscout reference prices; NVDA $53.3M, GLD $41.1M, SPY $30.6M, AMC $13.6M, AAPL $10.7M, TSLA $9.9M, SPCX $9.4M, GME $8.1M |
| DEX share | 1,037,560 transfers (71%) touch a Uniswap pool; 323,207 swaps, $59.8M |
| Addresses | 38,883 distinct |
| Mints / burns / admin events | 0 / 0 / 0 (no blocklist, pause, oracle or multiplier events; registry history shows only test blocks) |

Supply was fixed for the whole window, including through the US open: whatever Robinhood issues or redeems is not
happening on this chain in these hours. The market open still doubled the chain (15-minute buckets):

| bucket UTC | user txs | stock transfers | swaps | DEX $ | base fee max gwei |
|---|---|---|---|---|---|
| pre-open median | 74,919 | 30,922 | ~57,000 | ~7.8M | 0.35 |
| 13:00 | 108,372 | 44,620 | 81,998 | 11.3M | 0.323 |
| 13:15 | 106,535 | 41,410 | 76,504 | 8.3M | 0.320 |
| 13:30 | 141,562 | 80,386 | 99,179 | 14.4M | 0.437 |
| 13:45 | 122,220 | 84,012 | 93,561 | 10.2M | 0.408 |

On-chain prices from the stock/USDG pools match the reference within 0.5% for NVDA (233.5 → 231.5 vs 232.47), SPY,
AAPL, AMC, GLD, GOOGL and MSFT; TSLA traded at $371.1 against a $355.45 reference all window (+4.4%, 6,663 swap prints)
and RCAT at +4.4%, so either the reference lags or the on-chain token carries a premium. Pons memecoin launches now
use stock tokens as the quote asset (cyberbeer/NVDA 38,937 swaps, FINDER/AAPL 17,401, HOODSHOP/SHOP 17,526,
SLV/SILVERBACK 15,842), which is where a good part of NVDA's transfer count comes from.

A stock-token market maker sits at 0x51c72848 (unverified, 3.26M lifetime token transfers): 10,681 WETH in and 10,978
out (~$54M) against SPCX (2,521 / 2,606), NVDA (1,478 / 1,599), AAPL, QQQ, MU, PLTR, TSLA, SPY, AMD, INTC and CRCL,
with 22 counterparties in total. It holds 1,175 WETH, $654k USDG and stock inventory, and is topped up in 350–750 ETH
clips from a 5,600-ETH whale (0x53091256) through two relay EOAs (0x97b237ff, 0xbc8a0f5e); those are the window's
largest native transfers.

## 5. DEX and launchpads

2,502,292 swaps: 1,067,758 Uniswap v3, 1,389,748 v4, 44,786 v2, across 3,338 active v3 pools and 10,612 active v4 pools.
1,136,954 swaps in 1,265 pools could be priced: $355.8M, of which the 1-bp WETH/USDG v3 pool is $185.0M (52%; 398,755
swaps, 269 traders) and prints the chain's ETH price (2,484–2,511 over the window). Next: WETH/PONS $14.5M,
NVDA/USDG $12.6M, two more WETH/USDG tiers $8.6M and $7.6M, PONS/USDG $6.4M, AMC/USDG $5.9M, WETH/SPY $3.2M,
CASHCAT/WETH $3.2M, WETH/NVDA $2.9M, SPCX/USDG $2.8M. Stock-token pools sum to ~$47M of the top 40. Pools whose keys
are not recoverable from chain data (Pons hook pools without PositionManager positions) hold the largest unpriced
share.

Pool creation ran at one every seven seconds: 5,156 new v4 pools (3,960 hookless, 678 DopplerHookInitializer, 138
PonsV2MemeHook, 58 an unnamed hook), 210 v3 pools, 87 v2 pairs. PonsV2LaunchFactory (4,478 calls at 2.7M gas) and
PonsV2LaunchAndBuy (3,866 at 3.9M gas) alone burned 8.5 ETH. One sniper EOA, 0x49bbf2b7, sent 34,331 transactions
(nonce span 34,312), 10,331 of them straight at the Pons hook; a sniper contract exposes `snipe(...)` and the hooks
charge a decaying snipe tax. v4 liquidity was modified 133,549 times and 29,538 v4 position NFTs were minted.

## 6. USDG and DeFi

2,456,793 USDG transfers ($1.07B, 42,415 addresses). Paxos minted $7.09M (110 events) and burned $3.52M (35) natively
on the chain, net +$3.57M. Morpho Blue took $24.0M in and paid $23.9M out (35 counterparties); steakUSDG rebalanced
$19.1M each way in $4.5–4.7M clips against Morpho; the ethenaUSDG VaultV2 took $3.6M and paid $4.5M; Spark's spUSDG
vault netted +$3.55M; a ZkLighter bridge proxy netted +$1.26M; the largest single transfer was $12.2M between two EOAs
at 11:52. 2,340,218 WETH transfers make WETH the routing asset for nearly every swap.

## 7. Account abstraction and delegated EOAs

161,449 user operations (97.4% success) from 49,264 smart accounts: 121,851 through EntryPoint v0.8 (100 bundler EOAs
with 0x4337… vanity prefixes, ~1,100 ops each), 37,497 through v0.7 (22 bundlers), 2,101 through v0.6. 93% of ops paid
their own gas; a VerifyingPaymaster (0x00000000000667) sponsored 8,878 (5.5%), Pimlico's SingletonPaymasterV7 980.
`handleOps` burned 27.7 ETH (9.9% of fees). EIP-7702 set-code transactions: 38,779 (1.2%) from 4,773 delegated EOAs,
mostly into the EntryPoints, Multicall3 and two batch-executor delegates.

## 8. Bots, reverts and bids

284,969 transactions reverted and paid 14.2 ETH for it. The reverts sit in a dozen MEV contracts: a v4 quoter/executor
0x1521027b (21,406 calls, 81% failed), "getRich" 0xb0550000 (11,127, 90%), 0x4961443e (85%), 0x58accac8 (84%),
multi-DEX callback bots 0x44782f83 / 0x6a295210 (50–56%), 0x520ed467 (38%), and 0x9e8a3ce4 (100%: one wallet,
0x82d82125, sent 16,648 transactions that all failed and cost 1.34 ETH). Top bids: 3,000 gwei and 1,500 gwei from
0x59495c04 to 0xb1000000…, 1,000 gwei repeatedly from 0x093520bc, none charged. UniversalRouter users failed 9.8% of the
time (slippage on new launches). 0x6cb4d309 created 409 contracts, the classic disposable-contract sniper pattern.

## 9. Everything else

- Aggregators and terminals: Uniswap UniversalRouter 176,583 calls, SwapRouter02 79,707, V2 router 31,695, v4
  PositionManager 41,398; OKX DexRouter 64,689 (10.2 ETH gas); KyberSwap MetaAggregationRouterV2 184,915 swaps;
  0x AllowanceHolder 23,276; Axiom's trade router 93,276 calls (143 heavy senders, 2,100 ETH of value, 10.9 ETH gas);
  an unverified launchpad router 0xed090594 66,360 calls (8.6 ETH gas); a fee-collector Diamond 0xb300000b 28,377.
- NFTs: 178,239 ERC-721 transfers; SeaDrop mints of Frost MysteryBox (10,000), PonsBug (7,211), Robinhood Mingos
  (5,555), Mosa Clan (4,316), Ratatouille (4,067).
- Mass distributions: a MEME token reached 2,000 distinct receivers per 100 blocks (24k transfers); two fake "Global
  Dollar / USDG" DropERC20 tokens hit 500+ receivers per 100 blocks, the mainnet address-poisoning pattern; a
  SchiffyGoldClaims airdrop (1,813 claims in the first hours); "HoodLighterShare" 32k transfers.
- Transaction types: 2,814,121 EIP-1559, 374,619 legacy, 38,779 EIP-7702, 2,415 EIP-2930; 58 ETH deposits (type
  0x64), 96 retryable submissions and 96 redeems from L1.

## 10. Open questions and what to watch

- The chain reports a 7M gas/s speed limit (`getGasAccountingParams`) yet sustained 24M gas/s at a stable fee; the
  effective pricing parameters are not the ones the precompiles expose. Bitquery's 09-03 note reports the same gap.
- Who operates the 1% router and the market-maker venue. Both are unverified; the router's fee take ($432k / 10 h)
  is the single most valuable unattributed position on the chain.
- Where Robinhood's stock-token issuance happens: none of the 199 tokens minted or burned in a window that spans the
  US open. Either issuance is batched outside these hours or occurs elsewhere and is bridged.
- The fee decay: from 0.89 gwei on 09-04 to 0.31 gwei now with flat transaction counts. The Monday 18:01 UTC sweep
  size is the cleanest weekly read on the chain's revenue.
- TSLA's +4.4% on-chain premium versus the reference is either a stale reference or a real dislocation; a repeat window
  during the regular session with an external quote would settle it.

## Files

`analysis.json` (all figures), `tables.md` (deterministic tables), `followups.md` (L1 cost, fee accounts, weekly
distributions, base-fee history, registry events, identities), `method.md`, `insights.md`, `data/` (3,569 chunk
files, 1.1 GB), `pools.json` / `names.json` / `selectors.json` (caches), `stock_tokens.json`, `keep_addresses.json`,
`l1_poster_window.json`, `basefee_history.json`, `manifest.json`.

Scripts: `scripts/orbit_collect.py`, `scripts/orbit_scan.py`, `scripts/orbit_followups.py`.

External references: Bitquery, "Robinhood Chain Gas Fees: 25x in 11 Days, $4.5M a Day" (2026-09);
docs.robinhood.com/chain (connecting, bridging); robinhoodchain.blockscout.com.
