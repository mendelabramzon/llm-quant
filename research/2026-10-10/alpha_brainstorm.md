# Alpha that does not race — a brainstorm, 2026-10-10

Asked: "brainstorm alpha strategies which don't require latency / tx position in block competition". This note lists
the candidates, says where each edge would come from, and marks what this repo has already tested so the list does not
re-propose dead ideas. Six of the candidates were sent to history tests the same day (marked **running**); their
verdicts are recorded at the end once they return.

## The constraint, made testable

A strategy qualifies when all four hold:

1. **The P&L accrues over hours to weeks**, not at one block or one print.
2. **Late entry is cheap**: entering an hour after the signal keeps most of the edge. This is the operational test of
   "no latency": if the edge is gone an hour later, someone faster took it.
3. **Competition is on price, capital, patience or access**, never on transaction ordering, gas bids or co-location.
4. **It can be sized** from a book, a queue, an open interest or a supply schedule, and it has a falsifiable kill
   criterion.

## Where non-racing edges come from

| source | who pays, and why they accept a worse price | examples in this repo |
|---|---|---|
| 1. A constraint someone pays to escape | a holder who cannot wait (queues), cannot sell yet (unlocks), cannot reach a market (KYC, broker), or must exit by a date (delisting) | LST queue bids, unlock pre-short, equity funding carry |
| 2. Slow public information | facts that are public but need reading, joining or labelling; markets with retail attention under-react to them | governance labels, chain fundamentals (new) |
| 3. Calendar flows | flows whose date is known in advance even when their price impact is not | GSCI roll (priced), unlocks, listings |
| 4. Term structure | fixed-versus-floating prices set by speculators with a non-price motive (points, leverage) | Pendle PT switch |
| 5. Segmented capital | the same claim priced differently where moving capital is slow or costly | cross-chain dollar book |
| 6. Risk premia, sold on purpose | insurance with a price and a tail; earned, not found | sUSDe carry, LP in captive flow |

## What the repo has already learned

Survived history (in the book, `go`): Pendle PT-over-floating switch ($216k/yr), weETH/stETH/rsETH queue bids ($344k/yr,
one shared collateral pool in a stress), cross-chain dollar book ($109k/yr), HIP-3 equity funding carry ($330k/yr,
conservative, `go` unset). Under forward test: unlock pre-short.

Failed, and why — the pattern matters more than the list:

| idea | why it failed | lesson |
|---|---|---|
| HIP-3 oil funding carry | the oracle rolls on a GSCI schedule; funding pays 0.9 of each step | a large carry is often a schedule the market already prices |
| HL vs Binance/Bybit funding | real per unit; at size it equals the cost of two-venue capital | a structural spread can be the price of capital, not an edge |
| HL carry factor, cross-builder pairs | t < 1 out of sample; thin books | cross-sectional funding is noise outside a mechanism |
| Polymarket favourites / neg-risk / lag; Kalshi–Polymarket | no edge after fees; crypto-price lag automated away in 2026 | prediction-market lags are a speed game |
| equity open-reaction, ex-dividend, crypto-linked equities | perps price 90% of the gap by the open | price discovery on 24/7 perps is efficient |
| dollar PTs vs savings rate | the high spreads were where the defaults were | a fixed rate far above the benchmark is usually credit risk |

What survived had a **counterparty with a non-price motive**: impatience in a queue, points speculation, retail
leverage demand behind a broker-access barrier, insiders who must hedge before they can sell. That is the filter for
the candidates below.

## The candidates

Prior = a subjective chance that the idea survives an out-of-sample test at a size worth a book row (≥ $1M of capital,
or ≥ $25k per event). Status: **running** (sent to a history test 2026-10-10), *next* (worth a study), *watch*, *low*.

### 1. Paid for a constraint

