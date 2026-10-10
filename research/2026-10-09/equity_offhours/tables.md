# HIP-3 equity perps while the cash market is shut — tables

Generated 2026-10-09T20:55:52Z by `scripts/equity_offhours.py` from `analysis.json`. Sessions 2026-03-17 to 2026-10-08: 143 closed periods, 8802 name-sessions over 110 markets (7001 tradable at the pre-open hour). Costs at a $10,000 clip, fee case `schedule`.

## Price discovery: how much of the cash gap the perp had moved 30 minutes before the open

| subset | name-sessions | sessions | share priced (90% CI) | R² | gap on perp: slope, intercept | mean abs gap | mean abs unpriced |
|---|---|---|---|---|---|---|---|
| all | 8802 | 143 | 0.90 (0.88–0.92) | 0.90 | 1.00, -3.9bp | 174bp | 57bp |
| first_half | 2807 | 71 | 0.91 (0.89–0.93) | 0.90 | 0.99, -7.1bp | 174bp | 58bp |
| holiday | 289 | 5 | 0.92 (0.86–0.99) | 0.86 | 0.97, -14.8bp | 160bp | 61bp |
| overnight | 7020 | 114 | 0.90 (0.87–0.92) | 0.90 | 1.01, -3.0bp | 174bp | 57bp |
| pre_hour_over_100k | 4092 | 143 | 0.92 (0.90–0.94) | 0.93 | 1.01, -1.9bp | 209bp | 55bp |
| pre_hour_under_100k | 4710 | 143 | 0.87 (0.84–0.90) | 0.85 | 0.98, -5.6bp | 144bp | 58bp |
| ref_etf | 1213 | 143 | 0.97 (0.96–0.99) | 0.96 | 0.99, -1.7bp | 151bp | 34bp |
| ref_index | 284 | 143 | 1.01 (0.98–1.04) | 0.97 | 0.96, 0.3bp | 56bp | 11bp |
| ref_stock | 7305 | 143 | 0.90 (0.87–0.92) | 0.90 | 1.00, -4.4bp | 182bp | 62bp |
| second_half | 5995 | 72 | 0.90 (0.87–0.93) | 0.90 | 1.00, -2.3bp | 174bp | 56bp |
| weekend | 1493 | 24 | 0.93 (0.90–0.95) | 0.91 | 0.98, -5.0bp | 176bp | 55bp |

## Discovery curve: share of the gap priced h hours before the open

| hours before open | overnight share (R²) | weekend/holiday share (R²) |
|---|---|---|
| 16.5 | 0.13 (0.13), n=6993 | 0.25 (0.15), n=1715 |
| 13.5 | 0.28 (0.27), n=6881 | 0.36 (0.26), n=1728 |
| 9.5 | 0.41 (0.43), n=6861 | 0.53 (0.49), n=1761 |
| 6.5 | 0.49 (0.51), n=6925 | 0.56 (0.51), n=1762 |
| 4.5 | 0.65 (0.65), n=6925 | 0.69 (0.64), n=1772 |
| 2.5 | 0.70 (0.71), n=6952 | 0.76 (0.72), n=1773 |
| 1.5 | 0.80 (0.80), n=6966 | 0.87 (0.84), n=1776 |
| 0.5 | 0.90 (0.90), n=7020 | 0.93 (0.90), n=1782 |

## The oracle and funding while the market is shut

| measure | closed hours | open hours |
|---|---|---|
| hours | 249846 | 66376 |
| mean abs premium | 9.82bp | 6.07bp |
| share of hours outside the funding dead zone | 68.1% | 60.6% |
| mean funding APR (longs pay +) | 12.32% | 12.23% |

Implied oracle follows the perp while shut: median slope 1.00 over 104 markets with at least ten moves; 100.0% of them above 0.8. Funding formula reproduced on 99.3% of 316222 rows. Funding over a closed period: 3.72bp on average (5.73bp over a weekend), shorts paid in 78.7% of sessions; the gap left at 30 min before the open averaged -3.9bp with a standard deviation of 82bp.

## The perp against the pre-market tape at 09:00 ET (472 name-sessions, 2026-07-17 to 2026-10-08)

Mean absolute distance perp vs pre-market last trade 28.9bp (median 17.3bp). The opening print was 33.6bp from the perp and 44.6bp from the pre-market price on average, closer to the perp in 61% of name-sessions. The gap still open after the perp, regressed on the pre-market's deviation from it: slope 0.07, R² 0.01.

| symbol | n | mean abs perp vs pre-market | open vs perp | open vs pre-market |
|---|---|---|---|---|
| AAPL | 59 | 13.5bp | 22.9bp | 26.0bp |
| AMZN | 59 | 21.0bp | 29.3bp | 36.5bp |
| COIN | 59 | 52.4bp | 51.6bp | 74.6bp |
| META | 59 | 28.7bp | 40.9bp | 48.7bp |
| MSTR | 59 | 63.9bp | 50.0bp | 78.4bp |
| NVDA | 59 | 21.7bp | 26.3bp | 35.8bp |
| SPY | 59 | 9.5bp | 8.1bp | 11.2bp |
| TSLA | 59 | 20.3bp | 39.7bp | 45.8bp |

## Strategies (chosen on the first half of sessions, tested once on the second; 120 variants tried in all)

### open_reaction

