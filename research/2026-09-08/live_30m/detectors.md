# Detector sweep — research/2026-09-08/live_30m

Ran 13 detector(s); 22 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 0.36 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `borrow_cost` | 6 | 0.33 | cheapest venue to borrow each asset, capped by the liquidity actually withdrawable there |
| `dollar_rate_outlier` | 1 | 0.00 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `fixed_vs_floating` | 3 | 0.00 | Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth |
| `gas_concentration` | 0 | 0.00 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `liquidity_blackout` | 0 | 0.00 | lending reserves whose withdrawable liquidity collapses, and the time of day it happens |
| `lp_marginal_yield` | 1 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 3 | 0.49 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 0 | 0.36 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 0 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 1 | 0.35 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

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
  "Aave v3": 11187664,
  "SparkLend": 739279868,
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

Economics: net APR 3.48%, $34,759,581 per year, GO — clears gas, impact and competition at this size

### [notable] USDS borrows 1.60pp cheaper on SparkLend than Aave v3; $254.2M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDS",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 3.926,
  "liquidity_usd": 254177136,
  "utilisation": 0.6561827978309852,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 5.524,
  "liquidity_usd": 10852723
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.926,
   "liquidity_usd": 254177136,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 5.524,
   "liquidity_usd": 10852723,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.598,
 "refinance_gas_usd": 0.162,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.60%, $4,062,790 per year, GO — clears gas, impact and competition at this size

### [notable] USDT pays 0.94pp more on Aave v3 than SparkLend; best size $244.5M earns $1.0M a year over SparkLend

```json
{
 "asset": "USDT",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.558,
  "SparkLend": 2.619,
  "Compound v3 USDT": 3.014
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.561
 },
 "gap_pp_spot": 0.939,
 "gap_pp_despiked": 0.942,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 2984272898,
  "SparkLend": 391782517,
  "Compound v3 USDT": 185226370
 },
 "utilisation": {
  "Aave v3": 0.93,
  "SparkLend": 0.828,
  "Compound v3 USDT": 0.837
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 244531534,
  "apr_at_size_pct": 3.039,
  "over_low_venue_usd_per_year": 1028468
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.558
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.555
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.546
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.499
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 3.331
  }
 ]
}
```

Economics: net APR 0.42%, $1,028,468 per year, GO — clears gas, impact and competition at this size

### [notable] DAI borrows 0.67pp cheaper on SparkLend than Aave v3; $99.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "DAI",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.043,
  "liquidity_usd": 99710818,
  "utilisation": 0.6765814085988826,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.715,
  "liquidity_usd": 17430021
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.043,
   "liquidity_usd": 99710818,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.715,
   "liquidity_usd": 17430021,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.671,
 "refinance_gas_usd": 0.162,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.67%, $669,324 per year, GO — clears gas, impact and competition at this size

### [notable] PYUSD borrows 0.48pp cheaper on SparkLend than Morpho Blue; $83.2M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "PYUSD",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 3.89,
  "liquidity_usd": 83199792,
  "utilisation": 0.1680063821566896,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 4.367,
  "liquidity_usd": 8554845
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.89,
   "liquidity_usd": 83199792,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 4.367,
   "liquidity_usd": 8554845,
   "collateral": "sUSDe (0x9d39a5de, LLTV 91.5%)"
  }
 ],
 "gap_pp": 0.477,
 "refinance_gas_usd": 0.162,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.48%, $396,666 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDe/USDC: $1.0M in a ±0.01% band earns 0.1bp of fees less 0.0bp of divergence over 0.5h (13.5% a year if it repeats)

