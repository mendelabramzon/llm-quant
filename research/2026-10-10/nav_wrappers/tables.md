# nav_wrappers — tables (generated 2026-10-10T18:32:50+00:00)

Every number is from `analysis.json`; method in `scripts/nav_wrappers.py`; sources in `manifest.json`.

## (a) Trusts

### A1. NAV check: coin per share (XBRL) x Binance at 16:00 New York vs the sponsor's NAV per share

| trust | quarter-ends | median abs error | max abs error | anchors replaced | implied fee range |
|---|---:|---:|---:|---:|---|
| BCHG | 22 | 0.13% | 0.56% | 0 | 2.50%..4.33% |
| ETCG | 22 | 0.08% | 0.50% | 0 | 2.50%..3.74% |
| ETHE | 25 | 0.04% | 0.40% | 0 | 0.91%..3.64% |
| GBTC | 27 | 0.05% | 0.38% | 0 | 0.57%..2.48% |
| GLNK | 8 | 0.08% | 0.25% | 0 | 0.11%..2.50% |
| GSOL | 4 | 0.03% | 0.19% | 0 | 2.50%..2.50% |
| GTAO | 6 | 0.13% | 0.40% | 0 | 2.50%..3.35% |
| GXLM | 17 | 0.07% | 0.19% | 0 | 2.50%..2.50% |
| HZEN | 10 | 0.37% | 0.81% | 1 | 2.50%..3.65% |
| LTCN | 23 | 0.05% | 1.31% | 0 | 2.50%..3.10% |
| OBTC | 10 | 0.44% | 0.51% | 1 | 0.71%..3.18% |
| ZCSH | 17 | 0.20% | 0.56% | 0 | 2.50%..2.50% |

### A2. Conversion events (long trust, short coin perp; enter at the first close on or after the filing, exit at the first exchange close; open trades marked 2026-10-09)

| trust | set | filing | disc at filing | worst (date) | last OTC | at exit | excess on capital, NAV hedge | per year | max DD | $ hedge excess | funding sum | 1d late kept | 1w late kept | ADV at filing |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GBTC | early | 2021-10-19 | -18.3% | -48.7% (2022-12-13) | -1.5% | -1.3% | +17.8% | +8.0% | 7.3% | +11.8% | +16.8% | 89% | 77% | $281.7M |
| ETHE | early | 2023-10-02 | -31.8% | -32.9% (2023-10-04) | -1.3% | +0.2% | +43.1% | +53.3% | 29.4% | +62.6% | +12.3% | 102% | 91% | $21.8M |
| GSOL | late | 2024-12-03 | +98.2% | -1.4% (2025-07-03) | +0.6% | +0.0% | -48.2% | -53.3% | 43.2% | -38.9% | +1.0% | 92% | 97% | $3.7M |
| OBTC | late | 2024-08-27 | -3.3% | -14.4% (2025-05-29) | +0.2% | -0.1% | +0.4% | +0.3% | 14.0% | +0.7% | +8.3% | -67% | 113% | $0.3M |
| GLNK | late | 2025-09-08 | +99.6% | +0.2% (2025-12-02) | +12.2% | +0.2% | -44.1% | -189.5% | 45.8% | -29.7% | +1.2% | 94% | 103% | $1.2M |
| ZCSH | late | 2025-11-26 | -17.6% | -27.9% (2026-01-06) | -1.3% | +0.0% | +7.5% | +10.0% | 24.6% | -0.7% | -3.0% | 22% | 12% | $5.4M |
| LTCN | pending | 2025-01-24 | +32.4% | -16.2% (2026-08-07) | — | -4.8% | -28.3% | -16.6% | 24.3% | -29.4% | +7.4% | 65% | 28% | $3.8M |
| BCHG | pending | 2025-09-09 | -13.5% | -21.8% (2026-02-11) | — | -4.6% | -0.5% | -0.4% | 17.2% | -6.1% | -4.1% | -91% | -424% | $0.7M |
| GXLM | pending | 2025-09-24 | +6.7% | -1.5% (2025-11-19) | — | +50.7% | +5.6% | +5.4% | 11.0% | +5.8% | -0.6% | 126% | 106% | $0.8M |
| GTAO | pending | 2025-12-30 | +107.7% | +18.4% (2026-03-20) | — | +28.0% | -39.8% | -51.4% | 121.5% | -42.0% | -1.5% | 111% | 152% | $0.2M |

### A3. Entry rule chosen on the early conversions, tested on 2025-26 (pooled excess per year of capital)

