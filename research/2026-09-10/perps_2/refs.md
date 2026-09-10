# HIP-3 oracles against outside references

22 TradingView snapshots, 111 Hyperliquid snapshots, reference delay removed per quote (futures and indices 10 min, US equities 15 min, FX and spot metals live). US equities were **pre-market** at the last snapshot.

| market | reference | verdict | n | oracle vs ref (median bp) | sd | mark vs ref | mark vs oracle | funding APR | book between |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `para:OTHERS` | CRYPTOCAP:OTHERS x1e-9 | live | 22 | -776.9 | 14.0 | -780.7 | -3.2 | -51% | no |
| `xyz:NATGAS` | NYMEX:NG1! | live | 20 | 198.7 | 7.5 | 265.4 | 66.8 | 347% | no |
| `xyz:BRENTOIL` | ICEEUR:BRN1! | live | 20 | -176.7 | 8.3 | -244.9 | -69.3 | -375% | no |
| `xyz:CL` | NYMEX:CL1! | live | 20 | -147.4 | 8.5 | -208.4 | -64.1 | -331% | no |
| `xyz:PALLADIUM` | NYMEX:PA1! | live | 20 | -71.9 | 6.7 | -67.9 | 4.6 | 29% | yes |
| `para:TOTAL2` | CRYPTOCAP:TOTAL2 x1e-9 | live | 22 | -11.0 | 7.9 | -9.5 | 0.0 | -25% | no |
| `xyz:PLATINUM` | NYMEX:PL1! | live | 20 | -8.5 | 6.2 | -8.5 | 0.0 | 5% | yes |
| `para:BTCD` | CRYPTOCAP:BTC.D | live | 22 | 4.8 | 4.0 | 4.2 | 1.4 | 7% | yes |
| `para:10Y` | TVC:US10Y | live | 22 | -2.0 | 3.8 | -4.1 | 0.0 | -77% | no |
| `xyz:GOLD` | TVC:GOLD | live | 22 | 1.5 | 6.6 | 9.2 | 7.1 | 23% | no |
| `xyz:SILVER` | TVC:SILVER | live | 22 | 0.8 | 10.8 | 5.1 | 4.2 | 22% | no |
| `xyz:EUR` | FX_IDC:EURUSD | live | 22 | 0.7 | 1.3 | 9.0 | 8.6 | 31% | no |
| `xyz:JPY` | FX_IDC:USDJPY | live | 22 | -0.1 | 1.7 | -6.4 | -6.5 | -17% | no |
| `xyz:COPPER` | COMEX:HG1! | live | 20 | 0.0 | 4.8 | 4.6 | 4.4 | 17% | no |
| `xyz:GBP` | FX_IDC:GBPUSD | live | 22 | 0.0 | 1.3 | 0.4 | 0.0 | 0% | yes |
| `xyz:SOXL` | AMEX:SOXL | stale reference: exchange closed | 16 | -758.3 | 90.0 | -754.7 | 3.0 | 5% | yes |
| `xyz:KORU` | AMEX:KORU | stale reference: exchange closed | 16 | -548.6 | 95.6 | -545.7 | 2.4 | 5% | yes |
| `io:NBIS` | NASDAQ:NBIS | stale reference: exchange closed | 16 | -460.8 | 46.7 | -437.1 | 9.8 | 89% | no |
| `xyz:NBIS` | NASDAQ:NBIS | stale reference: exchange closed | 16 | -456.0 | 44.5 | -455.2 | 2.6 | 5% | yes |
| `xyz:SKHY` | NASDAQ:SKHY | stale reference: exchange closed | 16 | -439.5 | 29.9 | -443.3 | -6.1 | -29% | no |
| `xyz:CRWV` | NASDAQ:CRWV | stale reference: exchange closed | 16 | -422.8 | 44.9 | -422.0 | 1.0 | 5% | yes |
| `para:AAOI` | NASDAQ:AAOI | stale reference: exchange closed | 16 | -377.6 | 38.3 | -376.0 | 0.0 | 12% | yes |
| `xyz:AAOI` | NASDAQ:AAOI | stale reference: exchange closed | 16 | -376.6 | 37.6 | -375.7 | 2.9 | 19% | yes |
| `xyz:INTC` | NASDAQ:INTC | stale reference: exchange closed | 16 | -367.6 | 26.6 | -366.6 | 2.0 | 5% | yes |
| `xyz:BE` | NYSE:BE | stale reference: exchange closed | 16 | -362.3 | 60.9 | -365.0 | -2.5 | -1% | no |
| `xyz:MRVL` | NASDAQ:MRVL | stale reference: exchange closed | 16 | -348.5 | 35.2 | -348.5 | 1.1 | 5% | yes |
| `xyz:ARM` | NASDAQ:ARM | stale reference: exchange closed | 16 | -341.6 | 42.5 | -338.9 | 1.4 | 5% | yes |
| `xyz:NCLD` | NASDAQ:NCLD | stale reference: exchange closed | 16 | -331.9 | 59.7 | -314.6 | 22.7 | 77% | yes |
| `para:COHR` | NYSE:COHR | stale reference: exchange closed | 16 | -323.3 | 36.8 | -324.2 | 0.0 | -12% | no |
| `xyz:IREN` | NASDAQ:IREN | stale reference: exchange closed | 16 | -321.8 | 53.5 | -317.4 | 4.9 | 14% | yes |
| `para:IREN` | NASDAQ:IREN | stale reference: exchange closed | 16 | -319.1 | 53.8 | -317.3 | 0.2 | 8% | yes |
| `para:LRCX` | NASDAQ:LRCX | stale reference: exchange closed | 16 | -307.8 | 22.8 | -316.8 | -7.0 | 7% | no |
| `para:TER` | NASDAQ:TER | stale reference: exchange closed | 16 | -305.3 | 36.2 | -309.5 | -3.0 | -195% | no |
| `xyz:AMAT` | NASDAQ:AMAT | stale reference: exchange closed | 16 | -296.4 | 30.9 | -294.9 | 4.8 | 20% | yes |
| `para:GLW` | NYSE:GLW | stale reference: exchange closed | 16 | -292.9 | 30.0 | -294.7 | 0.0 | 6% | yes |
| `xyz:WDC` | NASDAQ:WDC | stale reference: exchange closed | 16 | -291.1 | 36.1 | -294.7 | -5.6 | -45% | yes |
| `xyz:SHAZ` | NASDAQ:SHAZ | stale reference: exchange closed | 16 | -275.3 | 70.0 | -331.3 | -20.8 | -142% | yes |
| `para:CRDO` | NASDAQ:CRDO | stale reference: exchange closed | 16 | -271.3 | 40.5 | -262.2 | 1.5 | 37% | yes |
| `xyz:LITE` | NASDAQ:LITE | stale reference: exchange closed | 16 | -269.3 | 35.1 | -268.7 | 0.7 | 5% | yes |
| `para:CIEN` | NYSE:CIEN | stale reference: exchange closed | 16 | -268.2 | 50.4 | -268.2 | 0.0 | 7% | yes |
| `xyz:URNM` | AMEX:URNM | stale reference: exchange closed | 16 | -258.5 | 31.4 | -218.8 | 34.2 | 179% | yes |
| `xyz:CRCL` | NYSE:CRCL | stale reference: exchange closed | 16 | -251.5 | 56.9 | -240.3 | 11.0 | 34% | yes |
| `xyz:MU` | NASDAQ:MU | stale reference: exchange closed | 16 | -251.2 | 31.3 | -249.3 | 2.0 | 5% | yes |
| `para:SMCI` | NASDAQ:SMCI | stale reference: exchange closed | 16 | -246.6 | 25.2 | -246.6 | 0.0 | 7% | yes |
| `para:STX` | NASDAQ:STX | stale reference: exchange closed | 16 | -236.1 | 38.4 | -257.2 | -7.1 | -33% | no |
| `xyz:QNT` | NASDAQ:QNT | stale reference: exchange closed | 16 | -230.9 | 56.6 | -210.0 | 16.8 | 123% | yes |
| `xyz:CBRS` | NASDAQ:CBRS | stale reference: exchange closed | 16 | -226.8 | 47.2 | -230.4 | -1.6 | -46% | yes |
| `xyz:SNDK` | NASDAQ:SNDK | stale reference: exchange closed | 16 | -221.5 | 32.0 | -222.6 | 0.0 | 5% | yes |
| `io:SNDK` | NASDAQ:SNDK | stale reference: exchange closed | 16 | -219.8 | 32.8 | -209.6 | -0.9 | -9% | no |
| `xyz:KR200` | KRX:KOSPI200 | stale reference: exchange closed | 22 | -217.9 | 14.1 | -219.7 | -0.9 | -44% | no |
| `xyz:AMD` | NASDAQ:AMD | stale reference: exchange closed | 16 | -216.6 | 20.1 | -216.4 | 0.0 | 5% | no |
| `xyz:ASML` | NASDAQ:ASML | stale reference: exchange closed | 16 | -215.2 | 17.6 | -210.3 | 3.5 | 5% | yes |
| `xyz:MSTR` | NASDAQ:MSTR | stale reference: exchange closed | 16 | -214.4 | 78.4 | -204.2 | 9.2 | 31% | yes |
| `xyz:SMH` | NASDAQ:SMH | stale reference: exchange closed | 16 | -207.0 | 25.1 | -194.4 | 12.6 | 56% | yes |
| `xyz:QCOM` | NASDAQ:QCOM | stale reference: exchange closed | 16 | -205.2 | 23.8 | -199.5 | 5.2 | 25% | yes |
| `xyz:HOOD` | NASDAQ:HOOD | stale reference: exchange closed | 16 | -203.4 | 41.9 | -197.3 | 4.4 | 10% | yes |
| `xyz:NOK` | NYSE:NOK | stale reference: exchange closed | 16 | -193.8 | 22.5 | -189.1 | 4.7 | 16% | yes |
| `xyz:RKLB` | NASDAQ:RKLB | stale reference: exchange closed | 16 | -192.8 | 33.8 | -188.0 | 6.8 | 15% | yes |
| `xyz:EWT` | AMEX:EWT | stale reference: exchange closed | 16 | -184.8 | 19.5 | -184.8 | 5.5 | 11% | yes |
| `xyz:EWY` | AMEX:EWY | stale reference: exchange closed | 16 | -184.0 | 33.1 | -181.6 | 1.1 | 5% | yes |
| `xyz:BMNR` | NYSE:BMNR | stale reference: exchange closed | 16 | -180.9 | 58.1 | -173.9 | 9.8 | 27% | yes |
| `xyz:DELL` | NYSE:DELL | stale reference: exchange closed | 16 | -176.3 | 21.9 | -176.7 | 0.0 | 5% | yes |
| `xyz:TSLA` | NASDAQ:TSLA | stale reference: exchange closed | 16 | -169.5 | 27.6 | -168.2 | 0.8 | 5% | yes |
| `xyz:GEV` | NYSE:GEV | stale reference: exchange closed | 16 | -165.5 | 27.2 | -165.5 | 0.0 | -6% | yes |
| `xyz:COIN` | NASDAQ:COIN | stale reference: exchange closed | 16 | -165.1 | 46.7 | -157.4 | 5.2 | 12% | yes |
| `xyz:TSM` | NYSE:TSM | stale reference: exchange closed | 16 | -163.8 | 25.6 | -160.2 | 4.1 | 8% | yes |
| `xyz:HIMS` | NYSE:HIMS | stale reference: exchange closed | 16 | -160.4 | 23.8 | -159.5 | 0.0 | 5% | yes |
| `xyz:SOFTBANK` | TSE:9984 | stale reference: exchange closed | 13 | -158.3 | 35.7 | -152.4 | 2.5 | 46% | no |
| `xyz:BB` | NYSE:BB | stale reference: exchange closed | 16 | -158.1 | 33.1 | -166.6 | -7.2 | -19% | no |
| `para:VST` | NYSE:VST | stale reference: exchange closed | 16 | -153.5 | 30.8 | -140.0 | 12.0 | 8% | yes |
| `para:AVGO` | NASDAQ:AVGO | stale reference: exchange closed | 16 | -152.0 | 20.6 | -147.5 | 3.6 | 35% | yes |
| `xyz:AVGO` | NASDAQ:AVGO | stale reference: exchange closed | 16 | -152.0 | 19.9 | -150.5 | 2.8 | 5% | yes |
| `xyz:JP225` | TVC:NI225 | stale reference: exchange closed | 22 | -147.9 | 5.9 | -149.5 | -2.3 | -3% | no |
| `xyz:PLTR` | NASDAQ:PLTR | stale reference: exchange closed | 16 | -147.8 | 36.3 | -151.0 | -3.0 | -4% | no |
| `xyz:CRWD` | NASDAQ:CRWD | stale reference: exchange closed | 16 | -145.3 | 33.2 | -139.3 | 4.7 | -11% | yes |
| `para:CRWD` | NASDAQ:CRWD | stale reference: exchange closed | 16 | -142.2 | 31.4 | -141.5 | 0.0 | -8% | yes |
| `xyz:BOT` | NASDAQ:BOT | stale reference: exchange closed | 16 | -137.3 | 12.9 | -75.9 | 63.3 | 274% | no |
| `xyz:XLE` | AMEX:XLE | stale reference: exchange closed | 16 | 137.0 | 14.5 | 145.8 | 10.0 | 33% | yes |
| `xyz:SMSN` | KRX:005930 | stale reference: exchange closed | 13 | -134.6 | 24.4 | -152.9 | -23.3 | -301% | no |
| `para:NET` | NYSE:NET | stale reference: exchange closed | 16 | -131.1 | 41.3 | -131.1 | 0.0 | 13% | yes |
| `xyz:NET` | NYSE:NET | stale reference: exchange closed | 16 | -130.8 | 43.1 | -135.3 | 0.0 | 5% | yes |
| `para:RDDT` | NYSE:RDDT | stale reference: exchange closed | 16 | 130.5 | 0.3 | 106.3 | -23.9 | 37% | yes |
| `mkts:USTECH` | NASDAQ:QQQ | stale reference: exchange closed | 5 | -121.5 | 2.2 | -118.5 | 2.8 | 5% | yes |
| `xyz:ORCL` | NYSE:ORCL | stale reference: exchange closed | 16 | -118.8 | 36.3 | -112.6 | 5.6 | 14% | yes |
| `para:SOFI` | NASDAQ:SOFI | stale reference: exchange closed | 16 | -118.3 | 33.8 | -118.3 | 0.0 | 468% | yes |
| `xyz:KIOXIA` | TSE:285A | stale reference: exchange closed | 13 | -115.4 | 47.2 | -58.8 | 62.4 | 305% | yes |
| `xyz:BABA` | NYSE:BABA | stale reference: exchange closed | 16 | -114.7 | 19.6 | -113.8 | 2.3 | 6% | yes |
| `xyz:SPCX` | NASDAQ:SPCX | stale reference: exchange closed | 16 | -105.7 | 27.0 | -105.4 | -0.3 | 5% | no |
| `xyz:XYZ100` | NASDAQ:NDX | stale reference: exchange closed | 16 | -105.0 | 17.7 | -105.9 | -0.3 | 5% | no |
| `xyz:NVDA` | NASDAQ:NVDA | stale reference: exchange closed | 16 | -96.0 | 21.0 | -96.9 | -1.6 | 5% | no |
| `xyz:RDDT` | NYSE:RDDT | stale reference: exchange closed | 16 | 89.5 | 38.9 | 96.3 | 6.4 | 62% | no |
| `xyz:IBM` | NYSE:IBM | stale reference: exchange closed | 16 | -89.2 | 32.1 | -92.5 | -1.7 | -6% | no |
| `xyz:EWZ` | AMEX:EWZ | stale reference: exchange closed | 16 | -86.6 | 10.3 | -87.5 | 1.7 | 5% | yes |
| `mkts:USBOND` | NASDAQ:TLT | stale reference: exchange closed | 5 | -78.3 | 2.2 | -80.3 | -2.7 | 5% | no |
| `xyz:USAR` | NASDAQ:USAR | stale reference: exchange closed | 16 | -70.3 | 19.2 | -62.1 | 9.4 | 49% | yes |
| `mkts:SMALL2000` | AMEX:IWM | stale reference: exchange closed | 5 | -68.5 | 2.1 | -64.0 | 4.5 | 26% | yes |
| `xyz:BX` | NYSE:BX | stale reference: exchange closed | 16 | 63.5 | 29.3 | 54.2 | -0.8 | -54% | no |
| `xyz:AAPL` | NASDAQ:AAPL | stale reference: exchange closed | 16 | 59.0 | 15.7 | 54.2 | -3.9 | -6% | yes |
| `mkts:US500` | AMEX:SPY | stale reference: exchange closed | 5 | -54.6 | 3.3 | -54.8 | -0.3 | 5% | no |
| `xyz:HYUNDAI` | KRX:005380 | stale reference: exchange closed | 13 | -50.7 | 12.4 | -65.9 | -26.0 | -194% | no |
| `xyz:MRNA` | NASDAQ:MRNA | stale reference: exchange closed | 16 | -49.4 | 28.6 | -52.4 | -3.7 | -17% | no |
| `xyz:ZM` | NASDAQ:ZM | stale reference: exchange closed | 16 | -49.4 | 45.1 | -42.4 | 14.0 | 60% | yes |
| `xyz:RIVN` | NASDAQ:RIVN | stale reference: exchange closed | 16 | -44.7 | 39.4 | -45.6 | -0.9 | 5% | yes |
| `xyz:AMZN` | NASDAQ:AMZN | stale reference: exchange closed | 16 | -44.4 | 23.0 | -41.6 | 1.8 | 5% | yes |
| `xyz:SP500` | SP:SPX | stale reference: exchange closed | 20 | -42.2 | 9.4 | -43.8 | -1.6 | 5% | no |
| `xyz:COST` | NASDAQ:COST | stale reference: exchange closed | 16 | 41.0 | 13.2 | 41.0 | 0.0 | 5% | yes |
| `xyz:EBAY` | NASDAQ:EBAY | stale reference: exchange closed | 16 | 40.6 | 1.7 | 30.9 | -9.6 | -62% | yes |
| `xyz:MSFT` | NASDAQ:MSFT | stale reference: exchange closed | 16 | -38.5 | 14.7 | -41.0 | -2.0 | 4% | no |
| `xyz:GOOGL` | NASDAQ:GOOGL | stale reference: exchange closed | 16 | -36.3 | 15.0 | -32.5 | 3.0 | 6% | yes |
| `xyz:LLY` | NYSE:LLY | stale reference: exchange closed | 16 | 35.9 | 3.1 | 35.9 | 1.3 | 5% | no |
| `xyz:SKHX` | KRX:000660 | stale reference: exchange closed | 13 | -32.1 | 16.6 | -47.1 | -19.7 | -185% | no |
| `xyz:XBI` | AMEX:XBI | stale reference: exchange closed | 16 | -29.8 | 16.6 | -20.7 | 8.2 | 96% | yes |
| `xyz:BIRD` | NASDAQ:BIRD | stale reference: exchange closed | 16 | -28.5 | 37.7 | 7.9 | 35.1 | -128% | yes |
| `xyz:META` | NASDAQ:META | stale reference: exchange closed | 16 | -27.8 | 14.6 | -28.2 | 0.0 | 5% | yes |
| `para:TTWO` | NASDAQ:TTWO | stale reference: exchange closed | 16 | -19.9 | 13.3 | -25.2 | -3.4 | 1096% | no |
| `xyz:DKNG` | NASDAQ:DKNG | stale reference: exchange closed | 16 | -19.7 | 39.5 | -10.1 | 0.0 | 31% | yes |
| `xyz:STRC` | NASDAQ:STRC | stale reference: exchange closed | 16 | 11.2 | 2.5 | 9.2 | -1.7 | -20% | yes |
| `para:MELI` | NASDAQ:MELI | stale reference: exchange closed | 16 | -10.4 | 25.9 | -10.4 | 0.0 | 484% | yes |
| `xyz:GME` | NYSE:GME | stale reference: exchange closed | 16 | 10.1 | 17.3 | 15.8 | 2.8 | 5% | yes |
| `xyz:NFLX` | NASDAQ:NFLX | stale reference: exchange closed | 16 | 9.2 | 27.3 | 8.9 | 0.0 | 5% | yes |
| `xyz:EWJ` | AMEX:EWJ | stale reference: exchange closed | 16 | -6.7 | 14.5 | 4.2 | 11.0 | 34% | no |
| `xyz:NOW` | NYSE:NOW | stale reference: exchange closed | 16 | 3.4 | 41.2 | 3.8 | -0.4 | 5% | no |
| `io:ANTH` | - | no reference | 0 | | | | | | |
| `io:GPRO` | - | no reference | 0 | | | | | | |
| `io:OAI` | - | no reference | 0 | | | | | | |
| `para:ANSEM` | - | no reference | 0 | | | | | | |
| `para:IGV` | - | no reference | 0 | | | | | | |
| `para:UNITREE` | - | no reference | 0 | | | | | | |
| `xyz:CXMT` | - | no reference | 0 | | | | | | |
| `xyz:DRAM` | - | no reference | 0 | | | | | | |
| `xyz:GIGADEV` | - | no reference | 0 | | | | | | |
| `xyz:LYTE` | - | no reference | 0 | | | | | | |
| `xyz:MAGS` | - | no reference | 0 | | | | | | |
| `xyz:MINIMAX` | - | no reference | 0 | | | | | | |
| `xyz:PURRDAT` | - | no reference | 0 | | | | | | |
| `xyz:SHEIN` | - | no reference | 0 | | | | | | |
| `xyz:UNITREE` | - | no reference | 0 | | | | | | |
| `xyz:ZHIPU` | - | no reference | 0 | | | | | | |
