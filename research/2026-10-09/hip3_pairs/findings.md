# Same name, two builder books: the funding difference does not pay its round trips — 2026-10-09

`hip3-cross-builder-funding` was quoted once, on 2026-09-10, from a snapshot: UNITREE at 307 points of funding between
Paragon and XYZ, $25k of capacity, `go` no. This re-prices it from every hour of both books since 2026-07-01
(`scripts/hip3_pairs.py`, local store `research/2026-10-09/perps_hip3`, no API calls; numbers in `analysis.json`,
table in `tables.md`). **The line is retired.**

**Method.** Eleven builder pairs share a name with open interest on both books; nine have hours on both sides of the
2026-09-10 13:00 UTC cutoff. Position +1 is long A and short B and earns p (r_A − r_B) − p (f_A − f_B) an hour. The rule
holds the side that receives the funding difference while its trailing-k mean exceeds X a year and leaves below X/2;
(k, X) are chosen per pair from 12 variants on the hours before the cutoff and held fixed after it. Each change of
position pays half of each leg's round trip at $100k as measured on 2026-09-10 (XYZ legs 12–24bp), or 40bp per leg
where a book was too thin to price (every Paragon leg; io:NBIS measured 44bp).

**Result.** Equal-weighted across the nine pairs, the month after the cutoff returned **−18.4% a year (Newey–West t
−2.99; bootstrap CI of the hourly mean entirely below zero)**. Eight of nine pairs lost or stayed flat. The funding
differences are real — a median 18% to 69% a year apart on seven pairs — but they flip often enough that a position
held long enough to collect them pays several round trips, and the two books' independent oracles add a basis with an
hourly standard deviation of 0.6% on UNITREE. The out-of-sample funding collected was +1.0% (AVGO) or less on every
pair but one, against costs of 1–3% a pair.

**The one exception is not evidence.** para:UNITREE / xyz:UNITREE made +2.53% after costs over the month (198 hours
held, funding +3.48%, basis +1.85%, t 1.35). Its in-sample funding was also positive (+2.79%), so the difference is
persistent there in a way it is not elsewhere; but the best of nine pairs, each chosen from twelve variants, being
positive for one month is what chance produces, and half its return was the oracle basis. It stays a watch item —
`hip3_pairs.py analyze` re-run monthly — and Paragon's UNITREE book ($1.5M of open interest, unpriced depth) caps it
at tens of thousands of dollars even if it holds.
