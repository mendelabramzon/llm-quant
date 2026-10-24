# The redemption buffer: a hedged Liquity v2 trove at the minimum rate, its BOLD in the stability pool

2026-10-23. Code: `scripts/stability_pool.py` (collect, troves, chain, funding, analyze, study), tests in
`scripts/test_stability_pool.py`. Raw data in this folder (gitignored).

## The idea in one paragraph

On Liquity v2, borrowers choose their own interest rate, and redemptions hit the lowest-rate troves first. An
unhedged borrower fears redemption: it sells the borrower's ETH and ends the leveraged position. So borrowers pay
2.5–8.4% a year to stand behind others in the queue, and 75% of that interest is minted to the branch's stability pool
(SP).

A borrower whose collateral is hedged with a short perp does not mind redemption. Redemption hands the redeemer the
collateral at the oracle price and **leaves the redemption fee in the trove**, which is at least 0.5% and averaged
0.87% here. That borrower can therefore:
1. sit at the 0.51% minimum, just behind the troves already at 0.5%;
2. put the minted BOLD in the same branch's SP;
3. collect the SP yield paid by everyone else.

The rent comes from the non-price motive of the other borrowers, who are averse to being redeemed. Nobody competes
for it:
- Liquidations are shared pro-rata, and the keeper who calls `liquidate()` only gets the gas compensation.
- Redemptions are raced by redeemers, but the trove is redeemed passively.
- Entering a day late loses one day.

## Data

Every log since the May 2025 redeployment, through block 26,256,557 (2026-10-23):