| variant | early n | early | late n | late | late per trade | pending n | pending per trade (marked) |
|---|---:|---:|---:|---:|---|---:|---|
| disc<0 | 2 | +20.0% | 3 | +2.3% | GSOL -2.5%, OBTC +0.4%, ZCSH +7.5% | 3 | LTCN -7.9%, BCHG -0.5%, GXLM +24.3% |
| disc<=-10% | 2 | +20.0% | 2 | +9.4% | OBTC +5.5%, ZCSH +7.5% | 2 | LTCN +1.1%, BCHG -0.5% |
| disc<=-20% | 2 | +21.7% | 1 | +15.7% | ZCSH +10.7% | 1 | BCHG +10.2% |
| disc<=-30% (chosen) | 2 | +29.9% | 0 | — |  | 0 |  |
| disc<=-5% | 2 | +20.0% | 2 | +5.2% | OBTC +2.2%, ZCSH +7.5% | 2 | LTCN -3.6%, BCHG -0.5% |

### A4. Discount buckets, forward 63-day hedged excess on capital (dollar hedge; early < 2025, late >= 2025)

| period | state | discount | trust-days | trusts | mean | NW t | hit |
|---|---|---|---:|---:|---:|---:|---:|
| early | no_filing | +0%..+inf | 3950 | 11 | +1.9% | 0.38 | 47% |
| early | no_filing | -10%..-5% | 530 | 9 | +3.4% | 0.85 | 62% |
| early | no_filing | -20%..-10% | 869 | 9 | +5.9% | 1.31 | 55% |
| early | no_filing | -30%..-20% | 861 | 9 | +4.5% | 1.26 | 59% |
| early | no_filing | -5%..+0% | 362 | 9 | +4.2% | 0.66 | 46% |
| early | no_filing | -inf..-30% | 2033 | 8 | +9.3% | 4.04 | 72% |
| early | pending | +0%..+inf | 20 | 1 | -29.3% | — | 0% |
| early | pending | -10%..-5% | 49 | 3 | +4.1% | — | 78% |
| early | pending | -20%..-10% | 194 | 2 | +1.9% | 0.70 | 52% |
| early | pending | -30%..-20% | 234 | 2 | +7.3% | 1.73 | 64% |
| early | pending | -5%..+0% | 115 | 3 | -1.0% | -1.01 | 35% |
| early | pending | -inf..-30% | 258 | 2 | +4.5% | 1.00 | 57% |
| late | no_filing | +0%..+inf | 964 | 7 | -6.2% | -1.61 | 35% |
| late | no_filing | -10%..-5% | 87 | 4 | +1.6% | 2.97 | 47% |
| late | no_filing | -20%..-10% | 76 | 4 | +14.9% | 3.75 | 87% |
| late | no_filing | -30%..-20% | 110 | 3 | -0.8% | -0.19 | 22% |
| late | no_filing | -5%..+0% | 65 | 4 | +0.9% | — | 42% |
| late | no_filing | -inf..-30% | 355 | 2 | +1.1% | 0.95 | 56% |
| late | pending | +0%..+inf | 812 | 7 | -5.0% | -2.45 | 40% |
| late | pending | -10%..-5% | 472 | 4 | -0.3% | -0.27 | 50% |
| late | pending | -20%..-10% | 322 | 4 | +3.6% | 2.99 | 72% |
| late | pending | -30%..-20% | 33 | 2 | +16.3% | — | 100% |
| late | pending | -5%..+0% | 213 | 6 | -2.3% | -2.13 | 31% |

### A4. Discount buckets, forward 63-day hedged excess on capital (NAV hedge; early < 2025, late >= 2025)

| period | state | discount | trust-days | trusts | mean | NW t | hit |
|---|---|---|---:|---:|---:|---:|---:|
| early | no_filing | +0%..+inf | 3950 | 11 | +12.8% | 1.92 | 52% |
| early | no_filing | -10%..-5% | 530 | 9 | +3.5% | 1.01 | 54% |
| early | no_filing | -20%..-10% | 869 | 9 | +5.9% | 1.39 | 51% |
| early | no_filing | -30%..-20% | 861 | 9 | +4.8% | 1.41 | 57% |
| early | no_filing | -5%..+0% | 362 | 9 | +5.8% | 0.78 | 40% |
| early | no_filing | -inf..-30% | 2033 | 8 | +6.3% | 2.17 | 68% |
| early | pending | +0%..+inf | 20 | 1 | -41.9% | — | 0% |
| early | pending | -10%..-5% | 49 | 3 | +3.6% | — | 78% |
| early | pending | -20%..-10% | 194 | 2 | +0.7% | 0.44 | 51% |
| early | pending | -30%..-20% | 234 | 2 | +9.1% | 5.04 | 90% |
| early | pending | -5%..+0% | 115 | 3 | -1.4% | -1.29 | 35% |
| early | pending | -inf..-30% | 258 | 2 | -0.6% | -0.15 | 43% |
| late | no_filing | +0%..+inf | 964 | 7 | -8.7% | -1.73 | 33% |
| late | no_filing | -10%..-5% | 87 | 4 | -0.4% | -0.46 | 43% |
| late | no_filing | -20%..-10% | 76 | 4 | +13.4% | 4.39 | 88% |
| late | no_filing | -30%..-20% | 110 | 3 | +2.9% | 0.48 | 62% |
| late | no_filing | -5%..+0% | 65 | 4 | +0.1% | — | 45% |
| late | no_filing | -inf..-30% | 355 | 2 | +4.6% | 1.90 | 63% |
| late | pending | +0%..+inf | 812 | 7 | -5.3% | -1.94 | 41% |
| late | pending | -10%..-5% | 472 | 4 | -0.4% | -0.46 | 51% |
| late | pending | -20%..-10% | 322 | 4 | +5.0% | 7.31 | 90% |
| late | pending | -30%..-20% | 33 | 2 | +18.8% | — | 100% |
| late | pending | -5%..+0% | 213 | 6 | -2.4% | -2.01 | 31% |

