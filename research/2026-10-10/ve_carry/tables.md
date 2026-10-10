# ve_carry tables (generated from analysis.json; 2026-10-10T18:41:18+00:00)

## Voter economics, Aerodrome (average vote, permanent lock, rewards priced at claim + 1 day, haircut)

| year | epochs | rewards | fees | bribes | majors share | voter APR mean | median | rebase APR | AERO mean | votes mean | top-10 pools share | reward/vote dispersion | votes in pools < half avg |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 19 | $3.0M | $1.1M | $1.9M | 59.2% | 43.2% | 42.4% | 4.5% | $0.036 | 468M | 77.8% | 57.4% | 28.8% |
| 2024 | 52 | $208.9M | $107.0M | $101.9M | 69.8% | 39.1% | 37.6% | 10.1% | $0.920 | 614M | 65.6% | 39.3% | 20.4% |
| 2025 | 52 | $179.4M | $147.5M | $31.9M | 77.2% | 26.8% | 25.9% | 4.5% | $0.827 | 840M | 60.3% | 22.1% | 10.4% |
| 2026 | 40 | $51.2M | $39.9M | $11.3M | 73.2% | 15.5% | 14.9% | 2.4% | $0.443 | 989M | 54.6% | 21.1% | 6.7% |

## AERO perp funding received by a short, annualised (mean of epochs)

| year | Binance | Bybit | OKX | Hyperliquid |
|---|---:|---:|---:|---:|
| 2024 | +12.87% | -15.06% | — | — |
| 2025 | -21.87% | -14.14% | — | -6.14% |
| 2026 | -8.93% | -4.67% | +8.08% | +3.65% |

Venue used (pre-committed: Binance once listed, Bybit before): {'binance': 96, 'bybit': 20}; epochs where shorts paid: 62.9%; mean used -15.54%, last 26 epochs -3.74%.

## Hedged carry (Aerodrome, AERO perps): excess over SSR on capital (1 + 1/3 per unit of notional), weekly, annualised

Test split at 2025-08-28; chosen on the first half: **t24/$5M/best-venue**; out-of-sample rank 2 of 22; OOS Newey-West t 3.87.

| variant | in sample | out of sample | OOS t | OOS boot 95% | OOS max DD | last 52 | last 26 |
|---|---:|---:|---:|---:|---:|---:|---:|
| avg/$1M/always | +11.44% | +4.20% | 1.51 | -1.1%..+9.7% | 2.3% | +1.58% | +6.25% |
| avg/$20M/always | +10.64% | +3.74% | 1.34 | -1.6%..+9.3% | 2.6% | +1.09% | +5.83% |
| avg/$5M/always | +11.26% | +4.10% | 1.47 | -1.2%..+9.6% | 2.3% | +1.47% | +6.16% |
| avg/$5M/best-venue | +14.01% | +11.32% | 3.81 | +5.8%..+17.3% | 0.7% | +9.56% | +16.17% |
| avg/$5M/on>SSR+0pp | -60.61% | -106.45% | -2.57 | -198.4%..-30.7% | 123.8% | -121.84% | -78.18% |
| avg/$5M/on>SSR+5pp | -60.64% | -51.46% | -1.84 | -110.2%..+3.7% | 62.1% | -60.50% | -37.43% |
| prev/$1M/always | +16.48% | +4.70% | 1.86 | -0.0%..+9.6% | 1.6% | +2.45% | +7.02% |
| prev/$20M/always | +13.80% | +3.75% | 1.52 | -1.0%..+8.6% | 2.2% | +1.52% | +6.12% |
| prev/$5M/always | +15.54% | +4.51% | 1.81 | -0.2%..+9.4% | 1.8% | +2.31% | +6.82% |
| prev/$5M/on>SSR+0pp | -58.51% | -106.61% | -2.58 | -199.1%..-31.0% | 123.7% | -121.64% | -78.08% |
| prev/$5M/on>SSR+5pp | -58.64% | -51.81% | -1.86 | -110.1%..+3.3% | 62.0% | -60.51% | -37.48% |
| t1/$1M/always | +14.21% | +7.71% | 2.70 | +2.0%..+13.2% | 1.8% | +5.77% | +14.22% |
| t1/$20M/always | +13.15% | +3.61% | 1.44 | -1.2%..+8.5% | 2.3% | +1.31% | +6.10% |
| t1/$5M/always | +13.83% | +4.51% | 1.80 | -0.4%..+9.3% | 1.9% | +2.27% | +7.44% |
| t1/$5M/on>SSR+0pp | -59.58% | -106.46% | -2.58 | -198.7%..-30.8% | 123.5% | -121.51% | -77.76% |
| t1/$5M/on>SSR+5pp | -59.65% | -51.93% | -1.86 | -110.3%..+3.3% | 62.1% | -60.67% | -37.78% |
| t24/$1M/always | +13.16% | +3.72% | 1.46 | -1.4%..+8.7% | 2.3% | +1.44% | +5.84% |
| t24/$20M/always | +12.77% | +3.15% | 1.26 | -1.6%..+8.1% | 2.5% | +0.84% | +5.40% |
| t24/$5M/always | +13.30% | +3.23% | 1.27 | -1.7%..+8.2% | 2.5% | +0.92% | +5.21% |
| t24/$5M/best-venue | +16.04% | +10.44% | 3.80 | +5.1%..+15.8% | 0.8% | +9.00% | +15.22% |
| t24/$5M/on>SSR+0pp | -59.72% | -107.11% | -2.59 | -199.4%..-31.7% | 123.9% | -122.15% | -78.88% |
| t24/$5M/on>SSR+5pp | -59.77% | -52.18% | -1.87 | -110.4%..+3.0% | 62.2% | -60.88% | -38.19% |

