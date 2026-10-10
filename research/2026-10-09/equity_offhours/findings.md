# HIP-3 equity perps while the cash market is shut (2026-10-09)

Sample: 143 sessions (2026-03-17 to 10-08), 8,802 name-sessions over 110 markets (`scripts/equity_offhours.py`,
numbers in `analysis.json`, tables in `tables.md`). Hourly candles reach back only to 2026-03-15 (Hyperliquid serves
the most recent 5,000 bars); the carry also uses 4h bars and funding rows back to each market's listing (from
2025-10-13). 120 variants were tried; each was chosen on the first half of the sample and tested once on the second.

**Price discovery.** The perp prices the open efficiently.
- At 09:00 ET it has moved 0.90 of the close-to-open gap with R² 0.90. That holds in both halves of the sample (0.91 and
  0.90) and on weekends (0.93). The regression slope is 1.00 and the intercept −3.9bp: an unbiased predictor.
- ETF perps price 0.97, index perps 1.01, stocks 0.90.
- What is left unpriced has a mean of −3.9bp and a standard deviation of 82bp, against a mean absolute gap of 174bp.
- Share of the gap priced as the night goes on: 0.13 at 17:00 ET, 0.41 at midnight, 0.49 at 03:00, then 0.65 at 05:00
  once pre-market opens at 04:00, 0.80 at 08:00, 0.90 at 09:00.
- Against Yahoo's pre-market tape (8 names, 472 name-sessions), the opening print was 33.6bp from the perp and 44.6bp
  from the pre-market last trade. It was closer to the perp 61% of the time. How far the pre-market sits from the perp
  predicts nothing (slope 0.07, R² 0.006): the perp does not lag pre-market trading.
- Crypto-linked names price Bitcoin's off-hours move fully: regressing the unpriced gap on BTC's move gives beta 0.015
  (R² 0.001, n 776).

**Oracle and funding while shut.**
- The implied oracle (mark / (1 + premium)) moves one-for-one with the perp: median slope 1.00, and every one of the
  104 markets with enough moves is above 0.8. With no anchor, funding cannot pull the perp toward anything, and the
  oracle snaps to the stock at the open.
- Funding is mult × (P + clamp(I − P, ±0.03%)) / 8 per hour. Per venue: trade.xyz 0.5 with I = 0.01% per 8h; Paragon
  0.6; Markets by Kinetiq 1.0 with a 5% a year I. This reproduces 99.3% of 316,222 funding rows.
- Longs pay about 12.3% a year whether the market is open or closed. The premium is wider while shut: 9.8bp against
  6.1bp.
- A short held from the close to 30 minutes after the open loses 6.7bp per name-session (t −0.56 over sessions), even
  after collecting 3.9bp of funding. Equities drift up overnight (+13.2bp mean gap).

**Strategies.**
- Open-reaction rules (follow or fade the off-hours move, unhedged or index-hedged): no-go, −1.0% and −13.9% a year out
  of sample, t −0.03 and −0.39.
- Crypto-linked names against Bitcoin: no-go, −77.9% out of sample, t −1.93.
- Ex-dividend shorts: no-go, 23 events, t 1.01; the perp had already moved a median 1.08× the dividend before the open.
- Same-stock pairs across builder venues: no-go, +8.4% out of sample but t 0.73 and about $27k a year of capacity.
- **The one survivor is a carry**: short the perps whose last 30 sessions paid at least 8% a year, buy the same stocks
  at a broker, capital 1.5× notional. It works for three reasons:
  - longs pay a funding floor of 5.5% a year whenever the premium sits in the dead zone;
  - retail demand for leveraged 24/7 stock exposure keeps the premium above that zone on a persistent set of names;
  - hedging requires a stock leg at a broker, which keeps arbitrage capital thin.
- On the long history (rule chosen 2025-10 to 2026-04, tested 2026-04-14 to 10-08 on hourly marks) it beat the 3.80%
  savings rate by **3.35% a year on capital** (5.03% on notional), t 4.06, Sharpe 4.75. On the hourly-only rerun it
  beat the savings rate by 1.63% (t 1.32); all 6 carry variants survive Benjamini–Hochberg there. Out of sample the
  basket's funding was 10.9% a year and its profit after basis and dividends 11.2%, against a 5.7% capital cost
  (3.80% × 1.5). Funding persistence holds back to listing: names that paid at least 8% went on to pay 9.7% against
  6.9% for all names, positive at 8 of 8 monthly rebalances. At 5% of each basket name's open interest that is $13.5M
  notional, about **$330k–$679k a year** over the savings rate.

**Kill criteria for the carry:**
- basket trailing funding below 6.1% a year;
- out-of-sample excess negative over a trailing quarter;
- trade.xyz changes its funding parameters (the formula reproducing fewer than 95% of rows);
- any name with negative funding on more than half the days of a month.

**Risks for the carry:**
- new shorts compress the premium into the dead zone, where funding drops to 5.5% and the excess over the savings rate
  disappears;
- squeezes outside US hours hit the perp short while the stock cannot be traded (2x leverage assumed);
- the deployer controls the oracle and the listing;
- capacity is an assumption (5% of open interest), not a measurement; March 2026 funding was about zero for every
  name, so the carry has quiet regimes;
- fees: Hyperliquid's docs leave open whether the deployer's fee share is applied after the 90% growth-mode cut; the
  study assumes it is (0.9bp taker; 9bp on MSTR, BMNR and STRC, which have growth mode off).

**What next:** record pre-open book snapshots every day (the in-session books used are the 2026-09-10 snapshots);
measure how much funding falls as shorts arrive; fetch ETF dividends (Nasdaq returns none); re-test the carry monthly
against its kill criteria.

## Coordinator's check (2026-10-10)

Recomputed from the raw funding rows: over the out-of-sample period (2026-04-14 to 10-08) the final basket's ten names
averaged 12.5% a year of funding paid to shorts, longs paying in 79–92% of hours — the carry is there. What the
summary above understates is the in-sample period of the long-history run: chosen on 2025-10-14 to 2026-04-13, the rule
earned only +1.23% a year over the savings rate there (Sharpe 0.23; no variant survives Benjamini–Hochberg on the full
sample; deflated Sharpe against all variants 0.008), and the basket grew from 3–8 names to 24–31 only in June–August as
high-funding listings arrived. The out-of-sample +3.35% is therefore a summer-2026 regime more than a tested constant.
The book quotes the conservative hourly-only result instead: +1.63% a year on capital, $330k a year at an assumed 5% of
open interest, `go` unset until a further quarter confirms it.
