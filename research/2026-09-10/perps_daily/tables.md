## Deterministic tables — Hyperliquid, 12:57 to 13:57 UTC

US cash equities were in **regular** at the window close (Thu 09:57 ET). Every HIP-3 equity, index and commodity market below traded through it anyway.


### The venue

| | |
|---|---:|
| perp DEXes | 11 |
| markets listed | 517 |
| markets not delisted | 316 |
| markets that traded in the hour | 315 |
| open interest | $14.4B |
| 24h notional volume | $10.5B |
| notional traded in the hour | $982.0M |
| trades in the hour | 465,882 |

### Every perp DEX on the venue

| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |
|---|---|---:|---:|---:|---:|---:|---|
| `core` | HyperCore (first-party) | 234 | 177 | $10.4B | $626.5M | — | the protocol |
| `xyz` | XYZ | 119 | 104 | $3.9B | $349.6M | 1x | deployer |
| `io` | EntropyIO | 9 | 5 | $50.4M | $4.2M | 1x | deployer |
| `para` | Paragon | 35 | 25 | $15.6M | $572.6k | 0.5x, 1x | deployer |
| `mkts` | Markets By Kinetiq | 23 | 4 | $5.6M | $1.2M | 1x | deployer |
| `abcd` | ABCDEx | 1 | 0 | $0 | $0 | 1x | deployer |
| `cash` | dreamcash | 17 | 0 | $0 | $0 | 1x | deployer |
| `flx` | Felix Exchange | 16 | 0 | $0 | $0 | 1x | deployer |
| `hyna` | HyENA | 25 | 0 | $0 | $0 | 0.1111x | deployer |
| `km` | Markets by Kinetiq | 23 | 0 | $0 | $0 | 1x | deployer |
| `vntl` | Ventuals | 15 | 0 | $0 | $0 | 1x | deployer |

### How much of its own premium each DEX charges as funding

Hourly funding divided by an eighth of the venue's reported premium, over markets with a premium above two basis points. A ratio near 1 charges the whole premium and the gap should close; a ratio near 0 charges nothing for it.

| dex | markets | median | 10th pct | 90th pct |
|---|---:|---:|---:|---:|
| `para` | 18 | 0.192 | -4.129 | 0.670 |
| `xyz` | 89 | 0.123 | -0.151 | 0.492 |
| `io` | 5 | 0.115 | -0.010 | 1.126 |
| `core` | 60 | 0.088 | -0.328 | 0.549 |

### What the sweep found at the top severity

| detector | finding |
|---|---|
| `funding_carry` | xyz:BRENTOIL pays longs 405% a year and costs 12.2bp to get in and out: 2.6 hours to break even |
| `funding_carry` | xyz:NATGAS pays shorts 417% a year and costs 18.5bp to get in and out: 3.9 hours to break even |
| `funding_carry` | xyz:CL pays longs 350% a year and costs 10.5bp to get in and out: 2.6 hours to break even |
| `premium_drift` | xyz:CL: the premium moved the same way 7 hours running, -0.398% to -0.638%, and funding is now -350% a year |
| `premium_drift` | xyz:BRENTOIL: the premium moved the same way 7 hours running, -0.458% to -0.716%, and funding is now -405% a year |

### Funding carries, priced against what they cost to hold

Size is $100,000. The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own multiplier. Capacity is the smaller of the book within 25bp and the headroom under the HIP-3 open-interest cap.

| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |
|---|---|---:|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | long | 405% | 12.2bp | 2.6 h | $2.4M | $235.2M | $12.6M |
| `xyz:NATGAS` | short | 417% | 18.5bp | 3.9 h | $143.1k | $12.5M | $1.0M |
| `xyz:CL` | long | 350% | 10.5bp | 2.6 h | $889.2k | $199.9M | $22.6M |
| `io:OAI` | short | 59% | 155.7bp | 230.6 h | $3.1k | $7.1M | $215.5k |
| `io:ANTH` | short | 25% | 51.3bp | 181.6 h | $58.6k | $28.3M | $955.5k |
| `xyz:QCOM` | short | 26% | 45.7bp | 153.3 h | $85.4k | $5.9M | $237.3k |
| `xyz:LLY` | short | 31% | 34.6bp | 98.3 h | $104.7k | $6.4M | $221.5k |
| `PONS` | short | 26% | 32.7bp | 108.5 h | $0 | $92.6M | $6.2M |
| `io:NBIS` | short | 89% | 42.7bp | 42.2 h | $223.1k | $9.8M | $388.2k |
| `xyz:CXMT` | long | 157% | 27.5bp | 15.4 h | $19.2k | $55.2M | $376.1k |
| `xyz:ORCL` | short | 24% | 21.4bp | 78.0 h | $44.9k | $21.9M | $2.2M |
| `xyz:JPY` | long | 15% | 18.3bp | 104.0 h | $1.8M | $37.6M | $116.5k |
| `xyz:MSTR` | short | 16% | 15.9bp | 88.4 h | $696.8k | $41.7M | $2.7M |
| `xyz:COPPER` | short | 25% | 17.9bp | 61.9 h | $109.1k | $18.4M | $333.6k |
| `xyz:EUR` | short | 30% | 18.3bp | 53.1 h | $1.8M | $33.0M | $41.0k |
| `TRX` | long | 39% | 18.4bp | 41.1 h | $49.0k | $14.5M | $645.3k |
| `xyz:CRCL` | short | 42% | 16.7bp | 34.6 h | $116.1k | $86.4M | $6.0M |
| `xyz:SKHY` | long | 31% | 12.5bp | 35.7 h | $1.0M | $218.1M | $14.9M |

