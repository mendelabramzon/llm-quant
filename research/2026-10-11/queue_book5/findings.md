# The queue book with kHYPE (five assets) and sAVAX at swap level — 2026-10-11

The one-pool queue book (`research/2026-10-10/queue_book`) runs the stETH, weETH, rsETH and LBTC queue bids from one
capital pool. kHYPE's bid was priced alone ($140,043 a year at $10M), and its locked capital looked uncorrelated with
the others. The joint simulation was never run, because kHYPE's environment lived inside `queue_bids_alt`. This study
exports it, runs the five-asset book under the same protocol, and rebuilds sAVAX from swaps.

**Read with the implementation caveat.** The first sections use `simulate_book`'s original convention: each sale is
bought at its own discount, capped at the venue median of its own hour. Only a bidder behind each seller gets that.
The last section re-prices everything as an hourly taker, the executable version (`research/2026-10-11/queue_live/
findings.md`). Quote those numbers, not the earlier ones.

## Answer

- **kHYPE reproduces exactly** through queue_book's protocol.
  - All six sizes are bit-identical; $10M gives $140,043.01 at h = 20.
  - The exported environment carries HyperEVM's costs ($1 gas, $1k minimum fill) instead of Ethereum's ($10, $5k).
- **On the five assets' common window** (2025-07-15 → 2026-10-09; hurdle chosen before 2026-02-26, tested on the
  following 226 days), one $15M pool earns **$460,554 a year** (t 4.55). The four Ethereum-side assets earn $276,873
  (t 3.50) on the same window.
- **The gain depends on moving capital between chains.** In a kHYPE stress the whole pool sits in kHYPE at day's end.

| $15M, five assets | out of sample | t | over all4 |
|---|---:|---:|---:|
| one fungible pool (ceiling) | $460,554 | 4.55 | +$183,681 |
| kHYPE leg an hour behind | $424,749 | 4.06 | +$147,876 |
| **kHYPE leg a day behind** (draft quote) | **$368,046** | 4.35 | +$91,173 |
| fixed split chosen in sample ($10M HyperEVM, $5M Ethereum) | $285,931 | 2.58 | +$9,058 |

- **sAVAX earns $75,530 a year at $3M** (t 6.38; 95% interval $50,603–$103,647). The flow caps it ($10M earns only
  $77,399).
- **The 2026-10-10 sAVAX queue model was wrong.** Benqi pays the rate recorded at the end of the 15-day cooldown, not
  at the request, so queued sAVAX keeps accruing.
  - Confirmed on 6,013 redeems: median −0.00001bp from the cooldown-end rate, p10–p90 ±0.024bp. That is 19.17bp above
    the rate at the request.
  - On the same sales the old model gives $17,186.
- **sAVAX does not diversify kHYPE.** Their daily locked capital correlates 0.67. Against the four Ethereum-side bids
  summed it is −0.01.

## The five-asset book by size (out of sample, every book chose h = 10)

| pool | all5 | t | 95% interval | stETH / weETH / rsETH / LBTC / kHYPE | all4, same window (t) |
|---:|---:|---:|---|---|---:|
| $5M | $201,382 | 5.97 | $140k–$267k | 7k / 35k / 31k / 41k / 87k | $145,888 (3.94) |
| $10M | $330,467 | 5.60 | $218k–$452k | 22k / 81k / 33k / 62k / 133k | $223,655 (3.86) |
| **$15M** | **$460,554** | 4.55 | $271k–$681k | 44k / 112k / 33k / 63k / 209k | $276,873 (3.50) |
| $20M | $575,433 | 3.91 | $306k–$894k | 66k / 135k / 33k / 63k / 279k | $329,482 (3.13) |
| $30M | $757,472 | 3.68 | $377k–$1.21M | 126k / 170k / 33k / 82k / 346k | $432,312 (2.63) |