### A5. Daily trust rules (dollar hedge): chosen on 2019-09..2024-12, tested 2025-01..2026-10

Chosen: **disc<=-5%|any**; test +20.8% a year over the savings rate (calendar), NW t 1.80, rank 1 of 8, deflated Sharpe 0.93, BH survivors (full sample): disc<=-5%|any, disc<=-10%|any. Late entry keeps 77% (1 day) and 52% (1 week) of the test excess.

| variant | in-sample excess / yr | test excess / yr | test active days |
|---|---:|---:|---:|
| disc<=-10%|any | +17.4% | +27.6% | 444 |
| disc<=-10%|filing | +9.3% | +17.3% | 303 |
| disc<=-20%|any | +14.9% | +25.6% | 444 |
| disc<=-20%|filing | +9.0% | +15.6% | 129 |
| disc<=-30%|any | +17.2% | +6.6% | 444 |
| disc<=-30%|filing | +6.6% | +0.0% | 0 |
| disc<=-5%|any | +16.9% | +20.8% | 444 |
| disc<=-5%|filing | +9.3% | +8.9% | 444 |

### A5. Daily trust rules (NAV hedge): chosen on 2019-09..2024-12, tested 2025-01..2026-10

Chosen: **disc<=-30%|any**; test +24.2% a year over the savings rate (calendar), NW t 0.92, rank 7 of 8, deflated Sharpe 0.80, BH survivors (full sample): none. Late entry keeps 74% (1 day) and 74% (1 week) of the test excess.

| variant | in-sample excess / yr | test excess / yr | test active days |
|---|---:|---:|---:|
| disc<=-10%|any | +15.7% | +38.1% | 444 |
| disc<=-10%|filing | +6.7% | +20.0% | 303 |
| disc<=-20%|any | +14.5% | +41.0% | 444 |
| disc<=-20%|filing | +6.3% | +26.4% | 129 |
| disc<=-30%|any | +21.6% | +24.2% | 444 |
| disc<=-30%|filing | +2.7% | +0.0% | 0 |
| disc<=-5%|any | +13.2% | +26.5% | 444 |
| disc<=-5%|filing | +6.8% | +11.1% | 444 |

### A6. Dollar P&L of test-period trades at capacity (10% of 60-day ADV x 5 days), dollar hedge

| rule | trades | excess $ / yr | mean trade excess | hit | by trust (excess $) |
|---|---:|---:|---:|---:|---|
| dollar|disc<=-10%|any | 24 | $0.9M | +6.0% | 96% | BCHG $0.1M, ETCG $0.1M, GXLM $0.0M, HZEN $0.0M, LTCN $0.0M, OBTC $0.0M, ZCSH $1.4M |
| dollar|disc<=-10%|filing | 11 | $0.6M | +5.4% | 91% | BCHG $0.0M, LTCN $0.0M, OBTC $0.0M, ZCSH $1.1M |
| dollar|disc<=-5%|any | 37 | $0.2M | +3.9% | 86% | BCHG $0.0M, ETCG $-0.9M, GXLM $0.1M, HZEN $0.0M, LTCN $0.2M, OBTC $0.0M, ZCSH $0.9M |

### A7. Trusts on 2026-10-09

