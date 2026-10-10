# The redemption surface, tables

Window 2026-03-13T20:23:59Z to 2026-10-09T20:06:47Z (blocks 24650913 to 26157137, 210 days); parameters chosen on days before 2026-06-26 and scored after. ETH staking benchmark 2.37% (Lido, measured over the window); Sky savings rate 3.62% over the window, 3.80% on the last day. 462 variants tried in all.

## Ranking by out-of-sample value at capacity

| asset | unit | hourly VW discount p50 / p90 / p99 (bp) | sell p50 / p90 / p99 (bp) | wait (median days) | capacity | OOS $/yr at capacity | 95% CI | in-sample $/yr | binding constraint |
|---|---|---|---|---:|---:|---:|---|---:|---|
| USDe (Ethena) — permissioned redemption | USD | 0.9 / 7.5 / 15.6 | 2.0 / 8.6 / 18.6 | 0.00 | $1,000,000 | $55,548 | $6,130 to $130,612 | $873,641 | redemption is permissioned |
| weETH (ether.fi) | ETH | 2.2 / 22.9 / 70.4 | 7.1 / 76.0 / 93.1 | 1.00 | $30,000,000 | $54,206 | $0 to $152,605 | $943,215 | capital locked in the queue (still growing at the largest size tested) |
| stETH / wstETH (Lido) | ETH | 1.2 / 7.1 / 40.5 | 6.0 / 53.6 / 78.3 | 1.00 | $30,000,000 | $53,359 | $0 to $160,078 | $499,809 | capital locked in the queue (still growing at the largest size tested) |
| rsETH (Kelp) | ETH | 27.9 / 42.0 / 66.4 | 28.7 / 41.4 / 66.3 | 12.04 | $3,000,000 | $41,838 | $24,190 to $61,146 | $24,623 | offered volume below NAV (more capital adds little) |
| syrupUSDC (Maple) | USD | 0.4 / 13.9 / 17.3 | 11.8 / 16.6 / 20.8 | 0.00 | $3,000,000 | $7,988 | $1,129 to $16,712 | $23,182 | offered volume below NAV (more capital adds little) |
| sUSDe (Ethena) — the 2026-09-10 study, extended | USD | -0.6 / 5.4 / 15.1 | 1.4 / 10.6 / 25.4 | 1.00 | $1,000,000 | $7,862 | $2,938 to $14,002 | $29,266 | exit or redemption capacity per day |
| syrupUSDT (Maple) | USD | 0.5 / 16.6 / 21.5 | 17.5 / 21.5 / 27.8 | 0.00 | $1,000,000 | $6,119 | $0 to $18,209 | $842 | offered volume below NAV (more capital adds little) |
| ezETH (Renzo) | ETH | 20.0 / 26.0 / 34.6 | 21.5 / 28.7 / 36.9 | 14.00 | $1,000,000 | $5,621 | $2,668 to $9,251 | $17,747 | offered volume below NAV (more capital adds little) |
| rETH (Rocket Pool) | ETH | 1.8 / 31.0 / 49.5 | 17.0 / 45.9 / 87.4 | 0.00 | $100,000 | $87 | $0 to $247 | $19,120 | exit or redemption capacity per day |
| sfrxUSD (Frax) — instant control | USD | -0.2 / 1.2 / 1.8 | 0.7 / 1.2 / 1.8 | 0.00 | - | $0 | - to - | - | nothing qualifies out of sample |
| sUSDS (Sky) — instant control | USD | -2.1 / 2.1 / 6.2 | -0.9 / 2.9 / 6.5 | 0.00 | - | $0 | - to - | - | nothing qualifies out of sample |

## USDe (Ethena) — permissioned redemption

