# The redemption surface: eleven claims, two windows, three queue bids that survive

Claude, 2026-10-10. Every number here is computed by `scripts/dislocation_history.py` (the `--assets` path) and stored in
`analysis.json` (the 210-day window) or `long_window_analysis.json` (two years); [tables.md](tables.md) and
[long_window_tables.md](long_window_tables.md) print them. This note only interprets. Read-only chain access; nothing
was traded.

## Why this study exists

The 2026-09-10 sUSDe study priced one standing bid from history: buy the claim below the NAV the protocol pays, redeem
through the cooldown, and value the bid as frequency x depth x what it could fill. It came to $41.5k a year at the $600k
the USDe exit allows. The state review asked for the same history across the whole redemption surface, so that every
event-driven strategy is priced the same way. This is that study: every Ethereum asset with an open-market price, a
protocol redemption at NAV, and enough DEX volume to measure.

## What was read

Two windows. The first is 210 days, blocks 24,650,913 to 26,157,137 (2026-03-13 20:24 to 2026-10-09 20:07 UTC), the
sUSDe study's first block so the April stress week is inside it, for all eleven assets. The second is 744 days, blocks
20,834,913 to 26,157,137 (from 2024-09-26), for the three assets where one window could not say how often stress comes:
Lido, ether.fi and Kelp. Twenty-seven pools on Curve, Uniswap v3 and v4, and Fluid, chosen from GeckoTerminal's top
pools by volume (`pools_discovered.json`) and kept only where the other side is the redemption unit at par or a token
whose NAV is read:

* staking tokens priced in ETH: stETH and wstETH (Lido), weETH (ether.fi), rsETH (Kelp), ezETH (Renzo), rETH (Rocket
  Pool);
* dollar claims: syrupUSDC and syrupUSDT (Maple), sUSDe (the earlier study, extended a month), USDe against USDC and USDT
  (redemption is for approved parties only);
* two controls with same-block redemption, where any measured edge is a fault of the method: sfrxUSD against frxUSD,
  and sUSDS against DOLA, frxUSD and USDT.

Each swap is priced against the NAV the protocol paid at that block, read daily through public archive nodes and
interpolated. The NAV functions were checked against what the protocols actually paid, from their own events: over two
years Kelp's 4,620 ETH payouts came to a median 0.0bp from `rsETHPrice` at the request (10th to 90th percentile -0.35 to
+0.42bp), Lido's 78,249 claims paid one ETH per stETH, and in the 210 days Renzo's 1,001 requests matched its rate
provider to within 0.16bp either way. The queues were measured, not assumed: Lido from its request and finalization
events (85,179 requests over two years), Maple from its withdrawal managers' events, ether.fi and Kelp from their
request counters read daily, Renzo from `coolDownPeriod()`, which went from 7 to 14 days in the spring. Rocket Pool's
burn capacity, `getTotalCollateral()`, was read daily too.

Not read: cbETH and pufETH (about $2k and $16k of DEX volume a day), eETH (no pool), sDAI (sUSDS is the Sky control) and
the Uniswap v4 USDe/USDC pool (about $13M a day of swaps, too many logs for this pass; four other USDe venues are read).

## The method, and the correction that decided most of the answers

A bid is simulated trade by trade. It matches each sale behind the seller and pays two pool fees on top of the seller's
price: the seller's fee is already in their price, and buying the same amount back pays the mid plus a fee again. It
pays the benchmark rate for every day the queue holds the capital (ETH: Lido's own realised staking rate, 2.37% over the
210 days and 2.70% over two years; dollars: the Sky savings rate charged day by day, 3.60% until 2026-10-06 and 3.80%
since). It cannot fill again until the queue pays. It runs at six sizes from $100k to $30M and seven hurdles from 0 to
20bp; the hurdle is chosen on the first half of each window (to 2026-06-26; to 2025-10-03 for the two-year window) and
the chosen bid is scored on the second half. That is 462 variants on the short window and 126 on the long one, and
every value below is out of sample unless it says otherwise, with a block-bootstrap 95% interval over days.

The first version paid the bid each seller's own price, and it was wrong in a way that mattered. At 17:00 UTC on
2026-09-19 someone sold $5.67M of wstETH 19.9bp under NAV into the Uniswap v3 pool while the median venue sat at 2.0bp.
That is not a redemption opportunity; it is a cross-venue arbitrage a searcher closes in the same block. Per print the
bid books $9,774 on that sale; capped at the market it books $187. So the edge is now capped at the median venue's
recent price less one fee: a patient bid is paid only for the discount the whole market shows. At $10M with no hurdle
the cap cuts the affected fills from $305,889 to $151,649 for Lido over two years, and from $388,798 to $217,355 for
USDe over 210 days. The median, not the best venue, because in April Fluid's oracle-centred weETH pool printed 9.7bp
under NAV while Uniswap traded 60.7bp under and Curve 31.3bp.

