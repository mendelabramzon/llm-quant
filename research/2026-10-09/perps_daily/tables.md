## Deterministic tables — Hyperliquid, 20:25 to 21:25 UTC

US cash equities were in **after-hours** at the window close (Fri 17:25 ET). Every HIP-3 equity, index and commodity market below traded through it anyway.


### The venue

| | |
|---|---:|
| perp DEXes | 11 |
| markets listed | 537 |
| markets not delisted | 336 |
| markets that traded in the hour | 310 |
| open interest | $15.4B |
| 24h notional volume | $6.2B |
| notional traded in the hour | $117.5M |
| trades in the hour | 127,697 |

### Every perp DEX on the venue

| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |
|---|---|---:|---:|---:|---:|---:|---|
| `core` | HyperCore (first-party) | 234 | 176 | $11.8B | $84.3M | — | the protocol |
| `xyz` | XYZ | 133 | 105 | $3.5B | $31.5M | 1x | deployer |
| `io` | EntropyIO | 11 | 9 | $62.7M | $1.3M | 1x | deployer |
| `para` | Paragon | 38 | 17 | $18.2M | $257.1k | 0.5x, 1x | deployer |
| `mkts` | Markets By Kinetiq | 24 | 3 | $11.1M | $24.1k | 1x | deployer |
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
| `xyz` | 84 | 0.198 | -0.057 | 0.529 |
| `para` | 26 | 0.183 | -0.094 | 0.522 |
| `io` | 8 | 0.101 | 0.026 | 0.189 |
| `core` | 54 | -0.111 | -0.322 | 0.387 |

### What the sweep found at the top severity

| detector | finding |
|---|---|
| `roll_premium` | xyz:BRENTOIL: the book prices the roll 0.39 of a step ahead of a +3.43% calendar spread; longs are paid 311% a year, the step costs 250%, net 60% while the roll lasts |
| `funding_carry` | xyz:BRENTOIL pays longs 311% a year and costs 12.8bp to get in and out: 3.6 hours to break even |
| `premium_drift` | xyz:CL: the premium moved the same way 7 hours running, -0.173% to -0.301%, and funding is now -113% a year |
| `premium_drift` | xyz:NATGAS: the premium moved the same way 7 hours running, 1.560% to 2.371%, and funding is now 771% a year |
| `premium_drift` | xyz:BRENTOIL: the premium moved the same way 7 hours running, -0.538% to -0.839%, and funding is now -311% a year |

### Funding carries, priced against what they cost to hold

Size is $100,000. The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own multiplier. Capacity is the smaller of the book within 25bp and the headroom under the HIP-3 open-interest cap.

| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |
|---|---|---:|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | long | 311% | 12.8bp | 3.6 h | $1.1M | $204.4M | $3.3M |
| `xyz:NATGAS` | short | 771% | 21.9bp | 2.5 h | $30.2k | $20.4M | $726.4k |
| `xyz:PURRDAT` | short | 25% | 51.4bp | 179.0 h | $7.0k | $17.5M | $22.2k |
| `CHIP` | long | 20% | 41.0bp | 179.7 h | $16.1k | $11.1M | $57.5k |
| `USELESS` | short | 19% | 39.4bp | 181.2 h | $10.8k | $9.8M | $183.1k |
| `xyz:QCOM` | short | 17% | 36.4bp | 188.6 h | $36.5k | $5.0M | $61.6k |
| `xyz:CL` | long | 113% | 12.7bp | 9.8 h | $135.0k | $135.7M | $2.8M |
| `xyz:WDC` | short | 19% | 21.6bp | 97.7 h | $19.3k | $4.6M | $30.2k |
| `xyz:CBRS` | short | 21% | 21.4bp | 89.4 h | $98.8k | $101.6M | $68.1k |
| `xyz:HOOD` | short | 20% | 20.7bp | 92.4 h | $183.0k | $29.1M | $30.9k |
| `io:NBIS` | short | 21% | 20.7bp | 87.3 h | $11.6k | $8.7M | $270.0k |
| `xyz:AVGO` | short | 16% | 18.9bp | 104.6 h | $73.8k | $12.7M | $38.0k |
| `io:OAI` | short | 29% | 22.2bp | 66.5 h | $2.8k | $5.5M | $125.3k |
| `xyz:CRCL` | short | 20% | 16.3bp | 70.3 h | $56.7k | $122.9M | $1.8M |
| `xyz:NBIS` | short | 41% | 20.6bp | 44.6 h | $45.1k | $29.7M | $219.2k |
| `TRX` | long | 29% | 16.6bp | 49.8 h | $63.6k | $13.7M | $43.0k |

