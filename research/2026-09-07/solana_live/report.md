# Solana mainnet live scan: 2026-09-07T13:19:41+00:00 to 2026-09-07T14:19:41+00:00 UTC

Slots 445075051 to 445086411 (11353 produced blocks of 11361 slots, 8 skipped, 7313 analyzed — INCOMPLETE COLLECTION), 8,701,355 transactions of which 4,914,733 votes and 3,786,622 non-vote (1,065,846 failed, 28.1%). SOL in-window swap price: first 105.7612, last 105.5921, median 105.7067 (min 105.5921, max 105.7665) from 414 swaps; Jupiter head price $104.23 at slot 445089891. Generated 2026-09-07T15:42:52+00:00 UTC by `scripts/solana_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

_No insights.md yet — narrative pending._

---

## A. Network: throughput, fees, compute, leaders

| metric | value |
|---|---|
| transactions per second (all / non-vote) | 3752 / 1633 |
| failed non-vote transactions | 1,065,846 (28.1%) |
| fees paid by non-vote txs | 157.6 SOL (base 21.2 + priority 136.4); vote fees 24.8 SOL |
| fees paid by failed txs | 34.4 SOL |
| Jito tips | 31.3 SOL in 246,278 tipping txs (8,718 unique tippers) |
| fee per non-vote tx (median / p90 / p99) | 5410 / 22500 / 505000 lamports |
| compute-unit price (median / p90 / p99, txs setting one) | 15060 / 1000000 / 21600000 µlamports (2,772,021 txs) |
| largest block by non-vote compute units | 69,998,302 |
| versioned (v0, lookup-table) tx share | 68.9% |
| Token-2022 share of token instructions | 22.0% |
| accounts created / token accounts closed | 1,386,884 / 1,285,546 |
| durable-nonce txs | 394,577 |


Per 5 minutes (SOL price = in-window swap median at the bin start):

| start | blocks | tx | non-vote | failed | fees SOL | tips SOL | CU (M) | swaps | DEX volume | SOL |
|---|---|---|---|---|---|---|---|---|---|---|
| 13:19 | 949 | 1,186,705 | 550,462 | 29% | 20.3 | 5.8 | 32157 | 89623 | $15.2M | $105.76 |
| 13:24 | 943 | 1,093,791 | 459,849 | 24% | 15.3 | 3.6 | 25110 | 86730 | $15.5M | $105.74 |
| 13:29 | 949 | 1,074,825 | 436,960 | 24% | 16.4 | 2.1 | 23197 | 79211 | $16.4M | $105.71 |
| 13:34 | 943 | 1,154,112 | 520,811 | 33% | 15.9 | 3.5 | 27610 | 78688 | $17.2M | $105.59 |
| 13:39 | 952 | 1,078,052 | 437,975 | 28% | 25.8 | 4.0 | 23691 | 81208 | $16.9M | $105.71 |
| 13:44 | 939 | 1,087,152 | 456,388 | 27% | 24.6 | 5.4 | 26915 | 78494 | $16.0M | $105.71 |
| 13:49 | 952 | 1,164,945 | 524,096 | 32% | 19.5 | 3.8 | 28203 | 88415 | $16.6M | $105.71 |
| 13:54 | 686 | 861,773 | 400,081 | 28% | 19.9 | 3.1 | 23311 | 71614 | $12.3M | $105.71 |


Leaders: 374 validators produced blocks. Most blocks: HEL1…e2TU (300), Fd7b…69Nk (296), DRpb…21hy (201), JUPi…1h4b (196), E1r4…dxHL (184), CAo1…Sve4 (168), 9eGr…8FoY (164), C8Be…JP1k (148). Skipped slots by leader: SSmB…oQLY (4), xLab…1ARE (4). Most Jito tips collected: E1r4…dxHL (1.8 SOL), GnC3…qta6 (1.5 SOL), DRpb…21hy (1.4 SOL), 9eGr…8FoY (1.2 SOL), Fd7b…69Nk (1.0 SOL), FBKF…jeNi (1.0 SOL).


Jito tip accounts (behavioural check — many unique payers confirms the label):

| tip account | tips SOL | unique payers |
|---|---|---|
| Cw8C…vLkY | 4.52 | 2422 |
| 3AVi…Z6jT | 4.27 | 2462 |
| HFqU…7gRe | 4.13 | 2523 |
| DttW…2KRL | 4.08 | 2466 |
| DfXy…DXjh | 3.81 | 2498 |
| ADaU…aS49 | 3.67 | 2453 |
| 96gY…rZU5 | 3.54 | 2497 |
| ADuU…DcEt | 3.31 | 2480 |


Top tippers:

| payer | label | tips SOL | tip txs |
|---|---|---|---|
| 4pSH…ks4N |  | 2.429 | 1277 |
| free…EByC |  | 2.128 | 526 |
| 5RzV…tFX7 |  | 1.680 | 21 |
| MRiY…oCsa |  | 0.805 | 28 |
| 64fc…QzQw |  | 0.694 | 315 |
| UUAh…V8yd |  | 0.588 | 200 |
| BGT8…C9fV |  | 0.518 | 205 |
| 35Qb…G16X |  | 0.498 | 32 |
| 5MtJ…RJaP |  | 0.452 | 140 |
| 75am…pwHP |  | 0.436 | 189 |
| HQ7r…Ucg3 |  | 0.400 | 3 |
| GQv7…RuzS |  | 0.360 | 10 |
| Bh4c…jFfz |  | 0.360 | 10 |
| MfDu…GVWa |  | 0.337 | 1718 |
| ASki…yNEG |  | 0.280 | 81 |


## B. Programs and transaction kinds

Transaction kinds (payer-centric classification: `swap` = a DEX/aggregator program with a sold and a bought leg; `pump_launch` = pump.fun `create`; `transfer` = only system/token programs with balances moving):

| kind | txs | share | fees SOL |
|---|---|---|---|
| failed | 1,065,846 | 28.1% | 34.36 |
| other | 891,646 | 23.5% | 11.30 |
| dex_other | 787,343 | 20.8% | 18.18 |
| swap | 653,983 | 17.3% | 76.42 |
| transfer | 325,080 | 8.6% | 5.23 |
| prediction | 34,835 | 0.9% | 0.18 |
| system_only | 11,179 | 0.3% | 11.47 |
| staking | 10,803 | 0.3% | 0.07 |
| perps | 2,870 | 0.1% | 0.03 |
| lending | 1,464 | 0.0% | 0.02 |
| launch | 1,097 | 0.0% | 0.30 |
| protocol | 319 | 0.0% | 0.01 |
| cctp | 125 | 0.0% | 0.01 |
| bridge | 22 | 0.0% | 0.00 |
| vault | 10 | 0.0% | 0.00 |


Top programs by transactions (main program = first non-system top-level program). `payers` = unique fee payers and the share of the top one — a program with one or two payers is a private bot; `tokens move` = share of its txs where any token balance changes (near zero = quote posting / opportunity checks, not trades); instruction names from Anchor logs when the tx has one main program:

| program | label | txs | failed | swaps | payers (top share) | tokens move | avg CU | avg keys | nonce txs | fees SOL | tips SOL | top instructions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pAMM…fXEA | Pump.fun Amm | 719,207 | 11% | 409,017 | 129478 (1%) | 89% | 105,581 | 26 | 1,912 | 24.83 | 1.88 | GetFees 693327, TransferChecked 507675, Sell 418038 |
| Etrn…jWih | Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates | 242,400 | 21% | 0 | 136 (52%) | 0% | 39,869 | 7 | 15,992 | 1.27 | 0.04 |  |
| JUP6…TaV4 | Jupiter Aggregator v6 | 175,413 | 62% | 37,427 | 11760 (10%) | 38% | 140,093 | 33 | 54,292 | 8.85 | 2.35 | RouteV2 61367, Route 49704, TransferChecked 44574 |
| Comp…1111 | Compute Budget | 167,401 | 2% | 0 | 35699 (15%) | 47% | 12,426 | 7 | 49 | 14.31 | 4.57 |  |
| 9H6t…q6Rp | HumidiFi | 138,245 | 28% | 0 | 21 (11%) | 0% | 362 | 5 | 0 | 1.43 | 0.00 |  |
| Tess…GLQH | TesseraV | 126,255 | 31% | 0 | 1 (100%) | 0% | 464 | 4 | 0 | 0.67 | 0.01 |  |
| 1111…1111 | System Program | 99,165 | 1% | 0 | 34597 (5%) | 4% | 1,685 | 6 | 11,574 | 1.49 | 1.77 |  |
| Dhpy…84HY | pump.fun sniper program (94% failed, 4 payers) | 83,757 | 94% | 1 | 4 (25%) | 0% | 4,675 | 60 | 0 | 0.88 | 0.00 | ExtendLookupTable 187, CreateLookupTable 187, InitializeImmutableOwner 187 |
| 9L1q…qqDF | arbitrage bot program (logs "No arb opportunity found"; 1 payer) | 77,368 | 21% | 0 | 1 (100%) | 0% | 39,140 | 52 | 13,788 | 0.71 | 0.11 | Swap2 60, Swap 43, TransferChecked 42 |
| ojh1…orch | Scorch | 66,719 | 47% | 0 | 1 (100%) | 0% | 799 | 5 | 0 | 0.48 | 0.00 |  |
| W1LD…1bWR | unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers) | 66,342 | 20% | 0 | 24 (10%) | 0% | 385 | 5 | 6,631 | 0.34 | 0.00 |  |
| Pris…F7qv | copychain.cc copy-trading bot program | 65,870 | 51% | 0 | 6 (48%) | 0% | 50,520 | 46 | 63,143 | 0.58 | 2.55 | InitializeImmutableOwner 1289, GetAccountDataSize 1289, InitializeAccount3 1289 |
| QuaN…bBDv | Quantum | 63,057 | 0% | 0 | 6 (19%) | 0% | 621 | 5 | 0 | 0.40 | 0.02 |  |
| cpam…1sGG | Meteora DAMM v2 | 60,071 | 32% | 38,067 | 2442 (1%) | 68% | 34,937 | 16 | 726 | 1.58 | 0.71 | TransferChecked 37828, Swap 31563, Swap2 27877 |
| dijk…1mBu | unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer) | 55,419 | 0% | 0 | 1 (100%) | 0% | 522 | 6 | 36,920 | 0.28 | 0.00 |  |
| 7JwT…94ZG | pump.fun sniper program (99% failed buys, 4 payers) | 49,748 | 99% | 1 | 4 (30%) | 0% | 1,396 | 47 | 0 | 0.33 | 0.00 |  |
| NA24…HTUV |  | 49,531 | 62% | 1 | 12 (23%) | 0% | 84,656 | 47 | 41,009 | 0.65 | 0.04 | InitializeImmutableOwner 1135, GetAccountDataSize 1135, InitializeAccount3 1135 |
| Hd7c…UH5w | unlabelled bot program (26 accounts, pump.fun Sell/GetFees inner calls, 3 payers) | 46,643 | 23% | 170 | 3 (72%) | 0% | 19,911 | 27 | 4,696 | 0.23 | 0.00 | GetFees 6149, Sell 6064, TransferChecked 166 |
| 6EF8…wF6P | Pump.fun | 43,714 | 24% | 23,005 | 6991 (2%) | 59% | 61,820 | 20 | 5,751 | 21.54 | 3.39 | GetFees 26407, TransferChecked 24600, Sell 14705 |
| BiSo…Uypi | BisonFi | 42,504 | 21% | 0 | 3 (58%) | 0% | 472 | 7 | 0 | 0.27 | 0.00 |  |
| 3RWL…v3eX |  | 41,731 | 100% | 0 | 4 (25%) | 0% | 1,620 | 57 | 186 | 0.38 | 0.00 | InitializeAccount3 186 |
| BevF…56A3 |  | 41,207 | 100% | 1 | 4 (25%) | 0% | 1,589 | 57 | 188 | 0.47 | 0.00 | InitializeAccount3 188, TransferChecked 1, BuyExactSolIn 1 |
| Arch…PMhy | Archer | 37,525 | 15% | 0 | 3 (61%) | 0% | 3,124 | 7 | 0 | 0.20 | 0.00 | TransferChecked 5 |
| 2DNb…Ksbh | BisonFi Predict | 36,894 | 8% | 0 | 2 (100%) | 0% | 660 | 4 | 0 | 0.18 | 0.00 | InitializeImmutableOwner 46, GetAccountDataSize 46, InitializeAccount3 46 |
| FLAS…txB9 | pump.fun trading bot program (Sell/GetFees inner calls) | 34,835 | 5% | 30,388 | 4414 (1%) | 95% | 85,865 | 31 | 3,007 | 7.35 | 0.04 | TransferChecked 31335, GetFees 25682, Sell 12287 |
| dbci…MaqN | Dynamic Bonding Curve | 34,279 | 27% | 22,665 | 2907 (1%) | 73% | 50,944 | 17 | 118 | 0.35 | 0.01 | Swap2 32635, TransferChecked 22727, InitializeAccount3 3827 |
| 6MWV…QEGh |  | 33,743 | 0% | 0 | 3 (87%) | 0% | 42,091 | 56 | 0 | 0.36 | 0.01 | TransferChecked 15, GetFees 15, Swap2 12 |
| ATok…8knL | Associated Token Account | 31,085 | 1% | 0 | 2015 (17%) | 90% | 51,173 | 13 | 0 | 0.31 | 0.00 |  |
| 99vQ…SrN2 | deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) | 30,925 | 1% | 0 | 2347 (82%) | 88% | 25,770 | 11 | 0 | 2.01 | 0.00 | DepositToken 27472, DepositNative 3364, TransferChecked 311 |
| BYdq…vZtw |  | 30,526 | 4% | 114 | 1 (100%) | 0% | 30,696 | 41 | 0 | 0.15 | 0.00 | GetFees 114, TransferChecked 110, BuyExactQuoteIn 58 |
| DDsn…AMEo |  | 28,394 | 26% | 4 | 3 (97%) | 1% | 113,824 | 57 | 979 | 0.55 | 0.12 | Swap 191, TransferChecked 178, Swap2 101 |
| SoLS…AVk4 |  | 26,728 | 26% | 3 | 1 (100%) | 0% | 113,856 | 58 | 0 | 0.46 | 0.11 | TransferChecked 77, GetFees 57, Swap 52 |
| Db8h…BEwH |  | 26,372 | 100% | 0 | 1 (100%) | 0% | 1,359 | 48 | 0 | 0.17 | 0.00 |  |
| DF1o…7QBH |  | 24,973 | 7% | 19,007 | 3742 (53%) | 93% | 223,991 | 39 | 0 | 7.89 | 0.04 | Swap 19314, TransferChecked 15462, Swap2 7091 |
| HQLD…prfS |  | 24,656 | 80% | 12 | 1 (100%) | 0% | 6,560 | 22 | 0 | 0.25 | 0.00 | TransferChecked 31, BuyExactSolIn 31, GetFees 31 |
| B72M…Rdht | BinaryFi | 24,511 | 5% | 0 | 2 (100%) | 0% | 1,039 | 13 | 14,576 | 0.14 | 0.00 |  |
| DZNT…tJbY |  | 24,374 | 21% | 0 | 1 (100%) | 0% | 415 | 7 | 0 | 0.13 | 0.01 |  |
| 4VXz…RjWH |  | 22,095 | 100% | 0 | 1 (100%) | 0% | 7,032 | 37 | 0 | 0.16 | 0.00 |  |
| LBUZ…Pwxo | Meteora DLMM | 22,094 | 10% | 6,824 | 1798 (9%) | 82% | 216,729 | 21 | 408 | 3.62 | 0.38 | TransferChecked 5633, ClaimFee2 5053, SwapWithPriceImpact2 4823 |
| Toke…xuEb | Token-2022 | 20,715 | 3% | 0 | 10120 (9%) | 34% | 9,684 | 9 | 0 | 0.24 | 0.00 |  |


Token launches (a new mint initialised inside a launchpad transaction): 1097 in the window by 513 creators — Pump.fun 796, Dynamic Bonding Curve 178, Raydium Launchlab 88, unlabelled launchpad (new mints + trades, tied to bundler wallet 6pSPqc…) 28, T1TA…XvGT 4, 24Uq…pyTi 3. New mints outside launchpads (CLMM position NFTs, LP tokens, other): Token-2022 mint churn bot (InitializeMint2 + close cycles, 1 payer, zero priority) 1848, Pump.fun Amm 110, prediction market (outcome tokens, BurnWorthlessOutcome) 100, Whirlpool 99, Compute Budget 70, Meteora DAMM v2 54.


`other` (no DEX, lending, bridge or transfer signature) is dominated by: Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates 190,542, arbitrage bot program (logs "No arb opportunity found"; 1 payer) 60,980, unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer) 55,419, unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers) 53,104, unlabelled bot program (26 accounts, pump.fun Sell/GetFees inner calls, 3 payers) 35,891, 6MWV…QEGh 33,724, copychain.cc copy-trading bot program 32,274, deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) 30,644. `dex_other` (a DEX program is invoked but no trader has a sold and a bought leg — quote posts, fee collection, failed-in-effect routes): Pump.fun Amm 232,272, HumidiFi 99,305, TesseraV 87,265, Quantum 62,760, Scorch 35,257, BisonFi 33,462, Archer 31,939, Jupiter Aggregator v6 29,671.


Top payers by transactions (bots):

| payer | label | txs | failed | fees SOL | tips SOL |
|---|---|---|---|---|---|
| FVnv…pwMg |  | 126,255 | 38990 | 0.67 | 0.01 |
| sp1n…3xpX |  | 125,418 | 30137 | 0.63 | 0.01 |
| AjkD…qu4b |  | 77,375 | 16303 | 0.71 | 0.11 |
| 83TS…ZgKC |  | 76,148 | 31462 | 0.69 | 0.05 |
| FTp1…Er5f |  | 55,419 | 0 | 0.28 | 0.00 |
| stnk…aAKr |  | 51,547 | 9589 | 0.26 | 0.00 |
| AgmL…zN51 |  | 42,271 | 353 | 9.12 | 0.00 |
| 7TRG…qkKE |  | 36,750 | 2865 | 0.18 | 0.00 |
| CFgk…Q9WH |  | 33,605 | 3285 | 0.17 | 0.00 |
| 3276…wQS6 |  | 31,827 | 15545 | 0.28 | 0.07 |
| FfAJ…MG9t |  | 31,211 | 9001 | 0.50 | 0.12 |
| 3ct4…fh5J |  | 30,896 | 1419 | 0.15 | 0.00 |
| 8TPW…UaHr |  | 29,519 | 5 | 0.31 | 0.00 |
| A7FM…aaVE |  | 27,410 | 7358 | 0.46 | 0.12 |
| 7ovu…1Ltx |  | 26,389 | 26355 | 0.17 | 0.00 |
| F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 26,332 | 6 | 0.31 | 0.00 |
| 6AHv…H2sM |  | 24,672 | 19609 | 0.25 | 0.01 |
| HCar…c3fT |  | 24,502 | 1117 | 0.14 | 0.00 |
| Gs7a…aj6y |  | 24,441 | 6367 | 0.14 | 0.00 |
| DotU…LXMK |  | 24,374 | 5115 | 0.13 | 0.01 |


Top payers by fees + tips:

| payer | label | txs | failed | fees SOL | tips SOL |
|---|---|---|---|---|---|
| AgmL…zN51 |  | 42,271 | 353 | 9.12 | 0.00 |
| MfDu…GVWa |  | 5,734 | 2817 | 3.82 | 0.34 |
| 9EwQ…qDj4 |  | 26 | 0 | 3.55 | 0.06 |
| 9cU2…SHwX |  | 1 | 0 | 3.43 | 0.00 |
| 3rBp…9SAC |  | 1 | 0 | 3.32 | 0.00 |
| 2CQg…ctFG |  | 303 | 192 | 2.32 | 0.27 |
| 4pSH…ks4N |  | 1,277 | 1277 | 0.01 | 2.43 |
| free…EByC |  | 3,592 | 3272 | 0.06 | 2.13 |
| MRiY…oCsa |  | 729 | 409 | 1.31 | 0.81 |
| 5RzV…tFX7 |  | 21 | 1 | 0.39 | 1.68 |
| E4Ez…TKBz |  | 11 | 3 | 2.04 | 0.00 |
| D4py…thqu |  | 36 | 0 | 1.42 | 0.00 |
| gtfo…CgFL |  | 14 | 0 | 1.38 | 0.00 |
| ASoG…wLeg |  | 139 | 0 | 1.29 | 0.08 |
| 5t4T…Ds1p |  | 13 | 0 | 1.34 | 0.00 |
| 66Pb…FNjD |  | 19 | 0 | 1.33 | 0.00 |
| AQHK…5FX8 |  | 35 | 4 | 1.30 | 0.00 |
| B2zY…quK7 |  | 27 | 2 | 1.10 | 0.00 |
| 7dGr…uuUu |  | 2,082 | 1857 | 0.83 | 0.18 |
| gtag…WNdd |  | 1,403 | 1174 | 0.94 | 0.00 |


## C. DEX: volume by venue, pairs, implied prices, largest swaps, sandwiches, launches

Priced volume $126.1M over 650,502 swaps (3,481 swaps between unpriced tokens are excluded). Volume = the larger priced leg of the payer; a swap that touches several venues is attributed to `multi`.

| venue | volume | swaps | unpriced swaps |
|---|---|---|---|
| Pump.fun Amm | $91.9M | 435,924 | 367 |
| Raydium CLMM | $3.9M | 6,407 | 317 |
| Whirlpool | $3.7M | 4,494 | 8 |
| Meteora DLMM | $3.3M | 11,853 | 43 |
| aggregator-only | $3.2M | 85,458 | 187 |
| BisonFi | $2.0M | 5,929 | 0 |
| Quantum | $1.4M | 3,977 | 0 |
| multi: AlphaQ+Manifest+Whirlpool | $909k | 20 | 0 |
| Raydium | $890k | 4,346 | 17 |
| HumidiFi | $669k | 2,038 | 1 |
| GoonFi V2 | $619k | 592 | 2 |
| Meteora DAMM v2 | $606k | 39,019 | 847 |
| multi: AlphaQ+Manifest | $531k | 164 | 0 |
| TesseraV | $509k | 716 | 2 |
| Manifest | $388k | 422 | 0 |
| multi: TesseraV+ZeroFi | $350k | 6 | 0 |
| multi: Meteora DLMM+Pump.fun Amm | $344k | 515 | 142 |
| multi: Meteora DLMM+Raydium CP | $307k | 2,737 | 41 |
| ZeroFi | $265k | 658 | 0 |
| multi: Raydium CP+Whirlpool | $230k | 2,552 | 7 |
| multi: Meteora DLMM+Pump.fun Amm+TesseraV | $222k | 66 | 2 |
| AlphaQ | $200k | 677 | 1 |
| multi: Meteora DLMM+TesseraV+Whirlpool | $190k | 47 | 2 |
| multi: Meteora DLMM+Whirlpool | $184k | 361 | 30 |
| multi: GoonFi V2+Meteora DLMM+Raydium CLMM | $176k | 109 | 14 |


Volume routed through aggregators (counted once per swap, overlapping with the venue table): Jupiter Aggregator v6 $10.8M


Top pairs:

| venue | pair | volume | swaps |
|---|---|---|---|
| Pump.fun Amm | GyKY…mApJ / SOL | $8.0M | 5655 |
| Pump.fun Amm | DkDs…1n2M / SOL | $7.6M | 6830 |
| Pump.fun Amm | AfUe…Jb5p / SOL | $6.6M | 7067 |
| Pump.fun Amm | 5dYh…ftag / SOL | $4.9M | 5254 |
| Pump.fun Amm | Bii2…SAwR / SOL | $4.5M | 4328 |
| Pump.fun Amm | 3Sdg…9nsq / SOL | $4.0M | 4009 |
| Pump.fun Amm | Gzpt…DyGN / SOL | $3.5M | 4635 |
| Pump.fun Amm | Htby…VGte / SOL | $2.5M | 2426 |
| Pump.fun Amm | DP3p…Nzai / SOL | $2.5M | 5223 |
| Pump.fun Amm | 9t7D…2jWf / SOL | $2.3M | 2231 |
| Pump.fun Amm | FWNZ…3uxM / SOL | $2.2M | 3414 |
| Pump.fun Amm | 7UF1…5y14 / SOL | $2.1M | 2327 |
| Whirlpool | SOL / USDC | $2.1M | 653 |
| Pump.fun Amm | BqUC…fjNS / SOL | $1.9M | 5831 |
| BisonFi | SOL / USDC | $1.9M | 5457 |
| Pump.fun Amm | SOL / yheF…wCx2 | $1.9M | 7466 |
| Pump.fun Amm | FVNB…CgRS / SOL | $1.8M | 11692 |
| Meteora DLMM | SOL / USDC | $1.8M | 452 |
| Pump.fun Amm | 773j…ceBJ / SOL | $1.7M | 6582 |
| Quantum | SOL / USDC | $1.3M | 3910 |
| Pump.fun Amm | 4WBk…quPq / SOL | $1.3M | 5287 |
| Pump.fun Amm | 5S4B…R2mj / SOL | $1.1M | 1488 |
| Pump.fun Amm | DiSr…BxVL / SOL | $989k | 2291 |
| Pump.fun Amm | FEdZ…9x2i / SOL | $934k | 2163 |
| Pump.fun Amm | 5vXi…AA73 / SOL | $916k | 1228 |
| Pump.fun Amm | FhGN…rmsq / SOL | $856k | 9323 |
| Pump.fun Amm | BoiK…csiv / SOL | $854k | 5444 |
| Pump.fun Amm | BnUq…kyr7 / SOL | $788k | 1969 |
| Pump.fun Amm | DZjS…grPY / SOL | $751k | 3817 |
| Pump.fun Amm | ENa5…URrH / SOL | $733k | 2344 |


Implied prices from single-pair swaps against a priced leg (median, min–max across the window):

| token | median | min | max | swaps | volume |
|---|---|---|---|---|---|
| USDC | $1.00265 | $0.0006898 | $775.9 | 19276 | $13.6M |
| SOL | $105.167 | $0.1362 | $1.441e+04 | 16404 | $11.3M |
| ? | $4.16241e-05 | $3.693e-05 | $4.642e-05 | 5369 | $8.0M |
| ? | $0.000121988 | $2.755e-05 | $0.0001436 | 5730 | $7.6M |
| ? | $2.48469e-05 | $2.285e-05 | $2.808e-05 | 7067 | $6.6M |
| ? | $1.83295e-05 | $1.492e-05 | $2.159e-05 | 4765 | $4.9M |
| ? | $7.76977e-05 | $6.49e-05 | $9.02e-05 | 4327 | $4.5M |
| ? | $1.83651e-05 | $1.71e-05 | $1.969e-05 | 4001 | $4.0M |
| ? | $2.9485e-05 | $2.711e-05 | $3.438e-05 | 3848 | $3.5M |
| ? | $3.01349e-06 | $9.864e-07 | $4.537e-06 | 2382 | $2.5M |
| ? | $0.000287932 | $5.041e-05 | $0.0004228 | 4546 | $2.5M |
| ? | $2.96908e-05 | $2.498e-05 | $3.6e-05 | 2227 | $2.3M |
| ? | $0.000173045 | $0.0001574 | $0.0001896 | 3405 | $2.2M |
| ? | $0.000158798 | $0.0001501 | $0.0002014 | 2319 | $2.1M |
| ? | $4.53558e-05 | $1.577e-05 | $0.0001247 | 5736 | $1.9M |
| USDT | $0.999957 | $0.9718 | $1450 | 3100 | $1.9M |
| ? | $0.000383437 | $0.0002254 | $0.0004809 | 7337 | $1.9M |
| ? | $5.58035e-05 | $1.07e-05 | $0.0001615 | 10999 | $1.8M |
| ? | $3.30734e-05 | $7.867e-06 | $0.0001019 | 6455 | $1.7M |
| ? | $3.23176e-05 | $1.485e-05 | $8.4e-05 | 5176 | $1.3M |
| ? | $7.50346e-05 | $5.453e-05 | $8.544e-05 | 1264 | $1.1M |
| ? | $0.00440101 | $0.004251 | $0.004566 | 1660 | $1.1M |
| ? | $0.000195481 | $5.041e-05 | $0.0003286 | 1939 | $986k |
| ? | $1.18186 | $1.182 | $1.182 | 11 | $963k |
| ? | $0.000193718 | $5.041e-05 | $0.0002831 | 1839 | $931k |
| ? | $7.51813e-05 | $5.451e-05 | $9.043e-05 | 1039 | $915k |
| ? | $0.109331 | $0.104 | $31.7 | 874 | $915k |
| ? | $3.53575e-05 | $9.142e-06 | $8.181e-05 | 5186 | $851k |
| ? | $2.76402e-05 | $1.318e-05 | $6.566e-05 | 8730 | $848k |
| ? | $0.00062553 | $0.0004908 | $0.0007244 | 1945 | $788k |


Largest swaps:

| time | venue | payer | sold | bought | value | tip SOL |
|---|---|---|---|---|---|---|
| 13:19:54 | multi: TesseraV+ZeroFi | 7S6s…HmQD | 3312 SOL | 350.0k USDC | $350k | 0.0000 |
| 13:44:28 | multi: AlphaQ+Manifest+Whirlpool | CS9a…RRWe | 300.0k USDC | raw 253.85B AvZZ…ZeUj | $300k | 0.0001 |
| 13:42:36 | Raydium | 4uNQ…8BWt | 123.8k USDC, 1174 SOL | raw 1085.26B 8HoQ…byvu | $248k | 0.0000 |
| 13:45:41 | Manifest | 5edL…Gjgr | 199.9k PYUSD | 199.9k USDC | $200k | 0.0000 |
| 13:46:22 | Pump.fun Amm | FzD1…wMBM | raw 19775.63B q8nz…pump | 1834 SOL | $194k | 0.0000 |
| 13:57:51 | multi: AlphaQ+Manifest | CS9a…RRWe | 190.0k PYUSD | 190.0k USDC | $190k | 0.0001 |
| 13:47:35 | Pump.fun Amm | DBca…RWoT | raw 414326.44B 7wej…pump | 1788 SOL | $189k | 0.0000 |
| 13:30:07 | Pump.fun Amm | HUqc…73un | 1550 SOL | raw 196021.13B wgKH…pump | $164k | 0.0000 |
| 13:44:29 | Pump.fun Amm | 6QXS…zbdW | 1500 SOL | raw 195678.17B EZUT…pump | $159k | 0.0000 |
| 13:53:40 | Pump.fun Amm | 9QvB…nMuL | raw 22583.18B 4bf5…hdC3 | raw 758378.95B FWNZ…3uxM, 1264 SOL | $134k | 0.0000 |
| 13:28:08 | multi: AlphaQ+Manifest+Raydium CLMM | 6HNV…3Gmi | 110.7k USDG | raw 96833.90B 5Y8N…cxp5 | $111k | 0.0000 |
| 13:27:10 | Pump.fun Amm | DZg4…WKTe | 999 SOL | raw 190503.72B Z93u…pump | $106k | 0.0000 |
| 13:42:43 | multi: AlphaQ+Manifest+Whirlpool | Exur…55Hy | 100.0k USDG | 100.0k USDC | $100k | 0.0000 |
| 13:56:13 | multi: AlphaQ+Manifest | Exur…55Hy | 100.0k USDG | 100.0k USDC | $100k | 0.0000 |
| 13:44:15 | multi: Manifest+Whirlpool | CS9a…RRWe | 100.0k USDC | raw 84.62B AvZZ…ZeUj | $100k | 0.0001 |
| 13:45:02 | multi: AlphaQ+Manifest+Whirlpool | CS9a…RRWe | 100.0k USDC | raw 84.61B AvZZ…ZeUj | $100k | 0.0000 |
| 13:44:19 | multi: AlphaQ+Manifest+Whirlpool | CS9a…RRWe | 100.0k USDC | raw 84.62B AvZZ…ZeUj | $100k | 0.0001 |
| 13:45:07 | Whirlpool | CS9a…RRWe | 100.0k USDC | raw 84.61B AvZZ…ZeUj | $100k | 0.0000 |
| 13:45:11 | multi: AlphaQ+Manifest+Whirlpool | CS9a…RRWe | 100.0k USDC | raw 84.61B AvZZ…ZeUj | $100k | 0.0000 |
| 13:44:23 | multi: AlphaQ+Manifest+Whirlpool | CS9a…RRWe | 100.0k USDC | raw 84.62B AvZZ…ZeUj | $100k | 0.0001 |
| 13:23:52 | multi: JupLend AMM+Manifest+SolFi V2 | 4fVL…VtWq | 100.0k USDT | 100.0k USDG | $100k | 0.0000 |
| 13:20:24 | multi: HumidiFi+Manifest+TesseraV | 5SvX…f7Uy | raw 22222.22B pump…9Dfn | 99.4k USDC | $99k | 0.0000 |
| 13:46:50 | Pump.fun Amm | EEPx…vZyo | raw 9697.27B zszL…pump | 875 SOL | $92k | 0.0000 |
| 13:51:58 | Pump.fun Amm | 5XWM…ihgV | raw 9872.00B jBxt…pump | 792 SOL | $84k | 0.0000 |
| 13:57:45 | multi: AlphaQ+Manifest | 23av…74DD | 76.0k USDC | 76.0k USDG | $76k | 0.0000 |


Same-block sandwich pattern (trader A buys, another trader buys the same token through the same pool, A sells — all in one block): 493 pattern matches, of which 4 closed the token position within 10% (the true sandwich shape; the rest are coincidental buy-buy-sell sequences in busy pump pools). Confirmed-shape victim volume $6843.

| attacker | closed sandwiches | PnL (SOL+stable legs) |
|---|---|---|
| 3ct4…fh5J | 3 | $1.49 |
| 3N1K…AdiS | 3 | $12.66 |
| 4GcC…HGfV | 2 | -$0.84 |
| 4vWg…NAux | 2 | $0.30 |
| Aceu…XBSS | 2 | $8.05 |
| 38ou…TRhY | 1 | $5.49 |
| BW42…7Q8A | 1 | -$10.11 |
| 7Mpf…XKm6 | 1 | $2.13 |
| G6iN…yynr | 1 | $8.44 |
| Df2f…iGCq | 1 | $41.05 |


| time | token | attacker | victim | victim size | front size | attacker PnL | closed | tips SOL |
|---|---|---|---|---|---|---|---|---|
| 13:38:21 | BqUC…fjNS | 7WpH…kjjz | EQNo…jdLx | $607 | $120 | -$6.66 | yes | 0.0 |
| 13:40:28 | BqUC…fjNS | 5PH8…Xdt8 | 7RXL…QMJN | $427 | $172 | -$9.12 | yes | 0.0 |
| 13:24:55 | yheF…wCx2 | 555A…noFe | AJaR…HGWt | $410 | $340 | -$16.98 | yes | 0.0 |
| 13:54:35 | 773j…ceBJ | 7QfA…WpQ7 | 8Q4t…gwcg | $380 | $144 | -$7.45 | yes | 0.0 |
| 13:35:11 | BnUq…kyr7 | 33R1…oZiC | 5Xz9…Fasi | $707 | $292 | $601 |  | 0.0 |
| 13:30:47 | BcGV…pump | 8iVc…2Jze | GtsZ…GNWy | $621 | $635 | -$511 |  | 0.0 |
| 13:53:49 | 7f36…LVBT | 6YNF…WJec | 57YY…Ph9y | $522 | $18.00 | $343 |  | 0.0 |
| 13:32:26 | yheF…wCx2 | 3nWL…z4tN | 8Wvk…7uYF | $502 | $98.00 | $325 |  | 0.0 |
| 13:30:38 | BqUC…fjNS | GiB9…yNe8 | EhXu…LNAE | $481 | $319 | $66.36 |  | 0.0 |
| 13:53:13 | DZjS…grPY | Dk9H…ZmsN | FaFu…Dp31 | $448 | $72.00 | -$10.81 |  | 0.0 |
| 13:46:40 | 773j…ceBJ | 7QfA…WpQ7 | 5twJ…GbQX | $442 | $314 | -$203 |  | 0.0 |
| 13:55:50 | 773j…ceBJ | Ak4U…uFcL | 3Cb7…Uh7G | $439 | $433 | -$301 |  | 0.0 |


Pump.fun (bonding curve + PumpSwap AMM): ok 785060, failed 241978, launches 824, pumpswap_pools_created 141, migrations 7. Bonding-curve SOL turnover 24854.8 SOL (buys 13515.6, sells 11339.2); PumpSwap trader SOL legs 870570.0 SOL. 383 unique launch creators; most active: VygS…Zg4R (41), 74fH…87Y4 (32), Amjv…praL (23), 3ph9…ioVA (22), 3Tnc…ebBu (17). Instruction mix: Sell 499629, BuyExactQuoteIn 246759, Buy 204907, SellV2 11299, BuyExactQuoteInV2 9417, BuyExactSolIn 6784, BondingCurveV3 6735, ClaimCashback 4213, BuyV2 2823, SellBondingCurvePercentage 2071, SellPumpSwapPercentage 1642, ClaimCashbackV2 1274.


## D. Lending: rates at head, events in window


Kamino SOL/BTC Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| SOL | 5.01% | 6.57% | 90.3% | $253.2M | $228.7M |
| dSOL | 0.00% | 1.61% | 0.0% | $235.8M | $104 |
| USDC | 3.58% | 5.40% | 82.1% | $122.4M | $100.4M |
| JITOSOL | 0.00% | 1.66% | 0.6% | $98.5M | $615k |
| cbBTC | 0.00% | 0.15% | 1.9% | $56.9M | $1.1M |
| JupSOL | 0.00% | 1.69% | 1.0% | $52.4M | $524k |
| USDG | 3.70% | 5.48% | 83.4% | $45.1M | $37.6M |
| PYUSD | 1.82% | 2.89% | 85.5% | $40.1M | $34.3M |
| hSOL | 0.00% | 1.61% | 0.0% | $28.5M | $11k |
| dfdvSOL | 0.00% | 1.61% | 0.0% | $22.4M | $0.00 |
| MSOL | 0.00% | 1.83% | 2.5% | $22.3M | $561k |
| xBTC | 0.00% | 0.11% | 1.5% | $18.7M | $275k |
| vSOL | 0.00% | 1.61% | 0.0% | $17.5M | $6510 |
| USDT | 3.21% | 5.14% | 77.8% | $10.5M | $8.2M |


Kamino JLP Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| JLP | 0.00% | 0.00% | 0.0% | $45.4M | $0.00 |
| USDC | 3.60% | 4.43% | 90.6% | $20.4M | $18.5M |
| USDT | 4.39% | 5.26% | 93.0% | $1.9M | $1.7M |
| PYUSD | 4.16% | 5.03% | 92.3% | $1.4M | $1.3M |


Kamino Ethena Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| USDe | 0.00% | 0.01% | 0.0% | $267.5M | $1027 |
| PYUSD | 3.41% | 4.05% | 93.8% | $251.4M | $235.9M |


Kamino Jito Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| JITOSOL | 0.00% | 0.02% | 1.7% | $21.6M | $366k |
| SOL | 4.92% | 5.84% | 93.9% | $20.6M | $19.3M |


Save (Solend) main market (reserves with ≥ $1M supplied; rates as reported by the Save API, utilisation from reserve state):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| mSOL | 0.00% | 0.00% | 0.0% | $24.9M | $0.00 |
| bSOL | 0.00% | 0.00% | 0.0% | $22.4M | $0.00 |
| USDC | 2.96% | 5.04% | 73.9% | $22.2M | $16.4M |
| SOL | 2.83% | 5.40% | 66.1% | $20.3M | $13.4M |
| jitoSOL | 0.00% | 0.00% | 0.0% | $8.7M | $0.00 |
| USDT | 1.76% | 4.08% | 54.3% | $5.2M | $2.8M |
| SAVE…tTFt | 0.00% | 0.00% | 0.0% | $5.1M | $0.00 |
| 7Q2a…cavn | 0.00% | 0.00% | 0.0% | $2.5M | $0.00 |
| cbBTC | 0.28% | 2.97% | 11.7% | $2.5M | $297k |
| jupSOL | 0.00% | 0.00% | 0.0% | $1.6M | $0.00 |


Jupiter Lend Earn (supply rate + rewards, bps as reported):

| vault | asset | supply APY | rewards | total | total assets |
|---|---|---|---|---|---|
| jlUSDC | USDC | 4.56% | 0.40% | 4.96% | $451.7M |
| jlJupUSD | JupUSD | 5.40% | 1.00% | 6.40% | $57.9M |
| jlWSOL | WSOL | 3.87% | 0.00% | 3.87% | $19.9M |
| jlUSDT | USDT | 4.30% | 0.00% | 4.30% | $17.5M |
| jlEURC | EURC | 3.74% | 0.00% | 3.74% | $5.1M |
| jlUSDS | USDS | 4.74% | 0.00% | 4.74% | $3.9M |
| jlUSDG | USDG | 8.32% | 0.00% | 8.32% | $2.9M |


Lending events in the window (instruction discriminators matched per program):

| venue | txs | failed | events |
|---|---|---|---|
| Kamino Lend | 2652 | 1524 | flash_borrow_reserve_liquidity (failed) 1404, flash_repay_reserve_liquidity (failed) 1404, refresh_reserve 750, refresh_reserves_batch 360, refresh_obligation 246, refresh_reserve (failed) 119, refresh_obligation (failed) 119, liquidate_obligation_and_redeem_reserve_collateral_v2 (failed) 118, withdraw_obligation_collateral_and_redeem_reserve_collateral_v2 96, deposit_reserve_liquidity_and_obligation_collateral_v2 94 |
| marginfi v2 | 950 | 114 | lending_account_start_flashloan (failed) 114, lending_account_end_flashloan (failed) 114, lending_account_repay (failed) 97, lending_account_borrow (failed) 95, lending_account_borrow 70, lending_account_repay 67, lending_account_start_flashloan 66, lending_account_end_flashloan 66, lending_account_withdraw 9, lending_account_deposit 7 |
| Jupiter Lend Earn | 366 | 7 |  |
| Save (Solend) | 19 | 2 | borrow_obligation_liquidity 7, withdraw_obligation_collateral_and_redeem_reserve_collateral 3, deposit_reserve_liquidity_and_obligation_collateral 2, borrow_obligation_liquidity (failed) 1, repay_obligation_liquidity 1, deposit_reserve_liquidity_and_obligation_collateral (failed) 1 |


Liquidations that succeeded: 0. Liquidation attempts (ok / failed, top payers): Kamino Lend 0 / 118 (bSoL…SpgW 118); marginfi v2 0 / 2 (A2KE…bdb2 2). Successful flash loans: Kamino Lend 28 txs (~$202k principal), marginfi v2 66 txs (~$0.00 principal). Flash-loan payers (with failures): Kamino Lend: guof…VNk3 (failed) 1285, Hz7K…r7sz (failed) 65, F1ae…esMm (failed) 22, Dsg7…p6aM 8, 7tUA…YsVH (failed) 7; marginfi v2: 3zdX…MPL8 64, MoSt…Xr6m (failed) 39, 3zZ6…uQv1 (failed) 20, 996m…1icu (failed) 17, ALVa…hGnz (failed) 15. Programs co-invoked in flash-loan txs: Kamino Lend: Jupiter Aggregator v6 1330, TesseraV 1301, Perps 1285, Meteora DLMM 48, Scorch 36; marginfi v2: Jupiter Aggregator v6 77, Meteora DLMM 67, Pump.fun Amm 33, Whirlpool 28, Raydium CLMM 26.


Same asset, different venue (supply APY / borrow APY / utilisation / supplied; reserves ≥ $5M; Jupiter Lend = supply + rewards, no borrow side):

| asset | venue | supply APY | borrow APY | util | supplied |
|---|---|---|---|---|---|
| USDC | Jupiter Lend | 4.96% | – | – | $451.7M |
| USDC | Kamino JLP | 3.60% | 4.43% | 91% | $20.4M |
| USDC | Kamino SOL/BTC | 3.58% | 5.40% | 82% | $122.4M |
| USDC | Save main | 2.96% | 5.04% | 74% | $22.2M |
| USDE | Kamino Ethena | 0.00% | 0.01% | 0% | $267.5M |
| SOL | Kamino SOL/BTC | 5.01% | 6.57% | 90% | $253.2M |
| SOL | Kamino Jito | 4.92% | 5.84% | 94% | $20.6M |
| SOL | Jupiter Lend | 3.87% | – | – | $19.9M |
| SOL | Save main | 2.83% | 5.40% | 66% | $20.3M |
| PYUSD | Kamino Ethena | 3.41% | 4.05% | 94% | $251.4M |
| PYUSD | Kamino SOL/BTC | 1.82% | 2.89% | 86% | $40.1M |
| JITOSOL | Kamino SOL/BTC | 0.00% | 1.66% | 1% | $98.5M |
| JITOSOL | Kamino Jito | 0.00% | 0.02% | 2% | $21.6M |
| JITOSOL | Save main | 0.00% | 0.00% | 0% | $8.7M |
| JUPUSD | Jupiter Lend | 6.40% | – | – | $57.9M |
| JUPSOL | Kamino SOL/BTC | 0.00% | 1.69% | 1% | $52.4M |
| JLP | Kamino JLP | 0.00% | 0.00% | 0% | $45.4M |
| USDG | Kamino SOL/BTC | 3.70% | 5.48% | 83% | $45.1M |
| USDT | Jupiter Lend | 4.30% | – | – | $17.5M |
| USDT | Kamino SOL/BTC | 3.21% | 5.14% | 78% | $10.5M |
| USDT | Save main | 1.76% | 4.08% | 54% | $5.2M |
| EURC | Jupiter Lend | 3.74% | – | – | $5.1M |


## E. Stablecoins and LSTs: issuance, pegs, NAV

Mints and burns on the registry stablecoin and LST mints, split by whether the instruction ran inside a CCTP transaction (bridge) or not (issuer treasury / stake pool):

| token | issuer minted | issuer burned | CCTP minted | CCTP burned | net |
|---|---|---|---|---|---|
| PYUSD | 0 | 570,000 | 0 | 0 | -570,000 |
| USDC | 0 | 64,365 | 0 | 365,468 | -429,833 |
| USDG | 0 | 175,959 | 0 | 0 | -175,959 |
| jupSOL | 88 | 0 | 0 | 0 | 88 |
| bSOL | 0 | 20 | 0 | 0 | -20 |
| mSOL | 18 | 2 | 0 | 0 | 16 |
| jitoSOL | 2 | 0 | 0 | 0 | 2 |
| bbSOL | 2 | 0 | 0 | 0 | 2 |
| INF | 1 | 0 | 0 | 0 | 1 |
| sSOL | 0 | 1 | 0 | 0 | -1 |
| JupUSD | 0 | 0 | 0 | 0 | 0 |


By mint authority (CCTP mints/burns carry the CCTP minter PDA as authority; issuer treasuries carry the issuer authority):

| token | side | authority | label | amount | n |
|---|---|---|---|---|---|
| PYUSD | burn | D3Pf…BZBo |  | 570,000 | 1 |
| USDC | burn | CCTP tx (user burn / custody) |  | 365,468 | 87 |
| USDG | burn | 4fVL…VtWq |  | 99,958 | 1 |
| USDG | burn | 23av…74DD |  | 76,001 | 1 |
| USDC | burn | 41zC…wePu | Binance-adjacent USDC routing wallet | 47,365 | 2 |
| USDC | burn | 7MjD…EoEG |  | 17,000 | 1 |
| jupSOL | mint | EMju…QDNw |  | 88 | 2 |
| mSOL | mint | 3JLP…g6KM |  | 18 | 4 |
| bSOL | burn | 9tMY…oGK5 |  | 15 | 2 |
| bSOL | burn | Lion…VK6y |  | 5 | 1 |
| jitoSOL | mint | 6iQK…pVSS |  | 2 | 24 |
| mSOL | burn | Eg8b…DhT2 |  | 2 | 1 |
| bbSOL | mint | 3pFT…xyGJ |  | 2 | 1 |
| INF | mint | AYhu…CGvW |  | 1 | 7 |
| sSOL | burn | 2pC4…DXtY |  | 1 | 1 |
| jitoSOL | burn | 2tKR…iKhW |  | 0 | 2 |
| JupUSD | burn | AkLh…ouCA |  | 0 | 4 |
| JupUSD | burn | 2Egd…Aq3J |  | 0 | 3 |
| JupUSD | burn | 8o5Y…YmUN |  | 0 | 2 |
| JupUSD | burn | Gsp2…hBJG |  | 0 | 3 |


Largest single mints/burns:

| time | token | side | amount | authority | CCTP tx |
|---|---|---|---|---|---|
| 13:28:36 | PYUSD | burn | 570,000 | D3Pf…BZBo |  |
| 13:24:50 | USDC | burn | 131,000 | HBgL…mxmD | yes |
| 13:24:56 | USDG | burn | 99,958 | 4fVL…VtWq |  |
| 13:22:58 | USDC | burn | 99,442 | 5SvX…f7Uy | yes |
| 13:57:58 | USDG | burn | 76,001 | 23av…74DD |  |
| 13:34:29 | USDC | burn | 50,000 | 6omu…Ynfb | yes |
| 13:26:09 | USDC | burn | 47,347 | 41zC…wePu |  |
| 13:33:10 | USDC | burn | 17,000 | 7MjD…EoEG |  |
| 13:20:49 | USDC | burn | 16,510 | Eeoc…Brwd | yes |
| 13:43:24 | jupSOL | mint | 88 | EMju…QDNw |  |
| 13:52:57 | USDC | burn | 7,791 | Eqbw…post | yes |
| 13:24:51 | USDC | burn | 4,148 | 5kKg…BAwW | yes |
| 13:55:24 | USDC | burn | 3,007 | 6H7G…DDBe | yes |
| 13:56:04 | USDC | burn | 3,000 | 7HBk…i3Fe | yes |
| 13:27:36 | USDC | burn | 3,000 | 288X…qtTm | yes |


Stablecoin prices at head (Jupiter aggregator price; deviation from par):

| token | price | vs par | liquidity (Jupiter) |
|---|---|---|---|
| USDC | $0.9999 | -1.3 bp | $410.8M |
| USDT | $0.9998 | -1.6 bp | $41.8M |
| PYUSD | $0.9999 | -1.1 bp | $29.7M |
| USDS | $0.9998 | -2.0 bp | $1.8M |
| USD1 | $0.9998 | -2.0 bp | $23.9M |
| USDG | $0.9999 | -0.5 bp | $36.4M |
| JupUSD | $0.9995 | -4.9 bp | $19.3M |
| USDe | $0.9999 | -0.5 bp | $8.9M |
| sUSDe | $1.2410 |  | $2781 |
| EURC | $1.1625 |  | $664k |


LSTs: SOL per token from the stake pool (Sanctum) vs market price in SOL (Jupiter price / Jupiter SOL price):

| LST | NAV (SOL) | market (SOL) | premium/discount | liquidity |
|---|---|---|---|---|
| jitoSOL | 1.27587 | 1.30004 | +189.5 bp | $1.07B |
| mSOL | 1.37665 | 1.40285 | +190.3 bp | $240.1M |
| bSOL | 1.29072 | 1.31348 | +176.3 bp | $96.0M |
| jupSOL | 1.18394 | 1.20796 | +202.9 bp | $540.1M |
| INF | 1.40784 | 1.44943 | +295.4 bp | $199.1M |
| hSOL | 1.16206 | 1.18408 | +189.5 bp | $96.1M |
| vSOL | 1.14911 | 1.17067 | +187.7 bp | $139.2M |
| dSOL | 1.18970 | 1.21254 | +192.0 bp | $293.0M |
| bbSOL | 1.14756 | 1.18485 | +324.9 bp | $131.9M |
| sSOL | 1.19559 | 1.16963 | -217.1 bp | $98k |


LST issuance in the window (mintTo/burn on the LST mints): jupSOL +88 −0, bSOL +0 −20, mSOL +18 −2, jitoSOL +2 −0, bbSOL +2 −0, INF +1 −0, sSOL +0 −1


## F. Bridges, exchanges, large transfers, poisoning

CCTP USDC: out $365k (87 deposit-for-burn), in $24k (5 receive-message; v2 pays recipients out of a custody token account instead of minting — Sui $2.00, Base $8513, Avalanche $15k).

| direction | chain | USDC | transfers |
|---|---|---|---|
| out | Arbitrum | $154k | 6 |
| out | Avalanche | $135k | 7 |
| out | Ethereum | $25k | 9 |
| out | HyperEVM | $16k | 30 |
| out | domain 27 | $14k | 19 |
| out | Polygon | $8333 | 4 |
| out | Ink | $7791 | 1 |
| out | Base | $4187 | 9 |
| out | Sui | $987 | 2 |
| in | Avalanche | $15k | 1 |
| in | Base | $8513 | 3 |
| in | Sui | $2.00 | 1 |


Largest CCTP transfers:

| time | direction | chain | USDC | payer | recipient (EVM) |
|---|---|---|---|---|---|
| 13:24:50 | out | Avalanche | $131k | HBgL…mxmD | 0xafa88a2f…a112 |
| 13:22:58 | out | Arbitrum | $99k | 5SvX…f7Uy | 0x28b5a0e9…cf5d |
| 13:34:29 | out | Arbitrum | $50k | FwDz…uaYq | 0x28b5a0e9…cf5d |
| 13:20:49 | out | Ethereum | $17k | Eeoc…Brwd | 0x4b3cd0bb…fa3e |
| 13:45:49 | in | Avalanche | $15k | D8P6…Tv7f |  |
| 13:52:57 | out | Ink | $7791 | Eqbw…post | 0x28b5a0e9…cf5d |
| 13:30:46 | in | Base | $4722 | BRtN…qbMp |  |
| 13:24:51 | out | Arbitrum | $4148 | 5kKg…BAwW | 0x28b5a0e9…cf5d |
| 13:55:24 | out | Base | $3007 | 6H7G…DDBe | 0x08b00cee…1e65 |
| 13:56:04 | out | Polygon | $3000 | 7HBk…i3Fe | 0x28b5a0e9…cf5d |
| 13:27:36 | out | Ethereum | $3000 | 288X…qtTm | 0x28b5a0e9…cf5d |
| 13:57:15 | out | HyperEVM | $2997 | CKuB…Ljcf | 0x28b5a0e9…cf5d |


Exchange net flow (labels from memory; the fan-in column is the behavioural check — a deposit hot wallet receives from many unique senders):

| exchange | net by asset | net USD | txs | senders | receivers | fan-in (SOL≥0.1) |
|---|---|---|---|---|---|---|
| Binance | USDC +8.77M, SOL -22.9k, USDT -94.6k, BONK -23.56B, RAY -53.1k | $6.1M | 1214 | 131 | 333 | 130 |
| KuCoin | USDC -546.3k, SOL -2984, USDT +47.5k, USDG +5994, BONK +1.45M | -$808k | 285 | 3 | 102 | 28 |
| Coinbase 2 | SOL +6095, USDC -28.0k, EURC -1587, WIF +3872, jitoSOL +1.352 | $615k | 370 | 174 | 124 | 172 |
| Coinbase | USDC -516.4k, SOL +147, EURC +4995, BONK +889.33M, PENGU +100.0k | -$491k | 197 | 31 | 87 | 26 |
| Gate.io | SOL -2101, USDT -51.1k, PENGU -4.02M, USDC -28.7k, USDG -12.0k | -$362k | 156 | 0 | 1 | 0 |
| MEXC | USDT -189.3k, SOL +295, USDC +15.8k, RAY -80, 6GmA…UNgx +115272.80B | -$142k | 367 | 125 | 110 | 49 |
| Coinbase 3 | SOL -209, USDC -13.8k, EURC -4910, BONK +1.69B, PYUSD +137 | -$36k | 219 | 31 | 113 | 27 |
| Bybit | SOL -0.0099, 7i5K…pfRx +2295.19B, a3W4…pump -4.90B, pump…9Dfn -2555.96B, USDT 0 | -$1.00 | 28 | 10 | 3 | 0 |


Label checks: Binance: fan-in consistent with exchange deposit address; Binance 2: no activity in window; Coinbase: fan-in consistent with exchange deposit address; Coinbase 2: fan-in consistent with exchange deposit address; Coinbase 3: fan-in consistent with exchange deposit address; Kraken: no activity in window; OKX: no activity in window; Bybit: some activity; Gate.io: some activity; KuCoin: fan-in consistent with exchange deposit address; MEXC: fan-in consistent with exchange deposit address; Crypto.com: no activity in window; Bitget: no activity in window; HTX: no activity in window


Unlabelled addresses with exchange-like fan-in (≥ 40 unique senders of ≥ 0.1 SOL):

| address | label | unique senders | transfers in | SOL in | median in | transfers out | destinations | SOL out | shape |
|---|---|---|---|---|---|---|---|---|---|
| 7uTT…i8pZ | vault of deposit router 99vQ… (largest unlabelled fan-in) | 1622 | 2597 | 6817.2 | 0.537 | 39 | 1 | 6833.8 | collector hub (many in, ≤2 out) |
| A1zq…2mos | sybil-cluster collector (3,254 wallets → 1 sweep in 6 min) | 710 | 710 | 819.6 | 0.297 | 1 | 1 | 1266.1 | collector hub (many in, ≤2 out) |
| 62jw…MZ4F | sybil-cluster collector (533 wallets → 1 sweep) | 533 | 533 | 680.1 | 0.582 | 1 | 1 | 680.1 | collector hub (many in, ≤2 out) |
| 7uEU…v7HD |  | 449 | 529 | 130.2 | 0.205 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 6FQv…EUX9 |  | 440 | 440 | 404.2 | 0.347 | 102 | 6+ | 891.3 | mixed |
| 6pSP…A52i | volume-bot hub cycling a pump token among ~820 wallets | 403 | 664 | 401.6 | 0.395 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| FC9B…xWcg | bundler hub (funds ~400 wallets and collects from ~400) | 397 | 397 | 2364.4 | 1.544 | 419 | 6+ | 2365.5 | mixed |
| 3AXU…KyM4 |  | 378 | 635 | 429.8 | 0.411 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| D7vr…5XfZ |  | 369 | 650 | 427.2 | 0.470 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| HCQS…1f3f |  | 361 | 544 | 330.1 | 0.325 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 9dua…zHJ9 |  | 340 | 497 | 376.4 | 0.489 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| CGMM…eksJ |  | 317 | 338 | 98.1 | 0.202 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| EW9d…Bs7J |  | 285 | 1705 | 5926.3 | 3.476 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| DJ9d…dp3R |  | 284 | 307 | 96.8 | 0.208 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| Dvfr…LK6e |  | 269 | 269 | 77.3 | 0.202 | 0 | 0 | 0.0 | deposit address (many in, little out) |


Distributors (≥ 200 outgoing SOL transfers of ≥ 0.1 SOL to ≥ 6 destinations — wallet funders, payout hubs):

| address | label | transfers out | SOL sent |
|---|---|---|---|
| F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 1985 | 9812.3 |
| BwWK…de6s |  | 1197 | 452.6 |
| CVrb…QKWa |  | 1027 | 1516.8 |
| 5tzF…uAi9 | Binance | 730 | 27946.7 |
| NMVX…VYXy |  | 602 | 689.7 |
| ARu4…5SZn |  | 590 | 747.2 |
| Biw4…PTUU |  | 573 | 798.7 |
| BMKa…sn1p |  | 529 | 458.2 |
| EUoK…a72Y |  | 526 | 892.0 |
| 3JsN…6c9G |  | 525 | 678.4 |
| 9aRk…PG8F |  | 472 | 1093.3 |
| 7bf1…uFiM |  | 420 | 1224.3 |


Largest priced position changes (per owner and asset inside one transaction, ≥ $100k):

| time | owner | label | asset | change | value | kind | programs |
|---|---|---|---|---|---|---|---|
| 13:54:08 | 9936…L3QK |  | USDC | +10.00M | $10.0M | lending | Huma |
| 13:54:08 | 7s1d…or2Z |  | USDC | -10.00M | $10.0M | lending | Huma |
| 13:35:44 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | -7.96M | $8.0M | transfer |  |
| 13:35:44 | 5tzF…uAi9 | Binance | USDC | +7.96M | $8.0M | transfer |  |
| 13:23:01 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | -5.06M | $5.1M | transfer |  |
| 13:23:01 | 5tzF…uAi9 | Binance | USDC | +5.06M | $5.1M | transfer |  |
| 13:25:38 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -4.88M | $4.9M | transfer |  |
| 13:25:38 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | +4.88M | $4.9M | transfer |  |
| 13:23:01 | BF61…b8Mw |  | USDC | -3.27M | $3.3M | other | 7pz2…K1Cp |
| 13:23:01 | DBds…RuRy |  | USDC | +3.27M | $3.3M | other | 7pz2…K1Cp |
| 13:44:07 | 6LY1…zkzF |  | USDC | +3.10M | $3.1M | transfer |  |
| 13:43:23 | 8CAA…bvwj |  | USDC | +3.10M | $3.1M | transfer |  |
| 13:44:07 | 8CAA…bvwj |  | USDC | -3.10M | $3.1M | transfer |  |
| 13:43:23 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -3.10M | $3.1M | transfer |  |
| 13:26:15 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -3.08M | $3.1M | transfer |  |
| 13:26:15 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | +3.08M | $3.1M | transfer |  |
| 13:21:04 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | +3.02M | $3.0M | transfer |  |
| 13:21:04 | 5tzF…uAi9 | Binance | USDC | -3.02M | $3.0M | transfer |  |
| 13:50:38 | 5tzF…uAi9 | Binance | USDC | -2.99M | $3.0M | transfer |  |
| 13:50:38 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | +2.99M | $3.0M | transfer |  |
| 13:25:09 | GA3o…KA88 |  | USDC | +2.50M | $2.5M | transfer |  |
| 13:25:09 | 2bpf…g42j |  | USDC | -2.50M | $2.5M | transfer |  |
| 13:20:38 | 45R4…5En6 |  | USDG | -1.45M | $1.4M | transfer |  |
| 13:20:38 | Cmtx…GLKx |  | USDG | +1.45M | $1.4M | transfer |  |
| 13:21:02 | Gem2…oTka |  | USDC | +1.41M | $1.4M | transfer |  |
| 13:21:02 | 7ZNe…spMN |  | USDC | -1.41M | $1.4M | transfer |  |
| 13:47:11 | 8Xcz…UBRv |  | USDC | -1.38M | $1.4M | transfer |  |
| 13:47:11 | GJFX…rVfP |  | USDC | +1.38M | $1.4M | transfer |  |
| 13:52:10 | GJFX…rVfP |  | USDC | -1.35M | $1.4M | transfer |  |
| 13:52:10 | 7kPU…DKAe |  | USDC | +1.35M | $1.4M | transfer |  |


Largest native SOL balance changes (≥ 1,000 SOL):

| time | account | label | change SOL | value | kind | payer |
|---|---|---|---|---|---|---|
| 13:20:37 | 5tzF…uAi9 | Binance | -12410.3 | $1.3M | transfer | 5tzF…uAi9 |
| 13:20:37 | 38xC…MdUP |  | +12398.4 | $1.3M | transfer | 5tzF…uAi9 |
| 13:42:01 | 52MF…4Vo5 |  | -7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:42:00 | 52MF…4Vo5 |  | +7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:42:00 | GYSY…75y2 |  | -7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:42:01 | 5YSo…hxV1 |  | +7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:24:28 | 5YSo…hxV1 |  | -7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:24:28 | 52MF…4Vo5 |  | +7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:24:29 | 52MF…4Vo5 |  | -7200.0 | $761k | transfer | 52MF…4Vo5 |
| 13:24:29 | GYSY…75y2 |  | +7200.0 | $761k | transfer | 52MF…4Vo5 |
| 13:27:39 | 7CGC…j9DV |  | -4734.0 | $500k | transfer | 7CGC…j9DV |
| 13:27:39 | 3vxh…gkom |  | +4734.0 | $500k | transfer | 7CGC…j9DV |
| 13:24:47 | 7v1w…XKwY |  | -4734.0 | $501k | transfer | 7v1w…XKwY |
| 13:24:47 | 7CGC…j9DV |  | +4734.0 | $501k | transfer | 7v1w…XKwY |
| 13:52:30 | 5tzF…uAi9 | Binance | -4004.0 | $423k | transfer | 5tzF…uAi9 |
| 13:52:30 | FkaL…3MZp |  | +4003.9 | $423k | transfer | 5tzF…uAi9 |
| 13:52:30 | FkaL…3MZp |  | -4001.8 | $423k | other | FkaL…3MZp |
| 13:52:30 | 5yiG…LF1R |  | +4001.8 | $423k | other | FkaL…3MZp |
| 13:29:48 | E1mB…BhZx |  | -3754.3 | $397k | dex_other | EGL3…HEdY |
| 13:29:48 | GkXG…W5LH |  | +3754.3 | $397k | dex_other | EGL3…HEdY |


Address-poisoning style dust (≤ 1 raw token unit or ≤ 1,000 lamports sent by the payer to ≥ 20 distinct recipients): 40,780 transfers in the window from 221 senders with ≥ 50 each. Top senders (senders that dust only a handful of accounts — market-maker heartbeats — are excluded: sp1n…3xpX 12316→8, FcEA…UVGR 6845→1, 6VAD…QBT5 5148→2, DotU…LXMK 4912→8):

| sender | dust transfers | distinct recipients |
|---|---|---|
| 7Z1X…7CeJ | 5201 | 5008 |
| 6uqx…XSPy | 4388 | 617 |
| DRro…GwEc | 1880 | 1756 |
| AeeT…Jbqj | 768 | 43 |
| 5fLX…tfmD | 637 | 39 |
| 2kwr…o17H | 637 | 39 |
| 6tUt…shDm | 628 | 40 |
| FFqh…E9VG | 468 | 456 |
| 2k5h…pP5y | 332 | 306 |
