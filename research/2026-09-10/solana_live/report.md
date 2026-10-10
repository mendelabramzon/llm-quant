# Solana mainnet live scan: 2026-09-10T16:55:43+00:00 to 2026-09-10T17:55:43+00:00 UTC

Slots 445934657 to 445945992 (11336 produced blocks of 11336 slots, 0 skipped, 1159 analyzed — INCOMPLETE COLLECTION), 1,401,583 transactions of which 781,061 votes and 620,522 non-vote (177,216 failed, 28.6%). SOL in-window swap price: first 99.5594, last 99.6479, median 99.5939 (min 99.5226, max 99.6479) from 174 swaps; Jupiter head price $99.99 at slot 445946425. Generated 2026-09-10T18:08:21+00:00 UTC by `scripts/solana_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

_No insights.md yet — narrative pending._

---

## Change since the previous Solana window

Previous: `research/2026-09-07/solana_live` (2026-09-07T13:19:41+00:00 to 2026-09-07T14:19:41+00:00). Current: `research/2026-09-10/solana_live` (2026-09-10T16:55:43+00:00 to 2026-09-10T17:55:43+00:00). Deterministic, from the two `analysis.json` files; deltas are relative to the previous window.

| metric | previous | current | change |
|---|---:|---:|---:|
| non-vote TPS | 1776 | 1682 | -5% |
| failed share of non-vote txs | 29.8% | 28.6% | -4% |
| non-vote fees | 268.9 | 25.0 | -91% |
| priority fees | 233.1 | 21.4 | -91% |
| fees paid by failed txs | 64.9 | 5.5 | -91% |
| Jito tips paid (successful txs) | 36.4 | 3.9 | -89% |
| swap share of non-vote txs | 16.1% | 16.2% | +1% |
| transfer share of non-vote txs | 9.1% | 8.4% | -8% |
| priced DEX volume | $205,189,806 | $20,552,771 | -90% |
| PumpSwap volume | $144,520,881 | $15,089,549 | -90% |
| self-matched (wash) volume | $86,773,770 | $6,328,565 | -93% |
| wash share of priced volume | 42.3% | 30.8% | -27% |
| sandwich patterns in pump pools | 757 | 128 | -83% |
| token launches | 1,750 | 225 | -87% |
| unique launch creators | 804 | 151 | -81% |
| pump.fun bonding-curve turnover | 41235.9 | 3782.5 | -91% |
| pump.fun cashback paid | 695.0 | 112.2 | -84% |
| PumpSwap pools created | 222 | 16 | -93% |
| liquidations (all venues) | 0 | 0 | – |
| failed Kamino flash loans | 2,384 | 30 | -99% |
| USDC net issuance | $-4,867,596 | $-89,718 | +98% |
| CCTP out | $2,381,901 | $89,718 | -96% |
| CCTP in | $2,330,602 | $0 | -100% |
| Binance net flow | $5,770,838 | $19,317,641 | +235% |
| SOL price (in-window median) | $105 | $100 | -5% |
| block producers | 446 | 146 | -67% |
| skipped slots | 8 | 0 | -100% |

**Programs entering the top 40 by transactions:** B88w…6kGH (?, 18,010 txs); FoaF…aseZ (?, 7,074 txs); 7obt…THFQ (?, 6,584 txs); HVi6…zt7H (?, 4,607 txs); oraf…cwiD (?, 4,377 txs); MAyh…MD4e (?, 3,194 txs); Live…hu9j (?, 3,182 txs); proV…CX3u (?, 3,143 txs); SPL Token (system, 3,056 txs).

**Programs leaving the top 40:** NA24…HTUV (101,067 txs last time); pump.fun sniper program (99% failed buys, 4 payers) (81,780 txs last time); unlabelled bot program (26 accounts, pump.fun Sell/GetFees inner calls, 3 payers) (76,629 txs last time); 6MWV…QEGh (75,388 txs last time); BYdq…vZtw (46,769 txs last time); 3QUn…EUoN (40,802 txs last time); BinaryFi (38,911 txs last time); Meteora DLMM (36,228 txs last time); naeb…2yCV (35,784 txs last time).

**Programs whose transaction count moved by 50% or more:** arbitrage bot program (logs "No arb opportunity found"; 1 payer) 137,824 → 6,585 (-95%); System Program 205,018 → 11,173 (-95%); Pump.fun 78,243 → 4,638 (-94%); SoLS…AVk4 49,728 → 3,253 (-93%); Meteora DAMM v2 82,605 → 5,508 (-93%); DDsn…AMEo 52,953 → 3,625 (-93%); deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) 45,788 → 3,406 (-93%); pump.fun sniper program (94% failed, 4 payers) 139,654 → 10,395 (-93%); 3RWL…v3eX 68,028 → 5,160 (-92%); Db8h…BEwH 36,396 → 2,999 (-92%); Jupiter Aggregator v6 328,366 → 27,849 (-92%); Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates 362,138 → 31,852 (-91%).

| named actors (top 10) | previous | current | still present |
|---|---:|---:|---|
| wash tokens | 10 | 10 | none |
| fan in hubs | 10 | 10 | 7uTT…i8pZ |
| distributors | 10 | 5 | BwWK…de6s, F7p3…gmNe |
| top payers | 10 | 10 | FVnv…pwMg, 83TS…ZgKC, sp1n…3xpX, FTp1…Er5f, 7TRG…qkKE, AjkD…qu4b |
| top fee payers | 10 | 10 | AgmL…zN51, 5SSQ…v4BZ |
| launch creators | 10 | 10 | Asi5…3aQs, bwam…fSXa |
| dust senders | 7 | 7 | 6uqx…XSPy |
| top pairs | 10 | 10 | none |

---

## Detector sweep (`solana_detect.py detect`): research/2026-09-10/solana_live

| detector | hits | error |
|---|---:|---|
| sol_wash_volume | 2 |  |
| sol_quote_poster | 0 |  |
| sol_failure_spam | 0 |  |
| sol_collector_hub | 0 |  |
| sol_launch_factory | 1 |  |
| sol_flash_loan_spam | 0 |  |
| sol_liquidation_drought | 1 |  |
| sol_exchange_flow | 2 |  |
| sol_cctp_unknown_domain | 1 |  |
| sol_dust_poisoning | 1 |  |
| sol_large_move | 4 |  |
| sol_lst_nav_basis | 0 |  |
| sol_stable_rate_gap | 2 |  |

## notable (4)

- `sol_wash_volume:all` $6,328,565 of $20,552,771 priced DEX volume (31%) is self-matched in 7,489 swaps by 2,889 wallet pairs
- `sol_wash_volume:venue:Pump.fun Amm` Pump.fun Amm: $6,328,561 (42% of its priced volume) self-matched in 7,485 swaps; top washed tokens BxrC…fL97 $1.8M
- `sol_stable_rate_gap:USDT:Kamino JLP/Save main` USDT pays 2.53pp more on Kamino JLP (4.39%, $1,859,279) than Save main (1.86%, $5,148,730)
- `sol_stable_rate_gap:PYUSD:Kamino JLP/Kamino SOL/BTC` PYUSD pays 2.55pp more on Kamino JLP (4.50%, $1,399,456) than Kamino SOL/BTC (1.96%, $40,434,072)

## info (10)

- `sol_exchange_flow:Coinbase 3` Coinbase 3 net +$20,756,722 over 68 txs (USDC +20.8M, SOL -0.0M, PYUSD +0.0M, EURC +0.0M)
- `sol_large_move:3ADzk5YDP9sgorvPSs9YPxigJiSqhgddpwHwwPwmEFib` 3ADz…EFib sent $19,614,838 USDT in one tx — Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance)
- `sol_large_move:5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9` 5tzF…uAi9 received $19,614,838 USDT in one tx — Binance
- `sol_exchange_flow:Binance` Binance net +$19,317,641 over 100 txs (USDT +19.6M, USD1 -0.2M, PENGU -0.1M, RAY -0.0M)
- `sol_large_move:GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE` GJRs…7npE received $18,894,647 USDC in one tx — Coinbase 3
- `sol_large_move:BjYtrpedqFgveTy8u55fYadfhcepwMtneJQL9SkK6ZmU` BjYt…6ZmU sent $18,894,647 USDC in one tx
- `sol_cctp_unknown_domain:out:domain 27` CCTP out to unmapped domain 27: $3,021 in 3 transfers
- `sol_launch_factory:all` 225 token launches by 151 creators; top 3 creators [7, 6, 5]
- `sol_liquidation_drought:all` 0 liquidations on any lending venue; 69 failed attempts (marginfi v2 69)
- `sol_dust_poisoning:6uqxgxbsVJWLWJfKipEJ5n21Jq51nYba9aVSjnEdXSPy` 6uqx…XSPy: 1,141 dust transfers to 323 recipients

---

## A. Network: throughput, fees, compute, leaders

| metric | value |
|---|---|
| transactions per second (all / non-vote) | 3798 / 1682 |
| failed non-vote transactions | 177,216 (28.6%) |
| fees paid by non-vote txs | 25.0 SOL (base 3.5 + priority 21.4); vote fees 3.9 SOL |
| fees paid by failed txs | 5.5 SOL |
| Jito tips (successful txs only; a failed tx reverts its tip) | 3.9 SOL in 33,325 tipping txs (2,214 unique tippers) |
| fee per non-vote tx (median / p90 / p99) | 5324 / 35000 / 410000 lamports |
| compute-unit price (median / p90 / p99, txs setting one) | 25000 / 1000000 / 20000000 µlamports (435,087 txs) |
| largest block by non-vote compute units | 68,078,513 |
| versioned (v0, lookup-table) tx share | 69.1% |
| Token-2022 share of token instructions | 24.4% |
| accounts created / token accounts closed | 266,892 / 249,238 |
| durable-nonce txs | 51,991 |


Per 5 minutes (SOL price = in-window swap median at the bin start):

| start | blocks | tx | non-vote | failed | fees SOL | tips SOL | CU (M) | swaps | DEX volume | of which self-matched | SOL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16:55 | 950 | 1,142,528 | 502,866 | 28% | 20.4 | 3.1 | 29491 | 83154 | $17.1M | $5.2M | $99.56 |
| 17:00 | 209 | 259,055 | 117,656 | 30% | 4.6 | 0.8 | 6303 | 17621 | $3.5M | $1.1M | $99.60 |


Leaders: 146 validators produced blocks. Most blocks: Fd7b…69Nk (55), HEL1…e2TU (40), CAo1…Sve4 (36), JUPi…1h4b (36), DRpb…21hy (32), E1r4…dxHL (24), C8Be…JP1k (24), 9jxg…nGFP (23). Skipped slots by leader: none. Most Jito tips collected: SWiz…2cov (0.4 SOL), krak…hXV1 (0.2 SOL), 9eGr…8FoY (0.2 SOL), HEL1…e2TU (0.2 SOL), JD54…HybB (0.2 SOL), EXck…nDMm (0.2 SOL).


Jito tip accounts (behavioural check — many unique payers confirms the label):

| tip account | tips SOL | unique payers |
|---|---|---|
| HFqU…7gRe | 0.61 | 656 |
| 3AVi…Z6jT | 0.53 | 646 |
| Cw8C…vLkY | 0.53 | 644 |
| 96gY…rZU5 | 0.52 | 676 |
| DttW…2KRL | 0.51 | 698 |
| ADuU…DcEt | 0.46 | 634 |
| ADaU…aS49 | 0.41 | 646 |
| DfXy…DXjh | 0.34 | 655 |


Top tippers:

| payer | label | tips SOL | tip txs |
|---|---|---|---|
| HM4G…pdMZ |  | 0.200 | 40 |
| ASsK…9eEG |  | 0.188 | 21 |
| GXRN…FWMy |  | 0.150 | 5 |
| 6FWh…j5EW |  | 0.150 | 5 |
| 5MtJ…RJaP |  | 0.104 | 31 |
| 9EwQ…qDj4 |  | 0.097 | 1 |
| 7jD9…exEa |  | 0.090 | 3 |
| 4k8m…uVGX |  | 0.085 | 22 |
| 7MYH…W24T |  | 0.075 | 5 |
| CEn4…jyCQ |  | 0.060 | 12 |
| BGT8…C9fV |  | 0.058 | 26 |
| ASZN…CTeg |  | 0.057 | 20 |
| 75am…pwHP |  | 0.056 | 25 |
| BCoR…mnct |  | 0.051 | 29 |
| 2CQg…ctFG |  | 0.051 | 1 |


## B. Programs and transaction kinds

Transaction kinds (payer-centric classification: `swap` = a DEX/aggregator program with a sold and a bought leg; `pump_launch` = pump.fun `create`; `transfer` = only system/token programs with balances moving):

| kind | txs | share | fees SOL |
|---|---|---|---|
| failed | 177,216 | 28.6% | 5.53 |
| dex_other | 156,807 | 25.3% | 2.17 |
| other | 123,031 | 19.8% | 1.91 |
| swap | 100,775 | 16.2% | 13.97 |
| transfer | 51,988 | 8.4% | 1.01 |
| prediction | 7,434 | 1.2% | 0.04 |
| system_only | 2,096 | 0.3% | 0.24 |
| perps | 604 | 0.1% | 0.01 |
| launch | 225 | 0.0% | 0.06 |
| lending | 154 | 0.0% | 0.00 |
| staking | 89 | 0.0% | 0.00 |
| protocol | 83 | 0.0% | 0.00 |
| cctp | 20 | 0.0% | 0.00 |


Top programs by transactions (main program = first non-system top-level program). `payers` = unique fee payers and the share of the top one — a program with one or two payers is a private bot; `tokens move` = share of its txs where any token balance changes (near zero = quote posting / opportunity checks, not trades); instruction names from Anchor logs when the tx has one main program:

| program | label | txs | failed | swaps | payers (top share) | tokens move | avg CU | avg keys | nonce txs | fees SOL | tips SOL | top instructions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pAMM…fXEA | Pump.fun Amm | 144,324 | 11% | 61,913 | 39975 (0%) | 89% | 98,404 | 25 | 163 | 2.07 | 0.13 | GetFeesWithQuoteMint 140844, TransferChecked 107047, Sell 78890 |
| Etrn…jWih | Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates | 31,852 | 24% | 0 | 81 (36%) | 0% | 53,869 | 7 | 3,049 | 0.17 | 0.00 |  |
| Comp…1111 | Compute Budget | 30,674 | 1% | 0 | 11606 (10%) | 29% | 9,854 | 7 | 1 | 0.82 | 0.87 |  |
| JUP6…TaV4 | Jupiter Aggregator v6 | 27,849 | 62% | 6,196 | 3499 (11%) | 38% | 146,297 | 32 | 7,744 | 1.15 | 0.03 | RouteV2 9555, Route 8800, TransferChecked 7447 |
| 9H6t…q6Rp | HumidiFi | 21,750 | 25% | 0 | 24 (11%) | 0% | 375 | 5 | 0 | 0.15 | 0.00 |  |
| Tess…GLQH | TesseraV | 21,118 | 36% | 0 | 1 (100%) | 0% | 448 | 4 | 0 | 0.11 | 0.00 |  |
| B88w…6kGH |  | 18,010 | 100% | 0 | 2 (50%) | 0% | 9,230 | 52 | 49 | 0.19 | 0.00 | InitializeAccount3 49 |
| Pris…F7qv | copychain.cc copy-trading bot program | 12,677 | 73% | 0 | 10 (35%) | 0% | 65,472 | 52 | 6,223 | 0.08 | 0.01 | GetAccountDataSize 268, InitializeAccount3 268, InitializeImmutableOwner 268 |
| QuaN…bBDv | Quantum | 12,475 | 1% | 0 | 6 (27%) | 0% | 592 | 5 | 0 | 0.08 | 0.00 |  |
| ojh1…orch | Scorch | 11,988 | 50% | 0 | 1 (100%) | 0% | 811 | 5 | 0 | 0.09 | 0.00 |  |
| 1111…1111 | System Program | 11,173 | 0% | 0 | 2305 (24%) | 6% | 4,065 | 6 | 2,137 | 0.18 | 0.39 |  |
| BiSo…Uypi | BisonFi | 10,804 | 27% | 0 | 3 (43%) | 0% | 458 | 7 | 0 | 0.06 | 0.00 |  |
| Dhpy…84HY | pump.fun sniper program (94% failed, 4 payers) | 10,395 | 94% | 0 | 4 (25%) | 0% | 4,590 | 60 | 0 | 0.13 | 0.00 | CloseAccount 23, CloseLookupTable 23, ExtendLookupTable 16 |
| W1LD…1bWR | unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers) | 10,311 | 30% | 0 | 21 (8%) | 0% | 394 | 5 | 781 | 0.05 | 0.00 |  |
| dijk…1mBu | unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer) | 9,766 | 0% | 0 | 1 (100%) | 0% | 522 | 6 | 6,490 | 0.05 | 0.00 |  |
| dbci…MaqN | Dynamic Bonding Curve | 8,048 | 44% | 4,376 | 882 (1%) | 56% | 48,111 | 17 | 0 | 0.09 | 0.00 | Swap2 7811, TransferChecked 6555, InitializeAccount3 650 |
| 2DNb…Ksbh | BisonFi Predict | 7,740 | 6% | 0 | 2 (100%) | 0% | 673 | 4 | 0 | 0.04 | 0.00 | GetAccountDataSize 9, InitializeAccount3 9, InitializeImmutableOwner 9 |
| FLAS…txB9 | pump.fun trading bot program (Sell/GetFees inner calls) | 7,378 | 6% | 6,155 | 2047 (3%) | 94% | 107,320 | 36 | 312 | 2.27 | 0.00 | TransferChecked 6764, GetFeesWithQuoteMint 4116, Sell 2074 |
| FoaF…aseZ |  | 7,074 | 0% | 0 | 1 (100%) | 0% | 45,539 | 50 | 0 | 0.09 | 0.00 | Swap 3, TransferChecked 2, GetFeesWithQuoteMint 1 |
| Arch…PMhy | Archer | 6,700 | 3% | 0 | 2 (65%) | 0% | 4,263 | 8 | 0 | 0.04 | 0.00 |  |
| 9L1q…qqDF | arbitrage bot program (logs "No arb opportunity found"; 1 payer) | 6,585 | 5% | 0 | 1 (100%) | 0% | 22,221 | 62 | 349 | 0.04 | 0.01 | TransferChecked 11, Swap2 11, GetFeesWithQuoteMint 5 |
| 7obt…THFQ |  | 6,584 | 95% | 3 | 1 (100%) | 3% | 76,537 | 34 | 6,419 | 0.14 | 0.01 | Swap 3508, GetAccountDataSize 3315, InitializeAccount3 3315 |
| BevF…56A3 |  | 5,697 | 100% | 0 | 4 (25%) | 0% | 1,561 | 57 | 16 | 0.08 | 0.00 | InitializeAccount3 16 |
| cpam…1sGG | Meteora DAMM v2 | 5,508 | 33% | 3,348 | 721 (1%) | 67% | 34,782 | 16 | 90 | 0.12 | 0.02 | TransferChecked 3566, Swap 3011, Swap2 2383 |
| 3RWL…v3eX |  | 5,160 | 100% | 0 | 4 (32%) | 0% | 1,653 | 57 | 18 | 0.05 | 0.00 | InitializeAccount3 18 |
| ATok…8knL | Associated Token Account | 5,081 | 10% | 0 | 244 (26%) | 85% | 78,656 | 14 | 0 | 0.08 | 0.00 |  |
| DF1o…7QBH |  | 4,962 | 4% | 4,149 | 909 (59%) | 96% | 232,302 | 40 | 0 | 1.67 | 0.01 | Swap 3945, TransferChecked 3173, Swap2 1464 |
| 6EF8…wF6P | Pump.fun | 4,638 | 13% | 3,396 | 938 (4%) | 82% | 74,281 | 22 | 1,258 | 4.21 | 0.39 | GetFeesWithQuoteMint 3962, TransferChecked 3479, InitializeAccount3 1641 |
| HVi6…zt7H |  | 4,607 | 0% | 0 | 1 (100%) | 0% | 53,242 | 57 | 0 | 0.03 | 0.00 | TransferChecked 7, GetFeesWithQuoteMint 7, Sell 5 |
| Toke…xuEb | Token-2022 | 4,492 | 10% | 0 | 1731 (16%) | 12% | 7,275 | 11 | 0 | 0.10 | 0.00 |  |
| oraf…cwiD |  | 4,377 | 0% | 0 | 1 (100%) | 0% | 568 | 4 | 0 | 0.02 | 0.00 |  |
| DZNT…tJbY |  | 3,941 | 20% | 0 | 1 (100%) | 0% | 413 | 7 | 0 | 0.02 | 0.00 |  |
| DDsn…AMEo |  | 3,625 | 25% | 1 | 2 (95%) | 2% | 123,161 | 56 | 185 | 0.09 | 0.02 | TransferChecked 54, Swap 50, GetFeesWithQuoteMint 38 |
| 99vQ…SrN2 | deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) | 3,406 | 0% | 0 | 487 (75%) | 84% | 27,472 | 11 | 0 | 0.18 | 0.00 | DepositToken 2876, DepositNative 528, TransferChecked 62 |
| SoLS…AVk4 |  | 3,253 | 23% | 0 | 1 (100%) | 1% | 123,204 | 56 | 0 | 0.08 | 0.02 | Swap 20, TransferChecked 19, GetFeesWithQuoteMint 19 |
| MAyh…MD4e |  | 3,194 | 1% | 0 | 1 (100%) | 99% | 126,306 | 25 | 0 | 0.14 | 0.00 | TransferChecked 3167, GetFeesWithQuoteMint 2612, Sell 1347 |
| Live…hu9j |  | 3,182 | 59% | 0 | 4 (42%) | 41% | 115,481 | 33 | 0 | 0.02 | 0.00 | TransferChecked 2690, GetFeesWithQuoteMint 2237, Swap 1825 |
| proV…CX3u |  | 3,143 | 8% | 2,404 | 633 (7%) | 92% | 223,999 | 37 | 52 | 0.24 | 0.01 | SwapTob 845, TransferChecked 833, SwapTobV3 823 |
| Toke…Q5DA | SPL Token | 3,056 | 1% | 0 | 555 (8%) | 81% | 6,289 | 11 | 0 | 0.09 | 0.00 |  |
| Db8h…BEwH |  | 2,999 | 100% | 0 | 1 (100%) | 0% | 1,359 | 48 | 0 | 0.02 | 0.00 |  |


Token launches (a new mint initialised inside a launchpad transaction): 225 in the window by 151 creators — Pump.fun 150, Raydium Launchlab 39, Dynamic Bonding Curve 29, unlabelled launchpad (new mints + trades, tied to bundler wallet 6pSPqc…) 5, T1TA…XvGT 2. New mints outside launchpads (CLMM position NFTs, LP tokens, other): Token-2022 mint churn bot (InitializeMint2 + close cycles, 1 payer, zero priority) 888, prediction market (outcome tokens, BurnWorthlessOutcome) 30, Whirlpool 22, Meteora DAMM v2 18, Raydium CLMM 15, Pump.fun Amm 13.


`other` (no DEX, lending, bridge or transfer signature) is dominated by: Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates 24,098, unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer) 9,766, unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers) 7,268, FoaF…aseZ 7,070, arbitrage bot program (logs "No arb opportunity found"; 1 payer) 6,224, HVi6…zt7H 4,597, oraf…cwiD 4,377, deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) 3,393. `dex_other` (a DEX program is invoked but no trader has a sold and a bought leg — quote posts, fee collection, failed-in-effect routes): Pump.fun Amm 66,155, HumidiFi 16,209, TesseraV 13,443, Quantum 12,377, BisonFi 7,900, Archer 6,483, Scorch 5,978, Jupiter Aggregator v6 4,292.


Top payers by transactions (bots):

| payer | label | txs | failed | fees SOL | tips SOL |
|---|---|---|---|---|---|
| FVnv…pwMg |  | 21,118 | 7675 | 0.11 | 0.00 |
| 83TS…ZgKC |  | 13,591 | 6010 | 0.12 | 0.01 |
| sp1n…3xpX |  | 11,443 | 2994 | 0.06 | 0.00 |
| FTp1…Er5f |  | 9,766 | 0 | 0.05 | 0.00 |
| 6x2c…b2jM |  | 9,073 | 8992 | 0.10 | 0.00 |
| BFju…XGAV |  | 9,001 | 8969 | 0.09 | 0.00 |
| 7TRG…qkKE |  | 7,705 | 472 | 0.04 | 0.00 |
| CzYQ…Lvyr |  | 7,077 | 0 | 0.09 | 0.00 |
| R32x…3kjk |  | 6,590 | 6251 | 0.14 | 0.01 |
| AjkD…qu4b |  | 6,587 | 349 | 0.04 | 0.01 |
| stnk…aAKr |  | 6,307 | 988 | 0.03 | 0.00 |
| AgmL…zN51 |  | 6,183 | 28 | 1.67 | 0.00 |
| BKNA…aaGg |  | 5,492 | 0 | 0.06 | 0.00 |
| EibQ…89Yj |  | 4,831 | 3542 | 0.02 | 0.00 |
| AXmn…V666 |  | 4,609 | 0 | 0.03 | 0.00 |
| Gs7a…aj6y |  | 4,592 | 1824 | 0.03 | 0.00 |
| ADGh…JiLQ |  | 4,418 | 3849 | 0.02 | 0.00 |
| TerR…6kT5 |  | 4,377 | 0 | 0.02 | 0.00 |
| GLKC…aBdK |  | 4,328 | 56 | 0.02 | 0.00 |
| FfAJ…MG9t |  | 4,327 | 1659 | 0.09 | 0.02 |


Top payers by fees + tips:

| payer | label | txs | failed | fees SOL | tips SOL |
|---|---|---|---|---|---|
| AgmL…zN51 |  | 6,183 | 28 | 1.67 | 0.00 |
| 6FWh…j5EW |  | 45 | 26 | 0.40 | 0.15 |
| GXRN…FWMy |  | 45 | 26 | 0.40 | 0.15 |
| 7jD9…exEa |  | 43 | 24 | 0.39 | 0.09 |
| FNvL…x4bs |  | 34 | 0 | 0.43 | 0.00 |
| 5SSQ…v4BZ |  | 13 | 0 | 0.40 | 0.00 |
| DAkn…U3VB |  | 1 | 1 | 0.40 | 0.00 |
| ELPm…Kif9 |  | 4 | 0 | 0.36 | 0.00 |
| DB6q…TShf |  | 15 | 0 | 0.35 | 0.00 |
| bwam…fSXa |  | 40 | 14 | 0.29 | 0.00 |
| 57st…4DyZ |  | 21 | 2 | 0.24 | 0.00 |
| 2VTg…KZRF |  | 12 | 0 | 0.20 | 0.00 |
| HM4G…pdMZ |  | 43 | 0 | 0.00 | 0.20 |
| 2CQg…ctFG |  | 15 | 10 | 0.15 | 0.05 |
| F5uf…wL2D |  | 9 | 2 | 0.20 | 0.00 |
| ASsK…9eEG |  | 29 | 0 | 0.00 | 0.19 |
| AaAh…8Hj7 |  | 3 | 0 | 0.18 | 0.00 |
| 4DvE…Gc39 |  | 12 | 0 | 0.18 | 0.00 |
| REDB…rMVt |  | 52 | 2 | 0.13 | 0.04 |
| F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 2,984 | 0 | 0.17 | 0.00 |


## C. DEX: volume by venue, pairs, implied prices, largest swaps, sandwiches, launches

Priced volume $20.6M over 100,116 swaps (659 swaps between unpriced tokens are excluded). Volume = the larger priced leg of the payer; a swap that touches several venues is attributed to `multi`.

| venue | volume | swaps | unpriced swaps |
|---|---|---|---|
| Pump.fun Amm | $15.1M | 64,332 | 43 |
| Raydium CLMM | $855k | 1,130 | 89 |
| BisonFi | $459k | 1,183 | 1 |
| aggregator-only | $453k | 14,409 | 148 |
| Whirlpool | $416k | 774 | 2 |
| Quantum | $311k | 893 | 0 |
| Meteora DLMM | $290k | 1,956 | 4 |
| multi: Manifest+Whirlpool | $228k | 18 | 0 |
| multi: GoonFi V2+Manifest | $153k | 10 | 0 |
| HumidiFi | $121k | 168 | 0 |
| multi: AlphaQ+GoonFi V2+Manifest+Raydium CLMM | $100k | 2 | 0 |
| multi: Meteora DLMM+Raydium CP | $65k | 773 | 4 |
| TesseraV | $57k | 193 | 0 |
| Meteora DAMM v2 | $57k | 3,460 | 121 |
| multi: Raydium+Raydium CLMM+Raydium CP | $56k | 888 | 0 |
| multi: Raydium+Raydium CLMM | $56k | 754 | 0 |
| Raydium CP | $51k | 221 | 70 |
| multi: Manifest+Raydium CLMM | $51k | 18 | 0 |
| multi: TesseraV+Whirlpool | $51k | 15 | 0 |
| Raydium | $50k | 835 | 3 |
| multi: AlphaQ+BisonFi+GoonFi V2+Manifest | $50k | 1 | 0 |
| multi: BisonFi+HumidiFi+Quantum+TesseraV | $50k | 1 | 0 |
| multi: GoonFi V2+HumidiFi+ZeroFi | $50k | 1 | 0 |
| multi: GoonFi V2+HumidiFi+TesseraV | $47k | 1 | 0 |
| SolFi V2 | $43k | 86 | 0 |


Volume routed through aggregators (counted once per swap, overlapping with the venue table): Jupiter Aggregator v6 $2.0M


Self-matched swaps (one transaction, two signers: the second signer's token and native-SOL legs mirror the trader's — a buy and a sell of the same token by the same operator inside one transaction, i.e. wash volume): $6.3M over 7,489 swaps from 2,889 wallet pairs, 30.8% of all priced volume.

| venue | self-matched volume | swaps | share of venue volume |
|---|---|---|---|
| Pump.fun Amm | $6.3M | 7,485 | 42% |
| multi: AlphaQ+HumidiFi+Whirlpool | $2.00 | 1 | 1% |
| multi: BisonFi+Whirlpool | $1.00 | 1 | 0% |
| Meteora DLMM | $1.00 | 1 | 0% |
| multi: GoonFi V2+Pump.fun Amm+Whirlpool | $1.00 | 1 | 0% |


| token | self-matched volume | swaps |
|---|---|---|
| BxrC…fL97 | $1.8M | 1,387 |
| E1kX…22hZ | $789k | 976 |
| 8odg…Zf5K | $690k | 705 |
| 9Uyd…DsAS | $673k | 687 |
| 2JsU…YvKd | $640k | 672 |
| 5cAf…ADex | $430k | 491 |
| CJjs…fCJu | $417k | 903 |
| 78Gy…Yied | $319k | 598 |
| Cxvx…1nxh | $214k | 289 |
| FzGW…uF8R | $202k | 359 |
| FwZm…ymZ4 | $128k | 134 |
| 9Lrk…DVvN | $67k | 284 |


Top pairs:

| venue | pair | volume | swaps |
|---|---|---|---|
| Pump.fun Amm | BxrC…fL97 / SOL | $2.1M | 1901 |
| Pump.fun Amm | E1kX…22hZ / SOL | $789k | 979 |
| Pump.fun Amm | 4ECo…ruNZ / SOL | $751k | 2789 |
| Pump.fun Amm | 8odg…Zf5K / SOL | $690k | 706 |
| Pump.fun Amm | 9Uyd…DsAS / SOL | $673k | 687 |
| Pump.fun Amm | 2JsU…YvKd / SOL | $640k | 672 |
| Pump.fun Amm | 5Wqe…9WHr / SOL | $604k | 1855 |
| Pump.fun Amm | FDLy…EHH9 / SOL | $604k | 2688 |
| Pump.fun Amm | 8QEg…U3SZ / SOL | $569k | 2214 |
| Pump.fun Amm | DfpA…ACfD / SOL | $512k | 2613 |
| Pump.fun Amm | 9LSq…3UpX / SOL | $460k | 1766 |
| Pump.fun Amm | SOL / Wehs…mBRK | $441k | 2050 |
| BisonFi | SOL / USDC | $440k | 1048 |
| Pump.fun Amm | 5cAf…ADex / SOL | $430k | 492 |
| Pump.fun Amm | 7sD5…9pwL / SOL | $428k | 1458 |
| Pump.fun Amm | CJjs…fCJu / SOL | $417k | 903 |
| Pump.fun Amm | 7ETB…UGiu / SOL | $409k | 3405 |
| Pump.fun Amm | Fb8M…zFqA / SOL | $362k | 2090 |
| Pump.fun Amm | 78Gy…Yied / SOL | $319k | 600 |
| Quantum | SOL / USDC | $305k | 871 |
| Pump.fun Amm | DJZ8…bw4Q / SOL | $294k | 1465 |
| Pump.fun Amm | AMeS…kUFr / SOL | $285k | 1748 |
| Pump.fun Amm | FVmv…r3pm / SOL | $239k | 1712 |
| Pump.fun Amm | 4VCT…DebY / SOL | $235k | 939 |
| multi: Manifest+Whirlpool | USDC / USDG | $227k | 3 |
| Whirlpool | SOL / USDC | $220k | 98 |
| Pump.fun Amm | Cxvx…1nxh / SOL | $219k | 638 |
| Pump.fun Amm | FzGW…uF8R / SOL | $202k | 359 |
| Pump.fun Amm | AFH5…Cpvc / SOL | $190k | 1199 |
| Pump.fun Amm | CgTw…pump / SOL | $161k | 1150 |


Implied prices from single-pair swaps against a priced leg (median, min–max across the window):

| token | median | min | max | swaps | volume |
|---|---|---|---|---|---|
| USDC | $1.00011 | $0.0009996 | $315.8 | 3337 | $2.5M |
| ? | $1.84942e-05 | $1.714e-05 | $2.011e-05 | 1880 | $2.1M |
| SOL | $99.6018 | $0.3152 | $199.2 | 2853 | $1.7M |
| ? | $0.000800239 | $0.0007316 | $0.0009452 | 976 | $789k |
| ? | $0.000255131 | $0.000121 | $0.0006177 | 2736 | $751k |
| ? | $3.49622e-05 | $3.374e-05 | $3.607e-05 | 706 | $690k |
| ? | $1.97926e-05 | $1.941e-05 | $2.03e-05 | 687 | $673k |
| ? | $3.00252e-05 | $2.961e-05 | $3.058e-05 | 672 | $640k |
| ? | $0.000109782 | $4.673e-05 | $0.0002696 | 1813 | $604k |
| ? | $0.000149813 | $7.49e-05 | $0.0002121 | 2635 | $603k |
| ? | $0.000405599 | $0.0002413 | $0.0008028 | 2170 | $568k |
| ? | $3.20316e-05 | $1.525e-05 | $4.804e-05 | 2521 | $511k |
| ? | $0.000103336 | $6.756e-05 | $0.0001392 | 1688 | $460k |
| ? | $0.000161579 | $0.0001042 | $0.0002776 | 1985 | $440k |
| ? | $1.13847e-05 | $1.12e-05 | $1.147e-05 | 491 | $430k |
| ? | $6.11535e-05 | $4.023e-05 | $0.0001263 | 1254 | $428k |
| ? | $0.000980026 | $0.0008891 | $0.001084 | 811 | $416k |
| ? | $0.000269438 | $0.0001576 | $0.0003947 | 3179 | $405k |
| USDT | $0.999669 | $0.9711 | $1.01 | 471 | $393k |
| ? | $0.00016571 | $0.0001087 | $0.0002956 | 1994 | $361k |
| ? | $0.000178237 | $0.0001715 | $0.0001902 | 598 | $319k |
| ? | $0.000119315 | $4.724e-05 | $0.0002125 | 848 | $294k |
| ? | $0.000411081 | $0.0001791 | $0.0005002 | 1670 | $284k |
| USDG | $1.00017 | $0.9998 | $1 | 37 | $254k |
| USD1 | $0.999378 | $0.9993 | $0.9997 | 33 | $243k |
| ? | $1.34368e-05 | $1.102e-05 | $4.111e-05 | 1622 | $238k |
| ? | $0.000220021 | $6.772e-05 | $0.000389 | 908 | $235k |
| ? | $5.88226e-05 | $5.002e-05 | $7.24e-05 | 290 | $218k |
| JLP | $4.37387 | $4.371 | $4.378 | 72 | $213k |
| ? | $0.000131182 | $0.0001197 | $0.0001395 | 359 | $202k |


Largest swaps:

| time | venue | payer | sold | bought | value | tip SOL |
|---|---|---|---|---|---|---|
| 16:59:38 | multi: Manifest+Whirlpool | F7p3…gmNe | 106.7k USDC | 106.7k USDG | $107k | 0.0000 |
| 16:56:28 | multi: Manifest+Whirlpool | F7p3…gmNe | 100.0k USDC | 100.0k USDG | $100k | 0.0000 |
| 16:58:42 | Pump.fun Amm | CA2m…bkQq | raw 50688.91B 4dn8…bWGa | raw 4345116.65B BxrC…fL97, 802 SOL | $80k | 0.0000 |
| 17:00:42 | Pump.fun Amm | 5urT…qkfB | raw 9879.46B vUtW…pump | 715 SOL | $71k | 0.0000 |
| 16:55:57 | multi: TesseraV+Whirlpool | 522j…DzU1 | 50.0k USDC | 11.4k JLP | $50k | 0.0000 |
| 16:55:51 | multi: GoonFi V2+Manifest | 522j…DzU1 | 50.0k USDC | 11.4k JLP | $50k | 0.0000 |
| 16:56:03 | multi: GoonFi V2+Manifest | 522j…DzU1 | 50.0k USDC | 11.4k JLP | $50k | 0.0000 |
| 16:56:09 | multi: GoonFi V2+Manifest | 522j…DzU1 | 50.0k USDC | 11.4k JLP | $50k | 0.0000 |
| 16:58:08 | multi: Manifest+Raydium CLMM | FKNg…CEqs | 50.0k USD1 | 50.0k USDC | $50k | 0.0000 |
| 17:01:31 | multi: AlphaQ+GoonFi V2+Manifest+Raydium CLMM | 5txA…xPaB | 50.0k USD1 | 50.0k USDT | $50k | 0.0000 |
| 16:57:18 | multi: AlphaQ+GoonFi V2+Manifest+Raydium CLMM | 5txA…xPaB | 50.0k USD1 | 50.0k USDT | $50k | 0.0000 |
| 16:58:18 | multi: AlphaQ+BisonFi+GoonFi V2+Manifest | stk1…j4o5 | 500 SOL | 49.8k USDC | $50k | 0.0000 |
| 16:58:32 | multi: BisonFi+HumidiFi+Quantum+TesseraV | stk1…j4o5 | 500 SOL | 49.8k USDC | $50k | 0.0000 |
| 16:56:37 | multi: GoonFi V2+HumidiFi+ZeroFi | BtDa…p2Ym | 500 SOL | 49.8k USDC | $50k | 0.0000 |
| 17:01:01 | multi: GoonFi V2+HumidiFi+TesseraV | 4JyP…g4qG | raw 12317.28B pump…9Dfn, 0.01787 SOL | 46.9k USDC | $47k | 0.0000 |
| 16:55:52 | Whirlpool | 3dq4…oWHK | raw 17192.10B pump…9Dfn, 42.8k USDC, 0.009507 SOL | raw 1 FjQQ…4DVv | $43k | 0.0000 |
| 16:56:49 | Pump.fun Amm | 36Dh…she3 | raw 900.00B 9CEv…BAGS, 412 SOL | raw 608.83B GFuP…9qxJ | $41k | 0.0000 |
| 16:59:20 | Whirlpool | F7ZG…xoEg | 377 SOL | 37.6k USDC | $38k | 0.0000 |
| 16:59:44 | Raydium CP | Cxsq…QE5E | raw 1000000000.00B 4d5T…JCRo, 350 SOL | raw 591607.98B 2wq6…HJws | $35k | 0.0000 |
| 16:59:39 | Pump.fun Amm | 287P…7293 | raw 3088.13B 3WYc…wo73 | raw 50793.83B AMeS…kUFr, 235 SOL | $23k | 0.0000 |
| 16:57:50 | Pump.fun Amm | DDfJ…31oi | raw 6323.76B 7ice…cfda | raw 185581.62B 4avJ…9sbb, 216 SOL | $21k | 0.0000 |
| 16:59:27 | Raydium CLMM | mtu6…8cY8 | 20.1k USDC | raw 57.92M 4k6B…97Po | $20k | 0.0003 |
| 16:59:28 | Raydium CLMM | mtu6…8cY8 | raw 57.92M 4k6B…97Po | 20.1k USDC | $20k | 0.0003 |
| 16:56:21 | multi: Manifest+Whirlpool | 8Ffs…EXpo | 20.0k USDC | 20.0k USDG | $20k | 0.0000 |
| 16:55:48 | Raydium CLMM | 8Rvq…CCs5 | 18.7k USDC | raw 18.66B 59MX…uJ7q | $19k | 0.0000 |


Same-block sandwich pattern (trader A buys, another trader buys the same token through the same pool, A sells — all in one block): 128 pattern matches, of which 2 closed the token position within 10% (the true sandwich shape; the rest are coincidental buy-buy-sell sequences in busy pump pools). Confirmed-shape victim volume $1729.

| attacker | closed sandwiches | PnL (SOL+stable legs) |
|---|---|---|
| 4vWg…NAux | 1 | $0.07 |
| HYVZ…Zhu6 | 1 | $13.12 |
| 7B7v…vrma | 1 | -$1.13 |
| Fhfw…AT4A | 1 | -$26.48 |
| 4jqx…wjB2 | 1 | -$5.16 |
| 6YNF…WJec | 1 | -$41.75 |
| Gw7V…sEzK | 1 | $0.00 |
| 6Zx9…wT7F | 1 | $25.87 |
| A6Nh…WeDi | 1 | -$7.28 |
| 3N1K…AdiS | 1 | $5.17 |


| time | token | attacker | victim | victim size | front size | attacker PnL | closed | tips SOL |
|---|---|---|---|---|---|---|---|---|
| 16:58:14 | BxrC…fL97 | Fhfw…AT4A | 6mKE…n6iB | $528 | $639 | -$26.48 | yes | 0.0 |
| 17:00:30 | 8QEg…U3SZ | 6bNj…DYgt | 6TrN…eMys | $370 | $141 | $17.81 | yes | 0.0 |
| 16:55:44 | BxrC…fL97 | GbWu…DWCS | 7UMc…1Hp4 | $1320 | $1784 | -$1120 |  | 0.0 |
| 16:58:08 | BxrC…fL97 | GbWu…DWCS | DPaf…MkpS | $1178 | $1646 | -$1071 |  | 0.0 |
| 16:55:57 | BxrC…fL97 | 7UMc…1Hp4 | 65tF…JPPr | $1045 | $1295 | -$637 |  | 0.0 |
| 16:57:48 | BxrC…fL97 | CTow…jNMk | 6XNS…WvYk | $992 | $1586 | -$873 |  | 0.0 |
| 16:58:07 | Wehs…mBRK | 85b8…v1T4 | F53E…neD1 | $617 | $167 | $280 |  | 0.0 |
| 16:56:36 | 5Wqe…9WHr | 2JAn…XbkF | F7vL…uFmH | $560 | $260 | $172 |  | 0.0 |
| 17:01:16 | DJZ8…bw4Q | 9sGq…exam | 51B3…AJoD | $541 | $600 | -$322 |  | 0.0 |
| 16:59:57 | 4ECo…ruNZ | BbC3…kv1W | 6YNF…WJec | $520 | $461 | -$239 |  | 0.0 |
| 16:59:31 | 4ECo…ruNZ | 6Z3i…stc6 | FteD…iKw8 | $502 | $229 | -$61.03 |  | 0.0 |
| 16:57:33 | Fb8M…zFqA | 6Xk3…YGjz | FMHD…DXvW | $455 | $87.00 | $9.75 |  | 0.0 |


Pump.fun (bonding curve + PumpSwap AMM): ok 151502, failed 32581, launches 155, pumpswap_pools_created 16. Bonding-curve SOL turnover 3782.5 SOL (buys 2042.1, sells 1740.4); PumpSwap trader SOL legs 151512.8 SOL. Cashback claims: 842 txs, 112.20 SOL received. 104 unique launch creators; most active: K6Eh…KHnR (7), bRxH…Vbxy (6), CpGT…Gptr (5), B9un…PMQf (5), aSWC…tE39 (4). Instruction mix: Sell 91379, BuyExactQuoteIn 48101, Buy 33689, SellV2 2452, BuyExactQuoteInV2 2106, BondingCurveV3 1501, BuyExactSolIn 1245, BuyV2 896, ClaimCashback 679, SellBondingCurvePercentage 441, ClaimCashbackV2 252, CreateV2 159.


## D. Lending: rates at head, events in window


Kamino SOL/BTC Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| SOL | 4.51% | 5.97% | 89.5% | $245.2M | $219.4M |
| dSOL | 0.00% | 1.60% | 0.0% | $226.4M | $100 |
| USDC | 3.53% | 5.37% | 81.6% | $124.4M | $101.5M |
| JITOSOL | 0.00% | 1.66% | 0.6% | $94.6M | $612k |
| cbBTC | 0.00% | 0.14% | 1.8% | $57.3M | $1.1M |
| JupSOL | 0.00% | 1.69% | 1.0% | $50.0M | $506k |
| PYUSD | 1.96% | 3.06% | 85.6% | $40.4M | $34.6M |
| USDG | 4.59% | 6.05% | 92.7% | $38.9M | $36.0M |
| hSOL | 0.00% | 1.60% | 0.0% | $27.4M | $10k |
| dfdvSOL | 0.00% | 1.60% | 0.0% | $21.5M | $0.00 |
| MSOL | 0.00% | 1.82% | 2.5% | $21.3M | $536k |
| xBTC | 0.00% | 0.11% | 1.3% | $18.1M | $243k |
| vSOL | 0.00% | 1.60% | 0.0% | $16.8M | $6252 |
| USDT | 3.86% | 5.59% | 85.2% | $9.9M | $8.4M |


Kamino JLP Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| JLP | 0.00% | 0.00% | 0.0% | $44.5M | $0.00 |
| USDC | 3.63% | 4.47% | 90.7% | $20.6M | $18.7M |
| USDT | 4.39% | 5.26% | 93.0% | $1.9M | $1.7M |
| PYUSD | 4.50% | 5.38% | 93.4% | $1.4M | $1.3M |


Kamino Ethena Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| USDe | 0.00% | 0.01% | 0.0% | $267.8M | $1027 |
| PYUSD | 3.41% | 4.05% | 93.9% | $251.5M | $236.0M |


Kamino Jito Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| JITOSOL | 0.00% | 0.02% | 1.7% | $20.8M | $351k |
| SOL | 4.19% | 5.12% | 91.5% | $20.3M | $18.5M |


Save (Solend) main market (reserves with ≥ $1M supplied; rates as reported by the Save API, utilisation from reserve state):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| mSOL | 0.00% | 0.00% | 0.0% | $23.6M | $0.00 |
| USDC | 3.17% | 5.31% | 75.2% | $22.0M | $16.6M |
| bSOL | 0.00% | 0.00% | 0.0% | $21.4M | $0.00 |
| SOL | 2.93% | 5.62% | 65.8% | $19.5M | $12.8M |
| jitoSOL | 0.00% | 0.00% | 0.0% | $8.2M | $0.00 |
| USDT | 1.86% | 4.28% | 54.8% | $5.1M | $2.8M |
| SAVE…tTFt | 0.00% | 0.00% | 0.0% | $4.9M | $0.00 |
| 7Q2a…cavn | 0.00% | 0.00% | 0.0% | $2.7M | $0.00 |
| cbBTC | 0.29% | 3.09% | 11.7% | $2.5M | $289k |
| jupSOL | 0.00% | 0.00% | 0.0% | $1.6M | $0.00 |


Jupiter Lend Earn (supply rate + rewards, bps as reported):

| vault | asset | supply APY | rewards | total | total assets |
|---|---|---|---|---|---|
| jlUSDC | USDC | 3.71% | 0.39% | 4.10% | $467.5M |
| jlJupUSD | JupUSD | 4.94% | 1.00% | 5.94% | $57.1M |
| jlWSOL | WSOL | 4.03% | 0.00% | 4.03% | $19.2M |
| jlUSDT | USDT | 3.70% | 0.00% | 3.70% | $17.6M |
| jlEURC | EURC | 4.75% | 0.00% | 4.75% | $5.1M |
| jlUSDS | USDS | 4.53% | 0.00% | 4.53% | $3.8M |
| jlUSDG | USDG | 5.65% | 0.00% | 5.65% | $3.0M |


Lending events in the window (instruction discriminators matched per program):

| venue | txs | failed | events |
|---|---|---|---|
| Kamino Lend | 174 | 30 | refresh_obligation 81, refresh_reserve 80, refresh_reserves_batch 62, deposit_reserve_liquidity_and_obligation_collateral_v2 39, withdraw_obligation_collateral_and_redeem_reserve_collateral_v2 35, borrow_obligation_liquidity_v2 32, flash_repay_reserve_liquidity (failed) 30, flash_borrow_reserve_liquidity (failed) 30, repay_obligation_liquidity_v2 26, redeem_reserve_collateral 22 |
| Jupiter Lend Earn | 27 | 4 |  |
| marginfi v2 | 111 | 86 | lending_account_end_flashloan (failed) 86, lending_account_start_flashloan (failed) 86, lending_account_repay (failed) 85, lending_account_liquidate (failed) 69, lending_account_start_flashloan 25, lending_account_repay 25, lending_account_borrow 25, lending_account_end_flashloan 25, lending_account_borrow (failed) 16 |
| Save (Solend) | 6 | 0 | borrow_obligation_liquidity 1, deposit_reserve_liquidity_and_obligation_collateral 1, withdraw_obligation_collateral_and_redeem_reserve_collateral 1 |


Liquidations that succeeded: 0. Liquidation attempts (ok / failed, top payers): marginfi v2 0 / 69 (ewcj…qaEP 69). Successful flash loans: Kamino Lend 2 txs (~$0.00 principal), marginfi v2 25 txs (~$0.00 principal). Flash-loan payers (with failures): marginfi v2: ewcj…qaEP (failed) 69, 3zdX…MPL8 25, EpgG…cf6W (failed) 9, R32x…3kjk (failed) 6, 996m…1icu (failed) 1; Kamino Lend: Hz7K…r7sz (failed) 13, F1ae…esMm (failed) 5, CHjn…ehjC (failed) 5, ENY9…VbJe (failed) 5, 3Jmb…3EWh (failed) 2. Programs co-invoked in flash-loan txs: Kamino Lend: Jupiter Aggregator v6 20, Flux 12, Meteora DLMM 10, HumidiFi 10, Whirlpool 6; marginfi v2: BisonFi 29, Jupiter Aggregator v6 26, TesseraV 8, Meteora DLMM 8, HumidiFi 7.


Same asset, different venue (supply APY / borrow APY / utilisation / supplied; reserves ≥ $5M; Jupiter Lend = supply + rewards, no borrow side):

| asset | venue | supply APY | borrow APY | util | supplied |
|---|---|---|---|---|---|
| USDC | Jupiter Lend | 4.10% | – | – | $467.5M |
| USDC | Kamino JLP | 3.63% | 4.47% | 91% | $20.6M |
| USDC | Kamino SOL/BTC | 3.53% | 5.37% | 82% | $124.4M |
| USDC | Save main | 3.17% | 5.31% | 75% | $22.0M |
| USDE | Kamino Ethena | 0.00% | 0.01% | 0% | $267.8M |
| PYUSD | Kamino Ethena | 3.41% | 4.05% | 94% | $251.5M |
| PYUSD | Kamino SOL/BTC | 1.96% | 3.06% | 86% | $40.4M |
| SOL | Kamino SOL/BTC | 4.51% | 5.97% | 89% | $245.2M |
| SOL | Kamino Jito | 4.19% | 5.12% | 91% | $20.3M |
| SOL | Jupiter Lend | 4.03% | – | – | $19.2M |
| SOL | Save main | 2.93% | 5.62% | 66% | $19.5M |
| JITOSOL | Kamino SOL/BTC | 0.00% | 1.66% | 1% | $94.6M |
| JITOSOL | Kamino Jito | 0.00% | 0.02% | 2% | $20.8M |
| JITOSOL | Save main | 0.00% | 0.00% | 0% | $8.2M |
| JUPUSD | Jupiter Lend | 5.94% | – | – | $57.1M |
| JUPSOL | Kamino SOL/BTC | 0.00% | 1.69% | 1% | $50.0M |
| JLP | Kamino JLP | 0.00% | 0.00% | 0% | $44.5M |
| USDG | Kamino SOL/BTC | 4.59% | 6.05% | 93% | $38.9M |
| USDT | Kamino SOL/BTC | 3.86% | 5.59% | 85% | $9.9M |
| USDT | Jupiter Lend | 3.70% | – | – | $17.6M |
| USDT | Save main | 1.86% | 4.28% | 55% | $5.1M |
| EURC | Jupiter Lend | 4.75% | – | – | $5.1M |


## E. Stablecoins and LSTs: issuance, pegs, NAV

Mints and burns on the registry stablecoin and LST mints, split by whether the instruction ran inside a CCTP transaction (bridge) or not (issuer treasury / stake pool):

| token | issuer minted | issuer burned | CCTP minted | CCTP burned | net |
|---|---|---|---|---|---|
| USDG | 12,162 | 518,158 | 0 | 0 | -505,996 |
| USDC | 0 | 0 | 0 | 89,718 | -89,718 |
| jitoSOL | 4 | 0 | 0 | 0 | 4 |
| USDT | 0 | 0 | 0 | 0 | 0 |
| INF | 0 | 0 | 0 | 0 | 0 |


By mint authority (CCTP mints/burns carry the CCTP minter PDA as authority; issuer treasuries carry the issuer authority):

| token | side | authority | label | amount | n |
|---|---|---|---|---|---|
| USDG | burn | F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 518,158 | 1 |
| USDC | burn | CCTP tx (user burn / custody) |  | 89,718 | 15 |
| USDG | mint | 3YJL…bhxR |  | 12,162 | 2 |
| jitoSOL | mint | 6iQK…pVSS |  | 4 | 13 |
| USDT | burn | L4om…vd27 |  | 0 | 1 |
| USDC | burn | 8Xis…SHYc |  | 0 | 1 |
| USDC | burn | Bp12…Yfxh |  | 0 | 1 |
| USDC | burn | GWhs…LCM3 |  | 0 | 1 |
| USDC | burn | DB54…vLAy |  | 0 | 1 |
| INF | mint | AYhu…CGvW |  | 0 | 1 |


Largest single mints/burns:

| time | token | side | amount | authority | CCTP tx |
|---|---|---|---|---|---|
| 16:59:41 | USDG | burn | 518,158 | F7p3…gmNe |  |
| 16:59:57 | USDC | burn | 69,866 | C5GT…sKNz | yes |
| 16:55:54 | USDC | burn | 10,000 | 4ApU…ZvYL | yes |
| 16:59:25 | USDG | mint | 6,123 | 3YJL…bhxR |  |
| 16:56:54 | USDG | mint | 6,039 | 3YJL…bhxR |  |
| 16:59:05 | USDC | burn | 6,000 | 4ApU…ZvYL | yes |
| 16:58:27 | USDC | burn | 2,905 | 9DbT…m4oU | yes |
| 17:01:02 | USDC | burn | 499 | 12uY…f969 | yes |
| 16:59:54 | USDC | burn | 185 | BWb7…m2Sk | yes |
| 16:57:42 | jitoSOL | mint | 1 | 6iQK…pVSS |  |
| 16:56:41 | jitoSOL | mint | 1 | 6iQK…pVSS |  |
| 16:55:43 | jitoSOL | mint | 0 | 6iQK…pVSS |  |
| 16:56:21 | jitoSOL | mint | 0 | 6iQK…pVSS |  |
| 16:56:23 | jitoSOL | mint | 0 | 6iQK…pVSS |  |
| 16:55:54 | jitoSOL | mint | 0 | 6iQK…pVSS |  |


Stablecoin prices at head (Jupiter aggregator price; deviation from par):

| token | price | vs par | liquidity (Jupiter) |
|---|---|---|---|
| USDC | $0.9998 | -1.8 bp | $412.2M |
| USDT | $0.9995 | -4.6 bp | $41.3M |
| PYUSD | $1.0000 | +0.4 bp | $32.4M |
| USDS | $0.9999 | -0.9 bp | $1.8M |
| USD1 | $0.9992 | -7.6 bp | $23.8M |
| USDG | $1.0000 | +0.1 bp | $35.4M |
| JupUSD | $0.9998 | -1.7 bp | $19.4M |
| USDe | $0.9996 | -4.2 bp | $8.8M |
| sUSDe | $1.2412 |  | $2742 |
| EURC | $1.1616 |  | $705k |


LSTs: market price in SOL (Jupiter price / Jupiter SOL price) against the stake-pool NAV read on-chain (finalized; pools verified by owner program and account type) and against Sanctum's sol-value API. The two NAV sources disagree by ~1.9% on every pool the on-chain read covers; the on-chain value is authoritative and the Sanctum column is kept only to document the discrepancy:

| LST | NAV on-chain (SOL) | market vs on-chain | Sanctum sol-value | market vs Sanctum | market (SOL) | liquidity |
|---|---|---|---|---|---|---|
| jitoSOL | 1.30057 | -0.5 bp | 1.27587 | +193.1 bp | 1.30051 | $1.03B |
| mSOL | – | – | 1.37665 | +194.1 bp | 1.40337 | $230.2M |
| bSOL | 1.31496 | -0.5 bp | 1.29072 | +187.3 bp | 1.31490 | $91.4M |
| jupSOL | 1.20851 | -2.3 bp | 1.18394 | +205.2 bp | 1.20824 | $517.2M |
| INF | – | – | 1.40784 | +306.5 bp | 1.45099 | $191.5M |
| hSOL | – | – | 1.16206 | +225.9 bp | 1.18830 | $92.5M |
| vSOL | – | – | 1.14911 | +159.6 bp | 1.16744 | $133.0M |
| dSOL | – | – | 1.18970 | +203.8 bp | 1.21395 | $281.4M |
| bbSOL | – | – | 1.14756 | +188.9 bp | 1.16925 | $125.1M |
| sSOL | – | – | 1.19559 | -359.5 bp | 1.15261 | $42k |


LST issuance in the window (mintTo/burn on the LST mints): jitoSOL +4 −0, INF +0 −0


## F. Bridges, exchanges, large transfers, poisoning

CCTP USDC: out $90k (15 deposit-for-burn), in $0.00 (0 receive-message; v2 pays recipients out of a custody token account instead of minting — none).

| direction | chain | USDC | transfers |
|---|---|---|---|
| out | Polygon | $70k | 2 |
| out | Plume | $16k | 2 |
| out | domain 27 | $3021 | 3 |
| out | Arbitrum | $734 | 3 |
| out | HyperEVM | $65.00 | 3 |
| out | Base | $1.00 | 2 |


Largest CCTP transfers:

| time | direction | chain | USDC | payer | recipient (EVM) |
|---|---|---|---|---|---|
| 16:59:57 | out | Polygon | $70k | C5GT…sKNz | 0x28b5a0e9…cf5d |
| 16:55:54 | out | Plume | $10k | 4ApU…ZvYL | 0x28b5a0e9…cf5d |
| 16:59:05 | out | Plume | $6000 | 4ApU…ZvYL | 0x28b5a0e9…cf5d |
| 16:58:27 | out | domain 27 | $2905 | 7QeU…BZVX | 0x9adf17d3…ded2 |
| 17:01:02 | out | Arbitrum | $499 | 12uY…f969 | 0x28b5a0e9…cf5d |
| 16:59:54 | out | Arbitrum | $185 | BWb7…m2Sk | 0x28b5a0e9…cf5d |
| 16:56:26 | out | domain 27 | $58.11 | 7QeU…BZVX | 0x9adf17d3…ded2 |
| 16:58:56 | out | domain 27 | $57.92 | 7QeU…BZVX | 0x9adf17d3…ded2 |
| 17:00:02 | out | Arbitrum | $50.01 | BqBb…1MUu | 0x28b5a0e9…cf5d |
| 16:58:52 | out | Polygon | $30.85 | Cc5M…Rnfc | 0x28b5a0e9…cf5d |
| 16:59:47 | out | HyperEVM | $28.76 | 7V8b…ZYgw | 0x28b5a0e9…cf5d |
| 16:56:03 | out | HyperEVM | $25.92 | 7V8b…ZYgw | 0x28b5a0e9…cf5d |


Exchange net flow (labels from memory; the fan-in column is the behavioural check — a deposit hot wallet receives from many unique senders):

| exchange | net by asset | net USD | txs | senders | receivers | fan-in (SOL≥0.1) |
|---|---|---|---|---|---|---|
| Coinbase 3 | USDC +20.76M, SOL -37.34, PYUSD +250, EURC +60.97 | $20.8M | 68 | 24 | 34 | 0 |
| Binance | USDT +19.60M, USD1 -150.1k, PENGU -6.82M, RAY -27.9k, SOL -268 | $19.3M | 100 | 3 | 46 | 2 |
| KuCoin | USDC -12.0k, SOL -104, USDT -6516, 6AJc…pump +119.93B, 9cRC…pump -7.44B | -$29k | 37 | 1 | 16 | 6 |
| Gate.io | USDT -11.2k, SOL -55.47, JUP -4775, USDC -954, F3ne…Xs5B -1579.20B | -$19k | 17 | 0 | 1 | 0 |
| Coinbase | SOL -83.16, USDC -5295 | -$14k | 51 | 0 | 31 | 0 |
| Coinbase 2 | EURC -5481, USDC -2011, SOL -8.885, PYUSD -18, TNSR…JAS6 -32392.69B | -$9281 | 36 | 0 | 18 | 0 |
| MEXC | USDC -3689, SOL -25.64, USDT -1646, CTPo…pump -54.53B, 5UUH…hgH2 +52.11B | -$7887 | 59 | 24 | 20 | 8 |
| Bybit | SKRb…ZhW3 +4024.43B | $0.00 | 1 | 1 | 0 | 0 |


Label checks: Binance: some activity; Binance 2: no activity in window; Coinbase: some activity; Coinbase 2: some activity; Coinbase 3: some activity; Kraken: no activity in window; OKX: no activity in window; Bybit: some activity; Gate.io: some activity; KuCoin: some activity; MEXC: some activity; Crypto.com: no activity in window; Bitget: no activity in window; HTX: no activity in window


Unlabelled addresses with exchange-like fan-in (≥ 40 unique senders of ≥ 0.1 SOL):

| address | label | unique senders | transfers in | SOL in | median in | transfers out | destinations | SOL out | shape |
|---|---|---|---|---|---|---|---|---|---|
| 7uTT…i8pZ | vault of deposit router 99vQ… (largest unlabelled fan-in) | 321 | 379 | 697.2 | 0.500 | 6 | 1 | 722.2 | collector hub (many in, ≤2 out) |
| 8LLd…paQx |  | 200 | 200 | 249.7 | 0.963 | 201 | 6+ | 310.0 | mixed |
| J26w…e1Dd |  | 178 | 247 | 168.9 | 0.486 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 8YMX…Ubq7 |  | 175 | 244 | 178.8 | 0.494 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 7cRV…Rbng |  | 135 | 164 | 104.2 | 0.396 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 2M2r…JWiP |  | 130 | 155 | 133.2 | 0.622 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 2j85…QvqX |  | 116 | 148 | 78.2 | 0.348 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| F7Hx…Y49w |  | 90 | 102 | 80.8 | 0.580 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| Hj7a…Z5iq |  | 89 | 89 | 18.6 | 0.220 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 4HdA…JSsg |  | 89 | 89 | 19.2 | 0.220 | 1 | 1 | 288.8 | collector hub (many in, ≤2 out) |
| EfLV…e5KT |  | 72 | 90 | 58.2 | 0.390 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| EHnr…SMMb |  | 70 | 85 | 60.7 | 0.490 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 8Wpj…ze37 |  | 67 | 79 | 58.0 | 0.494 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| w5xW…iTgs |  | 57 | 68 | 63.5 | 0.494 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| EW9d…Bs7J | SOL sink of program T1TA…XvGT (8.8k SOL from 425 senders, no outflow) | 56 | 221 | 808.5 | 3.658 | 0 | 0 | 0.0 | deposit address (many in, little out) |


Distributors (≥ 200 outgoing SOL transfers of ≥ 0.1 SOL to ≥ 6 destinations — wallet funders, payout hubs):

| address | label | transfers out | SOL sent |
|---|---|---|---|
| AsZj…RrWd |  | 700 | 667.7 |
| Dmym…QLsn |  | 350 | 341.6 |
| BwWK…de6s |  | 312 | 89.9 |
| F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 274 | 568.4 |
| 8LLd…paQx |  | 201 | 310.0 |


Largest priced position changes (per owner and asset inside one transaction, ≥ $100k):

| time | owner | label | asset | change | value | kind | programs |
|---|---|---|---|---|---|---|---|
| 17:00:01 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDT | -19.61M | $19.6M | transfer |  |
| 17:00:01 | 5tzF…uAi9 | Binance | USDT | +19.61M | $19.6M | transfer |  |
| 17:01:02 | GJRs…7npE | Coinbase 3 | USDC | +18.89M | $18.9M | transfer |  |
| 17:01:02 | BjYt…6ZmU |  | USDC | -18.89M | $18.9M | transfer |  |
| 17:00:39 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -2.00M | $2.0M | transfer |  |
| 17:00:39 | FGvC…CjS8 |  | USDC | +2.00M | $2.0M | transfer |  |
| 16:59:32 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -2.00M | $2.0M | transfer |  |
| 16:59:32 | GcSW…F58r |  | USDC | +2.00M | $2.0M | transfer |  |
| 17:00:10 | FGvC…CjS8 |  | USDC | +2.00M | $2.0M | transfer |  |
| 17:00:10 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -2.00M | $2.0M | transfer |  |
| 17:00:22 | FGvC…CjS8 |  | USDC | +2.00M | $2.0M | transfer |  |
| 17:00:22 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -2.00M | $2.0M | transfer |  |
| 17:01:02 | AmV7…aqaf |  | USDC | -1.86M | $1.9M | transfer |  |
| 17:01:02 | GJRs…7npE | Coinbase 3 | USDC | +1.86M | $1.9M | transfer |  |
| 16:56:20 | FpwQ…E99Q |  | USDC | +1.05M | $1.1M | transfer |  |
| 16:56:20 | BRif…nNtd |  | USDC | -1.05M | $1.1M | transfer |  |
| 16:56:20 | FpwQ…E99Q |  | USDC | +916.4k | $916k | transfer |  |
| 16:55:52 | FrRq…cf4P |  | USDC | -916.4k | $916k | transfer |  |
| 16:56:20 | 5SU1…Lv45 |  | USDC | -916.4k | $916k | transfer |  |
| 16:55:52 | 5SU1…Lv45 |  | USDC | +916.4k | $916k | transfer |  |
| 17:00:41 | GcSW…F58r |  | USDC | +800.0k | $800k | transfer |  |
| 17:00:41 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -800.0k | $800k | transfer |  |
| 16:56:27 | K6M1…d2dE |  | USDT | +565.5k | $566k | transfer |  |
| 17:00:48 | 5KMY…QcFa |  | USDT | +565.5k | $566k | transfer |  |
| 17:00:48 | K6M1…d2dE |  | USDT | -565.5k | $566k | transfer |  |
| 16:56:27 | Hmc2…D4ni |  | USDT | -565.5k | $566k | transfer |  |
| 16:59:41 | F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | USDG | -518.2k | $518k | other | paxo…r1nR |
| 16:56:56 | Gem2…oTka |  | USDC | +500.0k | $500k | transfer |  |
| 16:56:56 | GgQD…V2NH |  | USDC | -500.0k | $500k | transfer |  |
| 17:00:37 | AwTx…jnfn |  | USDC | -441.0k | $441k | transfer |  |


Largest native SOL balance changes (≥ 1,000 SOL):

| time | account | label | change SOL | value | kind | payer |
|---|---|---|---|---|---|---|
| 17:01:15 | 34Ss…qnoE |  | -11088.2 | $1.1M | staking | 59L2…sG6h |
| 17:01:15 | Aeg8…YBww |  | +11088.2 | $1.1M | staking | 59L2…sG6h |
| 16:56:33 | 8pUb…wFxV |  | -3919.0 | $390k | transfer | 8pUb…wFxV |
| 16:56:33 | 2Wsc…RAon |  | +3919.0 | $390k | transfer | 8pUb…wFxV |
| 17:00:56 | 6i3j…h4QZ |  | -2800.1 | $279k | dex_other | 6i3j…h4QZ |
| 17:00:56 | EYj9…rR9o |  | +2800.0 | $279k | dex_other | 6i3j…h4QZ |
| 16:59:58 | 5g7y…aBWs |  | -1832.3 | $183k | transfer | 5g7y…aBWs |
| 16:59:58 | 8tck…bwyA |  | +1832.3 | $183k | transfer | 5g7y…aBWs |
| 16:58:29 | EwJY…i418 |  | +1818.4 | $181k | dex_other | AgmL…zN51 |
| 16:55:49 | CYWf…z65n |  | +1345.3 | $134k | transfer | MfDu…GVWa |
| 16:55:49 | CHVm…Dq8n |  | -1345.3 | $134k | transfer | MfDu…GVWa |
| 17:01:19 | CYWf…z65n |  | -1320.2 | $132k | transfer | MfDu…GVWa |
| 17:01:19 | 2bUT…wij9 |  | +1320.2 | $132k | transfer | MfDu…GVWa |
| 17:01:18 | 2i2V…SV3z |  | -1250.3 | $125k | transfer | 2i2V…SV3z |
| 17:01:18 | GmkU…7qC6 |  | +1250.3 | $125k | transfer | 2i2V…SV3z |
| 16:57:21 | BGfL…VrXn |  | -1205.3 | $120k | transfer | BGfL…VrXn |
| 16:57:21 | 8FWb…6FqE |  | +1205.3 | $120k | transfer | BGfL…VrXn |
| 16:59:43 | CmCq…Sn7a |  | -1076.7 | $107k | transfer | CmCq…Sn7a |
| 16:59:43 | 4xLp…9Qdg |  | +1076.7 | $107k | transfer | CmCq…Sn7a |


Address-poisoning style dust (≤ 1 raw token unit or ≤ 1,000 lamports sent by the payer to ≥ 20 distinct recipients): 2,094 transfers in the window from 5 senders with ≥ 50 each. Top senders (senders that dust only a handful of accounts — market-maker heartbeats — are excluded: FcEA…UVGR 1541→1, 2pde…Pthh 1194→17, YQoB…SXEQ 1021→8, sp1n…3xpX 947→8):

| sender | dust transfers | distinct recipients |
|---|---|---|
| 6uqx…XSPy | 1141 | 323 |
| CEUA…qoXJ | 426 | 25 |
| GxDH…idr7 | 240 | 240 |
| 98T6…w3Mp | 118 | 24 |
| C4ud…4psU | 84 | 24 |
| H1TL…7xYm | 48 | 21 |
| FetP…6u5J | 37 | 37 |
