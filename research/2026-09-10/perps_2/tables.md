## Deterministic tables — Hyperliquid, 11:19 to 12:19 UTC

US cash equities were in **pre-market** at the window close (Thu 08:19 ET). Every HIP-3 equity, index and commodity market below traded through it anyway.


### The venue

| | |
|---|---:|
| perp DEXes | 11 |
| markets listed | 517 |
| markets not delisted | 316 |
| markets that traded in the hour | 310 |
| open interest | $14.5B |
| 24h notional volume | $9.1B |
| notional traded in the hour | $319.7M |
| trades in the hour | 212,436 |

### Every perp DEX on the venue

| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |
|---|---|---:|---:|---:|---:|---:|---|
| `core` | HyperCore (first-party) | 234 | 178 | $10.5B | $170.5M | — | the protocol |
| `xyz` | XYZ | 119 | 102 | $3.9B | $146.8M | 1x | deployer |
| `io` | EntropyIO | 9 | 5 | $51.6M | $1.5M | 1x | deployer |
| `para` | Paragon | 35 | 21 | $16.1M | $248.8k | 0.5x, 1x | deployer |
| `mkts` | Markets By Kinetiq | 23 | 4 | $5.0M | $602.1k | 1x | deployer |
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
| `para` | 20 | 0.314 | -0.129 | 0.986 |
| `io` | 5 | 0.279 | -0.081 | 0.727 |
| `xyz` | 86 | 0.237 | -0.094 | 0.505 |
| `core` | 61 | 0.047 | -0.337 | 0.461 |

### What the sweep found at the top severity

| detector | finding |
|---|---|
| `funding_carry` | xyz:BRENTOIL pays longs 383% a year and costs 12.6bp to get in and out: 2.9 hours to break even |
| `funding_carry` | xyz:CL pays longs 327% a year and costs 11.5bp to get in and out: 3.1 hours to break even |
| `funding_carry` | xyz:SKHX pays longs 153% a year and costs 13.7bp to get in and out: 7.9 hours to break even |
| `premium_drift` | xyz:CL: the premium moved the same way 7 hours running, -0.371% to -0.616%, and funding is now -327% a year |
| `premium_drift` | xyz:BRENTOIL: the premium moved the same way 7 hours running, -0.432% to -0.669%, and funding is now -383% a year |

### Funding carries, priced against what they cost to hold

Size is $100,000. The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own multiplier. Capacity is the smaller of the book within 25bp and the headroom under the HIP-3 open-interest cap.

| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |
|---|---|---:|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | long | 383% | 12.6bp | 2.9 h | $1.8M | $242.3M | $15.3M |
| `xyz:CL` | long | 327% | 11.5bp | 3.1 h | $463.5k | $194.1M | $59.9M |
| `xyz:SKHX` | long | 153% | 13.7bp | 7.9 h | $838.2k | $372.7M | $7.5M |
| `xyz:NATGAS` | short | 328% | 20.4bp | 5.5 h | $32.7k | $12.5M | $844.2k |
| `io:ANTH` | short | 18% | 59.0bp | 285.5 h | $19.6k | $28.9M | $415.2k |
| `xyz:CXMT` | long | 222% | 29.1bp | 11.5 h | $61.1k | $55.4M | $249.6k |
| `xyz:QCOM` | short | 34% | 38.3bp | 97.6 h | $41.5k | $6.0M | $41.6k |
| `io:NBIS` | short | 80% | 44.1bp | 48.2 h | $23.8k | $9.8M | $333.8k |
| `xyz:ORCL` | short | 15% | 25.1bp | 143.0 h | $101.0k | $21.7M | $143.6k |
| `PONS` | short | 66% | 38.2bp | 50.8 h | $0 | $92.4M | $8.5M |
| `TRUMP` | long | 34% | 25.8bp | 66.8 h | $92.1k | $12.7M | $75.6k |
| `xyz:BABA` | short | 15% | 20.7bp | 118.9 h | $134.6k | $12.0M | $45.4k |
| `PURR` | short | 91% | 40.3bp | 38.7 h | $11.3k | $10.9M | $32.6k |
| `xyz:COPPER` | short | 23% | 20.5bp | 77.4 h | $24.8k | $18.2M | $468.3k |
| `xyz:JPY` | long | 34% | 22.0bp | 56.1 h | $301.5k | $37.6M | $311.5k |
| `xyz:EUR` | short | 41% | 23.4bp | 49.5 h | $603.3k | $33.2M | $62.2k |
| `xyz:CRCL` | short | 19% | 16.4bp | 75.7 h | $139.5k | $75.5M | $2.5M |
| `xyz:MSTR` | short | 28% | 15.7bp | 49.1 h | $341.1k | $41.1M | $57.6k |
| `xyz:DRAM` | short | 27% | 12.8bp | 41.8 h | $219.9k | $78.8M | $3.6M |
| `xyz:SKHY` | long | 39% | 14.1bp | 31.8 h | $713.8k | $211.6M | $2.5M |