| # | idea | who pays / why speed is irrelevant | data | prior | status |
|---|---|---|---|---|---|
| 1.1 | **Binance TradFi perps × HIP-3** — use Binance's 217 TradFi perps (179 US equities, 8 commodities) as the 24/7 hedge leg of the equity carry, or trade the funding spread between the two venues | retail leverage demand on both venues; the broker barrier and US hours are what keep the HIP-3 carry open; positions are held for weeks | Binance fundingRate + klines; HIP-3 funding store | 35% | **running** (`tradfi_perps`) |
| 1.2 | **Forced expiry of delisted perps** — a delisting is a dated settlement; funding and basis blow out on the way (43% of the funding study's profit came from 13 later-delisted coins) | holders who must exit by a date; announcement-to-settlement takes days | HL store, Binance CMS announcements, exchange funding | 20% | **running** (`listing_lifecycle` b) |
| 1.3 | **More queue bids** — mETH, ETHx, osETH, pufETH, LBTC, tBTC on Ethereum; and the ether.fi payout check the weETH row is waiting on | sellers who will not wait for a 1–9 day queue; the bid waits | dislocation_history (archive RPC) | 40% for ≥1 new row | **running** (`queue_bids_ext`) |
| 1.4 | **Queue bids off Ethereum** — HYPE LSTs (7-day unstake), sAVAX (15-day), Cosmos/Celestia LSTs (21-day), BTC LSTs on BSC/Base | same mechanism, longer queues, fewer arbitrageurs | GeckoTerminal OHLCV + on-chain exchange rates | 30% | *next* |
| 1.5 | **Unlock pre-short** — short three days before a ≥1% insider cliff, long BTC | recipients hedge before they can deliver | DefiLlama schedules, HL perps | 35% | forward test: 20 events registered 2026-10-10 (`unlock_study.py forward`) |
| 1.6 | **Unlock delivery watch** — date the real delivery from vesting contracts and team-wallet → exchange deposits | fixes 1.5's biggest weakness (modelled dates; postponed or OTC'd cliffs) | on-chain transfers, labels | 25% (as an improvement to 1.5) | *next* |
| 1.7 | **Tokenized stocks as the on-chain stock leg** (xStocks, Ondo GM, Robinhood Chain stock tokens) vs HIP-3 perps | removes the broker; bounded by tokenized-stock DEX depth | GeckoTerminal pools, issuer NAV | 20% | *next* if 1.1 fails |
| 1.8 | **Gated-claim discounts in general** — claims whose exit is gated (100%-utilised lending vaults, cooldowns, RWA redemption windows) sold at a discount by holders who need out now | same as 1.3, a scanner across claim types | ERC-4626 secondary pools, Pendle PTs of gated assets | 15% | *next* |
| 1.9 | HYPE / ZEC spot–perp carry with staking yield | HL spot books thin; single coins, single half-year | HL store | 20% | *watch* (funding study) |

### 2. Slow public information (where an LLM has an edge)

| # | idea | who pays / why speed is irrelevant | data | prior | status |
|---|---|---|---|---|---|
| 2.1 | **Governance events, labelled by the LLM** — fee switches, buybacks, burns, revenue share, emission cuts vs dilution; drift from proposal to vote end and after | holders who don't read proposals; votes last days and tallies are public | Snapshot GraphQL, perp prices | 20% | **running** (`governance_events`) |
| 2.2 | **Chain fundamentals → native token** — stablecoin supply arriving, DEX volume, fees; weekly cross-section; the trading test of the chain-activity framework | slow diffusion of on-chain growth into prices | DefiLlama multi-year history, Binance klines | 20% | **running** (`fundamentals_factor`) |
| 2.3 | **Protocol value/growth factor** — fees or revenue to market cap, and their growth | as 2.2 | DefiLlama fees/revenue | 20% | **running** (same study) |
| 2.4 | **Listing pipelines measured from day +1** — Binance Alpha → perp listing, Coinbase roadmap → listing, Upbit; the drift after the first day, not the first minute | slow followers; the first minute is a speed game and is excluded | announcement archives, klines | 15% | *next* |
| 2.5 | **Tokenomics document diffs** — emission schedule edits, unlock postponements, buyback terms, read and diffed by the LLM | feeds 1.5, 1.6 and 2.1 with better event dates | docs, forums, governance posts | — (infrastructure) | *next* |
| 2.6 | **Hyperliquid positioning** — every position is public; aggregate leverage and liquidation clusters of the largest accounts as a slow contrarian signal | crowded leverage unwinds over days | HL clearinghouse states (forward collection only) | 15% | *next* (needs a collector) |

