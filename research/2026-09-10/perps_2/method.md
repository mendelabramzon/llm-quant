# Hyperliquid and HIP-3, second window: method

All reads are public and unauthenticated (`api.hyperliquid.xyz/info`, `scanner.tradingview.com`). Nothing is signed or
sent. Run from the repository root.

## The window, the tape, and the references

```sh
uv run python scripts/perp_collect.py window --out research/2026-09-10/perps_2 --hours 1 --workers 3 --interval 0.12
uv run python scripts/perp_collect.py tape   --out research/2026-09-10/perps_2 --minutes 30 --every 20
uv run python scripts/perp_refs.py snap      --out research/2026-09-10/perps_2 --minutes 16 --every 60   # alongside the tape
uv run python scripts/perp_scan.py analyze   --out research/2026-09-10/perps_2
uv run python scripts/perp_scan.py tape      --out research/2026-09-10/perps_2
uv run python scripts/perp_scan.py detect    --out research/2026-09-10/perps_2
uv run python scripts/perp_scan.py verify    --out research/2026-09-10/perps_2
uv run python scripts/perp_refs.py compare   --out research/2026-09-10/perps_2
uv run python scripts/perp_refs.py curve     --out research/2026-09-10/perps_2
uv run python scripts/perp_scan.py render    --out research/2026-09-10/perps_2
```

`perp_refs.py` is new. It resolves each builder market to a public reference (futures by contract month, US and
foreign equities, indices, FX, spot metals), snapshots the references and every Hyperliquid book once a minute, and in
`compare` aligns each reference quote with the Hyperliquid snapshot taken the reference's own delay earlier: 10
minutes for futures and indices, 15 for US equities, none for FX and spot metals. Non-USD references are converted with
the FX rows from the same scan. `curve` places the XYZ oil and gas oracles on the futures curve and reports the implied
front-month weight, which is the quantity a hedge has to match. Private-company and unlisted markets have no
reference and are reported as such.

## The funding history

```sh
uv run python scripts/perp_history.py collect --out research/2026-09-10/perps_history --since 2026-07-01 --workers 2 --interval 0.15
uv run python scripts/perp_history.py analyze --out research/2026-09-10/perps_history --window research/2026-09-08/perps_1h
uv run python scripts/perp_history.py render  --out research/2026-09-10/perps_history
```

`perp_history.py` is new. `collect` pages `fundingHistory` (hourly rate and premium, 500 rows a page) and hourly
`candleSnapshot` for every non-delisted market on every perp DEX from the start date to the last complete hour, and
resumes from the last row on disk. `analyze` is offline: per-market extremity and persistence, episodes (runs of hours
with |APR| at or above 100% on one paid side, entered at the close before the first extreme payment and exited at the
close of the first hour back under the threshold), premium snaps (a one-hour premium move above 40bp, with what the
mark did in the same hour), and the out-of-sample table for the earlier window's `funding_carry` and `premium_drift`
hits, held from that window's close to the end of the history. Sign conventions are in the module docstring and pinned
by `scripts/test_perp_history.py`.

## The ledger and the book

```sh
uv run python scripts/findings.py ingest  --out research/2026-09-08/perps_1h --chain hyperliquid
uv run python scripts/findings.py ingest  --out research/2026-09-10/perps_2  --chain hyperliquid
uv run python scripts/seed_strategies.py
uv run python scripts/strategies.py refresh --out research/2026-09-10/perps_2
uv run python scripts/strategies.py book
```

`findings.py` now accepts a window whose bounds are named `start_utc`/`end_utc` (a perp window) as well as
`first_utc`/`last_utc` (a chain window), so the perp detectors' hits are ledger findings keyed on `detector:coin` and
recur, decay and fall due like any other. The perp `funding_carry` and `cross_dex_basis` economics blocks now carry
`net_apr` and `go`, which is what the ledger's decay column and the book's quotes read.

## Limits

- Reference quotes are delayed public quotes, aligned by their stated delay; a residual timing slack of up to a minute
  remains, and US equities were outside regular hours for the whole window.
- The hedged figures in the history are a proxy: funding received plus the change in the venue's own premium, which is
  the experience of a position hedged in an instrument that tracks the oracle exactly. The oracle's methodology is the
  deployer's and unpublished; `curve` measures where it sits on the futures curve but not how it is computed.
- A public hourly history of the front-month futures was not reachable from this machine during the session (Yahoo
  answered 429 throughout), so the reference-hedged path over the history is not measured, only the oracle-hedged one.
- `fundingHistory` is the settled series. A market listed after the start date has a shorter series and says so in the
  hours column.
