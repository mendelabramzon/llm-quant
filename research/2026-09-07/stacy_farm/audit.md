# StacyVault (and the CORE-fork lineage): what else is wrong with it

Beyond the reward-timing skim (`findings.md`), does the found vault have other bugs — math errors, drains? I read the
verified source and checked the live state of StacyVault (`0x223Bc79…8DF8`); its CORE-family siblings share this code.

**Bottom line: yes, but the consequential ones are admin backdoors that let the deployer/owner take all deposits, not
a new public exploit an outsider can profit from. The "math errors" are real but benign.**

## Live admin fund-drain backdoors (HIGH — reasons never to deposit)

On-chain now: `owner = 0xcf01e78e…`, `superAdmin = 0x8aef57fe…` (the deployer, also `devaddr`), `migrator = 0x0`,
`contractStartBlock = 11,165,162` (a 2020 block — this is an old CORE-era contract revived in 2026).

- **superAdmin arbitrary-allowance drain — LIVE.** `setStrategyContractOrDistributionContractAllowance(token, amount,
  contract)` is `onlySuperAdmin` and gated only by `block.number > contractStartBlock + 95_000`. With a 2020 start that
  grace is long over, and `superAdmin` is the deployer, **not burned**. So the deployer can, right now, approve every
  pool's LP token and all STACY to a contract they control and take everything staked. Every depositor is fully exposed
  to the deployer.
- **Migrator backdoor — armable.** `setMigrator` (onlyOwner) sets any migrator; `migrate(pid)` is public and approves a
  pool's entire LP balance to it. `migrator` is currently `0x0`, so `migrate` reverts today, but the owner can arm it at
  any time and then anyone (or the owner) moves all LP out. This is the classic SushiSwap MasterChef migrator rug.

These are the standard CORE/MasterChef centralization backdoors. They confirm the strategy conclusion from the other
direction: **never stake real capital in this vault.** They are the deployer's tools, not an edge an outsider can use.

## Math and accounting errors (real, but not profitable)

- **Precision loss in `updatePool` (MEDIUM-as-a-bug, benign economically).** `accStacyPerShare += stacyRewardToDistribute
  * 1e12 / tokenSupply`. When the LP `tokenSupply` (18-decimal LP, often 1e15–1e17) exceeds `reward * 1e12`, the
  increment rounds to zero, yet `pendingRewards` was already decremented in `massUpdatePools`. So small reward lumps over
  a large pool are silently burned. It loses honest stakers a little; it does not create stealable value. (It slightly
  favours the flash-timing attacker, who dilutes honest stakers further.)
- **Deposit over-crediting with fee-on-transfer pool tokens (LOW, latent).** `deposit`/`depositFor` credit
  `user.amount += _amount` (the requested amount) while transferring via `safeTransferFrom`. If a pool token ever took a
  transfer fee, the vault would receive less than credited and the last withdrawer would be bricked. Not live — the pools
  are Uniswap-v2 LP tokens with no transfer fee — but it breaks if such a token is ever added as a pool.
- **`tokenSupply = pool.token.balanceOf(this)` not a tracked total (design flaw).** Rewards-per-share is computed over the
  vault's *current* LP balance, which is exactly what the flash-deposit exploit abuses; it also means anyone can donate
  LP directly to dilute honest stakers. This is the root of the reward-timing skim, restated.
- **`safeStacyTransfer` is dead code**, and `addPendingRewards` is permissionless and balance-delta based (anyone can
  donate STACY and count it as rewards — a gift, not an exploit). Both signal unaudited, copy-pasted 2020 code.

## What is NOT exploitable by an outsider

- No public theft of others' stake: `withdraw`/`withdrawFrom`/`emergencyWithdraw` are correctly access-controlled;
  `withdrawFrom` needs an allowance; STACY payout is capped at `min(pending, vault STACY balance)`.
- No reentrancy drain: STACY transfers from the vault are fee-exempt in the FeeApprover (they must be — otherwise the
  reentrant `addPendingRewards` during a payout would underflow `balanceOf − stacyBalance` and revert every claim, which
  it does not; the fork farm claims successfully). The LP token has no transfer hook.

## Verdict

The only outsider edge remains the dust reward-timing skim. The vault's other flaws are (a) live admin backdoors that
make it un-stakeable and (b) benign rounding. There is no additional profitable exploit here. The same audit applies to
the CORE-family siblings, which share this contract; each should be checked for its own `superAdmin`/`owner`/`migrator`
liveness before any interaction.
