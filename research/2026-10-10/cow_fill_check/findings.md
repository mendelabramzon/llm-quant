# Do resting below-NAV orders fill in a dislocation? CoW Protocol, April 2026 — 2026-10-10

The question comes from the queue-book proposal (research/2026-10-10/queue_book): run the queue bids as unescrowed
signed limit orders, with one balance backing every bid. The simulation assumes a waiting bid is filled at the
market's discount. This checks whether that happened on the record.

- **Scope.** Every CoW Protocol settlement trade during the deepest stETH episode of the two-year window, 2026-04-19 →
  05-09 (blocks 24,917,313–25,054,113): 51,464 trades.
- **Selection.** The trades that bought stETH, wstETH, weETH or rsETH with ETH/WETH: 802 trades, 45,777 ETH, 83 owners.
- **Order details.** Each order's details come from CoW's public API.

**Answer: yes.**

| | fills | ETH | discount to NAV at fill (p10 / p50 / p90) | fill minus venue median (p10 / p50 / p90) |
|---|---:|---:|---|---|
| all LST buys with ETH | 802 | 45,777 | 10.3 / 28.1 / 77.9bp | — |
| orders resting ≥ 1 hour before the fill | 91 | 6,023 | 19.0 / 31.2 / 87.2bp | −2.3 / +3.2 / +7.8bp |

- **Resting orders filled at their limit.** The median limit discount was 30.0bp against a 31.2bp fill, so solvers keep
  most of the surplus. Fills ran slightly deeper than the venue-median discount the simulation caps at.
- **The largest rested fills:**
  - 794 ETH of weETH at 27.6bp, after resting 19 hours;
  - stETH fills of 200–385 ETH at 75–87bp, after resting 1.3–11.5 hours on 2026-04-19.
- **Competition is on price, not speed.** 83 owners bought liquid staking tokens through CoW in those three weeks. The
  bids that won were the deepest ones; none of this required being first in a block.
- **Order class carries no information.** CoW's API classes every order as `limit`. Age at fill is what separates
  resting orders from swaps: median 0.016 hours across all fills, 90th percentile 1.7 hours.

What this does not show: that unescrowed orders stay fillable when the same balance backs several of them. That is
CoW's documented behaviour, and the settlement simply fails a trade the balance cannot cover. It was not observed here.

Numbers: `analysis.json`; code: `scripts/cow_fill_check.py` (collect → orders → analyze), test `scripts/test_cow_fill_check.py`.
