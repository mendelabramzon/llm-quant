# incentive_yields — tables (generated 2026-10-10T18:30:22+00:00)

Excess = weekly return minus the savings rate actually paid that week (DSR, then SSR), annualised. t = Newey-West (8 weekly lags); interval = 8-week block bootstrap, 95%. Split 2024-07-01.

## 1. Choose then test (pre-committed grid, $1M, N=5)

| universe | chosen | in-sample excess | OOS excess | OOS t | OOS rank | deflated Sharpe (in / OOS) |
|---|---|---|---|---|---|---|
| all | all k30 h0.5 H1 | +18.30% | +14.99% | 4.26 | 6 of 18 | 1.00 / 0.00 |
| bluechip | bluechip k7 h1.0 H4 | +0.76% | +2.76% | 3.29 | 5 of 18 | 0.77 / 1.00 |

## 2. Grid (36 variants, $1M, N=5)

| variant | in-sample excess | t | OOS excess | t | BH adj p (OOS, q=0.10) | switches/yr |
|---|---|---|---|---|---|---|
| all k30 h0.0 H1 | +14.87% | 10.94 | +6.86% | 0.89 | 0.463 | 44.1 |
| all k30 h0.0 H2 | +13.26% | 13.71 | +8.24% | 1.53 | 0.173 | 38.3 |
| all k30 h0.0 H4 | +12.08% | 10.21 | +8.63% | 2.18 | 0.051 | 31.2 |
| all k30 h0.5 H1 | +18.30% | 6.59 | +14.99% | 4.16 | 0.000 | 46.1 |
| all k30 h0.5 H2 | +17.00% | 6.75 | +12.51% | 3.25 | 0.003 | 42.6 |
| all k30 h0.5 H4 | +15.82% | 6.24 | +9.38% | 1.81 | 0.107 | 32.5 |
| all k30 h1.0 H1 | +13.28% | 2.03 | +17.79% | 5.01 | 0.000 | 47.4 |
| all k30 h1.0 H2 | +13.20% | 2.02 | +17.14% | 5.86 | 0.000 | 41.8 |
| all k30 h1.0 H4 | +11.39% | 1.80 | +13.82% | 3.10 | 0.005 | 33.5 |
| all k7 h0.0 H1 | +13.47% | 3.45 | +5.58% | 0.62 | 0.538 | 66.5 |
| all k7 h0.0 H2 | +16.03% | 9.41 | +12.47% | 3.75 | 0.001 | 52.9 |
| all k7 h0.0 H4 | +13.96% | 9.38 | +11.46% | 5.48 | 0.000 | 37.0 |
| all k7 h0.5 H1 | +16.46% | 3.49 | +8.95% | 1.04 | 0.386 | 73.1 |
| all k7 h0.5 H2 | +17.99% | 5.81 | +15.57% | 4.89 | 0.000 | 54.7 |
| all k7 h0.5 H4 | +17.87% | 6.57 | +14.26% | 6.37 | 0.000 | 38.8 |
| all k7 h1.0 H1 | +18.15% | 3.71 | +10.66% | 1.21 | 0.302 | 71.0 |
| all k7 h1.0 H2 | +15.42% | 2.29 | +18.79% | 5.65 | 0.000 | 55.2 |
| all k7 h1.0 H4 | +13.63% | 2.06 | +15.61% | 5.09 | 0.000 | 39.8 |
| bluechip k30 h0.0 H1 | -0.06% | -0.11 | -6.38% | -0.74 | 0.536 | 45.1 |
| bluechip k30 h0.0 H2 | -0.04% | -0.06 | +2.35% | 2.46 | 0.025 | 39.5 |
| bluechip k30 h0.0 H4 | -0.07% | -0.10 | +2.27% | 2.06 | 0.065 | 30.5 |
| bluechip k30 h0.5 H1 | +0.01% | 0.02 | -5.95% | -0.69 | 0.536 | 48.4 |
| bluechip k30 h0.5 H2 | +0.30% | 0.51 | +2.75% | 3.07 | 0.005 | 39.3 |
| bluechip k30 h0.5 H4 | +0.19% | 0.29 | +2.64% | 2.61 | 0.017 | 31.2 |
| bluechip k30 h1.0 H1 | +0.16% | 0.28 | -5.37% | -0.62 | 0.538 | 47.1 |
| bluechip k30 h1.0 H2 | +0.45% | 0.74 | +3.47% | 3.50 | 0.002 | 39.0 |
| bluechip k30 h1.0 H4 | +0.60% | 0.92 | +2.87% | 3.10 | 0.005 | 30.2 |
| bluechip k7 h0.0 H1 | -0.29% | -0.46 | -6.59% | -0.78 | 0.525 | 86.7 |
| bluechip k7 h0.0 H2 | -0.03% | -0.04 | +2.41% | 1.98 | 0.074 | 58.7 |
| bluechip k7 h0.0 H4 | +0.13% | 0.22 | +1.88% | 1.78 | 0.108 | 36.0 |
| bluechip k7 h0.5 H1 | -0.36% | -0.64 | -5.89% | -0.70 | 0.536 | 93.0 |
| bluechip k7 h0.5 H2 | +0.31% | 0.55 | +3.20% | 2.64 | 0.017 | 58.9 |
| bluechip k7 h0.5 H4 | +0.54% | 0.90 | +2.52% | 2.64 | 0.017 | 37.5 |
| bluechip k7 h1.0 H1 | +0.14% | 0.22 | -5.48% | -0.66 | 0.538 | 83.1 |
| bluechip k7 h1.0 H2 | +0.62% | 1.01 | +3.68% | 3.31 | 0.003 | 53.4 |
| bluechip k7 h1.0 H4 | +0.76% | 1.37 | +2.76% | 3.05 | 0.005 | 35.5 |

## 3a. Chosen variant, all universe: all k30 h0.5 H1

