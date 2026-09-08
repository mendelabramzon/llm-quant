# Detector sweep — research/2026-09-08/live_2h

Ran 10 detector(s); 28 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 1.26 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `dollar_rate_outlier` | 2 | 1.23 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `gas_concentration` | 0 | 0.00 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `lp_marginal_yield` | 8 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 4 | 1.91 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 0 | 1.40 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 1 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 6 | 1.31 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

### [high] Aave v3 USDC is fully utilised: $12.0k of exit liquidity on a $2.2B reserve

```json
{
 "venue": "Aave v3",
 "asset": "USDC",
 "supplied_usd": 2156271448,
 "borrowed_usd": 2156259491,
 "available_usd": 11957,
 "utilisation": 0.999994,
 "supply_apr_pct": 12.866,
 "borrow_apr_pct": 14.296,
 "why": "nobody can withdraw from this reserve until a borrower repays or a supplier arrives; any strategy whose exit leg is this reserve is blocked, and the high rate it prints is the symptom rather than an opportunity"
}
```

### [notable] unlabelled atomic bot pair 0x04ca7a7e passed $480.2M through in 7 txs (100% ended flat, 4 counterparties)

```json
{
 "address": "0x04ca7a7e602335a261b63128e89d43b6fe1e2c87",
 "shape": "pass-through",
 "gross_usd": 480220219,
 "txs": 7,
 "counterparties": 4,
 "tokens": 2,
 "pass_through_share": 1.0,
 "received_usd": 240126723,
 "sent_usd": 240093496,
 "retained_usd": 33228,
 "retention": 0.0001,
 "is_contract": true,
 "emits_logs": true,
 "receives_calldata": false,
 "originates_txs": false,
 "vanity_zeros": 1,
 "suggested_kind": "atomic bot pair",
 "why": "value arrives and leaves inside the same transaction, so this address holds nothing and its flow is not exchange flow; no vanity prefix, so the shape is the only claim",
 "next_step": "labels.py resolve --out <window> tries to name it; unnamed, it still must not be counted as an exchange"
}
```

### [notable] unlabelled atomic bot pair 0x26de7861 passed $480.0M through in 7 txs (100% ended flat, 1 counterparties)

