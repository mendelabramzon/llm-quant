# Detector sweep — research/2026-09-07/live_5h

Ran 8 detector(s); 26 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 3.06 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `dollar_rate_outlier` | 1 | 3.02 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `gas_concentration` | 1 | 3.13 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `mass_distribution` | 5 | 5.02 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 0 | 3.38 | address labels the window contradicts, which is how a headline moves by a multiple |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 12 | 3.29 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

### [notable] unlabelled unknown 0x76f30e3f cycled $450.6M and ended the window flat (42 txs, 13 counterparties)

```json
{
 "address": "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a",
 "shape": "cycles",
 "gross_usd": 901242144,
 "txs": 42,
 "counterparties": 13,
 "tokens": 5,
 "pass_through_share": 0.429,
 "received_usd": 450620816,
 "sent_usd": 450621328,
 "retained_usd": -512,
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

### [notable] unlabelled unknown 0x5aae4d2f passed $125.0M through in 16 txs (62% ended flat, 21 counterparties)

```json
{
 "address": "0x5aae4d2f360e156de3416936049837a7bb685588",
 "shape": "pass-through",
 "gross_usd": 124979964,
 "txs": 16,
 "counterparties": 21,
 "tokens": 8,
 "pass_through_share": 0.625,
 "received_usd": 62489716,
 "sent_usd": 62490248,
 "retained_usd": -532,
 "retention": -0.0,
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

### [notable] unlabelled eoa 0x13f12f5d cycled $59.7M and ended the window flat (4 txs, 2 counterparties)

```json
{
 "address": "0x13f12f5d8b269197be17f0ad4f0a5b27463c7839",
 "shape": "cycles",
 "gross_usd": 119395186,
 "txs": 4,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 59697593,
 "sent_usd": 59697593,
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
  "Aave v3": 11208127,
  "SparkLend": 733366661,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.03,
  "SparkLend": 0.656
 },
 "dilution_basis": "modelled",
 "best_size": null,
 "marginal_apr_ladder": null
}
```

Economics: net APR 3.48%, $34,761,177 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 1.95pp more on Compound v3 USDC than SparkLend; best size $93.5M earns $793k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.592,
  "SparkLend": 3.542,
  "Compound v3 USDC": 5.491,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.586
 },
 "gap_pp_spot": 1.949,
 "gap_pp_despiked": 1.949,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2306826965,
  "SparkLend": 25638998,
  "Compound v3 USDC": 373112857,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.934,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.907
 },
 "dilution_basis": "modelled",
 "best_size": {
  "size_usd": 93523182,
  "apr_at_size_pct": 4.39,
  "over_low_venue_usd_per_year": 793437
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 5.489
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 5.476
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 5.418
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 5.146
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 4.33
  }
 ]
}
```

Economics: net APR 0.85%, $793,437 per year, GO — clears gas, impact and competition at this size

### [notable] base fee peaked 1.012 gwei (15.1x the 0.067 gwei median) across 202 blocks

```json
{
 "blocks": [
  25922877,
  25923079
 ],
 "spike_blocks": 202,
 "median_gwei": 0.0671,
 "peak_gwei": 1.0117,
 "top_gas_in_spike": [
  {
   "address": "0x4313c378cc91ea583c91387b9216e2c03096b27f",
   "label": null,
   "share_in_spike": 0.1232,
   "share_outside": 0.0259,
   "lift": 4.8,
   "gas_in_spike": 1847949205
  }
 ],
 "attribution": "0x4313c378cc91ea583c91387b9216e2c03096b27f holds 12% of requested gas inside the spike against 2.6% outside"
}
```

### [notable] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 14,693 recipients in 52 txs (293 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 15233,
 "recipients": 14693,
 "txs": 52,
 "blocks": 52,
 "transfers_per_tx": 292.9,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "19612611693823596325",
 "uniform_amount_share": 0.025,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 10,521 recipients in 20 txs (601 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 12024,
 "recipients": 10521,
 "txs": 20,
 "blocks": 20,
 "transfers_per_tx": 601.2,
 "carrier_contract": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "5000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDT to 9,428 recipients in 112 txs (101 per tx)

```json
{
 "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "token_symbol": "USDT",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 11289,
 "recipients": 9428,
 "txs": 112,
 "blocks": 112,
 "transfers_per_tx": 100.8,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "299",
 "uniform_amount_share": 0.013,
 "usd_median": 0.00029898794432000003,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] mint distribution: zero address (mint/burn) (known- sent 0x06450dee to 4,509 recipients in 36 txs (250 per tx)

```json
{
 "token": "0x06450dee7fd2fb8e39061434babcfc05599a6fb8",
 "token_symbol": null,
 "sender": "0x0000000000000000000000000000000000000000",
 "sender_label": "zero address (mint/burn) (known-canonical)",
 "kind": "mint distribution",
 "transfers": 8986,
 "recipients": 4509,
 "txs": 36,
 "blocks": 35,
 "transfers_per_tx": 249.6,
 "carrier_contract": "0x0000000000771a79d0fc7f3b7fe270eb4498f20b",
 "carrier_label": null,
 "carrier_share": 0.601,
 "median_raw_amount": "13854240000000000000000000",
 "uniform_amount_share": 0.095,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDC to 2,052 recipients in 112 txs (23 per tx)

```json
{
 "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "token_symbol": "USDC",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 2554,
 "recipients": 2052,
 "txs": 112,
 "blocks": 112,
 "transfers_per_tx": 22.8,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "356",
 "uniform_amount_share": 0.005,
 "usd_median": 0.00035596017072,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] unlabelled mev_bot 0x00000000 cycled $34.0M and ended the window flat (42 txs, 1 counterparties)

```json
{
 "address": "0x000000000035b5e5ad9019092c665357240f594e",
 "shape": "cycles",
 "gross_usd": 67914798,
 "txs": 42,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 33957825,
 "sent_usd": 33956973,
 "retained_usd": 852,
 "retention": 0.0,
 "is_contract": true,
 "emits_logs": false,
 "receives_calldata": true,
 "originates_txs": false,
 "vanity_zeros": 10,
 "suggested_kind": "mev_bot",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled venue 0x99ac8ca7 passed $63.7M through in 13 txs (77% ended flat, 6 counterparties)

```json
{
 "address": "0x99ac8ca7087fa4a2a1fb6357269965a2014abc35",
 "shape": "pass-through",
 "gross_usd": 63701123,
 "txs": 13,
 "counterparties": 6,
 "tokens": 2,
 "pass_through_share": 0.769,
 "received_usd": 31850650,
 "sent_usd": 31850473,
 "retained_usd": 177,
 "retention": 0.0,
 "is_contract": true,
 "emits_logs": true,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "venue",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled eoa 0xf42bcfd3 cycled $31.7M and ended the window flat (3 txs, 1 counterparties)

```json
{
 "address": "0xf42bcfd3dd5fcdd984d24fd2787383195c7f2b51",
 "shape": "cycles",
 "gross_usd": 63375480,
 "txs": 3,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 31687740,
 "sent_usd": 31687740,
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

### [info] unlabelled eoa 0x14681e4e cycled $28.3M and ended the window flat (10 txs, 2 counterparties)

```json
{
 "address": "0x14681e4e26f1b5b5774ae3b7f694ff08bbbeb65c",
 "shape": "cycles",
 "gross_usd": 56535299,
 "txs": 10,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 28267649,
 "sent_usd": 28267649,
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

### [info] unlabelled venue 0xd8246178 passed $50.7M through in 584 txs (100% ended flat, 6 counterparties)

```json
{
 "address": "0xd82461784eb72d4b67cbab077989eb215315e272",
 "shape": "pass-through",
 "gross_usd": 50749497,
 "txs": 584,
 "counterparties": 6,
 "tokens": 2,
 "pass_through_share": 1.0,
 "received_usd": 25374933,
 "sent_usd": 25374564,
 "retained_usd": 369,
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

### [info] unlabelled atomic bot pair 0x92872b97 passed $44.1M through in 5 txs (100% ended flat, 2 counterparties)

```json
{
 "address": "0x92872b97d89b54646d036e3afd2bccb84d8e3ca1",
 "shape": "pass-through",
 "gross_usd": 44091033,
 "txs": 5,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 22045516,
 "sent_usd": 22045516,
 "retained_usd": 0,
 "retention": 0.0,
 "is_contract": true,
 "emits_logs": true,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "atomic bot pair",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled eoa 0xb99a2c4c cycled $20.0M and ended the window flat (3 txs, 4 counterparties)

```json
{
 "address": "0xb99a2c4c1c4f1fc27150681b740396f6ce1cbcf5",
 "shape": "cycles",
 "gross_usd": 39997916,
 "txs": 3,
 "counterparties": 4,
 "tokens": 2,
 "pass_through_share": 0.333,
 "received_usd": 19998881,
 "sent_usd": 19999035,
 "retained_usd": -154,
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

### [info] unlabelled eoa 0xf07e3258 cycled $17.8M and ended the window flat (6 txs, 4 counterparties)

```json
{
 "address": "0xf07e3258395089514200209153a5d25da97bc22c",
 "shape": "cycles",
 "gross_usd": 35610873,
 "txs": 6,
 "counterparties": 4,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 17805436,
 "sent_usd": 17805436,
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

### [info] unlabelled bot 0x093272c0 cycled $16.3M and ended the window flat (6 txs, 3 counterparties)

```json
{
 "address": "0x093272c07700d3ca5301c3bf9b3a392624179e2f",
 "shape": "cycles",
 "gross_usd": 32657466,
 "txs": 6,
 "counterparties": 3,
 "tokens": 1,
 "pass_through_share": 0.5,
 "received_usd": 16333939,
 "sent_usd": 16323527,
 "retained_usd": 10412,
 "retention": 0.0006,
 "is_contract": true,
 "emits_logs": true,
 "receives_calldata": true,
 "originates_txs": false,
 "vanity_zeros": 1,
 "suggested_kind": "bot",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] USDT pays 3.05pp more on SparkLend than Compound v3 USDT; best size $151.0M earns $1.8M a year over Compound v3 USDT [one-block read, de-spiking unavailable]

```json
{
 "asset": "USDT",
 "high_venue": "SparkLend",
 "low_venue": "Compound v3 USDT",
 "supply_apr_spot_pct": {
  "Aave v3": 3.502,
  "SparkLend": 6.048,
  "Compound v3 USDT": 2.995
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.535
 },
 "gap_pp_spot": 3.053,
 "gap_pp_despiked": 3.053,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for SparkLend USDT: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 2978667039,
  "SparkLend": 344422448,
  "Compound v3 USDT": 185353647
 },
 "utilisation": {
  "Aave v3": 0.922,
  "SparkLend": 0.96,
  "Compound v3 USDT": 0.832
 },
 "dilution_basis": "modelled",
 "best_size": {
  "size_usd": 150994758,
  "apr_at_size_pct": 4.205,
  "over_low_venue_usd_per_year": 1826129
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 6.046
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 6.031
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 5.961
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 5.639
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 4.687
  }
 ]
}
```

Economics: net APR 1.21%, $1,826,129 per year, GO — clears gas, impact and competition at this size

### [info] PYUSD pays 3.17pp more on Aave v3 than SparkLend; best size $11.9M earns $107k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.75,
  "SparkLend": 0.579
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.171,
 "gap_pp_despiked": 3.171,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7738422,
  "SparkLend": 100000071
 },
 "utilisation": {
  "Aave v3": 0.862,
  "SparkLend": 0.166
 },
 "dilution_basis": "modelled",
 "best_size": {
  "size_usd": 11934478,
  "apr_at_size_pct": 1.475,
  "over_low_venue_usd_per_year": 106910
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.702
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.321
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 2.278
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 0.886
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.269
  }
 ]
}
```

Economics: net APR 0.90%, $106,910 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.58pp more on Aave v3 than SparkLend; best size $14.3M earns $41k a year over SparkLend [one-block read, de-spiking unavailable]

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
  "Aave v3": 131755802,
  "SparkLend": 308247707
 },
 "utilisation": {
  "Aave v3": 0.864,
  "SparkLend": 0.677
 },
 "dilution_basis": "modelled",
 "best_size": {
  "size_usd": 14277816,
  "apr_at_size_pct": 2.744,
  "over_low_venue_usd_per_year": 40675
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.039
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.019
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 2.93
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 2.557
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 1.729
  }
 ]
}
```

Economics: net APR 0.28%, $40,674 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $235 of $146261 pool fees (0.16%) across 144 episodes by 10 operator(s)

```json
{
 "episodes": 144,
 "fee_taken_usd": 234.58,
 "pool_fees_usd": 146260.86,
 "share_of_fees": 0.0016,
 "swap_usd_bracketed": 363663,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 55,
   "fee_taken_usd": 107.84
  },
  {
   "sender": "0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2",
   "episodes": 11,
   "fee_taken_usd": 21.24
  },
  {
   "sender": "0x7556699aa8e6a7c9c69bcfaf9debd05f8192b063",
   "episodes": 9,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0x654fae4aa229d104cabead47e56703f58b174be4",
   "episodes": 8,
   "fee_taken_usd": 1.08
  },
  {
   "sender": "0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de",
   "episodes": 8,
   "fee_taken_usd": 66.79
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR 0.00%, $6,134 per year, GO — clears gas, impact and competition at this size

### [info] 221 poisoning attempt(s) from 94 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0x8f6a60d3178f33a11cf5239692255a9db0d6427722c26020928a000bf4c397ec",
   "big_eth": 328.5,
   "victim": "0xadef93fe74a9ad629ff194009b6d03159437f70f",
   "impersonated": "0x48142e8feb9d108fb20ae356ffff424ee43a1718",
   "attacker": "0x481424a5c9a77630db966c14c4eb0faf25141718",
   "dust_tx": "0x22202505b132b3f934c31b608fe3b821a8177c283f25ece17b92d0f174e7685a",
   "seconds_after": 384
  },
  {
   "big_tx": "0x8f6a60d3178f33a11cf5239692255a9db0d6427722c26020928a000bf4c397ec",
   "big_eth": 328.5,
   "victim": "0xadef93fe74a9ad629ff194009b6d03159437f70f",
   "impersonated": "0x48142e8feb9d108fb20ae356ffff424ee43a1718",
   "attacker": "0x48149b67ccf4aaa0d3d17b556533f34de68d1718",
   "dust_tx": "0xb89be859cac1f79db1b2f2e27f29c2fc0cfc04c9f9c3e513827be17fe7ea1d1c",
   "seconds_after": 2064
  },
  {
   "big_tx": "0x8f6a60d3178f33a11cf5239692255a9db0d6427722c26020928a000bf4c397ec",
   "big_eth": 328.5,
   "victim": "0xadef93fe74a9ad629ff194009b6d03159437f70f",
   "impersonated": "0x48142e8feb9d108fb20ae356ffff424ee43a1718",
   "attacker": "0x481424a5c9a77630db966c14c4eb0faf25141718",
   "dust_tx": "0xcd9b6c26d481d7b45c5c8faeda75527051e04a1cc7f0f3d185b9d04fe41cff45",
   "seconds_after": 2496
  },
  {
   "big_tx": "0x8f6a60d3178f33a11cf5239692255a9db0d6427722c26020928a000bf4c397ec",
   "big_eth": 328.5,
   "victim": "0x48142e8feb9d108fb20ae356ffff424ee43a1718",
   "impersonated": "0xadef93fe74a9ad629ff194009b6d03159437f70f",
   "attacker": "0xadeffddb2fac9a7856a1293e64fafa45a0d0f70f",
   "dust_tx": "0x0c4b225e9471e77bf3b4d91bd5f6ac0d79a1372fa6af1040b245952b08514485",
   "seconds_after": 312
  },
  {
   "big_tx": "0x80d4a5b666362acb17f1359be50cbfdc6d9a876e1e8f5766a7cd82cedd869f37",
   "big_eth": 121.61,
   "victim": "0xfc983bd93bc2451d298a57b0d3e4d27d128989a2",
   "impersonated": "0xee4ec11e6a4ce16fac88eacb6b56ee1c726adc75",
   "attacker": "0xee4e00f21d5851cc0836285a4e8ece2ad5eedc75",
   "dust_tx": "0x8be429731c12f06823e0bbb9be07bff7a9dfbae531a6628fb16c76c0534b8fbd",
   "seconds_after": 24
  },
  {
   "big_tx": "0x80d4a5b666362acb17f1359be50cbfdc6d9a876e1e8f5766a7cd82cedd869f37",
   "big_eth": 121.61,
   "victim": "0xfc983bd93bc2451d298a57b0d3e4d27d128989a2",
   "impersonated": "0xee4ec11e6a4ce16fac88eacb6b56ee1c726adc75",
   "attacker": "0xeefa95727d1e8d08572d199c78f35a8ab36adc75",
   "dust_tx": "0x0298ca3a9b00583432b908aa81023c4e6ec2bec95
```

### [info] SparkLend USDT pays 6.05% against the Sky savings rate at 3.60%; no rate curve, so the size it survives is unknown [one-block read, de-spiking unavailable]

```json
{
 "venue": "SparkLend",
 "asset": "USDT",
 "supply_apr_spot_pct": 6.048,
 "supply_apr_window_median_pct": null,
 "spiked": false,
 "despike_unavailable": true,
 "benchmark": "Sky savings rate",
 "benchmark_pct": 3.6,
 "gap_pp": 2.448,
 "supplied_usd": 344422448,
 "borrowed_usd": 330628608,
 "available_usd": 13793840,
 "utilisation": 0.96,
 "curve": null,
 "marginal_apr_ladder": [],
 "best": null,
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 2.45%, $24,480 per year, GO — clears gas, impact and competition at this size

