# Building the best onchain research analysis system — roadmap

This is the standing plan for `llm-quant`. The goal (see the research memo and memory) is a closed qual↔quant loop:
the LLM reads evidence, proposes mechanisms, and writes the infrastructure; deterministic code turns mechanisms into
reusable detectors and tests; the human steers. The metric we optimise is **time-to-verified-insight**: how fast a raw
signal becomes a true, capacity-aware, reproducible claim and then a reusable detector — not classification coverage.

## Session log — 2026-10-23 (the last two hours; repo trimmed to scripts and reports)

The report is [`research/2026-10-23/report.md`](research/2026-10-23/report.md). The window ran 13:09–15:09 UTC and was
a quiet, risk-off US open. It covered Ethereum, nine EVM chains, Hyperliquid, Binance/Bybit perps (new
`scripts/cex_window.py`) and the news. **Nothing enters the book.**

- **Negative-funding long: no-go.** `scripts/neg_funding_long.py` tested it, with findings in
  `research/2026-10-23/neg_funding_long/findings.md`.
  - Out of sample: +15% funding against −11% price per trade, median −3.2%, t 0.96, and 0 of 32 variants survive BH.
  - The Binance–Bybit gap hedge loses in all 18 variants.
  - This pairs with the Oct 11 floor-carry no-go: funding paid by hedgers who cannot borrow spot is not a rent to the
    other side.
- **USDC/USDT basis reversion:** about 4bp a trade on about 5 trades a year, and recent trades lose. It goes on the
  watch list only.
- **Compound USDC:** 169bp over SSR, but only about $1M wide. The cross-chain dollar book is $19k a year.
- **Fixed:** `live_scan.py` priced wstETH NAV off STETH/USD, which faked a −63bp discount. It now prices off ETH.
- **Forward tests** ran for the first time since Oct 11. **The queue book returned `kill: criterion 4`** on proxy
  evidence: other owners' 0bp-limit CoW orders rested while the median cleared by 1–2bp. **Decide:** retire the row, or
  re-specify c4 with a clearance margin.
- **.gitignore** is now a whitelist for `research/` (reports and code only). 11,276 data files were untracked with
  `--cached`.

## Session log — 2026-10-14 (prediction markets: eight alpha hunts, all no-go, and a selection bias found)

Asked to "research what happens in polymarket and prediction markets in general". After a first plan aimed at the
industry, the user redirected: research should find new alpha strategies, not cover regulation. Eight history-tested
studies followed, each on the repo's protocol:
- choose before a cutoff, test once after it;
- price the executable version;
- enter an hour late at the later price;
- state $ a year over SSR at capacity.

Each study's findings has a coordinator's check recomputed from its raw files. **Nothing enters the book.** Every
`book_entries.json` is `[]`, so no approval commands are pending.

| study | what was tested | result |
|---|---|---|
| `pm_weather` | Kalshi and Polymarket temperature buckets against the NBM station forecast (6 cities, whole events) | **no-go**: the price beats the model everywhere (Brier 0.1196 vs 0.1327 on Kalshi the day before; gap t 4.6–16.3). When they disagree by more than 15pp, outcomes follow the price. A model+price blend is worse than the price |
| `pm_crypto_options` | strike, range and touch markets against Deribit-implied probabilities | **no-go**: the market has the lower Brier in all 5 families. Options overstate touches (realised/implied vol 0.67–0.78), so the market already prices the variance risk premium |
| `pm_sports_sharp` | pre-game soccer and tennis against de-vigged Pinnacle or average odds | **no-go**: Polymarket's kick-off Brier equals the closing consensus (0.19770 vs 0.19772); every role bias is under one-way costs |
| `pm_rewards_mm` | venue liquidity rents against an hourly re-quoting maker | **no-go**: Polymarket pays $173k a day on chain (64 addresses take half) and Kalshi LIP $221k a day. Simulated rewards of 79–446% a year are lost to adverse selection (fills mark −3.3c at 6h); the verdict hinges on competitors' unobservable reward share |
| `pm_parlays` | Kalshi combos and Polymarket Combos: the house edge and who collects it | **no-go**: Kalshi combos are 58% of contracts, and makers net 0.19% per $ risked (t 1.04). Polymarket incumbents earn +1.93% (t 3.80) but 0.03% in August |
| `pm_combos_maker` | a new Polymarket combo quoter pricing off leg midpoints, winning only below the incumbent | **no-go**: the pick lost out of sample (t −0.34). Cross-game 7+ legs at 1.4× fair is descriptive only ($767k a year point estimate, interval −$190k to +$1.72M, test count z 1.9993) |
| `pm_wallet_skill` | persistent wallet skill, copied an hour late | **no-go**: skill exists in a few big sports bettors, but it is realised within 5 minutes (in play). Copying everyone at +1h loses 9.9% a signal |
| `pm_structure_scan` | question templates, date and strike ladders, hourly momentum and reversal (1,351 variants) | **no-go**: ladder violations sit in dead books (110 of 120 entries had no trade on one leg); the best template tilt failed its pre-registered fresh-event confirmation |

**What the session established.**
1. **For slow participants these prices are efficient.** Polymarket and Kalshi prices already contain the public
   model:
   - the NWS blend for weather;
   - Deribit's surface, net of its variance premium, for crypto;
   - the sharp books' close for soccer.
   An outside model that does not beat the price's Brier before trading has nothing to sell.
2. **Skill exists, but it is fast.** The wallets with persistent edge are in-play sports bettors whose edge decays
   within minutes. That is the speed game the repo excludes.
3. **Rents exist and are farmed.** Combined, the venues pay about $0.4M a day in liquidity rewards. Polymarket combo
   makers took about $33k a day, with margins compressing from about 19% to 8–9% since August. In both, a slow or
   model-only entrant is adversely selected or loses to the winner's curse.
4. **A selection bias in the stored universe.** `research/2026-10-09/polymarket_history/raw/universe.json.gz` keeps
   markets with at least $10k of lifetime volume. Members of multi-outcome events that cross that line are mostly the
   ones that rallied toward winning. Five studies measured the bias, each against whole events:
   - the structure scan: weather +7.7pp → −1.1pp, futures +7.9pp → −0.8pp;
   - sports: +8.2pp;
   - weather: +2.5pp;
   - wallets: +2.5–3.0pp;
   - crypto ranges: 0.183 against 0.131.

   It would have produced false "go"s in at least three studies. It also explains most of the 2026-10-09
   "short-horizon favourites overpriced" result: out of sample, neg-risk members score −5.0% gross against −2.0% for
   standalone markets. A dated correction is appended to that findings file, and its weather/props forward-test
   candidate is withdrawn.
   **Rule from now on:** any member-level Polymarket study selects whole events, fetching members under $10k from
   gamma.

**Facts learnt that cost time.**
- **Polymarket's collateral.** Rewards are paid in pUSD by `0x2c2795ea…a709` at 00:00 UTC. Combos collateral is pUSD
  approved to Exchange v3.
- **Polymarket endpoints:**
  - the list of markets that actually pays rewards is `/rewards/markets/current`; `/rewards/markets/multi` returns 100k
    mostly empty rows;
  - a combo leg's `position_id` is not a CLOB token; map it through gamma `positionIds` to `clobTokenIds`;
  - `batch-prices-history` takes 20 tokens a call.
- **Polygon blocks are about 1.5 s,** not 2 s. Block-number estimates overshoot Infura's 10k-block `getLogs` cap.
- **Kalshi:**
  - the batch candle endpoint returns nothing for markets archived before about April 2026, so fetch them one at a time;
  - the public settled-markets endpoint serves only August–October 2026;
  - weather settles on The Weather Company from 2026-08-14;
  - combo makers pay 0.035·C·p(1−p) since 2026-08-20;
  - LIP is US-only.
- **Settlement sources and fees:**
  - Polymarket weather settles on the maximum METAR reading, 0–2°F below the NWS climate report, so 70.7% of its
    settlements match the climate report.
  - Weather markets were fee-free until 2026-03-30.
  - football-data's Pinnacle columns stop after January 2026.
- **Free odds archives:** tennis-data's real files sit behind an obscured path; aussportsbetting.com is behind
  Cloudflare.

**Open, in order of expected value.** None is approved; the first two need the user's accounts or money.
1. **Polymarket combo paper quoter** for cross-game 7+ legs at m = 0.40. It is passive: it subscribes to the RFQ
   websocket and records hypothetical quotes. It needs CLOB credentials. Go after 60 days if count z ≥ 2 and excess > 0.
2. **Liquidity-reward micro-test,** about $2k across 20 joinable Polymarket markets for 14 days. It is real money and
   the only way to observe the reward share. The Kalshi LIP paper quoter needs a US-eligible account.
3. **Election night (2026-11-03)** minute books on both venues. The 2026-10-09 study's open item; the venue tilt is
   untested at minute resolution.
4. **Forward watch lists:**
   - resting soccer draw bids (+3.7% a signal out of sample, t 1.64);
   - range longshot NO (needs at least 500 fresh Q4 events);
   - a variance-adjusted options model for touch markets.

**Infrastructure.** Eight new scripts, each with tests (206 pass):
- `scripts/pm_weather.py`
- `scripts/pm_rewards_mm.py`
- `scripts/pm_crypto_options.py`
- `scripts/pm_sports_sharp.py`
- `scripts/pm_parlays.py`
- `scripts/pm_combos_maker.py`
- `scripts/pm_wallet_skill.py`
- `scripts/pm_structure_scan.py`

## Session log — 2026-10-11 (forward tests, the book written, and what an executable queue bidder earns)

Asked to "continue". The book's pending writes were approved and run; launchd was declined for now. The session froze
five forward tests and a watcher, then found and measured the gap between the queue book's backtest and any bidder
that can actually execute it. Interrupted once by the usage limit; the stopped workers were resumed and finished.

**The book.** Written with the user's approval (the 2026-10-10/11 command list): 29 rows, go-and-current **$1,421,473 a
year** over 8 rows, matching the simulation on a copy.

**The queue row's implementation** (`research/2026-10-11/queue_live/findings.md`). This is the session's main result.

| implementation, $15M, all4, out of sample | $ a year (t) | share of the backtest |
|---|---:|---:|
| backtest: each sale at its own print (only a bidder behind each seller gets it) | $409,885 (9.31) | 100% |
| **hourly taker: buy back the previous hour's qualifying sales at the next hour, at that hour's venue median** | **$294,743 (7.51)** | 72% |
| same, at the first trade after the hour | $317,253 (7.03) | 77% |
| daily re-quoted resting limit | $210,512 (8.01) | 51% |
| one fixed resting limit (15bp) | $191,626 (3.84) | 47% |
| the row as written: resting limits at hurdle + carry | ~$20.6k (trailing 90 days) | — |

- **Resting orders earn their limit, not the market.**
- **Dislocations persist for an hour.** 98% of stETH and 91% of weETH qualifying sales still clear at the next hour;
  the coordinator recomputed 98.4% and 92.9% from the swaps.
- **The 2026-10-10 late-entry figures were optimistic** (96% kept at an hour, 91% at a day). `simulate_book(delay_s)`
  delays the decision but keeps each sale's own price. Priced at the later market, an hour keeps 72–77% and a day 52%.
- **Two corrections, applied with the user's approval** (book go-and-current now **$1,166,284 a year** over 7 rows):
  - `lst-queue-book-one-pool`: hourly-taker legs, quote $294,743, kill criterion 1 on the hourly taker's trailing 90
    days.
  - `kinetiq-khype-queue-bid`: re-quote as an hourly taker, $113,872, go = no (t 1.21).
  - The old quotes stay in each row's history.

  ```
  uv run python scripts/strategies.py add --file research/2026-10-11/queue_live/book_entries.json --replace
  uv run python scripts/strategies.py add --file research/2026-10-11/queue_book5/book_entries_khype_requote.json --replace
  ```

**The other studies.**

