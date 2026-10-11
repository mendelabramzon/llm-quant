# Queue bids on one capital pool, with kHYPE — tables

Common window of the five assets 2025-07-15T00:00:00Z → 2026-10-09T20:06:47Z (452 days), split 2026-02-26: the hurdle is chosen on the first half and tested once on the second. all4 and eth3 are rerun on the same window, so every kHYPE row compares like for like. kHYPE fills pay HyperEVM costs ($1 a fill, $1,000 minimum); the Ethereum-side assets $10 and $5,000.

## Checks

### kHYPE alone through this protocol vs queue_bids_alt (2025-07-15 → 2026-10-09, 452 days, split 2026-02-26)

| size | queue_bids_alt | queue_book | difference | hurdle | t | identical |
|---:|---:|---:|---:|---|---:|---|
| $100,000 | $1,749 | $1,749 | $0.00 | h=20 | 2.42 | yes |
| $300,000 | $5,614 | $5,614 | $0.00 | h=20 | 2.41 | yes |
| $1,000,000 | $17,139 | $17,139 | $0.00 | h=20 | 2.43 | yes |
| $3,000,000 | $45,801 | $45,801 | $0.00 | h=20 | 2.34 | yes |
| $10,000,000 | $140,043 | $140,043 | $0.00 | h=20 | 1.44 | yes |
| $30,000,000 | $373,849 | $373,849 | $0.00 | h=10 | 2.65 | yes |

The saved unbounded locked-capital series (20bp, 452 days) is reproduced to $0.00 a day at most.

### all4 on its own window (2024-09-26 → 2026-10-09, 744 days) against the stored 2026-10-10 run

| size | stored | rerun | hurdle | t | identical |
|---:|---:|---:|---|---:|---|
| $1,000,000 | $36,605 | $36,605 | h=10 | 7.92 | yes |
| $3,000,000 | $115,438 | $115,438 | h=3 | 9.66 | yes |
| $5,000,000 | $192,197 | $192,197 | h=3 | 8.75 | yes |
| $10,000,000 | $326,286 | $326,286 | h=2 | 9.31 | yes |
| $15,000,000 | $409,889 | $409,889 | h=1 | 9.31 | yes |
| $20,000,000 | $508,553 | $508,553 | h=1 | 8.81 | yes |
| $30,000,000 | $678,884 | $678,884 | h=1 | 7.98 | yes |
| $50,000,000 | $987,373 | $987,373 | h=1 | 6.75 | yes |

Regression: all4 at $15M = $409,889 (expected $409,889): pass.

## Each asset alone on the common window (out of sample, $ a year)

| asset | $1M | $3M | $5M | $10M | $15M | $20M | $30M | $50M |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| etherfi_ev | $27,585 | $61,373 | $91,751 | $168,737 | $242,484 | $308,632 | $494,674 | $700,987 |
| kelp | $18,525 | $33,025 | $37,279 | $37,279 | $37,279 | $37,279 | $37,279 | $37,279 |
| khype | $17,139 | $45,801 | $78,737 | $140,043 | $283,208 | $335,460 | $373,849 | $460,038 |
| lbtc_cb | $12,143 | $39,390 | $56,136 | $79,805 | $84,983 | $84,983 | $84,983 | $84,983 |
| lido | $10,785 | $25,314 | $41,208 | $81,180 | $127,526 | $182,393 | $267,660 | $401,561 |

Separate books at the book sizes on this window: five $43,000,000 of capital, $502,790 a year; the four Ethereum-side $33,000,000, $362,747.

## One pool (common window)

