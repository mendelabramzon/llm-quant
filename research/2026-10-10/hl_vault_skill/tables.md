# hl_vault_skill — tables

Generated 2026-10-10T17:19:02Z from analysis.json (precommit af4ad9046f24…, written 2026-10-10T15:11:55Z). Monthly decisions; holding windows start at each vault's first grid point at or after the decision (median 4.0 days later, max 14.0). Returns are net of flows; "net" is after the leader's profit share in a simulated follower account; excess is over the savings rate paid in each year unless marked SSR.

## Data

| item | value |
|---|---|
| vaults in the stats file (closed) | 9477 (6387) |
| vaultDetails fetched: core / random sample of the rest | 3214 / 626 |
| HLP family excluded | 8 vaults |
| grid step (core vaults: 1d / 7d / 14d) | 6 / 2073 / 1105 |
| step flags (core) | closing 1658, dietz_fallback 1100, gt100pct 478, wipeout 184 |
| flagged steps inside u10k holding windows | dietz_fallback 26, gt100pct 14, wipeout 11 |
| decision calendar | 2025-01-01 → 2026-09-01, 21 months |
| choose / test | 2025-01-01..2025-10-01 / 2025-11-01..2026-09-01 |
| vault-months u10k / u100k | 2141 / 685 |

Eligible vaults by month (later-closed counted in u10k):

| month | u10k | u100k | u100k equity | u10k later closed |
|---|---:|---:|---:|---:|
| 2025-01-01 | 49 | 14 | $14.95M | 21 |
| 2025-02-01 | 47 | 9 | $12.30M | 16 |
| 2025-03-01 | 58 | 14 | $14.12M | 21 |
| 2025-04-01 | 59 | 16 | $11.62M | 24 |
| 2025-05-01 | 53 | 13 | $13.98M | 17 |
| 2025-06-01 | 58 | 15 | $10.84M | 17 |
| 2025-07-01 | 69 | 17 | $10.76M | 20 |
| 2025-08-01 | 92 | 24 | $20.42M | 23 |
| 2025-09-01 | 105 | 28 | $20.54M | 24 |
| 2025-10-01 | 117 | 36 | $29.35M | 34 |
| 2025-11-01 | 104 | 33 | $25.10M | 23 |
| 2025-12-01 | 99 | 37 | $24.90M | 21 |
| 2026-01-01 | 105 | 38 | $24.49M | 20 |
| 2026-02-01 | 120 | 43 | $28.69M | 22 |
| 2026-03-01 | 118 | 41 | $26.72M | 20 |
| 2026-04-01 | 126 | 44 | $43.69M | 19 |
| 2026-05-01 | 132 | 48 | $49.95M | 20 |
| 2026-06-01 | 146 | 46 | $51.45M | 17 |
| 2026-07-01 | 152 | 55 | $60.64M | 11 |
| 2026-08-01 | 160 | 55 | $63.68M | 10 |
| 2026-09-01 | 172 | 59 | $77.90M | 7 |

## Independent checks

