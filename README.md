# Onchain research pilot

**System roadmap:** [ROADMAP.md](ROADMAP.md) is the standing plan for turning this into the best onchain research
analysis system — prioritised recommendations (verified labels, TWAP head reads, a findings-verification pass, a detector
registry, an economics harness, a data-access layer), each grounded in a concrete failure this repo has hit. A verified,
provenance-tracked address-label registry (`scripts/address_labels.json`, consumed by `live_scan`) is the first item
landed: counting only `kind` in {exchange, exchange_deposit} as exchange flow corrected leverage-to-exchange on the
2026-09-07 window from $25.7M to $5.3M (CoW's settlement contract was being counted as a CEX) and RLUSD net outflow from
−$101.6M to −$0.9M (a token treasury mis-tagged as a hot wallet).


The latest study is [one day of Ethereum amount outliers, typed](research/2026-09-05/amount_outliers_eth_day/letter.md), with a [detailed report](research/2026-09-05/amount_outliers_eth_day/report.md) and the [LLM's notes](research/2026-09-05/amount_outliers_eth_day/qual_notes.md). It is Ethereum mainnet only, 24 hours (2026-09-04 14:00 to 2026-09-05 14:00 UTC). Known transaction types run deterministic investigations; unresolved clusters become LLM evidence packets, and investigated mechanisms become persistent rules in `scripts/type_registry.py`. Classification coverage is reported separately from the strength of the economic interpretation. The registry was grown in two sessions: Codex on a five-hour window (`research/2026-09-05/amount_outliers_eth_5h`, method in its `method.md`; its notes and report were not written before that session ended) and Claude on the full day, which replayed Codex's 58 types as round 1 and added 32 more over three rounds, the last of them an audit of one sampled occurrence per known type.

2026-09-07, a strategy study: [renting liquidity to a subsidized dollar](research/2026-09-07/captive_flow_lp/findings.md). USDG (Global Dollar / Paxos) rebates over 90% of its reserve yield to network partners, so a partner desk is paid to convert USDC into it and does so daily; that captive, non-toxic flow routes to two thin, ultra-low-fee Uniswap v4 pools where a small, early concentrated LP earns 14–16% APR versus 3.8% in the deep Curve pool. `scripts/captive_flow_lp.py` reads deployed TVL from the tick distribution, realized turnover and fees from the saved logs, the marginal-LP APR-by-size curve, and the taker-concentration checks (block-pinned, replayable offline); a Foundry fork test mints the position in the real v4 pool and collects one day of the observed flow. The same run closes the apxUSD/Strata thread: those below-NAV vaults are STRC tail-risk and first-loss tranches, priced risk rather than a redemption arbitrage.

Afternoon of 2026-09-06, live-scan follow-up: [where the dollar yield sits on mainnet right now](research/2026-09-06/opportunities/findings.md), a block-pinned map of every Morpho Blue market's IRM rate and every Pendle market's implied fixed yield, joined on PT collateral (`scripts/morpho_pendle_scan.py`, deterministic tables in `research/2026-09-06/opportunities/tables.md`).

Read [the research memo](research/2026-09-05/onchain_llm_research.md). It explains the observed mechanisms, research hypotheses, and a proposed division of work between deterministic tools and LLM interpretation.

The pilot samples the same two-minute interval across Ethereum, Base, Arbitrum, Optimism, and Polygon. Raw blocks include full transactions and receipts/logs. Follow-ups retain historical contract calls and selected pool logs. Everything is read-only; no wallet, transaction submission, daemon, or trading service is configured.

The collector uses Python's standard library. Analysis additionally requires `pycryptodome` for Ethereum Keccak, which was already available in the working environment. Run from this directory:

```sh
uv run python scripts/analyze_onchain.py
uv run python scripts/build_research_evidence.py
```

These two commands are offline and do not require the Infura keys. To collect a new discovery sample, supply a new output directory:

```sh
uv run python scripts/onchain_probe.py --out research/new-sample --seconds 120
```

The saved pilot is complete. For interrupted collections, the collector supports `--resume`; it preserves the original time window. `--boundary-recheck` verifies current first/last block hashes and every stored parent link instead of re-requesting all canonical headers. Per-chain manifests record the scope. End-to-end follow-up and report scripts currently target this pilot's paths and block numbers; they are research scripts rather than a general indexer.

The collector reads the first key from the existing local `infura_keys.txt`. Keys are not logged or written to research artifacts. The method-credit ceiling is conservative and applies to one invocation; multiple resumed invocations and follow-ups have their combined attempts reported in `analysis/research_evidence.json`. Estimated credits are not a billing statement. Run Infura jobs sequentially because independent processes do not share a rate limiter.

Useful evidence files:

- `research/2026-09-05/sample/manifest.json`: discovery window, acquisition metadata, completion, and finality snapshots.
- `research/2026-09-05/sample/*_manifest.json`: raw-file hashes and per-chain coverage.
- `research/2026-09-05/analysis/summary.json`: descriptive counts and structural event matches.
- `research/2026-09-05/analysis/research_evidence.json`: memo calculations and offline consistency checks.
- `research/2026-09-05/analysis/candidates.json`: selected examples plus deterministic hash-sampled controls.
- `research/2026-09-05/followup/`: historical state, metadata, focused event histories, and documented retrieval errors.

Protocol event shapes are not protocol identity. The original Polygon files preserve generic failed-receipt log flags; the analysis uses the subsequently verified native-fee-log exception. The memo describes this correction and the remaining limitations.

## Gas outliers: a quant-to-qual proof of concept

`scripts/gas_outliers.py` runs one iteration of the research loop over the saved sample. The deterministic step ranks every user transaction on each chain by gas limit, priority fee (`effectiveGasPrice - baseFeePerGas`), and total fee paid, selects the top three per metric per chain, and writes evidence packets with fact IDs and robust baseline positions. Chain-generated transactions (Arbitrum types 0x64-0x6a, OP Stack type 0x7e) are excluded, and a metric is skipped on a chain where no transaction exceeds the median (priority fee on Arbitrum). The LLM then reads the packets, not raw blocks, and writes `qual_notes.md`; the render step merges both into a report with explorer links.

```sh
uv run --with pycryptodome python scripts/gas_outliers.py scan      # offline, ~2 s
uv run --with pycryptodome python scripts/gas_outliers.py resolve   # bounded RPC: token symbol/decimals, code presence; cached; ~10k credits
uv run --with pycryptodome python scripts/gas_outliers.py render    # packets + context + qual_notes.md -> report.md
uv run --with pycryptodome python scripts/gas_outliers.py show <tx hash> [...]   # full decoded logs for one transaction
```

Outputs live in `research/2026-09-05/gas_outliers/`: `report.md` is the deliverable; `packets.json`, `stats.json`, and `context.json` are the quant artifacts; `qual_notes.md` is the LLM's interpretation keyed by transaction hash, with a `synthesis` section and a `feedback` section that lists what the qualitative pass asks the quant step to add next. `rpc_requests.jsonl` records the follow-up requests without credentials. Re-running `scan` regenerates the quant artifacts and leaves the notes untouched; the render marks any packet without a note.

## Large amounts: the second loop iteration, in USD

`scripts/amount_outliers.py` repeats the loop for a different quant filter: transactions that move large amounts in USD. `prices` reads Chainlink USD feeds pinned at each chain's last sampled block (the feed's `description()` must match the expected pair before its answer is used; the first verified candidate address wins) plus the wstETH ratio, and cross-checks ETH against swaps in the two factory-verified USDC/WETH pools of the pilot. `scan` values every top-level native transfer, every ERC-20 transfer of a registry token (addresses known to the author, checked against the chain by `resolve`) and every WETH wrap or unwrap, nets them per address and asset inside each transaction and across the window, ranks user transactions by largest position change, gross priced volume and native value, describes the population above `--threshold` (default $10,000: assets, shapes, repeated patterns, repeat actors, window-level nets, unpriced tokens), and writes packets for the top 3 per metric with at most one per repeated pattern plus 2 hash-sampled controls per chain. Stablecoins outside the feed set are taken at parity; tokens outside the registry are unpriced and listed rather than valued.

```sh
uv run --with pycryptodome python scripts/amount_outliers.py prices    # bounded RPC: ~3k credits; cached
uv run --with pycryptodome python scripts/amount_outliers.py scan      # offline given prices.json (falls back to in-sample ETH price without it), ~3 s
uv run --with pycryptodome python scripts/amount_outliers.py resolve   # bounded RPC: token symbol/decimals with registry checks, code presence; ~15k credits; cached
uv run --with pycryptodome python scripts/amount_outliers.py render    # packets + prices + context + qual_notes.md -> report.md
uv run --with pycryptodome python scripts/amount_outliers.py show <tx hash> [...]
uv run --with pycryptodome python scripts/cl_cycling_check.py          # offline follow-up asked for by the notes: do per-block liquidity cyclers ever meet a swap?
```

Outputs live in `research/2026-09-05/amount_outliers/`: `report.md` is the deliverable and `letter.md` the short narrative; `prices.json`, `packets.json`, `stats.json`, `context.json` and `cycling_check.json` are the quant artifacts; `qual_notes.md` is the LLM's interpretation keyed by transaction hash with `synthesis` and `feedback` sections. The main finding of this iteration is that most "large" transactions on Base and Optimism are bots minting concentrated-liquidity positions at the end of a block and burning them at the start of the next, which earns gauge emissions while the liquidity is almost never in the pool when a swap executes; `cycling_check.json` tests that on the pilot's 30-minute pool histories.

## Ethereum-only type research: a full day, typed by a growing registry

`scripts/eth_day_collect.py` collects full blocks and unfiltered logs for a window ending at a UTC time or at the latest finalized block (gzip on the wire, adaptive `eth_getLogs` ranges under the 10,000-result cap, resumable, hash-verified); receipts are not collected. `scripts/tx_types.py` runs the loop: `prices` (Chainlink, hourly for ETH and BTC, plus exchange rates and a registry check of every token's decimals), `statuses` (receipts for every no-log native transfer above the threshold), `scan` (USD legs, netting, event-supported flash-loan pairs, same-block sandwiches, implied prices for tokens outside the registry, calldata memos, day-long address profiles), `classify` (rules of `scripts/type_registry.py`, per-type investigation methods, residue clustering, packets, and an archive of every round under `round_XX/`), `resolve` (receipts, code and EIP-7702 designators, token symbols), `render` and `show`. `REGISTRY_ROUND=1..4` replays the registry as it stood after each round.

```sh
uv run python scripts/eth_day_collect.py collect --out research/2026-09-05/eth_day --end 2026-09-05T14:00:00Z --hours 24   # ~0.83M credits
uv run python scripts/eth_day_collect.py verify --out research/2026-09-05/eth_day
uv run --with pycryptodome python scripts/tx_types.py prices                                   # ~21k credits
uv run --with pycryptodome python scripts/tx_types.py statuses --max-credits 900000            # 7,852 receipts, ~0.64M credits
uv run --with pycryptodome python scripts/tx_types.py scan                                     # offline, ~6 minutes
REGISTRY_ROUND=1 uv run --with pycryptodome python scripts/tx_types.py classify --label 'round 1'
REGISTRY_ROUND=4 uv run --with pycryptodome python scripts/tx_types.py classify --audit-known --label 'round 4'
uv run --with pycryptodome python scripts/tx_types.py resolve --addresses <addresses named in the notes> --tokens <tokens>
uv run --with pycryptodome python scripts/tx_types.py render
uv run --with pycryptodome python scripts/tx_types.py show <hash> [...]
uv run --with pycryptodome python -m unittest discover -s scripts -p test_tx_types.py
```

The day: 7,173 blocks, 1,793,396 transactions, 5,962,702 logs; 67,572 transactions selected (position change of at least $10k, or flash principal of at least $10k, or gross priced legs of at least $100k), $26.0B of largest position changes. Coverage by round: 90.45% of transactions and 92.95% of USD with the inherited 58 types; 98.55% and 99.45% after the first LLM round (71 types); 99.12% and 99.80% after the second (80); 99.88% and 99.91% after the audit round (90), with 81 transactions in 50 clusters left. `rounds.json` records each step with the hashes of the code and registry it ran.

Outputs live in `research/2026-09-05/amount_outliers_eth_day/`: `letter.md` and `report.md` are the deliverables; `qual_notes.md` holds the LLM's notes keyed by transaction hash (with `synthesis`, `feedback` and `type` sections); `classified.json`, `residue.json`, `packets.json`, `investigations.jsonl.gz`, `all_matches_by_hash.json.gz`, `types_by_hash.json.gz`, `rounds.json` and `round_0X/` are the quant artifacts; `stats.json`, `prices.json`, `native_status.json`, `context.json`, `unknown_topics.json` and `addresses.json.gz` are inputs and lookups; `txs_big.jsonl.gz` (26 MB) is the selected population with full features. The full census `txs_all.jsonl.gz` (426 MB) and the raw blocks and logs (1.0 GB) are ignored by git; the block and log hashes are in the collection manifests. All RPC use is read-only on the first local key; keys are never written to outputs.

Codex's five-hour run (`research/2026-09-05/eth_5h`, `research/2026-09-05/amount_outliers_eth_5h`) is kept as the origin of the inherited registry; its `method.md` describes the learning cycle and its `round_0X/` archives its discovery and audit rounds.


## Cross-chain vault audit (2026-09-07)

[Classify the active vaults across chains and find the bugs](research/2026-09-07/vault_audit/report.md).
`scripts/vault_audit.py` enumerates active vaults per EVM from their deposit/stake event topics, fetches each one's
bytecode (Infura, batched), resolves EIP-1967 proxies to their implementation, classifies by the implementation's
function-selector signature (CORE-fork, MasterChef, ERC-4626, Beefy, Synthetix-staking, Curve-gauge, Yearn), clusters
by normalised code hash so hundreds of instances collapse into a few dozen implementations, and red-flags each
representative's verified source. Across Ethereum, Base, BSC and Arbitrum (~650 active vaults) the population is
dominated by audited protocols (Convex, Morpho, Yearn, Aerodrome/Velodrome, Beefy, Venus, Sky, Backed); the only
reward-timing-exploitable CORE fork is StacyVault, and the notable ERC-4626 vaults all carry share-inflation protection.
The pipeline's value is triage — isolating the unaudited, red-flagged outliers from the audited bulk.

```sh
uv run --with pycryptodome python scripts/vault_audit.py --chains ethereum,base,bsc,arbitrum --blocks 30000
```

## Replicating the StacyVault flash-farm (2026-09-07)

Following the five-hour scan's finding that a bot harvests StacyVault with flash-loaned liquidity every ~30 minutes, [this study](research/2026-09-07/stacy_farm/findings.md) reads the vault's and token's verified source, explains the two flaws that make it work (rewards distributed by instantaneous stake rather than time, and a same-block guard that `depositFor` skips), and reproduces the bot in `research/2026-09-07/stacy_farm/fork/src/StacyFarmer.sol`. A Foundry fork test flash-borrows from Balancer, dominates the USDC/WETH and WBTC/WETH staking pools, triggers the reward lump with `cherryPop`, harvests it, and repays, with a net token change of dust: no capital is used, only gas. The honest economics are in the note: at STACY's current ~$0.000017 the liquid take is roughly gas-break-even, the real 79% of emissions sits in the STACY/WETH pool that needs held STACY, and the strategy is a competitive inclusion race against the incumbent.

```sh
cd research/2026-09-07/stacy_farm/fork
forge test --match-test test_farm_pools_3_and_4 --fork-url https://eth.drpc.org -vv
```

`scripts/corevault_scan.py` generalises the Stacy finding into a cross-chain hunt: it browses a chain's Blockscout by
name, fingerprints the CORE/cVault reward-timing bug in each candidate's verified source, and scores exploitability by
pool composition and reward-token value. The Ethereum sweep found 22 vaults in the family, all carrying the bypassable
`depositFor`, but none combining a flash-mintable blue-chip pool with a valuable reward token; Arbitrum had none. Details
in [other_targets.md](research/2026-09-07/stacy_farm/other_targets.md). `scripts/etherscan.py` (Etherscan V2 unified-API client, key in the gitignored
`etherscan_key.txt`) gives the scanner verified-source access on BSC, Base, Polygon and Arbitrum from one key; on-chain
reads use free public RPCs. And `scripts/bytecode_fingerprint.py` solves discovery without a name index: it
identifies a CoreVault fork from its runtime bytecode (a rare cluster of function selectors — depositFor, addPendingRewards,
setAllowanceForPoolToken, startNewEpoch, setStrategyContract…) and enumerates forks by scanning `eth_getLogs` for the
MasterChef Deposit topic and bytecode-confirming each emitter — validated at 100% precision on the saved window (12
emitters, 1 confirmed fork). Method in [fingerprint_method.md](research/2026-09-07/stacy_farm/fingerprint_method.md). `scripts/corevault_hunt.py` runs the end-to-end cross-chain hunt: the local Infura keys are enabled for
Ethereum, BSC, Base, Polygon, Arbitrum, Optimism and Avalanche, so it enumerates recent active reward vaults by their
Deposit-topic logs per chain, bytecode-filters to CoreVault forks, and scores each for a flash-mintable blue-chip pool
and a reward token with real sellable liquidity (a $25k-depth gate, so dust tokens like STACY are flagged as forks but not
suitable).

## Five hours of mainnet, digested: 2026-09-07 02:39 to 07:39 UTC

[What happened in the last five hours](research/2026-09-07/live_5h/report.md) reuses the live-scan pipeline on a five-hour window and adds two offline digests. `scripts/window_events.py` reads the ETH/USD path tick by tick from the v3 USDC/WETH pool, the per-15-minute gas, blob and fullness series, builders, transaction types (including EIP-7702), blob posters by inbox, contract creations, new pools, validator withdrawals, the largest native transfers, the highest tips and the log-heaviest transactions into `events.json`. `scripts/window_followups.py` holds the follow-up checks the narrative asked for, configured at the top of the file: gas-limit attribution per target around a spike, Uniswap v4 volume for a token set, a sybil funding check on fresh wallets, the decode of a flash-loan bot's run, an address-poisoning matcher for look-alike zero-value transactions after large transfers, mass mint and airdrop tokens, and the Spark liquidity layer's operations, into `followups.json`. The narrative (`insights.md`) found a tokenized-stock micro-trading swarm (Ondo's NVDAON, TSLAON, SPCXON, SPYON and Stockereum.fun launch tokens) that pushed the base fee up ten times for forty minutes on half a million dollars of volume, Robinhood Chain as the largest blob poster ahead of Base, Spark's liquidity layer moving $46M of USDT from SparkLend into its savings vault and doubling the SparkLend USDT rate, a $218M Aave position at health factor 1.015, a flash-loan bot farming a memecoin MasterChef with $175M of Morpho liquidity every half hour, and poisoning bots trailing every large ETH transfer.

```sh
uv run --with pycryptodome python scripts/live_collect.py collect --out research/2026-09-07/live_5h --hours 5   # ~184k credits
uv run --with pycryptodome python scripts/live_scan.py head --out research/2026-09-07/live_5h
uv run --with pycryptodome python scripts/live_scan.py analyze --out research/2026-09-07/live_5h
uv run --with pycryptodome python scripts/live_scan.py head --out research/2026-09-07/live_5h                   # second pass: fee tiers, markets, health factors
uv run --with pycryptodome python scripts/live_scan.py analyze --out research/2026-09-07/live_5h && uv run --with pycryptodome python scripts/live_scan.py render --out research/2026-09-07/live_5h
uv run python scripts/window_events.py --out research/2026-09-07/live_5h --bucket 15 --md                        # offline
uv run python scripts/window_followups.py --out research/2026-09-07/live_5h                                     # offline
```

## Live scan: a trailing hour, then the head, block by block

`scripts/live_collect.py` pulls a trailing window of full blocks and unfiltered logs up to the current head (not the finalized block) and can keep tailing it with a parent-hash recheck for reorgs; `scripts/live_rpc.py` rotates across every local Infura key and parks throttled ones. `scripts/live_scan.py` decodes value legs, swaps (Uniswap v2/v3/v4, Curve, Balancer), liquidity changes, Aave/SparkLend/Morpho events, CCTP and OFT sends, WETH, Lido and issuance events, and aggregates them into the features a patient actor can use: passive LP fee yield per pool net of just-in-time liquidity, lending rates and utilisation shocks per reserve, health factors of the borrowers active in the window, borrow and withdraw proceeds followed to exchange wallets, exchange net flow, round trips, scheduled flow, stablecoin and LST implied prices against NAV, bridge destinations and the gas market. `head` reads prices (Chainlink with description checks), NAV rates, lending reserves on Aave, SparkLend and Compound v3, Sky and Ethena rates, and health factors at the head. `midnight` checks the 23:30 to 00:20 UTC balance routine for any date with four log queries. `live` tails the chain, writes one line per block with anything notable to `live_log.md`, and re-analyses the trailing hour every ten blocks. Uniswap v4 swaps are valued only from a leg whose tokens verifiably moved through the PoolManager, because hook pools emit deltas that never settle.

```sh
uv run --with pycryptodome python scripts/live_collect.py collect --out research/2026-09-06/live --hours 1   # ~38k credits per hour of blocks
uv run --with pycryptodome python scripts/live_scan.py head --out research/2026-09-06/live                  # ~35k credits
uv run --with pycryptodome python scripts/live_scan.py analyze --out research/2026-09-06/live               # offline, ~2 s
uv run --with pycryptodome python scripts/live_scan.py head --out research/2026-09-06/live                  # second pass: fee tiers, Morpho markets, health factors
uv run --with pycryptodome python scripts/live_scan.py analyze --out research/2026-09-06/live && uv run --with pycryptodome python scripts/live_scan.py render --out research/2026-09-06/live
uv run --with pycryptodome python scripts/live_scan.py midnight --out research/2026-09-06/live --date 2026-09-06
uv run --with pycryptodome python scripts/live_scan.py live --out research/2026-09-06/live --hours 1 --every 10
uv run --with pycryptodome python scripts/live_scan.py show --out research/2026-09-06/live <tx hash>
```

Outputs live in `research/2026-09-06/live/`: `report.md` is the deliverable (the LLM's `insights.md` followed by the deterministic tables and the live log); `analysis.json`, `head_state.json`, `pools.json`, `markets.json` and `midnight_<date>.json` are the quant artifacts. The raw blocks and logs (about 41 MB per hour) and the logs of the collectors are ignored by git. The first hour (2026-09-06 10:06 to 11:06 UTC) confirmed that the midnight Aave/PSM balance routine is daily, found a bot cycling about $3.5B of fee-free flash liquidity thirty times an hour for about $760 a run, and measured the cross-venue stablecoin rate dispersion; the narrative and the requests to the quant step are in `insights.md`.

## Completed five-hour Ethereum mainnet study

The [five-hour research memo](research/2026-09-05/amount_outliers_eth_5h/letter.md) covers 5 September 2026, 11:22:48–16:22:48 UTC: 392,428 transactions, 10,170 amount candidates, 54 observed primary categories, and 90.07% rule coverage. Twelve rules were learned through qualitative investigation. The [full report](research/2026-09-05/amount_outliers_eth_5h/report.md), [notes](research/2026-09-05/amount_outliers_eth_5h/qual_notes.md) and [validation](research/2026-09-05/amount_outliers_eth_5h/validation.json) retain evidence and uncertainty.

The final [frozen replay](research/2026-09-05/amount_outliers_eth_5h/replay/README.md) preserves this study independently of the separate day-long work in `scripts/`. Its defaults use the five-hour data and disable implied prices. From the repository root:

```sh
uv run python research/2026-09-05/amount_outliers_eth_5h/replay/tx_types.py scan
uv run python research/2026-09-05/amount_outliers_eth_5h/replay/tx_types.py classify --audit-known --label 'five-hour replay'
uv run python research/2026-09-05/amount_outliers_eth_5h/replay/tx_types.py render
uv run python research/2026-09-05/amount_outliers_eth_5h/replay/validate.py
```

Known rules investigate every selected occurrence; unresolved clusters produce LLM evidence packets. The LLM review is performed separately and its learned rules are retained. Coverage measures rule matches, not verified economic intent or classifier accuracy. Earlier rounds document discovery; round 7 records the completed feature scan and the final signed-account interpretation.
