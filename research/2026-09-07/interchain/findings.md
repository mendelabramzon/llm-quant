# Three chains, one desk

Interchain reading of the 2026-09-07 windows. Each per-chain study was written on its own; this joins them,
re-derives the numbers that connect them, and corrects two that do not survive re-derivation. Everything below
comes from artifacts already in this repository plus the saved raw windows;
[`scripts/interchain.py`](../../../scripts/interchain.py) recomputes all of it and writes
[`interchain.json`](interchain.json).

| chain | window (UTC) | span | blocks | transactions |
|---|---|---:|---:|---:|
| Ethereum mainnet | 02:39:11 → 12:39:59 | 10.0 h | 2,985 | 776,618 |
| Robinhood Chain (Orbit L2, id 4663) | 04:06:08 → 14:06:07 | 10.0 h | 356,874 | 3,229,934 user |
| Solana | 13:19:41 → 14:19:41 | 1.0 h | 11,353 | 6,394,363 non-vote |

Sources: [`live_5h`](../live_5h/report.md) and [`live_midday`](../live_midday/report.md) (Ethereum),
[`robinhood_10h`](../robinhood_10h/report.md), [`solana_live`](../solana_live/report.md),
[`captive_flow_lp`](../captive_flow_lp/findings.md).

---

## 1. One wallet is the hinge between all three chains

[`0xf70da978…dbef`](https://etherscan.io/address/0xf70da97812cb96acdf810712aa562db8dfa3dbef) is an externally
owned account with the same address on Ethereum and on Robinhood Chain. Today it is:

- **The entire withdrawal side of Relay's depository on both chains.** On Robinhood Chain the RelayDepository
  paid out $42,839,504 of USDG in 600 withdrawals and **every dollar went to this wallet**. On Ethereum the
  depository paid out $7.11M of USDC, $2.56M of USDT and five other tokens to **exactly one recipient**: the
  same wallet. Of the 31 solver wallets on Robinhood Chain, this is the only one that touches USDG at all —
  the other 30 moved less than one dollar of it between them.
- **A Paxos mint-and-redeem counterparty on both chains.** It received $1,707,964 of newly minted USDG on
  Robinhood Chain (24.1% of everything minted there in the window) and burned $1,038,769 (29.5% of burns); on
  Ethereum it received $2,095,709 of freshly minted USDG and burned $1,447,550.
- **A cross-chain treasury operator.** It sent $7,805,816 of USDC to Circle's `TokenMinterV2` (Cross-Chain
  Transfer Protocol burns) and cycled $2.57M through `StargatePoolUSDC` in the Ethereum windows.
- **The largest fee payer among the solvers**, 13,056 transactions and 2.162 ETH on Robinhood Chain, plus
  2,101 transactions on Ethereum.
- **The top taker in both thin Uniswap v4 USDC/USDG pools on Ethereum** — 61.6% of one pool's volume and 43.9%
  of the other, and not a liquidity provider in either. That is the entire premise of yesterday's
  [captive-flow LP study](../captive_flow_lp/findings.md).

### What that changes

The captive-flow study read this wallet as *a Global Dollar Network partner paid to hold USDG, rebalancing
inventory it is rewarded for holding*, and priced the strategy's main risk as "the desk might reroute to Paxos
direct mint/redeem." Both halves need revising:

1. **It is Relay's USDG inventory wallet, not a rebate farmer.** Its USDG is sourced to settle cross-chain
   intents on the chain where USDG is the settlement asset. The pool volume is a solver's marginal balancing
   need, not a subsidised conversion programme.
2. **The "might reroute to direct mint" risk is not in the future — it is already the base case.** The wallet
   used primary mint and redemption on *both* chains inside this window, at a larger size than its pool
   activity. The v4 pool is its top-up venue, not its main one.
3. **The book is close to flat.** Over the window it netted +$58,502 of USDG on Robinhood Chain and +$482,020
   on Ethereum against tens of millions of turnover. So pool volume tracks *gross settlement churn*, not a
   directional demand for USDG. The right leading indicator for the LP's fee yield is Relay's depository
   throughput, not USDG's issuance.

The strategy's shape survives — the flow is genuinely captive and genuinely non-toxic, because a $1↔$1
conversion carries no price information. What changes is what you monitor.

### USDG's supply is rotating toward the new chain

Counting transfers to and from the zero address on each chain:

| chain | window | minted | burned | net |
|---|---|---:|---:|---:|
| Ethereum | 10 h | $4.77M | $16.51M | **−$11.75M** |
| Robinhood Chain | 10 h | $7.09M | $3.52M | **+$3.57M** |
| Solana | 1 h | $0.011M | $0.176M | −$0.17M |

