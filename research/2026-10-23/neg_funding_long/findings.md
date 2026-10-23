# Long the perp after extreme negative funding — 2026-10-23

## Answer

**No-go.** Take a late-entered long in a Binance alt perp whose trailing funding is deeply negative.

- It does collect large funding: **+15% of notional per trade** out of sample, for the chosen rule.
- But the price falls by about **11%**, so the mean net is **+4.0% per trade**.
- That mean comes from a handful of short squeezes. In the median trade the long loses **3.2%**, and **46%** of trades
  win.
- Drop the **5 best of 153** out-of-sample trades and the mean is **−3.3%**.

**The chosen rule:** `L3_T100_HN`.

- Enter when trailing 3-day funding is ≤ −100bp per 8h and the perp trades ≥ $5M a day.
- Hold until funding normalises.

The protocol rejects it:

| | in sample | out of sample |
|---|---|---|
| excess a year (equal-weight book of open trades, not a return on a capital pool) | +361% | +192% |
| HAC t | 1.48 | **0.96** |

- The full-sample HAC t is 1.75.
- The block-bootstrap probability that the true mean is ≤ 0 is 16%.
- The deflated Sharpe is 0.75.
- **None of the 32 pre-registered variants survives one-sided BH.**

**Capacity.** At $250k a trade (within 2% of 7-day volume, with impact):

- The out-of-sample record nets **+$1.1M a year on about $0.9M of average open capital**.
- Without its 5 best trades it is **−$1.5M a year**.
- No capacity is stated for an edge that is indistinguishable from zero and whose sign depends on about 5 squeezes a
  year.

**The Bybit-short hedge does not rescue it.** The Binance–Bybit funding gap is not a carry: all 18 gap variants lose
out of sample.

**Coordinator's check.** These were recomputed from `trades.json.gz` (chosen rule, split at 2025-10-06):

| | trades | mean net | median | hit rate | mean without the best 5 | funding | price |
|---|---:|---:|---:|---:|---:|---:|---:|
| in sample | 76 | +8.9% | −2.8% | 38% | −6.1% | +9.0% | +0.0% |
| out of sample | 153 | +4.0% | −3.2% | 46% | −3.3% | +15.4% | −11.2% |

They match the study.

## Why

1. **Funding scales with the signal, and so does the price drop.** Take every coin-day with ≥ $5M of volume, entered a
   day late, at zero cost, held 7 days:

   | signal per 8h | funding over 7 days | median price |
   |---|---:|---:|
   | −10 to −25bp | +2.8% | −5.0% |
   | −50 to −100bp | +7.2% | −7.0% |
   | below −200bp | +17.2% | −13.6% |

   - The median total is negative in every bucket, for both horizons (3 and 7 days) and both lookbacks (1 and 3 days).
   - Hit rates are 39–47%.
   - The payers are not obviously wrong: the coins keep falling.
   - On the chosen rule's out-of-sample trades, the price fell 74% of the time. In 53% of the trades that received
     funding, the drift ate all of it.
2. **The mean is a squeeze lottery.**
   - The best trades are famous squeezes: COAI (Oct 2025, +366%), M (Sep 2025, +356%), ALPACA's delisting squeeze
     (Apr 2025, +299%), FUN, ENJ, ONG and ESPORTS.
   - The best 5 trades are 180% of the out-of-sample sum, and 164% in sample.
   - The worst trades lose 65–82%: RAVE, POWER, VIDT, FOLKS and MYX.
   - In 28 of 32 variants the out-of-sample mean turns negative without the best 5.
3. **The late entry gives up about half the mean.** The squeeze often comes in the first 24 hours after the signal.
   - Buying at the signal's own close (lag 0) earns +10.5% a trade over the full sample. That breaks the late-entry rule.
   - Buying a day later (lag 1) earns +5.6%.
4. **Costs are not the problem; variance is.**
   - Taker fee plus spread is 0.14% a trade.
   - The out-of-sample t is 0.99 at zero cost and 0.94 at double cost.
   - A $20M volume floor gives +6.6% a trade (t 1.26). A $1M floor gives +4.1% (t 0.76).
