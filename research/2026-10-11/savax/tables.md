# sAVAX at swap level — tables

Generated 2026-10-11T04:07:09Z from `analysis.json` by `scripts/queue_bids_alt.py savax --step render`.

Window 2025-07-15 → 2026-10-09 (452 days), split 2026-02-26; swaps rebuilt from sAVAX/WAVAX transfers into and out of 16 pools.

## A. Data path

| item | value |
|---|---|
| block tag honoured: https://api.avax.network/ext/bc/C/rpc | rate 1.288948 at 97238324 vs 1.257228 at 82238324: yes |
| block tag honoured: https://avalanche-mainnet.gateway.tenderly.co | rate 1.288948 at 97238324 vs 1.257228 at 82238324: yes |
| exchange rate at 40 random swap blocks vs the interpolated grid | median 0.010bp, max 3.076bp |
| swaps priced / sales of at least $1,000 | 210,399 / 20,691 |
| prints dropped (over 300bp from the rate) | 847 ($2,547,546) |
| RPC calls / errors | 3239 / 0 |

## B. The queue, from the verified source and every event in the window

| item | value |
|---|---|
| cooldownPeriod / redeemPeriod (read at the last block) | 15.00 days / 2.00 days |
| parameter updates in the window | 0 |
| what redeem pays | shares x the rate recorded by the last accrueRewards at or before startedAt + cooldownPeriod |
| paid rate vs the rate at the end of the cooldown | median -0.00bp, p10–p90 -0.02bp to 0.02bp, p99 0.17bp, range -12.77bp to 4.33bp (n 6013) |
| paid rate vs the rate at the request | median 19.17bp (the cooldown's accrual) |
| request → redeem, days | min 15.00, p5 15.00, median 15.07, p90 16.02, max 17.00; 89% within a day of the cooldown |
| fastest redeem of the requests made each day, days | median 15.002, p90 15.026, p99 15.043, max 16.352 (456 request days) |
| sAVAX requested / redeemed / returned overdue / cancelled | 16,929,330 / 14,680,682 / 1,105,644 / 1,026,037 |
| redeemed share of resolved requests | 87% (2461 redeemers; 3628 accounts let requests lapse) |
| accrueRewards | 16765, median gap 0.59 h, longest 25.2 h |
| warden withdrawals / deposits (AVAX) | 26,851,527 / 19,127,809 |

## C. Discount to the exchange rate (hourly, volume-weighted across pools)

| hours traded | p50 | p90 | p99 | max | ≥10bp | ≥20bp | ≥50bp | round trip | episodes (hours) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10,438 | 17.7bp | 42.2bp | 72.6bp | 194.3bp | 70% | 46% | 7% | 2.1bp | 83 (9838) |

| pool | pool-hours | volume | vw discount |
|---|---:|---:|---:|
| blackhole-v3 | 4,956 | $161,487,477 | 25.2bp |
| curve | 3 | $14 | 21.0bp |
| lydia | 80 | $62 | 51.3bp |
| pangolin | 905 | $19,370 | 107.2bp |
| pangolin-v3 | 1,196 | $70,045 | 26.0bp |
| pharaoh-dlmm | 936 | $12,459,100 | 43.7bp |
| pharaoh-legacy | 2,980 | $91,333,513 | 20.9bp |
| pharaoh-v3 | 7,067 | $85,833,038 | 33.7bp |
| traderjoe-v1 | 3,576 | $512,030 | 35.6bp |
| traderjoe-v2.2 | 7,935 | $219,036,461 | 23.6bp |
| traderjoe-v2.2-bs10 | 109 | $574,708 | 26.8bp |
| uniswap-v3 | 868 | $16,893 | 85.2bp |

| episode start | end | hours | volume | vw discount | peak | net of round trip |
|---|---|---:|---:|---:|---:|---:|
| 2025-09-09T06:00 | 2026-01-24T15:00 | 3270 | $312,893,490 | 32.5bp | 178.6bp | 30.4bp |
| 2025-07-15T23:00 | 2025-08-21T16:00 | 872 | $124,557,768 | 16.0bp | 67.3bp | 13.9bp |
| 2026-05-30T20:00 | 2026-07-08T22:00 | 908 | $18,491,449 | 43.2bp | 194.3bp | 41.2bp |
| 2026-03-03T15:00 | 2026-05-30T17:00 | 1997 | $30,623,392 | 19.1bp | 110.7bp | 17.1bp |
| 2026-07-11T01:00 | 2026-08-12T17:00 | 728 | $11,608,376 | 43.8bp | 85.4bp | 41.7bp |
| 2026-01-25T02:00 | 2026-02-14T04:00 | 451 | $16,370,061 | 15.3bp | 60.1bp | 13.2bp |
| 2026-07-09T01:00 | 2026-07-10T22:00 | 40 | $744,333 | 69.8bp | 76.3bp | 67.7bp |
| 2026-09-18T07:00 | 2026-09-27T01:00 | 202 | $3,071,557 | 11.0bp | 28.0bp | 9.0bp |

## D. The bid, out of sample (hurdle chosen on the first half, scored once on the second)

| size | hurdle | in sample | out of sample | 95% interval | t | fills OOS | median edge | trailing 90d |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| $100,000 | h=20 | $4,886 | $4,791 | $2,457 to $7,646 | 3.47 | 192 | 27.9bp | $3,480 |
| $300,000 | h=20 | $14,634 | $13,492 | $7,372 to $20,878 | 4.09 | 448 | 28.1bp | $7,560 |
| $1,000,000 | h=20 | $48,467 | $37,494 | $21,045 to $58,275 | 4.29 | 1142 | 27.7bp | $16,944 |
| $3,000,000 | h=10 | $123,780 | $75,530 | $50,603 to $103,647 | 6.38 | 3622 | 22.6bp | $40,362 |
| $10,000,000 | h=10 | $366,720 | $77,399 | $51,760 to $106,767 | 6.44 | 3687 | 25.7bp | $40,362 |
| $30,000,000 | h=2 | $706,339 | $82,186 | $57,144 to $110,680 | 7.01 | 4616 | 23.7bp | $44,869 |

Quoted at $3,000,000 (capacity rule: $3,000,000). Late entry (hurdle held): an hour late keeps 95%, a day late 93%. Verdict: **proposed**.

| variant at $3,000,000 | out of sample $/yr |
|---|---:|
| as quoted: accrual through the cooldown, measured redeem waits, venue-median cap | $75,530 (h=10) |
| the 2026-10-10 queue model at $3,000,000 (amount fixed at the request, 15.5 days of staking carry) | $17,186 (h=20) |
| per print, no venue-median cap (an upper bound) | $81,958 |
| GeckoTerminal bars, 2026-10-10 (2026-03-30 +194 days, half the volume as sales) | $42,343 at $3,000,000 |

| hourly taker (each qualifying sale bought at the next hour boundary) | own print | venue median of that hour | t | 95% interval | first trade after it |
|---|---:|---:|---:|---|---:|
| $1,000,000 | $37,494 | $33,318 (h=20) | 3.94 | $17,220 to $54,286 | $34,211 (h=20) |
| $3,000,000 | $75,530 | $70,073 (h=10) | 6.55 | $47,389 to $95,972 | $70,983 (h=10) |
| $10,000,000 | $77,399 | $71,482 (h=10) | 6.59 | $48,620 to $97,596 | $72,388 (h=10) |

Hourly taker at $3,000,000, late entry with the later price: an hour late 105%, a day late 104%; trailing 90 days $36,602.
Persistence at 1bp: of 18,709 sales that qualified in their own hour, 98% still cleared it at the next hour's venue median (98% by volume; 1% had no trade next hour; 99% of those traded), 96% at the first trade.
Persistence at 10bp: of 14,570 sales that qualified in their own hour, 97% still cleared it at the next hour's venue median (95% by volume; 1% had no trade next hour; 98% of those traded), 94% at the first trade.

Sales the bid could have bought at a profit: on 440 of 452 days; $171,962 on the median such day, $1,078,617 at the 90th percentile.

## E. The same pool-hours priced two ways (GeckoTerminal bar vs swap VWAP rebuilt from chain)

| pool | hours in both | median abs gap | p90 abs gap | signed median | bar volume / swap volume (p50) |
|---|---:|---:|---:|---:|---:|
| kyberswap-elastic | 0 | — | — | — | — |
| pharaoh-legacy | 0 | — | — | — | — |
| pharaoh-v3 | 3,841 | 0.60bp | 1.32bp | 0.00bp | 1.00 |
| traderjoe-v1 | 190 | 0.21bp | 20.02bp | -0.03bp | 1.00 |
| traderjoe-v2.2 | 762 | 1.00bp | 2.66bp | 0.49bp | 1.00 |

## F. Daily locked capital against the five-asset book (unbounded capital, 10bp; 2025-07-15 → 2026-10-09, 452 days)

| sAVAX against | correlation | days both locked | days either | at sAVAX's own hurdle (10bp) |
|---|---:|---:|---:|---:|
| etherfi_ev | 0.01 | 152 | 449 | 0.01 |
| kelp | -0.04 | 259 | 450 | -0.04 |
| khype | 0.67 | 228 | 443 | 0.67 |
| lbtc_cb | 0.24 | 304 | 446 | 0.24 |
| lido | -0.02 | 109 | 450 | -0.02 |
| the all4 summed | -0.01 | | | -0.01 |
| the all5 summed | 0.15 | | | 0.15 |
| the eth3 summed | -0.01 | | | -0.01 |

sAVAX would lock capital on 443 of 452 days; peak $28,803,262.

Fungible upper bound only (sAVAX sits on a third chain, with the same capital-crossing caveat as kHYPE):

| pool | all5 | all6 | increment | hurdle all6 | t all6 | sAVAX in all6 |
|---:|---:|---:|---:|---|---:|---:|
| $10,000,000 | $330,467 | $369,270 | $38,803 | h=10 | 7.19 | $61,830 |
| $15,000,000 | $460,554 | $499,807 | $39,252 | h=10 | 5.50 | $64,449 |
