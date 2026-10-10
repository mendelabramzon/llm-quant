# Governance events — tables

Generated 2026-10-10T12:30:19+00:00. Labels frozen 2026-10-10T12:26:08+00:00 (sha256 d71f689d4b22…); analysis started 2026-10-10T12:30:18+00:00; cutoff 2024-07-01T00:00:00+00:00; pair round trip at $25k a leg.

## Labels from the LLM reading (criteria.md)

Value events after same-day dedupe: 341 (priced 341: {'VALUE_DOWN': 167, 'VALUE_UP': 174}); 168 before the cutoff, 173 after; 63 tokens.

### Abnormal log return vs the equal-weight basket (vs BTC in brackets), t by event week

| label | window | n | mean | t week | hit | in-sample mean (t wk) | out-of-sample mean (t wk) |
|---|---|---:|---:|---:|---:|---:|---:|
| VALUE_UP | pre7 | 174 | +0.52% (-1.73%) | 0.91 | 47% | +0.28% (0.07) | +0.74% (1.36) |
| VALUE_UP | created+1d | 174 | +0.45% (+0.19%) | 1.37 | 49% | +0.09% (0.69) | +0.77% (1.58) |
| VALUE_UP | vote | 174 | +2.01% (+1.00%) | 2.68 | 56% | +3.65% (2.61) | +0.52% (0.84) |
| VALUE_UP | end+1d | 174 | +0.49% (+0.32%) | 1.25 | 45% | +0.61% (1.09) | +0.38% (0.60) |
| VALUE_UP | end+3d | 174 | +0.42% (-0.39%) | 0.92 | 46% | +0.41% (0.68) | +0.43% (0.70) |
| VALUE_UP | end+7d | 174 | +1.58% (-0.12%) | 1.91 | 51% | +3.74% (2.34) | -0.40% (-0.14) |
| VALUE_UP | created..end+7d | 174 | +3.49% (+0.76%) | 3.02 | 55% | +7.24% (3.37) | +0.07% (0.33) |
| VALUE_DOWN | pre7 | 167 | +0.52% (-0.95%) | 0.56 | 42% | +0.97% (0.73) | +0.05% (0.07) |
| VALUE_DOWN | created+1d | 167 | -0.04% (-0.53%) | -0.66 | 40% | -0.03% (-0.47) | -0.06% (-0.50) |
| VALUE_DOWN | vote | 167 | +0.19% (-1.56%) | 0.38 | 43% | -0.17% (-0.11) | +0.56% (0.65) |
| VALUE_DOWN | end+1d | 167 | +0.13% (-0.26%) | 0.59 | 46% | +0.46% (1.49) | -0.22% (-0.76) |
| VALUE_DOWN | end+3d | 167 | -0.43% (-0.77%) | -0.86 | 40% | -0.99% (-1.54) | +0.15% (0.14) |
| VALUE_DOWN | end+7d | 167 | -0.89% (-3.71%) | -0.60 | 44% | -1.22% (-0.43) | -0.54% (-0.43) |
| VALUE_DOWN | created..end+7d | 167 | -0.80% (-5.47%) | -0.37 | 43% | -1.50% (-0.64) | -0.08% (0.06) |
| NEUTRAL | pre7 | 1775 | +0.64% (-1.14%) | 1.88 | 46% | +0.33% (0.98) | +1.22% (2.23) |
| NEUTRAL | created+1d | 1775 | +0.12% (-0.03%) | 0.52 | 48% | +0.16% (0.06) | +0.06% (1.13) |
| NEUTRAL | vote | 1774 | +0.50% (-0.79%) | 1.87 | 47% | +0.30% (0.48) | +0.87% (3.18) |
| NEUTRAL | end+1d | 1775 | +0.28% (+0.08%) | 2.25 | 47% | +0.24% (0.94) | +0.36% (2.67) |
| NEUTRAL | end+3d | 1775 | +0.29% (-0.40%) | 1.16 | 47% | +0.18% (0.07) | +0.48% (2.27) |
| NEUTRAL | end+7d | 1775 | +0.56% (-1.20%) | 1.24 | 48% | +0.15% (0.10) | +1.33% (2.07) |
| NEUTRAL | created..end+7d | 1775 | +1.02% (-2.09%) | 2.12 | 47% | +0.42% (0.39) | +2.14% (3.69) |

Benjamini-Hochberg (q = 0.10) over the 14 value-label x window cells, event-week t: full sample VALUE_UP vote, VALUE_UP created..end+7d; in sample VALUE_UP vote, VALUE_UP end+7d, VALUE_UP created..end+7d; out of sample none.

Placebo (same token, created..end+7d shifted 15-30 days, away from other value events): VALUE_DOWN +0.19% (n 266, t wk -0.14); VALUE_UP +0.38% (n 290, t wk 0.65)

### Trades (pair vs BTC, after funding and costs; excess = over the placebo)

