#!/usr/bin/env python3
"""Live scan of Ethereum mainnet blocks for slow inefficiencies (not block-level MEV).

Reads the raw blocks and logs written by `live_collect.py`, decodes value legs, swaps, liquidity changes, lending events and
bridge sends, and aggregates them into features that a patient, non-latency actor can act on:

  * passive LP economics per pool (fee yield on in-range capital, share of fees taken by just-in-time liquidity),
  * lending rates per venue and reserve (utilisation shocks, cross-venue dispersion, carry), and health factors of the
    borrowers active in the window,
  * borrow/withdraw proceeds followed to exchange wallets (leverage-to-exchange pipeline),
  * exchange net flow per asset, large transfers, round trips, scheduled (TWAP-like) flow,
  * stablecoin and LST implied prices versus NAV or par (slow arbitrage through redemption paths),
  * bridge destinations (CCTP domains, LayerZero OFT endpoints),
  * gas market summary.

Commands (run from the repository root with `uv run --with pycryptodome python scripts/live_scan.py ...`):

  analyze  --out research/2026-09-06/live [--first N --last M]   offline over the raw files; writes analysis.json
  head     --out ...                                               bounded RPC at the head: prices, NAV rates, lending reserves,
                                                                   health factors, token metadata; writes head_state.json
  render   --out ...                                               analysis.json + head_state.json + insights.md -> report.md
  live     --out ...                                               tail the chain, re-analyze the trailing window, append live_log.md
  midnight --out ...                                               targeted log queries for the 23:30-00:20 UTC balance routine
  verify   --out ... [--mechanisms]                                re-derive the headline numbers from raw through an
                                                                   independent path; fails loudly on drift
  detect   --out ...                                               run every registered detector over the window
  pipeline --out ...                                               analyze, verify, detect and ingest, in dependency order
"""
import argparse
import collections
import datetime as dt
import json
import math
import statistics
import sys
import time
from pathlib import Path

from Crypto.Hash import keccak as _keccak

from live_collect import block_path, logs_path, read_gz, head as rpc_head, tail_once, first_block_at, utc
from live_rpc import RPC, RPCError, hx, word, sword, topic_addr, topic_int, enc_addr, enc_uint

ROOT = Path(__file__).resolve().parents[1]
EXPLORER = 'https://etherscan.io'


def keccak(s):
    return '0x' + _keccak.new(digest_bits=256, data=s.encode()).hexdigest()


def sel(s):
    return keccak(s)[:10]


# ----------------------------------------------------------------------------------------------------------------------
# Registries. Addresses are as known to the author; `head` verifies symbol()/decimals() of every token that matters.
# ----------------------------------------------------------------------------------------------------------------------
TOKENS = {
    '0xdac17f958d2ee523a2206206994597c13d831ec7': ('USDT', 6, 'USDT'),
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': ('USDC', 6, 'USDC'),
    '0x6b175474e89094c44da98b954eedeac495271d0f': ('DAI', 18, 'DAI'),
    '0x4c9edd5852cd905f086c759e8383e09bff1e68b3': ('USDe', 18, 'USD'),
    '0xdc035d45d973e3ec169d2276ddab16f1e407384f': ('USDS', 18, 'USD'),
    '0x6c3ea9036406852006290770bedfcaba0e23a0e8': ('PYUSD', 6, 'USD'),
    '0x5f98805a4e8be255a32880fdec7f6728c6568ba0': ('LUSD', 18, 'USD'),
    '0xf939e0a03fb07f59a73314e73794be0e57ac1b4e': ('crvUSD', 18, 'USD'),
    '0xc5f0f7b66764f6ec8c8dff7ba683102295e16409': ('FDUSD', 18, 'USD'),
    '0x73a15fed60bf67631dc6cd7bc5b6e8da8190acf5': ('USD0', 18, 'USD'),
    '0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f': ('GHO', 18, 'USD'),
    '0x8d0d000ee44948fc98c9b98a4fa4921476f08b0d': ('USD1', 18, 'USD'),
    '0x8292bb45bf1ee4d140127049757c2e0ff06317ed': ('RLUSD', 18, 'USD'),
    '0x0000000000085d4780b73119b644ae5ecd22b376': ('TUSD', 18, 'USD'),
    '0x8e870d67f660d95d5be530380d0ec0bd388289e1': ('USDP', 18, 'USD'),
    '0x853d955acef822db058eb8505911ed77f175b99e': ('FRAX', 18, 'USD'),
    '0xcacd6fd266af91b8aed52accc382b4e165586e29': ('frxUSD', 18, 'USD'),
    '0xc139190f447e929f090edeb554d95abb8b18ac1c': ('USDtb', 18, 'USD'),
    '0xe343167631d89b6ffc58b88d6b7fb0228795491d': ('USDG', 6, 'USD'),
    '0x00000000efe302beaa2b3e6e1b18d08d69a9012a': ('AUSD', 6, 'USD'),
    '0x865377367054516e17014ccded1e7d814edc9ce4': ('DOLA', 18, 'USD'),
    '0xfa2b947eec368f42195f24f36d2af29f7c24cec2': ('USDf', 18, 'USD'),
    '0x35d8949372d46b7a3d5a56006ae77b215fc69bc0': ('USD0++', 18, 'USD'),
    '0x1abaea1f7c830bd89acc67ec4af516284b1bc33c': ('EURC', 6, 'EUR'),
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': ('WETH', 18, 'ETH'),
    '0xae7ab96520de3a18e5e111b5eaab095312d7fe84': ('stETH', 18, 'STETH'),
    '0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0': ('wstETH', 18, 'WSTETH'),
    '0xae78736cd615f374d3085123a210448e74fc6393': ('rETH', 18, 'RETH'),
    '0xbe9895146f7af43049ca1c1ae358b0541ea49704': ('cbETH', 18, 'CBETH'),
    '0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee': ('weETH', 18, 'WEETH'),
    '0x35fa164735182de50811e8e2e824cfb9b6118ac2': ('eETH', 18, 'ETH'),
    '0xbf5495efe5db9ce00f80364c8b423567e58d2110': ('ezETH', 18, 'EZETH'),
    '0xa1290d69c65a6fe4df752f95823fae25cb99e5a7': ('rsETH', 18, 'RSETH'),
    '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599': ('WBTC', 8, 'BTC'),
    '0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf': ('cbBTC', 8, 'BTC'),
    '0x18084fba666a33d37592fa2633fd49a74dd93a88': ('tBTC', 18, 'BTC'),
    '0x8236a87084f8b84306f72007f36f2618a5634494': ('LBTC', 8, 'BTC'),
    '0xa3931d71877c0e7a3148cb7eb4463524fec27fbd': ('sUSDS', 18, 'SUSDS'),
    '0x83f20f44975d03b1b09e64809b757c47f942beea': ('sDAI', 18, 'SDAI'),
    '0x9d39a5de30e57443bff2a8307a4256c8797a3497': ('sUSDe', 18, 'SUSDE'),
    '0x514910771af9ca656af840dff83e8264ecf986ca': ('LINK', 18, 'LINK'),
    '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984': ('UNI', 18, 'UNI'),
    '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9': ('AAVE', 18, 'AAVE'),
    '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2': ('MKR', 18, 'MKR'),
    '0xd533a949740bb3306d119cc777fa900ba034cd52': ('CRV', 18, 'CRV'),
    '0xc18360217d8f7ab5e7c516566761ea12ce7f9d72': ('ENS', 18, 'ENS'),
}
NATIVE = 'ETH'
TOKENS['0x' + '0' * 40] = ('ETH', 18, 'ETH')  # Uniswap v4 native currency
FEEDS = {  # price key -> (feed, expected description)
    'ETH': ('0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419', 'ETH / USD'),
    'BTC': ('0xf4030086522a5beea4988f8ca5b36dbc97bee88c', 'BTC / USD'),
    'STETH': ('0xcfe54b5cd566ab89272946f602d76ea879cab4a8', 'STETH / USD'),
    'USDC': ('0x8fffffd4afb6115b954bd326cbe7b4ba576818f6', 'USDC / USD'),
    'USDT': ('0x3e7d1eab13ad0104d2750b8863b489d65364e32d', 'USDT / USD'),
    'DAI': ('0xaed0c38402a5d19df6e4c03f4e2dced6e29c1ee9', 'DAI / USD'),
    'LINK': ('0x2c1d072e956affc0d435cb7ac38ef18d24d9127c', 'LINK / USD'),
    'UNI': ('0x553303d460ee0afb37edff9be42922d8ff63220e', 'UNI / USD'),
    'AAVE': ('0x547a514d5e3769680ce22b2361c10ea13619e8a9', 'AAVE / USD'),
    'MKR': ('0xec1d1b3b0443256cc3860e24a46f108e699484aa', 'MKR / USD'),
    'CRV': ('0xcd627aa160a6fa45eb793d19ef54f5062f20f33f', 'CRV / USD'),
    'ENS': ('0x5c00128d4d1c2f4f652c267d7bcdd7ac99c16e16', 'ENS / USD'),
    'EUR': ('0xb49f677943bc038e9857d61e7d053caa2c1734c1', 'EUR / USD'),
}
# A second, independent view of the same exchange rate, where the contract publishes one. `nav_discount` builds a
# trade out of the difference between a NAV and a market price, and the NAV side was a single call with nothing to
# disagree with it — the last unchecked surface in the head state. An ERC-4626 vault's share price is also
# `totalAssets / totalSupply`, and the two are computed by different code inside the vault; Lido and Rocket Pool each
# publish a share-conversion function alongside their headline rate. Where a second view exists, `verify` compares it.
RATE_CROSSCHECK = {
    'SUSDS': ('ratio', 'totalAssets()', 'totalSupply()'),
    'SDAI':  ('ratio', 'totalAssets()', 'totalSupply()'),
    'SUSDE': ('ratio', 'totalAssets()', 'totalSupply()'),
    # stEthPerToken() lives on wstETH; the share-conversion that reproduces it lives on stETH, so this one needs its
    # own contract. Pointed at wstETH it simply returns nothing, which is a silent gap rather than a failure — the
    # reason the check reports how many rates it could compare, not just how many matched.
    'WSTETH': ('call', 'getPooledEthByShares(uint256)', None, '0xae7ab96520de3a18e5e111b5eaab095312d7fe84'),
    'RETH':   ('call', 'getEthValue(uint256)', None),
    'WEETH':  ('call', 'getEETHByWeETH(uint256)', None),
}
RATES = {  # price key -> (contract, method, underlying key)
    'WSTETH': ('0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0', 'stEthPerToken()', 'STETH'),
    'RETH': ('0xae78736cd615f374d3085123a210448e74fc6393', 'getExchangeRate()', 'ETH'),
    'CBETH': ('0xbe9895146f7af43049ca1c1ae358b0541ea49704', 'exchangeRate()', 'ETH'),
    'WEETH': ('0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee', 'getRate()', 'ETH'),
    'EZETH': ('0x74a09653a083691711cf8215a6ab074bb4e99ef5', 'getRate()', 'ETH'),   # Renzo balancer rate provider (memory)
    'RSETH': ('0x349a73444b1a310bae67ef67973022020d70020d', 'rsETHPrice()', 'ETH'),  # Kelp LRT oracle (memory)
    'SUSDS': ('0xa3931d71877c0e7a3148cb7eb4463524fec27fbd', 'convertToAssets(uint256)', 'USD'),
    'SDAI': ('0x83f20f44975d03b1b09e64809b757c47f942beea', 'convertToAssets(uint256)', 'DAI'),
    'SUSDE': ('0x9d39a5de30e57443bff2a8307a4256c8797a3497', 'convertToAssets(uint256)', 'USD'),
}
PARITY_KEYS = {'USD'}
STABLE_SYMBOLS = {s for s, _, k in TOKENS.values() if k in ('USD', 'USDC', 'USDT', 'DAI')}
REFERENCE_ORDER = ['USDC', 'USDT', 'DAI', 'ETH', 'BTC', 'STETH', 'USD']  # which side of a swap prices it
WETH = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'

AAVE_POOL = '0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2'
SPARK_POOL = '0xc13e21b648a5ee794902342038ff3adab66be987'
LENDING_POOLS = {AAVE_POOL: 'Aave v3', SPARK_POOL: 'SparkLend'}
MORPHO = '0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb'
V4_MANAGER = '0x000000000004444c5dc75cb358380d2e3de08a90'
COMETS = {'0xc3d688b66703497daa19211eedff47f25384cdc3': 'Compound v3 USDC', '0x3afdc9bca9213a35503b077a6072f3d0d5ab0840': 'Compound v3 USDT',
          '0xa17581a9e3356d9a858b789d68b4d866e593ae94': 'Compound v3 WETH'}
RATE_ASSETS = ['USDC', 'USDT', 'DAI', 'USDS', 'USDe', 'GHO', 'PYUSD', 'RLUSD', 'WETH', 'wstETH', 'weETH', 'WBTC', 'cbBTC', 'sUSDe', 'LINK']
CCTP_DOMAINS = {0: 'Ethereum', 1: 'Avalanche', 2: 'OP Mainnet', 3: 'Arbitrum', 4: 'Noble', 5: 'Solana', 6: 'Base', 7: 'Polygon', 8: 'Sui', 9: 'Aptos',
                10: 'Unichain', 11: 'Linea', 12: 'Codex', 13: 'Sonic', 14: 'World Chain'}
OFT_ADAPTERS = {'0x6c96de32cea08842dcc4058c14d3aaad7fa41dee': 'USDT', '0x147bde4f997f0d4c7544ed0c55eacf1e5e6bf9c4': 'USDG'}
LZ_EIDS = {30101: 'Ethereum', 30102: 'BNB', 30106: 'Avalanche', 30109: 'Polygon', 30110: 'Arbitrum', 30111: 'OP', 30184: 'Base', 30183: 'Linea',
           30165: 'zkSync', 30181: 'Mantle', 30214: 'Scroll', 30168: 'Solana', 30255: 'Fraxtal', 30332: 'Sonic', 30290: 'Berachain'}
# Exchange labels from model memory: unverified, shown with "(memory)".
MEMORY_LABELS = {
    '0x28c6c06298d514db089934071355e5743bf21d60': 'Binance 14', '0x21a31ee1afc51d94c2efccaa2092ad1028285549': 'Binance 15',
    '0xdfd5293d8e347dfe59e90efd55b2956a1343963d': 'Binance 16', '0x56eddb7aa87536c09ccc2793473599fd21a8b17f': 'Binance 17',
    '0x9696f59e4d72e237be84ffd425dcad154bf96976': 'Binance 18', '0x4976a4a02f38326660d17bf34b431dc6e2eb2327': 'Binance 20',
    '0xf977814e90da44bfa03b6295a0616a897441acec': 'Binance 8', '0x5a52e96bacdabb82fd05763e25335261b270efcb': 'Binance 28',
    '0xbe0eb53f46cd790cd13851d5eff43d12404d33e8': 'Binance 7', '0x71660c4005ba85c37ccec55d0c4493e66fe775d3': 'Coinbase 1',
    '0x503828976d22510aad0201ac7ec88293211d23da': 'Coinbase 2', '0xddfabcdc4d8ffc6d5beaf154f18b746a27f6db3f': 'Coinbase 3',
    '0x3cd751e6b0078be393132286c442345e5dc49699': 'Coinbase 4', '0xb5d85cbf7cb3ee0d56b3bb207d5fc4b82f43f511': 'Coinbase 5',
    '0xeb2629a2734e272bcc07bda959863f316f4bd4cf': 'Coinbase 6', '0xa9d1e08c7793af67e9d92fe308d5697fb81d3e43': 'Coinbase 10',
    '0x55fe002aeff02f77364de339a1292923a15844b8': 'Coinbase 11', '0x2910543af39aba0cd09dbb2d50200b3e800a63d2': 'Kraken 4',
    '0x0a869d79a7052c7f1b55a8ebabbea3421f0d07d5': 'Kraken 6', '0xe853c56864a2ebe4576a807d26fdc4a0ada51919': 'Kraken 3',
    '0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0': 'Kraken 5', '0x98ec059dc3adfbdd63429454aeb0c990fba4a128': 'OKX',
    '0x6cc5f688a315f3dc28a7781717a9a798a59fda7b': 'OKX 2', '0x5041ed759dd4afc3a72b8192c143f72f4724081a': 'OKX 3',
    '0xf89d7b9c864f589bbf53a82105107622b35eaa40': 'Bybit', '0x1db92e2eebc8e0c075a02bea49a2935bcd2dfcf4': 'Bybit 2',
    '0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec': 'Bitfinex 2', '0x876eabf441b2ee5b5b0554fd502a8e0600950cfa': 'Bitfinex',
    '0x0d0707963952f2fba59dd06f2b425ace40b492fe': 'Gate.io', '0x2b5634c42055806a59e9107ed44d43c426e58258': 'KuCoin 1',
    '0xd6216fc19db775df9774a6e33526131da7d19a2c': 'KuCoin 6', '0xab5c66752a9e8167967685f1450532fb96d5d24f': 'HTX 1',
    '0x5c985e89dde482efe97ea9f1950ad149eb73829b': 'HTX 5', '0xe93381fb4c4f14bda253907b18fad305d799241a': 'HTX 10',
    '0x6262998ced04146fa42253a5c0af90ca02dfd2a3': 'Crypto.com 1', '0x72a53cdbbcc1b9efa39c834a540550e23463aacb': 'Crypto.com 2',
    '0xd24400ae8bfebb18ca49be86258a3c749cf46853': 'Gemini 1', '0x6fc82a5fe25a5cdb58bc74600a40a69c065263f8': 'Gemini 2',
    '0x5f65f7b609678448494de4c87521cdf6cef1e932': 'Gemini 4', '0x1522900b6dafac587d499a862861c0869be6e428': 'Bitstamp 4',
    '0x75e89d5979e4f6fba9f97c104c2f0afb3f1dcb88': 'MEXC', '0x1ab4973a48dc892cd9971ece8e01dcc7688f8f23': 'Bitget',
    '0x40b38765696e3d5d8d9d834d8aad4bb6e418e489': 'Robinhood 2', '0xba826fec90cefdf6706858e5fbafcb27a290fbe0': 'Upbit',
    '0xf70da97812cb96acdf810712aa562db8dfa3dbef': 'exchange hot wallet with USDG desk (day study)',
    '0xee7ae85f2fe2239e27d9c1e23fffe168d63b4055': 'exchange deposit contract (day study, unidentified)',
    '0xaa8ba7d4611437141192e7ceced531bc0a133efb': 'hot wallet (day study, unidentified)',
    '0x05ff6964d21e5dae3b1010d5ae0465b3c450f381': 'hot wallet (day study, unidentified)',
}
NOT_EXCHANGES = {'0xcd531ae9efcce479654c4926dec5f6209531ca7b', V4_MANAGER, MORPHO, AAVE_POOL, SPARK_POOL, '0x00000000000014aa86c5d3c41765bb24e11bd701',
                 '0x51c72848c68a965f66fa7a88855f9f7784502a7f', '0xf6e72db5454dd049d0788e411b06cfaf16853042', '0x37305b1cd40574e4c5ce33f8e8306be057fd7341',
                 '0xa188eec8f81263234da3622a406892f3d630f98c', '0x98c23e9d8f34fefb1b7bd6a91b7ff122f4e16f5c', '0x23878914efe38d27c4d67ab83ed1b93a74d4086a',
                 '0x445f16314284b43dfa1fd3cd77b9dea4a1bebd97', '0x52aa899454998be5b000ad077a46bbe360f4e497', '0xfd78ee919681417d192449715b2594ab58f5d002',
                 '0x0889e9327b98d7d1be3c301a4585ff3330502c9a', '0x0000000000000000000000000000000000000000'}
