# Chain activity — 2026-10-10

Census of 567 chains from DefiLlama, growthepie, L2Beat, Blockchair, Tronscan, NEARBlocks, CoinGecko and Hyperliquid (days before 2026-10-10 UTC are complete); direct probe of 67 registry chains over 2026-10-09T00:00:00+00:00 → 2026-10-10T00:00:00+00:00 (24.0 h).

Tiers (how reasonable it is to trade there): deep 12, tradeable 27, token_only 33, thin 75, inactive 420.

## The list: chains by activity

Ranked by the mean percentile across DEX volume, fees, stablecoin float, TVL and transactions (at least three of the five measured). DEX, fees and transactions from the aggregators are 7-day daily averages, except where an aggregator has the probe's own day ("same day"); probe columns are the direct reading of one UTC day, with its standard error where it is a sample. Transfer value is net per transaction (see the probe docstring); `†` marks an asset whose estimate comes mostly from one sampled block, i.e. one large transfer scaled up.

| # | chain | family | tier | DEX/day | stables | TVL | fees/day | tx/day (aggregator) | tx/day (probe) | transfers/day (probe) | top assets moved (probe) |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Solana | solana | deep | $1.9B | $16.0B | $6.2B | $15.0M |  | 159.9M ±5.3M | $9.6B | SOL $4.2B, usdc $1.9B, SOL $1.7B |
| 2 | BSC | evm | deep | $765.2M | $13.3B | $5.6B | $2.7M |  | 14.0M ±271.0k | $4.5B | USDT $2.3B, USDC $535.5M†, SHARE $385.6M† |
| 3 | Base | evm | deep | $1.0B | $5.2B | $6.2B | $1.7M | 6.9M (growthepie, same day) | 6.9M ±175.0k | $185.6B | USDC $74.1B, WETH $66.3B, cbBTC $30.2B |
| 4 | Hyperliquid L1 (hyperevm) | evm | deep | $244.9M | $7.2B | $1.1B | $5.1M |  | 291.2k ±22.7k | $421.2M | USDC $323.0M, WHYPE $64.9M, USDT0 $12.6M |
| 5 | Ethereum | evm | deep | $1.4B | $144.8B | $51.4B | $11.5M | 1.8M (growthepie, same day) | 1.8M ±44.2k | $40.6B | USDC $18.8B, USDT $8.9B, ETH $3.7B |
| 6 | Tron | tron | deep | $52.8M | $95.0B | $5.7B | $246.4k | 11.7M (tronscan, same day) | 11.6M ±154.7k | $34.1B | USDT $31.7B, TRX $2.1B, USDD $125.4M |
| 7 | Robinhood Chain | evm | deep | $988.3M | $1.1B | $1.0B | $3.2M | 5.6M (growthepie, same day) | 5.7M ±427.4k | $2.0B | USDG $642.2M, WETH $595.3M, ETH $312.0M |
| 8 | Polygon | evm | deep | $219.3M | $2.9B | $678.0M | $1.2M | 5.3M (growthepie, same day) | 5.3M ±95.8k | $1.8B | USDC $633.5M, pUSD $355.1M, USDT0 $288.0M |
| 9 | Avalanche | evm | deep | $140.9M | $1.4B | $627.2M | $361.3k |  | 244.3k ±22.5k | $465.1M | WAVAX $183.2M, AvalancheUSDC $156.6M, USDT $50.3M† |
| 10 | Arbitrum | evm | deep | $132.6M | $3.8B | $1.4B | $306.2k | 1.4M (growthepie, same day) | 1.4M ±89.7k | $1.4B | USDC $877.6M, ETH $207.1M†, USDT0 $129.6M |
| 11 | Monad | evm | tradeable | $41.2M | $736.8M | $1.0B | $214.2k |  | 4.8M ±104.9k | $1.5B | USDC $1.4B†, AUSD $48.2M†, USDat $6.5M† |
| 12 | OP Mainnet (optimism) | evm | tradeable | $94.6M | $644.1M | $452.8M | $379.5k | 1.5M (growthepie, same day) | 1.5M ±38.8k | $12.7B | WETH $5.9B, USDC $5.6B, velo $798.8M |
| 13 | Arc | evm | tradeable | $44.3M | $496.7M | $561.1M | $167.3k |  | 783.4k ±38.0k | $155.8M | USDC $92.7M†, USDC $51.0M, WETH $11.7M |
| 14 | Sui | sui | tradeable | $38.8M | $487.0M | $527.5M | $115.2k |  | 5.4M ±115.5k | $746.5M | SUI $392.5M, USDSUI $192.0M†, DEEP $55.1M |
| 15 | Plasma | evm | tradeable | $4.7M | $1.3B | $511.5M | $130.5k |  | 618.8k ±20.6k | $2.6B | USDT0 $2.6B†, WXPL $868.6k†, XPL $1.8k† |
| 16 | Near | near | deep | $165.9M | $129.6M | $247.0M | $199.4k | 680.3k (nearblocks, same day) | 713.8k ±94.3k | $272.6M | USDC $161.6M†, DAI $51.3M†, USDT $29.3M† |
| 17 | X Layer | evm | deep | $18.0M | $1.6B | $164.7M | $27.1k | 731.8k (l2beat, same day) | 730.1k ±25.3k | $144.8M | xETH $88.9M†, USDG $19.7M, USDT0 $13.2M† |
| 18 | TON | ton | tradeable | $5.0M | $719.0M | $52.5M | $1.2M |  | 3.8M ±106.3k | $196.2M | TON $131.9M†, USD₮ $55.7M, tsTON $6.4M |
| 19 | Stellar | stellar | tradeable | $1.7M | $931.7M | $253.8M | $187.3k | 4.7M (blockchair-24h) | 4.9M | $42.2M | USDC $23.7M, XLM $15.8M, CETES $1.8M† |
| 20 | XRPL | xrpl | tradeable | $5.1M | $1.2B | $42.3M | $28.7k | 2.0M (blockchair-24h) | 1.9M ±241.6k | $686.7M | XRP $385.5M, OUSG $279.9M†, RLUSD $21.3M† |
| 21 | Aptos | aptos | tradeable | $5.8M | $904.5M | $49.7M | $53.1k |  | 8.6M | $248.0M | USDC $227.7M†, USDt $19.8M†, APT $431.1k† |
| 22 | THORChain | cosmos | token_only | $32.4M | - | $36.4M | $17.5k |  | 186.8k | $11.3M | RUNE $11.3M, RUJI $3.2k† |
| 23 | Sei | evm | tradeable | $7.2M | $309.0M | $33.1M | $41.9k |  | 11.4k ±3.8k | $3.2M | wSEI $1.3M, USDC $788.1k†, SEI $750.5k† |
| 24 | Chainflip |  | thin | $16.6M | - | $16.1M | $52.0k |  |  |  |  |
| 25 | Ink | evm | tradeable | $3.0M | $184.2M | $206.9M | $146.1k | 253.0k (growthepie, same day) | 199.6k ±9.1k | $339.0M | USDT0 $218.9M†, WETH $90.8M, kBTC $23.8M† |
| 26 | Starknet | starknet | tradeable | $21.6M | $152.4M | $165.3M | $58.5k | 212.3k (growthepie, same day) | 259.9k ±30.0k | $227.4M | ETH $75.4M†, STRK $65.1M, ZEC $44.2M† |
| 27 | Cronos | evm | tradeable | $2.7M | $139.0M | $152.4M | $18.6k |  | 88.3k ±19.5k | $13.5M | WCRO $5.1M†, CRO $3.9M†, CROCAT $2.3M† |
| 28 | Canton |  | token_only | $38.7M | - | $12.1M | $17.0k |  |  |  |  |
| 29 | Flare | evm | tradeable | $4.9M | $49.1M | $126.3M | $21.5k |  | 373.3k ±67.2k | $42.8M | FLR $38.2M†, FXRP $2.0M, USDT0 $1.4M |
| 30 | Cardano | cardano | tradeable | $3.3M | $71.4M | $69.9M | $30.4k | 343.4k (blockchair-24h) | 249.6k | $229.1M | ADA $225.4M, NIGHT $1.4M†, USDA $1.1M† |
| 31 | Mantle | evm | tradeable | $4.0M | $553.4M | $107.0M | $56.8k | 11.7k (growthepie, same day) | 14.7k ±2.1k | $7.1M | USDT $3.2M†, WMNT $2.2M†, WETH $1.3M† |
| 32 | Unichain | evm | tradeable | $7.8M | $25.3M | $27.2M | $18.3k | 635.7k (growthepie, same day) | 640.7k ±6.3k | $21.5M | USDC $10.0M†, HYPE $9.4M†, WETH $929.7k |
| 33 | PulseChain | evm | tradeable | $3.6M | $32.8M | $74.0M | $9.7k |  | 412.2k ±17.9k | $4.2M | ETH $896.1k, WPLS $817.9k, HEX $749.8k |
| 34 | Bitcoin | utxo | token_only | $364.0k | - | $4.4B | $9.8k | 598.8k (blockchair-24h) | 657.3k | $65.8B (gross) | BTC $65.8B |
| 35 | Gnosis | evm | tradeable | $3.1M | $15.5M | $95.9M | $14.3k | 437.0k (l2beat, same day) | 428.7k ±16.1k | $15.4M | EURe $4.1M†, EURe $3.1M†, aGnoEURe $2.5M† |
| 36 | Sonic | evm | tradeable | $1.7M | $157.1M | $17.6M | $6.6k |  | 214.5k ±39.2k | $64.4M | USDC $34.0M†, wS $18.1M, WETH $10.0M |
| 37 | BOT Chain |  | thin | $2.1M | - | $32.0M | $6.5k |  |  |  |  |
| 38 | Hedera | hedera | tradeable | $2.7M | $48.1M | $37.1M | $7.3k |  | 570.7k | $23.9M | HBAR $21.3M†, WHBAR $901.9k, USDC $873.0k |
| 39 | Celo | evm | tradeable | $1.3M | $111.6M | $14.4M | $4.2k | 892.7k (growthepie, same day) | 889.5k ±20.0k | $60.7M | cUSD $25.7M†, CELO $20.5M†, axlUSDC $9.4M† |
| 40 | Stacks |  | tradeable | $3.1M | $11.5M | $93.1M | $6.9k |  |  |  |  |
| 41 | Algorand | algorand | token_only | $505.8k | $64.2M | $35.0M | $7.4k |  | 1.2M | $19.3M | USDC $16.3M, ALGO $2.8M, FOLKS $73.2k† |
| 42 | Provenance |  | tradeable | $18.3M | $460.3M | $146.9M | $35 |  |  |  |  |
| 43 | edgeX L1 |  | thin | $31.7M | $2.3M | - | $78.8k |  |  |  |  |
| 44 | Berachain | evm | thin | $645.1k | $58.6M | $38.1M | $3.9k |  | 73.7k ±2.8k | $1.5M | BERA $1.2M†, WBERA $75.6k, sWBERA $53.2k† |
| 45 | MegaETH | evm | thin | $572.2k | $19.1M | $13.0M | $6.3k | 1.1M (growthepie, same day) | 2.0M ±20.5k | $3.8M | MEGA $3.6M†, USDm $188.7k, ETH $18.0k† |
| 46 | World Chain | evm | token_only | $530.8k | $16.2M | $43.5M | $2.8k | 629.6k (growthepie, same day) | 640.0k ±13.7k | $23.2M | WLD $22.6M, USDC.e $315.0k, Re7WLD $152.6k |
| 47 | Dexalot |  | thin | $28.5M | - | $1.8M | $2.9k |  |  |  |  |
| 48 | Hydration |  | thin | $934.0k | $13.6M | $56.5M | $4.4k |  |  |  |  |
| 49 | Kaia | evm | token_only | $839.6k | $222.0M | $9.3M | $1.1k |  | 437.9k ±83.6k | $54.9M | KAIA $32.9M, USD₮ $14.1M, WKLAY $2.8M |
| 50 | Vaulta |  | token_only | $4.9M | $1.7M | $50.7M | $4.3k |  |  |  |  |
| 51 | Pharos |  | thin | - | $12.0M | $73.4M | $1.7k |  |  |  |  |
| 52 | Tempo | evm | tradeable | $1.1M | $730.9M | $106.1M | $24 |  | 63.6k ±6.5k | $54.4M | USDC.e $51.6M, pathUSD $1.8M†, senpathUSD $1.0M† |
| 53 | ZKsync Era | evm | token_only | $404.9k | $36.1M | $15.1M | $67.3k | 18.5k (growthepie, same day) | 17.9k ±580 | $37.0M | zk $21.2M, WETH $4.6M†, ETH $4.5M† |
| 54 | Abstract | evm | thin | $1.8M | $3.5M | $4.9M | $84.0k | 105.4k (l2beat, same day) | 105.5k ±3.7k | $10.3M | ETH $4.5M†, WETH $1.7M, PENGU $1.6M† |
| 55 | Osmosis | cosmos | thin | $567.0k | $17.2M | $10.9M | $6.4k |  | 45.5k ±2.7k | $119.8M | USDC.n $103.7M, ATOM $8.9M, USDC $5.9M |
| 56 | Mezo |  | thin | $72.8k | $28.8M | $75.0M | $4.9k |  |  |  |  |
| 57 | Flow |  | thin | $496.5k | $71.7M | $11.5M | $1.4k |  |  |  |  |
| 58 | Katana | evm | thin | $526.2k | $10.2M | $40.5M | $8.0k | 25.1k (l2beat, same day) | 24.6k ±4.8k | $1.4M | KAT $611.4k†, vbUSDC $443.7k, vbETH $255.1k† |
| 59 | Mixin |  | thin | $32.9k | $34.5M | $77.1M | - |  |  |  |  |
| 60 | Rootstock | evm | thin | $419.7k | $11.4M | $82.4M | $1.6k |  | 6.1k ±334 | $1.9k | RBTC $1.9k† |

