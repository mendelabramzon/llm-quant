# Detector sweep — research/2026-09-10/live_10h

Ran 16 detector(s); 68 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 11.22 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `borrow_cost` | 5 | 0.00 | cheapest venue to borrow each asset, capped by the liquidity actually withdrawable there |
| `delegated_dust` | 1 | 14.83 | mass dust fan-out inside EIP-7702 / executeBatch calldata, from senders that mimic the recipient's counterparties |
| `dollar_rate_outlier` | 1 | 0.00 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `fixed_vs_floating` | 15 | 0.01 | Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth |
| `gas_concentration` | 1 | 23.00 | base-fee spikes attributed to the contract whose gas demand caused them |
| `honeypot_signature` | 3 | 12.98 | tokens whose buyers cannot sell: reverting sales, confiscatory taxes, buyers without sellers |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `liquidity_blackout` | 0 | 0.01 | lending reserves whose withdrawable liquidity collapses, and the time of day it happens |
| `lp_marginal_yield` | 10 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 7 | 16.09 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 2 | 11.82 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 2 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `recycled_swap_volume` | 2 | 11.93 | large same-transaction, same-pool v2-style swaps with nearly closed token positions |
| `solver_fingerprint` | 12 | 10.84 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

### [high] 0x59aab1bd… sprayed 175,378 dust legs from 11,956 delegated accounts at 20,729 wallets; 33.0% of testable legs came from a lookalike of the recipient's own counterparty

```json
{
 "operator": "0x59aab1bd0d26290274398c07b55955c15425e16b",
 "operator_label": null,
 "dust_legs": 175378,
 "executing_accounts": 11956,
 "recipients": 20729,
 "legs_with_a_testable_recipient": 84483,
 "legs_from_a_lookalike_counterparty": 27872,
 "lookalike_rate": 0.3299,
 "tokens": {
  "0xdac17f958d2ee523a2206206994597c13d831ec7": 27168,
  "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 25416,
  "0x6b175474e89094c44da98b954eedeac495271d0f": 90
 },
 "native_legs": 122704,
 "total_wei_moved": 12270400000000,
 "examples": [
  {
   "victim": "0x8dcc25c749a6216e2c387ec789624df3fea59f99",
   "dust_from": "0xe44e3a363702709df71a476e0d404b11156415cf",
   "mimics": "0xe44ed4605016a0a1c064270825c01b5ae60615cf",
   "tx": "0x49f54e058f4d34b90c13d3b9ad4a03b3b396d7f8eb05d13961af3402b69e1a9c"
  },
  {
   "victim": "0x1665f5f9b6ef50645b8ad90f1cd6690606f696b9",
   "dust_from": "0x6bfcabbeb93fba56148f18e75bd7f1dddf39c46d",
   "mimics": "0x6bfcbfcb0e5ac84511d28c3d4624feee8839c46d",
   "tx": "0x49f54e058f4d34b90c13d3b9ad4a03b3b396d7f8eb05d13961af3402b69e1a9c"
  },
  {
   "victim": "0x0702f80982ecf999b15afb7ae8a14a91894677f5",
   "dust_from": "0xea3ef1e33afe76fd0dfd75037d96f6d3a0ea7324",
   "mimics": "0xea3e1c459dce114449df0ff011b7a10fd3ea7324",
   "tx": "0x49f54e058f4d34b90c13d3b9ad4a03b3b396d7f8eb05d13961af3402b69e1a9c"
  },
  {
   "victim": "0x4e774e14ab943fb9680174a2354e351f83539aab",
   "dust_from": "0xf8c214321f4993926f4123f772a73fb4f9650b35",
   "mimics": "0xf8c29758f0dd604338b11415694ad4567b180b35",
   "tx": "0x49f54e058f4d34b90c13d3b9ad4a03b3b396d7f8eb05d13961af3402b69e1a9c"
  }
 ],
 "note": "lookalike = first 4 and last 4 hex characters shared with an address the recipient transacted with inside this window; a victim copying from a truncated history sees the same string. The rate is a floor: only in-window counterparties can be tested."
}
```

### [notable] unlabelled eoa 0x0ea04126 passed $11.1B through in 9 txs (100% ended flat, 3 counterparties)

