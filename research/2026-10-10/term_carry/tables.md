# Term carry — tables

Generated 2026-10-10T11:52:02+00:00 from `analysis.json`. Benchmark: SSR 3.80% a year unless a column says "vs savings paid" (Maker DSR, then the SSR, as paid at the time). Excess is per year on the capital the trade ties up.

## Funding a short perp received, by year (annualised mean of daily sums)

| series | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| binance:BTC | +7.4% | +17.2% | +30.6% | +4.2% | +7.9% | +11.9% | +5.1% | +2.9% |
| binance:ETH | +8.9% | +27.4% | +37.5% | +0.8% | +8.3% | +12.9% | +4.9% | +2.0% |
| binance:HYPE | — | — | — | — | — | — | +13.4% | +4.5% |
| binance:SOL | — | -13.0% | +28.8% | -38.1% | +1.4% | +13.6% | +0.4% | -1.0% |
| hl:BTC | — | — | — | — | +13.5% | +24.1% | +10.6% | +5.2% |
| hl:ETH | — | — | — | — | +20.0% | +22.0% | +8.5% | +5.9% |
| hl:HYPE | — | — | — | — | — | +117.3% | +22.0% | +9.1% |
| hl:SOL | — | — | — | — | +11.7% | +28.1% | +5.3% | +0.2% |
| susde | — | — | — | — | +0.0% | +13.4% | +6.0% | +4.0% |
| wsteth_staking | — | — | +5.7% | +4.5% | +4.4% | +3.2% | +2.8% | +2.4% |
| savings_paid | +3.9% | +1.5% | +0.0% | +0.1% | +2.9% | +7.8% | +5.5% | +3.7% |

sUSDe realised from 2024-07-01: 6.3% a year; savings rate paid over the same days: 5.3%.

## (a) Dated basis: the locked yield of buy-spot / sell-the-future held to expiry

| venue | days | span | locked excess, mean | median | share ≥ +2pp | vs savings paid, mean |
|---|---:|---|---:|---:|---:|---:|
| binance:BTC (portfolio) | 2076 | 2021-02-03 → 2026-10-10 | +2.6% | +0.8% | 43% | +2.2% |
| binance:ETH (portfolio) | 2075 | 2021-02-04 → 2026-10-10 | +1.9% | +0.2% | 37% | +1.5% |
| cme:BTC (cme_tbill) | 499 | 2024-10-11 → 2026-10-09 | +0.4% | +0.1% | 21% | -0.5% |
| cme:ETH (cme_tbill) | 495 | 2024-10-11 → 2026-10-09 | +0.3% | +0.0% | 26% | -0.6% |
| deribit:BTC (portfolio) | 2511 | 2018-10-05 → 2026-10-10 | +1.9% | +0.8% | 42% | +2.6% |
| deribit:ETH (portfolio) | 2474 | 2019-03-29 → 2026-10-10 | +1.0% | -0.3% | 35% | +1.9% |

### By year (front | next quarterly): mean annualised basis, mean locked excess, share of days ≥ +2pp

| venue | year | front basis | front excess | front ≥2pp | next basis | next excess | next ≥2pp |
|---|---|---:|---:|---:|---:|---:|---:|
| binance:BTC | 2021 | +18.5% | +12.1% | 67% | +13.8% | +8.9% | 77% |
| binance:BTC | 2022 | +2.5% | -3.8% | 5% | +1.9% | -2.9% | 4% |
| binance:BTC | 2023 | +6.4% | +0.1% | 31% | +7.4% | +2.8% | 44% |
| binance:BTC | 2024 | +12.7% | +6.4% | 88% | +12.5% | +7.9% | 100% |
| binance:BTC | 2025 | +6.5% | +0.2% | 23% | +7.0% | +2.4% | 50% |
| binance:BTC | 2026 | +3.1% | -3.1% | 0% | +3.5% | -1.1% | 0% |
| binance:ETH | 2021 | +20.3% | +13.9% | 72% | +14.8% | +9.9% | 77% |
| binance:ETH | 2022 | -0.3% | -6.6% | 5% | +0.5% | -4.3% | 4% |
| binance:ETH | 2023 | +5.0% | -1.3% | 6% | +5.9% | +1.2% | 37% |
| binance:ETH | 2024 | +12.9% | +6.6% | 82% | +12.5% | +7.9% | 94% |
| binance:ETH | 2025 | +5.8% | -0.5% | 19% | +6.3% | +1.7% | 36% |
| binance:ETH | 2026 | +2.2% | -4.0% | 0% | +2.7% | -1.9% | 0% |
| cme:BTC | 2024 | +12.2% | +4.5% | 81% | — | — | — |
| cme:BTC | 2025 | +7.0% | +0.6% | 27% | — | — | — |
| cme:BTC | 2026 | +5.0% | -0.7% | 1% | — | — | — |
| cme:ETH | 2024 | +13.6% | +5.5% | 93% | — | — | — |
| cme:ETH | 2025 | +7.1% | +0.7% | 32% | — | — | — |
| cme:ETH | 2026 | +4.1% | -1.4% | 4% | — | — | — |
| deribit:BTC | 2018 | — | — | — | -3.9% | -8.5% | 0% |
| deribit:BTC | 2019 | +3.6% | -3.2% | 30% | +3.1% | -1.6% | 33% |
| deribit:BTC | 2020 | +8.7% | +2.2% | 48% | +7.0% | +2.4% | 51% |
| deribit:BTC | 2021 | +14.8% | +8.3% | 65% | +13.5% | +8.9% | 84% |
| deribit:BTC | 2022 | +1.5% | -5.0% | 4% | +2.2% | -2.4% | 7% |
| deribit:BTC | 2023 | +5.0% | -1.5% | 18% | +4.9% | +0.2% | 22% |
| deribit:BTC | 2024 | +12.2% | +5.7% | 83% | +12.0% | +7.4% | 99% |
| deribit:BTC | 2025 | +6.9% | +0.4% | 27% | +7.1% | +2.5% | 55% |
| deribit:BTC | 2026 | +3.2% | -3.2% | 0% | +3.7% | -1.0% | 0% |
| deribit:ETH | 2019 | +8.4% | +1.7% | 55% | +6.3% | +1.6% | 42% |
| deribit:ETH | 2020 | +8.0% | +1.4% | 38% | +6.1% | +1.5% | 38% |
| deribit:ETH | 2021 | +14.8% | +8.3% | 65% | +14.1% | +9.5% | 84% |
| deribit:ETH | 2022 | -1.0% | -7.5% | 4% | +1.0% | -3.6% | 5% |
| deribit:ETH | 2023 | +3.5% | -2.9% | 9% | +3.8% | -0.8% | 14% |
| deribit:ETH | 2024 | +11.4% | +5.0% | 72% | +11.3% | +6.6% | 92% |
| deribit:ETH | 2025 | +5.5% | -1.0% | 17% | +5.8% | +1.2% | 25% |
| deribit:ETH | 2026 | +2.3% | -4.1% | 0% | +2.8% | -1.8% | 0% |

