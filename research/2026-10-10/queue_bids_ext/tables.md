# Queue bids, extended: tables

Generated 2026-10-10T12:23:03Z by `dislocation_history.py report`; every number is in analysis.json.

## A. ether.fi payout check (WithdrawRequestNFT, 2024-09-26 to 2026-10-10)

| measure | n | min | p1 | p10 | p50 | p90 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| payout vs eETH requested (bp) | 42756 | -5000.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| payout vs eETH requested, requests of 0.01 eETH or more (bp) | 40890 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| eETH requested vs share value at finalization (bp): the yield a prompt claimer forgoes | 40895 | -12.401 | -10.999 | -4.577 | -0.729 | -0.230 | -0.085 | -0.035 |
| payout vs share value at the claim (bp): includes owners who waited to claim | 42756 | -902.398 | -383.001 | -34.845 | -3.715 | -0.514 | -0.218 | -0.035 |
| request rate vs Rebase-event NAV (bp) | 40890 | -0.352 | -0.000 | -0.000 | 0.000 | 0.000 | 0.002 | 0.468 |
| request rate vs daily interpolated getRate (bp) | 40916 | -1.077 | -0.298 | -0.129 | -0.000 | 0.127 | 0.242 | 0.650 |
| getRate vs Rebase-event NAV at admin blocks (bp) | 310 | -0.000 | -0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| request to finalization (days) | 42761 | 0.052 | 0.089 | 0.236 | 0.794 | 6.460 | 16.041 | 17.566 |
| finalization to claim (days) | 42756 | 0.000 | 0.001 | 0.039 | 2.197 | 45.947 | 549.041 | 656.082 |
| request to claim (days) | 42756 | 0.064 | 0.243 | 0.678 | 5.133 | 48.834 | 549.778 | 656.367 |

Requests in window 42784 (4,768,155 eETH) from 30354 addresses; claims decoded 45073; event versions {"4 claimed": 2664, "4 open": 23, "5 claimed": 40092, "5 open": 5}. Exact payouts 100%; short by more than 0.01bp: 8 (0.000000 ETH in all). Fees: 0 requests carried one (0.000000 ETH). Invalidated [77151]; seized []. Unfinalized at the end 23 (1459.97 eETH); finalized but unclaimed 5 (750.91 eETH). NFTs moved between holders 786 times; 694 claims paid an owner other than the requester. Amount-weighted median wait 1.69 days.

Counter cross-check: 740 daily samples of lastFinalizedRequestId (the 2026-10-09 study) compared with the value after the latest admin execution: 0 mismatches.