| window | side | filter | n in | mean in | placebo in | excess t in | n out | mean out | placebo out | excess t out | t wk out | hit out | over SSR out | BH in | BH out |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| start+1d>end | up_long | all | 78 | +3.30% | -0.18% | 1.65 | 87 | -1.78% | -1.69% | -0.08 | -2.04 | 39% | -1.82% |  |  |
| start+1d>end | up_long | passed (look-ahead) | 69 | +2.30% | -0.32% | 1.17 | 78 | -1.98% | -1.67% | -0.28 | -2.10 | 38% | -2.02% |  |  |
| start+1d>end | down_short | all | 84 | +0.20% | +0.53% | -0.27 | 81 | +0.87% | +1.28% | -0.29 | 0.03 | 48% | +0.82% |  |  |
| start+1d>end | down_short | passed (look-ahead) | 73 | +0.54% | +0.75% | -0.17 | 75 | +1.15% | +1.33% | -0.13 | 0.23 | 49% | +1.09% |  |  |
| start+1d>end | both | all | 162 | +1.69% | +0.18% | 1.26 | 168 | -0.50% | -0.28% | -0.26 | -1.45 | 43% | -0.54% |  |  |
| start+1d>end | both | passed (look-ahead) | 142 | +1.40% | +0.23% | 0.92 | 153 | -0.45% | -0.25% | -0.21 | -1.34 | 44% | -0.49% |  |  |
| start+1d>end+1d | up_long | all | 83 | +4.71% | +0.37% | 1.57 | 91 | -1.57% | -1.79% | 0.20 | -1.97 | 41% | -1.63% |  |  |
| start+1d>end+1d | up_long | passed (look-ahead) | 74 | +4.08% | +0.16% | 1.29 | 82 | -1.85% | -1.77% | -0.07 | -2.08 | 40% | -1.90% |  |  |
| start+1d>end+1d | down_short | all | 85 | -0.01% | +0.88% | -0.58 | 82 | +1.12% | +1.72% | -0.40 | 0.23 | 59% | +1.06% |  |  |
| start+1d>end+1d | down_short | passed (look-ahead) | 74 | +0.30% | +1.76% | -1.05 | 76 | +1.31% | +1.72% | -0.25 | 0.30 | 59% | +1.25% |  |  |
| start+1d>end+1d | both | all | 168 | +2.32% | +0.62% | 1.08 | 173 | -0.30% | -0.16% | -0.15 | -0.99 | 49% | -0.35% |  |  |
| start+1d>end+1d | both | passed (look-ahead) | 148 | +2.19% | +0.95% | 0.74 | 158 | -0.33% | -0.16% | -0.17 | -1.13 | 49% | -0.39% |  |  |
| start+1d>end+3d | up_long | all | 83 | +4.63% | +1.03% | 1.02 | 91 | -1.91% | -2.63% | 0.56 | -1.22 | 36% | -1.99% |  |  |
| start+1d>end+3d | up_long | passed (look-ahead) | 74 | +3.76% | +0.93% | 0.76 | 82 | -2.36% | -2.74% | 0.29 | -1.41 | 35% | -2.43% |  |  |
| start+1d>end+3d | down_short | all | 85 | +1.35% | -1.02% | 0.92 | 82 | +0.78% | +2.24% | -0.75 | -0.13 | 59% | +0.70% |  |  |
| start+1d>end+3d | down_short | passed (look-ahead) | 74 | +1.88% | +1.67% | 0.14 | 76 | +0.59% | +2.41% | -0.88 | -0.36 | 59% | +0.51% |  |  |
| start+1d>end+3d | both | all | 168 | +2.98% | +0.02% | 1.35 | 173 | -0.63% | -0.37% | -0.23 | -0.63 | 47% | -0.71% |  |  |
| start+1d>end+3d | both | passed (look-ahead) | 148 | +2.82% | +1.30% | 0.75 | 158 | -0.94% | -0.37% | -0.47 | -0.92 | 47% | -1.01% |  |  |
| start+1d>end+7d | up_long | all | 83 | +9.59% | -0.12% | 1.86 | 91 | -3.36% | -3.45% | 0.05 | -1.99 | 36% | -3.48% |  |  |
| start+1d>end+7d | up_long | passed (look-ahead) | 74 | +10.65% | -0.41% | 1.91 | 82 | -4.03% | -3.36% | -0.40 | -2.22 | 34% | -4.15% |  |  |
| start+1d>end+7d | down_short | all | 85 | +2.92% | -0.79% | 1.35 | 82 | +2.49% | +2.23% | 0.11 | 0.29 | 61% | +2.36% |  |  |
| start+1d>end+7d | down_short | passed (look-ahead) | 74 | +3.12% | +0.90% | 0.93 | 76 | +2.51% | +2.26% | 0.10 | 0.30 | 62% | +2.38% |  |  |
| start+1d>end+7d | both | all | 168 | +6.22% | -0.45% | 2.27 | 173 | -0.59% | -0.82% | 0.16 | -0.81 | 48% | -0.71% |  |  |
| start+1d>end+7d | both | passed (look-ahead) | 148 | +6.88% | +0.23% | 2.11 | 158 | -0.89% | -0.78% | -0.07 | -1.15 | 47% | -1.01% |  |  |
| end+1h>end+1d | up_long | all | 83 | +0.78% | -0.22% | 1.06 | 91 | -0.35% | -0.96% | 1.08 | -1.26 | 36% | -0.36% |  |  |
| end+1h>end+1d | up_long | passed | 74 | +1.05% | -0.38% | 1.37 | 82 | -0.47% | -0.97% | 0.83 | -1.17 | 37% | -0.48% |  |  |
| end+1h>end+1d | down_short | all | 85 | -0.65% | +0.08% | -1.08 | 82 | -0.40% | -0.28% | -0.19 | -0.98 | 45% | -0.41% |  |  |
| end+1h>end+1d | down_short | passed | 74 | -0.67% | +0.35% | -1.41 | 76 | -0.41% | -0.31% | -0.14 | -0.98 | 46% | -0.42% |  |  |
| end+1h>end+1d | both | all | 168 | +0.06% | -0.07% | 0.22 | 173 | -0.37% | -0.64% | 0.61 | -1.24 | 40% | -0.38% |  |  |
| end+1h>end+1d | both | passed | 148 | +0.19% | -0.02% | 0.33 | 158 | -0.44% | -0.67% | 0.48 | -1.51 | 41% | -0.45% |  |  |
| end+1h>end+3d | up_long | all | 83 | +0.69% | -0.06% | 0.40 | 91 | -0.71% | -1.56% | 0.89 | -0.50 | 35% | -0.74% |  |  |
| end+1h>end+3d | up_long | passed | 74 | +0.96% | -0.12% | 0.57 | 82 | -1.01% | -1.70% | 0.69 | -0.68 | 33% | -1.04% |  |  |
| end+1h>end+3d | down_short | all | 85 | +0.66% | -1.29% | 1.30 | 82 | -0.71% | +0.21% | -0.71 | -0.74 | 50% | -0.74% |  |  |
| end+1h>end+3d | down_short | passed | 74 | +0.89% | +0.26% | 0.64 | 76 | -1.09% | +0.38% | -1.10 | -1.15 | 49% | -1.12% |  |  |
| end+1h>end+3d | both | all | 168 | +0.68% | -0.67% | 1.12 | 173 | -0.71% | -0.74% | 0.04 | -0.53 | 42% | -0.74% |  |  |
| end+1h>end+3d | both | passed | 148 | +0.93% | +0.07% | 0.81 | 158 | -1.05% | -0.74% | -0.37 | -0.96 | 41% | -1.08% |  |  |
| end+1h>end+7d | up_long | all | 83 | +4.67% | -0.92% | 1.90 | 91 | -2.09% | -2.76% | 0.47 | -1.34 | 40% | -2.16% |  |  |
| end+1h>end+7d | up_long | passed | 74 | +6.48% | -1.15% | 2.40 | 82 | -2.57% | -2.72% | 0.10 | -1.47 | 37% | -2.64% |  |  |
| end+1h>end+7d | down_short | all | 85 | +2.38% | -1.19% | 1.78 | 82 | +1.00% | +0.20% | 0.46 | 0.04 | 59% | +0.93% |  |  |
| end+1h>end+7d | down_short | passed | 74 | +2.36% | -0.42% | 1.38 | 76 | +0.82% | +0.22% | 0.33 | -0.01 | 58% | +0.74% |  |  |
| end+1h>end+7d | both | all | 168 | +3.51% | -1.05% | 2.58 | 173 | -0.62% | -1.39% | 0.67 | -0.75 | 49% | -0.69% |  |  |
| end+1h>end+7d | both | passed | 148 | +4.42% | -0.79% | 2.76 | 158 | -0.94% | -1.37% | 0.36 | -1.20 | 47% | -1.01% |  |  |