| set | pool | chosen | in sample | out of sample | t | 95% interval | by asset |
|---|---:|---|---:|---:|---:|---|---|
| all5 | $1M | h=10 | $86,822 | $46,475 | 6.46 | $33,036 – $58,791 | etherfi_ev $5,341, kelp $12,753, khype $18,644, lbtc_cb $8,468, lido $1,269 |
| all5 | $3M | h=10 | $240,744 | $138,308 | 6.05 | $97,264 – $181,040 | etherfi_ev $20,276, kelp $27,566, khype $58,819, lbtc_cb $27,994, lido $3,653 |
| all5 | $5M | h=10 | $361,025 | $201,382 | 5.97 | $140,146 – $267,229 | etherfi_ev $35,289, kelp $31,336, khype $86,564, lbtc_cb $40,959, lido $7,233 |
| all5 | $10M | h=10 | $655,757 | $330,467 | 5.60 | $217,729 – $452,212 | etherfi_ev $80,979, kelp $32,556, khype $132,537, lbtc_cb $62,421, lido $21,974 |
| all5 | $15M | h=10 | $972,836 | $460,554 | 4.55 | $270,531 – $680,515 | etherfi_ev $112,279, kelp $32,682, khype $209,041, lbtc_cb $62,547, lido $44,004 |
| all5 | $20M | h=10 | $1,273,303 | $575,433 | 3.91 | $305,848 – $894,424 | etherfi_ev $134,999, kelp $33,036, khype $278,724, lbtc_cb $62,676, lido $65,998 |
| all5 | $30M | h=10 | $1,952,906 | $757,472 | 3.68 | $377,419 – $1,212,512 | etherfi_ev $169,607, kelp $33,273, khype $346,184, lbtc_cb $82,448, lido $125,959 |
| all5 | $50M | h=10 | $2,781,649 | $964,747 | 3.18 | $424,709 – $1,659,463 | etherfi_ev $239,011, kelp $33,273, khype $359,238, lbtc_cb $82,448, lido $250,777 |
| all4 | $1M | h=10 | $58,765 | $33,293 | 5.00 | $20,780 – $45,886 | etherfi_ev $7,063, kelp $14,172, lbtc_cb $10,143, lido $1,915 |
| all4 | $3M | h=10 | $168,485 | $96,822 | 4.17 | $56,255 – $140,550 | etherfi_ev $26,380, kelp $28,178, lbtc_cb $37,248, lido $5,016 |
| all4 | $5M | h=10 | $257,660 | $145,888 | 3.94 | $81,110 – $218,588 | etherfi_ev $48,607, kelp $32,195, lbtc_cb $55,943, lido $9,143 |
| all4 | $10M | h=10 | $453,885 | $223,655 | 3.86 | $115,233 – $350,252 | etherfi_ev $82,998, kelp $33,273, lbtc_cb $76,141, lido $31,243 |
| all4 | $15M | h=10 | $617,938 | $276,873 | 3.50 | $129,315 – $456,129 | etherfi_ev $106,434, kelp $33,273, lbtc_cb $82,361, lido $54,806 |
| all4 | $20M | h=10 | $778,383 | $329,482 | 3.13 | $139,415 – $574,382 | etherfi_ev $130,677, kelp $33,273, lbtc_cb $82,448, lido $83,083 |
| all4 | $30M | h=10 | $1,089,502 | $432,312 | 2.63 | $149,315 – $832,468 | etherfi_ev $173,382, kelp $33,273, lbtc_cb $82,448, lido $143,209 |
| all4 | $50M | h=10 | $1,536,271 | $628,925 | 2.17 | $151,048 – $1,353,334 | etherfi_ev $240,446, kelp $33,273, lbtc_cb $82,448, lido $272,758 |
| eth3_khype | $1M | h=10 | $84,041 | $44,982 | 5.78 | $31,230 – $58,860 | etherfi_ev $5,875, kelp $15,708, khype $22,130, lido $1,269 |
| eth3_khype | $3M | h=10 | $224,523 | $115,845 | 5.98 | $79,784 – $152,022 | etherfi_ev $21,024, kelp $29,839, khype $61,283, lido $3,699 |
| eth3_khype | $5M | h=20 | $334,354 | $117,404 | 2.78 | $40,007 – $215,275 | etherfi_ev $48,045, kelp $8,332, khype $61,027 |
| eth3_khype | $10M | h=10 | $620,758 | $332,896 | 3.71 | $176,478 – $526,625 | etherfi_ev $81,759, kelp $32,195, khype $195,118, lido $23,824 |
| eth3_khype | $15M | h=10 | $935,766 | $445,194 | 3.40 | $216,594 – $723,596 | etherfi_ev $112,249, kelp $32,830, khype $255,156, lido $44,958 |
| eth3_khype | $20M | h=10 | $1,301,568 | $545,095 | 3.48 | $265,924 – $882,217 | etherfi_ev $135,450, kelp $33,075, khype $310,044, lido $66,526 |
| eth3_khype | $30M | h=10 | $1,970,342 | $678,539 | 3.48 | $319,507 – $1,109,170 | etherfi_ev $169,612, kelp $33,273, khype $349,638, lido $126,016 |
| eth3_khype | $50M | h=10 | $2,767,375 | $882,355 | 2.98 | $363,588 – $1,575,242 | etherfi_ev $239,012, kelp $33,273, khype $359,253, lido $250,817 |
| eth3 | $1M | h=10 | $48,249 | $27,756 | 4.41 | $16,381 – $39,879 | etherfi_ev $7,597, kelp $18,245, lido $1,915 |
| eth3 | $3M | h=10 | $134,607 | $63,129 | 3.85 | $32,958 – $96,871 | etherfi_ev $26,914, kelp $31,199, lido $5,016 |
| eth3 | $5M | h=10 | $205,814 | $91,535 | 3.24 | $41,969 – $151,685 | etherfi_ev $49,648, kelp $32,286, lido $9,600 |
| eth3 | $10M | h=10 | $378,820 | $147,480 | 2.94 | $59,659 – $263,812 | etherfi_ev $82,090, kelp $33,273, lido $32,118 |
| eth3 | $15M | h=10 | $541,768 | $195,005 | 2.64 | $66,647 – $375,383 | etherfi_ev $106,254, kelp $33,273, lido $55,478 |
| eth3 | $20M | h=10 | $708,105 | $248,619 | 2.42 | $69,661 – $495,386 | etherfi_ev $131,375, kelp $33,273, lido $83,971 |
| eth3 | $30M | h=10 | $1,017,949 | $350,305 | 2.15 | $72,721 – $750,499 | etherfi_ev $173,309, kelp $33,273, lido $143,723 |
| eth3 | $50M | h=10 | $1,447,131 | $546,530 | 1.88 | $72,721 – $1,259,963 | etherfi_ev $240,512, kelp $33,273, lido $272,745 |