### The rule, chosen on the first half of each venue's days, tested once on the rest

| venue | split | chosen | in-sample ann excess | test ann excess | test trades | mean locked excess / trade | t (trades) | time in trade | alt capital | vs savings paid |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| binance:BTC | 2023-12-08 | next_x2pp | +5.11% | +5.37% | 4 | +7.1% | 2.00 | 80% | +3.30% (cash3x) | +3.49% |
| binance:ETH | 2023-12-08 | front_x0pp | +4.98% | +4.89% | 8 | +6.4% | 2.51 | 66% | +3.14% (cash3x) | +2.92% |
| cme:BTC | 2025-10-10 | front_x2pp | +3.40% | +1.09% | 1 | +10.5% | — | 15% | +1.03% (cme_idle) | +1.17% |
| cme:ETH | 2025-10-10 | front_x2pp | +3.59% | +0.45% | 2 | +2.6% | — | 18% | +0.14% (cme_idle) | +0.58% |
| deribit:BTC | 2022-10-08 | next_x8pp | +4.70% | +3.47% | 4 | +10.0% | 6.08 | 36% | +1.10% (cash3x) | +0.84% |
| deribit:ETH | 2023-01-03 | next_x8pp | +5.86% | +2.36% | 3 | +10.1% | 5.98 | 23% | +1.90% (cash3x) | +0.69% |

## (b) Long spot / short perp: rules chosen before 2024-07-01, tested after (daily excess over the benchmark on capital)

