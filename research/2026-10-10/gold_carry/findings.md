# Gold carry: long tokenized gold, short the gold perp — 2026-10-10

The rent map ranked metal-perp funding third among under-tested pools. Gold and silver perps pay 6.3–14.7% a year on
$2.05B of open interest, and xyz's oracle follows spot.

**Answer: no-go. Two lines go on watch, and there is no book entry.**

The gold perps' funding is not a roll:

- Every XAU oracle follows spot gold.
- The PAXG/XAUT perps follow their own tokens.
- So funding above the cost of carry is a real premium paid by leveraged longs.

It does not survive the capital, though:

- The cost of carry implied by COMEX in 2026 is 2.8–3.8% a year (median 3.48%). That is about the savings rate.
- The two legs tie up 1.0–1.25× notional.

What is left out of sample:

- **+1.7% to +2.6% a year over SSR on capital** on the three venues that pay most: xyz:GOLD, Hyperliquid PAXG, and
  Binance XAUUSDT with PAXG as portfolio-margin collateral.
- **≤ +1%** on the token perps on Binance and Bybit, which arbitrageurs already work.

Nothing passes the pre-committed go rules, and the near-misses are what changes the answer:

- **Statistics:** the only variant that survives Benjamini–Hochberg across the 168 variants is $0.55M wide.
- **Size:** tokenized-gold depth caps the trade at about $1–2M (asks within 25bp: PAXG $2.13M, XAUT $2.05M across all
  books).
- **Best case:** about $62k a year.

## Verdict

Excess is over SSR (3.80%), out of sample. K is capital per unit of notional. BH p is the study-wide adjusted p-value.

| series (capital) | K | test window | excess | NW t (30 lags) | BH p | size | $/yr | verdict |
|---|---|---|---|---|---|---|---|---|
| xyz:GOLD × PAXG (cash) | 1.12 | 05-18→10-09 | +2.59% | 2.23 | 0.19 | $2.13M | $62k | **watch** |
| HL PAXG × PAXG (cash) | 1.15 | 01-08→10-09 | +1.69% | 2.17 | 0.20 | $1.02M | $20k | **watch** |
| Binance XAUUSDT × PAXG (portfolio-margin collateral) | 1.00 | 05-12→10-09 | +2.63% | 1.56 | 0.36 | $1.04M | $27k | no (t) |
| Binance XAUTUSDT × XAUT (collateral, trail30d) | 1.00 | 07-03→10-09 | +1.63% | 2.96 | 0.06 ✓ | $0.55M | $9k | no (size, 197 days) |
| Binance/Bybit PAXG perps × PAXG | 1.0–1.21 | — | −0.13% to +0.67% | ≤ 1.18 | — | — | — | no |
| Bybit XAUT/XAU × XAUT | 1.0–1.21 | — | +0.13% to +1.81% | ≤ 2.24 | — | — | — | no |
| Best-venue switching (PAXG / XAUT families) | ~1.1 | — | +1.56% / +1.79% | 1.01 / 0.44 | — | — | — | no |
| Silver | — | — | no tokenized silver on Binance, OKX, Bybit or HyperCore | — | — | — | — | no leg |

## What each oracle tracks

**XAU perps follow spot.** This covers Binance, Bybit, OKX, xyz and the delisted km/flx/cash GOLD markets.

- In US hours the index sits 43–50bp (median) below GC=F.
- It steps by the calendar spread exactly at GC=F's rolls: the PAXG/GC=F steps were −46, −57, −59 and −128bp on
  2026-01-28, 03-27, 05-27 and 07-29.
- Against PAXG it sits +4 to +14bp, with no steps (xyz: 0 steps against PAXG, 3 against GC=F). No roll is paid.

**The indices are circular blends.**

- Binance: dxFeed/Kaiko/Pyth/Massive spot feeds, plus xyz:GOLD at 7.6% and its own perp at 0.8%.
- OKX (weekend snapshot): Binance's index 57%, Hyperliquid's oracle 21%, its own perp 22%.

**Weekends.**

