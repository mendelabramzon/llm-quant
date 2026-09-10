# HIP-3 oracles against outside references

6 TradingView snapshots, 7 Hyperliquid snapshots, reference delay removed per quote (futures and indices 10 min, US equities 15 min, FX and spot metals live). US equities were **regular** at the last snapshot.

| market | reference | verdict | n | oracle vs ref (median bp) | sd | mark vs ref | mark vs oracle | funding APR | book between |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `para:OTHERS` | CRYPTOCAP:OTHERS x1e-9 | live | 6 | -753.6 | 6.0 | -763.1 | -10.6 | -52% | no |
| `xyz:SILVER` | TVC:SILVER | live | 6 | 3.6 | 7.6 | 7.9 | 4.3 | 8% | no |
| `para:10Y` | TVC:US10Y | live | 6 | -3.0 | 3.6 | -13.2 | -10.2 | 2% | no |
| `para:TOTAL2` | CRYPTOCAP:TOTAL2 x1e-9 | live | 6 | -0.9 | 3.1 | -10.3 | -8.9 | -23% | no |
| `xyz:GBP` | FX_IDC:GBPUSD | live | 6 | 0.7 | 0.5 | -0.4 | -0.7 | 0% | no |
| `xyz:JPY` | FX_IDC:USDJPY | live | 6 | -0.7 | 0.7 | -3.6 | -3.2 | -6% | no |
| `xyz:EUR` | FX_IDC:EURUSD | live | 6 | 0.4 | 0.6 | 7.0 | 6.0 | 27% | no |
| `xyz:GOLD` | TVC:GOLD | live | 6 | 0.4 | 4.0 | 4.3 | 3.9 | 7% | no |
| `para:BTCD` | CRYPTOCAP:BTC.D | live | 6 | -0.1 | 1.8 | 0.8 | 1.5 | 7% | yes |
| `xyz:KR200` | KRX:KOSPI200 | stale reference: exchange closed | 6 | -305.1 | 9.1 | -310.5 | -4.2 | -50% | yes |
| `xyz:JP225` | TVC:NI225 | stale reference: exchange closed | 6 | -153.6 | 6.5 | -155.5 | -2.3 | -1% | no |
| `io:ANTH` | - | no reference | 0 | | | | | | |
| `io:GPRO` | - | no reference | 0 | | | | | | |
| `io:NBIS` | NASDAQ:NBIS | no aligned snapshot | 0 | | | | | | |
| `io:OAI` | - | no reference | 0 | | | | | | |
| `io:SNDK` | NASDAQ:SNDK | no aligned snapshot | 0 | | | | | | |
| `mkts:SMALL2000` | AMEX:IWM | no aligned snapshot | 0 | | | | | | |
| `mkts:US500` | AMEX:SPY | no aligned snapshot | 0 | | | | | | |
| `mkts:USBOND` | NASDAQ:TLT | no aligned snapshot | 0 | | | | | | |
| `mkts:USTECH` | NASDAQ:QQQ | no aligned snapshot | 0 | | | | | | |
| `para:AAOI` | NASDAQ:AAOI | no aligned snapshot | 0 | | | | | | |
| `para:ANSEM` | - | no reference | 0 | | | | | | |
| `para:AVGO` | NASDAQ:AVGO | no aligned snapshot | 0 | | | | | | |
| `para:CIEN` | NYSE:CIEN | no aligned snapshot | 0 | | | | | | |
| `para:COHR` | NYSE:COHR | no aligned snapshot | 0 | | | | | | |
| `para:CRDO` | NASDAQ:CRDO | no aligned snapshot | 0 | | | | | | |
| `para:CRWD` | NASDAQ:CRWD | no aligned snapshot | 0 | | | | | | |
| `para:GLW` | NYSE:GLW | no aligned snapshot | 0 | | | | | | |
| `para:IGV` | - | no reference | 0 | | | | | | |
| `para:IREN` | NASDAQ:IREN | no aligned snapshot | 0 | | | | | | |
| `para:LRCX` | NASDAQ:LRCX | no aligned snapshot | 0 | | | | | | |
| `para:MELI` | NASDAQ:MELI | no aligned snapshot | 0 | | | | | | |
| `para:NET` | NYSE:NET | no aligned snapshot | 0 | | | | | | |
| `para:RDDT` | NYSE:RDDT | no aligned snapshot | 0 | | | | | | |
| `para:SMCI` | NASDAQ:SMCI | no aligned snapshot | 0 | | | | | | |
| `para:SOFI` | NASDAQ:SOFI | no aligned snapshot | 0 | | | | | | |
| `para:STX` | NASDAQ:STX | no aligned snapshot | 0 | | | | | | |
| `para:TER` | NASDAQ:TER | no aligned snapshot | 0 | | | | | | |
| `para:TTWO` | NASDAQ:TTWO | no aligned snapshot | 0 | | | | | | |
| `para:UNITREE` | - | no reference | 0 | | | | | | |
| `para:VST` | NYSE:VST | no aligned snapshot | 0 | | | | | | |
| `xyz:AAOI` | NASDAQ:AAOI | no aligned snapshot | 0 | | | | | | |
| `xyz:AAPL` | NASDAQ:AAPL | no aligned snapshot | 0 | | | | | | |
| `xyz:AMAT` | NASDAQ:AMAT | no aligned snapshot | 0 | | | | | | |
| `xyz:AMD` | NASDAQ:AMD | no aligned snapshot | 0 | | | | | | |
| `xyz:AMZN` | NASDAQ:AMZN | no aligned snapshot | 0 | | | | | | |
| `xyz:ARM` | NASDAQ:ARM | no aligned snapshot | 0 | | | | | | |
| `xyz:ASML` | NASDAQ:ASML | no aligned snapshot | 0 | | | | | | |
| `xyz:AVGO` | NASDAQ:AVGO | no aligned snapshot | 0 | | | | | | |
| `xyz:BABA` | NYSE:BABA | no aligned snapshot | 0 | | | | | | |
| `xyz:BB` | NYSE:BB | no aligned snapshot | 0 | | | | | | |
| `xyz:BE` | NYSE:BE | no aligned snapshot | 0 | | | | | | |
| `xyz:BIRD` | NASDAQ:BIRD | no aligned snapshot | 0 | | | | | | |
| `xyz:BMNR` | NYSE:BMNR | no aligned snapshot | 0 | | | | | | |
| `xyz:BOT` | NASDAQ:BOT | no aligned snapshot | 0 | | | | | | |
| `xyz:BRENTOIL` | ICEEUR:BRN1! | no aligned snapshot | 0 | | | | | | |
| `xyz:BX` | NYSE:BX | no aligned snapshot | 0 | | | | | | |
| `xyz:CBRS` | NASDAQ:CBRS | no aligned snapshot | 0 | | | | | | |
| `xyz:CL` | NYMEX:CL1! | no aligned snapshot | 0 | | | | | | |
| `xyz:COIN` | NASDAQ:COIN | no aligned snapshot | 0 | | | | | | |
| `xyz:COPPER` | COMEX:HG1! | no aligned snapshot | 0 | | | | | | |
| `xyz:COST` | NASDAQ:COST | no aligned snapshot | 0 | | | | | | |
| `xyz:CRCL` | NYSE:CRCL | no aligned snapshot | 0 | | | | | | |
| `xyz:CRWD` | NASDAQ:CRWD | no aligned snapshot | 0 | | | | | | |
| `xyz:CRWV` | NASDAQ:CRWV | no aligned snapshot | 0 | | | | | | |
| `xyz:CXMT` | - | no reference | 0 | | | | | | |
| `xyz:DELL` | NYSE:DELL | no aligned snapshot | 0 | | | | | | |
| `xyz:DKNG` | NASDAQ:DKNG | no aligned snapshot | 0 | | | | | | |
| `xyz:DRAM` | - | no reference | 0 | | | | | | |
| `xyz:EBAY` | NASDAQ:EBAY | no aligned snapshot | 0 | | | | | | |
| `xyz:EWJ` | AMEX:EWJ | no aligned snapshot | 0 | | | | | | |
| `xyz:EWT` | AMEX:EWT | no aligned snapshot | 0 | | | | | | |
| `xyz:EWY` | AMEX:EWY | no aligned snapshot | 0 | | | | | | |
| `xyz:EWZ` | AMEX:EWZ | no aligned snapshot | 0 | | | | | | |
| `xyz:GEV` | NYSE:GEV | no aligned snapshot | 0 | | | | | | |
| `xyz:GIGADEV` | - | no reference | 0 | | | | | | |
| `xyz:GME` | NYSE:GME | no aligned snapshot | 0 | | | | | | |
| `xyz:GOOGL` | NASDAQ:GOOGL | no aligned snapshot | 0 | | | | | | |
| `xyz:HIMS` | NYSE:HIMS | no aligned snapshot | 0 | | | | | | |
| `xyz:HOOD` | NASDAQ:HOOD | no aligned snapshot | 0 | | | | | | |
| `xyz:HYUNDAI` | KRX:005380 | no aligned snapshot | 0 | | | | | | |
| `xyz:IBM` | NYSE:IBM | no aligned snapshot | 0 | | | | | | |
| `xyz:INTC` | NASDAQ:INTC | no aligned snapshot | 0 | | | | | | |
| `xyz:IREN` | NASDAQ:IREN | no aligned snapshot | 0 | | | | | | |
| `xyz:KIOXIA` | TSE:285A | no aligned snapshot | 0 | | | | | | |
| `xyz:KORU` | AMEX:KORU | no aligned snapshot | 0 | | | | | | |
| `xyz:LITE` | NASDAQ:LITE | no aligned snapshot | 0 | | | | | | |
| `xyz:LLY` | NYSE:LLY | no aligned snapshot | 0 | | | | | | |
| `xyz:LYTE` | - | no reference | 0 | | | | | | |
| `xyz:MAGS` | - | no reference | 0 | | | | | | |
| `xyz:META` | NASDAQ:META | no aligned snapshot | 0 | | | | | | |
| `xyz:MINIMAX` | - | no reference | 0 | | | | | | |
| `xyz:MRNA` | NASDAQ:MRNA | no aligned snapshot | 0 | | | | | | |
| `xyz:MRVL` | NASDAQ:MRVL | no aligned snapshot | 0 | | | | | | |
| `xyz:MSFT` | NASDAQ:MSFT | no aligned snapshot | 0 | | | | | | |
| `xyz:MSTR` | NASDAQ:MSTR | no aligned snapshot | 0 | | | | | | |
| `xyz:MU` | NASDAQ:MU | no aligned snapshot | 0 | | | | | | |
| `xyz:NATGAS` | NYMEX:NG1! | no aligned snapshot | 0 | | | | | | |
| `xyz:NBIS` | NASDAQ:NBIS | no aligned snapshot | 0 | | | | | | |
| `xyz:NCLD` | NASDAQ:NCLD | no aligned snapshot | 0 | | | | | | |
| `xyz:NET` | NYSE:NET | no aligned snapshot | 0 | | | | | | |
| `xyz:NFLX` | NASDAQ:NFLX | no aligned snapshot | 0 | | | | | | |
| `xyz:NOK` | NYSE:NOK | no aligned snapshot | 0 | | | | | | |
| `xyz:NOW` | NYSE:NOW | no aligned snapshot | 0 | | | | | | |
| `xyz:NVDA` | NASDAQ:NVDA | no aligned snapshot | 0 | | | | | | |
| `xyz:ORCL` | NYSE:ORCL | no aligned snapshot | 0 | | | | | | |
| `xyz:PALLADIUM` | NYMEX:PA1! | no aligned snapshot | 0 | | | | | | |
| `xyz:PLATINUM` | NYMEX:PL1! | no aligned snapshot | 0 | | | | | | |
| `xyz:PLTR` | NASDAQ:PLTR | no aligned snapshot | 0 | | | | | | |
| `xyz:PURRDAT` | - | no reference | 0 | | | | | | |
| `xyz:QCOM` | NASDAQ:QCOM | no aligned snapshot | 0 | | | | | | |
| `xyz:QNT` | NASDAQ:QNT | no aligned snapshot | 0 | | | | | | |
| `xyz:RDDT` | NYSE:RDDT | no aligned snapshot | 0 | | | | | | |
| `xyz:RIVN` | NASDAQ:RIVN | no aligned snapshot | 0 | | | | | | |
| `xyz:RKLB` | NASDAQ:RKLB | no aligned snapshot | 0 | | | | | | |
| `xyz:SHAZ` | NASDAQ:SHAZ | no aligned snapshot | 0 | | | | | | |
| `xyz:SHEIN` | - | no reference | 0 | | | | | | |
| `xyz:SKHX` | KRX:000660 | no aligned snapshot | 0 | | | | | | |
| `xyz:SKHY` | NASDAQ:SKHY | no aligned snapshot | 0 | | | | | | |
| `xyz:SMH` | NASDAQ:SMH | no aligned snapshot | 0 | | | | | | |
| `xyz:SMSN` | KRX:005930 | no aligned snapshot | 0 | | | | | | |
| `xyz:SNDK` | NASDAQ:SNDK | no aligned snapshot | 0 | | | | | | |
| `xyz:SOFTBANK` | TSE:9984 | no aligned snapshot | 0 | | | | | | |
| `xyz:SOXL` | AMEX:SOXL | no aligned snapshot | 0 | | | | | | |
| `xyz:SP500` | SP:SPX | no aligned snapshot | 0 | | | | | | |
| `xyz:SPCX` | NASDAQ:SPCX | no aligned snapshot | 0 | | | | | | |
| `xyz:STRC` | NASDAQ:STRC | no aligned snapshot | 0 | | | | | | |
| `xyz:TSLA` | NASDAQ:TSLA | no aligned snapshot | 0 | | | | | | |
| `xyz:TSM` | NYSE:TSM | no aligned snapshot | 0 | | | | | | |
| `xyz:UNITREE` | - | no reference | 0 | | | | | | |
| `xyz:URNM` | AMEX:URNM | no aligned snapshot | 0 | | | | | | |
| `xyz:USAR` | NASDAQ:USAR | no aligned snapshot | 0 | | | | | | |
| `xyz:WDC` | NASDAQ:WDC | no aligned snapshot | 0 | | | | | | |
| `xyz:XBI` | AMEX:XBI | no aligned snapshot | 0 | | | | | | |
| `xyz:XLE` | AMEX:XLE | no aligned snapshot | 0 | | | | | | |
| `xyz:XYZ100` | NASDAQ:NDX | no aligned snapshot | 0 | | | | | | |
| `xyz:ZHIPU` | - | no reference | 0 | | | | | | |
| `xyz:ZM` | NASDAQ:ZM | no aligned snapshot | 0 | | | | | | |
