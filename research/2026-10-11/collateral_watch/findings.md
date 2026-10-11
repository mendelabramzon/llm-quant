# Collateral watch: who accepts what as margin, and the same-venue carry each asset pays — 2026-10-11

The 2026-10-10/11 synthesis found that the largest persistent rents are funding-formula parameters. When longs dominate,
a perp settles at the formula's interest leg, 0.01% per 8 hours (10.95% a year). The rent stays uncollected because the
arbitrage needs capital on two venues. It becomes collectable when a venue accepts the spot asset as margin: hold the
spot as collateral and short the same venue's perp. The book's best carry (HYPE on Hyperliquid) exists only for that
reason. `scripts/collateral_watch.py` snapshots every venue's collateral list daily, diffs it, and prices the
same-venue carry of each eligible asset.

## Answer

**The pattern is everywhere, and the spot book is what limits it.**

- **Hyperliquid's own pair is still the best at size.**

  | asset | 30-day funding | at the floor | excess on capital |
  |---|---:|---:|---:|
  | HYPE | 9.39% | 75% of hours | +5.09pp |
  | BTC (UBTC) | 8.88% | 63% of hours | +4.58pp |

  Portfolio margin lists exactly five reserves in the API (`allBorrowLendReserveStates`):
  - HYPE (LTV 0.65) and UBTC (0.50) as collateral;
  - USDC, USDT0 and USDH as borrowable stables (USDH is in the API but not in the docs' caps list).
- **642 collateral/perp pairs settle at the floor on at least half of the last 30 days' settlements.**
  - By venue: Binance 298, Bybit 208, OKX 134, Hyperliquid 2.
  - With a collateral ratio of 0.4 or more, capital per dollar of short is 1, and a perp that always pays the floor
    clears the savings rate by 7.15pp.
  - 383 pairs clear 2pp. Of the 106 books read, only one row clears both bars (2pp, and $1M within 25bp on both legs):
    Deribit XRP. Deribit funding has no interest leg, so that row is premium, not a floor rent. Its 7-day excess is
    already negative.
- **Sitting at the floor is not earning the carry.** MAGIC, KAIA, ERA and OGN sat at the floor on 73–89% of settlements
  yet paid −20% to −94% a year over 30 days through negative spikes.

## The lists (baseline 2026-10-11)

| venue | program | assets | notable (collateral ratio, first tier) |
|---|---|---:|---|
| Hyperliquid | portfolio margin | 5 reserves | HYPE 0.65, UBTC 0.50; USDC / USDT0 / USDH borrowable; per-user caps HYPE 1M ($85.5M), BTC 200 ($16.6M) |
| Hyperliquid | HIP-3 dexes | 11 | all stablecoin collateral (USDC ×6, USDH ×3, USDE ×1 not borrowable, USDT0 ×1); six have no live markets |
| Binance | portfolio margin | 488 (Pro tiers 496) | HYPE 0.70 (0.99 at $1M on Pro), XAUT/PAXG 0.80, WBETH 0.95, BNSOL 0.80, AERO 0.30, VELODROME 0.10; 91 tokenized stocks at 0.5–0.7 |
| Binance | multi-assets mode | 12 | BTC 0.95, ETH 0.95 |
| OKX | multi-currency margin | 273 of 1,173 | HYPE 0.95 (0.85 at $1M), DOGE 0.94 |
| Bybit | unified account | 268 | HYPE 0.80, XAUT 0.90, stETH 0.98 |
| Deribit | cross collateral | 21 | HYPE/SOL 0.85, PAXG 0.95; negative equity costs 0.05% a day |

## Top same-venue carries (30-day excess on capital)

| venue | asset → perp | 30d / 7d APR | at floor 30d | c | K | excess 30d (7d) | $ within 25bp, perp / spot |
|---|---|---|---:|---:|---:|---|---|
| Hyperliquid | HYPE | 9.39% / 8.40% | 75% | 0.65 | 1.00 | +5.09pp (+4.10) | $185k / $159k |
| Hyperliquid | UBTC → BTC | 8.88% / 8.50% | 63% | 0.50 | 1.00 | +4.58pp (+4.20) | $4.3M / $574k |
| Binance | ENA | 8.73% / 8.48% | 68% | 0.60 | 1.00 | +4.93pp | $312k / $165k |
| Binance | AERO | 9.46% / 10.49% | 80% | 0.30 | 1.15 | +4.43pp | $60k / $24k |
| Binance | HYPE | 5.67% / 6.46% | 51% | 0.70 | 1.00 | +1.87pp | — |
| OKX | OKB | 9.37% / 10.26% | 84% | 0.72 | 1.00 | +5.57pp | $53k / $68k |
| OKX | DOGE | 7.54% / 4.11% | 54% | 0.94 | 1.00 | +3.74pp | $1.49M / $585k |
| Bybit | XAUT | 6.48% | 59% | 0.85 | 1.00 | +2.68pp | $1.16M / $386k |
| Deribit | XRP | 8.65% / 2.54% | premium (no floor) | 0.85 | 1.00 | +4.85pp (−1.26) | $1.48M / $1.32M |

- K = 1 + max(0, im + 0.5 − 1.5c): the capital per dollar of short that survives a 50% rally without a top-up; im is
  the initial margin. Excess = (funding − borrow + known collateral yield) / K − SSR (3.80%), gross of trading costs.
- **Binance's raw ranking is topped by unusable rows.**
  - Stock tokens lead (BNCB +18.2pp, CRCLB +11.9pp), but their TradFi perps have no interest leg and nothing public
    says portfolio margin covers them. Their spot books hold under $54k within 25bp.
  - Below them come thin coins with c = 0.1. Bybit's top rows (GRVT, EGLD) are similar.

## What follows

- **The next study is running: the alt floor-carry basket.**
  - The question: does a diversified basket of collateral-eligible alts, chosen by trailing floor persistence, beat
    the savings rate out of sample after spikes, basis moves, delistings and costs?
  - The rent map estimated $0–0.3M accessible but never tested it.
  - A carry held for weeks can be built over days, so the 25bp-depth snapshot above understates capacity. The exit in
    a crash is the tail.
- **The watcher is the alarm for the HYPE pattern.** The next listing to look for: Hyperliquid accepting kHYPE, ETH,
  SOL or XAUT0 as portfolio-margin collateral. That would turn each into a same-venue carry at the formula rate.

## Endpoint gaps

- Hyperliquid's API has no caps or account requirements; they are parsed from the docs and the sections hashed.
- Binance's official collateral endpoints need a key. The public website endpoints used here are undocumented.
- Deribit's standard-margin haircuts come from a support article (hashed).
- Bybit's account-level collateral endpoint needs a key. Its single collateralRatio field is deprecated (HYPE 0.6
  there against 0.8 in the tiers).
