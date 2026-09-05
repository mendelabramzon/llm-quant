# Onchain research pilot

The latest study is [one day of Ethereum amount outliers, typed](research/2026-09-05/amount_outliers_eth_day/letter.md), with a [detailed report](research/2026-09-05/amount_outliers_eth_day/report.md) and the [LLM's notes](research/2026-09-05/amount_outliers_eth_day/qual_notes.md). It is Ethereum mainnet only, 24 hours (2026-09-04 14:00 to 2026-09-05 14:00 UTC). Known transaction types run deterministic investigations; unresolved clusters become LLM evidence packets, and investigated mechanisms become persistent rules in `scripts/type_registry.py`. Classification coverage is reported separately from the strength of the economic interpretation. The registry was grown in two sessions: Codex on a five-hour window (`research/2026-09-05/amount_outliers_eth_5h`, method in its `method.md`; its notes and report were not written before that session ended) and Claude on the full day, which replayed Codex's 58 types as round 1 and added 32 more over three rounds, the last of them an audit of one sampled occurrence per known type.

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

Codex's five-hour run (`research/2026-09-05/eth_5h`, `research/2026-09-05/amount_outliers_eth_5h`) is kept as the origin of the inherited registry; its `method.md` describes the learning cycle and its `round_0X/` archives the registry after each of its four rounds.