### 3. Calendar flows

| # | idea | who pays / why speed is irrelevant | data | prior | status |
|---|---|---|---|---|---|
| 3.1 | **New-listing decay** — short new perps against seasoned alts (not just BTC) for the first weeks, net of funding | airdrop and early-holder supply meets thin demand over weeks | HL store, daily candles | 35% | **running** (`listing_lifecycle` a) |
| 3.2 | **Index and ETF reconstitutions** — crypto index funds and ETF baskets announce changes days ahead | index trackers trade on the effective date | issuer announcements, klines | 15% | *next* |
| 3.3 | **ve(3,3) epoch economics** — on Aerodrome/Velodrome, LP where a bribe dollar buys more than a dollar of emissions | bribers overpay for votes or voters under-allocate; epochs are weekly | Base/Optimism voter and bribe logs | 25% | *next* |
| 3.4 | scheduled buybacks (HYPE Assistance Fund, PUMP and others) | constant flows are priced | treasury addresses | 5% | *low* |
| 3.5 | funding-settlement drift on 8-hourly CEX perps; options-expiry pinning | small, minutes-scale | klines | 5% | *low* |

### 4. Term structure

| # | idea | who pays / why speed is irrelevant | data | prior | status |
|---|---|---|---|---|---|
| 4.1 | **Dated futures basis** — buy spot, sell the quarterly when the annualised basis beats the savings rate by a margin; the yield is locked at entry | leveraged longs pay for exposure without funding risk | Binance continuous klines, Deribit, CME (Yahoo) | 50% (as a carry, not an anomaly) | **running** (`term_carry` a) |
| 4.2 | **DIY Ethena** — spot (or wstETH) + short perp on the venue that pays most, against sUSDe and the savings rate | the same longs, on the venue where they pay more | HL and CEX funding stores, sUSDe NAV | 35% | **running** (`term_carry` b) |
| 4.3 | **Boros funding swaps** — implied fixed funding against the funding later realised | fixed-rate buyers with a hedging motive | Boros API (if served) | 25% | **running** (`term_carry` c) |
| 4.4 | **Pendle YT points pricing** — implied value per point against realised airdrops; the other side of the PT switch | points speculators | pendle_history (YT prices), airdrop outcomes | 25% | *next* |
| 4.5 | volatility risk premium (DVOL vs realised) | option buyers pay for convexity | Deribit public API | measurement only | **running** (`term_carry` d) |

### 5. Segmented capital

| # | idea | who pays / why speed is irrelevant | data | prior | status |
|---|---|---|---|---|---|
| 5.1 | cross-chain dollar book | bridging takes minutes and attention; rates differ for days | multichain windows | in the book | running daily |
| 5.2 | **permissionless perp venues vs Hyperliquid** (Lighter, Aster, edgeX) — does coin-level funding structure persist without KYC on either side? | the funding study's open control | venue APIs | 20% | *next* |
| 5.3 | tokenized gold (PAXG/XAUT) vs gold perps | redemption is KYC-gated | DEX/CEX klines, perp funding | 15% | folded into 1.1 |
| 5.4 | **incentive-adjusted dollar yields** — Merkl campaigns and protocol rewards, net of the dilution your own deposit causes | campaign budgets are fixed; attention is not | Merkl API (free) | 30% for small rows | *next* |

### 6. Risk premia, priced and capped

