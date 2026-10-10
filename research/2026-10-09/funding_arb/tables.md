# Funding spreads: tables

Generated from `analysis.json` (2026-10-10T10:43:35+00:00) by `scripts/funding_arb.py render`. Grid 2025-10-01T00:00:00+00:00, 8973 hours; choose period to 2026-04-01, test period from it; decisions every 4 hours (slow family weekly); fees taker {'hl': 4.5, 'binance': 5.0, 'bybit': 5.5, 'okx': 5.0, 'hl_spot': 7.0}, maker {'hl': 1.5, 'binance': 2.0, 'bybit': 2.0, 'okx': 2.0, 'hl_spot': 4.0} (bp); savings rate 3.80%.

Mapping: 384 listings checked by price ratio (or premium sign where no overlapping closes), 1 dropped (bybit:PURR); Hyperliquid coins delisted inside the study and included: 21; CEX perpetuals delisted inside it and included: 23. HL price sources: 69.1% of live HL hours have a real close (1-hour candles from about 2026-03-15, 4-hour candles before).

### The structure under the spreads (A minus B funding, each coin over the year)

| pair (A − B) | coins | median coin mean | share of coins A > B | median absolute | same sign both halves | correlation of coin means, choose half vs test half |
|---|---:|---:|---:|---:|---:|---:|
| Hyperliquid vs Binance | 191 | 1.39% | 61% | 4.06% | 71% | 0.42 |
| Hyperliquid vs Bybit | 192 | 1.54% | 59% | 5.00% | 67% | 0.32 |
| Binance vs Bybit (control) | 186 | -0.65% | 40% | 2.36% | 58% | 0.12 |

### Hyperliquid vs Binance — 191 coins, 106 variants

Chosen on the choose period: `k168_X20_Yzero_Hinf`. Reserved-capital series (each coin with a live pair holds one unit of capital, idle or not), daily:

| | ann. return | Sharpe | max DD | hit rate | days |
|---|---:|---:|---:|---:|---:|
| choose period | 2.44% | 7.71 | 0.15% | 78% | 182 |
| test period | 3.74% | 4.93 | 0.30% | 79% | 191 |
| monthly walk-forward | 2.91% | 4.36 | 0.30% | 74% | 281 |

Test-period Newey–West t 6.05 (p 0.0000); block-bootstrap 95% interval of the daily mean 0.719bp to 1.387bp (share at or below zero 0.000); test rank of the chosen variant 13 of 106; deflated Sharpe of the choice 0.000 against 106 trials in this pair type (0.971 against N_eff 60, mean pairwise correlation 0.44) and 0.936 against all 361 trials in the study; 92 of 106 variants survive Benjamini–Hochberg at 10% on the full year.

Per unit of deployed capital (capital = notional of one leg): choose period 8.4%, test period 12.9%, test minus the savings rate 9.1%.

| trades | n | mean hours | funding bp | basis bp | cost bp | net bp (mean) | net bp (median) | hit | net / position-year |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| choose, taker | 472 | 547 | 77.4 | 2.1 | 28.2 | 51.3 | 12.2 | 56% | 8.2% |
| test, taker | 319 | 635 | 114.8 | -17.1 | 27.3 | 70.4 | 13.5 | 61% | 9.7% |
| test, maker (upper bound) | 319 | 635 | 114.8 | -17.1 | 7.0 | 90.7 | 33.8 | 74% | 12.5% |

The ten best variants on the choose period, on the test period (deployed return): median 7.6%, worst 5.1%; 81% of all 106 variants beat the savings rate on the test period.

| variant | choose Sharpe | test Sharpe | test deployed return |
|---|---:|---:|---:|
| `k168_X20_Yzero_Hinf` | 7.71 | 4.93 | 12.9% |
| `slow_k30d_X8_Yhalf` | 7.57 | 4.26 | 8.1% |
| `k168_X10_Yzero_Hinf` | 7.52 | 5.70 | 9.0% |
| `slow_k30d_X6_Yhalf` | 7.30 | 4.84 | 7.1% |
| `slow_k90d_X4_Yzero` | 6.87 | 4.87 | 5.1% |
| `k72_X30_Yzero_Hinf` | 6.81 | 4.37 | 14.0% |
| `slow_k90d_X6_Yzero` | 6.75 | 9.29 | 5.1% |
| `k168_X20_Yzero_H720` | 6.73 | 4.16 | 13.6% |
| `slow_k90d_X4_Yhalf` | 6.72 | 5.02 | 6.0% |
| `slow_k90d_X6_Yhalf` | 6.71 | 8.99 | 6.2% |

By direction, test trades: short hl long binance 159 trades, 85.7 bp net mean, 10.3% a position-year; short binance long hl 160 trades, 55.2 bp net mean, 8.9% a position-year.

| month | 25-10 | 25-11 | 25-12 | 26-01 | 26-02 | 26-03 | 26-04 | 26-05 | 26-06 | 26-07 | 26-08 | 26-09 | 26-10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| deployed return, annualised | 14% | 7% | 9% | 8% | 3% | 11% | 21% | 17% | 11% | 10% | 9% | 11% | 10% |
| average open positions | 41.2 | 68.9 | 50.5 | 48.2 | 47.9 | 53.7 | 58.1 | 38.4 | 43.3 | 50.1 | 50.2 | 61.3 | 69.1 |

With a 30-day HAC lag the test-period t is 5.15 (p 0.0000); a 30-day block bootstrap puts the daily mean between 0.683 and 1.447 bp. Margin stress: 50% of test trades saw a 25% move against one leg while held, 21% a 40% move.

Premium-proxy check on the 245 test trades with real closes on both legs at entry and exit: basis 13.1 bp a trade on real prices against 8.3 bp on the proxy (correlation 0.17, mean absolute gap 27.2 bp).

