# Rent map — where the money paid by non-price-motivated agents goes, 2026-10-10

The repo's survivors are rents. Someone with a non-price motive pays: for leverage on one venue, for not waiting in a
queue, for points. Whoever supplies the scarce resource that agent needs collects. This study sizes those payments
top-down, to say where the loop should look and how large each family can get.

**Conventions.** The fair rate is SSR 3.80% for dollars, 2.37% (staking) for ETH, and 0 for BTC and other coins. A
run-rate is the last 30 days × 365/30 unless stated.

**Headline.** Agents with a non-price motive pay about **$12.67B a year** into the pools below. That total leaves out
entertainment platforms, manager fees and energy rolls.

- **$2.21B of it is above a fair rate** (band $1.95–2.72B).
- **Patient capital without speed could plausibly collect $2.8–17.5M a year** of that. The book today is about $1.1M,
  so the ceiling is 3–16× the book.
- **Most of the ceiling sits in pools the repo has barely tested:** incentive budgets, perp LP vaults and metal-perp
  funding.
- **The largest above-fair pool is Hyperliquid funding ($850M).** It is limited by access to HL spot inventory, not by
  speed.

## The map (largest first; `analysis.json → map`)

| pool | size $/yr | above fair (band) | payer: motive | collector today | scarce resource | how contestable | repo evidence | accessible $/yr |
|---|---|---|---|---|---|---|---|---|
| Entertainment platforms (launchpads $2.92B, prediction markets $1.40B, trading apps $1.20B) | $6.65B (365d: $3.12B) | n/a | gamblers: entertainment | the platforms | the platform itself | owned | Polymarket studies no-go | 0 |
| DEX LP fees, supply side | $4.36B (365d: $2.49B) | not estimated | memecoin swappers (PumpSwap $1.24B, Uniswap v4 $1.10B, Meteora DLMM $0.56B); on major pairs, arbitrageurs | LPs (much memecoin liquidity is seeded by the protocol and locked) | decaying inventory, or beating LVR | racing | JIT retired; captive-flow LP is the exception | ~0 |
| CEX crypto funding (Binance top 100, Bybit and OKX top 30 each) | $2.24B paid by longs | $381M ($381–548M) | leveraged longs: leverage | basis desks, market makers, Ethena | nothing beyond capital (BTC/ETH funding 4.1–5.0%) | high | DIY Ethena no-go; altcoin excess lives in thin books | $0–0.3M |
| Perp-venue fees | $1.88B | LP vaults above SSR: $49M ($25–49M) | traders: leverage, convenience | HYPE buybacks (HL fees $1.05B), front-ends, LP vaults | tolerance for trader PnL and directional exposure | open to any depositor, pro rata | `house_vaults` running | $0.2–2.5M |
| Lending and CDP interest | $1.66B (365d: $1.95B) | $311M ($247–413M) | loopers, market makers: leverage on a carry | suppliers at about SSR; protocols (revenue $316M) | nothing beyond dollars | high | 2 of 27 reserves beat SSR | $0.1–0.4M |
| Hyperliquid main-dex crypto funding | $1.37B | $850M ($710–850M) | HL longs: self-custodial leverage; they pay 9.07% / 9.77% on BTC/ETH against 4.37% / 4.41% on Binance | shorts with capital on two venues; HYPE holders | HL spot as portfolio-margin collateral | medium | HYPE carry go; BTC/ETH on watch | $0.2–1.3M |
| HIP-3 and Binance TradFi equity funding | $552M | $98M ($98–184M) | 24/7 equity leverage | market makers hedging at brokers | a broker account; overnight gap risk | medium | thin go, re-quoted to $54–73k | $0.04–0.18M |
| Incentive budgets | $354M (up to $504M) | the same | issuers buying deposits: marketing | depositors, pro rata | attention, eligibility, tolerance for issuer credit | easy for capital, hard for attention | `incentive_yields` running | $1.8–10.1M |
| Metal perps (gold, silver; 4 venues) | $190M | $113M ($91–113M) | 24/7 leveraged metal exposure | unknown | a tokenized spot leg (PAXG/XAUT); venue access | low to medium | only the perp-vs-perp pair was tested | $0.4–1.4M |
| Pendle YT premium | $43M net (4.38% on $986M of YT) | $43M | YT buyers: points | PT holders and loopers | duration | medium | PT switch go ($216k) | $0.1–0.5M |
| Queue impatience | $10M | $7.6M ($0.8–9.8M) | holders of queued claims: impatience | LPs, bots, queue bidders | capital that can sit locked | medium | queue book $409,889/yr at $15M | $0.02–1.0M |