5. **Run on Bybit, the same family looks the same.** The chosen rule makes +5.5% a trade in sample and +4.8% out of
   sample (t 1.12). Half the variants are negative out of sample.
6. **The Binance–Bybit gap mean-reverts when it is big and is too small to pay when it persists.** Across 776 same-coin
   pairs:

   | gap per 8h | same sign the next day | pays a day |
   |---|---:|---:|
   | 10–50bp | 59–62% | 9–14bp |
   | ≥ 50bp | 36–48% | — |

   - The persistent small gaps earn 9–14bp a day, against about 30bp of four-sided taker cost.
   - All 18 gap variants are negative out of sample: −0.3% to −2.4% a trade (t −0.6 to −2.4).
   - The hedge fails in crashes. On 2026-06-09/10, HUSDT traded at 0.10 on Binance and 0.20 on Bybit, and one trade lost
     115% of a leg's notional when the two converged.
   - Short legs moved up to +1,170% during gap trades.
7. **The spot-hedged version cannot be tested.** There is no margin-borrow history on disk. For these names a spot
   borrow is usually unavailable, which is presumably why the payers short the perp in the first place.

## The current episode (2026-10-18 → 10-23)

The lead was looser than the prints:

| perp | turned negative | note |
|---|---|---|
| BTW | 10-19 16:00 UTC | |
| BIRB | 10-21 04:00 UTC | perp trades $1.2M a day, below every volume floor |
| ALT | 10-22 16:00 UTC | |
| GTC | on and off since 10-08 | |
| ARK | — | averaged −1bp over the five days |

**What a long bought at the 2026-10-18 15:00 UTC open paid by about 15:30 UTC on 10-23.** Costs are taker plus 10bp
half-spread, both sides.

| perp | funding | price | long net | hedged with a Bybit short |
|---|---:|---:|---:|---:|
| BTW | +7.1% | −28.1% | **−21.4%** | +0.2% |
| BIRB | +15.4% | +61.2% | **+76.3%** | −12.0% |
| ALT | +3.5% | −11.3% | **−8.1%** | −1.5% |
| GTC | +7.7% | +14.1% | **+21.5%** | no Bybit pair |
| ARK | +0.4% | +30.8% | **+31.0%** | −2.9% |

- **This table has look-ahead.** The names were picked on today's funding.
- It has the shape the history shows: two −8% to −21% losers next to a +76% squeeze.
- The chosen rule, entering at lag 1, traded none of the five. It held ERA (−10.7%) and KAIA (−3.2%).

## Data and method

- **Script.** `scripts/neg_funding_long.py`, run as `collect`, then `grid`, then
  `analyze --out research/2026-10-23/neg_funding_long`.
- **History.** Reused from `research/2026-10-11/alt_floor_carry/raw/` (2024-10-01 → 2026-10-10). It was topped up to
  2026-10-23 15:30 UTC from public endpoints:
  - Binance: bulk funding and daily klines for 800 symbols.
  - Bybit: 657 shared symbols.
  - Hourly klines for 16 names in the current episode.
- **Window.** 752 days ending 2026-10-22, split at 2025-10-06.
- **Universe.** 866 Binance USDT perps.
  - The 124 that were delisted are kept.
  - `clean_funding` removes phantom settlements on untraded days.
  - Signals are restated per 8h from each settlement's own interval.
- **Rule mechanics.**
  - The decision at the start of day d sees funding through d−1.
  - The long is bought at day d's close and earns funding from d+1.
  - The "N" exit fires the day after funding goes above −5bp per 8h, with a cap of 28 days.
- **Costs.** VIP0 taker plus the alt_floor_carry half-spread model.
- **Capacity.** Square-root impact (Y = 0.5) at a 2% participation cap.
- **Excess.** Net of the 3.80% savings rate while capital is deployed.
- **Grid.** 32 variants, pre-registered in `analysis.json`. Chosen with `backtest.choose_then_test` on Sharpe; BH applied
  to the one-sided full-sample HAC p.
- **Caveat on scale.** The uncapped dollar figure ($131M a year) is an artefact of COAI's and PIPPIN's billion-dollar
  volumes. It falls to −$45M without the best 5 trades. Do not quote it.
