# Onchain research pilot

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