| | in sample | out of sample |
|---|---|---|
| chosen | `fade|k=0.01|exit=post|all` | rank 12 of 48 |
| sessions | 72 | 71 |
| annual return on deployed notional | 54.5% | -1.0% |
| Sharpe | 2.76 | -0.05 |
| active sessions | 100.0% | 100.0% |
| trades | 1074 | 1645 |

Out of sample: Newey–West t -0.03 (p 0.980); bootstrap 95% interval of the mean session return -29.4 to 32.3 bp; deflated Sharpe of the in-sample choice against all 120 variants 0.134; BH survivors on the full sample: none. At the depth within 25bp on both legs: $15,316 a year (median size $127,859, 777 trades sized).


| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |
|---|---|---|---|---|
| `fade|k=0.02|exit=post|all` | 38.6% | 1.42 | 10.2% | 0.35 |
| `fade|k=0.01|exit=post|all` | 26.9% | 1.27 | -1.0% | -0.05 |
| `fade|k=0|exit=post|all` | 13.6% | 0.93 | -5.7% | -0.40 |
| `fade|k=0.005|exit=post|all` | 15.9% | 0.90 | -1.0% | -0.06 |
| `fade|k=0.02|exit=close1|closed_long` | 11.5% | 0.65 | 21.0% | 1.25 |
| `fade|k=0.01|exit=close1|closed_long` | 6.8% | 0.51 | 2.4% | 0.20 |
| `fade|k=0|exit=post|closed_long` | 2.8% | 0.48 | -2.7% | -0.52 |
| `follow|k=0.02|exit=post2|closed_long` | 4.7% | 0.29 | -4.0% | -0.22 |

### open_reaction_hedged

| | in sample | out of sample |
|---|---|---|
| chosen | `hedged|follow|k=0.02|exit=post2|closed_long` | rank 19 of 48 |
| sessions | 72 | 71 |
| annual return on deployed notional | 34.8% | -13.9% |
| Sharpe | 2.38 | -0.74 |
| active sessions | 20.8% | 19.7% |
| trades | 107 | 151 |

Out of sample: Newey–West t -0.39 (p 0.694); bootstrap 95% interval of the mean session return -34.0 to 22.6 bp; deflated Sharpe of the in-sample choice against all 120 variants 0.088; BH survivors on the full sample: none. At the depth within 25bp on both legs: $134,243 a year (median size $146,189, 60 trades sized).


| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |
|---|---|---|---|---|
| `hedged|fade|k=0.02|exit=post|all` | 18.6% | 0.68 | 16.6% | 0.54 |
| `hedged|follow|k=0.02|exit=post2|closed_long` | 10.6% | 0.63 | -13.9% | -0.74 |
| `hedged|fade|k=0.005|exit=close1|closed_long` | 6.0% | 0.62 | 11.2% | 1.30 |
| `hedged|fade|k=0.01|exit=close1|closed_long` | 3.0% | 0.25 | 7.4% | 0.79 |
| `hedged|fade|k=0.005|exit=post|closed_long` | -0.1% | -0.02 | -2.7% | -0.49 |
| `hedged|follow|k=0.01|exit=post2|closed_long` | -0.6% | -0.06 | -4.0% | -0.38 |
| `hedged|fade|k=0.005|exit=post2|closed_long` | -0.9% | -0.11 | 4.0% | 0.44 |
| `hedged|fade|k=0.02|exit=post|closed_long` | -1.9% | -0.14 | 6.9% | 0.44 |

### crypto_vs_btc

| | in sample | out of sample |
|---|---|---|
| chosen | `crypto|residual|follow|k=0.02` | rank 7 of 8 |
| sessions | 72 | 71 |
| annual return on deployed notional | 66.7% | -77.9% |
| Sharpe | 2.23 | -2.91 |
| active sessions | 38.9% | 43.7% |
| trades | 41 | 48 |

Out of sample: Newey–West t -1.93 (p 0.054); bootstrap 95% interval of the mean session return -62.0 to -0.1 bp; deflated Sharpe of the in-sample choice against all 120 variants 0.080; BH survivors on the full sample: none. At the depth within 25bp on both legs: $-55,361 a year (median size $152,077, 15 trades sized).


| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |
|---|---|---|---|---|
| `crypto|residual|follow|k=0.02` | -5.1% | -0.18 | -77.9% | -2.91 |
| `crypto|btc|fade|k=0.02` | -3.6% | -0.19 | -30.9% | -2.31 |
| `crypto|btc|follow|k=0` | -12.4% | -0.37 | 63.2% | 2.29 |
| `crypto|btc|follow|k=0.02` | -11.0% | -0.57 | 15.7% | 1.20 |
| `crypto|residual|fade|k=0` | -16.6% | -0.58 | -57.6% | -2.53 |
| `crypto|residual|fade|k=0.02` | -17.9% | -0.62 | 49.0% | 1.83 |
| `crypto|btc|fade|k=0` | -42.2% | -1.25 | -124.3% | -4.49 |
| `crypto|residual|follow|k=0` | -38.1% | -1.34 | -3.5% | -0.15 |

### carry

| | in sample | out of sample |
|---|---|---|
| chosen | `carry|top10|vol>=2M` | rank 5 of 6 |
| sessions | 72 | 72 |
| annual return on deployed notional | 3.6% | 1.6% |
| Sharpe | 5.10 | 2.13 |
| active sessions | 70.8% | 100.0% |
| rebalances | 4 | 3 |

