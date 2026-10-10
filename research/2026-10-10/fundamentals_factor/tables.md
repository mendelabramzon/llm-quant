# Fundamentals factor — tables

Generated 2026-10-10T12:56:31+00:00 from `analysis.json`. Weeks 2020-01-06 to 2026-09-28 (Mondays; each week earns Sunday close to Sunday close). Net = gross + funding − costs at 15bp a side on turnover (BTC hedge 6bp); $1 long and $1 short per $1 of capital; annualised with 52.18 weeks a year. SSR benchmark 3.80%.

## chains: 20 candidate variants, cutoff 2024-01-08 (in sample 2021-04-12 → 2024-01-08, out of sample → 2026-09-28)

Tokens ever tradable: 126.

| signal | hedge | names/wk | in: ann | in: Sharpe | out: ann | out: Sharpe | out: NW t | IC in | IC out | IC out t | turnover/wk | out: funding | out: cost | corr mom12 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| chain_composite | beta | 28.7 | -18.5% | -0.33 | +3.0% | 0.10 | 0.18 | 0.00 | 0.01 | 0.87 | 1.23 | -3.8% | +9.9% | 0.31 |
| chain_composite | dollar | 28.7 | -20.4% | -0.38 | +9.0% | 0.32 | 0.54 | 0.00 | 0.01 | 0.87 | 1.23 | -3.5% | +9.6% | 0.31 |
| dex_12w | beta | 28.2 | +1.0% | 0.01 | -3.1% | -0.11 | -0.19 | -0.01 | -0.00 | -0.27 | 0.88 | -1.9% | +7.1% | 0.31 |
| dex_12w | dollar | 28.2 | +5.3% | 0.07 | -2.9% | -0.09 | -0.17 | -0.01 | -0.00 | -0.27 | 0.88 | -1.4% | +6.9% | 0.31 |
| dex_4w | beta | 28.6 | -34.4% | -0.59 | -18.6% | -0.62 | -1.11 | -0.02 | -0.03 | -2.07 | 1.23 | +0.0% | +9.9% | 0.16 |
| dex_4w | dollar | 28.6 | -31.0% | -0.56 | -17.3% | -0.56 | -0.93 | -0.02 | -0.03 | -2.07 | 1.23 | +0.3% | +9.6% | 0.16 |
| fees_12w | beta | 19.8 | +40.1% | 1.11 | -17.7% | -0.46 | -0.84 | 0.02 | 0.01 | 0.82 | 0.90 | -1.1% | +7.4% | 0.29 |
| fees_12w | dollar | 19.8 | +47.5% | 1.22 | -13.2% | -0.34 | -0.61 | 0.02 | 0.01 | 0.82 | 0.90 | -0.9% | +7.1% | 0.29 |
| fees_4w | beta | 20.3 | +38.2% | 0.95 | -4.8% | -0.13 | -0.25 | 0.10 | 0.00 | 0.03 | 1.29 | -1.7% | +10.5% | 0.15 |
| fees_4w | dollar | 20.3 | +62.3% | 1.43 | -5.9% | -0.16 | -0.31 | 0.10 | 0.00 | 0.03 | 1.29 | -1.6% | +10.1% | 0.15 |
| stables_12w | beta | 26.5 | -9.2% | -0.20 | -9.6% | -0.26 | -0.50 | -0.00 | 0.03 | 2.02 | 0.83 | -2.9% | +6.7% | 0.18 |
| stables_12w | dollar | 26.5 | -24.8% | -0.50 | +0.9% | 0.02 | 0.05 | -0.00 | 0.03 | 2.02 | 0.83 | -2.8% | +6.5% | 0.18 |
| stables_4w | beta | 27.5 | -12.6% | -0.34 | +26.3% | 0.73 | 1.47 | 0.01 | 0.04 | 2.81 | 1.14 | -1.1% | +9.2% | 0.17 |
| stables_4w | dollar | 27.5 | -21.2% | -0.58 | +27.9% | 0.78 | 1.52 | 0.01 | 0.04 | 2.81 | 1.14 | -0.7% | +8.9% | 0.17 |
| stables_share_4w | beta | 27.5 | -44.4% | -1.38 | -1.8% | -0.05 | -0.11 | -0.01 | 0.02 | 1.31 | 1.04 | -1.1% | +8.5% | 0.12 |
| stables_share_4w | dollar | 27.5 | -47.1% | -1.42 | -0.5% | -0.02 | -0.03 | -0.01 | 0.02 | 1.31 | 1.04 | -1.1% | +8.2% | 0.12 |
| tvl_12w | beta | 30.6 | +44.5% | 0.84 | +14.5% | 0.49 | 0.83 | 0.01 | 0.01 | 0.80 | 0.81 | +0.0% | +6.6% | 0.44 |
| tvl_12w | dollar | 30.6 | +43.0% | 0.80 | +20.3% | 0.74 | 1.37 | 0.01 | 0.01 | 0.80 | 0.81 | -0.3% | +6.3% | 0.44 |
| tvl_4w | beta | 30.8 | +73.0% | 1.26 | +3.0% | 0.11 | 0.18 | 0.02 | 0.01 | 0.68 | 1.19 | -1.9% | +9.6% | 0.34 |
| tvl_4w | dollar | 30.8 | +74.5% | 1.27 | +12.2% | 0.45 | 0.81 | 0.02 | 0.01 | 0.68 | 1.19 | -2.1% | +9.3% | 0.34 |
| mom_12w (control) | beta | 56.4 | +15.7% | 0.27 | +16.5% | 0.37 | 0.61 | -0.02 | 0.02 | 0.81 | 0.99 | +3.5% | +8.1% | — |
| mom_12w (control) | dollar | 56.4 | +22.3% | 0.39 | +24.7% | 0.54 | 0.91 | -0.02 | 0.02 | 0.81 | 0.99 | +3.9% | +7.8% | — |
| mom_4w (control) | beta | 57.4 | +51.3% | 0.78 | +15.7% | 0.38 | 0.63 | -0.01 | -0.01 | -0.87 | 1.48 | +4.1% | +12.0% | — |
| mom_4w (control) | dollar | 57.4 | +59.6% | 0.90 | +20.5% | 0.49 | 0.83 | -0.01 | -0.01 | -0.87 | 1.48 | +4.4% | +11.6% | — |