DAY_PROFILES = ROOT / 'research' / '2026-09-05' / 'amount_outliers_eth_day' / 'addresses.json.gz'
VERIFIED_LABELS = ROOT / 'scripts' / 'address_labels.json'
EXCHANGE_KINDS = {'exchange', 'exchange_deposit'}   # only these count as exchange flow / leverage-to-exchange
KIND_TAG = {'exchange': 'hot_wallet', 'exchange_deposit': 'deposit_sink'}
MIDNIGHT = {'hub': '0x31173ed183e5a9450c3671018ec4d770c8a8bf18', 'aave_leg': '0x56957e411ea83a0b4a0689c1fb0d1e5ea0d20149',
            'susds_leg': '0x688cc76d3b009d805ab6b4d0a1cbd228131b5cbf', 'holder': '0xf1edbf98dda764ec51de3776371f0f7d6f6156a8'}

# ----------------------------------------------------------------------------------------------------------------------
# Event topics
# ----------------------------------------------------------------------------------------------------------------------
T = {name: keccak(sig) for name, sig in {
    'Transfer': 'Transfer(address,address,uint256)',
    'V2Swap': 'Swap(address,uint256,uint256,uint256,uint256,address)',
    'V3Swap': 'Swap(address,address,int256,int256,uint160,uint128,int24)',
    'V3Mint': 'Mint(address,address,int24,int24,uint128,uint256,uint256)',
    'V3Burn': 'Burn(address,int24,int24,uint128,uint256,uint256)',
    'V4Swap': 'Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)',
    'V4Modify': 'ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)',
    'V4Init': 'Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)',
    'CurveEx': 'TokenExchange(address,int128,uint256,int128,uint256)',
    'CurveExU': 'TokenExchange(address,uint256,uint256,uint256,uint256)',
    'CurveExUnd': 'TokenExchangeUnderlying(address,int128,uint256,int128,uint256)',
    'BalSwap': 'Swap(bytes32,address,address,uint256,uint256)',
    'AaveSupply': 'Supply(address,address,address,uint256,uint16)',
    'AaveBorrow': 'Borrow(address,address,address,uint256,uint8,uint256,uint16)',
    'AaveRepay': 'Repay(address,address,address,uint256,bool)',
    'AaveWithdraw': 'Withdraw(address,address,address,uint256)',
    'AaveLiq': 'LiquidationCall(address,address,address,uint256,uint256,address,bool)',
    'AaveRDU': 'ReserveDataUpdated(address,uint256,uint256,uint256,uint256,uint256)',
    'AaveFlash': 'FlashLoan(address,address,address,uint256,uint8,uint256,uint16)',
    'MorphoSupply': 'Supply(bytes32,address,address,uint256,uint256)',
    'MorphoWithdraw': 'Withdraw(bytes32,address,address,address,uint256,uint256)',
    'MorphoBorrow': 'Borrow(bytes32,address,address,address,uint256,uint256)',
    'MorphoRepay': 'Repay(bytes32,address,address,uint256,uint256)',
    'MorphoLiq': 'Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)',
    'MorphoFlash': 'FlashLoan(address,address,uint256)',
    'BalFlash': 'FlashLoan(address,address,uint256,uint256)',
    'CCTP1': 'DepositForBurn(uint64,address,uint256,address,bytes32,uint32,bytes32,bytes32)',
    'CCTP2': 'DepositForBurn(address,uint256,address,bytes32,uint32,bytes32,bytes32,uint256,uint32,bytes)',
    'CCTPMint1': 'MintAndWithdraw(address,uint256,address)',
    'CCTPMint2': 'MintAndWithdraw(address,uint256,address,uint256)',
    'OFTSent': 'OFTSent(bytes32,uint32,address,uint256,uint256)',
    'OFTReceived': 'OFTReceived(bytes32,uint32,address,uint256)',
    'WETHDeposit': 'Deposit(address,uint256)',
    'WETHWithdrawal': 'Withdrawal(address,uint256)',
    'LidoSubmitted': 'Submitted(address,uint256,address)',
    'LidoWithdrawalRequested': 'WithdrawalRequested(uint256,address,address,uint256,uint256)',
    'EthenaCooldown': 'Withdraw(address,address,address,uint256,uint256)',  # ERC4626 Withdraw shape; used at sUSDe only
    'USDCMint': 'Mint(address,address,uint256)',
    'USDCBurn': 'Burn(address,uint256)',
    'TetherIssue': 'Issue(uint256)',
    'TetherRedeem': 'Redeem(uint256)',
    'CoWTrade': 'Trade(address,address,address,uint256,uint256,uint256,bytes)',
    'UniXFill': 'Fill(bytes32,address,address,uint256)',
    'OneInchFilled': 'OrderFilled(bytes32,uint256)',
}.items()}
BY_TOPIC = {v: k for k, v in T.items()}
SEL = {name: sel(sig) for name, sig in {
    'symbol': 'symbol()', 'decimals': 'decimals()', 'name': 'name()', 'totalSupply': 'totalSupply()', 'balanceOf': 'balanceOf(address)',
    'token0': 'token0()', 'token1': 'token1()', 'fee': 'fee()', 'coins': 'coins(uint256)', 'latestRoundData': 'latestRoundData()',
    'description': 'description()', 'getUserAccountData': 'getUserAccountData(address)', 'getReserveData': 'getReserveData(address)',
    'idToMarketParams': 'idToMarketParams(bytes32)', 'getUtilization': 'getUtilization()', 'getSupplyRate': 'getSupplyRate(uint256)',
    'getBorrowRate': 'getBorrowRate(uint256)', 'baseToken': 'baseToken()', 'ssr': 'ssr()', 'dsr': 'dsr()', 'vestingAmount': 'vestingAmount()',
    'totalAssets': 'totalAssets()', 'getOptimalUsageRatio': 'getOptimalUsageRatio()', 'getVariableRateSlope1': 'getVariableRateSlope1()',
    'getVariableRateSlope2': 'getVariableRateSlope2()', 'getMaxVariableBorrowRate': 'getMaxVariableBorrowRate()',
}.items()}
RAY = 10 ** 27
Q96 = 2 ** 96


def short(a):
    return a[:6] + '…' + a[-4:]


def link_addr(a, label=None):
    return '[%s](%s/address/%s)' % (label or short(a), EXPLORER, a)


def link_tx(h):
    return '[%s](%s/tx/%s)' % (short(h), EXPLORER, h)


def usd_fmt(v):
    if v is None:
        return '–'
    a = abs(v)
    s = '$%.1fB' % (v / 1e9) if a >= 1e9 else '$%.1fM' % (v / 1e6) if a >= 1e6 else '$%.0fk' % (v / 1e3) if a >= 1e4 else '$%.0f' % v
    return s


def pct(v, d=2):
    return '–' if v is None else ('%.' + str(d) + 'f%%') % (100 * v)


def bps(v, d=1):
    return '–' if v is None else ('%+.' + str(d) + 'f bps') % (1e4 * v)


# ----------------------------------------------------------------------------------------------------------------------
# Prices
# ----------------------------------------------------------------------------------------------------------------------
class Prices:
    """USD per whole token by price key, from head_state.json (Chainlink feeds + NAV rates); parity for plain stables."""

    def __init__(self, head_state=None):
        self.usd = {'USD': 1.0}
        self.meta = {}
        hs = head_state or {}
        for k, v in (hs.get('feeds') or {}).items():
            if v.get('usd'):
                self.usd[k] = float(v['usd'])
        for k, v in (hs.get('rates') or {}).items():
            base = self.usd.get(v.get('underlying'))
            if v.get('rate') and base:
                self.usd[k] = float(v['rate']) * base
        self.extra = hs.get('tokens') or {}
        for k in ('USDC', 'USDT', 'DAI'):
            self.usd.setdefault(k, 1.0)

    def token(self, addr):
        """(symbol, decimals, price_usd_per_token or None)"""
        t = TOKENS.get(addr)
        if t:
            s, d, k = t
            return s, d, self.usd.get(k)
        x = self.extra.get(addr)
        if x and x.get('decimals') is not None:
            return x.get('symbol') or short(addr), int(x['decimals']), None
        return None

    def value(self, addr, raw):
        t = self.token(addr)
        if not t or t[2] is None:
            return None
        return raw / 10 ** t[1] * t[2]


# ----------------------------------------------------------------------------------------------------------------------
# Address book
# ----------------------------------------------------------------------------------------------------------------------
def load_address_book():
    """hot wallets and deposit sinks derived from the day study's behaviour profiles, plus memory labels.

    The deposit-sink rule used to read `sent == 0`, meaning "originated no transactions". Every *contract* satisfies that
    structurally, because contracts do not originate transactions, so the rule reduced to "a busy contract" and tagged 25
    addresses of which 22 forwarded value — among them the CoW settlement contract, the Uniswap Universal Router and a
    LI.FI-style bridge aggregator. Their flow was then counted as exchange flow and their receipt of borrow proceeds as
    leverage-to-exchange.

    A deposit sink is defined by *not forwarding*, so the rule now tests that directly: many distinct senders, at most a
    couple of distinct recipients, and a large in/out fan ratio. That is a candidate generator, not an identity claim, so
    every entry it produces is tagged `behaviour-day-study` and sits at the weakest provenance tier.
    """
    book = {}
    if DAY_PROFILES.exists():
        prof = json.load(__import__('gzip').open(DAY_PROFILES, 'rt'))
        for a, v in prof.items():
            if a in NOT_EXCHANGES or v.get('pool_swaps'):
                continue
            out_to = v.get('out_to_distinct', 0)
            if v['sent'] >= 100 and v['to_distinct'] >= 50 and float(v['big_usd']) >= 5e6:
                book[a] = {'tag': 'hot_wallet', 'kind': 'exchange', 'source': 'behaviour-day-study',
                           'label': MEMORY_LABELS.get(a, 'hot wallet (behaviour, day study)')}
            elif (v['in_from_distinct'] >= 200 and out_to <= 2 and v['in_from_distinct'] >= 50 * max(out_to, 1)
                  and float(v['big_usd']) >= 20e6):
                book[a] = {'tag': 'deposit_sink', 'kind': 'exchange_deposit', 'source': 'behaviour-day-study',
                           'label': MEMORY_LABELS.get(a, 'deposit sink (behaviour, day study)')}
    for a, l in MEMORY_LABELS.items():
        book.setdefault(a, {'tag': 'hot_wallet', 'kind': 'exchange', 'source': 'model-memory', 'label': l + ' (memory)'})
        if a in MEMORY_LABELS and '(memory)' not in book[a]['label'] and 'day study' not in book[a]['label']:
            book[a]['label'] = l + ' (memory)'
    # verified/typed overlay (scripts/address_labels.json): overrides behavioural + memory tags and carries a `kind`.
    # A settlement contract or token treasury tagged here as venue/protocol/treasury stops being counted as a CEX.
    if VERIFIED_LABELS.exists():
        try:
            vl = json.loads(VERIFIED_LABELS.read_text()).get('labels', {})
        except Exception:
            vl = {}
        import labels as _labels
        for a, v in vl.items():
            a = a.lower()
            kind, src = v.get('kind'), v.get('source', 'verified')
            old = book.get(a)
            # A registry entry wins unless the book already holds a *stronger* claim, so a behaviour-tier row cannot
            # overwrite a verified one. Every entry keeps its source, which is what lets `verify` report the band.
            if old and _labels.tier_rank(old.get('source')) < _labels.tier_rank(src):
                continue
            book[a] = {'tag': KIND_TAG.get(kind, 'labelled'), 'kind': kind, 'source': src,
                       'label': '%s (%s)' % (v.get('label', a), src)}
    return book


# ----------------------------------------------------------------------------------------------------------------------
# Decoding one block
# ----------------------------------------------------------------------------------------------------------------------
def tip_of(t, base_fee):
    if t.get('maxPriorityFeePerGas') is not None:
        return max(0, min(hx(t['maxPriorityFeePerGas']), hx(t['maxFeePerGas']) - base_fee))
    return max(0, hx(t.get('gasPrice', 0)) - base_fee)


def extra_data_text(b):
    try:
        raw = bytes.fromhex(b.get('extraData', '0x')[2:])
        s = raw.decode('utf-8', 'ignore')
        return ''.join(ch for ch in s if 32 <= ord(ch) < 127)[:40]
    except Exception:
        return ''


