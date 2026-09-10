# Detector sweep — research/2026-09-10/live_5h

Ran 17 detector(s); 60 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 5.32 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `borrow_cost` | 5 | 0.00 | cheapest venue to borrow each asset, capped by the liquidity actually withdrawable there |
| `delegated_dust` | 1 | 7.14 | mass dust fan-out inside EIP-7702 / executeBatch calldata, from senders that mimic the recipient's counterparties |
| `dollar_rate_outlier` | 1 | 0.00 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `fixed_vs_floating` | 13 | 0.01 | Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth |
| `gas_concentration` | 1 | 10.70 | base-fee spikes attributed to the contract whose gas demand caused them |
| `honeypot_signature` | 2 | 6.03 | tokens whose buyers cannot sell: reverting sales, confiscatory taxes, buyers without sellers |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `liquidity_blackout` | 0 | 0.01 | lending reserves whose withdrawable liquidity collapses, and the time of day it happens |
| `lp_marginal_yield` | 10 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 4 | 8.21 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 1 | 5.89 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 1 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `recycled_swap_volume` | 1 | 6.42 | large same-transaction, same-pool v2-style swaps with nearly closed token positions |
| `solver_fingerprint` | 12 | 5.74 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |
| `token_fan_in` | 1 | 8.07 | settled token transfers from thousands of senders concentrated at one recipient |

### [high] 0x59aab1bd… sprayed 119,982 dust legs from 8,486 delegated accounts at 15,501 wallets; 33.4% of testable legs came from a lookalike of the recipient's own counterparty

```json
{
 "operator": "0x59aab1bd0d26290274398c07b55955c15425e16b",
 "operator_label": null,
 "dust_legs": 119982,
 "executing_accounts": 8486,
 "recipients": 15501,
 "legs_with_a_testable_recipient": 37409,
 "legs_from_a_lookalike_counterparty": 12487,
 "lookalike_rate": 0.3338,
 "tokens": {
  "0xdac17f958d2ee523a2206206994597c13d831ec7": 11992,
  "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 9966,
  "0x6b175474e89094c44da98b954eedeac495271d0f": 20
 },
 "native_legs": 98004,
 "total_wei_moved": 9800400000000,
 "examples": [
  {
   "victim": "0x89d82bb032ba6d06177b8706d9ae494ea02132f1",
   "dust_from": "0x689ba2da16a864b9730f6726e8deac927b7fc694",
   "mimics": "0x689b02b4ded5a9a2e070f7679971e1edd143c694",
   "tx": "0x93a815c66256fdc3be3791b0fd9be5aafc3612968a46b13f3286b1edb6628177"
  },
  {
   "victim": "0xb802daf8e3a30c1c6cc42ac5cca8417a91d798cb",
   "dust_from": "0x79a000eb83c6df5d1ef47b8ed761b74d897a23d2",
   "mimics": "0x79a023d3097a64e6497ea8601e3236f6517a23d2",
   "tx": "0x93a815c66256fdc3be3791b0fd9be5aafc3612968a46b13f3286b1edb6628177"
  },
  {
   "victim": "0x992e7025c9a09a538a858a8095dc2930b44976e0",
   "dust_from": "0x35403c5f2aa617d86700d37003487ed2d81154c8",
   "mimics": "0x35409c665659b89a6fa91794f698dee8566d54c8",
   "tx": "0x93a815c66256fdc3be3791b0fd9be5aafc3612968a46b13f3286b1edb6628177"
  },
  {
   "victim": "0xa093d26e02de2ada5075aa8f915bd12c302644a6",
   "dust_from": "0xc474440c29eba6756285ee739ffede298656ce02",
   "mimics": "0xc474cd13ab5a29d3939b6362cc19fa7d7dd3ce02",
   "tx": "0x93a815c66256fdc3be3791b0fd9be5aafc3612968a46b13f3286b1edb6628177"
  }
 ],
 "note": "lookalike = first 4 and last 4 hex characters shared with an address the recipient transacted with inside this window; a victim copying from a truncated history sees the same string. The rate is a floor: only in-window counterparties can be tested."
}
```

### [notable] unlabelled atomic bot pair 0x772cff0b passed $2.1B through in 24 txs (100% ended flat, 2 counterparties)