**Chosen on the first half (best in-sample Sharpe): `fees_4w` / dollar.** In sample +62.3% a year (Sharpe 1.43, 38 weeks); out of sample -5.9% a year (Sharpe -0.16, NW t -0.31, 143 weeks; rank 15 of 20 by out-of-sample Sharpe). Deflated Sharpe of the in-sample choice: 0.42 given 20 family variants, 0.31 given every variant in the study. Out-of-sample net at 0/10/15/20/30bp a side: +4.1% / -2.6% / -5.9% / -9.3% / -16.0%. Break-even cost 6.2 bp a side. Placebo (signal shuffled within week, 200 reps): gross full-sample mean -0.2% (5–95%: -34.8% to +35.3%), gross out of sample -0.8% (5–95%: -33.0% to +32.1%), net -22.3% (it churns the book weekly); the real gross sits at the 81% percentile in full and 63% out of sample. Drop-one-token range out of sample: -16.1% to +2.9%. Against the same-hedge 12-week momentum book: beta 0.08, correlation 0.09, alpha +6.2% a year (NW t 0.30).

Best out of sample with hindsight (not a test): `stables_4w` / dollar, +27.9% a year (NW t 1.52; in sample -21.2%); rank IC out of sample 0.04 (t 2.81). Without its top three contributors (hedera-hashgraph, arbitrum, cardano) +5.5%; by half-year 2024H1 +55.2%, 2024H2 +23.3%, 2025H1 +37.1%, 2025H2 +78.0%, 2026H1 -22.1%, 2026H2 -33.5%.

### Rank IC by year (signal vs next-week return)

