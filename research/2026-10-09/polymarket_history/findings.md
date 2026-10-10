# Polymarket from its history: favourites, neg-risk sums and the resolution lag (2026-10-09)

The question was whether any of three common prediction-market claims makes a strategy at real size. The claims are
that favourites are underpriced, that neg-risk baskets sum to less than a dollar, and that you can buy a decided market
at 99c and wait for it to settle. The answer is no for all three.

The one edge that is statistically real is the resolution lag on crypto-price markets. Out of sample it won every
trade, with a HAC t of 5.33. But Polymarket automated its settlement during 2026, and the pool this edge draws on fell
from $1–3k a day to a few dollars a day. `book_entries.json` is therefore empty.

Every number is from `analysis.json`, `lagflow_crypto_price.json` or `trades_check.json`
(`scripts/polymarket_history.py`). The tables are in `tables.md` and the provenance is in `manifest.json`.

## What was collected

- **The resolved universe.** 446,503 closed markets with at least $10k of volume, from the gamma keyset endpoint (4,466
  pages, no errors).
  - 444,931 are binary with a clean resolution.
  - 1,745 resolved 50-50 and 1,472 were disputed at least once.
  - 95 binaries closed without a resolution and are excluded.
  - 77% closed in 2026.
- **Price histories for a stratified sample.** The sample has 25,483 markets, and 24,973 of them have a price series.
  - Each (category, volume bucket) stratum is capped at 3,000, 1,500 and 800 markets for the $1M+, $100k–1M and
    $10k–100k buckets.
  - Markets are drawn by a hash of their id, and every statistic is weighted back to the universe.
  - Each market has a 12-hourly series over its life and an hourly series over its last 14.5 days.
- **Four live snapshots on 2026-10-09** (20:06, 20:09, 20:23 and 20:41 UTC). Each covers about 10,400 neg-risk events
  and about 4,800 binary favourites. Only the last two filter on neg-risk membership and re-read candidates atomically,
  so only they are used for strategy B.
- **Fills.** Taker trades within ±30 minutes of 506 sampled backtest entries.
- **Lag flow.** Every taker trade between the scheduled end and the close, for 592 sampled crypto-price markets.

## Measurement facts that changed answers

- **A `prices-history` point is a midpoint, not a fill.** Half-cent values outnumber whole-cent values: 31,774 against
  19,205 of 99,642 points in 400 series. That only happens when the price is the midpoint of a one-tick spread. Every
  trade therefore pays the live median half-spread for its category and price band, plus the taker fee.
- **Fees are new and now nearly universal.** The share of closing markets that charge fees was 0.1% in December 2025,
  24% in January 2026, 91% in April and 99% from May. The fee is `feeRate × p × (1 − p)` per share, charged to takers
  only; geopolitics markets are free. The current schedule is charged to every trade, including historical ones that
  paid nothing.
- **For sports, the scheduled end is the game's start.** The median of `endDate − gameStartTime` is 0.0 h over 164,159
  markets. So "after the scheduled end" means in-play.
- **Gamma ignores the `negRisk` filter on events, and offset paging stops at about 2,100 rows.** The first snapshot
  therefore counted date ladders as neg-risk sets. Neg-risk membership is now taken from each event's own `negRisk`
  flag, and events are paged by keyset.
- **A book sweep is not simultaneous.** West Ham–QPR's three books were read at 20:13:10, 20:15:52 and 20:18:43 UTC,
  during the second half (`raw/live/snap_1791576591.json.gz`). Their bids summed to 1.06, which looked like a $16
  riskless NO basket. The jump in QPR's bid was a goal, not an arbitrage. Every candidate is now re-read in a single
  request.
- **The savings rate is 3.80%,** read on chain, and used as USDC's opportunity cost for the whole period.

## A. Buying the favourite ("high-probability bonds"): no-go

The test buys the favourite at a fixed horizon before the scheduled end, inside a price band, and holds it to the
close. There are 25 variants (5 horizons × 5 bands). The best is chosen on markets that closed before 2026-01-01 and
tested once on entries after that date. 62 variants were tried in all.

- **In sample the market is calibrated; out of sample short-horizon favourites were overpriced.**
  - In sample, the slope of logit(win) on logit(price) is 0.92–1.29, and every interval includes 1.
  - Out of sample, short-horizon favourites were overpriced: 0.81 (0.68–0.93) at 3 days and 0.83 (0.69–1.00) at 1 day.
  - At 30 days the out-of-sample slope is 1.41 (1.06–1.74).
- **The variant chosen in sample lost out of sample.**
  - The protocol chose the 30-day horizon, 0.98–0.995 band: 396 trades, all won, +5.9% a year over the savings rate.
  - Out of sample it made 447 trades, won 99.3%, and returned −5.1% a year (event interval −15.6% to +2.5%). It ranked
    8th of 25, with a HAC t of −0.90.
  - With no spread and no fee it would have made +1.5%, so the whole edge is smaller than the spread.