The same redemption counterparties appear on both EVM chains — `0xf845a0a0…` burned $10.21M on Ethereum and
$1.00M on Robinhood Chain, `0x50cfe7c1…` burned on both — so Paxos runs one counterparty list across chains and
this is one book, not two. The direction is clear, though the magnitudes are not a transfer: the windows differ,
other chains are unobserved, and a zero-address burn does not distinguish a Paxos redemption from a LayerZero
bridge send (`LZMultiCall` accounts for $1.01M of the Ethereum burns).

---

## 2. Relay is the largest retail flow on all three chains, and Ethereum is the smallest of the three

| chain | user deposits into the Relay depository | deposit txs | distinct depositors | payout concentration |
|---|---:|---:|---:|---|
| Robinhood Chain (10 h) | $42.9M USDG + 3,971 ETH ≈ **$52.8M** | 158,737 | 3,000+ | 1 wallet, 600 withdrawals |
| Ethereum (10 h) | $10.09M tokens + 1,291 ETH ≈ **$13.3M** | 13,190 | 2,233 token, 5,746 native | 1 wallet |
| Solana (1 h) | $8.80M USDC + 9,817 SOL ≈ **$9.8M** | 39,462 | 16,560 | swept in 60 txs to 1 treasury |

Average ticket sizes are $299 on Robinhood Chain and $223 on Solana. This is app-scale retail order flow, and
if the Solana hour is representative of its day, Solana originates roughly seven times Ethereum's Relay volume.

**This also answers today's open question on Solana.** The Solana narrative describes
`99vQwtBwYtrqqD9YSXbdum3KBdxPAVxYTaQ3cfnJSrN2` → vault `7uTT8Xi5…` → treasury `F7p3dFrj…` as "an unlabelled
custodial deposit system … with ~30k users an hour it is a major exchange, prediction market or perps venue and
should be identified." It is Relay's Solana depository: the same architecture, the same role, the same
one-treasury payout shape as the two EVM chains. Its router payer `AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51`
being the single largest fee payer on Solana for the hour is the Solana-side equivalent of the solver fleet
paying 19.5% of all fees on Robinhood Chain.

Three independent per-chain scans each found this network and none named it the same way. It belongs in
`scripts/address_labels.json` and `scripts/solana_labels.json` as one verified entity.

### The label registry had it booked as a centralised exchange

`scripts/address_labels.json` carried `0xf70da978…` as **"exchange hot wallet with USDG desk", kind `exchange`,
source `model-memory`**. `live_scan` counts `kind` in {exchange, exchange_deposit} as exchange flow, so all of
this wallet's Relay settlement and Paxos primary issuance was being booked as customer flow to a CEX:

| window | counted "in" | counted "out" | spurious net |
|---|---:|---:|---:|
| 02:39–07:39 | $3.52M | $9.75M | −$6.23M |
| 07:39–12:39 | $8.22M | $13.21M | −$5.00M |
| **total** | **$11.74M** | **$22.96M** | **−$11.22M** |

This is the same failure the registry was built to fix, one level up: it is not a mis-typed contract but a
mis-typed *counterparty*, sourced from memory. Corrected in place with the repo's own tool, retyped `bridge`
alongside `RelayRouterV3` and `RelayApprovalProxyV3`:

```sh
python3 scripts/labels.py add 0xf70da97812cb96acdf810712aa562db8dfa3dbef \
  --label "Relay solver / USDG inventory wallet (…)" --kind bridge --source etherscan-verified
```

The evidence for the retype is the three Relay contracts' verified names plus the measurement that this wallet
takes 100% of the depository's payouts on two chains. Ethereum exchange netflow for both windows should be
re-derived after this change; today's published figures include the amounts above.

---

## 3. A ten-week-old L2 out-earns Ethereum's own base fee by 31×

Same ten hours, both measured from saved blocks:

| | gas used | fee take | average price | settlement cost |
|---|---:|---:|---:|---:|
| Ethereum L1 (base fee burned) | 90.74 Ggas | **8.958 ETH ≈ $22,305** | 0.0987 gwei | — |
| Robinhood Chain (L2 base fee) | 865.83 Ggas | **279.185 ETH ≈ $696,375** | 0.3225 gwei | 0.0249 ETH to Ethereum |

9.5× the gas at 3.3× the price. Ethereum's own priority fees are the larger half of its fee market right now —
an upper bound of 132.7 ETH, computed from gas *limit* because the live-scan collector does not fetch receipts —
but the burn itself is $22k for a whole third of a day.

The three chains price urgency in three incompatible ways, and two of them charge nothing for it:

- **Ethereum** auctions it. Median tip 0.07 gwei against 2,406 gwei paid for the first slot after a
  centralised-exchange move — five orders of magnitude, concentrated on the two minutes when price moved.