Chosen on events before the cutoff (highest excess-over-placebo t among 30 tradable variants, 30 with enough events): **end+1h>end+7d, both, passed**; deflated Sharpe out of sample 0.00.

Live books of the tokens the chosen variant traded: median depth within 50bp (thinner side) $32k, within 25bp $10k; median impact 39.70 bp at $50k, 64.98 bp at $100k; median 24h volume $4.8M.

### Conditional (created..end+7d, vs the basket; descriptive, chosen after the split, not tested)

| label | split | group | n | mean | t week | hit | in-sample n, mean (t wk) | out-of-sample n, mean (t wk) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| VALUE_DOWN | binding | binding | 66 | -0.63% | 0.01 | 41% | 29, -3.20% (-0.81) | 37, +1.39% (0.91) |
| VALUE_DOWN | binding | signal | 46 | +0.19% | -0.12 | 43% | 31, -0.40% (-0.26) | 15, +1.41% (0.18) |
| VALUE_DOWN | binding | unknown | 55 | -1.85% | -1.26 | 45% | 25, -0.90% (-0.47) | 30, -2.64% (-1.25) |
| VALUE_DOWN | confidence | conf<0.8 | 120 | -0.77% | -0.71 | 42% | 66, -1.74% (-0.85) | 54, +0.42% (-0.11) |
| VALUE_DOWN | confidence | conf>=0.8 | 47 | -0.89% | -0.19 | 45% | 19, -0.67% (-0.39) | 28, -1.04% (0.04) |
| VALUE_DOWN | decisive | margin<0.8 | 33 | -0.84% | -0.43 | 42% | 21, -2.25% (-1.16) | 12, +1.61% (0.97) |
| VALUE_DOWN | decisive | margin>=0.8 | 117 | -0.69% | -0.05 | 44% | 53, -1.88% (-0.40) | 64, +0.29% (0.29) |
| VALUE_DOWN | decisive | not passed | 17 | -1.50% | -0.55 | 41% | 11, +1.76% (0.63) | 6, -7.48% (-1.44) |
| VALUE_DOWN | found_by | control sample | 1 | +13.50% | — | 100% | 1, +13.50% (—) | 0, — (—) |
| VALUE_DOWN | found_by | keyword screen | 166 | -0.89% | -0.42 | 43% | 84, -1.68% (-0.73) | 82, -0.08% (0.06) |
| VALUE_DOWN | outcome | failed | 17 | -1.50% | -0.55 | 41% | 11, +1.76% (0.63) | 6, -7.48% (-1.44) |
| VALUE_DOWN | outcome | passed | 150 | -0.72% | -0.28 | 43% | 74, -1.98% (-0.96) | 76, +0.50% (0.53) |
| VALUE_DOWN | surprise | continuation | 65 | -0.72% | -0.02 | 46% | 31, -3.89% (-1.38) | 34, +2.18% (0.97) |
| VALUE_DOWN | surprise | first appearance | 102 | -0.86% | -1.02 | 41% | 54, -0.13% (-0.11) | 48, -1.68% (-1.32) |
| VALUE_UP | binding | binding | 50 | +8.34% | 2.29 | 60% | 28, +12.02% (2.01) | 22, +3.64% (1.22) |
| VALUE_UP | binding | signal | 48 | +3.79% | 1.74 | 54% | 26, +6.98% (2.13) | 22, +0.02% (-0.28) |
| VALUE_UP | binding | unknown | 76 | +0.10% | 0.35 | 51% | 29, +2.84% (1.05) | 47, -1.59% (-0.70) |
| VALUE_UP | confidence | conf<0.8 | 110 | +4.28% | 2.71 | 56% | 59, +6.69% (2.68) | 51, +1.50% (0.82) |
| VALUE_UP | confidence | conf>=0.8 | 64 | +2.12% | 0.91 | 52% | 24, +8.59% (1.42) | 40, -1.76% (-1.06) |
| VALUE_UP | decisive | margin<0.8 | 32 | +11.73% | 2.31 | 66% | 18, +17.86% (2.04) | 14, +3.85% (1.37) |
| VALUE_UP | decisive | margin>=0.8 | 124 | +1.38% | 1.65 | 51% | 56, +3.96% (2.31) | 68, -0.75% (-0.30) |
| VALUE_UP | decisive | not passed | 18 | +3.37% | 0.72 | 61% | 9, +6.39% (0.69) | 9, +0.36% (0.20) |
| VALUE_UP | found_by | keyword screen | 174 | +3.49% | 3.02 | 55% | 83, +7.24% (3.37) | 91, +0.07% (0.33) |
| VALUE_UP | outcome | failed | 18 | +3.37% | 0.72 | 61% | 9, +6.39% (0.69) | 9, +0.36% (0.20) |
| VALUE_UP | outcome | passed | 156 | +3.50% | 2.87 | 54% | 74, +7.34% (3.32) | 82, +0.03% (0.24) |
| VALUE_UP | surprise | continuation | 53 | +0.28% | -0.03 | 49% | 18, +2.28% (0.76) | 35, -0.75% (-0.70) |
| VALUE_UP | surprise | first appearance | 121 | +4.89% | 3.14 | 57% | 65, +8.61% (3.36) | 56, +0.58% (0.44) |

### By year of publication (vs the basket)

