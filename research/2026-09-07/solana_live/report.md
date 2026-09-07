# Solana mainnet live scan: 2026-09-07T13:19:41+00:00 to 2026-09-07T14:19:41+00:00 UTC

Slots 445075051 to 445086411 (11353 produced blocks of 11361 slots, 8 skipped, 11353 analyzed), 14,026,271 transactions of which 7,631,908 votes and 6,394,363 non-vote (1,906,581 failed, 29.8%). SOL in-window swap price: first 105.7612, last 104.4154, median 105.0762 (min 104.3765, max 105.7665) from 2341 swaps; Jupiter head price $103.78 at slot 445130138. Generated 2026-09-07T18:28:10+00:00 UTC by `scripts/solana_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

# Onchain, Solana, last hour — 2026-09-07 13:19:41 to 14:19:41 UTC

Slots 445,075,051–445,086,411: 11,353 produced blocks of 11,361 slots (8 skipped), 14,026,271 transactions of which
7,631,908 votes and 6,394,363 non-vote; 1,906,581 non-vote transactions failed (29.8%). That is 3,895 transactions per
second, 1,776 of them non-vote. Collected over the GetBlock tokens in ~2 hours (8.5 GB compact, every block, parent links
and hashes verified), analysed offline by `scripts/solana_scan.py`; `verify` re-derives the headline counts from the raw
blocks with separate code. SOL drifted **$105.76 → $104.42 (−1.3%)** on the in-window swap path (median $105.08). This is
the first Solana window in the same manner as the Ethereum live scans, so several items below are structural rather than
news; the numbers that matter for comparison are the fee, failure and volume composition.

## The interesting things

> **Correction (added by the [interchain study](../interchain/findings.md), same day).** Item 8 says "USDG 8.32%
> on Jupiter Lend"; this report's own rate table and `head_state.json` say jlUSDG pays **5.42%** on $2.92M. The
> table is right. Item 5's unlabelled custodial system is **Relay's Solana depository**: program
> `99vQwtBwYtrqqD9YSXbdum3KBdxPAVxYTaQ3cfnJSrN2`, vault `7uTT8Xi5…`, payout treasury `F7p3dFrj…` — the same
> architecture this repo's Ethereum and Robinhood Chain windows show on those chains the same day.


1. **What Solana's 1,776 non-vote TPS actually are.** Only 16% of non-vote transactions are swaps (1.03M) and 9% are
   transfers. 30% fail. About 22% (~1.4M) are single-instruction *quote posts* by proprietary market makers that move no
   tokens at all: Phoenix Eternal (Ellipsis) 362k txs from 143 payers, the top three of them 78%; HumidiFi 239k (22 payers);
   TesseraV 210k from **one** payer; Scorch 107k (one payer); Quantum 98k; the unlabelled 40-byte poster `W1LD…` 106k and
   33-byte poster `dijk…` 90k (one payer, zero failures); BisonFi, Archer, BisonFi Predict ~60k each. Another ~275k are
   on-chain "nothing to do" checks that log their own verdict: the arbitrage program `9L1q…` logged *"No arb opportunity
   found"* 106,692 times (one payer, 137,831 txs) and the copychain.cc copy-trading program logged *"No profitable buy/sell
   pair was found"* 74,851 times. Machine traffic that never touches a balance is the largest single category of the chain.

2. **Four pump.fun sniper programs produced ~18% of all failures.** `Dhpy…` (139,654 txs, 94% failed), `7JwT…` (81,780,
   99%), `3RWL…` (68,028, 100%) and `BevF…` (62,118, 99%) — four payer wallets each — sent 351,580 transactions of which
   ~342,000 failed, 17.9% of the window's 1.9M failures, for ~3.5 SOL of fees in total (base fee only, no priority). Failed
   transactions paid 64.9 SOL of the 268.9 SOL of non-vote fees (24%); priority fees (233.1 SOL) dwarf base fees (35.8 SOL).

3. **PumpSwap is 70% of DEX volume and the top pairs are self-matched.** Priced DEX volume was $205.2M over 1.03M swaps;
   PumpSwap $144.5M (686k swaps), Raydium CLMM $8.1M, Orca $6.9M, Meteora DLMM $5.8M, Jupiter routes into unlabelled venues
   $5.3M; the largest non-pump pair is Orca SOL/USDC at $4.5M. The seven largest pairs of the hour are all pump tokens
   against SOL ($5.5M–$12.7M each) and their tapes are one-directional: `DkDs…` 11,394 buys vs 51 sells by 1,770 wallets
   (the six busiest at ~220 trades each), `GyKY…` 8,666 buys vs 2 sells from **23 wallets** at ~440 trades each with the
   price up 40%, `AfUe…` 12,997 buys vs 129 sells (six wallets at ~1,100 each). The mechanism, read from the transactions
   (e.g. `2ikJr7YU…`): one transaction, two signers, signer A pays 15.085 SOL and receives 42.59T tokens while signer B sells
   42.66T tokens and receives 15.018 SOL through the same pool (logs `Sell, GetFees, Buy, GetFees`); the operator loses only
   the 0.45% pool fee per round trip. The detector (a second signer whose token and native-SOL legs mirror the trader's)
   flags $86.8M over 91,743 swaps from 8,751 wallet pairs — 42% of all priced volume and 60% of PumpSwap's; the eight
   largest pairs of the hour are 95–100% self-matched.
   Pump.fun paid 695 SOL (~$73k) of cashback in 7,286 claims in the hour, so the volume being farmed is at least
   partly rebated; the operator's net cost is the pool fee minus cashback and creator-fee share.

4. **1,750 token launches in the hour, 804 creators.** Pump.fun 1,276, Meteora Dynamic Bonding Curve 272, Raydium Launchlab
   146, an unlabelled launchpad `6Vo3…` 48; the three busiest creators launched 60, 57 and 49 tokens each. PumpSwap created
   222 pools and the bonding curves turned over 41,236 SOL (~$4.3M). A separate Token-2022 mint-churn bot (`BopT…`, one
   payer, zero priority fee) created and closed 2,880 mints. Same-block sandwiches are essentially absent: 757 buy-buy-sell
   patterns in pump pools, only 3 where the attacker's token position actually closed ($11.6k of victim volume).

5. **An unlabelled custodial deposit system is the busiest retail flow on the chain.** Router program `99vQ…`
   (`DepositToken`/`DepositNative`, Ed25519-verified) fed vault `7uTT8X…` with **$8.80M USDC from 16,560 unique depositors**
   (39,462 deposits), 9,817 SOL from 3,169 senders, plus USDG, USDT, PYUSD and a `…CASH` vanity-mint token, swept in 60
   transactions to treasury `F7p3dF…`, which paid out **$10.17M USDC to 15,203 recipients** (33,867 transfers) and 14,722 SOL
   to 2,737. Its router payer `AgmLJBMD…` is the single largest fee payer on Solana this hour: 63,667 transactions, 14.06 SOL
   (~$1.5k) of priority fees at 1.5M µlamports/CU. The labels registry has no name for it; with ~30k users an hour it is a
   major exchange, prediction market or perps venue and should be identified.

6. **Wallet-cycling clusters — funded, traded, and swept back within minutes.** Six collector hubs received from 531 to
   3,254 unique wallets each and sent everything to one address. Three are exact SOL round trips against a distributor
   that funded the same number of wallets minutes earlier: `62jw…` 533 wallets / 680.1 SOL in 2m20s ← `BMKajGQ4…` (530
   transfers, 680.1 SOL); `ArLh…` 532 / 683.6 SOL ← `2Fs1…` (540, 683.6 SOL); `4QoH…` 531 / 654.1 SOL in **63 seconds** ←
   `C1yb…` (528, 654.1 SOL); the wallets touched pump tokens in between (holder-count and volume farming). Two 3,254-wallet
   clusters ran the same playbook 45 minutes apart — `A1zq…` at 13:25 (928 SOL in 2m19s, the token `3bQJ…pump` dumped by
   4,040 wallets from $0.00197 to $0.0000023, −99.9%) and `AcNh…` at 14:10 (1,238 SOL) — and each sent out **exactly
   396,351.83** tokens afterwards, so this is one automated bundle service. Together the five clusters cycled 8,103 wallets
   and ~4,180 SOL (~$440k); only 361 of the 3,254 `A1zq…` senders were funded inside the window (38 funders), the rest were
   pre-positioned.

7. **Kamino is being spammed, not liquidated.** 2,384 failed flash loans against 73 successful ones ($309k principal);
   `guof…VNk3` alone submitted 2,091 failing flash-borrow → Jupiter → Jupiter Perps transactions and succeeded in none; 184
   liquidation attempts by `bSoL…SpgW`, all failed; marginfi 223 failed flash loans against 104 successful, 3 failed
   liquidations; zero successful liquidations on Kamino, marginfi or Save in the hour.

8. **Rates: SOL earns more than dollars, and dollar yield is dispersed across venues.** Kamino main market SOL 5.01% supply
   / 6.57% borrow at 90% utilisation ($253M supplied, $229M borrowed) — the borrow demand is LST looping: dSOL $236M, jitoSOL
   $99M, jupSOL $52M, hSOL, vSOL sit as collateral at 0–2% utilisation. USDC: Jupiter Lend 4.96% (4.56% + 0.40% rewards, on
   $452M) vs Kamino 3.58% (82% util) vs Save 2.96% (74%); Kamino JLP-market USDC 3.60% at 91%. PYUSD: $251M in Kamino's
   Ethena market at 94% utilisation pays 3.41% vs 1.82% in the main market. USDG 8.32% on Jupiter Lend but only $2.9M;
   JupUSD 6.40% on $58M. Kamino's Ethena market holds $268M of USDe that nobody borrows. For reference the same morning on
   Ethereum: Aave USDC 3.58%, Compound 6.91%, Sky 3.60%.

9. **Stablecoins: $4.87M USDC burned, none minted.** Issuer burns $2.49M — one $2.28M redemption at 14:05:14 and 173k burned
   directly from Binance's USDC routing wallet `41zC…` — plus $2.38M burned through CCTP (134 deposits). PYUSD saw both sides:
   330,940 minted by the Paxos authority and 869,996 burned (570,000 and 299,996). USDG burned 176,059 against 10,826 minted.
   One treasury operator, `CS9a4zj4…`, did most of the PYUSD side: it received $869k by CCTP from Polygon, cycled $3.58M
   USDC, minted 331k and redeemed 300k PYUSD, and moved jlUSDC (Jupiter Lend shares) and Kamino positions; it shares
   counterparties with the $10M USDC that went into Huma (`7s1da8Dd… → 9936VFvg…` at 13:54) and on to a Squads multisig
   at 14:03.

10. **CCTP is balanced and small; one EVM contract takes most of the outflow.** Out $2.38M: Ethereum $1.94M (two transfers
    of $990k and $924k by `D2t2YViD…` at 14:06–14:07), Arbitrum $162k, Avalanche $135k, Polygon $77k, HyperEVM $32k (40
    transfers), an unmapped domain 27 $21k (33 transfers); $2.19M of it went to the same recipient `0x28b5a0e9…cf5d` on
    Ethereum, Arbitrum, Polygon and HyperEVM — a bridge aggregator's receiver. In $2.33M: Aptos $1.44M (two, to relayer
    `HGpYjXi9…`), Polygon $869k (two, `CS9a…`); every inbound was a v2 transfer paid out of the custody account, no mint.
    Twenty times smaller than the $104M CCTP→Arbitrum seen on Ethereum in the morning window.

11. **Exchanges: Binance took in stables and paid out SOL.** Binance hot wallet net +$5.8M (USDC +$5.5M, USDT +$2.9M, SOL
    −$2.5M ≈ 23.6k SOL out; 201 unique depositors confirm the label), and its internal plumbing is visible: routing wallet
    `41zC…` moved $20.9M in / $25.3M out and consolidation wallet `3ADz…` pushed $20.3M USDC, $2.5M USDT and 60.4M PUMP into
    the hot wallet (PUMP arriving from Gate.io and KuCoin). KuCoin −$1.30M, Gate.io −$520k, Coinbase −$466k, Coinbase 2
    +$332k (SOL in, cbBTC out), MEXC −$101k. A CEX–DEX desk, `MfDuWeqS…` (own router program, 4,685 txs), cycled 57k SOL
    and $6.3M USDC through Orca, Raydium CLMM and DLMM and deposited $3.35M USDC and 230k WIF to Binance; it received the
    hour's largest native transfer, 16,783 SOL ($1.75M) from `44P5Ct5J…`.

12. **MEV and spam economics.** Jito tips actually paid (a failed transaction reverts its tip): 36.4 SOL in
    403,497 successful tipping transactions from 11,786 wallets — an order of magnitude below the 233 SOL of priority
    fees; the largest "tipper" by intent, `4pSH…`, attached 14.3 SOL of tips to 4,711 transactions that all failed, and the
    largest paid tipper, `DtvmxrTA…`, paid 1.96 SOL across just 3 transactions. Every
    Jito tip account received ~3,450 unique payers, confirming the labels. Address-poisoning dust: 68,343 transfers from
    226 senders with ≥ 50 each (`6uqx…` 7,180 to 866 recipients, `7Z1X…` 6,916 to 6,658).

## Nothing broke

Pegs held: USDC/USDT/PYUSD/USD1 at $0.9999, USDG $1.0000, USDS $0.9998, JupUSD $0.9996, USDe $1.0000. LSTs trade within
±15 bp of on-chain NAV (at the head read: jitoSOL +9 bp, bSOL +5 bp, jupSOL +15 bp; NAV read from the stake-pool accounts,
which only update at the epoch boundary, so a small positive basis mid-epoch is accrued rewards) — note Sanctum's public
sol-value API is 1.9% below on-chain NAV for every pool and would have shown a spurious 2% premium. Zero liquidations on any lending venue. 8 skipped slots of 11,361; the largest block used 70.0M non-vote compute
units. 446 validators produced blocks; the top producer took 4.0% of them.

## What the Solana lens changes (method notes)

Payer-centric transaction kinds plus per-program "bot shape" columns (unique payers, top-payer share, share of transactions
that move any token, average compute) separate real activity from machine traffic; a trader is the payer or a signer with
both a sold and a bought leg, native SOL folded in. Fan-in/fan-out hubs (many senders, ≤ 2 destinations) surface the
custodial vaults and the wallet-cycling clusters that no label registry would. Two Solana-specific accounting traps were
fixed in-window: tips inside failed transactions are not paid, and CCTP v2 neither mints on receive nor burns through the
v1 discriminators. Volume needs a self-match test before it is quoted.

## Feedback for the quant step

- Identify the custodial system (`99vQ…`/`7uTT8X…`/`F7p3dF…`) and the bridge receiver `0x28b5a0e9…` — verified labels, not
  behaviour. Add the Astralane/other tip accounts (`astrazzn…` was tipped) so MEV tips are not Jito-only.
- Make the self-matched-swap detector a standing metric per venue and token, and net it out of every volume table;
  extend it to same-block (not same-transaction) pairs by the same funder.
- Promote the hub detector into a cluster report: for each collector hub, the funding distributor, the token(s) touched, and
  the net SOL cost per wallet; alert when the same token amount recurs (`396,351.83`).
- Read marginfi bank state on-chain (no public API) so the dollar-yield ladder covers all three big venues, and add Kamino
  borrow caps/utilisation kinks so the SOL 90% utilisation can be interpreted as capacity.
- Collection is bandwidth-bound (~2.7 MB/s); a second GetBlock region or a Helius/Triton endpoint would halve the two hours.

---

## A. Network: throughput, fees, compute, leaders

| metric | value |
|---|---|
| transactions per second (all / non-vote) | 3895 / 1776 |
| failed non-vote transactions | 1,906,581 (29.8%) |
| fees paid by non-vote txs | 268.9 SOL (base 35.8 + priority 233.1); vote fees 38.4 SOL |
| fees paid by failed txs | 64.9 SOL |
| Jito tips (successful txs only; a failed tx reverts its tip) | 36.4 SOL in 403,497 tipping txs (11,786 unique tippers) |
| fee per non-vote tx (median / p90 / p99) | 5418 / 22500 / 493745 lamports |
| compute-unit price (median / p90 / p99, txs setting one) | 16046 / 1000000 / 21600000 µlamports (4,713,604 txs) |
| largest block by non-vote compute units | 69,998,302 |
| versioned (v0, lookup-table) tx share | 69.6% |
| Token-2022 share of token instructions | 21.6% |
| accounts created / token accounts closed | 2,185,630 / 2,080,730 |
| durable-nonce txs | 716,995 |


Per 5 minutes (SOL price = in-window swap median at the bin start):

| start | blocks | tx | non-vote | failed | fees SOL | tips SOL | CU (M) | swaps | DEX volume | of which self-matched | SOL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 13:19 | 949 | 1,186,705 | 550,462 | 29% | 20.3 | 2.9 | 32157 | 89623 | $15.2M | $5.7M | $105.76 |
| 13:24 | 943 | 1,093,791 | 459,849 | 24% | 15.3 | 2.9 | 25110 | 86730 | $15.5M | $6.9M | $105.74 |
| 13:29 | 949 | 1,074,825 | 436,960 | 24% | 16.4 | 1.7 | 23197 | 79211 | $16.4M | $7.3M | $105.71 |
| 13:34 | 944 | 1,155,631 | 521,663 | 33% | 15.9 | 2.8 | 27666 | 78767 | $17.2M | $7.1M | $105.27 |
| 13:39 | 952 | 1,078,052 | 437,975 | 28% | 25.8 | 3.6 | 23691 | 81208 | $16.8M | $7.8M | $105.22 |
| 13:44 | 939 | 1,087,152 | 456,388 | 27% | 24.6 | 2.9 | 26915 | 78494 | $15.9M | $7.0M | $105.11 |
| 13:49 | 952 | 1,164,945 | 524,096 | 32% | 19.5 | 3.4 | 28203 | 88415 | $16.5M | $7.7M | $104.98 |
| 13:54 | 946 | 1,179,473 | 542,670 | 27% | 25.8 | 2.5 | 31537 | 95312 | $16.5M | $7.7M | $105.21 |
| 13:59 | 941 | 1,197,951 | 565,017 | 29% | 26.7 | 4.4 | 32242 | 90509 | $18.1M | $7.1M | $105.09 |
| 14:04 | 950 | 1,331,879 | 693,765 | 37% | 24.8 | 3.8 | 37720 | 89982 | $20.8M | $7.4M | $105.01 |
| 14:09 | 942 | 1,240,106 | 606,440 | 32% | 30.7 | 3.3 | 33173 | 87493 | $19.2M | $8.0M | $104.57 |
| 14:14 | 945 | 1,234,447 | 598,431 | 32% | 23.2 | 2.4 | 31351 | 85057 | $17.2M | $6.9M | $104.57 |
| 14:19 | 1 | 1,314 | 647 | 37% | 0.0 | 0.0 | 30 | 106 | $14k | $4455 | $104.42 |


Leaders: 446 validators produced blocks. Most blocks: Fd7b…69Nk (456), HEL1…e2TU (436), DRpb…21hy (301), JUPi…1h4b (284), CAo1…Sve4 (276), C8Be…JP1k (272), E1r4…dxHL (268), 9eGr…8FoY (228). Skipped slots by leader: SSmB…oQLY (4), xLab…1ARE (4). Most Jito tips collected: Btsm…DAaH (2.1 SOL), 9eGr…8FoY (1.7 SOL), GnC3…qta6 (1.6 SOL), DRpb…21hy (1.3 SOL), E1r4…dxHL (1.3 SOL), Fd7b…69Nk (1.2 SOL).


Jito tip accounts (behavioural check — many unique payers confirms the label):

| tip account | tips SOL | unique payers |
|---|---|---|
| ADuU…DcEt | 5.07 | 3347 |
| 96gY…rZU5 | 5.00 | 3342 |
| 3AVi…Z6jT | 4.76 | 3320 |
| HFqU…7gRe | 4.70 | 3342 |
| DttW…2KRL | 4.54 | 3259 |
| Cw8C…vLkY | 4.43 | 3259 |
| DfXy…DXjh | 4.26 | 3380 |
| ADaU…aS49 | 3.65 | 3312 |


Top tippers:

| payer | label | tips SOL | tip txs |
|---|---|---|---|
| Dtvm…MVKx |  | 1.964 | 3 |
| 5RzV…tFX7 |  | 1.180 | 20 |
| 8Uds…zkH6 |  | 1.038 | 201 |
| 64fc…QzQw |  | 1.038 | 484 |
| UUAh…V8yd |  | 0.812 | 281 |
| MRiY…oCsa |  | 0.812 | 38 |
| BGT8…C9fV |  | 0.804 | 344 |
| 2Fas…YgN4 |  | 0.781 | 115 |
| 75am…pwHP |  | 0.733 | 329 |
| 7dGr…uuUu |  | 0.548 | 81 |
| MfDu…GVWa | CEX-DEX market-making desk (own router GKyb…, Whirlpool/Raydium/DLMM; deposits to Binance via 3ADz…) | 0.528 | 2689 |
| 5MtJ…RJaP |  | 0.508 | 216 |
| HQ7r…Ucg3 |  | 0.410 | 4 |
| ASki…yNEG |  | 0.319 | 121 |
| FkaL…3MZp |  | 0.283 | 230 |


## B. Programs and transaction kinds

Transaction kinds (payer-centric classification: `swap` = a DEX/aggregator program with a sold and a bought leg; `pump_launch` = pump.fun `create`; `transfer` = only system/token programs with balances moving):

| kind | txs | share | fees SOL |
|---|---|---|---|
| failed | 1,906,581 | 29.8% | 64.89 |
| other | 1,486,417 | 23.2% | 19.68 |
| dex_other | 1,294,642 | 20.2% | 34.52 |
| swap | 1,030,907 | 16.1% | 125.48 |
| transfer | 579,445 | 9.1% | 9.32 |
| prediction | 56,791 | 0.9% | 0.29 |
| system_only | 18,820 | 0.3% | 13.96 |
| staking | 10,991 | 0.2% | 0.07 |
| perps | 5,006 | 0.1% | 0.05 |
| lending | 2,250 | 0.0% | 0.04 |
| launch | 1,750 | 0.0% | 0.55 |
| protocol | 500 | 0.0% | 0.02 |
| cctp | 199 | 0.0% | 0.01 |
| bridge | 39 | 0.0% | 0.00 |
| vault | 25 | 0.0% | 0.00 |


Top programs by transactions (main program = first non-system top-level program). `payers` = unique fee payers and the share of the top one — a program with one or two payers is a private bot; `tokens move` = share of its txs where any token balance changes (near zero = quote posting / opportunity checks, not trades); instruction names from Anchor logs when the tx has one main program:

| program | label | txs | failed | swaps | payers (top share) | tokens move | avg CU | avg keys | nonce txs | fees SOL | tips SOL | top instructions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pAMM…fXEA | Pump.fun Amm | 1,150,562 | 11% | 641,177 | 171562 (1%) | 88% | 104,676 | 25 | 2,848 | 40.13 | 2.31 | GetFees 1093738, TransferChecked 803587, Sell 656115 |
| Etrn…jWih | Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates | 362,138 | 22% | 0 | 143 (50%) | 0% | 41,725 | 7 | 24,866 | 1.92 | 0.06 |  |
| JUP6…TaV4 | Jupiter Aggregator v6 | 328,366 | 65% | 64,241 | 16783 (9%) | 35% | 139,529 | 32 | 107,271 | 15.88 | 2.87 | RouteV2 124075, Route 88200, TransferChecked 74291 |
| Comp…1111 | Compute Budget | 279,443 | 2% | 0 | 56048 (14%) | 44% | 11,886 | 7 | 76 | 19.12 | 7.74 |  |
| 9H6t…q6Rp | HumidiFi | 239,076 | 28% | 0 | 22 (12%) | 0% | 362 | 5 | 1 | 2.37 | 0.00 |  |
| Tess…GLQH | TesseraV | 210,243 | 31% | 0 | 1 (100%) | 0% | 461 | 4 | 0 | 1.12 | 0.02 |  |
| 1111…1111 | System Program | 205,018 | 0% | 0 | 59463 (6%) | 4% | 1,401 | 5 | 18,087 | 2.58 | 2.67 |  |
| Dhpy…84HY | pump.fun sniper program (94% failed, 4 payers) | 139,654 | 94% | 2 | 4 (25%) | 0% | 4,674 | 60 | 0 | 1.55 | 0.00 | ExtendLookupTable 310, CreateLookupTable 310, InitializeAccount3 310 |
| 9L1q…qqDF | arbitrage bot program (logs "No arb opportunity found"; 1 payer) | 137,824 | 22% | 0 | 1 (100%) | 0% | 38,535 | 53 | 27,344 | 1.32 | 0.20 | Swap2 116, GetFees 98, Swap 95 |
| Pris…F7qv | copychain.cc copy-trading bot program | 136,317 | 55% | 0 | 8 (46%) | 0% | 44,698 | 47 | 128,993 | 1.22 | 0.26 | InitializeAccount3 4757, GetAccountDataSize 4757, InitializeImmutableOwner 4757 |
| ojh1…orch | Scorch | 106,523 | 47% | 0 | 1 (100%) | 0% | 798 | 5 | 0 | 0.78 | 0.00 |  |
| W1LD…1bWR | unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers) | 106,140 | 20% | 0 | 24 (10%) | 0% | 387 | 5 | 10,880 | 0.55 | 0.01 |  |
| NA24…HTUV |  | 101,067 | 59% | 1 | 12 (22%) | 0% | 101,178 | 48 | 77,540 | 1.41 | 0.08 | InitializeAccount3 2377, GetAccountDataSize 2377, InitializeImmutableOwner 2377 |
| QuaN…bBDv | Quantum | 98,374 | 0% | 0 | 6 (19%) | 0% | 623 | 5 | 0 | 0.62 | 0.04 |  |
| dijk…1mBu | unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer) | 89,936 | 0% | 0 | 1 (100%) | 0% | 519 | 6 | 59,116 | 0.46 | 0.00 |  |
| cpam…1sGG | Meteora DAMM v2 | 82,605 | 31% | 51,847 | 3309 (0%) | 69% | 35,155 | 16 | 1,284 | 2.35 | 0.24 | TransferChecked 49162, Swap 43998, Swap2 37583 |
| 7JwT…94ZG | pump.fun sniper program (99% failed buys, 4 payers) | 81,780 | 99% | 1 | 4 (30%) | 0% | 1,391 | 47 | 0 | 0.56 | 0.00 |  |
| 6EF8…wF6P | Pump.fun | 78,243 | 27% | 37,865 | 9995 (1%) | 55% | 59,636 | 20 | 8,568 | 33.75 | 4.58 | GetFees 43765, TransferChecked 40830, Sell 28225 |
| Hd7c…UH5w | unlabelled bot program (26 accounts, pump.fun Sell/GetFees inner calls, 3 payers) | 76,629 | 22% | 249 | 3 (73%) | 0% | 19,907 | 27 | 6,973 | 0.39 | 0.00 | GetFees 9991, Sell 9866, TransferChecked 245 |
| 6MWV…QEGh |  | 75,388 | 0% | 0 | 3 (83%) | 0% | 40,950 | 56 | 0 | 0.84 | 0.01 | TransferChecked 31, GetFees 30, Swap2 26 |
| BiSo…Uypi | BisonFi | 70,093 | 22% | 0 | 3 (59%) | 0% | 462 | 7 | 0 | 0.46 | 0.01 |  |
| 3RWL…v3eX |  | 68,028 | 100% | 0 | 4 (25%) | 0% | 1,622 | 57 | 309 | 0.62 | 0.00 | InitializeAccount3 309 |
| BevF…56A3 |  | 62,118 | 99% | 1 | 4 (25%) | 0% | 1,597 | 57 | 310 | 0.71 | 0.00 | InitializeAccount3 310, GetFees 1, BuyExactSolIn 1 |
| 2DNb…Ksbh | BisonFi Predict | 61,264 | 9% | 0 | 2 (100%) | 0% | 650 | 4 | 0 | 0.31 | 0.00 | InitializeAccount3 74, GetAccountDataSize 74, InitializeImmutableOwner 74 |
| Arch…PMhy | Archer | 59,588 | 15% | 0 | 3 (62%) | 0% | 3,187 | 7 | 0 | 0.33 | 0.00 | TransferChecked 5 |
| FLAS…txB9 | pump.fun trading bot program (Sell/GetFees inner calls) | 54,399 | 6% | 46,940 | 5802 (1%) | 94% | 86,156 | 31 | 4,627 | 12.51 | 0.04 | TransferChecked 49342, GetFees 40044, Sell 19402 |
| DDsn…AMEo |  | 52,953 | 25% | 8 | 3 (97%) | 1% | 112,253 | 58 | 1,801 | 1.02 | 0.21 | TransferChecked 300, Swap 294, Swap2 171 |
| dbci…MaqN | Dynamic Bonding Curve | 50,926 | 28% | 33,327 | 3699 (1%) | 72% | 50,596 | 17 | 150 | 0.49 | 0.02 | Swap2 48113, TransferChecked 32986, InitializeAccount3 4758 |
| SoLS…AVk4 |  | 49,728 | 25% | 3 | 1 (100%) | 0% | 111,976 | 58 | 0 | 0.84 | 0.20 | TransferChecked 110, GetFees 88, Swap2 61 |
| BYdq…vZtw |  | 46,769 | 3% | 142 | 1 (100%) | 0% | 29,153 | 40 | 0 | 0.23 | 0.00 | GetFees 142, TransferChecked 138, BuyExactQuoteIn 71 |
| 99vQ…SrN2 | deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) | 45,788 | 1% | 0 | 3401 (81%) | 87% | 25,883 | 11 | 0 | 2.89 | 0.00 | DepositToken 40192, DepositNative 5481, TransferChecked 465 |
| ATok…8knL | Associated Token Account | 44,908 | 1% | 0 | 3626 (17%) | 88% | 48,099 | 12 | 0 | 0.43 | 0.00 |  |
| 3QUn…EUoN |  | 40,802 | 0% | 1 | 1 (100%) | 0% | 19,193 | 60 | 0 | 0.47 | 0.07 | GetFees 65, TransferChecked 65, Swap2 47 |
| DF1o…7QBH |  | 40,794 | 8% | 30,836 | 5478 (51%) | 92% | 219,958 | 39 | 2 | 12.46 | 0.08 | Swap 31328, TransferChecked 24623, Swap2 11358 |
| Toke…xuEb | Token-2022 | 39,997 | 4% | 0 | 13728 (4%) | 33% | 10,229 | 10 | 0 | 0.57 | 0.00 |  |
| B72M…Rdht | BinaryFi | 38,911 | 5% | 0 | 2 (100%) | 0% | 1,049 | 13 | 23,223 | 0.22 | 0.00 |  |
| DZNT…tJbY |  | 38,251 | 21% | 0 | 1 (100%) | 0% | 418 | 7 | 0 | 0.21 | 0.01 |  |
| Db8h…BEwH |  | 36,396 | 100% | 0 | 1 (100%) | 0% | 1,358 | 48 | 0 | 0.25 | 0.00 |  |
| LBUZ…Pwxo | Meteora DLMM | 36,228 | 11% | 10,474 | 2328 (10%) | 82% | 222,463 | 20 | 600 | 15.03 | 0.61 | TransferChecked 9643, ClaimFee2 8626, RemoveLiquidityByRange2 7719 |
| naeb…2yCV |  | 35,784 | 100% | 1 | 3 (35%) | 0% | 1,042 | 46 | 0 | 0.41 | 0.00 |  |


Token launches (a new mint initialised inside a launchpad transaction): 1750 in the window by 804 creators — Pump.fun 1276, Dynamic Bonding Curve 272, Raydium Launchlab 146, unlabelled launchpad (new mints + trades, tied to bundler wallet 6pSPqc…) 48, T1TA…XvGT 4, 24Uq…pyTi 4. New mints outside launchpads (CLMM position NFTs, LP tokens, other): Token-2022 mint churn bot (InitializeMint2 + close cycles, 1 payer, zero priority) 2880, Pump.fun Amm 178, prediction market (outcome tokens, BurnWorthlessOutcome) 170, Compute Budget 115, Whirlpool 113, Raydium CLMM 89.


`other` (no DEX, lending, bridge or transfer signature) is dominated by: Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates 281,376, arbitrage bot program (logs "No arb opportunity found"; 1 payer) 106,675, unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer) 89,936, unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers) 84,742, 6MWV…QEGh 75,352, copychain.cc copy-trading bot program 61,306, unlabelled bot program (26 accounts, pump.fun Sell/GetFees inner calls, 3 payers) 59,845, deposit router (DepositToken/DepositNative into vault 7uTT8Xi5…) 45,399. `dex_other` (a DEX program is invoked but no trader has a sold and a bought leg — quote posts, fee collection, failed-in-effect routes): Pump.fun Amm 382,910, HumidiFi 171,347, TesseraV 145,264, Quantum 97,941, Scorch 56,320, BisonFi 54,539, Archer 50,804, Jupiter Aggregator v6 49,816.


Top payers by transactions (bots):

| payer | label | txs | failed | fees SOL | tips SOL |
|---|---|---|---|---|---|
| FVnv…pwMg |  | 210,243 | 64979 | 1.12 | 0.02 |
| sp1n…3xpX |  | 180,840 | 43904 | 0.91 | 0.02 |
| AjkD…qu4b |  | 137,835 | 30963 | 1.32 | 0.20 |
| 83TS…ZgKC |  | 121,118 | 50203 | 1.10 | 0.08 |
| FTp1…Er5f |  | 89,936 | 0 | 0.46 | 0.00 |
| stnk…aAKr |  | 69,656 | 12389 | 0.35 | 0.01 |
| AgmL…zN51 |  | 63,667 | 486 | 14.06 | 0.00 |
| 3276…wQS6 |  | 63,222 | 32261 | 0.56 | 0.13 |
| 8TPW…UaHr |  | 62,839 | 5 | 0.68 | 0.00 |
| 7TRG…qkKE |  | 61,034 | 5710 | 0.30 | 0.00 |
| FfAJ…MG9t |  | 57,742 | 16094 | 0.91 | 0.21 |
| CFgk…Q9WH |  | 56,107 | 4984 | 0.28 | 0.00 |
| A7FM…aaVE |  | 51,147 | 13206 | 0.83 | 0.21 |
| 3ct4…fh5J |  | 47,236 | 1868 | 0.24 | 0.00 |
| 3Kvs…CSAZ |  | 42,901 | 17471 | 0.36 | 0.05 |
| Gs7a…aj6y |  | 41,269 | 11169 | 0.25 | 0.00 |
| DsCJ…fpx9 |  | 40,802 | 0 | 0.47 | 0.07 |
| F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 39,292 | 11 | 0.47 | 0.00 |
| HCar…c3fT |  | 38,893 | 1866 | 0.22 | 0.00 |
| DotU…LXMK |  | 38,251 | 7959 | 0.21 | 0.01 |


Top payers by fees + tips:

| payer | label | txs | failed | fees SOL | tips SOL |
|---|---|---|---|---|---|
| AgmL…zN51 |  | 63,667 | 486 | 14.06 | 0.00 |
| UUAh…V8yd |  | 18,654 | 16188 | 5.92 | 0.81 |
| MfDu…GVWa | CEX-DEX market-making desk (own router GKyb…, Whirlpool/Raydium/DLMM; deposits to Binance via 3ADz…) | 10,017 | 5379 | 5.40 | 0.53 |
| 5vjm…7uvq |  | 16 | 0 | 5.91 | 0.00 |
| 9EwQ…qDj4 |  | 30 | 0 | 4.23 | 0.06 |
| 5SSQ…v4BZ |  | 28 | 0 | 4.25 | 0.00 |
| 4aPp…qAmo |  | 1 | 1 | 4.10 | 0.00 |
| Dtvm…MVKx |  | 1,449 | 1298 | 1.50 | 1.96 |
| 9cU2…SHwX |  | 1 | 0 | 3.43 | 0.00 |
| 3rBp…9SAC |  | 1 | 0 | 3.32 | 0.00 |
| 2CQg…ctFG |  | 405 | 258 | 3.00 | 0.27 |
| MRiY…oCsa |  | 1,179 | 638 | 2.37 | 0.81 |
| 7dGr…uuUu |  | 3,718 | 3350 | 2.05 | 0.55 |
| E4Ez…TKBz |  | 21 | 6 | 2.53 | 0.00 |
| gtfo…CgFL |  | 20 | 1 | 2.08 | 0.00 |
| 5t4T…Ds1p |  | 25 | 0 | 2.06 | 0.00 |
| B2zY…quK7 |  | 33 | 3 | 2.00 | 0.00 |
| gtag…WNdd |  | 2,325 | 1942 | 1.84 | 0.00 |
| 8NQ3…eEQr |  | 2,310 | 2091 | 1.82 | 0.00 |
| 66Pb…FNjD |  | 34 | 0 | 1.71 | 0.00 |


## C. DEX: volume by venue, pairs, implied prices, largest swaps, sandwiches, launches

Priced volume $205.2M over 1,025,657 swaps (5,250 swaps between unpriced tokens are excluded). Volume = the larger priced leg of the payer; a swap that touches several venues is attributed to `multi`.

| venue | volume | swaps | unpriced swaps |
|---|---|---|---|
| Pump.fun Amm | $144.5M | 686,420 | 582 |
| Raydium CLMM | $8.1M | 10,705 | 567 |
| Whirlpool | $6.9M | 7,465 | 17 |
| Meteora DLMM | $5.8M | 19,363 | 85 |
| aggregator-only | $5.3M | 136,953 | 304 |
| BisonFi | $3.4M | 10,481 | 0 |
| Quantum | $2.3M | 6,689 | 0 |
| GoonFi V2 | $1.4M | 986 | 3 |
| Raydium | $1.2M | 6,899 | 20 |
| HumidiFi | $1.1M | 3,220 | 1 |
| Meteora DAMM v2 | $942k | 53,415 | 996 |
| TesseraV | $933k | 1,521 | 2 |
| multi: AlphaQ+Manifest+Whirlpool | $910k | 30 | 0 |
| multi: AlphaQ+Manifest | $904k | 391 | 1 |
| Manifest | $798k | 757 | 0 |
| multi: Meteora DLMM+TesseraV+Whirlpool | $540k | 95 | 5 |
| ZeroFi | $537k | 1,219 | 0 |
| multi: Meteora DLMM+Pump.fun Amm | $510k | 855 | 235 |
| multi: Meteora DLMM+Raydium CP | $457k | 3,921 | 65 |
| multi: Meteora DLMM+Pump.fun Amm+TesseraV | $398k | 110 | 3 |
| multi: Raydium CP+Whirlpool | $392k | 4,117 | 14 |
| AlphaQ | $383k | 1,240 | 2 |
| multi: TesseraV+ZeroFi | $351k | 12 | 0 |
| multi: Meteora DLMM+Whirlpool | $324k | 595 | 43 |
| PancakeSwap | $310k | 1,335 | 0 |


Volume routed through aggregators (counted once per swap, overlapping with the venue table): Jupiter Aggregator v6 $19.2M


Self-matched swaps (one transaction, two signers: the second signer's token and native-SOL legs mirror the trader's — a buy and a sell of the same token by the same operator inside one transaction, i.e. wash volume): $86.8M over 91,743 swaps from 8,751 wallet pairs, 42.3% of all priced volume.

| venue | self-matched volume | swaps | share of venue volume |
|---|---|---|---|
| Pump.fun Amm | $86.8M | 91,726 | 60% |
| multi: BisonFi+Pump.fun Amm+Raydium CLMM+Whirlpool | $2.00 | 2 | 0% |
| multi: HumidiFi+Pump.fun Amm+Raydium CP | $2.00 | 2 | 0% |
| Meteora DLMM | $1.00 | 1 | 0% |
| TesseraV | $1.00 | 1 | 0% |
| multi: GoonFi V2+Pump.fun Amm | $1.00 | 1 | 0% |
| BisonFi | $1.00 | 1 | 0% |
| multi: Meteora DLMM+Pump.fun Amm+Quantum+Raydium CP | $1.00 | 1 | 100% |


| token | self-matched volume | swaps |
|---|---|---|
| DkDs…1n2M | $12.6M | 9,643 |
| GyKY…mApJ | $11.9M | 7,842 |
| AfUe…Jb5p | $9.8M | 10,648 |
| 5dYh…ftag | $7.7M | 7,481 |
| Bii2…SAwR | $6.9M | 6,705 |
| Gzpt…DyGN | $5.6M | 6,109 |
| 3Sdg…9nsq | $5.5M | 5,466 |
| 7UF1…5y14 | $4.2M | 4,509 |
| DiSr…BxVL | $3.9M | 8,107 |
| Htby…VGte | $3.8M | 3,666 |
| 9t7D…2jWf | $3.5M | 3,431 |
| DP3p…Nzai | $2.5M | 4,887 |


Top pairs:

| venue | pair | volume | swaps |
|---|---|---|---|
| Pump.fun Amm | DkDs…1n2M / SOL | $12.7M | 11373 |
| Pump.fun Amm | GyKY…mApJ / SOL | $11.9M | 8663 |
| Pump.fun Amm | AfUe…Jb5p / SOL | $9.8M | 10648 |
| Pump.fun Amm | 5dYh…ftag / SOL | $7.7M | 7973 |
| Pump.fun Amm | Bii2…SAwR / SOL | $6.9M | 6710 |
| Pump.fun Amm | Gzpt…DyGN / SOL | $5.7M | 7354 |
| Pump.fun Amm | 3Sdg…9nsq / SOL | $5.5M | 5476 |
| Whirlpool | SOL / USDC | $4.5M | 1263 |
| Pump.fun Amm | 7UF1…5y14 / SOL | $4.3M | 4558 |
| Pump.fun Amm | DiSr…BxVL / SOL | $3.9M | 8651 |
| Pump.fun Amm | Htby…VGte / SOL | $3.9M | 3745 |
| Pump.fun Amm | 9t7D…2jWf / SOL | $3.5M | 3435 |
| BisonFi | SOL / USDC | $3.3M | 9743 |
| Meteora DLMM | SOL / USDC | $3.1M | 795 |
| Pump.fun Amm | DP3p…Nzai / SOL | $2.5M | 5223 |
| Quantum | SOL / USDC | $2.2M | 6579 |
| Pump.fun Amm | FWNZ…3uxM / SOL | $2.2M | 3414 |
| Pump.fun Amm | 5vXi…AA73 / SOL | $2.2M | 2904 |
| Pump.fun Amm | BCT6…4xZi / SOL | $2.1M | 9131 |
| Pump.fun Amm | 773j…ceBJ / SOL | $2.0M | 7835 |
| Pump.fun Amm | BqUC…fjNS / SOL | $1.9M | 5833 |
| Pump.fun Amm | SOL / yheF…wCx2 | $1.9M | 7466 |
| Pump.fun Amm | FVNB…CgRS / SOL | $1.8M | 11695 |
| Pump.fun Amm | DZjS…grPY / SOL | $1.8M | 8326 |
| Pump.fun Amm | BoiK…csiv / SOL | $1.7M | 10541 |
| Pump.fun Amm | Bh2g…6FGn / SOL | $1.7M | 4957 |
| Pump.fun Amm | 7f36…LVBT / SOL | $1.3M | 5095 |
| Pump.fun Amm | 4WBk…quPq / SOL | $1.3M | 5287 |
| Pump.fun Amm | FzCT…DxuQ / SOL | $1.2M | 9599 |
| Pump.fun Amm | 8gCc…RG35 / SOL | $1.2M | 7300 |


Implied prices from single-pair swaps against a priced leg (median, min–max across the window):

| token | median | min | max | swaps | volume |
|---|---|---|---|---|---|
| USDC | $1.00003 | $0.0004978 | $3.5e+08 | 34579 | $25.9M |
| SOL | $105.023 | $0.0003153 | $1.441e+04 | 29278 | $20.9M |
| ? | $0.000128608 | $2.755e-05 | $0.0001596 | 9657 | $12.7M |
| ? | $4.38371e-05 | $3.693e-05 | $5.216e-05 | 8266 | $11.9M |
| ? | $2.61769e-05 | $2.285e-05 | $3.104e-05 | 10648 | $9.8M |
| ? | $1.99608e-05 | $1.492e-05 | $2.51e-05 | 7481 | $7.7M |
| ? | $8.33994e-05 | $6.49e-05 | $9.801e-05 | 6709 | $6.9M |
| ? | $3.20114e-05 | $2.711e-05 | $3.834e-05 | 6187 | $5.6M |
| ? | $1.88444e-05 | $1.71e-05 | $2.046e-05 | 5468 | $5.5M |
| ? | $0.000167808 | $0.0001494 | $0.0002387 | 4547 | $4.3M |
| ? | $0.00035345 | $5.005e-05 | $0.0005002 | 7444 | $3.9M |
| ? | $4.08762e-06 | $9.802e-07 | $4.772e-06 | 3701 | $3.9M |
| USDT | $0.999962 | $0.9571 | $1450 | 5583 | $3.6M |
| ? | $3.19986e-05 | $2.498e-05 | $4.177e-05 | 3431 | $3.5M |
| ? | $0.000287471 | $5.041e-05 | $0.0004199 | 4545 | $2.5M |
| ? | $0.000172184 | $0.0001564 | $0.0001884 | 3405 | $2.2M |
| ? | $7.64115e-05 | $5.415e-05 | $9.366e-05 | 2470 | $2.2M |
| ? | $0.112597 | $0.104 | $31.7 | 1883 | $2.1M |
| ? | $2.33187e-05 | $9.285e-06 | $3.656e-05 | 8859 | $2.1M |
| ? | $3.33081e-05 | $7.826e-06 | $0.0001014 | 7687 | $2.0M |
| ? | $4.52227e-05 | $1.577e-05 | $0.000124 | 5738 | $1.9M |
| ? | $0.000383053 | $0.0002254 | $0.0004809 | 7337 | $1.9M |
| ? | $5.57899e-05 | $1.07e-05 | $0.0001607 | 11002 | $1.8M |
| ? | $4.70946e-05 | $1.179e-05 | $0.0001572 | 7038 | $1.8M |
| ? | $7.09215e-05 | $9.093e-06 | $0.0001759 | 10042 | $1.7M |
| ? | $4.02107e-05 | $2.021e-05 | $0.0001003 | 4850 | $1.7M |
| ? | $0.00437822 | $0.00425 | $0.004566 | 2481 | $1.5M |
| ? | $2.42049e-05 | $9.482e-06 | $7.959e-05 | 4946 | $1.3M |
| ? | $3.22824e-05 | $1.485e-05 | $8.4e-05 | 5176 | $1.3M |
| PYUSD | $1.00002 | $1.66e-10 | $1.01 | 151 | $1.3M |


Largest swaps:

| time | venue | payer | sold | bought | value | tip SOL |
|---|---|---|---|---|---|---|
| 13:19:54 | multi: TesseraV+ZeroFi | 7S6s…HmQD | 3312 SOL | 350.0k USDC | $350k | 0.0000 |
| 13:44:28 | multi: AlphaQ+Manifest+Whirlpool | CS9a…RRWe | 300.0k USDC | raw 253.85B AvZZ…ZeUj | $300k | 0.0001 |
| 14:12:27 | multi: AlphaQ+Manifest+Stableswap | CS9a…RRWe | 300.0k USDC | 300.0k PYUSD | $300k | 0.0001 |
| 13:42:36 | Raydium | 4uNQ…8BWt | 123.8k USDC, 1174 SOL | raw 1085.26B 8HoQ…byvu | $247k | 0.0000 |
| 14:12:16 | Pump.fun Amm | 5py3…uGfs | raw 126883.76B 32sw…UcSi | raw 10716191.63B 3Sdg…9nsq, 2074 SOL | $217k | 0.0000 |
| 13:45:41 | Manifest | 5edL…Gjgr | 199.9k PYUSD | 199.9k USDC | $200k | 0.0000 |
| 14:08:11 | Pump.fun Amm | 7gcs…ckis | 1900 SOL | raw 197938.33B 7G4C…pump | $199k | 0.0000 |
| 13:46:22 | Pump.fun Amm | FzD1…wMBM | raw 19775.63B q8nz…pump | 1834 SOL | $193k | 0.0000 |
| 13:57:51 | multi: AlphaQ+Manifest | CS9a…RRWe | 190.0k PYUSD | 190.0k USDC | $190k | 0.0001 |
| 13:47:35 | Pump.fun Amm | DBca…RWoT | raw 414326.44B 7wej…pump | 1788 SOL | $188k | 0.0000 |
| 14:11:15 | Pump.fun Amm | BFwu…E6NY | 1750 SOL | raw 197207.48B 9JmJ…pump | $183k | 0.0000 |
| 14:01:40 | multi: GoonFi V2+Meteora DLMM+Raydium CLMM+TesseraV | AgmL…zN51 | 165.3k USDC | raw 1028965.89B HcRL…DeJR | $165k | 0.0000 |
| 13:30:07 | Pump.fun Amm | HUqc…73un | 1550 SOL | raw 196021.13B wgKH…pump | $164k | 0.0000 |
| 13:44:29 | Pump.fun Amm | 6QXS…zbdW | 1500 SOL | raw 195678.17B EZUT…pump | $158k | 0.0000 |
| 14:17:52 | Pump.fun Amm | 5DqK…a72Y | 1428 SOL | raw 195144.51B bFYY…pump | $149k | 0.0000 |
| 14:04:23 | Pump.fun Amm | Gyxy…L6Bj | raw 9920.00B QLVo…pump | 1347 SOL | $141k | 0.0000 |
| 13:59:11 | multi: Manifest+Stabble Stable Swap | CS9a…RRWe | 140.0k PYUSD | 140.0k USDC | $140k | 0.0001 |
| 13:53:40 | Pump.fun Amm | 9QvB…nMuL | raw 22583.18B 4bf5…hdC3 | raw 758378.95B FWNZ…3uxM, 1264 SOL | $133k | 0.0000 |
| 14:00:58 | Pump.fun Amm | 2kuu…ufwa | raw 12002.20B iqca…pump | 1227 SOL | $129k | 0.0000 |
| 14:00:49 | Pump.fun Amm | JATR…2jB6 | raw 12100.01B W5ph…pump | 1176 SOL | $124k | 0.0000 |
| 14:08:08 | multi: GoonFi V2+HumidiFi | AgmL…zN51 | 122.1k USDC | raw 1399.88B 98sM…Mh5g | $122k | 0.0000 |
| 14:17:14 | multi: GoonFi V2+HumidiFi | AgmL…zN51 | raw 1400.17B 98sM…Mh5g | 122.1k USDC | $122k | 0.0000 |
| 13:28:08 | multi: AlphaQ+Manifest+Raydium CLMM | 6HNV…3Gmi | 110.7k USDG | raw 96833.90B 5Y8N…cxp5 | $111k | 0.0000 |
| 14:05:06 | Pump.fun Amm | 9ugN…iF3j | raw 9901.89B Nj2a…pump | 1017 SOL | $107k | 0.0000 |
| 14:02:39 | Pump.fun Amm | 8hyD…9Qqt | 1006 SOL | raw 190603.85B 8uyF…pump | $106k | 0.0000 |


Same-block sandwich pattern (trader A buys, another trader buys the same token through the same pool, A sells — all in one block): 757 pattern matches, of which 3 closed the token position within 10% (the true sandwich shape; the rest are coincidental buy-buy-sell sequences in busy pump pools). Confirmed-shape victim volume $12k.

| attacker | closed sandwiches | PnL (SOL+stable legs) |
|---|---|---|
| DULT…knL8 | 5 | $16.65 |
| 3ct4…fh5J | 3 | $1.48 |
| 3N1K…AdiS | 3 | $12.62 |
| 9ZrJ…bERu | 3 | $0.37 |
| 7Mpf…XKm6 | 2 | $7.10 |
| 4GcC…HGfV | 2 | -$0.84 |
| 4vWg…NAux | 2 | $0.30 |
| Aceu…XBSS | 2 | $8.02 |
| 9mcn…mcdb | 2 | -$0.15 |
| 4EPq…8hzq | 2 | $1.82 |


| time | token | attacker | victim | victim size | front size | attacker PnL | closed | tips SOL |
|---|---|---|---|---|---|---|---|---|
| 13:38:21 | BqUC…fjNS | 7WpH…kjjz | EQNo…jdLx | $603 | $119 | -$6.62 | yes | 0.0 |
| 14:07:43 | 7f36…LVBT | Ahph…RMbC | GyzR…FxCo | $539 | $373 | -$54.86 | yes | 0.0 |
| 13:40:28 | BqUC…fjNS | 5PH8…Xdt8 | 7RXL…QMJN | $424 | $171 | -$9.08 | yes | 0.0 |
| 14:17:28 | E1jY…r1CQ | CCJV…JurL | 4mdM…Z5q5 | $1055 | $86.00 | $71.58 |  | 0.0 |
| 13:35:11 | BnUq…kyr7 | 33R1…oZiC | 5Xz9…Fasi | $704 | $291 | $599 |  | 0.0 |
| 14:08:29 | 7f36…LVBT | bwus…WnNZ | 4FUz…HQzw | $622 | $215 | $57.18 |  | 0.0 |
| 13:30:47 | BcGV…pump | 8iVc…2Jze | GtsZ…GNWy | $621 | $635 | -$511 |  | 0.0 |
| 13:58:27 | Bh2g…6FGn | 3qS6…TnxL | 7RXL…QMJN | $606 | $257 | $154 |  | 0.0 |
| 14:14:05 | 2XJ4…4pWW | 4wkz…g9un | C1qy…vezC | $606 | $418 | -$367 |  | 0.0 |
| 14:08:01 | Bh2g…6FGn | EhXu…LNAE | 451s…gypz | $525 | $395 | $135 |  | 0.0 |
| 13:53:49 | 7f36…LVBT | 6YNF…WJec | 57YY…Ph9y | $519 | $18.00 | $341 |  | 0.0 |
| 14:00:46 | BCT6…4xZi | 9oQ2…QwnR | CUdp…tneG | $519 | $351 | -$71.90 |  | 0.0 |


Pump.fun (bonding curve + PumpSwap AMM): ok 1261006, failed 477683, launches 1324, pumpswap_pools_created 222, migrations 8. Bonding-curve SOL turnover 41235.9 SOL (buys 22579.7, sells 18656.3); PumpSwap trader SOL legs 1375266.4 SOL. Cashback claims: 7,286 txs, 695.04 SOL received. 626 unique launch creators; most active: VygS…Zg4R (57), 74fH…87Y4 (49), Amjv…praL (31), 3ph9…ioVA (22), FWkp…hJST (17). Instruction mix: Sell 790979, BuyExactQuoteIn 408961, Buy 318437, SellV2 19070, BuyExactQuoteInV2 15224, BondingCurveV3 11016, BuyExactSolIn 10600, ClaimCashback 6460, BuyV2 4941, SellBondingCurvePercentage 3408, SellPumpSwapPercentage 2295, ClaimCashbackV2 2086.


## D. Lending: rates at head, events in window


Kamino SOL/BTC Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| SOL | 4.96% | 6.51% | 90.3% | $252.7M | $228.1M |
| dSOL | 0.00% | 1.61% | 0.0% | $235.2M | $104 |
| USDC | 3.54% | 5.37% | 81.6% | $123.2M | $100.5M |
| JITOSOL | 0.00% | 1.66% | 0.6% | $98.2M | $614k |
| cbBTC | 0.00% | 0.15% | 2.0% | $57.0M | $1.1M |
| JupSOL | 0.00% | 1.69% | 1.0% | $52.1M | $523k |
| USDG | 3.77% | 5.53% | 84.2% | $44.7M | $37.6M |
| PYUSD | 1.98% | 3.09% | 85.6% | $40.0M | $34.3M |
| hSOL | 0.00% | 1.61% | 0.0% | $28.4M | $11k |
| dfdvSOL | 0.00% | 1.61% | 0.0% | $22.3M | $0.00 |
| MSOL | 0.00% | 1.83% | 2.5% | $22.2M | $559k |
| xBTC | 0.00% | 0.11% | 1.5% | $18.8M | $275k |
| vSOL | 0.00% | 1.61% | 0.0% | $17.4M | $6494 |
| USDT | 3.22% | 5.15% | 77.9% | $10.6M | $8.2M |


Kamino JLP Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| JLP | 0.00% | 0.00% | 0.0% | $45.3M | $0.00 |
| USDC | 3.53% | 4.36% | 90.4% | $20.4M | $18.5M |
| USDT | 4.38% | 5.26% | 93.0% | $1.9M | $1.7M |
| PYUSD | 4.18% | 5.05% | 92.4% | $1.4M | $1.3M |


Kamino Ethena Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| USDe | 0.00% | 0.01% | 0.0% | $267.5M | $1027 |
| PYUSD | 3.41% | 4.05% | 93.8% | $251.4M | $235.9M |


Kamino Jito Market (reserves with ≥ $1M supplied; APY as reported by the Kamino API):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| JITOSOL | 0.00% | 0.02% | 1.7% | $21.6M | $365k |
| SOL | 4.79% | 5.72% | 93.5% | $20.6M | $19.3M |


Save (Solend) main market (reserves with ≥ $1M supplied; rates as reported by the Save API, utilisation from reserve state):

| asset | supply APY | borrow APY | utilisation | supplied | borrowed |
|---|---|---|---|---|---|
| mSOL | 0.00% | 0.00% | 0.0% | $24.9M | $0.00 |
| bSOL | 0.00% | 0.00% | 0.0% | $22.3M | $0.00 |
| USDC | 2.96% | 5.04% | 73.9% | $22.2M | $16.4M |
| SOL | 2.84% | 5.42% | 66.2% | $20.2M | $13.4M |
| jitoSOL | 0.00% | 0.00% | 0.0% | $8.6M | $0.00 |
| USDT | 1.76% | 4.08% | 54.3% | $5.2M | $2.8M |
| SAVE…tTFt | 0.00% | 0.00% | 0.0% | $5.1M | $0.00 |
| 7Q2a…cavn | 0.00% | 0.00% | 0.0% | $2.5M | $0.00 |
| cbBTC | 0.28% | 2.98% | 11.7% | $2.5M | $296k |
| jupSOL | 0.00% | 0.00% | 0.0% | $1.6M | $0.00 |


Jupiter Lend Earn (supply rate + rewards, bps as reported):

| vault | asset | supply APY | rewards | total | total assets |
|---|---|---|---|---|---|
| jlUSDC | USDC | 4.56% | 0.40% | 4.96% | $451.7M |
| jlJupUSD | JupUSD | 5.09% | 0.99% | 6.08% | $57.9M |
| jlWSOL | WSOL | 3.85% | 0.00% | 3.85% | $19.8M |
| jlUSDT | USDT | 4.25% | 0.00% | 4.25% | $17.6M |
| jlEURC | EURC | 3.69% | 0.00% | 3.69% | $5.1M |
| jlUSDS | USDS | 4.74% | 0.00% | 4.74% | $3.9M |
| jlUSDG | USDG | 5.42% | 0.00% | 5.42% | $2.9M |


Lending events in the window (instruction discriminators matched per program):

| venue | txs | failed | events |
|---|---|---|---|
| Kamino Lend | 4339 | 2573 | flash_borrow_reserve_liquidity (failed) 2384, flash_repay_reserve_liquidity (failed) 2384, refresh_reserve 1197, refresh_reserves_batch 532, refresh_obligation 427, deposit_reserve_liquidity_and_obligation_collateral_v2 188, refresh_reserve (failed) 188, refresh_obligation (failed) 188, liquidate_obligation_and_redeem_reserve_collateral_v2 (failed) 184, borrow_obligation_liquidity_v2 170 |
| marginfi v2 | 1514 | 223 | lending_account_end_flashloan (failed) 223, lending_account_start_flashloan (failed) 223, lending_account_repay (failed) 184, lending_account_borrow (failed) 181, lending_account_borrow 107, lending_account_repay 106, lending_account_end_flashloan 104, lending_account_start_flashloan 104, lending_account_withdraw 18, lending_account_deposit 13 |
| Jupiter Lend Earn | 570 | 8 |  |
| Save (Solend) | 49 | 16 | repay_obligation_liquidity (failed) 12, borrow_obligation_liquidity 9, withdraw_obligation_collateral_and_redeem_reserve_collateral 8, deposit_reserve_liquidity_and_obligation_collateral 5, borrow_obligation_liquidity (failed) 2, repay_obligation_liquidity 2, deposit_reserve_liquidity_and_obligation_collateral (failed) 1 |


Liquidations that succeeded: 0. Liquidation attempts (ok / failed, top payers): Kamino Lend 0 / 184 (bSoL…SpgW 184); marginfi v2 0 / 3 (A2KE…bdb2 3). Successful flash loans: Kamino Lend 73 txs (~$309k principal), marginfi v2 104 txs (~$1.00 principal). Flash-loan payers (with failures): Kamino Lend: guof…VNk3 (failed) 2091, Hz7K…r7sz (failed) 178, F1ae…esMm (failed) 52, 7tUA…YsVH (failed) 19, 9Mpb…tX95 18; marginfi v2: 3zdX…MPL8 100, MoSt…Xr6m (failed) 50, 996m…1icu (failed) 39, 3zZ6…uQv1 (failed) 39, ALVa…hGnz (failed) 38. Programs co-invoked in flash-loan txs: Kamino Lend: Jupiter Aggregator v6 2234, TesseraV 2128, Perps 2091, Meteora DLMM 104, BisonFi 94; marginfi v2: Jupiter Aggregator v6 118, Meteora DLMM 102, Pump.fun Amm 63, Raydium CLMM 60, Whirlpool 35.


Same asset, different venue (supply APY / borrow APY / utilisation / supplied; reserves ≥ $5M; Jupiter Lend = supply + rewards, no borrow side):

| asset | venue | supply APY | borrow APY | util | supplied |
|---|---|---|---|---|---|
| USDC | Jupiter Lend | 4.96% | – | – | $451.7M |
| USDC | Kamino SOL/BTC | 3.54% | 5.37% | 82% | $123.2M |
| USDC | Kamino JLP | 3.53% | 4.36% | 90% | $20.4M |
| USDC | Save main | 2.96% | 5.04% | 74% | $22.2M |
| USDE | Kamino Ethena | 0.00% | 0.01% | 0% | $267.5M |
| SOL | Kamino SOL/BTC | 4.96% | 6.51% | 90% | $252.7M |
| SOL | Kamino Jito | 4.79% | 5.72% | 93% | $20.6M |
| SOL | Jupiter Lend | 3.85% | – | – | $19.8M |
| SOL | Save main | 2.84% | 5.42% | 66% | $20.2M |
| PYUSD | Kamino Ethena | 3.41% | 4.05% | 94% | $251.4M |
| PYUSD | Kamino SOL/BTC | 1.98% | 3.09% | 86% | $40.0M |
| JITOSOL | Kamino SOL/BTC | 0.00% | 1.66% | 1% | $98.2M |
| JITOSOL | Kamino Jito | 0.00% | 0.02% | 2% | $21.6M |
| JITOSOL | Save main | 0.00% | 0.00% | 0% | $8.6M |
| JUPUSD | Jupiter Lend | 6.08% | – | – | $57.9M |
| JUPSOL | Kamino SOL/BTC | 0.00% | 1.69% | 1% | $52.1M |
| JLP | Kamino JLP | 0.00% | 0.00% | 0% | $45.3M |
| USDG | Kamino SOL/BTC | 3.77% | 5.53% | 84% | $44.7M |
| USDT | Jupiter Lend | 4.25% | – | – | $17.6M |
| USDT | Kamino SOL/BTC | 3.22% | 5.15% | 78% | $10.6M |
| USDT | Save main | 1.76% | 4.08% | 54% | $5.2M |
| EURC | Jupiter Lend | 3.69% | – | – | $5.1M |


## E. Stablecoins and LSTs: issuance, pegs, NAV

Mints and burns on the registry stablecoin and LST mints, split by whether the instruction ran inside a CCTP transaction (bridge) or not (issuer treasury / stake pool):

| token | issuer minted | issuer burned | CCTP minted | CCTP burned | net |
|---|---|---|---|---|---|
| USDC | 0 | 2,485,695 | 0 | 2,381,901 | -4,867,596 |
| PYUSD | 330,940 | 869,996 | 0 | 0 | -539,056 |
| USDG | 10,826 | 176,059 | 0 | 0 | -165,233 |
| jupSOL | 89 | 0 | 0 | 0 | 89 |
| jitoSOL | 3 | 18 | 0 | 0 | -16 |
| bSOL | 0 | 21 | 0 | 0 | -21 |
| mSOL | 18 | 2 | 0 | 0 | 16 |
| INF | 2 | 0 | 0 | 0 | 2 |
| bbSOL | 2 | 0 | 0 | 0 | 2 |
| sSOL | 0 | 1 | 0 | 0 | -1 |
| JupUSD | 0 | 0 | 0 | 0 | 0 |


By mint authority (CCTP mints/burns carry the CCTP minter PDA as authority; issuer treasuries carry the issuer authority):

| token | side | authority | label | amount | n |
|---|---|---|---|---|---|
| USDC | burn | CCTP tx (user burn / custody) |  | 2,381,901 | 134 |
| USDC | burn | CMth…A5oR |  | 2,284,393 | 1 |
| PYUSD | burn | D3Pf…BZBo |  | 570,000 | 1 |
| PYUSD | mint | 8Jor…8Qk2 |  | 330,940 | 1 |
| PYUSD | burn | CS9a…RRWe | stablecoin treasury operator (mints/burns PYUSD with Paxos, cycles USDC, jlUSDC and Kamino; funds arrive by CCTP from Polygon) | 299,996 | 1 |
| USDC | burn | 41zC…wePu | Binance-adjacent USDC routing wallet | 173,303 | 3 |
| USDG | burn | 4fVL…VtWq |  | 99,958 | 1 |
| USDG | burn | 23av…74DD |  | 76,001 | 1 |
| USDC | burn | 7MjD…EoEG |  | 28,000 | 2 |
| USDG | mint | 3YJL…bhxR |  | 10,826 | 1 |
| USDG | burn | CRkp…FxjD |  | 100 | 1 |
| jupSOL | mint | EMju…QDNw |  | 89 | 3 |
| jitoSOL | burn | Dcxp…91NH |  | 18 | 1 |
| mSOL | mint | 3JLP…g6KM |  | 18 | 4 |
| bSOL | burn | 9tMY…oGK5 |  | 15 | 2 |
| bSOL | burn | Lion…VK6y |  | 5 | 2 |
| jitoSOL | mint | 6iQK…pVSS |  | 3 | 27 |
| INF | mint | AYhu…CGvW |  | 2 | 12 |
| mSOL | burn | Eg8b…DhT2 |  | 2 | 1 |
| bbSOL | mint | 3pFT…xyGJ |  | 2 | 1 |


Largest single mints/burns:

| time | token | side | amount | authority | CCTP tx |
|---|---|---|---|---|---|
| 14:05:14 | USDC | burn | 2,284,393 | CMth…A5oR |  |
| 14:06:30 | USDC | burn | 990,000 | D2t2…b8kw | yes |
| 14:07:00 | USDC | burn | 923,700 | D2t2…b8kw | yes |
| 13:28:36 | PYUSD | burn | 570,000 | D3Pf…BZBo |  |
| 14:00:17 | PYUSD | mint | 330,940 | 8Jor…8Qk2 |  |
| 14:12:42 | PYUSD | burn | 299,996 | CS9a…RRWe |  |
| 13:24:50 | USDC | burn | 131,000 | HBgL…mxmD | yes |
| 14:08:13 | USDC | burn | 125,938 | 41zC…wePu |  |
| 13:24:56 | USDG | burn | 99,958 | 4fVL…VtWq |  |
| 13:22:58 | USDC | burn | 99,442 | 5SvX…f7Uy | yes |
| 13:57:58 | USDG | burn | 76,001 | 23av…74DD |  |
| 13:34:29 | USDC | burn | 50,000 | 6omu…Ynfb | yes |
| 13:26:09 | USDC | burn | 47,347 | 41zC…wePu |  |
| 14:01:04 | USDC | burn | 41,000 | coNk…hGJb | yes |
| 14:07:48 | USDC | burn | 25,000 | vmpG…g7c8 | yes |


Stablecoin prices at head (Jupiter aggregator price; deviation from par):

| token | price | vs par | liquidity (Jupiter) |
|---|---|---|---|
| USDC | $0.9999 | -1.0 bp | $411.2M |
| USDT | $0.9998 | -1.7 bp | $41.8M |
| PYUSD | $1.0000 | +0.1 bp | $30.1M |
| USDS | $0.9998 | -1.7 bp | $1.8M |
| USD1 | $0.9999 | -1.5 bp | $23.9M |
| USDG | $1.0001 | +0.7 bp | $36.4M |
| JupUSD | $0.9997 | -3.1 bp | $19.3M |
| USDe | $0.9998 | -1.9 bp | $8.9M |
| sUSDe | $1.2408 |  | $2775 |
| EURC | $1.1623 |  | $657k |


LSTs: market price in SOL (Jupiter price / Jupiter SOL price) against the stake-pool NAV read on-chain (finalized; pools verified by owner program and account type) and against Sanctum's sol-value API. The two NAV sources disagree by ~1.9% on every pool the on-chain read covers; the on-chain value is authoritative and the Sanctum column is kept only to document the discrepancy:

| LST | NAV on-chain (SOL) | market vs on-chain | Sanctum sol-value | market vs Sanctum | market (SOL) | liquidity |
|---|---|---|---|---|---|---|
| jitoSOL | 1.30005 | +9.2 bp | 1.27587 | +198.9 bp | 1.30125 | $1.07B |
| mSOL | – | – | 1.37665 | +198.8 bp | 1.40402 | $239.3M |
| bSOL | 1.31443 | +4.5 bp | 1.29072 | +188.3 bp | 1.31502 | $95.7M |
| jupSOL | 1.20795 | +14.8 bp | 1.18394 | +217.9 bp | 1.20974 | $538.5M |
| INF | – | – | 1.40784 | +290.9 bp | 1.44880 | $198.1M |
| hSOL | – | – | 1.16206 | +209.9 bp | 1.18645 | $95.8M |
| vSOL | – | – | 1.14911 | +195.6 bp | 1.17158 | $138.7M |
| dSOL | – | – | 1.18970 | +218.2 bp | 1.21566 | $292.5M |
| bbSOL | – | – | 1.14756 | +204.1 bp | 1.17098 | $129.8M |
| sSOL | – | – | 1.19559 | -279.8 bp | 1.16214 | $97k |


LST issuance in the window (mintTo/burn on the LST mints): jupSOL +89 −0, jitoSOL +3 −18, bSOL +0 −21, mSOL +18 −2, INF +2 −0, bbSOL +2 −0, sSOL +0 −1


## F. Bridges, exchanges, large transfers, poisoning

CCTP USDC: out $2.4M (134 deposit-for-burn), in $2.3M (10 receive-message; v2 pays recipients out of a custody token account instead of minting — Sui $4.00, Base $8513, Avalanche $15k, Aptos $1.4M, Polygon $869k).

| direction | chain | USDC | transfers |
|---|---|---|---|
| out | Ethereum | $1.9M | 12 |
| out | Arbitrum | $162k | 9 |
| out | Avalanche | $135k | 7 |
| out | Polygon | $77k | 7 |
| out | HyperEVM | $32k | 40 |
| out | domain 27 | $21k | 33 |
| out | Ink | $7791 | 1 |
| out | Base | $4473 | 19 |
| out | Sui | $3341 | 3 |
| out | Noble | $329 | 1 |
| out | domain 15 | $80.00 | 1 |
| out | Plume | $0.00 | 1 |
| in | Aptos | $1.4M | 2 |
| in | Polygon | $869k | 2 |
| in | Avalanche | $15k | 1 |
| in | Base | $8513 | 3 |
| in | Sui | $4.00 | 2 |


Largest CCTP transfers:

| time | direction | chain | USDC | payer | recipient (EVM) |
|---|---|---|---|---|---|
| 14:06:30 | out | Ethereum | $990k | D2t2…b8kw | 0x28b5a0e9…cf5d |
| 14:07:00 | out | Ethereum | $924k | D2t2…b8kw | 0x28b5a0e9…cf5d |
| 14:02:26 | in | Aptos | $850k | HGpY…Zvzs |  |
| 14:02:57 | in | Aptos | $588k | HGpY…Zvzs |  |
| 14:12:13 | in | Polygon | $569k | CS9a…RRWe |  |
| 14:15:47 | in | Polygon | $300k | CS9a…RRWe |  |
| 13:24:50 | out | Avalanche | $131k | HBgL…mxmD | 0xafa88a2f…a112 |
| 13:22:58 | out | Arbitrum | $99k | 5SvX…f7Uy | 0x28b5a0e9…cf5d |
| 13:34:29 | out | Arbitrum | $50k | FwDz…uaYq | 0x28b5a0e9…cf5d |
| 14:01:04 | out | Polygon | $41k | 87pE…L5Uw | 0x28b5a0e9…cf5d |
| 14:07:48 | out | Polygon | $25k | vmpG…g7c8 | 0x28b5a0e9…cf5d |
| 13:20:49 | out | Ethereum | $17k | Eeoc…Brwd | 0x4b3cd0bb…fa3e |


Exchange net flow (labels from memory; the fan-in column is the behavioural check — a deposit hot wallet receives from many unique senders):

| exchange | net by asset | net USD | txs | senders | receivers | fan-in (SOL≥0.1) |
|---|---|---|---|---|---|---|
| Binance | USDC +5.53M, USDT +2.88M, SOL -23.6k, BONK -27.43B, PENGU -5.10M | $5.8M | 1912 | 203 | 518 | 201 |
| KuCoin | USDC -873.0k, SOL -3839, USDT -48.5k, BONK +5.97B, USDG +6293 | -$1.3M | 421 | 4 | 142 | 42 |
| Gate.io | SOL -2691, USDT -124.7k, USDC -52.5k, PENGU -4.02M, USDG -12.0k | -$520k | 237 | 0 | 1 | 0 |
| Coinbase | USDC -520.8k, EURC +42.0k, SOL +44.87, BONK +889.33M, WIF -10.9k | -$466k | 305 | 32 | 146 | 26 |
| Coinbase 2 | SOL +6946, cbBTC -4.57, USDC -36.9k, EURC -1587, WIF +3872 | $332k | 533 | 249 | 177 | 245 |
| Coinbase 3 | USDC -282.8k, SOL +1244, BONK +3.54B, EURC -8587, PYUSD +5695 | -$148k | 420 | 105 | 189 | 99 |
| MEXC | USDT -149.5k, SOL +304, USDC +16.4k, RAY -80, PENGU -3339 | -$101k | 593 | 190 | 172 | 82 |
| Bybit | SOL -0.0194, 7i5K…pfRx +2295.19B, a3W4…pump -4.90B, pump…9Dfn +9017.56B, USDT 0 | -$2.00 | 52 | 14 | 5 | 0 |
| Binance 2 | SOL 0, orca…ktZE -1196.72B | $0.00 | 1 | 0 | 1 | 0 |


Label checks: Binance: fan-in consistent with exchange deposit address; Binance 2: some activity; Coinbase: fan-in consistent with exchange deposit address; Coinbase 2: fan-in consistent with exchange deposit address; Coinbase 3: fan-in consistent with exchange deposit address; Kraken: no activity in window; OKX: no activity in window; Bybit: some activity; Gate.io: some activity; KuCoin: fan-in consistent with exchange deposit address; MEXC: fan-in consistent with exchange deposit address; Crypto.com: no activity in window; Bitget: no activity in window; HTX: no activity in window


Unlabelled addresses with exchange-like fan-in (≥ 40 unique senders of ≥ 0.1 SOL):

| address | label | unique senders | transfers in | SOL in | median in | transfers out | destinations | SOL out | shape |
|---|---|---|---|---|---|---|---|---|---|
| 7uTT…i8pZ | vault of deposit router 99vQ… (largest unlabelled fan-in) | 2348 | 4209 | 9739.1 | 0.537 | 60 | 1 | 9850.4 | collector hub (many in, ≤2 out) |
| AcNh…ZHJW | sybil-cluster collector (3,253 wallets → 1 sweep, same playbook and token amount as A1zq…) | 729 | 729 | 1131.3 | 0.317 | 1 | 1 | 1279.1 | collector hub (many in, ≤2 out) |
| A1zq…2mos | sybil-cluster collector (3,254 wallets → 1 sweep in 6 min) | 710 | 710 | 819.6 | 0.297 | 1 | 1 | 1266.1 | collector hub (many in, ≤2 out) |
| BTRk…g4WT |  | 536 | 536 | 662.2 | 0.548 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 62jw…MZ4F | sybil-cluster collector (533 wallets → 1 sweep) | 533 | 533 | 680.1 | 0.582 | 1 | 1 | 680.1 | collector hub (many in, ≤2 out) |
| ArLh…dbDf | sybil-cluster collector (532 wallets, 683.6 SOL round trip funded by 2Fs1…) | 532 | 532 | 683.5 | 0.576 | 1 | 1 | 683.6 | collector hub (many in, ≤2 out) |
| 4QoH…WEax | sybil-cluster collector (531 wallets, 654.1 SOL round trip funded by C1yb…) | 531 | 531 | 654.1 | 0.514 | 1 | 1 | 654.1 | collector hub (many in, ≤2 out) |
| BiAB…8MPm |  | 523 | 904 | 647.8 | 0.486 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 6sBT…N6P6 |  | 522 | 789 | 176.1 | 0.197 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 2d5H…KPBs |  | 464 | 732 | 418.8 | 0.376 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| FNmF…zrez |  | 450 | 450 | 899.8 | 0.234 | 105 | 6+ | 893.0 | mixed |
| 7uEU…v7HD |  | 449 | 529 | 130.2 | 0.205 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 6FQv…EUX9 |  | 440 | 440 | 404.2 | 0.347 | 102 | 6+ | 891.3 | mixed |
| EW9d…Bs7J | SOL sink of program T1TA…XvGT (8.8k SOL from 425 senders, no outflow) | 425 | 2521 | 8762.7 | 3.476 | 0 | 0 | 0.0 | deposit address (many in, little out) |
| 6pSP…A52i | volume-bot hub cycling a pump token among ~820 wallets | 403 | 664 | 401.6 | 0.395 | 0 | 0 | 0.0 | deposit address (many in, little out) |


Distributors (≥ 200 outgoing SOL transfers of ≥ 0.1 SOL to ≥ 6 destinations — wallet funders, payout hubs):

| address | label | transfers out | SOL sent |
|---|---|---|---|
| F7p3…gmNe | sweep destination of deposit vault 7uTT8X… | 3220 | 14665.9 |
| BwWK…de6s |  | 1645 | 590.7 |
| 5tzF…uAi9 | Binance | 1063 | 35122.5 |
| CVrb…QKWa |  | 1027 | 1516.8 |
| ARu4…5SZn |  | 964 | 1580.2 |
| Biw4…PTUU |  | 884 | 1255.4 |
| 9aRk…PG8F |  | 810 | 1931.0 |
| EUoK…a72Y |  | 635 | 1272.9 |
| NMVX…VYXy |  | 602 | 689.7 |
| BFwu…E6NY |  | 562 | 2013.1 |
| 2Fs1…UxK4 |  | 540 | 683.6 |
| BMKa…sn1p |  | 530 | 680.1 |


Largest priced position changes (per owner and asset inside one transaction, ≥ $100k):

| time | owner | label | asset | change | value | kind | programs |
|---|---|---|---|---|---|---|---|
| 14:03:25 | 9936…L3QK | Huma-linked treasury ($10M USDC in via Huma, out to a Squads multisig) | USDC | -10.00M | $10.0M | protocol | SQDS…2pCf |
| 13:54:08 | 9936…L3QK | Huma-linked treasury ($10M USDC in via Huma, out to a Squads multisig) | USDC | +10.00M | $10.0M | lending | Huma |
| 13:54:08 | 7s1d…or2Z |  | USDC | -10.00M | $10.0M | lending | Huma |
| 14:03:25 | 6q76…3ad2 |  | USDC | +10.00M | $10.0M | protocol | SQDS…2pCf |
| 14:17:12 | 81w9…ytUj |  | USDC | +9.77M | $9.8M | transfer |  |
| 14:17:12 | Bc5b…nXHf |  | USDC | -9.77M | $9.8M | transfer |  |
| 13:35:44 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | -7.96M | $8.0M | transfer |  |
| 13:35:44 | 5tzF…uAi9 | Binance | USDC | +7.96M | $8.0M | transfer |  |
| 13:23:01 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | -5.06M | $5.1M | transfer |  |
| 13:23:01 | 5tzF…uAi9 | Binance | USDC | +5.06M | $5.1M | transfer |  |
| 13:25:38 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -4.88M | $4.9M | transfer |  |
| 13:25:38 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | +4.88M | $4.9M | transfer |  |
| 14:11:05 | 5tzF…uAi9 | Binance | USDC | -4.80M | $4.8M | transfer |  |
| 14:11:05 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | +4.80M | $4.8M | transfer |  |
| 14:02:47 | BRif…nNtd |  | USDC | -4.50M | $4.5M | transfer |  |
| 14:02:03 | BRif…nNtd |  | USDC | +4.50M | $4.5M | transfer |  |
| 14:02:47 | DPqs…t1xo |  | USDC | +4.50M | $4.5M | transfer |  |
| 14:02:03 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -4.50M | $4.5M | transfer |  |
| 14:08:46 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | +3.91M | $3.9M | transfer |  |
| 14:08:46 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | -3.91M | $3.9M | transfer |  |
| 14:13:09 | 5tzF…uAi9 | Binance | USDC | +3.91M | $3.9M | transfer |  |
| 14:13:09 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | -3.91M | $3.9M | transfer |  |
| 14:16:19 | 5tzF…uAi9 | Binance | USDC | -3.60M | $3.6M | transfer |  |
| 14:16:19 | 41zC…wePu | Binance-adjacent USDC routing wallet | USDC | +3.60M | $3.6M | transfer |  |
| 14:18:03 | 5tzF…uAi9 | Binance | USDC | +3.35M | $3.3M | transfer |  |
| 14:18:03 | 3ADz…EFib | Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance) | USDC | -3.35M | $3.3M | transfer |  |
| 13:23:01 | BF61…b8Mw |  | USDC | -3.27M | $3.3M | other | 7pz2…K1Cp |
| 13:23:01 | DBds…RuRy |  | USDC | +3.27M | $3.3M | other | 7pz2…K1Cp |
| 13:44:07 | 6LY1…zkzF |  | USDC | +3.10M | $3.1M | transfer |  |
| 13:44:07 | 8CAA…bvwj |  | USDC | -3.10M | $3.1M | transfer |  |


Largest native SOL balance changes (≥ 1,000 SOL):

| time | account | label | change SOL | value | kind | payer |
|---|---|---|---|---|---|---|
| 14:14:52 | 44P5…Dyra | inter-exchange desk wallet (receives from Gate.io/KuCoin, sends PUMP/SOL to Binance-bound wallets and MfDu…) | -16783.0 | $1.8M | transfer | 44P5…Dyra |
| 14:14:52 | MfDu…GVWa | CEX-DEX market-making desk (own router GKyb…, Whirlpool/Raydium/DLMM; deposits to Binance via 3ADz…) | +16783.0 | $1.8M | transfer | 44P5…Dyra |
| 14:15:02 | MfDu…GVWa | CEX-DEX market-making desk (own router GKyb…, Whirlpool/Raydium/DLMM; deposits to Binance via 3ADz…) | -16782.9 | $1.8M | other | MfDu…GVWa |
| 14:15:02 | CTyF…AU8X |  | +16782.9 | $1.8M | other | MfDu…GVWa |
| 14:00:51 | 9SLP…KpKS |  | -15129.8 | $1.6M | transfer | 9SLP…KpKS |
| 14:00:51 | HRUR…Fm2P |  | +15129.8 | $1.6M | transfer | 9SLP…KpKS |
| 13:20:37 | 5tzF…uAi9 | Binance | -12410.3 | $1.3M | transfer | 5tzF…uAi9 |
| 13:20:37 | 38xC…MdUP |  | +12398.4 | $1.3M | transfer | 5tzF…uAi9 |
| 13:42:01 | 52MF…4Vo5 |  | -7200.0 | $758k | transfer | 5YSo…hxV1 |
| 13:42:00 | 52MF…4Vo5 |  | +7200.0 | $758k | transfer | 5YSo…hxV1 |
| 13:42:00 | GYSY…75y2 |  | -7200.0 | $758k | transfer | 5YSo…hxV1 |
| 13:42:01 | 5YSo…hxV1 |  | +7200.0 | $758k | transfer | 5YSo…hxV1 |
| 13:24:28 | 5YSo…hxV1 |  | -7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:24:28 | 52MF…4Vo5 |  | +7200.0 | $761k | transfer | 5YSo…hxV1 |
| 13:24:29 | 52MF…4Vo5 |  | -7200.0 | $761k | transfer | 52MF…4Vo5 |
| 13:24:29 | GYSY…75y2 |  | +7200.0 | $761k | transfer | 52MF…4Vo5 |
| 14:01:02 | 8vfX…Nr9c |  | -4957.4 | $521k | staking | vbfT…7A1i |
| 14:01:02 | 98C1…zajK |  | +4957.4 | $521k | staking | vbfT…7A1i |
| 13:27:39 | 7CGC…j9DV |  | -4734.0 | $500k | transfer | 7CGC…j9DV |
| 13:27:39 | 3vxh…gkom |  | +4734.0 | $500k | transfer | 7CGC…j9DV |


Address-poisoning style dust (≤ 1 raw token unit or ≤ 1,000 lamports sent by the payer to ≥ 20 distinct recipients): 68,343 transfers in the window from 226 senders with ≥ 50 each. Top senders (senders that dust only a handful of accounts — market-maker heartbeats — are excluded: sp1n…3xpX 17365→8, FcEA…UVGR 10623→1, DotU…LXMK 7674→8, stnk…aAKr 6172→8):

| sender | dust transfers | distinct recipients |
|---|---|---|
| 6uqx…XSPy | 7180 | 866 |
| 7Z1X…7CeJ | 6916 | 6658 |
| DRro…GwEc | 2320 | 2108 |
| AeeT…Jbqj | 1418 | 45 |
| 5fLX…tfmD | 697 | 39 |
| 2kwr…o17H | 697 | 39 |
| 6tUt…shDm | 688 | 40 |
