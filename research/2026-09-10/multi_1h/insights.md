# The cross-chain dollar book, second reading: a standing $10M switch and a rotating spike

**Window.** 2026-09-10 12:52 to 13:52 UTC, ten EVMs (Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, BSC,
Unichain, Linea, Scroll), 63 dollar reserves, benchmark the Sky savings rate at 3.60% read on Ethereum. The first
reading was 2026-09-08 06:28 to 07:29 UTC. Both windows now carry `detectors.json` from the new `cross_chain_rate`
detector in `scripts/multichain.py`, both are in the findings ledger under chain `multichain`, and the book hit is one
finding seen in two windows. The collection and detector were built by a parallel worker that was cut off before it
could write this note; the numbers below are its artifacts, read back.

## The book, twice

| | 2026-09-08 | 2026-09-10 |
|---|---:|---:|
| dollars the whole book absorbs, cheapest source first | $37.3M | **$21.1M** |
| blended spread on that fill | 48bp | **67bp** |
| worth a year | $177,794 | **$141,068** |
| switches bound by the destination's rate dilution | 13 | 15 |
| switches bound by the source's withdrawable liquidity | 7 | 8 |
| USDC rank correlation, chain rate against net CCTP flow | -0.57 | -0.27 |
| USDC high and low | Base 4.00%, Scroll 0.36% | Avalanche 7.19%, Scroll 0.37% |

The book is smaller and richer than two days ago, and it is a different book. On 09-08 every large USDC switch ran
to Base, which paid 4.00%. On 09-10 Base is a *source*: the destination is Avalanche at 7.19%, and every USDC switch
in the top six lands there:

| switch | net APR after the bridge round trip | capacity | worth a year | binding side |
|---|---:|---:|---:|---|
| USDT BSC to Ethereum | 0.69% | $10.2M | $70,991 | source withdrawable |
| USDC Optimism to Avalanche | 1.65% | $2.1M | $35,160 | source withdrawable |
| USDC Polygon to Avalanche | 2.11% | $1.6M | $33,604 | destination dilution |
| USDC BSC to Avalanche | 1.99% | $1.5M | $29,833 | destination dilution |
| USDC Arbitrum to Avalanche | 0.54% | $5.3M | $28,649 | destination dilution |
| USDC Base to Avalanche | 1.71% | $1.3M | $21,644 | destination dilution |

Avalanche's USDC reserve pays 4.3 to 4.6 percentage points more than five other chains and absorbs $1.3M to $5.3M
from each before its curve takes the rate back, so the whole Avalanche cluster is about $12M of capacity worth about
$150k a year, and it will be gone when a few million dollars arrive. Base on 09-08 was the same shape at a lower rate.

**What persisted is the one switch that is not a spike.** USDT from BSC to Ethereum was the second row on 09-08
(0.61% net on $10.3M, $62,516 a year) and the first on 09-10 (0.69% net on $10.2M, $70,991 a year), bound both times
by how much USDT can be withdrawn from the BSC reserve. That is a standing $10M switch at 60 to 70bp, two of two
windows, and it is the part of the book worth building a position around. The rest rotates with whichever small
reserve is momentarily over its kink.

**The bridge still is not the arbitrageur.** The rank correlation between a chain's USDC rate and its net CCTP flow
went from -0.57 to -0.27: dollars still moved, on balance, toward the lower rate. Two windows of nine and eight
chains are a weak instrument for this, and the sign is what the claim rests on, not the magnitude.

## What it means for the book

`cross-chain-usdc-switch-book` is now a strategy entry, quoted from the `book` finding each window: $21.1M at 67bp
today, with the USDT BSC-to-Ethereum row as its standing core. Two things discipline the number. Most rows compare
two rates that are both below the Sky savings rate, so a switch is an edge over the *benchmark* only when the
destination clears 3.60%: Avalanche's 7.19% does, Base's 4.00% did, Ethereum USDT at 3.86% barely does. And capacity
is a snapshot of the destination's curve and the source's withdrawable balance, which is why the total halved in two
days without any row disappearing.

Next for this thread: a third window at a different hour, so the persistence column has three points; the per-row
benchmark test made explicit in the detector (destination rate against SSR, not against the source); and the CCTP
correlation measured over a day of flow rather than an hour.
