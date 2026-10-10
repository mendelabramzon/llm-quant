# Being the house: perp-venue liquidity vaults, hedged, against the savings rate — 2026-10-10

On a perp venue the liquidity vault is the traders' counterparty. It earns fees, spreads, liquidation penalties and
traders' net losses, and pays their net wins. Its takers have non-price motives: retail leverage, and points farming that
churns volume. The question is whether any venue's vault, with its market exposure hedged, beats the savings rate out of
sample, and how much a new depositor can add.

## Answer

**Two vaults pass: one is small, the other carries hedge-model risk. HLP, the flagship, fails.**

- **GMX v2 GM SOL/USD [SOL-USDC] on Arbitrum, hedged with a SOL short: go, small.**
  - Test half: +10.8% a year over the savings rate (Newey–West t 2.62; BH-adjusted p 0.048).
  - Re-measured without selection: +9.1% to +10.9%.
  - The pool's own accounting explains it: 11.4% fees plus 4.9% traders' net losses, against a measured hedged yield of
    18.0%.
  - The pool holds only $4.9M and its income dilutes. A $2M deposit earns about +5.2%, roughly $103k a year.
- **JLP (Jupiter perps), hedged with SOL/ETH/BTC shorts: go, at a conservative quote.**
  - Test half: +8.3% (t 3.80) with the chosen 60-day hedge. Re-measured, it falls to +2.6% to +6.6%.
  - The hedged return is the LPs' 75% fee share. That was 13.9% a year in the test half and is 8.5% now, down from 45%
    (2024), 19% (2025) and 11% (2026).
  - Quoted at +2.5% on $10M, about $248k a year. The first kill gate is a live forward test of the net-delta hedge built
    from jlp-info.
- **HLP: no-go.** Its income is liquidation windfalls.
  - The liquidator child vaults made $74.7M of HLP's $138.6M; the market-making children net about $0.
  - Test half: +6.3% (t 1.25), with 67% of it from one 14-day window (the 10 Oct 2025 cascade).
  - Trailing year: +1.7% over the savings rate. Its dollar income does not grow with deposits.
- **Gains gUSDC: no-go.**
  - On data through December 2025 it read +5.5% (t 5.78).
  - The full test half reads +4.2% always on (t 0.88), with a 12.6% drawdown. Traders' open profits reached 11% of the
    vault on 21 Sep 2026, and the share price fell 7.4% that day.
- **Lighter LLP: no-go.** +48.5% in its launch half, then +3.2% (t 0.99).
- **Watch:** GM BTC-USDC and GLV BTC-USDC.

**Who pays.**

- Retail leverage, through fees, is the durable payer.
- Traders' net P&L against the house changes sign and arrives in jumps. They won 5.4% a year from GM ETH-USDC, lost 4.9%
  a year to GM SOL-USDC, and took gUSDC down to 87% collateralisation.
- Liquidation income (HLP) depends on crashes.

## Verdicts

| vault | choose half: excess (t) | test half: excess (t) | max DD / worst week / best-1% share | TVL / room at +2pp | verdict |
|---|---|---|---|---|---|
| GM SOL-USDC | +21.1% (3.78) | **+10.8% (2.62)**; re-measured +9.1…+10.9% | 3.7% / −3.5% / 34% | $4.9M / $5.5M | **go**, $2M |
| JLP | +36.9% (3.84) | **+8.3% (3.80)**; re-measured +2.6…+6.6% | 2.5% / −2.2% / 50% | $900M / not binding | **go**, +2.5% on $10M |
| GM BTC-USDC | +9.6% (3.99) | +4.3% (2.03); BH p 0.16 | 2.8% / −1.7% / 52% | $58.6M / $7.5M | watch |
| GLV BTC-USDC | +6.8% (2.26) | +5.0% (1.80) | 2.5% / −1.2% / 45% | $12.4M / $4.7M | watch |
| HLP | +40.2% (3.46) | +6.3% (1.25) | 3.1% / −2.0% / 67% | $181M / none | no-go |
| gUSDC (Arbitrum) | +4.2% (4.84) | −6.7% (−0.96) chosen rule; +4.2% (0.88) always on | 12.7% / −7.4% in a day | $4.1M / none | no-go |
| Lighter LLP | +48.5% (3.24) | +3.2% (0.99) | 3.3% / −1.7% / 76% | $83M / none | no-go |
| GM ETH-USDC | +12.7% (4.80) | +1.8% (0.55) | 4.2% / −2.8% | $45M | no-go |
| GM ETH-ETH | +8.3% (2.21) | +2.2% (1.09) | 1.2% / −1.0% | $17M | no-go |
| GM BTC-BTC | +3.7% (1.88) | −0.9% (−0.67) | 2.4% / −0.6% | $9M | no-go |
| GLV ETH-USDC | +9.8% (2.76) | +0.1% (0.03) | 5.5% / −1.8% | $14M | no-go |
| dYdX MegaVault | — | 90 days only: +7.8% raw | — | $1.8M | no-go (size) |

