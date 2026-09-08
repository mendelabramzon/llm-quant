# What the whole book is worth

Ethereum mainnet, **2026-09-08 04:29 to 05:27 UTC**, blocks 25,930,251–25,930,550 (300 blocks)
[[verify: blocks]] [[verify: transactions]] [[verify: logs]], with head reads at 05:29. A short window, collected to close the loop rather than to study the hour: twelve detectors run in
about five seconds, and **all seven** strategies in the book now re-price themselves from it — none is a memory.

## 1. Pendle, and the distinction that decides whether an implied yield is a trade

`detectors/fixed_vs_floating.py` discovers Pendle markets from the window's own `Swap` logs — the markets with live
flow, no hardcoded list and no API — reads each PT price through the PY oracle, and refuses to quote one whose
observation window `getOracleState` reports as unpopulated.

The classification is the point. A principal token's implied yield is a *term premium* only when the floating rate on
the same underlying is readable; otherwise it is the market's price of an issuer's credit, which this system has not
assessed. Each implied yield below is re-derived from its PT price and maturity [[verify: head-pendle-apy]]. In this
window:

| PT | implied | comparison | classification |
|---|---:|---|---|
| PT-sUSDS-26NOV2026 | 4.89% | Sky savings rate 3.60% | **term premium**, +129bp |
| PT-reUSD-10DEC2026 | 10.98% | — | credit spread |
| PT-trUSD-26NOV2026 | 10.07% | — | credit spread |

The eight markets that traded in the earlier 21:27–23:27 window were *all* credit spreads — implied yields of 6% to
23% with no comparable floating rate anywhere. Ranking Pendle by implied yield alone puts those at the top of a book;
the classifier is what keeps them out of it.

The matcher had to be fixed to do that honestly. Its first version matched underlyings by substring, so `USDE` inside
`SRUSDE` classified PT-srUSDe as a term premium on Ethena credit — a different issuer's product quoted as a rate view.
It now parses the asset segment of `PT-<asset>-<date>` and matches exactly. That is the error the detector exists to
prevent, committed by its own matcher.

## 2. The strategy book, sized — all seven re-pricing themselves

Every rate below is a detector's reading of the head state, and each of those readings satisfies its protocol's own
identity [[verify: head-supply-identity]] [[verify: head-irm-identity]] [[verify: head-morpho-identity]]
[[verify: head-pendle-apy]] [[verify: head-utilisation]].

| strategy | net APR | capacity | per year | its own detector |
|---|---:|---:|---:|---|
| Sky savings rate over Aave USDS | 3.48% | $1,000,000,000 | $34,800,000 | go |
| sUSDe cooldown redemption | 17.25% | $600,000 | $103,500 | **declines** |
| Morpho USDT borrow vs Aave | 1.46% | $6,353,460 | $92,761 | go |
| USDG captive-flow v4 LP | 10.37% | $150,000 | $15,555 | go |
| PT-sUSDS fixed vs the savings rate | 0.64% | $1,000,000 | $6,400 | go |
| Compound v3 USDC over SparkLend | 0.39% | $1,400,000 | $5,460 | go |
| Aave USDtb supply | 2.39% | $227,400 | $5,435 | go |

Excluding the savings rate — the benchmark, not an edge — the book totals about **$229,000 a year**, of which
**$125,600 survives its own detectors' verdicts**. Nothing here is stale: every row was re-priced from this window or
the one before it.

The declined row is the largest edge in the book, and it was declined by a check written after the table above was
first drafted. `nav_discount` now compares a discount against the dispersion of the prices it was averaged from. The
sUSDe reading is 7.4bp to NAV, 4.7bp after the round trip — measured across a window whose p10-to-p90 spread was
**5.4bp**. Significance 0.87: the edge is *inside* the noise of where the asset traded, so it is not distinguishable
from a sampling artifact, and the detector says so rather than quoting 17% a year.

That test is meaningful for a dollar claim, whose NAV barely moves inside a window, and deliberately conservative for
an ETH-denominated one, where the same spread also contains ETH's own move. Both cases are labelled in the evidence.

The last hand number to fall was the largest. "Borrow USDT on Morpho rather than Aave" was quoted at 91bp on $24M —
$218,400 a year — from a single afternoon two days ago. Measured: **1.46pp on $6.35M, $92,761**. The rate gap is
*wider* than the hand note said and the capacity is a quarter of it, because $24M was the vault's size and $6.35M is
what is actually withdrawable. The detector also names what the hand note omitted: the cheapest Morpho USDT market
lends against **sUSDS at 96.5% LLTV**, so the rate is only available to a borrower who can post that collateral.

On an isolated-market venue that distinction is the whole thing. A pooled reserve lets any listed collateral reach any
rate; a Morpho market is a rate *for one collateral*, and quoting it without saying which is quoting a price nobody
can necessarily trade. Every Morpho rate above satisfies the protocol's own supplier identity
[[verify: head-morpho-identity]] and every utilisation is re-derived from the balances [[verify: head-utilisation]].

