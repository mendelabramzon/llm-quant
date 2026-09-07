# Detector sweep — research/2026-09-08/live_2h

Ran 8 detector(s); 19 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `address_poisoning` | 1 | 1.26 | lookalike dust transfers that follow a large transfer, aimed at a later copy-paste |
| `dollar_rate_outlier` | 2 | 1.24 | dollar supply rates ranked against the risk-free dollar, sized from each reserve’s own rate curve |
| `gas_concentration` | 0 | 0.00 | base-fee spikes attributed to the contract whose gas demand caused them |
| `jit_liquidity` | 1 | 0.00 | fee share taken by liquidity minted for a single swap, per pool and per window |
| `mass_distribution` | 4 | 1.93 | one sender fanning a token out to thousands of recipients: airdrop, mint distribution or dust spam |
| `mislabelled_flow` | 0 | 1.38 | address labels the window contradicts, which is how a headline moves by a multiple |
| `rate_dispersion` | 5 | 0.00 | cross-venue supply-rate gaps on one asset, de-spiked and sized by rate dilution |
| `solver_fingerprint` | 6 | 1.33 | unlabelled contracts that pass value straight through: solvers, routers and searcher bots |

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