Excess is the hedged return on capital minus the savings rate paid that year. Capital is the vault plus one third of the
short notional. Every test half ends 2026-10-10.

## Data and method

**Sources.**

- **HLP:** `vaultDetails` for the parent and 7 child vaults.
  - The public API has no daily history. The allTime grid has 100 points, 7–14 days apart; the month grid (~10 h) covers
    only 30 days.
  - Returns are flow-adjusted by modified Dietz.
- **JLP:** DefiLlama daily price, checked against CoinGecko and jlp-info; DefiLlama fees and TVL.
- **GMX:** daily GM/GLV price snapshots from the GMX subgraph, plus its fee APR, trader-P&L APR and pool value.
- **Gains:** `shareToAssetsPrice` at a daily Arbitrum block (Infura archive).
- **LLP:** pool value divided by pool shares, from the venue's own ledger.
- **Hedges:** Binance USDT perps (1h closes and funding).

**Costs.**

- 5bp per hedge trade, with a 10% rebalance band.
- Margin of one third of the short notional, held idle.
- Vault round trips: JLP 0.2%, GM/GLV 0.12% (assumed fee levels), others 0.

**Protocol.**

- Each vault has 9–12 pre-committed variants: four hedges (none, in-sample beta, trailing 60-day beta, composition)
  crossed with three rules (always on, on when trailing-30-day excess > 0, > 2pp). The plan is hashed in analysis.json.
- The variant is chosen by Sharpe on each vault's first half and tested once on the second.
- Statistics: Newey–West t with 30-day lags, block bootstrap, deflated Sharpe, and Benjamini–Hochberg across the 11
  vaults.
- A "go" needs all of: at least +2pp, t ≥ 2, survival under BH, at least $1M of room, and every robustness
  re-measurement at least +2pp.

## Results

**GM SOL-USDC.**

- Chosen variant: in-sample beta of 0.45 SOL, always on.
- Bootstrap interval +2.5% to +18.5%; deflated Sharpe 0.998; 2026 alone +10.1%.
- Data checks: the subgraph price matches pool value / supply within 0.6%, and the lagged-SOL beta is insignificant
  (t 0.74), so the price is not stale.

**JLP.**

- The 60-day hedge (deflated Sharpe 0.959) ranked first of 12 variants in the test, but the result is fragile:
  - a 120-day window reads +2.7% (t 1.04);
  - weekly resampling reads +2.6% (t 0.94);
  - over the last year, CoinGecko prices give +3.3% where DefiLlama gives +6.6%.
- The steadier evidence:
  - the two price sources agree when matched by timestamp (daily correlation 0.91);
  - both give a market-neutral alpha of 10.6–11.2% over the last year (R² 0.96);
  - fees explain the hedged yield (13.9% against 15.3%).
- Fees are now 8.5% of AUM (the venue states 8.0%). That is about +3% over SSR if traders net zero.

**HLP.**

- Betas run −0.05 to +0.03, so hedging changes nothing.
- Without 1–15 Oct 2025 (+7.7% in 14 days), the test half earns +2.1%.
- The coarse grid blurs named incidents: the ETH-whale week −0.9%, the JELLY fortnight +0.5%, the POPCAT fortnight −0.8%.
- The last 30 days ran at +4.0% a year.

**LLP.**

- The venue's own daily-return series says +7.3% (t 3.55).
- It matches the ledger within 0.1% a month until August 2026, then diverges by 3.1pp. On 21, 22 and 29 August the
  ledger shows trading losses of $0.67M, $0.44M and $0.84M; the official series shows gains.
- Unreconciled, so no-go.

## Capacity

- **Dilution:** income is assumed fixed in dollars, so a deposit X dilutes the yield by T/(T+X).
  - HLP's income is fixed (slope t −0.76).
  - JLP's and GM SOL's look weakly proportional to TVL (t 1.17 and 1.59), so the fixed-income assumption is the
    conservative case.