```json
{
 "pool": "0x56fc29b86900aa0afa6e20b020429bffba1105cfb45070492c67529b46eb48c1",
 "venue": "uniswap_v4",
 "pair": "USDe/USDC",
 "stable_pair": true,
 "window_hours": 0.503,
 "observed_price_range_pct": 0.009,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 67.03
  },
  {
   "band_pct": 0.018,
   "apr_pct_at_10000": 37.92
  },
  {
   "band_pct": 0.045,
   "apr_pct_at_10000": 15.38
  },
  {
   "band_pct": 0.18,
   "apr_pct_at_10000": 3.88
  }
 ],
 "pool_band_capital_usd": 238656,
 "full_range_capital_usd": 4773484539,
 "passive_fees_usd": 9.57,
 "volume_usd": 308602,
 "swaps": 23,
 "annualisation_factor": 17415.5,
 "n_takers": 20,
 "top_taker": "0xcb9240ff4a99e086f1843229fc7fe1ba7b30f941",
 "top_taker_share": 0.2445,
 "taker_herfindahl": 0.1423,
 "apr_band_1pct_as_reported": 0.007,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.385,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.385,
   "over_benchmark_usd": 0.36,
   "annualised_net_apr_pct": 67.03
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.332,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.332,
   "over_benchmark_usd": 1.55,
   "annualised_net_apr_pct": 57.74
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.196,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.196,
   "over_benchmark_usd": 4.38,
   "annualised_net_apr_pct": 34.11
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.077,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.077,
   "over_benchmark_usd": 5.66,
   "annualised_net_apr_pct": 13.46
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 13.46%, $98,572 per year, GO — nets 13.46% a year at $1,000,000 in a ±0.010% band against a 3.60% savings rate

### [notable] USDC borrows 0.89pp cheaper on SparkLend than Compound v3 USDC; $2.0M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDC",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.267,
  "liquidity_usd": 2002475,
  "utilisation": 0.9219185798370789,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Compound v3 USDC",
  "borrow_apy_pct": 5.162,
  "liquidity_usd": 36408549
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.267,
   "liquidity_usd": 2002475,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.292,
   "liquidity_usd": 142443248,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 4.573,
   "liquidity_usd": 1594191,
   "collateral": "0xdc169abe56 (0xdc169abe, LLTV 91.5%)"
  },
  {
   "venue": "Compound v3 USDC",
   "borrow_apy_pct": 5.162,
   "liquidity_usd": 36408549,
   "collateral": "the Comet\u2019s listed collaterals"
  }
 ],
 "gap_pp": 0.894,
 "refinance_gas_usd": 0.162,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.89%, $17,907 per year, GO — clears gas, impact and competition at this size

### [notable] USDT borrows 0.79pp cheaper on Morpho Blue than Aave v3; $1.9M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDT",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.466,
  "liquidity_usd": 1910654,
  "utilisation": 0.901399,
  "collateral_required": "sUSDS (0xa3931d71, LLTV 96.5%)",
  "market": "0x3274643db77a064a"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.252,
  "liquidity_usd": 210066031
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.466,
   "liquidity_usd": 1910654,
   "collateral": "sUSDS (0xa3931d71, LLTV 96.5%)"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.516,
   "liquidity_usd": 67555362,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Compound v3 USDT",
   "borrow_apy_pct": 3.826,
   "liquidity_usd": 30147776,
   "collateral": "the Comet\u2019s listed collaterals"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.252,
   "liquidity_usd": 210066031,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.786,
 "refinance_gas_usd": 0.162,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.79%, $15,018 per year, GO — clears gas, impact and competition at this size

### [notable] RLUSD borrows 0.67pp cheaper on Morpho Blue than Aave v3; $1.2M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "RLUSD",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.75,
  "liquidity_usd": 1246903,
  "utilisation": 0.900451,
  "collateral_required": "cbBTC (0xcbb7c000, LLTV 86.0%)",
  "market": "0xffd010618ed3cb39"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.422,
  "liquidity_usd": 1786121
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.75,
   "liquidity_usd": 1246903,
   "collateral": "cbBTC (0xcbb7c000, LLTV 86.0%)"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.422,
   "liquidity_usd": 1786121,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.672,
 "refinance_gas_usd": 0.162,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.67%, $8,375 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 0.73pp more on Compound v3 USDC than SparkLend; best size $466k earns $2k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.624,
  "SparkLend": 3.541,
  "Compound v3 USDC": 4.271,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.624
 },
 "gap_pp_spot": 0.731,
 "gap_pp_despiked": 0.731,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2307156150,
  "SparkLend": 25645985,
  "Compound v3 USDC": 376227702,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.938,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.903
 },
 "dilution_basis": "sampled",
 "best_size": {
  "size_usd": 465599,
  "apr_at_size_pct": 3.915,
  "over_low_venue_usd_per_year": 1742
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 4.195
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.506
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.209
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.049
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 2.569
  }
 ]
}
```

Economics: net APR 0.37%, $1,742 per year, GO — clears gas, impact and competition at this size

### [notable] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 2,212 recipients in 6 txs (369 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 2215,
 "recipients": 2212,
 "txs": 6,
 "blocks": 6,
 "transfers_per_tx": 369.2,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "19610900130510540",
 "uniform_amount_share": 0.072,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] unlabelled unknown 0x76f30e3f passed $29.1M through in 8 txs (75% ended flat, 6 counterparties)

