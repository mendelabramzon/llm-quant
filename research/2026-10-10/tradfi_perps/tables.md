# Binance TradFi perps vs HIP-3 — tables (generated 2026-10-10T11:54:54Z)

## 1. Binance TradFi funding

Formula (h/8) x [P + clamp(I - P, +-0.05%)], capped per symbol; I = 0 after the launch months. Reproduced from hourly premium-index bars: 73.0% of 77471 settlements within 0.5bp, 80.2% within 1bp; the zero/non-zero call agrees on 86.9%. 68.5% of settlements are exactly zero. Implied clamp median 0.056% (IQR 0.046%–0.071%, n 23043).

Months with the interest leg on: 2025-12 (XAUUSDT), 2026-01 (XAGUSDT, XAUUSDT), 2026-02 (HOODUSDT, INTCUSDT)

| class | symbols | median APR since listing | hour-weighted | US session | weekday off-hours | weekend | last 90d median | zero settlements (median) | negative | symbols >= 8% | >= 5.7% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CN_EQUITY | 2 | -48.9% | -48.9% | -6.3% | -95.2% | -23.2% | -48.9% | 64% | 23% | 0 | 0 |
| COMMODITY | 8 | 15.1% | 11.5% | 7.1% | 8.7% | 16.3% | 8.5% | 53% | 5% | 6 | 6 |
| EQUITY | 178 | 4.2% | 4.3% | 6.6% | 5.8% | 1.6% | 2.8% | 77% | 4% | 54 | 71 |
| FX | 1 | 16.3% | 16.3% | 29.1% | 19.6% | 2.6% | 16.3% | 68% | 4% | 1 | 1 |
| HK_EQUITY | 15 | 13.7% | 9.5% | 1.8% | 18.5% | 4.3% | 13.7% | 76% | 3% | 11 | 11 |
| KR_EQUITY | 8 | 5.5% | 9.4% | -3.0% | 17.5% | 7.7% | 2.5% | 78% | 10% | 2 | 4 |
| PREMARKET | 4 | 5.5% | 5.5% | 5.5% | 5.5% | 5.5% | 5.5% | 0% | 0% | 0 | 0 |

Index sources across 213 symbols: aster_futures_index 2, binance_future 212, databento 26, dxfeed 182, hyperliquid 13, kaiko 203, massive 180, pyth_pro 189, redstone 4. Hyperliquid (a HIP-3 market) is a constituent of 13 indices: BZUSDT (xyz:BRENTOIL, 96.2%), CLUSDT (xyz:CL, 9.0%), COPPERUSDT (xyz:COPPER, 16.4%), CXMTUSDT (xyz:CXMT, 9.0%), HYUNDAIUSDT (xyz:HYUNDAI, 1.0%), NATGASUSDT (xyz:NATGAS, 9.0%), SAMSUNGUSDT (xyz:SMSN, 1.0%), SKHYNIXUSDT (xyz:SKHX, 1.0%), UNITREEUSDT (xyz:UNITREE, 9.1%), XAGUSDT (xyz:SILVER, 7.6%), XAUUSDT (xyz:GOLD, 7.6%), XPDUSDT (xyz:PALLADIUM, 12.3%), XPTUSDT (xyz:PLATINUM, 12.3%).

## 2. The pair family: funding spread HL - Binance

118 pairs with two weeks of overlap; median spread 5.2% a year; HL higher on 76% of pairs; first-half vs second-half correlation of pair means 0.49, same sign 67%.

