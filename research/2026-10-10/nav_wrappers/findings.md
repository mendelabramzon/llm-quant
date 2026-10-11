# Wrappers that trade away from what they hold: OTC crypto trusts and treasury companies — 2026-10-10

Listed vehicles that hold crypto but cannot be redeemed by their holders trade away from their holdings: OTC trusts
(the GBTC trade) and, since 2025, digital-asset treasury companies (DATs). Holders who need out sell at a discount; a
conversion, buyback, merger or liquidation may close it.

**Answer.** Buying a discount with the coin hedged paid well above the savings rate once, in the 2021–24
trust-conversion regime (GBTC, ETHE). It does not pay as a general rule today.

- **Trusts.** After the SEC's generic listing standards (2025-09-17), new conversions were fast and trusts traded at
  *premiums*.
  - The entry rule chosen on GBTC/ETHE never triggered on a single-coin trust after that.
  - What survives is a daily rule on thin OTC trusts: statistically real but worth about $0.16M a year at a realistic
    size. Most of that came from one trust (ZCSH) that has since listed.
  - Entered as a **standby (go = no)**.
- **DATs.** A deep *true* discount did not predict hedged convergence over 1–3 months, out of sample, with or without
  the names whose data failed checks. **No-go.**
- **Dashboards mislead.** Five of 18 "discounted" DATs are premiums once debt and preferred count. Several deep
  "discounts" rest on stale holdings.
