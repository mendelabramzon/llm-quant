# Temperature markets against the National Blend of Models: the price is the better forecast (2026-10-14)

**Verdict: no-go on both venues. `book_entries.json` is `[]`.**
- **The market price beat the model everywhere:** on every venue, at every decision time, in every city and in both
  periods.
- **No variant passes the go rule.**
- **Both venues were collected in full** (`universe`):
  - Kalshi: 6 cities × 407 days, 2,442 events and 14,652 markets.
  - Polymarket: 1,798 whole events, 17,938 members, across the same 6 US cities.

Numbers are from `analysis.json` (key in brackets) and `scripts/pm_weather.py`; tables are in `tables.md`.

## What was tested

The model priced each bucket from the NBM station bulletin (IEM NBS: the forecast high and its spread), at two decision
times:
- 16:00 local the day before (`d1_16`);
- 08:00 local on the day (`d0_08`).

A station-and-season bias, a seasonal variance and an empirical error shape were fitted on 2024-09 to 2025-08 only. The
rule bought a side when the model's probability beat the all-in cost by a set edge.

## Who the counterparty turned out to be

The hypothesis was retail trading without a model. In fact the price already contains more than the NBM. When model and
price disagree by more than 15pp, outcomes follow the price (`disagreement`, Kalshi `d1_16`):

| | n | model | price | resolved YES |
|---|---:|---:|---:|---:|
| model above price | 1,009 | 35.3% | 12.7% | 13.7% |
| model below price | 1,462 | 18.3% | 39.8% | 38.5% |

## Headline numbers

**Resolution** (`resolution_kalshi`, `resolution_polymarket`):
- The NWS climate report reproduces 2,440 of 2,441 Kalshi settlements.
- Polymarket settles on the maximum of all METAR reports: 1,798 of 1,800 match that, against 70.7% for the climate
  report.

**Calibration before any trade** (`pit`): the model's central 80% interval covers 81–89% of outcomes, and its 98%
interval covers 96–99%.

**Brier score, market against model** (`diagnostics`):

| venue | `d1_16` | `d0_08` | HAC t of the gap |
|---|---|---|---|
| Kalshi | 0.1196 vs 0.1327 | 0.1252 vs 0.1509 | 10.9 and 16.3 |
| Polymarket | 0.0620 vs 0.0681 | 0.0596 vs 0.0707 | 4.6 and 6.8 |

The t-statistics are in `brier_gap_significance`. The market is better in every city (`brier_by_month_and_city`).

**Kalshi's implied high** (`implied_mean`):
- the market's mean absolute error is 1.55°F against 1.95 for the model at `d1_16`;
- 1.24 against 1.73 at `d0_08`;
- a fresher model run lowers the model's error only to 1.89 (`nbm_lag_sensitivity`).

**Protocol** (`protocol`, `go`):
- **Kalshi** chose `d1_16|e0.15|taker|tail`. It was negative in sample, and out of sample its HAC t was −3.58 (rank 34
  of 48). No Kalshi variant is positive pooled in either period.
- **Polymarket** chose `d1_16|e0.10|taker|interior`. It made +7.0% a dollar in sample over 774 trades, then −3.7% out of
  sample over 1,524 trades (HAC t −1.41, rank 13 of 48). One Polymarket variant was positive out of sample, at +0.3% a
  dollar.
- Neither venue has any false-discovery survivors.

## Late entry

There is no edge to keep (`chosen.*.late_same_trades`):
- Kalshi: the same trades an hour later return −28.8% a dollar, against −29.7% at the decision.
- Polymarket: −4.2% a dollar, against −3.7%.

## Capacity

The touch is thin: $1–12 on Polymarket's 5–65¢ buckets and 9–39 contracts on Kalshi (`chosen.*.capacity`,
`live_costs`):
- Kalshi uses $14 of average capital and loses $936 a year. At 10% of the volume traded in the two hours around the
  decision, it uses $32 and loses $2,136 a year.
- Polymarket uses $277 and loses $2,368 a year over the savings rate.

Polymarket taker fills sat a median 0.5¢ below the price charged, so costs are not overstated. Median flow on our side
was $14 (`fills_check_polymarket`).

## The selection bias, measured here

From `selection_bias_check`:
- 70% of members (12,632 of 17,938) traded under $10k.
- At `d1_16`, members with $10k or more resolve YES 19.9% of the time, against a price of 17.4% and a model of 15.8%.
- All members resolve 10.05%, against 10.42% and 10.07%.

So the volume filter would have manufactured a +2.5pp "underpricing". This backtest uses whole events.

## Variants

From `audit`:
- 96 pre-registered: per venue, 2 decision times × 4 edges × taker or maker × 3 bucket types;
- another 96 with a flat variance model as a robustness check, for 192 in all.

Three choices were made before any return was seen: the error shape, the settlement record (from 5 candidates) and
the seasonal variance. Polymarket maker fills are priced on hourly prices, which undercounts them.

## Errors found and fixed

1. **Old Kalshi candles.** The batch candle endpoint returns nothing for markets archived before about April 2026. Those
   were fetched one market at a time.
2. **Kalshi settlement source.** Kalshi switched to The Weather Company for markets dated from 2026-08-14. One mismatch
   remains: KXHIGHMIA on 2026-08-29, where the climate report says 85 and the market settled at 90.
3. **Polymarket's source.** Polymarket settles on METAR readings, which run 0–2°F below the climate report, so KMIA
   (Miami) has a separate model per venue.
4. **Fees.** Polymarket weather markets charged no fee until 2026-03-30. The backtest charges the current 5% throughout.
5. **Variance.** The flat-variance model was too wide in summer, so the variance is now seasonal.
6. **Series weighting.** The first daily series weighted each day equally, which showed Kalshi's pick with an in-sample
   Sharpe of 1.82 while it lost 2.3% a dollar pooled. The series is now constant-capital; neither version passes
   (`protocol_per_day_stake_series`).

## Kill criteria and what next

Reopen this only if a forecast beats the price's Brier over a rolling quarter in some city, measured before any
trading. The gap to close is 0.006–0.027 Brier, about 0.4°F of mean absolute error.

To collect next:
- **Better models.** The price at 16:00 the day before already beats the NBM issued that morning. Try hourly HRRR and
  ECMWF ensemble output, plus same-day observations.
- **Market making.** A neutral study anchored on the price, with trade-level fills and Polymarket's 25% maker rebate.
- **Decision-hour books.** The snapshots here ran 07:36–11:25 UTC; take them at the decision hours.

## Coordinator's check

All four Brier pairs and the disagreement table were recomputed from `raw/rows.json.gz`, independently of the script.
Every number reproduces exactly:
- Kalshi: n 13,469 and 11,110.
- Polymarket: n 17,437 and 16,121.
- The model-above-price and model-below-price buckets match their means and counts.

A model–market blend scores 0.1226 on Kalshi `d1_16`, worse than the market alone (0.1196). Even mixed in, the NBM
adds nothing the price lacks.

## Files

- `scripts/pm_weather.py`
- `scripts/test_pm_weather.py` (28 tests pass)
- in this folder: `analysis.json`, `tables.md`, `manifest.json`, `book_entries.json` (`[]`)
- `raw/`, git-ignored
