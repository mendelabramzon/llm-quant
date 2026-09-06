# One transaction, a flash loan, no capital: what that actually is, and the engine to do it

Claude, 2026-09-06, answering "I don't want to use my own capital, I want something in one transaction with a flashloan." Everything below was read from Ethereum mainnet at block 25,918,423 and proven on a mainnet fork at that block with Foundry. Read-only; nothing was broadcast.

## The one thing to take away

**A single-transaction, flash-funded profit is, by definition, MEV.** A flash loan removes the capital constraint, not the need for an edge, and the only edges that resolve inside one transaction are the ones every searcher can also see and race for: arbitrage, liquidations, and bespoke exploits. So the two things asked across these messages — "don't compete with MEV bots" and "one transaction with a flashloan" — are opposite ends of the same axis. What separates them is time:

- The redemption trade from the previous note avoids the MEV race **because it takes a day** (the sUSDe cooldown). That day is exactly why a bot cannot race it, and exactly why it cannot be flash-loaned.
- An atomic flash-arb is instant **because it is a race**. It needs no capital and no overnight risk, and in return it is contested in-block by everyone.

You cannot have both. Below is the atomic engine, proven, plus the honest measurement of what it earns today.

## The engine: `WstEthFlashArb`

The one asset that is both atomically redeemable and deeply, dislocatably traded is **wstETH**: it unwraps to stETH at an exact on-chain ratio with no queue, and it trades in a multi-billion-dollar Uniswap v3 pool. Every other candidate is one or the other — atomic-redeem vaults (sDAI, sUSDS) sit at NAV because atomic redemption keeps them there, and the vaults that dislocate (sUSDe, the LRTs) have a cooldown or queue you cannot flash. That structural fact is why there is no easy atomic vault-NAV arb.

`WstEthFlashArb.sol` does the whole loop in one transaction, funded entirely by a **free Balancer flash loan** (Balancer holds ~1,135 WETH, Morpho ~11,097 WETH, both zero-fee):

```
flash WETH → buy wstETH on Uniswap v3 → unwrap wstETH to stETH → sell stETH for ETH on Curve
           → wrap ETH to WETH → repay the flash loan → keep the surplus
```

It is **risk-free by construction**: if the surplus is below `minProfit` the whole transaction reverts, so the worst case is the gas of a failed call — and through a private relay (Flashbots) a reverting bundle is simply not included, so a miss costs nothing at all. That is the right way to run it: fire it speculatively whenever a detector sees wstETH below its unwrap value by more than the round-trip cost.

Deploy is 12.5 kB; `run(flashWeth, minProfit)` is the only entry point (selector `0x7357f5d2`).

## The proof (Foundry, mainnet fork at block 25,918,423)

`WstEthFlashArb.sol` + `WstEthFlash.t.sol`, output in `flash_proof.txt`. All three tests pass.

- **Calm market, no edge.** With wstETH at its natural price the arb **reverts** and the owner's balance stays exactly 0 — zero capital in, nothing lost. (wstETH is ~0.5 bp *rich* vs its unwrap value right now; there is no standing edge.)
- **A dislocation, captured in one transaction.** After a $1.25M wstETH sell opens the pool, the owner — starting with **0 WETH** — flash-borrows 200 WETH, runs the loop, and ends with a positive WETH balance, all in one transaction. Own capital deployed: zero.
- **Sensitivity (honest about size).** Profit is bounded by how far someone else's sell dislocates the pool and by the arb size:

| wstETH sold into the pool | dislocation | profit on a 200 WETH flash |
|---|---|---|
| 300 (~$0.75M) | 0 bps | reverts (edge below cost) |
| 400 (~$1.0M) | 1 bp | reverts |
| 500 (~$1.25M) | 1 bp | +0.004 WETH (~$10) |
| 600 (~$1.5M) | 2 bps | +0.017 WETH (~$43) |
| 700 (~$1.75M) | 132 bps | +1.11 WETH (~$2,780) |

The realistic rows are the middle ones: a $1.25–1.5M sell moves this deep pool 1–2 bps and the arb nets tens of dollars. The 700-row jump is the pool's in-range liquidity breaking, which real market-makers prevent; do not read it as a forecast. **The honest conclusion: the standing atomic edge is 1–2 bps, and any real dislocation is small and contested in-block.**

## Why there is no free atomic lunch today (measured)

I checked every atomic, flash-loanable shape at this block:

| candidate | state | atomic edge |
|---|---|---|
| wstETH unwrap arb | v3 mid vs unwrap value | **−0.5 bp** (rich; no edge) |
| GHO GSM peg arb | GSM `getIsSeized() = 1`, zero liquidity | **unavailable** |
| sDAI / sUSDS / scrvUSD | trade at NAV; thin DEX pools | **none** |
| stETH / ETH | Curve | −2 bps (≈ fee) |

The efficient market has already taken them. What is left resolves to the three atomic shapes, each with its catch:

1. **Arbitrage** — the engine above. Real but 1–2 bp and won by whoever bids the highest priority fee or ships the fastest private bundle. This *is* the MEV race.
2. **Liquidations** — single-transaction, flash-funded, genuinely profitable, but they require a live underwater position (none among the accounts active this hour: lowest health factor 1.52) and are the most contested MEV of all.
3. **Bespoke protocol exploits** — I traced the bot cycling ~$3.5B of flash liquidity thirty times an hour (`0xfccc10ad…`, tx `0x22b3…329e`). Its profit is **not in ETH** (a `prestateTracer` diff shows the bot's ETH ~unchanged; it pays the builder `0xdadb0d80…` +0.0027 ETH and the EOA only gas). The ~$970 a run is in tokens extracted from one specific Balancer pool via a repeated-swap ladder — a bespoke exploit of that pool's math, not a general strategy, and not something to copy.

## Recommendation: pick your axis

- **If you want the zero-capital, single-transaction path**, you are in the MEV business. The `WstEthFlashArb` engine is ready and safe to fire speculatively (reverts on a miss). What it needs to actually earn is the other half of an MEV bot: a mempool/state watcher that detects a wstETH (or peg, or liquidation) dislocation the instant it opens, and a Flashbots bundle to win inclusion without paying on a miss. The live scanner from this session is the detector's starting point. Expect thin, contested bps, not the bot's $970 (that is a private exploit, not an arb).
- **If you want to avoid the MEV race**, take the redemption trade from the previous note: it earns the discount precisely because it holds through the cooldown, which is why no bot can take it — at the cost of a day of USDe exposure and a few hundred thousand dollars of capital.

Both engines are built and proven on a fork in this directory. The choice between them is the choice between contention and time.

## Artifacts

- `WstEthFlashArb.sol` — the atomic flash-arb engine; `WstEthFlash.t.sol` — its fork proof; `flash_proof.txt` — the run at block 25,918,423.
- `RedemptionArb.sol` / `Redemption.t.sol` / `fork_proof.txt` — the non-MEV cooldown engine (previous note, `redemption_liquidity.md`).

To reproduce: `anvil --fork-url https://ethereum-rpc.publicnode.com --silent &` then `forge test --fork-block-number 25918423 -vv`. Both contracts are research code and need an independent audit before real funds.