| signal | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|
| stables_4w | — | — | 0.09 | -0.03 | 0.03 | 0.08 | -0.00 |
| stables_12w | — | — | 0.12 | -0.07 | 0.03 | 0.05 | 0.01 |
| stables_share_4w | — | — | 0.05 | -0.04 | -0.01 | 0.05 | 0.00 |
| dex_4w | — | -0.06 | -0.04 | 0.01 | -0.04 | -0.02 | -0.01 |
| dex_12w | — | -0.04 | -0.01 | -0.01 | 0.00 | -0.00 | -0.01 |
| fees_4w | — | — | — | 0.10 | -0.01 | 0.01 | 0.01 |
| fees_12w | — | — | — | 0.02 | 0.03 | -0.00 | 0.02 |
| tvl_4w | — | 0.02 | 0.03 | 0.01 | -0.03 | 0.03 | 0.05 |
| tvl_12w | — | 0.01 | 0.02 | 0.00 | -0.02 | 0.02 | 0.05 |
| chain_composite | — | 0.02 | -0.00 | -0.00 | -0.04 | 0.04 | 0.05 |
| mom_4w | 0.07 | -0.06 | 0.01 | -0.05 | -0.04 | 0.03 | -0.04 |
| mom_12w | 0.09 | -0.07 | -0.03 | -0.02 | -0.02 | 0.06 | 0.01 |

### Walk-forward (choose on 104 weeks, hold 26)

| test from | chosen | train Sharpe | test ann | weeks |
|---|---|---:|---:|---:|
| 2023-04-10 | tvl_4w/dollar | 1.27 | -3.5% | 26 |
| 2023-10-09 | tvl_4w/beta | 0.51 | +77.6% | 26 |
| 2024-04-08 | fees_12w/dollar | 1.97 | -33.0% | 26 |
| 2024-10-07 | fees_12w/dollar | 1.08 | +42.4% | 26 |
| 2025-04-07 | tvl_12w/dollar | 1.43 | -4.9% | 26 |
| 2025-10-06 | tvl_12w/dollar | 1.22 | +26.2% | 26 |
| 2026-04-06 | stables_4w/beta | 1.04 | -18.2% | 26 |

Walk-forward concatenated: +12.4% a year, Sharpe 0.33, NW t 0.73 over 182 weeks.

Live books (2026-10-10T11:47:27+00:00): median cost per side including the 5bp taker fee, $1000k 55.0bp, $100k 37.4bp, $250k 69.7bp, $25k 18.9bp; median half-spread 0.86 bp, over 73 names.

## protocols: 14 candidate variants, cutoff 2024-01-22 (in sample 2021-05-03 → 2024-01-22, out of sample → 2026-09-28)

Tokens ever tradable: 245.

