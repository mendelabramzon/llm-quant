# Building the best onchain research analysis system — roadmap

This is the standing plan for `llm-quant`. The goal (see the research memo and memory) is a closed qual↔quant loop:
the LLM reads evidence, proposes mechanisms, and writes the infrastructure; deterministic code turns mechanisms into
reusable detectors and tests; the human steers. The metric we optimise is **time-to-verified-insight**: how fast a raw
signal becomes a true, capacity-aware, reproducible claim and then a reusable detector — not classification coverage.

## Session log — 2026-09-08 (ten chains at once, and the denominator that was wrong everywhere)

The loop had only ever run one chain at a time, which is a real blind spot for a *dollar*: USDC on Base and USDC on
Ethereum are the same claim on the same issuer, bridgeable in minutes for approximately nothing, so their lending rates
are two prices for one asset. This pass built the cross-chain layer and used it on a fresh hour
(2026-09-08 06:23–07:29 UTC): Ethereum block-by-block plus a logs-only trailing hour on ten EVMs.

Landed: `scripts/multichain.py` (collect / head / issuance / analyze / verify / render — discovery-first, no asserted
pool, bridge or token addresses), `scripts/fee_census.py`, and an `url=` parameter on `live_rpc.RPC` so several
networks can be live at once.

**The finding.** USDC pays 4.00% on Base and 0.36% on Scroll at the same instant — 3.64 percentage points across
$2.78B — and the whole thing is worth **$177,794 a year**. Two corrections get there and both are the point: the high
side dilutes along its kinked curve, and *the low side may not let you leave*. Optimism's USDC reserve pays 2.56% on
$11.3M of which **$2.3M is withdrawable**, so the $18.5M the curve calls optimal cannot be moved at an eighth of that
size. Capacity is `min(high-side optimum, low-side withdrawable)`, and for seven of twenty switches the second binds.
Filled once, cheapest source first, $8.73B of cross-chain dollars absorbs **$37.3M at 48bp**. Taking the rows
independently would claim $279k — 57% too high, because every row assumes the destination reserve is empty.

**The bridge is not the arbitrageur.** Net CCTP flow ranks **−0.57** against the USDC rate over eight chains: the two
highest-paying chains were the only net exporters. Eight addresses appear on both sides of the bridge among the largest
counterparties, which is inventory rebalancing toward demand rather than capital chasing yield. And 62% of CCTP sends
left for domains outside the scan entirely.

**The denominator was wrong on every chain, and version-dependently so.** Every capacity, width and best-size number
this repo computes rests on utilisation, read as `variableDebt.totalSupply() / aToken.totalSupply()`. That is not what
Aave prices with. Ethereum and Base reproduce their published borrow rate from the aToken total; Avalanche reproduces
it from `getVirtualUnderlyingBalance()` plus debt, the gap being unbacked aTokens. On Avalanche's GHO reserve the gap
is 0.46pp of utilisation, it straddles the 90% kink, and it is worth **151 basis points of borrow rate** — the aToken
ratio says 4.50%, the pool says 6.00%. Utilisation is now **inverted from the pool's own published borrow rate**, which
is correct whatever the deployment version. Three smaller ones fell out of the same verifier: a reserve factor of 1.0
is a mint facility, not a supply market (Aave's $135.2M Ethereum GHO reserve, which produced the largest switch on the
first pass, $12,798/yr, entirely imaginary); a flat IRM carries no information about utilisation and cannot be
inverted; and two tokens on Arbitrum both answer `symbol()` with "USDC", so switches are keyed by reserve address.

