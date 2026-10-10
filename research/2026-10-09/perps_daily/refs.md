# HIP-3 oracles against outside references

21 TradingView snapshots, 22 Hyperliquid snapshots, reference delay removed per quote (futures and indices 10 min, US equities 15 min, FX and spot metals live). US equities were **after-hours** at the last snapshot.

| market | reference | verdict | n | oracle vs ref (median bp) | sd | mark vs ref | mark vs oracle | funding APR | book between |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `para:OTHERS` | CRYPTOCAP:OTHERS x1e-9 | live | 21 | -642.5 | 2.0 | -645.2 | -3.7 | -2% | no |
| `xyz:NATGAS` | NYMEX:NG1! | live | 15 | 491.0 | 8.7 | 549.4 | 55.1 | 610% | no |
| `xyz:BRENTOIL` | ICEEUR:BRN1! | live | 15 | -214.9 | 4.1 | -240.6 | -23.4 | -252% | no |
| `xyz:CL` | NYMEX:CL1! | live | 15 | -79.9 | 0.9 | -81.0 | 0.0 | -71% | yes |
| `xyz:COPPER` | COMEX:HG1! | live | 15 | 19.6 | 0.3 | 19.0 | 0.0 | -22% | no |
| `xyz:PALLADIUM` | NYMEX:PA1! | live | 15 | 18.3 | 0.0 | 15.6 | -2.6 | 5% | yes |
| `xyz:PLATINUM` | NYMEX:PL1! | live | 15 | -15.9 | 0.2 | -17.7 | -1.8 | 5% | no |
| `xyz:EUR` | FX_IDC:EURUSD | live | 21 | 5.0 | 0.0 | 5.9 | 0.9 | 0% | yes |
| `xyz:GBP` | FX_IDC:GBPUSD | live | 21 | 3.8 | 0.4 | 6.8 | 3.0 | 1% | no |
| `xyz:SILVER` | TVC:SILVER | live | 21 | -2.8 | 1.0 | -6.1 | -3.8 | -2% | no |
| `para:TOTAL2` | CRYPTOCAP:TOTAL2 x1e-9 | live | 21 | -2.5 | 1.6 | -0.7 | 0.9 | 7% | yes |
| `xyz:JPY` | FX_IDC:USDJPY | live | 21 | 2.1 | 0.0 | 0.3 | -1.9 | 0% | yes |
| `para:10Y` | TVC:US10Y | live | 21 | 1.9 | 0.9 | 6.9 | 5.0 | 1% | no |
| `xyz:GOLD` | TVC:GOLD | live | 21 | -0.8 | 0.9 | -3.9 | -3.1 | -1% | no |
| `para:BTCD` | CRYPTOCAP:BTC.D | live | 21 | 0.6 | 0.5 | 4.1 | 3.3 | 7% | no |
| `xyz:SKHX` | KRX:000660 | stale reference: exchange closed | 5 | -289.8 | 0.0 | -288.2 | 1.6 | 8% | yes |
| `xyz:SMSN` | KRX:005930 | stale reference: exchange closed | 5 | -204.0 | 0.0 | -203.0 | 1.0 | 8% | yes |
| `xyz:HYUNDAI` | KRX:005380 | stale reference: exchange closed | 5 | -133.0 | 0.0 | -137.1 | -4.2 | -15% | no |
| `xyz:KR200` | KRX:KOSPI200 | stale reference: exchange closed | 21 | -130.4 | 0.0 | -130.4 | 0.0 | 5% | yes |
| `xyz:KIOXIA` | TSE:285A | stale reference: exchange closed | 5 | -70.4 | 1.3 | -91.2 | -20.9 | -68% | no |
| `xyz:URNM` | AMEX:URNM | stale reference: exchange closed | 10 | -56.1 | 1.8 | -27.6 | 28.1 | 83% | yes |
| `xyz:TWST` | NASDAQ:TWST | stale reference: exchange closed | 10 | 54.4 | 0.0 | 54.4 | 0.0 | 174% | yes |
| `xyz:QNT` | NASDAQ:QNT | stale reference: exchange closed | 10 | 50.7 | 0.8 | 69.7 | 19.3 | 74% | no |
| `xyz:PLTR` | NASDAQ:PLTR | stale reference: exchange closed | 10 | -48.6 | 1.4 | -53.6 | -4.8 | -7% | no |
| `xyz:BOT` | NASDAQ:BOT | stale reference: exchange closed | 10 | 46.9 | 15.2 | 33.9 | -5.2 | 2% | yes |
| `xyz:SOFTBANK` | TSE:9984 | stale reference: exchange closed | 5 | -42.7 | 0.0 | -43.3 | -0.5 | 70% | no |
| `xyz:KSTR` | AMEX:KSTR | stale reference: exchange closed | 10 | 38.0 | 0.0 | 35.1 | -2.8 | 12% | yes |
| `xyz:SKHY` | NASDAQ:SKHY | stale reference: exchange closed | 10 | 37.3 | 0.6 | 39.3 | 2.4 | 5% | no |
| `xyz:IREN` | NASDAQ:IREN | stale reference: exchange closed | 10 | 36.2 | 1.9 | 41.2 | 4.4 | 21% | no |
| `xyz:USAR` | NASDAQ:USAR | stale reference: exchange closed | 10 | 35.8 | 8.6 | 40.6 | 5.2 | 12% | no |
| `para:IREN` | NASDAQ:IREN | stale reference: exchange closed | 10 | 35.5 | 1.4 | 35.5 | 0.0 | 7% | yes |
| `para:MELI` | NASDAQ:MELI | stale reference: exchange closed | 10 | 35.4 | 0.1 | 35.4 | 0.0 | 7% | yes |
| `xyz:COIN` | NASDAQ:COIN | stale reference: exchange closed | 10 | 34.8 | 1.9 | 36.2 | 0.0 | 5% | no |
| `xyz:WDC` | NASDAQ:WDC | stale reference: exchange closed | 10 | -34.7 | 6.2 | -30.2 | 6.9 | 22% | yes |
| `xyz:SHAZ` | NASDAQ:SHAZ | stale reference: exchange closed | 10 | 34.3 | 0.0 | 22.0 | -12.2 | -22% | yes |
| `para:VST` | NYSE:VST | stale reference: exchange closed | 10 | -33.1 | 10.5 | -30.7 | 0.6 | 7% | yes |
| `xyz:CRCL` | NYSE:CRCL | stale reference: exchange closed | 10 | 32.5 | 5.0 | 35.4 | 5.5 | 16% | yes |
| `xyz:HIMS` | NYSE:HIMS | stale reference: exchange closed | 10 | -32.3 | 12.9 | -19.2 | 12.5 | 18% | yes |
| `para:CRDO` | NASDAQ:CRDO | stale reference: exchange closed | 10 | -31.3 | 3.3 | -26.5 | 4.7 | 33% | no |
| `para:CIFR` | NASDAQ:CIFR | stale reference: exchange closed | 10 | 29.6 | 7.4 | 34.9 | 3.6 | 10% | no |
| `xyz:CRWV` | NASDAQ:CRWV | stale reference: exchange closed | 10 | 29.5 | 0.3 | 26.7 | -2.8 | -2% | yes |
| `xyz:BIRD` | NASDAQ:BIRD | stale reference: exchange closed | 10 | 29.0 | 0.0 | 81.2 | 52.1 | 492% | no |
| `xyz:UMC` | NYSE:UMC | stale reference: exchange closed | 10 | -28.3 | 0.0 | -43.8 | -15.5 | 248% | no |
| `xyz:BB` | NYSE:BB | stale reference: exchange closed | 10 | -28.1 | 0.0 | -29.3 | -1.2 | 5% | no |
| `xyz:NBIS` | NASDAQ:NBIS | stale reference: exchange closed | 10 | 25.6 | 2.9 | 35.5 | 10.4 | 40% | no |
| `io:NBIS` | NASDAQ:NBIS | stale reference: exchange closed | 10 | 25.3 | 2.3 | 33.7 | 8.1 | 20% | no |
| `xyz:EBAY` | NASDAQ:EBAY | stale reference: exchange closed | 10 | 25.0 | 0.7 | 45.0 | 20.0 | 94% | no |
| `xyz:BE` | NYSE:BE | stale reference: exchange closed | 10 | -23.2 | 2.8 | -17.5 | 3.2 | 9% | yes |
| `xyz:EWJ` | AMEX:EWJ | stale reference: exchange closed | 10 | 23.0 | 0.0 | 8.5 | -14.5 | -58% | yes |
| `para:COHR` | NYSE:COHR | stale reference: exchange closed | 10 | -22.7 | 1.0 | -11.0 | 11.7 | 10% | yes |
| `para:STX` | NASDAQ:STX | stale reference: exchange closed | 10 | -21.5 | 0.1 | -18.7 | 2.8 | 13% | yes |
| `xyz:LRCX` | NASDAQ:LRCX | stale reference: exchange closed | 10 | 21.3 | 0.0 | 26.7 | 5.3 | -45% | no |
| `para:LRCX` | NASDAQ:LRCX | stale reference: exchange closed | 10 | 21.3 | 0.0 | 25.4 | 4.1 | 7% | yes |
| `xyz:MSTR` | NASDAQ:MSTR | stale reference: exchange closed | 10 | 20.1 | 4.2 | 20.7 | 0.3 | 5% | yes |
| `xyz:INTC` | NASDAQ:INTC | stale reference: exchange closed | 10 | -20.1 | 1.5 | -18.1 | 1.0 | 5% | yes |
| `para:SOFI` | NASDAQ:SOFI | stale reference: exchange closed | 10 | -19.0 | 5.1 | -9.5 | 9.5 | 33% | yes |
| `xyz:AVGO` | NASDAQ:AVGO | stale reference: exchange closed | 10 | 18.7 | 0.7 | 22.0 | 2.2 | 12% | no |
| `para:AVGO` | NASDAQ:AVGO | stale reference: exchange closed | 10 | 18.5 | 0.9 | 18.5 | 0.0 | -22% | yes |
| `xyz:LLY` | NYSE:LLY | stale reference: exchange closed | 10 | -17.6 | 0.0 | -18.4 | -0.8 | 5% | no |
| `xyz:EWZ` | AMEX:EWZ | stale reference: exchange closed | 10 | -17.2 | 0.5 | -10.2 | 6.9 | 5% | yes |
| `xyz:XLE` | AMEX:XLE | stale reference: exchange closed | 10 | 15.4 | 1.8 | 8.1 | -5.2 | -15% | yes |
| `xyz:BABA` | NYSE:BABA | stale reference: exchange closed | 10 | -15.3 | 0.0 | -15.3 | 0.0 | 5% | no |
| `xyz:GEV` | NYSE:GEV | stale reference: exchange closed | 10 | -15.2 | 0.0 | -14.7 | 0.5 | 5% | yes |
| `xyz:RIVN` | NASDAQ:RIVN | stale reference: exchange closed | 10 | 14.3 | 0.0 | 11.8 | -2.5 | -4% | yes |
| `xyz:CBRS` | NASDAQ:CBRS | stale reference: exchange closed | 10 | 14.0 | 3.2 | 17.7 | 4.0 | 20% | no |
| `xyz:KORU` | AMEX:KORU | stale reference: exchange closed | 10 | 14.0 | 4.0 | 23.5 | 7.8 | 5% | no |
| `xyz:LITE` | NASDAQ:LITE | stale reference: exchange closed | 10 | 14.0 | 1.7 | 12.6 | -1.8 | 5% | yes |
| `xyz:TSM` | NYSE:TSM | stale reference: exchange closed | 10 | -13.8 | 4.8 | -9.7 | 2.3 | 5% | yes |
| `xyz:MRVL` | NASDAQ:MRVL | stale reference: exchange closed | 10 | -13.1 | 0.9 | -9.8 | 3.3 | 5% | yes |
| `xyz:RDDT` | NYSE:RDDT | stale reference: exchange closed | 10 | -12.5 | 0.0 | -25.0 | -12.5 | -74% | no |
| `para:NET` | NYSE:NET | stale reference: exchange closed | 10 | 12.5 | 0.0 | 12.5 | 0.0 | -35% | yes |
| `xyz:NET` | NYSE:NET | stale reference: exchange closed | 10 | 12.5 | 0.0 | 8.3 | -4.2 | 0% | yes |
| `xyz:BX` | NYSE:BX | stale reference: exchange closed | 10 | 12.2 | 0.0 | 13.1 | 0.9 | 5% | no |
| `para:TTWO` | NASDAQ:TTWO | stale reference: exchange closed | 10 | 12.2 | 0.1 | 12.2 | 0.0 | 30% | yes |
| `xyz:AAPL` | NASDAQ:AAPL | stale reference: exchange closed | 10 | -11.3 | 0.4 | -11.9 | 0.0 | 5% | yes |
| `xyz:AMD` | NASDAQ:AMD | stale reference: exchange closed | 10 | -10.6 | 0.3 | -8.6 | 1.8 | 5% | yes |
| `xyz:BMNR` | NYSE:BMNR | stale reference: exchange closed | 10 | 10.4 | 1.0 | 23.3 | 12.9 | 31% | no |
| `xyz:IBM` | NYSE:IBM | stale reference: exchange closed | 10 | -10.3 | 1.0 | -10.8 | -0.4 | 5% | no |
| `xyz:NVDA` | NASDAQ:NVDA | stale reference: exchange closed | 10 | 9.8 | 0.8 | 9.8 | 0.0 | 5% | no |
| `xyz:AMAT` | NASDAQ:AMAT | stale reference: exchange closed | 10 | 9.6 | 0.3 | -0.2 | -9.8 | -39% | no |
| `xyz:META` | NASDAQ:META | stale reference: exchange closed | 10 | -9.5 | 1.7 | -9.5 | 0.0 | 5% | yes |
| `xyz:NCLD` | NASDAQ:NCLD | stale reference: exchange closed | 10 | 9.2 | 19.6 | -6.0 | -13.8 | 78% | yes |
| `xyz:ASML` | NASDAQ:ASML | stale reference: exchange closed | 10 | 8.8 | 1.0 | 18.9 | 9.8 | 39% | no |
| `para:SMH` | NASDAQ:SMH | stale reference: exchange closed | 10 | 8.7 | 0.5 | 6.8 | -1.9 | -30% | yes |
| `xyz:MRNA` | NASDAQ:MRNA | stale reference: exchange closed | 10 | -8.7 | 1.8 | -15.6 | -9.3 | -33% | no |
| `xyz:SPCX` | NASDAQ:SPCX | stale reference: exchange closed | 10 | 8.6 | 1.2 | 8.6 | 0.0 | 5% | yes |
| `xyz:SNDK` | NASDAQ:SNDK | stale reference: exchange closed | 10 | -8.3 | 1.6 | -6.4 | 2.5 | 5% | yes |
| `xyz:DELL` | NYSE:DELL | stale reference: exchange closed | 10 | -8.2 | 3.6 | -18.1 | -10.1 | -32% | yes |
| `xyz:SOXL` | AMEX:SOXL | stale reference: exchange closed | 10 | -7.9 | 1.8 | -10.0 | -2.1 | 5% | yes |
| `xyz:MU` | NASDAQ:MU | stale reference: exchange closed | 10 | -7.8 | 1.5 | -6.3 | 1.5 | 5% | yes |
| `para:RDDT` | NYSE:RDDT | stale reference: exchange closed | 10 | -7.8 | 0.0 | -17.8 | -10.0 | -64% | no |
| `xyz:DKNG` | NASDAQ:DKNG | stale reference: exchange closed | 10 | -7.7 | 0.0 | -7.7 | 0.0 | -18% | yes |
| `io:EWY` | AMEX:EWY | stale reference: exchange closed | 10 | 7.6 | 1.9 | 12.4 | 5.1 | 4% | no |
| `xyz:ORCL` | NYSE:ORCL | stale reference: exchange closed | 10 | 7.1 | 2.2 | 2.8 | -4.2 | -19% | yes |
| `xyz:EWT` | AMEX:EWT | stale reference: exchange closed | 10 | 7.0 | 3.5 | 8.3 | 1.3 | 5% | no |
| `xyz:ZM` | NASDAQ:ZM | stale reference: exchange closed | 10 | -6.9 | 4.2 | -19.5 | -10.2 | -29% | no |
| `para:SMCI` | NASDAQ:SMCI | stale reference: exchange closed | 10 | -6.8 | 0.8 | -6.8 | 0.0 | 7% | yes |
| `xyz:XYZ100` | NASDAQ:NDX | stale reference: exchange closed | 10 | 6.8 | 0.1 | 8.0 | 1.3 | 5% | no |
| `io:SNDK` | NASDAQ:SNDK | stale reference: exchange closed | 10 | -6.1 | 2.3 | -3.3 | 3.2 | 4% | yes |
| `xyz:EWY` | AMEX:EWY | stale reference: exchange closed | 10 | 5.9 | 0.3 | 10.4 | 4.5 | 5% | no |
| `xyz:JP225` | TVC:NI225 | stale reference: exchange closed | 21 | -5.9 | 2.4 | 6.1 | 11.3 | 44% | no |
| `xyz:TLT` | NASDAQ:TLT | stale reference: exchange closed | 10 | -5.3 | 1.2 | -2.7 | 2.6 | 5% | yes |
| `xyz:HOOD` | NASDAQ:HOOD | stale reference: exchange closed | 10 | 5.0 | 1.0 | 8.7 | 3.7 | 16% | no |
| `io:IONQ` | NYSE:IONQ | stale reference: exchange closed | 10 | -4.9 | 1.3 | -4.3 | 1.0 | 3% | no |
| `xyz:NOK` | NYSE:NOK | stale reference: exchange closed | 10 | -4.8 | 2.5 | -12.5 | -5.8 | -15% | no |
| `xyz:COST` | NASDAQ:COST | stale reference: exchange closed | 10 | 4.8 | 0.0 | -6.4 | -11.2 | -31% | no |
| `xyz:TSLA` | NASDAQ:TSLA | stale reference: exchange closed | 10 | -4.4 | 0.9 | -0.9 | 3.7 | 5% | yes |
| `para:CIEN` | NYSE:CIEN | stale reference: exchange closed | 10 | 4.0 | 2.3 | 4.7 | 0.0 | 7% | no |
| `xyz:GME` | NYSE:GME | stale reference: exchange closed | 10 | 3.8 | 0.9 | 3.8 | -1.1 | 5% | yes |
| `xyz:NOW` | NYSE:NOW | stale reference: exchange closed | 10 | 3.5 | 1.2 | 11.4 | 7.8 | 23% | no |
| `mkts:US500` | AMEX:SPY | stale reference: exchange closed | 10 | -3.5 | 1.3 | -3.5 | 0.0 | -2% | yes |
| `xyz:SP500` | SP:SPX | stale reference: exchange closed | 15 | 3.4 | 0.6 | -0.7 | -4.0 | -1% | yes |
| `xyz:QCOM` | NASDAQ:QCOM | stale reference: exchange closed | 10 | 2.8 | 0.0 | 8.3 | 5.4 | 15% | no |
| `xyz:NFLX` | NASDAQ:NFLX | stale reference: exchange closed | 10 | 2.8 | 2.9 | 9.2 | 5.1 | 5% | no |
| `xyz:MSFT` | NASDAQ:MSFT | stale reference: exchange closed | 10 | -2.6 | 1.4 | -4.9 | -1.8 | 3% | no |
| `para:TER` | NASDAQ:TER | stale reference: exchange closed | 10 | 2.2 | 9.5 | 23.3 | 23.5 | 166% | no |
| `xyz:RKLB` | NASDAQ:RKLB | stale reference: exchange closed | 10 | 2.2 | 1.6 | 5.1 | 0.6 | 5% | no |
| `xyz:GOOGL` | NASDAQ:GOOGL | stale reference: exchange closed | 10 | 2.1 | 0.7 | 3.3 | 1.4 | 5% | no |
| `xyz:CVX` | NYSE:CVX | stale reference: exchange closed | 10 | 1.9 | 0.0 | 7.5 | 5.7 | 133% | no |
| `xyz:ARM` | NASDAQ:ARM | stale reference: exchange closed | 10 | 1.7 | 1.7 | 4.7 | 2.3 | 11% | no |
| `mkts:USBOND` | NASDAQ:TLT | stale reference: exchange closed | 10 | -1.3 | 0.0 | -1.3 | 0.0 | 24% | yes |
| `para:CRWD` | NASDAQ:CRWD | stale reference: exchange closed | 10 | -1.3 | 0.4 | -11.3 | -10.0 | -3% | no |
| `mkts:USTECH` | NASDAQ:QQQ | stale reference: exchange closed | 10 | 1.1 | 1.5 | 1.5 | 0.0 | 5% | no |
| `xyz:CRWD` | NASDAQ:CRWD | stale reference: exchange closed | 10 | -1.1 | 0.4 | -3.3 | -2.2 | -5% | no |
| `para:AAOI` | NASDAQ:AAOI | stale reference: exchange closed | 10 | 0.9 | 3.9 | 0.9 | 0.0 | 7% | no |
| `xyz:AAOI` | NASDAQ:AAOI | stale reference: exchange closed | 10 | 0.9 | 3.7 | 9.1 | 4.6 | 5% | no |
| `xyz:XBI` | AMEX:XBI | stale reference: exchange closed | 10 | -0.7 | 2.2 | 5.2 | 5.9 | 5% | no |
| `para:GLW` | NYSE:GLW | stale reference: exchange closed | 10 | 0.6 | 0.0 | 0.6 | 0.0 | 7% | yes |
| `xyz:GLW` | NYSE:GLW | stale reference: exchange closed | 10 | 0.6 | 0.0 | 11.5 | 10.8 | 42% | no |
| `xyz:STRC` | NASDAQ:STRC | stale reference: exchange closed | 10 | 0.5 | 0.2 | -2.6 | -3.2 | -9% | no |
| `xyz:SMH` | NASDAQ:SMH | stale reference: exchange closed | 10 | 0.4 | 0.5 | 6.3 | 5.3 | 12% | no |
| `mkts:SMALL2000` | AMEX:IWM | stale reference: exchange closed | 10 | 0.4 | 1.9 | 0.4 | 0.0 | -17% | yes |
| `io:ANTH` | - | no reference | 0 | | | | | | |
| `io:DRAM` | - | no reference | 0 | | | | | | |
| `io:GPRO` | - | no reference | 0 | | | | | | |
| `io:OAI` | - | no reference | 0 | | | | | | |
| `io:TCNT` | - | no reference | 0 | | | | | | |
| `mkts:BVIV` | - | no reference | 0 | | | | | | |
| `para:2Y` | - | no reference | 0 | | | | | | |
| `para:30Y` | - | no reference | 0 | | | | | | |
| `para:ANSEM` | - | no reference | 0 | | | | | | |
| `para:IGV` | - | no reference | 0 | | | | | | |
| `para:TREAD` | - | no reference | 0 | | | | | | |
| `para:UNITREE` | - | no reference | 0 | | | | | | |
| `xyz:AMZN` | NASDAQ:AMZN | stale reference: exchange closed | 10 | 0.0 | 0.3 | 2.7 | 2.7 | 5% | no |
| `xyz:CXMT` | - | no reference | 0 | | | | | | |
| `xyz:DRAM` | - | no reference | 0 | | | | | | |
| `xyz:GIGADEV` | - | no reference | 0 | | | | | | |
| `xyz:HO` | - | no reference | 0 | | | | | | |
| `xyz:LYTE` | - | no reference | 0 | | | | | | |
| `xyz:MAGS` | - | no reference | 0 | | | | | | |
| `xyz:MINIMAX` | - | no reference | 0 | | | | | | |
| `xyz:OURA` | - | no reference | 0 | | | | | | |
| `xyz:PURRDAT` | - | no reference | 0 | | | | | | |
| `xyz:SHEIN` | - | no reference | 0 | | | | | | |
| `xyz:SNXX` | - | no reference | 0 | | | | | | |
| `xyz:UNITREE` | - | no reference | 0 | | | | | | |
| `xyz:ZHIPU` | - | no reference | 0 | | | | | | |