### Premiums that widened in one direction, hour after hour

| market | hours running | premium path (%) | funding now |
|---|---:|---|---:|
| `xyz:CL` | 7 | -0.398 → -0.409 → -0.435 → -0.505 → -0.560 → -0.597 → -0.616 → -0.638 | -350% |
| `xyz:BRENTOIL` | 7 | -0.458 → -0.477 → -0.541 → -0.585 → -0.600 → -0.627 → -0.669 → -0.716 | -405% |
| `xyz:NATGAS` | 5 | +0.447 → +0.513 → +0.493 → +0.503 → +0.527 → +0.607 → +0.626 → +0.668 | 417% |
| `xyz:KIOXIA` | 5 | -0.062 → -0.101 → -0.134 → -0.107 → -0.079 → +0.085 → +0.266 → +0.526 | 84% |

### The same underlying on two builder books

| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| NBIS | `xyz` | 229.71 | 229.71 | 5% | $33.0M | $3.3M | 2830 |
| NBIS | `io` | 230.31 | 229.9 | 89% | $9.8M | $388.2k | 1158 |
| UNITREE | `xyz` | 73.132 | 73.201 | -6% | $14.7M | $101.3k | 497 |
| UNITREE | `para` | 73.014 | 73.324 | -279% | $1.8M | $8.7k | 675 |
| RDDT | `xyz` | 152.43 | 152.43 | 52% | $309.0k | $25.5k | 164 |
| RDDT | `para` | 152.3699 | 152.3699 | -204% | $86.9k | $15.9k | 147 |
| AVGO | `xyz` | 362.49 | 362.28 | 9% | $15.7M | $449.1k | 551 |
| AVGO | `para` | 362.87 | 362.32 | 81% | $2.3M | $6.4k | 370 |
| IREN | `xyz` | 43.519 | 43.519 | 19% | $1.8M | $146.5k | 256 |
| IREN | `para` | 43.533 | 43.52 | 16% | $750.0k | $5.6k | 191 |
| CRWD | `xyz` | 211.06 | 211.06 | 5% | $623.3k | $17.9k | 116 |
| CRWD | `para` | 210.9403 | 210.96 | 7% | $64.3k | $24.6k | 676 |
| SNDK | `xyz` | 1689.6 | 1689.1 | 5% | $127.5M | $32.8M | 14123 |
| SNDK | `io` | 1690.9 | 1687.9 | 5% | $4.7M | $2.6M | 7790 |

### Hyperliquid funding against Binance and Bybit

| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |
|---|---:|---|---:|---:|---:|---:|
| TRX | -58% | Bin -15% | 43% | 18.4bp | 75 h | $14.5M |
| PONS | 11% | Bin 77% | 66% | 32.7bp | 87 h | $92.6M |
| JTO | 11% | Bybit -34% | 45% | 26.0bp | 102 h | $4.3M |
| AERO | 11% | Bybit -29% | 40% | 23.6bp | 103 h | $16.4M |
| TRUMP | 11% | Bin -31% | 41% | 25.7bp | 109 h | $12.6M |
| ETHFI | 131% | Bin 10% | 122% | 77.0bp | 111 h | $21.9M |
| PUMP | -26% | Bin 1% | 27% | 19.8bp | 130 h | $167.6M |
| kPEPE | 11% | Bin -18% | 29% | 23.6bp | 142 h | $18.4M |
| VIRTUAL | 11% | Bin -26% | 37% | 33.5bp | 160 h | $10.3M |
| POL | 11% | Bin -22% | 33% | 43.4bp | 228 h | $3.7M |

### Builder DEXes where nothing trades

Each of these required its deployer to stake 500,000 HYPE for at least 183 days.

| dex | name | markets | open interest | deployer |
|---|---|---:|---:|---|
| `hyna` | HyENA | 25 | $0 | `0x53e655101ea3…` |
| `km` | Markets by Kinetiq | 23 | $0 | `0x71f0019cc7fa…` |
| `cash` | dreamcash | 17 | $0 | `0xffa8198c62ad…` |
| `flx` | Felix Exchange | 16 | $0 | `0x2fab552502a6…` |
| `vntl` | Ventuals | 15 | $0 | `0x8888888192a4…` |
| `abcd` | ABCDEx | 1 | $0 | `0x372c7f69d0ec…` |

### Verification

`perp_scan.py verify` — 5 numeric checks, 7 identities, all_ok = **True**.

| identity | checked | failed | worst |
|---|---:|---:|---:|
| the venue’s premium is within two percent of the instantaneous impact-mid basis | 316 | 0 | 0.00e+00 |
| the reported basis equals the recomputed one | 517 | 0 | 0.00e+00 |
| the annualised funding equals the hourly rate times 8760 | 517 | 0 | 0.00e+00 |
| open interest in USD equals size times mark | 316 | 0 | 0.00e+00 |
| cap utilisation equals open interest over the cap | 245 | 0 | 0.00e+00 |
| the best ask is not below the best bid | 140 | 0 | 0.00e+00 |
| the round-trip cost never falls as the order grows | 140 | 0 | 0.00e+00 |

Coverage: 517 markets, 315 with candles, 140 with an order book, 140 with funding history. Collection failures: 1.