| pair | class | hours | HL APR | Binance APR | spread | first half | second half |
|---|---|---:|---:|---:|---:|---:|---:|
| para:TTWO | us_equity | 875 | 64.7% | 8.3% | 56.3% | 56.4% | 56.3% |
| para:VST | us_equity | 1280 | 65.7% | 11.4% | 54.3% | 64.5% | 44.1% |
| io:GPRO | us_equity | 872 | 58.4% | 23.4% | 34.9% | 42.1% | 27.7% |
| xyz:UNITREE | other | 1240 | -22.5% | -55.4% | 33.0% | 48.3% | 17.6% |
| para:AVGO | us_equity | 3392 | 36.4% | 6.3% | 30.0% | 19.3% | 40.8% |
| xyz:BMNR | us_equity | 844 | 37.4% | 8.9% | 28.5% | 33.1% | 23.9% |
| io:IONQ | us_equity | 705 | 29.2% | 0.8% | 28.5% | 30.6% | 26.3% |
| para:CRDO | us_equity | 2027 | 30.2% | 2.5% | 27.7% | 32.0% | 23.3% |
| para:AAOI | us_equity | 1715 | 34.6% | 9.5% | 25.2% | 36.8% | 13.5% |
| xyz:XBI | us_equity | 1041 | 26.8% | 2.4% | 24.4% | 27.0% | 21.8% |
| xyz:SHAZ | us_equity | 1928 | 19.4% | -4.5% | 23.9% | 62.3% | -14.6% |
| io:NBIS | us_equity | 1018 | 25.4% | 3.9% | 21.5% | 28.7% | 14.3% |
| para:SMCI | us_equity | 1355 | 21.0% | -0.4% | 21.4% | 24.9% | 17.8% |
| para:CIEN | us_equity | 1523 | 20.7% | 1.0% | 19.7% | 34.2% | 5.3% |
| para:IREN | us_equity | 1882 | 22.8% | 3.1% | 19.7% | 34.8% | 4.7% |
| para:COHR | us_equity | 2027 | 21.1% | 2.7% | 18.3% | 26.3% | 10.3% |
| xyz:IREN | us_equity | 1257 | 20.3% | 2.8% | 17.6% | 21.4% | 13.7% |
| xyz:NET | us_equity | 1252 | 23.3% | 6.6% | 16.7% | 28.5% | 5.0% |
| para:RDDT | us_equity | 1544 | 20.6% | 4.5% | 16.1% | 35.2% | -3.0% |
| para:GLW | us_equity | 2027 | 18.8% | 3.0% | 15.8% | 19.5% | 12.2% |
| xyz:SMH | us_equity | 1736 | 15.9% | 0.3% | 15.6% | 11.6% | 19.5% |
| para:SOFI | us_equity | 924 | 30.9% | 15.9% | 15.0% | 13.0% | 17.0% |
| xyz:GEV | us_equity | 1566 | 30.2% | 15.7% | 14.5% | 18.9% | 10.2% |
| xyz:NOW | us_equity | 3057 | 16.0% | 2.0% | 14.0% | 18.8% | 9.2% |
| para:LRCX | us_equity | 1954 | 15.0% | 2.2% | 12.8% | 11.7% | 13.9% |
| xyz:CXMT | other | 1264 | -30.7% | -43.5% | 12.7% | 24.8% | 0.6% |
| xyz:HYUNDAI | other | 3112 | 19.4% | 7.0% | 12.4% | 17.9% | 7.0% |
| xyz:GME | us_equity | 2912 | 11.8% | -0.5% | 12.2% | 16.2% | 8.2% |
| xyz:MINIMAX | other | 2032 | 24.0% | 12.2% | 11.8% | 17.5% | 6.2% |
| para:TER | us_equity | 1786 | 12.8% | 1.1% | 11.7% | 27.8% | -4.4% |
| xyz:HIMS | us_equity | 2936 | 11.3% | -0.1% | 11.4% | 15.0% | 7.8% |
| xyz:BE | us_equity | 2623 | 13.9% | 2.8% | 11.1% | 17.6% | 4.7% |
| xyz:KSTR | us_equity | 586 | 22.9% | 12.2% | 10.8% | 18.8% | 2.8% |
| xyz:NOK | us_equity | 2791 | 16.7% | 6.5% | 10.2% | 14.6% | 5.7% |
| xyz:QCOM | us_equity | 2624 | 16.0% | 5.9% | 10.1% | 12.1% | 8.0% |
| xyz:NBIS | us_equity | 2938 | 17.3% | 7.4% | 9.9% | 16.3% | 3.5% |
| xyz:PALLADIUM | commodity | 4992 | 26.1% | 16.2% | 9.9% | 10.0% | 9.8% |
| xyz:LLY | us_equity | 3128 | 12.7% | 3.1% | 9.6% | 11.7% | 7.6% |
| xyz:BX | us_equity | 2960 | -0.4% | -10.0% | 9.6% | 19.2% | -0.1% |
| xyz:RIVN | us_equity | 2912 | 9.3% | 0.1% | 9.2% | 10.2% | 8.2% |
| xyz:XLE | us_equity | 2912 | 7.4% | -1.8% | 9.2% | 4.5% | 13.9% |
| xyz:URNM | us_equity | 2936 | 8.0% | -1.1% | 9.1% | 3.6% | 14.5% |
| xyz:HOOD | us_equity | 4992 | 11.2% | 2.4% | 8.8% | 10.1% | 7.5% |
| xyz:PLTR | us_equity | 4992 | 4.1% | -3.8% | 8.0% | 15.1% | 0.8% |
| xyz:USAR | us_equity | 3752 | 17.2% | 9.3% | 7.9% | -0.4% | 16.2% |
| io:DRAM | us_equity | 537 | 15.8% | 9.0% | 6.8% | 6.6% | 7.0% |
| xyz:MRNA | us_equity | 1088 | 5.4% | -1.4% | 6.8% | 5.9% | 7.7% |
| io:EWY | us_equity | 513 | 12.7% | 6.0% | 6.7% | 7.5% | 5.9% |
| xyz:RKLB | us_equity | 3464 | 13.9% | 7.3% | 6.6% | 7.0% | 6.1% |
| xyz:AMZN | us_equity | 4992 | 7.9% | 1.5% | 6.4% | 11.5% | 1.3% |
| xyz:COIN | us_equity | 4992 | 7.2% | 1.0% | 6.2% | 6.9% | 5.5% |
| para:NET | us_equity | 1280 | 13.0% | 6.9% | 6.1% | 11.9% | 0.4% |
| xyz:WDC | us_equity | 2935 | 8.7% | 2.7% | 6.0% | 6.2% | 5.8% |
| xyz:EWY | us_equity | 4976 | 4.1% | -1.7% | 5.8% | 11.8% | -0.3% |
| xyz:EBAY | us_equity | 2936 | 7.9% | 2.3% | 5.6% | 12.3% | -1.1% |
| xyz:RDDT | us_equity | 1254 | 10.6% | 5.1% | 5.5% | 11.2% | -0.2% |
| xyz:AVGO | us_equity | 3081 | 11.3% | 5.9% | 5.4% | 7.8% | 2.9% |
| xyz:ORCL | us_equity | 3536 | 10.8% | 5.5% | 5.3% | 5.9% | 4.8% |
| xyz:CRWV | us_equity | 3464 | 10.2% | 5.0% | 5.2% | 8.7% | 1.7% |
| xyz:NFLX | us_equity | 2936 | 8.5% | 3.4% | 5.1% | 9.0% | 1.2% |
| xyz:AMAT | us_equity | 2457 | 10.1% | 5.0% | 5.0% | 10.1% | -0.0% |
| xyz:IBM | us_equity | 3080 | 7.8% | 2.9% | 4.9% | 6.4% | 3.5% |
| xyz:EWJ | us_equity | 4904 | -2.7% | -7.4% | 4.8% | 6.1% | 3.4% |
| xyz:SOXL | us_equity | 1542 | 6.6% | 2.2% | 4.4% | 5.2% | 3.7% |
| para:UNITREE | other | 1240 | -51.1% | -55.4% | 4.3% | -1.8% | 10.5% |
| xyz:BABA | us_equity | 4136 | 12.3% | 8.2% | 4.2% | 6.1% | 2.3% |
| xyz:SP500 | index_proxy | 4472 | -0.6% | -4.5% | 4.0% | 8.3% | -0.3% |
| xyz:AAOI | us_equity | 1255 | 13.9% | 10.0% | 3.9% | 2.5% | 5.4% |
| xyz:META | us_equity | 4736 | 8.5% | 4.9% | 3.6% | 2.2% | 5.0% |
| xyz:MRVL | us_equity | 3536 | 13.9% | 10.3% | 3.5% | 3.2% | 3.8% |
| xyz:MSTR | us_equity | 4992 | 7.1% | 3.6% | 3.5% | 2.2% | 4.7% |
| xyz:DELL | us_equity | 3080 | 3.8% | 0.6% | 3.2% | 5.7% | 0.7% |
| xyz:ASML | us_equity | 2888 | 10.4% | 7.2% | 3.1% | 3.6% | 2.7% |
| xyz:INTC | us_equity | 4992 | 9.9% | 6.8% | 3.1% | 1.4% | 4.8% |
| xyz:ZHIPU | other | 2032 | 23.4% | 20.4% | 3.0% | -3.3% | 9.4% |
| xyz:GOLD | commodity | 4992 | 7.1% | 4.2% | 2.9% | 4.0% | 1.8% |
| xyz:XYZ100 | index_proxy | 4472 | 3.5% | 0.6% | 2.9% | 4.0% | 1.8% |
| xyz:CRWD | us_equity | 1250 | 3.2% | 0.3% | 2.9% | 17.2% | -11.5% |
| xyz:KORU | us_equity | 1567 | -0.3% | -3.0% | 2.7% | 4.3% | 1.0% |
| xyz:SMSN | other | 3112 | 16.7% | 14.3% | 2.4% | -3.1% | 7.9% |
| xyz:NVDA | us_equity | 4736 | 8.8% | 6.7% | 2.2% | 2.8% | 1.6% |
| xyz:TSLA | us_equity | 4992 | 4.8% | 2.7% | 2.1% | 0.9% | 3.3% |
| xyz:ZM | us_equity | 2912 | 6.0% | 4.3% | 1.7% | 6.6% | -3.1% |
| mkts:US500 | us_equity | 2409 | 2.7% | 1.2% | 1.5% | 2.1% | 0.8% |
| xyz:ARM | us_equity | 3272 | 7.4% | 6.1% | 1.3% | -1.9% | 4.5% |
| xyz:SKHX | other | 3112 | 36.5% | 35.3% | 1.2% | -1.0% | 3.4% |
| io:SNDK | us_equity | 1233 | 5.0% | 3.9% | 1.1% | 4.6% | -2.3% |
| xyz:DRAM | us_equity | 3464 | 15.3% | 14.3% | 1.0% | -0.8% | 2.8% |
| xyz:COPPER | commodity | 4992 | 11.2% | 11.0% | 0.3% | -1.7% | 2.3% |
| xyz:MSFT | us_equity | 4136 | 7.4% | 7.3% | 0.1% | -3.2% | 3.3% |
| xyz:STRC | us_equity | 2384 | -7.9% | -7.9% | -0.0% | 4.0% | -4.0% |
| xyz:SILVER | commodity | 4992 | 8.0% | 8.2% | -0.2% | -1.4% | 1.1% |
| xyz:EWT | us_equity | 3128 | 2.5% | 2.7% | -0.2% | 1.9% | -2.2% |
| xyz:SKHY | us_equity | 2192 | -6.4% | -6.2% | -0.2% | -0.9% | 0.4% |
| xyz:TSM | us_equity | 4472 | 6.2% | 6.6% | -0.4% | -7.0% | 6.3% |
| para:CRWD | us_equity | 1451 | -0.4% | 0.3% | -0.7% | 1.0% | -2.4% |
| xyz:PLATINUM | commodity | 4992 | 10.5% | 11.2% | -0.7% | 0.6% | -2.1% |
| xyz:SPCX | us_equity | 3392 | 3.7% | 4.5% | -0.7% | -0.5% | -1.0% |
| xyz:LITE | us_equity | 3536 | 12.8% | 13.9% | -1.1% | -8.8% | 6.7% |
| xyz:GOOGL | us_equity | 4736 | 9.1% | 10.5% | -1.4% | -4.7% | 1.9% |
| mkts:USTECH | us_equity | 2409 | 1.0% | 2.5% | -1.5% | -1.4% | -1.5% |
| xyz:EWZ | us_equity | 2912 | 3.7% | 5.1% | -1.5% | -4.9% | 2.0% |
| xyz:NATGAS | commodity | 4596 | 50.6% | 52.6% | -2.0% | -2.2% | -1.7% |
| xyz:AMD | us_equity | 3752 | 7.2% | 9.4% | -2.2% | -7.6% | 3.2% |
| xyz:BRENTOIL | commodity | 4596 | -28.5% | -26.3% | -2.2% | -14.4% | 10.0% |
| xyz:AAPL | us_equity | 4472 | -0.2% | 2.7% | -2.9% | -5.0% | -0.9% |
| xyz:CRCL | us_equity | 4992 | 12.0% | 14.9% | -3.0% | -8.3% | 2.4% |
| xyz:MU | us_equity | 4448 | 12.6% | 15.7% | -3.1% | -10.1% | 3.9% |
| xyz:SNDK | us_equity | 4448 | 6.7% | 10.1% | -3.4% | -9.4% | 2.5% |
| xyz:CL | commodity | 4596 | -31.2% | -27.8% | -3.5% | -14.7% | 7.7% |
| xyz:COST | us_equity | 2936 | -3.2% | 0.4% | -3.6% | -7.2% | -0.0% |
| xyz:DKNG | us_equity | 2912 | -1.8% | 2.3% | -4.1% | -0.7% | -7.6% |
| xyz:LYTE | us_equity | 1280 | -0.3% | 4.3% | -4.6% | 10.8% | -20.1% |
| xyz:OURA | other | 391 | -0.2% | 5.4% | -5.6% | -5.8% | -5.4% |
| xyz:SNXX | us_equity | 584 | 7.6% | 14.0% | -6.4% | -9.2% | -3.5% |
| mkts:SMALL2000 | us_equity | 1065 | -9.0% | 0.9% | -9.9% | -25.7% | 5.8% |
| xyz:BOT | us_equity | 2216 | 9.1% | 22.9% | -13.8% | -16.0% | -11.6% |
| xyz:CBRS | us_equity | 3440 | -8.6% | 6.6% | -15.2% | -18.2% | -12.2% |

