# Detector sweep — research/2026-09-08/live_1h_b

Ran 13 detector(s); 30 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 0.64 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `borrow_cost` | 4 | 0.60 | cheapest venue to borrow each asset, capped by the liquidity actually withdrawable there |
| `dollar_rate_outlier` | 1 | 0.00 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `fixed_vs_floating` | 6 | 0.00 | Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth |
| `gas_concentration` | 0 | 0.00 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `liquidity_blackout` | 0 | 0.00 | lending reserves whose withdrawable liquidity collapses, and the time of day it happens |
| `lp_marginal_yield` | 3 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 4 | 0.91 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 2 | 0.67 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 1 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 2 | 0.64 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

### [notable] unlabelled unknown 0x76f30e3f passed $296.2M through in 16 txs (75% ended flat, 12 counterparties)

```json
{
 "address": "0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a",
 "shape": "pass-through",
 "gross_usd": 296236566,
 "txs": 16,
 "counterparties": 12,
 "tokens": 5,
 "pass_through_share": 0.75,
 "received_usd": 148117882,
 "sent_usd": 148118684,
 "retained_usd": -803,
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
  "Aave v3": 11187663,
  "SparkLend": 739261546,
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
  "liquidity_usd": 254171242,
  "utilisation": 0.6561822490918016,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 5.524,
  "liquidity_usd": 10852724
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.926,
   "liquidity_usd": 254171242,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 5.524,
   "liquidity_usd": 10852724,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.598,
 "refinance_gas_usd": 0.109,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.60%, $4,062,698 per year, GO — clears gas, impact and competition at this size

### [notable] USDT pays 0.94pp more on Aave v3 than SparkLend; best size $244.4M earns $1.0M a year over SparkLend

```json
{
 "asset": "USDT",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.56,
  "SparkLend": 2.619,
  "Compound v3 USDT": 3.013
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.562
 },
 "gap_pp_spot": 0.941,
 "gap_pp_despiked": 0.943,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 2982295987,
  "SparkLend": 391781209,
  "Compound v3 USDT": 185225658
 },
 "utilisation": {
  "Aave v3": 0.93,
  "SparkLend": 0.828,
  "Compound v3 USDT": 0.837
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 244369546,
  "apr_at_size_pct": 3.041,
  "over_low_venue_usd_per_year": 1032269
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.56
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.558
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.548
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.501
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 3.333
  }
 ]
}
```

Economics: net APR 0.42%, $1,032,269 per year, GO — clears gas, impact and competition at this size

### [notable] DAI borrows 0.67pp cheaper on SparkLend than Aave v3; $99.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "DAI",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.043,
  "liquidity_usd": 99696646,
  "utilisation": 0.676580042227611,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.715,
  "liquidity_usd": 17427696
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.043,
   "liquidity_usd": 99696646,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.715,
   "liquidity_usd": 17427696,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.671,
 "refinance_gas_usd": 0.109,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.67%, $669,229 per year, GO — clears gas, impact and competition at this size

### [notable] sUSDe trades 7.6bp below NAV, 4.9bp after the 2.7bp round trip; cooldownShares, then unstake after cooldownDuration (1 day)

```json
{
 "asset": "sUSDe",
 "nav_source": "0x9d39a5de convertToAssets(uint256)",
 "nav": 1.24705,
 "market_vw_price": 1.246107,
 "market_median": 1.246183,
 "market_p10": 1.246043,
 "discount_bps": 7.57,
 "traded_volume_usd": 463054,
 "implied_daily_volume_usd": 11080056,
 "refills_needed_per_year": 365,
 "swaps": 17,
 "venues": {
  "uniswap_v4": 17
 },
 "redemption": {
  "days": 1.0,
  "atomic": false,
  "availability": "always",
  "exit_bps": 2.7,
  "path": "cooldownShares, then unstake after cooldownDuration (1 day)"
 },
 "net_edge_bps": 4.87,
 "why": "the protocol pays NAV and the market paid less; the gap closes when you redeem, and the wait is the reason a bot cannot take it from you"
}
```

Economics: net APR 17.75%, $82,212 per year, GO — clears gas, impact and competition at this size

### [notable] USDC borrows 0.94pp cheaper on SparkLend than Compound v3 USDC; $2.0M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDC",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.268,
  "liquidity_usd": 1997418,
  "utilisation": 0.9221000074117023,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Compound v3 USDC",
  "borrow_apy_pct": 5.208,
  "liquidity_usd": 36354209
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.268,
   "liquidity_usd": 1997418,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.281,
   "liquidity_usd": 147894184,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 4.392,
   "liquidity_usd": 15184727,
   "collateral": "WBTC (0x2260fac5, LLTV 86.0%)"
  },
  {
   "venue": "Compound v3 USDC",
   "borrow_apy_pct": 5.208,
   "liquidity_usd": 36354209,
   "collateral": "the Comet\u2019s listed collaterals"
  }
 ],
 "gap_pp": 0.94,
 "refinance_gas_usd": 0.109,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.94%, $18,772 per year, GO — clears gas, impact and competition at this size

### [notable] USDT borrows 0.90pp cheaper on Morpho Blue than Aave v3; $1.9M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDT",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.352,
  "liquidity_usd": 1934740,
  "utilisation": 0.900279,
  "collateral_required": "sUSDS (0xa3931d71, LLTV 96.5%)",
  "market": "0x3274643db77a064a"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.254,
  "liquidity_usd": 209094780
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.352,
   "liquidity_usd": 1934740,
   "collateral": "sUSDS (0xa3931d71, LLTV 96.5%)"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.516,
   "liquidity_usd": 67555808,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Compound v3 USDT",
   "borrow_apy_pct": 3.825,
   "liquidity_usd": 30181766,
   "collateral": "the Comet\u2019s listed collaterals"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.254,
   "liquidity_usd": 209094780,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.901,
 "refinance_gas_usd": 0.109,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.90%, $17,438 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 0.77pp more on Compound v3 USDC than SparkLend; best size $535k earns $2k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.606,
  "SparkLend": 3.542,
  "Compound v3 USDC": 4.313,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.605
 },
 "gap_pp_spot": 0.771,
 "gap_pp_despiked": 0.771,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2307441333,
  "SparkLend": 25640797,
  "Compound v3 USDC": 376166118,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.936,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.903
 },
 "dilution_basis": "sampled",
 "best_size": {
  "size_usd": 535351,
  "apr_at_size_pct": 3.902,
  "over_low_venue_usd_per_year": 1929
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 4.236
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.547
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

Economics: net APR 0.36%, $1,929 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDC/USDT: $10.0k in a ±0.01% band earns 0.0bp of fees less 0.0bp of divergence over 1.0h (3.5% a year if it repeats)

```json
{
 "pool": "0x0fb0e40cec3bb23e13abc585958a93c796fbea56955e19a23727a716a0423239",
 "venue": "uniswap_v4",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 1.003,
 "observed_price_range_pct": 0.002,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3.54
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3.54
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3.54
  },
  {
   "band_pct": 0.04,
   "apr_pct_at_10000": 0.89
  }
 ],
 "pool_band_capital_usd": 843658,
 "full_range_capital_usd": 16874424051,
 "passive_fees_usd": 3.46,
 "volume_usd": 384932,
 "swaps": 115,
 "annualisation_factor": 8733.8,
 "n_takers": 104,
 "top_taker": "0x4037e1d87b2473428dd847826114af91406e1f69",
 "top_taker_share": 0.1159,
 "taker_herfindahl": 0.0416,
 "apr_band_1pct_as_reported": 0.0004,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.041,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.041,
   "over_benchmark_usd": -0.0,
   "annualised_net_apr_pct": 3.54
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.039,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.039,
   "over_benchmark_usd": -0.01,
   "annualised_net_apr_pct": 3.38
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.032,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.032,
   "over_benchmark_usd": -0.24,
   "annualised_net_apr_pct": 2.76
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.019,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.019,
   "over_benchmark_usd": -2.25,
   "annualised_net_apr_pct": 1.64
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 3.54%, $0 per year, no — nets 3.54% a year at $10,000 in a ±0.010% band against a 3.60% savings rate