| block | capital | bench | chosen | in-sample | test | test NW t | deflated SR (IS) | always-on test | always NW t | test bootstrap 95%% | top-4-week share |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| binance:BTC | collateral | const | always | +10.72% | +1.18% | 2.63 | 1.00 | +1.18% | 1.50 | -0.2%…+2.7% | 44% |
| binance:BTC | collateral | hist | always | +12.49% | -0.32% | -0.79 | 1.00 | -0.32% | -0.48 | -1.5%…+1.0% | — |
| binance:BTC | cash3x | const | always | +6.86% | -0.24% | -0.71 | 1.00 | -0.24% | -0.41 | -1.3%…+0.9% | — |
| binance:BTC | cash5x | const | always | +7.87% | +0.14% | 0.37 | 1.00 | +0.14% | 0.21 | -1.0%…+1.4% | 285% |
| hl:BTC | collateral | const | trail7d_x5pp | +17.74% | +4.53% | 5.02 | 1.00 | +5.68% | 4.12 | +2.0%…+7.6% | 27% |
| hl:BTC | collateral | hist | trail7d_x2pp | +15.50% | +2.68% | 3.09 | 1.00 | +4.18% | 3.56 | +0.3%…+5.4% | 41% |
| hl:BTC | cash3x | const | trail7d_x5pp | +13.05% | +3.11% | 4.63 | 1.00 | +3.83% | 3.64 | +1.2%…+5.4% | 30% |
| hl:BTC | cash5x | const | trail7d_x5pp | +14.74% | +3.73% | 4.93 | 1.00 | +4.66% | 3.96 | +1.6%…+6.4% | 28% |
| best:BTC | cash3x | const | trail7d_x5pp | +12.63% | +3.12% | 4.63 | 1.00 | +3.84% | 3.64 | +1.2%…+5.4% | 30% |
| best:BTC | cash3x | hist | trail7d_x5pp | +10.50% | +1.37% | 2.32 | 1.00 | +2.34% | 2.69 | -0.1%…+3.2% | 60% |
| binance:ETH | collateral | const | trail30d_x2pp | +14.47% | +1.21% | 2.74 | 1.00 | +1.04% | 1.21 | -0.0%…+2.8% | 53% |
| binance:ETH | collateral | hist | trail30d_x0pp | +16.03% | +0.08% | 0.19 | 1.00 | -0.45% | -0.63 | -1.0%…+1.3% | 651% |
| binance:ETH | cash3x | const | trail30d_x2pp | +9.77% | +0.40% | 1.31 | 1.00 | -0.42% | -0.66 | -0.4%…+1.4% | 106% |
| binance:ETH | cash5x | const | trail30d_x2pp | +11.04% | +0.56% | 1.57 | 1.00 | -0.27% | -0.38 | -0.4%…+1.8% | 88% |
| hl:ETH | collateral | const | trail30d_x0pp | +18.08% | +4.51% | 4.79 | 1.00 | +4.65% | 2.86 | +1.8%…+7.8% | 32% |
| hl:ETH | collateral | hist | trail30d_x2pp | +15.83% | +2.99% | 3.38 | 1.00 | +3.15% | 2.14 | +0.6%…+5.9% | 44% |
| hl:ETH | cash3x | const | trail30d_x0pp | +13.23% | +3.11% | 4.36 | 1.00 | +3.08% | 2.52 | +1.1%…+5.6% | 35% |
| hl:ETH | cash5x | const | trail30d_x0pp | +15.00% | +3.61% | 4.52 | 1.00 | +3.63% | 2.65 | +1.3%…+6.4% | 34% |
| best:ETH | cash3x | const | trail30d_x2pp | +13.28% | +2.29% | 3.91 | 1.00 | +2.39% | 2.69 | +0.7%…+4.1% | 37% |
| best:ETH | cash3x | hist | trail30d_x5pp | +10.58% | +0.95% | 2.02 | 1.00 | +0.90% | 1.15 | -0.1%…+2.2% | 73% |
| binance:wstETH | cash3x | const | trail30d_x0pp | +7.41% | +1.35% | 3.39 | 1.00 | +1.56% | 2.34 | +0.2%…+2.7% | 38% |
| hl:wstETH | cash3x | const | trail30d_x0pp | +15.42% | +4.80% | 6.48 | 1.00 | +5.08% | 4.12 | +2.6%…+7.5% | 24% |
| binance:SOL | collateral | const | trail30d_x5pp | +9.11% | +0.52% | 1.41 | 1.00 | -2.30% | -1.95 | -0.3%…+1.8% | 122% |
| binance:SOL | collateral | hist | trail30d_x5pp | +10.12% | +0.19% | 0.64 | 1.00 | -3.80% | -3.39 | -0.3%…+1.0% | 211% |
| binance:SOL | cash3x | const | trail30d_x5pp | +5.93% | +0.28% | 1.12 | 1.00 | -3.12% | -3.45 | -0.3%…+1.1% | 146% |
| binance:SOL | cash5x | const | trail30d_x5pp | +6.56% | +0.32% | 1.09 | 1.00 | -3.33% | -3.31 | -0.3%…+1.3% | 151% |
| hl:SOL | collateral | const | trail7d_x0pp | +22.69% | +2.44% | 1.98 | 1.00 | +1.68% | 0.75 | -1.1%…+6.6% | 69% |
| hl:SOL | collateral | hist | trail30d_x0pp | +19.86% | +2.88% | 2.83 | 1.00 | +0.18% | 0.09 | +0.1%…+6.3% | 54% |
| hl:SOL | cash3x | const | trail7d_x0pp | +16.75% | +1.48% | 1.60 | 1.00 | +0.78% | 0.46 | -1.2%…+4.6% | 84% |
| hl:SOL | cash5x | const | trail7d_x0pp | +18.62% | +1.72% | 1.66 | 1.00 | +1.01% | 0.53 | -1.3%…+5.2% | 81% |
| best:SOL | cash3x | const | trail30d_x5pp | +14.69% | +2.59% | 3.47 | 1.00 | +0.25% | 0.14 | +0.5%…+5.4% | 48% |
| best:SOL | cash3x | hist | trail30d_x0pp | +12.29% | +1.47% | 1.94 | 1.00 | -1.25% | -0.79 | -0.5%…+3.9% | 77% |
| binance:HYPE | collateral | const | always | +8.21% | +0.45% | 0.48 | 1.00 | +0.45% | 0.52 | -1.3%…+2.2% | 188% |
| binance:HYPE | collateral | hist | always | +7.64% | +0.63% | 0.67 | 1.00 | +0.63% | 0.71 | -1.2%…+2.5% | 139% |
| binance:HYPE | cash3x | const | always | +4.47% | -1.09% | -1.48 | 0.99 | -1.09% | -1.69 | -2.4%…+0.2% | — |
| binance:HYPE | cash5x | const | always | +5.10% | -1.25% | -1.54 | 0.99 | -1.25% | -1.61 | -2.9%…+0.3% | — |
| hl:HYPE | collateral | const | always | +25.23% | +4.30% | 5.68 | 1.00 | +4.30% | 5.57 | +2.9%…+5.7% | 27% |
| hl:HYPE | collateral | hist | always | +22.81% | +4.36% | 5.76 | 1.00 | +4.36% | 5.74 | +2.9%…+5.7% | 27% |
| hl:HYPE | cash3x | const | always | +18.36% | +2.69% | 4.85 | 1.00 | +2.69% | 4.88 | +1.6%…+3.7% | 32% |
| hl:HYPE | cash5x | const | always | +20.43% | +3.01% | 4.86 | 1.00 | +3.01% | 4.88 | +1.8%…+4.1% | 31% |
| best:HYPE | cash3x | const | always | +5.82% | +2.04% | 2.83 | 1.00 | +2.04% | 2.98 | +0.4%…+3.4% | 51% |
| best:HYPE | cash3x | hist | always | +5.28% | +2.25% | 3.10 | 1.00 | +2.25% | 3.16 | +0.6%…+3.7% | 48% |

