# Structural mispricing in Polymarket's resolved history: templates, ladders, dynamics (2026-10-14)

**Verdict: no-go, and `book_entries.json` is `[]`.** None of the four pre-registered hypotheses produces an executable
edge at real size.

One weak tilt survives the main protocol: buying NO on crypto price-range longshots a day before expiry. It failed the
confirmation test registered in advance on fresh events, and it is worth about $4k a year at the touch at most.

Numbers are from `analysis.json` (key in brackets) and `scripts/pm_structure_scan.py`; tables are in `tables.md`.

## Mechanism and counterparty

The rent hunted was lottery-ticket buying: cheap YES on drama, range buckets, exact scores and mention words. Where
that rent shows up at all, it is smaller than the spread plus fee once costs match the market's liquidity:
- YES at 0.10–0.25 in date-deadline markets;
- crypto range buckets the day before.

Ladder "violations" sit in dead books, so nobody on the other side is paying.

## The classifier and the selection-bias correction

**The template classifier** (`classifier`) was checked against 266 hand labels, written without seeing the regex
output:
- accuracy 94.7% overall, and 98.0% on the 50 random draws;
- macro precision 93.8%;
- precision by template: exact score, tweet count, mention and approval 100%; release-by 88%; drama-by-date 78%.

**The volume-floor bias is confirmed and corrected** (`selection_bias.ALL_MULTI`). In the same 564 completed events:
- the stored universe's members resolve YES 2.1pp above price;
- all tradable members resolve 1.8pp below price.

Before → after correction, the gap moves from +7.7pp to −1.1pp for weather and from +7.9pp to −0.8pp for futures. The
corrected design (`inventory.design`) has two parts:
- events complete in the universe, at their sample weights (19,166 markets);
- 564 hash-drawn incomplete events, with every member of at least $1k volume fetched (6,618 members).

## The four hypotheses

**(a) Drama by date** (`templates.calibration`, `templates.families.drama_by_date`).
- YES at 0.10–0.25 resolves 6.5–9.1% of the time against a 17–19% price. YES at 0.50–0.90 resolves *above* price.
  That is the favourite–longshot shape, not blanket overpricing of YES.
- The chosen rule (3 days out, YES at 0.10–0.25, buy NO) has t 1.31 on 53 trades. It survives BH within its own family
  only; $2.8k a year.

**(b) Other templates** (`templates.families.*`).
- 9 of 26 families are untestable: no variant has 30 trades on both sides of 2026-01-01. They are exact score, esports
  maps, props, approval, FDV, econ, ranking, futures and on-date.
- The best is `price_range|1d|0.02-0.10|NO`: +3.3% a trade, out-of-sample t 2.38, $3,980 a year.
- The pre-registered fresh-event confirmation (`confirmation.results`; 359 complete 2026 events) did not confirm it:
  +1.2% a trade, t 1.35, event-bootstrap p 0.16.
- The two `price_above` 6h variants reach only t 0.95 and 1.10.

**(c) Ladders.**
- At midpoints, 1.5% of strike-ladder pair-hours are violated (`ladders.history_stats.strike`). The midpoint trade
  shows +24% a trade, t 3.6.
- Fills tell a different story (`ladder_fills`): 110 of 120 sampled entries had no taker trade on one leg within 30
  minutes. Only 1 had fills that lock a profit. The median fill edge is −0.38¢, against +4.1¢ at midpoints.
- Live (`ladders.live`): five atomic POST /books re-reads between 07:45 and 08:38 UTC found 1–2 violations each, worth
  $0.35–1.39 on $251–671 of capital. That is $0.49 a day.

**(d) Dynamics** (`dynamics`). None of 72 variants is positive out of sample; the best loses 6.0% a trade. The chosen
24-hour momentum rule loses 7.8% a trade, t −2.32.

## Late entry and capacity

