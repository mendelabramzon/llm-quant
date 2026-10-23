# Crypto price markets against Deribit options: the option surface is the worse forecast (2026-10-14)

**Verdict: no-go. `book_entries.json` is `[]`.**

The question was whether Polymarket and Kalshi crypto markets ("above X on date", range buckets, "what price will
Bitcoin hit") misprice relative to Deribit's options. They don't, in any way we can trade:
- **Strikes and ranges** track the option-implied distribution to about 1–3c, with no consistent sign.
- **Touch markets** trade *below* the option-implied touch probability, and the outcomes side with the market.
- **No variant passes.** None of the 288 pre-registered variants survives the one-sided false-discovery test, and the
  variant chosen in sample lost out of sample (HAC t −1.46).

Every number is in `analysis.json` (key in brackets), produced by `scripts/pm_crypto_options.py`. Tables are in
`tables.md`.

## Why the hypothesis failed

The hypothesis was that retail traders price touches without a vol surface. In fact, Deribit's surface is a
risk-neutral price that carries a variance risk premium.

Over each decision's remaining window, realised vol (Binance, hourly) was below implied vol in:
- 68% of strike decisions;
- 77–79% of touch decisions.

The median realised/implied ratio was 0.86 for strikes and 0.67–0.78 for touches (`vrp`). Touch probabilities are the
most vol-sensitive, so the option model overstates them. Polymarket sits between the model and reality. For weekly
touches the model said 0.118, the market 0.098, and the outcome was 0.093 (`calibration['touch_week|all']`). The
counterparty to beat would have been the option sellers' risk premium, not uninformed retail.

## Headline numbers

The sample is 11,209 decisions on BTC/ETH markets in 1,247 events, April 2025 to October 2026
(`decisions_by_kind_h`).

**The market has the lower Brier score in every family** (`calibration[*].brier_market` vs `brier_model`):

| family | market | model |
|---|---:|---:|
| strike | 0.1144 | 0.1152 |
| range | 0.1377 | 0.1396 |
| daily touch | 0.0491 | 0.0494 |
| weekly touch | 0.0613 | 0.0635 |
| monthly touch | 0.0360 | 0.0371 |

**When model and market disagree by 5c or more, the outcome lands on the model's side only sometimes**
(`disagree_5c.share_outcome_on_model_side`):
- strikes 49% and ranges 54%, about a coin flip;
- daily touches 30%, weekly 22%, monthly 25%.

**Mean absolute deviation, market minus model** (`mad_history`; signed values in brackets):
- strikes 1.9c (+0.05c);
- ranges 2.9c;
- daily touches 2.4c;
- weekly touches 2.6c (−2.0c);
- monthly touches 1.5c.

At 1–2 sd from the barrier the touch markets sit −4.9c (weekly), −3.6c (monthly) and −2.5c (daily) below the
model.

**Live at 07:47 UTC today** (`live.by_venue_kind_hours`):

| venue | strikes | ranges | weekly touch | monthly touch |
|---|---:|---:|---:|---:|
| Polymarket | 1.0c | 1.3c | 7.6c (−2.8c) | 1.9c (−1.7c) |
| Kalshi | 1.3c | 1.1c | — | 2.7c (−1.7c), one-touch |

Live half-spreads are 2–3c on mid-priced strike and range books and 0.5–1c on touch books, plus the 0.07·p(1−p)
taker fee (`half_spread_live`).

**The protocol pick lost** (`protocol`):
- The pick was `range|72h|thr0.02|yes|taker`: 14 trades in sample at +178% a trade, then 2 trades out of sample,
  both lost.
- It ranked 207 of 288 out of sample, with a deflated Sharpe of 0.065. `bh_survivors_positive` is empty.
- The 8 two-sided survivors are all weekly-touch maker YES variants, and all lose significantly. For example,
  `touch_week|72h|thr0.02|yes|maker` lost 41.7% a trade in sample and 74.5% out of sample, winning 9% of trades.
- The model's touch signal points the wrong way.

**The touch approximation holds.** The reflection formula at the barrier-strike vol agrees with a 5-minute Monte Carlo
to within about 1 point (0.157 against 0.166 ± 0.006, and 0.157 against 0.149). It also agrees with twice the flat
digital (`touch_check`).

## Late entry, hedge and capacity

- **Late entry (+1h):** the 2 out-of-sample trades lost either way. "Share kept 1.0" is a share of a −100% edge
  (`late_entry`).
- **Delta hedge** (perp, hourly, 5bp fee): −108% against −100% unhedged on the same 2 trades (`hedge_overlay`). A hedge
  cannot fix the sign.
- **Capacity:**
  - The median trade is $394 when sized at the touch depth and capped at 10% of daily volume. That gives **−$1,580 a
    year over SSR** (`capacity`).
  - Median touch depth is $533 for mid-priced strikes and $546 for weekly touches, and under $35 in the tails.

## Variants

There were 291 variants in all:
- 288 pre-registered;
- the late-entry and hedge overlays;
- one post-hoc test.

The post-hoc test was added after seeing the calibration table: buy NO on weekly and monthly touches 0.5–2 sd from
the barrier. It returned −1.7% a trade in sample and +4.0% out of sample, with t 0.86 (`post_hoc_sell_touch`). It is
not significant.

## Errors found and fixed

1. **Touch strikes added mid-window count only from their creation.** The rule says "price action before this market's
   creation will not be considered". The first live read put the model at 1.0 on three open markets, such as ETH
   $2,700 in October. The window start is now the later of the window's opening and the market's creation.
2. **Deribit inverse options are priced Black76(F)/F.** Dividing by the index instead left the call- and put-implied
   forwards 13–30bp apart at 1–3 months.
3. **The question's 12:00 ET clock now sets the resolution time.** For 732 of 24,220 markets, `endDate` disagreed with
   the rule's clock by up to −744 h.
4. **SOL and XRP live surfaces were empty** because a USDC index name was wrong.
5. **Kalshi's 4am hourly events had leaked into the live table.** They were dropped: the table keeps only the 5pm
   daily events and markets at least 6h out.
6. **The stored universe's $10k volume filter biases outcomes.** It over-represents winning range buckets: the outcome
   rate is 0.183 against a market price of 0.131. This explains the in-sample pick, and it affects every study that
   draws members of multi-outcome events from `research/2026-10-09/polymarket_history/raw/universe.json.gz` (see
   Coordinator's check).

## Caveats

- **Price fetching stopped early, for time.** 2,740 of the 8,291 selected markets got price series. Strike and range
  decisions lean on the 2026-10-09 stratified sample, and daily touches are partial.
- **SOL and XRP have only a live model.** There is no historical model for them.
- **Kalshi is compared live only.** Two snapshots were read, and there is no Deribit window at 21:00 UTC for history.
- **Spreads were read in Asian hours,** about 07:45 UTC. That does not change the verdict: the touch edge has the wrong
  sign before costs.

## Kill criteria and what to collect next

Nothing is in the book. Reopen the study if either of these happens:
- a variance-adjusted model beats the market's Brier score on touch markets over a forward month (implied vol scaled by
  a trailing realised/implied ratio, fitted only on 2025);
- live touch markets trade more than 3c *above* the option model.

What to collect next:
- maker fills on the NO side of touch markets (data-api trades), to test selling the touch without the fee;
- Kalshi 5pm-ET history with matching Deribit windows;
- books in US hours.

## Coordinator's check

All five families' calibration rows were recomputed from `raw/decisions.json.gz` (11,209 rows), independently of the
script. Every number reproduces exactly:
- weekly touches: n 3,740; outcome 0.0933; model 0.1183; market 0.0983; Brier 0.0635 for the model against 0.0613 for
  the market; 22.5% on the model's side when they disagree by 5c or more;
- strikes: 0.1152 against 0.1144;
- ranges: 0.1396 against 0.1377;
- daily touches: 0.0494 against 0.0491;
- monthly touches: 0.0371 against 0.0360.

The range family's outcome rate of 0.183 against a price of 0.131 is the volume-filter bias, not an edge. The running
weather, structure-scan, sports, wallet-skill and rewards workers were told to select whole events, fetching members
under $10k from gamma, before any member-level calibration.

## Files

- `scripts/pm_crypto_options.py`
- `scripts/test_pm_crypto_options.py` (12 tests pass)
- in this folder: `analysis.json`, `tables.md`, `manifest.json`, `book_entries.json` (`[]`), and `raw/` (git-ignored)
