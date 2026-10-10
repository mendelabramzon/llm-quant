# Chain activity — 2026-10-09

Census of 569 chains from DefiLlama, growthepie, L2Beat, Blockchair, Tronscan, NEARBlocks, CoinGecko and Hyperliquid (days before 2026-10-09 UTC are complete); direct probe of 67 registry chains over 2026-10-08T00:00:00+00:00 → 2026-10-09T00:00:00+00:00 (24.0 h).

Tiers (how reasonable it is to trade there): deep 12, tradeable 28, token_only 39, thin 71, inactive 419.

## The list: chains by activity

Ranked by the mean percentile across DEX volume, fees, stablecoin float, TVL and transactions (at least three of the five measured). DEX, fees and transactions from the aggregators are 7-day daily averages, except where an aggregator has the probe's own day ("same day"); probe columns are the direct reading of one UTC day, with its standard error where it is a sample. Transfer value is net per transaction (see the probe docstring); `†` marks an asset whose estimate comes mostly from one sampled block, i.e. one large transfer scaled up.

| # | chain | family | tier | DEX/day | stables | TVL | fees/day | tx/day (aggregator) | tx/day (probe) | transfers/day (probe) | top assets moved (probe) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Solana | solana | deep | $2.1B | $16.1B | $6.3B | $15.6M |  | 177.6M ±5.2M | $27.7B | Kamino Reserve Collateral (SOL) Token $10.7B†, SOL $9.5B, usdc $4.4B† |
| 2 | BSC | evm | deep | $875.9M | $13.8B | $5.5B | $3.1M |  | 16.9M ±400.5k | $5.7B | USDT $2.6B, WBNB $678.7M, DRAMB $640.3M† |
| 3 | Base | evm | deep | $1.1B | $5.2B | $6.2B | $1.8M | 11.3M (growthepie, same day) | 12.3M ±1.1M | $129.3B | WETH $47.6B, USDC $43.5B, cbBTC $24.0B |
| 4 | Hyperliquid L1 (hyperevm) | evm | deep | $269.1M | $7.2B | $1.1B | $5.4M |  | 417.7k ±31.5k | $695.9M | USDC $256.7M, HYPE $235.4M†, WHYPE $144.3M |
| 5 | Ethereum | evm | deep | $1.5B | $146.1B | $51.4B | $11.4M | 1.8M (growthepie, same day) | 1.9M ±42.2k | $67.4B | USDC $30.8B, USDT $10.2B, DAI $9.0B† |
| 6 | Tron | tron | deep | $55.2M | $94.0B | $5.6B | $243.4k | 11.8M (tronscan, same day) | 11.4M ±129.6k | $37.8B | USDT $33.5B, TRX $4.0B, USDD $198.2M† |
| 7 | Robinhood Chain | evm | deep | $1.1B | $1.1B | $1.0B | $3.4M | 8.5M (growthepie, same day) | 8.1M ±361.7k | $2.8B | USDG $977.3M, WETH $767.2M, ETH $346.5M |
| 8 | Polygon | evm | deep | $217.6M | $2.9B | $684.4M | $1.2M | 5.5M (growthepie, same day) | 5.4M ±115.3k | $3.0B | USDC $1.8B, USDC $462.5M, pUSD $290.8M |
| 9 | Avalanche | evm | deep | $158.7M | $1.4B | $609.7M | $374.0k |  | 317.2k ±22.9k | $416.7M | AvalancheUSDC $179.6M, WAVAX $149.0M, USDT $38.1M |
| 10 | Arbitrum | evm | deep | $143.2M | $3.9B | $1.4B | $375.9k | 1.8M (growthepie, same day) | 2.1M ±197.6k | $1.1B | USDC $812.6M, WETH $256.7M, WBTC $125.1M† |
| 11 | Monad | evm | tradeable | $45.7M | $751.4M | $999.4M | $223.2k |  | 6.3M ±158.8k | $1.8B | aMonPT_AUSD_8OCT2026 $817.1M†, PT-AUSD-8OCT2026 $817.1M†, USDC $133.8M |
| 12 | OP Mainnet (optimism) | evm | tradeable | $95.7M | $636.1M | $451.3M | $351.4k | 1.7M (growthepie, same day) | 1.7M ±38.1k | $12.6B | USDC $5.8B, WETH $5.7B, velo $703.7M |
| 13 | Arc | evm | tradeable | $47.2M | $516.8M | $554.1M | $178.0k |  | 810.3k ±59.5k | $25.8M | USDC $25.0M, USDC $507.1k†, cirBTC $322.8k† |
| 14 | Sui | sui | tradeable | $42.8M | $490.4M | $518.4M | $114.1k |  | 7.4M ±163.9k | $1.9B | USDC $927.7M, SUI $879.6M†, DEEP $109.4M |
| 15 | Plasma | evm | tradeable | $5.4M | $1.3B | $498.4M | $131.9k |  | 600.1k ±16.4k | $114.4M | USDT0 $94.8M†, XPL $14.3M†, aPlaUSDT0 $2.3M† |
| 16 | Near | near | deep | $146.3M | $129.7M | $231.0M | $229.1k | 1.0M (nearblocks, same day) | 1.0M ±132.2k | $349.7M | NEAR $261.9M†, USDT $60.0M†, ETH $11.6M† |
| 17 | X Layer | evm | deep | $18.3M | $1.6B | $162.7M | $28.0k | 845.2k (l2beat, same day) | 822.1k ±24.8k | $125.5M | USDC $53.7M†, USDG $14.9M, AAPLx $12.6M† |
| 18 | Stellar | stellar | tradeable | $2.1M | $955.8M | $250.2M | $190.0k | 4.7M (blockchair-24h) | 5.1M | $232.8M | USDC $152.8M†, XLM $36.8M, sUSD $25.3M† |
| 19 | TON | ton | tradeable | $3.8M | $719.0M | $53.1M | $1.2M |  | 3.4M ±188.1k | $172.7M | USD₮ $96.1M, TON $69.7M, tsTON $4.8M† |
| 20 | XRPL | xrpl | tradeable | $6.1M | $1.2B | $41.8M | $30.6k | 2.3M (blockchair-24h) | 2.4M ±377.7k | $666.3M | XRP $652.9M, RLUSD $13.4M |
| 21 | Aptos | aptos | tradeable | $5.4M | $1.0B | $49.7M | $53.5k |  | 10.2M | $186.8M | USDt $186.6M†, USDC $125.0k†, APT $61.3k† |
| 22 | Sei | evm | tradeable | $7.4M | $308.7M | $32.8M | $45.7k |  | 17.3k ±4.5k | $5.1M | USDC $2.5M†, wSEI $2.4M, USDT0 $73.2k† |
| 23 | Chainflip |  | thin | $17.0M | - | $16.6M | $54.5k |  |  |  |  |
| 24 | Ink | evm | tradeable | $3.1M | $179.0M | $206.9M | $150.2k | 333.9k (growthepie, same day) | 353.8k ±49.2k | $3.4B | USDC $1.5B†, USDT0 $763.1M, WETH $560.6M |
| 25 | THORChain | cosmos | token_only | $26.2M | - | $36.1M | $9.7k |  | 190.3k | $3.8M | RUNE $3.8M |
| 26 | Canton |  | token_only | $38.5M | - | $12.2M | $16.9k |  |  |  |  |
| 27 | Starknet | starknet | tradeable | $17.2M | $152.9M | $165.1M | $57.3k | 187.9k (growthepie, same day) | 184.4k ±23.2k | $248.5M | STRK $119.7M, ETH $58.3M†, ZEC $46.9M† |
| 28 | Flare | evm | tradeable | $5.3M | $48.5M | $125.1M | $21.6k |  | 553.0k ±98.2k | $67.6M | FXRP $43.4M, WFLR $7.3M†, sFLR $7.2M† |
| 29 | Cronos | evm | tradeable | $2.4M | $138.5M | $153.0M | $16.6k |  | 90.9k ±34.2k | $9.1M | WCRO $3.3M, CRO $1.5M, USDC $1.4M |
| 30 | Cardano | cardano | tradeable | $4.0M | $71.2M | $65.4M | $32.0k | 312.5k (blockchair-24h) | 542.5k | $27.8M | ADA $17.9M, NIGHT $4.0M, DJED $2.5M† |
| 31 | Mantle | evm | tradeable | $5.4M | $553.9M | $107.3M | $61.3k | 23.7k (growthepie, same day) | 18.8k ±2.7k | $10.5M | WMNT $3.5M†, USDT $2.4M, MNT $2.0M† |
| 32 | Unichain | evm | tradeable | $8.9M | $27.7M | $27.3M | $20.3k | 689.0k (growthepie, same day) | 702.9k ±15.5k | $50.0M | USDC $28.8M, HYPE $10.9M, WETH $5.2M |
| 33 | PulseChain | evm | tradeable | $3.7M | $32.7M | $70.9M | $10.1k |  | 437.2k ±33.4k | $11.7M | PCOCK $3.7M†, WPLS $1.5M†, USDC $1.1M† |
| 34 | Bitcoin | utxo | token_only | $393.6k | - | $4.4B | $8.0k | 671.4k (blockchair-24h) | 630.1k | $89.4B (gross) | BTC $89.4B |
| 35 | Gnosis | evm | tradeable | $3.4M | $15.4M | $95.8M | $14.4k | 459.2k (l2beat, same day) | 474.0k ±17.7k | $22.1M | EURe $5.7M†, wstETH $5.0M, sDAI $5.0M |
| 36 | Sonic | evm | tradeable | $1.6M | $158.5M | $17.9M | $6.5k |  | 131.4k ±16.0k | $46.1M | wS $19.1M, WETH $15.0M, USDC $11.1M |
| 37 | Hedera | hedera | tradeable | $2.6M | $48.3M | $37.1M | $7.1k |  | 807.4k | $42.3M | HBAR $29.4M†, USDC $6.4M, WHBAR $6.4M |
| 38 | Celo | evm | tradeable | $1.2M | $113.6M | $17.8M | $4.0k | 896.7k (growthepie, same day) | 905.0k ±21.2k | $11.1M | CELO $3.7M†, BRLA $3.6M†, celo $1.9M† |
| 39 | BOT Chain |  | thin | $2.1M | - | $31.9M | $6.5k |  |  |  |  |
| 40 | Stacks |  | tradeable | $3.7M | $11.6M | $93.3M | $7.7k |  |  |  |  |
| 41 | edgeX L1 |  | thin | $35.4M | $2.4M | - | $88.1k |  |  |  |  |
| 42 | Provenance |  | tradeable | $19.7M | $469.9M | $131.8M | $34 |  |  |  |  |
| 43 | Algorand | algorand | token_only | $478.7k | $62.7M | $35.4M | $7.5k |  | 1.3M | $445.8M | USDC $355.9M†, ALGO $64.4M, xALGO $24.8M† |
| 44 | Flow |  | thin | $506.4k | $71.6M | $12.1M | $8.4k |  |  |  |  |
| 45 | MegaETH | evm | thin | $675.9k | $19.1M | $13.0M | $7.6k | 1.1M (growthepie, same day) | 2.0M ±20.4k | $458.4k | USDm $297.7k, MEGA $128.6k, WETH $32.1k† |
| 46 | Vaulta |  | thin | $5.7M | $1.7M | $47.6M | $14.2k |  |  |  |  |
| 47 | Berachain | evm | thin | $696.3k | $58.7M | $38.0M | $3.5k |  | 134.8k ±27.1k | $704.2k | BERA $695.4k†, sWBERA $4.5k†, WBERA $4.2k† |
| 48 | Dexalot |  | thin | $32.5M | - | $2.0M | $3.5k |  |  |  |  |
| 49 | World Chain | evm | token_only | $623.3k | $17.0M | $40.9M | $3.8k | 642.5k (growthepie, same day) | 657.9k ±15.1k | $18.5M | WLD $14.8M, USDC.e $2.6M†, Re7USDC $445.3k† |
| 50 | Hydration |  | tradeable | $1.0M | $13.6M | $55.5M | $5.0k |  |  |  |  |
| 51 | Tempo | evm | tradeable | $1.3M | $730.8M | $106.4M | $55 |  | 44.2k ±6.0k | $24.1M | USDC.e $19.9M†, USDT0 $4.0M†, pathUSD $130.2k† |
| 52 | ZKsync Era | evm | token_only | $411.2k | $36.1M | $15.0M | $67.4k | 17.1k (growthepie, same day) | 16.8k ±782 | $2.5M | zk $1.4M, WETH $347.9k, USDC $332.5k |
| 53 | ADI |  | thin | $2.5M | - | $1.5M | $72.6k | 20.4k (l2beat) |  |  |  |
| 54 | Abstract | evm | thin | $1.8M | $3.9M | $4.9M | $85.0k | 139.2k (l2beat, same day) | 140.8k ±4.8k | $6.6M | USDC.e $1.9M, WETH $1.4M, ETH $1.2M |
| 55 | Osmosis | cosmos | thin | $567.0k | $17.2M | $11.4M | $5.3k |  | 64.5k ±7.4k | $12.3M | USDC.inj $5.4M†, USDC.n $2.1M, ATOM $1.9M |
| 56 | Rootstock | evm | thin | $456.4k | $11.4M | $82.1M | $3.0k |  | 6.9k ±403 | $7.6k | RBTC $7.6k† |
| 57 | Kaia | evm | token_only | $320.0k | $241.9M | $9.1M | $1.3k |  | 177.1k ±31.2k | $39.2M | USD₮ $36.2M, WKLAY $1.1M, KAIA $1.0M† |
| 58 | Katana | evm | thin | $439.3k | $10.5M | $40.8M | $7.9k | 35.7k (l2beat, same day) | 38.7k ±7.0k | $117.8M | vbUSDC $67.3M†, vbETH $38.2M†, KAT $12.1M† |
| 59 | Mixin |  | thin | $32.9k | $34.5M | $77.1M | - |  |  |  |  |
| 60 | Morph |  | token_only | $404.5k | $31.2M | $87.2M | $4.5k | 12.5k (l2beat) |  |  |  |

