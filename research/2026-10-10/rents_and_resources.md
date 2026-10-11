# Rents, scarce resources, and where non-racing alpha lives — synthesis, 2026-10-10/11

The user asked for new and unique approaches to profitable strategies that do not race on speed or block position. This
session took the repo's one robust lesson and turned it into a search method:

- **The lesson.** What survives is a rent paid by someone with a non-price motive.
- **The method.** Size the rents top-down (the rent map). Ask what scarce resource collects each one. Test the
  under-collected ones from history under the same protocol as before.

The protocol: chosen on the past, tested once, costs and capital explicit, capacity measured, late entry measured.
Nine studies ran; every headline was re-derived by the coordinator from raw files.

## The frame

A participant without a speed edge earns only by supplying something another participant needs and cannot easily get
elsewhere. Five such resources showed up in the evidence:

| scarce resource | who pays for it | what it looks like |
|---|---|---|
| **locked capital** (patience) | holders who will not wait for a queue, a lock or a conversion | queue bids, discounted locks, trust conversions |
| **venue-specific capital** | leveraged longs on a venue where arbitrage capital is segmented | funding at the formula's interest rate on Hyperliquid |
| **tail tolerance** | traders paying for leverage | perp-venue liquidity vaults ("the house") |
| **attention and eligibility** | protocols renting deposits with incentive budgets | rotating through rewarded markets |
| **access** | anyone without the account or the paperwork | KYC'd redemptions, broker stock legs, Coinbase for LBTC |

The rent map (`rent_map/findings.md`) sizes the pools:

- **Total:** about $12.7B a year paid by non-price-motivated agents, $2.2B of it above a fair rate.
- **Accessible to patient capital:** a plausible $2.8–17.5M, 3–16× today's book.
- **The largest above-fair pool is Hyperliquid funding ($850M).** On 71.6% of open-interest-weighted hours HL funding
  sits exactly at the formula's interest rate (10.95% a year). It is a venue parameter, not a market price.

## What the nine studies found

| resource | study | verdict | $ a year at size |
|---|---|---|---|
| locked capital | **queue book, one pool** (stETH, weETH, rsETH, LBTC) | **go**: one $15M pool earns 86% of four separate books on 45% of the capital; $20M beats them | **$409,889 at $15M** (t 9.31) |
| locked capital | **kHYPE queue bid** (HyperEVM) | **go**, lumpy: every one of 13,426 queue confirmations paid exactly | **$140,043 at $10M** |
| locked capital | CoW resting orders in the April 2026 stETH episode | **implementation verified**: 91 orders resting ≥ 1h filled 6,023 ETH at a median 31bp below NAV | — |
| locked capital | Solana, BNB, Monad, Sonic, AVAX staking tokens | no-go or watch: withdrawal fees cap the discount; flow is thin | — |
| locked capital | veAERO lock + short perp | standby: +11.3% only on the best venue's (Hyperliquid's) funding; the 2026-10-22 merger ends the system | ~$2M |
| locked capital | OTC trusts, digital-asset treasury companies | standby / no-go: the GBTC regime ended with the 2025 listing standards; treasury discounts do not converge | ~$0.55M |
| venue capital | **HYPE carry with kHYPE as the spot leg** | **upgrade**: +4.48% over SSR (+1.21pp over spot HYPE) | **$224,000 at $5M** |
| venue capital | gold perps against PAXG/XAUT | no-go, two watch lines: funding is a real premium, but the cost of carry eats it and depth caps it | ≤ $62k |
| tail tolerance | **GMX GM SOL-USDC, hedged** | **go**, small: fees + traders' losses | **$103,000 at $2M** |
| tail tolerance | **JLP, hedged** | **go**, gated by a live forward test of the hedge | **$248,000 at $10M** |
| tail tolerance | HLP, gUSDC, Lighter LLP, GM ETH | no-go: HLP's market making nets zero; its income is crash liquidations | — |
| attention | incentive-adjusted dollar yields | no-go: displayed yields above ~5pp over SSR are credit risk once share prices are checked | +1% watch |
| skill | Hyperliquid vault managers | no-go: track records do not persist; the average vault loses | — |

