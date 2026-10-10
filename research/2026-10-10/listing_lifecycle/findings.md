# The life cycle of a perp: new listings bleed, delistings squeeze, and neither trades at size — 2026-10-10

Two questions about the ends of a market's life on Hyperliquid (`scripts/listing_lifecycle.py`):

- **(a) New listings.** Does a newly listed core perp lose value against seasoned alts in its first weeks, after the
  funding a short pays?
- **(b) Delistings.** What happens between a delisting notice and the settlement, on Hyperliquid and on Binance? Can any
  of it be captured at $10k–$100k an event, including the 92%-a-year "pre-delisting" spread credited in
  `research/2026-10-09/funding_arb`?

The rules are slow (hours to weeks, no race for latency or block position). Variants are chosen on the first half of
events and tested once on the second. Every number below is in `analysis.json` or `tables.md`.

**Verdict (a): no entry, a forward-test watch item.** The decay is real as a description: the median new token trails
the seasoned-alt basket by 25% after 30 days and 33% after 60. But the protocol's pick failed its test (listing-week
t 1.01), against the basket the same window earned +2.3% (t −0.10), and the trade is a short on lottery tickets: 16% of
test trades saw the coin double while held.

**Verdict (b): closed.** The Binance notice-period drift held in the first half (+15.0% an event) and reversed in the
second (−3.5%). Perp-against-spot lost (−1.9% an event). None of the 92% a year survives at $10k: it was earned weeks
before any notice, in books a few thousand dollars deep.

## 1. Data and method

**Listing calendar.** Every core perp Hyperliquid has listed: 234, live and delisted.

- Inputs: daily candles (one `candleSnapshot` call each, all history), hourly funding from the shared store (from
  2025-10-01), the funding study's delisted extras, and 1,002 `fundingHistory` pages fetched for the months before the
  store. All Hyperliquid calls went through `perp_rpc.Info` at 1.2–1.5 s spacing; 5 were throttled.
- **Listing = the first UTC day with a trade.** `candleSnapshot` returns zero-volume bars before a market opened, so the
  first bar is not the listing (§8, item 1).
- Sample: listings from 2024-01-01 to 2026-09-08, leaving out migrations of seasoned coins (RNDR→RENDER, MATIC→POL,
  FTM→S, MKR→SKY) and PAXG: **129 listings**.

  | quarter | 24Q1 | 24Q2 | 24Q3 | 24Q4 | 25Q1 | 25Q2 | 25Q3 | 25Q4 | 26Q1 | 26Q2 | 26Q3 |
  |---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
  | listings | 22 | 17 | 5 | 20 | 20 | 12 | 12 | 11 | 5 | 1 | 4 |

  The pace has collapsed: 10 listings in the first three quarters of 2026.
- **Cohorts**, from the first USDT/USDC perp on Binance or Bybit (delisted ones included): established (first CEX perp
  more than 60 days earlier) 26 — old coins new to Hyperliquid, such as ZEC, XMR, ICP and the 2024 batch of HBAR, XLM,
  SAND and ALGO; pre-launch (Hyperliquid first by at least two days, its "hyperps") 10; new tokens 91;
  Hyperliquid-only 2.

**The listing trade.**

- Entry: short at the daily close ending UTC day d+1 (the listing day is day 1), d ∈ {1, 3, 7}. Hold H ∈ {7, 14, 30, 60}
  days.
- Hedge: long the same notional of (i) BTC or (ii) an equal-weight basket of seasoned Hyperliquid alts (listed more than
  180 days before entry; 125–157 coins in 2025; delisted coins count while they traded and close at their last price).
- P&L = −coin return + hedge return + the funding the short receives (each day's rate times the coin's price that day
  over the entry price) − the hedge's funding − both round trips.
- Round trips at $25k a leg from today's books: the coin's own book where it has one (104 listings), otherwise the median
  of its listing year (25 delisted coins; median 46bp); BTC 9.1bp; the basket 11.4bp.
- Placebo: the same coin and window, entered 90 days later.
- Choose-then-test: 24 variants (3 d × 4 H × 2 hedges), chosen on listings before 2025-01-01 (the median listing date)
  by the t-statistic of listing-week means, tested once on the rest.