| run | excess (OOS) | t | 95% interval | gross return | max drawdown | weeks |
|---|---|---|---|---|---|---|
| main $1M, in sample | +18.30% | 6.59 | +13.34% to +23.79% | +22.45% | +0.00% | 89 |
| **main $1M, out of sample** | +14.99% | 4.16 | +6.35% to +20.91% | +20.29% | +6.25% | 118 |
| main $1M, oos_first_half | +16.84% | 7.72 | +12.77% to +20.94% | +23.54% | +1.75% | 59 |
| main $1M, oos_second_half | +13.14% | 1.93 | -1.96% to +23.83% | +17.05% | +6.25% | 59 |
| main $1M, last_52w | +11.75% | 1.58 | -4.18% to +23.46% | +15.56% | +6.25% | 52 |
| $100k (OOS) | +15.79% | 4.31 | +7.10% to +21.70% | +21.10% | +6.23% | 118 |
| $10M (OOS) | +5.51% | 1.62 | -2.51% to +10.89% | +10.81% | +7.09% | 118 |
| N=1 (OOS) | +20.26% | 5.09 | +12.82% to +27.77% | +25.56% | +2.13% | 118 |
| N=10 (OOS) | +4.41% | 0.62 | -11.49% to +16.77% | +9.72% | +15.38% | 118 |
| entered 1 day late (OOS) | +14.21% | 3.87 | +5.33% to +20.34% | +19.52% | +6.47% | 118 |
| entered 1 week late (OOS) | +12.22% | 3.66 | +4.63% to +17.73% | +17.52% | +5.75% | 118 |
| rewards at accrual price (OOS) | +14.74% | 4.09 | +6.14% to +20.63% | +20.04% | +6.24% | 118 |
| rewards ignored (OOS) | +9.93% | 3.02 | +2.38% to +15.46% | +15.23% | +6.31% | 118 |
| no hack/depeg/share marking (OOS) | +20.61% | 15.07 | +18.12% to +23.11% | +25.92% | +0.00% | 118 |
| each unmarked TVL collapse costs 10% (OOS) | +9.69% | 2.75 | +1.42% to +16.00% | +14.99% | +6.25% | 118 |
| each unmarked TVL collapse costs 50% (OOS) | -11.52% | -1.15 | -33.82% to +7.20% | -6.22% | +38.91% | 118 |
| without Pendle/Notional/Spectra fixed-rate pools (OOS) | +6.23% | 0.55 | -19.57% to +28.94% | +11.54% | +19.70% | 118 |
| without pools rebuilt from captures (OOS) | +15.04% | 4.15 | +6.32% to +20.94% | +20.35% | +6.25% | 118 |
| pools alive today only (biased) (OOS) | +0.85% | 0.05 | -38.48% to +39.85% | +6.15% | +39.86% | 118 |

Capital curve (OOS excess, t, $ a year): $100k +15.79% (t 4.31, $16k); $1.0M +14.99% (t 4.16, $150k); $10.0M +5.51% (t 1.62, $551k); $2.0M +12.62% (t 3.52, $252k); $20.0M -1.35% (t -0.40, $-270k); $300k +16.07% (t 4.41, $48k); $3.0M +11.31% (t 3.19, $339k); $5.0M +9.17% (t 2.63, $459k)

By year ($1M): 2022 +13.08% (excess +12.84%); 2023 +15.77% (excess +12.83%); 2024 +33.37% (excess +25.55%); 2025 +22.68% (excess +17.24%); 2026 +12.32% (excess +8.68%)

P&L components over the whole run ($1M): base $815k, rewards at sale $203k (imputed price $54k), costs $-44k, losses $-130k; switches a year 46.1; share of held days in pools dead today +72.4%.
OOS excess P&L $341k; top-5 pools +40% of it: merkl Ethereum USP $36k, notional-v3 Ethereum PTUSDE26MAR2025 $34k, peapods-finance Ethereum USDC $29k, notional-v3 Ethereum NGHO $19k, polynomial-liquidity Polynomial usd0++ $18k.

Losses ($1M run): collapse n=16 $0; dark n=44 $0; hack n=2 $-10k; share n=18 $-118k; share_open n=2 $-2k

Excess P&L by audit status: share_accruing 35 pools $113k (losses $-57k); share_flat 18 pools $-2k (losses $-63k); unaudited 91 pools $541k (losses $-10k)

Top held: idle Ethereum DAI (245 d); sherlock Ethereum USDC (238 d); toros OP Mainnet USDPY (189 d); opyn-squeeth Ethereum USDC (175 d); peapods-finance Ethereum USDC (175 d); idle Ethereum USDT (168 d); polynomial-liquidity Polynomial usd0++ (168 d); merkl Ethereum USP (154 d); credix Solana USDC (140 d); notional-v3 Ethereum NUSDC (140 d)

## 3b. Chosen variant, bluechip universe: bluechip k7 h1.0 H4

| run | excess (OOS) | t | 95% interval | gross return | max drawdown | weeks |
|---|---|---|---|---|---|---|
| main $1M, in sample | +0.76% | 1.37 | -0.39% to +1.88% | +4.90% | +0.68% | 89 |
| **main $1M, out of sample** | +2.76% | 3.05 | +1.24% to +4.64% | +8.06% | +0.44% | 118 |
| main $1M, oos_first_half | +1.41% | 2.56 | +0.31% to +2.30% | +8.11% | +0.44% | 59 |
| main $1M, oos_second_half | +4.10% | 2.64 | +1.49% to +7.48% | +8.01% | +0.25% | 59 |
| main $1M, last_52w | +3.98% | 2.30 | +1.13% to +8.00% | +7.79% | +0.25% | 52 |
| $100k (OOS) | +1.89% | 1.83 | +0.13% to +3.89% | +7.20% | +1.13% | 118 |
| $10M (OOS) | +0.19% | 0.28 | -1.03% to +1.61% | +5.50% | +0.99% | 118 |
| N=1 (OOS) | +5.24% | 2.91 | +1.96% to +9.12% | +10.54% | +1.39% | 118 |
| N=10 (OOS) | +2.05% | 3.04 | +0.80% to +3.37% | +7.36% | +0.45% | 118 |
| entered 1 day late (OOS) | +2.53% | 2.87 | +1.05% to +4.28% | +7.84% | +0.50% | 118 |
| entered 1 week late (OOS) | +1.56% | 2.21 | +0.29% to +2.91% | +6.87% | +0.49% | 118 |
| rewards at accrual price (OOS) | +2.76% | 3.03 | +1.23% to +4.63% | +8.06% | +0.44% | 118 |
| rewards ignored (OOS) | -0.04% | -0.03 | -2.10% to +2.28% | +5.27% | +3.33% | 118 |
| no hack/depeg/share marking (OOS) | +3.11% | 3.17 | +1.46% to +5.11% | +8.41% | +0.29% | 118 |
| each unmarked TVL collapse costs 10% (OOS) | +0.99% | 0.73 | -1.95% to +3.71% | +6.29% | +3.54% | 118 |
| each unmarked TVL collapse costs 50% (OOS) | -6.08% | -1.07 | -19.44% to +3.17% | -0.78% | +19.54% | 118 |
| without Pendle/Notional/Spectra fixed-rate pools (OOS) | +2.76% | 3.05 | +1.24% to +4.64% | +8.06% | +0.44% | 118 |
| without pools rebuilt from captures (OOS) | +2.93% | 3.02 | +1.30% to +4.84% | +8.24% | +0.44% | 118 |
| pools alive today only (biased) (OOS) | +1.53% | 3.39 | +0.64% to +2.34% | +6.84% | +0.76% | 118 |