| study | result |
|---|---|
| `queue_book5` | kHYPE reproduces exactly; `simulate_book` gained next-hour pricing (default off) that reproduces queue_live's hourly taker to the cent. As hourly takers: kHYPE alone $113,872 at $10M (t 1.21: fails go); five assets at $15M $293,463 with a one-day chain crossing (t 3.27; $353,855 fungible); all4 on that 452-day window $184,984; sAVAX $70,073 at $3M. kHYPE and sAVAX persist 98% into the next hour. Own-print headline recomputed by the coordinator ($460,554.41) |
| sAVAX at swap level | $75,530 a year at $3M (t 6.38). The 2026-10-10 queue model was wrong: Benqi pays the rate at the cooldown's end (6,013 redeems, median −0.00001bp), so queued sAVAX accrues. sAVAX correlates 0.67 with kHYPE |
| `jlp_forward` | Forward test day 0 (SOL 3,574,433.6 / ETH 26,633.4 / BTC 1,323.5 tokens of net delta, re-derived from raw). Hedging on Hyperliquid instead of Binance adds +1.54pp a year for JLP (+9.89% vs +8.35%) and +1.26pp for GM SOL-USDC, because HL funding sits at the formula rate on 41–55% of hours (Binance 11–18%). The gap narrowed in 2026. Decide the venue at day 60 |
| `watch_forward` | EMPD/BNC registered before the 10-14 vote (EMPD true mNAV 0.5590 re-derived); the gold watch reproduces the study exactly; money-market hold 1 sits at its 1pp kill line in young isolated markets |
| `collateral_watch` | 5 venues baselined. HL portfolio margin exposes 5 reserves in the API (HYPE 0.65, UBTC 0.50). HL HYPE +5.09pp and BTC +4.58pp (re-derived). 642 alt pairs settle at the floor at least half the time; the spot book binds, and floor share is not carry (negative spikes) |
| `alt_floor_carry` | **no-go** on Binance and Bybit: all 32 pre-registered variants lose in and out of sample (chosen: −0.14% and −0.40% a year out of sample; re-derived), even at zero costs. Floor share does not persist (32% of 28-day windows after ≥90% floor contain a spike), liquid floor names are ~1.5 per date, the book churns. New data trap: Binance prints floor funding for delisted perps (51,434 settlements on untraded days, 97% at the floor) |

**Infrastructure.**

- `scripts/forward_daily.py` runs every forward test with one log line a day (`research/forward_daily_log.md`, first
  pass clean in 46s). It has a `--skip` option for second runs the same day.
- `scripts/launchd/com.llm-quant.forward-daily.plist` (07:30 UTC) is not installed.
- 871+ tests pass.

**Method changes.**

1. **Late entry means entering late at the later price.** Every queue study's late-entry claim is optimistic until
   re-run that way. The corrected pricing lives in `queue_live.py implementations` (f)/(g) and should become a
   `simulate_book` option.
2. **Test the implementation, not only the signal.** A backtest's fill convention is an implementation claim. Price
   the executable versions (taker at the next hour, resting limit at its limit) before quoting.
3. **Place the hedge where longs pay the formula rate.** For any hedged row, compare the hedge venue's funding.
4. **One-sided BH for go rules.** `choose_then_test` now also returns `bh_survivors_positive`. The two-sided list
   counts significant losers.
5. **Cut Binance funding to traded days.** Delisted perps keep printing floor settlements. Re-check the rent map's
   floor shares.

**Errors found and fixed.**

- The coordinator ran the chains pass before 07:00 UTC; it re-probes the previous UTC day and overwrites its folder.
  Stopped, and restored from git.
- `strategies.py scorecard` writes `research/scorecard.json` even when the book is patched to a copy. Restored.
- The JLP sigma gate's 14-day run could be reached by one tail day; set to 15 before any scored period.
- Worker errors are listed in each `findings.md`.

**Next.**

1. Decide the JLP hedge venue at day 60 (~2026-12-10).
2. Redo the late-entry numbers of the 2026-10-09/10 queue studies with `simulate_book(later='hour')` (done for kHYPE,
   the five-asset book and sAVAX).
3. Re-check the rent map's Binance floor shares for phantom post-delisting settlements.
4. Read `research/forward_daily_log.md` daily. JLP day 60 is around 2026-12-10; EMPD +20 is 2026-11-09; money-market
   hold 1 ends 2026-11-09; queue paper v2/v3 register from 2026-10-12.
5. A keeper for the hourly taker needs a signing key: the user's call.
6. launchd when the user agrees; the chains pass only after 07:00 UTC.

## Session log — 2026-10-10/11 (rents and scarce resources: a rent map, nine studies, a shared queue book)

Asked to "continue the analysis, be profound and smart, find new and unique approaches and profitable alpha strategies".

**The method change.** The repo's one robust lesson became a search method:

- **The lesson.** Survivors are rents paid by agents with a non-price motive, collected by whoever supplies the scarce
  resource the agent needs: locked capital, venue-specific capital, tail tolerance, attention, access.
- **The rent map** (`rent_map`) sizes the pools top-down. About $12.7B a year is paid, $2.2B above a fair rate, of which
  roughly $2.8–17.5M is accessible to patient capital, 3–16× the book.
  - Hyperliquid's funding sits at the formula's interest rate on 71.6% of open-interest-weighted hours: the largest
    above-fair pool is a venue parameter.
- **Nine studies tested the under-collected pools.** Every headline was re-derived by the coordinator from raw files.

The synthesis is [rents_and_resources.md](research/2026-10-10/rents_and_resources.md).

