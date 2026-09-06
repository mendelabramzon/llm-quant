# Redemption-liquidity: the non-MEV edge, with a custom contract and a fork proof

Claude, 2026-09-06. This follows the live-scan request ("find non-trivial ways to extract value, do not compete with MEV bots") and the steer to *check smart contracts and vaults and propose something interesting, with a custom contract that composes a profitable transaction*. Everything below was read from Ethereum mainnet at block 25,918,242 through a public RPC, and the strategy contract was proven on a mainnet fork at that block with Foundry. All work is read-only. No transaction was broadcast; the composed transactions and the one missing input (a funded key) are in section 6.

## 1. The answer in one paragraph

On mainnet, **price space is efficient and time space is not.** Every atomic price arbitrage I measured is already competed down to the swap fee: stETH is 2 bps under ETH, sUSDe's secondary is 8 bps under NAV on the bid but at par on the ask, the savings vaults trade at NAV, GHO is 8.5 bps under peg. Chasing those means racing MEV bots, which is exactly what we don't want. The edge that MEV cannot take is **redemption that clears over time**: buying a protocol's redeemable claim below the value the protocol itself pays on redemption, then realizing the convergence through the protocol's own cooldown or withdrawal queue. A latency bot cannot race a payoff that takes a day to clear. The custom contract in this directory is a standing bid for that convergence. Today the standing discount is ~0 (markets are calm), so its expected value today is ~0; it earns when a dislocation opens, and the live scanner from this session is built to detect exactly those.

## 2. Why price arbitrage is the wrong game here (measured)

| claim | measured at block 25,918,242 | atomic edge |
|---|---|---|
| stETH vs ETH (Curve) | 1 stETH → 0.99978 ETH | −2 bps (≈ fee) |
| sUSDe vs NAV | NAV 1.24677; bid −8 bps, ask ≈ +8 bps | none on the ask |
| sDAI / sUSDS / scrvUSD | trade at NAV | none |
| GHO vs peg | 0.99915 | −8.5 bps, GSM-gated |
| msETH | 0.50 ETH | broken peg, no atomic redemption |

An atomic arbitrage only exists when the *ask* is below the redemption value, and it is not. This is what an efficient market looks like, and it is why "write a contract that buys low and redeems high atomically" nets zero today. The `FlashNavArb` contract that does exactly that (flash-borrow, buy share, redeem at NAV, repay) is included and proven mechanically, but its live EV is zero until an atomic-redeem vault dislocates.

## 3. The strategy: be the redemption bid in time

The trade is structural, not a race:

1. A redeemable claim trades below the value its protocol pays on redemption. The gap opens during derisking, a large forced sale, or a peg scare, not on a single block.
2. Buy the claim below that value.
3. Enter the protocol's redemption path at full value: an Ethena **cooldown** (now **1 day**, confirmed `cooldownDuration() = 86400`), a Lido or LRT **withdrawal queue** (1 to 10 days), or an atomic ERC-4626 **redeem** where the vault allows it.
4. When it clears, you receive the full redemption value. Your profit is the discount you bought at, minus two swap legs, minus the time value of the locked capital, minus the underlying's own peg risk over the wait.

A block-building bot is structurally excluded: it optimizes a single block and cannot hold a position for a day. This is redemption market-making, and you are paid the discount for providing the liquidity that impatient sellers want and bots will not.

The flagship instance is **sUSDe** (Ethena staked USDe): $3B+ of it, a 1-day cooldown that redeems at full NAV, and deep secondary liquidity (the Curve sDAI/sUSDe pool holds ~$5.4M). `CooldownArb` implements the full lifecycle.

## 4. The proof (Foundry, mainnet fork at block 25,918,242)

`RedemptionArb.sol` + `Redemption.t.sol`, run with `forge test --fork-url <rpc> --fork-block-number 25918242 -vv`. Raw output in `fork_proof.txt`.

