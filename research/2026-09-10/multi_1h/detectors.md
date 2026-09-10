# Detector sweep — research/2026-09-10/multi_1h

Ran 1 detector; 24 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `cross_chain_rate` | 24 | 0.000 | every priced cross-chain dollar switch, sized by min(high-side optimum, low-side withdrawable), plus the book filled once |

### [notable] the cross-chain dollar book absorbs $21.1M at 67bp, each destination filled once, cheapest source first (17 legs; the rows summed would claim $271,761 a year)

```json
{
 "total_size_usd": 21082232.97927631,
 "total_annual_usd": 141067.6079111909,
 "sum_of_rows_annual_usd": 271761.46285229916,
 "switches_priced": 23,
 "bindings": {
  "low-side withdrawable liquidity": 8,
  "high-side rate dilution": 15
 },
 "dollar_reserves": 63,
 "chains": [
  "arbitrum",
  "avalanche",
  "base",
  "bsc",
  "ethereum",
  "linea",
  "optimism",
  "polygon",
  "scroll",
  "unichain"
 ],
 "benchmark": {
  "apy": 0.03599999699843881,
  "name": "Sky savings rate (SSR), read on Ethereum at block 25942222"
 },
 "flow_vs_yield_spearman": {
  "n": 9,
  "note": "rank correlation between a chain's USDC supply APR and its net CCTP USDC flow over this one hour; a negative value means dollars moved toward the lower rate",
  "rho": -0.2677847708018314
 },
 "why": "the rows compete for the same destination reserve; filled once, the book is what the whole surface is worth, and the CCTP rank correlation says whether the bridge is closing it"
}
```

Economics: net APR 0.67%, capacity $21.1M, GO — the book clears $250k and 50bp blended

### [notable] USDT pays 0.85pp more on ethereum than bsc; $10.2M of it can move (bound by low-side withdrawable liquidity), earning 3.70% at size for $70,991 a year

