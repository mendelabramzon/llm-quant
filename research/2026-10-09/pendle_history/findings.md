# Pendle fixed against floating: every matured market, defaults included — 2026-10-09

The question was whether buying Pendle principal tokens has paid. The comparison is against holding the same token's
floating yield and against the savings rate, after the defaults. It also asks whether any rule for choosing PTs works on
markets it was not chosen on. The repo had only met Pendle in windows (`detectors/fixed_vs_floating.py`, the
`pt-susds-fixed-vs-ssr` book row). A window can read a fixed rate, but it cannot say whether buying that rate was a good
trade, because the outcome arrives at maturity. Pendle has now matured 916 markets, and a PT held to expiry pays exactly
one unit of its accounting asset. That makes it the cleanest held-to-maturity outcome on chain. Tables are in
`tables.md`; every number below is in `analysis.json` (main run), `analysis_size1m.json` ($1M per trade) or
`analysis_cut20250401.json` (an earlier cutoff). Code: `scripts/pendle_history.py`, 38 tests in
`scripts/test_pendle_history.py`.

## The answer

1. **Holding the PT instead of the same token paid, out of sample.** The rule chosen on the past was "the implied rate
   clears the token's own trailing-7-day interest by at least 5%". On trades entered after the 2025-09-01 cutoff it made
   **+7.09% a year** over the token's realised floating. That is the equal-weighted, marked-to-market book: Newey–West
   t 7.11 at a 77-day lag, bootstrap 95% interval +5.29% to +9.10%, 1,004 trades in 175 markets, 96% of them positive.
   It holds three ways:
   - weighted by pool TVL: +7.83%, t 7.16;
   - at $1M a trade instead of $100k: +4.35% (t 2.44), and +5.91% TVL-weighted;
   - with an earlier cutoff (2025-04-01): +5.55% (t 3.32).

   Charging the switch the reward tokens a holder would also have collected leaves +7.48% pooled per capital-year. The
   mechanism is the points premium. YT buyers pay for points, so in points markets the PT trades at a median 4.28% over
   the trailing interest, against 1.78% elsewhere. The PT holder is the one who sells them the points.

   Live today: 18 markets qualify. At the size that maximises dollars a year through each pool, that is **$10.0M of
   capacity and $423k a year** over the tokens' own floating. Of that, $6.6M and $216k is in tokens with measured
   interest; the rest is in tokens that pay none.

2. **Holding dollar PTs instead of the savings rate did not pay after defaults.** Every dollar PT in the panel, held
   to expiry, lost **−8.20% a year** to the savings rate out of sample (t −2.59). TVL-weighted it lost −2.95% (t −1.02).
   The rule chosen in sample (spread over the savings rate ≥ 10%) made +2.28% (t 0.41, interval −10.5% to +10.5%).

   Remove the defaults and every threshold earns +4.07% to +10.21% (t 4.4 to 11.2). The defaults are the whole story.
   They landed where the market charged least: dollar PTs bought at 2–6% over the savings rate lost **11.2% and 30.5% a
   year to default out of sample**, against 3.1% to 7.7% in the wider-spread buckets.

3. **Long YT on interest alone lost −112% a year out of sample** (t −5.5; 90% of trades negative). It loses even when
   the token's floating rate ran above the implied rate at entry. The impact charged to it is understated (see Caveats),
   so the true number is worse.

## What was read

- **Markets.** 1,033 markets on 13 chains. 814 come from Pendle's own market lists. 219 more appear only in the flat
  asset list, which outlives de-listing. That list still holds the December-2025 Stream xUSD market, both
  December-2025 Elixir sdeUSD markets, the March-2026 Stables Labs USDX/sUSDX markets and the March-2026 TermMax USDC
  vault. Daily v3 history answered for 910.
- **Blocked markets.** For 123, the API answers "market is unsafe". Their trades came from the transactions endpoint,
  which still answers, and their SY, yield token and asset came from the chain. They are small in aggregate: $12.9M of
  PT was bought in them, against $94.1B of trading volume in the served panel. One is a real casualty. In the sdeUSD
  (deUSD) market, $8.0M of liquidity was added and $399k of PT bought, and the buyers got back 0.1 cents on the dollar
  (USD-weighted excess over the savings rate −101%).
- **Prices.** 579 yield tokens and accounting assets, 477 of them priced by DefiLlama by contract. 31 more went through
  a CoinGecko-id fallback, which is how Stream's xUSD is priced; DefiLlama has no contract price for it.