The controls behave. sfrxUSD, redeemable into frxUSD in the same block and priced in frxUSD, never traded more than
1.81bp from NAV in 1,794 swaps and earns nothing at any size. sUSDS earns nothing out of sample, but its first half is
not clean: its pools quote DOLA, frxUSD and USDT, none of which is its redemption unit, and their basis against USDS in
April left $35,941 a year of in-sample "value" even after the cap. A control has to be priced in what it redeems into.

## The ranking

| asset | hourly discount p50 / p90 / p99 (210 days) | queue (median) | size | out-of-sample $/yr, 210 days | out-of-sample $/yr, two years | trailing 90 days |
|---|---|---:|---:|---:|---:|---:|
| weETH (ether.fi) | 2.2 / 22.9 / 70.4bp | 1.0 / 2.0 days | $10M | $41,077 ($2,882 to $103,509) | **$169,784** ($110,848 to $235,017) | $43,315 |
| stETH / wstETH (Lido) | 1.2 / 7.1 / 40.5bp | 1.0 / 2.0 days | $10M | $0 | **$129,884** ($75,037 to $194,241) | $19,548 |
| rsETH (Kelp) | 27.9 / 42.0 / 66.4bp | 12.0 / 5.0 days | $3M | **$41,838** ($24,190 to $61,146) | **$44,120** ($26,646 to $63,056) | $40,915 |
| USDe (approved redeemers only) | 0.9 / 7.5 / 15.6bp | same block | $1M | $55,548 ($6,130 to $130,612) | - | $10,230 |
| syrupUSDC (Maple) | 0.4 / 13.9 / 17.3bp | 3 minutes | $3M | $7,988 ($1,129 to $16,712) | - | $9,320 |
| sUSDe (Ethena), net of USDe | -0.6 / 5.4 / 15.1bp | 1 day | $1M | $7,862 ($2,938 to $14,002) | - | $8,083 |
| syrupUSDT (Maple) | 0.5 / 16.6 / 21.5bp | 4 minutes | $1M | $6,119 ($0 to $18,209) | - | $7,139 |
| ezETH (Renzo) | 20.0 / 26.0 / 34.6bp | 14 days | $1M | $5,621 ($2,668 to $9,251) | - | $5,295 |
| rETH (Rocket Pool) | 1.8 / 31.0 / 49.5bp | burn only | $100k | $87 | - | $86 |
| sfrxUSD (control) | -0.2 / 1.2 / 1.8bp | same block | - | $0 | - | - |
| sUSDS (control) | -2.1 / 2.1 / 6.2bp | same block | - | $0 | - | - |

Queues show the 210-day and the two-year medians. The trailing 90 days are from the two-year run for the three assets
it covers. The Lido, ether.fi and Kelp sizes are chosen for the book: the simulation's capacity rule (the smallest size
earning 90% of the best size's value) gives $30M for Lido and ether.fi, still growing, and $10M for Kelp over two years.

## What the second year changed

On the 210-day window Lido and ether.fi looked like options on one stress week. Its first half held the week of
2026-04-17: stETH 45.9bp under par on $698M through the original Curve pool, 44.4bp through the newer one, wstETH 36.0bp
on Uniswap; the Lido queue went from about a day to a 9.2-day median in April as 841,065 stETH were requested for
withdrawal in the month, against 201,709 to 388,035 in every other full month of the window. A $30M bid that kept buying
and queueing made $117,879 in April alone. The second half was quiet. The protocol, having seen one stress week, chose a
20bp hurdle for Lido at every size up to $10M, nothing in the second half reached it, and the out-of-sample value was
zero. At $30M the bid filled three times and its interval includes zero; weETH's was clear of zero only at $10M.

Two years say the quiet quarter was the exception. stETH traded at least 10bp under par in 18.4% of trading hours and at
least 20bp in 5.9%. The weekly discount through the original Curve pool reached 46.0bp (week of 2026-04-16, $686M),
28.4bp (2025-01-30, $666M), 27.0bp (2025-07-17, $578M) and 22.7bp (2025-02-20, $588M), and stayed at 19 to 27bp for
most of August 2025, while the Lido queue ran 7.4, 12.8 and 11.4 days in July, August and September 2025. A $10M bid
earns in almost every month: $60,220 in December 2024, $50,331 and $50,321 in January and February 2025, $34,980 in
August 2025, $31,053 in February 2026, $20,407 in April 2026 — and $229 and $508 in July and August 2026, the quietest
months of the two years. Chosen on 2024-09-26 to 2025-10-03 and scored on the year after, the hurdle at $10M is 1bp and
the bid makes $129,884 a year (2,629 fills, median edge 4.4bp). ether.fi is the same story with its own peaks
($73,981 at $10M in September 2025) and makes $169,784 a year (1,961 fills, median edge 3.3bp). Kelp's two-year number
($44,120 at $3M) confirms its short-window one.

