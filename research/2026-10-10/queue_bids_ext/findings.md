# Queue bids, extended: ether.fi pays exactly what it promises, and LBTC is the next claim in line — 2026-10-10

Every number here is in `analysis.json` (built by `scripts/dislocation_history.py report` from `etherfi_payouts.json`,
`raw/etherfi_long/analysis.json`, `raw/new_assets/analysis.json`, `raw/lbtc_payout/` and `candidates.json`);
[tables.md](tables.md) prints them. Read-only chain access; nothing was traded.

## What was asked

Two things. First, the payout check the book was waiting on before sizing `etherfi-weeth-queue-bid`: does ether.fi's
WithdrawRequestNFT pay the eETH a request fixes, does it charge a fee, how long does it really take, and does the instant
redemption route cap the discount? Second, which other staked or wrapped tokens on Ethereum can a patient bid buy below
what their own redemption pays, ranked by liquidity and access, with the top ones run through the same two-year history
and capacity simulation as the 2026-10-09 study.

## The ether.fi payout check: it pays to the wei, charges nothing, and is faster than the counters said

**What was read.** Every log of the WithdrawRequestNFT proxy (0x7d57…4c2e) from block 20,834,913 to 26,161,639
(2024-09-26 to 2026-10-10), every `AdminOperationsExecuted` of EtherFiAdmin (3,095), every `Rebase` of the LiquidityPool
(3,095, one per admin execution), every `Redeemed` of the RedemptionManager, and every `Upgraded` of the six contracts
involved. Finalization emits nothing on the NFT, so `lastFinalizedRequestId()` was read at all 3,095 admin execution
blocks through an archive node; the 740 daily counter samples of the 2026-10-09 study all agree with it (0 mismatches),
so finalization happens nowhere else. The event layouts were taken from the verified source of all five NFT
implementations in the window (the 2024 one through 2025-03-26, then 2025-03-26, 2025-06-26, 2026-02-12 and the
2026-07-14 "share-rate freeze"). Until July 2026 both events carried a fifth field, `fee`, and the 2024 implementation
emitted `paid + fee` as the claim amount; the decoder handles both versions. Four claims, one per era, were traced: the
ETH sent to the owner equals the decoded payout each time.

**What it paid.** 42,784 requests for 4,768,155 eETH from 30,354 addresses; 42,756 claimed for 4,765,944 ETH. Every
request of 0.01 eETH or more (40,890 claimed) was paid exactly its `amountOfEEth`: 0.0bp at the minimum and the maximum.
The only inexact payouts are eight requests of 2 wei paid 1 wei. **No request carried a fee** (the field was zero on all
42,784). One request was invalidated: id 77151, 750.5 eETH, requested 2026-04-21, never paid. None was seized. At the
end 23 requests (1,460 eETH) were unfinalized, all from the last day.

**Against what NAV.** `amountOfEEth / shareOfEEth` equals the LiquidityPool's Rebase-event share rate at the request
block to 0.002bp at the 99th percentile, and `getRate()` equals that rate at all 310 admin blocks checked. So the
discount the study prices against `getRate()` is the discount the queue pays. weETH's NAV is a step function that moves
only at rebases; the 2026-10-09 study drew a line between daily samples, which is off by −0.30 to +0.24bp at the 1st and
99th percentile of request times (−1.08 to +0.65bp at the extremes): small against a 3–4bp edge, and now removed. The
amount is fixed at the request, so a holder who claims at finalization gives up the yield of the wait: a median 0.73bp,
11.0bp at the 1st percentile, 12.4bp at worst. Against the share value at the actual claim the gap is larger (−3.7bp at
the median), because owners claim a median 2.2 days after finalization and some wait over a year.