- **Robinhood Chain** ignores it. 175,818 transactions from 9,674 senders bid at least 3× the base fee, some up
  to 3,000 gwei; **none was charged a single wei above base fee**. Nitro orders first-come-first-served, so
  the bidding infrastructure those bots run is inert and the competition there is pure latency.
- **Solana** charges it per transaction and keeps it on failure. Priority fees were 233.09 SOL against 35.80 SOL
  of base fee (86.7% of all non-vote fees), and failed transactions paid 64.89 SOL, 24.1% of the total. Jito
  tips are the opposite: they revert with the transaction, so of the intent to tip only 36.42 SOL was actually
  paid, and one wallet attached 14.3 SOL of tips to 4,711 transactions that all failed and paid none of it.

---

## 4. Two numbers in today's reports do not survive re-derivation

**(a) Tesla is not trading 4.4% rich on Robinhood Chain.** The report's fifth finding says TSLA "traded at
$371.1 against a $355.45 reference for the whole window (+4.4%, 6,663 price points)". Re-deriving the price
independently from each of TSLA's three USDG pools across the window:

| | value |
|---|---:|
| last price, deepest pool | 355.79 |
| range across all three pools | 354.39 – 356.40 |
| Blockscout reference | 355.45 |
| deviation | **+0.10%** |

Across all 43 stocks with a USDG pool, 40 are within 1% of reference, the median absolute deviation is 0.19%,
and only RCAT — a $918k token — exceeds 2%. There is no tokenized-equity mispricing on this chain today.

The cause is visible in the code. `scripts/orbit_scan.py` runs a second pass over newly resolved pools and
merges its prices with `setdefault` (lines 689–691), so a first-pass price can never be corrected by the second
pass, and every pool of a token overwrites the last without volume weighting. TSLA's `px_onchain_first` and
`px_onchain_last` being *exactly* equal at 371.15 across 6,663 points is that bug's fingerprint: a real AMM
price does not sit still through $9.9M of volume.

**(b) The Solana narrative contradicts its own table on USDG.** The insights say "USDG 8.32% on Jupiter Lend but
only $2.9M". The deterministic table in the same report, and `head_state.json` behind it, say jlUSDG pays
**5.42%** (5.42% supply, 0.00% rewards) on $2.92M. The table is right.

Both are the failure mode the roadmap's item 3 exists to catch: a headline number that nothing re-derives.

---

## 5. The dollar-yield ladder, three chains wide — and Robinhood Chain's rung, measured for the first time

No per-chain artifact carries a rate read for Robinhood Chain; its DeFi is described by flow only. Public
endpoints there serve no archive state, so the rate has to be realised forward instead: sample
`convertToAssets(1e24)` twice a few minutes apart and annualise. Measured live:

| vault (Robinhood Chain) | total assets | realised APY |
|---|---:|---:|
| steakUSDG | **$456.3M** | 3.77% |
| spUSDG (Spark) | $41.2M | 3.50% |
| ethenaUSDG | $23.5M | 2.46% |

Two independent runs of the method 25 minutes apart agree to within 3 basis points (3.75/3.77, 2.43/2.46,
3.50/3.50), so the read is the accrual rate, not sampling noise.

Joined with the other two chains' head reads:

| chain | venue | asset | supply | size |
|---|---|---|---:|---:|
| Ethereum | Compound v3 | USDC | **6.91%** | $373M |
| Ethereum | SparkLend | USDT | 6.05% → 2.62% | $344M → $391M |
| Solana | Jupiter Lend | JupUSD | 6.08% | $57.9M |
| Solana | Jupiter Lend | USDG | 5.42% | $2.9M |
| Solana | Jupiter Lend | USDC | 4.96% | $452M |
| Robinhood | steakUSDG | USDG | 3.77% | $456M |
| Ethereum | Sky savings rate | USDS | 3.60% | — |
| Ethereum | Aave v3 | USDC | 3.58% | $2,309M |
| Solana | Kamino main | USDC | 3.58% | — |
| Solana | Save main | USDC | 2.96% | $22M |

Two things fall out.

**The largest dollar pool outside Ethereum pays nearly the least.** $456M sits in one USDG vault on a
ten-week-old L2 earning 3.77%, while the same dollar earns 6.91% on Compound v3 and 4.96% on Jupiter Lend. That
capital is not yield-seeking; it is settlement inventory on the chain where USDG is the settlement asset. Which
is consistent with §1: USDG's holders there are the ecosystem, not allocators.

**The widest gap for the same asset is still inside one chain, not between chains.** Aave USDC 3.58% against
Compound v3 USDC 6.91% is 3.3 points, on $2.3B and $373M of deep, audited supply, with no bridge, no
cross-chain settlement risk and no new counterparty. Every cross-chain spread in the table is smaller. Before
this repo builds cross-chain rate tooling, the honest ranking is that venue selection on one chain dominates it.

---