Redemption: EthenaMinting.redeem: same block, approved redeemers only. Fee 0.0bp; earns nothing while queued; permissioned.
Wait: {"kind": "instant", "median_days": 0.0}.
Swaps priced 56029 (30402 sells), $3,644,957,062 traded, $1,810,180,724 sold; 145 prints beyond the bound excluded ($2,016,097). NAV max daily step: par.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-usde-usdc | 5522 | $71,882,119 | $35,835,157 | 4.0 | 3.2 | 1.00 |
| curve-usdt-usde | 16841 | $425,304,571 | $212,304,256 | 0.3 | 0.2 | 0.30 |
| fluid-usde-usdt | 19761 | $2,468,978,242 | $1,223,704,471 | 3.9 | 3.1 | 1.00 |
| v3-usde-usdc-1bp | 13905 | $678,792,130 | $338,336,841 | 2.1 | 3.1 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=0 | $268,379 | $36,261 | $1,413 to $91,932 | $2,837 | 1 | 4000 (504) | 4.1 | $511,518,781 | $0 |
| $300,000 | h=0 | $563,300 | $49,949 | $4,376 to $118,775 | $7,229 | 1 | 4193 (526) | 4.0 | $269,068,047 | $0 |
| $1,000,000 | h=0 | $873,641 | $55,548 | $6,130 to $130,612 | $10,230 | 1 | 4205 (530) | 4.0 | $61,326,536 | $0 |
| $3,000,000 | h=0 | $972,323 | $55,548 | $6,130 to $130,612 | $10,230 | 1 | 4205 (530) | 4.0 | $3,041,087 | $0 |
| $10,000,000 | h=0 | $978,939 | $55,548 | $6,130 to $130,612 | $10,230 | 1 | 4205 (530) | 4.0 | $0 | $0 |
| $30,000,000 | h=0 | $978,939 | $55,548 | $6,130 to $130,612 | $10,230 | 1 | 4205 (530) | 4.0 | $0 | $0 |

Value by month at capacity ($1,000,000, h=0): 2026-03 $7,800, 2026-04 $196,177, 2026-05 $35,422, 2026-06 $20,921, 2026-07 $4,571, 2026-08 $460, 2026-09 $711, 2026-10 $1,238.

## weETH (ether.fi)

Redemption: ether.fi WithdrawRequestNFT queue (unwrap weETH, request, wait for finalization, claim). Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"finalized": 209, "kind": "pointer", "max_days": 16.046, "median_days": 1.005, "p90_days": 5.019, "pending_at_end": 1, "pending_lower_bound_max_days": 0.0, "requests": 210}.
Swaps priced 25126 (9625 sells), $1,842,009,691 traded, $912,854,528 sold; 1029 prints beyond the bound excluded ($33,460,576). NAV max daily step: weeth_nav 1.1bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-weeth-weth | 9956 | $634,648,880 | $318,519,699 | 5.0 | 3.7 | 0.50 |
| fluid-weeth-eth | 2526 | $778,511,641 | $387,193,640 | 6.3 | 6.1 | 0.83 |
| v3-weeth-weth-1bp | 12644 | $428,849,169 | $207,141,189 | 30.3 | 29.7 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=5 | $3,783 | $203 | $0 to $610 | $237 | 5 | 25 (1) | 5.9 | $319,435,699 | $0 |
| $300,000 | h=5 | $12,050 | $680 | $0 to $2,040 | $793 | 5 | 46 (1) | 8.7 | $316,118,726 | $0 |
| $1,000,000 | h=5 | $41,490 | $2,348 | $0 to $7,043 | $2,739 | 5 | 113 (1) | 17.4 | $305,155,585 | $0 |
| $3,000,000 | h=3 | $111,970 | $11,829 | $0 to $30,171 | $9,556 | 4 | 330 (19) | 5.9 | $401,079,746 | $0 |
| $10,000,000 | h=2 | $358,185 | $41,077 | $2,882 to $103,509 | $34,615 | 3 | 788 (42) | 4.9 | $323,474,748 | $0 |
| $30,000,000 | h=3 | $943,215 | $54,206 | $0 to $152,605 | $54,364 | 4 | 1644 (29) | 15.8 | $133,766,723 | $0 |

Value by month at capacity ($30,000,000, h=3): 2026-03 $5,162, 2026-04 $140,840, 2026-05 $60,586, 2026-06 $64,747, 2026-07 $2,189, 2026-08 $0, 2026-09 $11,566, 2026-10 $1,839.

## stETH / wstETH (Lido)