Probed but outside the aggregator ranking: CosmosHub 15.7k tx/day (exact-blocks); Celestia 134.6k tx/day (sampled-blocks); Noble 2.4k tx/day (exact-index); dYdX 715.3k tx/day (sampled-blocks); Hyperliquid (HyperCore) 2.1B tx/day (sampled-blocks)

## The list, measured directly: every probed chain by transactions

One row per registry chain the probe read, busiest first. `$/tx` is net transfer value per transaction: a chain with millions of transactions and cents per transaction is busy with bots, not with money. `bookkeeping` is the share of transactions sent to registry-listed oracle, validator-signing or block-builder contracts — real transactions that are not activity (the headline keeps them, as L2Beat does). `top target` is the contract that received the largest share of transactions (and of value): one address carrying most of a chain is one actor, however large the totals.

| chain | family | tier | tx/day | method | bookkeeping | net transfers/day | $/tx | top target by txs | top target by value |
|---|---|---|---:|---|---:|---:|---:|---|---|
| Hyperliquid (HyperCore) | hyperliquid |  | 2.1B ±201.1M | sampled-blocks |  | $11.5B (traded) | - |  |  |
| Solana | solana | deep | 177.6M ±5.2M | sampled-blocks |  | $27.7B | $156.01 |  |  |
| BSC | evm | deep | 16.9M ±400.5k | sampled-blocks |  | $5.7B | $335.26 | `0x55d398326f` 11% | `0x55d398326f` 20% |
| Base | evm | deep | 12.3M ±1.1M | sampled-blocks |  | $129.3B | $10.5k | `0xcab0478549` 9% | `0x61040e143a` 45% |
| Tron | tron | deep | 11.4M ±129.6k | sampled-blocks |  | $37.8B | $3303.87 | `0xa614f803b6` 20% | `0xa614f803b6` 95% |
| Aptos | aptos | tradeable | 10.2M | exact-versions minus sampled system share |  | $186.8M | $18.32 |  |  |
| Robinhood Chain | evm | deep | 8.1M ±361.7k | sampled-blocks |  | $2.8B | $353.34 | `0xc33acc9394` 4% | `0x520ed46786` 14% |
| Sui | sui | tradeable | 7.4M ±163.9k | exact-counter x sampled user share |  | $1.9B | $259.50 |  |  |
| Monad | evm | tradeable | 6.3M ±158.8k | sampled-blocks |  | $1.8B | $292.59 | `0xd32edf6642` 24% | `0x69a5f9ad4f` 90% |
| Polygon | evm | deep | 5.4M ±115.3k | sampled-blocks |  | $3.0B | $551.98 | `0xe111180000` 19% | `0x3c499c542c` 41% |
| Stellar | stellar | tradeable | 5.1M | exact-blocks |  | $232.8M | $45.87 |  |  |
| TON | ton | tradeable | 3.4M ±188.1k | sampled-blocks |  | $172.7M | $50.35 |  |  |
| XRPL | xrpl | tradeable | 2.4M ±377.7k | sampled-blocks |  | $666.3M | $274.13 |  |  |
| Arbitrum | evm | deep | 2.1M ±197.6k | sampled-blocks |  | $1.1B | $511.85 | `0x12f51e668e` 16% | `0x93c30e6e09` 25% |
| MegaETH | evm | thin | 2.0M ±20.4k | sampled-blocks | 87% | $458.4k | $0.23 | `0x6342000000` 44% | `0x4256356011` 20% |
| Ethereum | evm | deep | 1.9M ±42.2k | sampled-blocks |  | $67.4B | $36.1k | `0xdac17f958d` 17% | `0xa0b86991c6` 39% |
| Injective | cosmos | tradeable | 1.8M | exact-index |  | $818.1M | $456.92 |  |  |
| XDC | evm | token_only | 1.8M ±242.8k | sampled-blocks | 56% | $2.8M | $1.58 | `0x0000000000` 56% | `0x26bcd76624` 89% |
| OP Mainnet (optimism) | evm | tradeable | 1.7M ±38.1k | sampled-blocks |  | $12.6B | $7460.42 | `0x1e04602a8b` 20% | `0xc26ae9339b` 32% |
| opBNB | evm | inactive | 1.3M ±90.6k | sampled-blocks |  | $63.3k | $0.05 | `0xa596e82b0e` 22% | `0x9e5aac1ba1` 100% |
| Algorand | algorand | token_only | 1.3M | exact-counter |  | $445.8M | $339.14 |  |  |
| Near | near | deep | 1.0M ±132.2k | sampled-blocks |  | $349.7M | $336.91 |  |  |
| Celo | evm | tradeable | 905.0k ±21.2k | sampled-blocks |  | $11.1M | $12.28 | `0xbedaccbd65` 45% | `0xa5e1a81738` 48% |
| X Layer | evm | deep | 822.1k ±24.8k | sampled-blocks |  | $125.5M | $152.70 | `0x6558dbe4c1` 37% | `0xb6ceceab30` 40% |
| Arc | evm | tradeable | 810.3k ±59.5k | sampled-blocks |  | $25.8M | $31.82 | `0x7e032e56c6` 20% | `0x278d858f05` 63% |
| Hedera | hedera | tradeable | 807.4k | exact-blocks |  | $42.3M | $52.36 |  |  |
| dYdX | cosmos | inactive | 715.3k ±1.8k | sampled-blocks |  | $189 | $0.00 |  |  |
| Unichain | evm | tradeable | 702.9k ±15.5k | sampled-blocks | 74% | $50.0M | $71.15 | `0x3c3a8a41e0` 61% | `0x6f16381f6b` 24% |
| World Chain | evm | token_only | 657.9k ±15.1k | sampled-blocks |  | $18.5M | $28.09 | `0x0000000071` 65% | `0x2cfc85d8e4` 68% |
| Bitcoin | utxo | token_only | 630.1k | exact-blocks |  | $89.4B (gross) | - |  |  |
| Plasma | evm | tradeable | 600.1k ±16.4k | sampled-blocks |  | $114.4M | $190.63 | `0x334987c805` 48% | `0xb8ce59fc37` 90% |
| Flare | evm | tradeable | 553.0k ±98.2k | sampled-blocks | 86% | $67.6M | $122.21 | `0x2ca6571daa` 86% | `0xd1b7a5efa9` 59% |
| Cardano | cardano | tradeable | 542.5k | exact-blocks |  | $27.8M | $51.20 |  |  |
| Gnosis | evm | tradeable | 474.0k ±17.7k | sampled-blocks |  | $22.1M | $46.53 | `0x1d4bceb37b` 10% | `0xd546f95c8a` 23% |
| PulseChain | evm | tradeable | 437.2k ±33.4k | sampled-blocks |  | $11.7M | $26.72 | `0x847aeff857` 4% | `0xc10a4ed9b4` 33% |
| Hyperliquid L1 (hyperevm) | evm | deep | 417.7k ±31.5k | sampled-blocks |  | $695.9M | $1666.13 | `0xcf6848bc4b` 9% | `0xafbe3a3c99` 20% |
| Ronin | evm | thin | 389.7k ±8.6k | sampled-blocks |  | $3.4M | $8.71 | `0x43f18c0752` 74% | `0xa8754b9fa1` 55% |
| Ink | evm | tradeable | 353.8k ±49.2k | sampled-blocks |  | $3.4B | $9732.97 | `0x2fa8df1bad` 27% | `0x1b35d13a2e` 56% |
| Blast | evm | thin | 320.3k ±7.3k | sampled-blocks |  | $957.6k | $2.99 | `0x848e45b91d` 70% | `0x5ff137d4b0` 96% |
| Avalanche | evm | deep | 317.2k ±22.9k | sampled-blocks |  | $416.7M | $1313.93 | `0xe844701934` 7% | `0xff2befc4ff` 20% |
| Soneium | evm | thin | 287.3k ±11.1k | sampled-blocks |  | $580.0k | $2.02 | `0x0000000071` 52% | `0x4cd00e3876` 60% |
| Plume Mainnet | evm | token_only | 206.4k | sampled-blocks |  | $205.2k | $0.99 | `0xee96619e24` 97% | `0x1716058d72` 100% |
| THORChain | cosmos | token_only | 190.3k | exact-blocks |  | $3.8M | $19.85 |  |  |
| Starknet | starknet | tradeable | 184.4k ±23.2k | sampled-blocks |  | $248.5M | $1347.70 |  |  |
| Kaia | evm | token_only | 177.1k ±31.2k | sampled-blocks |  | $39.2M | $221.19 | `0x6823622f0a` 12% | `0xd077a40096` 92% |
| Litecoin | utxo | token_only | 156.7k | exact-blocks |  | $2.1B (gross) | - |  |  |
| Abstract | evm | thin | 140.8k ±4.8k | sampled-blocks |  | $6.6M | $46.77 | `0x99bb83ae9b` 19% | `0xec23aad2c2` 18% |
| Berachain | evm | thin | 134.8k ±27.1k | sampled-blocks |  | $704.2k | $5.22 | `0xd2f19a79b0` 32% | `0x9ef0a91974` 51% |
| Celestia | cosmos | token_only | 134.6k ±226 | sampled-blocks |  | $5.7M | $42.51 |  |  |
| Sonic | evm | tradeable | 131.4k ±16.0k | sampled-blocks |  | $46.1M | $350.85 | `0xeac0722f31` 13% | `0x12e66c8f21` 87% |
| Tezos | tezos | thin | 105.3k | exact-indexer |  | $1.9M | $17.89 |  |  |
| Cronos | evm | tradeable | 90.9k ±34.2k | sampled-blocks |  | $9.1M | $100.27 | `0x7edaf2b98d` 28% | `0x895adcd554` 24% |
| Osmosis | cosmos | thin | 64.5k ±7.4k | sampled-blocks |  | $12.3M | $190.35 |  |  |
| Tempo | evm | tradeable | 44.2k ±6.0k | sampled-blocks |  | $24.1M | $545.71 | `create` 70% | `create` 83% |
| CORE | evm | thin | 40.0k ±1.8k | sampled-blocks |  | $832.5k | $20.80 | `0x0000000000` 72% | `0x47ebcf2742` 33% |
| Katana | evm | thin | 38.7k ±7.0k | sampled-blocks |  | $117.8M | $3040.75 | `0x62230cea61` 55% | `0x2659c6085d` 99% |
| Doge (dogecoin) | utxo | token_only | 18.9k | aggregator-24h |  | $1.1B (gross) | - |  |  |
| Mantle | evm | tradeable | 18.8k ±2.7k | sampled-blocks |  | $10.5M | $558.86 | `0x1908533788` 26% | `0xbdff0c1c8b` 32% |
| Sei | evm | tradeable | 17.3k ±4.5k | sampled-blocks |  | $5.1M | $295.53 | `0x11da6463d6` 32% | `0x11da6463d6` 50% |
| ZKsync Era | evm | token_only | 16.8k ±782 | sampled-blocks |  | $2.5M | $146.64 | `0x5a7d6b2f92` 6% | `0x5a7d6b2f92` 55% |
| CosmosHub | cosmos | token_only | 15.7k | exact-blocks |  | $22.6M | $1438.23 |  |  |
| Bitcoincash | utxo | token_only | 15.1k | aggregator-24h |  | $170.7M (gross) | - |  |  |
| Linea | evm | thin | 14.6k ±746 | sampled-blocks |  | $3.6M | $244.51 | `0xd8850c39d6` 6% | `0x1789e00436` 30% |
| Scroll | evm | token_only | 13.1k ±434 | sampled-blocks |  | $978.5k | $74.54 | `0x5300000000` 18% | `0x04a700f832` 31% |
| Zcash | utxo | token_only | 8.1k | aggregator-24h |  | $1.9B (gross) | - |  |  |
| Rootstock | evm | thin | 6.9k ±403 | sampled-blocks |  | $7.6k | $1.10 | `0x0000000000` 41% |  |
| Noble | cosmos | thin | 2.4k | exact-index |  | $897.6k | $381.94 |  |  |