- **Late entry** (the 2026-10-10 definition, which delays the decision but keeps each sale's own price) keeps 85–94%.
  That definition is what the persistence test re-examines.
- **Top month:** 27% of the out-of-sample value (top two 48–53%), against 32–41% for all4.
- **Correlations of daily locked capital** (10bp, unbounded capital):
  - weETH–stETH 0.83;
  - LBTC against the ETH bids −0.13 to −0.19;
  - kHYPE against the three ETH bids summed −0.14, against LBTC +0.13.
- **Weak points.**
  - The chosen h = 10 ranked 6th of 7 out of sample.
  - The in-sample half was 2.1–2.8× richer.
  - The test half is only 226 days, because kHYPE launched in July 2025.

## Implementation of the kHYPE leg

- CoW Protocol is not on HyperEVM, so the kHYPE leg cannot be an unescrowed resting order.
- When kHYPE's venue median clears the hurdle, capital moves to WHYPE on HyperEVM, and a keeper buys on the
  kHYPE/WHYPE pools. Out-of-sample fills were mostly on Ramses v3 (1,982), Project X (1,234) and Nest (717).
- Then Kinetiq `queueWithdrawal`, and `confirmWithdrawal` after 7 days. The HYPE exposure is hedged with a short perp.
- Valantis STEX is a competing standing bidder.
- The draft row (`book_entries.json`, `draft: true`) quotes the day-behind variant, $368,046 at $15M, go. **It is not
  written to the book**: the persistence test decides the implementation first, and any re-quote needs the user's
  approval.

## sAVAX data

- 231,974 swaps rebuilt from 16 sAVAX/WAVAX pools; 210,399 priced.
  - Tenderly's public gateway and api.avax.network both honour the block tag; publicnode and 1rpc are not archives.
  - 3,239 RPC calls, 0 errors.
  - The rate at 40 random swap blocks differs from the interpolated grid by a median 0.010bp.
- **Market.** Hourly discount median 17.7bp, 90th percentile 42.2bp; 46% of hours at 20bp or more. Swap prices agree
  with GeckoTerminal bars to 0.6–1.0bp.
- **Queue.** Cooldown 15 days, redeem window 2 days; the fastest redeem per request day was 15.00–15.04 days.
- **Bid.** Trailing 90 days $40,362 at $3M. Late entry (old definition) keeps 95% at an hour, 93% at a day. Lumpy:
  June–July 2026 hold 59% of the out-of-sample value.
- **Pool.** A fungible six-asset pool adds about $39k over all5 at $10–15M.

## Re-priced as hourly takers (the numbers to quote)

- **The option.** `simulate_book(later='hour'|'day', later_price='median'|'first')` (default off; the 2026-10-10 output
  reruns bit-identically).
  - A sale qualifies on its own-hour edge.
  - It is bought at the next hour boundary H, at min(print less two fees, the median of trades inside [H, H+1h) less one
    fee) − carry − fee.
  - It is skipped if nothing traded. Capital locks from the purchase.
- **Two implementations agree to the cent.** On queue_book's own environments, all4 at $15M gives $294,743.26 (t 7.51)
  at the median and $317,252.97 at the first trade, identical to `queue_live.py implementations` (f).
- **Persistence into the next hour** (qualifying sales still clearing 1bp at the next hour's median):
  - kHYPE 98% of 119,823, with every next hour traded;
  - sAVAX 98% of 18,709;
  - stETH 98%, weETH 91%, rsETH 34% and LBTC 53% (the last two mostly quiet hours, not recoveries).

| book (hourly taker, venue median) | out of sample | t | before (own print) |
|---|---:|---:|---:|
| kHYPE alone, $10M | $113,872 (h = 20) | 1.21 | $140,043 |
| kHYPE alone, $30M | $334,407 | 2.50 | $373,849 |
| all5, $15M, fungible across chains | $353,855 | 3.12 | $460,554 |
| **all5, $15M, kHYPE leg a day behind** (the draft row) | **$293,463** | 3.27 | $368,046 |
| all5, $15M, fixed split | $194,923 | — | $285,931 |
| all4, $15M, same 452-day window | $184,984 | 2.42 | $276,873 |
| all4, $15M, queue_book's 744-day window | $294,743 | 7.51 | $409,889 |
| sAVAX, $3M | $70,073 (h = 10) | 6.55 | $75,530 |

- **kHYPE alone now fails the book's go rule** (t 1.21). Its re-quote draft (`book_entries_khype_requote.json`,
  $113,872, go = no) keeps the row's $10M size rather than pick $30M after the fact.
- **Inside the pool kHYPE still adds +$108k** at $15M with the one-day crossing (+$169k fungible), over a quieter
  stretch for the ETH queues: all4 alone earns $184,984 on this window against $294,743 over two years.
- **Late entry at the later price** keeps 91–111% for the pools (the hurdle is re-chosen) and 104–105% for sAVAX.
- **The coordinator recommends quoting the four-asset hourly taker** for `lst-queue-book-one-pool`
  (`research/2026-10-11/queue_live/book_entries.json`: $294,743, t 7.51, two-year window). The five-asset draft
  quotes the same dollars with a shorter test (226 days, t 3.27) and needs capital to cross chains within a day. It is
  the upgrade once a HyperEVM leg runs.

## Errors found in the worker's own work (all fixed)

1. The first capital-use table counted a fill on every day it touched (kHYPE peaked at $22.2M inside a $15M pool). It
   is now an end-of-day snapshot.
2. One test expectation was wrong: an undelayed asset with no venue median is uncapped. The code was right.
3. The draft-row generator first referenced missing keys, and its venue sentence first cited whole-window volume. It
   is now generated from the fills.
4. The sAVAX renderer labelled the min and max as p1–p99.
5. Batched Tenderly calls drew 429s. The collection was restarted with single calls on a 20k-block grid.

## Open issues

- **Inputs outside the repo.** The lido/kelp swaps exist only in scratchpads (sha256s are in the manifest). Regenerate
  them with `dislocation_history.py analyze --assets lido,kelp` if the scratchpads are cleaned.
- **Stale entries left as they are.** `queue_bids_alt`'s sAVAX queue note and its "watch" verdict are now known to be
  wrong. They were left unchanged because existing results must not change.
- `queue_bids_alt.py` gained a `savax` subcommand. It is additive, and the 2026-10-10 analysis reruns bit-identically.

## Coordinator's check

Recomputed all5 at $15M and h = 10 from the environments alone (`queue_book.load_env` for the four Ethereum-side
assets, `queue_bids_alt.khype_book_env` for kHYPE, one `simulate_book` call). It does not read `analysis.json`.

- 5,219 out-of-sample fills over 226 days: **$460,554.41 a year**.
- By asset: weETH $112,279, kHYPE $209,041, LBTC $62,547, stETH $44,004, rsETH $32,682.
- Identical to the stored result.
