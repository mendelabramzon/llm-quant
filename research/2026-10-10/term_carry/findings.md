# Fixed against floating: dated basis, a do-it-yourself Ethena, Boros, and the volatility premium — 2026-10-10

The question is whether crypto derivatives carry offers a large yield above the Sky savings rate (SSR, 3.80% a year)
that does not depend on speed. The carry here is what derivatives pay to whoever is short leverage.
`scripts/term_carry.py` measures four places:

- (a) the basis of dated futures;
- (b) long spot / short perp on the venue that pays most — Ethena's trade, done by hand;
- (c) Pendle Boros's fixed-for-floating funding swaps;
- (d) as a measurement only, the options volatility premium.

Every number is in `analysis.json`; `tables.md` prints them and `manifest.json` lists sources and timings.

**Answer.** The large carries are real, but they are regime trades and the regime is off. In 2026, Binance BTC funding
averaged 2.9% a year and the quarterly basis about 3.1%; both are under the savings rate.

One thing was not regime-bound in the test: Hyperliquid's funding premium. The same coin pays roughly twice as much on
Hyperliquid as on Binance. Hyperliquid's new portfolio margin lets the spot be the short's collateral. That removes the
second block of capital that made earlier two-venue versions a cost-of-capital trade. Only HYPE held the premium in
every out-of-sample slice.

| | verdict | out of sample | now | size |
|---|---|---|---|---|
| (a) dated basis, rule "locked excess ≥ x" | standby, go = no | +2.4% to +5.4% a year over SSR (Deribit, Binance) | best locked excess +0.90%, under the 2pp trigger | ~$35M when on |
| (b) DIY Ethena on Binance | no-go | ≤ +1.2% a year; last 365 days −0.7% to −5.6% | funding 1.6–6.9% | — |
| (b) DIY Ethena on Hyperliquid, BTC/ETH/wstETH | watch | +3.1% to +5.7% (2024-07 → 2026-10) | last 365 days +0.3% to +2.5%; BTC/ETH t < 1 in each half since 2025-11 | — |
| (b) **HYPE spot as portfolio-margin collateral, short the Hyperliquid perp** | **proposed, go** | **+4.30%, t 5.68** | last 90 days +4.16% | **$5M, ~$200k a year** |
| (c) Boros implied vs realised | no-go | +0.12% (t 1.27); the in-sample winner lost | — | overlay only |
| (d) volatility premium | measurement | BTC +8.0 vol points, ETH +5.3 | 2026: +0.9 / +3.5 | — |

## 1. Data and method

- **Binance quarterlies.**
  - Continuous CURRENT_QUARTER and NEXT_QUARTER daily closes, 2021-02 → 2026-10, against Binance's index at the same close.
  - The contract each day refers to is the first (or second) quarterly expiry strictly after the close, at 08:00 UTC on
    the last Friday.
  - Checked at every roll: the basis converges to zero, and the series switches contracts after the roll.
- **Deribit quarterlies.**
  - Every quarterly since 2019, fetched by name; expired contracts are served and none were missing.
  - Daily bars are compared with the 08:00 UTC delivery price.
- **CME.**
  - Yahoo hourly BTC=F and ETH=F against BTC-USD and ETH-USD at the same hour, 2024-10 → 2026-10.
  - Yahoo's daily futures bars cannot be time-aligned with spot, so only the hourly window is used.
- **Funding.**
  - Binance from each perp's listing.
  - Hyperliquid 2023-05-12 → 2025-10-01 fetched here (5 seconds a call, no 429s), plus the shared store afterwards.
  - Daily funding is the sum of settlements in (d, d+1] UTC.
  - A short is marked to Binance's premium index, or to Hyperliquid's 00:00 premium.
- **Chain data** (public archive nodes, 486 grid points):
  - sUSDe `convertToAssets` every 3 days from 2023-11;
  - Maker's `Pot.dsr()` weekly from 2020;
  - wstETH `stEthPerToken()` weekly from 2021;
  - joined with the redemption study's daily NAVs from 2024-09-26.
- **Boros open API** (`api-boros.pendle.finance/apis`).
  - All 225 markets, matured ones included, with daily mark APR (`mr`) and underlying APR (`u`).
  - Daily `u` equals Binance's settled funding × 365 to 1e-12, so it is the floating leg itself.
  - 192 markets matured; 7,080 market-days were scored.
