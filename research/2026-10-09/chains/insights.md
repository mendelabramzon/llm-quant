# Chains with high activity, and where new activity is worth trading — 2026-10-09

The window is the complete UTC day **2026-10-08**, read two ways: from eight aggregators for ~570 chains (`census.json`,
history back to 2025-09) and directly from 67 chains in 17 families (`probe.json`, every number with its method). The
detectors, the verification and the tables are in `report.md`; this note is the reading. Every count below is the probe's
unless it says otherwise, and every one was compared with an aggregator on the same day where one exists (`verify.json`:
29 chains have a same-day reference; the probe agrees within ±10% on 34 of 42 chain-source pairs and within ±25% on 39;
the exceptions are explained in §4).

## 1. The list

**By transactions a day** (user transactions; protocol system transactions removed; ± is one standard error of a block
sample, no ± means an exact counter or every block read):

| family | chains, busiest first |
|---|---|
| HyperCore | Hyperliquid 2.06B ± 0.20B *actions* (orders and cancels, ~24k a second) |
| Solana | 177.6M ± 5.2M non-vote, 31% of them failed |
| EVM | BSC 16.9M, Base 12.3M, Robinhood Chain 8.1M, Monad 6.3M, Polygon 5.4M, Arbitrum 2.1M, MegaETH 2.0M, Ethereum 1.9M, XDC 1.8M, OP 1.7M, opBNB 1.3M, Celo 0.9M, X Layer 0.8M, Arc 0.8M |
| Tron | 11.4M ± 0.1M |
| Move | Aptos 10.2M, Sui 7.4M |
| ledgers | Stellar 5.1M, XRPL 2.4M ± 0.4M, Algorand 1.3M, Hedera 0.8M |
| TON | 3.4M ± 0.2M |
| Cosmos | Injective 1.8M, dYdX 0.7M, THORChain 0.19M, Celestia 0.13M |
| NEAR | 1.04M ± 0.13M |
| UTXO | Bitcoin 630k, Litecoin 157k, Dogecoin 19k |
| other | Cardano 543k (16x its usual day — §3), Starknet 184k, Tezos 105k |

**By where it is reasonable to trade** (`chain_census.tier_of`): of 569 chains, 12 are *deep* — Solana, BSC, Base,
Hyperliquid L1, Ethereum, Tron, Robinhood Chain, Polygon, Avalanche, Arbitrum, NEAR, X Layer — and 28 *tradeable* —
Monad, OP Mainnet, Arc, Sui, Plasma, Stellar, TON, XRPL, Aptos, Sei, Ink, Starknet, Flare, Cronos, Cardano, Mantle,
Unichain, PulseChain, Gnosis, Sonic, Hedera, Celo, Stacks, Provenance, Hydration, Tempo, Injective, Saga; 39 are
*token_only*, 71 *thin*, 419 *inactive*. (DefiLlama's "Off Chain" row was tiered as deep on the first build; it is a
pseudo-chain for off-chain venues and is now excluded.) *token_only* is the
other half of "reasonable to trade": Bitcoin, Algorand, THORChain, World Chain, ZKsync, Dogecoin, Zcash and others have
little on-chain liquidity, so their activity is a reason to trade the token (spot or the Hyperliquid perp), not on the
chain.

**Busy is not the same as active.** Value per transaction separates them. MegaETH carries $0.23 of net transfers per
transaction because 87% of its transactions are two oracle contracts updating each other; opBNB $0.05 (daily check-ins,
a game); XDC $1.58 (56% validator signatures to the `0x…89` system contract); Plume $0.99, Soneium $2.02, Blast $2.99,
Berachain $5.22, Ronin $8.71. At the other end Ethereum carries $36k per transaction and Tron $3.3k — the dollar rails.
The probe now reports this as `bookkeeping` (oracle, validator-signing and block-builder targets listed per chain in
the registry) beside the headline count: MegaETH 87%, Flare 86%, Unichain 74%, XDC 56%.

**Concentration says who the activity is.** One contract receives most of the value on Plasma (USDT0 itself, 90%),
Monad (Aave's `PoolInstance`, 90%, carrying the PT-AUSD-8OCT2026 position on its maturity day, §2), Sonic and Katana (a
`NonfungiblePositionManager`, 87% and 99%: position cycling, the pattern this repo found on Base in 2026-09), Kaia (USDT,
92%), XDC (one unverified contract, 89%). On Base four contracts take 74% of net transfer value (`0x6104…` 45%,
`0xb093…` 11%, `0x787f…` 10%, `0x2192…` 7%; three unverified, one a bare ERC-1967 proxy): single-leg fills of
$0.3–0.9M, which looks like private market-maker settlement that
DefiLlama's DEX adapters do not count, which is why Base's net transfer value ($129B/day) is two orders of magnitude
above its DEX volume ($1.1B/day). OP Mainnet has the same shape. Transfer value measures what moves; it is not
economic volume, and the report keeps the two apart.

## 2. What the detectors call new (2026-10-08)

Ranked by what it means for trading, not by severity:

1. **Cronos: transactions x2.6** (91k ± 34k on the full probe, 133k on the 40-block backfill, against a 36k median of
   the 13 days before; tradeable, $2.4M/day DEX). A memecoin wave — CROCAT, ULTCAT, BURN, CROBINHOOD lead the token
   transfers — on a chain with on-chain liquidity to trade it. This is the shape the framework exists to catch: new
   activity, idiosyncratic (the cross-chain median that day was x1.08), on a chain where entries and exits exist. Thin,
   though: the DEX volume behind it is a few million a day, and the contract taking 28% of the transactions cannot be
   named from Etherscan's API (Cronos is not on it).
