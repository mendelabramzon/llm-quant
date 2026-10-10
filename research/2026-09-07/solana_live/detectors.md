# Solana detectors: research/2026-09-07/solana_live

| detector | hits | error |
|---|---:|---|
| sol_wash_volume | 2 |  |
| sol_quote_poster | 21 |  |
| sol_failure_spam | 10 |  |
| sol_collector_hub | 14 |  |
| sol_launch_factory | 6 |  |
| sol_flash_loan_spam | 2 |  |
| sol_liquidation_drought | 1 |  |
| sol_exchange_flow | 1 |  |
| sol_cctp_unknown_domain | 2 |  |
| sol_dust_poisoning | 4 |  |
| sol_large_move | 7 |  |
| sol_lst_nav_basis | 0 |  |
| sol_stable_rate_gap | 4 |  |

## notable (16)

- `sol_wash_volume:all` $86,773,770 of $205,189,806 priced DEX volume (42%) is self-matched in 91,743 swaps by 8,751 wallet pairs
- `sol_wash_volume:venue:Pump.fun Amm` Pump.fun Amm: $86,773,758 (60% of its priced volume) self-matched in 91,726 swaps; top washed tokens DkDs…1n2M $12.6M, GyKY…mApJ $11.9M, AfUe…Jb5p $9.8M
- `sol_collector_hub:all` 9 unlabelled fan-in hubs with >=500 senders collected 15194 SOL; 4 fan-out distributors with >=1,000 transfers
- `sol_collector_hub:in:7uTT8Xi5RWXzy7h9XL244GRgEycDYDhLjr3ZyNdXi8pZ` 7uTT…i8pZ: 2,348 senders, 9739 SOL in (median 0.537), 60 transfer(s) out to 1 destination(s) — vault of deposit router 99vQ… (largest unlabelled fan-in)
- `sol_stable_rate_gap:USDC:Jupiter Lend/Save main` USDC pays 1.60pp more on Jupiter Lend (4.56%, $451,679,926) than Save main (2.96%, $22,177,432)
- `sol_collector_hub:in:AcNhnoXP933a5A78m3Vpy2rKeuzKY1bPyZWFppgkZHJW` AcNh…ZHJW: 729 senders, 1131 SOL in (median 0.317), 1 transfer(s) out to 1 destination(s) — sybil-cluster collector (3,253 wallets → 1 sweep, same playbook and token amount as A1zq…)
- `sol_collector_hub:in:A1zqWmtRyPvy3en6EKZDoivQ3ABz4xApc5ExzDcB2mos` A1zq…2mos: 710 senders, 820 SOL in (median 0.297), 1 transfer(s) out to 1 destination(s) — sybil-cluster collector (3,254 wallets → 1 sweep in 6 min)
- `sol_collector_hub:in:ArLh5MKcHRb8ZJbZwaSuLoGrkfEnUc4QndCExVysdbDf` ArLh…dbDf: 532 senders, 684 SOL in (median 0.576), 1 transfer(s) out to 1 destination(s) — sybil-cluster collector (532 wallets, 683.6 SOL round trip funded by 2Fs1…)
- `sol_collector_hub:in:62jw1nT7xfh5y4CvV2ym8hBeBpN6pfkFCvavuipiMZ4F` 62jw…MZ4F: 533 senders, 680 SOL in (median 0.582), 1 transfer(s) out to 1 destination(s) — sybil-cluster collector (533 wallets → 1 sweep)
- `sol_collector_hub:in:BTRkMytz72cCNt3QbCzGrgLim8CSJr3koK9c5wgNg4WT` BTRk…g4WT: 536 senders, 662 SOL in (median 0.548), 0 transfer(s) out to 0 destination(s)
- `sol_collector_hub:in:4QoHvvN9U3c5SuVsxo1WHDPm4AXU7q4LPvjqXhjYWEax` 4QoH…WEax: 531 senders, 654 SOL in (median 0.514), 1 transfer(s) out to 1 destination(s) — sybil-cluster collector (531 wallets, 654.1 SOL round trip funded by C1yb…)
- `sol_collector_hub:in:BiAByV6PVF3qsRhMiUEincR1jjYGHSYvT2nKiWuT8MPm` BiAB…8MPm: 523 senders, 648 SOL in (median 0.486), 0 transfer(s) out to 0 destination(s)
- `sol_stable_rate_gap:USDT:Kamino JLP/Save main` USDT pays 2.62pp more on Kamino JLP (4.38%, $1,870,868) than Save main (1.76%, $5,172,673)
- `sol_stable_rate_gap:USDG:Jupiter Lend/Kamino SOL/BTC` USDG pays 1.65pp more on Jupiter Lend (5.42%, $2,923,981) than Kamino SOL/BTC (3.77%, $44,702,438)
- `sol_stable_rate_gap:PYUSD:Kamino JLP/Kamino SOL/BTC` PYUSD pays 2.20pp more on Kamino JLP (4.18%, $1,416,976) than Kamino SOL/BTC (1.98%, $40,029,136)
- `sol_collector_hub:in:6sBT3V93pQNCFCuEpvAvfKrFkZhLV3uNHGuxfGUYN6P6` 6sBT…N6P6: 522 senders, 176 SOL in (median 0.197), 0 transfer(s) out to 0 destination(s)

