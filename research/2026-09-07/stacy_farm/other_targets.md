# Other targets like Stacy: a cross-chain scan of the CORE / cVault reward-timing family

Question: are there other live vaults exploitable the way StacyVault is, "probably on other chains"? This scans the
CORE / cVault.finance MasterChef family for the same bug and, critically, for the two conditions that make it *worth*
running — a flash-mintable blue-chip pool (cheap to dominate) and a reward token with real value and live fee flow.

Tool: `scripts/corevault_scan.py` browses a chain's Blockscout by contract name, fingerprints each candidate's verified
source, and reads pools and reward-token prices on-chain. Fingerprint = `depositFor` + lump rewards
(`addPendingRewards`/`updateAndPayOutPending`) + `accXPerShare`; it also reports whether the same-block guard is
bypassable and classifies each pool's LP as flash-mintable-blue-chip or native.

```sh
uv run --with pycryptodome python scripts/corevault_scan.py --chain ethereum
uv run --with pycryptodome python scripts/corevault_scan.py --chain arbitrum
```

## The bug is universal in the family; the constraint is pool composition + token value

The original CORE `CoreVault` (`0x7ca9…f0D3` behind `0xC5cacb…d8c9`) already pays rewards by *instantaneous* stake from
pushed lumps and has a `depositFor` that never guards the deposit block — it has **no same-block guard at all**. Every
fork inherits this. So the mechanism is not the filter; the filter is:

1. a pool whose LP you can flash-mint for free (both sides blue-chip: WETH/USDC/USDT/WBTC/DAI), and
2. that pool has little staked (cheap to dominate), and
3. a reward token that is actually worth something with live fee flow.

## Ethereum: 22 CoreVault-family vaults, all bypassable, none that clears the bar

| vault | reward token | reward price | pools | verdict |
|---|---|---|---|---|
| `0x223Bc7…8DF8` StacyVault | STACY | ~$0.000017 | WETH/STACY, CHADS/WETH, eMTRG/WETH, **USDC/WETH, WBTC/WETH** | blue-chip pools ✓ but token is dust → gas-break-even |
| `0xC5cacb…d8c9` CORE | CORE | **$5,824** | CORE/ETH native LP only | valuable token, but no flash-mintable pool |
| `0x37cc0b…912f` | STCP | $1.89 | WETH/STCP native | valuable-ish token, native pool only |
| `0x422d9d…9d55` | VCORE | n/a | **$AAPL/VCORE** | 2026 tokenized-stock fork (like Stacy), not blue-chip |
| `0xFF5439…c81e` + others | HDCORE/miniCORE/microCORE/TCORE/DFCORE/FCORE/FANC | dust/unknown | X/WETH native | dead relics |

All 22 carry the bypassable `depositFor`. **None combines a flash-mintable blue-chip pool with a valuable reward token.**
Stacy is the only one with blue-chip pools, and its token is dust; the valuable tokens (CORE $5,824, STCP $1.89) only
have native-token LP, which you cannot flash-mint without first buying the token — defeating the no-capital advantage.
`$AAPL/VCORE` confirms the family is being freshly redeployed in the 2026 tokenized-stock meme wave (the same wave that
produced Stacy/Stockereum), so a future fork *could* add a blue-chip pool with a live token — which is exactly what this
scanner is for.

## Cross-chain

An Etherscan V2 key (`etherscan_key.txt`, via `scripts/etherscan.py`) is now integrated. Its free tier serves verified
`getsourcecode` on Ethereum, BSC, Base, Polygon and Arbitrum (the `account`/`proxy`/`logs` modules are gated to a few
chains, so on-chain reads go through free public RPCs instead). So `corevault_scan --chain bsc|base|polygon` can
fingerprint any given address; the cross-chain pipeline is proven end-to-end (Stacy re-flags through the Etherscan
source backend; Pancake's MasterChef correctly does not match — it is time-weighted, not a CORE lump vault).

- **Arbitrum**: 40 contracts named CoreVault/cVault, **0 match the fingerprint** — unrelated yield vaults (`depositFor`
  present but no `accXPerShare` lump-reward design).
- **BSC / Base / Polygon**: source is now reachable, but **there is no name-search API on the free tier and no working
  Blockscout for these chains, so candidate discovery is the blocker** — the scanner needs seed addresses. Note also
  that BSC's "deflationary" scene was reflection-based (Safemoon-style), a different mechanism from the CORE MasterChef
  lump vault, so true CORE forks there are likely rare. The known ETH vaults (CORE, StacyVault) are **not** redeployed
  at the same addresses on BSC.
- **To actually sweep BSC** without a name index: use the bytecode method in
  [fingerprint_method.md](fingerprint_method.md) — collect a window of BSC logs with `live_collect`, run
  `bytecode_fingerprint.py enum-offline` to surface every active CoreVault fork by its `Deposit`-topic emissions +
  selector-cluster signature (no source or name needed), then `corevault_scan --chain bsc --addresses <them>` to score
  them. This closes the discovery gap on any chain with a public RPC.

## Cross-chain hunt results (2026-09-07, `scripts/corevault_hunt.py`)

The local Infura keys are enabled for every major chain, so the hunt enumerated *active* reward vaults (recent
`Deposit`-topic emitters), bytecode-confirmed the CoreVault forks, and scored them. "Suitable" now requires a
flash-mintable blue-chip pool **and** a reward token with ≥ $25k of pool depth (so dust like STACY is a fork but not
suitable).

| chain | window | active vaults scanned | CoreVault forks | suitable |
|---|---|---|---|---|
| Ethereum | last 100k blocks (~2 wk) | 136 | 1 (StacyVault) | 0 |
| BSC | last 80k blocks (~2.8 d) | 117 | 0 | 0 |
| Base | last 80k blocks (~1.9 d) | 462 | 0 | 0 |
| Polygon | last 80k blocks (~1.9 d) | 12 | 0 | 0 |
| Arbitrum | name search | 40 named | 0 | 0 |

**No suitable target exists right now on any chain scanned.** The only active CoreVault fork anywhere is StacyVault, and
its reward token has $8,634 of depth — gas-break-even, not suitable. The 21 other Ethereum forks (CORE, Hardcore, …) are
dormant (no recent deposits, so no reward flow). BSC/Base/Polygon have busy MasterChef ecosystems but none is a CoreVault
fork — confirming the family is Ethereum-native and the BSC "deflationary" scene was reflection-based, a different design.
Caveat: the non-Ethereum windows are short (2 days), so a fork that exists but was idle would be missed; extend `--blocks`
or add chains to widen the net.

## Verdict

No current target beats Stacy, and Stacy itself is gas-break-even. The durable output is the scanner as a **standing
detector**: re-run it per chain, and the moment a fresh CORE fork (the tokenized-stock wave is minting them) pairs a
valuable token with a blue-chip pool, it flags. Route any hit through the planned economics harness (see `ROADMAP.md`)
before deploying `StacyFarmer` against it.