## New activity

Detector hits, most severe first (info-level in `detectors.md`). Every hit carries its chain's tier so a surge on an untradeable chain reads as such.

- **[high]** Cardano transactions 542.5k on 2026-10-08 vs a 33.5k median over the 13 days before (x16.2, market x1.08; 10-05 34.0k, 10-06 34.2k, 10-07 326.7k)  `probe_tx_surge:cardano`
- **[notable]** Tempo stablecoin float +$678.1M in 30 days ($81.6M -> $759.7M, +831%); largest step $309.8M on 2026-09-30  `stable_inflow:Tempo:30d`
- **[notable]** Plasma stablecoin float +$395.6M in 30 days ($1.0B -> $1.4B, +38%); largest step $137.0M on 2026-09-17  `stable_inflow:Plasma:30d`
- **[notable]** USDf on Ethereum +$344.9M in 7 days ($1.2B -> $1.5B)  `stable_inflow:Ethereum:USDf`
- **[notable]** XRPL stablecoin float +$214.7M in 7 days ($1.1B -> $1.3B, +20%)  `stable_inflow:XRPL`
- **[notable]** Arc stablecoin float +$109.9M in 7 days ($458.8M -> $568.8M, +24%)  `stable_inflow:Arc`
- **[notable]** USDC on X Layer +$104.3M in 7 days ($17.1M -> $121.4M)  `stable_inflow:X Layer:USDC`
- **[notable]** OP Mainnet took 1.15% of all DEX volume this week, from 0.35% over the four weeks before (x3.2)  `dex_share_shift:OP Mainnet`
- **[notable]** OP Mainnet dex last 7 days: $95.7M/day vs $35.4M baseline (x2.7, market x0.85, rarer than 4% of its days); one day carries 98% of the excess  `chain_surge:OP Mainnet:dex:d7`
- **[notable]** OP Mainnet value without activity: transactions x1.02, DEX volume x2.71 (last 7 days vs 28 before)  `activity_divergence:OP Mainnet:value_without_activity`
- **[notable]** Near stablecoin float +$43.6M in 7 days ($88.5M -> $132.1M, +49%)  `stable_inflow:Near`
- **[notable]** USDC on Near +$40.2M in 7 days ($48.5M -> $88.7M)  `stable_inflow:Near:USDC`
- **[notable]** USDe on Monad +$28.0M in 7 days ($70.6M -> $98.7M)  `stable_inflow:Monad:USDe`
- **[notable]** Starknet dex last day: $33.7M/day vs $9.3M baseline (x3.6, market x1.20, rarer than 4% of its days)  `chain_surge:Starknet:dex:d1`
- **[notable]** USDT on Monad +$22.4M in 7 days ($35.0M -> $57.4M)  `stable_inflow:Monad:USDT`
- **[notable]** USDC on Hedera +$21.6M in 7 days ($26.7M -> $48.3M)  `stable_inflow:Hedera:USDC`
- **[notable]** OUSD on Base +$20.1M in 7 days ($64.9M -> $85.0M)  `stable_inflow:Base:OUSD`
- **[notable]** Mantle value without activity: transactions x1.07, DEX volume x2.23 (last 7 days vs 28 before)  `activity_divergence:Mantle:value_without_activity`
- **[notable]** Saga dex last day: $3.6M/day vs $686.1k baseline (x5.1, rarer than 4% of its days)  `chain_surge:Saga:dex:d1`
- **[notable]** OP Mainnet fees last day: $487.3k/day vs $116.9k baseline (x2.7, market x1.13, rarer than 2% of its days)  `chain_surge:OP Mainnet:fees:d1`
- **[notable]** OP Mainnet fees last 7 days: $351.4k/day vs $152.1k baseline (x2.3, market x0.96, rarer than 2% of its days); one day carries 73% of the excess  `chain_surge:OP Mainnet:fees:d7`
- **[notable]** Arbitrum daa last day: 345.8k/day vs 115.8k baseline (x2.9, market x0.99, rarer than 1% of its days)  `chain_surge:Arbitrum:daa:d1`
- **[notable]** Arbitrum daa last 7 days: 209.2k/day vs 118.2k baseline (x1.8, market x0.99, rarer than 2% of its days)  `chain_surge:Arbitrum:daa:d7`
- **[notable]** Near daa last 7 days: 135.9k/day vs 61.4k baseline (x2.2, market x0.99, rarer than 1% of its days)  `chain_surge:Near:daa:d7`
- **[notable]** Cronos transactions 90.9k on 2026-10-08 vs a 35.6k median over the 13 days before (x2.6, market x1.08; 10-05 30.4k, 10-06 70.6k, 10-07 60.2k)  `probe_tx_surge:cronos`