```json
{
 "address": "0x0ea041260095b20feda41ef4fdbef7d801f4c438",
 "shape": "pass-through",
 "gross_usd": 11083212925,
 "txs": 9,
 "counterparties": 3,
 "tokens": 3,
 "pass_through_share": 1.0,
 "received_usd": 5541606462,
 "sent_usd": 5541606462,
 "retained_usd": 0,
 "retention": -0.0,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": true,
 "originates_txs": true,
 "vanity_zeros": 1,
 "suggested_kind": "eoa",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled unknown 0x76f30e3f cycled $977.4M and ended the window flat (90 txs, 22 counterparties)

```json
{
 "address": "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a",
 "shape": "cycles",
 "gross_usd": 1954745928,
 "txs": 90,
 "counterparties": 22,
 "tokens": 8,
 "pass_through_share": 0.289,
 "received_usd": 977371739,
 "sent_usd": 977374189,
 "retained_usd": -2450,
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

### [notable] unlabelled atomic bot pair 0x26de7861 passed $1.6B through in 26 txs (100% ended flat, 2 counterparties)

```json
{
 "address": "0x26de7861e213a5351f6ed767d00e0839930e9ee1",
 "shape": "pass-through",
 "gross_usd": 1560000008,
 "txs": 26,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 780000004,
 "sent_usd": 780000004,
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

### [notable] unlabelled atomic bot pair 0x772cff0b passed $960.1M through in 16 txs (100% ended flat, 4 counterparties)

```json
{
 "address": "0x772cff0be38a6ed31aeae479cbcb26d54b8404cf",
 "shape": "pass-through",
 "gross_usd": 960148341,
 "txs": 16,
 "counterparties": 4,
 "tokens": 2,
 "pass_through_share": 1.0,
 "received_usd": 480092980,
 "sent_usd": 480055361,
 "retained_usd": 37619,
 "retention": 0.0001,
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

### [notable] unlabelled venue 0x04ca7a7e passed $600.8M through in 10 txs (100% ended flat, 7 counterparties)

```json
{
 "address": "0x04ca7a7e602335a261b63128e89d43b6fe1e2c87",
 "shape": "pass-through",
 "gross_usd": 600809447,
 "txs": 10,
 "counterparties": 7,
 "tokens": 2,
 "pass_through_share": 1.0,
 "received_usd": 300418681,
 "sent_usd": 300390765,
 "retained_usd": 27916,
 "retention": 0.0001,
 "is_contract": true,
 "emits_logs": true,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 1,
 "suggested_kind": "venue",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled unknown 0xb8d4a4df cycled $231.0M and ended the window flat (6 txs, 1 counterparties)

```json
{
 "address": "0xb8d4a4dfaa73c2c81868bf8c86a0f197c92cc31d",
 "shape": "cycles",
 "gross_usd": 461946930,
 "txs": 6,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 230973465,
 "sent_usd": 230973465,
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

### [notable] unlabelled unknown 0x491edfb0 cycled $204.9M and ended the window flat (9 txs, 11 counterparties)

```json
{
 "address": "0x491edfb0b8b608044e227225c715981a30f3a44e",
 "shape": "cycles",
 "gross_usd": 409813745,
 "txs": 9,
 "counterparties": 11,
 "tokens": 4,
 "pass_through_share": 0.333,
 "received_usd": 204906873,
 "sent_usd": 204906873,
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

### [notable] unlabelled bot 0xebf6c883 cycled $115.1M and ended the window flat (34 txs, 16 counterparties)

```json
{
 "address": "0xebf6c883a1d60ab38c8ed4780aadbfe4c805ed4f",
 "shape": "cycles",
 "gross_usd": 230371377,
 "txs": 34,
 "counterparties": 16,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 115087205,
 "sent_usd": 115284171,
 "retained_usd": -196966,
 "retention": -0.0017,
 "is_contract": true,
 "emits_logs": false,
 "receives_calldata": true,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "bot",
 "why": "it received and returned the same total across separate transactions, so it holds nothing over the window even though no single transaction nets out: a position opened and closed across blocks",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled venue 0x99926ab8 passed $221.9M through in 13 txs (92% ended flat, 7 counterparties)

```json
{
 "address": "0x99926ab8e1b589500ae87977632f13cf7f70f242",
 "shape": "pass-through",
 "gross_usd": 221874540,
 "txs": 13,
 "counterparties": 7,
 "tokens": 5,
 "pass_through_share": 0.923,
 "received_usd": 123268005,
 "sent_usd": 98606535,
 "retained_usd": 24661470,
 "retention": 0.2001,
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

### [notable] unlabelled unknown 0x629ad4d7 passed $133.3M through in 4 txs (100% ended flat, 3 counterparties)

```json
{
 "address": "0x629ad4d779f46b8a1491d3f76f7e97cb04d8b1cd",
 "shape": "pass-through",
 "gross_usd": 133295533,
 "txs": 4,
 "counterparties": 3,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 66647767,
 "sent_usd": 66647767,
 "retained_usd": 0,
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

### [notable] unlabelled atomic bot pair 0x26512a41 passed $123.3M through in 3 txs (100% ended flat, 2 counterparties)

```json
{
 "address": "0x26512a41c8406800f21094a7a7a0f980f6e25d43",
 "shape": "pass-through",
 "gross_usd": 123295553,
 "txs": 3,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 61647777,
 "sent_usd": 61647777,
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

### [notable] unlabelled mev_bot 0x00000000 cycled $61.3M and ended the window flat (90 txs, 1 counterparties)

```json
{
 "address": "0x000000000035b5e5ad9019092c665357240f594e",
 "shape": "cycles",
 "gross_usd": 122693984,
 "txs": 90,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 61349762,
 "sent_usd": 61344222,
 "retained_usd": 5540,
 "retention": 0.0001,
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

### [notable] USDS pays 3.45pp more on Sky SSR than Aave v3; rate does not dilute with size

```json
{
 "asset": "USDS",
 "high_venue": "Sky SSR",
 "low_venue": "Aave v3",
 "supply_apr_spot_pct": {
  "Aave v3": 0.148,
  "SparkLend": 2.318,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "SparkLend": 2.318
 },
 "gap_pp_spot": 3.452,
 "gap_pp_despiked": 3.452,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Sky SSR emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 9403896,
  "SparkLend": 869015506,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.036,
  "SparkLend": 0.656
 },
 "dilution_basis": "modelled",
 "best_size": null,
 "marginal_apr_ladder": null
}
```

Economics: net APR 3.45%, $34,516,960 per year, GO — clears gas, impact and competition at this size

### [notable] $19,819,951 of settled turnover in 1 same-pool atomic round trips; token positions almost close

```json
{
 "pool": "0x28cd762e49726a4f0725a2846c85d19462b3e563",
 "roundtrips": 1,
 "gross_priced_leg_usd": 19819950.863410585,
 "pool_net_priced_token_usd": -0.3581360036315525,
 "examples": [
  {
   "tx": "0x2d1fc502cbd8c511b2919aadcc0e013a453ae902ea268ef1d91abfc8ad513e40",
   "block": 25940870,
   "sender": "0x5c096ef846447cb935c5d247e4ab2a867ecc33a9",
   "gross_priced_leg_usd": 19819950.863410585,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-145220864583707",
   "pool_net_priced_token_usd": -0.3581360036315525,
   "closure_fractions": [
    0.0,
    3.613893895381711e-08
   ]
  }
 ],
 "note": "Gross turnover is preserved. Net here is only the pool\u2019s priced token delta; it excludes gas and other assets. A fee-rate times gross turnover estimate does not measure realizable LP profit through these price round trips."
}
```

### [notable] $14,796,862 of settled turnover in 3 same-pool atomic round trips; token positions almost close

```json
{
 "pool": "0xcb62c2d6894736d4216a41f5812bb9771de056d5",
 "roundtrips": 3,
 "gross_priced_leg_usd": 14796861.915716242,
 "pool_net_priced_token_usd": -0.29219182224695983,
 "examples": [
  {
   "tx": "0xf50f34a5a0885bff97fca92e6b48b07e413dc1124587ca01deca3f0b26b25992",
   "block": 25939240,
   "sender": "0x5afec0de001999766fb883860cae06f5932e6f32",
   "gross_priced_leg_usd": 4932287.305406387,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-39561677601924",
   "pool_net_priced_token_usd": -0.09756491365017385,
   "closure_fractions": [
    0.0,
    3.956173096944795e-08
   ]
  },
  {
   "tx": "0x6f5e4ed35fb08f8c74daa1ce20a924196cbc7a6607d4b521678387f81a6cd881",
   "block": 25941042,
   "sender": "0x5afec0de001999766fb883860cae06f5932e6f32",
   "gross_priced_leg_usd": 4932287.305238651,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-39493662318789",
   "pool_net_priced_token_usd": -0.09739717796179556,
   "closure_fractions": [
    0.0,
    3.949371559724854e-08
   ]
  },
  {
   "tx": "0x709cac9346ae05906fb0e6a9ed9f7afa24cec0f31ecfaec88c3b528e33ba50bd",
   "block": 25941732,
   "sender": "0x5afec0de001999766fb883860cae06f5932e6f32",
   "gross_priced_leg_usd": 4932287.305071204,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-39425763963627",
   "pool_net_priced_token_usd": -0.09722973063499042,
   "closure_fractions": [
    0.0,
    3.942581715316601e-08
   ]
  }
 ],
 "note": "Gross turnover is preserved. Net here is only the pool\u2019s priced token delta; it excludes gas and other assets. A fee-rate times gross turnover estimate does not measure realizable LP profit through these price round trips."
}
```

### [notable] USDS borrows 1.60pp cheaper on SparkLend than Aave v3; $298.8M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDS",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 3.926,
  "liquidity_usd": 298780480,
  "utilisation": 0.6561850996416866,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 5.529,
  "liquidity_usd": 9067578
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.926,
   "liquidity_usd": 298780480,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 5.529,
   "liquidity_usd": 9067578,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.603,
 "refinance_gas_usd": 1.568,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.60%, $4,789,910 per year, GO — clears gas, impact and competition at this size

### [notable] DAI borrows 0.68pp cheaper on SparkLend than Aave v3; $99.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "DAI",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.043,
  "liquidity_usd": 99720467,
  "utilisation": 0.676588136443915,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.722,
  "liquidity_usd": 17240278
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.043,
   "liquidity_usd": 99720467,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.722,
   "liquidity_usd": 17240278,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.678,
 "refinance_gas_usd": 1.568,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.68%, $676,513 per year, GO — clears gas, impact and competition at this size

### [notable] USDT pays 0.55pp more on Aave v3 than Compound v3 USDT; best size $120.9M earns $322k a year over Compound v3 USDT

```json
{
 "asset": "USDT",
 "high_venue": "Aave v3",
 "low_venue": "Compound v3 USDT",
 "supply_apr_spot_pct": {
  "Aave v3": 3.632,
  "SparkLend": 3.394,
  "Compound v3 USDT": 3.087
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.633,
  "SparkLend": 3.394
 },
 "gap_pp_spot": 0.545,
 "gap_pp_despiked": 0.546,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 2966640758,
  "SparkLend": 338360020,
  "Compound v3 USDT": 181757094
 },
 "utilisation": {
  "Aave v3": 0.939,
  "SparkLend": 0.942,
  "Compound v3 USDT": 0.857
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 120857079,
  "apr_at_size_pct": 3.353,
  "over_low_venue_usd_per_year": 322088
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.632
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.63
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.62
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.572
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 3.399
  }
 ]
}
```

Economics: net APR 0.27%, $322,087 per year, GO — clears gas, impact and competition at this size

### [notable] USDT borrows 1.48pp cheaper on Morpho Blue than Aave v3; $6.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDT",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 2.815,
  "liquidity_usd": 6650127,
  "utilisation": 0.896629,
  "collateral_required": "sUSDS (0xa3931d71, LLTV 96.5%)",
  "market": "0x26b178d49895f80c"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.297,
  "liquidity_usd": 180135513
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 2.815,
   "liquidity_usd": 6650127,
   "collateral": "sUSDS (0xa3931d71, LLTV 96.5%)"
  },
  {
   "venue": "Compound v3 USDT",
   "borrow_apy_pct": 3.882,
   "liquidity_usd": 25903933,
   "collateral": "the Comet\u2019s listed collaterals"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.003,
   "liquidity_usd": 19554419,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.297,
   "liquidity_usd": 180135513,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.481,
 "refinance_gas_usd": 1.568,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.48%, $98,510 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v3 USDC/USDT: $1.0M in a ±0.01% band earns 1.2bp of fees less 0.0bp of divergence over 10.0h (10.7% a year if it repeats)

```json
{
 "pool": "0x3416cf6c708da44db2624d63ea0aaef7113527c6",
 "venue": "uniswap_v3",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.015,
 "band_quoted_pct": 0.015,
 "concentration_multiplier": 13334.8,
 "band_ladder": [
  {
   "band_pct": 0.015,
   "apr_pct_at_10000": 12.42
  },
  {
   "band_pct": 0.03,
   "apr_pct_at_10000": 6.21
  },
  {
   "band_pct": 0.075,
   "apr_pct_at_10000": 2.49
  },
  {
   "band_pct": 0.3,
   "apr_pct_at_10000": 0.62
  }
 ],
 "pool_band_capital_usd": 6293262,
 "full_range_capital_usd": 83919603002,
 "passive_fees_usd": 893.47,
 "volume_usd": 8938051,
 "swaps": 558,
 "annualisation_factor": 876.0,
 "n_takers": 377,
 "top_taker": "0x6b063481f8216b5624ec496dd72376bef00faffd",
 "top_taker_share": 0.3491,
 "taker_herfindahl": 0.2318,
 "apr_band_1pct_as_reported": 0.0019,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1.417,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.417,
   "over_benchmark_usd": 1.01,
   "annualised_net_apr_pct": 12.42
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 1.409,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.409,
   "over_benchmark_usd": 4.99,
   "annualised_net_apr_pct": 12.34
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 1.365,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.365,
   "over_benchmark_usd": 23.86,
   "annualised_net_apr_pct": 11.96
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 1.225,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.225,
   "over_benchmark_usd": 81.41,
   "annualised_net_apr_pct": 10.73
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 10.73%, $71,315 per year, GO — nets 10.73% a year at $1,000,000 in a ±0.015% band against a 3.60% savings rate

### [notable] uniswap_v4 USDC/USDG: $1.0M in a ±0.02% band earns 0.9bp of fees less 0.0bp of divergence over 10.0h (8.2% a year if it repeats)

```json
{
 "pool": "0xb90d11907f96a9d5fd8979ef271d3bb9b90052d9299d1f95faa5168c55bcb716",
 "venue": "uniswap_v4",
 "pair": "USDC/USDG",
 "stable_pair": true,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.024,
 "band_quoted_pct": 0.024,
 "concentration_multiplier": 8334.8,
 "band_ladder": [
  {
   "band_pct": 0.024,
   "apr_pct_at_10000": 15.32
  },
  {
   "band_pct": 0.048,
   "apr_pct_at_10000": 7.7
  },
  {
   "band_pct": 0.12,
   "apr_pct_at_10000": 3.09
  },
  {
   "band_pct": 0.48,
   "apr_pct_at_10000": 0.78
  }
 ],
 "pool_band_capital_usd": 1133460,
 "full_range_capital_usd": 9447196187,
 "passive_fees_usd": 199.99,
 "volume_usd": 2438861,
 "swaps": 109,
 "annualisation_factor": 876.0,
 "n_takers": 64,
 "top_taker": "0xf70da97812cb96acdf810712aa562db8dfa3dbef",
 "top_taker_share": 0.5765,
 "taker_herfindahl": 0.3448,
 "apr_band_1pct_as_reported": 0.0037,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1.749,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.749,
   "over_benchmark_usd": 1.34,
   "annualised_net_apr_pct": 15.32
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 1.69,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.69,
   "over_benchmark_usd": 6.39,
   "annualised_net_apr_pct": 14.8
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 1.446,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.446,
   "over_benchmark_usd": 25.87,
   "annualised_net_apr_pct": 12.66
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.937,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.937,
   "over_benchmark_usd": 52.64,
   "annualised_net_apr_pct": 8.21
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 8.21%, $46,113 per year, GO — nets 8.21% a year at $1,000,000 in a ±0.024% band against a 3.60% savings rate

### [notable] DAI pays 0.61pp more on Aave v3 than SparkLend; best size $7.1M earns $22k a year over SparkLend

```json
{
 "asset": "DAI",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.077,
  "SparkLend": 2.459
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.07
 },
 "gap_pp_spot": 0.618,
 "gap_pp_despiked": 0.611,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 131498628,
  "SparkLend": 308338926
 },
 "utilisation": {
  "Aave v3": 0.869,
  "SparkLend": 0.677
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 7084742,
  "apr_at_size_pct": 2.771,
  "over_low_venue_usd_per_year": 22069
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.073
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.031
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 2.856
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 2.173
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.993
  }
 ]
}
```

Economics: net APR 0.31%, $22,069 per year, GO — clears gas, impact and competition at this size

### [notable] USDC borrows 1.29pp cheaper on Morpho Blue than Compound v3 USDC; $1.1M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDC",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 4.152,
  "liquidity_usd": 1117699,
  "utilisation": 0.638336,
  "collateral_required": "0xaf687b5ecb (0xaf687b5e, LLTV 86.0%)",
  "market": "0x908b037029b5c067"
 },
 "dearest": {
  "venue": "Compound v3 USDC",
  "borrow_apy_pct": 5.447,
  "liquidity_usd": 36092403
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 4.152,
   "liquidity_usd": 1117699,
   "collateral": "0xaf687b5ecb (0xaf687b5e, LLTV 86.0%)"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.268,
   "liquidity_usd": 2040972,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.293,
   "liquidity_usd": 142178742,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Compound v3 USDC",
   "borrow_apy_pct": 5.447,
   "liquidity_usd": 36092403,
   "collateral": "the Comet\u2019s listed collaterals"
  }
 ],
 "gap_pp": 1.295,
 "refinance_gas_usd": 1.568,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.29%, $14,472 per year, GO — clears gas, impact and competition at this size

### [notable] RLUSD borrows 0.67pp cheaper on Morpho Blue than Aave v3; $1.2M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "RLUSD",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.702,
  "liquidity_usd": 1240950,
  "utilisation": 0.9,
  "collateral_required": "cbBTC (0xcbb7c000, LLTV 86.0%)",
  "market": "0xffd010618ed3cb39"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.374,
  "liquidity_usd": 1857481
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.702,
   "liquidity_usd": 1240950,
   "collateral": "cbBTC (0xcbb7c000, LLTV 86.0%)"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.374,
   "liquidity_usd": 1857481,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.672,
 "refinance_gas_usd": 1.568,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.67%, $8,337 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 0.98pp more on Compound v3 USDC than SparkLend; best size $615k earns $3k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.625,
  "SparkLend": 3.542,
  "Compound v3 USDC": 4.524,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.635
 },
 "gap_pp_spot": 0.982,
 "gap_pp_despiked": 0.982,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2309822842,
  "SparkLend": 26204164,
  "Compound v3 USDC": 376036297,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.938,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.904
 },
 "dilution_basis": "sampled",
 "best_size": {
  "size_usd": 615441,
  "apr_at_size_pct": 4.052,
  "over_low_venue_usd_per_year": 3141
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 4.448
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.758
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.212
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.052
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 2.571
  }
 ]
}
```

Economics: net APR 0.51%, $3,141 per year, GO — clears gas, impact and competition at this size

### [notable] PT-SUSDS-26NOV2026 implies 4.92% fixed for 77 days against Sky savings rate at 3.60% — term premium

```json
{
 "market": "0x9c560ebaf78e596cbcc27411d633a74d628dd7dc",
 "pt": "0xdc169abe56461a2e0c034da431ac2a3ebf596094",
 "pt_symbol": "PT-SUSDS-26NOV2026",
 "implied_apy_pct": 4.924,
 "days_to_maturity": 77.14417824074074,
 "pt_to_asset": 0.9898931334574876,
 "underlying": "SUSDS",
 "comparison": "Sky savings rate",
 "floating_pct": 3.6,
 "gap_pp": 1.324,
 "classification": "term premium",
 "pt_depth_units": 757701,
 "pt_depth_usd": 750043,
 "oracle_ready": true,
 "why": "the same credit pays more fixed than floating for a fixed term, which is a view on the floating rate and nothing else"
}
```

Economics: net APR 0.66%, $344 per year, GO — clears gas, impact and competition at this size

### [notable] base fee peaked 0.422 gwei (3.6x the 0.119 gwei median) across 151 blocks

```json
{
 "blocks": [
  25940634,
  25940858
 ],
 "spike_blocks": 151,
 "median_gwei": 0.1187,
 "peak_gwei": 0.4216,
 "top_gas_in_spike": [],
 "attribution": "no single contract exceeds the share threshold: broad congestion, not one actor"
}
```

### [notable] 0x7db113ecd5: 28 buyers, 5 sellers, 64% of 11 sell attempts emitted no logs — sales fail or are taxed, but sellers do exist — a gate on some holders, or a thin pool

```json
{
 "token": "0x7db113ecd514c88b8b1a83c8c374793172558f74",
 "symbol": null,
 "label": null,
 "distinct_buyers": 28,
 "distinct_sellers": 5,
 "seller_to_buyer_ratio": 0.1786,
 "buy_legs": 41,
 "sell_legs": 8,
 "router_calls_naming_it": 11,
 "of_which_emitted_no_logs": 7,
 "fail_rate": 0.636,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 0.9016,
 "fee_beneficiary": "0x7db113ecd514c88b8b1a83c8c374793172558f74",
 "distinct_secondary_recipients": 1,
 "fee_concentration": 1.0,
 "fee_is_a_fee_not_a_split_route": true,
 "buy_leg_tax": 0.0984,
 "first_seen_block": 25940646,
 "verdict": "sales fail or are taxed, but sellers do exist \u2014 a gate on some holders, or a thin pool",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [notable] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 10,020 recipients in 20 txs (551 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 11022,
 "recipients": 10020,
 "txs": 20,
 "blocks": 20,
 "transfers_per_tx": 551.1,
 "carrier_contract": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "5000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] mint distribution: zero address (mint/burn) (known- sent 0x06450dee to 5,171 recipients in 66 txs (156 per tx)

```json
{
 "token": "0x06450dee7fd2fb8e39061434babcfc05599a6fb8",
 "token_symbol": null,
 "sender": "0x0000000000000000000000000000000000000000",
 "sender_label": "zero address (mint/burn) (known-canonical)",
 "kind": "mint distribution",
 "transfers": 10325,
 "recipients": 5171,
 "txs": 66,
 "blocks": 62,
 "transfers_per_tx": 156.4,
 "carrier_contract": "0x0de8bf93da2f7eecb3d9169422413a9bef4ef628",
 "carrier_label": null,
 "carrier_share": 0.951,
 "median_raw_amount": "12345112000000000000000000",
 "uniform_amount_share": 0.165,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 5,098 recipients in 120 txs (54 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 6525,
 "recipients": 5098,
 "txs": 120,
 "blocks": 120,
 "transfers_per_tx": 54.4,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "29413350719891758869",
 "uniform_amount_share": 0.01,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] exchange Bitstamp 4 (model-memory) moved 98% of its flow with one counterparty

```json
{
 "address": "0x1522900b6dafac587d499a862861c0869be6e428",
 "label": "Bitstamp 4 (model-memory)",
 "source": "model-memory",
 "counterparty": "0x7f604d597c15b2e2f60dc645844f68b1d781b752",
 "counterparty_label": "hot wallet (behaviour, day study)",
 "share": 0.976,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] exchange Binance 28 (model-memory) moved 100% of its flow with one counterparty

```json
{
 "address": "0x5a52e96bacdabb82fd05763e25335261b270efcb",
 "label": "Binance 28 (model-memory)",
 "source": "model-memory",
 "counterparty": "0x28c6c06298d514db089934071355e5743bf21d60",
 "counterparty_label": "Binance 14 (model-memory)",
 "share": 1.0,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] uniswap_v3 0x77e0…0a44/WETH: $1.0M in a ±0.01% band earns 72.6bp of fees less 0.0bp of divergence over 10.0h (636.1% a year if it repeats)

```json
{
 "pool": "0x433a00819c771b33fa7223a5b3499b24fbcd1bbc",
 "venue": "uniswap_v3",
 "pair": "0x77e0\u20260a44/WETH",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 44509.35
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 44509.35
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 44509.35
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 44509.35
  }
 ],
 "pool_band_capital_usd": 4353,
 "full_range_capital_usd": 87064371,
 "passive_fees_usd": 7292.67,
 "volume_usd": 729267,
 "swaps": 111,
 "annualisation_factor": 876.0,
 "n_takers": 56,
 "top_taker": "0x5b43453fce04b92e190f391a83136bfbecedefd1",
 "top_taker_share": 0.1525,
 "taker_herfindahl": 0.0548,
 "apr_band_1pct_as_reported": 14.785,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 5080.976,
   "divergence_bps_window": 0.0,
   "net_bps_window": 5080.976,
   "over_benchmark_usd": 5080.98,
   "annualised_net_apr_pct": 44509.35
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 1341.726,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1341.726,
   "over_benchmark_usd": 6708.63,
   "annualised_net_apr_pct": 11753.52
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 286.715,
   "divergence_bps_window": 0.0,
   "net_bps_window": 286.715,
   "over_benchmark_usd": 7167.87,
   "annualised_net_apr_pct": 2511.62
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 72.611,
   "divergence_bps_window": 0.0,
   "net_bps_window": 72.611,
   "over_benchmark_usd": 7261.06,
   "annualised_net_apr_pct": 636.07
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 636.07%, $6,360,689 per year, no — nets 636.07% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] uniswap_v3 USDC/0xbdf4…788b: $1.0M in a ±0.01% band earns 17.6bp of fees less 0.0bp of divergence over 10.0h (154.4% a year if it repeats)

```json
{
 "pool": "0xf8e349d1d827a6edf17ee673664cfad4ca78c533",
 "venue": "uniswap_v3",
 "pair": "USDC/0xbdf4\u2026788b",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 14037.18
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 14037.18
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 14037.18
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 14037.18
  }
 ],
 "pool_band_capital_usd": 1010,
 "full_range_capital_usd": 20193761,
 "passive_fees_usd": 1764.2,
 "volume_usd": 588065,
 "swaps": 247,
 "annualisation_factor": 876.0,
 "n_takers": 116,
 "top_taker": "0x5b43453fce04b92e190f391a83136bfbecedefd1",
 "top_taker_share": 0.2353,
 "taker_herfindahl": 0.0656,
 "apr_band_1pct_as_reported": 15.4208,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1602.418,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1602.418,
   "over_benchmark_usd": 1602.42,
   "annualised_net_apr_pct": 14037.18
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 345.856,
   "divergence_bps_window": 0.0,
   "net_bps_window": 345.856,
   "over_benchmark_usd": 1729.28,
   "annualised_net_apr_pct": 3029.7
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 70.284,
   "divergence_bps_window": 0.0,
   "net_bps_window": 70.284,
   "over_benchmark_usd": 1757.1,
   "annualised_net_apr_pct": 615.69
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 17.624,
   "divergence_bps_window": 0.0,
   "net_bps_window": 17.624,
   "over_benchmark_usd": 1762.42,
   "annualised_net_apr_pct": 154.39
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 154.39%, $1,543,880 per year, no — nets 154.39% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] PT-ROY-JT-APYUSD-5NOV2026 implies 308.67% fixed for 56 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x5949c3bfdf9babd759170a3a75c4fe52b03e6797",
 "pt": "0xd70be760f0bc3009db4563fe0b9eee54883adb50",
 "pt_symbol": "PT-ROY-JT-APYUSD-5NOV2026",
 "implied_apy_pct": 308.667,
 "days_to_maturity": 56.14417824074074,
 "pt_to_asset": 0.8053030568283613,
 "underlying": "ROY",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 305.067,
 "classification": "credit spread",
 "pt_depth_units": 498641,
 "pt_depth_usd": 401557,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 301.83%, $303,003 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v4 0x98a8…4665/USDC: $1.0M in a ±0.01% band earns 2.2bp of fees less 0.0bp of divergence over 10.0h (19.6% a year if it repeats)

```json
{
 "pool": "0x9f2d9491277a9f2551c1f7533c1789aa6023bba0c5e9397e8a019cac5c10fe7f",
 "venue": "uniswap_v4",
 "pair": "0x98a8\u20264665/USDC",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1424.11
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1424.11
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1424.11
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1424.11
  }
 ],
 "pool_band_capital_usd": 3786,
 "full_range_capital_usd": 75728339,
 "passive_fees_usd": 224.12,
 "volume_usd": 358596,
 "swaps": 65,
 "annualisation_factor": 876.0,
 "n_takers": 48,
 "top_taker": "0x7a27f9586d0895f045b80b3fb1d9d6ef4d54e9bc",
 "top_taker_share": 0.2335,
 "taker_herfindahl": 0.0951,
 "apr_band_1pct_as_reported": 0.5224,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 162.569,
   "divergence_bps_window": 0.0,
   "net_bps_window": 162.569,
   "over_benchmark_usd": 162.57,
   "annualised_net_apr_pct": 1424.11
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 41.669,
   "divergence_bps_window": 0.0,
   "net_bps_window": 41.669,
   "over_benchmark_usd": 208.34,
   "annualised_net_apr_pct": 365.02
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 8.831,
   "divergence_bps_window": 0.0,
   "net_bps_window": 8.831,
   "over_benchmark_usd": 220.78,
   "annualised_net_apr_pct": 77.36
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 2.233,
   "divergence_bps_window": 0.0,
   "net_bps_window": 2.233,
   "over_benchmark_usd": 223.27,
   "annualised_net_apr_pct": 19.56
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 19.56%, $195,585 per year, no — nets 19.56% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] uniswap_v3 0xa12c…f4f3/USDT: $1.0M in a ±0.01% band earns 2.1bp of fees less 0.0bp of divergence over 10.0h (18.4% a year if it repeats)