```json
{
 "asset": "USDT",
 "from": "bsc",
 "to": "ethereum",
 "from_pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0x55d398326f99059ff775485246999027b3197955",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.0300757130850757,
 "to_apr": 0.0385975001194506,
 "apr_at_size": 0.03702347318394543,
 "spread_pp": 0.8521787034374901,
 "unconstrained_size_usd": 160765341.68298453,
 "from_available_usd": 10217764.099227788,
 "movable_usd": 10217764.099227788,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 59020637.18063157,
 "to_supplied_usd": 2956748473.356633,
 "from_utilisation": 0.8268786024609771,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.69%, capacity $10.2M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 4.57pp more on avalanche than optimism; $2.1M of it can move (bound by low-side withdrawable liquidity), earning 4.27% at size for $35,160 a year

```json
{
 "asset": "USDC",
 "from": "optimism",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.02622725522657783,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.042686966718665564,
 "spread_pp": 4.568532746406211,
 "unconstrained_size_usd": 5998234.465836311,
 "from_available_usd": 2136126.764021,
 "movable_usd": 2136126.764021,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 11224860.563831,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.8096855310624571,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.65%, capacity $2.1M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 4.33pp more on avalanche than polygon; $1.6M of it can move (bound by high-side rate dilution), earning 4.97% at size for $33,604 a year

```json
{
 "asset": "USDC",
 "from": "polygon",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.028652132495210387,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.04973171097643509,
 "spread_pp": 4.326045019542955,
 "unconstrained_size_usd": 1594142.311305616,
 "from_available_usd": 11978104.186307,
 "movable_usd": 1594142.311305616,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 29835947.352788,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.5986535184121433,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 2.11%, capacity $1.6M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 4.08pp more on avalanche than bsc; $1.5M of it can move (bound by high-side rate dilution), earning 5.10% at size for $29,833 a year

```json
{
 "asset": "USDC",
 "from": "bsc",
 "to": "avalanche",
 "from_pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.031091990338652183,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.051014781156503666,
 "spread_pp": 4.082059235198775,
 "unconstrained_size_usd": 1497408.658249374,
 "from_available_usd": 2254247.5945793744,
 "movable_usd": 1497408.658249374,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 14142412.523764009,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.8406040934025607,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.99%, capacity $1.5M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 4.45pp more on avalanche than arbitrum; $5.3M of it can move (bound by high-side rate dilution), earning 3.28% at size for $28,649 a year

```json
{
 "asset": "USDC",
 "from": "arbitrum",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.027421394486680965,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.03281538977004961,
 "spread_pp": 4.449118820395897,
 "unconstrained_size_usd": 5311276.731962064,
 "from_available_usd": 29211968.335179,
 "movable_usd": 5311276.731962064,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 169803336.120469,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.8280407330724395,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.54%, capacity $5.3M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 3.49pp more on avalanche than base; $1.3M of it can move (bound by high-side rate dilution), earning 5.41% at size for $21,644 a year

```json
{
 "asset": "USDC",
 "from": "base",
 "to": "avalanche",
 "from_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.03701991911152463,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.05411532544936101,
 "spread_pp": 3.489266357911531,
 "unconstrained_size_usd": 1266084.059629138,
 "from_available_usd": 20464776.341829,
 "movable_usd": 1266084.059629138,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 183784019.323602,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.8886480204986353,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.71%, capacity $1.3M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 3.48pp more on avalanche than ethereum; $1.3M of it can move (bound by high-side rate dilution), earning 5.42% at size for $21,500 a year

```json
{
 "asset": "USDC",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.037134037521090985,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.054174783304561984,
 "spread_pp": 3.477854516954895,
 "unconstrained_size_usd": 1261681.2354983725,
 "from_available_usd": 140930288.202934,
 "movable_usd": 1261681.2354983725,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 2311681888.892313,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.9390385994657926,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.70%, capacity $1.3M, GO — clears $250k and 50bp net at the movable size

### [notable] USDT pays 1.01pp more on ethereum than optimism; $848k of it can move (bound by low-side withdrawable liquidity), earning 3.79% at size for $7,909 a year

```json
{
 "asset": "USDT",
 "from": "optimism",
 "to": "ethereum",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.028527991194845056,
 "to_apr": 0.0385975001194506,
 "apr_at_size": 0.03785403540760413,
 "spread_pp": 1.0069508924605546,
 "unconstrained_size_usd": 200900692.77077216,
 "from_available_usd": 848078.646136,
 "movable_usd": 848078.646136,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 4357967.514115,
 "to_supplied_usd": 2956748473.356633,
 "from_utilisation": 0.8053360532944651,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.93%, capacity $848k, GO — clears $250k and 50bp net at the movable size

### [notable] DAI pays 1.97pp more on polygon than arbitrum; $683k of it can move (bound by high-side rate dilution), earning 2.77% at size for $5,856 a year

```json
{
 "asset": "DAI",
 "from": "arbitrum",
 "to": "polygon",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.01910107912861677,
 "to_apr": 0.038765949878192915,
 "apr_at_size": 0.027681393855474284,
 "spread_pp": 1.9664870749576144,
 "unconstrained_size_usd": 682525.8187475253,
 "from_available_usd": 1159921.123913715,
 "movable_usd": 682525.8187475253,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 3588452.9264733074,
 "to_supplied_usd": 3719310.4608114716,
 "from_utilisation": 0.6770940531707537,
 "rate_source": {
  "from": "head spot (unchecked: 3 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.86%, capacity $683k, GO — clears $250k and 50bp net at the movable size

### [notable] DAI pays 1.42pp more on polygon than ethereum; $434k of it can move (bound by high-side rate dilution), earning 3.11% at size for $2,821 a year

```json
{
 "asset": "DAI",
 "from": "ethereum",
 "to": "polygon",
 "from_pool": "0xc13e21b648a5ee794902342038ff3adab66be987",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.02459267191285984,
 "to_apr": 0.038765949878192915,
 "apr_at_size": 0.03108906786489119,
 "spread_pp": 1.4173277965333075,
 "unconstrained_size_usd": 434168.9345698657,
 "from_available_usd": 99926898.15478468,
 "movable_usd": 434168.9345698657,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 307841341.81113034,
 "to_supplied_usd": 3719310.4608114716,
 "from_utilisation": 0.6757838977465762,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.65%, capacity $434k, GO — clears $250k and 50bp net at the movable size

### [info] USDC pays 3.83pp more on avalanche than linea; $207k of it can move (bound by low-side withdrawable liquidity), earning 6.89% at size for $7,308 a year

```json
{
 "asset": "USDC",
 "from": "linea",
 "to": "avalanche",
 "from_pool": "0xc47b8c00b0f69a36fa203ffeac0334874574a8ac",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x176211869ca2b568f2a7d4ee941e073a821ee1ff",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.03358717371239542,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.06891382421852597,
 "spread_pp": 3.832540897824452,
 "unconstrained_size_usd": 1399408.2224950828,
 "from_available_usd": 206874.055717,
 "movable_usd": 206874.055717,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 1637912.491149,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.873696453130772,
 "rate_source": {
  "from": "head spot (unchecked: 1 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 3.53%, capacity $207k, no — under $250k movable or under 50bp net at that size

### [info] USDC pays 6.83pp more on avalanche than scroll; $64k of it can move (bound by low-side withdrawable liquidity), earning 7.10% at size for $4,330 a year

```json
{
 "asset": "USDC",
 "from": "scroll",
 "to": "avalanche",
 "from_pool": "0x11fcfe756c05ad438e312a7fd934381537d3cffe",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x06efdbff2a14a7c8e15944d1f4a48f9f95f663a4",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.0036621081818068333,
 "to_apr": 0.07191258269063994,
 "apr_at_size": 0.07098363255981383,
 "spread_pp": 6.825047450883311,
 "unconstrained_size_usd": 36101454.388685256,
 "from_available_usd": 64315.809457,
 "movable_usd": 64315.809457,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 248909.88696,
 "to_supplied_usd": 59320431.034521,
 "from_utilisation": 0.7413843880721118,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 6.73%, capacity $64k, no — under $250k movable or under 50bp net at that size

### [info] GHO pays 6.81pp more on avalanche than arbitrum; $99k of it can move (bound by high-side rate dilution), earning 3.17% at size for $537 a year

```json
{
 "asset": "GHO",
 "from": "arbitrum",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x7dff72693f6a4149b17e7c6314655f6a9f7c8b33",
 "to_address": "0xfc421ad3c883bf9e7c4f42de845c4e4405799e73",
 "from_apr": 0.026306527843618983,
 "to_apr": 0.09441770012463936,
 "apr_at_size": 0.031704863218798555,
 "spread_pp": 6.811117228102037,
 "unconstrained_size_usd": 99385.87228119967,
 "from_available_usd": 170497.57715134957,
 "movable_usd": 99385.87228119967,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 723662.8362820086,
 "to_supplied_usd": 1073598.1884748554,
 "from_utilisation": 0.7645848018795847,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 2 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.54%, capacity $99k, no — under $250k movable or under 50bp net at that size

### [info] DAI pays 0.79pp more on polygon than optimism; $85k of it can move (bound by low-side withdrawable liquidity), earning 3.71% at size for $522 a year

```json
{
 "asset": "DAI",
 "from": "optimism",
 "to": "polygon",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.030900319285554038,
 "to_apr": 0.038765949878192915,
 "apr_at_size": 0.03706032103704423,
 "spread_pp": 0.7865630592638877,
 "unconstrained_size_usd": 213833.49989947514,
 "from_available_usd": 84701.39701979009,
 "movable_usd": 84701.39701979009,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 610179.8790565414,
 "to_supplied_usd": 3719310.4608114716,
 "from_utilisation": 0.8611783440664107,
 "rate_source": {
  "from": "head spot (unchecked: 1 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.62%, capacity $85k, no — under $250k movable or under 50bp net at that size

### [info] GHO pays 5.89pp more on avalanche than base; $10k of it can move (bound by high-side rate dilution), earning 6.49% at size for $307 a year

```json
{
 "asset": "GHO",
 "from": "base",
 "to": "avalanche",
 "from_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "to_address": "0xfc421ad3c883bf9e7c4f42de845c4e4405799e73",
 "from_apr": 0.03550423097207163,
 "to_apr": 0.09441770012463936,
 "apr_at_size": 0.06492225686293046,
 "spread_pp": 5.891346915256773,
 "unconstrained_size_usd": 10446.912184837853,
 "from_available_usd": 158772.94213068526,
 "movable_usd": 10446.912184837853,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1420744.4360504942,
 "to_supplied_usd": 1073598.1884748554,
 "from_utilisation": 0.8882471869009096,
 "rate_source": {
  "from": "head spot (unchecked: 6 updates)",
  "to": "head spot (unchecked: 2 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 2.94%, capacity $10k, no — under $250k movable or under 50bp net at that size

### [info] USDS pays 0.61pp more on ethereum than base; $48k of it can move (bound by low-side withdrawable liquidity), earning 2.32% at size for $294 a year

```json
{
 "asset": "USDS",
 "from": "base",
 "to": "ethereum",
 "from_pool": "0x09b11746dfd1b5a8325e30943f8b3d5000922e03",
 "to_pool": "0xc13e21b648a5ee794902342038ff3adab66be987",
 "from_address": "0x820c137fa70c8691f0e44dc420a5e53c168921dc",
 "to_address": "0xdc035d45d973e3ec169d2276ddab16f1e407384f",
 "from_apr": 0.017080006548361625,
 "to_apr": 0.023185550715293848,
 "apr_at_size": 0.023183166914320725,
 "spread_pp": 0.6105544166932222,
 "unconstrained_size_usd": 72762106.27532056,
 "from_available_usd": 48104.01176452861,
 "movable_usd": 48104.01176452861,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 125186.90162977694,
 "to_supplied_usd": 935624647.1086725,
 "from_utilisation": 0.6160809208819105,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 7 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.61%, capacity $48k, no — under $250k movable or under 50bp net at that size

### [info] USDT pays 0.47pp more on ethereum than linea; $54k of it can move (bound by low-side withdrawable liquidity), earning 3.82% at size for $234 a year

```json
{
 "asset": "USDT",
 "from": "linea",
 "to": "ethereum",
 "from_pool": "0xc47b8c00b0f69a36fa203ffeac0334874574a8ac",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0xa219439258ca9da29e9cc4ce5596924745e12b93",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.03388704096416664,
 "to_apr": 0.0385975001194506,
 "apr_at_size": 0.03822059490979843,
 "spread_pp": 0.4710459155283959,
 "unconstrained_size_usd": 70947664.64192843,
 "from_available_usd": 53920.917887,
 "movable_usd": 53920.917887,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 440514.478855,
 "to_supplied_usd": 2956748473.356633,
 "from_utilisation": 0.8775876166101686,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.43%, capacity $54k, no — under $250k movable or under 50bp net at that size

### [info] LUSD pays 2.10pp more on optimism than ethereum; $13k of it can move (bound by high-side rate dilution), earning 1.28% at size for $97 a year

```json
{
 "asset": "LUSD",
 "from": "ethereum",
 "to": "optimism",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
 "to_address": "0xc40f949f8a4e094d1b49a23ea9241d289b7b2819",
 "from_apr": 0.0054431567105405,
 "to_apr": 0.026435524987623065,
 "apr_at_size": 0.012756839018371678,
 "spread_pp": 2.0992368277082565,
 "unconstrained_size_usd": 13235.402631813595,
 "from_available_usd": 1271387.0056810286,
 "movable_usd": 13235.402631813595,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1897744.878107187,
 "to_supplied_usd": 24234.075476048238,
 "from_utilisation": 0.329944798026513,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.73%, capacity $13k, no — under $250k movable or under 50bp net at that size

### [info] FRAX pays 22.71pp more on avalanche than arbitrum; $4k of it can move (bound by high-side rate dilution), earning 1.71% at size for $54 a year

```json
{
 "asset": "FRAX",
 "from": "arbitrum",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x17fc002b466eec40dae837fc4be5c67993ddbd6f",
 "to_address": "0xd24c2ad096400b6fbcd2ad8b24e7acbc21a1da64",
 "from_apr": 0.003950837673808869,
 "to_apr": 0.23103616579147865,
 "apr_at_size": 0.017113662338084635,
 "spread_pp": 22.708532811766975,
 "unconstrained_size_usd": 4099.945336142382,
 "from_available_usd": 122741.4299457148,
 "movable_usd": 4099.945336142382,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 171470.9991556274,
 "to_supplied_usd": 6553.6403220797465,
 "from_utilisation": 0.28427575842743513,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.32%, capacity $4k, no — under $250k movable or under 50bp net at that size

### [info] LUSD pays 1.65pp more on optimism than arbitrum; $8k of it can move (bound by high-side rate dilution), earning 1.66% at size for $51 a year

```json
{
 "asset": "LUSD",
 "from": "arbitrum",
 "to": "optimism",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x93b346b6bc2548da6a1e7d98e9a421b42541425b",
 "to_address": "0xc40f949f8a4e094d1b49a23ea9241d289b7b2819",
 "from_apr": 0.00994370581157304,
 "to_apr": 0.026435524987623065,
 "apr_at_size": 0.01658196379764766,
 "spread_pp": 1.6491819176050027,
 "unconstrained_size_usd": 7703.099260473944,
 "from_available_usd": 117372.5116902898,
 "movable_usd": 7703.099260473944,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 191119.05813219203,
 "to_supplied_usd": 24234.075476048238,
 "from_utilisation": 0.3867429310574233,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.66%, capacity $8k, no — under $250k movable or under 50bp net at that size

### [info] USDe pays 2.55pp more on avalanche than ethereum; $4k of it can move (bound by high-side rate dilution), earning 1.94% at size for $40 a year

```json
{
 "asset": "USDe",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
 "to_address": "0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34",
 "from_apr": 0.010431712074797974,
 "to_apr": 0.03592839395944759,
 "apr_at_size": 0.01939176978384413,
 "spread_pp": 2.549668188464961,
 "unconstrained_size_usd": 4417.409492043629,
 "from_available_usd": 519393724.7539881,
 "movable_usd": 4417.409492043629,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 667711099.27809,
 "to_supplied_usd": 5874.642397648317,
 "from_utilisation": 0.22217324644642844,
 "rate_source": {
  "from": "window time-weighted",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.90%, capacity $4k, no — under $250k movable or under 50bp net at that size

### [info] FRAX pays 20.39pp more on avalanche than ethereum; $232 of it can move (bound by high-side rate dilution), earning 12.56% at size for $23 a year

```json
{
 "asset": "FRAX",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x853d955acef822db058eb8505911ed77f175b99e",
 "to_address": "0xd24c2ad096400b6fbcd2ad8b24e7acbc21a1da64",
 "from_apr": 0.02713900184854165,
 "to_apr": 0.23103616579147865,
 "apr_at_size": 0.12564400827216105,
 "spread_pp": 20.3897163942937,
 "unconstrained_size_usd": 231.97445804128296,
 "from_available_usd": 9924.463686735166,
 "movable_usd": 231.97445804128296,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 38802.25148621988,
 "to_supplied_usd": 6553.6403220797465,
 "from_utilisation": 0.7451003053759371,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 9.85%, capacity $232, no — under $250k movable or under 50bp net at that size

### [info] sUSDS pays 0.00pp more on base than ethereum; $67k of it can move (bound by high-side rate dilution), earning 0.00% at size for $0 a year

```json
{
 "asset": "sUSDS",
 "from": "ethereum",
 "to": "base",
 "from_pool": "0xc13e21b648a5ee794902342038ff3adab66be987",
 "to_pool": "0x09b11746dfd1b5a8325e30943f8b3d5000922e03",
 "from_address": "0xa3931d71877c0e7a3148cb7eb4463524fec27fbd",
 "to_address": "0x5875eee11cf8398102fdad704c9e96607675467a",
 "from_apr": 0.0,
 "to_apr": 4.925431933908977e-09,
 "apr_at_size": 1.2313580068935613e-09,
 "spread_pp": 4.925431933908977e-07,
 "unconstrained_size_usd": 66513.12035696136,
 "from_available_usd": 2978530.2695547114,
 "movable_usd": 66513.12035696136,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 2978530.2695547114,
 "to_supplied_usd": 66513.10714001025,
 "from_utilisation": 3.111507638930571e-61,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.00%, capacity $67k, no — under $250k movable or under 50bp net at that size

