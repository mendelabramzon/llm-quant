# Polymarket pre-game soccer against the sharp consensus: as sharp as the books (2026-10-14)

**Verdict: no-go. `book_entries.json` is `[]`.**
- No variant of 216 passed the go rule, under either way of pricing resting orders, and none is in
  `bh_survivors_positive`.
- Polymarket's pre-game soccer prices are already as sharp as the bookmaker consensus. There is no fan premium to
  collect.

Numbers are from `analysis.json` (key in brackets) and `scripts/pm_sports_sharp.py`; tables are in `tables.md`.

## Mechanism and counterparty

The hypothesis was that fan money pushes Polymarket away from the de-vigged consensus: Pinnacle where available,
otherwise the market average, de-vigged with Shin's method. It fails at the same moment:
- **Kick-off accuracy:** Brier 0.19770 for Polymarket against 0.19772 for the closing consensus; log-loss 0.58036
  against 0.58035 (`bias.main_close_h0.accuracy`).
- **Systematic deviations,** with 95% intervals (`bias.main_close_h0`):
  - draw +0.46pp (+0.40 to +0.53);
  - underdog −0.25pp (−0.32 to −0.19);
  - home −0.09pp; away −0.18pp;
  - longshots priced 0.1–0.2: −0.13pp.
- **Popular clubs carry no premium:** −0.14pp, against −0.21pp for other teams (`bias.popular_h2`).
- **Extra leagues** (2h before, against closing odds) show a mild favourite–longshot tilt. Favourites at 0.7–0.8 sit
  −1.15pp; longshots +0.4 to +0.7pp (`bias.extra_close_h2`).
- **Tennis** favourites sit −0.22pp (`bias.tennis_close_h1`).

Every one of these is below one-way costs: a half-spread of 0.5–1.5pp plus a fee of about 1.2pp at a price of 0.3.
Whoever prices Polymarket's pre-game soccer is watching the same books.

## Headline numbers

**Matching** (`match.stats`):
- 3,244 main-division and 2,032 extra-league matches: 95.1% of in-scope events, 98.5% in the main divisions.
- 5,275 resolutions agree with football-data's result and 0 disagree.
- A hand-checked sample of 40 was all correct.

**Run A** (pre-registered; maker fills priced on an hourly-midpoint proxy) (`selection`, `go_rule`):
- The choice was `maker|h2|thr0.00|draw|top5`.
- It made +1.17% a trade in sample (595 trades) and −1.38% out of sample (546 trades): HAC t −1.21, rank 166 of 216.

**Run B** (maker fills priced on real prints) (`protocol_fills.selection`):
- The choice was `maker|h24|thr0.03|fav|top5`.
- It made +15.1% in sample and −2.4% out of sample: t −0.26, rank 117.

**Takers:** buying every outcome at a zero threshold, 2h out, lost 7.7% a trade over 1,414 trades, against an expected
+4.9% (`variants`).

**Look-ahead** (`sensitivity.grid_mean_ret`):
- The mean variant returns −5.2% using pre-closing odds and +4.6% using closing odds, about 10pp a trade of look-ahead.
- Pre-closing odds are 15h to 3 days old at decision time, and Polymarket already beats them (Brier 0.1972 against
  0.1974 at 2h).

**Adverse selection:** filled maker orders have negative closing-line value, −2.6% in run A and −1.3% in run B.

**Costs confirmed:** the median taker buy was 0.005 above the midpoint, exactly the modelled half-spread
(`trades_check`).

## Late entry (+1h, at the later price)

- Run A's choice, out of sample: −1.38% becomes −0.98% (0.71 of a negative edge).
- Run B's choice: +6.2% becomes +6.8% over the full sample (1.10), and −2.4% becomes −1.05% out of sample (0.44).
- Neither has a positive out-of-sample edge to keep.

## Capacity

- Depth at the best ask is $526–1,801 in the top five leagues and $33–104 in other main divisions
  (`depth_model_usd_best_ask`).
- The median taker buy within an hour of entry is $298 (`trades_check`).
- Run A's choice: −$12.7k a year out of sample (−$12.8k against the savings rate).
- Run B's choice shows +$7.9k a year over the savings rate on $11.4k of capital, but only stake-weighted. Its
  equal-weight mean is −2.4% (t −0.26), so it is noise.