```json
{
 "pool": "0x4d68b530920d26c3b01c99fecc19e21011b72bbd",
 "venue": "uniswap_v3",
 "pair": "0xa12c\u2026f4f3/USDT",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1810.5
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1810.5
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1810.5
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1810.5
  }
 ],
 "pool_band_capital_usd": 194,
 "full_range_capital_usd": 3883013,
 "passive_fees_usd": 210.69,
 "volume_usd": 422223,
 "swaps": 552,
 "annualisation_factor": 876.0,
 "n_takers": 130,
 "top_taker": "0x5b43453fce04b92e190f391a83136bfbecedefd1",
 "top_taker_share": 0.1759,
 "taker_herfindahl": 0.0759,
 "apr_band_1pct_as_reported": 9.5774,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 206.678,
   "divergence_bps_window": 0.0,
   "net_bps_window": 206.678,
   "over_benchmark_usd": 206.68,
   "annualised_net_apr_pct": 1810.5
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 41.975,
   "divergence_bps_window": 0.0,
   "net_bps_window": 41.975,
   "over_benchmark_usd": 209.88,
   "annualised_net_apr_pct": 367.7
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 8.421,
   "divergence_bps_window": 0.0,
   "net_bps_window": 8.421,
   "over_benchmark_usd": 210.53,
   "annualised_net_apr_pct": 73.77
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 2.106,
   "divergence_bps_window": 0.0,
   "net_bps_window": 2.106,
   "over_benchmark_usd": 210.65,
   "annualised_net_apr_pct": 18.45
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 18.45%, $184,529 per year, no — nets 18.45% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] uniswap_v3 0x8b14…caea/USDC: $1.0M in a ±0.01% band earns 1.9bp of fees less 0.0bp of divergence over 10.0h (16.7% a year if it repeats)

```json
{
 "pool": "0x41a561b972039a9ccb975a4c17b84c9f95099e15",
 "venue": "uniswap_v3",
 "pair": "0x8b14\u2026caea/USDC",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1601.63
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1601.63
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1601.63
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1601.63
  }
 ],
 "pool_band_capital_usd": 460,
 "full_range_capital_usd": 9194831,
 "passive_fees_usd": 191.24,
 "volume_usd": 382476,
 "swaps": 630,
 "annualisation_factor": 876.0,
 "n_takers": 169,
 "top_taker": "0xba6b44209c5344e9fd2882dbac6da0c1cd680cb6",
 "top_taker_share": 0.2174,
 "taker_herfindahl": 0.0867,
 "apr_band_1pct_as_reported": 3.6712,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 182.835,
   "divergence_bps_window": 0.0,
   "net_bps_window": 182.835,
   "over_benchmark_usd": 182.83,
   "annualised_net_apr_pct": 1601.63
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 37.9,
   "divergence_bps_window": 0.0,
   "net_bps_window": 37.9,
   "over_benchmark_usd": 189.5,
   "annualised_net_apr_pct": 332.0
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 7.636,
   "divergence_bps_window": 0.0,
   "net_bps_window": 7.636,
   "over_benchmark_usd": 190.89,
   "annualised_net_apr_pct": 66.89
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 1.912,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.912,
   "over_benchmark_usd": 191.15,
   "annualised_net_apr_pct": 16.74
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 16.74%, $167,447 per year, no — nets 16.74% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] uniswap_v3 0x5a98…1b32/WETH: $1.0M in a ±0.01% band earns 1.7bp of fees less 0.0bp of divergence over 10.0h (15.3% a year if it repeats)

