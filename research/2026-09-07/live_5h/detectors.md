# Detector sweep — research/2026-09-07/live_5h

Ran 10 detector(s); 37 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 3.05 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `dollar_rate_outlier` | 1 | 2.98 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `gas_concentration` | 1 | 3.09 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `lp_marginal_yield` | 10 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 5 | 4.96 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 0 | 3.31 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 1 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 12 | 3.23 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

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

### [notable] uniswap_v3 USDe/USDC: $250.0k in a ±0.01% band earns 0.5bp of fees less 0.0bp of divergence over 5.0h (9.1% a year if it repeats)

```json
{
 "pool": "0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a",
 "venue": "uniswap_v3",
 "pair": "USDe/USDC",
 "stable_pair": true,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.011,
 "band_quoted_pct": 0.011,
 "concentration_multiplier": 18183.3,
 "band_ladder": [
  {
   "band_pct": 0.011,
   "apr_pct_at_10000": 12.91
  },
  {
   "band_pct": 0.022,
   "apr_pct_at_10000": 6.52
  },
  {
   "band_pct": 0.055,
   "apr_pct_at_10000": 2.62
  },
  {
   "band_pct": 0.22,
   "apr_pct_at_10000": 0.66
  }
 ],
 "pool_band_capital_usd": 554287,
 "full_range_capital_usd": 10078768497,
 "passive_fees_usd": 41.62,
 "volume_usd": 449296,
 "swaps": 43,
 "annualisation_factor": 1750.9,
 "n_takers": 17,
 "top_taker": "0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd",
 "top_taker_share": 0.697,
 "taker_herfindahl": 0.5018,
 "apr_band_1pct_as_reported": 0.0015,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.738,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.738,
   "over_benchmark_usd": 0.53,
   "annualised_net_apr_pct": 12.91
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.689,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.689,
   "over_benchmark_usd": 2.42,
   "annualised_net_apr_pct": 12.06
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.517,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.517,
   "over_benchmark_usd": 7.8,
   "annualised_net_apr_pct": 9.06
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.268,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.268,
   "over_benchmark_usd": 6.22,
   "annualised_net_apr_pct": 4.69
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 9.06%, $13,657 per year, GO — nets 9.06% a year at $250,000 in a ±0.011% band against a 3.60% savings rate

### [notable] uniswap_v3 USDC/USDT: $1.0M in a ±0.01% band earns 0.3bp of fees less 0.0bp of divergence over 5.0h (4.5% a year if it repeats)

```json
{
 "pool": "0x3416cf6c708da44db2624d63ea0aaef7113527c6",
 "venue": "uniswap_v3",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.004,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 7.43
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 7.43
  },
  {
   "band_pct": 0.02,
   "apr_pct_at_10000": 3.72
  },
  {
   "band_pct": 0.08,
   "apr_pct_at_10000": 0.93
  }
 ],
 "pool_band_capital_usd": 1554763,
 "full_range_capital_usd": 31097589308,
 "passive_fees_usd": 66.36,
 "volume_usd": 665228,
 "swaps": 259,
 "annualisation_factor": 1750.9,
 "n_takers": 176,
 "top_taker": "0x5aca530c36b8f4605786c485796e80a66ef42830",
 "top_taker_share": 0.1727,
 "taker_herfindahl": 0.0689,
 "apr_band_1pct_as_reported": 0.0008,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.424,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.424,
   "over_benchmark_usd": 0.22,
   "annualised_net_apr_pct": 7.43
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.414,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.414,
   "over_benchmark_usd": 1.04,
   "annualised_net_apr_pct": 7.24
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.368,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.368,
   "over_benchmark_usd": 4.05,
   "annualised_net_apr_pct": 6.44
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.26,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.26,
   "over_benchmark_usd": 5.41,
   "annualised_net_apr_pct": 4.55
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 4.55%, $9,473 per year, GO — nets 4.55% a year at $1,000,000 in a ±0.010% band against a 3.60% savings rate

### [notable] uniswap_v4 USDC/USDG: $250.0k in a ±0.01% band earns 0.3bp of fees less 0.0bp of divergence over 5.0h (6.1% a year if it repeats)