- **Costs** (VIP0 taker fees plus half-spreads; the spot leg is always bought on Binance spot):
  - Binance spot 10bp; Binance perps and quarterlies 5bp;
  - Hyperliquid perps 4.5bp;
  - Deribit 5bp;
  - CME about 1bp, plus 5bp for the spot;
  - Boros: taker fee 0.05% a year, settlement fee 0.1–0.2% a year, and a 25bp half-spread.
- **Capital per unit of notional.**
  - *Collateral = 1.0*: the spot is the short's collateral. This covers Binance portfolio margin, Deribit coin margin,
    and Hyperliquid portfolio margin for BTC and HYPE only.
  - On Hyperliquid, the short's 10% margin and any loss after a price rise are borrowed at 5.5%, and the legs are
    rebalanced after a 25% move.
  - *cash3x = 1.33 and cash5x = 1.2*: the short is margined separately in cash.
  - *CME = 1.4*, with the margin held in T-bills.
- **Benchmark.**
  - SSR 3.80% a year.
  - As a check, the savings rate actually paid (Maker's DSR, then the SSR): 0% in 2021–22, 7.8% in 2024, 5.5% in 2025,
    3.7% in 2026.
- **Protocol.** Each rule is chosen on the first part of time and tested once on the rest.
  - (a) 12 variants per venue: front or next quarterly × a threshold, chosen on the first half of each venue's history.
  - (b) 7 rules: always on, or on while trailing 7- or 30-day funding beats SSR + 0/2/5pp. Chosen on days before
    2024-07-01 (HYPE: on the first half of its own history); 196 series in total.
  - (c) 8 rules, chosen on trades that matured before 2026-03-01.
  - Statistics: Newey–West t with 30 lags, and a 30-day block bootstrap.

## 2. (a) Dated basis — a fixed yield that is only there in bull markets

Locked excess after a round trip, with the spot as collateral. Each cell is the mean excess, with the share of days at
least +2pp in brackets.

| year | Binance BTC next | Binance ETH next | Deribit BTC next | Deribit ETH next | CME BTC front |
|---|---:|---:|---:|---:|---:|
| 2021 | +8.9% (77%) | +9.9% (77%) | +8.9% (84%) | +9.5% (84%) | — |
| 2022 | −2.9% (4%) | −4.3% (4%) | −2.4% (7%) | −3.6% (5%) | — |
| 2023 | +2.8% (44%) | +1.2% (37%) | +0.2% (22%) | −0.8% (14%) | — |
| 2024 | +7.9% (100%) | +7.9% (94%) | +7.4% (99%) | +6.6% (92%) | +4.5% (81%) |
| 2025 | +2.4% (50%) | +1.7% (36%) | +2.5% (55%) | +1.2% (25%) | +0.6% (27%) |
| 2026 | −1.1% (0%) | −1.9% (0%) | −1.0% (0%) | −1.8% (0%) | −0.7% (1%) |

The rule, tested once on the second half of each venue's history:

| venue | test from | chosen | out of sample | trades | mean locked | 3x cash | vs savings paid |
|---|---|---|---:|---:|---:|---:|---:|
| Binance BTC | 2023-12-08 | next quarterly, x = 2pp | +5.37% | 4 | +7.1% (t 2.00) | +3.30% | +3.49% |
| Binance ETH | 2023-12-08 | front, x = 0 | +4.89% | 8 | +6.4% (t 2.51) | +3.14% | +2.92% |
| Deribit BTC | 2022-10-08 | next, x = 8pp | +3.47% | 4 | +10.0% | +1.10% | +0.84% |
| Deribit ETH | 2023-01-03 | next, x = 8pp (ranked 11th of 12 out of sample) | +2.36% | 3 | +10.1% | +1.90% | +0.69% |
| CME BTC / ETH | 2025-10-10 | front, x = 2pp | +1.09% / +0.45% | 1 / 2 | | | |

- The result does not depend on the threshold: Binance BTC's twelve variants made +4.1% to +5.4% out of sample.
- It does depend on 2024. The Binance BTC rule made +10.9% in 2024, +3.5% in 2025, and +1.0% in 2026, when it was in a
  trade only 30% of the time.
- Today the front quarterlies are 4.9% (BTC) and 4.2% (ETH) annualised. The best locked excess is +0.90% (Deribit BTC,
  March 2027).
- On the same expiries, Deribit's basis ran 1.1pp a year below Binance's USDT-margined basis (1,731 paired days).

**Verdict: standby.** Book row `dated-basis-cash-and-carry`, go = no, with a 2pp trigger.

## 3. (b) Long spot / short perp — Binance no longer pays; Hyperliquid does

Funding a short received, annualised mean:

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|
| Binance BTC | 30.6% | 4.2% | 7.9% | 11.9% | 5.1% | 2.9% |
| Binance ETH | 37.5% | 0.8% | 8.3% | 12.9% | 4.9% | 2.0% |
| Binance HYPE | | | | | 13.4% | 4.5% |
| Hyperliquid BTC | | | 13.5% | 24.1% | 10.6% | 5.2% |
| Hyperliquid ETH | | | 20.0% | 22.0% | 8.5% | 5.9% |
| Hyperliquid HYPE | | | | 117% (Dec) | 22.0% | 9.1% |
| sUSDe realised | | | 0.0% | 13.4% | 6.0% | 4.0% |
| savings rate paid | 0.0% | 0.1% | 2.9% | 7.8% | 5.5% | 3.7% |

Excess over SSR on capital, rule chosen before the split:

| block | capital | chosen | in sample | out of sample | t | always on | last 365 days | last 90 days |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Binance BTC | collateral | always | +10.7% | +1.18% | 2.63 | +1.18% | −0.72% | +1.52% |
| Binance ETH | collateral | 30d > SSR+2pp | +14.5% | +1.21% | 2.74 | +1.04% | −1.50% | +0.07% |
| Binance SOL | collateral | 30d > SSR+5pp | +9.1% | +0.52% | 1.41 | −2.30% | −5.62% | −1.42% |
| Hyperliquid BTC | collateral | 7d > SSR+5pp | +17.7% | +4.53% | 5.02 | +5.68% | +1.12% | +3.35% |
| Hyperliquid ETH | cash 3x | 30d > SSR | +13.2% | +3.11% | 4.36 | +3.08% | +0.66% | +2.56% |
| Hyperliquid ETH, wstETH spot | cash 3x | 30d > SSR | +15.4% | +4.80% | 6.48 | +5.08% | +2.50% | +4.18% |
| **Hyperliquid HYPE** | **collateral** | **always** | +25.2% | **+4.30%** | **5.68** | +4.30% | +4.03% | +4.16% |
| Hyperliquid HYPE | cash 3x | always | +18.4% | +2.69% | 4.85 | | +2.52% | +2.36% |

- **Binance.** The DIY carry beat SSR by about 1% a year with the spot as collateral, and by nothing on 3x cash margin or
  against the savings rate actually paid. sUSDe did better over the same test: 6.33%, against 4.98% total for the
  Binance BTC carry.
- **Hyperliquid BTC and ETH.** The money was made in 2024-07 → 2025-06. Always-on results from 2025-11-07:

  | | 2025-11-07 → 2026-03-31 | 2026-04-01 → now |
  |---|---:|---:|
  | BTC, collateral | +0.52% (t 0.41) | +0.93% (t 0.77) |
  | ETH, 3x cash | +0.49% (t 0.45) | +0.83% (t 0.93) |

  These stay a watch item. ETH is not accepted as portfolio-margin collateral on Hyperliquid, and wstETH adds the stETH
  discount tail (6–7% in June 2022) on top of 3x margin.
- **Hyperliquid HYPE** held everywhere.
  - Out of sample +4.30%; bootstrap 95% interval +2.85% to +5.66%; the best four weeks are 27% of the total.
  - Halves: +4.79% (t 3.52) on 2025-11-07 → 2026-03-31, and +3.93% (t 4.45) after.
  - 12 of the last 14 months were positive; the exceptions are 2026-05 (−0.4%) and October to date (−2.6%).
  - Over its 22 months in position the short received 37.4% of notional in funding, paid 1.4% in borrow and 3.3% in
    costs (25 rebalances).
  - The same trade on Binance made +0.45% (t 0.48), so the edge is the venue's funding level.
- **Multiple testing.** 173 of the 196 series survive Benjamini–Hochberg at q = 0.10 on the full sample, and every
  in-sample deflated Sharpe is 1.00: 2019–2024 funding was so high that almost every variant is significant, so neither
  statistic separates anything. The out-of-sample slices above do separate them.
- **Venue support.**
  - Binance: portfolio margin and multi-assets mode accept spot BTC/ETH as margin with haircuts (not re-verified this
    session).
  - Deribit: coin-margined.
  - Hyperliquid portfolio margin (docs read 2026-10-10): BTC LTV 0.5, user cap 200 BTC, global cap 5k BTC; HYPE LTV
    0.65, user cap 1M HYPE, global cap 25M; spot plus a short perp "collateralized by the spot balance" is explicitly
    supported; stablecoin borrow costs 5% + 4.75 × (utilisation − 80%); account value must be $10k–$25M.
  - Before Hyperliquid's portfolio margin existed, only the cash-margin rows were tradable there.

## 4. (c) Boros — fairly priced on average, wrong in both directions by turns

| group | markets | market-days | implied | realised | implied − realised | t (by day) |
|---|---:|---:|---:|---:|---:|---:|
| all | 192 | 7,080 | 2.08% | 1.96% | +0.12% | 1.27 |
| crypto | 150 | 6,003 | 4.31% | 4.12% | +0.20% | 1.43 |
| TradFi | 42 | 1,077 | −10.4% | −10.1% | −0.29% | 1.17 |
| Binance BTC / ETH | 13 / 13 | 802 / 850 | 4.44% / 3.82% | 3.83% / 2.85% | +0.61% / +0.97% | 1.63 / 2.19 |
| Hyperliquid BTC / ETH / HYPE | 24 / 17 / 10 | 879 / 825 / 292 | 6.01% / 6.25% / 8.98% | 6.26% / 6.86% / 9.81% | −0.25% / −0.61% / −0.83% | 0.28 / −0.75 / −1.11 |

- **The protocol's pick failed.** It was "pay fixed when implied is 10pp below the trailing week": train +6.4% a year
  (t 3.57, 42 trades), test −2.1% (t −1.28).
- **The sign flips with the cycle.** On crypto markets, receiving fixed made +1.7% to +2.4% in the train half, while
  funding was falling, and −1.6% to −2.3% in the test half (t −3.0 to −3.6); paying fixed did the mirror image. That is
  a forecast error that changes sign with the funding cycle, not a premium.
- **As an overlay**, receiving fixed can lock a carry. Live implied rates: Hyperliquid BTC 8.1–8.4% to November
  (trailing 30 days: 9.1%); Hyperliquid ETH 8.1–8.2% to December; Hyperliquid HYPE 8.8% to 30 October; Binance BTC
  5.0–5.3%.
- **Depth is small**: the Hyperliquid BTC USDT market has $0.85M of open interest, and the BTC-collateral market 68 BTC.
- **History accumulates.** `snapshot` appends the live term structure to `boros_snapshots.jsonl`.

**Verdict: no-go as a carry.**

## 5. (d) The volatility premium

DVOL against the realised volatility of the next 30 days (Binance hourly closes), 1,996 days, 2021-03 → 2026-09. Figures
are in vol points.

| | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | all | share positive | p5 | p1 | worst |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC | +16.5 | +13.0 | +7.3 | +6.3 | +3.7 | +0.9 | +8.0 (t 5.6) | 74% | −17 | −30 | −52 (May 2021) |
| ETH | +11.1 | +10.6 | +6.0 | +2.6 | −1.3 | +3.5 | +5.3 (t 2.5) | 66% | −28 | −67 | −97 (May 2021) |

The premium is there, the tail is fat (ETH: skew −0.78, kurtosis 6.0), and the premium shrinks year by year.

## 6. Size

- **HYPE carry.**
  - Binding leg: Hyperliquid's HYPE spot book, $1.14M within 25bp per side (read with 4-significant-figure aggregation;
    the default 20-level book spans only 3–5bp and shows $0.1M).
  - The perp has $2.4M within 25bp, $1.68B of open interest, and $217M a day of volume.
  - Quoted at $5M (four times the spot book, built over one to two weeks) × the trailing year's +4.0% ≈ $200k a year.
