# Detector sweep — research/2026-10-09/live_1h

Ran 17 detector(s); 32 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 0.68 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `borrow_cost` | 5 | 0.67 | cheapest venue to borrow each asset, capped by the liquidity actually withdrawable there |
| `delegated_dust` | 1 | 0.89 | mass dust fan-out inside EIP-7702 / executeBatch calldata, from senders that mimic the recipient's counterparties |
| `dollar_rate_outlier` | 1 | 0.00 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `fixed_vs_floating` | 3 | 0.00 | Pendle implied fixed yields against the floating rate on the same underlying, sized by PT depth |
| `gas_concentration` | 0 | 0.00 | base-fee spikes attributed to the contract whose gas demand caused them |
| `honeypot_signature` | 4 | 0.77 | tokens whose buyers cannot sell: reverting sales, confiscatory taxes, buyers without sellers |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `liquidity_blackout` | 0 | 0.00 | lending reserves whose withdrawable liquidity collapses, and the time of day it happens |
| `lp_marginal_yield` | 2 | 0.00 | concentrated-LP fee yield net of divergence, at the band that stayed in range and at real size |
| `mass_distribution` | 1 | 1.25 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 4 | 0.74 | address labels the window contradicts, which is how a headline moves by a multiple |
| `nav_discount` | 1 | 0.00 | redeemable claims trading away from the value the protocol pays, with the queue that separates them |
| `rate_dispersion` | 4 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `recycled_swap_volume` | 1 | 0.85 | large same-transaction, same-pool v2-style swaps with nearly closed token positions |
| `solver_fingerprint` | 2 | 0.71 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |
| `token_fan_in` | 1 | 1.11 | settled token transfers from thousands of senders concentrated at one recipient |

### [notable] hot wallet Binance 8 (model-memory) only received ($113.4M in, nothing out)

```json
{
 "address": "0xf977814e90da44bfa03b6295a0616a897441acec",
 "label": "Binance 8 (model-memory)",
 "source": "model-memory",
 "in_usd": 113424531,
 "why": "a hot wallet pays withdrawals out; a pure receiver is a deposit address or a treasury, which puts this inflow on the wrong side of net flow"
}
```

### [notable] $4,949,693 of settled turnover in 1 same-pool atomic round trips; token positions almost close

```json
{
 "pool": "0xcb62c2d6894736d4216a41f5812bb9771de056d5",
 "roundtrips": 1,
 "gross_priced_leg_usd": 4949693.278368884,
 "pool_net_priced_token_usd": -0.15117608641765995,
 "examples": [
  {
   "tx": "0xf2eff69f95828f85213729c859e39fa4ff0cf163087ea7ce5f224c23a09f04e8",
   "block": 26157179,
   "sender": "0x5afec0de001999766fb883860cae06f5932e6f32",
   "gross_priced_leg_usd": 4949693.278368884,
   "priced_token": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
   "pool_net_priced_token_raw": "-61084949155569",
   "pool_net_priced_token_usd": -0.15117608641765995,
   "closure_fractions": [
    0.0,
    6.10850302425933e-08
   ]
  }
 ],
 "note": "Gross turnover is preserved. Net here is only the pool\u2019s priced token delta; it excludes gas and other assets. A fee-rate times gross turnover estimate does not measure realizable LP profit through these price round trips."
}
```

### [notable] USDS borrows 1.21pp cheaper on SparkLend than Aave v3; $371.3M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDS",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.319,
  "liquidity_usd": 371256741,
  "utilisation": 0.6939380341869387,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 5.533,
  "liquidity_usd": 8088767
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.319,
   "liquidity_usd": 371256741,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 5.533,
   "liquidity_usd": 8088767,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.214,
 "refinance_gas_usd": 0.437,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.21%, $4,506,186 per year, GO — clears gas, impact and competition at this size

### [notable] DAI borrows 0.50pp cheaper on SparkLend than Aave v3; $74.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "DAI",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.436,
  "liquidity_usd": 74727884,
  "utilisation": 0.7137438873438366,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.938,
  "liquidity_usd": 11804671
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.436,
   "liquidity_usd": 74727884,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.938,
   "liquidity_usd": 11804671,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 0.502,
 "refinance_gas_usd": 0.437,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.50%, $374,791 per year, GO — clears gas, impact and competition at this size

### [notable] USDS pays 3.63pp more on Sky SSR than Aave v3; best size $8.1M earns $294k a year over Aave v3

```json
{
 "asset": "USDS",
 "high_venue": "Sky SSR",
 "low_venue": "Aave v3",
 "supply_apr_spot_pct": {
  "Aave v3": 0.167,
  "SparkLend": 2.697,
  "Sky SSR": 3.8
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 3.633,
 "gap_pp_despiked": 3.633,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Sky SSR emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 8427133,
  "SparkLend": 1213011684,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.04,
  "SparkLend": 0.694
 },
 "dilution_basis": "modelled",
 "best_size": {
  "size_usd": 8089023.170370896,
  "apr_at_size_pct": 3.7999998803906365,
  "over_low_venue_usd_per_year": 293906.08554234914
 },
 "unconstrained_best_size": null,
 "source_available_usd": 8089023.170370896,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": null
}
```