| label | window | year | n | mean | median | t week |
|---|---|---|---:|---:|---:|---:|
| VALUE_UP | created..end+7d | 2021 | 9 | +16.21% | +5.10% | 2.16 |
| VALUE_UP | created..end+7d | 2022 | 22 | +1.76% | +2.83% | 0.44 |
| VALUE_UP | created..end+7d | 2023 | 32 | +5.39% | +2.29% | 1.75 |
| VALUE_UP | created..end+7d | 2024 | 34 | +6.91% | +2.50% | 2.00 |
| VALUE_UP | created..end+7d | 2025 | 50 | -1.42% | -1.62% | -0.09 |
| VALUE_UP | created..end+7d | 2026 | 27 | +3.17% | +2.25% | 0.97 |
| VALUE_UP | end+7d | 2021 | 9 | +11.46% | +3.10% | 2.77 |
| VALUE_UP | end+7d | 2022 | 22 | +2.14% | +0.40% | 0.29 |
| VALUE_UP | end+7d | 2023 | 32 | +1.15% | +0.18% | 0.75 |
| VALUE_UP | end+7d | 2024 | 34 | +2.56% | -0.22% | 1.25 |
| VALUE_UP | end+7d | 2025 | 50 | -1.04% | -0.47% | 0.06 |
| VALUE_UP | end+7d | 2026 | 27 | +1.93% | +2.66% | 0.70 |
| VALUE_DOWN | created..end+7d | 2021 | 15 | -3.07% | -3.82% | -1.14 |
| VALUE_DOWN | created..end+7d | 2022 | 17 | -1.52% | -2.52% | 0.03 |
| VALUE_DOWN | created..end+7d | 2023 | 35 | +0.71% | -1.38% | 1.03 |
| VALUE_DOWN | created..end+7d | 2024 | 46 | -2.57% | -3.53% | -2.11 |
| VALUE_DOWN | created..end+7d | 2025 | 37 | -1.03% | -2.73% | -0.33 |
| VALUE_DOWN | created..end+7d | 2026 | 17 | +4.08% | +4.52% | 2.50 |
| VALUE_DOWN | end+7d | 2021 | 15 | -4.16% | -2.37% | -1.45 |
| VALUE_DOWN | end+7d | 2022 | 17 | +1.02% | +0.27% | 0.87 |
| VALUE_DOWN | end+7d | 2023 | 35 | -0.17% | -1.21% | 0.26 |
| VALUE_DOWN | end+7d | 2024 | 46 | -2.39% | -1.13% | -2.00 |
| VALUE_DOWN | end+7d | 2025 | 37 | -1.35% | -1.79% | -1.14 |
| VALUE_DOWN | end+7d | 2026 | 17 | +3.68% | +0.69% | 2.51 |
| NEUTRAL | created..end+7d | 2021 | 169 | +1.98% | -1.80% | 0.27 |
| NEUTRAL | created..end+7d | 2022 | 288 | +0.69% | -1.18% | 0.79 |
| NEUTRAL | created..end+7d | 2023 | 459 | -0.01% | -0.68% | -0.44 |
| NEUTRAL | created..end+7d | 2024 | 447 | +0.87% | -0.44% | 1.39 |
| NEUTRAL | created..end+7d | 2025 | 295 | +1.83% | +0.40% | 2.15 |
| NEUTRAL | created..end+7d | 2026 | 117 | +2.96% | +1.12% | 2.01 |
| NEUTRAL | end+7d | 2021 | 169 | +0.09% | -1.47% | -0.39 |
| NEUTRAL | end+7d | 2022 | 288 | +0.92% | -0.81% | 1.30 |
| NEUTRAL | end+7d | 2023 | 459 | -0.03% | -0.31% | -0.39 |
| NEUTRAL | end+7d | 2024 | 447 | +0.40% | -0.43% | 0.92 |
| NEUTRAL | end+7d | 2025 | 295 | +1.15% | +0.27% | 1.19 |
| NEUTRAL | end+7d | 2026 | 117 | +1.77% | +0.29% | 1.00 |

### Largest moves (created..end+7d, vs the basket)

| token | label | created | end | outcome | first? | AR vs basket | AR vs BTC | title |
|---|---|---|---|---|---|---:|---:|---|
| FLOKI | VALUE_UP | 2024-02-29 | 2024-03-02 | passed | yes | +140.2% | +145.6% | PROPOSAL: BURN 190,918,585,431.84 FLOKI TOKENS  |
| FLOKI | VALUE_UP | 2023-10-18 | 2023-10-20 | passed | yes | +63.0% | +58.6% | LAUNCH FLOKI STAKING PROGRAM AND INTRODUCE A REWARD TOKEN |
| MAGIC | VALUE_DOWN | 2025-07-28 | 2025-08-02 | passed | no | +57.5% | +61.3% | TIP-56: TIP-55 Re-Vote |
| CRV | VALUE_UP | 2021-11-20 | 2021-12-31 | passed | yes | +53.8% | +57.0% | Should Curve burn some CRVs? |
| APE | VALUE_DOWN | 2022-04-28 | 2022-05-05 | passed | no | -50.7% | -95.2% | AIP-21: Staking Process with Caps (1x drop) - Process |
| MANA | VALUE_UP | 2021-11-09 | 2021-11-16 | passed | yes | +46.2% | +59.5% | burn 10% of MANA (Total Supply) |
| YFI | VALUE_UP | 2021-12-07 | 2021-12-13 | passed | yes | +43.4% | +40.2% | YFI Tokenomics Non-Binding Poll |
| BNT | VALUE_UP | 2023-10-01 | 2023-10-04 | passed | yes | +39.0% | +26.7% | Proposal for the Bancor v2.1 vortex to use 100% of fees to burn BNT |
| SUSHI | VALUE_DOWN | 2024-12-06 | 2024-12-13 | passed | yes | +37.4% | +6.6% | Treasury Diversification Proposal [Signal] |
| BADGER | VALUE_UP | 2024-03-17 | 2024-03-20 | passed | yes | +36.4% | +39.7% | BIP 103 - Amendment 1 - 400k Vesting |
| ETHFI | VALUE_DOWN | 2024-06-25 | 2024-06-30 | passed | no | -35.4% | -45.8% | ETHFI DAO proposal: Season 3 and airdrop token allocation |
| GHST | VALUE_UP | 2025-03-08 | 2025-03-22 | passed | no | +33.1% | +23.3% | [AGIP 142] Buy 2 million dollars worth of GHST |
| MORPHO | VALUE_DOWN | 2024-12-07 | 2024-12-10 | passed | no | +31.0% | +7.9% | MIP-82- Increase MORPHO Reward Rate on Base |
| PEOPLE | VALUE_UP | 2022-05-04 | 2022-05-09 | failed | yes | -30.5% | -60.6% | PIP4: Convert assets in PeopleDAO treasury to $PEOPLE token |
| SPELL | VALUE_DOWN | 2023-09-11 | 2023-09-14 | passed | yes | +29.3% | +28.0% | AIP #28 - DWF Labs $SPELL Token Loan and Purchase Plans  |

