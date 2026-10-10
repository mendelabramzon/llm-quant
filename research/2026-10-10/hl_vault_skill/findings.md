# Hyperliquid vaults: is there manager skill you can rent? — 2026-10-10

**Answer: no.** Picking vaults by their public track record does not persist out of sample among vaults big enough to
deposit in. "Copy the leaderboard" is dead. The average vault loses against the savings rate.

One rule fixed in advance passed the hashed go rule on paper:

- **The rule:** hold the largest tenth of vaults by equity, weighted by equity.
- **The pass:** +44.4% a year over the savings rate out of sample, t 3.59.
- **Why it is declined:** it was the least-bad of 56 variants that all lost in sample. Over all 28 months it made
  −77.7% a year. Its test-half gain is explained by the size of BTC's monthly moves, not by skill.

It is written up only as a declined watch row (`go: false`) with a forward test.

| question | verdict | numbers |
|---|---|---|
| Do track records persist among vaults ≥ $100k? | **no** | out-of-sample rank ICs: 3-month return −0.018, 6-month −0.046, Sharpe −0.038, drawdown −0.008 |
| Copy the leaderboard (top decile by 3-month return, equal weight) | **dead** | −157.6%/yr in sample; +11.9% out of sample (t 0.39); +29.0% if you only see today's open vaults |
| Pre-committed winner: largest decile by equity, equity-weighted | **passed on paper; declined** | out of sample +44.4%/yr (t 3.59, BH p 0.005). In sample −105.1%; 28 months −77.7%/yr; alpha after the size of BTC's move −4.2% (t −0.27) |
| Average vault vs the savings rate | **loses** | equal-weight ≥ $10k: −71.9%/yr in sample, −21.5% out. Stats file alone: user vaults −$69.7M lifetime, 22.7% ended positive |
| Skill, beta or short volatility? | **none of these for the winners** | big-vault winners are *long* volatility (\|BTC\| loading t 2.52, R² 0.50); small vaults are long beta (BTC 0.37, t 2.70) |

## Data and method

- **Universe and fetch.** The stats file (`stats-data.hyperliquid.xyz/Mainnet/vaults`) lists 9,477 vaults, 6,387 of
  them closed. `vaultDetails` was fetched for 3,214 core vaults: equity today ≥ $10k, or a coarse lifetime P&L point
  ≥ $1k, plus the HLP family. A seeded 10% random sample (626) of the other 6,263 was fetched as well. That was 3,842
  calls at 1.25 s spacing, with 0 throttled and 0 failures. All 8 HLP-family vaults are tagged and excluded.
- **Returns.** The allTime grid is regular per vault: 7 days for 2,073 core vaults, 14 days for 1,105.
  - Step returns are Modified Dietz on account value and P&L, so net of flows.
  - A closing step earns on its starting equity, and closures stay in the record.
  - The returns chain into a time-weighted index per vault.
- **Decisions and holding.** Decisions are monthly at 00:00 UTC on the 1st.
  - Signals use only grid points at or before the decision.
  - Holding runs from each vault's first point at or after the decision to its first point at or after the next one: a
    median 4.0 days later, at most 14.
  - The profit share is simulated exactly in a follower account: 10% above the depositor's cost basis, paid pro rata
    on withdrawal.
- **Variants.** 56 were fixed before any forward return was computed (`precommit.json`, sha256 af4ad904…): 7 signals ×
  top quintile or decile × equal or equity weight × ≥ $10k or ≥ $100k.
  - leaderFraction, follower counts and allowDeposits exist only as of today, so they cannot be signals. They are
    recorded as API gaps.
- **Calendar.** The pre-committed rule starts it at the first month with ≥ 10 eligible $100k vaults. Choose on
  2025-01 → 2025-10, test once on 2025-11 → 2026-09.
- **Independent checks (worker):**
  - The stats file's lifetime P&L matches the `vaultDetails` P&L to $1 for all 2,293 closed vaults. For open vaults,
    79.6% match to $1 and 91.4% within 1% (fetched minutes apart).
  - Followers' own P&L against the index over the same dates: 1,210 followers with ≥ 60 days (Spearman 0.911, median
    gap −0.02pp, median |gap| 2.25pp), and 390 followers with 7–60 days (Spearman 0.908, median |gap| 1.13pp).

## Results, in and out of sample

**Persistence.**

- **Vaults ≥ $100k:** every return-based IC is about zero or negative out of sample (table above).
- **Vaults ≥ $10k:** ICs are positive in both halves (Sharpe 0.091, t 3.80, then 0.116, t 2.92). The quintiles show
  this is losers continuing to lose: the lowest-Sharpe fifth lost −10.0% a month in sample and −3.7% out.
- **No track-record portfolio helps a depositor:** even the top Sharpe quintile lost −5.2% a month in sample.
  Equal-weight top Sharpe quintile ≥ $100k: −50.8%/yr in sample, −16.1% out.

**The 56 variants.**

- All lost in sample, from −268% to −31% a year. The pick, `size|q10|cw|u100k`, had in-sample Sharpe −0.87 and
  deflated Sharpe 0.055.
