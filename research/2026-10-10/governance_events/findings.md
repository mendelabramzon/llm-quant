# Governance proposals read by an LLM, against the perp a patient trader would use — 2026-10-10

The question: when a DAO votes on Snapshot to put cash in holders' hands or take supply away (fee switches, buybacks,
burns, revenue shares, emission cuts) — or the reverse (new emissions, treasury token sales, large token-paid programs) —
does the token move over the days around the vote in a way a trader who reads proposals, not mempools, could capture?
This is the loop's first study in which the qualitative step is an LLM reading text and the quantitative step is code
that never sees a label change. `scripts/governance_events.py` collects every proposal of 97 Snapshot spaces whose token
has a Binance USDⓈ-M perpetual, screens them by keyword, has an LLM label each candidate against `criteria.md` (written
before any label, frozen with a hash before any price path), and prices a pair trade around each event from 4h Binance
klines and funding. Numbers are in `analysis.json` (per-event values in `events_priced.jsonl`), tables in `tables.md`,
the labeling audit in `labels.jsonl`, `label_agreement.json` and `label_batches/`.

**Verdict: no-go, no book entry.** In sample (2021 to mid-2024), proposals labelled VALUE_UP were followed by +7.24%
against an equal-weight basket from publication to a week after the vote (median +3.08%, 32 tokens, survives BH). Out of
sample (from 2024-07-01) the effect is gone (+0.07%), and the pre-registered trade lost money.

## What was measured

- **Proposals.** 19,774 from 99 spaces; two spaces dropped after reading their proposals (movedao.eth predates the MOVE
  token; celernetwork.eth is chat), 13 candidate spaces dropped before download for symbol collisions or NFT-weighted
  voting (veLIT vs Litentry, Bankless BANK vs Lorenzo, Forefront FF vs Falcon, ...). Kept: created 2021-01-01 to
  2026-10-01, closed, at least 3 votes, not flagged, PancakeSwap only from its eight team addresses (anyone can post
  there; 3,144 phishing and chat proposals dropped), and only where the token's perp traded from 8 days before
  publication to 8 days after the vote: **10,183 proposals**.
- **Screen.** Value keywords in the title or first 4,000 characters (fee switch, buyback, burn, revenue/fee share,
  staking rewards, emissions, inflation, tokenomics, token sale, OTC, max supply, treasury diversification, ...); generic
  words (treasury, grant, incentive, rewards, fees, vesting, unlock, ...) only in titles; 463 routine titles (gauge, farm,
  pool and market additions, listings, risk parameters) excluded unless the title also names a value term: **2,322 hits
  plus 200 random non-hits as blind controls, on 83 tokens**.
- **Labels.** Each of the 2,522 packets (title, choices, first 1,500 characters; no price, outcome or screen flag) was
  labelled VALUE_UP / VALUE_DOWN / NEUTRAL, with a surprise flag, binding/signal and confidence, by fresh LLM passes: 24
  parallel agents of the same model, one prompt (`label_batches/LABELER_PROMPT.md`), batches in token and time order,
  4.85M tokens. Frozen 2026-10-10 12:26:08 UTC (sha256 `d71f689d…`): **178 VALUE_UP, 169 VALUE_DOWN, 2,175 NEUTRAL**. A
  shuffled 10% (252) was relabelled blind by two further passes.
- **Events.** Same token, label and UTC day merged: **341 value events (174 up, 167 down) on 63 tokens**, 168 before the
  cutoff 2024-07-01 (fixed at the freeze from label dates only) and 173 after.
- **Abnormal return.** Log return between the last 4h closes at or before each anchor, less BTC's and less the
  equal-weight mean of every other priced token (at least 5). Windows: 7 days before publication, publication +1 day,
  the vote, end +1/+3/+7 days, publication to end +7 days.
- **Trade.** Long the VALUE_UP perp (short the VALUE_DOWN perp) against the opposite BTC perp, decided at vote start +1
  day or vote end +1 hour and filled at the next 4h close, closed at the end or end +1/+3/+7 days. Simple returns,
  Binance funding, 5bp taker on four fills, each token's impact at **$25k a leg from its live book** (median pair round
  trip 78bp; 0.63–0.65% on the events traded), and the savings rate (3.80%) on the notional for the days held. 30
  tradable variants (7 windows × 3 sides × all/passed; "passed" is not tradable before the vote ends).
- **Placebo:** the same token and window shape 15–30 days away, skipped if any labelled value event of that token falls
  inside it (±7 days). **Protocol:** the variant with the best in-sample excess-over-placebo t (at least 15 events) is
  tested once after the cutoff; t by event week; Benjamini–Hochberg at q = 0.10; deflated Sharpe. The go rule was
  written to `manifest.json` (`decision_rule`) before any return was computed.

## What it found

**The pre-registered trade failed.** The in-sample choice was long VALUE_UP / short VALUE_DOWN on passed votes, entered an
hour after the vote ends and held 7 days: +4.42% a trade against a placebo of −0.79% (148 events, excess t 2.76). Out of
sample it lost **−0.94% a trade** (158 events, 85 weeks) against a placebo of −1.37%: excess +0.43%, t 0.36; event-week
t of the P&L −1.20; hit rate 47%; −1.01% after the savings rate; −2.05% at $100k a leg; deflated Sharpe 0.00. None of the
30 variants survives BH in sample or out of sample.