```json
{
 "address": "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a",
 "shape": "pass-through",
 "gross_usd": 29058081,
 "txs": 8,
 "counterparties": 6,
 "tokens": 5,
 "pass_through_share": 0.75,
 "received_usd": 14528920,
 "sent_usd": 14529161,
 "retained_usd": -241,
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

### [info] PYUSD pays 3.30pp more on Aave v3 than SparkLend; best size $4.4M earns $51k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.886,
  "SparkLend": 0.588
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.298,
 "gap_pp_despiked": 3.298,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7587474,
  "SparkLend": 100000517
 },
 "utilisation": {
  "Aave v3": 0.88,
  "SparkLend": 0.168
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 4399095,
  "apr_at_size_pct": 1.741,
  "over_low_venue_usd_per_year": 50714
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.796
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.115
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

Economics: net APR 1.15%, $50,714 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.61pp more on Aave v3 than SparkLend; best size $7.1M earns $21k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "DAI",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.067,
  "SparkLend": 2.459
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 0.608,
 "gap_pp_despiked": 0.608,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 DAI: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 131586249,
  "SparkLend": 308302679
 },
 "utilisation": {
  "Aave v3": 0.868,
  "SparkLend": 0.677
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 7089463,
  "apr_at_size_pct": 2.762,
  "over_low_venue_usd_per_year": 21474
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.063
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.022
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 2.847
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 2.166
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.99
  }
 ]
}
```

Economics: net APR 0.30%, $21,474 per year, GO — clears gas, impact and competition at this size

### [info] PT-USDX-3DEC2026 implies 15.08% fixed for 86 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x0bef762d2094ac80821c657dea6783fc43435292",
 "pt": "0xa4b3a2eec53863fe2c9ab0041d480cf964942e84",
 "pt_symbol": "PT-USDX-3DEC2026",
 "implied_apy_pct": 15.078,
 "days_to_maturity": 85.64278935185185,
 "pt_to_asset": 0.967584331736232,
 "underlying": "USDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 11.478,
 "classification": "credit spread",
 "pt_depth_units": 609219,
 "pt_depth_usd": 589471,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 9.36%, $13,790 per year, GO — clears gas, impact and competition at this size

### [info] PT-TRUSD-26NOV2026 implies 9.99% fixed for 79 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xfcf009cb3135da12a6eb1f73f3ee05392a7bc947",
 "pt": "0x7191878f1fe834b28f4d0cead0e4375b814c4abb",
 "pt_symbol": "PT-TRUSD-26NOV2026",
 "implied_apy_pct": 9.988,
 "days_to_maturity": 78.64278935185185,
 "pt_to_asset": 0.979696215471707,
 "underlying": "TRUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 6.388,
 "classification": "credit spread",
 "pt_depth_units": 610808,
 "pt_depth_usd": 598406,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 4.08%, $6,102 per year, GO — clears gas, impact and competition at this size

### [info] Aave v3 USDtb pays 5.62% against the Sky savings rate at 3.60%; best size $116.4k earns $1.2k a year over it [one-block read, de-spiking unavailable]

