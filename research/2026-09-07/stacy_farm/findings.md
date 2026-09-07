# Replicating the StacyVault flash-farm

The bot `0x23fdc534…` (through helper `0x0fd368ed…`) that ran eight times in the five-hour window flash-borrows
from Morpho, momentarily dominates two StacyVault staking pools, triggers a reward lump, and harvests it, all in
one transaction with no committed capital. This reproduces it, proves it on a mainnet fork, and states the real
economics, which are small.

Contracts (verified source saved in `sources/`):

- StacyVault (MasterChef, a CORE/cVault fork): [0x223Bc7…8DF8](https://etherscan.io/address/0x223Bc79156CBb0a6D175Ea6130Cb382D01868DF8)
- Stacy token (STACY): [0xf12EC0…B327](https://etherscan.io/address/0xf12EC0D3Dab64DdEfBdC96474bDe25af3FE1B327)
- rewardsLock: [0x222207…8aE6](https://etherscan.io/address/0x222207E931D7Bf38466C395DA30E632872a98aE6)

## Why it works (two flaws, both in the verified source)

1. **Rewards are distributed by instantaneous stake, not by time.** `cherryPop()` on the token, and the token's
   transfer fee, push STACY into the vault in lumps and call `addPendingRewards`. On the next `massUpdatePools()`
   the whole lump is converted to `accStacyPerShare` over the current staked supply and paid pro-rata. Capital that
   is present for one transaction earns as much as capital staked for a week. So a flash-minted LP position that is
   ~100% of a pool's supply for one block captures ~100% of that pool's share of the lump.

2. **The same-block guard is on the wrong function.** `_withdraw` requires `block.number > user.lastDepositBlock`,
   but only `deposit()` sets `lastDepositBlock`. `depositFor(self, pid, amount)` never sets it, so a fresh
   depositor can deposit and withdraw in the same transaction. The bot deposits through `depositFor`.

Sequence in one transaction: flash-borrow → add on-ratio liquidity to each pool's Uniswap-v2 pair to mint a large
LP amount → `depositFor(self, pid, L)` → `cherryPop()` → `withdraw(self, pid, L)` (pays out) → burn the LP back →
repay the flash loan. Keep the STACY.

## What the fork proof shows (`fork/`, `fork_proof.txt`)

`forge test` on a latest-block mainnet fork, dominating pools 3 (USDC/WETH) and 4 (WBTC/WETH) by 1,000x their
staked supply, after warping 20 minutes so a pop has accrued:

| quantity | value |
|---|---|
| cherryPop available (20 min accrual) | ~165,000 STACY |
| STACY gained liquid by the farmer | ~4,900 STACY |
| STACY locked to the farmer (75%) | ~9,800 STACY |
| net USDC / WETH / WBTC change | −0.000001 / −4.5e-14 / −0.00000001 (dust) |
| gas | 2.04M |

The dust token change confirms the Balancer flash loan is fully repaid: **no capital is used**, only gas. Pools 3
and 4 hold almost nothing staked (the vault holds ~$44 of pool-3 LP), so a ~$20k USDC + ~9 WETH and ~2.5 WBTC + ~80
WETH flash is enough to reach 99.9% capture; the incumbent's $175M is overkill for these two pools.

## The economics are dust at today's price

STACY trades at ~6.8e-9 WETH ≈ **$0.000017** (pool 0 holds only 3.45 WETH ≈ $8,600 of liquidity). So one run at a
20-minute cadence captures pools 3+4's 8.4% of the pop:

- liquid ≈ 4,900 STACY ≈ **$0.083**
- locked ≈ 9,800 STACY ≈ **$0.166** (claimable later per the rewardsLock terms, not modelled here)
- gas ≈ 2.04M × 0.05 gwei ≈ 0.0001 ETH ≈ **$0.25**

At current price and cadence the liquid take is roughly gas-break-even. It scales linearly with time since the last
pop, but so does waiting. **This is a mechanism demonstration, not a live edge**, unless STACY appreciates.

Where the real yield is: pool 0 (STACY/WETH) carries 750/950 = **79% of emissions**, and the vault already holds
89.7% of pool-0 LP (held by the deployer). Capturing that requires being a real STACY/WETH LP, i.e. holding STACY,
i.e. exposure to a token whose own `cherryPop` drains 1%/day of its already-thin liquidity. The flash bot skips
pool 0 for exactly this reason and skims the 8.4% in pools 3+4.

## Prerequisites and risks before mainnet

- **cherryPop gate.** The caller must hold ≥10,000 CHADS (≈$140) or ≥1,000 eMTRG (≈$10). It is only a balance
  check, so it stays in the contract and is reusable. Fund the deployed `StacyFarmer` with one of them.
- **It is a race.** A pop is only worth taking after enough time accrues (`getCherryPopAmount ≥ 1 STACY`). The
  incumbent runs every ~30 min and pays priority fees; the loser's `cherryPop` yields little or its economics
  vanish. This becomes a standard MEV inclusion race.
- **75% is locked.** Only 25% of the vault payout is liquid immediately; confirm the rewardsLock release schedule
  before valuing the rest.
- **Adversarial.** This captures reward flow that would otherwise accrue to time-committed stakers of pools 3/4.
  It uses only public functions and touches no one's deposits, but it is not a neutral trade. Your call.
- **Fork ≠ mainnet.** The proof forks the latest block and warps time. On mainnet you also need the gate token
  funded, gas, and to win block inclusion against the incumbent.

## Run it

```sh
cd research/2026-09-07/stacy_farm/fork
forge test --match-test test_farm_pools_3_and_4 --fork-url https://eth.drpc.org -vv
```

`src/StacyFarmer.sol` is the strategy (owner-only): deploy with `(vault, balancerVault)`, send it CHADS or eMTRG,
then call `farm([3,4], 1000, 1e12)`. `sweep(token, to)` recovers STACY and any dust. The flash provider is
Balancer V2 (fee-free); the incumbent uses Morpho, which is equivalent.