Variants tried: 196; BH survivors at q=0.10 (full sample, NW 30 lags): 173 — binance:BTC:collateral:always, binance:BTC:collateral:trail7d_x0pp, binance:BTC:collateral:trail7d_x2pp, binance:BTC:collateral:trail7d_x5pp, binance:BTC:collateral:trail30d_x0pp, binance:BTC:collateral:trail30d_x2pp, binance:BTC:collateral:trail30d_x5pp, binance:BTC:cash3x:always, binance:BTC:cash3x:trail7d_x0pp, binance:BTC:cash3x:trail7d_x2pp, binance:BTC:cash3x:trail7d_x5pp, binance:BTC:cash3x:trail30d_x0pp, binance:BTC:cash3x:trail30d_x2pp, binance:BTC:cash3x:trail30d_x5pp, binance:BTC:cash5x:always, binance:BTC:cash5x:trail7d_x0pp, binance:BTC:cash5x:trail7d_x2pp, binance:BTC:cash5x:trail7d_x5pp, binance:BTC:cash5x:trail30d_x0pp, binance:BTC:cash5x:trail30d_x2pp, binance:BTC:cash5x:trail30d_x5pp, hl:BTC:collateral:always, hl:BTC:collateral:trail7d_x0pp, hl:BTC:collateral:trail7d_x2pp, hl:BTC:collateral:trail7d_x5pp, hl:BTC:collateral:trail30d_x0pp, hl:BTC:collateral:trail30d_x2pp, hl:BTC:collateral:trail30d_x5pp, hl:BTC:cash3x:always, hl:BTC:cash3x:trail7d_x0pp, hl:BTC:cash3x:trail7d_x2pp, hl:BTC:cash3x:trail7d_x5pp, hl:BTC:cash3x:trail30d_x0pp, hl:BTC:cash3x:trail30d_x2pp, hl:BTC:cash3x:trail30d_x5pp, hl:BTC:cash5x:always, hl:BTC:cash5x:trail7d_x0pp, hl:BTC:cash5x:trail7d_x2pp, hl:BTC:cash5x:trail7d_x5pp, hl:BTC:cash5x:trail30d_x0pp

### Chosen rule by calendar year (annualised excess on capital, constant SSR)

| block | capital | chosen | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| binance:BTC | collateral | always | +3.1% | +13.3% | +26.9% | +0.4% | +4.0% | +8.2% | +1.3% | -1.1% |
| binance:BTC | cash3x | always | +1.1% | +8.7% | +18.8% | -0.8% | +1.9% | +5.0% | -0.0% | -1.9% |
| binance:BTC | cash5x | always | +1.5% | +9.9% | +21.1% | -0.7% | +2.5% | +5.9% | +0.3% | -1.8% |
| hl:BTC | collateral | trail7d_x5pp | — | — | — | — | +11.9% | +18.6% | +4.4% | -0.2% |
| hl:BTC | cash3x | trail7d_x5pp | — | — | — | — | +8.8% | +13.5% | +3.0% | -0.3% |
| hl:BTC | cash5x | trail7d_x5pp | — | — | — | — | +10.0% | +15.3% | +3.7% | -0.2% |
| best:BTC | cash3x | trail7d_x5pp | — | — | — | — | +7.3% | +13.5% | +3.0% | -0.3% |
| binance:ETH | collateral | trail30d_x2pp | +0.4% | +23.6% | +33.3% | -0.8% | +3.8% | +8.8% | +0.6% | -0.4% |
| binance:ETH | cash3x | trail30d_x2pp | -0.0% | +16.2% | +23.4% | -0.9% | +1.9% | +5.5% | -0.1% | -0.4% |
| binance:ETH | cash5x | trail30d_x2pp | +0.1% | +18.1% | +26.1% | -0.9% | +2.5% | +6.4% | +0.0% | -0.4% |
| hl:ETH | collateral | trail30d_x0pp | — | — | — | — | +14.9% | +17.3% | +3.8% | +0.2% |
| hl:ETH | cash3x | trail30d_x0pp | — | — | — | — | +10.9% | +12.5% | +2.6% | +0.0% |
| hl:ETH | cash5x | trail30d_x0pp | — | — | — | — | +12.4% | +14.2% | +2.9% | +0.2% |
| best:ETH | cash3x | trail30d_x2pp | — | — | — | — | +10.6% | +11.0% | +2.3% | +0.1% |
| binance:wstETH | cash3x | trail30d_x0pp | — | — | +18.0% | -0.8% | +5.0% | +7.7% | +1.4% | -0.8% |
| hl:wstETH | cash3x | trail30d_x0pp | — | — | — | — | +12.9% | +14.9% | +4.3% | +1.3% |
| binance:SOL | collateral | trail30d_x5pp | — | +0.2% | +26.2% | -0.1% | +1.3% | +8.5% | -0.2% | +0.0% |
| binance:SOL | cash3x | trail30d_x5pp | — | -0.7% | +17.7% | -0.3% | +0.7% | +5.5% | -0.2% | +0.0% |
| binance:SOL | cash5x | trail30d_x5pp | — | -1.0% | +19.4% | -0.3% | +0.8% | +6.2% | -0.2% | +0.0% |
| hl:SOL | collateral | trail7d_x0pp | — | — | — | — | +16.1% | +22.0% | +0.8% | -2.2% |
| hl:SOL | cash3x | trail7d_x0pp | — | — | — | — | +11.9% | +16.0% | +0.2% | -1.8% |
| hl:SOL | cash5x | trail7d_x0pp | — | — | — | — | +13.3% | +17.9% | +0.2% | -1.9% |
| best:SOL | cash3x | trail30d_x5pp | — | — | — | — | +7.0% | +16.4% | +1.3% | -0.2% |
| binance:HYPE | collateral | always | — | — | — | — | — | — | +9.3% | +0.6% |
| binance:HYPE | cash3x | always | — | — | — | — | — | — | +5.4% | -1.1% |
| binance:HYPE | cash5x | always | — | — | — | — | — | — | +6.1% | -1.3% |
| hl:HYPE | collateral | always | — | — | — | — | — | +102.9% | +16.9% | +3.8% |
| hl:HYPE | cash3x | always | — | — | — | — | — | +77.4% | +12.1% | +2.3% |
| hl:HYPE | cash5x | always | — | — | — | — | — | +85.9% | +13.5% | +2.6% |
| best:HYPE | cash3x | always | — | — | — | — | — | — | +6.3% | +2.3% |

## (c) Boros: implied fixed against the floating actually paid to maturity