### Premiums that widened in one direction, hour after hour

| market | hours running | premium path (%) | funding now |
|---|---:|---|---:|
| `xyz:CL` | 7 | -0.371 → -0.398 → -0.409 → -0.435 → -0.505 → -0.560 → -0.597 → -0.616 | -327% |
| `xyz:BRENTOIL` | 7 | -0.432 → -0.458 → -0.477 → -0.541 → -0.585 → -0.600 → -0.627 → -0.669 | -383% |

### The same underlying on two builder books

| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| SNDK | `xyz` | 1735.4 | 1735.4 | 5% | $135.5M | $2.0M | 1944 |
| SNDK | `io` | 1735.2 | 1735.2 | -14% | $5.0M | $628.3k | 3925 |
| NBIS | `xyz` | 231.24 | 231.24 | 5% | $33.4M | $761.7k | 1248 |
| NBIS | `io` | 231.22 | 231.27 | 80% | $9.8M | $333.8k | 1294 |
| UNITREE | `xyz` | 73.329 | 73.41 | -32% | $14.7M | $47.4k | 227 |
| UNITREE | `para` | 73.177 | 73.5872 | -339% | $1.8M | $6.3k | 426 |
| CRWD | `xyz` | 205.47 | 205.48 | -40% | $610.3k | $37.7k | 216 |
| CRWD | `para` | 205.5229 | 205.5229 | 7% | $63.6k | $1.2k | 76 |

### Hyperliquid funding against Binance and Bybit

| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |
|---|---:|---|---:|---:|---:|---:|
| MORPHO | 11% | Bybit -67% | 78% | 42.0bp | 95 h | $4.7M |
| WLFI | 11% | Bybit -33% | 44% | 24.1bp | 95 h | $11.5M |
| ADA | -19% | Bin 11% | 30% | 20.5bp | 120 h | $32.7M |
| JTO | 11% | Bybit -22% | 33% | 22.4bp | 120 h | $4.5M |
| kPEPE | 8% | Bin -22% | 30% | 21.1bp | 124 h | $19.4M |
| AERO | 11% | Bin -17% | 28% | 21.0bp | 130 h | $16.7M |
| VIRTUAL | 11% | Bin -22% | 33% | 24.3bp | 130 h | $10.4M |
| SPX | 11% | Bybit -36% | 47% | 36.5bp | 135 h | $5.8M |
| CC | 11% | Bybit -28% | 39% | 31.4bp | 140 h | $4.5M |
| DOGE | 11% | Bybit -7% | 18% | 14.7bp | 142 h | $71.2M |

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

### What the tape says about the oracles

89 snapshots over 39 minutes. The test is the correlation of first differences between mark and oracle: an oracle that tracks the book has a correlation near 1 and can still hold a constant offset, which is a real basis; an oracle that has stopped moving has no variance at all, and its premium is an artifact that will vanish when it updates.

| regime | markets |
|---|---:|
| oracle tracks the book | 295 |
| both frozen | 195 |
| oracle moves independently | 27 |

### Verification

`perp_scan.py verify` — 5 numeric checks, 7 identities, all_ok = **True**.

| identity | checked | failed | worst |
|---|---:|---:|---:|
| the venue’s premium is within two percent of the instantaneous impact-mid basis | 316 | 0 | 0.00e+00 |
| the reported basis equals the recomputed one | 517 | 0 | 0.00e+00 |
| the annualised funding equals the hourly rate times 8760 | 517 | 0 | 0.00e+00 |
| open interest in USD equals size times mark | 316 | 0 | 0.00e+00 |
| cap utilisation equals open interest over the cap | 244 | 0 | 0.00e+00 |
| the best ask is not below the best bid | 140 | 0 | 0.00e+00 |
| the round-trip cost never falls as the order grows | 140 | 0 | 0.00e+00 |

Coverage: 517 markets, 316 with candles, 140 with an order book, 140 with funding history. Collection failures: 0.