## 3. Hourly pair grid (funding_arb machinery), chosen on the first half of pair-days

| sample | pairs | variants | test from | chosen | in-sample Sharpe | test reserved APR | test deployed APR | test t (30d) | rank | DSR | test trades | net / year held | cost/trade |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all matched pairs | 118 | 108 | 2026-08-07 | `slow_k90d_X8_Yzero` | 1.32 | 0.8% | 4.6% | 5.54 | 3 | 0.00 | 22 | 6.8% | 24.9bp |
| commodity | 8 | 108 | 2026-06-30 | `k168_X100_Yhalf_H168` | 2.40 | 0.0% | — | — | 106 | 0.00 | 0 | — | —bp |
| us_equity | 99 | 108 | 2026-08-10 | `always_short_hl` | 0.86 | 6.2% | 6.0% | 4.28 | 5 | 0.00 | 24 | 11.6% | 37.2bp |

Always-on (no signal), deployed APR before SSR, first half -> test (t, 30-day lags):

- all matched pairs: always_short_bn -4.8% -> -7.3% (t -9.82); always_short_hl 3.8% -> 5.1% (t 4.59)
- commodity: always_short_bn 1.5% -> -3.0% (t -1.50); always_short_hl -2.0% -> 2.5% (t 1.11)
- us_equity: always_short_bn -5.4% -> -8.3% (t -7.23); always_short_hl 4.2% -> 6.0% (t 4.28)