| abnormal return vs the basket, publication → end +7d | in sample (2021 – 2024-06) | out of sample (2024-07 – 2026-09) |
|---|---:|---:|
| VALUE_UP: n, mean (event-week t) | 83, **+7.24%** (3.37) | 91, **+0.07%** (0.33) |
| VALUE_UP: median, 5%-trimmed mean, hit rate | +3.08%, +5.11%, 64% | −0.32%, −0.26%, 46% |
| VALUE_UP placebo | +1.21% (n 130) | −0.29% (n 160) |
| VALUE_DOWN: n, mean (t), median | 85, −1.50% (−0.64), −3.05% | 82, −0.08% (0.06), −1.96% |
| NEUTRAL: n, mean (t), median | 1,159, +0.42% (0.39), −1.05% | 616, +2.14% (3.69), +0.77% |
| keyword-rule VALUE_UP: n, mean (t) | 156, +2.15% (1.64) | 163, +0.89% (0.48) |

**The drift was real, and it is gone.** Before mid-2024, proposals the LLM called value-raising were followed by +7.2%
against the basket from publication to a week after the vote. This is not one token: 32 tokens, median +3.1%, trimmed
mean +5.1%, three cells surviving BH (vote, end +7d, publication → end +7d). By year of publication the median was +5.1%
(2021, n 9), +2.8% (2022), +2.3% (2023), +2.5% (2024), **−1.6% (2025, n 50)** and +2.3% (2026, n 27, t 0.97). Out of
sample no cell of the abnormal-return table survives BH. In sample the effect sat in first appearances (+8.6%, t 3.36,
against +2.3% for continuations) and in contested votes (final margin under 80%: +17.9%, n 18); out of sample those were
+0.6% and +3.9% (n 14, t 1.37). Those splits were read after the halves, so they are description, not a test.

**Dilution never paid a short.** VALUE_DOWN medians are negative in both halves (−3.1%, −2.0%), but the means are near
zero. Shorting them against BTC earns what shorting the same coins on other dates earns: +2.49% a trade out of sample on
the vote-start window, against a placebo of +2.23%. That is alt-coins bleeding against BTC, not governance.

**The Snapshot date is late for the events that matter.** Uniswap's "Activate Uniswap Protocol Governance" (Snapshot
2024-03-01) followed a forum post a week earlier; from Snapshot creation to a week after the vote UNI did −4.8% against
the basket (+25.4% in the vote, −30.2% in the week after). "UNIfication" (Snapshot 2025-11-18, forum post days before)
did −14.6%. Ethena's fee switch (2026-08-27) ran +28.8% in the week *before* its Snapshot. The wins came from smaller
tokens and memecoin seasons: the FLOKI burn of 190.9B tokens (+140% against the basket, March 2024), Curve's 2021 "burn
some CRV" poll (+54%), the MANA 10% burn poll (+46%, November 2021); the 2022 Uniswap fee-switch temperature check
returned +15.6%. All of these fall in the in-sample regime.

## Size

Thin even had it held. The tokens the chosen variant traded (36 with a live book, of 44) held a median **$9.9k within
25bp** on the thinner side and $31.6k within 50bp; impact was 25bp at $25k, 40bp at $50k and 65bp at $100k a leg; median
24h volume $4.8M. At the in-sample +4.4% a trade, about 70 value events a year at $25k would be worth about $75k a year
gross. Out of sample it is negative.

## Verdict

**No-go; no book entry.** The edge existed from 2021 to mid-2024 and did not survive the test the protocol fixed in
advance. There are no kill criteria because nothing enters the book. The way back is a re-test dated by the forum post,
not the Snapshot vote, under the same frozen-label protocol.

## What the labelling step taught about an LLM as the qual stage

