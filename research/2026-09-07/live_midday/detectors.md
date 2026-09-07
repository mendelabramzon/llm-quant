# Detector sweep — research/2026-09-07/live_midday

Ran 4 detector(s); 9 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 5.95 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `gas_concentration` | 0 | 5.74 | base-fee spikes attributed to the contract whose gas demand caused them |
| `mislabelled_flow` | 3 | 6.21 | address labels the window contradicts, which is how a headline moves by a multiple |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |

### [high] deposit sink deposit sink (behaviour, day study) forwarded $10.0M in this window

```json
{
 "address": "0x3cc936b795a188f0e246cbb2d74c5bd190aecf18",
 "label": "deposit sink (behaviour, day study)",
 "source": "behaviour-day-study",
 "in_usd": 170356,
 "out_usd": 9999597,
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

### [notable] PYUSD pays 3.30pp more on Aave v3 than SparkLend; $5.6M halves the gap

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

### [notable] DAI pays 0.58pp more on Aave v3 than SparkLend; $14.0M halves the gap

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