- **Short horizons lost.**
  - At 1 day in the 0.85–0.995 band, favourites won 90.7% and the average trade returned −5.16%. This survives the
    false-discovery test as significantly negative.
  - Sports favourites won 87.1% against prices averaging 0.922 (gross −5.7% a trade). Weather favourites won 90.1%
    against 0.948 (gross −5.1%).
  - The sports losses are props around the 2026 World Cup (exact score, over/under), where one longshot per match pays.
  - The sports sign flipped: in 2024–25, sports favourites won 96.6% against 0.939.
  - Weather at 1 day was negative in both periods (gross −3.0% in sample), but this was only checked after the
    category split. It is a forward-test candidate, not a finding.

## B. Neg-risk sums: no-go

Two re-read snapshots, about 10,400 events each.

- **Clean events.** These are events that are not augmented and whose untradable members are all closed: 15,895
  event-snapshots.
  - The median sum of asks is 2.54 and the median sum of bids is 0.67.
  - Asks summed below 1 in 25 event-snapshots, and bids above 1 in 11.
  - Walking the books and paying fees, 8 baskets were profitable: $1.20 per snapshot on $151 of capital.
  - None beat the savings rate once annualised to the event's end, because all were long-dated (448, 114 and 83 days).
- **Augmented events are bets, not arbitrages.** Asks summed below 1 in 430 event-snapshots, but only because the named
  outcomes leave out "Other" and the placeholders. For example, 23 named outcomes in Lebanon's election cost $0.043 in
  total.
- **Incomplete events.** The 3 Guinea-Bissau hits have a suspended member, so the basket does not cover every outcome.
- **History is only an upper bound, because midpoints sit below asks.** It covers 278 clean events with at least $1M of
  volume. The median event sum is 1.013, and 3.7% of grid points are below 0.98. All 278 resolved with payouts summing
  to exactly $1.

## C. Resolution lag: no-go pooled; real on crypto prices, then automated away

- **Pooled across categories it lost at every threshold.**
  - Out-of-sample returns were −0.20% to −0.93% a trade.
  - The side priced at 0.95 still lost 2.07% of sports trades (in-play), 2.72% of weather, 1.99% of elections and 2.02%
    of politics.
- **Split by category, crypto prices never lost.** The split was added after the pooled result was seen; this is
  disclosed and counted in the 62 trials.
  - Chosen in sample (the 0.99 threshold on crypto prices): 382 trades, all won, +0.15% a trade.
  - Out of sample: 106 of 106 won (96 events), +0.11% a trade net, held about 3 hours. It ranked 2nd of 32, with a HAC t
    of 5.33 and a deflated Sharpe of about 1.0. All four crypto-price thresholds survive the false-discovery test.
  - The cost assumption holds: the median taker fill was at the midpoint (62 of 106 entries had fills).
- **The pool is gone.** The pool is what takers who bought the eventual winner after the scheduled end collected.
  - $742 a day in 2024–25, then $188 a day in 2026, spread across 879 wallets with the top 5 taking 29%.
  - Month by month: $1.2–3.1k a day from November 2024 to June 2025, then $2.6–25 a day from May 2026.
  - The mean lag between scheduled end and close fell from about 13 h to 0.27–1 h.
  - Of the 1,881 crypto-price markets that closed in September–October 2026, the median closed 0.23 h after its
    observation, all auto-resolved.
  - Live depth supports $408 of capital, which earns $1,287 a year.

## Caveats

- **Liquidity at entry.** Midpoints are not fills, and the fill check covers only part of the sample. For strategy A,
  24 of 32 sampled entries had no taker buy within 30 minutes.
- **Closed markets only.** The universe excludes markets still open, so markets that resolve slowly late in the sample
  are under-represented.
- **Volume buckets are measured after the fact.** Surprises attract volume, which makes A's results conservative.
- **Clustering is by Polymarket event.** One match's props can span several events, so the sports confidence intervals
  are too narrow.
- **Up/down family untested.** It had 26 in-sample and 25 out-of-sample trades.

## Kill criteria, revival triggers and what to collect next

- **Crypto-price resolution lag (retired).** Revive it if `lagflow` shows a median close-minus-end above 1 h for a week,
  or a monthly pool above $500 a day.
- **Neg-risk.** Act only on a re-read clean basket whose fee-paid profit, annualised to the event's end, beats the
  savings rate on more than $10k.
- **Favourites.** Act only if the 1-day or 3-day calibration slope is above 1.2, with an interval excluding 1, over a
  rolling quarter, net of the spread.
- **Next collection.**
  - Order-level data for maker strategies.
  - A websocket book feed for in-play neg-risk sums.
  - A forward test, with maker fills, of whether longshots were underpriced on World-Cup-scale props and weather
    markets.
