# Pendle fixed vs floating — tables

Generated 2026-10-09T20:50:03+00:00 from `analysis.json`; last data day 2026-10-09; choose/test cutoff 2025-09-01 (median expiry of matured markets that ever held $1M of pool TVL, first of that month); size $100k per trade through the AMM; pool TVL at entry >= $1.0M; median hold 77 days; 59 strategy variants tried in total.

## Universe

1033 markets (916 matured, 117 active). Listing: {"active": 85, "asset_list_only": 219, "inactive": 729}. History status: {"200": 910, "404": 123}. Metadata status: {"200": 910, "404": 123}.

Blocked by the API ("market is unsafe"): 123 markets.

## Identities

| check | n | median | p90 |
|---|---:|---:|---:|
| pool_tvl_identity_rel_err | 73995 | 0.00000 | 0.00000 |
| usd_pt_price_identity_abs_err | 19630 | 0.00032 | 0.00236 |
| usd_sy_growth_vs_interest_apy_abs_err_30d | 985 | 0.00510 | 0.03800 |

## Benchmark

Sky savings rate from Pendle sUSDS/sDAI markets: 1406 days, 2022-12-04 to 2026-10-09, now 3.80%.

## Recovery at maturity

All matured: {"default": 71, "no_price": 203, "no_price_at_maturity": 109, "ok": 442, "ok_unanchored": 39, "unmapped": 52}. Dollar markets that ever held $1M: {"default": 6, "no_price": 23, "no_price_at_maturity": 56, "ok": 211, "ok_unanchored": 25, "unmapped": 13}.

| market | protocol | class | expiry | max pool TVL | recovery | first break | source |
|---|---|---|---|---:|---:|---|---|
| apxUSD | APYX | stable | 2026-06-18 | $32.0M | 0.970 | - | llama:ethereum:0x98a878b1cd98131b271883b390f68d2c90674665 |
| RLP | Resolv | stable | 2026-04-09 | $8.9M | 0.741 | 2026-04-03 | llama:ethereum:0x4956b52ae2ff65d74ca2d61207523288e4528f96 |
| eUSD | Lybra | stable | 2024-12-26 | $5.6M | 0.921 | 2024-04-13 | llama:ethereum:0xdf3ac4f479375802a821f7b7b46cd7eb5e4262cc |
| YU | Yala | stable | 2025-12-04 | $4.0M | 0.979 | 2025-09-14 | llama:ethereum:0xe868084cf08f3c3db11f4b73a95473762d9463f7 |
| YU | Yala | stable | 2025-12-04 | $1.6M | 0.965 | 2025-09-15 | llama:base:0xe868084cf08f3c3db11f4b73a95473762d9463f7 |
| msUSD | Main Street Finance | stable | 2026-07-30 | $1.6M | 0.969 | 2026-06-25 | llama:ethereum:0x4ba01f22827018b4772cd326c7627fb4956a7c00 |
| USDX | usdx.money | stable | 2026-03-26 | $356k | 0.011 | 2025-11-06 | llama:base:0xf3527ef8de265eaa3716fb312c12847bfba66cef |
| wstUSR | Resolv | stable | 2026-06-25 | $306k | 0.889 | 2026-04-03 | llama:ethereum:0x1202f5c7b4b9e47a1a484e8b270be34dbbc75055 |

### Dollar markets whose PT holders lost more than 2% (from the trade panel)

