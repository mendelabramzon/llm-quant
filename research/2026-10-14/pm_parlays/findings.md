# Parlays and combos: the house edge, and who collects it (2026-10-14)

**Verdict: no-go for the book, and `book_entries.json` is `[]`.**

Selling Kalshi combos as an outside quoter, with the product of the leg prices as fair value, fails the protocol:
- the rule chosen on the first half did not hold up on the second;
- the executable version earned nothing.

The parlay rent on Kalshi is real but thin per dollar at risk, and Kalshi's fees take more of it than the makers keep.

On Polymarket, the incumbent combo makers' rent is statistically real: +1.93% on $217M risked, daily HAC t 3.80. Quoting
there is open to any account, and makers pay no fee. But this study could not run the protocol on Polymarket, because it
lacks leg prices at entry. So Polymarket combos are the open thread.

Numbers are from `analysis.json` (key in brackets) and `scripts/pm_parlays.py`; tables are in `tables.md`.

## Mechanism and counterparty

The payer is the parlay buyer, paying for entertainment. A buyer requests a combo, makers answer with private quotes, and
the best price fills. The quoter needs a fair-value model and full collateral (1 − p per contract sold).

The late-entry test does not apply. Each request is a private auction lasting seconds, so no mispricing persists for a
later entrant to take. Speed matters only as a response deadline, not as a race for position. The test that replaces it
is the winner's curse: you fill only where your quote is below the incumbents'.

| | Kalshi | Polymarket |
|---|---|---|
| who may quote | any API member; no maker designation documented; the 150-quotes-a-second tier is self-serve | any account through the SDK |
| response deadline | 3 s to confirm | 400 ms |
| buyer pays | 0.07·C·p(1−p) | 0.05·p(1−p); 96.7% of 14,523 onchain matches matched it exactly |
| maker pays | 0.035·C·p(1−p) since 2026-08-20 (except uncorrelated NFL parlays) | nothing |
| makers | about 5 firms (Oddpool) | 192; the top 5 hold 42.7% (`polymarket.onchain`) |

## Kalshi

**Sample.** 348 one-minute windows, 2026-08-16 to 10-12: 2.76M trades and a hashed subsample of 52,770 combo trades.
"Pre-game" means traded before every leg's game started. In-play combos were excluded as latency trades.

**Scale.** Combos are 58.4% of Kalshi contracts (`kalshi_sample.combo_share_of_contracts`). Buyers pay $41.0M a day in
combo premium (`kalshi_rent_per_day.all`).

**Margin over the legs.** Pre-game combos trade 9.5% above the product of the leg midpoints
(`kalshi_margin.all_pregame_priced`: n 22,932; premium-weighted 9.52%; 68% above the product of the leg asks).
- Cross-game combos: 5.1% overall, rising from 1.2% at 2 legs to 36% at 11+ (`kalshi_margin.struct.cross`,
  `kalshi_margin.cross_by_legs`).
- Same-game combos: 16.4% above, but correlated legs make that number meaningless as a margin. Reported as unpriced.

**Who gets the pre-game rent, per day** (`kalshi_rent_per_day.pregame`):

| | $ a day |
|---|---:|
| buyer premium | $20.5M |
| model margin | $1.63M |
| buyer fees | $1.06M |
| maker fees | $0.46M |
| makers' net | $1.16M |
| makers' capital at risk | $594M |

The makers' realized edge is 0.19% per dollar risked, with a t of 1.04 clustered by game
(`kalshi_maker_pnl.cls.pregame`).

**Protocol** (`protocol.choose_then_test`):
- 12 pre-registered variants: cross-game or same-game × margin m ∈ {all, 0, 5, 10, 20, 40%}.
- The in-sample pick was same-game at m = 0.20, with a Sharpe of 5.61. Out of sample its HAC t was 1.55, it ranked 6th of
  12, and no variant survived the false-discovery test.

**The executable version** quotes fair × 1.2 and wins only below the incumbent's price. It earned −4.9% a year, t −0.03,
payout z 0.25 (`implementation`).

**Winner's curse** (`winners_curse`):
- Same-game at m = 0 wins 84% of trades, at a model edge of +0.0005 a contract, but realizes −0.0049. Correlation is the
  curse.
- Cross-game at m = 0.05 wins 29% and realizes +0.0067, against a model edge of +0.0011.

**Regime.** Every cross-game variant lost in the first half and won in the second; same-game did the reverse
(`variant_descriptive`). Only cross-game at m = 0.05 has an out-of-sample payout z of 2 or more (2.04), and its in-sample
t was −0.88. It is a forward-test candidate, not a finding.

## Polymarket incumbents