| family | chosen | choose ann. | choose Sharpe | test ann. | test Sharpe | test t |
|---|---|---:|---:|---:|---:|---:|
| fast | `k168_X20_Yzero_Hinf` | 2.44% | 7.71 | 3.74% | 4.93 | 6.05 |
| slow | `slow_k30d_X8_Yhalf` | 1.89% | 7.57 | 3.33% | 4.26 | 5.93 |

Capacity at the live books (10 bp VWAP on every leg in both directions, at most 5% of the smaller open interest): **$-19k a year** on the test period across 145 coins (132 with books; median size $5k), on an average concurrent notional of $1.23M (peak $2.63M): -1.6% on the average capital, $-66k a year after paying the 3.80% savings rate on it ($-119k on the peak). The largest-capacity coin, ZEC, is 42% of that average capital; without it the book makes $-9k a year. At 20 bp VWAP: $-171k a year on a peak of $8.36M.

| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | $/yr after the savings rate |
|---|---:|---:|---:|---:|---:|
| $10k | 132 | $228k | $1k | 0.6% | $-7k |
| $25k | 132 | $380k | $-1k | -0.3% | $-16k |
| $50k | 132 | $530k | $-4k | -0.7% | $-24k |

| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |
|---|---:|---:|---:|---:|
| $0 to $5k | 66 | 163 | 66.0 | 9.5% |
| $5k to $25k | 41 | 93 | 13.9 | 2.0% |
| $25k to $100k | 20 | 29 | 16.2 | 1.5% |
| over $100k | 5 | 7 | 50.4 | 3.5% |

| coin | trades | hours | funding bp | basis bp | net bp (small) | size | slip bp/fill | net bp at size | $/yr at size |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| NEAR | 1 | 4284 | 700.1 | -351.9 | 326.8 | $114k | 6.3/4.3 | 307.9 | $7k |
| TAO | 1 | 4352 | 370.1 | -157.4 | 192.1 | $83k | 9.8/6.2 | 161.6 | $3k |
| XMR | 4 | 3068 | 501.7 | 4.2 | 425.9 | $27k | 7.3/6.6 | 318.8 | $2k |
| GRAM | 1 | 2108 | 299.9 | 15.0 | 288.3 | $28k | 7.3/9.4 | 262.6 | $1k |
| VVV | 2 | 2944 | 577.4 | -65.8 | 468.3 | $14k | 7.0/9.1 | 409.2 | $1k |
| kBONK | 2 | 1904 | 406.2 | -173.3 | 177.1 | $35k | 8.8/7.8 | 128.5 | $859 |
| WLFI | 1 | 3236 | 138.1 | -8.9 | 107.9 | $45k | 5.9/7.4 | 83.6 | $718 |
| kFLOKI | 2 | 2708 | 306.7 | -11.7 | 245.4 | $13k | 8.1/7.9 | 193.0 | $492 |
| MINA | 6 | 3712 | 716.4 | -32.6 | 534.7 | $6k | 8.2/5.9 | 401.0 | $441 |
| kNEIRO | 1 | 1820 | 609.4 | -38.7 | 547.0 | $4k | 8.8/7.1 | 519.8 | $429 |
| FET | 2 | 3788 | 503.3 | -313.1 | 140.8 | $25k | 6.4/9.0 | 90.7 | $427 |
| SAGA | 7 | 3044 | 1234.0 | 220.6 | 1225.3 | $2k | 10.0/4.8 | 1114.7 | $415 |
| AERO | 2 | 3504 | 592.2 | -267.2 | 281.1 | $9k | 9.4/6.0 | 225.7 | $404 |
| WIF | 1 | 1056 | 146.0 | -12.0 | 109.4 | $23k | 6.0/8.7 | 85.6 | $378 |
| SAND | 3 | 756 | 188.3 | 115.2 | 240.5 | $9k | 6.9/4.3 | 179.0 | $296 |
| ASTER | 1 | 1128 | 46.6 | -111.8 | -86.2 | $94k | 8.5/9.3 | -119.7 | $-2k |
| ENA | 1 | 1136 | 101.0 | -191.3 | -111.6 | $90k | 8.9/6.8 | -140.7 | $-2k |
| PUMP | 1 | 1164 | 118.4 | -344.5 | -248.7 | $80k | 6.6/9.3 | -276.8 | $-4k |
| ZRO | 2 | 1872 | 265.9 | -1224.6 | -1000.8 | $22k | 9.0/8.4 | -1066.4 | $-4k |
| ZEC | 3 | 2724 | 310.1 | -207.0 | 42.1 | $877k | 8.3/9.8 | -62.3 | $-10k |

**The slow family on its own** (`slow_k30d_X8_Yhalf`, chosen inside the family on the choose period): deployed return choose 5.2%, test 8.1%; 219 test trades, 37.6 bp net mean (-6.7 median), 47% hit, 3.3% a position-year; maker upper bound 4.9% a position-year; 33% of test trades saw a 40% move against one leg.

Capacity at the live books (10 bp VWAP on every leg in both directions, at most 5% of the smaller open interest): **$-30k a year** on the test period across 142 coins (133 with books; median size $6k), on an average concurrent notional of $1.58M (peak $3.44M): -1.9% on the average capital, $-90k a year after paying the 3.80% savings rate on it ($-161k on the peak). The largest-capacity coin, HYPE, is 27% of that average capital; without it the book makes $-38k a year. At 20 bp VWAP: $-185k a year on a peak of $9.81M.

| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | $/yr after the savings rate |
|---|---:|---:|---:|---:|---:|
| $10k | 133 | $265k | $2k | 0.7% | $-8k |
| $25k | 133 | $445k | $2k | 0.4% | $-15k |
| $50k | 133 | $631k | $-817 | -0.1% | $-25k |

| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |
|---|---:|---:|---:|---:|
| $0 to $5k | 62 | 108 | 34.9 | 3.2% |
| $5k to $25k | 40 | 66 | 25.7 | 2.5% |
| $25k to $100k | 21 | 25 | 3.9 | 0.2% |
| over $100k | 10 | 10 | 49.9 | 3.3% |

| coin | trades | hours | funding bp | basis bp | net bp (small) | size | net bp at size | $/yr at size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| WLD | 1 | 3596 | 644.8 | -43.2 | 579.1 | $139k | 548.1 | $14k |
| HYPE | 1 | 1680 | 87.5 | 1.1 | 68.7 | $1.19M | 36.9 | $8k |
| NEAR | 1 | 4100 | 714.8 | -408.1 | 285.3 | $114k | 266.4 | $6k |
| XMR | 1 | 4268 | 795.3 | -242.8 | 532.5 | $27k | 505.7 | $3k |
| VVV | 2 | 4100 | 853.4 | -107.8 | 702.3 | $14k | 643.2 | $2k |
| MINA | 2 | 3428 | 1086.8 | 45.4 | 1082.6 | $6k | 1038.0 | $1k |
| ONDO | 1 | 3428 | 416.2 | -269.9 | 124.8 | $60k | 99.2 | $1k |
| kFLOKI | 1 | 3024 | 330.4 | -5.3 | 300.3 | $13k | 274.1 | $699 |
| AERO | 1 | 3932 | 687.6 | -282.2 | 383.5 | $9k | 355.8 | $637 |
| BERA | 2 | 1916 | 148.3 | 237.0 | 332.7 | $9k | 277.9 | $452 |
| LINK | 1 | 572 | 33.2 | -82.0 | -69.4 | $208k | -97.8 | $-4k |
| PUMP | 1 | 1076 | 97.3 | -357.3 | -282.6 | $80k | -310.7 | $-5k |
| BNB | 1 | 572 | 41.3 | -61.3 | -40.1 | $565k | -64.9 | $-7k |
| SUI | 1 | 572 | 80.8 | -212.7 | -154.5 | $224k | -185.4 | $-8k |
| ZEC | 1 | 1076 | 152.7 | -258.1 | -125.7 | $877k | -160.5 | $-27k |

### Hyperliquid vs Bybit — 192 coins, 106 variants

Chosen on the choose period: `slow_k90d_X6_Yzero`. Reserved-capital series (each coin with a live pair holds one unit of capital, idle or not), daily:

| | ann. return | Sharpe | max DD | hit rate | days |
|---|---:|---:|---:|---:|---:|
| choose period | 1.73% | 6.00 | 0.08% | 76% | 182 |
| test period | 3.26% | 9.37 | 0.10% | 74% | 191 |
| monthly walk-forward | 2.43% | 6.38 | 0.18% | 70% | 281 |

Test-period Newey–West t 8.08 (p 0.0000); block-bootstrap 95% interval of the daily mean 0.679bp to 1.112bp (share at or below zero 0.000); test rank of the chosen variant 1 of 106; deflated Sharpe of the choice 0.000 against 106 trials in this pair type (0.968 against N_eff 48, mean pairwise correlation 0.55) and 0.885 against all 361 trials in the study; 70 of 106 variants survive Benjamini–Hochberg at 10% on the full year.

Per unit of deployed capital (capital = notional of one leg): choose period 5.8%, test period 5.0%, test minus the savings rate 1.2%.

| trades | n | mean hours | funding bp | basis bp | cost bp | net bp (mean) | net bp (median) | hit | net / position-year |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| choose, taker | 147 | 3875 | 249.5 | -25.3 | 29.8 | 194.4 | 84.8 | 65% | 4.4% |
| test, taker | 90 | 2117 | 164.2 | -50.8 | 28.2 | 85.3 | 27.6 | 60% | 3.5% |
| test, maker (upper bound) | 90 | 2117 | 164.2 | -50.8 | 7.0 | 106.4 | 50.0 | 63% | 4.4% |

The ten best variants on the choose period, on the test period (deployed return): median 5.1%, worst 4.1%; 47% of all 106 variants beat the savings rate on the test period.

| variant | choose Sharpe | test Sharpe | test deployed return |
|---|---:|---:|---:|
| `slow_k90d_X6_Yzero` | 6.00 | 9.37 | 5.0% |
| `slow_k90d_X6_Yhalf` | 5.91 | 7.97 | 5.9% |
| `slow_k30d_X6_Yzero` | 5.64 | 7.86 | 4.8% |
| `slow_k90d_X4_Yzero` | 5.57 | 9.35 | 4.4% |
| `slow_k90d_X4_Yhalf` | 5.55 | 8.22 | 5.1% |
| `slow_k90d_X8_Yzero` | 5.49 | 7.38 | 5.2% |
| `slow_k90d_X2_Yzero` | 5.23 | 9.12 | 4.1% |
| `slow_k90d_X8_Yhalf` | 5.19 | 6.65 | 6.3% |
| `slow_k30d_X6_Yhalf` | 5.18 | 7.74 | 5.7% |
| `slow_k90d_X2_Yhalf` | 5.15 | 9.31 | 4.5% |

By direction, test trades: short hl long bybit 62 trades, 54.1 bp net mean, 2.4% a position-year; short bybit long hl 28 trades, 154.3 bp net mean, 5.7% a position-year.

| month | 25-10 | 25-11 | 25-12 | 26-01 | 26-02 | 26-03 | 26-04 | 26-05 | 26-06 | 26-07 | 26-08 | 26-09 | 26-10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| deployed return, annualised | - | - | -58% | 5% | 8% | 6% | 8% | 3% | 5% | 4% | 3% | 7% | 6% |
| average open positions | 0.0 | 0.0 | 2.9 | 100.9 | 110.6 | 115.2 | 119.0 | 117.0 | 108.2 | 110.5 | 111.3 | 113.4 | 120.0 |