**Ethereum's fee market has stopped pricing blockspace.** Base fee 0.049 gwei at 50.6% fullness: the chain burned
0.443 ETH ($1,098) in the hour while users paid 3.068 ETH ($7,598) in priority fees, a **6.92x ratio**, of which
98.5% is spend above the gas-weighted median tip of 0.0087 gwei. **35.6% of all gas paid exactly zero.** The largest
single consumer of Ethereum blockspace was **XEN** batch-minting — 8.2% of the chain-hour for $2 of tips. Blocks are
half full because the marginal buyer of blockspace is an activity that only exists at a gas price of zero, which is
why the price stays at zero. Open item, and the first one in the next-steps list: `economics.py` charges gas at the
base fee and therefore understates an inclusion-sensitive leg by roughly sevenfold in this regime.

## Session log — 2026-09-08 (the output: a strategy book, and what the dollar surface is actually worth)

The loop's stated output is insight and proposed strategy. The roadmap had described only machinery, so this pass
built the terminal artifact and then used it, on a fresh two-hour window collected for the purpose (2026-09-07
21:27–23:27 UTC, 599 blocks).

Landed: `scripts/strategies.py` + `research/strategies.jsonl` (the strategy book — legs, capacity, **kill criteria**,
and a quote series so decay is visible), `scripts/seed_strategies.py`, `detectors/dollar_rate_outlier.py`, reserve
discovery via `getReservesList()` in `head`, per-reserve IRM parameters, and sampled Compound supply curves.

**The finding.** Measured against the risk-free dollar — Sky's savings rate, 3.60%, unlimited size, no venue risk —
exactly **two of twenty-seven dollar reserves** across Aave, SparkLend and Compound pay more than doing nothing. About
$8.5B of supplied dollars sits in reserves paying less than the issuer's own savings rate. And the two that clear it
are tiny: Compound v3 USDC sits 0.77 percentage points above a kink at exactly 90.0% utilisation, so its whole
5.69% headline is **$1.25M wide and worth $14k a year**; Aave's USDtb reserve is $227k wide and worth $5.4k. The best
two dollar rates on mainnet are jointly worth about $19,000 a year.

**Three bugs in this repo's own machinery, each of which changed a number.** The de-spiker read index 2 of each rate
point — the *borrow* rate — when de-spiking a *supply* rate, and survived because both sides were wrong in the same
direction (USDT gap 1.66pp → 0.98pp). The venue pair was selected on spot rates and de-spiked afterwards, so during
Aave's nightly utilisation spike the comparison became Aave-over-Spark, was correctly dismissed as an artifact, and
the real Compound-over-Spark finding was never compared at all — the spike hid a true finding rather than adding a
false one. And capacity was modelled with a smooth `r·S/(S+X)` curve on markets that have a cliff, reporting
**$93.8M of capacity worth $945k a year** for Compound USDC against a true **$1.4M worth $15k**, a 63x overstatement
of the number that decides whether a strategy is worth doing. All three are fixed and the detector's ladder now
reproduces `getSupplyRate` to two decimal places.

**The nightly routine, caught live.** At 23:41 UTC Aave's $2.16B USDC reserve stood at exactly 100.0000% utilisation
with **$503 of available liquidity**, after an account withdrew ~$152M of supply. The 12.87% it prints is worth about
$55 on $10M over the half hour it lasts; the finding is the other side — USDC cannot be withdrawn from Aave for
roughly thirty minutes every night, which is a hard constraint on any strategy whose exit leg is that reserve, and it
is now recorded as a risk on that strategy rather than as prose.

**What the book says about the loop.** Seven live strategies, two retired on economics. The largest edges are the
smallest positions: the 15.8% LP is a $150k idea, and the $1B-capacity idea pays 3.48% and is a savings account.
Nothing in the book is simultaneously large and mispriced. And only three of seven carry a quote a detector produced —
the rest were measured once in a dated session, which is the same failure the findings ledger fixed for findings.

## Session log — 2026-09-08 (the loop closes: staleness, claim tags, ledger, three detectors)

Landed: `scripts/provenance.py` (what an artifact was built from, and a hard gate on it), `scripts/findings.py` (the
findings ledger with recurrence, decay and a recheck cadence), three new detectors — `solver_fingerprint`,
`jit_liquidity`, `mass_distribution` — `labels.py adopt-shapes` (detector → registry), `live_scan pipeline` (the four
steps in dependency order), verify recipe ids with `[[verify: id]]` claim tagging, a fourth mechanism assertion, and
`scripts/test_findings.py` (13 tests over the two new bookkeeping modules).

