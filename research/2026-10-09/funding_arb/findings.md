# Funding spreads between Hyperliquid and the CEX perps: real, persistent, and only where the book is a few thousand dollars deep — 2026-10-09

Same coin, three venues, three funding rates. A trader short where funding is high and long where it is low holds no
coin exposure and collects the difference. This study measures that spread for a year on every Hyperliquid core perp
against Binance and Bybit, with OKX for the last quarter (`scripts/funding_arb.py`). Rules are chosen on the first half
and tested once on the second, and priced at the size the live books allow.

The spread is real and persistent, and it pays per unit traded. It does not pay at any size worth running, because it
sits in coins whose Hyperliquid book holds under $5k within 10bp, and in markets about to be delisted. **No variant goes
into the book.** Every number below is in `analysis.json`, `analysis_split0601.json` or `tables.md`.

## 1. Data and method

- **Hyperliquid**
  - Source: the shared store `research/2026-10-09/perps_history`. It has hourly funding with the premium for 336
    markets from 2025-10-01 to 2026-10-09. Its hourly candles exist only for the last 5,000 hours, starting 2026-03-15.
  - HL price path: real closes plus a fill-in. Hourly closes are used from mid-March. Before that, 4-hour closes for
    199 coins (5,000 bars reach back about 830 days). Between those closes, the HL price is estimated from the exchange
    leg's close through the two premium indices, in HL's own units.
  - 69.1% of live HL hours have a real close.
  - Check on the estimate: on 245 test trades with real closes on both legs, the real basis averaged 13.1bp a trade and
    the estimate 8.3bp. The correlation per trade is only 0.17, with a mean absolute gap of 27.2bp. So the estimate is
    noisy trade by trade. It only affects the first half, between 4-hour closes.
  - Robustness: a second split puts both halves on real hourly closes (grid from 2026-03-15, test from 2026-06-01).
- **Exchanges**
  - Binance and Bybit: funding at each settlement timestamp, plus hourly premium-index and trade candles from
    2025-09-25.
  - Settlement intervals change: 29 Binance and 45 Bybit symbols changed theirs during the year.
  - OKX: funding and candles from 2026-06-29 only, because its API keeps about three months.
- **Survivorship**
  - Of 56 delisted HL perps, 47 also had an exchange listing, and 21 traded inside the study. A delisted HL market keeps
    printing hourly rows with rate and premium both exactly zero; those rows count as not trading.
  - 23 exchange perps delisted during the study are included.
  - 384 listings were price-checked against HL. One was dropped (Bybit PURR).
  - Seven quote a different coin unit (TURBO on Bybit, kNEIRO on Binance, the k-coins on OKX), and are converted.
- **Pricing**
  - Positions are a fixed quantity from entry, priced on price levels. Funding is paid at each venue's own settlements.
  - Taker fees: HL 4.5, Binance 5, Bybit 5.5, OKX 5 bp, plus live half-spreads.
  - Capital is one leg's notional, i.e. each leg margined at 2x on its own venue. Savings rate (SSR) 3.80%.
- **Protocol**
  - 106 variants per pair:
    - Fast family: trailing 1, 3 or 7-day spread; entry at 10–100% a year; exit when the spread falls below 0 or half
      the entry level; maximum hold of 7 days, 30 days or none; decided every 4 hours.
    - Slow family: trailing 30 or 90 days; entry at 2–8%; decided weekly.
  - The variant is chosen by daily Sharpe on the first half. The Sharpe series charges one unit of capital to every
    coin with a live pair, idle or not ("reserved capital").
  - Also: a monthly walk-forward. The study tried 361 variants in total.
- **Capacity**
  - Live books on 2026-10-10 between 10:18 and 10:28 UTC: Binance 184, Bybit 183, OKX 149, Hyperliquid 178 perps and
    19 spot books. HL was read at no more than one call a second.
  - Per coin, capacity is the size whose slippage stays within 10bp on every leg in both directions, capped at 5% of the
    smaller open interest.

## 2. What the spread is

| pair (A − B) | coins | median coin mean | coins with A > B | median absolute | same sign both halves | correlation of coin means, first half vs second |
|---|---:|---:|---:|---:|---:|---:|
| Hyperliquid − Binance | 191 | +1.39% | 61% | 4.06% | 71% | 0.42 |
| Hyperliquid − Bybit | 192 | +1.54% | 59% | 5.00% | 67% | 0.32 |
| Binance − Bybit | 186 | −0.65% | 40% | 2.36% | 58% | 0.12 |

- When their premium is small, all venues charge the same interest rate: 10.95% a year. The median HL coin spent 59% of
  its hours exactly at the 1.25bp-an-hour floor.
