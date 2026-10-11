# Chain activity — 2026-10-11

Census of 567 chains from DefiLlama, growthepie, L2Beat, Blockchair, Tronscan, NEARBlocks, CoinGecko and Hyperliquid (days before 2026-10-11 UTC are complete); direct probe of 65 registry chains over 2026-10-10T00:00:00+00:00 → 2026-10-11T00:00:00+00:00 (24.0 h).

Tiers (how reasonable it is to trade there): deep 12, tradeable 26, token_only 28, thin 78, inactive 423.

## The list: chains by activity

Ranked by the mean percentile across DEX volume, fees, stablecoin float, TVL and transactions (at least three of the five measured). DEX, fees and transactions from the aggregators are 7-day daily averages, except where an aggregator has the probe's own day ("same day"); probe columns are the direct reading of one UTC day, with its standard error where it is a sample. Transfer value is net per transaction (see the probe docstring); `†` marks an asset whose estimate comes mostly from one sampled block, i.e. one large transfer scaled up.

| # | chain | family | tier | DEX/day | stables | TVL | fees/day | tx/day (aggregator) | tx/day (probe) | transfers/day (probe) | top assets moved (probe) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Solana | solana | deep | $1.9B | $16.0B | $6.2B | $15.1M |  |  |  |  |
| 2 | BSC | evm | deep | $730.0M | $13.3B | $5.6B | $2.5M |  | 13.5M ±223.5k | $4.1B | USDT $2.2B, BTCB $365.6M†, BNB $334.4M |
| 3 | Base | evm | deep | $1.0B | $5.2B | $6.2B | $1.8M | 6.0M (growthepie, same day) | 6.0M ±119.6k | $202.1B | USDC $92.9B, WETH $72.9B, cbBTC $25.6B |
| 4 | Hyperliquid L1 (hyperevm) | evm | deep | $246.7M | $7.2B | $1.1B | $5.1M |  | 343.2k ±19.0k | $438.7M | USDC $220.0M, HYPE $163.3M†, WHYPE $30.7M |
| 5 | Ethereum | evm | deep | $1.4B | $145.2B | $51.4B | $11.4M | 1.6M (growthepie, same day) | 1.6M ±40.3k | $10.6B | USDC $3.5B, USDT $2.9B, ETH $1.2B |
| 6 | Tron | tron | deep | $53.2M | $94.9B | $5.6B | $256.3k | 11.1M (tronscan, same day) | 10.9M ±147.1k | $18.0B | USDT $17.2B, TRX $654.4M, USDD $100.7M† |
| 7 | Robinhood Chain | evm | deep | $971.2M | $1.1B | $1.1B | $3.1M | 4.1M (growthepie, same day) | 4.2M ±206.2k | $3.0B | USDG $1.3B, steakUSDG $571.2M†, WETH $382.2M |
| 8 | Polygon | evm | deep | $217.0M | $2.9B | $679.7M | $1.2M | 4.8M (growthepie, same day) | 4.9M ±95.1k | $1.7B | USDC $655.6M, USDC $387.1M, pUSD $372.0M |
| 9 | Avalanche | evm | deep | $136.4M | $1.4B | $619.5M | $357.3k |  | 198.2k ±21.5k | $457.5M | WAVAX $180.7M, AvalancheUSDC $142.4M, USDT $94.2M |
| 10 | Arbitrum | evm | deep | $133.6M | $3.8B | $1.4B | $302.9k | 1.2M (growthepie, same day) | 1.2M ±58.8k | $2.0B | USDC $1.6B, USDT0 $215.6M†, WETH $93.4M† |
| 11 | Monad | evm | tradeable | $41.1M | $741.2M | $1.0B | $210.1k |  | 4.3M ±98.0k | $642.7M | USDC $311.1M, mUSD $102.8M†, USDT0 $73.5M† |
| 12 | Arc | evm | tradeable | $43.9M | $500.5M | $556.8M | $165.1k |  | 814.2k ±39.3k | $18.0M | USDC $16.6M, EURC $1.2M†, USDC $99.8k |
| 13 | Sui | sui | tradeable | $39.6M | $490.0M | $526.9M | $117.7k |  | 4.9M ±104.5k | $546.1M | SUI $285.9M†, USDSUI $206.4M†, USDC $28.4M |
| 14 | OP Mainnet (optimism) | evm | tradeable | $26.1M | $660.4M | $454.4M | $259.5k | 1.6M (growthepie, same day) | 1.5M ±28.5k | $13.0B | USDC $7.2B, WETH $4.6B, velo $832.6M |
| 15 | Plasma | evm | tradeable | $4.4M | $1.3B | $512.4M | $130.2k |  | 610.5k ±19.6k | $50.1M | USDT0 $46.6M, XPL $2.7M†, WXPL $828.1k |
| 16 | Near | near | deep | $177.4M | $129.6M | $248.3M | $294.7k | 850.3k (nearblocks, same day) | 902.5k ±59.5k | $167.0M | NEAR $162.4M†, wNEAR $3.2M†, XRP $844.1k† |
| 17 | X Layer | evm | deep | $18.3M | $1.6B | $160.5M | $27.0k | 564.1k (l2beat, same day) | 555.1k ±18.2k | $168.5M | USDT0 $134.5M†, USDC $25.1M†, USDG $2.8M |
| 18 | TON | ton | tradeable | $5.3M | $719.1M | $52.1M | $1.2M |  | 4.3M ±117.7k | $126.7M | TON $89.3M, USD₮ $32.1M, tsTON $2.2M† |
| 19 | Stellar | stellar | tradeable | $1.7M | $934.6M | $252.4M | $187.7k | 4.6M (blockchair-24h) | 4.8M | $23.1M | XLM $12.0M†, USDC $9.6M, VELO $615.0k† |
| 20 | Aptos | aptos | tradeable | $5.8M | $907.1M | $49.9M | $53.0k |  | 6.8M | $235.1k | USDt $206.4k†, USDC $28.6k† |
| 21 | XRPL | xrpl | tradeable | $5.6M | $1.2B | $41.9M | $28.7k | 1.9M (blockchair-24h) | 2.0M ±242.0k | $97.4M | XRP $97.1M, RLUSD $336.3k |
| 22 | THORChain | cosmos | token_only | $38.0M | - | $36.3M | $21.8k |  | 189.1k | $3.8M | RUNE $3.8M |
| 23 | Sei | evm | tradeable | $7.3M | $309.2M | $33.2M | $38.7k |  | 14.2k ±4.5k | $12.2M | wSEI $6.9M, USDC $5.1M†, WBTC $99.5k† |
| 24 | Ink | evm | tradeable | $3.0M | $184.0M | $209.6M | $137.7k | 214.7k (growthepie, same day) | 192.7k ±8.0k | $41.6M | USDT0 $22.5M†, WETH $10.9M†, kBTC $7.8M† |
| 25 | Chainflip |  | thin | $16.2M | - | $16.1M | $50.4k |  |  |  |  |
| 26 | Cronos | evm | tradeable | $3.0M | $139.0M | $151.4M | $19.5k |  | 37.9k ±7.8k | $1.9M | WCRO $1.0M, CRO $552.2k, ULTCAT $83.9k† |
| 27 | Starknet | starknet | tradeable | $23.8M | $153.0M | $167.1M | $61.0k | 224.1k (growthepie, same day) | 274.8k ±38.7k | $113.6M | STRK $59.4M, USDC $22.8M, ZEC $19.3M† |
| 28 | Canton |  | token_only | $39.2M | - | $11.9M | $17.7k |  |  |  |  |
| 29 | Flare | evm | tradeable | $4.6M | $48.2M | $124.7M | $21.0k |  | 456.0k ±78.6k | $129.2M | FLR $116.4M†, USDT0 $8.5M†, FXRP $2.4M† |
| 30 | Unichain | evm | tradeable | $7.9M | $27.7M | $27.2M | $18.4k | 622.3k (growthepie, same day) | 615.2k ±2.5k | $4.3M | USDC $2.0M†, HYPE $1.9M†, WETH $128.9k† |
| 31 | Bitcoin | utxo | token_only | $386.5k | - | $4.4B | $11.1k | 720.4k (blockchair-24h) | 754.7k | $45.1B (gross) | BTC $45.1B |
| 32 | Cardano | cardano | tradeable | $1.6M | $71.3M | $68.0M | $30.4k | 247.3k (blockchair-24h) | 308.7k | $67.1M | USDCX $34.5M†, ADA $19.5M, USDM $7.4M† |
| 33 | PulseChain | evm | tradeable | $2.6M | $32.8M | $76.6M | $7.2k |  | 442.3k ±16.3k | $3.2M | PLS $875.4k†, vPLS $484.8k†, WPLS $405.1k |
| 34 | Gnosis | evm | tradeable | $3.0M | $15.6M | $95.7M | $13.6k | 315.8k (l2beat, same day) | 318.0k ±11.8k | $1.4M | EURe $382.5k, USDC.e $282.2k†, sDAI $167.8k |
| 35 | Sonic | evm | tradeable | $1.7M | $157.2M | $18.5M | $6.9k |  | 126.2k ±19.2k | $34.4M | wS $13.0M, USDC $11.8M, WETH $8.3M |
| 36 | Mantle | evm | tradeable | $2.0M | $548.9M | $108.8M | $50.8k | 10.1k (growthepie, same day) | 7.6k ±1.9k | $7.2M | USDT $2.4M†, MNT $2.3M†, SVL $2.3M† |
| 37 | BOT Chain |  | thin | $2.2M | - | $31.9M | $6.7k |  |  |  |  |
| 38 | Hedera | hedera | tradeable | $2.4M | $48.1M | $36.9M | $6.8k |  | 677.6k | $3.5M | HBAR $1.9M†, USDC $1.3M†, WHBAR $252.7k† |
| 39 | Celo | evm | tradeable | $1.3M | $111.6M | $14.2M | $3.0k | 841.6k (growthepie, same day) | 788.4k ±16.3k | $9.0M | BRLA $3.5M†, axlUSDC $2.6M†, USDT0 $2.6M† |
| 40 | Stacks |  | tradeable | $2.9M | $11.5M | $93.1M | $6.4k |  |  |  |  |
| 41 | Algorand | algorand | token_only | $515.6k | $66.8M | $35.7M | $7.2k |  | 1.2M | $295.9M | USDC $248.7M†, ALGO $46.8M†, FOLKS $219.0k† |
| 42 | edgeX L1 |  | thin | $31.7M | $2.3M | - | $78.0k |  |  |  |  |
| 43 | Berachain | evm | thin | $617.0k | $61.1M | $38.2M | $4.9k |  | 67.2k ±3.5k | $624.8k | BERA $320.1k†, WBERA $93.9k†, USDC.e $71.6k† |
| 44 | Provenance |  | tradeable | $17.5M | $462.8M | $148.6M | $35 |  |  |  |  |
| 45 | Pharos |  | thin | - | $12.0M | $73.8M | $6.1k |  |  |  |  |
| 46 | Kaia | evm | token_only | $951.6k | $221.9M | $9.0M | $2.0k |  | 174.9k ±18.0k | $31.6M | USD₮ $29.9M†, WKLAY $918.7k, KAIA $529.2k |
| 47 | MegaETH | evm | thin | $545.8k | $19.2M | $12.9M | $-1.5k | 1.1M (growthepie, same day) | 2.0M ±21.6k | $296.8k | USDm $184.2k, MEGA $111.5k, WETH $610† |
| 48 | World Chain | evm | token_only | $490.0k | $16.6M | $44.1M | $3.0k | 593.8k (growthepie, same day) | 584.3k ±13.1k | $2.6M | WLD $1.8M, USDC.e $371.4k†, Re7WLD $219.4k |
| 49 | Hydration |  | thin | $856.0k | $13.6M | $56.1M | $3.0k |  |  |  |  |
| 50 | Osmosis | cosmos | thin | $569.9k | $17.2M | $11.1M | $7.5k |  | 55.9k | $476.6M | USDC.n $471.1M, ATOM $2.5M, USDC $1.4M |
| 51 | Dexalot |  | thin | $29.3M | - | $1.9M | $1.2k |  |  |  |  |
| 52 | ZKsync Era | evm | token_only | $437.8k | $36.1M | $15.3M | $67.2k | 16.6k (growthepie, same day) | 15.5k ±249 | $10.8M | zk $9.5M, WETH $567.0k, ETH $468.9k |
| 53 | Tempo | evm | thin | $894.4k | $731.1M | $106.6M | $22 |  | 46.5k ±7.1k | $112.2M | USDC.e $112.2M†, USDT0 $16.6k†, pathUSD $4.8k† |
| 54 | Katana | evm | thin | $595.8k | $10.2M | $40.6M | $8.4k | 18.0k (l2beat, same day) | 15.7k ±4.4k | $82.4M | vbETH $37.6M†, vbUSDC $35.6M†, KAT $9.2M† |
| 55 | Abstract | evm | thin | $1.8M | $3.4M | $4.7M | $84.2k | 87.4k (l2beat, same day) | 86.1k ±3.2k | $1.8M | USDC.e $1.2M†, ETH $295.4k, ETH $191.6k |
| 56 | Flow |  | thin | $477.2k | $71.7M | $12.6M | $872 |  |  |  |  |
| 57 | Mixin |  | thin | $32.9k | $34.5M | $77.1M | - |  |  |  |  |
| 58 | Rootstock | evm | thin | $429.2k | $11.4M | $83.1M | $1.3k |  | 5.4k ±223 | $101.1k | RBTC $101.1k† |
| 59 | XDC | evm | thin | $901.1k | $52.9M | $2.3M | $1.5k |  |  |  |  |
| 60 | Morph |  | thin | $334.4k | $30.8M | $75.4M | $4.3k | 10.9k (l2beat) |  |  |  |