225 markets listed; 192 matured with history; 7080 market-days scored (entry ≥ 7 days before maturity).

| group | markets | market-days | mean implied | mean realised | implied − realised | by-day mean | NW t (by day) | share implied above |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| all | 192 | 7080 | +2.1% | +2.0% | +0.12% | +0.82% | 1.27 | 49% |
| crypto | 150 | 6003 | +4.3% | +4.1% | +0.20% | +0.64% | 1.43 | 52% |
| tradfi | 42 | 1077 | -10.4% | -10.1% | -0.29% | +8.55% | 1.17 | 37% |
| hyperliquid:BTC | 24 | 879 | +6.0% | +6.3% | -0.25% | +0.18% | 0.28 | 46% |
| binance:ETH | 13 | 850 | +3.8% | +2.8% | +0.97% | +1.24% | 2.19 | 62% |
| hyperliquid:ETH | 17 | 825 | +6.3% | +6.9% | -0.61% | -0.45% | -0.75 | 36% |
| binance:BTC | 13 | 802 | +4.4% | +3.8% | +0.61% | +0.85% | 1.63 | 59% |
| okx:ETH | 9 | 421 | +2.7% | +2.7% | +0.00% | +0.14% | 0.34 | 59% |
| hyperliquid:HYPE | 10 | 292 | +9.0% | +9.8% | -0.83% | -0.76% | -1.11 | 34% |
| okx:BTC | 7 | 240 | +3.5% | +3.9% | -0.32% | -0.31% | -0.68 | 42% |
| bybit:HYPE | 7 | 198 | +3.4% | +2.5% | +0.92% | +1.01% | 1.58 | 68% |
| hyperliquid:BRENTOIL | 7 | 190 | -28.0% | -32.4% | +4.37% | +5.34% | 0.45 | 49% |
| hyperliquid:SOL | 5 | 165 | -1.5% | -1.4% | -0.12% | -0.16% | -0.16 | 52% |
| lighter:SOL | 5 | 164 | -0.8% | +0.7% | -1.44% | -1.40% | -1.17 | 40% |
| kucoin:BTC | 4 | 158 | +3.3% | +3.4% | -0.06% | +0.31% | 0.62 | 49% |
| lighter:ETH | 5 | 142 | +5.8% | +7.1% | -1.29% | -1.16% | -1.68 | 32% |
| binance:XRP | 5 | 136 | -0.6% | -2.2% | +1.58% | +1.63% | 1.05 | 64% |
| hyperliquid:CLOIL | 5 | 135 | -31.3% | -31.3% | -0.01% | +0.07% | 0.01 | 36% |
| binance:XAG | 5 | 121 | +11.9% | +10.3% | +1.64% | +1.64% | 0.31 | 38% |
| binance:XAU | 5 | 121 | +5.2% | +4.1% | +1.10% | +1.10% | 0.22 | 31% |
| kucoin:ETH | 4 | 118 | +3.6% | +4.9% | -1.31% | -1.19% | -2.59 | 19% |
| hyperliquid:XRP | 4 | 112 | -0.5% | -3.0% | +2.48% | +2.48% | 0.85 | 60% |
| hyperliquid:XAU | 4 | 103 | +6.1% | +6.3% | -0.20% | -0.20% | -0.13 | 38% |
| hyperliquid:XAG | 4 | 90 | +7.3% | +7.3% | +0.08% | +0.08% | 0.03 | 41% |
| gate:BTC | 3 | 87 | +3.2% | +3.0% | +0.16% | +0.16% | 0.47 | 56% |
| gate:HYPE | 3 | 87 | +4.1% | +4.4% | -0.28% | -0.25% | -1.09 | 32% |
| gate:ETH | 3 | 86 | +2.9% | +2.1% | +0.81% | +0.81% | 1.52 | 72% |
| hyperliquid:S&P500 | 3 | 79 | -1.7% | -2.2% | +0.46% | +0.46% | 0.28 | 33% |
| binance:BNB | 2 | 62 | +1.9% | -0.1% | +1.95% | +1.95% | 5.99 | 100% |
| binance:BRENTOIL | 2 | 61 | -44.3% | -34.4% | -9.90% | -8.95% | -0.86 | 26% |
| binance:CLOIL | 2 | 61 | -47.4% | -43.8% | -3.58% | -3.16% | -0.36 | 36% |
| binance:HYPE | 2 | 50 | +9.9% | +6.7% | +3.20% | +3.20% | 4.70 | 100% |
| hyperliquid:XYZ100 | 2 | 50 | -1.9% | +1.2% | -3.14% | -3.14% | -1.76 | 30% |
| hyperliquid:BNB | 1 | 44 | +5.8% | +0.2% | +5.60% | +5.60% | 9.55 | 100% |
| okx:HYPE | 2 | 43 | +5.8% | +1.4% | +4.38% | +4.38% | 13.86 | 100% |

Rules (receive fixed `rf` when implied − trailing-7d ≥ X; pay fixed `pf` when ≤ −X), chosen on trades that matured before 2026-03-01, tested on trades entered after it. APR is on notional after the taker fee, the settlement fee and a 25bp half-spread.

| rule | train n | train APR | train t | test n | test APR | test t | test hit | mean IM / notional |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| pf_X0pp | 652 | -1.47% | -1.38 | 2667 | +0.24% | -0.82 | 61% | 1.90% |
| pf_X10pp (chosen) | 42 | +6.37% | 3.57 | 285 | -2.07% | -1.28 | 61% | 11.61% |
| pf_X2pp | 161 | -0.12% | -0.51 | 1456 | +0.02% | -1.29 | 63% | 3.05% |
| pf_X5pp | 56 | +4.30% | 3.08 | 462 | -2.52% | -1.49 | 64% | 8.10% |
| rf_X0pp | 1163 | +1.52% | 3.13 | 2255 | -1.74% | -1.48 | 36% | 1.48% |
| rf_X10pp | 32 | +0.78% | -0.21 | 236 | -7.65% | -0.33 | 34% | 9.26% |
| rf_X2pp | 605 | +1.66% | 3.33 | 1205 | -1.88% | -0.24 | 39% | 2.35% |
| rf_X5pp | 190 | +1.28% | -0.22 | 476 | -3.45% | 0.22 | 37% | 5.02% |