Economics: net APR 3.63%, $293,906 per year, GO — clears gas, impact and competition at this size

### [notable] RLUSD borrows 1.65pp cheaper on Morpho Blue than SparkLend; $6.7M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "RLUSD",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 2.295,
  "liquidity_usd": 6736748,
  "utilisation": 0.723179,
  "collateral_required": "WBTC (0x2260fac5, LLTV 86.0%)",
  "market": "0xa128dddc761075df"
 },
 "dearest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 3.94,
  "liquidity_usd": 6649380
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 2.295,
   "liquidity_usd": 6736748,
   "collateral": "WBTC (0x2260fac5, LLTV 86.0%)"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.94,
   "liquidity_usd": 6649380,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.645,
 "refinance_gas_usd": 0.437,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.65%, $110,832 per year, GO — clears gas, impact and competition at this size

### [notable] USDC borrows 0.92pp cheaper on SparkLend than Compound v3 USDC; $4.6M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDC",
 "cheapest": {
  "venue": "SparkLend",
  "borrow_apy_pct": 4.369,
  "liquidity_usd": 4594212,
  "utilisation": 0.9053743247602655,
  "collateral_required": "any listed on the pool",
  "market": null
 },
 "dearest": {
  "venue": "Compound v3 USDC",
  "borrow_apy_pct": 5.288,
  "liquidity_usd": 36861138
 },
 "all_venues": [
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 4.369,
   "liquidity_usd": 4594212,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 4.771,
   "liquidity_usd": 35797141,
   "collateral": "cbBTC (0xcbb7c000, LLTV 86.0%)"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.964,
   "liquidity_usd": 135996604,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Compound v3 USDC",
   "borrow_apy_pct": 5.288,
   "liquidity_usd": 36861138,
   "collateral": "the Comet\u2019s listed collaterals"
  }
 ],
 "gap_pp": 0.919,
 "refinance_gas_usd": 0.437,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 0.92%, $42,219 per year, GO — clears gas, impact and competition at this size

### [notable] sUSDe trades 6.5bp below NAV, 3.8bp after the 2.7bp round trip; cooldownShares, then unstake after cooldownDuration (1 day)

```json
{
 "asset": "sUSDe",
 "nav_source": "0x9d39a5de convertToAssets(uint256)",
 "nav": 1.252245,
 "market_vw_price": 1.251425,
 "market_median": 1.251444,
 "market_p10": 1.251396,
 "discount_bps": 6.55,
 "traded_volume_usd": 211332,
 "implied_daily_volume_usd": 5071968,
 "refills_needed_per_year": 365,
 "swaps": 5,
 "venues": {
  "uniswap_v4": 5
 },
 "redemption": {
  "days": 1.0,
  "atomic": false,
  "availability": "always",
  "exit_bps": 2.7,
  "path": "cooldownShares, then unstake after cooldownDuration (1 day)"
 },
 "net_edge_bps": 3.85,
 "price_dispersion_bps": 0.62,
 "discount_at_p10_bps": 6.78,
 "significance_vs_dispersion": 6.16,
 "dispersion_note": "a dollar claim\u2019s NAV barely moves, so the spread is mostly execution dispersion and the test is meaningful",
 "why": "the protocol pays NAV and the market paid less; the gap closes when you redeem, and the wait is the reason a bot cannot take it from you"
}
```

Economics: net APR 14.00%, $29,586 per year, GO — clears gas, impact and competition at this size

### [notable] USDT borrows 1.18pp cheaper on Morpho Blue than Aave v3; $1.4M withdrawable there, gas is negligible at this base fee — the constraint is the collateral and the liquidity

```json
{
 "asset": "USDT",
 "cheapest": {
  "venue": "Morpho Blue",
  "borrow_apy_pct": 3.124,
  "liquidity_usd": 1434654,
  "utilisation": 0.797517,
  "collateral_required": "WBTC (0x2260fac5, LLTV 86.0%)",
  "market": "0x3c5a244b778095e1"
 },
 "dearest": {
  "venue": "Aave v3",
  "borrow_apy_pct": 4.299,
  "liquidity_usd": 221298641
 },
 "all_venues": [
  {
   "venue": "Morpho Blue",
   "borrow_apy_pct": 3.124,
   "liquidity_usd": 1434654,
   "collateral": "WBTC (0x2260fac5, LLTV 86.0%)"
  },
  {
   "venue": "Compound v3 USDT",
   "borrow_apy_pct": 3.968,
   "liquidity_usd": 18409505,
   "collateral": "the Comet\u2019s listed collaterals"
  },
  {
   "venue": "SparkLend",
   "borrow_apy_pct": 3.97,
   "liquidity_usd": 16265693,
   "collateral": "any listed on the pool"
  },
  {
   "venue": "Aave v3",
   "borrow_apy_pct": 4.299,
   "liquidity_usd": 221298641,
   "collateral": "any listed on the pool"
  }
 ],
 "gap_pp": 1.175,
 "refinance_gas_usd": 0.437,
 "caveat": "moving a position between venues also pays the spread on any collateral that has to be converted, which this does not price: it compares rates and liquidity only",
 "why": "the saving is capped by what is withdrawable at the cheap venue, and on an isolated market it is only available against the collateral that market accepts \u2014 which is usually the binding constraint rather than the rate"
}
```

