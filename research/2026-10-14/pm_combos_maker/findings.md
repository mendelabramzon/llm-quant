# Could a new quoter earn the Polymarket combo rent? (2026-10-14)

**Verdict: no-go, and `book_entries.json` is `[]`.**

The protocol's pick was cross-game combos of 4–6 legs, quoted at 1.4× the product of the leg midpoints:
- in sample it made $311k (Sharpe 6.33, t 3.37);
- in the test it lost: HAC t −0.34, rank 30 of 36, payout-count z 0.28 (`protocol.choose_then_test`, `variants`);
- capping each fill at $1,000 changes nothing: t −0.46 (`family_capped`).

One cell survives only as a description: cross-game combos of 7+ legs. It is a candidate for a forward paper quoter,
not a finding.

This follows `research/2026-10-14/pm_parlays`. That study found Polymarket's incumbent combo makers earn +1.93% on
$217M risked (t 3.80), but it lacked leg prices at entry. Numbers here come from `analysis.json` (key in brackets),
produced by `scripts/pm_combos_maker.py`. Tables are in `tables.md`.

## Mechanism and counterparty

- **The payer** is the parlay buyer, betting for entertainment. Buyers request YES on a multi-leg combo, makers quote
  privately within 400 ms, the best price fills, and makers pay no fee.