BH survivors (train, q=0.10): rf_X0pp, rf_X2pp, pf_X5pp, pf_X10pp

### Live term structure

| market | days | mark | bid | ask | trailing 7d | trailing 30d | OI (units) |
|---|---:|---:|---:|---:|---:|---:|---:|
| HYPERLIQUID-BTC-30OCT2026 | 20 | +7.94% | +8.00% | +8.12% | +9.31% | +9.08% | 68 |
| HYPERLIQUID-BTC-30OCT2026 | 20 | +8.12% | +8.12% | +8.64% | +9.31% | +9.08% | 845284 |
| LIGHTER-BTC-30OCT2026 | 20 | +6.09% | +5.81% | +6.13% | +6.47% | +7.61% | 11 |
| LIGHTER-BTC-27NOV2026 | 48 | +7.62% | +7.35% | +7.67% | +6.47% | +7.61% | 2 |
| HYPERLIQUID-BTC-27NOV2026 | 48 | +8.37% | +8.14% | +8.47% | +9.31% | +9.08% | 134034 |
| HYPERLIQUID-BTC-27NOV2026 | 48 | +8.14% | +7.95% | +8.26% | +9.31% | +9.08% | 10 |
| BINANCE-BTCUSDT-30OCT2026 | 20 | +5.00% | +4.69% | +5.00% | +1.56% | +4.53% | 31 |
| KUCOIN-BTCUSDT-30OCT2026 | 20 | +6.33% | +6.33% | +6.89% | +4.94% | +3.75% | 74 |
| OKX-BTCUSDT-30OCT2026 | 20 | +4.92% | +4.92% | +5.08% | +3.44% | +5.18% | 17 |
| GATE-BTCUSDT-30OCT2026 | 20 | +4.30% | +4.20% | +4.38% | +0.99% | +3.29% | 58 |
| BINANCE-BTCUSDT-27NOV2026 | 48 | +5.30% | +5.19% | +5.41% | +1.56% | +4.53% | 2 |
| GATE-BTCUSDT-27NOV2026 | 48 | +5.25% | +4.96% | +5.25% | +0.99% | +3.29% | 11 |
| OKX-BTCUSDT-27NOV2026 | 48 | +5.46% | +5.27% | +5.55% | +3.44% | +5.18% | 1 |
| KUCOIN-BTCUSDT-27NOV2026 | 48 | +5.89% | +5.84% | +5.89% | +4.94% | +3.75% | 5 |
| HYPERLIQUID-ETH-30OCT2026 | 20 | +8.13% | +7.99% | +8.14% | +8.93% | +9.83% | 11208 |
| LIGHTER-ETH-30OCT2026 | 20 | +5.97% | +5.42% | +5.97% | +2.01% | +6.56% | 689 |
| HYPERLIQUID-ETH-27NOV2026 | 48 | +8.08% | +7.98% | +8.18% | +8.93% | +9.83% | 1596 |
| LIGHTER-ETH-27NOV2026 | 48 | +5.98% | +5.91% | +5.98% | +2.01% | +6.56% | 282 |
| HYPERLIQUID-ETH-25DEC2026 | 76 | +8.19% | +8.01% | +8.19% | +8.93% | +9.83% | 2501 |
| BINANCE-ETHUSDT-30OCT2026 | 20 | +3.87% | +3.84% | +4.09% | +2.19% | +4.21% | 1328 |
| OKX-ETHUSDT-30OCT2026 | 20 | +2.85% | +2.74% | +3.08% | +2.50% | +3.99% | 2077 |
| GATE-ETHUSDT-30OCT2026 | 20 | +3.27% | +3.27% | +3.50% | +1.39% | +3.64% | 6028 |
| KUCOIN-ETHUSDT-30OCT2026 | 20 | +4.39% | +4.32% | +4.87% | +3.87% | +4.69% | 1012 |
| BINANCE-ETHUSDT-27NOV2026 | 48 | +4.56% | +4.37% | +4.69% | +2.19% | +4.21% | 306 |
| GATE-ETHUSDT-27NOV2026 | 48 | +4.41% | +4.29% | +4.60% | +1.39% | +3.64% | 1523 |
| OKX-ETHUSDT-27NOV2026 | 48 | +4.05% | +4.02% | +4.33% | +2.50% | +3.99% | 117 |
| KUCOIN-ETHUSDT-27NOV2026 | 48 | +4.93% | +4.83% | +4.99% | +3.87% | +4.69% | 43 |
| BINANCE-ETHUSDT-25DEC2026 | 76 | +4.39% | +4.31% | +4.61% | +2.19% | +4.21% | 330 |
| HYPERLIQUID-HYPE-30OCT2026 | 20 | +8.82% | +8.82% | +9.23% | +8.39% | +9.17% | 746987 |
| GATE-HYPEUSDT-30OCT2026 | 20 | +4.53% | +4.15% | +4.69% | +4.13% | +3.87% | 129068 |
| BYBIT-HYPEUSDT-30OCT2026 | 20 | +4.13% | +3.76% | +4.13% | +2.98% | +1.50% | 345733 |
| HYPERLIQUID-xyzBRENTOIL-19OCT2026 | 9 | -51.01% | -61.69% | -51.00% | -101.73% | -54.02% | 39618 |
| HYPERLIQUID-xyzBRENTOIL-18NOV2026 | 39 | -50.59% | -55.16% | -44.69% | -101.73% | -54.02% | 7500 |

