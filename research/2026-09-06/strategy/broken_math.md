# Pools with broken math: a hunt, and why it comes up almost empty

Claude, 2026-09-06. "Find pools with broken math, explain what is broken." I checked three concrete signatures of broken pool math across the pools active in this session, on a mainnet fork at block 25,918,509. The honest headline: **exploitable broken math does not persist at size.** The moment a pool's accounting is inconsistent, searchers drain it to dust and liquidity migrates, so the signatures survive only in abandoned pools worth cents. The scanner is `scripts/pool_math_scan.py`; the raw run is `broken_math_scan.txt`.

## What "broken math" means

A pool has broken math when the value you can take out differs from the value the pool *thinks* it holds. That is different from mispricing you trade against (an AMM with no oracle is not "broken", it is just arbitraged). Broken math is an internal inconsistency: a cached number that disagrees with reality, a rounding step that rounds the wrong way, an invariant that does not hold. Three signatures capture almost all of it:

1. **Rate-cache staleness.** A rate-scaled pool prices a rate-bearing token by a *cached* exchange rate; if the live rate has moved past the cache, the pool misprices the token.
2. **Reserve/balance drift.** A pool that caches reserves (Uniswap v2 style) holding a rebasing or fee-on-transfer token: `balanceOf(pool)` drifts from the cached reserve, and the excess is skimmable.
3. **Round-trip leak.** A correct AMM always returns strictly less than the input on A→B→A (it charges a fee). A pool that returns more has a rounding or invariant bug.

## The lead that did not pan out (a correction)

The bot that cycles ~$3.5B of flash liquidity for ~$970 a run (`0xfccc10ad…`) routes a repeated-swap ladder through one specific pool, `0x69d460e0…` — the classic look of a rounding exploit. It is not. The pool is a **Balancer v1 weighted pool**: DAI, USDC, WETH and REQ (Request Token), only **100 BPT** outstanding, ~$3k of total liquidity, 0.15% swap fee, weights 20/18.5/15.4/46.2%. I tested it directly (`BalV1Leak.t.sol`, on the fork):

