# Building the best onchain research analysis system — roadmap

This is the standing plan for `llm-quant`. The goal (see the research memo and memory) is a closed qual↔quant loop:
the LLM reads evidence, proposes mechanisms, and writes the infrastructure; deterministic code turns mechanisms into
reusable detectors and tests; the human steers. The metric we optimise is **time-to-verified-insight**: how fast a raw
signal becomes a true, capacity-aware, reproducible claim and then a reusable detector — not classification coverage.

## Where we are

Strengths, honestly: a clean separation of a deterministic feature layer from an LLM narrative (`analysis.json` +
tables vs `insights.md`); growing registries (`type_registry.py`, 90 types); a fork-proof habit (CooldownArb,
captive-flow LP, StacyFarmer) that turns a thesis into an executable, checkable artifact; per-round reproducibility in
`tx_types.py` (`rounds.json`). Collectors (`eth_day_collect`, `live_collect`), a broad feature engine (`live_scan`),
and offline digests (`window_events`, `window_followups`, `corevault_scan`).

Weaknesses, from this session's actual friction: labels are behavioural/memory and **wrong in ways that move headline
numbers** (CoW settlement counted as a CEX inflated leverage-to-exchange from $5.3M to $25.7M; an RLUSD treasury
inflated exchange outflow 100x); head reads are **spot and pollutable** by the same flash/midnight spikes the system
itself documents; there is **no automated verification** of a claim (every mechanism this session — the Morpho farmer,
the Stacy bug — was hand-verified from traces/source); one-off scripts don't become **reusable detectors**; data access
is fragile (Infura archive gaps, dRPC free-tier timeouts, Blockscout rate limits, forks only at latest, BSC/Polygon
need keys); and opportunity economics (capacity, gas, competition) are recomputed by hand each time, so a dust farm
like Stacy isn't auto-flagged.

## Recommendations, prioritised

Each: **problem observed → proposal → interface → effort → payoff.**

### P0 — correctness (do first; wrong numbers poison everything downstream)

**1. Verified, provenance-tracked labels registry.** *Started this session.*
Problem: `load_address_book` derives hot-wallet/deposit-sink tags from behaviour + memory; a settlement contract or a
token treasury reads as a CEX. Proposal: `scripts/address_labels.json` (done) with `{label, kind, source}` where `kind`
∈ {exchange, exchange_deposit, protocol, venue, vault, bridge, issuer, treasury, token, mev_bot}; `live_scan` counts
only exchange kinds as exchange flow and never chases borrowed funds through a labelled venue. Next: a `scripts/labels.py`
that fetches Blockscout verified names and known-canonical sets (routers, settlement, CCTP/OFT, bridge inboxes) on
demand and writes provenance, plus a coverage report (what fraction of window USD flows through labelled vs unlabelled
addresses). Effort: S (seed+wiring done), M (fetcher). Payoff: **demonstrated** — leverage-to-exchange corrected
$25.7M → $5.3M, RLUSD net −$101.6M → −$0.9M, on the 2026-09-07 window with no other change.

**2. Time-weight and de-spike every head read.**
Problem: the midnight Aave routine and flash bots spike `currentVariableBorrowRate`/reserves 3–10x for a single block;
`head` reads spot, so any rate the narrative quotes can be a one-block artifact. Proposal: read reserves/rates as the
median over the last K blocks (the raw window already has the series), and flag any single-block read that coincides
with a same-block flash loan or a >$10M same-reserve flow. Interface: `head_state.json` gains `{spot, twap_k, spiked}`
per reserve; the tables show TWAP and mark spikes. Effort: M. Payoff: removes a whole class of false rate findings.

