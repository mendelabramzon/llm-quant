# The one-pool queue book, run read-only: what an executable bidder earns — 2026-10-11

`lst-queue-book-one-pool` is the book's largest row: $409,889 a year at $15M. Its legs describe standing below-NAV CoW
limit orders re-signed daily. `scripts/queue_live.py` is the read-only bridge to running it small. It produces today's
ladder, unsigned CoW orders with EIP-712 digests, and a daily monitor that recomputes the row's kill criteria. It also
keeps a paper ledger (`research/queue_live_paper.jsonl`). Nothing is signed, sent or posted. Building it exposed a
gap between the backtest and every implementation the row could actually run.

## Answer

**The row's value assumed an execution no patient bidder gets.** `simulate_book` buys each sale at its own discount,
capped at the venue median of its own hour. Only a bidder trading right behind each seller gets that.

| implementation (out of sample, $15M) | all4 | eth3 | share of the backtest (all4) |
|---|---:|---:|---:|
| backtest: each sale at its own price | $409,885 (t 9.31) | $337,673 (7.31) | 100% |
| (a) decision delayed an hour, each sale still at its own price (the 2026-10-10 "late entry") | $392,430 (8.14) | $313,402 (6.35) | 96% |
| **(f) hourly taker: buy back the previous hour's qualifying sales at the next hour boundary, at that hour's venue median** | **$294,743 (7.51)** | **$255,634 (6.22)** | **72%** |
| (f) same, at the first trade after the boundary | $317,253 (7.03) | $289,059 (6.14) | 77% |
| (e) hourly re-quoted resting limit (earns its limit) | $222,477 (7.47) | $182,929 (5.96) | 54% |
| (g) taker a day later, venue median | $213,113 (5.70) | $185,810 (4.83) | 52% |
| (c) daily re-quoted resting limit | $210,512 (8.01) | $168,566 (6.26) | 51% |
| (b) one fixed resting limit (15bp, chosen in sample) | $191,626 (3.84) | $148,827 (2.93) | 47% |
| (d) two resting levels, 15bp and 30bp | $168,528 (3.54) | $126,726 (2.64) | 41% |
| the row as written: resting limits at hurdle + carry (1bp net) | — | — | trailing 90 days: $20.6k a year against $306.7k |

- **Resting orders earn their limit, not the market.** In April 2026, CoW orders filled at their limits (30.0bp limit,
  31.2bp fill).
  - A limit at the row's hurdle + carry fills on routine flow and nets about 1bp.
  - Deeper limits miss the shallow dislocations.
  - Re-quoting from the market keeps about half the value.
- **The discounts persist for an hour, mostly.**
  - Of the sales that qualified in their own hour, the share whose edge still clears 1bp at the next hour's venue
    median: stETH/wstETH 98% (a day later 91%), weETH 91% (82%), rsETH 34% (19%), LBTC 53% (32%).
  - For rsETH and LBTC the low shares are quiet venues, not recoveries. 64–80% and 46–68% of their sales had no later
    trade at all. Of those that did, 95–99.8% still cleared.
  - The median persisting sale keeps essentially all of its edge.
- **So the executable answer is an hourly taker: about $295–317k a year at $15M (all4), $256–289k ETH-only.**
  - The daily re-quote ($210,512) falls below (f)'s 95% interval ($218,712–$377,227).
  - A keeper signs one CoW order per token per hour. Nothing races for block position: the sale happened up to an hour
    earlier.
- **The 2026-10-10 late-entry test was overstated.** It delayed the decision but still filled each sale at its own
  price, and reported 96% kept at an hour and 91% at a day. Priced at the later market, an hour keeps 72–77% (all4) and
  a day keeps 52%. This changes the repo's late-entry screen; see Method change.

## The bridge

- **Ladder (2026-10-11, v1 rule).** Hurdle 1bp (the all4 choice at $15M, checked against queue_book at runtime).
  Carry = wstETH's 30-day NAV growth (2.313% a year) × the queue wait.

| token | NAV (ETH) | wait (days) | carry (bp) | limit (ETH/token) | below NAV (bp) | market median now (bp) |
|---|---:|---:|---:|---:|---:|---:|
| stETH | 1.00000000 | 1.00 | 0.63 | 0.99983692 | 1.63 | 0.16 |
| wstETH | 1.24601367 | 1.00 | 0.63 | 1.24581048 | 1.63 | 0.16 |
| weETH | 1.10549621 | 0.47 | 0.30 | 1.10535241 | 1.30 | 1.54 |
| rsETH | 1.08173852 | 6.37 | 4.04 | 1.08119369 | 5.04 | 26.60 |

