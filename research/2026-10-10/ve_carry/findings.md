# Hedged vote-escrow carry: Aerodrome and Velodrome — 2026-10-10

Vote-escrowed holders on Aerodrome (Base) and Velodrome (Optimism) are paid each epoch with the fees and bribes of the
pools they vote for. Two non-price motives pay them: protocols bribing to steer emissions, and traders' fees. The scarce
resource is the lock: few holders want years of AERO price risk. Two questions:

- (1) does a lock hedged with a short perp beat the savings rate after funding and exit costs;
- (2) does an attentive voter beat the average vote.

**Answer.**

**(1) Hedged carry: the pre-committed version is marginal, and nothing is tradable now.**

- The trade: lock AERO permanently, vote with the average, short the AERO perp on Binance (on Bybit before Binance
  listed).
- Out of sample (2025-08-28 → 2026-10-01) it beat the 3.80% savings rate by **+4.10% a year on capital** (t 1.47).
  Counting only major-token rewards, the excess is **+0.90%**.
- AERO's perp is where lockers and emission farmers hedge. A short paid 15.5% a year over the hedged window.
- Hedged on whichever venue paid shorts most over the trailing four epochs, the lock made **+11.32%** (t 3.81; +8.12%
  majors-only; positive in both halves of the test).
  - That venue was Hyperliquid in 38 of 58 test epochs. This is Hyperliquid's funding premium on a $36M-OI book.
  - The rule was added after seeing the test window's venue funding.
- The measured system ends at the 2026-10-22 merger into Aero. Two epochs remain, and the economics of the new sAERO
  stake are unpublished.
- A lock sold over the last year fetched 15–21% below its AERO: 13–19 months of the best excess.
- **Verdict: standby, go = no** (`book_entries.json`).

**(2) Attentive voter: votes were stale and are not now.**

- Before 2025-03-27, an attentive $1M voter earned +15 to +21 percentage points of APR over the average vote.
- Since then: deciding a day before the close earned −0.2pp, and voting on last week's rewards +1.4pp.
- Only final-hour votes kept +4.3pp at $1M (+0.9pp at $5M). That is a timing game, and the merger ends epochs.

**Velodrome: the cleanest history, too small to use.**

- VELODROMEUSDT funding sat at the interest-only +10.95% a year to shorts on 90% of settlements.
- A hedged veVELO lock made +16.12% over the savings rate out of sample (every week positive; +17.63% majors-only).
- The hedge book has $28k of bids within 1%, and VELO converts to AERO at the merger.

## Verdict

| | verdict | out of sample, excess over SSR on capital | now | size |
|---|---|---|---|---|
| veAERO + short on Binance/Bybit (pre-committed) | no-go | +4.10% (t 1.47); majors-only +0.90% | 2 legacy epochs left | — |
| veAERO + short on best trailing venue | standby, go = no | +11.32% (t 3.81); chosen variant (t24 rule, $5M) +10.44% (t 3.80) | exit 15–21%; merger 2026-10-22 | ~$2M (Hyperliquid) |
| veVELO + VELODROMEUSDT | no-go, ends at merger | +16.12% (t 25.7) | $28k bids within 1% | ~$0.5M |
| attentive voter | no edge without last-hour votes | second half, $1M: +1.37 / −0.21 / +4.26pp (prev / t24 / t1) | ends with epochs | — |
| buy discounted locks + hedge | inside the standby row | +5.48% main venue, +13.50% best venue | ~$2.3M of locks sold a month | small |

## Data and method

- **Chain.**
  - Multicall3 reads at a pinned block, covering all 1,990 Aerodrome and 846 Velodrome gauges, killed ones included.
  - 811,333 and 456,481 reads of `tokenRewardsPerEpoch`, none failed.
  - Each pool's votes at the epoch's end, T−24h and T−1h from supply checkpoints.
  - Rebase from `RewardsDistributor.tokensPerWeek / totalSupplyAt`.
- **Logs.**
  - 8,544 and 6,963 `NotifyReward` events in each epoch's last 24h: what a voter could not yet see.
  - 241,220 veNFT transfers and 45,501 receipts for the sales study.
