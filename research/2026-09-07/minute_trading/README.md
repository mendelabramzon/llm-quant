# Ethereum mainnet, positions held for minutes

The requested scope is any token on Ethereum mainnet, with trades lasting minutes. This first implementation is a bounded **paper experiment**, using current mainnet pool state and no wallet. Actual capital, allowed loss, and a signing arrangement have not been supplied. The $10,000 balance, $1,000 position, and $200 session loss threshold below are virtual research assumptions, not a capital allocation.

Run from the repository root, choosing a new output directory each time:

```sh
uv run --with pycryptodome python scripts/minute_trader.py \
  --out research/2026-09-07/minute_trading/next_trial \
  --minutes 30 --hold-seconds 300 --interval 30 \
  --notional-usd 1000 --cash-usd 10000 --max-loss-usd 200
```

`--minutes 0` takes one observation without opening positions. A trial lasts at most 60 minutes and exits at its end where a quote remains available. The planned holding window is configurable from 120 to 600 seconds. Stop and session loss thresholds can trigger earlier; polling, RPC failures, or loss of liquidity can delay exits. Entry is disabled when less than the planned holding period remains. The process stops when the bounded trial finishes; there is no installed daemon or background service.

The universe is discovered from 75 recent blocks of Uniswap v3 swap-shaped logs. It inspects the top 40 emitters by event count, checks pool identity against the canonical factory, reads token metadata, and chooses 10 supported pools by quote-side volume. Any base token can qualify, but this first adapter covers only direct WETH/USDC quote pairs on Uniswap v3. It does not scan all tokens, other DEXs, or other Uniswap versions. Activity can be manipulated; discovery ranking is not a quality endorsement.

The unvalidated rule looks for a three-minute price increase above both 50 basis points and twice the modeled round-trip cost, confirmed by a positive one-minute move, at least five recent swaps and at least 60% buy-side quote flow. It queues a candidate and requires it to qualify again at a later snapshot before recording a paper entry. The observation that a price recently moved more than costs is **not evidence that it will continue**. There has been no parameter optimization or claim of predictive advantage.

Pool fees and price impact come from pinned QuoterV2 calls in both directions. Each paper output gets an additional 20-basis-point haircut. Gas uses the observed gas market with a base-fee buffer, router overhead, and a 60,000-gas approval allowance on each leg. Exits quote the amount actually recorded at entry, preserving both entry and exit costs in simulated P&L. WETH and USDC are valued with checked Chainlink feeds. The accounting assumes the necessary quote asset and native gas inventory; wrapping, quote-asset conversion, and actual wallet funding are not modeled.

Quoter results are indications, not executed fills. Independent quotes do not persist our simulated market impact, test a funded wallet's full buy/approve/sell path, or account for token taxes, blacklists, MEV, failed transactions, and execution latency. A verified pool and a successful reverse quote do not establish token safety or sellability. Before real execution, these gaps need a wallet-specific fork simulation and prospective performance evidence after costs. Do not put private keys in chat or these artifacts.

Only read RPC methods are permitted. Contract calls have gas caps. Raw responses omit credentials and are saved with request parameters. Snapshots preserve timestamps and block hashes, recheck current and previous observed heads, reject stale data, and stop on detected reorgs. There is at most one paper position; failed exits stay open and prevent new entries. A loss threshold is a trigger, not a guaranteed loss cap.

Outputs are `discovery.json`, `snapshot_*.json`, `paper_book.json`, `report.md`, `run_status.json`, and `raw/`. An interrupted or failed run records its status and any unresolved paper position. Existing output directories are refused to preserve trial history.

Validation:

```sh
uv run --with pycryptodome python -m unittest discover -s scripts -p test_minute_trader.py
```

The tests cover decimal and token-order conversion, signed flows, conservative output rounding, causal entries, cost/staleness filtering, P&L accounting, failed exits, loss halts, late-entry suppression, invalid configuration, and the RPC read-only boundary.

Implementation references: [QuoterV2 interface](https://github.com/Uniswap/v3-periphery/blob/main/contracts/interfaces/IQuoterV2.sol), [QuoterV2 implementation](https://github.com/Uniswap/v3-periphery/blob/main/contracts/lens/QuoterV2.sol), and [Uniswap v3 swap events](https://github.com/Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol).