With a 30-day HAC lag the test-period t is 6.99 (p 0.0000); a 30-day block bootstrap puts the daily mean between 0.657 and 1.148 bp. Margin stress: 84% of test trades saw a 25% move against one leg while held, 59% a 40% move.

Premium-proxy check on the 16 test trades with real closes on both legs at entry and exit: basis -19.6 bp a trade on real prices against -17.7 bp on the proxy (correlation 0.98, mean absolute gap 11.7 bp).

| family | chosen | choose ann. | choose Sharpe | test ann. | test Sharpe | test t |
|---|---|---:|---:|---:|---:|---:|
| fast | `k168_X50_Yzero_Hinf` | 1.40% | 3.86 | 0.62% | 1.87 | 1.61 |
| slow | `slow_k90d_X6_Yzero` | 1.73% | 6.00 | 3.26% | 9.37 | 8.08 |

Capacity at the live books (10 bp VWAP on every leg in both directions, at most 5% of the smaller open interest): **$-15k a year** on the test period across 84 coins (81 with books; median size $2k), on an average concurrent notional of $431k (peak $1.81M): -3.4% on the average capital, $-31k a year after paying the 3.80% savings rate on it ($-83k on the peak). The largest-capacity coin, DOGE, is 9% of that average capital; without it the book makes $-761 a year. At 20 bp VWAP: $-37k a year on a peak of $4.09M.

| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | $/yr after the savings rate |
|---|---:|---:|---:|---:|---:|
| $10k | 81 | $162k | $341 | 0.2% | $-6k |
| $25k | 81 | $246k | $609 | 0.2% | $-9k |
| $50k | 81 | $309k | $513 | 0.2% | $-11k |

| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |
|---|---:|---:|---:|---:|
| $0 to $5k | 50 | 54 | 119.2 | 4.7% |
| $5k to $25k | 19 | 21 | -38.4 | -1.5% |
| $25k to $100k | 9 | 9 | 99.9 | 4.0% |
| over $100k | 3 | 3 | -64.1 | -23.8% |

| coin | trades | hours | funding bp | basis bp | net bp (small) | size | slip bp/fill | net bp at size | $/yr at size |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| WLD | 1 | 4604 | 685.0 | -29.2 | 632.3 | $100k | 8.1/8.5 | 602.5 | $11k |
| XMR | 1 | 4100 | 787.3 | -222.0 | 542.1 | $27k | 7.3/6.4 | 517.9 | $3k |
| VVV | 1 | 2924 | 461.0 | -145.3 | 293.9 | $7k | 5.4/10.0 | 264.9 | $337 |
| CC | 1 | 4604 | 428.2 | -43.0 | 358.5 | $4k | 4.0/9.6 | 338.0 | $265 |
| GMT | 1 | 1076 | -3.4 | 891.4 | 855.5 | $1k | 6.9/5.3 | 843.4 | $215 |
| MOODENG | 1 | 3932 | 109.2 | 125.1 | 200.2 | $6k | 9.2/6.8 | 182.2 | $203 |
| MORPHO | 1 | 4100 | 355.2 | -161.9 | 166.9 | $7k | 5.0/9.9 | 143.5 | $191 |
| APE | 1 | 4436 | 523.9 | -54.7 | 444.0 | $2k | 5.7/8.1 | 421.7 | $156 |
| kBONK | 1 | 2252 | 183.8 | -107.1 | 47.9 | $28k | 8.0/7.6 | 25.4 | $134 |
| MINA | 1 | 2588 | 478.4 | 77.4 | 528.8 | $1k | 3.0/9.6 | 510.8 | $125 |
| PENDLE | 1 | 1916 | 179.2 | -42.1 | 110.0 | $7k | 6.2/9.2 | 86.2 | $122 |
| CAKE | 1 | 1076 | 160.5 | -16.7 | 116.6 | $7k | 7.5/8.5 | 91.7 | $115 |
| ACE | 1 | 4436 | 578.4 | 92.4 | 639.0 | $889 | 4.9/9.8 | 621.4 | $105 |
| SAGA | 1 | 3596 | 226.3 | 208.5 | 404.7 | $1k | 7.7/8.5 | 382.6 | $93 |
| GAS | 1 | 3764 | 163.5 | 41.4 | 178.1 | $2k | 6.4/9.8 | 152.5 | $68 |
| XLM | 1 | 68 | 7.5 | -87.5 | -106.1 | $69k | 8.5/7.5 | -131.9 | $-2k |
| ENA | 1 | 1748 | 351.8 | -412.4 | -83.0 | $90k | 8.9/6.2 | -110.9 | $-2k |
| kPEPE | 1 | 236 | -0.1 | -35.8 | -60.9 | $203k | 9.5/8.1 | -91.1 | $-4k |
| LTC | 1 | 236 | 15.0 | -61.6 | -69.1 | $188k | 8.2/9.2 | -101.4 | $-4k |
| DOGE | 1 | 236 | 17.3 | -57.9 | -62.3 | $762k | 9.8/8.3 | -96.8 | $-14k |

**The fast family on its own** (`k168_X50_Yzero_Hinf`, chosen inside the family on the choose period): deployed return choose 11.9%, test 18.2%; 91 test trades, 57.3 bp net mean (-3.5 median), 49% hit, 18.1% a position-year; maker upper bound 25.9% a position-year; 20% of test trades saw a 40% move against one leg.

Capacity at the live books (10 bp VWAP on every leg in both directions, at most 5% of the smaller open interest): **$-2k a year** on the test period across 47 coins (37 with books; median size $1k), on an average concurrent notional of $10k (peak $80k): -18.0% on the average capital, $-2k a year after paying the 3.80% savings rate on it ($-5k on the peak). The largest-capacity coin, TRUMP, is 22% of that average capital; without it the book makes $-572 a year. At 20 bp VWAP: $-10k a year on a peak of $252k.

| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | $/yr after the savings rate |
|---|---:|---:|---:|---:|---:|
| $10k | 37 | $7k | $-852 | -12.6% | $-1k |
| $25k | 37 | $9k | $-952 | -11.1% | $-1k |
| $50k | 37 | $9k | $-1k | -14.3% | $-2k |

| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |
|---|---:|---:|---:|---:|
| $0 to $5k | 33 | 66 | -13.2 | -3.8% |
| $5k to $25k | 2 | 5 | -25.1 | -11.9% |
| $25k to $100k | 2 | 2 | 4.9 | 1.6% |
| over $100k | 0 | 0 | - | - |

| coin | trades | hours | funding bp | basis bp | net bp (small) | size | net bp at size | $/yr at size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| XMR | 1 | 412 | 96.5 | 0.8 | 74.2 | $27k | 50.0 | $258 |
| SAGA | 5 | 1076 | 763.0 | 40.9 | 653.4 | $1k | 542.7 | $132 |
| CASHCAT | 1 | 1024 | 446.6 | 18.8 | 437.3 | $2k | 416.9 | $120 |
| HEMI | 2 | 620 | 328.3 | 99.4 | 373.9 | $877 | 332.8 | $56 |
| AXS | 1 | 468 | 69.7 | 33.8 | 79.5 | $3k | 51.8 | $32 |
| ZORA | 2 | 624 | 54.7 | 89.9 | 85.5 | $888 | 50.3 | $9 |
| APEX | 1 | 1132 | 521.8 | 30.7 | 518.1 | $77 | 512.3 | $7 |
| GRIFFAIN | 3 | 448 | 100.2 | 519.7 | 535.0 | $63 | 507.8 | $6 |
| SOPH | 2 | 2084 | 407.3 | -265.8 | 90.5 | $518 | 53.3 | $5 |
| PROVE | 2 | 1456 | 323.1 | -223.5 | 42.5 | $1k | 13.4 | $4 |
| SKR | 5 | 492 | -324.9 | -76.5 | -538.0 | $1k | -609.1 | $-157 |
| NIL | 1 | 376 | 23.4 | -157.5 | -156.2 | $5k | -184.6 | $-160 |
| 2Z | 2 | 440 | 32.3 | -84.8 | -108.7 | $7k | -169.7 | $-222 |
| ACE | 7 | 1744 | -364.8 | -680.2 | -1267.3 | $889 | -1390.7 | $-235 |
| TRUMP | 1 | 136 | -26.3 | -10.8 | -64.4 | $74k | -89.4 | $-1k |

### Binance vs Bybit (control) — 186 coins, 106 variants

Chosen on the choose period: `slow_k30d_X4_Yzero`. Reserved-capital series (each coin with a live pair holds one unit of capital, idle or not), daily:

| | ann. return | Sharpe | max DD | hit rate | days |
|---|---:|---:|---:|---:|---:|
| choose period | 2.07% | 4.69 | 0.12% | 61% | 182 |
| test period | 0.71% | 2.78 | 0.17% | 63% | 191 |
| monthly walk-forward | 0.65% | 2.37 | 0.17% | 61% | 281 |

Test-period Newey–West t 1.92 (p 0.0550); block-bootstrap 95% interval of the daily mean -0.023bp to 0.377bp (share at or below zero 0.041); test rank of the chosen variant 8 of 106; deflated Sharpe of the choice 0.000 against 106 trials in this pair type (0.901 against N_eff 46, mean pairwise correlation 0.57) and 0.664 against all 361 trials in the study; 63 of 106 variants survive Benjamini–Hochberg at 10% on the full year.

Per unit of deployed capital (capital = notional of one leg): choose period 3.5%, test period 1.2%, test minus the savings rate -2.6%.

| trades | n | mean hours | funding bp | basis bp | cost bp | net bp (mean) | net bp (median) | hit | net / position-year |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| choose, taker | 312 | 2134 | 113.2 | -5.6 | 29.2 | 78.4 | 17.2 | 54% | 3.2% |
| test, taker | 200 | 1392 | 30.3 | -6.6 | 29.4 | -5.7 | -8.4 | 46% | -0.4% |
| test, maker (upper bound) | 200 | 1392 | 30.3 | -6.6 | 8.0 | 15.7 | 13.7 | 56% | 1.0% |

The ten best variants on the choose period, on the test period (deployed return): median 1.2%, worst -80.0%; 0% of all 106 variants beat the savings rate on the test period.

| variant | choose Sharpe | test Sharpe | test deployed return |
|---|---:|---:|---:|
| `slow_k30d_X4_Yzero` | 4.69 | 2.78 | 1.2% |
| `slow_k30d_X2_Yzero` | 4.42 | 0.38 | 0.2% |
| `slow_k30d_X6_Yzero` | 4.19 | 3.16 | 1.6% |
| `slow_k30d_X4_Yhalf` | 3.74 | 1.88 | 1.1% |
| `slow_k30d_X8_Yzero` | 3.69 | 3.14 | 1.8% |
| `slow_k30d_X2_Yhalf` | 3.63 | 0.05 | 0.0% |
| `slow_k30d_X6_Yhalf` | 3.37 | 1.85 | 1.5% |
| `k168_X100_Yzero_Hinf` | 3.13 | -3.04 | -80.0% |
| `slow_k90d_X8_Yzero` | 3.06 | 2.99 | 1.7% |
| `slow_k90d_X8_Yhalf` | 3.03 | 1.46 | 1.3% |

By direction, test trades: short binance long bybit 111 trades, 26.7 bp net mean, 1.6% a position-year; short bybit long binance 89 trades, -46.1 bp net mean, -3.0% a position-year.