- Out of sample it ranked 1st of 56: +44.4% net over the savings rate actually paid, +44.6% over SSR 3.80%, +49.6%
  gross.
  - Block-bootstrap 95% interval for the monthly mean: +1.8% to +6.0%. Deflated Sharpe 0.707.
  - BH survivors out of sample: 7 size variants plus `ret6|q10|ew|u10k`.
- The pass is robust to execution and data choices:

| check | out-of-sample net excess |
|---|---|
| entering one more grid step late | +41.4% (t 2.85) |
| 10bp friction | +43.9% |
| 10% fee on every positive month | +39.6% |
| conservative flow timing | +43.1% (t 3.45) |
| only vaults taking deposits today | +41.6% (t 1.84) |

**Why it is declined** (post-hoc, after seeing the result):

- **Regime flip:**
  - Before the calendar (2024-06 → 12) the same rule made −19.2% a month (worst month −82.9%).
  - In the choose half it held Sifu, a ~$10M vault whose lifetime index fell 99%.
  - The test half's winners are different managers: 5 distinct vaults held in sample, 12 out, 4 in both.
- **No alpha in the test half:** gross alpha −2.0%/yr (t −0.12). The portfolio earned in months with big BTC moves
  either way: BTC −21% → +9.5%, BTC +19.7% → +14.1%. Equity-weighted big-vault market: \|BTC\| t 3.99, R² 0.77.
- **Concentration:**
  - 3.3 vaults held on average.
  - drkmttr gave 41% of the test-half gain in 3 months; its August was +97.5%. Without it: +24.0% (t 3.46).
  - Growi HF gave 22%, Systemic HyperGrowth 17%.

## Survivorship bias

- **Across the 56 variants:** rerunning them on vaults open today adds +3.05pp a year on average (median +3.65pp, out
  of sample +2.43pp).
- **Copy the leaderboard, out of sample:** +11.9% becomes +29.0%.
- **Pooled monthly returns (≥ $10k):** survivors −0.83% a month, all vaults −1.76%, later-closed vaults −5.73%. 3.6% of
  eligible vault-months saw the vault close inside the month.
- **The pre-filter loses nothing measurable:** 14 of the 626 sampled excluded vaults ever held $10k and 4 held $100k,
  but none was eligible at a decision date.

## Capacity, as of 2026-10-01

- The rule holds 6 vaults with $46.4M of equity.
- Room before each leader's 5% floor is $102.0M; capped at 10% of each vault it is $3.29M.
- Growi HF, the steadiest holding, is at its floor (about $6k of room).
- Turnover is 22.2% a month one-sided. The profit share cost 2.36% of capital a year.

## Forward test (declined watch row in `book_entries.json`, `go: false`)

No capital unless both hold over 12 forward months:

- net excess over the savings rate > +2% a year with t > 2;
- alpha after BTC and \|BTC\| > 0 with t > 2.

Retire if any of these happen:

- trailing 6-month net excess turns negative;
- capped room falls below $1M;
- a selected vault loses > 20% inside a month and closes;
- one vault holds > 50% of the weight for 3 months.

The tails are large: drkmttr moved −44% and +58% in single weeks.

## What failed, and errors found

- **Failed: every track-record signal for investable vaults.** That includes "money follows winners" (3-month flows),
  with a negative IC in sample (−0.089, t −2.61) and about zero out.
- **Error: Modified Dietz blow-ups.** It exploded when money arrived, traded and left inside one 1–2-week step: +47,884%
  on a $2.4k vault. Those steps now use a conservative denominator: 1,100 core steps, 26 inside eligible holding
  windows. Pinned by a test.
- **Error: index zeroing.** A −100% clip zeroed an index forever. It is now a −99.99% floor (184 steps). Pinned by a
  test.
- **Error: the follower check is weak for performance-chased vaults.** Followers top up during run-ups, which made
  drkmttr look like a mismatch (+21% against +69%). Single-deposit followers match.
- **Protocol lesson.** The go rule had no requirement that the in-sample choice be positive, and no deflated-Sharpe
  floor, so a least-bad pick could pass on paper. Future go rules should require a positive in-sample choice.

## Next

- Run the forward test monthly (`collect`, then `analyze`; about 1 hour of paced calls).
- Add an in-sample floor to go rules built on `backtest.choose_then_test`.
- Lead only: big systematic vaults give long-volatility exposure without paying option premia. Compare with the
  volatility-premium series before reading anything into it.

## Coordinator's check

Recomputed from `raw/vaults_stats.json.gz` alone, without the worker's code: summing each user vault's last allTime P&L
point (HLP parent and 7 children excluded) gives **−$69.7M across 9,469 vaults, 22.7% positive**. That matches the note.

Files: `scripts/hl_vault_skill.py`, `scripts/test_hl_vault_skill.py` (23 tests), `analysis.json`, `tables.md`,
`manifest.json`, `precommit.json`, `book_entries.json`, `raw/` (20 MB).
