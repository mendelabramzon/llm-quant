# Onchain research pilot

**System roadmap:** [ROADMAP.md](ROADMAP.md) is the standing plan for turning this into the best onchain research
analysis system — prioritised recommendations, each grounded in a concrete failure this repo has hit. Seven of them have
now landed, and together they form a correctness layer that runs on every window:

| module | what it does | run it |
|---|---|---|
| `scripts/labels.py` | address labels with five provenance tiers, a proxy-following resolver, a coverage report, an audit, and `adopt-shapes` to file what a detector proved about the unlabelled tail | `labels.py audit --book` |
| `scripts/provenance.py` | records the labels, token table and block set an artifact was built from, and gates on them | `provenance.py check --out <window>` |
| `scripts/verify.py` | re-derives 13 headline numbers from the raw blocks through an independent path, asserts four mechanism claims against verified source and the chain, reports the label band, and checks that every prose claim cites a recipe | `live_scan.py verify --out <window>` |
| `scripts/economics.py` | one scorer for every opportunity: capacity, price impact, gas, locked capital, competition, decay | `economics.py` |
| `scripts/detectors/` | seven detectors, so each discovered mechanism is re-checked automatically forever | `live_scan.py detect --out <window>` |
| `scripts/findings.py` | the ledger: which findings recur, which decayed, which are due a re-check | `findings.py report` |
| `scripts/window_raw.py` | the minimal independent reader the verification is built on | — |

`live_scan.py pipeline --out <window>` runs analyze → verify → detect → ingest in that order, because that is the order
in which they depend on each other and running them out of order is how this repo produced corrected labels beside
uncorrected numbers, twice.

Why this exists, concretely. Exchange flow and leverage-to-exchange are computed from an address book, and a wrong
entry moves those headlines by multiples rather than percents. Four such entries have now been found:

| mislabel | headline it moved | found by |
|---|---|---|
| CoW settlement contract read as a CEX | leverage-to-exchange $25.7M → $5.3M | hand |
| an RLUSD treasury read as a CEX | RLUSD net flow −$101.6M → −$0.9M | hand |
| `sent == 0` deposit-sink rule (every contract satisfies it) | gross USDC inflow $823.2M → $497.1M | hand |
| a pass-through EOA tagged `exchange_deposit` | five-hour net stable flow −$24.8M → **+$75.2M** | `mislabelled_flow` detector |

The fourth is the one that matters for the system rather than the number. It was found automatically, on the second
window it appeared in, by the detector written to test labels against the window's own behaviour — and the ledger had
already recorded that it recurred. The address collects small inbound legs and forwards them in one large one: $99.99M
of USDC in a single transaction, to a verified Gnosis Safe. Counting that as exchange outflow is wrong under either
reading of the address, so the tag was retired without having to settle its identity.

The label band is the honest by-product, and it improved too. On the five-hour window net stable exchange flow read
+$91.6M with model-memory labels alone and −$24.8M once behavioural labels were included — a sign flip that turned out
to be measuring that single bad label. Corrected, the band runs +$91.6M to +$75.2M and no longer changes sign.

Two detectors earned their place the same way. The generalised gas detector rediscovered the tokenized-stock router
behind that window's 15x base-fee spike without being given its address; `mass_distribution` surfaced 0.0003 USDT sent
to 12,056 addresses in one campaign — token-transfer address poisoning at a scale the native-ETH poisoning detector
cannot see, and which the hand analysis of the same window missed.