### Inside the test window

| row | first half | t | second half | t | split | best 4 weeks / total | weeks > 0 |
|---|---:|---:|---:|---:|---|---:|---:|
| avg/$5M/always | +3.76% | 0.81 | +4.45% | 1.44 | 2026-03-19 | 62.5% | 67% |
| avg/$5M/best-venue | +9.24% | 2.46 | +13.40% | 3.14 | 2026-03-19 | 30.0% | 79% |
| t24/$5M/best-venue | +8.41% | 2.55 | +12.47% | 3.07 | 2026-03-19 | 27.0% | 79% |

### Sensitivities (not candidates in the choice)

| row | in sample | out of sample | OOS t | last 52 |
|---|---:|---:|---:|---:|
| avg/5x margin (m=0.2) | +13.16% | +5.21% | 1.63 | +2.06% |
| avg/best venue vs savings paid | +11.56% | +11.06% | 3.62 | +9.24% |
| avg/majors-only rewards | +5.38% | +0.90% | 0.36 | -1.47% |
| avg/majors-only rewards, best venue | +8.12% | +8.12% | 2.94 | +6.61% |
| avg/non-majors at 50% haircut | +9.32% | +3.11% | 1.14 | +0.45% |
| avg/non-majors at 50% haircut, best venue | +12.06% | +10.32% | 3.54 | +8.54% |

### Decomposition (annualised, on capital)

| variant | part | rewards | rebase | funding | basis | return | excess over SSR |
|---|---|---:|---:|---:|---:|---:|---:|
| avg/$5M/always | in_sample | +25.23% | +5.23% | -15.03% | -0.16% | +15.27% | +11.47% |
| avg/$5M/always | out_of_sample | +12.44% | +1.86% | -6.33% | +0.14% | +8.11% | +4.31% |
| avg/$5M/always | full | +18.83% | +3.55% | -10.68% | -0.01% | +11.69% | +7.89% |
| prev/$5M/always | in_sample | +29.50% | +5.23% | -15.03% | -0.16% | +19.54% | +15.74% |
| prev/$5M/always | out_of_sample | +12.85% | +1.86% | -6.33% | +0.14% | +8.51% | +4.71% |
| prev/$5M/always | full | +21.17% | +3.55% | -10.68% | -0.01% | +14.03% | +10.23% |
| t24/$5M/always | in_sample | +27.27% | +5.23% | -15.03% | -0.16% | +17.31% | +13.51% |
| t24/$5M/always | out_of_sample | +11.56% | +1.86% | -6.33% | +0.14% | +7.23% | +3.43% |
| t24/$5M/always | full | +19.41% | +3.55% | -10.68% | -0.01% | +12.27% | +8.47% |
| t24/$5M/best-venue | in_sample | +27.27% | +5.23% | -12.69% | +0.24% | +20.05% | +16.25% |
| t24/$5M/best-venue | out_of_sample | +11.56% | +1.86% | +1.02% | +0.00% | +14.44% | +10.64% |
| t24/$5M/best-venue | full | +19.41% | +3.55% | -5.83% | +0.12% | +17.24% | +13.44% |