| month | 25-10 | 25-11 | 25-12 | 26-01 | 26-02 | 26-03 | 26-04 | 26-05 | 26-06 | 26-07 | 26-08 | 26-09 | 26-10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| deployed return, annualised | - | 14% | 3% | 1% | 2% | -1% | 2% | 1% | 2% | 1% | 1% | 3% | -9% |
| average open positions | 0.0 | 107.4 | 134.2 | 129.6 | 130.4 | 126.8 | 119.8 | 109.7 | 115.5 | 101.9 | 104.5 | 91.8 | 84.8 |

With a 30-day HAC lag the test-period t is 2.60 (p 0.0092); a 30-day block bootstrap puts the daily mean between 0.030 and 0.322 bp. Margin stress: 70% of test trades saw a 25% move against one leg while held, 43% a 40% move.

Premium-proxy check on the 195 test trades with real closes on both legs at entry and exit: basis -3.9 bp a trade on real prices against -1.1 bp on the proxy (correlation 0.34, mean absolute gap 12.2 bp).

| family | chosen | choose ann. | choose Sharpe | test ann. | test Sharpe | test t |
|---|---|---:|---:|---:|---:|---:|
| fast | `k168_X100_Yzero_Hinf` | 0.86% | 3.13 | -0.17% | -3.04 | -1.90 |
| slow | `slow_k30d_X4_Yzero` | 2.07% | 4.69 | 0.71% | 2.78 | 1.92 |

Capacity at the live books (10 bp VWAP on every leg in both directions, at most 5% of the smaller open interest): **$-20k a year** on the test period across 121 coins (117 with books; median size $3k), on an average concurrent notional of $881k (peak $1.45M): -2.3% on the average capital, $-54k a year after paying the 3.80% savings rate on it ($-76k on the peak). The largest-capacity coin, ZEC, is 12% of that average capital; without it the book makes $-14k a year. At 20 bp VWAP: $-124k a year on a peak of $4.38M.

| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | $/yr after the savings rate |
|---|---:|---:|---:|---:|---:|
| $10k | 117 | $230k | $-3k | -1.2% | $-11k |
| $25k | 117 | $378k | $-4k | -1.1% | $-19k |
| $50k | 117 | $500k | $-7k | -1.3% | $-26k |

| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |
|---|---:|---:|---:|---:|
| $0 to $5k | 71 | 127 | -14.0 | -0.8% |
| $5k to $25k | 25 | 39 | 28.9 | 2.0% |
| $25k to $100k | 14 | 20 | 2.2 | 0.1% |
| over $100k | 7 | 8 | -6.7 | -0.4% |

| coin | trades | hours | funding bp | basis bp | net bp (small) | size | slip bp/fill | net bp at size | $/yr at size |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| USELESS | 2 | 3092 | 774.4 | 43.2 | 771.0 | $13k | 8.5/7.6 | 711.2 | $2k |
| TAO | 1 | 2252 | 75.2 | -4.3 | 49.0 | $71k | 5.7/8.0 | 22.5 | $306 |
| POL | 1 | 1580 | 132.6 | -0.4 | 109.2 | $20k | 7.8/8.6 | 78.3 | $303 |
| kFLOKI | 1 | 2688 | 183.0 | 10.3 | 165.1 | $10k | 7.0/9.0 | 140.3 | $279 |
| FARTCOIN | 1 | 1412 | 121.9 | 11.3 | 105.4 | $18k | 7.1/8.9 | 80.1 | $275 |
| JUP | 1 | 3024 | 145.5 | -14.3 | 104.7 | $16k | 5.4/9.8 | 79.9 | $238 |
| INJ | 1 | 2520 | 89.8 | -0.5 | 65.5 | $31k | 6.9/8.7 | 37.2 | $222 |
| DOT | 1 | 4604 | 87.0 | 5.4 | 69.8 | $25k | 5.3/8.2 | 44.5 | $214 |
| CAKE | 1 | 2924 | 206.9 | -20.3 | 160.6 | $7k | 5.2/8.9 | 137.3 | $184 |
| GRASS | 1 | 4268 | 200.2 | 18.3 | 191.5 | $6k | 7.0/7.2 | 169.1 | $180 |
| MINA | 2 | 3932 | 708.6 | 24.3 | 684.1 | $1k | 2.9/9.6 | 640.8 | $157 |
| PENGU | 1 | 2352 | 58.8 | 7.1 | 42.5 | $38k | 5.9/8.9 | 15.3 | $111 |
| SUSHI | 1 | 4436 | 235.4 | -11.2 | 190.5 | $2k | 6.1/8.3 | 174.3 | $82 |
| ASTER | 2 | 3428 | 103.3 | 6.7 | 62.3 | $28k | 4.1/9.5 | 13.9 | $73 |
| ALT | 1 | 3092 | 197.3 | 21.7 | 186.7 | $2k | 8.3/9.9 | 161.8 | $69 |
| TRUMP | 3 | 908 | 16.7 | 4.9 | -72.9 | $82k | 6.6/9.2 | -136.0 | $-2k |
| ADA | 1 | 840 | 4.4 | 0.0 | -24.5 | $222k | 8.1/9.8 | -52.4 | $-2k |
| TRX | 2 | 2016 | 4.0 | -4.0 | -49.1 | $157k | 3.1/6.8 | -81.6 | $-2k |
| ARK | 2 | 1748 | -2951.2 | -116.6 | -3125.6 | $4k | 7.1/8.2 | -3171.1 | $-3k |
| ZEC | 1 | 572 | 22.8 | 0.7 | 1.6 | $877k | 9.8/9.2 | -35.4 | $-6k |