- **Dated basis.**
  - 5% of $703M of quarterly open interest: Deribit BTC $483M, Deribit ETH $128M, Binance BTC $67M, Binance ETH $25M.
    That is about $35M.
  - Live depth within 25bp is $0.06–1.9M per contract, so a position is built over days.
  - CME was not measured.

## 7. Kill criteria

- **HYPE carry**, retire on any of:
  - trailing-30-day Hyperliquid HYPE funding below 6% a year;
  - realised excess over SSR negative over a trailing 90 days;
  - Hyperliquid's HYPE funding within 2pp of Binance's for 30 days;
  - portfolio-margin terms change (HYPE LTV below 0.5, user cap below 100k HYPE, or borrow rate above 10% for a week);
  - any auto-deleveraging of the short, a Hyperliquid halt, or an exploit.
- **Dated basis**: hold nothing unless the locked excess after a round trip is at least 2pp; a completed trade more than
  0.5% of notional away from its locked yield; quarterly open interest below $200M; retire after a year with fewer than
  10 trigger days.

## 8. What this cannot see

- **Venue failure.** Both legs of the HYPE trade, and the collateral, sit on Hyperliquid, in the venue's own token.
  Auto-deleveraging of the short in a crash, as on 2025-10-10, is not simulated.
- **Execution.** The study charges taker fees on daily decisions; it does not model building positions with limit
  orders. Deribit is measured as a last trade at 08:00 against a 30-minute index average.
