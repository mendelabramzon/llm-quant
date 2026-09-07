# Method: ten hours of Robinhood Chain (2026-09-07, 04:06–14:06 UTC)

## What the chain is

Robinhood Chain is an Arbitrum Orbit (Nitro) L2 settling to Ethereum with blob data availability, chain id 4663,
gas token ETH, ~0.1 s blocks (~10 blocks/s). The public RPC is `https://rpc.mainnet.chain.robinhood.com`, the explorer
is Blockscout at `robinhoodchain.blockscout.com`. Its L1 batch poster (0xdaa52608...) writes to the SequencerInbox
0xbd0d173e... and has been the single largest blob poster on Ethereum in this repo's mainnet windows since 09-07 morning.

## Window and data

- Window: blocks 56,535,399–56,892,272 (356,874 blocks), 04:06:08–14:06:07 UTC, chosen as "last 10 hours" at 14:06 UTC.
  The window contains the US pre-market and the first 36 minutes of the regular session (opens 13:30 UTC).
- Collector: `scripts/orbit_collect.py`. Each 100-block unit = one batched `eth_getBlockByNumber(full)` request plus one
  batched `eth_getBlockReceipts` request, reduced on the fly to `data/<first>.jsonl.gz`: every block header, every
  transaction joined with its receipt (gasUsed, gasUsedForL1, effectiveGasPrice, status, log count, created address,
  first 512 bytes of calldata), all logs from 217 whitelisted addresses (199 stock tokens from the Blockscout registry,
  USDG, WETH, steakUSDG, both ERC-4337 EntryPoints, ArbSys, the fee distributors, the fee router, Axiom, Relay,
  FormationMarket, the Pons fee router) plus all logs with whitelisted topics (Uniswap v2/v3/v4 swaps, pool creations,
  liquidity changes, UserOperationEvent, L2ToL1Tx, WETH deposit/withdrawal, ERC-721 transfers). Every other log is
  only counted (per emitter and topic; ERC-20 transfers per token with mint/burn counts and a capped distinct-receiver
  count).
- Endpoints (from chainlist, tested 2026-09-07): Blockmachine and PublicNode answer 100-block batches in <1 s but
  rate-limit sustained load with HTTP 429; bloXroute is steady but slower; the official RPC allows ~1 request/s;
  dRPC's free endpoint rejects batches; PublicNode refuses `eth_getLogs`; the official RPC caps `eth_getLogs` at 10,000
  logs and times out on unfiltered 5,000-block ranges. The four-endpoint pool sustained ~150 blocks/s (≈1,500 tx/s),
  so the window took ~40 minutes. The Python `urllib` default User-Agent is blocked by the official RPC (HTTP 403) and
  the Blockscout API is behind a Cloudflare challenge unless a browser User-Agent is sent.
- Analysis: `scripts/orbit_scan.py` (one streaming pass; pool keys for the most active pools resolved through
  Uniswap v4 `PositionManager.poolKeys(bytes25)` and v3 `token0/token1`, names from Blockscout, selector and event
  names from OpenChain; all cached in the window directory) and `scripts/orbit_followups.py` (L1 cost from the batch
  poster's mainnet transactions, fee-account balance history, weekly distributions, the stock-token registry's
  blocklist events, identities).
- L1 side: the batch poster's 1,605 transactions in the window were assembled from this repo's saved mainnet blocks
  (`live_5h`, `live_midday`, 04:06–12:39 UTC) plus 482 blocks fetched from Infura for 12:40–14:11 UTC; blob prices were
  recomputed from `excessBlobGas` with the update fraction calibrated on 12 sampled receipts (BPO2 fraction matched
  with 0.0% error).

## Conventions

- "User transactions" exclude the one ArbOS internal transaction per block (type 0x6a) and L1-initiated deposits
  (types 0x64/0x68/0x69).
- Fees are `gasUsed × effectiveGasPrice` from receipts. On this chain `effectiveGasPrice` equals the block base fee in
  100% of transactions (Nitro ignores priority fees) and `gasUsedForL1` is zero (L1 pricing is switched off:
  `ArbGasInfo.getPricesInWei` returns 0 per calldata byte), so fees are pure L2 base fee.
- USD: USDG = $1; ETH at the on-chain WETH/USDG volume-weighted price per 15-minute bucket; a stock token at
  Blockscout's rate (falling back to its own USDG pool's price). Stock-token prices from Blockscout are a coarse
  reference, not a market quote.
- "Failed" = receipt status 0; failed transactions pay the same fee.

## Limitations

- Logs outside the whitelist are counted, not stored: token flows for arbitrary memecoins, hook events and
  aggregator events are described from counts and from Blockscout spot checks, not from full decoding.
- Uniswap v4 pools created before the window whose liquidity never went through the PositionManager cannot be
  resolved to a token pair from chain data alone; their swaps stay unpriced and are reported as such.
- The chain's reported speed limit (`getGasAccountingParams` = 7M gas/s) is inconsistent with the observed sustained
  20–40M gas/s at a stable base fee; the fee mechanism's effective parameters are not derivable from the public
  precompiles (Bitquery's 2026-09 investigation reports the same gap).
- Blockscout's `exchange_rate` for stock tokens is used for valuation where no USDG pool traded; two tokens (MU, GME
  duplicates) show implausible rates and are excluded from USD totals where flagged.