Probed but outside the aggregator ranking: CosmosHub 21.2k tx/day (exact-blocks); Celestia 138.5k tx/day (sampled-blocks); Noble 3.9k tx/day (exact-index); dYdX 708.4k tx/day (sampled-blocks)

## The list, measured directly: every probed chain by transactions

One row per registry chain the probe read, busiest first. `$/tx` is net transfer value per transaction: a chain with millions of transactions and cents per transaction is busy with bots, not with money. `bookkeeping` is the share of transactions sent to registry-listed oracle, validator-signing or block-builder contracts — real transactions that are not activity (the headline keeps them, as L2Beat does). `top target` is the contract that received the largest share of transactions (and of value): one address carrying most of a chain is one actor, however large the totals.

| chain | family | tier | tx/day | method | bookkeeping | net transfers/day | $/tx | top target by txs | top target by value |
|---|---|---|---:|---|---:|---:|---:|---|---|
| Solana | solana | deep | 159.9M ±5.3M | sampled-blocks |  | $9.6B | $59.79 |  |  |
| BSC | evm | deep | 14.0M ±271.0k | sampled-blocks |  | $4.5B | $317.61 | `0x55d398326f` 13% | `0x55d398326f` 28% |
| Tron | tron | deep | 11.6M ±154.7k | sampled-blocks |  | $34.1B | $2939.17 | `0xa614f803b6` 20% | `0xa614f803b6` 94% |
| Aptos | aptos | tradeable | 8.6M | exact-versions minus sampled system share |  | $248.0M | $28.68 |  |  |
| Base | evm | deep | 6.9M ±175.0k | sampled-blocks |  | $185.6B | $27.0k | `0x833589fcd6` 5% | `0x61040e143a` 43% |
| Robinhood Chain | evm | deep | 5.7M ±427.4k | sampled-blocks |  | $2.0B | $341.06 | `0x62dee0d689` 6% | `0x520ed46786` 18% |
| Sui | sui | tradeable | 5.4M ±115.5k | exact-counter x sampled user share |  | $746.5M | $138.76 |  |  |
| Polygon | evm | deep | 5.3M ±95.8k | sampled-blocks |  | $1.8B | $338.66 | `0xe111180000` 22% | `0xe111180000` 17% |
| Stellar | stellar | tradeable | 4.9M | exact-blocks |  | $42.2M | $8.66 |  |  |
| Monad | evm | tradeable | 4.8M ±104.9k | sampled-blocks |  | $1.5B | $314.83 | `0xd32edf6642` 23% | `0x754704bc05` 95% |
| TON | ton | tradeable | 3.8M ±106.3k | sampled-blocks |  | $196.2M | $52.18 |  |  |
| MegaETH | evm | thin | 2.0M ±20.5k | sampled-blocks | 87% | $3.8M | $1.92 | `0x6342000000` 44% | `0x28b7e77f82` 93% |
| XRPL | xrpl | tradeable | 1.9M ±241.6k | sampled-blocks |  | $686.7M | $358.12 |  |  |
| Ethereum | evm | deep | 1.8M ±44.2k | sampled-blocks |  | $40.6B | $22.4k | `0xdac17f958d` 18% | `0xa0b86991c6` 38% |
| Injective | cosmos | tradeable | 1.6M | exact-index |  | $364.9M | $229.88 |  |  |
| OP Mainnet (optimism) | evm | tradeable | 1.5M ±38.8k | sampled-blocks |  | $12.7B | $8668.00 | `0x1e04602a8b` 24% | `0xf1b41a86d8` 33% |
| Arbitrum | evm | deep | 1.4M ±89.7k | sampled-blocks |  | $1.4B | $937.38 | `0xaf88d065e7` 15% | `0xaf88d065e7` 23% |
| XDC | evm | token_only | 1.3M ±219.9k | sampled-blocks | 49% | $23.5M | $17.77 | `0x0000000000` 49% | `0x26bcd76624` 87% |
| Algorand | algorand | token_only | 1.2M | exact-counter |  | $19.3M | $16.79 |  |  |
| opBNB | evm | inactive | 1.1M ±82.1k | sampled-blocks |  | $7.0k | $0.01 | `0xa596e82b0e` 15% | `0xb8ddeb6191` 60% |
| Celo | evm | tradeable | 889.5k ±20.0k | sampled-blocks |  | $60.7M | $68.28 | `0xbedaccbd65` 42% | `0x4861840c2e` 47% |
| Arc | evm | tradeable | 783.4k ±38.0k | sampled-blocks |  | $155.8M | $198.90 | `0x7e032e56c6` 18% | `0x77777777dc` 80% |
| X Layer | evm | deep | 730.1k ±25.3k | sampled-blocks |  | $144.8M | $198.35 | `0x6558dbe4c1` 34% | `0xe7b000003a` 62% |
| Near | near | deep | 713.8k ±94.3k | sampled-blocks |  | $272.6M | $381.91 |  |  |
| dYdX | cosmos | inactive | 708.4k ±2.1k | sampled-blocks |  | $21 | $0.00 |  |  |
| Bitcoin | utxo | token_only | 657.3k | exact-blocks |  | $65.8B (gross) | - |  |  |
| Unichain | evm | tradeable | 640.7k ±6.3k | sampled-blocks | 81% | $21.5M | $33.62 | `0x3c3a8a41e0` 67% | `0x5ba5d50744` 51% |
| World Chain | evm | token_only | 640.0k ±13.7k | sampled-blocks |  | $23.2M | $36.30 | `0x0000000071` 62% | `0x2cfc85d8e4` 95% |
| Plasma | evm | tradeable | 618.8k ±20.6k | sampled-blocks |  | $2.6B | $4170.30 | `0x334987c805` 46% | `0xb8ce59fc37` 91% |
| Hedera | hedera | tradeable | 570.7k | exact-blocks |  | $23.9M | $41.93 |  |  |
| Kaia | evm | token_only | 437.9k ±83.6k | sampled-blocks |  | $54.9M | $125.46 | `0x80d7705ef8` 22% | `0xd077a40096` 53% |
| Gnosis | evm | tradeable | 428.7k ±16.1k | sampled-blocks |  | $15.4M | $35.86 | `0x1d4bceb37b` 12% | `0xb50201558b` 41% |
| PulseChain | evm | tradeable | 412.2k ±17.9k | sampled-blocks |  | $4.2M | $10.10 | `0x76abe398ef` 9% | `0x6bf228eb7f` 32% |
| Flare | evm | tradeable | 373.3k ±67.2k | sampled-blocks | 87% | $42.8M | $114.72 | `0x2ca6571daa` 87% | `0x6f219564e6` 38% |
| Soneium | evm | thin | 322.9k ±8.9k | sampled-blocks |  | $279.4k | $0.87 | `0x0000000071` 48% | `0x50c4e75a51` 54% |
| Hyperliquid L1 (hyperevm) | evm | deep | 291.2k ±22.7k | sampled-blocks |  | $421.2M | $1446.55 | `0x278d858f05` 7% | `0xb21d281ded` 34% |
| Ronin | evm | thin | 269.8k ±7.7k | sampled-blocks |  | $1.4M | $5.36 | `0x43f18c0752` 56% | `0xf613e798ae` 29% |
| Starknet | starknet | tradeable | 259.9k ±30.0k | sampled-blocks |  | $227.4M | $874.84 |  |  |
| Cardano | cardano | tradeable | 249.6k | exact-blocks |  | $229.1M | $917.93 |  |  |
| Blast | evm | thin | 245.4k ±6.1k | sampled-blocks |  | $181.7k | $0.74 | `0x848e45b91d` 71% | `0xac4c6e212a` 77% |
| Avalanche | evm | deep | 244.3k ±22.5k | sampled-blocks |  | $465.1M | $1903.96 | `0xe844701934` 7% | `0x087befdbcf` 45% |
| Sonic | evm | tradeable | 214.5k ±39.2k | sampled-blocks |  | $64.4M | $300.25 | `0xeac0722f31` 28% | `0xee7ae85f2f` 48% |
| Plume Mainnet | evm | token_only | 209.4k | sampled-blocks |  | $8 | $0.00 | `0xee96619e24` 98% |  |
| Ink | evm | tradeable | 199.6k ±9.1k | sampled-blocks |  | $339.0M | $1698.76 | `0x2fa8df1bad` 53% | `0x1b35d13a2e` 52% |
| THORChain | cosmos | token_only | 186.8k | exact-blocks |  | $11.3M | $60.37 |  |  |
| Litecoin | utxo | token_only | 168.0k | exact-blocks |  | $2.2B (gross) | - |  |  |
| Celestia | cosmos | token_only | 138.5k ±229 | sampled-blocks |  | $4.9M | $35.09 |  |  |
| Abstract | evm | thin | 105.5k ±3.7k | sampled-blocks |  | $10.3M | $98.03 | `0x99bb83ae9b` 21% | `0x643e1471f3` 38% |
| Tezos | tezos | thin | 99.3k | exact-indexer |  | $3.0M | $30.57 |  |  |
| Cronos | evm | tradeable | 88.3k ±19.5k | sampled-blocks |  | $13.5M | $152.84 | `0xec68090566` 16% | `0xec68090566` 55% |
| Berachain | evm | thin | 73.7k ±2.8k | sampled-blocks |  | $1.5M | $19.94 | `0xd2f19a79b0` 59% | `0x0ac011eb02` 52% |
| Tempo | evm | tradeable | 63.6k ±6.5k | sampled-blocks |  | $54.4M | $855.58 | `create` 82% | `create` 98% |
| Osmosis | cosmos | thin | 45.5k ±2.7k | sampled-blocks |  | $119.8M | $2632.21 |  |  |
| CORE | evm | inactive | 37.9k ±1.7k | sampled-blocks |  | $101.7k | $2.69 | `0x0000000000` 76% | `0x62af865e65` 47% |
| Katana | evm | thin | 24.6k ±4.8k | sampled-blocks |  | $1.4M | $56.72 | `0x62230cea61` 69% | `0x7f1f4b4b29` 33% |
| CosmosHub | cosmos | token_only | 21.2k | exact-blocks |  | $31.1M | $1469.04 |  |  |
| Doge (dogecoin) | utxo | token_only | 17.9k | aggregator-24h |  | $1.1B (gross) | - |  |  |
| ZKsync Era | evm | token_only | 17.9k ±580 | sampled-blocks |  | $37.0M | $2066.05 | `0x5a7d6b2f92` 9% | `0x5a7d6b2f92` 65% |
| Bitcoincash | utxo | token_only | 15.2k | aggregator-24h |  | $159.1M (gross) | - |  |  |
| Mantle | evm | tradeable | 14.7k ±2.1k | sampled-blocks |  | $7.1M | $481.50 | `0x3c22698118` 21% | `0x44a13125ef` 52% |
| Linea | evm | thin | 12.9k ±543 | sampled-blocks |  | $1.5M | $116.51 | `0xd8850c39d6` 9% | `0x1789e00436` 34% |
| Sei | evm | tradeable | 11.4k ±3.8k | sampled-blocks |  | $3.2M | $282.35 | `0xd5886dfa67` 25% | `0xd5886dfa67` 64% |
| Scroll | evm | thin | 10.1k ±396 | sampled-blocks |  | $1.9M | $191.07 | `0x5300000000` 16% | `0xd29687c813` 83% |
| Zcash | utxo | token_only | 6.5k | aggregator-24h |  | $1.3B (gross) | - |  |  |
| Rootstock | evm | thin | 6.1k ±334 | sampled-blocks |  | $1.9k | $0.31 | `0x0000000000` 45% |  |
| Noble | cosmos | thin | 3.9k | exact-index |  | $102.5M | $26.4k |  |  |