```json
{
 "address": "0x772cff0be38a6ed31aeae479cbcb26d54b8404cf",
 "shape": "pass-through",
 "gross_usd": 2100027452,
 "txs": 24,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 1050000006,
 "sent_usd": 1050027447,
 "retained_usd": -27441,
 "retention": -0.0,
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

### [notable] unlabelled atomic bot pair 0x26de7861 passed $2.1B through in 24 txs (100% ended flat, 1 counterparties)

```json
{
 "address": "0x26de7861e213a5351f6ed767d00e0839930e9ee1",
 "shape": "pass-through",
 "gross_usd": 2100000012,
 "txs": 24,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 1050000006,
 "sent_usd": 1050000006,
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

### [notable] unlabelled unknown 0x76f30e3f cycled $560.2M and ended the window flat (40 txs, 13 counterparties)

```json
{
 "address": "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a",
 "shape": "cycles",
 "gross_usd": 1120387664,
 "txs": 40,
 "counterparties": 13,
 "tokens": 6,
 "pass_through_share": 0.45,
 "received_usd": 560192879,
 "sent_usd": 560194785,
 "retained_usd": -1906,
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

### [notable] unlabelled atomic bot pair 0xfce1984c passed $671.9M through in 3 txs (100% ended flat, 4 counterparties)

```json
{
 "address": "0xfce1984cd045caf1fe69443e14086d0dd1a48ed6",
 "shape": "pass-through",
 "gross_usd": 671913403,
 "txs": 3,
 "counterparties": 4,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 335930650,
 "sent_usd": 335982753,
 "retained_usd": -52103,
 "retention": -0.0002,
 "is_contract": true,
 "emits_logs": false,
 "receives_calldata": true,
 "originates_txs": false,
 "vanity_zeros": 0,
 "suggested_kind": "atomic bot pair",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled venue 0x8b6e6e7b passed $325.3M through in 9 txs (67% ended flat, 5 counterparties)

```json
{
 "address": "0x8b6e6e7b5b3801fed2cafd4b22b8a16c2f2db21a",
 "shape": "pass-through",
 "gross_usd": 325347732,
 "txs": 9,
 "counterparties": 5,
 "tokens": 1,
 "pass_through_share": 0.667,
 "received_usd": 162709069,
 "sent_usd": 162638663,
 "retained_usd": 70407,
 "retention": 0.0004,
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

### [notable] unlabelled venue 0x59cd1c87 passed $306.5M through in 14 txs (64% ended flat, 10 counterparties)

```json
{
 "address": "0x59cd1c87501baa753d0b5b5ab5d8416a45cd71db",
 "shape": "pass-through",
 "gross_usd": 306497740,
 "txs": 14,
 "counterparties": 10,
 "tokens": 1,
 "pass_through_share": 0.643,
 "received_usd": 155153913,
 "sent_usd": 151343827,
 "retained_usd": 3810086,
 "retention": 0.0246,
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

### [notable] unlabelled venue 0x99926ab8 passed $124.0M through in 5 txs (80% ended flat, 5 counterparties)

```json
{
 "address": "0x99926ab8e1b589500ae87977632f13cf7f70f242",
 "shape": "pass-through",
 "gross_usd": 124008461,
 "txs": 5,
 "counterparties": 5,
 "tokens": 4,
 "pass_through_share": 0.8,
 "received_usd": 74338930,
 "sent_usd": 49669531,
 "retained_usd": 24669399,
 "retention": 0.3319,
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

### [notable] unlabelled venue 0x666fedd4 passed $119.1M through in 156 txs (85% ended flat, 97 counterparties)

```json
{
 "address": "0x666fedd4cdd4e890a5ad20e7b60975409435a64a",
 "shape": "pass-through",
 "gross_usd": 119137818,
 "txs": 156,
 "counterparties": 97,
 "tokens": 20,
 "pass_through_share": 0.846,
 "received_usd": 59628270,
 "sent_usd": 59509548,
 "retained_usd": 118723,
 "retention": 0.002,
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

### [notable] $9,867,746 of settled turnover in 2 same-pool atomic round trips; token positions almost close

```json
{
 "pool": "0xcb62c2d6894736d4216a41f5812bb9771de056d5",
 "roundtrips": 2,
 "gross_priced_leg_usd": 9867746.082769059,
 "pool_net_priced_token_usd": -0.1926898068036296,
 "examples": [
  {
   "tx": "0x066d84a75b617eb0cd9f4ae2878f8db9933ee76dbb4fb639a7118c76b6a014c1",
   "block": 25945231,
   "sender": "0x5afec0de001999766fb883860cae06f5932e6f32",
   "gross_priced_leg_usd": 4933873.04146742,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-39088019084573",
   "pool_net_priced_token_usd": -0.09642779381117328,
   "closure_fractions": [
    0.0,
    3.908807183166015e-08
   ]
  },
  {
   "tx": "0xbfb13f71e2ae58e0483a6ccaafe09cf56a890b523fabc61a149308ac693101a2",
   "block": 25946094,
   "sender": "0x5afec0de001999766fb883860cae06f5932e6f32",
   "gross_priced_leg_usd": 4933873.041301639,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-39020818088369",
   "pool_net_priced_token_usd": -0.09626201299245632,
   "closure_fractions": [
    0.0,
    3.9020870747394424e-08
   ]
  }
 ],
 "note": "Gross turnover is preserved. Net here is only the pool\u2019s priced token delta; it excludes gas and other assets. A fee-rate times gross turnover estimate does not measure realizable LP profit through these price round trips."
}
```

### [notable] USDS borrows 1.63pp cheaper on SparkLend than Aave v3; $318.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDS",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 3.926,
  "liquidity_usd": 318737263,
  "utilisation": 0.6561851243688462,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 5.553,
  "liquidity_usd": 8790620
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.926,
   "liquidity_usd": 318737263,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 5.553,
   "liquidity_usd": 8790620,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.627,
 "refinance_gas_usd": 0.676,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.63%, $5,186,383 per year, GO — clears gas, impact and competition at this size

### [notable] DAI borrows 0.68pp cheaper on SparkLend than Aave v3; $99.5M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "DAI",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.043,
  "liquidity_usd": 99526097,
  "utilisation": 0.676595394024174,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.724,
  "liquidity_usd": 17179956
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.043,
   "liquidity_usd": 99526097,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.724,
   "liquidity_usd": 17179956,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.681,
 "refinance_gas_usd": 0.676,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.68%, $677,331 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDe/USDC: $1.0M in a ±0.03% band earns 2.4bp of fees less 0.0bp of divergence over 5.0h (41.2% a year if it repeats)

```json
{
 "pool": "0x56fc29b86900aa0afa6e20b020429bffba1105cfb45070492c67529b46eb48c1",
 "venue": "uniswap_v4",
 "pair": "USDe/USDC",
 "stable_pair": true,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.025,
 "band_quoted_pct": 0.025,
 "concentration_multiplier": 8001.5,
 "band_ladder": [
  {
   "band_pct": 0.025,
   "apr_pct_at_10000": 59.12
  },
  {
   "band_pct": 0.05,
   "apr_pct_at_10000": 29.63
  },
  {
   "band_pct": 0.125,
   "apr_pct_at_10000": 11.87
  },
  {
   "band_pct": 0.5,
   "apr_pct_at_10000": 2.98
  }
 ],
 "pool_band_capital_usd": 2265307,
 "full_range_capital_usd": 18125856479,
 "passive_fees_usd": 767.73,
 "volume_usd": 24765464,
 "swaps": 195,
 "annualisation_factor": 1752.0,
 "n_takers": 56,
 "top_taker": "0x515cc41a9b9a0e040082d027b72230ecdf0b41a1",
 "top_taker_share": 0.2191,
 "taker_herfindahl": 0.1149,
 "apr_band_1pct_as_reported": 0.015,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 3.374,
   "divergence_bps_window": 0.0,
   "net_bps_window": 3.374,
   "over_benchmark_usd": 3.17,
   "annualised_net_apr_pct": 59.12
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 3.316,
   "divergence_bps_window": 0.0,
   "net_bps_window": 3.316,
   "over_benchmark_usd": 15.55,
   "annualised_net_apr_pct": 58.09
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 3.052,
   "divergence_bps_window": 0.0,
   "net_bps_window": 3.052,
   "over_benchmark_usd": 71.17,
   "annualised_net_apr_pct": 53.48
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 2.351,
   "divergence_bps_window": 0.0,
   "net_bps_window": 2.351,
   "over_benchmark_usd": 214.57,
   "annualised_net_apr_pct": 41.19
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 41.19%, $375,927 per year, GO — nets 41.19% a year at $1,000,000 in a ±0.025% band against a 3.60% savings rate

### [notable] USDS pays 3.33pp more on Sky SSR than Aave v3; best size $8.8M earns $293k a year over Aave v3

```json
{
 "asset": "USDS",
 "high_venue": "Sky SSR",
 "low_venue": "Aave v3",
 "supply_apr_spot_pct": {
  "Aave v3": 0.272,
  "SparkLend": 2.318,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "SparkLend": 2.318
 },
 "gap_pp_spot": 3.328,
 "gap_pp_despiked": 3.328,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Sky SSR emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 9403945,
  "SparkLend": 927060711,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.065,
  "SparkLend": 0.656
 },
 "dilution_basis": "modelled",
 "best_size": {
  "size_usd": 8790759.686851714,
  "apr_at_size_pct": 3.599999699843881,
  "over_low_venue_usd_per_year": 292589.082248325
 },
 "unconstrained_best_size": null,
 "source_available_usd": 8790759.686851714,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": null
}
```

Economics: net APR 3.33%, $292,589 per year, GO — clears gas, impact and competition at this size

### [notable] USDT pays 0.72pp more on Aave v3 than Compound v3 USDT; best size $27.2M earns $156k a year over Compound v3 USDT [source liquidity capped]

```json
{
 "asset": "USDT",
 "high_venue": "Aave v3",
 "low_venue": "Compound v3 USDT",
 "supply_apr_spot_pct": {
  "Aave v3": 3.829,
  "SparkLend": 3.394,
  "Compound v3 USDT": 3.086
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.809
 },
 "gap_pp_spot": 0.742,
 "gap_pp_despiked": 0.723,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 2959853720,
  "SparkLend": 339546593,
  "Compound v3 USDT": 181764783
 },
 "utilisation": {
  "Aave v3": 0.941,
  "SparkLend": 0.942,
  "Compound v3 USDT": 0.857
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 27150077.55975556,
  "apr_at_size_pct": 3.661,
  "over_low_venue_usd_per_year": 156024
 },
 "unconstrained_best_size": {
  "size_usd": 138667671.7210955,
  "apr_at_size_pct": 3.402,
  "over_low_venue_usd_per_year": 438031
 },
 "source_available_usd": 27150077.55975556,
 "source_liquidity_basis": "underlying balanceOf(Comet), isWithdrawPaused",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.83
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.789
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.716
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.666
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 3.489
  }
 ]
}
```

Economics: net APR 0.57%, $156,024 per year, GO — clears gas, impact and competition at this size

### [notable] USDT borrows 1.70pp cheaper on Morpho Blue than Aave v3; $6.5M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDT",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 2.821,
  "liquidity_usd": 6453109,
  "utilisation": 0.899695,
  "collateral_required": "sUSDS (0xa3931d71, LLTV 96.5%)",
  "market": "0x26b178d49895f80c"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.522,
  "liquidity_usd": 175292344
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 2.821,
   "liquidity_usd": 6453109,
   "collateral": "sUSDS (0xa3931d71, LLTV 96.5%)"
  },
  {
   "venue": "Compound v3 USDT",
   "borrow_apy_pct": 3.882,
   "liquidity_usd": 25931060,
   "collateral": "the Comet\u2019s listed collaterals"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.003,
   "liquidity_usd": 19621079,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.522,
   "liquidity_usd": 175292344,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.701,
 "refinance_gas_usd": 0.676,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.70%, $109,777 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v3 USDe/USDC: $1.0M in a ±0.01% band earns 0.5bp of fees less 0.0bp of divergence over 5.0h (9.6% a year if it repeats)

```json
{
 "pool": "0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a",
 "venue": "uniswap_v3",
 "pair": "USDe/USDC",
 "stable_pair": true,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.011,
 "band_quoted_pct": 0.011,
 "concentration_multiplier": 18183.3,
 "band_ladder": [
  {
   "band_pct": 0.011,
   "apr_pct_at_10000": 23.4
  },
  {
   "band_pct": 0.022,
   "apr_pct_at_10000": 11.79
  },
  {
   "band_pct": 0.055,
   "apr_pct_at_10000": 4.74
  },
  {
   "band_pct": 0.22,
   "apr_pct_at_10000": 1.19
  }
 ],
 "pool_band_capital_usd": 673661,
 "full_range_capital_usd": 12249393240,
 "passive_fees_usd": 91.31,
 "volume_usd": 999580,
 "swaps": 36,
 "annualisation_factor": 1752.0,
 "n_takers": 15,
 "top_taker": "0x515cc41a9b9a0e040082d027b72230ecdf0b41a1",
 "top_taker_share": 0.3104,
 "taker_herfindahl": 0.225,
 "apr_band_1pct_as_reported": 0.0026,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1.336,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.336,
   "over_benchmark_usd": 1.13,
   "annualised_net_apr_pct": 23.4
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 1.262,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.262,
   "over_benchmark_usd": 5.28,
   "annualised_net_apr_pct": 22.11
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.989,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.989,
   "over_benchmark_usd": 19.58,
   "annualised_net_apr_pct": 17.32
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.546,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.546,
   "over_benchmark_usd": 34.01,
   "annualised_net_apr_pct": 9.56
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 9.56%, $59,586 per year, GO — nets 9.56% a year at $1,000,000 in a ±0.011% band against a 3.60% savings rate

### [notable] USDC borrows 2.35pp cheaper on Morpho Blue than Compound v3 USDC; $1.6M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDC",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.636,
  "liquidity_usd": 1646050,
  "utilisation": 0.545191,
  "collateral_required": "0xaf687b5ecb (0xaf687b5e, LLTV 86.0%)",
  "market": "0x908b037029b5c067"
 },
 "dearest": {
  "venue": "Compound v3 USDC",
  "borrow_apy_pct": 5.987,
  "liquidity_usd": 35481316
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.636,
   "liquidity_usd": 1646050,
   "collateral": "0xaf687b5ecb (0xaf687b5e, LLTV 86.0%)"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.268,
   "liquidity_usd": 2040821,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.395,
   "liquidity_usd": 141284146,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Compound v3 USDC",
   "borrow_apy_pct": 5.987,
   "liquidity_usd": 35481316,
   "collateral": "the Comet\u2019s listed collaterals"
  }
 ],
 "gap_pp": 2.351,
 "refinance_gas_usd": 0.676,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 2.35%, $38,698 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDe/USDT: $250.0k in a ±0.02% band earns 0.8bp of fees less 0.0bp of divergence over 5.0h (14.1% a year if it repeats)