A short window's out-of-sample test is only as good as the regimes in its first half. One stress week is not a
regime.

## rsETH: a permanent discount and a queue that pays it

In the 210 days rsETH traded under the NAV Kelp pays in 94.9% of the hours it traded, by 10bp or more, and by 20bp or
more in 79.7%; the median sale was 28.7bp under. Over two years the discount is smaller and still persistent (median
14.3bp, at least 10bp in 65% of hours). The queue pays exactly that NAV, as the payout check shows, and fixes the amount
at the request: against the NAV on the day of the payout the same payouts are 10.8bp short over the 210 days, the
staking yield the queue does not pay. The queue is the reason the discount exists: 12.0 days at the median over the 210
days (90th percentile 23.1, longest 30.1), 22 days in May. Net of two pool fees and the queue's carry, the median fill
keeps 18.3bp.

A $3M bid filled 171 times out of sample and made $41,838 a year, more than its first half ($24,623); the trailing 90
days run at $40,915. More capital barely helps ($43,488 at $10M) because what binds is the rsETH actually sold below NAV:
$20.7M in 210 days, almost all through one Fluid pool. Month by month at $3M: June $7,043, July $4,417, August $3,276,
September $2,145; May is zero, when the queue ran 22 days and Kelp's NAV sat unchanged on 35 of the window's days before
its largest step, 19.4bp, on 2026-05-16.

Twenty-eight basis points over twelve days is about 8.5% a year on the capital while it is deployed, and the sellers are
paying it to avoid a queue that can stretch to a month and to carry no restaking risk through it. That risk is the
bidder's now: a loss in Kelp's restaked positions during the queue lands on the queued withdrawal, which is paid at the
lower of the request and payout NAVs.

## Lido and ether.fi: queue bids sized by capital, not by flow