Redemption: Lido WithdrawalQueueERC721: request, wait for finalization, claim ETH. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"finalized": 20546, "kind": "lido", "max_days": 15.027, "median_days": 0.995, "p90_days": 9.057, "pending_at_end": 54, "pending_lower_bound_max_days": 0.431, "requests": 20600}.
Swaps priced 68702 (40541 sells), $4,501,083,488 traded, $2,178,644,885 sold; 108 prints beyond the bound excluded ($210,159,619). NAV max daily step: wsteth_nav 1.2bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-steth-eth | 18976 | $1,543,156,492 | $774,116,221 | 23.5 | 41.0 | 1.00 |
| curve-steth-ng | 15432 | $695,510,527 | $347,251,648 | 14.1 | 23.5 | 0.80 |
| fluid-wsteth-eth | 7578 | $1,232,679,900 | $606,185,196 | 3.2 | 2.1 | 1.00 |
| v3-wsteth-weth-1bp | 26716 | $1,029,736,568 | $451,091,820 | 11.1 | 2.9 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=20 | $2,179 | $0 | $0 to $0 | $0 | 7 | 8 (0) | 22.9 | $367,429,695 | $0 |
| $300,000 | h=20 | $6,609 | $0 | $0 to $0 | $0 | 7 | 21 (0) | 23.0 | $366,904,707 | $0 |
| $1,000,000 | h=20 | $20,030 | $0 | $0 to $0 | $0 | 7 | 61 (0) | 32.5 | $365,346,761 | $0 |
| $3,000,000 | h=20 | $58,310 | $0 | $0 to $0 | $0 | 7 | 88 (0) | 22.8 | $361,335,858 | $0 |
| $10,000,000 | h=20 | $227,751 | $0 | $0 to $0 | $0 | 7 | 192 (0) | 24.9 | $346,066,552 | $0 |
| $30,000,000 | h=5 | $499,809 | $53,359 | $0 to $160,078 | $62,252 | 3 | 825 (3) | 18.8 | $547,309,055 | $0 |

Value by month at capacity ($30,000,000, h=5): 2026-03 $0, 2026-04 $117,879, 2026-05 $21,244, 2026-06 $4,658, 2026-07 $0, 2026-08 $0, 2026-09 $15,350, 2026-10 $0.

## rsETH (Kelp)

Redemption: Kelp LRTWithdrawalManager: queue rsETH for ETH, wait for the unlock, complete. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"finalized": 135, "kind": "pointer", "max_days": 30.092, "median_days": 12.041, "p90_days": 23.089, "pending_at_end": 5, "pending_lower_bound_max_days": 5.218, "requests": 140}.
Swaps priced 842 (617 sells), $38,524,822 traded, $20,688,513 sold; 5 prints beyond the bound excluded ($13,064). NAV max daily step: rseth_nav 19.4bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-rseth-eth | 522 | $36,620,826 | $19,784,129 | 18.4 | 27.9 | 1.00 |
| v4-rseth-eth-5bp | 320 | $1,903,996 | $904,384 | 34.7 | 36.6 | - |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=5 | $1,364 | $2,647 | $1,231 to $4,119 | $2,664 | 7 | 42 (31) | 19.2 | $12,112,629 | $0 |
| $300,000 | h=5 | $3,606 | $9,492 | $4,497 to $15,039 | $9,398 | 6 | 67 (49) | 18.6 | $10,229,439 | $0 |
| $1,000,000 | h=0 | $9,115 | $27,830 | $12,031 to $44,994 | $25,902 | 1 | 112 (94) | 19.9 | $8,948,479 | $0 |
| $3,000,000 | h=0 | $24,623 | $41,838 | $24,190 to $61,146 | $40,915 | 2 | 205 (171) | 18.3 | $1,789,239 | $0 |
| $10,000,000 | h=0 | $31,533 | $43,488 | $25,078 to $64,574 | $42,840 | 1 | 220 (174) | 18.5 | $0 | $0 |
| $30,000,000 | h=0 | $31,533 | $43,488 | $25,078 to $64,574 | $42,840 | 1 | 220 (174) | 18.5 | $0 | $0 |

Value by month at capacity ($3,000,000, h=0): 2026-03 $576, 2026-04 $1,064, 2026-05 $0, 2026-06 $7,043, 2026-07 $4,417, 2026-08 $3,276, 2026-09 $2,145, 2026-10 $597.

## syrupUSDC (Maple)

