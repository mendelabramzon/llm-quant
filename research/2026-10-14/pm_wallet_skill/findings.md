# Copying Polymarket wallets an hour late: skill exists, but it is realized in minutes (2026-10-14)

**Verdict: no-go. `book_entries.json` is `[]`.** A few big sports bettors do have persistent skill at their own fills.
They realise it within minutes, so an hour-late copier pays for the move plus the spread.

The protocol picked `mk1d|t1_top300|nonsports|min1000|hold`, which was positive in sample on only 4 signals.
- Out of sample it had 55 signals at −5.6% each: HAC t −1.11, rank 43 of 72, deflated Sharpe 0.02 (`protocol`,
  `chosen`).
- No variant survives the one-sided false-discovery test.

Numbers are from `analysis.json` (key in brackets), produced by `scripts/pm_wallet_skill.py`. Tables are in `tables.md`.

## Mechanism and counterparty

The hypothesis was that informed wallets are paid by fans, and that prices absorb their trades slowly. Neither holds:
- **Who is skilled:** high-volume sports bettors.
- **When the edge arrives:** at once. For the top formation wallets, the +1h markout is most of the resolution edge.
- **How they trade:** their median hold is 0 days, i.e. in-play (`skilled_wallets_top50`).

An hour later the market maker has repriced, so the follower is the one paying the rent.

## Headline numbers

**The data, on the event-complete design** (`sample`):
- 1,102 events and 5,058 markets: the 3,655-market draw plus the missing members of its events, minus events with more
  than 10 members;
- 1.37M taker trades of at least $50;
- 178,932 wallets.

**On the market sample, skill is at the chance level** (`persistence`):
- 2.48% of 9,971 ranked wallets have a formation t of 2 or more; chance alone gives 2.3%.
- The Spearman correlation of formation t with test t is 0.048, over 1,489 wallets.
- Out of sample, the formation top 250 earn +0.9% per $ (t 0.17), and the bottom 100 earn +9.8% (t 1.45).

**Full trading histories show weak real persistence** (`hist_persistence`). This is stage 2: 2,488 wallets, scored on
standalone markets only.
- Spearman 0.118.
- Ranked by formation t, out of sample: the top 250 earn +4.91% per $ (t 2.80), the top 100 +6.39% (t 2.44), and the
  bottom 100 −10.7%.
- These wallets are 89–97% sports, with about 100–120 markets and $1–2M of volume each
  (`hist_top_wallets_profile.json`).

**Copying everyone at +1h loses** 9.9% per signal out of sample (t −3.26) (`baselines_1h`):
- sports signals lose 13.2% (t −3.42);
- non-sports signals make +1.3% (t 0.39).

**Following the stage-2 selection** (`secondary_hist`):
- The chosen variant has an out-of-sample t of −2.72, with no BH survivors.
- Non-sports variants were positive out of sample (best t 2.10) but negative in sample.

## How the edge decays with delay

Return per signal after spread and fee, on the same signals at every delay (`decay`, `secondary_hist.decay_*`):

| wallets (signals) | own fill | +5m | +1h | +1d |
|---|---:|---:|---:|---:|
| all (65,504) | −0.25% | −1.72% | −2.47% | −4.91% |
| full-history top 20 (157) | +6.65% | +1.14% | +1.81% | −1.71% |
| full-history top 100 (335) | −0.60% | −5.64% | −8.52% | −9.84% |

Most of the edge is gone within five minutes.

## Capacity and $/yr

- **Size per signal:** the smaller of the live touch depth and the leader's size. The median is $208, about 4% of the
  same-side flow within an hour either way.
- **Scale:** about 408 signals a year in the universe, on $4.4k of average capital.
- **Result:** the capacity-weighted point estimate is +$7.2k a year, but the protocol series is negative, so the stated
  figure is **$0 a year over SSR** (`capacity`).

## Variants

There are 187 per run:
- 72 pre-registered at +1h;
- 7 baselines;
- 72 at +1d (reported only);
- 36 stage-2.

The final code ran on three market sets. Six earlier runs were superseded by the fixes below (`variants_tried`).

## Errors found and fixed

1. **Volume-selection bias** (from the coordinator's note).
   - Neg-risk members of the $50k–$5M draw resolved YES 2.5–3.0pp above their mid-life price.
   - Event-complete sampling, weighted 1/P(event), brings the gap to −1.3pp (s.e. 0.8), and the all-taker formation
     edge from +1.78% to +0.08% per $ (`bias_comparison`).
   - Events with more than 10 members were dropped for cost: 1,547 events, containing 2,409 drawn markets.
2. **Degenerate clustered t.** A wallet that wins every trade has zero residuals and an infinite t. Before the fix, the
   top t was 4.2M, 10.7% of wallets looked significant, and Spearman read 0.17. The variance is now floored at the
   binomial variance under fair pricing, with tests.
3. **Misaligned marks.** Hourly points are stamped seconds after the hour, so "+1h" read a price 0–60 minutes after the
   signal. The fix moved the all-wallet follower from −7.0% to −12.6% per signal.
4. **Stage-2 bias.** The full histories rest on the $10k-filtered universe, so stage 2 is scored on standalone markets
   only. Including set members inflates the top-50 t from 2.0 to 7.2 (`hist_persistence_incl_sets_biased`).
5. **Disclosure.** Stage 2 was added after a dry run on 805 markets. It is secondary and never decides the go.

## Kill criteria and what next

Revive this only through a pre-registered forward test that clears all of:
- copy non-sports wallets selected on full history, at +1h;
- skip any signal whose price has moved more than 5c from the leader's fill;
- beat SSR after costs, with t ≥ 2, over at least 300 signals.

To collect next:
- maker fills (`takerOnly=false`);
- the 59 histories truncated at the cap;
- outcomes for the 277k markets outside the universe (12% of these wallets' dollars);
- the 1,547 large events;
- minute-level prices, to measure the five-minute decay directly.

## Coordinator's check

The primary sample was recounted from `raw/trades/*/*.json.gz`. Event membership comes from the script's
`event_members()`; the rows, wallets and the after-close cut were counted independently:
- 5,058 markets in 1,102 events (374 members have no trades file, because none of their trades reach $50);
- 1,365,508 trades and 178,932 wallets;
- 0 malformed rows, and 146 trades after the close excluded.

All of these match `sample` exactly.

## Files

- `scripts/pm_wallet_skill.py`
- `scripts/test_pm_wallet_skill.py` (30 tests pass)
- in this folder:
  - `analysis.json` (primary);
  - `analysis_events_sampled_only.json` and `analysis_volume_sample.json` (the bias comparisons);
  - `tables.md`, `manifest.json`, `book_entries.json` (`[]`);
  - `sample.json`, `hist_top_wallets_profile.json`;
  - `raw/` (git-ignored).
