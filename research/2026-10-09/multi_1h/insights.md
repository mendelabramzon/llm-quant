# The cross-chain dollar book, third reading: smaller, and the same two rows

**Window.** 2026-10-09 19:02 to 20:03 UTC, ten EVMs (Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, BSC,
Unichain, Linea, Scroll), 63 dollar reserves, benchmark the Sky savings rate at **3.80%** read on chain at 20:45 UTC
(`sUSDS.ssr()`; it was 3.60% in September). Collected, analysed, detected and verified with the unchanged
`scripts/multichain.py` (17 checks and 6 identities pass, `verify.json`), ingested under chain `multichain`, and the
book entry re-quoted from it. The earlier readings were 2026-09-08 06:28 UTC and 2026-09-10 12:52 UTC, so the three
windows sit at three different hours of the day across a month.

| | 2026-09-08 | 2026-09-10 | 2026-10-09 |
|---|---:|---:|---:|
| dollars the whole book absorbs, cheapest source first | $37.3M | $21.1M | **$18.8M** |
| blended spread on that fill | 48bp | 67bp | **58bp** |
| worth a year | $177,794 | $141,068 | **$108,925** |
| USDC rank correlation, chain rate against net CCTP flow | −0.57 | −0.27 | **−0.14** |

**The two rows that held are the two the September note named.** Avalanche's Aave USDC reserve pays 7.30%
(time-weighted over the hour; it was 7.19% on 09-10) and is again the destination for every large USDC switch:
from BSC, Arbitrum and Polygon at about 3.1–3.2% it takes $1.8M each before its own curve dilutes the rate, $37k a
year per source; the cluster is worth about $160k a year summed and less once filled once. And USDT from BSC to
Ethereum is a row for the third time — 0.42% net on $10.5M, $44,473 a year, bound by BSC's withdrawable liquidity —
narrower than September's 0.61–0.69% because Ethereum's USDT rate fell to 3.55%.

**Reading.** The book has shrunk with each reading ($178k → $141k → $109k a year), but it has not rotated since
September: Avalanche at 7.2–7.3% for a month is not a one-hour spike, and the flow correlation, while still negative
(dollars moving toward the lower rate), has drifted toward zero. Most of the Avalanche capacity is in its rate curve,
not in its depth ($4.1M available), so the first few million dollars in take the edge. The strategy entry keeps its
kill criteria (blended spread under 25bp for three windows; capacity under $5M; flow correlation above +0.5 for two);
none fires.