**3. A findings-verification pass (adversarial verify).**
Problem: headline numbers carry my confidence label but nothing re-derives them; mechanism claims are trusted prose.
Proposal: every headline number carries a machine-checkable recipe (a small closure: raw inputs → value) and a `verify`
step recomputes it from raw and fails loudly on drift; for a mechanism claim, `verify` pulls one `debug_traceTransaction`
or the verified source and asserts the *specific* fact (e.g. "depositFor does not set lastDepositBlock", "the $759 comes
from the Balancer leg"). This is the code-review "confirm each finding by re-deriving it" pattern applied to research.
Interface: `insights.md` claims tagged `[[verify: recipe-id]]`; `live_scan verify` emits a pass/fail table appended to
the report. Effort: M–L. Payoff: **the single biggest quality lever** — it makes the confidence labels earned, not asserted.

### P1 — leverage (build the flywheel that compounds)

**4. Detector registry.** *First detector landed: `scripts/bytecode_fingerprint.py`.*
A source-free bytecode fingerprint (selector cluster + non-standard event topic + normalised code hash) that identifies and
enumerates CoreVault forks on any chain — the template for detectors that run every window and grow like the type registry.
Problem: the JIT test, the midnight routine, the poisoning matcher, the gas-hog attribution, `corevault_scan`, the
leverage pipeline are one-off code, not reusable detectors. Proposal: `scripts/detectors/` where each detector is a
module exposing `scan(window) -> [hit]` with `{severity, evidence, economics_ref}`; `live_scan` runs the whole set every
window and the registry grows the way `type_registry` did. New mechanisms discovered by the LLM become detectors, not
prose. Effort: L. Payoff: every window automatically re-checks every past discovery; the system stops forgetting.

**5. Standard economics harness.**
Problem: capacity, gas, capital, competition and decay are computed by hand for each opportunity, so results aren't
comparable and dust isn't auto-flagged (Stacy looked mechanically live but is gas-break-even). Proposal: `scripts/economics.py`
— given a strategy's legs `{size, price_impact_curve, gas_units, capital_locked, competitors, decay_per_run}` it returns
capacity-adjusted net APR, break-even size, and a go/no-go. Every opportunity (rate dispersion, redemption arb, captive
LP, reward-timing harvest) reports through it. Effort: M. Payoff: honest, comparable rankings; the loop stops chasing dust.

**6. Data-access layer with a capability map and cache.** *Started this session (`scripts/etherscan.py`).*
An Etherscan V2 client now fetches verified source across chains from one key (BSC/Base/Polygon/Arbitrum/Ethereum), with
a per-chain public-RPC map for reads, and it already encodes a capability nuance the layer must generalise: the free tier
serves `getsourcecode` everywhere but gates `account`/`proxy`/`logs` to a few chains. Extend it into the full layer.
Problem: this session hit Infura archive gaps, dRPC free-tier timeouts on historical state, Blockscout proxy rate limits,
forks that only work at latest, and BSC/Polygon behind keys. Proposal: `scripts/rpc.py` unifying Infura + dRPC + public
endpoints with a per-chain capability table (which endpoint serves archive / trace / getLogs / at-block state), automatic
fallback, and an on-disk cache of fetched sources, labels and eth_calls. The **#1 missing capability is a trace+archive
endpoint** — it blocked bot balance-deltas and historical-block forks all session. Effort: M–L. Payoff: fork tests at any
block, trace-backed verification, fewer dead ends.

### P2 — breadth and rigour

**7. Multi-chain abstraction.** *Started (`corevault_scan` `CHAINS` presets).*
Problem: the deep tooling is Ethereum-only; the fresh forks (VCORE's `$AAPL` pool, Arbitrum candidates) are cross-chain,
and BSC is the historical home of the CORE family. Proposal: promote the `CHAINS` preset pattern into the collectors and
`live_scan` (per-chain blue-chip sets, factories, blob inboxes, RPC). Effort: L. Payoff: the meme waves that spawn these
setups are multi-chain; single-chain coverage misses most of them.

**8. Findings ledger with recheck cadence.**
Problem: findings are point-in-time; only the midnight routine is tracked daily. Proposal: `research/findings.jsonl`, each
finding an id + a recheck cron + a realized-vs-predicted log; a daily job re-runs the relevant detector and appends the
outcome. Effort: M. Payoff: closes the qual↔quant loop the memo describes and separates recurring edges from one-offs.

**9. Signal-testing harness with controls and multiple-hypothesis correction.**
Problem: the informed-flow test (does exchange netflow predict returns) was run once, ad hoc, and found null. Proposal:
generalise the hash-sampled controls already in `amount_outliers`, require out-of-sample and FDR control before any
"signal" is reported. Effort: M. Payoff: stops the loop from over-fitting a five-hour window.

**10. Reproducibility manifests everywhere.**
Problem: some follow-up scripts are path-hardcoded. Proposal: every artifact carries `{code_sha, registry_sha, block_range,
price_basis}` the way `tx_types` `rounds.json` already does. Effort: S per script. Payoff: any report is replayable and
diffable.

## Do next (concrete)

1. Finish the labels registry: `scripts/labels.py` (Blockscout fetch + known-canonical + coverage report), and add the
   Stockereum routers / FeeEscrow and provenance for the memory-only CEX labels.
2. Add `verify` to `live_scan` for the five headline numbers (leverage-to-exchange, exchange netflow, top rate dispersion,
   the biggest NAV discount, the gas-spike cause) and one trace-backed mechanism check.
3. Refactor `window_followups` checks and `corevault_scan` into the first three `detectors/` modules and route their
   opportunities through `economics.py`.

## Anti-goals

Read-only research, no execution service — the fork proofs stay proofs. Exact numbers live in code; prose only interprets,
with stated confidence that `verify` has to earn. Coverage % is a diagnostic, not the goal; the goal is verified,
capacity-aware insight that compounds into detectors.