The stETH and weETH bids are capital-bound. At $10M the Lido bid filled $1.38B of the $12.8B of qualifying stETH sales
over two years; the rest went by while its capital sat in the queue. Value keeps scaling to the largest size tested:
$401,697 and $411,361 a year out of sample at $30M for Lido and ether.fi. Per fill the edge is small (median 4.4bp and
3.3bp), so the costs carry the answer: two pool fees (1bp on Curve's stETH pools, whose NAV is exactly one ETH), the
queue's carry at 0.74bp a day, gas. The simulation lets the bid take every qualifying sale its capital allows. Other
queue arbitrageurs exist and take the same sales, so these are ceilings for one participant, and the $10M sizing in the
book is deliberately below the capacity rule's $30M.

In a stress the atomic route takes what it can first. ether.fi's instant redemption into stETH, at a 10bp fee, carried
11,183 redemptions for 202,563 eETH in April 2026, against 4 to 73 a month from June. The three ETH bids are not
additive: they dislocate together and draw on the same ETH capital, so in a stress they are one book with one capital
pool, filled best edge first.

## sUSDe, re-quoted

On the extended window the 2026-09-10 method, unchanged, gives **$36,438 a year** net of the USDe basis, down from
$41,506 over 181 days: September added $3,050 and October nothing, and two-thirds of the history's value is still
April's. Over the trailing 90 days the same method runs at $13,234 a year, so the book's kill criterion (under $5k a year
over a trailing 90 days) is not met, and none of the seven 30-day slices meets the old one either. The stricter
simulation agrees on the shape and cuts the level: $7,862 a year out of sample at $1M (interval $2,938 to $14,002),
$8,083 over the trailing 90 days, with the $600k a day USDe exit binding ($205M of qualifying sales missed for it at
$1M). The book row should be re-quoted to the simulation's out-of-sample $7,862, with the extended legacy reading as the
ceiling.

## The rest

* **USDe** is the largest 210-day number and not a strategy for this book: $55,548 a year at $1M (interval $6,130 to
  $130,612), $873,641 in the first half, but only an approved redeemer can turn USDe into dollars at par in the same
  block. It is the business question the sUSDe row already carries: what approved-minter access is worth.
* **Maple** processes redemptions in minutes (a median of about three on syrupUSDC; 7,042 of 7,182 requests done), so
  syrupUSDC and syrupUSDT are nearly instantly redeemable and their discounts are a race against bots, through pools
  with 5 and 8bp fees. $7,988 and $6,119 a year, the second with an interval that includes zero.
* **ezETH** sits about 20bp under NAV, like rsETH, behind a queue that doubled to 14 days, on a fraction of rsETH's
  volume: $5,621 a year at $1M (interval $2,668 to $9,251). Real, and too small to watch on its own.
* **rETH** traded 31bp under NAV at the 90th percentile and cannot be redeemed: `rETH.burn` pays only out of the rETH
  contract's balance and the deposit pool's excess, which held more than 1 ETH on 56% of days, up to 4,001 ETH, and has
  not since 2026-08-05. The in-sample $19,120 is the spring.

## What this changes in the book

* Add `kelp-rseth-queue-bid` ($3M), `lido-steth-queue-bid` ($10M) and `etherfi-weeth-queue-bid` ($10M), quoted at the
  two-year out-of-sample values: $44,120, $129,884 and $169,784 a year. Each is killed on a trailing 90-day value under
  $10k a year, on a queue too long for the discount, or on a payout that stops matching the NAV.
* Re-quote `susde-cooldown-redemption` to $7,862 a year out of sample; its kill criterion is not met.
* USDe, Maple, Renzo, Rocket Pool and the controls are not proposed.

## Assumptions and approximations

* NAVs are sampled once a day and interpolated. The largest daily steps were 1.25bp (wstETH, 210 days; 3.22bp over two
  years), 1.11bp (weETH; 1.55bp) and 19.4bp (rsETH, once); a discount measured on such a day can be off by up to the
  step. Most stETH fills are on Curve, where the NAV is exactly one ETH.
* Pool fees are read at the end of the window (Curve and Uniswap v3 `fee()`), taken from each v4 swap event, or taken
  from Fluid's public configuration; the rsETH and ezETH Fluid pools are not in Fluid's list and are assumed at 1bp.
  Curve's newer pools charge more when imbalanced, so in stress the two-fee cost is understated by up to about a fee.
* Fills are the volume sellers actually sold below NAV, matched at their price plus two fees and capped at the median
  venue. In an AMM a bid that absorbs a sale also lifts the price back, and competing bidders are not modelled, so
  these values are ceilings for one participant.
* Queue waits for ether.fi and Kelp come from counters read once a day, so they are known to a day; a same-day
  finalization counts as one day. ether.fi's payouts were not checked against its NAV in this study.
* The ETH bids are ETH-denominated; dollar values use the day's ETH price. Gas is $10 a fill and fills under $5,000 are
  skipped. Single prints more than 100bp from NAV are venue failures and are excluded and listed in the analysis files.

## Reproduction

```sh
uv run --with pycryptodome python scripts/dislocation_history.py collect --out research/2026-10-09/redemption_history --assets all
uv run --with pycryptodome python scripts/dislocation_history.py nav     --out research/2026-10-09/redemption_history --assets all
uv run --with pycryptodome python scripts/dislocation_history.py analyze --out research/2026-10-09/redemption_history --assets all
uv run --with pycryptodome python scripts/dislocation_history.py render  --out research/2026-10-09/redemption_history --assets all
# two-year window: the same commands with --out research/2026-10-09/redemption_history/raw/long --assets lido,etherfi,kelp
uv run --with pycryptodome python -m unittest scripts/test_dislocation_history.py
```

The two-year run's manifest pins blocks 20,834,913 to 26,157,137 and reuses the 210-day run's headers, NAV samples and
logs for the overlap. The sUSDe legacy re-run lives in `raw/susde_legacy`: the 2026-09-10 study's raw logs, headers and
NAV samples, extended by `collect` and `nav` without `--assets`; its tables are in `susde_legacy_tables.md`. Raw logs
sit under `raw/` and are ignored by git; the manifests carry their hashes.

## Coordinator's check (2026-10-10): what the bid's capital does while it waits

The simulation charges the staking rate (2.37–2.70%) on capital sitting in a queue and nothing on capital waiting for a
fill. Waiting capital held as idle WETH would forgo the staking yield — and against a benchmark of simply holding stETH,
that cost (staking less Aave's 1.33% WETH supply rate, about 1% a year on the whole bid) would take most of the Lido
number. The bid should not be run that way. Backed by WETH borrowed against wstETH collateral (Aave's e-mode, 1.96%
borrow on 2026-10-09) only when a fill happens, the waiting capital keeps earning staking and the queued capital costs
the borrow rate, below the staking carry the simulation charged; so the values above stand as conservative under that
funding, with two caveats added to each entry: the collateral is stETH-family, so it is marked down in exactly the
stress the bid buys into (keep the loan-to-value low), and the three ETH bids share that collateral, so in a stress they
are one book — their dollars a year are not additive.