- HL's 4%-an-hour cap never bound in 1.64 million coin-hours.
- On BTC since July, funding ran at 8.9% on Hyperliquid, 6.2% on Binance, 5.6% on OKX and 4.7% on Bybit.
- How to read it: one set of traders sets HL's premium and another sets the exchanges'. The two exchanges share theirs,
  so their coin-level spreads don't persist (0.12) while HL's against them do (0.42). But the persistent part is small:
  a median of 4% a year, which is about the savings rate.

## 3. Results

| variant | rule chosen on the first half | test, per year of position held (trades opened in the test) | test, marked daily | test t (30-day lag) | live capacity, $/yr (after savings rate) | verdict |
|---|---|---:|---:|---:|---:|---|
| (i) HL vs Binance | `k168_X20_Yzero_Hinf` | 9.7% on 319 trades (maker 12.5%) | 12.9% | 6.05 (5.15) | −$19k (−$66k) on $1.23M average | no-go |
| (ii) HL vs Bybit | `slow_k90d_X6_Yzero` | 3.5% on 90 trades | 5.0% | 8.08 (6.99) | −$15k (−$31k) on $431k | no-go |
| (iii) Binance vs Bybit (control) | `slow_k30d_X4_Yzero` | −0.4% on 200 trades | 1.2% | 1.92 (2.60) | −$20k (−$54k) on $881k | no-go, as expected |
| (iv) HL spot–perp | `k24_X20_Yzero` | t 1.62; 21.3% on capital (always-on 4.6%) | — | — | chosen $7k; always-on $74k | no-go |
| (v) HL carry factor | `k168_q20_dollar` | test Sharpe 0.10 (first half 1.08) | — | 0.08 | — | no-go |

Rule names read as: trailing hours, entry level in % a year, exit level, maximum hold. So `k168_X20_Yzero_Hinf` means:
short the venue with the higher funding when the trailing 7-day spread is above 20% a year, close when it changes sign,
no maximum hold.

## 4. Why the HL–Binance edge doesn't reach the book

**Per unit, it holds.**
- Every month from October 2025 to October 2026 was positive, from 2.7% (February) to 21.2% (April), marked daily.
- The ten best variants on the first half were all positive on the second: median 7.6%, worst 5.1%.
- 81% of the 106 variants beat the savings rate per unit, and 92 of 106 pass a false-discovery test at 10%.
- Deflated Sharpe: 0.971 after allowing for the 60 effectively independent variants tried, and 0.936 against all 361
  in the study.
- Both directions pay: short HL earned 10.3% a year, short Binance 8.9%.

**It lives in thin books.** The same test trades grouped by the coin's capacity at 10bp:

| coin capacity | coins | trades | net bp per trade | net per year of position held |
|---|---:|---:|---:|---:|
| under $5k | 66 | 163 | 66.0 | 9.5% |
| $5k–25k | 41 | 93 | 13.9 | 2.0% |
| $25k–100k | 20 | 29 | 16.2 | 1.5% |
| over $100k | 5 | 7 | 50.4 | 3.5% |

- **Delisted coins:** 43% of the test-period profit came from 13 coins that have since lost their HL book: MAVIA,
  ZEREBRO, TST, IP, PROMPT, DOOD, ARK, TON, MEW, CHILLGUY, HMSTR, NOT and XAI. They earned 92% a year: funding blows out
  on a market heading for delisting. Coins still listed made 5.8% a year even at small size.
- **At real sizes:**
  - At full live capacity, the book loses $19k a year. ZEC alone is 42% of the average capital.
  - Capping every coin at $10k leaves $1.3k a year on $228k (0.6%), −$7k after the savings rate. At $25k it loses
    $1.2k, at $50k $3.5k.
- **Margin:** the two legs sit on different venues, so a hedged pair is two separate positions to each venue's risk
  engine. 50% of test trades saw a 25% move against one leg while held, and 21% a 40% move. The collateral has to be
  moved before the losing leg is liquidated.
- **Both halves on real closes** (test from 2026-06-01): the chosen rule (`k168_X10_Yzero_Hinf`) shows 7.6% marked
  daily (t 9.90), but only 1.8% a year on trades opened in the test. The pattern by capacity is the same: under $5k
  6.6%, $5–25k −2.6%, $25–100k −2.7%, over $100k 0.7%.
- **On OKX:** the same rule from 2026-07-06 made −3.0% a year on 141 trades. Against Binance over the same dates it made
  +2.9% on 162. The last quarter is the weakest stretch of the year.

## 5. Who cannot arbitrage it

