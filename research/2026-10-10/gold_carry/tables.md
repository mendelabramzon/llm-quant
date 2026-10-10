# Gold carry: long tokenized gold, short the metal perp — tables (2026-10-10)

Every number below is in `analysis.json`; benchmark SSR 3.80% a year on capital unless noted.

## 1. Verdicts (pre-committed go rules: {"bh_study_wide": true, "both_test_halves_positive": true, "max_boot_p": 0.05, "min_capacity_usd": 1000000.0, "min_nw_t_30": 2.0, "min_oos_excess": 0.01})

| series | capital | K | chosen rule | test window | excess in sample | excess out of sample | NW t (30) | bootstrap p≤0 | BH adj p (168) | test halves | size (25bp) | $/yr at size | go |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hl:PAXG x PAXG@bn | cash10 | 1.15 | always | 2026-01-08→2026-10-09 | 4.39% | 1.69% | 2.17 | 0.024 | 0.20 | 0.57% / 2.80% | $1.02M | $20k | no |
| hl:PAXG x PAXG@bn | cash20 | 1.25 | always | 2026-01-08→2026-10-09 | 3.79% | 1.34% | 1.90 | 0.037 | 0.23 | 0.38% / 2.29% | $1.02M | $17k | no |
| bn:PAXGUSDT x PAXG@bn | collateral | 1.00 | always | 2026-01-02→2026-10-09 | 0.97% | 0.67% | 1.18 | 0.137 | 0.61 | 0.05% / 1.28% | $1.04M | $7k | no |
| bn:PAXGUSDT x PAXG@bn | cash10 | 1.11 | always | 2026-01-02→2026-10-09 | 0.40% | 0.10% | 0.19 | 0.406 | 0.95 | -0.48% / 0.68% | $2.13M | $2k | no |
| bn:PAXGUSDT x PAXG@bn | cash20 | 1.21 | always | 2026-01-02→2026-10-09 | 0.11% | -0.13% | -0.28 | 0.583 | 0.91 | -0.59% / 0.33% | $2.13M | $-3k | no |
| by:PAXGUSDT x PAXG@bn | cash10 | 1.11 | trail30d_x5pp | 2024-06-27→2026-10-09 | 4.44% | -0.02% | -0.02 | 0.504 | 1.00 | -0.01% / -0.03% | $688k | $-150 | no |
| by:PAXGUSDT x PAXG@bn | cash20 | 1.21 | trail30d_x5pp | 2024-06-27→2026-10-09 | 3.89% | -0.09% | -0.10 | 0.532 | 0.99 | -0.11% / -0.07% | $688k | $-781 | no |
| bn:XAUTUSDT x XAUT@bn | collateral | 1.00 | trail30d_x0pp | 2026-07-03→2026-10-09 | 0.10% | 1.63% | 2.96 | 0.008 | 0.06 | 1.76% / 1.50% | $553k | $9k | no |
| bn:XAUTUSDT x XAUT@bn | cash10 | 1.11 | trail30d_x0pp | 2026-07-03→2026-10-09 | -0.20% | 1.01% | 2.07 | 0.040 | 0.21 | 1.10% / 0.92% | $1.19M | $13k | no |
| bn:XAUTUSDT x XAUT@bn | cash20 | 1.21 | trail30d_x0pp | 2026-07-03→2026-10-09 | -0.26% | 0.64% | 1.43 | 0.114 | 0.43 | 0.70% / 0.58% | $1.19M | $9k | no |
| by:XAUTUSDT x XAUT@by | collateral | 1.00 | trail30d_x0pp | 2026-01-10→2026-10-09 | 0.55% | 0.95% | 2.24 | 0.024 | 0.19 | 1.27% / 0.62% | $459k | $4k | no |
| by:XAUTUSDT x XAUT@by | cash10 | 1.11 | trail30d_x0pp | 2026-01-10→2026-10-09 | 0.15% | 0.41% | 1.10 | 0.175 | 0.61 | 0.64% / 0.18% | $1.06M | $5k | no |
| by:XAUTUSDT x XAUT@by | cash20 | 1.21 | trail30d_x0pp | 2026-01-10→2026-10-09 | -0.07% | 0.13% | 0.39 | 0.374 | 0.87 | 0.32% / -0.05% | $1.06M | $2k | no |
| bn:XAUUSDT x PAXG@bn | collateral | 1.00 | always | 2026-05-12→2026-10-09 | 13.75% | 2.63% | 1.56 | 0.052 | 0.36 | 2.79% / 2.46% | $1.04M | $27k | no |
| bn:XAUUSDT x PAXG@bn | cash10 | 1.11 | always | 2026-05-12→2026-10-09 | 11.87% | 1.96% | 1.28 | 0.098 | 0.52 | 2.20% / 1.73% | $2.13M | $46k | no |
| bn:XAUUSDT x PAXG@bn | cash20 | 1.21 | always | 2026-05-12→2026-10-09 | 10.65% | 1.59% | 1.13 | 0.133 | 0.61 | 1.81% / 1.37% | $2.13M | $41k | no |
| bn:XAUUSDT x XAUT@bn | collateral | 1.00 | trail7d_x0pp | 2026-07-03→2026-10-09 | -1.31% | -2.70% | -0.74 | 0.803 | 0.82 | -8.57% / 3.05% | $553k | $-15k | no |
| by:XAUUSDT x XAUT@by | collateral | 1.00 | always | 2026-06-25→2026-10-09 | -0.26% | 1.81% | 0.46 | 0.337 | 0.86 | -4.92% / 8.42% | $459k | $8k | no |
| by:XAUUSDT x XAUT@by | cash10 | 1.11 | always | 2026-06-25→2026-10-09 | -0.81% | 1.15% | 0.33 | 0.378 | 0.91 | -4.93% / 7.11% | $2.05M | $26k | no |
| by:XAUUSDT x XAUT@by | cash20 | 1.21 | always | 2026-06-25→2026-10-09 | -0.98% | 0.79% | 0.24 | 0.412 | 0.92 | -4.73% / 6.21% | $2.05M | $20k | no |
| hl:xyz:GOLD x PAXG@bn | cash10 | 1.12 | always | 2026-05-18→2026-10-09 | 2.07% | 2.59% | 2.23 | 0.035 | 0.19 | 3.53% / 1.67% | $2.13M | $62k | no |
| hl:xyz:GOLD x PAXG@bn | cash20 | 1.22 | always | 2026-05-18→2026-10-09 | 1.69% | 2.21% | 2.07 | 0.040 | 0.21 | 3.06% / 1.36% | $2.13M | $57k | no |
| best_paxg_hedged | cash10 | 1.15 | trail30d_x5pp | 2024-06-27→2026-10-09 | 4.20% | 1.56% | 1.01 | 0.135 | 0.67 | 1.33% / 1.79% | — | — | no |
| best_xaut_hedged | cash10 | 1.11 | always | 2026-01-06→2026-10-09 | 0.69% | 1.79% | 0.44 | 0.324 | 0.87 | 3.94% / -0.35% | — | — | no |