2026-09-07, joining the day's per-chain windows: [three chains, one desk](research/2026-09-07/interchain/findings.md). The same wallet is the entire withdrawal side of Relay's depository on Ethereum *and* Robinhood Chain, a Paxos mint-and-redeem counterparty on both, and the top taker in the thin Uniswap v4 USDC/USDG pools that the captive-flow LP study is built on — so that flow is a cross-chain solver's inventory balancing, not a reward-rebate programme, and the risk it prices as future ("the desk might reroute to direct mint") is already its base case. The same network is the largest retail flow on all three chains, and the "unlabelled custodial deposit system" the Solana narrative asked to identify is its Solana depository. Robinhood Chain collected 279.2 ETH ($696k) of base fees in the ten hours Ethereum L1 burned 8.96 ETH ($22.3k), a 31x ratio, and charged nothing on 175,818 priority-fee bids. Two headline numbers do not survive re-derivation: TSLA on Robinhood Chain traded within 0.10% of its reference, not +4.4% (a `setdefault` merge in `orbit_scan.py` freezes a stale first-pass price), and the Solana narrative's "USDG 8.32% on Jupiter Lend" contradicts its own table's 5.42%. Robinhood Chain's missing rate rung is measured for the first time by realising share prices forward: $456M sits in steakUSDG earning 3.75%, below Compound v3 USDC at 6.91% on Ethereum and Jupiter Lend USDC at 4.96% on Solana. `scripts/interchain.py` recomputes every join offline.

2026-09-07, first window on another chain: [ten hours of Robinhood Chain](research/2026-09-07/robinhood_10h/report.md) (Arbitrum Orbit L2, chain id 4663, 04:06–14:06 UTC, 356,874 blocks, 3.23M user transactions). The chain earns ~$0.7M of base fees per ten hours against $62 of Ethereum blob and execution cost, with L1 pricing switched off and priority-fee bids ignored; the demand is a fleet of 31 Relay solver wallets (a fifth of all gas), an unverified 1%-fee memecoin router (11% of transactions, ~$430k of fees collected for its owner), ERC-4337 bundlers, Axiom, OKX, Kyber and Uniswap routers, and MEV bots whose reverts make up 9% of transactions. Tokenized stocks moved ~$268M in 1.46M transfers with zero mints or burns, three quarters of them through Uniswap pools, and their on-chain prices track their references within 0.2% (the TSLA premium originally reported here was a price-merge artifact, corrected in the interchain study above). New generic tooling: `scripts/orbit_collect.py` (batched blocks + receipts for any Nitro chain, reduced on the fly to compact chunks), `scripts/orbit_scan.py` (streaming analysis with pool-key resolution), `scripts/orbit_followups.py`; method and endpoint notes in `method.md`.

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

## Solana: the same live-scan loop on a second chain

2026-09-07: the trailing-window scan was ported to Solana mainnet (`research/2026-09-07/solana_live/`, deliverable `report.md`).
Data comes over the local GetBlock tokens (`getblock_keys.json`, gitignored; `scripts/solana_rpc.py` round-robins EU and US
hosts, needs a browser-like User-Agent on the US host, retries the frequent `IncompleteRead`s — the observed cap from this
machine is ~2.7 MB/s on the wire whatever the concurrency, i.e. ~1.9 blocks/s, so one hour of chain (~11,350 produced blocks,
~8.5 GB compact) takes ~100 minutes to collect). `scripts/solana_collect.py collect --hours N` pins the window (binary search on
`getBlockTime`, `getBlocks`, `getSlotLeaders`), stores every produced block with vote transactions dropped and logs reduced
(`Program data:`/`Program log:`/`Program return:`/error/consumed lines only), and `verify` checks parent links and file hashes.
`scripts/solana_decode.py` is a pure-python base58 + System/SPL Token/Token-2022/Compute Budget/CCTP decoder validated with
zero mismatches against the RPC's own `jsonParsed` output for the same block (`validate`). `scripts/solana_labels.json` is the
provenance-tracked label registry (Jupiter's DEX program list, canonical programs, memory-sourced CEX wallets that the scan
checks behaviourally by fan-in, and window-derived labels for bot programs and cluster hubs).

