# Solana detectors: research/2026-09-10/solana_live

| detector | hits | error |
|---|---:|---|
| sol_wash_volume | 2 |  |
| sol_quote_poster | 0 |  |
| sol_failure_spam | 0 |  |
| sol_collector_hub | 0 |  |
| sol_launch_factory | 1 |  |
| sol_flash_loan_spam | 0 |  |
| sol_liquidation_drought | 1 |  |
| sol_exchange_flow | 2 |  |
| sol_cctp_unknown_domain | 1 |  |
| sol_dust_poisoning | 1 |  |
| sol_large_move | 4 |  |
| sol_lst_nav_basis | 0 |  |
| sol_stable_rate_gap | 2 |  |

## notable (4)

- `sol_wash_volume:all` $6,328,565 of $20,552,771 priced DEX volume (31%) is self-matched in 7,489 swaps by 2,889 wallet pairs
- `sol_wash_volume:venue:Pump.fun Amm` Pump.fun Amm: $6,328,561 (42% of its priced volume) self-matched in 7,485 swaps; top washed tokens BxrC…fL97 $1.8M
- `sol_stable_rate_gap:USDT:Kamino JLP/Save main` USDT pays 2.53pp more on Kamino JLP (4.39%, $1,859,279) than Save main (1.86%, $5,148,730)
- `sol_stable_rate_gap:PYUSD:Kamino JLP/Kamino SOL/BTC` PYUSD pays 2.55pp more on Kamino JLP (4.50%, $1,399,456) than Kamino SOL/BTC (1.96%, $40,434,072)

## info (10)

- `sol_exchange_flow:Coinbase 3` Coinbase 3 net +$20,756,722 over 68 txs (USDC +20.8M, SOL -0.0M, PYUSD +0.0M, EURC +0.0M)
- `sol_large_move:3ADzk5YDP9sgorvPSs9YPxigJiSqhgddpwHwwPwmEFib` 3ADz…EFib sent $19,614,838 USDT in one tx — Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance)
- `sol_large_move:5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9` 5tzF…uAi9 received $19,614,838 USDT in one tx — Binance
- `sol_exchange_flow:Binance` Binance net +$19,317,641 over 100 txs (USDT +19.6M, USD1 -0.2M, PENGU -0.1M, RAY -0.0M)
- `sol_large_move:GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE` GJRs…7npE received $18,894,647 USDC in one tx — Coinbase 3
- `sol_large_move:BjYtrpedqFgveTy8u55fYadfhcepwMtneJQL9SkK6ZmU` BjYt…6ZmU sent $18,894,647 USDC in one tx
- `sol_cctp_unknown_domain:out:domain 27` CCTP out to unmapped domain 27: $3,021 in 3 transfers
- `sol_launch_factory:all` 225 token launches by 151 creators; top 3 creators [7, 6, 5]
- `sol_liquidation_drought:all` 0 liquidations on any lending venue; 69 failed attempts (marginfi v2 69)
- `sol_dust_poisoning:6uqxgxbsVJWLWJfKipEJ5n21Jq51nYba9aVSjnEdXSPy` 6uqx…XSPy: 1,141 dust transfers to 323 recipients