## 2. What each index tracks (US-session hours unless noted; bp)

| market | index/GC=F median | p05 / p95 | index/PAXG median | sd of daily median vs GC | vs PAXG | steps >25bp vs GC | vs PAXG | slope on own perp (open) | (shut) | shut hours frozen | weekends moving since |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bn:PAXGUSDT | -34.7 | -150.1 / 30.4 | 0.0 | 53.3 | 0.3 | 24 | 0 | 0.99 | 1.00 | 2% | — |
| bn:XAGUSDT | -24.8 | -83.1 / 26.7 | — | 33.6 | — | 6 | 0 | 1.01 | 0.14 | 45% | 2026-05 |
| bn:XAUTUSDT | -78.5 | -170.9 / -11.0 | -12.1 | 47.8 | 12.8 | 7 | 0 | 1.00 | 0.95 | 4% | — |
| bn:XAUUSDT | -42.7 | -123.0 / 0.1 | 4.0 | 36.9 | 23.6 | 5 | 5 | 1.03 | 0.19 | 50% | 2026-05 |
| by:PAXGUSDT | -38.7 | -164.6 / 32.7 | 0.0 | 59.9 | 1.0 | 40 | 0 | 0.88 | 1.07 | 17% | — |
| by:XAGUSDT | -30.4 | -84.6 / 2.2 | — | 27.3 | — | 3 | 0 | 1.00 | 0.70 | 18% | — |
| by:XAUTUSDT | -59.0 | -164.9 / 7.7 | -19.4 | 49.4 | 20.4 | 18 | 1 | 0.98 | 0.91 | 2% | — |
| by:XAUUSDT | -46.8 | -123.8 / 3.2 | 14.2 | 39.9 | 12.5 | 3 | 0 | 1.01 | 0.78 | 4% | 2026-03 |
| hl:PAXG | -57.2 | -146.0 / 5.5 | -0.4 | 41.6 | 0.6 | 3 | 0 | 1.00 | 1.01 | 2% | — |
| hl:cash:GOLD | -32.5 | -56.7 / 8.7 | 18.7 | 20.4 | 10.8 | 2 | 0 | 1.02 | 0.53 | 3% | — |
| hl:flx:GOLD | -40.0 | -74.9 / 10.1 | 11.5 | 22.1 | 14.6 | 2 | 1 | 1.02 | 0.94 | 1% | — |
| hl:km:GOLD | -37.7 | -76.1 / 5.4 | 12.6 | 23.4 | 13.2 | 2 | 1 | 0.99 | 0.72 | 2% | — |
| hl:xyz:GOLD | -49.8 | -134.6 / -2.4 | 8.6 | 41.6 | 13.5 | 3 | 0 | 1.01 | 0.64 | 4% | 2026-03 |
| hl:xyz:SILVER | -39.6 | -89.1 / 0.4 | — | 27.7 | — | 3 | 0 | 1.00 | 0.72 | 2% | 2026-03 |
| okx:XAG-USDT-SWAP | -24.4 | -82.8 / 27.7 | — | 33.5 | — | 5 | 0 | 1.01 | 0.78 | 12% | — |
| okx:XAU-USDT-SWAP | -50.5 | -120.3 / 11.1 | 6.9 | 37.6 | 23.7 | 7 | 1 | 1.01 | 0.72 | 19% | 2026-01 |

Binance XAU index first moved on a Saturday at 2026-05-09T05:00:00+00:00.

### Cost of carry implied by COMEX (USD rate − lease, incl. any COMEX premium over London)

| roll day | from | to | step of PAXG/GC=F (bp) | months | implied carry a year |
|---|---|---|---|---|---|
| 2024-05-29 | 2024-06 | 2024-08 | -149.0 | 2 | 8.94% |
| 2024-11-27 | 2024-12 | 2025-02 | -108.6 | 2 | 6.52% |
| 2025-01-29 | 2025-02 | 2025-04 | -109.5 | 2 | 6.57% |
| 2025-03-27 | 2025-04 | 2025-06 | -93.9 | 2 | 5.64% |
| 2025-05-28 | 2025-06 | 2025-08 | -56.9 | 2 | 3.42% |
| 2025-07-29 | 2025-08 | 2025-12 | -136.7 | 4 | 4.10% |
| 2025-11-26 | 2025-12 | 2026-02 | -79.3 | 2 | 4.76% |
| 2026-01-28 | 2026-02 | 2026-04 | -46.3 | 2 | 2.78% |
| 2026-03-27 | 2026-04 | 2026-06 | -57.3 | 2 | 3.44% |
| 2026-05-27 | 2026-06 | 2026-08 | -58.6 | 2 | 3.51% |
| 2026-07-29 | 2026-08 | 2026-12 | -128.0 | 4 | 3.84% |

