# Ethereum mainnet trailing ten-hour study

The directory uses the session's local date (Asia/Tbilisi). The chain window is on **2026-09-09 UTC**.

The new collection was anchored to Infura's `finalized` tag at invocation. Its immutable interval is
`[2026-09-09T10:32:24Z, 2026-09-09T20:32:24Z)`, blocks **25,939,239–25,942,222**, inclusive.
The endpoint timestamp is 20:32:23 UTC. Finality means the latest unfinalized minutes are excluded.
Every full transaction and every log is collected. A resumed collection preserves both boundaries.

## Reproduction

Run from the repository root. These commands use the existing local RPC credentials and make only read requests.

```sh
uv run --with pycryptodome python scripts/live_collect.py collect --out research/2026-09-10/live_10h --hours 10 --end-tag finalized --workers 6 --max-credits 1500000
uv run python scripts/eth_day_collect.py verify --out research/2026-09-10/live_10h
uv run --with pycryptodome python scripts/live_scan.py head --out research/2026-09-10/live_10h --block 25942222
uv run --with pycryptodome python scripts/live_scan.py analyze --out research/2026-09-10/live_10h
uv run --with pycryptodome python scripts/live_scan.py enrich --out research/2026-09-10/live_10h
uv run python scripts/window_events.py --out research/2026-09-10/live_10h --bucket 30 --md
uv run python scripts/fee_census.py receipts --out research/2026-09-10/live_10h --every 4
uv run python scripts/fee_census.py analyze --out research/2026-09-10/live_10h --every 4
uv run --with pycryptodome python scripts/live_scan.py pipeline --out research/2026-09-10/live_10h
uv run python research/2026-09-10/live_10h/roundtrip_evidence.py
uv run python scripts/strategies.py refresh --out research/2026-09-10/live_10h
# After writing or editing insights.md:
uv run python scripts/live_scan.py verify --out research/2026-09-10/live_10h
uv run --with pycryptodome python scripts/live_scan.py render --out research/2026-09-10/live_10h
```

The first analysis discovers pools and active borrowers; `enrich` reads those at the **same pinned block**, preserving prices and rates.
The pipeline rebuilds analysis after that enrichment before verification, detection and ledger ingestion.
The final seven sampled block-hash RPC rechecks matched the saved block manifest. `followup.py` records that recheck
and priority-transaction receipts; `roundtrip_evidence.py` adds canonical factory-pair and historical-reserve reads.
`summary.json` combines existing totals and evaluates the saved `rate_dispersion.marginal_rate_fn`/`sized` curve against
the 3.60% benchmark. It holds borrows fixed and does not simulate other market participants.

## Scope and interpretation

- All-block execution burn is exact in ETH: `sum(gasUsed * baseFeePerGas)`. USD uses the pinned ETH/USD feed.
- Receipt metrics sample every fourth produced block, starting at the first block: a systematic 25% sample, not a random sample.
  Sampled transaction hash sets and summed gas must match their block. Missing receipts fail analysis. Sampled totals are
  not full-window totals; extrapolation is explicitly labelled, without a statistical confidence claim.
- Priority fees are execution tips. They exclude direct builder/proposer transfers, other MEV payments, and blob fees.
  The [Ethereum fee documentation](https://ethereum.org/developers/docs/gas/) describes the base-plus-tip split.
- Opportunity cost scenarios use gas-weighted observed **effective fees including tips**: p75 for ordinary actions, p90
  for competing JIT execution. These are sensitivity assumptions, not inclusion guarantees or measured bot bids.
- USD activity uses the existing token registry, with stablecoins generally at par and other assets at endpoint feeds/NAV.
  Gross swap legs can count a routed trade more than once. Unpriced assets and unsupported protocols are outside valued totals.
- Exchange flow uses labelled addresses and large transfer legs (at least $10,000). Label tiers are reported separately.
  Native ETH flow is based on top-level transaction value; internal transfers and unsampled failed calls are limitations.
- Lending liquidations and market coverage follow the existing decoders. An absence is only an absence in that coverage.
  Health factors cover selected active borrowers at the endpoint, not all borrowers on Ethereum.
- A daytime window cannot test the previously observed UTC-midnight liquidity routine.
- Annualized LP and rate economics are conditional on measured conditions persisting; they are not forecasts.
- The Aave account-data correction decodes word 2 as available borrowing and word 4 as LTV, following the
  [pool interface](https://github.com/aave/aave-v3-core/blob/master/contracts/interfaces/IPool.sol).
  Health checks independently reconcile collateral, liquidation threshold and debt; asset-specific shocks require
  position composition, which this study does not collect.
- `delegated_dust` reads calldata. Its encoded transfer legs are attempts; there is no complete internal-execution census.
- The source-backed historical mechanism assertions were not run: they concern earlier studies, not this window's new claims.

Raw gzip files are retained locally and ignored by git; manifests and derived evidence remain reviewable.
