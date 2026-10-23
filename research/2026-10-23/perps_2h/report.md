_(no insights.md written yet)_

---

## Deterministic tables — Hyperliquid, 13:09 to 15:09 UTC

US cash equities were in **regular** at the window close (Fri 11:09 ET). Every HIP-3 equity, index and commodity market below traded through it anyway.


### The venue

| | |
|---|---:|
| perp DEXes | 11 |
| markets listed | 547 |
| markets not delisted | 342 |
| markets that traded in the hour | 339 |
| open interest | $15.7B |
| 24h notional volume | $8.5B |
| notional traded in the hour | $1.5B |
| trades in the hour | 862,695 |

### Every perp DEX on the venue

| dex | name | markets | traded | open interest | 1h notional | fee scale | oracle set by |
|---|---|---:|---:|---:|---:|---:|---|
| `core` | HyperCore (first-party) | 234 | 178 | $11.7B | $817.7M | — | the protocol |
| `xyz` | XYZ | 138 | 116 | $3.9B | $689.9M | 1x | deployer |
| `io` | EntropyIO | 15 | 11 | $78.0M | $12.7M | 1x | deployer |
| `para` | Paragon | 39 | 29 | $17.3M | $1.4M | 0.5x, 1x | deployer |
| `mkts` | Markets By Kinetiq | 24 | 5 | $9.9M | $656.5k | 1x | deployer |
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
| `mkts` | 4 | 0.226 | 0.140 | 1.042 |
| `xyz` | 82 | 0.183 | -0.000 | 0.485 |
| `para` | 27 | 0.176 | -0.100 | 0.513 |
| `io` | 7 | 0.155 | 0.010 | 0.581 |
| `core` | 57 | -0.128 | -0.364 | 0.430 |

### Funding carries, priced against what they cost to hold

Size is $100,000. The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own multiplier. Capacity is the smaller of the book within 25bp and the headroom under the HIP-3 open-interest cap.

| market | paid side | funding APR | round trip | break-even | capacity | open interest | 1h notional |
|---|---|---:|---:|---:|---:|---:|---:|
| `xyz:SNXX` | short | 19% | 39.3bp | 184.6 h | $31.1k | $2.2M | $1.6M |
| `xyz:BB` | short | 22% | 32.3bp | 127.5 h | $143.5k | $8.9M | $509.7k |
| `xyz:AAOI` | short | 21% | 24.6bp | 100.8 h | $14.0k | $5.3M | $837.4k |
| `ZRO` | short | 36% | 28.0bp | 67.5 h | $0 | $77.1M | $2.4M |
| `xyz:BE` | short | 54% | 24.1bp | 39.0 h | $0 | $7.6M | $8.9M |
| `WLFI` | long | 44% | 21.2bp | 42.6 h | $51.4k | $11.7M | $161.1k |
| `xyz:GOLD` | short | 26% | 11.2bp | 37.4 h | $1.0M | $329.3M | $14.4M |

### The same underlying on two builder books

| symbol | dex | mark | oracle | funding APR | open interest | 1h notional | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| DRAM | `xyz` | 47.431 | 47.42 | 5% | $73.0M | $14.3M | 11333 |
| DRAM | `io` | 47.413 | 47.416 | 5% | $1.4M | $986.4k | 3352 |
| SNDK | `xyz` | 1284.1 | 1283.8 | 5% | $127.4M | $65.2M | 25195 |
| SNDK | `io` | 1282.8 | 1283.4 | 5% | $7.4M | $6.9M | 15633 |
| UNITREE | `xyz` | 93.695 | 94.087 | -175% | $23.2M | $1.6M | 5564 |
| UNITREE | `para` | 93.3741 | 93.4199 | -90% | $2.1M | $157.6k | 2013 |
| RDDT | `xyz` | 148.23 | 148.3 | -55% | $294.8k | $95.5k | 679 |
| RDDT | `para` | 148.3224 | 148.305 | 7% | $62.2k | $15.1k | 228 |
| LRCX | `xyz` | 230.85 | 230.63 | 38% | $269.4k | $57.9k | 915 |
| LRCX | `para` | 230.6136 | 230.6251 | 7% | $142.0k | $15.9k | 109 |
| CRWD | `xyz` | 249.53 | 249.47 | 9% | $2.6M | $3.0M | 4361 |
| CRWD | `para` | 249.3997 | 249.458 | 7% | $140.5k | $59.2k | 919 |
| AVGO | `xyz` | 327.0 | 326.87 | 5% | $10.9M | $375.1k | 843 |
| AVGO | `para` | 326.69 | 326.9 | 7% | $270.0k | $4.0k | 38 |
| EWY | `xyz` | 151.35 | 151.3 | 5% | $9.8M | $2.8M | 2267 |
| EWY | `io` | 151.27 | 151.3 | 5% | $450.7k | $106.5k | 793 |

### Hyperliquid funding against Binance and Bybit

| coin | Hyperliquid | other venue | spread | HL round trip | break-even | HL open interest |
|---|---:|---|---:|---:|---:|---:|
| WLFI | -46% | Bin 11% | 57% | 21.2bp | 65 h | $11.7M |
| ADA | -18% | Bybit 11% | 29% | 19.9bp | 121 h | $31.1M |
| ZRO | 39% | Bin 7% | 32% | 28.0bp | 153 h | $77.1M |
| ETHFI | 11% | Bybit -8% | 19% | 18.0bp | 165 h | $9.7M |
| CC | 11% | Bin -30% | 41% | 50.3bp | 215 h | $6.0M |
| MORPHO | 11% | Bybit -11% | 22% | 27.2bp | 219 h | $7.3M |
| PENDLE | 11% | Bin -9% | 20% | 28.0bp | 243 h | $10.6M |
| BCH | 11% | Bybit -6% | 17% | 24.2bp | 256 h | $8.4M |
| CASHCAT | 11% | Bybit -17% | 28% | 44.1bp | 280 h | $23.9M |
| GRAM | -9% | Bybit 9% | 18% | 29.8bp | 288 h | $26.8M |

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
| the venue’s premium is within two percent of the instantaneous impact-mid basis | 342 | 0 | 0.00e+00 |
| the reported basis equals the recomputed one | 547 | 0 | 0.00e+00 |
| the annualised funding equals the hourly rate times 8760 | 547 | 0 | 0.00e+00 |
| open interest in USD equals size times mark | 342 | 0 | 0.00e+00 |
| cap utilisation equals open interest over the cap | 271 | 0 | 0.00e+00 |
| the best ask is not below the best bid | 140 | 0 | 0.00e+00 |
| the round-trip cost never falls as the order grows | 140 | 0 | 0.00e+00 |

Coverage: 547 markets, 342 with candles, 140 with an order book, 140 with funding history. Collection failures: 0.