## New activity

Detector hits, most severe first (info-level in `detectors.md`). Every hit carries its chain's tier so a surge on an untradeable chain reads as such.

- **[high]** TON dex last day: $13.1M/day vs $3.6M baseline (x3.6, market x0.69, rarer than 1% of its days)  `chain_surge:TON:dex:d1`
- **[high]** Cardano transactions 542.5k on 2026-10-08 vs a 33.5k median over the 13 days before (x16.2, market x1.08; 10-05 34.0k, 10-06 34.2k, 10-07 326.7k)  `probe_tx_surge:cardano`
- **[notable]** Tempo stablecoin float +$585.3M in 30 days ($145.4M -> $730.7M, +403%); largest step $309.8M on 2026-09-30  `stable_inflow:Tempo:30d`
- **[notable]** Plasma stablecoin float +$317.0M in 30 days ($1.1B -> $1.4B, +30%); largest step $137.0M on 2026-09-17  `stable_inflow:Plasma:30d`
- **[notable]** USDC on X Layer +$109.8M in 7 days ($17.9M -> $127.7M)  `stable_inflow:X Layer:USDC`
- **[notable]** OP Mainnet took 1.23% of all DEX volume this week, from 0.36% over the four weeks before (x3.4)  `dex_share_shift:OP Mainnet`
- **[notable]** OP Mainnet dex last 7 days: $94.6M/day vs $35.5M baseline (x2.7, market x0.81, rarer than 5% of its days); one day carries 99% of the excess  `chain_surge:OP Mainnet:dex:d7`
- **[notable]** OP Mainnet value without activity: transactions x0.99, DEX volume x2.66 (last 7 days vs 28 before)  `activity_divergence:OP Mainnet:value_without_activity`
- **[notable]** Near stablecoin float +$40.1M in 7 days ($88.7M -> $128.8M, +45%)  `stable_inflow:Near`
- **[notable]** USDe on Monad +$31.6M in 7 days ($69.7M -> $101.4M)  `stable_inflow:Monad:USDe`
- **[notable]** Starknet dex last day: $39.8M/day vs $9.7M baseline (x4.1, market x0.69, rarer than 4% of its days)  `chain_surge:Starknet:dex:d1`
- **[notable]** USDC on Near +$25.2M in 7 days ($63.4M -> $88.6M)  `stable_inflow:Near:USDC`
- **[notable]** QI on solana: $23.2M/day of transfers, absent from the previous 1 probe(s)  `probe_new_asset:solana:8TiMkgvsrat9tM2esko8zVTt99LZLpefUM4SnZaziXaQ`
- **[notable]** USDT on Monad +$21.3M in 7 days ($34.8M -> $56.0M)  `stable_inflow:Monad:USDT`
- **[notable]** WETH on arc: $11.7M/day of transfers, absent from the previous 1 probe(s)  `probe_new_asset:arc:0x128cc466b61f542da60c70e3aa11c10e19b84edb`
- **[notable]** Kaia dex last day: $4.0M/day vs $308.1k baseline (x12.9, market x0.69, rarer than 1% of its days)  `chain_surge:Kaia:dex:d1`
- **[notable]** Saga dex last day: $3.6M/day vs $686.1k baseline (x5.1, rarer than 4% of its days)  `chain_surge:Saga:dex:d1`
- **[notable]** OP Mainnet fees last 7 days: $379.5k/day vs $148.0k baseline (x2.6, market x0.93, rarer than 1% of its days); one day carries 65% of the excess  `chain_surge:OP Mainnet:fees:d7`
- **[notable]** OP Mainnet fees last day: $322.4k/day vs $116.9k baseline (x2.5, market x0.91, rarer than 3% of its days)  `chain_surge:OP Mainnet:fees:d1`
- **[notable]** Stable fees last day: $96.5k/day vs $10.4k baseline (x5.7, market x0.91, rarer than 1% of its days)  `chain_surge:Stable:fees:d1`
- **[notable]** Cronos fees last day: $34.5k/day vs $11.9k baseline (x2.4, market x0.91, rarer than 3% of its days)  `chain_surge:Cronos:fees:d1`
- **[notable]** Arbitrum daa last 7 days: 213.8k/day vs 118.1k baseline (x1.8, market x0.97, rarer than 2% of its days)  `chain_surge:Arbitrum:daa:d7`
- **[notable]** Near daa last 7 days: 126.7k/day vs 62.9k baseline (x2.0, market x0.97, rarer than 2% of its days)  `chain_surge:Near:daa:d7`
- **[notable]** World Chain daa last day: 41.2k/day vs 7.3k baseline (x5.5, market x0.92, rarer than 4% of its days)  `chain_surge:World Chain:daa:d1`
- **[notable]** Cronos transactions 90.9k on 2026-10-08 vs a 35.6k median over the 13 days before (x2.6, market x1.08; 10-05 30.4k, 10-06 70.6k, 10-07 60.2k)  `probe_tx_surge:cronos`