| what | rows | source |
|---|---|---|
| SP total deposits (`StabilityPoolBoldBalanceUpdated`) | 28,611 | 3 SPs |
| BOLD minted to each SP (the interest yield) | 40,388 | BOLD `Transfer` from 0x0 |
| `Liquidation` events | 64 | 3 TroveManagers |
| `TroveOperation` (each redeemed trove's rate and amount) | 16,793 (7,642 redemptions) | 3 TroveManagers |
| `Redemption`, `RedemptionFeePaidToTrove` | 7,315 / 7,642 | 3 TroveManagers |
| sUSDS NAV (SSR paid), BOLD→USDC executable at $100k/$1M, USDC→BOLD at $1M | 522 days | archive `eth_call` at 00:00 UTC |
| ETH funding: Hyperliquid hourly, Binance 8-hourly; Lido APR | 12,546 / 1,569 / daily | venue APIs, DefiLlama |

Contracts (the live deployment; the docs' table lists the January 2025 legacy one, now near-empty):

| item | address |
|---|---|
| BOLD | `0x6440f144b7e50d6a8439336510312d2f54beb01d` |
| CollateralRegistry | `0xf949982b91c8c61e952b3ba942cbbfaef5386684` |
| WETH branch | TM `0x7bcb64b2…`, SP `0x5721cbbd…` |
| wstETH branch | TM `0xa2895d6a…`, SP `0x9502b7c3…` |
| rETH branch | TM `0xb2b2abeb…`, SP `0xd442e410…` |

**Coordinator's check.** Two headlines were re-derived by independent paths, and both match to the unit:
- Redeemed BOLD, per branch: `Redemption.actual` against the per-trove sum of `TroveOperation`.
  - WETH: $10,346,024
  - wstETH: $31,167,038
  - rETH: $4,468,605
- Fees kept by troves: `Redemption._ETHFee` against `RedemptionFeePaidToTrove`.

## What a plain SP deposit earned (per BOLD, May 2025 – Oct 2026)

| SP | interest | liquidations | total | average deposits | liquidation premium, sold next hour |
|---|---|---|---|---|---|
| WETH | 4.60% | +0.35% | 4.95% | $7.6M | +2.3% (48 liquidations) |
| wstETH | 5.76% | +0.73% | 6.49% | $14.0M | +5.4% (12) |
| rETH | 7.31% | +0.07% | 7.38% | $3.2M | +3.2% (4) |

For comparison:
- **SSR paid over the same days:** 4.07%.
- **Cost of holding BOLD:** BOLD's median $100k sale price is 0.9992, and its 5th percentile is 0.995.
- **Dilution:** a buy-and-deposit position dilutes its own yield.

Plain deposits are roughly fair value, and that is not the strategy.

## The loop, simulated against history

The model, per day:
- **SP income:** SP income = (our BOLD) × (yield minted + 0.75 × our interest + liquidation gains) / (historical
  deposits + our BOLD). Our own deposit dilutes this.
- **Interest:** minus our interest at rate r.
- **Redemption hits:** for every historical redemption transaction, we absorb the BOLD it took from troves at rates
  above ours, capped at our debt. Ties go behind the troves already at our rate.
- **Each absorbed dollar:**
  1. +BOLD sold at the next day's $1M quote, scaled up for days above $1M;
  2. −collateral handed over, (1 − fee) × oracle/redemption price;
  3. −5bp to re-buy the collateral;
  4. −the 7-day upfront fee on re-borrowing, at a 6% branch rate, which is conservative.
- **Hedge:** the ETH leg is hedged and left out.

The result is the return per dollar of BOLD minted, at r = 0.51% and selling the redeemed BOLD the next day:

| branch | $1M | $5M | $10M | $20M | redeemed $ absorbed per $ of debt per year at $5M |
|---|---|---|---|---|---|
| wstETH | 11.3% | 5.2% | 3.8% | 2.6% | 3.3× |
| rETH | 6.3% | 2.8% | 1.6% | 0.9% | 0.4× |
| WETH | 4.9% | 2.6% | 1.8% | 1.1% | 1.1× |

**Why redemptions pay.** Per absorbed dollar, the cycle earned:
- WETH: +15bp
- wstETH: +35bp
- rETH: +57bp

The value-weighted fee (0.87%) exceeds BOLD's next-day discount (0.34–0.56%). The fee rises with redemption volume
(`baseRate`), so the fee is highest exactly when redemptions are heaviest.

**Protocol (42 variants: 3 branches × 7 rates × 2 resale policies, choose on the first half, test once on the second):**
- **At $1M:** chosen `wstETH r=0.5% sell_next_day`. In sample +10.4%, out of sample +11.9% (rank 1 of 42), OOS t 4.23.
- **At $5M:** chosen `wstETH r=0.5% wait_peg`. In sample +6.0%, out of sample +6.0% (rank 3), OOS t 2.21.
- **Survivors:** 40 of 42 variants survive one-sided BH.
- **Halves and quarters:** every branch is positive in both halves and in every calendar quarter at $5M.
- **Rate:** the lowest rate is best everywhere, as the thesis predicts. Every rate step up costs interest and buys no
  protection a hedged borrower needs.

**Worst case for queue position.** The default sim puts us *behind* the 24–43% of redeemed debt that sat at exactly
0.5%. Putting us in front instead adds about 1pp at $1M.

## The package, against the savings rate actually paid

The package is wstETH (or ETH) collateral at CR 2.5 × the BOLD, hedged by a perp short with 20% margin. Its capital
is 3.0 × the BOLD. The table gives daily excess over SSR at $5M of BOLD:

| hedge venue | branch | carry alone | carry + loop | second half | t |
|---|---|---|---|---|---|
| Hyperliquid | wstETH | +4.64% | **+6.38%** | +4.93% | 11.0 |
| Hyperliquid | rETH | +4.64% | +5.55% | +4.47% | 10.2 |
| Binance | wstETH | +0.87% | **+2.61%** | +1.51% | 6.9 |
| Binance | WETH | −1.22% | −0.36% | −1.38% | −1.1 |

ETH funding averaged 7.96% a year to shorts on Hyperliquid and 3.42% on Binance; Lido averaged 2.51%. Two notes:
- **The carry is not the claim.** The carry is the ETH spot–perp trade the book already watches (HL ETH carry is t < 1
  since 2025-11).
- **The loop increment is the claim.** It adds +1.7pp on capital, or +2.1% a year on the ETH notional at CR 2.5. It
  needs no capital beyond the collateral the carry already holds. It is what turns the Binance-hedged carry from about
  SSR into a positive spread.

## Forward quote, from today's state

Today's state (2026-10-23):

| branch | debt | SP | average rate |
|---|---|---|---|
| WETH | $12.9M | $8.1M | 3.47% |
| wstETH | $21.3M | $9.6M | 2.50% |
| rETH | $4.1M | $4.5M | 8.42% |

Forward income is the SP yield at today's flow, diluted by our deposit, minus 0.51%, plus the *historical* redemption
income at that size:

| allocation | per year |
|---|---|
| $2M each on WETH / wstETH / rETH | $69k + $119k + $84k = **$272k on $6M of BOLD (4.5%)** |
| $5M wstETH alone | $177k (3.5%) |

That is below the historical 5.2%, because branch rates have fallen.

**Capital.**
- Standalone: $18M ($15M collateral + $3M margin).
- On top of an existing hedged ETH carry: zero extra.

**Late entry:** the position is a standing one. A day's delay forgoes one day of SP income; nothing is raced.

## Risks and kill criteria

**Risks.**
- **Smart-contract risk.** The first v2 deployment had an SP bug and was relaunched in May 2025.
- **Trove liquidation if the hedge is not rebalanced.** At CR 2.5 ETH must fall 52% (MCR 120% on LST branches; 110% on
  WETH). The largest 24-hour fall in the sample was 15% (hourly closes). Move perp profit to the trove daily.
- **Branch shutdown.** If a branch's TCR falls below 110%, or its oracle fails, urgent redemptions pay redeemers a 1%
  bonus. We would lose about 1% on the remaining debt.
- **SP losses.** The SP loses if a trove is liquidated below 100% CR. That never happened here; all 64 liquidations
  paid the full 5%.
- **Redemption income is lumpy.** It was zero so far in Q4 2026: BOLD trades about 0.44% under peg, below the 0.5% fee
  floor.
- **Dilution.** If others copy the trade, SP yield falls toward the minimum rate.
- **Over-hedged gap after a redemption.** The perp short is too large until the next day's rebuild. This adds variance
  only.

**Kill criteria.**
1. Trailing-90-day loop P&L below 0.5% a year on the BOLD.
2. The branch average rate falls below 1%, so SP yield at our size is below 1.5%.
3. Any SP loss event (a liquidation at below 100% CR) or a branch shutdown.
4. BOLD below 0.98 for more than 7 days.
5. A Liquity security advisory.

## Implementation

Setup:
1. Buy wstETH and open a trove at CR 2.5 at 0.51%, using the BorrowerOperations `openTrove` with the rate hint.
2. Short the same ETH notional on Hyperliquid or Binance.
3. Deposit the BOLD in the wstETH SP.

Daily job:
1. Read `RedemptionFeePaidToTrove` for our trove id.
2. If we were redeemed, sell the free BOLD, re-buy wstETH, `adjustTrove` back to size, and resize the short.
3. Claim the SP's collateral gains and sell them.
4. Move perp profit and loss to keep CR between 2.2 and 2.8.

None of these steps is time-critical. The redemption fees are visible on-chain.

## Levered version: the 0.51% credit funds more hedged collateral (asked for 20-30%)

The loop above earns ~5% on its BOLD, an add-on to an existing hedged carry. The same credit can instead lever the
carry itself: mint BOLD at 0.51%, sell it for more wstETH (or rETH/WETH), hedge all collateral with a Hyperliquid
short. Per $ of equity, at CR `c` and perp leverage `k`, collateral is 1/(1-1/c+1/k): 1.875x at c=1.5, k=5. The edge
over doing this on Aave is the credit: unhedged borrowers pay 2.5-8.4% for the same BOLD, Aave USDC costs ~5%.

Code: `scripts/levered_trove.py`, tests in `scripts/test_levered_trove.py`. Hourly simulation from 2025-05-19:
- HL hourly funding, Lido APR, every historical redemption that would have reached a 0.51% trove (ties in front);
- band rebalancing decided at an hour's close, executed at the next close (bridge time);
- costs: BOLD sold at the day's Curve quote scaled past $1M, the 7-day upfront fee at 6% on every debt increase,
  5bp spot, 4.5bp perp taker;
- liquidation checks on Binance hourly highs and lows (wickier than Chainlink or the HL mark, so conservative).
  A trove liquidated at the wick costs 5% of debt and sells the collateral at the wick while the hedge settles at
  the close.

Return on equity, no liquidation in the sample (c=1.5, k=5, rebalance on a 10% move):

| branch | $1M equity | $5M equity | 2nd half ($1M / $5M) | max DD | redemptions absorbed ($1M) |
|---|---|---|---|---|---|
| wstETH | 22.5% | 18.7% | 19.0% / 15.2% | 0.35% | 23x equity |
| rETH | 18.6% | 17.9% | 15.0% / 14.2% | 0.34% | 2.5x |
| WETH (c=1.35) | 15.9% | 14.9% | 12.3% / 11.0% | 0.52% | 7.8x |

Protocol (`choose_then_test`, excess over SSR, first half chooses):
- **Full grid (108 variants incl. k=8): fails.** It chose wstETH c=1.5 k=8, OOS -0.6% ($1M), rank 83.
  k=8 survived the first half and was liquidated on 2026-08-19 (ETH +22% in 24h).
- **Risk-capped grid (k <= 5, fixed before looking at the OOS half, from the stress: a 10% band plus the worst 1h
  wick of +13% must not reach 2% maintenance): chose wstETH c=1.5 k=5 band=10%.** OOS excess over SSR +15.4%
  (t 7.99) at $1M, +11.5% (t 9.44) at $5M; rank 7/72; 58 one-sided BH survivors.
- **Quarterly ROE** (wstETH, $5M): 20.0, 30.4, 18.1, 11.6, 11.5, 21.5, 16.9%. This tracks HL funding: 2026Q1-Q2 at
  3.6-4.2% gave ~11%.
- **More leverage does not buy 25-30%.** Every c=1.35 variant on wstETH/rETH was liquidated once or twice.
  They lost 7-16% of equity, drew down 26-46%, and returned -15% to -1.4%.

Correction to the risk paragraph above: on hourly highs and lows the worst 24h was -21.6% (2025-10-10) and +22.3%
(2026-08-19); the -15% figure was close to close.

**Forward quote.**
- At HL funding of 8.7% (last 90 days) and Lido 2.22%: 1.875 x 10.9% - 1.25 x 0.51% = 19.8% gross.
- After about 2%/yr of rebalancing, that is **~17-18% ROE**.
- Capacity is BOLD's sale depth: at c=1.5, debt is 1.25x equity. $2M on each of wstETH and rETH means selling $5M of
  BOLD, against ~$38M outstanding and the $1M Curve quote at 0.997. That gives **~$700k/yr on $4M**.
- A Binance hedge at 3.4-4.7% funding gives ~10-12%.

**Kill criteria (levered).**
- HL ETH funding below 3% over a trailing 30 days: ROE falls below ~10% and the 6% liquidation buffer stops being
  worth it.
- Any perp or trove liquidation.
- BOLD below 0.99 for more than 3 days: our own sales are the peg risk.
- The rebalancer missing a 10% band for more than 2 hours.

### Small accounts ($1k-$300k): the follow-up question

- **Floor.** Liquity v2 `MIN_DEBT` is 2,000 BOLD and every trove locks 0.0375 ETH (~$90, refundable) as gas
  compensation. At CR 1.5 that means equity of at least ~$1.7k, so $1k cannot open a position.
- **Gas.** Ethereum base fees were 0.15 gwei (median) and 0.31 gwei (p90) over the last ~day. One full rebalance is
  modelled at a fixed $3, with $10 as the stress case. That covers adjustTrove, a Curve swap, a CCTP bridge and the
  $1 HL withdrawal.
- **New simulator options.**
  - `fixed`: the $ cost of each rebalance.
  - `relever_at=0.8`: after a redemption, trim the short at once (HL only) and rebuild the trove only below 80% of
    target.
  - Rebuilds after a redemption now wait for the next UTC day's quote, because BOLD trades below 1 - fee while
    redemptions run.
  - The rebalance band is tightened to 5%. With a 10% band, CR 1.5 drifts to ~1.36 before rebalancing, and whether
    the 2025-10-10 wick liquidates it then depends on path luck.

Return on equity at c=1.5, k=5, band 5%, $3 fixed (WETH c=1.35). None of these rows had a liquidation:

| equity | wstETH | rETH | 1st / 2nd half (best branch) | $/month (best) | redemptions absorbed, x equity per year |
|---|---|---|---|---|---|
| $10k | 29.0% | 49.0% | 61.9 / 36.1 (rETH) | $408 | 117 (rETH) |
| $30k | 33.1% | 37.0% | 42.0 / 31.9 (rETH) | $924 | 55 |
| $100k | 34.5% | 26.1% | 34.3 / 34.7 (wstETH) | $2,875 | 134 (wstETH) |
| $300k | 27.8% | 20.8% | 29.4 / 26.2 (wstETH) | $6,948 | 54 |
| $1M | 21.3% | 18.8% | 24.1 / 18.5 (wstETH) | $17,740 | 16 |

- **Why small is better.** A small trove is fully redeemed many times a year and keeps the fee each time
  (0.79% average). The rebuild costs ~0.6%.
- **Protocol.** `choose_then_test`, 36 variants per size (k <= 5), excess over SSR.
  - $100k chose wstETH c=1.5 k=5 band 5%: OOS +31.0% (t 4.56, rank 1/36), all 36 BH survivors.
  - $10k chose rETH c=1.5 k=5 band 5%: OOS +32.4% (t 4.73).
- **Fragility.** At $10k, `fixed` = $10 cuts wstETH to 12.1% and its worst quarter to -25.5%.
- **The churn is the fragile part.** At $100k on wstETH, fees are 106% of equity a year and costs 94%. 10bp more cost
  per redeemed dollar removes ~13pp of return on equity.
- **No 2026Q4 redemption reached a 0.51% trove.** (Corrected 2026-10-24: $6.3M was redeemed on WETH and wstETH,
  all from troves at exactly 0.50%, which other loopers keep re-opening; see `research/2026-10-24/cdp_forks`.) The floor with no redemptions at all (same prices and funding) is
  14.9% at $10k (fixed costs) and 17.5% at $100k-$300k, of which 11.6% / 13.8% in the second half.
- **Forward range.**
  - $10k: $125-400 a month.
  - $100k: $1.5-2.9k a month.
  - $10k a month needs ~$350k if redemptions return to history, ~$700k if they don't.

## Screened and set aside in the same pass

| candidate | why not |
|---|---|
| Buy BOLD, deposit in an SP (no trove) | +0.4–3pp over SSR before BOLD's 0–0.5% discount and own-dilution; the loop dominates it |
| Liquity v1 LUSD at 0% interest | Free credit is real: the 0.5% one-time fee, and LUSD sells at +37bp at $100k. But v1 takes only ETH, and the 2.5% staking yield forgone exceeds the credit's value at any safe CR. The v1 SP holds $6.6M against a 669% TCR and earns almost nothing |
| Aave Umbrella (stake aUSDC/aUSDT/aWETH) | +1.2–1.8pp reward over the aToken for first-loss on Aave deficits and a 20-day cooldown; a fair insurance premium, not a rent |
| fx Protocol SP v2 | 7–9% displayed on $73M; needs a share-price check (the repo's displayed-yield law) before it is believed |

## Next

1. **Felix on HyperEVM** (Liquity v2 code, HYPE/kHYPE/UBTC branches, feUSD SPs at 4–6%):
   - The same loop hedged on Hyperliquid's HYPE perp, which pays the book's best funding.
   - kHYPE collateral would stack the queue bid, the carry and the loop on one coin.
   - Blocker: HyperEVM archive RPC (three public endpoints ignore the block tag).
2. **The other Liquity v2 forks** (Nerite on Arbitrum, Asymmetry USDaf, Ebisu, Quill). `stability_pool.py` takes only
   addresses.
3. **Forward ledger.** Register a paper trove at 0.51% on each branch and score it daily from `RedemptionFeePaidToTrove`
   and SP mints.
