# The hedged floor-rate trove, across chains: every Liquity v2 fork, with $10k trades

2026-10-24, about one hour of work. Code: `scripts/cdp_forks.py`:
- `snapshot`: the live state of every fork, read through its CollateralRegistry;
- `redemptions`: 30 days of redemptions from explorer or RPC logs;
- `trades`: the $10k trade sizer.

Data in this folder (`snapshot.json`, `redemptions_*.json`, `hl_funding.json`, `trades_10000.json`).

## The pattern being searched for

A Liquity v2-style CDP lets borrowers set their own interest rate, and redemptions take the lowest-rate troves first.
Unhedged borrowers pay well above the floor to avoid redemption. A borrower whose collateral is shorted on a perp does
not care about redemption, so it can borrow at the 0.5% floor.

There are two ways to use that cheap credit:
- **Levered carry** (`scripts/levered_trove.py`): sell the stable for more collateral and short all of it. This earns
  staking yield plus perp funding on about 1.9x the equity.
- **Redemption buffer** (`scripts/stability_pool.py`): keep the stable in the stability pool and collect the redemption
  fee that stays in the trove.

The buffer pays only when the stable trades closer to peg than the fee after a redemption. This census shows where that
holds and where it does not.

## Census (live, 2026-10-24 ~00:30 UTC; branches with ≥ $20k debt)

How the columns are computed:
- **Share of redemptions** = the branch's unbacked debt (debt − SP) / the sum across branches. This is how the
  CollateralRegistry routes a redemption.
- **SP yield** = 75% × average rate × debt / SP. This assumes the Liquity v2 split; forks may differ.

| protocol | chain | stable: supply @ price | branch | debt | avg rate | lowest rate | debt at ≤ 0.51% | SP | SP yield (est) | share of redemptions | redeemed, last 30 days |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Liquity v2 | Ethereum | BOLD $38.3M @ 0.9956 | WETH | $12.9M | 3.47% | 0.50% | $287k | $8.1M | 4.1% | 29% | $2.38M (94% from 0.5% troves) |
| | | | wstETH | $21.3M | 2.50% | 0.50% | $2.17M | $9.6M | 4.2% | 71% | $5.19M (83% from 0.5% troves) |
| | | | rETH | $4.1M | 8.42% | 0.50% | $30k | $4.5M | 5.7% | 0% | $13k |
| Felix | HyperEVM | feUSD $9.35M @ 0.9983 | WHYPE | $7.95M | 3.47% | 0.50% | $4.21M | $5.0M | 4.1% | 91% | $14k in 14 days (all from 0.5% troves) |
| | | | UBTC | $0.42M | 11.29% | 0.60% | $0 | $1.95M | 1.8% | 0% | $0 in 14 days |
| | | | kHYPE | $0.53M | 9.63% | 4.00% | $0 | $0.87M | 4.4% | 0% | $0 in 14 days |
| | | | wstHYPE | $0.44M | 3.63% | 3.60% | $0 | $0.14M | 8.7% | 9% | $2k in 14 days (the 3.6% trove) |
| Enosys Loans | Flare | CDP $4.60M @ 0.9884 | FXRP | $3.76M | 5.91% | 5.10% | $0 | $3.35M | 5.0% | 95% | $288k in 1,349 txs (median $120), all from the 5.1% trove; fee 0.98% |
| | | | WFLR | $0.29M | 11.75% | 6.50% | $0 | $0.31M | 8.4% | 0% | $5k |
| | | | stXRP | $0.13M | 7.12% | 6.40% | $0 | $0.11M | 6.3% | 5% | $10k |
| | | | sFLR | $0.42M | 1.50% | 0.90% | $0 | $0.42M | 1.1% | 0% | $25k |
| Asymmetry USDaf | Ethereum | USDaf $0.24M @ 0.987 | ysyBOLD + 3 others | $0.24M | 0.5–4.9% | 0.50% | — | $0.04M | — | — | too small |
| Nerite | Arbitrum | USND $0.03M @ 0.994 | WETH | $0.03M | 1.67% | 0.80% | — | $0.01M | — | — | too small |
| Quill | Scroll | USDQ $0.12M | wstETH, SCR | $0.12M | 6.6–7% | — | — | ~0 | — | — | too small; SCR branch shut down |
| Base Dollar | Base | BD $0.08M | 5 branches | $0.08M | 1.0–1.5% | 0.50% | — | $0.05M | — | — | too small |
| Ebisu, DeFi Dollar, Orki | Ethereum / Plasma / Swellchain | — | — | < $0.02M | — | — | — | — | — | — | dead or empty |

