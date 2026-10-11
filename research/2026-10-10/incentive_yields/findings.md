# Paid by marketing budgets: incentive-adjusted dollar yields — 2026-10-10

Protocols and chains spend fixed token budgets to rent deposits. Attention, not speed, decides who collects them. Two
questions:

- does rotating through the highest incentive-adjusted dollar yields, net of losses, beat the savings rate;
- do new chains pay a premium slow enough to collect.

**Answer: no, on both questions.**

- **Question 1, all dollar pools.** The rotation beats the savings rate only on DefiLlama's displayed numbers. Where a
  share price can check the return, yields above ~5pp over the savings rate do not show up, and the pre-registered
  choice lost money.
- **Question 1, blue-chip lending.** This version passed its pre-registered test (+2.76% a year out of sample, t 3.05),
  but by luck. Its 18 pre-committed sibling variants averaged −0.16%, because one curated Morpho vault's 98%
  write-down caught six of them.
- **What survives** is about +1% a year of rewards on pooled money markets, found post hoc. Watch, not go.
- **Question 2, new venues.** The premium is visible in displayed yields (+4.7 to +6.1pp in a chain's months 1–3), but
  the pre-registered new-chain rule made −0.23%.

| question | verdict | out of sample, excess over the savings rate paid | size |
|---|---|---|---|
| (1) top-5 rotation, all dollar pools | **no-go** | +14.99% (t 4.16) on displayed yields; −3.75% (t −0.41) on pools a share price checks; +0.85% on pools alive today | — |
| (1) blue-chip lending rotation (k7, h 1.0, hold 4 weeks) | **watch** | +2.76% (t 3.05), +2.62% when checked; sibling average −0.16%, 6 of 18 at −5.4% to −6.6% | $27.6k/yr at $1M if the tail misses |
| (1) same, pooled money markets only (post hoc) | **watch, forward test** | +1.06% (t 3.24); every rewarded variant +0.8% to +1.3% | ~$10.6k/yr at $1M |
| (2) new-chain lending, chain age ≤ 90 days | **no-go** | −0.23% (t −0.89); −0.43% while invested | — |

## Data and method

**Universe.**

- `/poolsOld` is paywalled, so dead pools come from 135 Wayback captures of `yields.llama.fi/pools` (2022-10-13 →
  2026-10-10, roughly weekly) plus today's snapshot.
- That gives 5,080 single-exposure dollar pools; 3,775 reached $1M at some capture. DefiLlama's stablecoin flag also
  admits ETH/BTC wrappers and governance tokens, so a dollar-symbol test was added.
- Daily charts were fetched for 2,513 pools. Another 110 had their records deleted by DefiLlama (107 old Morpho vault
  ids) and were rebuilt from the captures.
- All 1,360 top-10 slots across the captures have data, in both universes.

**Rule.**

- Each Monday, using data before that day only: rank by trailing k-day `apyBase` + h × `apyReward`.
- Filters: TVL ≥ $1M, fresh data, no hack in the last 30 days, deposit token ≥ $0.985.
- Hold the top 5 in equal slices for H weeks; a held pool stays while it ranks in the top 10.
- 36 variants pre-committed (k 7/30 × h 0/0.5/1 × H 1/2/4 × universe; `precommit.json`).
- Blue-chip means DefiLlama category Lending, protocol TVL ≥ $1B and at least a year of history, judged at each date.

**Money.**

- Rewards are valued at the price on their sale day (weekly claim, sold a day later, 1% sale cost). Reward tokens were
  priced for 1,208 of the 1,411 pools that list them; the rest use the in-sample mean ratio (1.0075).
- Dilution: a deposit X into a pool of TVL T keeps T/(T+X) of both base and reward.
- Costs: gas by chain and era, $10 + 5–8bp per bridge, 2–50bp per stablecoin swap.

**Losses.**

- Hacks: 94 joined to pools. Severity is net amount stolen ÷ venue TVL; at ≥ 5% the slice is marked to zero for 30 days.
- Depegs of the deposit token beyond 1%.
- The share-price audit, which decides the verdict. DefiLlama floors vault yields at zero (3 negative `apyBase`
  records out of ~800k), so vault losses never appear in the yield series.
  - For 637 pools DefiLlama prices the share token. A vault share (414 pools) must deliver its claimed `apyBase` in its
    price; any shortfall is booked.
  - A vault whose TVL collapsed while held is marked four weeks later, because a 100%-utilised vault cannot be exited.

**Protocol.** Split at 2024-07-01: 89 weeks in sample, 118 out. Benchmark: the savings rate actually paid (DSR, then
SSR). Newey-West t with 8 lags, 8-week block bootstrap, Benjamini-Hochberg across variants, deflated Sharpe.

**Worker's independent check (passed).** Aave v3 USDC/USDT and Spark DAI on-chain supply index growth over 29 weekly
windows, against DefiLlama's summed daily `apyBase`:

- ratio 0.9995, mean gap −0.003pp, mean absolute gap 0.28pp;
- point rates at 23:00 UTC differ by up to 9.3pp on stress days (mean absolute gap 1.03pp over 42 reads), but weekly
  accrual matches.

## Results in and out of sample

**All dollar pools: displayed +18.30% in sample (t 6.59), +14.99% out (t 4.16, 95% interval +6.35% to +20.91%).** All 18
variants were positive out of sample. None of it survives the audit:

- 83% of the excess ($541k of $652k, on $1M over four years) came from 91 pools that no share price can check.
- Restricted to pools alive today, the same rule makes +0.85% (t 0.05). 72% of its held days were in pools that later
  died, and DefiLlama shows their yield but not their deaths.
- In the audited family, the in-sample choice made −3.75% out of sample (rank 13 of 18; siblings ranged −8.5% to +7.9%).
  Share shortfalls cost $435k.
- Across 17,954 four-week pool windows, the vault-share shortfall grows with displayed excess:

| displayed excess over savings | share shortfall | net excess, checked pools | net excess, unchecked pools |
|---|---|---|---|
| 2–5pp | −1.1pp | +1.58% | +1.37% |
| 5–10pp | −3.6pp | +2.10% | +5.38% |
| 10–20pp | −6.3pp | +3.55% | +10.17% |
| ≥ 20pp | −24.1pp | −5.24% | +22.75% |

Below ~5pp checked and unchecked pools agree. Above it, the extra yield is credit risk, as `pendle_history` found.

**Blue-chip (k7 h1.0 H4): +0.76% in sample (t 1.37), +2.76% out (t 3.05, interval +1.24% to +4.64%).**

- Both halves positive (+1.41%, +4.10%); last 52 weeks +3.98%. 11 of 18 blue-chip variants pass BH out of sample.
- It is all rewards: ignoring them gives −0.04%. Valuing them at accrual price instead of sale price changes nothing.
- Five pools made 70% of the excess; Aave's sGHO alone made 33%.

**The tail behind the siblings.**

- The worst sibling (k7 h0.0 H1) bought the Re7 USDC Morpho vault on 2025-11-10 at a share price of 1.099, during its
  100%-utilisation yield spike. It exited on 2025-11-17 at 0.0174: −$197k on a $200k slice.
- Six weekly variants caught it. A post-hoc guard against runs and spikes only moved the hit to the 4-week variants
  (−6.9% to −7.9%).
- Without the curated-vault platforms (Morpho vaults, Euler v2; post hoc), rewarded variants made +0.8% to +1.3%
  (t 2.1–4.7) and unrewarded ones −0.1% to −0.8%.

**References.**

- Holding Aave v3 USDC: −1.01% (t −3.29). The five largest blue-chip pools: −0.34%.
- In 2023–24 Maker's subsidised 5–8% savings rate beat every lending market. That is why the in-sample period earned
  nothing.

## Losses by venue type (all pools, zero size, annualised)

| type | annual loss | net excess |
|---|---|---|
| single-sided DEX pools | hacks −7.15% (4.1% chance per four weeks) | −8.91% |
| leveraged farming | hacks −3.51% | −2.46% |
| derivatives | hacks −2.08%, share/depeg −3.91% | −1.12% |
| yield vaults | share/depeg −3.68% | +1.04% |
| cross-chain bridges | share/depeg −4.17% | −1.80% |
| lending | hacks −1.21% | −1.25% |
| blue-chip lending | hacks 0.00%, share/depeg −0.65% | −0.80% |

## Survivorship

- The captures restore dead pools: 61% of the 2,623 pools with data are missing from today's `/pools`.
- The bias runs the unusual way here: dead pools carried the paper yield, so a survivors-only test *understates* the
  displayed edge.
- Bound on pools the captures missed: `/distinctID` lists 401,835 ids. Of 6,860 never-captured ids in the universe's
  projects, 1 of 80 sampled reached $1M after the start, for one day. That is about 86 missing pool-days against
  550,123, at most 0.02%.

## New-venue curve

Sample: 60 chains whose DefiLlama TVL starts on or after 2022-09-01. Premium is measured against the same-date median of
old chains.

| chain age (months) | displayed premium | net excess |
|---|---|---|
| 0–1 | +1.3pp | +2.3% |
| 1–2 | +4.7pp | +3.4% |
| 2–3 | +6.1pp | +5.2% |
| 3–6 | +2.1pp | +2.1% |
| 6–12 | +4.2pp | +3.5% |
| 12–24 | +1.9pp | +1.1% |
| 24+ | +2.0pp | −0.2% |

- Old chains' net excess is −1.0%.
- Fitted half-lives: 24.4 months for the displayed premium, 8.5 months for net excess. Both are poorly identified: months
  0–3 hold only 88 pool-windows, mostly unchecked.
- New pools on any chain show +2.6% net excess in their first month and −3.1% after two years.
- The pre-registered rule (top-3 lending pools by TVL on chains ≤ 90 days old) made −0.08% in sample and −0.23% out of
  sample. While invested it made −0.43% (64 weeks, 10 chains); the 180-day version made −0.96% (t −2.93).
- The premium sits in small, unchecked pools, not in a new chain's main lending markets.

## Capacity and incentive spend

**Capacity.** For the chosen blue-chip picks on 2026-10-05, the deposit at which marginal yield falls to SSR + 1pp
(4.8%) sums to $30.6M at displayed yields. The backtest is stricter:

| capital | out-of-sample excess |
|---|---|
| $1M | +2.76% |
| $2M | +1.74% |
| $5M | +1.01% (peak $50.7k/yr) |
| $10M | +0.19% |

Universe-wide at displayed yields the same measure is $634M (blue-chip) and $2.0B (all pools).

**Incentive spend now.**

- Total: $580.6M a year after excluding reward APRs above 500% and pools under $10k (raw sum $2.45B). Stable $268.5M,
  volatile $312.0M.
  - The rent map's $353.5M uses a stricter filter: DefiLlama's outlier flags and a 300% cap.
  - The honest band is roughly $350–580M.
- USD-stable single-exposure pools: $233.7M on $7.33B of TVL. This spend grew from $44M (2024-01) to $256M (2025-09) and
  was $227M on 2026-10-01.
- By chain: Ethereum $249.4M, Base $187.8M. By project: Morpho $126.3M, Aerodrome Slipstream $100.5M.
- Merkl's live campaigns: $267.4M a year, $247.4M of it on dollar positions.

## Late entry

| delay | blue-chip | all pools |
|---|---|---|
| 1 hour | finer than the daily data; the yield is accrual, so ~all kept | same |
| 1 day | +2.53% (92% kept) | +14.21% (95%) |
| 1 week | +1.56% (57%) | +12.22% (82%) |

## Risks and kill criteria (watch row in `book_entries.json`, go = false)

**Risks:** a curated vault's write-down bought at its yield spike; dependence on a few campaigns; the pooled-only
universe was defined after seeing the tail.

**Kill criteria:**

- trailing 13-week excess below 0;
- the picks' reward APR below 1pp for four weeks;
- a share shortfall above 1% or a matched hack at a held venue: exit; two in a quarter: retire;
- capacity of the picks below $2M.

## What failed

- `yields.llama.fi` answered HTTP 429 (rate limit, shared IP) to about two requests in three. 1,152 pools that were
  ≥ $1M at a capture have no chart. None of them ever reached a top-20, so they only thin the low-yield buckets of the
  window study.
- Vault losses are invisible without share prices: DefiLlama's `pricePerShare` only starts in 2026-02.
- Euler V1's hack nets to zero severity after funds were returned, so its three-week freeze is not modelled.
- Part (b), hedged LP, was not run.

## Errors found in the worker's own work

1. A one-day bad print (iUSD priced at 8e-7) turned $2k of rewards into $43.6M. Fixed with 3-day backward-median prices
   and a 3× cap on the sale ratio.
2. The stablecoin flag let USUALX, ZBU, sdBAL and ETH/BTC wrappers into the universe. Fixed with the dollar-symbol test.
3. Look-ahead: dollar status was judged on recent prices, which would have dropped tokens that later collapsed. It is
   now judged on each token's first 90 days.
4. A 1% depeg band let a vault's yield overstatement pass at about 0.4% a week. Vault shortfalls are now booked in full.
5. Every hack froze its slice, so a 0.3% Venus exploit zeroed a slice for 30 days. Now only hacks of ≥ 5% freeze. This
   is post hoc; it changes t-statistics, not the selection metric.
6. Yields project names differ from protocol slugs, so Euler V1 and Resolv were unmatched to their hacks. Fixed with an
   alias table.
7. The deleted Morpho charts. Rebuilding them moved blue-chip from +2.93% to +2.76% and exposed the Re7 tail.

## Next

1. Register a forward ledger for the pooled money-market rotation.
2. Add utilisation from the Morpho/Euler APIs as a run warning.
3. Extend the share-price audit to the 1,152 unfetched pools.
4. Value Pendle and Notional LPs with `pendle_history`.
5. Run part (b), hedged LP.

## Coordinator's check

Recomputed from `raw/pools_2026-10-10.json.gz` alone, with the worker's filter (reward APR in (0, 500%], TVL ≥ $10k):
1,877 pools, **$580.6M a year, $268.5M stable, $312.0M volatile**. That matches the note exactly.

Files: `scripts/incentive_yields.py`, `scripts/test_incentive_yields.py` (30 tests), `analysis.json`, `tables.md`,
`manifest.json`, `precommit.json`, `book_entries.json`, `raw/`.