| signal | hedge | names/wk | in: ann | in: Sharpe | out: ann | out: Sharpe | out: NW t | IC in | IC out | IC out t | turnover/wk | out: funding | out: cost | corr mom12 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pfees_12w | beta | 26.7 | +87.8% | 1.36 | +2.3% | 0.06 | 0.07 | 0.06 | 0.01 | 0.61 | 1.02 | -5.4% | +8.3% | 0.22 |
| pfees_12w | dollar | 26.7 | +85.1% | 1.32 | +0.4% | 0.01 | 0.01 | 0.06 | 0.01 | 0.61 | 1.02 | -5.6% | +8.0% | 0.22 |
| pfees_4w | beta | 27.3 | +44.9% | 0.74 | -16.5% | -0.44 | -0.58 | 0.04 | -0.00 | -0.29 | 1.39 | +0.4% | +11.2% | 0.14 |
| pfees_4w | dollar | 27.3 | +42.7% | 0.71 | -15.0% | -0.41 | -0.56 | 0.04 | -0.00 | -0.29 | 1.39 | +0.3% | +10.8% | 0.14 |
| pfees_fdv | beta | 27.4 | +52.8% | 0.66 | -9.9% | -0.24 | -0.38 | 0.07 | -0.01 | -0.65 | 0.70 | +4.1% | +5.7% | -0.03 |
| pfees_fdv | dollar | 27.4 | +56.3% | 0.71 | -8.1% | -0.19 | -0.34 | 0.07 | -0.01 | -0.65 | 0.70 | +4.3% | +5.4% | -0.03 |
| prev_12w | beta | 25.5 | +18.0% | 0.40 | +20.1% | 0.47 | 0.66 | 0.03 | 0.01 | 0.69 | 1.05 | -2.1% | +8.5% | 0.21 |
| prev_12w | dollar | 25.5 | +23.7% | 0.52 | +17.3% | 0.41 | 0.58 | 0.03 | 0.01 | 0.69 | 1.05 | -2.3% | +8.2% | 0.21 |
| prev_4w | beta | 26.0 | -19.8% | -0.42 | +10.7% | 0.24 | 0.35 | -0.00 | 0.01 | 0.52 | 1.40 | -0.2% | +11.3% | 0.14 |
| prev_4w | dollar | 26.0 | -16.0% | -0.34 | +13.1% | 0.30 | 0.46 | -0.00 | 0.01 | 0.52 | 1.40 | -0.3% | +10.9% | 0.14 |
| prev_fdv | beta | 26.7 | -3.6% | -0.07 | -12.7% | -0.29 | -0.51 | 0.03 | 0.01 | 0.56 | 0.75 | -3.7% | +6.1% | -0.09 |
| prev_fdv | dollar | 26.7 | +6.2% | 0.13 | -20.0% | -0.45 | -0.88 | 0.03 | 0.01 | 0.56 | 0.75 | -3.1% | +5.9% | -0.09 |
| protocol_composite | beta | 27.3 | +63.6% | 1.14 | -28.1% | -0.85 | -1.40 | 0.05 | -0.01 | -0.71 | 1.34 | +0.1% | +10.8% | 0.11 |
| protocol_composite | dollar | 27.3 | +63.0% | 1.15 | -26.0% | -0.75 | -1.22 | 0.05 | -0.01 | -0.71 | 1.34 | +0.1% | +10.5% | 0.11 |
| mom_12w (control) | beta | 70.8 | -37.3% | -0.67 | -4.4% | -0.10 | -0.17 | -0.06 | -0.02 | -1.56 | 1.06 | +11.1% | +8.6% | — |
| mom_12w (control) | dollar | 70.8 | -36.6% | -0.66 | +5.3% | 0.12 | 0.21 | -0.06 | -0.02 | -1.56 | 1.06 | +11.1% | +8.3% | — |
| mom_4w (control) | beta | 73.9 | +15.8% | 0.29 | +3.5% | 0.09 | 0.15 | -0.05 | -0.02 | -1.89 | 1.56 | +15.4% | +12.6% | — |
| mom_4w (control) | dollar | 73.9 | +3.7% | 0.07 | +12.6% | 0.30 | 0.54 | -0.05 | -0.02 | -1.89 | 1.56 | +15.1% | +12.2% | — |

**Chosen on the first half (best in-sample Sharpe): `pfees_12w` / beta.** In sample +87.8% a year (Sharpe 1.36, 142 weeks); out of sample +2.3% a year (Sharpe 0.06, NW t 0.07, 141 weeks; rank 5 of 14 by out-of-sample Sharpe). Deflated Sharpe of the in-sample choice: 0.78 given 14 family variants, 0.57 given every variant in the study. Out-of-sample net at 0/10/15/20/30bp a side: +10.2% / +4.9% / +2.3% / -0.4% / -5.7%. Break-even cost 19.9 bp a side. Placebo (signal shuffled within week, 200 reps): gross full-sample mean +2.8% (5–95%: -34.7% to +40.6%), gross out of sample +1.1% (5–95%: -35.1% to +38.5%), net -20.1% (it churns the book weekly); the real gross sits at the 100% percentile in full and 70% out of sample. Drop-one-token range out of sample: -8.7% to +11.0%. Against the same-hedge 12-week momentum book: beta 0.27, correlation 0.21, alpha +52.7% a year (NW t 1.76).

Best out of sample with hindsight (not a test): `prev_12w` / beta, +20.1% a year (NW t 0.66; in sample +18.0%); rank IC out of sample 0.01 (t 0.69). Without its top three contributors (bitway, jito-governance-token, venice-token) +9.6%; by half-year 2024H1 +53.2%, 2024H2 -130.1%, 2025H1 -1.0%, 2025H2 +14.8%, 2026H1 +56.1%, 2026H2 +254.2%.

### Rank IC by year (signal vs next-week return)