Median of rolls since 2025-12: 3.48%; level method over the last 60 days: 3.13% (median).

## 3. Funding a short receives (annualised from what was paid)

| market | first | delisted | interval h | since listing | first half | second half | last 90d | last 30d | spot open | spot shut | modal rate (floor) | negative |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bn:PAXGUSDT | 2025-03-27 |  | 4 | 4.88% | 5.04% | 4.72% | 5.34% | 8.14% | 5.05% | 4.50% | 45% at 10.95% | 22% |
| bn:XAGUSDT | 2026-01-07 |  | 4 | 20.81% | 32.88% | 8.77% | 7.11% | 8.24% | 15.70% | 32.19% | 46% at 0.00% | 6% |
| bn:XAUTUSDT | 2026-03-26 |  | 4 | 5.12% | 4.23% | 6.01% | 5.87% | 6.94% | 5.02% | 5.36% | 18% at 10.95% | 14% |
| bn:XAUUSDT | 2025-12-11 |  | 4 | 13.01% | 19.15% | 6.90% | 6.56% | 10.04% | 10.43% | 18.54% | 46% at 0.00% | 7% |
| by:PAXGUSDT | 2022-03-15 |  | 8 | 6.74% | 8.61% | 4.88% | 8.05% | 10.73% | 5.33% | 4.44% | 38% at 10.95% | 14% |
| by:XAGUSDT | 2026-03-09 |  | 4 | 8.41% | 8.94% | 7.90% | 8.24% | 12.38% | 7.82% | 9.91% | 67% at 0.00% | 3% |
| by:XAUTUSDT | 2025-04-03 |  | 4 | 4.64% | 4.14% | 5.14% | 5.16% | 6.29% | 4.35% | 5.28% | 55% at 10.95% | 22% |
| by:XAUUSDT | 2026-03-09 |  | 4 | 4.65% | 2.39% | 6.92% | 7.95% | 14.71% | 6.33% | 0.39% | 66% at 0.00% | 6% |
| hl:PAXG | 2025-04-06 |  | 1 | 8.12% | 9.42% | 6.82% | 8.91% | 10.25% | 8.24% | 7.86% | 68% at 10.95% | 12% |
| hl:cash:GOLD | 2026-02-05 | 2026-07-02 | 1 | 2.47% | 2.17% | 2.76% | 2.74% | 0.97% | 3.66% | -0.11% | 41% at 5.47% | 21% |
| hl:cash:SILVER | 2026-02-06 | 2026-07-01 | 1 | 3.94% | 3.96% | 3.92% | 3.95% | 4.04% | 5.80% | -0.02% | 45% at 5.47% | 16% |
| hl:flx:GOLD | 2025-12-12 | 2026-06-20 | 1 | 8.76% | 7.05% | 10.46% | 10.77% | 23.80% | 8.02% | 10.35% | 51% at 6.57% | 4% |
| hl:flx:SILVER | 2025-12-17 | 2026-06-19 | 1 | 5.75% | 6.49% | 5.00% | 4.86% | 5.60% | 7.89% | 1.04% | 48% at 6.57% | 9% |
| hl:km:GOLD | 2026-01-28 | 2026-06-17 | 1 | 7.33% | 7.99% | 6.68% | 7.40% | 5.15% | 8.74% | 4.29% | 55% at 5.00% | 13% |
| hl:km:SILVER | 2026-01-28 | 2026-06-17 | 1 | 7.38% | 8.54% | 6.23% | 9.00% | 6.76% | 5.99% | 10.40% | 46% at 5.00% | 17% |
| hl:xyz:GOLD | 2025-12-22 |  | 1 | 8.44% | 8.90% | 7.99% | 7.76% | 7.62% | 9.73% | 5.63% | 55% at 5.47% | 10% |
| hl:xyz:SILVER | 2025-12-26 |  | 1 | 10.12% | 10.98% | 9.25% | 8.30% | 7.97% | 11.93% | 6.20% | 50% at 5.47% | 10% |
| okx:XAG-USDT-SWAP | 2026-06-29 |  | 8 | 9.88% | 8.52% | 11.30% | 10.20% | 11.09% | 12.57% | 2.83% | 42% at 0.00% | 0% |
| okx:XAU-USDT-SWAP | 2026-06-29 |  | 8 | 7.45% | 3.52% | 11.42% | 8.10% | 13.00% | 10.07% | 0.59% | 55% at 0.00% | 4% |

## 4. Token premium over spot gold (bp)

| path | open hours | median | p05 | p95 | min | max | median while spot shut | sd of daily change |
|---|---|---|---|---|---|---|---|---|
| PAXG@binance / Binance XAU index (USDT) | 4982 | -4.0 | -28.6 | 48.5 | -67.6 | 155.1 | -15.1 | 10.4 |
| PAXG@coinbase (USD) / xyz:GOLD implied oracle (USD) | 3493 | -15.3 | -29.9 | 19.2 | -62.9 | 98.9 | -20.3 | 7.3 |
| PAXG@okx / OKX XAU-USDT index | 5647 | -6.0 | -25.4 | 47.7 | -57.1 | 103.3 | -2.2 | 6.8 |
| XAUT@binance / Binance XAU index (USDT) | 3250 | -20.7 | -55.8 | 3.1 | -104.9 | 17.8 | -31.3 | 9.5 |
| XAUT@bybit / Bybit XAU index | 3561 | -24.6 | -65.0 | 1.2 | -95.7 | 85.3 | -31.5 | 9.7 |
| XAUT@okx / OKX XAU-USDT index | 5647 | -19.3 | -52.4 | 3.7 | -89.6 | 50.1 | -21.0 | 7.0 |