**Primitives (both pass):**
- An atomic ERC-4626 pays NAV: redeeming 1,000,000 sDAI returned **1,180,195.98 DAI**, exactly `previewRedeem`.
- Flash liquidity is free: a Balancer flash loan of 100,000 DAI cost **0**. (Balancer v2 holds only ~112k DAI now; Maker's `DssFlash`, Morpho and SparkLend are also zero-fee and lend at $1B+ scale, proven by the bot in the live report that cycles ~$3.5B of it thirty times an hour.)

**Cooldown lifecycle, at today's natural ask** (buy sUSDe, cool down 1 day, redeem USDe at NAV, sell USDe→USDT): spent $236,039, locked NAV of $236,079 (entry discount +1 bp, i.e. at NAV), realized **$235,975** after the day. Net **−$63.77 (−2.7 bps)** — the cost of the two Curve legs. This is the honest "no free lunch today" number.

**Cooldown lifecycle under a realistic derisk sell** (a holder dumps sUSDe into the $5.4M pool, opening a discount; the contract buys $118k below NAV, waits the day, redeems at NAV). Net of the entry discount, the thin-pool exit and gas:

| derisk sell (sUSDe) | entry discount | USDe exit slippage | net PnL on $118k | 1-day return |
|---|---|---|---|---|
| 250k (~$310k) | 6 bps | 1 bp | +$49 | 4 bps |
| 500k (~$625k) | 11 bps | 1 bp | +$114 | 9 bps |
| 750k (~$935k) | 20 bps | 1 bp | +$221 | 18 bps |
| 1.0M (~$1.25M) | 38 bps | 1 bp | +$433 | 36 bps |
| 1.5M (~$1.87M) | 265 bps | 1 bp | +$3,115 | 263 bps |

The contract captures whatever discount exists and redeems at NAV a day later. Gas is negligible: `enter` 241k, `exit` 222k, about **$0.03 each** at the current 0.05 gwei base fee. Historical sUSDe dislocations have reached 1 to 5% in genuine stress, the top of this table.

## 5. Capacity and risks (the honest limits)

- **Exit liquidity is the binding constraint.** The deepest USDe DEX pool (Curve USDe/USDT) holds only ~$0.6M, so selling redeemed USDe on-chain caps a trade at a few hundred thousand dollars before slippage bites. Larger size needs Ethena's direct 1:1 redemption, which is KYC-gated. Most USDe is staked or minted/redeemed off-DEX, which is *why* the secondary can dislocate in the first place.
- **The discount must exceed the round-trip cost.** Two Curve legs cost ~2.7 bps here; the entry and exit slippage grow with size. Below a ~3–5 bp discount the trade is flat to negative (the natural-ask row).
- **Underlying peg risk over the wait.** You lock NAV in USDe at cooldown, but you still hold USDe (not USD) for a day; if USDe itself depegs during the wait, the exit price moves. Hedge with a USDe or ETH-perp short for a clean basis capture, or sell into strength.
- **EV today is ~0.** There is no standing discount right now. This is a standing bid that earns during dislocations. Its value is the readiness: the contract and the live scanner together turn a rare, fast-opening dislocation into a capture.

## 6. The composed transactions (ready to send; broadcast intentionally not done)

`CooldownArb` (bytecode 11.5 kB) and `FlashNavArb` (16.3 kB) compile clean and pass the fork tests. To run the sUSDe trade at size `A` sDAI:

1. **Deploy** `CooldownArb(owner, 0x9D39A5DE30e57443BfF2A8307A4256c8797A3497)` (owner = your address, second arg = sUSDe).
2. `owner` approves the contract for `A` sDAI, then calls **`enter(buyPath, A, minNav)`** with `buyPath = [(0x167478921b907422F8E88B43C4Af2B8BEa278d3A, 0, 1, sDAI, sUSDe)]` and `minNav` set to your slippage floor. Encoded selector `0x20acc06b`.
3. After 1 day, `owner` calls **`exit(sellPath, minOut)`** with `sellPath = [(0x5B03CcCAb7BA3010fA5CAd23746cbf0794938e96, 1, 0, USDe, USDT)]`. Encoded selector `0xcaa134b7`.

The full ABI-encoded calldata for a $118k example is in `fork_proof.txt`'s companion notes; regenerate for any size with `cast calldata`. **What is deliberately missing to actually broadcast: a funded signing key and a real `minNav`/`minOut` set to your risk tolerance.** I have no wallet configured and sending real value on mainnet is the operator's decision, so the pipeline stops at a proven, ready-to-sign transaction. Before sending real funds this contract should get an independent audit; it is research code.

## 7. The other verified non-MEV edges (a menu, with live numbers)

Ranked by how much they pay for how little contention. All read at block 25,918,242.

1. **Cross-venue rate dispersion (a business, not a trade).** Compound v3 USDC supplies **4.79%** vs Aave USDC **3.60%**; the cheapest dollar borrow is Compound USDT at **3.81%** vs SparkLend USDT **4.80%**. A ~1-point spread persists because moving supply costs attention, not gas. Event-driven on `ReserveDataUpdated`.
2. **Thin-reserve rate spikes.** Aave's **PYUSD** reserve pays **3.72%** supply / **4.82%** borrow on only $7.8M, with a convex curve (base 1%, slope1 4% to the 90% kink, slope2 **50%** to 100%). It sits at 85.9% utilization; ~$450k of new borrowing tips it past the kink and the rate rockets. A monitor that lists reserves near their kink, with the capacity left before it, catches these daily.
3. **The midnight routine (a calendar edge).** Confirmed daily in this session: at 23:34 UTC an entity withdraws ~$150M USDC from Aave, spiking the USDC borrow rate from 4.27% to **14.29%** for ~34 minutes, then re-supplies. Anything that schedules Aave USDC borrowing around 23:30–00:10 UTC avoids the spike; any rate read in that window is an artifact to fade.
4. **LRT withdrawal-queue discounts.** rsETH trades **−37 bps** to its Kelp redemption value with a 7–10 day queue; the same `CooldownArb`-style contract (swapped for the Kelp withdrawal path) captures it. Thin now, widens to 1–3% in LRT stress.
5. **Free flash liquidity at $3B** (Balancer/Maker/Morpho/Spark, zero fee) makes every atomic strategy capital-free; the binding constraint is the opportunity, never the capital.

Not worth it: Convex `earmarkRewards` keeper bounties pay ~0.005–0.01 CRV (pennies) on quiet pools and are contested; atomic price arbitrage is MEV.

## 8. How to reproduce

```sh
# read the live state (public RPC, no key)
uv run --with pycryptodome python scripts/drpc.py <txhash>          # tracing helper
# prove the contract on a mainnet fork
cd <foundry project with research/2026-09-06/strategy/RedemptionArb.sol as src, Redemption.t.sol as test>
anvil --fork-url https://ethereum-rpc.publicnode.com --silent &
forge test --fork-url http://127.0.0.1:8545 --fork-block-number 25918242 -vv
```

Artifacts here: `RedemptionArb.sol` (the contracts), `Redemption.t.sol` (the fork proof), `fork_proof.txt` (the run output at block 25,918,242).
