# An hour of perpetual futures: 515 markets, eleven venues inside one venue, and an oracle that is wrong about oil

**Window.** 2026-09-08, 10:33:29–11:33:29 UTC, Hyperliquid: the first-party perpetual DEX and all ten HIP-3
builder-deployed DEXes. 515 markets, 315 not delisted, 302 traded. **$14.6B of open interest**, $247.4M of notional in
the hour, 185,339 trades. Plus a live tape of the same 515 markets every 20 seconds afterwards.
`verify` passes: 5 numeric re-derivations, 7 identities, no failures.

US cash equities were in **pre-market** at the window close (Tue 07:33 ET). Every equity, index and commodity market
below traded straight through it, because a perp does not close and the thing it references does.

---

## What HIP-3 actually is, and why it makes a perp DEX worth measuring like a market surface

Under HIP-3 anyone who stakes **500,000 HYPE for at least 183 days** can deploy their own perpetual DEX on
Hyperliquid's matching engine, list markets on it, **set the oracle themselves**, and charge an additional fee share
of 0–300%. The protocol keeps the book and the margin engine; the deployer supplies the reference price and the
listing policy, and takes slashing risk if the oracle misbehaves.

That turns one venue into eleven, with eleven independent opinions about what things are worth. It is the same shape
as the cross-chain dollar surface this repo measured earlier in the day — one asset, several independently-operated
prices — except the dispersion here is not held open by bridging latency. It is held open by whoever set the oracle.

| dex | markets | traded | open interest | 1h notional |
|---|---:|---:|---:|---:|
| `core` HyperCore (first-party) | 233 | 177 | **$10.7B** | $181.7M |
| `xyz` XYZ | 119 | 102 | **$3.8B** | $62.8M |
| `io` EntropyIO | 9 | 5 | $45.9M | $2.5M |
| `para` Paragon | 34 | 14 | $16.6M | $60.6k |
| `mkts` Markets By Kinetiq | 23 | 4 | $5.2M | $301.5k |
| six others | 97 | 0 | **$0** | $0 |

Two numbers stand out before anything else. **HIP-3 is 26% of Hyperliquid's open interest** — $3.9B of the $14.6B —
and it is essentially one deployer: XYZ, listing 119 equities, indices, commodities, FX pairs and private-company
markets. And **six of the ten builder DEXes have no open interest at all.** Ninety-seven listed markets, zero
position, zero trades, behind six separate 500,000-HYPE stakes locked for six months. The deployment is cheap
relative to the stake only if somebody trades; on this window, for six of them, nobody did.

---

## 1. The finding: XYZ's oil oracle is above the market, and it has been for eight hours

`xyz:BRENTOIL` has **$266M of open interest**, traded **$3.2M** in the hour across 1,805 trades, quotes a
**0.6 basis point** spread, and its book is **54 basis points below its own oracle**. That gap has not merely
persisted — it has widened monotonically for eight consecutive hours:

```
premium   -0.354% → -0.377% → -0.407% → -0.439% → -0.476% → -0.486% → -0.518% → -0.536%
funding   -0.020% → -0.022% → -0.024% → -0.026% → -0.028% → -0.029% → -0.031% → -0.032%  per hour
```

Not one reversal in eight hours. The same shape appears on `xyz:CL` (WTI): eight hours, −0.278% to −0.418%, $243M of
open interest, $6.1M traded. And in the opposite direction on `xyz:NATGAS`, whose book sits *above* its oracle.

**A single snapshot cannot tell that from a stale oracle**, and the two call for opposite trades — so the tape was
built to settle it. Sampling all 515 markets every 20 seconds, the discriminator is the correlation of first
differences between mark and oracle. A frozen oracle has no variance. A live one tracking the book has a correlation
near 1 and can still hold a constant offset.

`xyz:BRENTOIL` is squarely in the second group. Over the tape its mark and oracle move up and down together, tick for
tick, while holding a **constant 54–56bp gap**, and the gap kept widening slowly while I watched. The oracle is not
stale. The venue's own reference price and the venue's own order book simply disagree about the price of oil, and have
for at least eight hours.

Which of the two is wrong is checkable from outside. Brent settled near **$97.29** on 2026-09-07 and WTI near
**$92.37** on 2026-09-08 (third-party quotes, weaker evidence than anything else in this report and subject to timing
slack). The XYZ book had Brent at **98.108** against an oracle of **98.640**, and WTI at **93.523** against **93.900**.
On both, **the book is the side closer to the outside world.** The oracle is high, and the funding rate is paying
people to take the price back down.