```json
{
 "address": "0x26de7861e213a5351f6ed767d00e0839930e9ee1",
 "shape": "pass-through",
 "gross_usd": 480000002,
 "txs": 7,
 "counterparties": 1,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 240000001,
 "sent_usd": 240000001,
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

### [notable] unlabelled venue 0xd8246178 passed $138.6M through in 808 txs (100% ended flat, 6 counterparties)

```json
{
 "address": "0xd82461784eb72d4b67cbab077989eb215315e272",
 "shape": "pass-through",
 "gross_usd": 138576380,
 "txs": 808,
 "counterparties": 6,
 "tokens": 3,
 "pass_through_share": 1.0,
 "received_usd": 69288190,
 "sent_usd": 69288190,
 "retained_usd": 0,
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
  "Aave v3": 11187698,
  "SparkLend": 748016681,
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

Economics: net APR 3.48%, $34,758,805 per year, GO — clears gas, impact and competition at this size

### [notable] USDT pays 0.98pp more on Aave v3 than SparkLend; best size $242.8M earns $1.1M a year over SparkLend

```json
{
 "asset": "USDT",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.604,
  "SparkLend": 2.619,
  "Compound v3 USDT": 3.002
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.603
 },
 "gap_pp_spot": 0.985,
 "gap_pp_despiked": 0.984,
 "head_read_spiked": false,
 "despiked": true,
 "despike_note": "median of the window log series",
 "supplied_usd": {
  "Aave v3": 2962871489,
  "SparkLend": 391764710,
  "Compound v3 USDT": 185305997
 },
 "utilisation": {
  "Aave v3": 0.936,
  "SparkLend": 0.828,
  "Compound v3 USDT": 0.834
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 242777901,
  "apr_at_size_pct": 3.079,
  "over_low_venue_usd_per_year": 1116507
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.603
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.601
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.592
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.544
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 3.372
  }
 ]
}
```

Economics: net APR 0.46%, $1,116,507 per year, GO — clears gas, impact and competition at this size

### [notable] sUSDe trades 7.1bp below NAV, 4.4bp after the 2.7bp round trip; cooldownShares, then unstake after cooldownDuration (1 day)

```json
{
 "asset": "sUSDe",
 "nav_source": "0x9d39a5de convertToAssets(uint256)",
 "nav": 1.247001,
 "market_vw_price": 1.24611,
 "market_median": 1.246198,
 "market_p10": 1.245819,
 "discount_bps": 7.14,
 "traded_volume_usd": 972880,
 "implied_daily_volume_usd": 11657074,
 "refills_needed_per_year": 365,
 "swaps": 21,
 "venues": {
  "uniswap_v4": 18,
  "curve": 3
 },
 "redemption": {
  "days": 1.0,
  "atomic": false,
  "availability": "always",
  "exit_bps": 2.7,
  "path": "cooldownShares, then unstake after cooldownDuration (1 day)"
 },
 "net_edge_bps": 4.44,
 "why": "the protocol pays NAV and the market paid less; the gap closes when you redeem, and the wait is the reason a bot cannot take it from you"
}
```

Economics: net APR 16.21%, $157,656 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v4 USDe/USDC: $1.0M in a ±0.01% band earns 0.3bp of fees less 0.0bp of divergence over 2.0h (12.7% a year if it repeats)

```json
{
 "pool": "0x56fc29b86900aa0afa6e20b020429bffba1105cfb45070492c67529b46eb48c1",
 "venue": "uniswap_v4",
 "pair": "USDe/USDC",
 "stable_pair": true,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.009,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 27.51
  },
  {
   "band_pct": 0.018,
   "apr_pct_at_10000": 15.36
  },
  {
   "band_pct": 0.045,
   "apr_pct_at_10000": 6.17
  },
  {
   "band_pct": 0.18,
   "apr_pct_at_10000": 1.55
  }
 ],
 "pool_band_capital_usd": 832853,
 "full_range_capital_usd": 16658315965,
 "passive_fees_usd": 53.01,
 "volume_usd": 1710011,
 "swaps": 39,
 "annualisation_factor": 4373.4,
 "n_takers": 19,
 "top_taker": "0x515cc41a9b9a0e040082d027b72230ecdf0b41a1",
 "top_taker_share": 0.3002,
 "taker_herfindahl": 0.218,
 "apr_band_1pct_as_reported": 0.0028,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.629,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.629,
   "over_benchmark_usd": 0.55,
   "annualised_net_apr_pct": 27.51
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.6,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.6,
   "over_benchmark_usd": 2.59,
   "annualised_net_apr_pct": 26.26
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.49,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.49,
   "over_benchmark_usd": 10.18,
   "annualised_net_apr_pct": 21.41
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.289,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.289,
   "over_benchmark_usd": 20.69,
   "annualised_net_apr_pct": 12.65
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 12.65%, $90,486 per year, GO — nets 12.65% a year at $1,000,000 in a ±0.010% band against a 3.60% savings rate

### [notable] USDC pays 2.15pp more on Compound v3 USDC than SparkLend; best size $1.4M earns $15k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 12.866,
  "SparkLend": 3.542,
  "Compound v3 USDC": 5.69,
  "Sky SSR": 3.6
 },
 "supply_apr_median_pct": {
  "Aave v3": 3.593
 },
 "gap_pp_spot": 2.148,
 "gap_pp_despiked": 2.148,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2156271448,
  "SparkLend": 25640465,
  "Compound v3 USDC": 374350853,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 1.0,
  "SparkLend": 0.922,
  "Compound v3 USDC": 0.908
 },
 "dilution_basis": "sampled",
 "best_size": {
  "size_usd": 1417172,
  "apr_at_size_pct": 4.596,
  "over_low_venue_usd_per_year": 14934
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 5.612
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 4.917
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.225
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.063
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 2.579
  }
 ]
}
```

Economics: net APR 1.05%, $14,934 per year, GO — clears gas, impact and competition at this size

### [notable] uniswap_v3 USDC/USDT: $250.0k in a ±0.01% band earns 0.1bp of fees less 0.0bp of divergence over 2.0h (4.9% a year if it repeats)

```json
{
 "pool": "0x3416cf6c708da44db2624d63ea0aaef7113527c6",
 "venue": "uniswap_v3",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.002,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 5.32
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 5.32
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 5.32
  },
  {
   "band_pct": 0.04,
   "apr_pct_at_10000": 1.33
  }
 ],
 "pool_band_capital_usd": 2504380,
 "full_range_capital_usd": 50091356757,
 "passive_fees_usd": 30.58,
 "volume_usd": 305765,
 "swaps": 88,
 "annualisation_factor": 4373.4,
 "n_takers": 71,
 "top_taker": "0x81e3add2b2b6ee38558c8c5a347d4f79e7aeb98e",
 "top_taker_share": 0.493,
 "taker_herfindahl": 0.2966,
 "apr_band_1pct_as_reported": 0.0005,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.122,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.122,
   "over_benchmark_usd": 0.04,
   "annualised_net_apr_pct": 5.32
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.12,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.12,
   "over_benchmark_usd": 0.19,
   "annualised_net_apr_pct": 5.24
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.111,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.111,
   "over_benchmark_usd": 0.72,
   "annualised_net_apr_pct": 4.86
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.087,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.087,
   "over_benchmark_usd": 0.49,
   "annualised_net_apr_pct": 3.82
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 4.86%, $3,149 per year, GO — nets 4.86% a year at $250,000 in a ±0.010% band against a 3.60% savings rate

### [notable] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDT to 4,669 recipients in 60 txs (95 per tx)

```json
{
 "token": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "token_symbol": "USDT",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 5692,
 "recipients": 4669,
 "txs": 60,
 "blocks": 60,
 "transfers_per_tx": 94.9,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "264",
 "uniform_amount_share": 0.003,
 "usd_median": 0.00026396224008,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] airdrop or multisend: 0x5eef5946ad78e614bb3ee7b9ed1097 sent 0x5eef5946 to 4,509 recipients in 9 txs (557 per tx)

```json
{
 "token": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "token_symbol": null,
 "sender": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 5010,
 "recipients": 4509,
 "txs": 9,
 "blocks": 9,
 "transfers_per_tx": 556.7,
 "carrier_contract": "0x5eef5946ad78e614bb3ee7b9ed1097c517ae97f7",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "5000000000",
 "uniform_amount_share": 1.0,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [notable] uniswap_v4 USDC/USDT: $10.0k in a ±0.01% band earns 0.1bp of fees less 0.0bp of divergence over 2.0h (2.6% a year if it repeats)

```json
{
 "pool": "0x0fb0e40cec3bb23e13abc585958a93c796fbea56955e19a23727a716a0423239",
 "venue": "uniswap_v4",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.004,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 2.59
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 2.59
  },
  {
   "band_pct": 0.02,
   "apr_pct_at_10000": 1.3
  },
  {
   "band_pct": 0.08,
   "apr_pct_at_10000": 0.32
  }
 ],
 "pool_band_capital_usd": 1997270,
 "full_range_capital_usd": 39948397409,
 "passive_fees_usd": 11.87,
 "volume_usd": 1318883,
 "swaps": 231,
 "annualisation_factor": 4373.4,
 "n_takers": 167,
 "top_taker": "0xae0cc0d6e76c2b13451ab90cd13a5fa71a5c59ba",
 "top_taker_share": 0.2163,
 "taker_herfindahl": 0.0929,
 "apr_band_1pct_as_reported": 0.0003,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.059,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.059,
   "over_benchmark_usd": -0.02,
   "annualised_net_apr_pct": 2.59
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.058,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.058,
   "over_benchmark_usd": -0.12,
   "annualised_net_apr_pct": 2.54
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.053,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.053,
   "over_benchmark_usd": -0.74,
   "annualised_net_apr_pct": 2.31
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.04,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.04,
   "over_benchmark_usd": -4.27,
   "annualised_net_apr_pct": 1.73
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 2.59%, $-87 per year, no — nets 2.59% a year at $10,000 in a ±0.010% band against a 3.60% savings rate

