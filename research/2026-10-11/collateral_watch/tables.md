# Collateral watch: 2026-10-11 (carry computed 2026-10-11T00:20:41+00:00)

Benchmark: term_carry.SSR (constant 3.80%/yr, the book protocol benchmark). Capital per $ of short: K = 1 + max(0, im + R - c(1+R)), im = max(1/10, 1/max leverage), c at a $1M holding, R = 50%. Excess: (funding APR - borrow APR x borrowed at entry + known collateral yield) / K - SSR; gross of trading costs (round trip in the json as rt_fee_bp). "At floor" is the share of settlements exactly at the formula's interest leg (0.01%/8h scaled to the interval; Hyperliquid 0.00125%/h = 10.95%/yr; 0 where a venue has no interest leg). Rows need 80% funding coverage over 30 days and a plausible spot/perp price match to rank.

## Collateral lists (snapshot 2026-10-11)

| venue | program | rows | ratio > 0 | fetch | notable (ratio = 1 - haircut, first tier) |
|---|---|---|---|---|---|
| binance | multi_assets | 12 | 12 | ok | BTC 0.95, ETH 0.95 |
| binance | portfolio_margin | 488 | 488 | ok | HYPE 0.70, BTC 0.95, ETH 0.95, SOL 0.80, XAUT 0.80, PAXG 0.80, WBETH 0.95, BNSOL 0.80, USDE 0.90, AERO 0.30, VELODROME 0.10, TAO 0.60, ENA 0.60; 91 stock tokens (TSLAB, NVDAB, ...) |
| binance | portfolio_margin_pro | 496 | 496 | ok | HYPE 1.00 (0.99 at $1M), BTC 1.00 (1.00 at $1M), ETH 1.00 (1.00 at $1M), SOL 1.00 (1.00 at $1M), XAUT 1.00 (0.99 at $1M), PAXG 1.00 (0.99 at $1M), WBETH 1.00 (1.00 at $1M), BNSOL 1.00 (1.00 at $1M), USDE 1.00 (1.00 at $1M), AERO 1.00 (0.40 at $1M), VELODROME 1.00 (0.24 at $1M), TAO 1.00 (0.72 at $1M), ENA 1.00 (0.72 at $1M) |
| bybit | uta | 268 | 268 | ok | HYPE 0.80, BTC 0.98, ETH 0.98, SOL 0.95, XAUT 0.90, STETH 0.98, METH 0.98, BBSOL 0.95, USDE 1.00, AERO 0.70, VELO 0.60, ENA 0.85 |
| deribit | cross_collateral | 21 | 21 | ok | HYPE 0.85, BTC 1.00, ETH 1.00, SOL 0.85, PAXG 0.95, STETH 0.93, USDE 0.95, TAO 0.62 |
| deribit | docs | 2 | 0 | ok | cross-collateral-table d512c716c776fae4, cross-collateral-article 616123e28d9702d3 |
| hyperliquid | docs | 5 | 0 | ok | page 3045578c964b1836, portfolio-margin 327343837133a642, ltv-and-borrowing a694da3ee460fef9, example-carry-trade 9786e0bf570c8d0f, liquidations 68dad06cd61dc645 |
| hyperliquid | hip3_collateral | 11 | 0 | ok | main: USDC (178/234 live), xyz: USDC (114/133 live), flx: USDH (0/16 live), vntl: USDH (0/15 live), hyna: USDE not borrowable (0/25 live), km: USDH (0/23 live), abcd: USDC (0/1 live), cash: USDT0 (0/17 live), para: USDC (30/38 live), mkts: USDC (5/24 live), io: USDC (9/12 live) |
| hyperliquid | portfolio_margin | 5 | 2 | ok | HYPE 0.65, UBTC 0.50 |
| okx | multi_currency_margin | 273 | 273 | ok | HYPE 0.95, BTC 0.98, ETH 0.98, SOL 0.97, XAUT 0.95, PAXG 0.85, BETH 0.98, TAO 0.80, ENA 0.90 |

Checks: {"deribit": {"article_not_in_pool": [], "collateral_fee_per_day": 0.0005, "pool_not_in_article": []}, "hyperliquid": {"docs_assets_without_reserve": [], "docs_ltv_mismatch": [], "docs_ltv_vs_api": {"HYPE": {"api": 0.65, "docs": 0.65}, "UBTC": {"api": 0.5, "docs": 0.5}}}}

## Same-venue carry, ranked by 30-day excess on capital

### hyperliquid (2 rankable rows, 0 not)

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hyperliquid | HYPE -> HYPE | direct | 0.650 | 1.00 | +8.40% | +9.39% | 75% (84%) | +0.50% | +4.10% | +5.09% | $1.7B | $185k / $159k |  |
| hyperliquid | UBTC -> BTC | wrapped | 0.500 | 1.00 | +8.50% | +8.88% | 63% (67%) | +0.50% | +4.20% | +4.58% | $3.2B | $4.3M / $574k |  |