| signal | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---:|---:|---:|---:|---:|---:|---:|
| pfees_4w | — | 0.11 | -0.01 | 0.05 | -0.03 | -0.03 | 0.06 |
| pfees_12w | — | 0.11 | 0.05 | 0.04 | -0.01 | -0.02 | 0.07 |
| prev_4w | — | 0.09 | -0.04 | 0.03 | -0.03 | 0.00 | 0.06 |
| prev_12w | — | 0.02 | 0.03 | 0.05 | -0.02 | -0.00 | 0.06 |
| pfees_fdv | — | 0.12 | 0.08 | 0.06 | -0.00 | -0.02 | -0.02 |
| prev_fdv | — | — | 0.04 | 0.02 | 0.01 | -0.01 | 0.03 |
| protocol_composite | — | 0.11 | 0.01 | 0.06 | -0.03 | -0.02 | 0.03 |
| mom_4w | 0.08 | -0.04 | -0.05 | -0.08 | -0.05 | -0.02 | 0.00 |
| mom_12w | 0.20 | -0.06 | -0.08 | -0.08 | -0.05 | -0.03 | 0.02 |

### Walk-forward (choose on 104 weeks, hold 26)

| test from | chosen | train Sharpe | test ann | weeks |
|---|---|---:|---:|---:|
| 2023-05-01 | pfees_12w/beta | 1.42 | +137.8% | 26 |
| 2023-10-30 | pfees_12w/beta | 1.14 | -37.7% | 26 |
| 2024-04-29 | pfees_12w/beta | 1.49 | +8.2% | 26 |
| 2024-10-28 | pfees_12w/dollar | 1.05 | -130.3% | 26 |
| 2025-04-28 | prev_4w/dollar | 0.82 | -87.8% | 26 |
| 2025-10-27 | pfees_fdv/beta | -0.17 | +77.6% | 26 |

Walk-forward concatenated: -5.4% a year, Sharpe -0.13, NW t -0.20 over 156 weeks.

Live books (2026-10-10T11:47:27+00:00): median cost per side including the 5bp taker fee, $1000k 172.5bp, $100k 55.2bp, $250k 99.8bp, $25k 23.3bp; median half-spread 1.38 bp, over 94 names.

Benjamini–Hochberg at q = 0.10 over the rank IC of 17 signals (in sample): survivors none.
Benjamini–Hochberg at q = 0.10 over the rank IC of 17 signals (out sample): survivors ['chains:stables_4w'].
Benjamini–Hochberg at q = 0.10 over 34 candidate variants (full): survivors none; smallest adjusted p 0.89.
Benjamini–Hochberg at q = 0.10 over 34 candidate variants (out of sample): survivors none; smallest adjusted p 0.99.

## The framework's "new activity", replayed: 1792 events on 100 tokens (dex_surge 801, fees_surge 445, stable_inflow 434, tvl_surge 112)

long the token perp from the close of D+1 to the close of D+1+h (D the data day), hedged with the same notional of BTC or of an equal-weight basket of the other liquid chain tokens; costs 15bp a side on the token, 6bp on BTC, 15bp on the basket; placebo: the same token 45 days either side, skipped within 14 days of a same-type event; chosen on the in-sample event-day t of the P&L; cutoff 2024-01-08.

