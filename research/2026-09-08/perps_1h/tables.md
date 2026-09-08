## Deterministic tables — Hyperliquid, 10:33 to 11:33 UTC

US cash equities were in **pre-market** at the window close (Tue 07:33 ET). Every HIP-3 equity, index and commodity market below traded through it anyway.


### The venue

| | |
|---|---:|
| perp DEXes | 11 |
| markets listed | 515 |
| markets not delisted | 315 |
| markets that traded in the hour | 302 |
| open interest | $14.6B |
| 24h notional volume | $6.4B |
| notional traded in the hour | $247.4M |
| trades in the hour | 185,339 |

### Every perp DEX on the venue

| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |
|---|---|---:|---:|---:|---:|---:|---|
| `core` | HyperCore (first-party) | 233 | 177 | $10.7B | $181.7M | — | the protocol |
| `xyz` | XYZ | 119 | 102 | $3.8B | $62.8M | 1x | deployer |
| `io` | EntropyIO | 9 | 5 | $45.9M | $2.5M | 1x | deployer |
| `para` | Paragon | 34 | 14 | $16.6M | $60.6k | 0.5x, 1x | deployer |
| `mkts` | Markets By Kinetiq | 23 | 4 | $5.2M | $301.5k | 1x | deployer |
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
| `para` | 20 | 0.311 | 0.032 | 0.808 |
| `core` | 68 | 0.182 | -0.349 | 0.481 |
| `xyz` | 79 | 0.157 | -0.129 | 0.514 |
| `mkts` | 4 | 0.055 | -0.150 | 0.182 |
| `io` | 5 | 0.016 | 0.008 | 0.495 |

### What the sweep found at the top severity

| detector | finding |
|---|---|
| `funding_carry` | xyz:BRENTOIL pays longs 285% a year and costs 11.9bp to get in and out: 3.6 hours to break even |
| `funding_carry` | xyz:NATGAS pays shorts 259% a year and costs 19.9bp to get in and out: 6.7 hours to break even |
| `funding_carry` | xyz:CL pays longs 217% a year and costs 10.9bp to get in and out: 4.4 hours to break even |
| `premium_drift` | SOPH: the premium moved the same way 7 hours running, -0.018% to -1.159%, and funding is now -1053% a year |
| `premium_drift` | xyz:CL: the premium moved the same way 7 hours running, -0.278% to -0.418%, and funding is now -217% a year |
| `premium_drift` | xyz:BRENTOIL: the premium moved the same way 7 hours running, -0.354% to -0.536%, and funding is now -285% a year |
| `oi_cap_pressure` | io:ANTH is at 100.0% of its HIP-3 open-interest cap ($24.0M of $24.0M) |

### Funding carries, priced against what they cost to hold

Size is $100,000. The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own multiplier. Capacity is the smaller of the book within 25bp and the headroom under the HIP-3 open-interest cap.

| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |
|---|---|---:|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | long | 285% | 11.9bp | 3.6 h | $474.2k | $265.9M | $3.2M |
| `xyz:NATGAS` | short | 259% | 19.9bp | 6.7 h | $124.5k | $10.1M | $550.3k |
| `xyz:CL` | long | 217% | 10.9bp | 4.4 h | $293.7k | $243.0M | $6.1M |
| `SYRUP` | short | 21% | 47.4bp | 200.4 h | $7.3k | $4.9M | $22.7k |
| `MEGA` | short | 23% | 37.3bp | 141.6 h | $18.6k | $4.5M | $60.3k |
| `xyz:AVGO` | short | 21% | 25.6bp | 107.9 h | $75.0k | $9.8M | $53.0k |
| `xyz:SOFTBANK` | short | 134% | 56.6bp | 36.9 h | $5.3k | $4.6M | $42.3k |
| `io:NBIS` | short | 31% | 26.9bp | 76.3 h | $23.8k | $9.8M | $516.4k |
| `xyz:ORCL` | short | 26% | 21.1bp | 71.6 h | $117.9k | $19.9M | $380.9k |