Left out of the table because they are not strategies:

- **Energy perps ($432M of roll flow).** Funding pays the roll, as `roll_carry` showed.
- **Manager and curator take ($123M).** Not a trade.

For scale only, excluded from the total:

- stablecoin issuers $9.32B on $312B of supply;
- staking $2.54B;
- chain fees $1.43B;
- RWA pass-through yield $0.88B;
- MEV and block builders $0.37B;
- liquidation penalties: not sized.

**Facts behind the biggest rows:**

- **HL funding is set by formula.** 71.6% of open-interest-weighted hours on HL's main dex settled at exactly 0.00125% an
  hour, the formula's interest rate (10.95% a year). So HL's above-fair funding is a venue parameter, not a market
  premium. It persists because collecting it needs HL-native spot or capital on two venues, and `funding_arb` priced
  two-venue capital at about the spread.
- **Lending is a dollar market.** Stablecoins are 85% of measured interest: Aave charges 4.64%, Morpho 4.77%. ETH
  lenders earn 1.92%, below the 2.37% staking yield, so their rent is negative.
- **Incentives are mostly dollar campaigns.** 70% go to stablecoin deposits. Merkl's lending budgets alone are $230M a
  year. The largest campaigns are Ethena's Aave loop programs ($26.4M and $14.6M) and Morpho vaults for USDe, USDG
  (Robinhood users only), RLUSD and PYUSD ($12–19M each).
- **Who collects funding.** Ethena's fees ($276M) equal 6.1% of the $4.55B longs pay on the four venues, and that figure
  also includes its staking and reserve yield. HLP is $181M earning 4.0%.

## Under-contested pools, ranked (`ranking`)

Score = mid above-fair × mid accessible share × (1 − repo coverage). The accessible shares are judgement anchored to
book quotes; the reasoning is in `NOTES`.

1. **Incentive budgets on dollar deposits** ($3.8M).
   - Test: a daily ledger of every live campaign over $1M a year, from Merkl's reward and APR history plus DefiLlama's
     reward APY. Simulate a $1–5M entry including our own dilution, selling the reward, and eligibility costs (e.g. the
     borrow cost of a required loop).
   - Kill if the median campaign nets less than SSR + 1%.
   - Status: `incentive_yields` is running.
2. **Perp LP vaults, hedged** ($0.8M).
   - JLP earns a 9.9% fee APR on $773M before trader PnL.
   - Kill if the hedged excess is under 2% a year or the worst month is below −3%.
   - Status: `house_vaults` is running.
3. **Tokenized-gold carry** ($0.7M).
   - Gold and silver perps pay 6.3–14.7% a year on $2.05B of open interest. The xyz GOLD and SILVER oracles follow spot,
     and 98% of HL gold hours paid longs to shorts.
   - Test: short each venue's metal perp against PAXG/XAUT.
   - Status: sent to `gold_carry` the same day.
4. **HL BTC/ETH carry at the formula rate** ($0.1M; already a watch item). Run a forward ledger with UBTC as
   portfolio-margin collateral. Kill if the 90-day excess falls below 2%.
5. **Queues off Ethereum.** Pairs against the native coin trade $5.0M a day (JitoSOL, kHYPE), worth at most $0.5–2.3M a
   year gross. Status: `queue_bids_alt` is running.

Unsized and worth chasing for data: ve(3,3) bribes (`ve_carry` running), prediction-market LP reward programs, and
Aerodrome emissions to concentrated-liquidity pools.

## Data and method

**Funding.**

- Hyperliquid: live `metaAndAssetCtxs` for the main dex and 10 HIP-3 dexes. Only xyz, io, para and mkts still have open
  interest; flx, vntl, hyna, km, cash and abcd are fully delisted. Rates come from the repo's hourly store (30 and 90
  days).