### By year (avg vote, $5M, always on)

| year | rewards | rebase | funding | basis | excess |
|---|---:|---:|---:|---:|---:|
| 2024 | +28.73% | +6.72% | -8.23% | -0.28% | +23.14% |
| 2025 | +19.90% | +3.41% | -15.36% | +0.09% | +4.24% |
| 2026 | +11.51% | +1.82% | -6.08% | +0.03% | +3.48% |

## Attentive voter: reward per vote over the average vote (own dilution included)

| lock | rule | mean premium | median | APR gain | 1st half | 2nd half | last 52 | epochs > avg | pools |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $1.0M | prev | +23.8% | +17.6% | +8.25% | +15.22% | +1.37% | +1.16% | 85% | 27.6 |
| $1.0M | early | +29.4% | +10.2% | +10.74% | +21.33% | +0.29% | -0.07% | 76% | 24.9 |
| $1.0M | t24 | +20.6% | +5.9% | +7.88% | +16.06% | -0.21% | -0.18% | 67% | 22.7 |
| $1.0M | t1 | +38.3% | +9.7% | +11.41% | +18.66% | +4.26% | +5.59% | 77% | 19.4 |
| $1.0M | oracle | +99.4% | +50.5% | +27.89% | +39.94% | +15.99% | +15.60% | 100% | 27.8 |
| $1.0M | t1 − t24 | +17.65% of the average | | | | | | | |
| $5.0M | prev | +17.5% | +13.9% | +5.40% | +9.60% | +1.24% | +1.11% | 91% | 29.5 |
| $5.0M | early | +12.9% | +7.4% | +4.70% | +9.77% | -0.31% | -0.64% | 70% | 29.0 |
| $5.0M | t24 | +8.5% | +4.0% | +3.33% | +7.25% | -0.55% | -0.74% | 65% | 28.6 |
| $5.0M | t1 | +16.6% | +7.3% | +5.27% | +9.73% | +0.87% | +1.07% | 79% | 27.9 |
| $5.0M | oracle | +42.3% | +27.8% | +12.31% | +16.91% | +7.78% | +6.28% | 100% | 29.5 |
| $5.0M | t1 − t24 | +8.09% of the average | | | | | | | |
| $20.0M | prev | +10.6% | +8.8% | +2.98% | +5.33% | +0.66% | +0.56% | 89% | 29.8 |
| $20.0M | early | +7.3% | +5.6% | +2.32% | +5.00% | -0.32% | -0.39% | 78% | 29.7 |
| $20.0M | t24 | +5.2% | +4.0% | +1.80% | +3.85% | -0.23% | -0.34% | 68% | 29.9 |
| $20.0M | t1 | +10.1% | +7.7% | +2.90% | +5.60% | +0.25% | +0.29% | 84% | 30.0 |
| $20.0M | oracle | +22.9% | +15.3% | +6.62% | +8.55% | +4.71% | +2.95% | 100% | 29.8 |
| $20.0M | t1 − t24 | +4.83% of the average | | | | | | | |

Timing: rewards notified in the last 24 h 15.2% of the epoch total (last hour 0.1%); votes that moved in the last 24 h 15.7% of all votes (last hour 10.7%).

## Exit

| variant | OOS excess | break-even discount after 3 / 6 / 12 / 24 months |
|---|---:|---|
| avg/$5M/always | +4.10% | 1.0% / 2.4% / 5.1% / 10.6% |
| prev/$5M/always | +4.51% | 1.1% / 2.6% / 5.6% / 11.6% |
| t24/$5M/best-venue | +10.44% | 3.1% / 6.6% / 13.5% / 27.4% |

veNFT sales (transfer + payment in the same transaction), discount to the locked AERO at the day's price:

| slice | n | value | paid | median | p25 | p75 | value-weighted |
|---|---:|---:|---:|---:|---:|---:|---:|
| all | 2256 | $104.7M | $67.4M | 27.1% | 18.8% | 35.1% | 35.7% |
| last_365d | 769 | $28.0M | $21.8M | 16.8% | 11.9% | 21.3% | 22.1% |
| permanent_or_4y | 2168 | $102.4M | $65.7M | 27.1% | 18.8% | 35.2% | 35.9% |
| size_10k_100k | 1224 | $42.8M | $30.1M | 28.3% | 20.3% | 34.7% | 29.8% |
| size_ge_100k | 194 | $59.3M | $35.3M | 34.1% | 25.8% | 42.8% | 40.4% |
| size_lt_10k | 838 | $2.7M | $2.0M | 24.2% | 15.8% | 32.2% | 26.1% |
| year_2023 | 50 | $218k | $155k | 26.3% | 22.1% | 30.6% | 28.9% |
| year_2024 | 699 | $43.7M | $23.1M | 38.1% | 30.8% | 50.5% | 47.0% |
| year_2025 | 1049 | $45.3M | $32.1M | 26.3% | 19.8% | 31.1% | 29.2% |
| year_2026 | 458 | $15.5M | $12.0M | 15.8% | 11.0% | 20.9% | 22.8% |

| venue | n | locked value | median discount | n last 365 days | median last 365 days | paid in AERO |
|---|---:|---:|---:|---:|---:|---:|
| unverified contract 0xbddcf6ab | 1172 | $68.7M | 31.4% | 49 | 17.8% | 760 |
| VexyMarketplace (listings) 0x6b478209 | 547 | $23.4M | 17.8% | 395 | 14.9% | 516 |
| VexyOffers (bids) 0x2903ee1a | 209 | $7.4M | 23.3% | 154 | 20.9% | 209 |
| Seaport 1.6 0x00000000 | 131 | $1.0M | 22.7% | 58 | 0.3% | 2 |
|  0x047f7b05 | 23 | $701k | 19.8% | 23 | 19.8% | 23 |
|  0x21574650 | 9 | $696k | 25.8% | 9 | 25.8% | 9 |
| ERC-4337 EntryPoint 0x5ff137d4 | 27 | $390k | 15.4% | 22 | 14.1% | 21 |
|  0x80a295fd | 20 | $317k | 50.3% | 6 | 42.0% | 0 |

Entry at a discount (buy a lock at d, hedge the full underlying, exit at the same d), test-window excess over SSR:

- all_sales_last_365d, d = 16.8%: average vote, main venue +5.48%; best venue +13.50%
- vexy_listings_last_365d, d = 14.9%: average vote, main venue +5.32%; best venue +13.21%
- vexy_offers_last_365d, d = 20.9%: average vote, main venue +5.81%; best venue +14.12%

iAERO (liquid permanently locked veAERO; minted at 0.95 per AERO): price/AERO last 0.754 (2026-10-09), 90-day mean 0.725, range 0.569..1.117 since 2025-11-26; exit cost by minting and selling now 28.3%; pools [{'name': 'iAERO / AERO', 'reserve_usd': 45094.9356, 'volume_24h_usd': 0.0}].

## Capacity (books read 2026-10-10 17:05)

| venue | OI | 24h volume | bids within 0.5% / 1% / 2% | asks within 1% | funding now (ann.) |
|---|---:|---:|---|---:|---:|
| binance | $47.1M | $42.1M | $166k / $373k / $608k | $314k | +10.95% |
| bybit | $30.6M | $15.2M | $131k / $204k / $438k | $178k | +10.95% |
| okx | $3.3M | — | $48k / $112k / $165k | $92k | — |
| hl | $36.1M | $6.9M | $60k / $179k / $427k | $200k | +10.95% |
| bybit_spot | — | — | $28k / $41k / $47k | $22k | — |
| coinbase_spot | — | — | $164k / $321k / $401k | $231k | — |

Total AERO perp OI: $117.2M. Binance VELODROMEUSDT: {'ask_0.5pct': 17338.36696, 'ask_1pct': 34984.94008, 'ask_2pct': 55939.61873, 'bid_0.5pct': 11351.50862, 'bid_1pct': 28038.05864, 'bid_2pct': 66414.59995, 'funding_now': 5e-05, 'oi_usd': 9563519.916271, 'vol24h_usd': 5180015.35913}.

## Live (epoch 2026-10-08, 2026-10-10 17:05)