## What kHYPE adds (out of sample, $ a year, same window)

| pool | all4 | all5 | all5 − all4 | kHYPE alone | increment / kHYPE alone | kHYPE share of all5 | eth3 | eth3+kHYPE | difference |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1M | $33,293 | $46,475 | $13,183 | $17,139 | 77% | 40% | $27,756 | $44,982 | $17,226 |
| $3M | $96,822 | $138,308 | $41,486 | $45,801 | 91% | 43% | $63,129 | $115,845 | $52,717 |
| $5M | $145,888 | $201,382 | $55,494 | $78,737 | 70% | 43% | $91,535 | $117,404 | $25,869 |
| $10M | $223,655 | $330,467 | $106,812 | $140,043 | 76% | 40% | $147,480 | $332,896 | $185,416 |
| $15M | $276,873 | $460,554 | $183,681 | $283,208 | 65% | 45% | $195,005 | $445,194 | $250,189 |
| $20M | $329,482 | $575,433 | $245,952 | $335,460 | 73% | 48% | $248,619 | $545,095 | $296,477 |
| $30M | $432,312 | $757,472 | $325,159 | $373,849 | 87% | 46% | $350,305 | $678,539 | $328,234 |
| $50M | $628,925 | $964,747 | $335,822 | $460,038 | 73% | 37% | $546,530 | $882,355 | $335,825 |

## Late entry (hurdle re-chosen in sample on the delayed book)

| set | pool | on time | 1 hour late | kept | 1 day late | kept |
|---|---:|---:|---:|---:|---:|---:|
| all5 | $10M | $330,467 | $290,907 | 88% | $281,704 | 85% |
| all5 | $15M | $460,554 | $428,798 | 93% | $393,629 | 85% |
| all5 | $20M | $575,433 | $541,486 | 94% | $481,200 | 84% |
| all4 | $10M | $223,655 | $193,131 | 86% | $228,631 | 102% |
| all4 | $15M | $276,873 | $257,240 | 93% | $280,829 | 101% |
| all4 | $20M | $329,482 | $332,815 | 101% | $316,175 | 96% |
| eth3_khype | $10M | $332,896 | $283,423 | 85% | $268,495 | 81% |
| eth3_khype | $15M | $445,194 | $398,458 | 90% | $357,103 | 80% |
| eth3_khype | $20M | $545,095 | $519,676 | 95% | $423,571 | 78% |
| eth3 | $10M | $147,480 | $135,312 | 92% | $158,360 | 107% |
| eth3 | $15M | $195,005 | $199,420 | 102% | $210,710 | 108% |
| eth3 | $20M | $248,619 | $274,996 | 111% | $258,545 | 104% |