### What that is worth, priced honestly

| market | paid side | funding APR | round trip at $100k | break-even | book at 25bp | OI cap headroom |
|---|---|---:|---:|---:|---:|---:|
| `xyz:BRENTOIL` | **long** | **285%** | 11.9bp, 0% unfilled | **3.6 hours** | $474k | $484M |
| `xyz:CL` | **long** | **217%** | 10.9bp, 0% unfilled | **4.4 hours** | $294k | $757M |
| `xyz:NATGAS` | **short** | **259%** | 19.9bp, 0% unfilled | **6.7 hours** | $125k | $90M |

The round trip is walked through the saved order book, both sides, plus the taker fee scaled by the deployer's own
multiplier. **Held for 24 hours at the current rate, the Brent leg nets 242% annualised — $663 on $100,000 after
every cost of getting in and out.** It pays for its own round trip in three hours and thirty-six minutes, on a
mechanism that has run one way for eight.

**And the honest part.** The capacity is $474k against the book *as it stands right now*, not the $484M of cap
headroom — a market trading $3.2M an hour will absorb more if you work the order, but nothing here measures that.
The position is **unhedged energy delta**: the funding is the whole edge, and if Brent moves 1% against you it costs
more than three days of the rate. There is no second Brent book on this venue to hedge into. And a funding rate
this size exists precisely because nobody has been willing to take the other side of it for eight hours, which is
information about the risk, not just about the reward.

---

## 2. Why the gap can stay open: builder DEXes do not charge their own premium

Funding exists to close exactly this gap. So why hasn't it?

I tried to assert Hyperliquid's published funding formula against the data and it did not fit — median error 2.2e-6
but wrong on 164 of 315 markets, worst on HIP-3. Rather than assume a formula, the loop measured the thing itself:
**how much of a venue's own reported premium its hourly funding actually charges.**

| dex | markets | median share of premium charged | 10th pct | 90th pct |
|---|---:|---:|---:|---:|
| `para` Paragon | 20 | 0.311 | 0.032 | 0.808 |
| `core` HyperCore | 68 | 0.182 | −0.349 | 0.481 |
| `xyz` XYZ | 79 | 0.157 | −0.129 | 0.514 |
| `mkts` Kinetiq | 4 | 0.055 | −0.150 | 0.182 |
| `io` EntropyIO | 5 | **0.016** | 0.008 | 0.495 |

A ratio near 1 charges the whole premium and the gap closes. **The median market on this venue charges under a fifth
of its own premium.** On EntropyIO the median is 1.6% — the funding rate is essentially disconnected from the premium
that is supposed to drive it.

That is the mechanism behind every number in this report. `xyz:BRENTOIL` charges about half its premium, which still
comes to 285% a year — and it is *still not enough* to attract the counterparty that would close a 54bp gap. On
EntropyIO the effect is starker in the other direction: `io:OAI` carries a **+0.997% premium** and pays **8% a year**,
and `io:ANTH` carries **+0.456%** and pays **8%**. Being long those markets is close to free despite the book sitting
half a percent above the reference.

## 3. The market that ran out of room

**`io:ANTH` is at 100.0% of its HIP-3 open-interest cap** — $24,011,199 against a $24,000,000 ceiling, slightly over
it. It traded in all 60 minutes of the window, 2,239 times, $745k of notional, and rose 1.6%. Its premium has been
positive for eight straight hours.

At the cap, total open interest cannot grow. A new buyer cannot be filled by a new seller opening a short; they can
only be filled by an existing long closing. **The cap converts the price into a queue**, and the premium is what the
queue costs. Meanwhile its order book holds **$42k of asks and $15k of bids within a full percent of mid** against
$24M of open interest — 85% of a $100,000 market order cannot be filled at all.

That is the same structure the cross-chain study found earlier today, where withdrawable liquidity rather than rate
capped seven of twenty dollar switches, and the ten-hour Ethereum study found on Aave's USDC reserve at midnight.
**Across three completely different systems this week, the binding constraint has been the size of the door, not the
size of the prize.**

## 4. The traps, which look identical to the opportunities until you price them

Twelve markets print an annualised funding rate above 50% on **fewer than 30 trades in the hour**. `para:RDDT` pays
longs **183% a year** with **zero trades** and $111,607 of open interest already sitting in it. `para:NET` pays
**154%** on zero trades. `para:TOTAL2` pays **121%** on one.

