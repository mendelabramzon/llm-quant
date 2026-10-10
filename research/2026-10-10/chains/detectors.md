# New-activity sweep — research/2026-10-10/chains

Ran 8 detectors; 40 hit(s): 2 high, 23 notable, 15 info.

| detector | hits | what it looks for |
|---|---:|---|
| `chain_surge` | 24 | a metric (DEX volume, fees, transactions, active addresses, TVL) against its trailing 28 days, empirical exceedance <= 5% |
| `chain_new` | 0 | first non-zero aggregator day within 60 days and already above the thin tier |
| `stable_inflow` | 7 | stablecoin float arriving on a chain, in total and per stablecoin |
| `dex_share_shift` | 1 | a chain's share of all DEX volume up x1.5 against its four-week share |
| `activity_divergence` | 1 | transactions and DEX volume moving apart over a week |
| `unregistered_active` | 3 | deep or tradeable chains with no direct probe yet |
| `probe_tx_surge` | 2 | the chain's own daily transactions (probe + backfill) x2 against its previous 14 days |
| `probe_new_asset` | 2 | an asset carrying >= $5M/day on the probe that the previous probes did not see |

### [high] TON dex last day: $13.1M/day vs $3.6M baseline (x3.6, market x0.69, rarer than 1% of its days)

`chain_surge:TON:dex:d1`

### [high] Cardano transactions 542.5k on 2026-10-08 vs a 33.5k median over the 13 days before (x16.2, market x1.08; 10-05 34.0k, 10-06 34.2k, 10-07 326.7k)

`probe_tx_surge:cardano`

### [notable] Tempo stablecoin float +$585.3M in 30 days ($145.4M -> $730.7M, +403%); largest step $309.8M on 2026-09-30

`stable_inflow:Tempo:30d`

### [notable] Plasma stablecoin float +$317.0M in 30 days ($1.1B -> $1.4B, +30%); largest step $137.0M on 2026-09-17

`stable_inflow:Plasma:30d`

### [notable] USDC on X Layer +$109.8M in 7 days ($17.9M -> $127.7M)

`stable_inflow:X Layer:USDC`

### [notable] OP Mainnet took 1.23% of all DEX volume this week, from 0.36% over the four weeks before (x3.4)

`dex_share_shift:OP Mainnet`

### [notable] OP Mainnet dex last 7 days: $94.6M/day vs $35.5M baseline (x2.7, market x0.81, rarer than 5% of its days); one day carries 99% of the excess

`chain_surge:OP Mainnet:dex:d7`

### [notable] OP Mainnet value without activity: transactions x0.99, DEX volume x2.66 (last 7 days vs 28 before)

`activity_divergence:OP Mainnet:value_without_activity`

### [notable] Near stablecoin float +$40.1M in 7 days ($88.7M -> $128.8M, +45%)

`stable_inflow:Near`

### [notable] USDe on Monad +$31.6M in 7 days ($69.7M -> $101.4M)

`stable_inflow:Monad:USDe`

### [notable] Starknet dex last day: $39.8M/day vs $9.7M baseline (x4.1, market x0.69, rarer than 4% of its days)

`chain_surge:Starknet:dex:d1`

### [notable] USDC on Near +$25.2M in 7 days ($63.4M -> $88.6M)

`stable_inflow:Near:USDC`

### [notable] QI on solana: $23.2M/day of transfers, absent from the previous 1 probe(s)

`probe_new_asset:solana:8TiMkgvsrat9tM2esko8zVTt99LZLpefUM4SnZaziXaQ`

### [notable] USDT on Monad +$21.3M in 7 days ($34.8M -> $56.0M)

`stable_inflow:Monad:USDT`

### [notable] WETH on arc: $11.7M/day of transfers, absent from the previous 1 probe(s)

`probe_new_asset:arc:0x128cc466b61f542da60c70e3aa11c10e19b84edb`

### [notable] Kaia dex last day: $4.0M/day vs $308.1k baseline (x12.9, market x0.69, rarer than 1% of its days)

`chain_surge:Kaia:dex:d1`

### [notable] Saga dex last day: $3.6M/day vs $686.1k baseline (x5.1, rarer than 4% of its days)

`chain_surge:Saga:dex:d1`

### [notable] OP Mainnet fees last 7 days: $379.5k/day vs $148.0k baseline (x2.6, market x0.93, rarer than 1% of its days); one day carries 65% of the excess

`chain_surge:OP Mainnet:fees:d7`

### [notable] OP Mainnet fees last day: $322.4k/day vs $116.9k baseline (x2.5, market x0.91, rarer than 3% of its days)

`chain_surge:OP Mainnet:fees:d1`

### [notable] Stable fees last day: $96.5k/day vs $10.4k baseline (x5.7, market x0.91, rarer than 1% of its days)

`chain_surge:Stable:fees:d1`

### [notable] Cronos fees last day: $34.5k/day vs $11.9k baseline (x2.4, market x0.91, rarer than 3% of its days)

`chain_surge:Cronos:fees:d1`

### [notable] Arbitrum daa last 7 days: 213.8k/day vs 118.1k baseline (x1.8, market x0.97, rarer than 2% of its days)

`chain_surge:Arbitrum:daa:d7`

### [notable] Near daa last 7 days: 126.7k/day vs 62.9k baseline (x2.0, market x0.97, rarer than 2% of its days)

`chain_surge:Near:daa:d7`

### [notable] World Chain daa last day: 41.2k/day vs 7.3k baseline (x5.5, market x0.92, rarer than 4% of its days)

`chain_surge:World Chain:daa:d1`

### [notable] Cronos transactions 90.9k on 2026-10-08 vs a 35.6k median over the 13 days before (x2.6, market x1.08; 10-05 30.4k, 10-06 70.6k, 10-07 60.2k)

`probe_tx_surge:cronos`


15 info-level hits omitted (`--all` lists them).