**If every proposal is approved** (simulated on a copy of the book, on its own rule of go and a current quote):

- The book goes from $1,022,032 a year, its value with last session's pending writes, to **$1,467,586**. It is $613,442
  today, before any pending write.
- The queue rows need **$15M instead of $33M**.

## Five things this session learned that generalise

1. **Diversify queue capital by underlying, not by issuer.**
   - Dislocations of tokens on the same underlying coincide: weETH and stETH correlate 0.70 in the capital they lock.
   - Different underlyings do not: LBTC −0.06 against the ETH tokens, kHYPE −0.03.
   - One pool of capital therefore earns nearly the sum of the separate books.
   - Unescrowed signed limit orders make this literal: one balance backs every bid, and a fill the balance cannot cover
     simply fails. They were seen filling at their limits in the April 2026 stETH episode.
   - Every new queue (HYPE, AVAX, BTC staking tokens) is worth more as a diversifier than its stand-alone dollars
     suggest.
2. **Displayed yield is not realised yield.**
   - DefiLlama's displayed dollar yields rotate to +15% a year over the savings rate out of sample. Where a share price
     can check them, nothing above ~5pp over SSR survives: the vault write-downs never appear in the yield series.
   - Same law as the Pendle dollar PTs: a rate far above the benchmark is a price for default.
   - Every yield must be checked against the share price before it is believed.
3. **The biggest persistent rents are formula parameters, collected with same-venue collateral.**
   - The funding formulas' interest leg is where the money is: Hyperliquid's HYPE and BTC/ETH, VELO on Binance at
     exactly the interest rate on 90% of settlements, AERO on Hyperliquid.
   - It stays uncollected because arbitrage capital must sit on two venues. It becomes collectable whenever a venue
     accepts the spot (or its staking token) as margin.
   - **Watch the collateral lists**: HYPE, BTC, and potentially XAUT0/PAXG, UBTC, kHYPE on Hyperliquid. Each addition
     is a new carry.
4. **Being the house pays only where fees dominate and flow is captive.**
   - GM SOL-USDC and JLP earn their fee share.
   - HLP's market-making children net about $0 over its life; its income is crash liquidations, which a new depositor
     buys at fixed-dollar dilution.
   - Traders beat the vault on GM ETH-USDC and on Gains in September 2026.
5. **Published edges decay, and the decay is measurable.**
   - The attentive voter's premium on Aerodrome was +15–21pp before March 2025 and is now ≈ 0 unless voting in the
     final hour.
   - Governance and fundamentals signals died in 2024.
   - The GBTC-style trust discount did not recur after the generic listing standards.
   - What remains is where the payer's motive is structural (impatience, leverage access), not where the information is
     public.

Two method changes came out of the work:

- **An in-sample floor in go rules.** `backtest.choose_then_test` now reports `in_sample_positive`. The vault-skill study
  showed a least-bad loser can "pass" out of sample.
- **The share-price audit**, for any yield claim (`incentive_yields`).

## What to do next, ranked

1. **Run the one-pool queue book live, small.**
   - ETH-only first: one WETH balance, resting CoW orders below NAV for stETH, weETH and rsETH, re-signed daily.
   - Add a cbBTC sub-pool for LBTC and a HyperEVM sub-pool for kHYPE.
   - This is the session's largest and best-evidenced result, and it needs no new research.
2. **Forward-test JLP with the venue's net-delta hedge**, 60 days, before any capital (the row's first kill gate).
3. **A collateral-list watcher.** A daily check of Hyperliquid's (and Binance portfolio margin's) accepted collateral and
   haircuts. Each new asset is a potential same-venue carry at the formula rate.
4. **Joint simulation of the five-asset queue book** with kHYPE's environment exported, plus sAVAX at swap level.
5. **Forward ledgers** for the watch items that need time, not more history: pooled money-market incentives, xyz:GOLD /
   HL PAXG carry, HL vault size-follow, sAERO after the merger, EMPD/BNC events.
6. **Install the launchd jobs.** The forward tests (unlocks, Boros, these) only advance while a session is open.

The book changes (eight proposals, two corrections) wait for the user's approval. The commands are in the ROADMAP's
session entry.