### binance (444 rankable rows, 4 not)

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| binance | BNCB -> BNCUSDT | stock token | 0.500 | 1.00 | -21.40% | +21.96% | 43% (52%) at 0 | +0.00% | -25.20% | +18.16% | $8.3M | $6k / $7k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | PDDB -> PDDUSDT | stock token | 0.500 | 1.00 | +18.10% | +16.74% | 68% (71%) at 0 | +0.00% | +14.30% | +12.94% | $1.5M | $5k / $15k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | CRCLB -> CRCLUSDT | stock token | 0.600 | 1.00 | +11.44% | +15.69% | 36% (52%) at 0 | +0.00% | +7.64% | +11.89% | $128.4M | $425k / $54k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | SHAZB -> SHAZUSDT | stock token | 0.500 | 1.00 | +16.98% | +14.97% | 59% (52%) at 0 | +0.00% | +13.18% | +11.17% | $808k | $3k / $605 | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | 牛来 -> 牛来USDT | direct | 0.100 | 1.45 | +10.95% | +19.14% | 72% (100%) | +0.00% | +3.75% | +9.40% | $22.8M | $9k / $8k |  |
| binance | NFLXB -> NFLXUSDT | stock token | 0.500 | 1.00 | +6.24% | +12.86% | 52% (67%) at 0 | +0.00% | +2.44% | +9.06% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | BABAB -> BABAUSDT | stock token | 0.500 | 1.00 | +7.98% | +12.83% | 49% (62%) at 0 | +0.00% | +4.18% | +9.03% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | 币安人生 -> 币安人生USDT | direct | 0.100 | 1.45 | +14.81% | +18.47% | 75% (83%) | +0.00% | +6.41% | +8.94% |  |  |  |
| binance | MITO -> MITOUSDT | direct | 0.100 | 1.45 | +16.33% | +18.12% | 69% (74%) | +0.00% | +7.46% | +8.70% |  |  |  |
| binance | COOKIE -> COOKIEUSDT | direct | 0.100 | 1.45 | +10.95% | +16.73% | 84% (100%) | +0.00% | +3.75% | +7.74% |  |  |  |
| binance | WLFI -> WLFIUSDT | direct | 0.700 | 1.00 | +10.18% | +11.04% | 90% (83%) | +0.00% | +6.38% | +7.24% |  |  |  |
| binance | NVDAB -> NVDAUSDT | stock token | 0.500 | 1.00 | +10.08% | +10.80% | 31% (29%) at 0 | +0.00% | +6.28% | +7.00% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |

### okx (169 rankable rows, 0 not)

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| okx | OKB -> OKB-USDT-SWAP | direct | 0.723 | 1.00 | +10.26% | +9.37% | 84% (95%) | +0.00% | +6.46% | +5.57% | $34.5M | $53k / $68k |  |
| okx | GRAM -> GRAM-USDT-SWAP | direct | 0.233 | 1.25 | +10.20% | +9.60% | 89% (90%) | +0.00% | +4.36% | +3.88% | $10.8M | $56k / $49k |  |
| okx | ASTER -> ASTER-USDT-SWAP | direct | 0.464 | 1.00 | +5.17% | +7.56% | 63% (45%) | +0.00% | +1.37% | +3.76% | $11.1M | $76k / $19k |  |
| okx | DOGE -> DOGE-USDT-SWAP | direct | 0.942 | 1.00 | +4.11% | +7.54% | 54% (43%) | +0.00% | +0.31% | +3.74% | $94.1M | $1.5M / $585k |  |
| okx | PUMP -> PUMP-USDT-SWAP | direct | 0.541 | 1.00 | +4.18% | +7.31% | 63% (45%) | +0.00% | +0.38% | +3.51% | $34.3M | $105k / $28k |  |
| okx | ONDO -> ONDO-USDT-SWAP | direct | 0.591 | 1.00 | +6.40% | +7.18% | 63% (65%) | +0.00% | +2.60% | +3.38% | $19.9M | $213k / $132k |  |
| okx | LTC -> LTC-USDT-SWAP | direct | 0.866 | 1.00 | +4.85% | +7.09% | 52% (24%) | +0.00% | +1.05% | +3.29% | $30.0M | $367k / $274k |  |
| okx | WIF -> WIF-USDT-SWAP | direct | 0.254 | 1.22 | +3.64% | +8.46% | 81% (52%) | +0.00% | -0.82% | +3.14% | $5.1M | $40k / $19k |  |
| okx | HBAR -> HBAR-USDT-SWAP | direct | 0.525 | 1.00 | +5.38% | +6.87% | 61% (48%) | +0.00% | +1.58% | +3.07% | $7.6M | $457k / $116k |  |
| okx | AUCTION -> AUCTION-USDT-SWAP | direct | 0.004 | 1.59 | +10.93% | +10.94% | 99% (98%) | +0.00% | +3.06% | +3.06% | $616k |  |  |
| okx | FLOW -> FLOW-USDT-SWAP | direct | 0.002 | 1.60 | +10.95% | +10.79% | 98% (100%) | +0.00% | +3.06% | +2.96% | $808k |  |  |
| okx | TURBO -> TURBO-USDT-SWAP | direct | 0.012 | 1.58 | +10.94% | +10.68% | 98% (98%) | +0.00% | +3.11% | +2.95% | $823k | $2k / $645 |  |