Capital curve (OOS excess, t, $ a year): $100k +1.89% (t 1.83, $2k); $1.0M +2.76% (t 3.05, $28k); $10.0M +0.19% (t 0.28, $19k); $2.0M +1.74% (t 2.05, $35k); $20.0M -3.21% (t -4.92, $-643k); $300k +2.73% (t 2.86, $8k); $3.0M +1.47% (t 1.79, $44k); $5.0M +1.01% (t 1.31, $51k)

By year ($1M): 2022 +1.40% (excess +1.16%); 2023 +3.44% (excess +0.50%); 2024 +8.76% (excess +0.94%); 2025 +8.46% (excess +3.02%); 2026 +7.41% (excess +3.76%)

P&L components over the whole run ($1M): base $221k, rewards at sale $91k (imputed price $9k), costs $-36k, losses $-8k; switches a year 35.5; share of held days in pools dead today +41.2%.
OOS excess P&L $55k; top-5 pools +70% of it: aave-v3 Ethereum SGHO $18k, morpho-blue Ethereum AUGUSTAUSDV2 $8k, morpho-v1 Ethereum APRUSDE $6k, morpho-blue Ethereum AUGUSTAUSD $4k, morpho-blue Ethereum ALPHAUSDCASIAV2 $3k.

Losses ($1M run): collapse n=24 $0; dark n=20 $0; hack n=1 $-590; share n=14 $-8k; share_open n=4 $-346

Excess P&L by audit status: share_accruing 46 pools $47k (losses $-8k); share_flat 34 pools $12k (losses $0); unaudited 31 pools $18k (losses $0)

Top held: aave-v3 Ethereum SGHO (420 d); compound-v2 Ethereum USDT (280 d); justlend-v1 Tron USDDOLD (280 d); compound-v3 Polygon USDC (224 d); compound-v2 Ethereum DAI (196 d); aave-v2 Avalanche USDT.E (168 d); aave-v2 Ethereum USDT (168 d); justlend-v1 Tron TUSD (168 d); aave-v3 Ethereum DAI (140 d); aave-v3 Arbitrum USDC (140 d)

## 3c. Audited family (post hoc): the same grid on pools whose return a share price checks

Pools with a share-price series: 637 (vault shares 414). Vault shares must deliver the claimed apyBase in their price (shortfalls booked in full); rebasing receipts are marked like the deposit token.

| universe | chosen | in-sample excess | OOS excess | OOS t | OOS rank |
|---|---|---|---|---|---|
| all | all k7 h0.5 H1 | +9.66% | -3.75% | -0.41 | 13 of 18 |
| bluechip | bluechip k7 h1.0 H4 | +0.50% | +2.62% | 2.80 | 7 of 18 |

| variant (audited) | in-sample excess | t | OOS excess | t | BH adj p |
|---|---|---|---|---|---|
| all k30 h0.0 H1 | +8.86% | 6.50 | -3.00% | -0.31 | 0.905 |
| all k30 h0.0 H2 | +8.36% | 6.20 | -3.79% | -0.58 | 0.722 |
| all k30 h0.0 H4 | +7.69% | 6.57 | -7.86% | -0.77 | 0.675 |
| all k30 h0.5 H1 | +4.38% | 0.77 | -1.15% | -0.12 | 0.947 |
| all k30 h0.5 H2 | +3.81% | 0.67 | -1.43% | -0.23 | 0.916 |
| all k30 h0.5 H4 | +3.01% | 0.56 | -7.03% | -0.70 | 0.675 |
| all k30 h1.0 H1 | +1.20% | 0.19 | -1.23% | -0.12 | 0.947 |
| all k30 h1.0 H2 | +0.65% | 0.11 | +0.65% | 0.10 | 0.947 |
| all k30 h1.0 H4 | -1.29% | -0.20 | -6.34% | -0.67 | 0.675 |
| all k7 h0.0 H1 | +8.85% | 4.81 | -8.47% | -0.79 | 0.675 |
| all k7 h0.0 H2 | +9.15% | 4.73 | +0.04% | 0.01 | 0.992 |
| all k7 h0.0 H4 | +8.85% | 5.85 | +3.17% | 1.27 | 0.405 |
| all k7 h0.5 H1 | +9.66% | 4.92 | -3.75% | -0.43 | 0.828 |
| all k7 h0.5 H2 | -0.38% | -0.05 | +7.83% | 2.72 | 0.034 |
| all k7 h0.5 H4 | +4.91% | 0.87 | +4.69% | 1.57 | 0.260 |
| all k7 h1.0 H1 | +4.77% | 0.78 | -2.41% | -0.28 | 0.905 |
| all k7 h1.0 H2 | -0.08% | -0.01 | +7.89% | 2.77 | 0.034 |
| all k7 h1.0 H4 | +4.87% | 0.89 | +5.53% | 1.93 | 0.128 |
| bluechip k30 h0.0 H1 | -0.04% | -0.07 | -6.41% | -0.77 | 0.675 |
| bluechip k30 h0.0 H2 | +0.05% | 0.09 | +2.14% | 2.33 | 0.064 |
| bluechip k30 h0.0 H4 | +0.04% | 0.06 | +2.39% | 2.18 | 0.088 |
| bluechip k30 h0.5 H1 | +0.16% | 0.32 | +3.13% | 3.21 | 0.011 |
| bluechip k30 h0.5 H2 | +0.37% | 0.63 | +3.02% | 3.44 | 0.009 |
| bluechip k30 h0.5 H4 | +0.24% | 0.39 | +2.94% | 3.16 | 0.011 |
| bluechip k30 h1.0 H1 | +0.15% | 0.29 | -5.76% | -0.66 | 0.675 |
| bluechip k30 h1.0 H2 | +0.31% | 0.53 | +3.23% | 3.67 | 0.009 |
| bluechip k30 h1.0 H4 | +0.39% | 0.61 | +3.08% | 3.38 | 0.009 |
| bluechip k7 h0.0 H1 | -0.24% | -0.39 | -6.85% | -0.82 | 0.675 |
| bluechip k7 h0.0 H2 | +0.02% | 0.03 | +1.96% | 1.54 | 0.262 |
| bluechip k7 h0.0 H4 | +0.15% | 0.25 | +2.20% | 2.02 | 0.111 |
| bluechip k7 h0.5 H1 | +0.01% | 0.02 | -6.03% | -0.72 | 0.675 |
| bluechip k7 h0.5 H2 | +0.35% | 0.60 | +2.61% | 2.08 | 0.104 |
| bluechip k7 h0.5 H4 | +0.47% | 0.81 | +2.52% | 2.38 | 0.062 |
| bluechip k7 h1.0 H1 | +0.09% | 0.17 | -6.11% | -0.70 | 0.675 |
| bluechip k7 h1.0 H2 | +0.39% | 0.67 | +2.86% | 2.58 | 0.039 |
| bluechip k7 h1.0 H4 | +0.50% | 0.85 | +2.62% | 2.66 | 0.035 |

