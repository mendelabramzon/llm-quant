# Captive-flow LP: USDC/USDG venues

Block **25920655**, 2026-09-06T20:19:35+00:00. Flow replayed from 2 contiguous windows of saved logs (1026 swaps). Deployed TVL and price read on-chain at the pinned block.

## Pools

| Pool | LP fee | Deployed TVL | 24h volume | Turnover | Gross fees/day | Marginal-LP APR (+$50k) | Top taker share |
|---|--:|--:|--:|--:|--:|--:|--:|
| USDC/USDG v4 0.65bp | 0.65 bp | $1,042,852 | $6,319,168 | 6.1x | $411 | 13.7% | 44% |
| USDC/USDG v4 0.75bp | 0.75 bp | $964,545 | $5,849,096 | 6.1x | $439 | 15.8% | 62% |
| USDC/USDG Curve | 1.00 bp | $20,028,824 | $20,799,839 | 1.0x | $2,080 | 3.8% | - |

## Marginal concentrated-LP APR by add size (v4)

| Pool | +$10k | +$50k | +$100k | +$500k |
|---|--:|--:|--:|--:|
| USDC/USDG v4 0.65bp | 14.2% | 13.7% | 13.1% | 9.7% |
| USDC/USDG v4 0.75bp | 16.4% | 15.8% | 15.0% | 10.9% |

## Flow quality

- **USDC/USDG v4 0.65bp**: top taker `0xf70da97812cb96acdf810712aa562db8dfa3dbef` is 44% of volume, is NOT an LP; 278 distinct takers, Herfindahl 0.223. Active peg band 0.010%.
- **USDC/USDG v4 0.75bp**: top taker `0xf70da97812cb96acdf810712aa562db8dfa3dbef` is 62% of volume, is NOT an LP; 101 distinct takers, Herfindahl 0.390. Active peg band 0.010%.