## (d) Volatility risk premium: DVOL against the next 30 days' realised volatility (vol points)

| asset | year | days | mean DVOL | mean RV | mean spread | median | share DVOL > RV | p5 | p1 | worst |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BTC | 2021 | 282 | 91.8% | 75.4% | +16.5% | +20.3% | 87% | -39.9% | -48.8% | -51.6% |
| BTC | 2022 | 365 | 73.7% | 60.7% | +13.0% | +15.3% | 73% | -20.9% | -22.9% | -26.4% |
| BTC | 2023 | 365 | 49.6% | 42.3% | +7.3% | +7.7% | 76% | -9.1% | -14.2% | -16.3% |
| BTC | 2024 | 366 | 57.7% | 51.4% | +6.3% | +7.3% | 77% | -13.3% | -17.7% | -20.1% |
| BTC | 2025 | 365 | 46.1% | 42.4% | +3.7% | +6.5% | 71% | -12.8% | -19.4% | -21.3% |
| BTC | 2026 | 253 | 43.5% | 42.6% | +0.9% | +2.7% | 57% | -20.7% | -24.5% | -25.8% |
| BTC | all | 1996 | | | +8.0% | +8.5% | 74% | -17.3% | -29.9% | -51.6% |
| ETH | 2021 | 282 | 109.4% | 98.3% | +11.1% | +24.2% | 79% | -76.6% | -93.7% | -97.3% |
| ETH | 2022 | 365 | 91.8% | 81.2% | +10.6% | +16.7% | 64% | -37.2% | -44.4% | -51.3% |
| ETH | 2023 | 365 | 51.8% | 45.8% | +6.0% | +6.2% | 75% | -9.1% | -12.8% | -16.5% |
| ETH | 2024 | 366 | 65.7% | 63.2% | +2.6% | +4.8% | 66% | -19.7% | -27.6% | -31.2% |
| ETH | 2025 | 365 | 69.4% | 70.7% | -1.3% | +0.4% | 52% | -25.1% | -29.6% | -37.9% |
| ETH | 2026 | 253 | 60.1% | 56.6% | +3.5% | +5.0% | 64% | -26.3% | -29.4% | -30.4% |
| ETH | all | 1996 | | | +5.3% | +6.1% | 66% | -28.1% | -66.6% | -97.3% |

## Capacity inputs (live books 2026-10-10T11:40:44+00:00)

| venue | instrument | OI | 24h volume | bids ≤10bp | asks ≤10bp | half-spread bp |
|---|---|---:|---:|---:|---:|---:|
| binance | BTCUSDT | $7.68B | $6.69B | $13.9M | $13.7M | 0.01 |
| binance | BTCUSDT_261225 | $50.5M | $11.4M | $538k | $1.0M | 0.01 |
| binance | BTCUSDT_270326 | $16.1M | $2.5M | $175k | $320k | 0.34 |
| binance | ETHUSDT | $5.87B | $3.75B | $10.9M | $12.0M | 0.02 |
| binance | ETHUSDT_261225 | $22.2M | $5.1M | $163k | $240k | 0.02 |
| binance | ETHUSDT_270326 | $2.7M | $410k | $54k | $24k | 3.04 |
| binance | HYPEUSDT | $334.0M | $339.6M | $888k | $486k | 0.06 |
| binance | SOLUSDT | $931.2M | $1.14B | $3.0M | $2.9M | 0.46 |
| binance | spot:BTCUSDT | — | $900.8M | $7.4M | $7.3M | 0.00 |
| binance | spot:ETHUSDT | — | $285.7M | $2.6M | $2.8M | 0.02 |
| binance | spot:SOLUSDT | — | $144.6M | $990k | $618k | 0.46 |
| deribit | BTC-11OCT26 | $244k | $323k | $55k | $105k | 0.15 |
| deribit | BTC-12OCT26 | $368k | $210k | $55k | $106k | 0.15 |
| deribit | BTC-13OCT26 | $2.6M | $2.9M | $80k | $105k | 0.45 |
| deribit | BTC-14OCT26 | $110 | $120 | $80k | $105k | 0.60 |
| deribit | BTC-16OCT26 | $6.3M | $1.2M | $70k | $124k | 0.15 |
| deribit | BTC-23OCT26 | $7.9M | $313k | $62k | $137k | 0.15 |
| deribit | BTC-24SEP27 | $4.9M | $157k | $56k | $64k | 2.87 |
| deribit | BTC-25DEC26 | $318.2M | $4.8M | $179k | $186k | 0.15 |
| deribit | BTC-25JUN27 | $65.0M | $245k | $56k | $49k | 0.73 |
| deribit | BTC-26MAR27 | $95.4M | $3.1M | $92k | $159k | 0.74 |
| deribit | BTC-27NOV26 | $37.5M | $2.1M | $58k | $58k | 0.30 |
| deribit | BTC-30OCT26 | $137.3M | $9.0M | $91k | $144k | 0.30 |
| deribit | BTC-PERPETUAL | $833.1M | $1.13B | — | — | — |
| deribit | ETH-11OCT26 | $1.1M | $453k | $48k | $33k | 0.50 |
| deribit | ETH-12OCT26 | $938k | $407k | $48k | $33k | 0.50 |
| deribit | ETH-13OCT26 | $442k | $446k | $48k | $33k | 0.50 |
| deribit | ETH-14OCT26 | $0 | $0 | $48k | $33k | 0.50 |
| deribit | ETH-16OCT26 | $6.0M | $256k | $39k | $54k | 0.50 |
| deribit | ETH-23OCT26 | $1.6M | $317k | $50k | $20k | 0.50 |
| deribit | ETH-24SEP27 | $6.2M | $407k | $22k | $22k | 1.92 |
| deribit | ETH-25DEC26 | $82.7M | $639k | $68k | $53k | 0.50 |
| deribit | ETH-25JUN27 | $13.8M | $322k | $25k | $10k | 3.88 |
| deribit | ETH-26MAR27 | $25.4M | $353k | $66k | $51k | 0.49 |
| deribit | ETH-27NOV26 | $6.8M | $697k | $35k | $40k | 0.50 |
| deribit | ETH-30OCT26 | $32.8M | $376k | $50k | $41k | 0.50 |
| deribit | ETH-PERPETUAL | $247.1M | $76.5M | — | — | — |
| hl | @107 | — | — | $50k | $211k | 0.06 |
| hl | @142 | — | — | $657k | $498k | 0.06 |
| hl | @151 | — | — | $478k | $422k | 0.20 |
| hl | @156 | — | — | $171k | $206k | 0.46 |
| hl | BTC | $3.16B | $1.22B | $5.4M | $5.1M | 0.06 |
| hl | ETH | $2.80B | $482.7M | $9.5M | $9.1M | 0.20 |
| hl | HYPE | $1.68B | $217.1M | $101k | $128k | 0.06 |
| hl | SOL | $622.1M | $126.6M | $2.7M | $1.9M | 0.46 |