Cross-check on the 150 common days 2026-03-16→2026-10-09: medians PAXG@binance -11.4, PAXG@coinbase (USD) -15.6, PAXG@okx -12.6; daily correlation Binance vs Coinbase/xyz 0.91, vs OKX 0.68.

Monthly medians:

- PAXG@binance / Binance XAU index (USDT) · 2025-12 41 · 2026-01 31 · 2026-02 21 · 2026-03 8 · 2026-04 -26 · 2026-05 -10 · 2026-06 -9 · 2026-07 -14 · 2026-08 -17 · 2026-09 1 · 2026-10 13
- XAUT@okx / OKX XAU-USDT index · 2025-10 -13 · 2025-11 -40 · 2025-12 0 · 2026-01 -5 · 2026-02 -19 · 2026-03 -25 · 2026-04 -30 · 2026-05 -19 · 2026-06 -39 · 2026-07 -22 · 2026-08 -45 · 2026-09 -4 · 2026-10 -2

## 5. Always-on detail (gross per notional; excess on capital)

| series | capital | funding | basis change | always, first half | always, second half | last 90d | by year | rebalances | days near liquidation | chosen vs savings rate paid | deflated Sharpe (168 trials) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hl:PAXG x PAXG@bn | cash10 | 8.10% | 0.13% | 4.39% | 1.69% | 3.06% | 2025 4.48%, 2026 1.66% | 29 | 3 | 1.79% | 0.87 |
| hl:PAXG x PAXG@bn | cash20 | 8.10% | 0.13% | 3.79% | 1.34% | 2.54% | 2025 3.87%, 2026 1.32% | 8 | 0 | 1.44% | 0.82 |
| bn:PAXGUSDT x PAXG@bn | collateral | 4.89% | -0.03% | 0.97% | 0.67% | 0.83% | 2025 0.98%, 2026 0.66% | 2 | 0 | 0.77% | 0.07 |
| bn:PAXGUSDT x PAXG@bn | cash10 | 4.89% | -0.03% | 0.40% | 0.10% | 0.28% | 2025 0.41%, 2026 0.09% | 29 | 3 | 0.20% | 0.02 |
| bn:PAXGUSDT x PAXG@bn | cash20 | 4.89% | -0.03% | 0.11% | -0.13% | -0.03% | 2025 0.12%, 2026 -0.13% | 8 | 1 | -0.03% | 0.01 |
| by:PAXGUSDT x PAXG@bn | cash10 | 6.74% | -0.02% | 3.77% | 0.42% | 2.56% | 2022 -0.89%, 2023 3.14%, 2024 6.87%, 2025 -0.76%, 2026 1.30% | 51 | 3 | -0.26% | 0.50 |
| by:PAXGUSDT x PAXG@bn | cash20 | 6.74% | -0.02% | 3.17% | 0.12% | 2.07% | 2022 -1.09%, 2023 2.59%, 2024 6.02%, 2025 -0.96%, 2026 0.95% | 15 | 1 | -0.34% | 0.45 |
| bn:XAUTUSDT x XAUT@bn | collateral | 5.12% | -0.14% | -0.40% | 1.63% | 1.36% | 2026 0.62% | 0 | 0 | 1.73% | 0.01 |
| bn:XAUTUSDT x XAUT@bn | cash10 | 5.12% | -0.14% | -0.82% | 0.98% | 0.72% | 2026 0.09% | 7 | 0 | 1.08% | 0.00 |
| bn:XAUTUSDT x XAUT@bn | cash20 | 5.12% | -0.14% | -0.99% | 0.69% | 0.46% | 2026 -0.15% | 0 | 0 | 0.73% | 0.00 |
| by:XAUTUSDT x XAUT@by | collateral | 4.81% | -0.16% | 0.15% | 1.01% | 0.66% | 2025 -0.00%, 2026 1.13% | 2 | 0 | 1.16% | 0.02 |
| by:XAUTUSDT x XAUT@by | cash10 | 4.81% | -0.16% | -0.32% | 0.41% | 0.09% | 2025 -0.46%, 2026 0.52% | 26 | 1 | 0.50% | 0.01 |
| by:XAUTUSDT x XAUT@by | cash20 | 4.81% | -0.16% | -0.58% | 0.13% | -0.11% | 2025 -0.71%, 2026 0.24% | 9 | 0 | 0.24% | 0.00 |
| bn:XAUUSDT x PAXG@bn | collateral | 13.11% | -0.66% | 13.75% | 2.63% | 2.04% | 2025 23.42%, 2026 7.11% | 2 | 0 | 2.73% | 0.05 |
| bn:XAUUSDT x PAXG@bn | cash10 | 13.11% | -0.66% | 11.87% | 1.96% | 1.37% | 2025 20.59%, 2026 5.95% | 17 | 1 | 2.06% | 0.05 |
| bn:XAUUSDT x PAXG@bn | cash20 | 13.11% | -0.66% | 10.65% | 1.59% | 1.03% | 2025 18.70%, 2026 5.23% | 4 | 0 | 1.69% | 0.04 |
| bn:XAUUSDT x XAUT@bn | collateral | 3.51% | -0.69% | -4.42% | 1.30% | 2.11% | 2026 -1.54% | 0 | 0 | -2.63% | 0.00 |
| by:XAUUSDT x XAUT@by | collateral | 4.68% | 0.43% | -0.26% | 1.81% | 3.48% | 2026 0.78% | 0 | 0 | 1.91% | 0.00 |
| by:XAUUSDT x XAUT@by | cash10 | 4.68% | 0.43% | -0.81% | 1.15% | 2.66% | 2026 0.17% | 11 | 0 | 1.25% | 0.00 |
| by:XAUUSDT x XAUT@by | cash20 | 4.68% | 0.43% | -0.98% | 0.79% | 2.17% | 2026 -0.09% | 3 | 0 | 0.89% | 0.00 |
| hl:xyz:GOLD x PAXG@bn | cash10 | 8.41% | -0.81% | 2.07% | 2.59% | 2.55% | 2025 -1.80%, 2026 2.46% | 16 | 1 | 2.69% | 0.01 |
| hl:xyz:GOLD x PAXG@bn | cash20 | 8.41% | -0.81% | 1.69% | 2.21% | 2.14% | 2025 -1.96%, 2026 2.07% | 4 | 0 | 2.31% | 0.01 |
| best_paxg_hedged | cash10 | — | — | 3.41% | 0.95% | 1.17% | 2022 -1.26%, 2023 2.90%, 2024 6.50%, 2025 0.08%, 2026 1.91% | 49 | 4 | 1.05% | 0.48 |
| best_xaut_hedged | cash10 | — | — | 0.69% | 1.79% | 0.16% | 2025 0.69%, 2026 1.77% | 24 | 1 | 1.89% | 0.02 |