Chosen rule, test trades by class: other 1 trades, net 18.4% / yr held (funding 20.7%, basis -0.3%); us_equity 21 trades, net 6.2% / yr held (funding 7.7%, basis 1.0%)

## 4. Daily carries on one calendar (2026-03-16 to 2026-10-09, 145 sessions)

Excess over the 3.80%% savings rate, a year, on capital (broker legs 1.5x notional, two-perp 1.0x). Each family has six variants (all / trailing >= 8%% / top ten, two volume floors), chosen on the first half.

| version | names | capital | chosen | test from | in-sample excess | Sharpe | OOS excess | OOS Sharpe | OOS t | rank | DSR | BH survivors | OOS basket funding | OOS basket P&L / notional |
|---|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bn_broker | 174 | 1.50 | `carry|trail_8pct|vol>=2M` | 2026-07-15 | 2.1% | 4.11 | 0.2% | 0.12 | 0.06 | 3 | 0.94 | 0 | 7.5% | 7.1% |
| xyz_broker_all | 84 | 1.50 | `carry|trail_8pct|vol>=0.5M` | 2026-07-15 | 9.0% | 7.43 | 2.3% | 5.60 | 3.91 | 2 | 1.00 | 6 | 8.7% | 9.4% |
| xyz_broker_twins | 99 | 1.50 | `carry|trail_8pct|vol>=0.5M` | 2026-07-15 | 7.6% | 7.39 | 2.8% | 6.93 | 4.93 | 1 | 1.00 | 6 | 9.4% | 10.3% |
| xyz_short_bn_long_twins | 102 | 1.00 | `carry|top10|vol>=2M` | 2026-07-15 | -4.6% | -1.08 | 0.4% | 0.50 | 0.28 | 5 | 0.30 | 0 | 9.8% | 5.1% |
| xyz_short_bn_long_twins_3x | 102 | 0.67 | `carry|top10|vol>=2M` | 2026-07-15 | -5.0% | -0.78 | 2.5% | 2.00 | 1.13 | 6 | 0.34 | 0 | 9.8% | 5.1% |
| xyz_short_bn_long_twins_spread_signal | 102 | 1.00 | `carry|trail_8pct|vol>=2M` | 2026-07-15 | -3.5% | -0.79 | 0.9% | 1.04 | 0.59 | 4 | 0.31 | 0 | 5.7% | 5.7% |

