# Three watch items held forward: EMPD/BNC, the gold carry, the pooled money-market rotation — 2026-10-11

Three of last session's watch items needed time rather than more history. Each now has a frozen rule and an
append-only ledger, in the convention of the unlock forward test. A registered row carries its own rule and
parameters, and `score` reads them from the row, so a later code edit cannot re-score it.

| item | ledger | registered | first verdict due | today |
|---|---|---|---|---|
| EMPD and BNC (treasury companies at 0.56–0.59 of true NAV) | `research/dat_events_forward.jsonl` | 2026-10-10 23:24 UTC, before EMPD's 10-14 vote | +20 sessions 2026-11-09, +60 sessions 2027-01-07 | accumulating (0 of 4 horizons) |
| gold carry: xyz:GOLD × PAXG and HL PAXG × PAXG (cash) | `research/gold_carry_forward.jsonl` | 2026-10-10 23:32 UTC; day 1 is 2026-10-11 | 90 days (2027-01-09); promote rule runs through 2026-12 | accumulating (0 of 90 days), no kill condition |
| pooled money-market rotation (k7, h 1.0, 4-week holds) | `research/mm_rotation_forward.jsonl` | hold 1 at 2026-10-10 23:43 UTC for the 2026-10-12 decision | 6 holds (~2027-03-29) | accumulating (0 of 6 holds) |

Code: `forward register|score` in `scripts/nav_wrappers.py`; `forward register|snapshot|score|replay` in
`scripts/gold_carry.py`; `forward register|snapshot|score` in `scripts/incentive_yields.py`. Raw snapshots are under
`research/2026-10-11/watch_forward/`. All three run daily from `scripts/forward_daily.py`. Tests: 18 new, 97 pass across
the three suites.

## EMPD and BNC

- **Rule.** The study's own `dat_forward` arithmetic on holdings frozen at registration:
  - long $1 of the stock at the entry close, short h × $1 of the coin's Binance perp;
  - h = coin value / (coin value + cash − debt − preferred), capped at 3, rebalanced at each close;
  - capital 1 + h/3; stock cost per side by ADV tier, perp 5bp per side; Binance funding to the short; excess over the
    savings rate paid.
- **Entry.** The first NYSE close after registration: 2026-10-12 16:00 ET, before the 10-14 open.
- **Horizons.** NYSE sessions: +20 is 2026-11-09, +60 is 2027-01-07. 60 sessions is the study's 3-month DAT exit.
- **Read against the sector.** An equal-weight placebo basket of the other discounted DATs (SKYA, HYPD, HSDT, NAKA,
  FWDI) on the same rule, and MSTR as the benchmark.
- **Verdicts.** Kill if the mean +60 excess over the placebo is not positive. Promote only to "pre-register more
  dated-catalyst names"; n = 2 is an anecdote, not a book entry.

| | close (10-09) | coin | coins | cash | debt | true mNAV | hedge h | cost/side |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| EMPD | 3.05 | BTC 82,337.03 | 1,514 | $74M | $45M | 0.559 (0.969 with the $65M AI stake at 0) | 0.811 | 100bp (ADV $996k) |
| BNC | 5.26 | BNB 737.68 | 515,054 | $7.08M | $16.80M | 0.585 | 1.026 | 10bp |
| MSTR (benchmark) | 154.34 | BTC | 848,000 | $5.711B | $6.714B (+$13.946B pref.) | 1.187 | 1.272 | 5bp |

- BNC's Binance stock perp (BNCUSDT) was recorded at registration:
  - mark 5.3817, 2.3% over Friday's close;
  - open interest ~$8.3M, 24h volume $1.08M, $92k bids and $58k asks within 1%;
  - the last 30 funding settlements sum to −0.30%.

## Gold carry

- **Rule.** The study's own: always on, cash10 capital, one-side cost = taker fee + measured half-spread, rebalance after
  a 5% perp move, exit cost on the last scored day.

| line | capital K | short margin | perp cost/side | token cost/side |
|---|---:|---:|---:|---:|
| xyz:GOLD × PAXG | 1.12 | 12% (8.3×) | 9.12bp | 10.01bp |
| HL PAXG × PAXG | 1.15 | 15% (6.7×) | 4.62bp | 10.01bp |

- **The forward code reproduces the study exactly** (`forward replay` on the study's raw data): xyz +2.5947% (NW t
  2.233, 145 days), HL PAXG +1.6883% (t 2.172, 275 days).