15 info-level hits (drops, divergences, thin chains, unregistered tradeable chains) are listed in `detectors.md`.

## What moved, by asset (probe)

Transfer value per day, net per transaction: what each account gained, so routed hops and flash-loan round trips cancel while both legs of a swap count (UTXO chains and Blockchair rows are gross outputs; Hyperliquid is traded notional). ± is one standard error of the stratified estimate; `top` is the share of the sampled value that came from one block (above 0.5 the figure is one large transfer scaled up).

| chain | asset | class | USD/day | ± | transfers/day | top |
|---|---|---|---:|---:|---:|---:|
| hyperliquid | BTC | btc | $3.4B | $0 |  |  |
| hyperliquid | ETH | eth | $1.8B | $0 |  |  |
| hyperliquid | HYPE | native | $530.7M | $0 |  |  |
| hyperliquid | xyz:XYZ100 | other | $454.8M | $0 |  |  |
| hyperliquid | ZEC | other | $444.5M | $0 |  |  |
| solana | Kamino Reserve Collateral (SOL) Token | other | $10.7B | $6.2B | 5.4k | 0.71 |
| solana | SOL | native | $9.5B | $3.0B | 131.2M | 0.27 |
| solana | usdc | usd_stable | $4.4B | $2.5B | 10.2M | 0.56 |
| solana | SOL | native | $1.7B | $194.1M | 60.4M | 0.07 |
| solana | usdt | usd_stable | $292.5M | $44.4M | 1.2M | 0.07 |
| bsc | USDT | usd_stable | $2.6B | $263.6M | 15.0M | 0.05 |
| bsc | WBNB | native | $678.7M | $109.7M | 2.6M | 0.08 |
| bsc | DRAMB | other | $640.3M | $641.6M | 959 | 1.00 |
| bsc | USDC | usd_stable | $619.7M | $386.0M | 1.2M | 0.62 |
| bsc | BNB | native | $235.2M | $38.6M |  | 0.14 |
| base | WETH | eth | $47.6B | $2.1B | 2.0M | 0.02 |
| base | USDC | usd_stable | $43.5B | $3.4B | 4.5M | 0.07 |
| base | cbBTC | btc | $24.0B | $1.5B | 613.0k | 0.02 |
| base | AERO | other | $2.8B | $438.4M | 619.1k | 0.09 |
| base | MORPHO | other | $1.0B | $207.5M | 28.7k | 0.12 |
| tron | USDT | usd_stable | $33.5B | $4.7B | 2.3M | 0.09 |
| tron | TRX | native | $4.0B | $890.7M |  | 0.24 |
| tron | USDD | usd_stable | $198.2M | $137.6M | 2.0k | 0.65 |
| tron | BTC | btc | $44.0M | $43.9M | 288 | 1.00 |
| tron | WTRX | native | $27.8M | $26.5M | 5.5k | 0.95 |
| aptos | USDt | usd_stable | $186.6M | $135.4M | 85.7k | 0.62 |
| aptos | USDC | usd_stable | $125.0k | $78.0k | 228.4k | 0.57 |
| aptos | APT | native | $61.3k | $61.7k | 28.6k | 1.00 |
| robinhood | USDG | usd_stable | $977.3M | $157.3M | 2.2M | 0.08 |
| robinhood | WETH | eth | $767.2M | $79.6M | 2.4M | 0.04 |
| robinhood | ETH | eth | $346.5M | $84.1M |  | 0.20 |
| robinhood | PONS | other | $162.1M | $106.8M | 96.7k | 0.63 |
| robinhood | NVDA | other | $91.2M | $57.6M | 103.7k | 0.61 |
| sui | USDC | usd_stable | $927.7M | $520.5M | 102.4k | 0.47 |
| sui | SUI | native | $879.6M | $752.3M | 797.6k | 0.85 |
| sui | DEEP | other | $109.4M | $58.8M | 22.0k | 0.34 |
| sui | WAL | other | $4.6M | $3.4M | 23.8k | 0.76 |
| sui | MAGMA | other | $1.1M | $572.8k | 7.3k | 0.30 |
| monad | aMonPT_AUSD_8OCT2026 | other | $817.1M | $817.5M | 715 | 1.00 |
| monad | PT-AUSD-8OCT2026 | other | $817.1M | $817.5M | 715 | 1.00 |
| monad | USDC | usd_stable | $133.8M | $62.5M | 438.5k | 0.34 |
| monad | AUSD | usd_stable | $21.6M | $20.7M | 26.5k | 0.95 |
| monad | MON | native | $21.3M | $14.4M |  | 0.95 |
| polygon | USDC | usd_stable | $1.8B | $968.4M | 971.0k | 0.44 |
| polygon | USDC | usd_stable | $462.5M | $151.6M | 4.1M | 0.27 |
| polygon | pUSD | other | $290.8M | $126.5M | 7.6M | 0.44 |
| polygon | USDT0 | usd_stable | $160.5M | $29.2M | 463.6k | 0.09 |
| polygon | DAI | usd_stable | $76.8M | $13.5M | 1.2M | 0.12 |
| stellar | USDC | usd_stable | $152.8M | $116.7M | 150.0k | 0.75 |
| stellar | XLM | native | $36.8M | $12.4M | 212.8k | 0.31 |
| stellar | sUSD | other | $25.3M | $25.0M | 9.8k | 0.98 |
| stellar | AQUA | other | $17.0M | $16.3M | 17.6k | 0.95 |
| stellar | VELO | other | $391.2k | $363.5k | 2.6k | 0.92 |
| ton | USD₮ | usd_stable | $96.1M | $48.4M | 140.2k | 0.48 |
| ton | TON | native | $69.7M | $22.2M | 2.5M | 0.23 |
| ton | tsTON | other | $4.8M | $2.9M | 4.6k | 0.51 |
| ton | UTYA | other | $1.3M | $1.2M | 880 | 0.92 |
| ton | DOGS | other | $233.7k | $136.6k | 1.8k | 0.47 |
| xrpl | XRP | native | $652.9M | $258.0M | 348.4k | 0.34 |
| xrpl | RLUSD | usd_stable | $13.4M | $5.1M | 266.4k | 0.29 |
| arbitrum | USDC | usd_stable | $812.6M | $285.0M | 1.2M | 0.29 |
| arbitrum | WETH | eth | $256.7M | $64.9M | 476.0k | 0.17 |
| arbitrum | WBTC | btc | $125.1M | $71.4M | 103.0k | 0.56 |
| arbitrum | USDT0 | usd_stable | $76.3M | $22.4M | 306.5k | 0.26 |
| arbitrum | ARB | other | $10.8M | $2.6M | 110.1k | 0.10 |
| megaeth | USDm | usd_stable | $297.7k | $79.2k | 113.4k | 0.17 |
| megaeth | MEGA | other | $128.6k | $63.7k | 7.1k | 0.38 |
| megaeth | WETH | eth | $32.1k | $22.5k | 4.8k | 0.66 |
| megaeth | ETH | eth | $31 | $26 |  | 0.81 |
| megaeth | BTC.b | btc | $0 | $0 | 432 |  |
| ethereum | USDC | usd_stable | $30.8B | $7.9B | 619.4k | 0.26 |
| ethereum | USDT | usd_stable | $10.2B | $1.4B | 573.5k | 0.07 |
| ethereum | DAI | usd_stable | $9.0B | $6.9B | 17.3k | 0.75 |
| ethereum | ETH | eth | $4.3B | $1.2B |  | 0.27 |
| ethereum | stETH | eth | $2.7B | $2.5B | 2.1k | 0.94 |
| injective | USDC.inj | usd_stable | $702.6M | $280.4M | 924.6k | 0.27 |
| injective | INJ | native | $90.0M | $80.1M | 2.0M | 0.87 |
| injective | WETH | eth | $25.4M | $3.7M | 63.2k | 0.04 |
| xdc | WXDC | native | $1.2M | $458.2k | 20.2k | 0.20 |
| xdc | GAMA | other | $604.0k | $415.2k | 9.9k | 0.50 |
| xdc | DOPU | other | $596.7k | $299.1k | 3.5k | 0.28 |
| xdc | XDC | native | $239.5k | $175.5k |  | 0.72 |
| xdc | USDC | usd_stable | $204.1k | $104.3k | 6.1k | 0.35 |
| optimism | USDC | usd_stable | $5.8B | $192.6M | 1.2M | 0.02 |
| optimism | WETH | eth | $5.7B | $280.1M | 770.0k | 0.02 |
| optimism | velo | other | $703.7M | $24.6M | 981.3k | 0.02 |
| optimism | OP | other | $341.0M | $58.0M | 391.6k | 0.17 |
| optimism | WBTC | btc | $33.4M | $7.3M | 48.0k | 0.14 |
| opbnb | USDT | usd_stable | $63.2k | $45.0k | 3.5k | 0.55 |
| opbnb | BNB | native | $25 | $8 |  | 0.26 |
| algorand | USDC | usd_stable | $355.9M | $264.4M | 132.3k | 0.68 |
| algorand | ALGO | native | $64.4M | $27.6M | 217.8k | 0.38 |
| algorand | xALGO | other | $24.8M | $24.7M | 1.6k | 1.00 |
| algorand | TALGO | other | $262.4k | $133.4k | 5.2k | 0.38 |
| algorand | goBTC | other | $151.7k | $101.7k | 20.7k | 0.66 |
| near | NEAR | native | $261.9M | $197.7M | 214.6k | 0.71 |
| near | USDT | usd_stable | $60.0M | $55.1M | 10.9k | 0.90 |
| near | ETH | eth | $11.6M | $8.6M | 10.9k | 0.66 |
| near | wNEAR | native | $10.3M | $5.1M | 103.2k | 0.46 |
| near | USDC | usd_stable | $4.3M | $1.5M | 89.7k | 0.23 |
| celo | CELO | native | $3.7M | $3.7M |  | 1.00 |
| celo | BRLA | other | $3.6M | $3.2M | 2.6k | 0.89 |
| celo | celo | native | $1.9M | $1.6M | 1.1M | 0.86 |
| celo | USDT0 | usd_stable | $1.5M | $226.4k | 6.0M | 0.07 |
| celo | WETH | eth | $268.8k | $107.2k | 6.0k | 0.18 |
| xlayer | USDC | usd_stable | $53.7M | $45.1M | 53.6k | 0.84 |
| xlayer | USDG | usd_stable | $14.9M | $4.8M | 197.9k | 0.30 |
| xlayer | AAPLx | other | $12.6M | $12.6M | 2.2k | 0.99 |
| xlayer | USDT0 | usd_stable | $7.5M | $1.6M | 192.2k | 0.17 |
| xlayer | OKB | native | $5.1M | $1.6M | 60.5k | 0.23 |
| arc | USDC | usd_stable | $25.0M | $7.1M |  | 0.24 |
| arc | USDC | usd_stable | $507.1k | $288.4k | 28.9k | 0.52 |
| arc | cirBTC | other | $322.8k | $269.5k | 4.3k | 0.81 |
| arc | EURC | eur_stable | $1.0k | $1.0k | 851 | 1.00 |
| hedera | HBAR | native | $29.4M | $20.7M | 169.8k | 0.69 |
| hedera | USDC | usd_stable | $6.4M | $2.3M | 21.5k | 0.30 |
| hedera | WHBAR | native | $6.4M | $2.3M | 22.1k | 0.31 |
| hedera | PACK | other | $4.2k | $3.1k | 797 | 0.63 |
| hedera | GRELF | other | $2.9k | $1.8k | 531 | 0.51 |
| dydx | USDC.n | usd_stable | $189 | $141 | 33.1k | 0.70 |
| unichain | USDC | usd_stable | $28.8M | $11.6M | 54.0k | 0.23 |
| unichain | HYPE | other | $10.9M | $5.7M | 18.1k | 0.40 |
| unichain | WETH | eth | $5.2M | $2.5M | 19.0k | 0.43 |
| unichain | WBTC | btc | $2.1M | $1.5M | 7.3k | 0.68 |
| unichain | ETH | eth | $1.9M | $1.5M |  | 0.74 |
| worldchain | WLD | other | $14.8M | $7.2M | 329.6k | 0.44 |
| worldchain | USDC.e | usd_stable | $2.6M | $1.6M | 74.1k | 0.54 |
| worldchain | Re7USDC | other | $445.3k | $432.1k | 7.8k | 0.97 |
| worldchain | Re7WLD | other | $297.0k | $164.3k | 33.3k | 0.58 |
| worldchain | WETH | eth | $247.5k | $160.9k | 16.4k | 0.65 |
| bitcoin | BTC | btc | $89.4B | $0 | 630.1k | 0.04 |
| plasma | USDT0 | usd_stable | $94.8M | $55.4M | 114.8k | 0.57 |
| plasma | XPL | native | $14.3M | $14.3M |  | 1.00 |
| plasma | aPlaUSDT0 | other | $2.3M | $2.2M | 4.1k | 0.95 |
| plasma | WXPL | native | $2.2M | $737.1k | 25.9k | 0.25 |
| plasma | aPlaUSDe | other | $666.2k | $667.5k | 508 | 1.00 |
| flare | FXRP | other | $43.4M | $18.2M | 32.6k | 0.29 |
| flare | WFLR | native | $7.3M | $5.3M | 21.3k | 0.79 |
| flare | sFLR | other | $7.2M | $5.5M | 2.4k | 0.83 |
| flare | USDT0 | usd_stable | $6.4M | $2.6M | 35.4k | 0.34 |
| flare | USDC.e | usd_stable | $2.3M | $2.2M | 7.2k | 0.93 |
| cardano | ADA | native | $17.9M | $1.7M | 519.6k | 0.04 |
| cardano | NIGHT | other | $4.0M | $1.9M | 14.9k | 0.44 |
| cardano | DJED | usd_stable | $2.5M | $2.6M | 1.4k | 1.00 |
| cardano | USDCX | usd_stable | $2.3M | $1.3M | 5.3k | 0.56 |
| cardano | SNEK | other | $959.8k | $793.3k | 5.3k | 0.78 |
| gnosis | EURe | eur_stable | $5.7M | $3.8M | 17.9k | 0.66 |
| gnosis | wstETH | eth | $5.0M | $1.4M | 30.4k | 0.15 |
| gnosis | sDAI | other | $5.0M | $1.3M | 79.5k | 0.15 |
| gnosis | USDC.e | usd_stable | $2.3M | $1.1M | 22.2k | 0.41 |
| gnosis | aGnoUSDCe | other | $946.9k | $943.3k | 254 | 1.00 |
| pulsechain | PCOCK | other | $3.7M | $3.6M | 3.1k | 1.00 |
| pulsechain | WPLS | native | $1.5M | $799.8k | 135.1k | 0.52 |
| pulsechain | USDC | usd_stable | $1.1M | $705.7k | 14.5k | 0.63 |
| pulsechain | ATROPA | other | $740.3k | $727.1k | 2.6k | 0.99 |
| pulsechain | HEX | other | $711.0k | $225.7k | 19.8k | 0.24 |
| hyperevm | USDC | usd_stable | $256.7M | $73.3M | 182.7k | 0.23 |
| hyperevm | HYPE | native | $235.4M | $159.1M |  | 0.66 |
| hyperevm | WHYPE | native | $144.3M | $44.1M | 196.3k | 0.29 |
| hyperevm | USDT0 | usd_stable | $26.6M | $9.2M | 69.4k | 0.23 |
| hyperevm | UBTC | btc | $12.6M | $9.2M | 19.3k | 0.73 |
| ronin | RON | native | $1.7M | $1.2M |  | 0.66 |
| ronin | SLP | other | $918.6k | $913.8k | 4.3k | 0.99 |
| ronin | AXS | other | $213.1k | $96.6k | 13.8k | 0.35 |
| ronin | WRON | native | $207.7k | $71.8k | 32.8k | 0.22 |
| ronin | WETH | eth | $136.9k | $53.4k | 39.7k | 0.25 |
| ink | USDC | usd_stable | $1.5B | $1.2B | 13.8k | 0.81 |
| ink | USDT0 | usd_stable | $763.1M | $357.1M | 23.8k | 0.23 |
| ink | WETH | eth | $560.6M | $299.8M | 23.3k | 0.31 |
| ink | kBTC | btc | $523.6M | $274.9M | 11.2k | 0.34 |
| ink | wQQQx | other | $96.6M | $96.7M | 432 | 1.00 |
| blast | USDB | usd_stable | $923.9k | $911.2k | 11.9k | 0.99 |
| blast | blast | other | $18.3k | $15.6k | 9.7k | 0.85 |
| blast | WETH | eth | $13.2k | $12.8k | 22.2k | 0.97 |
| blast | ETH | eth | $2.2k | $1.1k |  | 0.40 |
| blast | ESE | other | $33 | $33 | 432 | 1.00 |
| avalanche | AvalancheUSDC | other | $179.6M | $60.0M | 137.3k | 0.30 |
| avalanche | WAVAX | native | $149.0M | $48.7M | 139.9k | 0.28 |
| avalanche | USDT | usd_stable | $38.1M | $13.0M | 45.5k | 0.23 |
| avalanche | AVAX | native | $24.6M | $8.5M |  | 0.21 |
| avalanche | WETH | eth | $9.3M | $3.0M | 16.6k | 0.18 |
| soneium | USDC | usd_stable | $441.9k | $349.2k | 28.1k | 0.79 |
| soneium | WETH | eth | $55.2k | $23.6k | 21.4k | 0.30 |
| soneium | USDSC | other | $42.2k | $13.7k | 13.2k | 0.16 |
| soneium | ASTAR | other | $32.8k | $22.3k | 7.8k | 0.51 |
| soneium | ETH | eth | $3.7k | $1.5k |  | 0.32 |
| plume | pUSD | other | $102.4k | $102.6k | 1.0k | 1.00 |
| plume | USDC | usd_stable | $102.3k | $102.5k | 1.0k | 1.00 |
| plume | PLUME | native | $510 | $511 |  | 1.00 |
| thorchain | RUNE | native | $3.8M | $1.0M | 101.8k | 0.23 |
| starknet | STRK | native | $119.7M | $53.6M | 295.0k | 0.33 |
| starknet | ETH | eth | $58.3M | $53.6M | 32.2k | 0.92 |
| starknet | ZEC | other | $46.9M | $29.8M | 10.3k | 0.53 |
| starknet | USDC | usd_stable | $21.7M | $3.8M | 119.0k | 0.13 |
| starknet | strkBTC | btc | $992.5k | $479.7k | 10.0k | 0.38 |
| kaia | USD₮ | usd_stable | $36.2M | $18.1M | 114.9k | 0.36 |
| kaia | WKLAY | other | $1.1M | $514.5k | 57.0k | 0.40 |
| kaia | KAIA | native | $1.0M | $673.2k |  | 0.61 |
| kaia | oUSDT | other | $499.6k | $486.2k | 82.9k | 0.97 |
| kaia | USDT | usd_stable | $89.5k | $42.8k | 26.8k | 0.51 |
| litecoin | LTC | native | $2.1B | $0 | 156.7k | 0.02 |
| abstract | USDC.e | usd_stable | $1.9M | $844.8k | 54.8k | 0.34 |
| abstract | WETH | eth | $1.4M | $517.9k | 35.8k | 0.24 |
| abstract | ETH | eth | $1.2M | $255.8k | 415.1k | 0.18 |
| abstract | PENGU | other | $963.1k | $426.9k | 27.1k | 0.37 |
| abstract | ETH | eth | $935.4k | $280.8k |  | 0.22 |
| berachain | BERA | native | $695.4k | $508.0k |  | 0.73 |
| berachain | sWBERA | other | $4.5k | $4.5k | 1.3k | 1.00 |
| berachain | WBERA | native | $4.2k | $2.7k | 23.5k | 0.67 |
| berachain | USDe | usd_stable | $77 | $26 | 3.9k | 0.16 |
| celestia | TIA | native | $5.7M | $2.9M | 4.3k | 0.38 |
| sonic | wS | native | $19.1M | $8.8M | 47.9k | 0.28 |
| sonic | WETH | eth | $15.0M | $7.8M | 25.0k | 0.30 |
| sonic | USDC | usd_stable | $11.1M | $5.7M | 46.7k | 0.43 |
| sonic | S | native | $526.5k | $266.4k |  | 0.65 |
| sonic | WBTC | btc | $141.3k | $86.6k | 4.9k | 0.45 |
| tezos | XTZ | native | $1.8M | $0 | 83.3k |  |
| tezos | USDt | usd_stable | $32.4k | $0 | 1.2k |  |
| tezos | tzBTC | btc | $24.4k | $0 | 264 |  |
| tezos | oXTZ | other | $11.9k | $0 | 463 |  |
| tezos | uUSD | other | $2.1k | $0 | 857 |  |
| cronos | WCRO | native | $3.3M | $1.1M | 70.1k | 0.19 |
| cronos | CRO | native | $1.5M | $746.8k |  | 0.40 |
| cronos | USDC | usd_stable | $1.4M | $778.5k | 15.8k | 0.45 |
| cronos | CROCAT | other | $1.3M | $932.2k | 4.0k | 0.53 |
| cronos | ULTCAT | other | $489.1k | $387.9k | 13.8k | 0.77 |
| osmosis | USDC.inj | usd_stable | $5.4M | $3.7M | 5.1k | 0.67 |
| osmosis | USDC.n | usd_stable | $2.1M | $786.7k | 41.6k | 0.18 |
| osmosis | ATOM | other | $1.9M | $788.5k | 24.2k | 0.39 |
| osmosis | USDC | usd_stable | $977.9k | $201.8k | 35.1k | 0.12 |
| osmosis | ETH | eth | $409.8k | $243.6k | 8.4k | 0.53 |
| tempo | USDC.e | usd_stable | $19.9M | $19.5M | 38.0k | 0.98 |
| tempo | USDT0 | usd_stable | $4.0M | $3.9M | 3.1k | 0.98 |
| tempo | pathUSD | other | $130.2k | $118.1k | 34.1k | 0.90 |
| tempo | senpathUSD | other | $117.3k | $117.4k | 1.6k | 1.00 |
| tempo | OUSD | other | $0 | $0 | 6.2k | 0.37 |
| core | CORE | native | $829.5k | $481.5k |  | 0.53 |
| core | WCORE | native | $2.4k | $1.3k | 5.0k | 0.43 |
| core | USDT | usd_stable | $564 | $428 | 3.2k | 0.72 |
| core | BTC | btc | $20 | $20 | 432 | 1.00 |
| core | WBTC | btc | $16 | $16 | 288 | 1.00 |
| katana | vbUSDC | other | $67.3M | $47.6M | 8.5k | 0.55 |
| katana | vbETH | other | $38.2M | $36.5M | 5.8k | 0.95 |
| katana | KAT | other | $12.1M | $10.6M | 4.0k | 0.86 |
| katana | vbWBTC | other | $132.0k | $132.1k | 1.8k | 1.00 |
| katana | AUSD | usd_stable | $89.8k | $89.9k | 445 | 1.00 |
| dogecoin | DOGE | native | $1.1B | $0 | 18.9k |  |
| mantle | WMNT | native | $3.5M | $2.4M | 6.0k | 0.67 |
| mantle | USDT | usd_stable | $2.4M | $1.0M | 8.4k | 0.33 |
| mantle | MNT | native | $2.0M | $2.0M |  | 1.00 |
| mantle | cmETH | other | $881.8k | $831.3k | 1.9k | 0.94 |
| mantle | mETH | eth | $621.3k | $567.6k | 1.3k | 0.91 |
| sei | USDC | usd_stable | $2.5M | $1.6M | 9.1k | 0.50 |
| sei | wSEI | native | $2.4M | $1.5M | 26.3k | 0.49 |
| sei | USDT0 | usd_stable | $73.2k | $53.2k | 18.2k | 0.65 |
| sei | WETH | eth | $23.5k | $22.7k | 1.8k | 0.96 |
| sei | WBTC | btc | $18.5k | $18.6k | 908 | 1.00 |
| zksync | zk | other | $1.4M | $783.5k | 2.1k | 0.48 |
| zksync | WETH | eth | $347.9k | $93.6k | 6.4k | 0.20 |
| zksync | USDC | usd_stable | $332.5k | $117.6k | 4.0k | 0.30 |
| zksync | ETH | eth | $261.1k | $88.6k | 51.2k | 0.27 |
| zksync | ETH | eth | $70.4k | $25.2k |  | 0.29 |
| cosmoshub | ATOM | native | $22.6M | $14.6M | 48.8k | 0.63 |
| cosmoshub | USDC.inj | usd_stable | $20.5k | $20.4k | 78 | 1.00 |
| cosmoshub | STARS | other | $86 | $85 | 78 | 1.00 |
| cosmoshub | stATOM | other | $0 | $0 | 78 | 1.00 |
| cosmoshub | USDC | usd_stable | $0 | $0 | 78 | 1.00 |
| bitcoin-cash | BCH | native | $170.7M | $0 | 15.1k |  |
| linea | ETH | eth | $2.1M | $1.9M |  | 0.91 |
| linea | LINEA | other | $567.5k | $266.7k | 2.6k | 0.44 |
| linea | mUSD | usd_stable | $353.2k | $275.0k | 1.0k | 0.77 |
| linea | WETH | eth | $299.2k | $95.0k | 5.4k | 0.18 |
| linea | USDC | usd_stable | $197.9k | $64.8k | 5.1k | 0.25 |
| scroll | ETH | eth | $357.0k | $53.8k | 8.8k | 0.09 |
| scroll | USDC | usd_stable | $346.9k | $57.1k | 6.4k | 0.09 |
| scroll | SCR | other | $162.4k | $135.5k | 412 | 0.83 |
| scroll | USDT | usd_stable | $63.0k | $18.8k | 1.7k | 0.13 |
| scroll | ETH | eth | $46.0k | $29.8k |  | 0.62 |
| zcash | ZEC | native | $1.9B | $0 | 8.1k |  |
| rootstock | RBTC | native | $7.6k | $5.3k |  | 0.62 |
| noble | USDC | usd_stable | $877.5k | $279.4k | 2.4k | 0.23 |
| noble | EURe | eur_stable | $20.0k | $19.6k | 20 | 1.00 |
| noble | USDY | usd_stable | $54 | $52 | 40 | 1.00 |