2. **Cardano: transactions x16** (34k on 10-05 and 10-06, 327k on 10-07, 543k on 10-08, every block counted; the one
   `high` hit). Not trading: an estimated 348k ± 84k of the day's token transfers are HOSKY (from 12 sampled blocks) and
   net value is ~$51 per transaction — a mass distribution. Activity without value; the trade, if any, is the
   distributed token, not ADA.
3. **Arbitrum: active addresses x2.9** (346k vs 116k). Explained by one contract, `0x12f51e66…`, born at 14:58 UTC on
   10-08, receiving ~1,000 transactions an hour, each from a different wallet, each worth ~1e-7 ETH at 21,451 gas: a
   wallet-pinging campaign (points or sybil farming). No value, nothing to trade — and the detector would have called it
   a surge without the who-layer.
4. **Stablecoins arriving.** Tempo +$678M in 30 days (largest step +$310M on 09-30: Open USD), Plasma +$396M in 30 days,
   XRPL +$215M in 7 days, Arc +$110M in 7 days, USDC on X Layer 7x in a week ($17M → $121M), USDf on Ethereum +$345M in a
   week, USDC on NEAR and Hedera, USDe and USDT on Monad. Dollars arriving are the earliest sign of an economy forming,
   but Tempo is the caution: $760M of stablecoins and $1.3M/day of DEX volume — the float is sitting, not trading.
5. **Monad's "$817M" is one transfer scaled up.** PT-AUSD-8OCT2026 and its Aave wrapper appear in one of 400 sampled
   blocks, which the stratified estimate scales by ~540 (single-block share 1.0, marked † in the report). The event is
   real — the PT matured on 10-08 and positions unwound through Aave's pool — but its size is not measured by a sample,
   and `probe_new_asset` refuses single-block assets for exactly this reason.
6. **OP Mainnet DEX volume x2.7 for the week** — but 98% of the excess is one day (10-03, $496M against ~$30M). A spike,
   labelled as such; until a second day prints, it is one print (an adapter artifact or one block trade), not a regime.
7. **Starknet DEX x3.6 on the day** ($34M vs $9M) and Saga x5.1 ($3.6M vs $0.7M): single-day, idiosyncratic, tradeable
   on Starknet; worth a second day before acting.

The sell-off (ETH −8%, SOL −9% from 10-07 to 10-09) lifted many chains at once — Base +36% and Robinhood +33% on 10-08
in the aggregator series, Algorand 0.80M → 1.31M and Hedera 0.54M → 0.81M in the backfill — but none of these reach a
x2 day against their own month, and the cross-chain market factor (x1.08 on transactions that day) would demote one
that did.

## 3. Measurement lessons (each one is now in code)

- Gross transfer sums do not survive sampling (one Base block of flash loops scaled to "$666B/day" of WETH); value is
  net per transaction on every family (`chain_adapters.net_positive`).
- Solana: version-1 transactions now break `maxSupportedTransactionVersion: 0` (fixed here and in `solana_collect.py`),
  slots are ~0.27 s, per-node performance samples cover ~4.5 h, and GetBlock silently answers below its retention with
  its first available block — a calendar day is read from the public endpoint.
- Aggregators disagree, and the who-layer explains it: growthepie's MegaETH (1.11M) is L2Beat's (1.97M) minus the
  system oracle (1.98M x 0.565 = 1.12M).
- DefiLlama's stablecoin history writes a missing reading as `{}`; read as zero, every gap became a "launch" (USDD on
  Tron, $1.3B). Missing now cannot fire.
- Infrastructure facts: Rootstock's public nodes serve no logs; NEAR's non-archival nodes forget day-old blocks; Aptos
  rate-limits per IP; Blockscout's Base and Arbitrum instances are behind Cloudflare; DefiLlama's bridge and
  derivatives endpoints are now paid.

## 4. Where the verification disagrees

34 of 42 chain-source pairs agree within ±10% on the same UTC day (Base 1.09, Ethereum 1.02, Polygon 1.00, Tron 0.97,
Robinhood 0.95, Starknet 0.98, Unichain 1.02, Celo 1.01, ...). The rest: MegaETH vs growthepie 1.79 (explained above;
vs L2Beat 1.005); Mantle 0.79 (sparse blocks — most hold only the L1-info deposit — so 200 samples leave a 15% error);
Arbitrum 1.17 (inside two standard errors on a bursty day: the `0x12f5…` campaign started mid-afternoon); Linea 0.82;
Ronin 0.88 vs growthepie. Exact readers agree tightly where a second source exists:
Bitcoin and Litecoin within 0.4% of Blockchair, Stellar within 0.05%, Aptos within 0.4% of the Aptos explorer, NEAR
within 2% of NEARBlocks, Cardano exact against Koios. DefiLlama's per-chain DEX breakdown sums to 0.98x its own total
once the "Off Chain" pseudo-chain is removed (1.03x with it).

## 5. Requests for the next iteration (qual → quant)

1. A `new_top_target` detector: a contract newly among a chain's top targets by transactions or value, with its age —
   Arbitrum's `0x12f5…` would have been named on day one.
2. Identify the unverified contracts that carry Base's and OP's value (bytecode lens; same-address deployments across
   chains — `0x278d858f…` appears on Base, BSC, Avalanche and carries 63% of Arc's value).
3. Per-asset flow history, so `probe_new_asset` has a baseline (it is wired but needs a second probe day).
4. An hourly mode for the fastest chains, and Solana's backfill (its blocks are too heavy for the public endpoint).
5. Substrate (Bittensor, Polkadot) and Kaspa adapters; Canton and Provenance have no public node.
6. Install `scripts/launchd/com.llm-quant.chains-daily.plist` so the series accumulates; the detectors' empirical nulls
   on probe-only chains sharpen with every day of history.