| month | requests | eETH | wait p50 (days) | p90 | max | unfinalized | payout vs request p50 (bp) | vs NAV at payout p50 (bp) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-09 | 1312 | 41,722 | 0.2 | 0.3 | 0.4 | 0 | 0.0 | -1.7 |
| 2024-10 | 5570 | 321,156 | 0.4 | 0.6 | 2.1 | 0 | 0.0 | -2.8 |
| 2024-11 | 4210 | 256,596 | 0.3 | 0.6 | 1.2 | 0 | 0.0 | -2.5 |
| 2024-12 | 3297 | 364,813 | 0.7 | 0.9 | 3.8 | 0 | 0.0 | -2.4 |
| 2025-01 | 2265 | 137,234 | 0.7 | 1.5 | 3.0 | 0 | 0.0 | -2.7 |
| 2025-02 | 2783 | 235,475 | 0.7 | 0.9 | 1.4 | 0 | 0.0 | -1.9 |
| 2025-03 | 1651 | 206,489 | 0.7 | 1.3 | 2.0 | 0 | 0.0 | -2.1 |
| 2025-04 | 992 | 206,981 | 1.3 | 6.0 | 8.1 | 0 | 0.0 | -4.0 |
| 2025-05 | 920 | 116,177 | 1.4 | 2.8 | 5.9 | 0 | 0.0 | -5.6 |
| 2025-06 | 882 | 132,784 | 2.2 | 2.4 | 3.2 | 0 | 0.0 | -5.6 |
| 2025-07 | 1533 | 286,256 | 3.6 | 7.1 | 7.7 | 0 | 0.0 | -7.3 |
| 2025-08 | 2888 | 245,811 | 10.0 | 16.2 | 17.6 | 0 | 0.0 | -10.9 |
| 2025-09 | 1503 | 168,013 | 4.5 | 5.9 | 8.1 | 0 | 0.0 | -5.9 |
| 2025-10 | 832 | 85,472 | 5.2 | 5.4 | 5.5 | 0 | 0.0 | -9.4 |
| 2025-11 | 928 | 125,350 | 6.9 | 12.6 | 14.7 | 0 | 0.0 | -9.6 |
| 2025-12 | 932 | 39,989 | 5.3 | 5.4 | 6.0 | 0 | 0.0 | -8.5 |
| 2026-01 | 951 | 67,008 | 3.1 | 3.5 | 6.0 | 0 | 0.0 | -4.8 |
| 2026-02 | 1018 | 254,712 | 5.0 | 9.6 | 11.0 | 0 | 0.0 | -5.5 |
| 2026-03 | 1027 | 308,365 | 2.2 | 3.5 | 6.9 | 0 | 0.0 | -2.9 |
| 2026-04 | 1475 | 364,053 | 9.7 | 16.0 | 16.5 | 0 | 0.0 | -9.1 |
| 2026-05 | 1500 | 366,386 | 0.7 | 4.4 | 8.4 | 0 | 0.0 | -2.4 |
| 2026-06 | 1219 | 137,458 | 1.5 | 3.4 | 7.2 | 0 | 0.0 | -1.8 |
| 2026-07 | 824 | 113,600 | 0.4 | 3.9 | 5.1 | 0 | 0.0 | -1.6 |
| 2026-08 | 1099 | 94,930 | 0.3 | 0.4 | 1.2 | 0 | 0.0 | -0.2 |
| 2026-09 | 904 | 74,562 | 1.0 | 1.2 | 3.0 | 0 | 0.0 | -0.7 |
| 2026-10 | 269 | 16,762 | 1.0 | 2.9 | 3.4 | 23 | 0.0 | -0.7 |

### Instant redemptions (EtherFiRedemptionManager)

Events 15123, first 2025-03-26T14:10:55Z; eETH by output {"ETH": 16424, "stETH": 400075}.

| from (UTC) | output | fee bp |
|---|---|---:|
| 2025-03-26T14:10 | ETH | 30 |
| 2025-11-12T16:13 | stETH | 0 |
| 2025-11-24T22:14 | stETH | 10 |
| 2025-12-13T00:57 | stETH | 0 |
| 2025-12-13T11:10 | stETH | 10 |
| 2026-03-25T15:46 | stETH | 0 |
| 2026-03-28T17:58 | stETH | 10 |
| 2026-04-01T18:30 | stETH | 0 |
| 2026-04-02T18:17 | stETH | 10 |
| 2026-04-24T15:33 | stETH | 0 |
| 2026-04-24T16:16 | stETH | 10 |
| 2026-07-15T08:14 | stETH | 9 |
| 2026-07-15T15:22 | stETH | 10 |