Out of sample: Newey–West t 1.32 (p 0.187); bootstrap 95% interval of the mean session return -0.4 to 1.5 bp; deflated Sharpe of the in-sample choice against all 120 variants 0.569; BH survivors on the full sample: `carry|all|vol>=0.5M`, `carry|trail_8pct|vol>=0.5M`, `carry|top10|vol>=0.5M`, `carry|all|vol>=2M`, `carry|trail_8pct|vol>=2M`, `carry|top10|vol>=2M`. Sized at 5% of each basket name's open interest: $13,490,217 notional, $20,235,325 of capital, $330,450 a year over the savings rate; latest basket xyz:ARM, xyz:AVGO, xyz:BABA, xyz:BE, xyz:COIN, xyz:CRCL, xyz:HOOD, xyz:LLY, xyz:MSTR, xyz:RKLB.

In sample (from 2026-03-16): funding 12.2% a year per notional, P&L 13.8%, rebalancing 0.38%, 9.9 names held on average over 51 active days.
Out of sample (2026-06-29 to 2026-10-08): funding 9.9% a year per notional, P&L 8.7%, rebalancing 0.54%, 9.8 names held on average over 72 active days.

| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |
|---|---|---|---|---|
| `carry|trail_8pct|vol>=0.5M` | 4.4% | 4.28 | 2.8% | 5.10 |
| `carry|trail_8pct|vol>=2M` | 2.7% | 4.18 | 1.9% | 3.57 |
| `carry|all|vol>=0.5M` | 2.0% | 3.86 | 1.1% | 2.67 |
| `carry|top10|vol>=0.5M` | 4.5% | 3.75 | 3.5% | 2.79 |
| `carry|top10|vol>=2M` | 2.6% | 3.53 | 1.6% | 2.13 |
| `carry|all|vol>=2M` | 1.4% | 3.10 | 0.6% | 1.29 |

### carry_all_marks

| | in sample | out of sample |
|---|---|---|
| chosen | `carry|trail_8pct|vol>=2M` | rank 1 of 6 |
| sessions | 124 | 124 |
| annual return on deployed notional | 1.2% | 3.4% |
| Sharpe | 0.23 | 4.75 |
| active sessions | 83.1% | 100.0% |
| rebalances | 6 | 6 |

Out of sample: Newey–West t 4.06 (p 0.000); bootstrap 95% interval of the mean session return 0.7 to 2.0 bp; deflated Sharpe of the in-sample choice against all 120 variants 0.008; BH survivors on the full sample: none. Sized at 5% of each basket name's open interest: $13,490,217 notional, $20,235,325 of capital, $678,878 a year over the savings rate; latest basket xyz:ARM, xyz:AVGO, xyz:BABA, xyz:BE, xyz:COIN, xyz:CRCL, xyz:HOOD, xyz:LLY, xyz:MSTR, xyz:RKLB.

In sample (from 2025-10-14): funding 6.4% a year per notional, P&L 8.2%, rebalancing 0.24%, 6.6 names held on average over 103 active days.
Out of sample (2026-04-14 to 2026-10-08): funding 10.9% a year per notional, P&L 11.2%, rebalancing 0.43%, 17.4 names held on average over 124 active days.

| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |
|---|---|---|---|---|
| `carry|trail_8pct|vol>=0.5M` | 2.8% | 0.70 | 4.8% | 4.33 |
| `carry|top10|vol>=0.5M` | 2.8% | 0.64 | 4.7% | 3.40 |
| `carry|trail_8pct|vol>=2M` | 2.3% | 0.59 | 3.4% | 4.75 |
| `carry|top10|vol>=2M` | 2.1% | 0.52 | 3.0% | 4.37 |
| `carry|all|vol>=0.5M` | 1.5% | 0.38 | 2.3% | 4.07 |
| `carry|all|vol>=2M` | 1.4% | 0.36 | 1.7% | 3.61 |

### pairs

| | in sample | out of sample |
|---|---|---|
| chosen | `pairs|diff>=0.05` | rank 1 of 2 |
| sessions | 44 | 44 |
| annual return on deployed notional | -0.4% | 8.4% |
| Sharpe | -2.31 | 1.39 |
| active sessions | 4.5% | 100.0% |
| rebalances | 0 | 5 |

Out of sample: Newey–West t 0.73 (p 0.467); bootstrap 95% interval of the mean session return -5.2 to 14.2 bp; deflated Sharpe of the in-sample choice against all 120 variants 0.000; BH survivors on the full sample: none. Sized at 5% of each basket name's open interest: $476,572 notional, $319,303 of capital, $26,727 a year over the savings rate; latest basket -para:IREN/xyz:IREN, -para:NET/xyz:NET, io:NBIS/xyz:NBIS, para:AAOI/xyz:AAOI, para:AVGO/xyz:AVGO, para:RDDT/xyz:RDDT.


| variant | full-sample annual | full-sample Sharpe | out-of-sample annual | out-of-sample Sharpe |
|---|---|---|---|---|
| `pairs|diff>=0.05` | 4.0% | 0.93 | 8.4% | 1.39 |
| `pairs|diff>=0` | 0.1% | 0.04 | 1.5% | 0.65 |

### funding persistence (funding rows only, back to listing)

At 8 monthly rebalances the rank correlation between each name's trailing-30-session and next-21-session funding averaged 0.38 (positive at 100% of them); names that had paid at least 8% went on to pay 9.7% a year over the next 21 sessions (worst rebalance -0.0%) against 6.9% for all names.

