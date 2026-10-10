#!/usr/bin/env python3
"""Liquid staking tokens outside Ethereum, two ways to be paid: queue bids and delta-neutral staked collateral.

Why. The repo's only family that survived two history tests is the queue bid: holders who will not wait for a
redemption queue sell the liquid staking token (LST) below what the protocol pays, and a patient bidder buys it and
redeems. On Ethereum it priced weETH, stETH, rsETH and LBTC (`dislocation_history.py`). Off Ethereum the queues are
longer and the bidders fewer, so the same claim might pay more. Second, the HYPE spot / short-perp carry survived
because the spot is the short's collateral on the same venue (`term_carry.py`); with a staked token as that collateral
the excess becomes staking yield + funding - costs - SSR. This script asks both questions.

    D=research/2026-10-10/queue_bids_alt
    uv run --with pycryptodome python scripts/queue_bids_alt.py screen  --out $D
    uv run --with pycryptodome python scripts/queue_bids_alt.py collect --out $D --parts ohlcv,khype,jito,prices,llama,hyperlend,solsnap,capctx
    uv run --with pycryptodome python scripts/queue_bids_alt.py collect --out $D --parts rates --assets sts,slisbnb,aprmon
    uv run --with pycryptodome python scripts/queue_bids_alt.py collect --out $D --parts rates --assets savax --thin 4
    uv run --with pycryptodome python scripts/queue_bids_alt.py collect --out $D --parts khype_swaps --last-block 27999999
    uv run --with pycryptodome python scripts/queue_bids_alt.py collect --out $D --parts khype_swaps --first-block 28000000 --last-block 48185268
    uv run --with pycryptodome python scripts/queue_bids_alt.py analyze --out $D
    uv run --with pycryptodome python scripts/queue_bids_alt.py render  --out $D
    uv run --with pytest --with pycryptodome python -m pytest scripts/test_queue_bids_alt.py -q

kHYPE gets the full treatment (the only off-Ethereum LST with a multi-day queue and over $1M a day of DEX volume): its
swaps are rebuilt from kHYPE/WHYPE transfers into and out of every pool since launch (GeckoTerminal's 180 days are kept
as an independent price path), its exchange rate is read every ~3 hours from the StakingAccountant, and every
withdrawal request and confirmation since launch is decoded to check what the queue paid and how long it took. The bid
reuses `queue_book.simulate_book` (the shared rule that reproduces `dislocation_history.simulate_bid`) and
`backtest.choose_then_test`; the carry reuses `term_carry.run_carry_block` with the staking yield as the spot leg's
extra accrual.

Data. Pools and hourly OHLCV come from GeckoTerminal's free API (about 30 calls a minute shared with other workers on
this IP, so one call every `GT_MIN_INTERVAL` seconds and a minute's back-off on 429; the public API serves only the
last 180 days). Exchange rates come from the protocols' own view functions read through public archive RPCs (checked
against `latest` first: several public HyperEVM endpoints ignore the block tag and return today's state), or from the
protocols' public APIs where the chain has no archive. Queue events (requests, claims, fees) are read from the chain
where an archive with getLogs exists. Funding comes from the repo's stores (Hyperliquid, Binance) and Drift's public
data API. Everything is read-only; no keys are written.

Conventions. `discount_bps` is positive when the LST traded BELOW its exchange rate (the native amount the protocol
pays per token). Prices are in native units per LST (`currency=token`, `token=<LST side>`): GeckoTerminal then quotes
the volume in the other token's units, i.e. native. Zero-volume bars are dropped.
"""
import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import backtest as B  # noqa: E402
import drpc  # noqa: E402
from dislocation_history import (sel, interp, pct, market_discount_fn, daily_values,  # noqa: E402
                                 capacity_size, apr_from_nav, _bisect_right)

ROOT = Path(__file__).resolve().parents[1]
UTC = dt.timezone.utc
DAY = 86400
HOUR = 3600
UA = 'llm-quant research (read-only)'
GT = 'https://api.geckoterminal.com/api/v2'
GT_MIN_INTERVAL = 6.0          # seconds between GeckoTerminal calls: the free tier is ~30/min per IP and other workers share it
GT_HORIZON_DAYS = 180          # the public API refuses OHLCV older than 180 days (401: "past 180 days with Public API")
SSR = 0.038                    # Sky savings rate today (the dollar benchmark)
SAVINGS_PAID = {2023: 0.029, 2024: 0.078, 2025: 0.055, 2026: 0.037}   # what the savings rate actually paid, by year


def utc(ts=None):
    return dt.datetime.fromtimestamp(ts if ts is not None else time.time(), UTC).strftime('%Y-%m-%dT%H:%M:%SZ')


def ymd(ts):
    return dt.datetime.fromtimestamp(ts, UTC).strftime('%Y-%m-%d')