| month, output | redemptions | eETH | fee bp p50 | min | max |
|---|---:|---:|---:|---:|---:|
| 2025-03 ETH | 6 | 384 | 30.0 | 30.0 | 30.0 |
| 2025-04 ETH | 322 | 1,518 | 30.0 | 30.0 | 30.0 |
| 2025-05 ETH | 839 | 4,374 | 30.0 | 30.0 | 30.0 |
| 2025-06 ETH | 435 | 1,547 | 30.0 | 30.0 | 30.0 |
| 2025-07 ETH | 349 | 1,336 | 30.0 | 30.0 | 30.0 |
| 2025-08 ETH | 35 | 442 | 30.0 | 30.0 | 30.0 |
| 2025-09 ETH | 173 | 502 | 30.0 | 30.0 | 30.0 |
| 2025-10 ETH | 327 | 2,781 | 30.0 | 30.0 | 30.0 |
| 2025-11 ETH | 1 | 3 | 30.0 | 30.0 | 30.0 |
| 2025-11 stETH | 451 | 37,747 | 0.0 | 0.0 | 10.0 |
| 2025-12 ETH | 98 | 518 | 30.0 | 30.0 | 30.0 |
| 2025-12 stETH | 132 | 29,053 | 10.0 | 0.0 | 10.0 |
| 2026-01 ETH | 152 | 170 | 30.0 | 30.0 | 30.0 |
| 2026-01 stETH | 108 | 896 | 10.0 | 10.0 | 10.0 |
| 2026-02 ETH | 96 | 226 | 30.0 | 30.0 | 30.0 |
| 2026-02 stETH | 37 | 267 | 10.0 | 10.0 | 10.0 |
| 2026-03 ETH | 22 | 158 | 30.0 | 30.0 | 30.0 |
| 2026-03 stETH | 20 | 120,228 | 10.0 | 0.0 | 10.0 |
| 2026-04 ETH | 73 | 2,107 | 30.0 | 30.0 | 30.0 |
| 2026-04 stETH | 11183 | 202,563 | 10.0 | 0.0 | 10.0 |
| 2026-05 ETH | 39 | 338 | 30.0 | 30.0 | 30.0 |
| 2026-05 stETH | 41 | 1,579 | 10.0 | 10.0 | 10.0 |
| 2026-06 stETH | 73 | 7,064 | 10.0 | 10.0 | 10.0 |
| 2026-07 ETH | 48 | 17 | 30.0 | 30.0 | 30.0 |
| 2026-07 stETH | 28 | 192 | 10.0 | 9.1 | 10.0 |
| 2026-08 ETH | 4 | 1 | 30.0 | 30.0 | 30.0 |
| 2026-08 stETH | 10 | 238 | 10.0 | 10.0 | 10.0 |
| 2026-09 stETH | 17 | 183 | 10.0 | 10.0 | 10.0 |
| 2026-10 stETH | 4 | 65 | 10.0 | 10.0 | 10.0 |

Implementation upgrades in the window: 2024-10-07 0x308861a4 -> 0xa8a8be86; 2024-10-07 0x0ef8fa47 -> 0x92c27ba5; 2025-01-20 0x35fa1647 -> 0x46c51d2e; 2025-03-20 0xdadef1ff -> 0xe6f40295; 2025-03-26 0x0ef8fa47 -> 0x68358397; 2025-03-26 0x308861a4 -> 0xa6099d83; 2025-03-26 weETH -> 0x353e98f3; 2025-03-26 0x7d5706f6 -> 0x685870a5; 2025-06-26 0x7d5706f6 -> 0xc227640c; 2025-08-07 0x35fa1647 -> 0xcb3d917a; 2025-08-07 0x0ef8fa47 -> 0xd50f2848; 2025-08-07 0x308861a4 -> 0x02591176; 2025-08-07 weETH -> 0x2d10683e; 2025-10-30 0xdadef1ff -> 0x590015fd; 2025-10-30 0x308861a4 -> 0xa5c1ddd9; 2025-10-30 0xdadef1ff -> 0xe3f384dc; 2025-12-15 0x308861a4 -> 0x45c2fb84; 2026-02-02 0x308861a4 -> 0x8765bb2f; 2026-02-12 0xdadef1ff -> 0xb4fed2bf; 2026-02-12 0x7d5706f6 -> 0x2f4a5921; 2026-03-16 0x308861a4 -> 0x83bc649f; 2026-03-16 0xdadef1ff -> 0x6bd19158; 2026-07-14 0x35fa1647 -> 0xd1901dd3; 2026-07-14 0x308861a4 -> 0x17a16747; 2026-07-14 weETH -> 0xa6ca0607; 2026-07-14 0x0ef8fa47 -> 0x5b083dde; 2026-07-14 0xdadef1ff -> 0x5d53b303; 2026-07-14 0x7d5706f6 -> 0x41617d01; 2026-09-25 0x0ef8fa47 -> 0x841fa691

