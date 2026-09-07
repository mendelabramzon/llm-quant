# The dollar-yield surface, and what it is worth at size

Ethereum mainnet, **2026-09-07 21:27:35 to 23:27:35 UTC**, blocks 25,928,160–25,928,758 (599 blocks, 141,411
transactions, 491,580 logs) [[verify: blocks]] [[verify: transactions]] [[verify: logs]], plus head reads at
23:40 UTC. Written by Claude on 2026-09-08. Every number is in `analysis.json`, `head_state.json` or `detectors.json`;
`live_scan verify --out research/2026-09-08/live_2h` re-derives thirteen of them from the raw blocks through an
independent path and all thirteen pass. Nothing was signed or broadcast.

The window itself is unremarkable and that is useful: base fee 0.035–0.084 gwei (median 0.051), no liquidations,
exchange net flow −$5.5M in stables and −$3.0M in ETH [[verify: exchange-net-stables]] [[verify: exchange-net-eth]],
$7.1M of USDC minted against $6.8M burned [[verify: usdc-mint]] [[verify: usdc-burn]]. A quiet tape is the right
place to measure a *standing* surface, because nothing in it is a reaction to anything.

## 1. Two dollar markets on mainnet beat simply holding the savings rate. Both are small.

The right benchmark for a dollar is not the same dollar on another venue — it is the dollar an issuer will pay you for
in unlimited size at no venue risk. That is Sky's savings rate, **3.60%**. Measured against it, at the head:

| asset | venue | supply APR | vs savings rate | supplied | utilisation |
|---|---|---:|---:|---:|---:|
| **USDtb** | **Aave v3** | **8.05%** | **+4.45pp** | $15.4M | 83.2% |
| **USDC** | **Compound v3** | **5.69%** | **+2.09pp** | $374.4M | 90.8% |
| PYUSD | Aave v3 | 3.88% | +0.28pp | $7.6M | 87.8% |
| USDT | Aave v3 | 3.60% | +0.00pp | $2,962.9M | 93.6% |
| USDC | Aave v3 | 3.59% | −0.01pp | $2,156.3M | 100.0% |
| USDC | SparkLend | 3.54% | −0.06pp | $25.6M | 92.2% |
| DAI | Aave v3 | 3.07% | −0.53pp | $131.6M | 86.7% |
| USDT | Compound v3 | 3.00% | −0.60pp | $185.3M | 83.4% |
| USDT | SparkLend | 2.62% | −0.98pp | $391.8M | 82.8% |
| USDS | SparkLend | 2.32% | −1.28pp | $748.0M | 65.6% |
| USDe | Aave v3 | 1.72% | −1.88pp | $652.3M | 39.0% |
| PYUSD | SparkLend | 0.59% | −3.01pp | $100.0M | 16.7% |

Twenty-seven dollar-denominated reserves across Aave, SparkLend and Compound; **two of them pay more than doing
nothing.** Roughly $8.5B of supplied dollars sits in reserves paying *less* than the issuer's own savings rate. That is
the single most useful thing in this note, and it reframes every cross-venue rate finding this project has produced:
a gap between two venues is only an opportunity if the higher one clears the savings rate, and most do not.

Two of the recurring findings in the ledger fail exactly that test. "PYUSD pays 3.29pp more on Aave than SparkLend" is
true and worth **28bps** over the actual alternative, because SparkLend's PYUSD reserve is 16.7% utilised and paying
almost nothing. "DAI pays 0.61pp more on Aave than SparkLend" is a gap between 3.07% and 2.46%, **both below the
savings rate**. The detector was measuring the emptiness of the low venue.

## 2. The capacity of the best of them is $1.4M, not $94M.

Compound v3's USDC Comet sits at **90.77% utilisation against a kink at exactly 90.0%**. Read directly from the
contract's own `getSupplyRate`:

| utilisation | supply APR |
|---:|---:|
| 89.0% | 3.20% |
| 89.5% | 3.22% |
| **90.0% (kink)** | **3.24%** |
| 90.5% | 4.84% |
| 90.77% (now) | 5.70% |
| 91.0% | 6.44% |
| 92.0% | 9.63% |

The whole 5.69% headline lives in 0.77 percentage points of utilisation. Supplying into it moves you down that cliff:

| you supply | resulting utilisation | your APR | earned over the savings rate, per year |
|---:|---:|---:|---:|
| $100k | 90.74% | 5.61% | $2,012 |
| $1.0M | 90.53% | 4.92% | $13,169 |
| **$1.25M** | **90.46%** | **4.72%** | **$14,054** |
| $5.0M | 89.57% | 3.22% | −$18,774 |
| $50M | 80.07% | 2.88% | −$358,708 |

**$1.25M is the entire opportunity, and it is worth about $14,000 a year.** At $5M you are earning less than you would
have earned holding USDS and doing nothing.

The same arithmetic applied to Aave's USDtb reserve (IRM read on-chain: optimal 80%, base 0, slope1 4%, slope2 50%,
reserve factor 20%) gives **$227k of capacity worth $5.4k a year**. $626k of new supply takes utilisation to the kink
and the rate from 8.05% to 2.56% — below the savings rate.

So the honest summary of the mainnet dollar surface tonight: **the best two rates on the board are jointly worth about
$19,000 a year.** Everything larger pays less than the risk-free dollar.

## 3. Aave's $2.16B USDC reserve had $503 of exit liquidity at 23:41 UTC.

Caught live, read straight from the contract:

```
23:41:12 UTC   Aave v3 USDC   supply 12.87%   borrow 14.30%
supplied 2,156,510,591   borrowed 2,156,510,088   utilisation 1.000000   available 503
```

Supply fell from $2,308M to $2,156M while borrows did not move: an account withdrew about **$152M of USDC supply**,
taking a two-billion-dollar reserve to exactly 100% utilisation. This is the daily 23:30–00:10 UTC balance routine this
repo has been tracking since 2026-09-05, and it is the first time it has been captured at the head rather than
reconstructed from logs afterwards.

The 12.87% supply rate it prints is not an opportunity. It exists for about half an hour, and over that half hour
$10M of supply earns roughly **$55** more than it would at the savings rate. The finding is the other side of the same
fact: **for roughly thirty minutes every night, USDC cannot be withdrawn from Aave.** That is a hard operational
constraint on any strategy whose exit leg is that reserve — including the Compound-versus-Aave rotation above — and it
is now recorded as a risk on that strategy rather than as prose.

It is also a warning about every rate this system reads. A spot read of Aave USDC taken at 23:41 would have entered
the ledger as a 9.3-percentage-point cross-venue gap. The de-spiker caught it (`0.05pp on window medians`) — but only
after two bugs were fixed, below.

## 4. Three corrections to this system's own machinery, each of which changed a number

Written up because the loop's value is in what it catches, including in itself.

**The de-spiker was comparing supply rates against borrow medians.** `analysis.json` stores each rate point as
`[block, supply_apr, borrow_apr]`, and both `rate_dispersion` and the new detector read index 2 — the borrow rate —
when de-spiking a supply rate. It survived a shipped detector because both sides of the comparison were wrong in the
same direction, so the gap still looked plausible. Fixed: the USDT Aave-over-Spark gap went from 1.66pp to **0.98pp**.

**The venue pair was chosen on spot rates and then de-spiked.** During the nightly spike the highest USDC venue is
whichever reserve is momentarily starved, so the comparison became Aave-over-Spark, the de-spiker correctly called it
a spot artifact — and the real standing finding, Compound-over-Spark, was never compared at all. The spike did not
merely add a false finding; it **hid a true one**. Fixed by selecting the pair on de-spiked rates.