- **Kill the watch** (from the findings): trailing 30-day venue funding below 5.8%; PAXG's premium to spot below −50bp
  (daily open-hours median); an xyz oracle change or GOLD delisting; a Hyperliquid halt or auto-deleveraging.
- **Today.**
  - Funding, trailing 30 days: xyz 7.50% (last 7 days 6.05%, the closest to the 5.8% line); HL PAXG 10.25% (7 days
    10.91%).
  - Perp bids within 25bp on the coarse book: xyz $1.6–1.9M, HL PAXG $0.75–0.90M (the study had $2.29M and $1.02M).
  - PAXG asks within 25bp across five books: $2.1M. Savings rate 3.80%.

## Pooled money-market rotation

- **Rule** (blue-chip k7, h 1.0, 4-week holds, curated vaults excluded):
  - top 5 of a $1M book in equal slices; a held pool stays while ranked in the top 10;
  - universe: DefiLlama Lending protocols with ≥ $1B TVL and ≥ 365 days of history, minus 8 curated-vault slugs;
  - filters: pool TVL ≥ $1M, a record within 3 days, no hack in 30 days, deposit token ≥ $0.985;
  - the study's money model and share-price audit.
- **Selection** runs through the study's own selector code on live data; yields.llama.fi/pools is public (16,831 pools;
  /poolsOld still returns 402).
- **Hold 1** (decision 2026-10-12, through 2026-11-09), 95 of 160 candidates eligible:

| slice | pool | 7-day score (base + reward) | TVL |
|---|---|---:|---:|
| 1 | Kamino OnRe Market, Solana USDG | 8.40% (8.40 + 0) | $1.07M |
| 2 | Aave v3 Monad GHO | 7.97% (5.60 + 2.36) | $4.33M |
| 3 | Kamino OnRe Market, Solana USDC | 6.36% (6.36 + 0) | $5.61M |
| 4 | Aave v3 Plasma GHO | 6.20% (3.59 + 2.61) | $1.69M |
| 5 | Kamino Huma Market, Solana USDC | 6.00% (6.00 + 0) | $2.07M |

- **Hold 1 may end in a kill.** The picks' reward APR is 0.99pp equal-weight, right at the 1pp kill line; capacity is
  $2.92M against the $2M line.
- **These are young, isolated markets.** Kamino's RWA-collateral markets date from 2026-06, Aave on Monad from 2026-07,
  Aave on Plasma from 2026-03. The post-hoc filter that removed Morpho and Euler vaults does not remove them, and the
  study's own new-venue rule was a no-go. The forward test runs the frozen rule as registered. Read its result as a
  test of that rule, not of blue-chip lending.

## Data gaps

- EMPD's 10-14 meeting date comes from ATG and press, not a filing (www.sec.gov refuses the repo's User-Agent). EMPD's
  debt sources disagree ($45M vs $10M); the conservative $45M is kept.
- Auto-deleveraging is invisible in Hyperliquid's public API. Halts show only as missing funding hours, and an oracle
  change only through a drift heuristic.
- The PAXG kill uses daily open-hours medians. An hourly −50bp trigger would already have fired in the study window
  (hourly minimum −68bp).
- Kamino pools have no share price, so their audit falls back to the deposit token's depeg. The Monad and Plasma reward
  tokens have no DefiLlama price (rewards use the in-sample 1.0075 ratio).

## Errors found in the worker's own work (all fixed)

1. A refused registration created an empty ledger file.
2. The gold snapshot kept a still-open hourly bar, and a second snapshot overwrote the first one's partial mark.
3. Gold snapshots stored full 5,000-level books (171 kB). They are now trimmed to ±1% of the best price (14 kB).
4. A test expected an exit on a 0.28% share shortfall. The rule's threshold is 1%; the code was right.
5. A daily DAT `score` would have saved megabytes of raw data each run. It now fetches only when a close newly settles.

## Coordinator's check

- **EMPD, from the raw files alone.** `yahoo_EMPD.json.gz` gives a 2026-10-09 close of 3.05.
  `binance_BTC_study_1h.json.gz` gives a close of 82,337.03 for the bar opening 19:00 UTC.
  - Inputs: 1,514 BTC, $74M cash, $45M debt, 28,160,111 shares.
  - Result: true mNAV **0.5590**, **0.9688** with the AI stake at zero, hedge **0.8113**. That matches the registered
    row.
- **Hold 1's reward APR.** From the ledger's top-10, the five picks' trailing reward APRs (0, 2.364, 0, 2.606, 0)
  average **0.994pp**. That matches the note's 0.99pp at the kill line.