## B. The weETH bid re-quoted (two-year window, hurdle chosen on the first year)

### weETH (ether.fi)

Wait: {"finalized": 739, "kind": "pointer", "max_days": 18.095, "median_days": 2.008, "p90_days": 6.04, "pending_at_end": 1, "pending_lower_bound_max_days": 0.0, "requests": 740}. Capacity $30,000,000 (capital locked in the queue (still growing at the largest size tested)). NAV max daily step {"weeth_nav": 1.55}.

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp | missed for capital |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| $100,000 | h=3 | $3,968 | $1,562 | $1,000 to $2,222 | $406 | 261 (89) | 4.1 | $2,874,192,993 |
| $300,000 | h=2 | $13,491 | $5,408 | $3,596 to $7,501 | $1,701 | 632 (196) | 3.5 | $3,721,332,399 |
| $1,000,000 | h=2 | $44,024 | $19,551 | $12,888 to $27,326 | $5,215 | 1308 (377) | 4.0 | $3,606,944,460 |
| $3,000,000 | h=1 | $123,696 | $55,129 | $35,779 to $76,811 | $14,412 | 3241 (860) | 3.3 | $4,089,888,424 |
| $10,000,000 | h=0 | $378,735 | $169,784 | $110,848 to $235,017 | $43,315 | 6931 (1961) | 3.3 | $3,503,956,329 |
| $30,000,000 | h=0 | $912,606 | $411,361 | $270,603 to $556,018 | $68,198 | 12031 (3840) | 4.3 | $1,842,688,528 |

### weETH (ether.fi), queue and NAV from events

Wait: {"finalized": 42761, "kind": "events", "max_days": 17.566, "median_days": 0.794, "p90_days": 6.46, "pending_at_end": 23, "pending_lower_bound_max_days": 0.895, "requests": 42784}. Capacity $30,000,000 (capital locked in the queue (still growing at the largest size tested)). NAV max daily step {}.

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp | missed for capital |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| $100,000 | h=2 | $5,384 | $1,778 | $1,125 to $2,501 | $476 | 428 (98) | 3.2 | $3,907,030,000 |
| $300,000 | h=2 | $19,072 | $6,101 | $4,080 to $8,364 | $1,816 | 783 (184) | 3.3 | $3,860,524,952 |
| $1,000,000 | h=2 | $62,228 | $22,573 | $15,125 to $31,226 | $6,153 | 1459 (308) | 3.5 | $3,710,483,444 |
| $3,000,000 | h=1 | $169,248 | $62,882 | $41,813 to $86,779 | $25,378 | 3838 (875) | 3.1 | $4,008,797,396 |
| $10,000,000 | h=1 | $479,992 | $194,238 | $134,517 to $260,084 | $58,190 | 7298 (2044) | 3.7 | $2,917,407,263 |
| $30,000,000 | h=1 | $1,057,884 | $431,076 | $291,336 to $586,626 | $76,025 | 11869 (3716) | 5.0 | $1,511,937,398 |

## C. Did the instant route cap the weETH discount? Hourly VW discount by regime

| regime | from | hours | p50 | p90 | p99 | max | >= 5bp | >= 10bp | >= 20bp | >= 30bp |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| no instant route | 2024-09-26 | 4174 | 3.0 | 5.7 | 13.2 | 57.7 | 15% | 2% | 0% | 0% |
| instant into ETH opens (30bp public) | 2025-03-26 | 5332 | 4.4 | 25.9 | 40.1 | 59.0 | 46% | 33% | 18% | 8% |
| instant into stETH opens (10bp public) | 2025-11-12 | 5939 | 2.9 | 12.8 | 40.7 | 94.6 | 31% | 15% | 7% | 3% |