**Delistings.**

- **Binance.** Notices from the CMS "Delisting" catalog (161): 200 notices back to February 2025, 45 of which delist
  USD-M perps; bodies parsed for the settlement and reduce-only times. Settlement times from exchangeInfo
  `deliveryDate` (delisted contracts stay listed as SETTLING). Per symbol: funding, premium-index and trade klines from
  fapi; spot klines and daily 5-minute open interest from `data.binance.vision`. Result: 95 USD-M delistings settled
  2025-09-15 → 2026-10-05; 89 have a notice, on 34 dates (the other six — OMNI, AI16Z, FXS, OM, TON, STG — are migrations
  or rebrands that were never in the catalog).
- **Hyperliquid.** 21 delistings in the store's year, on 10 dates. The last trading hour is the last funding row before
  rate and premium turn exactly zero. The notice time is not in the API: it is inferred as the first hour whose trailing
  4h volume exceeds 8× the median of the two weeks before (14 of 21 show such a burst).
- **Hedge:** an hourly equal-weight basket of seasoned Binance perps (the funding study's 1h klines).
- **Costs:** fees Binance 5bp, Hyperliquid 4.5bp, Binance spot 10bp; half-spread plus impact against depth within 1% of
  mid, set to a fixed share of 24h volume measured on today's books (2.6% of volume on Binance, 5.1% on Hyperliquid).
- **Variants:** entry 2, 8 or 24 hours after the notice; exit one hour before the earlier of the first stated settlement
  and the actual one (before the 30-minute reduce-only window).

## 2. (a) What a new listing does

Mean (median) cumulative return of new listings over the seasoned basket, entry at the first daily close:

| day | listings | over the basket | over BTC | funding to the short |
|---:|---:|---:|---:|---:|
| 7 | 129 | −2.2% (−12.9%) | −5.0% | −0.09% |
| 30 | 129 | −11.3% (−22.8%) | −16.9% | +0.84% |
| 60 | 126 | −18.2% (−30.3%) | −33.3% | +1.53% |
| 90 | 126 | −21.0% (−32.3%) | −41.5% | +1.28% |

- By cohort, over the basket at day 60: new tokens −19.3% (median −32.6%), pre-launch −27.9% (−33.3%), established coins
  −6.6% (−15.1%). The gap between median and mean is the right tail: a new perp falls more often than not, and
  occasionally triples.
- Funding hardly charges for it: over all listings a short received +1.5% over 60 days; in the test half it paid −2.7%
  over 30 days and −4.4% over 60 while the coin fell 30.9% and 45.2%. The funding is concentrated in the squeezes (KAITO's
  short paid 21.4% in 30 days while the coin briefly doubled).

## 3. (a) The protocol's result

| rule (d, H, hedge) | in sample: mean, week t | test: n, mean, median, hit | test week t | placebo | test excess over own placebo (week t) |
|---|---:|---:|---:|---:|---:|
| **d7_H60_btc (chosen)** | +32.5%, 3.49 | 63, **+17.4%**, +37.9%, 83% | **1.01** | −1.8% | +25.6% (2.04) |
| d7_H60_basket | +21.6%, 2.17 | 63, **+2.3%**, +20.1%, 75% | −0.10 | −8.7% | +16.7% (1.46) |
| d1_H30_basket | +8.8%, 0.77 | 65, +14.6%, +24.0%, 83% | 2.89 | −7.3% | +21.3% (2.16) |
| d1_H60_basket | +19.8%, 2.10 | 63, +13.6%, +26.8%, 81% | 3.17 | −10.5% | +24.2% (2.41) |

P&L is per trade, as a fraction of one leg's notional, after costs.

- **The chosen rule did not hold.** The three 60-day BTC-hedged rules were the only in-sample survivors of a
  false-discovery test at q = 0.10; the chosen one has a deflated Sharpe of 0.63 against 24 tries. In the test its mean
  stayed positive (plain t 2.13), but by listing week t is 1.01, and it ranked 18th of 24. Hedged with the seasoned
  basket, the same window earned +2.3%: in the test half the basket fell 23.3% while the new coins fell 30.3%. Most of
  the BTC-hedged "decay" is the whole alt market falling against BTC — the unlock study's warning.
- **What held was not chosen.** Early, basket-hedged entries held out of sample (d1_H30_basket t 2.89, d1_H60_basket
  t 3.17) after unremarkable in-sample results (t 0.77 and 2.10). Preferring them now would be a choice made after
  seeing the test; it goes to a forward test instead.
- **Squeezes size the trade, not costs.** In the chosen rule's test trades the coin's daily high rose more than 50%
  above entry in 30% of trades, more than doubled in 16%, and peaked at +694%; 11% of trades lost more than half the
  notional (worst LAYER +238%, JELLY +202%, CASHCAT +194%, ZEC +90%). New listings mostly carry 3x maximum leverage, so
  a short that cannot post twice its notional is liquidated. Closing every trade at a +100% adverse move (1x margin)
  cuts d1_H30_basket to +12.9% (t 1.90), d1_H60_basket to +7.9% (t 1.29) and the chosen rule to +12.8% (t 0.35).

Cohorts (chosen rule, all listings; these splits were not part of the choice):

| cohort | n | mean | week t | test-half mean |
|---|---:|---:|---:|---:|
| New tokens | 90 | +28.7% | 4.31 | +26.7% |
| Established | 25 | +18.9% | 1.61 | −0.1% |
| Binance perp at entry | 100 | +25.3% | 3.80 | — |
| No Binance perp | 27 | +23.9% | 1.29 | −3.9% (n 10) |
| Airdrop allocation in DefiLlama's schedule | 35 | +25.1% | 4.00 | +10.5% |
| No airdrop | 23 | +12.4% | — | — |
| FDV at listing > $3B | 31 | +28.9% | 4.11 | — |
| FDV $0.5–3B | 25 | +7.6% | 0.47 | — |

The decay belongs to large-FDV new tokens with airdrops, which is the folklore (FDV known for 58 listings).

## 4. (a) Size

Only today's books exist, so "the first weeks" are the four coins listed in the last 120 days (GRAM, CASHCAT, PONS,
USELESS):

