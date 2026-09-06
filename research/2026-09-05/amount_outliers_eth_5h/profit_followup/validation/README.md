Read [findings.md](findings.md) for the verdict and [episodes.md](episodes.md) for the episode table.

This directory extends the original five-hour study without changing its classifier. All network methods used are read-only. No wallet, signature, bundle submission or real transaction was used. The public RPC is `https://eth.drpc.org`; the initial Infura capability probes use the repository's existing helper and redact credentials.

Run from the repository root. Offline calculations:

```sh
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/reconcile.py
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/mechanics.py
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/audit.py
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/render.py
```

`reconcile.py` asserts native cash equals traced value transfers minus receipt gas, and validates actual-state middle replays against the complete saved traces and ordered receipt logs. `mechanics.py` decodes the saved verified Ekubo ABIs and actual fee amounts. `audit.py` compares new receipts with the original raw Infura logs, reconciles state balance deltas, verifies zero debt at boundaries and closed LP positions, checks reserve indexes and rounding, and writes the audit plus SHA-256 manifest. `render.py` writes the episode tables; run `audit.py` once more afterward to refresh the manifest if any artifact changed. Python assertions must be enabled.

Acquisition/replay commands are resumable and use saved successful responses when present:

```sh
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/collect.py
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/replay_orders.py
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/check_balances.py
uv run --with eth-abi --with pycryptodome python research/2026-09-05/amount_outliers_eth_5h/profit_followup/validation/check_positions.py
```

These scripts also require the original `eth_5h/raw/blocks` and `eth_5h/raw/logs` files, present in this workspace and ignored by git. Source/metadata discovery responses are frozen under `sources/`, `calls/`, `extra_metadata.json` and `historical_code.json.gz`; their request parameters or source URLs are saved. No missing source is silently replaced with the current repository branch.

The two replay states are `txIndex = middle index` and `txIndex = opening index`, at the same block hash. Actual-state calls reproduce all 20 complete traces exactly. `close_without_middle` is a distinct test of the original closing calldata at the pre-middle state. It does not implement a modified unwind.

`balance_calls/` holds 40 Multicall traces reading every token touched by the operator's group, including zero-net debt tokens, plus native balances and Aave account data. `balances.json` contains decoded absolute before/after balances and deltas. `position_calls/` holds 51 measurements: before, active and after for each of the 17 positions. Position slots follow the verified Ekubo source or Uniswap position layouts and are checked against the independently emitted liquidity amounts. v3 getter outputs include tokens owed.

Native payment and gas accounting is validated independently against `prestateTracer` balance differences. ERC-20 Transfer logs are reconciled with `balanceOf` state changes; scaled Aave balances are checked separately because aToken Transfer amounts and indexed balances can differ by rounding. The group contains the sender, outer contract and helper identified in the original memo. Other token/claim changes are dust and are reported, not silently discarded. ETH and WETH are combined at their protocol conversion ratio; operating expenses, failed attempts, later rebalancing transactions, rebates and unrelated controlled accounts are outside the ledger.

`audit.py` contains the explicit retrospective output-recipient mapping. Some recipients are settlement or routing contracts. Output improvements are route-execution comparisons, not cross-chain delivery confirmation, a new routing algorithm, or evidence that the counterfactual ordering could have been won in an auction. Raw transfer changes for all addresses remain in `ledger.json` and the replay traces.

This is evidence obtained from RPC providers, cross-checked against the earlier independently collected receipts/logs and exact re-execution. It is not a trustless state-root proof, a local consensus-client validation, an out-of-sample backtest or a comprehensive operator PnL. The original and public RPC request logs preserve retrieval times and capability failures. [finality.json](finality.json) records the retrieved finalized head. [sha256.json](sha256.json) inventories the saved evidence.