Probed but outside the aggregator ranking: CosmosHub 16.7k tx/day (exact-blocks); Celestia 140.3k tx/day (sampled-blocks); Noble 9.5k tx/day (exact-index); dYdX 695.4k tx/day (sampled-blocks)

## The list, measured directly: every probed chain by transactions

One row per registry chain the probe read, busiest first. `$/tx` is net transfer value per transaction: a chain with millions of transactions and cents per transaction is busy with bots, not with money. `bookkeeping` is the share of transactions sent to registry-listed oracle, validator-signing or block-builder contracts — real transactions that are not activity (the headline keeps them, as L2Beat does). `top target` is the contract that received the largest share of transactions (and of value): one address carrying most of a chain is one actor, however large the totals.

| chain | family | tier | tx/day | method | bookkeeping | net transfers/day | $/tx | top target by txs | top target by value |
|---|---|---|---:|---|---:|---:|---:|---|---|
| BSC | evm | deep | 13.5M ±223.5k | sampled-blocks |  | $4.1B | $306.71 | `0x55d398326f` 13% | `0x55d398326f` 30% |
| Tron | tron | deep | 10.9M ±147.1k | sampled-blocks |  | $18.0B | $1645.52 | `0xa614f803b6` 19% | `0xa614f803b6` 96% |
| Aptos | aptos | tradeable | 6.8M | exact-versions minus sampled system share |  | $235.1k | $0.03 |  |  |
| Base | evm | deep | 6.0M ±119.6k | sampled-blocks |  | $202.1B | $33.9k | `0x6ff5693b99` 6% | `0x787fd1dc3b` 35% |
| Sui | sui | tradeable | 4.9M ±104.5k | exact-counter x sampled user share |  | $546.1M | $111.20 |  |  |
| Polygon | evm | deep | 4.9M ±95.1k | sampled-blocks |  | $1.7B | $343.09 | `0xe111180000` 21% | `0xccc88a9d1b` 24% |
| Stellar | stellar | tradeable | 4.8M | exact-blocks |  | $23.1M | $4.81 |  |  |
| Monad | evm | tradeable | 4.3M ±98.0k | sampled-blocks |  | $642.7M | $149.43 | `0xd32edf6642` 22% | `0x6131b5fae1` 44% |
| TON | ton | tradeable | 4.3M ±117.7k | sampled-blocks |  | $126.7M | $29.57 |  |  |
| Robinhood Chain | evm | deep | 4.2M ±206.2k | sampled-blocks |  | $3.0B | $715.47 | `0xcaf681a66d` 6% | `0x0000000071` 43% |
| XRPL | xrpl | tradeable | 2.0M ±242.0k | sampled-blocks |  | $97.4M | $47.94 |  |  |
| MegaETH | evm | thin | 2.0M ±21.6k | sampled-blocks | 87% | $296.8k | $0.15 | `0x6342000000` 44% | `0x12759afca6` 27% |
| Ethereum | evm | deep | 1.6M ±40.3k | sampled-blocks |  | $10.6B | $6604.78 | `0xdac17f958d` 20% | `0xdac17f958d` 24% |
| OP Mainnet (optimism) | evm | tradeable | 1.5M ±28.5k | sampled-blocks |  | $13.0B | $8643.25 | `0x1e04602a8b` 23% | `0xf1b41a86d8` 35% |
| Injective | cosmos | tradeable | 1.3M | exact-index |  | $1.3B | $950.18 |  |  |
| opBNB | evm | inactive | 1.2M ±79.1k | sampled-blocks |  | $22.5k | $0.02 | `0xa596e82b0e` 22% | `0x8e690c8196` 79% |
| Algorand | algorand | token_only | 1.2M | exact-counter |  | $295.9M | $244.21 |  |  |
| Arbitrum | evm | deep | 1.2M ±58.8k | sampled-blocks |  | $2.0B | $1775.81 | `0xaf88d065e7` 14% | `0x81d40f21f1` 38% |
| Near | near | deep | 902.5k ±59.5k | sampled-blocks |  | $167.0M | $185.09 |  |  |
| Arc | evm | tradeable | 814.2k ±39.3k | sampled-blocks |  | $18.0M | $22.11 | `0xddcdb85d4c` 22% | `0xb843bdc3a8` 90% |
| Celo | evm | tradeable | 788.4k ±16.3k | sampled-blocks |  | $9.0M | $11.42 | `0xbedaccbd65` 48% | `0xa5e1a81738` 39% |
| Bitcoin | utxo | token_only | 754.7k | exact-blocks |  | $45.1B (gross) | - |  |  |
| dYdX | cosmos | inactive | 695.4k ±1.6k | sampled-blocks |  | $815 | $0.00 |  |  |
| Hedera | hedera | tradeable | 677.6k | exact-blocks |  | $3.5M | $5.16 |  |  |
| Unichain | evm | tradeable | 615.2k ±2.5k | sampled-blocks | 84% | $4.3M | $7.00 | `0x3c3a8a41e0` 70% | `0x099b1a87de` 92% |
| Plasma | evm | tradeable | 610.5k ±19.6k | sampled-blocks |  | $50.1M | $82.05 | `0x334987c805` 47% | `0xb8ce59fc37` 94% |
| World Chain | evm | token_only | 584.3k ±13.1k | sampled-blocks |  | $2.6M | $4.49 | `0x0000000071` 67% | `0x2cfc85d8e4` 44% |
| X Layer | evm | deep | 555.1k ±18.2k | sampled-blocks |  | $168.5M | $303.54 | `0x6558dbe4c1` 19% | `0x779ded0c9e` 79% |
| Flare | evm | tradeable | 456.0k ±78.6k | sampled-blocks | 91% | $129.2M | $283.43 | `0x2ca6571daa` 91% | `0xd9770b1c7a` 80% |
| PulseChain | evm | tradeable | 442.3k ±16.3k | sampled-blocks |  | $3.2M | $7.15 | `0x76abe398ef` 8% | `0x2d7dcc5a1d` 21% |
| Ronin | evm | token_only | 407.2k ±8.3k | sampled-blocks |  | $5.4M | $13.26 | `0x43f18c0752` 74% | `0x7eae20d11e` 56% |
| Soneium | evm | thin | 351.0k ±8.0k | sampled-blocks |  | $61.8k | $0.18 | `0x0000000071` 47% | `0x384cdfe9c1` 59% |
| Hyperliquid L1 (hyperevm) | evm | deep | 343.2k ±19.0k | sampled-blocks |  | $438.7M | $1278.44 | `0x233ff29b23` 17% | `0xb21d281ded` 24% |
| Gnosis | evm | tradeable | 318.0k ±11.8k | sampled-blocks |  | $1.4M | $4.36 | `0x1d4bceb37b` 17% | `0x5f07734e2b` 28% |
| Cardano | cardano | tradeable | 308.7k | exact-blocks |  | $67.1M | $217.36 |  |  |
| Starknet | starknet | tradeable | 274.8k ±38.7k | sampled-blocks |  | $113.6M | $413.51 |  |  |
| Plume Mainnet | evm | token_only | 210.2k | sampled-blocks |  | $30 | $0.00 | `0xee96619e24` 99% | `0x77ab297da4` 100% |
| Avalanche | evm | deep | 198.2k ±21.5k | sampled-blocks |  | $457.5M | $2308.75 | `0xe844701934` 9% | `0x9702230a8e` 21% |
| Ink | evm | tradeable | 192.7k ±8.0k | sampled-blocks |  | $41.6M | $216.00 | `0x2fa8df1bad` 76% | `0x991d5546c4` 99% |
| THORChain | cosmos | token_only | 189.1k | exact-blocks |  | $3.8M | $20.28 |  |  |
| Blast | evm | thin | 182.1k ±5.5k | sampled-blocks |  | $34.0k | $0.19 | `0x848e45b91d` 61% | `0xb1a5700fa2` 82% |
| Kaia | evm | token_only | 174.9k ±18.0k | sampled-blocks |  | $31.6M | $180.47 | `0xcb56b163e5` 18% | `0xd077a40096` 93% |
| Litecoin | utxo | token_only | 164.1k | exact-blocks |  | $1.7B (gross) | - |  |  |
| Celestia | cosmos | token_only | 140.3k ±285 | sampled-blocks |  | $15.3M | $108.78 |  |  |
| Sonic | evm | tradeable | 126.2k ±19.2k | sampled-blocks |  | $34.4M | $272.67 | `0xeac0722f31` 24% | `0x12e66c8f21` 81% |
| Tezos | tezos | thin | 99.8k | exact-indexer |  | $2.3M | $23.16 |  |  |
| Abstract | evm | thin | 86.1k ±3.2k | sampled-blocks |  | $1.8M | $21.20 | `0x99bb83ae9b` 22% | `0x2ddf2129a5` 57% |
| Berachain | evm | thin | 67.2k ±3.5k | sampled-blocks |  | $624.8k | $9.30 | `0xd2f19a79b0` 64% | `0x6131b5fae1` 43% |
| Osmosis | cosmos | thin | 55.9k | exact-index |  | $476.6M | $8530.75 |  |  |
| Tempo | evm | thin | 46.5k ±7.1k | sampled-blocks |  | $112.2M | $2412.07 | `create` 84% | `create` 100% |
| Cronos | evm | tradeable | 37.9k ±7.8k | sampled-blocks |  | $1.9M | $49.67 | `0x1189331089` 13% | `0xa18f14a358` 33% |
| CORE | evm | inactive | 36.9k ±1.3k | sampled-blocks |  | $45.3k | $1.23 | `0x0000000000` 79% | `0xcced48e6fe` 33% |
| Doge (dogecoin) | utxo | token_only | 17.4k | aggregator-24h |  | $966.9M (gross) | - |  |  |
| CosmosHub | cosmos | token_only | 16.7k | exact-blocks |  | $9.5M | $571.70 |  |  |
| Katana | evm | thin | 15.7k ±4.4k | sampled-blocks |  | $82.4M | $5257.30 | `0x62230cea61` 57% | `0x2659c6085d` 100% |
| ZKsync Era | evm | token_only | 15.5k ±249 | sampled-blocks |  | $10.8M | $694.13 | `0x5a7d6b2f92` 12% | `0x5a7d6b2f92` 84% |
| Sei | evm | tradeable | 14.2k ±4.5k | sampled-blocks |  | $12.2M | $855.72 | `0x11da6463d6` 40% | `0x2dc9dd1862` 45% |
| Bitcoincash | utxo | token_only | 11.3k | aggregator-24h |  | $162.7M (gross) | - |  |  |
| Linea | evm | thin | 10.0k ±484 | sampled-blocks |  | $710.4k | $70.95 | `0x9dd23a4a08` 10% | `0x1789e00436` 33% |
| Noble | cosmos | thin | 9.5k | exact-index |  | $501.3M | $52.5k |  |  |
| Scroll | evm | thin | 8.3k ±270 | sampled-blocks |  | $247.2k | $29.64 | `0x5300000000` 34% | `0xd29687c813` 63% |
| Mantle | evm | tradeable | 7.6k ±1.9k | sampled-blocks |  | $7.2M | $958.14 | `0x3c22698118` 11% | `0x8c4ec2df83` 90% |
| Zcash | utxo | token_only | 6.4k | aggregator-24h |  | $423.2M (gross) | - |  |  |
| Rootstock | evm | thin | 5.4k ±223 | sampled-blocks |  | $101.1k | $18.69 | `0x0000000000` 52% |  |