- **Prices.** DefiLlama at the flip + 1 day (claim plus sale lag). Haircuts: 20% on non-major tokens, 50% on
  low-confidence prices; unpriced tokens count as zero.
- **Perps.** Funding, bars, open interest and books from Binance (from 2024-12-04), Bybit (2024-07-15), Hyperliquid
  (2025-11-11) and OKX (2026-06-29, the limit of its API).
- **Accounting per locked token.**
  - Carry: reward per vote + rebase − the fee to grow the short + funding − the change in basis.
  - Capital: (1 + 1/3) × price, i.e. the short margined at 3× in cash.
  - Entry cost: 0.3% at the start of each half.
- **Protocol.**
  - 22 variants fixed before any return was computed: four voter rules × $1M/$5M/$20M, on/off rules that exit at the
    observed discount, and two best-venue rows.
  - Chosen on the first half of 116 hedged epochs, tested once.
  - Newey–West t with 4 lags and a 4-epoch block bootstrap.
- **Attentive voter.** Votes are split over at most 30 pools to maximise posted reward × v / (votes + v), including own
  dilution, then scored against the final votes.

## Results

**Voter economics.**

- Voter APR (average vote, permanent lock): 39.1% in 2024, 26.8% in 2025, 15.5% in 2026 (mean AERO price $0.443).
- This epoch: 8.8% so far at $0.83, with bribes still arriving.
- Rebase: 10.1%, 4.5%, 2.4%.
- Bribes fell from $101.9M (2024) to $11.3M (2026 to date).

**Hedge cost.** Funding to an AERO short, mean of epochs:

| venue | full window | last 26 epochs |
|---|---:|---:|
| Binance | −14.7% | −3.7% |
| Bybit | −11.1% | −1.0% |
| Hyperliquid | +2.0% | +9.6% |
| OKX | +8.1% | +8.1% |

The worst months were −74.5% (Bybit, 2024-08) and −70.0% (Binance, 2025-02).

**Hedged carry.**

- Average vote on the main venue, by year: +23.1% (2024), +4.2% (2025), +3.5% (2026).
- Test-window decomposition on capital: rewards +12.4%, rebase +1.9%, funding −6.3% (best venue: +1.0%).
- In sample, every always-on row made +10.6% to +16.5%.
- Last 52 weeks: main venue +1.47%, best venue +9.56%.
- Against the savings rate actually paid: main venue +3.85% (t 1.35), best venue +11.06%.
- The on/off rules lost 51–107% a year: each exit sells the lock at the 27.1% median discount.

## Attentive voter

**Staleness has shrunk.**

- Reward-per-vote dispersion across pools fell from 39% (2024) to 21% (2026).
- Votes in pools paying under half the average fell from 20% to 7%.

**Premium over the average vote**, in APR points, first half / second half:

| lock | rule | first half | second half |
|---|---|---:|---:|
| $1M | prev (last week's rewards) | +15.2 | +1.4 |
| $1M | t24 (a day before the close) | +16.1 | −0.2 |
| $1M | t1 (an hour before the close) | +18.7 | +4.3 |
| $5M | t1 | +9.7 | +0.9 |

At $20M every rule's second-half premium is at most +0.7.

**Timing.**

- 15.2% of rewards are notified in the last 24 hours, 0.07% in the last hour.
- 10.7% of votes move in the last hour, when only whitelisted veNFTs may vote.

## Capacity

- **Perp open interest:** $117.2M in total.
- **Bids within 1%:** Binance $373k, Bybit $204k, Hyperliquid $179k (capped at 3× leverage), OKX $112k. Coinbase spot has
  $321k.
- **Best-venue excess:** rests on Hyperliquid, about $2M (5% of its OI).
- **Own dilution:** at $20M the attentive premium is a quarter to a third of its $1M value.

## Exit and entry

**veAERO sales.** 2,256 valued sales ($104.7M of locked AERO):

- median discount 27.1%; 16.8% over the last 365 days; 34.1% for locks worth $100k or more;
- by year: 38.1% (2024), 26.3% (2025), 15.8% (2026).

**By venue, last 365 days:**

- Vexy listings 14.9%; Vexy bids 20.9%.
- An unverified buyer took $68.7M of locks at a 31.4% median.
- iAERO: 0.754 of AERO, a 28.3% exit after the mint fee, in a $45k pool.

**Break-even discount.**

- Chosen variant: 13.5% after 12 months, 27.4% after 24.
- Average vote, main venue: 5.1% and 10.6%.

**Entry variant.** Buying at the 16.8% prevailing discount and exiting at the same discount gives the verdict row's
+5.48% / +13.50%. The risk becomes the discount widening.

## Late entry

- **The carry rows pass the late-entry test.** Rewards go to the votes standing at the epoch's end, so a lock or hedge
  placed an hour or a day late keeps the whole epoch.
- **The attentive premium fails it.** Since 2025-03 it needs final-hour votes.

## Risks and kill criteria

**Re-quote** only after eight post-merger weeks, and only if both hold:

- sAERO staker revenue + funding ≥ SSR + 5pp on capital;
- an sAERO exit at under 10% discount with ≥ $1M of volume a month.

**Kill** on any of:

- trailing-4-week funding below −5% on every venue with OI above $20M;
- Hyperliquid AERO OI below $20M, or its bids within 1% below $100k;
- delisting on the hedge venue;
- dilution of permanent stakes.

**Not modelled:**

- the conversion itself (MetaDEX's Base contracts are unpublished);
- margin calls: AERO rose from $0.433 to $0.822 between the 2026-07-23 and 2026-10-01 epochs;
- the Base sequencer and bridge;
- Hyperliquid auto-deleveraging.

## What failed

- The pre-committed hedge.
- Every on/off rule.
- Voting a day early.
- iAERO as an exit.
- The VELO hedge: tiny, and it ends at the merger.
- Measuring the post-merger economics: not possible yet.

## Errors found in the worker's own work

1. `live_rpc` raises Infura's −32603 without retrying. The multicall wrapper would have dropped reads, and the vote
   reader would have turned them into checkpoint 0. Fixed with retry before split and explicit nulls. A re-read of
   20,000 random votes per chain found no mismatches.
2. Infura's 10,000-result cap at Aerodrome's launch block broke the transfer scan. Fixed with adaptive ranges.
3. Hyperliquid's 4-significant-figure book spans 0.2%, so depth first read a flat $26k. It is $179k within 1%.
4. Always-on rows initially paid no entry cost. Fixed.
5. The first aero.xyz comparison used haircut values against gross revenue. Fixed.
6. The best-venue rule was added after seeing the test window's venue funding. Disclosed.
7. Lock values were read only for material sales plus 500 of 5,799 small ones, so the all-sales slice leans large and
   early.

**Worker's independent checks.**

- **Events against storage:** over three full weeks, 2,704 of 2,707 amounts are identical (the 3 exceptions are dust
  sent to never-voted contracts). Velodrome: 1,337 of 1,338.
- **RewardsSugar against storage:** 144/144 rewards and 60/60 votes on Base; 134/134 and 60/60 on Optimism.
- **aero.xyz quarterly revenue:** gross rewards here are 83–96% of it in 10 of 13 quarters.
- **Funding:** identical to the 2026-10-09 funding_arb pull on 2,279 and 2,280 common settlements.
- **AERO price:** DefiLlama against exchange closes, median gap 0.20%.

## Next

1. After 2026-10-22: measure sAERO staker revenue for eight weeks and re-run the protocol.
2. Keep a weekly forward ledger of Hyperliquid against CEX AERO funding and of the Vexy discount.
3. If the discount stays at or above 15%, test buying discounted sAERO NFTs hedged on Hyperliquid.

## Coordinator's check

Recomputed from `raw/perps/binance_VELODROMEUSDT_funding.json.gz` alone: 3,996 settlements on a 4-hour interval, of
which **90.0%** are exactly 0.005% (10.95% a year, the interest-only rate). That matches the note.

Files: `scripts/ve_carry.py`, `scripts/test_ve_carry.py` (20 tests), `analysis.json`, `tables.md`, `manifest.json`,
`book_entries.json` (one standby row, go = false), `raw/`.
