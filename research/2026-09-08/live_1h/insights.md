# What the whole book is worth

Ethereum mainnet, **2026-09-08 04:29 to 05:27 UTC**, blocks 25,930,251–25,930,550 (300 blocks)
[[verify: blocks]] [[verify: transactions]] [[verify: logs]], with head reads at 05:29. A short window, collected to close the loop rather than to study the hour: eleven detectors run in four
seconds, and six of the seven strategies in the book now re-price themselves from it.

## 1. Pendle, and the distinction that decides whether an implied yield is a trade

`detectors/fixed_vs_floating.py` discovers Pendle markets from the window's own `Swap` logs — the markets with live
flow, no hardcoded list and no API — reads each PT price through the PY oracle, and refuses to quote one whose
observation window `getOracleState` reports as unpopulated.

The classification is the point. A principal token's implied yield is a *term premium* only when the floating rate on
the same underlying is readable; otherwise it is the market's price of an issuer's credit, which this system has not
assessed. In this window:

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

## 2. The strategy book, sized

Six of seven re-price from detectors. Sorted by what each is worth per year at the capacity it actually supports:

| strategy | net APR | capacity | per year |
|---|---:|---:|---:|
| Sky savings rate over Aave USDS | 3.48% | $1,000,000,000 | $34,800,000 |
| Morpho USDT borrow vs Aave *(hand, stale)* | 0.91% | $24,000,000 | $218,400 |
| sUSDe cooldown redemption | 17.25% | $600,000 | $103,500 |
| USDG captive-flow v4 LP | 10.37% | $150,000 | $15,555 |
| PT-sUSDS fixed vs the savings rate | 0.64% | $1,000,000 | $6,400 |
| Aave USDtb supply | 2.37% | $227,400 | $5,389 |
| Compound v3 USDC over SparkLend | 0.34% | $1,400,000 | $4,760 |

**Excluding the savings rate — which is the benchmark, not an edge — the entire book is worth about $354,000 a year,
and $218,000 of that is a stale hand measurement from two days ago.** The verified, currently-re-priced part is
roughly $136,000, and $103,500 of *that* is one trade whose annualisation assumes a million dollars of sUSDe is
offered below NAV every single day.

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
of the opportunity is gone. The PT row is a modelling correction rather than a market move — and it required its own
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

The window aggregates are re-derived by `live_scan verify`. Everything in sections 1–3 comes from head reads and
contract calls at 05:29 UTC — no verify recipe re-derives a head read yet, so the entire rate and yield surface in
this note is a single reading. That remains the largest untagged surface in the system.