- Binance's index was 100% frozen through April. It has followed its own perp since Saturday 2026-05-09 05:00 UTC (slope
  0.54–0.69).
- OKX's index has moved since January 2026; Bybit's and xyz's always have.
- Effect on Binance XAU funding while spot is shut: 34.3% a year before the switch, 0.0% after. Open hours went from
  11.4% to 9.6%.

**Token perps** (HL PAXG, Binance/Bybit PAXG and XAUT) price off the token's exchange basket, 24/7: median 0.0bp from
Binance PAXG.

## Data and method

**Data.**

- Every funding settlement since listing: Hyperliquid hourly, Binance/Bybit 4-hourly, OKX 8-hourly (OKX serves only 3
  months).
- Hourly trade, index, mark and premium bars.
- PAXG/XAUT spot on Binance, OKX, Bybit and Coinbase; Yahoo GC=F/SI=F hourly.
- Live books on 6 venues (Saturday 17:57 UTC), collateral tables, issuer fee pages.

**Daily carry.**

- Funding, plus the change in the token-minus-perp basis, minus taker fees and half-spreads on entry, exit, rebalancing
  and venue switches.
- Divided by capital: cash10 (1 + 10% + maintenance margin), cash20, or collateral (1.0).
- Collateral rates read from the venues: Binance portfolio margin PAXG/XAUT 0.80; Bybit UTA XAUT 0.9 falling to 0.6 by
  size; OKX tiered. Hyperliquid's portfolio margin takes only BTC and HYPE; HyperCore XAUT0 traded $0 that day.

**Selection.**

- 7 pre-committed rules: always on; on while trailing 7- or 30-day funding beats SSR + 0/2/5pp. Plus monthly best-venue
  switching.
- Chosen on the first half of each series, tested once on the second.

## Results

Funding a short received since listing:

| venue | since listing | note |
|---|---|---|
| HL PAXG | 8.1% | |
| xyz:GOLD | 8.4% | |
| Binance XAU | 13.0% | 19.2% in launch months while the interest leg was on, 6.9% after |
| Binance PAXG | 4.9% | |
| Bybit PAXG | 6.7% | since 2022 |
| Bybit XAUT | 4.6% | |
| Bybit XAU | 4.7% | |
| OKX XAU | 7.5% | 3 months |

- **The rent map's 30-day rates were the top of their ranges** (Bybit XAU 14.7%, OKX 12.9%).
- **The token premium to spot is the hedge's main noise.** PAXG's median is −4bp, but monthly medians moved from +41bp
  (2025-12) to −26bp (2026-04) to +13bp (2026-10). XAUT runs about −21bp. That drift cost −0.66% (Binance XAU) and
  −0.81% (xyz) a year of basis.
- **Both test halves were positive for the two watch lines:** xyz 3.53% / 1.67%; HL PAXG 0.57% / 2.80%.
- **Bootstrap 95% intervals:** xyz −0.23% to +4.90%; HL PAXG +0.02% to +3.01%.
- **The edge is not tied to a gold bull market.** Bybit PAXG funding by year, 2022–26: 2.9 / 8.2 / 12.0 / 0.9 / 3.0%,
  against gold −1 / +11 / +29 / +65 / −4%. Monthly correlation −0.15.

## Capacity

Within 25bp, one shot, Saturday books:

| leg | depth |
|---|---|
| xyz:GOLD perp bids | $2.29M |
| HL PAXG perp bids | $1.02M |
| Binance XAU perp bids | $12.5M |
| PAXG token asks (Binance $1.04M, Kraken, Coinbase, OKX) | $2.13M |
| XAUT token asks | $2.05M |

- Above those sizes, the next $1M costs another 75bp one way on xyz, which leaves +1.25% on capital over a one-year
  hold. On HL PAXG it costs 64bp, leaving +0.57%.
- Ethereum supply: PAXG 436k oz ($1.83B), XAUT 827k oz ($3.46B). The largest DEX pools are PAXG/WETH ($15.6M) and
  PAXG/XAUt ($5.8M).