- Binance: daily `openInterestHist` × every funding settlement over 30 days (realised), plus 90-day rates.
- Bybit and OKX: open interest now × 30 days of settlements, with the tail extrapolated (×1.27 and ×1.19).

**Fees and incentives.**

- DefiLlama overviews (fees, revenue, supply side), with each protocol assigned to exactly one pool.
- Incentives = Σ tvlUsd × apyReward, minus DefiLlama-flagged outliers ($2.17B of absurd concentrated-liquidity APRs),
  anything over 300%, and pass-through vaults ($46M).

**DEX LVR.** On the 40 largest volatile major pairs, fees are $91.9M against LVR of $28.9M (full range) to $92.9M (4×
range). LPs therefore keep between 69% and −1% of fees.

**Lending.** The Aave API and Morpho API give the split by asset class.

**Pendle.** YT `totalSupply()` read on chain for 85 markets × (implied − trailing 30-day realised yield).

**Queues.** The repo's histories plus `queue_book`.

## Uncertainty

- **Windows.** 30-day and 365-day run-rates differ by about 2× for DEX and entertainment (a memecoin boom) and agree
  within 20% for lending and perps.
- **Incentives.** The band is $354–504M: the low end is DefiLlama alone, the high end adds Merkl and flagged pools under
  50% APR.
- **Lending above-fair share.** 14.9% measured on Aave, 24.8% on Morpho.
- **Queues are regime-dependent.** The last 13 weeks run at $0.9M a year against $8.9M over 210 days.
- **Accessible shares** are judgement.
- **Venues not covered:** Bitget, Gate, Deribit, Aster, Lighter.

## Checks

- **HL funding.** Realised flow (open interest interpolated across four snapshots × 31.3 days of settled hours) is
  $1.18B a year. Current open interest × the same hours gives $1.30B. Ratio 0.90.
- **Aave.** Aave's own API (borrowed × APR now) gives $428.4M a year; DefiLlama's aave-v3 fees over 30 days give
  $450.9M. Ratio 1.05.
- **Incentives.** Merkl's own API gives $267.0M against DefiLlama's $353.5M. For Morpho they agree ($139M against
  $126M). DefiLlama misses most of Aave's Merkl programs ($83M against $14M).
- **HL fees.** DefiLlama's fees divided by the venue's own volume give 8.0bp, inside the expected 2–12bp.
- **One failure.** DefiLlama's open interest for HL's main dex is 0.64 of what the venue reports, while xyz matches at
  1.00. The venue's numbers are used.

## Errors found (all fixed)

1. pump.fun Mobile App and Bankr ($149M) had landed in perp fees. Moved to entertainment.
2. World Liberty's "Lending" fees ($148M) are USD1 reserve yield, not borrower interest. Moved to stablecoin issuers.
3. Metal perps on Bybit and OKX, and PAXG on HL and Binance, were counted twice: once in crypto funding and its tail
   extrapolation, once in the metals row. The classes are now separate.
4. The LP-vault above-fair figure first included 144–250% APRs from tiny or mis-measured TVLs. Filtering to TVL ≥ $20M
   and APR ≤ 100% cut it from $120M to $49M.
5. DefiLlama's daily charts include today's partial day. Windows now end yesterday.
6. The LVR comparison included pools with no fee reading. Excluded.
7. One test fixture had an odd number of returns. The test was fixed, not the code.

**API gaps.** `poolsBorrow` and `overview/derivatives` are paid (HTTP 402). Bribe data is empty. HL serves no
open-interest history. Ethena's hedge venues were not read. Supply of tokenized gold is unknown.

## Coordinator's check

Recomputed from a separate DefiLlama `/pools` snapshot taken about four hours earlier, without the worker's code:
Σ tvlUsd × apyReward/100 over 1,385 rewarded pools, excluding DefiLlama outliers and APRs above 300%, gives **$398M a
year, 67% to stablecoin pools**. The worker also removed $46M of pass-through vaults: $398M − $46M ≈ $352M against its
$353.5M, and 67% against its 70%. Consistent.

Files: `scripts/rent_map.py`, `scripts/test_rent_map.py` (65 tests), `analysis.json`, `tables.md`, `manifest.json`,
`raw/` (515 files, 8.8 MB).