**The fast family on its own** (`k168_X100_Yzero_Hinf`, chosen inside the family on the choose period): deployed return choose 34.7%, test -80.0%; 11 test trades, -140.6 bp net mean (-141.3 median), 18% hit, -77.3% a position-year; maker upper bound -66.7% a position-year; 27% of test trades saw a 40% move against one leg.

Capacity at the live books (10 bp VWAP on every leg in both directions, at most 5% of the smaller open interest): **$-197 a year** on the test period across 8 coins (8 with books; median size $1k), on an average concurrent notional of $2k (peak $41k): -10.6% on the average capital, $-267 a year after paying the 3.80% savings rate on it ($-2k on the peak). The largest-capacity coin, SAND, is 70% of that average capital; without it the book makes $-17 a year. At 20 bp VWAP: $-1k a year on a peak of $98k.

| per-coin size limit (or capacity, if smaller) | coins | average concurrent notional | $/yr | return on it | $/yr after the savings rate |
|---|---:|---:|---:|---:|---:|
| $10k | 8 | $909 | $-28 | -3.1% | $-63 |
| $25k | 8 | $1k | $-103 | -7.2% | $-157 |
| $50k | 8 | $2k | $-197 | -10.6% | $-267 |

| coin capacity at 10bp | coins | test trades | net bp a trade (small size) | net a position-year |
|---|---:|---:|---:|---:|
| $0 to $5k | 6 | 9 | -163.3 | -89.9% |
| $5k to $25k | 1 | 1 | -86.0 | -47.1% |
| $25k to $100k | 1 | 1 | 8.7 | 4.7% |
| over $100k | 0 | 0 | - | - |

| coin | trades | hours | funding bp | basis bp | net bp (small) | size | net bp at size | $/yr at size |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ARK | 1 | 208 | 826.8 | -262.9 | 535.0 | $4k | 512.3 | $420 |
| SOPH | 1 | 168 | -18.6 | -206.4 | -251.5 | $518 | -267.5 | $-26 |
| BLUR | 3 | 504 | -102.3 | -263.5 | -446.7 | $375 | -488.8 | $-35 |
| BABY | 1 | 168 | -42.0 | -232.8 | -303.9 | $701 | -328.4 | $-44 |
| ACE | 1 | 168 | -115.5 | -412.0 | -555.5 | $889 | -569.8 | $-96 |
| KAITO | 1 | 160 | -22.8 | -35.9 | -86.0 | $5k | -107.6 | $-110 |
| SKR | 2 | 216 | -200.9 | -190.5 | -446.7 | $1k | -487.5 | $-125 |
| SAND | 1 | 160 | 46.7 | -14.1 | 8.7 | $37k | -25.5 | $-180 |

### The chosen rules on a third venue: Hyperliquid vs OKX (OKX funding history from 2026-06-29)

Rules chosen on Hyperliquid vs Binance before 2026-04-01, run unchanged from the first decision with a full signal window:

| rule | pair | from | coins | trades | mean hours | funding bp | basis bp | cost bp | net bp | hit | net / position-year |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| overall `k168_X20_Yzero_Hinf` | hl_okx | 2026-07-06 | 147 | 141 | 582 | 71.5 | -63.9 | 27.4 | -19.9 | 45% | -3.0% |
| overall `k168_X20_Yzero_Hinf` | hl_binance_same_dates | 2026-07-06 | 191 | 162 | 648 | 91.1 | -43.5 | 26.0 | 21.7 | 56% | 2.9% |
| slow `slow_k30d_X8_Yhalf` | hl_okx | 2026-08-05 | 147 | 107 | 655 | 60.8 | -111.7 | 26.3 | -77.2 | 20% | -10.3% |
| slow `slow_k30d_X8_Yhalf` | hl_binance_same_dates | 2026-08-05 | 191 | 118 | 752 | 79.7 | -87.1 | 25.9 | -33.2 | 31% | -3.9% |

### Hyperliquid spot–perp carry — 15 coins (AVAX, AZTEC, BTC, ENA, ETH, FARTCOIN, HYPE, MON, PUMP, PURR, SOL, STABLE, XPL, ZEC, kBONK), 31 variants

Chosen `k24_X20_Yzero`: choose period 3.40% a year (Sharpe 5.98), test period 10.12% (Sharpe 1.86, t 1.62). Return on capital (spot fully paid + perp at 2x = 1.5 of notional), test period: chosen 21.3%, always-on 4.6%. HYPE staking yield read from the validators: 2.18%.

Test-period P&L per coin is marked daily, so a position opened before the test period and still held counts for its test-period part; return on capital charges 1.5 of notional.

| perp | spot token | chosen: test P&L bp | return on capital | always-on: test P&L bp | return on capital | size at 10bp | chosen $/yr at size | always-on $/yr at size |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| PURR | PURR | 1628.0 | 23.0% | 742.4 | 9.5% | $0 | - | - |
| PUMP | UPUMP | 291.9 | 14.5% | 253.0 | 3.2% | $10k | $532 | $471 |
| HYPE | HYPE | 123.3 | 7.5% | 691.0 | 8.8% | $123k | $2k | $16k |
| MON | UMON | 238.3 | 13.3% | 237.2 | 3.0% | $2k | $61 | $71 |
| BTC | UBTC | 0.0 | - | 184.5 | 2.4% | $599k | - | $21k |
| ETH | UETH | 0.0 | - | 176.5 | 2.2% | $491k | - | $16k |
| SOL | USOL | 8.8 | 2.0% | 85.0 | 1.1% | $311k | $-738 | $4k |
| FARTCOIN | UFART | 927.6 | 13.7% | 235.6 | 3.0% | $4k | $660 | $173 |
| kBONK | UBONK | -246.2 | -10.5% | 39.9 | 0.5% | $0 | - | - |
| ENA | UENA | 255.8 | 8.9% | 219.1 | 2.8% | $708 | $32 | $29 |
| XPL | UXPL | 246.9 | 10.5% | 65.7 | 0.8% | $3k | $114 | $31 |
| STABLE | STABLE | 3661.5 | 385.3% | 252.2 | 3.2% | $0 | - | - |
| ZEC | UZEC | 507.3 | 13.0% | 1626.5 | 20.7% | $53k | $4k | $16k |
| AZTEC | AZTEC | 366.7 | 9.5% | 1044.7 | 13.3% | $22 | $1 | $4 |
| AVAX | UAVAX | -86.6 | -7.4% | -460.5 | -7.3% | $0 | - | - |