Two-perp rows, all twins and days: HL funding 9.8%, Binance funding 4.3%, basis 0.1% a year per notional.

| month | name-days | HL funding | Binance funding | basis | net (a year, per notional) |
|---|---:|---:|---:|---:|---:|
| 2026-03 | 116 | 0.4% | -8.2% | 0.7% | 9.2% |
| 2026-04 | 359 | -1.1% | -23.0% | -0.2% | 21.6% |
| 2026-05 | 483 | 13.1% | 28.6% | -0.6% | -16.1% |
| 2026-06 | 970 | 13.4% | 8.4% | -0.1% | 4.9% |
| 2026-07 | 1362 | 9.2% | 2.6% | 0.0% | 6.6% |
| 2026-08 | 1600 | 10.9% | 2.3% | -1.0% | 7.7% |
| 2026-09 | 1928 | 9.5% | 4.2% | -0.4% | 4.8% |
| 2026-10 | 674 | 9.3% | 5.7% | 5.3% | 8.9% |

Where the carry lives (equal-weight always-on rows, no selection, no costs; split at 2026-07-15; buckets by HL open interest now):

| carry | bucket | names | first half: P&L / notional | funding | excess on capital (t) | second half: P&L / notional | funding | excess on capital (t) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| broker_xyz | oi_under_5m | 44 | 23.1% | 21.7% | 11.6% (3.00) | 12.7% | 10.4% | 4.7% (2.70) |
| broker_xyz | oi_5m_to_20m | 21 | 12.1% | 11.0% | 4.2% (1.79) | 7.9% | 6.9% | 1.5% (2.20) |
| broker_xyz | oi_over_20m | 19 | 9.6% | 9.0% | 2.6% (2.26) | 6.6% | 6.0% | 0.6% (0.90) |
| broker_xyz | all | 84 | 15.2% | 14.1% | 6.3% (3.08) | 9.9% | 8.4% | 2.8% (3.63) |
| two_perp_twins | oi_under_5m | 61 | 8.4% | 8.9% | 4.6% (0.85) | 9.4% | 9.7% | 5.6% (3.38) |
| two_perp_twins | oi_5m_to_20m | 22 | 7.9% | 7.9% | 4.1% (0.59) | 5.1% | 4.9% | 1.3% (0.98) |
| two_perp_twins | oi_over_20m | 19 | 1.9% | 2.0% | -1.9% (-0.27) | 2.7% | 2.3% | -1.1% (-0.83) |
| two_perp_twins | all | 102 | 4.8% | 4.7% | 1.0% (0.14) | 6.9% | 6.8% | 3.1% (2.92) |

Capacity, xyz_broker_all (basket from 2026-09-15): planning notional (5% of OI) $15.87M, capital $23.81M, $539k a year over SSR at the OOS excess; capped also at the Saturday depth within 25bp: $1.58M notional, $54k a year.

| name | 5% of OI | with depth cap | HL OI | Binance OI | HL depth 25bp (Sat, min side) | HL depth 25bp bid/ask (2026-09-10 in session) | both venues min depth 25bp | size at 10bp (short HL) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xyz:AAOI | $112k | $12k | $2.25M | $14.53M | $12k | — / — | $12k | $5k |
| xyz:ARM | $294k | $106k | $5.87M | $10.39M | $106k | $154k / $176k | $62k | $53k |
| xyz:AVGO | $636k | $63k | $12.72M | $28.80M | $63k | $97k / $125k | $63k | $55k |
| xyz:BABA | $606k | $61k | $12.13M | $21.56M | $61k | $229k / $379k | $61k | $35k |
| xyz:BE | $263k | $13k | $5.26M | $6.67M | $13k | $55k / $82k | $13k | $11k |
| xyz:BOT | $159k | $1k | $3.18M | $540k | $1k | — / — | $1k | $262 |
| xyz:COIN | $890k | $159k | $17.80M | $18.10M | $159k | $253k / $160k | $128k | $112k |
| xyz:CRCL | $6.21M | $289k | $124.14M | $128.52M | $289k | $116k / $178k | $289k | $319k |
| xyz:CRWD | $104k | $12k | $2.07M | $2.74M | $12k | — / — | $12k | $7k |
| xyz:HIMS | $158k | $10k | $3.16M | $887k | $10k | — / — | $10k | $3k |
| xyz:HOOD | $1.46M | $168k | $29.18M | $14.64M | $168k | $371k / $455k | $100k | $29k |
| xyz:IREN | $212k | $4k | $4.24M | $7.08M | $4k | — / — | $4k | $4k |
| xyz:LITE | $321k | $78k | $6.42M | $18.83M | $78k | $103k / $130k | $78k | $29k |
| xyz:LLY | $249k | $31k | $4.97M | $2.54M | $31k | $132k / $157k | $31k | $17k |
| xyz:LYTE | $26k | $83 | $521k | $559k | $83 | — / — | $83 | $0 |
| xyz:MSTR | $2.27M | $385k | $45.36M | $78.90M | $385k | $697k / $471k | $385k | $249k |
| xyz:NOK | $77k | $2k | $1.54M | $6.62M | $2k | — / — | $2k | $0 |
| xyz:NOW | $98k | $3k | $1.97M | $1.34M | $3k | — / — | $3k | $656 |
| xyz:QCOM | $253k | $10k | $5.06M | $14.09M | $10k | $80k / $97k | $10k | $8k |
| xyz:QNT | $67k | — | $1.33M | — | — | — / — | — | — |
| xyz:RKLB | $644k | $67k | $12.87M | $11.61M | $67k | $33k / $47k | $67k | $66k |
| xyz:SHAZ | $45k | $627 | $907k | $795k | $627 | — / — | $627 | $0 |
| xyz:SMH | $135k | $6k | $2.70M | $825k | $6k | — / — | $5k | $17k |
| xyz:TSM | $385k | $71k | $7.71M | $16.58M | $71k | $126k / $60k | $71k | $40k |
| xyz:USAR | $156k | $19k | $3.12M | $3.31M | $19k | — / — | $14k | $8k |
| xyz:XLE | $50k | $7k | $1.00M | $608k | $7k | — / — | $7k | $3k |