| market | protocol | expiry | max pool TVL | trades | recovery (min / max) | yield-token ratio | accounting move (source) | API / market reading | first break | spread at entry |
|---|---|---|---:|---:|---|---:|---|---|---|---|
| sUSDX | usdx.money | 2026-03-26 | $28.2M | 19 | 0.011 / 0.273 | 1.000 | 0.011 (market) | 0.011 / 0.011 | 2025-11-05 | 3.7% to 5.3% |
| YU | Yala | 2025-12-04 | $1.6M | 2 | 0.265 / 0.265 | 0.965 | 0.275 (api) | 0.275 / 0.265 | 2025-09-14 | 6.6% to 8.8% |
| YU | Yala | 2025-12-04 | $4.0M | 2 | 0.269 / 0.269 | 0.979 | 0.275 (api) | 0.275 / 0.269 | 2025-09-14 | 5.3% to 5.8% |
| RLP | Resolv | 2026-04-09 | $8.9M | 15 | 0.328 / 0.329 | 0.741 | 0.442 (api) | 0.442 / 1.000 | 2026-03-22 | 2.3% to 6.2% |
| msUSD | Main Street Finance | 2026-07-30 | $1.6M | 10 | 0.330 / 0.330 | 0.969 | 0.340 (api) | 0.340 / 0.329 | 2026-06-20 | 2.9% to 4.6% |
| jrUSDat | Strata | 2026-08-27 | $2.7M | 3 | 0.461 / 0.490 | 1.000 | 0.461 (api) | 0.461 / 0.999 | 2026-05-28 | 9.0% to 12.3% |
| apxUSD | APYX | 2026-06-18 | $32.0M | 12 | 0.876 / 0.913 | 0.970 | 0.903 (api) | 0.903 / - | 2026-06-03 | 7.4% to 14.6% |
| eUSD | Lybra | 2024-12-26 | $5.6M | 10 | 0.883 / 0.962 | 0.921 | 0.958 (api) | 0.958 / 0.945 | 2024-04-13 | -7.2% to 1.9% |
| apyUSD | APYX | 2026-06-18 | $15.9M | 14 | 0.904 / 0.942 | 1.000 | 0.904 (api) | 0.904 / - | 2026-06-03 | 9.2% to 20.6% |
| USD0++ | Usual | 2025-06-26 | $23.0M | 25 | 0.922 / 0.978 | 1.000 | 0.922 (api) | 0.922 / - | 2025-01-10 | 4.5% to 16.7% |
| USD0++ | Usual | 2025-01-30 | $47.9M | 7 | 0.931 / 0.944 | 1.000 | 0.931 (api) | 0.931 / - | 2025-01-10 | 18.4% to 36.4% |
| USD0++ | Usual | 2025-02-27 | $13.5M | 5 | 0.936 / 0.950 | 1.000 | 0.936 (api) | 0.936 / - | 2025-01-10 | 11.4% to 27.9% |
| apxUSD | APYX | 2026-06-18 | $3.8M | 8 | 0.938 / 0.939 | 1.000 | 0.938 (api) | 0.938 / - | 2026-06-03 | 7.8% to 12.2% |
| USDai | USD.ai | 2026-03-19 | $48.2M | 2 | 0.951 / 0.958 | 1.000 | 0.951 (api) | 0.951 / 0.963 | - | 24.1% to 24.8% |
| sUSDai | USD.AI | 2026-03-19 | $22.3M | 2 | 0.951 / 0.958 | 1.000 | 0.951 (api) | 0.951 / 0.963 | - | 20.0% to 24.0% |
| USDai | USD.ai | 2025-11-20 | $141.8M | 2 | 0.951 / 0.958 | 1.000 | 0.951 (api) | 0.951 / 0.961 | - | 39.0% to 43.3% |
| sYUSD | Aegis | 2025-12-18 | $10.9M | 1 | 0.953 / 0.953 | 1.000 | 0.953 (market) | 0.999 / 0.953 | - | 10.1% to 10.1% |
| sUSDai | USD.AI | 2025-11-20 | $77.5M | 2 | 0.954 / 0.961 | 1.000 | 0.954 (api) | 0.954 / 0.961 | - | 31.0% to 40.8% |
| USD0++ | Usual | 2025-03-27 | $88.7M | 13 | 0.956 / 0.970 | 1.000 | 0.956 (api) | 0.956 / - | - | 5.7% to 23.4% |
| USD0++ | Usual | 2025-04-24 | $13.3M | 4 | 0.963 / 0.977 | 1.000 | 0.963 (api) | 0.963 / - | - | 7.9% to 22.1% |
| USD0++ | Usual | 2025-11-27 | $5.9M | 2 | 0.969 / 0.970 | 1.000 | 0.969 (api) | 0.969 / - | - | 5.3% to 5.6% |
| sUSDz | Anzen  | 2025-09-25 | $2.6M | 3 | 0.977 / 0.979 | 1.000 | 0.977 (api) | 0.977 / 0.997 | - | 5.5% to 5.8% |

Accounting-asset move, API reading against market reading, on 2877 dollar trades where both exist: median absolute difference 0.0006, p90 0.0035, 95% within 1%. Source used: market 495, API 3516.

## Markets the API blocks

123 markets answer "market is unsafe"; 69 have transactions. PT bought in them: $12.9M (the served panel traded $94121.8M in total). Matured dollar markets among them: 53, with $537k of PT bought, $400k of it priced; USD-weighted realised excess over the savings rate of those purchases: -100.91%.

