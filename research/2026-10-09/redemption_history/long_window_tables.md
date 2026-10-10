# The redemption surface, tables

Window 2024-09-26T12:53:11Z to 2026-10-09T20:06:47Z (blocks 20834913 to 26157137, 744 days); parameters chosen on days before 2025-10-03 and scored after. ETH staking benchmark 2.70% (Lido, measured over the window); Sky savings rate 5.29% over the window, 3.80% on the last day. 126 variants tried in all.

## Ranking by out-of-sample value at capacity

| asset | unit | hourly VW discount p50 / p90 / p99 (bp) | sell p50 / p90 / p99 (bp) | wait (median days) | capacity | OOS $/yr at capacity | 95% CI | in-sample $/yr | binding constraint |
|---|---|---|---|---:|---:|---:|---|---:|---|
| weETH (ether.fi) | ETH | 3.3 / 18.8 / 38.7 | 5.0 / 27.9 / 81.3 | 2.01 | $30,000,000 | $411,361 | $270,603 to $556,018 | $912,606 | capital locked in the queue (still growing at the largest size tested) |
| stETH / wstETH (Lido) | ETH | 3.1 / 14.4 / 29.7 | 7.0 / 26.2 / 62.3 | 1.98 | $30,000,000 | $401,697 | $220,429 to $621,619 | $906,683 | capital locked in the queue (still growing at the largest size tested) |
| rsETH (Kelp) | ETH | 14.3 / 30.1 / 56.6 | 18.5 / 30.8 / 59.5 | 5.03 | $10,000,000 | $50,894 | $29,952 to $74,100 | $60,604 | offered volume below NAV (more capital adds little) |

## weETH (ether.fi)

Redemption: ether.fi WithdrawRequestNFT queue (unwrap weETH, request, wait for finalization, claim). Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"finalized": 739, "kind": "pointer", "max_days": 18.095, "median_days": 2.008, "p90_days": 6.04, "pending_at_end": 1, "pending_lower_bound_max_days": 0.0, "requests": 740}.
Swaps priced 109897 (63962 sells), $15,341,663,729 traded, $7,530,864,826 sold; 1090 prints beyond the bound excluded ($42,861,265). NAV max daily step: weeth_nav 1.6bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-weeth-weth | 43640 | $3,505,040,603 | $1,754,788,453 | 6.1 | 4.2 | 0.50 |
| fluid-weeth-eth | 16595 | $5,839,902,302 | $2,908,447,545 | 4.8 | 4.8 | 0.83 |
| v3-weeth-weth-1bp | 49662 | $5,996,720,824 | $2,867,628,828 | 11.4 | 6.1 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=3 | $3,968 | $1,562 | $1,000 to $2,222 | $406 | 2 | 261 (89) | 4.1 | $2,874,192,993 | $0 |
| $300,000 | h=2 | $13,491 | $5,408 | $3,596 to $7,501 | $1,701 | 3 | 632 (196) | 3.5 | $3,721,332,399 | $0 |
| $1,000,000 | h=2 | $44,024 | $19,551 | $12,888 to $27,326 | $5,215 | 2 | 1308 (377) | 4.0 | $3,606,944,460 | $0 |
| $3,000,000 | h=1 | $123,696 | $55,129 | $35,779 to $76,811 | $14,412 | 4 | 3241 (860) | 3.3 | $4,089,888,424 | $0 |
| $10,000,000 | h=0 | $378,735 | $169,784 | $110,848 to $235,017 | $43,315 | 5 | 6931 (1961) | 3.3 | $3,503,956,329 | $0 |
| $30,000,000 | h=0 | $912,606 | $411,361 | $270,603 to $556,018 | $68,198 | 5 | 12031 (3840) | 4.3 | $1,842,688,528 | $0 |

Value by month at capacity ($30,000,000, h=0): 2024-09 $14,582, 2024-10 $35,598, 2024-11 $51,124, 2024-12 $98,240, 2025-01 $76,959, 2025-02 $112,758, 2025-03 $39,801, 2025-04 $21,554, 2025-05 $20,574, 2025-06 $446, 2025-07 $127,206, 2025-08 $177,073, 2025-09 $152,163, 2025-10 $24,497, 2025-11 $41,784, 2025-12 $914, 2026-01 $18,496, 2026-02 $54,106, 2026-03 $23,891, 2026-04 $102,629, 2026-05 $61,547, 2026-06 $73,160, 2026-07 $3,560, 2026-08 $1,167, 2026-09 $12,586, 2026-10 $2,944.

## stETH / wstETH (Lido)

