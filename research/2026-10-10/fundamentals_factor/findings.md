# On-chain fundamentals against token returns — 2026-10-10

The question is whether chain activity (stablecoins arriving, DEX volume, fees, TVL) predicts the chain token's return,
and whether protocol fees and revenue (their growth, and their size relative to value) predict the protocol token's. It
is also the test of the chain-activity framework's purpose, "detect new activity on chains where it is reasonable to
trade". `scripts/fundamentals_factor.py` answers it two ways: weekly cross-sectional books on the perps (Binance USD-M,
or Hyperliquid where Binance has none), hedged, net of funding and costs, chosen on the first half and tested once on
the second; and a point-in-time replay of the framework's own detectors. Numbers in `analysis.json`, tables in
`tables.md`.

**Verdict: no-go on both families, no book entry.** Chain flows and protocol fees/value do not predict token returns
once the variant is chosen on the first half and tested on the second, net of costs and funding. The framework's "new
activity", replayed day by day over five years, predicts nothing tradable: activity and price move together, and by the
time a day's reading is complete the move is in the price.

## What was measured

**Data (all free; nothing answered 402).**
- DefiLlama, 134 chains: stablecoin float (`stablecoins.llama.fi/stablecoincharts/{chain}`), TVL
  (`/v2/historicalChainTvl`), DEX volume (`/overview/dexs/{chain}`) and fees including gas (`/overview/fees/{chain}`).
- DefiLlama, 281 protocols: fees and revenue (`/summary/fees/{slug}`, parents aggregated), plus the all-chain stablecoin
  total.
- Binance: daily perp bars for 424 symbols, delisted ones included (the `data.binance.vision` listing names every perp
  symbol ever traded, and the API still serves purged ones such as MATICUSDT and LUNAUSDT); funding for every symbol that
  ever cleared the liquidity floor; Hyperliquid funding for the 24 coins that are some token's only venue; Hyperliquid
  daily candles for 161 coins; live books read 2026-10-10 at 11:47 UTC; CoinGecko supplies (free history capped at
  365 days).

**Universe.** A token pair is kept when the venue price is within 25% of DefiLlama's price for that CoinGecko id on the
median day the symbol traded: 199 chain pairs and 376 protocol pairs kept, 10 and 148 rejected. Four migrations named by
hand (MATIC→POL, KLAY→KAIA, EOS→A, MKR→SKY); 33 bridge or foundation "protocols" and XAUT excluded from the protocol
family (HYPE, DYDX, RUNE, INJ, FRAX kept as app-chains). A name must have traded the day before with at least $5M a day
over 28 days: 126 chain tokens and 245 protocol tokens were ever tradable, about 20–31 names a week.

**Signals** (34 variants: 17 signals × dollar-neutral or BTC-beta-neutral).
- Chain: 4- and 12-week log growth of stablecoin float (7-day mean, floor $10M), DEX volume (28-day mean, floor $250k a
  day), fees (floor $10k a day) and TVL (floor $20M); the 4-week change in the chain's share of all stablecoins, in
  percentage points; a composite.
