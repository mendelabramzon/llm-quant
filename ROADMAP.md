# Building the best onchain research analysis system — roadmap

This is the standing plan for `llm-quant`. The goal (see the research memo and memory) is a closed qual↔quant loop:
the LLM reads evidence, proposes mechanisms, and writes the infrastructure; deterministic code turns mechanisms into
reusable detectors and tests; the human steers. The metric we optimise is **time-to-verified-insight**: how fast a raw
signal becomes a true, capacity-aware, reproducible claim and then a reusable detector — not classification coverage.

## Session log — 2026-09-07 (infrastructure pass)

Landed: `scripts/window_raw.py` (an independent raw-window reader), `scripts/labels.py` (provenance registry, coverage,
resolver, audit), `scripts/verify.py` (13 numeric re-derivations + source-backed mechanism assertions + a label band),
`scripts/economics.py` (capacity/gas/competition/decay scorer, 24 unit tests), `scripts/detectors/` (registry + four
detectors), and `live_scan verify` / `live_scan detect`.

What it found, which is the point: the deposit-sink heuristic in `load_address_book` tested `sent == 0`, meaning
"originated no transactions" — a condition every *contract* meets structurally. The rule was therefore "any busy
contract is an exchange deposit sink", and it tagged 25 addresses of which 22 forwarded value, including the CoW
settlement contract, the Uniswap Universal Router and a Relay bridge depository. Their inflow counted as exchange flow
and their receipt of borrow proceeds as leverage-to-exchange. Corrected to test forwarding directly, on the 2026-09-07
midday window with nothing else changed:

| headline | before | after |
|---|---:|---:|
| exchange gross inflow, USDC | $823.2M | $497.1M |
| exchange net flow, stables | +$44.0M | +$13.2M |
| exchange net flow, ETH | −$17.4M | −$19.6M |
| leverage-to-exchange | $4.0M | $0 |

The verify pass then earned its keep a second time within the hour. A parallel study reclassified the wallet this repo
called an "exchange hot wallet with USDG desk" as the Relay solver it turned out to be, and `verify` failed immediately
on the two windows because their `analysis.json` predated that label. That is the intended behaviour: a stale analysis
against a changed registry is drift, and it now announces itself instead of sitting in a report.

And the label band on the five-hour window shows why provenance had to be explicit: net stable flow is **+$91.6M** using
model-memory labels alone and **−$24.8M** once behavioural labels are included. The sign of a headline depends on which
unverified labels you trust, so `verify` now reports the band rather than one number.

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

**1. Verified, provenance-tracked labels registry.** *Done — `scripts/labels.py`.*
Problem: `load_address_book` derives hot-wallet/deposit-sink tags from behaviour + memory; a settlement contract or a
token treasury reads as a CEX. Proposal: `scripts/address_labels.json` (done) with `{label, kind, source}` where `kind`
∈ {exchange, exchange_deposit, protocol, venue, vault, bridge, issuer, treasury, token, mev_bot}; `live_scan` counts
only exchange kinds as exchange flow and never chases borrowed funds through a labelled venue. Next: a `scripts/labels.py`
that fetches Blockscout verified names and known-canonical sets (routers, settlement, CCTP/OFT, bridge inboxes) on
demand and writes provenance, plus a coverage report (what fraction of window USD flows through labelled vs unlabelled
addresses). Effort: S (seed+wiring done), M (fetcher). Payoff: **demonstrated** — leverage-to-exchange corrected
$25.7M → $5.3M, RLUSD net −$101.6M → −$0.9M, on the 2026-09-07 window with no other change.

**2. Time-weight and de-spike every head read.** *Partly done — inside `detectors/rate_dispersion.py`.*
Problem: the midnight Aave routine and flash bots spike `currentVariableBorrowRate`/reserves 3–10x for a single block;
`head` reads spot, so any rate the narrative quotes can be a one-block artifact. Proposal: read reserves/rates as the
median over the last K blocks (the raw window already has the series), and flag any single-block read that coincides
with a same-block flash loan or a >$10M same-reserve flow. Interface: `head_state.json` gains `{spot, twap_k, spiked}`
per reserve; the tables show TWAP and mark spikes. **Shipped** where it decides something: the rate detector quotes the
median of the window's `ReserveDataUpdated` series and demotes any gap it could not de-spike to `info`. That correctly
demoted the SparkLend USDT 3.05pp gap — the ALM shock that normalised within the hour — below the Compound USDC gap that
held all window. *Still open*: `head_state.json` itself still stores spot values, and Compound and Sky emit no
comparable logs, so their reads cannot be de-spiked at all. Effort: M. Payoff: removes a whole class of false rate findings.