Redemption: Lido WithdrawalQueueERC721: request, wait for finalization, claim ETH. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"finalized": 85125, "kind": "lido", "max_days": 16.933, "median_days": 1.978, "p90_days": 10.026, "pending_at_end": 54, "pending_lower_bound_max_days": 0.431, "requests": 85179}.
Swaps priced 356222 (222898 sells), $40,128,331,584 traded, $19,565,594,408 sold; 471 prints beyond the bound excluded ($519,532,577). NAV max daily step: wsteth_nav 3.2bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-steth-eth | 73667 | $13,109,093,209 | $6,553,122,830 | 14.2 | 10.7 | 1.00 |
| curve-steth-ng | 38772 | $2,968,532,844 | $1,479,533,261 | 14.2 | 12.5 | 0.80 |
| fluid-wsteth-eth | 76423 | $11,798,477,362 | $5,863,017,223 | 4.4 | 2.6 | 1.00 |
| v3-wsteth-weth-1bp | 167360 | $12,252,228,169 | $5,669,921,093 | 10.0 | 7.6 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=5 | $2,762 | $1,045 | $492 to $1,719 | $194 | 4 | 120 (46) | 5.8 | $6,876,810,488 | $0 |
| $300,000 | h=5 | $8,996 | $3,664 | $1,699 to $5,931 | $664 | 5 | 225 (82) | 6.2 | $6,863,501,089 | $0 |
| $1,000,000 | h=5 | $31,368 | $12,616 | $5,856 to $20,688 | $2,310 | 5 | 576 (233) | 5.9 | $6,810,512,737 | $0 |
| $3,000,000 | h=3 | $98,597 | $43,689 | $23,953 to $67,094 | $7,016 | 2 | 2074 (654) | 4.4 | $9,224,878,123 | $0 |
| $10,000,000 | h=1 | $323,481 | $129,884 | $75,037 to $194,241 | $19,548 | 3 | 7002 (2629) | 4.4 | $11,379,046,405 | $0 |
| $30,000,000 | h=1 | $906,683 | $401,697 | $220,429 to $621,619 | $68,620 | 3 | 14306 (5144) | 4.3 | $9,400,137,914 | $0 |

Value by month at capacity ($30,000,000, h=1): 2024-09 $9,264, 2024-10 $29,978, 2024-11 $54,471, 2024-12 $167,722, 2025-01 $153,051, 2025-02 $150,709, 2025-03 $42,104, 2025-04 $94,787, 2025-05 $15,308, 2025-06 $1,602, 2025-07 $77,527, 2025-08 $93,502, 2025-09 $30,353, 2025-10 $43,617, 2025-11 $90,868, 2025-12 $3,969, 2026-01 $13,995, 2026-02 $95,877, 2026-03 $20,701, 2026-04 $80,808, 2026-05 $23,553, 2026-06 $22,561, 2026-07 $229, 2026-08 $508, 2026-09 $15,173, 2026-10 $1,239.

## rsETH (Kelp)

Redemption: Kelp LRTWithdrawalManager: queue rsETH for ETH, wait for the unlock, complete. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"finalized": 638, "kind": "pointer", "max_days": 30.092, "median_days": 5.032, "p90_days": 17.072, "pending_at_end": 5, "pending_lower_bound_max_days": 5.218, "requests": 643}.
Swaps priced 2783 (1803 sells), $233,522,511 traded, $115,450,108 sold; 5 prints beyond the bound excluded ($13,091). NAV max daily step: rseth_nav 19.4bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-rseth-eth | 2462 | $231,621,388 | $114,546,811 | 13.8 | 17.7 | 1.00 |
| v4-rseth-eth-5bp | 321 | $1,901,123 | $903,297 | 34.7 | 36.6 | - |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=5 | $2,045 | $2,547 | $1,544 to $3,664 | $2,573 | 6 | 132 (90) | 11.7 | $80,330,013 | $0 |
| $300,000 | h=0 | $5,798 | $7,612 | $4,659 to $10,762 | $8,884 | 4 | 255 (156) | 11.3 | $84,255,564 | $0 |
| $1,000,000 | h=0 | $16,706 | $22,803 | $14,069 to $32,537 | $24,200 | 3 | 457 (265) | 11.9 | $58,987,860 | $0 |
| $3,000,000 | h=2 | $38,624 | $44,120 | $26,646 to $63,056 | $38,932 | 3 | 690 (409) | 13.2 | $20,395,168 | $0 |
| $10,000,000 | h=0 | $60,604 | $50,894 | $29,952 to $74,100 | $40,336 | 1 | 813 (433) | 13.5 | $0 | $0 |
| $30,000,000 | h=0 | $60,604 | $50,894 | $29,952 to $74,100 | $40,336 | 1 | 813 (433) | 13.5 | $0 | $0 |

Value by month at capacity ($10,000,000, h=0): 2024-09 $0, 2024-10 $0, 2024-11 $0, 2024-12 $0, 2025-01 $34, 2025-02 $704, 2025-03 $228, 2025-04 $236, 2025-05 $2,001, 2025-06 $506, 2025-07 $12,356, 2025-08 $14,169, 2025-09 $31,532, 2025-10 $1,149, 2025-11 $14,123, 2025-12 $2,774, 2026-01 $81, 2026-02 $11,627, 2026-03 $3,029, 2026-04 $482, 2026-05 $0, 2026-06 $8,382, 2026-07 $4,570, 2026-08 $3,053, 2026-09 $2,019, 2026-10 $581.

## Not read

- USDe v4 0.003%: about $13M a day of swaps, too many logs for this pass; the other four USDe venues are read
- cbETH: Curve and Uniswap v3 pools trade ~$2.4k a day together, and unwrapping is a Coinbase account action
- eETH: no pool with volume; it trades as weETH
- pufETH: pools trade ~$16k a day; the vault exit fee read 0 but the daily withdrawal limit was not read
- sDAI: its only live pool is against sUSDe; sUSDS is the Sky control