## Late entry

The rules are slow, so this is not a speed trade: always-on rules keep 100% of the edge entered 1 hour or 1 day late,
and threshold rules 100–106%.

## Risks and kill criteria

- **Delistings.** 6 of 7 HIP-3 gold markets are delisted.
  - km, flx and cash lived 139–189 days and paid 2.5–8.8% while live.
  - Carry on them was −2.4% to +4.8%.
  - Last trade against PAXG ranged from −59bp to +4bp.
- **Weekend basis.** For XAU perps hedged with PAXG, the basis change over a weekend has a standard deviation of
  16–19bp, worst −76bp. Token perps: 3–5bp.
- **Liquidation.** cash10 on HL PAXG had 3 days when the intraday high came within 1% of liquidation, so margin needs
  topping up within hours.
- **Issuer gate.**
  - PAXG redeems through a Paxos account: 0.125% on the first $2M of 30-day net redemptions; physical delivery in bars
    of about 430 oz.
  - XAUT: 0.25% fee and about 430 oz for physical delivery (third-party sources; Tether's terms page did not render).
- **Kill the watch** if any of these happens:
  - trailing 30-day venue funding falls below 5.8%;
  - PAXG's premium to spot falls below −50bp (1st percentile so far: −36bp);
  - xyz changes its oracle method or delists GOLD;
  - Hyperliquid halts or auto-deleverages positions.

## What failed

- The Binance and Bybit PAXG/XAUT perps: arbitraged to about the cost of carry plus 1pp.
- Every two-venue cash version on those perps.
- Venue switching.
- Threshold rules: they bought in-sample highs (Bybit PAXG +4.44% in sample, −0.02% out of sample).

## Errors found in the worker's own work

1. **GC=F contract map.** It assumed Yahoo's GC=F held an October contract; it rolls August → December. The implied
   carry for that window was 6.6% before the fix and about 3.8% after. Fixed and pinned by a test.
2. **Hyperliquid depth.** The 20-level fine book understated depth: xyz $0.30M → $2.29M and PAXG $0.17M → $1.02M once
   the coarse book is used.
3. **Delisted HIP-3 markets.** Hyperliquid keeps serving zero-rate funding rows after a delisting; uncut, km:GOLD read
   4.0% instead of 7.3%.
4. **Weekend test.** Pooling the daily one-hour break with weekends hid Binance's oracle switch (it read 50% frozen); by
   month it is 100% frozen, then 3–6%.
5. **Collect log.** Two parallel collect processes overwrote each other's log; fixed with merge-on-write.

**Worker's verification.**

- Test-period xyz funding is 8.03% a year both from the raw rows and inside the simulator.
- Recomputed outside the simulator, excess is 2.92% before rebalancing costs against the simulator's 2.59%.
- Hyperliquid funding is identical to the shared store (6,988 hours) and reproduced 100% by the venue formula.
- PAXG's premium measured three ways over 150 common days: −11.4 / −15.6 / −12.6bp; daily correlation 0.91.

## Next

- Re-run `analyze` monthly. Promote xyz:GOLD / HL PAXG only if the excess holds above 2% with t > 2 through 2026-12 and
  survives BH.
- Re-test if Hyperliquid accepts XAUT0 or PAXG as portfolio-margin collateral (capital goes to 1.0, about +0.4% a year).
- Read weekday books.
- Confirm that Binance's TradFi perps can be held inside portfolio margin.

## Coordinator's check

Recomputed from `raw/hl/funding_xyz__GOLD.json.gz` alone: the mean hourly `fundingRate` over 2026-05-18 → 10-09 (3,480
hours) × 8,760 = **8.03% a year**. That matches the note. With a cost of carry of about 3.5% and 1.12× capital, the
+2.6% excess is the right order of magnitude.

Files: `scripts/gold_carry.py`, `scripts/test_gold_carry.py` (31 tests), `analysis.json`, `tables.md`, `manifest.json`,
`raw/` (12 MB). No `book_entries.json`: nothing passed.
