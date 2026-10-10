# Detector sweep — research/2026-10-09/multi_1h

Ran 1 detector; 22 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `cross_chain_rate` | 22 | 0.000 | every priced cross-chain dollar switch, sized by min(high-side optimum, low-side withdrawable), plus the book filled once |

### [notable] the cross-chain dollar book absorbs $18.8M at 58bp, each destination filled once, cheapest source first (15 legs; the rows summed would claim $227,928 a year)

```json
{
 "total_size_usd": 18751289.190089326,
 "total_annual_usd": 108924.55325176465,
 "sum_of_rows_annual_usd": 227928.06731803188,
 "switches_priced": 21,
 "bindings": {
  "low-side withdrawable liquidity": 5,
  "high-side rate dilution": 16
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
  "apy": 0.038,
  "name": "Sky savings rate (read on-chain 2026-10-09 20:45 UTC)"
 },
 "flow_vs_yield_spearman": {
  "n": 7,
  "note": "rank correlation between a chain's USDC supply APR and its net CCTP USDC flow over this one hour; a negative value means dollars moved toward the lower rate",
  "rho": -0.14285714285714285
 },
 "why": "the rows compete for the same destination reserve; filled once, the book is what the whole surface is worth, and the CCTP rank correlation says whether the bridge is closing it"
}
```

Economics: net APR 0.58%, capacity $18.8M, GO — the book clears $250k and 50bp blended

### [notable] USDC pays 4.18pp more on avalanche than bsc; $1.8M of it can move (bound by high-side rate dilution), earning 5.15% at size for $37,097 a year