| market | class | expiry | tx | PT bought | priced | implied (USD-wtd) | min recovery | excess vs SSR (USD-wtd) | yield token prices |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LP agETH | eth | 2024-12-26 | 95 | $6.2M | $0 | - | - | - | 135 |
| LP KS2-RT (KS2-RT) | other | 2024-03-28 | 794 | $5.1M | $0 | - | - | - | 0 |
| LP sMNT | other | 2024-10-03 | 219 | $1.1M | $0 | - | 0.913 | - | 422 |
| LP sdeUSD (deUSD) | stable | 2025-12-11 | 313 | $399k | $399k | 8.98% | 0.001 | -101.06% | 206 |
| LP gDAI | stable | 2025-03-27 | 87 | $137k | $0 | - | - | - | 422 |
| LP pumpBTC | btc | 2025-05-29 | 6 | $44k | $0 | - | - | - | 44 |
| LP sNUSD (NUSD) | stable | 2026-03-05 | 6 | $601 | $601 | 1.60% | 0.974 | -3.37% | 44 |
| LP stOBOL (OBOL) | other | 2025-11-06 | 11 | $293 | $0 | - | - | - | 0 |
| LP ARB-ETH CMLP (ARB-ETH CMLP) | eth | 2024-06-27 | 6 | $233 | $0 | - | - | - | 422 |
| LP cUSDO | stable | 2025-06-19 | 3 | $1 | $1 | 1.78% | 0.956 | -5.03% | 143 |
| LP slvlUSD (lvlUSD) | stable | 2026-03-26 | 9 | $1 | $0 | - | - | - | 255 |
| LP sNUSD (NUSD) | stable | 2026-01-29 | 4 | $0 | $0 | - | - | - | 44 |
| LP slvlUSD | stable | 2025-09-25 | 2 | $0 | $0 | 1.04% | 0.955 | -6.10% | 255 |
| LP aGHO (GHO) | stable | 2025-12-18 | 4 | $0 | $0 | - | - | - | 109 |
| LP gDAI | stable | 2024-12-26 | 5 | $0 | $0 | 5.88% | 1.000 | -0.05% | 422 |
| LP sfPEPE | other | 2024-12-26 | 5 | $0 | $0 | - | - | - | 422 |
| LP sdeUSD (sdeUSD) | stable | 2025-12-11 | 2 | $0 | $0 | - | - | - | 206 |
| LP loAZND (AZND) | other | 2026-07-02 | 2 | $0 | $0 | - | - | - | 105 |
| LP STRCx (STRCx) | other | 2026-11-26 | 2 | $0 | $0 | - | - | - | 270 |
| LP TEST (TEST) | other | 2026-07-30 | 0 | $0 | $0 | - | - | - | 0 |
| LP USD (Midas mEDGE) (USD (Midas mEDGE)) | stable | 2026-01-29 | 0 | $0 | $0 | - | - | - | 232 |
| LP USDS | stable | 2025-07-31 | 1 | $0 | $0 | - | - | - | 330 |
| LP eACRED (USDC) | stable | 2026-07-02 | 0 | $0 | $0 | - | - | - | 0 |
| LP sUSDD (USDD) | stable | 2026-08-13 | 2 | $0 | $0 | - | - | - | 322 |
| LP nBASIS (USDC) | stable | 2026-01-29 | 0 | $0 | $0 | - | - | - | 287 |

## Dollar trades by protocol (per trade, annualised, after defaults)