## Labels from the keyword screen alone

Value events after same-day dedupe: 937 (priced 937: {'VALUE_DOWN': 618, 'VALUE_UP': 319}); 607 before the cutoff, 330 after; 76 tokens.

### Abnormal log return vs the equal-weight basket (vs BTC in brackets), t by event week

| label | window | n | mean | t week | hit | in-sample mean (t wk) | out-of-sample mean (t wk) |
|---|---|---:|---:|---:|---:|---:|---:|
| VALUE_UP | pre7 | 319 | +0.55% (-0.91%) | 0.63 | 47% | -0.07% (-0.14) | +1.14% (1.37) |
| VALUE_UP | created+1d | 319 | +0.30% (+0.12%) | 1.22 | 50% | +0.38% (0.99) | +0.22% (0.80) |
| VALUE_UP | vote | 319 | +1.37% (+0.16%) | 2.15 | 51% | +2.01% (1.84) | +0.75% (1.21) |
| VALUE_UP | end+1d | 319 | +0.53% (+0.28%) | 2.34 | 46% | +0.44% (1.44) | +0.62% (2.47) |
| VALUE_UP | end+3d | 319 | +0.04% (-0.71%) | 0.64 | 42% | -0.29% (0.27) | +0.35% (1.17) |
| VALUE_UP | end+7d | 319 | +0.34% (-2.15%) | 0.57 | 47% | +0.34% (0.64) | +0.34% (0.08) |
| VALUE_UP | created..end+7d | 319 | +1.50% (-2.20%) | 1.68 | 49% | +2.15% (1.64) | +0.89% (0.48) |
| VALUE_DOWN | pre7 | 618 | +0.25% (-1.40%) | 1.02 | 44% | +0.34% (0.97) | +0.01% (0.32) |
| VALUE_DOWN | created+1d | 618 | +0.12% (-0.24%) | 0.69 | 47% | +0.18% (1.38) | -0.05% (-0.93) |
| VALUE_DOWN | vote | 618 | +0.60% (-0.99%) | 1.12 | 46% | +0.53% (0.46) | +0.80% (1.65) |
| VALUE_DOWN | end+1d | 618 | +0.14% (+0.03%) | 0.97 | 45% | +0.07% (0.19) | +0.33% (1.77) |
| VALUE_DOWN | end+3d | 618 | +0.14% (-0.51%) | 0.87 | 48% | -0.10% (-0.73) | +0.78% (2.56) |
| VALUE_DOWN | end+7d | 618 | +0.63% (-0.88%) | 1.13 | 48% | +0.50% (0.50) | +0.99% (1.44) |
| VALUE_DOWN | created..end+7d | 618 | +1.19% (-2.02%) | 1.60 | 48% | +1.02% (0.79) | +1.66% (1.84) |
| NEUTRAL | pre7 | 1265 | +0.85% (-1.09%) | 1.91 | 46% | +0.57% (1.23) | +1.29% (1.87) |
| NEUTRAL | created+1d | 1265 | +0.08% (-0.02%) | 0.32 | 47% | +0.04% (-0.15) | +0.14% (1.19) |
| NEUTRAL | vote | 1264 | +0.34% (-0.89%) | 1.04 | 47% | +0.05% (-0.23) | +0.81% (2.19) |
| NEUTRAL | end+1d | 1265 | +0.28% (+0.01%) | 1.79 | 47% | +0.33% (1.30) | +0.21% (1.39) |
| NEUTRAL | end+3d | 1265 | +0.36% (-0.37%) | 0.97 | 47% | +0.30% (0.42) | +0.44% (1.17) |
| NEUTRAL | end+7d | 1265 | +0.57% (-1.28%) | 1.05 | 49% | +0.15% (0.08) | +1.26% (1.85) |
| NEUTRAL | created..end+7d | 1265 | +0.88% (-2.25%) | 1.40 | 47% | +0.16% (-0.10) | +2.03% (2.97) |

Benjamini-Hochberg (q = 0.10) over the 14 value-label x window cells, event-week t: full sample none; in sample none; out of sample VALUE_UP end+1d, VALUE_DOWN end+3d.

Placebo (same token, created..end+7d shifted 15-30 days, away from other value events): VALUE_DOWN -0.19% (n 570, t wk -0.97); VALUE_UP +0.70% (n 351, t wk 1.25)

### Trades (pair vs BTC, after funding and costs; excess = over the placebo)