### audited all: all k7 h0.5 H1

| run | excess (OOS) | t | 95% interval | gross return | max drawdown | weeks |
|---|---|---|---|---|---|---|
| in sample | +9.66% | 4.92 | +6.18% to +13.45% | +13.81% | +0.88% | 89 |
| **out of sample** | -3.75% | -0.43 | -23.20% to +10.21% | +1.56% | +20.92% | 118 |
| $100k (OOS) | -4.05% | -0.46 | -23.58% to +9.77% | +1.26% | +21.16% | 118 |
| $10M (OOS) | -10.89% | -1.24 | -30.46% to +3.19% | -5.58% | +26.35% | 118 |
| 1 day late (OOS) | -6.46% | -0.74 | -26.83% to +8.14% | -1.16% | +26.28% | 118 |
| 1 week late (OOS) | +1.93% | 0.37 | -10.75% to +9.69% | +7.24% | +11.56% | 118 |
| no loss marking (OOS) | +15.08% | 14.70 | +12.92% to +17.21% | +20.38% | +0.00% | 118 |
| rewards ignored (OOS) | -7.71% | -0.85 | -28.18% to +6.22% | -2.41% | +25.95% | 118 |

Losses: collapse n=20 $0; dark n=47 $0; share n=90 $-435k; share_open n=2 $-1k; share_stuck n=1 $-23k
Top-5 OOS pools: merkl Ethereum USP $43k, veranta Base USDC $15k, strata-markets Ethereum JRUSDAT $12k, upshift Avalanche UPAUSD $11k, benqi-lending Avalanche USDC.E $10k

### audited bluechip: bluechip k7 h1.0 H4

| run | excess (OOS) | t | 95% interval | gross return | max drawdown | weeks |
|---|---|---|---|---|---|---|
| in sample | +0.50% | 0.85 | -0.67% to +1.68% | +4.64% | +0.68% | 89 |
| **out of sample** | +2.62% | 2.66 | +0.89% to +4.57% | +7.93% | +0.83% | 118 |
| $100k (OOS) | +1.72% | 1.58 | -0.14% to +3.86% | +7.03% | +0.97% | 118 |
| $10M (OOS) | +0.60% | 0.72 | -0.91% to +2.21% | +5.90% | +1.23% | 118 |
| 1 day late (OOS) | +2.53% | 2.55 | +0.79% to +4.47% | +7.83% | +0.83% | 118 |
| 1 week late (OOS) | +2.27% | 2.90 | +0.94% to +3.75% | +7.58% | +0.42% | 118 |
| no loss marking (OOS) | +3.37% | 3.35 | +1.71% to +5.31% | +8.67% | +0.20% | 118 |
| rewards ignored (OOS) | +0.01% | 0.01 | -2.07% to +2.43% | +5.32% | +2.95% | 118 |

Losses: collapse n=22 $0; dark n=14 $0; hack n=1 $-590; share n=20 $-16k; share_open n=5 $-473
Top-5 OOS pools: aave-v3 Ethereum SGHO $18k, morpho-blue Ethereum AUGUSTAUSDV2 $7k, morpho-blue Ethereum AUGUSTAUSD $5k, morpho-blue Ethereum AUSDC $4k, morpho-blue Ethereum CSUSDC $4k

## 4. References ($1M)

| reference | excess (OOS) | t | 95% interval | gross | max DD | weeks |
|---|---|---|---|---|---|---|
| aave_v3_usdc_ethereum_hold (in sample) | +0.03% | 0.07 | -0.75% to +0.75% | +4.17% | +0.71% | 89 |
| aave_v3_usdc_ethereum_hold (OOS) | -1.01% | -3.29 | -1.72% to -0.47% | +4.30% | +2.28% | 118 |
| top5_by_tvl_all_H4 (in sample) | -2.17% | -3.02 | -3.54% to -0.89% | +1.97% | +3.84% | 89 |
| top5_by_tvl_all_H4 (OOS) | -0.98% | -1.43 | -2.59% to +0.05% | +4.33% | +2.43% | 118 |
| top5_by_tvl_bluechip_H4 (in sample) | -0.89% | -1.17 | -2.43% to +0.31% | +3.25% | +2.17% | 89 |
| top5_by_tvl_bluechip_H4 (OOS) | -0.34% | -1.13 | -0.93% to +0.25% | +4.96% | +1.00% | 118 |

## 5. What you see vs what you get: every eligible pool, non-overlapping 4-week windows (17954)

Annualised, equal-weighted across pool-windows, zero size. net = base + rewards at sale + hack + depeg.

### displayed excess over savings, in sample

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| < SSR | 1844 | 407 | +2.6% | +2.5% | +0.5% | +0.5% | -2.14% | -0.20% | +0.7% | +5.7% | -5.07% | +1.30% | +3.42% | +6.02% |
| 0-2pp | 1161 | 348 | +3.8% | +3.4% | +0.9% | +0.9% | -2.47% | -1.06% | +0.7% | +3.0% | -2.30% | +0.86% | +6.80% | +7.06% |
| 2-5pp | 1123 | 384 | +6.1% | +4.3% | +1.9% | +1.9% | -0.73% | -0.96% | +4.5% | +3.0% | +1.49% | +0.80% | +5.52% | +5.88% |
| 5-10pp | 814 | 333 | +10.4% | +6.6% | +3.4% | +3.4% | -0.11% | -1.69% | +8.3% | +3.8% | +4.47% | +0.37% | +6.51% | +7.00% |
| 10-20pp | 431 | 201 | +17.8% | +10.6% | +5.6% | +5.5% | -4.68% | -1.73% | +9.7% | +5.3% | +4.39% | +0.46% | +6.73% | +4.87% |
| >= 20pp | 155 | 91 | +40.8% | +18.9% | +11.3% | +11.2% | +0.00% | -2.55% | +27.6% | +6.5% | +21.15% | +0.00% | +5.16% | +5.81% |