## New activity

Detector hits, most severe first (info-level in `detectors.md`). Every hit carries its chain's tier so a surge on an untradeable chain reads as such.

- **[high]** OP Mainnet fees last day: $455.5k/day vs $116.9k baseline (x3.9, market x0.79, rarer than 1% of its days)  `chain_surge:OP Mainnet:fees:d1`
- **[notable]** Tempo stablecoin float +$581.0M in 30 days ($151.1M -> $732.1M, +385%); largest step $309.8M on 2026-09-30  `stable_inflow:Tempo:30d`
- **[notable]** USDD on Ethereum +$211.0M in 7 days ($241.9M -> $452.9M)  `stable_inflow:Ethereum:USDD`
- **[notable]** USDC on X Layer +$108.7M in 7 days ($19.0M -> $127.7M)  `stable_inflow:X Layer:USDC`
- **[notable]** USDe on Monad +$32.0M in 7 days ($69.4M -> $101.4M)  `stable_inflow:Monad:USDe`
- **[notable]** USDC on Near +$25.2M in 7 days ($63.4M -> $88.6M)  `stable_inflow:Near:USDC`
- **[notable]** Near stablecoin float +$25.2M in 7 days ($103.7M -> $128.8M, +24%)  `stable_inflow:Near`
- **[notable]** CAP on bsc: $20.7M/day of transfers, absent from the previous 2 probe(s)  `probe_new_asset:bsc:0x99991c6aabba5a096f24f250b73580f5179b9999`
- **[notable]** USDT on Monad +$20.6M in 7 days ($33.4M -> $54.0M)  `stable_inflow:Monad:USDT`
- **[notable]** Saga dex last day: $3.6M/day vs $686.1k baseline (x5.1, rarer than 4% of its days)  `chain_surge:Saga:dex:d1`
- **[notable]** Arbitrum daa last 7 days: 214.8k/day vs 118.8k baseline (x1.8, market x0.96, rarer than 3% of its days)  `chain_surge:Arbitrum:daa:d7`
- **[notable]** Near daa last 7 days: 109.6k/day vs 66.5k baseline (x1.6, market x0.96, rarer than 4% of its days)  `chain_surge:Near:daa:d7`
- **[notable]** Ronin tx last day: 454.7k/day vs 145.4k baseline (x3.1, market x0.89, rarer than 1% of its days)  `chain_surge:Ronin:tx:d1`
- **[notable]** Ronin tx last 7 days: 256.1k/day vs 156.8k baseline (x1.6, market x0.90, rarer than 2% of its days)  `chain_surge:Ronin:tx:d7`
- **[notable]** Ronin daa last day: 312.8k/day vs 10.9k baseline (x28.6, market x0.91, rarer than 1% of its days)  `chain_surge:Ronin:daa:d1`
- **[notable]** Ronin daa last 7 days: 117.7k/day vs 16.2k baseline (x7.2, market x0.96, rarer than 2% of its days)  `chain_surge:Ronin:daa:d7`
- **[notable]** ApeChain tx last day: 236.3k/day vs 91.5k baseline (x2.5, market x0.89, rarer than 3% of its days)  `chain_surge:ApeChain:tx:d1`
- **[notable]** Kaia transactions 437.9k on 2026-10-09 vs a 140.4k median over the 14 days before (x3.1, market x0.93; 10-06 168.5k, 10-07 131.8k, 10-08 177.1k)  `probe_tx_surge:kaia`