| protocol | trades | markets | defaulted | promised spread | realised excess | worst trade | first entry | last expiry |
|---|---:|---:|---:|---:|---:|---:|---|---|
| Ethena | 553 | 42 | 0 | 5.85% | 5.85% | -3.85% | 2024-02-29 | 2026-08-13 |
| Aave | 153 | 16 | 0 | 0.42% | 0.46% | -5.08% | 2023-12-14 | 2026-05-28 |
| Gains Network | 152 | 5 | 0 | 2.73% | 2.73% | -6.65% | 2023-03-16 | 2025-12-18 |
| Resolv | 141 | 11 | 1 | 3.48% | -31.52% | -1170.52% | 2024-12-26 | 2026-04-09 |
| Midas | 135 | 12 | 0 | 5.93% | 5.93% | -3.79% | 2025-04-24 | 2026-09-24 |
| Strata | 126 | 12 | 1 | 4.11% | -4.07% | -202.31% | 2025-07-31 | 2026-09-17 |
| Usual | 122 | 7 | 6 | 8.78% | 0.90% | -81.94% | 2024-08-08 | 2025-11-27 |
| Cap | 92 | 4 | 0 | 3.55% | 3.55% | -1.87% | 2025-08-21 | 2026-07-23 |
| Falcon Finance | 85 | 4 | 0 | 5.06% | 5.06% | -1.14% | 2025-04-24 | 2026-06-18 |
| Upshift Finance | 71 | 4 | 0 | 3.72% | 3.72% | -0.64% | 2025-04-03 | 2026-04-30 |
| Spark | 67 | 4 | 0 | -0.26% | -0.26% | -8.49% | 2023-09-07 | 2025-12-18 |
| Silo | 66 | 4 | 0 | 4.09% | 4.09% | -4.20% | 2023-10-12 | 2025-08-14 |
| Level | 64 | 4 | 0 | 3.96% | 3.96% | -2.51% | 2025-02-27 | 2025-09-25 |
| InfiniFi | 62 | 6 | 0 | 5.72% | 5.72% | 0.76% | 2025-06-12 | 2026-03-26 |
| USD.AI | 62 | 4 | 2 | 10.49% | 8.30% | -9.49% | 2025-08-28 | 2026-06-18 |
| Neutrl | 60 | 5 | 0 | 3.99% | 3.99% | -2.84% | 2025-11-20 | 2026-09-24 |
| re.xyz | 60 | 3 | 0 | 6.40% | 6.49% | 3.02% | 2025-10-16 | 2026-06-25 |
| Saturn | 60 | 5 | 0 | 6.28% | 27.84% | 1.36% | 2026-04-16 | 2026-08-27 |
| Noon Capital | 56 | 4 | 0 | 3.42% | 3.42% | 0.03% | 2025-06-05 | 2026-07-30 |
| Aegis | 56 | 5 | 1 | 2.34% | 1.85% | -10.26% | 2025-05-15 | 2026-09-24 |
| OpenEden | 55 | 3 | 0 | 2.78% | 2.78% | -0.56% | 2025-04-10 | 2026-05-28 |
| USD.ai | 55 | 4 | 2 | 9.52% | 6.73% | -6.25% | 2025-08-28 | 2026-06-18 |
| Midas  | 52 | 4 | 0 | 4.23% | 4.23% | 1.60% | 2025-09-04 | 2026-09-24 |
| Avalon Finance | 51 | 3 | 0 | 1.31% | 1.31% | -0.25% | 2025-01-30 | 2025-12-18 |
| Karak | 48 | 3 | 0 | 7.18% | 7.18% | -3.19% | 2024-05-30 | 2025-01-30 |
| GAIB | 48 | 6 | 0 | 8.77% | 8.77% | 3.05% | 2025-06-05 | 2026-01-29 |
| APYX | 48 | 5 | 3 | 8.73% | -13.15% | -215.16% | 2026-03-05 | 2026-08-27 |
| Stargate | 46 | 2 | 0 | -4.05% | -4.05% | -5.84% | 2023-05-25 | 2024-06-27 |
| Superform | 45 | 5 | 0 | 3.65% | 3.65% | -3.42% | 2025-02-20 | 2026-04-30 |
| Syrup.Fi | 45 | 3 | 0 | 3.69% | 3.69% | -2.68% | 2024-10-17 | 2025-08-28 |
| Reservoir | 44 | 4 | 0 | 3.76% | 3.76% | -0.38% | 2025-04-17 | 2025-10-30 |
| usdx.money | 44 | 2 | 1 | 2.84% | -122.40% | -348.93% | 2025-03-03 | 2026-03-26 |
| Fluid | 42 | 4 | 0 | 2.44% | 2.44% | -1.29% | 2025-02-13 | 2026-02-26 |
| Yearn | 42 | 3 | 0 | 4.42% | 4.45% | -3.21% | 2025-05-08 | 2026-01-29 |
| f(x) Protocol | 39 | 2 | 0 | 3.00% | 3.00% | -2.01% | 2025-04-17 | 2026-04-30 |
| Hyperbeat | 39 | 4 | 0 | 8.12% | 8.12% | 1.86% | 2025-07-31 | 2026-01-22 |
| Trevee | 38 | 3 | 0 | 3.09% | 3.09% | -0.03% | 2025-02-27 | 2026-01-29 |
| Avant Protocol | 35 | 3 | 0 | 4.07% | 4.07% | 1.86% | 2026-01-15 | 2026-08-06 |
| Mellow | 34 | 2 | 0 | 6.35% | 6.35% | -3.84% | 2024-07-11 | 2025-03-27 |
| Astherus | 34 | 3 | 0 | 3.01% | 3.01% | -2.70% | 2025-02-27 | 2025-11-27 |

### (a) PT minus floating, by class

Chosen in sample: **ethena** (of 9 variants; out-of-sample rank 3; deflated Sharpe of the in-sample choice 1.000).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| all | 3.15% | 2.48 | 4613 | 2.34% | 6.00 | 0.34% | 3.52 | 1.17% to 3.54% | 3202 | 2.58% | 1.41% | 76% | yes |
| btc | 1.33% | 2.11 | 495 | 1.05% | 5.22 | 0.08% | 4.71 | 0.58% to 1.51% | 206 | 1.07% | 0.98% | 93% | yes |
| eth | 0.49% | 0.37 | 2082 | -0.44% | -0.96 | 0.98% | -0.60 | -1.97% to 0.61% | 540 | 0.12% | 0.09% | 57% | no |
| ethena | 7.99% | 3.79 | 458 | 2.30% | 6.01 | 0.17% | 2.17 | 0.60% to 4.44% | 293 | 2.37% | 1.40% | 81% | yes |
| hype | 0.00% | - | 0 | 1.43% | 1.93 | 0.47% | 1.75 | 0.13% to 3.30% | 202 | 2.18% | 1.14% | 77% | no |
| no_points | 2.86% | 2.36 | 1870 | 1.19% | 1.66 | 1.30% | 0.89 | -1.47% to 3.40% | 719 | 2.11% | 0.99% | 68% | no |
| other | 10.28% | 1.97 | 538 | 5.88% | 3.86 | 2.36% | 1.82 | -0.62% to 11.97% | 269 | 8.47% | 5.13% | 81% | no |
| points | 5.37% | 1.91 | 2743 | 2.50% | 7.42 | 0.17% | 4.30 | 1.41% to 3.71% | 2483 | 2.74% | 1.53% | 79% | yes |
| stable | 1.76% | 1.24 | 1040 | 3.03% | 7.94 | 0.18% | 4.94 | 1.90% to 4.25% | 1692 | 3.45% | 2.49% | 79% | yes |

Chosen variant out of sample, by class: ethena 293 trades, pooled 2.37%, median 1.40%, 81% positive.