| Boros market | OI | mark | bid | ask | long depth ±50bp | short depth ±50bp | days |
|---|---:|---:|---:|---:|---:|---:|---:|
| HYPERLIQUID-ETH-30OCT2026 | $28.0M | +8.13% | +7.99% | +8.14% | — | — | 20 |
| GATE-ETHUSDT-30OCT2026 | $15.1M | +3.32% | +3.31% | +3.40% | — | — | 20 |
| HYPERLIQUID-ETH-25DEC2026 | $6.2M | +8.19% | +8.01% | +8.19% | — | — | 76 |
| KUCOIN-BTCUSDT-30OCT2026 | $6.1M | +6.33% | +6.33% | +6.89% | — | — | 20 |
| OKX-ETHUSDT-30OCT2026 | $5.2M | +2.85% | +2.74% | +3.08% | — | — | 20 |
| GATE-BTCUSDT-30OCT2026 | $4.8M | +4.30% | +4.20% | +4.40% | — | — | 20 |
| HYPERLIQUID-ETH-27NOV2026 | $4.0M | +8.08% | +7.98% | +8.18% | — | — | 48 |
| GATE-ETHUSDT-27NOV2026 | $3.8M | +4.41% | +4.29% | +4.60% | — | — | 48 |
| BINANCE-ETHUSDT-30OCT2026 | $3.3M | +3.87% | +3.84% | +4.09% | — | — | 20 |
| BINANCE-BTCUSDT-30OCT2026 | $2.5M | +5.00% | +4.69% | +5.00% | — | — | 20 |
| KUCOIN-ETHUSDT-30OCT2026 | $2.5M | +4.39% | +4.32% | +4.87% | — | — | 20 |
| LIGHTER-ETH-30OCT2026 | $1.7M | +5.97% | +5.42% | +5.97% | — | — | 20 |
| OKX-BTCUSDT-30OCT2026 | $1.4M | +4.92% | +4.92% | +5.08% | — | — | 20 |
| GATE-BTCUSDT-27NOV2026 | $893k | +5.25% | +4.96% | +5.25% | — | — | 48 |
| LIGHTER-BTC-30OCT2026 | $878k | +6.09% | +5.81% | +6.13% | — | — | 20 |
| HYPERLIQUID-BTC-27NOV2026 | $850k | +8.14% | +7.95% | +8.26% | — | — | 48 |
| HYPERLIQUID-BTC-30OCT2026 | $845k | +8.12% | +8.12% | +8.64% | — | — | 20 |
| BINANCE-ETHUSDT-25DEC2026 | $823k | +4.39% | +4.31% | +4.61% | — | — | 76 |
| BINANCE-ETHUSDT-27NOV2026 | $765k | +4.56% | +4.37% | +4.69% | — | — | 48 |
| HYPERLIQUID-HYPE-30OCT2026 | $747k | +8.82% | +8.82% | +9.23% | — | — | 20 |
| LIGHTER-ETH-27NOV2026 | $704k | +5.98% | +5.91% | +5.98% | — | — | 48 |
| KUCOIN-BTCUSDT-27NOV2026 | $412k | +5.89% | +5.84% | +5.89% | — | — | 48 |
| BYBIT-HYPEUSDT-30OCT2026 | $346k | +4.13% | +3.76% | +4.13% | — | — | 20 |
| OKX-ETHUSDT-27NOV2026 | $293k | +4.05% | +4.02% | +4.33% | — | — | 48 |
| BINANCE-BTCUSDT-27NOV2026 | $174k | +5.30% | +5.19% | +5.41% | — | — | 48 |
| LIGHTER-BTC-27NOV2026 | $133k | +7.62% | +7.35% | +7.67% | — | — | 48 |
| GATE-HYPEUSDT-30OCT2026 | $129k | +4.53% | +4.15% | +4.69% | — | — | 20 |
| OKX-BTCUSDT-27NOV2026 | $111k | +5.46% | +5.27% | +5.55% | — | — | 48 |
| KUCOIN-ETHUSDT-27NOV2026 | $108k | +4.93% | +4.83% | +4.99% | — | — | 48 |
| HYPERLIQUID-xyzBRENTOIL-19OCT2026 | $40k | -51.01% | -61.69% | -51.00% | — | — | 9 |
| HYPERLIQUID-xyzBRENTOIL-18NOV2026 | $8k | -50.59% | -55.16% | -44.69% | — | — | 39 |
