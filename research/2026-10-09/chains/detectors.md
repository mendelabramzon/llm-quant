# New-activity sweep — research/2026-10-09/chains

Ran 8 detectors; 40 hit(s): 1 high, 24 notable, 15 info.

| detector | hits | what it looks for |
|---|---:|---|
| `chain_surge` | 18 | a metric (DEX volume, fees, transactions, active addresses, TVL) against its trailing 28 days, empirical exceedance <= 5% |
| `chain_new` | 0 | first non-zero aggregator day within 60 days and already above the thin tier |
| `stable_inflow` | 12 | stablecoin float arriving on a chain, in total and per stablecoin |
| `dex_share_shift` | 1 | a chain's share of all DEX volume up x1.5 against its four-week share |
| `activity_divergence` | 3 | transactions and DEX volume moving apart over a week |
| `unregistered_active` | 4 | deep or tradeable chains with no direct probe yet |
| `probe_tx_surge` | 2 | the chain's own daily transactions (probe + backfill) x2 against its previous 14 days |
| `probe_new_asset` | 0 | an asset carrying >= $5M/day on the probe that the previous probes did not see |

### [high] Cardano transactions 542.5k on 2026-10-08 vs a 33.5k median over the 13 days before (x16.2, market x1.08; 10-05 34.0k, 10-06 34.2k, 10-07 326.7k)

`probe_tx_surge:cardano`

### [notable] Tempo stablecoin float +$678.1M in 30 days ($81.6M -> $759.7M, +831%); largest step $309.8M on 2026-09-30

`stable_inflow:Tempo:30d`

### [notable] Plasma stablecoin float +$395.6M in 30 days ($1.0B -> $1.4B, +38%); largest step $137.0M on 2026-09-17

`stable_inflow:Plasma:30d`

### [notable] USDf on Ethereum +$344.9M in 7 days ($1.2B -> $1.5B)

`stable_inflow:Ethereum:USDf`

### [notable] XRPL stablecoin float +$214.7M in 7 days ($1.1B -> $1.3B, +20%)

`stable_inflow:XRPL`

### [notable] Arc stablecoin float +$109.9M in 7 days ($458.8M -> $568.8M, +24%)

`stable_inflow:Arc`

### [notable] USDC on X Layer +$104.3M in 7 days ($17.1M -> $121.4M)

`stable_inflow:X Layer:USDC`

### [notable] OP Mainnet took 1.15% of all DEX volume this week, from 0.35% over the four weeks before (x3.2)

`dex_share_shift:OP Mainnet`

### [notable] OP Mainnet dex last 7 days: $95.7M/day vs $35.4M baseline (x2.7, market x0.85, rarer than 4% of its days); one day carries 98% of the excess

`chain_surge:OP Mainnet:dex:d7`

### [notable] OP Mainnet value without activity: transactions x1.02, DEX volume x2.71 (last 7 days vs 28 before)

`activity_divergence:OP Mainnet:value_without_activity`

### [notable] Near stablecoin float +$43.6M in 7 days ($88.5M -> $132.1M, +49%)

`stable_inflow:Near`

### [notable] USDC on Near +$40.2M in 7 days ($48.5M -> $88.7M)

`stable_inflow:Near:USDC`

### [notable] USDe on Monad +$28.0M in 7 days ($70.6M -> $98.7M)

`stable_inflow:Monad:USDe`

### [notable] Starknet dex last day: $33.7M/day vs $9.3M baseline (x3.6, market x1.20, rarer than 4% of its days)

`chain_surge:Starknet:dex:d1`

### [notable] USDT on Monad +$22.4M in 7 days ($35.0M -> $57.4M)

`stable_inflow:Monad:USDT`

### [notable] USDC on Hedera +$21.6M in 7 days ($26.7M -> $48.3M)

`stable_inflow:Hedera:USDC`

### [notable] OUSD on Base +$20.1M in 7 days ($64.9M -> $85.0M)

`stable_inflow:Base:OUSD`

### [notable] Mantle value without activity: transactions x1.07, DEX volume x2.23 (last 7 days vs 28 before)

`activity_divergence:Mantle:value_without_activity`

### [notable] Saga dex last day: $3.6M/day vs $686.1k baseline (x5.1, rarer than 4% of its days)

`chain_surge:Saga:dex:d1`

### [notable] OP Mainnet fees last day: $487.3k/day vs $116.9k baseline (x2.7, market x1.13, rarer than 2% of its days)

`chain_surge:OP Mainnet:fees:d1`

### [notable] OP Mainnet fees last 7 days: $351.4k/day vs $152.1k baseline (x2.3, market x0.96, rarer than 2% of its days); one day carries 73% of the excess

`chain_surge:OP Mainnet:fees:d7`

### [notable] Arbitrum daa last day: 345.8k/day vs 115.8k baseline (x2.9, market x0.99, rarer than 1% of its days)

`chain_surge:Arbitrum:daa:d1`

### [notable] Arbitrum daa last 7 days: 209.2k/day vs 118.2k baseline (x1.8, market x0.99, rarer than 2% of its days)

`chain_surge:Arbitrum:daa:d7`

### [notable] Near daa last 7 days: 135.9k/day vs 61.4k baseline (x2.2, market x0.99, rarer than 1% of its days)

`chain_surge:Near:daa:d7`

### [notable] Cronos transactions 90.9k on 2026-10-08 vs a 35.6k median over the 13 days before (x2.6, market x1.08; 10-05 30.4k, 10-06 70.6k, 10-07 60.2k)

`probe_tx_surge:cronos`


15 info-level hits omitted (`--all` lists them).