### (b) PT when implied exceeds trailing-7d floating

Chosen in sample: **spread>=500bp** (of 8 variants; out-of-sample rank 2; deflated Sharpe of the in-sample choice 1.000).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| all | 3.15% | 2.48 | 4613 | 2.34% | 6.00 | 0.34% | 3.52 | 1.17% to 3.54% | 3202 | 2.58% | 1.41% | 76% | yes |
| spread>=0bp | 4.97% | 2.88 | 4006 | 2.97% | 8.44 | 0.18% | 4.48 | 1.79% to 4.21% | 2729 | 3.22% | 1.92% | 82% | yes |
| spread>=100bp | 5.93% | 3.03 | 3498 | 3.83% | 9.86 | 0.18% | 5.34 | 2.52% to 5.21% | 2138 | 4.41% | 3.04% | 89% | yes |
| spread>=1200bp | 14.44% | 2.73 | 877 | 12.31% | 12.04 | 0.65% | 5.81 | 8.62% to 16.75% | 282 | 16.81% | 13.17% | 100% | yes |
| spread>=200bp | 6.98% | 3.30 | 3018 | 4.64% | 10.55 | 0.21% | 5.86 | 3.17% to 6.18% | 1684 | 5.41% | 4.49% | 92% | yes |
| spread>=300bp | 6.92% | 2.97 | 2665 | 5.40% | 11.64 | 0.22% | 6.36 | 3.84% to 7.09% | 1403 | 6.41% | 5.34% | 94% | yes |
| spread>=500bp | 9.49% | 3.54 | 2049 | 7.09% | 13.41 | 0.24% | 7.11 | 5.29% to 9.10% | 1004 | 8.44% | 6.75% | 96% | yes |
| spread>=800bp | 11.10% | 2.18 | 1343 | 9.53% | 14.37 | 0.39% | 7.76 | 7.36% to 12.10% | 548 | 11.77% | 10.03% | 98% | yes |

Chosen variant out of sample, by class: btc 1 trades, pooled 3.79%, median 3.79%, 100% positive; eth 22 trades, pooled 6.08%, median 6.83%, 100% positive; ethena 82 trades, pooled 6.66%, median 6.14%, 100% positive; hype 49 trades, pooled 6.17%, median 5.88%, 100% positive; other 152 trades, pooled 14.85%, median 11.88%, 92% positive; stable 698 trades, pooled 7.15%, median 6.44%, 96% positive.

### (c) YT (interest only) when floating exceeds implied, against the savings rate

Chosen in sample: **yt>=100bp** (of 5 variants; out-of-sample rank 3; deflated Sharpe of the in-sample choice 0.000).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| yt>=0bp | -38.41% | -1.08 | 500 | -112.83% | -5.99 | 124.88% | -7.58 | -143.00% to -85.06% | 451 | -89.07% | -95.38% | 9% | yes |
| yt>=100bp | -27.50% | -0.99 | 234 | -112.41% | -4.62 | 124.42% | -5.47 | -150.92% to -80.18% | 224 | -109.90% | -104.99% | 10% | yes |
| yt>=200bp | -31.57% | -1.03 | 156 | -111.27% | -3.94 | 123.36% | -6.09 | -146.28% to -76.34% | 133 | -101.55% | -103.13% | 11% | yes |
| yt>=400bp | -38.22% | -1.18 | 97 | -138.73% | -3.83 | 153.97% | -4.45 | -203.97% to -80.71% | 74 | -119.77% | -108.70% | 8% | yes |
| yt_all | -171.14% | -4.97 | 4613 | -333.97% | -14.32 | 369.66% | -7.30 | -437.45% to -248.30% | 3202 | -256.15% | -303.39% | 3% | yes |

Chosen variant out of sample, by class: btc 8 trades, pooled -391.39%, median -452.08%, 0% positive; eth 42 trades, pooled -49.36%, median -71.11%, 17% positive; ethena 9 trades, pooled -116.39%, median -122.70%, 0% positive; hype 3 trades, pooled -484.32%, median -527.35%, 0% positive; other 29 trades, pooled -118.04%, median -105.79%, 7% positive; stable 133 trades, pooled -136.10%, median -110.89%, 11% positive.

### (d) Dollar PT over the savings rate, by spread at entry, after defaults