```json
{
 "pool": "0xcfecc1c9f3cb6190cb1ff7f65a130bfbe5107d38",
 "venue": "uniswap_v3",
 "pair": "0x5a98\u20261b32/WETH",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1480.97
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1480.97
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1480.97
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1480.97
  }
 ],
 "pool_band_capital_usd": 339,
 "full_range_capital_usd": 6778451,
 "passive_fees_usd": 174.79,
 "volume_usd": 352746,
 "swaps": 401,
 "annualisation_factor": 876.0,
 "n_takers": 178,
 "top_taker": "0x5b43453fce04b92e190f391a83136bfbecedefd1",
 "top_taker_share": 0.2604,
 "taker_herfindahl": 0.0762,
 "apr_band_1pct_as_reported": 4.5516,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 169.061,
   "divergence_bps_window": 0.0,
   "net_bps_window": 169.061,
   "over_benchmark_usd": 169.06,
   "annualised_net_apr_pct": 1480.97
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 34.723,
   "divergence_bps_window": 0.0,
   "net_bps_window": 34.723,
   "over_benchmark_usd": 173.61,
   "annualised_net_apr_pct": 304.17
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 6.982,
   "divergence_bps_window": 0.0,
   "net_bps_window": 6.982,
   "over_benchmark_usd": 174.55,
   "annualised_net_apr_pct": 61.16
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 1.747,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.747,
   "over_benchmark_usd": 174.73,
   "annualised_net_apr_pct": 15.31
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 15.31%, $153,063 per year, no — nets 15.31% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] rETH trades 20.5bp below NAV, 15.5bp after the 5.0bp round trip; burn into the Rocket Pool deposit pool, which is empty most of the time — conditional, so the exit may not be there when you want it

```json
{
 "asset": "rETH",
 "nav_source": "0xae78736c getExchangeRate()",
 "nav": 2888.763339,
 "market_vw_price": 2882.837547,
 "market_median": 2883.017591,
 "market_p10": 2882.465161,
 "discount_bps": 20.51,
 "traded_volume_usd": 232668,
 "implied_daily_volume_usd": 558403,
 "refills_needed_per_year": 365,
 "swaps": 21,
 "venues": {
  "uniswap_v3": 16,
  "curve": 2,
  "uniswap_v4": 3
 },
 "redemption": {
  "days": 1.0,
  "atomic": false,
  "availability": "conditional",
  "exit_bps": 5.0,
  "path": "burn into the Rocket Pool deposit pool, which is empty most of the time"
 },
 "net_edge_bps": 15.51,
 "price_dispersion_bps": 2.84,
 "discount_at_p10_bps": 21.8,
 "significance_vs_dispersion": 5.47,
 "dispersion_note": "the spread of an ETH-denominated claim also contains ETH\u2019s own move over the window, so this test is conservative here",
 "why": "the protocol pays NAV and the market paid less; the gap closes when you redeem, and the wait is the reason a bot cannot take it from you"
}
```

Economics: net APR 56.49%, $131,427 per year, GO — clears gas, impact and competition at this size

### [info] PT-APYUSD-5NOV2026 implies 14.12% fixed for 56 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xc5f938a8ef5f3bf9e72f5aa094baf5e03f4727d3",
 "pt": "0xb5be35d8ff83d431899b95851cb17a2b4bcef150",
 "pt_symbol": "PT-APYUSD-5NOV2026",
 "implied_apy_pct": 14.123,
 "days_to_maturity": 56.14417824074074,
 "pt_to_asset": 0.9798841545705176,
 "underlying": "APYUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 10.523,
 "classification": "credit spread",
 "pt_depth_units": 6484140,
 "pt_depth_usd": 6353706,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 7.29%, $115,774 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSDE-10DEC2026 implies 18.17% fixed for 91 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x90b70c407f1077f8eb92bf423b44cd92329b737a",
 "pt": "0x2ae4f59e500b6ddeb88c480edf277eda54a00205",
 "pt_symbol": "PT-REUSDE-10DEC2026",
 "implied_apy_pct": 18.169,
 "days_to_maturity": 91.14417824074074,
 "pt_to_asset": 0.9591698801166278,
 "underlying": "REUSDE",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 14.569,
 "classification": "credit spread",
 "pt_depth_units": 3586977,
 "pt_depth_usd": 3440520,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 12.58%, $108,169 per year, GO — clears gas, impact and competition at this size

### [info] PT-USD3-17DEC2026 implies 14.15% fixed for 98 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4a5067c3ff1abb7449244025b0e37feaf77d8e3e",
 "pt": "0x7f47c3e6b2c00fc4eb4d5ae50d0ab0ab6888eb4d",
 "pt_symbol": "PT-USD3-17DEC2026",
 "implied_apy_pct": 14.154,
 "days_to_maturity": 98.14417824074074,
 "pt_to_asset": 0.965031643842289,
 "underlying": "USD3",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 10.554,
 "classification": "credit spread",
 "pt_depth_units": 4538715,
 "pt_depth_usd": 4380003,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 8.70%, $95,301 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSD-10DEC2026 implies 11.12% fixed for 91 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x13285bcbc27f92b47b4edb99d744c07b48c977c0",
 "pt": "0xecfafdc7741323a945a163ed068b5a3c43483957",
 "pt_symbol": "PT-REUSD-10DEC2026",
 "implied_apy_pct": 11.12,
 "days_to_maturity": 91.14417824074074,
 "pt_to_asset": 0.9740149524325031,
 "underlying": "REUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 7.52,
 "classification": "credit spread",
 "pt_depth_units": 4133294,
 "pt_depth_usd": 4025890,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.53%, $55,627 per year, GO — clears gas, impact and competition at this size

### [info] PT-SUSDX-3DEC2026 implies 20.10% fixed for 84 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x5e572498e9f83650f0ff24194999bddb4b390928",
 "pt": "0x06ebad062fd573ca31a72d6dfb0f425da2153985",
 "pt_symbol": "PT-SUSDX-3DEC2026",
 "implied_apy_pct": 20.098,
 "days_to_maturity": 84.14417824074074,
 "pt_to_asset": 0.9586590132995738,
 "underlying": "SUSDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 16.498,
 "classification": "credit spread",
 "pt_depth_units": 1593213,
 "pt_depth_usd": 1527348,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 14.34%, $54,753 per year, GO — clears gas, impact and competition at this size

### [info] PYUSD pays 3.28pp more on Aave v3 than SparkLend; best size $4.4M earns $50k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.888,
  "SparkLend": 0.608
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.28,
 "gap_pp_despiked": 3.28,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7587149,
  "SparkLend": 100000828
 },
 "utilisation": {
  "Aave v3": 0.88,
  "SparkLend": 0.173
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 4398906,
  "apr_at_size_pct": 1.742,
  "over_low_venue_usd_per_year": 49894
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.798
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.117
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 1.602
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 0.352
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.071
  }
 ]
}
```