**What it found, which is again the point.** The `mislabelled_flow` detector had been reporting the same address at
high severity on both 2026-09-07 windows: [0x3cc936b7](https://etherscan.io/address/0x3cc936b795a188f0e246cbb2d74c5bd190aecf18),
tagged `exchange_deposit` by the day study's behaviour profile. It is an externally-owned account that collects small
inbound legs and forwards them in one large one — $99.99M of USDC in a single transaction on the five-hour window, to a
verified Gnosis Safe that forwarded the whole amount on again. Counting that leg as exchange outflow is wrong under
either reading: if the address is an exchange deposit address, the sweep goes to exchange infrastructure and the leg is
internal; if it is not, the leg is not exchange flow at all. Both readings agree, so the tag was retired without having
to settle the identity.

| headline, 2026-09-07 five-hour window | with the deposit-sink tag | corrected |
|---|---:|---:|
| exchange net flow, stables | −$24.8M | **+$75.2M** |
| exchange net flow, USDC | −$97.9M | **+$2.0M** |
| label band, model-memory → behaviour | +$91.6M → −$24.8M | +$91.6M → +$75.2M |

That is the third mislabel of this family, after the CoW settlement contract and the deposit-sink rule itself, and the
first found by a detector rather than by hand. The label band this repo introduced last session to flag its own
uncertainty turns out to have been measuring one bad label: with it gone, the band no longer changes sign.

**The staleness gate proved itself immediately.** Adopting nine shape labels changed the address book, and `verify` on
both windows refused to compare a single number until `analyze` was re-run — which is the behaviour that had to be
enforced by hand twice on 2026-09-07.

**The ledger says which findings are structure and which are noise.** Across the two windows: 47 findings, 22 recurring,
9 closed by labelling. The decay column shows what a single window cannot — the Compound-versus-Spark USDC gap widening
0.87% → 1.41% while the Sky SSR gap held flat at 3.48% — and `seen 1/2` marks every finding that a later sweep, running
the same detector, did not see again.

**The detectors found things the hand analysis had missed.** `mass_distribution` surfaced 0.0003 USDT sent to 12,056
addresses by one sender — token-transfer address poisoning at a scale the native-ETH poisoning detector cannot see.
`solver_fingerprint` characterised the whole unlabelled tail: the top three entries pass $1–9B straight through, each
with one or three counterparties, and `verify`'s new `fingerprint-matches-chain` assertion confirms against Blockscout
that the detector's contract-versus-account calls were right on every hit where it committed to one, and declined to
guess on the rest.

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

Weaknesses, updated 2026-09-08. Most of the 2026-09-07 list is now closed: claims are verified against an independent
re-derivation, mechanisms are re-runnable assertions, one-off scripts have become seven detectors, opportunity economics
run through one scorer, and a stale artifact announces itself. What remains, in the order it bites:

* **Data access is still the binding constraint.** No trace or archive endpoint means the CoreVault bytecode
  fingerprint and any balance-delta test cannot become detectors, and fork tests only run at latest. This blocks more
  planned work than everything else combined.
* **Head reads are still spot** where the venue emits no logs. Compound and Sky publish no `ReserveDataUpdated`, so
  three of the six standing rate findings carry "one-block read, de-spiking unavailable", including the two largest.
* **Labels remain mostly behavioural and model-memory**, and the fourth mislabel found (2026-09-08) moved a headline's
  sign. The detector now catches this class automatically, but catching is not preventing: 30% of window USD still
  touches an address the registry cannot name, and `adopt-shapes` can only file the half of that tail whose shape
  settles the question.
* **Coverage of prose by verified recipes is about half.** `verify` now counts it, which is the first step, but the
  tape prices, blob counts, gas-share arithmetic and health factors in every note are still single readings.

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
*Extended 2026-09-08 with a third class of check.* The numeric checks re-derive window aggregates through a second
code path, but `head_state.json` — where every rate and yield in every note lives — had no second path to read it
through and so was simply asserted. **Identity checks** cover it: the protocols publish relationships between the
fields they report (a supplier earns the borrow rate times utilisation less the reserve factor; a borrow rate is the
IRM curve at that utilisation; a Morpho supply APY carries the market fee instead; a PT's implied yield is a function
of price and maturity; the Compound read must lie on the curve sampled at the same block), and re-deriving one field
from the others tests the whole decode — word offsets, ray scaling, config bitmaps, curve parameters — against the
chain's own arithmetic. Seven classes and 188 individual identities pass on the 2026-09-08 windows, the last of them a genuine second
opinion rather than an internal one: `head-nav-crosscheck` reads each exchange rate a second way on chain — an
ERC-4626 vault's share price against its own `totalAssets / totalSupply`, `wstETH.stEthPerToken()` against
`stETH.getPooledEthByShares`, rETH's and weETH's share conversions — and the five that publish a second view agree to
twelve decimal places. Three (cbETH, ezETH, rsETH) publish none, so the check reports how many rates it could compare
rather than implying it checked them all. Setting Aave's USDC supply APR to its
borrow value — the exact shape of the rate-series bug found earlier the same day — fails `head-supply-identity`
immediately, naming the venue, asset, utilisation and reserve factor. It also found a reproducibility defect on its first run against fresh
data: `days_to_maturity` was stored rounded while `implied_apy` was computed from the unrounded value, so the artifact
did not reproduce its own output — a residual of 2e-6, and exactly the class of thing these checks exist to surface.

*Closed 2026-09-08*: every check now carries a stable id, a sentence cites it as `[[verify: exchange-net-stables]]`,
and `verify` fails on a citation with no matching check and counts the headline numbers that cite nothing — 55% of the
midday note's big numbers are tagged, 46% of the five-hour note's, and the untagged remainder is now visible rather
than assumed. A fourth mechanism assertion, `fingerprint-matches-chain`, checks the new tail detector's
contract-versus-account calls against Blockscout on every hit where it commits to one. Effort: M–L.
Payoff: **the single biggest quality lever** — it makes the confidence labels earned, not asserted.

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
a large transfer). Three more landed 2026-09-08: `solver_fingerprint` (the unlabelled tail, split by shape into
pass-through, cycling and retaining, with contract-versus-account proven from the window and reported as unknown when
the window cannot prove it), `jit_liquidity` (the share of pool fees taken by liquidity that arrived for one swap, per
pool and per window, with the operator economics priced as a race), and `mass_distribution` (one sender fanning a token
to thousands of recipients — airdrop, mint distribution or dust spam). The generalised gas detector **rediscovered the
tokenized-stock router** on the five-hour window without being given its address; `mass_distribution` found a
12,056-recipient USDT dust campaign the hand analysis of the same window had missed; and `mislabelled_flow` found the
fourth label bug. Effort: L. Payoff: every window automatically re-checks every past discovery; the system stops
forgetting.

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