| rebalance | names | rank corr | selected | forward APR selected | forward APR all |
|---|---|---|---|---|---|
| 2026-01-14 | 16 | 0.14 | 11 | 5.2% | 4.6% |
| 2026-02-13 | 18 | 0.27 | 9 | 6.7% | 5.3% |
| 2026-03-17 | 24 | 0.25 | 11 | -0.0% | -0.7% |
| 2026-04-16 | 26 | 0.33 | 4 | 19.2% | 10.5% |
| 2026-05-15 | 31 | 0.71 | 13 | 16.1% | 11.6% |
| 2026-06-16 | 42 | 0.41 | 33 | 13.4% | 10.7% |
| 2026-07-17 | 55 | 0.42 | 37 | 8.0% | 6.0% |
| 2026-08-17 | 66 | 0.49 | 36 | 9.3% | 6.8% |

### dividend

23 ex-dividend opens on 10 names; mean dividend 25.3bp; shorting 30 min before the open and covering 30 min after netted 25.3bp raw and 38.1bp index-hedged per event (first half 61.4bp, second half 16.8bp; t 1.01); the perp had moved a median 1.08 of the dividend before the open.

## Per market (sessions >= 20)

| market | ref | sessions | share priced | R² | mean abs unpriced | median pre-open hour notional | oracle follow slope |
|---|---|---|---|---|---|---|---|
| xyz:AAPL | AAPL | 143 | 0.83 | 0.90 | 24bp | $308,722 | 1.01 |
| xyz:AMD | AMD | 143 | 0.92 | 0.93 | 61bp | $399,034 | 1.00 |
| xyz:AMZN | AMZN | 143 | 0.87 | 0.93 | 33bp | $303,900 | 1.00 |
| xyz:BABA | BABA | 143 | 0.98 | 0.97 | 30bp | $48,147 | 1.00 |
| xyz:COIN | COIN | 143 | 0.87 | 0.90 | 63bp | $213,394 | 1.00 |
| xyz:CRCL | CRCL | 143 | 0.87 | 0.90 | 71bp | $876,789 | 1.00 |
| xyz:CRWV | CRWV | 143 | 0.93 | 0.93 | 76bp | $164,063 | 1.00 |
| xyz:EWJ | EWJ | 143 | 0.98 | 0.95 | 21bp | $13,286 | 1.00 |
| xyz:EWY | EWY | 143 | 0.97 | 0.98 | 31bp | $649,127 | 1.00 |
| xyz:GOOGL | GOOGL | 143 | 0.88 | 0.91 | 30bp | $515,680 | 1.00 |
| xyz:HOOD | HOOD | 143 | 0.92 | 0.90 | 66bp | $364,659 | 1.00 |
| xyz:INTC | INTC | 143 | 0.93 | 0.92 | 70bp | $1,154,799 | 1.00 |
| xyz:META | META | 143 | 0.91 | 0.93 | 38bp | $397,679 | 1.00 |
| xyz:MSFT | MSFT | 143 | 0.81 | 0.89 | 37bp | $374,747 | 1.00 |
| xyz:MSTR | MSTR | 143 | 0.93 | 0.94 | 59bp | $464,265 | 1.00 |
| xyz:MU | MU | 143 | 0.93 | 0.97 | 58bp | $3,812,865 | 1.00 |
| xyz:NFLX | NFLX | 143 | 0.84 | 0.93 | 37bp | $30,355 | 1.00 |
| xyz:NVDA | NVDA | 143 | 0.93 | 0.94 | 27bp | $1,614,387 | 1.00 |
| xyz:ORCL | ORCL | 143 | 0.89 | 0.91 | 55bp | $213,222 | 1.00 |
| xyz:PLTR | PLTR | 143 | 0.95 | 0.91 | 46bp | $157,025 | 1.00 |
| xyz:SNDK | SNDK | 143 | 0.87 | 0.95 | 78bp | $2,949,507 | 1.00 |
| xyz:TSLA | TSLA | 143 | 0.86 | 0.91 | 35bp | $629,370 | 1.00 |
| xyz:TSM | TSM | 143 | 0.94 | 0.96 | 30bp | $78,392 | 1.00 |
| xyz:URNM | URNM | 143 | 0.93 | 0.88 | 42bp | $5,576 | 0.99 |
| xyz:USAR | USAR | 143 | 0.84 | 0.83 | 92bp | $26,172 | 1.00 |
| xyz:XYZ100 | QQQ | 143 | 1.01 | 0.97 | 13bp | $10,969,785 | 1.00 |
| xyz:SP500 | SPY | 141 | 1.01 | 0.96 | 8bp | $10,629,490 | 1.00 |
| xyz:LLY | LLY | 136 | 0.70 | 0.74 | 48bp | $14,574 | 0.97 |
| xyz:HIMS | HIMS | 135 | 0.82 | 0.74 | 87bp | $18,022 | 0.99 |
| xyz:COST | COST | 132 | 0.68 | 0.67 | 33bp | $1,822 | 0.97 |
| xyz:DKNG | DKNG | 129 | 0.71 | 0.54 | 72bp | $1,408 | 0.98 |
| xyz:BIRD | BIRD | 120 | 0.75 | 0.68 | 131bp | $1,701 | 0.97 |
| xyz:GME | GME | 109 | 0.86 | 0.90 | 38bp | $9,639 | 0.98 |
| xyz:LITE | LITE | 109 | 0.93 | 0.90 | 81bp | $126,321 | 1.00 |
| xyz:MRVL | MRVL | 109 | 0.96 | 0.93 | 80bp | $715,817 | 1.00 |
| xyz:EWZ | EWZ | 108 | 0.92 | 0.86 | 47bp | $8,258 | 1.01 |
| xyz:RKLB | RKLB | 108 | 0.93 | 0.89 | 72bp | $119,141 | 0.99 |
| xyz:XLE | XLE | 108 | 0.91 | 0.83 | 34bp | $8,130 | 0.94 |
| xyz:EBAY | EBAY | 107 | 0.41 | 0.22 | 62bp | $1,334 | 0.95 |
| xyz:ZM | ZM | 107 | 0.70 | 0.78 | 58bp | $3,410 | 0.99 |
| xyz:BX | BX | 104 | 0.72 | 0.59 | 57bp | $3,581 | 0.98 |
| xyz:CBRS | CBRS | 101 | 0.93 | 0.90 | 85bp | $377,431 | 1.00 |
| xyz:ARM | ARM | 96 | 0.87 | 0.93 | 88bp | $141,917 | 0.99 |
| xyz:EWT | EWT | 95 | 0.96 | 0.98 | 22bp | $3,704 | 1.01 |
| xyz:BB | BB | 94 | 0.92 | 0.78 | 78bp | $129,538 | 0.98 |
| xyz:ASML | ASML | 91 | 0.93 | 0.93 | 48bp | $23,084 | 1.00 |
| xyz:DELL | DELL | 90 | 0.86 | 0.87 | 68bp | $64,695 | 1.00 |
| xyz:IBM | IBM | 90 | 0.99 | 0.96 | 42bp | $25,527 | 1.01 |
| xyz:AVGO | AVGO | 88 | 0.95 | 0.94 | 46bp | $61,673 | 1.00 |
| xyz:NOW | NOW | 87 | 0.94 | 0.91 | 57bp | $14,657 | 1.00 |
| xyz:QNT | QNT | 87 | 0.85 | 0.79 | 84bp | $27,533 | 0.99 |
| xyz:NBIS | NBIS | 84 | 0.87 | 0.92 | 92bp | $479,930 | 1.00 |
| xyz:WDC | WDC | 83 | 0.93 | 0.93 | 94bp | $74,675 | 1.00 |
| xyz:SPCX | SPCX | 81 | 0.98 | 0.92 | 49bp | $5,955,187 | 1.00 |
| xyz:NOK | NOK | 80 | 0.89 | 0.93 | 62bp | $33,412 | 1.00 |
| xyz:SMH | SMH | 80 | 0.95 | 0.97 | 32bp | $19,566 | 0.99 |
| xyz:BE | BE | 76 | 0.84 | 0.91 | 97bp | $102,611 | 1.00 |
| xyz:QCOM | QCOM | 76 | 0.91 | 0.94 | 48bp | $33,840 | 0.99 |
| xyz:STRC | STRC | 75 | 0.89 | 0.92 | 23bp | $31,046 | 0.93 |
| para:AVGO | AVGO | 71 | 0.95 | 0.92 | 56bp | $609 | 0.99 |
| xyz:AMAT | AMAT | 71 | 0.88 | 0.90 | 85bp | $39,599 | 1.00 |
| mkts:US500 | SPY | 69 | 0.94 | 0.95 | 8bp | $156,928 | 1.01 |
| mkts:USTECH | QQQ | 69 | 0.96 | 0.96 | 13bp | $155,906 | 1.01 |
| xyz:RIVN | RIVN | 69 | 0.82 | 0.89 | 57bp | $5,108 | 1.00 |
| xyz:SHAZ | SHAZ | 67 | 0.84 | 0.86 | 110bp | $13,567 | 1.00 |
| xyz:SKHY | SKHY | 63 | 0.92 | 0.96 | 63bp | $2,674,954 | 1.00 |
| para:CRDO | CRDO | 57 | 0.96 | 0.90 | 83bp | $3,590 | 1.00 |
| para:COHR | COHR | 55 | 0.83 | 0.92 | 83bp | $3,075 | 1.00 |
| para:IREN | IREN | 53 | 0.86 | 0.86 | 99bp | $1,222 | 1.00 |
| para:STX | STX | 49 | 0.76 | 0.83 | 108bp | $451 | 1.00 |
| para:GLW | GLW | 47 | 0.92 | 0.88 | 95bp | $905 | 1.00 |
| para:AAOI | AAOI | 46 | 0.92 | 0.90 | 112bp | $1,196 | 1.01 |
| para:LRCX | LRCX | 46 | 0.97 | 0.84 | 108bp | $1,301 | 0.99 |
| xyz:KORU | KORU | 45 | 0.98 | 0.99 | 63bp | $427,677 | 1.01 |
| xyz:GEV | GEV | 44 | 0.94 | 0.91 | 46bp | $1,803 | 1.00 |
| xyz:NCLD | NCLD | 44 | 0.93 | 0.93 | 70bp | $2,416 | 1.01 |
| xyz:SOXL | SOXL | 44 | 1.02 | 0.96 | 91bp | $869,266 | 1.00 |
| para:RDDT | RDDT | 42 | 0.88 | 0.86 | 64bp | $281 | 0.95 |
| para:CRWD | CRWD | 40 | 0.87 | 0.85 | 71bp | $321 | 0.99 |
| para:VST | VST | 39 | 0.97 | 0.88 | 42bp | $2,668 | 1.00 |
| xyz:AAOI | AAOI | 36 | 1.01 | 0.92 | 80bp | $28,473 | 1.00 |
| xyz:IREN | IREN | 36 | 0.88 | 0.87 | 74bp | $23,871 | 1.00 |
| xyz:NET | NET | 36 | 0.78 | 0.73 | 59bp | $2,594 | 1.03 |
| xyz:RDDT | RDDT | 36 | 0.77 | 0.66 | 57bp | $4,917 | 0.97 |
| io:SNDK | SNDK | 35 | 0.92 | 0.94 | 48bp | $951,832 | 0.99 |
| para:NET | NET | 35 | 1.13 | 0.88 | 91bp | $419 | 1.01 |
| xyz:CRWD | CRWD | 35 | 0.87 | 0.87 | 65bp | $24,764 | 1.01 |
| xyz:MRNA | MRNA | 35 | 0.74 | 0.82 | 83bp | $212,892 | 1.00 |
| para:TER | TER | 33 | 0.90 | 0.84 | 118bp | $222 | 1.00 |
| mkts:SMALL2000 | IWM | 30 | 1.01 | 0.91 | 16bp | $5,895 | 1.01 |
| mkts:USBOND | TLT | 29 | 0.83 | 0.79 | 18bp | $14,588 | 1.01 |
| io:NBIS | NBIS | 28 | 0.95 | 0.93 | 64bp | $154,423 | 1.00 |
| xyz:XBI | XBI | 28 | 0.82 | 0.62 | 39bp | $170 | 1.00 |
| xyz:BMNR | BMNR | 23 | 0.98 | 0.93 | 59bp | $19,979 | 0.99 |
| para:TTWO | TTWO | 22 | 0.82 | 0.53 | 32bp | $496 | 1.35 |
| para:SMCI | SMCI | 21 | 0.92 | 0.81 | 69bp | $173 | 1.00 |
| io:IONQ | IONQ | 20 | 0.83 | 0.94 | 73bp | $6,143 | 0.99 |