### bybit (241 rankable rows, 0 not)

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bybit | GRVT -> GRVTUSDT | direct | 0.114 | 1.43 | +17.75% | +29.98% | 58% (71%) | +0.00% | +8.63% | +17.18% | $3.6M | $2k / $10 |  |
| bybit | EGLD -> EGLDUSDT | direct | 0.209 | 1.29 | +24.72% | +19.86% | 61% (71%) | +0.00% | +15.41% | +11.63% | $3.3M | $21k / $4k |  |
| bybit | BABYDOGE -> 1000000BABYDOGEUSDT | multiplier | 0.022 | 1.57 | +10.95% | +20.79% | 84% (100%) | +0.00% | +3.19% | +9.47% | $314k | $9k / $1k |  |
| bybit | MERL -> MERLUSDT | direct | 0.207 | 1.29 | +8.89% | +15.70% | 66% (81%) | +0.00% | +3.09% | +8.37% | $1.1M | $1k / $1k |  |
| bybit | XDC -> XDCUSDT | direct | 0.473 | 1.00 | +10.76% | +10.20% | 93% (98%) | +0.00% | +6.96% | +6.40% | $2.9M | $4k / $2k |  |
| bybit | NEIROCTO -> 1000NEIROCTOUSDT | multiplier | 0.208 | 1.29 | +10.59% | +12.55% | 97% (98%) | +0.00% | +4.42% | +5.94% | $884k |  |  |
| bybit | SATS -> 10000SATSUSDT | multiplier | 0.209 | 1.29 | +15.06% | +12.08% | 97% (93%) | +0.00% | +7.90% | +5.59% | $286k |  |  |
| bybit | GRASS -> GRASSUSDT | direct | 0.353 | 1.07 | +10.90% | +9.56% | 92% (98%) | +0.00% | +6.39% | +5.13% | $27.4M | $78k / $6k |  |
| bybit | CGPT -> CGPTUSDT | direct | 0.205 | 1.29 | +10.95% | +11.30% | 99% (100%) | +0.00% | +4.67% | +4.94% | $330k |  |  |
| bybit | NIGHT -> NIGHTUSDT | direct | 0.566 | 1.00 | +9.30% | +8.61% | 88% (88%) | +0.00% | +5.50% | +4.81% | $4.1M | $4k / $8k |  |
| bybit | DYDX -> DYDXUSDT | direct | 0.225 | 1.26 | +10.95% | +10.81% | 97% (100%) | +0.00% | +4.88% | +4.77% | $3.3M |  |  |
| bybit | POPCAT -> POPCATUSDT | direct | 0.211 | 1.28 | +10.95% | +10.95% | 100% (100%) | +0.00% | +4.74% | +4.74% | $6.5M |  |  |

### deribit (15 rankable rows, 1 not)

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deribit | HBAR -> HBAR_USDC-PERPETUAL | direct | 0.675 | 1.00 | +38.03% | +20.73% | 1% (0%) at 0 | +0.00% | +34.23% | +16.93% | $952k | $179k / $180k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | HYPE -> HYPE_USDC-PERPETUAL | direct | 0.850 | 1.00 | +6.40% | +19.56% | 9% (22%) at 0 | +0.00% | +2.60% | +15.76% | $9.7M | $744k / $396k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | NEAR -> NEAR_USDC-PERPETUAL | direct | 0.750 | 1.00 | +5.13% | +18.84% | 0% (2%) at 0 | +0.00% | +1.33% | +15.04% | $2.5M | $422k / $196k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | XRP -> XRP_USDC-PERPETUAL | direct | 0.850 | 1.00 | +2.54% | +8.65% | 13% (45%) at 0 | +0.00% | -1.26% | +4.85% | $12.9M | $1.5M / $1.3M ok | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | LINK -> LINK_USDC-PERPETUAL | direct | 0.800 | 1.00 | +0.01% | +7.94% | 13% (31%) at 0 | +0.00% | -3.79% | +4.14% | $2.1M | $199k / $318k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | STETH -> ETH-PERPETUAL | staking token | 0.925 | 1.00 | +1.75% | +4.15% | 18% (29%) at 0 | +0.00% | +0.20% | +2.60% | $246.3M | $5.8M / $10k |  |
| deribit | TAO -> TAO_USDC-PERPETUAL | direct | 0.625 | 1.00 | +18.50% | +5.42% | 4% (10%) at 0 | +0.00% | +14.70% | +1.62% | $462k |  | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | BTC -> BTC-PERPETUAL | direct | 1.000 | 1.00 | +4.17% | +4.36% | 24% (16%) at 0 | +0.00% | +0.37% | +0.56% | $831.9M |  |  |
| deribit | DOGE -> DOGE_USDC-PERPETUAL | direct | 0.825 | 1.00 | +0.92% | +4.35% | 29% (51%) at 0 | +0.00% | -2.88% | +0.55% | $1.8M |  | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | ETH -> ETH-PERPETUAL | direct | 1.000 | 1.00 | +1.75% | +4.15% | 18% (29%) at 0 | +0.00% | -2.05% | +0.35% | $246.3M |  |  |
| deribit | CBETH -> ETH-PERPETUAL | staking token | 0.950 | 1.00 | +1.75% | +4.15% | 18% (29%) at 0 | +0.00% | -2.05% | +0.35% | $246.3M |  | staking yield of CBETH not counted |
| deribit | ADA -> ADA_USDC-PERPETUAL | direct | 0.750 | 1.00 | +1.39% | +3.68% | 8% (8%) at 0 | +0.00% | -2.41% | -0.12% | $1.1M |  | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |

## Books read (106 rows: per venue the 30 most traded rows above 2pp, the top 5, and Hyperliquid), by the smaller leg within 25bp

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deribit | XRP -> XRP_USDC-PERPETUAL | direct | 0.850 | 1.00 | +2.54% | +8.65% | 13% (45%) at 0 | +0.00% | -1.26% | +4.85% | $12.9M | $1.5M / $1.3M ok | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| binance | DOGE -> DOGEUSDT | direct | 0.800 | 1.00 | +3.50% | +6.45% | 41% (29%) | +0.00% | -0.30% | +2.65% | $226.0M | $1.6M / $743k |  |
| okx | DOGE -> DOGE-USDT-SWAP | direct | 0.942 | 1.00 | +4.11% | +7.54% | 54% (43%) | +0.00% | +0.31% | +3.74% | $94.1M | $1.5M / $585k |  |
| hyperliquid | UBTC -> BTC | wrapped | 0.500 | 1.00 | +8.50% | +8.88% | 63% (67%) | +0.50% | +4.20% | +4.58% | $3.2B | $4.3M / $574k |  |
| deribit | HYPE -> HYPE_USDC-PERPETUAL | direct | 0.850 | 1.00 | +6.40% | +19.56% | 9% (22%) at 0 | +0.00% | +2.60% | +15.76% | $9.7M | $744k / $396k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| bybit | XAUT -> XAUTUSDT | direct | 0.846 | 1.00 | +6.95% | +6.48% | 59% (69%) | +0.00% | +3.15% | +2.68% | $141.5M | $1.2M / $386k |  |
| binance | ADA -> ADAUSDT | direct | 0.800 | 1.00 | +4.06% | +6.01% | 51% (48%) | +0.00% | +0.26% | +2.21% | $96.8M | $681k / $277k |  |
| okx | LTC -> LTC-USDT-SWAP | direct | 0.866 | 1.00 | +4.85% | +7.09% | 52% (24%) | +0.00% | +1.05% | +3.29% | $30.0M | $367k / $274k |  |
| okx | BNB -> BNB-USDT-SWAP | direct | 0.841 | 1.00 | +3.23% | +5.84% | 44% (38%) | +0.00% | -0.57% | +2.04% | $53.3M | $892k / $260k |  |
| binance | NEAR -> NEARUSDT | direct | 0.700 | 1.00 | +6.92% | +7.06% | 52% (48%) | +0.00% | +3.12% | +3.26% | $307.2M | $886k / $256k |  |
| deribit | LINK -> LINK_USDC-PERPETUAL | direct | 0.800 | 1.00 | +0.01% | +7.94% | 13% (31%) at 0 | +0.00% | -3.79% | +4.14% | $2.1M | $199k / $318k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | NEAR -> NEAR_USDC-PERPETUAL | direct | 0.750 | 1.00 | +5.13% | +18.84% | 0% (2%) at 0 | +0.00% | +1.33% | +15.04% | $2.5M | $422k / $196k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| okx | PEPE -> PEPE-USDT-SWAP | direct | 0.800 | 1.00 | +1.38% | +5.81% | 56% (43%) | +0.00% | -2.42% | +2.01% | $25.3M | $393k / $194k |  |
| deribit | HBAR -> HBAR_USDC-PERPETUAL | direct | 0.675 | 1.00 | +38.03% | +20.73% | 1% (0%) at 0 | +0.00% | +34.23% | +16.93% | $952k | $179k / $180k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| binance | UNI -> UNIUSDT | direct | 0.700 | 1.00 | +4.18% | +6.82% | 43% (33%) | +0.00% | +0.38% | +3.02% | $180.2M | $494k / $172k |  |
| binance | LTC -> LTCUSDT | direct | 0.700 | 1.00 | +3.64% | +6.47% | 41% (19%) | +0.00% | -0.16% | +2.67% | $73.9M | $385k / $168k |  |
| binance | ENA -> ENAUSDT | direct | 0.600 | 1.00 | +8.48% | +8.73% | 68% (62%) | +0.00% | +4.68% | +4.93% | $122.0M | $312k / $165k |  |
| hyperliquid | HYPE -> HYPE | direct | 0.650 | 1.00 | +8.40% | +9.39% | 75% (84%) | +0.50% | +4.10% | +5.09% | $1.7B | $185k / $159k |  |
| binance | XLM -> XLMUSDT | direct | 0.500 | 1.00 | -0.49% | +6.48% | 67% (19%) | +0.00% | -4.29% | +2.68% | $40.0M | $479k / $159k |  |
| binance | TAO -> TAOUSDT | direct | 0.600 | 1.00 | +6.89% | +7.51% | 69% (62%) | +0.00% | +3.09% | +3.71% | $66.9M | $295k / $139k |  |
| okx | UNI -> UNI-USDT-SWAP | direct | 0.826 | 1.00 | +4.51% | +6.13% | 44% (29%) | +0.00% | +0.71% | +2.33% | $43.0M | $327k / $138k |  |
| binance | ASTER -> ASTERUSDT | direct | 0.500 | 1.00 | +7.76% | +8.77% | 68% (50%) | +0.00% | +3.96% | +4.97% | $94.3M | $163k / $133k |  |
| okx | ONDO -> ONDO-USDT-SWAP | direct | 0.591 | 1.00 | +6.40% | +7.18% | 63% (65%) | +0.00% | +2.60% | +3.38% | $19.9M | $213k / $132k |  |
| binance | HBAR -> HBARUSDT | direct | 0.500 | 1.00 | +6.48% | +6.84% | 42% (38%) | +0.00% | +2.68% | +3.04% | $38.1M | $364k / $121k |  |
| okx | SUI -> SUI-USDT-SWAP | direct | 0.833 | 1.00 | +2.40% | +6.05% | 44% (14%) | +0.00% | -1.40% | +2.25% | $41.2M | $413k / $120k |  |
| okx | HBAR -> HBAR-USDT-SWAP | direct | 0.525 | 1.00 | +5.38% | +6.87% | 61% (48%) | +0.00% | +1.58% | +3.07% | $7.6M | $457k / $116k |  |
| okx | ADA -> ADA-USDT-SWAP | direct | 0.814 | 1.00 | +5.25% | +6.42% | 66% (52%) | +0.00% | +1.45% | +2.62% | $31.5M | $416k / $113k |  |
| bybit | PEPE -> 1000PEPEUSDT | multiplier | 0.731 | 1.00 | +5.71% | +5.88% | 54% (62%) | +0.00% | +1.91% | +2.08% | $48.7M | $421k / $105k |  |
| okx | WLD -> WLD-USDT-SWAP | direct | 0.797 | 1.00 | +5.71% | +6.25% | 53% (38%) | +0.00% | +1.91% | +2.45% | $40.2M | $181k / $96k |  |
| bybit | ADA -> ADAUSDT | direct | 0.786 | 1.00 | +4.41% | +5.88% | 52% (52%) | +0.00% | +0.61% | +2.08% | $69.5M | $334k / $96k |  |
| bybit | NEAR -> NEARUSDT | direct | 0.850 | 1.00 | +5.81% | +6.21% | 67% (67%) | +0.00% | +2.01% | +2.41% | $205.9M | $691k / $89k |  |
| binance | ONDO -> ONDOUSDT | direct | 0.600 | 1.00 | +7.78% | +7.60% | 64% (55%) | +0.00% | +3.98% | +3.80% | $73.3M | $398k / $89k |  |
| binance | FIL -> FILUSDT | direct | 0.500 | 1.00 | +6.29% | +6.16% | 40% (33%) | +0.00% | +2.49% | +2.36% | $61.0M | $259k / $82k |  |
| binance | PUMP -> PUMPUSDT | direct | 0.500 | 1.00 | +7.88% | +8.46% | 63% (45%) | +0.00% | +4.08% | +4.67% | $112.6M | $300k / $77k |  |
| okx | ENA -> ENA-USDT-SWAP | direct | 0.555 | 1.00 | +3.79% | +6.48% | 65% (43%) | +0.00% | -0.01% | +2.68% | $14.2M | $228k / $72k |  |
| binance | PENGU -> PENGUUSDT | direct | 0.300 | 1.15 | +6.39% | +8.27% | 69% (52%) | +0.00% | +1.76% | +3.39% | $31.6M | $159k / $71k |  |
| bybit | ONDO -> ONDOUSDT | direct | 0.548 | 1.00 | +5.68% | +6.64% | 73% (62%) | +0.00% | +1.88% | +2.84% | $72.0M | $386k / $59k |  |
| binance | CRCLB -> CRCLUSDT | stock token | 0.600 | 1.00 | +11.44% | +15.69% | 36% (52%) at 0 | +0.00% | +7.64% | +11.89% | $128.4M | $425k / $54k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| okx | OKB -> OKB-USDT-SWAP | direct | 0.723 | 1.00 | +10.26% | +9.37% | 84% (95%) | +0.00% | +6.46% | +5.57% | $34.5M | $53k / $68k |  |
| bybit | ENA -> ENAUSDT | direct | 0.803 | 1.00 | +5.16% | +6.67% | 72% (69%) | +0.00% | +1.36% | +2.87% | $87.5M | $661k / $53k |  |