Sum at size: chosen rule $7k a year, always-on $74k a year.

### Cross-sectional carry factor on Hyperliquid core (a factor, not an arbitrage) — 12 variants

Chosen `k168_q20_dollar`: choose period 19.1% a year at 17.7% volatility (Sharpe 1.08); test period 1.7% at 17.4% (Sharpe 0.10, t 0.08, p 0.934, test rank 2); deflated Sharpe of the choice 0.605; correlation with BTC in the test period -0.26; mean daily turnover 26.2% of gross.

| variant | choose Sharpe | test Sharpe | test ann. |
|---|---:|---:|---:|
| `k24_q10_dollar` | 0.12 | -1.93 | -62.3% |
| `k24_q10_beta` | -0.20 | -1.25 | -40.0% |
| `k24_q20_dollar` | 0.02 | -2.16 | -37.2% |
| `k24_q20_beta` | -0.47 | -1.54 | -25.5% |
| `k72_q10_dollar` | -0.04 | -1.25 | -39.8% |
| `k72_q10_beta` | -0.44 | -0.63 | -19.8% |
| `k72_q20_dollar` | 0.61 | -1.11 | -19.6% |
| `k72_q20_beta` | -0.04 | -0.57 | -9.6% |
| `k168_q10_dollar` | 0.48 | -0.74 | -23.4% |
| `k168_q10_beta` | 0.13 | -0.29 | -9.0% |
| `k168_q20_dollar` | 1.08 | 0.10 | 1.7% |
| `k168_q20_beta` | 0.36 | 0.50 | 8.5% |

### Structural spreads, Hyperliquid minus Binance: same sign in both halves, |mean| at least 5%

| coin | mean (year) | choose half | test half | days beyond ±20% | daily autocorrelation |
|---|---:|---:|---:|---:|---:|
| MAVIA | 105.9% | 41.4% | 446.8% | 45% | 0.93 |
| ZEREBRO | 34.6% | 3.9% | 197.1% | 31% | 0.86 |
| XAI | -18.7% | -25.0% | -12.7% | 43% | 0.10 |
| STBL | 16.6% | 10.9% | 22.0% | 25% | 0.57 |
| ZETA | -14.7% | -17.9% | -11.7% | 35% | 0.32 |
| HYPER | -13.9% | -19.9% | -8.2% | 37% | -0.01 |
| PROVE | -13.7% | -21.2% | -6.6% | 32% | 0.52 |
| AERO | 13.0% | 12.6% | 13.3% | 32% | 0.42 |
| ALT | -13.0% | -12.2% | -13.7% | 31% | -0.03 |
| kNEIRO | -13.0% | -7.1% | -18.5% | 28% | 0.67 |
| ZEC | 12.5% | 16.0% | 9.1% | 20% | 0.55 |
| BABY | -12.3% | -17.4% | -7.5% | 29% | 0.01 |
| INIT | -11.7% | -20.0% | -3.9% | 24% | 0.10 |
| STABLE | -11.7% | -7.4% | -14.2% | 53% | 0.33 |
| HEMI | 11.1% | 7.3% | 14.7% | 30% | 0.46 |
| TON | 11.0% | 8.7% | 16.6% | 10% | 0.56 |
| XMR | 10.8% | 2.6% | 14.1% | 20% | 0.33 |
| ZRO | 10.8% | 11.5% | 10.2% | 23% | 0.51 |
| 2Z | -10.6% | -12.0% | -9.3% | 31% | 0.42 |
| VIRTUAL | 9.9% | 12.2% | 7.7% | 14% | 0.45 |
| WCT | -9.7% | -19.6% | -0.3% | 21% | 0.18 |
| DYM | -9.6% | -17.2% | -2.5% | 34% | 0.03 |
| HMSTR | 9.5% | 13.0% | 6.2% | 17% | 0.49 |
| TAO | 8.8% | 9.5% | 8.2% | 10% | 0.49 |
| S | -8.7% | -5.7% | -11.6% | 23% | 0.50 |
| PROMPT | 8.5% | 2.2% | 41.7% | 30% | 0.69 |
| SCR | -8.3% | -9.0% | -4.7% | 31% | 0.62 |
| IP | 8.3% | 6.7% | 11.5% | 28% | -0.05 |
| kBONK | 8.0% | 4.9% | 11.0% | 12% | 0.41 |
| APE | 7.9% | 10.1% | 5.8% | 14% | 0.23 |

131 of 191 coins have the same sign in both halves; 65 of those at |mean| >= 5%.

### Robustness: both halves on real hourly prices (grid from 2026-03-15, test from 2026-06-01)

| pair | chosen | test deployed return | test reserved Sharpe | test t | top-10 median test deployed | variants over the savings rate |
|---|---|---:|---:|---:|---:|---:|
| hl_binance | `k168_X10_Yzero_Hinf` | 7.6% | 16.68 | 9.90 | 6.0% | 76% |
| hl_bybit | `k168_X50_Yhalf_H168` | -13.4% | -1.36 | -0.72 | 4.9% | 27% |
| binance_bybit | `slow_k30d_X8_Yzero` | 1.9% | 2.14 | 0.96 | 1.2% | 0% |