```json
{
 "venue": "Aave v3",
 "asset": "USDtb",
 "supply_apr_spot_pct": 5.615,
 "supply_apr_window_median_pct": null,
 "spiked": false,
 "despike_unavailable": true,
 "benchmark": "Sky savings rate",
 "benchmark_pct": 3.6,
 "gap_pp": 2.015,
 "supplied_usd": 15445598,
 "borrowed_usd": 12640520,
 "available_usd": 2805078,
 "utilisation": 0.8184,
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
   "marginal_apr_pct": 4.737,
   "over_benchmark_usd_per_year": 1137
  },
  {
   "size_usd": 1000000.0,
   "marginal_apr_pct": 2.363,
   "over_benchmark_usd_per_year": -12369
  },
  {
   "size_usd": 10000000.0,
   "marginal_apr_pct": 0.987,
   "over_benchmark_usd_per_year": -261289
  },
  {
   "size_usd": 50000000.0,
   "marginal_apr_pct": 0.149,
   "over_benchmark_usd_per_year": -1725390
  }
 ],
 "best": {
  "size_usd": 116415.32182693481,
  "apr": 0.04592176780243453,
  "marginal_apr_pct": 4.592,
  "over_benchmark_usd_per_year": 1155
 },
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 0.99%, $1,155 per year, GO — clears gas, impact and competition at this size

### [info] PT-SRUSDE-22OCT2026 implies 5.45% fixed for 44 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x66ec657c59cdcaf171ab43b83da3942758bf8a97",
 "pt": "0x59bc9fae5d62b19d4f8d07d758047acb9ee19d34",
 "pt_symbol": "PT-SRUSDE-22OCT2026",
 "implied_apy_pct": 5.45,
 "days_to_maturity": 43.64278935185185,
 "pt_to_asset": 0.9936751517527479,
 "underlying": "SRUSDE",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 1.85,
 "classification": "credit spread",
 "pt_depth_units": 2123236,
 "pt_depth_usd": 2109807,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 0.92%, $1,080 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $7 of $92 pool fees (8.05%) across 15 episodes by 4 operator(s)

```json
{
 "episodes": 15,
 "fee_taken_usd": 7.44,
 "pool_fees_usd": 92.44,
 "share_of_fees": 0.0805,
 "swap_usd_bracketed": 47596,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 7,
   "fee_taken_usd": 4.52
  },
  {
   "sender": "0x654fae4aa229d104cabead47e56703f58b174be4",
   "episodes": 4,
   "fee_taken_usd": 2.92
  },
  {
   "sender": "0x49719d256a5ea16bfa579ea16e95bea9fa41a452",
   "episodes": 3,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0x4cd4499d6e6a0eb8995a2cabd400d1ad35c4d03e",
   "episodes": 1,
   "fee_taken_usd": 0.0
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR -0.00%, $-6,960 per year, no — net APR -0.00% below the 0.00% floor

### [info] 12 poisoning attempt(s) from 12 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0x5819d746ea89023a0bdff01d18caa418dfecf3d088397c35fbb0031ff595a62c",
   "big_eth": 110.79,
   "victim": "0xa47445f9170c17b64dee893463563fd3ee2b7fa9",
   "impersonated": "0xedc8f22c6cc3d568a3595ed3b27b05d25081091d",
   "attacker": "0xedc166cac4def42929e2f03d60492af335a1091d",
   "dust_tx": "0x03015911c9b613e05cdc61da0392fef0c4dee7c8d3410c35cb8180a76f8a9743",
   "seconds_after": 348
  },
  {
   "big_tx": "0x0691bdf9d454b7c488f19dc17c4bec4a2b9dc230d4e7ec968a71b48c0d0d3ae4",
   "big_eth": 300.01,
   "victim": "0xecb7950e7037fe99ec0c7de5a26730aa90f16759",
   "impersonated": "0xbd6988072d155a2ffe63bd1f2179d71087a0e8af",
   "attacker": "0xbd694e05d2412cbbf0ebbfb40c4900e163e6e8af",
   "dust_tx": "0x073d908548f183820f907016287169c8a8108932a04db425108af0479f956ae5",
   "seconds_after": 444
  },
  {
   "big_tx": "0x5b597fc169fbbfd894726b30eed0b60faacc07ad8bf5c63d360fa462b05b06a9",
   "big_eth": 300.01,
   "victim": "0xbd6988072d155a2ffe63bd1f2179d71087a0e8af",
   "impersonated": "0x578e5a1cb272027d37e348647b9a35a20da20d80",
   "attacker": "0x578e982ef5524c74e1e62798096ce4a1188f0d80",
   "dust_tx": "0x6f9815cc53cda5dc99c2799a1dae2ac62e478a4f02b5a27625e2aa46ddcc92f2",
   "seconds_after": 336
  },
  {
   "big_tx": "0x4876ee0da19b1e23baafbf1eedd1a1c63cb09f0a278b0a3adc76fc2e7c6b606b",
   "big_eth": 300.01,
   "victim": "0x578e5a1cb272027d37e348647b9a35a20da20d80",
   "impersonated": "0x41e29c02713929f800419abe5770faa8a5b4dadc",
   "attacker": "0x41e26cc12efa08b3d818cb0af7906c7cc814dadc",
   "dust_tx": "0x41c74df395ada7bd7f39b4ba2834e6eb47a7ab2e60062f29dc40185b5c76b064",
   "seconds_after": 912
  },
  {
   "big_tx": "0x5ab63ed6e6dfd09f76f1ed6f29d957b62f52f02900ad200f4ef53555e7dc0f15",
   "big_eth": 100.0,
   "victim": "0x62425cd6bdcb6bfe51558ea465b063486b70dc9f",
   "impersonated": "0xa448e8dd548c979974af572f751924363d257775",
   "attacker": "0xa4e4a3dfb018c39ff7eb286313672a78c5257775",
   "dust_tx": "0x29c40bd8008f7fc0cee4c1b9630a6628b8e84e24e65cff7bb939ef1a329947bd",
   "seconds_after": 348
  },
  {
   "big_tx": "0x41cdefeb3f188e0c32fe0f504c03f912d93210d776a1e69dda22259ec1244334",
   "big_eth": 733.65,
   "victim": "0x1c68c3de2b02d9ae478d37c7e6c92a53ff01fc66",
   "impersonated": "0x7ccd004bd52db9563670d0c1325a93191e44e5ec",
   "attacker": "0x7ccd11d7cc9e44b4c1d6b79c0b0731e9a909e5ec",
   "dust_tx": "0x6a483c4807007a4cf35e41cbee1d2dc37bd4cb3
```

### [info] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 1,503 recipients in 2 txs (752 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 1503,
 "recipients": 1503,
 "txs": 2,
 "blocks": 2,
 "transfers_per_tx": 751.5,
 "carrier_contract": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "5000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDT to 1,292 recipients in 15 txs (92 per tx)

```json
{
 "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "token_symbol": "USDT",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 1378,
 "recipients": 1292,
 "txs": 15,
 "blocks": 15,
 "transfers_per_tx": 91.9,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "333",
 "uniform_amount_share": 0.007,
 "usd_median": 0.00033295237101,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