Redemption: Maple WithdrawalManager queue: requestRedeem, processed by the pool delegate. Fee 0.0bp; keeps earning while queued; open to anyone.
Wait: {"finalized": 7042, "kind": "maple", "max_days": 1.564, "median_days": 0.002, "p90_days": 0.006, "pending_at_end": 140, "pending_lower_bound_max_days": 207.536, "requests": 7182}.
Swaps priced 2399 (702 sells), $177,016,747 traded, $39,058,148 sold; 0 prints beyond the bound excluded ($0). NAV max daily step: syrupusdc_nav 1.8bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-syrupusdc-usdc | 1041 | $47,216,754 | $17,590,733 | 6.8 | 10.8 | 5.00 |
| v4-syrupusdc-usdc-8bp | 1358 | $129,799,993 | $21,467,414 | 4.1 | 16.4 | - |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=0 | $2,591 | $1,422 | $448 to $2,648 | $1,659 | 1 | 47 (10) | 4.3 | $23,036,910 | $0 |
| $300,000 | h=2 | $6,350 | $3,695 | $991 to $7,138 | $4,311 | 1 | 41 (11) | 4.6 | $15,705,178 | $0 |
| $1,000,000 | h=2 | $13,142 | $6,182 | $1,111 to $12,694 | $7,212 | 1 | 44 (14) | 4.6 | $11,376,677 | $0 |
| $3,000,000 | h=0 | $23,182 | $7,988 | $1,129 to $16,712 | $9,320 | 1 | 63 (18) | 4.0 | $6,260,561 | $0 |
| $10,000,000 | h=0 | $39,273 | $7,988 | $1,129 to $16,712 | $9,320 | 1 | 64 (18) | 4.0 | $0 | $0 |
| $30,000,000 | h=0 | $39,273 | $7,988 | $1,129 to $16,712 | $9,320 | 1 | 64 (18) | 4.0 | $0 | $0 |

Value by month at capacity ($3,000,000, h=0): 2026-03 $1,273, 2026-04 $5,211, 2026-05 $177, 2026-06 $8, 2026-07 $0, 2026-08 $245, 2026-09 $2,053, 2026-10 $0.

## sUSDe (Ethena) — the 2026-09-10 study, extended

Redemption: cooldownShares, wait cooldownDuration (1 day), unstake to USDe, sell USDe on Curve. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"kind": "constant", "median_days": 1.0}.
Swaps priced 31924 (14082 sells), $1,604,373,378 traded, $785,547,477 sold; 15 prints beyond the bound excluded ($549,882). NAV max daily step: susde_nav 1.5bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-sdai-susde | 3236 | $245,311,463 | $123,769,071 | 4.8 | 4.3 | 2.00 |
| curve-susde-frxusd | 1429 | $22,319,373 | $11,299,963 | 0.6 | 2.3 | 1.00 |
| v4-susde-usdt | 27259 | $1,336,742,542 | $650,478,443 | 3.2 | 0.9 | - |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=3 | $3,371 | $1,265 | $502 to $2,207 | $1,276 | 2 | 77 (19) | 4.4 | $257,068,341 | $0 |
| $300,000 | h=2 | $11,344 | $3,546 | $1,348 to $6,463 | $3,562 | 3 | 176 (42) | 3.4 | $295,666,411 | $0 |
| $1,000,000 | h=2 | $29,266 | $7,862 | $2,938 to $14,002 | $8,083 | 2 | 315 (84) | 3.5 | $74,232,750 | $205,091,711 |
| $3,000,000 | h=2 | $30,704 | $8,451 | $3,051 to $15,085 | $8,770 | 2 | 309 (86) | 3.6 | $0 | $279,079,151 |
| $10,000,000 | h=2 | $30,704 | $8,451 | $3,051 to $15,085 | $8,770 | 2 | 309 (86) | 3.6 | $0 | $279,079,151 |
| $30,000,000 | h=2 | $30,704 | $8,451 | $3,051 to $15,085 | $8,770 | 2 | 309 (86) | 3.6 | $0 | $279,079,151 |

Value by month at capacity ($1,000,000, h=2): 2026-03 $1,405, 2026-04 $5,472, 2026-05 $947, 2026-06 $595, 2026-07 $268, 2026-08 $255, 2026-09 $1,249, 2026-10 $488.

## syrupUSDT (Maple)