class State:
    """Aggregates over a range of blocks. Built in one pass by `ingest`; summarised by `finish`."""

    def __init__(self, prices, book, pools_cache=None, market_cache=None):
        self.p = prices
        self.book = book
        self.pool_tokens = dict(pools_cache or {})   # pool -> [t0, t1] (v2/v3/curve inferred; v4 by poolId)
        self.pool_fee = {}                            # pool -> fee fraction (v3 from cache; v4 from event)
        self.pool_hook = {}                           # v4 poolId -> hook address (address(0) when none)
        self.unconfirmed_v4 = collections.Counter()   # hooked pools whose reported deltas exceeded confirmed token movements
        self.pool_venue = {}
        self.markets = dict(market_cache or {})      # morpho id -> {loan, collateral, lltv}
        self.blocks = []
        self.transfers = []       # priced ERC-20/native legs >= $10k: dict
        self.swaps = []           # priced swaps: dict
        self.pools = collections.defaultdict(lambda: {'n': 0, 'vol': 0.0, 'fee': 0.0, 'fee_jit': 0.0, 'cap_sum': 0.0, 'cap_n': 0, 'px': [], 'jit_n': 0, 'lp_in': 0.0, 'lp_out': 0.0})
        self.jit = []             # episodes
        self.rates = collections.defaultdict(list)   # (venue, reserve) -> [(block, ts, supply_apr, borrow_apr)]
        self.lending = []         # ops
        self.liquidations = []
        self.flash = collections.Counter()
        self.flash_usd = collections.Counter()
        self.bridges = []         # cctp / oft sends
        self.bridge_in = []       # cctp mints / oft received
        self.weth = collections.Counter()
        self.issuance = []
        self.lido = collections.Counter()
        self.cooldowns = []
        self.by_sender = collections.Counter()
        self.gas_by_sender = collections.Counter()
        self.gas_by_to = collections.Counter()
        self.unknown_topics = collections.Counter()
        self.unpriced_tokens = collections.Counter()
        self.intent_fills = collections.Counter()
        self.peg = collections.defaultdict(list)     # symbol -> [(usd_ref, amount, block, venue)]
        self.first_ts = None
        self.last_ts = None
        self.n_tx = 0
        self.n_logs = 0
        self.v4_counts = collections.Counter()

    # -- helpers ---------------------------------------------------------------------------------------------------------
    def tag(self, a):
        b = self.book.get(a)
        return b['tag'] if b else None

    def label(self, a):
        b = self.book.get(a)
        return b['label'] if b else None

    def is_exchange(self, a):
        """True only for centralized-exchange wallets/deposit addresses. Verified overlay `kind` decides; legacy
        behavioural/memory entries (no kind) keep their hot_wallet/deposit_sink meaning."""
        b = self.book.get(a)
        if not b:
            return False
        k = b.get('kind')
        if k is None:
            return b['tag'] in ('hot_wallet', 'deposit_sink')
        return k in EXCHANGE_KINDS

    def infer_pool_tokens(self, pool, tx_transfers, amt0, amt1, manager=None):
        """v3/v2/curve/v4: match token transfers into/out of the pool (or the v4 manager) in the same tx with the swap amounts."""
        known = self.pool_tokens.get(pool)
        if known and all(known):
            return known
        t0, t1 = (known or [None, None])
        target = manager or pool
        ins = [(l['token'], l['raw']) for l in tx_transfers if l['to'] == target]
        outs = [(l['token'], l['raw']) for l in tx_transfers if l['from'] == target]
        if manager and amt0 and t1 and not t0:
            pass
        for idx, amt in ((0, amt0), (1, amt1)):
            if amt == 0:
                continue
            cands = ins if amt > 0 else outs
            match = [tok for tok, raw in cands if raw == abs(amt)]
            if len(set(match)) == 1:
                if idx == 0:
                    t0 = match[0]
                else:
                    t1 = match[0]
        if manager and t1 and not t0 and amt0 and not [tok for tok, raw in (ins if amt0 > 0 else outs) if raw == abs(amt0)]:
            t0 = '0x' + '0' * 40  # v4 native ETH pool: currency0 is address(0)
        if t0 and t1 and t0 > t1:
            t0, t1 = None, None  # inconsistent (token0 must sort below token1)
        if t0 or t1:
            self.pool_tokens[pool] = [t0, t1]
        return [t0, t1]

    def price_swap(self, tok_in, raw_in, tok_out, raw_out, confirmed=None):
        """Return (usd, reference_side, implied prices dict) using the most trusted priced side."""
        best = None
        for side, tok, raw in (('in', tok_in, raw_in), ('out', tok_out, raw_out)):
            t = self.p.token(tok) if tok else None
            if not t or t[2] is None:
                continue
            if confirmed is not None and confirmed.get(tok) is False:
                continue
            key = TOKENS[tok][2] if tok in TOKENS else 'X'
            rank = REFERENCE_ORDER.index(key) if key in REFERENCE_ORDER else 9
            usd = raw / 10 ** t[1] * t[2]
            if best is None or rank < best[0]:
                best = (rank, side, usd, t[0])
        if not best:
            return None, None, {}
        rank, side, usd, sym = best
        implied = {}
        other_tok, other_raw = (tok_out, raw_out) if side == 'in' else (tok_in, raw_in)
        if other_tok and other_raw:
            ot = self.p.token(other_tok)
            if ot and other_tok != (tok_in if side == 'in' else tok_out):
                implied[other_tok] = (usd / (other_raw / 10 ** ot[1]), ot[0])
        return usd, side, implied

    # -- ingest ------------------------------------------------------------------------------------------------------------
    def ingest(self, b, logs):
        n, ts = hx(b['number']), hx(b['timestamp'])
        base = hx(b.get('baseFeePerGas', 0))
        txs = b['transactions']
        self.first_ts = ts if self.first_ts is None else min(self.first_ts, ts)
        self.last_ts = ts if self.last_ts is None else max(self.last_ts, ts)
        self.n_tx += len(txs)
        self.n_logs += len(logs)
        eth = self.p.usd.get('ETH')
        tips = [tip_of(t, base) for t in txs]
        self.blocks.append({'n': n, 'ts': ts, 'base_gwei': base / 1e9, 'gas_used': hx(b['gasUsed']), 'gas_limit': hx(b['gasLimit']), 'txs': len(txs),
                            'builder': extra_data_text(b), 'miner': b['miner'].lower(),
                            'tip_med_gwei': statistics.median(tips) / 1e9 if tips else 0, 'zero_tip': sum(1 for x in tips if x == 0),
                            'blob_gas': hx(b.get('blobGasUsed', 0))})
        by_tx = collections.defaultdict(list)
        for l in logs:
            by_tx[l['transactionHash']].append(l)
        txmap = {t['hash']: t for t in txs}
        for t in txs:
            frm = t['from'].lower()
            self.by_sender[frm] += 1
            self.gas_by_sender[frm] += hx(t['gas'])
            if t.get('to'):
                self.gas_by_to[t['to'].lower()] += hx(t['gas'])
            v = hx(t.get('value', 0))
            if v and eth and t.get('to'):
                usd = v / 1e18 * eth
                if usd >= 1e4:
                    self.transfers.append({'block': n, 'ts': ts, 'tx': t['hash'], 'token': NATIVE, 'sym': 'ETH', 'from': frm, 'to': t['to'].lower(), 'raw': v, 'usd': usd, 'li': -1})
        for h, tlogs in by_tx.items():
            t = txmap.get(h)
            if t is None:
                continue
            self.ingest_tx(n, ts, t, tlogs)

    def ingest_tx(self, n, ts, t, tlogs):
        sender = t['from'].lower()
        tx_transfers = []
        # pass 1: ERC-20 transfers (needed to identify pool tokens and follow proceeds)
        for l in tlogs:
            tp = l['topics']
            if tp and tp[0] == T['Transfer'] and len(tp) == 3 and len(l['data']) >= 66:
                tok = l['address'].lower()
                leg = {'token': tok, 'from': topic_addr(tp[1]), 'to': topic_addr(tp[2]), 'raw': word(l['data'], 0), 'li': hx(l['logIndex'])}
                tx_transfers.append(leg)
        for leg in tx_transfers:
            tk = self.p.token(leg['token'])
            if not tk:
                self.unpriced_tokens[leg['token']] += 1
                continue
            usd = self.p.value(leg['token'], leg['raw'])
            if usd is not None and usd >= 1e4:
                self.transfers.append({'block': n, 'ts': ts, 'tx': t['hash'], 'token': leg['token'], 'sym': tk[0], 'from': leg['from'], 'to': leg['to'], 'raw': leg['raw'], 'usd': usd, 'li': leg['li']})
        # pass 2: protocol events
        jit_mints = {}
        for l in tlogs:
            tp = l['topics']
            if not tp:
                continue
            name = BY_TOPIC.get(tp[0])
            addr = l['address'].lower()
            d = l['data']
            li = hx(l['logIndex'])
            if name is None:
                self.unknown_topics[tp[0]] += 1
                continue
            if name == 'Transfer':
                continue
            if name == 'V3Swap' and len(tp) == 3:
                a0, a1 = sword(d, 0), sword(d, 1)
                sqrtp, L, tick = word(d, 2), word(d, 3), sword(d, 4, 256)
                toks = self.infer_pool_tokens(addr, tx_transfers, a0, a1)
                self.record_swap(n, ts, t, li, 'uniswap_v3', addr, toks, a0, a1, sqrtp, L, self.pool_fee.get(addr), sender)
            elif name == 'V4Swap' and len(tp) == 3:
                pid = tp[1]
                a0, a1 = sword(d, 0, 128) if word(d, 0) < 2 ** 255 else sword(d, 0), sword(d, 1, 128) if word(d, 1) < 2 ** 255 else sword(d, 1)
                # amounts are int128 sign-extended to 256 bits in the ABI encoding
                a0, a1 = sword(d, 0), sword(d, 1)
                sqrtp, L, fee = word(d, 2), word(d, 3), word(d, 5)
                self.v4_counts[pid] += 1
                toks = self.pool_tokens.get(pid, [None, None])
                if not all(toks):
                    # settle/take move ERC-20s to and from the PoolManager; native ETH is currency0 = address(0) and has no log
                    toks = self.infer_pool_tokens(pid, [x for x in tx_transfers if V4_MANAGER in (x['to'], x['from'])], -a0, -a1, manager=V4_MANAGER)
                # v4 deltas are from the caller's view: negative = paid into the pool. Convert to v3 convention.
                self.pool_fee[pid] = fee / 1e6
                # A hook can return deltas and settle them as ERC-6909 claims, so the event's amounts need not have moved outside the
                # PoolManager. Value the swap only from a leg whose tokens verifiably entered or left the manager in this transaction:
                # an ERC-20 transfer to/from the manager, or for native ETH the transaction value plus WETH wrapped/unwrapped.
                confirmed = {}
                for tok, amt in ((toks[0], a0), (toks[1], a1)):
                    if not tok or not amt:
                        continue
                    if tok == '0x' + '0' * 40:
                        eth_cap = hx(t.get('value', 0)) + sum(word(l['data'], 0) for l in tlogs if l['topics'] and l['address'].lower() == WETH and l['topics'][0] in (T['WETHWithdrawal'], T['WETHDeposit']))
                        confirmed[tok] = abs(amt) <= eth_cap * 1.001 + 10 ** 15
                    else:
                        moved = sum(x['raw'] for x in tx_transfers if x['token'] == tok and V4_MANAGER in (x['to'], x['from']))
                        confirmed[tok] = abs(amt) <= moved * 1.001 + 1
                if all(toks) and not any(confirmed.get(tok) for tok in toks if self.p.token(tok) and self.p.token(tok)[2] is not None):
                    self.unconfirmed_v4[pid] += 1
                    continue
                self.record_swap(n, ts, t, li, 'uniswap_v4', pid, toks, -a0, -a1, sqrtp, L, fee / 1e6, sender, confirmed=confirmed)
            elif name == 'V2Swap' and len(tp) == 3:
                a0in, a1in, a0out, a1out = word(d, 0), word(d, 1), word(d, 2), word(d, 3)
                a0, a1 = a0in - a0out, a1in - a1out
                toks = self.infer_pool_tokens(addr, tx_transfers, a0, a1)
                self.record_swap(n, ts, t, li, 'uniswap_v2_like', addr, toks, a0, a1, None, None, self.pool_fee.get(addr, 0.003), sender)
            elif name in ('CurveEx', 'CurveExU', 'CurveExUnd') and len(tp) == 2:
                sold_i, sold, bought_i, bought = word(d, 0), word(d, 1), word(d, 2), word(d, 3)
                ins = [x for x in tx_transfers if x['to'] == addr and x['raw'] == sold]
                outs = [x for x in tx_transfers if x['from'] == addr and x['raw'] == bought]
                tok_in = ins[0]['token'] if len({x['token'] for x in ins}) == 1 else None
                tok_out = outs[0]['token'] if len({x['token'] for x in outs}) == 1 else None
                self.record_generic_swap(n, ts, t, li, 'curve', addr, tok_in, sold, tok_out, bought, sender)
            elif name == 'BalSwap' and len(tp) == 4:
                tok_in, tok_out = topic_addr(tp[2]), topic_addr(tp[3])
                self.record_generic_swap(n, ts, t, li, 'balancer', tp[1][:18], tok_in, word(d, 0), tok_out, word(d, 1), sender)
            elif name == 'V3Mint' and len(tp) == 4:
                owner, lo, hi = topic_addr(tp[1]), topic_int(tp[2]), topic_int(tp[3])
                L = word(d, 1)
                key = (addr, owner, lo, hi, L)
                jit_mints[key] = li
                self.lp_change(n, ts, t, addr, 'mint', L, word(d, 2), word(d, 3), owner, lo, hi, li)
            elif name == 'V3Burn' and len(tp) == 4:
                owner, lo, hi = topic_addr(tp[1]), topic_int(tp[2]), topic_int(tp[3])
                L = word(d, 0)
                self.lp_change(n, ts, t, addr, 'burn', L, word(d, 1), word(d, 2), owner, lo, hi, li)
            elif name == 'V4Modify' and len(tp) == 3:
                pid, owner = tp[1], topic_addr(tp[2])
                lo, hi, dL = sword(d, 0), sword(d, 1), sword(d, 2)
                self.lp_change(n, ts, t, pid, 'mint' if dL > 0 else 'burn', abs(dL), None, None, owner, lo, hi, li, salt=d[2 + 64 * 3:2 + 64 * 4])
            elif name == 'V4Init' and len(tp) == 4:
                self.pool_tokens[tp[1]] = [topic_addr(tp[2]), topic_addr(tp[3])]
                self.pool_fee[tp[1]] = word(d, 0) / 1e6
                self.pool_hook[tp[1]] = '0x' + d[2 + 64 * 2:2 + 64 * 3][-40:]
            elif addr in LENDING_POOLS and name.startswith('Aave'):
                self.aave_event(n, ts, t, addr, name, tp, d, li)
            elif addr == MORPHO and name.startswith('Morpho'):
                self.morpho_event(n, ts, t, name, tp, d, li)
            elif name in ('MorphoFlash', 'BalFlash', 'AaveFlash'):
                tok = topic_addr(tp[2]) if name == 'AaveFlash' and len(tp) >= 3 else (topic_addr(tp[2]) if name == 'MorphoFlash' and len(tp) == 3 else (topic_addr(tp[2]) if len(tp) >= 3 else None))
                amt = word(d, 0)
                usd = self.p.value(tok, amt) if tok else None
                self.flash[name] += 1
                if usd:
                    self.flash_usd[name] += usd
            elif name in ('CCTP1', 'CCTP2'):
                amt, dom = word(d, 0), word(d, 2)
                recipient = '0x' + d[2 + 64:2 + 128][-40:] if dom not in (5, 4, 8, 9) else d[2 + 64:2 + 128]
                usd = amt / 1e6
                self.bridges.append({'block': n, 'ts': ts, 'tx': t['hash'], 'kind': 'CCTP', 'token': 'USDC', 'usd': usd, 'dst': dom, 'dst_name': CCTP_DOMAINS.get(dom, 'domain %d' % dom),
                                     'recipient': recipient, 'sender': sender})
            elif name in ('CCTPMint1', 'CCTPMint2'):
                self.bridge_in.append({'block': n, 'kind': 'CCTP', 'usd': word(d, 0) / 1e6, 'recipient': topic_addr(tp[1]) if len(tp) > 1 else None})
            elif name == 'OFTSent' and len(tp) == 3:
                eid, amt = word(d, 0), word(d, 1)
                tok = OFT_ADAPTERS.get(addr)
                tok_addr = None
                if tok is None:
                    cands = [x['token'] for x in tx_transfers if x['raw'] == amt and (x['to'] == addr or x['to'] == '0x' + '0' * 40)]
                    if cands:
                        tok_addr = cands[0]
                        tk = self.p.token(tok_addr)
                        tok = tk[0] if tk else short(tok_addr)
                    elif addr in TOKENS:
                        tok, tok_addr = TOKENS[addr][0], addr
                usd = None
                src = tok_addr or next((a for a, (s, _, _) in TOKENS.items() if s == tok), None)
                if src:
                    usd = self.p.value(src, amt)
                self.bridges.append({'block': n, 'ts': ts, 'tx': t['hash'], 'kind': 'OFT', 'token': tok or short(addr), 'usd': usd, 'dst': eid, 'dst_name': LZ_EIDS.get(eid, 'eid %d' % eid),
                                     'recipient': None, 'sender': sender, 'adapter': addr})
            elif name == 'OFTReceived':
                pass
            elif name == 'WETHDeposit' and addr == WETH:
                self.weth['wrap'] += word(d, 0) / 1e18
            elif name == 'WETHWithdrawal' and addr == WETH:
                self.weth['unwrap'] += word(d, 0) / 1e18
            elif name == 'LidoSubmitted' and addr == '0xae7ab96520de3a18e5e111b5eaab095312d7fe84':
                self.lido['stake_eth'] += word(d, 0) / 1e18
            elif name == 'LidoWithdrawalRequested' and len(tp) == 4:
                self.lido['unstake_eth'] += word(d, 0) / 1e18
            elif name == 'USDCMint' and addr == '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48':
                self.issuance.append({'block': n, 'ts': ts, 'tx': t['hash'], 'token': 'USDC', 'kind': 'mint', 'usd': word(d, 0) / 1e6, 'to': topic_addr(tp[2]) if len(tp) > 2 else None})
            elif name == 'USDCBurn' and addr == '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48':
                self.issuance.append({'block': n, 'ts': ts, 'tx': t['hash'], 'token': 'USDC', 'kind': 'burn', 'usd': word(d, 0) / 1e6, 'to': topic_addr(tp[1]) if len(tp) > 1 else None})
            elif name in ('TetherIssue', 'TetherRedeem') and addr == '0xdac17f958d2ee523a2206206994597c13d831ec7':
                self.issuance.append({'block': n, 'ts': ts, 'tx': t['hash'], 'token': 'USDT', 'kind': 'mint' if name == 'TetherIssue' else 'burn', 'usd': word(d, 0) / 1e6, 'to': None})
            elif name == 'EthenaCooldown' and addr == '0x9d39a5de30e57443bff2a8307a4256c8797a3497':
                self.cooldowns.append({'block': n, 'usd': word(d, 0) / 1e18, 'owner': topic_addr(tp[3]) if len(tp) > 3 else None})
            elif name in ('CoWTrade', 'UniXFill', 'OneInchFilled'):
                self.intent_fills[name] += 1

    def record_generic_swap(self, n, ts, t, li, venue, pool, tok_in, raw_in, tok_out, raw_out, sender):
        usd, side, implied = self.price_swap(tok_in, raw_in, tok_out, raw_out)
        if usd is None:
            return
        ps = self.pools[pool]
        ps['n'] += 1
        ps['vol'] += usd
        self.pool_venue[pool] = venue
        if not self.pool_tokens.get(pool) and tok_in and tok_out:
            self.pool_tokens[pool] = sorted([tok_in, tok_out])
        for tok, (px, sym) in implied.items():
            self.peg[sym].append((usd, px, n, venue))
        self.swaps.append({'block': n, 'ts': ts, 'tx': t['hash'], 'li': li, 'venue': venue, 'pool': pool, 'sender': sender, 'to': (t.get('to') or '').lower(),
                           'tok_in': tok_in, 'tok_out': tok_out, 'raw_in': raw_in, 'raw_out': raw_out, 'usd': usd, 'implied': {k: v[0] for k, v in implied.items()}})

    def record_swap(self, n, ts, t, li, venue, pool, toks, a0, a1, sqrtp, L, fee, sender, confirmed=None):
        t0, t1 = toks if toks else (None, None)
        if a0 > 0:
            tok_in, raw_in, tok_out, raw_out = t0, a0, t1, -a1
        else:
            tok_in, raw_in, tok_out, raw_out = t1, a1, t0, -a0
        usd, side, implied = self.price_swap(tok_in, raw_in, tok_out, raw_out, confirmed)
        if confirmed is not None:
            implied = {k: v for k, v in implied.items() if confirmed.get(k) is not False}
        self.pool_venue[pool] = venue
        if usd is None:
            return
        ps = self.pools[pool]
        ps['n'] += 1
        ps['vol'] += usd
        fee_usd = usd * fee if fee else None
        if fee_usd:
            ps['fee'] += fee_usd
        cap = None
        if sqrtp and L and t0 and t1:
            # full-range-equivalent capital for liquidity L: 2*L*sqrtP in token1 raw units, or 2*L/sqrtP in token0 raw units
            sp = sqrtp / Q96
            for tok, amount_raw in ((t1, 2 * L * sp), (t0, 2 * L / sp if sp else 0)):
                v = self.p.value(tok, amount_raw) if tok else None
                if v:
                    cap = v
                    break
            if cap:
                ps['cap_sum'] += cap
                ps['cap_n'] += 1
            tk1 = self.p.token(t1) if t1 else None
            tk0 = self.p.token(t0) if t0 else None
            if tk0 and tk1:
                ps['px'].append((n, sp * sp * 10 ** (tk0[1] - tk1[1])))  # token1 per token0, whole units
        for tok, (px, sym) in implied.items():
            self.peg[sym].append((usd, px, n, venue))
        self.swaps.append({'block': n, 'ts': ts, 'tx': t['hash'], 'li': li, 'venue': venue, 'pool': pool, 'sender': sender, 'to': (t.get('to') or '').lower(),
                           'tok_in': tok_in, 'tok_out': tok_out, 'raw_in': raw_in, 'raw_out': raw_out, 'usd': usd, 'fee_usd': fee_usd, 'L': L, 'sqrtp': sqrtp, 'cap': cap,
                           'implied': {k: v[0] for k, v in implied.items()}})

    def lp_change(self, n, ts, t, pool, kind, L, a0, a1, owner, lo, hi, li, salt=None):
        ps = self.pools[pool]
        toks = self.pool_tokens.get(pool)
        usd = None
        if toks and a0 is not None:
            v0 = self.p.value(toks[0], a0) if toks[0] else None
            v1 = self.p.value(toks[1], a1) if toks[1] else None
            if v0 is not None or v1 is not None:
                usd = (v0 or 0) + (v1 or 0)
        if usd:
            ps['lp_in' if kind == 'mint' else 'lp_out'] += usd
        self.jit.append({'block': n, 'ts': ts, 'tx': t['hash'], 'pool': pool, 'kind': kind, 'L': L, 'owner': owner, 'lo': lo, 'hi': hi, 'li': li, 'usd': usd, 'sender': t['from'].lower(), 'salt': salt})

    def aave_event(self, n, ts, t, pool, name, tp, d, li):
        venue = LENDING_POOLS[pool]
        if len(tp) < 2:
            return
        if name == 'AaveRDU' and len(tp) == 2:
            reserve = topic_addr(tp[1])
            self.rates[(venue, reserve)].append((n, ts, word(d, 0) / RAY, word(d, 2) / RAY))
            return
        if name == 'AaveLiq' and len(tp) == 4:
            col, debt, user = topic_addr(tp[1]), topic_addr(tp[2]), topic_addr(tp[3])
            self.liquidations.append({'block': n, 'ts': ts, 'tx': t['hash'], 'venue': venue, 'user': user, 'collateral': col, 'debt': debt,
                                      'debt_usd': self.p.value(debt, word(d, 0)), 'collateral_usd': self.p.value(col, word(d, 1)), 'liquidator': '0x' + d[2 + 128:2 + 192][-40:]})
            return
        if name == 'AaveFlash':
            return
        reserve = topic_addr(tp[1])
        if len(tp) < 3 or len(d) < 66:
            return
        if name == 'AaveSupply':
            user, onb, amt = '0x' + d[2:66][-40:], topic_addr(tp[2]), word(d, 1)
            recv = None
        elif name == 'AaveBorrow':
            user, onb, amt = '0x' + d[2:66][-40:], topic_addr(tp[2]), word(d, 1)
            recv = user
        elif name == 'AaveRepay':
            user, onb, amt = topic_addr(tp[2]), topic_addr(tp[2]), word(d, 0)
            recv = None
        elif name == 'AaveWithdraw':
            user, onb, amt = topic_addr(tp[2]), topic_addr(tp[2]), word(d, 0)
            recv = topic_addr(tp[3])
        else:
            return
        tk = self.p.token(reserve)
        self.lending.append({'block': n, 'ts': ts, 'tx': t['hash'], 'venue': venue, 'kind': name[4:].lower(), 'reserve': reserve, 'sym': tk[0] if tk else short(reserve),
                             'user': user, 'account': onb, 'receiver': recv, 'raw': amt, 'usd': self.p.value(reserve, amt), 'sender': t['from'].lower(), 'li': li})

    def morpho_event(self, n, ts, t, name, tp, d, li):
        if len(tp) != 4:
            return
        mid = tp[1]
        mk = self.markets.get(mid) or {}
        if name == 'MorphoLiq':
            self.liquidations.append({'block': n, 'ts': ts, 'tx': t['hash'], 'venue': 'Morpho Blue', 'user': topic_addr(tp[3]), 'collateral': mk.get('collateral'), 'debt': mk.get('loan'),
                                      'debt_usd': self.p.value(mk['loan'], word(d, 0)) if mk.get('loan') else None, 'collateral_usd': self.p.value(mk['collateral'], word(d, 2)) if mk.get('collateral') else None,
                                      'liquidator': topic_addr(tp[2]), 'market': mid})
            return
        kind = name[6:].lower()
        if kind in ('withdraw', 'borrow'):
            # Withdraw/Borrow(id indexed, caller, onBehalf indexed, receiver indexed, assets, shares)
            user, account, recv, amt = '0x' + d[2:66][-40:], topic_addr(tp[2]), topic_addr(tp[3]), word(d, 1)
        else:
            # Supply/Repay(id indexed, caller indexed, onBehalf indexed, assets, shares)
            user, account, recv, amt = topic_addr(tp[2]), topic_addr(tp[3]), None, word(d, 0)
        loan = mk.get('loan')
        tk = self.p.token(loan) if loan else None
        self.lending.append({'block': n, 'ts': ts, 'tx': t['hash'], 'venue': 'Morpho Blue', 'kind': kind, 'reserve': loan, 'sym': tk[0] if tk else 'market ' + mid[:10],
                             'user': user, 'account': account, 'receiver': recv, 'raw': amt, 'usd': self.p.value(loan, amt) if loan else None,
                             'sender': t['from'].lower(), 'li': li, 'market': mid})

    # -- summaries ---------------------------------------------------------------------------------------------------------
    def finish(self):
        hours = max(1e-9, (self.last_ts - self.first_ts + 12) / 3600) if self.blocks else 1e-9
        out = {'window': {'first_block': self.blocks[0]['n'] if self.blocks else None, 'last_block': self.blocks[-1]['n'] if self.blocks else None,
                          'first_utc': utc(self.first_ts) if self.first_ts else None, 'last_utc': utc(self.last_ts) if self.last_ts else None,
                          'hours': round(hours, 3), 'blocks': len(self.blocks), 'transactions': self.n_tx, 'logs': self.n_logs}}
        out['gas'] = self.gas_summary()
        out['jit'] = self.jit_summary()
        out['lp'] = self.lp_summary(hours)
        out['lending_rates'] = self.rates_summary()
        out['lending_ops'] = self.lending_summary()
        out['liquidations'] = self.liquidations
        out['flash'] = {'count': dict(self.flash), 'usd': {k: round(v) for k, v in self.flash_usd.items()}}
        out['exchange_flow'] = self.exchange_flow()
        roll = collections.OrderedDict()
        for x in sorted([x for x in self.transfers if x['usd'] >= 5e6], key=lambda x: -x['usd']):
            k = (x['sym'], x['from'], x['to'], round(x['usd'], -4))
            if k in roll:
                roll[k]['count'] += 1
            else:
                roll[k] = dict(x, count=1)
        out['big_transfers'] = list(roll.values())[:80]
        out['round_trips'] = self.round_trips()
        out['scheduled'] = self.scheduled_flow()
        out['peg'] = self.peg_summary()
        out['bridges'] = self.bridge_summary()
        out['weth'] = {k: round(v, 2) for k, v in self.weth.items()}
        out['lido'] = {k: round(v, 2) for k, v in self.lido.items()}
        iss = collections.defaultdict(lambda: {'n': 0, 'usd': 0.0})
        for i in self.issuance:
            iss[i['token'] + ' ' + i['kind']]['n'] += 1
            iss[i['token'] + ' ' + i['kind']]['usd'] += i['usd']
        out['issuance'] = {'totals': {k: {'n': v['n'], 'usd': round(v['usd'])} for k, v in iss.items()}, 'largest': sorted(self.issuance, key=lambda i: -i['usd'])[:10]}
        out['cooldowns'] = {'n': len(self.cooldowns), 'usd': round(sum(c['usd'] for c in self.cooldowns))}
        out['intent_fills'] = dict(self.intent_fills)
        out['top_senders'] = [{'address': a, 'txs': c, 'label': self.label(a)} for a, c in self.by_sender.most_common(25)]
        out['top_gas_targets'] = [{'address': a, 'gas': g} for a, g in self.gas_by_to.most_common(15)]
        out['unknown_topics'] = self.unknown_topics.most_common(30)
        out['unpriced_tokens'] = self.unpriced_tokens.most_common(40)
        out['swap_totals'] = self.swap_totals()
        out['v4_pool_counts'] = dict(self.v4_counts.most_common(400))
        out['v4_unconfirmed'] = [{'pool': p, 'swaps': c, 'hook': self.pool_hook.get(p), 'tokens': self.pool_tokens.get(p)} for p, c in self.unconfirmed_v4.most_common(10)]
        out['atomic_cycles'] = self.atomic_cycles()
        out['big_swaps'] = sorted([{k: v for k, v in s.items() if k not in ('L', 'sqrtp')} for s in self.swaps if s['usd'] >= 1e6], key=lambda s: -s['usd'])[:60]
        return out

    def gas_summary(self):
        if not self.blocks:
            return {}
        bf = [b['base_gwei'] for b in self.blocks]
        return {'base_fee_gwei': {'min': round(min(bf), 3), 'median': round(statistics.median(bf), 3), 'max': round(max(bf), 3), 'first': round(bf[0], 3), 'last': round(bf[-1], 3)},
                'gas_used_share': round(sum(b['gas_used'] for b in self.blocks) / sum(b['gas_limit'] for b in self.blocks), 4),
                'txs_per_block': round(statistics.mean(b['txs'] for b in self.blocks), 1),
                'tip_median_gwei': round(statistics.median(b['tip_med_gwei'] for b in self.blocks), 4),
                'zero_tip_share': round(sum(b['zero_tip'] for b in self.blocks) / max(1, self.n_tx), 4),
                'builders': collections.Counter(b['builder'] or short(b['miner']) for b in self.blocks).most_common(10),
                'blob_blocks_share': round(sum(1 for b in self.blocks if b['blob_gas']) / len(self.blocks), 3)}

    def swap_totals(self):
        by_venue = collections.defaultdict(lambda: [0, 0.0])
        for s in self.swaps:
            by_venue[s['venue']][0] += 1
            by_venue[s['venue']][1] += s['usd']
        return {v: {'n': c, 'usd': round(u)} for v, (c, u) in sorted(by_venue.items(), key=lambda kv: -kv[1][1])}

    def jit_summary(self):
        """Match mint/burn pairs of identical (pool, owner, ticks, L) inside one block; attribute bracketed swaps."""
        by_block = collections.defaultdict(list)
        for e in self.jit:
            by_block[(e['block'], e['pool'])].append(e)
        episodes = []
        swaps_by = collections.defaultdict(list)
        for s in self.swaps:
            if s.get('L'):
                swaps_by[(s['block'], s['pool'])].append(s)
        for key, evs in by_block.items():
            mints = [e for e in evs if e['kind'] == 'mint']
            burns = [e for e in evs if e['kind'] == 'burn']
            used = set()
            for m in mints:
                for i, b in enumerate(burns):
                    if i in used or b['L'] != m['L'] or b['lo'] != m['lo'] or b['hi'] != m['hi'] or b['owner'] != m['owner'] or b['li'] <= m['li']:
                        continue
                    used.add(i)
                    inside = [s for s in swaps_by.get(key, []) if m['li'] < s['li'] < b['li']]
                    fee_taken = 0.0
                    for s in inside:
                        share = min(1.0, m['L'] / s['L']) if s['L'] else 0
                        if s.get('fee_usd'):
                            fee_taken += s['fee_usd'] * share
                        s['jit_share'] = max(s.get('jit_share', 0), share)
                    episodes.append({'block': key[0], 'pool': key[1], 'venue': self.pool_venue.get(key[1]), 'owner': m['owner'], 'sender': m['sender'], 'L': m['L'], 'usd': m['usd'],
                                     'same_tx': m['tx'] == b['tx'], 'swaps_bracketed': len(inside), 'swap_usd': round(sum(s['usd'] for s in inside)),
                                     'fee_taken_usd': round(fee_taken, 2), 'mint_tx': m['tx'], 'burn_tx': b['tx']})
                    break
        for s in self.swaps:
            if s.get('jit_share') and s.get('fee_usd'):
                self.pools[s['pool']]['fee_jit'] += s['fee_usd'] * s['jit_share']
        by_owner = collections.Counter()
        fee_by_owner = collections.Counter()
        for e in episodes:
            by_owner[e['sender']] += 1
            fee_by_owner[e['sender']] += e['fee_taken_usd']
        return {'episodes': len(episodes), 'fee_taken_usd': round(sum(e['fee_taken_usd'] for e in episodes), 2), 'swap_usd_bracketed': round(sum(e['swap_usd'] for e in episodes)),
                'operators': [{'sender': a, 'episodes': c, 'fee_taken_usd': round(fee_by_owner[a], 2)} for a, c in by_owner.most_common(10)],
                'largest': sorted(episodes, key=lambda e: -(e['usd'] or 0))[:15]}

    def lp_summary(self, hours):
        # Who the takers are decides whether a pool's fee yield is worth having. Fee income from many small
        # uninformed clips is rent; the same income from one informed flow is a transfer out of the LP, and the
        # captive-flow thesis in this repo turns entirely on one desk being 62% of a pool's volume. Concentration is
        # one pass over the swaps already in memory, so it belongs in the row rather than in a bespoke scanner.
        takers = collections.defaultdict(collections.Counter)
        for sw in self.swaps:
            if sw.get('usd'):
                takers[sw['pool']][sw.get('sender') or '?'] += sw['usd']
        rows = []
        for pool, ps in self.pools.items():
            if ps['n'] < 3 or ps['vol'] < 2e5:
                continue
            toks = self.pool_tokens.get(pool) or [None, None]
            syms = [(self.p.token(t) or (short(t),))[0] if t else '?' for t in toks]
            cap = ps['cap_sum'] / ps['cap_n'] if ps['cap_n'] else None
            fee = ps['fee'] if ps['fee'] else None
            passive = (fee - ps['fee_jit']) if fee is not None else None
            px = [p for _, p in ps['px']]
            rng = (max(px) / min(px) - 1) if px and min(px) > 0 else None
            row = {'pool': pool, 'venue': self.pool_venue.get(pool), 'pair': '/'.join(syms), 'tokens': toks, 'fee_tier': self.pool_fee.get(pool), 'swaps': ps['n'], 'volume_usd': round(ps['vol']),
                   'fees_usd': round(fee, 2) if fee else None, 'fees_to_jit_usd': round(ps['fee_jit'], 2), 'passive_fees_usd': round(passive, 2) if passive is not None else None,
                   'full_range_capital_usd': round(cap) if cap else None, 'price_range_pct': round(100 * rng, 3) if rng is not None else None,
                   'lp_added_usd': round(ps['lp_in']), 'lp_removed_usd': round(ps['lp_out'])}
            tk = takers.get(pool) or collections.Counter()
            tot = sum(tk.values())
            if tot:
                top = tk.most_common(3)
                row['n_takers'] = len(tk)
                row['top_taker'] = top[0][0]
                row['top_taker_share'] = round(top[0][1] / tot, 4)
                row['top3_taker_share'] = round(sum(v for _, v in top) / tot, 4)
                # Herfindahl over taker volume shares: 1.0 is a single counterparty, near zero is a crowd.
                row['taker_herfindahl'] = round(sum((v / tot) ** 2 for v in tk.values()), 4)
            if cap and passive is not None and cap > 0:
                fr = passive / cap / hours * 8760
                row['apr_full_range'] = round(fr, 5)
                row['apr_band_1pct'] = round(fr / (1 - 1 / math.sqrt(1.01)), 4)
                row['apr_band_0_1pct'] = round(fr / (1 - 1 / math.sqrt(1.001)), 4)
                row['stable_pair'] = all(s in STABLE_SYMBOLS for s in syms)
            rows.append(row)
        rows.sort(key=lambda r: -r['volume_usd'])
        return rows[:120]

    def rates_summary(self):
        out = []
        for (venue, reserve), series in self.rates.items():
            tk = self.p.token(reserve)
            s = sorted(series)
            sup = [x[2] for x in s]
            bor = [x[3] for x in s]
            out.append({'venue': venue, 'reserve': reserve, 'sym': tk[0] if tk else short(reserve), 'updates': len(s),
                        'supply_first': sup[0], 'supply_last': sup[-1], 'supply_min': min(sup), 'supply_max': max(sup),
                        'borrow_first': bor[0], 'borrow_last': bor[-1], 'borrow_min': min(bor), 'borrow_max': max(bor),
                        'borrow_range_pp': round(100 * (max(bor) - min(bor)), 3),
                        'series': [(x[0], round(x[2], 5), round(x[3], 5)) for x in s[::max(1, len(s) // 60)]]})
        out.sort(key=lambda r: -r['borrow_range_pp'])
        return out

    def mark_atomic(self):
        """Flag borrow+repay and withdraw+supply pairs of one account and reserve inside one transaction (flash-loan-like use of a pool)."""
        if getattr(self, '_atomic_done', False):
            return
        self._atomic_done = True
        by = collections.defaultdict(list)
        for o in self.lending:
            by[(o['tx'], o['venue'], o['account'], o['reserve'])].append(o)
        for key, ops in by.items():
            kinds = {o['kind'] for o in ops}
            if {'borrow', 'repay'} <= kinds or {'withdraw', 'supply'} <= kinds:
                for o in ops:
                    o['atomic'] = True

    def atomic_cycles(self):
        self.mark_atomic()
        by = collections.defaultdict(lambda: {'txs': set(), 'usd_max': 0.0, 'reserves': collections.Counter(), 'blocks': set()})
        for o in self.lending:
            if o.get('atomic') and o['kind'] in ('borrow', 'withdraw') and o['usd']:
                k = (o['venue'], o['account'])
                by[k]['txs'].add(o['tx'])
                by[k]['usd_max'] = max(by[k]['usd_max'], o['usd'])
                by[k]['reserves'][o['sym'] + ' ' + o['kind']] += o['usd']
                by[k]['blocks'].add(o['block'])
        rows = [{'venue': k[0], 'account': k[1], 'txs': len(v['txs']), 'largest_usd': round(v['usd_max']), 'gross_usd': round(sum(v['reserves'].values())),
                 'legs': {r: round(x) for r, x in v['reserves'].most_common(6)}, 'first_block': min(v['blocks']), 'last_block': max(v['blocks'])} for k, v in by.items()]
        rows.sort(key=lambda r: -r['gross_usd'])
        return rows[:20]

    def lending_summary(self):
        self.mark_atomic()
        tot = collections.defaultdict(lambda: collections.defaultdict(float))
        for o in self.lending:
            if o['usd']:
                tot[o['venue']][('atomic ' if o.get('atomic') else '') + o['kind']] += o['usd']
        ops = sorted([o for o in self.lending if (o['usd'] or 0) >= 2.5e5 and not o.get('atomic')], key=lambda o: -(o['usd'] or 0))
        per_account = collections.Counter()
        large = []
        for o in ops:
            per_account[o['account']] += 1
            if per_account[o['account']] <= 3:
                large.append(o)
        followed = [self.follow_proceeds(o) for o in large if o['kind'] in ('borrow', 'withdraw') and o.get('receiver')]
        return {'totals': {v: {k: round(x) for k, x in d.items()} for v, d in tot.items()}, 'large_ops': large[:80], 'proceeds_followed': [f for f in followed if f]}

    def follow_proceeds(self, o):
        """Where did the borrowed/withdrawn tokens go within 60 minutes? First hop, then a second hop if the first forwards."""
        recv, tok = o['receiver'], o['reserve']
        if not recv or not tok:
            return None
        later = [x for x in self.transfers if x['token'] == tok and x['from'] == recv and x['block'] >= o['block'] and x['ts'] - o['ts'] <= 3600]
        hops = []
        for x in sorted(later, key=lambda x: x['block'])[:12]:
            dst = x['to']
            tag, label = self.tag(dst), self.label(dst)
            second = None
            if dst not in self.book:  # chase a forwarding hop only through UNLABELLED intermediaries, not through a known venue/protocol
                fwd = [y for y in self.transfers if y['token'] == tok and y['from'] == dst and y['block'] >= x['block'] and y['ts'] - x['ts'] <= 3600 and self.is_exchange(y['to'])]
                if fwd:
                    second = {'to': fwd[0]['to'], 'label': self.label(fwd[0]['to']), 'usd': round(fwd[0]['usd'])}
            hops.append({'block': x['block'], 'to': dst, 'usd': round(x['usd']), 'tag': tag, 'label': label, 'forwarded_to_exchange': second, 'tx': x['tx']})
        to_exchange = sum(h['usd'] for h in hops if self.is_exchange(h['to']) or h['forwarded_to_exchange'])
        return {'op': {k: o[k] for k in ('block', 'ts', 'tx', 'venue', 'kind', 'sym', 'usd', 'account', 'receiver')}, 'hops': hops, 'to_exchange_usd': round(to_exchange)}

    def exchange_flow(self):
        by_asset = collections.defaultdict(lambda: {'in': 0.0, 'out': 0.0})
        by_label = collections.defaultdict(lambda: {'in': 0.0, 'out': 0.0})
        deposits = []
        for x in self.transfers:
            ti, to = self.is_exchange(x['from']), self.is_exchange(x['to'])
            if to and not ti:
                by_asset[x['sym']]['in'] += x['usd']
                by_label[self.label(x['to'])]['in'] += x['usd']
                if x['usd'] >= 1e6:
                    deposits.append(x)
            elif ti and not to:
                by_asset[x['sym']]['out'] += x['usd']
                by_label[self.label(x['from'])]['out'] += x['usd']
        assets = {k: {'in': round(v['in']), 'out': round(v['out']), 'net': round(v['in'] - v['out'])} for k, v in by_asset.items()}
        labels = sorted(({'label': k, 'in': round(v['in']), 'out': round(v['out'])} for k, v in by_label.items()), key=lambda r: -(r['in'] + r['out']))
        return {'by_asset': dict(sorted(assets.items(), key=lambda kv: -(kv[1]['in'] + kv[1]['out']))), 'by_label': labels[:25],
                'largest_deposits': sorted(deposits, key=lambda x: -x['usd'])[:25]}

    def round_trips(self):
        big = sorted([x for x in self.transfers if x['usd'] >= 1e7], key=lambda x: (x['block'], x['li']))
        same_tx = {(x['tx'], x['token'], x['from'], x['to']) for x in big}
        big = [x for x in big if (x['tx'], x['token'], x['to'], x['from']) not in same_tx]
        out, used = [], set()
        for i, a in enumerate(big):
            for j in range(i + 1, len(big)):
                b = big[j]
                if j in used or b['tx'] == a['tx'] or b['block'] <= a['block']:
                    continue
                if b['token'] == a['token'] and b['from'] == a['to'] and b['to'] == a['from'] and abs(b['usd'] - a['usd']) / a['usd'] < 0.02:
                    used.add(j)
                    out.append({'out_tx': a['tx'], 'back_tx': b['tx'], 'sym': a['sym'], 'usd': round(a['usd']), 'from': a['from'], 'via': a['to'], 'blocks_apart': b['block'] - a['block'],
                                'minutes': round((b['ts'] - a['ts']) / 60, 1)})
                    break
        # collapse repeated identical trips
        agg = collections.OrderedDict()
        for r in out:
            k = (r['sym'], r['from'], r['via'], round(r['usd'], -5))
            if k in agg:
                agg[k]['count'] += 1
            else:
                agg[k] = dict(r, count=1)
        return list(agg.values())[:30]

    def scheduled_flow(self):
        """Senders with >= 4 swaps in one direction: regularity of interval and size (TWAP-like programmes)."""
        groups = collections.defaultdict(list)
        for s in self.swaps:
            if s['usd'] >= 2e4:
                groups[(s['sender'], s['tok_in'], s['tok_out'])].append(s)
        rows = []
        for (sender, ti, to), ss in groups.items():
            if len(ss) < 4:
                continue
            ss.sort(key=lambda s: s['ts'])
            gaps = [ss[i + 1]['ts'] - ss[i]['ts'] for i in range(len(ss) - 1)]
            gaps = [g for g in gaps if g > 0]
            if len(gaps) < 3:
                continue
            sizes = [s['usd'] for s in ss]
            cv_gap = statistics.pstdev(gaps) / statistics.mean(gaps)
            cv_size = statistics.pstdev(sizes) / statistics.mean(sizes)
            rows.append({'sender': sender, 'label': self.label(sender), 'sell': (self.p.token(ti) or (short(ti),))[0] if ti else '?', 'buy': (self.p.token(to) or (short(to),))[0] if to else '?',
                         'n': len(ss), 'total_usd': round(sum(sizes)), 'median_usd': round(statistics.median(sizes)), 'median_gap_s': round(statistics.median(gaps)),
                         'cv_gap': round(cv_gap, 2), 'cv_size': round(cv_size, 2), 'venues': dict(collections.Counter(s['venue'] for s in ss)), 'first_block': ss[0]['block'], 'last_block': ss[-1]['block']})
        rows.sort(key=lambda r: (r['cv_gap'] + r['cv_size']) / (1 + math.log10(max(1, r['total_usd']))))
        return [r for r in rows if r['cv_gap'] < 0.6 and r['cv_size'] < 0.6][:20] + [r for r in rows if not (r['cv_gap'] < 0.6 and r['cv_size'] < 0.6)][:10]

    def peg_summary(self):
        out = {}
        feed_assets = {s for a, (s, d, k) in TOKENS.items() if k in FEEDS and k not in ('USDC', 'USDT', 'DAI')}  # ETH, BTC wrappers, LINK...: priced by feeds, not pegged
        for sym, obs in self.peg.items():
            if sym in feed_assets:
                continue
            obs = [o for o in obs if o[0] >= 500]
            if len(obs) < 3:
                continue
            tot = sum(u for u, _, _, _ in obs)
            if tot < 5e4:
                continue
            pxs = sorted(px for _, px, _, _ in obs)
            lo, hi = pxs[len(pxs) // 20], pxs[min(len(pxs) - 1, 19 * len(pxs) // 20)]
            kept = [o for o in obs if lo <= o[1] <= hi] or obs
            vw = sum(u * px for u, px, _, _ in kept) / sum(u for u, _, _, _ in kept)
            out[sym] = {'n': len(obs), 'volume_usd': round(tot), 'vw_price': vw, 'median': pxs[len(pxs) // 2], 'p10': pxs[len(pxs) // 10], 'p90': pxs[9 * len(pxs) // 10],
                        'venues': dict(collections.Counter(v for _, _, _, v in obs))}
        return out

    def bridge_summary(self):
        by = collections.defaultdict(lambda: {'n': 0, 'usd': 0.0, 'recipients': collections.Counter()})
        for x in self.bridges:
            k = (x['kind'], x['token'], x['dst_name'])
            by[k]['n'] += 1
            by[k]['usd'] += x['usd'] or 0
            if x['recipient']:
                by[k]['recipients'][x['recipient']] += x['usd'] or 0
        rows = [{'kind': k[0], 'token': k[1], 'destination': k[2], 'n': v['n'], 'usd': round(v['usd']), 'top_recipient': (v['recipients'].most_common(1)[0][0], round(v['recipients'].most_common(1)[0][1])) if v['recipients'] else None}
                for k, v in by.items()]
        rows.sort(key=lambda r: -r['usd'])
        return {'out': rows[:30], 'out_total_usd': round(sum(r['usd'] for r in rows)), 'cctp_in_usd': round(sum(x['usd'] for x in self.bridge_in)), 'cctp_in_n': len(self.bridge_in)}


# ----------------------------------------------------------------------------------------------------------------------
# Head-state reads (bounded RPC)
# ----------------------------------------------------------------------------------------------------------------------
def dec_str(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) >= 64:
            off = int.from_bytes(b[:32], 'big')
            ln = int.from_bytes(b[off:off + 32], 'big')
            return b[off + 32:off + 32 + ln].decode('utf-8', 'ignore')
        return b.rstrip(b'\0').decode('utf-8', 'ignore')
    except Exception:
        return None


def head_state(args):
    out = Path(args.out)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    hn, hts, hh = rpc_head(rpc)
    blk = hex(hn)
    # `head` reads state at the *current* block. Pointing it at a window collected hours ago would stamp tonight's
    # prices, rates and NAVs onto yesterday's blocks — and since `analyze` prices the window from `head_state.json`,
    # the whole analysis would then be a mix of two timeframes with nothing saying so. The provenance gate cannot
    # catch this: the labels and the token table would both be unchanged. So it is refused here.
    mf = out / 'manifest.json'
    if mf.exists():
        try:
            man = json.loads(mf.read_text())
        except Exception:
            man = {}
        last = man.get('last_block_at_collect')
        span = (last - man['first_block']) if (last and man.get('first_block')) else 0
        drift = (hn - last) if last else 0
        if last and drift > max(2 * span, 300) and not getattr(args, 'force', False):
            raise SystemExit(
                'refusing: the head is %d blocks past this window (collected to %d, head %d, window %d blocks).\n'
                'Reading state now would price a past window at present rates. Collect a fresh window, or pass '
                '--force if you intend the mismatch.' % (drift, last, hn, span))
    hs = {'block': hn, 'timestamp': hts, 'utc': utc(hts), 'feeds': {}, 'rates': {}, 'tokens': {}, 'lending': {}, 'compound': {}, 'health': [], 'sky': {}, 'ethena': {}}
    # Chainlink feeds with description check
    items = []
    for k, (feed, desc) in FEEDS.items():
        items += [(feed, SEL['description']), (feed, SEL['latestRoundData']), (feed, SEL['decimals'])]
    res = rpc.eth_calls(items, blk)
    for i, (k, (feed, desc)) in enumerate(FEEDS.items()):
        d, r, dec = res[3 * i], res[3 * i + 1], res[3 * i + 2]
        got = dec_str(d) if d else None
        if r and got == desc:
            decimals = word(dec, 0) if dec else 8
            hs['feeds'][k] = {'feed': feed, 'description': got, 'usd': word(r, 1) / 10 ** decimals, 'updated_at': word(r, 3), 'age_s': hts - word(r, 3)}
        else:
            hs['feeds'][k] = {'feed': feed, 'description': got, 'usd': None, 'error': 'description mismatch or call failed'}
    # NAV rates
    items = []
    for k, (c, m, u) in RATES.items():
        data = sel(m) + (enc_uint(10 ** 18) if '(uint256)' in m else '')
        items.append((c, data))
    res = rpc.eth_calls(items, blk)
    for (k, (c, m, u)), r in zip(RATES.items(), res):
        hs['rates'][k] = {'contract': c, 'method': m, 'underlying': u, 'rate': word(r, 0) / 1e18 if r else None}
    # the second view, on the same contract at the same block
    cc, keys = [], []
    for k, spec in RATE_CROSSCHECK.items():
        kind, a, b = spec[0], spec[1], spec[2]
        if k not in RATES:
            continue
        c = spec[3] if len(spec) > 3 else RATES[k][0]
        keys.append((k, kind))
        cc.append((c, sel(a) + (enc_uint(10 ** 18) if '(uint256)' in a else '')))
        cc.append((c, sel(b) if b else sel(a)))
    res = rpc.eth_calls(cc, blk) if cc else []
    for i, (k, kind) in enumerate(keys):
        x, y = res[2 * i], res[2 * i + 1]
        if kind == 'ratio':
            ta, ts = (word(x, 0) if x else None), (word(y, 0) if y else None)
            hs['rates'][k]['crosscheck'] = ({'method': 'totalAssets / totalSupply', 'rate': ta / ts,
                                             'total_assets': str(ta), 'total_supply': str(ts)}
                                            if ta and ts else {'method': 'totalAssets / totalSupply', 'rate': None})
        else:
            hs['rates'][k]['crosscheck'] = {'method': RATE_CROSSCHECK[k][1],
                                            'contract': (RATE_CROSSCHECK[k][3]
                                                         if len(RATE_CROSSCHECK[k]) > 3 else RATES[k][0]),
                                            'rate': (word(x, 0) / 1e18) if x else None}
    # token metadata check
    items = []
    toks = [(a, v) for a, v in TOKENS.items() if a != '0x' + '0' * 40]
    for a, _ in toks:
        items += [(a, SEL['symbol']), (a, SEL['decimals'])]
    res = rpc.eth_calls(items, blk)
    mismatches = []
    for i, (a, (s, d, k)) in enumerate(toks):
        sym, dec = res[2 * i], res[2 * i + 1]
        got_s, got_d = dec_str(sym) if sym else None, word(dec, 0) if dec else None
        if got_s is None or got_d != d:
            mismatches.append({'address': a, 'expected': [s, d], 'got': [got_s, got_d]})
    hs['token_registry_mismatches'] = mismatches
    # lending reserves: Aave + Spark getReserveData for RATE_ASSETS, then aToken / variableDebt totalSupply
    by_sym = {s: a for a, (s, d, k) in TOKENS.items()}
    for pool, venue in LENDING_POOLS.items():
        # Ask the pool which reserves it has, rather than reading a hardcoded list. RATE_ASSETS named fifteen symbols
        # and so made every other reserve invisible to the size and capacity checks: Aave's USDtb reserve was paying
        # 8.05% — the highest dollar supply rate on the venue — and appeared in `analysis.json` from its rate logs with
        # no supplied amount at all, which meant nothing downstream could rank or price it. The list is kept as the
        # fallback and as the ordering, but discovery decides membership.
        listed = rpc.eth_calls([(pool, sel('getReservesList()'))], blk)[0]
        discovered = []
        if listed and len(listed) >= 2 + 128:
            n = word(listed, 1)
            for i in range(min(n, 200)):
                a = '0x' + listed[2 + 64 * (2 + i):2 + 64 * (3 + i)][-40:]
                if a in TOKENS:
                    discovered.append(a)
        assets = discovered or [by_sym[s] for s in RATE_ASSETS if s in by_sym]
        res = rpc.eth_calls([(pool, SEL['getReserveData'] + enc_addr(a)) for a in assets], blk)
        rows = {}
        sup_items = []
        for a, r in zip(assets, res):
            if not r or len(r) < 2 + 64 * 12:
                continue
            atoken, vdebt, strategy = '0x' + r[2 + 64 * 8:2 + 64 * 9][-40:], '0x' + r[2 + 64 * 10:2 + 64 * 11][-40:], '0x' + r[2 + 64 * 11:2 + 64 * 12][-40:]
            rows[a] = {'sym': TOKENS[a][0], 'supply_apr': word(r, 2) / RAY, 'borrow_apr': word(r, 4) / RAY, 'aToken': atoken, 'variableDebt': vdebt, 'strategy': strategy, 'config': word(r, 0)}
            sup_items += [(atoken, SEL['totalSupply']), (vdebt, SEL['totalSupply'])]
        res2 = rpc.eth_calls(sup_items, blk)
        for i, a in enumerate([x for x in assets if x in rows]):
            s, dbt = res2[2 * i], res2[2 * i + 1]
            dec = TOKENS[a][1]
            px = Prices(hs).usd.get(TOKENS[a][2]) or (1.0 if TOKENS[a][2] == 'USD' else None)
            supplied = word(s, 0) / 10 ** dec if s else None
            borrowed = word(dbt, 0) / 10 ** dec if dbt else None
            rows[a].update({'supplied': supplied, 'borrowed': borrowed, 'utilisation': (borrowed / supplied) if supplied and borrowed is not None and supplied > 0 else None,
                            'supplied_usd': supplied * px if supplied is not None and px else None, 'borrowed_usd': borrowed * px if borrowed is not None and px else None})
        hs['lending'][venue] = rows
    # Rate-curve parameters for *every* discovered reserve, in one call each. Without the curve a supply rate cannot be
    # turned into a capacity: a rate is a point on a kinked function of utilisation, and how much new supply it survives
    # is the only number that decides whether an 8% headline is worth $5k a year or $5M. The v3.2 strategy packs all
    # four parameters into `getInterestRateDataBps(address)` in basis points; the four separate ray getters this used to
    # call returned nothing on this deployment, which is why `rate_curves` was empty.
    curves = {}
    for venue, rows in hs['lending'].items():
        items = [(r['strategy'], sel('getInterestRateDataBps(address)') + enc_addr(a))
                 for a, r in rows.items() if r.get('strategy') and int(r['strategy'], 16)]
        keys = [(venue, r['sym']) for a, r in rows.items() if r.get('strategy') and int(r['strategy'], 16)]
        res = rpc.eth_calls(items, blk) if items else []
        for (v, symb), r in zip(keys, res):
            if r and len(r) >= 2 + 64 * 4:
                curves['%s %s' % (v, symb)] = {'optimal': word(r, 0) / 1e4, 'base': word(r, 1) / 1e4,
                                               'slope1': word(r, 2) / 1e4, 'slope2': word(r, 3) / 1e4}
    # the reserve factor decides how much of the borrow rate reaches the supplier, so the curve is useless without it
    for venue, rows in hs['lending'].items():
        for a, r in rows.items():
            k = '%s %s' % (venue, r['sym'])
            if k in curves and r.get('config') is not None:
                curves[k]['reserve_factor'] = ((r['config'] >> 64) & 0xFFFF) / 1e4
    hs['rate_curves'] = curves
    # Compound v3
    for comet, name in COMETS.items():
        u = rpc.eth_calls([(comet, SEL['getUtilization']), (comet, SEL['baseToken'])], blk)
        if u[0]:
            util = word(u[0], 0)
            r = rpc.eth_calls([(comet, SEL['getSupplyRate'] + enc_uint(util)), (comet, SEL['getBorrowRate'] + enc_uint(util))], blk)
            if all(r):
                tt = rpc.eth_calls([(comet, SEL['totalSupply']), (comet, sel('totalBorrow()')), (comet, sel('decimals()'))], blk)
                dec = word(tt[2], 0) if tt[2] else 6
                hs['compound'][name] = {'base_token': '0x' + u[1][-40:] if u[1] else None, 'utilisation': util / 1e18, 'supply_apr': word(r[0], 0) * 31536000 / 1e18, 'borrow_apr': word(r[1], 0) * 31536000 / 1e18,
                                        'supplied': word(tt[0], 0) / 10 ** dec if tt[0] else None, 'borrowed': word(tt[1], 0) / 10 ** dec if tt[1] else None}
                # Sample the Comet's own supply curve. Compound's kink is far sharper than an Aave reserve's and these
                # markets sit right on it — USDC's kink is at exactly 90.0% utilisation and the market was at 90.77%,
                # where the rate falls from 5.70% to 3.24% over 0.77 percentage points. A detector that dilutes a
                # Compound rate with a smooth model overstates its capacity by more than an order of magnitude, so the
                # curve is measured here rather than assumed downstream.
                grid = [0.50, 0.60, 0.70, 0.75, 0.80, 0.84, 0.87, 0.89, 0.895, 0.90, 0.905, 0.91, 0.92, 0.94, 0.96, 0.98, 0.995]
                cur = rpc.eth_calls([(comet, SEL['getSupplyRate'] + enc_uint(int(x * 1e18))) for x in grid], blk)
                hs['compound'][name]['supply_curve'] = [[x, word(c, 0) * 31536000 / 1e18] for x, c in zip(grid, cur) if c]
    # Morpho Blue: the isolated-market side of the borrow book.
    hs['morpho'] = morpho_state(rpc, out, blk)
    # Pendle: the fixed-rate side of every yield-bearing dollar and ETH claim.
    #
    # The market list is discovered from the window's own `Swap` logs rather than hardcoded or fetched from an API.
    # That has a property a fixed list does not: it enumerates exactly the markets with live flow, updates itself as
    # markets expire and new ones list, and needs no network call to build. A market nobody traded in the window is a
    # market whose price is a quote rather than a trade, and leaving it out is the honest default.
    hs['pendle'] = pendle_state(rpc, out, blk, hn_ts=hs.get('timestamp'))
    # Sky savings rates, Ethena vesting
    r = rpc.eth_calls([('0xa3931d71877c0e7a3148cb7eb4463524fec27fbd', SEL['ssr']), ('0x197e90f9fde81202ff37a6f4ecd0bd4a2f1de6d8', SEL['dsr']),
                       ('0x9d39a5de30e57443bff2a8307a4256c8797a3497', SEL['vestingAmount']), ('0x9d39a5de30e57443bff2a8307a4256c8797a3497', SEL['totalAssets'])], blk)
    if r[0]:
        hs['sky']['ssr_apy'] = (word(r[0], 0) / RAY) ** 31536000 - 1
    if r[1]:
        hs['sky']['dsr_apy'] = (word(r[1], 0) / RAY) ** 31536000 - 1
    if r[2] and r[3]:
        va, ta = word(r[2], 0) / 1e18, word(r[3], 0) / 1e18
        hs['ethena'] = {'vesting_usde_8h': va, 'total_assets_usde': ta, 'apr_from_vesting': va * 3 * 365 / ta if ta else None}
    # health factors for accounts named by the analysis
    accounts = []
    ap = out / 'analysis.json'
    if ap.exists():
        an = json.loads(ap.read_text())
        seen = set()
        for o in an.get('lending_ops', {}).get('large_ops', []):
            if o['venue'] in LENDING_POOLS.values() and (o['usd'] or 0) >= 5e5 and o['account'] not in seen:
                seen.add(o['account'])
                accounts.append((o['venue'], o['account']))
        for l in an.get('liquidations', []):
            if l['venue'] in LENDING_POOLS.values() and (l['venue'], l['user']) not in accounts:
                accounts.append((l['venue'], l['user']))
    pool_of = {v: k for k, v in LENDING_POOLS.items()}
    res = rpc.eth_calls([(pool_of[v], SEL['getUserAccountData'] + enc_addr(a)) for v, a in accounts[:150]], blk)
    for (v, a), r in zip(accounts, res):
        if r and len(r) >= 2 + 64 * 6:
            hf = word(r, 5) / 1e18
            hs['health'].append({'venue': v, 'account': a, 'collateral_usd': word(r, 0) / 1e8, 'debt_usd': word(r, 1) / 1e8, 'liq_threshold': word(r, 3) / 1e4, 'ltv': word(r, 2) / 1e4,
                                 'health_factor': hf if hf < 1e6 else None, 'drop_to_liquidation': (1 - 1 / hf) if 0 < hf < 1e6 else None})
    hs['health'].sort(key=lambda h: -h['debt_usd'])
    # Morpho market params for markets named in the window
    mp = out / 'markets.json'
    markets = json.loads(mp.read_text()) if mp.exists() else {}
    need = []
    if ap.exists():
        for o in an.get('lending_ops', {}).get('large_ops', []) + an.get('liquidations', []):
            m = o.get('market')
            if m and m not in markets and m not in need:
                need.append(m)
    if need:
        res = rpc.eth_calls([(MORPHO, SEL['idToMarketParams'] + m[2:]) for m in need], blk)
        for m, r in zip(need, res):
            if r and len(r) >= 2 + 64 * 5:
                markets[m] = {'loan': '0x' + r[2:66][-40:], 'collateral': '0x' + r[66:130][-40:], 'lltv': word(r, 4) / 1e18}
        mp.write_text(json.dumps(markets, indent=1))
    # v3 fee tiers and unknown-token metadata for top pools
    pp = out / 'pools.json'
    pools = json.loads(pp.read_text()) if pp.exists() else {}
    if ap.exists():
        v3 = [r['pool'] for r in an.get('lp', []) if r['venue'] == 'uniswap_v3' and pools.get(r['pool'], {}).get('fee') is None][:150]
        if v3:
            res = rpc.eth_calls([(p, SEL['fee']) for p in v3], blk)
            for p, r in zip(v3, res):
                pools.setdefault(p, {})['fee'] = word(r, 0) / 1e6 if r else None
        # Uniswap v4 pool currencies come from same-transaction token movements (see State.infer_pool_tokens); Infura caps eth_getLogs at 10k blocks,
        # so the Initialize event cannot be looked up here.
        pp.write_text(json.dumps(pools, indent=1))
        unknown = [a for a, _ in an.get('unpriced_tokens', [])][:60]
        res = rpc.eth_calls([x for a in unknown for x in ((a, SEL['symbol']), (a, SEL['decimals']))], blk)
        for i, a in enumerate(unknown):
            s, d = res[2 * i], res[2 * i + 1]
            hs['tokens'][a] = {'symbol': dec_str(s) if s else None, 'decimals': word(d, 0) if d else None}
    hs['rpc'] = rpc.stats()
    (out / 'head_state.json').write_text(json.dumps(hs, indent=1, sort_keys=True))
    print(json.dumps({'block': hn, 'feeds_ok': sum(1 for v in hs['feeds'].values() if v.get('usd')), 'rates_ok': sum(1 for v in hs['rates'].values() if v.get('rate')),
                      'token_mismatches': len(mismatches), 'health_rows': len(hs['health']), 'compound': list(hs['compound']), **rpc.stats()}, indent=1))


# ----------------------------------------------------------------------------------------------------------------------
# Analyze over raw files
# ----------------------------------------------------------------------------------------------------------------------
MORPHO_IRM_SIG = ('borrowRateView((address,address,address,address,uint256),'
                  '(uint128,uint128,uint128,uint128,uint128,uint128))')
# Every Morpho Blue market event indexes the market id as topic 1, so the markets that saw activity in a window are
# readable from its own logs without an index or an API — the same self-updating discovery the Pendle reader uses.
MORPHO_MARKET_TOPICS = {keccak(sig) for sig in (
    'Supply(bytes32,address,address,uint256,uint256)',
    'Withdraw(bytes32,address,address,address,uint256,uint256)',
    'Borrow(bytes32,address,address,address,uint256,uint256)',
    'Repay(bytes32,address,address,uint256,uint256)',
    'AccrueInterest(bytes32,uint256,uint256,uint256)',
    'SupplyCollateral(bytes32,address,address,uint256)',
    'WithdrawCollateral(bytes32,address,address,address,uint256)',
)}


def morpho_markets_in_window(out, cap=60):
    """Morpho Blue market ids that saw activity in this window, busiest first."""
    import collections as _c
    c = _c.Counter()
    d = Path(out) / 'raw' / 'logs'
    if not d.exists():
        return []
    for p in sorted(d.glob('*.json.gz')):
        for l in read_gz(p):
            if l['address'].lower() != MORPHO:
                continue
            tp = l.get('topics')
            if tp and len(tp) >= 2 and tp[0] in MORPHO_MARKET_TOPICS:
                c[tp[1]] += 1
    return [i for i, _ in c.most_common(cap)]


def morpho_state(rpc, out, blk):
    """Per-market borrow and supply rates, utilisation and *withdrawable liquidity* for the active Morpho markets.

    The number that matters here is liquidity, not size. Morpho's markets are isolated, so a rate is only as good as
    the amount you could actually borrow against it, and a market at 99% utilisation quoting a cheap rate is quoting a
    rate on nothing. Aave and Compound blur this behind a single pooled reserve; Morpho does not, which is why the
    comparison has to carry it.

    The rate comes from the IRM's own view function — the same one Morpho calls on accrual — fed the market params and
    state structs. Both structs are entirely static types, so the encoding is a straight concatenation of words.
    """
    ids = morpho_markets_in_window(out)
    if not ids:
        return {}
    res = rpc.eth_calls([(MORPHO, sel(sg) + i[2:]) for i in ids
                         for sg in ('idToMarketParams(bytes32)', 'market(bytes32)')], blk)
    rows = []
    for k, i in enumerate(ids):
        pr, mk = res[2 * k], res[2 * k + 1]
        if not pr or len(pr) < 2 + 64 * 5 or not mk or len(mk) < 2 + 64 * 6:
            continue
        loan, coll = '0x' + pr[2:66][-40:], '0x' + pr[66:130][-40:]
        oracle, irm = '0x' + pr[130:194][-40:], '0x' + pr[194:258][-40:]
        rows.append({'id': i, 'loan': loan, 'collateral': coll, 'oracle': oracle, 'irm': irm,
                     'lltv': word(pr, 4) / 1e18,
                     'params': [loan, coll, oracle, irm, word(pr, 4)],
                     'state': [word(mk, j) for j in range(6)]})
    if not rows:
        return {}
    calls = []
    for r in rows:
        loan, coll, oracle, irm, lltv = r['params']
        body = (enc_addr(loan) + enc_addr(coll) + enc_addr(oracle) + enc_addr(irm) + enc_uint(lltv)
                + ''.join(enc_uint(x) for x in r['state']))
        calls.append((r['irm'], sel(MORPHO_IRM_SIG) + body))
        calls.append((r['loan'], SEL['decimals']))
        calls.append((r['loan'], SEL['symbol']))
    res = rpc.eth_calls(calls, blk)
    out_rows = {}
    for k, r in enumerate(rows):
        rate, dec, sy = res[3 * k], res[3 * k + 1], res[3 * k + 2]
        d = word(dec, 0) if dec else 18
        sup, bor, fee = r['state'][0], r['state'][2], r['state'][5] / 1e18
        per_sec = (word(rate, 0) / 1e18) if rate else None
        # Morpho quotes a per-second rate; the market compounds continuously, so the APY is the exponential.
        apy = (math.exp(per_sec * 31_536_000) - 1) if per_sec is not None else None
        util = (bor / sup) if sup else 0.0
        out_rows[r['id']] = {
            'id': r['id'], 'loan': r['loan'], 'collateral': r['collateral'], 'lltv': r['lltv'],
            'sym': dec_str(sy) if sy else None, 'decimals': d,
            'supplied': sup / 10 ** d, 'borrowed': bor / 10 ** d, 'liquidity': (sup - bor) / 10 ** d,
            'utilisation': round(util, 6), 'fee': fee,
            'borrow_apy': apy, 'supply_apy': (apy * util * (1 - fee)) if apy is not None else None}
    return out_rows


PENDLE_SWAP_TOPIC = keccak('Swap(address,address,int256,int256,uint256,uint256)')
PENDLE_PY_ORACLE = '0x9a9fa8338dd5e5b2188006f1cd2ef26d921650c2'   # PYLpOracle; every read is checked by getOracleState
PENDLE_TWAP = 900


def pendle_markets_in_window(out, cap=40):
    """Pendle markets that actually traded in this window, busiest first, from the raw logs."""
    import collections as _c
    c = _c.Counter()
    d = Path(out) / 'raw' / 'logs'
    if not d.exists():
        return []
    for p in sorted(d.glob('*.json.gz')):
        for l in read_gz(p):
            tp = l.get('topics')
            if tp and tp[0] == PENDLE_SWAP_TOPIC:
                c[l['address'].lower()] += 1
    return [a for a, _ in c.most_common(cap)]


def pendle_state(rpc, out, blk, hn_ts=None):
    """Implied fixed yield per traded Pendle market, with the depth behind it.

    A principal token redeems 1:1 into its asset at maturity, so its price *is* a fixed rate: `(1/p)^(365/days) − 1`.
    The rate is only meaningful when the oracle's observation window is populated, which `getOracleState` reports and
    this refuses to quote without — an unpopulated TWAP returns a number that looks like a price and is not one.

    Depth is the market's own PT balance: buying PT takes it from the market's reserves, so that balance is the most
    you could buy before the price impact is the whole trade. It is a ceiling, not a fill.
    """
    import datetime as _dt
    markets = pendle_markets_in_window(out)
    if not markets:
        return {}
    now = hn_ts or int(time.time())
    if isinstance(now, str):
        now = int(_dt.datetime.fromisoformat(now.replace('Z', '+00:00')).timestamp())
    res = rpc.eth_calls([(m, sel(sg)) for m in markets for sg in ('readTokens()', 'expiry()')], blk)
    rows = []
    for i, m in enumerate(markets):
        rt, ex = res[2 * i], res[2 * i + 1]
        if not rt or len(rt) < 2 + 3 * 64 or not ex:
            continue
        rows.append({'market': m, 'sy': '0x' + rt[2:66][-40:], 'pt': '0x' + rt[66:130][-40:],
                     'yt': '0x' + rt[130:194][-40:], 'expiry': word(ex, 0)})
    if not rows:
        return {}
    calls = []
    for r in rows:
        calls += [(PENDLE_PY_ORACLE, sel('getPtToAssetRate(address,uint32)') + enc_addr(r['market']) + enc_uint(PENDLE_TWAP)),
                  (PENDLE_PY_ORACLE, sel('getOracleState(address,uint32)') + enc_addr(r['market']) + enc_uint(PENDLE_TWAP)),
                  (r['pt'], SEL['symbol']), (r['pt'], SEL['decimals']),
                  (r['pt'], SEL['balanceOf'] + enc_addr(r['market']))]
    res = rpc.eth_calls(calls, blk)
    out_rows = {}
    for i, r in enumerate(rows):
        pa, st, sy, dc, bal = res[5 * i: 5 * i + 5]
        days = (r['expiry'] - now) / 86400 if r['expiry'] else None
        satisfied = bool(word(st, 2)) if (st and len(st) >= 2 + 3 * 64) else False
        p = word(pa, 0) / 1e18 if pa else None
        dec = word(dc, 0) if dc else 18
        r.update({'pt_symbol': dec_str(sy) if sy else None, 'pt_decimals': dec,
                  # Full precision, deliberately. `implied_apy` is computed from this value, so storing a rounded
                  # copy means the artifact no longer reproduces its own output — which is what `head-pendle-apy`
                  # caught on its first run against fresh data, at a residual of 2e-6.
                  'days_to_maturity': days,
                  'pt_to_asset': p, 'oracle_ready': satisfied,
                  'pt_depth_units': (word(bal, 0) / 10 ** dec) if bal else None})
        ok = p and days and days > 0 and satisfied
        r['implied_apy'] = ((1 / p) ** (365 / days) - 1) if ok else None
        out_rows[r['market']] = r
    return out_rows


def load_state(out, first=None, last=None, quiet=False):
    out = Path(out)
    hs = json.loads((out / 'head_state.json').read_text()) if (out / 'head_state.json').exists() else {}
    prices = Prices(hs)
    if 'ETH' not in prices.usd:
        raise RPCError('No ETH price: run `head` first (or supply head_state.json)')
    book = load_address_book()
    pools = json.loads((out / 'pools.json').read_text()) if (out / 'pools.json').exists() else {}
    markets = json.loads((out / 'markets.json').read_text()) if (out / 'markets.json').exists() else {}
    st = State(prices, book, market_cache=markets)
    for p, v in pools.items():
        if v.get('fee'):
            st.pool_fee[p] = v['fee']
        if v.get('tokens') and all(v['tokens']):
            st.pool_tokens[p] = v['tokens']
        if v.get('hook'):
            st.pool_hook[p] = v['hook']
    nums = sorted(int(p.name.split('.')[0]) for p in (out / 'raw' / 'blocks').glob('*.json.gz'))
    nums = [n for n in nums if (first is None or n >= first) and (last is None or n <= last) and logs_path(out, n).exists()]
    t0 = time.monotonic()
    for i, n in enumerate(nums):
        st.ingest(read_gz(block_path(out, n)), read_gz(logs_path(out, n)))
        if not quiet and i % 100 == 99:
            print(json.dumps({'ingested': i + 1, 'of': len(nums), 'seconds': round(time.monotonic() - t0, 1)}), flush=True)
    return st, nums


def analyze(args):
    out = Path(args.out)
    st, nums = load_state(out, args.first, args.last)
    res = st.finish()
    res['price_basis'] = {k: v for k, v in st.p.usd.items()}
    res['address_book_size'] = len(st.book)
    # What this analysis was built from. `verify` compares these before it compares a number, so a label edit reports
    # itself as staleness rather than as a numeric mismatch whose stated cause would be wrong. See provenance.py.
    import provenance
    res['provenance'] = provenance.stamp('analysis', out=out,
                                         first_block_analysed=nums[0] if nums else None,
                                         last_block_analysed=nums[-1] if nums else None)
    (out / 'analysis.json').write_text(json.dumps(res, indent=1, default=str))
    # cache inferred pool tokens for later runs
    pp = out / 'pools.json'
    pools = json.loads(pp.read_text()) if pp.exists() else {}
    for p, toks in st.pool_tokens.items():
        if toks and all(toks):
            pools.setdefault(p, {})['tokens'] = toks
    pp.write_text(json.dumps(pools, indent=1))
    print(json.dumps({'blocks': len(nums), 'transactions': st.n_tx, 'logs': st.n_logs, 'swaps_priced': len(st.swaps), 'transfers_10k': len(st.transfers), 'lending_ops': len(st.lending),
                      'jit_episodes': res['jit']['episodes'], 'rate_series': len(st.rates), 'bridges_out': len(st.bridges), 'unknown_topics': len(st.unknown_topics)}))


# ----------------------------------------------------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------------------------------------------------
def render(args):
    out = Path(args.out)
    an = json.loads((out / 'analysis.json').read_text())
    hs = json.loads((out / 'head_state.json').read_text()) if (out / 'head_state.json').exists() else {}
    ins = (out / 'insights.md').read_text() if (out / 'insights.md').exists() else '_insights.md not written yet_\n'
    w = an['window']
    L = []
    L.append('# Ethereum mainnet live scan: %s to %s UTC\n' % (w['first_utc'], w['last_utc']))
    L.append('Blocks %s to %s (%d blocks, %.2f h), %s transactions, %s logs. Prices at head block %s: ETH %s, BTC %s. Generated %s UTC by `scripts/live_scan.py`; '
             'the narrative section is written by the LLM from `analysis.json` and `head_state.json`, every table below is deterministic.\n'
             % (w['first_block'], w['last_block'], w['blocks'], w['hours'], f"{w['transactions']:,}", f"{w['logs']:,}", hs.get('block'),
                usd_fmt(an['price_basis'].get('ETH')), usd_fmt(an['price_basis'].get('BTC')), utc()))
    L.append(ins)
    L.append('\n---\n\n## A. Passive LP economics (fees to in-range liquidity, minus what just-in-time liquidity takes)\n')
    L.append('Per pool with at least 3 priced swaps and $200k of volume. `full-range capital` is the USD value a full-range position would need to hold the pool\'s in-range liquidity '
             '(2·L·√P); the band APRs scale that by the capital a ±1%% or ±0.1%% band needs for the same liquidity (×%.0f and ×%.0f) and assume the price stays inside the band, so they are '
             'gross ceilings before impermanent loss and rebalancing, not returns. `price range` is the max/min of the pool price in the window. Fees are the fee tier times input volume; '
             'v4 tiers come from the event, v3 tiers from `fee()`, v2-like pools are assumed 0.30%%.\n' % (1 / (1 - 1 / math.sqrt(1.01)), 1 / (1 - 1 / math.sqrt(1.001))))
    L.append('| pool | venue | pair | tier | swaps | volume | fees | to JIT | passive fees | full-range capital | APR full-range | APR ±1% band | price range |')
    L.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for r in an['lp'][:45]:
        L.append('| %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            link_addr(r['pool']) if r['venue'] != 'uniswap_v4' else short(r['pool']), r['venue'].replace('uniswap_', 'uni '), r['pair'], pct(r['fee_tier'], 2) if r['fee_tier'] is not None else '?', r['swaps'],
            usd_fmt(r['volume_usd']), usd_fmt(r['fees_usd']) if r['fees_usd'] else '–', usd_fmt(r['fees_to_jit_usd']) if r['fees_to_jit_usd'] else '$0',
            usd_fmt(r['passive_fees_usd']) if r['passive_fees_usd'] is not None else '–', usd_fmt(r['full_range_capital_usd']),
            pct(r.get('apr_full_range'), 2) if r.get('apr_full_range') is not None else '–', pct(r.get('apr_band_1pct'), 1) if r.get('apr_band_1pct') is not None else '–',
            ('%.3f%%' % r['price_range_pct']) if r.get('price_range_pct') is not None else '–'))
    j = an['jit']
    L.append('\nJust-in-time liquidity: %d episodes (mint and burn of identical liquidity inside one block), bracketing %s of swaps and taking about %s of fees. Operators:\n'
             % (j['episodes'], usd_fmt(j['swap_usd_bracketed']), usd_fmt(j['fee_taken_usd'])))
    for o in j['operators'][:8]:
        L.append('- %s: %d episodes, fees taken %s' % (link_addr(o['sender']), o['episodes'], usd_fmt(o['fee_taken_usd'])))
    L.append('\nSwap volume by venue: ' + ', '.join('%s %s (%d)' % (v, usd_fmt(x['usd']), x['n']) for v, x in an['swap_totals'].items()) + '.\n')
    if an.get('v4_unconfirmed'):
        L.append('\nUniswap v4 pools whose reported swap deltas were not matched by tokens moving through the PoolManager (hook-settled; excluded from volume): '
                 + '; '.join('%s (%s, %d swaps)' % (short(r['pool']), '/'.join(short(x) for x in (r['tokens'] or [])), r['swaps']) for r in an['v4_unconfirmed']) + '.\n')
    # lending
    L.append('\n## B. Lending: rates, utilisation, dispersion, health\n')
    L.append('Current reserve state at the head (`getReserveData`, aToken and variable-debt supply):\n')
    L.append('| venue | asset | supply APR | borrow APR | utilisation | supplied | borrowed |')
    L.append('|---|---|---|---|---|---|---|')
    for venue, rows in (hs.get('lending') or {}).items():
        for a, r in rows.items():
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (venue, r['sym'], pct(r['supply_apr']), pct(r['borrow_apr']), pct(r.get('utilisation'), 1), usd_fmt(r.get('supplied_usd')), usd_fmt(r.get('borrowed_usd'))))
    for name, c in (hs.get('compound') or {}).items():
        mult = an['price_basis'].get('ETH') if 'WETH' in name else 1.0
        L.append('| %s | base | %s | %s | %s | %s | %s |' % (name, pct(c['supply_apr']), pct(c['borrow_apr']), pct(c['utilisation'], 1), usd_fmt(c['supplied'] * mult) if c.get('supplied') else '–', usd_fmt(c['borrowed'] * mult) if c.get('borrowed') else '–'))
    sky, eth = hs.get('sky') or {}, hs.get('ethena') or {}
    L.append('\nSky savings rate (sUSDS) %s APY, DSR (sDAI) %s APY; sUSDe vesting implies %s APR on %s of USDe.\n' % (pct(sky.get('ssr_apy')), pct(sky.get('dsr_apy')), pct(eth.get('apr_from_vesting')), usd_fmt(eth.get('total_assets_usde'))))
    if hs.get('rate_curves'):
        # The curve source changed to `getInterestRateDataBps`, which reports base/slope1/slope2 and no max rate, so
        # the renderer reads what is there rather than a key that no longer exists.
        L.append('Rate curves: ' + '; '.join(
            '%s optimal %s, base %s, slope1 %s, slope2 %s%s' % (
                k, pct(v.get('optimal'), 0), pct(v.get('base'), 2), pct(v.get('slope1'), 2), pct(v.get('slope2'), 2),
                (', reserve factor %s' % pct(v['reserve_factor'], 0)) if v.get('reserve_factor') is not None else '')
            for k, v in sorted(hs['rate_curves'].items())) + '.\n')
    L.append('\nRate moves inside the window (`ReserveDataUpdated`, variable borrow APR range):\n')
    L.append('| venue | asset | updates | borrow first → last | borrow min–max | supply first → last |')
    L.append('|---|---|---|---|---|---|')
    for r in an['lending_rates'][:25]:
        L.append('| %s | %s | %d | %s → %s | %s – %s | %s → %s |' % (r['venue'], r['sym'], r['updates'], pct(r['borrow_first']), pct(r['borrow_last']), pct(r['borrow_min']), pct(r['borrow_max']), pct(r['supply_first']), pct(r['supply_last'])))
    lo = an['lending_ops']
    L.append('\nVolumes by venue and kind: ' + '; '.join('%s: %s' % (v, ', '.join('%s %s' % (k, usd_fmt(x)) for k, x in d.items())) for v, d in lo['totals'].items()) + '.\n')
    L.append('\nLargest operations (≥ $250k):\n')
    L.append('| block | venue | kind | asset | amount | account | tx |')
    L.append('|---|---|---|---|---|---|---|')
    for o in lo['large_ops'][:30]:
        L.append('| %d | %s | %s | %s | %s | %s | %s |' % (o['block'], o['venue'], o['kind'], o['sym'], usd_fmt(o['usd']), link_addr(o['account']), link_tx(o['tx'])))
    fol = [f for f in lo['proceeds_followed'] if f['hops']]
    if fol:
        L.append('\nWhere borrow/withdraw proceeds went (first hop within 60 min; exchange tags from the day-study address book and memory labels):\n')
        for f in fol[:20]:
            o = f['op']
            hops = '; '.join('%s → %s%s' % (usd_fmt(h['usd']), link_addr(h['to'], h['label'] or short(h['to'])), (' → forwarded to ' + (h['forwarded_to_exchange']['label'] or short(h['forwarded_to_exchange']['to']))) if h['forwarded_to_exchange'] else '') for h in f['hops'][:4])
            L.append('- %s %s %s %s by %s (%s): %s%s' % (o['venue'], o['kind'], usd_fmt(o['usd']), o['sym'], link_addr(o['account']), link_tx(o['tx']), hops, ' **[to exchange %s]**' % usd_fmt(f['to_exchange_usd']) if f['to_exchange_usd'] else ''))
    if hs.get('health'):
        L.append('\nHealth of the accounts active in the window (Aave/Spark `getUserAccountData` at the head):\n')
        L.append('| venue | account | collateral | debt | health factor | drop to liquidation |')
        L.append('|---|---|---|---|---|---|')
        for h in hs['health'][:25]:
            L.append('| %s | %s | %s | %s | %s | %s |' % (h['venue'], link_addr(h['account']), usd_fmt(h['collateral_usd']), usd_fmt(h['debt_usd']), ('%.3f' % h['health_factor']) if h['health_factor'] else '∞', pct(h['drop_to_liquidation'], 1) if h['drop_to_liquidation'] is not None else '–'))
    if an['liquidations']:
        L.append('\nLiquidations: ' + '; '.join('%s %s debt %s, collateral %s (%s)' % (l['venue'], link_addr(l['user']), usd_fmt(l['debt_usd']), usd_fmt(l['collateral_usd']), link_tx(l['tx'])) for l in an['liquidations'][:15]) + '.\n')
    fl = an['flash']
    L.append('\nFlash loans (events): ' + ', '.join('%s %d (%s)' % (k, v, usd_fmt(fl['usd'].get(k, 0))) for k, v in fl['count'].items()) + '.\n')
    if an.get('atomic_cycles'):
        L.append('\nAtomic borrow/repay or withdraw/supply cycles inside one transaction (a lending pool used as flash liquidity; excluded from the tables above):\n')
        for r in an['atomic_cycles'][:6]:
            L.append('- %s account %s: %d transactions, largest leg %s, gross %s; legs: %s' % (r['venue'], link_addr(r['account']), r['txs'], usd_fmt(r['largest_usd']), usd_fmt(r['gross_usd']), ', '.join('%s %s' % (k, usd_fmt(v)) for k, v in r['legs'].items())))
    # pegs
    L.append('\n## C. Stablecoin and LST implied prices versus NAV or par\n')
    L.append('Volume-weighted implied price from every priced swap in the window (the reference side is the stablecoin, WETH or BTC leg). NAV from the head-state rate reads.\n')
    L.append('| token | swaps | volume | implied USD (vw) | p10 – p90 | reference | deviation |')
    L.append('|---|---|---|---|---|---|---|')
    pb = an['price_basis']
    for sym, r in sorted(an['peg'].items(), key=lambda kv: -kv[1]['volume_usd']):
        ref = None
        t = next(((s, d, k) for a, (s, d, k) in TOKENS.items() if s == sym), None)
        if t:
            ref = pb.get(t[2])
        dev = (r['vw_price'] / ref - 1) if ref else None
        L.append('| %s | %d | %s | %.6g | %.6g – %.6g | %s | %s |' % (sym, r['n'], usd_fmt(r['volume_usd']), r['vw_price'], r['p10'], r['p90'], ('%.6g' % ref) if ref else '–', bps(dev) if dev is not None else '–'))
    # flows
    L.append('\n## D. Exchange flow, large transfers, round trips, scheduled flow\n')
    ef = an['exchange_flow']
    L.append('Net flow into tagged exchange wallets and deposit sinks by asset (address book: %d addresses; tags are behavioural from the day study plus memory labels):\n' % an['address_book_size'])
    L.append('| asset | in | out | net |')
    L.append('|---|---|---|---|')
    for k, v in list(ef['by_asset'].items())[:12]:
        L.append('| %s | %s | %s | %s |' % (k, usd_fmt(v['in']), usd_fmt(v['out']), usd_fmt(v['net'])))
    L.append('\nBy label: ' + '; '.join('%s in %s / out %s' % (r['label'], usd_fmt(r['in']), usd_fmt(r['out'])) for r in ef['by_label'][:12]) + '.\n')
    L.append('\nLargest transfers (≥ $5M, ERC-20 and native):\n')
    L.append('| block | asset | amount | from | to | tx |')
    L.append('|---|---|---|---|---|---|')
    for x in an['big_transfers'][:30]:
        L.append('| %d | %s | %s%s | %s | %s | %s |' % (x['block'], x['sym'], usd_fmt(x['usd']), (' ×%d' % x['count']) if x.get('count', 1) > 1 else '', link_addr(x['from'], None), link_addr(x['to'], None), link_tx(x['tx'])))
    if an['round_trips']:
        L.append('\nRound trips (≥ $10M out and back within the window): ' + '; '.join('%s %s from %s via %s, back after %.0f min' % (usd_fmt(r['usd']), r['sym'], link_addr(r['from']), link_addr(r['via']), r['minutes']) for r in an['round_trips']) + '.\n')
    sch = [r for r in an['scheduled'] if r['cv_gap'] < 0.6 and r['cv_size'] < 0.6]
    if sch:
        L.append('\nScheduled or programmatic flow (≥ 4 swaps by one sender in one direction; low dispersion of interval and size):\n')
        L.append('| sender | sells → buys | n | total | median size | median gap | cv gap | cv size | venues |')
        L.append('|---|---|---|---|---|---|---|---|---|')
        for r in sch[:15]:
            L.append('| %s | %s → %s | %d | %s | %s | %ds | %.2f | %.2f | %s |' % (link_addr(r['sender'], r['label']), r['sell'], r['buy'], r['n'], usd_fmt(r['total_usd']), usd_fmt(r['median_usd']), r['median_gap_s'], r['cv_gap'], r['cv_size'], ', '.join('%s %d' % kv for kv in r['venues'].items())))
    L.append('\nLargest swaps (≥ $1M):\n')
    L.append('| block | venue | sells → buys | size | sender | tx |')
    L.append('|---|---|---|---|---|---|')
    for s in an['big_swaps'][:20]:
        ti = next((v[0] for a, v in TOKENS.items() if a == s['tok_in']), short(s['tok_in']) if s['tok_in'] else '?')
        to = next((v[0] for a, v in TOKENS.items() if a == s['tok_out']), short(s['tok_out']) if s['tok_out'] else '?')
        L.append('| %d | %s | %s → %s | %s | %s | %s |' % (s['block'], s['venue'], ti, to, usd_fmt(s['usd']), link_addr(s['sender']), link_tx(s['tx'])))
    # bridges & issuance
    L.append('\n## E. Bridges, issuance, staking\n')
    br = an['bridges']
    L.append('Outbound: %s in the window (CCTP USDC burns and LayerZero OFT sends); inbound CCTP mints %s (%d).\n' % (usd_fmt(br['out_total_usd']), usd_fmt(br['cctp_in_usd']), br['cctp_in_n']))
    L.append('| kind | token | destination | n | amount | top recipient |')
    L.append('|---|---|---|---|---|---|')
    for r in br['out'][:20]:
        L.append('| %s | %s | %s | %d | %s | %s |' % (r['kind'], r['token'], r['destination'], r['n'], usd_fmt(r['usd']), ('%s %s' % (r['top_recipient'][0][:14] + '…', usd_fmt(r['top_recipient'][1]))) if r['top_recipient'] else '–'))
    iss = an['issuance']
    if iss.get('totals'):
        L.append('\nIssuance totals: ' + '; '.join('%s %s (%d)' % (k, usd_fmt(v['usd']), v['n']) for k, v in iss['totals'].items()) + '. Largest: '
                 + '; '.join('%s %s %s (%s)' % (i['token'], i['kind'], usd_fmt(i['usd']), link_tx(i['tx'])) for i in iss['largest'][:5]) + '.\n')
    L.append('\nWETH wrapped %.0f ETH, unwrapped %.0f ETH; Lido staked %.1f ETH, withdrawal requests %.1f ETH; sUSDe cooldowns %d for %s.\n'
             % (an['weth'].get('wrap', 0), an['weth'].get('unwrap', 0), an['lido'].get('stake_eth', 0), an['lido'].get('unstake_eth', 0), an['cooldowns']['n'], usd_fmt(an['cooldowns']['usd'])))
    # gas
    g = an['gas']
    L.append('\n## F. Gas market and block production\n')
    L.append('Base fee %s → %s gwei (min %s, median %s, max %s); blocks %.0f%% full; median tip %.3f gwei; %.1f%% of transactions pay zero tip; builders: %s.\n'
             % (g['base_fee_gwei']['first'], g['base_fee_gwei']['last'], g['base_fee_gwei']['min'], g['base_fee_gwei']['median'], g['base_fee_gwei']['max'], 100 * g['gas_used_share'], g['tip_median_gwei'], 100 * g['zero_tip_share'],
                ', '.join('%s %d' % (b or '?', c) for b, c in g['builders'][:6])))
    L.append('\nMost active senders: ' + ', '.join('%s %d' % (link_addr(s['address'], s['label']), s['txs']) for s in an['top_senders'][:10]) + '.\n')
    L.append('\nIntent fills: ' + ', '.join('%s %d' % kv for kv in an['intent_fills'].items()) + '. Unknown event topics: %d distinct in the top list; unpriced tokens seen: %d.\n' % (len(an['unknown_topics']), len(an['unpriced_tokens'])))
    if hs.get('token_registry_mismatches'):
        L.append('\nToken registry mismatches at the head (address not used for pricing): ' + '; '.join('%s expected %s got %s' % (m['address'], m['expected'], m['got']) for m in hs['token_registry_mismatches']) + '.\n')
    lp = out / 'live_log.md'
    if lp.exists():
        L.append('\n---\n\n## G. Live log\n')
        L.append(lp.read_text())
    (out / 'report.md').write_text('\n'.join(L) + '\n')
    print('wrote', out / 'report.md', len(L), 'lines')


# ----------------------------------------------------------------------------------------------------------------------
# Live loop
# ----------------------------------------------------------------------------------------------------------------------
def block_digest(st_prev, out, n, book, prices, markets, pools):
    """Decode one block on its own and return alert lines."""
    st = State(prices, book, market_cache=markets)
    for p, v in pools.items():
        if v.get('fee'):
            st.pool_fee[p] = v['fee']
        if v.get('tokens'):
            st.pool_tokens[p] = v['tokens']
    b = read_gz(block_path(out, n))
    logs = read_gz(logs_path(out, n))
    st.ingest(b, logs)
    ts = hx(b['timestamp'])
    lines = []
    for x in sorted(st.transfers, key=lambda x: -x['usd']):
        if x['usd'] >= 5e6:
            lines.append('transfer %s %s %s → %s (%s)' % (usd_fmt(x['usd']), x['sym'], link_addr(x['from'], st.label(x['from'])), link_addr(x['to'], st.label(x['to'])), link_tx(x['tx'])))
    for o in st.lending:
        if (o['usd'] or 0) >= 1e6:
            lines.append('lending %s %s %s %s account %s (%s)' % (o['venue'], o['kind'], usd_fmt(o['usd']), o['sym'], link_addr(o['account']), link_tx(o['tx'])))
    for l in st.liquidations:
        lines.append('**liquidation** %s user %s debt %s collateral %s (%s)' % (l['venue'], link_addr(l['user']), usd_fmt(l['debt_usd']), usd_fmt(l['collateral_usd']), link_tx(l['tx'])))
    for (venue, reserve), ser in st.rates.items():
        for (_, _, s_apr, b_apr) in ser:
            prev = st_prev.get((venue, reserve))
            if prev is not None and abs(b_apr - prev) >= 0.01:
                tk = prices.token(reserve)
                lines.append('**rate jump** %s %s borrow APR %s → %s' % (venue, tk[0] if tk else short(reserve), pct(prev), pct(b_apr)))
            st_prev[(venue, reserve)] = b_apr
    for s in st.swaps:
        if s['usd'] >= 2e6:
            ti = (prices.token(s['tok_in']) or (short(s['tok_in']),))[0] if s['tok_in'] else '?'
            to = (prices.token(s['tok_out']) or (short(s['tok_out']),))[0] if s['tok_out'] else '?'
            lines.append('swap %s %s → %s on %s by %s (%s)' % (usd_fmt(s['usd']), ti, to, s['venue'], link_addr(s['sender']), link_tx(s['tx'])))
    for x in st.bridges:
        if (x['usd'] or 0) >= 2e6:
            lines.append('bridge %s %s %s → %s (%s)' % (x['kind'], usd_fmt(x['usd']), x['token'], x['dst_name'], link_tx(x['tx'])))
    for i in st.issuance:
        if i['usd'] >= 5e6:
            lines.append('issuance %s %s %s (%s)' % (i['token'], i['kind'], usd_fmt(i['usd']), link_tx(i['tx'])))
    j = st.jit_summary()
    if j['episodes']:
        lines.append('JIT %d episode(s), %s of swaps bracketed, fees taken %s' % (j['episodes'], usd_fmt(j['swap_usd_bracketed']), usd_fmt(j['fee_taken_usd'])))
    bl = st.blocks[0]
    return ts, bl, lines


def live(args):
    out = Path(args.out)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    hs = json.loads((out / 'head_state.json').read_text())
    prices = Prices(hs)
    book = load_address_book()
    pools = json.loads((out / 'pools.json').read_text()) if (out / 'pools.json').exists() else {}
    markets = json.loads((out / 'markets.json').read_text()) if (out / 'markets.json').exists() else {}
    last_known = max(int(p.name.split('.')[0]) for p in (out / 'raw' / 'blocks').glob('*.json.gz'))
    log = out / 'live_log.md'
    if not log.exists():
        log.write_text('Live log started %s UTC at block %d. One line per block with anything notable; a rolling re-analysis of the trailing %.1f h every %d blocks rewrites the sections above.\n\n' % (utc(), last_known, args.hours, args.every))
    rate_prev = {}
    since_analysis = 0
    started = time.monotonic()
    print(json.dumps({'live_from': last_known + 1, 'every': args.every}), flush=True)
    while True:
        if args.max_minutes and (time.monotonic() - started) / 60 > args.max_minutes:
            print('max minutes reached', flush=True)
            return
        try:
            new, replaced, hn = tail_once(rpc, out, last_known, lag=args.lag)
        except RPCError as exc:
            print(json.dumps({'t': utc(), 'error': rpc.clean(str(exc))}), flush=True)
            time.sleep(5)
            continue
        for n in sorted(set(new) | set(replaced)):
            ts, bl, lines = block_digest(rate_prev, out, n, book, prices, markets, pools)
            head_line = '- **%d** %s base %.2f gwei, %d txs, %s%s' % (n, utc(ts)[11:19], bl['base_gwei'], bl['txs'], bl['builder'] or short(bl['miner']), ' (replaced after reorg)' if n in replaced else '')
            with log.open('a') as f:
                f.write(head_line + ('\n' if not lines else '\n' + ''.join('  - %s\n' % l for l in lines)))
            print(json.dumps({'block': n, 'alerts': len(lines), 'head': hn, **rpc.stats()}), flush=True)
        if new:
            last_known = max(new)
            since_analysis += len(new)
        if since_analysis >= args.every:
            since_analysis = 0
            try:
                first = last_known - int(args.hours * 300)
                st, nums = load_state(out, first, last_known, quiet=True)
                res = st.finish()
                res['price_basis'] = dict(st.p.usd)
                res['address_book_size'] = len(st.book)
                (out / 'analysis.json').write_text(json.dumps(res, indent=1, default=str))
                render(argparse.Namespace(out=str(out)))
                with log.open('a') as f:
                    f.write('- re-analysed blocks %d to %d at %s UTC: %d priced swaps, %d JIT episodes, %d lending ops ≥$250k, exchange net %s stables / %s ETH\n' % (
                        nums[0], nums[-1], utc()[11:19], len(st.swaps), res['jit']['episodes'], len(res['lending_ops']['large_ops']),
                        usd_fmt(sum(v['net'] for k, v in res['exchange_flow']['by_asset'].items() if k in STABLE_SYMBOLS)), usd_fmt(res['exchange_flow']['by_asset'].get('ETH', {}).get('net', 0))))
            except Exception as exc:
                print(json.dumps({'t': utc(), 'analysis_error': repr(exc)[:200]}), flush=True)
        time.sleep(args.poll)


# ----------------------------------------------------------------------------------------------------------------------
# Midnight routine check (targeted logs)
# ----------------------------------------------------------------------------------------------------------------------
def midnight(args):
    out = Path(args.out)
    rpc = RPC(log_path=out / 'rpc_errors.jsonl', max_credits=args.max_credits)
    hn, hts, _ = rpc_head(rpc)
    day = dt.datetime.fromisoformat(args.date + 'T00:00:00+00:00')
    t0 = int(day.timestamp()) - 45 * 60
    t1 = int(day.timestamp()) + 30 * 60
    a = first_block_at(rpc, t0, hn)
    b = first_block_at(rpc, t1, hn)
    usdc = '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'
    addrs = list(MIDNIGHT.values())
    pad = ['0x' + enc_addr(x) for x in addrs]
    rng = {'fromBlock': hex(a), 'toBlock': hex(b)}
    res = rpc.batch([
        ('eth_getLogs', [dict(rng, address=usdc, topics=[T['Transfer'], pad])]),
        ('eth_getLogs', [dict(rng, address=usdc, topics=[T['Transfer'], None, pad])]),
        ('eth_getLogs', [dict(rng, address=AAVE_POOL, topics=[T['AaveRDU'], '0x' + enc_addr(usdc)])]),
        ('eth_getLogs', [dict(rng, address=AAVE_POOL, topics=[[T['AaveWithdraw'], T['AaveSupply']], '0x' + enc_addr(usdc)])]),
    ], allow_errors=True)
    hdrs = {}
    need = sorted({hx(l['blockNumber']) for r in res if isinstance(r, list) for l in r})
    for i in range(0, len(need), 20):
        part = need[i:i + 20]
        for n, h in zip(part, rpc.batch([('eth_getBlockByNumber', [hex(n), False]) for n in part])):
            hdrs[n] = hx(h['timestamp'])
    names = {v: k for k, v in MIDNIGHT.items()}
    moves = []
    seen = set()
    for r in res[:2]:
        if not isinstance(r, list):
            continue
        for l in r:
            key = (l['transactionHash'], l['logIndex'])
            if key in seen:
                continue
            seen.add(key)
            f, t = topic_addr(l['topics'][1]), topic_addr(l['topics'][2])
            amt = word(l['data'], 0) / 1e6
            if amt >= 1e6:
                moves.append({'block': hx(l['blockNumber']), 'utc': utc(hdrs[hx(l['blockNumber'])]), 'usd': round(amt), 'from': names.get(f, f), 'to': names.get(t, t), 'tx': l['transactionHash']})
    moves.sort(key=lambda m: (m['block'], m['tx']))
    rates = []
    if isinstance(res[2], list):
        for l in res[2]:
            rates.append({'block': hx(l['blockNumber']), 'utc': utc(hdrs[hx(l['blockNumber'])]), 'supply_apr': word(l['data'], 0) / RAY, 'borrow_apr': word(l['data'], 2) / RAY})
    aave = []
    if isinstance(res[3], list):
        for l in res[3]:
            kind = 'withdraw' if l['topics'][0] == T['AaveWithdraw'] else 'supply'
            user = topic_addr(l['topics'][2]) if kind == 'withdraw' else '0x' + l['data'][2:66][-40:]
            amt = word(l['data'], 0 if kind == 'withdraw' else 1) / 1e6
            if amt >= 1e7:
                aave.append({'block': hx(l['blockNumber']), 'utc': utc(hdrs[hx(l['blockNumber'])]), 'kind': kind, 'user': names.get(user, user), 'usd': round(amt), 'tx': l['transactionHash']})
    result = {'date': args.date, 'blocks': [a, b], 'window_utc': [utc(t0), utc(t1)], 'usdc_moves_1m_plus': moves, 'aave_usdc_ops_10m_plus': aave,
              'aave_usdc_rates': rates, 'rate_max_borrow': max((r['borrow_apr'] for r in rates), default=None), 'rate_min_borrow': min((r['borrow_apr'] for r in rates), default=None),
              'recurred': any(m['from'] == 'hub' and m['to'] == 'holder' for m in moves), 'rpc': rpc.stats()}
    (out / ('midnight_%s.json' % args.date)).write_text(json.dumps(result, indent=1))
    print(json.dumps({k: v for k, v in result.items() if k not in ('aave_usdc_rates',)}, indent=1))
    print('rate path:', [(r['utc'][11:19], round(r['borrow_apr'], 4)) for r in rates[:: max(1, len(rates) // 25)]])


def show(args):
    """Decode every log of the given transactions from the raw files."""
    out = Path(args.out)
    hs = json.loads((out / 'head_state.json').read_text()) if (out / 'head_state.json').exists() else {}
    prices = Prices(hs)
    for h in args.hashes:
        found = None
        for p in sorted((out / 'raw' / 'blocks').glob('*.json.gz')):
            b = read_gz(p)
            t = next((x for x in b['transactions'] if x['hash'] == h), None)
            if t:
                found = (b, t)
                break
        if not found:
            print('not in raw files:', h)
            continue
        b, t = found
        n = hx(b['number'])
        logs = [l for l in read_gz(logs_path(out, n)) if l['transactionHash'] == h]
        print('tx %s block %d %s from %s to %s value %.4f ETH gas %d selector %s tip %.3f gwei' % (h, n, utc(hx(b['timestamp'])), t['from'], t.get('to'), hx(t.get('value', 0)) / 1e18, hx(t['gas']), t['input'][:10], tip_of(t, hx(b.get('baseFeePerGas', 0))) / 1e9))
        for l in logs:
            tp = l['topics']
            name = BY_TOPIC.get(tp[0], tp[0][:10]) if tp else 'anonymous'
            a = l['address'].lower()
            d = l['data']
            words = (len(d) - 2) // 64
            extra = ''
            if name == 'Transfer' and len(tp) == 3:
                tk = prices.token(a)
                extra = '%s → %s  %s %s' % (topic_addr(tp[1]), topic_addr(tp[2]), ('%.6f' % (word(d, 0) / 10 ** tk[1])) if tk else word(d, 0), tk[0] if tk else short(a))
            elif name == 'AaveRDU':
                extra = 'reserve %s supply %.4f%% borrow %.4f%%' % (topic_addr(tp[1]), 100 * word(d, 0) / RAY, 100 * word(d, 2) / RAY)
            elif name.startswith('Aave') or name.startswith('Morpho'):
                extra = 'topics ' + ' '.join(x[-40:][:10] + '…' for x in tp[1:]) + ' data ' + ' '.join(str(word(d, i)) for i in range(min(4, words)))
            elif name in ('V3Swap', 'V4Swap'):
                extra = 'a0 %d a1 %d L %d' % (sword(d, 0), sword(d, 1), word(d, 3))
            else:
                extra = 'topics %d data %d words' % (len(tp), words)
            print('  %4d %-16s %s %s' % (hx(l['logIndex']), name, short(a) if name != 'Transfer' else '', extra))


def verify_cmd(args):
    """Re-derive the headline numbers from raw through an independent path and assert the mechanism claims."""
    import subprocess
    cmd = [sys.executable, str(ROOT / 'scripts' / 'verify.py'), '--out', str(args.out)]
    if args.mechanisms:
        cmd.append('--mechanisms')
    raise SystemExit(subprocess.call(cmd))


def detect_cmd(args):
    """Run every registered detector over the window and write detectors.json + detectors.md."""
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / 'scripts' / 'detectors' / 'run.py'),
                                      '--out', str(args.out)]))


def pipeline_cmd(args):
    """analyze -> verify -> detect -> findings ingest, in the order the artifacts depend on each other.

    Run separately, these drift. `analysis.json` is built against the address book; `verify` re-derives its numbers and
    gates on that book; the detectors read the analysis; the ledger records what they found. Editing a label and
    re-running only `detect` leaves a stale analysis feeding fresh detectors, which is how two windows in this repo
    ended up quoting corrected labels beside uncorrected numbers. One command, one order, and `verify` still refuses
    to continue if the inputs moved underneath it.
    """
    import subprocess
    py = sys.executable
    steps = [('analyze', [py, __file__, 'analyze', '--out', str(args.out)]),
             ('verify', [py, str(ROOT / 'scripts' / 'verify.py'), '--out', str(args.out)]
                        + (['--mechanisms'] if args.mechanisms else [])),
             ('detect', [py, str(ROOT / 'scripts' / 'detectors' / 'run.py'), '--out', str(args.out)]),
             ('ledger', [py, str(ROOT / 'scripts' / 'findings.py'), 'ingest', '--out', str(args.out)])]
    for name, cmd in steps:
        print('\n=== %s ===' % name, flush=True)
        rc = subprocess.call(cmd)
        if rc:
            print('\n%s failed (exit %d); stopping so the later steps do not build on it.' % (name, rc))
            raise SystemExit(rc)
    print('\npipeline complete for %s' % args.out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('command', choices=['analyze', 'head', 'render', 'live', 'midnight', 'show', 'verify', 'detect',
                                       'pipeline'])
    p.add_argument('hashes', nargs='*')
    p.add_argument('--out', default=str(ROOT / 'research' / '2026-09-06' / 'live'))
    p.add_argument('--first', type=int)
    p.add_argument('--last', type=int)
    p.add_argument('--hours', type=float, default=1.0, help='live: trailing window to re-analyse')
    p.add_argument('--every', type=int, default=10, help='live: re-analyse every N new blocks')
    p.add_argument('--lag', type=int, default=0)
    p.add_argument('--poll', type=float, default=4.0)
    p.add_argument('--max-minutes', type=float, default=0)
    p.add_argument('--date', default='2026-09-06', help='midnight: UTC date whose 00:00 is checked')
    p.add_argument('--max-credits', type=int, default=6_000_000)
    p.add_argument('--mechanisms', action='store_true', help='verify: also run the source-backed mechanism assertions')
    p.add_argument('--force', action='store_true', help='head: read current state even for a window collected long ago')
    args = p.parse_args()
    {'analyze': analyze, 'head': head_state, 'render': render, 'live': live, 'midnight': midnight, 'show': show,
     'verify': verify_cmd, 'detect': detect_cmd, 'pipeline': pipeline_cmd}[args.command](args)


if __name__ == '__main__':
    main()