### [notable] uniswap_v4 USDT/USDS: $10.0k in a ±0.01% band earns 0.0bp of fees less 0.0bp of divergence over 2.0h (1.9% a year if it repeats)

```json
{
 "pool": "0x3b1b1f2e775a6db1664f8e7d59ad568605ea2406312c11aef03146c0cf89d5b9",
 "venue": "uniswap_v4",
 "pair": "USDT/USDS",
 "stable_pair": true,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.003,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1.86
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1.86
  },
  {
   "band_pct": 0.015,
   "apr_pct_at_10000": 1.24
  },
  {
   "band_pct": 0.06,
   "apr_pct_at_10000": 0.31
  }
 ],
 "pool_band_capital_usd": 5000963,
 "full_range_capital_usd": 100026769697,
 "passive_fees_usd": 21.36,
 "volume_usd": 3560337,
 "swaps": 78,
 "annualisation_factor": 4373.4,
 "n_takers": 57,
 "top_taker": "0x81e3add2b2b6ee38558c8c5a347d4f79e7aeb98e",
 "top_taker_share": 0.1825,
 "taker_herfindahl": 0.0837,
 "apr_band_1pct_as_reported": 0.0002,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.043,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.043,
   "over_benchmark_usd": -0.04,
   "annualised_net_apr_pct": 1.86
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.042,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.042,
   "over_benchmark_usd": -0.2,
   "annualised_net_apr_pct": 1.85
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.041,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.041,
   "over_benchmark_usd": -1.04,
   "annualised_net_apr_pct": 1.78
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.036,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.036,
   "over_benchmark_usd": -4.67,
   "annualised_net_apr_pct": 1.56
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 1.86%, $-175 per year, no — nets 1.86% a year at $10,000 in a ±0.010% band against a 3.60% savings rate

### [notable] uniswap_v4 USDC/USDT: $10.0k in a ±0.01% band earns 0.0bp of fees less 0.0bp of divergence over 2.0h (1.5% a year if it repeats)

```json
{
 "pool": "0x8aa4e11cbdf30eedc92100f4c8a31ff748e201d44712cc8c90d189edaa8e4e47",
 "venue": "uniswap_v4",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.002,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1.47
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1.47
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 1.47
  },
  {
   "band_pct": 0.04,
   "apr_pct_at_10000": 0.37
  }
 ],
 "pool_band_capital_usd": 904584,
 "full_range_capital_usd": 18093035704,
 "passive_fees_usd": 3.07,
 "volume_usd": 255931,
 "swaps": 40,
 "annualisation_factor": 4373.4,
 "n_takers": 35,
 "top_taker": "0x8b41013f5f0e23f5444d4a7927da0e567f50cdd7",
 "top_taker_share": 0.3023,
 "taker_herfindahl": 0.1681,
 "apr_band_1pct_as_reported": 0.0001,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.034,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.034,
   "over_benchmark_usd": -0.05,
   "annualised_net_apr_pct": 1.47
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.032,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.032,
   "over_benchmark_usd": -0.25,
   "annualised_net_apr_pct": 1.41
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.027,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.027,
   "over_benchmark_usd": -1.39,
   "annualised_net_apr_pct": 1.16
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.016,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.016,
   "over_benchmark_usd": -6.62,
   "annualised_net_apr_pct": 0.7
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 1.47%, $-219 per year, no — nets 1.47% a year at $10,000 in a ±0.010% band against a 3.60% savings rate