Chosen in sample: **>=15%** (of 7 variants; out-of-sample rank 3; deflated Sharpe of the in-sample choice 0.522).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| 10%-15% | 2.57% | 0.99 | 132 | 2.02% | 0.42 | 6.85% | 0.36 | -10.59% to 9.52% | 226 | 6.49% | 9.94% | 88% | no |
| 2%-4% | 0.63% | 0.44 | 267 | -8.65% | -1.17 | 10.44% | -1.57 | -21.13% to 0.35% | 452 | -9.41% | 2.01% | 81% | no |
| 4%-6% | 2.17% | 1.01 | 291 | -27.46% | -2.03 | 31.62% | -3.04 | -45.65% to -11.14% | 477 | -27.04% | 3.61% | 91% | yes |
| 6%-10% | 2.78% | 0.75 | 365 | 0.28% | 0.07 | 3.80% | 0.08 | -6.19% to 5.90% | 445 | 3.52% | 6.40% | 97% | no |
| <2% | -2.08% | -2.21 | 331 | -0.27% | -0.82 | 0.44% | -0.94 | -0.81% to 0.17% | 319 | 0.18% | 0.20% | 56% | no |
| >=15% | 5.74% | 1.70 | 112 | -2.59% | -0.28 | 12.25% | -0.28 | -23.71% to 12.49% | 66 | 10.26% | 14.18% | 89% | no |
| all_dollar | 1.82% | 1.23 | 1498 | -8.20% | -1.73 | 10.28% | -2.59 | -13.89% to -2.46% | 1985 | -6.92% | 3.38% | 84% | yes |

Chosen variant out of sample, by class: stable 66 trades, pooled 10.26%, median 14.18%, 89% positive.

### (d) Dollar PT over the savings rate, threshold rule, after defaults

Chosen in sample: **spread>=10%** (of 6 variants; out-of-sample rank 1; deflated Sharpe of the in-sample choice 0.938).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| spread>=0% | 2.85% | 1.67 | 1352 | -8.31% | -1.71 | 10.45% | -2.57 | -14.08% to -2.37% | 1930 | -7.11% | 3.48% | 86% | yes |
| spread>=10% | 4.63% | 1.71 | 244 | 2.28% | 0.46 | 6.79% | 0.41 | -10.48% to 10.53% | 292 | 7.26% | 10.25% | 89% | no |
| spread>=15% | 5.74% | 1.70 | 112 | -2.59% | -0.28 | 12.25% | -0.28 | -23.71% to 12.49% | 66 | 10.26% | 14.18% | 89% | no |
| spread>=2% | 3.93% | 1.57 | 1167 | -9.83% | -1.71 | 12.32% | -2.61 | -16.87% to -2.79% | 1666 | -8.39% | 3.94% | 89% | yes |
| spread>=4% | 4.40% | 1.17 | 900 | -10.41% | -1.70 | 13.28% | -2.37 | -18.87% to -2.40% | 1214 | -8.00% | 5.36% | 93% | yes |
| spread>=6% | 4.80% | 1.27 | 609 | 0.32% | 0.08 | 4.93% | 0.08 | -8.42% to 7.19% | 737 | 4.93% | 7.54% | 94% | no |

Chosen variant out of sample, by class: ethena 24 trades, pooled 8.86%, median 9.63%, 100% positive; stable 268 trades, pooled 7.12%, median 10.32%, 88% positive.

### (d) The same, defaults removed

Chosen in sample: **spread>=10%** (of 6 variants; out-of-sample rank 4; deflated Sharpe of the in-sample choice 1.000).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| spread>=0% | 3.37% | 2.09 | 1352 | 4.07% | 11.16 | 0.12% | 6.76 | 2.99% to 5.34% | 1930 | 4.44% | 3.66% | 91% | yes |
| spread>=10% | 6.95% | 4.30 | 244 | 9.18% | 11.69 | 0.25% | 7.98 | 7.12% to 11.63% | 292 | 11.64% | 10.38% | 100% | yes |
| spread>=15% | 8.01% | 3.76 | 112 | 10.21% | 7.97 | 0.81% | 4.36 | 5.92% to 14.99% | 66 | 17.94% | 16.65% | 100% | yes |
| spread>=2% | 4.41% | 1.81 | 1167 | 4.70% | 12.45 | 0.13% | 8.12 | 3.63% to 5.92% | 1666 | 5.18% | 4.23% | 95% | yes |
| spread>=4% | 5.00% | 1.36 | 900 | 5.83% | 12.80 | 0.13% | 9.80 | 4.71% to 7.07% | 1214 | 6.46% | 5.67% | 99% | yes |
| spread>=6% | 5.57% | 1.51 | 609 | 7.57% | 13.57 | 0.22% | 11.15 | 6.31% to 9.04% | 737 | 8.48% | 7.83% | 100% | yes |

### (d) Threshold rule, weighted by pool TVL at entry

Chosen in sample: **spread>=15%** (of 6 variants; out-of-sample rank 3; deflated Sharpe of the in-sample choice 0.979).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| spread>=0% | 4.49% | 2.41 | 1352 | -2.95% | -0.68 | 5.43% | -1.02 | -9.30% to 2.36% | 1930 | -7.11% | 3.48% | 86% | no |
| spread>=10% | 5.71% | 2.19 | 244 | 2.29% | 0.37 | 6.93% | 0.40 | -10.63% to 10.50% | 292 | 7.26% | 10.25% | 89% | no |
| spread>=15% | 7.23% | 2.44 | 112 | -3.17% | -0.34 | 11.94% | -0.35 | -23.69% to 10.67% | 66 | 10.26% | 14.18% | 89% | no |
| spread>=2% | 5.71% | 2.14 | 1167 | -3.66% | -0.73 | 6.49% | -1.12 | -10.76% to 2.41% | 1666 | -8.39% | 3.94% | 89% | no |
| spread>=4% | 5.97% | 1.57 | 900 | -2.01% | -0.49 | 5.20% | -0.74 | -7.79% to 3.24% | 1214 | -8.00% | 5.36% | 93% | no |
| spread>=6% | 6.25% | 1.63 | 609 | 2.61% | 0.58 | 4.97% | 0.64 | -6.71% to 8.67% | 737 | 4.93% | 7.54% | 94% | no |