Liquity v1 (0% interest, one-time fee, ETH only), for comparison:
- LUSD supply $25.7M @ 1.0029; borrowing fee 0.50% one-time; system collateral ratio 664%.
- Redemptions take the lowest collateral ratio first, and the fee goes to LQTY stakers, so a redeemed hedged trove is
  only flat.

Hedge funding on Hyperliquid, taking the lower of the 30-day and 90-day annualised rates:
- HYPE 8.61% ($1.6B open interest, max 10x);
- BTC 8.21% (40x);
- ETH 8.38% (25x);
- XRP 9.03% (20x);
- FLR is not listed on Hyperliquid or Binance, so the FLR branches are unhedgeable.

## Findings

1. **The redemption-buffer rent is already competed for on Liquity v2.** Since Oct 1, $6.3M of WETH and wstETH debt
   was redeemed, all of it from troves at exactly 0.50%. Those troves are re-opened over and over: the 0.5% layer is
   only $0.3M (WETH) and $0.7M (wstETH) at any moment. That is other borrowers running this strategy. A trove at 0.51%
   received nothing in Q4, so the small-account redemption income in yesterday's simulation is not available today.
2. **Enosys (Flare) shows the rent taken by redemption arbitrage instead.**
   - CDP trades at 0.988, about 1 minus the 0.98% fee.
   - Bots redeem in $120 pieces, 1,349 times a month.
   - A trove below 5.1% would be first in line. It would absorb about 25x its own debt a month, and each rebuild loses
     ~0.45% (the fee earned minus the 1.2% CDP discount, the upfront fee and trading costs).
   - **No-go at any rate below the redemption reach**, and above it the credit is no longer cheap.
3. **Cheap credit with no redemption exposure exists where the stability pool exceeds the branch's debt.** Those
   branches receive no redemptions:
   - Liquity v2 rETH: 0.51% vs an 8.42% average; $30k of debt queued at or below 0.51%;
   - Felix UBTC: 0.5% vs an 11.29% average; SP $1.95M vs debt $0.42M;
   - Felix kHYPE: 0.5% vs 9.63%.

   Here the floor rate is just a 3–11 point discount on credit for anyone indifferent to redemption. Leverage turns
   that into ~13–14% a year on equity.
4. **The other forks are too small to trade.** USDaf, Nerite, Quill, Base Dollar, Ebisu and Orki have less than $0.25M
   of stable each, so selling even $10k of their stable moves the price.

## Exact $10k trades (levered carry; prices at snapshot; first-year net)

Shared assumptions:
- Rebalance on a 5% move. Liquidation is checked hourly against highs and lows, as in `levered_trove.py`.
- Net = carry − one-time entry − fixed $/yr.
  - Carry = collateral × (stake + funding) − debt × 0.51%.
  - Entry = selling the stable once, plus the 7-day upfront fee at 6%.
  - Fixed = gas and bridging for ~150–250 rebalances: $450 on Ethereum, $40 on HyperEVM, $300 on Flare.
- Funding is the lower of the 30- and 90-day rates.

