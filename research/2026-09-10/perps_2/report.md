# HIP-3, second window: the oil funding was not an oracle error, it is a roll, and it paid anyway

**Window.** 2026-09-10 11:19:34 to 12:19:34 UTC, Hyperliquid: the first-party perp DEX and all ten HIP-3 builder DEXes,
517 markets, 316 not delisted. A 30-minute tape of every market every 20 seconds followed, with public reference
quotes for 118 builder markets once a minute alongside it. `verify` passes 5 numeric re-derivations and 7 identities.
US cash equities were in pre-market at the window close (Thu 08:19 ET). Two more artifacts sit beside this one: the
[funding history since 1 July](../perps_history/history.md) for every live market, and the
[reference comparison](refs.md) of each builder oracle against a price its deployer does not set.

The 2026-09-08 study found XYZ's Brent perp 54bp below its own oracle with longs paid 285% a year, and read it as an
oracle that was high. This window re-checks that claim three ways: what the same positions earned since, what the
oracle actually tracks, and how long such a rate has ever held on this venue.

---

## 1. Two days later the same three markets are wider, and the positions paid

| market | side paid | premium 09-08 | premium 09-10 | funding APR 09-08 | 09-10 | break-even | book at 25bp 09-08 | 09-10 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | long | -0.54% | -0.70% | 285% | **383%** | 2.9h | $474k | **$1.77M** |
| `xyz:CL` | long | -0.42% | -0.64% | 217% | 327% | 3.1h | $294k | $463k |
| `xyz:NATGAS` | short | +0.49% | +0.68% | 259% | 328% | 5.5h | $125k | $33k |

Premiums are the tape means (89 snapshots over 39 minutes after the window; mark and oracle move together with correlation 0.99 and a standard deviation of 2bp around the gap); the book figures are the depth within 25bp on the side a new position
has to cross. The Brent book is nearly four times deeper than two days ago; the gas book is a quarter of what it was.

**Out of sample.** The three `funding_carry` hits of 09-08 were held on paper from that window's close (11:33 UTC) to
the last complete hour of this session, 47 hours, using the settled hourly funding series and the hourly candles
(`perp_history.py`, out-of-sample table in [history.md](../perps_history/history.md)):