Descriptive only (too short to split, or delisted):

| perp | token | capital | window | funding | basis | always excess | NW t |
|---|---|---|---|---|---|---|---|
| okx:XAU-USDT-SWAP | XAUT@okx | collateral | 2026-06-29→2026-10-09 | 7.50% | 0.10% | 2.71% | 0.83 |
| hl:km:GOLD | PAXG@bn | cash10 | 2026-01-29→2026-06-16 | 7.40% | -3.01% | -1.16% | -0.27 |
| hl:flx:GOLD | PAXG@bn | cash10 | 2025-12-13→2026-06-19 | 8.75% | 2.01% | 4.79% | 1.24 |
| hl:cash:GOLD | PAXG@bn | cash10 | 2026-02-06→2026-07-01 | 2.39% | 0.54% | -2.38% | -1.08 |

## 6. Capacity (books at 2026-10-10T17:56:48+00:00, a Saturday)

| perp | token | capital | perp bids ≤25bp | token asks ≤25bp (venue) | (all venues) | open interest | size | test excess | $/yr at size | next $1M extra cost bp (one way) | next $1M excess (1-yr hold) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hl:PAXG | PAXG@bn | cash10 | $1.02M | $1.04M | $2.13M | $23.66M | $1.02M | 1.69% | $20k | 64 | 0.57% |
| hl:PAXG | PAXG@bn | cash20 | $1.02M | $1.04M | $2.13M | $23.66M | $1.02M | 1.34% | $17k | 64 | 0.31% |
| bn:PAXGUSDT | PAXG@bn | collateral | $3.03M | $1.04M | $2.13M | $95.70M | $1.04M | 0.67% | $7k | 38 | -0.09% |
| bn:PAXGUSDT | PAXG@bn | cash10 | $3.03M | $1.04M | $2.13M | $95.70M | $2.13M | 0.10% | $2k | 68 | -1.13% |
| bn:PAXGUSDT | PAXG@bn | cash20 | $3.03M | $1.04M | $2.13M | $95.70M | $2.13M | -0.13% | $-3k | 68 | -1.25% |
| by:PAXGUSDT | PAXG@bn | cash10 | $688k | $1.04M | $2.13M | $19.05M | $688k | -0.02% | $-150 | 72 | -1.32% |
| by:PAXGUSDT | PAXG@bn | cash20 | $688k | $1.04M | $2.13M | $19.05M | $688k | -0.09% | $-781 | 72 | -1.29% |
| bn:XAUTUSDT | XAUT@bn | collateral | $1.19M | $553k | $2.05M | $51.24M | $553k | 1.63% | $9k | 78 | 0.07% |
| bn:XAUTUSDT | XAUT@bn | cash10 | $1.19M | $553k | $2.05M | $51.24M | $1.19M | 1.01% | $13k | 135 | -1.43% |
| bn:XAUTUSDT | XAUT@bn | cash20 | $1.19M | $553k | $2.05M | $51.24M | $1.19M | 0.64% | $9k | 135 | -1.60% |
| by:XAUTUSDT | XAUT@by | collateral | $1.06M | $459k | $2.05M | $141.53M | $459k | 0.95% | $4k | — | — |
| by:XAUTUSDT | XAUT@by | cash10 | $1.06M | $459k | $2.05M | $141.53M | $1.06M | 0.41% | $5k | — | — |
| by:XAUTUSDT | XAUT@by | cash20 | $1.06M | $459k | $2.05M | $141.53M | $1.06M | 0.13% | $2k | — | — |
| bn:XAUUSDT | PAXG@bn | collateral | $12.50M | $1.04M | $2.13M | $608.76M | $1.04M | 2.63% | $27k | 34 | 1.94% |
| bn:XAUUSDT | PAXG@bn | cash10 | $12.50M | $1.04M | $2.13M | $608.76M | $2.13M | 1.96% | $46k | 52 | 1.02% |
| bn:XAUUSDT | PAXG@bn | cash20 | $12.50M | $1.04M | $2.13M | $608.76M | $2.13M | 1.59% | $41k | 52 | 0.73% |
| bn:XAUUSDT | XAUT@bn | collateral | $12.50M | $553k | $2.05M | $608.76M | $553k | -2.70% | $-15k | 60 | -3.91% |
| by:XAUUSDT | XAUT@by | collateral | $2.69M | $459k | $2.05M | $111.94M | $459k | 1.81% | $8k | — | — |
| by:XAUUSDT | XAUT@by | cash10 | $2.69M | $459k | $2.05M | $111.94M | $2.05M | 1.15% | $26k | — | — |
| by:XAUUSDT | XAUT@by | cash20 | $2.69M | $459k | $2.05M | $111.94M | $2.05M | 0.79% | $20k | — | — |
| hl:xyz:GOLD | PAXG@bn | cash10 | $2.29M | $1.04M | $2.13M | $299.49M | $2.13M | 2.59% | $62k | 75 | 1.25% |
| hl:xyz:GOLD | PAXG@bn | cash20 | $2.29M | $1.04M | $2.13M | $299.49M | $2.13M | 2.21% | $57k | 75 | 0.97% |