## D. New assets (2024-09-26 to 2026-10-09, split 2025-10-03)

### LBTC (Lombard)

Unit BTC. Swaps 33586, volume $1,986,383,998, sold $982,363,324; excluded prints 89. Hourly VW discount p50/p90/p99 5.4/17.7/26.3 bp; sells p50/p90/p99 10.0/20.6/31.3 bp. Wait {"kind": "constant", "median_days": 9.0}. Capacity $30,000,000 (capital locked in the queue (still growing at the largest size tested)); OOS $213,109 a year (CI $100,888 to $340,411), trailing 90 days $372,885.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-lbtc-cbbtc | 4395 | $410,756,249 | $202,679,839 | 13.9 | 17.0 | 1.00 |
| fluid-wbtc-lbtc | 7298 | $520,027,332 | $259,225,875 | 8.4 | 5.3 | 1.00 |
| v3-lbtc-cbbtc-1bp | 36 | $1,571,123 | $793,661 | 59.5 | 21.6 | 1.00 |
| v3-lbtc-wbtc-1bp | 21196 | $1,007,689,266 | $496,261,310 | 6.4 | 8.5 | 1.00 |
| v4-lbtc-cbbtc-2bp | 661 | $46,340,027 | $23,402,640 | 24.9 | 15.5 | - |

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp |
|---:|---|---:|---:|---|---:|---:|---:|
| $100,000 | h=5 | $1,545 | $1,258 | $707 to $1,861 | $2,537 | 114 (62) | 12.7 |
| $300,000 | h=5 | $5,067 | $4,732 | $2,494 to $7,321 | $10,783 | 220 (123) | 12.7 |
| $1,000,000 | h=3 | $14,884 | $13,042 | $7,373 to $19,511 | $28,263 | 660 (317) | 11.9 |
| $3,000,000 | h=2 | $42,028 | $34,235 | $19,741 to $50,675 | $71,641 | 1479 (676) | 10.6 |
| $10,000,000 | h=5 | $132,722 | $109,761 | $54,498 to $172,595 | $251,449 | 2576 (1175) | 11.6 |
| $30,000,000 | h=1 | $337,676 | $213,109 | $100,888 to $340,411 | $372,885 | 5025 (1906) | 11.5 |

### LBTC (Lombard), cbBTC pools only

Unit BTC. Swaps 5092, volume $458,667,400, sold $226,876,139; excluded prints 0. Hourly VW discount p50/p90/p99 14.7/24.3/32.3 bp; sells p50/p90/p99 17.0/27.3/35.9 bp. Wait {"kind": "constant", "median_days": 9.0}. Capacity $10,000,000 (offered volume below NAV (more capital adds little)); OOS $111,136 a year (CI $65,117 to $165,420), trailing 90 days $189,369.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-lbtc-cbbtc | 4395 | $410,756,249 | $202,679,839 | 13.9 | 17.0 | 1.00 |
| v3-lbtc-cbbtc-1bp | 36 | $1,571,123 | $793,661 | 59.5 | 21.6 | 1.00 |
| v4-lbtc-cbbtc-2bp | 661 | $46,340,027 | $23,402,640 | 24.9 | 15.5 | - |

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp |
|---:|---|---:|---:|---|---:|---:|---:|
| $100,000 | h=2 | $2,254 | $2,263 | $1,551 to $3,040 | $869 | 141 (90) | 13.6 |
| $300,000 | h=5 | $6,867 | $7,529 | $5,291 to $9,968 | $7,361 | 253 (182) | 13.8 |
| $1,000,000 | h=3 | $23,508 | $20,477 | $14,660 to $26,722 | $19,463 | 604 (432) | 13.5 |
| $3,000,000 | h=2 | $61,749 | $54,486 | $37,074 to $75,513 | $73,479 | 1181 (824) | 13.1 |
| $10,000,000 | h=0 | $140,318 | $111,136 | $65,117 to $165,420 | $189,369 | 1800 (1134) | 13.5 |
| $30,000,000 | h=0 | $197,141 | $115,702 | $67,137 to $172,653 | $202,373 | 1979 (1142) | 14.1 |

