# Binance TradFi perps against HIP-3: the hedge works, the carry does not survive it — 2026-10-10

The question: Binance lists 217 "TradFi" perpetuals (179 US equities, 15 Hong Kong, 8 Korea, 8 commodities, 2 China,
one FX, four pre-market). Can one of them replace the broker stock leg of the book's largest row,
`hip3-equity-funding-carry` (short trade.xyz single-stock perps that pay at least 8% a year, buy the stock at a broker)?
Is the funding spread between the two venues a trade of its own? Do the two venues' energy indices roll differently?
`scripts/tradfi_perps.py` (collect, hl-topup, stocks, match, books, analyze, render); numbers in `analysis.json`,
tables in `tables.md`, pairs in `pairs.json`.

**Verdict.**
- **(a) A Binance-hedged equity carry: no-go.** The second perp removes about 95% of the off-hours risk, but the Binance
  long pays its own funding (4.3% a year on the matched twins), and on liquid names what is left is below the savings
  rate.
- **(b) No standalone pair or commodity trade.** Wide spreads exist only in books a few thousand dollars deep. Both
  venues' energy indices roll on the same schedule, and each venue's funding pays for its own roll.
- **(c) The equity carry should be re-quoted down.** Its excess holds on a fresh split, but it sits in thin names:
  measured depth supports about $1.6–2.1M of notional, worth $54–73k a year, not $330k.

## What was measured

- **Binance:** all 217 TradFi perps from listing: every funding settlement (77,574 at analysis time), hourly trade,
  premium-index and index-price bars, index constituents, open interest. None has been delisted.
- **Hyperliquid:** the shared funding store, topped up to 2026-10-10 11:00 UTC for the 123 matched markets.
- **Stocks:** Yahoo daily closes and dividends for 175 of 178 underlyings.
- **Books:** live on both venues on Saturday 10-10 at 11:46 UTC; the 2026-09-10 in-session Hyperliquid books are the
  weekday reference.
- **Matching:** 123 pairs, by name and price. 121 are the same asset in the same units (price ratio 0.9986–1.0006, the
  USDT/USDC rate); 2 are index-versus-ETF proxies (SP500/SPY at 10.02, XYZ100/QQQ at 41.07); 6 were rejected, including
  the pre-IPO pairs ANTH and OAI, 2.6% and 4.4% apart.

## Q1. Binance's funding

- **Formula:** each settlement is (h/8)·[P + clamp(I − P, ±0.05%)], capped at ±2% for equities and ±0.5% for
  commodities. The interval h is 8 hours for US stocks and 4 hours for commodities and Asian stocks. The interest leg I
  has been zero since February 2026 (0.01% per 8 hours only in the launch months of XAU, XAG, HOOD and INTC).
- **Reproduction:** 80.2% of settlements within 1bp, 73.0% within 0.5bp; the zero/non-zero call agrees 86.9% of the
  time; the implied clamp is 0.056%.
- **68.5% of settlements are exactly zero.** Inside the band Binance longs pay nothing; trade.xyz charges a 5.5% floor.

Funding longs pay, a year:

| | since listing (median) | last 90 days | US session | weekday nights | weekend |
|---|---:|---:|---:|---:|---:|
| US equities (178) | 4.2% | 2.8% | 6.6% | 5.8% | 1.6% |
| Commodities (8) | 15.1% | 8.5% | | | |
| Hong Kong (15) | 13.7% | | | | |
| Korea (8) | 5.5% | | | | |
| China (UNITREE, CXMT) | −48.9% | | | | |

- On the 105 matched US twins, Hyperliquid charges 11.6% / 13.0% / 7.0% (session / nights / weekend) and Binance
  8.2% / 7.8% / 1.2%.
- A Binance-side broker carry is smaller than HIP-3's: +0.2% a year over the savings rate out of sample (t 0.06),
  against +2.3% (t 3.9) for xyz run the same way.

## Q2. The pair family