## Cross-source agreement

42 checks passed, 3 failed (tolerance ±25% on transaction counts).

| check | ok | detail |
|---|---|---|
| `tx-cross-source:abstract:l2beat` | ok | probe 140.8k/day (sampled-blocks) vs l2beat 139.2k/day: x1.011 |
| `tx-cross-source:arbitrum:growthepie` | ok | probe 2.1M/day (sampled-blocks) vs growthepie 1.8M/day: x1.172 |
| `tx-cross-source:arbitrum:l2beat` | ok | probe 2.1M/day (sampled-blocks) vs l2beat 1.8M/day: x1.171 |
| `tx-cross-source:base:growthepie` | ok | probe 12.3M/day (sampled-blocks) vs growthepie 11.3M/day: x1.093 |
| `tx-cross-source:base:l2beat` | ok | probe 12.3M/day (sampled-blocks) vs l2beat 11.3M/day: x1.092 |
| `tx-cross-source:bitcoin-cash:blockchair-24h` | ok | probe 15.1k/day (aggregator-24h) vs blockchair-24h 15.2k/day: x0.994 |
| `tx-cross-source:blast:l2beat` | ok | probe 320.3k/day (sampled-blocks) vs l2beat 321.4k/day: x0.997 |
| `tx-cross-source:celo:growthepie` | ok | probe 905.0k/day (sampled-blocks) vs growthepie 896.7k/day: x1.009 |
| `tx-cross-source:celo:l2beat` | ok | probe 905.0k/day (sampled-blocks) vs l2beat 896.7k/day: x1.009 |
| `tx-cross-source:dogecoin:blockchair-24h` | ok | probe 18.9k/day (aggregator-24h) vs blockchair-24h 18.8k/day: x1.005 |
| `tx-cross-source:ethereum:growthepie` | ok | probe 1.9M/day (sampled-blocks) vs growthepie 1.8M/day: x1.017 |
| `tx-cross-source:gnosis:l2beat` | ok | probe 474.0k/day (sampled-blocks) vs l2beat 459.2k/day: x1.032 |
| `tx-cross-source:ink:growthepie` | ok | probe 353.8k/day (sampled-blocks) vs growthepie 333.9k/day: x1.059 |
| `tx-cross-source:ink:l2beat` | ok | probe 353.8k/day (sampled-blocks) vs l2beat 334.0k/day: x1.059 |
| `tx-cross-source:katana:l2beat` | ok | probe 38.7k/day (sampled-blocks) vs l2beat 35.7k/day: x1.085 |
| `tx-cross-source:linea:growthepie` | ok | probe 14.6k/day (sampled-blocks) vs growthepie 17.9k/day: x0.819 |
| `tx-cross-source:linea:l2beat` | ok | probe 14.6k/day (sampled-blocks) vs l2beat 17.9k/day: x0.819 |
| `tx-cross-source:mantle:growthepie` | **FAIL** | probe 18.8k/day (sampled-blocks) vs growthepie 23.7k/day: x0.794 |
| `tx-cross-source:mantle:l2beat` | **FAIL** | probe 18.8k/day (sampled-blocks) vs l2beat 23.7k/day: x0.794 |
| `tx-cross-source:megaeth:growthepie` | **FAIL** | probe 2.0M/day (sampled-blocks) vs growthepie 1.1M/day: x1.786 |
| `tx-cross-source:megaeth:l2beat` | ok | probe 2.0M/day (sampled-blocks) vs l2beat 2.0M/day: x1.005 |
| `tx-cross-source:near:nearblocks` | ok | probe 1.0M/day (sampled-blocks) vs nearblocks 1.0M/day: x1.023 |
| `tx-cross-source:optimism:growthepie` | ok | probe 1.7M/day (sampled-blocks) vs growthepie 1.7M/day: x1.016 |
| `tx-cross-source:plume:growthepie` | ok | probe 206.4k/day (sampled-blocks) vs growthepie 207.1k/day: x0.997 |
| `tx-cross-source:polygon:growthepie` | ok | probe 5.4M/day (sampled-blocks) vs growthepie 5.5M/day: x0.998 |
| `tx-cross-source:polygon:l2beat` | ok | probe 5.4M/day (sampled-blocks) vs l2beat 5.5M/day: x0.998 |
| `tx-cross-source:robinhood:growthepie` | ok | probe 8.1M/day (sampled-blocks) vs growthepie 8.5M/day: x0.952 |
| `tx-cross-source:robinhood:l2beat` | ok | probe 8.1M/day (sampled-blocks) vs l2beat 8.5M/day: x0.952 |
| `tx-cross-source:ronin:growthepie` | ok | probe 389.7k/day (sampled-blocks) vs growthepie 441.6k/day: x0.882 |
| `tx-cross-source:scroll:growthepie` | ok | probe 13.1k/day (sampled-blocks) vs growthepie 13.3k/day: x0.987 |
| `tx-cross-source:scroll:l2beat` | ok | probe 13.1k/day (sampled-blocks) vs l2beat 13.3k/day: x0.987 |
| `tx-cross-source:soneium:growthepie` | ok | probe 287.3k/day (sampled-blocks) vs growthepie 285.1k/day: x1.008 |
| `tx-cross-source:soneium:l2beat` | ok | probe 287.3k/day (sampled-blocks) vs l2beat 285.3k/day: x1.007 |
| `tx-cross-source:starknet:growthepie` | ok | probe 184.4k/day (sampled-blocks) vs growthepie 187.9k/day: x0.981 |
| `tx-cross-source:starknet:l2beat` | ok | probe 184.4k/day (sampled-blocks) vs l2beat 192.7k/day: x0.957 |
| `tx-cross-source:tron:tronscan` | ok | probe 11.4M/day (sampled-blocks) vs tronscan 11.8M/day: x0.972 |
| `tx-cross-source:unichain:growthepie` | ok | probe 702.9k/day (sampled-blocks) vs growthepie 689.0k/day: x1.020 |
| `tx-cross-source:unichain:l2beat` | ok | probe 702.9k/day (sampled-blocks) vs l2beat 689.0k/day: x1.020 |
| `tx-cross-source:worldchain:growthepie` | ok | probe 657.9k/day (sampled-blocks) vs growthepie 642.5k/day: x1.024 |
| `tx-cross-source:xlayer:l2beat` | ok | probe 822.1k/day (sampled-blocks) vs l2beat 845.2k/day: x0.973 |
| `tx-cross-source:zcash:blockchair-24h` | ok | probe 8.1k/day (aggregator-24h) vs blockchair-24h 8.2k/day: x0.993 |
| `tx-cross-source:zksync:growthepie` | ok | probe 16.8k/day (sampled-blocks) vs growthepie 17.1k/day: x0.978 |
| `dex-breakdown` | ok | sum of per-chain 24h $10.5B vs DefiLlama total24h $10.7B (x0.9808) |
| `llama-keys` | ok | 0 contested of 263 inferred keys:  |
| `registry-ids` | ok | all registry identities resolve |