```json
{
 "asset": "USDC",
 "from": "bsc",
 "to": "avalanche",
 "from_pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.031148425908857497,
 "to_apr": 0.07295422915687204,
 "apr_at_size": 0.05152446466960772,
 "spread_pp": 4.180580324801454,
 "unconstrained_size_usd": 1820604.7632840946,
 "from_available_usd": 2115765.7618121314,
 "movable_usd": 1820604.7632840946,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 13339044.601664357,
 "to_supplied_usd": 70607970.620948,
 "from_utilisation": 0.8413862640548044,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 2.04%, capacity $1.8M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 4.14pp more on avalanche than arbitrum; $1.8M of it can move (bound by high-side rate dilution), earning 5.17% at size for $36,339 a year

```json
{
 "asset": "USDC",
 "from": "arbitrum",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.03156668481130635,
 "to_apr": 0.07295422915687204,
 "apr_at_size": 0.05174423440730956,
 "spread_pp": 4.138754434556569,
 "unconstrained_size_usd": 1800978.578239657,
 "from_available_usd": 20132219.666032,
 "movable_usd": 1800978.578239657,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 180264088.639411,
 "to_supplied_usd": 70607970.620948,
 "from_utilisation": 0.8883947774796617,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 2.02%, capacity $1.8M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 4.13pp more on avalanche than polygon; $1.8M of it can move (bound by high-side rate dilution), earning 5.18% at size for $36,162 a year

```json
{
 "asset": "USDC",
 "from": "polygon",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.03166527157572791,
 "to_apr": 0.07295422915687204,
 "apr_at_size": 0.05179601929601496,
 "spread_pp": 4.128895758114413,
 "unconstrained_size_usd": 1796357.0090303198,
 "from_available_usd": 10369037.758712,
 "movable_usd": 1796357.0090303198,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 27637121.985981,
 "to_supplied_usd": 70607970.620948,
 "from_utilisation": 0.6251731100762825,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 2.01%, capacity $1.8M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 3.22pp more on avalanche than base; $1.4M of it can move (bound by high-side rate dilution), earning 5.66% at size for $21,727 a year

```json
{
 "asset": "USDC",
 "from": "base",
 "to": "avalanche",
 "from_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.0407701499585843,
 "to_apr": 0.07295422915687204,
 "apr_at_size": 0.05655041978303232,
 "spread_pp": 3.2184079198287736,
 "unconstrained_size_usd": 1376847.8047433416,
 "from_available_usd": 17512124.038617,
 "movable_usd": 1376847.8047433416,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 181948581.608016,
 "to_supplied_usd": 70607970.620948,
 "from_utilisation": 0.9037558527815985,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.58%, capacity $1.4M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 2.95pp more on avalanche than ethereum; $1.3M of it can move (bound by high-side rate dilution), earning 5.79% at size for $18,243 a year

```json
{
 "asset": "USDC",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.04341533390354626,
 "to_apr": 0.07295422915687204,
 "apr_at_size": 0.05792149453041308,
 "spread_pp": 2.953889525332578,
 "unconstrained_size_usd": 1257602.3610297814,
 "from_available_usd": 134575282.29476,
 "movable_usd": 1257602.3610297814,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 2405821650.008549,
 "to_supplied_usd": 70607970.620948,
 "from_utilisation": 0.944066744393574,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.45%, capacity $1.3M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 2.46pp more on avalanche than optimism; $879k of it can move (bound by low-side withdrawable liquidity), earning 6.23% at size for $12,256 a year

```json
{
 "asset": "USDC",
 "from": "optimism",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
 "to_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "from_apr": 0.04838976832506667,
 "to_apr": 0.07295422915687204,
 "apr_at_size": 0.06233591994356842,
 "spread_pp": 2.4564460831805373,
 "unconstrained_size_usd": 1036435.2102915717,
 "from_available_usd": 878781.438538,
 "movable_usd": 878781.438538,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 10788295.762815,
 "to_supplied_usd": 70607970.620948,
 "from_utilisation": 0.9185384721998164,
 "rate_source": {
  "from": "head spot (unchecked: 3 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.39%, capacity $879k, GO — clears $250k and 50bp net at the movable size

### [notable] DAI pays 2.90pp more on polygon than arbitrum; $822k of it can move (bound by low-side withdrawable liquidity), earning 2.89% at size for $11,316 a year

```json
{
 "asset": "DAI",
 "from": "arbitrum",
 "to": "polygon",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.015124492250262253,
 "to_apr": 0.04415505007929775,
 "apr_at_size": 0.02889743835863107,
 "spread_pp": 2.9030557829035497,
 "unconstrained_size_usd": 976412.756217706,
 "from_available_usd": 821603.6313601464,
 "movable_usd": 821603.6313601464,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 3128201.7665193113,
 "to_supplied_usd": 3473245.8750840933,
 "from_utilisation": 0.7379181339383418,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.38%, capacity $822k, GO — clears $250k and 50bp net at the movable size

### [notable] GHO pays 2.06pp more on base than ethereum; $326k of it can move (bound by high-side rate dilution), earning 2.36% at size for $2,846 a year

```json
{
 "asset": "GHO",
 "from": "ethereum",
 "to": "base",
 "from_pool": "0xae05cd22df81871bc7cc2a04becfb516bfe332c8",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f",
 "to_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "from_apr": 0.014905187407873147,
 "to_apr": 0.035522973324719466,
 "apr_at_size": 0.023623043250571487,
 "spread_pp": 2.0617785916846323,
 "unconstrained_size_usd": 326493.3485080772,
 "from_available_usd": 29459787.51851276,
 "movable_usd": 326493.3485080772,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 60073007.608333305,
 "to_supplied_usd": 1442875.941960455,
 "from_utilisation": 0.5096002565647119,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 2 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.87%, capacity $326k, GO — clears $250k and 50bp net at the movable size

### [notable] DAI pays 1.57pp more on polygon than ethereum; $392k of it can move (bound by high-side rate dilution), earning 3.57% at size for $2,826 a year

```json
{
 "asset": "DAI",
 "from": "ethereum",
 "to": "polygon",
 "from_pool": "0xc13e21b648a5ee794902342038ff3adab66be987",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.02845672952548131,
 "to_apr": 0.04415505007929775,
 "apr_at_size": 0.035674212942853,
 "spread_pp": 1.5698320553816438,
 "unconstrained_size_usd": 391587.2538835283,
 "from_available_usd": 75110207.64165366,
 "movable_usd": 391587.2538835283,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 261080498.62640354,
 "to_supplied_usd": 3473245.8750840933,
 "from_utilisation": 0.7127216334049031,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.72%, capacity $392k, GO — clears $250k and 50bp net at the movable size

### [info] USDT pays 0.45pp more on ethereum than bsc; $10.5M of it can move (bound by low-side withdrawable liquidity), earning 3.53% at size for $44,473 a year

```json
{
 "asset": "USDT",
 "from": "bsc",
 "to": "ethereum",
 "from_pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0x55d398326f99059ff775485246999027b3197955",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.031039677192727436,
 "to_apr": 0.03553720099581354,
 "apr_at_size": 0.035259021587611385,
 "spread_pp": 0.4497523803086104,
 "unconstrained_size_usd": 92748212.298908,
 "from_available_usd": 10540365.315950457,
 "movable_usd": 10540365.315950457,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 64196743.69963989,
 "to_supplied_usd": 2721788638.014035,
 "from_utilisation": 0.8358124378414722,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.42%, capacity $10.5M, no — under $250k movable or under 50bp net at that size

### [info] USDT pays 0.43pp more on ethereum than optimism; $637k of it can move (bound by low-side withdrawable liquidity), earning 3.55% at size for $2,710 a year

```json
{
 "asset": "USDT",
 "from": "optimism",
 "to": "ethereum",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.03126424273972822,
 "to_apr": 0.03553720099581354,
 "apr_at_size": 0.03551598301361567,
 "spread_pp": 0.42729582560853197,
 "unconstrained_size_usd": 87765425.84864974,
 "from_available_usd": 637284.724196,
 "movable_usd": 637284.724196,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 4062627.946082,
 "to_supplied_usd": 2721788638.014035,
 "from_utilisation": 0.8430832073023828,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.43%, capacity $637k, no — under $250k movable or under 50bp net at that size

### [info] DAI pays 2.30pp more on polygon than optimism; $72k of it can move (bound by low-side withdrawable liquidity), earning 4.24% at size for $1,536 a year

```json
{
 "asset": "DAI",
 "from": "optimism",
 "to": "polygon",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.021123358915549582,
 "to_apr": 0.04415505007929775,
 "apr_at_size": 0.042376880614905334,
 "spread_pp": 2.303169116374817,
 "unconstrained_size_usd": 665509.5800602303,
 "from_available_usd": 72281.08811969549,
 "movable_usd": 72281.08811969549,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 564916.9380060266,
 "to_supplied_usd": 3473245.8750840933,
 "from_utilisation": 0.8720456524880849,
 "rate_source": {
  "from": "head spot (unchecked: 1 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 2.13%, capacity $72k, no — under $250k movable or under 50bp net at that size

### [info] USDS pays 21.94pp more on base than ethereum; $1k of it can move (bound by high-side rate dilution), earning 13.47% at size for $146 a year

```json
{
 "asset": "USDS",
 "from": "ethereum",
 "to": "base",
 "from_pool": "0xc13e21b648a5ee794902342038ff3adab66be987",
 "to_pool": "0x09b11746dfd1b5a8325e30943f8b3d5000922e03",
 "from_address": "0xdc035d45d973e3ec169d2276ddab16f1e407384f",
 "to_address": "0x820c137fa70c8691f0e44dc420a5e53c168921dc",
 "from_apr": 0.02697097559643681,
 "to_apr": 0.24637753685388972,
 "apr_at_size": 0.13474155334192284,
 "spread_pp": 21.94065612574529,
 "unconstrained_size_usd": 1354.3548353199653,
 "from_available_usd": 370508722.0007149,
 "movable_usd": 1354.3548353199653,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1210153813.9623668,
 "to_supplied_usd": 75215.68979805458,
 "from_utilisation": 0.6938662700626208,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 1 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 10.78%, capacity $1k, no — under $250k movable or under 50bp net at that size

### [info] LUSD pays 2.10pp more on optimism than ethereum; $13k of it can move (bound by high-side rate dilution), earning 1.29% at size for $96 a year

```json
{
 "asset": "LUSD",
 "from": "ethereum",
 "to": "optimism",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x5f98805a4e8be255a32880fdec7f6728c6568ba0",
 "to_address": "0xc40f949f8a4e094d1b49a23ea9241d289b7b2819",
 "from_apr": 0.005576653427963424,
 "to_apr": 0.026607990948934374,
 "apr_at_size": 0.012936748664781518,
 "spread_pp": 2.103133752097095,
 "unconstrained_size_usd": 13079.641620028444,
 "from_available_usd": 1250475.6724510961,
 "movable_usd": 13079.641620028444,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1877886.9273032001,
 "to_supplied_usd": 24280.29672016512,
 "from_utilisation": 0.3339663448822239,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.74%, capacity $13k, no — under $250k movable or under 50bp net at that size

### [info] FRAX pays 36.00pp more on avalanche than arbitrum; $4k of it can move (bound by high-side rate dilution), earning 1.81% at size for $59 a year

```json
{
 "asset": "FRAX",
 "from": "arbitrum",
 "to": "avalanche",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x17fc002b466eec40dae837fc4be5c67993ddbd6f",
 "to_address": "0xd24c2ad096400b6fbcd2ad8b24e7acbc21a1da64",
 "from_apr": 0.00392884475779489,
 "to_apr": 0.36392426367006353,
 "apr_at_size": 0.018102975098708743,
 "spread_pp": 35.99954189122687,
 "unconstrained_size_usd": 4170.651870113325,
 "from_available_usd": 122890.0422335013,
 "movable_usd": 4170.651870113325,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 171502.40184818226,
 "to_supplied_usd": 6466.996700097614,
 "from_utilisation": 0.28348342290144357,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.42%, capacity $4k, no — under $250k movable or under 50bp net at that size

### [info] LUSD pays 1.69pp more on optimism than arbitrum; $8k of it can move (bound by high-side rate dilution), earning 1.64% at size for $54 a year

```json
{
 "asset": "LUSD",
 "from": "arbitrum",
 "to": "optimism",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x93b346b6bc2548da6a1e7d98e9a421b42541425b",
 "to_address": "0xc40f949f8a4e094d1b49a23ea9241d289b7b2819",
 "from_apr": 0.009663008178857112,
 "to_apr": 0.026607990948934374,
 "apr_at_size": 0.01642811994438128,
 "spread_pp": 1.6944982770077264,
 "unconstrained_size_usd": 8020.178395634843,
 "from_available_usd": 118378.56260417966,
 "movable_usd": 8020.178395634843,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 190442.13978954457,
 "to_supplied_usd": 24280.29672016512,
 "from_utilisation": 0.3799208880777273,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.68%, capacity $8k, no — under $250k movable or under 50bp net at that size

### [info] USDe pays 1.39pp more on avalanche than ethereum; $7k of it can move (bound by high-side rate dilution), earning 0.62% at size for $27 a year

```json
{
 "asset": "USDe",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
 "to_address": "0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34",
 "from_apr": 0.0023662454289796234,
 "to_apr": 0.016309019856512064,
 "apr_at_size": 0.0062124515803551545,
 "spread_pp": 1.394277442753244,
 "unconstrained_size_usd": 7098.801252094438,
 "from_available_usd": 316432824.3804537,
 "movable_usd": 7098.801252094438,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 332281795.70030785,
 "to_supplied_usd": 4433.925608250497,
 "from_utilisation": 0.047707149526581005,
 "rate_source": {
  "from": "head spot (unchecked: 4 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.38%, capacity $7k, no — under $250k movable or under 50bp net at that size

### [info] FRAX pays 14.81pp more on avalanche than ethereum; $143 of it can move (bound by high-side rate dilution), earning 28.84% at size for $10 a year

```json
{
 "asset": "FRAX",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x853d955acef822db058eb8505911ed77f175b99e",
 "to_address": "0xd24c2ad096400b6fbcd2ad8b24e7acbc21a1da64",
 "from_apr": 0.2158206447566147,
 "to_apr": 0.36392426367006353,
 "apr_at_size": 0.2883562790642673,
 "spread_pp": 14.810361891344884,
 "unconstrained_size_usd": 143.4153144265078,
 "from_available_usd": 1279.0586634116044,
 "movable_usd": 143.4153144265078,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 29620.500786070217,
 "to_supplied_usd": 6466.996700097614,
 "from_utilisation": 0.95675237150708,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 7.25%, capacity $143, no — under $250k movable or under 50bp net at that size

### [info] GHO pays 0.06pp more on base than avalanche; $6k of it can move (bound by high-side rate dilution), earning 3.52% at size for $2 a year

```json
{
 "asset": "GHO",
 "from": "avalanche",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0xfc421ad3c883bf9e7c4f42de845c4e4405799e73",
 "to_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "from_apr": 0.03489034828417203,
 "to_apr": 0.035522973324719466,
 "apr_at_size": 0.03520559926789328,
 "spread_pp": 0.06326250405474382,
 "unconstrained_size_usd": 6489.440923379618,
 "from_available_usd": 119433.40991921307,
 "movable_usd": 6489.440923379618,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1025920.6498575769,
 "to_supplied_usd": 1442875.941960455,
 "from_utilisation": 0.8829457808238625,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 2 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.03%, capacity $6k, no — under $250k movable or under 50bp net at that size

### [info] GHO pays 0.05pp more on base than arbitrum; $5k of it can move (bound by high-side rate dilution), earning 3.53% at size for $1 a year

```json
{
 "asset": "GHO",
 "from": "arbitrum",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x7dff72693f6a4149b17e7c6314655f6a9f7c8b33",
 "to_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "from_apr": 0.03501836272305475,
 "to_apr": 0.035522973324719466,
 "apr_at_size": 0.03526999501254811,
 "spread_pp": 0.050461060166471366,
 "unconstrained_size_usd": 5165.670426134135,
 "from_available_usd": 76737.84712502506,
 "movable_usd": 5165.670426134135,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 650177.3442541234,
 "to_supplied_usd": 1442875.941960455,
 "from_utilisation": 0.8821487673586126,
 "rate_source": {
  "from": "head spot (unchecked: 2 updates)",
  "to": "head spot (unchecked: 2 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.03%, capacity $5k, no — under $250k movable or under 50bp net at that size

### [info] sUSDS pays 0.00pp more on base than ethereum; $43k of it can move (bound by high-side rate dilution), earning 0.00% at size for $0 a year

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
 "to_apr": 1.1957373187637376e-08,
 "apr_at_size": 2.989343286808559e-09,
 "spread_pp": 1.1957373187637375e-06,
 "unconstrained_size_usd": 42688.646560290304,
 "from_available_usd": 2978342.366278326,
 "movable_usd": 42688.646560290304,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 2978342.366278326,
 "to_supplied_usd": 42688.58443108979,
 "from_utilisation": 3.111507638930571e-61,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.00%, capacity $43k, no — under $250k movable or under 50bp net at that size