**How long.** Request to finalization, measured to the block: 0.79 days at the median request, 6.46 at the 90th
percentile, 16.0 at the 99th, 17.6 at the longest. Weighted by amount it is 1.69 days, because busy days are slow days,
not because big requests wait longer: on the 701 days with both, requests of 100 eETH or more waited a median 0.011 days
longer than requests under 10. The daily counters had said 2.0 days, because a same-day finalization counted as a full
day. Month by month the median ran 0.2 to 0.7 days through March 2025, rose to 10.0 days in August 2025 and 6.9 in
November, fell, rose to 9.7 in April 2026, and has been 0.3 to 1.5 days since May.

**The instant route did not cap the discount.** The RedemptionManager opened on 2025-03-26 with ETH output at 30bp and
added stETH output on 2025-11-12 at 10bp. Of the 400,075 eETH redeemed into stETH, 365,703 went fee-free in 496
redemptions by 124 receivers, two of them 236,904 and 96,722 eETH: the public 10bp route is a small part of it. The
11,183 April 2026 stETH redemptions the 2026-10-09 study cited for 202,563 eETH were 39 fee-free redemptions for 180,827
eETH and 11,144 public ones for 21,736 eETH. Hourly weETH discounts by regime (bp):

| regime | hours | p50 | p90 | p99 | max | >= 10bp | >= 30bp |
|---|---:|---:|---:|---:|---:|---:|---:|
| no instant route (to 2025-03-26) | 4,174 | 3.0 | 5.7 | 13.2 | 57.7 | 2% | 0% |
| ETH out at 30bp (to 2025-11-12) | 5,332 | 4.4 | 25.9 | 40.1 | 59.0 | 33% | 7.5% |
| stETH out at 10bp (since) | 5,939 | 2.9 | 12.8 | 40.7 | 94.6 | 15% | 3.0% |

Discounts wider than either fee kept happening after the routes opened, and the deepest hour came in April 2026. The
routes are bucket-limited and the regimes differ in queue length and stress, so this table cannot say how much the route
trims; it does say the route is not a cap. One decoding trap, fixed: every RedemptionManager implementation before
2026-07-14 emits the amount sent to the receiver in the field its event declares as `feeAmountToStakers`; read
literally, those events show a 99.7% fee.

### The weETH row, re-quoted

Same pools, bid, cost model and split as 2026-10-09: two pool fees, the market cap at the median venue, the hurdle
chosen on 2024-09-26 to 2025-10-03 and scored on the year after. The difference is that the queue is measured per
request and the NAV comes from the Rebase events. The 2026-10-09 run reproduces exactly first ($169,784 at $10M).

| wait model | median wait | $10M out of sample | 95% interval | trailing 90 days | fills (OOS) | median edge | $30M out of sample |
|---|---:|---:|---|---:|---:|---:|---:|
| daily counters (2026-10-09) | 2.0 days | $169,784 | $110,848 to $235,017 | $43,315 | 1,961 | 3.3bp | $411,361 |
| per request, day's median (quoted) | 0.79 days | **$194,238** | $134,517 to $260,084 | $58,190 | 2,044 | 3.7bp | $431,076 |
| per request, day's amount-weighted median | 2.12 days | $217,390 | $137,590 to $321,709 | $45,938 | 2,084 | 3.8bp | $436,415 |

The payout check takes nothing off the edge: no fee, no shortfall, and the NAV the study priced against is the one the
queue pays. The faster measured queue adds a little. That a longer wait model scores higher is path dependence (capital
locked at different moments meets different sales); all three sit inside each other's intervals. **Verdict: the row
stands, re-quoted to $194,238 a year at $10M.** The payout check no longer limits its size. The capacity rule still says
$30M ($431,076, interval $291,336 to $586,626); what should limit it is the shared collateral of the three ETH bids and
the bidders this simulation does not see.

## More assets: LBTC is the only one that clears

GeckoTerminal's 24-hour volume on 2026-10-10 ranks the candidates, counting only pools against the redemption unit.
Mechanics come from verified source and `eth_call`; table E in tables.md has every row.