Redemption: Maple WithdrawalManager queue. Fee 0.0bp; keeps earning while queued; open to anyone.
Wait: {"finalized": 3058, "kind": "maple", "max_days": 4.389, "median_days": 0.003, "p90_days": 0.524, "pending_at_end": 142, "pending_lower_bound_max_days": 205.504, "requests": 3200}.
Swaps priced 733 (151 sells), $61,923,404 traded, $7,730,244 sold; 0 prints beyond the bound excluded ($0). NAV max daily step: syrupusdt_nav 2.5bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| v4-syrupusdt-usdt-8bp | 733 | $61,923,404 | $7,730,244 | 3.5 | 17.5 | - |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=5 | $221 | $722 | $0 to $2,165 | $842 | 5 | 5 (3) | 6.6 | $1,448,709 | $0 |
| $300,000 | h=3 | $293 | $2,930 | $0 to $8,729 | $3,419 | 4 | 11 (7) | 4.7 | $856,405 | $0 |
| $1,000,000 | h=0 | $842 | $6,119 | $0 to $18,209 | $7,139 | 1 | 27 (16) | 2.9 | $0 | $0 |
| $3,000,000 | h=0 | $842 | $6,119 | $0 to $18,209 | $7,139 | 1 | 27 (16) | 2.9 | $0 | $0 |
| $10,000,000 | h=0 | $842 | $6,119 | $0 to $18,209 | $7,139 | 1 | 27 (16) | 2.9 | $0 | $0 |
| $30,000,000 | h=0 | $842 | $6,119 | $0 to $18,209 | $7,139 | 1 | 27 (16) | 2.9 | $0 | $0 |

Value by month at capacity ($1,000,000, h=0): 2026-03 $8, 2026-04 $161, 2026-05 $69, 2026-06 $4, 2026-07 $0, 2026-08 $13, 2026-09 $1,748, 2026-10 $0.

## ezETH (Renzo)

Redemption: Renzo WithdrawQueue: request, wait coolDownPeriod, claim. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"kind": "parameter", "median_days": 14.0, "samples": 8, "values_days": [7.0, 14.0]}.
Swaps priced 644 (459 sells), $24,503,840 traded, $13,385,469 sold; 0 prints beyond the bound excluded ($0). NAV max daily step: ezeth_nav 4.8bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| fluid-ezeth-eth | 644 | $24,503,840 | $13,385,469 | 19.6 | 21.5 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=0 | $2,394 | $1,513 | $713 to $2,508 | $1,390 | 2 | 53 (27) | 12.0 | $10,849,535 | $0 |
| $300,000 | h=0 | $7,792 | $4,548 | $1,986 to $7,523 | $4,096 | 1 | 93 (48) | 12.2 | $8,827,831 | $0 |
| $1,000,000 | h=0 | $17,747 | $5,621 | $2,668 to $9,251 | $5,295 | 1 | 134 (71) | 11.9 | $6,152,629 | $0 |
| $3,000,000 | h=0 | $47,420 | $5,621 | $2,668 to $9,251 | $5,295 | 1 | 148 (71) | 12.1 | $1,135,280 | $0 |
| $10,000,000 | h=0 | $55,732 | $5,621 | $2,668 to $9,251 | $5,295 | 1 | 150 (71) | 12.1 | $0 | $0 |
| $30,000,000 | h=0 | $55,732 | $5,621 | $2,668 to $9,251 | $5,295 | 1 | 150 (71) | 12.1 | $0 | $0 |

Value by month at capacity ($1,000,000, h=0): 2026-03 $89, 2026-04 $2,477, 2026-05 $2,019, 2026-06 $801, 2026-07 $500, 2026-08 $270, 2026-09 $488, 2026-10 $77.

## rETH (Rocket Pool)

Redemption: rETH.burn(): instant, only up to getTotalCollateral() (rETH balance plus deposit-pool excess). Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"kind": "instant", "median_days": 0.0}.
Swaps priced 15124 (6824 sells), $221,621,566 traded, $111,692,155 sold; 567 prints beyond the bound excluded ($2,854,526). NAV max daily step: reth_nav 1.2bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-reth-weth | 2020 | $10,731,880 | $5,415,894 | 25.2 | 26.6 | 1.00 |
| v3-reth-weth-1bp | 9287 | $156,580,176 | $78,835,003 | 17.7 | 15.9 | 1.00 |
| v4-reth-eth-1bp | 3817 | $54,309,510 | $27,441,258 | 15.7 | 13.2 | - |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=3 | $19,120 | $87 | $0 to $247 | $86 | 4 | 151 (2) | 15.3 | $2,439,191 | $61,195,611 |
| $300,000 | h=5 | $21,375 | $13 | $0 to $39 | $0 | 5 | 136 (1) | 15.3 | $286,360 | $59,111,948 |
| $1,000,000 | h=5 | $21,876 | $13 | $0 to $39 | $0 | 5 | 135 (1) | 15.3 | $0 | $59,211,733 |
| $3,000,000 | h=5 | $21,876 | $13 | $0 to $39 | $0 | 5 | 135 (1) | 15.3 | $0 | $59,211,733 |
| $10,000,000 | h=5 | $21,876 | $13 | $0 to $39 | $0 | 5 | 135 (1) | 15.3 | $0 | $59,211,733 |
| $30,000,000 | h=5 | $21,876 | $13 | $0 to $39 | $0 | 5 | 135 (1) | 15.3 | $0 | $59,211,733 |