**3. A findings-verification pass (adversarial verify).** *Done — `scripts/verify.py`.*
Problem: headline numbers carry my confidence label but nothing re-derives them; mechanism claims are trusted prose.
Proposal: every headline number carries a machine-checkable recipe (a small closure: raw inputs → value) and a `verify`
step recomputes it from raw and fails loudly on drift; for a mechanism claim, `verify` pulls one `debug_traceTransaction`
or the verified source and asserts the *specific* fact (e.g. "depositFor does not set lastDepositBlock", "the $759 comes
from the Balancer leg"). This is the code-review "confirm each finding by re-deriving it" pattern applied to research.
Interface: `live_scan verify --out <window>` prints a pass/fail table and writes `verify.json`; exit code is non-zero on
any failure. **Shipped**: 13 numeric checks re-derived through `window_raw` (blocks, transactions, logs, USDC mint and
burn, exchange net flow for stables and ETH, gross USDC inflow, leverage-to-exchange, the largest CCTP send, top gas
target and its gas, the widest borrow-rate gap), all passing on both 2026-09-07 windows in about 8 seconds; three
source-backed mechanism assertions (`stacy-deposit-for` fetches the verified source and asserts `depositFor` does not
write `lastDepositBlock`; `msca-not-exchange`; `no-contract-hot-wallets`); and the label-provenance band.

Writing it caught two decoder bugs immediately: only the CCTP **v1** `DepositForBurn` topic was being watched, so every
v2 send was silently dropped, and the destination domain was being sniffed rather than read from its fixed word.
*Still open*: `insights.md` claims are not yet tagged with recipe ids, so the link from a sentence to its check is by
convention rather than by reference. Effort: M–L. Payoff: **the single biggest quality lever** — it makes the confidence
labels earned, not asserted.

### P1 — leverage (build the flywheel that compounds)

**4. Detector registry.** *Done — `scripts/detectors/`.*
A source-free bytecode fingerprint (selector cluster + non-standard event topic + normalised code hash) that identifies and
enumerates CoreVault forks on any chain — the template for detectors that run every window and grow like the type registry.
Problem: the JIT test, the midnight routine, the poisoning matcher, the gas-hog attribution, `corevault_scan`, the
leverage pipeline are one-off code, not reusable detectors. Proposal: `scripts/detectors/` where each detector is a
module exposing `scan(window) -> [hit]` with `{severity, evidence, economics_ref}`; `live_scan` runs the whole set every
window and the registry grows the way `type_registry` did. **Shipped**: `detectors/__init__.py` holds the registry, a
`Hit` type and a shared `Context` that materialises the block and transfer streams once; `run.py` sweeps a window and
writes `detectors.json` + `detectors.md`. Four detectors so far — `mislabelled_flow` (label claims the window itself
refutes), `gas_concentration` (base-fee spikes attributed to the contract whose gas demand caused them),
`rate_dispersion` (de-spiked cross-venue gaps priced through `economics.py`), `address_poisoning` (lookalike dust after
a large transfer). The generalised gas detector **rediscovered the tokenized-stock router** on the five-hour window
without being given its address, which is the flywheel doing what it was built for. Effort: L.
Payoff: every window automatically re-checks every past discovery; the system stops forgetting.

**5. Standard economics harness.** *Done — `scripts/economics.py`.*
Problem: capacity, gas, capital, competition and decay are computed by hand for each opportunity, so results aren't
comparable and dust isn't auto-flagged (Stacy looked mechanically live but is gas-break-even). Proposal: `scripts/economics.py`
— given a strategy's legs `{size, price_impact_curve, gas_units, capital_locked, competitors, decay_per_run}` it returns
capacity-adjusted net APR, break-even size, and a go/no-go. **Shipped**, with four modelling distinctions that each
changed an answer: a flat per-run reward (`edge_usd`) is not bps on notional, so the StacyVault harvest prices at $7.42
a run and is auto-flagged as dust; a *race* pays gas on losing attempts while a held position does not; break-even is
searched below the optimum because impact makes net non-monotonic in size; and a stable pool takes an `amplification`
so a Curve leg is not charged constant-product impact. All four known opportunities now rank in one table, and
`rate_dispersion` reports through it with a dilution curve derived from the pool's own size. Effort: M.
Payoff: honest, comparable rankings; the loop stops chasing dust.

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

**7. Multi-chain abstraction.** *Started (`corevault_scan` `CHAINS` presets); Solana port landed 2026-09-07.*
The Solana port (`solana_rpc` / `solana_collect` / `solana_decode` / `solana_scan` / `solana_followups`, label registry
`solana_labels.json`) reproduces the live-scan deliverable on a non-EVM chain with the same contract: deterministic
`analysis.json` + tables, LLM `insights.md`, `verify` re-deriving the headline numbers. What it taught: the "interesting
things" lens must be chain-specific (payer-centric kinds, per-program bot-shape columns, fan-in/fan-out hubs) while the
deliverable shape stays identical; the data-access layer (item 6) must carry per-provider bandwidth caps (GetBlock ~2.7 MB/s
from this machine) as well as method capabilities.
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

The previous three items are done. What this pass exposed, in priority order:

1. **Make the staleness check automatic.** Both 2026-09-07 windows were re-analysed and their notes corrected by hand
   this session. Nothing yet stops the next one drifting: `analysis.json` should record the registry hash it was built
   against, and `verify` should fail on a mismatch before it compares a single number, rather than reporting a numeric
   mismatch whose real cause is a label edit.
2. **Tag claims with verify recipes.** Give each headline in `insights.md` a `[[verify: <id>]]` marker matching a check
   in `verify.py`, so a reader can go from a sentence to the code that re-derives it, and an untagged number is visibly
   unverified.
3. **Port the remaining one-off checks into detectors**: `corevault_scan` / `bytecode_fingerprint` (needs the RPC layer,
   item 6), the JIT-liquidity test, the midnight routine, and the mass-distribution matcher from `window_followups`.
4. **Label the $2B tail.** The top unlabelled addresses are unverified contracts; a vanity-prefix + unverified + high
   fan-out signature is a solver/MEV fingerprint worth a detector rather than a hand label.
5. **Findings ledger (item 8).** The detector sweep now produces comparable hits every window, which is exactly the
   input a `research/findings.jsonl` with a recheck cadence needs. This is the natural next build.

## Anti-goals

Read-only research, no execution service — the fork proofs stay proofs. Exact numbers live in code; prose only interprets,
with stated confidence that `verify` has to earn. Coverage % is a diagnostic, not the goal; the goal is verified,
capacity-aware insight that compounds into detectors.