- **It is consistent.** The blind second reading agreed on 249 of 252 packets (98.8%, Cohen's kappa 0.95) and on 36 of 38
  value labels. All three disagreements are materiality calls (a 4M ACX reward renewal, a 20% integrator fee share, a
  $1.3M covered-call vault). The surprise flag agreed on 34 of 38 value labels. The binding/signal field agreed on only
  73% of all packets, because it leans on general knowledge of each DAO's process.
- **A keyword screen alone is nearly useless as a classifier and good as a net.** The keyword rule agrees with the LLM on
  57% of candidates (kappa 0.09). Of 340 keyword-UP proposals only 87 were value-up: 26% precision, finding 49% of the
  LLM's 178. Keyword-DOWN precision is 8%. As a recall net it works: of 200 random proposals it missed, the LLM found one
  value event (SSV's "Incentivized Mainnet Program", missed because `incentive` does not match "incentivized"), which
  projects to about 40 misses (95% bound about 220) among 7,861 non-hits, against 346 found.
- **Reading sharpened the signal it had.** In sample the LLM's VALUE_UP events earned +7.2% against +2.2% for the keyword
  rule's. Out of sample both are zero. Better labels do not rescue a dead effect.
- **The rubric decided more than the reader.** Most disagreements a second reader would raise trace to rubric choices:
  revenue to the DAO treasury is not holder cash flow (which made Balancer's 2021 protocol-fee activation, Aave
  reserve-factor increases and most fee changes NEUTRAL, while the 2022–23 Uniswap fee-switch pilots got VALUE_UP at
  confidence 0.5); there is no materiality threshold for treasury token sales (a $200k AAVE OTC swap came out NEUTRAL, a
  $3M one VALUE_DOWN); the baseline for renewals is unclear (an expiring incentive program, renewed, reads as dilution
  against expiry and as a cut against the running rate); Decentraland grant freezes were NEUTRAL in one batch and
  VALUE_UP in the next (batch conventions drift, and a shuffled spot check is too small to see it); truncation at 1,500
  characters hides the number in about one hard case in five (the IoTeX burn split, Balancer BIP-371).
- **Batches leak future text.** Time-ordered batches let a labeller see a later proposal implementing an earlier one; one
  labeller said so and declined to use it. Labels are about what a proposal would do, so this cannot leak a price, but it
  is a look-ahead channel for the surprise flag.
- **Cost.** About 2,000 tokens a proposal: 4.85M tokens for 2,522 packets plus the spot checks.

## What this cannot see

- **Forum dates.** The real announcement is often a forum post or a post on X days before Snapshot; this study prices the
  Snapshot date, which is what made the marquee events look like continuations.
- **On-chain votes.** Binding Governor/Tally votes are not here. "Passed" means the Snapshot tally, and decisiveness is
  proxied by the final margin, because the API has no intermediate tally.
- **Historical books.** Costs come from today's books; the 2021–22 books for these tokens differed.
- **Tokens with no perp.** Tokens never listed on Binance USDⓈ-M are excluded (GNO, OHM, AURA, MNT, ...). Delisted perps
  are kept up to their last traded bar.
- **The basket's own drift.** The equal-weight basket includes small caps that crashed, so it drifts down; NEUTRAL
  proposals beat it by +2.1% out of sample. The placebo, not the basket, is the control the tests use.

## What went wrong and was fixed

1. Binance keeps serving delisted USDⓈ-M contracts as flat, zero-volume bars at the settlement price: BALUSDT stopped
   trading 2025-04-14 and still had bars on 2026-10-10; 22 tokens, 50,934 bars. Every post-delisting event would have
   scored a flat token against a moving BTC. Untraded bars are now missing, pinned by a test.
2. A 10-vote floor would have dropped 946 of 971 Synthetix proposals (the Spartan Council votes with about 8); the floor
   is now 3.
3. "Do nothing" was not read as a status-quo choice, so failed votes counted as passed. Fixed and pinned by a test.
4. Snapshot records a vote start up to 40 hours *before* creation on 804 of 2,522 candidates; "start + 1 day" could then
   trade a proposal nobody could see yet. The start anchor is clamped to publication, pinned by a test.
5. Screen v1 matched Aave per-asset "supply caps", 290 Decentraland grant boilerplates ("vesting") and generic
   "diversify"; it was tightened before any label (`routine()`, generic terms in titles only).
6. The space map: 13 symbol collisions removed, two spaces dropped after reading, PancakeSwap's open-posting spam
   filtered by author.
7. Analysis output: `tables.md` printed the keyword section before the LLM one (sorted JSON keys), and `analysis.json`
   was 5.2 MB of per-trade lists; both fixed, neither changed a number. The by-year, in/out conditional and
   BH-over-cells tables were added after the first run had been read, and are flagged in `manifest.json` `post_hoc`.

## What next

1. **Date events by the forum post** (Discourse APIs: gov.uniswap.org, governance.aave.com, research.lido.fi,
   forum.arbitrum.foundation, ...), keep the same frozen labels and protocol, and test whether the move has shifted to
   the announcement. The marquee examples say it has.
2. **Fix the three rubric gaps before any relabel** (treasury revenue versus holder cash flow, a sale-materiality
   threshold, the renewal baseline); then relabel a 10% sample across batch boundaries to measure the convention drift
   the shuffled spot check cannot see.
3. **Keep the screen, drop the keyword classifier.** Widen the stems (`incentiv`) and spend the reading budget on recall.

## Coordinator's check (2026-10-10)

`labels.jsonl` holds 2,522 labels (178 VALUE_UP, 169 VALUE_DOWN, 2,175 NEUTRAL) and hashes to `d71f689d…`, the hash
recorded at the freeze. The order of operations in `manifest.json`: label export 11:48:24, labelling 11:48:36–12:26:00,
decision rule written 11:55:07, freeze 12:26:08, first analysis 12:26:20. Klines and funding were downloaded 11:36–11:52,
before the freeze; the manifest states that only bar times and volumes were read then (to decide which proposals had a
tradable perp around them) and that no return was computed, and the labellers' packets carry no price. The protocol held.
The labelling cost (4.85M tokens of sub-agents for one study) is the number to plan the next qual stage around.