**8. Findings ledger with recheck cadence.** *Done — `scripts/findings.py`.*
Problem: findings are point-in-time; only the midnight routine is tracked daily. Proposal: `research/findings.jsonl`, each
finding an id + a recheck cron + a realized-vs-predicted log. **Shipped**: a finding is identified across windows by
`detector:key`, so the same rate gap on Monday and Tuesday is one finding observed twice; `research/windows.json` records
which detectors ran in each ingested window, which is what makes *absence* mean something — every finding reports
`seen / eligible` rather than a bare count, and a gap at 1/4 is visibly a spot artifact where 3/3 is a standing
dislocation. Economics-bearing hits keep their predicted net APR per observation, so the report prints a decay column.
`close` records why a finding was answered (nine were, by `adopt-shapes` labelling their addresses) so it stops
appearing in `due`. Effort: M. Payoff: **demonstrated** — 22 of 47 findings recur across two windows, and the ledger
flagged the 0x3cc936b7 mislabel as recurring before anyone looked at it.

**9. Signal-testing harness with controls and multiple-hypothesis correction.**
Problem: the informed-flow test (does exchange netflow predict returns) was run once, ad hoc, and found null. Proposal:
generalise the hash-sampled controls already in `amount_outliers`, require out-of-sample and FDR control before any
"signal" is reported. Effort: M. Payoff: stops the loop from over-fitting a five-hour window.