| window | side | filter | n in | mean in | placebo in | excess t in | n out | mean out | placebo out | excess t out | t wk out | hit out | over SSR out | BH in | BH out |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| start+1d>end | up_long | all | 149 | +0.99% | -2.33% | 2.35 | 160 | -1.30% | -0.09% | -1.22 | -1.50 | 42% | -1.34% |  |  |
| start+1d>end | up_long | passed (look-ahead) | 134 | +1.23% | -1.89% | 2.04 | 148 | -1.30% | -0.25% | -1.02 | -1.59 | 43% | -1.35% |  |  |
| start+1d>end | down_short | all | 442 | -0.91% | -0.21% | -0.73 | 165 | +0.34% | +0.21% | 0.13 | 0.08 | 47% | +0.29% |  |  |
| start+1d>end | down_short | passed (look-ahead) | 352 | -1.46% | -0.25% | -1.05 | 143 | +0.30% | +0.20% | 0.09 | -0.24 | 47% | +0.25% |  |  |
| start+1d>end | both | all | 591 | -0.43% | -0.82% | 0.49 | 325 | -0.47% | +0.07% | -0.78 | -1.22 | 45% | -0.52% |  |  |
| start+1d>end | both | passed (look-ahead) | 486 | -0.72% | -0.74% | 0.02 | 291 | -0.52% | -0.02% | -0.68 | -1.33 | 45% | -0.56% |  |  |
| start+1d>end+1d | up_long | all | 156 | +2.12% | -2.33% | 2.31 | 163 | -1.39% | -0.24% | -1.12 | -1.66 | 41% | -1.44% |  |  |
| start+1d>end+1d | up_long | passed (look-ahead) | 141 | +2.41% | -1.91% | 2.06 | 151 | -1.34% | -0.43% | -0.85 | -1.65 | 42% | -1.39% |  |  |
| start+1d>end+1d | down_short | all | 451 | -0.99% | +0.16% | -1.14 | 167 | +0.23% | +0.36% | -0.13 | -0.45 | 50% | +0.17% |  |  |
| start+1d>end+1d | down_short | passed (look-ahead) | 361 | -1.55% | +0.20% | -1.47 | 145 | +0.26% | +0.28% | -0.02 | -0.59 | 48% | +0.20% |  |  |
| start+1d>end+1d | both | all | 607 | -0.19% | -0.59% | 0.44 | 330 | -0.57% | +0.07% | -0.89 | -1.75 | 45% | -0.63% |  |  |
| start+1d>end+1d | both | passed (look-ahead) | 502 | -0.44% | -0.45% | 0.01 | 296 | -0.56% | -0.07% | -0.64 | -1.57 | 45% | -0.61% |  |  |
| start+1d>end+3d | up_long | all | 156 | +1.34% | -2.31% | 1.69 | 163 | -2.00% | -0.79% | -1.02 | -1.28 | 36% | -2.08% |  |  |
| start+1d>end+3d | up_long | passed (look-ahead) | 141 | +1.35% | -1.95% | 1.44 | 151 | -2.05% | -1.01% | -0.88 | -1.52 | 36% | -2.13% |  |  |
| start+1d>end+3d | down_short | all | 451 | -0.70% | +0.71% | -1.35 | 167 | +0.37% | +1.56% | -1.06 | -0.22 | 56% | +0.29% |  |  |
| start+1d>end+3d | down_short | passed (look-ahead) | 361 | -1.20% | +0.49% | -1.39 | 145 | +0.35% | +1.69% | -1.11 | -0.48 | 56% | +0.27% |  |  |
| start+1d>end+3d | both | all | 607 | -0.18% | -0.20% | 0.02 | 330 | -0.80% | +0.44% | -1.52 | -1.81 | 46% | -0.88% |  |  |
| start+1d>end+3d | both | passed (look-ahead) | 502 | -0.49% | -0.26% | -0.21 | 296 | -0.88% | +0.36% | -1.46 | -1.97 | 46% | -0.95% |  |  |
| start+1d>end+7d | up_long | all | 156 | +1.08% | -2.49% | 1.20 | 163 | -3.30% | -1.11% | -1.52 | -2.00 | 33% | -3.41% |  |  |
| start+1d>end+7d | up_long | passed (look-ahead) | 141 | +1.72% | -1.62% | 1.03 | 151 | -3.51% | -1.16% | -1.56 | -2.11 | 32% | -3.62% |  |  |
| start+1d>end+7d | down_short | all | 451 | -0.99% | +1.59% | -1.92 | 167 | +0.74% | +0.78% | -0.03 | 0.57 | 59% | +0.62% |  |  |
| start+1d>end+7d | down_short | passed (look-ahead) | 361 | -1.84% | +1.46% | -2.12 | 145 | +0.89% | +0.70% | 0.12 | 0.41 | 59% | +0.77% |  |  |
| start+1d>end+7d | both | all | 607 | -0.46% | +0.36% | -0.65 | 330 | -1.26% | -0.12% | -1.11 | -1.52 | 46% | -1.37% |  |  |
| start+1d>end+7d | both | passed (look-ahead) | 502 | -0.84% | +0.52% | -0.94 | 296 | -1.35% | -0.21% | -1.05 | -1.71 | 45% | -1.47% |  |  |
| end+1h>end+1d | up_long | all | 156 | +0.13% | -0.83% | 1.53 | 163 | -0.64% | -0.89% | 0.62 | -2.37 | 37% | -0.65% |  |  |
| end+1h>end+1d | up_long | passed | 141 | +0.15% | -0.83% | 1.44 | 151 | -0.59% | -0.91% | 0.75 | -2.25 | 38% | -0.60% |  |  |
| end+1h>end+1d | down_short | all | 451 | -0.64% | -0.31% | -0.99 | 167 | -0.51% | -0.52% | 0.02 | -2.36 | 43% | -0.52% |  |  |
| end+1h>end+1d | down_short | passed | 361 | -0.69% | -0.25% | -1.23 | 145 | -0.47% | -0.58% | 0.24 | -2.16 | 42% | -0.48% |  |  |
| end+1h>end+1d | both | all | 607 | -0.44% | -0.47% | 0.09 | 330 | -0.57% | -0.70% | 0.42 | -3.19 | 40% | -0.58% |  |  |
| end+1h>end+1d | both | passed | 502 | -0.45% | -0.43% | -0.07 | 296 | -0.53% | -0.74% | 0.68 | -2.85 | 40% | -0.54% |  |  |
| end+1h>end+3d | up_long | all | 156 | -0.64% | -0.76% | 0.11 | 163 | -1.29% | -1.28% | -0.02 | -1.52 | 35% | -1.32% |  |  |
| end+1h>end+3d | up_long | passed | 141 | -0.83% | -0.82% | -0.01 | 151 | -1.35% | -1.25% | -0.13 | -1.85 | 34% | -1.38% |  |  |
| end+1h>end+3d | down_short | all | 451 | -0.46% | +0.20% | -1.15 | 167 | -0.39% | +0.54% | -1.29 | -0.96 | 49% | -0.42% |  |  |
| end+1h>end+3d | down_short | passed | 361 | -0.51% | +0.01% | -0.80 | 145 | -0.40% | +0.71% | -1.46 | -1.00 | 50% | -0.43% |  |  |
| end+1h>end+3d | both | all | 607 | -0.51% | -0.09% | -0.83 | 330 | -0.83% | -0.33% | -0.99 | -2.35 | 42% | -0.86% |  |  |
| end+1h>end+3d | both | passed | 502 | -0.60% | -0.24% | -0.63 | 296 | -0.88% | -0.25% | -1.17 | -2.44 | 42% | -0.91% |  |  |
| end+1h>end+7d | up_long | all | 156 | -1.15% | -1.10% | -0.02 | 163 | -2.45% | -1.76% | -0.57 | -2.10 | 36% | -2.52% |  |  |
| end+1h>end+7d | up_long | passed | 141 | -0.78% | -0.63% | -0.08 | 151 | -2.65% | -1.63% | -0.78 | -2.16 | 34% | -2.72% |  |  |
| end+1h>end+7d | down_short | all | 451 | -0.71% | +1.00% | -1.79 | 167 | +0.00% | -0.31% | 0.27 | 0.28 | 54% | -0.07% |  |  |
| end+1h>end+7d | down_short | passed | 361 | -1.11% | +0.88% | -1.82 | 145 | +0.13% | -0.33% | 0.37 | 0.36 | 54% | +0.06% |  |  |
| end+1h>end+7d | both | all | 607 | -0.82% | +0.37% | -1.41 | 330 | -1.21% | -1.00% | -0.25 | -1.82 | 45% | -1.28% |  |  |
| end+1h>end+7d | both | passed | 502 | -1.02% | +0.42% | -1.51 | 296 | -1.29% | -0.97% | -0.34 | -1.90 | 44% | -1.36% |  |  |