- **Benchmark.** DefiLlama's sUSDS series from 2025-02-21 (596 days). Pendle's own sUSDS/sDAI markets fill 529 days
  before that, and DefiLlama's DSR covers the rest (281 days). Today's comparator is the on-chain sUSDS.ssr() reading,
  **3.80%**, not the 3.6% quoted earlier in the book. The Pendle-derived trailing interest on sUSDS reads 3.62%, a
  trailing 7-day number.
- **Identities.**
  - The API's pool TVL equals totalPt × ptPrice + totalSy × syPrice exactly on 73,995 rows, so the fields mean what
    they say.
  - On USD-accounted markets the PT price matches (1+implied)^(−τ) to a median 0.0003 (p90 0.0024).
  - The SY's 30-day growth matches compounded `underlyingInterestApy` to a median 0.51 points of APY (p90 3.8). This
    is the loosest identity, and the reason the floating leg is called a reading, not an exact number.
  - The accounting unit's move at expiry, read from the API and from the market, agrees within 1% on 95.4% of the
    2,877 dollar trades where both exist (median gap 0.0006).

## How it was measured

**Per trade.** Every matured market is entered once a week, from the first day its pool held $1M until 14 days before
expiry. Each entry buys $100k through Pendle's rate curve at that day's reserves. `pt_buy_quote` is the AMM's own
logit-proportion formula with the market's scalar root and fee, and the anchor is solved from the observed implied
rate. The median cost is 0.57 points of APY at $100k (p90 2.29). Each trade carries three legs over the same days:

- the PT to expiry;
- the yield token's realised interest (`underlyingInterestApy` compounded daily; points and reward tokens excluded);
- for dollar markets only, the savings rate.

The result is 8,819 trades across 603 markets.

**Defaults.** At expiry, one accounting unit is worth the yield token's market price divided by the SY exchange rate.
Pendle's history marks the SY at the protocol's own rate, so a collapsed token keeps its pre-collapse price there. xUSD
sat at $1.2659 through its December expiry while it traded at five cents. Two readings catch the two ways a holder
loses:

- **The ratio:** the yield token's market price over the API's SY price. It uses the median price over the three weeks
  after expiry, which is what a holder who could wait would get. It counts only when the same series agreed with the
  API in the market's first month, and only when the token's own price actually fell.
- **The accounting unit's move:** read from the API's own rows. This catches USD0++, which Pendle marked at market.

The ratio is applied to dollar markets only. For an ETH, BTC or HYPE unit, a USD ratio over three weeks is mostly the
underlying's own move: weETH "recovered" 0.959 in June 2024 because ETH fell, which is how the first version of this
check found 138 false defaults. Two refinements of what counts as a loss:

- Purchases after a dollar market had already broken are skipped (34 entries). Otherwise they would be priced at the
  API's stale accounting value, for example sUSDX bought at 97 cents of a USDX that traded at five.
- The market's move is used only when the yield token itself has no market price. Multiplying it into the ratio would
  count a same-token collapse twice: USDX is both the yield token and the accounting asset.

**The test.** The backtest is a book. Each entry day it commits one unit of capital, split equally across that day's
trades (or by pool TVL in the weighted runs). It holds every trade to expiry and marks it to market daily from the
implied rate. A default lands on its first break day.

Parameters are chosen on days before the cutoff, using only trades that had matured by then. The reported number is
the same rule applied to trades entered after the cutoff; 1,004 trades that straddle the cutoff are used on neither
side. The cutoff is a rule fixed before any strategy was scored: the median expiry of matured markets that ever held
$1M, first of its month. It lands at **2025-09-01**, leaving 4,613 trades to choose on and 3,202 to test.

Out-of-sample inference uses Newey–West with lags equal to the 77-day median hold, and a block bootstrap with blocks of
the same length. All 59 variants across eight families go through one Benjamini–Hochberg pass at q = 0.10. 28 positive
and 13 negative variants survive.

The Sharpe ratios in `tables.md` come from a book of accruing PTs marked from a smooth implied rate, which understates
risk. The trade-level distribution and the Newey–West t are the numbers to read.

## PT against the same token's floating rate (families a and b)

| class | OOS excess a year | NW t | OOS trades | BH q10 |
|---|---:|---:|---:|---|
| stable | +3.03% | 4.94 | 1,692 | yes |
| Ethena (USDe/sUSDe and derivatives) | +2.30% | 2.17 | 293 | yes |
| BTC | +1.05% | 4.71 | 206 | yes |
| HYPE | +1.43% | 1.75 | 202 | no |
| ETH | −0.44% | −0.60 | 540 | no |
| other | +5.88% | 1.82 | 269 | no |
| points markets | +2.50% | 4.30 | 2,483 | yes |
| no-points markets | +1.19% | 0.89 | 719 | no |