Token asks within 25bp: PAXG $2.13M (bn_spot:PAXGUSDC $60k, bn_spot:PAXGUSDT $1.04M, coinbase_spot:PAXG-USD $339k, kraken_spot:PAXGUSD $459k, okx:PAXG-USDT $232k); XAUT $2.05M (bitfinex_spot:XAUT:USD $58k, bitfinex_spot:XAUT:UST $301k, bn_spot:XAUTUSDC $67k, bn_spot:XAUTUSDT $553k, by_spot:XAUTUSDT $459k, okx:XAUT-USDT $614k)

## 7. Late entry (test period)

| series | capital | rule | on time | 1 hour late | 1 day late | kept (1h) | kept (1d) |
|---|---|---|---|---|---|---|---|
| hl:PAXG x PAXG@bn | cash10 | always | 1.69% | 1.69% | 1.69% | 1.00 | 1.00 |
| hl:PAXG x PAXG@bn | cash20 | always | 1.34% | 1.34% | 1.34% | 1.00 | 1.00 |
| bn:PAXGUSDT x PAXG@bn | collateral | always | 0.67% | 0.67% | 0.67% | 1.00 | 1.00 |
| bn:PAXGUSDT x PAXG@bn | cash10 | always | 0.10% | 0.10% | 0.10% | 1.00 | 1.00 |
| bn:PAXGUSDT x PAXG@bn | cash20 | always | -0.13% | -0.13% | -0.13% | — | — |
| by:PAXGUSDT x PAXG@bn | cash10 | trail30d_x5pp | -0.02% | -0.02% | 0.02% | — | — |
| by:PAXGUSDT x PAXG@bn | cash20 | trail30d_x5pp | -0.09% | -0.09% | -0.06% | — | — |
| bn:XAUTUSDT x XAUT@bn | collateral | trail30d_x0pp | 1.63% | 1.63% | 1.63% | 1.00 | 1.00 |
| bn:XAUTUSDT x XAUT@bn | cash10 | trail30d_x0pp | 1.01% | 1.01% | 1.01% | 1.00 | 1.00 |
| bn:XAUTUSDT x XAUT@bn | cash20 | trail30d_x0pp | 0.64% | 0.64% | 0.64% | 1.00 | 1.00 |
| by:XAUTUSDT x XAUT@by | collateral | trail30d_x0pp | 0.95% | 0.95% | 1.00% | 1.00 | 1.06 |
| by:XAUTUSDT x XAUT@by | cash10 | trail30d_x0pp | 0.41% | 0.41% | 0.41% | 1.00 | 1.00 |
| by:XAUTUSDT x XAUT@by | cash20 | trail30d_x0pp | 0.13% | 0.13% | 0.14% | 1.00 | 1.05 |
| bn:XAUUSDT x PAXG@bn | collateral | always | 2.63% | 2.63% | 2.63% | 1.00 | 1.00 |
| bn:XAUUSDT x PAXG@bn | cash10 | always | 1.96% | 1.96% | 1.96% | 1.00 | 1.00 |
| bn:XAUUSDT x PAXG@bn | cash20 | always | 1.59% | 1.59% | 1.59% | 1.00 | 1.00 |
| bn:XAUUSDT x XAUT@bn | collateral | trail7d_x0pp | -2.70% | -2.70% | -2.44% | — | — |
| by:XAUUSDT x XAUT@by | collateral | always | 1.81% | 1.81% | 1.81% | 1.00 | 1.00 |
| by:XAUUSDT x XAUT@by | cash10 | always | 1.15% | 1.15% | 1.15% | 1.00 | 1.00 |
| by:XAUUSDT x XAUT@by | cash20 | always | 0.79% | 0.79% | 0.79% | 1.00 | 1.00 |
| hl:xyz:GOLD x PAXG@bn | cash10 | always | 2.59% | 2.59% | 2.59% | 1.00 | 1.00 |
| hl:xyz:GOLD x PAXG@bn | cash20 | always | 2.21% | 2.21% | 2.21% | 1.00 | 1.00 |
| best_paxg_hedged | cash10 | trail30d_x5pp | 1.56% | 1.56% | 1.71% | 1.00 | 1.09 |
| best_xaut_hedged | cash10 | always | 1.79% | 1.79% | 1.79% | 1.00 | 1.00 |

## 8. Risks

Weekend change of the token-minus-perp basis (Friday close → one hour after the Sunday reopen, bp):

| pair | weekends | median | p05 | p95 | worst | sd |
|---|---|---|---|---|---|---|
| bn:PAXGUSDT x PAXG@bn | 80 | -0.2 | -4.9 | 4.0 | -7.8 | 3.4 |
| bn:XAUUSDT x PAXG@bn | 43 | 1.6 | -14.8 | 33.9 | -75.7 | 19.3 |
| by:XAUUSDT x XAUT@by | 30 | 3.7 | -12.9 | 21.6 | -22.1 | 11.0 |
| hl:PAXG x PAXG@bn | 78 | -0.5 | -7.9 | 6.7 | -14.2 | 4.6 |
| hl:xyz:GOLD x PAXG@bn | 41 | 0.9 | -20.3 | 35.2 | -25.1 | 16.3 |

