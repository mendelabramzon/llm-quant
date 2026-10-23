# Liquidity rents on Polymarket and Kalshi, against a slow quoter (2026-10-14)

**Verdict: no-go on both venues. `book_entries.json` is `[]`.**

The rents are real and large:
- Polymarket configures **$179.6k a day** of liquidity rewards (`budgets.usd_day_total`), and paid **$173k a day** over the
  last week (`chain.last7_mean_usd_day`).
- Kalshi's liquidity programme (LIP) paid **$220.7k a day** over 30 days (`kalshi.paid_out_last30_usd`).

But an hourly quoter gives most of its simulated rewards back to adverse selection:
- **Polymarket:** the variant chosen in sample (`crypto|d0.33v_x5_vol`) made +178% a year excess in sample and +4.8% out
  of sample. Its HAC t was 0.05, it ranked 33rd of 72, and it is not a false-discovery survivor (`protocol`, `go_rule`).
- **Kalshi:** the chosen `q100_novol` went from +336% in sample to +23% out of sample, t 0.22 (`kalshi_sim.protocol`).

Numbers are from `analysis.json` (key in brackets) and `scripts/pm_rewards_mm.py`; tables are in `tables.md`.

## Mechanism and counterparty

The payer is each venue's marketing budget, which has no price motive. The rent is clawed back by informed flow that
trades through an hour-old quote. Simulated fills gain 1.4c a share at 1 h, but lose 3.3c at 6 h and 3.0c at 24 h
(`markouts_chosen`).

The pools a slow quoter wins cheaply are exactly where that flow lives:
- the greedy allocation's first picks are same-day temperature and intraday-price markets;
- 35% of rewarded books have nobody inside the reward band, with a median half-spread of 12c (`competition.all`).

## Polymarket: the budget and who collects it

**Budget** (`budgets`): 18,563 markets carry rewards.
- By category: politics $91.5k a day, other $35.2k, sports $26.5k, economics $21.1k, crypto $5.3k.
- The median market gets $3 a day. Half the budget sits in 765 markets.

**Payouts** (`chain`): rewards are paid on chain in pUSD by `0x2c2795ea295d5eb51f9121b728ed2ea4e936a709` at 00:00 UTC.
- $7.72M over 61 days, growing from $94k a day to $173k a day.
- In the last 30 days, 8,550 addresses were paid. 64 of them take half; the top 10 take 19.9%; the median recipient got
  $12.57 (`chain.concentration_last30`).
- The rewards market is professionally farmed.

## The rent before and after adverse selection

**Before adverse selection.** With a conservative bound on competition and quotes at 1/3 of the max spread
(`rent_curve.0.33`):
- $100k of capital earns $9,988 a day;
- $1M earns $27,883 a day.

**The simulation:**
- **Sample:** 148 markets from a 180-market stratified sample, all already quoted on both sides by others; 334 hours.
- **Across all categories:** rewards run 79–446% a year of capital, against market-making losses of 96–795% a year
  (`variant_table`).
- **Rewards switched off:** the quoter loses 70% a year (`no_reward_baseline`).

**The verdict hinges on competitors' share of the rewards.** Public books aggregate orders by price level, so they cannot
show how much resting size is two-sided farming.
- On a central estimate, all 12 all-category variants have an out-of-sample t between −0.62 and 0.71
  (`central_rewards_sensitivity`).
- Only the optimistic bound passes, with t 4.0–23.4 (`optimistic_rewards_sensitivity`). It assumes one-sided liquidity
  outside a 0.10–0.90 midpoint counts for nothing.

## Kalshi slow programmes

Programmes of a day or longer are configured at $121.6k a day. The 15-minute programmes are speed games and are
excluded.
- The marginal reward on 100 contracts is a median 314% a year before adverse selection (`kalshi.by_class_sample`).
- The simulated daily P&L was positive on 11 of 15 days, and all four variants survive false-discovery on the full
  sample.
- The out-of-sample half was decided by one partial day: −$193 on 10-14, mostly from same-day mention, rain and approval
  markets (`kalshi_sim.chosen_daily`).
- **LIP is open to US members only.** Polymarket's international venue excludes US persons, so no single account holds
  both rents.

## Holding rewards and favourite carry

**Holding rewards** (`holding`) pay 3.25% a year on mid-valued YES + NO. A complete set therefore earns it, which is
−0.55% a year against the savings rate. At least 339 markets in 41 events qualify; the scan was capped, so this is a
floor.

