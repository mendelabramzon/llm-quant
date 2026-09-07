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