Economics: net APR 1.18%, $16,858 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 0.82pp more on Compound v3 USDC than SparkLend; best size $544k earns $2k a year over SparkLend

```json
{
 "asset": "USDC",
 "high_venue": "Compound v3 USDC",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 4.215,
  "SparkLend": 3.56,
  "Compound v3 USDC": 4.383,
  "Sky SSR": 3.8
 },
 "supply_apr_median_pct": {
  "Aave v3": 4.239
 },
 "gap_pp_spot": 0.824,
 "gap_pp_despiked": 0.824,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "Compound v3 USDC emits no ReserveDataUpdated logs, so the head read is the only source",
 "supplied_usd": {
  "Aave v3": 2405104132,
  "SparkLend": 48551433,
  "Compound v3 USDC": 382290309,
  "Sky SSR": 1000000000
 },
 "utilisation": {
  "Aave v3": 0.943,
  "SparkLend": 0.905,
  "Compound v3 USDC": 0.904
 },
 "dilution_basis": "sampled",
 "best_size": {
  "size_usd": 544066.837433391,
  "apr_at_size_pct": 3.973,
  "over_low_venue_usd_per_year": 2250
 },
 "unconstrained_best_size": {
  "size_usd": 544066.837433391,
  "apr_at_size_pct": 3.973,
  "over_low_venue_usd_per_year": 2250
 },
 "source_available_usd": 4599236.579087235,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 4.308
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.63
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.211
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 3.053
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 2.578
  }
 ]
}
```

Economics: net APR 0.41%, $2,250 per year, GO — clears gas, impact and competition at this size

### [notable] 0x59aab1bd… sprayed 3,984 dust legs from 968 delegated accounts at 1,740 wallets; 27.2% of testable legs came from a lookalike of the recipient's own counterparty

```json
{
 "operator": "0x59aab1bd0d26290274398c07b55955c15425e16b",
 "operator_label": null,
 "dust_legs": 3984,
 "executing_accounts": 968,
 "recipients": 1740,
 "legs_with_a_testable_recipient": 3769,
 "legs_from_a_lookalike_counterparty": 1026,
 "lookalike_rate": 0.2722,
 "tokens": {
  "0xdac17f958d2ee523a2206206994597c13d831ec7": 1626,
  "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": 1050,
  "0x6b175474e89094c44da98b954eedeac495271d0f": 2
 },
 "native_legs": 1306,
 "total_wei_moved": 130600000000,
 "examples": [
  {
   "victim": "0x97bdb3a66a58bffc10d31fcca926fb407d87b7ba",
   "dust_from": "0x939fc401043417696f2b5f2bfb5b24d4e4272f02",
   "mimics": "0x939f7e8f47041bfc357a08e4c7d50138c28c2f02",
   "tx": "0x2e62f9c7739ad5a7f8be78334c51dc8797d79f61c4b7bbe76b46ece188774047"
  },
  {
   "victim": "0x18282d0cc5b1b7b758b9acb05b1404ecf140e455",
   "dust_from": "0x4f6b71379d35b28756f98403ec634bd4c8880812",
   "mimics": "0x4f6bd762bb5ca5ddaab2492dbfd473741eab0812",
   "tx": "0x2e62f9c7739ad5a7f8be78334c51dc8797d79f61c4b7bbe76b46ece188774047"
  },
  {
   "victim": "0x97bdb3a66a58bffc10d31fcca926fb407d87b7ba",
   "dust_from": "0xfa33d790419395368910f6323bd547e63d366b3a",
   "mimics": "0xfa330abbb0fb4ea7b6d44bae2298045deb816b3a",
   "tx": "0x2e62f9c7739ad5a7f8be78334c51dc8797d79f61c4b7bbe76b46ece188774047"
  },
  {
   "victim": "0x6e89a93aa1e8698c85ea8da9aec00b979cebecd5",
   "dust_from": "0x4a3f12fee47b731af40453b056ef9088963805cf",
   "mimics": "0x4a3f34be6551abd3b4cbf85e963efbedbb3805cf",
   "tx": "0x1d11624e2a83fc5fee950c9af04531b367f7afab8e4c3fae04caa00b288097af"
  }
 ],
 "note": "lookalike = first 4 and last 4 hex characters shared with an address the recipient transacted with inside this window; a victim copying from a truncated history sees the same string. The rate is a floor: only in-window counterparties can be tested."
}
```