| listing age | coins | median depth ±50bp | round trip $25k | $50k | $100k | $250k | fills $100k inside the shown book |
|---|---:|---:|---:|---:|---:|---:|---:|
| ≤120 days | 4 | $63k | 49bp | 70bp | 105bp | 221bp | 2 of 4 |
| 120–365 days | 13 | $35k | 48bp | 84bp | 159bp | 383bp | 23% |
| >365 days | 158 | $45k | 47bp | 70bp | 133bp | 319bp | 32% |

Against a 15–17% edge per trade, a round trip eats half the edge only at about $0.6–1.1M, so costs do not bind; margin
and squeezes do. Re-costed at $100k a leg, the chosen rule still averages +15.9% a trade (mean cost 2.3%), week t 0.86.
Ten listings a year at $50k would be about $75k a year gross before squeezes: even a rule that passed would be small.

## 5. (b) What happens on the way out

**Binance** (89 notices):

| measure | median | other |
|---|---:|---|
| notice period | 102 h | 0.5 h to 558 h |
| coin move in the 2 hours after the notice | −14.6% | 86% of notices fell |
| coin move vs the basket, notice + 2 h → settlement | −16.5% | mean −6.4%; 77% negative; the right tail is squeezes |
| coin move in the 24 hours before the notice | −1.0% | no leak to speak of |
| volume in the 24 hours after the notice | 8.8× | |
| open interest two hours before settlement | 62% of its level at the notice | |
| funding, week before the notice | +11%/yr | the floor |
| funding, notice → settlement | +39%/yr | mean +63%; positive in 66% |
| funding, last 24 hours | +79%/yr | mean +142%; up to +2,983% (RVV) |
| premium two hours before settlement | 0 | |
| spot, 7 days after the perp settles | −31.9% | 37 coins with spot data |

- The first two hours are a latency race and are excluded by the brief.
- Funding is positive: longs pay shorts. "Funding blows out" on Binance means the short gets paid.
- In the settlement hour the book is reduce-only and prints run away (mean premium +7.1%; CHESS +89%); that hour cannot
  be traded. Six settlements were moved after the first notice: KDA, FLM, PERP, FIS, REI and VOXEL.