### [notable] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 5,375 recipients in 12 txs (453 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 5434,
 "recipients": 5375,
 "txs": 12,
 "blocks": 12,
 "transfers_per_tx": 452.8,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "19610938589326354",
 "uniform_amount_share": 0.14,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 2,004 recipients in 4 txs (626 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 2505,
 "recipients": 2004,
 "txs": 4,
 "blocks": 4,
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

### [info] unlabelled eoa 0x3a3c0060 cycled $42.1M and ended the window flat (3 txs, 2 counterparties)

```json
{
 "address": "0x3a3c006053a9b40286b9951a11be4c5808c11dc8",
 "shape": "cycles",
 "gross_usd": 83984679,
 "txs": 3,
 "counterparties": 2,
 "tokens": 2,
 "pass_through_share": 0.0,
 "received_usd": 42103217,
 "sent_usd": 41881461,
 "retained_usd": 221756,
 "retention": 0.0053,
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

### [info] exchange Binance 20 (model-memory) moved 94% of its flow with one counterparty

```json
{
 "address": "0x4976a4a02f38326660d17bf34b431dc6e2eb2327",
 "label": "Binance 20 (model-memory)",
 "source": "model-memory",
 "counterparty": "0x28c6c06298d514db089934071355e5743bf21d60",
 "counterparty_label": "Binance 14 (model-memory)",
 "share": 0.938,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] exchange Binance 28 (model-memory) moved 100% of its flow with one counterparty

```json
{
 "address": "0x5a52e96bacdabb82fd05763e25335261b270efcb",
 "label": "Binance 28 (model-memory)",
 "source": "model-memory",
 "counterparty": "0x835678a611b28684005a5e2233695fb6cbbb0007",
 "counterparty_label": null,
 "share": 1.0,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] PT-USD3-17DEC2026 implies 14.37% fixed for 100 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4a5067c3ff1abb7449244025b0e37feaf77d8e3e",
 "pt": "0x7f47c3e6b2c00fc4eb4d5ae50d0ab0ab6888eb4d",
 "pt_symbol": "PT-USD3-17DEC2026",
 "implied_apy_pct": 14.37,
 "days_to_maturity": 99.689,
 "pt_to_asset": 0.963991897387582,
 "underlying": "USD3",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 10.77,
 "classification": "credit spread",
 "pt_depth_units": 4564251,
 "pt_depth_usd": 4399901,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 8.95%, $98,434 per year, GO — clears gas, impact and competition at this size

### [info] PT-SUSDX-3DEC2026 implies 20.38% fixed for 86 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x5e572498e9f83650f0ff24194999bddb4b390928",
 "pt": "0x06ebad062fd573ca31a72d6dfb0f425da2153985",
 "pt_symbol": "PT-SUSDX-3DEC2026",
 "implied_apy_pct": 20.379,
 "days_to_maturity": 85.689,
 "pt_to_asset": 0.9573912851224085,
 "underlying": "SUSDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 16.779,
 "classification": "credit spread",
 "pt_depth_units": 1579629,
 "pt_depth_usd": 1512323,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 14.66%, $55,426 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSD-10DEC2026 implies 11.04% fixed for 93 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x13285bcbc27f92b47b4edb99d744c07b48c977c0",
 "pt": "0xecfafdc7741323a945a163ed068b5a3c43483957",
 "pt_symbol": "PT-REUSD-10DEC2026",
 "implied_apy_pct": 11.043,
 "days_to_maturity": 92.689,
 "pt_to_asset": 0.9737499575718152,
 "underlying": "REUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 7.443,
 "classification": "credit spread",
 "pt_depth_units": 4100072,
 "pt_depth_usd": 3992445,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.48%, $54,738 per year, GO — clears gas, impact and competition at this size

### [info] PYUSD pays 3.29pp more on Aave v3 than SparkLend; best size $4.4M earns $51k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.875,
  "SparkLend": 0.588
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.287,
 "gap_pp_despiked": 3.287,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7599086,
  "SparkLend": 100000442
 },
 "utilisation": {
  "Aave v3": 0.878,
  "SparkLend": 0.168
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 4405827,
  "apr_at_size_pct": 1.736,
  "over_low_venue_usd_per_year": 50590
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.786
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.108
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 1.599
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

Economics: net APR 1.15%, $50,590 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v4 sUSDe/USDT: $250.0k in a ±0.02% band earns 0.6bp of fees less 0.4bp of divergence over 1.0h (17.3% a year if it repeats)

```json
{
 "pool": "0xb20351bcf606dcc3525d2ed36760a86a5dec7423b77d41125bd4a416ba93448b",
 "venue": "uniswap_v4",
 "pair": "sUSDe/USDT",
 "stable_pair": false,
 "window_hours": 1.003,
 "observed_price_range_pct": 0.017,
 "band_quoted_pct": 0.017,
 "concentration_multiplier": 11766.2,
 "band_ladder": [
  {
   "band_pct": 0.017,
   "apr_pct_at_10000": 42.71
  },
  {
   "band_pct": 0.034,
   "apr_pct_at_10000": 21.75
  },
  {
   "band_pct": 0.085,
   "apr_pct_at_10000": 8.8
  },
  {
   "band_pct": 0.34,
   "apr_pct_at_10000": 2.22
  }
 ],
 "pool_band_capital_usd": 503379,
 "full_range_capital_usd": 5922855202,
 "passive_fees_usd": 46.92,
 "volume_usd": 464542,
 "swaps": 25,
 "annualisation_factor": 8733.8,
 "n_takers": 14,
 "top_taker": "0x3a55e304d9cf13e45ead6ba3dabccadd3a419356",
 "top_taker_share": 0.3807,
 "taker_herfindahl": 0.2373,
 "apr_band_1pct_as_reported": 0.0139,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.914,
   "divergence_bps_window": 0.425,
   "net_bps_window": 0.489,
   "over_benchmark_usd": 0.49,
   "annualised_net_apr_pct": 42.71
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.848,
   "divergence_bps_window": 0.425,
   "net_bps_window": 0.423,
   "over_benchmark_usd": 2.11,
   "annualised_net_apr_pct": 36.94
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.623,
   "divergence_bps_window": 0.425,
   "net_bps_window": 0.198,
   "over_benchmark_usd": 4.95,
   "annualised_net_apr_pct": 17.28
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.312,
   "divergence_bps_window": 0.425,
   "net_bps_window": -0.113,
   "over_benchmark_usd": -11.29,
   "annualised_net_apr_pct": -9.86
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 17.28%, $43,232 per year, no — nets 17.28% a year at $250,000 in a ±0.017% band, before any view on holding the pair

### [info] uniswap_v3 WBTC/USDT: $50.0k in a ±0.20% band earns 5.8bp of fees less 4.9bp of divergence over 1.0h (80.3% a year if it repeats)

```json
{
 "pool": "0x56534741cd8b152df6d48adf7ac51f75169a83b2",
 "venue": "uniswap_v3",
 "pair": "WBTC/USDT",
 "stable_pair": false,
 "window_hours": 1.003,
 "observed_price_range_pct": 0.195,
 "band_quoted_pct": 0.195,
 "concentration_multiplier": 1027.1,
 "band_ladder": [
  {
   "band_pct": 0.195,
   "apr_pct_at_10000": 177.02
  },
  {
   "band_pct": 0.39,
   "apr_pct_at_10000": 96.01
  },
  {
   "band_pct": 0.975,
   "apr_pct_at_10000": 40.42
  },
  {
   "band_pct": 3.9,
   "apr_pct_at_10000": 10.57
  }
 ],
 "pool_band_capital_usd": 199321,
 "full_range_capital_usd": 204731054,
 "passive_fees_usd": 144.42,
 "volume_usd": 288831,
 "swaps": 53,
 "annualisation_factor": 8733.8,
 "n_takers": 39,
 "top_taker": "0x5b43453fce04b92e190f391a83136bfbecedefd1",
 "top_taker_share": 0.1384,
 "taker_herfindahl": 0.0716,
 "apr_band_1pct_as_reported": 1.241,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 6.899,
   "divergence_bps_window": 4.873,
   "net_bps_window": 2.027,
   "over_benchmark_usd": 2.03,
   "annualised_net_apr_pct": 177.02
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 5.793,
   "divergence_bps_window": 4.873,
   "net_bps_window": 0.92,
   "over_benchmark_usd": 4.6,
   "annualised_net_apr_pct": 80.34
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 3.214,
   "divergence_bps_window": 4.873,
   "net_bps_window": -1.658,
   "over_benchmark_usd": -41.46,
   "annualised_net_apr_pct": -144.85
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 1.204,
   "divergence_bps_window": 4.873,
   "net_bps_window": -3.668,
   "over_benchmark_usd": -366.84,
   "annualised_net_apr_pct": -320.39
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 80.34%, $40,175 per year, no — nets 80.34% a year at $50,000 in a ±0.195% band, before any view on holding the pair

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
  "Aave v3": 131566889,
  "SparkLend": 308257558
 },
 "utilisation": {
  "Aave v3": 0.868,
  "SparkLend": 0.677
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 7088420,
  "apr_at_size_pct": 2.762,
  "over_low_venue_usd_per_year": 21470
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

Economics: net APR 0.30%, $21,470 per year, GO — clears gas, impact and competition at this size

### [info] Aave v3 USDtb pays 8.07% against the Sky savings rate at 3.60%; best size $227.4k earns $5.4k a year over it [one-block read, de-spiking unavailable]

```json
{
 "venue": "Aave v3",
 "asset": "USDtb",
 "supply_apr_spot_pct": 8.071,
 "supply_apr_window_median_pct": null,
 "spiked": false,
 "despike_unavailable": true,
 "benchmark": "Sky savings rate",
 "benchmark_pct": 3.6,
 "gap_pp": 4.471,
 "supplied_usd": 15445467,
 "borrowed_usd": 12859232,
 "available_usd": 2586235,
 "utilisation": 0.8326,
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
   "marginal_apr_pct": 7.147,
   "over_benchmark_usd_per_year": 3547
  },
  {
   "size_usd": 1000000.0,
   "marginal_apr_pct": 2.446,
   "over_benchmark_usd_per_year": -11543
  },
  {
   "size_usd": 10000000.0,
   "marginal_apr_pct": 1.022,
   "over_benchmark_usd_per_year": -257843
  },
  {
   "size_usd": 50000000.0,
   "marginal_apr_pct": 0.154,
   "over_benchmark_usd_per_year": -1722785
  }
 ],
 "best": {
  "size_usd": 227373.67544323206,
  "apr": 0.05986002454604566,
  "marginal_apr_pct": 5.986,
  "over_benchmark_usd_per_year": 5425
 },
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 2.39%, $5,425 per year, GO — clears gas, impact and competition at this size

### [info] PT-USDAT-14JAN2027 implies 5.99% fixed for 128 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4ccf6deb3d1895373f604b418ff55d8adae8b846",
 "pt": "0xba96292ee7673e3b546cc90db6d97111cd9a314f",
 "pt_symbol": "PT-USDAT-14JAN2027",
 "implied_apy_pct": 5.992,
 "days_to_maturity": 127.689,
 "pt_to_asset": 0.9798482108268098,
 "underlying": "USDAT",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 2.392,
 "classification": "credit spread",
 "pt_depth_units": 1512385,
 "pt_depth_usd": 1481908,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 1.19%, $3,723 per year, GO — clears gas, impact and competition at this size

### [info] PT-APXUSD-5NOV2026 implies 9.30% fixed for 58 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xaf0349fb9b1ba07d34381870c59b560b31412660",
 "pt": "0xaf687b5ecb525ccea96115088999b4ed80c388b6",
 "pt_symbol": "PT-APXUSD-5NOV2026",
 "implied_apy_pct": 9.303,
 "days_to_maturity": 57.689,
 "pt_to_asset": 0.9860396956094067,
 "underlying": "APXUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 5.703,
 "classification": "credit spread",
 "pt_depth_units": 389381,
 "pt_depth_usd": 383945,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 2.84%, $2,478 per year, GO — clears gas, impact and competition at this size

### [info] PT-SUSDD-26NOV2026 implies 5.15% fixed for 79 days against the Sky savings rate (as the risk-free dollar) at 3.60% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0xbeab098b510f758cd35122ee345957b8eccbb322",
 "pt": "0x459bcab2490843ad1fe1e4feff7f7ea16a14408b",
 "pt_symbol": "PT-SUSDD-26NOV2026",
 "implied_apy_pct": 5.15,
 "days_to_maturity": 78.689,
 "pt_to_asset": 0.9892329043099232,
 "underlying": "SUSDD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.6,
 "gap_pp": 1.55,
 "classification": "credit spread",
 "pt_depth_units": 1821479,
 "pt_depth_usd": 1801867,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 0.77%, $1,168 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $29 of $2015 pool fees (1.43%) across 23 episodes by 8 operator(s)

```json
{
 "episodes": 23,
 "fee_taken_usd": 28.78,
 "pool_fees_usd": 2015.42,
 "share_of_fees": 0.0143,
 "swap_usd_bracketed": 153146,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 9,
   "fee_taken_usd": 1.43
  },
  {
   "sender": "0x654fae4aa229d104cabead47e56703f58b174be4",
   "episodes": 5,
   "fee_taken_usd": 0.06
  },
  {
   "sender": "0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de",
   "episodes": 4,
   "fee_taken_usd": 26.61
  },
  {
   "sender": "0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2",
   "episodes": 1,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0x43370108f30ee5ed54a9565f37af3be8502903f5",
   "episodes": 1,
   "fee_taken_usd": 0.0
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR 0.00%, $10,123 per year, GO — clears gas, impact and competition at this size

### [info] 27 poisoning attempt(s) from 22 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0x95b91f0dfc7ad40b382d4c1ad85df0d4e121a67f420ccc2c47202b5802009228",
   "big_eth": 3961.0,
   "victim": "0x5a52e96bacdabb82fd05763e25335261b270efcb",
   "impersonated": "0x835678a611b28684005a5e2233695fb6cbbb0007",
   "attacker": "0x835eba92a1316dbeb8d055087479dcf72a3b0007",
   "dust_tx": "0xb5c3daf767aeaaf51a993c51cbc6455f4feb5da21591d5d0a0a5a06a02e29568",
   "seconds_after": 168
  },
  {
   "big_tx": "0x95b91f0dfc7ad40b382d4c1ad85df0d4e121a67f420ccc2c47202b5802009228",
   "big_eth": 3961.0,
   "victim": "0x835678a611b28684005a5e2233695fb6cbbb0007",
   "impersonated": "0x5a52e96bacdabb82fd05763e25335261b270efcb",
   "attacker": "0x5a5294faeff0de0cae7a4244dbfcb4097eedefcb",
   "dust_tx": "0x150a7a97da5fd73660ef2e354178f12c0791ddf3f50e5c019876ae4b95a304ec",
   "seconds_after": 240
  },
  {
   "big_tx": "0x95b91f0dfc7ad40b382d4c1ad85df0d4e121a67f420ccc2c47202b5802009228",
   "big_eth": 3961.0,
   "victim": "0x835678a611b28684005a5e2233695fb6cbbb0007",
   "impersonated": "0x5a52e96bacdabb82fd05763e25335261b270efcb",
   "attacker": "0x5a522e2a994cc9fd763d73ddf4d7a4e47bfcefcb",
   "dust_tx": "0xb140487eabb2d1ac676a90ed80a4059a7a26dbf8759ce453901ef2d6b76a2f2f",
   "seconds_after": 324
  },
  {
   "big_tx": "0xe828c5925aaf493a62d8321745622457a7ef354897f24bc9b523891fc9123308",
   "big_eth": 2320.0,
   "victim": "0xd496836babbea4bd4fb0c9e152c9622757364ad7",
   "impersonated": "0x843213e106387dbfaf4c1a69c85f49d36666a395",
   "attacker": "0x8432e382eb5495de53460535fe06891d3a2da395",
   "dust_tx": "0x9a09e4b687b38b84044964e8fe643ce600a59674ae13a46000b337b254ec3e8b",
   "seconds_after": 480
  },
  {
   "big_tx": "0xe828c5925aaf493a62d8321745622457a7ef354897f24bc9b523891fc9123308",
   "big_eth": 2320.0,
   "victim": "0xd496836babbea4bd4fb0c9e152c9622757364ad7",
   "impersonated": "0x843213e106387dbfaf4c1a69c85f49d36666a395",
   "attacker": "0x8432e3c9299a7d6476ed3ad34201b9fc2436a395",
   "dust_tx": "0x051c7668ea011d0187be4073505fd26f154c29cab51ff265fbc8de1e522e64f5",
   "seconds_after": 1032
  },
  {
   "big_tx": "0xe828c5925aaf493a62d8321745622457a7ef354897f24bc9b523891fc9123308",
   "big_eth": 2320.0,
   "victim": "0xd496836babbea4bd4fb0c9e152c9622757364ad7",
   "impersonated": "0x843213e106387dbfaf4c1a69c85f49d36666a395",
   "attacker": "0x8432e382eb5495de53460535fe06891d3a2da395",
   "dust_tx": "0xa2ed7d3441f72311e3c78047b832d6234e1ff
```

### [info] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDT to 1,992 recipients in 30 txs (73 per tx)

```json
{
 "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "token_symbol": "USDT",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 2203,
 "recipients": 1992,
 "txs": 30,
 "blocks": 30,
 "transfers_per_tx": 73.4,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "284",
 "uniform_amount_share": 0.003,
 "usd_median": 0.00028395937948,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] mint distribution: zero address (mint/burn) (known- sent 0x06450dee to 1,670 recipients in 10 txs (333 per tx)

```json
{
 "token": "0x06450dee7fd2fb8e39061434babcfc05599a6fb8",
 "token_symbol": null,
 "sender": "0x0000000000000000000000000000000000000000",
 "sender_label": "zero address (mint/burn) (known-canonical)",
 "kind": "mint distribution",
 "transfers": 3334,
 "recipients": 1670,
 "txs": 10,
 "blocks": 10,
 "transfers_per_tx": 333.4,
 "carrier_contract": "0x0de8bf93da2f7eecb3d9169422413a9bef4ef628",
 "carrier_label": null,
 "carrier_share": 0.537,
 "median_raw_amount": "17577216000000000000000000",
 "uniform_amount_share": 0.04,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