- fees known $1.4M, bribes so far $2k, votes 1014M, AERO $0.830: indicative voter APR so far 8.8% (bribes still arriving)
- locked 1054M AERO, 94.0% of it permanent; epochs left before the merger: 2

## Checks

- events vs storage: {'epochs': [1716422400, 1747872000, 1784160000], 'exact_matches': 2704, 'examples_mismatch': [['0x809909eb457495ab29cfdd0ae966796f5aad5ec1', '0x36be1d329444aef5d28df3662ec5b4f965cd93e9', 1747872000, 1000000000000000, 0], ['0xb03bf648ef64cef67b5a80ad12893d669ce7df8e', '0x940181a94a35a4569e4529a3cdfb74e38fd98631', 1747872000, 100000000000000000, 0], ['0x2984d568756c923e5ecc7cf6cc02ea46b7a48b24', '0x36be1d329444aef5d28df3662ec5b4f965cd93e9', 1747872000, 1000000000000000, 0]], 'keys': 2707, 'only_in_events': 3, 'only_in_storage': 0}
- Sugar vs storage: {'pools': 6, 'reward_exact': 144, 'reward_items': 144, 'vote_epochs': 60, 'vote_exact': 60}

| quarter | fees (ours, Base, haircut) | bribes (ours, haircut) | gross, Base + Optimism | aero.xyz revenue (all chains) | ratio |
|---|---:|---:|---:|---:|---:|
| 2023Q3 | $370k | $785k | $6.6M | $12.9M | 0.51 |
| 2023Q4 | $758k | $1.1M | $5.7M | $6.4M | 0.89 |
| 2024Q1 | $7.6M | $10.5M | $25.7M | $30.7M | 0.84 |
| 2024Q2 | $18.8M | $34.6M | $67.0M | $78.5M | 0.85 |
| 2024Q3 | $17.7M | $26.8M | $54.7M | $57.7M | 0.95 |
| 2024Q4 | $62.9M | $29.9M | $106.1M | $111.2M | 0.95 |
| 2025Q1 | $51.9M | $9.0M | $68.2M | $71.8M | 0.95 |
| 2025Q2 | $30.5M | $4.9M | $39.0M | $40.6M | 0.96 |
| 2025Q3 | $37.6M | $13.0M | $56.3M | $63.6M | 0.89 |
| 2025Q4 | $27.4M | $5.1M | $35.8M | $38.6M | 0.93 |
| 2026Q1 | $13.6M | $3.7M | $19.1M | $20.5M | 0.93 |
| 2026Q2 | $10.4M | $3.8M | $15.7M | $16.4M | 0.96 |
| 2026Q3 | $14.3M | $3.6M | $20.2M | $25.8M | 0.78 |
| 2026Q4 | $1.6M | $208k | — | — | — |

## Velodrome (Optimism), average vote

| year | rewards | fees | bribes | voter APR mean | median | rebase APR | VELO mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023 | $8.5M | $2.3M | $6.2M | 32.4% | 31.5% | 15.0% | $0.0665 |
| 2024 | $26.9M | $12.8M | $14.1M | 28.7% | 25.5% | 4.6% | $0.1079 |
| 2025 | $9.2M | $7.4M | $1.8M | 20.7% | 20.1% | 2.1% | $0.0569 |
| 2026 | $2.2M | $1.6M | $613k | 17.5% | 16.4% | 2.0% | $0.0186 |

VELODROMEUSDT (Binance) funding to a short by year: {'2024': '+2.75%', '2025': '+0.68%', '2026': '+11.29%'}; mean +5.17%, last 26 epochs +11.55%.

## Hedged carry (Velodrome, Binance VELODROMEUSDT): excess over SSR on capital (1 + 1/3 per unit of notional), weekly, annualised

Test split at 2025-11-13; chosen on the first half: **prev/$1M/always**; out-of-sample rank 3 of 22; OOS Newey-West t 26.95.

