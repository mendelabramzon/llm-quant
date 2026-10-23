# Ethereum mainnet live scan: 2026-10-23T13:09:47+00:00 to 2026-10-23T15:09:35+00:00 UTC

Blocks 26255531 to 26256129 (599 blocks, 2.00 h), 167,653 transactions, 502,741 logs. Prices at head block 26256177: ETH $2396, BTC $82k. Generated 2026-10-23T15:21:26+00:00 UTC by `scripts/live_scan.py`; the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.

_insights.md not written yet_


---

## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)

Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool's in-range liquidity (2·L·√P); the band APRs scale that by the capital a ±1% or ±0.1% band needs for the same liquidity (×201 and ×2001) and assume the price stays inside the band, so they are gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%.

| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0x2b21…f634 | uni v4 | USDC/USDT | 0.00% | 261 | $15.1M | $115 | $1 | $114 | $25.2B | 0.00% | 0.4% | 1.015% |
| 0x0fb0…3239 | uni v4 | USDC/USDT | 0.00% | 288 | $13.5M | $121 | $2 | $119 | $10.8B | 0.01% | 1.0% | 1.028% |
| [0x4e68…fa36](https://etherscan.io/address/0x4e68ccd3e89f51c3074ca5072bbac773960dfa36) | uni v3 | WETH/USDT | 0.30% | 92 | $6.9M | $21k | $0 | $21k | $1.2B | 7.58% | 1528.1% | 0.970% |
| [0xe055…939f](https://etherscan.io/address/0xe0554a476a092703abdb3ef35c80e0d76d32939f) | uni v3 | USDC/WETH | 0.01% | 1764 | $6.3M | $628 | $0 | $628 | $86.8M | 3.17% | 638.2% | 1.564% |
| [0x88e6…5640](https://etherscan.io/address/0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640) | uni v3 | USDC/WETH | 0.05% | 675 | $6.1M | $3048 | $0 | $3048 | $225.7M | 5.92% | 1191.9% | 1.483% |
| [0x5653…83b2](https://etherscan.io/address/0x56534741cd8b152df6d48adf7ac51f75169a83b2) | uni v3 | WBTC/USDT | 0.05% | 233 | $6.0M | $3014 | $0 | $3014 | $441.3M | 2.99% | 602.7% | 1.075% |
| [0xbafe…8e5d](https://etherscan.io/address/0xbafead7c60ea473758ed6c6021505e8bbd7e8e5d) | uni v3 | AUSD/USDC | 0.01% | 6 | $2.4M | $241 | $0 | $241 | $222.0B | 0.00% | 0.1% | 0.003% |
| 0x50b0…5fa8 | uni v4 | ETH/USDT | 0.35% | 43 | $2.2M | $7570 | $0 | $7570 | $449.6M | 7.37% | 1485.9% | 0.869% |
| 0x9831…3eea | uni v4 | ETH/USDC | 0.02% | 244 | $2.1M | $1153 | $0 | $1153 | $100.0M | 5.05% | 1017.1% | 1.369% |
| [0x8ad5…e6d8](https://etherscan.io/address/0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8) | uni v3 | USDC/WETH | 0.30% | 81 | $2.0M | $6041 | $0 | $6041 | $371.2M | 7.13% | 1436.1% | 0.975% |
| [0x11b8…97f6](https://etherscan.io/address/0x11b815efb8f581194ae79006d24e0d814b7697f6) | uni v3 | WETH/USDT | 0.05% | 418 | $1.9M | $969 | $1 | $968 | $69.6M | 6.09% | 1227.0% | 1.503% |
| [0xccee…363b](https://etherscan.io/address/0xcceef8a17d01e0097bd1ab51687754c86456363b) | uni v3 | WBTC/cirBTC | 0.01% | 10 | $1.9M | $193 | $0 | $193 | $36.4B | 0.00% | 0.5% | 0.020% |
| [0x4585…20c0](https://etherscan.io/address/0x4585fe77225b41b697c938b018e2ac67ac5a20c0) | uni v3 | WBTC/WETH | 0.05% | 120 | $1.8M | $920 | $0 | $920 | $425.7M | 0.95% | 190.7% | 0.416% |
| 0x395f…13a5 | uni v4 | USDC/USDT | 0.00% | 159 | $1.2M | $12 | $0 | $12 | $3.1B | 0.00% | 0.3% | 7.903% |
| 0xe63e…5d45 | uni v4 | PYUSD/USDS | 0.00% | 23 | $1.2M | $7 | $0 | $7 | $149.1B | 0.00% | 0.0% | 0.002% |
| [0xc7bb…0e9b](https://etherscan.io/address/0xc7bbec68d12a0d1830360f8ec58fa599ba1b0e9b) | uni v3 | WETH/USDT | 0.01% | 921 | $1.1M | $109 | $0 | $109 | $14.1M | 3.38% | 681.2% | 1.560% |
| 0x56fc…48c1 | uni v4 | USDe/USDC | 0.00% | 33 | $1.0M | $32 | $1 | $31 | $13.1B | 0.00% | 0.2% | 0.028% |
| [0xba9a…aa31](https://etherscan.io/address/0xba9abfdfb7c28e232d853d85c619e4248971aa31) | uni v3 | WETH/USDT | 0.04% | 142 | $962k | $426 | $0 | $426 | $68.5M | 2.73% | 549.2% | 1.232% |
| 0x5993…615e | uni v4 | ETH/WBTC | 0.06% | 69 | $905k | $566 | $0 | $566 | $296.8M | 0.83% | 168.1% | 0.392% |
| [0xa43f…ec9f](https://etherscan.io/address/0xa43fe16908251ee70ef74718545e4fe6c5ccec9f) | uni v2_like | 0x6982…1933/WETH | ? | 190 | $810k | $2429 | $0 | $2429 | – | – | – | – |
| [0xd661…b0c5](https://etherscan.io/address/0xd661623947ef2ead12d577b47021c167d163b0c5) | uni v3 | USDC/WETH | 0.02% | 248 | $795k | $146 | $0 | $146 | $33.3M | 1.93% | 387.9% | 1.384% |
| [0x0f18…8df6](https://etherscan.io/address/0x0f18d9cddc22c09537b477a9f5269a4832048df6) | uni v2_like | 0x226b…e220/WETH | ? | 4 | $789k | $2366 | $0 | $2366 | – | – | – | – |
| [0x5c2a…2972](https://etherscan.io/address/0x5c2ab69eb2bf12a2f4572d178687bd4660512972) | curve | 0x5086…0c72/sUSDe | ? | 20 | $674k | – | $0 | – | – | – | – | – |
| [0xe6d7…e76a](https://etherscan.io/address/0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a) | uni v3 | USDe/USDC | 0.01% | 9 | $641k | $64 | $0 | $64 | $7.3B | 0.00% | 0.8% | 0.028% |
| [0x94da…2e74](https://etherscan.io/address/0x94da82f51c909ec541bba03a1425d35c43222e74) | uni v3 | USDC/mUSD | 0.00% | 15 | $613k | $1 | $0 | $1 | $35.3B | 0.00% | 0.0% | 0.004% |
| 0xdce6…f78d | uni v4 | ETH/USDC | 0.35% | 37 | $596k | $2085 | $0 | $2085 | $142.5M | 6.41% | 1291.6% | 0.874% |
| 0xeda6…7edb | uni v4 | USDC/USDG | 0.00% | 11 | $527k | $30 | $0 | $30 | $55.5B | 0.00% | 0.1% | 0.001% |
| 0x7233…ca73 | uni v4 | ETH/USDT | 0.06% | 205 | $510k | $319 | $0 | $319 | $25.8M | 5.40% | 1088.1% | 1.453% |
| [0x9db9…425b](https://etherscan.io/address/0x9db9e0e53058c89e5b94e29621a205198648425b) | uni v3 | WBTC/USDT | 0.30% | 25 | $478k | $1434 | $0 | $1434 | $181.8M | 3.46% | 696.4% | 0.553% |
| [0x0b59…6460](https://etherscan.io/address/0x0b599ebf4e05af48b56d38e2dde520570c366460) | uni v3 | WBTC/LBTC | 0.01% | 12 | $477k | $48 | $0 | $48 | $3.8B | 0.01% | 1.1% | 0.013% |
| [0xf2d1…c356](https://etherscan.io/address/0xf2d197f39288416e24ef2a1b4be1af9250b0c356) | uni v3 | 0x385f…1e8d/WETH | 0.01% | 407 | $457k | $46 | $0 | $46 | $75k | 266.32% | 53663.7% | – |
| 0xd52e…5326 | uni v4 | 0x6874…2f38/USDT | 0.06% | 88 | $446k | $279 | $0 | $279 | $78.5M | 1.56% | 313.5% | – |
| [0x941d…503d](https://etherscan.io/address/0x941ddc62f8699f448e86c798e62520550616503d) | uni v3 | WBTC/USDT | 0.04% | 91 | $383k | $157 | $0 | $157 | $40.9M | 1.68% | 339.2% | 0.874% |
| 0x7067…09bb | uni v4 | USDC/cbBTC | 0.35% | 29 | $376k | $1317 | $0 | $1317 | $46.6M | 12.39% | 2496.0% | 1.636% |
| [0x99ac…bc35](https://etherscan.io/address/0x99ac8ca7087fa4a2a1fb6357269965a2014abc35) | uni v3 | WBTC/USDC | 0.30% | 27 | $363k | $1088 | $0 | $1088 | $138.0M | 3.45% | 695.6% | 0.543% |
| [0x1d42…d801](https://etherscan.io/address/0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801) | uni v3 | UNI/WETH | 0.30% | 60 | $357k | $1072 | $0 | $1072 | $52.6M | 8.92% | 1796.9% | 1.408% |
| [0x8d52…95ea](https://etherscan.io/address/0x8d5288b22eaef3084df16159d5491de6140e95ea) | uni v3 | 0x54ce…01f7/WETH | 0.01% | 389 | $342k | $34 | $0 | $34 | $431k | 34.81% | 7015.0% | – |
| [0xd51a…ae46](https://etherscan.io/address/0xd51a44d3fae010294c616388b506acda1bfaae46) | curve | WETH/USDT | ? | 150 | $337k | – | $0 | – | – | – | – | – |
| [0xc3db…ea18](https://etherscan.io/address/0xc3db44adc1fcdfd5671f555236eae49f4a8eea18) | uni v3 | 0x57e1…6061/WETH | 0.30% | 99 | $328k | $985 | $0 | $985 | $17.2M | 25.11% | 5059.3% | – |
| 0x9007…79b3 | uni v4 | ETH/USDT | 0.00% | 477 | $320k | $3 | $0 | $3 | $8.1M | 0.14% | 28.7% | 1.560% |
| 0x7094…e0b7 | uni v4 | ETH/rETH | 0.01% | 5 | $306k | $38 | $0 | $38 | $18.5B | 0.00% | 0.2% | 0.006% |
| 0x21c6…ca27 | uni v4 | ETH/USDC | 0.06% | 208 | $284k | $178 | $0 | $178 | $14.1M | 5.53% | 1114.9% | 1.458% |
| [0x8a7e…66dd](https://etherscan.io/address/0x8a7e585048bda875e64024118c506b14f78166dd) | uni v3 | 0x4580…af78/WETH | 0.30% | 34 | $282k | $847 | $0 | $847 | $68.9M | 5.38% | 1084.6% | – |
| [0x3416…27c6](https://etherscan.io/address/0x3416cf6c708da44db2624d63ea0aaef7113527c6) | uni v3 | USDC/USDT | 0.01% | 116 | $280k | $28 | $1 | $27 | $11.5B | 0.00% | 0.2% | 0.010% |
| 0x2287…1bba | uni v4 | ETH/USDT | 0.01% | 465 | $268k | $34 | $0 | $34 | $4.2M | 3.49% | 703.4% | 4.038% |

Just-in-time liquidity: 17 episodes (mint and burn of identical liquidity inside one block), bracketing $391k of swaps and taking about $19 of fees. Operators:

- [0xae2f…ae13](https://etherscan.io/address/0xae2fc483527b8ef99eb5d9b44875f005ba1fae13): 7 episodes, fees taken $13
- [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4): 4 episodes, fees taken $3
- [0x27c2…2bf2](https://etherscan.io/address/0x27c2a1733f14e1247c5feb1c37cd52ae7d0d2bf2): 2 episodes, fees taken $2
- [0x3437…e4ab](https://etherscan.io/address/0x34373bba18aa058f889c3fc28329c0bfb4b3e4ab): 2 episodes, fees taken $0
- [0xf059…c8ba](https://etherscan.io/address/0xf059ae77c438676e74fb88929145bed00377c8ba): 1 episodes, fees taken $1
- [0xc623…67c2](https://etherscan.io/address/0xc623b0b546bf3031ba88a583a46d5180df8d67c2): 1 episodes, fees taken $0

Swap volume by venue: uniswap_v3 $51.1M (13903), uniswap_v4 $45.0M (8917), uniswap_v2_like $3.2M (4579), curve $2.5M (722), balancer $9876 (76).


Uniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): 0xdb4c…43b1 (0x0000…0000/0xc8fb…8888, 118 swaps); 0x00b9…22d7 (0x0000…0000/0xa0b8…eb48, 71 swaps); 0x909e…6c32 (0x0000…0000/0xe172…f904, 70 swaps); 0xce28…0c2f (0x0000…0000/0xa27e…62d2, 58 swaps); 0x95de…f7b4 (0x0000…0000/0xd96a…5c82, 52 swaps); 0xe44d…ffd5 (0x2d4d…5047/0xa0b8…eb48, 49 swaps); 0x2287…1bba (0x0000…0000/0xdac1…1ec7, 39 swaps); 0x9547…3c2e (0x14d6…47a1/0x9566…1885, 25 swaps); 0xdc3d…1ad1 (0x1223…bca6/0xb10c…1338, 19 swaps); 0x80de…6103 (0x40aa…6aca/0x9566…1885, 18 swaps).


## B. Lending: rates, utilisation, dispersion, health

Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):

| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |
|---|---|---|---|---|---|---|
| Aave v3 | tBTC | 0.00% | 0.26% | 0.1% | $145.1M | $210k |
| Aave v3 | EURC | 2.39% | 4.02% | 65.9% | $44.7M | $29.5M |
| Aave v3 | UNI | 0.00% | 0.19% | 1.2% | $2.8M | $35k |
| Aave v3 | WBTC | 0.00% | 0.31% | 2.0% | $2.8B | $56.5M |
| Aave v3 | GHO | 0.00% | 4.50% | 78.8% | $135.3M | $106.5M |
| Aave v3 | USDe | 0.23% | 6.61% | 4.7% | $256.0M | $11.9M |
| Aave v3 | LINK | 0.01% | 0.51% | 3.3% | $91.1M | $3.0M |
| Aave v3 | LUSD | 0.00% | 6.58% | 25.3% | $1.9M | $475k |
| Aave v3 | DAI | 3.30% | 4.89% | 89.9% | $128.7M | $115.7M |
| Aave v3 | PYUSD | 3.67% | 4.79% | 85.2% | $8.1M | $6.9M |
| Aave v3 | wstETH | 0.00% | 0.02% | 1.5% | $2.3B | $35.0M |
| Aave v3 | AAVE | 0.00% | 0.00% | 0.0% | $121.2M | $0 |
| Aave v3 | LBTC | 0.00% | 0.00% | 0.0% | $219.4M | $1385 |
| Aave v3 | RLUSD | 3.03% | 4.91% | 77.1% | $3.0M | $2.3M |
| Aave v3 | sDAI | 0.00% | 0.00% | 0.0% | $51k | $0 |
| Aave v3 | FRAX | 0.00% | 67.73% | 98.3% | $30k | $29k |
| Aave v3 | sUSDe | 0.00% | 0.00% | 0.0% | $130.5M | $0 |
| Aave v3 | MKR | 0.00% | 0.16% | 1.1% | $208k | $2202 |
| Aave v3 | USDC | 4.07% | 4.80% | 94.2% | $2.4B | $2.2B |
| Aave v3 | rsETH | 0.00% | 0.00% | 0.0% | $795.4M | $2789 |
| Aave v3 | rETH | 0.00% | 0.02% | 0.1% | $95.3M | $114k |
| Aave v3 | cbETH | 0.00% | 0.05% | 0.3% | $15.2M | $50k |
| Aave v3 | ezETH | 0.00% | 0.00% | 0.0% | – | – |
| Aave v3 | WETH | 1.28% | 1.92% | 78.5% | $5.3B | $4.1B |
| Aave v3 | USDtb | 1.80% | 3.35% | 67.0% | $12.6M | $8.4M |
| Aave v3 | ENS | 0.08% | 1.77% | 8.9% | $73k | $6497 |
| Aave v3 | cbBTC | 0.00% | 0.29% | 0.8% | $1.4B | $11.3M |
| Aave v3 | weETH | 0.00% | 1.00% | 0.0% | $3.6B | $135k |
| Aave v3 | CRV | 0.33% | 5.60% | 11.7% | $2.9M | $343k |
| Aave v3 | USDT | 3.32% | 4.25% | 86.9% | $2.9B | $2.5B |
| Aave v3 | USDS | 0.22% | 5.54% | 5.2% | $4.9M | $257k |
| Aave v3 | USDG | 3.04% | 4.88% | 78.0% | $3.6M | $2.8M |
| Aave v3 | crvUSD | 0.67% | 3.03% | 44.1% | $172k | $76k |
| SparkLend | tBTC | 0.00% | 0.00% | 0.0% | $1.7M | $8 |
| SparkLend | WBTC | 0.00% | 0.01% | 0.2% | $185.8M | $341k |
| SparkLend | DAI | 2.84% | 4.43% | 71.3% | $264.5M | $188.7M |
| SparkLend | PYUSD | 0.83% | 4.19% | 21.9% | $100.0M | $21.9M |
| SparkLend | wstETH | 0.00% | 0.00% | 0.0% | $3.4B | $9579 |
| SparkLend | LBTC | 0.00% | 5.00% | 0.0% | $137.0M | $0 |
| SparkLend | RLUSD | 2.32% | 3.94% | 65.6% | $30.0M | $19.7M |
| SparkLend | sDAI | 0.00% | 1.00% | 0.0% | $30k | $0 |
| SparkLend | USDC | 3.55% | 4.36% | 90.4% | $49.5M | $44.8M |
| SparkLend | rsETH | 0.00% | 5.00% | 0.0% | $7474 | $0 |
| SparkLend | sUSDS | 0.00% | 0.00% | 0.0% | $3.3M | $0 |
| SparkLend | rETH | 0.00% | 0.25% | 0.0% | $10.7M | $1969 |
| SparkLend | ezETH | 0.00% | 5.00% | 0.0% | – | – |
| SparkLend | WETH | 1.38% | 1.86% | 78.1% | $1.6B | $1.2B |
| SparkLend | cbBTC | 0.00% | 0.07% | 5.5% | $280.9M | $15.4M |
| SparkLend | weETH | 0.00% | 5.00% | 0.0% | $101.5M | $0 |
| SparkLend | USDT | 3.38% | 3.95% | 95.1% | $320.0M | $304.2M |
| SparkLend | USDS | 2.69% | 4.32% | 69.3% | $1.3B | $892.0M |
| SparkLend | USDG | 0.00% | 3.54% | 0.0% | $1 | $0 |
| Compound v3 USDC | base | 5.49% | 6.53% | 90.7% | $388.3M | $352.2M |
| Compound v3 USDT | base | 5.22% | 6.23% | 90.6% | $160.2M | $145.2M |
| Compound v3 WETH | base | 1.50% | 1.92% | 75.0% | $121.6M | $91.2M |

Sky savings rate (sUSDS) 3.80% APY, DSR (sDAI) – APY; sUSDe vesting implies 5.01% APR on $1.2B of USDe.

Rate curves: Aave v3 AAVE optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 0%; Aave v3 CRV optimal 45%, base 3.00%, slope1 10.00%, slope2 150.00%, reserve factor 50%; Aave v3 DAI optimal 92%, base 0.00%, slope1 5.00%, slope2 35.00%, reserve factor 25%; Aave v3 ENS optimal 45%, base 0.00%, slope1 9.00%, slope2 300.00%, reserve factor 50%; Aave v3 EURC optimal 90%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 10%; Aave v3 FRAX optimal 90%, base 5.00%, slope1 5.50%, slope2 100.00%, reserve factor 100%; Aave v3 GHO optimal 99%, base 4.50%, slope1 0.00%, slope2 0.00%, reserve factor 100%; Aave v3 LBTC optimal 45%, base 0.00%, slope1 4.00%, slope2 300.00%, reserve factor 50%; Aave v3 LINK optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 20%; Aave v3 LUSD optimal 80%, base 5.00%, slope1 5.00%, slope2 100.00%, reserve factor 100%; Aave v3 MKR optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 50%; Aave v3 PYUSD optimal 90%, base 1.00%, slope1 4.00%, slope2 50.00%, reserve factor 10%; Aave v3 RLUSD optimal 80%, base 2.50%, slope1 2.50%, slope2 50.00%, reserve factor 20%; Aave v3 UNI optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 50%; Aave v3 USDC optimal 94%, base 0.00%, slope1 4.50%, slope2 10.00%, reserve factor 10%; Aave v3 USDG optimal 80%, base 0.00%, slope1 5.00%, slope2 30.00%, reserve factor 20%; Aave v3 USDS optimal 92%, base 5.50%, slope1 0.75%, slope2 35.00%, reserve factor 25%; Aave v3 USDT optimal 92%, base 0.00%, slope1 4.50%, slope2 10.00%, reserve factor 10%; Aave v3 USDe optimal 90%, base 6.60%, slope1 0.25%, slope2 12.00%, reserve factor 25%; Aave v3 USDtb optimal 80%, base 0.00%, slope1 4.00%, slope2 50.00%, reserve factor 20%; Aave v3 WBTC optimal 80%, base 0.25%, slope1 2.50%, slope2 300.00%, reserve factor 50%; Aave v3 WETH optimal 92%, base 0.00%, slope1 2.20%, slope2 6.00%, reserve factor 15%; Aave v3 cbBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 cbETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 crvUSD optimal 80%, base 0.00%, slope1 5.50%, slope2 50.00%, reserve factor 50%; Aave v3 ezETH optimal 45%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 15%; Aave v3 rETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 rsETH optimal 45%, base 0.00%, slope1 7.00%, slope2 300.00%, reserve factor 15%; Aave v3 sDAI optimal 90%, base 0.00%, slope1 5.00%, slope2 75.00%, reserve factor 20%; Aave v3 sUSDe optimal 90%, base 0.00%, slope1 0.00%, slope2 0.00%, reserve factor 20%; Aave v3 tBTC optimal 80%, base 0.25%, slope1 4.00%, slope2 60.00%, reserve factor 50%; Aave v3 weETH optimal 30%, base 1.00%, slope1 7.00%, slope2 300.00%, reserve factor 45%; Aave v3 wstETH optimal 80%, base 0.00%, slope1 1.00%, slope2 40.00%, reserve factor 35%.


Rate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):

| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |
|---|---|---|---|---|---|
| Aave v3 | USDC | 131 | 4.50% → 4.80% | 4.50% – 5.00% | 3.80% → 4.07% |
| Aave v3 | USDtb | 3 | 3.32% → 3.35% | 3.32% – 3.37% | 1.76% → 1.80% |
| SparkLend | USDS | 8 | 4.28% → 4.32% | 4.28% – 4.32% | 2.65% → 2.69% |
| Aave v3 | USDT | 140 | 4.28% → 4.25% | 4.25% – 4.28% | 3.36% → 3.32% |
| SparkLend | USDT | 4 | 3.94% → 3.95% | 3.94% – 3.95% | 3.37% → 3.38% |
| Aave v3 | WETH | 99 | 1.92% → 1.92% | 1.91% – 1.92% | 1.28% → 1.28% |
| Aave v3 | EURC | 2 | 4.03% → 4.02% | 4.02% – 4.03% | 2.39% → 2.39% |
| SparkLend | USDC | 3 | 4.36% → 4.36% | 4.36% – 4.36% | 3.55% → 3.55% |
| Aave v3 | WBTC | 22 | 0.31% → 0.31% | 0.31% – 0.31% | 0.00% → 0.00% |
| SparkLend | wstETH | 4 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| SparkLend | WETH | 9 | 1.86% → 1.86% | 1.86% – 1.86% | 1.38% → 1.38% |
| Aave v3 | AAVE | 6 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | wstETH | 6 | 0.02% → 0.02% | 0.02% – 0.02% | 0.00% → 0.00% |
| Aave v3 | GHO | 2 | 4.50% → 4.50% | 4.50% – 4.50% | 0.00% → 0.00% |
| Aave v3 | LINK | 5 | 0.51% → 0.51% | 0.51% – 0.51% | 0.01% → 0.01% |
| Aave v3 | RLUSD | 1 | 4.91% → 4.91% | 4.91% – 4.91% | 3.03% → 3.03% |
| Aave v3 | USDG | 2 | 4.88% → 4.88% | 4.88% – 4.88% | 3.04% → 3.04% |
| SparkLend | WBTC | 1 | 0.01% → 0.01% | 0.01% – 0.01% | 0.00% → 0.00% |
| Aave v3 | tBTC | 1 | 0.26% → 0.26% | 0.26% – 0.26% | 0.00% → 0.00% |
| Aave v3 | weETH | 2 | 1.00% → 1.00% | 1.00% – 1.00% | 0.00% → 0.00% |
| Aave v3 | cbBTC | 5 | 0.29% → 0.29% | 0.29% – 0.29% | 0.00% → 0.00% |
| Aave v3 | 0x6874…2f38 | 4 | 0.00% → 0.00% | 0.00% – 0.00% | 0.00% → 0.00% |
| Aave v3 | USDe | 2 | 6.61% → 6.61% | 6.61% – 6.61% | 0.23% → 0.23% |
| Aave v3 | DAI | 1 | 4.89% → 4.89% | 4.89% – 4.89% | 3.30% → 3.30% |
| SparkLend | weETH | 1 | 5.00% → 5.00% | 5.00% – 5.00% | 0.00% → 0.00% |

Volumes by venue and kind: Aave v3: withdraw $24.5M, borrow $13.3M, repay $26.0M, supply $17.4M, atomic withdraw $234.6M, atomic supply $239.9M; SparkLend: supply $186k, borrow $1865, repay $7.1M, withdraw $10.3M.


Largest operations (≥ $250k):

| block | venue | kind | asset | amount | account | tx |
|---|---|---|---|---|---|---|
| 26256084 | Aave v3 | repay | USDT | $13.0M | [0x31b7…b95a](https://etherscan.io/address/0x31b7d5a2b1ce1871dd642f6aecc0ef68d126b95a) | [0x1ba8…f8dd](https://etherscan.io/tx/0x1ba83ded74a42f15b8fb5a059e80ebf890af85b9c9cc271fdd6f11b0ca8ef8dd) |
| 26255730 | SparkLend | withdraw | USDS | $10.1M | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | [0x7b4c…1b41](https://etherscan.io/tx/0x7b4c1bb64f06250ca3edc8591d0648004cd69c6b50a3b71d3bedc55cc4151b41) |
| 26255722 | SparkLend | repay | USDS | $7.0M | [0xb561…5f60](https://etherscan.io/address/0xb561b1e79e448bc3a7ac4dc377eeecbc99505f60) | [0x92f0…0e0f](https://etherscan.io/tx/0x92f01fb18d31bef9aff7adce55ba10e72b8051835b445f35c31348009e5d0e0f) |
| 26256037 | Aave v3 | repay | USDC | $4.5M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0x1d84…c4cc](https://etherscan.io/tx/0x1d8416d50be154696628ec9aeb46c7a53e20b005c7cece11449393bb713fc4cc) |
| 26256037 | Aave v3 | borrow | USDC | $4.5M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xb35a…ad10](https://etherscan.io/tx/0xb35a9180421ab27f6c0a697857500c3d8641813e1ac74996881709f45386ad10) |
| 26256037 | Aave v3 | supply | USDT | $4.4M | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | [0xb35a…ad10](https://etherscan.io/tx/0xb35a9180421ab27f6c0a697857500c3d8641813e1ac74996881709f45386ad10) |
| 26255773 | Aave v3 | supply | USDT | $3.9M | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | [0x9393…db04](https://etherscan.io/tx/0x93934a8e4de2e91e056266a09ef095c457fe6c72c12888ece8e51f28899cdb04) |
| 26256092 | Aave v3 | withdraw | USDC | $3.6M | [0xaf45…a3b4](https://etherscan.io/address/0xaf4508ee8694a7fae8428d26735154d588caa3b4) | [0x85f2…e4ae](https://etherscan.io/tx/0x85f239e7b836dc1e7928e375af42fb015ebd5941d656f44fde183f7d008be4ae) |
| 26256047 | Aave v3 | withdraw | USDT | $2.0M | [0xaf45…a3b4](https://etherscan.io/address/0xaf4508ee8694a7fae8428d26735154d588caa3b4) | [0x4c90…44a7](https://etherscan.io/tx/0x4c907ddcb8ce622a44881cd3ee4f721322703a402f1473bebaaba5c3721144a7) |
| 26255687 | Aave v3 | supply | wstETH | $1.2M | [0x8921…a973](https://etherscan.io/address/0x89216ade9e9c5e4200ad318a43972087a544a973) | [0xa191…3633](https://etherscan.io/tx/0xa191bfd85c917a97138ada345966c140d9d4ff1318a6169853fc83474c7c3633) |
| 26255572 | Aave v3 | withdraw | USDC | $885k | [0xf5ca…4184](https://etherscan.io/address/0xf5ca9dcbabecdd95a5b7b091a2a70b81ddfa4184) | [0x5199…d39c](https://etherscan.io/tx/0x5199b8515230afc1145972e23a2ec79e9f2eebc3bc58494e68693011d103d39c) |
| 26255592 | Aave v3 | withdraw | WETH | $599k | [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) | [0xaf53…eb7e](https://etherscan.io/tx/0xaf53343b13e3739b761af6ce58abf34248158e91914168b8c32d4f8b5da2eb7e) |
| 26255674 | Aave v3 | withdraw | USDT | $399k | [0x8e57…3307](https://etherscan.io/address/0x8e57e5e769f9d8b5c211117eb8cfc2e3f29c3307) | [0x6c4b…5d9b](https://etherscan.io/tx/0x6c4b5573de0c583e6ca4134b40617e9a5aa829b85fc164b5df972c9fefcd5d9b) |
| 26255698 | Aave v3 | borrow | USDT | $399k | [0x8921…a973](https://etherscan.io/address/0x89216ade9e9c5e4200ad318a43972087a544a973) | [0xe10b…fcfe](https://etherscan.io/tx/0xe10be02adc82f6481d1f5a8f725f4ed6f82b853690db9ab51a02650e729dfcfe) |
| 26255785 | Aave v3 | supply | WETH | $349k | [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) | [0xfee4…fc9b](https://etherscan.io/tx/0xfee46492dec93465e9e7d9ffcfbca4c1844711b690771b064335354e7b8dfc9b) |
| 26255785 | Aave v3 | withdraw | WETH | $349k | [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) | [0x5272…9e69](https://etherscan.io/tx/0x52728e7113b28df57e062d767f69fb8bd94bfd2f866e05d1c17f391752859e69) |
| 26255785 | Aave v3 | repay | USDT | $280k | [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) | [0x5272…9e69](https://etherscan.io/tx/0x52728e7113b28df57e062d767f69fb8bd94bfd2f866e05d1c17f391752859e69) |
| 26255996 | Aave v3 | withdraw | USDC | $260k | [0x09bb…414c](https://etherscan.io/address/0x09bbf4c01906cc3d30b20c6507213142ad6d414c) | [0xac81…4924](https://etherscan.io/tx/0xac81f32a61f6114b88479ffc0259f39f11e9781e32f421c09abfc5b231124924) |
| 26256113 | Aave v3 | repay | USDT | $254k | [0xe71c…264d](https://etherscan.io/address/0xe71cbf47fff309813bcea54f3ecf49a5f129264d) | [0x9fb2…fa6c](https://etherscan.io/tx/0x9fb2b9909247b4400a70e0fa1747b2f67c6061debcdd6b576b040b99de8efa6c) |

Where borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):

- SparkLend withdraw $10.1M USDS by [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) ([0x7b4c…1b41](https://etherscan.io/tx/0x7b4c1bb64f06250ca3edc8591d0648004cd69c6b50a3b71d3bedc55cc4151b41)): $10.1M → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $139k → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $240k → [AllocatorBuffer (blockscout-verified)](https://etherscan.io/address/0xc395d150e71378b47a1b8e9de0c1a83b75a08324); $1.0M → [DaiUsds (blockscout-verified)](https://etherscan.io/address/0x3225737a9bbb6473cb4a45b7244aca2befdb276a)
- Aave v3 borrow $4.5M USDC by [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) ([0xb35a…ad10](https://etherscan.io/tx/0xb35a9180421ab27f6c0a697857500c3d8641813e1ac74996881709f45386ad10)): $4.5M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $4.5M → [Aave v3 aEthUSDC — the reserve's aToken; symbol() read on chain (chain-read)](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c); $2.8M → [Uniswap v4 PoolManager (known-canonical)](https://etherscan.io/address/0x000000000004444c5dc75cb358380d2e3de08a90); $2.8M → [Aave v3 aEthUSDC — the reserve's aToken; symbol() read on chain (chain-read)](https://etherscan.io/address/0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c)
- Aave v3 withdraw $3.6M USDC by [0xaf45…a3b4](https://etherscan.io/address/0xaf4508ee8694a7fae8428d26735154d588caa3b4) ([0x85f2…e4ae](https://etherscan.io/tx/0x85f239e7b836dc1e7928e375af42fb015ebd5941d656f44fde183f7d008be4ae)): $3.6M → [0xfc5c…8570](https://etherscan.io/address/0xfc5c08b98d92ad46c7e63f7b4f3da6c60ad08570)
- Aave v3 withdraw $2.0M USDT by [0xaf45…a3b4](https://etherscan.io/address/0xaf4508ee8694a7fae8428d26735154d588caa3b4) ([0x4c90…44a7](https://etherscan.io/tx/0x4c907ddcb8ce622a44881cd3ee4f721322703a402f1473bebaaba5c3721144a7)): $2.0M → [0xa445…4753](https://etherscan.io/address/0xa445f5c32c5e2e0b9af054d902466d6501074753)
- Aave v3 withdraw $885k USDC by [0xf5ca…4184](https://etherscan.io/address/0xf5ca9dcbabecdd95a5b7b091a2a70b81ddfa4184) ([0x5199…d39c](https://etherscan.io/tx/0x5199b8515230afc1145972e23a2ec79e9f2eebc3bc58494e68693011d103d39c)): $885k → [0x3902…b160](https://etherscan.io/address/0x39024e164c28a252e9130c360a9bc0f4e821b160)
- Aave v3 withdraw $599k WETH by [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) ([0xaf53…eb7e](https://etherscan.io/tx/0xaf53343b13e3739b761af6ce58abf34248158e91914168b8c32d4f8b5da2eb7e)): $31k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8)
- Aave v3 withdraw $399k USDT by [0x8e57…3307](https://etherscan.io/address/0x8e57e5e769f9d8b5c211117eb8cfc2e3f29c3307) ([0x6c4b…5d9b](https://etherscan.io/tx/0x6c4b5573de0c583e6ca4134b40617e9a5aa829b85fc164b5df972c9fefcd5d9b)): $399k → [0xd10a…6d69](https://etherscan.io/address/0xd10a6c36aeff21387f3b55fd8f19788a6d016d69) → forwarded to hot wallet (day study, unidentified) (model-memory) **[to exchange $399k]**
- Aave v3 withdraw $349k WETH by [0x5aae…5588](https://etherscan.io/address/0x5aae4d2f360e156de3416936049837a7bb685588) ([0x5272…9e69](https://etherscan.io/tx/0x52728e7113b28df57e062d767f69fb8bd94bfd2f866e05d1c17f391752859e69)): $349k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $349k → [0x45e9…9215](https://etherscan.io/address/0x45e9b04942176a513b22acc1ced75c34d2fd9215); $280k → [Aave v3 WETH (blockscout-verified)](https://etherscan.io/address/0x4d5f47fa6a74757f35c14fd3a6ef8e3c9bc514e8); $280k → [0x45e9…9215](https://etherscan.io/address/0x45e9b04942176a513b22acc1ced75c34d2fd9215)

Health of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):

| venue | account | collateral | debt | health factor | drop to liquidation |
|---|---|---|---|---|---|
| SparkLend | [0xb561…5f60](https://etherscan.io/address/0xb561b1e79e448bc3a7ac4dc377eeecbc99505f60) | $64.6M | $25.2M | 2.105 | 52.5% |
| Aave v3 | [0x31b7…b95a](https://etherscan.io/address/0x31b7d5a2b1ce1871dd642f6aecc0ef68d126b95a) | $18.3M | $3.2M | 5.187 | 80.7% |
| Aave v3 | [0x8921…a973](https://etherscan.io/address/0x89216ade9e9c5e4200ad318a43972087a544a973) | $1.2M | $399k | 2.438 | 59.0% |
| SparkLend | [0x1601…347e](https://etherscan.io/address/0x1601843c5e9bc251a3272907010afa41fa18347e) | $51.2M | $0 | ∞ | – |
| Aave v3 | [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a) | $0 | $0 | ∞ | – |
| Aave v3 | [0xed0c…4312](https://etherscan.io/address/0xed0c6079229e2d407672a117c22b62064f4a4312) | $93.0M | $0 | ∞ | – |
| Aave v3 | [0xaf45…a3b4](https://etherscan.io/address/0xaf4508ee8694a7fae8428d26735154d588caa3b4) | $0 | $0 | ∞ | – |
| Aave v3 | [0xf5ca…4184](https://etherscan.io/address/0xf5ca9dcbabecdd95a5b7b091a2a70b81ddfa4184) | $0 | $0 | ∞ | – |
| Aave v3 | [0xd016…5722](https://etherscan.io/address/0xd01607c3c5ecaba394d8be377a08590149325722) | $0 | $0 | ∞ | – |
| Aave v3 | [0x77ce…97ff](https://etherscan.io/address/0x77ce206c6c50e569d55a326163235069207897ff) | $1 | $0 | ∞ | – |

Liquidations: Morpho Blue [0x8775…7dae](https://etherscan.io/address/0x877554d4a9bba867d1aceed61547acab59db7dae) debt $18, collateral – ([0x719b…00cd](https://etherscan.io/tx/0x719b010be1dd7e963f8317193ae705420137a950ad5d972a1c1ac72ec4bb00cd)); Aave v3 [0x77ce…97ff](https://etherscan.io/address/0x77ce206c6c50e569d55a326163235069207897ff) debt $6, collateral $6 ([0xe41e…1991](https://etherscan.io/tx/0xe41edb4c1e580ee03862d2dd6dfb3821736cf6f6b6ebf9d66cdf63e5f2b61991)).


Flash loans (events): BalFlash 51 ($11.5M), MorphoFlash 1 ($0).


Atomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):

- Aave v3 account [0x76f3…5b1a](https://etherscan.io/address/0x76f30e3f75437fb862b8d2c4d80a671bceba5b1a): 6 transactions, largest leg $40.0M, gross $234.6M; legs: WETH withdraw $234.6M, USDT withdraw $0

## C. Stablecoin and LST implied prices versus NAV or par

Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.

| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |
|---|---|---|---|---|---|---|
| USDT | 617 | $30.4M | 0.998735 | 0.998656 – 0.998839 | 0.998621 | +1.1 bps |
| AUSD | 8 | $2.4M | 0.999758 | 0.999553 – 0.999911 | 1 | -2.4 bps |
| cirBTC | 272 | $2.3M | 81686.5 | 81266.7 – 81829.5 | – | – |
| USDe | 45 | $1.7M | 0.999833 | 0.99969 – 0.999892 | 1 | -1.7 bps |
| USDG | 13 | $662k | 0.999895 | 0.999858 – 0.999967 | 1 | -1.0 bps |
| USDS | 34 | $658k | 0.99984 | 0.999617 – 1.00002 | 1 | -1.6 bps |
| PYUSD | 9 | $655k | 1.00014 | 0.999154 – 1.00018 | 1 | +1.4 bps |
| mUSD | 10 | $613k | 0.999858 | 0.999836 – 0.999874 | – | – |
| sUSDe | 16 | $358k | 1.25413 | 1.25396 – 1.25421 | 1.25447 | -2.7 bps |
| TSLAon | 46 | $262k | 369.502 | 366.678 – 374.211 | – | – |
| PANGEA | 179 | $230k | 0.0017078 | 0.00116292 – 0.00212978 | – | – |
| AZTEC | 75 | $220k | 0.0169518 | 0.016783 – 0.0171357 | – | – |
| crvUSD | 32 | $213k | 0.998781 | 0.998491 – 0.998857 | 1 | -12.2 bps |
| wstETH | 19 | $206k | 2987.45 | 2987.03 – 2987.91 | 2987.64 | -0.6 bps |
| DAI | 40 | $189k | 0.999781 | 0.999626 – 0.999852 | 0.999784 | -0.0 bps |
| SPCXon | 66 | $136k | 147.079 | 145.845 – 148.721 | – | – |
| SKY | 73 | $124k | 0.0723104 | 0.0719038 – 0.0727579 | – | – |
| IMD | 42 | $121k | 5.0001 | 4.76063 – 5.08576 | – | – |
| frxUSD | 20 | $118k | 1.0001 | 0.999694 – 1.00003 | 1 | +1.0 bps |
| RAIL | 63 | $113k | 2.60418 | 2.58355 – 2.6438 | – | – |
| LIT | 98 | $106k | 3.35575 | 3.31222 – 3.39545 | – | – |
| FOLD | 58 | $90k | 0.0509891 | 0.0498652 – 0.052213 | – | – |
| NEAR | 68 | $82k | 4.89837 | 4.8393 – 4.96195 | – | – |
| RLUSD | 5 | $82k | 1.0001 | 0.999829 – 1.00016 | 1 | +1.0 bps |
| ADI | 78 | $63k | 8.00266 | 7.99615 – 8.00908 | – | – |
| evmbot | 47 | $50k | 0.000201087 | 0.000154486 – 0.000246222 | – | – |

## D. Exchange flow, large transfers, round trips, scheduled flow

Net flow into tagged exchange wallets and deposit sinks by asset (address book: 194 addresses; tags are behavioural from the day study plus memory labels):

| asset | in | out | net |
|---|---|---|---|
| USDC | $969.5M | $910.7M | $58.7M |
| USDT | $258.2M | $253.3M | $5.0M |
| ETH | $65.2M | $33.5M | $31.7M |
| cbBTC | $10.2M | $13.0M | $-2.8M |
| RLUSD | $4.0M | $8.5M | $-4.5M |
| UNI | $3.0M | $3.5M | $-566k |
| USD1 | $1.0M | $3.1M | $-2.1M |
| WBTC | $405k | $1.2M | $-766k |
| AAVE | $565k | $898k | $-333k |
| USDG | $406k | $608k | $-201k |
| LINK | $440k | $449k | $-8727 |
| EURC | $360k | $360k | $762 |

By label: Coinbase 11 (model-memory) in $460.3M / out $485.1M; Coinbase 10 (model-memory) in $472.6M / out $406.2M; Bitfinex 2 (model-memory) in $136.4M / out $72.8M; hot wallet (behaviour, day study) in $73.6M / out $74.7M; Binance 14 (model-memory) in $126.5M / out $19.4M; hot wallet (day study, unidentified) (model-memory) in $30.9M / out $70.1M; Binance 15 (model-memory) in $0 / out $33.6M; Binance 17 (model-memory) in $0 / out $25.3M; Binance 18 (model-memory) in $0 / out $19.8M; Binance 16 (model-memory) in $0 / out $11.6M; Gemini 4 (model-memory) in $4.1M / out $4.3M; Gate.io (model-memory) in $6.2M / out $1.4M.


Largest transfers (≥ $5M, ERC-20 and native):

| block | asset | amount | from | to | tx |
|---|---|---|---|---|---|
| 26255847 | cbBTC | $790.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x4147…6bca](https://etherscan.io/tx/0x41476f67d5d7f55d4b0efc28a36afe6806f6e4d8b59b39b120b3be8ca5ae6bca) |
| 26255847 | cbBTC | $790.1M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x4147…6bca](https://etherscan.io/tx/0x41476f67d5d7f55d4b0efc28a36afe6806f6e4d8b59b39b120b3be8ca5ae6bca) |
| 26255560 | USDC | $130.6M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xdce7…19a9](https://etherscan.io/tx/0xdce71085c6b4100f4f4f58062d507b7dca3666668cf13630b78f9e67882f19a9) |
| 26255560 | USDC | $130.6M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xdce7…19a9](https://etherscan.io/tx/0xdce71085c6b4100f4f4f58062d507b7dca3666668cf13630b78f9e67882f19a9) |
| 26256014 | USDC | $128.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xcbe6…4177](https://etherscan.io/tx/0xcbe689fb79998db7258a3d2bbf1ad66e3c2ca5715ad7751c22b6cb5659d74177) |
| 26256014 | USDC | $128.8M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xcbe6…4177](https://etherscan.io/tx/0xcbe689fb79998db7258a3d2bbf1ad66e3c2ca5715ad7751c22b6cb5659d74177) |
| 26255666 | USDC | $128.8M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x8b43…7603](https://etherscan.io/tx/0x8b438efae0d30b2683ab2d868a74a652c951178c81ba4d8218bbf727b7ec7603) |
| 26255666 | USDC | $128.8M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8b43…7603](https://etherscan.io/tx/0x8b438efae0d30b2683ab2d868a74a652c951178c81ba4d8218bbf727b7ec7603) |
| 26255954 | USDC | $128.5M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x9c44…d7fb](https://etherscan.io/tx/0x9c4406b5f8580208e6c899c4258fd14a0ef1479fba00f96492b49273a269d7fb) |
| 26255954 | USDC | $128.5M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x9c44…d7fb](https://etherscan.io/tx/0x9c4406b5f8580208e6c899c4258fd14a0ef1479fba00f96492b49273a269d7fb) |
| 26255963 | USDC | $128.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xccf6…bba4](https://etherscan.io/tx/0xccf60a8400c7af232aa5756effc6b296bb15cc0cb5dfcd8dd40b4b0c76adbba4) |
| 26255963 | USDC | $128.4M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xccf6…bba4](https://etherscan.io/tx/0xccf60a8400c7af232aa5756effc6b296bb15cc0cb5dfcd8dd40b4b0c76adbba4) |
| 26255763 | USDC | $128.4M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0x9cd5…e5f2](https://etherscan.io/tx/0x9cd5d698e8172e4d3dbc4f6037b2ef779c58608a21457fc70f55b92feab6e5f2) |
| 26255763 | USDC | $128.4M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x9cd5…e5f2](https://etherscan.io/tx/0x9cd5d698e8172e4d3dbc4f6037b2ef779c58608a21457fc70f55b92feab6e5f2) |
| 26255848 | USDC | $128.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xabbb…9492](https://etherscan.io/tx/0xabbbdaa52bacc12478092f73c2f7629e780b8816abadb4ffbb6672a123fa9492) |
| 26255848 | USDC | $128.1M | [0xd1c6…c7eb](https://etherscan.io/address/0xd1c6aca7ea7ed44e1873dafa054c28ceb690c7eb) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xabbb…9492](https://etherscan.io/tx/0xabbbdaa52bacc12478092f73c2f7629e780b8816abadb4ffbb6672a123fa9492) |
| 26255834 | USDT | $124.4M | [0xc712…b9e6](https://etherscan.io/address/0xc7128596e0cbfe72776eedbd306237baf34db9e6) | [0x1897…754a](https://etherscan.io/address/0x189736e4ef463f00ad33840fba682f810933754a) | [0x94e6…0970](https://etherscan.io/tx/0x94e64d2cdb0dd4d95ae8feecc2059deba7d68adb1c26cd9fc7137d760c9c0970) |
| 26255836 | USDT | $124.4M | [0x1897…754a](https://etherscan.io/address/0x189736e4ef463f00ad33840fba682f810933754a) | [0x7713…35ec](https://etherscan.io/address/0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec) | [0x179c…6d53](https://etherscan.io/tx/0x179cf83dd390bf139405681194d70434e5402561d26bbe4a886c1ee596ec6d53) |
| 26255607 | USDC | $116.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x276f…4e27](https://etherscan.io/tx/0x276fd039629fc2fd8c0d92063fcb5f7ef4c830375d6573f91982ac24cd5b4e27) |
| 26255607 | USDC | $116.9M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x276f…4e27](https://etherscan.io/tx/0x276fd039629fc2fd8c0d92063fcb5f7ef4c830375d6573f91982ac24cd5b4e27) |
| 26255959 | USDC | $115.6M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0x8eb8…c948](https://etherscan.io/tx/0x8eb829acd4131c9df12fbac5c33b700c8155f43cbadcb43b84c1ed6cba2cc948) |
| 26255959 | USDC | $115.6M | [0x06cf…f5ef](https://etherscan.io/address/0x06cff7088619c7178f5e14f0b119458d08d2f5ef) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x8eb8…c948](https://etherscan.io/tx/0x8eb829acd4131c9df12fbac5c33b700c8155f43cbadcb43b84c1ed6cba2cc948) |
| 26255866 | USDC | $115.1M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xad35…0732](https://etherscan.io/tx/0xad35ca97a6769d0884493dac7c0f4b5fe1ef8be7adff4ef1f7fb4edefb8c0732) |
| 26255866 | USDC | $115.1M | [0xd226…9f89](https://etherscan.io/address/0xd226997439ecfbeff8e110c8c78c8a7eefd19f89) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0xad35…0732](https://etherscan.io/tx/0xad35ca97a6769d0884493dac7c0f4b5fe1ef8be7adff4ef1f7fb4edefb8c0732) |
| 26255895 | WBTC | $109.9M | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0x00ac…5565](https://etherscan.io/address/0x00acd5005200e7009beb000000e35e1e002b5565) | [0x982f…639d](https://etherscan.io/tx/0x982f3755ac913f5bac20b6ae8d922c383d8ba924a7155d30f8d842e69475639d) |
| 26255895 | WBTC | $109.9M | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x00ac…5565](https://etherscan.io/address/0x00acd5005200e7009beb000000e35e1e002b5565) | [0x982f…639d](https://etherscan.io/tx/0x982f3755ac913f5bac20b6ae8d922c383d8ba924a7155d30f8d842e69475639d) |
| 26255895 | WBTC | $109.9M | [0x00ac…5565](https://etherscan.io/address/0x00acd5005200e7009beb000000e35e1e002b5565) | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x982f…639d](https://etherscan.io/tx/0x982f3755ac913f5bac20b6ae8d922c383d8ba924a7155d30f8d842e69475639d) |
| 26255895 | WBTC | $109.9M | [0xb40d…ec54](https://etherscan.io/address/0xb40dc920dfc7bd7d68322a0e1b8a05557adbec54) | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0x982f…639d](https://etherscan.io/tx/0x982f3755ac913f5bac20b6ae8d922c383d8ba924a7155d30f8d842e69475639d) |
| 26255895 | WBTC | $109.9M | [0x00ac…5565](https://etherscan.io/address/0x00acd5005200e7009beb000000e35e1e002b5565) | [0xbbbb…ffcb](https://etherscan.io/address/0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb) | [0x982f…639d](https://etherscan.io/tx/0x982f3755ac913f5bac20b6ae8d922c383d8ba924a7155d30f8d842e69475639d) |
| 26255596 | WBTC | $109.4M | [0x6cbe…b30c](https://etherscan.io/address/0x6cbe98eb2cdf0bc2e52a9b3ed014cd1740a4b30c) | [0xa0f1…75ea](https://etherscan.io/address/0xa0f1c3ad83e07d97b5e7030e177718be175275ea) | [0x7e7f…a192](https://etherscan.io/tx/0x7e7f2460688a071d186f7e530c067e776e50c4a4fa8872ce229e087d6a82a192) |

Round trips (≥ $10M out and back within the window): $50.0M USDC from [0x55fe…44b8](https://etherscan.io/address/0x55fe002aeff02f77364de339a1292923a15844b8) via [0x0000…0000](https://etherscan.io/address/0x0000000000000000000000000000000000000000), back after 92 min.


Scheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):

| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |
|---|---|---|---|---|---|---|---|---|
| [0xbec8…386d](https://etherscan.io/address/0xbec8607f49f6e98d0fad6916a9c9b6900d23386d) | USDC → USDT | 8 | $473k | $60k | 24s | 0.00 | 0.43 | uniswap_v4 8 |
| [0x6ba9…af5b](https://etherscan.io/address/0x6ba9d1efa3868a65c24c48eb6f76b02c8bfeaf5b) | WETH → USDC | 4 | $103k | $23k | 216s | 0.15 | 0.24 | uniswap_v3 4 |
| [0x6ba9…af5b](https://etherscan.io/address/0x6ba9d1efa3868a65c24c48eb6f76b02c8bfeaf5b) | USDC → USDT | 4 | $103k | $23k | 216s | 0.15 | 0.24 | uniswap_v4 4 |
| [0xb36c…56ce](https://etherscan.io/address/0xb36ce3f521a1ff4b0cffb82ddd71f0a51fcf56ce) | WETH → USDC | 4 | $108k | $26k | 1656s | 0.29 | 0.18 | uniswap_v3 4 |
| [0x7f86…a8e3](https://etherscan.io/address/0x7f86d8b6ac42503646c3ecb9ca4940332627a8e3) | 0x5086…0c72 → sUSDe | 5 | $324k | $64k | 24s | 0.47 | 0.14 | curve 5 |
| [0x9cf2…6195](https://etherscan.io/address/0x9cf2b94caba0ab5ea0709c9aaa68716908236195) | USDT → sUSDe | 8 | $266k | $32k | 24s | 0.53 | 0.14 | uniswap_v4 8 |
| [0xc8df…ebfe](https://etherscan.io/address/0xc8df1a5953aa7f62a35ff1501e0c10eb3c33ebfe) | USDC → WETH | 4 | $178k | $44k | 1956s | 0.47 | 0.39 | uniswap_v3 4 |
| [0x5b43…efd1](https://etherscan.io/address/0x5b43453fce04b92e190f391a83136bfbecedefd1) | USDC → ETH | 6 | $214k | $35k | 1128s | 0.51 | 0.38 | uniswap_v4 6 |
| [0x9cf2…6195](https://etherscan.io/address/0x9cf2b94caba0ab5ea0709c9aaa68716908236195) | sUSDe → 0x5086…0c72 | 6 | $288k | $43k | 24s | 0.53 | 0.39 | curve 6 |

Largest swaps (≥ $1M):

| block | venue | sells → buys | size | sender | tx |
|---|---|---|---|---|---|
| 26256037 | uniswap_v4 | USDC → USDT | $4.5M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xb35a…ad10](https://etherscan.io/tx/0xb35a9180421ab27f6c0a697857500c3d8641813e1ac74996881709f45386ad10) |
| 26256037 | uniswap_v4 | USDT → USDC | $4.4M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x1d84…c4cc](https://etherscan.io/tx/0x1d8416d50be154696628ec9aeb46c7a53e20b005c7cece11449393bb713fc4cc) |
| 26256098 | uniswap_v4 | USDC → USDT | $2.8M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x3c49…e005](https://etherscan.io/tx/0x3c4998e7206ef295963c6d1ed36b5849f447b748d4ed9b98265f3f1b8c0ae005) |
| 26256106 | uniswap_v4 | USDC → USDT | $2.7M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0x2de6…4233](https://etherscan.io/tx/0x2de613f7364a7f0c58b7190117c5f185c5393ad2c627c39841dd8dac3d244233) |
| 26256098 | uniswap_v4 | USDT → USDC | $2.7M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xe7ff…4009](https://etherscan.io/tx/0xe7fff50fb5072b557fb17781c009283d095d7de9f4be5e87f5d518b9832b4009) |
| 26256106 | uniswap_v4 | USDT → USDC | $2.6M | [0x654f…4be4](https://etherscan.io/address/0x654fae4aa229d104cabead47e56703f58b174be4) | [0xc0f7…37f0](https://etherscan.io/tx/0xc0f76e79ce9ceb6e7099e40d5f7bc323f0c1ea7450af480ff6752081832d37f0) |
| 26255840 | uniswap_v3 | 0x72df…075e → WBTC | $1.8M | [0xbee3…ccca](https://etherscan.io/address/0xbee355e5a9b1c5359796cf907138448b27f0ccca) | [0x62d7…77d8](https://etherscan.io/tx/0x62d744ea178c7bd04169e1ef7d310c2a52766b3b25f0378988d14705423877d8) |
| 26255817 | uniswap_v3 | USDT → 0x2a05…89df | $1.4M | [0x4337…c62f](https://etherscan.io/address/0x4337017d2e3f5e4160a27f6fdbdc38719343c62f) | [0xe86e…57e4](https://etherscan.io/tx/0xe86ef0455d2fa8d360297cd43316002ea5b626c82bcdeff301e22e4e46cd57e4) |
| 26256098 | uniswap_v3 | AUSD → USDC | $1.4M | [0xdd92…edfa](https://etherscan.io/address/0xdd922c841d85e12dac2dc2eef5a5e29cfff6edfa) | [0xeb5e…c5ae](https://etherscan.io/tx/0xeb5e85e76f00a7a84dfe4d2d6aab146a769785b3d80307c67dde14c79f36c5ae) |

## E. Bridges, issuance, staking

Outbound: $25.6M in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints $41.5M (388).

| kind | token | destination | n | amount | top recipient |
|---|---|---|---|---|---|
| OFT | USDe | eid 30383 | 1 | $8.3M | – |
| CCTP | USDC | Aptos | 4 | $3.6M | 64c815fa7c79a1… $3.6M |
| CCTP | USDC | Avalanche | 10 | $2.2M | 0x65c340eb0688… $1.6M |
| OFT | USDT | eid 30420 | 17 | $2.1M | – |
| CCTP | USDC | domain 26 | 11 | $1.8M | 0x424a31a57f7c… $1.0M |
| CCTP | USDC | Base | 53 | $1.3M | 0x3f42f688c7b3… $392k |
| OFT | USDG | Arbitrum | 5 | $1.3M | – |
| OFT | USDe | eid 30416 | 1 | $1000k | – |
| CCTP | USDC | domain 15 | 5 | $572k | 0x0551fa03e31b… $350k |
| CCTP | USDC | Solana | 20 | $489k | de57b1ae937424… $287k |
| OFT | AUSD | eid 30390 | 1 | $400k | – |
| OFT | USDT | eid 30383 | 2 | $379k | – |
| OFT | USDe | Avalanche | 3 | $338k | – |
| CCTP | USDC | OP Mainnet | 23 | $325k | 0x3a6a72459518… $197k |
| OFT | USDT | Polygon | 4 | $253k | – |
| CCTP | USDC | Arbitrum | 15 | $242k | 0xc435249d0e83… $109k |
| OFT | USDT | eid 30465 | 2 | $236k | – |
| CCTP | USDC | domain 19 | 28 | $170k | 0xe7842c1205a2… $64k |
| CCTP | USDC | Polygon | 8 | $161k | 0x1da38a31f369… $110k |
| OFT | USDG | eid 30416 | 3 | $135k | – |

Issuance totals: USDC burn $250.5M (231); USDC mint $209.3M (662). Largest: USDC burn $54.5M ([0xc2d8…6878](https://etherscan.io/tx/0xc2d874cf3453fc9c254b0bc59f4daf4490dcd187120b30ccfc6e9d68e69c6878)); USDC burn $50.0M ([0x8e5c…cf78](https://etherscan.io/tx/0x8e5c6a74221f2dd90ffca32b7ba7af2638652523c4d53a2f71698cd21c1dcf78)); USDC burn $50.0M ([0x3351…44b7](https://etherscan.io/tx/0x3351704c2cbc359e9d752b210d7f4476408534493c53873475651c63f04644b7)); USDC burn $50.0M ([0x9002…34d9](https://etherscan.io/tx/0x90026b92343f5f08ff9ca2080f8f4a44bb24ce27c51dd13f37269259767f34d9)); USDC mint $50.0M ([0x8acc…f988](https://etherscan.io/tx/0x8acc0522451efa7181c53c35136d1aecc2a5d94a58a3c5928d460d23493df988)).


WETH wrapped 7144 ETH, unwrapped 8470 ETH; Lido staked 841.8 ETH, withdrawal requests 275.3 ETH; sUSDe cooldowns 0 for $0.


## F. Gas market and block production

Base fee 0.102 → 0.186 gwei (min 0.102, median 0.205, max 0.4); blocks 51% full; median tip 0.102 gwei; 2.8% of transactions pay zero tip; builders: Titan (titanbuilder.xyz) 311, BuilderNet 127,  Quasar (quasar.win)  48, Eureka (eurekabuilder.xyz) 44, Builder+ www.btcs.com/builder 9, gethgo1.27.1linux 7.


Most active senders: [Binance 14 (model-memory)](https://etherscan.io/address/0x28c6c06298d514db089934071355e5743bf21d60) 1522, [Binance 15 (model-memory)](https://etherscan.io/address/0x21a31ee1afc51d94c2efccaa2092ad1028285549) 1109, [Binance 16 (model-memory)](https://etherscan.io/address/0xdfd5293d8e347dfe59e90efd55b2956a1343963d) 946, [0x6cdb…e313](https://etherscan.io/address/0x6cdb7776f6a20b9ed4441b791e9541a6fc04e313) 880, [Binance 17 (model-memory)](https://etherscan.io/address/0x56eddb7aa87536c09ccc2793473599fd21a8b17f) 832, [Binance 18 (model-memory)](https://etherscan.io/address/0x9696f59e4d72e237be84ffd425dcad154bf96976) 773, [hot wallet (behaviour, day study)](https://etherscan.io/address/0xf30ba13e4b04ce5dc4d254ae5fa95477800f0eb0) 653, [hot wallet (behaviour, day study)](https://etherscan.io/address/0x6872b6630a3afcd3117191a8403c2002e13df7de) 634, [0xbb2f…37e0](https://etherscan.io/address/0xbb2f33f73ccc2c74e3fb9bb8eb75241ac15337e0) 611, [hot wallet (day study, unidentified) (model-memory)](https://etherscan.io/address/0x05ff6964d21e5dae3b1010d5ae0465b3c450f381) 609.


Intent fills: CoWTrade 471, OneInchFilled 476, UniXFill 148. Unknown event topics: 30 distinct in the top list; unpriced tokens seen: 40.