### (b) Implied over trailing, weighted by pool TVL at entry

Chosen in sample: **spread>=500bp** (of 8 variants; out-of-sample rank 1; deflated Sharpe of the in-sample choice 1.000).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| all | 4.72% | 3.01 | 4613 | 3.78% | 12.54 | 0.13% | 6.35 | 2.59% to 4.92% | 3202 | 2.58% | 1.41% | 76% | yes |
| spread>=0bp | 6.53% | 3.21 | 4006 | 4.11% | 13.37 | 0.13% | 6.78 | 2.91% to 5.30% | 2729 | 3.22% | 1.92% | 82% | yes |
| spread>=100bp | 7.28% | 3.22 | 3498 | 5.01% | 14.01 | 0.15% | 7.93 | 3.81% to 6.27% | 2138 | 4.41% | 3.04% | 89% | yes |
| spread>=1200bp | 14.08% | 2.62 | 877 | 12.08% | 11.46 | 0.66% | 6.87 | 9.00% to 15.85% | 282 | 16.81% | 13.17% | 100% | yes |
| spread>=200bp | 7.95% | 3.32 | 3018 | 5.97% | 14.07 | 0.17% | 7.37 | 4.52% to 7.68% | 1684 | 5.41% | 4.49% | 92% | yes |
| spread>=300bp | 7.95% | 3.08 | 2665 | 6.70% | 14.58 | 0.19% | 7.24 | 5.07% to 8.72% | 1403 | 6.41% | 5.34% | 94% | yes |
| spread>=500bp | 10.57% | 3.67 | 2049 | 7.83% | 14.98 | 0.20% | 7.16 | 5.87% to 10.23% | 1004 | 8.44% | 6.75% | 96% | yes |
| spread>=800bp | 11.93% | 2.28 | 1343 | 10.06% | 13.52 | 0.40% | 8.18 | 8.04% to 12.75% | 548 | 11.77% | 10.03% | 98% | yes |

### (e) Dollar PT over the savings rate when implied clears the trailing floating, after defaults

Chosen in sample: **dollar_spread_over_trailing>=500bp** (of 4 variants; out-of-sample rank 2; deflated Sharpe of the in-sample choice 0.991).

| variant | IS APR | IS Sharpe | IS trades | OOS APR | OOS Sharpe | OOS max DD | OOS NW t (lag 77d) | OOS 95% CI (APR) | OOS trades | OOS pooled trade APR | OOS trade median APR | OOS share >0 | BH q10 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|
| dollar_spread_over_trailing>=0bp | 1.72% | 1.28 | 1247 | -9.43% | -1.78 | 11.64% | -2.67 | -15.65% to -3.26% | 1722 | -7.95% | 3.33% | 84% | yes |
| dollar_spread_over_trailing>=200bp | 0.82% | 0.60 | 1057 | -12.55% | -1.87 | 15.10% | -2.81 | -20.74% to -4.67% | 1246 | -9.80% | 3.76% | 85% | yes |
| dollar_spread_over_trailing>=500bp | 4.66% | 2.63 | 772 | -17.26% | -1.78 | 20.28% | -2.50 | -30.52% to -4.85% | 780 | -10.14% | 4.33% | 86% | yes |
| dollar_spread_over_trailing>=800bp | 5.94% | 2.50 | 545 | -30.69% | -1.57 | 35.04% | -1.76 | -68.71% to -3.28% | 402 | -14.66% | 6.83% | 88% | yes |

Chosen variant out of sample, by class: ethena 82 trades, pooled 3.88%, median 3.70%, 89% positive; stable 698 trades, pooled -11.63%, median 4.40%, 86% positive.

## Credit buckets (dollar PTs; rates pooled per capital-year)

| spread over savings rate at entry | trades | markets | capital-years | defaulted markets | promised spread | default loss | realised excess | median trade | OOS trades | OOS default loss | OOS realised excess |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| <2% | 694 | 98 | 220.3 | 1 | -1.43% | 0.28% | -1.71% | -0.24% | 319 | -0.24% | 0.18% |
| 2%-4% | 889 | 183 | 192.9 | 3 | 1.62% | 4.53% | -2.91% | 2.00% | 452 | 11.17% | -9.41% |
| 4%-6% | 909 | 180 | 181.9 | 8 | 3.63% | 14.36% | -10.73% | 3.67% | 477 | 30.52% | -27.04% |
| 6%-10% | 938 | 179 | 181.2 | 9 | 6.24% | 1.61% | 4.63% | 6.27% | 445 | 3.06% | 3.52% |
| 10%-15% | 399 | 103 | 71.5 | 9 | 10.17% | 3.09% | 7.08% | 9.68% | 226 | 3.53% | 6.49% |
| >=15% | 182 | 45 | 31.4 | 10 | 20.27% | 5.26% | 15.01% | 16.10% | 66 | 7.68% | 10.26% |