### [notable] techblockEURCV: 2,400 settled transfers from 2,072 senders converge on 0x4d2fb5f8ec (77.3% of token transfers)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "symbol": "techblockEURCV",
 "recipient": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "recipient_label": null,
 "transfers": 2400,
 "unique_senders": 2072,
 "token_transfer_share": 0.7729468599033816,
 "total_raw": "228496785086750930776550",
 "total_units": 228496.78508675093,
 "first_timestamp": 1791576323,
 "last_timestamp": 1791579623,
 "buckets": {
  "1791576000": 401,
  "1791576900": 588,
  "1791577800": 611,
  "1791578700": 612,
  "1791579600": 188
 },
 "examples": [
  {
   "tx": "0xfa604aeba8993f01406e8a31e96d8ee7c705b7703e1eb16468739019dda92f80",
   "block": 26157130,
   "sender": "0xffc265211b50bbf62851a3e981db5b4896e0b247",
   "raw": "3711090565343259506224"
  },
  {
   "tx": "0xfa604aeba8993f01406e8a31e96d8ee7c705b7703e1eb16468739019dda92f80",
   "block": 26157130,
   "sender": "0xc2163605a1e350e3dfb2eeccd04687895c00bd3e",
   "raw": "1500796610517606119377"
  },
  {
   "tx": "0xfa604aeba8993f01406e8a31e96d8ee7c705b7703e1eb16468739019dda92f80",
   "block": 26157130,
   "sender": "0xaa49bf6d717248201477765f830dcf6ba332ad8a",
   "raw": "685182848765278148617"
  }
 ],
 "note": "Settled positive non-mint/burn Transfer logs. Shared ownership, gas funders and deposit-versus-internal-sweep interpretation require follow-up."
}
```

### [notable] uniswap_v4 USDC/USDT: $10.0k in a ±0.01% band earns 0.0bp of fees less 0.0bp of divergence over 1.0h (2.7% a year if it repeats)

```json
{
 "pool": "0x2b21c65d9a7dc6926ee330a1c6e5a8037fd81774f3dc066536f800128e39f634",
 "venue": "uniswap_v4",
 "pair": "USDC/USDT",
 "stable_pair": true,
 "window_hours": 1.0,
 "observed_price_range_pct": 0.004,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 2.68
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 2.68
  },
  {
   "band_pct": 0.02,
   "apr_pct_at_10000": 1.35
  },
  {
   "band_pct": 0.08,
   "apr_pct_at_10000": 0.34
  }
 ],
 "pool_band_capital_usd": 1071008,
 "full_range_capital_usd": 21421758849,
 "passive_fees_usd": 3.31,
 "volume_usd": 547125,
 "swaps": 63,
 "annualisation_factor": 8760.0,
 "n_takers": 55,
 "top_taker": "0x5c3593481cba011737e36ded62f1797c9f6afce1",
 "top_taker_share": 0.1642,
 "taker_herfindahl": 0.0936,
 "apr_band_1pct_as_reported": 0.0003,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.031,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.031,
   "over_benchmark_usd": -0.01,
   "annualised_net_apr_pct": 2.68
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.03,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.03,
   "over_benchmark_usd": -0.07,
   "annualised_net_apr_pct": 2.59
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.025,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.025,
   "over_benchmark_usd": -0.46,
   "annualised_net_apr_pct": 2.19
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.016,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.016,
   "over_benchmark_usd": -2.74,
   "annualised_net_apr_pct": 1.4
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 2.68%, $-88 per year, no — nets 2.68% a year at $10,000 in a ±0.010% band against a 3.80% savings rate

### [notable] uniswap_v4 USDT/USDS: $10.0k in a ±0.01% band earns 0.0bp of fees less 0.0bp of divergence over 1.0h (2.3% a year if it repeats)

```json
{
 "pool": "0x3b1b1f2e775a6db1664f8e7d59ad568605ea2406312c11aef03146c0cf89d5b9",
 "venue": "uniswap_v4",
 "pair": "USDT/USDS",
 "stable_pair": true,
 "window_hours": 1.0,
 "observed_price_range_pct": 0.004,
 "band_quoted_pct": 0.01,
 "concentration_multiplier": 20001.5,
 "band_ladder": [
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 2.32
  },
  {
   "band_pct": 0.01,
   "apr_pct_at_10000": 2.32
  },
  {
   "band_pct": 0.02,
   "apr_pct_at_10000": 1.16
  },
  {
   "band_pct": 0.08,
   "apr_pct_at_10000": 0.29
  }
 ],
 "pool_band_capital_usd": 4997915,
 "full_range_capital_usd": 99965792101,
 "passive_fees_usd": 13.24,
 "volume_usd": 2206872,
 "swaps": 41,
 "annualisation_factor": 8760.0,
 "n_takers": 36,
 "top_taker": "0x5c3593481cba011737e36ded62f1797c9f6afce1",
 "top_taker_share": 0.1538,
 "taker_herfindahl": 0.0923,
 "apr_band_1pct_as_reported": 0.0002,
 "ladder": [
  {
   "size_usd": 10000.0,
   "fee_bps_window": 0.026,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.026,
   "over_benchmark_usd": -0.02,
   "annualised_net_apr_pct": 2.32
  },
  {
   "size_usd": 50000.0,
   "fee_bps_window": 0.026,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.026,
   "over_benchmark_usd": -0.09,
   "annualised_net_apr_pct": 2.3
  },
  {
   "size_usd": 250000.0,
   "fee_bps_window": 0.025,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.025,
   "over_benchmark_usd": -0.45,
   "annualised_net_apr_pct": 2.21
  },
  {
   "size_usd": 1000000.0,
   "fee_bps_window": 0.022,
   "divergence_bps_window": 0.0,
   "net_bps_window": 0.022,
   "over_benchmark_usd": -2.13,
   "annualised_net_apr_pct": 1.93
  }
 ],
 "why": "fee yield priced at the band the price actually stayed inside, at a size that dilutes the pool\u2019s own liquidity, net of the divergence that the same concentration amplifies"
}
```

