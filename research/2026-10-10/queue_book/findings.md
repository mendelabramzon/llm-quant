# Queue bids on one capital pool — 2026-10-10

The book holds four queue bids, each priced as if it owned its capital: stETH $130k a year at $10M, weETH $194k at $10M,
rsETH $44k at $3M and LBTC $111k at $10M. That is $479k on $33M. Every one of those studies found the same binding
constraint: capital locked in the redemption queue. The ROADMAP has twice said the ETH bids "share one collateral pool
in a stress" without measuring how often their dislocations coincide. `scripts/queue_book.py` measures it. It runs
`dislocation_history.simulate_bid`'s rule over the merged sells of all four assets, filling first come, first served
from one pool. With one asset it reproduces `simulate_bid` exactly (tested). The hurdle is chosen on the first half of
the common window (2024-09-26 → 2025-10-03) and tested once on the second (→ 2026-10-09).

**Answer: one pool needs well under half the capital.**

| | capital | out of sample, $ a year | per $ of capital |
|---|---:|---:|---:|
| four separate books (the book's sizes; reproduced exactly) | $33M | $479,378 | 1.45% |
| one pool, all four | $10M | $326,286 (t 9.31; 95% interval $255,637–$399,645) | 3.26% |
| one pool, all four | **$15M** | **$409,889** (t 9.31; $321,307–$503,564) | **2.73%** |
| one pool, all four | $20M | $508,553 (t 8.81; $395,497–$630,672) | 2.54% |
| one pool, the three ETH bids only | $15M | $337,677 (t 7.31) | 2.25% |

- $15M in one pool earns 86% of what four pools earn on $33M.
- $20M earns 106% of it, because a shared pool also catches each asset's overflow, which a separate book has no
  capital left to take.
- The returns are excess over the carry. Each fill is charged the staking yield it gives up while it waits in the
  queue, as in the per-asset studies.

## Why it works: the dislocations are not one event

Daily capital each asset would lock with unbounded capital (hurdle 2bp):

| pair | correlation | overlap (days both / days either) |
|---|---:|---:|
| weETH – stETH | 0.70 | 63% |
| rsETH – stETH | 0.38 | 36% |
| weETH – rsETH | 0.26 | 43% |
| LBTC – stETH | −0.04 | 44% |
| LBTC – weETH | −0.06 | 52% |

- **The ETH tokens stall together.** weETH and stETH stall in the same queues and the same deleveraging. Adding a third
  ETH token adds little.
- **LBTC is the diversifier.** Its discounts come from Babylon unbonding and BTC-side flows, unrelated to the ETH ones.
  In the $15M pool it contributes $97k, nearly its stand-alone $111k.
- **What this means for growing the book.** Diversify by the underlying asset and its queue (ETH, BTC, and next HYPE,
  AVAX, SOL), not by issuer of the same underlying.

## Robustness

- **Late entry passes.** Taking a sell only if the whole market already showed the discount an hour earlier keeps 85–96%
  of the value (all four, $10–20M). A day earlier keeps 85–91%. The ETH-only book keeps 92–95% at an hour and 89–91% at
  a day. Episodes last hours to weeks: the April 2026 stETH episode ran 20 days.
- **Not one stress.** At $15M the best month is 12% of the out-of-sample value and the best two are 24%.
  - The value is spread over every month from 2025-10 to 2026-10.
  - The exception is July–August 2026, which earned $8k and $6k. Summer 2026 had almost no dislocation.
- **In sample was richer.** $707k at $15M, because it holds the summer-2025 Lido queue: $915M of capital would have
  been locked at the peak on 2025-08-30. The chosen hurdle ranked 2nd–3rd of 7 out of sample.
- **Capacity still grows past $50M** ($987k a year at $50M, 1.97% per $). The constraint is the return per dollar,
  not the total.

## How to run it: resting orders backed by one balance

This section is a proposal, not tested on chain. The study models a pool that waits for sellers. On Ethereum that can
be literal. Off-chain-signed limit orders (CoW Protocol, 1inch) do not escrow funds: one WETH (or aWETH) balance can
back standing orders for stETH, weETH and rsETH below NAV at the same time. A fill is settled only if the balance is
there, so committing more than you hold is safe: a second fill during a stress simply fails. The orders are in ETH
terms, so they track NAV and need re-signing only as the exchange rates accrue (daily).

- **LBTC needs BTC capital.** The four-asset pool therefore needs one of:
  - a cbBTC sub-pool; or
  - borrow-on-fill against shared collateral (WETH or cbBTC borrowed on Aave against wstETH).
- **The ETH-only book needs neither.** It is $338k a year on $15M and runs on resting orders alone.
- **Checked on the record** ([cow_fill_check](../cow_fill_check/findings.md)).
  - In the April 2026 stETH episode, CoW orders that had rested an hour or more bought 6,023 ETH of liquid staking
    tokens in 91 fills, at a median 31.2bp below NAV.
  - That is at their limits (median 30.0bp) and +3.2bp beyond the venue median.
  - 83 owners were bidding.
- **Still to verify:**
  - several orders on one balance during one stress (documented, not observed);
  - the request-and-claim step after a fill (a keeper, not time-critical).

## Book

`book_entries.json` proposes one row, `lst-queue-book-one-pool` ($15M, $409,889 a year out of sample), to replace the
four separate rows rather than sit beside them: the book would otherwise count the same capital twice. Not written to
the book; needs the user's approval (`strategies.py add --file research/2026-10-10/queue_book/book_entries.json`, then
retire or mark the four component rows).

## Data and caveats

- **Inputs.** The per-asset studies' priced swaps and queue state, unchanged: research/2026-10-09/redemption_history
  long window (stETH, rsETH), research/2026-10-10/queue_bids_ext etherfi_long (weETH, the book's `etherfi_ev` variant)
  and new_assets (LBTC on cbBTC pools).
- **Regeneration.** The stETH/rsETH swaps files had to be regenerated in a scratch copy of the long window with
  `dislocation_history.py analyze --assets lido,kelp`. The rerun reproduced the stored numbers exactly ($401,697 and
  $50,894).
- **First come, first served.** A pool that reserved capital for deeper discounts could do better; that was not tried.
- **The cost of waiting is modelled, not borrowed.** It is the staking yield for ETH and 0.5% a year for BTC. With
  borrow-on-fill it would be the borrow rate (WETH ~2% on 2026-10-09).
- **LBTC's 9-day wait comes from Lombard's docs**, not from a measured queue. The bitcoin-side sample measured payouts
  at 5.4–6.0 days.

Numbers: `analysis.json` (`alone`, `joint`, `late_entry`, `concentration`, `overlap`); tables: `tables.md`. Test:
`scripts/test_queue_book.py` (4 pass).