## What each family's in-sample choice would hold today

| family | chosen | markets | capacity | $/yr before defaults | $/yr after historical default loss | net APR after defaults |
|---|---|---:|---:|---:|---:|---:|
| a_pt_minus_floating_by_class | ethena | 4 | $1.3M | $29k | $29k | 2.27% |
| b_pt_when_implied_over_trailing | spread>=500bp | 18 | $10.0M | $423k | $423k | 4.23% |
| c_yt_when_floating_over_implied | yt>=100bp | 0 | $0 | $0 | $0 | - |
| d_dollar_pt_over_ssr_buckets | >=15% | 5 | $2.3M | $277k | $157k | 6.91% |
| d_dollar_pt_over_ssr_thresholds | spread>=10% | 15 | $13.9M | $957k | $478k | 3.43% |
| e_dollar_pt_over_ssr_when_implied_over_trailing | dollar_spread_over_trailing>=500bp | 13 | $10.4M | $571k | $-117k | -1.13% |

## Live board (top 25 by dollars a year at the size that maximises them)

| market | class | points | days | pool TVL | implied | comparator | spread | best size | implied after | $/yr |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| apyUSD | stable | y | 27 | $19.7M | 16.16% | 3.80% | 12.36% | $5.0M | 8.67% | $244k |
| reUSDe | ethena |  | 62 | $4.7M | 18.63% | 3.80% | 14.83% | $2.5M | 11.41% | $190k |
| USD3 | stable |  | 69 | $7.2M | 15.13% | 3.80% | 11.33% | $2.5M | 9.14% | $133k |
| reUSD | stable |  | 62 | $12.4M | 11.86% | 3.80% | 8.06% | $2.5M | 8.84% | $126k |
| sUSDx | stable | y | 55 | $6.1M | 18.99% | 3.80% | 15.19% | $1.0M | 15.17% | $114k |
| siUSD | stable | y | 90 | $11.1M | 9.94% | 3.80% | 6.14% | $2.5M | 7.89% | $102k |
| SIERRA | stable | y | 13 | $11.0M | 9.74% | 3.80% | 5.94% | $2.5M | 7.64% | $96k |
| sUSDfr | stable |  | 111 | $1.8M | 29.99% | 3.80% | 26.19% | $500k | 20.58% | $84k |
| sUSD3 | stable |  | 69 | $1.3M | 24.60% | 3.80% | 20.80% | $500k | 14.70% | $55k |
| sUSDat | stable | y | 97 | $1.6M | 17.09% | 3.80% | 13.29% | $500k | 12.98% | $46k |
| sUSDai | stable | y | 139 | $3.1M | 9.90% | 3.80% | 6.10% | $1.0M | 6.60% | $28k |
| USDx | stable | y | 55 | $2.2M | 14.64% | 3.80% | 10.84% | $500k | 9.19% | $27k |
| siUSD | stable | y | 13 | $3.3M | 9.51% | 3.80% | 5.71% | $1.0M | 6.44% | $26k |
| jrRoyAPYUSD | stable | y | 27 | $986k | 19.32% | 3.80% | 15.52% | $250k | 13.21% | $24k |
| apxUSD | stable | y | 27 | $1.6M | 13.86% | 3.80% | 10.06% | $250k | 10.48% | $17k |
| strUSD | stable | y | 48 | $4.6M | 11.39% | 3.80% | 7.59% | $500k | 7.10% | $17k |
| sUSDat | stable | y | 97 | $1.4M | 13.97% | 3.80% | 10.17% | $250k | 9.75% | $15k |
| STRCx | other | y | 48 | $1.3M | 24.56% | 12.22% | 12.34% | $250k | 16.87% | $12k |
| USDat | stable | y | 97 | $2.1M | 8.41% | 3.80% | 4.61% | $500k | 6.02% | $11k |
| mAPOLLO | stable | y | 160 | $2.9M | 7.03% | 3.80% | 3.23% | $500k | 5.55% | $9k |
| USDat | stable | y | 97 | $1.6M | 9.03% | 3.80% | 5.23% | $250k | 7.18% | $8k |
| limUSD | stable |  | 48 | $1.3M | 10.19% | 3.80% | 6.39% | $250k | 7.05% | $8k |
| sUSDe | ethena | y | 13 | $22.1M | 5.10% | 3.80% | 1.30% | $1.0M | 4.54% | $7k |
| fxSAVE | stable |  | 20 | $1.4M | 9.02% | 3.80% | 5.22% | $250k | 6.19% | $6k |
| sUSN | stable | y | 286 | $1.2M | 8.61% | 3.80% | 4.81% | $250k | 6.17% | $6k |