That is the honest state of the mainnet dollar opportunity set as this system currently measures it. It is not a
disappointing result; it is the result. An efficient market is supposed to look like this, and the value of the loop
is that the number is now derived rather than asserted — every row has legs `economics.py` priced, a capacity that
came from a rate curve or a traded volume rather than a pool balance, and a kill criterion.

## 3. Two strategies decayed inside the session, and the book caught both

| strategy | earlier today | now | why |
|---|---:|---:|---|
| Compound v3 USDC over SparkLend | 1.46% | **0.34%** | utilisation drifted 90.77% → 90.30% against a kink at exactly 90.0%; best size fell $1.4M → $405k |
| PT-sUSDS fixed vs the savings rate | 1.37% *(hand, 09-06)* | **0.64%** | the raw gap narrowed 137bp → 129bp, and the hand study did not net Pendle's entry impact |

The Compound row is the kink analysis playing out in hours: 0.47 percentage points of utilisation, and three quarters
of the opportunity is gone. The read sits on the curve sampled at the same block [[verify: head-compound-curve]]. The PT row is a modelling correction rather than a market move — and it required its own
correction first. Charging a Pendle purchase the constant-product impact overstates it by about two orders of
magnitude, because Pendle's AMM is a rate curve; the detector now applies an amplification of 50, anchored to the one
observation this repo has (a $1M order into a $3.5M pool taking "a real part of" 137bp), and says so. Replacing that
estimate with a measured quote-by-size read from the Pendle router is the obvious next improvement.

## 4. A gap in the provenance gate, found by falling into it

`head_state.json` is an input to `analyze` — the entire window is priced from it — and it was not fingerprinted. So
re-running `head` on an old window silently re-prices every dollar figure in an analysis that is not re-run, with the
labels and the token table both unchanged, meaning no existing gate could see it. It happened here: the 21:27–23:27
window ended up carrying a head read from 05:21 the next morning.

Two fixes. `head` now refuses to read current state for a window collected long ago, because that mixes two
timeframes and nothing downstream would say so:

```
refusing: the head is 5007 blocks past this window (collected to 25925535, head 25930542, window 1491 blocks).
Reading state now would price a past window at present rates.
```

And `head` is now a provenance gate alongside labels, tokens and blocks, so an analysis whose head state moved
underneath it reports as stale before a single number is compared.

## 5. Everything else

- **JIT liquidity took 15.8% of pool fees in this window** ($26 of $168), against 0.06%–0.29% in the three previous
  ones. The absolute numbers are trivial and the share is not; it is the first window in which the per-window JIT hit
  cleared its 10% threshold, which is exactly the change the detector was written to notice.
- The dust-spam and airdrop campaigns continue at the same operators and the same cadence: 0xbeef007e to 5,666
  recipients, 0.0003 USDT to 2,568.
- `nav_discount` found nothing: no redeemable claim traded away from NAV by more than its round-trip cost in this
  hour, which is why the sUSDe strategy shows its last seen rate in brackets rather than a fresh one.

## What is checked, and what is not

The window aggregates are re-derived by `live_scan verify` from the raw blocks through a second code path. The rate
and yield surface — sections 1 to 3 — comes from head reads, and there is no second RPC path to read those through.
What there is instead, added after this note was first written, is a set of **identity checks**: each protocol
publishes relationships between the fields it reports, and re-deriving one from the others tests the whole decode
against the chain's own arithmetic. On this window, 182 individual identities pass:

| id | checked | identity |
|---|---:|---|
| `head-utilisation` | 50 | utilisation equals borrowed / supplied |
| `head-supply-identity` | 32 | supply APR equals borrow APR × utilisation × (1 − reserve factor) |
| `head-irm-identity` | 32 | borrow APR equals the reserve IRM evaluated at its utilisation |
| `head-compound-curve` | 3 | the Compound supply read lies on the curve sampled at the same block |
| `head-morpho-identity` | 60 | Morpho supply APY equals borrow APY × utilisation × (1 − fee) |
| `head-pendle-apy` | 5 | the Pendle implied yield is (1/price)^(365/days) − 1 |

They are not a second opinion on whether a rate is *correct* — the chain is the only source for that. They test that
the decode is right, which is where this session's two rate bugs actually lived. Setting Aave's USDC supply APR to
its borrow value, the exact shape of the earlier series bug, fails `head-supply-identity` immediately with the venue,
asset, utilisation and reserve factor named.

The peg prices behind `nav_discount` are now checked in the way that matters for the claim built on them: not by
re-deriving the average, but by asking whether the gap being called a discount is larger than the spread of the
prices it was averaged from. What still carries no check at all is the NAV side — the exchange rates in
`head_state.rates` are read from one contract method each, with no second view to disagree with them.