## Monthly concentration of the out-of-sample value

| set | pool | hurdle | best month | best two | months with value |
|---|---:|---:|---:|---:|---:|
| all4 | $10M | 10bp | 32% | 54% | 9 |
| all4 | $15M | 10bp | 37% | 57% | 9 |
| all4 | $20M | 10bp | 41% | 63% | 9 |
| all5 | $10M | 10bp | 27% | 48% | 9 |
| all5 | $15M | 10bp | 27% | 51% | 9 |
| all5 | $20M | 10bp | 27% | 53% | 9 |
| eth3_khype | $10M | 10bp | 26% | 52% | 9 |
| eth3_khype | $15M | 10bp | 28% | 55% | 9 |
| eth3_khype | $20M | 10bp | 28% | 56% | 9 |

all5 at $15M (10bp), out-of-sample value by month and asset:

| month | total | etherfi_ev | kelp | khype | lbtc_cb | lido |
|---|---:|---:|---:|---:|---:|---:|
| 2026-02 | $1,990 | $0 | $966 | $980 | $44 | $0 |
| 2026-03 | $25,911 | $0 | $1,363 | $23,548 | $1,000 | $0 |
| 2026-04 | $68,312 | $32,441 | $0 | $7,373 | $1,252 | $27,246 |
| 2026-05 | $76,249 | $31,427 | $0 | $44,553 | $269 | $0 |
| 2026-06 | $19,401 | $5,652 | $8,113 | $5,534 | $101 | $0 |
| 2026-07 | $4,473 | $0 | $4,473 | $0 | $0 | $0 |
| 2026-08 | $2,886 | $0 | $2,886 | $0 | $0 | $0 |
| 2026-09 | $67,445 | $0 | $1,853 | $45,008 | $20,584 | $0 |
| 2026-10 | $18,498 | $0 | $581 | $2,438 | $15,479 | $0 |

Capital each asset holds inside the all5 $15M pool at the end of each day (from its fills and waits):

| asset | peak | mean | peak out of sample | mean out of sample | 90th percentile |
|---|---:|---:|---:|---:|---:|
| whole pool | $15,000,000 | $7,764,348 | $15,000,000 | $4,694,624 | $15,000,000 |
| etherfi_ev | $14,734,200 | $1,599,842 | $14,734,200 | $713,819 | $6,710,745 |
| kelp | $3,523,853 | $387,318 | $3,523,853 | $502,350 | $1,341,877 |
| khype | $15,000,000 | $3,279,112 | $15,000,000 | $2,221,876 | $12,347,118 |
| lbtc_cb | $10,917,516 | $990,908 | $8,794,375 | $512,563 | $2,898,792 |
| lido | $13,370,395 | $1,507,167 | $11,586,917 | $744,016 | $7,436,074 |

## Two balances instead of one: an Ethereum pool plus a fixed HyperEVM kHYPE sub-pool

Each part is its own book and chooses its own hurdle in sample; the split marked was the best in sample.

