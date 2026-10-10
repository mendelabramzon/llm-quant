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