## Flagged: excess > 2pp and $1M within 25bp on both legs

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deribit | XRP -> XRP_USDC-PERPETUAL | direct | 0.850 | 1.00 | +2.54% | +8.65% | 13% (45%) at 0 | +0.00% | -1.26% | +4.85% | $12.9M | $1.5M / $1.3M ok | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |

Excess > 2pp but $1M does not fit within 25bp on both legs (or no book read): 382 rows

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| binance | BNCB -> BNCUSDT | stock token | 0.500 | 1.00 | -21.40% | +21.96% | 43% (52%) at 0 | +0.00% | -25.20% | +18.16% | $8.3M | $6k / $7k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| bybit | GRVT -> GRVTUSDT | direct | 0.114 | 1.43 | +17.75% | +29.98% | 58% (71%) | +0.00% | +8.63% | +17.18% | $3.6M | $2k / $10 |  |
| deribit | HBAR -> HBAR_USDC-PERPETUAL | direct | 0.675 | 1.00 | +38.03% | +20.73% | 1% (0%) at 0 | +0.00% | +34.23% | +16.93% | $952k | $179k / $180k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | HYPE -> HYPE_USDC-PERPETUAL | direct | 0.850 | 1.00 | +6.40% | +19.56% | 9% (22%) at 0 | +0.00% | +2.60% | +15.76% | $9.7M | $744k / $396k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| deribit | NEAR -> NEAR_USDC-PERPETUAL | direct | 0.750 | 1.00 | +5.13% | +18.84% | 0% (2%) at 0 | +0.00% | +1.33% | +15.04% | $2.5M | $422k / $196k | USDC-settled: losses after a rally are negative USDC equity, charged 0.05%/day (18.2%/yr) |
| binance | PDDB -> PDDUSDT | stock token | 0.500 | 1.00 | +18.10% | +16.74% | 68% (71%) at 0 | +0.00% | +14.30% | +12.94% | $1.5M | $5k / $15k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | CRCLB -> CRCLUSDT | stock token | 0.600 | 1.00 | +11.44% | +15.69% | 36% (52%) at 0 | +0.00% | +7.64% | +11.89% | $128.4M | $425k / $54k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| bybit | EGLD -> EGLDUSDT | direct | 0.209 | 1.29 | +24.72% | +19.86% | 61% (71%) | +0.00% | +15.41% | +11.63% | $3.3M | $21k / $4k |  |
| binance | SHAZB -> SHAZUSDT | stock token | 0.500 | 1.00 | +16.98% | +14.97% | 59% (52%) at 0 | +0.00% | +13.18% | +11.17% | $808k | $3k / $605 | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| bybit | BABYDOGE -> 1000000BABYDOGEUSDT | multiplier | 0.022 | 1.57 | +10.95% | +20.79% | 84% (100%) | +0.00% | +3.19% | +9.47% | $314k | $9k / $1k |  |
| binance | 牛来 -> 牛来USDT | direct | 0.100 | 1.45 | +10.95% | +19.14% | 72% (100%) | +0.00% | +3.75% | +9.40% | $22.8M | $9k / $8k |  |
| binance | NFLXB -> NFLXUSDT | stock token | 0.500 | 1.00 | +6.24% | +12.86% | 52% (67%) at 0 | +0.00% | +2.44% | +9.06% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | BABAB -> BABAUSDT | stock token | 0.500 | 1.00 | +7.98% | +12.83% | 49% (62%) at 0 | +0.00% | +4.18% | +9.03% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | 币安人生 -> 币安人生USDT | direct | 0.100 | 1.45 | +14.81% | +18.47% | 75% (83%) | +0.00% | +6.41% | +8.94% |  |  |  |
| binance | MITO -> MITOUSDT | direct | 0.100 | 1.45 | +16.33% | +18.12% | 69% (74%) | +0.00% | +7.46% | +8.70% |  |  |  |
| bybit | MERL -> MERLUSDT | direct | 0.207 | 1.29 | +8.89% | +15.70% | 66% (81%) | +0.00% | +3.09% | +8.37% | $1.1M | $1k / $1k |  |
| binance | COOKIE -> COOKIEUSDT | direct | 0.100 | 1.45 | +10.95% | +16.73% | 84% (100%) | +0.00% | +3.75% | +7.74% |  |  |  |
| binance | WLFI -> WLFIUSDT | direct | 0.700 | 1.00 | +10.18% | +11.04% | 90% (83%) | +0.00% | +6.38% | +7.24% |  |  |  |
| binance | NVDAB -> NVDAUSDT | stock token | 0.500 | 1.00 | +10.08% | +10.80% | 31% (29%) at 0 | +0.00% | +6.28% | +7.00% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | AAOIB -> AAOIUSDT | stock token | 0.500 | 1.00 | +8.75% | +10.55% | 46% (52%) at 0 | +0.00% | +4.95% | +6.75% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | ASR -> ASRUSDT | direct | 0.100 | 1.45 | +11.55% | +15.09% | 87% (93%) | +0.00% | +4.17% | +6.61% |  |  |  |
| binance | ADBEB -> ADBEUSDT | stock token | 0.500 | 1.00 | +11.98% | +10.31% | 67% (48%) at 0 | +0.00% | +8.18% | +6.51% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| bybit | XDC -> XDCUSDT | direct | 0.473 | 1.00 | +10.76% | +10.20% | 93% (98%) | +0.00% | +6.96% | +6.40% | $2.9M | $4k / $2k |  |
| binance | BMNRB -> BMNRUSDT | stock token | 0.500 | 1.00 | +5.68% | +10.13% | 59% (71%) at 0 | +0.00% | +1.88% | +6.33% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | MSTRB -> MSTRUSDT | stock token | 0.600 | 1.00 | +7.25% | +10.05% | 44% (62%) at 0 | +0.00% | +3.45% | +6.25% | $77.8M | $438k / $49k | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | NOM -> NOMUSDT | direct | 0.100 | 1.45 | +10.95% | +14.54% | 83% (100%) | +0.00% | +3.75% | +6.23% |  |  |  |
| bybit | NEIROCTO -> 1000NEIROCTOUSDT | multiplier | 0.208 | 1.29 | +10.59% | +12.55% | 97% (98%) | +0.00% | +4.42% | +5.94% | $884k |  |  |
| binance | MUBARAK -> MUBARAKUSDT | direct | 0.100 | 1.45 | +12.67% | +14.08% | 87% (90%) | +0.00% | +4.94% | +5.91% |  |  |  |
| binance | ASTSB -> ASTSUSDT | stock token | 0.500 | 1.00 | +10.64% | +9.70% | 57% (52%) at 0 | +0.00% | +6.84% | +5.90% |  |  | TradFi perp: interest leg 0; portfolio-margin eligibility of TradFi perps is not public |
| binance | BEAMX -> BEAMXUSDT | direct | 0.300 | 1.15 | +10.95% | +11.07% | 99% (100%) | +0.00% | +5.72% | +5.83% |  |  |  |