### displayed excess over savings, out of sample

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| < SSR | 4957 | 853 | +2.5% | +2.6% | +0.2% | +0.2% | -0.91% | -0.67% | +1.2% | +5.1% | -3.90% | +0.52% | +5.27% | +6.66% |
| 0-2pp | 2554 | 767 | +5.3% | +4.7% | +0.6% | +0.6% | -0.35% | -1.62% | +3.3% | +4.4% | -1.07% | +0.67% | +12.14% | +6.23% |
| 2-5pp | 2345 | 906 | +8.1% | +6.4% | +1.2% | +1.1% | -0.34% | -1.87% | +5.3% | +4.6% | +0.65% | +0.43% | +13.90% | +5.63% |
| 5-10pp | 1713 | 775 | +11.9% | +8.7% | +1.5% | +1.5% | -0.51% | -1.66% | +8.0% | +4.9% | +3.12% | +0.47% | +10.51% | +5.66% |
| 10-20pp | 631 | 365 | +18.7% | +11.9% | +3.4% | +3.4% | -0.24% | -5.45% | +9.6% | +5.3% | +4.27% | +0.32% | +16.80% | +5.86% |
| >= 20pp | 226 | 134 | +39.1% | +16.8% | +9.1% | +9.1% | -0.29% | -10.09% | +15.5% | +5.9% | +9.56% | +0.88% | +12.39% | +7.08% |

### venue category (DefiLlama)

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Lending | 9579 | 1058 | +5.5% | +4.1% | +1.1% | +1.1% | -1.21% | -0.59% | +3.4% | +4.7% | -1.25% | +0.60% | +9.04% | +8.17% |
| Yield | 2630 | 644 | +11.2% | +7.8% | +1.8% | +1.8% | -0.06% | -3.68% | +5.9% | +4.8% | +1.04% | +0.19% | +10.76% | +3.31% |
| Yield Aggregator | 1486 | 159 | +7.4% | +6.5% | +0.6% | +0.6% | -0.12% | -0.93% | +6.1% | +4.8% | +1.22% | +1.41% | +9.15% | +7.20% |
| Cross Chain Bridge | 601 | 37 | +6.8% | +1.0% | +5.7% | +5.7% | -0.08% | -4.17% | +2.5% | +4.3% | -1.80% | +0.17% | +1.50% | +0.17% |
| CDP | 524 | 41 | +4.7% | +3.3% | +1.3% | +1.3% | -0.16% | -0.15% | +4.3% | +4.5% | -0.24% | +0.19% | +5.73% | +3.44% |
| Derivatives | 421 | 33 | +12.0% | +9.2% | +1.6% | +1.6% | -2.08% | -3.91% | +4.7% | +5.9% | -1.12% | +0.71% | +14.96% | +2.14% |
| RWA | 408 | 59 | +5.7% | +4.9% | +0.5% | +0.5% | -0.00% | -2.60% | +2.8% | +4.3% | -1.43% | +0.25% | +9.31% | +0.74% |
| Dexs | 387 | 29 | +3.8% | +2.3% | +1.0% | +1.0% | -7.15% | -0.80% | -4.6% | +4.3% | -8.91% | +4.13% | +1.55% | +1.55% |
| Onchain Capital Allocator | 326 | 68 | +8.9% | +8.3% | +0.3% | +0.3% | -0.00% | -0.37% | +8.3% | +4.1% | +4.23% | +0.31% | +5.52% | +3.99% |
| Leveraged Farming | 314 | 22 | +6.8% | +5.8% | +0.4% | +0.4% | -3.51% | -0.40% | +2.3% | +4.7% | -2.46% | +1.59% | +0.32% | +1.27% |
| Basis Trading | 282 | 28 | +11.5% | +10.5% | +0.2% | +0.2% | -0.80% | -8.55% | +1.4% | +5.4% | -3.99% | +0.35% | +9.93% | +0.35% |
| Uncollateralized Lending | 240 | 54 | +10.1% | +8.1% | +1.7% | +1.7% | -0.38% | -0.01% | +9.5% | +3.9% | +5.56% | +0.42% | +2.08% | +22.08% |
| Bridge | 213 | 22 | +1.6% | +0.3% | +1.3% | +1.3% | +0.00% | +0.00% | +1.6% | +5.1% | -3.46% | +0.00% | +0.00% | +7.98% |
| Indexes | 121 | 5 | +2.8% | +2.7% | +0.0% | +0.0% | +0.00% | -0.58% | +2.1% | +6.2% | -4.10% | +0.00% | +7.44% | +1.65% |
| Dual-Token Stablecoin | 101 | 8 | +13.0% | +11.8% | +0.0% | +0.0% | +0.00% | +0.00% | +11.8% | +6.1% | +5.72% | +0.00% | +0.00% | +1.98% |
| unknown | 95 | 14 | +7.3% | +5.0% | +2.0% | +2.0% | +0.00% | +0.00% | +7.0% | +2.8% | +4.20% | +0.00% | +0.00% | +2.11% |
| Algo-Stables | 51 | 2 | +5.2% | +5.0% | +0.0% | +0.0% | +0.00% | -0.38% | +4.6% | +5.0% | -0.40% | +0.00% | +17.65% | +0.00% |
| Liquidity Manager | 38 | 7 | +16.3% | +14.5% | +0.0% | +0.0% | +0.00% | +0.00% | +14.5% | +2.7% | +11.80% | +0.00% | +0.00% | +7.89% |
| Risk Curators | 25 | 9 | +6.8% | +6.0% | +0.9% | +0.9% | +0.00% | +0.00% | +6.8% | +3.5% | +3.30% | +0.00% | +0.00% | +0.00% |
| Insurance | 22 | 3 | +14.5% | +14.9% | +0.0% | +0.0% | +0.00% | +0.00% | +14.9% | +3.7% | +11.17% | +0.00% | +0.00% | +0.00% |
| Options Vault | 22 | 2 | +11.6% | +11.0% | +0.0% | +0.0% | +0.00% | +0.00% | +11.0% | +4.8% | +6.28% | +0.00% | +0.00% | +4.55% |
| Liquid Staking | 20 | 3 | +7.1% | +0.0% | +6.6% | +6.3% | +0.00% | +0.00% | +6.3% | +3.9% | +2.40% | +0.00% | +0.00% | +10.00% |
| Prediction Market | 15 | 2 | +15.9% | +8.3% | +0.0% | +0.0% | +0.00% | +0.00% | +8.3% | +6.5% | +1.78% | +0.00% | +0.00% | +6.67% |
| Synthetics | 11 | 3 | +14.3% | +1.7% | +11.8% | +11.5% | +0.00% | +0.00% | +13.2% | +2.3% | +10.89% | +0.00% | +0.00% | +0.00% |
| Options | 9 | 1 | +8.5% | +0.0% | +7.1% | +7.1% | +0.00% | +0.00% | +7.1% | +3.5% | +3.59% | +0.00% | +0.00% | +11.11% |
| Farm | 6 | 3 | +5.4% | +0.0% | +5.1% | +5.0% | +0.00% | -55.09% | -50.1% | +1.4% | -51.50% | +0.00% | +16.67% | +16.67% |
| Stablecoin Wrapper | 5 | 1 | +19.8% | +16.1% | +0.0% | +0.0% | +0.00% | -41.58% | -25.5% | +3.5% | -29.03% | +0.00% | +60.00% | +0.00% |
| NFT Lending | 2 | 1 | +6.7% | +7.4% | +0.0% | +0.0% | +0.00% | +0.00% | +7.4% | +6.7% | +0.66% | +0.00% | +0.00% | +0.00% |