| test | result | reading |
|---|---|---|
| join 50 DAI → BPT → exit → DAI | net **−0.115 DAI** | loses the fee on the swapped portion — correct |
| swap DAI→REQ→DAI | net **−0.058 DAI** | loses ~2×0.15% fee — correct |
| geometric swap ladder (the bot's shape) | net **0** | no compounding leak |
| swap 1 wei DAI | reverts `ERR_DIV_ZERO` | a robustness quirk, not a profit |

The pool's math is sound; a $3k pool could not source $970 a run anyway. The bot's profit is **not in this pool and not in ETH** — a `prestateTracer` diff of its transaction shows the bot's ETH essentially unchanged, the builder `0xdadb0d80…` paid +0.0027 ETH, and the ~$970 arriving in tokens from the broader Aave/Maker/Spark bundle, not from a pool bug. Assuming "weird-looking pool" meant "broken pool" was wrong, and testing it was the point.

## The three scans, and what they found

**1. Rate-cache staleness — 0 of 36 active Balancer v2 pools.** For each rate-scaled pool I compared the pool's cached token rate to the live rate provider's `getRate()`. No gap above 0.1 bp. The class is small by construction anyway: an LST yields ~4%/year, so over even a one-day cache the rate drifts at most ~1 bp, and the pool refreshes the cache on the next swap. Worth catching only if a provider is misconfigured with a long duration or jumps; none here.

**2. Reserve/balance drift — the signature is present, but only in dust.** Uniswap-v2 and Sushi pairs holding rebasing tokens do carry skimmable excess, exactly as the math predicts (the reserve is cached, `balanceOf` grows with the rebase, `skim()` pays the difference to the caller):

| venue | pair | reserve | actual balance | skimmable |
|---|---|---|---|---|
| Sushi | stETH/WETH | 0.008196 stETH | 0.008198 stETH | 0.000002 stETH (~$0.005) |
| UniV2 | aEthWETH/WETH | 0.000131 | 0.000131 | ~0 |
| UniV2 | stETH/USDT | 0.001084 | 0.001084 | ~0 |

The signature is real — these pools *are* mathematically "broken" in the skim sense — but every one is an abandoned pair holding a few dollars. The reason is instructive: the entire ecosystem moved rebasing exposure into **wrapped, non-rebasing tokens (wstETH)** precisely so that AMM pools never carry this drift. The live wstETH liquidity ($billions) cannot be skimmed because wstETH does not rebase.

**3. Round-trip leak — 0 of 71 active Curve pools.** For each 2-coin Curve pool I computed `get_dy(0,1,x)` then `get_dy(1,0,·)` and checked whether the round trip returned more than it took. None did; every pool returns less, i.e. charges its fee correctly. No rounding or invariant leak in the active set.

## Why the hunt comes up empty (the actual insight)

Broken math is **self-limiting**, in a way price mispricing is not:

- A price gap is replenished by order flow, so it recurs and there is always something to arb. A math bug is a *fixed pot* — the inconsistent value sitting in the pool. The first searcher to find it drains the pot to the point where the residual is below gas, and it stays drained.
- Liquidity then migrates away from the broken construction. Rebasing tokens became wrapped tokens; unaudited pool types lose TVL; the vulnerable Curve Vyper versions from 2023 were drained and deprecated. The market removes broken math from where the money is.

So what a scan actually finds is three things, none of them a paycheck: **fossils** (dust skim pools), **pools that look broken but are correct** (the bot's v1 pool), and **sub-basis-point staleness** not worth the gas. A genuinely broken pool holding real liquidity is a live security vulnerability, not a standing yield — if you find one, the responsible and also the only durable move is disclosure, because the alternative is a race that ends the instant anyone else notices.

## How to catch the real thing when it appears

Broken math is an *event*, not a *state* — it shows up when something new or something changed. The scanner (`pool_math_scan.py`) runs the three signatures above continuously; the events that actually produce a live instance are:

- **A new or freshly migrated pool** before searchers have swept it (minutes-to-hours window).
- **A rate provider or oracle that jumps or is manipulable** — a rate-scaled pool whose provider reads a spot AMM price is the modern version of the classic oracle bug; watch for `getRate()` sources that are themselves manipulable.
- **A rebasing/fee-on-transfer token added to a v2/v3 pool** that does not wrap it — drift accrues every rebase; the scanner's skim check catches it while it is still funded.
- **Read-only reentrancy** in older Curve/pool code where `get_virtual_price` or a balance read can be entered mid-transaction — a different tool (a reentrancy harness), not a static scan.
- **A low-decimal or extreme-imbalance pool** where integer rounding becomes a meaningful fraction — the 1-wei `ERR_DIV_ZERO` on the v1 pool is the benign end of this; the malign end is a pool where `calcOutGivenIn` rounds up.

Run the scanner against the mempool-fresh set (new factory deploys, newly funded pairs) rather than the mature set, and pair it with a fast, revert-safe executor. That is an MEV pipeline, with the same conclusion as the flash-loan note: a single-transaction extraction of broken math is an MEV race, and the edge lives in seeing the freshly-broken pool before anyone else.

## Artifacts

- `scripts/pool_math_scan.py` — the three-signature scanner (rate caches, v2 skim, Curve round-trip); `broken_math_scan.txt` — the 2026-09-06 run.
- `BalV1Leak.t.sol` — the direct test proving the bot's Balancer v1 pool is not broken.

Reproduce: `anvil --fork-url https://ethereum-rpc.publicnode.com --silent &` then `uv run --with pycryptodome python scripts/pool_math_scan.py --rpc http://127.0.0.1:8545 --balancer-pools <pools> --curve-pools research/2026-09-06/live/pools.json`.