- **Liquid coins: nobody needs to.** HL's BTC funding premium over the exchanges (2.7–4.2 points) is about the cost of
  the capital a two-venue hedge ties up: one leg's notional at 3.80%. The structural spread is priced at the cost of
  capital.
- **Thin coins: depth and delisting.** Where the spread is wide, the barrier is the HL book, which holds under $5k within
  10bp, and the delisting process, where funding runs at 90% a year. Neither scales.
- **What KYC and siloed margin explain.** Binance is closed to US persons, who are a large share of HL's flow, and each
  venue margins its own leg. That is why the coin-level structure persists between HL and the exchanges and not between
  the two exchanges. But what's left over is smaller than the savings rate once fees and basis are paid.

## 6. What went wrong and was fixed

- **Mixed units.** Seven listings quote a different coin unit. Prices estimated from the other leg mixed those units,
  and one coin (TURBO on Bybit) showed a 1,000x jump in its daily marks. That broke HL vs Bybit's first half (Sharpe
  0.05, maximum drawdown 761%) and moved the HL vs Binance choice. Fixed with a unit ratio and pinned by a test.
- **Log returns.** Summing log returns overstated the basis 3.6x on SAGA, a coin that fell 73% while held. Replaced by
  fixed-quantity pricing on price levels.
- **End of data.** A price check at the last hour compared different hours on the two legs. Fixed.
- **Spot namesakes.** Four HL spot tokens share a ticker with a perp but are different assets: TRUMP @9, PUMP @20, BERA
  @117 and MON @129 (price ratios 0.0001, 0.05, 0.003, 0.36). The Unit-bridged tokens UPUMP and UMON are the real
  assets, picked by price ratio.
- **The slow family was added late.** It was added after a preliminary run showed persistent coin-level spreads in a
  profile table that included the test half. The variant within the family was still chosen on the first half only.
- **One statistic is uninformative here.** The deflated Sharpe that uses the spread of Sharpe ratios across variants
  comes out as 0.000 when nearly all variants are positive, so nothing is read into it.

## 7. Verdict and watch criteria

No entry. HL vs Binance stays a watch item. It becomes a strategy candidate only if all three hold:
- coins with more than $25k of capacity earn over 5% a year on positions held across a trailing 90 days;
- the first-half/second-half correlation of coin spreads stays above 0.3;
- the Binance vs Bybit control stays below the savings rate.

## 8. What next

1. **The delisting squeeze.** An event study of HL delisting announcements: the funding path, book depth and settlement
   price, to see whether any of the 92%-a-year pre-delisting spread can be captured at size.
2. **Binance's 217 TradFi perpetuals** (XAU, TSLA, MSTR, COIN…) against the HIP-3 xyz markets: a new pair family.
3. **Permissionless control.** Compare HL with Lighter, Aster or edgeX. If coin-level structure persists between two
   venues without KYC, KYC is not what segments the traders.
4. **Patient execution.** Capacity here is instantaneous. Building a position over hours from hourly volume would size
   larger in thin coins.
5. **HYPE and ZEC spot–perp carry.** Always-on, these made 8.8% and 20.7% on capital in the test half, with $123k and
   $53k of capacity at 10bp. Both are single coins over a single half-year; worth rechecking with the HYPE staking yield
   (2.18%) added to the spot leg.

## Errata (2026-10-10)

Found by `research/2026-10-10/listing_lifecycle` and checked by the coordinator; the numbers above are left as
published.

- §2, "the 1.25bp-an-hour floor": the interest-only floor is 1.25e-5 an hour, **0.125bp an hour**. The 10.95% a year in
  the same sentence is right.
- §4, "13 coins that have since lost their HL book": **HMSTR, NOT and XAI are still listed** on Hyperliquid (open
  interest $1.46M, $97k and $375k in this study's own snapshot). They scored zero capacity because their half-spreads
  (30, 10.6 and 10.5bp) exceed the 10bp cap, not because they were delisted. The ten truly delisted coins earned about
  234% a year of position held, 58% of it from MAVIA, and almost all of it 1–4 weeks before any delisting notice, in
  books under $5k: the delisting event study finds none of the "pre-delisting" spread capturable at $10k.
- §1 and every Hyperliquid `candleSnapshot` series: the venue returns zero-volume bars, with prices, for days to years
  before a market first traded (ZEC: 999 daily bars before 2025-10-02). This study treated a coin without funding rows
  as not live, so the effect here is probably small; any study that dates a listing from the first bar is wrong.
- The HYPE spot–perp carry in item 5 was taken up by `research/2026-10-10/term_carry`: with HYPE spot as Hyperliquid
  portfolio-margin collateral it beat the savings rate by +4.30% a year out of sample (t 5.68).
