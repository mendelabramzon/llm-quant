# Five-hour Ethereum study: method and reproduction

The immutable interval is `[2026-09-10T05:30:48Z, 2026-09-10T10:30:48Z)`, finalized at the original request. Collected block timestamps run 05:30:59–10:30:47 UTC, blocks 25,944,911–25,946,402. A pause before continuation does not move these bounds. This is a historical pinned snapshot when read later.

The existing Infura key rotation, concurrent bounded RPC batches, raw block/log storage, token/address registries, receipt census, verification, detector registry, findings ledger and strategy book were reused. RPC calls are read-only. No trades, transactions, deployments or external messages were sent.

## Reproduction

From the repository root, with the existing RPC credentials available locally:

```sh
# Existing manifest preserves the original boundaries when resuming this directory.
uv run python scripts/live_collect.py collect --out research/2026-09-10/live_5h --hours 5 --end-tag finalized --workers 6 --max-credits 1500000
uv run python scripts/eth_day_collect.py verify --out research/2026-09-10/live_5h
uv run python scripts/live_scan.py head --out research/2026-09-10/live_5h --block 25946402
uv run python scripts/live_scan.py analyze --out research/2026-09-10/live_5h
uv run python scripts/live_scan.py enrich --out research/2026-09-10/live_5h --max-credits 60000
uv run python scripts/window_events.py --out research/2026-09-10/live_5h --bucket 15 --md
uv run python scripts/fee_census.py receipts --out research/2026-09-10/live_5h --every 4
uv run python scripts/fee_census.py analyze --out research/2026-09-10/live_5h --every 4
uv run python scripts/live_scan.py pipeline --out research/2026-09-10/live_5h
uv run python research/2026-09-10/live_5h/borrower_followup.py
uv run python research/2026-09-10/live_5h/liquidity_followup.py
uv run python scripts/strategies.py refresh --out research/2026-09-10/live_5h
uv run --with matplotlib python research/2026-09-10/live_5h/chart.py
uv run python -m unittest discover -s scripts -p 'test_*.py'
# After writing insights.md:
uv run python scripts/live_scan.py verify --out research/2026-09-10/live_5h
uv run python scripts/live_scan.py render --out research/2026-09-10/live_5h
uv run python research/2026-09-10/live_5h/validate_study.py
```

A fresh directory requires the explicit original end timestamp rather than a new trailing collection. Raw compressed files remain local and git-ignored; manifests carry their hashes. Derived JSON, scripts, notes and figures are retained for review. Early burst previews are exploratory snapshots; the final detector and `validate_study.py` reproduce the settled cohort independently of those previews. The broader in-window funding exploration in `lpt_consolidation.json` is descriptive and does not identify common ownership.

## Measurement boundaries

- All-block gas and execution burn are exact in native units. USD conversion uses endpoint feeds. ETH price movement uses swaps in the USDC/WETH v3 0.05% pool, not an external exchange composite.
- Receipt fees are a systematic 25% sample, every fourth produced block, not a random sample. Exact transaction-hash sets and block gas totals are checked. Sample totals are not full-window totals; no confidence interval or full-window tip estimate is claimed.
- Fee scenarios use observed effective fees including tips. [Ethereum fee documentation](https://ethereum.org/developers/docs/gas/) explains the base/priority split. Blob charges and direct payments to proposers/builders are separate.
- Priced swap totals count decoded legs; routed trades and recycling inflate turnover relative to independent economic demand. V4 hook accounting and unsupported/unpriced protocols limit interpretation. Settled WETH transfers corroborate the two recycling examples; net pool WETH delta is not complete trader P&L.
- Exchange flow uses at-least-$10,000 legs and the current label registry. Labels are tiered, with a wide sensitivity band. Native transfers are top-level only, with incomplete execution-status coverage. No exchange-wide net-flow census or intent classification is claimed.
- LPT fan-in requires positive non-mint/burn ERC-20 Transfer logs. The new detector has a 2,000-distinct-sender threshold and 60% token-transfer concentration threshold. `validate_study.py` checks the exact LPT logs against direct transaction calldata, including amount and sender. A common recipient is not proof of common sender ownership.
- Aggregate cash caps source liquidity for Aave/Spark/Compound rate switches. Cash is checked at the same block as rates; reserve active/paused flags and Compound withdraw pause are applied. It is not an owned position, does not resolve user collateral constraints, and does not enforce destination supply caps or future exit liquidity. Borrowing and source opportunity rates are held fixed.
- Lending summaries now sort by block and log index, preserving intra-block direction, and save every final block update at full precision. The liquidity episode detector requires that complete series; old downsampled artifacts need re-analysis. Implied historical cash remains an estimate using endpoint supply and endpoint curve, not a historical balance census.
- Three borrower inventories use aToken and variable-debt balances, reserve configuration, and protocol oracle prices at the endpoint. They reconcile to aggregate account data, establishing coverage for these accounts only. HF shock examples hold quantities, debt value and thresholds fixed; correlated collateral/debt exposures must be interpreted in relative terms.
- rETH direct redemption liquidity is a pinned `getTotalCollateral()` read. Its oracle-valued discount compares five-hour VWAP to endpoint NAV and is not an executable quote. The gate now rejects conditional/permissioned/unknown exits; other configured redemption paths retain their existing assumptions and are not newly certified by this study.
- Delegated-dust statistics count encoded calldata attempts. Settled internal legs and losses are not fully measured. Builder strings are self-reported attribution, not validator ownership. Consensus withdrawals are not evidence of selling.

## What validation means

The final pass includes raw completeness and four canonical hash rechecks, receipt reconciliation, 21 independent headline recipes, eight groups of state identities, a complete detector sweep, three borrower exposure reconciliations, direct historical PYUSD/rETH reads and a raw-log/calldata check of the LPT cohort. Unit regressions cover source cash/pause sizing, exact cap boundaries, account/venue deduplication, same-block rate ordering, unsampled end-of-block series, conditional-redemption gating and fan-in sender concentration. Two integration tests are skipped by the existing suite configuration.

The prose verifier checks references to existing recipes; it does not independently verify every sentence. Detector economics, position composition and LPT evidence have their own linked artifacts and checks. Historical mechanism assertions from earlier studies were not rerun. Earlier reports are preserved; re-analysis is needed before relying on their rate-series duration estimates.