def day_ts(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d').replace(tzinfo=UTC).timestamp())


def read_gz(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    with gzip.open(p, 'rt') as f:
        return json.load(f)


def write_gz(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    with gzip.open(tmp, 'wt') as f:
        json.dump(obj, f, separators=(',', ':'))
    tmp.replace(p)


def read_json(path, default=None):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + '\n')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def log_line(out, msg):
    line = '%s %s' % (utc(), msg)
    print(line, flush=True)
    with open(Path(out) / 'collect.log', 'a') as f:
        f.write(line + '\n')


# ----------------------------------------------------------------------------------------------------------------------
# HTTP: polite GeckoTerminal client and plain JSON GET
# ----------------------------------------------------------------------------------------------------------------------
class Http:
    """JSON GET with a minimum interval between calls and a long back-off on 429 (the IP is shared)."""

    def __init__(self, min_interval=1.0, backoff=65.0, retries=8):
        self.min_interval, self.backoff, self.retries = min_interval, backoff, retries
        self.last = 0.0
        self.calls = self.errors = self.throttled = 0

    def get(self, url, params=None, headers=None, allow_status=()):
        if params:
            url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        h = {'Accept': 'application/json', 'User-Agent': UA}
        h.update(headers or {})
        last_err = None
        for attempt in range(self.retries):
            wait = self.min_interval - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.time()
            self.calls += 1
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=60) as r:
                    body = r.read()
                    if r.headers.get('Content-Encoding') == 'gzip':
                        body = gzip.decompress(body)
                    return json.loads(body)
            except urllib.error.HTTPError as e:
                if e.code in allow_status:
                    try:
                        return {'_status': e.code, '_body': json.loads(e.read())}
                    except Exception:
                        return {'_status': e.code}
                if e.code == 429:
                    self.throttled += 1
                    time.sleep(self.backoff * (1 + 0.5 * attempt))
                    continue
                self.errors += 1
                last_err = 'HTTP %s' % e.code
                if e.code in (400, 401, 403, 404):
                    raise
                time.sleep(5 * (attempt + 1))
            except Exception as e:  # noqa: BLE001 (transport)
                self.errors += 1
                last_err = str(e)[:160]
                time.sleep(5 * (attempt + 1))
        raise RuntimeError('GET failed after retries: %s (%s)' % (url[:120], last_err))


_GT = None


def gt():
    global _GT
    if _GT is None:
        _GT = Http(min_interval=GT_MIN_INTERVAL)
    return _GT


def gt_token_pools(network, token, page=1):
    d = gt().get('%s/networks/%s/tokens/%s/pools' % (GT, network, urllib.parse.quote(token, safe='')),
                 {'page': page}, allow_status=(404,))
    return d


def gt_ohlcv_page(network, pool, token_side, before=None, timeframe='hour', aggregate=1):
    p = {'aggregate': aggregate, 'limit': 1000, 'currency': 'token', 'token': token_side}
    if before:
        p['before_timestamp'] = int(before)
    return gt().get('%s/networks/%s/pools/%s/ohlcv/%s' % (GT, network, urllib.parse.quote(pool, safe=''), timeframe), p,
                    allow_status=(401, 404))


# ----------------------------------------------------------------------------------------------------------------------
# The candidates. Facts marked (read) were read on chain on 2026-10-10; (docs) come from protocol documentation and
# are listed as such in the analysis. Liquidity decides which ones get the full treatment.
# ----------------------------------------------------------------------------------------------------------------------
WHYPE = '0x5555555555555555555555555555555555555555'
WAVAX = '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'
WBNB = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
WS = '0x039e2fb66102314ce7b64ce5ce3e5183bc94ad38'
WMON = '0x3bd359c1119da7da1d913d1c4d2b7c461115433a'
WBERA = '0x6969696969696969696969696969696969696969'
WSOL = 'So11111111111111111111111111111111111111112'
SUI = '0x2::sui::SUI'
APT_FA = '0xa'
APT_COIN = '0x1::aptos_coin::AptosCoin'
WNEAR = 'wrap.near'
TON_NATIVE = 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c'
NATIVE0 = '0x0000000000000000000000000000000000000000'

NATIVES = {
    'hyperevm': {WHYPE}, 'avax': {WAVAX}, 'bsc': {WBNB}, 'sonic': {WS}, 'monad': {WMON, NATIVE0}, 'berachain': {WBERA},
    'solana': {WSOL}, 'sui-network': {SUI, '0x0000000000000000000000000000000000000000000000000000000000000002::sui::SUI'},
    'aptos': {APT_FA, APT_COIN}, 'near': {WNEAR}, 'ton': {TON_NATIVE},
    'hydration': {'5'},
}

# endpoints that answer historical eth_call correctly (verified against `latest` by `check_archive`)
ARCHIVE = {
    'hyperevm': ['https://rpc.hyperlend.finance/archive', 'https://hyperliquid.drpc.org'],
    'avax': ['https://api.avax.network/ext/bc/C/rpc'],
    'sonic': ['https://rpc.soniclabs.com', 'https://sonic-rpc.publicnode.com', 'https://sonic.drpc.org'],
    'monad': ['https://rpc2.monad.xyz'],          # rpc1 and monadinfra answer single calls but 403 any JSON-RPC batch
    'berachain': ['https://rpc.berachain.com', 'https://berachain.drpc.org'],
    'bsc': ['https://bsc.drpc.org', 'https://bsc-mainnet.public.blastapi.io', 'https://bsc-dataseed.bnbchain.org'],
}
# endpoints known to IGNORE the block tag on eth_call (they return latest state for any block): never use for history
NOT_ARCHIVE = {'hyperevm': ['https://rpc.hyperliquid.xyz/evm', 'https://rpc.hypurrscan.io', 'https://hyperliquid-json-rpc.stakely.io']}

KINETIQ_SM = '0x393d0b87ed38fc779fd9611144ae649ba6082109'        # StakingManager (router), kHYPE's minter and burner
KINETIQ_ACC = '0x9209648ec9d448ef57116b73a2f081835643dc7a'       # StakingAccountant: kHYPEToHYPE(uint256)

CANDIDATES = [
    # --- Hyperliquid (HyperCore staking: 7-day unstaking queue) ---
    {'key': 'khype', 'symbol': 'kHYPE', 'network': 'hyperevm', 'token': '0xfd739d4e423301ce9385c1fb8850539d657c296d',
     'native': 'HYPE', 'queue_days': 7.0, 'queue_src': 'StakingManager.withdrawalDelay() = 604,800 s (read)',
     'fee_bps': 0.0, 'fee_src': 'StakingManager.unstakeFeeRate() = 0 (read); history from UnstakeFeeRateUpdated events',
     'redeem': 'anyone: queueWithdrawal(kHYPE) then confirmWithdrawal(id) after the delay (read: source)',
     'instant': 'none: instantUnstake facet not deployed (calls revert SelectorNotFound, read)',
     'rate': {'kind': 'evm_call', 'to': KINETIQ_ACC, 'sig': 'kHYPEToHYPE(uint256)', 'arg': 10 ** 18}},
    {'key': 'sthype', 'symbol': 'stHYPE', 'network': 'hyperevm', 'token': '0xffaa4a3d97fe9107cef8a3f48c069f577ff76cc1',
     'native': 'HYPE', 'queue_days': 7.0, 'queue_src': 'docs (Valantis/Thunderhead overseer)', 'fee_bps': 0.0,
     'redeem': 'anyone via the overseer (docs)', 'instant': 'Valantis STEX AMM'},
    {'key': 'wsthype', 'symbol': 'wstHYPE', 'network': 'hyperevm', 'token': '0x94e8396e0869c9f2200760af0621afd240e1cf38',
     'native': 'HYPE', 'queue_days': 7.0, 'queue_src': 'docs', 'fee_bps': 0.0, 'redeem': 'unwrap to stHYPE', 'instant': ''},
    {'key': 'behype', 'symbol': 'beHYPE', 'network': 'hyperevm', 'token': '0xd8fc8f0b03eba61f64d08b0bef69d80916e5dda9',
     'native': 'HYPE', 'queue_days': 7.0, 'queue_src': 'docs (ether.fi)', 'fee_bps': 0.0,
     'redeem': 'anyone (docs)', 'instant': 'instant withdrawal with a fee when liquidity allows (docs)'},
    {'key': 'lhype', 'symbol': 'LHYPE', 'network': 'hyperevm', 'token': '0x5748ae796ae46a4f1348a1693de4b50560485562',
     'native': 'HYPE', 'queue_days': None, 'queue_src': 'looped vault, not a plain LST', 'fee_bps': None,
     'redeem': 'vault redemption', 'instant': ''},
    {'key': 'mhype', 'symbol': 'mHYPE', 'network': 'hyperevm', 'token': '0xdabb040c428436d41cecd0fb06bcfdbaad3a9aa8',
     'native': 'HYPE', 'queue_days': 7.0, 'queue_src': 'docs', 'fee_bps': None, 'redeem': '', 'instant': ''},
    # --- Avalanche ---
    {'key': 'savax', 'symbol': 'sAVAX', 'network': 'avax', 'token': '0x2b2c81e08f1af8835a78bb2a90ae924ace0ea4be',
     'native': 'AVAX', 'queue_days': 15.0, 'queue_src': 'cooldownPeriod() (read)', 'fee_bps': 0.0,
     'redeem': 'anyone: requestUnlock then redeem inside the redeem window', 'instant': '',
     'rate': {'kind': 'evm_call', 'to': '0x2b2c81e08f1af8835a78bb2a90ae924ace0ea4be', 'sig': 'getPooledAvaxByShares(uint256)', 'arg': 10 ** 18}},
    {'key': 'ggavax', 'symbol': 'ggAVAX', 'network': 'avax', 'token': '0xa25eaf2906fa1a3a13edac9b9657108af7b703e3',
     'native': 'AVAX', 'queue_days': 0.0, 'queue_src': 'ERC-4626 redeem from the liquidity buffer (docs)', 'fee_bps': 0.0,
     'redeem': 'anyone, up to the buffer', 'instant': 'the vault itself'},
    # --- BNB Chain ---
    {'key': 'slisbnb', 'symbol': 'slisBNB', 'network': 'bsc', 'token': '0xb0b84d294e0c75a6abe60171b70edeb2efd14a1b',
     'native': 'BNB', 'queue_days': 8.0, 'queue_src': 'StakeHub.unbondPeriod() = 604,800 s (read) + the bot batch (docs: 7-8 days)',
     'fee_bps': 0.0, 'redeem': 'anyone: requestWithdraw fixes the BNB amount at the request; claimWithdraw when claimable',
     'instant': 'instantWithdraw is whitelist-only (instantWhitelistOff() = false, read)',
     'rate': {'kind': 'evm_call', 'to': '0x1adb950d8bb3da4be104211d5ab038628e477fe6', 'sig': 'convertSnBnbToBnb(uint256)', 'arg': 10 ** 18}},
    {'key': 'bnbx', 'symbol': 'BNBx', 'network': 'bsc', 'token': '0x1bdd3cf7f79cfb8edbb955f20ad99211551ba275',
     'native': 'BNB', 'queue_days': 8.0, 'queue_src': 'docs (Stader: 7-15 days)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': ''},
    {'key': 'asbnb', 'symbol': 'asBNB', 'network': 'bsc', 'token': '0x77734e70b6e88b4d82fe632a168edf6e700912b6',
     'native': 'BNB', 'queue_days': 8.0, 'queue_src': 'docs (Astherus, on slisBNB)', 'fee_bps': None, 'redeem': '', 'instant': ''},
    # --- Sonic ---
    {'key': 'sts', 'symbol': 'stS', 'network': 'sonic', 'token': '0xe5da20f15420ad15de0fa650600afc998bbe3955',
     'native': 'S', 'queue_days': 14.0, 'queue_src': 'withdrawDelay() (read)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': '',
     'rate': {'kind': 'evm_call', 'to': '0xe5da20f15420ad15de0fa650600afc998bbe3955', 'sig': 'getRate()', 'arg': None}},
    {'key': 'os', 'symbol': 'OS', 'network': 'sonic', 'token': '0xb1e25689d55734fd3fffc939c4c3eb52dff8a794',
     'native': 'S', 'queue_days': 1.0, 'queue_src': 'docs (Origin vault, ARM)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': 'ARM'},
    # --- Monad / Berachain ---
    {'key': 'aprmon', 'symbol': 'aprMON', 'network': 'monad', 'token': '0x0c65a0bc65a5d819235b71f554d210d3f80e0852',
     'native': 'MON', 'queue_days': 1.0, 'queue_src': 'withdrawalDelay() = 1 (epochs, read); Monad unbonding (docs)',
     'fee_bps': None, 'redeem': 'anyone: ERC-7540 requestRedeem then redeem', 'instant': '',
     'rate': {'kind': 'evm_call', 'to': '0x0c65a0bc65a5d819235b71f554d210d3f80e0852', 'sig': 'convertToAssets(uint256)', 'arg': 10 ** 18}},
    {'key': 'shmon', 'symbol': 'shMON', 'network': 'monad', 'token': '0x1b68626dca36c7fe922fd2d55e4f631d962de19c',
     'native': 'MON', 'queue_days': None, 'queue_src': 'docs (FastLane)', 'fee_bps': None, 'redeem': 'anyone', 'instant': ''},
    {'key': 'smon', 'symbol': 'sMON', 'network': 'monad', 'token': '0xa3227c5969757783154c60bf0bc1944180ed81b9',
     'native': 'MON', 'queue_days': None, 'queue_src': 'docs (Kintsu)', 'fee_bps': None, 'redeem': 'anyone', 'instant': ''},
    {'key': 'ibera', 'symbol': 'iBERA', 'network': 'berachain', 'token': '0x9b6761bf2397bb5a6624a856cc84a3a14dcd3fe5',
     'native': 'BERA', 'queue_days': None, 'queue_src': 'docs (Infrared)', 'fee_bps': None, 'redeem': '', 'instant': ''},
    # --- Solana (one-epoch deactivation; Sanctum's instant unstake routes any pool's stake to SOL for a fee) ---
    {'key': 'jitosol', 'symbol': 'JitoSOL', 'network': 'solana', 'token': 'J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn',
     'native': 'SOL', 'queue_days': 2.5, 'queue_src': 'one epoch, ~2-3 days (docs)', 'fee_bps': 0.0,
     'redeem': 'anyone: withdraw stake, deactivate', 'instant': 'Sanctum router / Infinity, fee'},
    {'key': 'jupsol', 'symbol': 'JupSOL', 'network': 'solana', 'token': 'jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v',
     'native': 'SOL', 'queue_days': 2.5, 'queue_src': 'one epoch (docs)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': 'Sanctum'},
    {'key': 'bsol', 'symbol': 'bSOL', 'network': 'solana', 'token': 'bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1',
     'native': 'SOL', 'queue_days': 2.5, 'queue_src': 'one epoch (docs)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': 'Sanctum'},
    {'key': 'hsol', 'symbol': 'hSOL', 'network': 'solana', 'token': 'he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A',
     'native': 'SOL', 'queue_days': 2.5, 'queue_src': 'one epoch (docs)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': 'Sanctum'},
    {'key': 'msol', 'symbol': 'mSOL', 'network': 'solana', 'token': 'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
     'native': 'SOL', 'queue_days': 2.5, 'queue_src': 'one epoch (docs)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': 'Marinade pool, Sanctum'},
    {'key': 'inf', 'symbol': 'INF', 'network': 'solana', 'token': '5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm',
     'native': 'SOL', 'queue_days': 0.0, 'queue_src': 'Infinity pool redeems to SOL (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': 'itself'},
    {'key': 'bnsol', 'symbol': 'BNSOL', 'network': 'solana', 'token': 'BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85',
     'native': 'SOL', 'queue_days': 2.5, 'queue_src': 'one epoch (docs)', 'fee_bps': 0.0, 'redeem': 'anyone', 'instant': 'Sanctum'},
    # --- Sui / Aptos / NEAR / TON / Polkadot ---
    {'key': 'hasui', 'symbol': 'haSUI', 'network': 'sui-network',
     'token': '0xbde4ba4c2e274a60ce15c1cfff9e5c42e41654ac8b6d906a57efa4bd3c29f47d::hasui::HASUI',
     'native': 'SUI', 'queue_days': 1.0, 'queue_src': 'one epoch (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': 'Haedal instant, fee'},
    {'key': 'afsui', 'symbol': 'afSUI', 'network': 'sui-network',
     'token': '0xf325ce1300e8dac124071d3152c5c5ee6174914f8bc2161e88329cf579246efc::afsui::AFSUI',
     'native': 'SUI', 'queue_days': 1.0, 'queue_src': 'one epoch (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': 'Aftermath instant, fee'},
    {'key': 'vsui', 'symbol': 'vSUI', 'network': 'sui-network',
     'token': '0x549e8b69270defbfafd4f94e17ec44cdbdd99820b33bda2278dea3b9a32d3f55::cert::CERT',
     'native': 'SUI', 'queue_days': 1.0, 'queue_src': 'one epoch (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': 'Volo instant, fee'},
    {'key': 'amapt', 'symbol': 'amAPT', 'network': 'aptos', 'token': None, 'search': 'amapt',
     'native': 'APT', 'queue_days': 30.0, 'queue_src': 'Aptos lockup cycle, up to 30 days (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': ''},
    {'key': 'thapt', 'symbol': 'thAPT', 'network': 'aptos', 'token': None, 'search': 'thapt',
     'native': 'APT', 'queue_days': 30.0, 'queue_src': 'Aptos lockup cycle (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': ''},
    {'key': 'linear', 'symbol': 'LiNEAR', 'network': 'near', 'token': 'linear-protocol.near',
     'native': 'NEAR', 'queue_days': 2.5, 'queue_src': '4 epochs, ~52-65 h (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': 'LiNEAR pool, fee'},
    {'key': 'stnear', 'symbol': 'stNEAR', 'network': 'near', 'token': 'meta-pool.near',
     'native': 'NEAR', 'queue_days': 2.5, 'queue_src': '4 epochs (docs)', 'fee_bps': None, 'redeem': 'anyone', 'instant': 'Meta Pool liquidity, fee'},
    {'key': 'tston', 'symbol': 'tsTON', 'network': 'ton', 'token': 'EQC98_qAmNEptUtPc7W6xdHh_ZHrBUFpw5Ft_IzNU20QAJav',
     'native': 'TON', 'queue_days': 1.5, 'queue_src': 'end of the validation round, ~18-36 h (docs)', 'fee_bps': None,
     'redeem': 'anyone', 'instant': 'Tonstakers instant when the pool has liquidity'},
    {'key': 'vdot', 'symbol': 'vDOT', 'network': 'hydration', 'token': '15',
     'native': 'DOT', 'queue_days': 28.0, 'queue_src': 'Polkadot unbonding 28 days (docs)', 'fee_bps': None, 'redeem': 'anyone via Bifrost', 'instant': ''},
]
CAND = {c['key']: c for c in CANDIDATES}
# Not on GeckoTerminal at all (no Osmosis/Cosmos/Stride coverage): recorded as an API gap, not guessed.
NOT_COVERED = {'stTIA': 'Osmosis (Stride), 21 days', 'milkTIA': 'Osmosis (MilkyWay), 21 days', 'stATOM': 'Osmosis (Stride), 21 days',
               'vDOT/DOT pair': 'Bifrost DEX (not indexed); Hydration quotes vDOT against H2O only'}


def other_side(pool, network, token):
    """(lst_side, other_token_id) of a GeckoTerminal pool row, or (None, None) when the LST is not one of its two sides."""
    rel = pool['relationships']
    base = rel['base_token']['data']['id'].split('_', 1)[1]
    quote = rel['quote_token']['data']['id'].split('_', 1)[1]
    t = (token or '').lower()
    if base.lower() == t:
        return 'base', quote
    if quote.lower() == t:
        return 'quote', base
    return None, None


def is_native(network, tok):
    return tok in NATIVES.get(network, set()) or tok.lower() in {x.lower() for x in NATIVES.get(network, set())}


def screen_rows(cand, pools):
    """Pools of one LST against its own native coin, from GeckoTerminal pool rows."""
    rows = []
    for p in pools:
        side, oth = other_side(p, cand['network'], cand['token'])
        if side is None or not is_native(cand['network'], oth):
            continue
        a = p['attributes']
        rows.append({'pool': a['address'], 'name': a['name'], 'dex': p['relationships']['dex']['data']['id'],
                     'lst_side': side, 'reserve_usd': float(a.get('reserve_in_usd') or 0),
                     'vol24_usd': float((a.get('volume_usd') or {}).get('h24') or 0),
                     'created': a.get('pool_created_at'), 'fee_pct': fee_from_name(a['name'])})
    rows.sort(key=lambda r: -r['vol24_usd'])
    return rows


def fee_from_name(name):
    """GeckoTerminal appends the fee tier to concentrated-liquidity pool names ('kHYPE / WHYPE 0.01%')."""
    for tok in reversed(name.split()):
        if tok.endswith('%'):
            try:
                return float(tok[:-1])
            except ValueError:
                return None
    return None


def cmd_screen(args):
    out = Path(args.out)
    (out / 'raw').mkdir(parents=True, exist_ok=True)
    cache = read_gz(out / 'raw' / 'screen_pools.json.gz', {}) or {}
    keys = [k.strip() for k in args.assets.split(',')] if args.assets else [c['key'] for c in CANDIDATES]
    for k in keys:
        c = CAND[k]
        if k in cache and not args.refresh:
            continue
        pools, status = [], None
        if c.get('token'):
            for page in (1, 2):
                d = gt_token_pools(c['network'], c['token'], page)
                if not d or d.get('_status') or not d.get('data'):
                    status = (d or {}).get('_status') if page == 1 else status
                    break
                pools += d['data']
                if len(d['data']) < 20:
                    break
        else:
            d = gt().get('%s/search/pools' % GT, {'query': c['search'], 'network': c['network']})
            pools = d.get('data', [])
            for p in pools:            # adopt the LST's id from the first pool naming it
                for s in ('base_token', 'quote_token'):
                    tid = p['relationships'][s]['data']['id'].split('_', 1)[1]
                    if c['symbol'].lower() in p['attributes']['name'].lower().split(' / ')[0 if s == 'base_token' else -1].lower() and not is_native(c['network'], tid):
                        c['token'] = c['token'] or tid
        cache[k] = {'at': utc(), 'token': c.get('token'), 'pools': pools, 'status': status}
        write_gz(out / 'raw' / 'screen_pools.json.gz', cache)
        log_line(out, 'screen %s: %d pools' % (k, len(pools)))
    rows = []
    for k in keys:
        c = dict(CAND[k])
        c['token'] = c.get('token') or cache.get(k, {}).get('token')
        pr = screen_rows(c, cache.get(k, {}).get('pools', []))
        rows.append({'key': k, 'symbol': c['symbol'], 'network': c['network'], 'native': c['native'],
                     'token': c['token'], 'gt_status': cache.get(k, {}).get('status'),
                     'queue_days': c['queue_days'], 'queue_src': c['queue_src'], 'instant': c.get('instant'),
                     'vol24_native_pairs_usd': sum(r['vol24_usd'] for r in pr),
                     'reserve_native_pairs_usd': sum(r['reserve_usd'] for r in pr), 'pools': pr})
    rows.sort(key=lambda r: -r['vol24_native_pairs_usd'])
    write_json(out / 'screen.json', {'at': utc(), 'rows': rows, 'not_covered': NOT_COVERED,
                                     'http': {'calls': gt().calls, 'errors': gt().errors, 'throttled': gt().throttled}})
    for r in rows:
        print('%-8s %-11s %12.0f %12.0f  queue %s  pools %d' % (r['symbol'], r['network'], r['vol24_native_pairs_usd'],
                                                                r['reserve_native_pairs_usd'], r['queue_days'], len(r['pools'])))


# ----------------------------------------------------------------------------------------------------------------------
# EVM archive reads (batched JSON-RPC), block grids, event logs
# ----------------------------------------------------------------------------------------------------------------------
class Evm:
    """Batched JSON-RPC over a list of archive endpoints, rotating on failure, with a pause between batches."""

    def __init__(self, endpoints, pause=0.15, batch=25):
        self.endpoints, self.pause, self.batch = list(endpoints), pause, batch
        self.calls = self.errors = 0
        self.last = 0.0

    def _post(self, url, payload, timeout=90):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={'Content-Type': 'application/json', 'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())

    def many(self, calls):
        """[(method, params)] -> [result or {'error': ...}] in order; transport failures retried across endpoints."""
        out = []
        for i in range(0, len(calls), self.batch):
            chunk = calls[i:i + self.batch]
            payload = [{'jsonrpc': '2.0', 'id': j, 'method': m, 'params': pr} for j, (m, pr) in enumerate(chunk)]
            res, last = None, None
            for attempt in range(6):
                url = self.endpoints[attempt % len(self.endpoints)]
                wait = self.pause - (time.time() - self.last)
                if wait > 0:
                    time.sleep(wait)
                self.last = time.time()
                self.calls += 1
                try:
                    r = self._post(url, payload)
                    if isinstance(r, dict):          # some nodes answer a batch with one error object
                        raise RuntimeError(str(r)[:160])
                    by = {x.get('id'): x for x in r}
                    if any(('error' in by.get(j, {}) and 'rate' in str(by[j]['error']).lower()) for j in range(len(chunk))):
                        raise RuntimeError('rate limited')
                    res = [by.get(j, {}).get('result', {'error': by.get(j, {}).get('error', 'missing')}) for j in range(len(chunk))]
                    break
                except Exception as e:  # noqa: BLE001
                    self.errors += 1
                    last = str(e)[:160]
                    time.sleep(2.0 * (attempt + 1))
            if res is None:
                raise RuntimeError('batch failed on all endpoints: %s' % last)
            out += res
        return out

    def one(self, method, params):
        return self.many([(method, params)])[0]


def word_int(h, i=0):
    h = h[2:] if h.startswith('0x') else h
    return int(h[64 * i:64 * (i + 1)] or '0', 16)


def call_data(sig, arg=None):
    return sel(sig) + ('' if arg is None else '%064x' % int(arg))


def find_deploy_block(evm, address, lo, hi):
    """First block at which `address` has code (binary search on eth_getCode)."""
    while lo < hi:
        mid = (lo + hi) // 2
        code = evm.one('eth_getCode', [address, hex(mid)])
        if isinstance(code, str) and len(code) > 2:
            hi = mid
        else:
            lo = mid + 1
    return lo


def collect_block_times(evm, blocks, path):
    """{block: timestamp} for `blocks`, cached in `path` (resumable)."""
    have = {int(k): v for k, v in (read_gz(path, {}) or {}).items()}
    need = [b for b in blocks if b not in have]
    for i in range(0, len(need), 200):
        chunk = need[i:i + 200]
        res = evm.many([('eth_getBlockByNumber', [hex(b), False]) for b in chunk])
        for b, r in zip(chunk, res):
            if isinstance(r, dict) and r.get('timestamp'):
                have[b] = int(r['timestamp'], 16)
        write_gz(path, {str(k): v for k, v in sorted(have.items())})
    return have


def collect_rate_samples(evm, cand, blocks, path, log=None):
    """[(block, rate)] of the candidate's exchange-rate view at each block, resumable. Reverts are kept as None."""
    rt = cand['rate']
    data = call_data(rt['sig'], rt.get('arg'))
    have = {int(k): v for k, v in (read_gz(path, {}) or {}).items()}
    need = [b for b in blocks if b not in have]
    scale = float(rt.get('arg') or 10 ** 18)
    for i in range(0, len(need), 200):
        chunk = need[i:i + 200]
        res = evm.many([('eth_call', [{'to': rt['to'], 'data': data}, hex(b)]) for b in chunk])
        for b, r in zip(chunk, res):
            have[b] = (word_int(r) / scale) if isinstance(r, str) and len(r) >= 66 else None
        write_gz(path, {str(k): v for k, v in sorted(have.items())})
        if log:
            log('rates %s: %d/%d' % (cand['key'], min(i + 200, len(need)), len(need)))
    return have


def collect_logs(evm, address, topics, first, last, path, span=100_000, log=None):
    """All logs of `address` matching `topics` in [first, last], fetched in `span`-block windows, resumable by window."""
    st = read_gz(path, {'done': [], 'logs': []}) or {'done': [], 'logs': []}
    done = {tuple(x) for x in st['done']}
    windows = [(a, min(a + span - 1, last)) for a in range(first, last + 1, span)]
    todo = [w for w in windows if w not in done]
    for k in range(0, len(todo), 10):
        chunk = todo[k:k + 10]
        res = evm.many([('eth_getLogs', [{'address': address, 'topics': topics, 'fromBlock': hex(a), 'toBlock': hex(b)}])
                        for a, b in chunk])
        for (a, b), r in zip(chunk, res):
            if isinstance(r, list):
                st['logs'] += [{'block': int(x['blockNumber'], 16), 'tx': x['transactionHash'], 'li': int(x['logIndex'], 16),
                                'address': x['address'].lower(), 'topics': x['topics'], 'data': x['data']} for x in r]
                st['done'].append([a, b])
            else:
                raise RuntimeError('getLogs %d-%d failed: %s' % (a, b, str(r)[:200]))
        write_gz(path, st)
        if log:
            log('logs %s: %d/%d windows, %d logs' % (address[:10], len(st['done']), len(windows), len(st['logs'])))
    return st['logs']


def block_at(evm, ts, lo=1, hi=None):
    """Last block with timestamp <= ts (binary search on headers)."""
    hi = hi or int(evm.one('eth_blockNumber', []), 16)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        h = evm.one('eth_getBlockByNumber', [hex(mid), False])
        if int(h['timestamp'], 16) <= ts:
            lo = mid
        else:
            hi = mid - 1
    return lo


def block_grid(evm, start_ts, end_ts, step_s, anchors=96):
    """Blocks roughly every `step_s` seconds between two times: anchors read from headers, targets interpolated."""
    last = int(evm.one('eth_blockNumber', []), 16)
    b0 = block_at(evm, start_ts, 1, last)
    ab = sorted({b0 + (last - b0) * i // anchors for i in range(anchors + 1)})
    hs = evm.many([('eth_getBlockByNumber', [hex(b), False]) for b in ab])
    at = [int(h['timestamp'], 16) for h in hs]
    out = sorted({int(round(interp(at, ab, t))) for t in range(int(start_ts), int(min(end_ts, at[-1])) + 1, int(step_s))} | {last})
    return out


# ----------------------------------------------------------------------------------------------------------------------
# GeckoTerminal OHLCV (hourly, the last 180 days)
# ----------------------------------------------------------------------------------------------------------------------
def collect_ohlcv(network, pool, lst_side, path, now=None, log=None, max_age_h=12):
    """Every hourly bar GeckoTerminal will serve for the pool (newest first, paginated with before_timestamp), with the
    price in native per LST and the volume in native units. Skips pools fetched within `max_age_h` hours."""
    now = int(now or time.time())
    cur = read_gz(path)
    if cur and cur.get('complete') and now - cur.get('fetched', 0) < max_age_h * 3600:
        return cur
    horizon = now - GT_HORIZON_DAYS * DAY + 2 * HOUR
    bars, before, meta, pages, stop = {}, None, None, 0, None
    while True:
        d = gt_ohlcv_page(network, pool, lst_side, before=before)
        pages += 1
        if d.get('_status'):
            stop = 'status %s: %s' % (d['_status'], str(d.get('_body'))[:160])
            break
        meta = meta or d.get('meta')
        lst = d.get('data', {}).get('attributes', {}).get('ohlcv_list') or []
        for row in lst:
            bars[int(row[0])] = [float(x) for x in row[1:6]]
        if not lst:
            stop = 'empty page'
            break
        oldest = min(int(r[0]) for r in lst)
        if oldest <= horizon or len(lst) < 1000:
            stop = 'horizon' if oldest <= horizon else 'short page (history starts)'
            break
        before = oldest
    out = {'network': network, 'pool': pool, 'lst_side': lst_side, 'fetched': now, 'pages': pages, 'stop': stop,
           'complete': True, 'meta': meta, 'bars': [[t] + bars[t] for t in sorted(bars)]}
    write_gz(path, out)
    if log:
        log('ohlcv %s %s: %d bars, %d pages, stop=%s' % (network, pool[:12], len(bars), pages, stop))
    return out


def pools_for(screen, key, min_vol24=1000.0, min_reserve=50_000.0, top=6):
    """The pools worth a history: the LST against its native coin, with some volume or depth today."""
    row = next((r for r in screen['rows'] if r['key'] == key), None)
    if not row:
        return []
    ps = [p for p in row['pools'] if p['vol24_usd'] >= min_vol24 or p['reserve_usd'] >= min_reserve]
    return ps[:top]


# ----------------------------------------------------------------------------------------------------------------------
# Kinetiq (kHYPE) queue events
# ----------------------------------------------------------------------------------------------------------------------
def kq_topics():
    from dislocation_history import keccak
    return {
        'queued': keccak('WithdrawalQueued(address,address,uint256,uint256,uint256,uint256)'),
        'confirmed': keccak('WithdrawalConfirmed(address,uint256,uint256)'),
        'cancelled': keccak('WithdrawalCancelled(address,uint256,uint256,uint256)'),
        'fee_rate': keccak('UnstakeFeeRateUpdated(uint256)'),
        'delay': keccak('WithdrawalDelayUpdated(uint256)'),
        'paused': keccak('WithdrawalPaused(address)'),
        'unpaused': keccak('WithdrawalUnpaused(address)'),
        'stake': keccak('StakeReceived(address,address,uint256)'),
    }


# Every kHYPE/WHYPE venue that carried meaningful flow since launch, found by ranking kHYPE transfer counterparties on
# seven sample days (2025-08 .. 2026-02) and keeping the ones whose token0/token1 are WHYPE and kHYPE (read), plus
# GeckoTerminal's list. Fees (bp) from GeckoTerminal's pool names where shown; Valantis's STEX fee is dynamic and paid
# inside the swap amounts, so its nominal 1bp only enters the bid's buy-back cost.
KHYPE_POOLS = {
    '0xbe352daf66af94ccf2012a154a67daef95facb91': ('project-x', 1.0),
    '0x5cbe810071de393de35e574fb2830e16da794bab': ('hyperswap-v3', 1.0),
    '0x88b214ec94276b825e641820d5c97a9042f9dd60': ('valantis-stex', 1.0),
    '0xf9051e71aa3acfd4502eb69dd2d475cc525cc5f6': ('ramses-v3-2025', 1.0),       # GeckoTerminal: Ramses v3 0.01%, created 2025-07-15
    '0x7a37621a2a490214f03e6ce7199aeca9b7c565cc': ('kittenswap-algebra', 5.0),
    '0x705d5dda03d170384eb43eb1aa692a6fc548306f': ('ramses-v3', 0.8),
    '0xa83d60b1a9ca6dd1d0d2d9275c700114f2f3a8d6': ('nest', 1.0),
    '0x955dadf7bd49c941b6c5f9c19ee845c656cff85d': ('hybra-v4', 1.2),
    '0x7ca42c636f68717f0d84e5c9f0991bb7858060da': ('hybra-v3', 1.0),
}


def pad32(a):
    return '0x' + '0' * 24 + a[2:].lower()


def swaps_from_transfers(logs, pools, token_a, token_b):
    """Swaps of each pool from ERC-20 transfers in and out of it, grouped by (tx, pool): a swap moves one token in and
    the other out; liquidity adds and removes move both the same way and are dropped. `logs` are raw getLogs entries
    (deduplicated here by tx and log index). Returns [(block, tx, pool, side, amount_a, amount_b)], side 's' when
    token_a went INTO the pool (a holder sold token_a)."""
    seen, flows, blk = set(), collections.defaultdict(lambda: [0.0, 0.0]), {}
    pools = {p.lower() for p in pools}
    ta, tb = token_a.lower(), token_b.lower()
    for lg in logs:
        key = (lg['transactionHash'], lg['logIndex'])
        if key in seen:
            continue
        seen.add(key)
        tok = lg['address'].lower()
        if tok not in (ta, tb) or len(lg['topics']) < 3:
            continue
        i = 0 if tok == ta else 1
        frm = '0x' + lg['topics'][1][-40:]
        to = '0x' + lg['topics'][2][-40:]
        amt = int(lg['data'], 16) / 1e18 if lg['data'] not in ('0x', '') else 0.0
        b = int(lg['blockNumber'], 16)
        if frm in pools:
            flows[(lg['transactionHash'], frm)][i] -= amt
            blk[(lg['transactionHash'], frm)] = b
        if to in pools:
            flows[(lg['transactionHash'], to)][i] += amt
            blk[(lg['transactionHash'], to)] = b
    out = []
    for (tx, pool), (da, db) in flows.items():
        if da > 0 and db < 0:
            out.append((blk[(tx, pool)], tx, pool, 's', da, -db))
        elif da < 0 and db > 0:
            out.append((blk[(tx, pool)], tx, pool, 'b', -da, db))
    out.sort()
    return out


def collect_pool_swaps(evm, token_a, token_b, pools, first, last, outdir, span=50_000, shard=2_000_000, log=None):
    """Swap-level history of `pools` from token transfers, in `span`-block windows (split on the node's 20k-result cap),
    stored per `shard` blocks (resumable)."""
    from dislocation_history import keccak
    TR = keccak('Transfer(address,address,uint256)')
    padded = [pad32(p) for p in pools]
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    def fetch(a, b):
        q = [('eth_getLogs', [{'address': [token_a, token_b], 'topics': [TR, None, padded], 'fromBlock': hex(a), 'toBlock': hex(b)}]),
             ('eth_getLogs', [{'address': [token_a, token_b], 'topics': [TR, padded], 'fromBlock': hex(a), 'toBlock': hex(b)}])]
        r = evm.many(q)
        if all(isinstance(x, list) for x in r):
            return r[0] + r[1]
        err = ' '.join(str(x)[:200] for x in r if not isinstance(x, list))
        if 'max results' in err or 'too many' in err.lower() or 'limit' in err.lower():
            if b - a < 50:
                raise RuntimeError('cannot split %d-%d: %s' % (a, b, err))
            m = (a + b) // 2
            return fetch(a, m) + fetch(m + 1, b)
        raise RuntimeError('getLogs %d-%d: %s' % (a, b, err))

    for s0 in range(first - first % shard, last + 1, shard):
        fn = outdir / ('shard_%d.json.gz' % (s0 // shard))
        st = read_gz(fn, None) or {'done': [], 'swaps': []}
        done = {tuple(x) for x in st['done']}
        lo, hi = max(first, s0), min(last, s0 + shard - 1)
        wins = [(a, min(a + span - 1, hi)) for a in range(lo, hi + 1, span)]
        todo = [w for w in wins if w not in done]
        if not todo:
            continue
        for a, b in todo:
            logs = fetch(a, b)
            sw = swaps_from_transfers(logs, pools, token_a, token_b)
            st['swaps'] += [[x[0], x[1][:18], x[2], x[3], x[4], x[5]] for x in sw]
            st['done'].append([a, b])
        write_gz(fn, st)
        if log:
            log('pool swaps shard %d: %d windows, %d swaps' % (s0 // shard, len(st['done']), len(st['swaps'])))


# ----------------------------------------------------------------------------------------------------------------------
# Jito (JitoSOL) stake pool statistics: daily TVL and supply -> exchange rate
# ----------------------------------------------------------------------------------------------------------------------
def collect_jito(path, start='2024-01-01'):
    body = json.dumps({'bucket_type': 'Daily', 'range_filter': {'start': start + 'T00:00:00Z', 'end': utc()},
                       'sort_by': {'field': 'BlockTime', 'order': 'Asc'}}).encode()
    req = urllib.request.Request('https://kobe.mainnet.jito.network/api/v1/stake_pool_stats', data=body,
                                 headers={'Content-Type': 'application/json', 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read())
    tvl = {x['date']: x['data'] for x in d.get('tvl', [])}
    sup = {x['date']: x['data'] for x in d.get('supply', [])}
    apy = {x['date']: x['data'] for x in d.get('apy', [])}
    rows = []
    for k in sorted(tvl):
        if k in sup and sup[k]:
            ts = int(dt.datetime.strptime(k, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC).timestamp())
            rows.append({'ts': ts, 'utc': k, 'rate': tvl[k] / 1e9 / sup[k], 'tvl_sol': tvl[k] / 1e9, 'supply': sup[k], 'apy': apy.get(k)})
    write_gz(path, {'fetched': int(time.time()), 'rows': rows})
    return rows


# ----------------------------------------------------------------------------------------------------------------------
# DefiLlama yield charts (independent staking-yield path) and HyperLend reserve state (the margin's borrow cost)
# ----------------------------------------------------------------------------------------------------------------------
LLAMA_POOLS = {'bnsol': '9e709e57-84eb-496b-82ce-2e8f6a17db1b', 'jitosol': '0e7d0722-9054-4907-8593-567b353c0900',
               'savax': '3790c3e5-8644-4f6b-8feb-12434d8b99f9', 'slisbnb': '50bb5f69-85ea-4f70-81da-3661a1633fc4'}
HYPERLEND_POOL = '0x00a89d7a5a02160f20150ebea7a2b5e4879a1a8b'
HYPERLEND_ASSETS = {'USDT0': '0xb8ce59fc3717ada4c02eadf9682a9e934f625ebb', 'USDC': '0xb88339cb7199b77e23db6e890353e22632ba630f',
                    'WHYPE': WHYPE, 'kHYPE': '0xfd739d4e423301ce9385c1fb8850539d657c296d'}


def collect_llama(path):
    http = Http(min_interval=1.0)
    out = read_gz(path, {}) or {}
    for k, pid in LLAMA_POOLS.items():
        d = http.get('https://yields.llama.fi/chart/' + pid)
        out[k] = [{'ts': int(dt.datetime.strptime(x['timestamp'][:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=UTC).timestamp()),
                   'apy': x.get('apy'), 'apyBase': x.get('apyBase'), 'tvl': x.get('tvlUsd')} for x in d.get('data', [])]
    write_gz(path, out)
    return out


def collect_hyperlend(evm, blocks, path, log=None):
    """getReserveData(asset) at each block: the variable borrow index (word 3) gives the realised borrow cost between
    samples, word 4 the instantaneous rate (ray), word 0 the configuration (LTV bits 0-15, liquidation threshold 16-31)."""
    have = read_gz(path, {}) or {}
    for name, asset in HYPERLEND_ASSETS.items():
        cur = have.get(name, {})
        need = [b for b in blocks if str(b) not in cur]
        for i in range(0, len(need), 100):
            chunk = need[i:i + 100]
            res = evm.many([('eth_call', [{'to': HYPERLEND_POOL, 'data': sel('getReserveData(address)') + '0' * 24 + asset[2:]}, hex(b)])
                            for b in chunk])
            for b, r in zip(chunk, res):
                if isinstance(r, str) and len(r) >= 2 + 64 * 5:
                    cfg = word_int(r, 0)
                    cur[str(b)] = {'borrow_index': word_int(r, 3) / 1e27, 'borrow_rate': word_int(r, 4) / 1e27,
                                   'supply_rate': word_int(r, 2) / 1e27, 'ltv_bps': cfg & 0xFFFF, 'lt_bps': (cfg >> 16) & 0xFFFF}
                else:
                    cur[str(b)] = None
            have[name] = cur
            write_gz(path, have)
        if log:
            log('hyperlend %s: %d samples' % (name, len(cur)))
    return have


# ----------------------------------------------------------------------------------------------------------------------
# Solana snapshot: on-chain stake-pool rate and fees against Jupiter's best instant exit and entry, by size
# ----------------------------------------------------------------------------------------------------------------------
SOL_POOLS = {'JitoSOL': ('Jito4APyf642JPZPx3hGc6WWJ8zPKtRbRs4P815Awbb', 'J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn'),
             'JupSOL': ('8VpRhuxa7sUUepdY3kQiTmX9rS5vx4WgaXiAnXq4KCtr', 'jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v'),
             'bSOL': ('stk9ApL5HeVAwPLr3TLhDXdZS8ptVu7zp6ov8HFDuMi', 'bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1'),
             'BNSOL': ('Hr9pzexrBge3vgmBNRR8u42CNQgBXdHm4UkUN2DH4a7r', 'BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85')}


def parse_spl_stake_pool(d):
    """SPL stake-pool account (borsh): total lamports, pool token supply, last update epoch and the fees that matter."""
    import struct
    o = 1 + 32 * 3 + 1 + 32 * 5
    total, supply, epoch = struct.unpack_from('<QQQ', d, o)
    o += 24 + 48

    def fee():
        nonlocal o
        den, num = struct.unpack_from('<QQ', d, o)
        o += 16
        return num / den if den else 0.0

    def future():
        nonlocal o
        tag = d[o]
        o += 1
        return fee() if tag else None

    def opt_pk():
        nonlocal o
        tag = d[o]
        o += 1
        if tag:
            o += 32
    epoch_fee = fee()
    future()
    opt_pk()
    opt_pk()
    stake_dep = fee()
    stake_wd = fee()
    future()
    o += 1
    opt_pk()
    sol_dep = fee()
    o += 1
    opt_pk()
    sol_wd = fee()
    return {'rate': total / supply if supply else None, 'total_sol': total / 1e9, 'supply': supply / 1e9, 'epoch': epoch,
            'epoch_fee': epoch_fee, 'stake_withdrawal_fee_bps': 1e4 * stake_wd, 'sol_withdrawal_fee_bps': 1e4 * sol_wd,
            'stake_deposit_fee_bps': 1e4 * stake_dep, 'sol_deposit_fee_bps': 1e4 * sol_dep}


def collect_sol_snapshot(path):
    import base64
    http = Http(min_interval=1.2)

    def srpc(m, prm):
        req = urllib.request.Request('https://api.mainnet-beta.solana.com', data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': m, 'params': prm}).encode(),
                                     headers={'Content-Type': 'application/json', 'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    out = {'at': utc(), 'pools': {}}
    for name, (acct, mint) in SOL_POOLS.items():
        v = srpc('getAccountInfo', [acct, {'encoding': 'base64'}])['result']['value']
        st = parse_spl_stake_pool(base64.b64decode(v['data'][0]))
        quotes = []
        for n_lst in (10, 100, 1000, 10000, 50000):
            for side in ('sell', 'buy'):
                if side == 'sell':
                    q = {'inputMint': mint, 'outputMint': WSOL, 'amount': int(n_lst * 1e9), 'slippageBps': 50}
                else:
                    q = {'inputMint': WSOL, 'outputMint': mint, 'amount': int(n_lst * st['rate'] * 1e9), 'slippageBps': 50}
                try:
                    d = http.get('https://lite-api.jup.ag/swap/v1/quote', q)
                except Exception as e:  # noqa: BLE001
                    quotes.append({'lst': n_lst, 'side': side, 'error': str(e)[:120]})
                    continue
                ia, oa = int(d['inAmount']) / 1e9, int(d['outAmount']) / 1e9
                px = (oa / ia) if side == 'sell' else (ia / oa)           # SOL per LST
                quotes.append({'lst': n_lst, 'side': side, 'sol_per_lst': px, 'vs_rate_bps': 1e4 * (px / st['rate'] - 1.0),
                               'route': [x['swapInfo'].get('label') for x in d.get('routePlan', [])]})
        out['pools'][name] = {'stake_pool': st, 'quotes': quotes}
    write_gz(path, out)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# Capacity context today: Hyperliquid perp open interest and book depth, HyperLend caps for the kHYPE collateral leg
# ----------------------------------------------------------------------------------------------------------------------
def collect_capacity_context(path):
    def post(body):
        req = urllib.request.Request('https://api.hyperliquid.xyz/info', data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json', 'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    out = {'at': utc(), 'hl': {}, 'hyperlend': {}}
    meta = post({'type': 'metaAndAssetCtxs'})
    for a, c in zip(meta[0]['universe'], meta[1]):
        if a['name'] in ('HYPE', 'SOL', 'BTC', 'ETH'):
            out['hl'][a['name']] = {'oi_usd': float(c['openInterest']) * float(c['markPx']), 'volume_24h_usd': float(c['dayNtlVlm']),
                                    'funding_hourly': float(c['funding']), 'mark': float(c['markPx']), 'max_leverage': a.get('maxLeverage')}
            time.sleep(0.5)
            b = post({'type': 'l2Book', 'coin': a['name'], 'nSigFigs': 4})
            lv = b.get('levels') or [[], []]
            if lv[0] and lv[1]:
                mid = (float(lv[0][0]['px']) + float(lv[1][0]['px'])) / 2

                def depth(levels, bp):
                    return sum(float(x['px']) * float(x['sz']) for x in levels if abs(float(x['px']) / mid - 1) * 1e4 <= bp)
                out['hl'][a['name']].update({'bid_25bp_usd': depth(lv[0], 25), 'ask_25bp_usd': depth(lv[1], 25)})
    evm = Evm(ARCHIVE['hyperevm'], pause=0.2, batch=10)
    for name, asset in HYPERLEND_ASSETS.items():
        r = evm.one('eth_call', [{'to': HYPERLEND_POOL, 'data': sel('getReserveData(address)') + '0' * 24 + asset[2:]}, 'latest'])
        cfg = word_int(r, 0)
        a_tok = '0x' + r[2 + 64 * 8 + 24: 2 + 64 * 9]
        d_tok = '0x' + r[2 + 64 * 10 + 24: 2 + 64 * 11]
        sup, debt = evm.many([('eth_call', [{'to': a_tok, 'data': sel('totalSupply()')}, 'latest']),
                              ('eth_call', [{'to': d_tok, 'data': sel('totalSupply()')}, 'latest'])])
        dec = (cfg >> 48) & 0xFF
        out['hyperlend'][name] = {'ltv_bps': cfg & 0xFFFF, 'lt_bps': (cfg >> 16) & 0xFFFF, 'decimals': dec,
                                  'borrow_cap_tokens': (cfg >> 80) & ((1 << 36) - 1), 'supply_cap_tokens': (cfg >> 116) & ((1 << 36) - 1),
                                  'supplied_tokens': word_int(sup) / 10 ** dec if isinstance(sup, str) else None,
                                  'borrowed_tokens': word_int(debt) / 10 ** dec if isinstance(debt, str) else None,
                                  'borrow_rate_now': word_int(r, 4) / 1e27}
    write_gz(path, out)
    return out


# ----------------------------------------------------------------------------------------------------------------------
# collect
# ----------------------------------------------------------------------------------------------------------------------
HYPEREVM_STEP = 10_800          # blocks between rate samples (~3 hours at ~1 block a second)
DEEP = ['khype', 'jitosol', 'jupsol', 'bsol', 'msol', 'slisbnb', 'sts', 'savax', 'tston', 'lhype', 'aprmon', 'hasui']


def cmd_collect(args):
    out = Path(args.out)
    raw = out / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    log = lambda m: log_line(out, m)  # noqa: E731
    screen = read_json(out / 'screen.json')
    if not screen:
        raise SystemExit('run screen first')
    parts = set(args.parts.split(','))
    keys = [k.strip() for k in args.assets.split(',')] if args.assets else DEEP
    if 'ohlcv' in parts:
        for k in keys:
            for p in pools_for(screen, k):
                fn = raw / 'ohlcv' / ('%s__%s.json.gz' % (CAND[k]['network'], p['pool'].replace(':', '_')))
                try:
                    collect_ohlcv(CAND[k]['network'], p['pool'], p['lst_side'], fn, log=log)
                except Exception as e:  # noqa: BLE001
                    log('ohlcv %s %s FAILED: %s' % (k, p['pool'][:12], str(e)[:200]))
    if 'khype' in parts:
        evm = Evm(ARCHIVE['hyperevm'])
        last = int(evm.one('eth_blockNumber', []), 16)
        st = read_json(raw / 'khype_state.json', {}) or {}
        if 'deploy_block' not in st:
            st['deploy_block'] = find_deploy_block(evm, CAND['khype']['token'], 1, last)
            st['accountant_deploy_block'] = find_deploy_block(evm, KINETIQ_ACC, 1, last)
            st['manager_deploy_block'] = find_deploy_block(evm, KINETIQ_SM, 1, last)
            write_json(raw / 'khype_state.json', st)
        st['last_block'] = last
        write_json(raw / 'khype_state.json', st)
        log('khype deploy %s, accountant %s, manager %s, last %d' % (st['deploy_block'], st['accountant_deploy_block'],
                                                                     st['manager_deploy_block'], last))
        first = max(st['accountant_deploy_block'], st['deploy_block'])
        blocks = list(range(first + 1, last + 1, HYPEREVM_STEP)) + [last]
        collect_block_times(evm, blocks, raw / 'blocks_hyperevm.json.gz')
        collect_rate_samples(evm, CAND['khype'], blocks, raw / 'rates' / 'khype.json.gz', log=log)
        T = kq_topics()
        collect_logs(evm, KINETIQ_SM, [[T[x] for x in ('queued', 'confirmed', 'cancelled', 'fee_rate', 'delay', 'paused', 'unpaused')]],
                     st['manager_deploy_block'], last, raw / 'queue' / 'khype_events.json.gz', log=log)
        log('khype collect done; rpc calls %d errors %d' % (evm.calls, evm.errors))
    if 'rates' in parts:
        for k in [x for x in keys if CAND.get(x, {}).get('rate') and CAND[x]['network'] != 'hyperevm']:
            c = CAND[k]
            evm = Evm(ARCHIVE[c['network']], pause=1.0 if c['network'] == 'monad' else 0.3, batch=10 if c['network'] == 'monad' else 20)
            fn = raw / 'rates' / ('%s.json.gz' % k)
            bfn = raw / ('blocks_%s.json.gz' % c['network'])
            try:
                gfn = raw / ('grid_%s.json' % c['network'])
                grid = read_json(gfn)
                if not grid:
                    grid = block_grid(evm, time.time() - 215 * DAY, time.time(), 3 * HOUR)
                    write_json(gfn, grid)
                if args.thin > 1:
                    grid = sorted(set(grid[::args.thin]) | {grid[-1]})
                collect_block_times(evm, grid, bfn)
                collect_rate_samples(evm, c, grid, fn, log=log)
                log('rates %s done: %d samples, rpc calls %d errors %d' % (k, len(grid), evm.calls, evm.errors))
            except Exception as e:  # noqa: BLE001
                log('rates %s FAILED: %s' % (k, str(e)[:200]))
    if 'prices' in parts:
        p = collect_prices(raw / 'prices_usd.json.gz')
        log('prices: %s' % ', '.join('%s %d' % (k, len(v)) for k, v in p.items() if not k.startswith('_')))
    if 'khype_swaps' in parts:
        evm = Evm(ARCHIVE['hyperevm'], pause=0.2, batch=2)
        st = read_json(raw / 'khype_state.json')
        last = int(evm.one('eth_blockNumber', []), 16) if not args.last_block else args.last_block
        collect_pool_swaps(evm, CAND['khype']['token'], WHYPE, list(KHYPE_POOLS), args.first_block or st['deploy_block'], last,
                           raw / 'khype_swaps', log=log)
        if not args.first_block:
            st['swaps_last_block'] = last
            write_json(raw / 'khype_state.json', st)
        log('khype swaps done to block %d; rpc calls %d errors %d' % (last, evm.calls, evm.errors))
    if 'llama' in parts:
        d = collect_llama(raw / 'rates' / 'llama_yields.json.gz')
        log('llama: %s' % ', '.join('%s %d' % (k, len(v)) for k, v in d.items()))
    if 'hyperlend' in parts:
        evm = Evm(ARCHIVE['hyperevm'], pause=0.2, batch=25)
        bt = {int(k): v for k, v in read_gz(raw / 'blocks_hyperevm.json.gz').items()}
        daily = sorted(bt)[::8]                                   # every 8th 3-hour sample: daily
        collect_hyperlend(evm, daily, raw / 'rates' / 'hyperlend.json.gz', log=log)
    if 'capctx' in parts:
        d = collect_capacity_context(raw / 'capacity_context.json.gz')
        log('capacity context: HL %s; HyperLend %s' % (', '.join(d['hl']), ', '.join(d['hyperlend'])))
    if 'solsnap' in parts:
        d = collect_sol_snapshot(raw / 'sol_snapshot.json.gz')
        log('sol snapshot: %s' % ', '.join('%s %.6f' % (k, v['stake_pool']['rate']) for k, v in d['pools'].items()))
    if 'jito' in parts:
        rows = collect_jito(raw / 'rates' / 'jitosol_jito_api.json.gz')
        log('jito: %d daily rows, last rate %.6f' % (len(rows), rows[-1]['rate'] if rows else float('nan')))


# ----------------------------------------------------------------------------------------------------------------------
# Native prices (USD) for sizing: Binance USD-M daily closes
# ----------------------------------------------------------------------------------------------------------------------
PRICE_SYMBOLS = {'HYPE': 'HYPEUSDT', 'SOL': 'SOLUSDT', 'BNB': 'BNBUSDT', 'AVAX': 'AVAXUSDT', 'S': 'SUSDT',
                 'TON': 'TONUSDT', 'SUI': 'SUIUSDT', 'MON': 'MONUSDT', 'NEAR': 'NEARUSDT', 'APT': 'APTUSDT', 'BERA': 'BERAUSDT'}


def collect_prices(path, start='2025-01-01'):
    http = Http(min_interval=0.3)
    have = read_gz(path, {}) or {}
    t0 = day_ts(start) * 1000
    for nat, sym in PRICE_SYMBOLS.items():
        rows, t = {}, t0
        while True:
            try:
                d = http.get('https://fapi.binance.com/fapi/v1/klines', {'symbol': sym, 'interval': '1d', 'startTime': t, 'limit': 1000})
            except Exception as e:  # noqa: BLE001
                have['_error_' + nat] = str(e)[:120]
                break
            if not d:
                break
            for k in d:
                rows[int(k[0]) // 1000] = float(k[4])
            if len(d) < 1000:
                break
            t = int(d[-1][0]) + 1
        if rows:
            have[nat] = {str(k): v for k, v in sorted(rows.items())}
    write_gz(path, have)
    return have


def price_fn(prices, native):
    """ts -> USD per native coin: the Binance daily close of the day before (the latest known), clamped to the ends."""
    ser = prices.get(native) or {}
    xs = sorted(int(k) for k in ser)
    ys = [ser[str(k)] for k in xs]

    def f(ts):
        if not xs:
            return None
        j = _bisect_right(xs, ts - DAY) - 1
        return ys[max(0, min(j, len(ys) - 1))]
    return f


# ----------------------------------------------------------------------------------------------------------------------
# Discounts against the exchange rate, hour by hour
# ----------------------------------------------------------------------------------------------------------------------
MAX_BAR_BPS = 300.0      # an hourly bar whose average sits further than this from the rate is a broken venue, not a price
SELL_SHARE = 0.5         # OHLCV volume has no side: the share of a bar's volume taken to be sales (sensitivity: 0.25)
GAS_USD = 1.0            # HyperEVM / Solana / Sonic / Avalanche / BSC gas for buy + request + claim: under a dollar
MIN_FILL_USD = 1_000.0
SIZES_USD = [100_000, 300_000, 1_000_000, 3_000_000, 10_000_000, 30_000_000]
HURDLES_BPS = [0.0, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]
FEE_LEGS = 2.0


def rate_fn(samples, max_gap_s=2 * DAY, mode='linear'):
    """ts -> exchange rate from [(ts, rate)] samples. `linear` interpolates (protocol rates that step a little every
    few hours); `step` holds the last sample (rates that change once per epoch). None outside the sampled span."""
    s = sorted((t, r) for t, r in samples if r)
    xs = [t for t, _ in s]
    ys = [r for _, r in s]

    def f(ts):
        if not xs or ts < xs[0] or ts > xs[-1] + max_gap_s:
            return None
        if mode == 'step':
            return ys[_bisect_right(xs, ts) - 1]
        return interp(xs, ys, ts)
    return f


def bar_records(bars, rate_at, fee_bps, usd_at, pool, price='typical'):
    """Hourly bars [[ts, o, h, l, c, v_native]] -> records priced against the rate at mid-bar. Zero-volume bars and bars
    without a rate are dropped. `discount_bps` > 0 means the LST traded below the rate."""
    out = []
    for row in bars:
        t, o, h, l, c, v = row[:6]
        if not v or v <= 0 or c <= 0 or l <= 0:
            continue
        ts = int(t) + HOUR // 2
        R = rate_at(ts)
        u = usd_at(ts)
        if not R or not u:
            continue
        px = (h + l + c) / 3.0 if price == 'typical' else c
        out.append({'ts': ts, 'hour': int(t), 'pool': pool, 'price': px, 'rate': R,
                    'discount_bps': 1e4 * (R - px) / R, 'low_discount_bps': 1e4 * (R - l) / R,
                    'vol_native': v, 'usd': v * u, 'fee_bps': fee_bps})
    return out


def hourly_market(records):
    """{hour: (volume-weighted discount across pools, volume usd)} -- the whole market's price each hour."""
    acc = collections.defaultdict(lambda: [0.0, 0.0])
    for r in records:
        a = acc[r['hour']]
        a[0] += r['discount_bps'] * r['usd']
        a[1] += r['usd']
    return {h: (a[0] / a[1], a[1]) for h, a in sorted(acc.items()) if a[1] > 0}


def dist(values):
    v = [x for x in values if x is not None]
    if not v:
        return {'n': 0}
    return {'n': len(v), 'p10': pct(v, .1), 'p50': pct(v, .5), 'p90': pct(v, .9), 'p99': pct(v, .99), 'max': max(v),
            'min': min(v), 'share_ge_5bp': sum(1 for x in v if x >= 5) / len(v), 'share_ge_10bp': sum(1 for x in v if x >= 10) / len(v),
            'share_ge_20bp': sum(1 for x in v if x >= 20) / len(v), 'share_ge_50bp': sum(1 for x in v if x >= 50) / len(v)}


def episodes(market, threshold_bps, max_gap_hours=2):
    """Runs of hours whose market discount clears `threshold_bps` (the round trip: two fees + the queue's carry +
    any redemption fee); up to `max_gap_hours` silent hours may sit inside a run."""
    thr = threshold_bps if callable(threshold_bps) else (lambda h: threshold_bps)
    eps, cur = [], None
    for h, (d, vol) in sorted(market.items()):
        t_h = thr(h)
        if d > t_h:
            if cur and (h - cur['last']) // HOUR - 1 > max_gap_hours:
                eps.append(cur)
                cur = None
            if cur is None:
                cur = {'start': h, 'last': h, 'hours': 0, 'vol_usd': 0.0, 'peak_bps': d, 'sum_dv': 0.0, 'sum_net': 0.0}
            cur['last'] = h
            cur['hours'] += 1
            cur['vol_usd'] += vol
            cur['sum_dv'] += d * vol
            cur['sum_net'] += (d - t_h) * vol
            cur['peak_bps'] = max(cur['peak_bps'], d)
        elif cur is not None and (h - cur['last']) // HOUR > max_gap_hours:
            eps.append(cur)
            cur = None
    if cur:
        eps.append(cur)
    return [{'start_utc': utc(e['start']), 'end_utc': utc(e['last'] + HOUR), 'qualifying_hours': e['hours'],
             'span_hours': (e['last'] - e['start']) // HOUR + 1, 'volume_usd': e['vol_usd'],
             'vw_discount_bps': e['sum_dv'] / e['vol_usd'] if e['vol_usd'] else None, 'peak_bps': e['peak_bps'],
             'net_of_round_trip_bps': (e['sum_net'] / e['vol_usd']) if e['vol_usd'] else None} for e in eps]


def make_env(records, wait_at, carry_at, sell_share=SELL_SHARE, redemption_fee_bps=0.0, accrues=False):
    """The `queue_book.simulate_book` environment of one asset from hourly records: each bar becomes one sale of
    `sell_share` of its volume at the bar's average price; the edge is capped at the venue median less one fee."""
    sells = [{'ts': r['ts'], 'usd': r['usd'] * sell_share, 'discount_bps': r['discount_bps'], 'fee_bps': r['fee_bps'],
              'pool': r['pool'], 'tx': '%s@%d' % (r['pool'], r['hour'])} for r in records if r['discount_bps'] > 0]
    sells.sort(key=lambda x: (x['ts'], x['pool']))
    return {'sells': sells, 'wait': wait_at, 'carry': carry_at, 'accrues': accrues,
            'market': market_discount_fn(records), 'redemption_fee_bps': redemption_fee_bps}


def run_bid(env, first_day, n_days, sizes=SIZES_USD, hurdles=HURDLES_BPS, gas=GAS_USD, min_fill=MIN_FILL_USD):
    """The per-asset protocol: for each size, one daily value series per hurdle, the hurdle chosen on the first half
    (`backtest.choose_then_test`), scored once on the second; capacity = the smallest size earning 90% of the best."""
    import queue_book as QB
    res = {}
    for size in sizes:
        variants, per = {}, {}
        for h in hurdles:
            fills, st = QB.simulate_book({'a': env}, size, h, gas_usd=gas, min_fill_usd=min_fill)
            variants['h=%g' % h] = daily_values(fills, first_day, n_days)
            per['h=%g' % h] = (fills, st)
        ct = B.choose_then_test(variants, frac=0.5, periods_per_year=365, key='ann_return')
        ch = ct['chosen']
        c = ct['cutoff_index']
        oos = variants[ch][c:]
        boot = B.block_bootstrap(oos, block=7, n=2000)
        fills, st = per[ch]
        last_day = first_day + n_days - 1
        res[size] = {
            'chosen_hurdle': ch, 'hurdle_bps': float(ch.split('=')[1]),
            'in_sample_usd_per_year': ct['in_sample'].get('ann_return'),
            'out_of_sample_usd_per_year': ct['out_of_sample'].get('ann_return'), 'oos_t': ct['oos_t'],
            'oos_rank_of_chosen': ct['oos_rank'],
            'oos_ci95_usd_per_year': [boot['lo'] * 365 if boot['lo'] is not None else None, boot['hi'] * 365 if boot['hi'] is not None else None],
            'oos_share_of_bootstraps_le_0': boot['p_le_0'],
            'full_period_usd_per_year': sum(variants[ch]) * 365.0 / n_days,
            'trailing_90d_usd_per_year': sum(f['value_usd'] for f in fills if f['ts'] // DAY > last_day - 90) * 365.0 / 90,
            'by_hurdle_oos_usd_per_year': {v: sum(x[c:]) * 365.0 / max(1, n_days - c) for v, x in variants.items()},
            'fills': len(fills), 'fills_oos': sum(1 for f in fills if f['ts'] // DAY >= first_day + c),
            'filled_usd': st['filled_usd'], 'missed_capital_usd': st['missed_capital_usd'],
            'qualifying_usd': st['qualifying_usd'],
            'median_edge_bps': statistics.median([f['edge_bps'] for f in fills]) if fills else None,
            'value_by_month_usd': {m: round(sum(f['value_usd'] for f in fills if utc(f['ts'])[:7] == m), 2)
                                   for m in sorted({utc(f['ts'])[:7] for f in fills})},
            'top_fills': [{'utc': utc(f['ts']), 'usd': f['usd'], 'edge_bps': f['edge_bps'], 'value_usd': f['value_usd'],
                           'pool': f['pool']} for f in sorted(fills, key=lambda f: -f['value_usd'])[:6]],
            'cutoff_utc': utc((first_day + c) * DAY),
        }
    oos_by = {s: max(0.0, r['out_of_sample_usd_per_year'] or 0.0) for s, r in res.items()}
    cap = capacity_size(oos_by)
    return res, cap


def late_entry(env, size, hurdle, first_day, n_days, cutoff_index, gas=GAS_USD, min_fill=MIN_FILL_USD):
    """Share of the out-of-sample value kept by a bidder who only acts once the venue median has shown the edge for
    1 hour / 1 day (the repo's operational test of 'no latency')."""
    import queue_book as QB
    base_f, _ = QB.simulate_book({'a': env}, size, hurdle, gas_usd=gas, min_fill_usd=min_fill)
    base = sum(daily_values(base_f, first_day, n_days)[cutoff_index:])
    out = {'base_oos_usd': base}
    for label, d in (('1h', HOUR), ('1d', DAY)):
        f, _ = QB.simulate_book({'a': env}, size, hurdle, gas_usd=gas, min_fill_usd=min_fill, delay_s=d)
        v = sum(daily_values(f, first_day, n_days)[cutoff_index:])
        out[label] = {'oos_usd': v, 'kept_share': (v / base) if base > 0 else None}
    return out


def locked_capital_series(env, hurdle, first_day, n_days, gas=GAS_USD, min_fill=MIN_FILL_USD):
    """Daily capital the bid would lock with unbounded capital at `hurdle` (for the shared queue book)."""
    import queue_book as QB
    fills, _ = QB.simulate_book({'a': env}, QB.UNBOUNDED, hurdle, gas_usd=gas, min_fill_usd=min_fill)
    v = QB.locked_daily(fills, first_day, n_days)
    return [{'day': ymd((first_day + i) * DAY), 'locked_usd': round(x, 2)} for i, x in enumerate(v)]


# ----------------------------------------------------------------------------------------------------------------------
# Kinetiq queue: decode, match, check payouts
# ----------------------------------------------------------------------------------------------------------------------
def decode_kinetiq(logs, block_ts):
    """Requests and confirmations keyed by (user, withdrawalId); ids are per user. Amounts in HYPE/kHYPE (18 decimals)."""
    T = kq_topics()
    inv = {v: k for k, v in T.items()}
    req, conf, canc, params = {}, {}, {}, []
    for lg in sorted(logs, key=lambda x: (x['block'], x['li'])):
        kind = inv.get(lg['topics'][0])
        ts = block_ts(lg['block'])
        if kind == 'queued':
            user = '0x' + lg['topics'][2][-40:]
            wid = int(lg['topics'][3], 16)
            req[(user, wid)] = {'user': user, 'id': wid, 'block': lg['block'], 'ts': ts, 'tx': lg['tx'],
                                'khype': word_int(lg['data'], 0) / 1e18, 'hype': word_int(lg['data'], 1) / 1e18,
                                'fee_khype': word_int(lg['data'], 2) / 1e18}
        elif kind == 'confirmed':
            user = '0x' + lg['topics'][1][-40:]
            wid = int(lg['topics'][2], 16)
            conf[(user, wid)] = {'block': lg['block'], 'ts': ts, 'tx': lg['tx'], 'amount': word_int(lg['data'], 0) / 1e18}
        elif kind == 'cancelled':
            user = '0x' + lg['topics'][1][-40:]
            wid = int(lg['topics'][2], 16)
            canc[(user, wid)] = {'block': lg['block'], 'ts': ts, 'amount': word_int(lg['data'], 0) / 1e18}
        elif kind in ('fee_rate', 'delay'):
            params.append({'kind': kind, 'block': lg['block'], 'ts': ts, 'utc': utc(ts), 'value': word_int(lg['data'], 0)})
        elif kind in ('paused', 'unpaused'):
            params.append({'kind': kind, 'block': lg['block'], 'ts': ts, 'utc': utc(ts)})
    return req, conf, canc, params


def kinetiq_check(req, conf, canc, rate_at, min_khype=0.01):
    """Did every confirmation pay what its request fixed? At what exchange rate was the request fixed? How long from
    request to confirmation? Returns the summary and the per-request rows."""
    rows = []
    for k, r in req.items():
        c = conf.get(k)
        R = rate_at(r['ts'])
        row = dict(r)
        row['rate_at_request'] = R
        row['implied_rate'] = (r['hype'] / r['khype']) if r['khype'] else None
        row['rate_gap_bps'] = (1e4 * (row['implied_rate'] / R - 1.0)) if (R and row['implied_rate']) else None
        row['fee_bps'] = (1e4 * r['fee_khype'] / (r['khype'] + r['fee_khype'])) if (r['khype'] + r['fee_khype']) else None
        if c:
            row['paid'] = c['amount']
            row['paid_gap_bps'] = 1e4 * (c['amount'] / r['hype'] - 1.0) if r['hype'] else None
            row['wait_days'] = (c['ts'] - r['ts']) / DAY
            row['confirm_ts'] = c['ts']
        row['cancelled'] = k in canc
        rows.append(row)
    big = [r for r in rows if r['khype'] >= min_khype]
    paid = [r for r in big if 'paid' in r]
    gaps = [r['paid_gap_bps'] for r in paid if r['paid_gap_bps'] is not None]
    waits = [r['wait_days'] for r in paid]
    rg = [r['rate_gap_bps'] for r in big if r['rate_gap_bps'] is not None]
    fees = [r['fee_bps'] for r in big if r['fee_bps'] is not None]
    by_month = collections.defaultdict(list)
    for r in paid:
        by_month[utc(r['ts'])[:7]].append(r['wait_days'])
    summary = {
        'requests': len(rows), 'requests_ge_min': len(big), 'requested_khype': sum(r['khype'] for r in rows),
        'requested_hype': sum(r['hype'] for r in rows), 'confirmed': sum(1 for r in rows if 'paid' in r),
        'confirmed_hype': sum(r.get('paid', 0.0) for r in rows), 'cancelled': sum(1 for r in rows if r['cancelled']),
        'unconfirmed': sum(1 for r in rows if 'paid' not in r and not r['cancelled']),
        'unconfirmed_hype': sum(r['hype'] for r in rows if 'paid' not in r and not r['cancelled']),
        'paid_gap_bps': dist(gaps) if gaps else {'n': 0}, 'paid_exact_share': (sum(1 for g in gaps if abs(g) < 0.01) / len(gaps)) if gaps else None,
        'paid_short_count': sum(1 for g in gaps if g < -0.01), 'paid_over_count': sum(1 for g in gaps if g > 0.01),
        'rate_gap_bps': {'n': len(rg), 'p1': pct(rg, .01), 'p50': pct(rg, .5), 'p99': pct(rg, .99), 'min': min(rg) if rg else None, 'max': max(rg) if rg else None},
        'fee_bps': {'n': len(fees), 'p50': pct(fees, .5), 'max': max(fees) if fees else None, 'nonzero': sum(1 for f in fees if f > 0.01)},
        'wait_days': {'n': len(waits), 'p1': pct(waits, .01), 'p5': pct(waits, .05), 'p50': pct(waits, .5), 'p90': pct(waits, .9), 'max': max(waits) if waits else None},
        'wait_p5_by_month': {m: pct(v, .05) for m, v in sorted(by_month.items())},
        'wait_min_by_month': {m: min(v) for m, v in sorted(by_month.items())},
        'requested_hype_by_month': {m: sum(r['hype'] for r in rows if utc(r['ts'])[:7] == m) for m in sorted({utc(r['ts'])[:7] for r in rows})},
    }
    return summary, rows


# ----------------------------------------------------------------------------------------------------------------------
# analyze, part (a): queue bids
# ----------------------------------------------------------------------------------------------------------------------
# How each queue pays (all read from contracts unless marked docs): the wait a prompt claimer sees, whether the queued
# amount keeps earning (it does not when the native amount is fixed at the request), and the redemption fee.
QUEUE_MODEL = {
    'khype': {'wait': 'events', 'accrues': False, 'fee': 'events',
              'note': 'amount fixed at the request (every confirmation paid its WithdrawalQueued hypeAmount); 10bp unstake '
                      'fee until UnstakeFeeRateUpdated(0) at 2026-04-08 00:14 UTC; wait = the fastest confirmation of '
                      'requests made within a day either side (never under the 7-day withdrawalDelay) + 1 hour'},
    'jitosol': {'wait_days': 2.2, 'accrues': True, 'fee_bps': 10.0,
                'note': 'withdraw stake + deactivate: done at the next epoch boundary (an epoch is ~2.2 days); the stake '
                        'keeps earning until then; stake_withdrawal_fee 10bp (read from the stake pool account)'},
    'sts': {'wait_days': 14.5, 'accrues': False, 'fee_bps': 0.0,
            'note': 'undelegate fixes the S amount (convertToAssets at the request, source); withdrawDelay 14 days (read)'},
    'savax': {'wait_days': 15.5, 'accrues': False, 'fee_bps': 0.0,
              'note': 'requestUnlock; redeem pays the rate recorded at the unlock start (source); cooldown 15 days, redeem '
                      'window 2 days (read)'},
    'slisbnb': {'wait_days': 8.0, 'accrues': False, 'fee_bps': 0.0,
                'note': 'requestWithdraw fixes the BNB amount (source); BSC unbond 7 days (read) + the bot batch; instant '
                        'withdraw is whitelist-only (read)'},
    'aprmon': {'wait_days': 1.0, 'accrues': False, 'fee_bps': 10.0,
               'note': 'ERC-7540 requestRedeem fixes assets; withdrawalFee 10/10,000 (read); wait: one Monad epoch plus the '
                       'operator batch (assumed 1 day)'},
}
BAR_ASSETS = ['jitosol', 'slisbnb', 'sts', 'savax', 'aprmon']
DEFAULT_FEE_BPS = 1.0
PASS_USD = 25_000.0


def trailing_apr_fn(samples, window_days=30.0, fallback=0.02):
    """ts -> the LST's own annual growth over the trailing window: the staking yield the queued amount gives up."""
    s = sorted((t, r) for t, r in samples if r)
    ts = [t for t, _ in s]

    def f(t):
        j = _bisect_right(ts, t) - 1
        if j < 1:
            return fallback
        i = _bisect_right(ts, t - window_days * DAY) - 1
        i = max(0, min(i, j - 1))
        a = apr_from_nav([s[i], s[j]], days_min=0.5)
        return a if a is not None else fallback
    return f


def wait_from_events(rows, floor_days, pad_days=1.0 / 24):
    """ts -> wait (days) of a prompt claimer: the fastest confirmation among requests made within a day either side,
    never under the contract's delay, plus `pad_days`."""
    best = {}
    for r in rows:
        if r.get('wait_days') is None or r['khype'] < 0.01:
            continue
        d = int(r['ts'] // DAY)
        best[d] = min(best.get(d, 1e9), r['wait_days'])

    def f(ts):
        d = int(ts // DAY)
        cand = [best[x] for x in (d - 1, d, d + 1) if x in best]
        w = min(cand) if cand else floor_days
        return max(floor_days, w) + pad_days
    return f, best


def window_days(records, min_coverage=0.5):
    """First and count of whole UTC days covered by the records (the first and last partial days dropped)."""
    if not records:
        return None, 0
    d0 = int(min(r['ts'] for r in records) // DAY) + 1
    d1 = int(max(r['ts'] for r in records) // DAY) - 1
    return d0, max(0, d1 - d0 + 1)


def depth_below_round_trip(env, first_day, n_days):
    """Capacity from measured flow: per day, the sales whose edge (venue-median capped, net of two pool fees, the queue's
    carry and the redemption fee) was positive -- what a bid with unlimited capital could have bought at a profit."""
    rows = env.get(('_edges', FEE_LEGS, True, 0))
    if rows is None:
        return None
    by = collections.defaultdict(float)
    edge_usd = collections.defaultdict(float)
    for s, (edge, wait, seen) in zip(env['sells'], rows):
        if edge > 0:
            d = int(s['ts'] // DAY)
            if first_day <= d < first_day + n_days:
                by[d] += s['usd']
                edge_usd[d] += s['usd'] * edge / 1e4
    days = [by.get(first_day + i, 0.0) for i in range(n_days)]
    pos = [x for x in days if x > 0]
    return {'days': n_days, 'days_with_any': len(pos), 'usd_total': sum(days), 'usd_per_day_mean': sum(days) / n_days if n_days else None,
            'usd_per_active_day_p50': pct(pos, .5) if pos else None, 'usd_per_active_day_p90': pct(pos, .9) if pos else None,
            'usd_max_day': max(days) if days else None, 'edge_usd_total': sum(edge_usd.values()),
            'edge_usd_per_year_unbounded': sum(edge_usd.values()) * 365.0 / n_days if n_days else None}


def bid_block(records, sells_env, first_day, n_days, label, extra=None):
    """Distribution, episodes, bid grid, capacity, late entry and the locked-capital series for one asset."""
    grid, cap = run_bid(sells_env, first_day, n_days)
    size_q = cap or 1_000_000
    at = grid[size_q]
    c = B.cutoff_index(n_days, 0.5)
    late = late_entry(sells_env, size_q, at['hurdle_bps'], first_day, n_days, c)
    out = {'label': label, 'first_day': ymd(first_day * DAY), 'days': n_days, 'cutoff_utc': at['cutoff_utc'],
           'grid': {str(k): v for k, v in grid.items()}, 'capacity_size_usd': cap, 'quoted_size_usd': size_q,
           'at_quoted_size': at, 'late_entry': late, 'depth_below_round_trip': depth_below_round_trip(sells_env, first_day, n_days)}
    if extra:
        out.update(extra)
    return out


def summarize_records(records, threshold_bps):
    m = hourly_market(records)
    by_month = collections.defaultdict(list)
    for h, (d, v) in m.items():
        by_month[utc(h)[:7]].append((d, v))
    by_pool = collections.defaultdict(lambda: {'n': 0, 'usd': 0.0, 'dv': 0.0})
    for r in records:
        b = by_pool[r['pool']]
        b['n'] += 1
        b['usd'] += r['usd']
        b['dv'] += r['discount_bps'] * r['usd']
    eps = episodes(m, threshold_bps)
    return {
        'market_hourly_discount_bps': dist([d for d, _ in m.values()]),
        'hours_with_trades': len(m), 'volume_usd': sum(v for _, v in m.values()),
        'by_month': {mo: {'hours': len(xs), 'volume_usd': sum(v for _, v in xs), 'p50_bps': pct([d for d, _ in xs], .5),
                          'p90_bps': pct([d for d, _ in xs], .9), 'max_bps': max(d for d, _ in xs)} for mo, xs in sorted(by_month.items())},
        'by_pool': {k: {'records': v['n'], 'volume_usd': v['usd'], 'vw_discount_bps': v['dv'] / v['usd'] if v['usd'] else None}
                    for k, v in sorted(by_pool.items(), key=lambda kv: -kv[1]['usd'])},
        'round_trip_bps': threshold_bps(max(m)) if (callable(threshold_bps) and m) else threshold_bps,
        'episodes': {'count': len(eps), 'hours': sum(e['qualifying_hours'] for e in eps),
                     'longest_hours': max((e['span_hours'] for e in eps), default=0),
                     'deepest_bps': max((e['peak_bps'] for e in eps), default=None),
                     'volume_usd': sum(e['volume_usd'] for e in eps),
                     'top': sorted(eps, key=lambda e: -(e['volume_usd'] * (e['net_of_round_trip_bps'] or 0)))[:8]},
    }


def load_rate_samples(raw, key, network):
    if key == 'jitosol':
        rows = read_gz(raw / 'rates' / 'jitosol_jito_api.json.gz')['rows']
        return [(r['ts'], r['rate']) for r in rows]
    rates = read_gz(raw / 'rates' / ('%s.json.gz' % key)) or {}
    blocks = {int(k): v for k, v in (read_gz(raw / ('blocks_%s.json.gz' % network)) or {}).items()}
    return sorted((blocks[int(k)], v) for k, v in rates.items() if v and int(k) in blocks)


def analyze_bar_asset(key, raw, screen, prices):
    c = CAND[key]
    qm = QUEUE_MODEL[key]
    samples = load_rate_samples(raw, key, c['network'])
    if len(samples) < 10:
        return {'key': key, 'skipped': 'no exchange-rate history'}
    R = rate_fn(samples)
    apr = trailing_apr_fn(samples)
    U = price_fn(prices, c['native'])
    recs, excluded, pools = [], [], []
    for p in pools_for(screen, key):
        d = read_gz(raw / 'ohlcv' / ('%s__%s.json.gz' % (c['network'], p['pool'].replace(':', '_'))))
        if not d:
            continue
        fee = (p['fee_pct'] * 100.0) if p.get('fee_pct') is not None else DEFAULT_FEE_BPS
        rr = bar_records(d['bars'], R, fee, U, p['dex'] + ':' + p['pool'][:6])
        pools.append({'pool': p['pool'], 'dex': p['dex'], 'name': p['name'], 'fee_bps': fee, 'bars': len(d['bars']),
                      'records': len(rr), 'first_bar_utc': utc(d['bars'][0][0]) if d['bars'] else None,
                      'gt_stop': d.get('stop')})
        for r in rr:
            (excluded if abs(r['discount_bps']) > MAX_BAR_BPS else recs).append(r)
    first_day, n_days = window_days(recs)
    if n_days < 60:
        return {'key': key, 'skipped': 'under 60 days of bars', 'pools': pools}
    recs = [r for r in recs if first_day <= r['ts'] // DAY < first_day + n_days]
    wait_days = qm['wait_days']
    fee = qm['fee_bps']
    carry_at = (lambda ts: 1e4 * (apr(ts) or 0.0) / 365.0)
    env = make_env(recs, lambda ts: wait_days, carry_at, SELL_SHARE, fee, qm['accrues'])
    med_fee = statistics.median([r['fee_bps'] for r in recs])
    last_ts = max(r['ts'] for r in recs)
    rt = FEE_LEGS * med_fee + (0.0 if qm['accrues'] else wait_days * carry_at(last_ts)) + fee
    blk = bid_block(recs, env, first_day, n_days, c['symbol'])
    # sensitivity: a quarter of the volume as sales instead of half
    env25 = make_env(recs, lambda ts: wait_days, carry_at, 0.25, fee, qm['accrues'])
    g25, cap25 = run_bid(env25, first_day, n_days, sizes=[blk['quoted_size_usd']])
    blk['sell_share_0_25'] = {'out_of_sample_usd_per_year': g25[blk['quoted_size_usd']]['out_of_sample_usd_per_year'],
                              'chosen_hurdle': g25[blk['quoted_size_usd']]['chosen_hurdle']}
    blk.update(summarize_records(recs, rt))
    blk.update({'key': key, 'symbol': c['symbol'], 'native': c['native'], 'network': c['network'],
                'source': 'GeckoTerminal hourly bars (typical price, %.0f%% of volume as sales)' % (100 * SELL_SHARE),
                'pools': pools, 'excluded_bars': len(excluded), 'queue_model': qm,
                'staking_apr_latest': apr(last_ts), 'rate_latest': R(last_ts), 'rate_samples': len(samples)})
    blk['_env'] = env
    return blk


# Valantis's STEX pool is Kinetiq's instant-unstake venue: it buys kHYPE at a fee and redeems it through the queue, and
# usually holds no kHYPE to sell back, so a sale into it cannot be back-run. It is a competing bidder, reported apart and
# kept out of the bid's sales and of the venue median.
NOT_BACKRUNNABLE = {'valantis-stex'}


def khype_swap_records(raw, rate_at, block_ts, usd_at, min_khype=0.01, min_sell_usd=MIN_FILL_USD):
    """One pass over the swap shards, keeping memory flat: (hourly aggregates per pool, sells of at least
    `min_sell_usd` -- the bid can never fill a smaller one --, all sell discounts, excluded prints). The hourly
    aggregates carry what the market cap, the distributions and the bar cross-check need."""
    agg = {}
    sells, sell_disc, excluded = [], [], {'count': 0, 'usd': 0.0, 'examples': []}
    n_swaps = 0
    shards = sorted((raw / 'khype_swaps').glob('shard_*.json.gz'), key=lambda x: int(x.name.split('_')[1].split('.')[0]))
    for fn in shards:
        for b, tx, pool, side, ka, wb in (read_gz(fn) or {}).get('swaps', []):
            if ka < min_khype or wb <= 0:
                continue
            ts = block_ts(b)
            R = rate_at(ts)
            u = usd_at(ts)
            if not R or not u:
                continue
            name, fee = KHYPE_POOLS.get(pool, (pool[:10], DEFAULT_FEE_BPS))
            px = wb / ka
            d = 1e4 * (R - px) / R
            usd = ka * R * u
            if abs(d) > MAX_BAR_BPS:
                excluded['count'] += 1
                excluded['usd'] += usd
                if len(excluded['examples']) < 8:
                    excluded['examples'].append({'utc': utc(ts), 'pool': name, 'side': side, 'usd': usd, 'price': px, 'rate': R, 'discount_bps': d, 'tx': tx})
                continue
            n_swaps += 1
            h = ts // HOUR * HOUR
            a = agg.get((name, h))
            if a is None:
                a = agg[(name, h)] = [0.0, 0.0, 0, 0.0, 0.0, 0.0, fee]
            a[0] += d * usd
            a[1] += usd
            a[2] += 1
            a[3] += px * ka
            a[4] += ka
            a[5] += ka * R
            if side == 's' and name not in NOT_BACKRUNNABLE:
                sell_disc.append(d)
                if usd >= min_sell_usd:
                    sells.append({'ts': ts, 'usd': usd, 'discount_bps': d, 'fee_bps': fee, 'pool': name, 'tx': tx})
    sells.sort(key=lambda r: (r['ts'], r['tx']))
    hourly = [{'ts': h + HOUR // 2, 'hour': h, 'pool': name, 'discount_bps': a[0] / a[1], 'usd': a[1], 'n': a[2],
               'vwap': a[3] / a[4] if a[4] else None, 'khype': a[4], 'rate': a[5] / a[4] if a[4] else None, 'fee_bps': a[6]}
              for (name, h), a in sorted(agg.items(), key=lambda kv: (kv[0][1], kv[0][0])) if a[1] > 0]
    return hourly, sells, sell_disc, excluded, n_swaps


def analyze_khype(raw, screen, prices):
    """kHYPE: swap-level history from chain since launch, priced against the StakingAccountant rate, with the queue
    measured from Kinetiq's own events. GeckoTerminal's bars give a second, independent price path for the overlap."""
    blocks = {int(k): v for k, v in read_gz(raw / 'blocks_hyperevm.json.gz').items()}
    bs = sorted(blocks)
    tss = [blocks[b] for b in bs]
    block_ts = (lambda n: int(round(interp(bs, tss, n))))
    samples = sorted((blocks[int(k)], v) for k, v in read_gz(raw / 'rates' / 'khype.json.gz').items() if v and int(k) in blocks)
    R = rate_fn(samples)
    apr = trailing_apr_fn(samples)
    U = price_fn(prices, 'HYPE')
    logs = read_gz(raw / 'queue' / 'khype_events.json.gz')['logs']
    req, conf, canc, params = decode_kinetiq(logs, block_ts)
    pay, rows = kinetiq_check(req, conf, canc, R)
    # the fee was a rate on the request; no-fee requests price the NAV the queue pays directly
    nofee = [r['rate_gap_bps'] for r in rows if r['khype'] >= 0.01 and r['rate_gap_bps'] is not None and (r['fee_bps'] or 0) < 0.01]
    pay['rate_gap_bps_no_fee_requests'] = dist(nofee) if nofee else {'n': 0}
    pay['params'] = params
    fee_change = [x for x in params if x['kind'] == 'fee_rate']
    fee_off_ts = fee_change[-1]['ts'] if fee_change and fee_change[-1]['value'] == 0 else None
    wait_at, best = wait_from_events(rows, 7.0)
    pay['wait_model_daily_fastest_days'] = dist(list(best.values()))
    carry_stake = (lambda ts: 1e4 * (apr(ts) or 0.0) / 365.0)

    def fee_at(ts):
        return 10.0 if (fee_off_ts is None or ts < fee_off_ts) else 0.0

    # The redemption fee varies in time; simulate_book takes one fee per asset, so it is folded into the per-day carry
    # (fee / wait per day of wait), which subtracts exactly the fee from every edge it prices.
    carry_eff = (lambda ts: carry_stake(ts) + fee_at(ts) / wait_at(ts))
    recs, sells_big, sell_disc, excluded, n_swaps = khype_swap_records(raw, R, block_ts, U)
    out = {'key': 'khype', 'symbol': 'kHYPE', 'native': 'HYPE', 'network': 'hyperevm', 'payout_check': pay,
           'queue_model': QUEUE_MODEL['khype'], 'rate_samples': len(samples),
           'staking_apr_latest': apr(time.time()), 'rate_latest': samples[-1][1] if samples else None,
           'fee_off_utc': utc(fee_off_ts) if fee_off_ts else None}
    if not recs:
        out['skipped'] = 'no swaps collected yet'
        return out
    first_day, n_days = window_days(recs)
    all_hourly = [r for r in recs if first_day <= r['ts'] // DAY < first_day + n_days]
    stex = [r for r in all_hourly if r['pool'] in NOT_BACKRUNNABLE]
    recs = [r for r in all_hourly if r['pool'] not in NOT_BACKRUNNABLE]
    sells = [r for r in sells_big if first_day <= r['ts'] // DAY < first_day + n_days]
    env = {'sells': sells, 'wait': wait_at, 'carry': carry_eff, 'accrues': False, 'market': market_discount_fn(recs),
           'redemption_fee_bps': 0.0}
    last_ts = max(r['ts'] for r in recs)
    med_fee = statistics.median([r['fee_bps'] for r in recs])
    rt = (lambda h: FEE_LEGS * med_fee + wait_at(h) * carry_stake(h) + fee_at(h))    # the fee era raises it by 10bp
    blk = bid_block(recs, env, first_day, n_days, 'kHYPE (swaps)')
    blk.update(summarize_records(recs, rt))
    blk['competitor_stex'] = {'pool_hours': len(stex), 'volume_usd': sum(r['usd'] for r in stex),
                              'vw_discount_bps': (sum(r['discount_bps'] * r['usd'] for r in stex) / sum(r['usd'] for r in stex)) if stex else None,
                              'by_month_volume_usd': {m: sum(r['usd'] for r in stex if utc(r['hour'])[:7] == m) for m in sorted({utc(r['hour'])[:7] for r in stex})}}
    blk['swaps_priced'] = n_swaps
    blk['sells_at_least_min_fill'] = len(sells)
    blk['sell_volume_at_least_min_fill_usd'] = sum(r['usd'] for r in sells)
    blk['sell_discount_bps_all_sells'] = dist(sell_disc)
    blk['excluded_prints'] = excluded
    blk['source'] = 'on-chain swaps reconstructed from kHYPE/WHYPE transfers into and out of %d pools' % len(KHYPE_POOLS)
    blk['records_are'] = 'hourly per-pool aggregates (by_pool.records counts pool-hours)'
    # variants on the same sells: carry at HyperLend's WHYPE borrow rate (a bid funded by borrowing HYPE against
    # kHYPE), the fixed 7-day wait, no market cap (per print), and the fee era removed
    hl = read_gz(raw / 'rates' / 'hyperlend.json.gz') or {}
    wh = sorted((blocks[int(k)], v['borrow_index']) for k, v in (hl.get('WHYPE') or {}).items() if v and int(k) in blocks)
    if len(wh) > 10:
        bapr = trailing_apr_fn(wh, window_days=7.0)
        env_b = dict(env)
        env_b['carry'] = (lambda ts: 1e4 * (bapr(ts) or 0.0) / 365.0 + fee_at(ts) / wait_at(ts))
        env_b = {k: v for k, v in env_b.items() if not (isinstance(k, tuple))}
        g, cap_b = run_bid(env_b, first_day, n_days, sizes=[blk['quoted_size_usd']])
        blk['variant_carry_whype_borrow'] = {'out_of_sample_usd_per_year': g[blk['quoted_size_usd']]['out_of_sample_usd_per_year'],
                                             'chosen_hurdle': g[blk['quoted_size_usd']]['chosen_hurdle'],
                                             'whype_borrow_apr_mean': (wh[-1][1] / wh[0][1]) ** (365 * DAY / (wh[-1][0] - wh[0][0])) - 1}
    env_f = {k: v for k, v in env.items() if not isinstance(k, tuple)}
    env_f['wait'] = (lambda ts: 7.0 + 1.0 / 24)
    env_f['carry'] = (lambda ts: carry_stake(ts) + fee_at(ts) / (7.0 + 1.0 / 24))
    g, _ = run_bid(env_f, first_day, n_days, sizes=[blk['quoted_size_usd']])
    blk['variant_fixed_7d_wait'] = {'out_of_sample_usd_per_year': g[blk['quoted_size_usd']]['out_of_sample_usd_per_year'],
                                    'chosen_hurdle': g[blk['quoted_size_usd']]['chosen_hurdle']}
    import queue_book as QB
    env_n = {k: v for k, v in env.items() if not isinstance(k, tuple)}
    fills_pp, _ = QB.simulate_book({'a': env_n}, blk['quoted_size_usd'], blk['at_quoted_size']['hurdle_bps'],
                                   gas_usd=GAS_USD, min_fill_usd=MIN_FILL_USD, use_market_cap=False)
    c = B.cutoff_index(n_days, 0.5)
    blk['per_print_upper_bound_oos_usd_per_year'] = sum(daily_values(fills_pp, first_day, n_days)[c:]) * 365.0 / max(1, n_days - c)
    # the GeckoTerminal window priced from bars with the same queue model: a second price path for the bid itself
    brecs = []
    for addr, (name, fee) in KHYPE_POOLS.items():
        d = read_gz(raw / 'ohlcv' / ('hyperevm__%s.json.gz' % addr))
        if d and name not in NOT_BACKRUNNABLE:
            brecs += [r for r in bar_records(d['bars'], R, fee, U, name) if abs(r['discount_bps']) <= MAX_BAR_BPS]
    if brecs:
        bf, bn = window_days(brecs)
        brecs = [r for r in brecs if bf <= r['ts'] // DAY < bf + bn]
        benv = make_env(brecs, wait_at, carry_eff, SELL_SHARE, 0.0, False)
        bblk = bid_block(brecs, benv, bf, bn, 'kHYPE (GeckoTerminal bars)')
        bblk.update(summarize_records(brecs, rt))
        # the swap-level bid restricted to the same days, scored on the same split
        sw_env = {k: v for k, v in env.items() if not isinstance(k, tuple)}
        sw_env['sells'] = [x for x in env['sells'] if bf <= x['ts'] // DAY < bf + bn]
        g, _ = run_bid(sw_env, bf, bn, sizes=[bblk['quoted_size_usd']])
        bblk['swap_level_same_window'] = {'out_of_sample_usd_per_year': g[bblk['quoted_size_usd']]['out_of_sample_usd_per_year'],
                                          'chosen_hurdle': g[bblk['quoted_size_usd']]['chosen_hurdle'],
                                          'oos_ci95_usd_per_year': g[bblk['quoted_size_usd']]['oos_ci95_usd_per_year']}
        out['bars_window_block'] = bblk
    out.update(blk)
    out['_env'] = env
    out['_recs'] = recs
    return out


def bars_crosscheck_khype(raw, screen, prices, hourly):
    """The same pool-hours priced two ways: GeckoTerminal's bar (typical price) against the swap-level VWAP rebuilt from
    chain transfers. Agreement within a few bp says the discount is measured, not manufactured by either source."""
    blocks = {int(k): v for k, v in read_gz(raw / 'blocks_hyperevm.json.gz').items()}
    samples = sorted((blocks[int(k)], v) for k, v in read_gz(raw / 'rates' / 'khype.json.gz').items() if v and int(k) in blocks)
    R = rate_fn(samples)
    U = price_fn(prices, 'HYPE')
    sw = {(r['pool'], r['hour']): r for r in hourly}
    out = {}
    for addr, (name, fee) in KHYPE_POOLS.items():
        d = read_gz(raw / 'ohlcv' / ('hyperevm__%s.json.gz' % addr))
        if not d:
            continue
        diffs, ratios = [], []
        for b in bar_records(d['bars'], R, fee, U, name):
            x = sw.get((name, b['hour']))
            if x and x['vwap'] and x['rate']:
                diffs.append(1e4 * (b['price'] - x['vwap']) / x['rate'])
                if x['khype'] and x['rate']:
                    ratios.append(b['vol_native'] / (x['khype'] * x['rate']))
        out[name] = {'hours_both': len(diffs), 'abs_gap_bps': dist([abs(v) for v in diffs]) if diffs else {'n': 0},
                     'signed_median_gap_bps': pct(diffs, .5) if diffs else None,
                     'bar_volume_over_swap_volume': {'p10': pct(ratios, .1), 'p50': pct(ratios, .5), 'p90': pct(ratios, .9)} if ratios else None}
    return out


WATCH_USD = 10_000.0


def verdict_for(blk, min_usd=PASS_USD):
    """proposed: out of sample >= $25k a year with an interval clear of zero, half the value kept an hour late and the
    trailing 90 days >= $10k. Bar-only evidence (no measured sale side) must also clear the bar with a quarter of the
    volume as sales, or it stays on watch. watch: >= $10k a year with an interval clear of zero. Else no-go."""
    at = blk.get('at_quoted_size') or {}
    oos = at.get('out_of_sample_usd_per_year') or 0.0
    lo = (at.get('oos_ci95_usd_per_year') or [None])[0]
    late = (blk.get('late_entry') or {}).get('1h', {}).get('kept_share')
    t90 = at.get('trailing_90d_usd_per_year') or 0.0
    q = (blk.get('sell_share_0_25') or {}).get('out_of_sample_usd_per_year')
    if oos >= min_usd and lo is not None and lo > 0 and (late or 0) >= 0.5 and t90 >= 10_000:
        if q is not None and q < min_usd:
            return 'watch (bar-only evidence: %s a year with a quarter of the volume as sales)' % fu(q)
        return 'proposed'
    if oos >= WATCH_USD and lo is not None and lo > 0:
        return 'watch (positive, below the bar)'
    return 'no-go'


# ----------------------------------------------------------------------------------------------------------------------
# analyze, part (b): delta-neutral staking on one venue (term_carry's machinery, with the staking token as the spot)
# ----------------------------------------------------------------------------------------------------------------------
TC_DIR = ROOT / 'research' / '2026-10-10' / 'term_carry'


def daily_rate_accrual(samples, d0, d1):
    """{day: ln(rate(d+1)/rate(d))}: the staking yield that accrues on one unit of the LST over day d."""
    R = rate_fn(samples)
    out = {}
    for d in range(d0, d1):
        a, b = R(d * DAY), R((d + 1) * DAY)
        if a and b:
            out[d] = math.log(b / a)
    return out


def daily_apy_accrual(rows, d0, d1, field='apyBase'):
    """{day: apy/365} from a DefiLlama yield chart (percent), each day taking the latest reading at or before it."""
    pts = sorted((r['ts'] // DAY, r[field]) for r in rows if r.get(field) is not None)
    xs = [d for d, _ in pts]
    out = {}
    for d in range(d0, d1):
        j = _bisect_right(xs, d) - 1
        if j >= 0 and d - xs[j] <= 7:
            out[d] = math.log(1.0 + pts[j][1] / 100.0) / 365.0
    return out


def daily_end_discount(recs, hours=6):
    """{day: the market's volume-weighted discount (bp) over the last `hours` of the day}: where the LST leg is marked."""
    acc = collections.defaultdict(lambda: [0.0, 0.0])
    for r in recs:
        d = int(r['ts'] // DAY)
        if r['ts'] - d * DAY >= DAY - hours * HOUR:
            a = acc[d]
            a[0] += r['discount_bps'] * r['usd']
            a[1] += r['usd']
    return {d: a[0] / a[1] for d, a in acc.items() if a[1] > 0}


def basis_accrual(end_disc, days):
    """{day: -(disc(d) - disc(d-1)) / 1e4}: the LST leg's mark-to-market against the native coin, carried over gaps."""
    out, last = {}, None
    for d in days:
        cur = end_disc.get(d, last)
        if last is not None and cur is not None:
            out[d] = -(cur - last) / 1e4
        last = cur if cur is not None else last
    return out


def merge_extra(*parts):
    out = collections.defaultdict(float)
    for p in parts:
        for d, v in (p or {}).items():
            out[d] += v
    return dict(out)


def carry_summary(blk):
    pr = blk['protocol']
    ser = (blk.get('_series') or {}).get(pr['chosen']) or []
    full = B.perf(ser, 365) if ser else {}
    return {'full_max_drawdown': full.get('max_drawdown'), 'full_worst_day': full.get('worst'),
            'oos_max_drawdown': pr['out_of_sample'].get('max_drawdown'), 'oos_worst_day': pr['out_of_sample'].get('worst'),'name': blk['name'], 'capital': blk['capital'], 'first_day': blk['first_day'], 'last_day': blk['last_day'],
            'split_day': blk['split_day'], 'chosen_rule': pr['chosen'], 'oos_ann_excess': pr['out_of_sample'].get('ann_return'),
            'oos_t': pr['oos_t'], 'in_sample_ann_excess': pr['in_sample'].get('ann_return'),
            'oos_bootstrap_mean_ci': [blk['test_block_bootstrap_mean']['lo'] * 365 if blk['test_block_bootstrap_mean']['lo'] is not None else None,
                                      blk['test_block_bootstrap_mean']['hi'] * 365 if blk['test_block_bootstrap_mean']['hi'] is not None else None],
            'always_test_ann_excess': blk['always_test'].get('ann_return'), 'last_365d': blk['recent_ann_excess']['last_365d'],
            'last_90d': blk['recent_ann_excess']['last_90d'], 'by_year': blk['chosen_by_year_ann_excess'],
            'funding_received': blk['bookkeeping_chosen']['funding'], 'extra_received': blk['bookkeeping_chosen']['extra'],
            'basis_mtm': blk['bookkeeping_chosen']['basis'], 'costs': blk['bookkeeping_chosen']['costs'],
            'borrow': blk['bookkeeping_chosen'].get('borrow'), 'days_in': blk['bookkeeping_chosen']['days_in'],
            'rebalances': blk['bookkeeping_chosen']['rebalances'], 'test_concentration_top4_weeks': blk['test_concentration_top4_weeks']}


# What turning the staking token back into the coin costs, per side of the round trip (entry by minting at the rate is
# free): kHYPE exits through the queue for nothing since 2026-04-08 or on a DEX at the ~7bp market discount plus a 1bp
# pool; the Solana stake pools charge a 10bp withdrawal fee, which is also where their instant exits sit.
LST_SIDE_COST_BPS = {'kHYPE': 4.0, 'JitoSOL': 5.0, 'BNSOL': 5.0}


def carry_late_entry(summary):
    """An 'always' rule holds one position through the test half: an hour late changes nothing at daily decisions, a
    day late gives up one day of the excess. Threshold rules would need a re-simulation and are reported as such."""
    if summary['chosen_rule'] != 'always':
        return {'1h': None, '1d': None, 'note': 'threshold rule: not computed'}
    n = summary.get('days_in') or 0
    return {'1h': 1.0, '1d': (1.0 - 1.0 / n) if n else None, 'note': 'always-on: one position; a day late forgoes one day'}


def analyze_carry_b(raw, khype_recs, jito_rows, llama):
    import term_carry as TC
    tc_raw = TC_DIR / 'raw'
    const = TC.bench_of('const', None)
    d_end = int(time.time()) // DAY
    res = {'blocks': {}, 'notes': []}
    # ---- HYPE on Hyperliquid: spot HYPE (the term_carry row, reproduced) vs kHYPE as the spot leg -----------------
    V, closes, highs = TC.carry_inputs(tc_raw, 'HYPE')
    f, pm = V['hl']['f'], V['hl']['p']
    days_all = TC.span(f, d_end)
    spot_c = TC.venue_costs('binance', 'HYPE')[0]
    spot_k = spot_c + LST_SIDE_COST_BPS['kHYPE'] / 1e4
    perp_c = {'hl': TC.venue_costs('hl', 'HYPE')[1]}
    sp = days_all[0] + len(days_all) // 2
    base = TC.run_carry_block('hl:HYPE', days_all, {'hl': f}, {'hl': pm}, spot_c, perp_c, 'collateral', const, None, None,
                              closes, highs, sp)
    res['blocks']['hl_hype_spot_full_history'] = carry_summary(base)
    ks = sorted((t, r) for t, r in khype_recs['rate_samples_list'])
    d0 = max(int(ks[0][0] // DAY) + 1, days_all[0])
    days_k = [d for d in days_all if d >= d0]
    sp_k = days_k[0] + len(days_k) // 2
    stake = daily_rate_accrual(ks, days_k[0] - 1, days_k[-1] + 1)
    end_disc = daily_end_discount(khype_recs['recs']) if khype_recs.get('recs') else {}
    basis = basis_accrual(end_disc, days_k)
    usdt0 = khype_recs.get('usdt0_borrow_apr') or TC.HL_BORROW_APR
    same = TC.run_carry_block('hl:HYPE (kHYPE window)', days_k, {'hl': f}, {'hl': pm}, spot_c, perp_c, 'collateral', const,
                              None, None, closes, highs, sp_k)
    res['blocks']['hl_hype_spot_khype_window'] = carry_summary(same)
    saved = TC.HL_BORROW_APR
    try:
        TC.HL_BORROW_APR = usdt0          # the short's margin borrowed on HyperLend against kHYPE, not on HyperCore
        kb = TC.run_carry_block('hl:HYPE short, kHYPE spot (margin borrowed on HyperLend)', days_k, {'hl': f}, {'hl': pm},
                                spot_k, perp_c, 'collateral', const, None, merge_extra(stake, basis), closes, highs, sp_k)
        kb_nobasis = TC.run_carry_block('hl:HYPE short, kHYPE spot, staking only', days_k, {'hl': f}, {'hl': pm},
                                        spot_k, perp_c, 'collateral', const, None, stake, closes, highs, sp_k)
    finally:
        TC.HL_BORROW_APR = saved
    res['blocks']['hl_hype_short_khype_collateral'] = carry_summary(kb)
    res['blocks']['hl_hype_short_khype_staking_only'] = carry_summary(kb_nobasis)
    kc = TC.run_carry_block('hl:HYPE short cash 3x, kHYPE spot', days_k, {'hl': f}, {'hl': pm}, spot_k, perp_c, 'cash3x',
                            const, None, merge_extra(stake, basis), closes, highs, sp_k)
    res['blocks']['hl_hype_short_khype_cash3x'] = carry_summary(kc)
    res['khype_staking_apr_window'] = (sum(stake.values()) / len(stake) * 365.0) if stake else None
    res['khype_basis_days_marked'] = len([d for d in days_k if d in end_disc])
    res['usdt0_borrow_apr_used'] = usdt0
    # ---- SOL: Binance with BNSOL as the collateral (portfolio margin); Hyperliquid short with JitoSOL held apart -----
    V, closes, highs = TC.carry_inputs(tc_raw, 'SOL')
    bn_rows = llama.get('bnsol') or []
    if 'binance' in V and bn_rows:
        fb, pb = V['binance']['f'], V['binance']['p']
        dd = TC.span(fb, d_end)
        first_b = int(min(r['ts'] for r in bn_rows) // DAY) + 1
        days_b = [d for d in dd if d >= first_b]
        sp_b = days_b[0] + len(days_b) // 2
        st_b = daily_apy_accrual(bn_rows, days_b[0], days_b[-1] + 1)
        spot_s = TC.venue_costs('binance', 'SOL')[0]
        perp_s = {'binance': TC.venue_costs('binance', 'SOL')[1]}
        b0 = TC.run_carry_block('binance:SOL spot (BNSOL window)', days_b, {'binance': fb}, {'binance': pb}, spot_s, perp_s,
                                'collateral', const, None, None, closes, highs, sp_b)
        b1 = TC.run_carry_block('binance:SOL short, BNSOL collateral', days_b, {'binance': fb}, {'binance': pb},
                                spot_s + LST_SIDE_COST_BPS['BNSOL'] / 1e4, perp_s,
                                'collateral', const, None, st_b, closes, highs, sp_b)
        res['blocks']['binance_sol_spot_bnsol_window'] = carry_summary(b0)
        res['blocks']['binance_sol_short_bnsol_collateral'] = carry_summary(b1)
        res['bnsol_staking_apr_window'] = sum(st_b.values()) / len(st_b) * 365.0 if st_b else None
    if 'hl' in V and jito_rows:
        fh, ph = V['hl']['f'], V['hl']['p']
        dd = TC.span(fh, d_end)
        js = [(r['ts'], r['rate']) for r in jito_rows]
        first_j = int(min(t for t, _ in js) // DAY) + 1
        days_h = [d for d in dd if d >= first_j]
        sp_h = days_h[0] + len(days_h) // 2
        st_j = daily_rate_accrual(js, days_h[0], days_h[-1] + 1)
        spot_s = TC.venue_costs('binance', 'SOL')[0]
        perp_h = {'hl': TC.venue_costs('hl', 'SOL')[1]}
        h0 = TC.run_carry_block('hl:SOL cash 3x (JitoSOL window)', days_h, {'hl': fh}, {'hl': ph}, spot_s, perp_h, 'cash3x',
                                const, None, None, closes, highs, sp_h)
        h1 = TC.run_carry_block('hl:SOL short cash 3x, JitoSOL spot', days_h, {'hl': fh}, {'hl': ph},
                                spot_s + LST_SIDE_COST_BPS['JitoSOL'] / 1e4, perp_h, 'cash3x',
                                const, None, st_j, closes, highs, sp_h)
        res['blocks']['hl_sol_cash3x_jito_window'] = carry_summary(h0)
        res['blocks']['hl_sol_short_cash3x_jitosol'] = carry_summary(h1)
        res['jitosol_staking_apr_window'] = sum(st_j.values()) / len(st_j) * 365.0 if st_j else None
    for k, v in res['blocks'].items():
        v['late_entry'] = carry_late_entry(v)
    res['lst_side_cost_bps'] = LST_SIDE_COST_BPS
    res['notes'].append('Drift (JitoSOL/mSOL/INF cross-margin) not tested: data.api.drift.trade and its CloudFront host '
                        'do not resolve and the public S3 history bucket (drift-historical-data-v2) is empty (2026-10-10).')
    res['notes'].append('Hyperliquid portfolio margin accepts USDC, USDT, HYPE and BTC only (docs read 2026-10-10): no LST '
                        'can collateralise the short on HyperCore, so the kHYPE rows borrow the margin on HyperLend.')
    return res


# ----------------------------------------------------------------------------------------------------------------------
# analyze: everything into analysis.json
# ----------------------------------------------------------------------------------------------------------------------
def strip_private(o):
    if isinstance(o, dict):
        return {k: strip_private(v) for k, v in o.items() if not (isinstance(k, str) and k.startswith('_')) and not isinstance(k, tuple)}
    if isinstance(o, list):
        return [strip_private(x) for x in o]
    return o


def screen_table(screen):
    rows = []
    for r in screen['rows']:
        c = CAND[r['key']]
        rows.append({'key': r['key'], 'symbol': r['symbol'], 'network': r['network'], 'native': r['native'],
                     'vol24_native_pairs_usd': r['vol24_native_pairs_usd'], 'reserve_native_pairs_usd': r['reserve_native_pairs_usd'],
                     'pools': len(r['pools']), 'top_pool': (r['pools'][0]['dex'] + ' ' + r['pools'][0]['name']) if r['pools'] else None,
                     'queue_days': c.get('queue_days'), 'queue_src': c.get('queue_src'), 'redeem': c.get('redeem'),
                     'instant': c.get('instant'), 'deep': r['key'] in (['khype'] + BAR_ASSETS)})
    return rows


def cmd_analyze(args):
    t0 = time.time()
    out = Path(args.out)
    raw = out / 'raw'
    screen = read_json(out / 'screen.json')
    prices = read_gz(raw / 'prices_usd.json.gz')
    res = {'generated': utc(), 'benchmark': {'ssr': SSR, 'savings_paid_by_year': SAVINGS_PAID},
           'parameters': {'sell_share': SELL_SHARE, 'fee_legs': FEE_LEGS, 'gas_usd': GAS_USD, 'min_fill_usd': MIN_FILL_USD,
                          'sizes_usd': SIZES_USD, 'hurdles_bps': HURDLES_BPS, 'max_bar_bps': MAX_BAR_BPS,
                          'pass_usd_per_year': PASS_USD, 'gt_horizon_days': GT_HORIZON_DAYS},
           'screen': screen_table(screen), 'not_covered': NOT_COVERED, 'queue_bids': {}, 'api_gaps': [], 'checks': {}}
    # ---- kHYPE ----
    kh = analyze_khype(raw, screen, prices)
    kh_recs = kh.pop('_recs', None) or []
    kh_env = kh.pop('_env', None)
    if kh_recs:
        kh['bars_crosscheck'] = bars_crosscheck_khype(raw, screen, prices, kh_recs)
        # the GeckoTerminal window priced from bars, for a like-for-like comparison with the other assets
    res['queue_bids']['khype'] = kh
    print('khype done %.0fs' % (time.time() - t0), flush=True)
    # ---- bar assets ----
    envs = {'khype': kh_env} if kh_env else {}
    for k in BAR_ASSETS:
        try:
            blk = analyze_bar_asset(k, raw, screen, prices)
        except Exception as e:  # noqa: BLE001
            blk = {'key': k, 'skipped': 'error: %s' % str(e)[:200]}
        env = blk.pop('_env', None) if isinstance(blk, dict) else None
        if env:
            envs[k] = env
        res['queue_bids'][k] = blk
        print('%s done %.0fs' % (k, time.time() - t0), flush=True)
    # ---- verdicts and the shared-book series ----
    for k, blk in res['queue_bids'].items():
        if blk.get('skipped'):
            blk['verdict'] = 'no data: ' + blk['skipped']
            continue
        blk['verdict'] = verdict_for(blk)
        if blk['verdict'] == 'proposed' and k in envs:
            first_day = day_ts(blk['first_day']) // DAY
            blk['locked_capital_daily_unbounded'] = {
                'hurdle_bps': blk['at_quoted_size']['hurdle_bps'],
                'series': locked_capital_series(envs[k], blk['at_quoted_size']['hurdle_bps'], first_day, blk['days'])}
    # ---- Solana snapshot ----
    snap = read_gz(raw / 'sol_snapshot.json.gz')
    if snap:
        res['solana_instant_exit_snapshot'] = snap
    # ---- part (b) ----
    llama = read_gz(raw / 'rates' / 'llama_yields.json.gz') or {}
    jito = (read_gz(raw / 'rates' / 'jitosol_jito_api.json.gz') or {}).get('rows', [])
    blocks = {int(k): v for k, v in read_gz(raw / 'blocks_hyperevm.json.gz').items()}
    ks = sorted((blocks[int(k)], v) for k, v in read_gz(raw / 'rates' / 'khype.json.gz').items() if v and int(k) in blocks)
    hl = read_gz(raw / 'rates' / 'hyperlend.json.gz') or {}
    usdt = sorted((blocks[int(k)], v['borrow_index']) for k, v in (hl.get('USDT0') or {}).items() if v and int(k) in blocks)
    usdt_apr = ((usdt[-1][1] / usdt[0][1]) ** (365 * DAY / (usdt[-1][0] - usdt[0][0])) - 1) if len(usdt) > 2 else None
    try:
        res['carry_b'] = analyze_carry_b(raw, {'rate_samples_list': ks, 'recs': kh_recs, 'usdt0_borrow_apr': usdt_apr}, jito, llama)
    except Exception as e:  # noqa: BLE001
        import traceback
        res['carry_b'] = {'error': traceback.format_exc()[-1500:]}
    res['carry_b_inputs'] = {'hyperlend_usdt0_borrow_apr_realised': usdt_apr,
                             'hyperlend_khype_ltv_lt_bps': [((hl.get('kHYPE') or {}).get(max((hl.get('kHYPE') or {'0': 0}), key=int)) or {}).get(x) for x in ('ltv_bps', 'lt_bps')]}
    print('carry done %.0fs' % (time.time() - t0), flush=True)
    # ---- independent checks ----
    res['checks'] = independent_checks(raw, ks, jito, llama, snap, kh)
    res['api_gaps'] = [
        'GeckoTerminal public API serves OHLCV for the last 180 days only (401 beyond): the bar-based assets have ~7 months',
        'GeckoTerminal does not index Osmosis or other Cosmos chains: stTIA, milkTIA, stATOM not measurable here',
        'GeckoTerminal does not list Valantis STEX (kHYPE) pools: read from chain instead',
        'Drift data API host does not resolve and its S3 history bucket is empty: JitoSOL-on-Drift carry not testable',
        'Sanctum extra-api sol-value/current returned rates 2.3-2.5% below the on-chain stake pools (stale): not used',
        'Several public HyperEVM RPCs (rpc.hyperliquid.xyz/evm, rpc.hypurrscan.io, stakely) ignore the block tag on eth_call',
        'LiquidSwap route API returned a nonsensical route (65% impact via USOL) for WHYPE->kHYPE: no live depth quote for kHYPE',
        'BSC: publicnode/drpc/official seeds refused archive reads; blastapi served them',
        'TON (tsTON) and Hydration (vDOT vs H2O) not priced: no free exchange-rate history found',
    ]
    res['seconds'] = time.time() - t0
    write_json(out / 'analysis.json', strip_private(res))
    print('analysis written %.0fs' % (time.time() - t0), flush=True)


def independent_checks(raw, khype_samples, jito_rows, llama, snap, kh):
    """One headline number, two paths each."""
    out = {}
    # 1. kHYPE NAV: StakingAccountant.kHYPEToHYPE (sampled every 3h) vs the rate fixed in no-fee WithdrawalQueued events
    out['khype_nav_two_paths'] = (kh.get('payout_check') or {}).get('rate_gap_bps_no_fee_requests')
    # 2. JitoSOL: Jito's API (TVL / supply) vs the on-chain stake-pool account read today, and vs DefiLlama's APY
    if jito_rows and snap:
        onchain = snap['pools']['JitoSOL']['stake_pool']['rate']
        last = jito_rows[-1]
        out['jitosol_rate_api_vs_chain'] = {'api_rate': last['rate'], 'api_utc': last['utc'], 'onchain_rate': onchain,
                                            'onchain_epoch': snap['pools']['JitoSOL']['stake_pool']['epoch'],
                                            'gap_bps': 1e4 * (onchain / last['rate'] - 1.0), 'snapshot_utc': snap['at']}
        yr = [r for r in jito_rows if r['ts'] >= jito_rows[-1]['ts'] - 365 * DAY]
        g_api = (yr[-1]['rate'] / yr[0]['rate']) ** (365 * DAY / (yr[-1]['ts'] - yr[0]['ts'])) - 1
        ll = [r for r in (llama.get('jitosol') or []) if r['ts'] >= yr[0]['ts'] and r.get('apyBase') is not None]
        out['jitosol_yield_two_paths'] = {'api_rate_growth_365d': g_api,
                                          'llama_mean_apyBase_365d': (sum(r['apyBase'] for r in ll) / len(ll) / 100.0) if ll else None}
    return out


# ----------------------------------------------------------------------------------------------------------------------
# render: tables.md and manifest.json from analysis.json
# ----------------------------------------------------------------------------------------------------------------------
def fu(v):
    return '—' if v is None else ('$%s' % format(int(round(v)), ','))


def fb(v, d=1):
    return '—' if v is None else ('%.*fbp' % (d, v))


def fp(v, d=2):
    return '—' if v is None else ('%+.*f%%' % (d, 100 * v))


def fs(v):
    return '—' if v is None else ('%.0f%%' % (100 * v))


def cmd_render(args):
    out = Path(args.out)
    a = read_json(out / 'analysis.json')
    L = ['# queue_bids_alt — tables', '', 'Generated %s from `analysis.json` by `scripts/queue_bids_alt.py render`.' % a['generated'], '']
    L += ['## A. Candidates by DEX liquidity against the native coin (GeckoTerminal 24h, 2026-10-10)', '',
          '| rank | LST | chain | 24h volume | reserves | queue | redemption | instant route | deep |', '|---:|---|---|---:|---:|---|---|---|---|']
    for i, r in enumerate(a['screen'], 1):
        L.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (i, r['symbol'], r['network'], fu(r['vol24_native_pairs_usd']),
                 fu(r['reserve_native_pairs_usd']), ('%g d' % r['queue_days']) if r['queue_days'] is not None else '?',
                 (r['redeem'] or '')[:60], (r['instant'] or '')[:50], 'yes' if r['deep'] else ''))
    L += ['', 'Not covered by GeckoTerminal: ' + '; '.join('%s (%s)' % kv for kv in a['not_covered'].items()), '']
    kh = a['queue_bids'].get('khype', {})
    pc = kh.get('payout_check') or {}
    if pc:
        L += ['## B. kHYPE queue: what Kinetiq paid (every WithdrawalQueued / WithdrawalConfirmed since launch)', '',
              '| item | value |', '|---|---|',
              '| requests (≥ 0.01 kHYPE) | %s (%s) |' % (format(pc['requests'], ','), format(pc['requests_ge_min'], ',')),
              '| HYPE requested / confirmed | %s / %s |' % (format(int(pc['requested_hype']), ','), format(int(pc['confirmed_hype']), ',')),
              '| confirmations paying exactly the request | %s of %s (gap min %s, max %s) |' % (
                  fs(pc['paid_exact_share']), format(pc['paid_gap_bps'].get('n', 0), ','), fb(pc['paid_gap_bps'].get('min'), 3), fb(pc['paid_gap_bps'].get('max'), 3)),
              '| unconfirmed at the end | %s requests, %s HYPE |' % (format(pc['unconfirmed'], ','), format(int(pc['unconfirmed_hype']), ',')),
              '| cancelled | %d |' % pc['cancelled'],
              '| unstake fee | %s on %s requests; set to 0 at %s |' % (fb(pc['fee_bps'].get('p50')), format(pc['fee_bps'].get('nonzero', 0), ','), kh.get('fee_off_utc')),
              '| rate fixed in no-fee requests vs StakingAccountant (3-hourly samples) | p50 %s, p10–p90 %s to %s, p99 %s, min %s, max %s (n %s) |' % (
                  fb(pc['rate_gap_bps_no_fee_requests'].get('p50'), 2), fb(pc['rate_gap_bps_no_fee_requests'].get('p10'), 2),
                  fb(pc['rate_gap_bps_no_fee_requests'].get('p90'), 2), fb(pc['rate_gap_bps_no_fee_requests'].get('p99'), 2),
                  fb(pc['rate_gap_bps_no_fee_requests'].get('min'), 2), fb(pc['rate_gap_bps_no_fee_requests'].get('max'), 2),
                  format(pc['rate_gap_bps_no_fee_requests'].get('n', 0), ',')),
              '| request → confirmation, days | p1 %.2f, p5 %.2f, median %.2f, p90 %.2f, max %.1f |' % tuple(pc['wait_days'][x] for x in ('p1', 'p5', 'p50', 'p90', 'max')),
              '| fastest confirmation by month, days | %s |' % ', '.join('%s %.2f' % (m[2:], v) for m, v in pc['wait_min_by_month'].items()),
              '| HYPE requested by month | %s |' % ', '.join('%s %sk' % (m[2:], format(int(v / 1000), ',')) for m, v in pc['requested_hype_by_month'].items()),
              '']
    L += ['## C. Discounts to the exchange rate, hour by hour (market = volume-weighted across pools)', '',
          '| LST | source | window | hours traded | p50 | p90 | p99 | max | ≥10bp | ≥20bp | ≥50bp | round trip | episodes (hours) |',
          '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for k, b in a['queue_bids'].items():
        if b.get('skipped'):
            L.append('| %s | — | %s | | | | | | | | | | |' % (k, b['skipped']))
            continue
        blocks = [(b, b.get('source', ''))]
        if b.get('bars_window_block'):
            blocks.append((b['bars_window_block'], 'GeckoTerminal bars'))
        for x, src in blocks:
            d = x['market_hourly_discount_bps']
            e = x['episodes']
            L.append('| %s | %s | %s +%dd | %s | %s | %s | %s | %s | %s | %s | %s | %s | %d (%d) |' % (
                b.get('symbol', k), src[:40], x['first_day'], x['days'], format(x['hours_with_trades'], ','), fb(d.get('p50')), fb(d.get('p90')),
                fb(d.get('p99')), fb(d.get('max')), fs(d.get('share_ge_10bp')), fs(d.get('share_ge_20bp')), fs(d.get('share_ge_50bp')),
                fb(x['round_trip_bps']), e['count'], e['hours']))
    L += ['', '## D. The bid, out of sample (hurdle chosen on the first half, scored once on the second)', '',
          '| LST | source | size | hurdle | in sample $/yr | out of sample $/yr | 95% interval | t | fills OOS | median edge | trailing 90d $/yr | capacity | late 1h | late 1d | ¼ volume as sales | verdict |',
          '|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for k, b in a['queue_bids'].items():
        if b.get('skipped'):
            continue
        rows = [(b, b.get('source', ''), b.get('verdict'))]
        if b.get('bars_window_block'):
            rows.append((b['bars_window_block'], 'GeckoTerminal bars, same queue model', ''))
        for x, src, ver in rows:
            at = x['at_quoted_size']
            le = x['late_entry']
            ci = at['oos_ci95_usd_per_year']
            L.append('| %s | %s | %s | %s | %s | %s | %s to %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |' % (
                b.get('symbol', k), src[:34], fu(x['quoted_size_usd']), at['chosen_hurdle'], fu(at['in_sample_usd_per_year']),
                fu(at['out_of_sample_usd_per_year']), fu(ci[0]), fu(ci[1]), '%.2f' % at['oos_t'] if at['oos_t'] is not None else '—',
                at['fills_oos'], fb(at['median_edge_bps']), fu(at['trailing_90d_usd_per_year']), fu(x['capacity_size_usd']),
                fs(le['1h']['kept_share']), fs(le['1d']['kept_share']),
                fu((x.get('sell_share_0_25') or {}).get('out_of_sample_usd_per_year')), ver or ''))
    if kh.get('grid'):
        L += ['', '## E. kHYPE in detail', '', '### E1. Size grid (swap-level, %s +%d days, split %s)' % (kh['first_day'], kh['days'], kh['cutoff_utc']), '',
              '| size | hurdle | in sample | out of sample | 95% interval | fills OOS | filled | missed for capital | median edge | trailing 90d |',
              '|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|']
        for sz, g in kh['grid'].items():
            L.append('| %s | %s | %s | %s | %s to %s | %d | %s | %s | %s | %s |' % (fu(float(sz)), g['chosen_hurdle'], fu(g['in_sample_usd_per_year']),
                     fu(g['out_of_sample_usd_per_year']), fu(g['oos_ci95_usd_per_year'][0]), fu(g['oos_ci95_usd_per_year'][1]), g['fills_oos'],
                     fu(g['filled_usd']), fu(g['missed_capital_usd']), fb(g['median_edge_bps']), fu(g['trailing_90d_usd_per_year'])))
        at = kh['at_quoted_size']
        L += ['', '### E2. Value by month at %s (hurdle %s)' % (fu(kh['quoted_size_usd']), at['chosen_hurdle']), '',
              '| month | value | | month | value |', '|---|---:|---|---|---:|']
        ms = list(at['value_by_month_usd'].items())
        half = (len(ms) + 1) // 2
        for i in range(half):
            l1 = ms[i]
            l2 = ms[i + half] if i + half < len(ms) else ('', None)
            L.append('| %s | %s | | %s | %s |' % (l1[0], fu(l1[1]), l2[0], fu(l2[1]) if l2[1] is not None else ''))
        L += ['', '### E3. Variants at %s' % fu(kh['quoted_size_usd']), '', '| variant | out of sample $/yr | chosen hurdle |', '|---|---:|---|',
              '| as quoted (stake carry, fastest-claim wait, venue-median cap) | %s | %s |' % (fu(at['out_of_sample_usd_per_year']), at['chosen_hurdle'])]
        for name, key in (('carry at HyperLend WHYPE borrow (bid funded by borrowing HYPE)', 'variant_carry_whype_borrow'),
                          ('fixed 7-day wait', 'variant_fixed_7d_wait')):
            v = kh.get(key)
            if v:
                L.append('| %s | %s | %s |' % (name, fu(v['out_of_sample_usd_per_year']), v['chosen_hurdle']))
        L.append('| per print (no venue-median cap; an upper bound) | %s | %s |' % (fu(kh.get('per_print_upper_bound_oos_usd_per_year')), at['chosen_hurdle']))
        bw = kh.get('bars_window_block')
        if bw:
            sl = bw.get('swap_level_same_window') or {}
            L.append('| GeckoTerminal window, swap-level sales | %s | %s |' % (fu(sl.get('out_of_sample_usd_per_year')), sl.get('chosen_hurdle')))
            L.append('| GeckoTerminal window, bars with half the volume as sales | %s | %s |' % (fu(bw['at_quoted_size']['out_of_sample_usd_per_year']), bw['at_quoted_size']['chosen_hurdle']))
        cx = kh.get('bars_crosscheck') or {}
        if cx:
            L += ['', '### E4. The same pool-hours priced two ways (GeckoTerminal bar vs swap VWAP rebuilt from chain)', '',
                  '| pool | hours in both | median abs gap | p90 abs gap | signed median | bar volume / swap volume (p50) |', '|---|---:|---:|---:|---:|---:|']
            for pname, v in cx.items():
                g = v['abs_gap_bps']
                L.append('| %s | %s | %s | %s | %s | %s |' % (pname, format(v['hours_both'], ','), fb(g.get('p50'), 2), fb(g.get('p90'), 2),
                         fb(v['signed_median_gap_bps'], 2), '%.2f' % v['bar_volume_over_swap_volume']['p50'] if v.get('bar_volume_over_swap_volume') and v['bar_volume_over_swap_volume']['p50'] else '—'))
        st = kh.get('competitor_stex')
        if st:
            L += ['', 'Valantis STEX (instant unstake, a competing bidder, not back-runnable): %s of volume at a volume-weighted %s.' % (
                fu(st['volume_usd']), fb(st['vw_discount_bps']))]
        eps = (kh.get('episodes') or {}).get('top') or []
        if eps:
            L += ['', '### E5. Largest dislocation episodes (market discount above the round trip of %s)' % fb(kh['round_trip_bps']), '',
                  '| start | end | hours | volume | vw discount | peak | net of round trip |', '|---|---|---:|---:|---:|---:|---:|']
            for e in eps:
                L.append('| %s | %s | %d | %s | %s | %s | %s |' % (e['start_utc'][:16], e['end_utc'][:16], e['qualifying_hours'], fu(e['volume_usd']),
                         fb(e['vw_discount_bps']), fb(e['peak_bps']), fb(e['net_of_round_trip_bps'])))
    snap = a.get('solana_instant_exit_snapshot')
    if snap:
        L += ['', '## F. Solana: the instant exit against the stake pool (Jupiter quotes vs on-chain rate, %s)' % snap['at'], '',
              '| LST | rate | withdrawal fee (stake / SOL) | sell 10 | sell 1,000 | sell 10,000 | sell 50,000 | buy 1,000 | buy 10,000 |', '|---|---:|---|---:|---:|---:|---:|---:|---:|']
        for name, v in snap['pools'].items():
            q = {(x['side'], x['lst']): x.get('vs_rate_bps') for x in v['quotes']}
            sp = v['stake_pool']
            L.append('| %s | %.6f | %s / %s | %s | %s | %s | %s | %s | %s |' % (name, sp['rate'], fb(sp['stake_withdrawal_fee_bps'], 0), fb(sp['sol_withdrawal_fee_bps'], 0),
                     fb(q.get(('sell', 10))), fb(q.get(('sell', 1000))), fb(q.get(('sell', 10000))), fb(q.get(('sell', 50000))),
                     fb(q.get(('buy', 1000))), fb(q.get(('buy', 10000)))))
    cb = a.get('carry_b') or {}
    if cb.get('blocks'):
        L += ['', '## G. Part (b): long staking token, short the perp on one venue (excess over SSR, per year of capital)', '',
              '| row | capital | window (split) | rule | in sample | out of sample | t | bootstrap 95% | last 365d | last 90d | funding | staking + basis | borrow | costs |',
              '|---|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|']
        for k, v in cb['blocks'].items():
            ci = v['oos_bootstrap_mean_ci']
            L.append('| %s | %s | %s → %s (%s) | %s | %s | %s | %s | %s to %s | %s | %s | %s | %s | %s | %s |' % (
                v['name'], v['capital'], v['first_day'], v['last_day'], v['split_day'], v['chosen_rule'], fp(v['in_sample_ann_excess']),
                fp(v['oos_ann_excess']), '%.2f' % v['oos_t'] if v['oos_t'] is not None else '—', fp(ci[0]), fp(ci[1]),
                fp((v['last_365d'] or {}).get('chosen')), fp((v['last_90d'] or {}).get('chosen')), fp(v['funding_received'], 1),
                fp(v['extra_received'], 1), fp(v['borrow'], 2) if v['borrow'] is not None else '—', fp(v['costs'], 2)))
        L += ['', 'Staking yield over each window: kHYPE %s, BNSOL %s (DefiLlama apyBase), JitoSOL %s (Jito API). HyperLend USDT0 borrow used for the kHYPE margin: %s.' % (
            fp(cb.get('khype_staking_apr_window')), fp(cb.get('bnsol_staking_apr_window')), fp(cb.get('jitosol_staking_apr_window')), fp(cb.get('usdt0_borrow_apr_used')))]
        for n in cb.get('notes', []):
            L.append('- ' + n)
    L += ['', '## H. Independent checks', '']
    for k, v in (a.get('checks') or {}).items():
        L.append('- **%s**: `%s`' % (k, json.dumps(v, default=str)[:400]))
    L += ['', '## I. API gaps recorded (not guessed)', ''] + ['- ' + g for g in a.get('api_gaps', [])]
    (out / 'tables.md').write_text('\n'.join(L) + '\n')
    be = book_entries(a, out)
    if be:
        write_json(out / 'book_entries.json', be)
        print('book entries: %s' % ', '.join(e['id'] for e in be))
    elif (out / 'book_entries.json').exists():
        (out / 'book_entries.json').unlink()
    # manifest
    files = {}
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.name not in ('manifest.json',) and not p.name.endswith('.tmp'):
            files[str(p.relative_to(out))] = {'bytes': p.stat().st_size, 'sha256': sha256(p)}
    write_json(out / 'manifest.json', {
        'generated': utc(), 'script': 'scripts/queue_bids_alt.py', 'tests': 'scripts/test_queue_bids_alt.py',
        'sources': {'geckoterminal': GT + ' (pools, hourly OHLCV, last 180 days; one call per %.0fs)' % GT_MIN_INTERVAL,
                    'hyperevm_archive': ARCHIVE['hyperevm'], 'avalanche': ARCHIVE['avax'], 'sonic': ARCHIVE['sonic'],
                    'bsc': ['https://bsc-mainnet.public.blastapi.io'], 'monad': ARCHIVE['monad'],
                    'jito': 'https://kobe.mainnet.jito.network/api/v1/stake_pool_stats', 'solana_rpc': 'https://api.mainnet-beta.solana.com',
                    'jupiter': 'https://lite-api.jup.ag/swap/v1/quote', 'defillama_yields': 'https://yields.llama.fi/chart/<pool>',
                    'binance_klines': 'https://fapi.binance.com/fapi/v1/klines', 'term_carry_store': str(TC_DIR / 'raw'),
                    'hyperliquid_funding_store': 'research/2026-10-09/perps_history/funding'},
        'parameters': a.get('parameters'), 'files': files})
    print('rendered tables.md and manifest.json')


# ----------------------------------------------------------------------------------------------------------------------
# book entries for what passes (format of research/2026-10-10/queue_bids_ext/book_entries.json); never written to the
# book itself -- the coordinator adds them
# ----------------------------------------------------------------------------------------------------------------------
CARRY_PASS = {'min_oos': 0.02, 'min_t': 2.0}


def carry_passes(v, base=None):
    ci = v.get('oos_bootstrap_mean_ci') or [None, None]
    ok = ((v.get('oos_ann_excess') or 0) >= CARRY_PASS['min_oos'] and (v.get('oos_t') or 0) >= CARRY_PASS['min_t']
          and ci[0] is not None and ci[0] > 0 and ((v.get('last_90d') or {}).get('chosen') or 0) > 0)
    if base is not None:
        ok = ok and (v.get('oos_ann_excess') or 0) > (base.get('oos_ann_excess') or 0)
    return ok


def book_entries(a, out_dir):
    entries = []
    rel = str(Path(out_dir).relative_to(ROOT)) if str(out_dir).startswith(str(ROOT)) else str(out_dir)
    kh = a['queue_bids'].get('khype') or {}
    if kh.get('verdict') == 'proposed':
        at = kh['at_quoted_size']
        pc = kh['payout_check']
        entries.append({
            'id': 'kinetiq-khype-queue-bid', 'name': 'Buy kHYPE below the HYPE Kinetiq pays for it and redeem through the 7-day queue',
            'kind': 'redemption', 'status': 'proposed',
            'thesis': ('kHYPE trades below the HYPE its withdrawal queue pays: %s at the hourly median and %s at the 90th percentile '
                       'over %s days of swaps rebuilt from chain. A %s bid that redeems every fill made %s a year out of sample '
                       '(95%% interval %s to %s), %s over the trailing 90 days.') % (
                fb(kh['market_hourly_discount_bps']['p50']), fb(kh['market_hourly_discount_bps']['p90']), kh['days'],
                fu(kh['quoted_size_usd']), fu(at['out_of_sample_usd_per_year']), fu(at['oos_ci95_usd_per_year'][0]),
                fu(at['oos_ci95_usd_per_year'][1]), fu(at['trailing_90d_usd_per_year'])),
            'mechanism': ('Anyone can queueWithdrawal(kHYPE) on Kinetiq\'s StakingManager (0x393d...2109); the HYPE amount is '
                          'fixed at the request at StakingAccountant.kHYPEToHYPE and confirmWithdrawal pays it after '
                          'withdrawalDelay (604,800 s). Every one of %s confirmations since launch paid exactly its request; '
                          'the 10bp unstake fee was set to zero on %s. The bid prices against kHYPEToHYPE, waits the fastest '
                          'confirmation seen within a day of each fill (never under 7 days), charges two pool fees and the '
                          'staking yield forgone while queued, and caps each fill at the median venue less one fee.') % (
                format(pc['paid_gap_bps'].get('n', 0), ','), kh.get('fee_off_utc')),
            'legs': ['buy kHYPE with WHYPE on the kHYPE/WHYPE pools (Ramses v3, Nest, Project X, Hybra) behind a seller when the '
                     'median venue\'s discount less one fee clears the hurdle',
                     'queueWithdrawal on the Kinetiq StakingManager', 'confirmWithdrawal after 7 days; unwrap or reuse the HYPE'],
            'capacity_usd': kh['quoted_size_usd'], 'capital_days': 7.0,
            'kill_criteria': ['trailing 90-day value under $10k a year at the quoted size',
                              'any confirmation paying less than its WithdrawalQueued hypeAmount, or a non-zero unstakeFeeRate',
                              'the fastest confirmation over a month above 10 days', 'withdrawals paused for over a week'],
            'risks': ['HYPE price exposure of the capital unless hedged (a short HYPE perp, which itself earns funding)',
                      'Kinetiq contract, validator slashing and governance risk on HYPE queued for a week',
                      'other bidders (Valantis STEX, arbitrageurs) not simulated: values are ceilings for one participant'],
            'evidence': {'notes': '%s/analysis.json; tables.md; scripts/queue_bids_alt.py' % rel, 'findings': [], 'verify': []},
            'quotes': [{'at': a['generated'], 'go': True, 'present': True, 'source': 'history', 'usd': round(at['out_of_sample_usd_per_year']),
                        'net_apr': round((at['out_of_sample_usd_per_year'] or 0) / kh['quoted_size_usd'], 4), 'window': rel,
                        'note': 'hurdle %s chosen on the first half, scored on the second' % at['chosen_hurdle']}],
            'recheck_hours': 168})
    cb = (a.get('carry_b') or {}).get('blocks') or {}
    kc, base = cb.get('hl_hype_short_khype_collateral'), cb.get('hl_hype_spot_khype_window')
    if kc and base and carry_passes(kc, base):
        inc = kc['oos_ann_excess'] - base['oos_ann_excess']
        entries.append({
            'id': 'hl-hype-carry-khype-spot', 'name': 'HYPE spot/short-perp carry with kHYPE as the spot leg (margin borrowed on HyperLend)',
            'kind': 'carry', 'status': 'proposed',
            'thesis': ('The Hyperliquid HYPE carry, with the spot leg held as kHYPE: staking %s a year on top of funding. Over the same '
                       'window the kHYPE version beat the spot version by %s a year out of sample (%s vs %s over SSR, t %.2f), '
                       'after paying HyperLend\'s USDT0 rate (%s) on the short\'s margin instead of Hyperliquid\'s portfolio-margin rate.') % (
                fp(a['carry_b'].get('khype_staking_apr_window')), fp(inc), fp(kc['oos_ann_excess']), fp(base['oos_ann_excess']),
                kc['oos_t'], fp(a['carry_b'].get('usdt0_borrow_apr_used'))),
            'mechanism': ('Hyperliquid portfolio margin accepts only USDC, USDT, HYPE and BTC, so kHYPE cannot collateralise the '
                          'short on HyperCore: kHYPE is supplied to HyperLend (LTV 59%%, liquidation 74%%, priced at the Kinetiq '
                          'exchange rate by a fundamental oracle), USDT0 is borrowed for 10%% of notional and moved to HyperCore as '
                          'the short\'s margin; losses after a rise are borrowed too and the legs are rebalanced after a 25%% move. '
                          'The kHYPE leg is marked at the market discount daily; it exits through the queue at the rate.'),
            'legs': ['buy HYPE and mint kHYPE (or buy kHYPE below the rate on HyperEVM)', 'supply kHYPE to HyperLend; borrow USDT0 (10% of notional)',
                     'short the HYPE perp on Hyperliquid for the same notional', 'rebalance after a 25% price move'],
            'capacity_usd': 5_000_000, 'capital_days': None,
            'kill_criteria': ['the HYPE carry\'s own kill criteria (hl-hype-spot-perp-carry)',
                              'HyperLend USDT0 borrow above 15% for a week, or kHYPE LTV cut below 0.4',
                              'kHYPE oracle on HyperLend switched to a market feed', 'Kinetiq withdrawals paused or a non-zero unstake fee'],
            'risks': ['two venues on one chain: a HYPE crash needs margin moved from HyperCore gains to HyperLend before liquidation',
                      'kHYPE discount (12% in September 2025) is marked against the position until the queue pays',
                      'same venue and same funding as the existing HYPE carry: not additive capacity, an upgrade of its spot leg'],
            'evidence': {'notes': '%s/analysis.json (carry_b); tables.md G; scripts/queue_bids_alt.py' % rel, 'findings': [], 'verify': []},
            'quotes': [{'at': a['generated'], 'go': True, 'present': True, 'source': 'history', 'usd': round(5_000_000 * inc),
                        'net_apr': round(kc['oos_ann_excess'], 4), 'window': rel,
                        'note': 'increment over the spot leg at $5M: %s a year (rule %s chosen before %s)' % (fp(inc), kc['chosen_rule'], kc['split_day'])}],
            'recheck_hours': 168})
    return entries


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('screen')
    s.add_argument('--out', required=True)
    s.add_argument('--assets', default='')
    s.add_argument('--refresh', action='store_true')
    s.set_defaults(func=cmd_screen)
    s = sub.add_parser('collect')
    s.add_argument('--out', required=True)
    s.add_argument('--assets', default='')
    s.add_argument('--parts', default='ohlcv,khype,jito')
    s.add_argument('--last-block', type=int, default=0)
    s.add_argument('--first-block', type=int, default=0)
    s.add_argument('--thin', type=int, default=1)
    s.set_defaults(func=cmd_collect)
    s = sub.add_parser('analyze')
    s.add_argument('--out', required=True)
    s.set_defaults(func=cmd_analyze)
    s = sub.add_parser('render')
    s.add_argument('--out', required=True)
    s.set_defaults(func=cmd_render)
    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
