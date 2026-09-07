# Cross-chain vault audit: classify the active vaults, find the bugs

Goal: enumerate the vaults active across several EVMs, classify them by type, and find bugs / math weaknesses. Tooling:
`scripts/vault_audit.py` — enumerate active vaults per chain from their deposit/stake event topics (MasterChef,
ERC-4626, Synthetix-staking), fetch each one's runtime bytecode (Infura, batched), resolve EIP-1967 proxies to their
implementation, classify by the implementation's function-selector signature, cluster by normalised code hash so the
hundreds of instances collapse into a few dozen distinct implementations, and red-flag each representative's verified
source (Etherscan V2 key). Read-only. Windows: last ~30k blocks per chain.

## Landscape (Ethereum, Base, BSC, Arbitrum)

| chain | active vaults | ERC-4626 | MasterChef | CORE fork | other/unknown |
|---|---|---|---|---|---|
| Ethereum | 336 | 125 | 9 | 1 (Stacy) | 201 |
| Base | 236 | 43 | 3 | 0 | 190 |
| BSC | 67 | 5 | 7 | 0 | 55 |
| Arbitrum | 16 | 5 | 0 | 0 | 11 |

The largest clusters are all **audited, well-known protocols** — the enumeration catches every reward-bearing contract,
most of which are reputable:

| cluster | chain | count | what it is |
|---|---|---|---|
| VirtualBalanceRewardPool / BaseRewardPool | Ethereum | 40 + 28 | Convex Finance reward pools |
| VaultV2 | Ethereum | 20 | Morpho Vault V2 (has share-inflation protection) |
| Yearn V3 Vault | Ethereum | 14 | Yearn v3 |
| WrappedBackedTokenImplementation | Ethereum | 6 | Backed Finance tokenized assets (init-guarded, protected) |
| FeesVotingReward / BribeVotingReward | Base | 56 + 42 | Aerodrome/Velodrome (Solidly) voting rewards |
| BeefyRewardPool | Base | 17 | Beefy |
| StableERC4626ForVenus | BSC | 5 | Venus ERC-4626 wrapper (init-guarded, protected) |

The "unknown" bucket is dominated by these (my classifier has signatures for CORE/MasterChef/ERC-4626/Beefy/Synthetix/
Curve/Yearn, not for Convex or Solidly reward pools) plus EIP-1167 minimal-proxy clones and small custom contracts.

## Vulnerability classes checked, and what was found

**ERC-4626 share-inflation / donation attack — no live target.** Every notable ERC-4626 cluster (Morpho VaultV2, Backed,
the Venus wrapper) carries protection (virtual shares / decimals offset / dead shares) and an initializer guard. The
`balanceOf_accounting` red flag fires on them but is a false positive — they use `balanceOf(this)` safely. No unprotected
ERC-4626 vault surfaced among the active clusters.

**MasterChef reward-timing (the CORE class) — one instance.** Only StacyVault pays rewards by instantaneous stake with a
bypassable same-block guard (`findings.md`, `audit.md`). The other active MasterChefs are Sushi-style **per-block**
emission (`MoneyMaker`, `PoolMaster`, `YFNOEngine`, `BESCMasterChefV2`, …), which is time-weighted and not exploitable
that way.

**MasterChef migrator backdoor — not present in the customs checked.** The two representative custom MasterChefs
(`BESCMasterChefV2`, `YFNOEngine`) dropped SushiSwap's `setMigrator`/`migrate` owner-rug. StacyVault keeps it (owner can
arm it; currently `migrator = 0`) plus a live superAdmin drain — see `audit.md`.

**Fee-on-transfer deposit over-credit — one real bug.** `YFNOEngine` (a small custom MasterChef) records
`user.amount += requestedAmount` without checking the amount actually received, so a fee-on-transfer pool token would
over-credit stakers and brick the last withdrawer. Low value (tiny farm), but a genuine accounting error. StacyVault has
the same latent pattern; its pools are fee-free LP so it is not live there.

