# Altcoin floor carry: a basket of spot-long / same-venue perp-short positions chosen by trailing floor persistence (computed 2026-10-11T08:28:39+00:00)

Question: does a diversified, collateral-efficient basket of altcoin spot-long / same-venue perp-short positions, chosen by trailing floor persistence, beat the savings rate out of sample after negative funding spikes, basis moves, costs and realistic capacity, and how much capital can it hold?

The rule family was written to analysis.json at 2026-10-11T03:50:52+00:00, before any return was computed: `{"floor_share_min": [0.5, 0.75], "n_names": [10, 30], "rebalance_days": [7, 28], "spike_8h": [null, -0.0005], "spot_vol_min_usd": [2000000.0, 10000000.0]}`; rank: trailing-30d floor share (desc), then trailing-30d funding APR (desc), then spot 30d median quote volume (desc); 32 variants. Baseline: top-N by floor share with no floor threshold and no spike screen (spot volume >= $2M).

## Binance

**Verdict: the chosen variant FAILS the go rule** (in-sample positive, out-of-sample HAC t > 2, a BH survivor, out-of-sample excess positive at $3M): bh_survivor=False, in_sample_positive=False, oos_positive_at_3m=False, oos_t_gt_2=False.

Excess is over the savings rate paid each day (DSR, then the SSR; mean 6.48% in sample, 3.82% out of sample; term_carry.load_navs), on the capital the trade ties up (K = 1 + max(0, im + 0.5 - 1.5c), c = today's collateral ratio; median K 1.45, c quartiles [0.1, 0.1, 0.3]). Costs: taker fees spot 10bp / perp 5bp per side, half-spread from today's book tickers (75th percentile by volume bucket, floored at half a tick), double costs on forced exits. P&L window 2024-10-01..2026-10-10, split at 2025-10-06 (370 / 370 days).

### Data coverage

| item | value |
|---|---|
| USDT-margined coin perps found (listed any status + funding history) | 667 |
| by status today | {"PENDING_TRADING": 1, "SETTLING": 133, "TRADING": 525, "absent_from_exchangeInfo": 8} |
| symbols with funding history since 2024-09-01 | 929 |
| perps with a traded daily bar in the window | 649 |
| excluded (BTC, ETH, stables, gold, indices) | 7 |
| no same-coin spot pair on the venue | 209 |
|   no spot market (no data under any candidate name) | 206 |
|   spot overlap under 30 days | 3 |
|   a spot pair of the same name is another coin (rejected) | None |
| coins with both legs (the all-spot universe) | 433 |
| of which collateral today (main universe) | 354 |
| coins with a leg delisted in the window | 73 |
|   perp delisted | 73 |
|   spot delisted | 71 |
| perps with no traded bar in the window that still print settlements in it (dropped entirely) | 18 |
|   their settlements in the window | 21321 |
| settlements fetched (the perps above with a traded bar) | 1848034 |
| settlements kept | 1817551 |
| dropped: funding day without a traded perp bar, or after delivery | 30483 |
|   stamped after the last traded perp bar (phantom prints) | 22659 |
|   before the first traded bar (paging overshoot before the window, pre-market funding) | 7615 |
| collateral assets on 2026-10-11 | 488 |

Main universe at the 7-day rebalances: eligible names median 298 (min 193, max 354); at the floor on >= 50% of trailing settlements median 183; with spot volume >= $2M median 52, >= $10M median 10.

### Does floor persistence persist? (eligible coins at every 7-day rebalance, next 28 days)

| universe | trailing floor share | coin-dates | trailing APR | next floor share | next APR mean | next APR median | next APR p10 | next 28d has a spike < -0.05%/8h |
|---|---|---|---|---|---|---|---|---|
| main | [0.00, 0.25) | 4853 | -59.33% | 26% | -29.62% | -4.81% | -80.92% | 58% |
| main | [0.25, 0.50) | 6619 | -17.34% | 47% | -14.54% | +2.03% | -42.17% | 50% |
| main | [0.50, 0.75) | 8916 | -0.80% | 63% | -8.29% | +5.66% | -25.42% | 46% |
| main | [0.75, 0.90) | 5794 | +5.84% | 73% | -2.94% | +7.73% | -15.26% | 42% |
| main | [0.90, 1.00) | 3650 | +9.79% | 83% | +1.26% | +9.86% | -8.08% | 32% |
| main_spike_screened | [0.00, 0.25) | 1645 | -0.12% | 24% | -0.96% | +1.73% | -5.99% | 15% |
| main_spike_screened | [0.25, 0.50) | 2868 | +6.06% | 46% | +1.69% | +4.52% | -4.18% | 18% |
| main_spike_screened | [0.50, 0.75) | 4370 | +8.36% | 63% | +2.14% | +6.91% | -2.95% | 24% |
| main_spike_screened | [0.75, 0.90) | 3412 | +9.23% | 72% | +1.69% | +8.21% | -3.47% | 30% |
| main_spike_screened | [0.90, 1.00) | 2967 | +10.54% | 83% | +2.95% | +10.02% | -2.28% | 28% |
| main_v10m_spike_screened | [0.00, 0.25) | 843 | +0.85% | 21% | +0.97% | +1.82% | -5.20% | 10% |
| main_v10m_spike_screened | [0.25, 0.50) | 1145 | +8.88% | 46% | +4.58% | +5.14% | -2.50% | 12% |
| main_v10m_spike_screened | [0.50, 0.75) | 1192 | +10.58% | 57% | +7.26% | +7.24% | +0.23% | 15% |
| main_v10m_spike_screened | [0.75, 0.90) | 440 | +9.90% | 61% | +9.29% | +8.26% | +1.33% | 23% |
| main_v10m_spike_screened | [0.90, 1.00) | 161 | +10.76% | 66% | +10.07% | +8.89% | +2.18% | 22% |
| all_spot | [0.00, 0.25) | 5026 | -60.89% | 26% | -29.73% | -4.99% | -81.76% | 59% |
| all_spot | [0.25, 0.50) | 7152 | -17.61% | 47% | -14.72% | +2.03% | -44.08% | 50% |
| all_spot | [0.50, 0.75) | 10124 | -0.93% | 63% | -8.34% | +5.73% | -26.44% | 47% |
| all_spot | [0.75, 0.90) | 7061 | +5.49% | 74% | -2.85% | +7.78% | -15.03% | 43% |
| all_spot | [0.90, 1.00) | 4907 | +9.70% | 84% | +1.84% | +9.92% | -5.43% | 31% |

### Protocol: choose on the first half, test once on the second

| chosen | in-sample excess | IS Sharpe | in_sample_positive | OOS excess | OOS Sharpe | OOS HAC t | OOS t (30 lags) | OOS rank | deflated Sharpe (IS, 32 trials) | BH survivors (q=0.10, full sample, one-sided: mean > 0) |
|---|---|---|---|---|---|---|---|---|---|---|
| R28_F75_Sm5bp_V10M_N30 | -0.65% | -1.46 | False | -0.14% | -2.00 | -2.30 | -1.86 | 1/32 | 0.000 | 0 |

backtest.choose_then_test's own BH (two-sided p) would list 31 "survivors" here; 31 of them have a negative full-sample mean, i.e. they are significant losers.

Chosen variant: full sample -0.39% (t -1.45); deflated Sharpe full 0.000, OOS 0.000; OOS mean daily excess, 28-day block bootstrap 95% interval -0.31%..-0.02% a year.

### All variants (main universe, small size), by in-sample excess

| variant | full | in sample | OOS | OOS t | BH adj p | names held | invested | turnover/yr | forced exits | neg. funding/yr |
|---|---|---|---|---|---|---|---|---|---|---|
| R28_F75_Sm5bp_V10M_N30 (chosen) | -0.39% | -0.65% | -0.14% | -2.30 | 1.000 | 4.3 | 14% | 280% | 0 | 0.16% |
| R28_F75_Snone_V10M_N30 | -0.49% | -0.79% | -0.20% | -2.39 | 1.000 | 5.3 | 18% | 321% | 0 | 0.27% |
| R28_F75_Sm5bp_V10M_N10 | -0.72% | -1.02% | -0.41% | -2.30 | 1.000 | 2.7 | 27% | 504% | 0 | 0.33% |
| R28_F75_Snone_V10M_N10 | -1.09% | -1.59% | -0.59% | -2.39 | 1.000 | 3.3 | 33% | 578% | 0 | 0.63% |
| R28_F50_Sm5bp_V10M_N30 | -1.22% | -1.62% | -0.82% | -2.42 | 1.000 | 12.5 | 42% | 644% | 0 | 0.78% |
| R7_F75_Sm5bp_V10M_N30 | -0.96% | -1.73% | -0.18% | -2.69 | 1.000 | 4.9 | 16% | 564% | 0 | 0.17% |
| R7_F75_Snone_V10M_N30 | -1.31% | -2.30% | -0.31% | -2.82 | 1.000 | 6.0 | 20% | 671% | 0 | 0.37% |
| R7_F50_Sm5bp_V10M_N30 | -1.74% | -2.67% | -0.82% | -2.37 | 1.000 | 12.0 | 40% | 1101% | 0 | 0.58% |
| R28_F75_Sm5bp_V2M_N30 | -2.06% | -2.87% | -1.24% | -3.16 | 1.000 | 13.4 | 45% | 654% | 0 | 1.54% |
| R28_F50_Snone_V10M_N30 | -2.13% | -2.87% | -1.39% | -3.18 | 1.000 | 15.1 | 50% | 724% | 0 | 1.62% |
| R28_F50_Sm5bp_V10M_N10 | -2.17% | -2.98% | -1.35% | -2.63 | 1.000 | 6.0 | 60% | 1083% | 0 | 1.22% |
| R7_F75_Sm5bp_V10M_N10 | -1.88% | -3.21% | -0.55% | -2.69 | 1.000 | 2.8 | 28% | 1137% | 0 | 0.36% |
| R28_F75_Snone_V2M_N30 | -2.95% | -3.55% | -2.36% | -4.63 | 1.000 | 16.6 | 55% | 759% | 0 | 2.33% |
| R28_F75_Snone_V2M_N10 | -3.60% | -3.90% | -3.31% | -3.66 | 1.000 | 8.1 | 81% | 1180% | 0 | 2.85% |
| R28_F50_Snone_V2M_N10 | -6.58% | -4.43% | -8.73% | -3.68 | 1.000 | 10.0 | 100% | 1407% | 0 | 5.74% |
| R28_F50_Snone_V10M_N10 | -3.33% | -4.47% | -2.18% | -3.44 | 1.000 | 7.1 | 71% | 1216% | 0 | 2.34% |
| R7_F75_Sm5bp_V2M_N30 | -2.75% | -4.49% | -1.02% | -3.82 | 1.000 | 13.6 | 45% | 1289% | 0 | 0.96% |
| R7_F75_Snone_V10M_N10 | -2.75% | -4.55% | -0.94% | -2.82 | 1.000 | 3.4 | 34% | 1314% | 0 | 0.88% |
| R7_F50_Snone_V10M_N30 | -3.60% | -4.83% | -2.36% | -3.62 | 1.000 | 14.7 | 49% | 1328% | 0 | 2.08% |
| R28_F50_Sm5bp_V2M_N30 | -4.10% | -4.93% | -3.26% | -3.92 | 1.000 | 22.1 | 74% | 1041% | 0 | 3.14% |
| R28_F75_Sm5bp_V2M_N10 | -4.14% | -5.25% | -3.03% | -3.41 | 1.000 | 7.0 | 70% | 1061% | 0 | 3.36% |
| R7_F50_Sm5bp_V10M_N10 | -3.43% | -5.33% | -1.53% | -3.14 | 1.000 | 5.8 | 58% | 2003% | 0 | 0.95% |
| R28_F50_Snone_V2M_N30 | -5.90% | -5.85% | -5.96% | -6.05 | 1.000 | 25.8 | 86% | 1145% | 0 | 4.94% |
| R7_F75_Snone_V2M_N30 | -4.45% | -5.99% | -2.91% | -5.26 | 1.000 | 16.8 | 56% | 1475% | 0 | 2.43% |
| R28_F50_Sm5bp_V2M_N10 | -6.12% | -6.02% | -6.21% | -3.08 | 1.000 | 9.5 | 95% | 1386% | 0 | 5.21% |
| R7_F50_Sm5bp_V2M_N30 | -4.63% | -6.95% | -2.32% | -5.21 | 1.000 | 22.4 | 75% | 1964% | 0 | 2.00% |
| R7_F75_Sm5bp_V2M_N10 | -5.08% | -7.79% | -2.36% | -4.79 | 1.000 | 7.4 | 74% | 2188% | 0 | 2.20% |
| R7_F50_Snone_V10M_N10 | -6.54% | -7.98% | -5.10% | -3.25 | 1.000 | 7.0 | 70% | 2350% | 0 | 3.54% |
| R7_F50_Snone_V2M_N30 | -7.66% | -8.07% | -7.26% | -8.45 | 1.000 | 25.8 | 86% | 2128% | 0 | 4.86% |
| R7_F50_Sm5bp_V2M_N10 | -6.09% | -8.85% | -3.32% | -5.51 | 1.000 | 9.6 | 96% | 2690% | 0 | 2.69% |
| R7_F75_Snone_V2M_N10 | -7.67% | -9.90% | -5.45% | -4.12 | 1.000 | 8.4 | 84% | 2417% | 0 | 4.59% |
| R7_F50_Snone_V2M_N10 | -10.21% | -10.48% | -9.93% | -4.47 | 1.000 | 10.0 | 100% | 2759% | 0 | 6.98% |

### Chosen variant: where the P&L came from, and its tail

| funding/yr | of which at the floor | basis/yr | costs/yr | savings rate on invested/yr | excess/yr | turnover/yr | names held | invested |
|---|---|---|---|---|---|---|---|---|
| +1.24% | 60% | -0.04% | -0.53% | -1.06% | -0.39% | 280% | 4.3 | 14% |

| worst rolling week | worst calendar week | max drawdown | best 1% of days: share of excess (of gross) | negative settlements paid/yr (share of positive funding) | forced exits (delisting/gap) | rally rebalances |
|---|---|---|---|---|---|---|
| -0.24% from 2025-02-12 | -0.22% (2025-W06) | 1.2% | - (46%) | 0.2% (12%) | 0 (0/0) | 20 |

By year: 2024 +1.24% (92d), 2025 -1.07% (365d), 2026 -0.06% (283d). By half-year: 2024H2 +1.24%, 2025H1 -1.82%, 2025H2 -0.32%, 2026H1 -0.03%, 2026H2 -0.10%.

Best coins (P&L in capital units over the window, before the benchmark): CRVUSDT +0.11%, ETHFIUSDT +0.09%, NEIROUSDT +0.07%, 1000SATSUSDT +0.07%, TAOUSDT +0.06%, DYDXUSDT +0.06%, 1000BONKUSDT +0.05%, WLDUSDT +0.05%. Worst: PLUMEUSDT -0.02%, RAYSOLUSDT -0.00%, AIXBTUSDT -0.00%, XLMUSDT -0.00%, TRUMPUSDT -0.00%, 币安人生USDT -0.00%, IOUSDT -0.00%, 1MBABYDOGEUSDT -0.00%.

Last book (2026-09-29): XLMUSDT (floor 76%, spot vol $16.73M, c 0.50), ASTERUSDT (floor 78%, spot vol $12.71M, c 0.50).

### Baseline: always the top N by floor share

| baseline | full | in sample | OOS | OOS t | excess per $ deployed | worst week | max drawdown | neg. funding/yr | turnover/yr | names held |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline_R28_F0_Snone_V2M_N10 | -6.58% | -4.43% | -8.73% | -3.68 | -6.58% | -2.20% | 13.5% | 5.7% | 1407% | 10.0 |
| baseline_R28_F0_Snone_V2M_N30 | -7.30% | -5.85% | -8.75% | -6.64 | -7.30% | -0.99% | 15.2% | 6.2% | 1294% | 30.0 |

### Robustness

| run | full | in sample | OOS | OOS t |
|---|---|---|---|---|
| all-spot universe (delisted included, c = 0.10 for every coin): its own chosen R28_F75_Sm5bp_V10M_N30 | - | -1.00% | -0.14% | -2.56 |
| all-spot universe, the main chosen variant | -0.57% | -1.00% | -0.14% | -2.56 |
| main universe at the assumed ratio (bridge) | -0.51% | -0.88% | -0.14% | -2.56 |
| fees and spreads x2 | -0.93% | -1.61% | -0.25% | -2.64 |
| constant 3.80% benchmark | +0.12% | +0.35% | -0.12% | -2.19 |
| late entry: signal one day stale | -0.39% | -0.59% | -0.18% | -2.21 |

All-spot universe: BH survivors 0; in_sample_positive False; forced exits of the main chosen variant there 0 (none).

### Post hoc (computed after the protocol; selects nothing)

| run | full | in sample | OOS | OOS t |
|---|---|---|---|---|
| chosen, excess per $ actually deployed | -2.71% | -2.50% | -4.42% | - |
| chosen at zero fees and spreads | +0.14% | +0.31% | -0.03% | -0.61 |
| chosen at zero cost, per $ deployed | - | +1.20% | -0.88% | - |
| broad R28_F50_Sm5bp_V2M_N30 (costed) | -4.10% | -4.93% | -3.26% | -3.92 |
| broad, per $ deployed | - | -5.10% | -6.48% | - |
| broad at zero fees and spreads | -1.80% | -1.98% | -1.63% | -2.11 |

| P&L per year of capital deployed | funding | of which negative settlements | basis | costs | savings rate | invested |
|---|---|---|---|---|---|---|
| chosen, in sample | +9.19% | -0.99% | -0.31% | -3.71% | -7.67% | 26% |
| chosen, out of sample | +3.38% | -2.24% | -0.02% | -3.53% | -4.25% | 3% |
| broad, in sample | +4.65% | -3.40% | -0.15% | -3.05% | -6.55% | 97% |
| broad, out of sample | +0.58% | -5.94% | +0.11% | -3.24% | -3.93% | 50% |

Names kept from one rebalance to the next: chosen 14%, broad 40%.

Broad variant, whole window per year of capital: funding +2.40% (negative settlements -3.14%), basis -0.04%, costs -2.29%, savings rate on invested -4.16%; turnover 1041%; invested 97% in sample, 50% out of sample; worst week -0.91%, max drawdown 8.6%.

### Capacity (chosen variant; each name <= 2% of its 30-day median daily spot and perp volume, built and unwound over 3 days, square-root impact Y = 0.5, stress Y = 1)

| capital | excess full | excess OOS | OOS t | $/yr OOS | invested (OOS) | names capped | impact/yr | stress Y=1 OOS | cap only OOS | impact only OOS | baseline OOS | one-day crash unwind (median / worst) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $1.00M | -0.65% | -0.20% | -2.44 | -$2k | 14% (3%) | 0% | -0.26% | -0.26% | -0.14% | -0.20% | -11.39% | 0.0% / 1.0% |
| $3.00M | -0.84% | -0.24% | -2.44 | -$7k | 14% (3%) | 0% | -0.45% | -0.34% | -0.14% | -0.24% | -10.99% | 0.1% / 1.6% |
| $5.00M | -0.97% | -0.27% | -2.43 | -$14k | 14% (3%) | 0% | -0.58% | -0.40% | -0.14% | -0.27% | -8.97% | 0.1% / 2.1% |
| $10.00M | -1.11% | -0.30% | -2.40 | -$30k | 14% (3%) | 26% | -0.73% | -0.46% | -0.13% | -0.33% | -5.85% | 0.1% / 2.6% |

"cap only" keeps fees and spreads but no impact (what the participation cap alone costs: idle capital earns zero excess); "impact only" lifts the cap (what impact alone costs). The crash unwind is the cost of closing the whole book in one day at three times the trailing volatility and Y = 1, as a fraction of capital.

## Bybit

**Verdict: the chosen variant FAILS the go rule** (in-sample positive, out-of-sample HAC t > 2, a BH survivor, out-of-sample excess positive at $3M): bh_survivor=False, in_sample_positive=False, oos_positive_at_3m=False, oos_t_gt_2=False.

Excess is over the savings rate paid each day (DSR, then the SSR; mean 6.48% in sample, 3.82% out of sample; term_carry.load_navs), on the capital the trade ties up (K = 1 + max(0, im + 0.5 - 1.5c), c = today's collateral ratio; median K 1.29, c quartiles [0.1112033095, 0.206330169, 0.316853813]). Costs: taker fees spot 10bp / perp 5.5bp per side, half-spread from today's book tickers (75th percentile by volume bucket, floored at half a tick), double costs on forced exits. P&L window 2024-10-01..2026-10-10, split at 2025-10-06 (370 / 370 days).

### Data coverage

| item | value |
|---|---|
| USDT-margined coin perps found (listed any status + funding history) | 1065 |
| by status today | {"Closed": 272, "PendingOpen": 3, "Trading": 790} |
| symbols with funding history since 2024-09-01 | 1065 |
| perps with a traded daily bar in the window | 1061 |
| excluded (BTC, ETH, stables, gold, indices) | 8 |
| no same-coin spot pair on the venue | 640 |
|   no spot market (no data under any candidate name) | 632 |
|   spot overlap under 30 days | 7 |
|   a spot pair of the same name is another coin (rejected) | 1 |
| coins with both legs (the all-spot universe) | 413 |
| of which collateral today (main universe) | 239 |
| coins with a leg delisted in the window | 120 |
|   perp delisted | 112 |
|   spot delisted | 94 |
| perps with no traded bar in the window that still print settlements in it (dropped entirely) | 3 |
|   their settlements in the window | 14 |
| settlements fetched (the perps above with a traded bar) | 2234856 |
| settlements kept | 2191326 |
| dropped: funding day without a traded perp bar, or after delivery | 43530 |
|   stamped after the last traded perp bar (phantom prints) | 0 |
|   before the first traded bar (paging overshoot before the window, pre-market funding) | 43530 |
| collateral assets on 2026-10-11 | 268 |

Main universe at the 7-day rebalances: eligible names median 198 (min 137, max 233); at the floor on >= 50% of trailing settlements median 136; with spot volume >= $2M median 28, >= $10M median 4.

### Does floor persistence persist? (eligible coins at every 7-day rebalance, next 28 days)

| universe | trailing floor share | coin-dates | trailing APR | next floor share | next APR mean | next APR median | next APR p10 | next 28d has a spike < -0.05%/8h |
|---|---|---|---|---|---|---|---|---|
| main | [0.00, 0.25) | 1629 | -40.47% | 30% | -21.03% | -1.41% | -54.31% | 45% |
| main | [0.25, 0.50) | 4248 | -20.61% | 48% | -11.35% | +2.19% | -32.25% | 41% |
| main | [0.50, 0.75) | 6995 | -6.59% | 64% | -5.59% | +3.89% | -20.83% | 53% |
| main | [0.75, 0.90) | 4318 | +2.07% | 74% | -4.24% | +6.06% | -18.38% | 56% |
| main | [0.90, 1.00) | 2829 | +8.97% | 85% | -1.04% | +8.89% | -11.95% | 48% |
| main_spike_screened | [0.00, 0.25) | 752 | +1.84% | 29% | +0.85% | +2.09% | -4.74% | 9% |
| main_spike_screened | [0.25, 0.50) | 2299 | +5.90% | 48% | +3.11% | +3.74% | -1.48% | 12% |
| main_spike_screened | [0.50, 0.75) | 2999 | +8.45% | 64% | +5.67% | +6.62% | -0.05% | 21% |
| main_spike_screened | [0.75, 0.90) | 1876 | +9.28% | 72% | +6.05% | +8.05% | +0.04% | 29% |
| main_spike_screened | [0.90, 1.00) | 1891 | +10.59% | 85% | +4.02% | +9.58% | +0.29% | 36% |
| main_v10m_spike_screened | [0.00, 0.25) | 269 | +4.68% | 31% | +3.10% | +2.73% | -1.92% | 2% |
| main_v10m_spike_screened | [0.25, 0.50) | 470 | +11.25% | 47% | +6.14% | +4.78% | +0.19% | 4% |
| main_v10m_spike_screened | [0.50, 0.75) | 447 | +11.81% | 60% | +8.88% | +7.85% | -0.48% | 16% |
| main_v10m_spike_screened | [0.75, 0.90) | 163 | +9.98% | 63% | +9.33% | +7.33% | +2.57% | 24% |
| main_v10m_spike_screened | [0.90, 1.00) | 37 | +11.29% | 75% | +8.90% | +8.57% | +3.67% | 27% |
| all_spot | [0.00, 0.25) | 1902 | -55.92% | 31% | -31.27% | -2.91% | -82.56% | 50% |
| all_spot | [0.25, 0.50) | 5017 | -30.41% | 50% | -16.64% | +1.98% | -48.16% | 46% |
| all_spot | [0.50, 0.75) | 9174 | -11.24% | 66% | -9.51% | +3.86% | -35.30% | 56% |
| all_spot | [0.75, 0.90) | 7050 | +0.31% | 76% | -6.09% | +6.66% | -26.95% | 56% |
| all_spot | [0.90, 1.00) | 6470 | +8.82% | 87% | -0.51% | +9.86% | -13.19% | 44% |

### Protocol: choose on the first half, test once on the second

| chosen | in-sample excess | IS Sharpe | in_sample_positive | OOS excess | OOS Sharpe | OOS HAC t | OOS t (30 lags) | OOS rank | deflated Sharpe (IS, 32 trials) | BH survivors (q=0.10, full sample, one-sided: mean > 0) |
|---|---|---|---|---|---|---|---|---|---|---|
| R28_F50_Sm5bp_V10M_N30 | -0.02% | -0.04 | False | -0.40% | -1.15 | -1.87 | -1.73 | 7/32 | 0.001 | 0 |

backtest.choose_then_test's own BH (two-sided p) would list 24 "survivors" here; 24 of them have a negative full-sample mean, i.e. they are significant losers.

Chosen variant: full sample -0.21% (t -0.42); deflated Sharpe full 0.003, OOS 0.000; OOS mean daily excess, 28-day block bootstrap 95% interval -0.96%..-0.07% a year.

### All variants (main universe, small size), by in-sample excess

| variant | full | in sample | OOS | OOS t | BH adj p | names held | invested | turnover/yr | forced exits | neg. funding/yr |
|---|---|---|---|---|---|---|---|---|---|---|
| R28_F50_Sm5bp_V10M_N30 (chosen) | -0.21% | -0.02% | -0.40% | -1.87 | 1.000 | 6.3 | 21% | 347% | 0 | 0.40% |
| R28_F50_Snone_V10M_N30 | -0.67% | -0.32% | -1.02% | -3.20 | 1.000 | 7.9 | 26% | 410% | 0 | 0.86% |
| R28_F75_Sm5bp_V10M_N30 | -0.24% | -0.42% | -0.05% | -1.47 | 1.000 | 1.7 | 6% | 112% | 0 | 0.13% |
| R28_F75_Snone_V10M_N30 | -0.31% | -0.45% | -0.16% | -2.58 | 1.000 | 2.0 | 7% | 125% | 0 | 0.19% |
| R28_F50_Sm5bp_V10M_N10 | -0.78% | -0.55% | -1.01% | -2.00 | 1.000 | 4.2 | 42% | 792% | 0 | 0.92% |
| R28_F75_Sm5bp_V2M_N30 | -0.50% | -0.62% | -0.38% | -1.25 | 1.000 | 7.6 | 25% | 431% | 0 | 0.55% |
| R7_F75_Sm5bp_V10M_N30 | -0.38% | -0.71% | -0.06% | -1.73 | 1.000 | 1.9 | 6% | 260% | 0 | 0.09% |
| R7_F50_Sm5bp_V10M_N30 | -0.59% | -0.78% | -0.40% | -1.89 | 1.000 | 6.1 | 20% | 596% | 0 | 0.32% |
| R28_F75_Sm5bp_V10M_N10 | -0.47% | -0.79% | -0.15% | -1.47 | 1.000 | 1.5 | 15% | 296% | 0 | 0.33% |
| R28_F75_Snone_V10M_N10 | -0.68% | -0.87% | -0.49% | -2.58 | 1.000 | 1.7 | 17% | 325% | 0 | 0.51% |
| R7_F75_Snone_V10M_N30 | -0.55% | -0.90% | -0.20% | -2.76 | 1.000 | 2.3 | 8% | 314% | 0 | 0.17% |
| R28_F75_Snone_V2M_N30 | -1.93% | -1.18% | -2.68% | -2.61 | 1.000 | 10.6 | 35% | 532% | 0 | 1.90% |
| R28_F75_Sm5bp_V2M_N10 | -0.72% | -1.23% | -0.20% | -0.53 | 1.000 | 4.2 | 42% | 693% | 0 | 0.76% |
| R28_F50_Sm5bp_V2M_N30 | -1.19% | -1.35% | -1.03% | -2.09 | 1.000 | 15.0 | 50% | 755% | 0 | 1.07% |
| R7_F50_Snone_V10M_N30 | -1.42% | -1.41% | -1.42% | -2.58 | 1.000 | 8.0 | 27% | 725% | 0 | 1.05% |
| R7_F75_Sm5bp_V10M_N10 | -0.81% | -1.43% | -0.19% | -1.73 | 1.000 | 1.6 | 16% | 654% | 0 | 0.22% |
| R28_F50_Snone_V10M_N10 | -2.14% | -1.60% | -2.68% | -3.51 | 1.000 | 5.2 | 52% | 918% | 0 | 2.17% |
| R28_F75_Snone_V2M_N10 | -2.32% | -1.84% | -2.80% | -3.19 | 1.000 | 5.8 | 58% | 898% | 0 | 2.22% |
| R7_F75_Snone_V10M_N10 | -1.27% | -1.93% | -0.60% | -2.76 | 1.000 | 2.0 | 20% | 805% | 0 | 0.46% |
| R7_F50_Sm5bp_V10M_N10 | -1.64% | -2.16% | -1.11% | -2.11 | 1.000 | 4.1 | 41% | 1450% | 0 | 0.72% |
| R7_F75_Sm5bp_V2M_N30 | -1.31% | -2.25% | -0.36% | -1.22 | 1.000 | 7.7 | 26% | 779% | 0 | 0.43% |
| R28_F50_Sm5bp_V2M_N10 | -1.77% | -2.28% | -1.27% | -2.51 | 1.000 | 6.9 | 69% | 1181% | 0 | 1.42% |
| R28_F50_Snone_V2M_N10 | -4.26% | -2.44% | -6.08% | -5.07 | 1.000 | 9.4 | 94% | 1453% | 0 | 4.04% |
| R28_F50_Snone_V2M_N30 | -3.87% | -2.76% | -4.97% | -4.34 | 1.000 | 21.5 | 72% | 908% | 0 | 3.84% |
| R7_F50_Sm5bp_V2M_N30 | -2.22% | -3.06% | -1.39% | -2.67 | 1.000 | 15.1 | 50% | 1374% | 0 | 0.99% |
| R7_F75_Snone_V2M_N30 | -3.17% | -3.55% | -2.80% | -2.74 | 1.000 | 11.1 | 37% | 1009% | 0 | 2.12% |
| R7_F75_Sm5bp_V2M_N10 | -2.13% | -3.79% | -0.46% | -1.18 | 1.000 | 4.1 | 41% | 1340% | 0 | 0.72% |
| R7_F50_Snone_V10M_N10 | -3.83% | -3.80% | -3.87% | -2.59 | 1.000 | 5.3 | 53% | 1713% | 0 | 2.65% |
| R7_F50_Snone_V2M_N30 | -6.03% | -5.40% | -6.66% | -4.20 | 1.000 | 22.0 | 73% | 1665% | 0 | 4.66% |
| R7_F50_Sm5bp_V2M_N10 | -4.14% | -5.74% | -2.53% | -5.39 | 1.000 | 7.2 | 72% | 2338% | 0 | 1.54% |
| R7_F75_Snone_V2M_N10 | -4.92% | -6.20% | -3.64% | -3.34 | 1.000 | 6.0 | 60% | 1865% | 0 | 3.08% |
| R7_F50_Snone_V2M_N10 | -7.61% | -7.39% | -7.83% | -6.01 | 1.000 | 9.5 | 95% | 2744% | 0 | 4.93% |

### Chosen variant: where the P&L came from, and its tail

| funding/yr | of which at the floor | basis/yr | costs/yr | savings rate on invested/yr | excess/yr | turnover/yr | names held | invested |
|---|---|---|---|---|---|---|---|---|
| +2.00% | 53% | +0.01% | -0.63% | -1.59% | -0.21% | 347% | 6.3 | 21% |

| worst rolling week | worst calendar week | max drawdown | best 1% of days: share of excess (of gross) | negative settlements paid/yr (share of positive funding) | forced exits (delisting/gap) | rally rebalances |
|---|---|---|---|---|---|---|
| -0.29% from 2025-02-15 | -0.22% (2024-W52) | 1.9% | - (43%) | 0.4% (17%) | 0 (0/0) | 21 |

By year: 2024 +4.14% (92d), 2025 -1.40% (365d), 2026 -0.10% (283d). By half-year: 2024H2 +4.14%, 2025H1 -2.18%, 2025H2 -0.62%, 2026H1 -0.05%, 2026H2 -0.19%.

Best coins (P&L in capital units over the window, before the benchmark): DOGEUSDT +0.17%, POPCATUSDT +0.17%, 1000PEPEUSDT +0.17%, XRPUSDT +0.14%, ARBUSDT +0.14%, NEARUSDT +0.14%, WLDUSDT +0.13%, LTCUSDT +0.12%. Worst: GRASSUSDT -0.05%, PENGUUSDT -0.03%, VIRTUALUSDT -0.02%, TRUMPUSDT -0.01%, SUSDT -0.00%, PNUTUSDT +0.01%, ONDOUSDT +0.01%, GALAUSDT +0.01%.

Last book (2026-09-29): ENAUSDT (floor 70%, spot vol $24.91M, c 0.80), NEARUSDT (floor 66%, spot vol $16.52M, c 0.85), ASTERUSDT (floor 64%, spot vol $11.80M, c 0.57), WLDUSDT (floor 56%, spot vol $11.34M, c 0.76), MNTUSDT (floor 58%, spot vol $11.29M, c 0.99).

### Baseline: always the top N by floor share

| baseline | full | in sample | OOS | OOS t | excess per $ deployed | worst week | max drawdown | neg. funding/yr | turnover/yr | names held |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline_R28_F0_Snone_V2M_N10 | -5.87% | -2.44% | -9.30% | -4.63 | -5.87% | -1.74% | 12.8% | 5.7% | 1528% | 10.0 |
| baseline_R28_F0_Snone_V2M_N30 | -6.30% | -2.74% | -9.86% | -6.23 | -6.36% | -1.08% | 14.0% | 6.3% | 1126% | 29.7 |

### Robustness

| run | full | in sample | OOS | OOS t |
|---|---|---|---|---|
| all-spot universe (delisted included, c = 0.21 for every coin): its own chosen R28_F50_Sm5bp_V10M_N30 | - | -0.44% | -0.37% | -2.05 |
| all-spot universe, the main chosen variant | -0.40% | -0.44% | -0.37% | -2.05 |
| main universe at the assumed ratio (bridge) | -0.43% | -0.50% | -0.36% | -2.08 |
| fees and spreads x2 | -0.85% | -1.10% | -0.59% | -2.36 |
| constant 3.80% benchmark | +0.58% | +1.53% | -0.38% | -1.80 |
| late entry: signal one day stale | -0.12% | +0.16% | -0.40% | -1.83 |

All-spot universe: BH survivors 0; in_sample_positive False; forced exits of the main chosen variant there 0 (none).

### Post hoc (computed after the protocol; selects nothing)

| run | full | in sample | OOS | OOS t |
|---|---|---|---|---|
| chosen, excess per $ actually deployed | -1.01% | -0.06% | -7.58% | - |
| chosen at zero fees and spreads | +0.42% | +1.06% | -0.22% | -1.06 |
| chosen at zero cost, per $ deployed | - | +2.88% | -4.09% | - |
| broad R28_F50_Sm5bp_V2M_N30 (costed) | -1.19% | -1.35% | -1.03% | -2.09 |
| broad, per $ deployed | - | -1.65% | -5.50% | - |
| broad at zero fees and spreads | +0.37% | +1.07% | -0.34% | -0.73 |

| P&L per year of capital deployed | funding | of which negative settlements | basis | costs | savings rate | invested |
|---|---|---|---|---|---|---|
| chosen, in sample | +10.82% | -1.30% | +0.07% | -2.94% | -8.01% | 37% |
| chosen, out of sample | +0.20% | -5.91% | -0.00% | -3.49% | -4.28% | 5% |
| broad, in sample | +8.36% | -1.44% | -0.14% | -2.96% | -6.92% | 82% |
| broad, out of sample | +1.77% | -5.12% | +0.47% | -3.69% | -4.04% | 19% |

Names kept from one rebalance to the next: chosen 45%, broad 39%.

Broad variant, whole window per year of capital: funding +3.58% (negative settlements -1.07%), basis -0.01%, costs -1.55%, savings rate on invested -3.20%; turnover 755%; invested 82% in sample, 19% out of sample; worst week -0.64%, max drawdown 3.8%.

### Capacity (chosen variant; each name <= 2% of its 30-day median daily spot and perp volume, built and unwound over 3 days, square-root impact Y = 0.5, stress Y = 1)

| capital | excess full | excess OOS | OOS t | $/yr OOS | invested (OOS) | names capped | impact/yr | stress Y=1 OOS | cap only OOS | impact only OOS | baseline OOS | one-day crash unwind (median / worst) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $1.00M | -0.55% | -0.51% | -2.21 | -$5k | 21% (5%) | 0% | -0.34% | -0.62% | -0.40% | -0.51% | -11.60% | 0.1% / 1.1% |
| $3.00M | -0.80% | -0.59% | -2.39 | -$18k | 21% (5%) | 0% | -0.59% | -0.78% | -0.40% | -0.59% | -9.93% | 0.1% / 1.8% |
| $5.00M | -0.97% | -0.65% | -2.48 | -$32k | 21% (5%) | 1% | -0.76% | -0.89% | -0.40% | -0.65% | -7.37% | 0.2% / 2.3% |
| $10.00M | -1.06% | -0.60% | -2.46 | -$60k | 19% (5%) | 44% | -0.90% | -0.86% | -0.34% | -0.75% | -4.38% | 0.2% / 2.8% |

"cap only" keeps fees and spreads but no impact (what the participation cap alone costs: idle capital earns zero excess); "impact only" lifts the cap (what impact alone costs). The crash unwind is the cost of closing the whole book in one day at three times the trailing volatility and Y = 1, as a fraction of capital.

## Caveats

- Collateral survivorship: collateral lists exist only as of the watcher's 2026-10-11 snapshot. The main universe is today's list, so every coin delisted before today is absent from it and never forces an exit there; the all-spot universe includes delisted coins and shows what they cost.
- Ratios are today's for the whole history (Binance: the classic program; Bybit: UTA tiers at a $1M holding).
- Daily closes are last trades, not mids, so the basis at entry and exit carries last-trade noise; funding is paid on the settlement's mark price where the venue reports it (Binance) and on the day's perp close otherwise (Bybit).
- Half-spreads come from one Sunday snapshot of book tickers applied by volume bucket to the whole history; impact is a square-root model, not measured fills.
- OKX is not covered: its public funding history serves about three months, not the window.