```json
{
 "pool": "0x63bb22f47c7ede6578a25c873e77eb782ec8e4c19778e36ce64d37877b5bd1e7",
 "venue": "uniswap_v4",
 "pair": "USDe/USDT",
 "stable_pair": true,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.021,
 "band_quoted_pct": 0.021,
 "concentration_multiplier": 9525.3,
 "band_ladder": [
  {
   "band_pct": 0.021,
   "apr_pct_at_10000": 32.98
  },
  {
   "band_pct": 0.042,
   "apr_pct_at_10000": 16.96
  },
  {
   "band_pct": 0.105,
   "apr_pct_at_10000": 6.91
  },
  {
   "band_pct": 0.42,
   "apr_pct_at_10000": 1.75
  }
 ],
 "pool_band_capital_usd": 168627,
 "full_range_capital_usd": 1606220295,
 "passive_fees_usd": 33.62,
 "volume_usd": 589843,
 "swaps": 58,
 "annualisation_factor": 1752.0,
 "n_takers": 17,
 "top_taker": "0x515cc41a9b9a0e040082d027b72230ecdf0b41a1",
 "top_taker_share": 0.2665,
 "taker_herfindahl": 0.1734,
 "apr_band_1pct_as_reported": 0.0074,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1.882,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.882,
   "over_benchmark_usd": 1.68,
   "annualised_net_apr_pct": 32.98
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 1.538,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.538,
   "over_benchmark_usd": 6.66,
   "annualised_net_apr_pct": 26.94
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.803,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.803,
   "over_benchmark_usd": 14.94,
   "annualised_net_apr_pct": 14.07
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.288,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.288,
   "over_benchmark_usd": 8.22,
   "annualised_net_apr_pct": 5.04
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 14.07%, $26,175 per year, GO — nets 14.07% a year at $250,000 in a ±0.021% band against a 3.60% savings rate

### [notable] uniswap_v4 USDT/USDS: $1.0M in a ±0.01% band earns 0.3bp of fees less 0.0bp of divergence over 5.0h (4.8% a year if it repeats)

```json
{
 "pool": "0x3b1b1f2e775a6db1664f8e7d59ad568605ea2406312c11aef03146c0cf89d5b9",
 "venue": "uniswap_v4",
 "pair": "USDT/USDS",
 "stable_pair": true,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.009,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 5.72
  },
  {
   "band_pct": 0.018,
   "apr_pct_at_10000": 3.18
  },
  {
   "band_pct": 0.045,
   "apr_pct_at_10000": 1.27
  },
  {
   "band_pct": 0.18,
   "apr_pct_at_10000": 0.32
  }
 ],
 "pool_band_capital_usd": 5000573,
 "full_range_capital_usd": 100018959074,
 "passive_fees_usd": 163.68,
 "volume_usd": 27280804,
 "swaps": 436,
 "annualisation_factor": 1752.0,
 "n_takers": 183,
 "top_taker": "0x515cc41a9b9a0e040082d027b72230ecdf0b41a1",
 "top_taker_share": 0.1409,
 "taker_herfindahl": 0.0396,
 "apr_band_1pct_as_reported": 0.0006,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.327,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.327,
   "over_benchmark_usd": 0.12,
   "annualised_net_apr_pct": 5.72
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.324,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.324,
   "over_benchmark_usd": 0.59,
   "annualised_net_apr_pct": 5.68
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.312,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.312,
   "over_benchmark_usd": 2.66,
   "annualised_net_apr_pct": 5.46
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.273,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.273,
   "over_benchmark_usd": 6.73,
   "annualised_net_apr_pct": 4.78
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 4.78%, $11,791 per year, GO — nets 4.78% a year at $1,000,000 in a ±0.010% band against a 3.60% savings rate

### [notable] uniswap_v3 USDC/USDT: $1.0M in a ±0.01% band earns 0.3bp of fees less 0.0bp of divergence over 5.0h (4.4% a year if it repeats)