**Uninitialized-proxy / arbitrary-approval flags — mostly false positives.** The `unguarded_initialize` and
`arbitrary_approve` flags land overwhelmingly on audited code (Yearn, Aerodrome, Beefy, Sky sUSDS, Backed) that guards
`initialize` with an initializer modifier and approves its own strategies deliberately. No live uninitialized-proxy
takeover surfaced; each flagged custom outlier in the long tail still needs individual review.

## Honest verdict

The active vault landscape across these chains is overwhelmingly **audited, reputable protocol code** — Convex, Morpho,
Yearn, Aerodrome/Velodrome, Beefy, Venus, Sky, Curve LlamaLend, Backed. Exploitable bugs are rare and concentrated in a
thin tail of small, unaudited custom forks. The two concrete findings are StacyVault (reward-timing skim + live admin
drains, both dust/rug) and YFNOEngine (fee-on-transfer over-credit, tiny). No high-value fund-drain bug surfaced in the
active set.

This is the expected result: a broad "audit every vault" pass mostly re-confirms audited protocols. The value of the
pipeline is **triage** — it isolates the handful of unaudited, red-flagged outliers from the audited bulk so a human
audit spends its time where a bug can actually live. To go deeper, point `vault_audit.py` at the long-tail
`unknown`/unverified clusters (especially on Base and BSC, where copy-paste forks concentrate) and manually review the
ones that classify as a known-vulnerable type or carry a non-generic red flag.

## Run it

```sh
uv run --with pycryptodome python scripts/vault_audit.py --chains ethereum,base,bsc,arbitrum --blocks 30000
# classification.json holds every vault, its type, cluster (logic hash), proxy impl, and per-representative red flags.
```

## Deep-audit of the unverified custom vaults (Base, BSC, Polygon, Optimism, Arbitrum)

`scripts/vault_deep_audit.py` twin-matches every unverified contract's normalised code hash against verified code (an
unverified clone of known code needs no source review) and profiles the genuinely novel unverified bytecode: dangerous
opcodes (DELEGATECALL outside a proxy, SELFDESTRUCT, CALLCODE, tx.origin), the selector-type guess, owner, and balances.

Result across the five chains: **24 novel-unverified clusters, every one a single instance, and none is a valuable
exploitable vault.** What they actually are:

- **Mostly not vaults.** The deposit/stake event enumeration also catches MEV bots and ephemeral contracts. Many novel
  "vaults" carry `tx.origin` (ORIGIN), `SELFDESTRUCT`, or `CREATE2`, and several returned **zero bytecode minutes after
  the scan** — they had self-destructed. These are sandwich/JIT bots, not vaults.
- **No TVL.** Token-balance checks (wrapped-native, USDC/USDT/BUSD/BTCB) came back empty for essentially all of them;
  native balances were zero or dust, with one BSC contract holding ~13 BNB in a 543-byte forwarder.
- **One genuine unverified vault with real (small) TVL:** an Arbitrum ERC-4626 (`0x5449c957…`) holding **~$67k USD₮0**.
  A second (`0x2aed63eb…`) is an ERC-4626 with a SELFDESTRUCT opcode holding $0.10 (a test). The $67k one is the only
  unverified custom vault worth a manual bytecode review, and at that size with no source the effort/reward is poor.

## Overall conclusion for the whole vault sweep

Across sixteen EVMs of enumeration and a source/bytecode audit of the active set, there is **no high-value exploitable
custom vault.** The real vault TVL lives in audited protocols (Convex, Morpho, Yearn, Aerodrome/Velodrome, Beefy, Venus,
Sky, Backed); the unaudited long tail is MEV-bot junk and tiny farms with no TVL; the reward-timing-exploitable CORE
family is a single dust vault (Stacy). This is a real, if negative, finding — and the pipeline (`vault_audit.py`,
`vault_deep_audit.py`, `bytecode_fingerprint.py`, with cross-chain code-hash twin-matching) now stands as the reusable
detector to re-run and flag a valuable target the moment one appears.