- **Coverage gaps.** CME has only two years of history and no open interest. Binance's portfolio-margin terms were not
  re-read.
- **Selection.** HYPE was suggested by the funding_arb study's test half (2026-04 → 10), which overlaps this test. The
  earlier, independent part of this test (2025-11-07 → 2026-03-31) held: +4.79%, t 3.52.

## 9. What went wrong and was fixed

1. **Deribit timing.** Deribit's daily bars close at 08:00 UTC, but the first pass compared them with a midnight index.
   On 2022-06-15 that index sat 3.1% away from Binance's. The Deribit BTC rule then showed +10.2% out of sample; against
   the 08:00 delivery price it is +3.47%. Pinned by a test.
2. **Boros fields.** The redesigned API moved the asset and venue to `underlyingSymbol`, `platform.name` and
   `fundingRateSymbol`. The first pass merged every market into one floating stream and found a false +13.8% "bias"
   (t 2.84).
3. **Boros hourly series.** The hourly `historical-underlying-apr` disagrees with settled funding (3.67% vs 7.75% on
   2025-10-01). The daily `/indicators` `u` is used instead.
4. **Deribit pagination.** Delivery prices come 100 per page, so the first fetch kept only 100 days.
5. **HYPE reference price.** It was never set because Binance's HYPE prices start after the carry's first entry, so no
   borrow or rebalance cost was charged before May 2025. The HYPE result moved from +5.62% to +4.30%. Pinned by a test.
