# Detector sweep — research/2026-09-07/live_5h

Ran 4 detector(s); 8 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 5.56 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `gas_concentration` | 1 | 9.74 | base-fee spikes attributed to the contract whose gas demand caused them |
| `mislabelled_flow` | 1 | 5.22 | address labels the window contradicts, which is how a headline moves by a multiple |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |

### [high] deposit sink deposit sink (behaviour, day study) forwarded $100.0M in this window

```json
{
 "address": "0x3cc936b795a188f0e246cbb2d74c5bd190aecf18",
 "label": "deposit sink (behaviour, day study)",
 "source": "behaviour-day-study",
 "in_usd": 195682,
 "out_usd": 99988812,
 "why": "a deposit sink is defined by not forwarding; this one forwards, so its outflow is being counted as exchange outflow"
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
 }
}
```

Economics: net APR 3.48%, $34,761,177 per year, GO — clears gas, impact and competition at this size

### [notable] USDC pays 1.95pp more on Compound v3 USDC than SparkLend; $80.5M halves the gap

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
  "Aave v3": 4.269
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
 }
}
```

Economics: net APR 0.87%, $793,766 per year, GO — clears gas, impact and competition at this size

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

### [info] USDT pays 3.05pp more on SparkLend than Compound v3 USDT; $116.3M halves the gap [one-block read, de-spiking unavailable]

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
  "Aave v3": 4.239
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
 }
}
```

Economics: net APR 1.26%, $1,828,306 per year, GO — clears gas, impact and competition at this size

### [info] PYUSD pays 3.17pp more on Aave v3 than SparkLend; $5.7M halves the gap [one-block read, de-spiking unavailable]

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
 }
}
```

Economics: net APR 1.30%, $100,272 per year, GO — clears gas, impact and competition at this size

### [info] DAI pays 0.58pp more on Aave v3 than SparkLend; $13.9M halves the gap [one-block read, de-spiking unavailable]

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
 }
}
```

Economics: net APR 0.28%, $40,715 per year, GO — clears gas, impact and competition at this size

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