Capacity, xyz_broker_twins (basket from 2026-09-15): planning notional (5% of OI) $15.85M, capital $23.78M, $664k a year over SSR at the OOS excess; capped also at the Saturday depth within 25bp: $1.59M notional, $66k a year.

| name | 5% of OI | with depth cap | HL OI | Binance OI | HL depth 25bp (Sat, min side) | HL depth 25bp bid/ask (2026-09-10 in session) | both venues min depth 25bp | size at 10bp (short HL) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| para:AAOI | $7k | $5k | $150k | $14.53M | $5k | — / — | $5k | $0 |
| para:CRDO | $37k | $1k | $733k | $2.43M | $1k | — / — | $1k | $0 |
| xyz:AAOI | $112k | $12k | $2.25M | $14.53M | $12k | — / — | $12k | $5k |
| xyz:ARM | $294k | $106k | $5.87M | $10.39M | $106k | $154k / $176k | $62k | $53k |
| xyz:AVGO | $636k | $63k | $12.72M | $28.80M | $63k | $97k / $125k | $63k | $55k |
| xyz:BABA | $606k | $61k | $12.13M | $21.56M | $61k | $229k / $379k | $61k | $35k |
| xyz:BE | $263k | $13k | $5.26M | $6.67M | $13k | $55k / $82k | $13k | $11k |
| xyz:BOT | $159k | $1k | $3.18M | $540k | $1k | — / — | $1k | $262 |
| xyz:COIN | $890k | $159k | $17.80M | $18.10M | $159k | $253k / $160k | $128k | $112k |
| xyz:CRCL | $6.21M | $289k | $124.14M | $128.52M | $289k | $116k / $178k | $289k | $319k |
| xyz:CRWD | $104k | $12k | $2.07M | $2.74M | $12k | — / — | $12k | $7k |
| xyz:HIMS | $158k | $10k | $3.16M | $887k | $10k | — / — | $10k | $3k |
| xyz:HOOD | $1.46M | $168k | $29.18M | $14.64M | $168k | $371k / $455k | $100k | $29k |
| xyz:IREN | $212k | $4k | $4.24M | $7.08M | $4k | — / — | $4k | $4k |
| xyz:LITE | $321k | $78k | $6.42M | $18.83M | $78k | $103k / $130k | $78k | $29k |
| xyz:LLY | $249k | $31k | $4.97M | $2.54M | $31k | $132k / $157k | $31k | $17k |
| xyz:LYTE | $26k | $83 | $521k | $559k | $83 | — / — | $83 | $0 |
| xyz:MSTR | $2.27M | $385k | $45.36M | $78.90M | $385k | $697k / $471k | $385k | $249k |
| xyz:NOK | $77k | $2k | $1.54M | $6.62M | $2k | — / — | $2k | $0 |
| xyz:NOW | $98k | $3k | $1.97M | $1.34M | $3k | — / — | $3k | $656 |
| xyz:QCOM | $253k | $10k | $5.06M | $14.09M | $10k | $80k / $97k | $10k | $8k |
| xyz:RKLB | $644k | $67k | $12.87M | $11.61M | $67k | $33k / $47k | $67k | $66k |
| xyz:SHAZ | $45k | $627 | $907k | $795k | $627 | — / — | $627 | $0 |
| xyz:SMH | $135k | $6k | $2.70M | $825k | $6k | — / — | $5k | $17k |
| xyz:TSM | $385k | $71k | $7.71M | $16.58M | $71k | $126k / $60k | $71k | $40k |
| xyz:USAR | $156k | $19k | $3.12M | $3.31M | $19k | — / — | $14k | $8k |
| xyz:XLE | $50k | $7k | $1.00M | $608k | $7k | — / — | $7k | $3k |

Capacity, xyz_short_bn_long_twins (basket from 2026-09-15): planning notional (5% of OI) $12.60M, capital $12.60M, $54k a year over SSR at the OOS excess; capped also at the Saturday depth within 25bp: $1.20M notional, $5k a year.

| name | 5% of OI | with depth cap | HL OI | Binance OI | HL depth 25bp (Sat, min side) | HL depth 25bp bid/ask (2026-09-10 in session) | both venues min depth 25bp | size at 10bp (short HL) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xyz:ARM | $294k | $62k | $5.87M | $10.39M | $106k | $154k / $176k | $62k | $53k |
| xyz:AVGO | $636k | $63k | $12.72M | $28.80M | $63k | $97k / $125k | $63k | $55k |
| xyz:BABA | $606k | $61k | $12.13M | $21.56M | $61k | $229k / $379k | $61k | $35k |
| xyz:BE | $263k | $13k | $5.26M | $6.67M | $13k | $55k / $82k | $13k | $11k |
| xyz:COIN | $890k | $128k | $17.80M | $18.10M | $159k | $253k / $160k | $128k | $112k |
| xyz:CRCL | $6.21M | $289k | $124.14M | $128.52M | $289k | $116k / $178k | $289k | $319k |
| xyz:HOOD | $732k | $100k | $29.18M | $14.64M | $168k | $371k / $455k | $100k | $29k |
| xyz:LLY | $127k | $31k | $4.97M | $2.54M | $31k | $132k / $157k | $31k | $17k |
| xyz:MSTR | $2.27M | $385k | $45.36M | $78.90M | $385k | $697k / $471k | $385k | $249k |
| xyz:RKLB | $580k | $67k | $12.87M | $11.61M | $67k | $33k / $47k | $67k | $66k |