- **What a new quoter brings** is a pricing model (the legs' CLOB midpoints) and collateral of 1 − q per contract.
  Nothing depends on block position.
- **The winner's curse is built into the test.** The quoter fills only below the incumbent's observed price. Fills are
  sized in notional, as the docs specify.

## Data

- **Sample:** 38,529 of 529,004 incumbent NO positions, stratified by month × legs × structure × maker. All 6,856 tickets
  of $1,000 or more are included at weight 1 (`sample`).
- **Leg prices:** 1-minute CLOB midpoints from `batch-prices-history`, 20 tokens per call (5,653 requests, 0 errors).
  - 99.98% of pre-game positions are priced, with a median leg age of 32 s.
  - In-play flow (27.0%) is excluded (`coverage`).

## Headline numbers

**The leg product is a usable fair value** (`calibration`):
- Cross-game combos hit 1.023× the fair in sample (z 1.07) and 1.031× in the test (z 1.33).
- For same-game combos the naive product under-predicts: they hit 1.19× it (z 4.50). The correlation lift fitted in
  sample brings that to 1.059× in sample and 1.064× in the test.

**The rent has compressed.** The incumbents' premium-weighted margin over fair fell from about 19% in June–July to 8–9%
from August on (`incumbent_margin.month`). By cell (`incumbent_margin.struct_legs`):
- cross-game, 2–3 legs: 8.1%;
- cross-game, 4–6 legs: 17.8%;
- cross-game, 7+ legs: 47.1%;
- same-game, 7+ legs: 133%.

**The winner's curse is visible.** Cross-game 2–3 legs is the bulk of the flow, and it loses in both halves at every
margin up to 0.20. The quoter wins exactly where the leg fair sits lowest against the incumbents.

**The go gates for the pick** (`go_rule`):

| gate | result |
|---|---|
| positive in sample | yes |
| test HAC t ≥ 2 | no (−0.34) |
| in the BH survivors | yes |
| payout-count z ≥ 2, in sample / in test | 2.07 / 0.28 |
| excess over the 3.80% savings rate | −$180k a year on $499k of peak capital |

## Capacity, dollars and the tail

**The pick, in the test period** (`capacity`, `tail`):
- It won 11.6% of its cell's requests, 0.87% of the incumbents' premium.
- It lost $161k a year on $88k of average capital and $499k at peak.
- Worst day −$46.8k; worst week −$51.3k.
- The buffer for a 1% daily ruin probability is $46.8k empirically, or $6.7k if outcomes were independent.

**Descriptive only: cross-game 7+ legs at m = 0.40** (`descriptive_cross7`):
- All six margins in this cell are positive in both halves, and all survive BH in both families.
- At m = 0.40 it wins 46% of the cell's requests: 23.7% of its premium, 0.61% of all incumbent premium.
- It makes $801k a year on the incumbents' flow, on $223k of average and $891k of peak capital.
- Excess over the savings rate is $767k, with a 95% interval of −$190k to +$1.72M.
- Worst day −$1.9k; one losing day in 43.
- It is short a lottery: 28.75 payouts against the 40.77 the quotes imply.
  - The payout-count z is 2.016 in sample and 1.9993 in the test.
  - The dollar payout z is 1.45 and 1.64.
- It was not the in-sample choice, and its test count z falls just short of 2.

## Variants

72 were evaluated and none dropped:
- **Family A (36):** m ∈ {0, 2, 5, 10, 20, 40%} × cross-game or same-game × 2–3, 4–6 or 7+ legs, at full fill size.
- **Family B (36):** the same grid with a $1,000 notional cap per request. It was registered before any test-period
  prices were on disk, after June showed that 1% of tickets carry 37% of all |P&L|.

The in-sample choice was frozen in `manifest.json` (`in_sample_choice_frozen`) while September was still downloading.

## Errors found and fixed (`errors_found`)

1. **Leg token mapping.** A leg's `position_id` is not a CLOB token, and prices-history returns nothing for it. It maps
   through gamma `positionIds` to `clobTokenIds`: 195,346 legs, 0 index mismatches.
2. **A table bug in pm_parlays.** Its `by_legs` table overwrote its own buckets. It shows 33,007 of 81,228 positions in
   "5-6", 7,268 of 61,183 in "7-10", and 1 of 17,202 in "11+".
3. **The pm_parlays $11k recount gap is fees, not partials.** It is $11,188.64 of entry fees on positions where the maker
   held YES. The partials are 2,802 NO positions on which incumbents lost $238k. On every one, the payout equals the
   product of the leg values, with a void leg counting 0.5.
4. **The dollar payout z passes a lottery.** A book that never pays scores z 2.0 on one expected payout. The gate is now
   the payout-count z against the count the quotes imply.
5. **Whales.** The first 5% draw measured a few tickets at weight 26. The certainty stratum fixes this.
6. **Notional sizing.** Per the docs, a lower quote fills notional / q contracts, and BUY quotes above 0.90909 are
   rejected.
7. **Censoring at the end of the data.** A combo resolves at its first losing leg, so pulling only resolved positions
   misses recent combos that are still alive. Re-running the test through Oct 8 gives t −0.55 for the pick.

## Kill criteria and what next

- **Dead:** quoting combos of 2–6 legs off leg midpoints. Reopen only if the incumbents' margin over the leg product stays
  above 15% for a month.
- **A pre-registered forward paper quoter** for cross-game 7+ legs at m = 0.40. It places nothing:
  - subscribe to `RFQ_REQUEST` and `RFQ_TRADE` at `wss://combos-rfq-gateway-quoter.polymarket.com/ws/rfq` (needs CLOB
    credentials);
  - price each pre-game request from the leg midpoints at receipt, and record q;
  - record whether q would have undercut the traded price, log unfilled requests separately, and mark each at
    resolution.
  - **Go** after 60 days if the count z ≥ 2, the dollar payout z ≥ 2 and the excess > 0.
  - **Kill** if the count z < 0 after 40 expected payouts, or if the 7+ margin falls below 40%.
- **Feasibility** (`feasibility`):
  - No size, rate or position limits are published.
  - Collateral is pUSD approved to Exchange v3.
  - Requests and trades are both streamed, so unfilled requests should be visible. That is an inference; the docs do not
    say so.
- **Limits** (`limitations`):
  - About 6% of positions aggregate several fills.
  - Incumbent quotes are held fixed, though they would likely respond to a new quoter.
  - Only filled requests are observed.

## Coordinator's check

The fair-value calibration was recomputed from `raw/sample.json.gz`, `raw/gamma.json.gz` and `raw/prices/`,
independently of the script:
- each leg's `position_id` mapped through gamma to its CLOB token;
- the last 1-minute midpoint at or before entry, at most 30 minutes old;
- pre-game legs only;
- a hit is the maker's NO position losing.

| | n | weighted, recomputed | reported |
|---|---:|---:|---:|
| cross-game, in sample | 15,443 | 1.014× | 1.023× (n 15,546) |
| cross-game, test | 9,358 | 1.028× | 1.031× |
| same-game naive, in sample | 3,129 | 1.189× | 1.19× |

My stricter staleness rule left 2,653 positions unpriced (1,015 with no series, 1,638 stale), which accounts for the
small differences. The conclusions hold: the leg product is a usable fair value for cross-game combos, and the naive
product under-predicts same-game combos by about a fifth.

## Files

- `scripts/pm_combos_maker.py`
- `scripts/test_pm_combos_maker.py` (18 tests pass)
- in this folder: `analysis.json`, `tables.md`, `manifest.json`, `book_entries.json` (`[]`)
- `raw/` (71 MB) and the two logs, git-ignored