### blue-chip lending vs other

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| other | 13136 | 1917 | +7.7% | +5.6% | +1.5% | +1.5% | -1.30% | -1.71% | +4.1% | +4.7% | -0.61% | +0.83% | +6.78% | +5.09% |
| bluechip | 4818 | 538 | +4.7% | +3.9% | +0.6% | +0.6% | -0.00% | -0.65% | +3.8% | +4.6% | -0.80% | +0.08% | +12.76% | +9.32% |

### reward share of the displayed yield

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no reward | 11511 | 1620 | +5.9% | +5.5% | +0.1% | +0.0% | -0.46% | -1.46% | +3.7% | +4.8% | -1.15% | +0.59% | +7.88% | +6.36% |
| reward < half | 3893 | 802 | +8.2% | +6.1% | +1.4% | +1.4% | -1.87% | -1.12% | +4.5% | +4.7% | -0.18% | +0.46% | +12.79% | +6.22% |
| reward >= half | 2550 | 535 | +9.4% | +1.8% | +6.7% | +6.7% | -1.75% | -1.76% | +5.0% | +4.2% | +0.81% | +1.06% | +3.92% | +5.61% |

### displayed excess, pools whose vault share price audits the yield

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0-2pp | 862 | 184 | +5.1% | +4.6% | +0.6% | +0.6% | -0.06% | -2.01% | +3.2% | +4.1% | -0.93% | +0.81% | +44.55% | +4.87% |
| < SSR | 822 | 149 | +3.4% | +3.9% | +0.3% | +0.3% | -1.98% | -2.04% | +0.2% | +5.5% | -5.34% | +1.22% | +35.64% | +4.62% |
| 2-5pp | 797 | 220 | +7.7% | +6.3% | +1.1% | +1.1% | -0.29% | -1.11% | +6.0% | +4.4% | +1.58% | +0.38% | +46.30% | +4.64% |
| 5-10pp | 487 | 219 | +12.0% | +9.2% | +1.4% | +1.4% | +0.00% | -3.59% | +7.0% | +4.9% | +2.10% | +0.00% | +45.38% | +4.11% |
| 10-20pp | 262 | 143 | +18.7% | +13.4% | +2.0% | +1.9% | -0.01% | -6.26% | +9.0% | +5.5% | +3.55% | +0.38% | +47.71% | +4.58% |
| >= 20pp | 102 | 64 | +38.5% | +18.1% | +7.1% | +7.1% | +0.00% | -24.08% | +1.1% | +6.4% | -5.24% | +0.00% | +33.33% | +7.84% |

### displayed excess, pools with no share price (apyBase taken as given)

| bucket | pool-windows | pools | displayed | base | reward face | reward at sale | hack | depeg | net | savings | net excess | P(hack) | P(depeg) | P(collapse) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| < SSR | 4571 | 816 | +2.1% | +2.1% | +0.3% | +0.3% | -1.50% | -0.41% | +0.6% | +5.2% | -4.61% | +0.88% | +0.55% | +6.80% |
| 2-5pp | 2332 | 852 | +7.3% | +5.5% | +1.5% | +1.5% | -0.37% | -1.25% | +5.4% | +4.0% | +1.37% | +0.56% | +0.39% | +5.70% |
| 0-2pp | 2303 | 733 | +5.0% | +4.2% | +0.8% | +0.8% | -1.50% | -0.08% | +3.5% | +4.1% | -0.65% | +0.83% | +0.09% | +6.60% |
| 5-10pp | 1768 | 740 | +11.2% | +7.7% | +2.3% | +2.3% | -0.19% | -0.05% | +9.8% | +4.4% | +5.38% | +0.28% | +0.17% | +6.67% |
| 10-20pp | 687 | 330 | +18.2% | +10.5% | +5.5% | +5.4% | -0.21% | -0.32% | +15.4% | +5.2% | +10.17% | +0.15% | +0.44% | +6.11% |
| >= 20pp | 239 | 118 | +40.7% | +17.4% | +11.8% | +11.8% | -0.27% | +0.00% | +28.9% | +6.2% | +22.75% | +0.84% | +0.00% | +6.69% |

## 6. New-venue premium

Young chains (first DefiLlama TVL on/after 2022-09-01): APTOS 2022-10-21, TON 2022-12-06, Starknet 2022-12-08, Flare 2023-01-11, CORE 2023-02-09, zkSync_Era 2023-03-25, Polygon_zkEVM 2023-03-28, Sui 2023-05-06, Neutron 2023-06-07, Mantle 2023-07-17, Linea 2023-07-19, Base 2023-07-27, Opbnb 2023-08-16, Sei 2023-08-17, Manta 2023-09-15, Scroll 2023-10-11, Bifrost_Network 2023-10-18, Nolus 2023-10-19, Mode 2023-11-23, Stellar 2024-02-27, Blast 2024-02-29, Fraxtal 2024-03-08, Sapphire 2024-03-12, Venom 2024-04-03, Bsquared 2024-04-19, Xlayer 2024-04-22, Bob 2024-05-02, Re.al 2024-05-23, Taiko 2024-05-27, IOTA_EVM 2024-06-06, Etherlink 2024-06-27, Cronos_zkEVM 2024-08-16, Gravity 2024-08-30, Polynomial 2024-09-13, Fuel-ignition 2024-10-18, Hyperliquid_L1 2024-12-01, Hyperliquid 2024-12-01, Sonic 2024-12-17, Ink 2024-12-18, Swellchain 2024-12-21, Plume 2025-01-30, Berachain 2025-02-06, Unichain 2025-02-11, Hemi 2025-03-04, Move 2025-03-11, Saga 2025-03-11, Plume_Mainnet 2025-04-10, Katana 2025-05-22, Echelon_Initia 2025-06-06, TAC 2025-07-18, Plasma 2025-09-19, Mezo 2025-10-01, ZIGChain 2025-11-05, Monad 2025-11-20, Stable 2025-12-08, MegaETH 2025-12-30, Tempo 2026-03-21, Pharos 2026-05-12, Strato 2026-05-15, Robinhood_Chain 2026-07-02

| chain age | pool-windows | chains | displayed | premium vs old-chain median | reward at sale | losses | net excess |
|---|---|---|---|---|---|---|---|
| m0-1 | 9 | 4 | +7.1% | +1.3% | +3.3% | -0.35% | +2.29% |
| m1-2 | 33 | 11 | +10.8% | +4.7% | +3.9% | -1.05% | +3.42% |
| m2-3 | 46 | 12 | +11.8% | +6.1% | +4.1% | +0.00% | +5.21% |
| m3-6 | 228 | 24 | +7.2% | +2.1% | +2.2% | -0.01% | +2.10% |
| m6-12 | 586 | 32 | +9.9% | +4.2% | +2.3% | -0.26% | +3.46% |
| m12-24 | 857 | 28 | +7.9% | +1.9% | +1.6% | -0.63% | +1.13% |
| m24+ | 927 | 15 | +7.1% | +2.0% | +1.3% | -2.72% | -0.21% |