- **Live candidates** exist at 0.35–0.69× true NAV in names trading $0.5–11M a day. Only one has a dated catalyst
  (EMPD's 2026-10-14 vote), and its real discount is ambiguous.

| part | verdict | out of sample | now | size |
|---|---|---|---|---|
| (a) entry rule chosen on GBTC/ETHE (discount ≥30%, filing pending) | never triggered on single-coin trusts | 0 trades | no pending trust at ≥5% | — |
| (a) daily rule: any OTC trust at ≥5% discount, dollar hedge | **standby, go = no** | +20.8%/yr over savings rate, t 1.80, rank 1 of 8, deflated Sharpe 0.93, survives BH | LTCN −4.8%, BCHG −4.6% | ~$0.55M; +$164k/yr in test |
| (b) DAT true-mNAV < x, beta hedge | no-go | +0.2%/trade (t 0.09); without flagged names +1.7% (t 0.49) | — | — |
| (b) dashboard (naive) mNAV < x | no-go | −1.4%/trade (t −0.66) after +2.8% (t 3.44) in sample | — | — |
| (b) events (buybacks, coin sales, activists) | no-go / watch | no drift after buybacks; coin sales −39%/60d (n=3) | EMPD vote 10-14 | ~$0.5M |

## Data and method

`scripts/nav_wrappers.py` (collect / analyze / render). Curated events and overrides, each with a source, are in
`curated.json`; sources and gaps are in `manifest.json` (71 URLs).

**Trusts.**

- 23 OTC or converted trusts.
- Coin per share comes from each trust's 10-Q/10-K XBRL (units ÷ shares) and is carried between filings at the sponsor
  fee.
- NAV per share = coin per share × the Binance price at 16:00 New York.
- Hedge: a short of the coin's Binance perp, with its funding.
- Conversion dates come from the EDGAR filing index (S-1/S-3, 8-A12B, first 424B3) and press releases.

**DATs.**

- 41 screened; 32 have daily look-through series.
- Holdings: StrategyTracker's daily ledger (20 BTC treasuries) or CoinGecko's weekly chart (the public API allows 365
  days).
- Cash, debt and preferred: from the *original* 10-Q/10-K, used only from the filing date onward.
- Three ratios:
  - naive = market cap ÷ coin value;
  - EV = Strategy's definition;
  - true = price ÷ (coins + cash − debt − preferred) per share, convertibles counted as shares only when in the money.

**Protocol.**

- Trust entry variants were chosen on GBTC/ETHE and tested on the 2024–26 conversions.
- Daily trust rules: 8 variants × 2 hedges, chosen on 2019-09 to 2024-12, tested on 2025-01 to 2026-10.
- DAT rules: 18 variants per signal and hedge, chosen on weeks before 2026-04-01.
- Event holding windows were chosen on events before 2026-01-01.
- Costs: ADV-tiered spreads (trusts under $1M ADV pay at least 1% per side) plus 5bp on the perp. The short's margin is
  1/3 of notional.
- Benchmark: the savings rate actually paid each year (2026: 3.7%).
- Capacity: 10% of 60-day dollar volume over 5 days.

**Worker's independent checks.**

- *Trusts:* the computed NAV against the sponsor's published NAV per share agrees within a median 0.03–0.44% across
  4–27 quarter-ends per trust (GBTC 0.05% over 27).
- *Strategy (MSTR)*, from three or four sources each:
  - BTC: 848,000 / 847,999 / 846,000 (10-Q) / 844,504 (10-Q fair value ÷ price).
  - Preferred: $14.15B / $13.95B / $14.44B.
  - Debt: $6.714B / $6.710B.
  - Shares: 422.07M / 421.98M.

## Results — (a) trusts

**Early conversions (in sample).** Long the trust, short the coins it holds.

| | filed | discount at filing | trough | at first exchange close | excess on capital | per year | 1 day late keeps | 1 week late keeps |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GBTC | 2021-10-19 | −18.3% | −48.7% (2022-12-13) | −1.3% (2024-01-11) | +17.8% | +8.0% | 89% | 77% |
| ETHE | 2023-10-02 | −31.8% | | +0.2% (2024-07-23) | +43.1% | +53.3% | 102% | 91% |

GBTC's daily volume at filing was $282M.

**Later conversions (tested).** The discount ≥30% rule (chosen in sample at +29.9% a year) never triggered.

- GSOL and GLNK were at **+98% and +100% premiums** when they filed. GTAO filed at +108% and is still pending.
- OBTC: −3.3% when Bitwise's deal was announced; +0.4% excess by listing.
- ZCSH: −17.6% at filing, 0 at listing 2026-08-25. +7.5% with the coin-holdings hedge, −0.7% with the dollar hedge.
- The pattern did recur in two basket trusts, quarter-end data only: GDLC at −36.7% and BITW at −37.0% on 2024-09-30,
  both about 0 after listing (2025-09-19, 2025-12-09). There is no daily NAV for baskets, so no return was computed.
  Volume at filing was $1.2M and $3.3M a day.

**Daily rules (2025-01 to 2026-10).**

- Dollar hedge: the chosen "any trust at ≥5% discount" made +20.8% a year (t 1.80); the 10% variant made +27.6%.
- The coin-holdings hedge is net short |discount| × NAV of the coin, so its results swing with the coin's direction. Its
  chosen rule ranked 7th of 8 (t 0.92).
- At an ADV-limited size the chosen rule made **+$164k a year** (37 trades, +3.9% each on average, 86% positive). By
  trust: ZCSH +$0.88M, LTCN +$0.19M, and **ETCG −$0.86M** — a no-catalyst discount held since 2021.

## Results — (b) DATs

**Naive against true ratio on 2026-10-09.** Debt and preferred turn five dashboard discounts into premiums:

| | naive | true |
|---|---:|---:|
| MSTR | 0.93 | 1.19 (EV 1.15, matching Strategy's own figure) |
| Metaplanet | 0.63 | 1.29 ($1.78B debt) |
| DFDV | 0.55 | 1.04 |
| BRR | 0.77 | 1.23 |
| UPXI | 0.37 | 3.97 |

**Weekly panel.** 1,077 DAT-weeks; 823 eligible, 541 after dropping names whose holdings fail the 10-Q check.

- Out of sample, deep true discounts did not converge: below 0.5, +0.7% per 40 days (t 0.20); 0.5–0.7, +3.3% (t 1.65),
  after −11.0% in sample.
- The only stable sign is premium decay: true mNAV 1.1–1.5 lost 14.8% per 40 days (t −3.75). Trading that needs a
  borrow, which was not tested.
- Coin-holdings-hedged rules made +6.5% in sample (t 2.16) and −11.1% out of sample (t −2.50). That swing is the coin's
  direction, not convergence.

**Events (27, each dated against EDGAR 8-K/6-K/proxy filings).**

- Buyback authorizations (n=10): +20d −1.3% (t −0.19), +60d −4.8%.
- Executed buybacks (n=4): +1.1% over 20 days.
- Coin sales to fund buybacks or repay debt (n=3): **−39.2% over 60 days** (t −2.64).
- Activists: day-0 +5.0% (n=3); +60d +33.6% (n=2).
- Window chosen in sample: 5 days (+3.9%); tested: +0.8% (n=5).

## Live candidates (true mNAV from dashboard holdings / from 10-Q holdings)

| DAT | true mNAV | catalyst | ADV | capacity | legs |
|---|---|---|---:|---:|---|
| SKYA | 0.33 / 0.35 | none | $0.5M | $0.25M | SOL perp |
| HYPD | 0.32 / 0.41 | preferred appears converted (unverified) | $1.6M | $0.8M | HYPE perp |
| TONX | 0.55 / 0.52 | $250M buyback; 10b5-1 plan since 2026-07-01 | $1.1M | $0.5M | **no TON perp** (Binance and Bybit stopped in 2026-06) |
| **EMPD** | **0.56 (0.97 if the AI stake is worth 0)** | ATG proxy fight; Delaware courts backed ATG; **vote 2026-10-14** | $1.0M | $0.5M | BTC perp |
| **BNC** | 0.58 / 0.58 | $250M buyback (2025-09-22); YZi settlement and new board (2026-06-24) | $10.8M | $5.4M | BNB perp; **BNCUSDT stock perp** |
| HSDT | 0.61 / 0.55 | none | $0.9M | $0.45M | SOL perp |
| NAKA | 0.69 / 0.69 | none | $1.4M | $0.7M | BTC perp |
| FWDI | 0.65 / 1.07 (holdings unresolved) | $1B buyback; 6.16M shares bought 2026-03 | $11.7M | $5.8M | FWDIUSDT stock perp |

- **EMPD's discount is mostly a dashboard artefact.** Its 2026-07-10 8-K and The Block report 1,400 BTC sold since
  2026-05-07: 1,514 BTC and about $74M cash remain, $65M of it committed to an AI venture. The dashboards still show
  about 2,930 BTC.
- Trusts today: LTCN −4.8% and BCHG −4.6% (conversion filings pending, S-3/A filed 2026-09-11); ETCG −36.9% with no
  filing.
- No trust has a listed perp. Binance TradFi lists MSTR, BMNR, FWDI, BNC and STRC; HIP-3 lists MSTR, BMNR and STRC.

## Late entry

- Conversion trades: 1 day late keeps 89–102%, 1 week late 77–91%.
- Daily trust rule: 77% and 52%.
- DAT events: the first trading hour carries a median 65% of the event day's move (20 events), and there is no drift
  afterwards to keep.

## Risks and kill criteria (standby row `otc-trust-discount-standby`)

**Risks:** no catalyst (ETCG); OTC spreads of 2–9% in the smallest trusts; dollars concentrated in one name; sponsor
distributions (the 2024 Mini Trusts took 10% of GBTC's and ETHE's coin).

**Kill if:**

- any position is held 12 months without a conversion filing;
- trailing 12-month excess over the savings rate is negative;
- a filing is withdrawn;
- there are fewer than 3 trades a year.

For any DAT trade: verify holdings against the latest 10-Q or 8-K first, exit if coins are sold for anything other than
buybacks, and exit after 3 months.

## What failed

- The GBTC-style entry rule found no target among 2025–26 single-coin conversions.
- DAT discount convergence at 1–3 months.
- Buyback announcements produced no drift.
- Coin-funded buybacks were followed by further losses.

## Errors found in the worker's own work

1. **Yahoo closes.** Yahoo scales GBTC and ETHE closes before the Mini Trust spin-offs by about 0.9, which manufactured a
   −11% "discount" at GBTC's conversion. Undone; the GBTC trough then reads −48.7%, matching the widely reported level.
2. **Split basis.** XBRL comparatives are restated after splits, so adjusting by period date left GBTC with one usable
   data point. Replaced by a continuity rule, pinned by a test.
3. **OBTC.** Its 2025 share count contradicts its own NAV; that data point was replaced by NAV ÷ price.
4. **Hedge direction.** The coin-holdings hedge's in-sample DAT "edge" was the coin crash.
5. **Stale dashboard holdings:** EMPD, FRMM (~13,700 ETH by its 10-Q, not 69,802), FGNX. The live table uses the
   company documents and the panel was re-run without these names.
6. **Partial or mis-scaled XBRL units:** SBET's tag covers 229k of about 870k ETH; FGNX's is 1000×. XXI's XBRL share
   count is the pre-merger shell's single share.
7. **Two input bugs:** a Metaplanet preferred currency bug ($3.5 trillion); MSTR's stale 30 June cash (true ratio 1.29 →
   1.19 with the KPI-implied $5.7B).

**Gaps:** www.sec.gov refused the "llm-quant research" UA, so filing texts came from press releases; nine non-reporting
trusts have no coin-per-share data; basket trusts have no daily NAV; borrow for shorting premiums was not measured.

## Next

1. Pre-register EMPD and BNC as forward tests, scored at +20 and +60 days.
2. Get daily basket NAVs (GDLC, BITW) to measure the one 2024–25 recurrence of the GBTC pattern.
3. Run a 10-Q-versus-dashboard holdings check before any DAT trade.
4. Test borrow availability and cost for the decaying 1.1–1.5× premium names.

## Coordinator's check

Recomputed Strategy's three ratios from the note's own inputs and the raw prices alone:

- **Inputs:** MSTR's 2026-10-09 close $154.34 (`raw/yahoo/MSTR.json.gz`); BTC $82,514 at 20:00 UTC
  (`raw/binance/BTC_1h.json.gz`); 848,000 BTC; $5.7B cash; $6.714B debt; $14.15B preferred; 422.07M shares.
- **Result:** true mNAV **1.189**, EV mNAV **1.148**, naive **0.931**. That matches the table: the dashboard "discount"
  is a premium once debt and preferred count.

Files: `scripts/nav_wrappers.py`, `scripts/test_nav_wrappers.py` (18 tests), `analysis.json`, `tables.md`,
`manifest.json`, `book_entries.json`, `curated.json`, `universe.json`, `raw/`.