The data covers 25 makers, who account for 84.1% of onchain maker dollars: 571,696 resolved positions since June
(`polymarket.maker_positions`).
- $217M risked for +$4.19M: 1.93% on cost and 8.8% of the premium sold. The daily HAC t over 126 days is 3.80.
- Per-maker returns run from −0.43% to +5.64%. Eight of the 25 earn 0.5% or less, and six earn above 2%.
- By month: June 3.8%, July 1.75%, **August 0.03%**, September 1.7%, October to date 3.75% (`by_month`).
- Positions resolve within hours (the first record opened at 07:10 and resolved at 08:02). The return is earned on
  capital that turns over many times a year, so the yearly yield on capital is far above 1.93%. The top 25 net about
  $33k a day (`polymarket.maker_positions.daily`).
- The pre-game margin over the legs' order-book midpoints is 8.4% (n = 257, `polymarket.fair_at_entry`). The
  fair-value sample is small: equal-weighted, makers made −2.7% ± 4.6% on it.
- Flow: $538k a day of combo buys and $16.7k a day of fees. Kalshi's combo market is about 76× larger.

## Capacity

None is stated, because nothing passed. Scaled to the whole flow, the executable version's point estimate is
+$114M a year, with a 95% interval of −$818M to +$1,045M (`capacity.implementation_whole_flow`). That is noise
multiplied by a ~1,700× scale-up, not a capacity.

## Variants

There are 12 variants in the family, plus the chosen variant's executable version and 10 own-quote counterparts reported
descriptively: 23 evaluated in all, none dropped. The payout-z gate was added after a partial run; it only tightens the
go rule.

## Errors found and fixed

1. **Empty book sides passed as leg prices.** Kalshi candles show an empty side as bid 0 or ask 0.999. Legs wider than
   10¢ are now unpriced.
2. **A lottery short made a daily HAC t of 6.5.** At m = 0.40 the quote won only 1-in-1000 shots, with 0.2 payouts
   expected in the sample. A payout-z and expected-payouts gate was added.
3. **Busy windows were mostly in-play trades.** Kalshi's game start times now classify pre-game exactly.
4. **The Polygon block-time estimate was wrong.** Blocks are 1.5 s, not 2 s; the first window landed 11 days off. It was
   replaced by a search, with a fallback for blocks Infura refuses.
5. **Six parallel Kalshi collectors were rate-limited.** They were cut to four and the 3 lost windows refetched.
6. **Two positions drove the Polymarket fair-value result.** The size-weighted figure was −19.6% for makers;
   equal-weighted it is −2.7% ± 4.6%.

## Kill criteria and what to collect next

- **Kalshi:** reopen only if the cross-game margin (5.1%) beats the maker fee's share of premium (about 3%) by 3 points
  for a month, and a pre-registered rule clears payout z ≥ 2 in both halves.
- **Polymarket:** treat the rent as gone if the top makers' return on cost stays under 1% for two months. August was
  0.03%.
- **Next:**
  - leg midpoints at entry for about 20k Polymarket combo fills, to run the protocol where makers pay no fee;
  - Kalshi's authenticated request feed (unfilled requests and competing quotes), for the true winner's curse;
  - Kalshi's historical tier (September 2025 to August 2026). Cross-game at m = 0.05 has a full-sample payout z of 1.77;
    about 4× the data would settle it.

## Coordinator's check

Polymarket's pooled maker result was recomputed from `raw/polymarket/positions/*.json.gz` (25 makers, independently
of the script). P&L is payout minus entry cost minus fees, over resolved positions:

| | recomputed | reported |
|---|---:|---:|
| positions | 571,696 | 571,696 |
| cost | $217,034,015 | $217.02M |
| P&L | $4,177,164 | $4.19M |
| return on cost | 1.925% | 1.930% |
| per-maker range | −0.434% to +5.62% | −0.43% to +5.64% |
| makers at or below 0.5% / above 2% | 8 / 6 | 8 / 6 |

The $11k gap is entry fees. `research/2026-10-14/pm_combos_maker` traced it to $11,188.64 of fees on positions where
the maker held YES; this recount charges them and the script did not. It does not change the conclusion. The
month-by-month series is reported here because it qualifies the headline: the rent nearly vanished in August.

The same study found that this study's `polymarket.maker_positions.by_legs` table overwrote its own buckets: it shows
33,007 of 81,228 positions in "5-6", 7,268 of 61,183 in "7-10", and 1 of 17,202 in "11+". Use
`research/2026-10-14/pm_combos_maker/analysis.json` for leg-count splits.

## Files

- `scripts/pm_parlays.py`
- `scripts/test_pm_parlays.py` (21 tests pass)
- in this folder: `analysis.json`, `tables.md`, `manifest.json`, `book_entries.json` (`[]`)
- `raw/` (181 MB) and the logs, git-ignored