**Long-dated favourite carry as a maker** (`fav_carry`) used standalone binaries only: 2,934 of 17,717 entries.
- The chosen `7d|0.85-0.95` has an out-of-sample t of 1.25, so it is a no-go.
- Fills are adverse. At 7 days in the 0.95–0.995 band, filled bids won 73% of the time, against a 91% unconditional
  win rate.

## Late entry, capacity, variants

- **Late entry** (quotes centred on an hour-stale midpoint): it kept 16% on Polymarket and 377% on Kalshi
  (`late_entry`). Both are shares of a near-zero base.
- **Capacity:** the simulated Polymarket portfolio averaged $3,512 of capital, worth about $168 a year at its
  insignificant out-of-sample excess (`capacity`). A full-fill stress, in which any trade through the quote fills all of
  it, gives −79% out of sample.
- **Variants:** 253 in total (`variants_grand_total`).
  - Polymarket: 72 tested, plus 144 from a first pass and a naive family, plus 28 sensitivity runs.
  - Kalshi: 5.
  - Favourite carry: 4.

## Errors found and fixed

1. **First pass (disclosed, and its variants counted).** It quoted books with no competitor inside the band, where the
   midpoint is not a price, so it booked whole pools (t 5.1). Quoting is now restricted to markets others already quote
   on both sides, and never inside today's touch (`first_pass_disclosed`).
2. **Wrong rewards endpoint.** `/rewards/markets/multi` returns 100k rows, mostly with empty configs. The list that pays
   is `/rewards/markets/current`, and its total matches the chain to 96%.
3. **Scan cap.** The gamma scan stopped at its 2,000-page cap and missed 1,932 rewarded markets. They were filled by
   condition id.
4. **Polygon block time.** Blocks are about 1.5 s, not 2 s. One estimate produced a 14,963-block `getLogs` range, over
   Infura's 10k limit. Also, 188 of 678 RPC batches hit transient errors and were retried (`manifest.chain_rpc_log`).
5. **Deleted helpers.** An edit deleted the simulation helpers. They were restored, and all 30 tests pass.
6. **Unusable competition field.** The CLOB's `market_competitiveness` is not in reward-score units: half its values
   fall below the lower bound. It was not used.
7. **No historical reward rates.** Closed markets drop their reward rates, so the simulation uses today's
   (`manifest.closed_market_reward_check`).

## Kill criteria and what next

**Polymarket.** A paper quoter cannot observe its own reward share. The next step would be a pre-registered live
micro-test. **That is real money and needs the user's decision.**
- **Size and scope:** about $2k across 20 joinable markets, excluding same-day weather and intraday markets.
- **Quoting:** at 1/3 of the max spread and 5× the minimum size, with the volatility screen and hourly re-quotes, and no
  quotes in the last 24 h before a market ends.
- **Measurement:** read `/rewards/user/percentages` hourly and the 00:00 payout daily.
- **Kill rule:** stop after 14 days if rewards + spread + rebates − markouts fall below the savings rate, or if the
  realised share is at or below the conservative bound.

**Kalshi.** LIP scoring is linear in size, so a paper quoter is feasible.
- **Quoting:** 100 contracts on both best bids, in programmes of a day or longer, with hourly re-quotes and no quotes
  within 24 h of close.
- **Kill rule:** stop if the 30-day paper net is below the savings rate.
- **Account:** it needs a US-eligible account.

**Monitor.** Re-run the payout scan monthly. The rent is shrinking if payouts fall below $100k a day, or if the top 64
addresses take more than 60%.

## Coordinator's check

The payout series was recomputed from `raw/chain_payouts.json.gz`, independently of the script. Everything reproduces
exactly:
- 61 payout days, 2026-08-15 to 2026-10-14;
- a total of $7,716,350.78;
- last-7-day mean $173,064.96, first-7-day mean $94,324.91;
- in the last 30 days, 8,550 recipients and $4,456,609.07 paid; 64 addresses take half, the top 10 take 19.88%, and the
  median recipient got $12.57.

All payouts are in pUSD; no USDC.e payouts appear. A second payer, `0xdd8db71ce3be8d71ff148b2163d64da181a29e8b`, paid
small amounts on 3 days from 2026-10-11, probably a separate programme. It is not included in the totals.

## Files

- `scripts/pm_rewards_mm.py`
- `scripts/test_pm_rewards_mm.py` (30 tests pass)
- in this folder: `analysis.json`, `tables.md`, `manifest.json`, `book_entries.json` (`[]`)
- `collect_*.log` and `raw/` (both git-ignored)