## Same-underlying builder pairs (short the first, long the second; close to close)

| pair | days | funding difference APR | pair P&L APR | spread sd | same-sign days | round trip | open interest |
|---|---|---|---|---|---|---|---|
| para:AVGO/xyz:AVGO | 54 | 23.0% | 24.0% | 29.4bp | 67% | 38.3bp | $0.5M / $12.7M |
| io:NBIS/xyz:NBIS | 28 | 18.3% | 18.1% | 7.8bp | 89% | 25.0bp | $8.3M / $29.5M |
| para:AAOI/xyz:AAOI | 32 | 13.8% | 29.3% | 37.9bp | 56% | 60.0bp | $0.2M / $2.3M |
| para:IREN/xyz:IREN | 36 | -5.0% | -4.9% | 73.0bp | 67% | 60.0bp | $0.4M / $4.4M |
| para:NET/xyz:NET | 22 | -3.6% | -2.2% | 36.0bp | 68% | 60.0bp | $0.1M / $0.6M |
| mkts:USTECH/xyz:XYZ100 | 69 | -3.3% | -3.3% | 0.1bp | 81% | 8.4bp | $4.9M / $201.2M |
| mkts:US500/xyz:SP500 | 69 | 1.9% | 1.9% | 0.7bp | 64% | 7.5bp | $1.9M / $377.1M |
| io:SNDK/xyz:SNDK | 35 | -1.1% | -1.2% | 4.9bp | 74% | 12.5bp | $4.6M / $122.3M |
| para:CRWD/xyz:CRWD | 35 | 0.7% | -4.1% | 23.9bp | 60% | 60.0bp | $0.1M / $2.0M |
| para:RDDT/xyz:RDDT | 36 | -0.0% | 2.7% | 20.8bp | 50% | 60.0bp | $0.1M / $0.6M |