**10. Reproducibility manifests everywhere.**
Problem: some follow-up scripts are path-hardcoded. Proposal: every artifact carries `{code_sha, registry_sha, block_range,
price_basis}` the way `tx_types` `rounds.json` already does. Effort: S per script. Payoff: any report is replayable and
diffable.

## Do next (concrete)

Items 1, 2, 4 and 5 of the previous list are done; item 3 is done except for the two detectors that need the RPC layer
or a window that spans midnight. What this pass exposed, in priority order:

1. **A window that spans midnight, so the midnight-routine detector can be written and fire.** Every window collected
   so far runs 02:39–12:39 UTC, and the daily 23:30–00:20 balance routine — the most reliably recurring mechanism this
   project has found — is the one thing the detector registry still cannot re-check. It needs a collection, not code.
2. **De-spike `head_state.json` itself.** `rate_dispersion` de-spikes what it quotes, but the head file still stores spot
   values and Compound and Sky emit no `ReserveDataUpdated` logs, so their reads cannot be de-spiked at all. Three of the
   six standing rate findings are marked "one-block read, de-spiking unavailable" for exactly that reason, and the two
   largest by predicted APR are among them.
3. **Close the loop on the `retains` half of the tail.** `solver_fingerprint` splits unlabelled addresses into
   pass-through and retaining, and `adopt-shapes` only files the first kind, because a shape claim cannot settle what a
   retaining address is. Those are the ones whose mislabelling moves headlines — 0x3cc936b7 was one — so they need a
   cheap identity route: funder graph, first-funding transaction, or a counterparty-set match against known exchange
   infrastructure.
4. **The data-access layer (item 6).** Still the largest blocker: no trace or archive endpoint means the CoreVault
   bytecode fingerprint and the JIT-liquidity balance-delta test cannot become detectors, and fork tests only run at
   latest.
5. **Signal-testing harness (item 9).** The ledger now produces exactly the input it needs — a repeated observation of
   the same finding with a predicted number attached — so out-of-sample and FDR control on "does this edge persist" is
   the natural next build after a few more windows accumulate.

## The output the loop is for

Everything above is machinery. The loop exists to produce two things, and the roadmap had not named either until now:

**Insight** — a claim about how a market works that is true, capacity-aware, reproducible and dated. The system's
apparatus for this is in place: `analysis.json` for the numbers, `verify` to re-derive them, the detector registry to
re-check the mechanism next window, and the findings ledger to say whether it recurred.

**A proposed strategy** — a claim about the *future*: that a mechanism will keep producing an edge, and that the edge
survives gas, impact, competition and decay at a size worth deploying. This is a different object from a finding and
needs three things a finding does not: legs that `economics.py` can price, falsifiable **kill criteria**, and a **quote
series** so decay is visible rather than remembered.

`scripts/strategies.py` and `research/strategies.jsonl` are that book. Its first honest reading, seeded 2026-09-08 with
every strategy this repo has produced, is the diagnostic the loop needed: nine strategies, two retired on economics,
two fork-proven, and **only three whose numbers a detector re-prices automatically**. The rest were measured once in a
dated session and have not been re-measured since, which is exactly the failure the findings ledger was built to stop
for findings and had not yet stopped for strategies. A strategy backed by a detector stays current for free; a strategy
backed by a bespoke scanner decays into a memory the moment the session ends.