- **JLP:** a $10M deposit costs 0.1pp. The AUM limit is $3B against $0.9B today.
- **GM SOL-USDC:** +6.9% at $1M, +5.3% at $2M, +2.3% at $5M. The deposit cap is $17.5M per side.
- **Hedge depth** never binds: Binance daily volume is $2.1B in SOL, $8.8B in ETH, $11.5B in BTC.
- **gUSDC withdrawals** wait 3 epochs of 3.0 days. That costs only 0.09% but means no exit while traders are winning.

## Late entry

- An always-on deposit made an hour or a day late keeps over 99.7% of the annual edge.
- The P&L arrives in jumps, though:
  - HLP made 67% of its test P&L in one window;
  - JLP made 50% on its best 1% of days;
  - GM SOL made 34% on its best 1% of days.
- Leaving between jumps forfeits them. HLP's trailing rule, lagged one period, kept 58%.

## Risks and kill criteria (full text in `book_entries.json`)

**JLP.**

- Kill gates:
  - 30-day fee yield below 6.5%;
  - 90-day hedged excess below 0;
  - first 60 days live under +1% with the jlp-info net-delta hedge;
  - daily hedged standard deviation above 0.5% for two weeks;
  - any exploit, fee-split change or AUM-limit change.
- Tails: crowded-long rallies (worst test day −2.1% when SOL rose 10.6%), Solana and Wormhole custody, and margin held on
  a second venue.

**GM SOL-USDC.**

- Kill gates:
  - fee APR (from the subgraph) below 6%;
  - 90-day excess below 0;
  - pool below $3M or above $15M;
  - a GMX v2 exploit or a wrapped-SOL depeg.
- Tail: worst test day −2.0% (5 Feb 2026, SOL −15.0%).

## What failed and why

- **HLP:** it is a crash-liquidation business with fixed-dollar income. A new depositor buys rare windfalls and earns
  about the savings rate between them.
- **gUSDC:** traders beat the vault in September 2026 (collateralisation fell to 87%), and only $4.1M remains.
- **LLP:** the launch-year yield did not persist.
- **GM ETH-USDC and GLV ETH-USDC:** traders won (5.4% a year; 8.7% a year against 9.0% of fees).
- **Single-token GM pools:** fee yields of only 2–4%.
- **dYdX MegaVault:** $1.8M and 90 days of history.
- **No usable history:** Ostium, Avantis, Aster (404), edgeX (503), Drift (DNS failure), Extended (summary only: $64M,
  9.4% 30-day APR), Paradex (no protocol vault).

## Errors found in the worker's own work

1. A path-precedence bug crashed the first HLP collect.
2. Two collectors raced on one manifest; manifests are now one per part.
3. gUSDC supply was scaled by 1e18 instead of its 6 decimals.
4. The GMX subgraph has no daily fee period, so the fee decomposition uses its APR snapshots.
5. The JLP source check first paired prices 22 hours apart and showed a 0.04 correlation; matched properly it is 0.91.
6. LLP first used Dietz despite $4B of internal flows; it now uses value/shares.
7. The first verdict rule labelled any small positive vault "watch" regardless of t.
8. The 120-day robustness window was added after seeing JLP's results diverge. It is applied to every vault but was not
   pre-registered.
9. A run on partial Gains data briefly produced a "go" row; it was removed once the full series arrived.

## Next

1. Forward-test JLP with the jlp-info net-delta hedge.
2. Snapshot HLP and LLP daily, since their APIs serve no daily history.
3. Reconcile LLP's August 2026 numbers.
4. Size the GM SOL deposit against GMX price impact.
5. Keep watching GM BTC-USDC and GLV BTC-USDC.

## Coordinator's check

Recomputed from the raw `vaultDetails` files (`raw/hlp/2026-10-10/`), without the worker's code, from the last allTime
P&L point of each child vault:

| child vaults | lifetime P&L |
|---|---:|
| Liquidator | $43.52M |
| Liquidator 2 | $30.82M |
| Liquidator 4 | $0.84M |
| Liquidator 3 | −$0.50M |
| **liquidators, total** | **$74.7M** |
| Strategy A | $4.39M |
| Strategy B | −$4.35M |
| Strategy X | $0.45M |
| **strategies, total** | **+$0.49M** |

Against the parent's $138.6M this matches the note: HLP's market making nets about zero, and its income is liquidations.

Files: `scripts/house_vaults.py`, `scripts/test_house_vaults.py` (21 tests), `analysis.json`, `tables.md`,
`manifest.json`, `book_entries.json`, `raw/`.