- **Spread:** 118 pairs; Hyperliquid − Binance funding has a median of +5.2% a year and is higher on Hyperliquid for 76%
  of pairs. Persistence (first-half vs second-half pair means): 0.49.
- **Liquid names are small or negative:** CRCL −3.0%, MU −3.1%, SNDK −3.4%, NVDA +2.2%, TSLA +2.1%, MSTR +3.5%, HOOD
  +8.8%, gold +2.9%.
- **Hourly grid** (the funding study's machinery, 108 variants, chosen on pair-days before 08-07): `slow_k90d_X8`, 4.6%
  on deployed capital in the test (+0.8% over the savings rate), t 5.5, deflated Sharpe 0.00.
- **Always-on, short Hyperliquid / long Binance:** 3.8% in the first half, 5.1% in the second (t 4.6).
- **The book's rule with a Binance hedge:** −4.6% in sample, +0.4% out of sample (t 0.28); selecting on the spread
  instead, +0.9% (t 0.59). Nothing survives Benjamini–Hochberg.

**Where the profit sits.** Always-on, no costs, excess over the savings rate on capital, first half → second half
(split 07-15):

| Hyperliquid open interest | two-perp | broker |
|---|---|---|
| over $20M | −1.9% → −1.1% (t −0.8) | +2.6% → +0.6% (t 0.9) |
| $5–20M | +4.1% → +1.3% | +4.2% → +1.5% |
| under $5M | +4.6% → +5.6% (t 3.4) | +11.6% → +4.7% |

Broker-carry funding on the names over $20M fell from 9.0% to 6.0%, against a 5.7% cost of capital at 1.5x. By month,
the two-perp spread was +21.6% in April and −16.1% in May (Binance's launch months), then +4.8% to +8.9% from June to
October.

## Q3. Off-hours risk (names with Hyperliquid open interest of $5M or more)

Worst move against the short while the cash market is shut, p95 / p99 / max:

| | broker short (perp move) | two-perp short (basis move) |
|---|---|---|
| overnight | 5.4% / 9.9% / 27.9% | 0.26% / 0.50% / 9.4% |
| weekend | 5.9% / 7.9% / 14.4% | 0.55% / 1.24% / 2.3% |

- The 9.4% overnight outlier is SPCX, a SpaceX-linked name priced off different oracles on the two venues.
- The basis gap at the Monday open is 0.21% at p95. Hourly correlation is 0.99 / 0.96 / 0.90 (session / nights /
  weekend); the second perp removes 97% / 92% / 80% of the variance.
- Binance's index includes HIP-3 prices for 13 symbols. On the Saturday snapshot BZUSDT's index was 96.2% xyz:BRENTOIL;
  CL, NATGAS and XAU give it 7.6–9%.

## Q4. Capacity (Saturday books; Hyperliquid's weekday depth was about 1.5–2x)

| basket (09-15) | 5% of open interest | capped at depth within 25bp | $ a year over the savings rate |
|---|---:|---:|---:|
| two-perp, top 10 | $12.6M | $1.20M | $54k planning / $5k at depth |
| broker, all xyz | $15.9M | $1.58M (weekday books: $2.14M) | $539k planning / $54k at depth / $73k at weekday depth |

## Q5. Commodities

- **Metals:** gold +2.9%, silver −0.2%, copper +0.3%, platinum −0.7%; palladium +9.9% but $20k of capacity. The grid
  never traded a commodity pair.
- **Energy front weights in October:** NG 1.00 → 0.80 → 0.60 on both venues; Brent 0.81 → 0.62 on Binance against
  0.77 → 0.60 on xyz. Binance steps about an hour earlier (21:00–22:00 UTC), so the index ratio jumps at xyz's step hours
  (September: +202bp Brent, +222bp WTI), but the perp-perp basis moved only −0.01% to +0.02% per window.
- **Each venue's funding paid for its own roll:** September Brent −4.19% on Hyperliquid vs −4.26% on Binance; WTI −3.63%
  vs −3.82%. The pair nets ±0.5% per window from June to September before a 15–25bp round trip. No trade.

## The equity carry, re-tested

The all-xyz broker carry, chosen on 03-16..07-14 and tested on 07-15..10-09: `trail_8pct|vol>=0.5M` made +2.26% a year
on capital (t 3.91, bootstrap 1.28–3.24%, deflated Sharpe 0.999, all 6 variants survive BH); the book's own `vol>=2M`
variant made +2.29% (t 3.84). The edge is real on a fresh split, and it sits in thin names. Suggested re-quote: net APR
about 3.4% on notional (1.5 × 2.26%), $54–73k a year at depth-capped capacity, `go` still unset.

## Kill and watch criteria

- **Equity carry:** retire if the trailing-quarter funding of basket names over $20M of open interest stays below 5.7%
  while the excess comes only from names under $5M; retire if depth-capped capacity falls below $1M of notional.
- **Two-perp spread (watch only):** promote if twins over $20M of open interest earn more than 5.7% a year over a
  trailing 90 days, Binance's interest leg stays at zero, and persistence stays above 0.3.

## What this cannot see

- **Delisted HIP-3 markets:** 49 builder markets delisted before 10-09 (19 on Markets by Kinetiq, including TSLA, GOLD,
  NVDA) are missing from the store.
- **Fees:** Binance's TradFi taker fee is assumed at 5bp; the liquid-name conclusion holds before costs.
- **Capacity:** Saturday books; "5% of open interest" assumes shorts do not compress the premium (unmeasured); the depth
  cap is one-shot, and building over days would size larger.
- **Stablecoins:** the two-perp hedge is USDT on one side and USDC on the other.
- **History:** Binance's equity history is 4–8 months, and its first two months were a launch regime.

## What went wrong and was fixed

1. **4-hour Binance symbols** scale funding by h/8: the unscaled crypto formula fit within 1bp on only 56–67% of
   settlements, the scaled one on 87–92%. Pinned by a test.
2. **Same-unit tolerance** at 3% let ANTH through (2.6% apart); tightened to 1%, since real twins agree within 0.1%.
   Pinned by a test.
3. **The two-perp out-of-sample profit** (+3.1%, t 2.9) came from Paragon, EntropyIO and Kinetiq markets under $5M of
   open interest; the open-interest split found it, and showed that the broker carry's excess is mostly thin names too.
4. **Off-hours numbers** were first inflated by stale prints in thin Paragon books; a liquid subset is reported.
5. **Snapshot path:** the loader failed on a relative path; fixed with `resolve()`.

**Found in existing code, not edited:** `equity_offhours.FUND_PARAMS` assumes one funding multiplier per builder dex,
but `universe.json` carries per-market values (io:ANTH and io:OAI 0.125, xyz:OURA 0.005, para:2Y/10Y/30Y 0.1);
`funding_arb.Pair.funding` scales both legs' funding by leg B's price path, which is approximate when the legs diverge.

## What next

1. Re-quote the equity carry with depth-aware capacity and add the liquid-bucket kill criterion.
2. Measure how far funding falls when shorts arrive (a Hyperliquid open-interest event study) to replace the assumed 5%
   of open interest.
3. Snapshot weekday books on both venues and re-run `analyze` in December to see whether Binance's post-June regime holds
   on liquid names.

## Coordinator's check (2026-10-10)

Recomputed from the raw Binance files: 77,820 TradFi settlements on disk (the study analysed 77,574 before its top-up),
**68.5% exactly zero**; since listing TSLAUSDT paid longs' funding of 1.90% a year (58% of settlements zero), NVDAUSDT
6.67% (50% zero), XAUUSDT 13.04% (46% zero). The mechanism the verdict rests on — Binance has no interest floor on these
contracts, trade.xyz does — is in the raw data. Not re-checked: the depth-capped capacity, which uses a Saturday book
and is the number that moves the book's largest row.