| trust | coin | venue | status | filing | close | NAV | discount | ADV60 | spread est. | capacity |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| GBTC | BTC | PCX | listed | 2021-10-19 | 63.54 | 63.60 | -0.1% | $106.5M | 0.0% | $53.3M |
| ETHE | ETH | PCX | listed | 2023-10-02 | 19.85 | 19.88 | -0.1% | $48.3M | 0.0% | $24.1M |
| ETCG | ETC | OQX | no conversion filing | — | 4.01 | 6.35 | -36.9% | $0.1M | 0.0% | $0.1M |
| BCHG | BCH | OQX | pending conversion | 2025-09-09 | 2.10 | 2.20 | -4.6% | $0.4M | 0.0% | $0.2M |
| LTCN | LTC | OQX | pending conversion | 2025-01-24 | 4.85 | 5.10 | -4.8% | $0.6M | 0.0% | $0.3M |
| ZCSH | ZEC | PCX | listed | 2025-11-26 | 32.02 | 32.01 | +0.0% | $36.4M | 0.0% | $18.2M |
| GXLM | XLM | OQX | pending conversion | 2025-09-24 | 23.75 | 15.76 | +50.7% | $0.2M | 2.5% | $0.1M |
| GSOL | SOL | PCX | listed | 2024-12-03 | 8.21 | 7.79 | +5.4% | $22.3M | 0.0% | $11.1M |
| GLNK | LINK | PCX | listed | 2025-09-08 | 11.28 | 11.30 | -0.2% | $4.7M | 0.0% | $2.3M |
| GTAO | TAO | OQX | pending conversion | 2025-12-30 | 6.55 | 5.12 | +28.0% | $0.2M | 1.9% | $0.1M |
| HZEN | ZEN | OQX | no conversion filing | — | 0.84 | 0.51 | +62.9% | $0.1M | 5.2% | $0.0M |
| MANA | MANA | OQB | no conversion filing | — | 0.81 | — | — | $0.0M | 9.0% | $0.0M |
| FILG | FIL | OQB | no conversion filing | — | 2.61 | — | — | $0.1M | 5.9% | $0.0M |
| GLIV | LPT | OQB | no conversion filing | — | 2.34 | — | — | $0.0M | 2.0% | $0.0M |
| GBAT | BAT | OQB | no conversion filing | — | 1.10 | — | — | $0.0M | 7.4% | $0.0M |
| GSNR | NEAR | OQB | pending conversion | 2026-01-20 | 7.80 | — | — | $0.2M | 2.1% | $0.1M |
| STCK | STX | OQB | no conversion filing | — | 3.11 | — | — | $0.0M | 3.7% | $0.0M |
| OBTC | BTC | NGM | listed | 2024-08-27 | 26.33 | 25.91 | +1.6% | $0.1M | 0.0% | $0.1M |
| OBNB | BNB | OQX | no conversion filing | — | 16.60 | — | — | $0.0M | 1.9% | $0.0M |
| OBNK | BONK | OQX | no conversion filing | — | 1.22 | — | — | $0.0M | 0.0% | $0.0M |
| GDLC | basket | PCX | listed | 2024-10-15 | 37.23 | — | — | $1.2M | 0.0% | $0.6M |
| BITW | basket | PCX | listed | 2024-11-14 | 53.24 | — | — | $1.5M | 0.0% | $0.8M |
| DEFG | basket | OQB | no conversion filing | — | 14.81 | — | — | $0.0M | 1.9% | $0.0M |

### A8. Basket trusts: sponsor NAV per share at quarter-ends vs the close

- GDLC (filing 2024-10-15, listed 2025-09-19): 2024-09-30 -36.7%, 2024-12-31 +23.9%, 2025-03-31 -8.6%, 2025-06-30 -2.1%, 2025-09-30 -0.0%, 2025-12-31 -15.6%, 2026-03-31 +0.2%, 2026-06-30 +0.1%
- BITW (filing 2024-11-14, listed 2025-12-09): 2024-09-30 -37.0%, 2024-12-31 -10.6%, 2025-03-31 -9.0%, 2025-06-30 -6.6%, 2025-09-30 -2.2%, 2025-12-31 -0.4%, 2026-03-31 -0.0%, 2026-06-30 -0.2%

## (b) DATs

### B1. Live: three ratios on 2026-10-09 (sorted by true mNAV; flags in analysis.json)

