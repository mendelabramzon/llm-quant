# sUSDe discount history: 180 days of the secondary market against NAV

Claude, 2026-09-10. Every number here is computed by `scripts/dislocation_history.py` and printed in
[tables.md](tables.md) and `summary.json`; this note only interprets. Read-only chain access; nothing was traded.

## Why this study exists

The `susde-cooldown-redemption` strategy in the book is a standing bid: buy sUSDe below the value Ethena pays on
redemption, cool down for a day, redeem at NAV. Every live window since 2026-09-06 re-measured that discount for a few
hours and found it absent or inside the price noise, which is what an event-driven edge looks like on a quiet day and
says nothing about the event. The strategy's value is frequency times depth times what a bid could actually fill, so
it needs a history, not another window. This is that history: 180.7 days of every swap in the three sUSDe pools that
carry the volume, each priced against the NAV the protocol paid at that block.

## What was read

Blocks 24,650,913 to 25,946,913, 2026-03-13 20:24 to 2026-09-10 12:13 UTC (the finalized head when collection began).
Three sUSDe pools: the Uniswap v4 sUSDe/USDT pool (84% of the volume), the Curve sDAI/sUSDe pool the fork proof used,
and the Curve sUSDe/frxUSD pool. 45,089 swap events, of which 30,113 are priced (13,209 sells of sUSDe into a pool,
16,904 buys), 14,961 are under $1,000 and dropped as dust, and 15 are single prints more than 100bp from NAV and
listed separately. That is $1.52B of turnover at NAV, about $0.75B of it sells. NAV comes from `convertToAssets` on
sUSDe and sDAI, sampled once a day at historical blocks through two public archive endpoints and interpolated; sUSDe
NAV rose from 1.22356 to 1.24740 over the period. A fourth pool, Curve USDe/USDC, supplies USDe's own price against the
dollar hour by hour, because the strategy exits by selling USDe and a discount on sUSDe that is really a discount on
USDe is not capturable through the cooldown.

## The distribution: frequent and shallow

Two series are reported. The raw discount is what the `nav_discount` detector measures on a window. The series net of
the USDe basis is what a cooldown redemption that exits into a dollar can keep.

| hourly volume-weighted discount | p50 | p90 | p99 | p99.9 | max | hours above the 2.7bp round trip |
|---|---:|---:|---:|---:|---:|---:|
| raw | 2.8bp | 9.3bp | 17.3bp | 23.0bp | 32.5bp | 51% |
| net of USDe basis | -0.8bp | 5.8bp | 15.7bp | 29.8bp | 44.3bp | 26% |

Half of all trading hours show sUSDe below NAV by more than the round trip in the raw series, and a quarter do net of
USDe's own basis. Only 7% of hours (raw) and 2% (net) reach 10bp; 1% and 0% reach 20bp. The deepest sell of a typical
hour is 4.5bp below NAV; the deepest sell of the whole half year is 43.1bp, a 285,306 sUSDe sale into the Curve
sDAI/sUSDe pool at 01:36 UTC on 2026-04-20 during the one real stress week in the sample. The median sell trade is 5.0bp
below NAV and the median buy 3.5bp, so the secondary market for sUSDe sits structurally a few basis points under NAV:
sellers pay a small fee for immediacy, buyers pay a smaller one, and the cooldown is what both are pricing.

Applying the detector's own rule hour by hour (the volume-weighted discount must clear the round trip by more than
the hour's p10 to p90 spread of trade prices, with the history's median spread of 1.8bp used for hours with fewer than
three trades) gives 193 raw episodes and 154 net ones. Their median length is two hours. 59% of days contain at least
one qualifying hour in the raw series and 34% net. This is not a rare dislocation that a patient bid waits months for.
It is a small, near-permanent discount that briefly widens most days and occasionally, in April, widened a lot.

## What the bid would have earned

The book caps the strategy at $600,000 because that is the USDe exit depth on Curve. With one fill of that size per
episode at the episode's volume-weighted net discount, the history is worth **$25,517 raw and $20,544 net of the USDe
basis, which annualise to $51,554 and $41,506 a year**. Allowing one refill per day inside a multi-day episode raises
that to $76,724 and $44,632. April 2026 carries most of it: $13,489 of the $20,544 net comes from that month, and the
single 27-hour episode starting 2026-04-19 04:00 UTC, with a 23.1bp volume-weighted discount and $34.8M sold into the
pools, is the most valuable event in the sample at $1,226 for a $600k fill. Outside April the net series earned about
$7,000 in five months, roughly $17,000 a year.

The trade-level upper bound is the instructive comparison. If every sell below NAV minus the round trip had been bought
at its own price with no capacity limit and no competition, the history would have paid $635,000 a year net of basis
($913,000 raw). The gap between $41,500 and $635,000 is entirely the $600,000 exit cap: 8,758 sells worth $561M
happened below the round trip, and the cap lets a bid take about $44M of them. Capacity binds, not frequency and not
depth. The way to make this strategy larger is a larger exit, which means Ethena's direct redemption rather than the
Curve pool, and that leg is permissioned.

Three things make even these numbers generous. In an automated market maker the volume sold during an episode is
what pushed the price down, so a bid that absorbs it also lifts the price back toward NAV; the fillable volume is an
upper bound on what one participant could have taken at the recorded prices. A buyer stepping in after a seller pays
the pool fee again (1.01bp in the v4 pool, more on Curve), and the 2.7bp round trip is a fork measurement at the natural
ask, not at size. And other bidders exist: the buy side of these pools is 16,904 trades, many of them arbitrageurs
already doing the cooldown trade.