| total | kHYPE sub-pool | Ethereum pool | in sample | out of sample | t | 95% interval | Ethereum hurdle | kHYPE hurdle |
|---:|---:|---:|---:|---:|---:|---|---|---|
| $15,000,000 | $2,000,000 | $13,000,000 | $623,874 | $289,438 | 3.85 | $148,044 – $458,778 | h=10 | h=20 |
| $15,000,000 | $3,000,000 | $12,000,000 | $623,811 | $295,017 | 3.90 | $148,942 – $466,083 | h=10 | h=20 |
| $15,000,000 | $5,000,000 | $10,000,000 | $620,935 | $302,391 | 3.84 | $152,904 – $474,806 | h=10 | h=20 |
| $15,000,000 | $7,500,000 | $7,500,000 | $617,945 | $302,821 | 3.17 | $139,781 – $519,439 | h=10 | h=20 |
| $15,000,000 | $10,000,000 (chosen) | $5,000,000 | $628,369 | $285,931 | 2.58 | $119,467 – $541,527 | h=10 | h=20 |
| $15,000,000 | one fungible pool (all5) | | $972,836 | $460,554 | 4.55 | $270,531 – $680,515 | h=10 | h=10 |
| $20,000,000 | $2,000,000 | $18,000,000 | $785,633 | $340,952 | 3.43 | $157,860 – $569,779 | h=10 | h=20 |
| $20,000,000 | $3,000,000 | $17,000,000 | $786,504 | $345,246 | 3.51 | $163,813 – $571,758 | h=10 | h=20 |
| $20,000,000 | $5,000,000 | $15,000,000 | $784,988 | $355,610 | 3.61 | $170,184 – $573,886 | h=10 | h=20 |
| $20,000,000 | $7,500,000 | $12,500,000 | $797,765 | $369,578 | 3.26 | $165,320 – $617,959 | h=10 | h=20 |
| $20,000,000 | $10,000,000 (chosen) | $10,000,000 | $824,594 | $363,698 | 2.93 | $154,237 – $649,335 | h=10 | h=20 |
| $20,000,000 | one fungible pool (all5) | | $1,273,303 | $575,433 | 3.91 | $305,848 – $894,424 | h=10 | h=10 |

## One pool whose HyperEVM leg is reached only after the capital moves

kHYPE buys only once the venue median showed the edge the crossing time earlier, and its capital returns to the pool that long after the queue pays (carry charged over the crossing); Ethereum fills are on time. Hurdle re-chosen in sample.

| crossing | pool | chosen | in sample | out of sample | t | 95% interval | kept of fungible | over all4 | kHYPE in it |
|---|---:|---|---:|---:|---:|---|---:|---:|---:|
| 1d | $10M | h=10 | $696,095 | $273,341 | 4.72 | $166,298 – $396,230 | 83% | $49,686 | $65,940 |
| 1d | $15M | h=10 | $1,032,357 | $368,046 | 4.35 | $207,182 – $555,092 | 80% | $91,173 | $102,732 |
| 1d | $20M | h=10 | $1,294,969 | $458,742 | 3.95 | $244,802 – $721,094 | 80% | $129,260 | $131,878 |
| 1h | $10M | h=10 | $673,108 | $301,180 | 4.95 | $185,912 – $427,894 | 91% | $77,525 | $102,294 |
| 1h | $15M | h=10 | $1,018,470 | $424,749 | 4.06 | $233,099 – $652,188 | 92% | $147,876 | $184,329 |
| 1h | $20M | h=10 | $1,335,545 | $534,926 | 3.66 | $271,177 – $850,866 | 93% | $205,444 | $241,446 |

Late entry on the 1d-crossing pool at $15,000,000 (hurdle re-chosen): an hour late $373,776 (102%), a day late $376,911 (102%).

Late entry on the 1h-crossing pool at $15,000,000 (hurdle re-chosen): an hour late $426,931 (101%), a day late $393,266 (93%).

## How often the dislocations coincide (unbounded capital, hurdle 10 bp, the all5 choice at $10M)

- Peak capital each asset would lock: etherfi_ev $163,349,515, kelp $8,716,692, khype $200,207,060, lbtc_cb $11,372,813, lido $515,530,733
- Sum of the peaks $899,176,813; peak of the sum $641,992,039 (all4: $641,992,039; ETH three: $641,992,039); 99th percentile of the sum $594,654,674; 90th $315,737,454.
- Busiest day 2025-09-01; days with any capital locked: 447 of 452.
- kHYPE against the sums: -0.14 with the three ETH bids, -0.14 with all four.