- Only Hyperliquid publishes the cost of negative portfolio-margin balances; elsewhere margin borrow rates stand in.
- Staking yields are not counted, except Deribit's stETH.

## Errors found in the worker's own work (all fixed before the final outputs)

1. Tier bounds above 9.9e10 were read as "no limit", which double-counted tiers for tiny-priced coins (SATS ratio
   3.86). The baseline was rebuilt from its raw files (`snapshot --from-raw`).
2. The depth checks first picked the highest-excess rows, which have the thinnest books. They now go by perp volume.
3. A most-common-rate check fired whenever a funding interval changed inside the window. KAIA moved to 1-hour
   settlements; OKX's ONDO and ENA moved from 4 to 8 hours.
4. Capping covered days at 30 overstated the APR by 1/720 when 721 hourly settlements fell in a window.
5. A debug snapshot landed under the UTC date 2026-10-10 and was deleted, so the baseline is dated 2026-10-11.

## Coordinator's check

Recomputed from `carry_inputs/funding_hyperliquid.json.gz` alone, over the 30 days to `computed_at_ms` in
`carry.json`:

| asset | settlements | APR | at the floor | APR − 0.50% borrow − 3.80% SSR |
|---|---:|---:|---:|---:|
| HYPE | 720 | 9.3900% | 75% | **+5.09pp** |
| BTC | 720 | 8.8771% | 63% | **+4.58pp** |

That matches the table. The worker also cross-checked both coins against `perp_daily`'s store over the same window
(HYPE 9.392%, BTC 8.917%; n = 721 each, the window boundary differing by one settlement).