- **Orders.** One GPv2 order per token, each sized to the whole (unescrowed) pool, valid 26 hours. The digest code is
  pinned to two real orders: uid `0x01a4bae6…` (fetched from CoW's API, a 150-WETH partially fillable sell for stETH)
  and one from cow_fill_check's data. The digest equals the uid's first 32 bytes. The `eth-account` library's EIP-712
  hash agrees for both and for all four of today's orders.
- **Kill criteria, computed daily** (`monitor`):
  1. **Trailing 90 days at $15M** (2026-07-12 → 10-10): $306,707 a year under the backtest convention ($162,276 for
     the v3 hourly taker, $146,257 for the v2 daily re-quote). All are above the $40k line, but ETH-only is thin: $59,919
     for v3.
  2. **Payout checks pass**: 83 Lido claims, 23 ether.fi (no fee, no invalidation) and 3 Kelp, all paid in full.
  3. **LBTC vs ETH-token locked-capital correlation** over the trailing year: −0.034. The pass line is 0.5.
  4. **Resting orders not filling.** The literal check flags 31 hours, every one in a token with no CoW buyers that
     hour, so they show no bidding rather than failed fills. Of 25 observed resting orders, none sat through a cleared
     hour.
     - Once our own orders rest, the check reads the owner's orders from CoW's account endpoint (it lists unfilled
       ones) and the funded hours. A funded order that sits through a cleared hour without filling is a failure.
- **Paper ledger.** v1 registered for 2026-10-11 (resting at hurdle + carry). v2 (daily re-quoted limit) and v3 (hourly
  taker) are frozen and register from the 2026-10-12 run. Each version is scored as its own paper pool. P&L is reported
  at the rule's price, at the first trade, and at the worst accepted price. There are 0 fills so far, because no
  finalized sales came after the first registration.

## Method change

- **Late entry means entering late at the later price.** The repo's screen (feedback: "entering an hour late keeps most
  of the edge") must price the delayed entry at the market when it happens, not at the original print.
- `queue_book.simulate_book(delay_s=…)` and `dislocation_history.simulate_bid` delay only the decision.
- Every queue study's late-entry claim is therefore optimistic: weETH/stETH/rsETH (2026-10-09), LBTC (2026-10-10),
  kHYPE, the five-asset book and sAVAX (2026-10-11).
- `queue_live.py implementations` holds the corrected version, (f) and (g). It should become an option of
  `simulate_book` so every study uses it.

## Errors found in the worker's own work (all fixed)

1. The limit was rounded to the nearest 1e-4bp, which could price up to 5e-9 above the exact limit. It now rounds the
   discount up (tested with exact fractions).
2. Criterion 4 first reported "kill" on 30 hours that only showed no bidding.
3. The quote's venue fees first came from the new window only.
4. The paper P&L at the limit ignored NAV accrual after registration (a signed limit is a fixed price).
5. A garbled guard in `register`; four wrong test expectations over three rounds (the code was right each time).
6. A verdict clause said a day-late join loses a third of (b) and (d). It keeps 37–45%, and the clause is now computed.

## Caveats

- (f) prices the whole buyback at the later price. Where others partly bought the pool back, a large buy walks past it,
  so big volumes are flattered.
- The strict readings skip sales whose next hour had no trade. A real taker would still buy those, so rsETH and LBTC are
  understated.
- Carry uses the same hindsight-measured wait as the backtest.
- (b) and (d) keep simulate_book's $5k minimum and $10 gas filters, which a resting order cannot refuse.

## Coordinator's check

- **Persistence, from the priced swaps directly.** The check uses `queue_book.load_env` and the raw
  `swaps_<asset>.jsonl.gz`, with the later median taken over all trades in [H, H+1h); it does not use queue_live's code.
  - stETH/wstETH: 138,092 qualifying sales, **98.4%** still clear 1bp at the next hour.
  - weETH: 37,899 sales, **92.9%**.
  - The note says 98% and 91%. The 2pp on weETH comes from the median definition (all trades pooled here, venue
    medians there).
- **Trailing-90-day figures** in `research/queue_live/monitor/2026-10-11.json`: all4 $306,707, eth3 $137,989, at-hurdle
  $20,569. They match the note.
