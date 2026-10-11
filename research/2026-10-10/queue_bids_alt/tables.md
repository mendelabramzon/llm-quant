# queue_bids_alt — tables

Generated 2026-10-10T22:09:34Z from `analysis.json` by `scripts/queue_bids_alt.py render`.

## A. Candidates by DEX liquidity against the native coin (GeckoTerminal 24h, 2026-10-10)

| rank | LST | chain | 24h volume | reserves | queue | redemption | instant route | deep |
|---:|---|---|---:|---:|---|---|---|---|
| 1 | JitoSOL | solana | $1,937,523 | $12,349,064 | 2.5 d | anyone: withdraw stake, deactivate | Sanctum router / Infinity, fee | yes |
| 2 | kHYPE | hyperevm | $1,475,146 | $7,320,971 | 7 d | anyone: queueWithdrawal(kHYPE) then confirmWithdrawal(id) af | none: instantUnstake facet not deployed (calls rev | yes |
| 3 | JupSOL | solana | $440,227 | $204,601 | 2.5 d | anyone | Sanctum |  |
| 4 | bSOL | solana | $305,814 | $1,105,605 | 2.5 d | anyone | Sanctum |  |
| 5 | mSOL | solana | $186,674 | $3,091,625 | 2.5 d | anyone | Marinade pool, Sanctum |  |
| 6 | tsTON | ton | $164,604 | $192,902 | 1.5 d | anyone | Tonstakers instant when the pool has liquidity |  |
| 7 | slisBNB | bsc | $150,009 | $4,072,750 | 8 d | anyone: requestWithdraw fixes the BNB amount at the request; | instantWithdraw is whitelist-only (instantWhitelis | yes |
| 8 | INF | solana | $126,574 | $336,879 | 0 d | anyone | itself |  |
| 9 | LHYPE | hyperevm | $68,566 | $413,372 | ? | vault redemption |  |  |
| 10 | hSOL | solana | $67,426 | $43,123 | 2.5 d | anyone | Sanctum |  |
| 11 | aprMON | monad | $63,397 | $39,115 | 1 d | anyone: ERC-7540 requestRedeem then redeem |  | yes |
| 12 | stS | sonic | $33,957 | $505,232 | 14 d | anyone |  | yes |
| 13 | haSUI | sui-network | $30,396 | $4,039,043 | 1 d | anyone | Haedal instant, fee |  |
| 14 | shMON | monad | $22,911 | $938,574 | ? | anyone |  |  |
| 15 | sAVAX | avax | $20,308 | $1,240,644 | 15 d | anyone: requestUnlock then redeem inside the redeem window |  | yes |
| 16 | afSUI | sui-network | $10,368 | $62,695 | 1 d | anyone | Aftermath instant, fee |  |
| 17 | stNEAR | near | $9,554 | $91,748,183 | 2.5 d | anyone | Meta Pool liquidity, fee |  |
| 18 | stHYPE | hyperevm | $6,181 | $262,516 | 7 d | anyone via the overseer (docs) | Valantis STEX AMM |  |
| 19 | LiNEAR | near | $5,856 | $5,171,657 | 2.5 d | anyone | LiNEAR pool, fee |  |
| 20 | wstHYPE | hyperevm | $5,789 | $181,151 | 7 d | unwrap to stHYPE |  |  |
| 21 | vSUI | sui-network | $4,370 | $398,158 | 1 d | anyone | Volo instant, fee |  |
| 22 | beHYPE | hyperevm | $4,163 | $30,127 | 7 d | anyone (docs) | instant withdrawal with a fee when liquidity allow |  |
| 23 | sMON | monad | $3,938 | $13,091 | ? | anyone |  |  |
| 24 | amAPT | aptos | $1,913 | $355,867 | 30 d | anyone |  |  |
| 25 | mHYPE | hyperevm | $1,892 | $24,904 | 7 d |  |  |  |
| 26 | iBERA | berachain | $1,471 | $18,163 | ? |  |  |  |
| 27 | BNSOL | solana | $943 | $830,374 | 2.5 d | anyone | Sanctum |  |
| 28 | OS | sonic | $843 | $28,212 | 1 d | anyone | ARM |  |
| 29 | asBNB | bsc | $393 | $25,986 | 8 d |  |  |  |
| 30 | BNBx | bsc | $34 | $2,181,387 | 8 d | anyone |  |  |
| 31 | thAPT | aptos | $15 | $467,161 | 30 d | anyone |  |  |
| 32 | ggAVAX | avax | $1 | $5,933 | 0 d | anyone, up to the buffer | the vault itself |  |
| 33 | vDOT | hydration | $0 | $0 | 28 d | anyone via Bifrost |  |  |

Not covered by GeckoTerminal: milkTIA (Osmosis (MilkyWay), 21 days); stATOM (Osmosis (Stride), 21 days); stTIA (Osmosis (Stride), 21 days); vDOT/DOT pair (Bifrost DEX (not indexed); Hydration quotes vDOT against H2O only)

## B. kHYPE queue: what Kinetiq paid (every WithdrawalQueued / WithdrawalConfirmed since launch)

| item | value |
|---|---|
| requests (≥ 0.01 kHYPE) | 15,167 (14,629) |
| HYPE requested / confirmed | 41,434,480 / 41,097,384 |
| confirmations paying exactly the request | 100% of 13,426 (gap min 0.000bp, max 0.000bp) |
| unconfirmed at the end | 1,504 requests, 337,096 HYPE |
| cancelled | 0 |
| unstake fee | 10.0bp on 10,791 requests; set to 0 at 2026-04-08T00:14:01Z |
| rate fixed in no-fee requests vs StakingAccountant (3-hourly samples) | p50 0.00bp, p10–p90 -0.00bp to 0.00bp, p99 0.32bp, min -0.57bp, max 0.51bp (n 3,838) |
| request → confirmation, days | p1 7.00, p5 7.00, median 9.17, p90 27.76, max 443.8 |
| fastest confirmation by month, days | 25-07 8.08, 25-08 7.10, 25-09 7.00, 25-10 7.00, 25-11 7.00, 25-12 7.00, 26-01 7.00, 26-02 7.00, 26-03 7.00, 26-04 7.00, 26-05 7.00, 26-06 7.00, 26-07 7.01, 26-08 7.00, 26-09 7.00, 26-10 7.00 |
| HYPE requested by month | 25-07 100k, 25-08 911k, 25-09 3,770k, 25-10 5,891k, 25-11 11,122k, 25-12 5,049k, 26-01 1,173k, 26-02 1,832k, 26-03 2,216k, 26-04 1,559k, 26-05 2,464k, 26-06 1,328k, 26-07 450k, 26-08 1,026k, 26-09 2,135k, 26-10 402k |

## C. Discounts to the exchange rate, hour by hour (market = volume-weighted across pools)

| LST | source | window | hours traded | p50 | p90 | p99 | max | ≥10bp | ≥20bp | ≥50bp | round trip | episodes (hours) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| aprMON | GeckoTerminal hourly bars (typical price | 2026-03-13 +211d | 4,964 | 18.8bp | 33.3bp | 76.6bp | 276.2bp | 90% | 42% | 3% | 14.7bp | 93 (3774) |
| JitoSOL | GeckoTerminal hourly bars (typical price | 2026-03-13 +211d | 5,064 | 7.4bp | 10.5bp | 26.4bp | 108.9bp | 13% | 2% | 0% | 12.0bp | 175 (279) |
| kHYPE | on-chain swaps reconstructed from kHYPE/ | 2025-07-15 +452d | 10,836 | 9.8bp | 30.1bp | 64.1bp | 260.2bp | 49% | 23% | 2% | 5.9bp | 105 (5301) |
| kHYPE | GeckoTerminal bars | 2026-03-12 +212d | 5,087 | 7.8bp | 20.8bp | 37.6bp | 107.6bp | 33% | 12% | 1% | 5.9bp | 52 (2903) |
| sAVAX | GeckoTerminal hourly bars (typical price | 2026-03-30 +194d | 4,100 | 17.4bp | 52.9bp | 74.8bp | 207.6bp | 69% | 44% | 11% | 22.0bp | 75 (1543) |
| slisBNB | GeckoTerminal hourly bars (typical price | 2026-04-08 +185d | 4,432 | 12.7bp | 17.1bp | 23.9bp | 73.2bp | 80% | 4% | 0% | 4.0bp | 3 (4407) |
| stS | GeckoTerminal hourly bars (typical price | 2026-03-17 +207d | 4,967 | 5.8bp | 42.0bp | 118.0bp | 297.8bp | 43% | 34% | 7% | 19.9bp | 17 (1701) |

## D. The bid, out of sample (hurdle chosen on the first half, scored once on the second)

| LST | source | size | hurdle | in sample $/yr | out of sample $/yr | 95% interval | t | fills OOS | median edge | trailing 90d $/yr | capacity | late 1h | late 1d | ¼ volume as sales | verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| aprMON | GeckoTerminal hourly bars (typical | $100,000 | h=5 | $18,052 | $8,301 | $2,651 to $15,134 | 2.80 | 337 | 14.8bp | $6,872 | $100,000 | 96% | 60% | $3,376 | no-go |
| JitoSOL | GeckoTerminal hourly bars (typical | $1,000,000 | h=0 | $2,054 | $0 | $0 to $0 | — | 0 | 1.0bp | $0 | — | — | — | $0 | no-go |
| kHYPE | on-chain swaps reconstructed from  | $10,000,000 | h=20 | $370,709 | $140,043 | $17,327 to $356,703 | 1.44 | 864 | 24.6bp | $245,331 | $30,000,000 | 76% | 31% | — | proposed |
| kHYPE | same, at the capacity-rule size | $30,000,000 | h=10 | $1,192,401 | $373,849 | $137,989 to $703,305 | 2.65 | 8183 | 15.3bp | $400,475 | $30,000,000 | 87% | 51% | — |  |
| kHYPE | GeckoTerminal bars, same queue mod | $30,000,000 | h=0 | $509,460 | $511,447 | $89,370 to $1,314,524 | 1.61 | 2701 | 6.4bp | $583,189 | $30,000,000 | 99% | 98% | — |  |
| sAVAX | GeckoTerminal hourly bars (typical | $3,000,000 | h=0 | $12,640 | $42,343 | $1,755 to $94,834 | 2.06 | 85 | 10.2bp | $45,636 | $3,000,000 | 74% | 54% | $20,931 | watch (bar-only evidence: $20,931 a year with a quarter of the volume as sales) |
| slisBNB | GeckoTerminal hourly bars (typical | $3,000,000 | h=2 | $113,743 | $2,112 | $1,152 to $3,377 | 3.89 | 172 | 9.3bp | $2,165 | $3,000,000 | 98% | 99% | $866 | no-go |
| stS | GeckoTerminal hourly bars (typical | $1,000,000 | h=0 | $13,476 | $17,090 | $2,101 to $35,797 | 2.19 | 185 | 23.7bp | $7,759 | $1,000,000 | 93% | 72% | $7,726 | watch (positive, below the bar) |

## E. kHYPE in detail

### E1. Size grid (swap-level, 2025-07-15 +452 days, split 2026-02-26T00:00:00Z)

| size | hurdle | in sample | out of sample | 95% interval | fills OOS | filled | missed for capital | median edge | trailing 90d |
|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| $100,000 | h=20 | $3,905 | $1,749 | $441 to $3,279 | 39 | $1,499,695 | $432,807,860 | 20.5bp | $1,071 |
| $1,000,000 | h=20 | $35,360 | $17,139 | $5,014 to $32,194 | 170 | $12,479,618 | $421,833,739 | 21.2bp | $12,171 |
| $10,000,000 | h=20 | $370,709 | $140,043 | $17,327 to $356,703 | 864 | $82,495,606 | $346,965,098 | 24.6bp | $245,331 |
| $300,000 | h=20 | $11,619 | $5,614 | $1,643 to $10,414 | 70 | $4,376,301 | $429,937,056 | 20.6bp | $3,439 |
| $3,000,000 | h=20 | $102,397 | $45,801 | $12,035 to $89,033 | 444 | $32,613,313 | $401,700,044 | 21.9bp | $38,771 |
| $30,000,000 | h=10 | $1,192,401 | $373,849 | $137,989 to $703,305 | 8183 | $398,402,856 | $379,619,063 | 15.3bp | $400,475 |

### E2. Value by month at $10,000,000 (hurdle h=20)

| month | value | | month | value |
|---|---:|---|---|---:|
| 2025-09 | $65,620 | | 2026-03 | $829 |
| 2025-10 | $96,400 | | 2026-04 | $9,558 |
| 2025-11 | $39,316 | | 2026-05 | $15,832 |
| 2025-12 | $26,928 | | 2026-09 | $60,492 |
| 2026-02 | $1,270 | |  |  |

### E3. Variants on the same sales (out of sample $/yr, hurdle chosen in sample)

| variant | $10M | $30M |
|---|---:|---:|
| as quoted: staking carry, fastest-claim wait, venue-median cap | $140,043 (h=20) | $373,849 (h=10) |
| carry at HyperLend WHYPE borrow (bid funded by borrowing HYPE against kHYPE) | $156,977 (h=20) | $363,547 (h=10) |
| fixed 7-day wait | $141,087 (h=20) | $375,712 (h=10) |
| print filter at 1,000bp (keeps the 2025-09-24 depeg sales) | $139,981 (h=20) | $373,788 (h=10) |
| per print, no venue-median cap (an upper bound) | $185,553 (h=20) | $425,807 (h=10) |

### E3b. Same window (2026-03-12 +212 days), same queue model: bars with half the volume as sales vs measured sales

| size | bars $/yr OOS (hurdle) | swaps $/yr OOS (hurdle) | swaps 95% interval |
|---:|---:|---:|---|
| $1,000,000 | $12,476 (h=10) | $10,822 (h=10) | $0 to $26,701 |
| $3,000,000 | $32,081 (h=10) | $29,982 (h=10) | $0 to $78,727 |
| $10,000,000 | $181,069 (h=3) | $189,719 (h=10) | $0 to $560,374 |
| $30,000,000 | $511,447 (h=0) | $433,892 (h=0) | $72,914 to $1,129,610 |

### E4. The same pool-hours priced two ways (GeckoTerminal bar vs swap VWAP rebuilt from chain)

| pool | hours in both | median abs gap | p90 abs gap | signed median | bar volume / swap volume (p50) |
|---|---:|---:|---:|---:|---:|
| hybra-v4 | 4,941 | 0.11bp | 0.55bp | 0.01bp | 1.00 |
| hyperswap-v3 | 3,933 | 0.36bp | 1.03bp | 0.00bp | 1.00 |
| kittenswap-algebra | 3,949 | 0.14bp | 1.41bp | 0.00bp | 1.00 |
| nest | 1,806 | 0.67bp | 5.09bp | 0.00bp | 1.00 |
| project-x | 4,934 | 0.54bp | 1.17bp | -0.00bp | 1.00 |
| ramses-v3 | 4,975 | 0.06bp | 0.41bp | 0.01bp | 1.00 |

Valantis STEX (instant unstake, a competing bidder, not back-runnable): $325,852,267 of volume at a volume-weighted 9.0bp.

### E5. Largest dislocation episodes (market discount above the round trip of 5.9bp)

| start | end | hours | volume | vw discount | peak | net of round trip |
|---|---|---:|---:|---:|---:|---:|
| 2025-09-23T18:00 | 2025-09-30T14:00 | 164 | $372,863,821 | 103.1bp | 260.2bp | 86.1bp |
| 2025-10-10T06:00 | 2025-10-21T19:00 | 277 | $531,176,655 | 54.6bp | 97.9bp | 38.0bp |
| 2025-11-02T16:00 | 2025-11-23T01:00 | 489 | $457,605,563 | 31.3bp | 42.2bp | 14.9bp |
| 2025-12-05T08:00 | 2025-12-24T14:00 | 462 | $202,585,650 | 29.0bp | 44.4bp | 12.6bp |
| 2026-09-19T12:00 | 2026-09-28T05:00 | 208 | $58,326,438 | 46.6bp | 104.2bp | 40.8bp |
| 2026-05-18T04:00 | 2026-06-08T02:00 | 502 | $201,674,365 | 17.5bp | 41.9bp | 11.7bp |
| 2026-02-04T08:00 | 2026-02-20T17:00 | 391 | $123,501,988 | 29.0bp | 37.2bp | 12.8bp |
| 2025-10-22T02:00 | 2025-10-27T12:00 | 129 | $101,570,640 | 21.9bp | 28.4bp | 5.2bp |

## F. Solana: the instant exit against the stake pool (Jupiter quotes vs on-chain rate, 2026-10-10T17:31:33Z)

| LST | rate | withdrawal fee (stake / SOL) | sell 10 | sell 1,000 | sell 10,000 | sell 50,000 | buy 1,000 | buy 10,000 |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| BNSOL | 1.135336 | 10bp / 10bp | -11.6bp | -12.2bp | -20.9bp | -76.4bp | 0.0bp | 0.0bp |
| JitoSOL | 1.305717 | 10bp / 10bp | -7.0bp | -7.3bp | -9.2bp | -15.8bp | -6.7bp | -5.4bp |
| JupSOL | 1.213808 | 10bp / 10bp | -10.0bp | -10.4bp | -14.8bp | -81.2bp | -8.3bp | -0.8bp |
| bSOL | 1.320038 | 10bp / 10bp | -9.6bp | -10.9bp | -11.0bp | -87.7bp | -6.6bp | -0.7bp |

## G. Part (b): long staking token, short the perp on one venue (excess over SSR, per year of capital)

| row | capital | window (split) | rule | in sample | out of sample | t | bootstrap 95% | last 365d | last 90d | funding | staking + basis | borrow | costs |
|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| binance:SOL short, BNSOL collateral | collateral | 2025-02-27 → 2026-10-09 (2025-12-19) | trail30d_x0pp | +1.13% | -0.36% | -0.62 | -1.45% to +0.78% | -0.29% | +0.33% | +1.4% | +2.1% | +0.00% | +1.44% |
| binance:SOL spot (BNSOL window) | collateral | 2025-02-27 → 2026-10-09 (2025-12-19) | trail30d_x2pp | -0.22% | +0.00% | — | +0.00% to +0.00% | +0.00% | +0.00% | +0.8% | +0.0% | +0.00% | +0.38% |
| hl:HYPE short cash 3x, kHYPE spot | cash3x | 2025-07-07 → 2026-10-09 (2026-02-22) | always | +7.41% | +3.44% | 3.06 | +1.58% to +5.11% | +3.98% | +3.54% | +14.7% | +2.5% | +0.00% | +1.73% |
| hl:HYPE short, kHYPE spot (margin borrowed on HyperLend) | collateral | 2025-07-07 → 2026-10-09 (2026-02-22) | always | +10.14% | +4.48% | 2.93 | +1.87% to +6.64% | +5.35% | +5.17% | +14.7% | +2.5% | +1.91% | +3.23% |
| hl:HYPE short, kHYPE spot, staking only | collateral | 2025-07-07 → 2026-10-09 (2026-02-22) | always | +10.27% | +4.41% | 4.22 | +2.11% to +6.32% | +5.29% | +5.26% | +14.7% | +2.6% | +1.91% | +3.23% |
| hl:HYPE | collateral | 2024-12-06 → 2026-10-09 (2025-11-07) | always | +25.23% | +4.30% | 5.68 | +2.85% to +5.66% | +4.03% | +4.16% | +37.4% | +0.0% | +1.43% | +3.31% |
| hl:HYPE (kHYPE window) | collateral | 2025-07-07 → 2026-10-09 (2026-02-22) | always | +9.08% | +3.27% | 3.27 | +1.06% to +5.15% | +4.03% | +4.16% | +14.7% | +0.0% | +1.01% | +2.11% |
| hl:SOL cash 3x (JitoSOL window) | cash3x | 2024-01-02 → 2026-10-09 (2025-05-22) | trail30d_x2pp | +11.75% | +0.61% | 0.91 | -0.91% to +2.32% | -0.96% | -0.07% | +34.2% | +0.0% | +0.00% | +2.88% |
| hl:SOL short cash 3x, JitoSOL spot | cash3x | 2024-01-02 → 2026-10-09 (2025-05-22) | always | +17.05% | +2.41% | 2.43 | -0.55% to +5.31% | -0.37% | +4.08% | +33.3% | +18.9% | +0.00% | +2.50% |

Staking yield over each window: kHYPE +2.05%, BNSOL +5.36% (DefiLlama apyBase), JitoSOL +6.83% (Jito API). HyperLend USDT0 borrow used for the kHYPE margin: +10.40%.
- Drift (JitoSOL/mSOL/INF cross-margin) not tested: data.api.drift.trade and its CloudFront host do not resolve and the public S3 history bucket (drift-historical-data-v2) is empty (2026-10-10).
- Hyperliquid portfolio margin accepts USDC, USDT, HYPE and BTC only (docs read 2026-10-10): no LST can collateralise the short on HyperCore, so the kHYPE rows borrow the margin on HyperLend.

## H. Independent checks

- **jitosol_rate_api_vs_chain**: `{"api_rate": 1.3055308765106586, "api_utc": "2026-10-10T16:37:39Z", "gap_bps": 1.4232257863788789, "onchain_epoch": 1054, "onchain_rate": 1.305716683031495, "snapshot_utc": "2026-10-10T17:31:33Z"}`
- **jitosol_yield_two_paths**: `{"api_rate_growth_365d": 0.05599108655790941, "llama_mean_apyBase_365d": 0.05612191780821917}`
- **khype_nav_two_paths**: `{"max": 0.5073596076710096, "min": -0.5669393434981629, "n": 3838, "p10": -0.004964352268266301, "p50": 0.0, "p90": 0.004812484685423617, "p99": 0.31774449668371396, "share_ge_10bp": 0.0, "share_ge_20bp": 0.0, "share_ge_50bp": 0.0, "share_ge_5bp": 0.0}`

## I. API gaps recorded (not guessed)

- GeckoTerminal public API serves OHLCV for the last 180 days only (401 beyond): the bar-based assets have ~7 months
- GeckoTerminal does not index Osmosis or other Cosmos chains: stTIA, milkTIA, stATOM not measurable here
- GeckoTerminal does not list Valantis STEX (kHYPE) pools: read from chain instead
- Drift data API host does not resolve and its S3 history bucket is empty: JitoSOL-on-Drift carry not testable
- Sanctum extra-api sol-value/current returned rates 2.3-2.5% below the on-chain stake pools (stale): not used
- Several public HyperEVM RPCs (rpc.hyperliquid.xyz/evm, rpc.hypurrscan.io, stakely) ignore the block tag on eth_call
- LiquidSwap route API returned a nonsensical route (65% impact via USOL) for WHYPE->kHYPE: no live depth quote for kHYPE
- BSC: publicnode/drpc/official seeds refused archive reads; blastapi served them
- TON (tsTON) and Hydration (vDOT vs H2O) not priced: no free exchange-rate history found
- Monad: rpc1.monad.xyz and rpc-mainnet.monadinfra.com answer single calls but 403 any JSON-RPC batch; rpc2 serves both
- Avalanche public archive (api.avax.network) takes ~12 s a call: sAVAX rate sampled every 12 h, no swap-level rebuild