Funding against gold's own monthly return (gold by year: 2020 26%, 2021 -5%, 2022 -1%, 2023 11%, 2024 29%, 2025 65%, 2026 -4%):

| market | months | corr | mean APR, gold up months | down months | by year |
|---|---|---|---|---|---|
| bn:PAXGUSDT | 18 | -0.22 | 4.29% | 5.90% | 2025 5.03%, 2026 4.62% |
| bn:XAUUSDT | 10 | 0.25 | 20.53% | 6.71% | 2025 28.95%, 2026 11.92% |
| by:PAXGUSDT | 54 | -0.15 | 2.75% | 9.61% | 2022 2.94%, 2023 8.15%, 2024 12.01%, 2025 0.93%, 2026 2.98% |
| by:XAUTUSDT | 18 | -0.10 | 4.18% | 5.24% | 2025 3.93%, 2026 5.14% |
| hl:PAXG | 18 | 0.08 | 8.10% | 8.09% | 2025 9.54%, 2026 6.66% |
| hl:xyz:GOLD | 9 | — | 11.25% | 6.05% | 2026 8.36% |

Delisted HIP-3 metal markets (live: xyz:GOLD and xyz:SILVER only; 6 gold and 6 silver HIP-3 markets on other builders are flagged isDelisted in the venue metadata (2026-10-10); no data served for hyna:GOLD, mkts:GOLD, vntl:GOLDJM, hyna:SILVER, mkts:SILVER, vntl:SILVERJM):

| market | first funding | last trade | days live | funding while live | PAXG over last trade (bp) | carry excess (always, cash10) |
|---|---|---|---|---|---|---|
| hl:km:GOLD | 2026-01-28 | 2026-06-17 | 139 | 7.33% | -59.3 | -1.16% |
| hl:flx:GOLD | 2025-12-12 | 2026-06-20 | 189 | 8.76% | 4.2 | 4.79% |
| hl:cash:GOLD | 2026-02-05 | 2026-07-02 | 146 | 2.47% | -5.2 | -2.38% |
| hl:km:SILVER | 2026-01-28 | 2026-06-17 | 139 | 7.38% | — | — |
| hl:flx:SILVER | 2025-12-17 | 2026-06-19 | 183 | 5.75% | — | — |
| hl:cash:SILVER | 2026-02-06 | 2026-07-01 | 144 | 3.94% | — | — |

## 9. Collateral, issuers, token supply