### Premiums that widened in one direction, hour after hour

| market | hours running | premium path (%) | funding now |
|---|---:|---|---:|
| `xyz:CL` | 7 | -0.173 → -0.178 → -0.198 → -0.221 → -0.230 → -0.235 → -0.253 → -0.301 | -113% |
| `xyz:NATGAS` | 7 | +1.560 → +1.649 → +1.708 → +1.828 → +1.926 → +2.071 → +2.221 → +2.371 | 771% |
| `xyz:BRENTOIL` | 7 | -0.538 → -0.590 → -0.634 → -0.640 → -0.674 → -0.713 → -0.762 → -0.839 | -311% |

### The same underlying on two builder books

| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| SNDK | `xyz` | 1580.7 | 1580.1 | 5% | $122.1M | $2.5M | 1786 |
| SNDK | `io` | 1581.6 | 1581.1 | 5% | $4.8M | $577.2k | 4069 |
| NBIS | `xyz` | 221.85 | 221.76 | 41% | $29.7M | $219.2k | 699 |
| NBIS | `io` | 221.82 | 221.65 | 21% | $8.7M | $270.0k | 1366 |

### Hyperliquid funding against Binance and Bybit

| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |
|---|---:|---|---:|---:|---:|---:|
| XRP | 11% | Bybit -11% | 22% | 13.1bp | 102 h | $279.2M |
| USELESS | 22% | Bin 74% | 52% | 39.4bp | 134 h | $9.8M |
| TRX | -29% | Bin -50% | 21% | 16.6bp | 136 h | $13.7M |
| VVV | 11% | Bybit -23% | 34% | 28.3bp | 148 h | $68.6M |
| AAVE | 11% | Bybit -17% | 28% | 24.3bp | 150 h | $72.7M |
| MON | 11% | Bybit -19% | 30% | 26.0bp | 151 h | $46.7M |
| GRAM | 11% | Bin -18% | 29% | 30.1bp | 179 h | $32.5M |
| SKY | -19% | Bin 11% | 30% | 31.7bp | 184 h | $6.5M |
| CHIP | -19% | Bybit 11% | 30% | 41.0bp | 239 h | $11.1M |
| kPEPE | 11% | Bin -6% | 17% | 23.7bp | 243 h | $27.3M |

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

22 snapshots over 24 minutes. The test is the correlation of first differences between mark and oracle: an oracle that tracks the book has a correlation near 1 and can still hold a constant offset, which is a real basis; an oracle that has stopped moving has no variance at all, and its premium is an artifact that will vanish when it updates.

| regime | markets |
|---|---:|
| oracle moves independently | 75 |
| oracle tracks the book | 63 |
| both frozen | 53 |
| oracle frozen while the book moved | 15 |

### Verification

`perp_scan.py verify` — 5 numeric checks, 7 identities, all_ok = **True**.

| identity | checked | failed | worst |
|---|---:|---:|---:|
| the venue’s premium is within two percent of the instantaneous impact-mid basis | 336 | 0 | 0.00e+00 |
| the reported basis equals the recomputed one | 537 | 0 | 0.00e+00 |
| the annualised funding equals the hourly rate times 8760 | 537 | 0 | 0.00e+00 |
| open interest in USD equals size times mark | 336 | 0 | 0.00e+00 |
| cap utilisation equals open interest over the cap | 267 | 0 | 0.00e+00 |
| the best ask is not below the best bid | 140 | 0 | 0.00e+00 |
| the round-trip cost never falls as the order grows | 140 | 0 | 0.00e+00 |

Coverage: 537 markets, 331 with candles, 140 with an order book, 140 with funding history. Collection failures: 5.