## Collateral whose perp sits at the formula's interest leg on most settlements (>= 50% of 30 days): 642

By venue: hyperliquid 2, binance 298, okx 134, bybit 208, deribit 0. The 40 most traded perps (24 h volume):

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| binance | MAGIC -> MAGICUSDT | direct | 0.300 | 1.15 | -49.83% | -20.27% | 85% (81%) | +0.00% | -47.13% | -21.43% |  |  |  |
| hyperliquid | UBTC -> BTC | wrapped | 0.500 | 1.00 | +8.50% | +8.88% | 63% (67%) | +0.50% | +4.20% | +4.58% | $3.2B | $4.3M / $574k |  |
| binance | STRK -> STRKUSDT | direct | 0.300 | 1.15 | +4.92% | +8.86% | 77% (40%) | +0.00% | +0.48% | +3.91% | $46.4M | $94k / $17k |  |
| binance | NEAR -> NEARUSDT | direct | 0.700 | 1.00 | +6.92% | +7.06% | 52% (48%) | +0.00% | +3.12% | +3.26% | $307.2M | $886k / $256k |  |
| okx | STRK -> STRK-USDT-SWAP | direct | 0.101 | 1.45 | +5.44% | +9.15% | 88% (74%) | +0.00% | -0.04% | +2.51% | $18.9M | $51k / $19k |  |
| okx | MAGIC -> MAGIC-USDT-SWAP | direct | 0.007 | 1.59 | -68.36% | -26.33% | 74% (64%) | +0.00% | -46.80% | -20.36% | $5.9M |  |  |
| binance | HYPE -> HYPEUSDT | direct | 0.700 | 1.00 | +6.46% | +5.67% | 51% (48%) | +0.00% | +2.66% | +1.87% |  |  |  |
| okx | NEAR -> NEAR-USDT-SWAP | direct | 0.770 | 1.00 | +6.42% | +5.45% | 51% (48%) | +0.00% | +2.62% | +1.65% | $66.6M |  |  |
| bybit | NEAR -> NEARUSDT | direct | 0.850 | 1.00 | +5.81% | +6.21% | 67% (67%) | +0.00% | +2.01% | +2.41% | $205.9M | $691k / $89k |  |
| binance | KAIA -> KAIAUSDT | direct | 0.100 | 1.45 | -420.41% | -90.83% | 73% (36%) | +0.00% | -293.74% | -66.44% |  |  |  |
| bybit | STRK -> STRKUSDT | direct | 0.692 | 1.00 | +8.56% | +7.10% | 83% (90%) | +0.00% | +4.76% | +3.30% | $40.8M | $60k / $6k |  |
| hyperliquid | HYPE -> HYPE | direct | 0.650 | 1.00 | +8.40% | +9.39% | 75% (84%) | +0.50% | +4.10% | +5.09% | $1.7B | $185k / $159k |  |
| binance | ADA -> ADAUSDT | direct | 0.800 | 1.00 | +4.06% | +6.01% | 51% (48%) | +0.00% | +0.26% | +2.21% | $96.8M | $681k / $277k |  |
| binance | LUMIA -> LUMIAUSDT | direct | 0.100 | 1.45 | +10.80% | +10.82% | 99% (98%) | +0.00% | +3.65% | +3.67% | $9.7M | $13k / $3k |  |
| binance | CFX -> CFXUSDT | direct | 0.300 | 1.15 | +8.69% | +8.85% | 76% (67%) | +0.00% | +3.76% | +3.89% | $10.9M | $23k / $18k |  |
| binance | ERA -> ERAUSDT | direct | 0.100 | 1.45 | -241.09% | -48.12% | 85% (50%) | +0.00% | -170.07% | -36.99% |  |  |  |
| binance | BAT -> BATUSDT | direct | 0.100 | 1.45 | -8.19% | +4.91% | 81% (67%) | +0.00% | -9.45% | -0.42% |  |  |  |
| okx | WLD -> WLD-USDT-SWAP | direct | 0.797 | 1.00 | +5.71% | +6.25% | 53% (38%) | +0.00% | +1.91% | +2.45% | $40.2M | $181k / $96k |  |
| binance | PUMP -> PUMPUSDT | direct | 0.500 | 1.00 | +7.88% | +8.46% | 63% (45%) | +0.00% | +4.08% | +4.67% | $112.6M | $300k / $77k |  |
| binance | TIA -> TIAUSDT | direct | 0.300 | 1.15 | +5.39% | +6.50% | 57% (43%) | +0.00% | +0.89% | +1.85% |  |  |  |
| binance | ENA -> ENAUSDT | direct | 0.600 | 1.00 | +8.48% | +8.73% | 68% (62%) | +0.00% | +4.68% | +4.93% | $122.0M | $312k / $165k |  |
| okx | DOGE -> DOGE-USDT-SWAP | direct | 0.942 | 1.00 | +4.11% | +7.54% | 54% (43%) | +0.00% | +0.31% | +3.74% | $94.1M | $1.5M / $585k |  |
| binance | CHIP -> CHIPUSDT | direct | 0.100 | 1.45 | +0.96% | +6.62% | 70% (50%) | +0.00% | -3.14% | +0.77% |  |  |  |
| bybit | MAGIC -> MAGICUSDT | direct | 0.222 | 1.27 | -51.32% | -23.24% | 89% (88%) | +0.00% | -44.32% | -22.16% | $4.8M |  |  |
| okx | PUMP -> PUMP-USDT-SWAP | direct | 0.541 | 1.00 | +4.18% | +7.31% | 63% (45%) | +0.00% | +0.38% | +3.51% | $34.3M | $105k / $28k |  |
| binance | OGN -> OGNUSDT | direct | 0.100 | 1.45 | -225.73% | -45.20% | 77% (24%) | +0.00% | -159.48% | -34.97% |  |  |  |
| binance | ONDO -> ONDOUSDT | direct | 0.600 | 1.00 | +7.78% | +7.60% | 64% (55%) | +0.00% | +3.98% | +3.80% | $73.3M | $398k / $89k |  |
| bybit | WLD -> WLDUSDT | direct | 0.763 | 1.00 | +3.82% | +5.61% | 60% (38%) | +0.00% | +0.02% | +1.81% | $86.1M |  |  |
| binance | OP -> OPUSDT | direct | 0.500 | 1.00 | +4.98% | +5.46% | 52% (48%) | +0.00% | +1.18% | +1.66% |  |  |  |
| okx | CFX -> CFX-USDT-SWAP | direct | 0.077 | 1.49 | +5.06% | +7.60% | 74% (52%) | +0.00% | -0.39% | +1.31% | $4.5M |  |  |
| binance | TAO -> TAOUSDT | direct | 0.600 | 1.00 | +6.89% | +7.51% | 69% (62%) | +0.00% | +3.09% | +3.71% | $66.9M | $295k / $139k |  |
| binance | DOT -> DOTUSDT | direct | 0.500 | 1.00 | +3.89% | +4.52% | 54% (62%) | +0.00% | +0.09% | +0.72% |  |  |  |
| bybit | ADA -> ADAUSDT | direct | 0.786 | 1.00 | +4.41% | +5.88% | 52% (52%) | +0.00% | +0.61% | +2.08% | $69.5M | $334k / $96k |  |
| okx | ADA -> ADA-USDT-SWAP | direct | 0.814 | 1.00 | +5.25% | +6.42% | 66% (52%) | +0.00% | +1.45% | +2.62% | $31.5M | $416k / $113k |  |
| binance | INJ -> INJUSDT | direct | 0.300 | 1.15 | +4.58% | +5.79% | 53% (38%) | +0.00% | +0.19% | +1.24% |  |  |  |
| okx | BAT -> BAT-USDT-SWAP | direct | 0.021 | 1.57 | -19.90% | -2.26% | 52% (19%) | +0.00% | -16.49% | -5.24% | $2.0M |  |  |
| bybit | KAIA -> KAIAUSDT | direct | 0.063 | 1.50 | -420.23% | -93.67% | 73% (45%) | +0.00% | -283.06% | -66.05% | $7.4M |  |  |
| binance | PIXEL -> PIXELUSDT | direct | 0.100 | 1.45 | +6.88% | +10.00% | 97% (88%) | +0.00% | +0.95% | +3.10% | $3.6M | $9k / $8k |  |
| binance | AERO -> AEROUSDT | direct | 0.300 | 1.15 | +10.49% | +9.46% | 80% (95%) | +0.00% | +5.32% | +4.43% | $50.5M | $60k / $24k |  |
| okx | OP -> OP-USDT-SWAP | direct | 0.116 | 1.43 | +3.43% | +4.60% | 53% (48%) | +0.00% | -1.40% | -0.58% | $6.1M |  |  |

