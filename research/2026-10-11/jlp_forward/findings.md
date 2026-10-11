# JLP's net-delta hedge, held forward — and what the hedge venue is worth — 2026-10-11

`jlp-hedged-house-lp` holds JLP (Jupiter perps' liquidity pool) and shorts its SOL/ETH/BTC delta. It is quoted at +2.5%
a year over the savings rate on $10M, about $248k. Its first kill gate is a live test of the hedge the venue's own
composition implies, because the backtest could only hedge with trailing regressions: jlp-info serves no composition
history. `scripts/jlp_forward.py` runs that test. While building it, the hedge venue turned out to matter as much as the
hedge model.

## Answer

- **The forward test is running.** Day 0 is 2026-10-11 00:02:34 UTC and the verdict is "accumulating (0 of 60 days)",
  with no flags. Day 60 falls around 2026-12-10.
- **The net delta, from jlp-info.** Per custody, the pool's AUM is linear in the oracle price, so its delta in tokens
  is `owned − locked + shortSizes / shortAvgPrice`:
  - longs post the token as collateral, and their locked size makes the pool short their exposure beyond it;
  - traders' shorts make the pool long.
  - On every snapshot the AUM-implied price and the short-PnL-implied price agree to ~3e-9. The two re-price each
    custody's aumUsd to within about $2.
- **Today's hedge** for $10M of JLP (2,143,429 JLP):

  | asset | net delta (tokens) | % of AUM | short | composition hedge ratio | backtest 60-day regression beta |
  |---|---:|---:|---:|---:|---:|
  | SOL | 3,574,433.6 | 43.8% | $4.382M | 0.438 | 0.415 |
  | ETH | 26,633.4 | 7.4% | $0.743M | 0.074 | 0.064 |
  | BTC | 1,323.5 | 12.2% | $1.223M | 0.122 | 0.209 |

  - The regression would short $0.87M more BTC and $0.23M less SOL.
  - The 30-day fee yield is 8.53%, against the 6.5% gate.
- **Hedging on Hyperliquid instead of Binance adds +1.5pp a year on capital for JLP and +1.3pp for GM SOL-USDC.** That
  is measured over the backtests' own test halves, with the same variants chosen and every re-measurement improving.

| | JLP (test 2025-06-27 → 2026-10-09) | GM SOL-USDC (test 2025-03-22 → 2026-10-10) |
|---|---|---|
| chosen variant (both venues) | roll60, always on | static, always on |
| excess, Binance (the book's basis) | +8.35% (t 3.80) | +10.79% (t 2.62) |
| excess, Hyperliquid | **+9.89% (t 4.21)** | **+12.05% (t 2.85)** |
| funding income per unit of vault | +0.76% → +2.64% a year | −0.07% → +1.38% a year |
| weekly re-measurement | +2.61% → +4.28% | +9.14% → +10.40% |
| daily 120-day re-measurement | +2.69% → +4.29% | +10.94% → +12.18% |

- **Why: Hyperliquid's funding sits at the formula rate far more often.** Over JLP's test half, the share of hours at
  0.00125% an hour (the rate paid while the premium sits inside the clamp; not a floor, since rates go below it):

  | asset | at the formula rate | below it (negative) | mean, Hyperliquid | Binance settlements at 0.01% | mean, Binance |
  |---|---:|---:|---:|---:|---:|
  | SOL | 41.2% | 53.8% (30.4%) | +2.86% | 18.1% | −0.25% |
  | ETH | 55.0% | 39.9% (14.6%) | +7.88% | 11.0% | +3.24% |
  | BTC | 53.6% | 41.8% (15.5%) | +7.56% | 12.7% | +4.08% |

  - Hyperliquid paid shorts more than Binance in every year for every coin.
  - The gap narrowed in 2026 so far: SOL +0.2% against −1.0%, ETH +5.9% against +2.0%, BTC +5.2% against +2.9%.
- **What it means for the book.**
  - The row's conservative quote (+2.5%) came from the least favourable re-measurement, +2.6% on Binance. On
    Hyperliquid that reading is +4.3%.
  - No re-quote is proposed now: the row is gated by the 60-day forward test, which records both venues. Decide the
    venue, and any re-quote, at day 60.
  - Margin on Hyperliquid is USDC rather than USDT. That is noted, not modelled.
  - This is the rent map's lesson applied to a hedge leg: place the short where longs pay the formula rate.

## The frozen rule

- **Position.** Hold $10M of JLP. At each daily snapshot, set each short to net delta per JLP × JLP held; the hedge set
  at row t earns from t to t+1.
- **Capital.** JLP plus one third of the gross short as margin.
- **Costs.**
  - The JLP round trip plus the hedge close, amortised over 365 days for the verdict; the 60-day amortisation and the
    before-one-offs excess are reported beside it.
  - Binance VIP0 taker on the notional rebalanced.
  - Actual Binance funding between snapshots, with Hyperliquid as a second column.
- **Verdict.**
  - Kill at 60 days if the excess over the savings rate is below +1% a year. Promote above +2.5% with Newey–West
    t > 2.
  - Immediate kill if the 30-day fee yield falls below 6.5%, or if the rolling 14-day hedged sigma stays above 0.5% for
    15 consecutive days.
  - A single window above 0.5% is a warning. One tail day sits in at most 14 windows, so it cannot reach the kill
    alone.
  - Review flags: AUM limit, custody set, an unhedged custody, or the DEX price more than 1% from NAV.
- **Revisions.** One revision, dated 2026-10-11, was decided before any scored period. It recorded:
  - the 365-day amortisation, and the 15-day sigma run (amended from 14, which a single tail day could still reach);
  - the hash replaced (`6dfd4a88dece6013`) and the one row written under it.
  - Any undocumented edit is flagged.
- **Side by side.** The backtest's roll60 regression hedge runs on the same rows, so the test also says which hedge
  model is right.

## Checks

- An exact-fraction re-derivation of row 0 from the raw file matches every digit.
- The JLP supply equals the on-chain `getTokenSupply`.
- Converted at Kraken's USDT/USD, the Jupiter oracle sits within 0.1–0.7bp of the Binance index. The raw −9bp gap is
  the USDT discount, not stale data.
- The regression reproduces house_vaults' `last_rolling_betas` to 4.8e-9.
- The simulator equals `house_vaults.simulate_hedge` to 1e-9. Both Binance backtests reproduce `analysis.json` exactly.
- Hyperliquid's funding history matches the repo's perp_history store exactly over the 8,971 hours both hold.
- An independent recomputation of JLP's funding gap gives +1.84pp a year per unit of vault, against the protocol's
  +1.87pp.

## Errors found in the worker's own work (all fixed)

1. A funding settlement published just after a snapshot would have fallen in no period. The snapshot now looks back 2
   hours.
2. One failed Hyperliquid fetch would have nulled the whole column. Now only the affected periods drop out.
3. The uniform −9bp oracle gap was first read as staleness; it is USDT/USD, which each row now records.
4. Stale DefiLlama data would have fed the fee gate silently. It now flags after 3 days.
5. The by-year funding profiles annualised per row × 8,760, which overstated Hyperliquid's 8-hourly 2023 rows.
6. The per-asset funding split first ran over the whole history instead of restarting at the test half.
7. Two wrong test expectations; the code was right.

## Open issues

- jlp-info cannot show an exploit or a fee-split change. AUM-limit, custody, unhedged-custody, depeg, stale-fee and
  rule-hash changes are flagged automatically.
- The NAV comes from Jupiter's API; only the supply is verified on chain.
- The regression column needs house_vaults' local raw files (gitignored).
- `house_vaults.collect_binance` stores the still-open last hourly bar as if closed. This does not affect its published
  numbers.

## Coordinator's check

- **Net deltas from the raw snapshot.** From `raw/2026-10-11/jlp_info_000233Z.json` with exact fractions, using
  owned − locked + globalShortSizes / globalShortAveragePrice:
  - SOL **3,574,433.6268**, ETH **26,633.3849**, WBTC **1,323.4953**.
  - These match the ledger row.
- **Hyperliquid SOL funding from the raw cache.** From `raw/hl_history/funding_SOL.json.gz` over 2025-06-27 →
  2026-10-09:
  - 11,280 hours: **41.2%** at the formula rate, **53.8%** below it, **30.4%** negative;
  - mean **+2.87%** a year.
  - The table has +2.86%.