```sh
uv run python scripts/solana_collect.py collect --out research/2026-09-07/solana_live --hours 1 --workers 8
uv run python scripts/solana_collect.py verify  --out research/2026-09-07/solana_live
uv run python scripts/solana_scan.py head    --out research/2026-09-07/solana_live   # Jupiter prices, Kamino/Save/Jupiter Lend rates, Sanctum LST NAV, Jito tip floor, epoch
uv run python scripts/solana_scan.py prices  --out research/2026-09-07/solana_live   # SOL/USD path from in-window SOL<->USDC/USDT swaps, every 10th block
uv run python scripts/solana_scan.py analyze --out research/2026-09-07/solana_live   # offline, ~12 min for one hour
uv run python scripts/solana_scan.py render  --out research/2026-09-07/solana_live   # insights.md + tables -> report.md
uv run python scripts/solana_scan.py show <signature>                                # decoded instructions, balances, logs from the local blocks
uv run python scripts/solana_followups.py profile|program|token|cluster --out ...     # address profiles, program shape, token tape, sybil-funding check
```

What `analyze` computes (all from the saved blocks; USD basis = stables at par, SOL from the in-window swap path, registry
tokens from the Jupiter head read, everything else priced only through the opposite leg of a swap): throughput, vote/non-vote
and failed shares, base vs priority fees, Jito tips by tip account and tipper, compute-unit prices, leaders and skipped slots;
programs with the bot-shape columns (unique payers, top-payer share, share of txs that move any token, average CU and
accounts, durable-nonce use); payer-centric transaction kinds; DEX volume by venue and pair, implied prices, largest swaps,
same-block sandwich patterns with a position-closure test, token launches by launchpad; lending events by instruction
discriminator (Kamino, marginfi, Save) with liquidation attempts and flash-loan payers; stablecoin and LST mints/burns split
between issuer and CCTP; CCTP in/out by domain (v2 pays receivers from a custody account rather than minting); exchange net
flow with a fan-in label check; fan-in/fan-out hubs (collector hubs, deposit addresses, distributors); largest position changes;
address-poisoning dust senders.

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

## Ten hours across midnight: the routine, traced (2026-09-08)

[Ten hours of Ethereum, and the thirty-four minutes that mattered](research/2026-09-08/live_10h/report.md)
(2026-09-07 22:26 -> 2026-09-08 08:26 UTC; 2,993 blocks, 675,675 transactions, 2,371,958 logs; `verify` green).

Ten hours of mainnet is, on almost every measure, ten hours of nothing: ETH moved 1.7%, $250.0M of DEX volume,
**one liquidation for one dollar of debt**, and block fullness between 49.8% and 52.0% in every half-hour bucket.
Two things happened anyway.

**The nightly balance routine, traced end to end for the first time.** Prior windows had recorded by hand that Aave's
USDC reserve went to 100% utilisation for about half an hour around 23:41 UTC. This session turned that sentence into
`detectors/liquidity_blackout.py` -- it inverts each reserve's published borrow rate through its own IRM to recover the
utilisation the pool was priced at, and reports collapses of withdrawable liquidity **with the clock time they happen**.
It fired on the first window that could contain one: *Aave v3 USDC closed its exit at 23:47 UTC for 22 minutes, $55.4k
withdrawable on a $2.3B reserve at 99.9976% utilisation.* Following it through the window's own transfers gives the
whole mechanism: at 23:35:47 one EOA redeems $245,571,215 of sUSDS into USDC through Sky's PSM plumbing; at 23:37:47 a
second withdraws **$151,780,227 from Aave -- 100.16% of that reserve's free liquidity**; both send to one hub, which
forwards **$397,310,079** to a third address at 23:41:23 and takes it back at 00:03:59; every leg reverses to the dollar
by 00:09:35. Nothing is traded and nothing earned. The routine costs its operator about **$900** in forgone yield and
imposes **$8,879** of extra interest on Aave's USDC borrowers while a $2.31B exit is shut.

**The fee-market result was not an artifact of a quiet hour.** Over ten hours Ethereum burned **$11,334** and users paid
**$75,713** to block builders -- a **6.68x** ratio against 6.92x on the one-hour window, never below 4.4x in any
half-hour bucket. 54.3% of gas paid a tip at or under 0.01 gwei, and 17.6% went to four unverified batch contracts (the
largest a **XEN** minter) that paid $9 between them. `fee_census.py --every N` makes a ten-hour census cost 753k credits
instead of 3M by regular subsample; rates and ratios need no scaling and totals are labelled as sampled.