**Hyperliquid** (21 delistings): most were quiet (funding at the floor, $20k–$500k a day of volume); the inferred
notice runs a median 105 hours; the last price sits a median 0.23% from the CEX price, so settlement is near the index.
A few markets blew out (annualised funding, last 30 days / last 24 hours): LAUNCHCOIN +169% / +3,478%, OM −461% /
−2,170%, ZEREBRO +233% / +857%; MAVIA +540% for its last 30 days.

## 6. (b) The trades

| trade | delay | n | mean an event at $25k | median | t by notice day | first half → second half |
|---|---:|---:|---:|---:|---:|---|
| Binance drift: short the perp, long the basket, to settlement | 2 h | 80 | +5.75% | +12.5% | 1.29 | +15.0% → **−3.5%** (t −0.75) |
| same | 24 h | 81 | +5.21% | +9.2% | 1.20 | +9.3% → +1.2% |
| Binance perp short, long spot (funding > 0) | 2 h | 34 | −1.90% | −1.1% | −2.34 | −0.7% → −3.1% |
| Binance against HL perp | 2 h | 3 | −0.58% | — | — | too few |
| HL drift | 2 h | 21 | −3.50% | −1.3% | −1.27 | — |
| HL vs CEX perp (short the higher funding) | 2 h | 17 | −4.56% | −2.0% | −2.12 | −1.4% → −7.4% |

- **Binance drift.** Placebo a month earlier: −2.3%. The first half's best delay (2 h) lost in the second half, and no
  delay held: the squeeze tail and the funding a short collects roughly cancel the drift.
- **Perp against spot** loses on basis: the perp rises against spot into the last hours; all 34 coins with a spot leg
  lose after costs.
- **The 92%-a-year spread.** On HL vs CEX the gross was +42% a year of position held at the 2-hour delay (−11% at 8 hours):
  about 0.3% an event over 65 hours. Net an event: −1.5% at $10k, −9.9% at $50k, −20.8% at $100k. **None of it survives**,
  at about 84 Binance notices (on 34 dates) and 21 Hyperliquid delistings (on 10 dates) a year.
- **Where it was earned.** Across the ten coins Hyperliquid really delisted, the HL-minus-Binance spread summed to
  7,979bp over the funding study's test period: 95% of it in the last 30 days before the last trading hour, 28% in the
  last 7, 2% in the last 24 hours. Most of it came 1–4 weeks before any notice (MAVIA 4,213bp, ZEREBRO 1,859bp, TST
  1,313bp): the spread of a dying, thin market, which the funding study's own rule already traded, in books under $5k.

## 7. Kill criteria and watch items

Nothing enters the book.

- **New listings: watch item, pre-registered forward test.** Short every new core listing at the close of its second
  UTC day, hold 30 days, long the seasoned basket, close at a +100% adverse move. Promote only if, after 30 listings, the
  mean beats both the placebo and the savings rate on twice the notional (the margin a squeeze needs), at a
  listing-week t above 2; drop if the mean over the basket is not positive after 30 listings. At about ten listings a
  year this takes about three years; pooling Binance and Bybit new perps would be faster.
- **Delistings: closed.** Reopen only on an observable Hyperliquid notice time, or a venue where the post-settlement spot
  decline (−32% median over 7 days) can be shorted.

## 8. What went wrong and was fixed

1. **Zero-volume bars before a listing.** `candleSnapshot` returns zero-volume bars for days, sometimes years, before a
   market traded: 124 of 234 coins. ZEC's bars start 2023-01-07 but it first traded 2025-10-02; ICP, XMR, AXS and DASH
   are similar; AERO by 342 days; MEW by 36. Taking the first bar as the listing would have misdated 44 of the 129
   listings by more than a day and priced pre-listing days nobody traded. Fixed: listing = the first traded bar; earlier
   bars are dropped; the funding fetch ranges were recomputed after the fix.
2. **The notice filter dropped real delistings.** "ALPHAUSDT" tripped an "alpha" exclusion meant for Binance Alpha, and
   "USDⓈ-Margined" tripped a "margin" exclusion meant for margin delistings; the ALPHA and IP notices were dropped. Fixed
   with phrase matching, pinned by a test.