| # | idea | status |
|---|---|---|
| 6.1 | volatility risk premium | measured in 4.5; trading needs an options venue |
| 6.2 | HLP and other Hyperliquid vaults; does vault skill persist? | *next* (vault histories are public) |
| 6.3 | captive-flow LP (USDG) | fork-proven, absent from recent windows |

## Excluded on purpose (speed or ordering decides them)

Sandwiching and back-running, liquidation races, JIT liquidity, CEX–DEX arbitrage, sniping new pools, oracle-update
back-runs, the first minute after a listing or delisting announcement, cross-chain intent filling where the first
filler wins, Polymarket crypto-price lag.

## Cross-cutting changes this list implies

- **Every event strategy gets a pre-registered forward ledger.** `unlock_study.py forward` (register before entry,
  score after the window from the venue's own history) is the pattern; reuse it for 1.2, 2.1 and 3.1 if they pass.
- **A late-entry column in the book.** For each row, the edge if entered one hour late, as a fraction of the edge at
  the signal: the standing check that the book stays free of speed races.
- **History accumulates only if the daily jobs run.** The chain, perps and Solana launchd templates are still not
  installed (needs the user).

## Verdicts of the studies sent out today

| study | idea | verdict | what it means for the book |
|---|---|---|---|
| `term_carry` | 4.2 DIY Ethena | **go for one coin**: HYPE spot as Hyperliquid portfolio-margin collateral, short the HYPE perp, +4.30% a year over the savings rate out of sample (t 5.68; both halves positive), because the same coin pays 9.6% on Hyperliquid and 4.5% on Binance. BTC/ETH on Hyperliquid: watch (t < 1 since 2025-11). Binance: no-go | new row `hl-hype-spot-perp-carry`, $5M, ~$200k/yr (pending: the book write was blocked, see below) |
| `term_carry` | 4.1 dated basis | **standby**: +2.4% to +5.4% a year over the savings rate out of sample, but a regime trade: no day in 2026 cleared +2pp | new row `dated-basis-cash-and-carry`, go = no, ~$35M when triggered |
| `term_carry` | 4.3 Boros | **no-go** as a carry: implied − realised +0.12% (t 1.27); the sign flips with the funding cycle; usable only as a rate lock | daily `boros snapshot` added to the perps pass |
| `term_carry` | 4.5 VRP | measured: BTC +8.0, ETH +5.3 vol points since 2021, shrinking to +0.9 / +3.5 in 2026, fat left tail | none |
| `fundamentals_factor` | 2.2 / 2.3 chain and protocol fundamentals | **no-go on both.** Chain flows: the chosen variant (4-week fee growth) made −5.9%/yr out of sample, no BH survivor among 34 variants. Protocol fee growth and fees/FDV worked in 2021–23 (IC 0.04–0.12) and have been zero since 2024. The chain-activity detectors, replayed day by day over five years (1,792 events), lose in all 16 variants: activity and price move together, so the reading arrives after the move. Watch: 4-week stablecoin-float growth (out-of-sample IC 0.041, t 2.81, but negative in sample and in both halves of 2026) | none; `chain_census.py` stablecoin-gap bug fixed |
| `governance_events` | 2.1 governance events labelled by the LLM | **no-go.** 2,522 proposals labelled against a rubric frozen (hashed) before any return was computed; VALUE_UP proposals were followed by +7.2% against the basket in 2021 – mid-2024 and +0.07% after; the pre-registered trade lost −0.94% a trade out of sample (t 0.36 over placebo). The labels are consistent (blind re-read kappa 0.95) and far better than keywords (kappa 0.09), but better labels do not rescue a dead effect; the Snapshot date is days late for the events that matter (forum posts lead) | none; next: date events by forum post |
| `queue_bids_ext` | 1.3 more queue bids + ether.fi payout check | **payout check passed**: over two years every ether.fi request of ≥ 0.01 eETH was paid exactly (40,890 claims), no fees, one invalidated request; the queue's median is 0.79 days (not 2.0); the instant route does not cap the discount. **One new asset clears: LBTC** (redeemable by anyone to a bitcoin address, ~6 days, pays the payout-day rate), $111k/yr at $10M on the cbBTC pools, needs a Coinbase account for the return leg. OETH, tBTC, osETH, mETH, ETHx and others: too small, one-event, permissioned or dead | weETH re-quoted **$170k → $194k/yr**; new row `lombard-lbtc-queue-bid` (both pending) |
| `listing_lifecycle` | 3.1 new-listing decay | **no entry; forward-test watch item.** The decay is real as a description (median new token −25% / −33% against seasoned alts at 30 / 60 days; funding takes about a tenth of the move), but the protocol's pick failed its test (listing-week t 1.01) and against the seasoned basket it earned +2.3%; 16% of test trades saw the coin double while held. Early basket-hedged entries held out of sample (t 2.89–3.17) but were not chosen | none; pre-registered: short each new core listing at the close of its 2nd UTC day, hold 30 days, long the seasoned basket, stop at +100% |
| `listing_lifecycle` | 1.2 delistings | **closed.** Binance's notice drift reversed (+15.0% → −3.5% an event), perp-vs-spot lost, and the funding study's "92% a year pre-delisting" spread was earned weeks before any notice in sub-$5k books (none survives at $10k) | erratum added to `funding_arb/findings.md` |
| `tradfi_perps` | 1.1 Binance TradFi × HIP-3 | **no-go**: the second perp removes ~95% of off-hours risk, but Binance longs pay their own funding (68.5% of Binance settlements are zero, no interest floor), and on liquid names what is left is below the savings rate; no commodity roll trade (each venue's funding pays its own roll) | the equity carry re-tests at +2.26% on capital (t 3.91) but sits in thin names: **re-quote $330k → $54–73k a year** (pending) |

## What the six tests taught, and what to test next

**The filter held.** Both survivors have a counterparty with a non-price motive: leveraged longs who pay twice as much
for the same coin on one venue (the HYPE carry), and holders who will not wait a week for a redemption queue (weETH,
LBTC). Every candidate that rested on information — on-chain fundamentals, governance proposals, activity surges — was
priced by the time it was public: each worked in 2021–23 and has been zero since 2024, which is what an edge that the
market learned looks like. Spreads that were large turned out to be the cost of capital (the TradFi pair) or to live in
books a few thousand dollars deep (delistings, new-listing squeezes).

**What that says about the remaining list.** Promote the candidates where someone is paid to bear a constraint, and
demote the information ones unless the information is genuinely hard to get:

| next | why now |
|---|---|
| 1.4 queue bids off Ethereum (HYPE LSTs with a 7-day unstake, sAVAX 15-day, Cosmos/Celestia 21-day) | the one family that has now survived twice; longer queues, fewer bidders |
| a combined ETH queue book (Lido, ether.fi, Kelp on one capital pool) | the payout check no longer limits the weETH bid; shared collateral does |
| 5.4 incentive-adjusted dollar yields (Merkl and protocol rewards, net of your own dilution) | fixed budgets, attention-limited; small rows, but many |
| 3.3 ve(3,3) epoch economics (Aerodrome/Velodrome) | bribers paying for votes is a non-price motive with a weekly calendar |
| 2.1 governance, dated by the forum post | the one information idea with a specific, testable reason it failed (the date) |
| HYPE carry forward tracking; Boros as its rate lock | the newest row; its kill criteria need a daily series on both venues |

**Pending, needs the user.** Five book writes (auto mode refused them as a shared-resource change): add
`hl-hype-spot-perp-carry` and `dated-basis-cash-and-carry`; replace `etherfi-weeth-queue-bid` and add
`lombard-lbtc-queue-bid`; re-quote `hip3-equity-funding-carry` to about $73k a year. Commands are in the ROADMAP's
2026-10-10 entry. And the daily launchd jobs, without which the forward ledgers only advance when a session is open.
