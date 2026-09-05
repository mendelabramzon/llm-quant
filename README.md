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
