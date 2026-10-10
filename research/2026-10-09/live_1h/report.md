# Ethereum mainnet live scan: 2026-10-09T20:05:11+00:00 to 2026-10-09T21:04:59+00:00 UTC

Blocks 26157129 to 26157427 (299 blocks, 1.00 h), 80,862 transactions, 284,370 logs. Prices at head block 26157448: ETH $2475, BTC $82k. Generated 2026-10-09T21:13:35+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

# Ethereum, one hour on 2026-10-09: the book's mainnet lines re-quoted after a month

**Window.** Blocks 26,157,129–26,157,427, 2026-10-09 20:05–21:05 UTC: 299 blocks, 80,862 transactions, 284,370 logs
(`live_collect.py collect --hours 1`, two `head` passes, `live_scan.py pipeline`). Its purpose was narrow: six of the
book's Ethereum lines had not been re-priced since 2026-09-10, and a quote that old is a memory. Every number below is
from `analysis.json`, `detectors.json` and the book's quote series.

**What the detectors re-quoted.**

| strategy | last quote before | this window |
|---|---|---|
| `compound-usdc-supply-spread` | 0.74% | **0.41%** — Compound v3 USDC pays 0.82pp over SparkLend, best size $544k, $2.2k a year |
| `morpho-usdt-borrow-vs-aave` | 1.70% | **1.18%** — $1.4M withdrawable in the cheap Morpho USDT market, down from $6.35M |
| `sky-ssr-vs-aave-usds` (benchmark) | 3.33% | **3.63%** — the savings rate is 3.80% on chain |
| `susde-cooldown-redemption` | 6.92% (history) | **14.0%** — sUSDe 6.5bp under NAV, 3.8bp after the round trip, on a one-day cooldown; a window reading of a frequent shallow discount, which the 181-day history prices lower |
| `aave-usdtb-supply` | 0.65% | **not seen** — the USDtb reserve no longer clears the savings rate |
| `usdg-captive-flow-lp` | (8.21%) | **not seen** — no USDG/USDC swaps in the hour |

The Ethereum dollar surface is where the September book left it, a little thinner: the two lending spreads narrowed,
the Morpho saving kept its rate but lost three quarters of its withdrawable size, and USDtb's 8% reserve is gone. The
largest `borrow_cost` hit is USDS borrowed on SparkLend 1.21pp cheaper than on Aave with $371M withdrawable — a saving
for an existing borrower, not a return.

**One verification change, and why it is not a loosening.** The pipeline stopped on two identity failures, both Aave
v3 FRAX ($29.6k supplied): the stored borrow rate (28.20%) was not the IRM at the head utilisation (96.44% → 31.26%).
An Aave reserve stores its rates at its last interaction; an idle one accrues interest, its utilisation drifts up, and
its rates stay put. The stored pair still agrees with itself at one earlier utilisation — 28.20% inverts through the
curve to 95.68%, and the stored supply rate equals 28.20% × 95.68% × 0.8 to within the tolerance — which a decode error
cannot produce. `verify.py` now classifies that case as `head-stale-reserves` (reported, with both utilisations) and
still fails a pair that is inconsistent, or whose implied utilisation is above the head's
(`test_verify_stale_reserve.py`). FRAX's rates imply about 45 days without an interaction.


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