Unconditionally, the switch from the token to its PT earned a few points a year in dollars and BTC and nothing in ETH.
That is not robust to size: at $1M a trade, stable falls to +1.59% (t 1.23) and BTC to −0.24%.

Conditioning on the implied rate clearing the token's trailing interest is what survives. The out-of-sample result
rises steadily with the threshold:

| implied − trailing ≥ | 0 | 1% | 2% | 3% | **5% (chosen)** | 8% | 12% |
|---|---:|---:|---:|---:|---:|---:|---:|
| OOS excess a year | +2.97% | +3.83% | +4.64% | +5.40% | **+7.09%** | +9.53% | +12.31% |

The 5% rule ranked second of eight out of sample. By class, out of sample, the chosen rule made:

| class | trades | pooled excess |
|---|---:|---:|
| stable | 698 | +7.15% |
| other | 152 | +14.85% |
| Ethena | 82 | +6.66% |
| HYPE | 49 | +6.17% |
| ETH | 22 | +6.08% |

Its worst trade made −13.6% a year.

**What it is, and what it is not.**

- It is the price YT buyers pay for points (and for leverage on the floating rate), collected by the side that sells
  them that exposure.
- It is not a dollar yield. Against the savings rate the same trades carry the token's full credit, and those are the
  trades that defaulted (below). For a holder who is in the token anyway, the switch keeps the credit unchanged, gives
  up the points, and earned a measured 7% a year for them out of sample.
- Ten of today's 18 qualifying markets are tokens that pay no measured interest at all (AUSD, USDat, apxUSD, Axis USDx,
  Royco's junior tranche). For them, "over floating" is the whole implied rate, and the right comparison for anyone not
  already holding the token is family (d).

Today's book under the chosen rule is led by:

- Sierra (implied 9.74% over 3.79% trailing; $2.5M at 7.64% after impact; $96k a year);
- 3Jane USD3 (15.13% over 6.61%; $2.5M; $63k);
- re.xyz reUSDe (18.63% over 12.52%; $1.0M; $28k).

## Long YT on interest alone (family c)

Out of sample, every variant lost between −111% and −139% a year: 451 trades at the loosest threshold and 74 at the
tightest, with 8–11% of trades positive. A YT bought because the token was paying more than the implied rate on the
day of purchase lost because the floating rate did not stay there. The interest-only payoff never recovers the points
value built into the price. Retired before it starts.

## Dollar PTs against the savings rate, after defaults (families d and e)

| spread over the savings rate at entry | trades | defaulted markets | promised spread | default loss | realised excess | OOS trades | OOS default loss | OOS excess |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| under 2% | 694 | 1 | −1.43% | 0.28% | −1.71% | 319 | −0.24% | +0.18% |
| 2–4% | 889 | 3 | 1.62% | 4.53% | −2.91% | 452 | 11.17% | −9.41% |
| 4–6% | 909 | 8 | 3.63% | 14.36% | −10.73% | 477 | 30.52% | −27.04% |
| 6–10% | 938 | 9 | 6.24% | 1.61% | +4.63% | 445 | 3.06% | +3.52% |
| 10–15% | 399 | 9 | 10.17% | 3.09% | +7.08% | 226 | 3.53% | +6.49% |
| 15% and over | 182 | 10 | 20.27% | 5.26% | +15.01% | 66 | 7.68% | +10.26% |

Rates are pooled per capital-year, so a 30-day trade that lost everything counts for 30 days, not a year.

The losses, from `tables.md`, with recovery per dollar of accounting asset:

| market | expiry | pool at peak | recovery | spread at entry |
|---|---|---:|---|---|
| Stables Labs sUSDX | March 2026 | $28.2M | 1.1 cents | 3.7–5.3% |
| Resolv RLP | April 2026 | $8.9M | 33 cents | 2.3–6.2% |
| Yala YU | December 2025 | | 27 cents | 2.6–8.8% |
| Main Street msUSD | July 2026 | | 33 cents | 2.9–4.6% |
| Strata jrUSDat | August 2026 | | 46–49 cents | |
| APYX apxUSD/apyUSD | June 2026 | $32M and $16M | 88–94 cents | |
| Usual USD0++ (four expiries in 2025) | 2025 | | 92–97 cents | |
| USD.AI USDai/sUSDai | November 2025 and March 2026 | | 95–96 cents | 20–43% |
| Lybra eUSD | December 2024 | | 88–96 cents | |
| Aegis sYUSD | | | 95 cents | |
| Anzen sUSDz | | | 98 cents | |