## Known cases: Hyperliquid portfolio margin

| venue | asset -> perp | match | c at $1M | K | 7d APR | 30d APR | at floor 30d (7d) | borrow | excess 7d | excess 30d | OI | perp bid / spot ask <=25bp | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hyperliquid | HYPE -> HYPE | direct | 0.650 | 1.00 | +8.40% | +9.39% | 75% (84%) | +0.50% | +4.10% | +5.09% | $1.7B | $185k / $159k |  |
| hyperliquid | UBTC -> BTC | wrapped | 0.500 | 1.00 | +8.50% | +8.88% | 63% (67%) | +0.50% | +4.20% | +4.58% | $3.2B | $4.3M / $574k |  |

- HYPE: API 30d +9.39%, at floor 75.3%; same window from perp_daily's store (to 2026-10-10T22:00:00+00:00): +9.39% vs API +9.39% (n 721 vs 721, agree True); term_carry 2026 year-to-date mean +9.13%.
- BTC: API 30d +8.88%, at floor 62.6%; same window from perp_daily's store (to 2026-10-10T22:00:00+00:00): +8.92% vs API +8.92% (n 721 vs 721, agree True); term_carry 2026 year-to-date mean +5.19%.
- HYPE caps: user supply cap $85.5M, global supply room $954.0M.
- UBTC caps: user supply cap $16.6M, global supply room $230.1M.