Value by month at capacity ($100,000, h=3): 2026-03 $0, 2026-04 $3,545, 2026-05 $79, 2026-06 $1,877, 2026-07 $25, 2026-08 $0, 2026-09 $0, 2026-10 $0.

## sfrxUSD (Frax) — instant control

Redemption: ERC-4626 redeem into frxUSD, same block. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"kind": "instant", "median_days": 0.0}.
Swaps priced 1794 (994 sells), $57,294,389 traded, $28,793,461 sold; 0 prints beyond the bound excluded ($0). NAV max daily step: sfrxusd_nav 1.4bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-sfrxusd-frxusd | 1794 | $57,294,389 | $28,793,461 | -0.4 | 0.7 | 1.00 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=0 | $0 | $0 | $0 to $0 | $0 | 1 | 0 (0) | - | $0 | $0 |
| $300,000 | h=0 | $0 | $0 | $0 to $0 | $0 | 1 | 0 (0) | - | $0 | $0 |
| $1,000,000 | h=0 | $0 | $0 | $0 to $0 | $0 | 1 | 0 (0) | - | $0 | $0 |
| $3,000,000 | h=0 | $0 | $0 | $0 to $0 | $0 | 1 | 0 (0) | - | $0 | $0 |
| $10,000,000 | h=0 | $0 | $0 | $0 to $0 | $0 | 1 | 0 (0) | - | $0 | $0 |
| $30,000,000 | h=0 | $0 | $0 | $0 to $0 | $0 | 1 | 0 (0) | - | $0 | $0 |

## sUSDS (Sky) — instant control

Redemption: ERC-4626 redeem into USDS, same block. Fee 0.0bp; earns nothing while queued; open to anyone.
Wait: {"kind": "instant", "median_days": 0.0}.
Swaps priced 38872 (19694 sells), $3,963,616,566 traded, $1,960,484,142 sold; 817 prints beyond the bound excluded ($12,735,245). NAV max daily step: susds_nav 1.0bp.

| pool | swaps | volume | sell volume | VW discount bp | median sell bp | fee bp |
|---|---:|---:|---:|---:|---:|---:|
| curve-dola-susds | 2261 | $29,198,278 | $14,285,363 | -46.7 | -51.6 | 1.00 |
| curve-frxusd-susds | 5823 | $139,992,086 | $69,160,106 | -0.7 | -0.3 | 1.00 |
| curve-susds-usdt | 30788 | $3,794,426,202 | $1,877,038,673 | 0.1 | -1.0 | 0.10 |

| bid size | hurdle chosen in sample | in-sample $/yr | out-of-sample $/yr | 95% CI | trailing 90 days $/yr | OOS rank of choice | fills (OOS) | median edge bp | missed for capital | missed for exit cap |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| $100,000 | h=0 | $3,223 | $0 | $0 to $0 | $0 | 1 | 111 (0) | 1.9 | $113,619,588 | $0 |
| $300,000 | h=0 | $11,525 | $0 | $0 to $0 | $0 | 1 | 220 (0) | 1.0 | $81,792,577 | $0 |
| $1,000,000 | h=0 | $32,073 | $0 | $0 to $0 | $0 | 1 | 240 (0) | 0.9 | $12,648,144 | $0 |
| $3,000,000 | h=0 | $35,801 | $0 | $0 to $0 | $0 | 1 | 242 (0) | 0.9 | $739,560 | $0 |
| $10,000,000 | h=0 | $35,941 | $0 | $0 to $0 | $0 | 1 | 242 (0) | 0.9 | $0 | $0 |
| $30,000,000 | h=0 | $35,941 | $0 | $0 to $0 | $0 | 1 | 242 (0) | 0.9 | $0 | $0 |

## Not read

- USDe v4 0.003%: about $13M a day of swaps, too many logs for this pass; the other four USDe venues are read
- cbETH: Curve and Uniswap v3 pools trade ~$2.4k a day together, and unwrapping is a Coinbase account action
- eETH: no pool with volume; it trades as weETH
- pufETH: pools trade ~$16k a day; the vault exit fee read 0 but the daily withdrawal limit was not read
- sDAI: its only live pool is against sUSDe; sUSDS is the Sky control
