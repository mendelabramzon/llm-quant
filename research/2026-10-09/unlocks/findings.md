# Token unlocks against the perp you can short into them — 2026-10-09

The question: do prices still drift down into large scheduled unlocks to insiders and early investors, and does the
drift survive the cost of shorting it on the instrument a trader would use — the Hyperliquid perp, with its funding?
`scripts/unlock_study.py` matches DefiLlama's documented cliff schedules (`defillama-datasets.llama.fi`, the free
dataset bucket; the `/emissions` API is now paid) to Hyperliquid core perps, and prices a short-the-coin / long-BTC
trade around each cliff from a year of hourly prices and funding (`research/2026-10-09/perps_history`, 1h bars from
2026-03-15 because Hyperliquid serves only the last 5,000; 4h bars fetched for the months before). Numbers are in
`analysis.json`, the full table in `tables.md`, and the forward calendar in `upcoming.json`.

## What was measured

- **Identity.** 100 tokens matched a Hyperliquid perp by symbol *and* by price (DefiLlama's price within 25% of the
  perp's mark; thousand-unit tickers at 1000x); no symbol was rejected on price. MOVE's schedule failed to download.
- **Events.** Cliffs in the `insiders` and `privateSale` categories, merged by day, sized against the supply already
  unlocked that day from DefiLlama's documented curve: **362 events on 41 coins** between 2025-10-15 and 2026-10-08,
  203 before the 2026-04-01 cutoff and 159 after. 193 are at least 1% of unlocked supply (84 after the cutoff, about
  161 a year). Airdrop cliffs (10) are reported separately and are too few to test.
- **The trade.** Short the perp and buy the same notional of BTC at T+a, close both at T+b. P&L = −(coin log return −
  BTC log return) + the funding the short received − the funding the BTC long paid − both round trips. Round trips are
  each coin's own at $100k from the 2026-09-10 books (73 coins priced, median 35bp; 35bp where unpriced) plus 9.1bp for
  BTC: the mean cost charged out of sample was 0.47% a trade.
- **The placebo.** The same coins and windows 15 days before and after each event (skipped within a week of another
  real event). Alt-coins fell against BTC for much of this year, so shorting almost any of them against BTC made money;
  the claim is about unlocks only where the event beats its own placebo.
- **The protocol.** 24 variants (8 windows × 3 minimum sizes), chosen on events before 2026-04-01 by the excess over
  placebo, tested once on events after it. Events cluster on calendar dates, so the out-of-sample t is also computed
  on event-day means.

## What it found

**The protocol's own choice did not hold.** In sample the best variant was the symmetric window, three days before to
three days after the unlock, at ≥1% of supply: +2.45% a trade against a placebo of −1.36% (excess t 2.87). Out of
sample it made +0.73% against −0.26% (excess t 0.59, by-day t 0.33). That is the result this study reports as its
test.

**The part that held is the run-up, and the reversal after it is the mechanism's signature.** Splitting the window at
the unlock:

| window, size ≥ 1% | in sample | placebo | excess t | out of sample | placebo | excess t | by-day t | hit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 days before → unlock | +1.80% | −0.23% | 2.32 | **+1.98%** | −0.34% | 2.04 | 2.18 | 63% |
| same, size ≥ 2% | +1.89% | −0.10% | 1.66 | **+2.62%** | −0.23% | 2.27 | 2.93 | 58% |
| unlock → 3 days after (≥ 0.5%) | +0.20% | −1.14% | 1.42 | **−1.58%** | +0.11% | −1.78 | −2.16 | 47% |
| 14 days before → unlock | +5.16% | +2.61% | 1.42 | +0.87% | −0.55% | 0.62 | 0.59 | 57% |

Out of sample the coin falls 2.5–3.2% against BTC in the three days before a ≥1% insider cliff and rebounds about 1%
in the three days after. That is what hedging pressure looks like: recipients who cannot sell before T can short the
perp before T, and deliver into those shorts after it. The funding does not charge for it: a short over the three
pre-unlock days received about zero (−0.00% to −0.01%), while over fourteen days it paid 0.39%. The pre-unlock window
was one of nine in-sample survivors of a false-discovery test at q = 0.10, but it was not the protocol's pick, and
preferring it now is a choice made after seeing the out-of-sample table. So this is a hypothesis with good support, not
a tested rule.

**And it may be fading.** By calendar quarter, the pre-unlock excess over placebo (size ≥ 1%) was +1.83% (2025Q4),
+1.53% (2026Q1), +4.54% (2026Q2) and **−0.59% (2026Q3)**; at ≥ 2% the same signs (+1.16, +1.88, +5.38, −0.89). The most
recent full quarter is negative.

## Size

Thin. The coins that unlock are mid-caps whose Hyperliquid books held a median $38k of bids within 25bp on 2026-09-10
(25th percentile $13k; median open interest $1.9M); the round trip at $100k was 35bp, and at that size the round trip
eats a fifth of the edge. At the out-of-sample mean, ~$38k a trade and ~161 events a year at ≥1%, the run-up is worth
about **$120k a year** gross of any decay, on average deployed notional of ~$50k (three-day holds overlap about 1.3 at
a time).

## Verdict and the forward test

Entered in the book as `unlock-preshort`, **proposed with `go` no** until a forward test confirms it: every insider or
investor cliff of at least 1% of unlocked supply on a Hyperliquid perp, short the perp and buy BTC three days before,
close both at the unlock, sized to the bids within 25bp. `unlock_study.py upcoming` lists the calendar (20 events in
the next 45 days, first PUMP on 10-12, STRK 10-14, ARB 10-15, ZK 10-17, ZRO 10-20, EIGEN 10-31). After 30 forward
events, re-run `collect`, `prices` and `analyze`: kill it if the mean excess over the placebo is not positive; promote
it to `go` if it is positive at an event-day t above 2.

## What this cannot see

- DefiLlama's schedules are documented plans; a team can delay, re-lock or OTC-sell an allocation, and the timestamp is
  the model's, not an on-chain transfer. Watching the vesting contracts would date the actual delivery.
- Recipients' hedging is inferred from the shape (down before, up after), not observed. Hyperliquid's open interest
  and Binance's would show whether shorts build into the event.
- The books are a month old; capacity should be re-read at the entry time of each forward trade.