15 info-level hits (drops, divergences, thin chains, unregistered tradeable chains) are listed in `detectors.md`.

## What moved, by asset (probe)

Transfer value per day, net per transaction: what each account gained, so routed hops and flash-loan round trips cancel while both legs of a swap count (UTXO chains and Blockchair rows are gross outputs; Hyperliquid is traded notional). ± is one standard error of the stratified estimate; `top` is the share of the sampled value that came from one block (above 0.5 the figure is one large transfer scaled up).

| chain | asset | class | USD/day | ± | transfers/day | top |
|---|---|---|---:|---:|---:|---:|
| solana | SOL | native | $4.2B | $487.2M | 123.1M | 0.08 |
| solana | usdc | usd_stable | $1.9B | $420.8M | 9.4M | 0.21 |
| solana | SOL | native | $1.7B | $240.6M | 56.1M | 0.12 |
| solana | USELESS | other | $497.6M | $499.6M | 8.8k | 1.00 |
| solana | usdt | usd_stable | $286.2M | $118.7M | 929.1k | 0.40 |
| bsc | USDT | usd_stable | $2.3B | $270.6M | 14.8M | 0.06 |
| bsc | USDC | usd_stable | $535.5M | $294.0M | 1.2M | 0.54 |
| bsc | SHARE | other | $385.6M | $382.6M | 2.9k | 0.99 |
| bsc | WBNB | native | $363.7M | $48.9M | 2.1M | 0.08 |
| bsc | BNB | native | $292.2M | $43.9M |  | 0.07 |
| tron | USDT | usd_stable | $31.7B | $3.1B | 2.4M | 0.06 |
| tron | TRX | native | $2.1B | $488.9M |  | 0.18 |
| tron | USDD | usd_stable | $125.4M | $56.4M | 2.2k | 0.29 |
| tron | WTRX | native | $43.3M | $31.5M | 5.8k | 0.70 |
| tron | JST | other | $8.7M | $6.9M | 1.4k | 0.79 |
| aptos | USDC | usd_stable | $227.7M | $227.0M | 467.1k | 0.99 |
| aptos | USDt | usd_stable | $19.8M | $19.9M | 29.2k | 1.00 |
| aptos | APT | native | $431.1k | $306.7k | 87.6k | 0.55 |
| base | USDC | usd_stable | $74.1B | $2.2B | 3.7M | 0.01 |
| base | WETH | eth | $66.3B | $2.3B | 1.5M | 0.01 |
| base | cbBTC | btc | $30.2B | $1.8B | 499.8k | 0.03 |
| base | AERO | other | $5.0B | $544.8M | 609.1k | 0.06 |
| base | cbETH | eth | $1.1B | $50.6M | 82.5k | 0.01 |
| robinhood | USDG | usd_stable | $642.2M | $157.3M | 1.5M | 0.17 |
| robinhood | WETH | eth | $595.3M | $122.0M | 1.9M | 0.14 |
| robinhood | ETH | eth | $312.0M | $101.0M |  | 0.29 |
| robinhood | SPCX | other | $92.9M | $88.9M | 32.3k | 0.96 |
| robinhood | NVDA | other | $63.1M | $27.2M | 94.1k | 0.36 |
| sui | SUI | native | $392.5M | $220.6M | 1.1M | 0.40 |
| sui | USDSUI | usd_stable | $192.0M | $157.3M | 11.4k | 0.81 |
| sui | DEEP | other | $55.1M | $31.4M | 30.5k | 0.38 |
| sui | US | other | $54.1M | $42.6M | 21.0k | 0.77 |
| sui | USDC | usd_stable | $49.9M | $24.1M | 106.8k | 0.38 |
| polygon | USDC | usd_stable | $633.5M | $256.3M | 5.3M | 0.39 |
| polygon | pUSD | usd_stable | $355.1M | $74.8M | 8.8M | 0.16 |
| polygon | USDT0 | usd_stable | $288.0M | $119.1M | 330.9k | 0.30 |
| polygon | USDC | usd_stable | $277.8M | $99.2M | 914.6k | 0.24 |
| polygon | AUDF | other | $87.9M | $86.9M | 582 | 0.99 |
| stellar | USDC | usd_stable | $23.7M | $4.4M | 138.2k | 0.12 |
| stellar | XLM | native | $15.8M | $9.1M | 255.2k | 0.46 |
| stellar | CETES | other | $1.8M | $1.6M | 2.0k | 0.90 |
| stellar | SHX | other | $438.4k | $174.7k | 4.3k | 0.41 |
| stellar | sUSD | other | $179.0k | $124.8k | 2.3k | 0.65 |
| monad | USDC | usd_stable | $1.4B | $1.4B | 88.0k | 0.99 |
| monad | AUSD | usd_stable | $48.2M | $44.1M | 18.6k | 0.91 |
| monad | USDat | other | $6.5M | $6.5M | 715 | 1.00 |
| monad | WMON | native | $4.8M | $2.0M | 138.1k | 0.35 |
| monad | WETH | eth | $2.2M | $1.0M | 27.2k | 0.28 |
| ton | TON | native | $131.9M | $68.8M | 2.8M | 0.51 |
| ton | USD₮ | usd_stable | $55.7M | $7.4M | 168.2k | 0.09 |
| ton | tsTON | other | $6.4M | $2.0M | 4.2k | 0.23 |
| ton | TAC | other | $881.7k | $863.6k | 216 | 1.00 |
| ton | NOT | other | $522.2k | $439.5k | 1.4k | 0.86 |
| megaeth | MEGA | other | $3.6M | $2.8M | 4.5k | 0.74 |
| megaeth | USDm | usd_stable | $188.7k | $57.8k | 126.8k | 0.19 |
| megaeth | ETH | eth | $18.0k | $17.0k |  | 0.95 |
| megaeth | WETH | eth | $11.5k | $8.5k | 2.4k | 0.72 |
| megaeth | BTC.b | btc | $2.1k | $2.1k | 216 | 1.00 |
| xrpl | XRP | native | $385.5M | $85.0M | 324.4k | 0.15 |
| xrpl | OUSG | other | $279.9M | $279.3M | 112 | 1.00 |
| xrpl | RLUSD | usd_stable | $21.3M | $13.9M | 244.0k | 0.64 |
| ethereum | USDC | usd_stable | $18.8B | $3.4B | 774.5k | 0.10 |
| ethereum | USDT | usd_stable | $8.9B | $1.2B | 943.7k | 0.08 |
| ethereum | ETH | eth | $3.7B | $1.2B |  | 0.24 |
| ethereum | PYUSD | usd_stable | $1.1B | $786.4M | 7.8k | 0.64 |
| ethereum | LINK | other | $1.0B | $867.9M | 9.4k | 0.84 |
| injective | USDC.inj | usd_stable | $302.3M | $137.5M | 816.0k | 0.43 |
| injective | INJ | native | $36.2M | $24.8M | 1.6M | 0.48 |
| injective | WETH | eth | $23.0M | $2.9M | 59.1k | 0.03 |
| injective | USDT | usd_stable | $3.5M | $3.5M | 6.0k | 1.00 |
| injective | ATOM | other | $2.3k | $2.3k | 3.6k | 1.00 |
| optimism | WETH | eth | $5.9B | $242.2M | 856.0k | 0.01 |
| optimism | USDC | usd_stable | $5.6B | $141.5M | 1.1M | 0.01 |
| optimism | velo | other | $798.8M | $23.1M | 1.2M | 0.01 |
| optimism | OP | other | $274.6M | $15.1M | 426.8k | 0.04 |
| optimism | WBTC | btc | $55.8M | $13.6M | 40.4k | 0.13 |
| arbitrum | USDC | usd_stable | $877.6M | $239.2M | 1.4M | 0.21 |
| arbitrum | ETH | eth | $207.1M | $200.0M |  | 0.96 |
| arbitrum | USDT0 | usd_stable | $129.6M | $67.4M | 154.0k | 0.49 |
| arbitrum | WETH | eth | $64.7M | $24.0M | 260.9k | 0.31 |
| arbitrum | MAGIC | other | $25.3M | $16.9M | 27.9k | 0.50 |
| xdc | XDC | native | $19.3M | $10.8M |  | 0.48 |
| xdc | WXDC | native | $1.9M | $429.4k | 22.1k | 0.13 |
| xdc | DOPU | other | $937.1k | $251.8k | 4.5k | 0.18 |
| xdc | GAMA | other | $919.5k | $428.4k | 14.7k | 0.33 |
| xdc | USDC | usd_stable | $405.4k | $136.3k | 7.6k | 0.18 |
| algorand | USDC | usd_stable | $16.3M | $9.4M | 60.4k | 0.48 |
| algorand | ALGO | native | $2.8M | $1.1M | 100.8k | 0.33 |
| algorand | FOLKS | other | $73.2k | $44.7k | 4.5k | 0.57 |
| algorand | xALGO | other | $52.7k | $34.7k | 3.0k | 0.64 |
| algorand | TALGO | other | $46.3k | $33.8k | 1.9k | 0.65 |
| opbnb | USDT | usd_stable | $5.2k | $3.8k | 48.4k | 0.60 |
| opbnb | BNB | native | $1.8k | $1.4k |  | 0.71 |
| celo | cUSD | usd_stable | $25.7M | $18.8M | 15.1k | 0.63 |
| celo | CELO | native | $20.5M | $17.2M |  | 0.82 |
| celo | axlUSDC | other | $9.4M | $9.5M | 864 | 1.00 |
| celo | BRLA | other | $2.5M | $1.4M | 3.5k | 0.34 |
| celo | USDT0 | usd_stable | $1.7M | $431.5k | 7.4M | 0.20 |
| arc | USDC | usd_stable | $92.7M | $84.3M | 55.3k | 0.91 |
| arc | USDC | usd_stable | $51.0M | $23.2M |  | 0.32 |
| arc | WETH | eth | $11.7M | $7.4M | 4.3k | 0.45 |
| arc | cirBTC | btc | $339.2k | $338.7k | 3.4k | 1.00 |
| arc | COOL | other | $89.2k | $83.8k | 2.6k | 0.94 |
| xlayer | xETH | other | $88.9M | $63.1M | 6.0k | 0.56 |
| xlayer | USDG | usd_stable | $19.7M | $6.1M | 204.3k | 0.19 |
| xlayer | USDT0 | usd_stable | $13.2M | $7.0M | 175.8k | 0.51 |
| xlayer | PAXGy | other | $5.8M | $5.8M | 864 | 1.00 |
| xlayer | OKB | native | $3.8M | $1.8M | 52.3k | 0.39 |
| near | USDC | usd_stable | $161.6M | $162.9M | 9.8k | 1.00 |
| near | DAI | usd_stable | $51.3M | $51.8M | 2.4k | 1.00 |
| near | USDT | usd_stable | $29.3M | $29.5M | 4.9k | 1.00 |
| near | wNEAR | native | $16.2M | $13.4M | 83.1k | 0.82 |
| near | USDC | usd_stable | $6.8M | $6.6M | 19.6k | 0.97 |
| dydx | USDC.n | usd_stable | $21 | $12 | 27.1k | 0.50 |
| bitcoin | BTC | btc | $65.8B | $0 | 657.3k | 0.04 |
| unichain | USDC | usd_stable | $10.0M | $5.9M | 34.6k | 0.51 |
| unichain | HYPE | other | $9.4M | $5.9M | 13.8k | 0.54 |
| unichain | WETH | eth | $929.7k | $337.4k | 6.9k | 0.19 |
| unichain | WBTC | btc | $544.2k | $315.5k | 2.6k | 0.52 |
| unichain | USDT0 | usd_stable | $333.0k | $281.1k | 3.0k | 0.83 |
| worldchain | WLD | other | $22.6M | $12.3M | 306.1k | 0.40 |
| worldchain | USDC.e | usd_stable | $315.0k | $112.4k | 56.6k | 0.24 |
| worldchain | Re7WLD | other | $152.6k | $74.3k | 30.2k | 0.47 |
| worldchain | WBTC | btc | $68.9k | $64.1k | 2.2k | 0.93 |
| worldchain | WETH | eth | $57.4k | $32.0k | 11.2k | 0.39 |
| plasma | USDT0 | usd_stable | $2.6B | $2.3B | 109.6k | 0.90 |
| plasma | WXPL | native | $868.6k | $552.3k | 26.2k | 0.57 |
| plasma | XPL | native | $1.8k | $1.5k |  | 0.80 |
| plasma | aPlaUSDT0 | other | $572 | $573 | 1.5k | 1.00 |
| plasma | WETH | eth | $10 | $10 | 1.5k | 1.00 |
| hedera | HBAR | native | $21.3M | $20.0M | 177.8k | 0.94 |
| hedera | WHBAR | native | $901.9k | $451.7k | 2.7k | 0.35 |
| hedera | USDC | usd_stable | $873.0k | $448.1k | 2.4k | 0.36 |
| hedera | XSAUCE | other | $758.7k | $759.8k | 265 | 1.00 |
| hedera | BSL | other | $85.2k | $85.4k | 265 | 1.00 |
| kaia | KAIA | native | $32.9M | $12.7M |  | 0.32 |
| kaia | USD₮ | usd_stable | $14.1M | $5.2M | 128.2k | 0.27 |
| kaia | WKLAY | other | $2.8M | $1.1M | 143.6k | 0.35 |
| kaia | oXRP | other | $2.1M | $2.0M | 56.0k | 0.92 |
| kaia | bora | other | $1.6M | $1.5M | 9.4k | 0.93 |
| gnosis | EURe | eur_stable | $4.1M | $2.2M | 15.6k | 0.51 |
| gnosis | EURe | eur_stable | $3.1M | $2.1M | 11.4k | 0.68 |
| gnosis | aGnoEURe | other | $2.5M | $2.1M | 741 | 0.82 |
| gnosis | USDC.e | usd_stable | $2.2M | $883.5k | 10.5k | 0.41 |
| gnosis | USDC | usd_stable | $895.5k | $821.4k | 8.3k | 0.92 |
| pulsechain | ETH | eth | $896.1k | $459.1k | 12.6k | 0.43 |
| pulsechain | WPLS | native | $817.9k | $281.8k | 116.3k | 0.33 |
| pulsechain | HEX | other | $749.8k | $267.1k | 31.9k | 0.32 |
| pulsechain | USDC | usd_stable | $454.5k | $135.2k | 15.0k | 0.25 |
| pulsechain | DAI | usd_stable | $272.0k | $87.4k | 17.8k | 0.23 |
| flare | FLR | native | $38.2M | $36.3M |  | 0.95 |
| flare | FXRP | other | $2.0M | $1.0M | 28.0k | 0.40 |
| flare | USDT0 | usd_stable | $1.4M | $671.1k | 16.2k | 0.46 |
| flare | WFLR | native | $922.5k | $646.1k | 7.1k | 0.65 |
| flare | USDC.e | usd_stable | $285.7k | $216.5k | 790 | 0.69 |
| soneium | USDC | usd_stable | $189.6k | $143.5k | 13.0k | 0.75 |
| soneium | WETH | eth | $38.2k | $17.4k | 12.3k | 0.34 |
| soneium | USDSC | other | $27.8k | $15.5k | 2.4k | 0.49 |
| soneium | ETH | eth | $15.0k | $8.2k |  | 0.50 |
| soneium | USDT0 | usd_stable | $7.5k | $6.5k | 1.5k | 0.86 |
| hyperevm | USDC | usd_stable | $323.0M | $163.5M | 125.2k | 0.41 |
| hyperevm | WHYPE | native | $64.9M | $12.5M | 122.1k | 0.09 |
| hyperevm | USDT0 | usd_stable | $12.6M | $4.5M | 45.7k | 0.22 |
| hyperevm | HYPE | native | $6.5M | $2.7M |  | 0.35 |
| hyperevm | UBTC | btc | $4.6M | $2.0M | 13.6k | 0.32 |
| ronin | RON | native | $631.0k | $439.3k |  | 0.49 |
| ronin | WRON | native | $269.6k | $83.4k | 36.7k | 0.25 |
| ronin | AXS | other | $116.9k | $52.6k | 11.9k | 0.37 |
| ronin | PIXEL | other | $116.6k | $39.8k | 12.1k | 0.19 |
| ronin | USDC | usd_stable | $113.8k | $69.2k | 17.1k | 0.60 |
| starknet | ETH | eth | $75.4M | $55.3M | 55.3k | 0.72 |
| starknet | STRK | native | $65.1M | $14.6M | 439.1k | 0.12 |
| starknet | ZEC | other | $44.2M | $31.5M | 5.0k | 0.58 |
| starknet | USDC | usd_stable | $40.3M | $5.8M | 146.0k | 0.07 |
| starknet | strkBTC | btc | $1.3M | $448.7k | 11.9k | 0.18 |
| cardano | ADA | native | $225.4M | $55.6M | 256.1k | 0.22 |
| cardano | NIGHT | other | $1.4M | $674.3k | 7.5k | 0.56 |
| cardano | USDA | usd_stable | $1.1M | $1.1M | 1.8k | 0.93 |
| cardano | SNEK | other | $622.9k | $649.7k | 2.5k | 1.00 |
| cardano | USDM | usd_stable | $237.3k | $247.5k | 1.8k | 1.00 |
| blast | ETH | eth | $169.0k | $99.1k |  | 0.53 |
| blast | WETH | eth | $6.0k | $5.0k | 13.2k | 0.82 |
| blast | USDB | usd_stable | $5.3k | $4.8k | 9.5k | 0.92 |
| blast | blast | other | $716 | $587 | 4.8k | 0.87 |
| blast | ezETH | eth | $517 | $502 | 864 | 0.97 |
| avalanche | WAVAX | native | $183.2M | $42.0M | 69.7k | 0.10 |
| avalanche | AvalancheUSDC | other | $156.6M | $30.8M | 79.2k | 0.09 |
| avalanche | USDT | usd_stable | $50.3M | $36.4M | 23.6k | 0.71 |
| avalanche | AVAX | native | $45.6M | $21.7M |  | 0.28 |
| avalanche | btc.b | btc | $19.8M | $8.8M | 10.4k | 0.42 |
| sonic | USDC | usd_stable | $34.0M | $30.1M | 44.2k | 0.88 |
| sonic | wS | native | $18.1M | $7.0M | 49.0k | 0.25 |
| sonic | WETH | eth | $10.0M | $6.4M | 17.8k | 0.45 |
| sonic | S | native | $1.9M | $1.3M |  | 0.65 |
| sonic | USSD | other | $150.2k | $88.7k | 3.6k | 0.40 |
| plume | PLUME | native | $8 | $8 |  | 1.00 |
| ink | USDT0 | usd_stable | $218.9M | $177.3M | 23.3k | 0.80 |
| ink | WETH | eth | $90.8M | $46.1M | 22.9k | 0.42 |
| ink | kBTC | btc | $23.8M | $18.1M | 2.6k | 0.73 |
| ink | USDC | usd_stable | $3.8M | $2.3M | 10.4k | 0.57 |
| ink | oUSDT | other | $580.4k | $490.5k | 7.8k | 0.84 |
| thorchain | RUNE | native | $11.3M | $5.3M | 103.5k | 0.39 |
| thorchain | RUJI | other | $3.2k | $3.2k | 117 | 1.00 |
| litecoin | LTC | native | $2.2B | $0 | 168.0k | 0.02 |
| celestia | TIA | native | $4.9M | $3.1M | 3.0k | 0.56 |
| abstract | ETH | eth | $4.5M | $3.6M | 295.3k | 0.79 |
| abstract | WETH | eth | $1.7M | $927.0k | 14.3k | 0.43 |
| abstract | PENGU | other | $1.6M | $1.0M | 7.8k | 0.55 |
| abstract | USDC.e | usd_stable | $1.4M | $857.8k | 28.2k | 0.59 |
| abstract | ETH | eth | $842.3k | $600.5k |  | 0.70 |
| tezos | XTZ | native | $2.9M | $0 | 79.1k |  |
| tezos | USDt | usd_stable | $113.7k | $0 | 253 |  |
| tezos | stXTZ | other | $4.8k | $0 | 207 |  |
| tezos | tzBTC | btc | $3.2k | $0 | 39 |  |
| tezos | oXTZ | other | $2.2k | $0 | 228 |  |
| cronos | WCRO | native | $5.1M | $3.2M | 51.1k | 0.60 |
| cronos | CRO | native | $3.9M | $2.6M |  | 0.64 |
| cronos | CROCAT | other | $2.3M | $2.3M | 11.0k | 0.99 |
| cronos | ATOM | other | $511.8k | $420.3k | 3.0k | 0.79 |
| cronos | USDC | usd_stable | $415.8k | $290.4k | 11.0k | 0.61 |
| berachain | BERA | native | $1.2M | $857.7k |  | 0.61 |
| berachain | WBERA | native | $75.6k | $38.7k | 39.7k | 0.40 |
| berachain | sWBERA | other | $53.2k | $42.1k | 1.5k | 0.77 |
| berachain | HONEY | other | $47.7k | $32.0k | 1.7k | 0.59 |
| berachain | USDC.e | usd_stable | $28.2k | $28.2k | 216 | 1.00 |
| tempo | USDC.e | usd_stable | $51.6M | $20.4M | 90.4k | 0.33 |
| tempo | pathUSD | usd_stable | $1.8M | $1.2M | 89.6k | 0.52 |
| tempo | senpathUSD | other | $1.0M | $922.5k | 8.4k | 0.92 |
| tempo | USDT0 | usd_stable | $67.4k | $67.5k | 1.5k | 1.00 |
| tempo | OUSD | usd_stable | $4.3k | $3.3k | 13.0k | 0.72 |
| osmosis | USDC.n | usd_stable | $103.7M | $17.1M | 30.6k | 0.10 |
| osmosis | ATOM | other | $8.9M | $1.9M | 44.9k | 0.14 |
| osmosis | USDC | usd_stable | $5.9M | $2.4M | 40.1k | 0.36 |
| osmosis | USDC.inj | usd_stable | $569.9k | $367.7k | 2.8k | 0.63 |
| osmosis | OSMO | native | $150.4k | $31.6k | 31.5k | 0.11 |
| core | CORE | native | $97.1k | $47.8k |  | 0.41 |
| core | WCORE | native | $2.8k | $1.3k | 3.6k | 0.35 |
| core | USDT | usd_stable | $961 | $481 | 1.6k | 0.35 |
| core | BOW | other | $391 | $243 | 720 | 0.43 |
| core | WCORE | native | $362 | $257 | 288 | 0.55 |
| katana | KAT | other | $611.4k | $476.9k | 2.2k | 0.75 |
| katana | vbUSDC | other | $443.7k | $200.5k | 4.0k | 0.32 |
| katana | vbETH | other | $255.1k | $163.9k | 2.2k | 0.56 |
| katana | vbWBTC | other | $43.2k | $43.3k | 448 | 1.00 |
| katana | vbUSDT | other | $43.1k | $43.1k | 1.3k | 1.00 |
| cosmoshub | ATOM | native | $31.1M | $9.8M | 56.7k | 0.18 |
| cosmoshub | USDC.inj | usd_stable | $43 | $40 | 175 | 0.93 |
| cosmoshub | stATOM | other | $3 | $3 | 877 | 0.89 |
| cosmoshub | USDC | usd_stable | $0 | $0 | 351 | 0.91 |
| cosmoshub | STRD | other | $0 | $0 | 789 | 0.70 |
| dogecoin | DOGE | native | $1.1B | $0 | 17.9k |  |
| zksync | zk | other | $21.2M | $8.3M | 5.1k | 0.25 |
| zksync | WETH | eth | $4.6M | $3.9M | 7.1k | 0.85 |
| zksync | ETH | eth | $4.5M | $3.9M | 55.5k | 0.87 |
| zksync | ETH | eth | $4.4M | $3.9M |  | 0.89 |
| zksync | USDC | usd_stable | $1.8M | $1.1M | 1.2k | 0.45 |
| bitcoin-cash | BCH | native | $159.1M | $0 | 15.2k |  |
| mantle | USDT | usd_stable | $3.2M | $1.9M | 4.8k | 0.56 |
| mantle | WMNT | native | $2.2M | $1.9M | 5.0k | 0.83 |
| mantle | WETH | eth | $1.3M | $871.1k | 1.7k | 0.61 |
| mantle | KII | other | $192.7k | $138.0k | 864 | 0.79 |
| mantle | MNT | native | $45.7k | $30.6k |  | 0.50 |
| linea | LINEA | other | $452.8k | $251.9k | 1.3k | 0.44 |
| linea | USDC | usd_stable | $444.5k | $260.7k | 3.7k | 0.58 |
| linea | ETH | eth | $243.2k | $123.0k |  | 0.50 |
| linea | WETH | eth | $222.3k | $94.2k | 3.5k | 0.36 |
| linea | weETH | eth | $80.4k | $78.5k | 241 | 0.98 |
| sei | wSEI | native | $1.3M | $807.9k | 4.7k | 0.45 |
| sei | USDC | usd_stable | $788.1k | $616.6k | 19.0k | 0.74 |
| sei | SEI | native | $750.5k | $752.0k |  | 1.00 |
| sei | USDT0 | usd_stable | $247.4k | $247.6k | 16.1k | 1.00 |
| sei | DRG | other | $115.2k | $115.5k | 949 | 1.00 |
| scroll | SCR | other | $1.4M | $838.3k | 534 | 0.43 |
| scroll | ETH | eth | $187.6k | $176.1k |  | 0.95 |
| scroll | ETH | eth | $146.2k | $28.7k | 4.8k | 0.14 |
| scroll | USDC | usd_stable | $140.3k | $28.3k | 3.3k | 0.14 |
| scroll | USDT | usd_stable | $13.1k | $7.8k | 1.2k | 0.50 |
| zcash | ZEC | native | $1.3B | $0 | 6.5k |  |
| rootstock | RBTC | native | $1.9k | $1.7k |  | 0.91 |
| noble | USDC | usd_stable | $102.5M | $11.5M | 2.8k | 0.04 |