**Capacity was modelled with a smooth curve on markets that have a cliff.** `rate_dispersion` modelled dilution as
`r·S/(S+X)`, which cannot express a kink. On Compound USDC that reported **$93.8M of capacity worth $945k a year**
against a true **$1.4M worth $15k** — a 63x overstatement of the number that decides whether a strategy is worth
doing. Fixed by pricing against each venue's real model: Aave and SparkLend from the reserve's own IRM parameters,
Compound from its `getSupplyRate` sampled across utilisations at head time. The detector's ladder now reproduces the
on-chain reads to two decimal places.

Two supporting changes made those possible: the head now discovers reserves from `getReservesList()` instead of a
hardcoded fifteen-symbol list — which is why USDtb, the highest dollar rate on the board, was invisible to every size
check until today — and it fetches each reserve's IRM parameters, which had been silently returning nothing.

## 5. What is proposed, and what it is worth

The strategy book (`research/strategies.jsonl`, `scripts/strategies.py`) now holds every strategy this repo has
produced, each with legs, capacity, kill criteria and a quote series. Ranked at this window:

| strategy | status | net APR | capacity | quote age |
|---|---|---:|---:|---:|
| USDG captive-flow v4 LP | fork-proven | 15.80% | $150k | 28h |
| Sky savings rate over Aave USDS | monitored | 3.48% | $1B | current |
| Aave USDtb supply | proposed | 2.36% | $227k | current |
| PT-sUSDS fixed vs the savings rate | proposed | 1.37% | $1M | 35h |
| Compound v3 USDC over SparkLend | monitored | 1.05% | $1.4M | current |
| sUSDe cooldown redemption | fork-proven | standing bid | $600k | 35h |
| Morpho USDT borrow vs Aave | proposed | 0.91% | $24M | **stale** |

Two were retired on economics rather than on mechanism and are not shown: mainnet JIT liquidity (the entire field
nets ~$6k a year at a 10% win rate) and the StacyVault reward harvest ($7.42 a run — the bug is real and still
asserted by `verify`, and it pays nothing).

The shape of that table is the finding. **The largest edges are the smallest positions.** The 15.8% LP is a $150k
idea; the $1B-capacity idea pays 3.48% and is a savings account. Nothing in the book is simultaneously large and
mispriced, which is what an efficient dollar market is supposed to look like, and it is worth stating plainly rather
than implying otherwise by quoting headline rates.

**Only three of the seven have a quote a detector produced.** The other four were measured once in a dated session and
have not been re-measured since; the Morpho USDT borrow spread is already past its staleness threshold. That gives the
next round of work an ordering principle: write the detector that re-prices the highest strategy in the book that
nothing re-prices — the captive-flow LP first, then the Pendle fixed-versus-floating gap, then the sUSDe ask against
NAV.

## 6. Everything else in the window

- **Two atomic bot pairs passed $480M each through 7 transactions, ending exactly flat** (0x04ca7a7e, 0x26de7861 —
  the second returned $240,000,001 against $240,000,001 received, to the dollar). Both are contracts, neither is
  labelled, and their flow is not exchange flow.
- **Address poisoning continues** at the same background rate; `mass_distribution` again finds the 0.0003-USDT dust
  campaign, now at a smaller scale in a two-hour window.
- **JIT liquidity took $3.86 of pool fees** across 44 episodes — 0.06% of fees, consistent with the two 2026-09-07
  windows. Still not a tax on passive LPs.
- **No liquidations, no mislabelled-flow hits.** The address book survived this window without a contradiction, which
  it did not manage on either 2026-09-07 window.

## What is checked, and what is not

The `[[verify: id]]` markers name recipes in `scripts/verify.py` that re-derive that number from the raw blocks
through a path sharing no aggregation code with `analyze`. The rate table in section 1, the capacity ladders in
section 2 and the live blackout read in section 3 are head reads and direct contract calls, not window aggregates;
they carry no marker because no recipe re-derives them yet, and a `getSupplyRate` ladder is the obvious next check to
write. The Compound and Sky rates cannot be de-spiked at all — neither venue emits rate-update logs — so those two
rows are single readings by construction.