15 info-level hits (drops, divergences, thin chains, unregistered tradeable chains) are listed in `detectors.md`.

## What moved, by asset (probe)

Transfer value per day, net per transaction: what each account gained, so routed hops and flash-loan round trips cancel while both legs of a swap count (UTXO chains and Blockchair rows are gross outputs; Hyperliquid is traded notional). ± is one standard error of the stratified estimate; `top` is the share of the sampled value that came from one block (above 0.5 the figure is one large transfer scaled up).

| chain | asset | class | USD/day | ± | transfers/day | top |
|---|---|---|---:|---:|---:|---:|
| bsc | USDT | usd_stable | $2.2B | $378.2M | 13.5M | 0.14 |
| bsc | BTCB | btc | $365.6M | $319.9M | 106.5k | 0.87 |
| bsc | BNB | native | $334.4M | $82.4M |  | 0.21 |
| bsc | WBNB | native | $283.3M | $52.8M | 2.1M | 0.18 |
| bsc | USDC | usd_stable | $272.2M | $29.3M | 2.4M | 0.04 |
| tron | USDT | usd_stable | $17.2B | $3.2B | 2.1M | 0.13 |
| tron | TRX | native | $654.4M | $54.0M |  | 0.07 |
| tron | USDD | usd_stable | $100.7M | $73.4M | 2.2k | 0.71 |
| tron | JST | other | $16.9M | $11.7M | 3.2k | 0.66 |
| tron | WTRX | native | $2.7M | $1.3M | 5.3k | 0.46 |
| aptos | USDt | usd_stable | $206.4k | $207.7k | 29.5k | 1.00 |
| aptos | USDC | usd_stable | $28.6k | $20.0k | 88.6k | 0.52 |
| base | USDC | usd_stable | $92.9B | $3.1B | 3.0M | 0.01 |
| base | WETH | eth | $72.9B | $2.9B | 1.1M | 0.02 |
| base | cbBTC | btc | $25.6B | $1.2B | 351.4k | 0.02 |
| base | AERO | other | $4.2B | $600.2M | 607.2k | 0.07 |
| base | cbETH | eth | $1.3B | $41.8M | 77.1k | 0.01 |
| sui | SUI | native | $285.9M | $260.5M | 770.7k | 0.91 |
| sui | USDSUI | usd_stable | $206.4M | $181.6M | 5.7k | 0.87 |
| sui | USDC | usd_stable | $28.4M | $15.9M | 90.4k | 0.40 |
| sui | DEEP | other | $15.1M | $12.3M | 17.0k | 0.80 |
| sui | WAL | other | $6.2M | $3.6M | 39.6k | 0.46 |
| polygon | USDC | usd_stable | $655.6M | $112.2M | 4.6M | 0.14 |
| polygon | USDC | usd_stable | $387.1M | $141.2M | 912.6k | 0.23 |
| polygon | pUSD | usd_stable | $372.0M | $79.5M | 8.0M | 0.16 |
| polygon | USDT0 | usd_stable | $160.5M | $72.8M | 402.9k | 0.44 |
| polygon | LGNS | other | $41.6M | $5.3M | 2.3M | 0.08 |
| stellar | XLM | native | $12.0M | $8.9M | 1.9M | 0.73 |
| stellar | USDC | usd_stable | $9.6M | $2.6M | 129.3k | 0.19 |
| stellar | VELO | other | $615.0k | $568.8k | 2.0k | 0.92 |
| stellar | SHX | other | $301.3k | $121.1k | 4.9k | 0.26 |
| stellar | BLND | other | $205.9k | $206.8k | 864 | 1.00 |
| monad | USDC | usd_stable | $311.1M | $181.1M | 78.5k | 0.47 |
| monad | mUSD | usd_stable | $102.8M | $82.8M | 7.3k | 0.77 |
| monad | USDT0 | usd_stable | $73.5M | $73.4M | 8.8k | 1.00 |
| monad | AUSD | usd_stable | $36.7M | $26.4M | 15.4k | 0.80 |
| monad | wnUSDT0 | other | $32.3M | $32.3M | 1.5k | 1.00 |
| ton | TON | native | $89.3M | $26.2M | 3.5M | 0.17 |
| ton | USD₮ | usd_stable | $32.1M | $6.3M | 145.2k | 0.17 |
| ton | tsTON | other | $2.2M | $1.7M | 1.3k | 0.74 |
| ton | CATI | other | $1.8M | $1.8M | 240 | 1.00 |
| ton | MAJOR | other | $335.5k | $310.8k | 1.0k | 0.94 |
| robinhood | USDG | usd_stable | $1.3B | $682.9M | 1.1M | 0.44 |
| robinhood | steakUSDG | other | $571.2M | $571.2M | 5.6k | 1.00 |
| robinhood | WETH | eth | $382.2M | $55.6M | 1.7M | 0.08 |
| robinhood | ETH | eth | $368.6M | $118.8M |  | 0.20 |
| robinhood | SPY | other | $283.7M | $279.4M | 43.4k | 0.98 |
| xrpl | XRP | native | $97.1M | $21.8M | 384.4k | 0.21 |
| xrpl | RLUSD | usd_stable | $336.3k | $163.1k | 247.1k | 0.46 |
| megaeth | USDm | usd_stable | $184.2k | $57.7k | 96.1k | 0.18 |
| megaeth | MEGA | other | $111.5k | $58.5k | 2.6k | 0.35 |
| megaeth | WETH | eth | $610 | $609 | 432 | 1.00 |
| megaeth | ETH | eth | $470 | $469 |  | 1.00 |
| ethereum | USDC | usd_stable | $3.5B | $682.9M | 596.9k | 0.15 |
| ethereum | USDT | usd_stable | $2.9B | $538.2M | 792.6k | 0.13 |
| ethereum | ETH | eth | $1.2B | $334.0M |  | 0.26 |
| ethereum | RLUSD | usd_stable | $872.0M | $534.9M | 1.1k | 0.45 |
| ethereum | WETH | eth | $444.5M | $157.1M | 230.5k | 0.29 |
| optimism | USDC | usd_stable | $7.2B | $151.3M | 1.2M | 0.01 |
| optimism | WETH | eth | $4.6B | $216.7M | 925.6k | 0.02 |
| optimism | velo | other | $832.6M | $23.4M | 1.5M | 0.01 |
| optimism | OP | other | $299.2M | $11.3M | 491.6k | 0.02 |
| optimism | WBTC | btc | $13.9M | $5.4M | 14.5k | 0.26 |
| injective | USDC.inj | usd_stable | $1.2B | $341.7M | 576.8k | 0.16 |
| injective | INJ | native | $54.4M | $31.0M | 1.3M | 0.34 |
| injective | WETH | eth | $20.9M | $2.6M | 60.2k | 0.04 |
| injective | USDT | usd_stable | $5.4k | $5.5k | 2.4k | 1.00 |
| opbnb | USDT | usd_stable | $13.4k | $9.4k | 19.0k | 0.66 |
| opbnb | WBNB | native | $8.7k | $8.8k | 10.4k | 1.00 |
| opbnb | BNB | native | $269 | $233 |  | 0.86 |
| opbnb | THE | other | $57 | $58 | 1.7k | 1.00 |
| algorand | USDC | usd_stable | $248.7M | $246.3M | 57.9k | 0.99 |
| algorand | ALGO | native | $46.8M | $35.7M | 99.0k | 0.72 |
| algorand | FOLKS | other | $219.0k | $176.9k | 4.2k | 0.82 |
| algorand | xALGO | other | $37.6k | $24.6k | 3.1k | 0.60 |
| algorand | fALGO | other | $27.8k | $23.6k | 471 | 0.83 |
| arbitrum | USDC | usd_stable | $1.6B | $809.5M | 574.4k | 0.48 |
| arbitrum | USDT0 | usd_stable | $215.6M | $156.3M | 120.4k | 0.72 |
| arbitrum | WETH | eth | $93.4M | $57.9M | 215.4k | 0.60 |
| arbitrum | WBTC | btc | $33.0M | $26.2M | 17.0k | 0.78 |
| arbitrum | MAGIC | other | $21.8M | $11.8M | 31.7k | 0.39 |
| near | NEAR | native | $162.4M | $129.8M | 7.8M | 0.83 |
| near | wNEAR | native | $3.2M | $2.1M | 22.0k | 0.60 |
| near | XRP | other | $844.1k | $851.0k | 2.4k | 1.00 |
| near | USDC | usd_stable | $494.2k | $249.8k | 19.6k | 0.32 |
| near | USDt | usd_stable | $85.5k | $86.2k | 2.4k | 1.00 |
| arc | USDC | usd_stable | $16.6M | $2.5M |  | 0.06 |
| arc | EURC | eur_stable | $1.2M | $1.2M | 2.6k | 1.00 |
| arc | USDC | usd_stable | $99.8k | $46.5k | 32.4k | 0.31 |
| arc | COOL | other | $14.9k | $14.9k | 2.6k | 1.00 |
| arc | POLL | other | $14.7k | $14.7k | 4.3k | 1.00 |
| celo | BRLA | other | $3.5M | $2.5M | 2.2k | 0.67 |
| celo | axlUSDC | other | $2.6M | $2.6M | 1.3k | 1.00 |
| celo | USDT0 | usd_stable | $2.6M | $1.3M | 6.6M | 0.50 |
| celo | celo | native | $165.0k | $90.5k | 1.0M | 0.36 |
| celo | XAUT | other | $99.2k | $61.3k | 13.8k | 0.87 |
| bitcoin | BTC | btc | $45.1B | $0 | 754.7k | 0.05 |
| dydx | USDC.n | usd_stable | $815 | $758 | 70.3k | 0.93 |
| hedera | HBAR | native | $1.9M | $1.1M | 173.8k | 0.55 |
| hedera | USDC | usd_stable | $1.3M | $1.1M | 1.1k | 0.81 |
| hedera | WHBAR | native | $252.7k | $253.0k | 1.1k | 1.00 |
| hedera | HSUITE | other | $2.6k | $2.6k | 264 | 1.00 |
| hedera | STEAM | other | $282 | $282 | 1.8k | 1.00 |
| unichain | USDC | usd_stable | $2.0M | $1.9M | 15.1k | 0.94 |
| unichain | HYPE | other | $1.9M | $1.9M | 4.8k | 0.97 |
| unichain | WETH | eth | $128.9k | $94.6k | 1.7k | 0.65 |
| unichain | WBTC | btc | $99.5k | $99.6k | 432 | 1.00 |
| unichain | ETH | eth | $99.4k | $99.6k |  | 1.00 |
| plasma | USDT0 | usd_stable | $46.6M | $19.6M | 83.3k | 0.31 |
| plasma | XPL | native | $2.7M | $2.7M |  | 1.00 |
| plasma | WXPL | native | $828.1k | $438.1k | 11.3k | 0.40 |
| plasma | WETH | eth | $3 | $3 | 1.5k | 1.00 |
| worldchain | WLD | other | $1.8M | $690.5k | 296.1k | 0.27 |
| worldchain | USDC.e | usd_stable | $371.4k | $217.0k | 72.4k | 0.57 |
| worldchain | Re7WLD | other | $219.4k | $49.7k | 34.3k | 0.18 |
| worldchain | wARS | other | $78.1k | $76.6k | 1.7k | 0.98 |
| worldchain | Re7WARS | other | $76.6k | $76.6k | 1.3k | 1.00 |
| xlayer | USDT0 | usd_stable | $134.5M | $131.0M | 167.6k | 0.97 |
| xlayer | USDC | usd_stable | $25.1M | $19.5M | 18.1k | 0.75 |
| xlayer | USDG | usd_stable | $2.8M | $745.4k | 126.1k | 0.16 |
| xlayer | xETH | other | $2.0M | $1.7M | 5.6k | 0.82 |
| xlayer | OKB | native | $1.6M | $533.2k | 38.9k | 0.18 |
| flare | FLR | native | $116.4M | $116.2M |  | 1.00 |
| flare | USDT0 | usd_stable | $8.5M | $7.6M | 4.7k | 0.89 |
| flare | FXRP | other | $2.4M | $1.9M | 5.8k | 0.78 |
| flare | APS | other | $1.1M | $875.4k | 779 | 0.80 |
| flare | WFLR | native | $753.0k | $578.3k | 5.8k | 0.72 |
| pulsechain | PLS | native | $875.4k | $537.2k |  | 0.61 |
| pulsechain | vPLS | other | $484.8k | $480.2k | 379 | 1.00 |
| pulsechain | WPLS | native | $405.1k | $85.1k | 108.6k | 0.11 |
| pulsechain | HEX | other | $364.6k | $163.4k | 16.8k | 0.42 |
| pulsechain | USDC | usd_stable | $271.5k | $95.2k | 12.2k | 0.29 |
| ronin | PIXEL | other | $2.4M | $1.4M | 13.4k | 0.49 |
| ronin | RON | native | $1.2M | $751.2k |  | 0.54 |
| ronin | WRON | native | $822.4k | $310.6k | 43.4k | 0.30 |
| ronin | WETH | eth | $469.4k | $207.0k | 51.8k | 0.31 |
| ronin | USDC | usd_stable | $271.8k | $143.4k | 14.7k | 0.36 |
| soneium | USDC | usd_stable | $29.5k | $17.5k | 7.6k | 0.56 |
| soneium | ASTAR | other | $16.6k | $16.3k | 2.2k | 0.98 |
| soneium | ETH | eth | $6.4k | $2.4k |  | 0.30 |
| soneium | USDSC | other | $5.3k | $2.7k | 1.7k | 0.36 |
| soneium | WETH | eth | $3.9k | $1.9k | 4.1k | 0.35 |
| hyperevm | USDC | usd_stable | $220.0M | $76.0M | 128.6k | 0.25 |
| hyperevm | HYPE | native | $163.3M | $159.6M |  | 0.98 |
| hyperevm | WHYPE | native | $30.7M | $6.2M | 103.6k | 0.11 |
| hyperevm | USDT0 | usd_stable | $16.9M | $10.1M | 32.5k | 0.56 |
| hyperevm | UETH | other | $3.0M | $1.9M | 4.4k | 0.58 |
| gnosis | EURe | eur_stable | $382.5k | $187.8k | 8.1k | 0.49 |
| gnosis | USDC.e | usd_stable | $282.2k | $203.5k | 10.2k | 0.72 |
| gnosis | sDAI | other | $167.8k | $94.0k | 38.9k | 0.37 |
| gnosis | wstETH | eth | $139.2k | $72.5k | 3.4k | 0.36 |
| gnosis | WXDAI | native | $113.5k | $71.7k | 101.9k | 0.54 |
| cardano | USDCX | usd_stable | $34.5M | $34.6M | 13.5k | 0.96 |
| cardano | ADA | native | $19.5M | $2.3M | 292.6k | 0.05 |
| cardano | USDM | usd_stable | $7.4M | $7.4M | 9.6k | 0.96 |
| cardano | NIGHT | other | $5.0M | $4.4M | 24.9k | 0.84 |
| cardano | SNEK | other | $463.8k | $483.7k | 5.7k | 1.00 |
| starknet | STRK | native | $59.4M | $17.4M | 451.7k | 0.19 |
| starknet | USDC | usd_stable | $22.8M | $4.7M | 120.5k | 0.15 |
| starknet | ZEC | other | $19.3M | $19.2M | 3.0k | 1.00 |
| starknet | ETH | eth | $6.9M | $1.9M | 49.1k | 0.19 |
| starknet | WBTC | btc | $1.8M | $1.5M | 9.5k | 0.80 |
| plume | WPLUME | native | $19 | $19 | 2.1k | 1.00 |
| plume | nCREDIT | other | $11 | $11 | 1.1k | 1.00 |
| plume | PLUME | native | $0 | $0 |  |  |
| avalanche | WAVAX | native | $180.7M | $44.2M | 81.6k | 0.14 |
| avalanche | AvalancheUSDC | other | $142.4M | $42.9M | 77.3k | 0.18 |
| avalanche | USDT | usd_stable | $94.2M | $52.7M | 27.2k | 0.41 |
| avalanche | AVAX | native | $18.7M | $14.2M |  | 0.75 |
| avalanche | WETH | eth | $9.1M | $4.0M | 8.9k | 0.26 |
| ink | USDT0 | usd_stable | $22.5M | $22.5M | 9.1k | 1.00 |
| ink | WETH | eth | $10.9M | $10.8M | 9.5k | 0.99 |
| ink | kBTC | btc | $7.8M | $7.8M | 432 | 1.00 |
| ink | USDC | usd_stable | $242.4k | $242.7k | 864 | 1.00 |
| ink | oUSDT | other | $145.2k | $145.4k | 864 | 1.00 |
| thorchain | RUNE | native | $3.8M | $1.6M | 115.6k | 0.35 |
| blast | ETH | eth | $26.2k | $23.4k |  | 0.89 |
| blast | blast | other | $6.4k | $6.4k | 1.5k | 1.00 |
| blast | WETH | eth | $707 | $675 | 16.2k | 0.95 |
| blast | BLASTUP | other | $676 | $676 | 864 | 1.00 |
| blast | USDB | usd_stable | $30 | $15 | 1.9k | 0.34 |
| kaia | USD₮ | usd_stable | $29.9M | $22.1M | 107.1k | 0.72 |
| kaia | WKLAY | other | $918.7k | $379.3k | 32.8k | 0.29 |
| kaia | KAIA | native | $529.2k | $261.1k |  | 0.31 |
| kaia | USDT | usd_stable | $51.1k | $29.6k | 12.5k | 0.50 |
| kaia | bora | other | $49.3k | $49.3k | 2.2k | 1.00 |
| litecoin | LTC | native | $1.7B | $0 | 164.1k | 0.02 |
| celestia | TIA | native | $15.3M | $14.5M | 4.5k | 0.95 |
| sonic | wS | native | $13.0M | $6.2M | 32.5k | 0.32 |
| sonic | USDC | usd_stable | $11.8M | $5.6M | 25.0k | 0.33 |
| sonic | WETH | eth | $8.3M | $5.5M | 6.2k | 0.46 |
| sonic | S | native | $1.1M | $652.6k |  | 0.54 |
| sonic | USSD | other | $60.0k | $35.5k | 3.9k | 0.54 |
| tezos | XTZ | native | $2.3M | $0 | 79.9k |  |
| tezos | stXTZ | other | $13.4k | $0 | 184 |  |
| tezos | oXTZ | other | $2.7k | $0 | 527 |  |
| tezos | USDt | usd_stable | $1.6k | $0 | 88 |  |
| tezos | uUSD | other | $302 | $0 | 122 |  |
| abstract | USDC.e | usd_stable | $1.2M | $713.2k | 14.9k | 0.55 |
| abstract | ETH | eth | $295.4k | $84.4k | 229.9k | 0.16 |
| abstract | ETH | eth | $191.6k | $62.5k |  | 0.25 |
| abstract | WETH | eth | $112.1k | $68.0k | 7.3k | 0.42 |
| abstract | PENGU | other | $49.4k | $46.9k | 8.0k | 0.95 |
| berachain | BERA | native | $320.1k | $235.1k |  | 0.67 |
| berachain | WBERA | native | $93.9k | $58.4k | 79.3k | 0.54 |
| berachain | USDC.e | usd_stable | $71.6k | $51.7k | 1.5k | 0.60 |
| berachain | HONEY | other | $61.1k | $43.4k | 864 | 0.54 |
| berachain | sWBERA | other | $23.5k | $20.1k | 2.2k | 0.85 |
| osmosis | USDC.n | usd_stable | $471.1M | $56.2M | 32.1k | 0.02 |
| osmosis | ATOM | other | $2.5M | $1.1M | 23.6k | 0.39 |
| osmosis | USDC | usd_stable | $1.4M | $466.4k | 19.9k | 0.30 |
| osmosis | USDC | usd_stable | $441.2k | $413.9k | 6.4k | 0.94 |
| osmosis | USDT | usd_stable | $424.1k | $414.0k | 666 | 0.98 |
| tempo | USDC.e | usd_stable | $112.2M | $112.4M | 52.5k | 1.00 |
| tempo | USDT0 | usd_stable | $16.6k | $15.1k | 3.0k | 0.90 |
| tempo | pathUSD | usd_stable | $4.8k | $4.8k | 31.5k | 0.99 |
| tempo | senpathUSD | other | $4.8k | $4.8k | 2.3k | 0.99 |
| tempo | OUSD | usd_stable | $2 | $2 | 4.5k | 0.89 |
| cronos | WCRO | native | $1.0M | $339.5k | 37.9k | 0.20 |
| cronos | CRO | native | $552.2k | $256.1k |  | 0.37 |
| cronos | ULTCAT | other | $83.9k | $76.4k | 7.0k | 0.91 |
| cronos | USDC | usd_stable | $65.0k | $37.8k | 6.0k | 0.38 |
| cronos | PENGU | other | $40.0k | $40.1k | 999 | 1.00 |
| core | CORE | native | $43.4k | $20.9k |  | 0.36 |
| core | WCORE | native | $870 | $869 | 288 | 1.00 |
| core | WCORE | native | $543 | $375 | 1.3k | 0.56 |
| core | USDT | usd_stable | $531 | $381 | 288 | 0.58 |
| core | PZP | other | $12 | $7 | 576 | 0.40 |
| dogecoin | DOGE | native | $966.9M | $0 | 17.4k |  |
| cosmoshub | ATOM | native | $9.5M | $3.8M | 51.7k | 0.33 |
| cosmoshub | USDC | usd_stable | $377 | $376 | 78 | 1.00 |
| cosmoshub | ETH | eth | $155 | $155 | 390 | 1.00 |
| cosmoshub | USDC.inj | usd_stable | $62 | $62 | 78 | 1.00 |
| cosmoshub | stATOM | other | $0 | $0 | 78 | 1.00 |
| katana | vbETH | other | $37.6M | $37.5M | 1.8k | 1.00 |
| katana | vbUSDC | other | $35.6M | $35.5M | 2.2k | 1.00 |
| katana | KAT | other | $9.2M | $9.2M | 1.3k | 1.00 |
| katana | ETH | eth | $0 | $0 |  |  |
| zksync | zk | other | $9.5M | $4.5M | 6.4k | 0.43 |
| zksync | WETH | eth | $567.0k | $200.2k | 8.0k | 0.31 |
| zksync | ETH | eth | $468.9k | $192.3k | 47.2k | 0.38 |
| zksync | USDC | usd_stable | $101.7k | $53.9k | 2.4k | 0.50 |
| zksync | USDT | usd_stable | $84.9k | $53.4k | 738 | 0.44 |
| sei | wSEI | native | $6.9M | $3.8M | 14.2k | 0.39 |
| sei | USDC | usd_stable | $5.1M | $3.3M | 6.6k | 0.54 |
| sei | WBTC | btc | $99.5k | $79.6k | 1.9k | 0.76 |
| sei | USDT0 | usd_stable | $33.7k | $33.8k | 947 | 1.00 |
| sei | WETH | eth | $25.5k | $23.8k | 3.8k | 0.93 |
| bitcoin-cash | BCH | native | $162.7M | $0 | 11.3k |  |
| linea | USDC | usd_stable | $194.2k | $106.1k | 2.0k | 0.47 |
| linea | ETH | eth | $186.2k | $120.6k |  | 0.67 |
| linea | LINEA | other | $178.5k | $67.8k | 1.2k | 0.23 |
| linea | USDT | usd_stable | $99.6k | $90.0k | 845 | 0.91 |
| linea | mUSD | usd_stable | $29.9k | $15.2k | 282 | 0.41 |
| noble | USDC | usd_stable | $501.3M | $35.7M | 6.5k | 0.02 |
| scroll | SCR | other | $142.6k | $138.9k | 341 | 0.98 |
| scroll | ETH | eth | $37.0k | $11.6k | 4.6k | 0.21 |
| scroll | USDC | usd_stable | $22.0k | $8.2k | 1.9k | 0.21 |
| scroll | ETH | eth | $21.2k | $15.8k |  | 0.74 |
| scroll | USDT | usd_stable | $12.1k | $3.8k | 682 | 0.36 |
| mantle | USDT | usd_stable | $2.4M | $2.2M | 2.4k | 0.91 |
| mantle | MNT | native | $2.3M | $2.3M |  | 0.97 |
| mantle | SVL | other | $2.3M | $2.3M | 216 | 1.00 |
| mantle | WMNT | native | $269.2k | $205.9k | 1.9k | 0.75 |
| mantle | mETH | eth | $6.9k | $6.2k | 432 | 0.89 |
| zcash | ZEC | native | $423.2M | $0 | 6.4k |  |
| rootstock | RBTC | native | $101.1k | $83.6k |  | 0.84 |

