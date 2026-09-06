# Five WETH round trips, blocks 25,918,255–25,918,258

The five transactions produced **0.015085355775556401 ETH, approximately $37.74, after gas and direct builder payments**. The $25M transfer alerts are the principal of five separate fee-free Morpho flash loans. They are not the traded amount or the profit. The two execution contracts are not assumed to have the same owner.

## What happens

Each transaction borrows exactly **9,987.297572591 WETH** from Morpho at `0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb`. Its `FlashLoan` event and call trace confirm the mechanism; the identical amount returns at the end. Between borrowing and repayment, the execution contract trades small amounts around closed exchange routes, unwraps the surplus WETH, pays the block builder in native ETH, and pays the remainder to a recipient. Gas is additionally charged to the submitting address.

[Morpho's documentation](https://legacy.docs.morpho.org/morpho/tutorials/free-flash-loans) confirms that its flash loans have no loan fee and require repayment within the same transaction. If repayment fails, the transaction reverts. A successful flash loan leaves no outstanding debt.

WETH is [wrapped ETH](https://weth.io/): the ERC-20 form used by token contracts and exchange pools, redeemable into native ETH. It provides the funding and accounting currency here. The loans do not express a view about ETH's price. The full loan amount is encoded in the submitted calldata, before the Morpho call; it is not the observed exchange input amount. All five reuse that number while trading very different sizes. A generous reusable funding allocation is a plausible explanation for the oversizing, but the off-chain sizing policy is not established by these traces. The unused principal remains with the execution contract during the route and is repaid, and Morpho's zero fee makes the extra principal cheap to borrow.

## Routes and profit

Values below mark ETH at **$2,501.73911263**, the Chainlink ETH/USD answer retrieved separately at each of the four blocks. This is a valuation of ETH proceeds, not a USD cash payout. Gross profit already reflects exchange and hook costs; it is before gas and direct builder payment.

| Block | Transaction | Route | Gross | Builder payment | Gas | Net |
|---|---|---|---:|---:|---:|---:|
| 25,918,255 | [0x48e7…3e71](https://etherscan.io/tx/0x48e76f2a95b299a50b500fef292aec3d18c13275d8db0d039226523568a93e71) | Two WETH → STONKREUM → USDC → WETH loops | $12.34 | $7.40 | $0.19 | **$4.75** |
| 25,918,255 | [0x79b6…ef44](https://etherscan.io/tx/0x79b6e003c7875cd6b8f6a5d5a12185bc1f77923d0885d415fc58ad518bceef44) | WETH → STONKREUM → USDC → ETH/WETH | $0.77 | $0.47 | $0.13 | **$0.17** |
| 25,918,256 | [0x1ce1…94c0](https://etherscan.io/tx/0x1ce14251154eaa92ad3afbf54ca108bcf95b91229973e29e3988bf4ccbe894c0) | Two STONKREUM loops plus WETH → USDC → USDT → USDS → ETH/WETH | $97.78 | $65.25 | $0.32 | **$32.21** |
| 25,918,257 | [0x53f3…b76c](https://etherscan.io/tx/0x53f35442939398107ff25290484902a29eb515aa7683724a7928f117e80bb76c) | WETH/ETH → MUon → USDT → WETH | $0.84 | $0.15 | $0.12 | **$0.57** |
| 25,918,258 | [0x6afb…bbd4](https://etherscan.io/tx/0x6afb8db6c1a4d5f1ed76b7b8c9b0eb7fd0733844f3f0551c7500c02facb3bbd4) | WETH/ETH → USDS → USDT → WETH | $0.15 | $0.01 | $0.10 | **$0.04** |
| | | Total, calculated before rounding | **$111.87** | **$73.29** | **$0.85** | **$37.74** |

The first transaction actually spends about **0.02549 WETH ($63.77)** across its two loops and receives about **0.03042105 WETH ($76.11)** back. Its 9,987 WETH loan is vastly larger than its trading requirement. Most of the principal never enters a pool.

The STONKREUM symbol and Stonkreum.fun name were retrieved from `0x89587d36065cb81b49b783bd3cd3c210c4ccd210` at block 25,918,258. Its WETH and USDC pools provide different effective prices: these transactions buy the token with WETH and sell the same token quantity for USDC, then close the loop back into ETH/WETH. That establishes an executed arbitrage opportunity. It does not establish a fundamental investment thesis or the origin of the mismatch. All three transactions finish with zero net STONKREUM inventory change.

MUon at `0x050362ab1072cb2ce74d74770e22a3203ad04ee5` identifies itself as Micron Technology (Ondo Tokenized); [the issuer's filed terms](https://www.lb.lt/uploads/prospectuses/docs/63984_e75140c04ea31178edaa056295f053e6.pdf) corroborate its address. The fourth transaction similarly finishes without a MUon inventory change. The fifth trades only ETH/WETH and stablecoins. The observed changing routes are consistent with automated searches for profitable exchange cycles; the logs do not identify the off-chain search algorithm or prove exactly why each price gap arose.

## Reading the live display

The alert is a large-transfer filter, so the enormous funding and repayment legs dominate the display while the small trades and ETH payouts are omitted. Five loans generate ten displayed transfers and roughly $250M of gross transfer volume, while the net principal flow is zero.

`base 0.11 gwei` is Ethereum's base gas fee, not the Base network. Titan and BuilderNet are the builders of those Ethereum blocks. All five receipts have zero priority fee above the base fee; the traces nevertheless show **$73.29 of direct ETH payments to the block fee recipients**. A zero priority fee therefore does not mean the builder was unpaid.

The “re-analysed blocks” line is a rolling-window summary of many transactions. Its swap count, JIT count, lending count and exchange net flows are not profit figures for these five loans.

## Evidence and reproduction

`raw/` retains the locally collected transaction/block/log records, independent dRPC receipts, successful call traces, prestate-tracer transaction diffs, token metadata and historical Chainlink answers. Four independently retrieved block headers match the locally collected hashes. Every receipt is successful and its logs exactly match the local logs. `requests.jsonl` records successful HTTP responses and RPC errors; the initial transient HTTP failures are not recorded there. These are RPC-provider observations, not locally verified consensus proofs.

`inspect.py` collects the evidence with read-only RPC methods and caches results. `analyze.py` is offline and writes `summary.json`, retaining exact wei amounts and unrounded valuations. Run from the repository root:

```sh
python3 research/2026-09-06/weth_roundtrips/analyze.py
```

The accounting combines the native balance changes of each submitting address, its execution contract and its explicit non-builder payout recipient. It independently verifies that these changes equal successful native call flows minus receipt gas. In `0x53f3…b76c`, the payout goes to `0xd3c9ba180b831e75c361baf68694d45e7ba53418`, while a different sender pays gas; the reported figure combines those transaction cash flows without claiming proven common ownership. All other native payouts go to their submitting addresses. Token transfers plus WETH wrapping/unwrapping leave only stablecoin dust: -0.000002 USDC, +0.000001 USDC and -0.000001 USDT across the relevant transactions; this dust is excluded from the rounded ETH PnL table.

These figures cover only the five specified successful transactions. They exclude infrastructure expense and any other transactions, including failed attempts. They are not the operators' full-period business profit. Existing scanner files were not modified.