### LBTC (Lombard), cbBTC pools, paid at the rate six days later

Unit BTC. Swaps 5092, volume $458,679,712, sold $226,881,785; excluded prints 0. Hourly VW discount p50/p90/p99 15.3/24.4/32.5 bp; sells p50/p90/p99 17.5/27.2/38.5 bp. Wait {"kind": "constant", "median_days": 6.0}. Capacity $10,000,000 (offered volume below NAV (more capital adds little)); OOS $121,970 a year (CI $71,630 to $181,411), trailing 90 days $201,798.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-lbtc-cbbtc | 4395 | $410,771,134 | $202,686,705 | 14.3 | 17.6 | 1.00 |
| v3-lbtc-cbbtc-1bp | 36 | $1,571,194 | $793,697 | 59.9 | 21.8 | 1.00 |
| v4-lbtc-cbbtc-2bp | 661 | $46,337,385 | $23,401,382 | 24.3 | 15.8 | - |

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp |
|---:|---|---:|---:|---|---:|---:|---:|
| $100,000 | h=5 | $3,136 | $3,372 | $2,535 to $4,247 | $1,684 | 215 (150) | 14.9 |
| $300,000 | h=5 | $9,732 | $10,181 | $7,543 to $12,836 | $6,564 | 381 (283) | 14.4 |
| $1,000,000 | h=3 | $30,918 | $29,928 | $21,623 to $38,875 | $27,347 | 808 (569) | 13.9 |
| $3,000,000 | h=2 | $81,085 | $76,429 | $50,154 to $105,091 | $108,395 | 1369 (958) | 14.2 |
| $10,000,000 | h=0 | $157,053 | $121,970 | $71,630 to $181,411 | $201,798 | 1881 (1158) | 14.6 |
| $30,000,000 | h=0 | $204,947 | $121,970 | $71,630 to $181,411 | $201,798 | 2015 (1158) | 15.1 |

### OETH (Origin)

Unit ETH. Swaps 21731, volume $252,367,673, sold $141,792,163; excluded prints 0. Hourly VW discount p50/p90/p99 5.6/12.8/25.9 bp; sells p50/p90/p99 6.3/12.8/27.2 bp. Wait {"finalized": 701, "kind": "oeth", "max_days": 49.2, "median_days": 0.01, "p90_days": 4.86, "pending_at_end": 0, "pending_lower_bound_max_days": null, "requests": 701}. Capacity $3,000,000 (offered volume below NAV (more capital adds little)); OOS $6,141 a year (CI $1,861 to $11,344), trailing 90 days $100.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-oeth-eth | 4532 | $50,928,723 | $30,266,393 | 8.0 | 6.9 | 4.00 |
| curve-oeth-weth | 17199 | $201,438,950 | $111,525,770 | 6.4 | 6.0 | 1.00 |

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp |
|---:|---|---:|---:|---|---:|---:|---:|
| $100,000 | h=2 | $167 | $1,612 | $386 to $3,534 | $0 | 136 (129) | 8.5 |
| $300,000 | h=1 | $559 | $3,122 | $1,058 to $6,023 | $100 | 203 (195) | 8.5 |
| $1,000,000 | h=1 | $1,857 | $4,386 | $1,453 to $8,227 | $100 | 226 (217) | 8.4 |
| $3,000,000 | h=1 | $4,702 | $6,141 | $1,861 to $11,344 | $100 | 270 (261) | 8.0 |
| $10,000,000 | h=0 | $10,592 | $6,693 | $2,427 to $11,883 | $818 | 303 (285) | 8.4 |
| $30,000,000 | h=0 | $10,592 | $6,693 | $2,427 to $11,883 | $818 | 303 (285) | 8.4 |