| # | protocol / branch | exact legs ($10k equity) | collateral / debt / HL margin | net $/yr | $/month | ROE | liquidates at | redemption exposure | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Liquity v2 rETH** (Ethereum) | Buy 2.22 rETH with $6,250. Open a trove through Liquity's leverage zapper to **6.67 rETH** of collateral, borrowing **12,500 BOLD at 0.51%** (BOLD → rETH on Curve/Uniswap). Send $3,750 USDC to Hyperliquid and **short 7.84 ETH** (5x). | $18,750 / $12,500 / $3,750 | **$1,394** | **$116** | 13.9% | ETH −20% (CR 1.5 → MCR 1.2) | none routed (SP > debt); $30k queued at ≤0.51% | **go**, best on Ethereum |
| 2 | **Felix UBTC** (HyperEVM) | Buy 0.080 UBTC with $6,521. Open a Felix trove with **0.214 UBTC**, borrowing **10,870 feUSD at 0.5%**. Sell feUSD on HyperCore spot FEUSD/USDC (bid $79k at 0.999) and loop into UBTC. **Short 0.214 BTC** on HL (5x) with $3,478. | $17,391 / $10,870 / $3,478 | **$1,309** | **$109** | 13.1% | BTC −22% (CR 1.6 → MCR 1.25) | none routed (SP $1.95M vs debt $0.42M); we would be first in line | **go**, cheapest to operate (no cross-chain bridging) |
| 3 | **Felix kHYPE** (HyperEVM) | **156.4 kHYPE** of collateral, borrowing **6,522 feUSD at 0.5%** (CR 1.9). **Short 160 HYPE** on HL (3x) with $4,130. | $12,391 / $6,522 / $4,130 | $1,264 | $105 | 12.6% | HYPE −29% (MCR 1.35) | none routed today; first in line (lowest is 4.0%) | go; HYPE moves ~2x ETH, so leverage is lower |
| 4 | Felix wstHYPE | the same with 155 wstHYPE | $12,391 / $6,522 / $4,130 | $1,252 | $104 | 12.5% | HYPE −29% | 9% of routed redemptions; first in line (lowest is 3.6%) | go, watch redemptions |
| 5 | Liquity v2 wstETH | as #1 with **6.28 wstETH**, short 7.84 ETH | $18,750 / $12,500 / $3,750 | $1,397 | $116 | 14.0% | ETH −20% | 71% of routed redemptions, but $2.17M queued at ≤ 0.51% ahead of us | go; the same carry as rETH, with no redemption income at 0.51% |
| 6 | Liquity v2 WETH | **9.10 WETH**, borrowing 16,129 BOLD at 0.51% (CR 1.35), short 9.10 ETH | $21,774 / $16,129 / $4,355 | $1,194 | $99 | 11.9% | ETH −19% | 29%; $287k ahead | ok; no staking yield |
| 7 | Liquity v1 LUSD | ETH trove at 0% interest (0.5% one-time fee). Mint 12,500 LUSD and **sell it at 1.0029**. Hold 7.84 ETH, short 7.84 ETH | $18,750 / $12,500 / $3,750 | ~$1,095 | ~$91 | 11% | ETH −27% (MCR 1.1) | redeemed first by collateral ratio, at no gain or loss | ok; no staking yield, but no rate risk ever |
| 8 | Enosys FXRP (Flare) | 13,173 FXRP of collateral, borrowing 11,429 CDP at 0.5%, short 13,173 XRP | $17,143 / $11,429 / $4,286 | carry $1,034, but redemption churn costs about −$1,200 a month | negative | — | XRP −27% | 95% routed, and we would be first: ~25x the debt each month | **no-go** |

**Bottom line for $10k.** The best trades are Liquity v2 rETH, Felix UBTC and Felix kHYPE. Each makes **$105–116 a
month (12.6–14% a year)**. Splitting $10k across two of them gives the same total with less venue risk. That is ~2.5x
the savings rate, from a rent nobody is racing for on those branches. It is still a long way from $1k a month: at
these rates that takes ~$85–95k.

## What would change the numbers

- **Funding.** Every row is about 1.7–1.9x funding plus staking. Each point of HL funding moves the result by ~$15 a
  month at $10k. In 2026Q1–Q2, ETH funding at 3.6–4.2% would have halved these rows.
- **Redemption routing.** Routing flips when a branch's SP falls below its debt. Felix kHYPE and UBTC and Liquity rETH
  then start receiving redemptions, and our trove sits first in line. That is fine while the stable trades near peg
  (the trove keeps the 0.5–1% fee) and costly when the stable trades at 1 − fee (finding 2). Kill rule: rebuild only
  when the stable is at or above 0.997.
- **The stability pool split for forks.** The 75% split is assumed for Felix and Enosys. It does not enter the trade
  rows above, only the SP-yield column.
- **Liquidation.** The c and k choices come from the ETH path since May 2025. HYPE and BTC paths were not simulated
  here.

## Next

1. Simulate Felix UBTC and kHYPE with `levered_trove.py`, using BTC and HYPE hourly paths.
2. Felix redemption history beyond 14 days. HyperEVM RPCs cap a log query at 1,000 blocks, so 14 days is 1,210
   calls over three endpoints. Felix's `Redemption` event does not match Liquity's signature; the counts above come
   from `TroveOperation` (op 6).
3. A forward paper ledger for rows 1–3.