Capacity, xyz_short_bn_long_twins_spread_signal (basket from 2026-09-15): planning notional (5% of OI) $711k, capital $711k, $7k a year over SSR at the OOS excess; capped also at the Saturday depth within 25bp: $123k notional, $1k a year.

| name | 5% of OI | with depth cap | HL OI | Binance OI | HL depth 25bp (Sat, min side) | HL depth 25bp bid/ask (2026-09-10 in session) | both venues min depth 25bp | size at 10bp (short HL) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| xyz:BE | $263k | $13k | $5.26M | $6.67M | $13k | $55k / $82k | $13k | $11k |
| xyz:LITE | $321k | $78k | $6.42M | $18.83M | $78k | $103k / $130k | $78k | $29k |
| xyz:LLY | $127k | $31k | $4.97M | $2.54M | $31k | $132k / $157k | $31k | $17k |

## 5. While the cash market is shut: broker hedge vs Binance hedge

| period | name-periods | perp up p50 / p95 / p99 / max (broker short) | basis up p50 / p95 / p99 / max (two-perp short) | basis gap at open, abs p50 / p95 |
|---|---:|---|---|---|
| holiday | 244 | 2.09% / 7.23% / 8.48% / 9.90% | 0.16% / 1.09% / 2.69% / 3.35% | 0.08% / 0.40% |
| overnight | 6083 | 0.82% / 4.94% / 8.87% / 27.89% | 0.11% / 0.68% / 1.54% / 9.42% | 0.07% / 0.53% |
| overnight_hl_oi_over_5m | 3422 | 0.90% / 5.38% / 9.91% / 27.89% | 0.07% / 0.26% / 0.50% / 9.42% | 0.05% / 0.22% |
| weekend | 1367 | 1.20% / 5.28% / 7.74% / 14.40% | 0.18% / 0.99% / 1.71% / 5.48% | 0.07% / 0.57% |
| weekend_hl_oi_over_5m | 759 | 1.42% / 5.92% / 7.93% / 14.40% | 0.10% / 0.55% / 1.24% / 2.33% | 0.06% / 0.21% |

| hours | pairs | median corr | median sd HL (bp) | median sd basis (bp) | variance hedged |
|---|---:|---:|---:|---:|---:|
| offhours | 100 | 0.96 | 62.7 | 16.2 | 91.5% |
| session | 99 | 0.99 | 125.7 | 17.1 | 97.5% |
| weekend | 99 | 0.90 | 39.7 | 15.4 | 79.9% |

Worst basis excursions: xyz:SPCX 2026-06-09 overnight 9.42%; xyz:BOT 2026-07-21 overnight 7.06%; para:LRCX 2026-07-29 overnight 6.71%; para:CRDO 2026-07-29 overnight 6.45%; para:AAOI 2026-09-23 overnight 6.24%; para:RDDT 2026-08-10 overnight 5.93%; para:COHR 2026-07-17 weekend 5.48%; para:CRDO 2026-07-17 weekend 5.37%; para:COHR 2026-08-12 overnight 4.72%; xyz:DRAM 2026-05-22 holiday 4.53%

## 6. Energy: Binance index vs trade.xyz oracle around the GSCI roll

**xyz:BRENTOIL / BZUSDT** (4610 hours; sd of the hourly log-ratio change 43.3bp)

| month | xyz rolls | ratio change at the five step hours (bp) | sum | pair short xyz: HL funding | Binance funding | basis | net |
|---|---|---|---:|---:|---:|---:|---:|
| 2026-04 | True | 6 -100 56 -83 9 | -112 | -3.33% | -2.01% | -0.54% | -1.86% |
| 2026-05 | True | -43 38 -0 11 15 | 21 | -2.75% | -3.00% | -0.08% | 0.17% |
| 2026-06 | True | 25 -5 -16 -70 -1 | -67 | -0.88% | -0.84% | -0.01% | -0.06% |
| 2026-07 | True | 6 9 22 4 15 | 55 | -0.09% | -0.41% | -0.02% | 0.30% |
| 2026-08 | True | 23 16 10 1 18 | 68 | -1.97% | -2.45% | 0.00% | 0.49% |
| 2026-09 | True | 20 7 96 56 23 | 202 | -4.19% | -4.26% | -0.01% | 0.06% |
| 2026-10 | True | 22 23 36 — — | 81 | -1.78% | -1.80% | — | — |

October front weights (BZZ26.NYM / BZF27.NYM): 2026-09-28 Binance 1.01 xyz 1.00; 2026-09-29 Binance 1.01 xyz 1.01; 2026-09-30 Binance 1.02 xyz 1.01; 2026-10-01 Binance 1.02 xyz 0.99; 2026-10-02 Binance 1.01 xyz 1.00; 2026-10-04 Binance 0.99 xyz 1.07; 2026-10-05 Binance 1.01 xyz 1.01; 2026-10-06 Binance 1.00 xyz 0.99; 2026-10-07 Binance 1.00 xyz 1.01; 2026-10-08 Binance 0.81 xyz 0.77; 2026-10-09 Binance 0.62 xyz 0.60