| pair | correlation of daily locked capital | days both locked | days either | overlap |
|---|---:|---:|---:|---:|
| etherfi_ev|kelp | 0.22 | 102 | 322 | 32% |
| etherfi_ev|khype | -0.12 | 72 | 314 | 23% |
| etherfi_ev|lbtc_cb | -0.17 | 105 | 360 | 29% |
| etherfi_ev|lido | 0.83 | 109 | 165 | 66% |
| kelp|khype | -0.11 | 106 | 388 | 27% |
| kelp|lbtc_cb | -0.13 | 160 | 413 | 39% |
| kelp|lido | 0.17 | 73 | 309 | 24% |
| khype|lbtc_cb | 0.13 | 197 | 338 | 58% |
| khype|lido | -0.14 | 40 | 304 | 13% |
| lbtc_cb|lido | -0.19 | 68 | 355 | 19% |

kHYPE at its own stand-alone hurdle (20bp), the others at 10bp: etherfi_ev -0.10, kelp -0.08, lbtc_cb 0.11, lido -0.10; with the ETH three summed -0.10, with all four -0.10.

## The hourly taker: what an executable bidder earns

Everything above buys each sale at its own print, capped at its own hour's venue median: only a bidder right behind each seller gets that. Here a sale that qualifies on that own-hour edge is bought at the next hour boundary H at the venue median of the trades inside [H, H+1h) (the rule; the first trade after H is the closer reading), and skipped when nothing traded there or the edge no longer clears the hurdle (`simulate_book(later='hour')`). Hurdle re-chosen in sample.

### Check against queue_live's implementations (f) and (g): all4 at $15M on queue_book's window

| version | queue_live | queue_book | hurdle | t | identical |
|---|---:|---:|---|---:|---|
| a day later|first | $213,887 | $213,887 | h=1 | 5.87 | yes |
| a day later|median | $213,113 | $213,113 | h=1 | 5.70 | yes |
| next hour|first | $317,253 | $317,253 | h=2 | 7.03 | yes |
| next hour|median | $294,743 | $294,743 | h=1 | 7.51 | yes |

Own-print baseline: queue_book $409,889, queue_live $409,885; the own-print baselines differ by about $4: queue_live resolves requests pending at the study's end with later queue events (waits of 63 stETH, 10 weETH and 10 rsETH sales in the last days); with its waits swapped into these envs the own-print value is queue_live's, and every later-priced value is identical.

### kHYPE alone (452 days, split 2026-02-26)

| size | own print | next hour, median | t | 95% interval | next hour, first trade | t |
|---:|---:|---:|---:|---|---:|---:|
| $10,000,000 | $140,043 | $113,872 (h=20) | 1.21 | $3,735 – $315,571 | $121,174 (h=20) | 1.23 |
| $30,000,000 | $373,849 | $334,407 (h=10) | 2.50 | $113,162 – $643,769 | $353,094 (h=10) | 2.50 |

kHYPE at $10M, later price, late entry: an hour late $183,448 (161%), a day late $128,458 (113%).

### The books as hourly takers (common window)