- Protocol: 4- and 12-week growth of fees (floor $10k a day) and revenue (floor $3k a day); fees and revenue over FDV
  (capped max supply where there is one, otherwise today's total); a composite. Control: price momentum.

**Book.** Rebalance Mondays 00:00 UTC on data up to Saturday (one full day of publication lag); returns Sunday close to
Sunday close; long the top tercile, short the bottom, equal weight, $1 a side; 15bp a side on drift-adjusted turnover
(6bp for the BTC hedge), plus funding paid or received.

**Protocol.** Best in-sample Sharpe with at least 26 weeks; cutoffs 2024-01-08 for chains (data from 2021-04-12) and
2024-01-22 for protocols (from 2021-05-03); Newey–West t; Benjamini–Hochberg at q = 0.10 over the variants and over the
ICs; deflated Sharpe; walk-forward (choose on 104 weeks, hold 26); a 200-run placebo with the signal shuffled within each
week; drop-one-token; regression on the momentum book.

**Replay of the framework.** `chain_surge` (DEX and fees over 1 and 7 days, TVL over 7, with the same ratio, empirical p,
floors and market-excess test) and `stable_inflow`, replayed for every day using only data up to that day; the first
fire per token and type in 28 days counts. The replay matches `surge_stats` to machine precision (unit test) and the
10-09/10-10 readings exactly. Trade: long the token from the close of the day after the data day, for 7 or 28 days,
hedged with BTC or with a basket of other chain tokens (16 variants); placebo the same token 45 days either side.

## What it found

| test | in sample | out of sample | t | note |
|---|---|---|---|---|
| chains, chosen: 4-week fee growth, dollar-neutral | +62.3%/yr, Sharpe 1.43, only 38 weeks | −5.9%/yr | NW −0.31 | ranked 15th of 20 out of sample; deflated Sharpe 0.42 (0.31 over all 66 variants tried); rank IC 0.0005 |
| chains, walk-forward | — | +12.4%/yr | 0.73 | windows swing between +78% and −33% |
| protocols, chosen: 12-week fee growth, beta-neutral | +87.8%/yr, Sharpe 1.36, 142 weeks | +2.3%/yr (+15.9% gross, −5.4% funding, −8.3% costs) | NW 0.07 | break-even cost 20bp a side |
| protocols, walk-forward | — | −5.4%/yr | −0.20 | |
| BH, q = 0.10, 34 long/short variants | — | — | — | no survivors; smallest adjusted p 0.89 (full sample), 0.99 (out of sample) |
| detector replay, chosen: DEX surge, long 28 days vs BTC | +3.54%/trade (t 1.89) | −0.78%/trade | by-day −0.93 | all 16 event variants lose out of sample; hit rates 19–40% |

**Chain flows: nothing survives.** ICs mostly within ±0.05. DEX-volume growth has an IC of −0.03 and loses 17% a year as
a book. TVL growth partly tracks the token's own price (rank correlation with 12-week momentum 0.34 to 0.44). A stricter
in-sample minimum (52 weeks) would have chosen 4-week TVL growth: +12.2% (t 0.81).

**Hindsight only: stablecoin-float growth.** Its out-of-sample rank IC is 0.041 (t 2.81), the only one of 17 signal ICs
that survives BH out of sample (adjusted p 0.085), and +27.9% a year as a book (t 1.52). But in sample its IC was 0.01
(adjusted p 0.93) and its book lost 21.2%; without its top three contributors (HBAR, ARB, ADA) it makes +5.5%; and it
lost 22% and 34% annualised in the two halves of 2026. A watch item on a frozen rule, not a strategy.

**Protocols worked until 2023.** Fee-growth IC by year: 0.11 (2021), 0.05, 0.04, then −0.01 (2024) and −0.02 (2025).
Fees over FDV: 0.12, 0.08, 0.06, then −0.00 and −0.02; out of sample it made −8.1% even with the supply look-ahead
favouring it.

**Detectors replayed: 1,792 events on 100 tokens** (from 12,279 detector-days).

| out of sample | vs BTC | by-day t | vs alt basket | by-day t |
|---|---|---|---|---|
| DEX surge, 7 days | −0.70% | −1.29 | −0.84% | −1.28 |
| DEX surge, 28 days (the in-sample choice; +3.54% in sample) | −0.78% | −0.93 | −0.67% | −0.50 |
| fee surge, 7 days | −1.39% | −1.98 | −1.29% | −2.43 |
| fee surge, 28 days | −1.57% | −0.92 | −0.44% | −0.21 |
| TVL surge, 7 days | −1.25% | −0.61 | −2.86% | −2.44 |
| TVL surge, 28 days | −8.95% | −2.04 | −3.30% | −1.02 |
| stablecoin inflow, 7 days | −1.42% | −1.49 | −1.06% | −1.01 |
| stablecoin inflow, 28 days | −4.39% | −2.64 | −1.67% | −0.32 |

All 16 variants lose. The DEX-surge 28-day excess over its own placebo (t 4.04) shrinks to t 1.39 once the alt basket
takes out the time effect: surges happen when alts as a group are strong. After a fee or TVL surge the token lags other
alts by 0.7–2.3% gross the next week, too little to short. The anecdote that shows why: STRK rose 28% from the close of
the 10-08 data day to 10-10, but fell 2.5% from the first close a trader could act on (10-09).

## Size

Nothing is sized. Live books, median cost per side including the 5bp taker fee:

| per name | chain tokens (73 names) | protocol tokens (94 names) |
|---|---|---|
| $25k | 18.9bp | 23.3bp |
| $100k | 37.4bp | 55.2bp |
| $250k | 69.7bp | 99.8bp |

So 15bp a side holds only at about $15–25k a name; weekly turnover is 0.8–1.4 of the $2 gross book, so costs run 6–11% a
year.

## Verdict

- **Chain flows:** no-go.
- **Protocol value and growth:** no-go. The effect was real in 2021–23 and has been zero since 2024.
- **Does the framework's "new activity" predict anything tradable?** No. Surges and inflows are followed by
  underperformance against BTC and, slightly, against other alts.
- **Watch item:** `stables_4w`, dollar-neutral terciles, $5M liquidity floor, 15bp a side, frozen. Re-run
  `fundamentals_factor.py analyze` after 2027-01; it earns a forward-tested row only if the new weeks alone show IC ≥ 0.04
  with NW t ≥ 2.

## What this cannot see

- **Vintage:** DefiLlama's history is downloaded today, after revisions and backfills.
- **Short stablecoin history:** most chains' series start 2022-05-12, and Terra Classic's starts that day at $10.1B, so
  the Terra/UST case cannot be tested.
- **Survivorship:** chains or protocols DefiLlama removed entirely are absent.
- **FDV** is not point in time where the token has no cap (a look-ahead that favours the signal, which still failed).
- **Costs:** a flat 15bp across six years. **Spot-only tokens** (CRO, OKB, FLR, RON, GNO, OSMO) have no perp.
  **Transactions and active addresses** have only about a year of history.

## What went wrong and was fixed

1. Binance's flat bars after delisting (68 pairs, 24,165 bars; TONUSDT, FTMUSDT, MKRUSDT) shadowed the venue the token
   moved to (TON → Hyperliquid "GRAM", MKR → SKY) and zeroed momentum and beta. Untraded bars are dropped everywhere and
   each week trades the first liquid venue; regression test added.
2. Hyperliquid's pre-listing bars (86 pairs, 44,686 bars) were already dropped from returns, but the identity check still
   chose its day from all bars and so compared settlement or pre-listing prices with DefiLlama's live price; fixing it
   recovered 14 wrongly rejected pairs (Raydium's RAY, GLMR, ORBS, BOND, ALPACA, ...). Neither trap changed the verdict.
3. DefiLlama serves "OP Mainnet" and "Optimism" as one series under two names (summed, they double OP's float):
   deduplicated.
4. The 33 bridge and foundation "protocols" carrying a chain token's CoinGecko id are excluded.
5. The share signal is measured in percentage points (in logs it ranks chains identically to float growth).
6. The placebo is compared gross (a shuffled book's net is about −21% a year of pure churn cost).
7. The event study gained a basket hedge, and events are chosen on P&L rather than on excess over placebo.
8. The partial intraday bar is excluded; DefiLlama's HTTP 500 answers (chains without an adapter) are cached.

## What next

1. Fix `chain_census.py`'s stablecoin history (done by the coordinator the same day; see below) and archive the census's
   raw DefiLlama responses daily, since its history is revised after the fact.
2. Point the framework at what flows move mechanically: lending rates and DEX depth on the chain the dollars arrive on —
   the repo's dollar book — not token timing.
3. Keep the stablecoin IC on its frozen rule and re-run after 2027-01.

## Coordinator's check (2026-10-10)

- The replay's anchor readings are the framework's own: `research/2026-10-09/chains/detectors.json` has
  `Starknet:dex:d1` at ratio 3.611 on 2026-10-08, and `research/2026-10-10/chains/detectors.json` has `Starknet:dex:d1`
  at 4.119 and `TON:dex:d1` at 3.611 on 2026-10-09, exactly as the study reports.
- The census bug is real and is fixed: `chain_census.py` read DefiLlama's missing stablecoin day (`totalCirculatingUSD:
  {}`) as 0 when building the history, and normalised every history series with `float(b or 0)`. A new `stable_points`
  keeps a missing reading as None and the normalisation keeps None, which `complete_days` already drops; pinned by
  `test_a_missing_stablecoin_reading_is_a_gap_not_a_zero`. None of the chain-level `stable_inflow` hits in the 10-09 and
  10-10 windows rests on a zero baseline, so no recorded finding came from the bug; the windows' raw history files still
  hold the zeros, and the next daily pass refetches clean history.