| variant | in sample | out of sample | OOS t | OOS boot 95% | OOS max DD | last 52 | last 26 |
|---|---:|---:|---:|---:|---:|---:|---:|
| avg/$1M/always | +10.90% | +18.55% | 25.73 | +17.1%..+19.9% | 0.0% | +14.53% | +17.63% |
| avg/$20M/always | +6.31% | +11.95% | 20.04 | +10.7%..+13.2% | 0.1% | +7.83% | +11.87% |
| avg/$5M/always | +9.59% | +16.12% | 25.69 | +14.8%..+17.3% | 0.0% | +12.09% | +15.55% |
| avg/$5M/best-venue | +9.81% | +16.18% | 35.72 | +15.3%..+17.0% | 0.0% | +12.18% | +15.88% |
| avg/$5M/on>SSR+0pp | -2.98% | +14.45% | 10.15 | +11.7%..+16.7% | 0.0% | +10.59% | +15.55% |
| avg/$5M/on>SSR+5pp | -2.98% | +14.45% | 10.15 | +11.7%..+16.7% | 0.0% | +10.59% | +15.55% |
| prev/$1M/always | +13.36% | +20.03% | 27.29 | +18.6%..+21.4% | 0.0% | +16.10% | +19.13% |
| prev/$20M/always | +6.66% | +11.71% | 19.55 | +10.5%..+12.9% | 0.1% | +7.57% | +11.70% |
| prev/$5M/always | +11.07% | +16.44% | 26.62 | +15.2%..+17.7% | 0.0% | +12.44% | +15.90% |
| prev/$5M/on>SSR+0pp | -1.69% | +14.71% | 10.38 | +11.9%..+16.9% | 0.0% | +10.88% | +15.90% |
| prev/$5M/on>SSR+5pp | -1.69% | +14.71% | 10.38 | +11.9%..+16.9% | 0.0% | +10.88% | +15.90% |
| t1/$1M/always | +12.99% | +19.80% | 25.63 | +18.3%..+21.3% | 0.0% | +15.95% | +18.96% |
| t1/$20M/always | +7.00% | +12.04% | 20.08 | +10.8%..+13.2% | 0.1% | +7.94% | +11.98% |
| t1/$5M/always | +11.22% | +16.82% | 26.98 | +15.6%..+18.0% | 0.0% | +12.89% | +16.21% |
| t1/$5M/on>SSR+0pp | -1.54% | +15.06% | 10.37 | +12.2%..+17.3% | 0.0% | +11.30% | +16.21% |
| t1/$5M/on>SSR+5pp | -1.54% | +15.06% | 10.37 | +12.2%..+17.3% | 0.0% | +11.30% | +16.21% |
| t24/$1M/always | +12.52% | +19.23% | 26.35 | +17.8%..+20.6% | 0.0% | +15.38% | +18.31% |
| t24/$20M/always | +6.77% | +11.66% | 19.07 | +10.4%..+12.9% | 0.1% | +7.57% | +11.58% |
| t24/$5M/always | +10.85% | +16.33% | 25.90 | +15.0%..+17.6% | 0.0% | +12.39% | +15.68% |
| t24/$5M/best-venue | +11.08% | +16.39% | 35.60 | +15.5%..+17.2% | 0.0% | +12.48% | +16.01% |
| t24/$5M/on>SSR+0pp | -1.88% | +14.59% | 10.32 | +11.8%..+16.7% | 0.0% | +10.82% | +15.68% |
| t24/$5M/on>SSR+5pp | -1.88% | +14.59% | 10.32 | +11.8%..+16.7% | 0.0% | +10.82% | +15.68% |

### Inside the test window

| row | first half | t | second half | t | split | best 4 weeks / total | weeks > 0 |
|---|---:|---:|---:|---:|---|---:|---:|
| avg/$5M/always | +16.91% | 29.19 | +15.37% | 15.36 | 2026-04-23 | 16.3% | 100% |
| avg/$5M/best-venue | +16.50% | 33.82 | +15.88% | 22.34 | 2026-04-23 | 12.0% | 100% |
| prev/$1M/always | +21.25% | 30.87 | +18.85% | 18.09 | 2026-04-23 | 15.0% | 100% |

### Sensitivities (not candidates in the choice)

| row | in sample | out of sample | OOS t | last 52 |
|---|---:|---:|---:|---:|
| avg/5x margin (m=0.2) | +11.35% | +18.61% | 25.93 | +14.11% |
| avg/best venue vs savings paid | +8.27% | +16.26% | 38.61 | +12.09% |
| avg/majors-only rewards | +9.95% | +17.63% | 24.91 | +13.55% |
| avg/majors-only rewards, best venue | +10.17% | +17.70% | 35.52 | +13.64% |
| avg/non-majors at 50% haircut | +10.93% | +18.88% | 25.35 | +14.81% |
| avg/non-majors at 50% haircut, best venue | +11.16% | +18.94% | 34.00 | +14.89% |

