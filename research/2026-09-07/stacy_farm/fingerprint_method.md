# Finding CORE-fork vaults by bytecode, not by name

The discovery bottleneck for the Stacy bug class was enumeration: verified-source name search only exists on a few
Blockscout chains, and Etherscan/BscScan have no name-search API. The fix is to stop relying on names or source at all
and fingerprint the **bytecode and event logs**, which are present for every contract on every chain, verified or not.
`scripts/bytecode_fingerprint.py` implements three signals.

## 1. Selector-cluster signature (the discriminator)

A contract's dispatcher is a run of `PUSH4 <selector> … EQ … JUMPI`. Walking the runtime bytecode while respecting PUSH
data recovers the exact set of 4-byte function selectors the contract implements — no source needed. The CoreVault
lineage carries a rare cluster that ordinary MasterChef forks (Sushi, Pancake) do not:

| selector | function |
|---|---|
| 0x4cf5fbf5 | depositFor(address,uint256,uint256) |
| 0x3a0967cd | withdrawFrom(address,uint256,uint256) |
| 0xdbe0901f | setAllowanceForPoolToken(address,uint256,uint256) |
| 0x423d6fa0 | addPendingRewards(uint256) |
| 0x3aab0a62 | startNewEpoch() |
| 0xc4014588 | setStrategyContractOrDistributionContractAllowance(address,uint256,address) |
| 0x630b5ba1 | massUpdatePools() |

Rule: match ≥ 5 of these with `depositFor` and `addPendingRewards` mandatory → it is a CoreVault fork. **Validated:**

| contract | chain | matched | verdict |
|---|---|---|---|
| StacyVault, CORE impl, HDCORE, a CORE clone, STCP | Ethereum | **7 / 7** | fork ✓ |
| PancakeSwap MasterChef | BSC | 1 / 7 (only massUpdatePools) | not a fork ✓ |
| CAKE token | BSC | 0 / 7 | not a fork ✓ |

This runs on `eth_getCode` alone, so it works on unverified and renamed contracts and on any chain with a public RPC.

## 2. Event-topic enumeration (the finder)

To find candidates with no list at all, scan `eth_getLogs` for a topic and bytecode-confirm each emitter:

- `Deposit(address,uint256,uint256)` topic `0x90890809…` — every active MasterChef-style vault emits it (high recall),
  so filter the emitters through signal 1 (high precision).
- `Approval(address,address,uint256,uint256)` topic `0xb3fd5071…` — a **non-standard 4-arg Approval** unique to the
  CoreVault `setAllowanceForPoolToken`; rare, so high precision, but low recall (allowances are seldom set).

**Validated offline** over the saved 5-hour Ethereum window (`enum-offline`): 12 unique `Deposit`-topic emitters, of which
the bytecode filter confirmed exactly one CoreVault fork — StacyVault, 7/7, 16 log hits — and rejected the other 11.
100% precision, target found.

## 3. Normalised code hash (the clusterer)

`norm_codehash` strips the Solidity metadata trailer and zeroes PUSH20 address immediates, then hashes — so forks that
differ only in hardcoded token/pair/router addresses collapse to one logic hash. The five Ethereum forks above have five
different logic hashes (different compiler versions), so they are independent deployments, not clones; the signal earns
its keep when one deployer mass-produces identical vaults across chains (the 2026 tokenized-stock wave is a candidate).

## Run it

```sh
# confirm any candidate(s) on any chain, source-free
uv run --with pycryptodome python scripts/bytecode_fingerprint.py fp --chain bsc --addresses 0x...,0x...

# enumerate from collected logs (live_collect / eth_day_collect output)
uv run --with pycryptodome python scripts/bytecode_fingerprint.py enum-offline --chain ethereum --logs research/2026-09-07/live_5h/raw/logs

# enumerate live over a block range (needs a logs endpoint that serves topic-only getLogs — Infura, not dRPC free)
uv run --with pycryptodome python scripts/bytecode_fingerprint.py enumerate --chain ethereum --from <a> --to <b> --deposit
```

`corevault_scan.py` now folds signal 1 into every result (`bytecode_matched`, `bytecode_fork`, `logic_hash`) and will
classify an **unverified** contract as a fork on bytecode alone, so a BSC/Base target with no source is still caught and
scored.

## Limitation and the standing recipe

Live enumeration needs an endpoint that serves topic-only `eth_getLogs`: dRPC's free tier refuses it, Infura (the 10 local
keys, 10k-block cap) serves it. So the durable recipe is: collect a window of logs per chain with `live_collect`, then
`enum-offline` to surface every active CoreVault fork, then `corevault_scan --addresses <them>` to score exploitability.
That closes the discovery gap on any chain with a public RPC, no name index or paid tier required.