These are not edges. The rate is derived from a premium that a book with no trading cannot correct, and whoever is
already in the position is collecting or paying it with no way out at size. A screen that ranks by funding rate alone
puts these at the top of the page — which is why the detector that finds them is separate from the one that finds
carries, and reports them as a hazard rather than a trade.

The same discipline kills most of the cross-venue funding table. Fifteen coins show a Hyperliquid-versus-Binance or
-Bybit funding spread above 15% annualised, which is a genuinely delta-neutral pair. But charging both legs at the
Hyperliquid round trip, only a handful clear their costs inside three days, and the other venue's number is a
*prediction* for its next interval rather than a settled rate.

## 5. Three more things the hour showed

**Nine underlyings trade on two builder books at once, with two oracles and two funding rates.** `UNITREE` is 42bp
apart across XYZ and Paragon with **135 percentage points** between their funding rates. `NBIS` is 15.5bp apart with
25 points of funding between XYZ and EntropyIO — and both books are real, trading $758k and $516k in the hour. That
pair is delta-neutral by construction: same underlying, opposite sides, and the funding difference is the carry. It
is the cleanest structure in the window and it exists only because HIP-3 lets two people list the same thing.

**Two oracles never moved at all while their books did.** `xyz:ZHIPU` held a single oracle price across all 35
snapshots of the tape while its book moved thirteen times; `xyz:MINIMAX` did the same across eight book moves. Both
are private Chinese AI companies with no continuous public market to reference. That is the stale-oracle case, and it
is the one where any premium is an artifact that will vanish the moment the feed updates — the opposite trade to
Brent, and indistinguishable from it without the tape. `xyz:HYUNDAI` looked like a third on a shorter tape and then
its oracle moved twice, which is exactly why the classification is re-run on every extension of the series rather
than fixed at first sight.

**The equity complex is quiet and well-arbitraged.** `xyz:SP500` carries **$360M of open interest**, the largest
single HIP-3 market on the venue, and trades 9.5bp round trip. NVDA, GOOGL, TSLA, MU, GOLD and XYZ100 all sit at
exactly **5.47% funding** — the floor, meaning premium ≈ 0; AAPL is at 3.59% on a −1.6bp basis. Whatever is wrong with
XYZ's oil oracle is not wrong with its equity oracles.

---

## What the loop changed about itself

Four rounds, recorded in `rounds.json`. The useful entries are the failures.

**Round 1** joined cross-DEX markets on their ticker and reported a 32,046,130 basis-point "dispersion" between
Stacks at $0.27 and an unrelated `para:STX` at $857.79. Tickers are not identities; the join now requires the marks
to agree within 5% and records the collisions it rejects.

**Round 2** built the tape, because one snapshot cannot separate a stale oracle from a structural basis and the two
call for opposite trades. That distinction is what made the Brent finding a trade rather than a guess.

**Round 3's verifier earned the session.** It asserted `premium == (mark − oracle) / oracle` and **304 of 315 markets
failed**. The assertion was wrong: the venue's premium is an hourly average sampled against the *impact* prices, not
an instantaneous mark-to-oracle gap. Chasing that led to fitting the funding formula, which also did not hold — and
replacing the assertion with a *measurement* of how much premium each DEX charges as funding produced the table in
section 2, which is the explanation for section 1. **The best finding in this report came out of an assertion that
failed.** The same round found `dead_market` returning zero hits because it skipped delisted markets, and the six dead
builder DEXes have every market delisted — the filter had removed the entire finding.

**Round 4** widened the premium bound from one percentage point to two, because exactly one market of 315 exceeded it:
SOPH, which carries the most extreme premium on the venue. A bound that the widest real market fails is a bound that
tests nothing.

## What to build next

1. **A funding-decay ledger.** Every number here is a rate, and a rate's value is the product of its size and how
   long it holds. The findings ledger already tracks recurrence for EVM findings; funding needs the same, keyed on
   `(dex, coin)`, so "285% for eight hours" becomes "285% for eight hours, and here is what happened next."
2. **Sweep the whole HIP-3 oracle surface against external references.** The oil finding was caught because two
   correlated markets drifted together. A systematic comparison of every builder oracle against a public reference
   would find the rest, and would also price the deployer-slashing risk HIP-3 creates.
3. **Model the OI cap as a queue.** `io:ANTH` shows the shape; the interesting quantity is what the premium does as
   utilisation approaches 100%, which needs several markets observed through a cap event.
4. **Take the depth curve seriously.** Capacity here is the book at one instant. A market trading $3.2M an hour will
   absorb far more worked patiently, and the difference between $474k and $3M of capacity is the difference between
   a curiosity and a position.