3. **Parser format.** The first parser read only the "date : symbols" wording and missed "settlement on … at date" (most
   notices) and spot notices that delist "the contracts of the aforementioned token(s)". Rewritten by sentence; all
   three wordings are tested.
4. **Moved settlements.** Six settlements moved after the first notice (FLM's notice said 11-04; it settled 11-21). Exits
   now come before the earlier of the stated and actual times.
5. **Slippage not rising with size.** Median round-trip slippage fell as size rose (40bp at $25k, 35bp at $50k), because
   coins whose book could not fill a size dropped out of that size's median and the aggregated book was measured against
   its own mid. Fixed: slippage against the true mid, extrapolated linearly beyond the shown book; the share of coins
   that can fill each size is reported.
6. **Entry timing.** Entry at the listing-day boundary read a pre-trading bar; for a coin listed late in the day, "d = 1"
   meant two hours. Entry is now the close of day d+1.
7. **Variable reuse.** A cost variable reused the coin's name in the HL delisting loop, which would have mislabelled
   trades.
8. **Rate limit.** The venue's shared rate limit (other workers) slowed the funding fetch, so the pre-store basket-funding
   proxy was cut from ten seasoned coins to five. It is the weakest number here: after 2025-10-01 the five coins' funding
   ran 13.9 points a year above the full basket's. The in-sample basket-hedged P&L may be understated by up to about 2%
   a 60-day trade; that does not change the choice.
9. **Test expectation.** One test expectation (price-weighted funding) was wrong; the code was right.

## 9. What this cannot see

- Book depth in a listing's first weeks before the last 120 days, or during any past delisting: part (b)'s costs come
  from the depth-to-volume model, not from observed books.
- Hyperliquid's notice times (inferred) and its open-interest history.
- Binance's settlement-price formula: the reduce-only hour was excluded, not modelled.
- Liquidation mechanics: the +100% stop is a stand-in.
- FDV covers 58 of 129 listings and the airdrop flag 58, from DefiLlama's index matched by symbol and price.

## 10. What next

1. **Post-settlement short.** After Binance's perp settles, its spot falls a median 32% in seven days while Hyperliquid's
   or Bybit's perp may still list the coin; a short there, from settlement to the spot delisting, is slow, untested, and
   measurable with the Bybit legs.
2. **Forward test of the early basket-hedged listing short** (§7), pooled with Binance and Bybit new listings so it
   reaches 30 events within months.
3. **Dying-market detector:** a thin Hyperliquid market whose funding runs away for weeks (the MAVIA, ZEREBRO, TST
   shape), for monitoring rather than trading.

## Errors found in earlier work

- `research/2026-10-09/funding_arb/findings.md` §4, "13 coins that have since lost their HL book": HMSTR, NOT and XAI
  are still listed on Hyperliquid (open interest $1.46M, $97k and $375k in that study's own snapshot); their capacity was
  zero because their half-spreads (30, 10.6 and 10.5bp) exceed its 10bp cap. The quoted 92% a year includes them; the
  ten truly delisted coins earned about 234% a year of position held, 58% of it from MAVIA.
- The same study's §2, "1.25bp-an-hour floor": the interest-only floor is 1.25e-5 an hour, i.e. 0.125bp an hour
  (10.95% a year); the annual figure in the same sentence is right.
- Zero-volume pre-listing bars (§8, item 1) apply to every 4h and 1h `candleSnapshot` series in the repo, e.g.
  `funding_arb/raw/hl_extra/candles_4h` and `unlocks/raw/candles_4h`. In those studies a coin without funding rows was
  not live, so the damage is probably small, but nothing checks for pre-listing bars.

## Coordinator's check (2026-10-10)

Read from this study's raw files: ZEC's daily `candleSnapshot` series has 1,373 bars beginning 2023-01-07 (open 41.35,
volume 0, zero trades); the first bar with volume is 2025-10-02 (360,186 ZEC in 42,357 trades), after **999 zero-volume
bars that carry prices**. The pre-listing-bar error is real and repo-wide. The floor arithmetic checks: 0.01% per 8
hours is 1.25e-5 an hour, 0.125bp, and 1.25e-5 × 8,760 = 10.95% a year.