## Variants

559 were tried (`n_variants_tried`):
- 216 pre-registered;
- 108 maker variants re-priced on prints;
- 216 in a disclosure re-run on the uncorrected universe;
- 12 post-hoc same-time variants;
- 5 sensitivities;
- 2 re-selections by execution type.

## Errors found and fixed

1. **The $10k-volume universe filter** (from the coordinator's note). 2,350 of 5,276 matched events were missing members
   (`universe_selection`).
   - Universe members of incomplete events resolved YES 48.1% of the time, against a 39.9% midpoint: +8.2pp (+6.7 to
     +9.6).
   - The re-added members resolved 17.7% against 26.4%.
   - After rebuilding every event from gamma, the result is 33.34% against 33.34%.
   - Keeping only complete events would also select on outcome. Event-level selection is mild, about 1 standard error.
   - The uncorrected backtest would have flattered the taker grid by 3.5pp a trade.
2. **The maker fill proxy.** It filled 9 of 300 sampled signals where real prints went through the limit 104 times. The
   maker family was re-priced on prints for all 9,669 members.
3. **Kick-off mismatches.** 20 matches had Polymarket kick-offs that disagreed with football-data, some played a day
   earlier, so their "pre-game" midpoints were already 0.001 or 1.0. They were dropped.
4. **Name matching.** NFKD normalisation dropped æ, ø and ı. "Real" alone matched Real Madrid to Real Sociedad, so
   generic tokens are now down-weighted. Rennes and Sporting aliases were added, plus edit distance for Greek
   spellings.
5. **Data access:**
   - tennis-data's plain URL is a parked domain; the real files sit under an obscured path.
   - The 2026-10-09 half-spread table covered only 0.85–0.995 favourites, so a tier-specific table was built from
     today's books.
   - football-data's Pinnacle columns stop after January 2026, so 2,828 of 3,244 decisions used the market average.
6. **Not done:**
   - Kalshi's public settled-markets endpoint returns only August–October 2026.
   - The free US-sports odds archive (aussportsbetting.com) sits behind a Cloudflare challenge.

## Kill criteria and what next

**Main-league pre-game soccer is dead.** Reopen it only if, over a rolling quarter, Polymarket's kick-off Brier is worse
than the closing consensus by more than 0.002 (interval excluding zero), or a role deviates by more than 1.5pp.

**Resting draw bids: forward test only.**
- `maker|h24|thr0.00|draw|all` made +4.2% a signal in sample and +3.7% out of sample: t 1.64, not a false-discovery
  survivor.
- It matches a period effect: draws beat the consensus by 1.4pp across all football-data fixtures.
- Kill it if the quarterly draw rate returns to the consensus.

**Same-time trading.** The post-hoc family (Polymarket's kick-off midpoint against closing odds) made +4.7% ± 7.3% a
trade over 487 trades (`exploratory_same_time`). Testing it needs a live sharp feed (Betfair or Pinnacle) logged in the
same minute as Polymarket's books. It is likely stale-quote sniping around team news, which is the speed game this repo
excludes.

**Kalshi against Polymarket on US sports** needs a paid closing-line archive.

## Coordinator's check

The kick-off accuracy was recomputed independently of the script from `raw/matches_full.json.gz` and the price series in
`raw/prices/`:
- main divisions only;
- Polymarket's hourly midpoint at kick-off + 2 minutes, at most 36h stale;
- fair value from the closing odds, de-vigged by my own Shin implementation and by the multiplicative method.

The result: n 9,410 member outcomes, Brier 0.19681 for Polymarket against 0.19730 (Shin) and 0.19734 (multiplicative)
for the consensus. The script reports n 9,668, 0.19770 and 0.19772. The gap in n comes from member and staleness
selection. Both computations reach the same conclusion: Polymarket's kick-off price is at least as accurate as the
de-vigged closing consensus.

## Files

- `scripts/pm_sports_sharp.py` (subcommands odds, live, match, complete, prices, tennis, prints, trades, analyze, render)
- `scripts/test_pm_sports_sharp.py` (40 tests pass)
- in this folder: `analysis.json`, `tables.md`, `manifest.json`, `book_entries.json` (`[]`)
- `raw/` (134 MB, git-ignored)