Chosen on events before the cutoff (highest excess-over-placebo t among 30 tradable variants, 30 with enough events): **start+1d>end, up_long, all**; deflated Sharpe out of sample 0.00.

Live books of the tokens the chosen variant traded: median depth within 50bp (thinner side) $36k, within 25bp $14k; median impact 35.56 bp at $50k, 60.53 bp at $100k; median 24h volume $5.5M.

### Conditional (created..end+7d, vs the basket; descriptive, chosen after the split, not tested)

| label | split | group | n | mean | t week | hit | in-sample n, mean (t wk) | out-of-sample n, mean (t wk) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| VALUE_DOWN | binding | binding | 222 | +2.42% | 1.53 | 49% | 162, +2.64% (1.25) | 60, +1.84% (1.12) |
| VALUE_DOWN | binding | signal | 193 | +0.65% | 1.37 | 47% | 157, -0.27% (-0.11) | 36, +4.65% (3.11) |
| VALUE_DOWN | binding | unknown | 203 | +0.37% | 0.91 | 48% | 132, +0.57% (0.62) | 71, -0.01% (0.70) |
| VALUE_DOWN | confidence | conf<0.8 | 146 | +1.19% | 0.74 | 52% | 98, +0.14% (-0.04) | 48, +3.33% (1.19) |
| VALUE_DOWN | confidence | conf>=0.8 | 472 | +1.19% | 1.64 | 47% | 353, +1.26% (1.21) | 119, +0.98% (1.55) |
| VALUE_DOWN | decisive | margin<0.8 | 120 | +1.80% | 1.62 | 46% | 93, +2.22% (1.49) | 27, +0.37% (0.67) |
| VALUE_DOWN | decisive | margin>=0.8 | 386 | +1.50% | 0.74 | 49% | 268, +1.19% (-0.04) | 118, +2.22% (1.77) |
| VALUE_DOWN | decisive | not passed | 112 | -0.53% | -0.46 | 48% | 90, -0.71% (-0.58) | 22, +0.21% (0.17) |
| VALUE_DOWN | found_by | control sample | 29 | +3.30% | 1.66 | 55% | 25, +3.23% (1.42) | 4, +3.77% (0.84) |
| VALUE_DOWN | found_by | keyword screen | 589 | +1.09% | 1.28 | 48% | 426, +0.89% (0.51) | 163, +1.60% (1.73) |
| VALUE_DOWN | outcome | failed | 112 | -0.53% | -0.46 | 48% | 90, -0.71% (-0.58) | 22, +0.21% (0.17) |
| VALUE_DOWN | outcome | passed | 506 | +1.57% | 1.48 | 48% | 361, +1.45% (0.74) | 145, +1.88% (1.77) |
| VALUE_DOWN | surprise | continuation | 230 | +0.86% | 0.34 | 51% | 158, +0.26% (-0.56) | 72, +2.16% (2.10) |
| VALUE_DOWN | surprise | first appearance | 388 | +1.39% | 1.14 | 47% | 293, +1.43% (0.56) | 95, +1.27% (1.21) |
| VALUE_UP | binding | binding | 130 | +1.70% | 1.30 | 48% | 63, +2.25% (1.02) | 67, +1.18% (0.86) |
| VALUE_UP | binding | signal | 90 | +3.05% | 1.95 | 56% | 47, +4.09% (2.25) | 43, +1.92% (0.44) |
| VALUE_UP | binding | unknown | 99 | -0.15% | 0.05 | 44% | 46, +0.02% (0.03) | 53, -0.31% (0.05) |
| VALUE_UP | confidence | conf<0.8 | 107 | +2.94% | 2.08 | 57% | 53, +4.26% (1.84) | 54, +1.65% (0.97) |
| VALUE_UP | confidence | conf>=0.8 | 212 | +0.78% | 0.18 | 45% | 103, +1.06% (0.17) | 109, +0.52% (0.08) |
| VALUE_UP | decisive | margin<0.8 | 102 | +3.05% | 1.68 | 50% | 46, +3.88% (0.99) | 56, +2.38% (1.67) |
| VALUE_UP | decisive | margin>=0.8 | 190 | +0.74% | 0.90 | 49% | 95, +1.67% (1.22) | 95, -0.19% (-0.23) |
| VALUE_UP | decisive | not passed | 27 | +1.05% | 0.38 | 41% | 15, -0.15% (-0.06) | 12, +2.55% (0.74) |
| VALUE_UP | found_by | control sample | 2 | -2.24% | — | 0% | 1, -1.44% (—) | 1, -3.04% (—) |
| VALUE_UP | found_by | keyword screen | 317 | +1.53% | 1.69 | 49% | 155, +2.17% (1.64) | 162, +0.92% (0.52) |
| VALUE_UP | outcome | failed | 27 | +1.05% | 0.38 | 41% | 15, -0.15% (-0.06) | 12, +2.55% (0.74) |
| VALUE_UP | outcome | passed | 292 | +1.55% | 1.56 | 50% | 141, +2.39% (1.60) | 151, +0.76% (0.32) |
| VALUE_UP | surprise | continuation | 122 | +0.25% | -0.45 | 50% | 50, -1.34% (-0.90) | 72, +1.34% (0.34) |
| VALUE_UP | surprise | first appearance | 197 | +2.28% | 2.07 | 48% | 106, +3.79% (2.02) | 91, +0.53% (0.62) |

### By year of publication (vs the basket)