## Ten chains at once: the cross-chain dollar surface (2026-09-08)

[One hour, ten chains: the dollar is one asset with ten prices, and nobody is arbitraging it](research/2026-09-08/multi_1h/report.md)
(06:23-07:29 UTC). `scripts/multichain.py` is a logs-first trailing-window scanner for every EVM the local keys reach
(Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, BSC, Unichain, Linea, Scroll). It is **discovery-first**:
no pool, bridge or token address is asserted. Lending markets are found by scanning the chain for one topic
(`ReserveDataUpdated`), so every Aave-v3-family deployment announces itself and hands back its full intra-hour rate
path in the same query; CCTP is found by its own topics and each emitter is then asked on-chain for its Circle domain
(`localMessageTransmitter()` -> `localDomain()`), so the chain-to-domain map is verified rather than recalled, and
USDC's address on each chain falls out of the indexed `burnToken`.

```sh
uv run --with pycryptodome python scripts/multichain.py collect  --out research/2026-09-08/multi_1h --hours 1   # ~90k credits
uv run --with pycryptodome python scripts/multichain.py head     --out research/2026-09-08/multi_1h             # ~200k credits
uv run --with pycryptodome python scripts/multichain.py issuance --out research/2026-09-08/multi_1h
uv run --with pycryptodome python scripts/multichain.py analyze  --out research/2026-09-08/multi_1h --benchmark-head research/2026-09-08/live_1h_b/head_state.json
uv run --with pycryptodome python scripts/multichain.py verify   --out research/2026-09-08/multi_1h
uv run --with pycryptodome python scripts/multichain.py render   --out research/2026-09-08/multi_1h
```

**The finding.** USDC pays 4.00% on Base and 0.36% on Scroll at the same instant, a 3.64-percentage-point spread on
$2.78B. It is worth **$177,794 a year**. Capacity is `min(high-side dilution, low-side withdrawable liquidity)` and for
seven of twenty switches the second one binds -- Optimism's USDC reserve pays 2.56% on $11.3M of which $2.3M can be
withdrawn. Filling each destination once, cheapest source first, the whole $8.73B cross-chain dollar complex absorbs
**$37.3M for 48 basis points**. And CCTP does not close it: net flow correlates **-0.57** with the rate, because the
addresses on both ends of the bridge are solvers rebalancing inventory toward demand, not capital chasing yield.

**`scripts/fee_census.py`** answers the question the trailing hour raised: with the L1 base fee at 0.049 gwei and blocks
50.6% full, the chain burned 0.44 ETH ($1,098) in an hour while users paid 3.07 ETH ($7,598) in priority fees -- a
**6.92x ratio**. 35.6% of all gas paid exactly zero tip, and the largest single consumer of Ethereum blockspace was
**XEN** batch-minting at 8.2% of the chain-hour for $2 of tips. `economics.py` charges gas at the base fee, which
understates an inclusion-sensitive leg by about sevenfold in this regime.

**And the machinery caught its own errors, which is the other half.** `aToken.totalSupply()` is *not* the denominator
Aave prices with: Ethereum and Base reproduce their published borrow rate from it, Avalanche reproduces it from
`getVirtualUnderlyingBalance()` plus debt, and on Avalanche's GHO reserve the 0.46pp difference straddles the 90% kink
and is worth **151 basis points of borrow rate**. Utilisation is now inverted from the pool's own published rate, which
is version-independent by construction. Three more: a reserve factor of 1.0 is a mint facility rather than a supply
market (Aave's $135M Ethereum GHO reserve, which produced the largest fake switch on the first pass); a flat IRM cannot
be inverted; and two different tokens on Arbitrum both answer `symbol()` with "USDC".

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