| DAT | coin | coins | coin value | cash | debt | preferred | market cap | naive | EV | true | true, 10-Q holdings | ADV60 | stock perp | 10-Q check | flags |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| GDC | BTC | 7,500 | $617.5M | $7.2M | $0.0M | $0.0M | $5.6M | 0.01 | -0.00 | 0.01 | — | $2.2M | — | — | non-pure: operating business; implausible true mNAV 0.01: asset existence/ownership or sha |
| NXTT | BTC | 5,833 | $480.3M | $159.0M | $0.6M | $0.0M | $7.8M | 0.02 | -0.31 | 0.01 | — | $1.3M | — | — | non-pure: operating business; implausible true mNAV 0.01: asset existence/ownership or sha |
| DDC | BTC | 2,899 | $238.7M | $2.5M | $30.0M | $0.0M | $11.6M | 0.05 | 0.16 | 0.05 | — | $1.1M | — | — | non-pure: operating food business; implausible true mNAV 0.05: asset existence/ownership or sha |
| HYPD | HYPE | 1,930,000 | $161.1M | $9.6M | $8.4M | $0.0M | $52.0M | 0.32 | 0.32 | 0.32 | 0.41 | $1.6M | — | 0.79 |  |
| FGNX | ETH | 40,093 | $99.3M | $24.9M | $1.8M | $15.5M | $34.7M | 0.35 | 0.27 | 0.32 | 0.59 | $0.5M | — | 0.52 | holdings check: 10-Q implies ~20,700 ETH at 2026-03-31 vs Co |
| SKYA | SOL | 2,077,799 | $225.4M | $12.1M | $0.0M | $0.0M | $78.2M | 0.35 | 0.29 | 0.33 | 0.35 | $0.5M | — | 0.94 |  |
| FRMM | ETH | 69,802 | $172.9M | $4.1M | $25.9M | $0.0M | $59.2M | 0.34 | 0.47 | 0.39 | 4.90 | $0.9M | — | 0.20 | holdings check: 10-Q implies ~13,700 ETH at 2026-06-30 vs Co |
| BTCS | ETH | 70,787 | $175.4M | $0.3M | $13.5M | $0.0M | $64.3M | 0.37 | 0.44 | 0.40 | — | $2.4M | — | 0.04 | holdings check: 10-Q fair value covers ~2,900 ETH vs CoinGec |
| TONX | TON | 219,709,826 | $303.2M | $28.8M | $0.0M | $0.0M | $182.0M | 0.60 | 0.51 | 0.55 | 0.52 | $1.1M | — | 1.05 | no live Binance perp on TON (hedge leg unavailable there) |
| EMPD | BTC | 1,514 | $124.7M | $74.0M | $45.0M | $0.0M | $85.9M | 0.69 | 0.46 | 0.56 (0.97) | — | $1.0M | — | 0.99 | holdings check: 8-K 2026-07-10: 1,514 BTC vs dashboards ~2,9 |
| BNC | BNB | 515,054 | $379.9M | $7.1M | $16.8M | $0.0M | $216.6M | 0.57 | 0.60 | 0.58 | 0.58 | $10.8M | BNCUSDT | 1.01 |  |
| HSDT | SOL | 2,064,717 | $224.0M | $3.6M | $0.0M | $4.0M | $137.2M | 0.61 | 0.61 | 0.61 | 0.55 | $0.9M | — | 1.12 |  |
| FWDI | SOL | 7,550,000 | $819.1M | $11.0M | $0.0M | $0.0M | $542.0M | 0.66 | 0.65 | 0.65 | 1.07 | $11.7M | FWDIUSDT | 0.61 | holdings check: 10-Q fair value implies ~4.57M SOL vs CoinGe |
| NAKA | BTC | 4,467 | $367.8M | $19.1M | $164.7M | $0.0M | $152.8M | 0.42 | 0.81 | 0.69 | 0.69 | $1.4M | — | 1.00 | holdings check: 10-Q units tag 3,805 BTC vs fair value-impli |
| SBET | ETH | 868,699 | $2.15B | $56.2M | $0.0M | $0.0M | $1.86B | 0.87 | 0.84 | 0.84 | 32.26 | $66.9M | — | 0.00 |  |
| LITS | LTC | 650,716 | $41.1M | $5.7M | $0.0M | $0.0M | $41.2M | 1.00 | 0.86 | 0.88 | — | $0.6M | — | — |  |
| SUIG | SUI | 108,368,594 | $114.4M | $3.1M | $0.0M | $0.0M | $107.5M | 0.94 | 0.91 | 0.91 | — | $0.9M | — | — |  |
| BMNR | ETH | 5,390,404 | $13.35B | $340.3M | $0.0M | $0.0M | $13.93B | 1.04 | 1.02 | 1.02 | 1.01 | $871.9M | BMNRUSDT | 1.01 |  |
| DFDV | SOL | 2,294,576 | $248.9M | $4.3M | $120.6M | $0.0M | $137.9M | 0.55 | 1.02 | 1.04 | — | $8.6M | — | 0.39 | holdings check: 10-Q fair value implies ~0.88M SOL vs CoinGe |
| MSTR | BTC | 848,000 | $69.82B | $5.71B | $6.71B | $13.95B | $65.14B | 0.93 | 1.15 | 1.19 | 1.19 | $2.84B | MSTRUSDT | 1.00 |  |
| BRR | BTC | 5,405 | $450.7M | $15.3M | $184.5M | $0.0M | $346.3M | 0.77 | 1.14 | 1.23 | 1.26 | $17.2M | — | 0.99 |  |
| XXI | BTC | 43,514 | $3.58B | $117.7M | $484.3M | $0.0M | $4.10B | 1.14 | 1.25 | 1.27 | — | $11.4M | — | — |  |
| 3350.T | BTC | 44,000 | $3.62B | $65.8M | $1.78B | $149.1M | $2.28B | 0.63 | 1.14 | 1.29 | — | $48.0M | — | — | capital structure history not reliable (debt/preferred from  |
| SWC.L | BTC | 2,747 | $228.1M | $1.0M | $24.9M | $0.0M | $281.1M | 1.23 | 1.34 | 1.38 | — | $1.1M | — | — |  |
| PURR | HYPE | 17,600,000 | $1.47B | $137.9M | $0.0M | $0.0M | $2.23B | 1.52 | 1.42 | 1.39 | 0.86 | $207.4M | xyz:PURRDAT? | 1.66 |  |
| ASST | BTC | 29,462 | $2.43B | $145.5M | $0.0M | $702.4M | $2.81B | 1.16 | 1.39 | 1.50 | — | $169.9M | — | — |  |
| ORBS | WLD | 277,222,975 | $136.9M | $11.0M | $0.0M | $0.0M | $361.0M | 2.64 | 2.56 | 2.44 | 1.26 | $12.8M | — | 2.02 | holdings check: 10-Q fair value implies ~559M WLD vs CoinGec |
| TRON | TRX | 691,236,729 | $229.7M | $0.0M | $0.0M | $0.0M | $595.3M | 2.59 | 2.59 | 2.59 | 2.42 | $1.5M | — | 1.07 |  |
| UPXI | SOL | 2,173,204 | $235.8M | $5.8M | $219.7M | $0.0M | $86.6M | 0.37 | 1.27 | 3.97 | 0.27 | $3.3M | — | 2.25 | holdings check: 10-Q fair value implies ~4.88M SOL vs CoinGe |
| ALCPB.PA | BTC | 2,834 | $235.3M | $0.0M | $0.0M | $0.0M | $1.43B | 6.08 | 6.08 | 6.08 | — | $1.9M | — | — |  |
| BTBT | ETH | 158,462 | $392.6M | $83.6M | $414.6M | $9.1M | $457.7M | 1.17 | 2.03 | 8.72 | — | $41.0M | — | 0.01 | non-pure: owns a WhiteFiber stake not in the look-through NA |
| DJT | BTC | 9,542 | $785.7M | $215.5M | $989.0M | $0.0M | $2.25B | 2.87 | 3.85 | 185.79 | 35.71 | $36.0M | — | 1.06 | non-pure: operating company (Truth Social) |

### B2. True-mNAV buckets, forward hedged excess (beta hedge, 40 trading days; all eligible names; split 2026-04-01)

| period | true mNAV | weeks | signals | names | mean per trade | NW t |
|---|---|---:|---:|---:|---:|---:|
| in_sample | -inf..0.5 | 8 | 9 | 2 | -6.9% | -4.22 |
| in_sample | 0.5..0.7 | 21 | 47 | 5 | -1.1% | -0.83 |
| in_sample | 0.7..0.9 | 19 | 38 | 7 | +0.6% | 0.49 |
| in_sample | 0.9..1.1 | 17 | 32 | 5 | +8.1% | 2.81 |
| in_sample | 1.1..1.5 | 20 | 29 | 3 | -2.7% | -0.67 |
| in_sample | 1.5..inf | 21 | 30 | 3 | +0.3% | 0.14 |
| test | -inf..0.5 | 19 | 93 | 8 | +1.0% | 0.30 |
| test | 0.5..0.7 | 19 | 83 | 9 | -1.7% | -0.71 |
| test | 0.7..0.9 | 18 | 60 | 10 | +2.7% | 0.84 |
| test | 0.9..1.1 | 19 | 40 | 7 | -0.9% | -0.41 |
| test | 1.1..1.5 | 14 | 26 | 5 | -16.3% | -6.25 |
| test | 1.5..inf | 20 | 95 | 7 | -2.0% | -0.52 |

### B2. True-mNAV buckets, forward hedged excess (beta hedge, 40 trading days; excluding names with stale or unresolved holdings; split 2026-04-01)

| period | true mNAV | weeks | signals | names | mean per trade | NW t |
|---|---|---:|---:|---:|---:|---:|
| in_sample | -inf..0.5 | 8 | 8 | 1 | -8.3% | -8.51 |
| in_sample | 0.5..0.7 | 11 | 14 | 3 | -11.0% | -3.58 |
| in_sample | 0.7..0.9 | 18 | 34 | 5 | -0.2% | -0.22 |
| in_sample | 0.9..1.1 | 16 | 24 | 3 | +3.5% | 2.77 |
| in_sample | 1.1..1.5 | 19 | 26 | 2 | -3.6% | -0.82 |
| in_sample | 1.5..inf | 21 | 22 | 2 | -1.2% | -0.36 |
| test | -inf..0.5 | 19 | 70 | 5 | +0.7% | 0.20 |
| test | 0.5..0.7 | 17 | 30 | 5 | +3.3% | 1.65 |
| test | 0.7..0.9 | 18 | 53 | 8 | +4.2% | 0.83 |
| test | 0.9..1.1 | 19 | 35 | 5 | -0.7% | -0.31 |
| test | 1.1..1.5 | 14 | 25 | 4 | -14.8% | -3.75 |
| test | 1.5..inf | 20 | 63 | 5 | -1.2% | -0.28 |

### B3. DAT rules: buy every week all names below x, hold k days (18 variants per line; chosen in sample by NW t)

| universe | signal / hedge | chosen | in-sample per trade (t) | test per trade (t) | test rank | late 1d kept |
|---|---|---|---|---|---:|---:|
| all eligible | naive|asset | naive<0.7|65d | +10.7% (5.14) | -12.7% (-4.58) | 13 | — |
| all eligible | naive|beta | naive<0.9|65d | +2.8% (3.44) | -1.4% (-0.66) | 10 | 32% |
| all eligible | true|asset | true<0.7|65d | +6.5% (2.16) | -11.1% (-2.50) | 14 | — |
| all eligible | true|beta | true<0.6|40d | +1.2% (0.35) | +0.2% (0.09) | 11 | 554% |
| robust | naive|asset | naive<0.9|65d | +3.4% (2.86) | -7.5% (-4.67) | 14 | — |
| robust | naive|beta | naive<0.6|20d | +0.0% (0.00) | +0.9% (0.23) | 11 | 70% |
| robust | true|asset | true<1.0|65d | +0.3% (0.20) | -4.3% (-4.22) | 16 | — |
| robust | true|beta | true<0.5|20d | -3.5% (-1.07) | +1.7% (0.49) | 13 | 109% |

### B4. Events (hedged excess on capital; day 0 = first close on or after the announcement; dollar hedge where no NAV series)

| DAT | date | type | EDGAR filing | true mNAV before | day-0 reaction | +5d | +20d | +60d | 20d, 1 day late | 20d, 1 week late | first-hour share of day-0 move |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BMNR | 2025-07-25 | buyback_auth | 8-K 2025-07-24 | — | -1.8% | -13.5% | +5.7% | +23.0% | +17.7% | +19.1% | 65% |
| FRMM | 2025-08-11 | buyback_auth | 8-K 2025-08-11 | — | +4.3% | +132.6% | +57.6% | +47.5% | -92.7% | -75.3% | — |
| SBET | 2025-08-22 | buyback_auth | 8-K 2025-08-22 | — | +0.8% | -3.9% | -5.2% | -17.0% | -5.5% | -1.4% | 61% |
| TONX | 2025-09-04 | buyback_auth | 8-K 2025-09-05 | — | -5.1% | -23.8% | -24.3% | -33.9% | -23.1% | -0.8% | 203% |
| SBET | 2025-09-09 | buyback_exec | 8-K 2025-09-09 | — | +4.7% | -2.1% | +1.7% | -10.9% | +4.9% | +3.7% | 59% |
| FGNX | 2025-09-09 | buyback_auth | 8-K 2025-09-09 | — | — | — | — | — | — | — | — |
| TONX | 2025-09-12 | buyback_exec | 8-K 2025-09-12 | — | -8.1% | -2.2% | -5.7% | -13.1% | -5.6% | -3.7% | 24% |
| BNC | 2025-09-22 | buyback_auth | 8-K 2025-09-22 | — | -15.1% | -2.3% | -9.6% | -2.0% | -9.0% | -7.6% | 77% |
| ASST | 2025-09-22 | merger | 425 2025-09-22 | 5.24 | -1.8% | -42.4% | -106.1% | -71.9% | -92.6% | -63.9% | 198% |
| FRMM | 2025-10-27 | coin_sale_buyback | 8-K 2025-10-27 | — | +5.6% | -1.6% | -24.1% | -69.6% | -31.0% | -22.8% | — |
| 3350.T | 2025-10-28 | buyback_auth | — | 0.99 | +3.0% | -1.7% | -2.8% | +19.5% | +0.0% | -1.3% | 345% |
| FWDI | 2025-11-03 | buyback_auth | 8-K 2025-11-04 | — | +7.1% | -17.2% | -24.6% | -29.3% | -10.6% | -7.6% | — |
| SQNS | 2025-11-04 | coin_sale_debt | 6-K 2025-11-04 | — | -8.8% | +3.6% | +11.8% | -6.7% | +10.5% | +7.7% | 50% |
| UPXI | 2025-11-13 | buyback_auth | 8-K 2025-11-14 | — | +1.6% | -13.9% | -19.6% | -53.6% | -15.8% | -5.9% | 50% |
| FGNX | 2025-11-20 | coin_sale_buyback | 8-K 2025-11-21 | — | — | — | — | — | — | — | — |
| PURR | 2025-12-08 | buyback_auth | 8-K 2025-12-08 | — | +3.6% | -4.0% | +8.9% | +8.2% | +1.9% | +12.4% | 150% |
| FRMM | 2025-12-19 | coin_sale_debt | 8-K 2025-12-19 | — | +0.4% | -19.5% | -22.9% | -41.3% | -16.8% | -3.7% | — |
| ASST | 2026-01-16 | merger_close | 8-K 2026-01-16 | 1.34 | -2.1% | -6.6% | -24.4% | +4.8% | -24.3% | -17.9% | 46% |
| FGNX | 2026-01-21 | buyback_exec | 8-K 2026-01-21 | — | — | — | — | — | — | — | — |
| EMPD | 2026-01-08 | activist | — | 0.52 | +1.3% | -4.0% | +5.4% | +17.7% | +4.7% | +8.9% | -9% |
| FWDI | 2026-03-19 | buyback_exec | 8-K 2026-03-19 | 0.65 | -0.3% | -4.4% | -1.7% | +11.3% | +2.7% | +2.2% | 287% |
| BMNR | 2026-04-09 | buyback_auth | 8-K 2026-04-09 | 0.96 | -1.9% | +0.2% | +0.7% | -10.8% | +1.1% | +0.3% | 224% |
| UPXI | 2026-05-06 | buyback_exec | 8-K 2026-05-07 | — | — | — | — | — | — | — | -100% |
| BNC | 2026-06-24 | activist_settle | 8-K 2026-06-24 | 0.32 | +15.0% | +2.8% | +3.3% | +49.4% | -6.4% | -0.1% | 114% |
| TONX | 2026-07-01 | buyback_exec | 8-K 2026-07-01 | 0.37 | +14.2% | +7.1% | +10.2% | +24.3% | +13.2% | +2.5% | 189% |
| EMPD | 2026-08-28 | activist | DFAN14A 2026-09-01 | 0.44 | -1.4% | +4.9% | -5.9% | — | -10.2% | -11.3% | 32% |
| SQNS | 2026-09-24 | coin_sale_exit | 6-K 2026-09-24 | — | -4.5% | -4.7% | — | — | — | — | 58% |

| group | n | day-0 | +20d (n, t) | +60d (n, t) | 20d 1 day late | 20d 1 week late |
|---|---:|---:|---|---|---:|---:|
| activist|all | 3 | +5.0% | +0.9% (3, 0.33) | +33.6% (2, 3.00) | -4.0% | -0.8% |
| activist|late | 3 | +5.0% | +0.9% (3, 0.33) | +33.6% (2, 3.00) | -4.0% | -0.8% |
| all_supportive|all | 21 | +0.7% | -2.0% (17, -0.44) | -5.5% (16, -0.74) | -9.2% | -5.2% |
| all_supportive|early | 14 | +0.0% | -3.5% (12, -0.56) | -10.9% (12, -1.19) | -14.1% | -7.6% |
| all_supportive|late | 7 | +2.4% | +1.7% (5, 0.70) | +10.6% (4, 1.61) | +2.3% | +0.5% |
| buyback_auth|all | 11 | -0.3% | -1.3% (10, -0.19) | -4.8% (10, -0.53) | -13.6% | -6.8% |
| buyback_auth|early | 10 | -0.2% | -1.6% (9, -0.20) | -4.2% (9, -0.41) | -15.2% | -7.6% |
| buyback_auth|late | 1 | -1.9% | +0.7% (1, —) | -10.8% (1, —) | +1.1% | +0.3% |
| buyback_exec|all | 6 | +2.6% | +1.1% (4, 0.39) | +2.9% (4, 0.37) | +3.8% | +1.2% |
| buyback_exec|early | 2 | -1.7% | -2.0% (2, -0.76) | -12.0% (2, -15.03) | -0.3% | -0.0% |
| buyback_exec|late | 4 | +6.9% | +4.2% (2, 1.01) | +17.8% (2, 3.89) | +7.9% | +2.3% |
| coin_sale|all | 5 | -1.9% | -11.7% (3, -1.22) | -39.2% (3, -2.64) | -12.4% | -6.2% |
| coin_sale|early | 4 | -1.0% | -11.7% (3, -1.22) | -39.2% (3, -2.64) | -12.4% | -6.2% |
| coin_sale|late | 1 | -4.5% | — | — | — | — |
| merger|all | 2 | -2.0% | -65.2% (2, -2.26) | -33.5% (2, -1.24) | -58.5% | -40.9% |
| merger|early | 1 | -1.8% | -106.1% (1, —) | -71.9% (1, —) | -92.6% | -63.9% |
| merger|late | 1 | -2.1% | -24.4% (1, —) | +4.8% (1, —) | -24.3% | -17.9% |

Holding window chosen on events before 2026-01-01: 5 days (in-sample means 5: +3.9%, 20: -3.5%, 60: -10.9%); test mean +0.8% over 5 events.
First trading hour carries a median 65% of the event day's move (20 events with hourly bars).

### B5. Independent-path check: Strategy (MSTR)

- BTC: StrategyTracker 848,000; CoinGecko 847,999; 10-Q units 846,000 at 2026-06-30; 10-Q fair value / BTC price 844,504.
- Preferred: StrategyTracker per-series sum $14.15B; Strategy KPI $13.95B; XBRL temporary equity $14.44B at 2026-06-30.
- Debt: KPI $6.71B; XBRL LongTermDebt $6.71B. Shares: KPI market cap / price 422,068,161; StrategyTracker 421,977,908.