## The kill criterion

The book retires the strategy if there is no sUSDe ask below NAV minus 10bp in 30 days of windows. Measured as a sell
of at least $10,000 at 10bp or more below NAV, the criterion was **not met in any of the six full 30-day slices**, raw
or net of basis. Net of basis the slices contain 97, 1,012, 6, 14, 8 and 36 such sells, worth $9.4M, $125.6M, $1.5M,
$1.7M, $4.6M and $3.9M. The one-day partial slice at the end contains none, which is the same reading the recent live
windows gave. By its own rule the strategy stays; by its option value it is a $40,000 a year standing bid at the book's
capacity, two thirds of which was one week.

## Two events worth knowing about

**April 19 to 22, 2026.** sUSDe traded 12.1bp below NAV volume-weighted for the whole month and 17.5bp for an 80-hour
stretch, with $133.7M sold into the pools; 67% of April's sell volume was at 10bp or deeper and 13% at 20bp or deeper.
USDe itself held par (0.3bp average basis), so this was a discount on the cooldown, not on the dollar. This is the
shape the strategy was designed for, and it is the only time in six months it appeared at size.

**March 22, 2026, 03:12 to 04:37 UTC.** The v4 sUSDe/USDT pool ran out of USDT on one side: three sells printed at
0.94, 0.86 and 1.01 USDT per sUSDe against a NAV of 1.2245 (2,324bp, 3,012bp and 1,730bp below NAV, $164k of notional),
and two buys an hour later printed 6% to 7% above NAV. In the same minutes the Curve sDAI/sUSDe pool traded 15 to 25bp
below NAV, so this was one venue's liquidity failing rather than a market price for sUSDe; the prints are excluded from
every series above and listed in section F of the tables. A concentrated liquidity position sitting just below NAV in
that pool would have bought sUSDe at a 14% to 30% discount that night, for a few tens of thousands of dollars. That is a
different strategy from the taker bid in the book, and a thin pool's failures are not a schedule.

## What this changes in the book

* The strategy's quote should be an option value at capacity, not an annualised rate from the last window: about
  $41,500 a year net of USDe basis at $600k, of which about $17,000 a year is the ex-April run rate.
* The kill criterion is not close to triggering and is the wrong test: at 10bp it fires on almost every month while
  the value stays small. A better one is the net option value over a trailing 90 days falling below the cost of
  watching it, or the USDe exit depth falling below $250k.
* The `nav_discount` detector's window reading is consistent with this history: it declines the edge on quiet days
  because the edge on quiet days is inside the noise, and it would have fired through April.
* Scaling is an exit problem. The next question is not a better signal but whether a KYC-gated direct USDe redemption
  is available at $5M to $25M, which would multiply the capacity term by ten to forty times against the same history.

## Assumptions and approximations

* NAV is sampled daily and interpolated linearly between samples; sUSDe NAV vests continuously at 1 to 3bp a day, so
  the error is under 1bp. Swap timestamps are interpolated from one header a day and hourly buckets can be off by a few
  minutes at their edges.
* The sDAI leg is valued at its own NAV and DAI at par; USDT, frxUSD and USDC are at par. A stablecoin off par moves
  the raw discount one for one; the USDe basis series corrects for USDe only.
* Discounts are effective trade prices including the fee that trader paid. Sells are what a seller received, which a
  buyer could have matched only as that seller's counterparty at that moment.
* Single prints beyond 100bp from NAV (15 sUSDe prints, 11 USDe/USDC prints) are venue liquidity failures and are
  excluded from the series; 608 sUSDe swaps with no USDe/USDC trade within 24 hours are dropped from the net series.
* Three sUSDe pools and one USDe pool are read. Other venues, over-the-counter flow and direct Ethena mint and redeem
  are not visible, so fillable volume is a lower bound on what was offered and an upper bound on what one bid could
  have taken here.
* Uniswap v4 amounts come from the Swap event; the live windows in this repo confirmed that this pool settles its
  deltas as real transfers through the PoolManager, and no hook check was made here.
* Archive reads went through eth.drpc.org and eth.merkle.io, which both answered `eth_call` at the oldest block;
  publicnode returned 403 and 1rpc.io does not serve historical state. Infura spent 116,490 credits across the two
  collection runs (81,900 for headers plus the sUSDe pools, 34,590 for the basis pool), well under the 300,000 cap.

## Reproduction

```sh
uv run --with pycryptodome python scripts/dislocation_history.py collect --out research/2026-09-10/susde_history --days 180
uv run --with pycryptodome python scripts/dislocation_history.py nav     --out research/2026-09-10/susde_history
uv run --with pycryptodome python scripts/dislocation_history.py analyze --out research/2026-09-10/susde_history
uv run --with pycryptodome python scripts/dislocation_history.py render  --out research/2026-09-10/susde_history
uv run --with pycryptodome python -m unittest scripts/test_dislocation_history.py
```

`collect` is resumable and pins its block range in `manifest.json`; `nav` only needs the header grid, so it can run
while `collect` is still pulling logs. Raw logs sit under `raw/` and are ignored by git; `manifest.json` carries their
hashes and the hashes of every derived file.