## Cross-source agreement

41 checks passed, 4 failed (tolerance ±25% on transaction counts).

| check | ok | detail |
|---|---|---|
| `tx-cross-source:abstract:l2beat` | ok | probe 86.1k/day (sampled-blocks) vs l2beat 87.4k/day: x0.986 |
| `tx-cross-source:arbitrum:growthepie` | ok | probe 1.2M/day (sampled-blocks) vs growthepie 1.2M/day: x0.998 |
| `tx-cross-source:arbitrum:l2beat` | ok | probe 1.2M/day (sampled-blocks) vs l2beat 1.2M/day: x0.997 |
| `tx-cross-source:base:growthepie` | ok | probe 6.0M/day (sampled-blocks) vs growthepie 6.0M/day: x0.994 |
| `tx-cross-source:base:l2beat` | ok | probe 6.0M/day (sampled-blocks) vs l2beat 6.0M/day: x0.994 |
| `tx-cross-source:bitcoin-cash:blockchair-24h` | ok | probe 11.3k/day (aggregator-24h) vs blockchair-24h 11.3k/day: x1.000 |
| `tx-cross-source:blast:l2beat` | ok | probe 182.1k/day (sampled-blocks) vs l2beat 181.8k/day: x1.002 |
| `tx-cross-source:celo:growthepie` | ok | probe 788.4k/day (sampled-blocks) vs growthepie 841.6k/day: x0.937 |
| `tx-cross-source:celo:l2beat` | ok | probe 788.4k/day (sampled-blocks) vs l2beat 841.6k/day: x0.937 |
| `tx-cross-source:dogecoin:blockchair-24h` | ok | probe 17.4k/day (aggregator-24h) vs blockchair-24h 17.4k/day: x1.001 |
| `tx-cross-source:ethereum:growthepie` | ok | probe 1.6M/day (sampled-blocks) vs growthepie 1.6M/day: x0.973 |
| `tx-cross-source:gnosis:l2beat` | ok | probe 318.0k/day (sampled-blocks) vs l2beat 315.8k/day: x1.007 |
| `tx-cross-source:ink:growthepie` | ok | probe 192.7k/day (sampled-blocks) vs growthepie 214.7k/day: x0.897 |
| `tx-cross-source:ink:l2beat` | ok | probe 192.7k/day (sampled-blocks) vs l2beat 214.8k/day: x0.897 |
| `tx-cross-source:katana:l2beat` | ok | probe 15.7k/day (sampled-blocks) vs l2beat 18.0k/day: x0.873 |
| `tx-cross-source:linea:growthepie` | ok | probe 10.0k/day (sampled-blocks) vs growthepie 10.1k/day: x0.987 |
| `tx-cross-source:linea:l2beat` | ok | probe 10.0k/day (sampled-blocks) vs l2beat 10.1k/day: x0.987 |
| `tx-cross-source:mantle:growthepie` | **FAIL** | probe 7.6k/day (sampled-blocks) vs growthepie 10.1k/day: x0.749 |
| `tx-cross-source:mantle:l2beat` | **FAIL** | probe 7.6k/day (sampled-blocks) vs l2beat 10.1k/day: x0.749 |
| `tx-cross-source:megaeth:growthepie` | **FAIL** | probe 2.0M/day (sampled-blocks) vs growthepie 1.1M/day: x1.767 |
| `tx-cross-source:megaeth:l2beat` | ok | probe 2.0M/day (sampled-blocks) vs l2beat 2.0M/day: x0.997 |
| `tx-cross-source:near:nearblocks` | ok | probe 902.5k/day (sampled-blocks) vs nearblocks 850.3k/day: x1.061 |
| `tx-cross-source:optimism:growthepie` | ok | probe 1.5M/day (sampled-blocks) vs growthepie 1.6M/day: x0.957 |
| `tx-cross-source:plume:growthepie` | ok | probe 210.2k/day (sampled-blocks) vs growthepie 210.6k/day: x0.998 |
| `tx-cross-source:polygon:growthepie` | ok | probe 4.9M/day (sampled-blocks) vs growthepie 4.8M/day: x1.006 |
| `tx-cross-source:polygon:l2beat` | ok | probe 4.9M/day (sampled-blocks) vs l2beat 4.8M/day: x1.006 |
| `tx-cross-source:robinhood:growthepie` | ok | probe 4.2M/day (sampled-blocks) vs growthepie 4.1M/day: x1.016 |
| `tx-cross-source:robinhood:l2beat` | ok | probe 4.2M/day (sampled-blocks) vs l2beat 4.1M/day: x1.015 |
| `tx-cross-source:ronin:growthepie` | ok | probe 407.2k/day (sampled-blocks) vs growthepie 454.7k/day: x0.895 |
| `tx-cross-source:scroll:growthepie` | ok | probe 8.3k/day (sampled-blocks) vs growthepie 9.2k/day: x0.908 |
| `tx-cross-source:scroll:l2beat` | ok | probe 8.3k/day (sampled-blocks) vs l2beat 9.2k/day: x0.908 |
| `tx-cross-source:soneium:growthepie` | ok | probe 351.0k/day (sampled-blocks) vs growthepie 342.4k/day: x1.025 |
| `tx-cross-source:soneium:l2beat` | ok | probe 351.0k/day (sampled-blocks) vs l2beat 342.5k/day: x1.025 |
| `tx-cross-source:starknet:growthepie` | ok | probe 274.8k/day (sampled-blocks) vs growthepie 224.1k/day: x1.227 |
| `tx-cross-source:starknet:l2beat` | ok | probe 274.8k/day (sampled-blocks) vs l2beat 230.1k/day: x1.195 |
| `tx-cross-source:tron:tronscan` | ok | probe 10.9M/day (sampled-blocks) vs tronscan 11.1M/day: x0.985 |
| `tx-cross-source:unichain:growthepie` | ok | probe 615.2k/day (sampled-blocks) vs growthepie 622.3k/day: x0.988 |
| `tx-cross-source:unichain:l2beat` | ok | probe 615.2k/day (sampled-blocks) vs l2beat 622.4k/day: x0.988 |
| `tx-cross-source:worldchain:growthepie` | ok | probe 584.3k/day (sampled-blocks) vs growthepie 593.8k/day: x0.984 |
| `tx-cross-source:xlayer:l2beat` | ok | probe 555.1k/day (sampled-blocks) vs l2beat 564.1k/day: x0.984 |
| `tx-cross-source:zcash:blockchair-24h` | ok | probe 6.4k/day (aggregator-24h) vs blockchair-24h 6.4k/day: x0.999 |
| `tx-cross-source:zksync:growthepie` | ok | probe 15.5k/day (sampled-blocks) vs growthepie 16.6k/day: x0.934 |
| `dex-breakdown` | **FAIL** | sum of per-chain 24h $5.2B vs DefiLlama total24h $5.5B (x0.9407) |
| `llama-keys` | ok | 0 contested of 263 inferred keys:  |
| `registry-ids` | ok | all registry identities resolve |

Probe failures: solana (RpcError: {"code": -32602, "message": "BigTable query failed (maybe timeout due ); xdc (RpcError: {"code": -32603, "message": "failsafe timeout policy exceeded on netwo)