| book | pool | own print | next hour, median | t | 95% interval | by asset (median) | next hour, first trade |
|---|---:|---:|---:|---:|---|---|---:|
| all5 | $5M | $201,382 | $102,349 (h=20) | 2.07 | $15,428 – $218,151 | etherfi_ev $57,178, kelp $3,301, khype $35,339, lbtc_cb $6,531 | $99,895 (h=20) |
| all5 | $10M | $330,467 | $236,002 (h=10) | 3.79 | $119,110 – $374,106 | etherfi_ev $59,397, kelp $10,490, khype $126,258, lbtc_cb $17,650, lido $22,206 | $220,624 (h=20) |
| all5 | $15M | $460,554 | $353,855 (h=10) | 3.12 | $154,521 – $604,455 | etherfi_ev $76,519, kelp $10,490, khype $203,765, lbtc_cb $18,598, lido $44,483 | $365,189 (h=10) |
| all5 | $20M | $575,433 | $446,291 (h=10) | 3.08 | $185,970 – $767,114 | etherfi_ev $98,627, kelp $10,607, khype $243,587, lbtc_cb $26,722, lido $66,747 | $460,869 (h=10) |
| all5_1d_crossing | $5M | — | $107,945 (h=10) | 3.79 | $53,407 – $168,928 | etherfi_ev $33,626, kelp $10,492, khype $36,279, lbtc_cb $17,542, lido $10,006 | $107,114 (h=10) |
| all5_1d_crossing | $10M | $273,341 | $193,592 (h=10) | 3.49 | $88,786 – $319,348 | etherfi_ev $58,037, kelp $10,607, khype $64,462, lbtc_cb $31,709, lido $28,777 | $191,525 (h=10) |
| all5_1d_crossing | $15M | $368,046 | $293,463 (h=10) | 3.27 | $127,024 – $496,836 | etherfi_ev $84,636, kelp $10,607, khype $110,922, lbtc_cb $35,416, lido $51,881 | $288,520 (h=10) |
| all5_1d_crossing | $20M | $458,742 | $356,373 (h=10) | 3.07 | $142,096 – $617,638 | etherfi_ev $103,021, kelp $10,607, khype $124,036, lbtc_cb $35,416, lido $83,292 | $352,679 (h=10) |
| all4 | $5M | $145,888 | $81,051 (h=10) | 2.83 | $28,265 – $148,194 | etherfi_ev $37,016, kelp $10,528, lbtc_cb $23,553, lido $9,954 | $78,004 (h=10) |
| all4 | $10M | $223,655 | $134,224 (h=10) | 2.62 | $43,583 – $254,397 | etherfi_ev $58,810, kelp $10,607, lbtc_cb $34,393, lido $30,413 | $130,773 (h=10) |
| all4 | $15M | $276,873 | $184,984 (h=10) | 2.42 | $49,527 – $363,300 | etherfi_ev $85,314, kelp $10,607, lbtc_cb $35,416, lido $53,646 | $180,378 (h=10) |
| all4 | $20M | $329,482 | $235,122 (h=10) | 2.21 | $51,125 – $491,265 | etherfi_ev $102,560, kelp $10,607, lbtc_cb $35,416, lido $86,538 | $231,219 (h=10) |

| pool | all5 − all4 (median) | kHYPE leg a day behind − all4 | all5 − all4 (first trade) |
|---:|---:|---:|---:|
| $5M | $21,298 | $26,894 | $21,890 |
| $10M | $101,777 | $59,368 | $89,851 |
| $15M | $168,872 | $108,480 | $184,812 |
| $20M | $211,169 | $121,251 | $229,650 |

### Late entry with the later price (hurdle re-chosen)

| book | pool | on time | an hour late | kept | a day late | kept |
|---|---:|---:|---:|---:|---:|---:|
| all5_1d_crossing | $15M | $293,463 | $297,913 | 102% | $309,286 | 105% |
| all5 | $10M | $236,002 | $262,945 | 111% | $230,885 | 98% |
| all5 | $15M | $353,855 | $360,538 | 102% | $333,274 | 94% |
| all5 | $20M | $446,291 | $444,821 | 100% | $406,343 | 91% |

### Does the discount persist into the next hour? (sales qualifying on their own-hour edge, full window)

| asset | hurdle | qualifying sales | still clear at the next hour's median | by volume | no trade next hour | of those traded | at the first trade |
|---|---:|---:|---:|---:|---:|---:|---:|
| etherfi_ev | 1bp | 37,899 | 91% | 91% | 3% | 94% | 92% |
| kelp | 1bp | 1,635 | 34% | 34% | 64% | 96% | 35% |
| khype | 1bp | 119,823 | 98% | 99% | 0% | 98% | 99% |
| lbtc_cb | 1bp | 2,814 | 53% | 51% | 46% | 100% | 53% |
| lido | 1bp | 138,092 | 98% | 98% | 0% | 98% | 98% |
| etherfi_ev | 10bp | 12,661 | 93% | 91% | 2% | 95% | 95% |
| kelp | 10bp | 1,018 | 31% | 31% | 65% | 87% | 31% |
| khype | 10bp | 72,572 | 98% | 98% | 0% | 98% | 98% |
| lbtc_cb | 10bp | 2,088 | 53% | 48% | 44% | 96% | 53% |
| lido | 10bp | 41,739 | 95% | 91% | 0% | 95% | 96% |

Fixed split at $15M as hourly takers (each part its own hurdle; the split best in sample): $10,000,000 on HyperEVM, $194,923 a year ($2,000,000 → $187,947, $3,000,000 → $191,078, $5,000,000 → $198,002, $7,500,000 → $204,122, $10,000,000 → $194,923).