### tBTC (Threshold)

Unit BTC. Swaps 174899, volume $5,392,912,223, sold $2,681,639,935; excluded prints 69. Hourly VW discount p50/p90/p99 3.9/21.4/32.9 bp; sells p50/p90/p99 4.5/23.7/35.5 bp. Wait {"kind": "constant", "median_days": 0.2}. Capacity $30,000,000 (offered volume below NAV (more capital adds little)); OOS $58,834 a year (CI $1,840 to $161,943), trailing 90 days $1,787.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-tbtc-wbtc | 29382 | $1,152,866,194 | $573,463,066 | 4.7 | -0.2 | 1.00 |
| v3-tbtc-wbtc-1bp | 139130 | $4,002,084,739 | $1,990,485,370 | 7.6 | 5.3 | 1.00 |
| v4-tbtc-cbbtc-1bp | 6387 | $237,961,290 | $117,691,499 | 4.9 | 4.7 | - |

| size | hurdle | in-sample $/yr | OOS $/yr | 95% CI | trailing 90d $/yr | fills (OOS) | median edge bp |
|---:|---|---:|---:|---|---:|---:|---:|
| $100,000 | h=5 | $5,283 | $790 | $0 to $2,017 | $0 | 190 (24) | 8.2 |
| $300,000 | h=3 | $14,113 | $2,920 | $23 to $7,739 | $0 | 420 (57) | 6.3 |
| $1,000,000 | h=2 | $36,779 | $8,098 | $585 to $19,990 | $939 | 851 (159) | 5.6 |
| $3,000,000 | h=1 | $73,406 | $18,742 | $1,572 to $45,070 | $1,663 | 1437 (300) | 5.3 |
| $10,000,000 | h=0 | $107,437 | $44,605 | $1,840 to $117,862 | $1,787 | 1924 (562) | 6.2 |
| $30,000,000 | h=0 | $111,199 | $58,834 | $1,840 to $161,943 | $1,787 | 2175 (796) | 7.1 |

## D2. LBTC payouts matched on Bitcoin (sample)

| request event | sampled | matched | requests from | to | wait p50 (days) | wait max | paid vs getRate at request p50 (bp) | min | max | BTC paid per LBTC p50 |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|
| MessageSent | 25 | 20 | 2026-09-13 | 2026-09-30 | 5.4 | 10.2 | 2.3 | -6.2 | 9.8 | 1.004717 |
| UnstakeRequest | 30 | 28 | 2025-04-05 | 2025-11-01 | 6.0 | 9.6 | 0.0 | 0.0 | 1.5 | 1.000000 |

Paid per LBTC against getRate on the payout day (last daily sample before the payout), 20 payouts since 2025-11: median -0.00bp, -0.01 to 2.96bp. The payout applies the rate at payout, not at the request.

## E. Candidates ranked by DEX liquidity and redemption access (GeckoTerminal 24h, 2026-10-10)