```json
{
 "pool": "0x3416cf6c708da44db2624d63ea0aaef7113527c6",
 "venue": "uniswap_v3",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.003,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 5.27
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 5.27
  },
  {
   "band_pct": 0.015,
   "apr_pct_at_10000": 3.52
  },
  {
   "band_pct": 0.06,
   "apr_pct_at_10000": 0.88
  }
 ],
 "pool_band_capital_usd": 4918215,
 "full_range_capital_usd": 98371678447,
 "passive_fees_usd": 148.31,
 "volume_usd": 1484297,
 "swaps": 840,
 "annualisation_factor": 1752.0,
 "n_takers": 388,
 "top_taker": "0xf70da97812cb96acdf810712aa562db8dfa3dbef",
 "top_taker_share": 0.1315,
 "taker_herfindahl": 0.0521,
 "apr_band_1pct_as_reported": 0.0005,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.301,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.301,
   "over_benchmark_usd": 0.1,
   "annualised_net_apr_pct": 5.27
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.299,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.299,
   "over_benchmark_usd": 0.47,
   "annualised_net_apr_pct": 5.23
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.287,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.287,
   "over_benchmark_usd": 2.04,
   "annualised_net_apr_pct": 5.03
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.251,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.251,
   "over_benchmark_usd": 4.51,
   "annualised_net_apr_pct": 4.39
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 4.39%, $7,902 per year, GO — nets 4.39% a year at $1,000,000 in a ±0.010% band against a 3.60% savings rate

### [notable] RLUSD borrows 0.61pp cheaper on Morpho Blue than Aave v3; $1.3M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "RLUSD",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.704,
  "liquidity_usd": 1285187,
  "utilisation": 0.9,
  "collateral_required": "cbBTC (0xcbb7c000, LLTV 86.0%)",
  "market": "0xffd010618ed3cb39"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.315,
  "liquidity_usd": 1944736
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.704,
   "liquidity_usd": 1285187,
   "collateral": "cbBTC (0xcbb7c000, LLTV 86.0%)"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.315,
   "liquidity_usd": 1944736,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.611,
 "refinance_gas_usd": 0.676,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.61%, $7,852 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 1.46pp more on Compound v3 USDC than SparkLend; best size $935k earns $7k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.713,
  "SparkLend": 3.542,
  "Compound v3 USDC": 5.004,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.708
 },
 "gap_pp_spot": 1.462,
 "gap_pp_despiked": 1.462,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2311347345,
  "SparkLend": 26205820,
  "Compound v3 USDC": 375541132,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.939,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.906
 },
 "dilution_basis": "sampled",
 "best_size": {
  "size_usd": 934776.6150709104,
  "apr_at_size_pct": 4.285,
  "over_low_venue_usd_per_year": 6950
 },
 "unconstrained_best_size": {
  "size_usd": 934776.6150709104,
  "apr_at_size_pct": 4.285,
  "over_low_venue_usd_per_year": 6950
 },
 "source_available_usd": 2043550.632056614,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 4.927
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 4.235
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.217
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.056
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 2.574
  }
 ]
}
```

Economics: net APR 0.74%, $6,950 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDC/USDT: $250.0k in a ±0.01% band earns 0.3bp of fees less 0.0bp of divergence over 5.0h (4.9% a year if it repeats)