Economics: net APR 1.13%, $49,894 per year, GO — clears gas, impact and competition at this size

### [info] PT-SUSD3-17DEC2026 implies 22.88% fixed for 98 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x7972de1c2f9f11f622a188fbae8c0a943880424f",
 "pt": "0x41f45d21502bde8211e94d94ef2eeebcfc48a6ac",
 "pt_symbol": "PT-SUSD3-17DEC2026",
 "implied_apy_pct": 22.879,
 "days_to_maturity": 98.14417824074074,
 "pt_to_asset": 0.946108055850053,
 "underlying": "SUSD3",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 19.279,
 "classification": "credit spread",
 "pt_depth_units": 912690,
 "pt_depth_usd": 863504,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 17.43%, $37,621 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v4 0x01a8…50ad/WBTC: $1.0M in a ±0.01% band earns 0.4bp of fees less 0.0bp of divergence over 10.0h (3.5% a year if it repeats)

```json
{
 "pool": "0x94ae557b1f24e1360ea34283686ef3af173d89d7d1bab66d8ae19198a9a0cde0",
 "venue": "uniswap_v4",
 "pair": "0x01a8\u202650ad/WBTC",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 47.99
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 47.99
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 47.99
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 47.99
  }
 ],
 "pool_band_capital_usd": 68476,
 "full_range_capital_usd": 1369626412,
 "passive_fees_usd": 42.99,
 "volume_usd": 343960,
 "swaps": 34,
 "annualisation_factor": 876.0,
 "n_takers": 28,
 "top_taker": "0x0ea041260095b20feda41ef4fdbef7d801f4c438",
 "top_taker_share": 0.3648,
 "taker_herfindahl": 0.1769,
 "apr_band_1pct_as_reported": 0.0055,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 5.478,
   "divergence_bps_window": 0.0,
   "net_bps_window": 5.478,
   "over_benchmark_usd": 5.48,
   "annualised_net_apr_pct": 47.99
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 3.629,
   "divergence_bps_window": 0.0,
   "net_bps_window": 3.629,
   "over_benchmark_usd": 18.14,
   "annualised_net_apr_pct": 31.79
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 1.35,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.35,
   "over_benchmark_usd": 33.75,
   "annualised_net_apr_pct": 11.82
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.402,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.402,
   "over_benchmark_usd": 40.23,
   "annualised_net_apr_pct": 3.52
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 3.52%, $35,241 per year, no — nets 3.52% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] PT-STRUSD-26NOV2026 implies 11.79% fixed for 77 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xac028348c46d3455899a2b9b50077c11960eaddb",
 "pt": "0x74299580811e1c3c1a2831db079ba0a8f513998f",
 "pt_symbol": "PT-STRUSD-26NOV2026",
 "implied_apy_pct": 11.79,
 "days_to_maturity": 77.14417824074074,
 "pt_to_asset": 0.9767186185341614,
 "underlying": "STRUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 8.19,
 "classification": "credit spread",
 "pt_depth_units": 1806024,
 "pt_depth_usd": 1763977,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.84%, $25,735 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v4 ETH/LINK: $50.0k in a ±1.78% band earns 47.9bp of fees less 44.4bp of divergence over 10.0h (30.8% a year if it repeats)

```json
{
 "pool": "0xb2b5618903d74bbac9e9049a035c3827afc4487cde3b994a1568b050f4c8e2e4",
 "venue": "uniswap_v4",
 "pair": "ETH/LINK",
 "stable_pair": false,
 "window_hours": 10.0,
 "observed_price_range_pct": 1.783,
 "band_quoted_pct": 1.783,
 "concentration_multiplier": 113.7,
 "band_ladder": [
  {
   "band_pct": 1.783,
   "apr_pct_at_10000": 39.26
  },
  {
   "band_pct": 3.566,
   "apr_pct_at_10000": 20.43
  },
  {
   "band_pct": 8.915,
   "apr_pct_at_10000": 8.63
  },
  {
   "band_pct": 35.66,
   "apr_pct_at_10000": 2.57
  }
 ],
 "pool_band_capital_usd": 1960818,
 "full_range_capital_usd": 222882780,
 "passive_fees_usd": 9629.12,
 "volume_usd": 2751964,
 "swaps": 95,
 "annualisation_factor": 876.0,
 "n_takers": 69,
 "top_taker": "0x47da8dba29f6ed62fcd95acdaaeda07d6a947147",
 "top_taker_share": 0.2616,
 "taker_herfindahl": 0.1207,
 "apr_band_1pct_as_reported": 7.6258,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 48.859,
   "divergence_bps_window": 44.376,
   "net_bps_window": 4.482,
   "over_benchmark_usd": 4.48,
   "annualised_net_apr_pct": 39.26
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 47.887,
   "divergence_bps_window": 44.376,
   "net_bps_window": 3.51,
   "over_benchmark_usd": 17.55,
   "annualised_net_apr_pct": 30.75
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 43.555,
   "divergence_bps_window": 44.376,
   "net_bps_window": -0.822,
   "over_benchmark_usd": -20.54,
   "annualised_net_apr_pct": -7.2
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 32.522,
   "divergence_bps_window": 44.376,
   "net_bps_window": -11.854,
   "over_benchmark_usd": -1185.45,
   "annualised_net_apr_pct": -103.85
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 30.75%, $15,374 per year, no — nets 30.75% a year at $50,000 in a ±1.783% band, before any view on holding the pair

### [info] PT-USDX-3DEC2026 implies 15.24% fixed for 84 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x0bef762d2094ac80821c657dea6783fc43435292",
 "pt": "0xa4b3a2eec53863fe2c9ab0041d480cf964942e84",
 "pt_symbol": "PT-USDX-3DEC2026",
 "implied_apy_pct": 15.243,
 "days_to_maturity": 84.14417824074074,
 "pt_to_asset": 0.9678222031824487,
 "underlying": "USDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 11.643,
 "classification": "credit spread",
 "pt_depth_units": 626814,
 "pt_depth_usd": 606644,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 9.48%, $14,382 per year, GO — clears gas, impact and competition at this size

### [info] PT-USDAT-14JAN2027 implies 6.92% fixed for 126 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4ccf6deb3d1895373f604b418ff55d8adae8b846",
 "pt": "0xba96292ee7673e3b546cc90db6d97111cd9a314f",
 "pt_symbol": "PT-USDAT-14JAN2027",
 "implied_apy_pct": 6.915,
 "days_to_maturity": 126.14417824074074,
 "pt_to_asset": 0.977155431984973,
 "underlying": "USDAT",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 3.315,
 "classification": "credit spread",
 "pt_depth_units": 2084291,
 "pt_depth_usd": 2036676,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 1.88%, $9,549 per year, GO — clears gas, impact and competition at this size

### [info] PT-SIUSD-22OCT2026 implies 9.13% fixed for 42 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x1f34887b270bfaf56cf7973572654874c8ed740e",
 "pt": "0xe3cdf5b8d7aedfc9f768dbdcc334146fae989188",
 "pt_symbol": "PT-SIUSD-22OCT2026",
 "implied_apy_pct": 9.128,
 "days_to_maturity": 42.14417824074074,
 "pt_to_asset": 0.9899644729182291,
 "underlying": "SIUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 5.528,
 "classification": "credit spread",
 "pt_depth_units": 1409833,
 "pt_depth_usd": 1395685,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 2.76%, $6,170 per year, GO — clears gas, impact and competition at this size

### [info] PT-TRUSD-26NOV2026 implies 9.59% fixed for 77 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xfcf009cb3135da12a6eb1f73f3ee05392a7bc947",
 "pt": "0x7191878f1fe834b28f4d0cead0e4375b814c4abb",
 "pt_symbol": "PT-TRUSD-26NOV2026",
 "implied_apy_pct": 9.591,
 "days_to_maturity": 77.14417824074074,
 "pt_to_asset": 0.9808291853065207,
 "underlying": "TRUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 5.991,
 "classification": "credit spread",
 "pt_depth_units": 577155,
 "pt_depth_usd": 566090,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 3.63%, $5,144 per year, GO — clears gas, impact and competition at this size

### [info] PT-APXUSD-5NOV2026 implies 9.92% fixed for 56 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xaf0349fb9b1ba07d34381870c59b560b31412660",
 "pt": "0xaf687b5ecb525ccea96115088999b4ed80c388b6",
 "pt_symbol": "PT-APXUSD-5NOV2026",
 "implied_apy_pct": 9.919,
 "days_to_maturity": 56.14417824074074,
 "pt_to_asset": 0.9855576273255369,
 "underlying": "APXUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 6.319,
 "classification": "credit spread",
 "pt_depth_units": 426473,
 "pt_depth_usd": 420313,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 3.15%, $3,238 per year, GO — clears gas, impact and competition at this size

### [info] PT-SRUSDE-22OCT2026 implies 5.45% fixed for 42 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x66ec657c59cdcaf171ab43b83da3942758bf8a97",
 "pt": "0x59bc9fae5d62b19d4f8d07d758047acb9ee19d34",
 "pt_symbol": "PT-SRUSDE-22OCT2026",
 "implied_apy_pct": 5.449,
 "days_to_maturity": 42.14417824074074,
 "pt_to_asset": 0.9938922992151491,
 "underlying": "SRUSDE",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 1.849,
 "classification": "credit spread",
 "pt_depth_units": 2122797,
 "pt_depth_usd": 2109832,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 0.92%, $1,036 per year, GO — clears gas, impact and competition at this size

### [info] Aave v3 USDtb pays 4.88% against the Sky savings rate at 3.60%; best size $74.5k earns $481 a year over it [one-block read, de-spiking unavailable]

```json
{
 "venue": "Aave v3",
 "asset": "USDtb",
 "supply_apr_spot_pct": 4.879,
 "supply_apr_window_median_pct": null,
 "spiked": false,
 "despike_unavailable": true,
 "benchmark": "Sky savings rate",
 "benchmark_pct": 3.6,
 "gap_pp": 1.279,
 "supplied_usd": 15494382,
 "borrowed_usd": 12613898,
 "available_usd": 2880485,
 "utilisation": 0.8141,
 "curve": {
  "base": 0.0,
  "optimal": 0.8,
  "reserve_factor": 0.2,
  "slope1": 0.04,
  "slope2": 0.5
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "marginal_apr_pct": 4.024,
   "over_benchmark_usd_per_year": 424
  },
  {
   "size_usd": 1000000.0,
   "marginal_apr_pct": 2.339,
   "over_benchmark_usd_per_year": -12607
  },
  {
   "size_usd": 10000000.0,
   "marginal_apr_pct": 0.979,
   "over_benchmark_usd_per_year": -262080
  },
  {
   "size_usd": 50000000.0,
   "marginal_apr_pct": 0.148,
   "over_benchmark_usd_per_year": -1725814
  }
 ],
 "best": {
  "size_usd": 74505.80596923828,
  "apr": 0.042452805344724315,
  "marginal_apr_pct": 4.245,
  "over_benchmark_usd_per_year": 481
 },
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 0.64%, $480 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $269 of $310366 pool fees (0.09%) across 194 episodes by 10 operator(s)

```json
{
 "episodes": 194,
 "fee_taken_usd": 269.21,
 "pool_fees_usd": 310365.74,
 "share_of_fees": 0.0009,
 "swap_usd_bracketed": 885831,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 69,
   "fee_taken_usd": 179.27
  },
  {
   "sender": "0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de",
   "episodes": 18,
   "fee_taken_usd": 75.95
  },
  {
   "sender": "0x654fae4aa229d104cabead47e56703f58b174be4",
   "episodes": 16,
   "fee_taken_usd": 4.87
  },
  {
   "sender": "0x4a54d76d7235d69e6d41bc26b5b431ff9f66248c",
   "episodes": 12,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0xe20446cccbfd5f9038e747f1dea8016ecbd94ae5",
   "episodes": 9,
   "fee_taken_usd": 0.0
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR -0.03%, $-321,390 per year, no — negative net per run at this size

### [info] 408 poisoning attempt(s) from 207 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0x47aca87b9ec69d090dfdb4c4176f3faae736c68abb2ab9b78d864e17bb48fa0c",
   "big_eth": 139.0,
   "victim": "0x95ae79a2a8e49cf86ffebae0df694d8bb7c1ab80",
   "impersonated": "0xbea9f7fd27f4ee20066f18def0bc586ec221055a",
   "attacker": "0xbea837c5cdda0a2db7655480ba9f37cd9721055a",
   "dust_tx": "0xd71baa66c2b623042f3e84afc75c6540cb2df9158daf56501d73986c2257efac",
   "seconds_after": 2832
  },
  {
   "big_tx": "0xd23f6f0ca3b9492f4eac367a9dbaa477d4e1fbe8f1acf801f125768d2a8b998c",
   "big_eth": 300.0,
   "victim": "0x53563b9ec34d016324d7cc41f66d7789167e8625",
   "impersonated": "0x98fae4bc489b83a8a2e0cbd7592a0cd8297821f9",
   "attacker": "0x98fa6ceea3e49627b57bcca38f6f9c822d5721f9",
   "dust_tx": "0x076251afe406e7406ab69147429be8ca19b77a7bf51295c6c58f387c3e954e5a",
   "seconds_after": 252
  },
  {
   "big_tx": "0xd23f6f0ca3b9492f4eac367a9dbaa477d4e1fbe8f1acf801f125768d2a8b998c",
   "big_eth": 300.0,
   "victim": "0x53563b9ec34d016324d7cc41f66d7789167e8625",
   "impersonated": "0x98fae4bc489b83a8a2e0cbd7592a0cd8297821f9",
   "attacker": "0x98f90d419003b0a2971f81eec79971d63e7821f9",
   "dust_tx": "0xf2d7f669acfc996719e46efb361032404295a2081935eb4ee3511a1cbf978b28",
   "seconds_after": 264
  },
  {
   "big_tx": "0xd23f6f0ca3b9492f4eac367a9dbaa477d4e1fbe8f1acf801f125768d2a8b998c",
   "big_eth": 300.0,
   "victim": "0x53563b9ec34d016324d7cc41f66d7789167e8625",
   "impersonated": "0x98fae4bc489b83a8a2e0cbd7592a0cd8297821f9",
   "attacker": "0x98f90d419003b0a2971f81eec79971d63e7821f9",
   "dust_tx": "0x363394b920a8e82bb2f9d97c4ece04d88f04f76f65c7be3c1d9ce0ca62e8d786",
   "seconds_after": 372
  },
  {
   "big_tx": "0xd23f6f0ca3b9492f4eac367a9dbaa477d4e1fbe8f1acf801f125768d2a8b998c",
   "big_eth": 300.0,
   "victim": "0x53563b9ec34d016324d7cc41f66d7789167e8625",
   "impersonated": "0x98fae4bc489b83a8a2e0cbd7592a0cd8297821f9",
   "attacker": "0x98fa6ceea3e49627b57bcca38f6f9c822d5721f9",
   "dust_tx": "0xc63c5bd09f70e7101396539ee9a5b39ef3a387148e4ac22b4d1cec05eb01ea32",
   "seconds_after": 816
  },
  {
   "big_tx": "0xd23f6f0ca3b9492f4eac367a9dbaa477d4e1fbe8f1acf801f125768d2a8b998c",
   "big_eth": 300.0,
   "victim": "0x53563b9ec34d016324d7cc41f66d7789167e8625",
   "impersonated": "0x98fae4bc489b83a8a2e0cbd7592a0cd8297821f9",
   "attacker": "0x98fab0f1e5a7326f85198f2ddff58768b6f421f9",
   "dust_tx": "0x403af5339a2c6a0ab2f4f0a9f439472f852ea6e00ec
```

### [info] 0x33e8f27903: 37 buyers, 2 sellers — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x33e8f279032eb970eea519260e46213414f889b8",
 "symbol": null,
 "label": null,
 "distinct_buyers": 37,
 "distinct_sellers": 2,
 "seller_to_buyer_ratio": 0.0541,
 "buy_legs": 51,
 "sell_legs": 9,
 "router_calls_naming_it": 9,
 "of_which_emitted_no_logs": 0,
 "fail_rate": 0.0,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 25939361,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] 0x9447dd95f5: 25 buyers, 2 sellers — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x9447dd95f576fdf6ed8219fff45bd1362430b787",
 "symbol": null,
 "label": null,
 "distinct_buyers": 25,
 "distinct_sellers": 2,
 "seller_to_buyer_ratio": 0.08,
 "buy_legs": 25,
 "sell_legs": 5,
 "router_calls_naming_it": 5,
 "of_which_emitted_no_logs": 0,
 "fail_rate": 0.0,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 25939357,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] airdrop or multisend: 0x5f934e3dab2e77e160e40af4e94406 sent 0x9cb7a4ef to 1,556 recipients in 8 txs (194 per tx)

```json
{
 "token": "0x9cb7a4ef0cae65b07362bc679a0b874041e3da53",
 "token_symbol": null,
 "sender": "0x5f934e3dab2e77e160e40af4e94406d09bfa2169",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 1556,
 "recipients": 1556,
 "txs": 8,
 "blocks": 8,
 "transfers_per_tx": 194.5,
 "carrier_contract": "0x5f934e3dab2e77e160e40af4e94406d09bfa2169",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "313000000000000000000",
 "uniform_amount_share": 0.033,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] airdrop or multisend: 0xd176aaf656c1b6c6a20f053675a668 sent 0x514b9e54 to 1,161 recipients in 4 txs (388 per tx)

```json
{
 "token": "0x514b9e5467b9eb811519e316263c9099eae546ca",
 "token_symbol": null,
 "sender": "0xd176aaf656c1b6c6a20f053675a668a974728931",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 1553,
 "recipients": 1161,
 "txs": 4,
 "blocks": 4,
 "transfers_per_tx": 388.2,
 "carrier_contract": "0x965973a65f49c99e05f56ed00fad4ac50bfced5a",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "100000000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] airdrop or multisend: 0xd152f549545093347a162dce210e72 sent USDC to 604 recipients in 3 txs (201 per tx)

```json
{
 "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "token_symbol": "USDC",
 "sender": "0xd152f549545093347a162dce210e7293f1452150",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 604,
 "recipients": 604,
 "txs": 3,
 "blocks": 3,
 "transfers_per_tx": 201.3,
 "carrier_contract": "0xd152f549545093347a162dce210e7293f1452150",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "35870000",
 "uniform_amount_share": 0.003,
 "usd_median": 35.8658796131,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] airdrop or multisend: 0xf108cfd5598685fdbd3bf6ec63bbeb sent USDC to 518 recipients in 14 txs (37 per tx)

```json
{
 "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "token_symbol": "USDC",
 "sender": "0xf108cfd5598685fdbd3bf6ec63bbebbc7d4e6ee5",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 518,
 "recipients": 518,
 "txs": 14,
 "blocks": 14,
 "transfers_per_tx": 37.0,
 "carrier_contract": "0x72fe31aae72fea4e1f9048a8a3ca580eeba3cd58",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "640000000",
 "uniform_amount_share": 0.887,
 "usd_median": 639.9264832,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] sDAI trades 9.8bp above NAV — the market is paying for immediacy

```json
{
 "asset": "sDAI",
 "nav_source": "0x83f20f44 convertToAssets(uint256)",
 "nav": 1.179821,
 "market_vw_price": 1.180978,
 "market_median": 1.180958,
 "market_p10": 1.180887,
 "discount_bps": -9.81,
 "traded_volume_usd": 181660,
 "implied_daily_volume_usd": 435984,
 "refills_needed_per_year": 18250,
 "swaps": 3,
 "venues": {
  "curve": 3
 },
 "redemption": {
  "days": 0.0,
  "atomic": true,
  "availability": "always",
  "exit_bps": 1.0,
  "path": "ERC-4626 redeem into DAI, same transaction"
 },
 "net_edge_bps": -10.81,
 "price_dispersion_bps": 1.34,
 "discount_at_p10_bps": -9.04,
 "significance_vs_dispersion": -8.05,
 "dispersion_note": "a dollar claim\u2019s NAV barely moves, so the spread is mostly execution dispersion and the test is meaningful",
 "why": "a claim above NAV is the same mechanism seen from the seller\u2019s side"
}
```