### Premiums that widened in one direction, hour after hour

| market | hours running | premium path (%) | funding now |
|---|---:|---|---:|
| `SOPH` | 7 | -0.018 → -0.245 → -0.312 → -0.489 → -0.672 → -0.963 → -1.093 → -1.159 | -1053% |
| `xyz:CL` | 7 | -0.278 → -0.299 → -0.324 → -0.332 → -0.358 → -0.383 → -0.414 → -0.418 | -217% |
| `xyz:BRENTOIL` | 7 | -0.354 → -0.377 → -0.407 → -0.439 → -0.476 → -0.486 → -0.518 → -0.536 | -285% |
| `io:ANTH` | 5 | +0.966 → +0.109 → +0.171 → +0.360 → +0.397 → +0.424 → +0.474 → +0.472 | 8% |

### The same underlying on two builder books

| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| UNITREE | `xyz` | 78.729 | 78.751 | 5% | $18.1M | $22.1k | 310 |
| UNITREE | `para` | 78.3987 | 78.1721 | 141% | $1.9M | $2.3k | 167 |
| NBIS | `xyz` | 231.82 | 231.83 | 5% | $56.8M | $757.9k | 1404 |
| NBIS | `io` | 232.18 | 231.83 | 31% | $9.8M | $516.4k | 1350 |
| SNDK | `xyz` | 1758.0 | 1758.3 | -7% | $128.7M | $5.0M | 3422 |
| SNDK | `io` | 1760.2 | 1758.0 | 1% | $5.3M | $657.4k | 4116 |

### Hyperliquid funding against Binance and Bybit

| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |
|---|---:|---|---:|---:|---:|---:|
| SOPH | -1063% | Bin -4380% | 3317% | 117.4bp | 6 h | $4.2M |
| UNI | 11% | Bybit -32% | 43% | 20.3bp | 83 h | $62.8M |
| VVV | 12% | Bin 65% | 53% | 28.4bp | 93 h | $26.9M |
| PONS | 11% | Bin 81% | 70% | 43.2bp | 108 h | $102.7M |
| GRASS | 11% | Bybit -25% | 35% | 33.2bp | 164 h | $9.7M |
| TRX | 11% | Bybit -8% | 19% | 18.2bp | 171 h | $14.4M |
| TRUMP | -15% | Bin 11% | 26% | 25.7bp | 172 h | $14.2M |
| MEGA | 23% | Bin -14% | 37% | 37.3bp | 178 h | $4.5M |
| WIF | 11% | Bybit -24% | 35% | 35.5bp | 179 h | $5.6M |
| LINK | 11% | Bybit -7% | 18% | 19.5bp | 189 h | $80.9M |

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

35 snapshots over 13 minutes. The test is the correlation of first differences between mark and oracle: an oracle that tracks the book has a correlation near 1 and can still hold a constant offset, which is a real basis; an oracle that has stopped moving has no variance at all, and its premium is an artifact that will vanish when it updates.

| regime | markets |
|---|---:|
| oracle tracks the book | 268 |
| both frozen | 195 |
| oracle moves independently | 50 |
| oracle frozen while the book moved | 2 |

### Verification

`perp_scan.py verify` — 5 numeric checks, 7 identities, all_ok = **True**.

| identity | checked | failed | worst |
|---|---:|---:|---:|
| the venue’s premium is within two percent of the instantaneous impact-mid basis | 315 | 0 | 0.00e+00 |
| the reported basis equals the recomputed one | 515 | 0 | 0.00e+00 |
| the annualised funding equals the hourly rate times 8760 | 515 | 0 | 0.00e+00 |
| open interest in USD equals size times mark | 315 | 0 | 0.00e+00 |
| cap utilisation equals open interest over the cap | 244 | 0 | 0.00e+00 |
| the best ask is not below the best bid | 140 | 0 | 0.00e+00 |
| the round-trip cost never falls as the order grows | 140 | 0 | 0.00e+00 |

Coverage: 515 markets, 313 with candles, 140 with an order book, 140 with funding history. Collection failures: 2.