Economics: net APR 2.32%, $-175 per year, no — nets 2.32% a year at $10,000 in a ±0.010% band against a 3.80% savings rate

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

### [info] exchange 0xa9ac43f5b5e38155a288d1a01d2cbc4478e14573 ( moved 98% of its flow with one counterparty

```json
{
 "address": "0xa9ac43f5b5e38155a288d1a01d2cbc4478e14573",
 "label": "0xa9ac43f5b5e38155a288d1a01d2cbc4478e14573 (behaviour-day-study)",
 "source": "behaviour-day-study",
 "counterparty": "0x9c22a4039f269e72de6b029b273be059cdbb831c",
 "counterparty_label": null,
 "share": 0.982,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] unlabelled bot 0x410144de cycled $18.4M and ended the window flat (4 txs, 6 counterparties)

```json
{
 "address": "0x410144dec85bb1929057829d54fb3b8d3f0ea4a3",
 "shape": "cycles",
 "gross_usd": 36829121,
 "txs": 4,
 "counterparties": 6,
 "tokens": 3,
 "pass_through_share": 0.0,
 "received_usd": 18414561,
 "sent_usd": 18414559,
 "retained_usd": 2,
 "retention": 0.0,
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

### [info] unlabelled atomic bot pair 0x56a76b42 passed $25.1M through in 7 txs (100% ended flat, 2 counterparties)

```json
{
 "address": "0x56a76b428244a50513ec81e225a293d128fd581d",
 "shape": "pass-through",
 "gross_usd": 25131395,
 "txs": 7,
 "counterparties": 2,
 "tokens": 1,
 "pass_through_share": 1.0,
 "received_usd": 12565697,
 "sent_usd": 12565697,
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

### [info] exchange Bitfinex 2 (model-memory) moved 99% of its flow with one counterparty

```json
{
 "address": "0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec",
 "label": "Bitfinex 2 (model-memory)",
 "source": "model-memory",
 "counterparty": "0x386f6b1719b62a27b6b79798390a612b36267f03",
 "counterparty_label": null,
 "share": 0.991,
 "why": "a venue serving one counterparty is plumbing between related accounts, not exchange flow"
}
```

### [info] PT-SUSDX-3DEC2026 implies 18.99% fixed for 54 days against the Sky savings rate (as the risk-free dollar) at 3.80% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x5e572498e9f83650f0ff24194999bddb4b390928",
 "pt": "0x06ebad062fd573ca31a72d6dfb0f425da2153985",
 "pt_symbol": "PT-SUSDX-3DEC2026",
 "implied_apy_pct": 18.994,
 "days_to_maturity": 54.11862268518519,
 "pt_to_asset": 0.9745454819943283,
 "underlying": "SUSDX",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.8,
 "gap_pp": 15.194,
 "classification": "credit spread",
 "pt_depth_units": 3188198,
 "pt_depth_usd": 3107044,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 11.84%, $91,953 per year, GO — clears gas, impact and competition at this size

### [info] PT-REUSD-10DEC2026 implies 11.86% fixed for 61 days against the Sky savings rate (as the risk-free dollar) at 3.80% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x13285bcbc27f92b47b4edb99d744c07b48c977c0",
 "pt": "0xecfafdc7741323a945a163ed068b5a3c43483957",
 "pt_symbol": "PT-REUSD-10DEC2026",
 "implied_apy_pct": 11.863,
 "days_to_maturity": 61.11862268518519,
 "pt_to_asset": 0.9814030716988212,
 "underlying": "REUSD",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.8,
 "gap_pp": 8.063,
 "classification": "credit spread",
 "pt_depth_units": 5569620,
 "pt_depth_usd": 5466042,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 5.09%, $69,582 per year, GO — clears gas, impact and competition at this size

### [info] PYUSD pays 7.16pp more on Aave v3 than SparkLend; best size $3.5M earns $40k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "PYUSD",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 8.181,
  "SparkLend": 1.025
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 7.156,
 "gap_pp_despiked": 7.156,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 PYUSD: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 7919280,
  "SparkLend": 100001540
 },
 "utilisation": {
  "Aave v3": 0.91,
  "SparkLend": 0.266
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 3471811.4081616686,
  "apr_at_size_pct": 2.171,
  "over_low_venue_usd_per_year": 39770
 },
 "unconstrained_best_size": {
  "size_usd": 3471811.4081616686,
  "apr_at_size_pct": 2.171,
  "over_low_venue_usd_per_year": 39770
 },
 "source_available_usd": 73446313.430516,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 4.04
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.339
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 1.747
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 0.389
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 0.078
  }
 ]
}
```

Economics: net APR 1.15%, $39,770 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.52pp more on Aave v3 than SparkLend; best size $5.3M earns $14k a year over SparkLend [one-block read, de-spiking unavailable]

```json
{
 "asset": "DAI",
 "high_venue": "Aave v3",
 "low_venue": "SparkLend",
 "supply_apr_spot_pct": {
  "Aave v3": 3.365,
  "SparkLend": 2.846
 },
 "supply_apr_median_pct": {},
 "gap_pp_spot": 0.519,
 "gap_pp_despiked": 0.519,
 "head_read_spiked": null,
 "despiked": false,
 "despike_note": "too few log observations for Aave v3 DAI: this is one block, and a large transfer or flash loan can move a reserve rate several-fold for one block",
 "supplied_usd": {
  "Aave v3": 129301413,
  "SparkLend": 261052534
 },
 "utilisation": {
  "Aave v3": 0.909,
  "SparkLend": 0.714
 },
 "dilution_basis": "irm",
 "best_size": {
  "size_usd": 5267571.102601006,
  "apr_at_size_pct": 3.107,
  "over_low_venue_usd_per_year": 13790
 },
 "unconstrained_best_size": {
  "size_usd": 5267571.102601006,
  "apr_at_size_pct": 3.107,
  "over_low_venue_usd_per_year": 13790
 },
 "source_available_usd": 75100021.89031062,
 "source_liquidity_basis": "underlying balanceOf(aToken), reserve active/paused flags",
 "capacity_note": "Aggregate source cash is a ceiling, not an owned position. Account collateral, destination supply caps and exit-time liquidity still need checks. Source opportunity rate and borrows are held fixed.",
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "apr_pct": 3.361
  },
  {
   "size_usd": 1000000.0,
   "apr_pct": 3.314
  },
  {
   "size_usd": 5000000.0,
   "apr_pct": 3.12
  },
  {
   "size_usd": 25000000.0,
   "apr_pct": 2.363
  },
  {
   "size_usd": 100000000.0,
   "apr_pct": 1.07
  }
 ]
}
```

Economics: net APR 0.26%, $13,790 per year, GO — clears gas, impact and competition at this size

### [info] PT-USDAT-14JAN2027 implies 8.41% fixed for 96 days against the Sky savings rate (as the risk-free dollar) at 3.80% — credit spread, not a rate trade: nothing here prices that issuer’s credit

```json
{
 "market": "0x4ccf6deb3d1895373f604b418ff55d8adae8b846",
 "pt": "0xba96292ee7673e3b546cc90db6d97111cd9a314f",
 "pt_symbol": "PT-USDAT-14JAN2027",
 "implied_apy_pct": 8.405,
 "days_to_maturity": 96.11862268518519,
 "pt_to_asset": 0.978971665855006,
 "underlying": "USDAT",
 "comparison": "the Sky savings rate (as the risk-free dollar)",
 "floating_pct": 3.8,
 "gap_pp": 4.605,
 "classification": "credit spread",
 "pt_depth_units": 1116845,
 "pt_depth_usd": 1093360,
 "oracle_ready": true,
 "why": "no floating rate on this underlying is readable, so the excess over the risk-free dollar is the market\u2019s price of an issuer\u2019s credit \u2014 a judgement this system has not made, quoted here only so it is not mistaken for a term premium"
}
```

Economics: net APR 2.72%, $7,423 per year, GO — clears gas, impact and competition at this size

### [info] Aave v3 PYUSD pays 8.18% against the Sky savings rate at 3.80%; best size $47.7k earns $1.0k a year over it [one-block read, de-spiking unavailable]

```json
{
 "venue": "Aave v3",
 "asset": "PYUSD",
 "supply_apr_spot_pct": 8.181,
 "supply_apr_window_median_pct": null,
 "spiked": false,
 "despike_unavailable": true,
 "benchmark": "Sky savings rate",
 "benchmark_pct": 3.8,
 "gap_pp": 4.381,
 "supplied_usd": 7919280,
 "borrowed_usd": 7206964,
 "available_usd": 712316,
 "utilisation": 0.9101,
 "curve": {
  "base": 0.01,
  "optimal": 0.9,
  "reserve_factor": 0.1,
  "slope1": 0.04,
  "slope2": 0.5
 },
 "marginal_apr_ladder": [
  {
   "size_usd": 100000.0,
   "marginal_apr_pct": 4.04,
   "over_benchmark_usd_per_year": 240
  },
  {
   "size_usd": 1000000.0,
   "marginal_apr_pct": 3.339,
   "over_benchmark_usd_per_year": -4612
  },
  {
   "size_usd": 10000000.0,
   "marginal_apr_pct": 1.009,
   "over_benchmark_usd_per_year": -279100
  },
  {
   "size_usd": 50000000.0,
   "marginal_apr_pct": 0.174,
   "over_benchmark_usd_per_year": -1813040
  }
 ],
 "best": {
  "size_usd": 47683.7158203125,
  "apr": 0.05945757103051772,
  "marginal_apr_pct": 5.946,
  "over_benchmark_usd_per_year": 1023
 },
 "why": "a headline rate is a point on a kinked curve; what it is worth is the marginal APR at the size you can actually put in, over the dollar you would otherwise hold"
}
```

Economics: net APR 2.15%, $1,023 per year, GO — clears gas, impact and competition at this size

### [info] JIT took $2 of $1011 pool fees (0.17%) across 7 episodes by 5 operator(s)

```json
{
 "episodes": 7,
 "fee_taken_usd": 1.69,
 "pool_fees_usd": 1011.32,
 "share_of_fees": 0.0017,
 "swap_usd_bracketed": 20774,
 "top_operators": [
  {
   "sender": "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
   "episodes": 3,
   "fee_taken_usd": 1.67
  },
  {
   "sender": "0x34373bba18aa058f889c3fc28329c0bfb4b3e4ab",
   "episodes": 1,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0xcee2cc4ecaa4dfe48c0cdb0b503657ff5247b279",
   "episodes": 1,
   "fee_taken_usd": 0.0
  },
  {
   "sender": "0x3ee92cd00993a4488ae153ab41ac7947cbcbc1de",
   "episodes": 1,
   "fee_taken_usd": 0.02
  },
  {
   "sender": "0xab567bb4953ac3b184e6078dd8d3d1dbf2dc03e2",
   "episodes": 1,
   "fee_taken_usd": 0.0
  }
 ],
 "why": "fees taken by liquidity that was not at risk are credited to passive LPs by any yield number computed from total fees; the honest input is passive_fees_usd"
}
```

Economics: net APR -0.00%, $-8,956 per year, no — net APR -0.00% below the 0.00% floor

### [info] 15 poisoning attempt(s) from 12 lookalike sender(s) after large transfers

```json
{
 "matches": [
  {
   "big_tx": "0xd2296ebc243504d560b15b221367f29ab59a6ab6805d29ecca866e4f2006a6f3",
   "big_eth": 1929.9,
   "victim": "0x32cb90b69da0d2c675b97d0284db65a7203e03da",
   "impersonated": "0x774e17035f619db9e869ad5559cae7d4ec18db20",
   "attacker": "0x774e197b119d62be3e03b50c69f8a97de459db20",
   "dust_tx": "0x2f00469783478d38f6004b506b64aa6d43982d5a2743b50b165565b7bfaab0cf",
   "seconds_after": 324
  },
  {
   "big_tx": "0xd2296ebc243504d560b15b221367f29ab59a6ab6805d29ecca866e4f2006a6f3",
   "big_eth": 1929.9,
   "victim": "0x32cb90b69da0d2c675b97d0284db65a7203e03da",
   "impersonated": "0x774e17035f619db9e869ad5559cae7d4ec18db20",
   "attacker": "0x774e197b119d62be3e03b50c69f8a97de459db20",
   "dust_tx": "0x2bf3604a725878bbdbb0042c46331ede350b222b3b4d24c80820b88bb49c729f",
   "seconds_after": 468
  },
  {
   "big_tx": "0xd2296ebc243504d560b15b221367f29ab59a6ab6805d29ecca866e4f2006a6f3",
   "big_eth": 1929.9,
   "victim": "0x32cb90b69da0d2c675b97d0284db65a7203e03da",
   "impersonated": "0x774e17035f619db9e869ad5559cae7d4ec18db20",
   "attacker": "0x774e338953cb3e415db28ce0051a12568086db20",
   "dust_tx": "0x62b7e3828b5dd17e45fe3cedc0f9b6448ac298a328442c3a5e79720f82af292b",
   "seconds_after": 1716
  },
  {
   "big_tx": "0x4d54d9b02d52625859ab9f6ae2203e7de1bf40302933ef20a2768259e08739f3",
   "big_eth": 349.33,
   "victim": "0x7f654086ec0574e3fd89723b575250f41024d8a9",
   "impersonated": "0x874d3a8a3d438158f0d3de4e28c0a43e26ea9b49",
   "attacker": "0x874d4c845d276cbe28aaabe2597fdd8bc7539b49",
   "dust_tx": "0x06fc5149522cab6711addb737b281f0110c15569d757a9d8aa4a39a4e4cda942",
   "seconds_after": 108
  },
  {
   "big_tx": "0x4d54d9b02d52625859ab9f6ae2203e7de1bf40302933ef20a2768259e08739f3",
   "big_eth": 349.33,
   "victim": "0x7f654086ec0574e3fd89723b575250f41024d8a9",
   "impersonated": "0x874d3a8a3d438158f0d3de4e28c0a43e26ea9b49",
   "attacker": "0x874d75d2d092c657e8ca2b94747b155213329b49",
   "dust_tx": "0x0a85c43c98cb19f841b84997a5ed584c07412c00f391fee5878788d9bca164ee",
   "seconds_after": 1416
  },
  {
   "big_tx": "0x4d54d9b02d52625859ab9f6ae2203e7de1bf40302933ef20a2768259e08739f3",
   "big_eth": 349.33,
   "victim": "0x7f654086ec0574e3fd89723b575250f41024d8a9",
   "impersonated": "0x874d3a8a3d438158f0d3de4e28c0a43e26ea9b49",
   "attacker": "0x874d4c845d276cbe28aaabe2597fdd8bc7539b49",
   "dust_tx": "0xffa004efb89fe46bdcff41679ec048968c1e
```

### [info] 0x5becd8d8cd: 367 buyers, 2 sellers — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x5becd8d8cd9c36a3cc848cfc9055cdab2915f489",
 "symbol": null,
 "label": null,
 "distinct_buyers": 367,
 "distinct_sellers": 2,
 "seller_to_buyer_ratio": 0.0054,
 "buy_legs": 916,
 "sell_legs": 348,
 "router_calls_naming_it": 348,
 "of_which_emitted_no_logs": 0,
 "fail_rate": 0.0,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 26157129,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] 0x60fd13ba6e: 309 buyers, 4 sellers — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x60fd13ba6eb4b4df8b3fbef5fe39eb9449616d74",
 "symbol": null,
 "label": null,
 "distinct_buyers": 309,
 "distinct_sellers": 4,
 "seller_to_buyer_ratio": 0.0129,
 "buy_legs": 324,
 "sell_legs": 115,
 "router_calls_naming_it": 115,
 "of_which_emitted_no_logs": 0,
 "fail_rate": 0.0,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 26157129,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] 0xb602651846: 136 buyers, 13 sellers — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0xb6026518463ec80f1cb33e4318e802487c27f995",
 "symbol": null,
 "label": null,
 "distinct_buyers": 136,
 "distinct_sellers": 13,
 "seller_to_buyer_ratio": 0.0956,
 "buy_legs": 183,
 "sell_legs": 58,
 "router_calls_naming_it": 58,
 "of_which_emitted_no_logs": 0,
 "fail_rate": 0.0,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 26157129,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] 0x41a4594575: 101 buyers, 1 sellers — buyers far outnumber sellers and sales were attempted, but none is shown to fail