**Late entry:**
- `price_range` keeps 110% of its edge, and 135% on the fresh events (`templates.families.price_range.late_entry`).
- Ladders keep 31%, and only 46% of violations are still positive after costs an hour later
  (`ladders.history_entries_theta0`).

**Capacity:**
- Median best-ask depth for NO at 0.90–0.98 in range markets is $46 (`live.depth_best_ask`).
- `price_range` uses $372 of capital for $3,980 a year; on fresh events, $503 a year.
- Ladders: $179 a year.

## Variants

1,351 in all:
- 1,248 template variants;
- 72 dynamics;
- 28 ladder;
- 3 in the pre-registered confirmation (`confirm_preregistration.json`).

All 1,348 main variants were also run once on the uncorrected design. That run is superseded and kept in
`raw/analysis_uncorrected.json`.

One-sided BH at q = 0.10 leaves 9 survivors:
- 4 strike-ladder midpoint bounds, which are not executable;
- 5 template variants with 7–50 out-of-sample trades.

## Errors found and fixed

1. **Volume-floor winner bias.** It produced the uncorrected run's "go" on favourites in multi-member templates.
2. **Thin markets charged liquid spreads.** Live spreads are 2–8× wider under $10k of volume. Costs now follow each
   market's volume class; without this, `price_range` had looked confirmed.
3. **Heavy weights.** `sports_draw` at "$57.9k/yr" came from 5 trades weighted up to 2,107. Its complete events alone
   lose 8.9% a trade.
4. **Ladder parser bugs:**
   - a UTC endDate shifted "December 31" into the next year;
   - one December market had a bad gamma endDate;
   - 2022 markets carried 2023 relisting start dates;
   - "Kansas" matched "Kansas State";
   - a comparison word was read with a different number;
   - bare counts were treated as date ladders;
   - the direction of "top N" was reversed;
   - "reach" was used for strikes below spot;
   - a ">126" label meant $126K.

   A resolution-consistency audit now shows inconsistent pairs at 0.004% for strike ladders, 0.03% for date ladders and
   0.35% for touch ladders.
5. **Stale midpoints.**
   - Points are now capped at 2 hours old.
   - Ladder trades are valued at the locked payout.
   - A ladder go needs executable fills.
6. **Pilot census truncated** at 249,893 open markets. Later snapshots use a $1k volume floor.
7. **Confirm-shard write race.** The gaps were filled with a single unsharded pass.

## Kill criteria and what next

- **Range longshots (NO):**
  - Re-test on at least 500 fresh Q4 events.
  - Kill if the fresh t is below 1, or if NO-side touch depth stays under $100.
  - Only a maker version scales (resting NO bids, no fee), and testing it needs order-level fill data.
- **Ladders:** revive only if live reads show more than $50 a day beating SSR for a week.
- **Drama by date:** needs about 2.3× more out-of-sample data (`near_misses`), which means complete-event collection
  for by-date templates.
- **The nine untestable 2026-era templates:** forward-collect their books.

## Coordinator's check

The ladder fill check was recomputed from `ladder_fills.json` (120 rows), independently of the script. It reproduces
exactly:
- 110 entries with no taker trade on one leg within ±30 minutes;
- 10 with fills on both legs;
- 1 with a positive fill edge;
- a median fill edge of −0.376¢, against +4.062¢ at midpoints.

`selection_bias.ALL_MULTI` matches the report: completed events' universe members +2.08pp (n 1,999), all tradable
members −1.83pp (n 3,263), and the corrected design −1.41pp (n 10,532).

## Files

- `scripts/pm_structure_scan.py`
- `scripts/test_pm_structure_scan.py` (27 tests pass)
- in this folder:
  - `analysis.json`, `tables.md`, `manifest.json` (21,621 requests, 7 retried errors, 0 throttled);
  - `book_entries.json` (`[]`);
  - `hand_labels.json`, `confirm_preregistration.json`, `ladder_fills.json`;
  - `raw/` (git-ignored, 204 MB): 16.4k new price series, the full events, and the live snapshots.