| study | verdict |
|---|---|
| `queue_book` (coordinator) | **go**: the four queue bids on one capital pool. $15M earns $409,889/yr out of sample (t 9.31), 86% of the four separate books on 45% of their $33M. Dislocations correlate within an underlying (weETH–stETH 0.70) but not across them (LBTC −0.06; kHYPE −0.03). Late entry keeps 85–96% (1h), 85–91% (1d); best month 12% of the value |
| `cow_fill_check` (coordinator) | **implementation verified**: in the April 2026 stETH episode, CoW orders resting ≥ 1h filled 6,023 ETH of LSTs (91 fills) at a median 31bp below NAV, at their limits; 83 bidders. One unescrowed balance can back every bid |
| `house_vaults` | **go ×2**: GMX GM SOL-USDC hedged ($103k at $2M; fees 11.4% + traders' losses 4.9%); JLP hedged, conservative ($248k at $10M, gated by a live forward test). HLP no-go: its liquidators made $74.7M of $138.6M, its market makers ≈ $0. gUSDC, Lighter LLP, GM ETH no-go |
| `queue_bids_alt` | **go ×2**: kHYPE queue bid ($140,043 at $10M; 13,426/13,426 confirmations exact; lumpy); kHYPE as the HYPE carry's spot leg (+4.48% vs +3.27%: **upgrade** of `hl-hype-spot-perp-carry`, $224k at $5M). Solana LSTs capped by a 10bp withdrawal fee; slisBNB, aprMON no-go; sAVAX, stS watch |
| `rent_map` | the map above; ranked the gaps that became `gold_carry` and confirmed incentive budgets and LP vaults as the largest under-tested pools |
| `incentive_yields` | **no-go**: displayed dollar yields rotate to +15%/yr over SSR out of sample, but nothing above ~5pp survives a share-price audit (vault write-downs never reach the yield series); blue-chip rotation passed by luck (siblings −0.16%); new-chain premium lives in small unchecked pools (rule −0.23%). Watch: +1% on pooled money markets |
| `ve_carry` | **standby**: hedged veAERO +11.3% only when hedged on Hyperliquid's funding; pre-committed +4.10% (t 1.47); the attentive-voter premium fell from +15–21pp to ≈ 0 (final-hour votes only); the 2026-10-22 Aero merger ends the measured system |
| `nav_wrappers` | **standby / no-go**: GBTC/ETHE conversions paid (+8%/+53% a year); after the 2025 listing standards trusts filed at premiums; DAT true-NAV discounts do not converge; 5 of 18 dashboard "discounts" are premiums once debt and preferred count (MSTR naive 0.93, true 1.19) |
| `gold_carry` | **no-go, two watch lines**: gold perps follow spot (no roll), but the cost of carry (2.8–3.8%) ≈ SSR; +1.7–2.6% left on capital, capped at $1–2M by tokenized-gold depth |
| `hl_vault_skill` | **no-go**: 9,477 vaults, survivorship-free; track records do not persist; user vaults lost $69.7M lifetime, 22.7% positive. A least-bad pick "passed" out of sample (+44%) and lost −78%/yr over the full history |

**Method changes.**

- `backtest.choose_then_test` now reports `in_sample_positive`. Go rules should require it: the vault-skill study showed
  how a least-bad loser passes.
- Yields are believed only after a share-price audit (`incentive_yields`).
- Queue bids are sized as one book with `queue_book.simulate_book`, which reproduces `simulate_bid` exactly with one
  asset (tested).

**Errors found and fixed.**

- In `queue_bids_alt`'s HYPE upgrade entry, `usd` held the increment ($60k), not the total. Corrected to $224,000 before
  any write.
- Three public HyperEVM RPCs ignore the block tag (use HyperLend's archive or dRPC).
- GeckoTerminal printed a false 778bp kHYPE hour.
- Sanctum's `sol-value` API is 230–250bp stale.
- DefiLlama floors vault yields at zero.
- Yahoo rescales GBTC/ETHE closes before the Mini Trust spin-offs.
- Infura's −32603 is not retried by `live_rpc`; `ve_carry` wraps it.

The full lists are in each `findings.md`.

**The book, pending the user's approval** (auto mode refused book writes last session). Run in this order:

```
# carried over from the previous session
uv run python scripts/strategies.py add --file research/2026-10-10/term_carry/book_entries.json
uv run python scripts/strategies.py add --file research/2026-10-10/queue_bids_ext/book_entries.json --replace
uv run python scripts/strategies.py quote hip3-equity-funding-carry --window research/2026-10-10/tradfi_perps --net-apr 0.034 --usd 73000 --go yes
# this session: go rows (the kHYPE file replaces the HYPE carry with its kHYPE version)
uv run python scripts/strategies.py add --file research/2026-10-10/queue_bids_alt/book_entries.json --replace
uv run python scripts/strategies.py add --file research/2026-10-10/queue_book/book_entries.json
uv run python scripts/strategies.py add --file research/2026-10-10/house_vaults/book_entries.json
# the four queue components are priced inside the one-pool row: mark them go=no so they are not counted twice
uv run python scripts/strategies.py quote lido-steth-queue-bid    --window research/2026-10-10/queue_book --net-apr 0.0130 --usd 129884 --go no --note 'component of lst-queue-book-one-pool: priced inside it, not additive'
uv run python scripts/strategies.py quote etherfi-weeth-queue-bid --window research/2026-10-10/queue_book --net-apr 0.0194 --usd 194238 --go no --note 'component of lst-queue-book-one-pool: priced inside it, not additive'
uv run python scripts/strategies.py quote kelp-rseth-queue-bid    --window research/2026-10-10/queue_book --net-apr 0.0147 --usd 44120  --go no --note 'component of lst-queue-book-one-pool: priced inside it, not additive'
uv run python scripts/strategies.py quote lombard-lbtc-queue-bid  --window research/2026-10-10/queue_book --net-apr 0.0111 --usd 111136 --go no --note 'component of lst-queue-book-one-pool: priced inside it, not additive'
# watch and standby rows (go = no)
for s in hl_vault_skill incentive_yields nav_wrappers ve_carry; do uv run python scripts/strategies.py add --file research/2026-10-10/$s/book_entries.json; done
```

**What the approved book would hold.** The commands were run on a scratch copy of the book, counting rows on its own
rule (go, current quote, not retired):

| state | go and current, $ a year |
|---|---:|
| today | $613,442 |
| with the previous session's pending writes | $1,022,032 |
| with this session's as well | **$1,467,586** |

- The queue rows now need $15M instead of $33M.
- Two of the new rows are gated (JLP's forward test) or lumpy (kHYPE).
- The cross-chain dollar book's quote is stale and is not counted.

**Next.**

1. Run the one-pool queue book live and small: ETH-only first, resting CoW orders from one WETH balance.
2. Forward-test JLP's net-delta hedge for 60 days.
3. A daily watcher of Hyperliquid's and Binance's accepted collateral: each new asset is a same-venue carry at the
   formula rate.
4. Joint five-asset queue simulation with kHYPE's environment exported; sAVAX at swap level.
5. Forward ledgers for the watch items: pooled money-market incentives, xyz:GOLD / HL PAXG, HL vault size-follow, sAERO
   after the merger, EMPD (vote 10-14) and BNC.
6. Install the launchd jobs.

## Session log — 2026-10-10 (alpha that does not race: a brainstorm, six history tests, a forward ledger)

Asked to "continue what is left and brainstorm alpha strategies that don't require latency or a position in the block".
The brainstorm is [alpha_brainstorm.md](research/2026-10-10/alpha_brainstorm.md): about 35 candidates in six families by
where a non-racing edge comes from (a constraint someone pays to escape, slow public information, calendar flows, term
structure, segmented capital, risk premia sold on purpose), each marked against what this repo has already killed and
why. Its operational test for "no latency": entering an hour late keeps most of the edge.

**What was left, done.** The unlock pre-short's forward test runs: `unlock_study.py forward register|score` froze 20
cliffs before their entries (SEI first, 10-10 14:23 UTC; median bid depth $20k at registration) in
`research/unlocks_forward.jsonl`, and scores each from Hyperliquid's own history after its window (identical to the
study's store on six past events); `perp_daily.py` now registers, scores and refreshes DefiLlama's schedule weekly, and
keeps Boros's term structure daily. The ether.fi payout check, the delisting event study and Binance's TradFi perps
against HIP-3 are three of the six studies below. Still open: `roll_carry.py analyze` after the 10-12/13 roll steps, and
installing the launchd jobs (the user's call).

| study | verdict |
|---|---|
| `term_carry` | **go, new row** `hl-hype-spot-perp-carry`: HYPE spot as Hyperliquid portfolio-margin collateral, short the perp, +4.30%/yr over the savings rate out of sample (t 5.68, both halves), $5M, ~$200k/yr — the same coin pays 9.6% on Hyperliquid and 4.5% on Binance. Dated basis: standby row (+2.4–5.4% out of sample, but no 2026 day cleared +2pp). DIY Ethena on Binance no-go; Hyperliquid BTC/ETH watch; Boros no-go (implied − realised +0.12%, sign flips with the cycle); VRP measured, shrinking |
| `tradfi_perps` | **no-go**: Binance's TradFi perps hedge 95% of the equity carry's off-hours risk, but 68.5% of their settlements are zero (no interest floor), so the hedged carry is below the savings rate on liquid names; no commodity roll trade. **Re-quote the equity carry $330k → $54–73k/yr** (its excess holds at t 3.91 but in thin names) |
| `queue_bids_ext` | **payout check passed**: 40,890 ether.fi claims paid exactly, no fees, queue median 0.79 days (not 2.0); the instant route is not a cap. weETH re-quoted **$170k → $194k/yr**; **new row** `lombard-lbtc-queue-bid` $111k/yr at $10M (needs a Coinbase account for the BTC→cbBTC leg); OETH, tBTC, osETH, mETH, ETHx and others too small, one-event, permissioned or dead |
| `listing_lifecycle` | **no entry.** New listings decay (median −25%/−33% vs seasoned alts at 30/60 days) but the pre-registered rule failed (week t 1.01) and 16% of trades saw the coin double; a forward-test rule is written down. Delistings closed: the "92%/yr pre-delisting" spread was earned weeks before any notice in sub-$5k books |
| `fundamentals_factor` | **no-go.** Chain flows and protocol fees/value predicted returns in 2021–23 and not since; the chain-activity detectors replayed over five years (1,792 events) lose in all 16 variants — activity and price move together, so the reading arrives after the move. Watch: 4-week stablecoin growth (OOS IC 0.041) |
| `governance_events` | **no-go.** 2,522 Snapshot proposals labelled by LLM passes against a rubric hashed before any price; VALUE_UP drifted +7.2% before mid-2024 and +0.07% after; the pre-registered trade lost out of sample. Labels are consistent (blind kappa 0.95) and keyword rules are not (kappa 0.09); Snapshot dates lag the forum post that moves the price. Labelling cost 4.85M tokens |

**The pattern held.** What survived has a counterparty with a non-price motive: leverage demand on the venue that charges
it most (HYPE), holders who will not wait a week for a queue (weETH, LBTC). What died was information the market
already prices (fundamentals, governance, activity surges), a spread that is the cost of capital (the TradFi pair), or
an edge in books a few thousand dollars deep (delistings; new listings' squeezes).

**The book, pending one approval.** Auto mode refused the coordinator's writes to `research/strategies.jsonl` as a shared
resource, so five changes wait for the user: add `hl-hype-spot-perp-carry` and `dated-basis-cash-and-carry`
(`strategies.py add --file research/2026-10-10/term_carry/book_entries.json`); replace `etherfi-weeth-queue-bid` and add
`lombard-lbtc-queue-bid` (`... add --file research/2026-10-10/queue_bids_ext/book_entries.json --replace`); re-quote
`hip3-equity-funding-carry` down (`... quote hip3-equity-funding-carry --window research/2026-10-10/tradfi_perps
--net-apr 0.034 --usd 73000`). With them, go-and-current moves from about $1.03M to about $1.10M a year, and the largest
row is a measured capacity (the HYPE carry) rather than an assumed one. Two concentrations: the HYPE and equity carries
are both Hyperliquid venue risk, and the three ETH queue bids share one collateral pool in a stress.

**Errors found in earlier work.** `chain_census.py` wrote DefiLlama's missing stablecoin days as 0 (fixed, tested; no
recorded hit rested on one); Hyperliquid `candleSnapshot` serves zero-volume pre-listing bars that carry prices (ZEC: 999
days) and Binance serves delisted perps as flat zero-volume bars for months — every study reading either must drop
untraded bars; the funding study's "1.25bp an hour" floor is 0.125bp and three of its "delisted" coins are still listed
(erratum appended); `equity_offhours.FUND_PARAMS` assumes one funding multiplier per builder where some markets differ;
the 2026-10-09 redemption note attributed April's instant redemptions to the public route (89% were fee-free large
holders); `test_dislocation_history.py` needed pycryptodome to import (now falls back). Test runs: 638 pass under
`uv run --with pytest --with pycryptodome python -m pytest scripts` — plain `unittest discover` misses the pytest-style
files.

Next: approve the book writes; install the launchd jobs so the forward tests and Boros history accumulate; score the
unlock forward test as windows close (SEI 10-13, STRK 10-14, ARB 10-15); `roll_carry.py analyze` after the October roll;
a combined ETH queue book on one capital pool; one live LBTC redeem-and-convert cycle; the governance re-test dated by
forum posts; brainstorm items 1.4 (queue bids off Ethereum: HYPE LSTs, sAVAX), 5.4 (incentive-adjusted dollar yields)
and 3.3 (ve(3,3) epoch economics).

## Session log — 2026-10-09/10, second session (fill the gaps, more data, find alpha: ten history-tested studies)

Asked to "fill the gaps, gain more data, find several alpha strategies". The gap was history: every book line had
been priced from windows. This session collected a year of Hyperliquid funding (`research/2026-10-09/perps_history`,
336 markets; 1h candles only reach 2026-03-15 because the venue serves the last 5,000 bars — 4h bars fill earlier
months), futures by contract month (Yahoo; send UA `Mozilla/5.0`, a Chrome string gets 429), every Pendle market,
446k resolved Polymarket markets, Kalshi, and DefiLlama's free unlock schedules (`defillama-datasets.llama.fi`; the
API is paid). New shared harness `scripts/backtest.py` (time splits, Newey–West, block bootstrap, BH, deflated
Sharpe; ROADMAP P2 item 9). Book entries now enter through `strategies.py add/quote`; the scorecard prefers a quote's
own capacity-aware dollars.

| study | verdict |
|---|---|
| `roll_carry.py` — HIP-3 oil carry | **retired** ($2.84M/yr line). Oracles roll on the GSCI schedule, a fifth a day on the 5th–9th US business days at 22:00 UTC (schedule fits 99% of hours); funding pays 0.89–0.97 of each step; every hedged Sep/Oct window lost after costs. The 09-10 "tenth" read an hourly premium that straddles the step. `roll_premium` now uses 5 days; `perp_refs` curves come from the calendar |
| `hip3_pairs.py` — cross-builder funding | **retired**: nine pairs −18.4%/yr OOS (t −2.99); UNITREE a watch item |
| `pendle_history.py` (worker) | **go**: hold the PT instead of the token when implied − trailing-7d ≥ 5%: +7.1%/yr OOS (recomputed 8.4% per capital-year, 96% of 1,004 trades); book carries only measured-interest tokens, $6.6M / $216k a year. Dollar PTs vs the savings rate lost −8.2%/yr after defaults (spreads of 2–6% were where the defaults were). `pt-susds-fixed-vs-ssr` retired (43bp at $250k) |
| `equity_offhours.py` (worker) | perps price 90% of the cash gap by 09:00 ET (efficient); every open rule fails; **go, thin**: short high-funding xyz equity perps, long the stock at a broker: +3.35%/yr over SSR on capital OOS (t 4.06) after an in-sample period that earned only +1.23% (Sharpe 0.23), hourly-only rerun +1.63% (t 1.32); the book quotes the conservative $330k/yr at an assumed 5% of OI |
| `unlock_study.py` | pre-registered window failed OOS; the 3 days before a ≥1% insider cliff held (+1.98%/trade after costs vs placebo −0.34%, event-day t 2.18) but 2026Q3 was negative → `unlock-preshort` proposed, go=no, 30-event forward test (`upcoming` lists them) |
| `polymarket_history.py` (worker) | **no-go** on favourites, neg-risk sums and resolution lag; crypto-price lag was real (106/106) and was automated away in 2026 |
| `pm_crossvenue.py` (worker) | **no-go**: 3,226 Kalshi–Polymarket pairs; best live gap $4.59 after fees; gaps closing |
| multichain third window | cross-chain book $18.8M at 58bp ($109k/yr); Avalanche USDC 7.3% and BSC→ETH USDT held for a third reading |
| Ethereum 1h window (`live_1h`) | re-quoted the stale mainnet lines (USDtb gone, Morpho USDT $1.4M withdrawable); `verify` now classifies idle Aave reserves whose stored rates are consistent at an earlier utilisation as `head-stale-reserves` instead of failing |
| `dislocation_history.py --assets` (worker, resumed) | **go, three queue bids**: weETH $170k/yr and stETH $130k/yr at $10M, rsETH $44k/yr at $3M, two-year out-of-sample (the 210-day window alone priced Lido at $0 — one stress week is not a regime); bids capped at the median venue’s discount (a single-pool print is a searcher’s arb); funded by WETH borrowed against wstETH so idle capital keeps staking; the three share collateral and are not additive in a stress. sUSDe re-quoted to $7.9k/yr; USDe needs approved-redeemer access; Maple, Renzo, rETH too small or dead |
| `funding_arb.py` (worker, resumed) | **no-go**: HL vs Binance is statistically real per unit (every month positive, t 5.15) but lives in coins with under $5k of HL depth and in pre-delisting markets (43% of the profit); at live capacity it is below the savings rate; Binance vs Bybit control flat; HL’s structural BTC premium over the exchanges (2.7–4.2pp) is the cost of two-venue capital |
| chain activity, UTC day 10-09 (`research/2026-10-10/chains`) | second daily pass: Starknet DEX x4.1 for a second day (the first reading asked for one), TON DEX x3.6 new, stablecoin arrivals continue; 39/45 cross-checks agree |

**Where the book stands.** Thirteen live rows (plus the benchmark); nine current and go, worth about $1.03M a year at capacity on their own quotes: the equity funding carry $330k, the Pendle switch $216k, the weETH, stETH and rsETH queue bids $344k between them (one shared collateral pool in a stress), the cross-chain book $109k, and the small mainnet spreads. `unlock-preshort` waits on its forward test. The two studies stopped at the usage limit were resumed and finished; all 440 tests pass. Next: the forward test of `unlock-preshort` (first entries STRK 10-11, ARB 10-12); `roll_carry.py analyze` after the 10-12/13 steps to complete October; an ether.fi payout check before sizing the weETH bid; the funding study's delisting-squeeze event study and Binance TradFi perps against HIP-3; install the launchd jobs (needs the user).

## Session log — 2026-10-09 (every chain at once: activity, tradeability, and what is new)

Asked for "a list of chains with high activity, all types of chains, measuring transactions and volume transferred in
different assets, as the framework to detect new activity on chains where it is reasonable to trade". Deliverables:
[the report](research/2026-10-09/chains/report.md) (the ranked list, the directly measured list, the detector hits,
per-asset flows, cross-source agreement) and [the reading](research/2026-10-09/chains/insights.md).

Landed: `scripts/chain_registry.json` (67 chains, 17 families), `scripts/chain_census.py` (~570 chains from eight
aggregators, daily history, tiers), `scripts/chain_probe.py` with `scripts/chain_adapters/` (one adapter per family:
evm/tron, solana, sui, aptos, starknet, near, ton, cosmos, xrpl, stellar, hedera, algorand, tezos, cardano, utxo,
blockchair, hyperliquid; four of them written by parallel workers), `scripts/chain_activity.py` (analyze, nine
detectors, verify, render, series, an unattended `run`), a 14-day transaction backfill so probe-only chains have a
baseline on day one, a launchd template, and 89 tests across five files (274 in the repo, all passing).

**What the measurement taught, in the order it bit.**
- *Gross transfer sums are meaningless under sampling.* The first EVM sweep summed `Transfer` logs and one Base block of
  flash-loan loops scaled to "$666B a day" of WETH. Value is now net per transaction (each account's positive net
  change, `chain_adapters.net_positive`) on every family, which is what balance-delta chains report natively; Gnosis went
  from $22.8B gross to $9.7M net. Even net, Base and OP carry tens of billions a day through two to four unverified
  contracts, so transfer value is a measure of what moves, not of economic volume, which stays DefiLlama's.
- *Solana moved under the repo.* Blocks now carry version-1 transactions (15% of one block), so `getBlock` with
  `maxSupportedTransactionVersion: 0` fails: fixed here and in `solana_collect.py`, which would otherwise have broken
  the Solana daily pass. Slots are now ~0.27 s. `getRecentPerformanceSamples` keeps ~4.5 h per node, not 12, and a
  lagging node records a "60 s" sample of 600+ slots; GetBlock prunes blocks within hours and answers
  `getBlocksWithLimit` below its retention with its first available block, silently; a calendar day is read from the
  public endpoint's long-term storage instead.
- *The aggregators disagree with each other, and the probe can say why.* MegaETH reads 1.98M on the probe and L2Beat,
  1.11M on growthepie: 43.5% of its transactions go to the system oracle `0x6342…0001`, and 1.98M x 0.565 = 1.12M.
  Unichain is 74% builder bookkeeping, XDC 56% validator signatures, Flare 86% oracle submissions: `bookkeeping_targets`
  now reports them beside the headline.
- *DefiLlama's stablecoin endpoint writes a missing reading as `{}`*, which a naive parse turns into zero and every
  stablecoin with a gap into a "launch" (USDD on Tron, $1.3B, "new"). Missing is now None and cannot fire.
- *The market moves every chain at once.* 10-07 to 10-09 was a sell-off (ETH -8%, SOL -9%) and transactions rose on
  most chains together; a surge now has to exceed the cross-chain median move of the same day by half.
- Rootstock's public nodes serve no `eth_getLogs`; NEAR's non-archival nodes forget blocks after ~23 h; Aptos limits an
  IP to 40k compute units per 5 minutes; Blockscout's Base and Arbitrum instances sit behind Cloudflare.

**The first reading** (UTC day 2026-10-08, 67 chains probed, 569 in the census): the probe agrees with the aggregators
within ±10% on 34 of 42 same-day chain-source pairs; 12 chains are deep and 28 tradeable; the one `high` hit is Cardano
(34k → 543k transactions in two days, a HOSKY mass distribution), and the most tradeable new activity is a memecoin
wave on Cronos (x2.6). Arbitrum's tripled active addresses were one contract born that afternoon and pinged by ~1,000
fresh wallets an hour — the who-layer, not the count, is what says whether new activity is worth a trade.

Next: the who-layer as a detector (a contract newly among a chain's top targets — Arbitrum's `0x12f5…` was born on the
probe day and tripled the chain's active addresses); identify the unverified contracts that carry Base's and OP's
value (bytecode lens); an hourly mode for fresher detection; Solana's backfill (blocks are too heavy for the public
endpoint at 40 a day); Substrate (Bittensor, Polkadot) and Kaspa adapters; per-asset flow history so `probe_new_asset`
has a baseline; install the launchd job so the series accumulates.

## Session log — 2026-09-10 (five-hour Ethereum continuation: 72,446 LPT senders, and two rejected signals)

[Five-hour study](research/2026-09-10/live_5h/report.md), pinned to finalized blocks 25,944,911–25,946,402,
05:30:48–10:30:48 UTC: 460,074 transactions and 1,338,947 logs. The original request's window is preserved across the pause.

**Small transfers were the missing activity signal.** 72,446 distinct senders transferred 161,357.65 LPT to the same
Binance-labelled address, 99.91% of positive non-mint/burn LPT transfers and 15.75% of all transactions. All matched
direct transaction calldata; 72,443 occurred after 08:30, with a median of 2.1502 LPT. This is consistent with coordinated
consolidation, not proof of ownership or selling. `detectors/token_fan_in.py` makes the pattern repeatable without a
USD price or $10,000 transfer floor. Tips remain economically material: the 25% receipt sample measures 4.145 ETH of
tips against 0.846 ETH burned, 4.90x. Exact all-block execution burn is 3.463 ETH.

**Two attractive stories failed verification.** A supposed 24-minute Aave PYUSD blackout came from sorting same-block
updates by rate instead of log index. Historical state shows 896,452 PYUSD cash and 4.919% borrow APR after both
intra-block squeezes. The analyzer now preserves log order and complete end-of-block updates; the episode detector
requires that series and the false alarm disappears. Earlier sampled artifacts need re-analysis before duration claims.
rETH's 48.53bp discount had almost no direct burn liquidity: `getTotalCollateral()` returned 0.000000034 ETH. Its
conditional $1.92m/year arithmetic no longer enters the book as GO; conditional/permissioned/unknown exits are gated.

**Two prior TODOs are addressed.** Source cash and withdrawal flags now cap single-chain rate switches: Compound USDT
→ Aave falls from a destination-only $138.67m / $438k per year to $27.15m / $156k; fixed-rate Sky no longer inherits a
synthetic $1bn size. Source ownership, collateral constraints and destination caps remain unmeasured. Token-level
borrower inventories reconcile for three accounts: Spark's $293.73m low-HF debt is WETH against wstETH; Aave's $30.30m
position is USDC/USDT debt against USDe/sUSDe. Their relevant shocks are relative prices, not a blanket ETH/USD drop.
Enrichment now keys accounts by venue as well as address, retaining 39 health observations.

All 17 detectors completed with 60 hits; 174 unit tests ran (172 passed, two existing skips), 21 aggregate checks and
eight state-identity groups passed. The new study retains code, historical reads, raw-cohort checks and a figure.
Next: older funding/ownership history for the LPT cohort; repeated executable rate/exit quotes; re-analysis of earlier
rate-duration claims with log ordering preserved. The midnight routine itself is outside this daytime window.

## Session log — 2026-09-10, second session (develop further: the perps thread and the sUSDe history)

The state review earlier this day found the loop precise about $10k-class Ethereum findings and silent on its two
highest-EV threads, each dropped after one window. This session gave both a second window and, where a window cannot
answer, a history. Deliverables: [the perps note](research/2026-09-10/perps_2/insights.md), the
[funding history](research/2026-09-10/perps_history/history.md), the
[reference comparison](research/2026-09-10/perps_2/refs.md) and the
[sUSDe discount history](research/2026-09-10/susde_history/findings.md).

Landed: `scripts/perp_history.py` (months of hourly funding and candles for every live market; episodes, premium
snaps, and an out-of-sample table for any earlier window's hits; 12 tests), `scripts/perp_refs.py` (public delayed
references for 118 builder markets, delay-aligned, session-gated, with the futures-curve placement of the energy
oracles), `scripts/dislocation_history.py` (181 days of every sUSDe swap against NAV; 22 tests), the findings ledger
now accepting perp windows, `net_apr`/`go` on the perp economics blocks, a book refresh that only speaks for
strategies whose detectors ran in the window, and two new book entries.

**The 09-08 oracle claim was wrong, and the trade was right anyway.** Compared with public quotes aligned by their
own delay, XYZ's oracles are within a basis point on FX and spot metals and within 25bp on ten of fifteen live
references; the exceptions are the three energy markets, and the futures curve explains them. All three energy
oracles sit 0.6 of the way from the front contract to the second and all three books at 0.45: the oracle is a
constant-maturity blend, the book prices the same blend a few days further along, and the premium is the lead times
the calendar spread, 0.15 x 4.67% = 0.70% on Brent (observed 0.70%), with the sign reversed on gas because the gas
curve is in contango (observed +0.68%). The funding history shows the roll: at 22:00 UTC on 09-08 and 09-09 the
Brent premium narrowed from -1.0% to -0.4% with the mark unmoved and the implied oracle down 0.47%, a tenth of the
spread, so the oracle steps once a day at the futures reopen over about ten trading days. Longs are paid because
they are one step behind a roll, not because an oracle is broken.

**Out of sample.** The three 09-08 `funding_carry` hits, held on paper 47 hours through the settled funding series:
+164.5bp, +136.9bp and +156.4bp of funding collected; the premium moved 7 to 17bp against the paid side; net of the
quoted round trip the oracle-hedged proxy made **+145bp, +109bp and +125bp**, break-even at hour 4, 4 and 5 against
predictions of 3.6, 4.4 and 6.7. The five other carries that sweep flagged at 20% to 130% collected 5 to 12bp and
lost on the hedged reading. The rate was only a story where the premium was structural.

**And the history says the regime is eleven days old.** Over 71 days the Brent premium averaged -0.05% and changed
sign 308 times; the longest run above 100% before 7 September was 19 hours; the current one is 61. Across XYZ's 104
markets 9.8% of all hours ran above 100% a year in 6,967 episodes with a median length of one hour, 98.7% of which
flipped within 72 hours: extreme HIP-3 funding is mostly one-hour noise on thin books, and only the energy run is a
mechanism. The book now holds `hip3-oil-funding-carry` (long the perp, short the futures blend the oracle tracks;
$1.7M of ask depth at 25bp; kill on funding under 50% for a day, premium beyond -1.5%, oracle 2% off the blend,
depth under $250k) and `hip3-cross-builder-funding` (UNITREE at 307 points between two builder books, priced at $25k
because the small book is that thin). The book prints the detector's unhedged 337%; the hedged expectation, funding
less a tenth of the spread per day, is about 200% a year, and both numbers have a clock: the spread, and a depth that
was $474k two days earlier.

**The sUSDe bid, priced from history instead of re-measured on windows.** 45,089 swaps in three pools over 181 days
against the NAV Ethena paid at each block: the discount is frequent and shallow (median 2.8bp, p99 17bp), one real
stress week in April at 17.5bp for 80 hours, and a $600k standing bid, which is the on-chain USDe exit, would have
earned **$41,500 a year net of USDe's basis**, $635k without the capacity cap. The exit binds. The kill criterion the
book carried (no ask 10bp under NAV in 30 days) never came close to firing in six months and was the wrong test; it
is replaced by the trailing option value and the exit depth, and the strategy is re-quoted at 6.9% on $600k.

**Two of the loop's own errors this session, for the record.** The first `perp_history` episode definition exited on
the last extreme hour and so scored every episode against the paid side by construction (hedged-positive share 24%;
84% once fixed, pinned by a test). The first reference map matched a private company to a delisted pharmaceutical
and compared Markets by Kinetiq's ETF-priced perps against index points; both were caught by printing the raw values
and are recorded in the module.

**Later the same day: the detector, the runner, the scorecard.** `detectors/roll_premium` in `perp_scan.py` turns the
mechanism into a re-check: it predicts the premium from the curve placement, scores the fit, and prices the carry net
of a tenth of the spread per trading day; Brent quotes 213% while the roll lasts and 167% after a daily round trip,
and the book entry is now quoted from that finding rather than from the unhedged 337%. `scripts/perp_daily.py` runs
one unattended pass (history append, window, references, detectors, verify, ingest, book refresh, history) with a
launchd template that is not installed by this session. `strategies.py scorecard` prints the two numbers the state
review asked for beside time-to-verified-insight: **$3.0M a year at capacity across the seven strategies whose own
detectors say go** (of which $2.84M is the oil carry, so the clock on that number is the calendar spread and one
book's depth), 88% of the 57 twice-seen rates kept at least half their first reading, and 4 of the 9 out-of-sample
funding predictions were positive hedged (the three energy ones and one cross-builder book). Ethena's minting contract,
read on chain, caps redemption at 10,000,000 USDe per block, so the sUSDe bid's scaling limit is approved-minter
access, not protocol capacity.

**The cross-chain dollar book, second reading** ([note](research/2026-09-10/multi_1h/insights.md); collection and the
`cross_chain_rate` detector in `multichain.py` by a parallel worker that was cut off by the account's session limit
before it could ingest or write, so the numbers were read back from its artifacts). The book absorbs **$21.1M at
67bp, $141k a year**, against $37.3M at 48bp two days earlier, and it is a different book: the destination rotated
from Base at 4.00% to Avalanche at 7.19%, and the one row that held is USDT from BSC to Ethereum, 60 to 70bp on about
$10M, bound by BSC withdrawable liquidity in both windows. The CCTP flow-against-rate correlation is still negative
(-0.57 then -0.27). Both windows are in the ledger under chain `multichain`, the `book` finding reads 2 of 2, and
`cross-chain-usdc-switch-book` is a strategy entry quoted from it.

**The first unattended pass ran, and taught the runner something.** With a five-minute reference run there is no
Hyperliquid snapshot ten or fifteen minutes before a delayed quote, so only the live-quoted FX and metals aligned and
the energy curve never formed; the runner now samples for twenty minutes and the tape analysis reads the reference
run's own snapshots. The pass otherwise completed end to end: history appended, window, detectors, verify, ledger,
book, history re-scored, one line in `research/perps_daily_log.md`.

Next: let the daily pass accumulate so premium against spread becomes a regression; a third cross-chain window at a
different hour; the per-row benchmark test (destination rate against SSR) inside `cross_chain_rate`.

## Session log — 2026-09-10 (Ethereum: $34.6m of turnover, $0.65 of WETH)

[Ten-hour study](research/2026-09-10/live_10h/report.md), pinned to finalized blocks 25,939,239–25,942,222:
2026-09-09 10:32–20:32 UTC, 861,766 transactions and 2,365,900 logs. ETH fell 1.04%; decoded DEX turnover was
$489.89m; two covered lending liquidations repaid $120.87. The daytime window does not test the midnight routine.

**The new detector found another example immediately.** Three flash-funded roundtrips in 7AΩ∞/WETH generated $14.8m
of turnover in a pool with only 0.023 WETH. They returned nearly all borrowed capital after a token-side reserve
reduction, leaving $0.29 of WETH before gas. `recycled_swap_volume` requires actual priced-token transfers to match
the Swap events, then checks whether both token positions almost close in the same transaction. Its first sweep found
another $19.8m roundtrip in BULL/WETH. Together: **7.07% of all priced DEX volume, 65.43% of v2-style volume, $0.65
of WETH extracted before gas and $0.29 after execution gas**, before other internal payments. Both factory pairs,
historical reserves and successful receipts were checked. The prior $44,391 fee estimate on the first pool was
volume times an assumed tier, not realizable LP income; the report now flags such rows and leaves passive income
unmeasured. Gross volume stays intact.

**The fee-cost TODO is addressed for six economics detectors.** Every fourth block's receipts (746 blocks) show
13.623 ETH of tips against 3.071 ETH burned, **4.44x**. Full-window execution burn, available directly from every
header, is **12.357 ETH**. Effective-fee gas-weighted p75/p90 are 0.706/2.058 gwei; standard/competing scenarios now
use these, with window checks and a base-plus-tip fallback. Direct bids and blob fees remain separate. Exactly-zero
tips and <=0.01-gwei tips are distinct fields. Fullness was 50.50% of the maximum, near the fee mechanism's target;
this alone is not evidence of underutilization.

Landed: finalized collection with immutable resume bounds; explicit-block head reads and `enrich` at the saved block;
concurrent small RPC batches; receipt completeness and gas reconciliation; exact full-window burn; stricter aggregate
verification; corrected `getUserAccountData` LTV/available-borrow decoding with health identities; detector failures
now fail the pipeline. All 16 detectors completed, 68 hits were ingested, and seven linked strategies were re-quoted.

**What remains narrow.** Compound USDC's 4.524% endpoint rate is about a $615k position worth $2.8k/year above the
3.60% Sky savings benchmark, holding conditions fixed. USDtb's excess is only ~$481/year. The single-chain USDT
switch detector still quotes a destination optimum ($120.9m) larger than the source's balance-based liquidity
($25.9m); the report constrains the interpretation. Two sampled Aave accounts carry $34.7m debt near HF 1.02, but
collateral/debt composition is needed before translating that into a market-price shock.

Next: source-liquidity constraints in single-chain rate switches; repeated pinned snapshots for Compound and other
venues without rate logs; reserve/balance accounting for extreme roundtrips; composition of the low-HF positions.
The `dollar_rate_outlier` detector currently traverses Aave/Spark lending rows only; Compound is repriced through
`rate_dispersion` and the study's explicit benchmark calculation, not through that detector's absence signal.

## Session log — 2026-09-08 (perpetual futures: the first instruments that read a market, not a ledger)

Everything before this read *settlement* — transfers, lending state, bridge legs. A perp DEX settles almost nothing on
chain; it produces a price, a funding rate and an open-interest number, and all the value is in the relationships
between them. That needs its own collector, and HIP-3 makes it worth the trouble: a 500,000-HYPE stake buys you your
own perp DEX on Hyperliquid's engine, your own listings, **your own oracle**, and 0–300% of extra fees.

Landed: `scripts/perp_rpc.py`, `scripts/perp_collect.py` (window + tape), `scripts/perp_scan.py`
(analyze / tape / detect / verify / render) with eight perp detectors, and `rounds.json` recording the loop.

**The finding.** `xyz:BRENTOIL` is 54bp below its own oracle and has widened monotonically for eight hours; `xyz:CL`
the same; `xyz:NATGAS` the reverse. Longs are paid 285% and 217% annualised, the round trip costs 11.9bp and 10.9bp at
$100k with nothing unfilled, and both break even in under five hours. External quotes put the *book* closer to the
real price than the oracle on both, so the deployer's oil oracle is high and the funding rate is paying people to
correct it. Capacity is $474k of book against $484M of cap headroom, and the delta is unhedged — there is no second
Brent on the venue.

**The tape is what made it a trade.** One snapshot cannot separate a stale oracle from a structural basis and the two
call for opposite trades. Sampling all 515 markets every 20 seconds and correlating *first differences* of mark and
oracle separates them: 268 markets where the oracle tracks the book, 2 where it never moved at all
(`xyz:ZHIPU`, `xyz:MINIMAX` — private companies with no continuous public market). Brent is firmly in the first group.

**The verifier produced the explanation.** It asserted `premium == (mark − oracle) / oracle` and 304 of 315 markets
failed. The assertion was wrong — the venue's premium is an hourly average sampled against the *impact* prices. Chasing
it led to fitting the funding formula, which also did not hold (wrong on 164 of 315, worst on HIP-3), so the loop
replaced the assertion with a **measurement**: how much of its own premium each DEX charges as funding. Median under a
fifth; EntropyIO 1.6%. That table is why a 54bp gap can stay open for eight hours against a 285% toll. The best
finding in the session came out of an assertion that failed.

**The constraint is the door again.** `io:ANTH` sits at 100.0% of its HIP-3 open-interest cap — $24,011,199 against
$24,000,000 — with $42k of asks and $15k of bids behind $24M of position, and 85% of a $100k order unfillable. At the
cap, open interest cannot grow, so a buyer can only be filled by a long closing: the cap turns the price into a queue
and the premium is what the queue costs. That is the third system this week — after cross-chain dollar switches and
Aave's midnight USDC reserve — where the binding constraint was the size of the door rather than the size of the prize.

**And the dead half.** Six of ten builder DEXes carry zero open interest across 97 listed markets, each behind a
500,000-HYPE stake locked for 183 days.

Open: funding is a *rate*, and a rate's worth is its size times how long it holds. The findings ledger tracks
recurrence for EVM findings; funding needs the same, keyed on `(dex, coin)`.

## Session log — 2026-09-08 (ten hours across midnight: a sentence becomes a detector)

A trailing ten-hour window (2026-09-07 22:26 -> 2026-09-08 08:26 UTC, 2,993 blocks, 675,675 transactions) chosen so it
spans 00:00 UTC, because the one thing every previous window could only see a fragment of is the nightly routine.

Landed: `detectors/liquidity_blackout.py`, `fee_census.py --every N` (regular subsample + a diurnal series),
`window_events.py` blob inboxes now fall through to the label registry, and six registry entries.

**The routine, traced end to end.** The blackout detector inverts each reserve's published borrow rate through its own
IRM to recover the utilisation the pool was priced at, then reports episodes where withdrawable liquidity collapses
*with their clock time* — because an episode that recurs at the same minute is a schedule, and a schedule is a fact you
can plan an exit around. It fired on the first window that could hold one: **Aave v3 USDC, 23:47–00:08, 21.6 minutes,
99.9976% utilisation, $55,371 withdrawable on a $2.31B reserve.** Following it through the window's transfers gives
every leg: 23:35:47 an EOA redeems $245,571,215 of sUSDS to USDC atomically through Sky's plumbing; 23:37:47 a second
withdraws **$151,780,227 from Aave, 100.16% of the reserve's free liquidity**; both feed one hub; 23:41:23 the hub sends
**$397,310,079** to a third address; 00:03:59 it comes back; by 00:09:35 both positions are rebuilt to the dollar.
Nothing traded, nothing earned, all five addresses hold zero USDC now. Cost to the operator: ~$900. Cost to Aave's USDC
borrowers: **$8,879**, of which $8,214 reached the suppliers who stayed.

**The fee-market claim survived a full diurnal cycle.** Burn $11,334 against $75,713 of priority fees over ten hours, a
**6.68x** ratio (6.92x on the hour), never under 4.4x in any half-hour bucket, with fullness pinned between 49.8% and
52.0% and the median base fee in a 0.045–0.072 gwei band. 54.3% of gas tips at or under 0.01 gwei; 17.6% goes to four
unverified batch contracts paying $9. **And one row of the previous report was mislabelled**: "35.6% of gas paid exactly
zero" used a 0.001 gwei cutoff. Strictly, that hour reads 9.0% exactly zero and 44.6% at or under 0.01 — the claim is
unchanged and now confirmed at ten-hour scale, the label was wrong, and both the repo report and the published artifact
are corrected.

**Two labelling gaps closed by the same window.** `solver_fingerprint` had been reporting the **sUSDS token contract**
as "an unlabelled bot cycling $249.6M"; and `window_events.py` printed the largest blob poster on Ethereum — Robinhood
Chain's SequencerInbox, 4,998 of 18,394 blobs, ahead of Base and OP Mainnet — as "(unlabelled)" in every digest since
the Orbit study, because it kept a hand-written table beside a registry that already knew the name. The registry edit
made `verify` refuse to compare a number until `analyze` was re-run, which is the staleness gate working as designed.

**Signal on the rest of the window: none.** One liquidation, for $1 of debt, in ten hours. Every dollar peg inside 30bp.
JIT liquidity took **$236 of $224,564** of pool fees — 0.11%, against the tax it is usually described as.

## Session log — 2026-09-08 (ten chains at once, and the denominator that was wrong everywhere)

The loop had only ever run one chain at a time, which is a real blind spot for a *dollar*: USDC on Base and USDC on
Ethereum are the same claim on the same issuer, bridgeable in minutes for approximately nothing, so their lending rates
are two prices for one asset. This pass built the cross-chain layer and used it on a fresh hour
(2026-09-08 06:23–07:29 UTC): Ethereum block-by-block plus a logs-only trailing hour on ten EVMs.

Landed: `scripts/multichain.py` (collect / head / issuance / analyze / verify / render — discovery-first, no asserted
pool, bridge or token addresses), `scripts/fee_census.py`, and an `url=` parameter on `live_rpc.RPC` so several
networks can be live at once.

**The finding.** USDC pays 4.00% on Base and 0.36% on Scroll at the same instant — 3.64 percentage points across
$2.78B — and the whole thing is worth **$177,794 a year**. Two corrections get there and both are the point: the high
side dilutes along its kinked curve, and *the low side may not let you leave*. Optimism's USDC reserve pays 2.56% on
$11.3M of which **$2.3M is withdrawable**, so the $18.5M the curve calls optimal cannot be moved at an eighth of that
size. Capacity is `min(high-side optimum, low-side withdrawable)`, and for seven of twenty switches the second binds.
Filled once, cheapest source first, $8.73B of cross-chain dollars absorbs **$37.3M at 48bp**. Taking the rows
independently would claim $279k — 57% too high, because every row assumes the destination reserve is empty.

**The bridge is not the arbitrageur.** Net CCTP flow ranks **−0.57** against the USDC rate over eight chains: the two
highest-paying chains were the only net exporters. Eight addresses appear on both sides of the bridge among the largest
counterparties, which is inventory rebalancing toward demand rather than capital chasing yield. And 62% of CCTP sends
left for domains outside the scan entirely.

**The denominator was wrong on every chain, and version-dependently so.** Every capacity, width and best-size number
this repo computes rests on utilisation, read as `variableDebt.totalSupply() / aToken.totalSupply()`. That is not what
Aave prices with. Ethereum and Base reproduce their published borrow rate from the aToken total; Avalanche reproduces
it from `getVirtualUnderlyingBalance()` plus debt, the gap being unbacked aTokens. On Avalanche's GHO reserve the gap
is 0.46pp of utilisation, it straddles the 90% kink, and it is worth **151 basis points of borrow rate** — the aToken
ratio says 4.50%, the pool says 6.00%. Utilisation is now **inverted from the pool's own published borrow rate**, which
is correct whatever the deployment version. Three smaller ones fell out of the same verifier: a reserve factor of 1.0
is a mint facility, not a supply market (Aave's $135.2M Ethereum GHO reserve, which produced the largest switch on the
first pass, $12,798/yr, entirely imaginary); a flat IRM carries no information about utilisation and cannot be
inverted; and two tokens on Arbitrum both answer `symbol()` with "USDC", so switches are keyed by reserve address.

**Ethereum's fee market has stopped pricing blockspace.** Base fee 0.049 gwei at 50.6% fullness: the chain burned
0.443 ETH ($1,098) in the hour while users paid 3.068 ETH ($7,598) in priority fees, a **6.92x ratio**, of which
98.5% is spend above the gas-weighted median tip of 0.0087 gwei. **35.6% of all gas paid exactly zero.** The largest
single consumer of Ethereum blockspace was **XEN** batch-minting — 8.2% of the chain-hour for $2 of tips. Blocks are
half full because the marginal buyer of blockspace is an activity that only exists at a gas price of zero, which is
why the price stays at zero. Open item, and the first one in the next-steps list: `economics.py` charges gas at the
base fee and therefore understates an inclusion-sensitive leg by roughly sevenfold in this regime.

## Session log — 2026-09-08 (the output: a strategy book, and what the dollar surface is actually worth)

The loop's stated output is insight and proposed strategy. The roadmap had described only machinery, so this pass
built the terminal artifact and then used it, on a fresh two-hour window collected for the purpose (2026-09-07
21:27–23:27 UTC, 599 blocks).

Landed: `scripts/strategies.py` + `research/strategies.jsonl` (the strategy book — legs, capacity, **kill criteria**,
and a quote series so decay is visible), `scripts/seed_strategies.py`, `detectors/dollar_rate_outlier.py`, reserve
discovery via `getReservesList()` in `head`, per-reserve IRM parameters, and sampled Compound supply curves.

**The finding.** Measured against the risk-free dollar — Sky's savings rate, 3.60%, unlimited size, no venue risk —
exactly **two of twenty-seven dollar reserves** across Aave, SparkLend and Compound pay more than doing nothing. About
$8.5B of supplied dollars sits in reserves paying less than the issuer's own savings rate. And the two that clear it
are tiny: Compound v3 USDC sits 0.77 percentage points above a kink at exactly 90.0% utilisation, so its whole
5.69% headline is **$1.25M wide and worth $14k a year**; Aave's USDtb reserve is $227k wide and worth $5.4k. The best
two dollar rates on mainnet are jointly worth about $19,000 a year.

**Three bugs in this repo's own machinery, each of which changed a number.** The de-spiker read index 2 of each rate
point — the *borrow* rate — when de-spiking a *supply* rate, and survived because both sides were wrong in the same
direction (USDT gap 1.66pp → 0.98pp). The venue pair was selected on spot rates and de-spiked afterwards, so during
Aave's nightly utilisation spike the comparison became Aave-over-Spark, was correctly dismissed as an artifact, and
the real Compound-over-Spark finding was never compared at all — the spike hid a true finding rather than adding a
false one. And capacity was modelled with a smooth `r·S/(S+X)` curve on markets that have a cliff, reporting
**$93.8M of capacity worth $945k a year** for Compound USDC against a true **$1.4M worth $15k**, a 63x overstatement
of the number that decides whether a strategy is worth doing. All three are fixed and the detector's ladder now
reproduces `getSupplyRate` to two decimal places.

**The nightly routine, caught live.** At 23:41 UTC Aave's $2.16B USDC reserve stood at exactly 100.0000% utilisation
with **$503 of available liquidity**, after an account withdrew ~$152M of supply. The 12.87% it prints is worth about
$55 on $10M over the half hour it lasts; the finding is the other side — USDC cannot be withdrawn from Aave for
roughly thirty minutes every night, which is a hard constraint on any strategy whose exit leg is that reserve, and it
is now recorded as a risk on that strategy rather than as prose.

**What the book says about the loop.** Seven live strategies, two retired on economics. The largest edges are the
smallest positions: the 15.8% LP is a $150k idea, and the $1B-capacity idea pays 3.48% and is a savings account.
Nothing in the book is simultaneously large and mispriced. And only three of seven carry a quote a detector produced —
the rest were measured once in a dated session, which is the same failure the findings ledger fixed for findings.

## Session log — 2026-09-08 (the loop closes: staleness, claim tags, ledger, three detectors)

Landed: `scripts/provenance.py` (what an artifact was built from, and a hard gate on it), `scripts/findings.py` (the
findings ledger with recurrence, decay and a recheck cadence), three new detectors — `solver_fingerprint`,
`jit_liquidity`, `mass_distribution` — `labels.py adopt-shapes` (detector → registry), `live_scan pipeline` (the four
steps in dependency order), verify recipe ids with `[[verify: id]]` claim tagging, a fourth mechanism assertion, and
`scripts/test_findings.py` (13 tests over the two new bookkeeping modules).

**What it found, which is again the point.** The `mislabelled_flow` detector had been reporting the same address at
high severity on both 2026-09-07 windows: [0x3cc936b7](https://etherscan.io/address/0x3cc936b795a188f0e246cbb2d74c5bd190aecf18),
tagged `exchange_deposit` by the day study's behaviour profile. It is an externally-owned account that collects small
inbound legs and forwards them in one large one — $99.99M of USDC in a single transaction on the five-hour window, to a
verified Gnosis Safe that forwarded the whole amount on again. Counting that leg as exchange outflow is wrong under
either reading: if the address is an exchange deposit address, the sweep goes to exchange infrastructure and the leg is
internal; if it is not, the leg is not exchange flow at all. Both readings agree, so the tag was retired without having
to settle the identity.

| headline, 2026-09-07 five-hour window | with the deposit-sink tag | corrected |
|---|---:|---:|
| exchange net flow, stables | −$24.8M | **+$75.2M** |
| exchange net flow, USDC | −$97.9M | **+$2.0M** |
| label band, model-memory → behaviour | +$91.6M → −$24.8M | +$91.6M → +$75.2M |

That is the third mislabel of this family, after the CoW settlement contract and the deposit-sink rule itself, and the
first found by a detector rather than by hand. The label band this repo introduced last session to flag its own
uncertainty turns out to have been measuring one bad label: with it gone, the band no longer changes sign.

**The staleness gate proved itself immediately.** Adopting nine shape labels changed the address book, and `verify` on
both windows refused to compare a single number until `analyze` was re-run — which is the behaviour that had to be
enforced by hand twice on 2026-09-07.

**The ledger says which findings are structure and which are noise.** Across the two windows: 47 findings, 22 recurring,
9 closed by labelling. The decay column shows what a single window cannot — the Compound-versus-Spark USDC gap widening
0.87% → 1.41% while the Sky SSR gap held flat at 3.48% — and `seen 1/2` marks every finding that a later sweep, running
the same detector, did not see again.

**The detectors found things the hand analysis had missed.** `mass_distribution` surfaced 0.0003 USDT sent to 12,056
addresses by one sender — token-transfer address poisoning at a scale the native-ETH poisoning detector cannot see.
`solver_fingerprint` characterised the whole unlabelled tail: the top three entries pass $1–9B straight through, each
with one or three counterparties, and `verify`'s new `fingerprint-matches-chain` assertion confirms against Blockscout
that the detector's contract-versus-account calls were right on every hit where it committed to one, and declined to
guess on the rest.

## Session log — 2026-09-07 (infrastructure pass)

Landed: `scripts/window_raw.py` (an independent raw-window reader), `scripts/labels.py` (provenance registry, coverage,
resolver, audit), `scripts/verify.py` (13 numeric re-derivations + source-backed mechanism assertions + a label band),
`scripts/economics.py` (capacity/gas/competition/decay scorer, 24 unit tests), `scripts/detectors/` (registry + four
detectors), and `live_scan verify` / `live_scan detect`.

What it found, which is the point: the deposit-sink heuristic in `load_address_book` tested `sent == 0`, meaning
"originated no transactions" — a condition every *contract* meets structurally. The rule was therefore "any busy
contract is an exchange deposit sink", and it tagged 25 addresses of which 22 forwarded value, including the CoW
settlement contract, the Uniswap Universal Router and a Relay bridge depository. Their inflow counted as exchange flow
and their receipt of borrow proceeds as leverage-to-exchange. Corrected to test forwarding directly, on the 2026-09-07
midday window with nothing else changed:

| headline | before | after |
|---|---:|---:|
| exchange gross inflow, USDC | $823.2M | $497.1M |
| exchange net flow, stables | +$44.0M | +$13.2M |
| exchange net flow, ETH | −$17.4M | −$19.6M |
| leverage-to-exchange | $4.0M | $0 |

The verify pass then earned its keep a second time within the hour. A parallel study reclassified the wallet this repo
called an "exchange hot wallet with USDG desk" as the Relay solver it turned out to be, and `verify` failed immediately
on the two windows because their `analysis.json` predated that label. That is the intended behaviour: a stale analysis
against a changed registry is drift, and it now announces itself instead of sitting in a report.

And the label band on the five-hour window shows why provenance had to be explicit: net stable flow is **+$91.6M** using
model-memory labels alone and **−$24.8M** once behavioural labels are included. The sign of a headline depends on which
unverified labels you trust, so `verify` now reports the band rather than one number.

## Where we are

Strengths, honestly: a clean separation of a deterministic feature layer from an LLM narrative (`analysis.json` +
tables vs `insights.md`); growing registries (`type_registry.py`, 90 types); a fork-proof habit (CooldownArb,
captive-flow LP, StacyFarmer) that turns a thesis into an executable, checkable artifact; per-round reproducibility in
`tx_types.py` (`rounds.json`). Collectors (`eth_day_collect`, `live_collect`), a broad feature engine (`live_scan`),
and offline digests (`window_events`, `window_followups`, `corevault_scan`).

Weaknesses, updated 2026-09-08. Most of the 2026-09-07 list is now closed: claims are verified against an independent
re-derivation, mechanisms are re-runnable assertions, one-off scripts have become seven detectors, opportunity economics
run through one scorer, and a stale artifact announces itself. What remains, in the order it bites:

* **Data access is still the binding constraint.** No trace or archive endpoint means the CoreVault bytecode
  fingerprint and any balance-delta test cannot become detectors, and fork tests only run at latest. This blocks more
  planned work than everything else combined.
* **Head reads are still spot** where the venue emits no logs. Compound and Sky publish no `ReserveDataUpdated`, so
  three of the six standing rate findings carry "one-block read, de-spiking unavailable", including the two largest.
* **Labels remain mostly behavioural and model-memory**, and the fourth mislabel found (2026-09-08) moved a headline's
  sign. The detector now catches this class automatically, but catching is not preventing: 30% of window USD still
  touches an address the registry cannot name, and `adopt-shapes` can only file the half of that tail whose shape
  settles the question.
* **Coverage of prose by verified recipes is about half.** `verify` now counts it, which is the first step, but the
  tape prices, blob counts, gas-share arithmetic and health factors in every note are still single readings.

## Recommendations, prioritised

Each: **problem observed → proposal → interface → effort → payoff.**

### P0 — correctness (do first; wrong numbers poison everything downstream)

**1. Verified, provenance-tracked labels registry.** *Done — `scripts/labels.py`.*
Problem: `load_address_book` derives hot-wallet/deposit-sink tags from behaviour + memory; a settlement contract or a
token treasury reads as a CEX. Proposal: `scripts/address_labels.json` (done) with `{label, kind, source}` where `kind`
∈ {exchange, exchange_deposit, protocol, venue, vault, bridge, issuer, treasury, token, mev_bot}; `live_scan` counts
only exchange kinds as exchange flow and never chases borrowed funds through a labelled venue. Next: a `scripts/labels.py`
that fetches Blockscout verified names and known-canonical sets (routers, settlement, CCTP/OFT, bridge inboxes) on
demand and writes provenance, plus a coverage report (what fraction of window USD flows through labelled vs unlabelled
addresses). Effort: S (seed+wiring done), M (fetcher). Payoff: **demonstrated** — leverage-to-exchange corrected
$25.7M → $5.3M, RLUSD net −$101.6M → −$0.9M, on the 2026-09-07 window with no other change.

**2. Time-weight and de-spike every head read.** *Partly done — inside `detectors/rate_dispersion.py`.*
Problem: the midnight Aave routine and flash bots spike `currentVariableBorrowRate`/reserves 3–10x for a single block;
`head` reads spot, so any rate the narrative quotes can be a one-block artifact. Proposal: read reserves/rates as the
median over the last K blocks (the raw window already has the series), and flag any single-block read that coincides
with a same-block flash loan or a >$10M same-reserve flow. Interface: `head_state.json` gains `{spot, twap_k, spiked}`
per reserve; the tables show TWAP and mark spikes. **Shipped** where it decides something: the rate detector quotes the
median of the window's `ReserveDataUpdated` series and demotes any gap it could not de-spike to `info`. That correctly
demoted the SparkLend USDT 3.05pp gap — the ALM shock that normalised within the hour — below the Compound USDC gap that
held all window. *Still open*: `head_state.json` itself still stores spot values, and Compound and Sky emit no
comparable logs, so their reads cannot be de-spiked at all. Effort: M. Payoff: removes a whole class of false rate findings.

**3. A findings-verification pass (adversarial verify).** *Done — `scripts/verify.py`.*
Problem: headline numbers carry my confidence label but nothing re-derives them; mechanism claims are trusted prose.
Proposal: every headline number carries a machine-checkable recipe (a small closure: raw inputs → value) and a `verify`
step recomputes it from raw and fails loudly on drift; for a mechanism claim, `verify` pulls one `debug_traceTransaction`
or the verified source and asserts the *specific* fact (e.g. "depositFor does not set lastDepositBlock", "the $759 comes
from the Balancer leg"). This is the code-review "confirm each finding by re-deriving it" pattern applied to research.
Interface: `live_scan verify --out <window>` prints a pass/fail table and writes `verify.json`; exit code is non-zero on
any failure. **Shipped**: 13 numeric checks re-derived through `window_raw` (blocks, transactions, logs, USDC mint and
burn, exchange net flow for stables and ETH, gross USDC inflow, leverage-to-exchange, the largest CCTP send, top gas
target and its gas, the widest borrow-rate gap), all passing on both 2026-09-07 windows in about 8 seconds; three
source-backed mechanism assertions (`stacy-deposit-for` fetches the verified source and asserts `depositFor` does not
write `lastDepositBlock`; `msca-not-exchange`; `no-contract-hot-wallets`); and the label-provenance band.

Writing it caught two decoder bugs immediately: only the CCTP **v1** `DepositForBurn` topic was being watched, so every
v2 send was silently dropped, and the destination domain was being sniffed rather than read from its fixed word.
*Extended 2026-09-08 with a third class of check.* The numeric checks re-derive window aggregates through a second
code path, but `head_state.json` — where every rate and yield in every note lives — had no second path to read it
through and so was simply asserted. **Identity checks** cover it: the protocols publish relationships between the
fields they report (a supplier earns the borrow rate times utilisation less the reserve factor; a borrow rate is the
IRM curve at that utilisation; a Morpho supply APY carries the market fee instead; a PT's implied yield is a function
of price and maturity; the Compound read must lie on the curve sampled at the same block), and re-deriving one field
from the others tests the whole decode — word offsets, ray scaling, config bitmaps, curve parameters — against the
chain's own arithmetic. Seven classes and 188 individual identities pass on the 2026-09-08 windows, the last of them a genuine second
opinion rather than an internal one: `head-nav-crosscheck` reads each exchange rate a second way on chain — an
ERC-4626 vault's share price against its own `totalAssets / totalSupply`, `wstETH.stEthPerToken()` against
`stETH.getPooledEthByShares`, rETH's and weETH's share conversions — and the five that publish a second view agree to
twelve decimal places. Three (cbETH, ezETH, rsETH) publish none, so the check reports how many rates it could compare
rather than implying it checked them all. Setting Aave's USDC supply APR to its
borrow value — the exact shape of the rate-series bug found earlier the same day — fails `head-supply-identity`
immediately, naming the venue, asset, utilisation and reserve factor. It also found a reproducibility defect on its first run against fresh
data: `days_to_maturity` was stored rounded while `implied_apy` was computed from the unrounded value, so the artifact
did not reproduce its own output — a residual of 2e-6, and exactly the class of thing these checks exist to surface.

*Closed 2026-09-08*: every check now carries a stable id, a sentence cites it as `[[verify: exchange-net-stables]]`,
and `verify` fails on a citation with no matching check and counts the headline numbers that cite nothing — 55% of the
midday note's big numbers are tagged, 46% of the five-hour note's, and the untagged remainder is now visible rather
than assumed. A fourth mechanism assertion, `fingerprint-matches-chain`, checks the new tail detector's
contract-versus-account calls against Blockscout on every hit where it commits to one. Effort: M–L.
Payoff: **the single biggest quality lever** — it makes the confidence labels earned, not asserted.

### P1 — leverage (build the flywheel that compounds)

**4. Detector registry.** *Done — `scripts/detectors/`.*
A source-free bytecode fingerprint (selector cluster + non-standard event topic + normalised code hash) that identifies and
enumerates CoreVault forks on any chain — the template for detectors that run every window and grow like the type registry.
Problem: the JIT test, the midnight routine, the poisoning matcher, the gas-hog attribution, `corevault_scan`, the
leverage pipeline are one-off code, not reusable detectors. Proposal: `scripts/detectors/` where each detector is a
module exposing `scan(window) -> [hit]` with `{severity, evidence, economics_ref}`; `live_scan` runs the whole set every
window and the registry grows the way `type_registry` did. **Shipped**: `detectors/__init__.py` holds the registry, a
`Hit` type and a shared `Context` that materialises the block and transfer streams once; `run.py` sweeps a window and
writes `detectors.json` + `detectors.md`. Four detectors so far — `mislabelled_flow` (label claims the window itself
refutes), `gas_concentration` (base-fee spikes attributed to the contract whose gas demand caused them),
`rate_dispersion` (de-spiked cross-venue gaps priced through `economics.py`), `address_poisoning` (lookalike dust after
a large transfer). A ninth landed the same day and is defensive rather than economic: `honeypot_signature` finds tokens whose buyers
cannot sell, from the window alone. Receipts are not collected, but a reverted transaction emits no logs, so a failed
sale is visible as an absence — against a measured 4.4% base rate for router-targeted transactions that emit nothing.
Its three signals are individually useless and jointly discriminating, and the write-up in
`research/2026-09-08/honeypots/method.md` records three wrong versions that each produced a confident false answer: a
99% sell tax on WETH, a 30% tax on MANA, and a 70% failure rate on Centrifuge's CFG. On seven real windows it now
proves no honeypot and makes no high-severity claim, so `scripts/test_honeypot.py` builds synthetic windows where the
answer is known to show it can still fire — and that positive control caught a real bug in the denominator, which had
been counting buys as attempted sales.

Three more landed 2026-09-08: `solver_fingerprint` (the unlabelled tail, split by shape into
pass-through, cycling and retaining, with contract-versus-account proven from the window and reported as unknown when
the window cannot prove it), `jit_liquidity` (the share of pool fees taken by liquidity that arrived for one swap, per
pool and per window, with the operator economics priced as a race), and `mass_distribution` (one sender fanning a token
to thousands of recipients — airdrop, mint distribution or dust spam). The generalised gas detector **rediscovered the
tokenized-stock router** on the five-hour window without being given its address; `mass_distribution` found a
12,056-recipient USDT dust campaign the hand analysis of the same window had missed; and `mislabelled_flow` found the
fourth label bug. Effort: L. Payoff: every window automatically re-checks every past discovery; the system stops
forgetting.

**5. Standard economics harness.** *Done — `scripts/economics.py`.*
Problem: capacity, gas, capital, competition and decay are computed by hand for each opportunity, so results aren't
comparable and dust isn't auto-flagged (Stacy looked mechanically live but is gas-break-even). Proposal: `scripts/economics.py`
— given a strategy's legs `{size, price_impact_curve, gas_units, capital_locked, competitors, decay_per_run}` it returns
capacity-adjusted net APR, break-even size, and a go/no-go. **Shipped**, with four modelling distinctions that each
changed an answer: a flat per-run reward (`edge_usd`) is not bps on notional, so the StacyVault harvest prices at $7.42
a run and is auto-flagged as dust; a *race* pays gas on losing attempts while a held position does not; break-even is
searched below the optimum because impact makes net non-monotonic in size; and a stable pool takes an `amplification`
so a Curve leg is not charged constant-product impact. All four known opportunities now rank in one table, and
`rate_dispersion` reports through it with a dilution curve derived from the pool's own size. Effort: M.
Payoff: honest, comparable rankings; the loop stops chasing dust.

**6. Data-access layer with a capability map and cache.** *Started this session (`scripts/etherscan.py`).*
An Etherscan V2 client now fetches verified source across chains from one key (BSC/Base/Polygon/Arbitrum/Ethereum), with
a per-chain public-RPC map for reads, and it already encodes a capability nuance the layer must generalise: the free tier
serves `getsourcecode` everywhere but gates `account`/`proxy`/`logs` to a few chains. Extend it into the full layer.
Problem: this session hit Infura archive gaps, dRPC free-tier timeouts on historical state, Blockscout proxy rate limits,
forks that only work at latest, and BSC/Polygon behind keys. Proposal: `scripts/rpc.py` unifying Infura + dRPC + public
endpoints with a per-chain capability table (which endpoint serves archive / trace / getLogs / at-block state), automatic
fallback, and an on-disk cache of fetched sources, labels and eth_calls. The **#1 missing capability is a trace+archive
endpoint** — it blocked bot balance-deltas and historical-block forks all session. Effort: M–L. Payoff: fork tests at any
block, trace-backed verification, fewer dead ends.

### P2 — breadth and rigour

**7. Multi-chain abstraction.** *Started (`corevault_scan` `CHAINS` presets); Solana port landed 2026-09-07.*
The Solana port (`solana_rpc` / `solana_collect` / `solana_decode` / `solana_scan` / `solana_followups`, label registry
`solana_labels.json`) reproduces the live-scan deliverable on a non-EVM chain with the same contract: deterministic
`analysis.json` + tables, LLM `insights.md`, `verify` re-deriving the headline numbers. What it taught: the "interesting
things" lens must be chain-specific (payer-centric kinds, per-program bot-shape columns, fan-in/fan-out hubs) while the
deliverable shape stays identical; the data-access layer (item 6) must carry per-provider bandwidth caps (GetBlock ~2.7 MB/s
from this machine) as well as method capabilities.
*2026-09-10, second Solana window:* the port became a loop member rather than a one-off. `solana_detect.py` runs 13
Solana detectors over `analysis.json` + `head_state.json` (wash volume by venue, quote posters, failure bots, fan-in hubs,
launch factories, flash-loan spam, liquidation drought, exchange flow, unknown CCTP domains, dust senders, large moves,
LST NAV basis, stable rate gaps) in the Ethereum `Hit` shape, so `findings.py ingest --chain solana` folds them into the
shared ledger; `diff` writes the window-over-window change table the narrative starts from; `solana_daily.py` chains
collect → verify → head → prices → analyze → detect → diff → render → ingest unattended (launchd template). Ledger keys
are the persistent things (program, venue, hub, asset pair), never a pump mint. Not yet done from the 09-07 request list:
same-block self-match by funder, marginfi on-chain banks, Kamino borrow caps, a second RPC region.
Problem: the deep tooling is Ethereum-only; the fresh forks (VCORE's `$AAPL` pool, Arbitrum candidates) are cross-chain,
and BSC is the historical home of the CORE family. Proposal: promote the `CHAINS` preset pattern into the collectors and
`live_scan` (per-chain blue-chip sets, factories, blob inboxes, RPC). Effort: L. Payoff: the meme waves that spawn these
setups are multi-chain; single-chain coverage misses most of them.

**8. Findings ledger with recheck cadence.** *Done — `scripts/findings.py`.*
Problem: findings are point-in-time; only the midnight routine is tracked daily. Proposal: `research/findings.jsonl`, each
finding an id + a recheck cron + a realized-vs-predicted log. **Shipped**: a finding is identified across windows by
`detector:key`, so the same rate gap on Monday and Tuesday is one finding observed twice; `research/windows.json` records
which detectors ran in each ingested window, which is what makes *absence* mean something — every finding reports
`seen / eligible` rather than a bare count, and a gap at 1/4 is visibly a spot artifact where 3/3 is a standing
dislocation. Economics-bearing hits keep their predicted net APR per observation, so the report prints a decay column.
`close` records why a finding was answered (nine were, by `adopt-shapes` labelling their addresses) so it stops
appearing in `due`. Effort: M. Payoff: **demonstrated** — 22 of 47 findings recur across two windows, and the ledger
flagged the 0x3cc936b7 mislabel as recurring before anyone looked at it.

**9. Signal-testing harness with controls and multiple-hypothesis correction.**
Problem: the informed-flow test (does exchange netflow predict returns) was run once, ad hoc, and found null. Proposal:
generalise the hash-sampled controls already in `amount_outliers`, require out-of-sample and FDR control before any
"signal" is reported. Effort: M. Payoff: stops the loop from over-fitting a five-hour window.

**10. Reproducibility manifests everywhere.**
Problem: some follow-up scripts are path-hardcoded. Proposal: every artifact carries `{code_sha, registry_sha, block_range,
price_basis}` the way `tx_types` `rounds.json` already does. Effort: S per script. Payoff: any report is replayable and
diffable.

## Do next (concrete)

Items 1, 2, 4 and 5 of the previous list are done; item 3 is done except for the two detectors that need the RPC layer
or a window that spans midnight. What this pass exposed, in priority order:

1. **A window that spans midnight, so the midnight-routine detector can be written and fire.** Every window collected
   so far runs 02:39–12:39 UTC, and the daily 23:30–00:20 balance routine — the most reliably recurring mechanism this
   project has found — is the one thing the detector registry still cannot re-check. It needs a collection, not code.
2. **De-spike `head_state.json` itself.** `rate_dispersion` de-spikes what it quotes, but the head file still stores spot
   values and Compound and Sky emit no `ReserveDataUpdated` logs, so their reads cannot be de-spiked at all. Three of the
   six standing rate findings are marked "one-block read, de-spiking unavailable" for exactly that reason, and the two
   largest by predicted APR are among them.
3. **Close the loop on the `retains` half of the tail.** `solver_fingerprint` splits unlabelled addresses into
   pass-through and retaining, and `adopt-shapes` only files the first kind, because a shape claim cannot settle what a
   retaining address is. Those are the ones whose mislabelling moves headlines — 0x3cc936b7 was one — so they need a
   cheap identity route: funder graph, first-funding transaction, or a counterparty-set match against known exchange
   infrastructure.
4. **The data-access layer (item 6).** Partly resolved, and the standing claim here was too pessimistic. The public
   dRPC endpoint answers *historical state* per call: during the 2026-09-08 bytecode study it returned
   `eth_getTransactionCount` for an address at 1, 7, 30, 90, 180 and 270 days back, and a binary search over
   `eth_getCode` dated two contract deployments to within a block. That is enough to age an actor and to date a
   deployment — it turned "an unlabelled address sent 2,258 transactions" into a six-month history with a measured
   ramp. What it will not do is bulk: it answers 403 to a batched JSON-RPC request, so an archive read is one call at a
   time and only affordable for a handful of pinned questions. Traces are still missing, so CREATE2 children remain
   invisible and the JIT balance-delta test still cannot become a detector.
5. **Signal-testing harness (item 9).** The ledger now produces exactly the input it needs — a repeated observation of
   the same finding with a predicted number attached — so out-of-sample and FDR control on "does this edge persist" is
   the natural next build after a few more windows accumulate.

## The output the loop is for

Everything above is machinery. The loop exists to produce two things, and the roadmap had not named either until now:

**Insight** — a claim about how a market works that is true, capacity-aware, reproducible and dated. The system's
apparatus for this is in place: `analysis.json` for the numbers, `verify` to re-derive them, the detector registry to
re-check the mechanism next window, and the findings ledger to say whether it recurred.

**A proposed strategy** — a claim about the *future*: that a mechanism will keep producing an edge, and that the edge
survives gas, impact, competition and decay at a size worth deploying. This is a different object from a finding and
needs three things a finding does not: legs that `economics.py` can price, falsifiable **kill criteria**, and a **quote
series** so decay is visible rather than remembered.

`scripts/strategies.py` and `research/strategies.jsonl` are that book. Its first honest reading, seeded 2026-09-08 with
every strategy this repo has produced, is the diagnostic the loop needed: nine strategies, two retired on economics,
two fork-proven, and **only three whose numbers a detector re-prices automatically**. The rest were measured once in a
dated session and have not been re-measured since, which is exactly the failure the findings ledger was built to stop
for findings and had not yet stopped for strategies. A strategy backed by a detector stays current for free; a strategy
backed by a bespoke scanner decays into a memory the moment the session ends.

Excluding the savings rate, which is the benchmark rather than an edge, the whole book measures at **about $229,000
a year**, of which **$125,600 survives its own detectors' verdicts** — and that is the point of building it. The
$103,500 difference is one row: the sUSDe redemption trade, the largest edge in the book, declined by a significance
test written the same day. Its 4.7bp net edge was measured across a window whose p10-to-p90 price spread was 5.4bp,
so the discount is not distinguishable from where the asset traded. A book that reports that is worth more than one
that reports 17% a year. Every row now has legs `economics.py` priced, a capacity that came
from a rate curve, a withdrawable balance or a traded volume rather than a headline size, and a kill criterion. An
efficient market is supposed to look like this; the value of the loop is that the number is derived rather than
asserted, and that it moves on its own when the market does.

The book also disciplines the reading of a finding. A cross-venue rate gap is only an opportunity if the *higher* venue
clears the risk-free dollar, and most do not: "PYUSD pays 3.29pp more on Aave than SparkLend" is worth 28bps over the
actual alternative, and "DAI pays 0.61pp more on Aave than SparkLend" compares two rates that are both below the
savings rate. `dollar_rate_outlier` exists to make that comparison the default one.

That gives the next round of detector work a clear ordering principle: **write the detector that re-prices the highest
strategy in the book that nothing re-prices.** The first of those is done — `detectors/lp_marginal_yield.py` prices a
concentrated-LP position at the band the price stayed inside, at real size, net of the divergence the same
concentration amplifies, and it gave the captive-flow LP its first automatic decay series (15.80% hand study → 6.13%
→ 10.37% → absent, zero swaps in a two-hour window). The second is done too — `detectors/nav_discount.py`
compares what a protocol pays on redemption against what the market paid for the claim, and separates the two with the
three things that decide whether a discount is a trade: the measured round-trip cost (the sUSDe path is −2.7bp, which
is 38% of a 7.1bp discount), the *availability* of the redemption leg (rETH's larger 17.7bp discount is demoted
because Rocket Pool's burn pool is empty most of the time), and capacity taken as the volume actually offered rather
than pool depth. Five of the seven strategies now re-price themselves. The third is done as well: `head` now discovers Pendle markets from
the window's own `Swap` logs — the markets with live flow, no hardcoded list and no API — and
`detectors/fixed_vs_floating.py` classifies each implied yield as a *term premium* (the floating rate on the same
underlying is readable, so the gap is a rate view) or a *credit spread* (it is not, so the excess is the price of an
issuer's credit that nothing here has assessed). Every Pendle market that traded in the 21:27–23:27 window was the
second kind, at 6% to 23%. And the fourth: `detectors/borrow_cost.py` ranks the cheapest venue to
borrow each dollar and caps the saving at the liquidity actually withdrawable there, reading Morpho Blue's isolated
markets from the window's own event topics. **All seven strategies now re-price themselves; none is a hand
measurement.** The last one to fall was the largest: "borrow USDT on Morpho rather than Aave" was quoted at 91bp on
$24M and measures at 1.46pp on $6.35M — a wider rate on a quarter of the size, because $24M was the vault and $6.35M
is what is withdrawable, and the cheap market lends only against sUSDS at 96.5% LLTV, which the hand note never said.

Two gates were added after the loop fell into the gap between them. `head_state.json` is an input to `analyze` — the
whole window is priced from it — and it was not fingerprinted, so re-running `head` silently re-priced an analysis
that was not re-run, with labels and tokens both unchanged and no gate able to see it. `head` is now a provenance
gate, and `head` itself refuses to read current state for a window collected long ago rather than mixing two
timeframes.

## Anti-goals

Read-only research, no execution service — the fork proofs stay proofs. Exact numbers live in code; prose only interprets,
with stated confidence that `verify` has to earn. Coverage % is a diagnostic, not the goal; the goal is verified,
capacity-aware insight that compounds into detectors.