### [info] unlabelled venue 0x11111133 passed $69.3M through in 808 txs (100% ended flat, 5 counterparties)

```json
{
 "address": "0x111111338c5091e8440b67b168bae16a668ac0de",
 "shape": "pass-through",
 "gross_usd": 69288190,
 "txs": 808,
 "counterparties": 5,
 "tokens": 3,
 "pass_through_share": 1.0,
 "received_usd": 34644095,
 "sent_usd": 34644095,
 "retained_usd": 0,
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

### [info] unlabelled eoa 0x8a766185 passed $51.9M through in 518 txs (99% ended flat, 7 counterparties)

```json
{
 "address": "0x8a766185b4965fb2ffe57e9bd7ca1dddb4d8ee86",
 "shape": "pass-through",
 "gross_usd": 51945259,
 "txs": 518,
 "counterparties": 7,
 "tokens": 3,
 "pass_through_share": 0.988,
 "received_usd": 25928619,
 "sent_usd": 26016640,
 "retained_usd": -88021,
 "retention": -0.0034,
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

### [info] unlabelled eoa 0x5c2c1aa8 cycled $20.8M and ended the window flat (7 txs, 5 counterparties)

```json
{
 "address": "0x5c2c1aa8cebdeb2225e93481f93469ac8e1d210f",
 "shape": "cycles",
 "gross_usd": 41542277,
 "txs": 7,
 "counterparties": 5,
 "tokens": 2,
 "pass_through_share": 0.0,
 "received_usd": 20771138,
 "sent_usd": 20771138,
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

### [info] uniswap_v3 WETH/USDT: $1.0M in a ±0.28% band earns 10.7bp of fees less 6.9bp of divergence over 2.0h (163.6% a year if it repeats)

```json
{
 "pool": "0x4e68ccd3e89f51c3074ca5072bbac773960dfa36",
 "venue": "uniswap_v3",
 "pair": "WETH/USDT",
 "stable_pair": false,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.278,
 "band_quoted_pct": 0.278,
 "concentration_multiplier": 720.9,
 "band_ladder": [
  {
   "band_pct": 0.278,
   "apr_pct_at_10000": 349.07
  },
  {
   "band_pct": 0.556,
   "apr_pct_at_10000": 175.55
  },
  {
   "band_pct": 1.39,
   "apr_pct_at_10000": 70.82
  },
  {
   "band_pct": 5.56,
   "apr_pct_at_10000": 18.27
  }
 ],
 "pool_band_capital_usd": 2485342,
 "full_range_capital_usd": 1791742998,
 "passive_fees_usd": 3724.71,
 "volume_usd": 1241569,
 "swaps": 103,
 "annualisation_factor": 4373.4,
 "n_takers": 83,
 "top_taker": "0x58a497019644d8c383c8d3764c32ffd43506e836",
 "top_taker_share": 0.2426,
 "taker_herfindahl": 0.1599,
 "apr_band_1pct_as_reported": 1.8316,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 14.927,
   "divergence_bps_window": 6.945,
   "net_bps_window": 7.981,
   "over_benchmark_usd": 7.98,
   "annualised_net_apr_pct": 349.07
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 14.691,
   "divergence_bps_window": 6.945,
   "net_bps_window": 7.746,
   "over_benchmark_usd": 38.73,
   "annualised_net_apr_pct": 338.77
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 13.617,
   "divergence_bps_window": 6.945,
   "net_bps_window": 6.672,
   "over_benchmark_usd": 166.8,
   "annualised_net_apr_pct": 291.79
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 10.687,
   "divergence_bps_window": 6.945,
   "net_bps_window": 3.742,
   "over_benchmark_usd": 374.16,
   "annualised_net_apr_pct": 163.64
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 163.64%, $1,636,366 per year, no — nets 163.64% a year at $1,000,000 in a ±0.278% band, before any view on holding the pair

### [info] PYUSD pays 3.29pp more on Aave v3 than SparkLend; best size $4.4M earns $51k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.875,
  "SparkLend": 0.585
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.29,
 "gap_pp_despiked": 3.29,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7599229,
  "SparkLend": 100001127
 },
 "utilisation": {
  "Aave v3": 0.878,
  "SparkLend": 0.167
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 4405910,
  "apr_at_size_pct": 1.736,
  "over_low_venue_usd_per_year": 50722
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.785
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

Economics: net APR 1.15%, $50,722 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.61pp more on Aave v3 than SparkLend; best size $7.1M earns $21k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "DAI",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.066,
  "SparkLend": 2.459
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 0.607,
 "gap_pp_despiked": 0.607,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 DAI: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 131588802,
  "SparkLend": 308261201
 },
 "utilisation": {
  "Aave v3": 0.867,
  "SparkLend": 0.677
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 7089600,
  "apr_at_size_pct": 2.761,
  "over_low_venue_usd_per_year": 21408
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.062
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.021
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 2.846
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

Economics: net APR 0.30%, $21,408 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v3 WBTC/WETH: $50.0k in a ±0.25% band earns 6.4bp of fees less 6.2bp of divergence over 2.0h (11.1% a year if it repeats)

```json
{
 "pool": "0x4585fe77225b41b697c938b018e2ac67ac5a20c0",
 "venue": "uniswap_v3",
 "pair": "WBTC/WETH",
 "stable_pair": false,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.247,
 "band_quoted_pct": 0.247,
 "concentration_multiplier": 811.2,
 "band_ladder": [
  {
   "band_pct": 0.247,
   "apr_pct_at_10000": 36.23
  },
  {
   "band_pct": 0.494,
   "apr_pct_at_10000": 19.88
  },
  {
   "band_pct": 1.235,
   "apr_pct_at_10000": 8.42
  },
  {
   "band_pct": 4.94,
   "apr_pct_at_10000": 2.22
  }
 ],
 "pool_band_capital_usd": 438000,
 "full_range_capital_usd": 355312639,
 "passive_fees_usd": 313.58,
 "volume_usd": 627160,
 "swaps": 84,
 "annualisation_factor": 4373.4,
 "n_takers": 55,
 "top_taker": "0x82da8233b45b02c154d9ce3c46e99eec18e25a4f",
 "top_taker_share": 0.1774,
 "taker_herfindahl": 0.0681,
 "apr_band_1pct_as_reported": 0.7776,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 7.0,
   "divergence_bps_window": 6.171,
   "net_bps_window": 0.828,
   "over_benchmark_usd": 0.83,
   "annualised_net_apr_pct": 36.23
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 6.426,
   "divergence_bps_window": 6.171,
   "net_bps_window": 0.255,
   "over_benchmark_usd": 1.27,
   "annualised_net_apr_pct": 11.14
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 4.558,
   "divergence_bps_window": 6.171,
   "net_bps_window": -1.613,
   "over_benchmark_usd": -40.33,
   "annualised_net_apr_pct": -70.56
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 2.181,
   "divergence_bps_window": 6.171,
   "net_bps_window": -3.991,
   "over_benchmark_usd": -399.05,
   "annualised_net_apr_pct": -174.52
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 11.14%, $5,554 per year, no — nets 11.14% a year at $50,000 in a ±0.247% band, before any view on holding the pair

### [info] Aave v3 USDtb pays 8.05% against the Sky savings rate at 3.60%; best size $227.4k earns $5.4k a year over it [one-block read, de-spiking unavailable]

```json
{
 "venue": "Aave v3",
 "asset": "USDtb",
 "supply_apr_spot_pct": 8.05,
 "supply_apr_window_median_pct": null,
 "spiked": false,
 "despike_unavailable": true,
 "benchmark": "Sky savings rate",
 "benchmark_pct": 3.6,
 "gap_pp": 4.45,
 "supplied_usd": 15446317,
 "borrowed_usd": 12857871,
 "available_usd": 2588446,
 "utilisation": 0.8324,
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
   "marginal_apr_pct": 7.124,
   "over_benchmark_usd_per_year": 3524
  },
  {
   "size_usd": 1000000.0,
   "marginal_apr_pct": 2.445,
   "over_benchmark_usd_per_year": -11551
  },
  {
   "size_usd": 10000000.0,
   "marginal_apr_pct": 1.021,
   "over_benchmark_usd_per_year": -257871
  },
  {
   "size_usd": 50000000.0,
   "marginal_apr_pct": 0.154,
   "over_benchmark_usd_per_year": -1722803
  }
 ],
 "best": {
  "size_usd": 227373.67544323206,
  "apr": 0.059634935002953186,
  "marginal_apr_pct": 5.963,
  "over_benchmark_usd_per_year": 5374
 },
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 2.36%, $5,374 per year, GO — clears gas, impact and competition at this size

### [info] uniswap_v4 sUSDe/USDT: $50.0k in a ±0.04% band earns 1.1bp of fees less 1.0bp of divergence over 2.0h (3.5% a year if it repeats)

```json
{
 "pool": "0xb20351bcf606dcc3525d2ed36760a86a5dec7423b77d41125bd4a416ba93448b",
 "venue": "uniswap_v4",
 "pair": "sUSDe/USDT",
 "stable_pair": false,
 "window_hours": 2.003,
 "observed_price_range_pct": 0.039,
 "band_quoted_pct": 0.039,
 "concentration_multiplier": 5129.7,
 "band_ladder": [
  {
   "band_pct": 0.039,
   "apr_pct_at_10000": 5.86
  },
  {
   "band_pct": 0.078,
   "apr_pct_at_10000": 3.09
  },
  {
   "band_pct": 0.195,
   "apr_pct_at_10000": 1.27
  },
  {
   "band_pct": 0.78,
   "apr_pct_at_10000": 0.32
  }
 ],
 "pool_band_capital_usd": 775883,
 "full_range_capital_usd": 3980050445,
 "passive_fees_usd": 87.15,
 "volume_usd": 862880,
 "swaps": 29,
 "annualisation_factor": 4373.4,
 "n_takers": 22,
 "top_taker": "0x8b41013f5f0e23f5444d4a7927da0e567f50cdd7",
 "top_taker_share": 0.6713,
 "taker_herfindahl": 0.4985,
 "apr_band_1pct_as_reported": 0.0193,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 1.109,
   "divergence_bps_window": 0.975,
   "net_bps_window": 0.134,
   "over_benchmark_usd": 0.13,
   "annualised_net_apr_pct": 5.86
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 1.055,
   "divergence_bps_window": 0.975,
   "net_bps_window": 0.08,
   "over_benchmark_usd": 0.4,
   "annualised_net_apr_pct": 3.51
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.85,
   "divergence_bps_window": 0.975,
   "net_bps_window": -0.125,
   "over_benchmark_usd": -3.13,
   "annualised_net_apr_pct": -5.48
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.491,
   "divergence_bps_window": 0.975,
   "net_bps_window": -0.484,
   "over_benchmark_usd": -48.42,
   "annualised_net_apr_pct": -21.17
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies; no benchmark is applied \u2014 the alternative to LPing a volatile pair is holding the pair, and this detector has no view on that"
}
```

Economics: net APR 3.51%, $1,749 per year, no — nets 3.51% a year at $50,000 in a ±0.039% band, before any view on holding the pair

### [info] JIT took $15 of $12707 pool fees (0.12%) across 44 episodes by 10 operator(s)

```json
{
 "episodes": 44,
 "fee_taken_usd": 14.66,
 "pool_fees_usd": 12707.07,
 "share_of_fees": 0.0012,
 "swap_usd_bracketed": 45443,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 15,
   "fee_taken_usd": 10.26
  },
  {
   "sender": "0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de",
   "episodes": 9,
   "fee_taken_usd": 2.43
  },
  {
   "sender": "0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2",
   "episodes": 4,
   "fee_taken_usd": 0.74
  },
  {
   "sender": "0x58c75e1031040910a676c4fd30837e5f8a0b55f1",
   "episodes": 3,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0xaaa0bf2e340c2125603b8ffd4ec30faea08effff",
   "episodes": 2,
   "fee_taken_usd": 0.0
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR -0.00%, $-15,105 per year, no — net APR -0.00% below the 0.00% floor

### [info] 66 poisoning attempt(s) from 37 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0x298bad0b5f6c319611858b5707034c5827ca34394332726364a96ad65199e1ae",
   "big_eth": 155.61,
   "victim": "0x84f08e76913cb8e49560c70216c2daa73d0e8d21",
   "impersonated": "0x4214984f79eda3cb3ccfe6d6b9aa92c046f166c4",
   "attacker": "0x4214f1cacac62ac2d500e716e1af8338509166c4",
   "dust_tx": "0xbabefc11bd327576b9607401d8b4cf3dd9038a26e53cf8692bb40a3ebfaebc39",
   "seconds_after": 204
  },
  {
   "big_tx": "0x298bad0b5f6c319611858b5707034c5827ca34394332726364a96ad65199e1ae",
   "big_eth": 155.61,
   "victim": "0x84f08e76913cb8e49560c70216c2daa73d0e8d21",
   "impersonated": "0x4214984f79eda3cb3ccfe6d6b9aa92c046f166c4",
   "attacker": "0x4214b1b8d4950928fa6f0531c67ce4573e1466c4",
   "dust_tx": "0x17f7126f6ccc3d386a67b0b88368f034fc1bca2c1d7552ad492a4e13e8e5f14d",
   "seconds_after": 516
  },
  {
   "big_tx": "0x298bad0b5f6c319611858b5707034c5827ca34394332726364a96ad65199e1ae",
   "big_eth": 155.61,
   "victim": "0x84f08e76913cb8e49560c70216c2daa73d0e8d21",
   "impersonated": "0x4214984f79eda3cb3ccfe6d6b9aa92c046f166c4",
   "attacker": "0x42230ad802f0cf6b10acf7ad458672bb04f166c4",
   "dust_tx": "0x7adc71c5f2f7d94435c2c8887d6d1ccd6e6a9b2cfbf1430f439a67d4f1b61d9d",
   "seconds_after": 3204
  },
  {
   "big_tx": "0xd871545c53f1fad2746d92107905490ac012db000f84b465975fdfd4c55ad84b",
   "big_eth": 1600.04,
   "victim": "0xceb69f6342ece283b2f5c9088ff249b5d0ae66ea",
   "impersonated": "0x93bf2c486128097da8bd2dfe62b83f3f85790342",
   "attacker": "0x93beed5bd43f9fa5d5eafcb55eb9451ce1390342",
   "dust_tx": "0x3fbd2654c766eb439d400244a65fa5ae32b1e1fef468db2b131a9a9ad050ba95",
   "seconds_after": 3492
  },
  {
   "big_tx": "0xd84e8eabaa7378f0f010fc33adae4e0f3ffc8c0dc5a95b13bbc7121f53f3e7af",
   "big_eth": 108.41,
   "victim": "0x747f76fba9402f7c3fe0489f345b016f0be78a47",
   "impersonated": "0x30d5d27683cfc6cc7afe8a681e24864e335d5dc4",
   "attacker": "0x30d5b57521301616204c19d2e5a27fffd3ca5dc4",
   "dust_tx": "0x5a1698aa98cc11bc98985024a41a6adef2167a58efa5a73033e80a5a5126976f",
   "seconds_after": 456
  },
  {
   "big_tx": "0xd84e8eabaa7378f0f010fc33adae4e0f3ffc8c0dc5a95b13bbc7121f53f3e7af",
   "big_eth": 108.41,
   "victim": "0x747f76fba9402f7c3fe0489f345b016f0be78a47",
   "impersonated": "0x30d5d27683cfc6cc7afe8a681e24864e335d5dc4",
   "attacker": "0x30d52773a10cdb04cbeea9ba6f6355b650e55dc4",
   "dust_tx": "0x8f8ec7bd563c82be07044cc5ae9990ae6e3
```

### [info] dust spam: 0x7d9f4ca54131e588fc1fe577973b55 sent USDC to 1,238 recipients in 60 txs (25 per tx)

```json
{
 "token": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "token_symbol": "USDC",
 "sender": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "sender_label": null,
 "kind": "dust spam",
 "transfers": 1500,
 "recipients": 1238,
 "txs": 60,
 "blocks": 60,
 "transfers_per_tx": 25.0,
 "carrier_contract": "0x7d9f4ca54131e588fc1fe577973b55fb11231e76",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "286",
 "uniform_amount_share": 0.005,
 "usd_median": 0.0002859678679,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

### [info] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 924 recipients in 26 txs (40 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 1036,
 "recipients": 924,
 "txs": 26,
 "blocks": 26,
 "transfers_per_tx": 39.8,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "29417013623999576395",
 "uniform_amount_share": 0.005,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