Largest hourly ratio moves off the xyz schedule: 2026-04-12T23 +601bp, 2026-04-08T01 -515bp, 2026-04-19T23 +474bp, 2026-04-08T00 +468bp, 2026-04-02T02 +356bp, 2026-06-14T23 +350bp

**xyz:CL / CLUSDT** (4610 hours; sd of the hourly log-ratio change 46.8bp)

| month | xyz rolls | ratio change at the five step hours (bp) | sum | pair short xyz: HL funding | Binance funding | basis | net |
|---|---|---|---:|---:|---:|---:|---:|
| 2026-04 | True | -40 -54 55 -82 -18 | -140 | -4.94% | -3.22% | -0.28% | -1.99% |
| 2026-05 | True | -43 22 9 17 12 | 16 | -3.07% | -3.05% | -0.14% | -0.16% |
| 2026-06 | True | 19 -3 -12 -56 -6 | -58 | -1.39% | -1.37% | 0.00% | -0.02% |
| 2026-07 | True | -9 -7 8 -5 15 | 2 | 0.09% | -0.01% | 0.02% | 0.13% |
| 2026-08 | True | 28 18 9 -23 15 | 46 | -1.01% | -1.10% | -0.01% | 0.08% |
| 2026-09 | True | 32 13 88 57 32 | 222 | -3.63% | -3.82% | 0.02% | 0.21% |
| 2026-10 | True | -11 -29 10 — — | -29 | -0.56% | -0.67% | — | — |

October front weights (CLX26.NYM / CLZ26.NYM): 2026-09-28 Binance 1.01 xyz 0.99; 2026-09-29 Binance 1.01 xyz 1.02; 2026-09-30 Binance 1.02 xyz 1.01; 2026-10-01 Binance 1.02 xyz 1.02; 2026-10-02 Binance 1.02 xyz 1.01; 2026-10-04 Binance 1.01 xyz 1.23; 2026-10-05 Binance 1.02 xyz 1.05; 2026-10-06 Binance 1.02 xyz 0.99; 2026-10-07 Binance 1.04 xyz 1.01; 2026-10-08 Binance 0.88 xyz 0.71; 2026-10-09 Binance 0.69 xyz 0.56

Largest hourly ratio moves off the xyz schedule: 2026-04-07T23 -518bp, 2026-04-08T00 +516bp, 2026-04-12T23 +510bp, 2026-04-19T23 +506bp, 2026-05-06T12 +368bp, 2026-06-14T23 +338bp

**xyz:NATGAS / NATGASUSDT** (4610 hours; sd of the hourly log-ratio change 32.5bp)

| month | xyz rolls | ratio change at the five step hours (bp) | sum | pair short xyz: HL funding | Binance funding | basis | net |
|---|---|---|---:|---:|---:|---:|---:|
| 2026-04 | True | 7 40 -56 54 51 | 96 | 5.03% | 6.64% | 0.10% | -1.52% |
| 2026-05 | True | 121 -77 -72 -43 -51 | -122 | 6.74% | 6.39% | 0.34% | 0.68% |
| 2026-06 | True | -1 6 -6 -2 -13 | -17 | 0.81% | 0.48% | 0.10% | 0.43% |
| 2026-07 | True | -8 9 -6 -16 11 | -10 | -1.08% | -0.59% | -0.02% | -0.51% |
| 2026-08 | True | 0 -38 -10 -14 -9 | -70 | 1.64% | 1.53% | -0.01% | 0.10% |
| 2026-09 | True | -5 -30 -26 -61 -32 | -154 | 3.95% | 4.17% | 0.02% | -0.20% |
| 2026-10 | True | -140 119 -55 — — | -76 | 5.51% | 6.02% | — | — |

October front weights (NGX26.NYM / NGZ26.NYM): 2026-09-28 Binance 1.00 xyz 1.00; 2026-09-29 Binance 1.00 xyz 0.99; 2026-09-30 Binance 1.00 xyz 1.00; 2026-10-01 Binance 1.00 xyz 0.99; 2026-10-02 Binance 1.00 xyz 1.00; 2026-10-04 Binance 1.00 xyz 0.96; 2026-10-05 Binance 1.01 xyz 1.01; 2026-10-06 Binance 1.01 xyz 1.00; 2026-10-07 Binance 1.00 xyz 1.00; 2026-10-08 Binance 0.80 xyz 0.80; 2026-10-09 Binance 0.60 xyz 0.60

Largest hourly ratio moves off the xyz schedule: 2026-04-12T23 +251bp, 2026-09-27T23 -222bp, 2026-07-16T16 +214bp, 2026-05-07T15 +214bp, 2026-06-18T18 -201bp, 2026-07-16T15 -199bp

## 7. Matching

123 pairs ({'proxy': 2, 'same': 121}), by Binance class {'CN_EQUITY': 3, 'COMMODITY': 8, 'EQUITY': 105, 'HK_EQUITY': 3, 'KR_EQUITY': 3, 'PREMARKET': 1}; 31 HIP-3 markets have no Binance twin; rejected on price: io:ANTH/ANTHROPICUSDT (price ratio 1.0263), io:OAI/OPENAIUSDT (price ratio 1.0436), io:TCNT/HK0700USDT (price ratio 0.1273), xyz:GIGADEV/GIGADEVUSDT (price ratio 0.9356), xyz:KR200/KODEX200USDT (price ratio 13.5627), xyz:SMSN/SAMSUNGEMUSDT (price ratio 0.1758).