Excluding the savings rate, which is the benchmark rather than an edge, the whole book measures at **about $229,000
a year**, of which **$125,600 survives its own detectors' verdicts** — and that is the point of building it. The
$103,500 difference is one row: the sUSDe redemption trade, the largest edge in the book, declined by a significance
test written the same day. Its 4.7bp net edge was measured across a window whose p10-to-p90 price spread was 5.4bp,
so the discount is not distinguishable from where the asset traded. A book that reports that is worth more than one
that reports 17% a year. Every row now has legs `economics.py` priced, a capacity that came
from a rate curve, a withdrawable balance or a traded volume rather than a headline size, and a kill criterion. An
efficient market is supposed to look like this; the value of the loop is that the number is derived rather than
asserted, and that it moves on its own when the market does.

The book also disciplines the reading of a finding. A cross-venue rate gap is only an opportunity if the *higher* venue
clears the risk-free dollar, and most do not: "PYUSD pays 3.29pp more on Aave than SparkLend" is worth 28bps over the
actual alternative, and "DAI pays 0.61pp more on Aave than SparkLend" compares two rates that are both below the
savings rate. `dollar_rate_outlier` exists to make that comparison the default one.

That gives the next round of detector work a clear ordering principle: **write the detector that re-prices the highest
strategy in the book that nothing re-prices.** The first of those is done — `detectors/lp_marginal_yield.py` prices a
concentrated-LP position at the band the price stayed inside, at real size, net of the divergence the same
concentration amplifies, and it gave the captive-flow LP its first automatic decay series (15.80% hand study → 6.13%
→ 10.37% → absent, zero swaps in a two-hour window). The second is done too — `detectors/nav_discount.py`
compares what a protocol pays on redemption against what the market paid for the claim, and separates the two with the
three things that decide whether a discount is a trade: the measured round-trip cost (the sUSDe path is −2.7bp, which
is 38% of a 7.1bp discount), the *availability* of the redemption leg (rETH's larger 17.7bp discount is demoted
because Rocket Pool's burn pool is empty most of the time), and capacity taken as the volume actually offered rather
than pool depth. Five of the seven strategies now re-price themselves. The third is done as well: `head` now discovers Pendle markets from
the window's own `Swap` logs — the markets with live flow, no hardcoded list and no API — and
`detectors/fixed_vs_floating.py` classifies each implied yield as a *term premium* (the floating rate on the same
underlying is readable, so the gap is a rate view) or a *credit spread* (it is not, so the excess is the price of an
issuer's credit that nothing here has assessed). Every Pendle market that traded in the 21:27–23:27 window was the
second kind, at 6% to 23%. And the fourth: `detectors/borrow_cost.py` ranks the cheapest venue to
borrow each dollar and caps the saving at the liquidity actually withdrawable there, reading Morpho Blue's isolated
markets from the window's own event topics. **All seven strategies now re-price themselves; none is a hand
measurement.** The last one to fall was the largest: "borrow USDT on Morpho rather than Aave" was quoted at 91bp on
$24M and measures at 1.46pp on $6.35M — a wider rate on a quarter of the size, because $24M was the vault and $6.35M
is what is withdrawable, and the cheap market lends only against sUSDS at 96.5% LLTV, which the hand note never said.

Two gates were added after the loop fell into the gap between them. `head_state.json` is an input to `analyze` — the
whole window is priced from it — and it was not fingerprinted, so re-running `head` silently re-priced an analysis
that was not re-run, with labels and tokens both unchanged and no gate able to see it. `head` is now a provenance
gate, and `head` itself refuses to read current state for a window collected long ago rather than mixing two
timeframes.

## Anti-goals

Read-only research, no execution service — the fork proofs stay proofs. Exact numbers live in code; prose only interprets,
with stated confidence that `verify` has to earn. Coverage % is a diagnostic, not the goal; the goal is verified,
capacity-aware insight that compounds into detectors.