Old chains: displayed +6.7%, net excess -1.02% (15268 pool-windows).
Half-life of the displayed premium: 24.4 months (A 4.1 pp); of the net excess: 8.5 months.

| new-chain rule ($1M, N=5, weekly) | excess (OOS) | t | 95% interval | gross | max DD | weeks |
|---|---|---|---|---|---|---|
| new_chain_lending_180d_score in sample | -0.02% | -0.13 | -0.41% to +0.32% | +4.12% | +0.36% | 89 |
| new_chain_lending_180d_score OOS | -0.50% | -1.42 | -1.13% to +0.19% | +4.81% | +1.13% | 118 |
| new_chain_lending_180d_score: excess when invested -0.04% in sample (54 wk), -0.60% out of sample (98 wk, t -1.43); chains Base, Berachain, Blast, Canto, Echelon Initia, Katana, Manta, MegaETH, Mode, Monad, Move, Plasma, Robinhood Chain, Sonic, Stable, Tempo, Unichain; active weeks 152; losses collapse n=11 $0; dark n=7 $0; share n=2 $-513 | | | | | | |
| new_chain_lending_180d_tvl in sample | -0.02% | -0.13 | -0.41% to +0.32% | +4.12% | +0.36% | 89 |
| new_chain_lending_180d_tvl OOS | -0.96% | -2.93 | -1.50% to -0.28% | +4.35% | +2.17% | 118 |
| new_chain_lending_180d_tvl: excess when invested -0.04% in sample (54 wk), -1.15% out of sample (98 wk, t -3.12); chains Base, Berachain, Blast, Canto, Echelon Initia, Katana, Manta, MegaETH, Mode, Monad, Move, Plasma, Robinhood Chain, Sonic, Stable, Tempo, Unichain; active weeks 152; losses collapse n=9 $0; dark n=1 $0 | | | | | | |
| new_chain_lending_90d_score in sample | -0.08% | -0.80 | -0.28% to +0.13% | +4.07% | +0.27% | 89 |
| new_chain_lending_90d_score OOS | +0.05% | 0.18 | -0.42% to +0.58% | +5.35% | +0.47% | 118 |
| new_chain_lending_90d_score: excess when invested -0.38% in sample (19 wk), +0.09% out of sample (64 wk, t 0.19); chains Base, Berachain, Blast, Echelon Initia, Monad, Move, Plasma, Robinhood Chain, Sonic, Tempo; active weeks 83; losses collapse n=8 $0; dark n=4 $0; share n=1 $-479 | | | | | | |
| new_chain_lending_90d_tvl in sample | -0.08% | -0.80 | -0.28% to +0.13% | +4.07% | +0.27% | 89 |
| new_chain_lending_90d_tvl OOS | -0.23% | -0.89 | -0.69% to +0.32% | +5.07% | +0.91% | 118 |
| new_chain_lending_90d_tvl: excess when invested -0.38% in sample (19 wk), -0.43% out of sample (64 wk, t -0.94); chains Base, Berachain, Blast, Echelon Initia, Monad, Move, Plasma, Robinhood Chain, Sonic, Tempo; active weeks 83; losses collapse n=6 $0; dark n=1 $0 | | | | | | |

## 7. Capacity at 2026-10-05 (marginal yield falls to SSR + 1pp = +4.80%)

chosen_all: sum $25.2M — neutral-trade Solana USDC TVL $1.4M yield +62.9% X* $3.7M; royco-v2 Ethereum JRROYAPYUSD TVL $1.2M yield +54.0% X* $2.9M; neutral-trade Solana USDC TVL $2.3M yield +66.5% X* $6.2M; gains-network Arbitrum USDC TVL $4.8M yield +45.7% X* $10.1M; pendle-v2 Ethereum SUSDAT TVL $1.4M yield +36.0% X* $2.4M
chosen_bluechip: sum $30.6M — morpho-blue Ethereum APYXAPXUSD TVL $1.9M yield +14.2% X* $1.3M; morpho-blue Ethereum FCUSDT TVL $17.4M yield +13.7% X* $12.0M; morpho-blue Ethereum ROXCUSDC TVL $20.4M yield +12.4% X* $12.3M; morpho-blue Base NOONECOUSDC TVL $3.2M yield +10.1% X* $1.4M; morpho-blue Monad AUGUSTUSDCV2 TVL $8.4M yield +9.6% X* $3.5M
universe_all: 672 eligible, 335 above the hurdle, sum $2.02B; largest: usd-ai Arbitrum SUSDAI $119.1M; morpho-blue Robinhood Chain STEAKUSDG $110.6M; apyx-protocol Ethereum APXUSD $109.4M; maple Ethereum USDC $106.7M; morpho-blue Ethereum SENPYUSDMAIN $63.9M; morpho-blue Ethereum SENRLUSDV2 $63.9M; usual-usd0 Ethereum BUSD0 $63.6M; re Ethereum REUSD $54.5M
universe_bluechip: 242 eligible, 80 above the hurdle, sum $633.7M; largest: morpho-blue Robinhood Chain STEAKUSDG $110.6M; maple Ethereum USDC $106.7M; morpho-blue Ethereum SENPYUSDMAIN $63.9M; morpho-blue Ethereum SENRLUSDV2 $63.9M; morpho-blue Base SIRLOINUSDC $42.3M; morpho-blue Ethereum SENPYUSDPRIMEV2 $40.4M; maple Ethereum USDT $35.2M; morpho-blue Ethereum SENPYUSDPST $18.4M

## 8. Incentive spend now (sum tvlUsd x apyReward, clean = apyReward <= 500% and tvlUsd >= $10k)

Total $580.6M a year (raw $2.45B), 1877 pools paying; stable $268.5M, volatile $312.0M; USD-stable single-exposure $233.7M on TVL $7.33B.

Top chains: Ethereum $249.4M; Base $187.8M; Robinhood Chain $37.0M; Avalanche $20.5M; Tron $17.6M; Hyperliquid L1 $15.3M; Monad $10.8M; OP Mainnet $9.5M; Sui $7.9M; Solana $6.3M; Tempo $2.3M; Berachain $2.3M; Arbitrum $2.1M; Mezo $1.9M; Flare $1.4M