## Hedged funding carry per market (short perp, long stock; close to close)

| market | days | funding APR | carry P&L APR | basis sd | daily P&L sd | funding > 0 days | open interest |
|---|---|---|---|---|---|---|---|
| xyz:SP500 | 141 | -1.3% | -1.7% | 7.4bp | 6.7bp | 48% | $377.1M |
| xyz:XYZ100 | 248 | 5.3% | 5.7% | 18.9bp | 28.0bp | 80% | $201.2M |
| xyz:SKHY | 63 | -6.4% | -4.6% | 11.5bp | 19.6bp | 25% | $141.4M |
| xyz:SPCX | 81 | 4.5% | 5.5% | 10.8bp | 15.6bp | 62% | $126.5M |
| xyz:CRCL | 202 | 10.7% | 14.6% | 60.3bp | 84.8bp | 91% | $123.4M |
| xyz:SNDK | 180 | 8.4% | 17.6% | 48.9bp | 55.6bp | 80% | $122.3M |
| xyz:MU | 200 | 13.1% | 14.9% | 45.9bp | 73.7bp | 92% | $113.4M |
| xyz:NVDA | 225 | 10.6% | 10.3% | 41.0bp | 61.5bp | 93% | $110.3M |
| xyz:CBRS | 101 | -9.0% | -8.6% | 10.5bp | 17.4bp | 24% | $101.3M |
| xyz:GOOGL | 222 | 10.8% | 12.6% | 22.7bp | 30.6bp | 95% | $99.1M |
| xyz:INTC | 212 | 13.8% | 13.1% | 40.7bp | 59.4bp | 94% | $54.9M |
| xyz:META | 220 | 7.3% | 7.7% | 26.5bp | 41.1bp | 91% | $52.9M |
| xyz:MSTR | 212 | 8.0% | 8.4% | 59.7bp | 92.3bp | 81% | $45.1M |
| xyz:TSLA | 225 | 6.6% | 6.1% | 42.9bp | 61.0bp | 86% | $43.8M |
| xyz:AMZN | 222 | 8.9% | 10.2% | 26.6bp | 41.1bp | 94% | $37.9M |
| xyz:AAPL | 219 | 2.3% | 2.8% | 24.9bp | 34.4bp | 68% | $33.4M |
| xyz:NBIS | 84 | 16.9% | 16.1% | 11.3bp | 18.1bp | 94% | $29.5M |
| xyz:HOOD | 216 | 9.8% | 10.3% | 48.5bp | 70.5bp | 93% | $29.4M |
| xyz:MSFT | 221 | 7.5% | 7.8% | 26.6bp | 36.6bp | 91% | $22.9M |
| xyz:ORCL | 208 | 9.2% | 8.6% | 42.3bp | 65.0bp | 91% | $22.1M |
| xyz:AMD | 211 | 5.6% | 5.6% | 38.2bp | 58.4bp | 88% | $19.2M |
| xyz:SOXL | 44 | 6.6% | 5.8% | 10.6bp | 15.3bp | 84% | $18.3M |
| xyz:COIN | 215 | 5.1% | -0.6% | 48.9bp | 70.6bp | 89% | $18.2M |
| xyz:PLTR | 224 | 2.6% | 3.5% | 47.0bp | 70.0bp | 65% | $15.8M |
| xyz:RKLB | 108 | 20.1% | 20.1% | 10.4bp | 20.7bp | 99% | $12.9M |
| xyz:AVGO | 88 | 11.1% | 13.4% | 10.4bp | 16.8bp | 95% | $12.7M |
| xyz:BABA | 183 | 9.9% | 10.3% | 21.4bp | 29.6bp | 93% | $12.0M |
| xyz:STRC | 75 | -6.7% | 6.1% | 17.2bp | 26.1bp | 28% | $11.9M |
| xyz:BB | 94 | 22.4% | 21.7% | 22.1bp | 35.7bp | 82% | $11.1M |
| xyz:MRVL | 109 | 20.0% | 20.4% | 10.4bp | 15.6bp | 98% | $10.9M |
| io:NBIS | 28 | 26.4% | 25.8% | 7.6bp | 10.7bp | 96% | $8.3M |
| xyz:DELL | 90 | 5.2% | 5.1% | 18.0bp | 25.0bp | 62% | $7.8M |
| xyz:CRWV | 172 | 8.1% | 6.0% | 51.6bp | 83.3bp | 80% | $7.7M |
| xyz:TSM | 171 | 6.7% | 4.7% | 25.5bp | 41.3bp | 86% | $7.6M |
| xyz:KORU | 45 | -0.5% | 1.3% | 13.3bp | 22.9bp | 49% | $7.4M |
| xyz:EWY | 153 | 6.0% | 7.4% | 27.9bp | 41.7bp | 77% | $7.2M |
| xyz:NFLX | 209 | 6.9% | 6.8% | 25.9bp | 41.0bp | 92% | $6.9M |
| xyz:LITE | 109 | 17.6% | 22.3% | 11.3bp | 29.9bp | 92% | $6.6M |
| xyz:ARM | 96 | 8.8% | 7.5% | 15.3bp | 25.2bp | 86% | $5.6M |
| xyz:BE | 76 | 13.2% | 15.0% | 19.5bp | 26.3bp | 82% | $5.4M |
| xyz:QCOM | 76 | 15.7% | 17.5% | 15.6bp | 24.3bp | 99% | $5.1M |
| xyz:LLY | 135 | 17.4% | 17.9% | 17.2bp | 26.8bp | 90% | $5.1M |
| mkts:USTECH | 69 | 1.0% | 1.3% | 5.7bp | 8.4bp | 61% | $4.9M |
| io:SNDK | 35 | 4.6% | 5.0% | 6.5bp | 8.6bp | 77% | $4.6M |
| xyz:WDC | 82 | 8.4% | 7.3% | 10.0bp | 18.7bp | 88% | $4.6M |
| xyz:MRNA | 35 | 5.6% | 6.2% | 7.8bp | 13.6bp | 80% | $4.5M |
| xyz:IREN | 36 | 19.7% | 18.2% | 10.8bp | 17.5bp | 97% | $4.4M |
| mkts:USBOND | 27 | 4.2% | 4.4% | 12.2bp | 17.0bp | 59% | $3.5M |
| xyz:HIMS | 136 | 21.6% | 20.3% | 26.7bp | 47.1bp | 82% | $3.2M |
| xyz:USAR | 175 | 13.4% | 11.5% | 51.1bp | 80.2bp | 83% | $3.1M |
| xyz:GME | 109 | 28.8% | 30.1% | 13.8bp | 27.1bp | 90% | $3.1M |
| xyz:SMH | 80 | 14.8% | 16.0% | 15.9bp | 23.3bp | 72% | $2.7M |
| xyz:BMNR | 23 | 38.9% | 28.3% | 23.9bp | 40.4bp | 100% | $2.7M |
| xyz:AAOI | 36 | 13.3% | 15.2% | 13.4bp | 19.3bp | 94% | $2.3M |
| para:VST | 41 | 61.7% | 69.5% | 27.0bp | 49.8bp | 95% | $2.2M |
| xyz:ASML | 91 | 15.9% | 17.8% | 11.9bp | 24.7bp | 89% | $2.1M |
| xyz:CRWD | 35 | 0.0% | 1.0% | 13.1bp | 19.7bp | 46% | $2.0M |
| xyz:URNM | 174 | 27.5% | 29.2% | 42.0bp | 68.4bp | 67% | $2.0M |
| xyz:IBM | 90 | 8.5% | 8.5% | 12.7bp | 16.9bp | 86% | $2.0M |
| xyz:NOW | 87 | 15.5% | 14.6% | 13.3bp | 19.0bp | 99% | $2.0M |
| mkts:US500 | 69 | 2.6% | 2.7% | 4.3bp | 5.7bp | 77% | $1.9M |
| xyz:EWZ | 102 | 5.1% | 4.8% | 15.9bp | 29.3bp | 56% | $1.8M |
| xyz:NOK | 80 | 16.6% | 17.3% | 18.5bp | 24.5bp | 84% | $1.6M |
| xyz:AMAT | 71 | 9.8% | 12.1% | 12.8bp | 19.1bp | 85% | $1.5M |
| xyz:RIVN | 69 | 8.3% | 8.9% | 21.1bp | 28.9bp | 77% | $1.4M |
| xyz:QNT | 87 | 10.9% | 11.7% | 30.3bp | 47.6bp | 68% | $1.3M |
| xyz:XLE | 109 | 17.3% | 16.9% | 21.1bp | 38.2bp | 73% | $1.1M |
| xyz:EWJ | 153 | 0.4% | 0.6% | 11.4bp | 23.4bp | 70% | $0.9M |
| xyz:SHAZ | 67 | 23.0% | 23.5% | 19.9bp | 35.9bp | 63% | $0.9M |
| mkts:SMALL2000 | 25 | -13.5% | -11.8% | 10.9bp | 20.0bp | 72% | $0.8M |
| para:CRDO | 50 | 30.0% | 32.5% | 37.9bp | 56.2bp | 86% | $0.7M |
| xyz:RDDT | 36 | 11.3% | 9.3% | 18.8bp | 31.5bp | 69% | $0.6M |
| xyz:EWT | 96 | 3.8% | 3.9% | 17.0bp | 28.7bp | 56% | $0.6M |
| xyz:NET | 36 | 23.1% | 24.3% | 16.5bp | 20.7bp | 67% | $0.6M |
| xyz:ZM | 107 | 16.6% | 17.4% | 16.3bp | 37.3bp | 64% | $0.6M |
| para:COHR | 53 | 21.0% | 16.4% | 42.6bp | 62.1bp | 85% | $0.6M |
| para:AVGO | 62 | 39.3% | 38.1% | 29.1bp | 45.4bp | 81% | $0.5M |
| xyz:BX | 102 | 16.6% | 18.3% | 30.8bp | 40.2bp | 56% | $0.5M |
| xyz:DKNG | 120 | 2.4% | 2.3% | 31.5bp | 59.7bp | 56% | $0.5M |
| xyz:COST | 131 | 8.8% | 9.5% | 15.2bp | 31.2bp | 70% | $0.5M |
| para:GLW | 41 | 20.0% | 26.9% | 75.6bp | 98.6bp | 88% | $0.4M |
| para:IREN | 54 | 21.9% | 28.9% | 81.1bp | 107.5bp | 96% | $0.4M |
| para:STX | 49 | 5.1% | 3.7% | 41.0bp | 63.2bp | 65% | $0.4M |
| xyz:NCLD | 44 | 49.5% | 55.8% | 18.0bp | 61.0bp | 68% | $0.4M |
| para:LRCX | 36 | 13.8% | 3.1% | 64.8bp | 88.1bp | 89% | $0.4M |
| para:SMCI | 27 | 22.7% | 27.8% | 69.9bp | 104.2bp | 96% | $0.3M |
| xyz:GEV | 45 | 30.2% | 35.3% | 22.8bp | 38.9bp | 84% | $0.2M |
| xyz:EBAY | 108 | 14.9% | 17.0% | 31.3bp | 56.7bp | 65% | $0.2M |
| para:AAOI | 45 | 34.4% | 45.8% | 49.9bp | 83.0bp | 96% | $0.2M |
| para:TER | 27 | 9.9% | -3.6% | 74.0bp | 108.8bp | 63% | $0.1M |
| para:NET | 31 | 17.2% | 26.2% | 40.5bp | 69.0bp | 48% | $0.1M |
| xyz:XBI | 29 | 27.5% | 31.6% | 22.4bp | 40.1bp | 69% | $0.1M |
| io:IONQ | 20 | 29.2% | 40.6% | 27.7bp | 35.6bp | 100% | $0.1M |
| para:CRWD | 37 | 2.2% | -6.9% | 23.6bp | 37.1bp | 70% | $0.1M |
| para:RDDT | 43 | 16.1% | 12.0% | 22.0bp | 39.8bp | 63% | $0.1M |
| xyz:BIRD | 119 | 49.4% | 81.1% | 71.8bp | 159.3bp | 61% | $0.1M |
