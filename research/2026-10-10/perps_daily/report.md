_(no insights.md written yet)_

---

Companion tables: [refs.md](refs.md): oracles against outside references; [refs_curve.json](refs_curve.json): where the oil oracles sit on the futures curve.

## Deterministic tables — Hyperliquid, 22:06 to 23:06 UTC

US cash equities were in **weekend** at the window close (Sat 19:06 ET). Every HIP-3 equity, index and commodity market below traded through it anyway.


### The venue

| | |
|---|---:|
| perp DEXes | 11 |
| markets listed | 538 |
| markets not delisted | 336 |
| markets that traded in the hour | 293 |
| open interest | $15.7B |
| 24h notional volume | $2.9B |
| notional traded in the hour | $137.5M |
| trades in the hour | 111,589 |

### Every perp DEX on the venue

| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |
|---|---|---:|---:|---:|---:|---:|---|
| `core` | HyperCore (first-party) | 234 | 178 | $12.1B | $131.1M | — | the protocol |
| `xyz` | XYZ | 133 | 98 | $3.6B | $5.7M | 1x | deployer |
| `io` | EntropyIO | 12 | 9 | $64.8M | $741.4k | 1x | deployer |
| `para` | Paragon | 38 | 5 | $17.6M | $23.1k | 0.5x, 1x | deployer |
| `mkts` | Markets By Kinetiq | 24 | 3 | $11.3M | $7.3k | 1x | deployer |
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
| `para` | 27 | 0.293 | 0.013 | 0.774 |
| `xyz` | 73 | 0.206 | -0.044 | 0.472 |
| `core` | 59 | 0.104 | -0.384 | 0.654 |
| `io` | 8 | 0.081 | 0.059 | 0.171 |

### Funding carries, priced against what they cost to hold

Size is $100,000. The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own multiplier. Capacity is the smaller of the book within 25bp and the headroom under the HIP-3 open-interest cap.

| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |
|---|---|---:|---:|---:|---:|---:|---:|
| `CHIP` | short | 196% | 26.9bp | 12.0 h | $62.1k | $22.9M | $2.5M |
| `CC` | short | 54% | 39.7bp | 65.0 h | $12.2k | $6.7M | $43.1k |
| `MET` | long | 66% | 34.5bp | 45.5 h | $14.0k | $7.6M | $31.5k |
| `io:OAI` | short | 21% | 20.0bp | 84.4 h | $18.8k | $5.6M | $180.9k |
| `XMR` | short | 35% | 23.7bp | 59.8 h | $0 | $67.0M | $149.2k |
| `xyz:CL` | short | 22% | 13.3bp | 53.5 h | $133.0k | $138.4M | $897.0k |
| `xyz:BRENTOIL` | short | 35% | 12.5bp | 31.7 h | $2.7M | $201.0M | $1.6M |

### The same underlying on two builder books

| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| SNDK | `xyz` | 1598.4 | 1597.7 | 11% | $125.0M | $69.7k | 133 |
| SNDK | `io` | 1598.9 | 1598.0 | 8% | $5.2M | $396.9k | 1876 |
| NBIS | `xyz` | 222.78 | 223.0 | -49% | $29.9M | $95.6k | 107 |
| NBIS | `io` | 223.01 | 222.93 | 1% | $9.1M | $62.4k | 422 |
| DRAM | `xyz` | 57.667 | 57.658 | 5% | $76.3M | $40.1k | 110 |
| DRAM | `io` | 57.71 | 57.683 | 3% | $879.8k | $29.9k | 148 |
| EWY | `xyz` | 178.11 | 178.1 | 5% | $8.0M | $22.5k | 104 |
| EWY | `io` | 178.19 | 178.14 | 3% | $460.2k | $6.3k | 34 |

### Hyperliquid funding against Binance and Bybit

| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |
|---|---:|---|---:|---:|---:|---:|
| CHIP | 226% | Bin 3% | 223% | 26.9bp | 21 h | $22.9M |
| TRX | -6% | Bin -32% | 26% | 15.5bp | 103 h | $14.1M |
| CC | 58% | Bybit -8% | 66% | 39.7bp | 105 h | $6.7M |
| STRK | 11% | Bybit -25% | 36% | 24.3bp | 120 h | $55.1M |
| LIT | 11% | Bybit -12% | 23% | 20.2bp | 153 h | $180.7M |
| kPEPE | 11% | Bin -11% | 22% | 20.4bp | 166 h | $27.5M |
| ONDO | 11% | Bybit -6% | 17% | 17.0bp | 176 h | $58.4M |
| BCH | 11% | Bin -6% | 17% | 19.3bp | 199 h | $7.9M |
| XMR | 31% | Bin 11% | 20% | 23.7bp | 209 h | $67.0M |
| ARB | 11% | Bin -9% | 20% | 25.8bp | 226 h | $19.1M |

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

22 snapshots over 23 minutes. The test is the correlation of first differences between mark and oracle: an oracle that tracks the book has a correlation near 1 and can still hold a constant offset, which is a real basis; an oracle that has stopped moving has no variance at all, and its premium is an artifact that will vanish when it updates.

| regime | markets |
|---|---:|
| both frozen | 78 |
| oracle moves independently | 72 |
| oracle frozen while the book moved | 50 |
| oracle tracks the book | 7 |

### Verification

`perp_scan.py verify` — 5 numeric checks, 7 identities, all_ok = **True**.

| identity | checked | failed | worst |
|---|---:|---:|---:|
| the venue’s premium is within two percent of the instantaneous impact-mid basis | 336 | 0 | 0.00e+00 |
| the reported basis equals the recomputed one | 538 | 0 | 0.00e+00 |
| the annualised funding equals the hourly rate times 8760 | 538 | 0 | 0.00e+00 |
| open interest in USD equals size times mark | 336 | 0 | 0.00e+00 |
| cap utilisation equals open interest over the cap | 267 | 0 | 0.00e+00 |
| the best ask is not below the best bid | 140 | 0 | 0.00e+00 |
| the round-trip cost never falls as the order grows | 140 | 0 | 0.00e+00 |

Coverage: 538 markets, 336 with candles, 140 with an order book, 140 with funding history. Collection failures: 0.