```json
{
 "pool": "0xb90d11907f96a9d5fd8979ef271d3bb9b90052d9299d1f95faa5168c55bcb716",
 "venue": "uniswap_v4",
 "pair": "USDC/USDG",
 "stable_pair": true,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.006,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 7.54
  },
  {
   "band_pct": 0.012,
   "apr_pct_at_10000": 6.29
  },
  {
   "band_pct": 0.03,
   "apr_pct_at_10000": 2.53
  },
  {
   "band_pct": 0.12,
   "apr_pct_at_10000": 0.63
  }
 ],
 "pool_band_capital_usd": 1033361,
 "full_range_capital_usd": 20668770435,
 "passive_fees_usd": 44.9,
 "volume_usd": 547574,
 "swaps": 43,
 "annualisation_factor": 1750.9,
 "n_takers": 38,
 "top_taker": "0x2156f29d64f81701b58877129006e8b1964149b6",
 "top_taker_share": 0.1918,
 "taker_herfindahl": 0.0886,
 "apr_band_1pct_as_reported": 0.0008,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.43,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.43,
   "over_benchmark_usd": 0.22,
   "annualised_net_apr_pct": 7.54
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.414,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.414,
   "over_benchmark_usd": 1.04,
   "annualised_net_apr_pct": 7.26
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.35,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.35,
   "over_benchmark_usd": 3.61,
   "annualised_net_apr_pct": 6.13
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.221,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.221,
   "over_benchmark_usd": 1.52,
   "annualised_net_apr_pct": 3.87
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 6.13%, $6,321 per year, GO — nets 6.13% a year at $250,000 in a ±0.010% band against a 3.60% savings rate

### [notable] uniswap_v4 USDe/USDC: $250.0k in a ±0.02% band earns 0.3bp of fees less 0.0bp of divergence over 5.0h (4.7% a year if it repeats)

```json
{
 "pool": "0x56fc29b86900aa0afa6e20b020429bffba1105cfb45070492c67529b46eb48c1",
 "venue": "uniswap_v4",
 "pair": "USDe/USDC",
 "stable_pair": true,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.019,
 "band_quoted_pct": 0.019,
 "concentration_multiplier": 10527.8,
 "band_ladder": [
  {
   "band_pct": 0.019,
   "apr_pct_at_10000": 5.8
  },
  {
   "band_pct": 0.038,
   "apr_pct_at_10000": 2.92
  },
  {
   "band_pct": 0.095,
   "apr_pct_at_10000": 1.17
  },
  {
   "band_pct": 0.38,
   "apr_pct_at_10000": 0.29
  }
 ],
 "pool_band_capital_usd": 995028,
 "full_range_capital_usd": 10475467536,
 "passive_fees_usd": 33.31,
 "volume_usd": 1074418,
 "swaps": 67,
 "annualisation_factor": 1750.9,
 "n_takers": 41,
 "top_taker": "0x6cc60a0b57bc882a0471980d0e2d4ad7ddf3c4bd",
 "top_taker_share": 0.4324,
 "taker_herfindahl": 0.2273,
 "apr_band_1pct_as_reported": 0.0011,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.331,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.331,
   "over_benchmark_usd": 0.13,
   "annualised_net_apr_pct": 5.8
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.319,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.319,
   "over_benchmark_usd": 0.57,
   "annualised_net_apr_pct": 5.58
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.268,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.268,
   "over_benchmark_usd": 1.55,
   "annualised_net_apr_pct": 4.68
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.167,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.167,
   "over_benchmark_usd": -3.86,
   "annualised_net_apr_pct": 2.92
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 4.68%, $2,714 per year, GO — nets 4.68% a year at $250,000 in a ±0.019% band against a 3.60% savings rate

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

### [info] uniswap_v4 AP/USDC: $10.0k in a ±1690.53% band earns 15685.3bp of fees less 7232.8bp of divergence over 5.0h (147998.5% a year if it repeats)

```json
{
 "pool": "0x8559fbcaad88ee1a367d3d6a0dc5f1a73ec134952aa04555ede1157e9d6d0841",
 "venue": "uniswap_v4",
 "pair": "AP/USDC",
 "stable_pair": false,
 "window_hours": 5.003,
 "observed_price_range_pct": 1690.528,
 "band_quoted_pct": 1690.528,
 "concentration_multiplier": 1.3,
 "band_ladder": [
  {
   "band_pct": 1690.528,
   "apr_pct_at_10000": 147998.49
  },
  {
   "band_pct": 3381.056,
   "apr_pct_at_10000": 143007.85
  },
  {
   "band_pct": 8452.64,
   "apr_pct_at_10000": 138487.72
  },
  {
   "band_pct": 33810.56,
   "apr_pct_at_10000": 134622.69
  }
 ],
 "pool_band_capital_usd": 20176,
 "full_range_capital_usd": 26419,
 "passive_fees_usd": 47331.15,
 "volume_usd": 313763,
 "swaps": 1079,
 "annualisation_factor": 1750.9,
 "n_takers": 191,
 "top_taker": "0x331d9a049d496385998067abf6cbb6371c8d2466",
 "top_taker_share": 0.0842,
 "taker_herfindahl": 0.0345,
 "apr_band_1pct_as_reported": 632042.2211,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 15685.274,
   "divergence_bps_window": 7232.803,
   "net_bps_window": 8452.471,
   "over_benchmark_usd": 8452.47,
   "annualised_net_apr_pct": 147998.49
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 6744.68,
   "divergence_bps_window": 7232.803,
   "net_bps_window": -488.123,
   "over_benchmark_usd": -2440.62,
   "annualised_net_apr_pct": -8546.79
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 1751.867,
   "divergence_bps_window": 7232.803,
   "net_bps_window": -5480.937,
   "over_benchmark_usd": -137023.41,
   "annualised_net_apr_pct": -95968.43
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 463.951,
   "divergence_bps_window": 7232.803,
   "net_bps_window": -6768.852,
   "over_benchmark_usd": -676885.21,
   "annualised_net_apr_pct": -118519.18
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 147998.49%, $14,799,848 per year, no — nets 147998.49% a year at $10,000 in a ±1690.528% band, before any view on holding the pair

### [info] uniswap_v4 NVDAon/USDC: $250.0k in a ±2.49% band earns 181.8bp of fees less 61.9bp of divergence over 5.0h (2099.2% a year if it repeats)

```json
{
 "pool": "0xff145fd4d52ebd0e758393740aea7eb6228569285b348176c1cdfc5363793b72",
 "venue": "uniswap_v4",
 "pair": "NVDAon/USDC",
 "stable_pair": false,
 "window_hours": 5.003,
 "observed_price_range_pct": 2.492,
 "band_quoted_pct": 2.492,
 "concentration_multiplier": 81.8,
 "band_ladder": [
  {
   "band_pct": 2.492,
   "apr_pct_at_10000": 12827.3
  },
  {
   "band_pct": 4.984,
   "apr_pct_at_10000": 7054.96
  },
  {
   "band_pct": 12.46,
   "apr_pct_at_10000": 3121.49
  },
  {
   "band_pct": 49.84,
   "apr_pct_at_10000": 997.24
  }
 ],
 "pool_band_capital_usd": 61214,
 "full_range_capital_usd": 5004451,
 "passive_fees_usd": 5657.95,
 "volume_usd": 566304,
 "swaps": 1206,
 "annualisation_factor": 1750.9,
 "n_takers": 447,
 "top_taker": "0xaa936257cd7689d3f04336389dc951c0b439a64f",
 "top_taker_share": 0.0516,
 "taker_herfindahl": 0.0134,
 "apr_band_1pct_as_reported": 398.8592,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 794.503,
   "divergence_bps_window": 61.912,
   "net_bps_window": 732.591,
   "over_benchmark_usd": 732.59,
   "annualised_net_apr_pct": 12827.3
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 508.746,
   "divergence_bps_window": 61.912,
   "net_bps_window": 446.834,
   "over_benchmark_usd": 2234.17,
   "annualised_net_apr_pct": 7823.83
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 181.803,
   "divergence_bps_window": 61.912,
   "net_bps_window": 119.891,
   "over_benchmark_usd": 2997.27,
   "annualised_net_apr_pct": 2099.23
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 53.316,
   "divergence_bps_window": 61.912,
   "net_bps_window": -8.596,
   "over_benchmark_usd": -859.61,
   "annualised_net_apr_pct": -150.51
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 2099.23%, $5,248,068 per year, no — nets 2099.23% a year at $250,000 in a ±2.492% band, before any view on holding the pair

### [info] uniswap_v3 0x3c3a…f354/USDe: $1.0M in a ±0.01% band earns 12.7bp of fees less 0.0bp of divergence over 5.0h (222.7% a year if it repeats)

```json
{
 "pool": "0x9aac67deef711d438ad711ae495b8cb43a6ee1a8",
 "venue": "uniswap_v3",
 "pair": "0x3c3a\u2026f354/USDe",
 "stable_pair": false,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 20818.66
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 20818.66
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 20818.66
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 20818.66
  }
 ],
 "pool_band_capital_usd": 705,
 "full_range_capital_usd": 14108312,
 "passive_fees_usd": 1272.86,
 "volume_usd": 424288,
 "swaps": 195,
 "annualisation_factor": 1750.9,
 "n_takers": 69,
 "top_taker": "0xf1c270e675a1da57aee8ac6d4f1236e226648234",
 "top_taker_share": 0.0993,
 "taker_herfindahl": 0.0413,
 "apr_band_1pct_as_reported": 31.8291,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1188.993,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1188.993,
   "over_benchmark_usd": 1188.99,
   "annualised_net_apr_pct": 20818.66
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 251.031,
   "divergence_bps_window": 0.0,
   "net_bps_window": 251.031,
   "over_benchmark_usd": 1255.15,
   "annualised_net_apr_pct": 4395.42
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 50.771,
   "divergence_bps_window": 0.0,
   "net_bps_window": 50.771,
   "over_benchmark_usd": 1269.28,
   "annualised_net_apr_pct": 888.98
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 12.72,
   "divergence_bps_window": 0.0,
   "net_bps_window": 12.72,
   "over_benchmark_usd": 1271.96,
   "annualised_net_apr_pct": 222.71
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 222.71%, $2,227,138 per year, no — nets 222.71% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

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

### [info] uniswap_v3 0x00f3…8917/WETH: $1.0M in a ±0.01% band earns 1.9bp of fees less 0.0bp of divergence over 5.0h (33.2% a year if it repeats)

```json
{
 "pool": "0x4068038ab5490063a3ead93b3712ed082e62bd59",
 "venue": "uniswap_v3",
 "pair": "0x00f3\u20268917/WETH",
 "stable_pair": false,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.0,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3276.41
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3276.41
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3276.41
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 3276.41
  }
 ],
 "pool_band_capital_usd": 124,
 "full_range_capital_usd": 2478080,
 "passive_fees_usd": 189.44,
 "volume_usd": 379939,
 "swaps": 498,
 "annualisation_factor": 1750.9,
 "n_takers": 55,
 "top_taker": "0x3e10ab3b27129eebf0c06b7f8ed5c47119416977",
 "top_taker_share": 0.3751,
 "taker_herfindahl": 0.1854,
 "apr_band_1pct_as_reported": 26.9689,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 187.122,
   "divergence_bps_window": 0.0,
   "net_bps_window": 187.122,
   "over_benchmark_usd": 187.12,
   "annualised_net_apr_pct": 3276.41
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 37.794,
   "divergence_bps_window": 0.0,
   "net_bps_window": 37.794,
   "over_benchmark_usd": 188.97,
   "annualised_net_apr_pct": 661.76
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 7.574,
   "divergence_bps_window": 0.0,
   "net_bps_window": 7.574,
   "over_benchmark_usd": 189.35,
   "annualised_net_apr_pct": 132.61
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 1.894,
   "divergence_bps_window": 0.0,
   "net_bps_window": 1.894,
   "over_benchmark_usd": 189.42,
   "annualised_net_apr_pct": 33.17
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 33.17%, $331,665 per year, no — nets 33.17% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

### [info] rETH trades 17.7bp below NAV, 12.7bp after the 5.0bp round trip; burn into the Rocket Pool deposit pool, which is empty most of the time — conditional, so the exit may not be there when you want it

```json
{
 "asset": "rETH",
 "nav_source": "0xae78736c getExchangeRate()",
 "nav": 2909.45091,
 "market_vw_price": 2904.298196,
 "market_median": 2904.156629,
 "market_p10": 2903.378049,
 "discount_bps": 17.71,
 "traded_volume_usd": 361204,
 "implied_daily_volume_usd": 1732740,
 "refills_needed_per_year": 365,
 "swaps": 28,
 "venues": {
  "uniswap_v3": 15,
  "uniswap_v4": 7,
  "curve": 6
 },
 "redemption": {
  "days": 1.0,
  "atomic": false,
  "availability": "conditional",
  "exit_bps": 5.0,
  "path": "burn into the Rocket Pool deposit pool, which is empty most of the time"
 },
 "net_edge_bps": 12.71,
 "why": "the protocol pays NAV and the market paid less; the gap closes when you redeem, and the wait is the reason a bot cannot take it from you"
}
```

Economics: net APR 46.38%, $167,541 per year, GO — clears gas, impact and competition at this size

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

### [info] uniswap_v4 ETH/USDC: $250.0k in a ±0.05% band earns 2.6bp of fees less 1.3bp of divergence over 5.0h (23.9% a year if it repeats)

```json
{
 "pool": "0xb2b92b56988a4edbe255989792c6ea239b25eaf66b42093145cbf8f630db3a17",
 "venue": "uniswap_v4",
 "pair": "ETH/USDC",
 "stable_pair": false,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.051,
 "band_quoted_pct": 0.051,
 "concentration_multiplier": 3923.1,
 "band_ladder": [
  {
   "band_pct": 0.051,
   "apr_pct_at_10000": 73.39
  },
  {
   "band_pct": 0.102,
   "apr_pct_at_10000": 37.8
  },
  {
   "band_pct": 0.255,
   "apr_pct_at_10000": 15.41
  },
  {
   "band_pct": 1.02,
   "apr_pct_at_10000": 3.91
  }
 ],
 "pool_band_capital_usd": 214258,
 "full_range_capital_usd": 840547791,
 "passive_fees_usd": 122.58,
 "volume_usd": 323422,
 "swaps": 82,
 "annualisation_factor": 1750.9,
 "n_takers": 47,
 "top_taker": "0x95480d3f27658e73b2785d30beb0c847d78294c7",
 "top_taker_share": 0.2545,
 "taker_herfindahl": 0.1278,
 "apr_band_1pct_as_reported": 0.0514,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 5.466,
   "divergence_bps_window": 1.275,
   "net_bps_window": 4.191,
   "over_benchmark_usd": 4.19,
   "annualised_net_apr_pct": 73.39
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 4.639,
   "divergence_bps_window": 1.275,
   "net_bps_window": 3.364,
   "over_benchmark_usd": 16.82,
   "annualised_net_apr_pct": 58.9
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 2.64,
   "divergence_bps_window": 1.275,
   "net_bps_window": 1.366,
   "over_benchmark_usd": 34.14,
   "annualised_net_apr_pct": 23.91
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 1.01,
   "divergence_bps_window": 1.275,
   "net_bps_window": -0.265,
   "over_benchmark_usd": -26.53,
   "annualised_net_apr_pct": -4.65
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 23.91%, $59,777 per year, no — nets 23.91% a year at $250,000 in a ±0.051% band, before any view on holding the pair

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

### [info] uniswap_v3 wstETH/WETH: $1.0M in a ±0.01% band earns 0.2bp of fees less 0.0bp of divergence over 5.0h (2.8% a year if it repeats)

```json
{
 "pool": "0x109830a1aaad605bbf02a9dfa7b0b92ec2fb7daa",
 "venue": "uniswap_v3",
 "pair": "wstETH/WETH",
 "stable_pair": false,
 "window_hours": 5.003,
 "observed_price_range_pct": 0.003,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 4.78
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 4.78
  },
  {
   "band_pct": 0.015,
   "apr_pct_at_10000": 3.2
  },
  {
   "band_pct": 0.06,
   "apr_pct_at_10000": 0.8
  }
 ],
 "pool_band_capital_usd": 1533918,
 "full_range_capital_usd": 30680670454,
 "passive_fees_usd": 45.64,
 "volume_usd": 456358,
 "swaps": 88,
 "annualisation_factor": 1750.9,
 "n_takers": 69,
 "top_taker": "0x5c3593481cba011737e36ded62f1797c9f6afce1",
 "top_taker_share": 0.5666,
 "taker_herfindahl": 0.3507,
 "apr_band_1pct_as_reported": 0.0005,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.296,
   "divergence_bps_window": 0.023,
   "net_bps_window": 0.273,
   "over_benchmark_usd": 0.27,
   "annualised_net_apr_pct": 4.78
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.288,
   "divergence_bps_window": 0.023,
   "net_bps_window": 0.266,
   "over_benchmark_usd": 1.33,
   "annualised_net_apr_pct": 4.65
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.256,
   "divergence_bps_window": 0.023,
   "net_bps_window": 0.233,
   "over_benchmark_usd": 5.83,
   "annualised_net_apr_pct": 4.09
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.18,
   "divergence_bps_window": 0.023,
   "net_bps_window": 0.158,
   "over_benchmark_usd": 15.76,
   "annualised_net_apr_pct": 2.76
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 2.76%, $27,595 per year, no — nets 2.76% a year at $1,000,000 in a ±0.010% band, before any view on holding the pair

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