### Decomposition (annualised, on capital)

| variant | part | rewards | rebase | funding | basis | return | excess over SSR |
|---|---|---:|---:|---:|---:|---:|---:|
| avg/$5M/always | in_sample | +14.12% | +1.61% | -1.86% | -0.23% | +13.64% | +9.84% |
| avg/$5M/always | out_of_sample | +10.13% | +1.50% | +8.60% | -0.06% | +20.17% | +16.37% |
| avg/$5M/always | full | +12.13% | +1.55% | +3.37% | -0.14% | +16.90% | +13.10% |
| prev/$1M/always | in_sample | +17.89% | +1.61% | -1.86% | -0.23% | +17.41% | +13.61% |
| prev/$1M/always | out_of_sample | +14.04% | +1.50% | +8.60% | -0.06% | +24.08% | +20.28% |
| prev/$1M/always | full | +15.97% | +1.55% | +3.37% | -0.14% | +20.74% | +16.94% |
| prev/$5M/always | in_sample | +15.60% | +1.61% | -1.86% | -0.23% | +15.12% | +11.32% |
| prev/$5M/always | out_of_sample | +10.45% | +1.50% | +8.60% | -0.06% | +20.49% | +16.69% |
| prev/$5M/always | full | +13.02% | +1.55% | +3.37% | -0.14% | +17.80% | +14.00% |
| t24/$5M/always | in_sample | +15.38% | +1.61% | -1.86% | -0.23% | +14.90% | +11.10% |
| t24/$5M/always | out_of_sample | +10.34% | +1.50% | +8.60% | -0.06% | +20.38% | +16.58% |
| t24/$5M/always | full | +12.86% | +1.55% | +3.37% | -0.14% | +17.64% | +13.84% |

### By year (avg vote, $5M, always on)

| year | rewards | rebase | funding | basis | excess |
|---|---:|---:|---:|---:|---:|
| 2024 | +18.36% | +1.79% | -0.89% | -1.08% | +14.38% |
| 2025 | +13.63% | +1.58% | -0.54% | +0.01% | +10.87% |
| 2026 | +9.86% | +1.51% | +8.66% | -0.29% | +15.94% |

| Velodrome lock | rule | mean premium | APR gain | 2nd half |
|---|---|---:|---:|---:|
| $1.0M | prev | +18.3% | +4.45% | +2.56% |
| $1.0M | early | +21.8% | +6.40% | +1.90% |
| $1.0M | t24 | +20.5% | +6.08% | +1.59% |
| $1.0M | t1 | +37.9% | +11.78% | +2.29% |
| $5.0M | prev | +11.0% | +2.61% | +1.06% |
| $5.0M | early | +13.2% | +3.26% | +1.20% |
| $5.0M | t24 | +12.7% | +3.25% | +0.94% |
| $5.0M | t1 | +21.2% | +5.50% | +1.52% |
| $20.0M | prev | +0.9% | +0.25% | -0.03% |
| $20.0M | early | +3.9% | +0.84% | +0.29% |
| $20.0M | t24 | +1.3% | +0.47% | +0.03% |
| $20.0M | t1 | +9.1% | +1.88% | +0.46% |

- Velodrome checks: {'events_vs_storage': {'epochs': [1716422400, 1747872000, 1784160000], 'exact_matches': 1337, 'examples_mismatch': [['0xf75b7ac406d90622eedbacc51d8487352e5aa207', '0x9560e827af36c94d2ac33a39bce1fe78631088db', 1716422400, 5000000000000000000, 0]], 'keys': 1338, 'only_in_events': 1, 'only_in_storage': 0}, 'reward_reads': 456481, 'reward_reads_failed': 0, 'sugar_vs_storage': {'pools': 6, 'reward_exact': 134, 'reward_items': 134, 'vote_epochs': 60, 'vote_exact': 60}, 'votes_reread_sample': {'failed_rereads': 0, 'mismatches': 0, 'sampled': 20000, 'stored_nulls_in_sample': 0, 'stored_nulls_total': 0}}