## 6. Volume quality differs by an order of magnitude, and the detector transfers

Solana's scan built a self-matched-swap detector and found **$86.77M of $205.19M priced volume (42.3%)** is one
operator trading with itself, 60.0% of PumpSwap's. Applying the same idea to Robinhood Chain — in the weaker
form the Orbit logs allow, since they record the calling contract rather than the end user, so this is
same-block, same-caller, opposite-direction offsetting volume:

| pool | swaps sampled | calling contracts | self-matched share |
|---|---:|---:|---:|
| WETH/USDG v3, 1 bp (the chain's ETH/USD venue) | 15,768 | 119 | **0.72%** |
| USDG/NVDA v3, 5 bp | 2,860 | 55 | 1.35% |

Robinhood Chain's volume is real; Solana's headline number is not, and the Solana report says so itself. A
second correction falls out of the same pass: the Robinhood report describes the top pool as having "269
traders", but `pool_traders` records `topics[1]` of a v3 Swap, which is the calling contract. The 119 sampled
callers are routers — 44.8% of them the unverified 1%-fee router — not 119 people.

Making the self-match test a standing per-venue metric, and netting it out of every volume table, is the single
most transferable thing in today's three reports.

---

## 7. Requests to the quant step

1. **Label Relay once, everywhere.** *Partly done this session:* `0xf70da978…`, `RelayRouterV3` and
   `RelayApprovalProxyV3` are now typed `bridge` in `scripts/address_labels.json` (§2). Still to add: the other
   30 solver wallets, and `99vQwtBwYtrqqD9YSXbdum3KBdxPAVxYTaQ3cfnJSrN2` / `7uTT8Xi5…` / `F7p3dFrj…` /
   `AgmLJBMD…` in `scripts/solana_labels.json`. Then re-derive Ethereum exchange netflow for both windows.
2. **Fix the Orbit price merge.** Replace the `setdefault` merge in `orbit_scan.py` with a volume-weighted
   price per token across its pools, keep the per-pool series, and add the deviation-versus-reference check that
   found this (`interchain.py --only stocks`) as a standing assertion.
3. **Give Robinhood Chain a `head` read.** Morpho Blue markets, steakUSDG / spUSDG / ethenaUSDG, and the USDG
   pools. A chain holding $456M in one vault should not be measured by flow alone. The forward-realised
   share-price method in `interchain.py --only live` works without archive state.
4. **Port the self-match detector to every chain** and net it out of the volume tables, per venue and per token.
5. **Add a daily gas-and-fee series to `orbit_followups`.** Robinhood Chain's network fee accrual fell 2,699 →
   2,099 → 1,321 ETH per day across 09-04 to 09-06 while its base fee fell from ~0.89 to 0.31 gwei. Whether
   that is falling demand or falling price cannot be separated from four sampled blocks per day, and it is the
   number that governs the captive-flow LP thesis.
6. **Re-frame the captive-flow monitor** around Relay depository throughput rather than USDG issuance, per §1.

---

## Reproduce

```sh
uv run python scripts/interchain.py --date 2026-09-07                       # offline; fees, relay, usdg, stocks, yield, selfmatch
uv run python scripts/interchain.py --date 2026-09-07 --only stocks         # re-derives every stock price from its own pools
uv run python scripts/interchain.py --date 2026-09-07 --only live           # Robinhood vault yields; needs network, takes ~8 min
```

Offline sections read only `research/2026-09-07/*/analysis.json`, `head_state.json`, `pools.json`,
`stock_tokens.json`, `followups.json` and the saved raw windows. The `live` section makes read-only `eth_call`s
to public Robinhood Chain endpoints. No wallet or key is configured anywhere in this repository.

## Limitations

- The three windows overlap but are not identical, and Solana's is one hour against ten. Per-chain totals are
  never summed across chains without saying so.
- Ethereum priority fees are an upper bound: `live_collect` saves blocks and logs but not receipts, so gas
  *limit* stands in for gas used. Collecting receipts would also give Ethereum a revert rate to set against
  Solana's 29.8% and Robinhood Chain's 8.8%; today there is no comparable number for Ethereum.
- The stock-price re-derivation samples every 12th data chunk; the deviation figures are stable across sample
  steps 12, 18 and a contiguous first-400-chunk pass, but they are not the full census.
- The Robinhood self-match test is not the Solana one. It cannot see the end user behind a router, so it bounds
  intra-block self-offsetting rather than measuring operator-level wash trading.
- Vault APYs are realised over 424 seconds and annualised. That is a clean read of the accrual rate at this
  instant, not a forward yield.
- USDG issuance is counted as transfers to and from the zero address. It does not separate a Paxos redemption
  from a LayerZero bridge burn; `LZMultiCall` accounts for $1.01M of the Ethereum burns and the rest is
  unattributed.