```json
{
 "token": "0x41a4594575557efbf85cd950749bb0c1e99bcefd",
 "symbol": null,
 "label": null,
 "distinct_buyers": 101,
 "distinct_sellers": 1,
 "seller_to_buyer_ratio": 0.0099,
 "buy_legs": 105,
 "sell_legs": 68,
 "router_calls_naming_it": 68,
 "of_which_emitted_no_logs": 0,
 "fail_rate": 0.0,
 "window_base_fail_rate": 0.044,
 "buy_leg_retention": 1.0,
 "fee_beneficiary": null,
 "distinct_secondary_recipients": 0,
 "fee_concentration": null,
 "fee_is_a_fee_not_a_split_route": false,
 "buy_leg_tax": 0.0,
 "first_seen_block": 26157130,
 "verdict": "buyers far outnumber sellers and sales were attempted, but none is shown to fail",
 "why": "a transaction that emitted no logs reverted or did nothing, and a sell gate is what produces reverts; the buyer/seller ratio alone is the shape of any fresh launch, so it is never the finding on its own",
 "false_positives": "a thin pool reverting on slippage, an anti-sniper cooldown in a token\u2019s first minutes, and calldata that names several tokens so a failure is attributed to all of them. Confirm by reading the contract or simulating a sale before treating this as a verdict."
}
```

### [info] airdrop or multisend: 0x4d2fb5f8ec243fde4df1a9678b8223 sent 0xbeef007e to 659 recipients in 14 txs (50 per tx)

```json
{
 "token": "0xbeef007ecfbfdf9b919d0050821a9b6dbd634ff0",
 "token_symbol": null,
 "sender": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "sender_label": null,
 "kind": "airdrop or multisend",
 "transfers": 707,
 "recipients": 659,
 "txs": 14,
 "blocks": 14,
 "transfers_per_tx": 50.5,
 "carrier_contract": "0x4d2fb5f8ec243fde4df1a9678b82238570c7e0e4",
 "carrier_label": null,
 "carrier_share": 1.0,
 "median_raw_amount": "24450882090022279644",
 "uniform_amount_share": 0.005,
 "usd_median": null,
 "why": "a batched fan-out to this many wallets is a campaign; it explains log-count and gas anomalies, and a funded holder set is what a later coordinated sell looks like beforehand"
}
```

