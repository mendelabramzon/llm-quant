# HIP-3 oracles against outside references

21 TradingView snapshots, 22 Hyperliquid snapshots, reference delay removed per quote (futures and indices 10 min, US equities 15 min, FX and spot metals live). US equities were **weekend** at the last snapshot.

| market | reference | verdict | n | oracle vs ref (median bp) | sd | mark vs ref | mark vs oracle | funding APR | book between |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `xyz:NATGAS` | NYMEX:NG1! | live | 15 | 643.8 | 0.2 | 642.2 | -1.5 | 4% | yes |
| `para:OTHERS` | CRYPTOCAP:OTHERS x1e-9 | live | 21 | -626.4 | 0.9 | -626.6 | 0.0 | -1% | yes |
| `xyz:BRENTOIL` | ICEEUR:BRN1! | live | 15 | -235.9 | 0.5 | -231.1 | 4.9 | 19% | yes |
| `xyz:CL` | NYMEX:CL1! | live | 15 | -83.4 | 0.9 | -78.2 | 6.0 | 19% | yes |
| `xyz:COPPER` | COMEX:HG1! | live | 15 | 41.8 | 0.1 | 43.5 | 1.6 | 5% | no |
| `xyz:PLATINUM` | NYMEX:PL1! | live | 15 | -35.4 | 0.0 | -35.4 | 0.0 | 5% | yes |
| `xyz:PALLADIUM` | NYMEX:PA1! | live | 15 | 21.7 | 0.4 | 26.1 | 4.3 | 5% | no |
| `xyz:SILVER` | TVC:SILVER | live | 21 | -18.7 | 0.1 | -19.2 | -0.5 | 5% | yes |
| `xyz:GOLD` | TVC:GOLD | live | 21 | -7.7 | 0.1 | -7.7 | 0.0 | 5% | yes |
| `para:10Y` | TVC:US10Y | live | 21 | 7.6 | 0.0 | 17.2 | 9.5 | 1% | no |
| `xyz:EUR` | FX_IDC:EURUSD | live | 21 | 5.4 | 0.0 | 5.4 | 0.0 | 0% | yes |
| `xyz:GBP` | FX_IDC:GBPUSD | live | 21 | 3.0 | 0.0 | -7.6 | -10.6 | -6% | yes |
| `xyz:JPY` | FX_IDC:USDJPY | live | 21 | 1.5 | 0.0 | 1.5 | 0.0 | 0% | no |
| `para:TOTAL2` | CRYPTOCAP:TOTAL2 x1e-9 | live | 21 | -0.3 | 0.6 | 1.7 | 1.7 | 7% | no |
| `para:BTCD` | CRYPTOCAP:BTC.D | live | 21 | 0.2 | 0.3 | -4.6 | -4.7 | -11% | no |
| `xyz:SKHX` | KRX:000660 | stale reference: exchange closed | 5 | -208.5 | 0.0 | -207.7 | 0.8 | 5% | yes |
| `xyz:BOT` | NASDAQ:BOT | stale reference: exchange closed | 10 | 187.1 | 0.0 | 200.8 | 13.5 | 65% | no |
| `xyz:CRCL` | NYSE:CRCL | stale reference: exchange closed | 10 | 176.1 | 0.1 | 175.2 | -0.9 | 5% | yes |
| `xyz:AAOI` | NASDAQ:AAOI | stale reference: exchange closed | 10 | 145.0 | 0.4 | 139.5 | -4.9 | -12% | yes |
| `para:AAOI` | NASDAQ:AAOI | stale reference: exchange closed | 10 | 141.1 | 0.0 | 159.9 | 18.5 | 95% | no |
| `xyz:BB` | NYSE:BB | stale reference: exchange closed | 10 | -140.3 | 0.0 | -141.6 | -1.4 | 1% | no |
| `xyz:KORU` | AMEX:KORU | stale reference: exchange closed | 10 | 121.0 | 0.0 | 119.9 | -1.1 | 5% | yes |
| `xyz:SMSN` | KRX:005930 | stale reference: exchange closed | 5 | -117.6 | 0.0 | -116.6 | 1.0 | 5% | yes |
| `xyz:SKHY` | NASDAQ:SKHY | stale reference: exchange closed | 10 | 110.0 | 0.0 | 110.0 | 0.0 | 5% | no |
| `xyz:MRNA` | NASDAQ:MRNA | stale reference: exchange closed | 10 | -106.2 | 0.6 | -101.3 | 5.2 | 21% | yes |
| `io:SNDK` | NASDAQ:SNDK | stale reference: exchange closed | 10 | 102.6 | 0.3 | 108.3 | 5.6 | 6% | no |
| `xyz:HYUNDAI` | KRX:005380 | stale reference: exchange closed | 5 | -102.4 | 0.0 | -102.4 | 0.0 | 5% | yes |
| `xyz:SNDK` | NASDAQ:SNDK | stale reference: exchange closed | 10 | 101.0 | 0.3 | 103.9 | 2.8 | 5% | no |
| `xyz:QNT` | NASDAQ:QNT | stale reference: exchange closed | 10 | 99.8 | 0.0 | 88.1 | -11.5 | -56% | yes |
| `xyz:LITE` | NASDAQ:LITE | stale reference: exchange closed | 10 | -91.6 | 0.5 | -88.0 | 3.7 | 5% | yes |
| `xyz:COIN` | NASDAQ:COIN | stale reference: exchange closed | 10 | 87.0 | 0.2 | 87.8 | 0.8 | 5% | no |
| `xyz:NBIS` | NASDAQ:NBIS | stale reference: exchange closed | 10 | 86.6 | 0.4 | 78.7 | -7.8 | -29% | yes |
| `xyz:CRWV` | NASDAQ:CRWV | stale reference: exchange closed | 10 | 86.0 | 0.3 | 81.9 | -3.9 | 1% | yes |
| `xyz:BMNR` | NYSE:BMNR | stale reference: exchange closed | 10 | 85.3 | 0.0 | 84.5 | -0.8 | 5% | yes |
| `io:NBIS` | NASDAQ:NBIS | stale reference: exchange closed | 10 | 84.1 | 0.8 | 87.8 | 3.8 | 1% | no |
| `xyz:MSTR` | NASDAQ:MSTR | stale reference: exchange closed | 10 | 82.3 | 0.6 | 76.5 | -5.8 | -7% | yes |
| `xyz:KR200` | KRX:KOSPI200 | stale reference: exchange closed | 21 | -78.7 | 0.0 | -78.7 | 0.0 | 33% | yes |
| `xyz:BIRD` | NASDAQ:BIRD | stale reference: exchange closed | 10 | 74.7 | 0.0 | 106.8 | 31.8 | 33% | no |
| `xyz:MU` | NASDAQ:MU | stale reference: exchange closed | 10 | 70.9 | 0.0 | 70.9 | 0.0 | 5% | yes |
| `xyz:CBRS` | NASDAQ:CBRS | stale reference: exchange closed | 10 | 67.6 | 0.0 | 67.6 | 0.0 | 5% | yes |
| `xyz:BABA` | NYSE:BABA | stale reference: exchange closed | 10 | -67.3 | 0.0 | -63.8 | 3.6 | 5% | yes |
| `xyz:RIVN` | NASDAQ:RIVN | stale reference: exchange closed | 10 | 67.3 | 0.7 | 74.9 | 7.1 | 40% | no |
| `xyz:SPCX` | NASDAQ:SPCX | stale reference: exchange closed | 10 | 64.6 | 0.0 | 65.2 | 0.6 | 5% | no |
| `xyz:AVGO` | NASDAQ:AVGO | stale reference: exchange closed | 10 | 62.0 | 0.1 | 60.9 | -1.1 | 5% | yes |
| `xyz:MRVL` | NASDAQ:MRVL | stale reference: exchange closed | 10 | 58.5 | 0.5 | 53.4 | -5.1 | -13% | yes |
| `xyz:DELL` | NYSE:DELL | stale reference: exchange closed | 10 | -56.0 | 0.0 | -56.5 | -0.5 | 5% | no |
| `xyz:KSTR` | AMEX:KSTR | stale reference: exchange closed | 10 | 53.6 | 0.0 | 53.6 | 0.0 | 110% | yes |
| `io:EWY` | AMEX:EWY | stale reference: exchange closed | 10 | 50.8 | 0.0 | 53.6 | 2.8 | 3% | no |
| `xyz:AMAT` | NASDAQ:AMAT | stale reference: exchange closed | 10 | 50.0 | 0.4 | 42.6 | -7.1 | -28% | yes |
| `xyz:EWY` | AMEX:EWY | stale reference: exchange closed | 10 | 48.5 | 0.0 | 49.1 | 0.6 | 5% | no |
| `xyz:QCOM` | NASDAQ:QCOM | stale reference: exchange closed | 10 | 47.9 | 0.0 | 48.1 | 0.3 | 5% | no |
| `xyz:HOOD` | NASDAQ:HOOD | stale reference: exchange closed | 10 | 47.7 | 0.0 | 49.1 | 1.4 | 5% | no |
| `para:MELI` | NASDAQ:MELI | stale reference: exchange closed | 10 | 47.5 | 0.0 | 42.0 | -5.5 | -18% | yes |
| `para:TER` | NASDAQ:TER | stale reference: exchange closed | 10 | 46.9 | 0.0 | 32.2 | -14.7 | -78% | yes |
| `xyz:IREN` | NASDAQ:IREN | stale reference: exchange closed | 10 | 46.3 | 0.0 | 42.6 | -3.7 | 5% | yes |
| `xyz:NVDA` | NASDAQ:NVDA | stale reference: exchange closed | 10 | 45.8 | 0.3 | 48.8 | 2.8 | 5% | no |
| `para:COHR` | NYSE:COHR | stale reference: exchange closed | 10 | -42.7 | 0.0 | -42.7 | 0.0 | -23% | yes |
| `xyz:SOFTBANK` | TSE:9984 | stale reference: exchange closed | 5 | -41.9 | 0.0 | -41.9 | 0.0 | 5% | yes |
| `xyz:SOXL` | AMEX:SOXL | stale reference: exchange closed | 10 | 41.1 | 0.8 | 32.2 | -10.0 | -37% | yes |
| `para:IREN` | NASDAQ:IREN | stale reference: exchange closed | 10 | 40.7 | 0.0 | 40.7 | 0.0 | 45% | yes |
| `xyz:EBAY` | NASDAQ:EBAY | stale reference: exchange closed | 10 | 40.1 | 0.0 | 48.1 | 8.0 | 34% | no |
| `xyz:SHAZ` | NASDAQ:SHAZ | stale reference: exchange closed | 10 | 39.3 | 0.0 | 42.7 | 3.4 | 56% | no |
| `xyz:ZM` | NASDAQ:ZM | stale reference: exchange closed | 10 | -36.9 | 0.0 | -35.1 | 1.8 | -15% | yes |
| `xyz:HIMS` | NYSE:HIMS | stale reference: exchange closed | 10 | -35.4 | 0.7 | -20.7 | 14.8 | 70% | yes |
| `para:TTWO` | NASDAQ:TTWO | stale reference: exchange closed | 10 | -35.0 | 0.0 | -35.0 | 0.0 | -36% | yes |
| `xyz:EWZ` | AMEX:EWZ | stale reference: exchange closed | 10 | -33.5 | 0.0 | -36.4 | -2.9 | -40% | no |
| `xyz:GLW` | NYSE:GLW | stale reference: exchange closed | 10 | -32.6 | 0.0 | -34.8 | -2.2 | -16% | no |
| `xyz:BX` | NYSE:BX | stale reference: exchange closed | 10 | 32.4 | 0.0 | 34.1 | 1.7 | 5% | no |
| `xyz:ARM` | NASDAQ:ARM | stale reference: exchange closed | 10 | 31.9 | 0.3 | 29.3 | -2.6 | -4% | yes |
| `xyz:TWST` | NASDAQ:TWST | stale reference: exchange closed | 10 | 31.3 | 0.0 | 31.3 | 0.0 | 188% | yes |
| `xyz:USAR` | NASDAQ:USAR | stale reference: exchange closed | 10 | 31.1 | 0.0 | 31.8 | 0.8 | 5% | no |
| `xyz:INTC` | NASDAQ:INTC | stale reference: exchange closed | 10 | 31.0 | 0.5 | 29.6 | -1.4 | 2% | yes |
| `xyz:STRC` | NASDAQ:STRC | stale reference: exchange closed | 10 | -30.3 | 0.0 | -30.3 | 0.0 | 5% | yes |
| `xyz:ASML` | NASDAQ:ASML | stale reference: exchange closed | 10 | 29.5 | 0.0 | 30.1 | 0.6 | 5% | no |
| `para:GLW` | NYSE:GLW | stale reference: exchange closed | 10 | -28.3 | 0.2 | -30.6 | -2.2 | -176% | no |
| `para:SOFI` | NASDAQ:SOFI | stale reference: exchange closed | 10 | -28.3 | 0.0 | -29.6 | -1.3 | -35% | no |
| `xyz:RKLB` | NASDAQ:RKLB | stale reference: exchange closed | 10 | 27.4 | 0.1 | 25.3 | -2.2 | -0% | yes |
| `xyz:NCLD` | NASDAQ:NCLD | stale reference: exchange closed | 10 | 27.2 | 0.0 | 56.4 | 29.2 | 341% | no |
| `xyz:EWJ` | AMEX:EWJ | stale reference: exchange closed | 10 | 24.6 | 0.1 | 25.0 | 0.4 | -37% | no |
| `para:SMCI` | NASDAQ:SMCI | stale reference: exchange closed | 10 | -23.9 | 0.0 | -20.5 | 3.4 | 24% | yes |
| `xyz:GME` | NYSE:GME | stale reference: exchange closed | 10 | 23.7 | 0.0 | 21.6 | -2.1 | 5% | yes |
| `para:CIEN` | NYSE:CIEN | stale reference: exchange closed | 10 | 23.1 | 0.0 | 23.1 | 0.0 | -91% | yes |
| `para:VST` | NYSE:VST | stale reference: exchange closed | 10 | -22.3 | 0.0 | -22.3 | 0.0 | -21% | yes |
| `xyz:AMD` | NASDAQ:AMD | stale reference: exchange closed | 10 | 22.0 | 0.1 | 21.8 | -0.1 | 5% | yes |
| `xyz:DKNG` | NASDAQ:DKNG | stale reference: exchange closed | 10 | -20.4 | 0.0 | -24.0 | -3.6 | -46% | no |
| `xyz:CRWD` | NASDAQ:CRWD | stale reference: exchange closed | 10 | 20.4 | 0.2 | 27.6 | 6.9 | 21% | no |
| `xyz:LLY` | NYSE:LLY | stale reference: exchange closed | 10 | -20.1 | 0.0 | -17.6 | 2.5 | 5% | yes |
| `para:AVGO` | NASDAQ:AVGO | stale reference: exchange closed | 10 | 19.9 | 0.0 | 38.2 | 18.2 | 79% | no |
| `xyz:AAPL` | NASDAQ:AAPL | stale reference: exchange closed | 10 | -19.6 | 0.2 | -20.8 | -1.0 | 5% | no |
| `para:CIFR` | NASDAQ:CIFR | stale reference: exchange closed | 10 | 18.9 | 0.0 | 15.1 | -3.7 | -17% | yes |
| `xyz:JP225` | TVC:NI225 | stale reference: exchange closed | 21 | -17.6 | 0.0 | -26.9 | -9.3 | -37% | no |
| `xyz:TLT` | NASDAQ:TLT | stale reference: exchange closed | 10 | -17.6 | 0.0 | -9.9 | 7.7 | 140% | yes |
| `xyz:GOOGL` | NASDAQ:GOOGL | stale reference: exchange closed | 10 | -16.5 | 0.1 | -16.9 | -0.4 | 5% | no |
| `xyz:NOK` | NYSE:NOK | stale reference: exchange closed | 10 | -16.4 | 0.0 | -6.8 | 9.7 | 5% | yes |
| `xyz:COST` | NASDAQ:COST | stale reference: exchange closed | 10 | -16.2 | 0.0 | -16.2 | 0.0 | -12% | yes |
| `para:LRCX` | NASDAQ:LRCX | stale reference: exchange closed | 10 | 16.1 | 0.0 | 16.1 | 0.0 | -41% | yes |
| `para:CRWD` | NASDAQ:CRWD | stale reference: exchange closed | 10 | 15.7 | 0.0 | 15.7 | 0.0 | 115% | yes |
| `xyz:UMC` | NYSE:UMC | stale reference: exchange closed | 10 | -15.2 | 0.0 | -15.2 | 0.0 | -85% | yes |
| `xyz:KIOXIA` | TSE:285A | stale reference: exchange closed | 5 | -14.4 | 0.0 | -8.9 | 5.4 | 1% | yes |
| `xyz:SMH` | NASDAQ:SMH | stale reference: exchange closed | 10 | 13.8 | 0.1 | 14.6 | 0.8 | 5% | no |
| `xyz:IBM` | NYSE:IBM | stale reference: exchange closed | 10 | -13.2 | 0.0 | -11.4 | 1.8 | 5% | yes |
| `para:STX` | NASDAQ:STX | stale reference: exchange closed | 10 | 13.0 | 0.0 | 36.8 | 23.7 | 58% | no |
| `para:NET` | NYSE:NET | stale reference: exchange closed | 10 | 12.5 | 0.0 | 13.2 | 0.7 | 7% | yes |
| `xyz:MSFT` | NASDAQ:MSFT | stale reference: exchange closed | 10 | -11.6 | 0.1 | -10.9 | 0.7 | 5% | yes |
| `xyz:EWT` | AMEX:EWT | stale reference: exchange closed | 10 | 10.5 | 0.0 | 11.4 | 0.9 | -15% | no |
| `xyz:URNM` | AMEX:URNM | stale reference: exchange closed | 10 | 10.4 | 0.8 | 23.0 | 12.6 | 103% | no |
| `io:IONQ` | NYSE:IONQ | stale reference: exchange closed | 10 | -10.4 | 1.8 | -6.9 | 3.6 | 11% | yes |
| `mkts:SMALL2000` | AMEX:IWM | stale reference: exchange closed | 10 | 10.4 | 0.0 | 10.4 | 0.0 | 5% | yes |
| `para:CRDO` | NASDAQ:CRDO | stale reference: exchange closed | 10 | 10.0 | 0.0 | 10.0 | 0.0 | 42% | yes |
| `xyz:NOW` | NYSE:NOW | stale reference: exchange closed | 10 | 9.9 | 0.0 | 14.9 | 5.0 | 5% | no |
| `xyz:ORCL` | NYSE:ORCL | stale reference: exchange closed | 10 | -9.9 | 0.0 | -9.9 | 0.0 | 5% | yes |
| `xyz:RDDT` | NYSE:RDDT | stale reference: exchange closed | 10 | 9.4 | 0.0 | 8.4 | -0.9 | 20% | yes |
| `xyz:XYZ100` | NASDAQ:NDX | stale reference: exchange closed | 10 | 9.3 | 0.1 | 8.7 | -1.0 | 5% | yes |
| `mkts:USBOND` | NASDAQ:TLT | stale reference: exchange closed | 10 | -9.1 | 0.0 | -9.1 | 0.0 | 27% | yes |
| `para:RDDT` | NYSE:RDDT | stale reference: exchange closed | 10 | -7.9 | 0.0 | 9.1 | 17.0 | 128% | no |
| `xyz:BE` | NYSE:BE | stale reference: exchange closed | 10 | -7.0 | 0.8 | 2.1 | 8.7 | 19% | no |
| `para:SMH` | NASDAQ:SMH | stale reference: exchange closed | 10 | 5.9 | 0.0 | 8.3 | 2.4 | 7% | no |
| `xyz:XLE` | AMEX:XLE | stale reference: exchange closed | 10 | 5.5 | 0.0 | 5.5 | 0.0 | -6% | yes |
| `xyz:AMZN` | NASDAQ:AMZN | stale reference: exchange closed | 10 | -4.6 | 0.0 | -4.2 | 0.4 | 5% | no |
| `xyz:NFLX` | NASDAQ:NFLX | stale reference: exchange closed | 10 | -4.6 | 0.0 | -6.4 | -1.9 | -7% | no |
| `mkts:USTECH` | NASDAQ:QQQ | stale reference: exchange closed | 10 | -4.4 | 0.0 | -4.4 | 0.0 | 5% | yes |
| `xyz:TSLA` | NASDAQ:TSLA | stale reference: exchange closed | 10 | -3.9 | 0.2 | -5.2 | -1.3 | 5% | no |
| `xyz:WDC` | NASDAQ:WDC | stale reference: exchange closed | 10 | -3.8 | 0.0 | -4.7 | -0.9 | 5% | no |
| `xyz:META` | NASDAQ:META | stale reference: exchange closed | 10 | 3.2 | 0.1 | 4.4 | 1.3 | 5% | no |
| `xyz:NET` | NYSE:NET | stale reference: exchange closed | 10 | -2.8 | 0.0 | -8.7 | -6.0 | -19% | no |
| `xyz:LRCX` | NASDAQ:LRCX | stale reference: exchange closed | 10 | -2.5 | 0.0 | 30.3 | 32.8 | 5% | no |
| `xyz:TSM` | NYSE:TSM | stale reference: exchange closed | 10 | -2.2 | 0.2 | -5.1 | -2.9 | -3% | no |
| `xyz:CVX` | NYSE:CVX | stale reference: exchange closed | 10 | -1.9 | 0.0 | -9.4 | -7.5 | -319% | no |
| `xyz:GEV` | NYSE:GEV | stale reference: exchange closed | 10 | 1.7 | 0.0 | 10.2 | 8.5 | 61% | no |
| `mkts:US500` | AMEX:SPY | stale reference: exchange closed | 10 | -1.7 | 0.0 | -1.7 | 0.0 | 5% | no |
| `xyz:PLTR` | NASDAQ:PLTR | stale reference: exchange closed | 10 | -1.4 | 0.0 | -1.9 | -0.5 | 5% | yes |
| `xyz:XBI` | AMEX:XBI | stale reference: exchange closed | 10 | -1.3 | 0.0 | 3.9 | 5.2 | 5% | no |
| `xyz:SP500` | SP:SPX | stale reference: exchange closed | 15 | -0.8 | 0.2 | -1.8 | -1.0 | 5% | no |
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