| label | window | year | n | mean | median | t week |
|---|---|---|---:|---:|---:|---:|
| VALUE_UP | created..end+7d | 2021 | 13 | +1.91% | -3.33% | 0.30 |
| VALUE_UP | created..end+7d | 2022 | 33 | +3.64% | -1.49% | 1.06 |
| VALUE_UP | created..end+7d | 2023 | 64 | +1.05% | +0.16% | 1.00 |
| VALUE_UP | created..end+7d | 2024 | 95 | +1.27% | -1.08% | 0.31 |
| VALUE_UP | created..end+7d | 2025 | 77 | +0.66% | +0.99% | 0.59 |
| VALUE_UP | created..end+7d | 2026 | 37 | +2.62% | +2.25% | 1.03 |
| VALUE_UP | end+7d | 2021 | 13 | -1.06% | -0.56% | -0.26 |
| VALUE_UP | end+7d | 2022 | 33 | +2.45% | +0.40% | 1.33 |
| VALUE_UP | end+7d | 2023 | 64 | -0.23% | -0.57% | 0.20 |
| VALUE_UP | end+7d | 2024 | 95 | -0.23% | -1.08% | -0.50 |
| VALUE_UP | end+7d | 2025 | 77 | +0.50% | -0.00% | 0.30 |
| VALUE_UP | end+7d | 2026 | 37 | +1.08% | +0.69% | 0.13 |
| VALUE_DOWN | created..end+7d | 2021 | 67 | +6.18% | +0.75% | 1.55 |
| VALUE_DOWN | created..end+7d | 2022 | 109 | -1.73% | -1.38% | -1.50 |
| VALUE_DOWN | created..end+7d | 2023 | 186 | +0.70% | -0.29% | 0.95 |
| VALUE_DOWN | created..end+7d | 2024 | 155 | +1.09% | -0.22% | 0.75 |
| VALUE_DOWN | created..end+7d | 2025 | 67 | +1.65% | +0.56% | 0.85 |
| VALUE_DOWN | created..end+7d | 2026 | 34 | +2.99% | +1.63% | 1.79 |
| VALUE_DOWN | end+7d | 2021 | 67 | +1.39% | -1.54% | 0.53 |
| VALUE_DOWN | end+7d | 2022 | 109 | -0.01% | -1.45% | -0.52 |
| VALUE_DOWN | end+7d | 2023 | 186 | +0.72% | +0.33% | 1.01 |
| VALUE_DOWN | end+7d | 2024 | 155 | +0.33% | -0.14% | 0.22 |
| VALUE_DOWN | end+7d | 2025 | 67 | +0.45% | +0.21% | 0.41 |
| VALUE_DOWN | end+7d | 2026 | 34 | +2.42% | +0.91% | 1.70 |
| NEUTRAL | created..end+7d | 2021 | 117 | +0.20% | -2.67% | -0.50 |
| NEUTRAL | created..end+7d | 2022 | 204 | +1.34% | -0.06% | 1.36 |
| NEUTRAL | created..end+7d | 2023 | 301 | -0.08% | -0.86% | -0.59 |
| NEUTRAL | created..end+7d | 2024 | 301 | +0.58% | -1.12% | 0.45 |
| NEUTRAL | created..end+7d | 2025 | 249 | +1.39% | -0.14% | 1.26 |
| NEUTRAL | created..end+7d | 2026 | 93 | +3.36% | +2.76% | 2.20 |
| NEUTRAL | end+7d | 2021 | 117 | +0.22% | -1.20% | -0.35 |
| NEUTRAL | end+7d | 2022 | 204 | +1.18% | +0.01% | 1.52 |
| NEUTRAL | end+7d | 2023 | 301 | -0.37% | -1.03% | -1.16 |
| NEUTRAL | end+7d | 2024 | 301 | +0.45% | -0.15% | 0.77 |
| NEUTRAL | end+7d | 2025 | 249 | +0.93% | +0.21% | 0.73 |
| NEUTRAL | end+7d | 2026 | 93 | +2.16% | +0.37% | 1.22 |

### Largest moves (created..end+7d, vs the basket)

| token | label | created | end | outcome | first? | AR vs basket | AR vs BTC | title |
|---|---|---|---|---|---|---:|---:|---|
| FLOKI | VALUE_UP | 2024-02-29 | 2024-03-02 | passed | yes | +140.2% | +145.6% | PROPOSAL: BURN 190,918,585,431.84 FLOKI TOKENS  |
| MANA | VALUE_DOWN | 2021-10-20 | 2021-10-27 | passed | yes | +112.8% | +140.4% | Decentraland Community Building Grant |
| MANA | VALUE_DOWN | 2021-10-25 | 2021-11-01 | passed | yes | +100.3% | +117.2% | Altcoin Radio Grant |
| OM | VALUE_DOWN | 2024-03-13 | 2024-03-20 | passed | yes | +93.9% | +91.4% | Proposal: Establish a Community Staking Platform Outside MANTRA Finance |
| ZRX | VALUE_DOWN | 2024-03-06 | 2024-03-11 | passed | no | +93.1% | +96.3% | Temperature Check / [GRANT REQUEST] pZEIP-1_M2: BundleSwapFeature (31Third) |
| MANA | VALUE_DOWN | 2021-11-10 | 2021-11-17 | passed | yes | +77.1% | +87.4% | Easily manage your land's content with dclconnect |
| MANA | VALUE_DOWN | 2021-10-29 | 2021-11-05 | passed | yes | +74.5% | +88.9% | Develop a Wearable Royalty Fee Calculator |
| OGN | VALUE_UP | 2022-03-10 | 2022-03-17 | passed | yes | +65.2% | +75.5% | Launch new governance token for OUSD?  |
| GTC | VALUE_DOWN | 2021-11-22 | 2021-11-29 | passed | yes | +58.5% | +45.1% | GR12 Matching Pool Allocations |
| ONE | VALUE_DOWN | 2022-06-10 | 2022-07-01 | passed | no | -55.2% | -39.6% | MtopSwap Snapshot v2 |
| CRV | VALUE_UP | 2021-11-20 | 2021-12-31 | passed | yes | +53.8% | +57.0% | Should Curve burn some CRVs? |
| CTSI | VALUE_DOWN | 2023-04-11 | 2023-04-18 | passed | yes | +53.3% | +50.4% | New grant: Developing a decentralized painting canvas on Cartesi Rollups  |
| AAVE | VALUE_UP | 2024-12-08 | 2024-12-12 | passed | no | +50.0% | +18.6% | [ARFC] Aave Liquidity Committee Funding Phase V |
| MANA | VALUE_UP | 2021-11-09 | 2021-11-16 | passed | yes | +46.2% | +59.5% | burn 10% of MANA (Total Supply) |
| MANA | VALUE_DOWN | 2021-11-04 | 2021-11-11 | passed | no | +39.3% | +37.0% | Should we modify Blender grant to patron level support? |

## Labeling

Blind spot check: 252 proposals, agreement 99%, Cohen kappa 0.95; surprise flag agreement 89%. Keyword-only classifier vs the LLM on all 2522 candidates: agreement 57%, kappa 0.09.

LLM labels of the random control sample (proposals the screen missed): {'NEUTRAL': 199, 'VALUE_DOWN': 1, 'VALUE_UP': 0}; of the screen hits: {'NEUTRAL': 1976, 'VALUE_DOWN': 168, 'VALUE_UP': 178}.