6. **Portfolio margin is not free.** Adding the borrow on the short's margin took Hyperliquid BTC from +5.09% to +4.53%.
7. **Pre-deployment chain sample.** One sample taken before wstETH existed returned `0x`; it is tolerated and refilled.
8. **Existing repo data.** `unlock-preshort`'s `net_apr` of 2.4 prints as 240%: it is $120k a year over about $50k of
   average deployed notional, so it is not comparable with rows quoted per year of capital. The SSR measured from
   sUSDS's NAV was 3.60% APY until 2026-10-06 and about 3.80% from 2026-10-07.

## 10. What next

1. Forward-track the HYPE carry: funding on both venues, portfolio-margin terms, borrow rate, and a paper position.
   Re-run `analyze` monthly.
2. Use Boros overlays (Hyperliquid BTC/HYPE at about 8–9%) to lock the carry for one to three months, at a few $M of size.
3. Read CME's open interest and history, and set a daily alert for when any dated contract's locked excess crosses 2pp.

## Coordinator's check (2026-10-10)

Recomputed from the raw funding files rather than the study's tables: Hyperliquid HYPE funding averaged **9.64% a year
over the test window** (2025-11-07 → 2026-10-09; 9.96% in its first half, 9.40% in its second), 9.14% in 2026 to date
and 8.19% in October so far; Binance's HYPE perp paid **4.55%** over 2026 (1,691 settlements). The venue premium the
row rests on is in the raw data. Net of SSR (3.80%), the ~0.55% margin borrow and the ~1–1.5% a year of rebalancing
costs, the study's +4.30% follows. Two things the row's number does not show: it sits on the same venue as the equity
carry (`hip3-equity-funding-carry`), so the book's two largest go rows now share one venue risk; and the funding that
pays it is the same leverage demand that the 2025-10-10 crash auto-deleveraged, which the study does not simulate.