**Recycled turnover:** the detector found same-pool atomic round trips in 1 pool(s). For flagged rows, `fees*` is only gross volume times an assumed tier; realized passive income is unmeasured. Token balance changes through the round trip can contradict that USD fee estimate. See [detector evidence](detectors.md).

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x3b1b…d5b9 | uni v4 | USDT/USDS | 0.00% | 41 | $2.2M | $13 | $0 | $13 | $100.0B | 0.00% | 0.0% | 0.004% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 13 | $1.7M | $10 | $0 | $10 | $149.1B | 0.00% | 0.0% | 0.004% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 939 | $1.3M | $132 | $2 | $131 | $110.2M | 1.04% | 209.6% | 0.473% |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 160 | $1.1M | $10 | $0 | $10 | $7.7B | 0.00% | 0.2% | 0.508% |
| 0xeda6…7edb | uni v4 | USDC/USDG | 0.00% | 6 | $1.0M | $12 | $0 | $12 | $43.1B | 0.00% | 0.1% | 0.010% |
| 0x2b21…f634 | uni v4 | USDC/USDT | 0.00% | 63 | $547k | $3 | $0 | $3 | $21.4B | 0.00% | 0.0% | 0.004% |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 184 | $478k | $239 | $0 | $239 | $273.2M | 0.77% | 154.5% | 0.261% |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 35 | $435k | $217 | $0 | $217 | $544.7M | 0.35% | 70.5% | 0.194% |
| [0xd815…8459](https://etherscan.io/address/0xd815f8f5df15bd9521b5c8c36f65f3ffdd9e8459) | uni v3 | TAUFA/WETH | 0.01% | 439 | $423k | $42 | $0 | $42 | $137k | 270.93% | 54592.0% | 236.951% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 7 | $418k | $209 | $0 | $209 | $11.4B | 0.02% | 3.2% | 0.008% |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 8 | $322k | $10 | $0 | $10 | $11.8B | 0.00% | 0.1% | 0.007% |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.00% | 198 | $299k | $12 | $0 | $12 | $55.3M | 0.18% | 37.0% | 0.359% |
| 0xe500…a657 | uni v4 | USDC/WETH | 0.00% | 186 | $289k | $1 | $0 | $1 | $63.7M | 0.02% | 4.1% | 0.306% |
| [0x6486…b672](https://etherscan.io/address/0x64869c8d4b7c5a6a2f102c9fceea7f7de846b672) | uni v3 | WBTC/0x73e0…db98 | 0.01% | 6 | $289k | $29 | $0 | $29 | $3.4B | 0.01% | 1.5% | – |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 447 | $262k | $26 | $0 | $26 | $16.3M | 1.41% | 284.9% | 0.782% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 71 | $232k | $2 | $0 | $2 | $8.2B | 0.00% | 0.1% | 0.004% |
| 0xb203…448b | uni v4 | sUSDe/USDT | 0.01% | 7 | $212k | $21 | $0 | $21 | $9.2B | 0.00% | 0.4% | 0.005% |
| [0xe8f7…e124](https://etherscan.io/address/0xe8f7c89c5efa061e340f2d2f206ec78fd8f7e124) | uni v3 | WBTC/cbBTC | 0.01% | 3 | $211k | $21 | $0 | $21 | $52.0B | 0.00% | 0.1% | 0.001% |

Just-in-time liquidity: 7 episodes (mint and burn of identical liquidity inside one block), bracketing $21k of swaps and taking about $2 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 3 episodes, fees taken $2
- [0x3437…e4ab](https://etherscan.io/address/0x34373bba18aa058f889c3fc28329c0bfb4b3e4ab): 1 episodes, fees taken $0
- [0xcee2…b279](https://etherscan.io/address/0xcee2cc4ecaa4dfe48c0cdb0b503657ff5247b279): 1 episodes, fees taken $0
- [0x3ee9…c1de](https://etherscan.io/address/0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de): 1 episodes, fees taken $0
- [0xab56…03e2](https://etherscan.io/address/0xab567bb4953ac3b184e6078dd8d3d1dbf2dc03e2): 1 episodes, fees taken $0

Swap volume by venue: uniswap_v4 $9.5M (4404), uniswap_v3 $6.0M (6302), uniswap_v2_like $5.6M (2928), curve $903k (278), balancer $34k (52).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0x161c…aeaa (0x0000…0000/0xc9c8…20cc, 75 swaps); 0x81e6…80c7 (0x68b4…cd19/0xc02a…6cc2, 55 swaps); 0xec7c…c250 (0x0000…0000/0xf9f7…5bd7, 40 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 34 swaps); 0x93aa…ac7f (0xc02a…6cc2/0xdbd7…cc43, 32 swaps); 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 25 swaps); 0xa3a2…c761 (0xa0b8…eb48/0xc9c8…20cc, 25 swaps); 0xfaa4…f0f7 (0x0000…0000/0x1b54…a6b8, 24 swaps); 0x3136…cb82 (0x0000…0000/0x3991…fef3, 22 swaps); 0xca37…e0c4 (0x0000…0000/0x4e67…8722, 19 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | tBTC | 0.00% | 0.26% | 0.1% | $143.9M | $212k |
| Aave v3 | EURC | 2.21% | 3.87% | 63.4% | $45.5M | $28.8M |
| Aave v3 | UNI | 0.00% | 0.19% | 1.2% | $2.9M | $36k |
| Aave v3 | WBTC | 0.00% | 0.32% | 2.1% | $2.8B | $59.7M |
| Aave v3 | GHO | 0.00% | 4.50% | 82.6% | $135.2M | $111.7M |
| Aave v3 | USDe | 0.24% | 6.61% | 4.8% | $332.3M | $15.9M |
| Aave v3 | LINK | 0.02% | 0.64% | 4.1% | $98.4M | $4.1M |
| Aave v3 | LUSD | 0.56% | 2.09% | 33.4% | $1.9M | $627k |
| Aave v3 | DAI | 3.36% | 4.94% | 90.9% | $129.3M | $117.5M |
| Aave v3 | PYUSD | 8.18% | 9.99% | 91.0% | $7.9M | $7.2M |
| Aave v3 | wstETH | 0.00% | 0.03% | 2.4% | $2.4B | $59.0M |
| Aave v3 | AAVE | 0.00% | 0.00% | 0.0% | $136.6M | $0 |
| Aave v3 | LBTC | 0.00% | 0.00% | 0.0% | $221.6M | $1399 |
| Aave v3 | RLUSD | 2.75% | 4.76% | 72.3% | $3.1M | $2.2M |
| Aave v3 | sDAI | 0.00% | 0.00% | 0.0% | $51k | $0 |
| Aave v3 | FRAX | 21.58% | 28.20% | 96.4% | $30k | $29k |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $131.4M | $0 |
| Aave v3 | MKR | 0.00% | 0.16% | 1.1% | $218k | $2308 |
| Aave v3 | USDC | 4.21% | 4.96% | 94.3% | $2.4B | $2.3B |
| Aave v3 | rsETH | 0.00% | 0.00% | 0.0% | $860.3M | $2879 |
| Aave v3 | rETH | 0.00% | 0.02% | 0.1% | $101.2M | $117k |
| Aave v3 | cbETH | 0.00% | 0.05% | 0.3% | $15.7M | $54k |
| Aave v3 | ezETH | 0.00% | 0.00% | 0.0% | – | – |
| Aave v3 | WETH | 1.33% | 1.96% | 79.8% | $5.4B | $4.3B |
| Aave v3 | USDtb | 3.83% | 5.92% | 80.8% | $13.1M | $10.6M |
| Aave v3 | ENS | 0.07% | 1.72% | 8.6% | $85k | $7268 |
| Aave v3 | cbBTC | 0.00% | 0.28% | 0.6% | $1.4B | $8.8M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.8B | $139k |
| Aave v3 | CRV | 0.32% | 5.57% | 11.6% | $2.9M | $336k |
| Aave v3 | USDT | 3.55% | 4.30% | 91.9% | $2.7B | $2.5B |
| Aave v3 | USDS | 0.17% | 5.53% | 4.0% | $8.4M | $338k |
| Aave v3 | USDG | 3.27% | 5.11% | 80.1% | $4.8M | $3.8M |
| Aave v3 | crvUSD | 0.58% | 2.83% | 41.2% | $186k | $76k |
| SparkLend | tBTC | 0.00% | 0.00% | 0.0% | $1.7M | $8 |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $177.4M | $344k |
| SparkLend | DAI | 2.85% | 4.44% | 71.4% | $261.1M | $186.3M |
| SparkLend | PYUSD | 1.03% | 4.29% | 26.6% | $100.0M | $26.6M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.4B | $9895 |
| SparkLend | LBTC | 0.00% | 5.00% | 0.0% | $189.9M | $0 |
| SparkLend | RLUSD | 2.37% | 3.94% | 66.8% | $20.0M | $13.4M |
| SparkLend | sDAI | 0.00% | 1.00% | 0.0% | $30k | $0 |
| SparkLend | USDC | 3.56% | 4.37% | 90.5% | $48.6M | $44.0M |
| SparkLend | rsETH | 0.00% | 5.00% | 0.0% | $7714 | $0 |
| SparkLend | sUSDS | 0.00% | 0.00% | 0.0% | $3.3M | $0 |
| SparkLend | rETH | 0.00% | 0.25% | 0.0% | $11.0M | $2032 |
| SparkLend | ezETH | 0.00% | 5.00% | 0.0% | – | – |
| SparkLend | WETH | 1.45% | 1.91% | 80.3% | $1.6B | $1.3B |
| SparkLend | cbBTC | 0.00% | 0.06% | 4.6% | $333.0M | $15.3M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $104.7M | $0 |
| SparkLend | USDT | 3.40% | 3.97% | 95.1% | $329.1M | $312.9M |
| SparkLend | USDS | 2.70% | 4.32% | 69.4% | $1.2B | $841.8M |
| SparkLend | USDG | 0.00% | 3.54% | 0.0% | $1 | $0 |
| Compound v3 USDC | base | 4.38% | 5.29% | 90.4% | $382.3M | $345.4M |
| Compound v3 USDT | base | 3.20% | 3.97% | 88.9% | $165.1M | $146.7M |
| Compound v3 WETH | base | 1.45% | 1.90% | 72.7% | $125.1M | $90.9M |

Sky savings rate (sUSDS) 3.80% APY, DSR (sDAI) – APY; sUSDe vesting implies 4.73% APR on $1.2B of USDe.

Rate curves: Aave v3 AAVE optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 0%; Aave v3 CRV optimal 45%, base 3.00%, slope1 10.00%, slope2 150.00%, reserve factor 50%; Aave v3 DAI optimal 92%, base 0.00%, slope1 5.00%, slope2 35.00%, reserve factor 25%; Aave v3 ENS optimal 45%, base 0.00%, slope1 9.00%, slope2 300.00%, reserve factor 50%; Aave v3 EURC optimal 90%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 10%; Aave v3 FRAX optimal 90%, base 0.00%, slope1 5.50%, slope2 40.00%, reserve factor 20%; Aave v3 GHO optimal 99%, base 4.50%, slope1 0.00%, slope2 0.00%, reserve factor 100%; Aave v3 LBTC optimal 45%, base 0.00%, slope1 4.00%, slope2 300.00%, reserve factor 50%; Aave v3 LINK optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 LUSD optimal 80%, base 0.00%, slope1 5.00%, slope2 50.00%, reserve factor 20%; Aave v3 MKR optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 50%; Aave v3 PYUSD optimal 90%, base 1.00%, slope1 4.00%, slope2 50.00%, reserve factor 10%; Aave v3 RLUSD optimal 80%, base 2.50%, slope1 2.50%, slope2 50.00%, reserve factor 20%; Aave v3 UNI optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 50%; Aave v3 USDC optimal 94%, base 0.00%, slope1 4.40%, slope2 10.00%, reserve factor 10%; Aave v3 USDG optimal 80%, base 0.00%, slope1 5.00%, slope2 30.00%, reserve factor 20%; Aave v3 USDS optimal 92%, base 5.50%, slope1 0.75%, slope2 35.00%, reserve factor 25%; Aave v3 USDT optimal 94%, base 0.00%, slope1 4.40%, slope2 10.00%, reserve factor 10%; Aave v3 USDe optimal 90%, base 6.60%, slope1 0.25%, slope2 12.00%, reserve factor 25%; Aave v3 USDtb optimal 80%, base 0.00%, slope1 4.00%, slope2 50.00%, reserve factor 20%; Aave v3 WBTC optimal 80%, base 0.25%, slope1 2.50%, slope2 300.00%, reserve factor 50%; Aave v3 WETH optimal 92%, base 0.00%, slope1 2.20%, slope2 6.00%, reserve factor 15%; Aave v3 cbBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 cbETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 crvUSD optimal 80%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 50%; Aave v3 ezETH optimal 45%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 15%; Aave v3 rETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 rsETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 sDAI optimal 90%, base 0.00%, slope1 5.00%, slope2 75.00%, reserve factor 20%; Aave v3 sUSDe optimal 90%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 20%; Aave v3 tBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 weETH optimal 30%, base 1.00%, slope1 7.00%, slope2 300.00%, reserve factor 45%; Aave v3 wstETH optimal 80%, base 0.00%, slope1 1.00%, slope2 40.00%, reserve factor 35%.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | USDC | 63 | 4.99% → 5.10% | 4.99% – 5.15% | 4.24% → 4.34% |
| SparkLend | USDT | 2 | 4.00% → 3.97% | 3.97% – 4.00% | 3.42% → 3.40% |
| SparkLend | USDS | 3 | 4.32% → 4.33% | 4.32% – 4.33% | 2.70% → 2.71% |
| Aave v3 | USDT | 40 | 4.30% → 4.30% | 4.30% – 4.30% | 3.55% → 3.55% |
| Aave v3 | WETH | 48 | 1.96% → 1.96% | 1.95% – 1.96% | 1.33% → 1.33% |
| Aave v3 | GHO | 2 | 4.50% → 4.50% | 4.50% – 4.50% | 0.00% → 0.00% |
| Aave v3 | WBTC | 10 | 0.32% → 0.32% | 0.32% – 0.32% | 0.00% → 0.00% |
| Aave v3 | USDe | 4 | 6.61% → 6.61% | 6.61% – 6.61% | 0.24% → 0.24% |
| Aave v3 | wstETH | 4 | 0.03% → 0.03% | 0.03% – 0.03% | 0.00% → 0.00% |
| Aave v3 | cbBTC | 9 | 0.28% → 0.28% | 0.28% – 0.28% | 0.00% → 0.00% |
| Aave v3 | LINK | 2 | 0.64% → 0.64% | 0.64% – 0.64% | 0.02% → 0.02% |
| Aave v3 | DAI | 3 | 4.94% → 4.94% | 4.94% – 4.94% | 3.37% → 3.36% |
| SparkLend | WETH | 2 | 1.91% → 1.91% | 1.91% – 1.91% | 1.45% → 1.45% |
| SparkLend | RLUSD | 1 | 3.94% → 3.94% | 3.94% – 3.94% | 2.37% → 2.37% |
| Aave v3 | AAVE | 5 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | USDG | 1 | 5.11% → 5.11% | 5.11% – 5.11% | 3.27% → 3.27% |
| Aave v3 | 0x6874…2f38 | 1 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | EURC | 1 | 3.87% → 3.87% | 3.87% – 3.87% | 2.21% → 2.21% |
| SparkLend | WBTC | 1 | 0.01% → 0.01% | 0.01% – 0.01% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: repay $1.6M, borrow $1.2M, supply $6.4M, withdraw $11.1M, atomic supply $8.2M, atomic withdraw $8.2M; SparkLend: withdraw $64k, supply $7.0M, borrow $4.4M, repay $25k.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 26157266 | SparkLend | supply | WETH | $3.6M | [0xdd64…c737](https://etherscan.io/address/0xdd647ce113505b34c62412d2a804ce1bfbcfc737) | [0xdde0…8052](https://etherscan.io/tx/0xdde03353d3720ed377d1baed825d96b3ec0d18ab559b772f1c95ec9a0cad8052) |
| 26157416 | Aave v3 | withdraw | WBTC | $3.4M | [0xdf26…9aaa](https://etherscan.io/address/0xdf2609ec3d2e07a79d2e25e52960e75250bd9aaa) | [0xe919…92a9](https://etherscan.io/tx/0xe919e695b604a85df753deba58ecdf6737303ddc193acf55beb747c509e392a9) |
| 26157423 | SparkLend | supply | WBTC | $3.4M | [0xdf26…9aaa](https://etherscan.io/address/0xdf2609ec3d2e07a79d2e25e52960e75250bd9aaa) | [0x08bd…4efd](https://etherscan.io/tx/0x08bd8e8b2648496b45bde8fe1113b208b229c4fd460f4fdb4c3897cd267f4efd) |
| 26157274 | SparkLend | borrow | RLUSD | $2.4M | [0xdd64…c737](https://etherscan.io/address/0xdd647ce113505b34c62412d2a804ce1bfbcfc737) | [0x3ff1…49b3](https://etherscan.io/tx/0x3ff173e55e72f69453d2db57d4e113afe06935260124f88cb9d7f6cd31c349b3) |
| 26157304 | Aave v3 | withdraw | USDC | $2.2M | [0xd4fa…d23e](https://etherscan.io/address/0xd4fa2d31b7968e448877f69a96de69f5de8cd23e) | [0xa94a…99d7](https://etherscan.io/tx/0xa94a6ff63d28ea765e361376973528e0e831853250e0bca333ae6515f96499d7) |
| 26157425 | SparkLend | borrow | USDS | $2.0M | [0xdf26…9aaa](https://etherscan.io/address/0xdf2609ec3d2e07a79d2e25e52960e75250bd9aaa) | [0x4646…ff90](https://etherscan.io/tx/0x4646541aec8addbaef35fa04cdd324af28b91eb27b94433a0e59088d3f99ff90) |
| 26157426 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x833f…089f](https://etherscan.io/tx/0x833f7a1e984285779eaadaf58646deb7d512fa168da73085a93c1adc729d089f) |
| 26157426 | Aave v3 | withdraw | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xe551…fdf5](https://etherscan.io/tx/0xe5513fbb164af3d3cc383ccc7471038907f2e086477d3e9d70aa12d15aeafdf5) |
| 26157300 | Aave v3 | supply | WETH | $1.8M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x564e…da4e](https://etherscan.io/tx/0x564e21f90c5e34f93b54412f3bfd2bac09aa2a273749bb7bae3681f8b652da4e) |
| 26157130 | Aave v3 | supply | USDC | $1.3M | [0x3bd9…bad0](https://etherscan.io/address/0x3bd9248048df95db4fbd748c6cd99c1baa40bad0) | [0x6a71…db7f](https://etherscan.io/tx/0x6a717c9eb59dbbf03f46c5f1cb6963a93d0694bb4c068e723348a27e3bc0db7f) |
| 26157311 | Aave v3 | repay | USDT | $415k | [0x4101…a4a3](https://etherscan.io/address/0x410144dec85bb1929057829d54fb3b8d3f0ea4a3) | [0xa02a…b74e](https://etherscan.io/tx/0xa02ac00cea6cb6be76824579f93b9e380d4a29a625e215045a7c9630c319b74e) |
| 26157311 | Aave v3 | borrow | USDT | $415k | [0x4101…a4a3](https://etherscan.io/address/0x410144dec85bb1929057829d54fb3b8d3f0ea4a3) | [0xf73e…b917](https://etherscan.io/tx/0xf73e4885e0fcbc5c2d908e16b20b2c3d7389f007bb75b4eb1a480bd8b0e8b917) |
| 26157311 | Aave v3 | supply | USDC | $413k | [0x4101…a4a3](https://etherscan.io/address/0x410144dec85bb1929057829d54fb3b8d3f0ea4a3) | [0xf73e…b917](https://etherscan.io/tx/0xf73e4885e0fcbc5c2d908e16b20b2c3d7389f007bb75b4eb1a480bd8b0e8b917) |
| 26157233 | Aave v3 | withdraw | USDT | $404k | [0x38f6…3848](https://etherscan.io/address/0x38f6a1b46144faee6a6d9f79d8de264c18e23848) | [0xbcc8…c771](https://etherscan.io/tx/0xbcc85e53ec61ff008d3f88102025bea64674e74b25463ead739133fe8837c771) |
| 26157423 | Aave v3 | supply | USDC | $345k | [0x3bd9…bad0](https://etherscan.io/address/0x3bd9248048df95db4fbd748c6cd99c1baa40bad0) | [0xe1cd…9548](https://etherscan.io/tx/0xe1cdf9e7410f6445ec63e68cda5074042680974aa70bd4329ceb7156d2749548) |
| 26157296 | Aave v3 | withdraw | USDT | $260k | [0xe286…79e8](https://etherscan.io/address/0xe28660e51e08f988aef28e46421305e83eb479e8) | [0xaaab…71cf](https://etherscan.io/tx/0xaaab66e2bd71ca0fa99d6d06e1a27698e9a757788afdb8bdeb038dfc540871cf) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- Aave v3 withdraw $3.4M WBTC by [0xdf26…9aaa](https://etherscan.io/address/0xdf2609ec3d2e07a79d2e25e52960e75250bd9aaa) ([0xe919…92a9](https://etherscan.io/tx/0xe919e695b604a85df753deba58ecdf6737303ddc193acf55beb747c509e392a9)): $3.4M → [0x4197…15b2](https://etherscan.io/address/0x4197ba364ae6698015ae5c1468f54087602715b2)
- SparkLend borrow $2.4M RLUSD by [0xdd64…c737](https://etherscan.io/address/0xdd647ce113505b34c62412d2a804ce1bfbcfc737) ([0x3ff1…49b3](https://etherscan.io/tx/0x3ff173e55e72f69453d2db57d4e113afe06935260124f88cb9d7f6cd31c349b3)): $2.4M → [0xa7a2…6f9f](https://etherscan.io/address/0xa7a2b57866f6b68032797bfcc6ae6d779a776f9f) → forwarded to Binance 14 (model-memory) **[to exchange $2.4M]**
- Aave v3 withdraw $2.2M USDC by [0xd4fa…d23e](https://etherscan.io/address/0xd4fa2d31b7968e448877f69a96de69f5de8cd23e) ([0xa94a…99d7](https://etherscan.io/tx/0xa94a6ff63d28ea765e361376973528e0e831853250e0bca333ae6515f96499d7)): $2.2M → [0x4b94…093b](https://etherscan.io/address/0x4b94ddf643cd0e1ae993c5912e23c884a63b093b)
- Aave v3 withdraw $1.8M WETH by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xe551…fdf5](https://etherscan.io/tx/0xe5513fbb164af3d3cc383ccc7471038907f2e086477d3e9d70aa12d15aeafdf5)): $1.8M → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $1.8M → [0x0000…594e](https://etherscan.io/address/0x000000000035b5e5ad9019092c665357240f594e)
- Aave v3 borrow $415k USDT by [0x4101…a4a3](https://etherscan.io/address/0x410144dec85bb1929057829d54fb3b8d3f0ea4a3) ([0xf73e…b917](https://etherscan.io/tx/0xf73e4885e0fcbc5c2d908e16b20b2c3d7389f007bb75b4eb1a480bd8b0e8b917)): $415k → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $415k → [Aave v3 USDT (blockscout-verified)](https://etherscan.io/address/0x23878914efe38d27c4d67ab83ed1b93a74d4086a); $266k → [0x0457…432c](https://etherscan.io/address/0x04571c32a4e1c5f39bc3a238cb95b215058c432c)
- Aave v3 withdraw $404k USDT by [0x38f6…3848](https://etherscan.io/address/0x38f6a1b46144faee6a6d9f79d8de264c18e23848) ([0xbcc8…c771](https://etherscan.io/tx/0xbcc85e53ec61ff008d3f88102025bea64674e74b25463ead739133fe8837c771)): $404k → [CoW Protocol settlement (GPv2Settlement) (known-canonical)](https://etherscan.io/address/0x9008d19f58aabd9ed0d60971565aa8510560ab41)
- Aave v3 withdraw $260k USDT by [0xe286…79e8](https://etherscan.io/address/0xe28660e51e08f988aef28e46421305e83eb479e8) ([0xaaab…71cf](https://etherscan.io/tx/0xaaab66e2bd71ca0fa99d6d06e1a27698e9a757788afdb8bdeb038dfc540871cf)): $260k → [0x58d7…0ba9](https://etherscan.io/address/0x58d75b0389da45c62eba861f2c2857d51bc30ba9) → forwarded to Binance 14 (model-memory) **[to exchange $260k]**

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| Aave v3 | [0xdf26…9aaa](https://etherscan.io/address/0xdf2609ec3d2e07a79d2e25e52960e75250bd9aaa) | $16.7M | $10.1M | 1.298 | 22.9% |
| SparkLend | [0xdd64…c737](https://etherscan.io/address/0xdd647ce113505b34c62412d2a804ce1bfbcfc737) | $3.6M | $2.4M | 1.280 | 21.9% |
| SparkLend | [0xdf26…9aaa](https://etherscan.io/address/0xdf2609ec3d2e07a79d2e25e52960e75250bd9aaa) | $3.4M | $2.0M | 1.316 | 24.0% |
| Aave v3 | [0xd4fa…d23e](https://etherscan.io/address/0xd4fa2d31b7968e448877f69a96de69f5de8cd23e) | $72.7M | $0 | ∞ | – |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| Aave v3 | [0x3bd9…bad0](https://etherscan.io/address/0x3bd9248048df95db4fbd748c6cd99c1baa40bad0) | $3.3M | $0 | ∞ | – |

Flash loans (events): BalFlash 18 ($2.5M).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x4101…a4a3](https://etherscan.io/address/0x410144dec85bb1929057829d54fb3b8d3f0ea4a3): 2 transactions, largest leg $3.7M, gross $8.2M; legs: WETH withdraw $8.2M

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDS | 40 | $3.8M | 0.999823 | 0.999788 – 0.999854 | 1 | -1.8 bps |
| USDT | 166 | $2.0M | 0.999111 | 0.999086 – 0.999138 | 0.999055 | +0.6 bps |
| USDG | 14 | $1.1M | 0.999963 | 0.999916 – 1 | 1 | -0.4 bps |
| TAUFA | 344 | $385k | 0.00188461 | 0.0011843 – 0.00285545 | – | – |
| USDe | 5 | $321k | 0.999611 | 0.999574 – 0.999685 | 1 | -3.9 bps |
| RLUSD | 3 | $305k | 1.00002 | 0.999784 – 1.00003 | 1 | +0.2 bps |
| sUSDe | 5 | $211k | 1.25142 | 1.2514 – 1.25147 | 1.25224 | -6.5 bps |
| DAI | 9 | $184k | 0.999616 | 0.999608 – 0.999901 | 0.999889 | -2.7 bps |
| BUNKER | 162 | $165k | 0.0152295 | 0.0143418 – 0.0159608 | – | – |
| USD1 | 5 | $136k | 0.999214 | 0.999019 – 0.999224 | 1 | -7.9 bps |
| CLAUS | 51 | $135k | 0.0144096 | 0.0137501 – 0.0150776 | – | – |
| crvUSD | 15 | $110k | 0.999848 | 0.999416 – 1.00164 | 1 | -1.5 bps |
| RAD | 51 | $101k | 0.351493 | 0.338385 – 0.363867 | – | – |
| SIMD | 65 | $97k | 0.000662749 | 0.000348805 – 0.00107112 | – | – |
| ONDO | 30 | $73k | 0.475067 | 0.472921 – 0.477393 | – | – |
| IMD | 36 | $72k | 8.55687 | 8.34126 – 8.75751 | – | – |
| QNT | 38 | $58k | 245.035 | 243.664 – 246.211 | – | – |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 194 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDC | $175.9M | $172.1M | $3.8M |
| ETH | $16.2M | $114.1M | $-97.8M |
| LINK | $129.8M | $120k | $129.7M |
| USDT | $40.5M | $47.8M | $-7.3M |
| USDG | $15.6M | $10.0M | $5.6M |
| RLUSD | $2.8M | $0 | $2.8M |
| USD1 | $134k | $2.1M | $-1.9M |
| PYUSD | $0 | $1.6M | $-1.6M |
| UNI | $81k | $1.0M | $-933k |
| EURC | $79k | $534k | $-455k |
| AAVE | $211k | $391k | $-179k |
| WBTC | $537k | $0 | $537k |

By label: hot wallet (behaviour, day study) in $59.2M / out $173.9M; Coinbase 10 (model-memory) in $84.3M / out $96.0M; Binance 14 (model-memory) in $147.8M / out $3.8M; Coinbase 11 (model-memory) in $75.5M / out $62.6M; Bitfinex 2 (model-memory) in $9.0M / out $33k; hot wallet (day study, unidentified) (model-memory) in $4.8M / out $2.3M; Binance 16 (model-memory) in $0 / out $4.1M; Binance 18 (model-memory) in $0 / out $2.7M; Binance 15 (model-memory) in $0 / out $1.9M; Binance 20 (model-memory) in $0 / out $1.4M; Coinbase 5 (model-memory) in $929k / out $163k; Gate.io (model-memory) in $507k / out $218k.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 26157271 | WBTC | $475.3M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xd637…95c7](https://etherscan.io/tx/0xd6375bb2c6d91246b63b7439208ccd1b0430c39bf017a1180c72dd614d1195c7) |
| 26157271 | WBTC | $475.3M | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd637…95c7](https://etherscan.io/tx/0xd6375bb2c6d91246b63b7439208ccd1b0430c39bf017a1180c72dd614d1195c7) |
| 26157271 | USDC | $117.2M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xd637…95c7](https://etherscan.io/tx/0xd6375bb2c6d91246b63b7439208ccd1b0430c39bf017a1180c72dd614d1195c7) |
| 26157271 | USDC | $117.2M | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd637…95c7](https://etherscan.io/tx/0xd6375bb2c6d91246b63b7439208ccd1b0430c39bf017a1180c72dd614d1195c7) |
| 26157230 | LINK | $113.4M | [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) | [0xf977…acec](https://etherscan.io/address/0xf977814e90da44bfa03b6295a0616a897441acec) | [0x5814…1921](https://etherscan.io/tx/0x5814c72afb78ee67a8863487ed5fdee901988f690c45c0b363ee808ca4651921) |
| 26157184 | WBTC | $108.1M | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) | [0xd7b3…6f0a](https://etherscan.io/tx/0xd7b3220af299164dda78a1094ff48b77e35e334d6ba2a3997483cf87db106f0a) |
| 26157184 | WBTC | $108.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) | [0xd7b3…6f0a](https://etherscan.io/tx/0xd7b3220af299164dda78a1094ff48b77e35e334d6ba2a3997483cf87db106f0a) |
| 26157184 | WBTC | $108.1M | [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0xd7b3…6f0a](https://etherscan.io/tx/0xd7b3220af299164dda78a1094ff48b77e35e334d6ba2a3997483cf87db106f0a) |
| 26157184 | WBTC | $108.1M | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0xd7b3…6f0a](https://etherscan.io/tx/0xd7b3220af299164dda78a1094ff48b77e35e334d6ba2a3997483cf87db106f0a) |
| 26157184 | WBTC | $108.1M | [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd7b3…6f0a](https://etherscan.io/tx/0xd7b3220af299164dda78a1094ff48b77e35e334d6ba2a3997483cf87db106f0a) |
| 26157346 | ETH | $106.8M | [0xa9ac…4573](https://etherscan.io/address/0xa9ac43f5b5e38155a288d1a01d2cbc4478e14573) | [0x9c22…831c](https://etherscan.io/address/0x9c22a4039f269e72de6b029b273be059cdbb831c) | [0x4334…d46a](https://etherscan.io/tx/0x4334145d1643b0adab30206fd9cf34f414855642220bedde4f68711cbb37d46a) |
| 26157168 | LINK | $57.5M | [0x9b1c…cde9](https://etherscan.io/address/0x9b1c1752b6b6eaf62a8c491a8681b32c1f7ecde9) | [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) | [0x1d0f…9c4e](https://etherscan.io/tx/0x1d0f1263c828d4ff2a147c05ef27b96f6527a2a7f032e8cf1e02a4e82e459c4e) |
| 26157132 | USDC | $50.0M | [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) | [0xc0a2…265a](https://etherscan.io/address/0xc0a2bc76be4cfda76594dcae17894317be2b265a) | [0x10b6…87be](https://etherscan.io/tx/0x10b69c05713c99a481df7261ca28fedc23a9a73793328bf2da67bb2c6e7587be) |
| 26157146 | USDC | $50.0M | [0xc0a2…265a](https://etherscan.io/address/0xc0a2bc76be4cfda76594dcae17894317be2b265a) | [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) | [0x214e…97f2](https://etherscan.io/tx/0x214eba09c258a4a721db4d4f54c334630a8b6f0eb40d87eb08be0e55887b97f2) |
| 26157174 | USDC | $49.7M | [0x4d38…9160](https://etherscan.io/address/0x4d38769e5a15513b6312895a5ce17f0797a59160) | [0xa9d1…3e43](https://etherscan.io/address/0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43) | [0x2cb4…c92c](https://etherscan.io/tx/0x2cb45c9ed5f08ae4004a346ab1a271fd0acfc1cb9d81f9fa85fc9a8364c4c92c) |
| 26157271 | WETH | $39.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xd637…95c7](https://etherscan.io/tx/0xd6375bb2c6d91246b63b7439208ccd1b0430c39bf017a1180c72dd614d1195c7) |
| 26157271 | WETH | $39.4M | [0x0ea0…c438](https://etherscan.io/address/0x0ea041260095b20feda41ef4fdbef7d801f4c438) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd637…95c7](https://etherscan.io/tx/0xd6375bb2c6d91246b63b7439208ccd1b0430c39bf017a1180c72dd614d1195c7) |
| 26157279 | ETH | $37.1M | [0xc263…54f7](https://etherscan.io/address/0xc263058778daeacfa39bd47c4fdba8d46fef54f7) | [0x403e…78ff](https://etherscan.io/address/0x403e17bdfb54187ea041977d551f9ca7241c78ff) | [0x1e72…c3fc](https://etherscan.io/tx/0x1e7295d5ae308ecbad5d53281a96bb1f87b0b993ac94ee47013f53c093c1c3fc) |
| 26157143 | WETH | $35.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xc2ed…046a](https://etherscan.io/tx/0xc2ed464310bc50b1087424e7511c2f3770c707b160ac23144c0997e88290046a) |
| 26157143 | WETH | $35.7M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xc2ed…046a](https://etherscan.io/tx/0xc2ed464310bc50b1087424e7511c2f3770c707b160ac23144c0997e88290046a) |
| 26157199 | WETH | $35.7M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x87f7…5ff2](https://etherscan.io/tx/0x87f71feb7d52a00f1479e7c0136c612ed74e842d0a40ace124318c5686b15ff2) |
| 26157199 | WETH | $35.7M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x87f7…5ff2](https://etherscan.io/tx/0x87f71feb7d52a00f1479e7c0136c612ed74e842d0a40ace124318c5686b15ff2) |
| 26157322 | LINK | $25.6M ×2 | [0x9b1c…cde9](https://etherscan.io/address/0x9b1c1752b6b6eaf62a8c491a8681b32c1f7ecde9) | [0x28c6…1d60](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) | [0xa98a…2274](https://etherscan.io/tx/0xa98a109dcc7ce53a48eb26dea457ca89d328b2315630f49bfba2d8dd5b652274) |
| 26157208 | LINK | $25.6M ×2 | [0x4a87…f6cf](https://etherscan.io/address/0x4a87ece3efffcb012fbe491aa028032e07b6f6cf) | [0x9b1c…cde9](https://etherscan.io/address/0x9b1c1752b6b6eaf62a8c491a8681b32c1f7ecde9) | [0xab59…4201](https://etherscan.io/tx/0xab591f1b6523c9513f81d9c6ecfc37fb0d517a25f50110801102f7c583e94201) |
| 26157191 | ETH | $25.1M | [0xcd53…ca7b](https://etherscan.io/address/0xcd531ae9efcce479654c4926dec5f6209531ca7b) | [0x951e…4035](https://etherscan.io/address/0x951e83f8800f547ae749f293da4f5769dfd04035) | [0x2307…36f4](https://etherscan.io/tx/0x2307bf4022bb5f93c0e261a60d12f0714f7df666384df1082353114636f336f4) |
| 26157246 | WETH | $21.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x4bab…f412](https://etherscan.io/address/0x4babacf0cac16610059c53206d1ffd0049f3f412) | [0x1974…5425](https://etherscan.io/tx/0x1974dda644b71057ce5ff04cbbae876c1ce221fb297cf0b2fe53806715505425) |
| 26157246 | WETH | $21.5M | [0x4bab…f412](https://etherscan.io/address/0x4babacf0cac16610059c53206d1ffd0049f3f412) | [0xdacc…3b94](https://etherscan.io/address/0xdacc39450d67784a4648e4ce42f2789e3ba23b94) | [0x1974…5425](https://etherscan.io/tx/0x1974dda644b71057ce5ff04cbbae876c1ce221fb297cf0b2fe53806715505425) |
| 26157246 | WETH | $21.5M | [0xdacc…3b94](https://etherscan.io/address/0xdacc39450d67784a4648e4ce42f2789e3ba23b94) | [0x4bab…f412](https://etherscan.io/address/0x4babacf0cac16610059c53206d1ffd0049f3f412) | [0x1974…5425](https://etherscan.io/tx/0x1974dda644b71057ce5ff04cbbae876c1ce221fb297cf0b2fe53806715505425) |
| 26157246 | WETH | $21.5M | [0x4bab…f412](https://etherscan.io/address/0x4babacf0cac16610059c53206d1ffd0049f3f412) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x1974…5425](https://etherscan.io/tx/0x1974dda644b71057ce5ff04cbbae876c1ce221fb297cf0b2fe53806715505425) |
| 26157346 | USDT | $21.0M | [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) | [0x6ac3…f60b](https://etherscan.io/address/0x6ac38d1b2f0c0c3b9e816342b1ca14d91d5ff60b) | [0x55b1…877b](https://etherscan.io/tx/0x55b11dfc2fc23ec65e9c1b96701e40c66365b24ad2252bcf0851a0af7958877b) |

Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0x01b6…f408](https://etherscan.io/address/0x01b6386cc069f07063f3f15ec2578e166f06f408) | DAI → USDT | 4 | $125k | $31k | 396s | 0.08 | 0.18 | curve 4 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 26157179 | uniswap_v2_like | 0x622b…bf2d → WETH | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0xf2ef…04e8](https://etherscan.io/tx/0xf2eff69f95828f85213729c859e39fa4ff0cf163087ea7ce5f224c23a09f04e8) |
| 26157179 | uniswap_v2_like | WETH → 0x622b…bf2d | $2.5M | [0x5afe…6f32](https://etherscan.io/address/0x5afec0de001999766fb883860cae06f5932e6f32) | [0xf2ef…04e8](https://etherscan.io/tx/0xf2eff69f95828f85213729c859e39fa4ff0cf163087ea7ce5f224c23a09f04e8) |

## E. Bridges, issuance, staking

Outbound: $5.7M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $2.5M (118).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| CCTP | USDC | Arbitrum | 19 | $3.2M | 0x4b94ddf643cd… $2.2M |
| CCTP | USDC | domain 19 | 47 | $800k | 0xe23f406ba4fe… $600k |
| CCTP | USDC | OP Mainnet | 7 | $657k | 0x8ec0170b28dc… $647k |
| CCTP | USDC | Base | 19 | $317k | 0x2917956eff0b… $301k |
| CCTP | USDC | Avalanche | 6 | $223k | 0x5e023c31e1d3… $221k |
| OFT | USDT | eid 30420 | 1 | $208k | – |
| CCTP | USDC | Solana | 10 | $123k | 953fa59e872410… $51k |
| CCTP | USDC | domain 26 | 2 | $123k | 0xa54dc4425190… $120k |
| OFT | USDT | Polygon | 3 | $45k | – |
| OFT | USDT | eid 30295 | 1 | $17k | – |
| OFT | USDG | eid 30416 | 3 | $16k | – |
| OFT | EURC | OP | 1 | $11k | – |
| CCTP | USDC | Polygon | 10 | $5111 | 0xc1062b7c5dc8… $3001 |
| OFT | USDC | Arbitrum | 1 | $3000 | – |
| OFT | USDG | Arbitrum | 1 | $2532 | – |
| CCTP | USDC | domain 25 | 3 | $1400 | 0xcf1957f88543… $1400 |
| OFT | USDC | eid 30401 | 1 | $1036 | – |
| CCTP | USDC | Linea | 2 | $1012 | 0x33fc2046b564… $1000 |
| CCTP | USDC | domain 27 | 2 | $365 | 0x291790269332… $365 |
| OFT | USDT | eid 30125 | 2 | $123 | – |

Issuance totals: USDC mint $15.2M (184); USDC burn $42.2M (156). Largest: USDC mint $10.6M ([0x5014…2ef6](https://etherscan.io/tx/0x501443f93df758d714a69c12b625c45291fe1823733393ca9913c8c11ed72ef6)); USDC burn $6.0M ([0x5de3…00e0](https://etherscan.io/tx/0x5de30bc0273ec20a58e957e8a5748c873386ed897b45d448c9afb848eb9200e0)); USDC burn $5.2M ([0xc804…c777](https://etherscan.io/tx/0xc8049d38e3cf3bf96148323b99102294a3b58e4392b5e2f7bdc4e31eba9fc777)); USDC burn $2.6M ([0xe72d…8a64](https://etherscan.io/tx/0xe72df01d50d03f3cf13d282180a3c25bf50acd56aa3b8d5fd76580eb46008a64)); USDC burn $2.2M ([0x17ac…bd4b](https://etherscan.io/tx/0x17acced6f807e96fcab69fbbd2facef2e5d9c49a16f62b11c0e3f84aab96bd4b)).


WETH wrapped 3492 ETH, unwrapped 1701 ETH; Lido staked 16.5 ETH, withdrawal requests 4060.3 ETH; sUSDe cooldowns 2 for $157k.


## F. Gas market and block production

Base fee 0.239 → 0.099 gwei (min 0.086, median 0.12, max 0.268); blocks 49% full; median tip 0.077 gwei; 2.9% of transactions pay zero tip; builders:  Quasar (quasar.win)  109, Titan (titanbuilder.xyz) 99, BuilderNet 41, Eureka (eurekabuilder.xyz) 11, bombora.build  10, Nethermind v2.1.0 5.


Most active senders: [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 544, [0x5594…ed53](https://etherscan.io/address/0x559432e18b281731c054cd703d4b49872be4ed53) 524, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 405, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 344, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x264bd8291fae1d75db2c5f573b07faa6715997b5) 341, [0xbb2f…37e0](https://etherscan.io/address/0xbb2f33f73ccc2c74e3fb9bb8eb75241ac15337e0) 331, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 330, [hot wallet (behaviour, day study)](https://etherscan.io/address/0xf30ba13e4b04ce5dc4d254ae5fa95477800f0eb0) 309, [0x3963…aa49](https://etherscan.io/address/0x396343362be2a4da1ce0c1c210945346fb82aa49) 258, [Binance 17 (model-memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 236.


Intent fills: CoWTrade 201, OneInchFilled 220, UniXFill 38. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