| market | funding collected | premium moved against the paid side | hedged proxy, net of the quoted round trip | unhedged, net | realised break-even |
|---|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` long | +164.5bp | -7.3bp | **+145.3bp** | +303.3bp | hour 4 (predicted 3.6) |
| `xyz:CL` long | +136.9bp | -17.0bp | **+109.1bp** | +325.1bp | hour 4 (predicted 4.4) |
| `xyz:NATGAS` short | +156.4bp | -11.9bp | **+124.6bp** | +605.8bp | hour 5 (predicted 6.7) |

The hedged proxy is funding received plus the change in the venue's own premium, which is what a position hedged in
an instrument tracking the oracle exactly would have kept; it is a proxy, not a fill. It is the first time in this
repo that a predicted rate has been followed by a measured realisation, and the realisation was about 0.7% a day on
the hedged reading. The unhedged column is oil and gas moving the right way over two days and says nothing about the
mechanism.

The other five carries the 09-08 sweep flagged at 20% to 130% a year (SYRUP, MEGA, AVGO, SOFTBANK, ORCL) collected 5
to 12bp of funding in the same 47 hours and lost 8 to 64bp on the hedged reading. The rate was the story only where the
premium was structural.

---

## 2. What the XYZ oracle is, measured from outside

The 09-08 note compared the oil oracle with two third-party settlement quotes and concluded the book was the side closer
to the world. This window compares every builder market with a public delayed quote, aligned by the quote's own delay
(`perp_refs.py`, [refs.md](refs.md)). Fifteen references were live during the window (FX, spot metals, the base
metals and platinum group futures, crypto indices, the 10-year yield); the 103 cash-equity references were stale
closes because the US, Korean and Japanese sessions were shut, and are reported but not scored.

| oracle against a live outside reference | median gap |
|---|---:|
| `xyz:GBP`, `xyz:JPY`, `xyz:EUR` against the FX pairs | 0.0bp, -0.3bp, +0.9bp |
| `xyz:GOLD`, `xyz:SILVER`, `xyz:COPPER` against spot gold, spot silver, COMEX copper | +0.7bp, +0.6bp, +0.8bp |
| `para:10Y`, `para:BTCD`, `para:TOTAL2` against US10Y, BTC dominance, total-2 cap | -2.0bp, +4.7bp, -11.5bp |
| `xyz:PLATINUM`, `xyz:PALLADIUM` against the NYMEX front contracts | -8.8bp, -70.7bp |
| `xyz:CL`, `xyz:BRENTOIL`, `xyz:NATGAS` against the front contracts | **-142bp, -172bp, +198bp** |

Ten of fifteen within 25bp, FX and spot metals within a basis point. XYZ's oracle is accurate wherever it can be
checked against one price. The energy markets are the exception, and the reason is that oil has several prices a month
apart. The scanner serves the named contract months, so the oracle can be placed on the curve ([refs_curve.json](refs_curve.json)):

| market | front (Nov / Oct) | second (Dec / Nov) | front over second | oracle | mark | oracle's front weight | mark's front weight |
|---|---:|---:|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | 105.53 | 100.88 | +4.68% | 103.72 | 103.00 | **0.61** | **0.46** |
| `xyz:CL` | 100.39 | 96.58 | +3.87% | 98.90 | 98.31 | **0.62** | **0.45** |
| `xyz:NATGAS` | 2.780 | 2.918 | -4.66% | 2.8336 | 2.8525 | **0.59** | **0.46** |
| `xyz:GOLD` | spot 4344.25 | GC front 4377.8 | -0.77% | 4341.2 | 4344.1 | 1.00 (spot) | 0.95 |

Three markets, three curves, one number: every energy oracle sits 0.6 of the way from the front contract to the
second, and every book sits at 0.46. Gold's oracle is spot, not the future. That pattern has one reading: **the oracle
is a constant-maturity blend rolling from the front month to the second, and the book prices the same blend a few
days further along the roll.** The premium that follows is minus the difference in weight times the calendar spread:
0.15 x 4.68% = 0.70% for Brent (observed 0.70%), 0.17 x 3.87% = 0.66% for WTI (observed 0.64%), and with the gas curve
in contango the same lead puts the book *above* the oracle, 0.13 x 4.66% = 0.61% (observed 0.68%). One mechanism gives
all three magnitudes and both signs. Longs are paid on oil because oil is backwardated; shorts are paid on gas because
gas is in contango.

The funding history shows the roll happening. The premium jumps by more than 40bp in a single hour on only a handful of
hours in 71 days, and the recent ones are at the same clock time:

| hour (UTC) | market | premium before | after | mark that hour | implied oracle that hour |
|---|---|---:|---:|---:|---:|
| 09-08 22:00 | `xyz:BRENTOIL` | -1.02% | -0.43% | +0.12% | **-0.47%** |
| 09-09 22:00 | `xyz:BRENTOIL` | -1.11% | -0.44% | +0.19% | **-0.49%** |
| 09-08 22:00 | `xyz:CL` | -0.83% | -0.37% | +0.12% | -0.34% |
| 09-09 22:00 | `xyz:CL` | -0.95% | -0.39% | +0.22% | -0.34% |
| 09-08 22:00 | `xyz:NATGAS` | +1.03% | +0.34% | -0.23% | +0.46% |
| 09-09 22:00 | `xyz:NATGAS` | +1.16% | +0.54% | +0.05% | +0.67% |

At 22:00 UTC, when the futures reopen after the daily settlement break, the oracle steps down by about a tenth of the
front-to-second spread (0.47% against 4.68% on Brent, 0.34% against 3.87% on WTI, up 0.46% against a 4.66% contango
on gas) while the mark does not move, because the book had already priced the step. So the oracle rolls over roughly
ten trading days, one step a day, the premium is a sawtooth that is narrowest just after 22:00 and widens through the
day as the book prices the next step, and the hourly average of that sawtooth is what the funding formula charges at
half of premium/8 an hour. The 09-08 reading that the oracle was "high" was wrong in the way that matters: nothing is
mispriced, and the funding is the price of being one step ahead of a roll. Expiry rules as published: ICE Brent Nov
2026 ceases 2026-09-30, NYMEX WTI Oct 2026 on 2026-09-22, Henry Hub Oct on 2026-09-28; none of them was verified
against an exchange calendar.

---

## 3. The history says this regime is eleven days old

Seventy-one days of hourly funding and premium for all 316 live markets, 491,692 market-hours
([history.md](../perps_history/history.md)):

| `xyz:` market | hours | mean funding APR | median abs APR | 90th pct | hours over 100% | longest run over 100% | sign flips | premium mean | min | max | funding paid to one side over 71 days |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `BRENTOIL` | 1,716 | -22% | 9% | 113% | 11.0% | **61h (now)** | 308 | -0.049% | -1.53% | +0.53% | 4.34% to longs |
| `CL` | 1,716 | -14% | 5% | 80% | 7.5% | 59h (now) | 291 | -0.033% | -1.57% | +0.60% | 2.68% to longs |
| `NATGAS` | 1,716 | +19% | 9% | 92% | 9.3% | 59h (now) | 230 | +0.041% | -0.50% | +1.16% | 3.63% to shorts |
| `GOLD` | 1,716 | +8% | 5% | 18% | 0.0% | 0h | 58 | +0.022% | -0.10% | +0.13% | 1.56% to shorts |

Over the summer the Brent premium averaged five basis points and changed sign 308 times. Before 7 September the longest
run above 100% was 19 hours, in a cluster on 7 to 13 August: eight episodes of 12 to 19 hours at 150% to 190%, each
collecting 24 to 39bp of funding, each positive on the hedged reading (+29 to +48bp, because the premium relaxed from
-0.21% toward -0.1%), mixed unhedged (-162 to +382bp), and six of the eight had flipped sign within 72 hours. The
current run is three times longer and three times wider than anything in the history. Under the mechanism in section
2 that is what a steep curve does: the premium is the lead times the spread, and a 4.7% one-month backwardation is
what the September supply move produced. The spread's own history was not measured this session (no public hourly
futures history was reachable), so "the premium scales with the spread" is an inference from three markets on one
day and two daily steps, not a regression.

The rest of HIP-3 says extreme funding there is mostly noise. Across XYZ's 104 markets, 9.8% of all market-hours ran
above 100% a year, 6,967 episodes with a median length of one hour, 98.7% of them flipped sign within 72 hours, and the
median episode paid 2.8bp. Ten episodes lasted a day or more in 71 days across 104 markets, and three of them are the
energy run above. On the first-party book the picture is 2.1% of hours, 1,910 episodes, a median of 3bp, and 17
markets over 100% for a day or more, illiquid names (ACE at -347% mean on $648k of open interest) that a book this thin cannot be entered in.

---

## 4. What it is worth, stated with its two clocks

The hedged carry has a clean expression under the mechanism: the long collects the funding and pays the roll. Funding
on Brent is 1.05% a day at the current rate. A constant-maturity *price* index in a 4.68% backwardation rolls down a
tenth of that per trading day, 0.47%, and a futures hedge does not share the roll, so a long perp against short
futures loses that step and keeps the difference: about **0.55% a day, roughly 200% a year, before basis noise**. The
oracle-hedged proxy realised 0.74% a day over the 47 out-of-sample hours because the premium widened less than a
step. At the $1.77M of ask depth within 25bp measured this window that is on the order of $9,000 a day.

Both inputs have a clock. The rate is a function of a calendar spread that was flat in July and steep now, and it will
be what the spread is. The depth is one snapshot on a book that was $474k two days ago. The funding multiplier (0.5)
and the oracle are the deployer's parameters and can change without notice; HIP-3 carries slashing and delisting
risk; the hedge is on a futures exchange, which is a second margin account and a second operational surface; and a
second hedged participant compresses the premium by the act of doing this. The book quotes
`hip3-oil-funding-carry` at 337% because its linked detector prices the funding net of one round trip over a day and
knows nothing about the roll; the hedged expectation above is the number to hold it to, and a `roll_premium`
detector that subtracts the step is the first item below. The entry carries the legs, the capacity, and four kill criteria: funding under 50% for 24 hours,
premium beyond -1.5%, oracle more than 2% off the blend it has tracked, ask depth under $250k. The ledger now holds
the three findings at 2 of 2 windows with the decay column reading 285% to 383%, 217% to 327%, 259% to 328%.

**Cross-builder pairs, priced.** `UNITREE` trades on XYZ and Paragon 21bp apart with 307 percentage points between
their funding rates (XYZ charges shorts 32%, Paragon pays longs 339%); `NBIS` on XYZ and EntropyIO at 75 points,
`CRWD` at 46, `SNDK` at 19. The pair is delta-neutral in the underlying on one margin engine, and the detector now
prices it: Paragon's UNITREE book was too thin to be collected ($6k traded in the hour), EntropyIO's NBIS has $24k of
bid depth within 25bp, and SNDK's $106k pays 19 points gross, which two round trips turn negative over a day. A real
mechanism at a size that does not matter; it stays in the book as `hip3-cross-builder-funding` at $25k so the next
window re-prices it rather than rediscovers it.

**The sUSDe standing bid, priced from 181 days of history** (parallel study, [findings](../susde_history/findings.md)).
Every swap in the three sUSDe pools since 13 March against the NAV Ethena paid at that block: the discount is frequent
and shallow, median 2.8bp, 99th percentile 17bp, one real stress week in April at 17.5bp for 80 hours. A $600k bid,
which is the on-chain USDe exit, would have earned about **$41,500 a year net of USDe's own basis**, two thirds of it
in April; without the capacity cap the same history pays $635k a year, so the exit binds, not frequency or depth. The
book's kill criterion (no ask 10bp under NAV in 30 days) never came close to firing and was the wrong test; it is
replaced by the trailing option value and the exit depth, and the strategy is re-quoted at 6.9% on $600k. Scaling
it is a permissioned-redemption question, not a signal question.

---

## What changed in the machinery

* `scripts/perp_history.py` and its tests: months of hourly funding and candles for every live market, episodes with
  the paid side's realised funding, mark move and hedged proxy, premium snaps, and the out-of-sample table for any
  earlier window's hits. The first version scored every episode against the paid side by exiting on the last extreme
  hour; the test suite pins the corrected convention.
* `scripts/perp_refs.py`: public delayed references for 118 builder markets, aligned by delay, FX-converted where
  the reference is a foreign share, scaled where it is a market cap, session-gated where it is a cash close; and the
  curve placement that decodes the energy oracles. Two mapping errors were caught by the first run and are recorded
  in the module: a private company resolved to a delisted pharmaceutical, and Markets by Kinetiq quotes ETF prices
  (SPY, QQQ, IWM, TLT), not index points.
* The findings ledger accepts perp windows; both perp windows are ingested, so the energy findings recur and decay
  like any other. Perp `funding_carry` and `cross_dex_basis` hits carry `net_apr` and `go`.
* Two strategies added to the book, one re-quoted from history with its kill criterion replaced.
* By the parallel worker: `scripts/dislocation_history.py` and 22 tests, and the sUSDe study.

## What to build next

1. **A daily perp window with the history appended** (about 650 requests) and the calendar spread recorded from the
   scanner in the same snapshot, so premium against spread becomes a regression over weeks rather than three points
   on one day. The roll steps at 22:00 UTC give a clean daily test of the mechanism.
2. **A `roll_premium` detector**: premium minus lead times spread, flagged when the lead exceeds 0.1 and the spread
   exceeds 1%, so the regime's end is detected the day it happens instead of read off a ledger a week later.
3. **The hedge leg priced from the scanner**: the front/second blend the oracle tracks, its quoted depth, and the roll
   schedule, so the strategy's capacity is min(book, hedge) rather than the book alone.
4. **sUSDe scaling**: whether a direct USDe redemption at $5M to $25M is available, which multiplies the one binding
   term of a strategy that is otherwise fully measured.

---

Companion tables: [refs.md](refs.md): oracles against outside references; [refs_curve.json](refs_curve.json): where the oil oracles sit on the futures curve.

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