## Errors and notes

{"carry_errors": {}, "notes": []}

## Endpoint gaps

- Hyperliquid: the info API serves portfolio-margin eligibility, LTV and borrow/supply rates (allBorrowLendReserveStates) but not the supply/borrow caps or the account requirements; those are parsed from the docs page and hashed per section.
- Binance: the official portfolio-margin collateral endpoints (/sapi/v1/portfolio/collateralRate, /sapi/v2/portfolio/collateralRate) need an API key; the website bapi endpoints used here are public but undocumented. Leverage brackets (true max leverage, maintenance tiers) are keyed (/fapi/v1/leverageBracket); requiredMarginPercent from exchangeInfo is used. Whether TradFi perps can be margined by portfolio-margin collateral is not stated by any public endpoint.
- Binance multi-assets mode: /fapi/v1/assetIndex lists 29 index assets but exchangeInfo marks only the marginAvailable ones as collateral; the haircut is read as the bid buffer.
- OKX: discount tiers are in units of the currency (disCcyEq = maxAmt x rate) and need a spot price to read at $1M; loan rates are the basic daily rates (VIP discounts not applied).
- Bybit: the single collateralRatio in /v5/spot-margin-trade/data is deprecated by the tiered logic; tiers from /v5/spot-margin-trade/collateral are used. Account-level collateral switches (/v5/account/collateral-info) are keyed.
- Deribit: the API serves the cross-collateral pool (get_currencies.in_cross_collateral_pool) and X:PM haircuts (public/pme/get_params) but not the standard-margin (X:SM) haircuts; those come from the support article (Zendesk help-centre JSON), hashed. Deribit funding has no interest leg (a dead band around zero), so its floor share counts hours at exactly 0.
- No venue publishes the borrow cost of its portfolio-margin negative balances as an API field except Hyperliquid (borrowYearlyRate); Binance/OKX/Bybit margin borrow rates are used as the stand-in, Deribit's collateral fee comes from the article.