## Cross-source agreement

39 checks passed, 6 failed (tolerance ±25% on transaction counts).

| check | ok | detail |
|---|---|---|
| `tx-cross-source:abstract:l2beat` | ok | probe 105.5k/day (sampled-blocks) vs l2beat 105.4k/day: x1.001 |
| `tx-cross-source:arbitrum:growthepie` | ok | probe 1.4M/day (sampled-blocks) vs growthepie 1.4M/day: x1.049 |
| `tx-cross-source:arbitrum:l2beat` | ok | probe 1.4M/day (sampled-blocks) vs l2beat 1.4M/day: x1.049 |
| `tx-cross-source:base:growthepie` | ok | probe 6.9M/day (sampled-blocks) vs growthepie 6.9M/day: x1.001 |
| `tx-cross-source:base:l2beat` | ok | probe 6.9M/day (sampled-blocks) vs l2beat 6.9M/day: x1.001 |
| `tx-cross-source:bitcoin-cash:blockchair-24h` | ok | probe 15.2k/day (aggregator-24h) vs blockchair-24h 16.4k/day: x0.928 |
| `tx-cross-source:blast:l2beat` | ok | probe 245.4k/day (sampled-blocks) vs l2beat 244.9k/day: x1.002 |
| `tx-cross-source:celo:growthepie` | ok | probe 889.5k/day (sampled-blocks) vs growthepie 892.7k/day: x0.996 |
| `tx-cross-source:celo:l2beat` | ok | probe 889.5k/day (sampled-blocks) vs l2beat 892.7k/day: x0.996 |
| `tx-cross-source:dogecoin:blockchair-24h` | ok | probe 17.9k/day (aggregator-24h) vs blockchair-24h 18.0k/day: x0.998 |
| `tx-cross-source:ethereum:growthepie` | ok | probe 1.8M/day (sampled-blocks) vs growthepie 1.8M/day: x1.005 |
| `tx-cross-source:gnosis:l2beat` | ok | probe 428.7k/day (sampled-blocks) vs l2beat 437.0k/day: x0.981 |
| `tx-cross-source:ink:growthepie` | **FAIL** | probe 199.6k/day (sampled-blocks) vs growthepie 253.0k/day: x0.789 |
| `tx-cross-source:ink:l2beat` | **FAIL** | probe 199.6k/day (sampled-blocks) vs l2beat 253.0k/day: x0.789 |
| `tx-cross-source:katana:l2beat` | ok | probe 24.6k/day (sampled-blocks) vs l2beat 25.1k/day: x0.979 |
| `tx-cross-source:linea:growthepie` | ok | probe 12.9k/day (sampled-blocks) vs growthepie 13.2k/day: x0.977 |
| `tx-cross-source:linea:l2beat` | ok | probe 12.9k/day (sampled-blocks) vs l2beat 13.2k/day: x0.977 |
| `tx-cross-source:mantle:growthepie` | **FAIL** | probe 14.7k/day (sampled-blocks) vs growthepie 11.7k/day: x1.255 |
| `tx-cross-source:mantle:l2beat` | **FAIL** | probe 14.7k/day (sampled-blocks) vs l2beat 11.7k/day: x1.255 |
| `tx-cross-source:megaeth:growthepie` | **FAIL** | probe 2.0M/day (sampled-blocks) vs growthepie 1.1M/day: x1.733 |
| `tx-cross-source:megaeth:l2beat` | ok | probe 2.0M/day (sampled-blocks) vs l2beat 2.0M/day: x0.987 |
| `tx-cross-source:near:nearblocks` | ok | probe 713.8k/day (sampled-blocks) vs nearblocks 680.3k/day: x1.049 |
| `tx-cross-source:optimism:growthepie` | ok | probe 1.5M/day (sampled-blocks) vs growthepie 1.5M/day: x0.983 |
| `tx-cross-source:plume:growthepie` | ok | probe 209.4k/day (sampled-blocks) vs growthepie 209.9k/day: x0.997 |
| `tx-cross-source:polygon:growthepie` | ok | probe 5.3M/day (sampled-blocks) vs growthepie 5.3M/day: x0.999 |
| `tx-cross-source:polygon:l2beat` | ok | probe 5.3M/day (sampled-blocks) vs l2beat 5.3M/day: x0.999 |
| `tx-cross-source:robinhood:growthepie` | ok | probe 5.7M/day (sampled-blocks) vs growthepie 5.6M/day: x1.025 |
| `tx-cross-source:robinhood:l2beat` | ok | probe 5.7M/day (sampled-blocks) vs l2beat 5.6M/day: x1.025 |
| `tx-cross-source:ronin:growthepie` | ok | probe 269.8k/day (sampled-blocks) vs growthepie 301.0k/day: x0.896 |
| `tx-cross-source:scroll:growthepie` | ok | probe 10.1k/day (sampled-blocks) vs growthepie 9.5k/day: x1.062 |
| `tx-cross-source:scroll:l2beat` | ok | probe 10.1k/day (sampled-blocks) vs l2beat 9.5k/day: x1.061 |
| `tx-cross-source:soneium:growthepie` | ok | probe 322.9k/day (sampled-blocks) vs growthepie 332.8k/day: x0.970 |
| `tx-cross-source:soneium:l2beat` | ok | probe 322.9k/day (sampled-blocks) vs l2beat 332.9k/day: x0.970 |
| `tx-cross-source:starknet:growthepie` | ok | probe 259.9k/day (sampled-blocks) vs growthepie 212.3k/day: x1.224 |
| `tx-cross-source:starknet:l2beat` | ok | probe 259.9k/day (sampled-blocks) vs l2beat 217.0k/day: x1.197 |
| `tx-cross-source:tron:tronscan` | ok | probe 11.6M/day (sampled-blocks) vs tronscan 11.7M/day: x0.990 |
| `tx-cross-source:unichain:growthepie` | ok | probe 640.7k/day (sampled-blocks) vs growthepie 635.7k/day: x1.008 |
| `tx-cross-source:unichain:l2beat` | ok | probe 640.7k/day (sampled-blocks) vs l2beat 635.8k/day: x1.008 |
| `tx-cross-source:worldchain:growthepie` | ok | probe 640.0k/day (sampled-blocks) vs growthepie 629.6k/day: x1.017 |
| `tx-cross-source:xlayer:l2beat` | ok | probe 730.1k/day (sampled-blocks) vs l2beat 731.8k/day: x0.998 |
| `tx-cross-source:zcash:blockchair-24h` | ok | probe 6.5k/day (aggregator-24h) vs blockchair-24h 6.5k/day: x1.002 |
| `tx-cross-source:zksync:growthepie` | ok | probe 17.9k/day (sampled-blocks) vs growthepie 18.5k/day: x0.966 |
| `dex-breakdown` | **FAIL** | sum of per-chain 24h $7.3B vs DefiLlama total24h $7.6B (x0.9632) |
| `llama-keys` | ok | 0 contested of 264 inferred keys:  |
| `registry-ids` | ok | all registry identities resolve |
