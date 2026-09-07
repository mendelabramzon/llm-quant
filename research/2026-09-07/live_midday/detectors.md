# Detector sweep — research/2026-09-07/live_midday

Ran 7 detector(s); 27 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 3.38 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `gas_concentration` | 0 | 3.29 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 2 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `mass_distribution` | 5 | 5.53 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 2 | 3.66 | address labels the window contradicts, which is how a headline moves by a multiple |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 12 | 3.57 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

### [notable] unlabelled unknown 0x76f30e3f cycled $288.8M and ended the window flat (30 txs, 13 counterparties)

```json
{
 "address": "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a",
 "shape": "cycles",
 "gross_usd": 577511044,
 "txs": 30,
 "counterparties": 13,
 "tokens": 5,
 "pass_through_share": 0.467,
 "received_usd": 288755436,
 "sent_usd": 288755608,
 "retained_usd": -172,
 "retention": -0.0,
 "is_contract": null,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "unknown",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled unknown 0x9649788a cycled $117.0M and ended the window flat (6 txs, 1 counterparties)

```json
{
 "address": "0x9649788adfbdfc2bd39a0058be57ed36583c6043",
 "shape": "cycles",
 "gross_usd": 233973710,
 "txs": 6,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 116986855,
 "sent_usd": 116986855,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": null,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "unknown",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled eoa 0xe69f81b8 cycled $109.2M and ended the window flat (24 txs, 5 counterparties)

```json
{
 "address": "0xe69f81b825d7dc31ee9becef4dbeab5cf30e3abb",
 "shape": "cycles",
 "gross_usd": 218315932,
 "txs": 24,
 "counterparties": 5,
 "tokens": 2,
 "pass_through_share": 0.0,
 "received_usd": 109157966,
 "sent_usd": 109157966,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled eoa 0xed9b63d1 cycled $109.0M and ended the window flat (4 txs, 4 counterparties)

```json
{
 "address": "0xed9b63d1d4efa9ae415854486400c9354227bcdd",
 "shape": "cycles",
 "gross_usd": 218043017,
 "txs": 4,
 "counterparties": 4,
 "tokens": 2,
 "pass_through_share": 0.0,
 "received_usd": 109021508,
 "sent_usd": 109021508,
 "retained_usd": 0,
 "retention": -0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled unknown 0x5aae4d2f passed $113.5M through in 12 txs (67% ended flat, 11 counterparties)

```json
{
 "address": "0x5aae4d2f360e156de3416936049837a7bb685588",
 "shape": "pass-through",
 "gross_usd": 113459420,
 "txs": 12,
 "counterparties": 11,
 "tokens": 6,
 "pass_through_share": 0.667,
 "received_usd": 56730647,
 "sent_usd": 56728773,
 "retained_usd": 1874,
 "retention": 0.0,
 "is_contract": null,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "unknown",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled eoa 0x14681e4e cycled $52.2M and ended the window flat (16 txs, 3 counterparties)

```json
{
 "address": "0x14681e4e26f1b5b5774ae3b7f694ff08bbbeb65c",
 "shape": "cycles",
 "gross_usd": 104327968,
 "txs": 16,
 "counterparties": 3,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 52163984,
 "sent_usd": 52163984,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] USDS pays 3.48pp more on Sky SSR than Aave v3; rate does not dilute with size

```json
{
 "asset": "USDS",
 "high_venue": "Sky SSR",
 "low_venue": "Aave v3",
 "supply_apr_spot_pct": {
  "Aave v3": 0.124,
  "SparkLend": 2.318,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.476,
 "gap_pp_despiked": 3.476,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Sky SSR emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 11208135,
  "SparkLend": 747432633,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.03,
  "SparkLend": 0.656
 }
}
```

Economics: net APR 3.48%, $34,761,142 per year, GO — clears gas, impact and competition at this size

### [notable] hot wallet Binance 8 (model-memory) only received ($10.3M in, nothing out)

```json
{
 "address": "0xf977814e90da44bfa03b6295a0616a897441acec",
 "label": "Binance 8 (model-memory)",
 "source": "model-memory",
 "in_usd": 10293140,
 "why": "a hot wallet pays withdrawals out; a pure receiver is a deposit address or a treasury, which puts this inflow on the wrong side of net flow"
}
```

### [notable] USDT pays 1.63pp more on Aave v3 than SparkLend; $707.8M halves the gap

```json
{
 "asset": "USDT",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.563,
  "SparkLend": 2.619,
  "Compound v3 USDT": 3.022
 },
 "supply_apr_median_pct": {
  "Aave v3": 4.25
 },
 "gap_pp_spot": 0.944,
 "gap_pp_despiked": 1.631,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 2980073116,
  "SparkLend": 390856533,
  "Compound v3 USDT": 184036285
 },
 "utilisation": {
  "Aave v3": 0.93,
  "SparkLend": 0.828,
  "Compound v3 USDT": 0.839
 }
}
```

Economics: net APR 0.72%, $5,857,547 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 3.37pp more on Compound v3 USDC than SparkLend; $120.1M halves the gap

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.584,
  "SparkLend": 3.542,
  "Compound v3 USDC": 6.912,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 4.266
 },
 "gap_pp_spot": 3.37,
 "gap_pp_despiked": 3.37,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2308817883,
  "SparkLend": 25640640,
  "Compound v3 USDC": 372712068,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.933,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.911
 }
}
```

Economics: net APR 1.41%, $2,079,665 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDe/USDC: JIT took 12.8% of fees, so its quoted LP yield is overstated

```json
{
 "pool": "0x56fc29b86900aa0afa6e20b020429bffba1105cfb45070492c67529b46eb48c1",
 "venue": "uniswap_v4",
 "pair": "USDe/USDC",
 "fees_usd": 51.54,
 "fees_to_jit_usd": 6.58,
 "passive_fees_usd": 44.96,
 "volume_usd": 1662653,
 "apr_band_1pct_all_fees": 0.0011,
 "apr_band_1pct_passive_only": 0.00096,
 "why": "price this pool on passive fees; the JIT share never reaches liquidity that stayed"
}
```

### [notable] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 12,661 recipients in 60 txs (240 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 14432,
 "recipients": 12661,
 "txs": 60,
 "blocks": 60,
 "transfers_per_tx": 240.5,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "19612457833215659",
 "uniform_amount_share": 0.16,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDT to 12,056 recipients in 146 txs (100 per tx)

```json
{
 "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "token_symbol": "USDT",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 14652,
 "recipients": 12056,
 "txs": 146,
 "blocks": 146,
 "transfers_per_tx": 100.4,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "278",
 "uniform_amount_share": 0.003,
 "usd_median": 0.00027798879104,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 10,521 recipients in 20 txs (626 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 12525,
 "recipients": 10521,
 "txs": 20,
 "blocks": 20,
 "transfers_per_tx": 626.2,
 "carrier_contract": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "5000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] mint distribution: zero address (mint/burn) (known- sent 0x06450dee to 3,175 recipients in 55 txs (115 per tx)

```json
{
 "token": "0x06450dee7fd2fb8e39061434babcfc05599a6fb8",
 "token_symbol": null,
 "sender": "0x0000000000000000000000000000000000000000",
 "sender_label": "zero address (mint/burn) (known-canonical)",
 "kind": "mint distribution",
 "transfers": 6314,
 "recipients": 3175,
 "txs": 55,
 "blocks": 35,
 "transfers_per_tx": 114.8,
 "carrier_contract": "0x02c39d9278ed139ca602fa8d509f0f2e0caa2868",
 "carrier_label": null,
 "carrier_share": 0.269,
 "median_raw_amount": "20294186000000000000000000",
 "uniform_amount_share": 0.125,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDC to 2,990 recipients in 146 txs (25 per tx)

```json
{
 "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "token_symbol": "USDC",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 3701,
 "recipients": 2990,
 "txs": 146,
 "blocks": 146,
 "transfers_per_tx": 25.3,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "300",
 "uniform_amount_share": 0.03,
 "usd_median": 0.000299966295,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] unlabelled eoa 0xea6df897 cycled $34.3M and ended the window flat (42 txs, 3 counterparties)

```json
{
 "address": "0xea6df897fc8ea83d2b81391abec672ae1cfbae1c",
 "shape": "cycles",
 "gross_usd": 68620217,
 "txs": 42,
 "counterparties": 3,
 "tokens": 2,
 "pass_through_share": 0.0,
 "received_usd": 34310108,
 "sent_usd": 34310108,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled eoa 0x342869e3 cycled $30.0M and ended the window flat (4 txs, 2 counterparties)

```json
{
 "address": "0x342869e3d16adf2c30f6e762bbc449493f783142",
 "shape": "cycles",
 "gross_usd": 59997581,
 "txs": 4,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 29998790,
 "sent_usd": 29998790,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled eoa 0x424323d2 cycled $29.5M and ended the window flat (19 txs, 6 counterparties)

```json
{
 "address": "0x424323d25d30c687bdf79bb333da1d41c0373f37",
 "shape": "cycles",
 "gross_usd": 59042881,
 "txs": 19,
 "counterparties": 6,
 "tokens": 4,
 "pass_through_share": 0.263,
 "received_usd": 29521440,
 "sent_usd": 29521441,
 "retained_usd": -1,
 "retention": -0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled eoa 0x8e712469 cycled $28.9M and ended the window flat (4 txs, 2 counterparties)

```json
{
 "address": "0x8e712469e6cb10f6a9008fdcf2ab46c3ccc08232",
 "shape": "cycles",
 "gross_usd": 57869450,
 "txs": 4,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 28934725,
 "sent_usd": 28934725,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled venue 0xd8246178 passed $57.5M through in 640 txs (100% ended flat, 6 counterparties)

```json
{
 "address": "0xd82461784eb72d4b67cbab077989eb215315e272",
 "shape": "pass-through",
 "gross_usd": 57504792,
 "txs": 640,
 "counterparties": 6,
 "tokens": 3,
 "pass_through_share": 1.0,
 "received_usd": 28752401,
 "sent_usd": 28752391,
 "retained_usd": 10,
 "retention": 0.0,
 "is_contract": true,
 "emits_logs": true,
 "receives_calldata": true,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "venue",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled unknown 0x17dc4d78 cycled $24.0M and ended the window flat (4 txs, 3 counterparties)

```json
{
 "address": "0x17dc4d78e8abca9408c43541beb3c8215655403a",
 "shape": "cycles",
 "gross_usd": 47998065,
 "txs": 4,
 "counterparties": 3,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 23999032,
 "sent_usd": 23999032,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": null,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "unknown",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] exchange Binance 8 (model-memory) moved 100% of its flow with one counterparty

```json
{
 "address": "0xf977814e90da44bfa03b6295a0616a897441acec",
 "label": "Binance 8 (model-memory)",
 "source": "model-memory",
 "counterparty": "0x28c6c06298d514db089934071355e5743bf21d60",
 "counterparty_label": "Binance 14 (model-memory)",
 "share": 1.0,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] PYUSD pays 3.30pp more on Aave v3 than SparkLend; $5.6M halves the gap [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.875,
  "SparkLend": 0.579
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.296,
 "gap_pp_despiked": 3.296,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7598941,
  "SparkLend": 100000399
 },
 "utilisation": {
  "Aave v3": 0.878,
  "SparkLend": 0.166
 }
}
```

Economics: net APR 1.36%, $103,199 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.58pp more on Aave v3 than SparkLend; $14.0M halves the gap [one-block read, de-spiking unavailable]

```json
{
 "asset": "DAI",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.042,
  "SparkLend": 2.459
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 0.582,
 "gap_pp_despiked": 0.582,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 DAI: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 131757470,
  "SparkLend": 308265074
 },
 "utilisation": {
  "Aave v3": 0.864,
  "SparkLend": 0.677
 }
}
```

Economics: net APR 0.28%, $40,748 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $44 of $15099 pool fees (0.29%) across 145 episodes by 10 operator(s)

```json
{
 "episodes": 145,
 "fee_taken_usd": 43.71,
 "pool_fees_usd": 15098.81,
 "share_of_fees": 0.0029,
 "swap_usd_bracketed": 628566,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 42,
   "fee_taken_usd": 26.53
  },
  {
   "sender": "0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2",
   "episodes": 13,
   "fee_taken_usd": 0.29
  },
  {
   "sender": "0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de",
   "episodes": 11,
   "fee_taken_usd": 6.35
  },
  {
   "sender": "0x654fae4aa229d104cabead47e56703f58b174be4",
   "episodes": 9,
   "fee_taken_usd": 0.85
  },
  {
   "sender": "0x6159af7a56d35da5efa508e0d90a435cbb59cbb1",
   "episodes": 6,
   "fee_taken_usd": 0.0
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR -0.00%, $-21,164 per year, no — net APR -0.00% below the 0.00% floor

### [info] 203 poisoning attempt(s) from 116 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0x6516ec2e4a4d7ab6d1be997e992fd0adebf51b877a501f63be36d1f76e8c7e9e",
   "big_eth": 193.97,
   "victim": "0x70866250eb6d24b3ee6e2330111fd06b6154ffc0",
   "impersonated": "0x18e24850fdeceee577da1e08c63b260cff69b962",
   "attacker": "0x18e20eba61b0ee6ca3089edbd674255323c1b962",
   "dust_tx": "0xfbc9a65a6714246747aca6f1587b1d7b284de22f3b4f822a116df8079658cff1",
   "seconds_after": 72
  },
  {
   "big_tx": "0x6516ec2e4a4d7ab6d1be997e992fd0adebf51b877a501f63be36d1f76e8c7e9e",
   "big_eth": 193.97,
   "victim": "0x70866250eb6d24b3ee6e2330111fd06b6154ffc0",
   "impersonated": "0x18e24850fdeceee577da1e08c63b260cff69b962",
   "attacker": "0x18e2f0a72c1c232ca4241b6b9091d39037fcb962",
   "dust_tx": "0x284a644ddf1c25cef29a28cfe678f305099adefb9fab71c822b8d6c9f0aeecd3",
   "seconds_after": 528
  },
  {
   "big_tx": "0x6516ec2e4a4d7ab6d1be997e992fd0adebf51b877a501f63be36d1f76e8c7e9e",
   "big_eth": 193.97,
   "victim": "0x70866250eb6d24b3ee6e2330111fd06b6154ffc0",
   "impersonated": "0x18e24850fdeceee577da1e08c63b260cff69b962",
   "attacker": "0x18e2429717a1d1c9d9c9ed0ed553fea282c5b962",
   "dust_tx": "0x80f00aa2c4bdb2f349459dc176699c8feb8326f260410e2cc0d88b50439f0fd4",
   "seconds_after": 780
  },
  {
   "big_tx": "0x6516ec2e4a4d7ab6d1be997e992fd0adebf51b877a501f63be36d1f76e8c7e9e",
   "big_eth": 193.97,
   "victim": "0x70866250eb6d24b3ee6e2330111fd06b6154ffc0",
   "impersonated": "0x18e24850fdeceee577da1e08c63b260cff69b962",
   "attacker": "0x18e624636f99e632fc82631c39299941cbe9b962",
   "dust_tx": "0xa0aab4fa30e8e6c67f9ef725a7728e198fa95f72bd204a2affb479edb6a204dd",
   "seconds_after": 840
  },
  {
   "big_tx": "0x6516ec2e4a4d7ab6d1be997e992fd0adebf51b877a501f63be36d1f76e8c7e9e",
   "big_eth": 193.97,
   "victim": "0x70866250eb6d24b3ee6e2330111fd06b6154ffc0",
   "impersonated": "0x18e24850fdeceee577da1e08c63b260cff69b962",
   "attacker": "0x18e20eba61b0ee6ca3089edbd674255323c1b962",
   "dust_tx": "0x91563cc93487db7eae1106894e3e33bccd05d12ede30a5341dfb4daf5a1e6e75",
   "seconds_after": 1056
  },
  {
   "big_tx": "0x6516ec2e4a4d7ab6d1be997e992fd0adebf51b877a501f63be36d1f76e8c7e9e",
   "big_eth": 193.97,
   "victim": "0x70866250eb6d24b3ee6e2330111fd06b6154ffc0",
   "impersonated": "0x18e24850fdeceee577da1e08c63b260cff69b962",
   "attacker": "0x18e2f0a72c1c232ca4241b6b9091d39037fcb962",
   "dust_tx": "0xdbfd822d6b857f18ab2e0ad8e6d823db3e6bdf
```

