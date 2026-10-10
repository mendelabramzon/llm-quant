# The XYZ oil carry is the roll yield, and it is priced — 2026-10-09

The book's largest line, `hip3-oil-funding-carry` ($2.84M a year at capacity), was priced from one window on
2026-09-10 and a 47-hour out-of-sample test. This study re-prices it over every roll since 2026-07-01, hour by hour,
with the hedge leg taken from the actual futures (`scripts/roll_carry.py`; Hyperliquid funding and candles from
`research/2026-10-09/perps_hip3`, futures from Yahoo's chart API by contract month; numbers in `analysis.json`,
tables in `tables.md`). **The line is retired.** The funding is real, but it is the price of the oracle's roll, and the
hedged position that collects it collects slightly less than the roll costs.

## 1. The oracle rolls on the GSCI schedule

All three energy oracles (Brent, WTI, Henry Hub gas) are a blend of the front and second futures whose front weight
falls **a fifth of the way each day, at the Globex reopen (22:00 UTC in US daylight time), on the 5th to 9th US
business days of the month** — the S&P GSCI roll convention. The weight read from the venue (oracle = close / (1 +
premium), placed between the two contracts) went 1.00 → 0.80 → 0.60 → 0.40 → 0.20 → 0.00 on 2026-09-08, 09, 10, 11
and 14, and 1.00 → 0.80 → 0.60 on 10-07, 08 and 09; October's last two steps fall on 10-12 and 10-13. The schedule,
written down as code (`roll_steps`, `predicted_weight`), predicts the measured weight within 0.1 on 99.0% (Brent, 486
hours), 98.9% (WTI, 756) and 99.5% (gas, 594) of the hours where the curve resolves it, median absolute error
0.003–0.006. July's roll shows in the gas funding on 07-08..14 and August's in all three on 08-07, 10, 11, 12, 13.
Between rolls the oracle sits entirely on the next contract and the funding is near zero; when the rolled-out
contract expires the calendar's front becomes that contract and the weight reads 1.00 again.

Three statements in the 2026-09-10 note were wrong, and this is why:

* **"A tenth of the spread per trading day."** It is a fifth. The 09-10 reading came from the 22:00 UTC funding row,
  whose premium is an hourly mean that straddles the step and so shows about half of it (the weight reads 0.875 in
  that hour and 0.80 the next).
* **"The regime is eleven days old."** The roll happens every month. What changed in September was the calendar
  spread — Brent's front-to-second backwardation widened to 4–5% — and the funding scales with it: about 150% a year
  on August's roll days, 280–340% on September's, 190–220% in October with a 3% spread, and 635–680% paid to gas
  shorts in October with a 9% contango.
* **"+145bp hedged out of sample in 47 hours."** That was the oracle-hedged proxy, which hedges with the oracle itself.
  The oracle's step is exactly what no tradeable hedge shares: a futures position does not lose a fifth of the spread
  at 22:00 UTC; an index that rolls does. The proxy left the cost of the trade out of the trade.

## 2. The funding pays for the step, and not quite all of it

Over the 24 hours that end at each step, the side the curve pays collected **a median 0.92 (Brent), 0.97 (WTI) and
0.89 (gas) of the step** (seven steps each with both futures legs; `funding_vs_step`). That is what a market that
prices the roll looks like: the book trades the blend ahead of the oracle (the premium builds from about −0.3% after
a step to −1.0% before the next), the funding at half of premium/8 an hour returns roughly the day's roll-down, and a
long hedged with the futures blend ends each window about flat before costs.

Holding the paid side through each roll with the futures blend as the hedge (re-weighted at the start of each UTC
day to the weight the oracle showed), the per-window result — no parameter fitted, the side is the sign of the curve
and the window is the published schedule:

| roll | entry | Brent gross / net | WTI gross / net | gas gross / net |
|---|---|---|---|---|
| Sep, enter 21:00 before the first step | eve | −0.04% / −0.18% | −0.07% / −0.22% | −0.66% / −0.81% |
| Sep, enter 00:00 on the first roll day | day | −0.96% / −1.11% | −1.29% / −1.44% | −0.50% / −0.64% |
| Oct (three of five steps so far) | eve | −0.16% / −0.31% | +0.02% / −0.13% | −0.15% / −0.30% |

Net is after one perp round trip at $100k (12.6bp, the 09-10 book) and 1bp each way on the future. The September
funding collected was 3.1–3.5% of notional per window; the hedged basis took 3.1–3.9% back. July and August cannot be
hedged with the blend from this data (Yahoo drops a contract when it expires, so their second month is gone); with the
front alone as the hedge they scatter between −1.6% and +1.6% per window, which is the spread's own noise.

A rule fitted the usual way says the same. Choosing a trailing-funding entry threshold on the hours before the book's
2026-09-10 quote (12 variants per market, front-only hedge) and testing it after: Brent −1.07% over the month (held
133 of 704 hours, Newey–West t −1.23), WTI −1.08% (t −1.17), gas −0.44% (t −0.65); every chosen variant had a deflated
Sharpe under 0.3 in sample. Unhedged, the same positions made +61% and +60% a year on Brent and WTI — oil rose — which
is the oil beta the strategy was supposed to remove, not carry.

## 3. Verdict and corrections

* `hip3-oil-funding-carry`: **retired**. Quoted at −4.8% a year on notional (the mean September net per window, −0.40%,
  times twelve windows), `go` no. Kill evidence: the funding-to-step ratio and the schedule fit above.
* `perp_scan.py` `roll_premium`: the step is now a fifth of the spread per roll day (`--roll-days 5`); on the 09-10
  Brent snapshot the detector now nets the funding to 42% a year before the round trip and declines it after, and a
  positive control (funding at 0.1% an hour) still fires (`test_perp_scan_roll.py`).
* The metals are controls and behave like it: gold, silver and platinum held no position under any chosen rule; copper
  and palladium made +0.05% and +0.70% out of sample with t-statistics of 0.39 and 1.18.

## 4. What is left, and what to collect

* The ratio sits below one in 18 of 21 steps. If that persists, the side that *pays* (short the perp in
  backwardation, long the futures blend) keeps about a tenth of each step — roughly 0.1 × the spread per window
  before a 0.15% round trip, positive only when the spread is wide (gas in October). That is a hypothesis from seven
  steps, not a strategy; the daily pass now carries the corrected detector, and `roll_carry.py analyze` re-run after
  each roll (next: 10-12/13, then 11-06..12) will say whether it holds.
* A contract-month futures source that keeps expired months would let July and August be hedged properly; Yahoo does
  not. EIA publishes WTI contracts 1–4 daily (`RCLC1..4`) if a daily hedge is enough.
* Brent depth at 25bp was $1.77M on 09-10; nothing here needed it, because nothing here clears its costs.
