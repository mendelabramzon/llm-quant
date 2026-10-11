# New-activity sweep — research/2026-10-11/chains

Ran 8 detectors; 33 hit(s): 1 high, 17 notable, 15 info.

| detector | hits | what it looks for |
|---|---:|---|
| `chain_surge` | 21 | a metric (DEX volume, fees, transactions, active addresses, TVL) against its trailing 28 days, empirical exceedance <= 5% |
| `chain_new` | 0 | first non-zero aggregator day within 60 days and already above the thin tier |
| `stable_inflow` | 7 | stablecoin float arriving on a chain, in total and per stablecoin |
| `dex_share_shift` | 0 | a chain's share of all DEX volume up x1.5 against its four-week share |
| `activity_divergence` | 0 | transactions and DEX volume moving apart over a week |
| `unregistered_active` | 3 | deep or tradeable chains with no direct probe yet |
| `probe_tx_surge` | 1 | the chain's own daily transactions (probe + backfill) x2 against its previous 14 days |
| `probe_new_asset` | 1 | an asset carrying >= $5M/day on the probe that the previous probes did not see |

### [high] OP Mainnet fees last day: $455.5k/day vs $116.9k baseline (x3.9, market x0.79, rarer than 1% of its days)

`chain_surge:OP Mainnet:fees:d1`

### [notable] Tempo stablecoin float +$581.0M in 30 days ($151.1M -> $732.1M, +385%); largest step $309.8M on 2026-09-30

`stable_inflow:Tempo:30d`

### [notable] USDD on Ethereum +$211.0M in 7 days ($241.9M -> $452.9M)

`stable_inflow:Ethereum:USDD`

### [notable] USDC on X Layer +$108.7M in 7 days ($19.0M -> $127.7M)

`stable_inflow:X Layer:USDC`

### [notable] USDe on Monad +$32.0M in 7 days ($69.4M -> $101.4M)

`stable_inflow:Monad:USDe`

### [notable] USDC on Near +$25.2M in 7 days ($63.4M -> $88.6M)

`stable_inflow:Near:USDC`

### [notable] Near stablecoin float +$25.2M in 7 days ($103.7M -> $128.8M, +24%)

`stable_inflow:Near`

### [notable] CAP on bsc: $20.7M/day of transfers, absent from the previous 2 probe(s)

`probe_new_asset:bsc:0x99991c6aabba5a096f24f250b73580f5179b9999`

### [notable] USDT on Monad +$20.6M in 7 days ($33.4M -> $54.0M)

`stable_inflow:Monad:USDT`

### [notable] Saga dex last day: $3.6M/day vs $686.1k baseline (x5.1, rarer than 4% of its days)

`chain_surge:Saga:dex:d1`

### [notable] Arbitrum daa last 7 days: 214.8k/day vs 118.8k baseline (x1.8, market x0.96, rarer than 3% of its days)

`chain_surge:Arbitrum:daa:d7`

### [notable] Near daa last 7 days: 109.6k/day vs 66.5k baseline (x1.6, market x0.96, rarer than 4% of its days)

`chain_surge:Near:daa:d7`

### [notable] Ronin tx last day: 454.7k/day vs 145.4k baseline (x3.1, market x0.89, rarer than 1% of its days)

`chain_surge:Ronin:tx:d1`

### [notable] Ronin tx last 7 days: 256.1k/day vs 156.8k baseline (x1.6, market x0.90, rarer than 2% of its days)

`chain_surge:Ronin:tx:d7`

### [notable] Ronin daa last day: 312.8k/day vs 10.9k baseline (x28.6, market x0.91, rarer than 1% of its days)

`chain_surge:Ronin:daa:d1`

### [notable] Ronin daa last 7 days: 117.7k/day vs 16.2k baseline (x7.2, market x0.96, rarer than 2% of its days)

`chain_surge:Ronin:daa:d7`

### [notable] ApeChain tx last day: 236.3k/day vs 91.5k baseline (x2.5, market x0.89, rarer than 3% of its days)

`chain_surge:ApeChain:tx:d1`

### [notable] Kaia transactions 437.9k on 2026-10-09 vs a 140.4k median over the 14 days before (x3.1, market x0.93; 10-06 168.5k, 10-07 131.8k, 10-08 177.1k)

`probe_tx_surge:kaia`


15 info-level hits omitted (`--all` lists them).
