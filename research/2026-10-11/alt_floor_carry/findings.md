# The altcoin floor-carry basket: long spot as collateral, short the same venue's perp — 2026-10-11

The collateral watcher found 642 altcoin collateral/perp pairs settling at the funding formula's interest leg (10.95% a
year) on at least half of their last 30 days' settlements. Binance portfolio margin accepts 488 spot assets, so the
two-venue constraint that keeps the HYPE carry uncollected does not bind there. The rent map had estimated the
altcoin excess at $0–0.3M accessible, but never tested it. `scripts/alt_floor_carry.py` tests a diversified basket
chosen by trailing floor persistence, with negative spikes, basis moves, delistings, costs and capacity.

## Answer

**No-go, on Binance and on Bybit.**

- All 32 pre-registered variants lose on both venues: in sample, out of sample, and over the full window.
- The variant that loses least is the one that deploys the least capital.
- They still lose at zero fees and spreads.

| | Binance | Bybit |
|---|---|---|
| chosen variant | 28-day, ≥75% floor, spike screen, ≥$10M volume, 30 names | 28-day, ≥50% floor, spike screen, ≥$10M, 30 names |
| in-sample excess (in_sample_positive) | −0.65% a year (False) | −0.02% (False) |
| out-of-sample excess (HAC t) | −0.14% (−2.30) | −0.40% (−1.87) |
| bootstrap 95% interval, out of sample | −0.31% to −0.02% | −0.96% to −0.07% |
| one-sided BH survivors | 0 of 32 | 0 of 32 |
| capital deployed, out of sample | 3% | 5% |
| baseline (top N by floor share, no screens), out of sample | about −8.7% | −9.3% to −9.9% |

## Why it fails

- **Floor share does not persist.**
  - Coins at the floor on ≥ 90% of trailing settlements earned a mean of only +1.26% a year over the next 28 days
    (median +9.86%).
  - 32% of those windows contain a negative spike.
  - On Binance, negative settlements cost the fully invested baseline 5.7–6.2% a year.
- **Only liquid, screened names hold their carry, and there are almost none.**
  - With spot volume ≥ $10M and the spike screen, the top bucket earns +10.07%, but it holds about 1.5 names per date.
  - Since late 2025 there have been 0–13 liquid names at the floor on any date.
- **Funding fell away out of sample.** Per dollar deployed on Binance:

  | | funding | of which negative settlements | costs | savings rate |
  |---|---:|---:|---:|---:|
  | in sample | +9.19% | −0.99% | −3.71% | −7.67% |
  | out of sample | +3.38% | −2.24% | −3.53% | −4.25% |

  On Bybit, funding per deployed dollar fell from +10.82% to +0.20% (negative settlements −5.91%).
- **The book churns.** Only 14–45% of names survive from one rebalance to the next, which costs 3–3.7% a year.
- **Costs are not the root cause.** At zero costs the chosen variant is still −0.03% (Binance) and −0.22% (Bybit) out of
  sample.

The rent is real and visible: the formula rate is paid most hours. But the payers' motive is the same leverage demand
that reverses in a sell-off, and the reversals land on exactly the coins that looked safest. The HYPE carry survives
because Hyperliquid's own spot is the collateral at size and its longs pay persistently. The long tail fails because
the persistence is not there and liquid names are scarce.

## Data

- **Window.** P&L runs 2024-10-01 → 2026-10-10 (740 days), split at 2025-10-06. The benchmark is the savings rate paid
  each day: mean 6.48% in sample, 3.82% out of sample.
- **Binance USD-M.** 667 USDT coin perps, including 133 delisted (still listed as SETTLING), 8 found only in the bulk
  funding feed, and 4 recovered from data.binance.vision. 354 are on today's portfolio-margin list. 1,817,551
  settlements kept.
- **Bybit.** 1,065 USDT perps (272 closed); 239 are unified-account collateral. 2,191,326 settlements kept.
- **OKX not done.** Its public funding history reaches back only about three months.
- **Floor detection.** The floor is pro rata to each settlement's own interval, so it follows Binance's 8h, 4h, 2h and
  1h switches.
  - `probe` matched the collateral watcher exactly on 18 coin/venue pairs (Binance MAGIC 85.00% / −20.27%, KAIA
    72.95% / −90.83%).

## A new data trap: phantom settlements after delisting

- **Binance keeps printing funding at exactly the floor for delisted perps.**
  - Inside the window, 69 perps have 51,434 settlements on days they did not trade, and 97% sit exactly at the floor.
  - 18 perps never traded in the window yet printed 21,321 settlements. WAVESUSDT, delisted 2024-06-11, was still
    "settling" in June 2025.
- **Without a cut these look like perfect floor coins.** The study keeps a settlement only on a day the perp traded,
  and only before its delivery date.
- Bybit has no such prints.
- **Any Binance funding-history study that does not cut on traded days is exposed.** The rent map's floor shares should
  be checked against this.

## Robustness

- An all-spot universe (delisted coins included, one assumed collateral ratio) picks the same variants and loses.
- With the constant 3.80% benchmark, in sample turns slightly positive (+0.35% Binance, +1.53% Bybit); out of sample is
  still −0.12% and −0.38%.
- Doubled costs: worse. A signal one day stale: unchanged.
- **Capacity.** It is irrelevant here: every size loses, from −$2k a year at $1M to −$30k at $10M on Binance. What binds
  is the universe, not the participation cap.

## Method fix found here

`backtest.choose_then_test` ran Benjamini–Hochberg on two-sided p-values, so it listed 31 Binance and 24 Bybit
"survivors" that were all significant losers. It now also returns `bh_survivors_positive`, the one-sided test for a
positive mean, which a go rule should use. The existing field is unchanged, so earlier outputs reproduce; a test pins
the difference.

## Errors found in the worker's own work (all fixed before any results)

1. A 2-hour gap was read as a missing hourly settlement. Binance really runs 2-hour intervals (modal 0.0025%, the
   floor).
2. A spot-mapping failure label mixed "no spot market" with "different coin". There is one genuine mismatch, Bybit FB.
3. Bybit ignores `status=Closed` for spot pairs, so delisted pairs are fetched by name.
4. Capacity rows sorted as text.

## Coordinator's check

Recomputed from `series.json.gz` alone, as the mean daily excess × 365 on each side of the cutoff (day 370 of 740):

| venue | in sample | out of sample |
|---|---:|---:|
| Binance | **−0.65%** a year | **−0.14%** |
| Bybit | **−0.02%** | **−0.40%** |

That matches the note.