```json
{
 "pool": "0x8aa4e11cbdf30eedc92100f4c8a31ff748e201d44712cc8c90d189edaa8e4e47",
 "venue": "uniswap_v4",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.008,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 6.16
  },
  {
   "band_pct": 0.016,
   "apr_pct_at_10000": 3.87
  },
  {
   "band_pct": 0.04,
   "apr_pct_at_10000": 1.55
  },
  {
   "band_pct": 0.16,
   "apr_pct_at_10000": 0.39
  }
 ],
 "pool_band_capital_usd": 943973,
 "full_range_capital_usd": 18880869809,
 "passive_fees_usd": 33.55,
 "volume_usd": 2795476,
 "swaps": 207,
 "annualisation_factor": 1752.0,
 "n_takers": 148,
 "top_taker": "0x99a5b028d785a7bd475339b1f8548d6d659ce5c2",
 "top_taker_share": 0.1225,
 "taker_herfindahl": 0.0596,
 "apr_band_1pct_as_reported": 0.0006,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.352,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.352,
   "over_benchmark_usd": 0.15,
   "annualised_net_apr_pct": 6.16
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.338,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.338,
   "over_benchmark_usd": 0.66,
   "annualised_net_apr_pct": 5.91
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.281,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.281,
   "over_benchmark_usd": 1.89,
   "annualised_net_apr_pct": 4.92
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.173,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.173,
   "over_benchmark_usd": -3.29,
   "annualised_net_apr_pct": 3.02
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 4.92%, $3,311 per year, GO — nets 4.92% a year at $250,000 in a ±0.010% band against a 3.60% savings rate

### [notable] PT-SUSDS-26NOV2026 implies 4.93% fixed for 77 days against Sky savings rate at 3.60% — term premium

```json
{
 "market": "0x9c560ebaf78e596cbcc27411d633a74d628dd7dc",
 "pt": "0xdc169abe56461a2e0c034da431ac2a3ebf596094",
 "pt_symbol": "PT-SUSDS-26NOV2026",
 "implied_apy_pct": 4.926,
 "days_to_maturity": 76.56195601851852,
 "pt_to_asset": 0.9899640880083489,
 "underlying": "SUSDS",
 "comparison": "Sky savings rate",
 "floating_pct": 3.6,
 "gap_pp": 1.326,
 "classification": "term premium",
 "pt_depth_units": 758193,
 "pt_depth_usd": 750584,
 "oracle_ready": true,
 "why": "the same credit pays more fixed than floating for a fixed term, which is a view on the floating rate and nothing else"
}
```

Economics: net APR 0.66%, $345 per year, GO — clears gas, impact and competition at this size

### [notable] base fee peaked 0.244 gwei (4.2x the 0.057 gwei median) across 164 blocks

```json
{
 "blocks": [
  25945817,
  25946402
 ],
 "spike_blocks": 164,
 "median_gwei": 0.0573,
 "peak_gwei": 0.2436,
 "top_gas_in_spike": [
  {
   "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
   "label": null,
   "share_in_spike": 0.1508,
   "share_outside": 0.0848,
   "lift": 1.8,
   "gas_in_spike": 1778550861
  },
  {
   "address": "0x58b6a8a3302369daec383334672404ee733ab239",
   "label": null,
   "share_in_spike": 0.119,
   "share_outside": 0.0365,
   "lift": 3.3,
   "gas_in_spike": 1402554821
  }
 ],
 "attribution": "0xdac17f958d2ee523a2206206994597c13d831ec7 holds 15% of requested gas inside the spike against 8.5% outside"
}
```

### [notable] mint distribution: zero address (mint/burn) (known- sent 0x06450dee to 32,298 recipients in 488 txs (132 per tx)

```json
{
 "token": "0x06450dee7fd2fb8e39061434babcfc05599a6fb8",
 "token_symbol": null,
 "sender": "0x0000000000000000000000000000000000000000",
 "sender_label": "zero address (mint/burn) (known-canonical)",
 "kind": "mint distribution",
 "transfers": 64571,
 "recipients": 32298,
 "txs": 488,
 "blocks": 177,
 "transfers_per_tx": 132.3,
 "carrier_contract": "0x0de8bf93da2f7eecb3d9169422413a9bef4ef628",
 "carrier_label": null,
 "carrier_share": 0.986,
 "median_raw_amount": "24191180000000000000000000",
 "uniform_amount_share": 0.5,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 17,808 recipients in 61 txs (311 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 18969,
 "recipients": 17808,
 "txs": 61,
 "blocks": 61,
 "transfers_per_tx": 311.0,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "19607766244053945",
 "uniform_amount_share": 0.15,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 7,515 recipients in 14 txs (573 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 8016,
 "recipients": 7515,
 "txs": 14,
 "blocks": 14,
 "transfers_per_tx": 572.6,
 "carrier_contract": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "5000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDT to 3,262 recipients in 35 txs (105 per tx)

```json
{
 "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "token_symbol": "USDT",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 3663,
 "recipients": 3262,
 "txs": 35,
 "blocks": 35,
 "transfers_per_tx": 104.7,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "293",
 "uniform_amount_share": 0.003,
 "usd_median": 0.00029294382311,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] LPT: 72,446 settled transfers from 72,446 senders converge on Binance 14 (model-memory) (99.9% of token transfers)

```json
{
 "token": "0x58b6a8a3302369daec383334672404ee733ab239",
 "symbol": "LPT",
 "recipient": "0x28c6c06298d514db089934071355e5743bf21d60",
 "recipient_label": "Binance 14 (model-memory)",
 "transfers": 72446,
 "unique_senders": 72446,
 "token_transfer_share": 0.9991035842837639,
 "total_raw": "161357654758466719775465",
 "total_units": 161357.65475846673,
 "first_timestamp": 1789021379,
 "last_timestamp": 1789036247,
 "buckets": {
  "1789020900": 1,
  "1789026300": 1,
  "1789027200": 1,
  "1789029000": 11863,
  "1789029900": 9375,
  "1789030800": 9212,
  "1789031700": 9351,
  "1789032600": 9364,
  "1789033500": 8554,
  "1789034400": 7410,
  "1789035300": 6949,
  "1789036200": 365
 },
 "examples": [
  {
   "tx": "0x526587165dc56c5a83daa6391e512bf3054efcc88990016b1e04e4ea0aebc8b5",
   "block": 25945171,
   "sender": "0xe769a22209688b2359d6ebc46461f89a6b62005b",
   "raw": "552777777780000000000"
  },
  {
   "tx": "0x78492bd336101d2e78881f1c8d949ce1472043fa5620238312eb837fc10ad52d",
   "block": 25945619,
   "sender": "0xfe9529b753b412941127fea1981e5ce0a85c101e",
   "raw": "2483410000000000000000"
  },
  {
   "tx": "0xeb381921d7e2b3a27dc794ae29bfdd0a60bb5701ec5bc9db1bce0af5b2cdef7d",
   "block": 25945655,
   "sender": "0x06fd4ba7973a0d39a91734bbc35bc2bcaa99e3b0",
   "raw": "1502723650510000000000"
  }
 ],
 "note": "Settled positive non-mint/burn Transfer logs. Shared ownership, gas funders and deposit-versus-internal-sweep interpretation require follow-up."
}
```

### [info] unlabelled venue 0x277c6a64 passed $99.5M through in 5 txs (80% ended flat, 6 counterparties)

```json
{
 "address": "0x277c6a642564a91ff78b008022d65683cee5ccc5",
 "shape": "pass-through",
 "gross_usd": 99452565,
 "txs": 5,
 "counterparties": 6,
 "tokens": 4,
 "pass_through_share": 0.8,
 "received_usd": 49678956,
 "sent_usd": 49773609,
 "retained_usd": -94654,
 "retention": -0.0019,
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

### [info] unlabelled eoa 0x54d25040 passed $74.4M through in 28 txs (86% ended flat, 2 counterparties)

```json
{
 "address": "0x54d250405d22e858d125ce2c1affc7d73afe6029",
 "shape": "pass-through",
 "gross_usd": 74350216,
 "txs": 28,
 "counterparties": 2,
 "tokens": 3,
 "pass_through_share": 0.857,
 "received_usd": 22340407,
 "sent_usd": 52009810,
 "retained_usd": -29669403,
 "retention": -1.3281,
 "is_contract": false,
 "emits_logs": false,
 "receives_calldata": false,
 "originates_txs": true,
 "vanity_zeros": 0,
 "suggested_kind": "eoa",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [info] unlabelled mev_bot 0x00000000 cycled $33.9M and ended the window flat (40 txs, 1 counterparties)

```json
{
 "address": "0x000000000035b5e5ad9019092c665357240f594e",
 "shape": "cycles",
 "gross_usd": 67764338,
 "txs": 40,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 0.0,
 "received_usd": 33882490,
 "sent_usd": 33881848,
 "retained_usd": 641,
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

### [info] unlabelled eoa 0xcde5d48f cycled $33.4M and ended the window flat (22 txs, 6 counterparties)

```json
{
 "address": "0xcde5d48fca07f9c52300d2e65632dd71ed169b90",
 "shape": "cycles",
 "gross_usd": 66733814,
 "txs": 22,
 "counterparties": 6,
 "tokens": 7,
 "pass_through_share": 0.0,
 "received_usd": 33366907,
 "sent_usd": 33366907,
 "retained_usd": 1,
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

### [info] uniswap_v3 WETH/USDT: $1.0M in a ±0.25% band earns 16.6bp of fees less 6.3bp of divergence over 5.0h (181.4% a year if it repeats)

```json
{
 "pool": "0x4e68ccd3e89f51c3074ca5072bbac773960dfa36",
 "venue": "uniswap_v3",
 "pair": "WETH/USDT",
 "stable_pair": false,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.251,
 "band_quoted_pct": 0.251,
 "concentration_multiplier": 798.3,
 "band_ladder": [
  {
   "band_pct": 0.251,
   "apr_pct_at_10000": 307.38
  },
  {
   "band_pct": 0.502,
   "apr_pct_at_10000": 154.44
  },
  {
   "band_pct": 1.255,
   "apr_pct_at_10000": 62.23
  },
  {
   "band_pct": 5.02,
   "apr_pct_at_10000": 16.01
  }
 ],
 "pool_band_capital_usd": 2278587,
 "full_range_capital_usd": 1819024229,
 "passive_fees_usd": 5450.44,
 "volume_usd": 1816814,
 "swaps": 467,
 "annualisation_factor": 1752.0,
 "n_takers": 276,
 "top_taker": "0x2c937e3b0ea4198303d85ae11e4ac5fe3181c990",
 "top_taker_share": 0.1861,
 "taker_herfindahl": 0.0887,
 "apr_band_1pct_as_reported": 1.0578,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 23.816,
   "divergence_bps_window": 6.271,
   "net_bps_window": 17.545,
   "over_benchmark_usd": 17.54,
   "annualised_net_apr_pct": 307.38
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 23.407,
   "divergence_bps_window": 6.271,
   "net_bps_window": 17.136,
   "over_benchmark_usd": 85.68,
   "annualised_net_apr_pct": 300.22
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 21.555,
   "divergence_bps_window": 6.271,
   "net_bps_window": 15.284,
   "over_benchmark_usd": 382.11,
   "annualised_net_apr_pct": 267.78
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 16.624,
   "divergence_bps_window": 6.271,
   "net_bps_window": 10.353,
   "over_benchmark_usd": 1035.33,
   "annualised_net_apr_pct": 181.39
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 181.39%, $1,813,898 per year, no — nets 181.39% a year at $1,000,000 in a ±0.251% band, before any view on holding the pair

### [info] uniswap_v3 WBTC/WETH: $250.0k in a ±0.24% band earns 15.0bp of fees less 5.9bp of divergence over 5.0h (159.2% a year if it repeats)

```json
{
 "pool": "0x4585fe77225b41b697c938b018e2ac67ac5a20c0",
 "venue": "uniswap_v3",
 "pair": "WBTC/WETH",
 "stable_pair": false,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.236,
 "band_quoted_pct": 0.236,
 "concentration_multiplier": 849.0,
 "band_ladder": [
  {
   "band_pct": 0.236,
   "apr_pct_at_10000": 306.88
  },
  {
   "band_pct": 0.472,
   "apr_pct_at_10000": 156.14
  },
  {
   "band_pct": 1.18,
   "apr_pct_at_10000": 63.39
  },
  {
   "band_pct": 4.72,
   "apr_pct_at_10000": 16.34
  }
 ],
 "pool_band_capital_usd": 416616,
 "full_range_capital_usd": 353688965,
 "passive_fees_usd": 998.82,
 "volume_usd": 1997631,
 "swaps": 175,
 "annualisation_factor": 1752.0,
 "n_takers": 106,
 "top_taker": "0x3be1268daefd632dad9631e9ccf25a1ef6b33c11",
 "top_taker_share": 0.1987,
 "taker_herfindahl": 0.0649,
 "apr_band_1pct_as_reported": 0.9969,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 23.413,
   "divergence_bps_window": 5.897,
   "net_bps_window": 17.516,
   "over_benchmark_usd": 17.52,
   "annualised_net_apr_pct": 306.88
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 21.406,
   "divergence_bps_window": 5.897,
   "net_bps_window": 15.509,
   "over_benchmark_usd": 77.55,
   "annualised_net_apr_pct": 271.72
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 14.983,
   "divergence_bps_window": 5.897,
   "net_bps_window": 9.087,
   "over_benchmark_usd": 227.17,
   "annualised_net_apr_pct": 159.2
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 7.051,
   "divergence_bps_window": 5.897,
   "net_bps_window": 1.154,
   "over_benchmark_usd": 115.42,
   "annualised_net_apr_pct": 20.22
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 159.20%, $398,002 per year, no — nets 159.20% a year at $250,000 in a ±0.236% band, before any view on holding the pair

### [info] uniswap_v3 USDC/WETH: $250.0k in a ±0.25% band earns 13.3bp of fees less 6.2bp of divergence over 5.0h (123.6% a year if it repeats)

```json
{
 "pool": "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8",
 "venue": "uniswap_v3",
 "pair": "USDC/WETH",
 "stable_pair": false,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.249,
 "band_quoted_pct": 0.249,
 "concentration_multiplier": 804.7,
 "band_ladder": [
  {
   "band_pct": 0.249,
   "apr_pct_at_10000": 279.63
  },
  {
   "band_pct": 0.498,
   "apr_pct_at_10000": 142.83
  },
  {
   "band_pct": 1.245,
   "apr_pct_at_10000": 58.13
  },
  {
   "band_pct": 4.98,
   "apr_pct_at_10000": 15.02
  }
 ],
 "pool_band_capital_usd": 347660,
 "full_range_capital_usd": 279766680,
 "passive_fees_usd": 793.36,
 "volume_usd": 264454,
 "swaps": 55,
 "annualisation_factor": 1752.0,
 "n_takers": 28,
 "top_taker": "0xeaa9ebddd373c4bd8bb92dfcc9c7e7fcdb268e51",
 "top_taker_share": 0.1839,
 "taker_herfindahl": 0.1219,
 "apr_band_1pct_as_reported": 1.0011,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 22.182,
   "divergence_bps_window": 6.221,
   "net_bps_window": 15.961,
   "over_benchmark_usd": 15.96,
   "annualised_net_apr_pct": 279.63
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 19.951,
   "divergence_bps_window": 6.221,
   "net_bps_window": 13.73,
   "over_benchmark_usd": 68.65,
   "annualised_net_apr_pct": 240.54
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 13.274,
   "divergence_bps_window": 6.221,
   "net_bps_window": 7.053,
   "over_benchmark_usd": 176.33,
   "annualised_net_apr_pct": 123.57
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 5.887,
   "divergence_bps_window": 6.221,
   "net_bps_window": -0.334,
   "over_benchmark_usd": -33.42,
   "annualised_net_apr_pct": -5.85
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 123.57%, $308,930 per year, no — nets 123.57% a year at $250,000 in a ±0.249% band, before any view on holding the pair

### [info] PT-APYUSD-5NOV2026 implies 14.12% fixed for 56 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xc5f938a8ef5f3bf9e72f5aa094baf5e03f4727d3",
 "pt": "0xb5be35d8ff83d431899b95851cb17a2b4bcef150",
 "pt_symbol": "PT-APYUSD-5NOV2026",
 "implied_apy_pct": 14.117,
 "days_to_maturity": 55.561956018518515,
 "pt_to_asset": 0.9800994633181038,
 "underlying": "APYUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 10.517,
 "classification": "credit spread",
 "pt_depth_units": 6476850,
 "pt_depth_usd": 6347957,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 7.25%, $115,027 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSDE-10DEC2026 implies 18.16% fixed for 91 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x90b70c407f1077f8eb92bf423b44cd92329b737a",
 "pt": "0x2ae4f59e500b6ddeb88c480edf277eda54a00205",
 "pt_symbol": "PT-REUSDE-10DEC2026",
 "implied_apy_pct": 18.157,
 "days_to_maturity": 90.56195601851852,
 "pt_to_asset": 0.9594490496881547,
 "underlying": "REUSDE",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 14.557,
 "classification": "credit spread",
 "pt_depth_units": 3583307,
 "pt_depth_usd": 3438001,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 12.55%, $107,880 per year, GO — clears gas, impact and competition at this size

### [info] PT-USD3-17DEC2026 implies 14.11% fixed for 98 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4a5067c3ff1abb7449244025b0e37feaf77d8e3e",
 "pt": "0x7f47c3e6b2c00fc4eb4d5ae50d0ab0ab6888eb4d",
 "pt_symbol": "PT-USD3-17DEC2026",
 "implied_apy_pct": 14.106,
 "days_to_maturity": 97.56195601851852,
 "pt_to_asset": 0.9653442635565657,
 "underlying": "USD3",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 10.506,
 "classification": "credit spread",
 "pt_depth_units": 4534056,
 "pt_depth_usd": 4376925,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 8.64%, $94,588 per year, GO — clears gas, impact and competition at this size

### [info] PT-SUSDX-3DEC2026 implies 20.33% fixed for 84 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x5e572498e9f83650f0ff24194999bddb4b390928",
 "pt": "0x06ebad062fd573ca31a72d6dfb0f425da2153985",
 "pt_symbol": "PT-SUSDX-3DEC2026",
 "implied_apy_pct": 20.33,
 "days_to_maturity": 83.56195601851852,
 "pt_to_asset": 0.9585153821039194,
 "underlying": "SUSDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 16.73,
 "classification": "credit spread",
 "pt_depth_units": 1626693,
 "pt_depth_usd": 1559211,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 14.56%, $56,743 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSD-10DEC2026 implies 11.04% fixed for 91 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x13285bcbc27f92b47b4edb99d744c07b48c977c0",
 "pt": "0xecfafdc7741323a945a163ed068b5a3c43483957",
 "pt_symbol": "PT-REUSD-10DEC2026",
 "implied_apy_pct": 11.043,
 "days_to_maturity": 90.56195601851852,
 "pt_to_asset": 0.9743447397905655,
 "underlying": "REUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 7.443,
 "classification": "credit spread",
 "pt_depth_units": 4070486,
 "pt_depth_usd": 3966056,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.44%, $53,919 per year, GO — clears gas, impact and competition at this size

### [info] PYUSD pays 3.29pp more on Aave v3 than SparkLend; best size $4.4M earns $50k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.904,
  "SparkLend": 0.613
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.291,
 "gap_pp_despiked": 3.291,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7581817,
  "SparkLend": 100000768
 },
 "utilisation": {
  "Aave v3": 0.882,
  "SparkLend": 0.174
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 4395814.70148976,
  "apr_at_size_pct": 1.749,
  "over_low_venue_usd_per_year": 49941
 },
 "unconstrained_best_size": {
  "size_usd": 4395814.70148976,
  "apr_at_size_pct": 1.749,
  "over_low_venue_usd_per_year": 49941
 },
 "source_available_usd": 82566483.848158,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.813
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.129
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 1.608
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 0.353
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.071
  }
 ]
}
```

Economics: net APR 1.14%, $49,941 per year, GO — clears gas, impact and competition at this size

### [info] PT-SUSD3-17DEC2026 implies 23.83% fixed for 98 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x7972de1c2f9f11f622a188fbae8c0a943880424f",
 "pt": "0x41f45d21502bde8211e94d94ef2eeebcfc48a6ac",
 "pt_symbol": "PT-SUSD3-17DEC2026",
 "implied_apy_pct": 23.83,
 "days_to_maturity": 97.56195601851852,
 "pt_to_asset": 0.9444710837125914,
 "underlying": "SUSD3",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 20.23,
 "classification": "credit spread",
 "pt_depth_units": 944466,
 "pt_depth_usd": 892021,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 18.37%, $40,961 per year, GO — clears gas, impact and competition at this size

### [info] PT-STRUSD-26NOV2026 implies 11.83% fixed for 77 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xac028348c46d3455899a2b9b50077c11960eaddb",
 "pt": "0x74299580811e1c3c1a2831db079ba0a8f513998f",
 "pt_symbol": "PT-STRUSD-26NOV2026",
 "implied_apy_pct": 11.83,
 "days_to_maturity": 76.56195601851852,
 "pt_to_asset": 0.9768195022528944,
 "underlying": "STRUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 8.23,
 "classification": "credit spread",
 "pt_depth_units": 1816154,
 "pt_depth_usd": 1774055,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.86%, $25,981 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.62pp more on Aave v3 than SparkLend; best size $7.1M earns $22k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "DAI",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.08,
  "SparkLend": 2.459
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 0.62,
 "gap_pp_despiked": 0.62,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 DAI: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 131451538,
  "SparkLend": 307744835
 },
 "utilisation": {
  "Aave v3": 0.869,
  "SparkLend": 0.677
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 7082204.918894945,
  "apr_at_size_pct": 2.773,
  "over_low_venue_usd_per_year": 22246
 },
 "unconstrained_best_size": {
  "size_usd": 7082204.918894945,
  "apr_at_size_pct": 2.773,
  "over_low_venue_usd_per_year": 22246
 },
 "source_available_usd": 99894296.04482904,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.076
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.034
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 2.859
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 2.175
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.994
  }
 ]
}
```

Economics: net APR 0.31%, $22,246 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v4 EURC/USDC: $250.0k in a ±0.07% band earns 2.1bp of fees less 1.7bp of divergence over 5.0h (7.8% a year if it repeats)

```json
{
 "pool": "0xb2b92b56988a4edbe255989792c6ea239b25eaf66b42093145cbf8f630db3a17",
 "venue": "uniswap_v4",
 "pair": "EURC/USDC",
 "stable_pair": false,
 "window_hours": 5.0,
 "observed_price_range_pct": 0.068,
 "band_quoted_pct": 0.068,
 "concentration_multiplier": 2942.7,
 "band_ladder": [
  {
   "band_pct": 0.068,
   "apr_pct_at_10000": 40.03
  },
  {
   "band_pct": 0.136,
   "apr_pct_at_10000": 20.66
  },
  {
   "band_pct": 0.34,
   "apr_pct_at_10000": 8.44
  },
  {
   "band_pct": 1.36,
   "apr_pct_at_10000": 2.15
  }
 ],
 "pool_band_capital_usd": 269014,
 "full_range_capital_usd": 791621522,
 "passive_fees_usd": 111.18,
 "volume_usd": 293349,
 "swaps": 55,
 "annualisation_factor": 1752.0,
 "n_takers": 36,
 "top_taker": "0x1bebaf9f291461c96491bcb15de1d56262eb3e6d",
 "top_taker_share": 0.2041,
 "taker_herfindahl": 0.1053,
 "apr_band_1pct_as_reported": 0.0496,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 3.985,
   "divergence_bps_window": 1.7,
   "net_bps_window": 2.285,
   "over_benchmark_usd": 2.29,
   "annualised_net_apr_pct": 40.03
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 3.485,
   "divergence_bps_window": 1.7,
   "net_bps_window": 1.785,
   "over_benchmark_usd": 8.93,
   "annualised_net_apr_pct": 31.28
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 2.142,
   "divergence_bps_window": 1.7,
   "net_bps_window": 0.442,
   "over_benchmark_usd": 11.06,
   "annualised_net_apr_pct": 7.75
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.876,
   "divergence_bps_window": 1.7,
   "net_bps_window": -0.824,
   "over_benchmark_usd": -82.36,
   "annualised_net_apr_pct": -14.43
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 7.75%, $19,377 per year, no — nets 7.75% a year at $250,000 in a ±0.068% band, before any view on holding the pair

### [info] PT-USDX-3DEC2026 implies 15.54% fixed for 84 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x0bef762d2094ac80821c657dea6783fc43435292",
 "pt": "0xa4b3a2eec53863fe2c9ab0041d480cf964942e84",
 "pt_symbol": "PT-USDX-3DEC2026",
 "implied_apy_pct": 15.541,
 "days_to_maturity": 83.56195601851852,
 "pt_to_asset": 0.9674691109741451,
 "underlying": "USDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 11.941,
 "classification": "credit spread",
 "pt_depth_units": 648885,
 "pt_depth_usd": 627777,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 9.77%, $15,329 per year, GO — clears gas, impact and competition at this size

### [info] PT-USDAT-14JAN2027 implies 6.96% fixed for 126 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4ccf6deb3d1895373f604b418ff55d8adae8b846",
 "pt": "0xba96292ee7673e3b546cc90db6d97111cd9a314f",
 "pt_symbol": "PT-USDAT-14JAN2027",
 "implied_apy_pct": 6.961,
 "days_to_maturity": 125.56195601851852,
 "pt_to_asset": 0.977117921125418,
 "underlying": "USDAT",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 3.361,
 "classification": "credit spread",
 "pt_depth_units": 2113909,
 "pt_depth_usd": 2065538,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 1.91%, $9,884 per year, GO — clears gas, impact and competition at this size

### [info] PT-TRUSD-26NOV2026 implies 9.69% fixed for 77 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xfcf009cb3135da12a6eb1f73f3ee05392a7bc947",
 "pt": "0x7191878f1fe834b28f4d0cead0e4375b814c4abb",
 "pt_symbol": "PT-TRUSD-26NOV2026",
 "implied_apy_pct": 9.693,
 "days_to_maturity": 76.56195601851852,
 "pt_to_asset": 0.9807806392002837,
 "underlying": "TRUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 6.093,
 "classification": "credit spread",
 "pt_depth_units": 586200,
 "pt_depth_usd": 574934,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 3.72%, $5,348 per year, GO — clears gas, impact and competition at this size

### [info] PT-APXUSD-5NOV2026 implies 9.88% fixed for 56 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xaf0349fb9b1ba07d34381870c59b560b31412660",
 "pt": "0xaf687b5ecb525ccea96115088999b4ed80c388b6",
 "pt_symbol": "PT-APXUSD-5NOV2026",
 "implied_apy_pct": 9.881,
 "days_to_maturity": 55.561956018518515,
 "pt_to_asset": 0.9857589939388811,
 "underlying": "APXUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 6.281,
 "classification": "credit spread",
 "pt_depth_units": 423394,
 "pt_depth_usd": 417364,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 3.13%, $3,146 per year, GO — clears gas, impact and competition at this size

### [info] PT-SRUSDE-22OCT2026 implies 5.44% fixed for 42 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x66ec657c59cdcaf171ab43b83da3942758bf8a97",
 "pt": "0x59bc9fae5d62b19d4f8d07d758047acb9ee19d34",
 "pt_symbol": "PT-SRUSDE-22OCT2026",
 "implied_apy_pct": 5.437,
 "days_to_maturity": 41.561956018518515,
 "pt_to_asset": 0.993989521540615,
 "underlying": "SRUSDE",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 1.837,
 "classification": "credit spread",
 "pt_depth_units": 2114647,
 "pt_depth_usd": 2101937,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 0.92%, $1,008 per year, GO — clears gas, impact and competition at this size

### [info] Aave v3 USDtb pays 4.88% against the Sky savings rate at 3.60%; best size $74.5k earns $485 a year over it [one-block read, de-spiking unavailable]

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
 "supplied_usd": 15495588,
 "borrowed_usd": 12615405,
 "available_usd": 2880183,
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
   "marginal_apr_pct": 4.03,
   "over_benchmark_usd_per_year": 430
  },
  {
   "size_usd": 1000000.0,
   "marginal_apr_pct": 2.34,
   "over_benchmark_usd_per_year": -12605
  },
  {
   "size_usd": 10000000.0,
   "marginal_apr_pct": 0.979,
   "over_benchmark_usd_per_year": -262066
  },
  {
   "size_usd": 50000000.0,
   "marginal_apr_pct": 0.148,
   "over_benchmark_usd_per_year": -1725799
  }
 ],
 "best": {
  "size_usd": 74505.80596923828,
  "apr": 0.042509823991568566,
  "marginal_apr_pct": 4.251,
  "over_benchmark_usd_per_year": 485
 },
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 0.65%, $485 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $109 of $56289 pool fees (0.19%) across 164 episodes by 10 operator(s)

```json
{
 "episodes": 164,
 "fee_taken_usd": 108.82,
 "pool_fees_usd": 56289.37,
 "share_of_fees": 0.0019,
 "swap_usd_bracketed": 1524434,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 70,
   "fee_taken_usd": 83.1
  },
  {
   "sender": "0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2",
   "episodes": 16,
   "fee_taken_usd": 3.66
  },
  {
   "sender": "0x654fae4aa229d104cabead47e56703f58b174be4",
   "episodes": 8,
   "fee_taken_usd": 1.31
  },
  {
   "sender": "0x5c096ef846447cb935c5d247e4ab2a867ecc33a9",
   "episodes": 8,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0xc54b77b28ee4d18cd3d93991f08b79bc85c71097",
   "episodes": 6,
   "fee_taken_usd": 19.79
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR -0.04%, $-352,786 per year, no — negative net per run at this size

### [info] 277 poisoning attempt(s) from 130 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0xd6e581c232644bdc445174d0a6c3698efe1950ee5f66e3060a48c5f6b0bd7fe4",
   "big_eth": 100.0,
   "victim": "0xbeb33a4bbca7f0928f6d0f8d17bc466aa3c031d9",
   "impersonated": "0x2cd5917abf2558430b3f53f1ea6a0657178ff568",
   "attacker": "0x2cd2a8fde29fe93e67208f8c3dbd9fbd71aff568",
   "dust_tx": "0xa420f8f7554b53b2dad510f86d93f3facbc002b35f9a1dd1ea9313a9a2f0a6f4",
   "seconds_after": 60
  },
  {
   "big_tx": "0xd6e581c232644bdc445174d0a6c3698efe1950ee5f66e3060a48c5f6b0bd7fe4",
   "big_eth": 100.0,
   "victim": "0xbeb33a4bbca7f0928f6d0f8d17bc466aa3c031d9",
   "impersonated": "0x2cd5917abf2558430b3f53f1ea6a0657178ff568",
   "attacker": "0x2cd56f8e5f8fd1907aaccbb875eb0c1ca3c7f568",
   "dust_tx": "0x3c7f56f259f16fc488d1ffb4137db0312c942427ae85c588345677acaeef9513",
   "seconds_after": 480
  },
  {
   "big_tx": "0xea7d8668d72156c9b72b5bb3f355c44721487416b5e7017815b955375f716189",
   "big_eth": 7649.9,
   "victim": "0xe0f4adb71439bbca30ec162dd933f22273db58cc",
   "impersonated": "0x8fa4ee1776032b612206e754ec2382b534d4ac6f",
   "attacker": "0x8fa43302d71abe061980957292202e6083e2ac6f",
   "dust_tx": "0x1cd3b8ee75aa677b709631d303b2b13660509d863370ce3905505062a858bd81",
   "seconds_after": 588
  },
  {
   "big_tx": "0xdd704fe0a4606e892f24f4127e98a2dae09cbd08ac2b29e4506662c720331521",
   "big_eth": 206.0,
   "victim": "0xcfbbf8dc80bb324d2f8634cc73d6e8f6784d3230",
   "impersonated": "0x73dec5699480469a6c7cb160108b0c40cd1e6294",
   "attacker": "0x73d587f34785704920f8697e8455913f641e6294",
   "dust_tx": "0x35f4ee97f3defbbe603412392c37238ecc868cd5ca7f66133215d5502037561c",
   "seconds_after": 192
  },
  {
   "big_tx": "0xdd704fe0a4606e892f24f4127e98a2dae09cbd08ac2b29e4506662c720331521",
   "big_eth": 206.0,
   "victim": "0xcfbbf8dc80bb324d2f8634cc73d6e8f6784d3230",
   "impersonated": "0x73dec5699480469a6c7cb160108b0c40cd1e6294",
   "attacker": "0x73dea632d829524b1a9d4789b1101e830fa06294",
   "dust_tx": "0x9dcc5dbd3583b476fc1b44781742a4fbf86b56be87376510bbc6b0fbfa0f6403",
   "seconds_after": 516
  },
  {
   "big_tx": "0xdd704fe0a4606e892f24f4127e98a2dae09cbd08ac2b29e4506662c720331521",
   "big_eth": 206.0,
   "victim": "0xcfbbf8dc80bb324d2f8634cc73d6e8f6784d3230",
   "impersonated": "0x73dec5699480469a6c7cb160108b0c40cd1e6294",
   "attacker": "0x73d587f34785704920f8697e8455913f641e6294",
   "dust_tx": "0xa3c7c9b084d77f6009a77a89ed296beefde7a9b98a93
```

### [info] 0x6b35bbf505: 65 buyers, 4 sellers, 5% of 22 sell attempts emitted no logs — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x6b35bbf5056c8ff0d46fcc991a906d361c6fa686",
 "symbol": null,
 "label": null,
 "distinct_buyers": 65,
 "distinct_sellers": 4,
 "seller_to_buyer_ratio": 0.0615,
 "buy_legs": 106,
 "sell_legs": 21,
 "router_calls_naming_it": 22,
 "of_which_emitted_no_logs": 1,
 "fail_rate": 0.045,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 25945001,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] 0x33e8f27903: 35 buyers, 2 sellers, 8% of 12 sell attempts emitted no logs — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x33e8f279032eb970eea519260e46213414f889b8",
 "symbol": null,
 "label": null,
 "distinct_buyers": 35,
 "distinct_sellers": 2,
 "seller_to_buyer_ratio": 0.0571,
 "buy_legs": 47,
 "sell_legs": 11,
 "router_calls_naming_it": 12,
 "of_which_emitted_no_logs": 1,
 "fail_rate": 0.083,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 25945014,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] rETH trades 48.5bp below NAV, 43.5bp after the 5.0bp round trip; burn into available rETH contract ETH and excess deposit-pool ETH; liquidity requires a pinned check — conditional, so the exit may not be there when you want it

```json
{
 "asset": "rETH",
 "nav_source": "0xae78736c getExchangeRate()",
 "nav": 2889.872023,
 "market_vw_price": 2875.848864,
 "market_median": 2876.367523,
 "market_p10": 2868.238173,
 "discount_bps": 48.53,
 "traded_volume_usd": 1205638,
 "implied_daily_volume_usd": 5787062,
 "refills_needed_per_year": 365,
 "swaps": 100,
 "venues": {
  "uniswap_v3": 22,
  "uniswap_v4": 49,
  "curve": 29
 },
 "redemption": {
  "days": 1.0,
  "atomic": false,
  "availability": "conditional",
  "exit_bps": 5.0,
  "path": "burn into available rETH contract ETH and excess deposit-pool ETH; liquidity requires a pinned check"
 },
 "net_edge_bps": 43.53,
 "price_dispersion_bps": 39.79,
 "discount_at_p10_bps": 74.86,
 "significance_vs_dispersion": 1.09,
 "dispersion_note": "the spread of an ETH-denominated claim also contains ETH\u2019s own move over the window, so this test is conservative here",
 "why": "the protocol pays NAV and the market paid less; the gap closes when you redeem, and the wait is the reason a bot cannot take it from you"
}
```

Economics: net APR unquoted, $0 per year, no — Redemption is conditional; exit capacity/access has not been verified. The conditional model is not an executable quote.