Top projects: morpho-blue $126.3M; aerodrome-slipstream $100.5M; sky-lending $53.4M; aerodrome-v1 $47.4M; usual-usd0 $31.1M; sparklend $24.5M; convex-finance $23.9M; curve-dex $20.8M; pharaoh-v3 $18.0M; justlend-v1 $17.6M; stake-dao-yield $13.1M; nest-cl $12.2M; aave-v3 $11.2M; zeebu $7.3M; velodrome-v2 $6.0M

Through the captures (clean total / stable / volatile / USD-stable single): 2022-10-13 $909.4M/$257.7M/$651.7M/$90.6M; 2022-12-15 $850.0M/$171.4M/$678.6M/$54.6M; 2023-02-16 $1.28B/$280.1M/$1.00B/$87.9M; 2023-06-06 $663.1M/$156.3M/$506.9M/$57.0M; 2023-10-03 $475.2M/$122.3M/$352.9M/$39.7M; 2024-02-05 $637.3M/$149.8M/$487.5M/$68.5M; 2024-09-01 $854.7M/$126.9M/$727.8M/$49.9M; 2025-03-01 $783.0M/$292.8M/$490.3M/$247.6M; 2025-05-01 $1.01B/$336.8M/$677.6M/$227.6M; 2025-07-01 $828.7M/$254.2M/$574.5M/$187.1M; 2025-09-01 $1.18B/$401.6M/$775.0M/$211.1M; 2025-10-31 $931.3M/$447.6M/$483.7M/$230.9M; 2026-01-01 $575.4M/$337.4M/$238.0M/$203.9M; 2026-03-01 $515.3M/$305.3M/$210.0M/$250.8M; 2026-04-30 $389.3M/$209.5M/$179.9M/$164.4M; 2026-07-01 $353.9M/$175.6M/$178.3M/$143.6M; 2026-09-01 $520.4M/$259.9M/$260.5M/$221.0M

## 9. Survivorship

{"bound": {"estimated_missing_pool_days_tvl_1m": 85.75, "missing_share_upper_bound": 0.00015584993877323835, "note": "never-captured ids from the universe projects, any asset (an upper bound for dollar pools)", "sample_pool_days_tvl_1m": 1, "sample_pools_ever_1m": 1, "universe_pool_days_tvl_1m_after_start": 550123}, "dead_share": 0.6099885627144491, "dead_today": 1600, "missing_chart_check": {"all": {"examples": [], "share": 0.0, "slots": 1360, "slots_without_chart": 0, "top": 10}, "bluechip": {"examples": [], "share": 0.0, "slots": 1360, "slots_without_chart": 0, "top": 10}}, "pools_with_chart": 2623, "universe_build": {"first": "20221013234043", "last": "20261010", "pools_any_tvl": 8254, "pools_kept": 5080, "snapshots": 136}, "wayback": {"capture_days_in_cdx": 462, "first": "2022-10-13", "have": 135, "picked": 135, "rule": "closest capture within 7 days of the 1st, 8th, 15th and 22nd of each month"}}
distinctID sample: {"distinct_ids": 401835, "fetched": 80, "ids_seen_at_captures": 203279, "sampled": 80, "unseen_in_universe_projects": 6860}

## 10. Independent check: on-chain supply rate vs DefiLlama apyBase

n 42, mean difference -0.728 pp, mean |difference| 1.026 pp, max |difference| 9.301 pp

| pool | day | on-chain APY | DefiLlama apyBase |
|---|---|---|---|
| aave-v3 USDC | 2023-03-15 | 1.126% | 1.551% |
| aave-v3 USDC | 2023-07-15 | 2.855% | 2.668% |
| aave-v3 USDC | 2023-11-15 | 6.193% | 8.325% |
| aave-v3 USDC | 2024-03-15 | 10.639% | 6.063% |
| aave-v3 USDC | 2024-07-15 | 5.936% | 5.808% |
| aave-v3 USDC | 2024-11-15 | 8.499% | 4.168% |
| aave-v3 USDC | 2025-03-15 | 2.762% | 2.792% |
| aave-v3 USDC | 2025-07-15 | 4.019% | 3.561% |
| aave-v3 USDC | 2025-11-15 | 4.171% | 4.178% |
| aave-v3 USDC | 2026-03-15 | 2.052% | 1.821% |
| aave-v3 USDC | 2026-07-15 | 3.227% | 3.251% |
| aave-v3 USDC | 2026-10-05 | 3.993% | 4.570% |
| aave-v3 USDT | 2023-03-15 | 2.656% | 2.486% |
| aave-v3 USDT | 2023-07-15 | 2.658% | 2.788% |
| aave-v3 USDT | 2023-11-15 | 5.971% | 5.379% |
| aave-v3 USDT | 2024-03-15 | 14.137% | 4.836% |
| aave-v3 USDT | 2024-07-15 | 6.134% | 5.966% |
| aave-v3 USDT | 2025-03-15 | 5.379% | 2.763% |
| aave-v3 USDT | 2025-07-15 | 3.468% | 3.579% |
| aave-v3 USDT | 2025-11-15 | 3.488% | 3.221% |
| aave-v3 USDT | 2026-07-15 | 2.695% | 2.654% |
| aave-v3 USDT | 2026-10-05 | 3.614% | 3.711% |
| sparklend DAI | 2023-07-15 | 1.492% | 1.481% |
| sparklend DAI | 2023-11-15 | 4.920% | 4.874% |
| sparklend DAI | 2024-03-15 | 15.168% | 14.140% |
| sparklend DAI | 2024-07-15 | 7.714% | 8.122% |
| sparklend DAI | 2024-11-15 | 8.005% | 6.112% |
| sparklend DAI | 2025-03-15 | 5.980% | 5.812% |
| sparklend DAI | 2026-07-15 | 2.367% | 2.339% |
| sparklend DAI | 2026-10-05 | 2.887% | 2.708% |
| compound-v3 USDC | 2023-03-15 | 2.036% | 1.996% |
| compound-v3 USDC | 2023-07-15 | 6.269% | 4.401% |
| compound-v3 USDC | 2023-11-15 | 3.210% | 5.277% |
| compound-v3 USDC | 2024-03-15 | 13.469% | 9.223% |
| compound-v3 USDC | 2024-07-15 | 5.662% | 5.477% |
| compound-v3 USDC | 2024-11-15 | 9.951% | 7.774% |
| compound-v3 USDC | 2025-03-15 | 4.065% | 3.931% |
| compound-v3 USDC | 2025-07-15 | 4.483% | 3.593% |
| compound-v3 USDC | 2025-11-15 | 3.279% | 3.534% |
| compound-v3 USDC | 2026-03-15 | 2.548% | 2.334% |
| compound-v3 USDC | 2026-07-15 | 3.272% | 3.228% |
| compound-v3 USDC | 2026-10-05 | 4.486% | 3.864% |