| rank | token | 24h volume | redemption | verdict |
|---:|---|---:|---|---|
| 1 | LBTC | $12.1M | anyone, to a bitcoin script; ~6 days; pays the rate on the payout day | **proposed** |
| 2 | OETH | $1.09M | anyone, WETH 1:1, no fee; minutes to days | too small: $6,141 a year at $3M |
| 3 | tBTC | $0.55M | anyone, BTC; 0.2% fee; hours | not proposed: one event carries it |
| 4 | swETH | $0.19M | anyone; swEXIT queue | too thin: one $0.16M-deep pool |
| 5 | osETH | $0.16M | open only since 2026-09-03 (the redeemer was a Safe) | permissioned 23 of 24 months; watch |
| 6 | frxETH | $0.12M | anyone; fixed 30-day maturity | too small for a 30-day lock (~22bp of carry) |
| 7 | cbETH | $0.07M | Coinbase account | permissioned |
| 8–10 | sfrxETH, mETH, pufETH | $0.03–0.05M | anyone | too small |
| 11–14 | ETHx, rswETH, cmETH, ankrETH | under $5k | | dead |

Custodial BTC wrappers (WBTC, cbBTC, cirBTC, kBTC, SolvBTC) redeem only for merchants or account holders and were not
ranked. OETH, LBTC and tBTC went through the full history (blocks 20,834,913 to 26,157,137, the existing rows' window).

**LBTC.** Lombard's LBTC trades persistently below what Lombard pays for it. Since August 2025 it carries an exchange
rate: `getRate()`, the inverse of the StakedLBTCOracle's `ratio()`, was 1.00485 BTC on 2026-10-09. The market prices LBTC
between par and that rate. Anyone can redeem it to any bitcoin script for a flat 10,000 sats. The bitcoin is paid off
Ethereum, so the payout was checked on Bitcoin: 55 redemptions were sampled, their scripts turned into addresses, and each
matched to the first payment after the request; 48 matched.

- In 2025, before the rate, they paid one for one after a median 6.0 days (longest 9.6).
- Since November 2025 they pay LBTC times the rate **on the payout day**: all 20 matched payouts are within 0.0 to
  +3.0bp of that day's rate, after a median 5.4 days (longest 10.2).
- The rate moves both ways (it fell 10.6bp on 2026-09-22), so the bid carries about a week of rate risk per fill.

Priced against WBTC and cbBTC at par on all five pools, a $10M bid made $109,761 a year out of sample. But cbBTC traded
about 10bp above WBTC on 2026-10-10. The discount against cbBTC (14.7bp at the hourly median, 10bp or more in 77% of
trading hours) is twice the discount against WBTC (6–8bp). The loop that closes runs through cbBTC: redeem to a
Coinbase deposit address, convert the bitcoin to cbBTC one for one, withdraw, buy again.

On the three cbBTC pools a $10M bid made **$111,136 a year out of sample** (interval $65,117 to $165,420; 1,134 fills;
median edge 13.5bp), and $189,369 annualised over the trailing 90 days, with a 9-day wait (Lombard documents 7 to 9).
Priced instead at the rate six days after each trade, with a six-day wait, it made $121,970. What binds is the LBTC sold
below NAV: $30M earns $115,702.

The row needs a Coinbase account for the return leg. That is a business requirement like the broker behind the equity
carry, not a permissioned redemption; without one, the row carries `go: false`.

**OETH.** Origin's vault redeems for anyone at one WETH per OETH, no fee, and the 693 claims checked paid exactly what was
requested. The queue is fast: a median 20 minutes, 4.9 days at the 90th percentile, 49 days at the longest when the vault
lacked WETH. Origin's own ARM bought OETH at par until 2025-12-17 and bids 25bp under since. OETH sits a median 5.6bp
under par, but little sells deep enough: $6,141 a year at $3M (interval $1,861 to $11,344).

**tBTC.** Threshold redeems for anyone in hours, for 0.2% plus the bitcoin fee. It makes $58,834 a year at $30M, but the
interval starts at $1,840, October 2025 (the 10th–11th crash) carries $64,998 of the value at capacity, and the trailing
90 days run at $1,787. Its pools quote WBTC, whose own basis sits inside the measured discount. Not proposed.

## What this changes in the book

- **`etherfi-weeth-queue-bid` (replace):** $194,238 a year at $10M, capital days 0.8. The "payouts not checked" risk and
  the "once it is run" kill criterion are replaced by the check's own result and a standing re-check.
- **`lombard-lbtc-queue-bid` (new, proposed):** $111,136 a year at $10M on the cbBTC pools, `go` conditional on a
  Coinbase account for the bitcoin-to-cbBTC leg. LBTC is BTC-denominated and shares no collateral with the ETH bids.
- **Not proposed:** OETH (too small); tBTC (one event, the fee, and WBTC's basis); osETH (permissioned until 2026-09-03);
  frxETH, swETH, mETH, pufETH, sfrxETH (too small); cbETH (permissioned); ETHx, rswETH, cmETH, ankrETH (dead).

## Kill criteria

- **weETH:** trailing 90-day value under $10k at $10M ($58,190 now); queue median above 10 days for a month (it touched
  10.0 in August 2025 and 9.7 in April 2026); any claim on 0.01 eETH or more paying less than its request, or any request
  fee (`etherfi --step analyze`); a negative rebase before finalization (since July 2026 a claim pays the lesser of the
  request and the shares at the finalization rate); the public stETH instant fee cut below 5bp.
- **LBTC:** trailing 90-day value under $10k at $10M ($189,369 now); a payout more than 2bp below LBTC times the payout
  day's rate, or a request unpaid after 14 days (re-run the bitcoin sample); the hourly discount to cbBTC below 5bp at
  the median over 30 days (14.7bp now); Coinbase charging for or suspending the conversion; Lombard redemptions disabled
  for over a week.

## What this cannot see

- **Other bidders.** Every value is a ceiling for one participant. The instant route's fee-free users and Origin's two
  ARMs (OETH and stETH) are bidders the simulation does not model, and the ARMs' own fills are not in the pool set.
- **LBTC's payout off Ethereum,** except through a 55-request sample. The wait is assumed (9 days), not measured per
  request. The Coinbase conversion was not tested. Lombard's custody and Babylon risk are not priced.
- **A $10M weETH bid's own request.** The within-day size check covers requests up to a few thousand eETH, not a bid that
  dominates the day's queue.
- **Balancer and Pendle venues** (osETH's Balancer v3 pool, the dead Balancer v2 swETH pools). GeckoTerminal's ranking is
  one day's volume.

## What went wrong and was fixed

- The RedemptionManager's `Redeemed` events showed a 99.7% fee: before 2026-07-14 the field declared as the stakers' fee
  carries the receiver's amount (verified in all four older implementations); the decoder now tells them apart.
- The topic-only `Redeemed` pass caught twelve other protocols' events; the analysis keeps ether.fi's manager only.
- Dust requests showed −5,000bp payouts and 8,482bp rate gaps (2-wei requests). Requests under 0.01 eETH (1,868) are
  reported but kept out of the distributions.
- The first regime table labelled the stETH route "0bp" because its first redemptions were the fee-free ones; regimes are
  now labelled by the fee most redemptions paid.
- LBTC first looked 30–40bp above par, which a 1:1 NAV would call a premium; in fact LBTC has an exchange rate.
  `getRate()` reverts before November 2025, so the NAV is read from the oracle's `ratio()`, which answers from block
  ~22.95M at 1.0.
- LBTC's payout was first assumed fixed at the request, like ether.fi's and Kelp's; the bitcoin payouts showed the rate
  on the payout day, and the history was re-priced that way as a check ($121,970 against $111,136).
- LBTC priced against WBTC and cbBTC at par mixed in a ~10bp basis between them; the proposed row uses cbBTC pools only.
- Infrastructure: three of four public archive endpoints refused (403, 429, 522); 40 reads failed on the fourth and were
  re-read (3,095 of 3,095). The new-asset collector stopped at its default 300k credit ceiling and resumed.
- Repo issues: `python3 -m unittest scripts/test_dislocation_history.py` failed at import without pycryptodome (the module
  now falls back to a pure-Python keccak; the tests pass both ways); the 2026-10-09 note's "202,563 eETH" of April
  instant redemptions is 89% fee-free large holders, not the public 10bp route; the coordinator's brief gave weETH's
  median edge as 4.4bp, which is Lido's (the weETH row said 3.3bp).

## What next

1. **LBTC:** one live cycle (redeem a small amount to a Coinbase deposit address, convert to cbBTC) to confirm the wait
   and a zero-cost return leg; then re-run the bitcoin payout sample monthly as the kill check.
2. **A combined ETH book:** Lido, ether.fi and Kelp on one capital pool, best edge first, to size the weETH bid now that
   the payout check no longer limits it.
3. **Competing bidders:** read Origin's ARMs (OETH and stETH) and ether.fi's fee-free redeemers as competitors; re-run
   osETH after three months of its open redeemer.

## Reproduction

```sh
D=research/2026-10-10/queue_bids_ext
uv run --with pycryptodome python scripts/dislocation_history.py etherfi --step collect  --out $D --last-block 26161639 --seed-headers research/2026-10-09/redemption_history/raw/long/headers.json
uv run --with pycryptodome python scripts/dislocation_history.py etherfi --step finality --out $D --endpoints https://eth.drpc.org
uv run --with pycryptodome python scripts/dislocation_history.py etherfi --step analyze  --out $D --state research/2026-10-09/redemption_history/raw/long/state.json
# weETH re-quote: raw/etherfi_long holds APFS clones of research/2026-10-09/redemption_history/raw/long plus etherfi_payouts.json
uv run --with pycryptodome python scripts/dislocation_history.py analyze --out $D/raw/etherfi_long --assets etherfi,etherfi_ev,etherfi_ev_aw
# new assets (manifest pinned to blocks 20,834,913..26,157,137; state seeded with wsteth_nav and susds_nav)
uv run --with pycryptodome python scripts/dislocation_history.py collect --out $D/raw/new_assets --assets oeth,lbtc,tbtc --batch 8 --max-credits 3000000
uv run --with pycryptodome python scripts/dislocation_history.py nav     --out $D/raw/new_assets --assets oeth,lbtc,tbtc --endpoints https://eth.drpc.org
uv run --with pycryptodome python scripts/dislocation_history.py analyze --out $D/raw/new_assets --assets oeth,lbtc,tbtc,lbtc_cb,lbtc_cb_pay
uv run --with pycryptodome python scripts/dislocation_history.py report  --out $D
python3 -m unittest scripts/test_dislocation_history.py
```

The LBTC bitcoin payout check uses the module's `segwit_address`, `decode_lombard_redeem` and `match_btc_payout`
(tested), which reproduce the sample's decoding exactly (186 of 186 payloads). The mempool.space driver that fetched the
payments was a scratch script; its inputs and outputs are saved in `raw/lbtc_payout`.

## Coordinator's check (2026-10-10)

Recomputed from `etherfi_requests.jsonl.gz` (the decoded per-request file): 42,784 requests, 42,756 claimed, **40,890
claims of at least 0.01 eETH paid exactly their request (payout − request: 0.000000bp at the minimum and the maximum)**,
zero requests or claims with a fee, request-to-finalization median 0.79 days, 90th percentile 6.46, longest 17.57 (42,761
requests with a wait); 4,768,155 eETH requested and 4,765,944 ETH paid. This re-derives the summary from the decoded
events, not from the chain; the four on-chain traces above are the study's own. One portfolio note the row does not
carry: the LBTC bid's $10M of idle cbBTC is long bitcoin unless hedged, and a short BTC perp against it is the cash-and-carry
that `term_carry` measured (Hyperliquid BTC, watch), so the bid can sit on top of a hedged BTC book rather than on idle
dollars.