The pattern is the finding. The market charged the widest spreads to points-heavy issuers that did not default
(USD.AI's 20–43% lost 4–5 cents and still won by a mile). It charged 2–6% to issuers that went to a few cents. A credit
book that buys spread loses, because the spread was not where the risk was.

The in-sample choice changed with the data and failed on each version: spread ≥ 10% in the main run (+2.28% OOS),
≥ 15% at $1M (−4.20%), ≥ 10% with the earlier cutoff (+0.49%). Family (e) restricts to dollar PTs whose implied clears
the trailing floating, which is the dollar half of the rule that worked in (b). It loses everywhere out of sample:
−17.26% for the chosen threshold, t −2.50.

**The book's existing Pendle row.** PT-sUSDS-26NOV2026 quotes 5.01% today against an on-chain savings rate of 3.80%.
At the $250k that maximises dollars through its $4.8M pool, it fills at 4.23%: 43bp over the savings rate, **$1,073
a year**. History has two matured Sky PTs that held $1M, the sDAI markets of March and September 2024. Held to expiry,
they lost 2.18% a year to the DSR (17% of entries positive), because the DSR was raised to 15% in March 2024. The row
is a term-premium view on governance, not a carry. At this size it is dust.

## What failed, and what this cannot see

- **Points are not valued.** The switch's 7% is what YT buyers paid for the points the token holder gives up. If those
  points turn into airdrops worth more, the holder of the token did better. Nothing here observes an airdrop.
- **About a fifth of dollar TVL has no independent maturity price.** Of dollar markets that ever held $1M (worth $6.8B
  at their peaks), $4.85B were checked healthy by market price at maturity and $54M flagged as defaults. $1.46B had no
  market price at maturity, or none at all, and rests on the API's own unit price.
- **Recovery is the median over the three weeks after expiry.** For a collapsing token like RLP, that is below the
  price at expiry (33 against about 41 cents).
- **Impact is AMM-only.** Pendle's limit orders add depth, so $100k is costed conservatively for PT buyers.
- **YT impact is understated.** A YT buy sells roughly 1/price times as much PT through the pool, which family (c)
  does not charge. It loses anyway.
- **No fee or gas on exit is charged.** PTs redeem at expiry.
- **The floating leg is the API's interest reading.** It matches the SY's own growth to half a point of APY in the
  median, not exactly.
- **Junior tranches and insurance tokens are in the stable class.** RLP and jrUSDat are there because Pendle tags them
  that way. They are dollar-denominated risk, which is why they are in the credit table.
- **The deflated Sharpe and the in-sample Sharpe do not mean much here.** A book of accruing PTs marked from a smooth
  rate has little daily variance, so the out-of-sample t-statistic and the trade distribution carry the evidence.

## Kill criteria for the surviving row

Retire `pendle-pt-over-floating-switch` on any of these:

- Over a trailing 90 days, matured switches under the 5% rule realise less than +2% a year over the tokens' floating.
- Live capacity under the rule falls below $2M.
- Any single protocol is more than 30% of the live book.
- The median of implied minus trailing interest in points markets falls below 2%, which means the premium has closed.

## What to collect next

- **Airdrop value per points programme.** Price the 7% against what points actually paid, using token distributions to
  Pendle YT holders.
- **Limit-order depth.** `/v2/limit-orders/book/{chainId}` would raise the switch's capacity, which is AMM-only here.
- **On-chain reconstruction for the 123 markets the API blocks.** Only sdeUSD among them had real dollar flow, but the
  ETH-class agETH ($6.2M of PT bought) and the KS2-RT market ($5.1M) are unpriced.
- **A daily re-run.** Run `collect` (cached, cheap after the first pass) and `analyze` daily, so that the switch's live
  book becomes a quote series.

## Coordinator's check (2026-10-10)

Recomputed from `trades.json.gz` with the study's own excess formula ((fixed_net − floating) × recovery): the 5% rule's
1,004 out-of-sample trades earn +8.44% per capital-year pooled before reward tokens (the +7.09% above is the
equal-weighted mark-to-market book, net of rewards), 96% positive; in sample +12.35% over 2,039 trades. Two splits
matter for the book. Six hundred and two of the 1,004 trades are tokens with no measured interest (median trailing rate
0.00%): there the "switch" is a PT against a zero-yield token, which is the dollar-PT question and failed after
defaults, so the book entry carries only the measured-interest markets ($6.6M, $216k a year). And the no-points markets
show the excess too (+9.6% over 154 trades), so it is a forward-rate premium — fixed rates set above the floating that
followed in a falling-rate period — as much as a points price; a rising-rate year would shrink it.