| rank | token | 24h volume vs unit | reserve vs unit | redemption | access | queue | verdict |
|---:|---|---:|---:|---|---|---|---|
| 1 | LBTC | $12,078,338 | $15,773,354 | redeemForBtc to a bitcoin script (redeem before 2025-11-20); flat 10,000-sat fee; NAV 1/oracle ratio, 1.00485 BTC on 2026-10-09 | permissionless redemption to any bitcoin script; BTC paid off chain by Lombard, at LBTC x getRate (48 of 55 sampled payouts matched on Bitcoin); the bid's return leg (BTC -> cbBTC 1:1) needs a Coinbase account | measured on Bitcoin for a sample: request to payout median 5.4 days (2026-09, 20 payouts) and 6.0 days (2025, 28 payouts), max 10.2; Lombard docs say 7-9 days; the simulation uses 9 | PROPOSED (lombard-lbtc-queue-bid): cbBTC pools only, $10M, $111,136 a year out of sample (CI $65,117 to $165,420); all five pools give $109,761 at $10M but mix in WBTC's basis |
| 2 | OETH | $1,093,591 | $53,163,443 | OETH vault requestWithdrawal -> claimWithdrawal, WETH 1:1, no fee | permissionless; only the requester can claim | hours: measured from WithdrawalRequested/WithdrawalClaimable | too small: $6,141 a year out of sample at $3M (CI $1,861 to $11,344); the queue pays in minutes (median 20 minutes, p90 4.9 days) and the issuer's ARM bids too; payouts exact (693 claims) |
| 3 | tBTC | $550,836 | $21,859,630 | TBTCVault.unmintAndRedeem -> Bridge redemption; 0.2% treasury fee + bitcoin tx fee (<= 100,000 sats) | permissionless; BTC paid on Bitcoin | median 4.9h request to completion proof (1,000 requests, 2025-09/11) | not proposed: $58,834 a year out of sample at $30M but the interval starts at $1,840, October 2025's crash carries it and the trailing 90 days run at $1,787; 21bp fee; WBTC quotes carry their own basis |
| 4 | swETH | $185,564 | $227,166 | swEXIT createWithdrawRequest (max 500 swETH) -> finalizeWithdrawal; pays amount x min(rate at request, processed rate) | permissionless | not measured; 47 requests unprocessed at the 2026-10-10 read | too thin: one Uniswap v3 5bp pool with $0.16M reserve carries the volume |
| 5 | osETH | $157,181 | $31,197,311 | EthOsTokenRedeemer enterExitQueue -> claimExitedAssets at NAV when processed (accrues while queued) | permissioned until 2026-09-03 (redeemer was a Safe); open since | ~11h median since 2026-09-16; 29.23 osETH unprocessed since 2026-09-30; funding needs a privileged positions manager | permissioned for 23 of the 24 months; too new to price, watch |
| 6 | frxETH | $123,316 | $28,431,961 | FraxEtherRedemptionQueue v1: enterRedemptionQueue -> burnRedemptionTicketNft after a fixed maturity; fee 0 since 2023-11 | permissionless | fixed maturity 30 days now (7 to 60 days since 2023); claims can revert while the contract is underfunded (1,167 ETH vs 1,300 ETH owed) | too small: $0.12M a day against a 30-day lock worth ~22bp of staking carry |
| 7 | cbETH | $68,026 | $2,360,476 | Coinbase unwrap | permissioned (Coinbase account) | - | permissioned |
| 8 | sfrxETH | $50,706 | $330,510 | ERC-4626 to frxETH, then the frxETH queue | permissionless | as frxETH | too small ($0.05M a day, through a three-coin pool) |
| 9 | mETH | $27,970 | $1,694,288 | Mantle Staking unstakeRequest -> claimUnstakeRequest; ETH fixed at request; no fee | permissionless | ~12-20h (3,600-block finality + oracle + funding) | too small on Ethereum ($0.03M a day; mETH liquidity lives on Mantle) |
| 10 | pufETH | $25,614 | $5,511,061 | PufferVault ERC-4626 redeem/withdraw, instant, 1% exit fee, capped by vault ETH (287 ETH) | permissionless | instant | too small ($0.03M a day); the 1% instant exit caps the discount |
| 11 | ETHx | $4,430 | $626,632 | Stader UserWithdrawalManager requestWithdraw -> finalize -> claim | permissionless | ~7-10 days (not verified) | dead ($4k a day) |
| 12 | rswETH | $3,618 | $118,173 | Swell restaking withdrawal | permissionless | - | dead ($4k a day) |
| 13 | cmETH | $678 | $37,859 | Mantle restaking wrapper | - | - | dead (<$1k a day) |
| 14 | ankrETH | $0 | $968,571 | Ankr unstake | - | - | dead ($0 a day) |