- Binance portfolio margin collateral rates: {"BTC": 0.95, "ETH": 0.95, "PAXG": 0.8, "USDC": 0.9999, "USDT": 0.9999, "XAUT": 0.8}; multi-assets mode lists gold: False
- Bybit UTA tiers (max qty, ratio): {"PAXG": [], "XAUT": [["40", 0.9], ["180", 0.85], ["360", 0.8], ["540", 0.7], ["99999999999", 0.6], ["", 0.0]]}
- OKX tiers (min, max, discount): {"PAXG": [["0", "12", 0.85], ["12", "20", 0.8], ["20", "32", 0.75], ["32", "52", 0.7], ["52", "72", 0.65], ["72", "92", 0.6], ["92", "112", 0.55], ["112", "132", 0.5]], "XAUT": [["0", "50", 0.95], ["50", "75", 0.91], ["75", "100", 0.89], ["100", "150", 0.87], ["150", "200", 0.85], ["200", "250", 0.83], ["250", "300", 0.81], ["300", "350", 0.79]]}
- Hyperliquid: BTC and HYPE only (docs read 2026-10-10, term_carry); no gold token; HyperCore spot gold pairs: [{"day_ntl_vlm": 0.0, "mark": 0.3696, "pair": "@182", "tokens": ["XAUT0", "USDC"]}, {"day_ntl_vlm": 0.0, "mark": 0.01017, "pair": "@209", "tokens": ["XAUT0", "USDT0"]}, {"day_ntl_vlm": 0.0, "mark": 0.5, "pair": "@715", "tokens": ["XAUM", "USDC"]}]
- PAXG: Paxos Trust Company (NYDFS-regulated); 1 PAXG = 1 fine troy oz in London Good Delivery bars. Redeem: Paxos account holders (onboarded, KYC) can sell PAXG to Paxos for USD at the gold price or take allocated bars/unallocated gold; physical bars need about 430 oz plus fees (third-party guides; the official minimums article was not read). Fees: creation waived through 2027-01-01 (then 0.02 PAXG under 2 oz, 1.0% → 0.125% by size); redemption 0.125% on the first $2M of 30-day net redemptions, 0.25% to $10M, 0.35% to $20M, 0.5% above (from 2026-09-01); in-kind conversion to bars 0.05%; no storage fee.
- XAUT: TG Commodities Limited (Tether Gold); 1 XAUT = 1 troy oz in a Swiss vault. Redeem: verified TG Commodities customers (non-US); physical delivery to a Swiss address, minimum about 430 XAUT per third-party listings; USD redemption possible. Fees: 0.25% on creation and redemption plus a 150 USDT verification fee (third-party listings: rwa.xyz, MEXC; Tether's own terms page is script-rendered and was not read).
- PAXG on Ethereum: 436458 oz ($1.83B); top-20 DEX pools hold $32.64M, trade $1.40M a day; largest: PAXG / WETH uniswap_v2 $15.59M; PAXG / XAUt 0.01% uniswap_v3 $5.83M; PAXG / XAUt 0.05% uniswap_v3 $3.23M; PAXG / XAUt fluid-ethereum $2.33M
- XAUT on Ethereum: 827418 oz ($3.46B); top-20 DEX pools hold $44.09M, trade $1.51M a day; largest: GOLDGR / XAUt 0.01% pancakeswap-v3-ethereum $15.86M; PAXG / XAUt 0.01% uniswap_v3 $5.83M; XAUt / USDT 0.05% uniswap_v3 $5.34M; XAUt / USDT 0.05% uniswap-v4-ethereum $4.11M

## 10. Verification

```
{
 "bn_rent_map_vs_fresh:PAXGUSDT": {
  "max_abs_diff": 0.0,
  "overlap": 552
 },
 "bn_rent_map_vs_fresh:XAGUSDT": {
  "max_abs_diff": 0.0,
  "overlap": 552
 },
 "bn_rent_map_vs_fresh:XAUTUSDT": {
  "max_abs_diff": 0.0,
  "overlap": 552
 },
 "bn_rent_map_vs_fresh:XAUUSDT": {
  "max_abs_diff": 0.0,
  "overlap": 552
 },
 "headline_recomputed": {
  "basis_change_from_hourly_closes": -9.271892142437288e-05,
  "block": "hl:xyz:GOLD x PAXG@bn",
  "excess_before_rebalancing_costs": 0.029183880481404585,
  "funding_apr_from_raw_rows": 0.08026210066551724,
  "model": "cash10",
  "simulator_oos_excess": 0.025946608189138784,
  "test_days": 145,
  "window": [
   "2026-05-18",
   "2026-10-09"
  ]
 },
 "hl_formula:PAXG": {
  "apr_formula_mean": 0.08118722428991691,
  "apr_reported_mean": 0.08118722309161527,
  "rows": 13250,
  "within_0p001pct": 1.0
 },
 "hl_formula:xyz:GOLD": {
  "apr_formula_mean": 0.08442812413606865,
  "apr_reported_mean": 0.08442812344886291,
  "rows": 7011,
  "within_0p001pct": 1.0
 },
 "hl_formula:xyz:SILVER": {
  "apr_formula_mean": 0.10189828850309969,
  "apr_reported_mean": 0.10115563058334232,
  "rows": 6929,
  "within_0p001pct": 0.9946601241160341
 },
 "hl_store_vs_fresh:PAXG": {
  "identical_share": 1.0,
  "max_abs_diff": 0.0,
  "overlap_hours": 8971
 },
 "hl_store_vs_fresh:xyz:GOLD": {
  "identical_share": 1.0,
  "max_abs_diff": 0.0,
  "overlap_hours": 6988
 },
 "hl_store_vs_fresh:xyz:SILVER": {
  "identical_share": 1.0,
  "max_abs_diff": 0.0,
  "overlap_hours": 6906
 },
 "paxg_premium_three_paths": {
  "corr_daily_binance_vs_coinbase": 0.9079851696368271,
  "corr_daily_binance_vs_okx": 0.6849451826418101,
  "days": 150,
  "first": "2026-03-16",
  "last": "2026-10-09",
  "median_of_daily_medians": {
   "PAXG@binance / Binance XAU index (USDT)": -0.001139807049801489,
   "PAXG@coinbase (USD) / xyz:GOLD implied oracle (USD)": -0.0015640567885958911,
   "PAXG@okx / OKX XAU-USDT index": -0.0012644438279279524
  }
 }
}
```

## 11. API gaps

- Spot XAU/USD history: Yahoo XAUUSD=X is gone (404) and Pyth Benchmarks history returns 401/404 without a key; Binance's XAU index (spot feeds dxFeed/Kaiko/Massive/Pyth plus xyz:GOLD) is the spot reference, GC=F the futures
- stooq.com serves a JavaScript proof-of-work page to scripts; not used
- OKX serves 3 months of funding history (from 2026-06-29) and XAU index candles from 2025-10-31 only
- Hyperliquid does not serve oracle history; its oracle is implied as close / (1 + hourly average premium)
- Hyperliquid PAXG funding history starts 2025-04-06 although daily candles start 2025-03-27
- HIP-3 hyna/mkts/vntl gold and silver markets (all delisted) return no funding or candles
- Binance TradFi perps (XAUUSDT) inside portfolio margin: not confirmed from public data; collateral rates are for the PM account (PAXG and XAUT 0.80)
- Bitfinex XAUT books are thin; Kraken/Coinbase PAXG books are USD-quoted (no stablecoin conversion applied)
- Tether Gold's official terms page renders by script; XAUT redemption terms are from third-party listings
- Book depth is one Saturday snapshot (2026-10-10); weekday books for the XAU perps were not read

Multiple testing: 168 variants; BH q=0.10 survivors: hl:PAXG x PAXG@bn|cash10|trail30d_x2pp, hl:PAXG x PAXG@bn|cash20|trail30d_x2pp, bn:PAXGUSDT x PAXG@bn|collateral|trail7d_x5pp, bn:PAXGUSDT x PAXG@bn|cash10|trail7d_x5pp, bn:PAXGUSDT x PAXG@bn|cash20|trail7d_x2pp, bn:PAXGUSDT x PAXG@bn|cash20|trail7d_x5pp, bn:PAXGUSDT x PAXG@bn|cash20|trail30d_x2pp, bn:XAUTUSDT x XAUT@bn|collateral|always, bn:XAUTUSDT x XAUT@bn|collateral|trail30d_x0pp, bn:XAUTUSDT x XAUT@bn|collateral|trail30d_x2pp, by:XAUTUSDT x XAUT@by|collateral|trail7d_x2pp, by:XAUTUSDT x XAUT@by|cash10|trail7d_x2pp, by:XAUTUSDT x XAUT@by|cash20|trail7d_x2pp; among chosen: bn:XAUTUSDT x XAUT@bn|collateral|trail30d_x0pp.