## info (58)

- `sol_large_move:9936VFvgRmW1STvdgeyPQaKHDx5DwBtbhZkT3HcdL3QK` 9936…L3QK sent $10,000,000 USDC in one tx — Huma-linked treasury ($10M USDC in via Huma, out to a Squads multisig)
- `sol_large_move:7s1da8DduuBFqGra5bJBjpnvL5E9mGzCuMk1Qkh4or2Z` 7s1d…or2Z sent $10,000,000 USDC in one tx
- `sol_large_move:6q76D2fJxPqzQQfUBMmkb2MzT4Vg7VGe2dgXHKd33ad2` 6q76…3ad2 received $10,000,000 USDC in one tx
- `sol_large_move:81w96XvKAZZFmmuzaohSQUyxtGnAPJmkjwoBFBmtytUj` 81w9…ytUj received $9,767,758 USDC in one tx
- `sol_large_move:Bc5bth4Mn2n8DX1etZwvnq3uDEGg479s2D24TCEsnXHf` Bc5b…nXHf sent $9,767,758 USDC in one tx
- `sol_large_move:3ADzk5YDP9sgorvPSs9YPxigJiSqhgddpwHwwPwmEFib` 3ADz…EFib sent $7,956,238 USDC in one tx — Binance-bound consolidation wallet (receives from Gate/KuCoin, sends to Binance)
- `sol_large_move:5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9` 5tzF…uAi9 received $7,956,238 USDC in one tx — Binance
- `sol_exchange_flow:Binance` Binance net +$5,770,838 over 1,912 txs (USDC +5.5M, USDT +2.9M, SOL -2.5M, BONK -0.1M)
- `sol_collector_hub:out:5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9` 5tzF…uAi9: 1,063 SOL transfers out (35122 SOL) to 6+ destinations — Binance
- `sol_collector_hub:out:F7p3dFrjRTbtRp8FRF6qHLomXbKRBzpvBLjtQcfcgmNe` F7p3…gmNe: 3,220 SOL transfers out (14666 SOL) to 6+ destinations — sweep destination of deposit vault 7uTT8X…
- `sol_collector_hub:out:CVrbFfQuU3L1bv1UAMrZkfJNYjUk6V5znZptZHZfQKWa` CVrb…QKWa: 1,027 SOL transfers out (1517 SOL) to 6+ destinations
- `sol_collector_hub:out:BwWK17cbHxwWBKZkUYvzxLcNQ1YVyaFezduWbtm2de6s` BwWK…de6s: 1,645 SOL transfers out (591 SOL) to 6+ destinations
- `sol_cctp_unknown_domain:out:domain 27` CCTP out to unmapped domain 27: $20,523 in 33 transfers
- `sol_cctp_unknown_domain:out:domain 15` CCTP out to unmapped domain 15: $80 in 1 transfers
- `sol_quote_poster:all` 20 quote-posting programs sent 2,335,133 txs = 36.5% of non-vote transactions
- `sol_quote_poster:EtrnLzgbS7nMMy5fbD42kXiUzGg8XQzJ972Xtk1cjWih` Phoenix Eternal (Ellipsis) — market-maker spline/oracle parameter updates: 362,138 txs from 143 payer(s), 0.0% move a token, 22% failed, 1.9 SOL fees
- `sol_quote_poster:9H6tua7jkLhdm3w8BvgpTn5LZNU7g4ZynDmCiNN3q6Rp` HumidiFi: 239,076 txs from 22 payer(s), 0.0% move a token, 28% failed, 2.4 SOL fees
- `sol_quote_poster:TessVdML9pBGgG9yGks7o4HewRaXVAMuoVj4x83GLQH` TesseraV: 210,243 txs from 1 payer(s), 0.0% move a token, 31% failed, 1.1 SOL fees
- `sol_quote_poster:DhpyNWkdxFh3DRPsBrwRwrK3TYC5t7Q4arnSvf3t84HY` pump.fun sniper program (94% failed, 4 payers): 139,654 txs from 4 payer(s), 0.0% move a token, 94% failed, 1.6 SOL fees
- `sol_quote_poster:9L1qqo7q7vq7sKuMsBGKPF81z6GK7N4orWGgGFwwqqDF` arbitrage bot program (logs "No arb opportunity found"; 1 payer): 137,824 txs from 1 payer(s), 0.1% move a token, 22% failed, 1.3 SOL fees
- `sol_quote_poster:Prism8hsRo6Ww5jiN5Zeh3YDPLZHqHduCPSAV7JF7qv` copychain.cc copy-trading bot program: 136,317 txs from 8 payer(s), 0.0% move a token, 55% failed, 1.2 SOL fees
- `sol_quote_poster:ojh19ojaKduoJZuaJADhcVGp4xt1TcdAvZmpVsCorch` Scorch: 106,523 txs from 1 payer(s), 0.0% move a token, 47% failed, 0.8 SOL fees
- `sol_quote_poster:W1LDCARDa67SPBG7TFpQivHnEZXRtxCFP13ysEd1bWR` unlabelled tiny-payload poster (40 bytes, 2 accounts, ~20 payers): 106,140 txs from 24 payer(s), 0.0% move a token, 20% failed, 0.5 SOL fees
- `sol_quote_poster:NA247a7YE9S3p9CdKmMyETx8TTwbSdVbVYHHxpnHTUV` NA24…HTUV: 101,067 txs from 12 payer(s), 0.1% move a token, 59% failed, 1.4 SOL fees
- `sol_quote_poster:QuaNtZsgYRe5Z9Bk4LZ4cTD9tbkVoyCNf1R2BN9bBDv` Quantum: 98,374 txs from 6 payer(s), 0.0% move a token, 0% failed, 0.6 SOL fees
- `sol_quote_poster:dijkbkCAKfFTCxQg3u1pg82gVU1jJGHBBRcteD11mBu` unlabelled tiny-payload poster (33 bytes, 2 accounts, 1 payer): 89,936 txs from 1 payer(s), 0.0% move a token, 0% failed, 0.5 SOL fees
- `sol_quote_poster:7JwTi9ambvCTYwZbNQEZA8hzpG3ymPWRZpAxgKPJ94ZG` pump.fun sniper program (99% failed buys, 4 payers): 81,780 txs from 4 payer(s), 0.0% move a token, 99% failed, 0.6 SOL fees
- `sol_quote_poster:Hd7c1kYHqYJ7dD1bLf9C61XC22JgbGp4P1PQ8UNcUH5w` unlabelled bot program (26 accounts, pump.fun Sell/GetFees inner calls, 3 payers): 76,629 txs from 3 payer(s), 0.3% move a token, 22% failed, 0.4 SOL fees
- `sol_quote_poster:6MWVTis8rmmk6Vt9zmAJJbmb3VuLpzoQ1aHH4N6wQEGh` 6MWV…QEGh: 75,388 txs from 3 payer(s), 0.0% move a token, 0% failed, 0.8 SOL fees
- `sol_quote_poster:BiSoNHVpsVZW2F7rx2eQ59yQwKxzU5NvBcmKshCSUypi` BisonFi: 70,093 txs from 3 payer(s), 0.0% move a token, 22% failed, 0.5 SOL fees
- `sol_quote_poster:3RWLeScYhxvdywAcFWxoVBb88eBDspskcHEX1Q55v3eX` 3RWL…v3eX: 68,028 txs from 4 payer(s), 0.0% move a token, 100% failed, 0.6 SOL fees
- `sol_quote_poster:BevFQ2LKT3riywRANkmWWKE5dksoTkpCtn7B1uzp56A3` BevF…56A3: 62,118 txs from 4 payer(s), 0.0% move a token, 99% failed, 0.7 SOL fees
- `sol_quote_poster:2DNbzPochEcyCcWMbL4d9S3u9QqQEj5bbe6cSZFvKsbh` BisonFi Predict: 61,264 txs from 2 payer(s), 0.0% move a token, 9% failed, 0.3 SOL fees
- `sol_quote_poster:Archer8kgiavM61GyusMzaaS2ft5sALtNsD1HxkUPMhy` Archer: 59,588 txs from 3 payer(s), 0.0% move a token, 15% failed, 0.3 SOL fees
- `sol_quote_poster:DDsnwb7dxKSjzTYDFjU8F6rpYNZa1sp7Fmfb2nGDAMEo` DDsn…AMEo: 52,953 txs from 3 payer(s), 0.8% move a token, 25% failed, 1.0 SOL fees
- `sol_failure_spam:all` 9 failure bots: 508,490 failed txs = 26.7% of all failures, 5.0 SOL of fees
- `sol_failure_spam:DhpyNWkdxFh3DRPsBrwRwrK3TYC5t7Q4arnSvf3t84HY` pump.fun sniper program (94% failed, 4 payers): 139,654 txs, 94% failed, 4 payer(s), 1.6 SOL fees
- `sol_failure_spam:7JwTi9ambvCTYwZbNQEZA8hzpG3ymPWRZpAxgKPJ94ZG` pump.fun sniper program (99% failed buys, 4 payers): 81,780 txs, 99% failed, 4 payer(s), 0.6 SOL fees
- `sol_failure_spam:3RWLeScYhxvdywAcFWxoVBb88eBDspskcHEX1Q55v3eX` 3RWL…v3eX: 68,028 txs, 100% failed, 4 payer(s), 0.6 SOL fees
- `sol_failure_spam:BevFQ2LKT3riywRANkmWWKE5dksoTkpCtn7B1uzp56A3` BevF…56A3: 62,118 txs, 99% failed, 4 payer(s), 0.7 SOL fees
- `sol_failure_spam:Db8hf6HoijsAi6PZdXn4wByhB6LVrn17MPS6XprQBEwH` Db8h…BEwH: 36,396 txs, 100% failed, 1 payer(s), 0.2 SOL fees
- `sol_failure_spam:naebaL84HEJ55PFPrsUZMa4CC8CjmW9YkRDQZiN2yCV` naeb…2yCV: 35,784 txs, 100% failed, 3 payer(s), 0.4 SOL fees
- `sol_failure_spam:4jjVJMSUdpjqkpNm5PEqd6xMwB3GysdoG7E3UGh8FQtp` 4jjV…FQtp: 34,951 txs, 100% failed, 1 payer(s), 0.4 SOL fees
- `sol_failure_spam:4VXz7mbrduuykm6XbmpPKrvV2FkFxb3QcQGFevEWRjWH` 4VXz…RjWH: 33,861 txs, 100% failed, 1 payer(s), 0.2 SOL fees
- `sol_failure_spam:9w1gh7mKG8WZN5k4aiMcAtUpQceVrL1tJzfkK9EcTNzp` 9w1g…TNzp: 26,486 txs, 100% failed, 2 payer(s), 0.2 SOL fees
- `sol_launch_factory:all` 1,750 token launches by 804 creators; top 3 creators [60, 57, 49]
- `sol_launch_factory:Asi5DTGEeiso6k7ya6ndDabEZ7DRCgfTpCBLPH5E3aQs` Asi5…3aQs launched 60 tokens in the hour
- `sol_launch_factory:VygS4a8U5ZXPak13LrqaTW7vKPEcoTcyfZ3eRLoZg4R` VygS…Zg4R launched 57 tokens in the hour
- `sol_launch_factory:74fHCK8r4AR8rSbTF8HYqjG7Dbio7utvZWdwAE5H87Y4` 74fH…87Y4 launched 49 tokens in the hour
- `sol_launch_factory:AmjvT9vh3m9VNFkqzUqNsJvxxAaQMq9dHKWB8MPepraL` Amjv…praL launched 31 tokens in the hour
- `sol_launch_factory:3ph9MUgWBFV123nQCtJL62XCPYdpUMtaxcfCpD8QioVA` 3ph9…ioVA launched 22 tokens in the hour
- `sol_flash_loan_spam:Kamino Lend:guofisumfbUkeV169uPKWx1EcRiq7idJe25xBtdVNk3` guof…VNk3: 2,091 failed flash loans on Kamino Lend, no successes
- `sol_flash_loan_spam:Kamino Lend:Hz7KY4XrZs7A5XHonoUwBhqarVZJCnm4ByDvQzcDr7sz` Hz7K…r7sz: 178 failed flash loans on Kamino Lend, no successes
- `sol_liquidation_drought:all` 0 liquidations on any lending venue; 187 failed attempts (Kamino Lend 184, marginfi v2 3)
- `sol_dust_poisoning:6uqxgxbsVJWLWJfKipEJ5n21Jq51nYba9aVSjnEdXSPy` 6uqx…XSPy: 7,180 dust transfers to 866 recipients
- `sol_dust_poisoning:7Z1X7kuBnAqMthkUQb7mRs8cvdKpde6QXUjHgAp27CeJ` 7Z1X…7CeJ: 6,916 dust transfers to 6,658 recipients
- `sol_dust_poisoning:DRrohsjhNZTbNpXWLwqtJLP5SCij3iZbYRtw3VacGwEc` DRro…GwEc: 2,320 dust transfers to 2,108 recipients
- `sol_dust_poisoning:AeeT8wTGMnQRz2jM5zk13NCq97Ng1Q2XgCnpVgFWJbqj` AeeT…Jbqj: 1,418 dust transfers to 45 recipients