- Stats-file coarse allTime P&L vs vaultDetails P&L, closed vaults: n 2293, exact to $1 100.0%, within 1% 100.0%, median rel. diff 0.000%, p95 0.00%.
- Stats-file coarse allTime P&L vs vaultDetails P&L, open vaults: n 1547, exact to $1 79.6%, within 1% 91.4%, median rel. diff 0.000%, p95 2.54%.
- Listed followers (single spell, >= 60 days, >= $1k basis): own P&L / basis vs this study's index over the same dates: n 1210, Spearman 0.911, median diff -0.02%, median |diff| 2.25%, within 5pp 60.9%; mean -25.79% (followers) vs -22.78% (index).
- Stats file alone, lifetime dollar P&L of all 9469 user vaults (HLP family out, leaders' money in): $-69.67M in total (gains $54.50M, losses $-124.17M); 22.7% of vaults ended positive, 24.8% lost more than $1k; closed vaults $-24.32M, open vaults $-45.34M.
- Same check, followers of 7-60 days (less room for top-ups): n 390, Spearman 0.908, median |diff| 1.13%, within 5pp 76.9%.
  - low flow vaults: n 36, Spearman 0.964, median |diff| 1.36%, within 5pp 77.8%.
  - high flow vaults: n 1174, Spearman 0.906, median |diff| 2.29%, within 5pp 60.4%.

## The vault market: every eligible vault

| portfolio | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |
|---|---:|---:|---:|---:|---:|---:|
| u10k|ew|all net | -71.90% | -1.42 | -21.46% | -0.71 | -1.03 | -9.00% |
| u10k|ew|survivors_only net | -67.76% | -1.36 | -17.57% | -0.58 | -0.83 | -9.66% |
| u10k|cw|all net | -94.10% | -2.00 | +30.41% | 2.37 | 2.26 | -2.63% |
| u10k|cw|survivors_only net | -101.09% | -1.88 | +35.68% | 2.99 | 2.53 | -2.49% |
| u100k|ew|all net | -75.79% | -1.49 | -1.73% | -0.09 | -0.12 | -4.71% |
| u100k|ew|survivors_only net | -84.93% | -1.47 | +6.27% | 0.35 | 0.43 | -4.15% |
| u100k|cw|all net | -99.05% | -1.92 | +35.37% | 3.03 | 2.64 | -1.97% |
| u100k|cw|survivors_only net | -106.07% | -1.83 | +40.10% | 3.62 | 2.84 | -1.83% |

Pooled vault-months (each vault-month weighs the same; mean monthly holding return before fees):

| universe / part | n | mean | median | survivors (n, mean) | later closed (n, mean) | closed within the month |
|---|---:|---:|---:|---|---|---:|
| u10k|in | 707 | -5.03% | -0.00% | 490, -4.41% | 217, -6.44% | 6.08% |
| u10k|out | 1434 | -0.15% | +0.00% | 1244, +0.58% | 190, -4.91% | 2.37% |
| u10k|full | 2141 | -1.76% | +0.00% | 1734, -0.83% | 407, -5.73% | 3.60% |
| u100k|in | 186 | -5.36% | -0.02% | 122, -5.91% | 64, -4.30% | 5.91% |
| u100k|out | 499 | +0.98% | +0.29% | 438, +1.83% | 61, -5.13% | 1.80% |
| u100k|full | 685 | -0.74% | +0.12% | 560, +0.15% | 125, -4.71% | 2.92% |

## Persistence: monthly rank IC of each signal with the next holding return

| signal / universe | IC in | t in | IC out | t out | share of months > 0 (out) | IC out, survivors only |
|---|---:|---:|---:|---:|---:|---:|
| ret3|u10k | 0.059 | 1.46 | 0.082 | 1.42 | 64% | 0.077 |
| ret6|u10k | 0.053 | 1.91 | 0.113 | 3.15 | 82% | 0.104 |
| sharpe6|u10k | 0.091 | 3.80 | 0.116 | 2.92 | 82% | 0.108 |
| mdd6|u10k | 0.106 | 2.77 | 0.092 | 1.54 | 73% | 0.076 |
| flow3|u10k | -0.058 | -1.17 | -0.039 | -1.18 | 45% | -0.064 |
| tvlg3|u10k | 0.006 | 0.09 | 0.030 | 0.84 | 64% | 0.005 |
| size|u10k | -0.001 | -0.02 | 0.079 | 5.01 | 91% | 0.077 |
| ret3|u100k | -0.010 | -0.08 | -0.018 | -0.23 | 64% | -0.017 |
| ret6|u100k | 0.030 | 0.38 | -0.046 | -1.02 | 64% | -0.068 |
| sharpe6|u100k | 0.054 | 0.72 | -0.038 | -0.60 | 55% | -0.058 |
| mdd6|u100k | 0.137 | 1.40 | -0.008 | -0.14 | 64% | -0.036 |
| flow3|u100k | -0.089 | -2.61 | 0.016 | 0.32 | 36% | -0.020 |
| tvlg3|u100k | -0.020 | -0.27 | 0.016 | 0.25 | 73% | -0.014 |
| size|u100k | -0.025 | -0.23 | 0.093 | 2.34 | 82% | 0.085 |

Quintiles (equal-weight mean monthly holding return before fees; q5 = highest signal):

| signal / universe | part | q1 | q2 | q3 | q4 | q5 | q5 − q1 | t |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| ret3|u10k | in | -9.24% | -2.78% | -3.47% | -5.42% | -4.98% | +4.26% | 1.20 |
| ret3|u10k | out | -2.39% | -3.10% | -1.29% | +0.25% | +0.92% | +3.31% | 0.53 |
| ret6|u10k | in | -12.24% | +0.50% | -4.24% | -1.19% | -8.62% | +3.61% | 0.87 |
| ret6|u10k | out | -5.52% | -1.18% | -2.60% | +1.61% | +2.04% | +7.56% | 1.58 |
| sharpe6|u10k | in | -10.03% | -4.39% | -1.38% | -3.98% | -5.21% | +4.82% | 1.56 |
| sharpe6|u10k | out | -3.74% | -1.89% | -1.31% | -1.80% | +3.07% | +6.80% | 1.70 |
| mdd6|u10k | in | -10.22% | -5.21% | -3.12% | -3.61% | -3.80% | +6.42% | 1.47 |
| mdd6|u10k | out | -1.85% | -2.07% | +0.15% | -1.24% | -0.59% | +1.26% | 0.22 |
| flow3|u10k | in | -1.12% | -1.75% | -4.61% | -5.67% | -11.81% | -10.70% | -1.92 |
| flow3|u10k | out | +1.53% | +0.36% | -0.72% | -4.58% | -1.87% | -3.40% | -1.52 |
| size|u10k | in | -3.45% | -6.29% | -6.06% | -4.31% | -5.08% | -1.63% | -0.82 |
| size|u10k | out | -0.88% | -1.70% | -2.75% | -3.88% | +3.64% | +4.53% | 1.79 |
| ret3|u100k | in | -1.52% | -0.91% | -4.30% | -0.97% | -11.24% | -9.72% | -0.79 |
| ret3|u100k | out | +3.00% | +1.23% | -1.68% | -0.29% | +0.25% | -2.75% | -0.63 |
| ret6|u100k | in | -5.05% | +3.11% | -5.24% | -7.39% | -4.48% | +0.57% | 0.07 |
| ret6|u100k | out | +6.28% | -3.24% | -0.77% | -0.64% | +0.98% | -5.30% | -1.77 |
| sharpe6|u100k | in | -7.74% | +2.60% | -2.89% | -6.34% | -6.30% | +1.44% | 0.28 |
| sharpe6|u100k | out | +3.74% | -0.47% | -0.50% | +0.37% | -0.78% | -4.52% | -1.52 |
| mdd6|u100k | in | -8.68% | -3.11% | -0.93% | -3.76% | -4.21% | +4.46% | 0.57 |
| mdd6|u100k | out | +4.47% | -0.98% | +0.98% | -1.81% | -0.04% | -4.51% | -1.10 |
| flow3|u100k | in | -3.68% | +1.55% | +2.81% | -9.29% | -11.54% | -7.86% | -1.07 |
| flow3|u100k | out | +1.29% | +1.35% | +1.81% | +0.36% | -1.78% | -3.08% | -0.91 |
| size|u100k | in | -0.62% | -7.13% | -0.83% | +5.53% | -14.19% | -13.57% | -1.72 |
| size|u100k | out | -6.08% | -2.68% | +2.18% | +4.40% | +3.92% | +10.00% | 2.73 |

## The 56 pre-committed variants (net excess over the savings rate paid, per year)

Chosen on the first half by Sharpe: **size|q10|cw|u100k**; its out-of-sample rank 1 of 56; deflated Sharpe of the choice (in sample, 56 tried) 0.055; BH survivors out of sample (q 0.10): ret6|q10|ew|u10k, size|q5|ew|u100k, size|q5|cw|u10k, size|q5|cw|u100k, size|q10|ew|u10k, size|q10|ew|u100k, size|q10|cw|u10k, size|q10|cw|u100k.

| variant | in: net/yr | in Sharpe | out: net/yr | out t | BH adj. p | out gross/yr | mean held | out max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| size|q10|cw|u100k | -105.07% | -0.87 | +44.38% | 3.59 | 0.005 | +49.62% | 3.3 | 2.3% |
| size|q10|ew|u100k | -103.07% | -0.91 | +57.55% | 2.59 | 0.076 | +64.07% | 3.3 | 10.2% |
| mdd6|q10|cw|u10k | -62.23% | -0.93 | +6.51% | 0.41 | 0.863 | +8.89% | 10.2 | 9.9% |
| ret6|q5|ew|u100k | -63.98% | -0.93 | -0.23% | -0.01 | 0.992 | +5.75% | 6.6 | 21.7% |
| mdd6|q10|cw|u100k | -79.25% | -0.97 | +10.37% | 0.89 | 0.701 | +12.67% | 3.3 | 9.8% |
| mdd6|q10|ew|u100k | -84.06% | -1.05 | -8.42% | -0.78 | 0.720 | -7.26% | 3.3 | 9.2% |
| size|q5|cw|u10k | -101.20% | -1.21 | +42.91% | 3.95 | 0.001 | +47.62% | 20.4 | 2.1% |
| sharpe6|q5|ew|u100k | -50.78% | -1.24 | -16.10% | -1.34 | 0.592 | -13.41% | 6.6 | 20.5% |
| size|q10|cw|u10k | -116.19% | -1.26 | +48.50% | 4.44 | 0.001 | +53.58% | 10.2 | 2.7% |
| ret3|q10|ew|u100k | -157.61% | -1.26 | +11.90% | 0.39 | 0.863 | +20.15% | 3.3 | 23.5% |
| flow3|q10|ew|u100k | -145.04% | -1.30 | -29.92% | -1.01 | 0.701 | -23.27% | 3.3 | 34.5% |
| mdd6|q5|cw|u10k | -30.74% | -1.34 | +1.13% | 0.08 | 0.992 | +3.27% | 20.4 | 8.5% |
| size|q5|cw|u100k | -145.96% | -1.36 | +41.79% | 3.98 | 0.001 | +46.24% | 6.6 | 2.4% |
| flow3|q10|cw|u100k | -157.14% | -1.42 | -26.68% | -0.85 | 0.701 | -20.35% | 3.3 | 38.4% |
| ret6|q5|cw|u100k | -126.22% | -1.46 | +15.70% | 0.54 | 0.815 | +21.92% | 6.6 | 16.9% |
| tvlg3|q10|ew|u100k | -167.46% | -1.46 | -32.84% | -1.27 | 0.632 | -26.76% | 3.3 | 37.2% |
| ret6|q10|ew|u10k | -87.42% | -1.49 | +68.73% | 2.67 | 0.070 | +82.65% | 10.2 | 10.7% |
| sharpe6|q10|ew|u100k | -117.34% | -1.50 | +0.39% | 0.01 | 0.992 | +3.96% | 3.3 | 22.6% |
| ret3|q5|ew|u10k | -75.04% | -1.55 | +0.49% | 0.03 | 0.992 | +9.28% | 20.4 | 18.4% |
| ret3|q5|cw|u10k | -98.10% | -1.57 | -7.37% | -0.20 | 0.963 | -0.87% | 20.4 | 34.2% |
| ret3|q10|cw|u100k | -201.26% | -1.62 | +34.44% | 1.04 | 0.697 | +42.25% | 3.3 | 13.9% |
| sharpe6|q5|cw|u100k | -93.42% | -1.62 | -19.43% | -0.64 | 0.772 | -15.24% | 6.6 | 26.2% |
| ret6|q5|cw|u10k | -98.80% | -1.69 | +9.55% | 0.35 | 0.885 | +15.20% | 20.4 | 18.5% |
| ret6|q10|cw|u10k | -143.99% | -1.71 | +55.77% | 1.84 | 0.331 | +66.73% | 10.2 | 9.3% |
| tvlg3|q5|cw|u10k | -154.82% | -1.73 | +4.80% | 0.23 | 0.954 | +11.43% | 20.4 | 14.7% |
| tvlg3|q5|cw|u100k | -151.14% | -1.77 | +46.58% | 1.11 | 0.696 | +57.73% | 6.6 | 18.3% |
| tvlg3|q10|cw|u100k | -201.04% | -1.79 | -37.45% | -1.17 | 0.676 | -31.20% | 3.3 | 51.0% |
| ret6|q10|ew|u100k | -218.41% | -1.81 | +30.98% | 0.87 | 0.701 | +40.44% | 3.3 | 18.4% |
| sharpe6|q10|ew|u10k | -85.62% | -1.83 | +11.00% | 0.84 | 0.701 | +15.86% | 10.0 | 9.0% |
| size|q5|ew|u10k | -68.61% | -1.84 | +35.36% | 2.34 | 0.120 | +40.66% | 20.4 | 4.2% |
| mdd6|q10|ew|u10k | -71.14% | -1.87 | -14.16% | -1.68 | 0.399 | -12.81% | 10.2 | 16.1% |
| sharpe6|q10|cw|u10k | -104.24% | -1.89 | -12.11% | -0.53 | 0.815 | -8.77% | 10.0 | 19.2% |
| flow3|q5|cw|u10k | -174.92% | -1.89 | +73.58% | 1.07 | 0.696 | +86.61% | 20.4 | 25.3% |
| ret3|q5|cw|u100k | -187.21% | -1.92 | -1.23% | -0.02 | 0.992 | +6.46% | 6.6 | 46.9% |
| flow3|q5|cw|u100k | -183.15% | -1.93 | +51.28% | 0.93 | 0.701 | +64.00% | 6.6 | 28.1% |
| sharpe6|q10|cw|u100k | -183.13% | -1.94 | +2.66% | 0.09 | 0.992 | +6.47% | 3.3 | 19.9% |
| tvlg3|q5|ew|u100k | -156.46% | -2.00 | -11.02% | -0.45 | 0.847 | -4.37% | 6.6 | 26.7% |
| size|q10|ew|u10k | -94.65% | -2.00 | +54.37% | 2.50 | 0.088 | +61.32% | 10.2 | 5.9% |
| sharpe6|q5|ew|u10k | -80.43% | -2.05 | +25.44% | 2.06 | 0.222 | +32.19% | 19.8 | 5.5% |
| ret6|q10|cw|u100k | -265.45% | -2.07 | +48.28% | 1.24 | 0.632 | +57.58% | 3.3 | 12.0% |
| ret3|q5|ew|u100k | -171.27% | -2.08 | -6.72% | -0.25 | 0.954 | +0.33% | 6.6 | 26.0% |
| size|q5|ew|u100k | -176.33% | -2.12 | +37.43% | 2.91 | 0.040 | +42.40% | 6.6 | 6.1% |
| tvlg3|q5|ew|u10k | -151.53% | -2.12 | -12.57% | -0.52 | 0.815 | -4.66% | 20.4 | 31.4% |
| flow3|q5|ew|u10k | -154.87% | -2.14 | -34.38% | -0.94 | 0.701 | -26.29% | 20.4 | 47.2% |
| ret3|q10|ew|u10k | -142.22% | -2.15 | +57.14% | 1.39 | 0.578 | +71.13% | 10.2 | 21.0% |
| ret6|q5|ew|u10k | -118.05% | -2.32 | +13.23% | 0.66 | 0.772 | +20.91% | 20.4 | 13.1% |
| mdd6|q5|ew|u10k | -56.30% | -2.35 | -12.00% | -1.52 | 0.516 | -10.57% | 20.4 | 15.0% |
| ret3|q10|cw|u10k | -202.75% | -2.35 | +35.20% | 0.65 | 0.772 | +45.73% | 10.2 | 34.7% |
| mdd6|q5|ew|u100k | -63.68% | -2.38 | -5.73% | -0.81 | 0.707 | -4.25% | 6.6 | 7.6% |
| mdd6|q5|cw|u100k | -50.86% | -2.39 | +0.21% | 0.02 | 0.992 | +2.15% | 6.6 | 9.2% |
| flow3|q5|ew|u100k | -189.63% | -2.44 | -31.45% | -0.88 | 0.701 | -24.79% | 6.6 | 44.1% |
| flow3|q10|cw|u10k | -260.32% | -2.64 | -56.68% | -1.78 | 0.349 | -49.67% | 10.1 | 56.4% |
| sharpe6|q5|cw|u10k | -112.85% | -2.65 | -13.92% | -0.51 | 0.815 | -9.54% | 19.8 | 20.5% |
| flow3|q10|ew|u10k | -206.05% | -2.70 | -44.70% | -1.07 | 0.696 | -34.76% | 10.1 | 63.3% |
| tvlg3|q10|ew|u10k | -207.44% | -2.70 | -50.99% | -1.47 | 0.533 | -42.33% | 10.1 | 67.6% |
| tvlg3|q10|cw|u10k | -268.09% | -2.74 | -15.04% | -0.64 | 0.772 | -6.13% | 10.1 | 28.5% |

## The chosen variant: size|q10|cw|u100k

| series | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |
|---|---:|---:|---:|---:|---:|---:|
| net, over savings paid | -105.07% | -1.36 | +44.38% | 3.59 | 2.99 | -2.31% |
| net, over SSR 3.80% | -103.37% | -1.33 | +44.61% | 3.64 | 3.02 | -2.32% |
| gross (no profit share) | -98.86% | -1.25 | +49.62% | 3.67 | 3.13 | -1.66% |
| net, 10% of every positive month | -111.27% | -1.48 | +39.55% | 3.15 | 2.67 | -2.65% |
| net, entering one grid step late | -165.65% | -3.75 | +41.41% | 2.85 | 1.89 | -5.99% |
| net, 10bp friction on turnover | -105.77% | -1.36 | +43.94% | 3.54 | 2.96 | -2.36% |
| net, survivors only (biased) | -101.91% | -0.90 | +45.26% | 2.97 | 2.82 | -2.00% |
| net, vaults taking deposits today | -119.31% | -1.10 | +41.58% | 1.84 | 1.96 | -6.85% |

Out of sample: block-bootstrap 95% interval of the monthly mean +1.81% to +5.97% (point +3.70%); deflated Sharpe (56 variants) 0.707. Monthly one-sided turnover 22.2%; profit share paid 2.36% of capital a year; median equity of the selected vaults $12.74M (out of sample $26.61M); 0 of 70 selected vault-months closed inside the month.

Factor regressions of monthly excess return (HAC t, 2 lags):

| series | n | alpha/yr | t | beta BTC | t | gamma abs BTC | t | beta HYPE | t | R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chosen, gross | 21 | +22.69% | 0.29 | -0.62 | -1.07 | -0.34 | -0.49 | — | — | 0.09 |
| chosen, net | 21 | +18.04% | 0.23 | -0.61 | -1.07 | -0.35 | -0.51 | — | — | 0.09 |
| chosen, gross, with HYPE | 21 | -37.48% | -0.63 | -0.38 | -1.05 | 0.56 | 0.77 | -0.33 | -1.58 | 0.20 |
| market u10k|ew|all, gross | 21 | -69.66% | -1.56 | 0.37 | 2.70 | 0.24 | 0.91 | — | — | 0.26 |
| market u10k|ew|all, gross, with HYPE | 21 | -48.54% | -1.06 | 0.29 | 2.65 | -0.07 | -0.23 | 0.12 | 2.80 | 0.35 |
| market u10k|cw|all, gross | 21 | -26.48% | -0.46 | -0.16 | -0.44 | 0.03 | 0.05 | — | — | 0.01 |
| market u10k|cw|all, gross, with HYPE | 21 | -46.87% | -0.97 | -0.08 | -0.31 | 0.33 | 0.62 | -0.11 | -0.86 | 0.04 |
| market u100k|ew|all, gross | 21 | -59.64% | -1.21 | 0.28 | 3.10 | 0.23 | 0.82 | — | — | 0.14 |
| market u100k|ew|all, gross, with HYPE | 21 | -49.21% | -0.96 | 0.24 | 2.51 | 0.07 | 0.21 | 0.06 | 1.53 | 0.16 |
| market u100k|cw|all, gross | 21 | -22.87% | -0.37 | -0.22 | -0.56 | -0.00 | -0.00 | — | — | 0.02 |
| market u100k|cw|all, gross, with HYPE | 21 | -50.09% | -1.00 | -0.12 | -0.42 | 0.40 | 0.71 | -0.15 | -1.03 | 0.06 |
| ret3|q10|ew|u100k, gross | 21 | -49.20% | -0.44 | -0.14 | -0.37 | -0.09 | -0.11 | — | — | 0.00 |
| ret3|q5|cw|u100k, gross | 21 | -138.73% | -1.75 | 0.01 | 0.02 | 0.50 | 0.67 | — | — | 0.02 |
| sharpe6|q5|ew|u100k, gross | 21 | -5.91% | -0.13 | -0.09 | -0.74 | -0.20 | -0.78 | — | — | 0.03 |

## Reference: copy the leaderboard

| strategy | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |
|---|---:|---:|---:|---:|---:|---:|
| ret3|q10|ew|u100k net | -157.61% | -1.49 | +11.90% | 0.39 | 0.34 | -17.49% |
| ret3|q10|ew|u100k net, survivors only | -152.57% | -2.00 | +28.97% | 0.88 | 0.69 | -17.78% |
| ret3|q5|cw|u100k net | -187.21% | -2.28 | -1.23% | -0.02 | -0.03 | -23.31% |
| ret3|q5|cw|u100k net, survivors only | -186.46% | -2.22 | +3.15% | 0.06 | 0.06 | -27.35% |
| sharpe6|q5|ew|u100k net | -50.78% | -1.39 | -16.10% | -1.34 | -0.87 | -11.06% |
| sharpe6|q5|ew|u100k net, survivors only | -38.81% | -0.73 | -11.34% | -1.19 | -0.74 | -7.62% |

## Survivorship

Rerunning all 56 variants on vaults that are open today (the database a leaderboard shows) changes the net excess by +3.05% a year on average over the full calendar (median +3.65%; out of sample +2.43%).

Pre-filter (random 10% sample of the 6.3k vaults left out of the full fetch): 14 of 626 sampled vaults ever held >= $10k, 4 >= $100k.

| universe | sampled vaults ever eligible | est. population | est. vault-months missed | share of universe | mean holding return (sample) |
|---|---:|---:|---:|---:|---:|
| u10k | 0 | 0 | 0 | 0.0% | — |
| u100k | 0 | 0 | 0 | 0.0% | — |

## Capacity at the 2026-10-01 decision

**chosen**: 6 vaults, equity $46.37M, follower room before the leader's 5% floor $102.03M (capped at 10% of each vault: $3.29M); 6 open and taking deposits.

| vault | signal | equity | leader share | room | deposits | listed followers |
|---|---:|---:|---:|---:|---|---:|
| drkmttr (0xc179e0…) | 13532250.848 | $8.88M | 36.8% | $56.55M | open | 100 |
| Growi HF (0x1e37a3…) | 12674518.016 | $13.57M | 5.0% | $6k | open | 100 |
| [ Systemic Strategies ] L/S Grids (0x07fd99…) | 10788835.312 | $9.72M | 7.1% | $4.15M | open | 100 |
| [ Systemic Strategies ] ♾️ HyperGrowth ♾ (0xd6e562…) | 6367391.518 | $6.13M | 10.3% | $6.51M | open | 100 |
| BredoStrategy (0x654016…) | 5855210.587 | $6.41M | 8.8% | $4.87M | open | 100 |
| Long LINK Short XRP (0x73ce82…) | 3135421.468 | $1.66M | 95.2% | $29.94M | open | 100 |

**naive_ret3_q10_u100k**: 6 vaults, equity $18.15M, follower room before the leader's 5% floor $93.60M (capped at 10% of each vault: $1.81M); 6 open and taking deposits.

| vault | signal | equity | leader share | room | deposits | listed followers |
|---|---:|---:|---:|---:|---|---:|
| Long LINK Short XRP (0x73ce82…) | 8.003 | $1.66M | 95.2% | $29.94M | open | 100 |
| DOEZOE (0xcae0d1…) | 4.369 | $26k | 5.3% | $2k | open | 76 |
| Brob (0x749118…) | 3.410 | $1.05M | 15.5% | $2.20M | open | 100 |
| BredoStrategy (0x654016…) | 2.954 | $6.41M | 8.8% | $4.87M | open | 100 |
| drkmttr (0xc179e0…) | 2.291 | $8.88M | 36.8% | $56.55M | open | 100 |
| DailyTradeAI  Low risk (0x44ff91…) | 2.237 | $128k | 6.5% | $38k | open | 113 |

## Post-hoc diagnostics (after the pre-committed result was seen; not part of the test)

Factor regressions on the test half only (11 months):

| series | n | alpha/yr | t | beta BTC | t | gamma abs BTC | t | beta HYPE | t | R² |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chosen, gross | 11 | -2.01% | -0.12 | 0.10 | 1.35 | 0.40 | 2.52 | — | — | 0.50 |
| chosen, net | 11 | -4.23% | -0.27 | 0.09 | 1.31 | 0.38 | 2.47 | — | — | 0.50 |
| chosen, gross, with HYPE | 11 | +3.18% | 0.18 | 0.11 | 1.40 | 0.34 | 1.86 | 0.02 | 0.47 | 0.50 |
| market u100k cw, gross | 11 | -16.55% | -1.60 | 0.12 | 2.50 | 0.44 | 3.99 | — | — | 0.77 |

Where the test-half gross return came from (sum of weight x monthly return +49.17%; 5 distinct vaults held in the choose half, 12 in the test half, 4 in both):

| vault | months held | contribution | share |
|---|---:|---:|---:|
| drkmttr | 3 | +20.21% | 41.1% |
| Growi HF | 11 | +10.85% | 22.1% |
| [ Systemic Strategies ] ♾️ HyperGrowth ♾ | 6 | +8.37% | 17.0% |
| Sifu | 4 | +6.71% | 13.7% |
| BredoStrategy | 1 | +5.78% | 11.8% |
| Scott Phillips Trading Vault | 2 | +2.42% | 4.9% |
| Hyperrr | 1 | +0.81% | 1.7% |
| FC Genesis - Quantum | 2 | -0.06% | -0.1% |
| Long HYPE & BTC / Short Garbage | 4 | -0.56% | -1.1% |
| Orbit Value Strategies | 2 | -0.63% | -1.3% |

Leaving vaults out (net excess over savings, per year):

| left out | in | out | t out |
|---|---:|---:|---:|
| drkmttr | -105.07% | +23.95% | 3.46 |
| Growi HF | -212.44% | +55.23% | 2.26 |
| [ Systemic Strategies ] ♾️ HyperGrowth ♾ | -105.07% | +56.48% | 2.36 |
| Sifu | -53.47% | +42.06% | 2.50 |
| BredoStrategy | -105.07% | +38.28% | 3.37 |
| without the top 3 together | -212.44% | +32.30% | 1.63 |

Conservative flow timing (deposits at the start of each step, withdrawals at its end):

| series | in: excess/yr | t | out: excess/yr | t | out Sharpe | worst month |
|---|---:|---:|---:|---:|---:|---:|
| chosen | -98.90% | -1.41 | +43.12% | 3.45 | 2.91 | -2.79% |
| market u100k cw | -98.47% | -2.10 | +35.36% | 3.06 | 2.70 | -1.98% |
| market u10k ew | -70.35% | -1.43 | -18.35% | -0.63 | -0.90 | -8.60% |

Follower check on the vaults that carry the test half (own P&L vs index):

| vault | tenure >= 60d: n, Spearman, median abs diff | 7-60d: n, Spearman, median abs diff |
|---|---|---|
| drkmttr | 23, 0.28, 39.5% | 53, 0.84, 7.1% |
| Growi HF | 31, 0.95, 2.6% | 15, 0.72, 0.5% |
| [ Systemic Strategies ] ♾️ HyperGrowth ♾ | 49, 0.94, 5.4% | 5, 0.60, 0.7% |
| Sifu | 11, 0.87, 0.4% | — |
| BredoStrategy | 7, 0.57, 135.5% | 24, 0.91, 5.8% |

The chosen rule over all the history available (2024-06-01 → 2026-09-01, 28 months): net excess -77.66% a year (t -1.55), 13 months positive.

Before the calendar (2024-06-01 → 2024-12-01, 7 months with >= 3 eligible vaults): mean monthly net excess -19.19%, worst month -82.90%, t -2.01; largest holdings Fried Chicken Enjoyooor, Sifu, outpxce [friendtech].

## Chosen variant, month by month

| month | eligible | held | gross | net | savings | matched BTC | selected equity | closed in month |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-01-01 | 14 | 1 | -11.52% | -11.52% | +0.47% | +1.68% | $10.80M | 0 |
| 2025-02-01 | 9 | 1 | -24.39% | -24.39% | +0.42% | -6.50% | $9.02M | 0 |
| 2025-03-01 | 14 | 1 | +73.98% | +71.53% | +0.47% | -8.70% | $9.68M | 0 |
| 2025-04-01 | 16 | 2 | -72.09% | -71.95% | +0.45% | +19.60% | $6.76M | 0 |
| 2025-05-01 | 13 | 1 | -1.43% | -1.43% | +0.47% | +7.96% | $5.02M | 0 |
| 2025-06-01 | 15 | 2 | -29.57% | -29.64% | +0.45% | +3.86% | $5.69M | 0 |
| 2025-07-01 | 17 | 2 | -10.84% | -11.03% | +0.47% | +13.30% | $4.60M | 0 |
| 2025-08-01 | 24 | 2 | +19.53% | +17.58% | +0.47% | -5.25% | $7.36M | 0 |
| 2025-09-01 | 28 | 3 | -0.98% | -1.06% | +0.45% | +7.25% | $8.40M | 0 |
| 2025-10-01 | 36 | 4 | -20.49% | -21.07% | +0.47% | -14.50% | $12.74M | 0 |
| 2025-11-01 | 33 | 3 | +1.26% | +1.68% | +0.45% | -9.78% | $13.17M | 0 |
| 2025-12-01 | 37 | 4 | +0.59% | +0.50% | +0.47% | -0.42% | $13.06M | 0 |
| 2026-01-01 | 38 | 4 | +10.17% | +9.49% | +0.31% | -20.96% | $12.79M | 0 |
| 2026-02-01 | 43 | 4 | -1.37% | -2.03% | +0.28% | -1.53% | $14.55M | 0 |
| 2026-03-01 | 41 | 4 | +3.52% | +3.26% | +0.31% | -6.16% | $12.60M | 0 |
| 2026-04-01 | 44 | 4 | +4.80% | +4.37% | +0.30% | +18.43% | $26.61M | 0 |
| 2026-05-01 | 48 | 5 | +3.03% | +2.52% | +0.31% | -21.49% | $31.68M | 0 |
| 2026-06-01 | 46 | 5 | +3.69% | +3.33% | +0.30% | -4.63% | $33.91M | 0 |
| 2026-07-01 | 55 | 6 | +6.66% | +5.97% | +0.31% | +6.88% | $36.66M | 0 |
| 2026-08-01 | 55 | 6 | +15.40% | +14.06% | +0.31% | +19.63% | $39.42M | 0 |
| 2026-09-01 | 59 | 6 | +1.42% | +1.24% | +0.30% | +10.13% | $47.00M | 0 |