| event | days | hedge | n in | mean in | by-day t in | placebo in | n out | mean out | by-day t out | placebo out | excess t out | hit out | abnormal out | BH adj p out |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dex_surge | 7 | btc | 224 | +0.15% | 1.00 | -0.53% | 389 | -0.70% | -1.29 | -2.43% | 1.82 | 36% | -0.57% | 0.40 |
| dex_surge | 7 | basket | 223 | -0.55% | 0.09 | -1.07% | 389 | -0.84% | -1.28 | -0.85% | 0.02 | 35% | -0.38% | 0.40 |
| dex_surge | 28 | btc | 224 | +3.54% | 1.89 | -2.40% | 378 | -0.78% | -0.93 | -8.89% | 4.04 | 35% | -1.15% | 0.48 |
| dex_surge | 28 | basket | 223 | +0.75% | 0.66 | -3.94% | 378 | -0.67% | -0.50 | -2.98% | 1.39 | 39% | -0.29% | 0.70 |
| fees_surge | 7 | btc | 88 | +1.07% | 0.69 | -0.89% | 261 | -1.39% | -1.98 | -1.53% | 0.15 | 37% | -1.40% | 0.15 |
| fees_surge | 7 | basket | 87 | +0.38% | 0.31 | -1.54% | 261 | -1.29% | -2.43 | -0.83% | -0.59 | 37% | -1.00% | 0.08 |
| fees_surge | 28 | btc | 88 | +2.91% | 0.85 | -0.06% | 251 | -1.57% | -0.92 | -4.86% | 1.68 | 34% | -1.98% | 0.48 |
| fees_surge | 28 | basket | 87 | -0.37% | -0.27 | -0.76% | 251 | -0.44% | -0.21 | -1.56% | 0.65 | 39% | -0.17% | 0.83 |
| tvl_surge | 7 | btc | 39 | +3.08% | 0.81 | -0.52% | 33 | -1.25% | -0.61 | -3.10% | 0.79 | 36% | -0.85% | 0.67 |
| tvl_surge | 7 | basket | 39 | +0.15% | -0.06 | -1.83% | 33 | -2.86% | -2.44 | -1.21% | -1.12 | 36% | -2.09% | 0.08 |
| tvl_surge | 28 | btc | 39 | +11.49% | 1.80 | +11.26% | 32 | -8.95% | -2.04 | -6.27% | -0.47 | 19% | -8.57% | 0.15 |
| tvl_surge | 28 | basket | 39 | +0.93% | 0.16 | +1.15% | 32 | -3.30% | -1.02 | -1.24% | -0.46 | 28% | -2.00% | 0.48 |
| stable_inflow | 7 | btc | 80 | +3.30% | 1.25 | -0.35% | 255 | -1.42% | -1.49 | -1.48% | 0.06 | 31% | -1.19% | 0.36 |
| stable_inflow | 7 | basket | 79 | -0.11% | -0.10 | -0.40% | 255 | -1.06% | -1.01 | -0.90% | -0.18 | 36% | -0.53% | 0.48 |
| stable_inflow | 28 | btc | 80 | +7.77% | 1.49 | +20.53% | 246 | -4.39% | -2.64 | -4.87% | 0.26 | 32% | -4.57% | 0.08 |
| stable_inflow | 28 | basket | 79 | -1.50% | -0.17 | +13.33% | 246 | -1.67% | -0.32 | -0.48% | -0.69 | 40% | -1.20% | 0.80 |

Chosen in sample (highest event-day t of the P&L): dex_surge over 28 days against btc — in +3.54% a trade (by-day t 1.89; placebo -2.40%); out of sample -0.78% (by-day t -0.93; placebo -8.89%, excess t 4.04).

## Anecdotes (not evidence)

| event | data day | token | since the data day close | vs BTC | since entry (close of D+1) | vs BTC | note |
|---|---|---|---:|---:|---:|---:|---|
| Starknet DEX volume x3.6 (first reading) | 2026-10-08 | binance:STRKUSDT | +28.1% | +26.7% | -2.5% | -2.9% |  |
| Starknet DEX volume x4.1 (second day) | 2026-10-09 | binance:STRKUSDT | -2.5% | -2.9% | — | — | entry close (2026-10-10) not yet printed when the books were read |
| TON DEX volume x3.6 | 2026-10-09 | hl:GRAM | -0.5% | -0.8% | — | — | entry close (2026-10-10) not yet printed when the books were read |
| Cronos transactions x2.6, memecoin wave | 2026-10-08 | crypto-com-chain | — | — | — | — | no perp in the universe |
| Plasma stablecoins +$396M in 30 days | 2026-10-08 | binance:XPLUSDT | +3.8% | +2.4% | +2.7% | +2.3% |  |
| XRPL stablecoins +$215M in 7 days | 2026-10-08 | binance:XRPUSDT | +1.8% | +0.4% | +0.7% | +0.3% |  |
| X Layer USDC x7 in a week | 2026-10-08 | okb | — | — | — | — | no perp in the universe |
| Tempo stablecoins +$678M in 30 days (no token) | 2026-10-08 | — | — | — | — | — | no token |
| Arc stablecoins +$110M in 7 days (gas token is USDC) | 2026-10-08 | — | — | — | — | — | no token |
