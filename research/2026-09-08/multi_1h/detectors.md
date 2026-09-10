# Detector sweep — research/2026-09-08/multi_1h

Ran 1 detector; 21 hit(s).

| detector | hits | seconds | what it looks for |
|---|---:|---:|---|
| `cross_chain_rate` | 21 | 0.000 | every priced cross-chain dollar switch, sized by min(high-side optimum, low-side withdrawable), plus the book filled once |

### [notable] USDC pays 1.32pp more on base than arbitrum; $15.8M of it can move (bound by high-side rate dilution), earning 3.18% at size for $79,348 a year

```json
{
 "asset": "USDC",
 "from": "arbitrum",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.026741843290162815,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.031768173489831485,
 "spread_pp": 1.3245458720741283,
 "unconstrained_size_usd": 15786551.682792377,
 "from_available_usd": 32425667.978483,
 "movable_usd": 15786551.682792377,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 174215353.932516,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.8139514279900948,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.50%, capacity $15.8M, GO — clears $250k and 50bp net at the movable size

### [notable] USDT pays 0.63pp more on ethereum than bsc; $10.3M of it can move (bound by low-side withdrawable liquidity), earning 3.54% at size for $62,516 a year

```json
{
 "asset": "USDT",
 "from": "bsc",
 "to": "ethereum",
 "from_pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0x55d398326f99059ff775485246999027b3197955",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.02930166952161186,
 "to_apr": 0.03560616096824923,
 "apr_at_size": 0.03535818784863139,
 "spread_pp": 0.6304491446637368,
 "unconstrained_size_usd": 146952387.88327283,
 "from_available_usd": 10322116.141672803,
 "movable_usd": 10322116.141672803,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 58830751.46660538,
 "to_supplied_usd": 2982756522.737711,
 "from_utilisation": 0.8245456496058314,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.61%, capacity $10.3M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 1.44pp more on base than optimism; $2.3M of it can move (bound by low-side withdrawable liquidity), earning 3.66% at size for $24,754 a year

```json
{
 "asset": "USDC",
 "from": "optimism",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.02558440843750234,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.03655768801037241,
 "spread_pp": 1.440289357340176,
 "unconstrained_size_usd": 17899013.013147093,
 "from_available_usd": 2255850.020359,
 "movable_usd": 2255850.020359,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 11267592.883695,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.7997807662375056,
 "rate_source": {
  "from": "head spot (unchecked: 3 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.10%, capacity $2.3M, GO — clears $250k and 50bp net at the movable size

### [notable] USDC pays 1.12pp more on base than bsc; $2.6M of it can move (bound by low-side withdrawable liquidity), earning 3.64% at size for $19,628 a year

```json
{
 "asset": "USDC",
 "from": "bsc",
 "to": "base",
 "from_pool": "0x6807dc923806fe8fd134338eabca509979a7e0cb",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.028822516682546283,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.03643064120291014,
 "spread_pp": 1.1164785328357816,
 "unconstrained_size_usd": 12228769.940689877,
 "from_available_usd": 2579931.3878038195,
 "movable_usd": 2579931.3878038195,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 14231202.598396039,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.8187130724068732,
 "rate_source": {
  "from": "head spot (unchecked: 3 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.76%, capacity $2.6M, GO — clears $250k and 50bp net at the movable size

### [notable] USDT pays 0.86pp more on ethereum than optimism; $904k of it can move (bound by low-side withdrawable liquidity), earning 3.56% at size for $7,733 a year

```json
{
 "asset": "USDT",
 "from": "optimism",
 "to": "ethereum",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "from_address": "0x94b008aa00579c1307b0ef2c499ad98a8ce58e58",
 "to_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
 "from_apr": 0.02702686478025745,
 "to_apr": 0.03560616096824923,
 "apr_at_size": 0.03558175722189861,
 "spread_pp": 0.8579296187991778,
 "unconstrained_size_usd": 208844376.12413472,
 "from_available_usd": 903956.006335,
 "movable_usd": 903956.006335,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 4366677.315444,
 "to_supplied_usd": 2982756522.737711,
 "from_utilisation": 0.7929236213459863,
 "rate_source": {
  "from": "head spot (unchecked: 1 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.86%, capacity $904k, GO — clears $250k and 50bp net at the movable size

### [notable] DAI pays 1.63pp more on polygon than arbitrum; $598k of it can move (bound by high-side rate dilution), earning 2.70% at size for $4,341 a year

```json
{
 "asset": "DAI",
 "from": "arbitrum",
 "to": "polygon",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.019776560752829655,
 "to_apr": 0.03606936690463246,
 "apr_at_size": 0.027035420911077364,
 "spread_pp": 1.6292806151802803,
 "unconstrained_size_usd": 597969.2206715718,
 "from_available_usd": 1098268.1529317908,
 "movable_usd": 597969.2206715718,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 3527475.2782703703,
 "to_supplied_usd": 3854522.064751615,
 "from_utilisation": 0.688962654301446,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.73%, capacity $598k, GO — clears $250k and 50bp net at the movable size

### [notable] GHO pays 3.82pp more on base than ethereum; $307k of it can move (bound by high-side rate dilution), earning 2.47% at size for $2,747 a year

```json
{
 "asset": "GHO",
 "from": "ethereum",
 "to": "base",
 "from_pool": "0xae05cd22df81871bc7cc2a04becfb516bfe332c8",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f",
 "to_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "from_apr": 0.01574544141535374,
 "to_apr": 0.053929161960120146,
 "apr_at_size": 0.024680214804263807,
 "spread_pp": 3.81837205447664,
 "unconstrained_size_usd": 307493.02264791063,
 "from_available_usd": 24998380.266835384,
 "movable_usd": 307493.02264791063,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 59978584.874303065,
 "to_supplied_usd": 1391257.4663792488,
 "from_utilisation": 0.5832115692755271,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 6 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.89%, capacity $307k, GO — clears $250k and 50bp net at the movable size

### [notable] DAI pays 1.15pp more on polygon than ethereum; $377k of it can move (bound by high-side rate dilution), earning 2.99% at size for $2,013 a year

```json
{
 "asset": "DAI",
 "from": "ethereum",
 "to": "polygon",
 "from_pool": "0xc13e21b648a5ee794902342038ff3adab66be987",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x6b175474e89094c44da98b954eedeac495271d0f",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.024592179370067257,
 "to_apr": 0.03606936690463246,
 "apr_at_size": 0.029926798069517885,
 "spread_pp": 1.14771875345652,
 "unconstrained_size_usd": 377331.52789437666,
 "from_available_usd": 100110859.47878939,
 "movable_usd": 377331.52789437666,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 308405114.76763976,
 "to_supplied_usd": 3854522.064751615,
 "from_utilisation": 0.6757771304023044,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.53%, capacity $377k, GO — clears $250k and 50bp net at the movable size

### [info] the cross-chain dollar book absorbs $37.3M at 48bp, each destination filled once, cheapest source first (14 legs; the rows summed would claim $279,425 a year)

```json
{
 "total_size_usd": 37276234.70931492,
 "total_annual_usd": 177793.53974701528,
 "sum_of_rows_annual_usd": 279425.4482091083,
 "switches_priced": 20,
 "bindings": {
  "high-side rate dilution": 13,
  "low-side withdrawable liquidity": 7
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
  "name": "Sky savings rate (SSR), read on Ethereum at block 25931150"
 },
 "flow_vs_yield_spearman": {
  "n": 8,
  "note": "rank correlation between a chain's USDC supply APR and its net CCTP USDC flow over this one hour; a negative value means dollars moved toward the lower rate",
  "rho": -0.5748606057183643
 },
 "why": "the rows compete for the same destination reserve; filled once, the book is what the whole surface is worth, and the CCTP rank correlation says whether the bridge is closing it"
}
```

Economics: net APR 0.48%, capacity $37.3M, no — the book is under $250k or under 50bp blended

### [info] USDC pays 1.19pp more on base than polygon; $12.2M of it can move (bound by low-side withdrawable liquidity), earning 3.29% at size for $58,812 a year

```json
{
 "asset": "USDC",
 "from": "polygon",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.028121300602676407,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.032939681260442326,
 "spread_pp": 1.1866001408227693,
 "unconstrained_size_usd": 13395459.985913437,
 "from_available_usd": 12205848.919788,
 "movable_usd": 12205848.919788,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 30002728.273867,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.5932775392322409,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.48%, capacity $12.2M, no — under $250k movable or under 50bp net at that size

### [info] USDC pays 0.71pp more on base than avalanche; $6.0M of it can move (bound by high-side rate dilution), earning 3.51% at size for $13,230 a year

```json
{
 "asset": "USDC",
 "from": "avalanche",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.03292428437059128,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.03513792676139773,
 "spread_pp": 0.7063017640312821,
 "unconstrained_size_usd": 5976788.650652602,
 "from_available_usd": 7639950.66966,
 "movable_usd": 5976788.650652602,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 61202608.577097,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.8751540039164265,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.22%, capacity $6.0M, no — under $250k movable or under 50bp net at that size

### [info] USDC pays 3.63pp more on base than scroll; $65k of it can move (bound by low-side withdrawable liquidity), earning 3.91% at size for $2,308 a year

```json
{
 "asset": "USDC",
 "from": "scroll",
 "to": "base",
 "from_pool": "0x11fcfe756c05ad438e312a7fd934381537d3cffe",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x06efdbff2a14a7c8e15944d1f4a48f9f95f663a4",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.0036379930883277322,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.03905291532898175,
 "spread_pp": 3.6349308922576364,
 "unconstrained_size_usd": 110493281.95386922,
 "from_available_usd": 65165.062969,
 "movable_usd": 65165.062969,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 249835.355083,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.7389385052016835,
 "rate_source": {
  "from": "head spot (unchecked: 1 updates)",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 3.54%, capacity $65k, no — under $250k movable or under 50bp net at that size

### [info] USDC pays 0.39pp more on base than ethereum; $1.8M of it can move (bound by high-side rate dilution), earning 3.68% at size for $1,227 a year

```json
{
 "asset": "USDC",
 "from": "ethereum",
 "to": "base",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
 "to_address": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
 "from_apr": 0.0360561619719762,
 "to_apr": 0.0399873020109041,
 "apr_at_size": 0.03675342403691467,
 "spread_pp": 0.3931140038927902,
 "unconstrained_size_usd": 1759843.2445915486,
 "from_available_usd": 142502438.519985,
 "movable_usd": 1759843.2445915486,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 2307442353.444558,
 "to_supplied_usd": 183766508.754312,
 "from_utilisation": 0.9382436617742229,
 "rate_source": {
  "from": "window time-weighted",
  "to": "window time-weighted"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.07%, capacity $1.8M, no — under $250k movable or under 50bp net at that size

### [info] DAI pays 0.54pp more on polygon than optimism; $87k of it can move (bound by low-side withdrawable liquidity), earning 3.45% at size for $337 a year

```json
{
 "asset": "DAI",
 "from": "optimism",
 "to": "polygon",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
 "to_address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063",
 "from_apr": 0.03062862822455939,
 "to_apr": 0.03606936690463246,
 "apr_at_size": 0.03449407845129152,
 "spread_pp": 0.5440738680073067,
 "unconstrained_size_usd": 159202.6778334293,
 "from_available_usd": 87102.77001454454,
 "movable_usd": 87102.77001454454,
 "binding": "low-side withdrawable liquidity",
 "from_supplied_usd": 610788.3686482293,
 "to_supplied_usd": 3854522.064751615,
 "from_utilisation": 0.8573840182036314,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.39%, capacity $87k, no — under $250k movable or under 50bp net at that size

### [info] GHO pays 2.32pp more on base than arbitrum; $64k of it can move (bound by high-side rate dilution), earning 3.37% at size for $187 a year

```json
{
 "asset": "GHO",
 "from": "arbitrum",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0x7dff72693f6a4149b17e7c6314655f6a9f7c8b33",
 "to_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "from_apr": 0.0307103623332137,
 "to_apr": 0.053929161960120146,
 "apr_at_size": 0.03365057087339169,
 "spread_pp": 2.3218799626906446,
 "unconstrained_size_usd": 63557.179735047845,
 "from_available_usd": 116533.6375699164,
 "movable_usd": 63557.179735047845,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 669576.5602786072,
 "to_supplied_usd": 1391257.4663792488,
 "from_utilisation": 0.8261071453641569,
 "rate_source": {
  "from": "head spot (unchecked: 3 updates)",
  "to": "head spot (unchecked: 6 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.29%, capacity $64k, no — under $250k movable or under 50bp net at that size

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
 "to_apr": 0.026424054019705982,
 "apr_at_size": 0.012753531752152839,
 "spread_pp": 2.0980897309165485,
 "unconstrained_size_usd": 13229.458990684248,
 "from_available_usd": 1271387.0056810286,
 "movable_usd": 13229.458990684248,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1897681.1023730903,
 "to_supplied_usd": 24230.015985123362,
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

### [info] FRAX pays 22.51pp more on avalanche than arbitrum; $4k of it can move (bound by high-side rate dilution), earning 1.71% at size for $54 a year

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
 "to_apr": 0.22902135778209803,
 "apr_at_size": 0.017097927089167433,
 "spread_pp": 22.507052010828914,
 "unconstrained_size_usd": 4093.1512927329204,
 "from_available_usd": 122741.4299457148,
 "movable_usd": 4093.1512927329204,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 171466.81644502096,
 "to_supplied_usd": 6547.598322303757,
 "from_utilisation": 0.28427575842743513,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 1.31%, capacity $4k, no — under $250k movable or under 50bp net at that size

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
 "to_apr": 0.026424054019705982,
 "apr_at_size": 0.016577986877402733,
 "spread_pp": 1.648034820813294,
 "unconstrained_size_usd": 7698.214020305328,
 "from_available_usd": 117372.5116902898,
 "movable_usd": 7698.214020305328,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 191107.32540990418,
 "to_supplied_usd": 24230.015985123362,
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

### [info] FRAX pays 20.19pp more on avalanche than ethereum; $230 of it can move (bound by high-side rate dilution), earning 12.47% at size for $22 a year

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
 "to_apr": 0.22902135778209803,
 "apr_at_size": 0.12470036777223292,
 "spread_pp": 20.18823559335564,
 "unconstrained_size_usd": 229.6232708574612,
 "from_available_usd": 9924.463686735166,
 "movable_usd": 229.6232708574612,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 38795.75498214119,
 "to_supplied_usd": 6547.598322303757,
 "from_utilisation": 0.7451003053759371,
 "rate_source": {
  "from": "head spot (unchecked: 0 updates)",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 9.76%, capacity $230, no — under $250k movable or under 50bp net at that size

### [info] USDe pays 1.88pp more on avalanche than ethereum; $2k of it can move (bound by high-side rate dilution), earning 2.43% at size for $16 a year

```json
{
 "asset": "USDe",
 "from": "ethereum",
 "to": "avalanche",
 "from_pool": "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
 "to_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "from_address": "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
 "to_address": "0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34",
 "from_apr": 0.016540375514481773,
 "to_apr": 0.03538365348587987,
 "apr_at_size": 0.02425761510290574,
 "spread_pp": 1.88432779713981,
 "unconstrained_size_usd": 2108.1999560219974,
 "from_available_usd": 411806117.2365097,
 "movable_usd": 2108.1999560219974,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 660960381.0931027,
 "to_supplied_usd": 5874.129897296382,
 "from_utilisation": 0.3769764236763239,
 "rate_source": {
  "from": "window time-weighted",
  "to": "head spot (unchecked: 0 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.77%, capacity $2k, no — under $250k movable or under 50bp net at that size

### [info] GHO pays 0.54pp more on base than avalanche; $1k of it can move (bound by high-side rate dilution), earning 5.12% at size for $3 a year

```json
{
 "asset": "GHO",
 "from": "avalanche",
 "to": "base",
 "from_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
 "to_pool": "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",
 "from_address": "0xfc421ad3c883bf9e7c4f42de845c4e4405799e73",
 "to_address": "0x6bb7a212910682dcfdbd5bcbb3e28fb4e8da10ee",
 "from_apr": 0.04856092740231136,
 "to_apr": 0.053929161960120146,
 "apr_at_size": 0.05124313058082063,
 "spread_pp": 0.5368234557808784,
 "unconstrained_size_usd": 1002.3768069517098,
 "from_available_usd": 104292.38367434165,
 "movable_usd": 1002.3768069517098,
 "binding": "high-side rate dilution",
 "from_supplied_usd": 1089181.869204719,
 "to_supplied_usd": 1391257.4663792488,
 "from_utilisation": 0.9037527815457025,
 "rate_source": {
  "from": "head spot (unchecked: 2 updates)",
  "to": "head spot (unchecked: 6 updates)"
 },
 "capacity_matches_row": true,
 "why": "the same dollar on two chains is one claim on one issuer; the spread is what the lending markets fail to equalise, and it is only worth what can be moved"
}
```

Economics: net APR 0.27%, capacity $1k, no — under $250k movable or under 50bp net at that size

